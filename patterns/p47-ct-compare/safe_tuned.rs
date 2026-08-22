//! p47 rung R3 -- safe-tuned. **The constant-time rung, in safe Rust.**
//!
//! R2's structure with the comparison replaced by the or-accumulate:
//! `a.iter().zip(b.iter()).fold(0u8, |acc, (x, y)| acc | (x ^ y))`, then one
//! test of the accumulator. No `unsafe`, no `black_box`, no crate, no
//! `volatile`.
//!
//! ⚠ **THE MANAGER'S TASK FILE ASKED WHETHER LLVM SHORT-CIRCUITS THIS FOLD AT
//! `-O3`, AND THE ANSWER IS NO.** Measured before this file was written
//! (../NOTES.md 0): the fold vectorises to SSE2 `movdqu/movdqu/pxor/por`,
//! contains no data-dependent branch, and its `Ir` is **constant to the
//! instruction** across thirteen values of the first-mismatch position `k` --
//! 489 905 at every one of them, at `-C opt-level=2` and `=3`, in a free
//! function and inlined into a caller that *branches on the result*, and for
//! fixed-size arrays as well (`[u8;16]` becomes
//! `pcmpeqb ; pmovmskb ; xor ; cmove`, branchless). So *"constant-time code is
//! not expressible in safe Rust at -O3"* -- which the task file offered as the
//! stronger alternative finding -- is **false on this toolchain**, and the
//! weaker, true statement is the one p47 ships.
//!
//! ⚠ **BUT THE ACCUMULATOR TYPE IS LOAD-BEARING AND `u8` IS THE ONLY GOOD
//! ONE.** `fold(0u64, |acc, (x, y)| acc | ((x ^ y) as u64))` -- the same
//! algorithm, one cast different -- lowers to a `movzwl/punpcklbw/punpcklwd/
//! punpckldq` widening loop that moves **4 bytes per iteration** instead of
//! 32, because LLVM vectorises the zero-extension rather than the xor.
//! ../spec.md pins `fold(0u8` for that reason and ../NOTES.md 8 measures the
//! difference. It is still constant-time; it is just five times the work.
//!
//! **What this rung does NOT change from R2 is the slicing.** Both reslice the
//! window twice per comparison with `&buf[a..b]`, so the bounds checks and the
//! panic pads are identical between them and `R2 - R3` is a pure *comparison
//! idiom* difference with the safety term cancelled. That matching is
//! deliberate: it is the only pair in this pattern that isolates the leak from
//! everything else, and `.memory/01-ladder.md` finding 14 is why it had to be
//! built that way rather than reasoned about.
//!
//! **R3 is DEARER than R2 on mismatching data and CHEAPER on matching data**,
//! and both directions are the same fact: R2 stops early. ../NOTES.md 4 quotes
//! the crossover.

#[path = "../../common/driver.rs"]
mod driver;

const MATCH: u64 = 7;
const MISS: u64 = 251;

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    if len < 8 {
        return 0;
    }
    let ntag: usize = buf[off] as usize + 256 * (buf[off + 1] as usize)
        + 65536 * (buf[off + 2] as usize) + 16777216 * (buf[off + 3] as usize);
    let tlen: usize = buf[off + 4] as usize + 256 * (buf[off + 5] as usize)
        + 65536 * (buf[off + 6] as usize) + 16777216 * (buf[off + 7] as usize);
    if ntag == 0 || tlen == 0 {
        return 0;
    }
    let mut acc: u64 = 0;
    let mut p: usize = 8;
    let mut o: usize = 0;
    while o < ntag && len - p >= 2 * tlen {
        // THE TIMING LINE. Every byte is read on every call; the accumulator
        // is tested once, after the fold.
        let a: &[u8] = &buf[off + p..off + p + tlen];
        let b: &[u8] = &buf[off + p + tlen..off + p + 2 * tlen];
        let d: u8 = a.iter().zip(b.iter()).fold(0u8, |acc, (x, y)| acc | (x ^ y));
        acc = if d == 0 {
            acc.wrapping_mul(31).wrapping_add(MATCH)
        } else {
            acc.wrapping_mul(31).wrapping_add(MISS)
        };
        p = p + 2 * tlen;
        o = o + 1;
    }
    acc.wrapping_mul(31).wrapping_add(o as u64)
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
