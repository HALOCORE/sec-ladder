//! p12 rung R2 -- safe-naive.
//!
//! The mechanical port a working Rust programmer writes first: index `buf[..]`
//! for the header, for every byte the scan looks at and for every byte the copy
//! reads, and index `dst[..]` for every byte the copy writes, with the
//! window-relative index spelled `off + q` / `off + i` exactly as the C spells
//! it. Zero `unsafe`.
//!
//! **This is the first pattern where the safe rung cannot express the bug at
//! all**, and it is p08's shape on length rather than on aliasing. `dst` is a
//! `[u8; DST_CAP]`; `dst[dlen] = b` with `dlen >= DST_CAP` panics, and there is
//! no safe spelling that writes past it. So the capacity check in this rung is
//! not what makes it safe -- rustc's bounds check is -- and deleting the check
//! turns R2 into a rung that PANICS where R1 corrupts. That control is built in
//! ../NOTES.md 7 and it is the p12 analogue of p02's.
//!
//! The consequence for the numbers: `dlen + slen <= DST_CAP` is a *semantic*
//! line in the Rust rungs (it decides which strings are copied) and a *safety*
//! line only in C. Both rungs need it to produce the same checksum, so it is in
//! `idiom.required` for all seven cells and no rung comparison moves on it.
//! What R2-vs-R4 measures is the bounds check on top of it, at matched
//! spelling: the same three loops, the same indices, `buf[i]`/`dst[i]` against
//! `get_unchecked`/`get_unchecked_mut`.
//!
//! **The copy is a byte loop, not `copy_from_slice`** (../spec.md
//! `idiom.required`), for p02's reason: one operator flips `bulk_calls` and
//! 100% of the delta. R3 spells it in bulk, deliberately, and ../NOTES.md 3
//! reports that as a spelling difference with the routine named.
//!
//! **The scan is bounded by the window in this rung and in every other**, R1
//! included -- p12's bug is the write. NOTES.md 1 shows on the disassembly that
//! -O3 keeps the scan, the copy and the destination fold as three separate
//! loops in every rung; it is checked, not assumed.

#[path = "../../common/driver.rs"]
mod driver;

const DST_CAP: usize = 128;

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md. `#[inline(never)]` only in `isolated` builds, so the
// `whole` builds can inline it the way LTO'd C would.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    if len < 4 {
        return 0;
    }
    let nstr: usize = buf[off] as usize + 256 * (buf[off + 1] as usize)
        + 65536 * (buf[off + 2] as usize) + 16777216 * (buf[off + 3] as usize);
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
            if buf[off + q] == 0 {
                break;
            }
            q = q + 1;
        }
        let slen: usize = q - p;
        if slen <= DST_CAP && dlen + slen <= DST_CAP {
            let mut i: usize = p;
            while i < q {
                let b: u8 = buf[off + i];
                dst[dlen] = b;
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
        acc = acc.wrapping_mul(31).wrapping_add(dst[i] as u64);
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
