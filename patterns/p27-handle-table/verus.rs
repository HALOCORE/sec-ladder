//! p27 rung R5 -- unsafe Rust + a Verus proof.
//!
//! This is unsafe.rs's exec code with the SAFETY comments turned into
//! obligations a verifier discharges. **What is new here is which obligation.**
//! Every other R5 in this tree proves a *spatial* fact -- an index is inside a
//! buffer. p27's central obligation is a *temporal* one: at the moment of the
//! read, the record still exists. It is carried by a linear resource,
//! `PointsTo<u8>`, which `vstd::raw_ptr::deallocate` **consumes**, so a read
//! after a free has no permission to present and the proof fails.
//!
//! **The proof forces the line the C rung forgot.** `live[h] = 0` is not
//! decoration in this rung: without it the loop invariant cannot be
//! re-established after a CLOSE, because the invariant says *every slot the
//! liveness array calls alive has a permission in the map* and the permission
//! for `h` has just been consumed by `deallocate`. That is the pattern's
//! sentence, and it is checkable by deleting the line (../NOTES.md 10, mutant
//! M2).
//!
//! **TCB: seven items** -- `buf_get_unchecked`, `arr_get_unchecked`,
//! `arr_set_unchecked`, `rec_alloc`, `rec_free`, `load_input`, `emit`. Five of
//! the seven are the SPATIAL accessors and the infra every pattern here ships;
//! **the temporal property costs none of them.** Two of those are the
//! allocation API, and they are here
//! for a CODEGEN reason rather than a trust reason: they are
//! `vstd::raw_ptr::allocate` / `deallocate` copied character for character into
//! this crate so that the call is direct and `#[inline(always)]`, because vstd
//! carries no `#[inline]` and R4 cannot emit a GOT-indirect cross-crate call.
//! **Their verified twins are vstd's own `allocate` and `deallocate`**, so the
//! gate itself proves the copies are no stronger than the originals.
//!
//! The measured alternative ships as a control: with vstd's API called directly
//! the TCB is **five** items and **zero** of them touches the lifetime
//! property -- and the R4/R5 pair is then `differ` rather than `exact`, so under
//! this project's `identity` pin that configuration is not a rung. That is
//! TASK_055 §2.5's alarm in its true, measured form. ../NOTES.md 5 and 6.
//!
//! **The table is indexed CHECKED, in this rung and in unsafe.rs**, and that is
//! a measured decision rather than a concession: `h < ntab` and `ntab <= TABCAP`
//! together already delete rustc's bounds check on `tab[h]`, so a
//! `get_unchecked` accessor here would buy zero instructions and cost two
//! trusted items. ../NOTES.md 4 has the disassembly and the control.
//!
//! SAFETY (1): `off + len <= buf.len()` is the caller's structural
//!   precondition. Unchecked in unsafe.rs; discharged at the call site here.
//! SAFETY (2): `len >= 4` guards the window header.
//! SAFETY (3): the op is read only under `len - p >= 2` with `p <= len`.
//! SAFETY (4): **the record read `rec_read(tab[h])` happens only under
//!   `live[h] == 1`, and `live[h] == 1` implies the permission for slot `h` is
//!   still in the map.** That is the obligation p27 is about, and R1's bug is
//!   exactly a caller that cannot discharge it.
//! SAFETY (5): `deallocate` is called exactly once per record -- CLOSE clears
//!   `live[h]` and the epilogue only frees slots the array still calls alive --
//!   so there is no double free, and every slot alive at the end is freed, so
//!   there is no leak.

// Plain-Rust I/O helpers. Outside `verus!`, so Verus treats the whole module as
// external (external-by-default). Reached only through `load_input`/`emit`.
#[path = "../../common/driver.rs"]
mod driver;

use vstd::layout::valid_layout;
use vstd::map::*;
use vstd::prelude::*;
use vstd::raw_ptr::*;

verus! {

// `group_slice_axioms` gives `slice@.len() == spec_slice_len(slice)`, hence
// `slice@.len() <= usize::MAX` -- without it `off + len` cannot be shown not to
// overflow `usize`. `group_array_axioms` gives `tab@.len() == TABCAP` for a
// `[*mut u8; TABCAP]` and the fill axiom for `[null_mut(); TABCAP]`.
// `group_layout_axioms` + `align_of_u8` are what `into_typed::<u8>` needs;
// `align_of_u8` sits deliberately OUTSIDE the alignment group (`layout.rs:266`,
// "not part of the alignment broadcast group due to proof time-out") so the
// group alone is not enough. `group_raw_ptr_axioms` is what turns
// `ptr_mut_from_data(p@) == p` into a usable fact. `lemma_u128_shr_is_div` and
// `lemma_mul_inequality` are the DRIVER's, not the kernel's.
broadcast use {
    vstd::slice::group_slice_axioms,
    vstd::array::group_array_axioms,
    vstd::layout::group_layout_axioms,
    vstd::layout::align_of_u8,
    vstd::raw_ptr::group_raw_ptr_axioms,
    vstd::bits::lemma_u128_shr_is_div,
    vstd::arithmetic::mul::lemma_mul_inequality,
};

/// The handle table's extent, a compile-time constant in every rung.
pub const TABCAP: usize = 32;

/// One record, one allocation, `RECSZ` bytes. A record is one byte: the unit of
/// this pattern is the ALLOCATION, not the payload.
pub const RECSZ: usize = 1;

/// What a rejected operation folds instead of a record. A compile-time constant
/// in every rung.
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
/// `vals[j]` is slot `j`'s record value and `lv[j]` its liveness; `vals.len()`
/// is `ntab`, the number of slots ever opened. Note what this says and does not
/// say: it describes the PROGRAM -- open until the table is full, close only a
/// live slot, read only a live slot, fold SENT otherwise -- and it says nothing
/// about `nops` being honest or about the op stream being well formed. Every
/// adversarial input is inside this domain (`../spec.md`).
///
/// **`lv` is where the temporal property lives.** A READ folds `vals[h]` only
/// when `lv[h]`; a rung that folds it anyway is not this function.
pub open spec fn run(
    buf: Seq<u8>,
    off: int,
    len: int,
    o: int,
    nops: int,
    p: int,
    vals: Seq<u8>,
    lv: Seq<bool>,
    acc: u64,
) -> u64
    decreases nops - o,
{
    if o >= nops || len - p < 2 {
        acc.wrapping_mul(31).wrapping_add(vals.len() as u64)
    } else {
        let c = buf[off + p];
        let a = buf[off + p + 1];
        let h = a as int;
        if c % 4 == 0 {
            if vals.len() < TABCAP as int {
                run(
                    buf,
                    off,
                    len,
                    o + 1,
                    nops,
                    p + 2,
                    vals.push(a),
                    lv.push(true),
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
                    vals,
                    lv,
                    acc.wrapping_mul(31).wrapping_add(SENT),
                )
            }
        } else if c % 4 == 1 {
            if h < vals.len() && lv[h] {
                run(
                    buf,
                    off,
                    len,
                    o + 1,
                    nops,
                    p + 2,
                    vals,
                    lv.update(h, false),
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
                    vals,
                    lv,
                    acc.wrapping_mul(31).wrapping_add(SENT),
                )
            }
        } else {
            if h < vals.len() && lv[h] {
                run(
                    buf,
                    off,
                    len,
                    o + 1,
                    nops,
                    p + 2,
                    vals,
                    lv,
                    acc.wrapping_mul(31).wrapping_add(vals[h] as u64),
                )
            } else {
                run(
                    buf,
                    off,
                    len,
                    o + 1,
                    nops,
                    p + 2,
                    vals,
                    lv,
                    acc.wrapping_mul(31).wrapping_add(SENT),
                )
            }
        }
    }
}

/// What the kernel must return.
pub open spec fn op_fold(buf: Seq<u8>, off: int, len: int) -> u64 {
    if len < 4 {
        0
    } else if nops_at(buf, off) == 0 {
        0
    } else {
        run(buf, off, len, 0, nops_at(buf, off), 4, Seq::empty(), Seq::empty(), 0)
    }
}

/// THE TEMPORAL INVARIANT, one slot of it. `perms` and `dal` are the linear
/// resources; a slot the exec array calls alive has both, they name that slot's
/// pointer, and the byte behind the pointer is the value the abstract machine
/// says it is.
pub open spec fn slot_ok(
    tab: Seq<*mut u8>,
    vals: Seq<u8>,
    perms: Map<int, PointsTo<u8>>,
    dal: Map<int, Dealloc>,
    j: int,
) -> bool {
    &&& perms.dom().contains(j)
    &&& dal.dom().contains(j)
    &&& perms[j].ptr() == tab[j]
    &&& perms[j].is_init()
    &&& perms[j].value() == vals[j]
    &&& dal[j].addr() == tab[j].addr()
    &&& dal[j].size() == RECSZ
    &&& dal[j].align() == 1
    &&& dal[j].provenance() == tab[j]@.provenance
}

/// THE TEMPORAL INVARIANT. **This is the sentence R1 violates**: it says the
/// permission map's domain covers exactly the slots the liveness array calls
/// alive, so a read of a slot the array calls dead has nothing to present.
pub open spec fn wf(
    tab: Seq<*mut u8>,
    live: Seq<u8>,
    vals: Seq<u8>,
    lv: Seq<bool>,
    ntab: int,
    perms: Map<int, PointsTo<u8>>,
    dal: Map<int, Dealloc>,
) -> bool {
    &&& 0 <= ntab <= TABCAP
    &&& tab.len() == TABCAP
    &&& live.len() == TABCAP
    &&& vals.len() == ntab
    &&& lv.len() == ntab
    &&& forall|j: int| 0 <= j < ntab ==> ((#[trigger] lv[j]) <==> live[j] == 1u8)
    &&& forall|j: int| 0 <= j < ntab && lv[j] ==> #[trigger] slot_ok(tab, vals, perms, dal, j)
}

// ------------------------------------------------------------------- TCB ----
// TRUSTED ITEM 1 of 7. vstd ships no specification for `<[T]>::get_unchecked`,
// so this is the axiom that licenses the unchecked read of the window. It is
// sound because the standard library's documented contract for `get_unchecked`
// is exactly this: if the caller guarantees `i < v.len()`, the call is defined
// and yields `v[i]`. Identical, character for character, to the accessor p01,
// p02, p03, p05, p06, p07, p11, p12, p13, p14, p16 and p17 ship.
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

// TRUSTED ITEM 6 of 7. Argument parsing, file I/O and little-endian decoding,
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

// TRUSTED ITEM 7 of 7. `println!` is not verifiable; no `ensures`. Counted with
// the six above -- every `external_body` item is TCB, not just the interesting
// one (`.memory/04-verus.md`).
#[verifier::external_body]
fn emit(acc: u64) {
    driver::emit(acc);
}

// TRUSTED ITEM 2 of 7. The unchecked TABLE read, generic over the element type
// so that the pointer table and the liveness array share ONE axiom instead of
// two. vstd ships no specification for `<[T; N]>::get_unchecked`, and the
// standard library's documented contract is exactly this `requires`/`ensures`
// pair.
//
// **It is here because it is worth 41.70 Ir/call on `small`** -- the bound
// `h < ntab <= TABCAP` does NOT delete rustc's check on `tab[h]`, which an
// earlier draft of this pattern asserted without measuring. Three
// `panic_bounds_check` call sites survive in the checked kernel at `-O3`.
// ../NOTES.md 4.
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

// TRUSTED ITEM 3 of 7. The unchecked TABLE store, same shape. The `ensures` is a
// whole-sequence equality (`update`), not a statement about slot `i` alone, so
// it says both "slot `i` became `x`" and "nothing else moved".
//
// `x` is a pure VALUE parameter -- stored, never used as an address or a length
// -- so it has no precondition, and `../spec.md`'s `verus.unsafe_justifications`
// says so and the gate shouts it every run. `.memory/04-verus.md` names this
// false positive of the parameter-coverage rule; p03 was the first pattern to
// exercise it, p12 the second, p06 the third, p14 the fourth.
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

// TRUSTED ITEM 4 of 7, and **the one that is not what it looks like.** This is
// `vstd::raw_ptr::allocate` (`raw_ptr.rs:908`) -- its `requires`, its `ensures`
// and its body, character for character -- copied into this crate for ONE
// reason, which is codegen: vstd carries no `#[inline]` on `allocate`, so a
// rung that called it would emit a GOT-indirect cross-crate `call` that
// unsafe.rs cannot produce, and R4 and R5 would stop being the same machine
// code. Measured: with vstd's own `allocate` the pair is `differ` at both opt
// levels, and with this wrapper it is `exact`. ../NOTES.md 5 has the
// disassembly, and controls/ ships the vstd-pure rung so the claim is checkable.
//
// **Its verified twin is vstd's `allocate` itself** (below), so the gate proves
// that this contract is no stronger than the one vstd already discharges. That
// is what makes it a RELOCATION of trust rather than new trust
// (`.memory/04-verus.md`'s U-license / V-gap / infra vocabulary) -- and it is
// the honest form of TASK_055 §2.5's alarm: the zero-project-local-axiom
// configuration exists, and under this project's `identity` pin it is not a
// rung.
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
        pt.0@.provenance == pt.1@.provenance(),
    opens_invariants none
{
    allocate(size, align)
}

// TRUSTED ITEM 5 of 7, and THE REAL `free`. `vstd::raw_ptr::deallocate`
// (`raw_ptr.rs:948`), contract and body character for character, local for the
// same codegen reason as item 4, with vstd's own `deallocate` as its twin.
//
// **It CONSUMES the `PointsToRaw` and the `Dealloc`**, and that is the whole
// temporal argument: after this call the caller has no permission to present,
// so a later read of the same address is unprovable. A freelist push into a
// slab would consume nothing, the stale read would be in bounds of a live
// allocation, and the bug would be p17's LOGICAL class instead of this one.
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

// --------------------------------------------------------- the record ops ---
// **NOT trusted items.** `rec_open`, `rec_close` and `rec_read` are ordinary
// verified functions. Everything unchecked they do happens either inside vstd
// -- `ptr_ref` and `ptr_mut_write` are `external_body` there, `into_typed`,
// `into_raw` and `leak_contents` are vstd `axiom fn`s -- or inside items 4 and
// 5, whose twins are vstd's own allocation API.
//
// They are free functions rather than inline expressions because unsafe.rs has
// to be byte-identical to this file, and its own `rec_*` are the same three
// bodies with the permissions deleted (../NOTES.md 5).
#[inline(always)]
fn rec_open(v: u8) -> (r: (*mut u8, Tracked<PointsTo<u8>>, Tracked<Dealloc>))
    ensures
        r.1@.ptr() == r.0,
        r.1@.is_init(),
        r.1@.value() == v,
        r.2@.addr() == r.0.addr(),
        r.2@.size() == RECSZ,
        r.2@.align() == 1,
        r.2@.provenance() == r.0@.provenance,
{
    assert(valid_layout(RECSZ, 1));
    let (base, Tracked(raw), Tracked(dealloc)) = rec_alloc(RECSZ, 1);
    let tracked mut pt = raw.into_typed::<u8>(base.addr());
    assert(pt.ptr() == base);
    ptr_mut_write(base, Tracked(&mut pt), v);
    (base, Tracked(pt), Tracked(dealloc))
}

// THE REAL `free`. `deallocate` CONSUMES the `PointsToRaw` and the `Dealloc`,
// which is what makes a later read of the same slot unprovable rather than
// merely wrong. A freelist push into a slab would not: the stale read would be
// in bounds of a live allocation, `PointsTo` would license it, and the bug
// would be p17's LOGICAL class rather than this one (../spec.md, TASK_055 §2.8).
#[inline(always)]
fn rec_close(p: *mut u8, Tracked(pt): Tracked<PointsTo<u8>>, Tracked(dl): Tracked<Dealloc>)
    requires
        pt.ptr() == p,
        dl.addr() == p.addr(),
        dl.size() == RECSZ,
        dl.align() == 1,
        dl.provenance() == p@.provenance,
{
    let tracked mut q = pt;
    proof {
        q.leak_contents();
    }
    let tracked raw = q.into_raw();
    rec_free(p, RECSZ, 1, Tracked(raw), Tracked(dl));
}

#[inline(always)]
fn rec_read(p: *mut u8, Tracked(pt): Tracked<&PointsTo<u8>>) -> (r: u8)
    requires
        pt.ptr() == p,
        pt.is_init(),
    ensures
        r == pt.value(),
{
    *ptr_ref(p, Tracked(pt))
}

// ---------------------------------------------------------------- kernel ----
// Same exec code as unsafe.rs. Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> (r: u64)
    requires
        off + len <= buf@.len(),
    ensures
        r == op_fold(buf@, off as int, len as int),
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
    let mut tab: [*mut u8; TABCAP] = [core::ptr::null_mut(); TABCAP];
    let mut live: [u8; TABCAP] = [0u8; TABCAP];
    let tracked mut perms = Map::<int, PointsTo<u8>>::tracked_empty();
    let tracked mut dal = Map::<int, Dealloc>::tracked_empty();
    let ghost mut vals: Seq<u8> = Seq::empty();
    let ghost mut lv: Seq<bool> = Seq::empty();
    let mut ntab: usize = 0;
    let mut acc: u64 = 0;
    let mut p: usize = 4;
    let mut o: usize = 0;
    // "The operations from here, with the table we have built, are all the
    // operations." p14's and p06's relational shape. This loop exits TWO ways
    // (`o == nops` and the window-exhausted break), so it needs
    // `invariant_except_break` plus a loop `ensures`.
    while o < nops
        invariant_except_break
            o <= nops,
            p <= len,
            off + len <= buf@.len(),
            buf@.len() <= usize::MAX,
            wf(tab@, live@, vals, lv, ntab as int, perms, dal),
            run(buf@, off as int, len as int, o as int, nops as int, p as int, vals, lv, acc)
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
            wf(tab@, live@, vals, lv, ntab as int, perms, dal),
            acc.wrapping_mul(31).wrapping_add(ntab as u64) == run(
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
        let h: usize = a as usize;
        if c % 4 == 0 {
            if ntab < TABCAP {
                let ghost tab0 = tab@;
                let ghost perms0 = perms;
                let ghost dal0 = dal;
                let ghost vals0 = vals;
                let ghost n0 = ntab as int;
                let (q, Tracked(pt), Tracked(dd)) = rec_open(a);
                proof {
                    perms.tracked_insert(n0, pt);
                    dal.tracked_insert(n0, dd);
                    vals = vals.push(a);
                    lv = lv.push(true);
                }
                arr_set_unchecked(&mut tab, ntab, q);
                arr_set_unchecked(&mut live, ntab, 1u8);
                ntab = ntab + 1;
                proof {
                    assert forall|j: int| 0 <= j < ntab as int && lv[j] implies slot_ok(
                        tab@,
                        vals,
                        perms,
                        dal,
                        j,
                    ) by {
                        if j < n0 {
                            assert(lv[j]);
                            assert(slot_ok(tab0, vals0, perms0, dal0, j));
                        }
                    }
                }
                acc = acc.wrapping_mul(31).wrapping_add(a as u64);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else if c % 4 == 1 {
            if h < ntab && arr_get_unchecked(&live, h) == 1u8 {
                assert(lv[h as int]);
                assert(slot_ok(tab@, vals, perms, dal, h as int));
                let ghost tab0 = tab@;
                let ghost perms0 = perms;
                let ghost dal0 = dal;
                let tracked pt = perms.tracked_remove(h as int);
                let tracked dd = dal.tracked_remove(h as int);
                rec_close(arr_get_unchecked(&tab, h), Tracked(pt), Tracked(dd));
                // THE LINE THE C RUNG FORGOT. Without it the invariant below
                // cannot be re-established: `deallocate` has consumed slot
                // `h`'s permission and `live[h]` would still claim it exists.
                arr_set_unchecked(&mut live, h, 0u8);
                proof {
                    lv = lv.update(h as int, false);
                    assert forall|j: int| 0 <= j < ntab as int && lv[j] implies slot_ok(
                        tab@,
                        vals,
                        perms,
                        dal,
                        j,
                    ) by {
                        assert(j != h as int);
                        assert(slot_ok(tab0, vals, perms0, dal0, j));
                    }
                }
                acc = acc.wrapping_mul(31).wrapping_add(1);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else {
            // THE SAFETY LINE, and c/kernel.c omits exactly the second
            // conjunct. Here it is not merely a test: `live[h] == 1u8` is what
            // the invariant converts into `perms.dom().contains(h)`, and
            // `tracked_borrow` cannot be called without it.
            if h < ntab && arr_get_unchecked(&live, h) == 1u8 {
                assert(lv[h as int]);
                assert(slot_ok(tab@, vals, perms, dal, h as int));
                let tracked t = perms.tracked_borrow(h as int);
                let v: u8 = rec_read(arr_get_unchecked(&tab, h), Tracked(t));
                acc = acc.wrapping_mul(31).wrapping_add(v as u64);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        }
        o = o + 1;
    }
    // ------- the epilogue: free every record still alive -------------------
    // R2 and R3 do not have this loop: dropping the table IS this loop, written
    // by the language. That is the pattern's headline and ../NOTES.md 3 prices
    // it.
    let mut j: usize = 0;
    while j < ntab
        invariant
            j <= ntab,
            wf(tab@, live@, vals, lv, ntab as int, perms, dal),
        decreases ntab - j,
    {
        if arr_get_unchecked(&live, j) == 1u8 {
            assert(lv[j as int]);
            assert(slot_ok(tab@, vals, perms, dal, j as int));
            let ghost tab0 = tab@;
            let ghost perms0 = perms;
            let ghost dal0 = dal;
            let tracked pt = perms.tracked_remove(j as int);
            let tracked dd = dal.tracked_remove(j as int);
            rec_close(arr_get_unchecked(&tab, j), Tracked(pt), Tracked(dd));
            arr_set_unchecked(&mut live, j, 0u8);
            proof {
                lv = lv.update(j as int, false);
                assert forall|k: int| 0 <= k < ntab as int && lv[k] implies slot_ok(
                    tab@,
                    vals,
                    perms,
                    dal,
                    k,
                ) by {
                    assert(k != j as int);
                    assert(slot_ok(tab0, vals, perms0, dal0, k));
                }
            }
        }
        j = j + 1;
    }
    acc.wrapping_mul(31).wrapping_add(ntab as u64)
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
            assert(r == op_fold(buf@, (k * stride) as int, stride as int));
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    emit(acc);
}

} // verus!
