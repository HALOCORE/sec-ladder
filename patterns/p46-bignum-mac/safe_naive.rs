//! p46 rung R2 -- safe Rust, naive. The obvious port of `c/kernel_hardened.c`:
//! index the scratch arrays, let the language check the index.
//!
//! **What the language's checks ARE here, and why there are THREE of them.**
//! The MAC step reads `bl[j]`, reads `out[i + j]` and writes `out[i + j]`, so
//! one schoolbook step carries three bounds checks -- the densest check site in
//! this tree. Measured against R4 they cost `7.00` instructions per MAC step
//! (../NOTES.md 8), i.e. the check apparatus is two thirds again as large as
//! the ten-instruction MAC it guards.
//!
//! ⚠ The checks are NOT hoistable, and that is not an accident of spelling.
//! `i + j < OUTCAP` follows from `i < n`, `j < m` and `n + m <= OUTCAP` by
//! purely LINEAR reasoning -- there is no `lemma_mul_inequality` in it, which
//! is exactly what makes p46 not p05 -- and LLVM still does not do it. The
//! measurement that establishes there IS a rung boundary here is in
//! ../NOTES.md 0b, and it was run before any cell was written precisely because
//! a fixed-capacity `[u64; 96]` gives LLVM a compile-time length and the checks
//! might have vanished. They do not: this rung's kernel body is 186
//! instructions against the unsafe rung's 111.
//!
//! This rung keeps the output-side bound as well, so that all six rungs compute
//! the same function on every input including the adversarial ones. That is a
//! deliberate choice with a cost: it means R2's per-access checks are *provably
//! redundant* on every call the benchmark makes, and LLVM still cannot remove
//! them. ../verus.rs proves the fact that would let it; rustc never learns it.
//! See `.memory/01-ladder.md` finding 2.

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

/// Little-endian limb decode. Checked, like every other read in this rung.
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
    let mut i: usize = 0;
    while i < n {
        let ai: u64 = ld64(w, 8 + 8 * i);
        let mut carry: u64 = 0;
        let mut j: usize = 0;
        while j < m {
            let bj: u64 = bl[j];
            let t: u128 =
                (ai as u128) * (bj as u128) + (out[i + j] as u128) + (carry as u128);
            out[i + j] = t as u64;
            carry = (t >> 64) as u64;
            j = j + 1;
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
