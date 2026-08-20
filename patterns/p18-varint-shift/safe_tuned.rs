//! p18 rung R3 -- safe-tuned.
//!
//! Same semantics as R2, written the way an experienced Rust programmer writes
//! a varint decoder that must stay inside one window: reslice the window once so
//! that every per-byte bounds check is against a slice whose length LLVM already
//! knows, and keep the scan an explicit cursor. Zero `unsafe`.
//!
//! **The window reslice is the TWO-STEP form** (`.memory/01-ladder.md`
//! finding 3, the p04 lever): `buf.split_at(off).1.split_at(len).0` rather than
//! `&buf[off..off + len]`. Both keep both bounds checks; the two-step form is
//! one instruction cheaper because `buf_len - off` is computed in place in a
//! register that is dead afterwards while `off + len` needs a scratch one.
//! ../NOTES.md 8 reports what it is worth here.
//!
//! **TWO MORE IN-CONTRACT R3 SPELLINGS ARE MEASURED AND PUBLISHED BESIDE THIS
//! ONE** (`.memory/01-ladder.md` finding 3, which four patterns have now got
//! wrong by publishing a point instead of its class): `t_1step`, whose window
//! reslice is the one-step `&buf[off..off + len]`, and `t_chain`, whose two fold
//! statements are chained into one expression. ../NOTES.md 8d quotes all three
//! with the input named, and this one is the cheapest of them. **Which spelling
//! ships was decided before any of them was measured** -- this one, because it
//! is the minimum diff from R2, so that R2-vs-R3 isolates the reslice -- and
//! `.memory/02-bench-rules.md`'s "NEVER re-ship a rung because a cheaper
//! in-contract spelling was found" is why that order matters.
//!
//! ⚠ **`t_iter`, whose scan is `w[p..].iter()`, is OUT of contract**: ../spec.md's
//! `idiom` block pins `while p < len` on all four Rust rungs, because that bound
//! is what keeps p18 out of p11's territory. It is measured anyway -- the price
//! of a declaration is what the declaration excludes -- and an earlier draft of
//! this header wrongly called it the second in-contract spelling
//! (../NOTES.md 12).
//!
//! **What is deliberately NOT reached for: `chunks_exact`, `from_le_bytes` and
//! `iter().take_while()`.** ../spec.md forbids all three **in every rung**
//! rather than in some -- a whole-pattern exclusion, which keeps the two sides
//! of the comparison equal, unlike the scoped kind `.memory/01-ladder.md`
//! caught on p13. Each is priced or its prover disposition measured in
//! ../NOTES.md 9 rather than asserted.
//!
//! **The safety line `if shift < VBITS` is carried by all four Rust rungs**, and
//! in Rust at the measured flags it is a SEMANTIC line and not a safety line --
//! see safe_naive.rs's header and ../NOTES.md 7, which is the pattern's sharpest
//! row.

#[path = "../../common/driver.rs"]
mod driver;

const VBITS: u32 = 64;

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    if len < 4 {
        return 0;
    }
    let w: &[u8] = buf.split_at(off).1.split_at(len).0;
    let nv: usize = w[0] as usize + 256 * (w[1] as usize)
        + 65536 * (w[2] as usize) + 16777216 * (w[3] as usize);
    if nv == 0 {
        return 0;
    }
    let mut acc: u64 = 0;
    let mut p: usize = 4;
    let mut v: usize = 0;
    while v < nv {
        if p == len {
            break;
        }
        let mut val: u64 = 0;
        let mut shift: u32 = 0;
        let mut nb: usize = 0;
        while p < len {
            let c: u8 = w[p];
            p = p + 1;
            nb = nb + 1;
            // THE SAFETY LINE. c/kernel.c omits exactly this.
            if shift < VBITS {
                val = val | (((c & 0x7f) as u64) << shift);
            }
            shift = shift.wrapping_add(7);
            if c & 0x80 == 0 {
                break;
            }
        }
        acc = acc.wrapping_mul(31).wrapping_add(val);
        acc = acc.wrapping_mul(31).wrapping_add(nb as u64);
        v = v + 1;
    }
    acc.wrapping_mul(31).wrapping_add(nv as u64)
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
