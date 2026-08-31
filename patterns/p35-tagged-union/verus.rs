//! p35 rung R5 -- unsafe Rust + a Verus proof.
//!
//! This is unsafe.rs's exec code with the SAFETY comments turned into
//! obligations a verifier discharges. **What is new here is that ONE of those
//! obligations is a first-class rule of Verus's type system, and the project's
//! own gate cannot use it.** Read ../NOTES.md 6 before quoting anything from
//! this file.
//!
//! ⚠⚠⚠ **VERUS SUPPORTS THE RUST `union` NATIVELY.** Written inside `verus!`,
//! a read of the wrong member is
//!
//!     error: requirement not met: to access this field, the union must be in
//!            the correct variant
//!
//! and `requires p is i` discharges it. That is not a vstd specification and a
//! `std_specs/` grep misses it entirely: it is a LANGUAGE BUILTIN. So the
//! correct-variant obligation -- exactly the thing `c/kernel.c` gets wrong -- is
//! the one obligation in this tree that the prover checks *at the operation*
//! rather than through an axiom.
//!
//! ⚠⚠⚠ **AND THIS FILE DOES NOT USE IT THAT WAY, BECAUSE THE GATE FORBIDS THE
//! SPELLING THAT DOES.** `harness/check.py`'s `_scan_unsafe_sites` requires
//! every `unsafe` TOKEN to sit inside a `#[verifier::external_body]` item's
//! body, and a union read is spelled `unsafe { p.i }` in Rust whether or not
//! Verus checks it. So the three union reads below are wrapped as TRUSTED items
//! -- which moves the read out of the region Verus checks and into an axiom --
//! and each of them then owes a VERIFIED TWIN that **cannot be written, because
//! Rust has no safe spelling of a union read at all** (`error[E0133]`, and
//! `_TWIN_BANNED` forbids `unsafe` in a twin).
//!
//! **The three are declared in `verus.twin_justifications` and the gate BLOCKS
//! them, every run, out loud.** That is the honest configuration and the row
//! ships with the gap as its result -- `p42`'s precedent, *"THE PIN PROTECTED
//! THE PATTERN; THE PROOF DID NOT"*, in a different currency.
//! `../controls/union_oracle.py` measures both configurations side by side: the
//! shipped one, and the one where the read stays in verified code and Verus
//! itself discharges the variant obligation with a must-fail arm. The second is
//! the STRONGER proof and it is the one `check.py` refuses.
//!
//! ⚠ **What the shipped configuration still gets, and it is not nothing.** The
//! wrappers' `requires` are `v@[i] is i` / `is o` / `is d`, and **Verus checks
//! those AT EVERY CALL SITE** -- delete the tag test in front of a `pay_*` call
//! and the proof fails with `precondition not satisfied`. So the tag/variant
//! agreement IS proved.
//!
//! ⚠⚠ **WHAT THE AXIOM COVERS -- CORRECTED AT TASK_153, TASK_152 M5.** This
//! note used to end *"what is axiomatised is only that the wrapper's body
//! reads the member its name says"*. That describes ONE of TWO unchecked
//! operations. `unsafe { v.get_unchecked(i).i }` is an **unchecked INDEX** and
//! a **union field read**, and the axiom asserts both: that the body reads the
//! member its name says, AND that `i < v@.len()` is the whole of what licenses
//! the index. Neither clause's STRENGTH is tested for these three items, which
//! is exactly what their three BLOCKED rows say.
//! ⚠ **A narrower CONFIGURATION C exists and is NOT shipped** -- split the
//! index into a `fn pay_ref(v, i) -> &Pay` that DOES have a safe twin (`&v[i]`,
//! which verifies) and axiomatise only the bare field read, which is the split
//! `pay_set_unchecked` already uses on the WRITE side. It is gate-legal
//! (`_scan_unsafe_sites` -> 0 failures) and verifies `2/0` and `3/0` with the
//! twin (`.temp/t152/verus/c4_split.rs`). It does NOT reduce `blocked`, and it
//! adds a TENTH trusted item; the shipped configuration keeps nine and states
//! the axiom's true width here instead. ../NOTES.md 6a records the choice.
//!
//! ⚠⚠ **AND THE `requires` ITSELF CAN BE DELETED WITHOUT VERUS NOTICING**
//! (`../controls/proof_mutants.py` arm `X1`, TASK_152 M3): strike
//! `v@[i as int] is {i,o,d}` from all three readers and the file still reports
//! `16 verified, 0 errors` at the pinned obligation count. The only thing that
//! catches it is `../spec.md`'s item pin -- a declaration the author writes --
//! and the gate stage that judges STRENGTH rather than triviality, `5c-twin`,
//! is BLOCKED for exactly these three items. In configuration B the same
//! deletion FAILS at the read. ../NOTES.md 6b and 6d.
//!
//! ⚠ **`f64` IS OPAQUE AT THE PINNED vstd AND THE PROOF SAYS SO.** `f64`
//! arithmetic carries an `add_req` precondition nothing discharges and `u8 as
//! f64` is a *"(possibly) non-deterministic"* cast (`vstd/float.rs`), so the
//! DBL payload is built from LITERALS and the `d > 1.0` comparison is
//! axiomatised inside `pay_d_gt1` against the spec function `dbl_gt1`. The
//! proof establishes that the kernel folds `dbl_gt1(dbl_of(a))` consistently
//! with the spec; it does NOT establish what that boolean is. ../NOTES.md 6c.
//!
//! **TCB: nine items** -- `buf_get_unchecked`, `arr_get_unchecked`,
//! `arr_set_unchecked`, `pay_set_unchecked`, `pay_i`, `pay_o`, `pay_d_gt1`,
//! `load_input`, `emit`. Four carry verified twins, three are the union reads
//! that cannot have one, and two (`load_input`/`emit`) are trusted I/O with no
//! `ensures` and are outside the memory-safety argument. ../NOTES.md 6a counts
//! them.
//!
//! SAFETY (1): `off + len <= buf.len()` is the caller's structural
//!   precondition; discharged at the call site in `main`.
//! SAFETY (2): `len >= 4` guards the window header.
//! SAFETY (3): the op is read only under `len - p >= 2` with `p <= len`.
//! SAFETY (4): `idx = a % CELLS` is `< CELLS` for every `a`.
//! SAFETY (5): **the correct-variant obligation**, carried by `wf_cells` and
//!   re-established by every arm of the loop. This is p35's safety line.
//! SAFETY (6): the `T_PTR` payload is `BUDGET - navail` with `navail >= 1`, so
//!   it is `< BUDGET` and `arena[o]` is in bounds. The second half of
//!   `wf_cells`, and the only SPATIAL obligation in this pattern.

// Plain-Rust I/O helpers. Outside `verus!`, so Verus treats the whole module as
// external (external-by-default). Reached only through `load_input`/`emit`.
#[path = "../../common/driver.rs"]
mod driver;

use vstd::prelude::*;

verus! {

// `group_slice_axioms` gives `slice@.len() == spec_slice_len(slice)`, hence
// `slice@.len() <= usize::MAX`. `group_array_axioms` gives `v@.len() == N` and
// the fill axiom for `[0u8; N]`. `lemma_u128_shr_is_div` and
// `lemma_mul_inequality` are the DRIVER's. **No `raw_ptr` and no `layout`
// group: p35 has no pointers and no allocation -- see the module note on why
// the union carries an OFFSET.**
broadcast use {
    vstd::slice::group_slice_axioms,
    vstd::array::group_array_axioms,
    vstd::bits::lemma_u128_shr_is_div,
    vstd::arithmetic::mul::lemma_mul_inequality,
};

/// Tagged cells, a compile-time constant in every rung.
pub const CELLS: usize = 8;

/// The arena, in bytes: how many pointer/double payloads can be issued before
/// the store starts failing. A compile-time constant in every rung.
pub const BUDGET: usize = 4;

/// What a rejected operation folds. A compile-time constant in every rung.
pub const SENT: u64 = 251;

/// The tag alphabet. `T_UNSET` is what a cell nothing has written carries, and
/// it folds `SENT` -- so p35's bug is never "read uninitialised".
pub const T_UNSET: u8 = 0;

pub const T_INT: u8 = 1;

pub const T_PTR: u8 = 2;

pub const T_DBL: u8 = 3;

/// THE UNION, declared INSIDE `verus!` -- outside it Verus asks for an
/// `external_type_specification` and the correct-variant rule is unavailable.
/// The fields are `pub` because `get_union_field` appears in `pub open spec`
/// functions and Verus otherwise treats the datatype as opaque there.
///
/// ⚠ No `#[derive(Clone, Copy)]`: `core::clone::AssertParamIsCopy` is
/// `not supported`. The cell array is therefore built from an eight-element
/// array LITERAL, and unsafe.rs spells it the same way.
pub union Pay {
    pub i: u64,
    pub d: f64,
    pub o: u32,
}

// ------------------------------------------------------------------ spec ----
/// The little-endian u32 at absolute byte position `p`, written out the way
/// every rung writes it. Spelled with `+` and `*` rather than `|` and `<<` on
/// purpose (`.memory/04-verus.md`): the two are the same function on bytes and
/// compile to the same instruction, but only the first is linear arithmetic.
pub open spec fn u32_at(buf: Seq<u8>, p: int) -> int {
    buf[p] as int + 256 * (buf[p + 1] as int) + 65536 * (buf[p + 2] as int) + 16777216 * (
    buf[p + 3] as int)
}

/// How many operations the window at `off` declares. **Declared, and it bounds
/// nothing** -- the cursor guard is what stops the walk.
pub open spec fn nops_at(buf: Seq<u8>, off: int) -> int {
    u32_at(buf, off)
}

/// What SET_INT stores, in every rung.
pub open spec fn int_payload(a: u8) -> u64 {
    (a as u64).wrapping_mul(2654435761)
}

/// The arena, byte for byte, as every rung initialises it.
pub open spec fn arena_byte(k: int) -> u8 {
    (k as u8).wrapping_mul(11).wrapping_add(5)
}

/// What SET_DBL stores. **Two LITERALS** -- see the module note on `f64`.
pub open spec fn dbl_of(a: u8) -> f64 {
    if a % 2 == 0 {
        0.25f64
    } else {
        2.5f64
    }
}

/// The comparison GET makes on the DBL arm. ⚠ Verus cannot connect the EXEC
/// `d > 1.0f64` to this SPEC `x > 1.0f64` at the pinned vstd -- that link is
/// the axiom inside `pay_d_gt1`. What the proof establishes is that the kernel
/// folds this function of the payload, not what the function's value is.
pub open spec fn dbl_gt1(x: f64) -> bool {
    x > 1.0f64
}

/// THE ABSTRACT MACHINE'S STATE: the tag array, the payload array and the
/// budget. The arena is not here because no rung ever writes it -- `arena_byte`
/// is the whole of it.
pub ghost struct St {
    pub tags: Seq<u8>,
    pub pays: Seq<Pay>,
    pub navail: int,
}

/// The three union members, at spec level. ⚠ **These exist because
/// `harness/vparse.py` splits a `requires`/`ensures` clause on top-level
/// commas and does not treat `<...>` as nesting, so the literal spelling
/// `get_union_field::<Pay, u64>(p, "i")` in a clause is torn in half at the
/// generic argument's comma and the `spec.md` pin records two fragments. Naming
/// them is the fix, and it reads better anyway. Reported in
/// `.tasks/TASK_148_REPORT.md`.
pub open spec fn pay_int(p: Pay) -> u64 {
    get_union_field::<Pay, u64>(p, "i")
}

pub open spec fn pay_off(p: Pay) -> u32 {
    get_union_field::<Pay, u32>(p, "o")
}

pub open spec fn pay_dbl(p: Pay) -> f64 {
    get_union_field::<Pay, f64>(p, "d")
}

/// **THE CORRECT-VARIANT INVARIANT, AND IT IS p35's SAFETY LINE WRITTEN AS A
/// PREDICATE.** A cell's tag names the union member its payload actually is,
/// and a `T_PTR` payload is a legal arena offset. `c/kernel.c` breaks the first
/// conjunct; nothing in this pattern can break the second while the first
/// holds.
pub open spec fn wf_cell(t: u8, p: Pay) -> bool {
    &&& (t == T_INT ==> p is i)
    &&& (t == T_PTR ==> p is o && pay_off(p) < BUDGET as u32)
    &&& (t == T_DBL ==> p is d)
}

pub open spec fn wf_cells(st: St) -> bool {
    &&& st.tags.len() == CELLS as int
    &&& st.pays.len() == CELLS as int
    &&& 0 <= st.navail <= BUDGET as int
    &&& forall|k: int| 0 <= k < CELLS as int ==> wf_cell(#[trigger] st.tags[k], st.pays[k])
}

/// ONE OPERATION: the new state and what it folds.
///
/// **The two SET arms are the whole pattern.** Each writes the payload and the
/// tag TOGETHER, inside the `navail > 0` test, so a failed store leaves the
/// cell exactly as it was. `c/kernel.c` writes the tag outside the test.
pub open spec fn step(st: St, c: u8, a: u8) -> (St, u64) {
    let k = (a % (CELLS as u8)) as int;
    if c % 4 == 0 {
        (
            St {
                tags: st.tags.update(k, T_INT),
                pays: st.pays.update(k, Pay { i: int_payload(a) }),
                ..st
            },
            a as u64,
        )
    } else if c % 4 == 1 {
        if st.navail > 0 {
            (
                St {
                    tags: st.tags.update(k, T_PTR),
                    pays: st.pays.update(k, Pay { o: (BUDGET as int - st.navail) as u32 }),
                    navail: st.navail - 1,
                },
                1u64,
            )
        } else {
            (st, SENT)
        }
    } else if c % 4 == 2 {
        if st.navail > 0 {
            (
                St {
                    tags: st.tags.update(k, T_DBL),
                    pays: st.pays.update(k, Pay { d: dbl_of(a) }),
                    navail: st.navail - 1,
                },
                2u64,
            )
        } else {
            (st, SENT)
        }
    } else {
        let t = st.tags[k];
        if t == T_INT {
            (st, pay_int(st.pays[k]) & 0xFFu64)
        } else if t == T_PTR {
            (st, arena_byte(pay_off(st.pays[k]) as int) as u64)
        } else if t == T_DBL {
            (
                st,
                if dbl_gt1(pay_dbl(st.pays[k])) {
                    1u64
                } else {
                    0u64
                },
            )
        } else {
            (st, SENT)
        }
    }
}

/// The empty machine: every tag `T_UNSET`, every payload the zero integer, the
/// budget full.
pub open spec fn st0() -> St {
    St {
        tags: Seq::new(CELLS as nat, |i: int| T_UNSET),
        pays: Seq::new(CELLS as nat, |i: int| Pay { i: 0 }),
        navail: BUDGET as int,
    }
}

/// THE ABSTRACT MACHINE. It describes the PROGRAM -- stop when the window runs
/// out, fold `SENT` for a store the budget cannot serve, fold `SENT` for a cell
/// nothing has written -- and it says nothing about `nops` being honest or
/// about the op stream being well formed. Every adversarial input is inside
/// this domain (../spec.md).
pub open spec fn run(
    buf: Seq<u8>,
    off: int,
    len: int,
    o: int,
    nops: int,
    p: int,
    st: St,
    acc: u64,
) -> u64
    decreases nops - o,
{
    if o >= nops || len - p < 2 {
        acc.wrapping_mul(31).wrapping_add(st.navail as u64)
    } else {
        let s = step(st, buf[off + p], buf[off + p + 1]);
        run(buf, off, len, o + 1, nops, p + 2, s.0, acc.wrapping_mul(31).wrapping_add(s.1))
    }
}

/// What the kernel must return.
pub open spec fn cell_fold(buf: Seq<u8>, off: int, len: int) -> u64 {
    if len < 4 {
        0
    } else if nops_at(buf, off) == 0 {
        0
    } else {
        run(buf, off, len, 0, nops_at(buf, off), 4, st0(), 0)
    }
}

// ------------------------------------------------------------------- TCB ----
// TRUSTED ITEM 1 of 9. vstd ships no specification for `<[T]>::get_unchecked`,
// so this is the axiom that licenses the unchecked read of the window. It is
// sound because the standard library's documented contract for `get_unchecked`
// is exactly this: if the caller guarantees `i < v.len()`, the call is defined
// and returns `v[i]`. Every unsafe rung in this project ships it.
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

// THE VERIFIED TWIN of trusted item 1.
#[cfg(slb_twin)]
fn slb_twin_buf_get_unchecked(v: &[u8], i: usize) -> (r: u8)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    v[i]
}

// TRUSTED ITEMS 2 and 3 of 9: the unchecked ARRAY read and store, generic over
// the element type so that the tag array and the arena share one accessor.
// Same documented `get_unchecked` contract as item 1.
#[inline(always)]
#[verifier::external_body]
fn arr_get_unchecked<T: Copy, const N: usize>(v: &[T; N], i: usize) -> (r: T)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    unsafe { *v.get_unchecked(i) }
}

#[cfg(slb_twin)]
fn slb_twin_arr_get_unchecked<T: Copy, const N: usize>(v: &[T; N], i: usize) -> (r: T)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    v[i]
}

#[inline(always)]
#[verifier::external_body]
fn arr_set_unchecked<T: Copy, const N: usize>(v: &mut [T; N], i: usize, x: T)
    requires
        i < old(v)@.len(),
    ensures
        final(v)@ == old(v)@.update(i as int, x),
{
    unsafe {
        *v.get_unchecked_mut(i) = x;
    }
}

#[cfg(slb_twin)]
fn slb_twin_arr_set_unchecked<T: Copy, const N: usize>(v: &mut [T; N], i: usize, x: T)
    requires
        i < old(v)@.len(),
    ensures
        final(v)@ == old(v)@.update(i as int, x),
{
    v[i] = x;
}

// TRUSTED ITEM 4 of 9: the payload store. `Pay` is not `Copy`, so it cannot
// share `arr_set_unchecked`. ⚠ **Writing a union member is SAFE Rust** -- only
// reading one is not -- so the axiom here is the unchecked INDEX and nothing
// else, and the twin below is an ordinary checked store.
#[inline(always)]
#[verifier::external_body]
fn pay_set_unchecked<const N: usize>(v: &mut [Pay; N], i: usize, x: Pay)
    requires
        i < old(v)@.len(),
    ensures
        final(v)@ == old(v)@.update(i as int, x),
{
    unsafe {
        *v.get_unchecked_mut(i) = x;
    }
}

#[cfg(slb_twin)]
fn slb_twin_pay_set_unchecked<const N: usize>(v: &mut [Pay; N], i: usize, x: Pay)
    requires
        i < old(v)@.len(),
    ensures
        final(v)@ == old(v)@.update(i as int, x),
{
    v[i] = x;
}

// ⚠⚠ TRUSTED ITEMS 5, 6 and 7 of 9: THE THREE UNION READS, AND THE THREE THE
// GATE BLOCKS. Read the module note first.
//
// Each `requires` has TWO conjuncts: the index is in range, and **the cell is
// in the member's variant**. Verus checks BOTH at every call site -- delete the
// tag test in front of one of these calls and the proof fails with
// `precondition not satisfied` -- so the tag/variant agreement is PROVED.
//
// ⚠⚠ WHAT THE AXIOM COVERS, CORRECTED AT TASK_153 (TASK_152 M5). This comment
// read ~~What is axiomatised is only that the body reads the member its name
// says~~, and that names ONE of TWO unchecked operations. Each body below does
// an UNCHECKED INDEX and a UNION FIELD READ, and the axiom asserts both: that
// the member read is the one the item's name says, AND that `i < v@.len()` is
// the whole of what licenses `get_unchecked`. The module note has the narrower
// configuration C that was measured and not shipped.
//
// ⚠⚠ AND THE VARIANT CONJUNCT CAN BE DELETED OUTRIGHT: strike `v@[i as int] is
// {i,o,d}` from all three and the file still verifies at 16 obligations
// (../controls/proof_mutants.py arm `X1`). Nothing but ../spec.md's item pin
// catches it. Configuration B RESISTS the same deletion -- Verus fails at the
// read -- so the two configurations differ in more than axiom-versus-check.
//
// **Neither can have a verified twin**, because Rust has no safe spelling of a
// union read (`error[E0133]`) and `_TWIN_BANNED` forbids `unsafe` in a twin.
// They are declared in `verus.twin_justifications` and the gate BLOCKS them out
// loud on every run. `../controls/union_oracle.py` measures the configuration
// where Verus checks the read itself -- which is STRONGER, and which
// `_scan_unsafe_sites` refuses.
#[inline(always)]
#[verifier::external_body]
fn pay_i<const N: usize>(v: &[Pay; N], i: usize) -> (r: u64)
    requires
        i < v@.len(),
        v@[i as int] is i,
    ensures
        r == pay_int(v@[i as int]),
{
    unsafe { v.get_unchecked(i).i }
}

#[inline(always)]
#[verifier::external_body]
fn pay_o<const N: usize>(v: &[Pay; N], i: usize) -> (r: u32)
    requires
        i < v@.len(),
        v@[i as int] is o,
    ensures
        r == pay_off(v@[i as int]),
{
    unsafe { v.get_unchecked(i).o }
}

// ⚠ This one carries a SECOND axiom beyond the union read: that the exec
// comparison `d > 1.0f64` agrees with the spec function `dbl_gt1`. At the
// pinned vstd there is no way to prove that -- `f64` comparison is specified
// through `partial_cmp`'s existential and its arithmetic through an
// undischargeable `add_req`. See the module note.
#[inline(always)]
#[verifier::external_body]
fn pay_d_gt1<const N: usize>(v: &[Pay; N], i: usize) -> (r: bool)
    requires
        i < v@.len(),
        v@[i as int] is d,
    ensures
        r == dbl_gt1(pay_dbl(v@[i as int])),
{
    unsafe { v.get_unchecked(i).d > 1.0 }
}

// TRUSTED ITEM 8 of 9: the input loader. Plain Rust I/O, no `unsafe`, no
// `ensures` -- it is outside the memory-safety argument entirely.
#[verifier::external_body]
fn load_input() -> (r: (u64, u64, Vec<u8>)) {
    let path = driver::arg_path();
    let inp = driver::load(&path);
    let (stride_w, bytes) = driver::head1_u64_bytes(&inp);
    (inp.n_iters, stride_w, bytes)
}

// TRUSTED ITEM 9 of 9: the output. Same shape, same reason.
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
        r == cell_fold(buf@, off as int, len as int),
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
    let mut tags: [u8; CELLS] = [T_UNSET; CELLS];
    let mut pays: [Pay; CELLS] = [
        Pay { i: 0 },
        Pay { i: 0 },
        Pay { i: 0 },
        Pay { i: 0 },
        Pay { i: 0 },
        Pay { i: 0 },
        Pay { i: 0 },
        Pay { i: 0 },
    ];
    let mut arena: [u8; BUDGET] = [0u8; BUDGET];
    let mut j: usize = 0;
    while j < BUDGET
        invariant
            j <= BUDGET,
            arena@.len() == BUDGET as int,
            forall|k: int| 0 <= k < j as int ==> (#[trigger] arena@[k]) == arena_byte(k),
        decreases BUDGET - j,
    {
        arr_set_unchecked(&mut arena, j, (j as u8).wrapping_mul(11).wrapping_add(5));
        j = j + 1;
    }
    let mut navail: usize = BUDGET;
    let mut acc: u64 = 0;
    let mut p: usize = 4;
    let mut o: usize = 0;
    proof {
        assert(tags@ =~= st0().tags);
        assert(pays@ =~= st0().pays);
        assert(St { tags: tags@, pays: pays@, navail: navail as int } =~= st0());
    }
    while o < nops
        invariant_except_break
            o <= nops,
            p <= len,
            4 <= len,
            off + len <= buf@.len(),
            buf@.len() <= usize::MAX,
            navail <= BUDGET,
            arena@.len() == BUDGET as int,
            forall|k: int|
                0 <= k < BUDGET as int ==> (#[trigger] arena@[k]) == arena_byte(k),
            wf_cells(St { tags: tags@, pays: pays@, navail: navail as int }),
            run(
                buf@,
                off as int,
                len as int,
                o as int,
                nops as int,
                p as int,
                St { tags: tags@, pays: pays@, navail: navail as int },
                acc,
            ) == run(buf@, off as int, len as int, 0, nops as int, 4, st0(), 0),
        ensures
            acc.wrapping_mul(31).wrapping_add(navail as u64) == run(
                buf@,
                off as int,
                len as int,
                0,
                nops as int,
                4,
                st0(),
                0,
            ),
        decreases nops - o,
    {
        if len - p < 2 {
            break;
        }
        let c: u8 = buf_get_unchecked(buf, off + p);
        let a: u8 = buf_get_unchecked(buf, off + p + 1);
        let ghost st_in = St { tags: tags@, pays: pays@, navail: navail as int };
        let ghost acc_in = acc;
        let ghost p_in = p as int;
        let ghost o_in = o as int;
        p = p + 2;
        let idx: usize = (a % CELLS as u8) as usize;
        let v: u64 = if c % 4 == 0 {
            pay_set_unchecked(&mut pays, idx, Pay { i: (a as u64).wrapping_mul(2654435761) });
            arr_set_unchecked(&mut tags, idx, T_INT);
            a as u64
        } else if c % 4 == 1 {
            // ==================== THE SAFETY LINE (1 of 2) ==================
            // Publish the tag only once the payload it describes is in place.
            // c/kernel.c writes the tag store before the `if`, on a path where
            // the payload store may not happen.
            //
            // ⚠ Nothing about this ORDER is forced by a linear resource. What
            // fails without it is `wf_cells` -- the correct-variant invariant --
            // and therefore the `requires` of the `pay_*` call in the GET arm.
            // ../NOTES.md 6b.
            if navail > 0 {
                pay_set_unchecked(&mut pays, idx, Pay { o: (BUDGET - navail) as u32 });
                arr_set_unchecked(&mut tags, idx, T_PTR);
                navail = navail - 1;
                1
            } else {
                SENT
            }
            // ================================================================
        } else if c % 4 == 2 {
            // ==================== THE SAFETY LINE (2 of 2) ==================
            if navail > 0 {
                pay_set_unchecked(
                    &mut pays,
                    idx,
                    if a % 2 == 0 {
                        Pay { d: 0.25 }
                    } else {
                        Pay { d: 2.5 }
                    },
                );
                arr_set_unchecked(&mut tags, idx, T_DBL);
                navail = navail - 1;
                2
            } else {
                SENT
            }
            // ================================================================
        } else {
            let t: u8 = arr_get_unchecked(&tags, idx);
            if t == T_INT {
                pay_i(&pays, idx) & 0xFF
            } else if t == T_PTR {
                arr_get_unchecked(&arena, pay_o(&pays, idx) as usize) as u64
            } else if t == T_DBL {
                if pay_d_gt1(&pays, idx) {
                    1
                } else {
                    0
                }
            } else {
                SENT
            }
        };
        acc = acc.wrapping_mul(31).wrapping_add(v);
        proof {
            let st_out = St { tags: tags@, pays: pays@, navail: navail as int };
            assert(st_out =~= step(st_in, c, a).0);
            assert(v == step(st_in, c, a).1);
            assert(run(buf@, off as int, len as int, o_in, nops as int, p_in, st_in, acc_in)
                == run(
                buf@,
                off as int,
                len as int,
                o_in + 1,
                nops as int,
                p_in + 2,
                st_out,
                acc,
            ));
        }
        o = o + 1;
    }
    // No epilogue: nothing was ever acquired.
    acc.wrapping_mul(31).wrapping_add(navail as u64)
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
            assert(r == cell_fold(buf@, (k * stride) as int, stride as int));
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    emit(acc);
}

} // verus!
