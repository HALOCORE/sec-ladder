//! p25 rung R4 -- unsafe.
//!
//! R2's algorithm with the two bounds checks the algorithm's own guards already
//! imply removed: the window bytes are read through `buf_get_unchecked` and the
//! saved element through `vec_get_unchecked`.
//!
//! ⚠⚠ **WHAT THIS RUNG DOES *NOT* DO IS HOLD THE INTERIOR POINTER, AND THAT IS
//! THE ROW'S UNSAFE-SIDE RESULT RATHER THAN AN OMISSION.** `c/kernel.c` saves
//! `cur = &toks[curi]` and dereferences it after the vector has moved. Writing
//! that in Rust needs a raw `*const u8` taken from `toks.as_ptr()` and
//! dereferenced under a guard -- **and it is not admissible here, for a reason
//! that is a fact about the proof rung and not a preference:** `identity` pins
//! R4 and R5 to the same machine code, R5 has to verify, and Verus cannot
//! license `*cur`. A raw dereference needs a `PointsTo` permission, and the
//! permission for a `Vec`'s buffer is not obtainable; worse, `curbase == toks`
//! is an **address** comparison and Verus's pointers carry PROVENANCE, so
//! address equality does not imply the permission you hold is the one that names
//! that byte. **The stale interior pointer is not merely unsafe at R4 and R5, it
//! is UNREPRESENTABLE at R5** -- and `../controls/rust_bug.py` builds the R4
//! that does hold it, shows it reproduces `c/kernel.c` under Miri, and records
//! that it is the arm the identity pin excludes. ../NOTES.md 6b.
//!
//! **So p25's ladder deletes the bug ABOVE R1 and every rung above it is
//! spatial.** SAFETY (5) below is what is left of the temporal obligation: the
//! saved index is still in range, which is trivial here because a vector only
//! grows. That is a smaller obligation than p27's, p29's, p32's or p34's, and
//! saying so is the result; ../NOTES.md 6 states it in full.
//!
//! **The vectors are `Vec<u8>`**, not raw blocks, in this rung and in R5. That
//! is `.memory/01-ladder.md`'s law taken seriously: the row is about an
//! allocation that MOVES, and `Vec::push` is the allocator call that moves it --
//! a hand-rolled `std::alloc::realloc` would be a different program with the
//! same shape and no closer to C. ../NOTES.md 5 prices the two growth policies
//! against each other, which is the one place C and `Vec` are not the same
//! program.
//!
//! SAFETY (1): `off + len <= buf.len()` is the caller's structural
//!   precondition. Unchecked here; discharged at the call site by Verus in
//!   verus.rs.
//! SAFETY (2): `len >= 4` guards the window header, so
//!   `off + 3 < off + len <= buf.len()`.
//! SAFETY (3): the op is read only under `len - p >= 2` with `p <= len`, so
//!   `off + p + 1 < off + len <= buf.len()`.
//! SAFETY (4): `MAXCAP` bounds both vectors, so `toks.len() + strs.len()` cannot
//!   overflow the `u64` the epilogue folds.
//! SAFETY (5): **WHAT IS LEFT OF THE TEMPORAL ONE.** `curi` is set only under
//!   `toks.len() > 0` and to `a % toks.len()`, so `curi < toks.len()` when
//!   `have` becomes true; `toks` never shrinks, so `have ==> curi < toks.len()`
//!   holds at every later READ and `vec_get_unchecked(&toks, curi)` is in bounds.
//!   ⚠ **`c/kernel.c` cannot discharge this by any argument about indices**,
//!   because the thing it dereferences is not an index into the current vector
//!   -- it is an address into a block `realloc` retired.

#[path = "../../common/driver.rs"]
mod driver;

const MAXCAP: usize = 64;
const SENT: u64 = 251;

// The unchecked window read. Same accessor every unsafe rung in this project
// ships; in verus.rs it is trusted item 1 of 4.
#[inline(always)]
fn buf_get_unchecked(v: &[u8], i: usize) -> u8 {
    unsafe { *v.get_unchecked(i) }
}

// The unchecked VECTOR read. vstd ships no specification for
// `<[T]>::get_unchecked`, so verus.rs carries this as trusted item 2 of 4 with
// the standard library's own documented contract as its `requires`/`ensures`
// pair, and a verified twin that spells the same contract with `v[i]`.
#[inline(always)]
fn vec_get_unchecked(v: &Vec<u8>, i: usize) -> u8 {
    unsafe { *v.get_unchecked(i) }
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
    let mut toks: Vec<u8> = Vec::new();
    let mut strs: Vec<u8> = Vec::new();
    let mut curi: usize = 0;
    let mut have: bool = false;
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
                let v: u8 = vec_get_unchecked(&toks, curi);
                acc = acc.wrapping_mul(31).wrapping_add(v as u64);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        }
        o = o + 1;
    }
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
