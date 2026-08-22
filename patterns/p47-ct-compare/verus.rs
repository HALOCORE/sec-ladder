//! p47 rung R5 -- unsafe + Verus proof.
//!
//! R4's exec code verbatim, plus the specs and proofs that discharge every
//! unchecked read in it.
//!
//! ⚠⚠ **THIS IS THE ONE PATTERN IN THIS PROJECT WHERE THE PROOF DOES NOT
//! EXCLUDE THE C RUNG'S DEFECT, AND IT IS NOT BECAUSE THE PROOF IS WEAK.**
//! Every other `verus.rs` here can say "change the one character `c/kernel.c`
//! gets wrong and Verus stops verifying". Substitute p47's bug into this file
//! -- replace the or-accumulate with an early-exiting comparison that returns
//! the same verdict -- and **Verus verifies it, at the same obligation count,
//! with the same `ensures`, and the resulting binary leaks.**
//! `controls/proof_mutants.py` builds exactly that mutant (`m_leak`) and
//! ../NOTES.md 9 shows it verifying.
//!
//! The reason is structural and worth stating precisely rather than as a
//! shrug:
//!
//!   * `ensures r == tag_fold(buf@, off, len)` is a statement about the
//!     **value** the function returns. p47's defect does not change the value.
//!   * A timing property is a statement about the **trace** -- which
//!     instructions ran, in what number -- and Verus's logic has no term that
//!     denotes a trace, no cost model, and no way to quantify over the two
//!     executions a non-interference property compares. It is not that the
//!     property is hard to prove here; **it is not expressible in the assertion
//!     language at all.**
//!   * The property is also not a property of *this program* alone. It is a
//!     property of the machine code, and the machine code is chosen by LLVM
//!     after Verus has finished. Even a Verus that could state it would be
//!     stating it about the wrong artefact -- which is
//!     `.memory/06-catalogue.md`'s hazard 2 (*a text pin binds the source, not
//!     the object*) with the prover in place of the pin.
//!
//! **So the top rung of this project's ladder certifies a leaking kernel.**
//! That is p17 (*provably memory-safe and still leaking*) one level up, and it
//! is a clean negative the project can state precisely rather than a stall.
//! ../NOTES.md 9 gives the full statement of what *can* be proved.
//!
//!     requires  off + len <= buf@.len()
//!
//! ONE clause, as on p03, p06, p10, p11, p12, p14, p18 and p27 and unlike p17.
//! It is structural -- about the shape of the buffer the driver built, not
//! about its contents -- so it holds on *every* input this benchmark runs,
//! `adversarial-*` included, and the gate checks it call by call. `ntag`,
//! `tlen` and every tag byte are attacker data and none of them is an
//! assumption. In particular **there is no `requires` that `ntag` or `tlen` is
//! honest**; a precondition about the contents of a file is one no loader can
//! discharge (`.memory/02-bench-rules.md`).
//!
//! **THE SPEC DECIDES A COMPARISON THE CONSTANT-TIME WAY, ON PURPOSE.** `xacc`
//! is the or-accumulate of the byte-wise xor over the whole tag -- the same
//! recursion the exec code performs -- and the verdict is `xacc(..) == 0`.
//! Writing the spec as `a =~= b` (sequence equality) would have been shorter
//! and would have specified the same function; it is written this way so that
//! **`model.py`'s two implementations can disagree about the algorithm and
//! agree about the answer** -- its simulation uses Python's early-exiting
//! `bytes.__eq__` and its helper mirrors this file. The gate then checks the
//! leaking and the constant-time decision procedures against each other on
//! every call of every input.
//!
//! The little-endian header is decoded with `+` and `*` rather than `|` and
//! `<<` (`.memory/04-verus.md`): the two are the same function on bytes and
//! compile to the same instruction, but only the first is linear arithmetic.
//! The **only** bit operations anywhere in this file are the `|` and `^`
//! inside `xacc`, which are never reasoned about -- the proof unfolds the
//! recursion and never inspects a bit -- so there is no `by (bit_vector)`
//! here.
//!
//! TCB tally: ../NOTES.md 6. **Three** `external_body` items, **one** of them
//! with a `requires` -- the same shape as p10 and p18, and for the same
//! structural reason: p47's kernel performs exactly ONE kind of memory access,
//! a byte read of the input window. There is no scratch, no output buffer, no
//! allocation and no write of any kind.

use vstd::prelude::*;

// Plain-Rust I/O helpers. Outside `verus!`, so Verus treats the whole module
// as external (external-by-default). Reached only through `load_input`/`emit`.
#[path = "../../common/driver.rs"]
mod driver;

verus! {

// `group_slice_axioms` gives `slice@.len() == spec_slice_len(slice)`, hence
// `slice@.len() <= usize::MAX` -- without it `off + len` cannot be shown not
// to overflow `usize`. `lemma_u128_shr_is_div` turns `x >> 64` into
// `x / 2^64`, which is the driver's multiply-shift barrier bound, and the mul
// group is what the driver's window-offset bound `k * stride + stride <=
// n_blob` needs; the KERNEL needs neither. p47 needs NO array group -- it has
// no array.
//
// p47 targets x86-64 only (`.memory/00-environment.md`). Verus treats `usize`
// as architecture-independent by default, so `2 * tlen` on a `usize` built
// from four bytes is `possible arithmetic underflow/overflow` on a
// hypothetical 32-bit target. This declaration is CHECKED by Verus against the
// actual compilation target rather than assumed, so it is not an axiom and
// adds nothing to the TCB.
global size_of usize == 8;

broadcast use {
    vstd::slice::group_slice_axioms,
    vstd::bits::lemma_u128_shr_is_div,
    vstd::arithmetic::mul::lemma_mul_inequality,
};

/// What an equal comparison folds. Compile-time constant in all eight rungs.
pub const MATCH: u64 = 7;

/// What an unequal comparison folds. Compile-time constant in all eight rungs.
pub const MISS: u64 = 251;

// ------------------------------------------------------------------ spec ----
/// The little-endian u32 at absolute byte position `p`, written out the way
/// every rung writes it: `b0 + 256*b1 + 65536*b2 + 16777216*b3`.
pub open spec fn u32_at(buf: Seq<u8>, p: int) -> int {
    buf[p] as int + 256 * (buf[p + 1] as int) + 65536 * (buf[p + 2] as int)
        + 16777216 * (buf[p + 3] as int)
}

/// ONE COMPARISON, decided the constant-time way: the or-accumulate of
/// `secret[i] ^ candidate[i]` over **every** `i`, from byte `i` with running
/// accumulator `d`. The tags are `buf[base .. base+tlen]` and
/// `buf[base+tlen .. base+2*tlen]`.
///
/// This is a recursion over the whole tag and *not* `a =~= b`, deliberately --
/// see the module comment. A rung that stopped at the first differing byte
/// computes the same predicate and satisfies this spec, which is precisely
/// p47's result.
pub open spec fn xacc(buf: Seq<u8>, base: int, tlen: int, i: int, d: u8) -> u8
    decreases tlen - i,
{
    if i >= tlen {
        d
    } else {
        xacc(buf, base, tlen, i + 1, d | (buf[base + i] ^ buf[base + tlen + i]))
    }
}

/// THE MACHINE: comparisons `o .. ntag`, folding each VERDICT into `acc`.
///
/// The walk stops for either of two reasons -- the declared count is exhausted
/// or the window cannot hold another `2*tlen` bytes -- and `o` is folded once
/// at the end, so a rung that performed a different NUMBER of comparisons
/// cannot produce this value. **What is folded is `MATCH`/`MISS` and never a
/// tag byte**: that is what makes two windows with the same verdict sequence
/// and different first-mismatch positions indistinguishable to this
/// specification, and it is the pattern's whole subject.
pub open spec fn twalk(
    buf: Seq<u8>,
    off: int,
    len: int,
    tlen: int,
    o: int,
    ntag: int,
    p: int,
    acc: u64,
) -> u64
    decreases ntag - o,
{
    if o >= ntag || len - p < 2 * tlen {
        acc.wrapping_mul(31).wrapping_add(o as u64)
    } else {
        twalk(
            buf,
            off,
            len,
            tlen,
            o + 1,
            ntag,
            p + 2 * tlen,
            if xacc(buf, off + p, tlen, 0, 0) == 0 {
                acc.wrapping_mul(31).wrapping_add(MATCH)
            } else {
                acc.wrapping_mul(31).wrapping_add(MISS)
            },
        )
    }
}

/// What the kernel returns.
///
/// The two early exits are the tests every rung keeps, R1 included: a window
/// too short to hold the header, and a header declaring no comparisons or a
/// zero-length tag. **R1 keeps both, and R1 keeps the window guard inside
/// `twalk` too** -- what it gets wrong is not any of them.
pub open spec fn tag_fold(buf: Seq<u8>, off: int, len: int) -> u64 {
    if len < 8 {
        0
    } else {
        let ntag = u32_at(buf, off);
        let tlen = u32_at(buf, off + 4);
        if ntag == 0 || tlen == 0 {
            0
        } else {
            twalk(buf, off, len, tlen, 0, ntag, 8, 0)
        }
    }
}

// ------------------------------------------------------------------- TCB ----
// TRUSTED ITEM 1 of 3, and **the only one with a `requires`**. vstd ships no
// specification for `<[T]>::get_unchecked`, so this is the axiom that licenses
// the unchecked read of the window. It is sound because the standard library's
// documented contract for `get_unchecked` is exactly this: if the caller
// guarantees `i < v.len()`, the call is defined and yields `v[i]`. Identical,
// character for character, to the accessor p01, p02, p03, p05, p06, p07, p10,
// p11, p12, p13, p14, p16, p17, p18 and p27 ship.
//
// ⚠ **ON p47 THIS ITEM'S `requires` HAS NOTHING TO DO WITH THE PATTERN'S
// BUG**, and that is a difference from p10 worth naming. p10's defect is an
// out-of-bounds read and `i < v@.len()` is exactly what excludes it. p47's
// defect is a timing leak; `c/kernel.c` violates no bound, so this
// precondition -- and every other obligation in this file -- is silent about
// it. ../NOTES.md 6 and 9.
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

// THE VERIFIED TWIN of trusted item 1 (`harness/check.py` step 5c-twin). Same
// signature and same contract, character for character, implemented in
// *checked* code: a `requires` too weak to license `*v.get_unchecked(i)` is
// too weak to license `v[i]`, and Verus can see the second one. `#[cfg(slb_twin)]`
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
// delegated to common/driver.rs so that all eight rungs read the file the same
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

// TRUSTED ITEM 3 of 3. `println!` is not verifiable; no `ensures`. Counted
// with the two above -- every `external_body` item is TCB, not just the
// interesting one (`.memory/04-verus.md`: the pilot was published as "one
// 3-line wrapper" and the true tally was three items, one of which was
// `main`).
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
        r == tag_fold(buf@, off as int, len as int),
{
    // Ghost only: mentioning `spec_slice_len` fires vstd's `axiom_spec_len`,
    // which is what tells the SMT solver a slice length fits in a `usize` --
    // needed to rule out `off + p + tlen + i` overflowing. Erases at compile
    // time.
    assert(buf@.len() == vstd::slice::spec_slice_len(buf));
    if len < 8 {
        return 0;
    }
    let ntag: usize = buf_get_unchecked(buf, off) as usize + 256 * (buf_get_unchecked(
        buf,
        off + 1,
    ) as usize) + 65536 * (buf_get_unchecked(buf, off + 2) as usize) + 16777216 * (
    buf_get_unchecked(buf, off + 3) as usize);
    let tlen: usize = buf_get_unchecked(buf, off + 4) as usize + 256 * (buf_get_unchecked(
        buf,
        off + 5,
    ) as usize) + 65536 * (buf_get_unchecked(buf, off + 6) as usize) + 16777216 * (
    buf_get_unchecked(buf, off + 7) as usize);
    if ntag == 0 || tlen == 0 {
        return 0;
    }
    let mut acc: u64 = 0;
    let mut p: usize = 8;
    let mut o: usize = 0;
    // "The comparisons from here, with the accumulator as it stands, are all
    // the comparisons." The loop has a SINGLE exit -- the two stopping
    // conditions are both in the `while` condition rather than one of them
    // being a `break` -- so a plain `invariant` suffices and no
    // `invariant_except_break` is needed (p18 needed one on both its loops).
    while o < ntag && len - p >= 2 * tlen
        invariant
            o <= ntag,
            8 <= p <= len,
            len <= usize::MAX,
            1 <= tlen <= 0xffff_ffff,
            ntag <= 0xffff_ffff,
            off + len <= buf@.len(),
            buf@.len() <= usize::MAX,
            twalk(
                buf@,
                off as int,
                len as int,
                tlen as int,
                o as int,
                ntag as int,
                p as int,
                acc,
            ) == twalk(buf@, off as int, len as int, tlen as int, 0, ntag as int, 8, 0),
        decreases ntag - o,
    {
        let ghost acc_before = acc;
        let ghost p_before = p;
        let mut d: u8 = 0;
        let mut i: usize = 0;
        // THE TAG LOOP. Also a single exit. The invariant is one unfolding of
        // `xacc` per step; there is no lemma anywhere in this file.
        //
        // **This loop is the security property and Verus cannot see it.** What
        // the invariant below states is that `d` is the accumulator the spec
        // describes -- a fact about the VALUE. That the loop runs `tlen` times
        // whatever the data says is a fact about the TRACE, and there is no
        // clause here, or anywhere in Verus, that says it.
        while i < tlen
            invariant
                i <= tlen,
                o < ntag,
                p + 2 * tlen <= len,
                8 <= p <= len,
                1 <= tlen <= 0xffff_ffff,
                off + len <= buf@.len(),
                buf@.len() <= usize::MAX,
                xacc(buf@, (off + p) as int, tlen as int, i as int, d) == xacc(
                    buf@,
                    (off + p) as int,
                    tlen as int,
                    0,
                    0,
                ),
            decreases tlen - i,
        {
            d = d | (buf_get_unchecked(buf, off + p + i) ^ buf_get_unchecked(
                buf,
                off + p + tlen + i,
            ));
            i = i + 1;
        }
        // Ghost only: `i == tlen`, so `xacc` at `i` is its own base case, and
        // the loop invariant therefore identifies `d` with the spec's verdict.
        assert(xacc(buf@, (off + p) as int, tlen as int, tlen as int, d) == d);
        acc = if d == 0 {
            acc.wrapping_mul(31).wrapping_add(MATCH)
        } else {
            acc.wrapping_mul(31).wrapping_add(MISS)
        };
        p = p + 2 * tlen;
        o = o + 1;
        // Ghost only: unfold `twalk` once at the value it had on entry to this
        // iteration. Its `xacc` IS the accumulator the tag loop built.
        assert(twalk(
            buf@,
            off as int,
            len as int,
            tlen as int,
            o as int - 1,
            ntag as int,
            p_before as int,
            acc_before,
        ) == twalk(buf@, off as int, len as int, tlen as int, o as int, ntag as int, p as int, acc));
    }
    // Ghost only: the loop exited, so `twalk` at `(o, p)` is its own base case.
    assert(twalk(buf@, off as int, len as int, tlen as int, o as int, ntag as int, p as int, acc)
        == acc.wrapping_mul(31).wrapping_add(o as u64));
    acc.wrapping_mul(31).wrapping_add(o as u64)
}

// ---------------------------------------------------------------- driver ----
fn main() {
    let (n_iters, stride_w, bytes) = load_input();
    // SLB-DRIVER-BEGIN
    let n_blob: usize = bytes.len();
    let buf: &[u8] = bytes.as_slice();
    let mut acc: u64 = 0;
    if stride_w >= 8 && stride_w <= n_blob as u64 {
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
                8 <= stride <= n_blob,
                buf@.len() == n_blob,
                nwin == n_blob / stride,
                nwin >= 1,
            decreases n_iters - it,
        {
            // Ghost only: `k` must land inside the blob. Two nonlinear steps,
            // so Z3 needs both spelled out. Erases at compile time -- R4 and
            // R5 stay byte-identical.
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
            // Without it the postcondition is decoration -- deleting it
            // entirely still verifies, so nothing but mutation testing defends
            // it (`.memory/04-verus.md`). Ghost code erases, so the driver loop
            // stays byte-identical to R4's.
            assert(r == tag_fold(buf@, (k * stride) as int, stride as int));
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    emit(acc);
}

} // verus!
