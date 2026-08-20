//! p06 rung R2 -- safe-naive.
//!
//! The mechanical port a working Rust programmer writes first: index `buf[..]`
//! for the header and for every record header, index `scr[..]` for every byte
//! the three reverses touch, and spell the window-relative index `off + p` /
//! `off + i` exactly as the C spells it. Zero `unsafe`.
//!
//! **Safe Rust cannot express the C spelling of an in-place reverse at all**,
//! and that is p06's structural finding. Two cursors walking toward each other
//! into one buffer, with a live `&mut` at each end, is what the borrow checker
//! exists to reject. What R2 *can* do is index -- `let t = scr[a]; let u =
//! scr[b - 1]; scr[a] = u; scr[b - 1] = t;` -- which is four bounds checks per
//! swap and no aliasing question at all, because each index is a separate,
//! momentary access rather than a live borrow. R3
//! reaches for `split_at_mut`, which answers the same disjointness question in
//! the type system at the price of `std`'s own `unsafe`; R4 asserts it; R5
//! proves it. **Four trusted bases for one fact** -- ../NOTES.md 6.
//!
//! **The copy into the scratch is the same bulk `copy_from_slice` in all four
//! Rust rungs and `memcpy` in both C rungs**, deliberately, so that the
//! measured difference between rungs is the ROTATE and not the load
//! (../spec.md). p02's retraction is the precedent.
//!
//! The cursor guards are subtraction-first (`len - p < 8`) in every rung: `p <=
//! len` is maintained by the guards themselves so the subtraction cannot wrap,
//! while the additive form `p + 8 > len` can overflow `usize` and Verus rejects
//! it. R4 must have a byte-identical R5 twin, so the spelling that verifies is
//! the spelling all seven rungs use.
//!
//! **The reduction `if m != 0 { r = r % m } else { r = 0 }` is a SEMANTIC line
//! in the Rust rungs and a SAFETY line only in C.** All four Rust rungs carry
//! it, so no Rust-vs-Rust comparison moves on it; what R2-vs-R4 measures is the
//! bounds checks on top of it, at matched spelling. Deleting it from R2 turns
//! R2 into a rung that agrees with C bit-for-bit in regime 1 and PANICS in
//! regime 2 -- that control is ../NOTES.md 7 and it is the pattern's sharpest
//! row.

#[path = "../../common/driver.rs"]
mod driver;

const SCR: usize = 64;

// THE BULK LOAD, and the one place all seven rungs are held to the same
// spelling: `memcpy` in C, this in all four Rust rungs, and verus.rs's trusted
// `scr_load` -- whose body is the same bulk call -- in R5. THE RECEIVER is
// scoped 2-and-2: this rung writes `dst[..n]`, and unsafe.rs and verus.rs write
// `a` after `split_at_mut(n)` because `RangeTo<usize>` has no
// `SliceIndexSpecImpl` at the pinned vstd. Its price is ZERO at -O3
// (../NOTES.md 6a).
// ../spec.md
// pins it, so that the measured difference between rungs is the ROTATE and not
// the load. p02's retraction is the precedent: one operator flips `bulk_calls`
// and 100% of the delta.
//
// It is a `#[inline(always)]` free function rather than an inline expression
// because R4 must be byte-identical to R5 and R5's copy is a free function.
// (The reason recorded here until TASK_048 -- "R5's copy has to be inside an
// `#[verifier::external_body]` item, there is no vstd spec for
// `copy_from_slice`" -- is FALSE in both halves: the pinned vstd specifies
// `copy_from_slice` at `vstd/std_specs/slice.rs:205`, and R5's `scr_load` is
// VERIFIED, not trusted, as of TASK_048. What survives is the helper BOUNDARY,
// which is what changes LLVM's inlining order.) R4 must be byte-identical
// to R5 at -O3. Written inline in `kernel` instead, R4 is 179 instructions;
// written this way it is 208, because the call boundary changes LLVM's
// inlining order. That 29-instruction delta is the `identity` pin's price on
// this pattern and ../NOTES.md 3 measures what it costs in executed `Ir`.
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
        let mut r: usize = buf[off + p + 4] as usize
            + 256 * (buf[off + p + 5] as usize)
            + 65536 * (buf[off + p + 6] as usize)
            + 16777216 * (buf[off + p + 7] as usize);
        p = p + 8;
        let m: usize = if nelem < SCR { nelem } else { SCR };
        if len - p < nelem {
            break;
        }
        scr_load(&mut scr, buf, off + p, m);
        p = p + nelem;
        // THE SAFETY LINE. c/kernel.c omits exactly this.
        if m != 0 {
            r = r % m;
        } else {
            r = 0;
        }
        let mut a: usize = 0;
        let mut b: usize = r;
        while a < b {
            let t: u8 = scr[a];
            let u: u8 = scr[b - 1];
            scr[a] = u;
            scr[b - 1] = t;
            a = a + 1;
            b = b - 1;
        }
        a = r;
        b = m;
        while a < b {
            let t: u8 = scr[a];
            let u: u8 = scr[b - 1];
            scr[a] = u;
            scr[b - 1] = t;
            a = a + 1;
            b = b - 1;
        }
        a = 0;
        b = m;
        while a < b {
            let t: u8 = scr[a];
            let u: u8 = scr[b - 1];
            scr[a] = u;
            scr[b - 1] = t;
            a = a + 1;
            b = b - 1;
        }
        let mut i: usize = 0;
        while i < m {
            acc = acc.wrapping_mul(31).wrapping_add(scr[i] as u64);
            i = i + 1;
        }
        acc = acc.wrapping_mul(31).wrapping_add(m as u64);
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
