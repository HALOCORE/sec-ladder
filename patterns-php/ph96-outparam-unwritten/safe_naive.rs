//! ph96 rung R2 -- safe-naive.
//!
//! The mechanical port a working Rust programmer writes first: slice the window
//! with `&win[..]`, index every byte with `b[i]`, carry the out-parameter as an
//! `Option<&mut Zval>`, open it with `.unwrap()`. Zero `unsafe`.
//!
//! ⚠⚠ **READ THIS BEFORE COMPARING THIS RUNG TO R1h.** The four Rust rungs
//! implement `c/kernel_hardened.c` **plus one guard upstream never wrote**, and
//! the difference is a FINDING rather than a liberty:
//!
//!     R1     zend_object_handlers.c as shipped 5.0.0 -- CRASH-061. TWO
//!            unguarded releases of the `zend_execute_API.c:595` sentinel:
//!            `:512-513` (offsetunset) and `:427-429` (offsetexists).
//!     R1h    + cf020f133487 (Marcus Boerger, 2005-03-19, "- Fix #31185"),
//!            BACKPORTED: three lines, and they repair `:512-513` ONLY.
//!     R2-5   R1h, plus the `:385` guard at `:427`.
//!
//! ⭐⭐⭐ **THE EXTRA GUARD IS NOT A CHOICE THIS ROW MADE -- IT IS WHAT THE TYPE
//! FORCES.** `Option<&mut Zval>` cannot be released without being opened, and
//! the `None` arm has to go somewhere. Upstream's C can, and does, simply not
//! have an arm there. So the sentence *safe Rust cannot express the `:427`
//! limb* is this row's sharpest ladder result, and `CLAUDE.md` rule 6 makes it
//! a finding and never a problem. `controls/second_limb.py` drives that exact
//! state through all six rungs and records what each does; `../spec.md`'s
//! divergence ledger itemises the guard; `../NOTES.md` section 5 has the scope.
//!
//! ⭐ On the WHOLE benign domain the three coincide exactly, because the extra
//! guard is reachable only from the sentinel state and `inputs/gen.py` refuses a
//! measured corpus that carries one.
//!
//! ⭐⭐ **WHAT THIS ROW IS ABOUT, IN ONE LINE OF RUST.** C says *the callee wrote
//! nothing* with a NULL `zval *` and has no way to make the caller check; Rust
//! says it with `Option<&mut Zval>`, which the const assertion below measures at
//! **the same 8 bytes** and which cannot be released without being opened. The
//! safety is a TYPE, not a test, and the type costs nothing to carry.
//!
//! ⚠ **WHAT THE RUST RUNGS THEREFORE CANNOT SHOW, AND IT IS A FINDING RATHER
//! THAN A GAP** (`CLAUDE.md` rule 6): no rung here reproduces the defect,
//! because in C the bug is an OMISSION -- a test that is not written -- and in
//! Rust reproducing it would take a COMMISSION, an `unwrap` or an
//! `unwrap_unchecked` on an unguarded out-parameter. `controls/rust_bug.py`
//! builds both of those on purpose and records what they do. `../NOTES.md`
//! section 10.
//!
//! **Do not read this rung's number as an unwrap tax without the decomposition
//! in `../NOTES.md` section 9.** A ph96 call does four different things
//! depending on the shape byte, and only two of them read the value at all.

#[path = "../../common/driver.rs"]
mod driver;

// ------------------------------------------------------- shared arithmetic --
// Identical text in all four Rust rungs and re-derived independently in
// model.py. See ../spec.md for why each is what it is.

/// One call record: a consumer SHAPE, a call STATUS, a WROTE-OUTPUT bit and the
/// zval the user method would have returned.
const REC: usize = 16;
/// The largest `Z_STRLEN` a record can carry.
const STRMAX: usize = 10;
/// Where `Z_STRVAL` starts inside the record.
const SOFF: usize = 6;

// Z_TYPE_P -- upstream's own numbering, Zend/zend.h:302-309. Four of the eight
// are reachable here; ../spec.md `provenance.divergences` itemises the rest.
const IS_NULL: u8 = 0;
const IS_LONG: u8 = 1;
const IS_BOOL: u8 = 3;
const IS_STRING: u8 = 6;
const TYTAB: [u8; 4] = [IS_NULL, IS_LONG, IS_BOOL, IS_STRING];

const TAG_READ: u64 = 0x11;
const TAG_UNDEF: u64 = 0x12;
const TAG_WRITE: u64 = 0x13;
const TAG_EXISTS: u64 = 0x14;
const TAG_UNSET: u64 = 0x15;
const TAG_CORE: u64 = 0x16;

/// ⭐⭐⭐ **THE ROW'S LAYOUT CLAIM, AS A COMPILE-TIME ASSERTION RATHER THAN A
/// CLAIM.** `Option<&mut T>` is the null-pointer-optimised layout: the
/// discriminant lives in the reference's own null niche, so an optional
/// exclusive reference occupies exactly the bytes of the `zval *` C spends on
/// the same job. If this ever stopped holding, every Rust rung in this row would
/// fail to BUILD rather than quietly measure something else.
const _: () = assert!(
    core::mem::size_of::<Option<&mut Zval>>() == core::mem::size_of::<&mut Zval>()
);
const _: () = assert!(core::mem::size_of::<Option<&mut Zval>>() == 8);

/// `struct _zval_struct` -- Zend/zend.h:287-293, with `Z_STRVAL` kept as an
/// offset into the record rather than as a borrowed slice. `../spec.md`
/// itemises that; `c/kernel.c` writes `str.val = b + 6` and this is the same
/// six.
///
/// ⚠ **THE C RUNGS ASSERT THE FIELD OFFSETS AND THESE DO NOT**, because Rust
/// gives `#[repr(Rust)]` no offsets to assert and no rung here dereferences a
/// null. The layout claim this file makes is about the OPTIONAL above, which is
/// the one the ladder prices.
struct Zval {
    ty: u8,
    is_ref: u8,
    refcount: u32,
    lval: u8,
    slen: usize,
}

/// R2/R3 spelling: a bounds-checked slice index.
#[inline(always)]
fn sget(v: &[u8], i: usize) -> u8 {
    v[i]
}

/// R2/R3 spelling: a bounds-checked sub-slice.
#[inline(always)]
fn wsub(v: &[u8], o: usize, n: usize) -> &[u8] {
    &v[o..o + n]
}

/// R2/R3 spelling: a bounds-checked index into the type table.
#[inline(always)]
fn ty_get(k: usize) -> u8 {
    TYTAB[k]
}

/// R2/R3 spelling: the CHECKED open of the out-parameter.
///
/// ⭐⭐ It cannot panic, and the reason is a NULL TEST at each of its two call
/// sites: `zend_object_handlers.c:385` at the `read` shape, which upstream
/// wrote, and the same spelling at the `exists` shape, which upstream did not.
/// R4 and R5 write `unwrap_unchecked` here, and R5 PROVES exactly those tests.
#[inline(always)]
fn opt_get<'a>(t: Option<&'a mut Zval>) -> &'a mut Zval {
    t.unwrap()
}

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md. `#[inline(never)]` only in `isolated` builds, so the
// `whole` builds can inline it the way LTO'd C would.

/// `_zval_ptr_dtor` -- zend_execute_API.c:384-396. In C the FIRST STATEMENT is
/// the dereference; here the value is already open, which is the whole point.
///
/// `zval_dtor` + `safe_free_zval_ptr` are PROJECTED onto the release tally: the
/// row models no allocator (`../spec.md`, `uses_allocator: false`).
#[inline(always)]
fn zval_ptr_dtor(z: &mut Zval, n_rel: &mut u64) {
    z.refcount = z.refcount - 1; // :389
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

/// `i_zend_is_true` -- Zend/zend_execute.h:68-112, narrowed to four type tags.
///
/// R2 spelling: one bounds-checked index for the string's first byte.
#[inline(always)]
fn is_true(z: &Zval, b: &[u8]) -> u64 {
    if z.ty == IS_NULL {
        0 // :74
    } else if z.ty == IS_LONG || z.ty == IS_BOOL {
        if z.lval != 0 {
            1 // :79
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
        0 // :108
    }
}

/// Fold `Z_STRLEN` bytes of `Z_STRVAL`. The terminator is folded too, so that a
/// rung stopping at the wrong place disagrees.
///
/// R2 spelling: one bounds-checked index per byte.
#[inline(always)]
fn fold_bytes(acc: u64, b: &[u8], n: usize) -> u64 {
    let mut a: u64 = acc;
    let mut i: usize = 0;
    while i < n {
        a = a.wrapping_mul(31).wrapping_add(sget(b, SOFF + i) as u64);
        i = i + 1;
    }
    a.wrapping_mul(31).wrapping_add(1)
}

/// What the VM goes on to read out of the zval `zend_std_read_dimension`
/// returns to it at `:395`. A `u64` kernel cannot return a zval, so the row
/// folds the type tag and, for a string, its whole `Z_STRLEN`.
#[inline(always)]
fn fold_zval(acc: u64, z: &Zval, b: &[u8]) -> u64 {
    let a: u64 = acc.wrapping_mul(31).wrapping_add(z.ty as u64);
    if z.ty == IS_STRING {
        fold_bytes(a, b, z.slen)
    } else {
        a.wrapping_mul(31).wrapping_add(z.lval as u64)
    }
}

/// `zend_call_method` + `zend_call_function` -- zend_interfaces.c:30-96 and
/// zend_execute_API.c:537-874, narrowed.
///
/// ⛔⛔ **THE TWO BITS ARE INDEPENDENT AND THAT IS THE ROW.** `b[1]` decides
/// whether `zend_call_function` returns FAILURE (`:667`, `:674`, `:679`) and
/// `b[2]` decides whether the user method left an output. `*fci->retval_ptr_ptr
/// = NULL` at `:595` runs BEFORE either, so the out-parameter is the sentinel on
/// both arms -- and `:873` returns SUCCESS whatever the method did.
///
/// Returns `true` for the `E_CORE_ERROR` arm at `zend_interfaces.c:86`, which
/// terminates the request upstream and is PROJECTED here onto *this call
/// contributes a CORE tag and the consumer does not run*.
#[inline(always)]
fn call_method(b: &[u8], slot: &mut Zval, want_output: bool,
               wrote_out: &mut bool, n_rel: &mut u64) -> bool {
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
    *wrote_out = wrote; // :94 `return *retval_ptr_ptr;`
    false
}

/// `zend_std_read_dimension` -- zend_object_handlers.c:378-400. SHAPE 0, the
/// OUTPUT contract, GUARDED at `:385`.
#[inline(always)]
fn read_dimension(b: &[u8], slot: &mut Zval, acc: u64, n_rel: &mut u64,
                  n_core: &mut u64) -> u64 {
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
    let a: u64 = fold_zval(acc, rv, b); // :395 the zval reaches the VM
    rv.refcount = rv.refcount - 1; // :393 Undo PZVAL_LOCK()
    a.wrapping_mul(31).wrapping_add(TAG_READ)
}

/// `zend_std_write_dimension` -- zend_object_handlers.c:403-417. SHAPE 1, the
/// NO-OUTPUT contract: `:413` passes NULL, 99 lines before `:512` passes
/// `&retval`.
#[inline(always)]
fn write_dimension(b: &[u8], slot: &mut Zval, acc: u64, n_rel: &mut u64,
                   n_core: &mut u64) -> u64 {
    let mut wrote_out: bool = false;
    if call_method(b, slot, false, &mut wrote_out, n_rel) {
        // :413
        *n_core = n_core.wrapping_add(1);
        return acc.wrapping_mul(31).wrapping_add(TAG_CORE);
    }
    acc.wrapping_mul(31).wrapping_add(TAG_WRITE)
}

/// `zend_std_has_dimension` -- zend_object_handlers.c:420-434. SHAPE 2, the
/// OUTPUT contract, UNGUARDED UPSTREAM.
///
/// ⛔⛔ **THE `retval.is_none()` ARM BELOW IS NOT UPSTREAM'S AND NOT
/// cf020f133487's.** Upstream goes straight from `:427` to `:428
/// i_zend_is_true(retval)`, which reads `op->type` at offset 0x14. See the
/// module header: the arm exists because `Option` cannot be opened without one,
/// and that is the finding. `controls/second_limb.py` measures both sides.
#[inline(always)]
fn has_dimension(b: &[u8], slot: &mut Zval, acc: u64, n_rel: &mut u64,
                 n_core: &mut u64) -> u64 {
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
    let res: u64 = is_true(rv, b); // :428
    zval_ptr_dtor(rv, n_rel); // :429
    acc.wrapping_mul(31).wrapping_add(TAG_EXISTS).wrapping_add(res) // :430
}

/// `zend_std_unset_dimension` -- zend_object_handlers.c:506-517, WITH
/// cf020f133487. SHAPE 3, the row's own site.
///
/// ⭐ After the fix this function and `write_dimension` differ in one constant,
/// which is the fix's whole content: `:512` was changed into `:413`.
#[inline(always)]
fn unset_dimension(b: &[u8], slot: &mut Zval, acc: u64, n_rel: &mut u64,
                   n_core: &mut u64) -> u64 {
    let mut wrote_out: bool = false;
    if call_method(b, slot, false, &mut wrote_out, n_rel) {
        // :512, with NULL for `retval_ptr_ptr`
        *n_core = n_core.wrapping_add(1);
        return acc.wrapping_mul(31).wrapping_add(TAG_CORE);
    }
    acc.wrapping_mul(31).wrapping_add(TAG_UNSET)
}

#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    let win: &[u8] = &buf[off..off + len];
    let nrec: usize = len / REC;
    let mut acc: u64 = 0;
    let mut n_rel: u64 = 0;
    let mut n_core: u64 = 0;
    let mut slot = Zval { ty: 0, is_ref: 0, refcount: 0, lval: 0, slen: 0 };

    let mut r: usize = 0;
    while r < nrec {
        let b: &[u8] = wsub(win, r * REC, REC);
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
    let path = driver::arg_path();
    let inp = driver::load(&path);
    let (stride_w, bytes) = driver::head1_u64_bytes(&inp);
    let n_iters: u64 = inp.n_iters;
    // SLB-DRIVER-BEGIN
    let n_blob: usize = bytes.len();
    let buf: &[u8] = bytes.as_slice();
    let mut acc: u64 = 0;
    if stride_w >= 16 && stride_w <= n_blob as u64 {
        let stride: usize = stride_w as usize;
        let nwin: u64 = (n_blob / stride) as u64;
        let mut it: u64 = 0;
        while it < n_iters {
            let k: usize = ((acc as u128 * nwin as u128) >> 64) as usize;
            let r: u64 = kernel(buf, k * stride, stride);
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    driver::emit(acc);
}
