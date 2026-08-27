//! p42 rung R5 -- unsafe + Verus proof.
//!
//! R4's exec code verbatim, plus the specs and proofs that discharge every
//! unsafe precondition: the slice reads, the allocation's layout, the address
//! of every digest byte, the initialisation of every byte read back, and the
//! legality of the final `dealloc`.
//!
//! ⚠⚠ **AND, SINCE TASK_110, THE PROPERTY THE ROW IS ACTUALLY ABOUT -- WHICH
//! THIS COMMENT USED TO SAY WAS IMPOSSIBLE. READ THIS BEFORE QUOTING THE ROW.**
//! Until TASK_110 this paragraph said *"the proof rung of this ladder cannot
//! state the property the row prices"*, and that claim is RETRACTED: TASK_109
//! §A built a counterexample on this very file and TASK_110 shipped it. What is
//! true is narrower and better.
//!
//! `vstd::raw_ptr` models the *permission* to release -- `Tracked<Dealloc>` --
//! and that permission is **AFFINE at the pinned Verus, not linear**: a proof
//! may simply DROP it. So an R5 that holds the token BARE and forgets the error
//! path's `dig_free` still reports `0 errors`. Measured, with a control that
//! fires, and the control is committed: `controls/affine_leak.rs`, `2 verified,
//! 0 errors` for the leaking arm and `error[E0382]: use of moved value` for the
//! must-fail arm, i.e. the tokens are move-only and the probe is not vacuous.
//! Move-only plus droppable is exactly affine.
//!
//! **What a proof cannot drop is a MAP whose contents a postcondition names.**
//! So this rung never holds a bare `Tracked<Dealloc>`: `led_alloc` escrows it,
//! `led_free` withdraws it, and `kbody` ensures the ledger comes back EMPTY on
//! every exit -- including the early `return 0` that is p42's whole subject.
//! The price is **+3 obligations (15 -> 18), zero new trusted items and zero
//! instructions**: neither wrapper is `external_body` and neither contains
//! `unsafe`, so `check.py::_is_trusted` leaves both out, and the `identity` pin
//! still reads `exact` against R4. ../NOTES.md 6.
//!
//! ⚠ **The residual trust, named rather than left implicit:** the obligation
//! binds allocations that go through `led_alloc`. A direct call to `dig_alloc`
//! still drops its token silently. That is a MODULE-LEVEL DISCIPLINE, not a
//! global guarantee. ⚠ **And the clean negative beside it, so nobody re-runs
//! the search:** there is NO linear / must-consume / no-drop tracked mode at
//! the pinned Verus -- **22** distinct `verifier::` attribute names in the
//! pinned `rust_verify`'s string table and none of them is one (the only match
//! for "linear" is `verifier::nonlinear`), and `grep -rn affine
//! ~/tools/verus/vstd/` is 0 hits. ⚠ TASK_109 A1 put that count at 23;
//! recounted at TASK_110 with `sort -u`, it is 22, and the conclusion is
//! unchanged. ../NOTES.md 6d.
//!
//! Nothing here is an `assume`.
//!
//! Two more things this rung is, for the usual reasons:
//!   * `main` is *inside* `verus!` and is *not* `external_body`, so the call
//!     `kernel(vs, off, win_len)` is a real verified call site and its
//!     `requires` is genuinely discharged (`.memory/02-bench-rules.md` rule 2);
//!   * the contract is total on VALUES -- there is no `requires` on the array
//!     contents, so every measured input is inside the verified domain by
//!     construction, `adversarial-*` included (rules 1 and 3).
//!
//! ⚠ **The driver's `win_len_w <= P42_MAXWIN` conjunct is load-bearing and is
//! this rung's doing**, disclosed rather than buried: `vstd::layout::
//! valid_layout(size, 1)` is `size <= isize::MAX`, and the pinned vstd
//! axiomatises NO bound on a slice's length beyond `usize::MAX` -- `grep -rn
//! 'isize::MAX' ~/tools/verus/vstd/` finds it only inside `layout.rs` itself.
//! So the ceiling has to come from the driver, and it is p17's route: a
//! conjunct every rung carries, outside the measured loop, costing nothing per
//! call. It is also the check a C program that allocates from an untrusted
//! header owes anyway.
//!
//! TCB tally: ../NOTES.md 7. Five `external_body` items, three of them trusted
//! by `check.py::_is_trusted`, each with a verified twin. The ledger adds
//! neither: `led_alloc` and `led_free` are ordinary verified functions.

use vstd::prelude::*;
use vstd::layout::valid_layout;
use vstd::map::Map;
use vstd::raw_ptr::{allocate, deallocate, ptr_mut_from_data, ptr_mut_write, ptr_ref, Dealloc,
                    PointsTo, PointsToRaw, Provenance, PtrData};
use vstd::set::Set;
use vstd::set_lib::set_int_range;

// Plain-Rust I/O helpers. Outside `verus!`, so Verus treats the whole module as
// external (external-by-default). Reached only through `load_input`/`emit`.
#[path = "../../common/driver.rs"]
mod driver;

verus! {

// `group_slice_axioms` gives `slice@.len() == spec_slice_len(slice)`, hence
// `slice@.len() <= usize::MAX`. `group_layout_axioms` + `align_of_u8` are what
// `valid_layout(len, 1)` and `into_typed::<u8>` need. `group_raw_ptr_axioms`
// turns `ptr_mut_from_data(p@) == p` into a usable fact. `group_map_lemmas` and
// `group_set_lemmas` are for the digest's permission map and its domain.
// `lemma_u128_shr_is_div` is the DRIVER's, not the kernel's.
broadcast use {
    vstd::slice::group_slice_axioms,
    vstd::layout::group_layout_axioms,
    vstd::layout::align_of_u8,
    vstd::raw_ptr::group_raw_ptr_axioms,
    vstd::map::group_map_lemmas,
    vstd::set::group_set_lemmas,
    vstd::bits::lemma_u128_shr_is_div,
};

/// The low byte of a well-formed record header. ../spec.md "Payload layout".
pub const TAG: u64 = 0xA7;
/// The decode constant. Arbitrary and shared by all six rungs.
pub const MIX: u64 = 0x9E37_79B9_7F4A_7C15;
/// The driver's ceiling on the window length. See the module comment.
pub const MAXWIN: u64 = 65536;

// ------------------------------------------------------------------ spec ----
/// The wrapping sum of `(v[off] ^ MIX) .. (v[off+n-1] ^ MIX)`.
pub open spec fn scan(v: Seq<u64>, off: int, n: int) -> u64
    decreases n,
{
    if n <= 0 {
        0u64
    } else {
        scan(v, off, n - 1).wrapping_add(v[off + n - 1] ^ MIX)
    }
}

/// Digest byte `i`: bits 24..31 of the running sum after `i+1` elements. The
/// SHIFT is load-bearing -- bits 0..7 of a wrapping sum depend only on bits
/// 0..7 of the inputs, and those carry the constant record tag, so a digest
/// taken from the low byte would not read the payload at all (../NOTES.md 4).
pub open spec fn digb(v: Seq<u64>, off: int, i: int) -> u8 {
    (scan(v, off, i + 1) >> 24) as u8
}

/// The digest folded BACKWARDS: `dig[len-1]`, then `dig[len-2]`, and so on for
/// `k` bytes. This is the reason the digest has to be materialised at all: the
/// last byte is needed first, and it is a function of every element before it.
pub open spec fn rfold(v: Seq<u64>, off: int, len: int, k: int) -> u64
    decreases k,
{
    if k <= 0 {
        0u64
    } else {
        rfold(v, off, len, k - 1).wrapping_mul(31).wrapping_add(digb(v, off, len - k) as u64)
    }
}

/// What all six rungs compute. The tag test is IN the specification, because it
/// is in every rung: a malformed window is 0, and the difference between the
/// rungs is what happens to the digest buffer on the way out.
pub open spec fn kspec(v: Seq<u64>, off: int, len: int) -> u64 {
    if v[off] & 0xff != TAG {
        0u64
    } else {
        rfold(v, off, len, len)
    }
}

/// Slot `j` of the digest: a live, initialised `PointsTo<u8>` at `base + j`
/// holding `digb(v, off, j)`. The permission map's well-formedness.
pub open spec fn slot_ok(
    perms: Map<int, PointsTo<u8>>,
    base: usize,
    prov: Provenance,
    v: Seq<u64>,
    off: int,
    j: int,
) -> bool {
    &&& perms.dom().contains(j)
    &&& perms[j].ptr() == ptr_mut_from_data::<u8>(
        PtrData { addr: (base + j) as usize, provenance: prov, metadata: () },
    )
    &&& perms[j].is_init()
    &&& perms[j].value() == digb(v, off, j)
}

// ------------------------------------------------------------------- TCB ----
// TRUSTED ITEM 1 of 5. vstd ships no specification for `<[T]>::get_unchecked`
// (`grep -rn get_unchecked ~/tools/verus/vstd/` -> 0 hits), so this is the
// axiom that licenses the unsafe read. Sound because the standard library's
// documented contract for `get_unchecked` is exactly this.
#[inline(always)]
#[verifier::external_body]
fn v_get_unchecked(v: &[u64], i: usize) -> (r: u64)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    unsafe { *v.get_unchecked(i) }
}

// THE VERIFIED TWIN of trusted item 1. Same contract, checked code: a
// `requires` too weak to license `*v.get_unchecked(i)` is too weak to license
// `v[i]`, and Verus can see the second one.
#[cfg(slb_twin)]
fn slb_twin_v_get_unchecked(v: &[u64], i: usize) -> (r: u64)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    v[i]
}

// TRUSTED ITEM 2 of 5. `vstd::raw_ptr::allocate` (raw_ptr.rs:908) -- vstd's
// `requires` verbatim, FOUR of vstd's FIVE `ensures`, and vstd's body with
// `alloc::alloc::` respelled `std::alloc::` -- copied into this crate for ONE
// reason, which is
// codegen: vstd carries no `#[inline]` on `allocate`, so calling vstd's leaves
// a real call in this crate's object code where R4's `#[inline(always)]`
// helper has none, and the `identity` pin drops. p27 measured exactly that
// (`patterns/p27-handle-table/verus.rs`, trusted item 4). Its verified twin is
// vstd's own `allocate`, so the gate re-derives every clause here against the
// upstream one it was copied from.
//
// ⚠ The dropped clause is vstd's `pt.0.addr() as int % align as int == 0`, and
// it is dropped because the gate MEASURED that nothing depends on it: p42
// allocates with `align == 1`, `into_typed::<u8>` needs
// `start % align_of::<u8>() == 0`, and `align_of::<u8>() == 1`, so the clause is
// discharged by an axiom rather than by this item. Stage 5c deletes each
// `ensures` conjunct in turn and requires the file to FAIL; this one still
// verified clean -- `15 verified, 0 errors` at TASK_104, ⚠ which was the base
// count THEN and is 18 since TASK_110's ledger, so read it as "no error", not
// as a current figure. It was a trusted claim carried for free. ✅ The four
// conjuncts that DID survive are load-bearing on the current tree and the gate
// re-derives it every run: each gives `17 verified, 1 errors` against a base of
// 18. Every difference from vstd is a WEAKENING or a respelling, never a
// strengthening.
#[inline(always)]
#[verifier::external_body]
fn dig_alloc(size: usize, align: usize) -> (pt: (
    *mut u8,
    Tracked<PointsToRaw>,
    Tracked<Dealloc>,
))
    requires
        valid_layout(size, align),
        size != 0,
    ensures
        pt.1@.is_range(pt.0.addr() as int, size as int),
        pt.0.addr() + size <= usize::MAX + 1,
        pt.2@@ == (vstd::raw_ptr::DeallocData {
            addr: pt.0.addr(),
            size: size as nat,
            align: align as nat,
            provenance: pt.1@.provenance(),
        }),
        pt.0@.provenance == pt.1@.provenance(),
    opens_invariants none
{
    let layout = unsafe { std::alloc::Layout::from_size_align_unchecked(size, align) };
    let p = unsafe { std::alloc::alloc(layout) };
    if p == core::ptr::null_mut() {
        std::process::abort();
    }
    (p, Tracked::assume_new(), Tracked::assume_new())
}

// THE VERIFIED TWIN of trusted item 2, and it is vstd's own `allocate`.
#[cfg(slb_twin)]
fn slb_twin_dig_alloc(size: usize, align: usize) -> (pt: (
    *mut u8,
    Tracked<PointsToRaw>,
    Tracked<Dealloc>,
))
    requires
        valid_layout(size, align),
        size != 0,
    ensures
        pt.1@.is_range(pt.0.addr() as int, size as int),
        pt.0.addr() + size <= usize::MAX + 1,
        pt.2@@ == (vstd::raw_ptr::DeallocData {
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

// TRUSTED ITEM 3 of 5, and THE REAL `free`. `vstd::raw_ptr::deallocate`
// (raw_ptr.rs:948), same `requires`, same body with `std::alloc::` for
// `::alloc::alloc::`. It CONSUMES the `PointsToRaw` and the `Dealloc`, which is
// what makes a use-after-free unstateable here. ⚠ Consuming is NOT the same as
// being obliged to consume, so this item's contract still says nothing about
// whether the release HAPPENS -- what says that is `led_free`'s caller-side
// obligation and `kbody`'s postcondition, one level up, at zero cost to this
// item's trusted text. See the module comment.
//
// ⚠ It is a REAL `free` rather than a freelist push. ../spec.md pins that:
// pushing the block onto a pattern-local freelist would leave the "leaked"
// block inside a live allocation, LeakSanitizer would see nothing, and the row
// would be measuring bookkeeping instead of memory.
#[inline(always)]
#[verifier::external_body]
fn dig_free(
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
    let layout = unsafe { std::alloc::Layout::from_size_align_unchecked(size, align) };
    unsafe {
        std::alloc::dealloc(p, layout);
    }
}

// THE VERIFIED TWIN of trusted item 3, and it is vstd's own `deallocate`.
#[cfg(slb_twin)]
fn slb_twin_dig_free(
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

// TRUSTED ITEM 4 of 5. Argument parsing, file I/O and little-endian decoding,
// delegated to common/driver.rs so that all six rungs read the file the same
// way. It states **no** `ensures` at all, deliberately: an `ensures` here would
// be an axiom about the contents of a file, which nothing can justify.
#[verifier::external_body]
fn load_input() -> (r: (u64, u64, Vec<u64>)) {
    let path = driver::arg_path();
    let inp = driver::load(&path);
    let (win_len_w, vals) = driver::head_u64_body(&inp);
    (inp.n_iters, win_len_w, vals)
}

// TRUSTED ITEM 5 of 5. `println!` is not verifiable; no `ensures`.
#[verifier::external_body]
fn emit(acc: u64) {
    driver::emit(acc);
}

// --------------------------------------------------------- verified helpers -
// Not trusted: no `external_body`, no `unsafe`. `with_addr` and `addr` are
// specified by the pinned vstd (`raw_ptr.rs`'s `pointer_specs!` macro), and
// `<*mut T>::add` is NOT -- which is why every rung spells the digest address
// this way. See ../NOTES.md 9 for the measured cost of that constraint.
#[inline(always)]
fn dig_at(p: *mut u8, base: usize, i: usize) -> (q: *mut u8)
    requires
        p.addr() == base,
        base + i <= usize::MAX,
    ensures
        q == ptr_mut_from_data::<u8>(
            PtrData { addr: (base + i) as usize, provenance: p@.provenance, metadata: () },
        ),
{
    p.with_addr(base + i)
}

#[inline(always)]
fn dig_write(q: *mut u8, Tracked(pt): Tracked<&mut PointsTo<u8>>, b: u8)
    requires
        old(pt).ptr() == q,
    ensures
        final(pt).ptr() == q,
        final(pt).is_init(),
        final(pt).value() == b,
{
    ptr_mut_write(q, Tracked(pt), b)
}

#[inline(always)]
fn dig_read(q: *mut u8, Tracked(pt): Tracked<&PointsTo<u8>>) -> (b: u8)
    requires
        pt.ptr() == q,
        pt.is_init(),
    ensures
        b == pt.value(),
{
    *ptr_ref(q, Tracked(pt))
}

// ------------------------------------------------------------- ledger ------
// THE LEAK-FREEDOM OBLIGATION, and it is the reason this rung covers p42's own
// bug class. ⚠ **Neither of these two items is trusted**: no `external_body`,
// no `unsafe`, so `check.py::_is_trusted` leaves both out and the TCB stays at
// five items. They are ordinary verified wrappers over this file's own
// `dig_alloc`/`dig_free`.
//
// The encoding: never hold a bare `Tracked<Dealloc>`. `led_alloc` ESCROWS the
// token into a tracked map; `led_free` withdraws it and spends it; and `kbody`
// below `ensures` the map's domain comes back EMPTY, which Verus checks on
// every exit, the early `return 0` included. Dropping a `Dealloc` is legal --
// it is affine, `controls/affine_leak.rs` -- but dropping the MAP that holds it
// is not, because the postcondition names the map's domain.
//
// ⚠ **Key by a ghost `int`, NOT by the address.** `dig_alloc` promises nothing
// about the returned address being absent from the ledger, so
// `dom.insert(a).remove(a) =~= dom` is unprovable and the postcondition fails
// on BOTH exits. A ghost key with `!old(led).dom().contains(k)` is discharged
// by the caller for free. This was measured, both ways, at TASK_109.
//
// ⚠ **What this does NOT buy, and it is the honest limit:** the obligation
// binds allocations that go through `led_alloc`. A direct call to `dig_alloc`
// -- or to `vstd::raw_ptr::allocate` -- still drops its token silently. That is
// a MODULE-LEVEL DISCIPLINE, not a global guarantee. ../NOTES.md 6.
pub type Ledger = Map<int, Dealloc>;

#[inline(always)]
fn led_alloc(size: usize, align: usize, Ghost(k): Ghost<int>, Tracked(led): Tracked<&mut Ledger>) -> (r: (
    *mut u8,
    Tracked<PointsToRaw>,
))
    requires
        valid_layout(size, align),
        size != 0,
        !old(led).dom().contains(k),
    ensures
        r.1@.is_range(r.0.addr() as int, size as int),
        r.0.addr() + size <= usize::MAX + 1,
        r.0@.provenance == r.1@.provenance(),
        final(led).dom() =~= old(led).dom().insert(k),
        final(led)[k]@ == (vstd::raw_ptr::DeallocData {
            addr: r.0.addr(),
            size: size as nat,
            align: align as nat,
            provenance: r.1@.provenance(),
        }),
{
    let (p, Tracked(pt), Tracked(dl)) = dig_alloc(size, align);
    proof {
        led.tracked_insert(k, dl);
    }
    (p, Tracked(pt))
}

#[inline(always)]
fn led_free(
    p: *mut u8,
    size: usize,
    align: usize,
    Tracked(pt): Tracked<PointsToRaw>,
    Ghost(k): Ghost<int>,
    Tracked(led): Tracked<&mut Ledger>,
)
    requires
        old(led).dom().contains(k),
        old(led)[k]@ == (vstd::raw_ptr::DeallocData {
            addr: p.addr(),
            size: size as nat,
            align: align as nat,
            provenance: pt.provenance(),
        }),
        pt.is_range(p.addr() as int, size as int),
        p@.provenance == pt.provenance(),
    ensures
        final(led).dom() =~= old(led).dom().remove(k),
{
    let tracked dl;
    proof {
        dl = led.tracked_remove(k);
    }
    dig_free(p, size, align, Tracked(pt), Tracked(dl));
}

// ---------------------------------------------------------------- kernel ----
// Same exec code as unsafe.rs. Contract: ../spec.md.
//
// ⚠ **The pinned signature does not move, and that is deliberate**: the ledger
// is a LOCAL of `kernel` and the obligation is pushed onto the
// `#[inline(always)]` `kbody` below. `spec.md`'s `kernel` string, its
// `driver.canonical` token sequence and the four other rungs are untouched.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(v: &[u64], off: usize, len: usize) -> (r: u64)
    requires
        off + len <= v@.len(),
        1 <= len <= isize::MAX,
    ensures
        r == kspec(v@, off as int, len as int),
{
    let tracked mut led: Ledger = Map::tracked_empty();
    kbody(v, off, len, Tracked(&mut led))
}

#[inline(always)]
fn kbody(v: &[u64], off: usize, len: usize, Tracked(led): Tracked<&mut Ledger>) -> (r: u64)
    requires
        off + len <= v@.len(),
        1 <= len <= isize::MAX,
        old(led).dom() =~= Set::<int>::empty(),
    ensures
        r == kspec(v@, off as int, len as int),
        // ⚠ THE LEAK-FREEDOM OBLIGATION. Checked on EVERY exit, including the
        // early `return 0` on the error path -- which is the path the C rung
        // gets wrong. Delete either `led_free` below and this clause fails,
        // naming the exit: `controls/ledger_leak.py`, the arm that must fire.
        final(led).dom() =~= Set::<int>::empty(),
{
    // Ghost only: mentioning `spec_slice_len` fires vstd's `axiom_spec_len`,
    // which is what tells the SMT solver a slice length fits in a `usize`.
    assert(v@.len() == vstd::slice::spec_slice_len(v));
    assert(valid_layout(len, 1));
    let (p, Tracked(raw)) = led_alloc(len, 1, Ghost(0int), Tracked(&mut *led));
    let base: usize = p.addr();
    let ghost prov = raw.provenance();

    if v_get_unchecked(v, off) & 0xff != TAG {
        // THE ERROR PATH. The release here is hand-written, exactly as R4's is
        // and exactly as the C rung's is missing -- and, since TASK_110, it is
        // also the one Verus CHECKS IS PRESENT: withdrawing the escrowed token
        // is the only way to empty the ledger this exit's postcondition names.
        led_free(p, len, 1, Tracked(raw), Ghost(0int), Tracked(&mut *led));
        return 0;
    }

    let tracked mut rest: PointsToRaw = raw;
    let tracked mut perms: Map<int, PointsTo<u8>> = Map::tracked_empty();
    let mut run: u64 = 0;
    let mut i: usize = 0;
    while i < len
        invariant
            0 <= i <= len,
            off + len <= v@.len(),
            v@.len() <= usize::MAX,
            p.addr() == base,
            p@.provenance == prov,
            base + len <= usize::MAX + 1,
            rest.provenance() == prov,
            rest.is_range(base + i, len - i),
            perms.dom() =~= set_int_range(0, i as int),
            forall|j: int| 0 <= j < i ==> #[trigger] slot_ok(perms, base, prov, v@, off as int, j),
            run == scan(v@, off as int, i as int),
        decreases len - i,
    {
        let q: *mut u8 = dig_at(p, base, i);
        let tracked mut pt: PointsTo<u8>;
        proof {
            let tracked (a, b) = rest.split(set_int_range(base + i, base + i + 1));
            rest = b;
            pt = a.into_typed::<u8>((base + i) as usize);
        }
        run = run.wrapping_add(v_get_unchecked(v, off + i) ^ MIX);
        let b: u8 = (run >> 24) as u8;
        dig_write(q, Tracked(&mut pt), b);
        let ghost perms0 = perms;
        proof {
            perms.tracked_insert(i as int, pt);
            assert(perms.dom() =~= set_int_range(0, i + 1));
            assert forall|t: int| 0 <= t < i + 1 implies #[trigger] slot_ok(
                perms,
                base,
                prov,
                v@,
                off as int,
                t,
            ) by {
                if t < i as int {
                    assert(slot_ok(perms0, base, prov, v@, off as int, t));
                    assert(perms[t] == perms0[t]);
                }
            }
        }
        i = i + 1;
    }

    // THE FOLD, as a do-while over a DESCENDING CURSOR. `j` is ghost; the only
    // exec induction variable is `q` itself, which is why this shape is cheaper
    // than the index fold it replaced (../NOTES.md 11b). It never forms the
    // one-past-the-end pointer, which is the reason the `r4_endptr` spelling is
    // inadmissible: `dig_alloc` ensures only `addr + size <= usize::MAX + 1`,
    // so `dig_at(p, base, len)`'s `base + i <= usize::MAX` is unprovable
    // (../NOTES.md 9). Four operations, all specified at the pinned vstd:
    // `with_addr`, `addr`, `ptr_ref` and `<*mut T as PartialEq>::eq`
    // (`~/tools/verus/vstd/raw_ptr.rs`, `pointer_specs!`).
    let mut acc: u64 = 0;
    let mut q: *mut u8 = dig_at(p, base, len - 1);
    let ghost mut j: int = 0;
    loop
        invariant_except_break
            j < len,
            q == ptr_mut_from_data::<u8>(
                PtrData { addr: (base + (len - 1 - j)) as usize, provenance: prov, metadata: () },
            ),
        invariant
            0 <= j <= len,
            p.addr() == base,
            p@.provenance == prov,
            base + len <= usize::MAX + 1,
            rest.provenance() == prov,
            rest.is_range(base + (len - j), j),
            perms.dom() =~= set_int_range(0, len - j),
            forall|t: int|
                0 <= t < len - j ==> #[trigger] slot_ok(perms, base, prov, v@, off as int, t),
            acc == rfold(v@, off as int, len as int, j),
        ensures
            rest.provenance() == prov,
            rest.is_range(base as int, len as int),
            acc == rfold(v@, off as int, len as int, len as int),
        decreases len - j,
    {
        let ghost idx: int = len - 1 - j;
        let ghost perms0 = perms;
        assert(slot_ok(perms, base, prov, v@, off as int, idx));
        let tracked mut pt: PointsTo<u8> = perms.tracked_remove(idx);
        acc = acc.wrapping_mul(31).wrapping_add(dig_read(q, Tracked(&pt)) as u64);
        proof {
            j = j + 1;
            assert(perms.dom() =~= set_int_range(0, idx));
            assert forall|t: int| 0 <= t < idx implies #[trigger] slot_ok(
                perms,
                base,
                prov,
                v@,
                off as int,
                t,
            ) by {
                assert(slot_ok(perms0, base, prov, v@, off as int, t));
                assert(perms[t] == perms0[t]);
            }
            assert(pt.ptr()@.provenance == prov);
            pt.leak_contents();
            let tracked r2 = pt.into_raw();
            assert(r2.provenance() == prov);
            let tracked joined = r2.join(rest);
            assert(joined.dom() =~= set_int_range(base + idx, base + len));
            rest = joined;
        }
        // The loop leaves through the base of the allocation, never past its
        // end. `<*mut T as PartialEq>::eq` ensures `res <==> addr and metadata
        // agree`, which is what turns this exec test into the ghost `j == len`.
        if q == p {
            proof {
                assert(q@.addr == p@.addr);
                assert(j == len);
            }
            break;
        }
        q = q.with_addr(q.addr() - 1);
    }

    led_free(p, len, 1, Tracked(rest), Ghost(0int), Tracked(&mut *led));
    acc
}

// ---------------------------------------------------------------- driver ----
fn main() {
    let (n_iters, win_len_w, vals) = load_input();
    // SLB-DRIVER-BEGIN
    let n_vals: usize = vals.len();
    let vs: &[u64] = vals.as_slice();
    let mut acc: u64 = 0;
    if win_len_w > 0 && win_len_w <= MAXWIN && win_len_w <= n_vals as u64 {
        let win_len: usize = win_len_w as usize;
        let nwin: u64 = (n_vals - win_len + 1) as u64;
        let mut it: u64 = 0;
        while it < n_iters
            invariant
                1 <= win_len <= n_vals,
                win_len <= MAXWIN,
                vs@.len() == n_vals,
                nwin == n_vals - win_len + 1,
            decreases n_iters - it,
        {
            // Ghost only, and the reason the barrier could be a multiply-shift
            // rather than a `%`: `off` must still be in range.
            // `(acc * nwin) >> 64 < nwin` because `acc <= u64::MAX` implies
            // `acc * nwin < nwin * 2^64`. Both steps are nonlinear, so Z3 needs
            // them spelled out. Erases at compile time -- R4 and R5 stay
            // byte-identical.
            proof {
                let p: int = (acc as int) * (nwin as int);
                assert((acc as u128) * (nwin as u128) <= (u64::MAX as u128) * (u64::MAX as u128))
                    by (nonlinear_arith)
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
            let off: usize = ((acc as u128 * nwin as u128) >> 64) as usize;
            let r: u64 = kernel(vs, off, win_len);
            // Ghost only: this is what *consumes* the kernel's `ensures`.
            // Without it the postcondition is decoration.
            assert(r == kspec(vs@, off as int, win_len as int));
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    emit(acc);
}

} // verus!
