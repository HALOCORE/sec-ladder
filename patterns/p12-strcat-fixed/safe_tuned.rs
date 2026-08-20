//! p12 rung R3 -- safe-tuned.
//!
//! Same semantics as R2, written the way an experienced Rust programmer writes
//! a bounded concatenation: reslice the window once so every later index is
//! against a slice of known length, do the copy with `copy_from_slice` (one
//! bounds check per string instead of one per byte, and it lowers to `memcpy`),
//! and fold the destination with an iterator over `&dst[..dlen]`. Still zero
//! `unsafe`.
//!
//! **What is deliberately NOT varied here: the scan.** p11 exists to compare
//! `strlen` / `memchr` / `CStr::from_bytes_until_nul` / `iter().position()`, and
//! it measured a 12x library term and a 5.3x spelling term on exactly that
//! loop. If R3 reached for `from_bytes_until_nul` here, p12's headline would be
//! p11's finding wearing p12's label. So the scan is the same indexed byte loop
//! in R2, R3, R4 and R5 -- over the reslice rather than over `buf` -- and the
//! COPY is what moves. `.memory/03-measurement.md`: name the routine beside
//! every rate, and difference rates only within a routine.
//!
//! **So R3 - R4 here is a SPELLING difference and must not be quoted as a
//! safety tax.** The matched-spelling safety number on this pattern is
//! `R2 - R4`: byte-loop copy against byte-loop copy, indexed against unchecked,
//! nothing else different. ../NOTES.md 3 gives both and says which is which.
//!
//! **The two checks that survive here are NOT the destination's** -- measured
//! by decoding their panic `Location`s (`controls/pads.py`), after ../NOTES.md
//! 4 first read the pad COUNT the other way and this comment repeated it:
//!
//!   * `&buf[off..off + len]` (50:24) survives -- its bound is the CALLER's
//!     precondition and is unprovable inside `kernel`;
//!   * `&w[p..q]` (71:54) survives -- its bound `q <= len` is a RUNTIME value;
//!   * both destination accesses are elided, `dst[dlen..dlen + slen]` and
//!     `&dst[..dlen]` alike, because `dlen <= DST_CAP` is bounded by a
//!     CONSTANT that the guarded increments show LLVM.
//!
//! So the discriminator is literal-vs-runtime bound, not p03's same-block vs
//! loop-carried one, and p03's result does not transplant. ../NOTES.md 4.

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
    let w: &[u8] = &buf[off..off + len];
    let nstr: usize = w[0] as usize + 256 * (w[1] as usize)
        + 65536 * (w[2] as usize) + 16777216 * (w[3] as usize);
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
            if w[q] == 0 {
                break;
            }
            q = q + 1;
        }
        let slen: usize = q - p;
        if slen <= DST_CAP && dlen + slen <= DST_CAP {
            dst[dlen..dlen + slen].copy_from_slice(&w[p..q]);
            dlen = dlen + slen;
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
    acc = dst[..dlen]
        .iter()
        .fold(acc, |h, &b| h.wrapping_mul(31).wrapping_add(b as u64));
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
