//! p35 rung R2 -- safe Rust, the mechanical port. **And the mismatch this
//! pattern is about is UNREPRESENTABLE here, which is the row's R2 result.**
//!
//! C's cell is a TAG plus a UNION, and the two are separate objects that a
//! program is trusted to keep in step. Rust's answer is an `enum`: the
//! discriminant and the payload are ONE value, written by ONE assignment, and
//! there is no program -- safe or not -- that can publish `Cell::Ptr` while the
//! storage holds the integer a previous `Cell::Int` put there.
//!
//! ⚠ **So this rung has NO SAFETY LINE, and that is not an omission.**
//! `c/kernel_hardened.c` needs a statement ordering because the tag store and
//! the payload store are two statements; here they are one, so the ordering
//! constraint has no site to be violated at. The boundary is COMPILE TIME --
//! p08's shape -- and ../NOTES.md 3 measures what it costs.
//!
//! What this rung does NOT get for free: the arena read. `Cell::Ptr(o)` carries
//! an offset, and safe Rust bounds-checks `arena[o as usize]` on every `GET`
//! that dispatches to it, because nothing in the type system knows that a `u32`
//! stored by this kernel is below `BUDGET`. That check is one of the two levers
//! R3 and R4 move; the other is the window read.

#[path = "../../common/driver.rs"]
mod driver;

/// Tagged cells. Must equal `P35_CELLS` in c/kernel.h and `CELLS` in model.py.
const CELLS: usize = 8;
/// The arena, in bytes: how many pointer/double payloads can be issued before
/// the store starts failing. Must equal `P35_BUDGET`.
const BUDGET: usize = 4;
/// What a rejected operation folds. Must equal `P35_SENT`.
const SENT: u64 = 251;

/// THE TAGGED VALUE. One value, not two -- see the module note.
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
    let nops: usize = buf[off] as usize + 256 * (buf[off + 1] as usize)
        + 65536 * (buf[off + 2] as usize)
        + 16777216 * (buf[off + 3] as usize);
    if nops == 0 {
        return 0;
    }
    let mut cells: [Cell; CELLS] = [Cell::Unset; CELLS];
    let mut arena: [u8; BUDGET] = [0u8; BUDGET];
    let mut j: usize = 0;
    while j < BUDGET {
        arena[j] = (j as u8).wrapping_mul(11).wrapping_add(5);
        j = j + 1;
    }
    let mut navail: usize = BUDGET;
    let mut acc: u64 = 0;
    let mut p: usize = 4;
    let mut o: usize = 0;
    while o < nops {
        if len - p < 2 {
            break;
        }
        let c: u8 = buf[off + p];
        let a: u8 = buf[off + p + 1];
        p = p + 2;
        let idx: usize = (a % CELLS as u8) as usize;
        if c % 4 == 0 {
            cells[idx] = Cell::Int((a as u64).wrapping_mul(2654435761));
            acc = acc.wrapping_mul(31).wrapping_add(a as u64);
        } else if c % 4 == 1 {
            if navail > 0 {
                cells[idx] = Cell::Ptr((BUDGET - navail) as u32);
                navail = navail - 1;
                acc = acc.wrapping_mul(31).wrapping_add(1);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else if c % 4 == 2 {
            if navail > 0 {
                cells[idx] = Cell::Dbl(if a % 2 == 0 { 0.25 } else { 2.5 });
                navail = navail - 1;
                acc = acc.wrapping_mul(31).wrapping_add(2);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else {
            let v: u64 = match cells[idx] {
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
            };
            acc = acc.wrapping_mul(31).wrapping_add(v);
        }
        o = o + 1;
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
