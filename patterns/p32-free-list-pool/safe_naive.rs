//! p32 rung R2 -- safe Rust, naive.
//!
//! ⚠⚠ **THE REPRESENTATION IS NOT A CHOICE AND IT IS NOT A TRANSLATION EITHER:
//! IT IS C'S, EXACTLY.** `p27` and `p29` both get one half of their safety line
//! written by the language, because their records are `Option<Box<Rec>>` and
//! `tab[i] = None` frees the record and invalidates the slot in one operation.
//! **`p32` gets nothing.** The pool is a `[u8; SLOTS * BLK]` the kernel owns for
//! the whole call; no block is ever allocated, no block is ever dropped, and
//! `Option`, `Box`, borrowck, drop glue and Miri all have exactly nothing to
//! attach to. Three consequences, and they are this row's headline:
//!
//!   1. **Both conjuncts have to be written out by hand, in safe Rust exactly as
//!      in C** -- `h == NIL` and `gen[h as usize] != g`. Delete the second and
//!      this rung is `c/kernel.c`'s bug, in safe Rust, with `#![forbid(
//!      unsafe_code)]` satisfied and every detector silent. That arm is
//!      `../controls/storage_arms.py`'s `safe-rust-bug`, and it reproduces the
//!      buggy C **bit for bit on every input**.
//!   2. **The safe rung cannot be memory-unsafe and neither can the C rung.**
//!      There is no dangling pointer anywhere in this pattern -- see
//!      `../c/kernel.h` -- so "safe Rust prevents the bug" is not available as a
//!      sentence, in either direction. What safe Rust prevents here is nothing,
//!      and what it costs here is a bounds check.
//!   3. **Slots ARE recycled**, which is the difference from `p27`/`p29`'s
//!      convention (`ntab` only grows). Recycling is the pattern. The
//!      incarnation counter is what replaces the one-bit liveness flag those
//!      two get away with, and it is the thing the file cannot forge because a
//!      handle is issued by ALLOC and named by REGISTER, never spelled by the
//!      input (`../c/kernel.h`; `../NOTES.md` 1b measures the forgeable variant).
//!
//! Naive in the places R3 tunes: the registers are a NIL-sentinel pair of
//! parallel arrays rather than `Option<(u8, u32)>`, the pool is flat so every
//! payload access re-computes `h * BLK + 1`, `h as usize` is re-widened at each
//! use, and the opcode is an `if` chain. ⚠ **Whether any of that survives
//! optimisation was NOT measured: this pattern publishes no rung-to-rung cost
//! headline at all** (`../NOTES.md` 8), and the absence is declared rather than
//! reported as a zero.
//!
//! Wrapping arithmetic is spelled `wrapping_mul` / `wrapping_add` because
//! `-C debug-assertions=on` would otherwise panic on the fold and on the
//! generation bump, and the C rungs wrap by definition (C99 6.2.5p9).

#[path = "../../common/driver.rs"]
mod driver;

const SLOTS: usize = 8;
const BLK: usize = 4;
const NREG: usize = 8;
const NIL: u8 = 255;
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
    let mut pool: [u8; SLOTS * BLK] = [0u8; SLOTS * BLK];
    let mut nx: [u8; SLOTS] = [0u8; SLOTS];
    let mut gen: [u32; SLOTS] = [0u32; SLOTS];
    let mut regs: [u8; NREG] = [NIL; NREG];
    let mut regg: [u32; NREG] = [0u32; NREG];
    let mut j: usize = 0;
    while j < SLOTS {
        nx[j] = if j + 1 < SLOTS { (j + 1) as u8 } else { NIL };
        j = j + 1;
    }
    let mut freehead: u8 = 0;
    let mut nalloc: usize = 0;
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
        let r: usize = (a % NREG as u8) as usize;
        let v: u64 = if c % 4 == 0 {
            // ALLOC: pop the free list into handle register `r`. **Nothing is
            // allocated** -- the block already exists and always did.
            if freehead == NIL {
                SENT
            } else {
                let s: usize = freehead as usize;
                freehead = nx[s];
                pool[s * BLK] = a;
                pool[s * BLK + 1] = a.wrapping_mul(7).wrapping_add(1);
                regs[r] = s as u8;
                let gs: u32 = gen[s];
                regg[r] = gs;
                nalloc = nalloc + 1;
                (s as u64).wrapping_add((gs as u64).wrapping_mul(8))
            }
        } else {
            // FREE, READ and WRITE all consume the handle in register `r`, so
            // they share its decode and they share the one guard below.
            let h: u8 = regs[r];
            let g: u32 = regg[r];
            // THE SAFETY LINE. c/kernel.c omits the second conjunct and nothing
            // else. Note what safe Rust does NOT give here: `h == NIL` is a
            // sentinel test this rung writes, not an `Option` discriminant,
            // because nothing is ever dropped and there is no `None` for the
            // language to produce.
            if h == NIL {
                SENT
            } else if gen[h as usize] != g {
                SENT
            } else if c % 4 == 1 {
                gen[h as usize] = gen[h as usize].wrapping_add(1);
                nx[h as usize] = freehead;
                freehead = h;
                1
            } else if c % 4 == 2 {
                pool[h as usize * BLK + 1] as u64
            } else {
                pool[h as usize * BLK + 1] = a.wrapping_mul(13).wrapping_add(3);
                3
            }
        };
        acc = acc.wrapping_mul(31).wrapping_add(v);
        o = o + 1;
    }
    // No epilogue, in ANY rung: there is nothing to release. `p27` and `p29`
    // both have one and both hand it to `Drop` in the safe rungs; p32's pool is
    // a local array and the C rungs have no epilogue either.
    acc.wrapping_mul(31).wrapping_add(nalloc as u64)
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
