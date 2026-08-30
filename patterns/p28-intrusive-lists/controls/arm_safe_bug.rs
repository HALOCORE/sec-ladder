//! p28 CONTROLS -- **safe Rust with the safety line DELETED**, and nothing else
//! changed. `#![forbid(unsafe_code)]`.
//!
//! Built and run by `controls/rust_arms.py`. Not a rung, not in the matrix, not
//! measured.
//!
//! ⚠⚠⚠ **WHAT IT MEASURES, AND THE ANSWER IS NOT THE ONE THIS FILE FIRST
//! PREDICTED.** `../safe_naive.rs` writes the nine-line chain splice out by hand
//! and says nothing in the type system asks it to. This file is that claim's
//! experiment: `../safe_tuned.rs` with the block deleted and with no other
//! semantic edit. The first draft of this header predicted *"a WRONG ANSWER"*,
//! and `../safe_naive.rs`'s first draft said the same. **Both were false.**
//! `controls/rust_arms.json` carries the numbers; here is what they say:
//!
//!     input                     checked      strict spelling   lenient spelling
//!     adversarial-uaf-read      correct      correct           correct
//!     adversarial-uaf-head      correct      correct           correct
//!     adversarial-uaf-write     correct      correct           correct
//!     adversarial-many          correct      **PANIC** (101)   correct
//!
//! **In the safe slot-table representation, deleting p28's safety line does not
//! change the ANSWER on any input this pattern ships.** Its only trace is a
//! `None` where `.unwrap()` expects `Some`.
//!
//! ⚠ **AND THERE IS A REASON, not a coincidence, which is worth more than the
//! table.** The eviction list is insertion-ordered and every chain is
//! newest-first, so **the globally oldest object in a bucket is that bucket's
//! chain TAIL** -- TRIM always evicts a chain tail, and the entries the buggy
//! rung leaves behind therefore form a SUFFIX of the chain. Truncating the walk
//! at the first `None` slot loses only objects that are already gone. So the
//! safe rung's walk sees exactly the live prefix, which is exactly the correct
//! chain, and GET and DEL are right for a structural reason rather than by luck.
//! (⚠ This is an ARGUMENT plus a measurement over the shipped inputs, not a
//! proof. A cache whose eviction order and chain order disagreed would not have
//! it.) The one path that notices is PUT, which writes the old chain head's `hp`
//! without walking to it -- and when every object in the bucket has been
//! evicted, that head is a `None` slot.
//!
//! **So safe Rust's answer to p28's omission is: NOTHING, or a PANIC, decided by
//! the input and by which of two idiomatic safe spellings the port uses. Never
//! undefined behaviour, and -- on these inputs -- never a silently wrong
//! answer.** Miri is silent on every input in both spellings
//! (`controls/rust_arms.py` runs it) while it reports UB on
//! `controls/arm_rawptr.rs`'s bug arm on all four adversarial inputs. **That
//! contrast is the row's safe-Rust result**, and it is a STRONGER outcome than
//! `p32`'s: p32's safe rung reproduces its buggy C bit for bit, and p28's cannot
//! reproduce its buggy C at all.
//!
//! ⚠ **The ONE structural difference from `../safe_tuned.rs`**: the six link
//! writes go through `write_link` below, so both spellings live in one binary
//! and can be compared in one run. `write_link`'s `strict` branch is what
//! `.as_mut().unwrap()` does and its `lenient` branch is what `if let` does;
//! nothing else differs from the shipped rung except the deleted safety line.
//!
//! ⚠ It is not a claim that safe Rust is unsafe. `tab[i]` is bounds-checked,
//! `as_mut()` is discriminant-checked, and the program is memory-safe
//! throughout. The finding is that MEMORY SAFETY IS NOT THE PROPERTY THIS ROW
//! IS ABOUT -- and here, unusually, the safe representation happens to deliver
//! the FUNCTIONAL property too, for a reason nothing in the type system knows.
//!
//! usage: `P28_SAFE=strict|lenient ./arm_safe_bug <input-file>`  (default strict)

#![forbid(unsafe_code)]

#[path = "../../../common/driver.rs"]
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

/// The six link writes of `../safe_tuned.rs`, routed through one place so that
/// the two idiomatic safe spellings can be compared in one binary. See the
/// header. `which`: 0 = `lp`, 1 = `ln`, 2 = `hn`, 3 = `hp`.
fn write_link(tab: &mut [Option<Box<Obj>>; SLOTS], i: u8, which: u8, val: u8,
              strict: bool) {
    match tab[i as usize].as_mut() {
        Some(ob) => match which {
            0 => ob.lp = val,
            1 => ob.ln = val,
            2 => ob.hn = val,
            _ => ob.hp = val,
        },
        None => {
            if strict {
                // What `.as_mut().unwrap()` does, spelled so the diagnostic
                // says which link named a freed object.
                panic!("p28 arm_safe_bug: link names slot {}, which this \
                        window has already freed", i);
            }
            // lenient: `if let Some(..)` simply skips the write.
        }
    }
}

pub fn kernel(buf: &[u8], off: usize, len: usize, strict: bool) -> u64 {
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
            if tail != NIL {
                let v: usize = tail as usize;
                let (_vk, lpv, _hpv, _hnv) = match tab[v].as_ref() {
                    Some(ob) => (ob.key, ob.lp, ob.hp, ob.hn),
                    None => (0u8, NIL, NIL, NIL),
                };
                if lpv != NIL {
                    write_link(&mut tab, lpv, 1, NIL, strict);
                } else {
                    head = NIL;
                }
                tail = lpv;
                // THE SAFETY LINE IS DELETED HERE. `../safe_tuned.rs` has the
                // nine-line chain splice between `tail = lpv;` and the free
                // below; this file has nothing, exactly as `c/kernel.c` has
                // nothing.
                tab[v] = None;
                acc = acc.wrapping_mul(31).wrapping_add(3);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
            o = o + 1;
            continue;
        }
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
                    write_link(&mut tab, head, 0, s, strict);
                } else {
                    tail = s;
                }
                head = s;
                if bucket[b] != NIL {
                    write_link(&mut tab, bucket[b], 3, s, strict);
                }
                bucket[b] = s;
                nmade = nmade + 1;
                acc = acc.wrapping_mul(31).wrapping_add(a as u64);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else if c % 4 == 1 {
            if found {
                acc = acc.wrapping_mul(31).wrapping_add(
                    tab[cur as usize].as_ref().unwrap().val as u64,
                );
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else {
            if found {
                let (hpv, hnv, lpv, lnv) = match tab[cur as usize].as_ref() {
                    Some(ob) => (ob.hp, ob.hn, ob.lp, ob.ln),
                    None => (NIL, NIL, NIL, NIL),
                };
                if hpv != NIL {
                    write_link(&mut tab, hpv, 2, hnv, strict);
                } else {
                    bucket[b] = hnv;
                }
                if hnv != NIL {
                    write_link(&mut tab, hnv, 3, hpv, strict);
                }
                if lpv != NIL {
                    write_link(&mut tab, lpv, 1, lnv, strict);
                } else {
                    head = lnv;
                }
                if lnv != NIL {
                    write_link(&mut tab, lnv, 0, lpv, strict);
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
    acc.wrapping_mul(31).wrapping_add(nmade as u64)
}

fn main() {
    let strict = std::env::var("P28_SAFE").unwrap_or_else(|_| "strict".into())
        != "lenient";
    let path = driver::arg_path();
    let inp = driver::load(&path);
    let (stride_w, bytes) = driver::head1_u64_bytes(&inp);
    let n_iters: u64 = inp.n_iters;
    let n_blob: usize = bytes.len();
    let buf: &[u8] = bytes.as_slice();
    let mut acc: u64 = 0;
    if stride_w >= 4 && stride_w <= n_blob as u64 {
        let stride: usize = stride_w as usize;
        let nwin: u64 = (n_blob / stride) as u64;
        let mut it: u64 = 0;
        while it < n_iters {
            let k: usize = ((acc as u128 * nwin as u128) >> 64) as usize;
            let r: u64 = kernel(buf, k * stride, stride, strict);
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    driver::emit(acc);
}
