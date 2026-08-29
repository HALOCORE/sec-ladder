//! p29 rung R3 -- safe Rust, tuned. Same semantics, same representation, same
//! allocator traffic as R2; what moves is how many times a slot is visited.
//!
//! Three levers, all of them on the WALK, which is what three of the four
//! opcodes begin with. ⚠ **None of them is priced**: this pattern publishes no
//! rung-to-rung cost (../NOTES.md 8), so what follows is a description of the
//! spelling difference and not a claim about it.
//!
//!   1. **one discriminant test per step instead of four.** R2 writes
//!      `tab[cur].is_some()` in the loop condition and then
//!      `tab[cur].as_ref().unwrap()` once per field it reads. R3 asks
//!      `match tab[cur].as_ref()` once and destructures the three fields it
//!      needs into locals, so the `Option` is examined exactly once per step;
//!   2. **one bounds check per step instead of four**, for the same reason --
//!      `tab[cur]` is indexed once;
//!   3. **the successor descent reads `l` once**, where R2 reads it three times
//!      (the loop condition, the liveness test and the move).
//!
//! What is deliberately NOT changed: the representation is still
//! `Option<Box<Rec>>` with slots never recycled, the allocation is still one
//! `Box::new` per record, and the SAFETY LINE is still the same two conjuncts.
//! A rung that changed any of those would be a different benchmark
//! (`.memory/01-ladder.md`, and ../spec.md's `idiom`).
//!
//! Still zero `unsafe`, and still no epilogue: dropping the table is the
//! epilogue.

#[path = "../../common/driver.rs"]
mod driver;

const TABCAP: usize = 32;
const NIL: usize = 255;
const SENT: u64 = 251;

struct Rec {
    key: u8,
    val: u8,
    l: u8,
    r: u8,
}

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    if len < 4 {
        return 0;
    }
    let nops: usize = buf[off] as usize + 256 * (buf[off + 1] as usize) + 65536 * (buf[off + 2]
        as usize) + 16777216 * (buf[off + 3] as usize);
    if nops == 0 {
        return 0;
    }
    let mut tab: [Option<Box<Rec>>; TABCAP] = [const { None }; TABCAP];
    let mut ntab: usize = 0;
    let mut root: usize = NIL;
    let mut g_has: bool = false;
    let mut g_slot: usize = 0;
    let mut g_key: u8 = 0;
    let mut acc: u64 = 0;
    let mut p: usize = 4;
    let mut o: usize = 0;
    while o < nops {
        if len - p < 2 {
            break;
        }
        let c: u8 = buf[off + p];
        let a: u8 = buf[off + p + 1];
        p = p + 2;
        if c % 4 == 0 {
            let mut cur: usize = root;
            let mut par: usize = NIL;
            let mut goleft: bool = false;
            let mut dup: bool = false;
            let mut steps: usize = 0;
            while cur != NIL && steps < TABCAP {
                let (k, l, r) = match tab[cur].as_ref() {
                    Some(rec) => (rec.key, rec.l as usize, rec.r as usize),
                    None => break,
                };
                steps = steps + 1;
                if a < k {
                    par = cur;
                    goleft = true;
                    cur = l;
                } else if a > k {
                    par = cur;
                    goleft = false;
                    cur = r;
                } else {
                    tab[cur].as_mut().unwrap().val = a.wrapping_mul(7).wrapping_add(1);
                    dup = true;
                    break;
                }
            }
            if dup {
                acc = acc.wrapping_mul(31).wrapping_add(a as u64);
            } else if ntab < TABCAP {
                tab[ntab] = Some(Box::new(Rec {
                    key: a,
                    val: a.wrapping_mul(7).wrapping_add(1),
                    l: NIL as u8,
                    r: NIL as u8,
                }));
                if par == NIL {
                    root = ntab;
                } else if goleft {
                    tab[par].as_mut().unwrap().l = ntab as u8;
                } else {
                    tab[par].as_mut().unwrap().r = ntab as u8;
                }
                ntab = ntab + 1;
                acc = acc.wrapping_mul(31).wrapping_add(a as u64);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else if c % 4 == 1 {
            let mut cur: usize = root;
            let mut found: bool = false;
            let mut steps: usize = 0;
            while cur != NIL && steps < TABCAP {
                let (k, l, r) = match tab[cur].as_ref() {
                    Some(rec) => (rec.key, rec.l as usize, rec.r as usize),
                    None => break,
                };
                steps = steps + 1;
                if a < k {
                    cur = l;
                } else if a > k {
                    cur = r;
                } else {
                    found = true;
                    break;
                }
            }
            if found {
                g_has = true;
                g_slot = cur;
                g_key = a;
                acc = acc.wrapping_mul(31).wrapping_add(1);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else if c % 4 == 2 {
            let mut cur: usize = root;
            let mut par: usize = NIL;
            let mut goleft: bool = false;
            let mut found: bool = false;
            let mut steps: usize = 0;
            while cur != NIL && steps < TABCAP {
                let (k, l, r) = match tab[cur].as_ref() {
                    Some(rec) => (rec.key, rec.l as usize, rec.r as usize),
                    None => break,
                };
                steps = steps + 1;
                if a < k {
                    par = cur;
                    goleft = true;
                    cur = l;
                } else if a > k {
                    par = cur;
                    goleft = false;
                    cur = r;
                } else {
                    found = true;
                    break;
                }
            }
            if found {
                let mut guard: usize = 0;
                while guard < TABCAP {
                    guard = guard + 1;
                    let (cl, cr) = match tab[cur].as_ref() {
                        Some(rec) => (rec.l as usize, rec.r as usize),
                        None => break,
                    };
                    if cl != NIL && tab[cl].is_some() && cr != NIL && tab[cr].is_some() {
                        let mut sp: usize = cur;
                        let mut s: usize = cr;
                        let mut sgoleft: bool = false;
                        let mut sst: usize = 0;
                        loop {
                            let sl: usize = match tab[s].as_ref() {
                                Some(rec) => rec.l as usize,
                                None => break,
                            };
                            if sl == NIL || sst >= TABCAP || tab[sl].is_none() {
                                break;
                            }
                            sst = sst + 1;
                            sp = s;
                            s = sl;
                            sgoleft = true;
                        }
                        // THE SUBSTITUTION: the successor's key and val are
                        // copied INTO the victim's record. Nothing is freed and
                        // no `Option` discriminant changes -- which is why the
                        // safety line below needs its second conjunct.
                        let (sk, sv) = match tab[s].as_ref() {
                            Some(rec) => (rec.key, rec.val),
                            None => break,
                        };
                        let rec = tab[cur].as_mut().unwrap();
                        rec.key = sk;
                        rec.val = sv;
                        cur = s;
                        par = sp;
                        goleft = sgoleft;
                        continue;
                    }
                    let ch: u8 = if cl != NIL { cl as u8 } else { cr as u8 };
                    if par == NIL {
                        root = ch as usize;
                    } else if goleft {
                        tab[par].as_mut().unwrap().l = ch;
                    } else {
                        tab[par].as_mut().unwrap().r = ch;
                    }
                    // THE FREE **and** THE INVALIDATION, in one operation.
                    tab[cur] = None;
                    break;
                }
                acc = acc.wrapping_mul(31).wrapping_add(2);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else {
            // THE SAFETY LINE, spelled as one `match` rather than R2's
            // `is_some()` + `unwrap()`. The FIRST conjunct is the `Some` arm --
            // the language's own -- and the SECOND, `rec.key == g_key`, is the
            // one no language writes for you.
            let v: Option<u8> = if g_has {
                match tab[g_slot].as_ref() {
                    Some(rec) if rec.key == g_key => Some(rec.val),
                    _ => None,
                }
            } else {
                None
            };
            match v {
                Some(x) => acc = acc.wrapping_mul(31).wrapping_add(x as u64),
                None => acc = acc.wrapping_mul(31).wrapping_add(SENT),
            }
        }
        o = o + 1;
    }
    acc.wrapping_mul(31).wrapping_add(ntab as u64)
}

// ---------------------------------------------------------------- driver ----
fn main() {
    let path = driver::arg_path();
    let inp = driver::load(&path);
    let (stride_w, bytes) = driver::head1_u64_bytes(&inp);
    let n_iters: u64 = inp.n_iters;
    // SLB-DRIVER-BEGIN
    let n_blob: usize = bytes.len();
    let buf: &[u8] = bytes.as_slice();
    let mut acc: u64 = 0;
    if stride_w >= 4 && stride_w <= n_blob as u64 {
        let stride: usize = stride_w as usize;
        let nwin: u64 = (n_blob / stride) as u64;
        let mut it: u64 = 0;
        while it < n_iters {
            let k: usize = ((acc as u128 * nwin as u128) >> 64) as usize;
            let r: u64 = kernel(buf, k * stride, stride);
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    driver::emit(acc);
}
