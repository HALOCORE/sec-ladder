//! p23 rung R3 -- safe-tuned.
//!
//! Same semantics as R2, written the way an experienced Rust programmer writes
//! an in-place exchange: reslice the window once, exchange with
//! `<[T]>::swap`, and fold the live prefix with an iterator instead of an
//! index loop. Still zero `unsafe` **in this file** -- and that qualifier is
//! the TCB result, not a pedantic aside.
//!
//! **R3's trusted base is not zero; it is `std`'s.** `<[T]>::swap` is
//! `ptr::swap` under one bounds check it performs itself; `split_at` is
//! `from_raw_parts` under one. So the disjointness fact R4 asserts and R5
//! proves is, here, discharged by the standard library and audited by nobody in
//! this repository. ../NOTES.md 6 tabulates all four bases for the one fact.
//!
//! **The window reslice is the TWO-STEP form** (`.memory/01-ladder.md`
//! finding 3, the p04 lever): `buf.split_at(off).1.split_at(len).0` rather than
//! `&buf[off..off + len]`. Both keep both bounds checks; the two-step form is
//! one instruction cheaper because `buf_len - off` is computed in place in a
//! register that is dead afterwards while `off + len` needs a scratch one.
//!
//! **The three levers were measured SEPARATELY and the answer is worth having**
//! (../NOTES.md 9, and the closed decomposition is repeated in ../spec.md's
//! `why`). ⚠ **Those figures are a PROBE's** (`.temp/t101/cost23.rs`, marginal
//! whole-program `Ir`/call under a fixed driver), and a probe measures a slope
//! whose intercept is a property of the probe (`.memory/03-measurement.md`), so
//! what transfers is the ORDERING and the ZERO, not the magnitudes: against R2
//! at the median-pivot band, `<[T]>::swap` alone is **0.00** -- it compiles to
//! the same bytes as R2's four indexed accesses -- the reslice alone is
//! **-38.00** and the iterator fold alone is **-16.00**, and the two together
//! are **-46.00** rather than -54.00. So R3's whole advantage over R2 here is
//! the *header* reslice and the *fold*, and **none of it is the swap**, which
//! is the operation the pattern is about. ../NOTES.md 9 re-fits all of it
//! against the SHIPPED cells.
//!
//! **What is deliberately NOT reached for: `<[T]>::iter().position()` /
//! `rposition()` for the two scans.** That spelling is the most idiomatic thing
//! Rust offers for "advance while", and ../spec.md forbids it **in every rung**
//! rather than in some -- a whole-pattern exclusion, which stays visible and
//! keeps the two sides equal, unlike the scoped kind `.memory/01-ladder.md`
//! caught on p13. It is priced as a control anyway (../NOTES.md 9), because a
//! fiat whose price is not published is a thumb on the scale -- and the price
//! is the reason it is excluded: **it is the DEAREST R3 spelling at the median
//! pivot and the CHEAPEST at the minimum**, so a rung built on it would make
//! p23's safe-side headline a function of which band was measured.
//!
//! **The copy into the scratch is the same bulk `copy_from_slice` as R2's**, so
//! R2-vs-R3 is the partition, the reslice and the fold and nothing else.
//!
//! The scan guard `i < j` is a SEMANTIC line here, exactly as in R2, R4 and R5;
//! only c/kernel.c omits it.

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
#[inline(always)]
fn scr_load(dst: &mut [u8; SCR], src: &[u8], from: usize, n: usize) {
    dst[..n].copy_from_slice(&src[from..from + n]);
}

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    if len < 4 {
        return 0;
    }
    let w: &[u8] = buf.split_at(off).1.split_at(len).0;
    let nrec: usize = w[0] as usize + 256 * (w[1] as usize)
        + 65536 * (w[2] as usize) + 16777216 * (w[3] as usize);
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
        let nelem: usize = w[p] as usize + 256 * (w[p + 1] as usize)
            + 65536 * (w[p + 2] as usize) + 16777216 * (w[p + 3] as usize);
        let pv: u8 = w[p + 4];
        p = p + 8;
        let m: usize = if nelem < SCR { nelem } else { SCR };
        if len - p < nelem {
            break;
        }
        scr_load(&mut scr, w, p, m);
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
                scr.swap(i, j - 1);
                i = i + 1;
                j = j - 1;
            }
        }
        acc = scr[..m]
            .iter()
            .fold(acc, |h, &e| h.wrapping_mul(31).wrapping_add(e as u64));
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
