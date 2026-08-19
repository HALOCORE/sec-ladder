//! p09 rung R4 -- unsafe.
//!
//! R2's algorithm with every bounds check removed: the two header fields, every
//! query word and every bitset word go through `get_unchecked`. **What does NOT
//! go away is the guard** -- `q < nbits`. That is not a bounds check, it is the
//! kernel's semantics; a rung without it would be R1's bug written in Rust
//! rather than an unsafe rung. This rung is correct; it just has nothing
//! checking that it is. R5 (verus.rs) is this exec code with the SAFETY comments
//! below turned into obligations a verifier discharges.
//!
//! SAFETY (1): `off + len <= buf.len()` is the caller's structural
//!   precondition. Unchecked here; discharged at the call site by Verus.
//! SAFETY (2): `len >= 8` guards the header, so `off + 7 < off + len`.
//! SAFETY (3): the query reads are at `qs + 4*k .. qs + 4*k + 4` under `k < nq`
//!   and `qs == off + 8 + 8*nwords` and `8*nwords + 4*nq <= len - 8`, so the
//!   last byte read is at `off + 8 + 8*nwords + 4*nq - 1 <= off + len - 1`.
//! SAFETY (4): the popcount pass reads `ws + 8*i .. +8` under `i < nwords`, and
//!   `8*nwords <= len - 8`. **Linear in the loop counter.**
//! SAFETY (5): the query loop reads `ws + 8*(q >> 6) .. +8` under `q < nbits`,
//!   and `q >> 6 <= (nbits - 1) >> 6 < (nbits + 63) >> 6 == nwords`.
//!
//! **SAFETY (5) is the whole pattern.** The guard is on the *bit* index and the
//! access is on the *word* index, so the fact the access needs is one the guard
//! does not state: it has to come through a **shift**. Every earlier pattern's
//! checked rung is checked against something the guard mentions -- a slice
//! length, an array capacity, an emptiness -- and p09's is not. Z3 discharges it
//! in three ghost lines (`verus.rs`'s `lemma_guard_bounds_word`), with no lemma
//! about the *program* and no `nonlinear_arith`. What LLVM does with the same
//! fact is NOTES.md 4.
//!
//! And SAFETY (4) is the control that makes it a mechanism rather than an
//! anecdote: the popcount pass reads the **same array** with the **same
//! byte-at-a-time assembly** through an index that is linear in its own loop
//! counter. Same buffer, same helper, same fold; the only difference is whether
//! the index came through a shift.
//!
//! `w.count_ones()` is `popcount64(w)` in R5, an `#[inline(always)]` trusted
//! wrapper -- vstd ships no specification for it. NOTES.md 3d prices the
//! intrinsic against C's `__builtin_popcountll` and reports which instruction
//! each rung actually emits, because a rung that lowered to a software popcount
//! while another emitted `popcnt` would be an ISA comparison and not a safety
//! one (`.memory/03-measurement.md`, p11's rule).

#[path = "../../common/driver.rs"]
mod driver;

// ---------------------------------------------------------------- decoders --
#[inline(always)]
fn load_u32(buf: &[u8], p: usize) -> u64 {
    (unsafe { *buf.get_unchecked(p) }) as u64 + 256 * (unsafe { *buf.get_unchecked(p + 1) } as u64)
        + 65536 * (unsafe { *buf.get_unchecked(p + 2) } as u64)
        + 16777216 * (unsafe { *buf.get_unchecked(p + 3) } as u64)
}

#[inline(always)]
fn load_u64(buf: &[u8], p: usize) -> u64 {
    (unsafe { *buf.get_unchecked(p) }) as u64 + 256 * (unsafe { *buf.get_unchecked(p + 1) } as u64)
        + 65536 * (unsafe { *buf.get_unchecked(p + 2) } as u64)
        + 16777216 * (unsafe { *buf.get_unchecked(p + 3) } as u64)
        + 4294967296 * (unsafe { *buf.get_unchecked(p + 4) } as u64)
        + 1099511627776 * (unsafe { *buf.get_unchecked(p + 5) } as u64)
        + 281474976710656 * (unsafe { *buf.get_unchecked(p + 6) } as u64)
        + 72057594037927936 * (unsafe { *buf.get_unchecked(p + 7) } as u64)
}

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    if len < 8 {
        return 0;
    }
    let nbits: u64 = load_u32(buf, off);
    let nq: u64 = load_u32(buf, off + 4);
    if nbits == 0 || nq == 0 {
        return 0;
    }
    let nwords: u64 = (nbits + 63) >> 6;
    if 8 * nwords + 4 * nq > (len - 8) as u64 {
        return 0;
    }
    let ws: usize = off + 8;
    let qs: usize = ws + (8 * nwords) as usize;
    let mut acc: u64 = 0;
    let mut hits: u64 = 0;
    let mut k: u64 = 0;
    while k < nq {
        let q: u64 = load_u32(buf, qs + (4 * k) as usize);
        if q < nbits {
            let w: u64 = load_u64(buf, ws + (8 * (q >> 6)) as usize);
            if w & (1u64 << (q & 63)) != 0 {
                hits = hits.wrapping_add(1);
            }
            acc = acc.wrapping_mul(31).wrapping_add(w);
        }
        k = k + 1;
    }
    acc = acc.wrapping_mul(31).wrapping_add(hits);
    let mut i: u64 = 0;
    while i < nwords {
        let w: u64 = load_u64(buf, ws + (8 * i) as usize);
        acc = acc.wrapping_mul(31).wrapping_add(w.count_ones() as u64);
        i = i + 1;
    }
    acc.wrapping_mul(31).wrapping_add(nbits).wrapping_mul(31).wrapping_add(nq)
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
