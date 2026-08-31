//! p35 CONTROL ARM: **can SAFE Rust reproduce `c/kernel.c`'s bug?** Not a
//! rung -- a control. Driven by `controls/rust_bug.py`.
//!
//! ⚠⚠ **THE ANSWER HAS TWO HALVES AND ONLY ONE OF THEM IS "NO".**
//!
//! The shipped safe rungs (`safe_naive.rs`, `safe_tuned.rs`) hold a `Cell`
//! ENUM, and there the mismatch is **unrepresentable**: the discriminant and
//! the payload are one value written by one assignment, so no safe program --
//! and no unsafe one either -- can publish `Cell::Ptr` over an integer
//! payload. That is `p08`'s shape, a COMPILE-TIME boundary, and it is the
//! row's safe-Rust result.
//!
//! **But safe Rust has a second spelling of a tagged union**, and this file is
//! it: a tag array beside a `u64` payload array, with the reinterpretation done
//! by `f64::from_bits` -- which is SAFE, TOTAL and defined for every bit
//! pattern. Written in the buggy order, this program **reproduces C's silent
//! wrong value bit for bit**, under `#![forbid(unsafe_code)]`, with no
//! detector anywhere.
//!
//! ⚠ **What it does NOT reproduce is the LOUD harm.** `pays[k] as usize` used
//! as an arena index is bounds-checked, so the PTR arm PANICS -- `index out of
//! bounds` -- where C dereferences an attacker-derived pointer. So safe Rust
//! turns the loud harm into a controlled abort and leaves the silent one
//! exactly as it is.
//!
//! **That is why `from_bits` and `to_bits` are in `../spec.md`'s `forbidden`
//! list**: they are safe Rust's TOTAL reinterpretation, and a rung spelling
//! them would delete the correct-variant obligation altogether -- the pattern
//! with it -- while looking like the same algorithm. This control is where that
//! spelling is measured instead of shipped.

#![forbid(unsafe_code)]

#[path = "../../../common/driver.rs"]
mod driver;

const CELLS: usize = 8;
const BUDGET: usize = 4;
const SENT: u64 = 251;
const T_UNSET: u8 = 0;
const T_INT: u8 = 1;
const T_PTR: u8 = 2;
const T_DBL: u8 = 3;

pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    if len < 4 {
        return 0;
    }
    let nops: usize = buf[off] as usize
        + 256 * (buf[off + 1] as usize)
        + 65536 * (buf[off + 2] as usize)
        + 16777216 * (buf[off + 3] as usize);
    if nops == 0 {
        return 0;
    }
    // The tag and the payload as TWO objects, which is what makes the bug
    // expressible at all. The payload is the raw eight bytes, exactly as the
    // C union stores them.
    let mut tags: [u8; CELLS] = [T_UNSET; CELLS];
    let mut pays: [u64; CELLS] = [0u64; CELLS];
    let mut arena: [u8; BUDGET] = [0u8; BUDGET];
    for (j, slot) in arena.iter_mut().enumerate() {
        *slot = (j as u8).wrapping_mul(11).wrapping_add(5);
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
        let v: u64 = if c % 4 == 0 {
            pays[idx] = (a as u64).wrapping_mul(2654435761);
            tags[idx] = T_INT;
            a as u64
        } else if c % 4 == 1 {
            // THE SAFETY LINE, REMOVED. c/kernel.c's ordering exactly.
            tags[idx] = T_PTR;
            if navail > 0 {
                pays[idx] = (BUDGET - navail) as u64;
                navail = navail - 1;
                1
            } else {
                SENT
            }
        } else if c % 4 == 2 {
            // THE SAFETY LINE, REMOVED.
            tags[idx] = T_DBL;
            if navail > 0 {
                pays[idx] = (if a % 2 == 0 { 0.25f64 } else { 2.5f64 }).to_bits();
                navail = navail - 1;
                2
            } else {
                SENT
            }
        } else {
            let t: u8 = tags[idx];
            if t == T_INT {
                pays[idx] & 0xFF
            } else if t == T_PTR {
                // BOUNDS-CHECKED. This is where safe Rust turns C's wild
                // dereference into a panic.
                arena[pays[idx] as usize] as u64
            } else if t == T_DBL {
                // SAFE, TOTAL, and DEFINED for every bit pattern -- so this
                // reproduces C's silent wrong value exactly.
                if f64::from_bits(pays[idx]) > 1.0 {
                    1
                } else {
                    0
                }
            } else {
                SENT
            }
        };
        acc = acc.wrapping_mul(31).wrapping_add(v);
        o = o + 1;
    }
    acc.wrapping_mul(31).wrapping_add(navail as u64)
}

fn main() {
    let path = driver::arg_path();
    let inp = driver::load(&path);
    let (stride_w, bytes) = driver::head1_u64_bytes(&inp);
    let n_iters: u64 = inp.n_iters;
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
    driver::emit(acc);
}
