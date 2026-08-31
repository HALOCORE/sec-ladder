//! p34 rung R2 -- safe Rust, naive.
//!
//! ⚠⚠ **THE REPRESENTATION IS NOT A CHOICE, AND NEITHER IS THE RESULT.** A
//! reference-counted heap object in safe Rust is `Rc<T>`, and `Rc` owns the
//! count. Three consequences, and together they are this row's safe-Rust
//! finding:
//!
//!   1. `Option<Rc<Obj>>` is **niche-optimised to one pointer word** -- `None`
//!      *is* the null pointer -- so this stack is byte-for-byte C's `stk[]`.
//!      The safe representation IS the C representation, arrived at by
//!      construction. p27's `Option<Box<u8>>` result, one axis over.
//!   2. **THERE IS NO SITE AT WHICH THIS RUNG COULD FORGET THE RETAIN.**
//!      `Rc::clone` increments and hands back the new reference in one
//!      operation; there is no way to obtain a second `Rc<Obj>` without it, and
//!      a borrow (`&Rc<Obj>`) cannot be stored in the stack array because the
//!      borrow checker ties it to the array it came from. **c/kernel.c's bug is
//!      exactly the separation of "publish a reference" from "count it", and
//!      safe Rust does not offer the separation.** `../controls/safe_arms.py`
//!      measures that claim rather than asserting it, and it also measures the
//!      OTHER branch -- an index-arena port, which is equally safe Rust and
//!      which reproduces the buggy C bit for bit.
//!   3. **There is no epilogue in this rung.** Dropping the stack releases every
//!      reference still held; the loop the C and unsafe rungs write by hand is
//!      written by the language. ../NOTES.md 5 prices the difference.
//!
//! Naive in the two places R3 tunes: the op walk is a cursor and an `if` chain,
//! and the READ path asks `as_ref()` and then `unwrap()`s -- a discriminant test
//! plus a panicking unwrap on the same slot. Every index is a plain `stk[i]` and
//! a plain `buf[off + p]`, so rustc emits its own bounds check on top of the
//! guard the algorithm already has; ../NOTES.md 5 is what that costs.
//!
//! Wrapping arithmetic is spelled `wrapping_mul` / `wrapping_add` because
//! `-C debug-assertions=on` would otherwise panic on the fold, and the C rungs
//! wrap by definition (C99 6.2.5p9).

#[path = "../../common/driver.rs"]
mod driver;

use std::rc::Rc;

const CAP: usize = 16;
const DLEN: usize = 8;
const SENT: u64 = 251;

/// The object, WITHOUT a reference count: `Rc` owns the count and keeps it in
/// its own header, ahead of this struct. That is the one field R4's and R5's
/// `Obj` has and this one does not, and it is the whole of the difference
/// between a rung that can express p34's bug and a rung that cannot.
pub struct Obj {
    pub len: usize,
    pub data: [u8; DLEN],
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
                // THE ALLOCATION. `Rc::new` is one allocation of the count pair
                // plus the object, the same allocator C's `malloc` uses.
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
                // THE RETAIN, and the line C forgets -- except that here it is
                // not a line one could forget. `Rc::clone` IS the publication of
                // the second reference, and the increment is inside it.
                let t: Rc<Obj> = Rc::clone(stk[ntop - 1].as_ref().unwrap());
                stk[ntop] = Some(t);
                ntop = ntop + 1;
                acc = acc.wrapping_mul(31).wrapping_add(1);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else if c % 4 == 2 {
            if ntop > 0 {
                // THE RELEASE. Dropping the `Rc` decrements the count and frees
                // the object at zero -- the decrement, the test and the `free`
                // in one operation that cannot come apart.
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
    // No epilogue: `stk` is dropped here and that releases every reference still
    // held, freeing every object whose count reaches zero.
    acc.wrapping_mul(31).wrapping_add(nnew as u64)
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
