//! p35 CONTROL ARM: **`c/kernel.c`'s bug, written in UNSAFE RUST with a real
//! `union`.** Not a rung -- a control. Driven by `controls/rust_bug.py`.
//!
//! This is `unsafe.rs`'s kernel with the SAFETY LINE removed: the tag store
//! moves out of the `navail > 0` test, exactly as in `c/kernel.c`. The question
//! it answers is the one `.memory/01-ladder.md` asks of every row -- *can the
//! unsafe rung reproduce the C bug, and does any Rust-side instrument see it?*
//!
//! **The answers, measured by `controls/rust_bug.py`:**
//!
//!   * the DBL arm reproduces C's silent wrong value **bit for bit** -- the
//!     union punning is the same reinterpretation of the same eight bytes --
//!     and **Miri says nothing**, because reading a union member other than
//!     the one last stored is NOT undefined behaviour in Rust when the bytes
//!     are a valid value of the field's type, and every bit pattern is a valid
//!     `u32`, `u64` and `f64`;
//!   * the PTR arm does NOT reproduce C's harm, and that is the OFFSET
//!     substitution showing up as a measurement rather than as prose: the union
//!     yields a `u32` offset instead of a pointer, so what follows is an
//!     out-of-bounds `get_unchecked` into a 4-byte arena rather than the
//!     dereference of an attacker-derived pointer. **Miri DOES see that one.**
//!
//! ⚠ So the substitution documented in `../spec.md` does not merely make the
//! Rust side quieter: it changes which instrument fires. `../NOTES.md` 5.

#[path = "../../../common/driver.rs"]
mod driver;

const CELLS: usize = 8;
const BUDGET: usize = 4;
const SENT: u64 = 251;
const T_UNSET: u8 = 0;
const T_INT: u8 = 1;
const T_PTR: u8 = 2;
const T_DBL: u8 = 3;

union Pay {
    i: u64,
    d: f64,
    o: u32,
}

#[inline(always)]
fn bg(v: &[u8], i: usize) -> u8 {
    unsafe { *v.get_unchecked(i) }
}

pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    if len < 4 {
        return 0;
    }
    let nops: usize = bg(buf, off) as usize
        + 256 * (bg(buf, off + 1) as usize)
        + 65536 * (bg(buf, off + 2) as usize)
        + 16777216 * (bg(buf, off + 3) as usize);
    if nops == 0 {
        return 0;
    }
    let mut tags: [u8; CELLS] = [T_UNSET; CELLS];
    let mut pays: [Pay; CELLS] = [
        Pay { i: 0 },
        Pay { i: 0 },
        Pay { i: 0 },
        Pay { i: 0 },
        Pay { i: 0 },
        Pay { i: 0 },
        Pay { i: 0 },
        Pay { i: 0 },
    ];
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
        let c: u8 = bg(buf, off + p);
        let a: u8 = bg(buf, off + p + 1);
        p = p + 2;
        let idx: usize = (a % CELLS as u8) as usize;
        let v: u64 = if c % 4 == 0 {
            pays[idx] = Pay { i: (a as u64).wrapping_mul(2654435761) };
            tags[idx] = T_INT;
            a as u64
        } else if c % 4 == 1 {
            // THE SAFETY LINE, REMOVED. c/kernel.c's ordering exactly.
            tags[idx] = T_PTR;
            if navail > 0 {
                pays[idx] = Pay { o: (BUDGET - navail) as u32 };
                navail = navail - 1;
                1
            } else {
                SENT
            }
        } else if c % 4 == 2 {
            // THE SAFETY LINE, REMOVED.
            tags[idx] = T_DBL;
            if navail > 0 {
                pays[idx] = if a % 2 == 0 { Pay { d: 0.25 } } else { Pay { d: 2.5 } };
                navail = navail - 1;
                2
            } else {
                SENT
            }
        } else {
            let t: u8 = tags[idx];
            if t == T_INT {
                unsafe { pays[idx].i & 0xFF }
            } else if t == T_PTR {
                // ⚠ The union may be in the `i` variant here, in which case
                // this reads the low 32 bits of an integer as an offset and
                // indexes a 4-byte array with it. THAT is undefined behaviour
                // in Rust and Miri reports it -- unlike the union read itself.
                let k: u32 = unsafe { pays[idx].o };
                unsafe { *arena.get_unchecked(k as usize) as u64 }
            } else if t == T_DBL {
                // ⚠ This one is DEFINED Rust even when the variant is wrong:
                // every bit pattern is a valid `f64`. Miri is silent and the
                // value is simply the reinterpretation C also computes.
                if unsafe { pays[idx].d } > 1.0 {
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
