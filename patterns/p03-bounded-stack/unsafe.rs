//! p03 rung R4 -- unsafe.
//!
//! R2's algorithm with every bounds check removed: the four header bytes, the
//! five bytes of every operation, the push's write and the pop's read all go
//! through `get_unchecked` / `get_unchecked_mut`. **What does NOT go away are
//! the two guards** -- `sp < STACK_CAP` and `sp > 0`. Those are not bounds
//! checks, they are the kernel's semantics; a rung without the second one would
//! be R1's bug written in Rust rather than an unsafe rung. This rung is
//! correct; it just has nothing checking that it is. R5 (verus.rs) is this exec
//! code with the SAFETY comments below turned into obligations a verifier
//! discharges.
//!
//! SAFETY (1): `off + len <= buf.len()` is the caller's structural
//!   precondition. Unchecked here; discharged at the call site by Verus in
//!   verus.rs.
//! SAFETY (2): `len >= 4` guards the header, so `off + 3 < off + len <=
//!   buf.len()`.
//! SAFETY (3): the operation reads are at `off + 4 + 5*k .. off + 8 + 5*k`
//!   under `k < nops` and `5*nops <= len - 4`, so the last byte read is at
//!   `off + 4 + 5*(nops-1) + 4 = off + 5*nops - 1 + 4 <= off + len - 1`.
//! SAFETY (4): the push writes `stack[sp]` only under `sp < STACK_CAP`.
//! SAFETY (5): the pop reads `stack[sp]` after `sp -= 1` under `sp > 0`, and
//!   `sp <= STACK_CAP` holds on entry to every iteration -- `sp` starts at 0
//!   and is only incremented under `sp < STACK_CAP`.
//!
//! **SAFETY (5) is the whole pattern, and it is the first obligation in this
//! project that is a loop invariant over a branch the ATTACKER picks.** p05's
//! index is nonlinear but computable before the loop; p07's is
//! `off + 8 + 4*mid`; p11's scan has no closed form but the *sequence of
//! operations* is still fixed by the code. Here the file decides, per step,
//! which of two updates `sp` gets, so `sp <= STACK_CAP` has to survive a
//! two-armed branch and the back edge. Z3 discharges it in one clause
//! (`verus.rs`'s `sp <= STACK_CAP` invariant, no lemma, no `nonlinear_arith`).
//! **LLVM does not**, and that is a measured 3.00000 Ir per executed pop in
//! both safe rungs -- NOTES.md 4 has the law, the mechanism and the
//! `-unroll-count`-style isolating control.
//!
//! The asymmetry is what makes it a mechanism rather than an anecdote: the
//! PUSH's index is guarded in the *same basic block* by `sp < STACK_CAP`, so
//! LLVM deletes that check and the safe rungs' push path is
//! instruction-identical to this one's. Same array, same constant bound, same
//! function, two answers.
//!
//! `stack` is `[0u64; STACK_CAP]` here too, not a `MaybeUninit`. Matching C's
//! uninitialised array would need a fourth trusted item and would move a
//! per-call constant that is not a bounds check; NOTES.md 3c prices the
//! initialisation instead, so the C-vs-Rust constant is named and not hidden.

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
    let nops: usize = unsafe { *buf.get_unchecked(off) } as usize
        + 256 * (unsafe { *buf.get_unchecked(off + 1) } as usize)
        + 65536 * (unsafe { *buf.get_unchecked(off + 2) } as usize)
        + 16777216 * (unsafe { *buf.get_unchecked(off + 3) } as usize);
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
        let op: u8 = unsafe { *buf.get_unchecked(off + 4 + 5 * k) };
        let val: u64 = unsafe { *buf.get_unchecked(off + 5 + 5 * k) } as u64
            + 256 * (unsafe { *buf.get_unchecked(off + 6 + 5 * k) } as u64)
            + 65536 * (unsafe { *buf.get_unchecked(off + 7 + 5 * k) } as u64)
            + 16777216 * (unsafe { *buf.get_unchecked(off + 8 + 5 * k) } as u64);
        if op == 0 {
            if sp < STACK_CAP {
                unsafe { *stack.get_unchecked_mut(sp) = val; }
                sp = sp + 1;
            }
        } else {
            if sp > 0 {
                sp = sp - 1;
                acc = acc.wrapping_mul(31)
                    .wrapping_add(unsafe { *stack.get_unchecked(sp) });
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
