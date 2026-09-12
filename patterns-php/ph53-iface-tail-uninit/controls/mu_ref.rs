// ph53 control -- ITEM 79's REPRESENTATION, THE HALF THAT VERIFIES.
//
// `Vec<MaybeUninit<&u64>>`: the slot holds a REFERENCE INTO THE POOL, exactly as
// `zend_class_entry.interfaces[i]` holds a `ph53_iface *`. `c/kernel.h:97`
// declares `struct ph53_iface { uint64_t id; }` -- one `u64` field -- so `&u64`
// is that struct's reference with the newtype elided.
//
// WHAT THIS FILE ESTABLISHES, and it is `TASK_PHP_041` §8.12's own claim put
// where a command can re-check it:
//
//   1. the FAULTING consumer verifies on this representation, with the read
//      spelled as a genuine pointer dereference (`*p`);
//   2. ⭐ AND §11.5's FOURTH OBLIGATION IS GONE. On the shipped index
//      representation the slot holds a `u32` and `pool_get_unchecked` needs
//      `p < MAXP` -- *"the PRICE OF THE REPRESENTATION and not part of the C's
//      obligation"* (`../unsafe.rs`'s header). Here there is no index to bound:
//      the only obligation left on the read is `is_init`, which IS the defect.
//
// ⛔ WHAT IT DOES NOT ESTABLISH is in `mu_ref_cmp.rs`, which is the same program
// plus the COMPARE-ONLY consumer and which Verus REFUSES.
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

fn main() {
    let pool: [u64; MAXP] = [11u64, 22, 33, 44, 55, 66, 77, 88];
    let mut slots = mk(2);
    let mut wrote: [bool; MAXD] = [false; MAXD];
    slots[0] = MaybeUninit::new(&pool[1]);
    wrote[0] = true;
    assert(slots@[0].mem_contents().is_init());
    let r = instanceof_ref(&slots, &wrote, 22u64);
    assert(r.0 == 1);
}

} // verus!
