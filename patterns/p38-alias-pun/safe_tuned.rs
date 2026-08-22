//! p38 rung R3 -- safe Rust, tuned. Still immune, and immune for the same
//! reason R2 is: **Rust has no type-based aliasing rule**, so there is nothing
//! the tuning could have given away.
//!
//! What the tuning changes is the ordinary safety column, and only that:
//!
//!   * the decode loop reslices the window **once** (`&buf[off + 4..]`) and
//!     indexes the reslice, instead of computing `off + 4 + 2*j` against the
//!     whole blob on every byte;
//!   * the payload fold reslices the scratch **once per record** and walks the
//!     reslice, so the per-word bound is `seg.len()` rather than `SCRATCH_W`.
//!
//! Both are the levers `.memory/01-ladder.md` names for an R3, they cost zero
//! `unsafe` and zero trusted items, and they leave the algorithm identical.
//! **The clamp and the read-back are character-identical to R2's**, which is
//! deliberate: it is the pair that shows p38's immunity is not a property of
//! one spelling.

#[path = "../../common/driver.rs"]
mod driver;

/// The decode scratch, in words. Must equal `SLB_P38_SCRATCH_W` in c/kernel.h
/// and `SCRATCH_W` in model.py.
const SCRATCH_W: usize = 256;

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    if len < 4 {
        return 0;
    }
    let nrec: usize = buf[off] as usize + 256 * (buf[off + 1] as usize)
        + 65536 * (buf[off + 2] as usize) + 16777216 * (buf[off + 3] as usize);
    if nrec == 0 {
        return 0;
    }
    let mut sc: [u16; SCRATCH_W] = [0; SCRATCH_W];
    let mut nw: usize = (len - 4) / 2;
    if nw > SCRATCH_W {
        nw = SCRATCH_W;
    }
    let src: &[u8] = &buf[off + 4..off + 4 + 2 * nw];
    let mut j: usize = 0;
    while j < nw {
        sc[j] = src[2 * j] as u16 + 256 * (src[2 * j + 1] as u16);
        j = j + 1;
    }
    let mut acc: u64 = 0;
    let mut i: usize = 0;
    let mut o: usize = 0;
    while o < nrec && i + 2 <= nw {
        let room: usize = (nw - i - 2) / 2;
        // THE CLAMP, character-identical to R2's.
        if sc[i] as usize + 65536 * (sc[i + 1] as usize) > room {
            sc[i] = (room % 65536) as u16;
            sc[i + 1] = (room / 65536) as u16;
        }
        let n: usize = sc[i] as usize + 65536 * (sc[i + 1] as usize);
        let seg: &[u16] = &sc[i + 2..i + 2 + 2 * n];
        let mut k: usize = 0;
        while k < seg.len() {
            acc = acc.wrapping_mul(31).wrapping_add(seg[k] as u64);
            k = k + 1;
        }
        i = i + 2 + 2 * n;
        o = o + 1;
    }
    acc.wrapping_mul(31).wrapping_add(o as u64)
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
