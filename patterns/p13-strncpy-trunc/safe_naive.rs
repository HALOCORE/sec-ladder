//! p13 rung R2 -- safe-naive.
//!
//! The mechanical port a working Rust programmer writes first: index `buf[..]`
//! for the header, for every byte the source scan looks at and for every byte
//! the copy reads, and index `dst[..]` for every byte the copy writes, the
//! zero-fill writes and the CONSUMER reads, with the window-relative index
//! spelled `off + q` / `off + p + i` exactly as the C spells it. Zero `unsafe`.
//!
//! **This rung cannot express the bug, and the way it fails is the interesting
//! part.** The consumer is `while dst[d] != 0 { d = d + 1; }` -- the same
//! unbounded loop C writes -- but in Rust `dst[32]` is a bounds check and a
//! panic, not a read of the caller's frame. So a p13 R2 with the termination
//! store deleted **panics** where R1 silently returns a wrong answer built from
//! stack residue. That control is built in ../NOTES.md 7 and it is the p13
//! analogue of p12's.
//!
//! Consequence for the numbers: `dst[DST_CAP - 1] = 0;` is a *semantic* line in
//! the Rust rungs -- it decides where the consumer stops and therefore what
//! `d` is -- and a *safety* line only in C. All four Rust rungs carry it, so no
//! rung comparison here moves on it, and R1-vs-R1h is the only place its cost
//! is read. `.memory/02-bench-rules.md`.
//!
//! **The copy and the zero-fill are byte loops, not `copy_from_slice`/`fill`**
//! (../spec.md `idiom.required`), for p02's reason: one operator flips
//! `bulk_calls` and 100% of the delta. R3 spells both in bulk, deliberately,
//! and ../NOTES.md 3 reports that as a spelling difference with the routine
//! named.
//!
//! **The zero-fill is not an optimisation target.** It is what `strncpy` does,
//! it is why `dst` is written in full on every iteration, and it is why the
//! per-string cost is O(DST_CAP) rather than O(slen). Deleting it would delete
//! the pattern's largest measured effect (../NOTES.md 3).

#[path = "../../common/driver.rs"]
mod driver;

const DST_CAP: usize = 32;

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
        let n: usize = if slen < DST_CAP { slen } else { DST_CAP };
        let mut i: usize = 0;
        while i < n {
            dst[i] = buf[off + p + i];
            i = i + 1;
        }
        let mut j: usize = n;
        while j < DST_CAP {
            dst[j] = 0;
            j = j + 1;
        }
        dst[DST_CAP - 1] = 0;
        let mut d: usize = 0;
        while dst[d] != 0 {
            d = d + 1;
        }
        acc = acc.wrapping_mul(31).wrapping_add(d as u64);
        acc = acc.wrapping_mul(31).wrapping_add(dst[0] as u64);
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
