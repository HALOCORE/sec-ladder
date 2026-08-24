//! p19 rung R4 -- unsafe Rust. Every read in the fold is unchecked; what makes
//! that sound is the validation pass above it, and nothing else.
//!
//! **This is AppArmor's own idiom, not a benchmark contrivance**:
//! `verify_dfa()` walks the unpacked table once at policy load and
//! `aa_dfa_match()` then indexes `next[]`, `check[]` and `def[]` with no test
//! at all (c/kernel.h quotes both). p19's R4 is that program.
//!
//! The exec code below is **byte-for-byte** ../verus.rs's, and the gate pins
//! it (`identity: unsafe == verus`). The only difference is that this file
//! asserts the invariant in a comment and that one proves it.
//!
//! SAFETY, per unchecked read:
//!   (1) `buf_get_unchecked(tbl, i)` in the validation loop: `i < TBL` is the
//!       loop condition and `tbl.len() == TBL` by construction.
//!   (2) `buf_get_unchecked(w, p)`: `p < len` is the loop condition and
//!       `w.len() == len` by construction.
//!   (3) `buf_get_unchecked(tbl, st * 256 + b)`: **the one that matters.**
//!       `b <= 255` because it is a `u8`, and `st < NST` is the loop-carried
//!       invariant the validation pass establishes -- every entry it accepted
//!       is `< NST`, and `st` is only ever assigned such an entry. So
//!       `st * 256 + b <= 7*256 + 255 = 2047 < TBL`. ../verus.rs discharges
//!       exactly this, and `c/kernel.c` is the same program with the pass that
//!       establishes it deleted.
//!
//! ⚠ **THE R4 SIDE WAS SEARCHED BEFORE THIS SPELLING WAS CHOSEN**
//! (`.memory/01-ladder.md`; the p10/p27/p38/p22 trap). Three admissible-shaped
//! R4 spellings -- this one, the `get_unchecked` message walk with an explicit
//! index, and a raw-pointer walk -- span **11 Ir/call at m = 4096**, i.e.
//! 0.0027 Ir/byte. The R4 side is **DEGENERATE**, which is the falsifiable way
//! to say it (`.tasks/TASK_026.md` §0 item 4), and the published `R3 - R4` and
//! `R2 - R4` differences do not depend on which of the three is shipped.
//! ⚠ A fourth spelling, absolute `buf[off + ..]` indexing with no sub-slices --
//! p36's shape -- is **+2.25 Ir/byte DEARER**, because the `off` add cannot be
//! folded into the base pointer and the fold unrolls 2x instead of 4x. It is a
//! control, not a rung, and it is why every rung here takes sub-slices
//! (../NOTES.md 10).

#[path = "../../common/driver.rs"]
mod driver;

/// The decoder's table capacity. Must equal `SLB_P19_NST` in c/kernel.h and
/// `NST` in model.py.
const NST: usize = 8;

/// Bytes of transition table: `NST` rows of 256 columns.
const TBL: usize = 2048;

/// What an invalid table folds to.
const REJ: u64 = 0xd1b5_4a32_d192_ed03;

/// The unchecked read. In ../verus.rs this is the pattern's one contracted
/// trusted item; here it is an ordinary `#[inline(always)]` helper, and the two
/// files' exec code is byte-identical.
#[inline(always)]
fn buf_get_unchecked(v: &[u8], i: usize) -> u8 {
    unsafe { *v.get_unchecked(i) }
}

/// The checked sub-slice, as a FUNCTION rather than as an inline expression.
///
/// ⚠ **This shape is forced by the `identity` pin and it is not cosmetic.**
/// ../verus.rs takes its sub-slices with `vstd::slice::slice_subrange`, which
/// is an ordinary out-of-line call at `O0`. Written here as the inline
/// expression `&v[i..j]`, R4 emits the bounds check in line at `O0` and the two
/// rungs land at identity level `differ` -- the only pattern in the tree that
/// would, all 22 others pinning `norel`. As a function they are a call each,
/// so `O0` is `norel` (link layout) and `O3` is `exact` (both inline to the
/// same 235 bytes). ../NOTES.md 5 carries both measurements.
#[inline]
fn subrange(v: &[u8], i: usize, j: usize) -> &[u8] {
    &v[i..j]
}

/// p19's kernel. Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    if len <= TBL {
        return 0;
    }
    let w = subrange(buf, off, off + len);
    let tbl = subrange(w, 0, TBL);
    let mut i: usize = 0;
    while i < TBL {
        if buf_get_unchecked(tbl, i) as usize >= NST {
            return REJ;
        }
        i += 1;
    }
    let mut p: usize = TBL;
    let mut st: usize = 0;
    let mut acc: u64 = 0;
    while p < len {
        let b = buf_get_unchecked(w, p) as usize;
        let ns = buf_get_unchecked(tbl, st * 256 + b) as usize;
        st = ns;
        acc = acc.wrapping_mul(31).wrapping_add(ns as u64);
        p = p + 1;
    }
    acc.wrapping_mul(31).wrapping_add(st as u64)
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
    if stride_w > 0 && stride_w <= n_blob as u64 {
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
