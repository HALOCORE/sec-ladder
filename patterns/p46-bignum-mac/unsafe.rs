//! p46 rung R4 -- unsafe Rust. Every read and write in the fold is unchecked;
//! what makes that sound is the output-side bound above it, and nothing else.
//!
//! **This is the shipped bignum idiom, not a benchmark contrivance**: OpenSSL's
//! `bn_mul_add_words()` indexes `rp[]` and `ap[]` with no test at all, licensed
//! by `BN_mul()` having called `bn_wexpand(rr, top)` first (c/kernel.h quotes
//! the shape). p46's R4 is that program.
//!
//! The exec code below is **byte-for-byte** ../verus.rs's, and the gate pins it
//! (`identity: unsafe == verus`). The only difference is that this file asserts
//! the invariant in a comment and that one proves it.
//!
//! SAFETY, per unchecked access:
//!   (1) `buf_get_unchecked(w, p)` inside `load_u64`: the caller checks
//!       `p + 8 <= w.len()` structurally -- `8 + 8*(n + m) <= len` was tested
//!       above and every limb offset is `8 + 8*k` with `k < n + m`.
//!   (2) `arr_get_unchecked(&bl, j)` / `arr_set_unchecked(&mut bl, ...)`:
//!       `j < m <= 255 < BCAP`, because `m` came out of a single byte.
//!   (3) `arr_get_unchecked(&out, i + j)` and the matching write: **the ones
//!       that matter.** `i < n` and `j < m` are the loop conditions, and
//!       `n + m <= OUTCAP` is the test `c/kernel.c` omits, so
//!       `i + j <= n + m - 2 < OUTCAP`. `out[i + m]` is bounded the same way by
//!       `i <= n - 1`. ../verus.rs discharges exactly this, and `c/kernel.c` is
//!       the same program with the test that establishes it deleted.
//!   (4) the MAC itself cannot overflow `u128`: `(2^64-1)^2 + 2*(2^64-1)` is
//!       `2^128 - 1` exactly. **No rung checks that and none has to**; it is a
//!       proof obligation with no runtime counterpart (../NOTES.md 6).
//!
//! ⚠⚠ **THE R4 SIDE WAS SEARCHED BEFORE THIS SPELLING WAS CHOSEN, AND THE
//! SEARCH FOUND A CHEAPER SPELLING THAT IS NOT A RUNG** (`.memory/01-ladder.md`;
//! the p10/p27/p38/p22 trap). Three admissible R4 spellings were measured on
//! the shipped shape: this one, the `mac` helper written out in the loop body
//! (`0.00` Ir/call flat) and a running output index `oi` (`-2.00` flat). Both
//! levers are flat in `n` and in `m`, so this side's span is **2 Ir/call** and
//! the published `R3 - R4` law does not depend on which of the three ships
//! (../NOTES.md 8b). ⚠ This comment said `+25` Ir/call flat for the running
//! index; that was `.temp/t89/cost.rs`'s `r4d` row -- a PRE-BUILD probe number,
//! retracted with the rest of that probe (../NOTES.md 0b) -- and it disagreed
//! with this pattern's own NOTES 8b as shipped.
//!
//! A fourth spelling, `r4_mutreslice` -- a checked per-row reslice with
//! unchecked indexing inside it -- is **`1.5` Ir/MAC CHEAPER than this rung and
//! cheaper than every safe spelling too**, and it is **NOT a rung.**
//!
//! ⚠⚠ **THE REASON THIS COMMENT USED TO GIVE FOR THAT IS FALSE AND IS
//! RETRACTED** (TASK_089_REVIEW B1, settled at TASK_092). It said the pinned
//! vstd cannot specify a mutable sub-slice -- *"`slice_subrange` covers `&[T]`
//! only while `ExSliceIndex::index_mut` carries a `requires` and no
//! `ensures`"*. `vstd/slice.rs`'s `ExSliceIndex` is a **trait declaration, not
//! the specification**; `~/tools/verus/vstd/std_specs/slice.rs` ships
//! `assume_specification[ <Range<usize> as SliceIndex<[T]>>::index_mut ]` with
//! a full **value-level** `final(r)@ == final(slice)@.subrange(..)`, and
//! `r4_mutreslice`'s **full R5 verifies: `21 verified, 0 errors`**, mutation
//! tested twice.
//!
//! **What actually disqualifies it, measured** (../NOTES.md 0c):
//!   (a) it costs **two new trusted items** -- unchecked read and write through
//!       a `&mut [u64]` -- because the pinned vstd has **zero** occurrences of
//!       `get_unchecked` anywhere. 5 `external_body` items become 7, 3
//!       contracted become 5. That is the same disqualifier ../spec.md's own
//!       named-spelling paragraph records for p16's `r4_hdr`.
//!   (b) its R4/R5 pair is **`differ` at `-O3`**: `R5 - R4 = 15n + 1` Ir/call,
//!       against this pattern's pinned `identity: unsafe == verus, O3 exact`.
//!       LLVM keeps the per-row reslice bound test in the R5 build (+3/row) and
//!       does not fold `load_u64`'s eight byte reads into one `mov` (+12/row).
//!
//! **So this rung is off the floor of its own class, by a known amount, for a
//! reason that is a property of the TCB and of the identity pin rather than of
//! the program** -- and that is why ../safe_tuned.rs beats it. Do not read
//! p46's `R3 - R4` as a safety number, and read ../NOTES.md 0c before quoting
//! "safe beats unsafe": it says exactly what that headline is contingent on.

#[path = "../../common/driver.rs"]
mod driver;

/// The product scratch capacity, in 64-bit limbs. Must equal
/// `SLB_P46_OUTCAP` in c/kernel.h and `OUTCAP` in model.py.
const OUTCAP: usize = 96;

/// The b-operand scratch, in 64-bit limbs. Sized for the DECLARED TYPE's full
/// range (`m` is a byte), so the pre-decode below can never leave it.
const BCAP: usize = 256;

/// What an over-long product folds to.
const REJ: u64 = 0x9e37_79b9_7f4a_7c15;

/// The unchecked byte read. In ../verus.rs this is a contracted trusted item;
/// here it is an ordinary `#[inline(always)]` helper.
#[inline(always)]
fn buf_get_unchecked(v: &[u8], i: usize) -> u8 {
    unsafe { *v.get_unchecked(i) }
}

/// The unchecked limb read from a fixed-capacity array.
#[inline(always)]
fn arr_get_unchecked<T: Copy, const N: usize>(v: &[T; N], i: usize) -> T {
    unsafe { *v.get_unchecked(i) }
}

/// The unchecked limb WRITE. p46's out-of-bounds access is a write, which is
/// what separates its bug from p05's read.
#[inline(always)]
fn arr_set_unchecked<T: Copy, const N: usize>(v: &mut [T; N], i: usize, x: T) {
    unsafe {
        *v.get_unchecked_mut(i) = x;
    }
}

/// The checked sub-slice, as a FUNCTION rather than as an inline expression.
///
/// ⚠ **This shape is forced by the `identity` pin and it is not cosmetic**
/// (p19 measured it first). ../verus.rs takes its window with
/// `vstd::slice::slice_subrange`, which is an ordinary out-of-line call at
/// `O0`. Written here as the inline expression `&v[i..j]`, R4 emits the bounds
/// check in line at `O0` and the two rungs land at identity level `differ`. As
/// a function they are a call each, so `O0` is `norel` (link layout) and `O3`
/// is `exact` (both inline to the same bytes).
#[inline]
fn subrange(v: &[u8], i: usize, j: usize) -> &[u8] {
    &v[i..j]
}

/// Little-endian limb decode, unchecked. The ADDITIVE spelling, byte-for-byte
/// the other rungs'.
#[inline(always)]
fn load_u64(w: &[u8], p: usize) -> u64 {
    buf_get_unchecked(w, p) as u64 + 256 * (buf_get_unchecked(w, p + 1) as u64)
        + 65536 * (buf_get_unchecked(w, p + 2) as u64)
        + 16777216 * (buf_get_unchecked(w, p + 3) as u64)
        + 4294967296 * (buf_get_unchecked(w, p + 4) as u64)
        + 1099511627776 * (buf_get_unchecked(w, p + 5) as u64)
        + 281474976710656 * (buf_get_unchecked(w, p + 6) as u64)
        + 72057594037927936 * (buf_get_unchecked(w, p + 7) as u64)
}

/// One schoolbook multiply-accumulate step, exact in 128 bits.
#[inline(always)]
fn mac(ai: u64, bj: u64, c: u64, carry: u64) -> (u64, u64) {
    let t: u128 = (ai as u128) * (bj as u128) + (c as u128) + (carry as u128);
    let lo: u64 = t as u64;
    let hi: u64 = (t >> 64) as u64;
    (lo, hi)
}

/// p46's kernel. Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    if len < 8 {
        return 0;
    }
    let w = subrange(buf, off, off + len);
    let n: usize = buf_get_unchecked(w, 0) as usize;
    let m: usize = buf_get_unchecked(w, 1) as usize;
    if n == 0 || m == 0 {
        return 0;
    }
    if 8 + 8 * (n + m) > len {
        return 0;
    }
    // >>> THE SAFETY LINE. c/kernel.c omits this test. <<<
    if n + m > OUTCAP {
        return REJ;
    }
    let mut bl: [u64; BCAP] = [0u64; BCAP];
    let mut jd: usize = 0;
    while jd < m {
        arr_set_unchecked(&mut bl, jd, load_u64(w, 8 + 8 * (n + jd)));
        jd = jd + 1;
    }
    let mut out: [u64; OUTCAP] = [0u64; OUTCAP];
    let mut i: usize = 0;
    while i < n {
        let ai: u64 = load_u64(w, 8 + 8 * i);
        let mut carry: u64 = 0;
        let mut j: usize = 0;
        while j < m {
            let bj: u64 = arr_get_unchecked(&bl, j);
            let c: u64 = arr_get_unchecked(&out, i + j);
            let (lo, hi) = mac(ai, bj, c, carry);
            arr_set_unchecked(&mut out, i + j, lo);
            carry = hi;
            j = j + 1;
        }
        arr_set_unchecked(&mut out, i + m, carry);
        i = i + 1;
    }
    let mut acc: u64 = 0;
    let mut k: usize = 0;
    while k < n + m {
        acc = acc.wrapping_mul(31).wrapping_add(arr_get_unchecked(&out, k));
        k = k + 1;
    }
    acc.wrapping_mul(31).wrapping_add(n as u64).wrapping_mul(31).wrapping_add(m as u64)
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
