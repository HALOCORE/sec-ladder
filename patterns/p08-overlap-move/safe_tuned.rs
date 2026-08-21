//! p08 rung R3 -- safe-tuned.
//!
//! Same semantics as R2, written the way an experienced Rust programmer writes
//! an in-place shift: `copy_within`. That is the only safe spelling of the
//! operation, and it is `memmove` semantics **by construction** -- the overlap
//! is not checked for and not rejected, it is *defined*.
//!
//! **R2 and R3 differ in the body of `move_right` and in nothing else** -- same
//! header decode, same guard, same `copy_in` (both safe rungs keep the `dst[..n]`
//! receiver; R4/R5 respell it `split_at_mut` -- NOTES.md 6d), same fold, same
//! loop forms. So
//! R2 - R3 is the cost of the naive spelling, measured rather than attributed
//! (`.memory/01-ladder.md`: *attribute to a mechanism, never to a comparison*).
//!
//! `.memory/01-ladder.md`: never publish a safety-cost claim without this rung.
//! On p08 R3 is not merely free, it is the whole result -- it emits the same
//! `memmove` call R4 does (NOTES.md 3), so on this pattern the tuned SAFE rung
//! IS the unsafe rung.

#[path = "../../common/driver.rs"]
mod driver;

/// The scratch capacity. A compile-time constant, like p02's destination
/// buffer -- but `m = min(avail, SCR)` and `avail` comes from the file, so the
/// measured length is attacker data and nothing is constant-folded.
const SCR: usize = 4096;

/// Copy the window's `n` data bytes into the scratch.
///
/// **THE RECEIVER IS SCOPED 2-AND-2 (TASK_056).** `dst[..n]` is the receiver
/// here and in the other safe rung; `dst.split_at_mut(n)` is the receiver in
/// `unsafe.rs` and `verus.rs`, because `RangeTo` has no `SliceIndexSpecImpl` at
/// the pinned vstd and the `identity` pin makes R4 and R5 one program. Nothing
/// chains this rung to the prover, so it does not respell. **The price of the
/// split is published and it is not zero**: `-O3` byte-identical, `-O0` +2
/// static instructions and **+27.00 whole-program `Ir`/call** on R4 and R5 only
/// (+2.00 exclusive of `kernel`; the two metrics differ and NOTES.md 6d says
/// why). p06's `idiom.required[5].rust` is the precedent for the 2-and-2 scope.
#[inline(always)]
fn copy_in(dst: &mut [u8], src: &[u8], from: usize, n: usize) {
    dst[..n].copy_from_slice(&src[from..from + n]);
}

/// THE OPERATION: `v[dr..m] <- v[0..m-dr]`.
///
/// R3's spelling: `copy_within`, which is the *only* safe way to express this
/// in one buffer and is `memmove` semantics by definition -- correct by
/// construction, with the overlap ruled out not by a check but by the operation
/// having been chosen. Measured: it lowers to a tail `jmp memmove`, the same
/// call R4's `ptr::copy` emits (NOTES.md 3).
#[inline(always)]
fn move_right(v: &mut [u8], dr: usize, m: usize) {
    v.copy_within(0..m - dr, dr);
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
