//! p14 rung R5 -- unsafe + Verus proof.
//!
//! R4's exec code verbatim, plus the specs and proofs that discharge every
//! unchecked read AND the one unchecked WRITE in it.
//!
//! **The obligation is a PARTITION, and the postcondition is the FUNCTIONAL
//! one.** The kernel's `ensures` says the accumulator is the fold of the field
//! table the line's delimiters determine -- count, then each field's length and
//! its bytes, in order -- not merely that nothing was accessed out of bounds. A
//! memory-safety-only spec would accept a kernel that recorded the wrong
//! lengths, or the right lengths in the wrong order; this one does not.
//! ../NOTES.md 10.
//!
//! **The proof is ONE lemma and two ghost sequences that only ever grow.**
//!
//!   * `toks(scr, m, i, s)` is the UNCAPPED sequence of field lengths still to
//!     be produced, from cursor `i` with the current field starting at `s`. It
//!     is a RECURSION on `m + 1 - i`, not a closed form, because a partition
//!     has no closed form -- and that is the difference between p14's proof and
//!     p06's, where `rev_range` and `rot_left` were `Seq::new` closed forms.
//!   * The scan loop carries `toks(scr,m,0,0) == tkg + toks(scr,m,i,s)`, where
//!     `tkg` is the ghost sequence of the lengths the table already holds.
//!     Every step is one unfolding of `toks` plus a `=~=`.
//!   * `stg` is where each recorded field starts, one entry longer than `tkg`
//!     so that `stg[nt]` is where the NEXT field would start. The scan carries
//!     `forall k < nt: stg[k] + tkg[k] <= m`, and that `forall` is what
//!     discharges `cur + q < m` in the fold. **Both ghosts grow by `push` and
//!     nothing else, and that choice is the whole reason this proof is short**:
//!     `Seq::push` leaves every earlier index alone by an axiom vstd already
//!     has, where re-deriving the sequence from the exec array at every step
//!     (`Seq::new(nt, |k| tl[k])`) needs a prefix lemma per invariant. The first
//!     draft did the latter and failed two invariants and an assertion;
//!     ../NOTES.md 5 has both versions and the error text.
//!   * `lemma_scan_exit` is the one lemma, and it is where the safety line
//!     meets the specification: the scan stops either with the cursor off the
//!     end (the table IS the partition) or with the table full (the table is
//!     the partition's `MAXTOK`-prefix, which is the TRUNCATION R1h performs).
//!
//!     requires  off + len <= buf@.len()
//!
//! ONE clause, as on p03, p06, p11 and p12 and unlike p17. It is structural --
//! about the shape of the buffer the driver built, not about its contents -- so
//! it holds on *every* input this benchmark runs, `adversarial-*` included, and
//! the gate checks it call by call. `nline`, `llen`, and every byte of the
//! window including every delimiter in it are attacker data and none of them is
//! an assumption.
//!
//! **The cursor guards are SUBTRACTION-FIRST and that is what keeps the clause
//! count at one.** `len - p < 4` needs `p <= len`, which the guards themselves
//! maintain; the additive `p + 4 > len` is a `usize` overflow Verus rejects, and
//! buying it back would cost either a second `requires` (p17's route) or a
//! second driver conjunct. p07's lesson, on a third pattern. All seven rungs use
//! it, so no rung comparison moves on it.
//!
//! Note what the spec does **not** assume: that `nline` is honest, that `llen`
//! fits the window, or that a line holds at most `MAXTOK` fields. `walk` is
//! defined as the *program's* walk, so `adversarial-run17`, `-alt33`, `-full65`,
//! `-many` and `degenerate` are all inside the verified domain and the kernel
//! agrees with `model.py` on all five.
//!
//! TCB tally: NOTES.md 6. **Six** `external_body` items, four of them with a
//! `requires`, all listed there individually, because an under-counted TCB is
//! how the pilot's fatal defect hid in plain sight (`.memory/04-verus.md`).
//! `scr_load` is **not** among them: the pinned vstd specifies
//! `copy_from_slice`, `split_at_mut` and the array reborrow, so the bulk load is
//! proved rather than assumed -- p06's TASK_048 result, applied here from the
//! start rather than retrofitted.

use vstd::prelude::*;

// Plain-Rust I/O helpers. Outside `verus!`, so Verus treats the whole module as
// external (external-by-default). Reached only through `load_input`/`emit`.
#[path = "../../common/driver.rs"]
mod driver;

verus! {

// `group_slice_axioms` gives `slice@.len() == spec_slice_len(slice)`, hence
// `slice@.len() <= usize::MAX` -- without it `off + len` cannot be shown not to
// overflow `usize`. `group_array_axioms` gives `scr@.len() == SCR` for a
// `[u8; SCR]` and the fill axiom for `[0; SCR]`. `lemma_u128_shr_is_div` turns
// `x >> 64` into `x / 2^64`, which is what the driver's multiply-shift barrier
// bound is about, and the mul group is what the driver's window-offset bound
// `k * stride + stride <= n_blob` needs; the KERNEL needs neither.
broadcast use {
    vstd::slice::group_slice_axioms,
    vstd::array::group_array_axioms,
    vstd::bits::lemma_u128_shr_is_div,
    vstd::arithmetic::mul::lemma_mul_inequality,
};

/// The scratch's extent, a compile-time constant in every rung.
pub const SCR: usize = 64;

/// The field table's extent, a compile-time constant in every rung. **This is
/// the bound R1 omits**, and it is a bound on a COUNT rather than on a length.
pub const MAXTOK: usize = 16;

/// The field separator, a compile-time constant in every rung.
pub const DELIM: u8 = 44;

// ------------------------------------------------------------------ spec ----
/// The little-endian u32 at absolute byte position `p`, written out the way
/// every rung writes it: `b0 + 256*b1 + 65536*b2 + 16777216*b3`.
///
/// Spelled with `+` and `*` rather than `|` and `<<` on purpose
/// (`.memory/04-verus.md`): the two are the same function on bytes and compile
/// to the same instruction, but only the first is linear arithmetic.
pub open spec fn u32_at(buf: Seq<u8>, p: int) -> int {
    buf[p] as int + 256 * (buf[p + 1] as int) + 65536 * (buf[p + 2] as int)
        + 16777216 * (buf[p + 3] as int)
}

/// How many lines the window at `off` declares. **Declared, and it bounds
/// nothing** -- see `walk`.
pub open spec fn nline_at(buf: Seq<u8>, off: int) -> int {
    u32_at(buf, off)
}

/// The scratch every rung starts from. Safe Rust has no uninitialised array, so
/// all four Rust rungs write `[0u8; SCR]` and both C rungs `memset` it.
pub open spec fn zero_scr() -> Seq<u8> {
    Seq::new(SCR as nat, |i: int| 0u8)
}

/// THE BULK LOAD: `scr` with its prefix `[0, m)` replaced by `buf[at .. at+m)`.
pub open spec fn load_into(scr: Seq<u8>, buf: Seq<u8>, at: int, m: int) -> Seq<u8> {
    Seq::new(scr.len(), |i: int| if 0 <= i < m { buf[at + i] } else { scr[i] })
}

/// THE PARTITION: the UNCAPPED sequence of field lengths of `scr[0 .. m)`, from
/// cursor `i` with the current field starting at `s`.
///
/// `i == m` is a VIRTUAL DELIMITER, which is what makes the tail field arrive
/// at the same site as every other field -- in the spec exactly as in the exec
/// code, and it is why the kernel's safety line is one line rather than two.
///
/// A recursion and not a closed form: a partition has none. This is where p14's
/// proof is a level above p06's.
pub open spec fn toks(scr: Seq<u8>, m: int, i: int, s: int) -> Seq<int>
    decreases m + 1 - i,
{
    if i > m {
        Seq::empty()
    } else if i == m || scr[i] == DELIM {
        seq![i - s] + toks(scr, m, i + 1, i + 1)
    } else {
        toks(scr, m, i + 1, s)
    }
}

/// How many fields the CHECKED kernel records for a line: the uncapped count,
/// truncated at `MAXTOK`. **Truncation is the hardened behaviour and the
/// contract pins it** -- ../spec.md.
pub open spec fn ntok(scr: Seq<u8>, m: int) -> int {
    if toks(scr, m, 0, 0).len() < MAXTOK as int {
        toks(scr, m, 0, 0).len() as int
    } else {
        MAXTOK as int
    }
}

/// The Horner fold over one field's bytes, `scr[q .. end)`.
pub open spec fn fold_bytes(scr: Seq<u8>, q: int, end: int, acc: u64) -> u64
    decreases end - q,
{
    if q >= end {
        acc
    } else {
        fold_bytes(scr, q + 1, end, acc.wrapping_mul(31).wrapping_add(scr[q] as u64))
    }
}

/// The Horner fold over the field table: for each field, its LENGTH and then
/// its CONTENT, in order, with the cursor stepping over the delimiter.
///
/// **Order-sensitive, over the full recorded extent, and all three components
/// are load-bearing.** TASK_004_REVIEW's reason for the full-extent rule is
/// elision; p06's is invariance under permutation. p14 supplies the THIRD, one
/// level up: tokenising is a PARTITION, so a fold that folded only the
/// concatenated content would be blind to where the boundaries are -- every
/// partition of the same line gives the same bytes in the same order. Folding
/// the lengths in order is what makes a boundary bug visible at all, and
/// folding the count is what makes a truncation visible. ../NOTES.md 2.
pub open spec fn fold_toks(scr: Seq<u8>, tk: Seq<int>, j: int, cur: int, acc: u64) -> u64
    decreases tk.len() - j,
{
    if j >= tk.len() {
        acc
    } else {
        fold_toks(
            scr,
            tk,
            j + 1,
            cur + tk[j] + 1,
            fold_bytes(scr, cur, cur + tk[j], acc.wrapping_mul(31).wrapping_add(tk[j] as u64)),
        )
    }
}

/// One line's contribution: the fold over its (capped) field table, then the
/// field COUNT.
pub open spec fn line_fold(scr: Seq<u8>, m: int, acc: u64) -> u64 {
    fold_toks(scr, toks(scr, m, 0, 0).take(ntok(scr, m)), 0, 0, acc).wrapping_mul(
        31,
    ).wrapping_add(ntok(scr, m) as u64)
}

/// THE MACHINE. Lines `line .. nline`, carrying the scratch contents, the
/// cursor and the accumulator.
///
/// **The walk stops when the window runs out, whatever `nline` says** -- the two
/// `break`s are `len - p < 4` and `len - p < llen`, and both are in the spec.
///
/// The scratch is NOT re-zeroed between lines, exactly as in the exec code, and
/// that is why `scr` is carried: the stale bytes above `m` are never read, but
/// the SEQUENCE is what the postcondition is about and it has to be the real
/// one.
pub open spec fn walk(
    buf: Seq<u8>,
    off: int,
    len: int,
    line: int,
    nline: int,
    p: int,
    scr: Seq<u8>,
    acc: u64,
) -> u64
    decreases nline - line,
{
    if line >= nline {
        acc
    } else if len - p < 4 {
        acc
    } else {
        let llen = u32_at(buf, off + p);
        let p2 = p + 4;
        let m = if llen < SCR as int {
            llen
        } else {
            SCR as int
        };
        if len - p2 < llen {
            acc
        } else {
            let scr1 = load_into(scr, buf, off + p2, m);
            walk(buf, off, len, line + 1, nline, p2 + llen, scr1, line_fold(scr1, m, acc))
        }
    }
}

/// What the kernel returns.
///
/// The two early exits are the tests every rung keeps, R1 included: a window too
/// short to hold the header, and a zero count. **R1 keeps both.** What R1 omits
/// is the `MAXTOK` bound inside `walk`'s `ntok`, and that is the only thing it
/// omits.
pub open spec fn split_fold(buf: Seq<u8>, off: int, len: int) -> u64 {
    if len < 4 {
        0
    } else if nline_at(buf, off) == 0 {
        0
    } else {
        walk(buf, off, len, 0, nline_at(buf, off), 4, zero_scr(), 0).wrapping_mul(
            31,
        ).wrapping_add(nline_at(buf, off) as u64)
    }
}

// ----------------------------------------------------------------- proof ----
/// THE ONE LEMMA: what the scan's carried sequence equality becomes when the
/// scan stops.
///
/// Both exits are here because they are the two halves of `ntok`'s definition
/// and they must not drift apart: the scan either runs the cursor off the end,
/// in which case the recorded table IS the whole partition, or it fills the
/// table, in which case the recorded table is the partition's `MAXTOK`-prefix
/// and the partition is at least that long. **The second case is the truncation
/// R1h performs and R1 does not**, so this lemma is where the pattern's safety
/// line meets its specification.
pub proof fn lemma_scan_exit(scr: Seq<u8>, m: int, i: int, s: int, tkg: Seq<int>)
    requires
        toks(scr, m, 0, 0) == tkg + toks(scr, m, i, s),
        i > m || tkg.len() == MAXTOK as int,
        tkg.len() <= MAXTOK as int,
    ensures
        tkg.len() == ntok(scr, m),
        toks(scr, m, 0, 0).take(ntok(scr, m)) == tkg,
{
    let all = toks(scr, m, 0, 0);
    if i > m {
        assert(toks(scr, m, i, s) == Seq::<int>::empty());
        assert(all =~= tkg);
        assert(all.take(ntok(scr, m)) =~= tkg);
    } else {
        assert(all.len() >= MAXTOK as int);
        assert(all.take(MAXTOK as int) =~= tkg);
    }
}

// ------------------------------------------------------------------- TCB ----
// TRUSTED ITEM 1 of 6. vstd ships no specification for `<[T]>::get_unchecked`,
// so this is the axiom that licenses the unchecked read of the SOURCE window.
// It is sound because the standard library's documented contract for
// `get_unchecked` is exactly this: if the caller guarantees `i < v.len()`, the
// call is defined and yields `v[i]`. Identical, character for character, to the
// accessor p01, p02, p03, p05, p06, p07, p11, p12, p13, p16 and p17 ship.
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

// TRUSTED ITEM 2 of 6. The SCRATCH read, performed by the scan and by the fold.
// The scratch is a fixed-size `[u8; 64]`, so the bound is the array's
// type-level length rather than a runtime `len()`.
//
// The `requires` is ONE conjunct and NOT `i < v@.len(), v@.len() == 64`: for a
// `&[u8; 64]` the second is a TAUTOLOGY, discharged from the parameter type
// alone by vstd's `array_len_matches_n`, and p03's gate run caught exactly that
// draft (`.memory/04-verus.md`; p03 NOTES.md 5b).
#[inline(always)]
#[verifier::external_body]
fn scr_get_unchecked(v: &[u8; 64], i: usize) -> (r: u8)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    unsafe { *v.get_unchecked(i) }
}

// THE VERIFIED TWIN of trusted item 2.
#[cfg(slb_twin)]
fn slb_twin_scr_get_unchecked(v: &[u8; 64], i: usize) -> (r: u8)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    v[i]
}

// TRUSTED ITEM 3 of 6. The FIELD TABLE read, performed by the fold. Same shape
// as item 2 on a `[usize; 16]`.
#[inline(always)]
#[verifier::external_body]
fn tl_get_unchecked(v: &[usize; 16], i: usize) -> (r: usize)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    unsafe { *v.get_unchecked(i) }
}

// THE VERIFIED TWIN of trusted item 3.
#[cfg(slb_twin)]
fn slb_twin_tl_get_unchecked(v: &[usize; 16], i: usize) -> (r: usize)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    v[i]
}

// TRUSTED ITEM 4 of 6, and **the item p14 exists for**: the unchecked STORE
// into the fixed field table. Its `requires` is what excludes R1's
// out-of-bounds store, and R1's bug is exactly a caller that cannot discharge
// it.
//
// The `ensures` is a whole-sequence equality (`update`), not a statement about
// slot `i` alone, so it says both "slot `i` became `x`" and "nothing else
// moved" -- the shape `.memory/02-bench-rules.md` argues for, and it is what
// `lemma_tl_seq_push` needs in order to compose.
//
// `x` is a pure VALUE parameter -- stored, never used as an address or a length
// -- so it has no precondition, and `../spec.md`'s `verus.unsafe_justifications`
// says so and the gate shouts it every run. `.memory/04-verus.md` names this
// false positive of the parameter-coverage rule; p03 was the first pattern to
// exercise it, p12 the second, p06 the third and p14 the fourth.
#[inline(always)]
#[verifier::external_body]
fn tl_set_unchecked(v: &mut [usize; 16], i: usize, x: usize)
    requires
        i < old(v)@.len(),
    ensures
        final(v)@ == old(v)@.update(i as int, x),
{
    unsafe {
        *v.get_unchecked_mut(i) = x;
    }
}

// THE VERIFIED TWIN of trusted item 4. `v[i] = x` is the checked stand-in for
// `*v.get_unchecked_mut(i) = x`; weaken the shared `requires` and Verus rejects
// the indexed store.
#[cfg(slb_twin)]
fn slb_twin_tl_set_unchecked(v: &mut [usize; 16], i: usize, x: usize)
    requires
        i < old(v)@.len(),
    ensures
        final(v)@ == old(v)@.update(i as int, x),
{
    v[i] = x;
}

// THE BULK LOAD -- and it is NOT a trusted item, deliberately and from the
// start. `.memory/04-verus.md`'s rule, as corrected at TASK_048: a bulk copy
// needs a trusted wrapper when R4's SPELLING is unsupported, not when the copy
// is. R4 here spells `copy_from_slice`, which the pinned vstd specifies
// (`vstd/std_specs/slice.rs:205`), together with `split_at_mut` (`:185`) and the
// `&mut [u8; 64] -> &mut [u8]` reborrow (`vstd/array.rs:175
// ref_mut_array_unsizing_coercion`, which Verus inserts itself and which never
// appears in source). So the axiom RELOCATES into vstd rather than living here,
// and ../NOTES.md 6b says what that does to the TCB column.
//
// The receiver is `split_at_mut(n)` and not `dst[..n]` because `..n` is a
// `RangeTo<usize>` and `RangeTo` has NO `SliceIndexSpecImpl` at the pinned vstd
// -- only `usize` and `Range<usize>` do -- so `dst[..n]` cannot be verified at
// all. safe_naive.rs and safe_tuned.rs keep `dst[..n]`; this rung and unsafe.rs
// write the three exec lines below character for character. ../NOTES.md 6a.
//
// It is a free function rather than an expression inside `kernel` because R4
// has to be byte-identical to it.
#[inline(always)]
fn scr_load(dst: &mut [u8; 64], src: &[u8], from: usize, n: usize)
    requires
        n <= old(dst)@.len(),
        from + n <= src@.len(),
    ensures
        final(dst)@ == load_into(old(dst)@, src@, from as int, n as int),
{
    assert(src@.len() == vstd::slice::spec_slice_len(src));
    let ghost d0 = dst@;
    let s: &mut [u8] = dst;
    let (a, _b) = s.split_at_mut(n);
    a.copy_from_slice(&src[from..from + n]);
    assert(dst@ =~= load_into(d0, src@, from as int, n as int));
}

// TRUSTED ITEM 5 of 6. Argument parsing, file I/O and little-endian decoding,
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

// TRUSTED ITEM 6 of 6. `println!` is not verifiable; no `ensures`. Counted with
// the five above -- every `external_body` item is TCB, not just the interesting
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
        r == split_fold(buf@, off as int, len as int),
{
    // Ghost only: mentioning `spec_slice_len` fires vstd's `axiom_spec_len`,
    // which is what tells the SMT solver a slice length fits in a `usize` --
    // needed to rule out `off + len` overflowing. Erases at compile time.
    assert(buf@.len() == vstd::slice::spec_slice_len(buf));
    if len < 4 {
        return 0;
    }
    let nline: usize = buf_get_unchecked(buf, off) as usize + 256 * (buf_get_unchecked(
        buf,
        off + 1,
    ) as usize) + 65536 * (buf_get_unchecked(buf, off + 2) as usize) + 16777216 * (
    buf_get_unchecked(buf, off + 3) as usize);
    if nline == 0 {
        return 0;
    }
    let mut scr: [u8; SCR] = [0; SCR];
    let mut tl: [usize; MAXTOK] = [0; MAXTOK];
    // Ghost only: `[0; 64]`'s view IS the all-zeros sequence.
    assert(scr@ =~= zero_scr());
    let mut acc: u64 = 0;
    let mut p: usize = 4;
    let mut ln: usize = 0;
    // "The lines from here, with the scratch we have built and where the cursor
    // is, are all the lines." p06's and p12's relational shape. This loop exits
    // THREE ways (`ln == nline` and the two window-exhausted breaks), so it
    // needs `invariant_except_break` plus a loop `ensures`.
    while ln < nline
        invariant_except_break
            ln <= nline,
            0 < nline,
            nline == nline_at(buf@, off as int),
            4 <= len,
            4 <= p <= len,
            scr@.len() == SCR,
            tl@.len() == MAXTOK,
            off + len <= buf@.len(),
            buf@.len() <= usize::MAX,
            walk(buf@, off as int, len as int, ln as int, nline as int, p as int, scr@, acc)
                == walk(buf@, off as int, len as int, 0, nline as int, 4, zero_scr(), 0),
        ensures
            walk(buf@, off as int, len as int, 0, nline as int, 4, zero_scr(), 0) == acc,
        decreases nline - ln,
    {
        let ghost p_before = p as int;
        let ghost ln_before = ln as int;
        let ghost acc_before = acc;
        let ghost scr_before = scr@;
        if len - p < 4 {
            break;
        }
        let llen: usize = buf_get_unchecked(buf, off + p) as usize + 256 * (
        buf_get_unchecked(buf, off + p + 1) as usize) + 65536 * (buf_get_unchecked(
            buf,
            off + p + 2,
        ) as usize) + 16777216 * (buf_get_unchecked(buf, off + p + 3) as usize);
        p = p + 4;
        let m: usize = if llen < SCR {
            llen
        } else {
            SCR
        };
        if len - p < llen {
            break;
        }
        scr_load(&mut scr, buf, off + p, m);
        let ghost scr_loaded = scr@;
        p = p + llen;
        let mut nt: usize = 0;
        let mut s: usize = 0;
        let mut i: usize = 0;
        // `tkg` is the field-length sequence the table already holds and `stg`
        // is where each of those fields starts, one entry longer so that
        // `stg[nt]` is where the NEXT field would start. Both are ghost, both
        // only ever grow by a push, and that is deliberate: a `Seq::push` leaves
        // every earlier index alone by an axiom vstd already has, where a
        // `Seq::new`-style re-derivation from the exec array would need a prefix
        // lemma at every step. ../NOTES.md 5.
        let ghost mut tkg: Seq<int> = Seq::empty();
        let ghost mut stg: Seq<int> = seq![0int];
        // THE SCAN. The invariant is the partition split in two: what the table
        // already holds, and what `toks` still has to produce. It exits two ways
        // -- cursor past the end, or table full -- so it carries the disjunction
        // out and `lemma_scan_exit` reads it.
        while i <= m
            invariant_except_break
                m <= SCR,
                scr@ == scr_loaded,
                scr@.len() == SCR,
                tl@.len() == MAXTOK,
                nt <= MAXTOK,
                s <= i <= m + 1,
                tkg.len() == nt as int,
                stg.len() == nt as int + 1,
                stg[0] == 0,
                s as int == stg[nt as int],
                forall|k: int|
                    0 <= k < nt as int ==> #[trigger] stg[k + 1] == stg[k] + tkg[k] + 1,
                forall|k: int| #![trigger tkg[k]] 0 <= k < nt as int ==> stg[k] + tkg[k] <= m as int,
                forall|k: int| #![trigger tl@[k]] 0 <= k < nt as int ==> tkg[k] == tl@[k] as int,
                toks(scr@, m as int, 0, 0) == tkg + toks(
                    scr@,
                    m as int,
                    i as int,
                    s as int,
                ),
            ensures
                m <= SCR,
                scr@ == scr_loaded,
                scr@.len() == SCR,
                tl@.len() == MAXTOK,
                nt <= MAXTOK,
                tkg.len() == nt as int,
                stg.len() == nt as int + 1,
                stg[0] == 0,
                forall|k: int|
                    0 <= k < nt as int ==> #[trigger] stg[k + 1] == stg[k] + tkg[k] + 1,
                forall|k: int| #![trigger tkg[k]] 0 <= k < nt as int ==> stg[k] + tkg[k] <= m as int,
                forall|k: int| #![trigger tl@[k]] 0 <= k < nt as int ==> tkg[k] == tl@[k] as int,
                toks(scr@, m as int, 0, 0) == tkg + toks(
                    scr@,
                    m as int,
                    i as int,
                    s as int,
                ),
                i as int > m as int || nt == MAXTOK,
            decreases m + 1 - i,
        {
            if i == m || scr_get_unchecked(&scr, i) == DELIM {
                // THE SAFETY LINE. c/kernel.c omits exactly this.
                if nt == MAXTOK {
                    break;
                }
                let flen: usize = i - s;
                tl_set_unchecked(&mut tl, nt, flen);
                proof {
                    tkg = tkg.push(i as int - s as int);
                    stg = stg.push(i as int + 1);
                }
                nt = nt + 1;
                s = i + 1;
            }
            i = i + 1;
        }
        proof {
            lemma_scan_exit(scr@, m as int, i as int, s as int, tkg);
        }
        let mut cur: usize = 0;
        let mut j: usize = 0;
        let ghost acc_pre_fold = acc;
        // THE FOLD over the table. `cur` is field `j`'s start -- `stg[j]` -- and
        // the two `forall`s the scan carried are what keep `cur + q` inside the
        // scratch.
        while j < nt
            invariant
                m <= SCR,
                nt <= MAXTOK,
                j <= nt,
                scr@.len() == SCR,
                tl@.len() == MAXTOK,
                tkg.len() == nt as int,
                stg.len() == nt as int + 1,
                cur as int == stg[j as int],
                forall|k: int|
                    0 <= k < nt as int ==> #[trigger] stg[k + 1] == stg[k] + tkg[k] + 1,
                forall|k: int| #![trigger tkg[k]] 0 <= k < nt as int ==> stg[k] + tkg[k] <= m as int,
                forall|k: int| #![trigger tl@[k]] 0 <= k < nt as int ==> tkg[k] == tl@[k] as int,
                fold_toks(scr@, tkg, j as int, cur as int, acc) == fold_toks(
                    scr@,
                    tkg,
                    0,
                    0,
                    acc_pre_fold,
                ),
            decreases nt - j,
        {
            let tj: usize = tl_get_unchecked(&tl, j);
            acc = acc.wrapping_mul(31).wrapping_add(tj as u64);
            let mut q: usize = 0;
            let ghost acc_pre_bytes = acc;
            while q < tj
                invariant
                    q <= tj,
                    cur + tj <= m <= SCR,
                    scr@.len() == SCR,
                    fold_bytes(scr@, cur + q as int, cur + tj as int, acc) == fold_bytes(
                        scr@,
                        cur as int,
                        cur + tj as int,
                        acc_pre_bytes,
                    ),
                decreases tj - q,
            {
                acc = acc.wrapping_mul(31).wrapping_add(
                    scr_get_unchecked(&scr, cur + q) as u64,
                );
                q = q + 1;
            }
            cur = cur + tj + 1;
            j = j + 1;
        }
        acc = acc.wrapping_mul(31).wrapping_add(nt as u64);
        // Ghost only: unfold `walk` once at the value it had on entry to this
        // iteration. Its `llen` and `m` ARE the exec values, its `load_into` IS
        // what `scr_load` did, and its `line_fold` IS what the scan and the fold
        // built.
        assert(walk(buf@, off as int, len as int, ln_before, nline as int, p_before,
            scr_before, acc_before) == walk(buf@, off as int, len as int, ln_before + 1,
            nline as int, p as int, scr@, acc));
        ln = ln + 1;
    }
    acc.wrapping_mul(31).wrapping_add(nline as u64)
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
        // is the guard immediately above, and integer division only rounds down,
        // so `n_blob / stride >= 1` -- but that is a fact about division and Z3
        // needs the lemma named.
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
            assert(r == split_fold(buf@, (k * stride) as int, stride as int));
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    emit(acc);
}

} // verus!
