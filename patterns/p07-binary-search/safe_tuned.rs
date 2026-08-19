//! p07 rung R3 -- safe-tuned.
//!
//! Same semantics as R2, written the way an experienced Rust programmer writes
//! a byte-level decoder: reslice the four bytes of each little-endian u32 once
//! and index the 4-byte slice, so a probe carries **one** bounds check instead
//! of four. The reslice *is* the check, it happens once per probe, and it is
//! outside the decode by construction rather than by the optimiser's goodwill.
//! Still zero `unsafe`.
//!
//! `u32::from_le_bytes(buf[ep..ep + 4].try_into().unwrap())` would be the more
//! idiomatic spelling still, and it is deliberately *not* used -- it is in
//! ../spec.md's `forbidden` list. Two reasons, and the second is the one that
//! decides it: it would delete the written-out little-endian decode that every
//! rung shares, and it **cannot be an R4/R5 spelling at the pinned vstd**
//! (`TryFromSliceError` and `from_le_bytes` are both `is not supported`), so a
//! rung that used it would be comparing a safe cell against an unsafe cell that
//! cannot exist. `.memory/01-ladder.md`: a rung covered by an `identity` pin is
//! chained to the prover. NOTES.md 10a measures it as an out-of-contract
//! control anyway, and says so.
//!
//! **This rung doubles as the decomposition control** `.memory/01-ladder.md`
//! finding 4 asks for. R2 and R3 differ in the *decode* and in nothing else --
//! same header handling, same length check, same half-open bounds, same
//! midpoint spelling, same three-way compare, same fold -- so R2 - R3 is the
//! cost of the per-byte check on the probe path, measured rather than
//! attributed. NOTES.md 3.
//!
//! `.memory/01-ladder.md`: never publish a safety-cost claim without this rung,
//! and never without at least two in-contract spellings of it. NOTES.md 10a has
//! the second one (`r3_split`, `split_at` instead of a range reslice).

#[path = "../../common/driver.rs"]
mod driver;

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    if len < 8 {
        return 0;
    }
    let hdr: &[u8] = &buf[off..off + 8];
    let n: usize = hdr[0] as usize + 256 * (hdr[1] as usize)
        + 65536 * (hdr[2] as usize) + 16777216 * (hdr[3] as usize);
    let nq: usize = hdr[4] as usize + 256 * (hdr[5] as usize)
        + 65536 * (hdr[6] as usize) + 16777216 * (hdr[7] as usize);
    if n == 0 || nq == 0 {
        return 0;
    }
    let avail: usize = len - 8;
    if 4 * (n as u64) + 4 * (nq as u64) > avail as u64 {
        return 0;
    }
    let mut acc: u64 = 0;
    for q in 0..nq {
        let kp: usize = off + 8 + 4 * n + 4 * q;
        let kw: &[u8] = &buf[kp..kp + 4];
        let key: u32 = kw[0] as u32 + 256 * (kw[1] as u32)
            + 65536 * (kw[2] as u32) + 16777216 * (kw[3] as u32);
        let mut lo: usize = 0;
        let mut hi: usize = n;
        let mut found: u64 = 0xffff_ffff_ffff_ffff;
        while lo < hi {
            let mid: usize = lo + (hi - lo) / 2;
            let ep: usize = off + 8 + 4 * mid;
            let ew: &[u8] = &buf[ep..ep + 4];
            let v: u32 = ew[0] as u32 + 256 * (ew[1] as u32)
                + 65536 * (ew[2] as u32) + 16777216 * (ew[3] as u32);
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
