//! p49 CONTROL ARM: **`Rc<RefCell<Buf>>` -- the bug, in SAFE Rust, with no
//! `unsafe` anywhere.**
//!
//! ⚠⚠ **THIS ARM REPRODUCES `c/kernel.c` BIT FOR BIT.** `CLAUDE.md` rule 6
//! names *"safe Rust reproduces the bug bit-identically"* as a FINDING and never
//! a kill; on this row it is the finding, and this file is half the measurement.
//! `controls/safe_arms.py` builds it, runs it against every shipped input and
//! asserts the equality.
//!
//! **Why it works.** `Rc<RefCell<T>>` is the idiomatic safe spelling of *shared
//! and mutable*, which is precisely what an intern pool with an in-place
//! cycle-breaker is. Deduplication is `Rc::clone`; the write-through is
//! `rec.borrow_mut().data[0] = 0`. The runtime borrow check passes -- there is
//! only ever ONE borrow outstanding at a time -- so nothing panics, nothing is
//! undefined, and the corruption crosses the ownership boundary exactly as it
//! does in C.
//!
//! ⚠ **The borrow checker has nothing to say here, and neither does `RefCell`'s
//! dynamic one.** They are about *aliasing an object while it is being mutated*.
//! p49's bug is about *whether the object is yours to mutate at all*, and no
//! Rust rule states that.
//!
//! Its sibling `arm_rc_makemut.rs` is this program with `RefCell` removed and
//! `Rc::make_mut` in its place, **plus a 20-line accounting block at the write
//! site that this file does not have** — a `strong_count` test, a budget
//! refusal, a budget charge and a flag clear, none of which is the safety.
//! ⚠ *"The same program with one type changed"* was the shipped claim and it
//! was measured FALSE (`TASK_162` MAJOR 3). ✅ **With that block deleted the
//! two files ARE one type apart and still disagree on all five discriminating
//! inputs, so the type is what rules the bug out.** `../NOTES.md` 3e.
//!
//! Not a rung: it is never built by `harness/build.py` and never measured.

#[path = "../../../common/driver.rs"]
mod driver;

use std::cell::RefCell;
use std::rc::Rc;

const MEM: usize = 64;
const ARENA: usize = 20;
const NENT: usize = 8;
const NREC: usize = 12;
const NKEY: u8 = 7;
const MAXW: u8 = 6;
const THRESH: u8 = 4;
const SENT: u64 = 251;

/// One BUFFER. `len` is how many bytes of `data` are the string.
#[derive(Clone)]
pub struct Buf {
    pub len: u8,
    pub data: [u8; MAXW as usize],
}

fn cbyte(key: u8, j: u8) -> u8 {
    key.wrapping_mul(7).wrapping_add(j.wrapping_mul(13)).wrapping_add(1)
}

fn make(key: u8, w: u8) -> Buf {
    let mut d = [0u8; MAXW as usize];
    let mut j: u8 = 0;
    while j < w {
        d[j as usize] = cbyte(key, j);
        j = j + 1;
    }
    Buf { len: w, data: d }
}

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
    // THE DEDUP TABLE: the string `(key, w)` -> the buffer it names.
    let mut table: Vec<(u8, u8, Rc<RefCell<Buf>>)> = Vec::new();
    // THE RECORDS: the buffer, and whether this record is one of several naming
    // it. The flag is bookkeeping for the CHECKSUM only -- nothing reads it
    // before the write, which is the bug.
    let mut recs: Vec<(Rc<RefCell<Buf>>, u8)> = Vec::new();
    let mut arena_used: usize = 0;
    let mut priv_used: usize = 0;
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
        let w: u8 = 1 + a % MAXW;
        let key: u8 = a % NKEY;
        let v: u64 = if c % 4 == 0 || c % 4 == 1 {
            if recs.len() >= NREC {
                SENT
            } else if w < THRESH {
                match table.iter().position(|e| e.0 == key && e.1 == w) {
                    // A DEDUP HIT: `Rc::clone` publishes a second reference to
                    // ONE buffer. Correct, intended, and the contract.
                    Some(k) => {
                        recs.push((Rc::clone(&table[k].2), 1));
                        a as u64
                    },
                    None => {
                        if table.len() >= NENT || arena_used + (w as usize) > ARENA {
                            SENT
                        } else {
                            let b = Rc::new(RefCell::new(make(key, w)));
                            table.push((key, w, Rc::clone(&b)));
                            recs.push((b, 1));
                            arena_used = arena_used + w as usize;
                            a as u64
                        }
                    },
                }
            } else if priv_used + (w as usize) > MEM - ARENA {
                SENT
            } else {
                recs.push((Rc::new(RefCell::new(make(key, w))), 0));
                priv_used = priv_used + w as usize;
                a as u64
            }
        } else if c % 4 == 2 {
            if recs.is_empty() {
                SENT
            } else {
                let t: usize = (a as usize) % recs.len();
                // >>> THE BUG, IN SAFE RUST. `borrow_mut()` hands out a `&mut`
                // to storage this record may be sharing with another, and
                // nothing anywhere asks whether it is this record's to write.
                // The dynamic borrow check passes: there is one borrow. <<<
                recs[t].0.borrow_mut().data[0] = 0;
                2
            }
        } else {
            if recs.is_empty() {
                SENT
            } else {
                let t: usize = (a as usize) % recs.len();
                let b = recs[t].0.borrow();
                let mut x: u64 = 0;
                let mut j: u8 = 0;
                while j < b.len {
                    x = x.wrapping_mul(31).wrapping_add(b.data[j as usize] as u64);
                    j = j + 1;
                }
                x
            }
        };
        acc = acc.wrapping_mul(31).wrapping_add(v);
        o = o + 1;
    }
    let nrec = recs.len();
    for (b, shd) in recs.iter() {
        let bb = b.borrow();
        let mut j: u8 = 0;
        while j < bb.len {
            acc = acc.wrapping_mul(31).wrapping_add(bb.data[j as usize] as u64);
            j = j + 1;
        }
        acc = acc.wrapping_mul(31).wrapping_add(*shd as u64);
    }
    acc.wrapping_mul(31).wrapping_add(nrec as u64)
}

fn main() {
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
            let r: u64 = kernel(buf, k * stride, stride);
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    driver::emit(acc);
}
