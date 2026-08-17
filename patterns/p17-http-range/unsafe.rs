//! p17 rung R4 -- unsafe.
//!
//! R2's algorithm with every bounds check removed: the `nsuf` word, each suffix
//! entry and every served byte are read with `get_unchecked`. The one thing
//! that survives is the range test -- this rung is correct, it just has nothing
//! checking that it is. R5 (verus.rs) is this exec code with the SAFETY
//! comments below turned into obligations a verifier discharges.
//!
//! SAFETY (1): `off + len <= buf.len()` is the caller's structural
//!   precondition. Unchecked here; discharged at the call site by Verus in
//!   verus.rs.
//! SAFETY (2): `len >= 2` guards the `nsuf` word, so `off + 1 < off + len <=
//!   buf.len()`.
//! SAFETY (3): `2 + 2*nsuf <= len` puts the whole suffix table inside the
//!   window, so `off + 3 + 2*i < off + body_start <= off + len` for `i < nsuf`.
//!   The addition cannot overflow: `nsuf <= 65535`, so `2 + 2*nsuf <= 131072`.
//! SAFETY (4): `start >= 0` is what makes `base = off + body_start + start`
//!   a non-negative index at all, and `start < end` bounds it above:
//!   `base + n == off + body_start + end == off + len <= buf.len()`, so every
//!   `base + j` with `j < n` is inside the buffer.
//!
//! **(4) is where p17 differs from every earlier pattern, and it is worth
//! reading twice.** `start >= 0` does two separate jobs and only one of them is
//! memory safety. Drop it and the index is negative only when `s > len`; when
//! `content_len < s <= len` the index is a perfectly valid one and the read is
//! in bounds -- of the *allocation*, and of the *window*, and therefore of
//! anything `get_unchecked`'s `requires` could possibly demand. So a proof that
//! this rung never reads out of bounds does not exclude the leak. Only the
//! functional postcondition `r == range_fold(..)` does. See verus.rs and
//! ../spec.md.

#[path = "../../common/driver.rs"]
mod driver;

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    if len < 2 {
        return 0;
    }
    let nsuf: usize = unsafe { *buf.get_unchecked(off) } as usize
        + 256 * (unsafe { *buf.get_unchecked(off + 1) } as usize);
    if 2 + 2 * nsuf > len {
        return 0;
    }
    let body_start: usize = 2 + 2 * nsuf;
    let content_len: i64 = (len - body_start) as i64;
    let mut acc: u64 = 0;
    let mut nserved: u64 = 0;
    let mut i: usize = 0;
    while i < nsuf {
        let s: i64 = unsafe { *buf.get_unchecked(off + 2 + 2 * i) } as i64
            + 256 * (unsafe { *buf.get_unchecked(off + 3 + 2 * i) } as i64);
        let start: i64 = content_len - s;
        let end: i64 = content_len;
        if start < end && start >= 0 {
            let base: i64 = (off + body_start) as i64 + start;
            let n: i64 = end - start;
            let mut j: i64 = 0;
            while j < n {
                acc = acc.wrapping_mul(31).wrapping_add(
                    unsafe { *buf.get_unchecked((base + j) as usize) } as u64,
                );
                j = j + 1;
            }
            nserved = nserved.wrapping_add(1);
        }
        i = i + 1;
    }
    acc.wrapping_mul(31).wrapping_add(nserved)
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
    if stride_w >= 2 && stride_w <= n_blob as u64 && n_blob as u64 <= 9223372036854775807 {
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
