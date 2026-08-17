//! p16 rung R5 -- unsafe + Verus proof.
//!
//! R4's exec code verbatim, plus the specs and proofs that discharge every
//! unchecked read in it. What the proof is *about*, in one line: the kernel's
//! two runtime tests are jointly sufficient, so a walk whose trip count and
//! whose every step come from attacker data never reads outside the window.
//!
//! **Read this before judging the `ensures`.** p02's security property was
//! statable as a postcondition -- an equality on the whole destination buffer,
//! which said "nothing outside the copied prefix moved". **p16's is not.** This
//! kernel writes nothing; the harm it models is a *read*, and "no byte outside
//! the window was read" is not a property of the return value, because a kernel
//! could read out of bounds and discard the byte.
//!
//! So for this pattern the memory-safety claim rests **entirely on the
//! discharged `requires` of the trusted accessor**, not on any `ensures`. Every
//! `get_unchecked(buf, i)` below carries the obligation `i < buf@.len()`, and
//! *that* -- proved at every one of the call sites, for indices the attacker's
//! own length fields chose -- is the security property. The kernel's `ensures`
//! exists to make the proof non-vacuous and to tie the value to `model.py`; it
//! is not the safety argument and must not be presented as one. NOTES.md 5
//! says so at length, and it is why `harness/check.py`'s clause-deletion and
//! verified-twin stages matter more here than on any earlier pattern.
//!
//! The `requires` is
//!
//!     off + len <= buf@.len()
//!
//! and nothing else: the window is inside the blob. That is structural -- it is
//! about the shape of the buffer the driver built, not about its contents -- so
//! it holds on *every* input this benchmark runs, `adversarial-*` included, and
//! the gate checks it call by call. Every `vlen` a `u16` can express is an
//! argument of the problem, not an assumption.
//!
//! TCB tally: NOTES.md. Three `external_body` items, all listed there
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
// group is what the window-offset bound `k * stride + stride <= n_blob` needs:
// both steps of it are nonlinear.
broadcast use {
    vstd::slice::group_slice_axioms,
    vstd::bits::lemma_u128_shr_is_div,
    vstd::arithmetic::mul::lemma_mul_inequality,
};

// ------------------------------------------------------------------ spec ----
/// The value length the record at `p` declares: a little-endian u16 prefix.
/// Attacker data. Every value in `0 ..= 65535` is possible and the kernel is
/// total on all of them -- including the ones that make the record overrun the
/// window, which is the whole pattern.
pub open spec fn vlen_at(buf: Seq<u8>, p: int) -> int {
    buf[p + 1] as int + 256 * (buf[p + 2] as int)
}

/// `acc`, with `s[from .. from+n)` folded into it left to right. Horner with a
/// multiplier of 31; `u64::wrapping_mul`/`wrapping_add` are usable in spec
/// position because vstd marks them `#[verifier::allow_in_spec]`.
pub open spec fn fold_bytes(s: Seq<u8>, from: int, n: int, acc: u64) -> u64
    decreases n,
{
    if n <= 0 {
        acc
    } else {
        fold_bytes(s, from, n - 1, acc).wrapping_mul(31).wrapping_add(
            s[from + n - 1] as u64,
        )
    }
}

/// The walk itself: from `p` to `end`, carrying `(acc, nrec)`.
///
/// This is the function p16 exists to be about, and its shape is the pattern.
/// It is **recursive rather than a fold over a known range**, because the
/// number of steps and the position of every step come from bytes inside the
/// buffer. `decreases end - p` is what makes it well founded, and the reason it
/// works is that a record occupies `3 + vlen >= 3` bytes: progress is
/// guaranteed by the *header*, not by the length field.
///
/// Note that the tag byte is folded **before** the fit test, so a walk stopped
/// by a malformed record still carries that record's tag. Every rung does the
/// same; it is why an unparsable chain and a chain one byte shorter give
/// different answers.
pub open spec fn tlv_walk(buf: Seq<u8>, p: int, end: int, acc: u64, nrec: u64) -> (u64, u64)
    decreases end - p,
{
    if end - p >= 3 {
        let a1 = acc.wrapping_mul(31).wrapping_add(buf[p] as u64);
        if vlen_at(buf, p) > end - (p + 3) {
            (a1, nrec)
        } else {
            tlv_walk(
                buf,
                p + 3 + vlen_at(buf, p),
                end,
                fold_bytes(buf, p + 3, vlen_at(buf, p), a1),
                nrec.wrapping_add(1),
            )
        }
    } else {
        (acc, nrec)
    }
}

/// What the kernel returns: the walk over `buf[off .. off+len)`, with the
/// record count mixed into the checksum so that a walker which mis-parses the
/// chain but folds the same bytes cannot produce the same answer.
pub open spec fn tlv_fold(buf: Seq<u8>, off: int, len: int) -> u64 {
    tlv_walk(buf, off, off + len, 0, 0).0.wrapping_mul(31).wrapping_add(
        tlv_walk(buf, off, off + len, 0, 0).1,
    )
}

// ------------------------------------------------------------------- TCB ----
// TRUSTED ITEM 1 of 3, and **the whole of this pattern's security argument**.
// vstd ships no specification for `<[T]>::get_unchecked`, so this is the axiom
// that licenses the unchecked read. It is sound because the standard library's
// documented contract for `get_unchecked` is exactly this: if the caller
// guarantees `i < v.len()`, the call is defined and yields `v[i]`.
//
// The `requires` is not decoration and it is not one obligation among several.
// p16 has no `ensures` that states memory safety -- a read-only kernel cannot
// have one (see the module comment) -- so `i < v@.len()`, discharged at every
// call site, IS the property. Three of those call sites are the header reads,
// discharged from `end - p >= 3`; the fourth is the value fold, discharged from
// the fit test, which is the line c/kernel.c deletes.
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
// `precondition not met: index in bounds for this access`; that off-by-one
// passed the entire gate before this stage existed (TASK_008_REVIEW), because
// 5a only asks whether the clause mentions every parameter and 5c-req only
// whether it is a tautology, and `i <= v@.len()` is neither trivial nor silent.
//
// **Be honest about what a green twin means here.** p16's accessor is the same
// single-clause `i < v@.len()` p01 and p02 ship, so 5c-twin passing on p16 is
// *not* evidence that anything hard was checked -- there is no missing conjunct
// for it to find, because there is only one conjunct. The mechanism's value
// accrues from p17 on, where a multi-clause accessor can be short one. What
// p16 does contribute is the *negative* control: NOTES.md 7 shows this twin
// failing on `i <= v@.len()`, for this pattern's own accessor rather than
// p02's, which is precisely the off-by-one OOB read the pattern models.
//
// `#[cfg(slb_twin)]` is a cfg no build ever sets, so rustc strips this before
// codegen: the twin costs zero instructions structurally.
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
//
// One `ensures`. It is the *value*, not the safety property -- see the module
// comment. What makes it worth having anyway: it is what stops the proof being
// vacuous, it is what `model.py` re-derives independently, and it is what forces
// the loop invariants to describe the walk rather than merely bound the indices.
// A kernel that returned 0 unconditionally would satisfy every bounds
// obligation in this file.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> (r: u64)
    requires
        off + len <= buf@.len(),
    ensures
        r == tlv_fold(buf@, off as int, len as int),
{
    // Ghost only: mentioning `spec_slice_len` fires vstd's `axiom_spec_len`,
    // which is what tells the SMT solver a slice length fits in a `usize` --
    // needed to rule out `off + len` overflowing. Erases at compile time.
    assert(buf@.len() == vstd::slice::spec_slice_len(buf));
    let mut p: usize = off;
    let end: usize = off + len;
    let mut acc: u64 = 0;
    let mut nrec: u64 = 0;
    // `invariant_except_break` + `ensures`, because the walk exits two ways and
    // Verus cannot assume the loop condition is false after a `break`. The
    // invariant is the interesting line: *the walk from here, with what we have
    // accumulated, is the whole walk*. That is the only form the invariant can
    // take, because there is no closed-form description of where the walk will
    // be after i steps -- the positions are the data.
    while end - p >= 3
        invariant_except_break
            off <= p <= end,
            end == off + len,
            end <= buf@.len(),
            buf@.len() <= usize::MAX,
            tlv_walk(buf@, p as int, end as int, acc, nrec) == tlv_walk(
                buf@,
                off as int,
                end as int,
                0,
                0,
            ),
        ensures
            acc == tlv_walk(buf@, off as int, end as int, 0, 0).0,
            nrec == tlv_walk(buf@, off as int, end as int, 0, 0).1,
        decreases end - p,
    {
        // Ghost only: the accumulator before the tag is folded, so that the
        // `break` arm below can name the value the invariant is stated about.
        let ghost a0: u64 = acc;
        acc = acc.wrapping_mul(31).wrapping_add(get_unchecked(buf, p) as u64);
        let vlen: usize = get_unchecked(buf, p + 1) as usize + 256 * (get_unchecked(
            buf,
            p + 2,
        ) as usize);
        if vlen > end - (p + 3) {
            break;
        }
        // Ghost only: the accumulator after the tag and before the value, which
        // is what `fold_bytes` in `tlv_walk` starts from.
        let ghost a1: u64 = acc;
        let mut j: usize = 0;
        while j < vlen
            invariant
                j <= vlen,
                p + 3 + vlen <= end,
                end <= buf@.len(),
                acc == fold_bytes(buf@, (p + 3) as int, j as int, a1),
            decreases vlen - j,
        {
            acc = acc.wrapping_mul(31).wrapping_add(get_unchecked(buf, p + 3 + j) as u64);
            j = j + 1;
        }
        p = p + 3 + vlen;
        nrec = nrec.wrapping_add(1);
    }
    acc.wrapping_mul(31).wrapping_add(nrec)
}

// ---------------------------------------------------------------- driver ----
fn main() {
    let (n_iters, stride_w, bytes) = load_input();
    // SLB-DRIVER-BEGIN
    let n_blob: usize = bytes.len();
    let buf: &[u8] = bytes.as_slice();
    let mut acc: u64 = 0;
    if stride_w >= 3 && stride_w <= n_blob as u64 {
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
                3 <= stride <= n_blob,
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
            // stays byte-identical to R4's; `harness/dloop.py` exempts ghost
            // statements from the driver diff exactly as it exempts
            // `invariant`/`decreases`.
            assert(r == tlv_fold(buf@, (k * stride) as int, stride as int));
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    emit(acc);
}

} // verus!
