//! ph96 rung R5 -- unsafe + Verus.
//!
//! Same exec code as `unsafe.rs`, plus the proof that licenses it. What is
//! proved, and it is a VALUE postcondition rather than a memory-safety-only
//! retreat:
//!
//!     requires  off + len <= buf@.len()
//!     ensures   r == s_fold(buf@, off as int, len as int)
//!
//! `s_fold` is the four `ArrayAccess` handlers with `cf020f133487` applied at
//! `:512` and the `:385` guard added at `:427`, spelled as recursive spec
//! functions over the call stream, and `model.py` re-derives the same `u64`
//! from a different decomposition.
//!
//! ⭐⭐⭐ **THE OBLIGATION THIS ROW IS ABOUT IS `I12/O1`, IT IS ONE CONJUNCT, AND
//! IT IS ON THE OUT-PARAMETER'S OWN ACCESSOR.** `opt_get`'s `requires` is
//! `t.is_some()` -- *a NULL return, sentinel, status code, **or NULL-able
//! out-parameter** must be tested*, with the possibility in the TYPE. It is
//! discharged at both call sites from a NULL test: `zend_object_handlers.c:385`
//! at the `read` shape, which upstream wrote, and the same spelling at `:427`,
//! which upstream did not.
//!
//! ⚠⚠ **AND IT IS *NOT* DISCHARGED FROM THE CALL'S STATUS, WHICH IS THE POINT.**
//! `call_method` returns `false` -- SUCCESS -- with `*wrote_out == false`
//! whenever the user method threw, and its `ensures` says so in terms:
//! `*final(wrote_out) == (!s_core(b@) && want_output && s_wrote(b@))`. **The
//! status's contract is exactly strong enough to prove that the out-parameter
//! may be absent, and that is the defect.** `zend_execute_API.c:592-594` is
//! upstream's own comment saying the same thing in English.
//! `controls/negatives.py --emit r1` deletes the `:385` test from this file and
//! that mutant must FAIL to verify.
//!
//! ⭐ **THE SENTINEL IS A SPEC FUNCTION, AND THE 2x2 IS FOUR LINES OF IT.**
//! `s_step`'s shape dispatch is the whole of `zend_object_handlers.c`'s four
//! handlers: shape 1 never looks, shape 0 and shape 2 test first, shape 3 after
//! `cf020f133487` never looks either. A reader who wants the row in one screen
//! can read `s_step`.
//!
//! ⚠ The other five unchecked classes rest on facts that have nothing to do with
//! PHP: `i < v@.len()` and `o + n <= v@.len()` on the blob, `k < 4` on a type
//! table indexed by a residue, and two I/O wrappers. `../NOTES.md` section 8
//! keeps them apart, because an editor who deleted a NULL test would be removing
//! the precondition of exactly ONE of them.

use vstd::prelude::*;

// Plain-Rust I/O helpers. Outside `verus!`, so Verus treats the whole module as
// external (external-by-default). Reached only through `load_input`/`emit`.
#[path = "../../common/driver.rs"]
mod driver;

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

pub const REC: usize = 16;

pub const STRMAX: usize = 10;

pub const SOFF: usize = 6;

pub const IS_NULL: u8 = 0;

pub const IS_LONG: u8 = 1;

pub const IS_BOOL: u8 = 3;

pub const IS_STRING: u8 = 6;

pub const TYTAB: [u8; 4] = [IS_NULL, IS_LONG, IS_BOOL, IS_STRING];

pub const TAG_READ: u64 = 0x11;

pub const TAG_UNDEF: u64 = 0x12;

pub const TAG_WRITE: u64 = 0x13;

pub const TAG_EXISTS: u64 = 0x14;

pub const TAG_UNSET: u64 = 0x15;

pub const TAG_CORE: u64 = 0x16;

/// `struct _zval_struct` -- Zend/zend.h:287-293, with `Z_STRVAL` kept as an
/// offset into the record rather than as a borrowed slice.
pub struct Zval {
    pub ty: u8,
    pub is_ref: u8,
    pub refcount: u32,
    pub lval: u8,
    pub slen: usize,
}

// ------------------------------------------------------------------ spec ----
//
// ⚠ `s_tytab` is the TABLE'S OWN VIEW and not a second copy of its bytes. Verus
// does not evaluate the literal and does not need to: the postcondition is *the
// kernel computes this fold of the blob AND of this table*, and the table is in
// the source above. `model.py` carries its own transcription and
// `controls/tables.py` diffs the two, which is what would catch a typo in
// either.
//
// ⚠⚠ `#[verifier::opaque]` ON `s_step` AND `s_fold_zval` IS A MEASURED
// DECISION, NOT A STYLE. Without it `kernel`'s loop unfolds `s_run` -> `s_step`
// -> `s_fold_zval` -> ten `s_fold_bytes` recursions on EVERY iteration.
// `controls/rlimit_bisect.sh` has the bisect, before and after.

pub open spec fn s_tytab(k: int) -> u8 {
    TYTAB[k]
}

pub open spec fn s_shape(b: Seq<u8>) -> int {
    (b[0] % 4) as int
}

/// ⛔ THE STATUS, AND IT *IS* TESTED -- `zend_interfaces.c:81`, `E_CORE_ERROR`.
pub open spec fn s_core(b: Seq<u8>) -> bool {
    b[1] % 5 == 0
}

/// ⛔ ... and THIS is the proposition `zend_object_handlers.c:513` needs, which
/// `s_core` is not. They come apart at exactly one point, and
/// `zend_execute_API.c:592-594`'s comment is upstream naming that point.
pub open spec fn s_wrote(b: Seq<u8>) -> bool {
    b[2] % 3 != 0
}

pub open spec fn s_ty(b: Seq<u8>) -> u8 {
    s_tytab((b[3] % 4) as int)
}

pub open spec fn s_lval(b: Seq<u8>) -> u8 {
    b[4]
}

pub open spec fn s_slen(b: Seq<u8>) -> int {
    (b[5] % 11) as int
}

/// `i_zend_is_true` -- Zend/zend_execute.h:68-112, narrowed to four type tags.
pub open spec fn s_true(b: Seq<u8>) -> u64 {
    if s_ty(b) == IS_NULL {
        0u64
    } else if s_ty(b) == IS_LONG || s_ty(b) == IS_BOOL {
        if s_lval(b) != 0 {
            1u64
        } else {
            0u64
        }
    } else if s_ty(b) == IS_STRING {
        if s_slen(b) == 0 || (s_slen(b) == 1 && b[SOFF as int] == 48u8) {
            0u64
        } else {
            1u64
        }
    } else {
        0u64
    }
}

pub open spec fn s_fold_bytes(acc: u64, b: Seq<u8>, i: int, n: int) -> u64
    decreases n - i,
{
    if i >= n {
        acc.wrapping_mul(31).wrapping_add(1)
    } else {
        s_fold_bytes(acc.wrapping_mul(31).wrapping_add(b[SOFF + i] as u64), b, i + 1, n)
    }
}

#[verifier::opaque]
pub open spec fn s_fold_zval(acc: u64, b: Seq<u8>) -> u64 {
    let a = acc.wrapping_mul(31).wrapping_add(s_ty(b) as u64);
    if s_ty(b) == IS_STRING {
        s_fold_bytes(a, b, 0, s_slen(b))
    } else {
        a.wrapping_mul(31).wrapping_add(s_lval(b) as u64)
    }
}

/// Did THIS CALL of `zend_call_method` release the value itself? True exactly
/// on the NO-OUTPUT contract (`zend_interfaces.c:88-93`) with something to
/// release.
pub open spec fn s_relc(b: Seq<u8>, want_output: bool) -> bool {
    !s_core(b) && !want_output && s_wrote(b)
}

/// Did this record release a returned value exactly once? `I16/O2` is *the
/// outputs of an aborted call must not be ... destroyed*, so this is the
/// quantity that obligation is about. Shape 0 hands the value to the VM
/// (`:395`) and does NOT release it; the other three do.
pub open spec fn s_rel1(b: Seq<u8>) -> bool {
    !s_core(b) && s_wrote(b) && s_shape(b) != 0
}

/// ⭐⭐⭐ **THE 2x2, AS FOUR ARMS OF ONE SPEC FUNCTION.** Shape 1 (`:413`) never
/// looks at the out-parameter; shape 0 (`:385`) tests it; shape 2 (`:427`) tests
/// it HERE and does not upstream; shape 3 (`:512` with `cf020f133487`) never
/// looks either. `../NOTES.md` section 5 has the scope of the second-limb claim.
#[verifier::opaque]
pub open spec fn s_step(b: Seq<u8>, acc: u64) -> u64 {
    if s_core(b) {
        acc.wrapping_mul(31).wrapping_add(TAG_CORE)
    } else if s_shape(b) == 1 {
        acc.wrapping_mul(31).wrapping_add(TAG_WRITE)
    } else if s_shape(b) == 0 {
        if !s_wrote(b) {
            acc.wrapping_mul(31).wrapping_add(TAG_UNDEF)
        } else {
            s_fold_zval(acc, b).wrapping_mul(31).wrapping_add(TAG_READ)
        }
    } else if s_shape(b) == 2 {
        if !s_wrote(b) {
            acc.wrapping_mul(31).wrapping_add(TAG_UNDEF)
        } else {
            acc.wrapping_mul(31).wrapping_add(TAG_EXISTS).wrapping_add(s_true(b))
        }
    } else {
        acc.wrapping_mul(31).wrapping_add(TAG_UNSET)
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

pub open spec fn s_nrel(win: Seq<u8>, r: int) -> u64
    decreases r,
{
    if r <= 0 {
        0u64
    } else if s_rel1(s_rec(win, r - 1)) {
        s_nrel(win, r - 1).wrapping_add(1)
    } else {
        s_nrel(win, r - 1)
    }
}

pub open spec fn s_ncore(win: Seq<u8>, r: int) -> u64
    decreases r,
{
    if r <= 0 {
        0u64
    } else if s_core(s_rec(win, r - 1)) {
        s_ncore(win, r - 1).wrapping_add(1)
    } else {
        s_ncore(win, r - 1)
    }
}

/// What the kernel must return. `model.py::ph96_fold` re-derives it.
pub open spec fn s_fold(buf: Seq<u8>, off: int, ln: int) -> u64 {
    let win = buf.subrange(off, off + ln);
    let nrec = ln / (REC as int);
    s_run(win, nrec).wrapping_mul(31).wrapping_add(s_nrel(win, nrec)).wrapping_mul(31).wrapping_add(
        s_ncore(win, nrec),
    )
}

// ------------------------------------------------------- TRUSTED, item 1/6 --
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

// THE VERIFIED TWIN of trusted item 1 (`harness/check.py` step 5c-twin). Same
// signature and same contract, character for character -- the gate lifts both
// and diffs them, so a trusted item whose contract drifted from what a safe
// implementation can meet is caught.
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

// ------------------------------------------------------- TRUSTED, item 2/6 --
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

// ------------------------------------------------------- TRUSTED, item 3/6 --
#[verifier::external_body]
#[inline(always)]
fn ty_get(k: usize) -> (r: u8)
    requires
        k < 4,
    ensures
        r == s_tytab(k as int),
{
    unsafe { *TYTAB.get_unchecked(k) }
}

#[cfg(slb_twin)]
#[inline(always)]
fn slb_twin_ty_get(k: usize) -> (r: u8)
    requires
        k < 4,
    ensures
        r == s_tytab(k as int),
{
    TYTAB[k]
}

// ------------------------------------------------------- TRUSTED, item 4/6 --
// ⭐⭐⭐ THE ROW'S OWN TRUSTED ITEM, AND `I12/O1` WORD FOR WORD. The `requires`
// is what makes it sound and the `ensures` is what makes it useful; both are
// trusted, and `../NOTES.md` section 8 argues each one.
#[verifier::external_body]
#[inline(always)]
fn opt_get<'a>(t: Option<&'a mut Zval>) -> (r: &'a mut Zval)
    requires
        t.is_some(),
    ensures
        *r == *t.unwrap(),
{
    unsafe { t.unwrap_unchecked() }
}

#[cfg(slb_twin)]
#[inline(always)]
fn slb_twin_opt_get<'a>(t: Option<&'a mut Zval>) -> (r: &'a mut Zval)
    requires
        t.is_some(),
    ensures
        *r == *t.unwrap(),
{
    t.unwrap()
}

// ------------------------------------------------------- TRUSTED, item 5/6 --
#[verifier::external_body]
fn load_input() -> (r: (u64, u64, Vec<u8>)) {
    let path = driver::arg_path();
    let inp = driver::load(&path);
    let (stride_w, bytes) = driver::head1_u64_bytes(&inp);
    (inp.n_iters, stride_w, bytes)
}

// ------------------------------------------------------- TRUSTED, item 6/6 --
// `println!` is not verifiable; no `ensures`. Counted with the five above --
// every `external_body` item is TCB, not just the interesting ones
// (`.memory/04-verus.md`).
#[verifier::external_body]
fn emit(acc: u64) {
    driver::emit(acc);
}

// ---------------------------------------------------------------- kernel ----

/// `_zval_ptr_dtor` -- zend_execute_API.c:384-396. Same exec code as
/// `unsafe.rs`.
#[inline(always)]
fn zval_ptr_dtor(z: &mut Zval, n_rel: &mut u64)
    requires
        old(z).refcount >= 1,
    ensures
        old(z).refcount == 1 ==> *final(n_rel) == (*old(n_rel)).wrapping_add(1),
        old(z).refcount != 1 ==> *final(n_rel) == *old(n_rel),
{
    z.refcount = z.refcount - 1;  // :389
    if z.refcount == 0 {
        // :390-392 zval_dtor + safe_free_zval_ptr_rel
        *n_rel = n_rel.wrapping_add(1);
    } else if z.refcount == 1 {
        // :393-394. Upstream's second arm, kept with its reason: a method
        // return in this row always arrives at refcount 1, so this arm is
        // unreachable here. `../NOTES.md` section 6.
        z.is_ref = 0;
    }
}

/// `i_zend_is_true` -- Zend/zend_execute.h:68-112. Same exec code as
/// `unsafe.rs`.
#[inline(always)]
fn is_true(z: &Zval, b: &[u8]) -> (r: u64)
    requires
        b@.len() == REC,
        z.ty == s_ty(b@),
        z.lval == s_lval(b@),
        z.slen == s_slen(b@),
    ensures
        r == s_true(b@),
{
    if z.ty == IS_NULL {
        0  // :74
    } else if z.ty == IS_LONG || z.ty == IS_BOOL {
        if z.lval != 0 {
            1  // :79
        } else {
            0
        }
    } else if z.ty == IS_STRING {
        // :85-90 -- BOTH conjuncts, and a rung that dropped either would agree
        // with upstream on every string but the one-byte "0".
        if z.slen == 0 || (z.slen == 1 && sget(b, SOFF) == b'0') {
            0
        } else {
            1
        }
    } else {
        0  // :108
    }
}

/// Fold `Z_STRLEN` bytes of `Z_STRVAL`. Same exec code as `unsafe.rs`.
#[inline(always)]
fn fold_bytes(acc: u64, b: &[u8], n: usize) -> (r: u64)
    requires
        b@.len() == REC,
        n <= STRMAX,
    ensures
        r == s_fold_bytes(acc, b@, 0, n as int),
{
    let mut a: u64 = acc;
    let mut i: usize = 0;
    while i < n
        invariant
            i <= n,
            n <= STRMAX,
            b@.len() == REC,
            s_fold_bytes(acc, b@, 0, n as int) == s_fold_bytes(a, b@, i as int, n as int),
        decreases n - i,
    {
        a = a.wrapping_mul(31).wrapping_add(sget(b, SOFF + i) as u64);
        i = i + 1;
    }
    a.wrapping_mul(31).wrapping_add(1)
}

/// What the VM goes on to read out of the zval `zend_std_read_dimension`
/// returns to it at `:395`. Same exec code as `unsafe.rs`.
#[inline(always)]
fn fold_zval(acc: u64, z: &Zval, b: &[u8]) -> (r: u64)
    requires
        b@.len() == REC,
        z.ty == s_ty(b@),
        z.lval == s_lval(b@),
        z.slen == s_slen(b@),
        z.slen <= STRMAX,
    ensures
        r == s_fold_zval(acc, b@),
{
    reveal(s_fold_zval);
    let a: u64 = acc.wrapping_mul(31).wrapping_add(z.ty as u64);
    if z.ty == IS_STRING {
        fold_bytes(a, b, z.slen)
    } else {
        a.wrapping_mul(31).wrapping_add(z.lval as u64)
    }
}

/// `zend_call_method` + `zend_call_function` -- zend_interfaces.c:30-96 and
/// zend_execute_API.c:537-874, narrowed. Same exec code as `unsafe.rs`.
///
/// ⛔⛔ **THE `ensures` BELOW IS THE DEFECT, STATED AS A CONTRACT.** The status
/// this function returns is `s_core(b@)` and the out-parameter it leaves is
/// `s_wrote(b@)`, and NOTHING relates them: a caller that has `!r` -- SUCCESS --
/// knows nothing at all about whether the output is there.
#[inline(always)]
fn call_method(
    b: &[u8],
    slot: &mut Zval,
    want_output: bool,
    wrote_out: &mut bool,
    n_rel: &mut u64,
) -> (r: bool)
    requires
        b@.len() == REC,
    ensures
        r == s_core(b@),
        *final(wrote_out) == (!s_core(b@) && want_output && s_wrote(b@)),
        s_relc(b@, want_output) ==> *final(n_rel) == (*old(n_rel)).wrapping_add(1),
        !s_relc(b@, want_output) ==> *final(n_rel) == *old(n_rel),
        *final(wrote_out) ==> final(slot).ty == s_ty(b@),
        *final(wrote_out) ==> final(slot).lval == s_lval(b@),
        *final(wrote_out) ==> final(slot).slen == s_slen(b@),
        *final(wrote_out) ==> final(slot).slen <= STRMAX,
        *final(wrote_out) ==> final(slot).refcount == 1,
{
    // zend_execute_API.c:595 -- the sentinel, unconditionally and first.
    let mut wrote: bool = false;
    let failed: bool = sget(b, 1) % 5 == 0;
    if !failed && sget(b, 2) % 3 != 0 {
        // the user method returned a value: ZVAL_* + the caller's own hold.
        slot.ty = ty_get((sget(b, 3) % 4) as usize);
        slot.refcount = 1;
        slot.is_ref = 0;
        slot.lval = sget(b, 4);
        slot.slen = (sget(b, 5) % ((STRMAX + 1) as u8)) as usize;
        wrote = true;
    }
    // :870-873 -- the exception is re-thrown and the status does not say so.
    if failed {
        // zend_interfaces.c:81-86 -- the STATUS *is* tested.
        *wrote_out = false;
        return true;
    }
    if !want_output {
        // zend_interfaces.c:88-93 -- the NO-OUTPUT contract disposes of the
        // value behind its OWN `if (retval)` NULL test, which is the very test
        // `zend_object_handlers.c:513` omits.
        if wrote {
            zval_ptr_dtor(slot, n_rel);
        }
        *wrote_out = false;
        return false;
    }
    *wrote_out = wrote;  // :94 `return *retval_ptr_ptr;`
    false
}

/// `zend_std_read_dimension` -- zend_object_handlers.c:378-400. Same exec code
/// as `unsafe.rs`.
#[inline(always)]
fn read_dimension(b: &[u8], slot: &mut Zval, acc: u64, n_rel: &mut u64, n_core: &mut u64) -> (r:
    u64)
    requires
        b@.len() == REC,
        s_shape(b@) == 0,
    ensures
        r == s_step(b@, acc),
        s_rel1(b@) ==> *final(n_rel) == (*old(n_rel)).wrapping_add(1),
        !s_rel1(b@) ==> *final(n_rel) == *old(n_rel),
        s_core(b@) ==> *final(n_core) == (*old(n_core)).wrapping_add(1),
        !s_core(b@) ==> *final(n_core) == *old(n_core),
{
    reveal(s_step);
    let mut wrote_out: bool = false;
    if call_method(b, slot, true, &mut wrote_out, n_rel) {
        // :384
        *n_core = n_core.wrapping_add(1);
        return acc.wrapping_mul(31).wrapping_add(TAG_CORE);
    }
    let retval: Option<&mut Zval> = if wrote_out { Some(slot) } else { None };
    if retval.is_none() {
        // :385-389. With EG(exception) set -- which is the state that put the
        // sentinel here -- the E_ERROR at :387 is NOT raised.
        return acc.wrapping_mul(31).wrapping_add(TAG_UNDEF);
    }
    let rv: &mut Zval = opt_get(retval);
    let a: u64 = fold_zval(acc, rv, b);  // :395 the zval reaches the VM
    rv.refcount = rv.refcount - 1;  // :393 Undo PZVAL_LOCK()
    a.wrapping_mul(31).wrapping_add(TAG_READ)
}

/// `zend_std_write_dimension` -- zend_object_handlers.c:403-417. Same exec code
/// as `unsafe.rs`.
#[inline(always)]
fn write_dimension(b: &[u8], slot: &mut Zval, acc: u64, n_rel: &mut u64, n_core: &mut u64) -> (r:
    u64)
    requires
        b@.len() == REC,
        s_shape(b@) == 1,
    ensures
        r == s_step(b@, acc),
        s_rel1(b@) ==> *final(n_rel) == (*old(n_rel)).wrapping_add(1),
        !s_rel1(b@) ==> *final(n_rel) == *old(n_rel),
        s_core(b@) ==> *final(n_core) == (*old(n_core)).wrapping_add(1),
        !s_core(b@) ==> *final(n_core) == *old(n_core),
{
    reveal(s_step);
    let mut wrote_out: bool = false;
    if call_method(b, slot, false, &mut wrote_out, n_rel) {
        // :413
        *n_core = n_core.wrapping_add(1);
        return acc.wrapping_mul(31).wrapping_add(TAG_CORE);
    }
    acc.wrapping_mul(31).wrapping_add(TAG_WRITE)
}

/// `zend_std_has_dimension` -- zend_object_handlers.c:420-434. Same exec code as
/// `unsafe.rs`.
///
/// ⛔⛔ **THE `retval.is_none()` ARM BELOW IS NOT UPSTREAM'S AND NOT
/// cf020f133487's.** See the module header and `../NOTES.md` section 5.
#[inline(always)]
fn has_dimension(b: &[u8], slot: &mut Zval, acc: u64, n_rel: &mut u64, n_core: &mut u64) -> (r: u64)
    requires
        b@.len() == REC,
        s_shape(b@) == 2,
    ensures
        r == s_step(b@, acc),
        s_rel1(b@) ==> *final(n_rel) == (*old(n_rel)).wrapping_add(1),
        !s_rel1(b@) ==> *final(n_rel) == *old(n_rel),
        s_core(b@) ==> *final(n_core) == (*old(n_core)).wrapping_add(1),
        !s_core(b@) ==> *final(n_core) == *old(n_core),
{
    reveal(s_step);
    let mut wrote_out: bool = false;
    if call_method(b, slot, true, &mut wrote_out, n_rel) {
        // :427
        *n_core = n_core.wrapping_add(1);
        return acc.wrapping_mul(31).wrapping_add(TAG_CORE);
    }
    let retval: Option<&mut Zval> = if wrote_out { Some(slot) } else { None };
    if retval.is_none() {
        return acc.wrapping_mul(31).wrapping_add(TAG_UNDEF);
    }
    let rv: &mut Zval = opt_get(retval);
    let res: u64 = is_true(rv, b);  // :428
    zval_ptr_dtor(rv, n_rel);  // :429
    acc.wrapping_mul(31).wrapping_add(TAG_EXISTS).wrapping_add(res)  // :430
}

/// `zend_std_unset_dimension` -- zend_object_handlers.c:506-517, WITH
/// cf020f133487. Same exec code as `unsafe.rs`.
#[inline(always)]
fn unset_dimension(b: &[u8], slot: &mut Zval, acc: u64, n_rel: &mut u64, n_core: &mut u64) -> (r:
    u64)
    requires
        b@.len() == REC,
        s_shape(b@) == 3,
    ensures
        r == s_step(b@, acc),
        s_rel1(b@) ==> *final(n_rel) == (*old(n_rel)).wrapping_add(1),
        !s_rel1(b@) ==> *final(n_rel) == *old(n_rel),
        s_core(b@) ==> *final(n_core) == (*old(n_core)).wrapping_add(1),
        !s_core(b@) ==> *final(n_core) == *old(n_core),
{
    reveal(s_step);
    let mut wrote_out: bool = false;
    if call_method(b, slot, false, &mut wrote_out, n_rel) {
        // :512, with NULL for `retval_ptr_ptr`
        *n_core = n_core.wrapping_add(1);
        return acc.wrapping_mul(31).wrapping_add(TAG_CORE);
    }
    acc.wrapping_mul(31).wrapping_add(TAG_UNSET)
}

// Same exec code as unsafe.rs. Contract: ../spec.md.
//
// One `ensures`, and it is the VALUE, not the safety property. What makes it
// worth having: it is what stops the proof being vacuous, it is what `model.py`
// re-derives independently, and it is what forces the invariants to describe the
// four handlers rather than merely bound an index. A kernel that returned 0
// unconditionally would satisfy every bounds obligation in this file.
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
    let mut n_rel: u64 = 0;
    let mut n_core: u64 = 0;
    let mut slot = Zval { ty: 0, is_ref: 0, refcount: 0, lval: 0, slen: 0 };
    let mut r: usize = 0;
    while r < nrec
        invariant
            r <= nrec,
            nrec * REC <= len,
            win@.len() == len,
            acc == s_run(win@, r as int),
            n_rel == s_nrel(win@, r as int),
            n_core == s_ncore(win@, r as int),
        decreases nrec - r,
    {
        // Ghost only: record `r` is entirely inside the window. Nonlinear, so
        // Z3 needs it spelled out. Erases at compile time -- R4 and R5 stay
        // byte-identical.
        assert((r + 1) * REC <= nrec * REC) by (nonlinear_arith)
            requires
                r + 1 <= nrec,
        ;
        let b: &[u8] = wsub(win, r * REC, REC);
        assert(b@ =~= s_rec(win@, r as int));
        let sh: u8 = sget(b, 0) % 4;
        if sh == 0 {
            acc = read_dimension(b, &mut slot, acc, &mut n_rel, &mut n_core);
        } else if sh == 1 {
            acc = write_dimension(b, &mut slot, acc, &mut n_rel, &mut n_core);
        } else if sh == 2 {
            acc = has_dimension(b, &mut slot, acc, &mut n_rel, &mut n_core);
        } else {
            acc = unset_dimension(b, &mut slot, acc, &mut n_rel, &mut n_core);
        }
        r = r + 1;
    }
    acc.wrapping_mul(31).wrapping_add(n_rel).wrapping_mul(31).wrapping_add(n_core)
}

// ---------------------------------------------------------------- driver ----
fn main() {
    let (n_iters, stride_w, bytes) = load_input();
    // SLB-DRIVER-BEGIN
    let n_blob: usize = bytes.len();
    let buf: &[u8] = bytes.as_slice();
    let mut acc: u64 = 0;
    if stride_w >= 16 && stride_w <= n_blob as u64 {
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
                16 <= stride <= n_blob,
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
