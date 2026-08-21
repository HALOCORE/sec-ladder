//! p10 rung R5 -- unsafe + Verus proof.
//!
//! R4's exec code verbatim, plus the specs and proofs that discharge every
//! unchecked read in it.
//!
//! **THE OBLIGATION THAT MATTERS HERE IS EXACTLY THE ONE `c/kernel.c` GETS
//! WRONG.** The largest index the kernel forms is `off + 8 + taps + n - 1`, and
//! the whole of what keeps it inside `buf` is the guard `last >= len` plus the
//! kernel's one structural precondition. Change `>=` to `>` in this file --
//! the same one character, in the same comparison, that separates the two C
//! cells -- and Verus stops verifying: `9 verified, 1 errors`,
//! *invariant not satisfied before loop* on `8 + taps + n - 1 < len`.
//! ⚠ **That rejection lands one level EARLIER than the obligation the pattern
//! is about**, and saying so is the honest form of the claim: weaken BOTH
//! copies of that invariant as well and the rejection moves to
//! *precondition not satisfied* on `buf_get_unchecked`'s `i < v@.len()`,
//! which IS the out-of-bounds read. Both mutants are built by
//! `controls/gen_controls.py` (`m_fence`, `m_fence3`) and their exact error
//! text is in ../NOTES.md 10.
//!
//! ⚠ **AND THE SECOND GUARD IS LOAD-BEARING FOR A DIFFERENT REASON.**
//! `if n < taps` is not a memory-safety guard at all -- it is what stops
//! `n - 2*r` from underflowing, and Verus rejects the subtraction without it
//! (`possible arithmetic underflow/overflow`) before it ever gets to an index.
//! Two guards, two different failure modes, one line apart. That is why both
//! are pinned in every rung including R1: p10 models a fencepost and not a wild
//! index.
//!
//!     requires  off + len <= buf@.len()
//!
//! ONE clause, as on p03, p06, p11, p12, p14 and p18 and unlike p17. It is
//! structural -- about the shape of the buffer the driver built, not about its
//! contents -- so it holds on *every* input this benchmark runs,
//! `adversarial-*` included, and the gate checks it call by call. `n`, `r` and
//! every byte of the window are attacker data and none of them is an
//! assumption. In particular **there is no `requires` that `n` or `r` is
//! honest**; a precondition about the contents of a file is one no loader can
//! discharge (`.memory/02-bench-rules.md`) and it would delete every row this
//! pattern exists for.
//!
//! **THERE IS NO OVERFLOW OBLIGATION ON THE ACCUMULATOR, BY DESIGN AND NOT BY
//! LUCK.** TASK_057 predicted the obligations would be `r <= i < n - r` plus
//! non-overflow of the accumulator. The second one does not exist: `s` is a
//! `u32` accumulated with `wrapping_add`/`wrapping_mul` and the fold is the
//! project's usual wrapping Horner chain, so every arithmetic operation in the
//! kernel is total. What replaced it is the `n - 2*r` underflow above, which is
//! a *subtraction* obligation and is discharged by a guard rather than by a
//! bound on the data. ../NOTES.md 6.
//!
//! **The specification is written with `+` and `*` only** -- there is no `|`,
//! no `<<` and no `by (bit_vector)` anywhere in this file, and the only
//! multiplications are by literals or by the loop's own induction variables.
//! `dotp` and `fwalk` are *the folds the program performs*, not closed forms,
//! which is what keeps the solver in the fragment it is good at.
//!
//! TCB tally: ../NOTES.md 6. **Three** `external_body` items, **one** of them
//! with a `requires` -- the same shape as p18, and for the same structural
//! reason: p10's kernel performs exactly ONE kind of memory access, a byte read
//! of the input window. There is no scratch, no output buffer, no bulk copy and
//! no write of any kind.

use vstd::prelude::*;

// Plain-Rust I/O helpers. Outside `verus!`, so Verus treats the whole module as
// external (external-by-default). Reached only through `load_input`/`emit`.
#[path = "../../common/driver.rs"]
mod driver;

verus! {

// `group_slice_axioms` gives `slice@.len() == spec_slice_len(slice)`, hence
// `slice@.len() <= usize::MAX` -- without it `off + len` cannot be shown not to
// overflow `usize`. `lemma_u128_shr_is_div` turns `x >> 64` into `x / 2^64`,
// which is what the driver's multiply-shift barrier bound is about, and the mul
// group is what the driver's window-offset bound `k * stride + stride <= n_blob`
// needs; the KERNEL needs neither. p10 needs NO array group -- it has no array.
// p10 targets x86-64 only (`.memory/00-environment.md`), and it is the first
// pattern here that has to SAY so. Verus treats `usize` as
// architecture-independent by default, so `2 * r + 1` on a `usize` built from
// four bytes is `possible arithmetic underflow/overflow` on a hypothetical
// 32-bit target -- measured, not guessed (../NOTES.md 6). p07 dodged the same
// obligation by computing its length check in `u64`; p10 cannot, because
// ../spec.md pins the spelling `2 * r + 1` in all seven rungs and an
// `(r as u64)` cast would put R5 outside its own pattern's declaration. This
// declaration is CHECKED by Verus against the actual compilation target rather
// than assumed, so it is not an axiom and adds nothing to the TCB.
global size_of usize == 8;

broadcast use {
    vstd::slice::group_slice_axioms,
    vstd::bits::lemma_u128_shr_is_div,
    vstd::arithmetic::mul::lemma_mul_inequality,
};

// ------------------------------------------------------------------ spec ----
/// The little-endian u32 at absolute byte position `p`, written out the way
/// every rung writes it: `b0 + 256*b1 + 65536*b2 + 16777216*b3`.
///
/// Spelled with `+` and `*` rather than `|` and `<<` on purpose
/// (`.memory/04-verus.md`): the two are the same function on bytes and compile
/// to the same instruction, but only the first is linear arithmetic. On p10
/// that keeps the ENTIRE file inside linear arithmetic -- there is no other
/// bit operation anywhere in the kernel.
pub open spec fn u32_at(buf: Seq<u8>, p: int) -> int {
    buf[p] as int + 256 * (buf[p + 1] as int) + 65536 * (buf[p + 2] as int)
        + 16777216 * (buf[p + 3] as int)
}

/// ONE OUTPUT: the `2r+1`-tap dot product at window position `i`, accumulated
/// from tap `j` with running sum `s`.
///
/// A recursion and not a closed form, and wrapping after **every tap** rather
/// than once at the end -- because that is what the program does. `model.py`'s
/// simulation is the independent check on it: that one sums in Python's
/// unbounded integers and masks to 32 bits once per output, which is the other
/// way of saying the same thing, and the two agree on every input.
///
/// The sample index is `off + sb + i + j` and the coefficient index is
/// `off + 8 + j`, exactly as in the exec code -- so a rung that read the
/// coefficients in reverse, or slid the window by the wrong amount, does not
/// satisfy this.
pub open spec fn dotp(
    buf: Seq<u8>,
    off: int,
    sb: int,
    i: int,
    j: int,
    taps: int,
    s: u32,
) -> u32
    decreases taps - j,
{
    if j >= taps {
        s
    } else {
        dotp(
            buf,
            off,
            sb,
            i,
            j + 1,
            taps,
            s.wrapping_add(
                (buf[off + sb + i + j] as u32).wrapping_mul(buf[off + 8 + j] as u32),
            ),
        )
    }
}

/// THE MACHINE: outputs `i .. nout`, folding each dot product into `acc`.
///
/// The fold is order-sensitive (`acc*31 + s`), so a rung that emitted the
/// outputs in a different order cannot produce this value; and `nout` is folded
/// once at the end in `fir_fold`, so a rung that emitted a different NUMBER of
/// outputs -- which is exactly what an off-by-one does -- cannot either.
pub open spec fn fwalk(
    buf: Seq<u8>,
    off: int,
    sb: int,
    i: int,
    nout: int,
    taps: int,
    acc: u64,
) -> u64
    decreases nout - i,
{
    if i >= nout {
        acc
    } else {
        fwalk(
            buf,
            off,
            sb,
            i + 1,
            nout,
            taps,
            acc.wrapping_mul(31).wrapping_add(dotp(buf, off, sb, i, 0, taps, 0) as u64),
        )
    }
}

/// What the kernel returns.
///
/// The three early exits are the tests every rung keeps, R1 included: a window
/// too short to hold the header, a window that cannot hold one full tap
/// neighbourhood, and the fencepost. **R1 keeps all three** -- what it gets
/// wrong is the RELATION in the third, `last > len` where this says
/// `last >= len`, and that one character is the whole of the bug.
pub open spec fn fir_fold(buf: Seq<u8>, off: int, len: int) -> u64 {
    if len < 8 {
        0
    } else {
        let n = u32_at(buf, off);
        let r = u32_at(buf, off + 4);
        let taps = 2 * r + 1;
        if n < taps {
            0
        } else if 8 + taps + n - 1 >= len {
            0
        } else {
            fwalk(buf, off, 8 + taps, 0, n - 2 * r, taps, 0).wrapping_mul(31).wrapping_add(
                (n - 2 * r) as u64,
            )
        }
    }
}

// ------------------------------------------------------------------- TCB ----
// TRUSTED ITEM 1 of 3, and **the only one with a `requires`**. vstd ships no
// specification for `<[T]>::get_unchecked`, so this is the axiom that licenses
// the unchecked read of the window. It is sound because the standard library's
// documented contract for `get_unchecked` is exactly this: if the caller
// guarantees `i < v.len()`, the call is defined and yields `v[i]`. Identical,
// character for character, to the accessor p01, p02, p03, p05, p06, p07, p11,
// p12, p13, p14, p16, p17 and p18 ship.
//
// **On p10 this item's `requires` IS the pattern's bug**, which is a difference
// from p18 worth naming: p18's defect is an out-of-range SHIFT that no accessor
// precondition can exclude, so its trusted item had nothing to do with its bug.
// p10's defect is an out-of-bounds READ, and `i < v@.len()` is exactly what
// excludes it. ../NOTES.md 6.
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
// delegated to common/driver.rs so that all seven rungs read the file the same
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
        r == fir_fold(buf@, off as int, len as int),
{
    // Ghost only: mentioning `spec_slice_len` fires vstd's `axiom_spec_len`,
    // which is what tells the SMT solver a slice length fits in a `usize` --
    // needed to rule out `off + sb + i + j` overflowing. Erases at compile time.
    assert(buf@.len() == vstd::slice::spec_slice_len(buf));
    if len < 8 {
        return 0;
    }
    let n: usize = buf_get_unchecked(buf, off) as usize + 256 * (buf_get_unchecked(
        buf,
        off + 1,
    ) as usize) + 65536 * (buf_get_unchecked(buf, off + 2) as usize) + 16777216 * (
    buf_get_unchecked(buf, off + 3) as usize);
    let r: usize = buf_get_unchecked(buf, off + 4) as usize + 256 * (buf_get_unchecked(
        buf,
        off + 5,
    ) as usize) + 65536 * (buf_get_unchecked(buf, off + 6) as usize) + 16777216 * (
    buf_get_unchecked(buf, off + 7) as usize);
    // `2 * r + 1` and `8 + taps + n - 1` are the ONLY two `usize`-overflow
    // obligations in this kernel -- there is no accumulator overflow obligation
    // at all, because every arithmetic operation on `s` and `acc` is wrapping.
    // Both discharge from the `global size_of usize == 8` above with no ghost
    // help; an earlier draft carried `assert(n <= 0xffff_ffff)` and
    // `assert(r <= 0xffff_ffff)` here, which were needed BEFORE that
    // declaration existed and are dead after it (measured both ways,
    // ../NOTES.md 6).
    let taps: usize = 2 * r + 1;
    // THE WINDOW GUARD, present in every rung. Without it `n - 2 * r` below is
    // `possible arithmetic underflow/overflow` and p10 would be modelling a
    // wild index rather than a fencepost.
    if n < taps {
        return 0;
    }
    let last: usize = 8 + taps + n - 1;
    // THE SAFETY LINE. c/kernel.c writes `last > len`. This is also the whole
    // of what discharges every `buf_get_unchecked` below.
    if last >= len {
        return 0;
    }
    let nout: usize = n - 2 * r;
    let sb: usize = 8 + taps;
    let mut acc: u64 = 0;
    let mut i: usize = 0;
    // "The outputs from here, with the accumulator as it stands, are all the
    // outputs." This loop exits exactly ONE way (`i == nout`), so a plain
    // `invariant` suffices -- p18 needed `invariant_except_break` on both of its
    // loops because both could exit early; p10's cannot.
    while i < nout
        invariant
            i <= nout,
            nout == n - 2 * r,
            taps == 2 * r + 1,
            sb == 8 + taps,
            n >= taps,
            8 + taps + n - 1 < len,
            off + len <= buf@.len(),
            buf@.len() <= usize::MAX,
            fwalk(buf@, off as int, sb as int, i as int, nout as int, taps as int, acc)
                == fwalk(buf@, off as int, sb as int, 0, nout as int, taps as int, 0),
        decreases nout - i,
    {
        let ghost acc_before = acc;
        let mut s: u32 = 0;
        let mut j: usize = 0;
        // THE TAP LOOP. Also a single exit. The invariant is one unfolding of
        // `dotp` per step; there is no lemma anywhere in this file.
        while j < taps
            invariant
                j <= taps,
                i < nout,
                nout == n - 2 * r,
                taps == 2 * r + 1,
                sb == 8 + taps,
                n >= taps,
                8 + taps + n - 1 < len,
                off + len <= buf@.len(),
                buf@.len() <= usize::MAX,
                dotp(buf@, off as int, sb as int, i as int, j as int, taps as int, s)
                    == dotp(buf@, off as int, sb as int, i as int, 0, taps as int, 0),
            decreases taps - j,
        {
            s = s.wrapping_add(
                (buf_get_unchecked(buf, off + sb + i + j) as u32).wrapping_mul(
                    buf_get_unchecked(buf, off + 8 + j) as u32,
                ),
            );
            j = j + 1;
        }
        // Ghost only: `j == taps`, so `dotp` at `j` is its own base case.
        assert(dotp(buf@, off as int, sb as int, i as int, taps as int, taps as int, s) == s);
        acc = acc.wrapping_mul(31).wrapping_add(s as u64);
        // Ghost only: unfold `fwalk` once at the value it had on entry to this
        // iteration. Its `dotp` IS the sum the tap loop built.
        assert(fwalk(buf@, off as int, sb as int, i as int, nout as int, taps as int, acc_before)
            == fwalk(buf@, off as int, sb as int, i as int + 1, nout as int, taps as int, acc));
        i = i + 1;
    }
    // Ghost only: `i == nout`, so `fwalk` at `i` is its own base case.
    assert(fwalk(buf@, off as int, sb as int, nout as int, nout as int, taps as int, acc) == acc);
    acc.wrapping_mul(31).wrapping_add(nout as u64)
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
        // is the guard immediately above, and integer division only rounds down,
        // so `n_blob / stride >= 1` -- but that is a fact about division and Z3
        // needs the lemma named.
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
            // Ghost only: `k` must land inside the blob. Two nonlinear steps, so
            // Z3 needs both spelled out. Erases at compile time -- R4 and R5
            // stay byte-identical.
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
            // Without it the postcondition is decoration -- deleting it entirely
            // still verifies, so nothing but mutation testing defends it
            // (`.memory/04-verus.md`). Ghost code erases, so the driver loop
            // stays byte-identical to R4's.
            assert(r == fir_fold(buf@, (k * stride) as int, stride as int));
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    emit(acc);
}

} // verus!
