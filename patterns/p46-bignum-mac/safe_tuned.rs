//! p46 rung R3 -- safe Rust, tuned. **This is the rung the pattern is for, and
//! it is the rung that beats the unsafe one.**
//!
//! One lever, zero `unsafe`, zero trusted items: walk the output row and the b
//! operand as ITERATORS instead of indexing them.
//!
//!     for (o, &bj) in out[i..i + m].iter_mut().zip(bl[..m].iter()) { ... }   // R3
//!     while j < m { ... bl[j] ... out[i + j] ... }                           // R2
//!
//! The reslice `out[i..i + m]` is one bounds check per ROW -- `O(n)` -- and the
//! `zip` then walks two cursors with no per-step test at all, where R2 pays
//! three per MAC step, `O(n*m)`. **That asymptotic change is the whole lever.**
//!
//! ⚠⚠ **AND IT MAKES SAFE RUST CHEAPER THAN THE UNSAFE RUNG. READ THE NEXT
//! PARAGRAPH BEFORE QUOTING THAT.**
//!
//! ⚠⚠ **NONE OF IT IS SAFETY, AND THE R4 SIDE WAS SEARCHED FIRST**
//! (`.memory/01-ladder.md`; the p10/p27/p38/p22 trap). Three R3 spellings and
//! three R4 spellings were measured on a 2x2 `(n, m)` grid before either rung
//! was written (../NOTES.md 0b). The **cheapest unsafe spelling found**, a
//! checked per-row reslice with unchecked indexing inside it, is
//! `1.5` Ir/MAC **cheaper than this rung** -- and it is **not an admissible
//! R4**, because it takes a MUTABLE sub-slice and the pinned vstd has no
//! specification for one: `slice_subrange` exists for `&[T]` only, and
//! `ExSliceIndex::index_mut` carries a `requires` and no `ensures` at all, so a
//! write through it cannot be related back to the array and R5 cannot discharge
//! its postcondition. **Measured, not read off the source** (../NOTES.md 0c).
//!
//! So p46's "safe beats unsafe" is `.memory/01-ladder.md` finding 14's
//! mechanism with a number on it -- *the safe class can reach spellings the
//! unsafe class cannot, because the unsafe class is chained to the prover* --
//! and it is the second measured instance after p16's, the first on a WRITE,
//! and the first where the gap is priced rather than argued.

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

/// Little-endian limb decode. Byte-for-byte R2's, so that the ONLY difference
/// between the two safe rungs is the MAC loop's addressing.
#[inline(always)]
fn ld64(w: &[u8], p: usize) -> u64 {
    w[p] as u64 + 256 * (w[p + 1] as u64) + 65536 * (w[p + 2] as u64)
        + 16777216 * (w[p + 3] as u64) + 4294967296 * (w[p + 4] as u64)
        + 1099511627776 * (w[p + 5] as u64) + 281474976710656 * (w[p + 6] as u64)
        + 72057594037927936 * (w[p + 7] as u64)
}

/// p46's kernel. Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    if len < 8 {
        return 0;
    }
    let w: &[u8] = &buf[off..off + len];
    let n: usize = w[0] as usize;
    let m: usize = w[1] as usize;
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
        bl[jd] = ld64(w, 8 + 8 * (n + jd));
        jd = jd + 1;
    }
    let mut out: [u64; OUTCAP] = [0u64; OUTCAP];
    let bs: &[u64] = &bl[0..m];
    let mut i: usize = 0;
    while i < n {
        let ai: u64 = ld64(w, 8 + 8 * i);
        let mut carry: u64 = 0;
        for (o, &bj) in out[i..i + m].iter_mut().zip(bs.iter()) {
            let t: u128 = (ai as u128) * (bj as u128) + (*o as u128) + (carry as u128);
            *o = t as u64;
            carry = (t >> 64) as u64;
        }
        out[i + m] = carry;
        i = i + 1;
    }
    let mut acc: u64 = 0;
    let mut k: usize = 0;
    while k < n + m {
        acc = acc.wrapping_mul(31).wrapping_add(out[k]);
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
