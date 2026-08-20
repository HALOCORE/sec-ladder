//! p14 rung R2 -- safe-naive.
//!
//! The mechanical port a working Rust programmer writes first: index `buf[..]`
//! for the window header and for every line header, index `scr[..]` for the
//! scan and the fold, index `tl[..]` for the field table, and spell the
//! window-relative index `off + p` exactly as the C spells it. Zero `unsafe`.
//!
//! **Safe Rust cannot express a `strtok`-shaped tokenizer at all**, and that is
//! the reason every rung here -- C included -- stores `(length)` descriptors
//! rather than pointers. Two spellings were put to `rustc` before the wire
//! format was fixed (../NOTES.md 0): holding `&[u8]` fields into a scratch that
//! is still being NUL-overwritten is `E0506 cannot assign to scr[_] because it
//! is borrowed`, and returning fields that outlive the scratch is `E0515 cannot
//! return value referencing local variable`. **Both are compile-time
//! rejections, so neither has a run-time check to price** -- which is p08's
//! structural result and is precisely why neither is p14's bug. p14's bug
//! survives into safe Rust as a *bounds check*, and a bounds check is a cost.
//!
//! **The copy into the scratch is the same bulk `copy_from_slice` in all four
//! Rust rungs and `memcpy` in both C rungs**, deliberately, so that the
//! measured difference between rungs is the SPLIT and not the load
//! (../spec.md). p02's retraction is the precedent.
//!
//! The cursor guards are subtraction-first (`len - p < 4`) in every rung: `p <=
//! len` is maintained by the guards themselves so the subtraction cannot wrap,
//! while the additive form `p + 4 > len` can overflow `usize` and Verus rejects
//! it. R4 must have a byte-identical R5 twin, so the spelling that verifies is
//! the spelling all seven rungs use.
//!
//! **The field-count bound `if nt == MAXTOK { break; }` is carried by all four
//! Rust rungs.** In Rust it is a SEMANTIC line, not a safety line -- rustc's
//! bounds check on `tl[nt]` is what makes the safe rungs safe, and R4 asserts
//! the same fact -- so no Rust-vs-Rust comparison moves on it. Deleting it from
//! R2 turns R2 into a rung that PANICS where C corrupts its frame; that control
//! is ../NOTES.md 7 and it is the pattern's sharpest row.

#[path = "../../common/driver.rs"]
mod driver;

const SCR: usize = 64;
const MAXTOK: usize = 16;
const DELIM: u8 = b',';

// THE BULK LOAD, and the one place all seven rungs are held to the same
// spelling: `memcpy` in C, this in all four Rust rungs. THE RECEIVER is scoped
// 2-and-2 exactly as p06's is and for the same measured reason: this rung
// writes `dst[..n]`, and unsafe.rs and verus.rs write `a` after
// `split_at_mut(n)` because `RangeTo<usize>` has no `SliceIndexSpecImpl` at the
// pinned vstd. Its price is published in ../NOTES.md 6a.
//
// It is a `#[inline(always)]` free function rather than an inline expression
// because R4 must be byte-identical to R5 and R5's copy is a free function.
#[inline(always)]
fn scr_load(dst: &mut [u8; SCR], src: &[u8], from: usize, n: usize) {
    dst[..n].copy_from_slice(&src[from..from + n]);
}

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md. `#[inline(never)]` only in `isolated` builds, so the
// `whole` builds can inline it the way LTO'd C would.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    if len < 4 {
        return 0;
    }
    let nline: usize = buf[off] as usize + 256 * (buf[off + 1] as usize)
        + 65536 * (buf[off + 2] as usize) + 16777216 * (buf[off + 3] as usize);
    if nline == 0 {
        return 0;
    }
    let mut scr: [u8; SCR] = [0; SCR];
    let mut tl: [usize; MAXTOK] = [0; MAXTOK];
    let mut acc: u64 = 0;
    let mut p: usize = 4;
    let mut ln: usize = 0;
    while ln < nline {
        if len - p < 4 {
            break;
        }
        let llen: usize = buf[off + p] as usize + 256 * (buf[off + p + 1] as usize)
            + 65536 * (buf[off + p + 2] as usize)
            + 16777216 * (buf[off + p + 3] as usize);
        p = p + 4;
        let m: usize = if llen < SCR { llen } else { SCR };
        if len - p < llen {
            break;
        }
        scr_load(&mut scr, buf, off + p, m);
        p = p + llen;
        let mut nt: usize = 0;
        let mut s: usize = 0;
        let mut i: usize = 0;
        while i <= m {
            if i == m || scr[i] == DELIM {
                // THE SAFETY LINE. c/kernel.c omits exactly this.
                if nt == MAXTOK {
                    break;
                }
                let flen: usize = i - s;
                tl[nt] = flen;
                nt = nt + 1;
                s = i + 1;
            }
            i = i + 1;
        }
        let mut cur: usize = 0;
        let mut j: usize = 0;
        while j < nt {
            let tj: usize = tl[j];
            acc = acc.wrapping_mul(31).wrapping_add(tj as u64);
            let mut q: usize = 0;
            while q < tj {
                acc = acc.wrapping_mul(31).wrapping_add(scr[cur + q] as u64);
                q = q + 1;
            }
            cur = cur + tj + 1;
            j = j + 1;
        }
        acc = acc.wrapping_mul(31).wrapping_add(nt as u64);
        ln = ln + 1;
    }
    acc.wrapping_mul(31).wrapping_add(nline as u64)
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
