//! p04 rung R2 -- safe-naive.
//!
//! The mechanical port a working Rust programmer writes first: index `buf[..]`
//! for the header and for all five bytes of every operation, with the
//! window-relative index spelled `off + 4 + 5 * k` exactly as the C spells it,
//! and index `ring[tail]` / `ring[head]` for the enqueue and the dequeue. Zero
//! `unsafe`.
//!
//! **Two DIFFERENT bounds checks live in this rung and only one of them costs
//! anything, which is p04's result.** The opcode-stream reads are checked
//! against `buf.len()`, which the optimiser has to re-derive per operation
//! because nothing has handed it the window; R3 fixes exactly that with one
//! reslice. The *ring* accesses are checked against the array's fixed length
//! 64 -- and **both of those checks are deleted outright**, because
//!
//! ```text
//!     tail = (tail + 1) % RING_CAP;      lowers to     inc ; and $0x3f
//! ```
//!
//! and a mask fixes the high bits, so LLVM's known-bits analysis carries
//! `tail < 64` around the loop-carried phi with no help. p05 asked the same
//! question of a *multiply* and p09 of a *shift*; on `%` at a power of two the
//! answer is that the bound survives, and this rung has **zero panic landing
//! pads for `ring`** to prove it (../NOTES.md 1).
//!
//! It is not a property of `%`. `controls/gen_controls.py` ships the identical
//! source at `RING_CAP = 60` and **both ring checks come back** -- 12 static
//! instructions and 3 landing pads instead of 1 (../NOTES.md 1a). One edit, and
//! it is the largest single effect in this pattern.
//!
//! ⚠ **This comment used to explain that as "at 60 the fact is a RANGE rather
//! than known bits", and that is FALSE** (TASK_042_REVIEW MAJOR 3). `% 60`
//! supplies known bits too -- `computeKnownBits(urem x, 60)` zeroes the high 58,
//! i.e. `x % 60 < 64` -- and that fact *does* survive the loop-carried phi:
//! `% 60` into a `[u64; 64]` array elides the check. The measured rule is
//! quantitative and has zero fitted parameters:
//!
//!     urem x, C  supplies  x < next_pow2(C), and the ring check is elided when
//!     next_pow2(CAP) <= ARR_LEN  -- necessarily, and sufficiently absent a
//!     guard relating the two cursors.
//!
//! `next_pow2(64) = 64 <= 64`; `next_pow2(60) = 64 > 60`. That is the whole of
//! the 60-vs-64 gap, and ../NOTES.md 1e is the 48-kernel separation that
//! establishes it -- including the row that carries the headline: spelling the
//! wrap as a source-level *branch* brings both checks back **at 64 as well**, at
//! the identical provable range, so the range is never what carries.
//!
//! `ring` is `[0u64; RING_CAP]` because safe Rust has no uninitialised array;
//! C's `uint64_t ring[64];` is not initialised. That is a per-call constant, it
//! is not a bounds check, and ../NOTES.md 3c prices it separately rather than
//! letting it hide inside a safety number.

#[path = "../../common/driver.rs"]
mod driver;

const RING_CAP: usize = 64;

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
    let mut ring: [u64; RING_CAP] = [0; RING_CAP];
    let mut acc: u64 = 0;
    let mut head: usize = 0;
    let mut tail: usize = 0;
    let mut k: usize = 0;
    while k < nops {
        let op: u8 = buf[off + 4 + 5 * k];
        let val: u64 = buf[off + 5 + 5 * k] as u64 + 256 * (buf[off + 6 + 5 * k] as u64)
            + 65536 * (buf[off + 7 + 5 * k] as u64)
            + 16777216 * (buf[off + 8 + 5 * k] as u64);
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
