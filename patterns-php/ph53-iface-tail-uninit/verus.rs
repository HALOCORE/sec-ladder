//! ph53 rung R5 -- unsafe + Verus.
//!
//! Same exec code as `unsafe.rs`, plus the proof that licenses it.
//!
//!     requires  off + len <= buf@.len(),  76 <= len
//!     ensures   r == iface_fold(buf@, off as int, len as int)
//!
//! `iface_fold` is the class-declaration interface array as a pure function of
//! the window's bytes, spelled as four recursive spec functions -- `scan_d`,
//! `scan_c`, `run_ops` and `iface_win` -- and `model.py` re-derives the same
//! `u64` from a different decomposition.
//!
//! ============================================================================
//! ⭐⭐ WHAT THE PROOF RESTS ON, AND THE THREE THINGS IT SAYS ABOUT THIS ROW
//! ============================================================================
//! **1. `mem_contents()` IS THE GHOST STATE FOR INITIALISEDNESS, so there is
//! no hand-rolled `Seq<bool>` for it.** `vstd/std_specs/maybe_uninit.rs` ships
//! `assume_specification` for `MaybeUninit::{new, uninit, assume_init,
//! assume_init_ref, assume_init_mut}`, with `uninit()` ensuring
//! `MemContents::Uninit` and every `assume_init*` carrying
//! `requires m.mem_contents().is_init()`. The obligation the row is about is
//! literally that `requires`, and **in ordinary exec code `assume_init`
//! therefore costs NO trusted item** -- verified at 6/0 in
//! `.temp/php41/probe_wrap.rs`. ⛔ **THIS FILE CANNOT USE THAT, and the reason
//! is a collision between two sound gate rules**: `_scan_unsafe_sites` requires
//! every `unsafe` token to sit inside an `external_body` body, and 5c-twin
//! requires every trusted item to have a VERIFIED twin -- which for a
//! `MaybeUninit` read would itself need `unsafe`, because there is no safe exec
//! route from `MaybeUninit<T>` to `T`. So `slot_read_unchecked` folds
//! `get_unchecked` and `assume_init` into one trusted item that re-asserts by
//! hand the precondition vstd already provides, and its twin is justified away.
//! ../NOTES.md 11 reports it. `get_unchecked` itself the pinned vstd does not
//! mention at all -- 0 files under `~/tools/verus/vstd/`.
//!
//! **2. THE VALUE POSTCONDITION DOES NEED ONE GHOST `Seq`, AND IT IS NOT A
//! `Seq<bool>`.** `run_ops` has to say what the kernel RETURNS, and a spec
//! function cannot construct a `MaybeUninit` (`mem_contents` is `uninterp`),
//! so the spec-level slot array is a `Seq<Option<u32>>` and `abst()` is the
//! abstraction function from the exec state to it. ⚠ `TASK_PHP_040_REPORT.md`
//! §5.6 predicted *"no hand-rolled ghost state"*; that is **right about the
//! memory obligation and wrong about the value postcondition**, and
//! `../NOTES.md` §11 reports it as a partial refutation rather than as a
//! confirmation.
//!
//! **3. ⚠⚠⚠ AND THE OBLIGATION IS NOT DISCHARGEABLE OVER A FAITHFUL R4.**
//! Whether slot `i` was written is a property of the **op stream**, i.e. of
//! attacker data; ../spec.md's driver loop is pinned canonical and calls
//! `kernel(buf, k * stride, stride)` with no test, so there is no call site at
//! which coverage could be established and no `requires` that could carry it.
//! ▶ **A rung that reproduces the defect cannot be verified and a rung that
//! verifies does not reproduce it**, so R4/R5 carry a one-byte-per-slot
//! runtime witness and the faithful witness-free version is a CONTROL:
//! `controls/r4_nowitness.rs`, measured, Miri'd, and put through Verus with
//! its error text. `../NOTES.md` §11.
//!
//! ⚠ The FOURTH obligation -- `pool_get_unchecked`'s `p < MAXP` -- is the
//! **price of the representation**, not part of the C's. The C stores a
//! `zend_class_entry *` and needs only that the pointer designate a class;
//! safe Rust cannot store an address in memory it owns, so all four Rust rungs
//! store an INDEX (ph45's precedent) and an index needs a RANGE as well as an
//! initialisedness. So the invariant is a conjunction where the C's obligation
//! is a single fact, and `controls/negatives.py` fires on each conjunct
//! separately.

use vstd::prelude::*;
use vstd::raw_ptr::MemContents;
use core::mem::MaybeUninit;

// Plain-Rust I/O helpers. Outside `verus!`, so Verus treats the whole module as
// external (external-by-default). Reached only through `load_input`/`emit`.
#[path = "../../common/driver.rs"]
mod driver;

verus! {

// `group_slice_axioms` gives `slice@.len() == spec_slice_len(slice)`, hence
// `slice@.len() <= usize::MAX`, without which `off + len` cannot be shown not
// to overflow. `lemma_u128_shr_is_div` turns `x >> 64` into `x / 2^64` for the
// driver's multiply-shift barrier bound; the mul group is what the
// window-offset bound `k * stride + stride <= n_blob` needs.
broadcast use {
    vstd::slice::group_slice_axioms,
    vstd::bits::lemma_u128_shr_is_div,
    vstd::arithmetic::mul::lemma_mul_inequality,
};

/// `c/kernel.h` `PH53_MAXD` -- the largest `ce->num_interfaces` this row
/// admits.
pub const MAXD: usize = 16;

/// `c/kernel.h` `PH53_MAXP` -- interfaces in scope.
pub const MAXP: usize = 8;

pub const HDR: usize = 12;

pub const POOL_OFF: usize = HDR;

pub const OPS_OFF: usize = POOL_OFF + 8 * MAXP;   // 76

pub const OP_BYTES: usize = 9;

// ------------------------------------------------------------------ spec ----

/// A little-endian u32 at `o`, exactly as every rung decodes it.
pub open spec fn rd32s(w: Seq<u8>, o: int) -> u32 {
    (w[o] as u32) | ((w[o + 1] as u32) << 8) | ((w[o + 2] as u32) << 16) | ((w[o + 3] as u32)
        << 24)
}

/// A little-endian u64 at `o`.
pub open spec fn rd64s(w: Seq<u8>, o: int) -> u64 {
    (rd32s(w, o) as u64) | ((rd32s(w, o + 4) as u64) << 32)
}

/// Ops the window has room for. Derived from the LENGTH and never trusted out
/// of the blob.
pub open spec fn cap_of(ln: int) -> int {
    (ln - OPS_OFF as int) / OP_BYTES as int
}

/// `ce->num_interfaces` after phase 1 -- what `zend_compile.c:2591` counted.
pub open spec fn nd_of(w: Seq<u8>) -> int {
    (rd32s(w, 0) as int) % (MAXD as int + 1)
}

/// Interfaces in scope.
pub open spec fn np_of(w: Seq<u8>) -> int {
    1 + (rd32s(w, 4) as int) % (MAXP as int)
}

/// Ops in the stream.
pub open spec fn no_of(w: Seq<u8>, ln: int) -> int {
    (rd32s(w, 8) as int) % (cap_of(ln) + 1)
}

/// The interface pool -- all `MAXP` entries, read from the window.
///
/// ⚠ Every entry is read on every rung, `n_pool` or not, so that the per-call
/// pool work is a CONSTANT and the spec is exact. The alternative -- reading
/// only `0..n_pool` -- leaves the C's `ph53_iface pool[8]` partly
/// uninitialised, which is a second uninitialised read this row is not about.
pub open spec fn pool_of(w: Seq<u8>) -> Seq<u64> {
    Seq::new(MAXP as nat, |j: int| rd64s(w, POOL_OFF as int + 8 * j))
}

/// `php_shim_tally()` after one kernel call -- `emalloc_shim.h:642-648`.
///
/// The kernel calls `php_shim_reset()` first, so every counter starts at zero;
/// then `php_shim_erealloc(NULL, 8*n)` takes `_emalloc`'s malloc arm (the
/// cache was just wiped) and the teardown `php_shim_efree`s it. So
/// `n_alloc == n_free == 1`, `n_cache_hit == 0` and
/// `bytes_mallocked == REAL_SIZE(8 * nd)`, which is `8 * nd` because `8 * nd`
/// is already 8-aligned.
///
/// ⭐ **Both arms of `zend_compile.c:2570` are visible here**: the dead arm
/// allocates nothing, so the tally is 0.
pub open spec fn tally_of(nd: int) -> u64 {
    if nd <= 0 {
        0u64
    } else {
        (1000003u64 ^ 1000033u64 ^ 0u64) ^ ((8 * nd) as u64).wrapping_mul(1000039)
    }
}

/// The abstraction function from the EXEC slot state to the spec's.
///
/// ⚠⚠ **THIS IS THE ONE GHOST `Seq` THE ROW NEEDS, AND IT EXISTS FOR THE VALUE
/// POSTCONDITION AND NOT FOR MEMORY SAFETY.** `mem_contents()` already carries
/// initialisedness; what it cannot do is let a spec function BUILD a slot
/// array, because `mem_contents` is `uninterp` and there is no spec-mode
/// constructor for `MaybeUninit`. So `run_ops` works over `Seq<Option<u32>>`
/// and this maps `(slots, wrote)` onto it.
pub open spec fn abst(slots: Seq<MaybeUninit<u32>>, wrote: Seq<bool>, n: int) -> Seq<Option<u32>> {
    Seq::new(
        n as nat,
        |i: int|
            if wrote[i] {
                Some(slots[i].mem_contents().value())
            } else {
                None::<u32>
            },
    )
}

/// `instanceof_function_ex`'s interface loop -- `Zend/zend_operators.c`
/// `:1530-1538`, narrowed. Returns `(hit, matched_id, examined)`.
///
/// ⚠ `None` -- a slot no `FILL` wrote -- is SKIPPED. The C dereferences it,
/// which is the defect; this spec describes the rung that does not, which is
/// what R2, R3, R4 and R5 all implement. `.memory-php/02-ladder.md`: *"the
/// hardened C rung carries the historical fix and the Rust rungs carry
/// whatever is actually memory-safe."*
pub open spec fn scan_d(slots: Seq<Option<u32>>, pool: Seq<u64>, i: int, n: int, t: u64) -> (u64,
    u64,
    u64,
)
    decreases n - i,
{
    if i >= n {
        (0u64, 0u64, n as u64)
    } else {
        match slots[i] {
            Some(p) => if pool[p as int] == t {
                (1u64, pool[p as int], (i + 1) as u64)
            } else {
                scan_d(slots, pool, i + 1, n, t)
            },
            None => scan_d(slots, pool, i + 1, n, t),
        }
    }
}

/// `zend_do_inherit_interfaces`'s dedup scan -- `Zend/zend_compile.c:1951`.
/// The index it stops at, or `n`.
///
/// ⚠⚠ **IT READS THE SLOT AND DOES NOT REACH THE POOL.** That is why
/// `d09cdd9f71f3` lands here at a different severity from `scan_d`: with the
/// array zeroed, this comparison is DEFINED AND CORRECT and `scan_d`'s
/// dereference is a NULL dereference. One hunk, two severities.
pub open spec fn scan_c(slots: Seq<Option<u32>>, i: int, n: int, t: u32) -> u64
    decreases n - i,
{
    if i >= n {
        n as u64
    } else {
        match slots[i] {
            Some(p) => if p == t {
                i as u64
            } else {
                scan_c(slots, i + 1, n, t)
            },
            None => scan_c(slots, i + 1, n, t),
        }
    }
}

/// The op stream, one op per unfolding. THE BLOB IS THE OPCODE STREAM.
pub open spec fn run_ops(
    w: Seq<u8>,
    nd: int,
    np: int,
    pool: Seq<u64>,
    k: int,
    no: int,
    slots: Seq<Option<u32>>,
    acc: u64,
) -> (Seq<Option<u32>>, u64)
    decreases no - k,
{
    if k >= no {
        (slots, acc)
    } else {
        let p = OPS_OFF as int + OP_BYTES as int * k;
        let op = (w[p] as int) % 3;
        let a = rd32s(w, p + 1);
        let b = rd32s(w, p + 5);
        if op == 0 {
            // ZEND_ADD_INTERFACE's runtime half.
            let d = if nd > 0 {
                (a as int) % nd
            } else {
                0int
            };
            let pi = (b as int) % np;
            let s2 = if nd > 0 {
                slots.update(d, Some(pi as u32))
            } else {
                slots
            };
            run_ops(w, nd, np, pool, k + 1, no, s2, acc.wrapping_mul(31).wrapping_add(d as u64))
        } else if op == 1 {
            let t = (a as int) % np;
            let r = scan_d(slots, pool, 0, nd, pool[t]);
            let a1 = acc.wrapping_mul(31).wrapping_add(r.0);
            let a2 = a1.wrapping_mul(31).wrapping_add(r.1);
            let a3 = a2.wrapping_mul(31).wrapping_add(r.2);
            run_ops(w, nd, np, pool, k + 1, no, slots, a3)
        } else {
            let t = (a as int) % np;
            let i = scan_c(slots, 0, nd, t as u32);
            let a1 = acc.wrapping_mul(31).wrapping_add(
                if i != nd as u64 {
                    1u64
                } else {
                    0u64
                },
            );
            let a2 = a1.wrapping_mul(31).wrapping_add(i);
            run_ops(w, nd, np, pool, k + 1, no, slots, a2)
        }
    }
}

/// One window's answer, as a function of its bytes alone.
pub open spec fn iface_win(w: Seq<u8>, ln: int) -> u64 {
    let nd = nd_of(w);
    let r = run_ops(
        w,
        nd,
        np_of(w),
        pool_of(w),
        0,
        no_of(w, ln),
        Seq::new(nd as nat, |i: int| None::<u32>),
        0u64,
    );
    r.1 ^ tally_of(nd)
}

/// What the kernel must return. `model.py::iface_fold` re-derives it.
pub open spec fn iface_fold(buf: Seq<u8>, off: int, ln: int) -> u64 {
    iface_win(buf.subrange(off, off + ln), ln)
}

// ------------------------------------------------------- TRUSTED, item 1/6 --
// `v[i]` with no bounds check. The `requires` is what makes it sound and the
// `ensures` is what makes it useful; both are trusted, and `../NOTES.md` §11
// argues each one.
#[verifier::external_body]
fn win_get_unchecked(v: &[u8], i: usize) -> (r: u8)
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
fn slb_twin_win_get_unchecked(v: &[u8], i: usize) -> (r: u8)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    v[i]
}

// ------------------------------------------------------- TRUSTED, item 2/6 --
// ⚠⚠⚠ THIS ITEM IS A COLLISION BETWEEN TWO SOUND GATE RULES, AND IT IS THE
// ROW'S SHARPEST INFRASTRUCTURE FINDING.  The obligation `MaybeUninit` needs is
// ALREADY SPECIFIED in the pinned vstd -- `std_specs/maybe_uninit.rs`'s
// `assume_specification[ MaybeUninit::<T>::assume_init ]` carries
// `requires m.mem_contents().is_init()` -- so in ordinary exec code
// `unsafe { m.assume_init() }` needs NO trusted item at all, and
// `.temp/php41/probe_wrap.rs` verifies exactly that shape at 6/0.
//
// ⛔ BUT `harness/check.py::_scan_unsafe_sites` requires EVERY `unsafe` token
// in a pinned Verus source to sit inside the body of an `external_body` item,
// with no justification hatch -- and `assume_init` is `unsafe`.  And 5c-twin
// requires every trusted item to have a VERIFIED twin, which for this
// operation would itself need an `unsafe` token, because there is NO safe exec
// route from `MaybeUninit<T>` to `T`.
//
// ▶ SO THE TWO RULES ARE JOINTLY UNSATISFIABLE FOR A `MaybeUninit` READ, and
// the shape that satisfies them both is this one: fold `get_unchecked` and
// `assume_init` into ONE trusted item whose `requires` RE-ASSERTS BY HAND the
// precondition vstd already provides, and justify the twin's absence.
// `verus.twin_justifications` carries the argument and ../NOTES.md 11 reports
// the collision rather than hiding it in a wrapper.  ⭐ The TCB count is
// unchanged by the fold (one item either way); what is lost is that the
// `is_init` precondition is now MINE rather than vstd's.
#[verifier::external_body]
fn slot_read_unchecked(v: &Vec<MaybeUninit<u32>>, i: usize) -> (r: u32)
    requires
        i < v@.len(),
        v@[i as int].mem_contents().is_init(),
    ensures
        r == v@[i as int].mem_contents().value(),
{
    unsafe { (*v.get_unchecked(i)).assume_init() }
}

// ------------------------------------------------------- TRUSTED, item 3/6 --
// ⚠ `x: MaybeUninit<u32>` is a PURE VALUE and needs no precondition: every
// inhabitant is a legal store into a slot of that type, initialised or not.
// The `ensures` names the WHOLE post-state -- `old(v)@.update(i, x)` -- so a
// body that also clobbered `v[i + 1]` could not satisfy it. That completeness
// is the thing a write wrapper's contract can get wrong, and it is why Miri is
// required on this row (../spec.md `miri`).
#[verifier::external_body]
fn slot_set_unchecked(v: &mut Vec<MaybeUninit<u32>>, i: usize, x: MaybeUninit<u32>)
    requires
        i < old(v)@.len(),
    ensures
        final(v)@ == old(v)@.update(i as int, x),
{
    unsafe { *v.get_unchecked_mut(i) = x };
}

#[cfg(slb_twin)]
fn slb_twin_slot_set_unchecked(v: &mut Vec<MaybeUninit<u32>>, i: usize, x: MaybeUninit<u32>)
    requires
        i < old(v)@.len(),
    ensures
        final(v)@ == old(v)@.update(i as int, x),
{
    v[i] = x;
}

// ------------------------------------------------------- TRUSTED, item 4/6 --
// ⚠ `a: &[u64; MAXP]` is a SHARED REFERENCE TO A FIXED-SIZE ARRAY and its
// length is in its TYPE, so there is nothing about it left for a `requires` to
// say beyond the index: `a@.len() == MAXP` holds for every `a` this signature
// admits, by `vstd::array::array_len_matches_n`.
#[verifier::external_body]
fn pool_get_unchecked(a: &[u64; MAXP], i: usize) -> (r: u64)
    requires
        i < MAXP,
    ensures
        r == a@[i as int],
{
    unsafe { *a.get_unchecked(i) }
}

#[cfg(slb_twin)]
fn slb_twin_pool_get_unchecked(a: &[u64; MAXP], i: usize) -> (r: u64)
    requires
        i < MAXP,
    ensures
        r == a@[i as int],
{
    a[i]
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

/// `common-php/emalloc_shim.h:642-648`, reproduced ARITHMETICALLY (§B, §B1.2).
#[inline(always)]
fn tally(n_decl: usize) -> (r: u64)
    requires
        n_decl <= MAXD,
    ensures
        r == tally_of(n_decl as int),
{
    if n_decl == 0 {
        0
    } else {
        let real_size: u64 = 8 * (n_decl as u64);
        (1000003u64 ^ 1000033u64 ^ 0u64) ^ real_size.wrapping_mul(1000039)
    }
}

#[inline(always)]
fn rd32(w: &[u8], o: usize) -> (r: u32)
    requires
        o + 4 <= w@.len(),
    ensures
        r == rd32s(w@, o as int),
{
    // Ghost only: `spec_slice_len` is what tells the solver a slice length
    // fits in a `usize`, which is what keeps `o + 3` from overflowing.
    assert(w@.len() == vstd::slice::spec_slice_len(w));
    (win_get_unchecked(w, o) as u32) | ((win_get_unchecked(w, o + 1) as u32) << 8)
        | ((win_get_unchecked(w, o + 2) as u32) << 16) | ((win_get_unchecked(w, o + 3) as u32)
        << 24)
}

#[inline(always)]
fn rd64(w: &[u8], o: usize) -> (r: u64)
    requires
        o + 8 <= w@.len(),
    ensures
        r == rd64s(w@, o as int),
{
    assert(w@.len() == vstd::slice::spec_slice_len(w));
    (rd32(w, o) as u64) | ((rd32(w, o + 4) as u64) << 32)
}

/// `instanceof_function_ex`'s interface loop -- `Zend/zend_operators.c`
/// `:1530-1538`, narrowed. **THE FAULTING CONSUMER.** Same exec code as
/// `unsafe.rs`.
#[inline(always)]
fn instanceof_ex(
    slots: &Vec<MaybeUninit<u32>>,
    wrote: &[bool; MAXD],
    pool: &[u64; MAXP],
    target_id: u64,
) -> (r: (u64, u64, u64))
    requires
        slots@.len() <= MAXD,
        forall|j: int|
            0 <= j < slots@.len() ==> (#[trigger] wrote@[j] ==> slots@[j].mem_contents().is_init()
                && slots@[j].mem_contents().value() < MAXP),
    ensures
        r == scan_d(
            abst(slots@, wrote@, slots@.len() as int),
            pool@,
            0,
            slots@.len() as int,
            target_id,
        ),
{
    let n: usize = slots.len();
    let ghost a = abst(slots@, wrote@, slots@.len() as int);
    let ghost target = scan_d(a, pool@, 0, slots@.len() as int, target_id);
    let mut examined: u64 = 0;
    let mut i: usize = 0;
    // ⚠⚠ `target` IS PINNED BY AN INVARIANT AND NOT MERELY BY ITS `let ghost`
    // BINDING, and the reason is measured rather than stylistic: a `while`
    // body sees the invariants and the loop condition and NOTHING from before
    // the loop, and this loop RETURNS FROM INSIDE ITS BODY on a match. With
    // the binding alone, both early exits fail their postcondition while every
    // assert inside them passes -- which is a confusing way to be told the
    // binding is out of scope.
    while i < n
        invariant
            i <= n,
            n == slots@.len(),
            n <= MAXD,
            wrote@.len() == MAXD,
            examined == i as u64,
            a == abst(slots@, wrote@, slots@.len() as int),
            target == scan_d(a, pool@, 0, slots@.len() as int, target_id),
            forall|j: int|
                0 <= j < n ==> (#[trigger] wrote@[j] ==> slots@[j].mem_contents().is_init()
                    && slots@[j].mem_contents().value() < MAXP),
            scan_d(a, pool@, i as int, n as int, target_id) == target,
        decreases n - i,
    {
        examined = (i + 1) as u64;
        // ⚠ `wrote` is indexed SAFELY and deliberately: it is this rung's own
        // safety mechanism, and reaching it with `get_unchecked` would make
        // the witness rest on the thing it exists to establish.
        if wrote[i] {
            let p: u32 = slot_read_unchecked(slots, i);
            let id: u64 = pool_get_unchecked(pool, p as usize);
            assert(a[i as int] == Some(p));
            if id == target_id {
                assert(scan_d(a, pool@, i as int, n as int, target_id) == (1u64, id, (i + 1)
                    as u64));
                return (1, id, examined);
            }
        } else {
            assert(a[i as int] is None);
        }
        i = i + 1;
    }
    assert(scan_d(a, pool@, n as int, n as int, target_id) == (0u64, 0u64, n as u64));
    (0, 0, examined)
}

/// `zend_do_inherit_interfaces`'s dedup scan -- `Zend/zend_compile.c:1951`,
/// narrowed. **THE COMPARE-ONLY CONSUMER**: it reads the slot and does not
/// reach the pool at all.
#[inline(always)]
fn inherit_scan(slots: &Vec<MaybeUninit<u32>>, wrote: &[bool; MAXD], target: u32) -> (r: usize)
    requires
        slots@.len() <= MAXD,
        forall|j: int|
            0 <= j < slots@.len() ==> (#[trigger] wrote@[j] ==> slots@[j].mem_contents().is_init()
                && slots@[j].mem_contents().value() < MAXP),
    ensures
        r == scan_c(abst(slots@, wrote@, slots@.len() as int), 0, slots@.len() as int, target),
{
    let n: usize = slots.len();
    let ghost a = abst(slots@, wrote@, slots@.len() as int);
    let ghost target_i = scan_c(a, 0, slots@.len() as int, target);
    let mut i: usize = 0;
    while i < n
        invariant
            i <= n,
            n == slots@.len(),
            n <= MAXD,
            wrote@.len() == MAXD,
            a == abst(slots@, wrote@, slots@.len() as int),
            target_i == scan_c(a, 0, slots@.len() as int, target),
            forall|j: int|
                0 <= j < n ==> (#[trigger] wrote@[j] ==> slots@[j].mem_contents().is_init()
                    && slots@[j].mem_contents().value() < MAXP),
            scan_c(a, i as int, n as int, target) == target_i,
        decreases n - i,
    {
        if wrote[i] {
            let p: u32 = slot_read_unchecked(slots, i);
            assert(a[i as int] == Some(p));
            if p == target {
                assert(scan_c(a, i as int, n as int, target) == i as u64);
                return i;
            }
        } else {
            assert(a[i as int] is None);
        }
        i = i + 1;
    }
    assert(scan_c(a, n as int, n as int, target) == n as u64);
    n
}

// Same exec code as unsafe.rs. Contract: ../spec.md.
//
// One `ensures`, and it is the VALUE, not the safety property. What makes it
// worth having: it is what stops the proof being vacuous, it is what
// `model.py` re-derives independently, and it is what forces the invariant to
// describe the op stream rather than merely bound an index. A kernel that
// returned 0 unconditionally would satisfy every bounds obligation in this
// file. `controls/negatives.py` mutates it and every mutant must FAIL.
#[verifier::rlimit(60)]
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> (r: u64)
    requires
        off + len <= buf@.len(),
        76 <= len,
    ensures
        r == iface_fold(buf@, off as int, len as int),
{
    // Ghost only: mentioning `spec_slice_len` fires vstd's `axiom_spec_len`,
    // which is what tells the SMT solver a slice length fits in a `usize`.
    assert(buf@.len() == vstd::slice::spec_slice_len(buf));
    let win: &[u8] = &buf[off..off + len];
    assert(win@.len() == vstd::slice::spec_slice_len(win));
    assert(win@ =~= buf@.subrange(off as int, off + len));

    let cap: usize = (len - OPS_OFF) / OP_BYTES;
    let n_decl: usize = (rd32(win, 0) as usize) % (MAXD + 1);
    let n_pool: usize = 1 + (rd32(win, 4) as usize) % MAXP;
    let n_ops: usize = (rd32(win, 8) as usize) % (cap + 1);
    assert(cap as int == cap_of(len as int));
    assert(n_decl as int == nd_of(win@));
    assert(n_pool as int == np_of(win@));
    assert(n_ops as int == no_of(win@, len as int));
    // Every op record is inside the window: `cap` is derived from `len` by the
    // same division, so `OPS_OFF + 9*cap <= len`. Two steps, because the
    // product is nonlinear and Z3 needs the division identity named.
    proof {
        vstd::arithmetic::div_mod::lemma_fundamental_div_mod(
            (len - OPS_OFF) as int,
            OP_BYTES as int,
        );
        assert(OP_BYTES as int * (cap as int) <= (len - OPS_OFF) as int);
    }
    assert(OPS_OFF as int + OP_BYTES as int * (cap as int) <= len as int);

    let mut pool: [u64; MAXP] = [0u64; MAXP];
    let mut k: usize = 0;
    while k < MAXP
        invariant
            k <= MAXP,
            pool@.len() == MAXP,
            win@.len() == len,
            76 <= len,
            forall|j: int| 0 <= j < k ==> #[trigger] pool@[j] == pool_of(win@)[j],
        decreases MAXP - k,
    {
        pool[k] = rd64(win, POOL_OFF + 8 * k);
        k = k + 1;
    }
    assert(pool@ =~= pool_of(win@));

    // zend_compile.c:3747-3748, then phase 1's :2591 n_decl times.
    // ⚠⚠ `idx[k]` is `opline->extended_value` and it is `k` because the count
    // starts at zero. It is written out rather than folded away because the
    // row is about the count moving with nothing written.
    let mut idx: [usize; MAXD] = [0usize; MAXD];
    let mut num_interfaces: usize = 0;
    let mut d0: usize = 0;
    while d0 < n_decl
        invariant
            d0 <= n_decl,
            n_decl <= MAXD,
            num_interfaces == d0,
            idx@.len() == MAXD,
            forall|j: int| 0 <= j < d0 ==> #[trigger] idx@[j] == j,
        decreases n_decl - d0,
    {
        idx[d0] = num_interfaces;                   // :2591
        num_interfaces = num_interfaces + 1;
        d0 = d0 + 1;
    }

    // phase 2, zend_compile.c:2569-2572. Sized to the COUNT, nothing written.
    // ⭐ `MaybeUninit::uninit()` rather than `Vec::set_len` +
    // `spare_capacity_mut`: that shape is R4's most natural one and the pinned
    // vstd specifies NEITHER of those two, so it is unverifiable here and R4
    // and R5 must be the same program (../spec.md `identity`).
    let mut slots: Vec<MaybeUninit<u32>> = Vec::with_capacity(num_interfaces);
    let mut u: usize = 0;
    while u < num_interfaces
        invariant
            u <= num_interfaces,
            slots@.len() == u,
            forall|j: int|
                0 <= j < u ==> #[trigger] slots@[j].mem_contents() == MemContents::<u32>::Uninit,
        decreases num_interfaces - u,
    {
        slots.push(MaybeUninit::uninit());
        u = u + 1;
    }
    let mut wrote: [bool; MAXD] = [false; MAXD];
    assert(forall|j: int| 0 <= j < MAXD ==> !(#[trigger] wrote@[j]));
    assert(abst(slots@, wrote@, n_decl as int) =~= Seq::new(n_decl as nat, |i: int| None::<u32>));

    let ghost target = run_ops(
        win@,
        n_decl as int,
        n_pool as int,
        pool@,
        0,
        n_ops as int,
        Seq::new(n_decl as nat, |i: int| None::<u32>),
        0u64,
    );

    let mut acc: u64 = 0;
    let mut o: usize = 0;
    while o < n_ops
        invariant
            o <= n_ops,
            n_ops <= cap,
            OPS_OFF as int + OP_BYTES as int * (cap as int) <= len as int,
            win@.len() == len,
            n_decl <= MAXD,
            1 <= n_pool <= MAXP,
            idx@.len() == MAXD,
            forall|j: int| 0 <= j < n_decl ==> #[trigger] idx@[j] == j,
            slots@.len() == n_decl,
            wrote@.len() == MAXD,
            pool@ == pool_of(win@),
            forall|j: int|
                0 <= j < n_decl ==> (#[trigger] wrote@[j] ==> slots@[j].mem_contents().is_init()
                    && slots@[j].mem_contents().value() < n_pool),
            run_ops(
                win@,
                n_decl as int,
                n_pool as int,
                pool@,
                o as int,
                n_ops as int,
                abst(slots@, wrote@, n_decl as int),
                acc,
            ) == target,
        decreases n_ops - o,
    {
        // Every byte of this op record is inside the window.
        assert(OPS_OFF as int + OP_BYTES as int * (o as int) + OP_BYTES as int <= len
            as int) by (nonlinear_arith)
            requires
                (o as int) < n_ops as int,
                n_ops as int <= cap as int,
                OPS_OFF as int + OP_BYTES as int * (cap as int) <= len as int,
                OP_BYTES as int == 9,
        ;
        let p: usize = OPS_OFF + OP_BYTES * o;
        let op: u32 = (win_get_unchecked(win, p) as u32) % 3;
        let a: u32 = rd32(win, p + 1);
        let b: u32 = rd32(win, p + 5);
        let ghost a0 = abst(slots@, wrote@, n_decl as int);
        if op == 0 {
            let d: usize = if n_decl > 0 {
                (a as usize) % n_decl
            } else {
                0
            };
            let pi: u32 = (b % (n_pool as u32)) as u32;
            if n_decl > 0 {
                slot_set_unchecked(&mut slots, idx[d], MaybeUninit::new(pi));
                wrote[idx[d]] = true;
                assert(idx@[d as int] == d);
                assert(abst(slots@, wrote@, n_decl as int) =~= a0.update(d as int, Some(pi)));
            }
            acc = acc.wrapping_mul(31).wrapping_add(d as u64);
        } else if op == 1 {
            let t: usize = (a as usize) % n_pool;
            let tid: u64 = pool_get_unchecked(&pool, t);
            let (hit, matched, examined) = instanceof_ex(&slots, &wrote, &pool, tid);
            acc = acc.wrapping_mul(31).wrapping_add(hit);
            acc = acc.wrapping_mul(31).wrapping_add(matched);
            acc = acc.wrapping_mul(31).wrapping_add(examined);
        } else {
            let t: u32 = (a % (n_pool as u32)) as u32;
            let i: usize = inherit_scan(&slots, &wrote, t);
            acc = acc.wrapping_mul(31).wrapping_add((i != slots.len()) as u64);
            acc = acc.wrapping_mul(31).wrapping_add(i as u64);
        }
        o = o + 1;
    }
    assert(acc == target.1);

    let t: u64 = tally(n_decl);
    assert(iface_win(win@, len as int) == target.1 ^ tally_of(n_decl as int));
    acc ^ t
}

// ---------------------------------------------------------------- driver ----
fn main() {
    let (n_iters, stride_w, bytes) = load_input();
    // SLB-DRIVER-BEGIN
    let n_blob: usize = bytes.len();
    let buf: &[u8] = bytes.as_slice();
    let mut acc: u64 = 0;
    if stride_w >= 76 && stride_w <= n_blob as u64 {
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
                76 <= stride <= n_blob,
                buf@.len() == n_blob,
                nwin == n_blob / stride,
                nwin >= 1,
            decreases n_iters - it,
        {
            // Ghost only: `k` must land inside the blob. Two nonlinear steps,
            // so Z3 needs both spelled out. Erases at compile time -- R4 and
            // R5 stay byte-identical.
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
            // Without it the postcondition is decoration -- deleting it
            // entirely still verifies, so nothing but mutation testing
            // defends it (`.memory/04-verus.md`).
            assert(r == iface_fold(buf@, (k * stride) as int, stride as int));
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    emit(acc);
}

} // verus!
