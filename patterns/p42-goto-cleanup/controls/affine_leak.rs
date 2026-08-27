// p42 control 3 -- VERUS CANNOT STATE LEAK-FREEDOM AT THE PINNED VERSION.
//
// This file is p42's central negative result, in a form anyone can re-run:
//
//     ./verus_run.py patterns/p42-goto-cleanup/controls/affine_leak.rs
//     -> verification results:: 2 verified, 0 errors
//
// `leaky` allocates, takes an error path, and NEVER deallocates.  Both tracked
// tokens -- the `PointsToRaw` and the `Dealloc` -- go out of scope on that path.
// Verus accepts it.  So `Tracked<Dealloc>` is AFFINE (droppable), not LINEAR
// (must be consumed), and an R5 that forgot the error path's `dig_free` would
// report `0 errors` exactly as verus.rs does.
//
// THE POSITIVE CONTROL is `moved_twice` below, and it must FAIL, because
// otherwise this file would prove nothing: a token that could be used freely
// would not be a resource at all.  It is rejected -- by rustc, not by Verus:
//
//     error[E0382]: use of moved value: `pt`
//       ... `PointsToRaw`, which does not implement the `Copy` trait
//     error[E0382]: use of moved value: `dl` ... `Dealloc` ...
//
// so the tokens ARE move-only.  Move-only and droppable is exactly affine.
//
// HOW TO RUN BOTH ARMS: as committed, the `moved_twice` arm is behind
// `#[cfg(p42_control_must_fail)]`, so the default run is the 2/0 above.  Add
// `--cfg p42_control_must_fail` and the run must fail with the two E0382s.
//
//   ./verus_run.py patterns/p42-goto-cleanup/controls/affine_leak.rs \
//       --cfg p42_control_must_fail      # MUST FAIL
//
// See ../NOTES.md 6.
use vstd::prelude::*;
use vstd::layout::valid_layout;
use vstd::raw_ptr::{allocate, deallocate};

verus! {

broadcast use {
    vstd::layout::group_layout_axioms,
    vstd::layout::align_of_u8,
    vstd::raw_ptr::group_raw_ptr_axioms,
};

fn leaky(err: bool) -> (r: u64) {
    assert(valid_layout(64, 1));
    let (p, Tracked(pt), Tracked(dl)) = allocate(64, 1);
    if err {
        // NO deallocate on this path. Both tracked tokens are dropped here.
        // Verus does not object, and that is p42's finding.
        return 0;
    }
    deallocate(p, 64, 1, Tracked(pt), Tracked(dl));
    1
}

#[cfg(p42_control_must_fail)]
fn moved_twice() -> (r: u64) {
    assert(valid_layout(64, 1));
    let (p, Tracked(pt), Tracked(dl)) = allocate(64, 1);
    deallocate(p, 64, 1, Tracked(pt), Tracked(dl));
    deallocate(p, 64, 1, Tracked(pt), Tracked(dl));   // MUST be rejected
    1
}

fn main() {
    let x = leaky(false);
}

} // verus!
