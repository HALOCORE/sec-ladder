//! p11 rung R2 -- safe-naive.
//!
//! The mechanical port a working Rust programmer writes first: index `buf[..]`
//! for the header, for every byte the scan looks at and for every byte the fold
//! reads, with the window-relative index spelled `off + q` / `off + i` exactly
//! as the C spells it. Zero `unsafe`.
//!
//! **The scan is where safe Rust has no choice.** C says `strlen(p)`, which is
//! bounded by the sentinel and by nothing else. This rung cannot: an index
//! expression `buf[off + q]` carries a bounds check, so writing the C loop out
//! in safe Rust *already* bounds it -- by the slice. The `q < len` test is here
//! anyway, because bounding by the slice would let one window's scan run into
//! the next window (the driver hands the kernel the whole blob -- p17's finding,
//! `.memory/01-ladder.md`: "the language's bound is the slice it was given").
//! So this rung carries **two** bounds per byte where R4 carries one, and
//! NOTES.md 3 measures what the second one costs.
//!
//! **The scan and the fold are two separate loops**, here and in every rung
//! (../spec.md `idiom.required`). NOTES.md 1 shows on the disassembly that -O3
//! keeps them separate in all six rungs; it is checked, not assumed.

#[path = "../../common/driver.rs"]
mod driver;

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
        let mut h: u64 = 0;
        let mut i: usize = p;
        while i < q {
            h = h.wrapping_mul(31).wrapping_add(buf[off + i] as u64);
            i = i + 1;
        }
        acc = acc.wrapping_mul(31).wrapping_add(h ^ (slen as u64));
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
