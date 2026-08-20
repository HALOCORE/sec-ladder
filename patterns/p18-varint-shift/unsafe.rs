//! p18 rung R4 -- unsafe.
//!
//! R2's algorithm with every bounds check removed: the four window-header bytes
//! and every varint byte the scan reads go through `get_unchecked`. **What does
//! NOT go away is `if shift < VBITS`** -- that is not a bounds check, it is the
//! kernel's semantics (the hardened cell TRUNCATES at the accumulator's width
//! and `spec.md` pins that answer), and a rung without it would be R1's
//! undefined shift written in Rust rather than an unsafe rung. This rung is
//! correct; it just has nothing checking that it is. R5 (verus.rs) is this exec
//! code with the SAFETY comments below turned into obligations a verifier
//! discharges.
//!
//! SAFETY (1): `off + len <= buf.len()` is the caller's structural
//!   precondition. Unchecked here; discharged at the call site by Verus in
//!   verus.rs.
//! SAFETY (2): `len >= 4` guards the window header, so
//!   `off + 3 < off + len <= buf.len()`.
//! SAFETY (3): the scan reads `buf[off + p]` only under `p < len`, and `p` never
//!   decreases, so `off + p < off + len <= buf.len()`.
//!
//! **p18's `unsafe` block does NOT carry the pattern's bug, and that is what
//! makes this rung worth reading.** In every earlier pattern the missing line
//! and the `unsafe` are about the same fact: R1's overrun is exactly what the
//! trusted accessor's `requires` excludes. Here they are about DIFFERENT facts.
//! The `unsafe` is spatial -- `i < v.len()` -- and R1's bug is arithmetic --
//! `shift < 64`. So **this rung's trusted base has nothing to say about the
//! pattern's bug**, its trusted `requires` would discharge just as happily with
//! the safety line deleted, and the only thing in the whole ladder that rejects
//! the deletion is R5's `possible bit shift underflow/overflow`. ../NOTES.md 6
//! tabulates that and ../NOTES.md 10 measures it on a mutant.
//!
//! There is no bulk load and no scratch: p18's kernel reads bytes one at a time
//! by construction, because the length of a varint is not known until its last
//! byte has been read. So p14's `scr_load` has no analogue here, no rung calls
//! any libc routine inside the kernel, and the kernel-exclusive `Ir` column is a
//! comparison of seven rungs that all call NOTHING (`.memory/03-measurement.md`,
//! "the kernel-exclusive column is comparable only when the rungs call the SAME
//! libc routines" -- here the set is empty in all seven, which is the strongest
//! form of that condition and ../NOTES.md 3 verifies it from the disassembly).
//!
//! The cursor guards compare `p` against `len` directly rather than
//! subtraction-first, because p18's cursor advances by ONE and never by a
//! declared length: `p < len` needs no arithmetic at all, so there is nothing to
//! overflow and nothing for a `requires` to buy back. That is why p07's and
//! p14's subtraction-first idiom does not appear here. ../NOTES.md 5.

#[path = "../../common/driver.rs"]
mod driver;

const VBITS: u32 = 64;

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    if len < 4 {
        return 0;
    }
    let nv: usize = unsafe { *buf.get_unchecked(off) } as usize
        + 256 * (unsafe { *buf.get_unchecked(off + 1) } as usize)
        + 65536 * (unsafe { *buf.get_unchecked(off + 2) } as usize)
        + 16777216 * (unsafe { *buf.get_unchecked(off + 3) } as usize);
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
            let c: u8 = unsafe { *buf.get_unchecked(off + p) };
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
