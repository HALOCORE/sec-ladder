//! p19 rung R5 -- unsafe + Verus proof.
//!
//! R4's exec code verbatim, plus the specs and proofs that discharge every
//! unchecked read in it. **The obligation is a LOOP-CARRIED DATA INVARIANT**,
//! and that is what is new here: `st < NST` holds not because of arithmetic on
//! a loop counter but because 2048 bytes read out of the input at run time were
//! all checked once, before the loop, and `st` is only ever assigned one of
//! them. The proof is the two-line argument a kernel developer writes in a
//! comment above `aa_dfa_match()` -- made mechanical.
//!
//! ⚠ **THE OBLIGATION IS EXACTLY WHAT `c/kernel.c` WALKS THROUGH.** That rung
//! is this program with the validation pass deleted; the invariant then has no
//! establishing step, the `assert(st * 256 + b < TBL)` below is false, and the
//! read leaves the window. There is no Verus spelling of `c/kernel.c` that
//! verifies, which is the strongest form of "the proof is load-bearing" this
//! project has: the deleted lines are not an optimisation the prover happens to
//! reject, they are the premise.
//!
//! **Why the window is taken with `vstd::slice::slice_subrange` and not by
//! absolute `buf[off + ..]` indexing** (p36's shape): measured, absolute
//! indexing costs the *unsafe* rung **+2.25 Ir/byte** -- the `off` add cannot
//! be folded into the base pointer and the fold unrolls 2x instead of 4x -- and
//! it costs the *masked safe* rung **+10.87 Ir/byte**, because `buf.len()` is a
//! runtime value so the bounds check is no longer elidable. Sub-slices are
//! therefore forced, on both sides, and `slice_subrange` is what makes them
//! expressible here. It compiles to `&slice[i..j]`: this file's `kernel` and
//! an R4 written with `&w[0..TBL]` are **byte-identical, `235 B`,
//! `ac3fb207cd05963419d722adcd8b9da2` on both**, extracted from the linked
//! binaries (../NOTES.md 5).
//!
//! ⚠ `slice_subrange` is a **vstd** `external_body` item, not an
//! author-written one. It does not enter this pattern's TCB tally, which counts
//! project-local trusted items (`.memory/04-verus.md`); the standing question
//! about *used* vstd trusted items is `RECAP`'s gate work and is not settled
//! here. ../NOTES.md 7 says so beside the tally rather than leaving it implied.
//!
//! TCB tally: ../NOTES.md 7. **Three** `external_body` items, **one** of them
//! with a contract.
//!
//! SAFETY (1): `off + len <= buf.len()` is the caller's structural
//!   precondition. Discharged at the call site by the driver's proof below.
//! SAFETY (2): the validation loop reads `tbl[i]` under `i < TBL` with
//!   `tbl@.len() == TBL`.
//! SAFETY (3): the fold reads `w[p]` under `p < len` with `w@.len() == len`.
//! SAFETY (4): **the fold reads `tbl[st * 256 + b]` under `st < NST`**, the
//!   invariant the validation loop establishes. This is the one.

// Plain-Rust I/O helpers. Outside `verus!`, so Verus treats the whole module as
// external (external-by-default). Reached only through `load_input`/`emit`.
#[path = "../../common/driver.rs"]
mod driver;

use vstd::prelude::*;
use vstd::slice::slice_subrange;

verus! {

// p19 targets x86-64 only (`.memory/00-environment.md`). Verus treats `usize`
// as architecture-independent by default, so `st * 256` and `off + len` would
// carry hypothetical 32-bit overflow obligations. This declaration is CHECKED
// by Verus against the actual compilation target rather than assumed, so it is
// not an axiom and adds nothing to the TCB.
global size_of usize == 8;

// `group_slice_axioms` gives `slice@.len() == spec_slice_len(slice)`, hence
// `slice@.len() <= usize::MAX` -- without it `off + len` cannot be shown not to
// overflow `usize`. `lemma_u128_shr_is_div` turns `x >> 64` into `x / 2^64`,
// the driver's multiply-shift barrier bound, and the mul group is what the
// driver's window-offset bound needs; the KERNEL needs neither.
broadcast use {
    vstd::slice::group_slice_axioms,
    vstd::bits::lemma_u128_shr_is_div,
    vstd::arithmetic::mul::lemma_mul_inequality,
};

/// The decoder's table capacity: the number of states the program has room
/// for. A compile-time constant in every rung, exactly as AppArmor's unpacked
/// tables are bounded by the `state_count` its header declares.
///
/// A `const` inside `verus!` is its own obligation (`.memory/04-verus.md`,
/// measured on p08's `SCR`), so the three constants here contribute 3 to the
/// count pinned in ../spec.md.
pub const NST: usize = 8;

/// Bytes of transition table: `NST` rows of 256 columns, one per input byte.
pub const TBL: usize = 2048;

/// What an invalid table folds to. A compile-time constant in every rung.
pub const REJ: u64 = 0xd1b5_4a32_d192_ed03;

// ------------------------------------------------------------------ spec ----
/// **THE VALIDITY PREDICATE**: every transition entry names a state that
/// exists. `verify_dfa()` at the specification level.
pub open spec fn tbl_ok(w: Seq<u8>) -> bool {
    forall|j: int| 0 <= j < TBL ==> ((#[trigger] w[j]) as int) < NST as int
}

/// The abstract machine. Note what it says and what it does not: it describes
/// the PROGRAM -- fold the message a byte at a time through the table -- and it
/// says nothing about the table being valid. Validity is `tbl_ok`'s job, and
/// `window_fold` is where the two meet.
pub open spec fn run(w: Seq<u8>, p: int, st: int, acc: u64) -> u64
    decreases w.len() - p,
{
    if p >= w.len() {
        acc.wrapping_mul(31).wrapping_add(st as u64)
    } else {
        let ns = w[st * 256 + (w[p] as int)] as int;
        run(w, p + 1, ns, acc.wrapping_mul(31).wrapping_add(ns as u64))
    }
}

/// What one window folds to. Total: every adversarial input is inside this
/// domain (../spec.md).
pub open spec fn window_fold(w: Seq<u8>) -> u64 {
    if w.len() <= TBL as int {
        0
    } else if !tbl_ok(w) {
        REJ
    } else {
        run(w, TBL as int, 0, 0)
    }
}

/// What the kernel must return.
pub open spec fn st_fold(buf: Seq<u8>, off: int, len: int) -> u64 {
    window_fold(buf.subrange(off, off + len))
}

// --------------------------------------------------------------- trusted ----
// TRUSTED ITEM 1 of 3, and the only one with a contract. The unchecked read.
// vstd ships no specification for `<[T]>::get_unchecked` (0 hits at the pinned
// version), and the standard library's documented contract is exactly this
// `requires`/`ensures` pair.
#[inline(always)]
#[verifier::external_body]
fn buf_get_unchecked(v: &[u8], i: usize) -> (r: u8)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    unsafe { *v.get_unchecked(i) }
}

// THE VERIFIED TWIN of trusted item 1. Same signature, same contract, body the
// *checked* code: a `requires` too weak to license `*v.get_unchecked(i)` is too
// weak to license `v[i]`, and Verus can see the second one. `#[cfg(slb_twin)]`
// is a cfg no measured build ever sets, so rustc strips it before codegen.
#[cfg(slb_twin)]
fn slb_twin_buf_get_unchecked(v: &[u8], i: usize) -> (r: u8)
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
// one (`.memory/04-verus.md`).
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
        r == st_fold(buf@, off as int, len as int),
{
    // Ghost only: mentioning `spec_slice_len` fires vstd's `axiom_spec_len`,
    // which is what tells the SMT solver a slice length fits in a `usize`.
    assert(buf@.len() == vstd::slice::spec_slice_len(buf));
    if len <= TBL {
        assert(buf@.subrange(off as int, off + len).len() <= TBL);
        return 0;
    }
    let w = slice_subrange(buf, off, off + len);
    let tbl = slice_subrange(w, 0, TBL);
    // ---- the validation pass. `c/kernel.c` is this program without it. -----
    let mut i: usize = 0;
    while i < TBL
        invariant
            i <= TBL,
            tbl@.len() == TBL,
            tbl@ =~= w@.subrange(0, TBL as int),
            w@ == buf@.subrange(off as int, off + len),
            w@.len() == len,
            len > TBL,
            forall|j: int| 0 <= j < i ==> ((#[trigger] w@[j]) as int) < NST as int,
        decreases TBL - i,
    {
        if buf_get_unchecked(tbl, i) as usize >= NST {
            assert(!tbl_ok(w@));
            return REJ;
        }
        i += 1;
    }
    assert(tbl_ok(w@));
    // ---- the fold. Every read unchecked, licensed by the pass above. -------
    let mut p: usize = TBL;
    let mut st: usize = 0;
    let mut acc: u64 = 0;
    while p < len
        invariant
            TBL <= p <= len,
            st < NST,
            len > TBL,
            w@ == buf@.subrange(off as int, off + len),
            w@.len() == len,
            tbl@.len() == TBL,
            tbl@ =~= w@.subrange(0, TBL as int),
            tbl_ok(w@),
            run(w@, TBL as int, 0, 0) == run(w@, p as int, st as int, acc),
        decreases len - p,
    {
        let b = buf_get_unchecked(w, p) as usize;
        // THE SAFETY LINE, as an obligation. `b <= 255` because it is a `u8`
        // and `st < NST` is the loop-carried invariant, so the index is inside
        // the table; the entry read is itself `< NST`, which re-establishes it.
        assert(st * 256 + b < TBL);
        assert(((w@[(st * 256 + b) as int]) as int) < NST as int);
        let ns = buf_get_unchecked(tbl, st * 256 + b) as usize;
        st = ns;
        acc = acc.wrapping_mul(31).wrapping_add(ns as u64);
        p = p + 1;
    }
    acc.wrapping_mul(31).wrapping_add(st as u64)
}

// ---------------------------------------------------------------- driver ----
fn main() {
    let (n_iters, stride_w, bytes) = load_input();
    // SLB-DRIVER-BEGIN
    let n_blob: usize = bytes.len();
    let buf: &[u8] = bytes.as_slice();
    let mut acc: u64 = 0;
    if stride_w > 0 && stride_w <= n_blob as u64 {
        let stride: usize = stride_w as usize;
        let nwin: u64 = (n_blob / stride) as u64;
        let mut it: u64 = 0;
        // Ghost only: at least one whole window is present.
        proof {
            vstd::arithmetic::div_mod::lemma_div_non_zero(n_blob as int, stride as int);
        }
        while it < n_iters
            invariant
                1 <= stride <= n_blob,
                buf@.len() == n_blob,
                nwin == n_blob / stride,
                nwin >= 1,
            decreases n_iters - it,
        {
            // Ghost only: `k` must land inside the blob. Two nonlinear steps, so
            // Z3 needs both spelled out. Erases at compile time.
            proof {
                let pp: int = (acc as int) * (nwin as int);
                assert((acc as u128) * (nwin as u128) <= (u64::MAX as u128) * (u64::MAX
                    as u128)) by (nonlinear_arith)
                    requires
                        acc <= u64::MAX,
                        nwin <= u64::MAX,
                ;
                assert(vstd::arithmetic::power2::pow2(64) == 0x1_0000_0000_0000_0000nat) by {
                    vstd::arithmetic::power2::lemma2_to64_rest();
                }
                assert(pp < (nwin as int) * 0x1_0000_0000_0000_0000int) by (nonlinear_arith)
                    requires
                        pp == (acc as int) * (nwin as int),
                        acc <= u64::MAX,
                        nwin >= 1,
                ;
            }
            let k: usize = ((acc as u128 * nwin as u128) >> 64) as usize;
            // Ghost only: the window index `k` names a window that is entirely
            // present, so `k * stride + stride <= n_blob` and the kernel's
            // structural precondition is discharged. Both steps are nonlinear.
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
            assert(r == st_fold(buf@, (k * stride) as int, stride as int));
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    emit(acc);
}

} // verus!
