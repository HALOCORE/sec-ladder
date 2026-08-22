//! p38 rung R5 -- unsafe + Verus proof.
//!
//! R4's exec code verbatim, plus the specs and proofs that discharge every
//! unchecked read and write in it.
//!
//! ⚠⚠ **VERUS HAS NOTHING TO SAY ABOUT TYPE-BASED ALIASING EITHER, AND ON p38
//! THAT IS NOT A GAP.** It is p47's shape one axis over, and the reason is
//! different and worth stating precisely:
//!
//!   * On p47 the property (constant time) is **inexpressible** in the
//!     assertion language -- there is no term denoting a trace.
//!   * On p38 the property is **vacuous**: strict aliasing is a rule of the C
//!     abstract machine, and this program is not in C. Rust has no type-based
//!     aliasing rule, `&mut`'s `noalias` is uniqueness rather than type
//!     identity, and there is consequently no obligation for Verus to
//!     discharge. **The proof does not fail to exclude p38's bug; the bug does
//!     not exist in the language the proof is about.**
//!
//! So the honest statement, and it is the deliverable rather than a caveat:
//! **every obligation in this file is a SPATIAL one** -- `i < v@.len()` on the
//! window, `i < 256` on the scratch -- and what excludes p38's harm is not any
//! of them but the fact that the read below observes the write above, which is
//! a property of the *language* and is assumed, not proved, by every rung here
//! including R2. ../NOTES.md 9 gives the full statement, and
//! `controls/proof_mutants.py` shows two mutants that DO fail, both spatial.
//!
//!     requires  off + len <= buf@.len()
//!
//! ONE clause, as on p03, p06, p10, p11, p12, p14, p18, p27 and p47 and unlike
//! p17. It is structural -- about the shape of the buffer the driver built, not
//! about its contents -- so it holds on *every* input this benchmark runs,
//! `adversarial-*` included, and the gate checks it call by call. `nrec` and
//! every record word are attacker data and none of them is an assumption. In
//! particular **there is no `requires` that `nrec` or any record length is
//! honest**; a precondition about the contents of a file is one no loader can
//! discharge (`.memory/02-bench-rules.md`), and the CLAMP is what stops the
//! walk instead.
//!
//! **THE SPEC CARRIES THE CLAMP AS A SEQUENCE UPDATE**, `rwalk`'s `sc2`, rather
//! than as `min(declared, room)` in a local. That is deliberate: the exec code
//! writes the clamped length back into the scratch and reads it out again, and
//! the whole of p38 is that a C compiler may answer the second read from before
//! the first write. A specification written as a `min` would have described a
//! program in which that question cannot be asked. `model.py`'s `_rwalk`
//! mirrors this function, update for update.
//!
//! The little-endian header is decoded with `+` and `*` rather than `|` and
//! `<<` (`.memory/04-verus.md`): the two are the same function on bytes and
//! compile to the same instruction, but only the first is linear arithmetic.
//! **There is no bit operation anywhere in this file**, so there is no
//! `by (bit_vector)`.
//!
//! TCB tally: ../NOTES.md 7. **Five** `external_body` items, **three** of them
//! with contracts -- the same shape as p03 and for the same structural reason:
//! p38's kernel has two buffers and one of them is written.

use vstd::prelude::*;

// Plain-Rust I/O helpers. Outside `verus!`, so Verus treats the whole module
// as external (external-by-default). Reached only through `load_input`/`emit`.
#[path = "../../common/driver.rs"]
mod driver;

verus! {

// `group_slice_axioms` gives `slice@.len() == spec_slice_len(slice)`, hence
// `slice@.len() <= usize::MAX`. `group_array_axioms` gives
// `sc@.len() == SCRATCH_W` for a `[u16; SCRATCH_W]` and the fill axiom for
// `[0; SCRATCH_W]` -- p03 is the other pattern here with a fixed-size array.
// `lemma_u128_shr_is_div` turns `x >> 64` into `x / 2^64`, the driver's
// multiply-shift barrier bound, and the mul group is what the driver's
// window-offset bound needs; the KERNEL needs neither.
//
// p38 targets x86-64 only (`.memory/00-environment.md`). Verus treats `usize`
// as architecture-independent by default, so `i + 2 + 2 * n` on a `usize` built
// from two file words is `possible arithmetic overflow` on a hypothetical
// 32-bit target. This declaration is CHECKED by Verus against the actual
// compilation target rather than assumed, so it is not an axiom and adds
// nothing to the TCB.
global size_of usize == 8;

broadcast use {
    vstd::slice::group_slice_axioms,
    vstd::array::group_array_axioms,
    vstd::bits::lemma_u128_shr_is_div,
    vstd::arithmetic::mul::lemma_mul_inequality,
};

/// The decode scratch, in words. A compile-time constant in every rung.
///
/// A `const` inside `verus!` is its own obligation (`.memory/04-verus.md`,
/// measured on p08's `SCR`), so this contributes 1 to the count pinned in
/// ../spec.md and the decomposition there says so.
pub const SCRATCH_W: usize = 256;

// ------------------------------------------------------------------ spec ----
/// The little-endian u32 at absolute byte position `p`, written out the way
/// every rung writes it: `b0 + 256*b1 + 65536*b2 + 16777216*b3`.
pub open spec fn u32_at(buf: Seq<u8>, p: int) -> int {
    buf[p] as int + 256 * (buf[p + 1] as int) + 65536 * (buf[p + 2] as int)
        + 16777216 * (buf[p + 3] as int)
}

/// How many words of the record stream the parser decodes: `(len-4)/2`,
/// truncated to the scratch. A property of the parser, in every rung and in
/// model.py.
pub open spec fn nw_of(len: int) -> int {
    if (len - 4) / 2 > SCRATCH_W as int {
        SCRATCH_W as int
    } else {
        (len - 4) / 2
    }
}

/// The decode scratch as the kernel leaves it before the walk: word `j` of the
/// record stream for `j < nw_of(len)`, and zero above that -- because safe Rust
/// has no uninitialised array and all four Rust rungs write `[0u16; SCRATCH_W]`.
/// (C's `uint16_t sc[256];` is not initialised; nothing in the defined
/// semantics reads those slots, and the whole of p38 is what happens when a
/// compiler decides otherwise.)
pub open spec fn dec(buf: Seq<u8>, off: int, len: int) -> Seq<u16> {
    Seq::new(
        SCRATCH_W as nat,
        |j: int|
            if 0 <= j < nw_of(len) {
                (buf[off + 4 + 2 * j] as int + 256 * (buf[off + 5 + 2 * j] as int)) as u16
            } else {
                0u16
            },
    )
}

/// The payload fold: words `k .. cnt` of the record whose payload starts at
/// scratch word `base`, Horner-folded into `acc`.
pub open spec fn wfold(sc: Seq<u16>, base: int, k: int, cnt: int, acc: u64) -> u64
    decreases cnt - k,
{
    if k >= cnt {
        acc
    } else {
        wfold(sc, base, k + 1, cnt, acc.wrapping_mul(31).wrapping_add(sc[base + k] as u64))
    }
}

/// THE MACHINE: records `o .. nrec` from scratch word `i`, carrying the scratch
/// contents and the accumulator.
///
/// **`sc2` is the clamp** -- the record's declared length written back as the
/// two 16-bit halves the format defines it to be -- and `n` is read out of
/// `sc2` and not computed as a `min`. See the module comment: that is the
/// distinction p38 exists to measure, and a `min` would have specified it away.
///
/// The walk stops for either of two reasons -- the declared count is exhausted,
/// or fewer than two words remain -- and `o` is folded once at the end, so a
/// rung that walked a different NUMBER of records cannot produce this value.
pub open spec fn rwalk(sc: Seq<u16>, nw: int, nrec: int, i: int, o: int, acc: u64) -> u64
    decreases nrec - o,
{
    if o >= nrec || i + 2 > nw {
        acc.wrapping_mul(31).wrapping_add(o as u64)
    } else {
        let room = (nw - i - 2) / 2;
        let d = sc[i] as int + 65536 * (sc[i + 1] as int);
        let sc2 = if d > room {
            sc.update(i, (room % 65536) as u16).update(i + 1, (room / 65536) as u16)
        } else {
            sc
        };
        let n = sc2[i] as int + 65536 * (sc2[i + 1] as int);
        rwalk(sc2, nw, nrec, i + 2 + 2 * n, o + 1, wfold(sc2, i + 2, 0, 2 * n, acc))
    }
}

/// What the kernel returns.
///
/// The two early exits are the tests every rung keeps, R1 included: a window
/// too short to hold the header, and a header declaring no records. **R1 keeps
/// both, and R1 keeps the clamp inside `rwalk` too** -- what it gets wrong is
/// none of them.
pub open spec fn rec_fold(buf: Seq<u8>, off: int, len: int) -> u64 {
    if len < 4 {
        0
    } else {
        let nrec = u32_at(buf, off);
        if nrec == 0 {
            0
        } else {
            rwalk(dec(buf, off, len), nw_of(len), nrec, 0, 0, 0)
        }
    }
}

// ------------------------------------------------------------------- TCB ----
// TRUSTED ITEM 1 of 5. vstd ships no specification for
// `<[T]>::get_unchecked`, so this is the axiom that licenses the unchecked read
// of the input window. It is sound because the standard library's documented
// contract for `get_unchecked` is exactly this: if the caller guarantees
// `i < v.len()`, the call is defined and yields `v[i]`. Identical, character
// for character, to the accessor sixteen other patterns here ship.
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

// TRUSTED ITEM 2 of 5. The scratch is a fixed-size `[u16; SCRATCH_W]`, so the
// bound is the array's type-level length rather than a runtime `len()`.
//
// The `requires` is ONE conjunct and NOT `i < v@.len(), v@.len() == 256`: for a
// `&[u16; 256]` the second is a tautology discharged from the parameter type
// alone by vstd's `array_len_matches_n`, and a tautological conjunct on a
// TRUSTED item is the shape `.memory/04-verus.md` warns about. p03 shipped the
// same accessor for `[u64; 64]` and the gate's 5c-req probe is what found it.
#[inline(always)]
#[verifier::external_body]
fn sc_get_unchecked(v: &[u16; 256], i: usize) -> (r: u16)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    unsafe { *v.get_unchecked(i) }
}

// THE VERIFIED TWIN of trusted item 2.
#[cfg(slb_twin)]
fn slb_twin_sc_get_unchecked(v: &[u16; 256], i: usize) -> (r: u16)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    v[i]
}

// TRUSTED ITEM 3 of 5, and the one that writes. **This is the accessor p38's
// clamp goes through**, and the `ensures` is a whole-sequence equality
// (`update`) rather than a statement about slot `i` alone, so it says both
// "slot `i` became `x`" and "nothing else moved".
//
// ⚠ **AND IT IS WHERE THE LANGUAGE DIFFERENCE LIVES.** The corresponding C
// expression is `r[0] = (uint16_t)(v % 65536)`, and in C a *later* read of the
// same storage through a `uint32_t` lvalue need not observe it. This `ensures`
// says it does, and it is not an assumption about the write -- it is Rust's
// memory model, which has no type-based aliasing rule for the axiom to be
// wrong about. ../NOTES.md 9.
//
// `x` is a pure VALUE parameter -- written, never used as an address or a
// length -- so it has no precondition, and ../spec.md's
// `verus.unsafe_justifications` says so and the gate shouts it every run.
#[inline(always)]
#[verifier::external_body]
fn sc_set_unchecked(v: &mut [u16; 256], i: usize, x: u16)
    requires
        i < old(v)@.len(),
    ensures
        final(v)@ == old(v)@.update(i as int, x),
{
    unsafe {
        *v.get_unchecked_mut(i) = x;
    }
}

// THE VERIFIED TWIN of trusted item 3. `v[i] = x` is the checked stand-in for
// `*v.get_unchecked_mut(i) = x`; weaken the shared `requires` and Verus rejects
// the indexed store.
#[cfg(slb_twin)]
fn slb_twin_sc_set_unchecked(v: &mut [u16; 256], i: usize, x: u16)
    requires
        i < old(v)@.len(),
    ensures
        final(v)@ == old(v)@.update(i as int, x),
{
    v[i] = x;
}

// TRUSTED ITEM 4 of 5. Argument parsing, file I/O and little-endian decoding,
// delegated to common/driver.rs so that all eight rungs read the file the same
// way. It states **no** `ensures` at all, deliberately: an `ensures` here would
// be an axiom about the contents of a file, which nothing can justify. It
// contains no `unsafe`, so it stays outside the twin regime.
#[verifier::external_body]
fn load_input() -> (r: (u64, u64, Vec<u8>)) {
    let path = driver::arg_path();
    let inp = driver::load(&path);
    let (stride_w, bytes) = driver::head1_u64_bytes(&inp);
    (inp.n_iters, stride_w, bytes)
}

// TRUSTED ITEM 5 of 5. `println!` is not verifiable; no `ensures`. Counted with
// the four above -- every `external_body` item is TCB, not just the interesting
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
        r == rec_fold(buf@, off as int, len as int),
{
    // Ghost only: mentioning `spec_slice_len` fires vstd's `axiom_spec_len`,
    // which is what tells the SMT solver a slice length fits in a `usize`.
    assert(buf@.len() == vstd::slice::spec_slice_len(buf));
    if len < 4 {
        return 0;
    }
    let nrec: usize = buf_get_unchecked(buf, off) as usize + 256 * (buf_get_unchecked(
        buf,
        off + 1,
    ) as usize) + 65536 * (buf_get_unchecked(buf, off + 2) as usize) + 16777216 * (
    buf_get_unchecked(buf, off + 3) as usize);
    if nrec == 0 {
        return 0;
    }
    let mut sc: [u16; 256] = [0; 256];
    let mut nw: usize = (len - 4) / 2;
    if nw > SCRATCH_W {
        nw = SCRATCH_W;
    }
    let mut j: usize = 0;
    // THE DECODE LOOP. "Words 0..j of the scratch are already the record
    // stream's words." The tail stays zero, which is what makes the final
    // `=~=` below an equality of whole sequences.
    while j < nw
        invariant
            j <= nw,
            nw == nw_of(len as int),
            nw <= SCRATCH_W,
            4 <= len,
            sc@.len() == SCRATCH_W,
            off + len <= buf@.len(),
            buf@.len() <= usize::MAX,
            forall|t: int| #![trigger sc@[t]] 0 <= t < j ==> sc@[t] == dec(buf@, off as int, len as int)[t],
            forall|t: int| #![trigger sc@[t]] j <= t < SCRATCH_W ==> sc@[t] == 0u16,
        decreases nw - j,
    {
        let w: u16 = buf_get_unchecked(buf, off + 4 + 2 * j) as u16 + 256 * (buf_get_unchecked(
            buf,
            off + 5 + 2 * j,
        ) as u16);
        sc_set_unchecked(&mut sc, j, w);
        j = j + 1;
    }
    // Ghost only: the decoded scratch IS the specification's `dec`.
    assert(sc@ =~= dec(buf@, off as int, len as int));
    let mut acc: u64 = 0;
    let mut i: usize = 0;
    let mut o: usize = 0;
    // THE WALK. "The records from here, with the scratch and the accumulator we
    // have, are the whole walk." Same relational shape as p03's operation loop
    // -- and, like p03's, the state it carries is a SEQUENCE the loop mutates.
    while o < nrec && i + 2 <= nw
        invariant
            o <= nrec,
            i <= nw,
            nw <= SCRATCH_W,
            sc@.len() == SCRATCH_W,
            rwalk(sc@, nw as int, nrec as int, i as int, o as int, acc) == rwalk(
                dec(buf@, off as int, len as int),
                nw as int,
                nrec as int,
                0,
                0,
                0,
            ),
        decreases nrec - o,
    {
        let ghost sc_before = sc@;
        let ghost acc_before = acc;
        let ghost i_before = i as int;
        let room: usize = (nw - i - 2) / 2;
        let d: usize = sc_get_unchecked(&sc, i) as usize + 65536 * (sc_get_unchecked(
            &sc,
            i + 1,
        ) as usize);
        // THE CLAMP, written through `u16` lvalues.
        if d > room {
            let lo: u16 = (room % 65536) as u16;
            let hi: u16 = (room / 65536) as u16;
            sc_set_unchecked(&mut sc, i, lo);
            sc_set_unchecked(&mut sc, i + 1, hi);
        }
        // THE RE-READ. In C this load may be answered from before the two
        // stores above; in Rust it may not, and no `unsafe` changes that.
        let n: usize = sc_get_unchecked(&sc, i) as usize + 65536 * (sc_get_unchecked(
            &sc,
            i + 1,
        ) as usize);
        // Ghost only: `room <= 127 < 65536`, so the clamp's two halves read
        // back as `room` exactly, and `n <= room` on both branches. Then
        // `2*room <= nw - i - 2` is the fact that bounds every payload read.
        assert(n <= room);
        assert(2 * room <= nw - i - 2) by (nonlinear_arith)
            requires
                room == (nw - i - 2) / 2,
                i + 2 <= nw,
        ;
        let ghost sc_mid = sc@;
        let mut k: usize = 0;
        // THE PAYLOAD FOLD. Single exit, so a plain `invariant` suffices; the
        // clause is one unfolding of `wfold` per step and there is no lemma.
        while k < 2 * n
            invariant
                k <= 2 * n,
                i + 2 + 2 * n <= nw,
                nw <= SCRATCH_W,
                sc@ == sc_mid,
                sc@.len() == SCRATCH_W,
                wfold(sc@, i + 2, k as int, 2 * n as int, acc) == wfold(
                    sc@,
                    i + 2,
                    0,
                    2 * n as int,
                    acc_before,
                ),
            decreases 2 * n - k,
        {
            acc = acc.wrapping_mul(31).wrapping_add(sc_get_unchecked(&sc, i + 2 + k) as u64);
            k = k + 1;
        }
        // Ghost only: `k == 2*n`, so `wfold` at `k` is its own base case and
        // the loop invariant identifies `acc` with the spec's fold.
        assert(wfold(sc@, i + 2, 2 * n as int, 2 * n as int, acc) == acc);
        i = i + 2 + 2 * n;
        o = o + 1;
        // Ghost only: unfold `rwalk` once at the state this iteration started
        // from. Its `sc2` IS the scratch the clamp left behind.
        assert(rwalk(sc_before, nw as int, nrec as int, i_before, o as int - 1, acc_before)
            == rwalk(sc@, nw as int, nrec as int, i as int, o as int, acc));
    }
    // Ghost only: the loop exited, so `rwalk` at `(i, o)` is its own base case.
    assert(rwalk(sc@, nw as int, nrec as int, i as int, o as int, acc)
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
            // so Z3 needs both spelled out. Erases at compile time -- R4 and R5
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
            // Without it the postcondition is decoration -- deleting it
            // entirely still verifies, so nothing but mutation testing defends
            // it (`.memory/04-verus.md`). Ghost code erases, so the driver loop
            // stays byte-identical to R4's.
            assert(r == rec_fold(buf@, (k * stride) as int, stride as int));
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    emit(acc);
}

} // verus!
