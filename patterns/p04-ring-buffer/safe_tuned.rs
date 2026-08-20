//! p04 rung R3 -- safe-tuned.
//!
//! Same semantics as R2, written the way an experienced Rust programmer writes
//! a record walker: **reslice the window once**, then index the reslice. The
//! reslice is the bounds check; it happens once per call rather than five times
//! per operation, and it is outside the loop by construction rather than by the
//! optimiser's goodwill. Still zero `unsafe`.
//!
//! **And then there is nothing left on the ring side to remove.** The two ring
//! accesses in this file -- `ring[tail]` and `ring[head]` -- compile to the
//! same bytes as `get_unchecked`, because `(x + 1) % RING_CAP` at a
//! power-of-two `RING_CAP` is a mask and LLVM carries known bits around the
//! loop-carried phi. Measured before this rung was written and again after
//! (../NOTES.md 1): this kernel's *only* surviving panic landing pad is the
//! window reslice below, and it is the same one pad whether the ring is
//! indexed or `get_unchecked`ed.
//!
//! | rung | opcode-stream check | ring check |
//! |---|---|---|
//! | R2 | per operation | **0** |
//! | **R3** | one reslice per call | **0** |
//! | R4/R5 | 0 | 0 |
//!
//! ⚠ **THIS IS NOT THE CHEAPEST IN-CONTRACT R3, and the header used to claim it
//! was** (TASK_042_REVIEW blocker 1). Six in-contract spellings across **five
//! distinct machine codes** measure `3367 / 11666` against this rung's
//! `3368 / 11667` -- `+4.00` against R4 where this measures `+5.00`. Two of them
//! ship as controls (`r3_reslice2_get`, `r3_reslice2_split`); the cheapest form
//! is the **two-step reslice**, `buf.get(off..).unwrap().get(..len).unwrap()` or
//! `buf.split_at(off).1.split_at(len).0`.
//!
//! The mechanism is **register allocation, not bounds-check removal**: both
//! forms keep both checks, but `off + len` needs a scratch register while
//! `buf_len - off` is computed in place in `%rsi`, which is dead afterwards
//! (`mov ; add ; jb ; cmp ; ja` against `sub ; jb ; cmp ; ja`). ../NOTES.md 10a
//! has the listings; **`+4.00` is p04's published safety tax** and this rung's
//! `+5.00` is the shipped-rung difference.
//!
//! **This rung is NOT re-shipped on the cheaper spelling, deliberately** --
//! ../NOTES.md 13c states the decision and the project-wide rule it implies. In
//! one line: the shipped rung is chosen by *idiom*, before measurement, and
//! `&buf[off..off + len]` is what an experienced Rust programmer writes; the
//! search bounds the class and is published as a span with the cheapest
//! endpoint named. The `idiom` block pins no reslice spelling at all, so every
//! one of the six is in contract by construction.
//!
//! (`.memory/01-ladder.md` finding 3 requires at least two in-contract R3
//! spellings with the cheaper quoted. There are now six; the dearest is
//! `w[4..4 + 5 * nops].chunks_exact(5)` at `+239 / +832`. None of them touches
//! the ring, because there is nothing there to touch.)
//!
//! **What is NOT here, and why**: `ring[tail & (RING_CAP - 1)]` is
//! `idiom.forbidden` -- and ../NOTES.md 10a measures that forbidding it removes
//! **no machine code from the admissible class**, because at `RING_CAP = 64`
//! the masked spelling is byte-identical to the `%` one. It is forbidden for a
//! semantic reason (`%` is the operator this pattern exists to ask about, and a
//! mask answers a different question), not to protect a number. A `VecDeque`,
//! or a `Vec` with `push_back`/`pop_front`, would delete the two explicit
//! cursors that the result folds and that the proof's invariant is about.

#[path = "../../common/driver.rs"]
mod driver;

const RING_CAP: usize = 64;

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    if len < 4 {
        return 0;
    }
    let w: &[u8] = &buf[off..off + len];
    let nops: usize = w[0] as usize + 256 * (w[1] as usize)
        + 65536 * (w[2] as usize) + 16777216 * (w[3] as usize);
    if nops == 0 {
        return 0;
    }
    if 5 * (nops as u64) > (len - 4) as u64 {
        return 0;
    }
    let mut ring: [u64; RING_CAP] = [0; RING_CAP];
    let mut acc: u64 = 0;
    let mut head: usize = 0;
    let mut tail: usize = 0;
    let mut k: usize = 0;
    while k < nops {
        let op: u8 = w[4 + 5 * k];
        let val: u64 = w[5 + 5 * k] as u64 + 256 * (w[6 + 5 * k] as u64)
            + 65536 * (w[7 + 5 * k] as u64)
            + 16777216 * (w[8 + 5 * k] as u64);
        if op == 0 {
            if (tail + 1) % RING_CAP != head {
                ring[tail] = val;
                tail = (tail + 1) % RING_CAP;
            }
        } else {
            if head != tail {
                acc = acc.wrapping_mul(31).wrapping_add(ring[head]);
                head = (head + 1) % RING_CAP;
            }
        }
        k = k + 1;
    }
    acc.wrapping_mul(31).wrapping_add(head as u64).wrapping_mul(31)
        .wrapping_add(tail as u64).wrapping_mul(31).wrapping_add(nops as u64)
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
