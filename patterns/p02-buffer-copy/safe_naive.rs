//! p02 rung R2 -- safe-naive.
//!
//! The mechanical port a working Rust programmer writes first: read the prefix
//! with `src[i]`, reject a record that does not fit, then copy it a byte at a
//! time with indexed writes. Zero `unsafe`.
//!
//! The three-term rejection test is the *same* test R1h, R3, R4 and R5 write.
//! Safe Rust does not make it unnecessary; it makes omitting it a panic instead
//! of an out-of-bounds write. That difference is the pattern.
//!
//! **Do not read this rung's number as a bounds-check tax.** TASK_004 did, and
//! TASK_004_REVIEW refuted it by changing one loop at a time (NOTES.md §3a):
//! the indexed *fold* below costs exactly zero against R4, and the whole delta
//! comes from the indexed *copy* not being turned into a `memcpy`. The reason
//! is the rejection test one line above it: `src.len() - (src_off + 2)` is
//! subtraction-first (spec.md:44-48 mandates that -- the additive form can wrap
//! `usize` and wave the attack through), and LLVM cannot then prove the loop
//! index in bounds, so loop-idiom recognition never fires. Writing the check
//! additively flips `bulk_calls []` -> `['memcpy@GLIBC_2.14']` and 118
//! instructions -> 87. This rung is kept exactly as it is because it is a *fair*
//! naive port -- a real programmer does write this -- but its cost is a codegen
//! accident and it must be reported beside the variants in NOTES.md §3a.

#[path = "../../common/driver.rs"]
mod driver;

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md. `#[inline(never)]` only in `isolated` builds, so the
// `whole` builds can inline it the way LTO'd C would.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(src: &[u8], src_off: usize, dst: &mut [u8]) -> u64 {
    let len: usize = src[src_off] as usize + 256 * (src[src_off + 1] as usize);
    if len > dst.len() || len > src.len() - (src_off + 2) {
        return 0;
    }
    for i in 0..len {
        dst[i] = src[src_off + 2 + i];
    }
    let mut acc: u64 = 0;
    for i in 0..len {
        acc = acc.wrapping_add(dst[i] as u64);
    }
    acc
}

// ---------------------------------------------------------------- driver ----
fn main() {
    let path = driver::arg_path();
    let inp = driver::load(&path);
    let (cap_w, stride_w, bytes) = driver::head2_u64_bytes(&inp);
    let n_iters: u64 = inp.n_iters;
    let mut dbuf: Vec<u8> = driver::zeroed(cap_w);
    // SLB-DRIVER-BEGIN
    let n_src: usize = bytes.len();
    let src: &[u8] = bytes.as_slice();
    let dst: &mut [u8] = dbuf.as_mut_slice();
    let mut acc: u64 = 0;
    if stride_w >= 2 && stride_w <= n_src as u64 {
        let stride: usize = stride_w as usize;
        let nrec: u64 = (n_src / stride) as u64;
        let mut it: u64 = 0;
        while it < n_iters {
            let k: usize = ((acc as u128 * nrec as u128) >> 64) as usize;
            let r: u64 = kernel(src, k * stride, dst);
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    driver::emit(acc);
}
