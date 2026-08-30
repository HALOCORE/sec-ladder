//! p32 rung R4 -- unsafe.
//!
//! R2's algorithm with every array access unchecked. **What does NOT go away is
//! the safety line**, `gen[h] != g` at the one site where a handle is consumed.
//! That is
//! not a bounds check -- `h` is `NIL` or a real slot in every rung including R1,
//! so no index here can ever be out of range and there is no bounds check to
//! remove there. It is the kernel's SEMANTICS: the hardened cell folds SENT for
//! a handle whose block has been recycled, and ../spec.md pins that answer. A
//! rung without it would be R1's bug written in Rust rather than an unsafe rung.
//! This rung is correct; it just has nothing checking that it is. R5 (verus.rs)
//! is this exec code with the SAFETY comments below turned into obligations a
//! verifier discharges.
//!
//! ⚠⚠ **WHAT THIS RUNG'S `unsafe` BUYS IS BOUNDS CHECKS AND NOTHING ELSE, AND
//! THAT IS A RESULT ABOUT THE PATTERN.** `p27`'s and `p29`'s unsafe rungs hold
//! raw pointers to individually allocated records and call `allocate` /
//! `deallocate` by hand -- seven trusted items, two of them the allocation API.
//! **p32 allocates nothing.** Its storage is `[u8; POOLSZ]`, alive for the
//! whole call, so there is no pointer to hold, no `PointsTo` to consume, no
//! `Dealloc` token, and no `global layout` declaration. **TCB: five items**, and
//! all five are the ones every unsafe rung in this project already ships.
//! ../NOTES.md 6 counts them.
//!
//! **The registers stay a NIL-sentinel pair of parallel arrays** rather than R3's
//! `Option<(u8, u32)>`, because verus.rs's abstract machine carries them as two
//! `Seq`s and R4 ships R5's exec code. The `Option` spelling is R3's lever and
//! it is measured nowhere -- this pattern publishes no rung-to-rung cost at all
//! (../NOTES.md 8).
//!
//! SAFETY (1): `off + len <= buf.len()` is the caller's structural
//!   precondition. Unchecked here; discharged at the call site in verus.rs.
//! SAFETY (2): `len >= 4` guards the window header.
//! SAFETY (3): the op is read only under `len - p >= 2` with `p <= len`.
//! SAFETY (4): `r = a % NREG` is `< NREG` for every `a`, so `regs[r]` and
//!   `regg[r]` are in bounds unconditionally.
//! SAFETY (5): `freehead` is `NIL` or `< SLOTS`, and it is only ever assigned
//!   from `nx[s]` (whose every element is `NIL` or `< SLOTS`) or from a slot
//!   `h < SLOTS`. So `nx[s]`, `gen[s]` and `pool[s * BLK + i]` are in bounds
//!   under `freehead != NIL`.
//! SAFETY (6): `regs[r]` is `NIL` or `< SLOTS`, because ALLOC is the only writer
//!   and it stores `freehead` under `freehead != NIL`. So the shared
//!   handle-consuming path indexes `gen`, `nx` and `pool` in bounds.
//! SAFETY (7): **there is no temporal obligation here at all**, and that is the
//!   pattern. The pool is a local array; nothing is allocated, nothing is freed,
//!   nothing dangles, and `gen[h] != g` is a FUNCTIONAL condition on a live
//!   object rather than a licence to dereference. What the omission costs is a
//!   wrong answer and an aliased handle, never undefined behaviour.
//!   ../NOTES.md 6b says what that does to R5.

#[path = "../../common/driver.rs"]
mod driver;

const SLOTS: usize = 8;
const BLK: usize = 4;
// The pool's extent. Named rather than written `SLOTS * BLK` at the array type
// so that this file and verus.rs declare the same thing the same way.
const POOLSZ: usize = 32;
const NREG: usize = 8;
const NIL: u8 = 255;
const SENT: u64 = 251;

// The unchecked window read. Same accessor every unsafe rung in this project
// ships; in verus.rs it is trusted item 1 of 5.
#[inline(always)]
fn buf_get_unchecked(v: &[u8], i: usize) -> u8 {
    unsafe { *v.get_unchecked(i) }
}

// The unchecked ARRAY read and store, generic over the element type so that the
// pool, the free-list links, the generations and both register arrays share one
// accessor. verus.rs's trusted items 2 and 3.
#[inline(always)]
fn arr_get_unchecked<T: Copy, const N: usize>(v: &[T; N], i: usize) -> T {
    unsafe { *v.get_unchecked(i) }
}

#[inline(always)]
fn arr_set_unchecked<T: Copy, const N: usize>(v: &mut [T; N], i: usize, x: T) {
    unsafe {
        *v.get_unchecked_mut(i) = x;
    }
}

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    if len < 4 {
        return 0;
    }
    let nops: usize = buf_get_unchecked(buf, off) as usize + 256 * (buf_get_unchecked(
        buf,
        off + 1,
    ) as usize) + 65536 * (buf_get_unchecked(buf, off + 2) as usize) + 16777216 * (
    buf_get_unchecked(buf, off + 3) as usize);
    if nops == 0 {
        return 0;
    }
    let mut pool: [u8; POOLSZ] = [0u8; POOLSZ];
    let mut nx: [u8; SLOTS] = [0u8; SLOTS];
    let mut gen: [u32; SLOTS] = [0u32; SLOTS];
    let mut regs: [u8; NREG] = [NIL; NREG];
    let mut regg: [u32; NREG] = [0u32; NREG];
    let mut j: usize = 0;
    while j < SLOTS {
        arr_set_unchecked(&mut nx, j, if j + 1 < SLOTS { (j + 1) as u8 } else { NIL });
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
        let c: u8 = buf_get_unchecked(buf, off + p);
        let a: u8 = buf_get_unchecked(buf, off + p + 1);
        p = p + 2;
        let r: usize = (a % NREG as u8) as usize;
        let v: u64 = if c % 4 == 0 {
            if freehead == NIL {
                SENT
            } else {
                let s: usize = freehead as usize;
                freehead = arr_get_unchecked(&nx, s);
                arr_set_unchecked(&mut pool, s * BLK, a);
                arr_set_unchecked(&mut pool, s * BLK + 1, a.wrapping_mul(7).wrapping_add(1));
                arr_set_unchecked(&mut regs, r, s as u8);
                let gs: u32 = arr_get_unchecked(&gen, s);
                arr_set_unchecked(&mut regg, r, gs);
                nalloc = nalloc + 1;
                (s as u64).wrapping_add((gs as u64).wrapping_mul(8))
            }
        } else {
            let h: u8 = arr_get_unchecked(&regs, r);
            let g: u32 = arr_get_unchecked(&regg, r);
            // THE SAFETY LINE. c/kernel.c omits the second conjunct.
            if h == NIL {
                SENT
            } else if arr_get_unchecked(&gen, h as usize) != g {
                SENT
            } else if c % 4 == 1 {
                let gh: u32 = arr_get_unchecked(&gen, h as usize).wrapping_add(1);
                arr_set_unchecked(&mut gen, h as usize, gh);
                arr_set_unchecked(&mut nx, h as usize, freehead);
                freehead = h;
                1
            } else if c % 4 == 2 {
                arr_get_unchecked(&pool, h as usize * BLK + 1) as u64
            } else {
                arr_set_unchecked(&mut pool, h as usize * BLK + 1, a.wrapping_mul(13)
                    .wrapping_add(3));
                3
            }
        };
        acc = acc.wrapping_mul(31).wrapping_add(v);
        o = o + 1;
    }
    // No epilogue: nothing was ever acquired.
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
