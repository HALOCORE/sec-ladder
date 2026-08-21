//! p10 rung R3 -- safe-tuned.
//!
//! Same semantics as R2, written the way an experienced Rust programmer writes
//! a sliding-window reduction: **`slice::windows(taps)`**, which yields each
//! `2r+1`-wide window as a slice whose length LLVM already knows, and
//! `iter().zip()` over it and the coefficients. Zero `unsafe`, and **zero
//! indexing operations in the tap loop** -- where R2 has two per tap.
//!
//! **`slice::windows` takes a RUNTIME size.** `taps = 2*r + 1` is read out of
//! the file, and the whole R3 spelling depends on that being legal; it is
//! verified rather than assumed (../NOTES.md 0.1). It is also why
//! `chunks_exact` is FORBIDDEN and `windows` is not: `chunks_exact` with a
//! runtime chunk size computes `len - len % chunk_size` and lowers to a
//! hardware `div`, which callgrind prices at **one `Ir`** and the machine at
//! tens of cycles (`.memory/03-measurement.md`). `windows` needs no division
//! and the disassembly of all eight cells contains no `div`/`idiv`
//! (../NOTES.md 1).
//!
//! ⚠ **THIS IS THE FIRST USE OF `windows()` IN THIS PROJECT.**
//! `grep -rn "windows(" patterns/*/*.rs` returned nothing before p10.
//!
//! **The window reslice is the TWO-STEP form** (`.memory/01-ladder.md`
//! finding 3, the p04 lever): `buf.split_at(off).1.split_at(len).0` rather than
//! `&buf[off..off + len]`. Both keep both bounds checks and both contribute the
//! same **two** panic landing pads, so the difference is not check removal.
//! ⚠ **What is measured here is exactly `-1.00 Ir/call`, on both blobs, and
//! `.memory/03-measurement.md` says a one-instruction win is
//! INSTRUCTION-COUNT-ONLY and this box cannot supply the wall-clock column to
//! rescue it.** So p10 confirms finding 3's sign and magnitude and **does not
//! retire the backlog item** -- an earlier draft of ../NOTES.md 8d said it did,
//! and that is retracted at ../NOTES.md 14.
//!
//! **TWO MORE IN-CONTRACT R3 SPELLINGS ARE MEASURED AND PUBLISHED BESIDE THIS
//! ONE** (`.memory/01-ladder.md` finding 3, which four patterns have got wrong
//! by publishing a point instead of its class): `t_winidx`, whose inner loop
//! indexes the window `windows()` already handed it, and `t_1step`, whose
//! reslice is the one-step form. ../NOTES.md 8d quotes all of them with the
//! input named, and **this one is not the cheapest**. Which spelling ships was
//! decided before any p10 cell was measured -- this one, because
//! `windows() + zip()` is the library idiom p10 exists to exercise -- and
//! `.memory/02-bench-rules.md`'s "NEVER re-ship a rung because a cheaper
//! in-contract spelling was found" is why that order matters.
//!
//! **What is deliberately NOT reached for: `chunks_exact`, `from_le_bytes`,
//! `.sum()`, `step_by` and `copy_from_slice`.** ../spec.md forbids all five
//! **in every rung** rather than in some -- a whole-pattern exclusion, which
//! keeps the two sides of the comparison equal, unlike the scoped kind
//! `.memory/01-ladder.md` caught on p13. `.sum()` in particular: `Sum for u32`
//! uses `+`, which panics under `-C debug-assertions=on` and under Miri, so a
//! rung using it would behave differently in two of the gate's own
//! configurations while looking identical in the twenty-four measured cells.

#[path = "../../common/driver.rs"]
mod driver;

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    if len < 8 {
        return 0;
    }
    let w: &[u8] = buf.split_at(off).1.split_at(len).0;
    let n: usize = w[0] as usize + 256 * (w[1] as usize)
        + 65536 * (w[2] as usize) + 16777216 * (w[3] as usize);
    let r: usize = w[4] as usize + 256 * (w[5] as usize)
        + 65536 * (w[6] as usize) + 16777216 * (w[7] as usize);
    let taps: usize = 2 * r + 1;
    // THE WINDOW GUARD, present in every rung: without it `n - 2*r` underflows.
    if n < taps {
        return 0;
    }
    let last: usize = 8 + taps + n - 1;
    // THE SAFETY LINE. c/kernel.c writes `last > len`.
    if last >= len {
        return 0;
    }
    let nout: usize = n - 2 * r;
    let coef: &[u8] = &w[8..8 + taps];
    let samp: &[u8] = &w[8 + taps..8 + taps + n];
    let mut acc: u64 = 0;
    for win in samp.windows(taps) {
        let mut s: u32 = 0;
        for (a, b) in win.iter().zip(coef.iter()) {
            s = s.wrapping_add((*a as u32).wrapping_mul(*b as u32));
        }
        acc = acc.wrapping_mul(31).wrapping_add(s as u64);
    }
    acc.wrapping_mul(31).wrapping_add(nout as u64)
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
