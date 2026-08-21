//! p10 rung R4 -- unsafe.
//!
//! R2's structure with every bounds check removed: `get_unchecked` on the
//! header, on the coefficients and on the samples. **The obligation it takes on
//! is exactly the one `c/kernel.c` gets wrong** -- that the largest index it
//! forms, `off + 8 + taps + n - 1`, is inside `buf` -- and `verus.rs` discharges
//! it from the `last >= len` guard plus the kernel's one structural
//! precondition.
//!
//! **This rung is not check-free by fiat: it is check-free because the guard is
//! still there.** Deleting `if last >= len` here does not make it faster, it
//! makes it `c/kernel.c` with the bug promoted from a one-byte overread to
//! whatever the header asks for -- and `verus.rs` stops verifying. ../NOTES.md
//! 10 has that mutant.
//!
//! ⚠ **AT `-O3` THIS RUNG'S TAP LOOP IS BYTE-IDENTICAL TO R2's IN ITS
//! VECTORISED BODY** -- the same seventeen-instruction SSE2 sequence per eight
//! taps. The difference between safe and unsafe here lives entirely in the
//! scalar epilogue (`taps mod 8` taps per output) and in a 22-instruction
//! per-output guard R2 pays and this rung does not. ../NOTES.md 8.
//!
//! ⚠ **AND SAFE RUST IS CHEAPER PER SCALAR-EPILOGUE TAP THAN THIS RUNG IS** --
//! 7.00 against 9.00 -- because `windows()`+`zip()` hands the epilogue two
//! consumed iterators where this rung's index arithmetic hands it three pointer
//! bumps. That is a *fixed-R4* comparison and nothing more
//! (`.memory/01-ladder.md` finding 14): it bounds
//! `inf(in-contract R3) - R4ship` and does not bound the class.
//! ../NOTES.md 8c.
//!
//! **`#[cfg(slb_isolated)] inline(never)`** matches every other rung, so the
//! `isolated` column measures a real call in all seven cells.

#[path = "../../common/driver.rs"]
mod driver;

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    if len < 8 {
        return 0;
    }
    let n: usize = unsafe { *buf.get_unchecked(off) } as usize
        + 256 * (unsafe { *buf.get_unchecked(off + 1) } as usize)
        + 65536 * (unsafe { *buf.get_unchecked(off + 2) } as usize)
        + 16777216 * (unsafe { *buf.get_unchecked(off + 3) } as usize);
    let r: usize = unsafe { *buf.get_unchecked(off + 4) } as usize
        + 256 * (unsafe { *buf.get_unchecked(off + 5) } as usize)
        + 65536 * (unsafe { *buf.get_unchecked(off + 6) } as usize)
        + 16777216 * (unsafe { *buf.get_unchecked(off + 7) } as usize);
    let taps: usize = 2 * r + 1;
    // THE WINDOW GUARD, present in every rung: without it `n - 2*r` underflows.
    if n < taps {
        return 0;
    }
    let last: usize = 8 + taps + n - 1;
    // THE SAFETY LINE. c/kernel.c writes `last > len`. Here it is also the
    // whole of what discharges this rung's `get_unchecked` obligations.
    if last >= len {
        return 0;
    }
    let nout: usize = n - 2 * r;
    let sb: usize = 8 + taps;
    let mut acc: u64 = 0;
    let mut i: usize = 0;
    while i < nout {
        let mut s: u32 = 0;
        let mut j: usize = 0;
        while j < taps {
            s = s.wrapping_add(
                (unsafe { *buf.get_unchecked(off + sb + i + j) } as u32)
                    .wrapping_mul(unsafe { *buf.get_unchecked(off + 8 + j) } as u32));
            j = j + 1;
        }
        acc = acc.wrapping_mul(31).wrapping_add(s as u64);
        i = i + 1;
    }
    acc.wrapping_mul(31).wrapping_add(nout as u64)
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
