//! p35 rung R4 -- unsafe Rust. **The union comes back, and with it the safety
//! line the safe rungs did not have to write.**
//!
//! R2 and R3 hold a `Cell` enum: the tag and the payload are ONE value and a
//! mismatch is unrepresentable, so those rungs have no ordering constraint to
//! violate. This rung holds C's shape -- a `[u8; CELLS]` of tags beside a
//! `[Pay; CELLS]` of unions -- so the two stores are two statements again and
//! **the ordering constraint is back, spelled by hand, at the two sites marked
//! below.** That is the row's cost gradient and it is a gradient in OBLIGATION,
//! not in instructions: ../NOTES.md 3.
//!
//! ⚠ **What `unsafe` buys here is bounds checks; what it COSTS is the
//! correct-variant obligation.** Every `pay_*` read below is undefined unless
//! the cell's tag names the member being read, and nothing in this file checks
//! that -- the algorithm maintains it. R5 (verus.rs) is this exec code with the
//! SAFETY comments turned into obligations a verifier discharges, and the
//! correct-variant one is **first class in Verus's type system**: a wrong
//! variant read is `error: requirement not met: to access this field, the union
//! must be in the correct variant`. ../NOTES.md 6.
//!
//! ⚠⚠ **THE UNION HOLDS AN ARENA OFFSET WHERE C HOLDS A POINTER, AND THAT IS
//! DISCLOSED RATHER THAN HIDDEN.** `.memory/01-ladder.md`: *a rung covered by an
//! `identity` pin is chained to the prover.* ../spec.md pins
//! `identity: unsafe == verus`, and R5 cannot hold a `*const u8` and dereference
//! it without `vstd::raw_ptr`'s `PointsTo` machinery -- which is p27's and p29's
//! row, and would put an allocation proof inside a type-confusion pattern. So
//! all four Rust rungs carry `o: u32`, the offset of the same arena byte C's
//! pointer points at, and every checksum agrees. ../NOTES.md 5 measures what
//! the substitution does and does not change.
//!
//! ⚠⚠⚠ **THIS RUNG IS THE ENDPOINT NOBODY SEARCHED, AND THE SENTENCE THAT
//! RESTED ON THAT IS RETRACTED (TASK_152 M1, landed TASK_153).** ../NOTES.md 3
//! published ~~R3 (safe, tuned) IS CHEAPER THAN R4 (unsafe): -5.3%~~ as a
//! safe-vs-unsafe result. R3's side had TWO levers counted; **this side had
//! ONE named and ZERO counterfactuals measured.** Give R4 R3's own op-walk and
//! **R4 wins by 203.05 Ir/call (6.63%) at identical checksums**, so the figure
//! is not about `unsafe` at all -- it is **THE PRICE OF THE `identity` PIN,
//! 373.61 Ir/call (11.56%)**, and that spelling cannot ship because
//! `chunks_exact`, `Take` and `ChunksExact` are all `is not supported` at the
//! pinned vstd while `identity: unsafe == verus` chains this file to R5.
//! ⚠ At `-O0` the SHIPPED pair already runs the other way (R4 14591.09 against
//! R3 17783.37 on `large.bin`), so the sign is not even stable across
//! optimisation level. ../NOTES.md 3 has the four-arm rig and its two controls.
//!
//! SAFETY (1): `off + len <= buf.len()` is the caller's structural
//!   precondition. Unchecked here; discharged at the call site in verus.rs.
//! SAFETY (2): `len >= 4` guards the window header.
//! SAFETY (3): the op is read only under `len - p >= 2` with `p <= len`.
//! SAFETY (4): `idx = a % CELLS` is `< CELLS` for every `a`, so `tags[idx]` and
//!   `pays[idx]` are in bounds unconditionally.
//! SAFETY (5): **THE CORRECT-VARIANT OBLIGATION.** `pay_i` is read only under
//!   `tags[idx] == T_INT`, `pay_o` only under `T_PTR` and `pay_d_gt1` only
//!   under `T_DBL`; and a tag is published only on a path that has just stored
//!   the matching member. This is the invariant `c/kernel.c` breaks.
//! SAFETY (6): the offset stored on the `T_PTR` path is `BUDGET - navail` with
//!   `navail >= 1`, so it is `< BUDGET` and `arena[o]` is in bounds. This is
//!   the second half of `wf_cells` in verus.rs and the only obligation on this
//!   pattern's unchecked reads that is SPATIAL.

#[path = "../../common/driver.rs"]
mod driver;

/// Tagged cells. Must equal `P35_CELLS` in c/kernel.h and `CELLS` in model.py.
const CELLS: usize = 8;
/// The arena, in bytes. Must equal `P35_BUDGET`.
const BUDGET: usize = 4;
/// What a rejected operation folds. Must equal `P35_SENT`.
const SENT: u64 = 251;

const T_UNSET: u8 = 0;
const T_INT: u8 = 1;
const T_PTR: u8 = 2;
const T_DBL: u8 = 3;

/// THE UNION. Three members, three types, one storage. C's
/// `union { uint64_t i; double d; uint8_t *p; }` with the pointer replaced by
/// the arena offset -- see the module note.
///
/// ⚠ No `#[derive(Clone, Copy)]`: verus.rs cannot have one
/// (`core::clone::AssertParamIsCopy` is `not supported`), and R4 ships R5's
/// exec code. The arrays below are therefore built from an eight-element array
/// LITERAL rather than a repeat-expression.
union Pay {
    i: u64,
    d: f64,
    o: u32,
}

// The unchecked window read. Same accessor every unsafe rung in this project
// ships; in verus.rs it is a trusted item with a verified twin.
#[inline(always)]
fn buf_get_unchecked(v: &[u8], i: usize) -> u8 {
    unsafe { *v.get_unchecked(i) }
}

// The unchecked ARRAY read and store, generic over the element type so that the
// tags and the arena share one accessor. Verified twins in verus.rs.
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

// The payload store. `Pay` is not `Copy`, so it needs its own accessor rather
// than sharing `arr_set_unchecked`. **Writing a union member is SAFE Rust** --
// only the read is not -- so the `unsafe` here is the unchecked INDEX and
// nothing else, and verus.rs's twin for it is `v[i] = x`.
#[inline(always)]
fn pay_set_unchecked<const N: usize>(v: &mut [Pay; N], i: usize, x: Pay) {
    unsafe {
        *v.get_unchecked_mut(i) = x;
    }
}

// THE THREE UNION READS. Each is undefined unless the cell is in the member's
// variant -- SAFETY (5) -- and each is the item verus.rs cannot give a verified
// twin, because **Rust has no safe spelling of a union read at all**
// (`error[E0133]`). ../NOTES.md 6a.
#[inline(always)]
fn pay_i<const N: usize>(v: &[Pay; N], i: usize) -> u64 {
    unsafe { v.get_unchecked(i).i }
}

#[inline(always)]
fn pay_o<const N: usize>(v: &[Pay; N], i: usize) -> u32 {
    unsafe { v.get_unchecked(i).o }
}

#[inline(always)]
fn pay_d_gt1<const N: usize>(v: &[Pay; N], i: usize) -> bool {
    unsafe { v.get_unchecked(i).d > 1.0 }
}

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md. Every unchecked access below is discharged in
// ../verus.rs; the exec code there is this code, character for character.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    if len < 4 {
        return 0;
    }
    let nops: usize = buf_get_unchecked(buf, off) as usize
        + 256 * (buf_get_unchecked(buf, off + 1) as usize)
        + 65536 * (buf_get_unchecked(buf, off + 2) as usize)
        + 16777216 * (buf_get_unchecked(buf, off + 3) as usize);
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
        arr_set_unchecked(&mut arena, j, (j as u8).wrapping_mul(11).wrapping_add(5));
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
        let c: u8 = buf_get_unchecked(buf, off + p);
        let a: u8 = buf_get_unchecked(buf, off + p + 1);
        p = p + 2;
        let idx: usize = (a % CELLS as u8) as usize;
        let v: u64 = if c % 4 == 0 {
            pay_set_unchecked(&mut pays, idx, Pay { i: (a as u64).wrapping_mul(2654435761) });
            arr_set_unchecked(&mut tags, idx, T_INT);
            a as u64
        } else if c % 4 == 1 {
            // ==================== THE SAFETY LINE (1 of 2) ==================
            // Publish the tag only once the payload it describes is in place.
            // c/kernel.c writes the tag store before the `if`, on a path where
            // the payload store may not happen.
            if navail > 0 {
                pay_set_unchecked(&mut pays, idx, Pay { o: (BUDGET - navail) as u32 });
                arr_set_unchecked(&mut tags, idx, T_PTR);
                navail = navail - 1;
                1
            } else {
                SENT
            }
            // ================================================================
        } else if c % 4 == 2 {
            // ==================== THE SAFETY LINE (2 of 2) ==================
            if navail > 0 {
                pay_set_unchecked(
                    &mut pays,
                    idx,
                    if a % 2 == 0 { Pay { d: 0.25 } } else { Pay { d: 2.5 } },
                );
                arr_set_unchecked(&mut tags, idx, T_DBL);
                navail = navail - 1;
                2
            } else {
                SENT
            }
            // ================================================================
        } else {
            let t: u8 = arr_get_unchecked(&tags, idx);
            if t == T_INT {
                pay_i(&pays, idx) & 0xFF
            } else if t == T_PTR {
                arr_get_unchecked(&arena, pay_o(&pays, idx) as usize) as u64
            } else if t == T_DBL {
                if pay_d_gt1(&pays, idx) {
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
