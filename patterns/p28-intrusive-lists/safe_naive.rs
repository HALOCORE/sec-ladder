//! p28 rung R2 -- safe Rust, naive.
//!
//! **THE REPRESENTATION IS NOT A CHOICE, AND SAYING SO IS HALF THIS PATTERN'S
//! RESULT.** The C rungs put four raw pointers inside every object: `lp`/`ln`
//! for the eviction list and `hn`/`hp` for the hash chain. Safe Rust cannot
//! write that down at all -- an object on two lists is an object with two
//! owners, and `&mut` aliasing forbids it -- so the safe port replaces the
//! POINTERS with SLOT NUMBERS into a table and keeps the two lists as `u8`
//! links. Three consequences, and the second is the one worth reading:
//!
//!   1. `tab[i] = None` **frees the object and invalidates the slot in one
//!      operation**, so `Box`'s drop is the `free` and there is no epilogue in
//!      this rung: dropping the table is the epilogue. The allocator traffic is
//!      the C rungs' -- one allocation per object, one free per DEL and per
//!      TRIM -- so this is `p29`'s `Option<Box<Rec>>` shape and not an arena.
//!      ⚠ **The old catalogue sentence *"safe Rust's answer is an arena that
//!      never frees"* is FALSE OF THIS SPELLING.** ../NOTES.md 4.
//!   2. ⚠⚠ **THE SAFETY LINE DOES NOT GO AWAY AND THE LANGUAGE DOES NOT WRITE
//!      IT.** The nine lines TRIM needs to leave the hash chain are written out
//!      here exactly as in C, with `Option`/slot spelling instead of pointers.
//!      Nothing in the type system knows that an object is a member of two
//!      containers, because in this representation it is a member of NEITHER --
//!      the containers are two sets of `u8` fields, and Rust sees `u8`s.
//!      ⚠⚠⚠ **AND YET DELETING THE BLOCK CHANGES NO ANSWER, which is not what
//!      this comment first predicted and is the more interesting result.**
//!      `controls/arm_safe_bug.rs` is this rung minus the block, in both
//!      idiomatic safe spellings, and on every shipped input it either matches
//!      the CHECKED kernel exactly or PANICS -- never a silently wrong answer,
//!      never undefined behaviour, and Miri never reports anything. The reason
//!      is structural: eviction is insertion-ordered and chains are
//!      newest-first, so TRIM always evicts a chain TAIL and the stale entries
//!      form a SUFFIX; a walk that stops at the first `None` slot loses only
//!      objects that are already gone. ../NOTES.md 4b, and
//!      `controls/rust_arms.json` for the table.
//!      ✅ **That is now a THEOREM rather than an argument** (../NOTES.md 4c,
//!      three steps from slot-monotonicity and never-recycling), and it
//!      survived an attack: 3,257,436 EXHAUSTIVELY enumerated op sequences plus
//!      20,000 randomised ones, **zero** value differences and **zero**
//!      counterexamples, with 17,687 of the 20,000 actually truncating the
//!      walk. ⚠ **Its two hypotheses are the useful part** -- eviction order
//!      equals chain order, and slots are never recycled -- because a cache
//!      that broke either would not have the result. ⚠ And the PANIC is the
//!      typical outcome of the strict spelling, not an exotic one: 80% of
//!      random windows.
//!   3. Slots are **never recycled** (`nmade` only grows), which is `p27`'s and
//!      `p29`'s convention and is what keeps the answer a function of the ops
//!      rather than of the allocator. It is also why every rung, C included,
//!      carries the allocation budget `nmade < SLOTS`: c/kernel.h says so.
//!
//! ⚠ **What the walk's `tab[cur].is_some()` conjunct is, and is not.** It is the
//! `Option` discriminant, and in a CORRECT rung it can never be false -- a chain
//! holds only live objects. It is here because the language demands a decision
//! before it will hand out the record, and `unwrap()` on a `None` would be a
//! panic rather than an answer. **The C rungs have no such test and cannot**;
//! ../NOTES.md 5 counts the asymmetry and says why no cost claim rests on it
//! (this pattern publishes none -- ../NOTES.md 8).
//!
//! Naive in the places R3 tunes: every walk step indexes `tab` and then
//! `as_ref().unwrap()`s it, once per field it reads, so the discriminant and the
//! bounds check are paid several times per step; every splice re-indexes the
//! victim for each of its four links. ⚠ **Whether any of it survives -O3 was NOT
//! measured**: this pattern publishes no rung-to-rung cost at all
//! (../NOTES.md 8).
//!
//! Wrapping arithmetic is spelled `wrapping_mul` / `wrapping_add` because
//! `-C debug-assertions=on` would otherwise panic on the fold, and the C rungs
//! wrap by definition (C99 6.2.5p9).

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
        if c % 4 == 0 {
            // PUT. Walk the hash chain; a hit updates the object in place.
            let mut cur: u8 = bucket[b];
            let mut steps: usize = 0;
            let mut found: bool = false;
            while cur != NIL && tab[cur as usize].is_some() && steps < SLOTS {
                steps = steps + 1;
                if tab[cur as usize].as_ref().unwrap().key == a {
                    found = true;
                    break;
                }
                cur = tab[cur as usize].as_ref().unwrap().hn;
            }
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
            // GET. The same walk, then read the object's payload.
            let mut cur: u8 = bucket[b];
            let mut steps: usize = 0;
            let mut found: bool = false;
            while cur != NIL && tab[cur as usize].is_some() && steps < SLOTS {
                steps = steps + 1;
                if tab[cur as usize].as_ref().unwrap().key == a {
                    found = true;
                    break;
                }
                cur = tab[cur as usize].as_ref().unwrap().hn;
            }
            if found {
                acc = acc.wrapping_mul(31).wrapping_add(
                    tab[cur as usize].as_ref().unwrap().val as u64,
                );
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else if c % 4 == 2 {
            // DEL. The same walk, then a SPLICE out of BOTH lists. DEL arrives
            // ALONG the hash chain, so it holds a chain cursor when it frees --
            // which is why DEL is not the path that forgets.
            let mut cur: u8 = bucket[b];
            let mut steps: usize = 0;
            let mut found: bool = false;
            while cur != NIL && tab[cur as usize].is_some() && steps < SLOTS {
                steps = steps + 1;
                if tab[cur as usize].as_ref().unwrap().key == a {
                    found = true;
                    break;
                }
                cur = tab[cur as usize].as_ref().unwrap().hn;
            }
            if found {
                if tab[cur as usize].as_ref().unwrap().hp != NIL {
                    let q: usize = tab[cur as usize].as_ref().unwrap().hp as usize;
                    tab[q].as_mut().unwrap().hn = tab[cur as usize].as_ref().unwrap().hn;
                } else {
                    bucket[b] = tab[cur as usize].as_ref().unwrap().hn;
                }
                if tab[cur as usize].as_ref().unwrap().hn != NIL {
                    let q: usize = tab[cur as usize].as_ref().unwrap().hn as usize;
                    tab[q].as_mut().unwrap().hp = tab[cur as usize].as_ref().unwrap().hp;
                }
                if tab[cur as usize].as_ref().unwrap().lp != NIL {
                    let q: usize = tab[cur as usize].as_ref().unwrap().lp as usize;
                    tab[q].as_mut().unwrap().ln = tab[cur as usize].as_ref().unwrap().ln;
                } else {
                    head = tab[cur as usize].as_ref().unwrap().ln;
                }
                if tab[cur as usize].as_ref().unwrap().ln != NIL {
                    let q: usize = tab[cur as usize].as_ref().unwrap().ln as usize;
                    tab[q].as_mut().unwrap().lp = tab[cur as usize].as_ref().unwrap().lp;
                } else {
                    tail = tab[cur as usize].as_ref().unwrap().lp;
                }
                tab[cur as usize] = None;
                acc = acc.wrapping_mul(31).wrapping_add(2);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else {
            // TRIM. Reclaim the OLDEST object. It arrives here through the
            // EVICTION list and therefore holds no hash-chain cursor.
            if tail != NIL {
                let v: usize = tail as usize;
                if tab[v].as_ref().unwrap().lp != NIL {
                    let q: usize = tab[v].as_ref().unwrap().lp as usize;
                    tab[q].as_mut().unwrap().ln = NIL;
                } else {
                    head = NIL;
                }
                tail = tab[v].as_ref().unwrap().lp;
                // THE SAFETY LINE. c/kernel.c omits it; this rung writes it out
                // by hand, because nothing in safe Rust knows that this object
                // is a member of a second container.
                let vb: usize = (tab[v].as_ref().unwrap().key % NB as u8) as usize;
                if tab[v].as_ref().unwrap().hp != NIL {
                    let q: usize = tab[v].as_ref().unwrap().hp as usize;
                    tab[q].as_mut().unwrap().hn = tab[v].as_ref().unwrap().hn;
                } else {
                    bucket[vb] = tab[v].as_ref().unwrap().hn;
                }
                if tab[v].as_ref().unwrap().hn != NIL {
                    let q: usize = tab[v].as_ref().unwrap().hn as usize;
                    tab[q].as_mut().unwrap().hp = tab[v].as_ref().unwrap().hp;
                }
                tab[v] = None;
                acc = acc.wrapping_mul(31).wrapping_add(3);
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
