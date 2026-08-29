//! p29 rung R2 -- safe Rust, naive.
//!
//! **The representation is not a choice, and it is `p27`'s.** Safe Rust cannot
//! hold a pointer to a record it has freed, so a slot is `Option<Box<Rec>>`:
//! `Some` while the record lives, `None` once it does not, and the cached
//! lookup result is a SLOT INDEX rather than an address. Three consequences:
//!
//!   1. `tab[i] = None` **frees the record and invalidates the slot in one
//!      operation**, so the first conjunct of the safety line -- *is the
//!      allocation still there?* -- is written by the language. This rung
//!      cannot commit p29's use-after-free class at all.
//!   2. **The second conjunct is not.** `tab[g_slot].as_ref().unwrap().key ==
//!      g_key` has to be written out, in safe Rust exactly as in C, because
//!      nothing in the type system knows that a live record's OCCUPANT can
//!      change. Deleting it makes this rung silently wrong on precisely the
//!      inputs ASan cannot see. Its C twin is `controls/arms.py`'s `liveonly`
//!      arm, which is wrong on EVERY use-after-recycle window and fires ASan
//!      zero times -- ../NOTES.md 2b.
//!   3. Slots are **never recycled** (`ntab` only grows), so a `None` slot stays
//!      `None` for the rest of the window. That is `p27`'s convention and it is
//!      what keeps the safe rung's answer a function of the ops rather than of
//!      the allocator. ../spec.md says what the other two spellings do.
//!
//! **There is no epilogue in this rung.** Dropping the table frees every record
//! still alive; the loop the C and unsafe rungs write by hand is written by the
//! language. ../NOTES.md 3 records the asymmetry; **no price is published for
//! it, here or anywhere in this pattern** (../NOTES.md 8).
//!
//! Naive in the places R3 tunes: every walk step indexes `tab` and then
//! `as_ref().unwrap()`s it, so the discriminant is tested twice per step, and
//! every index is a plain `tab[i]` under an explicit bound, so rustc emits its
//! own bounds check on top of the semantic one. ⚠ **Whether it survives was NOT
//! measured**: this pattern publishes no rung-to-rung cost at all
//! (../NOTES.md 8).
//!
//! Wrapping arithmetic is spelled `wrapping_mul` / `wrapping_add` because
//! `-C debug-assertions=on` would otherwise panic on the fold, and the C rungs
//! wrap by definition (C99 6.2.5p9).

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
            while cur != NIL && tab[cur].is_some() && steps < TABCAP {
                steps = steps + 1;
                if a < tab[cur].as_ref().unwrap().key {
                    par = cur;
                    goleft = true;
                    cur = tab[cur].as_ref().unwrap().l as usize;
                } else if a > tab[cur].as_ref().unwrap().key {
                    par = cur;
                    goleft = false;
                    cur = tab[cur].as_ref().unwrap().r as usize;
                } else {
                    tab[cur].as_mut().unwrap().val = a.wrapping_mul(7).wrapping_add(1);
                    dup = true;
                    break;
                }
            }
            if dup {
                acc = acc.wrapping_mul(31).wrapping_add(a as u64);
            } else if ntab < TABCAP {
                // THE ALLOCATION: `Box::new(..)` is one `malloc`, the same
                // allocator and the same size class as C's `malloc(RECSZ)`.
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
            while cur != NIL && tab[cur].is_some() && steps < TABCAP {
                steps = steps + 1;
                if a < tab[cur].as_ref().unwrap().key {
                    cur = tab[cur].as_ref().unwrap().l as usize;
                } else if a > tab[cur].as_ref().unwrap().key {
                    cur = tab[cur].as_ref().unwrap().r as usize;
                } else {
                    found = true;
                    break;
                }
            }
            if found {
                // The cached lookup result is a SLOT INDEX. Safe Rust cannot
                // hold the address: `E0502`, and that is generic borrowck and
                // not this row's mechanism (`TASK_133` 3d).
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
            while cur != NIL && tab[cur].is_some() && steps < TABCAP {
                steps = steps + 1;
                if a < tab[cur].as_ref().unwrap().key {
                    par = cur;
                    goleft = true;
                    cur = tab[cur].as_ref().unwrap().l as usize;
                } else if a > tab[cur].as_ref().unwrap().key {
                    par = cur;
                    goleft = false;
                    cur = tab[cur].as_ref().unwrap().r as usize;
                } else {
                    found = true;
                    break;
                }
            }
            if found {
                let mut guard: usize = 0;
                while guard < TABCAP {
                    guard = guard + 1;
                    if tab[cur].as_ref().unwrap().l as usize != NIL
                        && tab[tab[cur].as_ref().unwrap().l as usize].is_some()
                        && tab[cur].as_ref().unwrap().r as usize != NIL
                        && tab[tab[cur].as_ref().unwrap().r as usize].is_some()
                    {
                        let mut sp: usize = cur;
                        let mut s: usize = tab[cur].as_ref().unwrap().r as usize;
                        let mut sgoleft: bool = false;
                        let mut sst: usize = 0;
                        while tab[s].as_ref().unwrap().l as usize != NIL
                            && tab[tab[s].as_ref().unwrap().l as usize].is_some()
                            && sst < TABCAP
                        {
                            sst = sst + 1;
                            sp = s;
                            s = tab[s].as_ref().unwrap().l as usize;
                            sgoleft = true;
                        }
                        // THE SUBSTITUTION: the successor's key and val are
                        // copied INTO the victim's record. The victim's
                        // allocation is NOT freed, so no `Option` discriminant
                        // anywhere changes -- which is exactly why the safety
                        // line below needs a second conjunct.
                        let sk: u8 = tab[s].as_ref().unwrap().key;
                        let sv: u8 = tab[s].as_ref().unwrap().val;
                        tab[cur].as_mut().unwrap().key = sk;
                        tab[cur].as_mut().unwrap().val = sv;
                        cur = s;
                        par = sp;
                        goleft = sgoleft;
                        continue;
                    }
                    let ch: u8 = if tab[cur].as_ref().unwrap().l as usize != NIL {
                        tab[cur].as_ref().unwrap().l
                    } else {
                        tab[cur].as_ref().unwrap().r
                    };
                    if par == NIL {
                        root = ch as usize;
                    } else if goleft {
                        tab[par].as_mut().unwrap().l = ch;
                    } else {
                        tab[par].as_mut().unwrap().r = ch;
                    }
                    // THE FREE **and** THE INVALIDATION, in one operation. This
                    // is the line C splits in two.
                    tab[cur] = None;
                    break;
                }
                acc = acc.wrapping_mul(31).wrapping_add(2);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else {
            // THE SAFETY LINE. c/kernel.c omits both conjuncts. In safe Rust
            // the FIRST is written by the language -- `is_some()` is the
            // `Option` discriminant, which is what `tab[cur] = None` set -- and
            // the SECOND is not written by anything. A live record whose
            // occupant has changed is a perfectly good `Some`.
            if g_has && tab[g_slot].is_some()
                && tab[g_slot].as_ref().unwrap().key == g_key
            {
                let v: u8 = tab[g_slot].as_ref().unwrap().val;
                acc = acc.wrapping_mul(31).wrapping_add(v as u64);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        }
        o = o + 1;
    }
    // No epilogue: `tab` is dropped here and that frees every live record.
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
