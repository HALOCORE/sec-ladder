//! p34 rung R5 -- unsafe Rust + a Verus proof.
//!
//! This is unsafe.rs's exec code with the SAFETY comments turned into
//! obligations a verifier discharges. **What is new here is which obligation,
//! and it is the hardest one in this project.**
//!
//! p27's R5 proves *at the moment of the read, the record still exists*, and one
//! `PointsTo<u8>` per slot carries it: a slot is alive or it is not. **p34 cannot
//! do that, because a `PointsTo` is LINEAR and p34's whole subject is ALIASING**
//! -- two stack entries naming one object is the normal, correct state of this
//! kernel, and there is only one permission to go round. So the permission is
//! keyed by OBJECT rather than by stack entry, and the proof carries the bridge
//! between the two:
//!
//! > **`perms[k].value().rc == cnt(stk, k)`** -- the count stored in the
//! > object's own first word equals the NUMBER OF STACK ENTRIES naming it.
//!
//! `cnt` is an occurrence count over a `Seq<int>`, and to the best of this
//! project's knowledge it is **the first multiset-flavoured obligation in the
//! tree**: every other R5 here proves a spatial fact about one index, or (p27,
//! p29) a liveness fact about one slot. ../NOTES.md 6 states what that costs.
//!
//! **The proof forces the line the C rung forgot.** Delete `obj_retain` from the
//! DUP arm and the invariant cannot be re-established: `cnt(stk, k)` has gone up
//! by one and `rc` has not. **And the failure is not merely a refinement
//! failure**: with the count out of step, `obj_dec`'s `requires rc > 0` is
//! unprovable at the second release and `obj_free`'s permission has already been
//! consumed. ../controls/proof_mutants.py demonstrates it with an ATTACK arm, a
//! VACUITY arm, an X1 arm that strikes the central conjunct itself, and a
//! spec-only arm.
//!
//! ⚠⚠ **LEAK-FREEDOM IS PROVED HERE TOO, AND IT IS A COROLLARY RATHER THAN A
//! SEPARATE OBLIGATION.** `obj_ok` says a key in the permission map has
//! `cnt(stk, k) > 0`; the epilogue runs until `ntop == 0`, so `stk` is empty and
//! `cnt` is `0` for every `k`; therefore the map is EMPTY when the kernel
//! returns. The `assert(perms.dom() =~= Set::empty())` at the end of the kernel
//! is that statement, and deleting the epilogue makes it fail. ⚠ Note what this
//! does NOT say: Verus does not force a tracked resource to be consumed, so a
//! rung that simply dropped the map would verify -- what is proved is that THIS
//! rung's map is empty, not that any rung's must be.
//!
//! ⚠ **WHAT `Rc` WOULD HAVE COST, AND WHY IT IS NOT USED.** The pinned
//! `~/tools/verus/vstd/std_specs/smart_ptrs.rs` is **78 lines** and has no
//! `strong_count`, no `Rc::clone`, no `into_raw`/`from_raw` and no
//! `increment_strong_count`, so there is no route to a proof ABOUT `Rc`'s
//! counter at this pin. **That is a RESULT and it is reported as one**
//! (../NOTES.md 6); it is also the reason this rung models the counter itself,
//! which is what the C rung does anyway.
//!
//! **TCB: seven items** -- `buf_get_unchecked`, `arr_get_unchecked`,
//! `arr_set_unchecked`, `rec_alloc`, `rec_free`, `load_input`, `emit`. Exactly
//! p27's seven, and **the reference-counting obligation costs none of them**.
//! Two are the allocation API, copied from vstd for a CODEGEN reason rather than
//! a trust reason -- vstd carries no `#[inline]`, so an R5 that called vstd's
//! `allocate` emits a GOT-indirect cross-crate `call` R4 cannot produce -- and
//! **their verified twins are vstd's own `allocate` and `deallocate`**, so the
//! gate re-derives every run that the copies are no stronger than the originals.
//! ⚠ p34's `rec_alloc` ships **FOUR** of vstd's five `ensures` where p27 ships
//! three. The one p27 drops and p34 keeps is the ALIGNMENT conjunct: p27
//! allocates at `align == 1`, so it is trivial there, while
//! `PointsToRaw::into_typed::<Obj>` needs it here at `align == 8`. The one BOTH
//! drop is `pt.0.addr() + size <= usize::MAX + 1`, **and on p34 that is the
//! gate's finding rather than the author's judgement**: the first full run of
//! stage 5c reported it NOT LOAD-BEARING -- deleting it still gave `24 verified,
//! 0 errors` -- so it was deleted, which is a strict WEAKENING and the direction
//! the gate asks for. ../NOTES.md 6d records the move and the contract hash it
//! cost.
//!
//! ⚠⚠ **THE LAYOUT FACT IS A `global layout` DIRECTIVE AND NOT AN AXIOM, AND
//! THAT IS WORTH KNOWING.** `vstd::layout::size_of` is UNINTERPRETED for a user
//! struct -- there is no axiom anywhere in the pinned vstd that says a struct
//! with a `usize` field is bigger than zero bytes -- so `into_typed` and
//! `rec_alloc`'s `size != 0` cannot be discharged without telling Verus the
//! layout. `global layout Obj is size == 24, align == 8;` does that, **and rustc
//! CHECKS it at codegen**: with a wrong number the file still verifies and then
//! fails to compile with `evaluation panicked: does not have the expected size`.
//! It is the one layout fact in this tree that the compiler, rather than a
//! reviewer, is responsible for. ../NOTES.md 6a.
//!
//! SAFETY (1): `off + len <= buf.len()` is the caller's structural
//!   precondition. Unchecked in unsafe.rs; discharged at the call site here.
//! SAFETY (2): `len >= 4` guards the window header.
//! SAFETY (3): the op is read only under `len - p >= 2` with `p <= len`.
//! SAFETY (4): every `stk[i]` is formed under `i < ntop <= CAP`.
//! SAFETY (5): **THE TEMPORAL ONE.** `wf` below says the permission map's domain
//!   is exactly the set of objects some stack entry names, that each one's
//!   stored `rc` equals the number of entries naming it, and that each one's
//!   permission names that entry's pointer. `obj_free` is reachable only when
//!   the decrement returned 0, i.e. only when the count -- and therefore the
//!   number of live entries -- is zero.

// Plain-Rust I/O helpers. Outside `verus!`, so Verus treats the whole module as
// external (external-by-default). Reached only through `load_input`/`emit`.
#[path = "../../common/driver.rs"]
mod driver;

use vstd::layout::*;
use vstd::map::*;
use vstd::prelude::*;
use vstd::raw_ptr::*;

verus! {

// `group_slice_axioms` gives `slice@.len() == spec_slice_len(slice)`, hence
// `slice@.len() <= usize::MAX` -- without it `off + len` cannot be shown not to
// overflow `usize`. `group_array_axioms` gives `stk@.len() == CAP` for a
// `[*mut Obj; CAP]`, the fill axiom for `[null_mut(); CAP]`, and the same two
// for the `[u8; DLEN]` payload. `group_layout_axioms` is what `valid_layout`
// needs beside the `global layout` directive below. `group_raw_ptr_axioms` is
// what turns `ptr_mut_from_data(p@) == p` -- and the `*mut u8` <-> `*mut Obj`
// casts -- into usable facts. `lemma_u128_shr_is_div` and
// `lemma_mul_inequality` are the DRIVER's, not the kernel's.
broadcast use {
    vstd::slice::group_slice_axioms,
    vstd::array::group_array_axioms,
    vstd::layout::group_layout_axioms,
    vstd::raw_ptr::group_raw_ptr_axioms,
    vstd::bits::lemma_u128_shr_is_div,
    vstd::arithmetic::mul::lemma_mul_inequality,
};

/// The stack's extent, a compile-time constant in every rung.
pub const CAP: usize = 16;

/// Payload bytes per object, a compile-time constant in every rung.
pub const DLEN: usize = 8;

/// What a rejected operation folds. A compile-time constant in every rung.
pub const SENT: u64 = 251;

/// One heap object: the reference count in its own first word, a length, and the
/// payload. `#[repr(C)]` fixes the field order to the one c/kernel.c's disclosed
/// layout note describes.
#[repr(C)]
#[derive(Clone, Copy)]
pub struct Obj {
    pub rc: usize,
    pub len: usize,
    pub data: [u8; DLEN],
}

// THE LAYOUT, told to Verus and CHECKED BY RUSTC AT CODEGEN. See the header:
// `size_of` is uninterpreted for a user struct at the pinned vstd, so without
// this directive neither `rec_alloc`'s `size != 0` nor `into_typed`'s alignment
// precondition can be discharged. A wrong value here verifies and then fails to
// compile.
global layout Obj is size == 24, align == 8;

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

/// An object's payload byte is a function of the operand that created it, in
/// every rung: `a * 7 + 1` truncated to a byte.
pub open spec fn val_of(a: u8) -> u8 {
    a.wrapping_mul(7).wrapping_add(1)
}

/// HOW MANY STACK ENTRIES NAME OBJECT `k`. **This is the function p34's
/// invariant is built out of**, and it is the reason this R5 is not p27's: a
/// `PointsTo` is linear and cannot be split between two aliases, so the proof
/// counts the aliases instead of holding one permission per alias.
pub open spec fn cnt(s: Seq<int>, k: int) -> nat
    decreases s.len(),
{
    if s.len() == 0 {
        0nat
    } else {
        cnt(s.drop_last(), k) + (if s.last() == k {
            1nat
        } else {
            0nat
        })
    }
}

/// `cnt` of a push. The DUP and NEW arms both need it.
pub proof fn lemma_cnt_push(s: Seq<int>, x: int, k: int)
    ensures
        cnt(s.push(x), k) == cnt(s, k) + (if x == k {
            1int
        } else {
            0int
        }),
{
    assert(s.push(x).drop_last() =~= s);
}

/// `cnt` of a `drop_last`. The POP and epilogue arms both need it.
pub proof fn lemma_cnt_drop(s: Seq<int>, k: int)
    requires
        s.len() > 0,
    ensures
        cnt(s, k) == cnt(s.drop_last(), k) + (if s.last() == k {
            1int
        } else {
            0int
        }),
{
}

/// **THE LEMMA THE `free` RESTS ON.** A count of zero means no entry names the
/// object, so releasing the permission cannot strand a live alias.
pub proof fn lemma_cnt_zero(s: Seq<int>, k: int)
    requires
        cnt(s, k) == 0,
    ensures
        forall|i: int| 0 <= i < s.len() ==> s[i] != k,
    decreases s.len(),
{
    if s.len() > 0 {
        lemma_cnt_zero(s.drop_last(), k);
        assert forall|i: int| 0 <= i < s.len() implies s[i] != k by {
            if i < s.len() - 1 {
                assert(s.drop_last()[i] == s[i]);
            }
        }
    }
}

/// The converse, which the NEW arm needs: an object no entry names has count 0.
pub proof fn lemma_cnt_absent(s: Seq<int>, k: int)
    requires
        forall|i: int| 0 <= i < s.len() ==> s[i] != k,
    ensures
        cnt(s, k) == 0,
    decreases s.len(),
{
    if s.len() > 0 {
        assert forall|i: int| 0 <= i < s.drop_last().len() implies s.drop_last()[i] != k by {
            assert(s.drop_last()[i] == s[i]);
        }
        lemma_cnt_absent(s.drop_last(), k);
        assert(s.last() == s[s.len() - 1]);
    }
}

/// `cnt` never exceeds the stack depth, which is what keeps `rc + 1` from
/// overflowing on the DUP path.
pub proof fn lemma_cnt_le(s: Seq<int>, k: int)
    ensures
        cnt(s, k) <= s.len(),
    decreases s.len(),
{
    if s.len() > 0 {
        lemma_cnt_le(s.drop_last(), k);
    }
}

/// THE ABSTRACT MACHINE, and the whole functional specification.
///
/// `stk` is a stack of OBJECT IDS and `vals[k]` is object `k`'s payload byte;
/// `vals.len()` is how many objects the window has created, which is what the
/// kernel folds last. ⚠⚠ **There is no reference count in this function at
/// all.** Under the checked semantics an object is alive exactly while some
/// entry names it and its payload never changes, so the ANSWER is a function of
/// the id stack alone. The counting is an IMPLEMENTATION obligation and it lives
/// in `wf`, not here -- which is why `controls/proof_mutants.py`'s attack arm
/// fails on memory safety rather than on the postcondition.
///
/// Note what this says and does not say: it describes the PROGRAM -- push until
/// the stack is full, duplicate only a non-empty stack that has room, pop only a
/// non-empty stack, read through `a % depth`, fold SENT otherwise -- and it says
/// nothing about `nops` being honest or the op stream being well formed. Every
/// adversarial input is inside this domain (`../spec.md`).
pub open spec fn run(
    buf: Seq<u8>,
    off: int,
    len: int,
    o: int,
    nops: int,
    p: int,
    stk: Seq<int>,
    vals: Seq<u8>,
    acc: u64,
) -> u64
    decreases nops - o,
{
    if o >= nops || len - p < 2 {
        acc.wrapping_mul(31).wrapping_add(vals.len() as u64)
    } else {
        let c = buf[off + p];
        let a = buf[off + p + 1];
        if c % 4 == 0 {
            if stk.len() < CAP as int {
                run(
                    buf,
                    off,
                    len,
                    o + 1,
                    nops,
                    p + 2,
                    stk.push(vals.len() as int),
                    vals.push(val_of(a)),
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
                    stk,
                    vals,
                    acc.wrapping_mul(31).wrapping_add(SENT),
                )
            }
        } else if c % 4 == 1 {
            if stk.len() > 0 && stk.len() < CAP as int {
                run(
                    buf,
                    off,
                    len,
                    o + 1,
                    nops,
                    p + 2,
                    stk.push(stk.last()),
                    vals,
                    acc.wrapping_mul(31).wrapping_add(1),
                )
            } else {
                run(
                    buf,
                    off,
                    len,
                    o + 1,
                    nops,
                    p + 2,
                    stk,
                    vals,
                    acc.wrapping_mul(31).wrapping_add(SENT),
                )
            }
        } else if c % 4 == 2 {
            if stk.len() > 0 {
                run(
                    buf,
                    off,
                    len,
                    o + 1,
                    nops,
                    p + 2,
                    stk.drop_last(),
                    vals,
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
                    stk,
                    vals,
                    acc.wrapping_mul(31).wrapping_add(SENT),
                )
            }
        } else {
            if stk.len() > 0 {
                run(
                    buf,
                    off,
                    len,
                    o + 1,
                    nops,
                    p + 2,
                    stk,
                    vals,
                    acc.wrapping_mul(31).wrapping_add(
                        vals[stk[(a as int) % (stk.len() as int)]] as u64,
                    ),
                )
            } else {
                run(
                    buf,
                    off,
                    len,
                    o + 1,
                    nops,
                    p + 2,
                    stk,
                    vals,
                    acc.wrapping_mul(31).wrapping_add(SENT),
                )
            }
        }
    }
}

/// What the kernel must return.
pub open spec fn rc_fold(buf: Seq<u8>, off: int, len: int) -> u64 {
    if len < 4 {
        0
    } else if nops_at(buf, off) == 0 {
        0
    } else {
        run(buf, off, len, 0, nops_at(buf, off), 4, Seq::empty(), Seq::empty(), 0)
    }
}

/// ONE OBJECT'S HALF OF THE TEMPORAL INVARIANT. `perms` and `dal` are the linear
/// resources; an object the permission map knows about has both, its stored
/// count equals the number of stack entries naming it, and that number is not
/// zero -- which is what makes the map's domain exactly the live set.
pub open spec fn obj_ok(
    k: int,
    stk: Seq<int>,
    vals: Seq<u8>,
    perms: Map<int, PointsTo<Obj>>,
    dal: Map<int, Dealloc>,
) -> bool {
    &&& dal.dom().contains(k)
    &&& perms[k].is_init()
    &&& perms[k].value().rc == cnt(stk, k)
    &&& cnt(stk, k) > 0
    &&& 0 <= k < vals.len()
    &&& perms[k].value().data@[0] == vals[k]
    &&& dal[k].addr() == perms[k].ptr().addr()
    &&& dal[k].size() == size_of::<Obj>()
    &&& dal[k].align() == align_of::<Obj>()
    &&& dal[k].provenance() == perms[k].ptr()@.provenance
}

/// **THE TEMPORAL INVARIANT, AND THE SENTENCE `c/kernel.c` VIOLATES.** The
/// bridge is the third conjunct of `obj_ok`: the count the object stores equals
/// the number of stack entries naming it. Everything else here is bookkeeping
/// around that one equation.
pub open spec fn wf(
    stke: Seq<*mut Obj>,
    ntop: int,
    stk: Seq<int>,
    vals: Seq<u8>,
    perms: Map<int, PointsTo<Obj>>,
    dal: Map<int, Dealloc>,
) -> bool {
    &&& 0 <= ntop <= CAP as int
    &&& stke.len() == CAP as int
    &&& stk.len() == ntop
    &&& forall|i: int| 0 <= i < ntop ==> perms.dom().contains(#[trigger] stk[i])
    &&& forall|i: int| 0 <= i < ntop ==> perms[#[trigger] stk[i]].ptr() == stke[i]
    &&& forall|k: int| #[trigger] perms.dom().contains(k) ==> obj_ok(k, stk, vals, perms, dal)
}

// ------------------------------------------------------------------- TCB ----
// TRUSTED ITEM 1 of 7. vstd ships no specification for `<[T]>::get_unchecked`,
// so this is the axiom that licenses the unchecked read of the window. It is
// sound because the standard library's documented contract for `get_unchecked`
// is exactly this: if the caller guarantees `i < v.len()`, the call is defined
// and yields `v[i]`. Identical, character for character, to the accessor p01,
// p02, p03, p05, p06, p07, p11, p12, p13, p14, p16, p17, p27, p29, p32 and p35
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

// TRUSTED ITEM 6 of 7. Argument parsing, file I/O and little-endian decoding,
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

// TRUSTED ITEM 7 of 7. `println!` is not verifiable; no `ensures`. Counted with
// the six above -- every `external_body` item is TCB, not just the interesting
// one (`.memory/04-verus.md`).
#[verifier::external_body]
fn emit(acc: u64) {
    driver::emit(acc);
}

// TRUSTED ITEM 2 of 7. The unchecked ARRAY read, generic over the element type
// so that the pointer stack and the object payload share ONE axiom instead of
// two. vstd ships no specification for `<[T; N]>::get_unchecked`, and the
// standard library's documented contract is exactly this `requires`/`ensures`
// pair. ../NOTES.md 5 prices the checked spelling on this pattern.
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

// THE VERIFIED TWIN of trusted item 2.
#[cfg(slb_twin)]
fn slb_twin_arr_get_unchecked<T: Copy, const N: usize>(v: &[T; N], i: usize) -> (r: T)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    v[i]
}

// TRUSTED ITEM 3 of 7. The unchecked ARRAY store, same shape. The `ensures` is a
// whole-sequence equality (`update`), not a statement about slot `i` alone, so
// it says both "slot `i` became `x`" and "nothing else moved".
//
// `x` is a pure VALUE parameter -- stored, never used as an address or a length
// -- so it has no precondition, and `../spec.md`'s `verus.unsafe_justifications`
// says so and the gate shouts it every run.
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

// THE VERIFIED TWIN of trusted item 3.
#[cfg(slb_twin)]
fn slb_twin_arr_set_unchecked<T: Copy, const N: usize>(v: &mut [T; N], i: usize, x: T)
    requires
        i < old(v)@.len(),
    ensures
        final(v)@ == old(v)@.update(i as int, x),
{
    v[i] = x;
}

// TRUSTED ITEM 4 of 7. This is `vstd::raw_ptr::allocate` (`raw_ptr.rs:908`) --
// vstd's `requires` verbatim, **FOUR of vstd's FIVE `ensures`**, and vstd's body
// with `alloc::alloc::` respelled `std::alloc::` -- copied into this crate for
// ONE reason, which is codegen: vstd carries no `#[inline]` on `allocate`, so a
// rung that called it would emit a GOT-indirect cross-crate `call` that
// unsafe.rs cannot produce, and R4 and R5 would stop being the same machine
// code (p27's TASK_055 measurement).
//
// ⚠ p27 ships THREE of the five and drops the alignment and address-range
// conjuncts because its records are `u8` at `align == 1`. p34's object is
// `align == 8` and `PointsToRaw::into_typed::<Obj>` requires
// `start % align_of::<Obj>() == 0`, so **the alignment conjunct is load-bearing
// here and the gate's clause-mutation stage says so** -- while
// `pt.0.addr() + size <= usize::MAX + 1` is NOT, on this pattern as on p27, and
// stage 5c is what found that out. Dropping it makes the item strictly WEAKER,
// which is the direction the gate asks for.
//
// **Its verified twin is vstd's `allocate` itself**, so the gate proves that
// this contract is no stronger than the one vstd already discharges.
#[inline(always)]
#[verifier::external_body]
fn rec_alloc(size: usize, align: usize) -> (pt: (
    *mut u8,
    Tracked<PointsToRaw>,
    Tracked<Dealloc>,
))
    requires
        valid_layout(size, align),
        size != 0,
    ensures
        pt.1@.is_range(pt.0.addr() as int, size as int),
        pt.2@@ == (DeallocData {
            addr: pt.0.addr(),
            size: size as nat,
            align: align as nat,
            provenance: pt.1@.provenance(),
        }),
        pt.0.addr() as int % align as int == 0,
        pt.0@.provenance == pt.1@.provenance(),
    opens_invariants none
{
    // SAFETY: valid_layout is a precondition
    let layout = unsafe { std::alloc::Layout::from_size_align_unchecked(size, align) };
    // SAFETY: size != 0
    let p = unsafe { std::alloc::alloc(layout) };
    if p == core::ptr::null_mut() {
        std::process::abort();
    }
    (p, Tracked::assume_new(), Tracked::assume_new())
}

// THE VERIFIED TWIN of trusted item 4, and it is vstd's own `allocate`. If this
// item's contract were stronger than vstd's in any respect, this twin would not
// verify.
#[cfg(slb_twin)]
fn slb_twin_rec_alloc(size: usize, align: usize) -> (pt: (
    *mut u8,
    Tracked<PointsToRaw>,
    Tracked<Dealloc>,
))
    requires
        valid_layout(size, align),
        size != 0,
    ensures
        pt.1@.is_range(pt.0.addr() as int, size as int),
        pt.2@@ == (DeallocData {
            addr: pt.0.addr(),
            size: size as nat,
            align: align as nat,
            provenance: pt.1@.provenance(),
        }),
        pt.0.addr() as int % align as int == 0,
        pt.0@.provenance == pt.1@.provenance(),
    opens_invariants none
{
    allocate(size, align)
}

// TRUSTED ITEM 5 of 7, and THE REAL `free`. `vstd::raw_ptr::deallocate`
// (`raw_ptr.rs:948`): all six of vstd's `requires` and no `ensures`, exactly as
// vstd has it, local for the same codegen reason as item 4, with vstd's own
// `deallocate` as its twin. ⚠ Two respellings, neither semantic: vstd
// destructures its tracked parameters and so writes `dealloc.addr()`, while this
// item takes plain `pt` / `dealloc` and writes `dealloc@.addr()`; and the body
// writes `std::alloc::dealloc` where vstd writes `::alloc::alloc::`.
//
// **It CONSUMES the `PointsToRaw` and the `Dealloc`**, and that is what makes a
// later touch of the same object unprovable rather than merely wrong. A
// free-list push into a slab would consume nothing, the stale read would be in
// bounds of a live allocation, and the bug would be p32's row instead of this
// one (../spec.md).
#[inline(always)]
#[verifier::external_body]
fn rec_free(
    p: *mut u8,
    size: usize,
    align: usize,
    pt: Tracked<PointsToRaw>,
    dealloc: Tracked<Dealloc>,
)
    requires
        dealloc@.addr() == p.addr(),
        dealloc@.size() == size,
        dealloc@.align() == align,
        dealloc@.provenance() == pt@.provenance(),
        pt@.is_range(dealloc@.addr() as int, dealloc@.size() as int),
        p@.provenance == dealloc@.provenance(),
    opens_invariants none
{
    // SAFETY: ensured by the dealloc token
    let layout = unsafe { std::alloc::Layout::from_size_align_unchecked(size, align) };
    unsafe {
        std::alloc::dealloc(p, layout);
    }
}

// THE VERIFIED TWIN of trusted item 5, and it is vstd's own `deallocate`.
#[cfg(slb_twin)]
fn slb_twin_rec_free(
    p: *mut u8,
    size: usize,
    align: usize,
    pt: Tracked<PointsToRaw>,
    dealloc: Tracked<Dealloc>,
)
    requires
        dealloc@.addr() == p.addr(),
        dealloc@.size() == size,
        dealloc@.align() == align,
        dealloc@.provenance() == pt@.provenance(),
        pt@.is_range(dealloc@.addr() as int, dealloc@.size() as int),
        p@.provenance == dealloc@.provenance(),
    opens_invariants none
{
    deallocate(p, size, align, pt, dealloc)
}

// --------------------------------------------------------- the object ops ---
// **NOT trusted items.** `obj_new`, `obj_retain`, `obj_dec`, `obj_read` and
// `obj_free` are ordinary verified functions. Everything unchecked they do
// happens either inside vstd -- `ptr_mut_write`, `ptr_mut_ref` and `ptr_ref` are
// `external_body` there, `into_typed`, `into_raw` and `leak_contents` are vstd
// `axiom fn`s -- or inside items 2 to 5, whose twins are vstd's own API.
//
// They are free functions rather than inline expressions because unsafe.rs has
// to be byte-identical to this file, and its own `obj_*` are the same five
// bodies with the permissions deleted.
#[inline(always)]
fn obj_new(val: u8) -> (r: (*mut Obj, Tracked<PointsTo<Obj>>, Tracked<Dealloc>))
    ensures
        r.1@.ptr() == r.0,
        r.1@.is_init(),
        r.1@.value().rc == 1,
        r.1@.value().data@[0] == val,
        r.2@.addr() == r.0.addr(),
        r.2@.size() == size_of::<Obj>(),
        r.2@.align() == align_of::<Obj>(),
        r.2@.provenance() == r.0@.provenance,
{
    let size = core::mem::size_of::<Obj>();
    let align = core::mem::align_of::<Obj>();
    let (base, Tracked(raw), Tracked(dealloc)) = rec_alloc(size, align);
    let tracked mut pt = raw.into_typed::<Obj>(base.addr());
    let q: *mut Obj = base as *mut Obj;
    let mut d: [u8; DLEN] = [0u8; DLEN];
    arr_set_unchecked(&mut d, 0, val);
    ptr_mut_write(q, Tracked(&mut pt), Obj { rc: 1, len: DLEN, data: d });
    (q, Tracked(pt), Tracked(dealloc))
}

// THE SAFETY LINE, and the only increment in this rung. c/kernel.c omits exactly
// the call to this function. **Its `requires` is where the missing retain would
// be caught if the invariant did not catch it first**: without the count in step
// with the stack, `wf` cannot be re-established after this call.
#[inline(always)]
fn obj_retain(p: *mut Obj, Tracked(pt): Tracked<&mut PointsTo<Obj>>)
    requires
        old(pt).ptr() == p,
        old(pt).is_init(),
        old(pt).value().rc < usize::MAX,
    ensures
        final(pt).ptr() == p,
        final(pt).is_init(),
        final(pt).value().rc == old(pt).value().rc + 1,
        final(pt).value().data == old(pt).value().data,
{
    let r = ptr_mut_ref(p, Tracked(pt));
    r.rc = r.rc + 1;
}

// The release half. ⚠ **`rc > 0` is the precondition `c/kernel.c` cannot
// discharge on its second release**, and it is an ordinary arithmetic obligation
// rather than a permission one -- the permission obligation is `obj_free`'s.
#[inline(always)]
fn obj_dec(p: *mut Obj, Tracked(pt): Tracked<&mut PointsTo<Obj>>) -> (n: usize)
    requires
        old(pt).ptr() == p,
        old(pt).is_init(),
        old(pt).value().rc > 0,
    ensures
        final(pt).ptr() == p,
        final(pt).is_init(),
        final(pt).value().rc == old(pt).value().rc - 1,
        final(pt).value().data == old(pt).value().data,
        n == old(pt).value().rc - 1,
{
    let r = ptr_mut_ref(p, Tracked(pt));
    let n = r.rc - 1;
    r.rc = n;
    n
}

#[inline(always)]
fn obj_read(p: *mut Obj, Tracked(pt): Tracked<&PointsTo<Obj>>) -> (r: u8)
    requires
        pt.ptr() == p,
        pt.is_init(),
    ensures
        r == pt.value().data@[0],
{
    arr_get_unchecked(&ptr_ref(p, Tracked(pt)).data, 0)
}

// THE REAL `free`. `rec_free` CONSUMES the `PointsToRaw` and the `Dealloc`,
// which is what makes a later touch of the same object unprovable.
#[inline(always)]
fn obj_free(p: *mut Obj, Tracked(pt): Tracked<PointsTo<Obj>>, Tracked(dl): Tracked<Dealloc>)
    requires
        pt.ptr() == p,
        dl.addr() == p.addr(),
        dl.size() == size_of::<Obj>(),
        dl.align() == align_of::<Obj>(),
        dl.provenance() == p@.provenance,
{
    let size = core::mem::size_of::<Obj>();
    let align = core::mem::align_of::<Obj>();
    let tracked mut q = pt;
    proof {
        q.leak_contents();
    }
    let tracked raw = q.into_raw();
    rec_free(p as *mut u8, size, align, Tracked(raw), Tracked(dl));
}

// ---------------------------------------------------------------- kernel ----
// Same exec code as unsafe.rs. Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> (r: u64)
    requires
        off + len <= buf@.len(),
    ensures
        r == rc_fold(buf@, off as int, len as int),
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
    let mut stk: [*mut Obj; CAP] = [core::ptr::null_mut(); CAP];
    let mut ntop: usize = 0;
    let mut nnew: usize = 0;
    let tracked mut perms = Map::<int, PointsTo<Obj>>::tracked_empty();
    let tracked mut dal = Map::<int, Dealloc>::tracked_empty();
    let ghost mut ids: Seq<int> = Seq::empty();
    let ghost mut vals: Seq<u8> = Seq::empty();
    let mut acc: u64 = 0;
    let mut p: usize = 4;
    let mut o: usize = 0;
    proof {
        assert(cnt(Seq::<int>::empty(), 0) == 0);
    }
    while o < nops
        invariant_except_break
            o <= nops,
            p <= len,
            off + len <= buf@.len(),
            buf@.len() <= usize::MAX,
            nnew <= o,
            o <= nops,
            vals.len() == nnew as int,
            wf(stk@, ntop as int, ids, vals, perms, dal),
            run(buf@, off as int, len as int, o as int, nops as int, p as int, ids, vals, acc)
                == run(
                buf@,
                off as int,
                len as int,
                0,
                nops as int,
                4,
                Seq::empty(),
                Seq::empty(),
                0,
            ),
        ensures
            wf(stk@, ntop as int, ids, vals, perms, dal),
            vals.len() == nnew as int,
            acc.wrapping_mul(31).wrapping_add(nnew as u64) == run(
                buf@,
                off as int,
                len as int,
                0,
                nops as int,
                4,
                Seq::empty(),
                Seq::empty(),
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
            if ntop < CAP {
                let ghost ids0 = ids;
                let ghost vals0 = vals;
                let ghost perms0 = perms;
                let ghost dal0 = dal;
                let ghost k0: int = nnew as int;
                let (q, Tracked(pt), Tracked(dd)) = obj_new(a.wrapping_mul(7).wrapping_add(1));
                proof {
                    assert forall|i: int| 0 <= i < ids.len() implies ids[i] != k0 by {
                        assert(perms.dom().contains(ids[i]));
                        assert(obj_ok(ids[i], ids, vals, perms, dal));
                    }
                    lemma_cnt_absent(ids, k0);
                    perms.tracked_insert(k0, pt);
                    dal.tracked_insert(k0, dd);
                    ids = ids.push(k0);
                    vals = vals.push(val_of(a));
                }
                arr_set_unchecked(&mut stk, ntop, q);
                ntop = ntop + 1;
                nnew = nnew + 1;
                proof {
                    assert forall|j: int| perms.dom().contains(j) implies obj_ok(
                        j,
                        ids,
                        vals,
                        perms,
                        dal,
                    ) by {
                        lemma_cnt_push(ids0, k0, j);
                        if j != k0 {
                            assert(perms0.dom().contains(j));
                            assert(obj_ok(j, ids0, vals0, perms0, dal0));
                        }
                    }
                }
                acc = acc.wrapping_mul(31).wrapping_add(a as u64);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else if c % 4 == 1 {
            if ntop > 0 && ntop < CAP {
                let ghost ids0 = ids;
                let ghost perms0 = perms;
                let ghost k0: int = ids[ntop as int - 1];
                assert(perms.dom().contains(k0));
                assert(obj_ok(k0, ids, vals, perms, dal));
                proof {
                    lemma_cnt_le(ids, k0);
                }
                let t = arr_get_unchecked(&stk, ntop - 1);
                let tracked mut pt = perms.tracked_remove(k0);
                // THE LINE THE C RUNG FORGOT.
                obj_retain(t, Tracked(&mut pt));
                proof {
                    perms.tracked_insert(k0, pt);
                    ids = ids.push(k0);
                }
                arr_set_unchecked(&mut stk, ntop, t);
                ntop = ntop + 1;
                proof {
                    assert forall|j: int| perms.dom().contains(j) implies obj_ok(
                        j,
                        ids,
                        vals,
                        perms,
                        dal,
                    ) by {
                        lemma_cnt_push(ids0, k0, j);
                        assert(perms0.dom().contains(j));
                        assert(obj_ok(j, ids0, vals, perms0, dal));
                    }
                }
                acc = acc.wrapping_mul(31).wrapping_add(1);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else if c % 4 == 2 {
            if ntop > 0 {
                let ghost ids0 = ids;
                let ghost perms0 = perms;
                let ghost dal0 = dal;
                let ghost k0: int = ids[ntop as int - 1];
                assert(perms.dom().contains(k0));
                assert(obj_ok(k0, ids, vals, perms, dal));
                ntop = ntop - 1;
                let q = arr_get_unchecked(&stk, ntop);
                let tracked mut pt = perms.tracked_remove(k0);
                let tracked dd = dal.tracked_remove(k0);
                let n = obj_dec(q, Tracked(&mut pt));
                proof {
                    ids = ids.drop_last();
                    lemma_cnt_drop(ids0, k0);
                }
                if n == 0 {
                    obj_free(q, Tracked(pt), Tracked(dd));
                    proof {
                        lemma_cnt_zero(ids, k0);
                    }
                } else {
                    proof {
                        perms.tracked_insert(k0, pt);
                        dal.tracked_insert(k0, dd);
                    }
                }
                proof {
                    assert forall|j: int| perms.dom().contains(j) implies obj_ok(
                        j,
                        ids,
                        vals,
                        perms,
                        dal,
                    ) by {
                        lemma_cnt_drop(ids0, j);
                        assert(perms0.dom().contains(j));
                        assert(obj_ok(j, ids0, vals, perms0, dal0));
                    }
                    assert forall|i: int| 0 <= i < ntop as int implies perms.dom().contains(
                        ids[i],
                    ) by {
                        assert(ids[i] == ids0[i]);
                        assert(perms0.dom().contains(ids0[i]));
                    }
                }
                acc = acc.wrapping_mul(31).wrapping_add(2);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else {
            if ntop > 0 {
                let j: usize = (a as usize) % ntop;
                let ghost k0: int = ids[j as int];
                assert(perms.dom().contains(k0));
                assert(obj_ok(k0, ids, vals, perms, dal));
                let tracked tp = perms.tracked_borrow(k0);
                let v: u8 = obj_read(arr_get_unchecked(&stk, j), Tracked(tp));
                acc = acc.wrapping_mul(31).wrapping_add(v as u64);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        }
        o = o + 1;
    }
    // ------- the epilogue: release every reference still on the stack -------
    // R2 and R3 do not have this loop: dropping the stack IS this loop, written
    // by the language. ../NOTES.md 5 prices it.
    while ntop > 0
        invariant
            wf(stk@, ntop as int, ids, vals, perms, dal),
        decreases ntop,
    {
        let ghost ids0 = ids;
        let ghost perms0 = perms;
        let ghost dal0 = dal;
        let ghost k0: int = ids[ntop as int - 1];
        assert(perms.dom().contains(k0));
        assert(obj_ok(k0, ids, vals, perms, dal));
        ntop = ntop - 1;
        let q = arr_get_unchecked(&stk, ntop);
        let tracked mut pt = perms.tracked_remove(k0);
        let tracked dd = dal.tracked_remove(k0);
        let n = obj_dec(q, Tracked(&mut pt));
        proof {
            ids = ids.drop_last();
            lemma_cnt_drop(ids0, k0);
        }
        if n == 0 {
            obj_free(q, Tracked(pt), Tracked(dd));
            proof {
                lemma_cnt_zero(ids, k0);
            }
        } else {
            proof {
                perms.tracked_insert(k0, pt);
                dal.tracked_insert(k0, dd);
            }
        }
        proof {
            assert forall|j: int| perms.dom().contains(j) implies obj_ok(
                j,
                ids,
                vals,
                perms,
                dal,
            ) by {
                lemma_cnt_drop(ids0, j);
                assert(perms0.dom().contains(j));
                assert(obj_ok(j, ids0, vals, perms0, dal0));
            }
            assert forall|i: int| 0 <= i < ntop as int implies perms.dom().contains(ids[i]) by {
                assert(ids[i] == ids0[i]);
                assert(perms0.dom().contains(ids0[i]));
            }
        }
    }
    // LEAK-FREEDOM, as a corollary of the invariant rather than as a separate
    // obligation: `obj_ok` requires `cnt(ids, k) > 0`, and `ids` is empty here.
    proof {
        assert(ids.len() == 0);
        assert forall|k: int| !perms.dom().contains(k) by {
            if perms.dom().contains(k) {
                lemma_cnt_absent(ids, k);
                assert(obj_ok(k, ids, vals, perms, dal));
            }
        }
        assert(perms.dom() =~= Set::<int>::empty());
    }
    acc.wrapping_mul(31).wrapping_add(nnew as u64)
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
            assert(r == rc_fold(buf@, (k * stride) as int, stride as int));
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    emit(acc);
}

} // verus!
