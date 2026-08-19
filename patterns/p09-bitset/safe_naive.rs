//! p09 rung R2 -- safe-naive.
//!
//! The mechanical port a working Rust programmer writes first: index `buf[..]`
//! for every one of the header, query and bitset-word bytes, with the absolute
//! index spelled exactly as the C spells it. Zero `unsafe`.
//!
//! **THREE different bounds checks live in this rung and they do not behave the
//! same, which is p09's result.** All three are against `buf.len()`:
//!
//! * the **header** reads, `off .. off+8`, once per call;
//! * the **popcount pass**, `ws + 8*i .. +8` under `i < nwords` -- an index
//!   that is linear in its own loop counter;
//! * the **query** read, `ws + 8*(q >> 6) .. +8` under `q < nbits` -- an index
//!   the optimiser can only bound by taking the guard **through a shift**.
//!
//! The second and third are the same array, the same helper and the same fold.
//! NOTES.md 4 measures both, and the difference between them is the number this
//! pattern publishes.
//!
//! R3 (safe_tuned.rs) reslices the window once, which is what hands the
//! optimiser the length it otherwise has to re-derive per access. That removes
//! 100% of one of these terms and 0% of another; which is which is the finding.

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
// Contract: ../spec.md. `#[inline(never)]` only in `isolated` builds, so the
// `whole` builds can inline it the way LTO'd C would.
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
