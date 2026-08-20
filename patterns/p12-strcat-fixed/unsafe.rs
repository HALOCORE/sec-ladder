//! p12 rung R4 -- unsafe.
//!
//! R2's algorithm with every bounds check removed: the four header bytes, every
//! byte the scan looks at, every byte the copy reads and every byte the copy
//! WRITES go through `get_unchecked` / `get_unchecked_mut`. **What does NOT go
//! away is `dlen + slen <= DST_CAP`** -- that is not a bounds check, it is the
//! kernel's semantics, and a rung without it would be R1's bug written in Rust
//! rather than an unsafe rung. This rung is correct; it just has nothing
//! checking that it is. R5 (verus.rs) is this exec code with the SAFETY
//! comments below turned into obligations a verifier discharges.
//!
//! SAFETY (1): `off + len <= buf.len()` is the caller's structural
//!   precondition. Unchecked here; discharged at the call site by Verus in
//!   verus.rs.
//! SAFETY (2): `len >= 4` guards the header, so `off + 3 < off + len <=
//!   buf.len()`.
//! SAFETY (3): the scan reads `off + q` only under `q < len`, so
//!   `off + q < off + len <= buf.len()`.
//! SAFETY (4): the copy reads `off + i` only under `i < q`, and `q <= len` on
//!   exit from the scan loop, so `off + i < off + len <= buf.len()`.
//! SAFETY (5): **the copy WRITES `dst[dlen]` only under
//!   `dlen0 + slen <= DST_CAP`, where `dlen == dlen0 + (i - p)` and `i < q`, so
//!   `dlen < dlen0 + slen <= DST_CAP == dst.len()`.**
//! SAFETY (6): the destination fold reads `dst[i]` only under `i < dlen`, and
//!   `dlen <= DST_CAP` is the loop-carried invariant that (5) also maintains.
//!
//! **(5) is the obligation p12 exists for, and it is a WRITE.** p03 is the only
//! earlier pattern with one -- its `stack_set_unchecked` stores into a
//! `[u64; 64]` local under `sp < STACK_CAP` -- and the two differ in what
//! supplies the bound: p03's guard is in the same basic block as the store and
//! bounds a scalar that moves by one, while p12's guard is one loop level ABOVE
//! the store and bounds a cursor that advances by the whole string. So the fact
//! the prover needs is `dlen0 + (i - p) < DST_CAP` derived from a guard tested
//! before the inner loop began -- which is p03's *pop* shape (the upper bound
//! comes from the loop-carried invariant, not locally) sitting on a *write*.
//! ../NOTES.md 5 has the invariant and 4 has what LLVM does with the same fact.
//!
//! **(6) is the second half and it costs something LLVM cannot avoid**: the
//! destination fold's bound `dlen <= DST_CAP` is not available in its own basic
//! block either. NOTES.md 4 measures both.
//!
//! The `if q >= len { break; }` line before the cursor step is p11's, and for
//! p11's reason: the scan may legitimately stop at `q == len`, so `q + 1` is
//! `len + 1`, and vstd has no axiom that a slice is at most `isize::MAX` bytes.
//! p11 measured that line at 1.00000 Ir per scanned byte; it is in every p12
//! rung, so no rung comparison here moves on it.

#[path = "../../common/driver.rs"]
mod driver;

const DST_CAP: usize = 128;

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
    let mut dlen: usize = 0;
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
        if slen <= DST_CAP && dlen + slen <= DST_CAP {
            let mut i: usize = p;
            while i < q {
                let b: u8 = unsafe { *buf.get_unchecked(off + i) };
                unsafe { *dst.get_unchecked_mut(dlen) = b; }
                dlen = dlen + 1;
                i = i + 1;
            }
        }
        acc = acc.wrapping_mul(31).wrapping_add(slen as u64);
        if q >= len {
            break;
        }
        p = q + 1;
        if p >= len {
            break;
        }
        s = s + 1;
    }
    let mut i: usize = 0;
    while i < dlen {
        acc = acc.wrapping_mul(31).wrapping_add(unsafe { *dst.get_unchecked(i) } as u64);
        i = i + 1;
    }
    acc.wrapping_mul(31).wrapping_add(dlen as u64).wrapping_mul(31)
        .wrapping_add(nstr as u64)
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
