//! p03 rung R3 -- safe-tuned.
//!
//! Same semantics as R2, written the way an experienced Rust programmer writes
//! a record walker: **reslice the window once**, then index the reslice. The
//! reslice is the bounds check; it happens once per call rather than five times
//! per operation, and it is outside the loop by construction rather than by the
//! optimiser's goodwill. Still zero `unsafe`.
//!
//! **That one line removes 100% of the opcode-stream tax and 0% of the stack
//! tax**, and the split is what p03 is for. Measured on the disassembly
//! (NOTES.md 4): with the reslice, this rung's loop body is
//! instruction-identical to R4's on the PUSH path and differs from it on the
//! POP path by exactly `lea; cmp; ja`. So
//!
//! | rung | opcode-stream check | stack check |
//! |---|---|---|
//! | R2 | 11.00000 Ir/op | 3.00000 Ir/executed pop |
//! | **R3** | **0** | **3.00000 Ir/executed pop** |
//! | R4/R5 | 0 | 0 |
//!
//! **There are two in-contract R3 spellings and this is the cheaper**
//! (`.memory/01-ladder.md` finding 3 requires at least two, with the cheaper
//! quoted). The other is `w[4..4 + 5 * nops].chunks_exact(5)`, built as a
//! control in NOTES.md 10a; it is +100.00 Ir/call dearer on both blobs because
//! `chunks_exact` re-derives the record base per step where the explicit
//! `5 * k` cursor folds into the addressing mode. Neither spelling touches the
//! stack check, which is the number this pattern publishes.
//!
//! **What is NOT here, and why**: `stack[sp & (STACK_CAP - 1)]` would delete the
//! surviving check for `1.00000` of its `3.00000` Ir (NOTES.md 4d) and is
//! `idiom.forbidden`, because masking an index is not the same program -- it
//! silently turns an out-of-range access into an in-range one, which is the
//! *opposite* of what this pattern is about. A `VecDeque`, a `Vec` with
//! `push`/`pop`, or `stack.last()` would each delete the explicit `sp` that the
//! result folds and that the proof's invariant is about.

#[path = "../../common/driver.rs"]
mod driver;

const STACK_CAP: usize = 64;

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
    let mut stack: [u64; STACK_CAP] = [0; STACK_CAP];
    let mut acc: u64 = 0;
    let mut sp: usize = 0;
    let mut k: usize = 0;
    while k < nops {
        let op: u8 = w[4 + 5 * k];
        let val: u64 = w[5 + 5 * k] as u64 + 256 * (w[6 + 5 * k] as u64)
            + 65536 * (w[7 + 5 * k] as u64)
            + 16777216 * (w[8 + 5 * k] as u64);
        if op == 0 {
            if sp < STACK_CAP {
                stack[sp] = val;
                sp = sp + 1;
            }
        } else {
            if sp > 0 {
                sp = sp - 1;
                acc = acc.wrapping_mul(31).wrapping_add(stack[sp]);
            }
        }
        k = k + 1;
    }
    acc.wrapping_mul(31).wrapping_add(sp as u64).wrapping_mul(31).wrapping_add(nops as u64)
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
