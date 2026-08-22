//! p38 rung R4 -- unsafe Rust. **Still immune, and this is the pattern's
//! point.**
//!
//! Every other pattern in this tree has the shape *"C has the bug, safe Rust
//! rejects it, and `unsafe` gets it back"*. p38 is the first where `unsafe`
//! does **not** get it back, because the thing it would have to get back does
//! not exist in the language: Rust has no type-based aliasing rule, so no
//! amount of `unsafe` makes a `u32` read of a `[u16]` into undefined behaviour.
//! `ptr::read_unaligned::<u32>` on a `*const u16` is *defined Rust* and returns
//! the bytes that are there.
//!
//! ⚠ **AND THIS RUNG DOES NOT SPELL IT THAT WAY, FOR A REASON THAT IS ITSELF A
//! RESULT.** ../spec.md pins `identity: unsafe == verus, O3 exact`, so an R4
//! is not a program that *may* use `unsafe`: it is a program that must have a
//! byte-identical R5 twin that Verus verifies (`.memory/01-ladder.md` finding
//! 14). At the pinned vstd, `as_ptr`, `add` and `read_unaligned` are each
//! `is not supported`, so the direct analogue of C's pun is **not an
//! admissible R4** -- it would cost a new trusted item. It ships as the control
//! `r4_pun` in controls/gen_controls.py with the Verus error text beside it,
//! and ../NOTES.md 8 measures it. **The safe class reaches a spelling the
//! unsafe class cannot, on a pattern whose subject is that spelling** -- the
//! fifth instance of that result and the sharpest.
//!
//! What this rung does instead is the ordinary R4 lever: the two bounds checks
//! per scratch access and the one per window byte become `get_unchecked` /
//! `get_unchecked_mut`, licensed by the guards already in the algorithm. The
//! obligations are the same ones R5 discharges.

#[path = "../../common/driver.rs"]
mod driver;

/// The decode scratch, in words. Must equal `SLB_P38_SCRATCH_W` in c/kernel.h
/// and `SCRATCH_W` in model.py.
const SCRATCH_W: usize = 256;

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md. Every unchecked access below is discharged in
// ../verus.rs; the exec code there is this code, character for character.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    if len < 4 {
        return 0;
    }
    let nrec: usize = unsafe {
        *buf.get_unchecked(off) as usize + 256 * (*buf.get_unchecked(off + 1) as usize)
            + 65536 * (*buf.get_unchecked(off + 2) as usize)
            + 16777216 * (*buf.get_unchecked(off + 3) as usize)
    };
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
        let w: u16 = unsafe {
            *buf.get_unchecked(off + 4 + 2 * j) as u16
                + 256 * (*buf.get_unchecked(off + 5 + 2 * j) as u16)
        };
        unsafe {
            *sc.get_unchecked_mut(j) = w;
        }
        j = j + 1;
    }
    let mut acc: u64 = 0;
    let mut i: usize = 0;
    let mut o: usize = 0;
    while o < nrec && i + 2 <= nw {
        let room: usize = (nw - i - 2) / 2;
        // THE CLAMP. Unchecked stores through `u16` lvalues, read back below
        // through `u16` lvalues. There is no type-based aliasing rule in Rust
        // for `unsafe` to unlock, so this read observes this write.
        let d: usize = unsafe {
            *sc.get_unchecked(i) as usize + 65536 * (*sc.get_unchecked(i + 1) as usize)
        };
        if d > room {
            let lo: u16 = (room % 65536) as u16;
            let hi: u16 = (room / 65536) as u16;
            unsafe {
                *sc.get_unchecked_mut(i) = lo;
                *sc.get_unchecked_mut(i + 1) = hi;
            }
        }
        let n: usize = unsafe {
            *sc.get_unchecked(i) as usize + 65536 * (*sc.get_unchecked(i + 1) as usize)
        };
        let mut k: usize = 0;
        while k < 2 * n {
            acc = acc.wrapping_mul(31).wrapping_add(unsafe {
                *sc.get_unchecked(i + 2 + k) as u64
            });
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
