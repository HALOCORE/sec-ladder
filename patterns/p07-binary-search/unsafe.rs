//! p07 rung R4 -- unsafe.
//!
//! R2's algorithm with every bounds check removed: the eight header bytes, the
//! four bytes of each query key and the four bytes of each probed element are
//! read with `get_unchecked`. The one thing that survives is the length test --
//! this rung is correct, it just has nothing checking that it is. R5 (verus.rs)
//! is this exec code with the SAFETY comments below turned into obligations a
//! verifier discharges.
//!
//! SAFETY (1): `off + len <= buf.len()` is the caller's structural
//!   precondition. Unchecked here; discharged at the call site by Verus in
//!   verus.rs.
//! SAFETY (2): `len >= 8` guards the header, so `off + 7 < off + len <=
//!   buf.len()`.
//! SAFETY (3): `4*n + 4*nq <= avail == len - 8` is the length check, computed
//!   in `u64` because `n` and `nq` are u32 fields and `4*n + 4*nq` reaches
//!   34 359 738 360, which does not fit 32 bits. For `q < nq`,
//!
//!       4*n + 4*q + 4 <= 4*n + 4*nq <= avail
//!
//!   so `off + 8 + 4*n + 4*q + 3 < off + 8 + avail == off + len <= buf.len()`,
//!   and for `mid < hi <= n`,
//!
//!       4*mid + 4 <= 4*n <= avail
//!
//!   so the probe is inside the window too.
//!
//! **(3) is where p07 differs from p05, and the difference is that there is no
//! nonlinearity at all.** p05's index is `i*ncol + j`, a product of two
//! *variables*, so its proof needs `lemma_mul_inequality` and two
//! `by (nonlinear_arith)` blocks. Every multiplication here is by the literal
//! 4, so every step above is linear and Z3 takes all of them for free. What
//! p07 pays instead is the `break` and the loop-bound relation
//! `bsearch(lo, hi) == bsearch(0, n)`, which is p16's `invariant_except_break`
//! shape. NOTES.md 5 has the tally.
//!
//! **Why the bounds are half-open.** `hi = n`, `while lo < hi`, `hi = mid`. The
//! textbook inclusive form (`hi = n - 1`, `while lo <= hi`, `hi = mid - 1`)
//! underflows `usize` at `mid == 0`, which any key below `elements[0]` reaches
//! -- on *well-formed* input, not adversarially. In this rung that underflow
//! would be a `get_unchecked` at index 2^63; in R2/R3 it is a panic. NOTES.md 6
//! derives the variant and measures it.

#[path = "../../common/driver.rs"]
mod driver;

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    if len < 8 {
        return 0;
    }
    let n: usize = unsafe { *buf.get_unchecked(off) } as usize
        + 256 * (unsafe { *buf.get_unchecked(off + 1) } as usize)
        + 65536 * (unsafe { *buf.get_unchecked(off + 2) } as usize)
        + 16777216 * (unsafe { *buf.get_unchecked(off + 3) } as usize);
    let nq: usize = unsafe { *buf.get_unchecked(off + 4) } as usize
        + 256 * (unsafe { *buf.get_unchecked(off + 5) } as usize)
        + 65536 * (unsafe { *buf.get_unchecked(off + 6) } as usize)
        + 16777216 * (unsafe { *buf.get_unchecked(off + 7) } as usize);
    if n == 0 || nq == 0 {
        return 0;
    }
    let avail: usize = len - 8;
    if 4 * (n as u64) + 4 * (nq as u64) > avail as u64 {
        return 0;
    }
    let mut acc: u64 = 0;
    let mut q: usize = 0;
    while q < nq {
        let kp: usize = off + 8 + 4 * n + 4 * q;
        let key: u32 = unsafe { *buf.get_unchecked(kp) } as u32
            + 256 * (unsafe { *buf.get_unchecked(kp + 1) } as u32)
            + 65536 * (unsafe { *buf.get_unchecked(kp + 2) } as u32)
            + 16777216 * (unsafe { *buf.get_unchecked(kp + 3) } as u32);
        let mut lo: usize = 0;
        let mut hi: usize = n;
        let mut found: u64 = 0xffff_ffff_ffff_ffff;
        while lo < hi {
            let mid: usize = lo + (hi - lo) / 2;
            let ep: usize = off + 8 + 4 * mid;
            let v: u32 = unsafe { *buf.get_unchecked(ep) } as u32
                + 256 * (unsafe { *buf.get_unchecked(ep + 1) } as u32)
                + 65536 * (unsafe { *buf.get_unchecked(ep + 2) } as u32)
                + 16777216 * (unsafe { *buf.get_unchecked(ep + 3) } as u32);
            if v == key {
                found = mid as u64;
                break;
            }
            if v < key {
                lo = mid + 1;
            } else {
                hi = mid;
            }
        }
        acc = acc.wrapping_mul(31).wrapping_add(found.wrapping_add(1));
        q = q + 1;
    }
    acc.wrapping_mul(31).wrapping_add((n as u64).wrapping_mul(nq as u64))
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
