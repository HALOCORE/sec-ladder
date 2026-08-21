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
//! ⚠ **AT `-O3` THIS RUNG'S VECTORISED TAP BODY IS THE SAME SEVENTEEN SSE2
//! INSTRUCTIONS AS R2's, IN THE SAME MNEMONIC ORDER -- but NOT byte-identical**
//! (the register allocation differs; an earlier draft of this comment said
//! "byte-identical" and that was wrong, ../NOTES.md 1). The difference between
//! safe and unsafe lives in the scalar epilogue (`taps mod 8` taps per output)
//! and in a **24**-instruction per-output guard R2 pays and this rung does not
//! -- 24 counted on the shipped listing; a day-one probe with a different guard
//! structure gave 22, so the number is a property of a spelling.
//! ../NOTES.md 8c.
//!
//! ⚠ **THIS RUNG IS DEARER THAN SAFE `windows()+zip()`, AND NOT BECAUSE OF A
//! BOUNDS CHECK.** Both figures are `-O3`, and BOTH MODES ARE QUOTED because
//! the mechanism is different in each (../NOTES.md 8b, 8b3):
//!
//! * `isolated`: this rung and R3 cost the SAME 9 instructions per epilogue tap
//!   -- the `scaltap` coefficient of `R3 - R4` is exactly **0.00** -- and the
//!   whole margin is **-5.00 Ir per OUTPUT**, four outer induction variables and
//!   two stack reloads against R3's one advancing pointer.
//! * `whole`: the per-output difference vanishes (26.00 both) and the same cause
//!   reappears in the epilogue as **-2.00 Ir per epilogue tap**, R3's 7 against
//!   this rung's 9 -- two `lea`s re-forming `off + sb + i + j` and `off + 8 + j`
//!   every tap.
//!
//! **It is the index expression and not the safety**: `c-clang`, idiomatic C
//! with no bounds check anywhere and the same four-term index, fits `nout` at
//! **30.00** isolated -- dearer per output than BOTH Rust rungs -- and matches
//! R3 exactly in `whole` (26.00/output, 7/epilogue tap).
//!
//! ⚠ **The 7.00-against-9.00 figure this comment used to carry was the day-one
//! probe's, not the shipped cells'**, and it flattered the pattern's headline;
//! it is retracted at ../NOTES.md 14. All of the above is still a *fixed-R4*
//! comparison (`.memory/01-ladder.md` finding 14) -- see ../NOTES.md 8e for the
//! admissible cheaper R4 (`u_win`) and the span it opens.
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
