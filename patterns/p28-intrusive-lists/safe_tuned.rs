//! p28 rung R3 -- safe Rust, tuned. Same semantics, same representation, same
//! allocator traffic as R2; what moves is how many times a slot is indexed.
//!
//! Three levers, and all three are on the same thing -- **R2 re-indexes `tab`
//! once per FIELD and this rung indexes it once per OBJECT**. ⚠ **None of them
//! is priced**: this pattern publishes no rung-to-rung cost (../NOTES.md 8), so
//! what follows describes the spelling difference and claims nothing about it.
//!
//!   1. **one discriminant test and one bounds check per walk step instead of
//!      three.** R2 writes `tab[cur].is_some()` in the loop condition and then
//!      `tab[cur].as_ref().unwrap()` once for `key` and again for `hn`. R3 asks
//!      `match tab[cur].as_ref()` once and destructures both fields into
//!      locals;
//!   2. **the DEL splice reads the victim's four links ONCE** into `hpv`,
//!      `hnv`, `lpv`, `lnv`, where R2 re-reads whichever one it needs at each of
//!      the eight sites;
//!   3. **TRIM reads `key`, `lp`, `hp` and `hn` once**, in one borrow, before it
//!      touches anything else -- which it must, because the safety line writes
//!      into the neighbours it just named.
//!
//! What is deliberately NOT changed: the representation is still
//! `Option<Box<Obj>>` over a slot table with `u8` links and slots never
//! recycled, the allocation is still one `Box::new` per object and one drop per
//! DEL and per TRIM, and **THE SAFETY LINE IS STILL WRITTEN OUT BY HAND** -- the
//! same nine-line splice, in the same place, for the same reason. A rung that
//! changed any of those would be a different benchmark
//! (`.memory/01-ladder.md`, and ../spec.md's `idiom`).
//!
//! Still zero `unsafe`, and still no epilogue: dropping the table is the
//! epilogue.

#[path = "../../common/driver.rs"]
mod driver;

const NB: usize = 8;
const SLOTS: usize = 48;
const NIL: u8 = 255;
const SENT: u64 = 251;

struct Obj {
    key: u8,
    val: u8,
    lp: u8,
    ln: u8,
    hn: u8,
    hp: u8,
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
    let mut tab: [Option<Box<Obj>>; SLOTS] = [const { None }; SLOTS];
    let mut bucket: [u8; NB] = [NIL; NB];
    let mut head: u8 = NIL;
    let mut tail: u8 = NIL;
    let mut nmade: usize = 0;
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
        let b: usize = (a % NB as u8) as usize;
        if c % 4 == 3 {
            // TRIM. Reclaim the OLDEST object. It arrives here through the
            // EVICTION list and therefore holds no hash-chain cursor.
            if tail != NIL {
                let v: usize = tail as usize;
                let (vk, lpv, hpv, hnv) = match tab[v].as_ref() {
                    Some(ob) => (ob.key, ob.lp, ob.hp, ob.hn),
                    None => (0u8, NIL, NIL, NIL),
                };
                if lpv != NIL {
                    tab[lpv as usize].as_mut().unwrap().ln = NIL;
                } else {
                    head = NIL;
                }
                tail = lpv;
                // THE SAFETY LINE. c/kernel.c omits it; this rung writes it out
                // by hand, because nothing in safe Rust knows that this object
                // is a member of a second container.
                let vb: usize = (vk % NB as u8) as usize;
                if hpv != NIL {
                    tab[hpv as usize].as_mut().unwrap().hn = hnv;
                } else {
                    bucket[vb] = hnv;
                }
                if hnv != NIL {
                    tab[hnv as usize].as_mut().unwrap().hp = hpv;
                }
                tab[v] = None;
                acc = acc.wrapping_mul(31).wrapping_add(3);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
            o = o + 1;
            continue;
        }
        // THE WALK, shared by PUT, GET and DEL. One borrow per step.
        let mut cur: u8 = bucket[b];
        let mut steps: usize = 0;
        let mut found: bool = false;
        while cur != NIL && steps < SLOTS {
            let (k, nx) = match tab[cur as usize].as_ref() {
                Some(ob) => (ob.key, ob.hn),
                None => break,
            };
            steps = steps + 1;
            if k == a {
                found = true;
                break;
            }
            cur = nx;
        }
        if c % 4 == 0 {
            // PUT. A hit updates the object in place.
            if found {
                tab[cur as usize].as_mut().unwrap().val = a.wrapping_mul(7).wrapping_add(1);
                acc = acc.wrapping_mul(31).wrapping_add(a as u64);
            } else if nmade < SLOTS {
                let s: u8 = nmade as u8;
                tab[s as usize] = Some(
                    Box::new(
                        Obj {
                            key: a,
                            val: a.wrapping_mul(7).wrapping_add(1),
                            lp: NIL,
                            ln: head,
                            hn: bucket[b],
                            hp: NIL,
                        },
                    ),
                );
                if head != NIL {
                    tab[head as usize].as_mut().unwrap().lp = s;
                } else {
                    tail = s;
                }
                head = s;
                if bucket[b] != NIL {
                    tab[bucket[b] as usize].as_mut().unwrap().hp = s;
                }
                bucket[b] = s;
                nmade = nmade + 1;
                acc = acc.wrapping_mul(31).wrapping_add(a as u64);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else if c % 4 == 1 {
            // GET.
            if found {
                acc = acc.wrapping_mul(31).wrapping_add(
                    tab[cur as usize].as_ref().unwrap().val as u64,
                );
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else {
            // DEL. A SPLICE out of BOTH lists, then the free. DEL arrives ALONG
            // the hash chain, so it holds a chain cursor when it frees -- which
            // is why DEL is not the path that forgets.
            if found {
                let (hpv, hnv, lpv, lnv) = match tab[cur as usize].as_ref() {
                    Some(ob) => (ob.hp, ob.hn, ob.lp, ob.ln),
                    None => (NIL, NIL, NIL, NIL),
                };
                if hpv != NIL {
                    tab[hpv as usize].as_mut().unwrap().hn = hnv;
                } else {
                    bucket[b] = hnv;
                }
                if hnv != NIL {
                    tab[hnv as usize].as_mut().unwrap().hp = hpv;
                }
                if lpv != NIL {
                    tab[lpv as usize].as_mut().unwrap().ln = lnv;
                } else {
                    head = lnv;
                }
                if lnv != NIL {
                    tab[lnv as usize].as_mut().unwrap().lp = lpv;
                } else {
                    tail = lpv;
                }
                tab[cur as usize] = None;
                acc = acc.wrapping_mul(31).wrapping_add(2);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        }
        o = o + 1;
    }
    // No epilogue: dropping `tab` frees every object still alive, which is the
    // loop the C and unsafe rungs write by hand. ../NOTES.md 4.
    acc.wrapping_mul(31).wrapping_add(nmade as u64)
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
