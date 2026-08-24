//! p19 rung R2 -- safe Rust, naive. The obvious port of `c/kernel_hardened.c`:
//! index the table, let the language check the index.
//!
//! **What the language's check IS here, and why that is the whole point.**
//! `tbl[st * 256 + b]` panics when `st * 256 + b >= 2048`, i.e. when
//! `st >= NST` -- and LLVM lowers it to exactly that, `cmp $0x8,%rdx / jae`.
//! So safe Rust's automatic bounds check and the validation pass
//! `c/kernel.c` omits are **the same predicate**, enforced in two places: once
//! per access here, once per call there. The pattern prices both.
//!
//! This rung keeps the validation pass as well, so that all six rungs compute
//! the same function on every input including the adversarial ones. That is a
//! deliberate choice with a cost: it means R2's per-access check is *provably
//! redundant* on every call the benchmark makes, and LLVM still cannot remove
//! it, because the fact that would let it -- "every table entry is < NST" -- is
//! a loop-carried data invariant over 2048 bytes read at run time. ../verus.rs
//! proves that invariant; rustc never learns it. See `.memory/01-ladder.md`
//! finding 2.
//!
//! ⚠ The check is NOT hoistable and this is not an accident of spelling: `st`
//! is loop-carried and data-dependent, so there is no loop-invariant bound to
//! lift. Its exit edge also forecloses unrolling -- measured, the checked fold
//! body is **15 instructions for one byte** where the unchecked one is **35 for
//! four** (../NOTES.md 8).

#[path = "../../common/driver.rs"]
mod driver;

/// The decoder's table capacity. Must equal `SLB_P19_NST` in c/kernel.h and
/// `NST` in model.py.
const NST: usize = 8;

/// Bytes of transition table: `NST` rows of 256 columns.
const TBL: usize = NST * 256;

/// What an invalid table folds to.
const REJ: u64 = 0xd1b5_4a32_d192_ed03;

/// p19's kernel. Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    if len <= TBL {
        return 0;
    }
    let w: &[u8] = &buf[off..off + len];
    let tbl: &[u8] = &w[0..TBL];
    // >>> THE SAFETY LINE. c/kernel.c omits this loop. <<<
    let mut i: usize = 0;
    while i < TBL {
        if tbl[i] as usize >= NST {
            return REJ;
        }
        i = i + 1;
    }
    let msg: &[u8] = &w[TBL..len];
    let mut st: usize = 0;
    let mut acc: u64 = 0;
    for &b in msg {
        st = tbl[st * 256 + b as usize] as usize;
        acc = acc.wrapping_mul(31).wrapping_add(st as u64);
    }
    acc.wrapping_mul(31).wrapping_add(st as u64)
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
    if stride_w > 0 && stride_w <= n_blob as u64 {
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
