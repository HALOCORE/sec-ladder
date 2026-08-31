//! p34 CONTROL ARM: **can safe Rust publish a second `Rc` reference WITHOUT
//! counting it?** Attempt 1 of 2. Not a rung, and **it is expected NOT TO
//! COMPILE.** Driven by `controls/safe_arms.py`.
//!
//! `c/kernel.c`'s bug is the separation of two things C lets you do separately:
//! *publish a second reference to this object* and *increment its count*. This
//! file is the most direct safe-Rust transcription of that separation --
//! `Rc::clone` replaced by a move out of the borrow the stack already holds --
//! and it is the arm that says whether safe Rust offers the separation at all.
//!
//! **Expected: `error[E0507]: cannot move out of ... which is behind a shared
//! reference`.** `safe_arms.py` asserts the compile FAILS and records the error
//! code; a build that succeeded would refute this row's safe-Rust finding and is
//! a louder result than the failure.
//!
//! ⚠ Everything else in this file is `safe_naive.rs` unchanged, so the compile
//! error is caused by the two edited lines and not by scaffolding.

#![forbid(unsafe_code)]

#[path = "../../../common/driver.rs"]
mod driver;

use std::rc::Rc;

const CAP: usize = 16;
const DLEN: usize = 8;
const SENT: u64 = 251;

pub struct Obj {
    pub len: usize,
    pub data: [u8; DLEN],
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
    let mut stk: [Option<Rc<Obj>>; CAP] = [const { None }; CAP];
    let mut ntop: usize = 0;
    let mut nnew: usize = 0;
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
            if ntop < CAP {
                let mut d: [u8; DLEN] = [0u8; DLEN];
                d[0] = a.wrapping_mul(7).wrapping_add(1);
                stk[ntop] = Some(Rc::new(Obj { len: DLEN, data: d }));
                ntop = ntop + 1;
                nnew = nnew + 1;
                acc = acc.wrapping_mul(31).wrapping_add(a as u64);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else if c % 4 == 1 {
            if ntop > 0 && ntop < CAP {
                // THE ATTEMPT. `Rc::clone(t)` is what safe_naive.rs writes and
                // it increments; this line tries to publish the same reference
                // WITHOUT incrementing, by moving the `Rc` out of the borrow the
                // stack already holds.
                //
                // error[E0507]: cannot move out of `*t` which is behind a
                //               shared reference
                let t: &Rc<Obj> = stk[ntop - 1].as_ref().unwrap();
                stk[ntop] = Some(*t);
                ntop = ntop + 1;
                acc = acc.wrapping_mul(31).wrapping_add(1);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else if c % 4 == 2 {
            if ntop > 0 {
                ntop = ntop - 1;
                stk[ntop] = None;
                acc = acc.wrapping_mul(31).wrapping_add(2);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else {
            if ntop > 0 {
                let v: u8 = stk[(a as usize) % ntop].as_ref().unwrap().data[0];
                acc = acc.wrapping_mul(31).wrapping_add(v as u64);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        }
        o = o + 1;
    }
    acc.wrapping_mul(31).wrapping_add(nnew as u64)
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
