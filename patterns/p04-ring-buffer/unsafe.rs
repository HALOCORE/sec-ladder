//! p04 rung R4 -- unsafe.
//!
//! R2's algorithm with every bounds check removed: the four header bytes, the
//! five bytes of every operation, the enqueue's write and the dequeue's read
//! all go through `get_unchecked` / `get_unchecked_mut`. **What does NOT go
//! away are the two guards** -- `(tail + 1) % RING_CAP != head` and
//! `head != tail`. Those are not bounds checks, they are the kernel's
//! semantics; a rung without the first would be R1's bug written in Rust rather
//! than an unsafe rung. This rung is correct; it just has nothing checking that
//! it is. R5 (verus.rs) is this exec code with the SAFETY comments below turned
//! into obligations a verifier discharges.
//!
//! SAFETY (1): `off + len <= buf.len()` is the caller's structural
//!   precondition. Unchecked here; discharged at the call site by Verus in
//!   verus.rs.
//! SAFETY (2): `len >= 4` guards the header, so `off + 3 < off + len <=
//!   buf.len()`.
//! SAFETY (3): the operation reads are at `off + 4 + 5*k .. off + 8 + 5*k`
//!   under `k < nops` and `5*nops <= len - 4`, so the last byte read is at
//!   `off + 4 + 5*(nops-1) + 4 = off + 5*nops - 1 + 4 <= off + len - 1`.
//! SAFETY (4): `tail < RING_CAP` and `head < RING_CAP` on entry to every
//!   iteration. Both start at 0 and every update is `(x + 1) % RING_CAP`, whose
//!   value is in `[0, RING_CAP)` for *every* input `x`.
//!
//! **SAFETY (4) is the whole pattern, and note what it is NOT: it is not
//! relational.** p03's obligation is `sp <= STACK_CAP`, maintained across an
//! attacker-chosen branch, and the guard that maintains it is the same guard
//! the program needs to be correct. Here the two facts are independent
//! one-variable facts, each discharged by its own `%`, and **neither guard
//! participates**. Delete the fullness check and both facts still hold; delete
//! the emptiness check and both still hold. That is exactly why R1's bug is
//! invisible to every memory-safety mechanism this project has
//! (../NOTES.md 6), and it is the same sentence as "the ring buffer cannot
//! overflow its indices".
//!
//! The consequence for cost is the other half: because the fact is carried by a
//! *mask*, LLVM has it too. `safe_tuned.rs`'s `ring[tail]` and this file's
//! `get_unchecked_mut(tail)` compile to the **same bytes** (../NOTES.md 1), so
//! `get_unchecked` on the ring buys exactly nothing here and the only thing
//! this rung's `unsafe` actually removes is the opcode-stream check R3 already
//! removed with a reslice.
//!
//! `ring` is `[0u64; RING_CAP]` here too, not a `MaybeUninit`. Matching C's
//! uninitialised array would need a fourth trusted item and would move a
//! per-call constant that is not a bounds check; ../NOTES.md 3c prices the
//! initialisation instead, so the C-vs-Rust constant is named and not hidden.

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
    let mut ring: [u64; RING_CAP] = [0; RING_CAP];
    let mut acc: u64 = 0;
    let mut head: usize = 0;
    let mut tail: usize = 0;
    let mut k: usize = 0;
    while k < nops {
        let op: u8 = unsafe { *buf.get_unchecked(off + 4 + 5 * k) };
        let val: u64 = unsafe { *buf.get_unchecked(off + 5 + 5 * k) } as u64
            + 256 * (unsafe { *buf.get_unchecked(off + 6 + 5 * k) } as u64)
            + 65536 * (unsafe { *buf.get_unchecked(off + 7 + 5 * k) } as u64)
            + 16777216 * (unsafe { *buf.get_unchecked(off + 8 + 5 * k) } as u64);
        if op == 0 {
            if (tail + 1) % RING_CAP != head {
                unsafe { *ring.get_unchecked_mut(tail) = val; }
                tail = (tail + 1) % RING_CAP;
            }
        } else {
            if head != tail {
                acc = acc.wrapping_mul(31)
                    .wrapping_add(unsafe { *ring.get_unchecked(head) });
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
