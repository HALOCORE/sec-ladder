//! p42 rung R5 -- unsafe + Verus proof.
//!
//! R4's exec code verbatim, plus the specs and proofs that discharge every
//! unsafe precondition: the slice reads, the allocation's layout, the address
//! of every digest byte, the initialisation of every byte read back, and the
//! legality of the final `dealloc`.
//!
//! ⚠⚠ **AND NOT THE ONE THE PATTERN IS ABOUT. READ THIS BEFORE QUOTING THE
//! ROW.** p42's bug is a heap block that is never released on one path.
//! `vstd::raw_ptr` models the *permission* to release -- `Tracked<Dealloc>` --
//! and that permission is **AFFINE at the pinned Verus, not linear**: a proof
//! may simply DROP it. So an R5 that forgot the error path's `dig_free` still
//! reports `0 errors`. Measured, with a control that fires:
//!
//!   `.temp/t104/verus/lin_drop.rs` -- `allocate(64,1)` then `return 0` on one
//!   path with no `deallocate` -- `2 verified, 0 errors`.
//!   `.temp/t104/verus/lin_ctl.rs` -- the same tokens USED AFTER `deallocate`
//!   consumed them -- rejected, `error[E0382]: use of moved value`, i.e. the
//!   tokens are move-only and the probe was not vacuous.
//!
//! **So this rung is p42's central negative result: the proof rung of this
//! ladder cannot state the property the row prices.** What it does state is the
//! functional postcondition below, which is real and which every mutation stage
//! attacks; what it does not state is leak-freedom, and ../NOTES.md 6 says so
//! at length rather than leaving a reader to assume the `identity` pin covers
//! it. Nothing here is an `assume`.
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
//! by `check.py::_is_trusted`, each with a verified twin.

use vstd::prelude::*;
use vstd::layout::valid_layout;
use vstd::map::Map;
use vstd::raw_ptr::{allocate, deallocate, ptr_mut_from_data, ptr_mut_write, ptr_ref, Dealloc,
                    PointsTo, PointsToRaw, Provenance, PtrData};
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
// `ensures` conjunct in turn and requires the file to FAIL; this one still gave
// `15 verified, 0 errors`, i.e. it was a trusted claim carried for free. Every
// difference from vstd is a WEAKENING or a respelling, never a strengthening.
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
// what makes a use-after-free unstateable here -- and what does NOT make a
// LEAK unstateable, because consuming is not the same as being obliged to
// consume. See the module comment.
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

// ---------------------------------------------------------------- kernel ----
// Same exec code as unsafe.rs. Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(v: &[u64], off: usize, len: usize) -> (r: u64)
    requires
        off + len <= v@.len(),
        1 <= len <= isize::MAX,
    ensures
        r == kspec(v@, off as int, len as int),
{
    // Ghost only: mentioning `spec_slice_len` fires vstd's `axiom_spec_len`,
    // which is what tells the SMT solver a slice length fits in a `usize`.
    assert(v@.len() == vstd::slice::spec_slice_len(v));
    assert(valid_layout(len, 1));
    let (p, Tracked(raw), Tracked(dl)) = dig_alloc(len, 1);
    let base: usize = p.addr();
    let ghost prov = raw.provenance();

    if v_get_unchecked(v, off) & 0xff != TAG {
        // THE ERROR PATH. The release here is hand-written, exactly as R4's is
        // and exactly as the C rung's is missing; Verus checks that it is
        // LEGAL, and nothing checks that it is PRESENT.
        dig_free(p, len, 1, Tracked(raw), Tracked(dl));
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

    let mut acc: u64 = 0;
    let mut j: usize = 0;
    while j < len
        invariant
            0 <= j <= len,
            p.addr() == base,
            p@.provenance == prov,
            base + len <= usize::MAX + 1,
            rest.provenance() == prov,
            rest.is_range(base + (len - j), j as int),
            perms.dom() =~= set_int_range(0, (len - j) as int),
            forall|t: int|
                0 <= t < len - j ==> #[trigger] slot_ok(perms, base, prov, v@, off as int, t),
            acc == rfold(v@, off as int, len as int, j as int),
        decreases len - j,
    {
        let idx: usize = len - 1 - j;
        let q: *mut u8 = dig_at(p, base, idx);
        let ghost perms0 = perms;
        assert(slot_ok(perms, base, prov, v@, off as int, idx as int));
        let tracked mut pt: PointsTo<u8> = perms.tracked_remove(idx as int);
        let b: u8 = dig_read(q, Tracked(&pt));
        acc = acc.wrapping_mul(31).wrapping_add(b as u64);
        proof {
            assert(perms.dom() =~= set_int_range(0, idx as int));
            assert forall|t: int| 0 <= t < idx as int implies #[trigger] slot_ok(
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
        j = j + 1;
    }

    dig_free(p, len, 1, Tracked(rest), Tracked(dl));
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
