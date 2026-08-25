//! p19 rung R3 -- safe Rust, tuned. **This is the rung the pattern is for.**
//!
//! One lever, zero `unsafe`, zero trusted items: mask the state before using it
//! as a row index.
//!
//!     st = tbl[(st & (NST - 1)) * 256 + b as usize] as usize;   // R3
//!     st = tbl[ st                * 256 + b as usize] as usize;   // R2
//!
//! `(st & 7) * 256 + b <= 7*256 + 255 = 2047 < tbl.len()`, and `tbl` was formed
//! by `&w[0..TBL]` so LLVM knows its length is the constant 2048. The index is
//! therefore provably in range, the bounds check is **deleted**, and the fold
//! unrolls 4x -- which the checked spelling's exit edge forbids.
//!
//! ⚠⚠ **THE MASK IS NOT A DIFFERENT PROGRAM, AND THE REASON IS THE PROOF.**
//! The validation pass above the fold establishes `st < NST` on every path that
//! reaches it, so `st & (NST - 1) == st` **identically, on every input this
//! benchmark can present**, adversarial ones included -- and that equality is
//! precisely the loop invariant ../verus.rs discharges (`st < NST`, ../NOTES.md
//! 6). R2 and R3 return the same `u64` on all EIGHT gate-checked inputs. (They
//! also agree on the 19 `sweep-m*` blobs, but those are diagnostic and are not
//! in `inputs_checked`; this line used to say "nine", which was neither count.)
//! **Delete the validation pass and the claim fails**: the mask would silently
//! remap an out-of-range state where the checked spelling panics. So this rung
//! is a respelling *because* the pattern validates, and the same two lines
//! without the pass would be two different benchmarks. ../spec.md's `idiom.why`
//! says so in the hashed block.
//!
//! ⚠ **AND THE MASK IS NOT FREE.** It is exactly one `and $0x7` per message
//! byte -- `R3 - R4 = 1.00000 * m + 4 - [m mod 4 != 0]` instructions per call,
//! zero residual over the 19 committed `sweep-m*` lengths (../NOTES.md 12).
//! ⚠ This line used to read `1.00000 * m - 2`, from a five-length probe on a
//! DIFFERENT BINARY whose lengths were all `m = 0 (mod 4)`: **the slope was
//! right and the intercept was not, twice over.** The identical +1.00 appears when the mask is
//! added to the *unsafe* rung, which is how ../NOTES.md 8 attributes it to the
//! mask rather than to the check. **Safe Rust reaches within one instruction
//! per byte of unsafe Rust here, and not to it: that one instruction is what a
//! proof replaces.**
//!
//! Levers considered and measured (../NOTES.md 10): the mask-plus-row-reslice
//! and the `&[u8; 2048]` `try_into` spellings land within 11 Ir/call of this
//! one; the branch-clamp spelling `if st < NST { st } else { 0 }` is **8.25
//! Ir/byte DEARER than the shipped R4**, i.e. dearer than the bounds check it
//! was meant to replace.

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
        st = tbl[(st & (NST - 1)) * 256 + b as usize] as usize;
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
