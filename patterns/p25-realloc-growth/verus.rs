//! p25 rung R5 -- unsafe Rust + a Verus proof.
//!
//! This is unsafe.rs's exec code with the SAFETY comments turned into
//! obligations a verifier discharges. **What is new here is not the difficulty
//! of the obligation -- it is which obligation is left, and that is the row's
//! result.**
//!
//! ⚠⚠ **THE TEMPORAL OBLIGATION HAS NO ANALOGUE AT R5, BECAUSE NO RUNG ABOVE R1
//! CAN HOLD THE STALE INTERIOR POINTER.** `c/kernel.c`'s bug is a dereference of
//! `cur = &toks[curi]` after `realloc` has retired the block it points into.
//! Writing that in Rust needs a raw `*const u8` and a guard on
//! `curbase == toks.as_ptr()`, and **Verus cannot license the dereference**:
//!
//!   * reading `*cur` needs a `PointsTo` permission, and the permission for a
//!     `Vec`'s buffer is not obtainable through any vstd API at the pin;
//!   * the guard is an **address** comparison, and Verus's pointers carry
//!     PROVENANCE (`PtrData { addr, provenance, metadata }`), so
//!     `curbase == toks.as_ptr()` does not entail that the permission you hold
//!     is the one that names that byte. The guard is *exactly* the fact the
//!     proof would need and *exactly* the fact address equality does not give.
//!
//! So R4 and R5 save an INDEX, `realloc` copies, and the read is correct by
//! construction. What is left to prove is SAFETY (5) below -- `have ==> curi <
//! toks.len()` -- a spatial obligation that is trivial because a vector only
//! grows. **p25 is the first row in this tree where the ladder DELETES the bug
//! above R1 rather than making it provable**, and the honest statement of the
//! R5 result is that its obligation is smaller than p27's, p29's, p32's or
//! p34's. ../NOTES.md 6 states it in full and ../controls/rust_bug.py builds the
//! R4 that *does* hold the pointer, so the claim is measured rather than
//! asserted.
//!
//! ⚠ **THAT IS NOT A VACUOUS PROOF, AND THE MUTANT BATTERY IS WHAT SAYS SO.**
//! `../controls/proof_mutants.py` ships an ATTACK arm (delete the `curi <
//! toks.len()` conjunct from the loop invariant: `vec_get_unchecked`'s
//! precondition then fails), a VACUITY arm (a constant kernel body: the
//! postcondition fails, so the `ensures` is not discharged by anything), an X1
//! arm (strike the SAVE's re-establishment of the conjunct, which is the one
//! statement that makes it true), and a SPEC-WEAKEN arm.
//!
//! ⚠⚠ **THIS IS THE FIRST R5 IN THIS TREE TO CALL `Vec::push` IN EXEC CODE.**
//! Measured, not assumed: no other `verus.rs` in `patterns/` contains an exec
//! `.push(` on a `Vec` -- p14's, p27's, p28's, p29's and p34's are all `Seq`
//! pushes in ghost code. vstd's `assume_specification[Vec::push]` carries
//! `final(vec)@ == old(vec)@.push(value)` and **no `requires` at all**, so the
//! growth costs no trusted item and no precondition; `group_vec_axioms` is what
//! ties `vec.len()` to `vec@.len()`. ../NOTES.md 6a.
//!
//! **TCB: four items** -- `buf_get_unchecked`, `vec_get_unchecked`,
//! `load_input`, `emit`. That is **three fewer than p27's and p34's seven** and
//! one fewer than p32's five, and the reason is the same fact as above: this
//! rung allocates through `Vec`, whose allocation and deallocation are vstd's
//! problem rather than this file's, so there is no `rec_alloc`/`rec_free` pair
//! to trust. The two interesting items have verified twins (`harness/check.py`
//! step 5c-twin); `load_input` and `emit` state no `ensures` and have none.
//!
//! SAFETY (1): `off + len <= buf.len()` is the caller's structural
//!   precondition. Unchecked in unsafe.rs; discharged at the call site here.
//! SAFETY (2): `len >= 4` guards the window header.
//! SAFETY (3): the op is read only under `len - p >= 2` with `p <= len`.
//! SAFETY (4): `MAXCAP` bounds both vectors, so the epilogue's sum cannot
//!   overflow.
//! SAFETY (5): **WHAT IS LEFT OF THE TEMPORAL ONE.** The loop invariant carries
//!   `have ==> curi < toks@.len()`; `SAVE` re-establishes it with
//!   `a % toks.len()` under `toks.len() > 0`, and `Vec::push` can only lengthen
//!   `toks@`, so it survives every growth. That is what licenses
//!   `vec_get_unchecked(&toks, curi)`.

// Plain-Rust I/O helpers. Outside `verus!`, so Verus treats the whole module as
// external (external-by-default). Reached only through `load_input`/`emit`.
#[path = "../../common/driver.rs"]
mod driver;

use vstd::prelude::*;

verus! {

// `group_slice_axioms` gives `slice@.len() == spec_slice_len(slice)`, hence
// `slice@.len() <= usize::MAX` -- without it `off + len` cannot be shown not to
// overflow `usize`. `group_vec_axioms` is the same fact for a `Vec`
// (`axiom_spec_len`), and it is what makes `toks.len()` and `toks@.len()` the
// same number; no other pattern in this tree needs it, because no other R5
// grows a `Vec` in exec code. `lemma_u128_shr_is_div` and `lemma_mul_inequality`
// are the DRIVER's, not the kernel's.
broadcast use {
    vstd::slice::group_slice_axioms,
    vstd::std_specs::vec::group_vec_axioms,
    vstd::bits::lemma_u128_shr_is_div,
    vstd::arithmetic::mul::lemma_mul_inequality,
};

/// The largest capacity either vector reaches, a compile-time constant in every
/// rung. ⚠ In the C rungs it is an explicit bound beside a `tcap` that doubles
/// from `SEED`; in the four Rust rungs it is the whole of the capacity
/// discipline, because `MAXCAP == SEED * 2**k` makes `n < MAXCAP` accept exactly
/// the pushes the C form accepts. ../spec.md pins the equivalence.
pub const MAXCAP: usize = 64;

/// What a rejected operation folds. A compile-time constant in every rung.
pub const SENT: u64 = 251;

// ------------------------------------------------------------------ spec ----
/// The little-endian u32 at absolute byte position `p`, written out the way
/// every rung writes it: `b0 + 256*b1 + 65536*b2 + 16777216*b3`.
///
/// Spelled with `+` and `*` rather than `|` and `<<` on purpose
/// (`.memory/04-verus.md`): the two are the same function on bytes and compile
/// to the same instruction, but only the first is linear arithmetic.
pub open spec fn u32_at(buf: Seq<u8>, p: int) -> int {
    buf[p] as int + 256 * (buf[p + 1] as int) + 65536 * (buf[p + 2] as int) + 16777216 * (
    buf[p + 3] as int)
}

/// How many operations the window at `off` declares. **Declared, and it bounds
/// nothing** -- the cursor guard is what stops the walk.
pub open spec fn nops_at(buf: Seq<u8>, off: int) -> int {
    u32_at(buf, off)
}

/// THE ABSTRACT MACHINE, and the whole functional specification.
///
/// ⚠⚠ **There is no heap, no block, no capacity and no allocator in this
/// function at all** -- two byte sequences and one saved INTEGER index. That is
/// the row's specification-side statement: under the checked semantics
/// `realloc` COPIES, so the element the saved index names is the same element
/// before and after a growth, and where the bytes live cannot be observed.
/// `c/kernel.c`'s bug is precisely that a third representation -- the ADDRESS
/// the interior pointer holds -- can fall out of step with this one.
///
/// Note what this says and does not say: it describes the PROGRAM -- push until
/// the vector is full, save an index only into a non-empty token vector, read
/// only after a save, fold SENT otherwise -- and it says nothing about `nops`
/// being honest or the op stream being well formed. Every adversarial input is
/// inside this domain (`../spec.md`).
pub open spec fn run(
    buf: Seq<u8>,
    off: int,
    len: int,
    o: int,
    nops: int,
    p: int,
    toks: Seq<u8>,
    strs: Seq<u8>,
    have: bool,
    curi: int,
    acc: u64,
) -> u64
    decreases nops - o,
{
    if o >= nops || len - p < 2 {
        acc.wrapping_mul(31).wrapping_add((toks.len() + strs.len()) as u64)
    } else {
        let c = buf[off + p];
        let a = buf[off + p + 1];
        if c % 4 == 0 {
            if toks.len() < MAXCAP as int {
                run(
                    buf,
                    off,
                    len,
                    o + 1,
                    nops,
                    p + 2,
                    toks.push(a),
                    strs,
                    have,
                    curi,
                    acc.wrapping_mul(31).wrapping_add(a as u64),
                )
            } else {
                run(
                    buf,
                    off,
                    len,
                    o + 1,
                    nops,
                    p + 2,
                    toks,
                    strs,
                    have,
                    curi,
                    acc.wrapping_mul(31).wrapping_add(SENT),
                )
            }
        } else if c % 4 == 1 {
            if strs.len() < MAXCAP as int {
                run(
                    buf,
                    off,
                    len,
                    o + 1,
                    nops,
                    p + 2,
                    toks,
                    strs.push(a),
                    have,
                    curi,
                    acc.wrapping_mul(31).wrapping_add(a as u64),
                )
            } else {
                run(
                    buf,
                    off,
                    len,
                    o + 1,
                    nops,
                    p + 2,
                    toks,
                    strs,
                    have,
                    curi,
                    acc.wrapping_mul(31).wrapping_add(SENT),
                )
            }
        } else if c % 4 == 2 {
            if toks.len() > 0 {
                run(
                    buf,
                    off,
                    len,
                    o + 1,
                    nops,
                    p + 2,
                    toks,
                    strs,
                    true,
                    (a as int) % (toks.len() as int),
                    acc.wrapping_mul(31).wrapping_add(2),
                )
            } else {
                run(
                    buf,
                    off,
                    len,
                    o + 1,
                    nops,
                    p + 2,
                    toks,
                    strs,
                    have,
                    curi,
                    acc.wrapping_mul(31).wrapping_add(SENT),
                )
            }
        } else {
            if have {
                run(
                    buf,
                    off,
                    len,
                    o + 1,
                    nops,
                    p + 2,
                    toks,
                    strs,
                    have,
                    curi,
                    acc.wrapping_mul(31).wrapping_add(toks[curi] as u64),
                )
            } else {
                run(
                    buf,
                    off,
                    len,
                    o + 1,
                    nops,
                    p + 2,
                    toks,
                    strs,
                    have,
                    curi,
                    acc.wrapping_mul(31).wrapping_add(SENT),
                )
            }
        }
    }
}

/// What the kernel must return.
pub open spec fn parse_fold(buf: Seq<u8>, off: int, len: int) -> u64 {
    if len < 4 {
        0
    } else if nops_at(buf, off) == 0 {
        0
    } else {
        run(
            buf,
            off,
            len,
            0,
            nops_at(buf, off),
            4,
            Seq::empty(),
            Seq::empty(),
            false,
            0,
            0,
        )
    }
}

// --------------------------------------------------------------- trusted ----
// TRUSTED ITEM 1 of 4. The unchecked window read. vstd ships no specification
// for `<[T]>::get_unchecked`, and the standard library's documented contract is
// exactly this: if the caller guarantees `i < v.len()`, the call is defined and
// yields `v[i]`. Identical, character for character, to the accessor p01, p02,
// p03, p05, p06, p07, p11, p12, p13, p14, p16, p17, p27, p29, p32, p34 and p35
// ship.
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
// signature and same contract, character for character, implemented in *checked*
// code: a `requires` too weak to license `*v.get_unchecked(i)` is too weak to
// license `v[i]`, and Verus can see the second one. `#[cfg(slb_twin)]` is a cfg
// no measured build ever sets, so rustc strips it before codegen.
#[cfg(slb_twin)]
fn slb_twin_buf_get_unchecked(v: &[u8], i: usize) -> (r: u8)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    v[i]
}

// TRUSTED ITEM 2 of 4. The unchecked VECTOR read -- the one the safety line's
// obligation licenses. Same shape as item 1 over a `Vec<u8>` rather than a
// slice, because p25's token vector is a `Vec` and `Vec::get_unchecked` derefs
// to the slice method, which vstd also does not specify.
#[inline(always)]
#[verifier::external_body]
fn vec_get_unchecked(v: &Vec<u8>, i: usize) -> (r: u8)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    unsafe { *v.get_unchecked(i) }
}

// THE VERIFIED TWIN of trusted item 2.
#[cfg(slb_twin)]
fn slb_twin_vec_get_unchecked(v: &Vec<u8>, i: usize) -> (r: u8)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    v[i]
}

// TRUSTED ITEM 3 of 4. Argument parsing, file I/O and little-endian decoding,
// delegated to common/driver.rs so that all seven rungs read the file the same
// way. It states **no** `ensures` at all, deliberately: an `ensures` here would
// be an axiom about the contents of a file, which nothing can justify.
#[verifier::external_body]
fn load_input() -> (r: (u64, u64, Vec<u8>)) {
    let path = driver::arg_path();
    let inp = driver::load(&path);
    let (stride_w, bytes) = driver::head1_u64_bytes(&inp);
    (inp.n_iters, stride_w, bytes)
}

// TRUSTED ITEM 4 of 4. `println!` is not verifiable; no `ensures`. Counted with
// the three above -- every `external_body` item is TCB, not just the interesting
// one (`.memory/04-verus.md`).
#[verifier::external_body]
fn emit(acc: u64) {
    driver::emit(acc);
}

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> (r: u64)
    requires
        off + len <= buf@.len(),
    ensures
        r == parse_fold(buf@, off as int, len as int),
{
    // Ghost only: mentioning `spec_slice_len` fires vstd's `axiom_spec_len`,
    // which is what tells the SMT solver a slice length fits in a `usize`.
    assert(buf@.len() == vstd::slice::spec_slice_len(buf));
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
    while o < nops
        invariant_except_break
            o <= nops,
            p <= len,
            off + len <= buf@.len(),
            buf@.len() <= usize::MAX,
            toks@.len() <= MAXCAP,
            strs@.len() <= MAXCAP,
            // SAFETY (5), and the conjunct the ATTACK arm deletes.
            have ==> curi < toks@.len(),
            run(
                buf@,
                off as int,
                len as int,
                o as int,
                nops as int,
                p as int,
                toks@,
                strs@,
                have,
                curi as int,
                acc,
            ) == run(
                buf@,
                off as int,
                len as int,
                0,
                nops as int,
                4,
                Seq::empty(),
                Seq::empty(),
                false,
                0,
                0,
            ),
        ensures
            toks@.len() <= MAXCAP,
            strs@.len() <= MAXCAP,
            acc.wrapping_mul(31).wrapping_add((toks@.len() + strs@.len()) as u64) == run(
                buf@,
                off as int,
                len as int,
                0,
                nops as int,
                4,
                Seq::empty(),
                Seq::empty(),
                false,
                0,
                0,
            ),
        decreases nops - o,
    {
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
                // THE ONE STATEMENT THAT RE-ESTABLISHES SAFETY (5). The X1 mutant
                // strikes it and the loop invariant then fails.
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
    let (n_iters, stride_w, bytes) = load_input();
    // SLB-DRIVER-BEGIN
    let n_blob: usize = bytes.len();
    let buf: &[u8] = bytes.as_slice();
    let mut acc: u64 = 0;
    if stride_w >= 4 && stride_w <= n_blob as u64 {
        let stride: usize = stride_w as usize;
        let nwin: u64 = (n_blob / stride) as u64;
        let mut it: u64 = 0;
        // Ghost only: at least one whole window is present.
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
            assert(r == parse_fold(buf@, (k * stride) as int, stride as int));
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    emit(acc);
}

} // verus!
