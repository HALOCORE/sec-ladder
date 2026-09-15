//! ph97 rung R5 -- unsafe + Verus.
//!
//! Same exec code as `unsafe.rs`, plus the proof that licenses it. What is
//! proved, and it is a VALUE postcondition rather than a memory-safety-only
//! retreat:
//!
//!     requires  off + len <= buf@.len(),  REC <= len
//!     ensures   r == s_fold(buf@, off as int, len as int)
//!
//! `s_fold` is `mb_get_info` with `f7326d627962` applied, spelled as recursive
//! spec functions over the call stream, and `model.py` re-derives the same
//! `u64` from a different decomposition.
//!
//! ⭐⭐⭐ **THE OBLIGATION THIS ROW IS ABOUT IS `I12/O3`, IT IS ONE CONJUNCT,
//! AND IT IS ON THE COMPARE'S OWN ACCESSOR.** `opt_get`'s `requires` is
//! `t.is_some()` -- *a possibly-NULL pointer must not be passed to a callee
//! that dereferences it without testing it*, with the possibility in the TYPE.
//! It is discharged at all five call sites from ONE fact: `typ.is_none() ||`,
//! which is `f7326d627962` (Antony Dovgal, 2005-01-28, *"MFB: fix #31732"*).
//!
//! ⚠⚠ **AND IT IS *NOT* DISCHARGED FROM THE PARSER'S POSTCONDITION, WHICH IS
//! THE POINT.** `parse_va_args` returns `true` -- SUCCESS -- with `*wrote ==
//! false` whenever `num_args == 0`, and its `ensures` says so in terms:
//! `*final(wrote) == (num_args == 1)`. **The parser's contract is exactly
//! strong enough to prove that `typ` may be `None`, and that is the defect.**
//! Only the 2005 guard rules `None` out at the compare. `controls/negatives.py
//! --emit r1` deletes `typ.is_none() ||` from this file and that mutant must
//! FAIL to verify.
//!
//! ⭐ **THE SPEC SCANNER'S INVARIANT IS THE MECHANISM, WRITTEN AS A PROOF.**
//! `parse_va_args`'s first loop carries
//!
//!     s == 0 ==> min_num_args == -1 && max_num_args == 0,
//!     s == 1 ==> min_num_args ==  0 && max_num_args == 0,
//!     s == 2 ==> min_num_args ==  0 && max_num_args == 1,
//!
//! and the middle line IS `zend_API.c:486` -- `min_num_args = max_num_args`
//! executed while `max_num_args` is still zero, because `"|s"` puts the `|`
//! first. A reader who wants the bug in three lines can read those three.
//!
//! ⚠ The other six unchecked classes rest on facts that have nothing to do with
//! PHP: `i < NTYP` on a frame-width array, `i < v@.len()` and `o + n <=
//! v@.len()` on the blob, and `k < NSEL` / `k < NENC` on two tables indexed by
//! literals. `../NOTES.md` §10 keeps them apart, because an editor who deleted
//! the 2005 patch would be removing the precondition of exactly ONE of them.

use vstd::prelude::*;

// Plain-Rust I/O helpers. Outside `verus!`, so Verus treats the whole module as
// external (external-by-default). Reached only through `load_input`/`emit`.
#[path = "../../common/driver.rs"]
mod driver;

/// ⭐⭐⭐ **P1, AS A COMPILE-TIME ASSERTION RATHER THAN A CLAIM.** Outside
/// `verus!` on purpose: it is a fact about the LAYOUT rustc chooses and not
/// something Verus decides, and it is carried by all four Rust rungs
/// byte-identically so that a layout change fails the BUILD of every one of
/// them rather than quietly moving a number.
const _: () = assert!(
    core::mem::size_of::<Option<&[u8; 21]>>() == core::mem::size_of::<&[u8; 21]>()
);
const _: () = assert!(core::mem::size_of::<Option<&[u8; 21]>>() == 8);

verus! {

// `group_slice_axioms` gives `slice@.len() == spec_slice_len(slice)`, hence
// `slice@.len() <= usize::MAX`, without which `o + n` cannot be shown not to
// overflow. `lemma_u128_shr_is_div` turns `x >> 64` into `x / 2^64` for the
// driver's multiply-shift barrier bound; the mul group is what the window-offset
// bound `k * stride + stride <= n_blob` needs.
broadcast use {
    vstd::slice::group_slice_axioms,
    vstd::bits::lemma_u128_shr_is_div,
    vstd::arithmetic::mul::lemma_mul_inequality,
};

// ------------------------------------------------------- shared arithmetic --
// Identical text in all four Rust rungs and re-derived independently in
// model.py.

pub const REC: usize = 24;

pub const STRMAX: usize = 20;

pub const NTYP: usize = 21;

pub const IS_NULL: u8 = 0;

pub const IS_BOOL: u8 = 1;

pub const IS_STRING: u8 = 2;

pub const TAG_FALSE: u64 = 0x0F;

pub const TAG_ALL: u64 = 0x0A;

pub const TAG_SEL1: u64 = 0x10;

pub const TAG_SEL2: u64 = 0x11;

pub const TAG_SEL3: u64 = 0x12;

pub const TAG_SEL4: u64 = 0x13;

pub const ENC_INVALID: usize = 0;

pub const ENC_PASS: usize = 1;

pub const ENC_8859_1: usize = 2;

pub const NENC: usize = 3;

pub const G_INTERNAL: usize = ENC_8859_1;

pub const G_HTTP_IN: usize = ENC_INVALID;

pub const G_HTTP_OUT: usize = ENC_PASS;

pub const G_OVERLOAD: usize = ENC_PASS;

/// `mbfl_no2encoding` composed with `mbfl_no_encoding2name` --
/// mbfl_encoding.c:253-265. Index 0 IS the `return "";` at `:261`.
pub const NAMES: [[u8; NTYP]; NENC] = [
    *b"\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0",
    *b"pass\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0",
    *b"ISO-8859-1\0\0\0\0\0\0\0\0\0\0\0",
];

/// `mb_get_info`'s own type spec -- mbstring.c:3215. ⛔ THE `|` IS FIRST AND
/// THAT IS THE WHOLE DEFECT.
pub const SPEC: [u8; 2] = [b'|', b's'];

pub const NSEL: usize = 5;

/// The five selectors, in `mb_get_info`'s own chain order.
pub const SELS: [[u8; NTYP]; NSEL] = [
    *b"all\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0",
    *b"internal_encoding\0\0\0\0",
    *b"http_input\0\0\0\0\0\0\0\0\0\0\0",
    *b"http_output\0\0\0\0\0\0\0\0\0\0",
    *b"func_overload\0\0\0\0\0\0\0\0",
];

// ------------------------------------------------------------------ spec ----
//
// ⚠ `s_sel` and `s_name` are the TABLES' OWN VIEWS and not a second copy of
// their bytes. Verus does not evaluate the literals, and it does not need to:
// the postcondition is *the kernel computes this fold of the blob AND of these
// two tables*, and the tables are in the source above. `model.py` carries its
// own transcription and `controls/tables.py` diffs the two, which is what would
// catch a typo in either.

// ⚠⚠ `#[verifier::opaque]` ON `s_all`, `s_step` AND `s_false` IS A MEASURED
// DECISION, NOT A STYLE. Without it `kernel`'s loop unfolds `s_run` -> `s_step`
// -> `s_all` -> eight `s_fold_str` recursions -> `s_cmp` recursions on EVERY
// iteration, and the budget it needed was both large and NON-MONOTONE --
// `rlimit` 10 passed, 30 FAILED and 60 passed plain, which is a proof that
// passes on one side of a coin flip. Opaque, the three are revealed in
// `get_info` and nowhere else, so `kernel`'s unfolding stops at `s_step` and
// never reaches the compare or the fold. ⚠ `s_cmp` and `s_fold_str` are NOT
// opaque and do not need to be: nothing reaches them except through these
// three. ../NOTES.md §11 has the bisect, before and after.
pub open spec fn s_sel(k: int) -> Seq<u8> {
    SELS[k]@
}

pub open spec fn s_name(k: int) -> Seq<u8> {
    NAMES[k]@
}

pub open spec fn zeros21() -> Seq<u8> {
    Seq::new(NTYP as nat, |i: int| 0u8)
}

/// NUL-pad a body out to the frame width.
pub open spec fn s_pad(s: Seq<u8>) -> Seq<u8> {
    s + Seq::new((NTYP - s.len()) as nat, |i: int| 0u8)
}

/// `tolower` in the C locale.
pub open spec fn s_lower(c: u8) -> u8 {
    if 65 <= c && c <= 90 {
        (c + 32) as u8
    } else {
        c
    }
}

/// `strcasecmp(3)` over two frame-width operands.
pub open spec fn s_cmp(a: Seq<u8>, b: Seq<u8>, i: int) -> int
    decreases NTYP - i,
{
    if i >= NTYP {
        0int
    } else {
        let ca = s_lower(a[i]);
        let cb = s_lower(b[i]);
        if ca != cb {
            ca as int - cb as int
        } else if ca == 0 {
            0int
        } else {
            s_cmp(a, b, i + 1)
        }
    }
}

/// Fold one NUL-terminated name into the checksum, terminator included.
pub open spec fn s_fold_str(acc: u64, s: Seq<u8>, i: int) -> u64
    decreases NTYP - i,
{
    if i >= NTYP || s[i] == 0 {
        acc.wrapping_mul(31).wrapping_add(1)
    } else {
        s_fold_str(acc.wrapping_mul(31).wrapping_add(s[i] as u64), s, i + 1)
    }
}

// ---- one 24-byte call record ----------------------------------------------

pub open spec fn s_argc(b: Seq<u8>) -> int {
    (b[0] % 3) as int
}

pub open spec fn s_ty(b: Seq<u8>) -> u8 {
    (b[1] % 4) as u8
}

pub open spec fn s_len(b: Seq<u8>) -> int {
    (b[2] % 21) as int
}

pub open spec fn s_lval(b: Seq<u8>) -> u8 {
    b[3]
}

/// Which type tags the `'s'` arm of `zend_parse_arg` CONVERTS -- zend_API.c:
/// 310-317 plus the IS_NULL fall-through at :302-308. IS_ARRAY is the one it
/// refuses at :330.
pub open spec fn s_type_ok(ty: u8) -> bool {
    ty == IS_NULL || ty == IS_BOOL || ty == IS_STRING
}

/// `convert_to_string_ex`'s result, before padding.
pub open spec fn s_body_of(ty: u8, lval: u8, ln: int, val: Seq<u8>) -> Seq<u8> {
    if ty == IS_STRING {
        val.subrange(0, ln)
    } else if ty == IS_BOOL {
        if lval % 2 == 1 {
            seq![49u8]
        } else {
            Seq::empty()
        }
    } else {
        Seq::empty()
    }
}

pub open spec fn s_body(b: Seq<u8>) -> Seq<u8> {
    s_body_of(s_ty(b), s_lval(b), s_len(b), b.subrange(4, 4 + STRMAX))
}

/// What `typ` points at when the parser wrote it.
pub open spec fn s_frame(b: Seq<u8>) -> Seq<u8> {
    s_pad(s_body(b))
}

/// ⛔⛔ **THE GUARD, AND WHAT IT DOES AND DOES NOT DECIDE.** `zend_parse_
/// parameters` returns SUCCESS unless the count test refuses (`num_args > 1`,
/// because `"|s"` gives `min == 0` and `max == 1`) or the supplied argument is
/// of a type the `'s'` arm will not convert. **`num_args == 0` is SUCCESS**, and
/// nothing here says anything about whether the out-parameter was written.
pub open spec fn s_ok(b: Seq<u8>) -> bool {
    s_argc(b) <= 1 && (s_argc(b) == 0 || s_type_ok(s_ty(b)))
}

/// ⛔ ... and THIS is the proposition `mbstring.c:3219` needs, which `s_ok` is
/// not. They come apart at exactly one point: `s_argc(b) == 0`.
pub open spec fn s_wrote(b: Seq<u8>) -> bool {
    s_argc(b) == 1
}

pub open spec fn s_match(b: Seq<u8>, k: int) -> bool {
    s_cmp(s_sel(k), s_frame(b), 0) == 0
}

/// `array_init` plus the four `add_assoc_string`s -- mbstring.c:3220-3232.
/// A fixed-size output: four keys, four values, no allocation in any rung.
#[verifier::opaque]
pub open spec fn s_all(acc: u64) -> u64 {
    let a0 = acc.wrapping_mul(31).wrapping_add(TAG_ALL);
    let a1 = s_fold_str(a0.wrapping_mul(31).wrapping_add(1), s_sel(1), 0);
    let a2 = s_fold_str(a1, s_name(G_INTERNAL as int), 0);
    let a3 = s_fold_str(a2.wrapping_mul(31).wrapping_add(2), s_sel(2), 0);
    let a4 = s_fold_str(a3, s_name(G_HTTP_IN as int), 0);
    let a5 = s_fold_str(a4.wrapping_mul(31).wrapping_add(3), s_sel(3), 0);
    let a6 = s_fold_str(a5, s_name(G_HTTP_OUT as int), 0);
    let a7 = s_fold_str(a6.wrapping_mul(31).wrapping_add(4), s_sel(4), 0);
    s_fold_str(a7, s_name(G_OVERLOAD as int), 0)
}

/// One call's contribution to the checksum -- mbstring.c:3209-3252 with
/// `f7326d627962`.
#[verifier::opaque]
pub open spec fn s_step(b: Seq<u8>, acc: u64) -> u64 {
    if !s_ok(b) {
        acc.wrapping_mul(31).wrapping_add(TAG_FALSE)
    } else if !s_wrote(b) || s_match(b, 0) {
        s_all(acc)
    } else if s_match(b, 1) {
        s_fold_str(acc.wrapping_mul(31).wrapping_add(TAG_SEL1), s_name(G_INTERNAL as int), 0)
    } else if s_match(b, 2) {
        s_fold_str(acc.wrapping_mul(31).wrapping_add(TAG_SEL2), s_name(G_HTTP_IN as int), 0)
    } else if s_match(b, 3) {
        s_fold_str(acc.wrapping_mul(31).wrapping_add(TAG_SEL3), s_name(G_HTTP_OUT as int), 0)
    } else if s_match(b, 4) {
        s_fold_str(acc.wrapping_mul(31).wrapping_add(TAG_SEL4), s_name(G_OVERLOAD as int), 0)
    } else {
        acc.wrapping_mul(31).wrapping_add(TAG_FALSE)
    }
}

/// Whether this call took one of the two `RETURN_FALSE` arms (`:3216`, `:3250`).
#[verifier::opaque]
pub open spec fn s_false(b: Seq<u8>) -> bool {
    if !s_ok(b) {
        true
    } else if !s_wrote(b) || s_match(b, 0) || s_match(b, 1) || s_match(b, 2) || s_match(b, 3)
        || s_match(b, 4) {
        false
    } else {
        true
    }
}

pub open spec fn s_rec(win: Seq<u8>, r: int) -> Seq<u8> {
    win.subrange(r * (REC as int), r * (REC as int) + (REC as int))
}

/// Recursion is BACKWARDS so that a forward loop's invariant is
/// `acc == s_run(win, r)` and not a quantifier.
pub open spec fn s_run(win: Seq<u8>, r: int) -> u64
    decreases r,
{
    if r <= 0 {
        0u64
    } else {
        s_step(s_rec(win, r - 1), s_run(win, r - 1))
    }
}

pub open spec fn s_nfalse(win: Seq<u8>, r: int) -> u64
    decreases r,
{
    if r <= 0 {
        0u64
    } else if s_false(s_rec(win, r - 1)) {
        s_nfalse(win, r - 1).wrapping_add(1)
    } else {
        s_nfalse(win, r - 1)
    }
}

/// What the kernel must return. `model.py::ph97_fold` re-derives it.
pub open spec fn s_fold(buf: Seq<u8>, off: int, ln: int) -> u64 {
    let win = buf.subrange(off, off + ln);
    let nrec = ln / (REC as int);
    s_run(win, nrec).wrapping_mul(31).wrapping_add(s_nfalse(win, nrec))
}

// ------------------------------------------------------- TRUSTED, item 1/9 --
// ⭐⭐⭐ THE ROW'S OWN TRUSTED ITEM, AND `I12/O3` WORD FOR WORD. The `requires`
// is what makes it sound and the `ensures` is what makes it useful; both are
// trusted, and `../NOTES.md` §10 argues each one.
#[verifier::external_body]
#[inline(always)]
fn opt_get(t: Option<&[u8; NTYP]>) -> (r: &[u8; NTYP])
    requires
        t.is_some(),
    ensures
        r@ == t.unwrap()@,
{
    unsafe { t.unwrap_unchecked() }
}

// THE VERIFIED TWIN of trusted item 1 (`harness/check.py` step 5c-twin). Same
// signature and same contract, character for character -- the gate lifts both
// and diffs them, so a trusted item whose contract drifted from what a safe
// implementation can meet is caught.
#[cfg(slb_twin)]
#[inline(always)]
fn slb_twin_opt_get(t: Option<&[u8; NTYP]>) -> (r: &[u8; NTYP])
    requires
        t.is_some(),
    ensures
        r@ == t.unwrap()@,
{
    t.unwrap()
}

// ------------------------------------------------------- TRUSTED, item 2/9 --
#[verifier::external_body]
#[inline(always)]
fn aget(v: &[u8; NTYP], i: usize) -> (r: u8)
    requires
        i < NTYP,
    ensures
        r == v@[i as int],
{
    unsafe { *v.get_unchecked(i) }
}

#[cfg(slb_twin)]
#[inline(always)]
fn slb_twin_aget(v: &[u8; NTYP], i: usize) -> (r: u8)
    requires
        i < NTYP,
    ensures
        r == v@[i as int],
{
    v[i]
}

// ------------------------------------------------------- TRUSTED, item 3/9 --
// ⚠ `x: u8` is a PURE VALUE and needs no precondition; the unchecked
// operation's definedness depends on `i` and on nothing about the byte being
// written. The `ensures` names the WHOLE post-state -- `old(v)@.update(i, x)` --
// so a body that also clobbered `v[i + 1]` could not satisfy it. That
// completeness is the thing a write wrapper's contract can get wrong, and it is
// why Miri is required on this row (../spec.md `miri`).
#[verifier::external_body]
#[inline(always)]
fn fset(v: &mut [u8; NTYP], i: usize, x: u8)
    requires
        i < NTYP,
    ensures
        final(v)@ == old(v)@.update(i as int, x),
{
    unsafe { *v.get_unchecked_mut(i) = x };
}

#[cfg(slb_twin)]
#[inline(always)]
fn slb_twin_fset(v: &mut [u8; NTYP], i: usize, x: u8)
    requires
        i < NTYP,
    ensures
        final(v)@ == old(v)@.update(i as int, x),
{
    v[i] = x;
}

// ------------------------------------------------------- TRUSTED, item 4/9 --
#[verifier::external_body]
#[inline(always)]
fn sget(v: &[u8], i: usize) -> (r: u8)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    unsafe { *v.get_unchecked(i) }
}

#[cfg(slb_twin)]
#[inline(always)]
fn slb_twin_sget(v: &[u8], i: usize) -> (r: u8)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    v[i]
}

// ------------------------------------------------------- TRUSTED, item 5/9 --
#[verifier::external_body]
#[inline(always)]
fn wsub(v: &[u8], o: usize, n: usize) -> (r: &[u8])
    requires
        o + n <= v@.len(),
    ensures
        r@ == v@.subrange(o as int, (o + n) as int),
{
    unsafe { v.get_unchecked(o..o + n) }
}

#[cfg(slb_twin)]
#[inline(always)]
fn slb_twin_wsub(v: &[u8], o: usize, n: usize) -> (r: &[u8])
    requires
        o + n <= v@.len(),
    ensures
        r@ == v@.subrange(o as int, (o + n) as int),
{
    assert(v@.len() == vstd::slice::spec_slice_len(v));
    &v[o..o + n]
}

// ------------------------------------------------------- TRUSTED, item 6/9 --
#[verifier::external_body]
#[inline(always)]
fn sel_get(k: usize) -> (r: &'static [u8; NTYP])
    requires
        k < NSEL,
    ensures
        r@ == s_sel(k as int),
{
    unsafe { SELS.get_unchecked(k) }
}

#[cfg(slb_twin)]
#[inline(always)]
fn slb_twin_sel_get(k: usize) -> (r: &'static [u8; NTYP])
    requires
        k < NSEL,
    ensures
        r@ == s_sel(k as int),
{
    &SELS[k]
}

// ------------------------------------------------------- TRUSTED, item 7/9 --
#[verifier::external_body]
#[inline(always)]
fn name_get(k: usize) -> (r: &'static [u8; NTYP])
    requires
        k < NENC,
    ensures
        r@ == s_name(k as int),
{
    unsafe { NAMES.get_unchecked(k) }
}

#[cfg(slb_twin)]
#[inline(always)]
fn slb_twin_name_get(k: usize) -> (r: &'static [u8; NTYP])
    requires
        k < NENC,
    ensures
        r@ == s_name(k as int),
{
    &NAMES[k]
}

// ------------------------------------------------------- TRUSTED, item 8/9 --
#[verifier::external_body]
fn load_input() -> (r: (u64, u64, Vec<u8>)) {
    let path = driver::arg_path();
    let inp = driver::load(&path);
    let (stride_w, bytes) = driver::head1_u64_bytes(&inp);
    (inp.n_iters, stride_w, bytes)
}

// ------------------------------------------------------- TRUSTED, item 9/9 --
// `println!` is not verifiable; no `ensures`. Counted with the eight above --
// every `external_body` item is TCB, not just the interesting ones
// (`.memory/04-verus.md`).
#[verifier::external_body]
fn emit(acc: u64) {
    driver::emit(acc);
}

// ---------------------------------------------------------------- kernel ----

#[inline(always)]
fn lower(c: u8) -> (r: u8)
    ensures
        r == s_lower(c),
{
    if c >= b'A' && c <= b'Z' {
        c + 32
    } else {
        c
    }
}

/// `strcasecmp(3)`, C locale -- IN THE KERNEL, not in libc. Same exec code as
/// `unsafe.rs`.
#[inline(always)]
fn strcasecmp(a: &[u8; NTYP], b: &[u8; NTYP]) -> (r: i32)
    ensures
        r as int == s_cmp(a@, b@, 0),
{
    let mut i: usize = 0;
    while i < NTYP
        invariant
            i <= NTYP,
            s_cmp(a@, b@, 0) == s_cmp(a@, b@, i as int),
        decreases NTYP - i,
    {
        let ca: u8 = lower(aget(a, i));
        let cb: u8 = lower(aget(b, i));
        if ca != cb {
            return ca as i32 - cb as i32;
        }
        if ca == 0 {
            return 0;
        }
        i = i + 1;
    }
    0
}

/// Fold one NUL-terminated name into the checksum. Same exec code as
/// `unsafe.rs`.
#[inline(always)]
fn fold_str(acc: u64, s: &[u8; NTYP]) -> (r: u64)
    ensures
        r == s_fold_str(acc, s@, 0),
{
    let mut a: u64 = acc;
    let mut i: usize = 0;
    while i < NTYP
        invariant
            i <= NTYP,
            s_fold_str(acc, s@, 0) == s_fold_str(a, s@, i as int),
        decreases NTYP - i,
    {
        let c: u8 = aget(s, i);
        if c == 0 {
            return a.wrapping_mul(31).wrapping_add(1);
        }
        a = a.wrapping_mul(31).wrapping_add(c as u64);
        i = i + 1;
    }
    a.wrapping_mul(31).wrapping_add(1)
}

/// One argument, as `zend_parse_arg` sees it.
pub struct Zval<'a> {
    pub ty: u8,
    pub lval: u8,
    pub len: usize,
    pub val: &'a [u8],
}

/// `zend_parse_arg`, the `'s'` arm -- zend_API.c:297-333. Same exec code as
/// `unsafe.rs`.
#[inline(always)]
fn parse_arg(arg: &Zval, frame: &mut [u8; NTYP], n_out: &mut usize) -> (r: bool)
    requires
        old(frame)@ == zeros21(),
        arg.val@.len() == STRMAX,
        arg.len <= STRMAX,
    ensures
        r == s_type_ok(arg.ty),
        r ==> *final(n_out) <= STRMAX,
        r ==> final(frame)@ == s_pad(s_body_of(arg.ty, arg.lval, arg.len as int, arg.val@)),
{
    let mut n: usize = 0;
    if arg.ty == IS_STRING {
        // convert_to_string_ex, zend_API.c:314
        while n < arg.len && n < STRMAX
            invariant
                n <= arg.len,
                arg.len <= STRMAX,
                arg.val@.len() == STRMAX,
                frame@ == s_pad(arg.val@.subrange(0, n as int)),
            decreases STRMAX - n,
        {
            fset(frame, n, sget(arg.val, n));
            assert(frame@ =~= s_pad(arg.val@.subrange(0, n + 1)));
            n = n + 1;
        }
    } else if arg.ty == IS_BOOL {
        if arg.lval % 2 == 1 {
            fset(frame, 0, b'1');
            assert(frame@ =~= s_pad(seq![49u8]));
            n = 1;
        }
    } else if arg.ty != IS_NULL {
        return false; // zend_API.c:330 -- "string", then E_WARNING, then FAILURE
    }
    fset(frame, n, 0);
    assert(frame@ =~= s_pad(s_body_of(arg.ty, arg.lval, arg.len as int, arg.val@)));
    *n_out = n;
    true
}

/// `zend_parse_va_args` -- zend_API.c:463-549. `false` is FAILURE. Same exec
/// code as `unsafe.rs`.
///
/// ⛔⛔ THE SPEC SCANNER AND THE COUNT TEST ARE UPSTREAM'S, CHARACTER FOR
/// CHARACTER, BECAUSE THEY ARE THE MECHANISM -- and here the mechanism is a
/// LOOP INVARIANT: after one character of `"|s"` the running `max_num_args` is
/// still 0, so `min_num_args = max_num_args` at `:486` makes the minimum ZERO.
#[inline(always)]
fn parse_va_args(
    num_args: usize,
    type_spec: &[u8],
    arg: &Zval,
    frame: &mut [u8; NTYP],
    wrote: &mut bool,
    typ_len: &mut i32,
) -> (r: bool)
    requires
        old(frame)@ == zeros21(),
        *old(wrote) == false,
        type_spec@ == seq![124u8, 115u8],
        arg.val@.len() == STRMAX,
        arg.len <= STRMAX,
        num_args <= 2,
    ensures
        r == (num_args <= 1 && (num_args == 0 || s_type_ok(arg.ty))),
        r ==> *final(wrote) == (num_args == 1),
        r && *final(wrote) ==> final(frame)@ == s_pad(s_body_of(arg.ty, arg.lval, arg.len as int, arg.val@)),
{
    let mut min_num_args: i32 = -1;  // :467
    let mut max_num_args: i32 = 0;   // :468
    let mut s: usize = 0;
    while s < type_spec.len()
        invariant
            type_spec@ == seq![124u8, 115u8],
            s <= 2,
            s == 0 ==> (min_num_args == -1 && max_num_args == 0),
            s == 1 ==> (min_num_args == 0 && max_num_args == 0),
            s == 2 ==> (min_num_args == 0 && max_num_args == 1),
        decreases type_spec@.len() - s,
    {
        // :474
        let c: u8 = sget(type_spec, s);
        if c == b'l' || c == b'd' || c == b's' || c == b'b' || c == b'r' || c == b'a' || c == b'o'
            || c == b'O' || c == b'z' || c == b'Z' {
            max_num_args = max_num_args + 1;  // :482
        } else if c == b'|' {
            min_num_args = max_num_args;  // :486
        } else if c == b'/' || c == b'!' {
            // Pass -- :489-492
        } else {
            return false;  // :503
        }
        s = s + 1;
    }
    if min_num_args < 0 {
        // :507
        min_num_args = max_num_args;
    }
    if (num_args as i32) < min_num_args || (num_args as i32) > max_num_args {
        return false;  // :511 -> :524
    }
    let mut n: usize = 0;
    let mut na: usize = num_args;
    let mut sp: usize = 0;
    while na > 0
        invariant
            na <= num_args,
            num_args <= 1,
            sp <= 2,
            !*wrote ==> sp == 0,
            arg.val@.len() == STRMAX,
            arg.len <= STRMAX,
            *wrote == (na < num_args),
            !*wrote ==> frame@ == zeros21(),
            *wrote ==> s_type_ok(arg.ty),
            *wrote ==> frame@ == s_pad(s_body_of(arg.ty, arg.lval, arg.len as int, arg.val@)),
        decreases na,
    {
        // :537
        na = na - 1;
        if sp < type_spec.len() && sget(type_spec, sp) == b'|' {
            // :539
            sp = sp + 1;
        }
        if !parse_arg(arg, frame, &mut n) {
            return false;  // :543
        }
        *wrote = true;
        *typ_len = n as i32;  // :316
        sp = sp + 1;
    }
    true  // :548
}

/// `PHP_FUNCTION(mb_get_info)` -- mbstring.c:3209-3252, plus `f7326d627962`.
/// Same exec code as `unsafe.rs`.
#[inline(always)]
fn get_info(b: &[u8], acc: u64, falses: &mut u64) -> (r: u64)
    requires
        b@.len() == REC,
    ensures
        r == s_step(b@, acc),
        s_false(b@) ==> *final(falses) == (*old(falses)).wrapping_add(1),
        !s_false(b@) ==> *final(falses) == *old(falses),
{
    reveal(s_step);
    reveal(s_false);
    reveal(s_all);
    // ⭐⭐ TWO INDEPENDENT BYTES. `num_args` is *was an argument supplied?*;
    // `ty` is *is it well-typed?*. A kernel that derived one from the other
    // would have deleted the mechanism.
    let num_args: usize = (sget(b, 0) % 3) as usize;
    let arg = Zval {
        ty: sget(b, 1) % 4,
        len: (sget(b, 2) % ((STRMAX + 1) as u8)) as usize,
        lval: sget(b, 3),
        val: wsub(b, 4, STRMAX),
    };
    let mut frame: [u8; NTYP] = [0u8; NTYP];
    assert(frame@ =~= zeros21());
    // :3211 `char *typ = NULL;` -- in Rust the absence is in the TYPE, and
    // `wrote` is the one bit `typ = NULL` encodes: *did the write loop run?*
    let mut wrote: bool = false;
    // :3212 `int typ_len;`. Upstream leaves it UNINITIALISED and never reads
    // it; this rung sets it and never reads it either. ../NOTES.md §3.
    let mut typ_len: i32 = 0;
    let spec_str: &[u8] = &SPEC;
    assert(spec_str@ =~= seq![124u8, 115u8]);
    if !parse_va_args(num_args, spec_str, &arg, &mut frame, &mut wrote, &mut typ_len) {
        // :3215 -> :3216
        *falses = (*falses).wrapping_add(1);
        return acc.wrapping_mul(31).wrapping_add(TAG_FALSE);
    }
    let typ: Option<&[u8; NTYP]> = if wrote { Some(&frame) } else { None };
    assert(s_frame(b@) =~= s_pad(s_body_of(arg.ty, arg.lval, arg.len as int, arg.val@)));
    let mut a: u64 = acc;
    // ⭐⭐ :3219 WITH f7326d627962. `typ.is_none() ||` is the 2005 patch, and it
    // is what discharges `opt_get`'s `requires` at all five sites: here by
    // short-circuit, and in the four `else if` arms because reaching one means
    // this condition was FALSE.
    if typ.is_none() || strcasecmp(sel_get(0), opt_get(typ)) == 0 {
        a = a.wrapping_mul(31).wrapping_add(TAG_ALL);  // :3220 array_init
        // :3221-3231. The four `!= NULL` tests are upstream's and are DEAD --
        // `mbfl_no_encoding2name` returns "" and never NULL (../NOTES.md §4).
        a = fold_str(a.wrapping_mul(31).wrapping_add(1), sel_get(1));
        a = fold_str(a, name_get(G_INTERNAL));
        a = fold_str(a.wrapping_mul(31).wrapping_add(2), sel_get(2));
        a = fold_str(a, name_get(G_HTTP_IN));
        a = fold_str(a.wrapping_mul(31).wrapping_add(3), sel_get(3));
        a = fold_str(a, name_get(G_HTTP_OUT));
        a = fold_str(a.wrapping_mul(31).wrapping_add(4), sel_get(4));
        a = fold_str(a, name_get(G_OVERLOAD));
    } else if strcasecmp(sel_get(1), opt_get(typ)) == 0 {
        // :3233
        a = fold_str(a.wrapping_mul(31).wrapping_add(TAG_SEL1), name_get(G_INTERNAL));
    } else if strcasecmp(sel_get(2), opt_get(typ)) == 0 {
        // :3237
        a = fold_str(a.wrapping_mul(31).wrapping_add(TAG_SEL2), name_get(G_HTTP_IN));
    } else if strcasecmp(sel_get(3), opt_get(typ)) == 0 {
        // :3241
        a = fold_str(a.wrapping_mul(31).wrapping_add(TAG_SEL3), name_get(G_HTTP_OUT));
    } else if strcasecmp(sel_get(4), opt_get(typ)) == 0 {
        // :3245
        a = fold_str(a.wrapping_mul(31).wrapping_add(TAG_SEL4), name_get(G_OVERLOAD));
    } else {
        // :3249-3250
        *falses = (*falses).wrapping_add(1);
        return acc.wrapping_mul(31).wrapping_add(TAG_FALSE);
    }
    a
}

// Same exec code as unsafe.rs. Contract: ../spec.md.
//
// One `ensures`, and it is the VALUE, not the safety property. What makes it
// worth having: it is what stops the proof being vacuous, it is what `model.py`
// re-derives independently, and it is what forces the invariants to describe the
// parse and the chain rather than merely bound an index. A kernel that returned
// 0 unconditionally would satisfy every bounds obligation in this file.
// ⚠⚠ AND THERE IS NO MINIMUM-LENGTH `requires` EITHER, WHICH IS ALSO A
// MEASUREMENT. `REC <= len` was written here first and `check.py` stage 5c-req
// DELETED IT AND GOT 47 verified, 0 errors -- so no call site had to discharge
// it and the body never used it. It is decoration, and it came out. `nrec =
// len / REC` is zero for a short window, the loop does not run, and `s_fold`
// returns the same 0 the exec code does. ▶ The driver's `stride_w >= 24` is a
// STRUCTURAL choice about what a window is, not a precondition of this kernel.
//
// ⭐⭐⭐ THERE IS NO `#[verifier::rlimit]` ON THIS ROW AND THAT IS A MEASUREMENT,
// NOT AN OMISSION. Verus's default is 10. Bisected on this box with
// `controls/rlimit_bisect.sh`: **1** suffices, plain and under `--cfg
// slb_twin`, and every value from 1 to 30 gives 47/0 and 54/0. ⚠ Before the
// three `#[verifier::opaque]` attributes above it did NOT: the requirement was
// large and NON-MONOTONE -- 10 passed, 30 failed, 60 passed plain -- which is
// the symptom to recognise. An rlimit error is a shape, not a size.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> (r: u64)
    requires
        off + len <= buf@.len(),
    ensures
        r == s_fold(buf@, off as int, len as int),
{
    // Ghost only: mentioning `spec_slice_len` fires vstd's `axiom_spec_len`,
    // which is what tells the SMT solver a slice length fits in a `usize`.
    assert(buf@.len() == vstd::slice::spec_slice_len(buf));
    let win: &[u8] = &buf[off..off + len];
    assert(win@.len() == vstd::slice::spec_slice_len(win));
    assert(win@ =~= buf@.subrange(off as int, off + len));
    let nrec: usize = len / REC;
    // Ghost only: `nrec * REC <= len`, which is what bounds every record slice.
    proof {
        vstd::arithmetic::div_mod::lemma_fundamental_div_mod(len as int, REC as int);
    }
    assert(nrec * REC <= len);
    let mut acc: u64 = 0;
    let mut falses: u64 = 0;
    let mut r: usize = 0;
    while r < nrec
        invariant
            r <= nrec,
            nrec * REC <= len,
            win@.len() == len,
            acc == s_run(win@, r as int),
            falses == s_nfalse(win@, r as int),
        decreases nrec - r,
    {
        // Ghost only: record `r` is entirely inside the window. Nonlinear, so
        // Z3 needs it spelled out. Erases at compile time -- R4 and R5 stay
        // byte-identical.
        assert((r + 1) * REC <= nrec * REC) by (nonlinear_arith)
            requires
                r + 1 <= nrec,
        ;
        acc = get_info(wsub(win, r * REC, REC), acc, &mut falses);
        r = r + 1;
    }
    acc.wrapping_mul(31).wrapping_add(falses)
}

// ---------------------------------------------------------------- driver ----
fn main() {
    let (n_iters, stride_w, bytes) = load_input();
    // SLB-DRIVER-BEGIN
    let n_blob: usize = bytes.len();
    let buf: &[u8] = bytes.as_slice();
    let mut acc: u64 = 0;
    if stride_w >= 24 && stride_w <= n_blob as u64 {
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
                24 <= stride <= n_blob,
                buf@.len() == n_blob,
                nwin == n_blob / stride,
                nwin >= 1,
            decreases n_iters - it,
        {
            // Ghost only: `k` must land inside the blob. Two nonlinear steps, so
            // Z3 needs both spelled out.
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
            assert(r == s_fold(buf@, (k * stride) as int, stride as int));
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    emit(acc);
}

} // verus!
