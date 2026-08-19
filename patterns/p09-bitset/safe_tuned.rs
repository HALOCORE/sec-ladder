//! p09 rung R3 -- safe-tuned.
//!
//! Same semantics as R2, written the way an experienced Rust programmer writes
//! a windowed reader: **reslice the window once**, then index the reslice. The
//! reslice is the bounds check; it happens once per call rather than once per
//! byte, and it is outside both loops by construction rather than by the
//! optimiser's goodwill. Still zero `unsafe`.
//!
//! **The reslice hands LLVM `win.len() == len`, which is exactly the length the
//! per-access checks were re-deriving.** What it does NOT hand LLVM is
//! `q >> 6 < nwords`: that fact has to come from the guard `q < nbits` through a
//! shift, and the reslice says nothing about it. So this rung is the one that
//! isolates p09's question -- NOTES.md 4 measures which of its checks survive
//! the reslice and which do not, and the popcount pass (same array, same
//! helper, index linear in the loop counter) is the negative control beside it.
//!
//! **There are two in-contract R3 spellings and NOTES.md 10a measures both**
//! (`.memory/01-ladder.md` finding 3 requires at least two, with the cheaper
//! quoted, and the cheapest-found figure must name its input). The other walks
//! the query array with `chunks_exact(4)` over `win[qs0 .. qs0 + 4*nq]`.
//!
//! **What is NOT here, and why**: reinterpreting the word region as a `&[u64]`
//! (`align_to`, `from_raw_parts`, `bytemuck`) would delete the byte-addressed
//! index that carries the shift, and it is `idiom.forbidden`. It is also not
//! available to an R4 at the pinned vstd, so a rung using it would compare a
//! safe cell against an unsafe cell that cannot exist.

#[path = "../../common/driver.rs"]
mod driver;

// ---------------------------------------------------------------- decoders --
#[inline(always)]
fn load_u32(buf: &[u8], p: usize) -> u64 {
    buf[p] as u64 + 256 * (buf[p + 1] as u64) + 65536 * (buf[p + 2] as u64)
        + 16777216 * (buf[p + 3] as u64)
}

#[inline(always)]
fn load_u64(buf: &[u8], p: usize) -> u64 {
    buf[p] as u64 + 256 * (buf[p + 1] as u64) + 65536 * (buf[p + 2] as u64)
        + 16777216 * (buf[p + 3] as u64) + 4294967296 * (buf[p + 4] as u64)
        + 1099511627776 * (buf[p + 5] as u64) + 281474976710656 * (buf[p + 6] as u64)
        + 72057594037927936 * (buf[p + 7] as u64)
}

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    if len < 8 {
        return 0;
    }
    let win: &[u8] = &buf[off..off + len];
    let nbits: u64 = load_u32(win, 0);
    let nq: u64 = load_u32(win, 4);
    if nbits == 0 || nq == 0 {
        return 0;
    }
    let nwords: u64 = (nbits + 63) >> 6;
    if 8 * nwords + 4 * nq > (len - 8) as u64 {
        return 0;
    }
    let ws: usize = 8;
    let qs: usize = ws + (8 * nwords) as usize;
    let mut acc: u64 = 0;
    let mut hits: u64 = 0;
    let mut k: u64 = 0;
    while k < nq {
        let q: u64 = load_u32(win, qs + (4 * k) as usize);
        if q < nbits {
            let w: u64 = load_u64(win, ws + (8 * (q >> 6)) as usize);
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
        let w: u64 = load_u64(win, ws + (8 * i) as usize);
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
