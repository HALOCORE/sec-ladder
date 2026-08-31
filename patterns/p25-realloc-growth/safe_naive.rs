//! p25 rung R2 -- safe Rust, naive.
//!
//! ⚠⚠ **THE SAVED REFERENCE IS AN INDEX, AND THAT IS NOT A CHOICE THIS FILE
//! MAKES -- IT IS THE ONLY THING SAFE RUST OFFERS.** `&toks[curi]` cannot be
//! held across `toks.push(..)`; the borrow checker refuses it. So the safe port
//! saves `curi`, and:
//!
//!   1. **the bug is not merely prevented, it is ABSENT.** `realloc` COPIES, so
//!      `toks[curi]` names the same element before and after a growth. There is
//!      nothing here for the safety line to guard, and this rung is
//!      *character-for-character* what `c/kernel_hardened.c`'s `else` branch
//!      does. **The safe port IS the hardened rung**, arrived at by
//!      construction.
//!   2. ⚠ **`E0502` IS NOT THE EVIDENCE FOR THAT AND MUST NOT BE QUOTED AS IF IT
//!      WERE.** `../controls/safe_arms.py` compiles the `&T`-across-`push`
//!      spelling and gets `E0502` -- and it also compiles a NEGATIVE CONTROL
//!      that cannot have p25's bug (a `struct S { v: u32 }` with no container,
//!      no growth and no saved reference) and gets the **same code and the same
//!      message**. The error code carries no information about interior pointers.
//!      **The fourth time this project has read a rustc code as distinguishing
//!      when it was not** -- p25's own `E0502` (catalogue), p28's `E0382`/`E0499`
//!      and p34's `E0507`.
//!
//! **There is no capacity variable in this rung and there does not need to be.**
//! The C rungs write `tcap` because `realloc` needs a size; `Vec::push` owns the
//! same doubling policy internally. `MAXCAP` is `SEED * 2**k`, so the C guard
//! `ntok < MAXCAP` with growth at `ntok == tcap` accepts exactly the pushes
//! `toks.len() < MAXCAP` accepts -- ../spec.md pins the equivalence and
//! ../NOTES.md 5 measures what the *number of `realloc` calls* differs by, which
//! is the one place the two growth policies are not the same program.
//!
//! Naive in the two places R3 tunes: the op walk is a cursor and an `if` chain,
//! so every op byte costs its own bounds check, and the opcode is a chain of
//! `if`s rather than a `match`. Every index is a plain `buf[off + p]` and a plain
//! `toks[curi]`, so rustc emits its own bounds check on top of the guard the
//! algorithm already has; ../NOTES.md 5 is what that costs.
//!
//! Wrapping arithmetic is spelled `wrapping_mul` / `wrapping_add` because
//! `-C debug-assertions=on` would otherwise panic on the fold, and the C rungs
//! wrap by definition (C99 6.2.5p9).

#[path = "../../common/driver.rs"]
mod driver;

const MAXCAP: usize = 64;
const SENT: u64 = 251;

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    if len < 4 {
        return 0;
    }
    let nops: usize = buf[off] as usize + 256 * (buf[off + 1] as usize) + 65536 * (buf[off + 2]
        as usize) + 16777216 * (buf[off + 3] as usize);
    if nops == 0 {
        return 0;
    }
    // THE TWO GROWABLE VECTORS. `Vec<u8>` is the same allocator C's `realloc`
    // uses, and `push` past the capacity is the same doubling growth.
    let mut toks: Vec<u8> = Vec::new();
    let mut strs: Vec<u8> = Vec::new();
    // THE SAVED REFERENCE, and it is an INDEX. See the header.
    let mut curi: usize = 0;
    let mut have: bool = false;
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
        if c % 4 == 0 {
            if toks.len() < MAXCAP {
                toks.push(a);
                acc = acc.wrapping_mul(31).wrapping_add(a as u64);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else if c % 4 == 1 {
            if strs.len() < MAXCAP {
                strs.push(a);
                acc = acc.wrapping_mul(31).wrapping_add(a as u64);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else if c % 4 == 2 {
            if toks.len() > 0 {
                curi = (a as usize) % toks.len();
                have = true;
                acc = acc.wrapping_mul(31).wrapping_add(2);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else {
            if have {
                let v: u8 = toks[curi];
                acc = acc.wrapping_mul(31).wrapping_add(v as u64);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        }
        o = o + 1;
    }
    // No epilogue: dropping `toks` and `strs` frees both blocks, which is the
    // `free(toks); free(strs);` the C rungs write by hand.
    acc.wrapping_mul(31).wrapping_add((toks.len() + strs.len()) as u64)
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
