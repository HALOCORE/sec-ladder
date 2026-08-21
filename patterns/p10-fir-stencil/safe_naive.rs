//! p10 rung R2 -- safe-naive.
//!
//! The direct port of `c/kernel_hardened.c`: one `&[u8]`, indexed with an
//! absolute offset for every access, no reslice, no iterator. `buf[off + sb + i
//! + j]` and `buf[off + 8 + j]` are **two indexing operations per tap**, which
//! is exactly what p10 exists to price.
//!
//! ⚠ **AND THE PRICE IS NOT WHAT IT LOOKS LIKE, WHICH IS THE PATTERN'S
//! RESULT.** At `-O3` LLVM vectorises this loop -- an SSE2 body of seventeen
//! instructions per eight taps, **byte-identical to `unsafe.rs`'s** -- and the
//! per-tap bounds checks survive only in the **scalar epilogue**, `taps mod 8`
//! of them per output. What R2 pays instead of a per-tap check is a
//! **22-instruction per-output `cmp`/`cmov` chain** computing how many taps may
//! be vectorised without a bounds violation. So the tax is per OUTPUT and per
//! EPILOGUE TAP, and **0.00 per vectorised tap**. ../NOTES.md 8.
//!
//! **The tap loop's spelling is deliberately not pinned** (../spec.md's `idiom`
//! block): indexed, `windows()` and `get_unchecked` are all in contract, and
//! comparing them is the whole experiment. What *is* pinned is that every rung
//! computes the same `2r+1` products of the same operands in the same order
//! into the same wrapping `u32`.
//!
//! **The safety line `if last >= len` is carried by all four Rust rungs.** In
//! Rust it is not what stands between the program and the overread -- the
//! bounds check is -- but it is what makes the Rust rungs return 0 where
//! `c/kernel.c` returns a fold, so it is what keeps the checksum comparable
//! across all seven rungs. ../NOTES.md 7.

#[path = "../../common/driver.rs"]
mod driver;

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md. `#[inline(never)]` only in `isolated` builds, so the
// `whole` builds can inline it the way LTO'd C would.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    if len < 8 {
        return 0;
    }
    let n: usize = buf[off] as usize + 256 * (buf[off + 1] as usize)
        + 65536 * (buf[off + 2] as usize) + 16777216 * (buf[off + 3] as usize);
    let r: usize = buf[off + 4] as usize + 256 * (buf[off + 5] as usize)
        + 65536 * (buf[off + 6] as usize) + 16777216 * (buf[off + 7] as usize);
    let taps: usize = 2 * r + 1;
    // THE WINDOW GUARD, present in every rung: without it `n - 2*r` underflows.
    if n < taps {
        return 0;
    }
    let last: usize = 8 + taps + n - 1;
    // THE SAFETY LINE. c/kernel.c writes `last > len`.
    if last >= len {
        return 0;
    }
    let nout: usize = n - 2 * r;
    let sb: usize = 8 + taps;
    let mut acc: u64 = 0;
    let mut i: usize = 0;
    while i < nout {
        let mut s: u32 = 0;
        let mut j: usize = 0;
        while j < taps {
            s = s.wrapping_add(
                (buf[off + sb + i + j] as u32).wrapping_mul(buf[off + 8 + j] as u32));
            j = j + 1;
        }
        acc = acc.wrapping_mul(31).wrapping_add(s as u64);
        i = i + 1;
    }
    acc.wrapping_mul(31).wrapping_add(nout as u64)
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
    if stride_w >= 8 && stride_w <= n_blob as u64 {
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
