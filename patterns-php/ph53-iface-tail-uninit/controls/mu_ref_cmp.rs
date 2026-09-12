// ph53 control -- ITEM 79's REPRESENTATION, THE HALF THAT VERUS REFUSES.
//
// `mu_ref.rs` is this file minus `inherit_ref` and it verifies at 8/0. The one
// thing added here is the COMPARE-ONLY consumer -- `zend_compile.c:1951`, which
// READS THE SLOT AND DOES NOT DEREFERENCE IT -- and that asymmetry is this
// row's headline, so a representation that cannot carry it cannot carry the row.
//
// ⛔⛔ **THIS FILE MUST FAIL, AND THE MESSAGE IS THE POINT.** Verus 0.2026.08.09
// answers, at the `p` in `core::ptr::eq(p, target)`:
//
//     error: The verifier does not yet support the following Rust feature:
//            dereferencing a pointer (here the dereference is implicit)
//
// ⚠⚠⚠ THREE LAYERS, AND `TASK_PHP_041` §8.12 COLLAPSED THEM INTO ONE SENTENCE
// (*"`core::ptr::eq` ... which the pinned vstd does not specify"*). The outcome
// it reached is right; the reason is not, and the difference decides whether
// this is a row's problem or Verus's:
//
//   1. `core::ptr::eq(a, b)` on two `&u64` -- REFUSED, as above.
//   2. `(a as *const u64) == (b as *const u64)` -- **THE SAME REFUSAL AT THE
//      SAME POSITION**, i.e. the barrier is the `&T` -> `*const T` COERCION and
//      not the comparison.
//   3. ⭐ THE COMPARISON ITSELF IS FULLY SPECIFIED. `~/tools/verus/vstd/raw_ptr.rs:221`
//      ships `assume_specification[ <*const T as PartialEq<*const T>>::eq ]`
//      with `ensures res <==> (x@.addr == y@.addr) && (x@.metadata ==
//      y@.metadata)`, and `a == b` on two ALREADY-RAW `*const u64` verifies
//      against exactly that postcondition. So *"vstd does not specify it"* is
//      false of the comparison and true of nothing that matters here.
//   4. ⚠ AND EVEN WITH A POINTER IN HAND THE POSTCONDITION WOULD NOT CLOSE.
//      `vstd::raw_ptr::SharedReference` is the stop-gap route from `&'a T` to
//      `*const T` (`new` then `as_ptr`), but `new`'s `ensures` names only
//      `s.value()` and `ptr()` is `uninterp` -- so NOTHING relates
//      `&pool[i]`'s address to `i`, and `scan_c`'s answer is an INDEX. The
//      compare-only consumer's `ensures` is unprovable for a second, independent
//      reason.
//
// ▶ So item 79's representation drops the COMPARE-ONLY consumer, and it drops it
// because Verus cannot take a pointer out of a reference -- not because a spec
// is missing. `controls/spellings.py --verus` runs this file as a MUST-FIRE arm
// and asserts the message above, so the day Verus supports the coercion this
// claim stops being true out loud instead of quietly.

use vstd::prelude::*;
use vstd::raw_ptr::MemContents;
use core::mem::MaybeUninit;

verus! {

pub const MAXD: usize = 16;

pub const MAXP: usize = 8;

/// `(hit, matched_id, examined)` -- `scan_d` on the reference representation.
/// ⚠ The slot's spec value is a `&u64`, so the fold reads the POINTEE and the
/// spec says so; nothing here mentions an index or a bound.
pub open spec fn scan_ref(slots: Seq<Option<&u64>>, i: int, n: int, t: u64) -> (u64, u64, u64)
    decreases n - i,
{
    if i >= n {
        (0u64, 0u64, n as u64)
    } else {
        match slots[i] {
            Some(p) => if *p == t {
                (1u64, *p, (i + 1) as u64)
            } else {
                scan_ref(slots, i + 1, n, t)
            },
            None => scan_ref(slots, i + 1, n, t),
        }
    }
}

pub open spec fn abst_ref<'a>(
    slots: Seq<MaybeUninit<&'a u64>>,
    wrote: Seq<bool>,
    n: int,
) -> Seq<Option<&'a u64>> {
    Seq::new(
        n as nat,
        |i: int|
            if wrote[i] {
                Some(slots[i].mem_contents().value())
            } else {
                None::<&'a u64>
            },
    )
}

// THE ONE TRUSTED ITEM, and it is the `MaybeUninit` read. ⚠ There is no safe
// exec expression from `MaybeUninit<T>` to `T` -- that is what the type means --
// and `harness/check.py::_scan_unsafe_sites` requires every `unsafe` token in a
// pinned Verus source to sit inside an `external_body` body, so ONE is the
// floor for a shippable rung on this row and ZERO is reachable only in a
// control. `../NOTES.md` §11.5.
#[verifier::external_body]
fn mu_read<'a>(m: MaybeUninit<&'a u64>) -> (r: &'a u64)
    requires
        m.mem_contents().is_init(),
    ensures
        r == m.mem_contents().value(),
{
    unsafe { m.assume_init() }
}

fn mk<'a>(n: usize) -> (v: Vec<MaybeUninit<&'a u64>>)
    ensures
        v@.len() == n,
        forall|i: int|
            0 <= i < n ==> #[trigger] v@[i].mem_contents() == MemContents::<&'a u64>::Uninit,
{
    let mut v: Vec<MaybeUninit<&'a u64>> = Vec::with_capacity(n);
    let mut k: usize = 0;
    while k < n
        invariant
            k <= n,
            v@.len() == k,
            forall|i: int|
                0 <= i < k ==> #[trigger] v@[i].mem_contents() == MemContents::<&'a u64>::Uninit,
        decreases n - k,
    {
        v.push(MaybeUninit::uninit());
        k = k + 1;
    }
    v
}

/// `instanceof_function_ex`'s loop -- `Zend/zend_operators.c:1530-1538`.
/// **THE FAULTING CONSUMER, and on this representation the read is a genuine
/// pointer dereference.**
fn instanceof_ref(
    slots: &Vec<MaybeUninit<&u64>>,
    wrote: &[bool; MAXD],
    target_id: u64,
) -> (r: (u64, u64, u64))
    requires
        slots@.len() <= MAXD,
        forall|j: int|
            0 <= j < slots@.len() ==> (#[trigger] wrote@[j]
                ==> slots@[j].mem_contents().is_init()),
    ensures
        r == scan_ref(abst_ref(slots@, wrote@, slots@.len() as int), 0, slots@.len() as int,
            target_id),
{
    let n: usize = slots.len();
    let ghost a = abst_ref(slots@, wrote@, slots@.len() as int);
    let ghost target = scan_ref(a, 0, slots@.len() as int, target_id);
    let mut examined: u64 = 0;
    let mut i: usize = 0;
    while i < n
        invariant
            i <= n,
            n == slots@.len(),
            n <= MAXD,
            wrote@.len() == MAXD,
            examined == i as u64,
            a == abst_ref(slots@, wrote@, slots@.len() as int),
            target == scan_ref(a, 0, slots@.len() as int, target_id),
            forall|j: int|
                0 <= j < n ==> (#[trigger] wrote@[j] ==> slots@[j].mem_contents().is_init()),
            scan_ref(a, i as int, n as int, target_id) == target,
        decreases n - i,
    {
        examined = (i + 1) as u64;
        if wrote[i] {
            // ⭐ NO INDEX AND NO BOUND: the slot IS the pointer.
            let p: &u64 = mu_read(slots[i]);
            let id: u64 = *p;
            assert(a[i as int] == Some(p));
            if id == target_id {
                assert(scan_ref(a, i as int, n as int, target_id) == (1u64, id, (i + 1) as u64));
                return (1, id, examined);
            }
        } else {
            assert(a[i as int] is None);
        }
        i = i + 1;
    }
    assert(scan_ref(a, n as int, n as int, target_id) == (0u64, 0u64, n as u64));
    (0, 0, examined)
}

/// `zend_do_inherit_interfaces`'s dedup scan -- `Zend/zend_compile.c:1951`.
/// **THE COMPARE-ONLY CONSUMER.** ⛔ The `core::ptr::eq` below is what Verus
/// refuses; every other line of this function verifies in `mu_ref.rs`'s shape.
fn inherit_ref(slots: &Vec<MaybeUninit<&u64>>, wrote: &[bool; MAXD], target: &u64) -> (r: usize)
    requires
        slots@.len() <= MAXD,
        forall|j: int|
            0 <= j < slots@.len() ==> (#[trigger] wrote@[j]
                ==> slots@[j].mem_contents().is_init()),
{
    let n: usize = slots.len();
    let mut i: usize = 0;
    while i < n
        invariant
            i <= n,
            n == slots@.len(),
            n <= MAXD,
            wrote@.len() == MAXD,
            forall|j: int|
                0 <= j < n ==> (#[trigger] wrote@[j] ==> slots@[j].mem_contents().is_init()),
        decreases n - i,
    {
        if wrote[i] {
            let p: &u64 = mu_read(slots[i]);
            if core::ptr::eq(p, target) {
                return i;
            }
        }
        i = i + 1;
    }
    n
}

fn main() {
    let pool: [u64; MAXP] = [11u64, 22, 33, 44, 55, 66, 77, 88];
    let mut slots = mk(2);
    let mut wrote: [bool; MAXD] = [false; MAXD];
    slots[0] = MaybeUninit::new(&pool[1]);
    wrote[0] = true;
    assert(slots@[0].mem_contents().is_init());
    let r = instanceof_ref(&slots, &wrote, 22u64);
    assert(r.0 == 1);
    let j = inherit_ref(&slots, &wrote, &pool[1]);
}

} // verus!
