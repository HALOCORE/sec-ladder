//! p05 rung R4 -- unsafe.
//!
//! R2's algorithm with every bounds check removed: the four header bytes and
//! every matrix element are read with `get_unchecked`. The one thing that
//! survives is the size test -- this rung is correct, it just has nothing
//! checking that it is. R5 (verus.rs) is this exec code with the SAFETY
//! comments below turned into obligations a verifier discharges.
//!
//! SAFETY (1): `off + len <= buf.len()` is the caller's structural
//!   precondition. Unchecked here; discharged at the call site by Verus in
//!   verus.rs.
//! SAFETY (2): `len >= 4` guards the header, so `off + 3 < off + len <=
//!   buf.len()`.
//! SAFETY (3): `nrow * ncol <= avail == len - 4` is the size check, computed in
//!   `usize` (64-bit here, and Verus proves it lossless for a 32-bit `usize`
//!   too: `nrow, ncol <= 65535`, so the product is at most 4 294 836 225 and
//!   fits either width). For `i < nrow` and `j < ncol`,
//!
//!       i*ncol + j <= (nrow-1)*ncol + (ncol-1) = nrow*ncol - 1 < avail
//!
//!   so `off + 4 + i*ncol + j < off + 4 + avail == off + len <= buf.len()`.
//!   **That middle step is nonlinear**, which is why R5 needs
//!   `by (nonlinear_arith)` and `lemma_mul_inequality` where p16 and p17 needed
//!   neither: their indices were sums, this one is a product.
//!
//! **(3) is where p05 differs from every earlier pattern.** p16's missing check
//! let an unsigned bound underflow; p17's let a signed index go negative. Here
//! the index is *computed by multiplication*, so the check that guards it can
//! itself overflow -- and does, one width down. See c/kernel_hardened.c.
//!
//! `row` is `u32` and `acc` is `u64`; ../spec.md's "Load-bearing" section has
//! the measurement that forced the narrower row accumulator, and NOTES.md 1 has
//! the disassembly. It is the one deviation from TASK_013's pseudocode.

#[path = "../../common/driver.rs"]
mod driver;

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    if len < 4 {
        return 0;
    }
    let nrow: usize = unsafe { *buf.get_unchecked(off) } as usize
        + 256 * (unsafe { *buf.get_unchecked(off + 1) } as usize);
    let ncol: usize = unsafe { *buf.get_unchecked(off + 2) } as usize
        + 256 * (unsafe { *buf.get_unchecked(off + 3) } as usize);
    if nrow == 0 || ncol == 0 {
        return 0;
    }
    let avail: usize = len - 4;
    if nrow * ncol > avail {
        return 0;
    }
    let mut acc: u64 = 0;
    let mut i: usize = 0;
    while i < nrow {
        let mut row: u32 = 0;
        let mut j: usize = 0;
        while j < ncol {
            row = row.wrapping_add(
                unsafe { *buf.get_unchecked(off + 4 + i * ncol + j) } as u32,
            );
            j = j + 1;
        }
        acc = acc.wrapping_mul(31).wrapping_add(row as u64);
        i = i + 1;
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
