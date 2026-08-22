//! p38 rung R2 -- safe Rust, naive. **Immune to p38's bug by construction.**
//!
//! This rung is not "the C bug with a bounds check added". Rust has **no
//! type-based aliasing rule at all**: `&mut T`'s `noalias` is *uniqueness*, a
//! provenance property, and no Rust reference or raw pointer carries a type tag
//! the optimiser may reason from. There is therefore nothing here for the
//! aliasing rule to exploit, and nothing this rung had to do to be safe from
//! it. It writes the length back through `u16` lvalues and reads it back the
//! only way Rust offers -- from the same `u16` array -- and the read observes
//! the write, at every optimisation level, on every compiler this project has.
//!
//! **That is the pattern's headline and it is what makes p38 different from
//! every other pattern here.** Everywhere else the shape is *C has the bug,
//! safe Rust rejects it, R4 gets it back*. Here R2, R3, R4 and R5 are all
//! immune, and none of them is immune because of a check. ../NOTES.md 5 lists
//! the four columns that say so; that is the finding, not a gap.
//!
//! The naive spelling: every access to the window and to the scratch is a
//! bounds-checked index. R3 reslices, R4 uses `get_unchecked`, and the
//! difference between them is p38's safety column -- which is an ordinary one
//! and has nothing to do with aliasing.

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
    let mut j: usize = 0;
    while j < nw {
        sc[j] = buf[off + 4 + 2 * j] as u16 + 256 * (buf[off + 5 + 2 * j] as u16);
        j = j + 1;
    }
    let mut acc: u64 = 0;
    let mut i: usize = 0;
    let mut o: usize = 0;
    while o < nrec && i + 2 <= nw {
        let room: usize = (nw - i - 2) / 2;
        // THE CLAMP, written through `u16` lvalues exactly as the C rungs
        // write it -- and read back below through `u16` lvalues, because that
        // is the only way Rust offers. Nothing here can be reordered past it.
        if sc[i] as usize + 65536 * (sc[i + 1] as usize) > room {
            sc[i] = (room % 65536) as u16;
            sc[i + 1] = (room / 65536) as u16;
        }
        let n: usize = sc[i] as usize + 65536 * (sc[i + 1] as usize);
        let mut k: usize = 0;
        while k < 2 * n {
            acc = acc.wrapping_mul(31).wrapping_add(sc[i + 2 + k] as u64);
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
