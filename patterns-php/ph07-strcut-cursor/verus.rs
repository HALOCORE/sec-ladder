//! ph07 rung R5 -- unsafe + Verus.
//!
//! Same exec code as `unsafe.rs`, plus the proof that licenses it. What is
//! proved, and it is a VALUE postcondition rather than a memory-safety-only
//! retreat:
//!
//!     requires  off + len <= buf@.len(),  9 <= len
//!     ensures   r == strcut_fold(buf@, off as int, len as int)
//!
//! `strcut_fold` is `mbfl_strcut`'s mblen_table arm with `cb3cca21b345`
//! applied, spelled as three mutually independent recursive spec functions --
//! `walk_start`, `walk_end`, `fold_out` -- and `model.py` re-derives the same
//! `u64` from a different decomposition.
//!
//! ⚠⚠ **THE OBLIGATION THIS ROW IS ABOUT IS `walk_start`'s TERMINATION AND ITS
//! BOUND, AND THEY ARE THE SAME OBLIGATION.** `mbfilter.c:1202-1210` is
//! `for (;;) { m = mbtab[*p]; n += m; p += m; if (n > from) break; start = n; }`
//! -- an unbounded loop over a cursor advanced by data. Two facts make it
//! tractable, and they come from two different places:
//!
//!   * every `mblen_table_utf8` entry is `>= 1`, so `n` strictly increases and
//!     `from + 1 - n` is a `decreases`. That is a fact about STATIC DATA and
//!     `lemma_mbtab_pos` proves it out of the literal table by
//!     `by (compute_only)` plus one induction -- **no `assume`, no
//!     `external_body`, no sixth trusted item.** ⭐ It is the answer to
//!     `TASK_PHP_016` §5.2: the 256-byte table lifts as static data and costs
//!     the proof one lemma, not a tier;
//!   * `n <= from <= string->len` at every read, which is **`cb3cca21b345`
//!     hunk (a)**. Delete that line and `get_unchecked(s, n)` has no
//!     precondition -- which is exactly `c/kernel.c`.
//!     `controls/negatives.py --emit noguard` runs that mutant and it must
//!     FAIL to verify.
//!
//! ⭐ **The end walk needs neither.** `mbfilter.c:1213`'s
//! `if (k >= (int)string->len)` means `walk_end` only ever runs with
//! `n <= k < string->len`, so its reads are in range for a reason that is in
//! the 5.0.0 source already. **One walk carries its own bound and the other
//! does not**, and the proof makes the difference visible as a proof
//! obligation that exists on one and not the other. NOTES.md §5, §10.

use vstd::prelude::*;

// Plain-Rust I/O helpers. Outside `verus!`, so Verus treats the whole module as
// external (external-by-default). Reached only through `load_input`/`emit`.
#[path = "../../common/driver.rs"]
mod driver;

verus! {

// `group_slice_axioms` gives `slice@.len() == spec_slice_len(slice)`, hence
// `slice@.len() <= usize::MAX`, without which `off + len` cannot be shown not
// to overflow. `group_array_axioms` is what lets the proof see INTO the 256-byte
// `MBTAB`. `lemma_u128_shr_is_div` turns `x >> 64` into `x / 2^64` for the
// driver's multiply-shift barrier bound; the mul group is what the window-offset
// bound `k * stride + stride <= n_blob` needs.
broadcast use {
    vstd::slice::group_slice_axioms,
    vstd::bits::lemma_u128_shr_is_div,
    vstd::arithmetic::mul::lemma_mul_inequality,
};

/// `mblen_table_utf8` -- ext/mbstring/libmbfl/filters/mbfilter_utf8.c:39-56,
/// the same 256 numbers `c/kernel.c` and the other three Rust rungs carry.
/// STATIC DATA: in PHP it is a field of a `const mbfl_encoding`, not input.
pub const MBTAB: [u8; 256] = [
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
    2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
    3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3,
    4, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 1, 1,
];

// ------------------------------------------------------------------ spec ----

/// The step size `mblen_table_utf8` gives for a lead byte, as a CLOSED FORM.
///
/// ⚠⚠ **WHY A CLOSED FORM AND NOT `MBTAB@[b]`, AND IT IS A MEASURED REASON.**
/// `MBTAB@` is `array_view`, which vstd defines as `Seq::new(256, ...)`, so
/// every mention of it in a spec function drags `lemma_seq_new_index` into the
/// SMT context -- **4 127 instantiations, 88 % of the kernel's total cost, and
/// the kernel did not verify at rlimit 100** (`.temp/php16/09-profile.log`).
/// With the table out of `walk_start`/`walk_end` the same kernel verifies at
/// the DEFAULT rlimit with no override. NOTES.md §10.
///
/// ⚠ This is a SUBSTITUTION, and it is discharged rather than asserted:
/// `lemma_mbtab_matches` proves `MBTAB@[b] == mbtab_of(b)` for all 256 `b`,
/// mechanically, out of the literal table -- which is a stronger instrument
/// than the differential `PROTOCOL_PHP.md` §A1(c) asks for. `model.py`'s
/// selfcheck check 5 makes the same comparison against `c/kernel.c`'s text.
pub open spec fn mbtab_of(b: u8) -> int {
    if b < 0xC0 {
        1
    } else if b < 0xE0 {
        2
    } else if b < 0xF0 {
        3
    } else if b < 0xF8 {
        4
    } else if b < 0xFC {
        5
    } else if b < 0xFE {
        6
    } else {
        1
    }
}

/// The literal table agrees with the closed form on `MBTAB@[0..n]`, as a
/// recursive conjunction so that `by (compute_only)` can evaluate it. This is
/// ph03's `emit_ok_upto` recipe applied to static data instead of arithmetic.
pub open spec fn mbtab_matches_upto(n: nat) -> bool
    decreases n,
{
    if n == 0 {
        true
    } else {
        MBTAB@[n as int - 1] as int == mbtab_of((n - 1) as u8) && mbtab_matches_upto(
            (n - 1) as nat,
        )
    }
}

pub proof fn lemma_mbtab_elim(n: nat, k: int)
    requires
        mbtab_matches_upto(n),
        0 <= k < n,
    ensures
        MBTAB@[k] as int == mbtab_of(k as u8),
    decreases n,
{
    broadcast use vstd::array::group_array_axioms;

    if (n as int) - 1 == k {
    } else {
        lemma_mbtab_elim((n - 1) as nat, k);
    }
}

/// ⭐ ALL 256 ENTRIES, MECHANICALLY. This is what makes lifting the
/// `mblen_table` as static data cost one lemma rather than a tier
/// (`TASK_PHP_016` §5.2).
pub proof fn lemma_mbtab_matches(b: u8)
    ensures
        MBTAB@[b as int] as int == mbtab_of(b),
{
    broadcast use vstd::array::group_array_axioms;

    assert(mbtab_matches_upto(256)) by (compute_only);
    lemma_mbtab_elim(256, b as int);
}

/// ⭐ THE TERMINATION PREMISE OF THE WHOLE ROW. Without `mbtab_of(b) >= 1` the
/// start walk's `decreases` does not decrease and `mbfl_strcut` is not provably
/// terminating at all. On the closed form it is a seven-way case split.
pub proof fn lemma_mbtab_pos(b: u8)
    ensures
        mbtab_of(b) >= 1,
{
}

/// One little-endian 32-bit head word of the window.
pub open spec fn head_u32(w: Seq<u8>, i: int) -> u32 {
    (w[i] as u32) | ((w[i + 1] as u32) << 8) | ((w[i + 2] as u32) << 16) | ((w[i
        + 3] as u32) << 24)
}

/// mbstring.c:1787-1793 -- a negative `from` counts from the end and floors at
/// zero. ⚠ The GUARD frame, and it clamps from BELOW only; nothing here bounds
/// `from` from above, which is CRASH-124.
pub open spec fn guard_from(slen: int, fw: u32) -> int {
    if fw < 0x8000_0000 {
        fw as int
    } else if slen >= (0u32.wrapping_sub(fw)) as int {
        slen - (0u32.wrapping_sub(fw)) as int
    } else {
        0
    }
}

/// mbstring.c:1795-1801 -- a negative `length` stops that many from the end.
pub open spec fn guard_len(slen: int, frm: int, lw: u32) -> int {
    if lw < 0x8000_0000 {
        lw as int
    } else {
        let a = if slen >= frm { slen - frm } else { 0 };
        let d = (0u32.wrapping_sub(lw)) as int;
        if a >= d { a - d } else { 0 }
    }
}

/// mbfilter.c:1202-1210, ROTATED: the C reads once before its first test, so
/// the caller enters this with `n == mbtab_of(s[0])` and `start == 0`.
/// ⚠ The `decreases` is `from + 1 - n` and it needs `mbtab_of >= 1`; that is
/// what `walk_start_dec` supplies and `lemma_mbtab_pos` proves.
pub open spec fn walk_start(s: Seq<u8>, frm: int, n: int, start: int) -> (int, int)
    decreases (if n > frm { 0int } else { frm + 7 - n })
    via walk_start_dec
{
    if n > frm {
        (n, start)
    } else {
        walk_start(s, frm, n + mbtab_of(s[n]), n)
    }
}

#[via_fn]
proof fn walk_start_dec(s: Seq<u8>, frm: int, n: int, start: int) {
    lemma_mbtab_pos(s[n]);
}

/// mbfilter.c:1217-1222. ⭐ The BOUNDED walk: the caller only enters it when
/// `k < string->len`, so `n <= k` at every read is enough to keep it in range.
pub open spec fn walk_end(s: Seq<u8>, k: int, n: int, end: int) -> int
    decreases (if n > k { 0int } else { k + 7 - n })
    via walk_end_dec
{
    if n > k {
        end
    } else {
        walk_end(s, k, n + mbtab_of(s[n]), n)
    }
}

#[via_fn]
proof fn walk_end_dec(s: Seq<u8>, k: int, n: int, end: int) {
    lemma_mbtab_pos(s[n]);
}

/// The Horner fold the benchmark wrapper applies to the returned substring --
/// mbstring.c:1810's `RETVAL_STRINGL(ret->val, ret->len, 0)` consumed.
pub open spec fn fold_out(s: Seq<u8>, i: int, e: int, acc: u64) -> u64
    decreases e - i,
{
    if i >= e {
        acc
    } else {
        fold_out(s, i, e - 1, acc).wrapping_mul(31).wrapping_add(s[e - 1] as u64)
    }
}

/// `php_shim_tally()` after one reset + one `emalloc(cap)` + one `efree`
/// (`common-php/emalloc_shim.h:644-647`). `n_alloc = n_free = 1`,
/// `n_cache_hit = 0` because the reset empties the size-class cache, and
/// `bytes_mallocked` is the TRUNCATED `real_size = (cap + 7) & ~7`.
pub open spec fn tally_of(cap: int) -> u64 {
    let rs: u64 = (cap as u64).wrapping_add(7) & !7u64;
    ((1000003u64 ^ 1000033u64) ^ rs.wrapping_mul(1000039))
}

/// What the kernel must return. `model.py::strcut_fold` re-derives it.
pub open spec fn strcut_fold(buf: Seq<u8>, off: int, len: int) -> u64 {
    let fw = head_u32(buf, off);
    let lw = head_u32(buf, off + 4);
    let s = buf.subrange(off + 8, off + len);
    let slen = len - 9;
    let f0 = guard_from(slen, fw);
    let l0 = guard_len(slen, f0, lw);
    if f0 > slen {
        0xFFFF_FFFFu64
    } else {
        let length = if f0 + l0 > slen { slen - f0 } else { l0 };
        let w = walk_start(s, f0, mbtab_of(s[0]), 0);
        let k = w.1 + length;
        let end0 = if k >= slen { slen } else { walk_end(s, k, w.0, w.1) };
        let st1 = if w.1 > slen { slen } else { w.1 };
        let en1 = if end0 > slen { slen } else { end0 };
        let st2 = if st1 > en1 { en1 } else { st1 };
        let cnt = en1 - st2;
        (fold_out(s, st2, en1, 0).wrapping_mul(31).wrapping_add(cnt as u64)) ^ tally_of(
            cnt + 8,
        )
    }
}

// ----------------------------------------------------------------- proof ----

/// Folding a copy from the front is folding the original from `ao`.
pub proof fn lemma_fold_shift(a: Seq<u8>, b: Seq<u8>, ao: int, n: int, acc: u64)
    requires
        0 <= ao,
        0 <= n,
        ao + n <= a.len(),
        n <= b.len(),
        forall|t: int| 0 <= t < n ==> a[ao + t] == b[t],
    ensures
        fold_out(b, 0, n, acc) == fold_out(a, ao, ao + n, acc),
    decreases n,
{
    if n > 0 {
        lemma_fold_shift(a, b, ao, n - 1, acc);
    }
}

// ------------------------------------------------------------------- TCB ----
// TRUSTED ITEM 1 of 4, and the whole of this row's security argument. vstd
// ships no specification for `<[T]>::get_unchecked`, so this is the axiom that
// licenses the unchecked reads. It is sound because the standard library's
// documented contract for `get_unchecked` is exactly this: if the caller
// guarantees `i < v.len()`, the call is defined and yields `v[i]`.
//
// FOUR call sites: the two walks' `mbtab[*p]`, and the copy's source read.
// Every one of them is discharged from `n <= from <= slen` or `n <= k < slen`,
// i.e. from `cb3cca21b345` hunk (a) and from mbfilter.c:1213 respectively.
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

// THE VERIFIED TWIN of trusted item 1 (`harness/check.py` step 5c-twin). Same
// signature and same contract, character for character -- the gate lifts both
// from `get_unchecked` above and refuses a twin whose signature differs -- but
// implemented in *checked* code. A `requires` too weak to license
// `*v.get_unchecked(i)` is too weak to license `v[i]`, and Verus can see the
// second one. `#[cfg(slb_twin)]` is a cfg no build ever sets, so rustc strips
// this before codegen: the twin costs zero instructions structurally.
#[cfg(slb_twin)]
fn slb_twin_get_unchecked(v: &[u8], i: usize) -> (r: u8)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    v[i]
}

// TRUSTED ITEM 2 of 4 -- the unchecked DESTINATION read, for the final fold.
// Same contract, a `Vec` rather than a slice.
#[inline(always)]
#[verifier::external_body]
fn vget_unchecked(v: &Vec<u8>, i: usize) -> (r: u8)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    unsafe { *v.get_unchecked(i) }
}

#[cfg(slb_twin)]
fn slb_twin_vget_unchecked(v: &Vec<u8>, i: usize) -> (r: u8)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    v[i]
}

// TRUSTED ITEM 3 of 4 -- the unchecked DESTINATION WRITE, `mbfilter.c:1250`'s
// `*w++ = *p++`. The `ensures` is the *whole* new state, `old(v)@.update(i, x)`,
// not just `v@[i] == x`: an `ensures` naming only the written element would let
// a body that also clobbered `v[i+1]` through, which is precisely the class
// `.memory/04-verus.md` records as the most dangerous vacuity mode.
#[inline(always)]
#[verifier::external_body]
fn vset_unchecked(v: &mut Vec<u8>, i: usize, x: u8)
    requires
        i < old(v)@.len(),
    ensures
        final(v)@ == old(v)@.update(i as int, x),
{
    unsafe { *v.get_unchecked_mut(i) = x };
}

#[cfg(slb_twin)]
fn slb_twin_vset_unchecked(v: &mut Vec<u8>, i: usize, x: u8)
    requires
        i < old(v)@.len(),
    ensures
        final(v)@ == old(v)@.update(i as int, x),
{
    v.set(i, x);
}

// TRUSTED ITEM 4 of 4. Argument parsing, file I/O and little-endian decoding,
// delegated to common/driver.rs so that all six rungs read the file the same
// way. It states **no** `ensures` at all, deliberately: an `ensures` here would
// be an axiom about the contents of a file, which nothing can justify. Every
// fact the proof needs is re-derived at run time from `bytes.len()` inside
// verified code. It contains no `unsafe`, so it stays outside the twin regime.
#[verifier::external_body]
fn load_input() -> (r: (u64, u64, Vec<u8>)) {
    let path = driver::arg_path();
    let inp = driver::load(&path);
    let (stride_w, bytes) = driver::head1_u64_bytes(&inp);
    (inp.n_iters, stride_w, bytes)
}

// `println!` is not verifiable; no `ensures`. Counted with the four above --
// every `external_body` item is TCB, not just the interesting ones
// (`.memory/04-verus.md`).
#[verifier::external_body]
fn emit(acc: u64) {
    driver::emit(acc);
}

// -------------------------------------------------------- exec arithmetic ---
// Same text as unsafe.rs. Each carries the `ensures` that ties the machine
// arithmetic to the spec function above it, so none of them is trusted.

/// One `mblen_table_utf8` lookup. Same body as the other three Rust rungs;
/// the `ensures` is what keeps `MBTAB@` inside THIS query instead of inside
/// the kernel's.
#[inline(always)]
fn mbtab(b: u8) -> (r: u8)
    ensures
        r as int == mbtab_of(b),
        r >= 1,
{
    proof {
        broadcast use vstd::array::group_array_axioms;

        lemma_mbtab_matches(b);
        lemma_mbtab_pos(b);
    }
    MBTAB[b as usize]
}

#[inline(always)]
fn tally(cap: usize) -> (r: u64)
    ensures
        r == tally_of(cap as int),
{
    let real_size: u64 = (cap as u64).wrapping_add(7) & !7u64;
    1000003u64 ^ 1000033u64 ^ real_size.wrapping_mul(1000039)
}

// ---------------------------------------------------------------- kernel ----
// Same exec code as unsafe.rs. Contract: ../spec.md.
//
// One `ensures`, and it is the VALUE, not the safety property -- see the module
// comment. What makes it worth having anyway: it is what stops the proof being
// vacuous, it is what `model.py` re-derives independently, and it is what forces
// the invariants to describe the walks rather than merely bound the cursors. A
// kernel that returned 0 unconditionally would satisfy every bounds obligation
// in this file.
// ⚠⚠ **THE ONE PROOF-BUDGET OVERRIDE IN THIS ROW, DISCLOSED WITH ITS
// NUMBERS.** Verus's default rlimit is 10. Measured on this box
// (`.temp/php16/10-rlimit.log`): the kernel needs ~10-12 plain and **15 under
// `--cfg slb_twin`**, where the three verified twins add to the module's SMT
// context -- so at the default it verified plain and FAILED twin, and with two
// `assert`s removed it verified twin and FAILED plain. **A proof that passes
// on one side of a coin flip is not a proof**, so the budget is set to 30,
// which is 2x the worst measured requirement and leaves both sides with
// margin. `harness/check.py::_verus` passes no `--rlimit`, so this has to be
// an attribute rather than a flag.
//
// ⚠ It is 30 and not 300 because the cost was ATTACKED FIRST, not budgeted
// around: `MBTAB@` out of the spec functions took the kernel from "does not
// verify at rlimit 100" to "verifies at 10 in five seconds" (see `mbtab_of`).
// NOTES.md §10 has the before/after.
#[verifier::rlimit(30)]
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> (r: u64)
    requires
        off + len <= buf@.len(),
        9 <= len,
    ensures
        r == strcut_fold(buf@, off as int, len as int),
{
    // Ghost only: mentioning `spec_slice_len` fires vstd's `axiom_spec_len`,
    // which is what tells the SMT solver a slice length fits in a `usize`.
    assert(buf@.len() == vstd::slice::spec_slice_len(buf));
    let fw: u32 = (buf[off] as u32) | ((buf[off + 1] as u32) << 8) | ((buf[off + 2] as u32)
        << 16) | ((buf[off + 3] as u32) << 24);
    let lw: u32 = (buf[off + 4] as u32) | ((buf[off + 5] as u32) << 8) | ((buf[off + 6] as u32)
        << 16) | ((buf[off + 7] as u32) << 24);
    let s: &[u8] = &buf[off + 8..off + len];
    let slen: usize = s.len() - 1;
    assert(s@.len() == vstd::slice::spec_slice_len(s));
    assert(s@ =~= buf@.subrange(off + 8, off + len));
    // `s@.len() == len - 8` and `len <= buf@.len() <= usize::MAX`, so the walk
    // cursor has nine bytes of headroom above the largest slice length -- which
    // is what makes `n = n + m` (with `m <= 6`) provably free of overflow. vstd
    // exposes no `slice.len() <= isize::MAX`, so this is where the bound comes
    // from and it is why the kernel `requires 9 <= len`.
    assert(s@.len() + 8 <= usize::MAX);
    // Ghost only: name every quantity `strcut_fold` names, so the postcondition
    // is a chain of one-step equalities rather than one search. ⚠ Without this
    // the kernel exceeds Verus's default rlimit; with it there is budget to
    // spare, and NO `#[verifier::rlimit]` override is needed. NOTES.md §10.
    let ghost slq: int = len as int - 9;
    assert(slen as int == slq);
    assert(fw == head_u32(buf@, off as int));
    assert(lw == head_u32(buf@, off as int + 4));

    let frm: usize = if fw < 0x8000_0000 {
        fw as usize
    } else {
        slen.saturating_sub((0u32.wrapping_sub(fw)) as usize)
    };
    let length: usize = if lw < 0x8000_0000 {
        lw as usize
    } else {
        slen.saturating_sub(frm).saturating_sub((0u32.wrapping_sub(lw)) as usize)
    };
    assert(frm as int == guard_from(slq, fw));
    assert(length as int == guard_len(slq, frm as int, lw));
    let ghost f0: int = frm as int;
    let ghost l0: int = length as int;
    // cb3cca21b345 hunk (a) -- the line every `get_unchecked` below rests on.
    if frm > slen {
        assert(strcut_fold(buf@, off as int, len as int) == 0xFFFF_FFFFu64);
        return 0xFFFF_FFFFu64;
    }
    // cb3cca21b345 hunk (b).
    let length: usize = if frm.saturating_add(length) > slen {
        slen - frm
    } else {
        length
    };
    assert(length as int == (if f0 + l0 > slq { slq - f0 } else { l0 }));

    // mbfilter.c:1202-1210, rotated: the C reads once before its first test.
    let mut n: usize = mbtab(get_unchecked(s, 0)) as usize;
    assert(n as int == mbtab_of(s@[0]));
    let mut start: usize = 0;
    let ghost w = walk_start(s@, f0, mbtab_of(s@[0]), 0);
    while n <= frm
        invariant
            1 <= n <= frm + 6,
            0 <= start <= frm,
            frm <= slen,
            slen + 1 == s@.len(),
            s@.len() + 8 <= usize::MAX,
            walk_start(s@, frm as int, n as int, start as int) == w,
        decreases frm + 7 - n,
    {
        start = n;
        let m: usize = mbtab(get_unchecked(s, n)) as usize;
        n = n + m;
    }
    assert(w == (n as int, start as int));

    // mbfilter.c:1212-1223 -- the end walk, which IS bounded.
    let k: usize = start.saturating_add(length);
    let ghost ks: int = w.1 + length as int;
    assert(k as int == ks);
    let ghost end0: int = if ks >= slq {
        slq
    } else {
        walk_end(s@, ks, w.0, w.1)
    };
    let mut end: usize;
    if k >= slen {
        end = slen;
    } else {
        end = start;
        let ghost e = walk_end(s@, k as int, n as int, start as int);
        while n <= k
            invariant
                k < slen,
                slen + 1 == s@.len(),
                s@.len() + 8 <= usize::MAX,
                n <= slen + 6,
                end <= slen,
                walk_end(s@, k as int, n as int, end as int) == e,
            decreases k + 7 - n,
        {
            end = n;
            let m: usize = mbtab(get_unchecked(s, n)) as usize;
            n = n + m;
        }
        assert(e == end as int);
    }
    assert(end as int == end0);
    // mbfilter.c:1227-1241 -- the clamps.
    if start > slen {
        start = slen;
    }
    if end > slen {
        end = slen;
    }
    if start > end {
        start = end;
    }
    // mbfilter.c:1243-1256 -- `mbfl_malloc((n + 8))` and the copy.
    let cnt: usize = end - start;
    let cap: usize = cnt + 8;
    let mut out: Vec<u8> = vec![0u8; cap];
    let mut i: usize = 0;
    while i < cnt
        invariant
            i <= cnt,
            cnt == end - start,
            start + cnt <= s@.len(),
            out@.len() == cap,
            cap == cnt + 8,
            forall|t: int| 0 <= t < i ==> out@[t] == s@[start + t],
        decreases cnt - i,
    {
        vset_unchecked(&mut out, i, get_unchecked(s, start + i));
        i = i + 1;
    }
    proof {
        lemma_fold_shift(s@, out@, start as int, cnt as int, 0);
    }
    let mut acc: u64 = 0;
    let mut j: usize = 0;
    while j < cnt
        invariant
            j <= cnt,
            cnt <= out@.len(),
            acc == fold_out(out@, 0, j as int, 0),
        decreases cnt - j,
    {
        acc = acc.wrapping_mul(31).wrapping_add(vget_unchecked(&out, j) as u64);
        j = j + 1;
    }
    acc = acc.wrapping_mul(31).wrapping_add(cnt as u64);
    assert(acc == fold_out(s@, start as int, end as int, 0).wrapping_mul(31).wrapping_add(
        cnt as u64,
    ));
    acc ^ tally(cap)
}

// ---------------------------------------------------------------- driver ----
fn main() {
    let (n_iters, stride_w, bytes) = load_input();
    // SLB-DRIVER-BEGIN
    let n_blob: usize = bytes.len();
    let buf: &[u8] = bytes.as_slice();
    let mut acc: u64 = 0;
    if stride_w >= 9 && stride_w <= n_blob as u64 {
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
                9 <= stride <= n_blob,
                buf@.len() == n_blob,
                nwin == n_blob / stride,
                nwin >= 1,
            decreases n_iters - it,
        {
            // Ghost only: `k` must land inside the blob. Two nonlinear steps, so
            // Z3 needs both spelled out. Erases at compile time -- R4 and R5
            // stay byte-identical.
            proof {
                let pr: int = (acc as int) * (nwin as int);
                assert((acc as u128) * (nwin as u128) <= (u64::MAX as u128) * (u64::MAX
                    as u128)) by (nonlinear_arith)
                    requires
                        acc <= u64::MAX,
                        nwin <= u64::MAX,
                ;
                assert(vstd::arithmetic::power2::pow2(64) == 0x1_0000_0000_0000_0000nat) by {
                    vstd::arithmetic::power2::lemma2_to64_rest();
                }
                assert(pr < (nwin as int) * 0x1_0000_0000_0000_0000int) by (nonlinear_arith)
                    requires
                        pr == (acc as int) * (nwin as int),
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
            // (`.memory/04-verus.md`).
            assert(r == strcut_fold(buf@, (k * stride) as int, stride as int));
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    emit(acc);
}

} // verus!
