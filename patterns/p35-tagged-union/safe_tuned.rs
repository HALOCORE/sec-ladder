//! p35 rung R3 -- safe Rust, tuned. Same `enum`, same semantics, **zero
//! `unsafe`**, and the same compile-time impossibility of a tag/payload
//! mismatch that R2 has: the tuning here is about the BOUNDS checks, not about
//! the type discipline, because the type discipline already costs nothing.
//!
//! Two levers, and they are the two `.memory/01-ladder.md` names for R3:
//!
//!   * **reslice the window once** -- `&buf[off .. off + len]` -- so the walk
//!     indexes one object with a length LLVM knows, instead of adding `off` to
//!     a cursor on every access;
//!   * **walk the op stream with `chunks_exact(2)`**, which replaces the
//!     two-byte read and the `len - p < 2` cursor guard with an iterator whose
//!     bound the optimiser can see. `.take(nops)` carries the declared count.
//!
//! ⚠ **What this rung does NOT remove, and it is the whole of the gap to R4:
//! the arena index.** `Cell::Ptr(k)` carries an offset, and no safe spelling
//! tells the compiler `k < BUDGET`, so `arena[k as usize]` keeps its check on
//! every `GET` that dispatches to the pointer arm. R4 removes it with
//! `get_unchecked` and R5 proves the precondition that licenses that.
//! ../NOTES.md 3 has the per-rung numbers.
//!
//! ⚠⚠ **WHICH OF THE TWO LEVERS IS ACTUALLY R4-EXCLUSIVE -- MEASURED ON BOTH
//! SIDES AT TASK_153, BECAUSE THE FIRST TIME ONLY THIS SIDE WAS SEARCHED.**
//! Lever 1, the reslice, is **not** exclusive: `&buf[off..end]` VERIFIES at the
//! pinned vstd (`2 verified, 0 errors`), so R4/R5 could always have taken it --
//! and given to R4 it COSTS `+8.00` Ir/call at `-O3`, which is why it is not
//! the source of this rung's win. Lever 2 is the exclusive one: `chunks_exact`,
//! `ChunksExact` and `Take` are each `is not supported`, and `identity: unsafe
//! == verus` chains R4 to R5. **So the R3-minus-R4 gap prices the `identity`
//! pin and is NOT a safe-versus-unsafe result** -- matched on the op-walk, R4
//! wins by 6.63%. ../NOTES.md 3.
//!
//! ⚠ The equivalence of `chunks_exact(2).take(nops)` to C's
//! `for (i = 0; i < nops; i++) { if (len - p < 2) break; ... }` is exact and
//! not approximate: both stop at `min(nops, (len - 4) / 2)` operations, and the
//! trailing `navail` term is folded the same way in both.

#[path = "../../common/driver.rs"]
mod driver;

/// Tagged cells. Must equal `P35_CELLS` in c/kernel.h and `CELLS` in model.py.
const CELLS: usize = 8;
/// The arena, in bytes. Must equal `P35_BUDGET`.
const BUDGET: usize = 4;
/// What a rejected operation folds. Must equal `P35_SENT`.
const SENT: u64 = 251;

/// THE TAGGED VALUE, identical to R2's. One value, not two.
#[derive(Clone, Copy)]
enum Cell {
    Unset,
    Int(u64),
    Ptr(u32),
    Dbl(f64),
}

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    if len < 4 {
        return 0;
    }
    let w: &[u8] = &buf[off..off + len];
    let nops: usize = w[0] as usize + 256 * (w[1] as usize) + 65536 * (w[2] as usize)
        + 16777216 * (w[3] as usize);
    if nops == 0 {
        return 0;
    }
    let mut cells: [Cell; CELLS] = [Cell::Unset; CELLS];
    let mut arena: [u8; BUDGET] = [0u8; BUDGET];
    for (j, slot) in arena.iter_mut().enumerate() {
        *slot = (j as u8).wrapping_mul(11).wrapping_add(5);
    }
    let mut navail: usize = BUDGET;
    let mut acc: u64 = 0;
    for op in w[4..].chunks_exact(2).take(nops) {
        let c: u8 = op[0];
        let a: u8 = op[1];
        let idx: usize = (a % CELLS as u8) as usize;
        let v: u64 = match c % 4 {
            0 => {
                cells[idx] = Cell::Int((a as u64).wrapping_mul(2654435761));
                a as u64
            }
            1 => {
                if navail > 0 {
                    cells[idx] = Cell::Ptr((BUDGET - navail) as u32);
                    navail = navail - 1;
                    1
                } else {
                    SENT
                }
            }
            2 => {
                if navail > 0 {
                    cells[idx] = Cell::Dbl(if a % 2 == 0 { 0.25 } else { 2.5 });
                    navail = navail - 1;
                    2
                } else {
                    SENT
                }
            }
            _ => match cells[idx] {
                Cell::Int(x) => x & 0xFF,
                Cell::Ptr(k) => arena[k as usize] as u64,
                Cell::Dbl(d) => {
                    if d > 1.0 {
                        1
                    } else {
                        0
                    }
                }
                Cell::Unset => SENT,
            },
        };
        acc = acc.wrapping_mul(31).wrapping_add(v);
    }
    acc.wrapping_mul(31).wrapping_add(navail as u64)
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
