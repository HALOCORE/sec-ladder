//! p18 rung R2 -- safe-naive.
//!
//! The mechanical port a working Rust programmer writes first: index `buf[..]`
//! for the window header and for every varint byte, and spell the
//! window-relative index `off + p` exactly as the C spells it. Zero `unsafe`.
//!
//! **The safety line is `if shift < VBITS`, and in Rust it is not a safety line
//! at all in the configuration this benchmark measures.** Deleting it from this
//! rung does not produce a panic and does not produce a bounds-check failure:
//! at `-C debug-assertions=off`, which is what every one of the 24 measured
//! cells uses, `<<` with an oversized count MASKS the count and this rung
//! returns the same silently wrong integer C returns. Measured, bit for bit,
//! against all four C builds -- ../NOTES.md 7.
//!
//! What does catch it is `-C debug-assertions=on` (the `O0d` axis, which no
//! pattern in this project had ever measured), Miri, and Verus. All three are
//! outside the 24-cell matrix. That is p18's whole point and ../NOTES.md 0.2
//! states it with the measurement.
//!
//! **`shift` is `u32` and the increment is `wrapping_add(7)` in all seven
//! rungs**, matching C's `unsigned` which wraps by 6.2.5p9. It is not
//! defensive: it is what makes the `O0d` measurement attributable, because it
//! leaves the SHIFT and the two cursor increments as the only arithmetic in the
//! kernel a debug-assertions build can fire on. ../NOTES.md 5.
//!
//! **The scan is bounded by `p < len` in every rung, R1 included**, so every
//! read of `buf` is in bounds in every rung. p18 is not p11 and not p16: its
//! bug is arithmetic, and no rung of it ever reads out of bounds on any input.
//!
//! There is no scratch buffer and nothing crosses a call boundary -- `val`,
//! `shift`, `nb`, `p` and `acc` are locals -- so the driver's repeat protocol is
//! honest by construction. ../NOTES.md 0c measures it rather than asserting it.

#[path = "../../common/driver.rs"]
mod driver;

const VBITS: u32 = 64;

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md. `#[inline(never)]` only in `isolated` builds, so the
// `whole` builds can inline it the way LTO'd C would.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    if len < 4 {
        return 0;
    }
    let nv: usize = buf[off] as usize + 256 * (buf[off + 1] as usize)
        + 65536 * (buf[off + 2] as usize) + 16777216 * (buf[off + 3] as usize);
    if nv == 0 {
        return 0;
    }
    let mut acc: u64 = 0;
    let mut p: usize = 4;
    let mut v: usize = 0;
    while v < nv {
        if p == len {
            break;
        }
        let mut val: u64 = 0;
        let mut shift: u32 = 0;
        let mut nb: usize = 0;
        while p < len {
            let c: u8 = buf[off + p];
            p = p + 1;
            nb = nb + 1;
            // THE SAFETY LINE. c/kernel.c omits exactly this.
            if shift < VBITS {
                val = val | (((c & 0x7f) as u64) << shift);
            }
            shift = shift.wrapping_add(7);
            if c & 0x80 == 0 {
                break;
            }
        }
        acc = acc.wrapping_mul(31).wrapping_add(val);
        acc = acc.wrapping_mul(31).wrapping_add(nb as u64);
        v = v + 1;
    }
    acc.wrapping_mul(31).wrapping_add(nv as u64)
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
