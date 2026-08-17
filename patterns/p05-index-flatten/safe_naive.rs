//! p05 rung R2 -- safe-naive.
//!
//! The mechanical port a working Rust programmer writes first: index `buf[..]`
//! for the header and for every element of the matrix, with the flattened index
//! spelled `off + 4 + i * ncol + j` exactly as the C spells it, and fold with
//! `for j in 0..ncol`. Zero `unsafe`.
//!
//! **This is the first rung in this project whose measured loop vectorises**,
//! and that is what p05 exists to measure. Every earlier pattern folded with
//! `acc = acc*31 + b`, a serial dependence chain, so the safe-vs-unsafe gap had
//! only ever been measured on a scalar loop on both sides. Here the inner loop
//! is a plain associative sum, so LLVM is free to widen it -- and the question
//! the pattern asks is whether a per-element bounds check stops it.
//!
//! Measured answer (NOTES.md 3, and it is not the answer TASK_013 predicted):
//! **it does not.** LLVM hoists the check out of the vector body, and this
//! rung's vector loop is instruction-for-instruction R4's. What the check costs
//! instead is (a) a per-*row* preamble that computes how many iterations are
//! safe, and (b) a live bounds check in the **scalar epilogue** -- the
//! `ncol mod 8` elements the vector body cannot take. So the tax is O(nrow),
//! not O(nrow*ncol), and its size depends on `ncol`'s residue.
//!
//! **Do not read this rung's number as a bounds-check tax without the
//! decomposition in NOTES.md 3.** That mistake was made on p02 and retracted,
//! and nearly made again on p16. One loop at a time, and on p05 there is a
//! third possibility neither of those had: the residue of the vector width.

#[path = "../../common/driver.rs"]
mod driver;

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md. `#[inline(never)]` only in `isolated` builds, so the
// `whole` builds can inline it the way LTO'd C would.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    if len < 4 {
        return 0;
    }
    let nrow: usize = buf[off] as usize + 256 * (buf[off + 1] as usize);
    let ncol: usize = buf[off + 2] as usize + 256 * (buf[off + 3] as usize);
    if nrow == 0 || ncol == 0 {
        return 0;
    }
    let avail: usize = len - 4;
    if nrow * ncol > avail {
        return 0;
    }
    let mut acc: u64 = 0;
    for i in 0..nrow {
        let mut row: u32 = 0;
        for j in 0..ncol {
            row = row.wrapping_add(buf[off + 4 + i * ncol + j] as u32);
        }
        acc = acc.wrapping_mul(31).wrapping_add(row as u64);
    }
    acc.wrapping_mul(31).wrapping_add((nrow * ncol) as u64)
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
