//! p13 rung R4 -- unsafe.
//!
//! R2's algorithm with every bounds check removed: the four header bytes, every
//! byte the source scan looks at, every byte the copy reads, every byte the
//! copy and the zero-fill WRITE, and **every byte the consumer reads** go
//! through `get_unchecked` / `get_unchecked_mut`. **What does NOT go away is
//! `dst[DST_CAP - 1] = 0`** -- that is not a bounds check, it is the line
//! `strncpy` does not write for you, and a rung without it would be R1's bug
//! written in Rust rather than an unsafe rung. This rung is correct; it just
//! has nothing checking that it is. R5 (verus.rs) is this exec code with the
//! SAFETY comments below turned into obligations a verifier discharges.
//!
//! SAFETY (1): `off + len <= buf.len()` is the caller's structural
//!   precondition. Unchecked here; discharged at the call site by Verus in
//!   verus.rs.
//! SAFETY (2): `len >= 4` guards the header, so `off + 3 < off + len <=
//!   buf.len()`.
//! SAFETY (3): the source scan reads `off + q` only under `q < len`, so
//!   `off + q < off + len <= buf.len()`.
//! SAFETY (4): the copy reads `off + p + i` only under `i < n <= slen = q - p`
//!   and `q <= len`, so `off + p + i < off + q <= off + len <= buf.len()`.
//! SAFETY (5): the copy writes `dst[i]` only under `i < n <= DST_CAP`, and the
//!   zero-fill writes `dst[j]` only under `j < DST_CAP`; `dst.len()` IS
//!   `DST_CAP`. Both are bounded by a compile-time constant in the same basic
//!   block as the store, which is p03's easy shape and NOT this pattern's
//!   obligation.
//! SAFETY (6): **THE OBLIGATION p13 EXISTS FOR, AND IT IS AT A DIFFERENT SITE
//!   FROM THE FACT THAT DISCHARGES IT.** The consumer reads `dst[d]` under **no
//!   bound at all** -- `while *dst.get_unchecked(d) != 0` is exactly C's
//!   unbounded scan. What makes it defined is an invariant established by a
//!   different statement, one line above: `dst[DST_CAP - 1] = 0` puts a zero
//!   byte in the last slot, so the scan stops at or before `DST_CAP - 1` and
//!   `d < DST_CAP` at every read. Delete that store and this rung is
//!   out-of-bounds; bound the loop instead and it is a different (easier)
//!   kernel. p11 proved a scan terminates from a sentinel it was **given**;
//!   p13 has to **establish** the sentinel first, and carry it across the store
//!   into the loop.
//!
//! **(6) is the first two-site obligation in this project.** Every earlier
//! pattern's unchecked access is licensed by a guard on the same value, in the
//! same loop or the one above it (p12's `dlen + slen <= DST_CAP` is a loop
//! level up, which was the previous record). Here the licensing fact is not
//! about the index at all: it is about the *contents* of the array being
//! indexed.
//!
//! The `if q >= len { break; }` line before the cursor step is p11's, and for
//! p11's reason: the source scan may legitimately stop at `q == len`, so
//! `q + 1` is `len + 1`, and vstd has no axiom that a slice is at most
//! `isize::MAX` bytes. It is in every p13 rung, so no rung comparison here
//! moves on it.

#[path = "../../common/driver.rs"]
mod driver;

const DST_CAP: usize = 32;

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    if len < 4 {
        return 0;
    }
    let nstr: usize = unsafe { *buf.get_unchecked(off) } as usize
        + 256 * (unsafe { *buf.get_unchecked(off + 1) } as usize)
        + 65536 * (unsafe { *buf.get_unchecked(off + 2) } as usize)
        + 16777216 * (unsafe { *buf.get_unchecked(off + 3) } as usize);
    if nstr == 0 {
        return 0;
    }
    let mut dst: [u8; DST_CAP] = [0; DST_CAP];
    let mut acc: u64 = 0;
    let mut p: usize = 4;
    let mut s: usize = 0;
    while s < nstr {
        let mut q: usize = p;
        while q < len {
            if unsafe { *buf.get_unchecked(off + q) } == 0 {
                break;
            }
            q = q + 1;
        }
        let slen: usize = q - p;
        let n: usize = if slen < DST_CAP { slen } else { DST_CAP };
        let mut i: usize = 0;
        while i < n {
            let b: u8 = unsafe { *buf.get_unchecked(off + p + i) };
            unsafe { *dst.get_unchecked_mut(i) = b; }
            i = i + 1;
        }
        let mut j: usize = n;
        while j < DST_CAP {
            unsafe { *dst.get_unchecked_mut(j) = 0; }
            j = j + 1;
        }
        unsafe { *dst.get_unchecked_mut(DST_CAP - 1) = 0; }
        let mut d: usize = 0;
        while unsafe { *dst.get_unchecked(d) } != 0 {
            d = d + 1;
        }
        acc = acc.wrapping_mul(31).wrapping_add(d as u64);
        acc = acc.wrapping_mul(31).wrapping_add(unsafe { *dst.get_unchecked(0) } as u64);
        if q >= len {
            break;
        }
        p = q + 1;
        if p >= len {
            break;
        }
        s = s + 1;
    }
    acc.wrapping_mul(31).wrapping_add(nstr as u64)
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
