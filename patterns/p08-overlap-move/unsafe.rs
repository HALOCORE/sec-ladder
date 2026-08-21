//! p08 rung R4 -- unsafe.
//!
//! R3's kernel with the move written as a raw `core::ptr::copy`. That is
//! `memmove`, so this rung is *correct*; it just has nothing checking that the
//! pointer arithmetic is in range. R5 (verus.rs) is this exec code with the
//! SAFETY comment below turned into obligations a verifier discharges.
//!
//! **R3 and R4 differ in the body of `move_right` and in nothing else.** Both
//! lower to a tail `jmp memmove`; NOTES.md 3 reports whether the two kernels are
//! byte-identical, which is the question p08 was built to ask.
//!
//! **p08 has exactly one `unsafe` block and it is the pattern itself.** Every
//! earlier pattern in this project spent its `unsafe` on an element accessor --
//! `get_unchecked` -- because the harm being modelled was an out-of-bounds
//! index. p08's harm is not spatial: the guard `d + nrep > m` is present in
//! every rung, nothing leaves the scratch, and the bug is *aliasing*. So the
//! header decode and the fold are written with ordinary checked indexing here,
//! and NOTES.md 3 measures what that costs against C. (Measured: the fold's
//! bounds check is eliminated outright, because `m <= SCR` is provable from
//! `m = min(avail, SCR)` and `scr` has a compile-time length -- the safe and
//! unsafe folds are the same 25 instructions per 4 bytes.)

#[path = "../../common/driver.rs"]
mod driver;

/// The scratch capacity. A compile-time constant, like p02's destination
/// buffer -- but `m = min(avail, SCR)` and `avail` comes from the file, so the
/// measured length is attacker data and nothing is constant-folded.
const SCR: usize = 4096;

/// Copy the window's `n` data bytes into the scratch.
///
/// **THE RECEIVER IS SCOPED 2-AND-2, and the scope is TASK_056's.** `dst[..n]`
/// is the receiver in `safe_naive.rs` and `safe_tuned.rs`; `dst.split_at_mut(n)`
/// is the receiver here and in `verus.rs`. The split exists because `RangeTo`
/// has no `SliceIndexSpecImpl` at the pinned vstd, so `dst[..n]` is not
/// verifiable as written — and the `identity` pin makes R4 and R5 one program,
/// so R4 respells with R5 while nothing chains R2 and R3 to the prover. p06's
/// `idiom.required[5].rust` is the precedent and says the same thing.
///
/// **THE PRICE IS MEASURED, both halves** (`.memory/02-bench-rules.md`): at
/// `-O3` it is ZERO — `md5_raw 44b63d20ccf1`, 168/166, 5 pads, +0.00 `Ir`/call,
/// byte-identical to the `dst[..n]` spelling — and at `-O0` it costs this rung
/// and `verus.rs` **+2 static instructions (206/206 → 208/208)**, **+2.00
/// `Ir`/call exclusive of `kernel`** and **+27.00 `Ir`/call whole-program**,
/// which is the number the gate records in `marginal_ir_per_call`. The two
/// differ because at `-O0` `split_at_mut` is a real call and its 25
/// instructions are attributed to its own symbol. It is not a check: both
/// spellings keep exactly one bounds check and emit the same 5 panic pads at
/// the same sites. `<[T]>::split_at_mut` returns a two-slice tuple — four
/// words — so it comes back through the hidden `sret` pointer where
/// `<[T] as IndexMut<Range>>` returns two words in `rax:rdx`. ../NOTES.md 6d.
#[inline(always)]
fn copy_in(dst: &mut [u8], src: &[u8], from: usize, n: usize) {
    let (a, _b) = dst.split_at_mut(n);
    a.copy_from_slice(&src[from..from + n]);
}

/// THE OPERATION: `v[dr..m] <- v[0..m-dr]`.
///
/// R4's spelling: the raw `ptr::copy`, which is `memmove` and is therefore
/// *correct* -- this rung is unverified, not unsound.
///
/// SAFETY: `dr <= m <= SCR == v.len()`, established by the kernel's guard
/// `d + nrep > m -> reject` and by `m = min(avail, SCR)`, so `p.add(dr)` is in
/// bounds and `[p, p+m-dr)` and `[p+dr, p+m)` are both inside the object.
/// `ptr::copy` is `memmove`, so the overlap is defined. Unchecked here;
/// discharged by Verus in verus.rs, where this body is the pattern's ONE
/// trusted item.
///
/// **`ptr::copy_nonoverlapping` here would re-open the C bug exactly** -- its
/// whole safety contract is the non-overlap that `d` controls.
/// `controls/gen_controls.py` builds that mutant and NOTES.md 5 runs it under
/// Miri.
#[inline(always)]
fn move_right(v: &mut [u8], dr: usize, m: usize) {
    unsafe {
        let p = v.as_mut_ptr();
        core::ptr::copy(p, p.add(dr), m - dr);
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
