//! p06 rung R3 -- safe-tuned.
//!
//! Same semantics as R2, written the way an experienced Rust programmer writes
//! an in-place reverse: split the range in half with `split_at_mut`, zip the
//! front against the reversed back, and `mem::swap` the pairs. Still zero
//! `unsafe` **in this file** -- and that qualifier is the pattern's TCB result,
//! not a pedantic aside.
//!
//! **R3's trusted base is not zero; it is `std`'s.** `split_at_mut` is the
//! function whose whole job is to hand out two `&mut` into one allocation, and
//! it does that with `unsafe` inside `core` -- `from_raw_parts_mut` on the two
//! halves -- licensed by a bounds check it performs itself. `mem::swap` is
//! `ptr::swap_nonoverlapping`. So the disjointness fact that R4 asserts and R5
//! proves is, here, *discharged by the standard library* and audited by nobody
//! in this repository. ../NOTES.md 6 tabulates all four bases for the one fact,
//! which is p06's answer to "what must move into the trusted base to reach C's
//! assembly".
//!
//! **The window reslice is the TWO-STEP form** (`.memory/01-ladder.md`
//! finding 3, the p04 lever): `buf.split_at(off).1.split_at(len).0` rather than
//! `&buf[off..off + len]`. Both keep both bounds checks; the two-step form is
//! one instruction cheaper because `buf_len - off` is computed in place in a
//! register that is dead afterwards while `off + len` needs a scratch one.
//! ../NOTES.md 9 reports what it is worth here.
//!
//! **What is deliberately NOT reached for: `<[T]>::reverse()` and
//! `<[T]>::rotate_left()`.** Both are single library calls that would delete the
//! three-reverse decomposition this pattern measures, and ../spec.md forbids
//! them **in every rung** rather than in some -- a whole-pattern exclusion,
//! which stays visible and keeps the two sides of the comparison equal, unlike
//! the scoped kind `.memory/01-ladder.md` caught on p13. They are built and
//! priced as controls anyway (../NOTES.md 8), because a fiat whose price is not
//! published is a thumb on the scale.
//!
//! **The copy into the scratch is the same bulk `copy_from_slice` as R2's**, so
//! R2-vs-R3 is the rotate and the fold and nothing else.
//!
//! `if a < b` before the reslice is not a defensive extra: it is R2's and R4's
//! own `while a < b` test spelled once instead of once per iteration, and it is
//! load-bearing, because the second reverse's range is `[r, m)` and `r > m` is
//! reachable in the delete-the-check control (../NOTES.md 7), where
//! `&mut scr[r..m]` would panic on the RANGE rather than on the index and would
//! hide which regime the control is in.

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
        let mut r: usize = w[p + 4] as usize + 256 * (w[p + 5] as usize)
            + 65536 * (w[p + 6] as usize) + 16777216 * (w[p + 7] as usize);
        p = p + 8;
        let m: usize = if nelem < SCR { nelem } else { SCR };
        if len - p < nelem {
            break;
        }
        scr_load(&mut scr, w, p, m);
        p = p + nelem;
        // THE SAFETY LINE. c/kernel.c omits exactly this.
        if m != 0 {
            r = r % m;
        } else {
            r = 0;
        }
        let mut a: usize = 0;
        let mut b: usize = r;
        if a < b {
            let s: &mut [u8] = &mut scr[a..b];
            let n: usize = s.len();
            let (front, back) = s.split_at_mut(n / 2);
            for (x, y) in front.iter_mut().zip(back.iter_mut().rev()) {
                core::mem::swap(x, y);
            }
        }
        a = r;
        b = m;
        if a < b {
            let s: &mut [u8] = &mut scr[a..b];
            let n: usize = s.len();
            let (front, back) = s.split_at_mut(n / 2);
            for (x, y) in front.iter_mut().zip(back.iter_mut().rev()) {
                core::mem::swap(x, y);
            }
        }
        a = 0;
        b = m;
        if a < b {
            let s: &mut [u8] = &mut scr[a..b];
            let n: usize = s.len();
            let (front, back) = s.split_at_mut(n / 2);
            for (x, y) in front.iter_mut().zip(back.iter_mut().rev()) {
                core::mem::swap(x, y);
            }
        }
        acc = scr[..m]
            .iter()
            .fold(acc, |h, &e| h.wrapping_mul(31).wrapping_add(e as u64));
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
