//! p16 rung R4 -- unsafe.
//!
//! R2's algorithm with every bounds check removed: the tag, the two length
//! bytes and every value byte are read with `get_unchecked`. The one thing that
//! survives is the *fit test* -- this rung is correct, it just has nothing
//! checking that it is. R5 (verus.rs) is this exec code with the SAFETY
//! comments below turned into obligations a verifier discharges.
//!
//! Note what the two tests have to be sufficient *for*, because on this pattern
//! it is a chain rather than a single load:
//!
//! SAFETY (1): `off + len <= buf.len()` is the caller's structural
//!   precondition, so `end <= buf.len()`. Unchecked here; discharged at the
//!   call site by Verus in verus.rs.
//! SAFETY (2): `end - p >= 3` keeps `p + 2 < end <= buf.len()`, so the three
//!   header reads are in bounds. The subtraction cannot underflow because
//!   `p <= end` -- see (4).
//! SAFETY (3): `vlen > end - (p + 3)` rejects exactly the values for which the
//!   value fold would read past `end`, so `p + 3 + j < end <= buf.len()` for
//!   every `j < vlen`.
//! SAFETY (4): and (3) is *also* what keeps `p <= end` after `p += 3 + vlen`,
//!   which is what makes (2)'s subtraction sound on the next iteration. Delete
//!   the one `if` and this file is c/kernel.c: the read runs off the end AND
//!   `end - p` underflows, so the walk never terminates at the buffer end.
//!   The two obligations are not independent; that is the interesting thing
//!   about a chained parser and the reason the R5 loop invariant carries
//!   `p <= end` explicitly.

#[path = "../../common/driver.rs"]
mod driver;

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    let mut p: usize = off;
    let end: usize = off + len;
    let mut acc: u64 = 0;
    let mut nrec: u64 = 0;
    while end - p >= 3 {
        acc = acc.wrapping_mul(31).wrapping_add(unsafe { *buf.get_unchecked(p) } as u64);
        let vlen: usize = unsafe { *buf.get_unchecked(p + 1) } as usize
            + 256 * (unsafe { *buf.get_unchecked(p + 2) } as usize);
        if vlen > end - (p + 3) {
            break;
        }
        let mut j: usize = 0;
        while j < vlen {
            acc = acc
                .wrapping_mul(31)
                .wrapping_add(unsafe { *buf.get_unchecked(p + 3 + j) } as u64);
            j = j + 1;
        }
        p = p + 3 + vlen;
        nrec = nrec.wrapping_add(1);
    }
    acc.wrapping_mul(31).wrapping_add(nrec)
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
    if stride_w >= 3 && stride_w <= n_blob as u64 {
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
