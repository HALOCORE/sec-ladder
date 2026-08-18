//! p08 rung R2 -- safe-naive.
//!
//! **The C program this pattern models cannot be transliterated into safe Rust
//! at all.** `memcpy(scr + dr, scr, m - dr)` needs a `&[u8]` and a `&mut [u8]`
//! into one buffer at the same time, and the borrow checker rejects that at
//! *compile time* -- `E0502`, no runtime check, nothing to measure.
//! `controls/gen_controls.py` emits the exact program and NOTES.md 5 has the
//! `rustc` diagnostic. So the port a working Rust programmer actually writes is
//! the one below: an explicit **reverse** indexed byte loop.
//!
//! That is the fair naive port and not a pessimisation. It is what you get if
//! you know the shift must run high-to-low and you do not yet know
//! `copy_within` exists.
//!
//! **This rung is where p08's honesty lives.** Safe Rust prevents the
//! *undefined behaviour*; it does not prevent *wrongness*. Write the same loop
//! forward -- `for j in 0..m - dr { v[j + dr] = v[j] }` -- and you get a
//! silently replicated buffer, safely, with no panic and no diagnostic. That
//! control is built (`controls/gen_controls.py`, NOTES.md 5) because a write-up
//! that claims "Rust fixes this" without it is overclaiming.
//!
//! **R2, R3 and R4 differ in the body of `move_right` and in NOTHING else** --
//! same header decode, same guard, same `copy_in`, same fold, same loop forms.
//! `.memory/01-ladder.md`: *a safety tax must be attributed to a mechanism,
//! never to a comparison*. Here the mechanism is isolated by construction rather
//! than by a decomposition experiment afterwards.

#[path = "../../common/driver.rs"]
mod driver;

/// The scratch capacity. A compile-time constant, like p02's destination
/// buffer -- but `m = min(avail, SCR)` and `avail` comes from the file, so the
/// measured length is attacker data and nothing is constant-folded.
const SCR: usize = 4096;

/// Copy the window's `n` data bytes into the scratch. Identical in all four
/// Rust rungs; in verus.rs it is the one trusted item that is *not* the pattern.
#[inline(always)]
fn copy_in(dst: &mut [u8], src: &[u8], from: usize, n: usize) {
    dst[..n].copy_from_slice(&src[from..from + n]);
}

/// THE OPERATION: `v[dr..m] <- v[0..m-dr]`.
///
/// R2's spelling: a reverse indexed byte loop, bounds-checked on both sides.
/// Reverse because the ranges overlap when `2*dr < m` and a forward loop would
/// read a byte it had already overwritten. LLVM does **not** turn this into a
/// `memmove` call -- measured, `.temp/p08/probe/idiom.rs`, both `for` and
/// `while` spellings and on a slice as well as an array -- so this rung really
/// does execute `m - dr` checked byte moves.
#[inline(always)]
fn move_right(v: &mut [u8], dr: usize, m: usize) {
    for j in (0..m - dr).rev() {
        v[j + dr] = v[j];
    }
}

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md. `#[inline(never)]` only in `isolated` builds, so the
// `whole` builds can inline it the way LTO'd C would.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    if len < 4 {
        return 0;
    }
    let d: usize = buf[off] as usize + 256 * (buf[off + 1] as usize);
    let nrep_w: usize = buf[off + 2] as usize + 256 * (buf[off + 3] as usize);
    let avail: usize = len - 4;
    let m: usize = if avail < SCR { avail } else { SCR };
    let nrep: usize = 1 + nrep_w % 4;
    if m < 2 || d == 0 || d + nrep > m {
        return 0;
    }
    let mut scr: [u8; SCR] = [0u8; SCR];
    copy_in(&mut scr, buf, off + 4, m);
    for r in 0..nrep {
        let dr: usize = d + r;
        move_right(&mut scr, dr, m);
    }
    let mut acc: u64 = 0;
    for j in 0..m {
        acc = acc.wrapping_mul(31).wrapping_add(scr[j] as u64);
    }
    acc.wrapping_mul(31).wrapping_add(m as u64)
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
