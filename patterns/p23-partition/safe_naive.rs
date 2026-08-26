//! p23 rung R2 -- safe-naive.
//!
//! The mechanical port a working Rust programmer writes first: index `buf[..]`
//! for the header and for every record header, index `scr[..]` for every byte
//! the two scans and the swap touch, and spell the window-relative index
//! `off + p` exactly as the C spells it. Zero `unsafe`.
//!
//! **Safe Rust cannot express the C spelling of the swap at all**, the same way
//! p06's reverses cannot: two cursors walking toward each other into one buffer
//! with a live `&mut` at each end is what the borrow checker exists to reject.
//! What R2 *can* do is index -- `let t = scr[i]; let u = scr[j - 1]; scr[i] =
//! u; scr[j - 1] = t;` -- which is four bounds checks per swap and no aliasing
//! question at all, because each index is a separate momentary access rather
//! than a live borrow. R3 reaches for `<[T]>::swap`, which answers the same
//! disjointness question inside `core`; R4 asserts it; R5 proves it.
//!
//! **The scan guard `i < j` is a SEMANTIC line in the Rust rungs and a SAFETY
//! line only in C.** All four Rust rungs carry it, so no Rust-vs-Rust
//! comparison moves on it; what R2-vs-R4 measures is the bounds checks *on top
//! of* it, at matched spelling. Deleting it from R2 turns R2 into a rung that
//! agrees with C bit-for-bit on every benign record and PANICS on an
//! adversarial one -- that control is ../NOTES.md 7 and it is the pattern's
//! sharpest row, because the panic is the bounds check doing the job the
//! missing conjunct was supposed to do.
//!
//! **The copy into the scratch is the same bulk `copy_from_slice` in all four
//! Rust rungs and `memcpy` in both C rungs**, deliberately, so that the
//! measured difference between rungs is the PARTITION and not the load
//! (../spec.md). p02's retraction is the precedent.
//!
//! The cursor guards are subtraction-first (`len - p < 8`) in every rung: `p <=
//! len` is maintained by the guards themselves so the subtraction cannot wrap,
//! while the additive form `p + 8 > len` can overflow `usize` and Verus rejects
//! it. R4 must have a byte-identical R5 twin, so the spelling that verifies is
//! the spelling all seven rungs use.

#[path = "../../common/driver.rs"]
mod driver;

const SCR: usize = 64;

// THE BULK LOAD, and the one place all seven rungs are held to the same
// spelling: `memcpy` in C, this in safe_naive.rs and safe_tuned.rs, and the
// `split_at_mut` receiver in unsafe.rs and verus.rs -- 2-and-2, for p06's
// measured reason (`..n` is a `RangeTo<usize>`, which has no
// `SliceIndexSpecImpl` at the pinned vstd, so `dst[..n]` cannot be verified at
// all). ../spec.md pins the CALL, so that the measured difference between rungs
// is the PARTITION and not the load.
//
// It is a `#[inline(always)]` free function rather than an inline expression
// because R4 must be byte-identical to R5 and R5's copy is a free function; a
// call boundary changes LLVM's inlining order and p06 measured that at 29
// static instructions.
#[inline(always)]
fn scr_load(dst: &mut [u8; SCR], src: &[u8], from: usize, n: usize) {
    dst[..n].copy_from_slice(&src[from..from + n]);
}

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md. `#[inline(never)]` only in `isolated` builds, so the
// `whole` builds can inline it the way LTO'd C would.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    if len < 4 {
        return 0;
    }
    let nrec: usize = buf[off] as usize + 256 * (buf[off + 1] as usize)
        + 65536 * (buf[off + 2] as usize) + 16777216 * (buf[off + 3] as usize);
    if nrec == 0 {
        return 0;
    }
    let mut scr: [u8; SCR] = [0; SCR];
    let mut acc: u64 = 0;
    let mut p: usize = 4;
    let mut rec: usize = 0;
    while rec < nrec {
        if len - p < 8 {
            break;
        }
        let nelem: usize = buf[off + p] as usize + 256 * (buf[off + p + 1] as usize)
            + 65536 * (buf[off + p + 2] as usize)
            + 16777216 * (buf[off + p + 3] as usize);
        let pv: u8 = buf[off + p + 4];
        p = p + 8;
        let m: usize = if nelem < SCR { nelem } else { SCR };
        if len - p < nelem {
            break;
        }
        scr_load(&mut scr, buf, off + p, m);
        p = p + nelem;
        let mut i: usize = 0;
        let mut j: usize = m;
        while i < j {
            // THE SAFETY LINE, half 1. c/kernel.c omits the `i < j &&`.
            while i < j && scr[i] <= pv {
                i = i + 1;
            }
            // THE SAFETY LINE, half 2. c/kernel.c omits the `i < j &&`.
            while i < j && scr[j - 1] >= pv {
                j = j - 1;
            }
            if i < j {
                let t: u8 = scr[i];
                let u: u8 = scr[j - 1];
                scr[i] = u;
                scr[j - 1] = t;
                i = i + 1;
                j = j - 1;
            }
        }
        let mut q: usize = 0;
        while q < m {
            acc = acc.wrapping_mul(31).wrapping_add(scr[q] as u64);
            q = q + 1;
        }
        acc = acc.wrapping_mul(31).wrapping_add(i as u64);
        rec = rec + 1;
    }
    acc.wrapping_mul(31).wrapping_add(nrec as u64)
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
