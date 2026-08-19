//! p11 rung R3 -- safe-tuned.
//!
//! Same semantics as R2, written the way an experienced Rust programmer writes
//! a NUL-terminated-record reader: reslice the window once, then hand each
//! remaining span to the standard library's *bounded* NUL search --
//! `CStr::from_bytes_until_nul`, which is `core::slice::memchr` -- and fold the
//! measured span with an iterator. The reslice and the iterator *are* the
//! bounds checks, they happen once per string rather than once per byte, and
//! they are outside both inner loops by construction rather than by the
//! optimiser's goodwill. Still zero `unsafe`.
//!
//! **This is the rung the pattern is about, and there are two in-contract
//! spellings of it.** `.memory/01-ladder.md` requires at least two and the
//! cheaper quoted; the other is `rest.iter().position(|&b| b == 0)`, built as a
//! control in NOTES.md 10a. They are not close:
//!
//! | scan spelling | what it lowers to | Ir per scanned byte |
//! |---|---|---|
//! | `CStr::from_bytes_until_nul` (this rung) | `core::slice::memchr`, 2 x u64 SWAR | **0.937500** above 15 bytes |
//! | `iter().position(\|&b\| b == 0)` | a scalar byte loop | **5.00000** |
//! | C `strlen` (R1/R1h) | glibc IFUNC -> AVX2 `vpcmpeqb %ymm` | **0.078125** |
//!
//! all three read off the disassembly (`body_len / K`), never off a marginal
//! (TASK_026 §0 item 2). **The R1-vs-R3 gap is therefore a LIBRARY and DISPATCH
//! difference, not a safety cost**, and NOTES.md 2 separates the terms rather
//! than quoting the ratio: glibc resolves `strlen` through an IFUNC to a
//! hand-written AVX2 routine at load time, while `core::slice::memchr` is
//! compiled once for baseline `x86-64` and nothing in this repo builds with
//! `-march`. This project retracted "C beats Rust" once for exactly this class
//! of error (`.memory/01-ladder.md`, p02's `memcpy` idiom), and the clang column
//! decides.
//!
//! **`core::slice::memchr` has a 16-byte threshold and it is visible in the
//! measurements.** The routine takes a scalar byte loop for spans below 16
//! bytes, so on `small.bin` (mean string length 7) this rung's scan is *not*
//! word-at-a-time at all and pays a call as well. `large.bin`'s mean length is
//! 100. That is why ../spec.md requires the two measured inputs to have
//! different mean string lengths, and why the sweep walks length 1..64.
//!
//! `str::from_utf8` / `CStr::to_str` would be the next step a real reader takes
//! and is deliberately *not* here: it is a validation pass this kernel does not
//! specify, and it would put a third loop over the same bytes.

use std::ffi::CStr;

#[path = "../../common/driver.rs"]
mod driver;

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    if len < 4 {
        return 0;
    }
    let w: &[u8] = &buf[off..off + len];
    let nstr: usize = w[0] as usize + 256 * (w[1] as usize)
        + 65536 * (w[2] as usize) + 16777216 * (w[3] as usize);
    if nstr == 0 {
        return 0;
    }
    let mut acc: u64 = 0;
    let mut p: usize = 4;
    let mut s: usize = 0;
    while s < nstr {
        let rest: &[u8] = &w[p..];
        let q: usize = p + match CStr::from_bytes_until_nul(rest) {
            Ok(c) => c.to_bytes().len(),
            Err(_) => rest.len(),
        };
        let slen: usize = q - p;
        let h: u64 = w[p..q]
            .iter()
            .fold(0u64, |h, &b| h.wrapping_mul(31).wrapping_add(b as u64));
        acc = acc.wrapping_mul(31).wrapping_add(h ^ (slen as u64));
        if q >= len {
            break;
        }
        p = q + 1;
        if p >= len {
            break;
        }
        s = s + 1;
    }
    acc.wrapping_mul(31).wrapping_add(nstr as u64)
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
