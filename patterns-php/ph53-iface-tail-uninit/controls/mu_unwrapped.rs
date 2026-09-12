//! ph53 CONTROL — **the obligation, UNWRAPPED, verified against vstd's own
//! specification and NOT against a hand-written contract.**
//!
//!     ./verus_run.py patterns-php/ph53-iface-tail-uninit/controls/mu_unwrapped.rs
//!     -> verification results:: 7 verified, 0 errors
//!
//! ⚠⚠⚠ **THIS FILE IS WHAT KEEPS `verus.rs`'s `slot_read_unchecked` HONEST.**
//! That item is `#[verifier::external_body]`, so its `requires` — including
//! `v@[i as int].mem_contents().is_init()` — is **TRUSTED**: Verus never looks
//! at the body. Normally 5c-twin is what checks that a trusted `requires` is
//! strong enough to license a *checked* implementation, and on that one item
//! **there can be no twin** (`../NOTES.md` §11.5: there is no safe exec route
//! from `MaybeUninit<T>` to `T`, so any twin's body would carry an `unsafe`
//! token outside a trusted body, which `check.py::_scan_unsafe_sites` refuses).
//!
//! ▶ **So this file is the substitute, and it is a stronger object than a twin
//! would have been:** it drives the SAME operations with **no trusted item at
//! all**, letting the pinned vstd's own `assume_specification` carry the
//! obligation. `mk` builds `n` uninitialised slots and proves them `Uninit`;
//! `fill` writes one through `Vec`'s `IndexMut` and proves it `Init`; `qread`
//! reads it back under `requires v@[i].mem_contents().is_init()` and proves the
//! value. **If `verus.rs`'s hand-asserted contract ever drifted from what vstd
//! actually says, this file would stop verifying** — and it costs one command.
//!
//! ⭐ It is also the evidence for the row's Verus-side headline: **in ordinary
//! exec code `MaybeUninit::assume_init` needs NO trusted item**, because
//! `~/tools/verus/vstd/std_specs/maybe_uninit.rs` carries
//! `requires m.mem_contents().is_init()`. `verus.rs` cannot use that only
//! because of the gate rule above, not because Verus cannot express it.
//!
//! ⭐⭐ AND IT SETTLES `TASK_PHP_040_REPORT.md` §5.6's ONE UNRESOLVED RESIDUAL
//! RISK: *"whether the `FILL` assignment through `Vec`'s `index_mut` carries a
//! value-level `ensures`."* **It does, and the whole of it** —
//! `std_specs/vec.rs`'s `vec_index_mut` ensures
//! `*element == old(vec)@.index(i)`,
//! `final(vec)@ == old(vec)@.update(i, *final(element))` **and**
//! `*final(element) == final(vec)@.index(i)`. `fill` below is that assignment
//! and it verifies.
//!
//! ⚠ It is NOT a rung and not on any build path: `harness/build.py` has no
//! `RUST_SRC` entry for it and it has no `main` that reads an input.
use vstd::prelude::*;
use vstd::raw_ptr::MemContents;
use core::mem::MaybeUninit;

verus! {

broadcast use vstd::slice::group_slice_axioms;

/// `c/kernel.h` `PH53_MAXP`.
pub const MAXP: usize = 8;

/// Phase 2, as `verus.rs` does it: `n` slots, sized to the count, nothing
/// written. ⚠ `MaybeUninit::uninit()` rather than `Vec::set_len` +
/// `spare_capacity_mut`, which the pinned vstd does not specify -- that is
/// `../spec.md`'s `idiom.forbidden[1]` and this is where it is checked.
fn mk(n: usize) -> (v: Vec<MaybeUninit<u32>>)
    ensures
        v@.len() == n,
        forall|i: int| 0 <= i < n ==> #[trigger] v@[i].mem_contents() == MemContents::<u32>::Uninit,
{
    let mut v: Vec<MaybeUninit<u32>> = Vec::with_capacity(n);
    let mut k: usize = 0;
    while k < n
        invariant
            k <= n,
            v@.len() == k,
            forall|i: int|
                0 <= i < k ==> #[trigger] v@[i].mem_contents() == MemContents::<u32>::Uninit,
        decreases n - k,
    {
        v.push(MaybeUninit::uninit());
        k = k + 1;
    }
    v
}

/// A `FILL`, through `Vec`'s `IndexMut` -- `_040` §5.6's unresolved residual
/// risk, and it verifies.
fn fill(v: &mut Vec<MaybeUninit<u32>>, i: usize, x: u32)
    requires
        i < old(v)@.len(),
    ensures
        final(v)@.len() == old(v)@.len(),
        final(v)@[i as int].mem_contents() == MemContents::Init(x),
{
    v[i] = MaybeUninit::new(x);
}

/// ⭐⭐ THE OBLIGATION, UNWRAPPED. No `external_body`, no twin, no hand-written
/// contract for `assume_init`: the `requires` below is what licenses it and
/// vstd's `assume_specification` is what demands it.
fn qread(v: &Vec<MaybeUninit<u32>>, i: usize) -> (r: u32)
    requires
        i < v@.len(),
        v@[i as int].mem_contents().is_init(),
    ensures
        r == v@[i as int].mem_contents().value(),
{
    let m: MaybeUninit<u32> = v[i];
    unsafe { m.assume_init() }
}

/// The row's phase 2 + one FILL + one QUERY, end to end.
fn go(n: usize, p: u32) -> (r: u32)
    requires
        0 < n,
        p < MAXP as u32,
    ensures
        r == p,
{
    let mut v = mk(n);
    fill(&mut v, 0, p);
    assert(v@[0].mem_contents().is_init());
    qread(&v, 0)
}

fn main() {
    let r = go(6, 3);
    assert(r == 3);
}

} // verus!
