//! p03 rung R2 -- safe-naive.
//!
//! The mechanical port a working Rust programmer writes first: index `buf[..]`
//! for the header and for all five bytes of every operation, with the
//! window-relative index spelled `off + 4 + 5 * k` exactly as the C spells it,
//! and index `stack[sp]` for the push and the pop. Zero `unsafe`.
//!
//! **Two DIFFERENT bounds checks live in this rung and they behave differently,
//! which is p03's result.** The opcode-stream reads are checked against
//! `buf.len()`, which the optimiser has to re-derive per operation because
//! nothing has handed it the window; R3 fixes exactly that with one reslice.
//! The *stack* reads are checked against the array's fixed length 64, and there
//! the optimiser's success depends on where the guard sits:
//!
//! * the PUSH's `stack[sp]` sits inside `if sp < STACK_CAP`, in the same basic
//!   block, so LLVM deletes its check outright -- **0.00000 Ir**, and R3's push
//!   path is instruction-identical to R4's;
//! * the POP's `stack[sp]` needs `sp <= STACK_CAP` to have survived the
//!   attacker-chosen `if op == 0` branch and the loop back-edge, and LLVM does
//!   not carry it -- **3.00000 Ir per executed pop**.
//!
//! One array, one constant bound, one kernel, two answers. NOTES.md 4.
//!
//! `stack` is `[0u64; STACK_CAP]` because safe Rust has no uninitialised array;
//! C's `uint64_t stack[64];` is not initialised. That is a per-call constant,
//! it is not a bounds check, and NOTES.md 3c prices it separately rather than
//! letting it hide inside a safety number.

#[path = "../../common/driver.rs"]
mod driver;

const STACK_CAP: usize = 64;

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md. `#[inline(never)]` only in `isolated` builds, so the
// `whole` builds can inline it the way LTO'd C would.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    if len < 4 {
        return 0;
    }
    let nops: usize = buf[off] as usize + 256 * (buf[off + 1] as usize)
        + 65536 * (buf[off + 2] as usize) + 16777216 * (buf[off + 3] as usize);
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
        let op: u8 = buf[off + 4 + 5 * k];
        let val: u64 = buf[off + 5 + 5 * k] as u64 + 256 * (buf[off + 6 + 5 * k] as u64)
            + 65536 * (buf[off + 7 + 5 * k] as u64)
            + 16777216 * (buf[off + 8 + 5 * k] as u64);
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
