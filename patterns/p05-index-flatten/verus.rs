//! p05 rung R5 -- unsafe + Verus proof.
//!
//! R4's exec code verbatim, plus the specs and proofs that discharge every
//! unchecked read in it.
//!
//! **What is new here is the shape of the obligation, not its difficulty.**
//! p16's kernel indexed with a running position and p17's with a signed offset;
//! both are *sums*, and Z3 does linear integer arithmetic for free. p05 indexes
//! with `4 + i*ncol + j`, so the central obligation
//!
//!     i < nrow  &&  j < ncol  &&  nrow*ncol <= avail   ==>   i*ncol + j < avail
//!
//! is **nonlinear in two variables at once** and Z3 will not find it. The step
//! that carries it is `(i+1)*ncol <= nrow*ncol` from `i+1 <= nrow`, i.e.
//! `vstd::arithmetic::mul::lemma_mul_inequality`, joined to
//! `(i+1)*ncol == i*ncol + ncol` by one `by (nonlinear_arith)`. That pair sits
//! in the outer loop's invariant as `i*ncol + ncol <= nrow*ncol` and everything
//! else falls out linearly.
//!
//! The same nonlinearity is why the C bug is worth modelling: the *check*
//! `nrow*ncol > avail` is a multiplication too, so it can overflow in a
//! narrower type and silently pass. See c/kernel_hardened.c -- with u16
//! dimension fields the product exceeds `INT_MAX` but still fits `uint32_t`, so
//! it is the **signed** 32-bit spelling that breaks and not the unsigned one.
//! Nothing in this file can have that bug: `usize` here is proved lossless for
//! the product, and the spec functions are written over `int`, which is
//! unbounded.
//!
//! The `requires` is
//!
//!     off + len <= buf@.len()
//!
//! and that is all of it. It is structural -- about the shape of the buffer the
//! driver built, not about its contents -- so it holds on *every* input this
//! benchmark runs, `adversarial-*` included, and the gate checks it call by
//! call. Both declared dimensions, all 2^32 pairs, are arguments of the problem
//! and not assumptions.
//!
//! p17 needed a second clause, `buf@.len() <= i64::MAX`, because it cast to
//! `i64` and vstd has no axiom that a slice is at most `isize::MAX` bytes. p05
//! is unsigned end to end, so that clause would constrain nothing this proof
//! uses and it is deliberately absent -- along with the driver conjunct that
//! discharged it. Carrying a dead precondition forward from the template would
//! be exactly the "a `requires` no caller should have to discharge" failure
//! `.memory/02-bench-rules.md` warns about, in miniature.
//!
//! TCB tally: NOTES.md 5. Three `external_body` items, all listed there
//! individually, because an under-counted TCB is how the pilot's fatal defect
//! hid in plain sight (`.memory/04-verus.md`).

use vstd::prelude::*;

// Plain-Rust I/O helpers. Outside `verus!`, so Verus treats the whole module as
// external (external-by-default). Reached only through `load_input`/`emit`.
#[path = "../../common/driver.rs"]
mod driver;

verus! {

// `group_slice_axioms` gives `slice@.len() == spec_slice_len(slice)`, hence
// `slice@.len() <= usize::MAX` -- without it `off + len` cannot be shown not to
// overflow `usize`. `lemma_u128_shr_is_div` turns `x >> 64` into `x / 2^64`,
// which is what the driver's multiply-shift barrier bound is about. The mul
// group is what BOTH the window-offset bound `k * stride + stride <= n_blob`
// and p05's own `i*ncol + ncol <= nrow*ncol` need: every one of those steps is
// nonlinear.
broadcast use {
    vstd::slice::group_slice_axioms,
    vstd::bits::lemma_u128_shr_is_div,
    vstd::arithmetic::mul::lemma_mul_inequality,
};

// ------------------------------------------------------------------ spec ----
/// How many rows the window at `off` declares: a little-endian u16 at window
/// bytes 0..2. Declared, not derived -- that is the pattern.
pub open spec fn nrow_at(buf: Seq<u8>, off: int) -> int {
    buf[off] as int + 256 * (buf[off + 1] as int)
}

/// How many columns the window at `off` declares: a little-endian u16 at window
/// bytes 2..4.
///
/// **This is the attacker's number and the whole pattern is what the kernel
/// does with it.** `ncol` is the inner loop's trip count *and* the stride of
/// the flattened index, so it appears twice in every index the kernel forms.
pub open spec fn ncol_at(buf: Seq<u8>, off: int) -> int {
    buf[off + 2] as int + 256 * (buf[off + 3] as int)
}

/// Row `i`'s accumulator after its first `j` columns: a **u32** wrapping sum of
/// `buf[off + 4 + i*ncol + c]` for `c` in `0 .. j`.
///
/// Two things about this function are load-bearing.
///
/// * It is **associative** at the value level -- a plain sum, not a Horner
///   chain -- which is what lets LLVM vectorise the exec loop. p05 exists to
///   measure that, and a spec written as a Horner fold would have specified a
///   different program (see ../spec.md, "Load-bearing").
/// * The index is written `off + 4 + i*ncol + c`, the flattened 2-D index,
///   rather than as a running position. `row_fold` is therefore nonlinear in
///   its own arguments and the proof cannot dodge it.
pub open spec fn row_fold(buf: Seq<u8>, off: int, ncol: int, i: int, j: int) -> u32
    decreases j,
{
    if j <= 0 {
        0u32
    } else {
        row_fold(buf, off, ncol, i, j - 1).wrapping_add(
            buf[off + 4 + i * ncol + (j - 1)] as u32,
        )
    }
}

/// The matrix walk: rows `i .. nrow`, carrying the u64 accumulator.
///
/// The Horner step `acc*31 + row` happens once per **row**, so the result
/// depends on row order and the two loops cannot be re-associated into one flat
/// scan -- which is what stops a rung "vectorising" by folding the whole matrix
/// as a single sum and getting the same answer by accident.
///
/// `decreases nrow - i`: the trip count is a u16 read out of the buffer, so it
/// is attacker data, but it does not move during the walk.
pub open spec fn grid_walk(
    buf: Seq<u8>,
    off: int,
    nrow: int,
    ncol: int,
    i: int,
    acc: u64,
) -> u64
    decreases nrow - i,
{
    if i >= nrow {
        acc
    } else {
        grid_walk(
            buf,
            off,
            nrow,
            ncol,
            i + 1,
            acc.wrapping_mul(31).wrapping_add(row_fold(buf, off, ncol, i, ncol) as u64),
        )
    }
}

/// What the kernel returns: the walk over the declared matrix, with the element
/// count mixed into the checksum so that a rung which walks a *different number
/// of elements* cannot produce the same answer even if the bytes happened to
/// fold the same way.
///
/// The three early exits are the tests every rung keeps except where marked: a
/// window too short to hold the header, a zero dimension, and -- **the one R1
/// omits, and the only one it omits** -- a declared matrix bigger than the
/// bytes that arrived.
pub open spec fn grid_fold(buf: Seq<u8>, off: int, len: int) -> u64 {
    if len < 4 {
        0
    } else if nrow_at(buf, off) == 0 || ncol_at(buf, off) == 0 {
        0
    } else if nrow_at(buf, off) * ncol_at(buf, off) > len - 4 {
        0
    } else {
        grid_walk(buf, off, nrow_at(buf, off), ncol_at(buf, off), 0, 0).wrapping_mul(
            31,
        ).wrapping_add((nrow_at(buf, off) * ncol_at(buf, off)) as u64)
    }
}

// ------------------------------------------------------------------- TCB ----
// TRUSTED ITEM 1 of 3. vstd ships no specification for `<[T]>::get_unchecked`,
// so this is the axiom that licenses the unchecked read. It is sound because
// the standard library's documented contract for `get_unchecked` is exactly
// this: if the caller guarantees `i < v.len()`, the call is defined and yields
// `v[i]`.
//
// It is the *whole* security argument on p05, as it was on p16 and unlike p17.
// p05's harm is an ordinary out-of-bounds read -- the declared matrix is bigger
// than the buffer -- so `i < v@.len()`, discharged at every call site, is
// exactly what rules it out. The functional `ensures` on `kernel` is what keeps
// the proof honest about *which* bytes were folded; it is not carrying the
// memory-safety claim here.
#[inline(always)]
#[verifier::external_body]
fn get_unchecked(v: &[u8], i: usize) -> (r: u8)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    unsafe { *v.get_unchecked(i) }
}

// THE VERIFIED TWIN of trusted item 1 (`harness/check.py` step 5c-twin).
//
// Same signature and same contract, character for character -- the gate lifts
// both from `get_unchecked` above and refuses a twin whose signature differs --
// but implemented in *checked* code. A `requires` too weak to license
// `*v.get_unchecked(i)` is too weak to license `v[i]`, and Verus can see the
// second one. Weaken the pair to `i <= v@.len()` and this fails with
// `precondition not met: index in bounds for this access`.
//
// **The twin is idle again, and p05 does not change that either.**
// `.memory/04-verus.md` records that what the twin uniquely catches is a
// *missing conjunct* in a multi-clause trusted `requires`, and that its value
// accrues from the first pattern needing a multi-clause trusted accessor --
// which is a property of the *intrinsic being wrapped*, not of the pattern
// number. p05 wraps the same single-clause `<[u8]>::get_unchecked` that p01,
// p02, p16 and p17 wrap. Manufacturing a multi-clause accessor to exercise the
// mechanism would be gaming the gate; NOTES.md 8 reports "still idle" instead,
// for the fourth pattern running.
//
// `#[cfg(slb_twin)]` is a cfg no measured build ever sets, so rustc strips this
// before codegen: the twin costs zero instructions structurally.
#[cfg(slb_twin)]
fn slb_twin_get_unchecked(v: &[u8], i: usize) -> (r: u8)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    v[i]
}

// TRUSTED ITEM 2 of 3. Argument parsing, file I/O and little-endian decoding,
// delegated to common/driver.rs so that all six rungs read the file the same
// way. It states **no** `ensures` at all, deliberately: an `ensures` here would
// be an axiom about the contents of a file, which nothing can justify. Every
// fact the proof needs is re-derived at run time from `bytes.len()` inside
// verified code. It contains no `unsafe`, so it stays outside the twin regime
// (`.memory/04-verus.md`: the regime is keyed on `external_body` + a non-empty
// `ensures` OR `unsafe`).
#[verifier::external_body]
fn load_input() -> (r: (u64, u64, Vec<u8>)) {
    let path = driver::arg_path();
    let inp = driver::load(&path);
    let (stride_w, bytes) = driver::head1_u64_bytes(&inp);
    (inp.n_iters, stride_w, bytes)
}

// TRUSTED ITEM 3 of 3. `println!` is not verifiable; no `ensures`. Counted with
// the two above -- every `external_body` item is TCB, not just the interesting
// one (`.memory/04-verus.md`: the pilot was published as "one 3-line wrapper"
// and the true tally was three items, one of which was `main`).
#[verifier::external_body]
fn emit(acc: u64) {
    driver::emit(acc);
}

// ---------------------------------------------------------------- kernel ----
// Same exec code as unsafe.rs. Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> (r: u64)
    requires
        off + len <= buf@.len(),
    ensures
        r == grid_fold(buf@, off as int, len as int),
{
    // Ghost only: mentioning `spec_slice_len` fires vstd's `axiom_spec_len`,
    // which is what tells the SMT solver a slice length fits in a `usize` --
    // needed to rule out `off + len` overflowing. Erases at compile time.
    assert(buf@.len() == vstd::slice::spec_slice_len(buf));
    if len < 4 {
        return 0;
    }
    let nrow: usize = get_unchecked(buf, off) as usize + 256 * (get_unchecked(
        buf,
        off + 1,
    ) as usize);
    let ncol: usize = get_unchecked(buf, off + 2) as usize + 256 * (get_unchecked(
        buf,
        off + 3,
    ) as usize);
    if nrow == 0 || ncol == 0 {
        return 0;
    }
    let avail: usize = len - 4;
    // Ghost only: `nrow, ncol <= 65535`, so the product is at most
    // 4 294 836 225 and cannot overflow a `usize` of either width Verus models
    // (`usize::MAX` is `u32::MAX` or `u64::MAX`, and 4 294 836 225 < 4 294 967
    // 295). This is the same multiplication whose *narrower signed* spelling is
    // the bug in c/kernel_hardened.c's comment; here it is discharged rather
    // than assumed.
    assert(nrow * ncol <= 0xffff_ffffusize) by (nonlinear_arith)
        requires
            nrow <= 65535,
            ncol <= 65535,
    ;
    if nrow * ncol > avail {
        return 0;
    }
    let mut acc: u64 = 0;
    let mut i: usize = 0;
    // The invariant is the shape p16 found and p17 re-used: *the walk from
    // here, with what we have accumulated, is the whole walk.* The extra
    // conjunct p05 needs, and neither of them did, is the nonlinear one:
    // `i*ncol + ncol <= nrow*ncol`. It is what makes every index this row will
    // form provably below `avail`, and it is re-established at the bottom of
    // the loop from `i+1 <= nrow` by `lemma_mul_inequality`.
    while i < nrow
        invariant
            i <= nrow,
            0 < ncol,
            nrow == nrow_at(buf@, off as int),
            ncol == ncol_at(buf@, off as int),
            avail == len - 4,
            4 <= len,
            nrow * ncol <= avail,
            off + len <= buf@.len(),
            buf@.len() <= usize::MAX,
            grid_walk(buf@, off as int, nrow as int, ncol as int, i as int, acc)
                == grid_walk(buf@, off as int, nrow as int, ncol as int, 0, 0),
        decreases nrow - i,
    {
        // Ghost only, and this is p05's whole arithmetic difficulty in four
        // lines. `i < nrow` gives `i + 1 <= nrow`, hence
        // `(i+1)*ncol <= nrow*ncol` by monotonicity of multiplication in a
        // non-negative factor (`lemma_mul_inequality`), and
        // `(i+1)*ncol == i*ncol + ncol` by distributivity. Together:
        // `i*ncol + ncol <= nrow*ncol <= avail`, so every index this row will
        // form is inside the window. Z3 finds neither step on its own, and the
        // conjunct cannot live in the outer invariant instead -- at `i == nrow`
        // it is false, which is exactly why the obligation is interesting.
        proof {
            vstd::arithmetic::mul::lemma_mul_inequality(
                i as int + 1,
                nrow as int,
                ncol as int,
            );
            assert(((i as int) + 1) * (ncol as int) == (i as int) * (ncol as int) + (
            ncol as int)) by (nonlinear_arith);
        }
        let mut row: u32 = 0;
        let mut j: usize = 0;
        while j < ncol
            invariant
                j <= ncol,
                0 < ncol,
                i < nrow,
                avail == len - 4,
                4 <= len,
                nrow * ncol <= avail,
                i * ncol + ncol <= nrow * ncol,
                off + len <= buf@.len(),
                buf@.len() <= usize::MAX,
                row == row_fold(buf@, off as int, ncol as int, i as int, j as int),
            decreases ncol - j,
        {
            // Ghost only: this element is inside the window. `j < ncol` and the
            // outer invariant give `i*ncol + j < i*ncol + ncol <= nrow*ncol <=
            // avail`, hence `off + 4 + i*ncol + j < off + 4 + avail == off +
            // len <= buf@.len()`. Every step is linear *given* the invariant;
            // the invariant itself is where the nonlinearity was paid for.
            assert(i * ncol + j < nrow * ncol);
            row = row.wrapping_add(
                get_unchecked(buf, off + 4 + i * ncol + j) as u32,
            );
            j = j + 1;
        }
        acc = acc.wrapping_mul(31).wrapping_add(row as u64);
        i = i + 1;
    }
    acc.wrapping_mul(31).wrapping_add((nrow * ncol) as u64)
}

// ---------------------------------------------------------------- driver ----
fn main() {
    let (n_iters, stride_w, bytes) = load_input();
    // SLB-DRIVER-BEGIN
    let n_blob: usize = bytes.len();
    let buf: &[u8] = bytes.as_slice();
    let mut acc: u64 = 0;
    if stride_w >= 4 && stride_w <= n_blob as u64 {
        let stride: usize = stride_w as usize;
        let nwin: u64 = (n_blob / stride) as u64;
        let mut it: u64 = 0;
        // Ghost only: at least one whole window is present. `stride <= n_blob`
        // is the guard immediately above, and integer division only rounds
        // down, so `n_blob / stride >= 1` -- but that is a fact about division
        // and Z3 needs the lemma named.
        proof {
            vstd::arithmetic::div_mod::lemma_div_non_zero(n_blob as int, stride as int);
        }
        while it < n_iters
            invariant
                4 <= stride <= n_blob,
                buf@.len() == n_blob,
                nwin == n_blob / stride,
                nwin >= 1,
            decreases n_iters - it,
        {
            // Ghost only: `k` must land inside the blob. Two nonlinear steps, so
            // Z3 needs both spelled out. (1) `(acc * nwin) >> 64 < nwin` because
            // `acc <= u64::MAX` implies `acc * nwin < nwin * 2^64`;
            // `lemma_u128_shr_is_div` turns the shift into the division the
            // argument is about. (2) `k * stride + stride <= n_blob` because
            // `k <= nwin - 1` and `nwin * stride <= n_blob`. Erases at compile
            // time -- R4 and R5 stay byte-identical.
            proof {
                let p: int = (acc as int) * (nwin as int);
                assert((acc as u128) * (nwin as u128) <= (u64::MAX as u128) * (u64::MAX
                    as u128)) by (nonlinear_arith)
                    requires
                        acc <= u64::MAX,
                        nwin <= u64::MAX,
                ;
                assert(vstd::arithmetic::power2::pow2(64) == 0x1_0000_0000_0000_0000nat) by {
                    vstd::arithmetic::power2::lemma2_to64_rest();
                }
                assert(p < (nwin as int) * 0x1_0000_0000_0000_0000int) by (nonlinear_arith)
                    requires
                        p == (acc as int) * (nwin as int),
                        acc <= u64::MAX,
                        nwin >= 1,
                ;
            }
            let k: usize = ((acc as u128 * nwin as u128) >> 64) as usize;
            // Ghost only: the window index `k` names a window that is entirely
            // present, so `k * stride + stride <= n_blob` and the kernel's
            // structural precondition is discharged. `nwin * stride <= n_blob`
            // because division rounds down; `k * stride <= (nwin - 1) * stride`
            // because `k < nwin`. Both are nonlinear.
            proof {
                assert(k < nwin);
                vstd::arithmetic::div_mod::lemma_fundamental_div_mod(
                    n_blob as int,
                    stride as int,
                );
                assert((nwin as int) * (stride as int) <= n_blob as int);
                assert((k as int) * (stride as int) <= ((nwin as int) - 1) * (stride as int));
                assert(((nwin as int) - 1) * (stride as int) == (nwin as int) * (stride as int)
                    - (stride as int)) by (nonlinear_arith);
                assert((k as int) * (stride as int) + (stride as int) <= n_blob as int);
            }
            let r: u64 = kernel(buf, k * stride, stride);
            // Ghost only: this is what *consumes* the kernel's `ensures`.
            // Without it the postcondition is decoration -- deleting it entirely
            // still verifies, so nothing but mutation testing defends it
            // (`.memory/04-verus.md`). Ghost code erases, so the driver loop
            // stays byte-identical to R4's.
            assert(r == grid_fold(buf@, (k * stride) as int, stride as int));
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    emit(acc);
}

} // verus!
