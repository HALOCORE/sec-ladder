//! p42 rung R3 -- safe-tuned.
//!
//! Same semantics as R2, rewritten to help LLVM. Two levers, and both are about
//! the SCRATCH rather than about the fold:
//!
//!   1. `Vec::with_capacity(len)` instead of `vec![0u8; len]`. R2's spelling
//!      allocates AND zeroes `len` bytes; this one only allocates. The zeroing
//!      is a cost safe Rust pays because it has no way to hand out
//!      uninitialised bytes -- and `with_capacity` is how safe Rust avoids
//!      paying it, by never observing the bytes before they are written.
//!   2. `extend` over an iterator with a known length, instead of `push` per
//!      element or an indexed store. `Map<slice::Iter>` is `TrustedLen`, so
//!      `Vec::extend` takes its specialised path: one capacity check for the
//!      whole run rather than one per element, and no bounds check on the
//!      store. The reverse fold is `.iter().rev().fold(..)`, which is an
//!      exact-size double-ended iterator and needs no index arithmetic at all.
//!
//! **What is NOT tuned away, deliberately: the allocation still precedes the
//! tag test.** ../spec.md pins that order for every rung. Moving the test up is
//! not a tuning, it is the fix for the bug the pattern is about, and a rung
//! that took it would be measuring a different program from the C rung.
//!
//! Still zero `unsafe`, and still one `return` on the error path with the
//! compiler's `Drop` glue behind it.
//!
//! ⚠ **`with_capacity` + `extend` is a REAL lever and not a spelling
//! preference**: it is the difference between `__rust_alloc_zeroed` and
//! `__rust_alloc`. ../NOTES.md 5 measures it.

#[path = "../../common/driver.rs"]
mod driver;

/// The low byte of a well-formed record header. ../spec.md "Payload layout".
const TAG: u64 = 0xA7;
/// The decode constant. Arbitrary and shared by all six rungs.
const MIX: u64 = 0x9E37_79B9_7F4A_7C15;
/// The driver's ceiling on the window length, and therefore on the digest
/// allocation. Outside the measured loop and carried by every rung; R5 needs it
/// to discharge `valid_layout`. See verus.rs's module comment.
const MAXWIN: u64 = 65536;

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(v: &[u64], off: usize, len: usize) -> u64 {
    let mut dig: Vec<u8> = Vec::with_capacity(len);
    if v[off] & 0xff != TAG {
        // The error path. `dig` is dropped here, exactly as in R2: the capacity
        // was reserved, nothing was written into it, and the compiler releases
        // it anyway because it owns it.
        return 0;
    }
    let mut run: u64 = 0;
    dig.extend(v[off..off + len].iter().map(|&x| {
        run = run.wrapping_add(x ^ MIX);
        (run >> 24) as u8
    }));
    dig.iter()
        .rev()
        .fold(0u64, |a, &b| a.wrapping_mul(31).wrapping_add(b as u64))
}

// ---------------------------------------------------------------- driver ----
fn main() {
    let path = driver::arg_path();
    let inp = driver::load(&path);
    let (win_len_w, vals) = driver::head_u64_body(&inp);
    let n_iters: u64 = inp.n_iters;
    // SLB-DRIVER-BEGIN
    let n_vals: usize = vals.len();
    let vs: &[u64] = vals.as_slice();
    let mut acc: u64 = 0;
    if win_len_w > 0 && win_len_w <= MAXWIN && win_len_w <= n_vals as u64 {
        let win_len: usize = win_len_w as usize;
        let nwin: u64 = (n_vals - win_len + 1) as u64;
        let mut it: u64 = 0;
        while it < n_iters {
            let off: usize = ((acc as u128 * nwin as u128) >> 64) as usize;
            let r: u64 = kernel(vs, off, win_len);
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    driver::emit(acc);
}
