//! ph52 CONTROL -- **the obligation, UNWRAPPED, verified against vstd's own
//! specification and NOT against a hand-written contract.**
//!
//!     ./verus_run.py patterns-php/ph52-concat-copy-uninit/controls/mu_unwrapped.rs
//!     -> verification results:: 6 verified, 0 errors
//!
//! ⚠⚠⚠ **THIS FILE IS WHAT KEEPS `verus.rs`'s `slot_read_unchecked` HONEST.**
//! That item is `#[verifier::external_body]`, so its `requires` -- including
//! `m.mem_contents().is_init()` -- is **TRUSTED**: Verus never looks at the body.
//! Normally 5c-twin is what checks that a trusted `requires` is strong enough to
//! license a *checked* implementation, and on that one item **there can be no
//! twin** (`../NOTES.md` §11: there is no safe exec route from `MaybeUninit<T>` to
//! `T`, so any twin's body would carry an `unsafe` token outside a trusted body,
//! which `check.py::_scan_unsafe_sites` refuses).
//!
//! ▶ **So this file is the substitute, and it is a stronger object than a twin
//! would have been:** it drives the SAME operations with **no trusted item at
//! all**, letting the pinned vstd's own `assume_specification` carry the
//! obligation. `unconstructed` proves a bare `MaybeUninit::uninit()` is `Uninit`;
//! `construct` writes one and proves it `Init`; `teardown` reads it back under
//! `requires m.mem_contents().is_init()` and proves the value. **If `verus.rs`'s
//! hand-asserted contract ever drifted from what vstd actually says, this file
//! would stop verifying** -- and it costs one command.
//!
//! ⭐ It is also the evidence for the row's Verus-side headline: **in ordinary
//! exec code `MaybeUninit::assume_init_ref` needs NO trusted item**, because
//! `~/tools/verus/vstd/std_specs/maybe_uninit.rs:45-49` carries
//! `requires m.mem_contents().is_init()`. `verus.rs` cannot use that only because
//! of the gate rule above, not because Verus cannot express it.
//!
//! ⭐⭐ **AND IT IS WHERE THE ROW's SHAPE SHOWS AGAINST `ph53`'s.** ph53's copy of
//! this file needs a `Vec<MaybeUninit<u32>>`, a `with_capacity`/`push` loop, a
//! `forall` over the slots and `Vec`'s `IndexMut` specification. ph52 needs a
//! SINGLE LOCAL, because the C's slot is one -- so there is no indexing to
//! specify, no loop to invariant and no quantifier. **That difference is the same
//! O(slots) story the runtime witness tells, one level up**, and it is why this
//! file is 4 items plus `main` where ph53's is 4 plus `main` over a whole `Vec`.
//!
//! ⚠ It is NOT a rung and not on any build path: `harness/build.py` has no
//! `RUST_SRC` entry for it and its `main` reads no input.
use vstd::prelude::*;
use vstd::raw_ptr::MemContents;
use core::mem::MaybeUninit;

verus! {

/// What a constructed slot holds -- `verus.rs`'s `Pr`, same two fields.
#[derive(Clone, Copy)]
pub struct Pr {
    pub req: usize,
    pub len: usize,
}

/// `Zend/zend_operators.c:1148` -- `zval op1_copy;`, with nothing written.
/// ⚠ `MaybeUninit::uninit()` and NOT `mem::zeroed()` or a `Default`: forging a
/// value is what the catalogue's trap warns against and what R2 has to do.
fn unconstructed() -> (m: MaybeUninit<Pr>)
    ensures
        m.mem_contents() == MemContents::<Pr>::Uninit,
{
    MaybeUninit::uninit()
}

/// `Zend/zend.c:263` -- `expr_copy->type = IS_STRING;`, i.e. the slot becoming
/// constructed. The WHOLE value is written at once, which is what makes the
/// witness a single bit rather than a per-field record.
fn construct(m: &mut MaybeUninit<Pr>, p: Pr)
    ensures
        final(m).mem_contents() == MemContents::Init(p),
{
    *m = MaybeUninit::new(p);
}

/// ⭐⭐ THE OBLIGATION, UNWRAPPED. No `external_body`, no twin, no hand-written
/// contract for `assume_init_ref`: the `requires` below is what licenses it and
/// vstd's `assume_specification` (`std_specs/maybe_uninit.rs:45-49`) is what
/// demands it.
fn teardown(m: &MaybeUninit<Pr>) -> (r: Pr)
    requires
        m.mem_contents().is_init(),
    ensures
        r == m.mem_contents().value(),
{
    unsafe { *m.assume_init_ref() }
}

/// `concat_function`'s own shape: declare the slot, construct it at `:263`, tear
/// it down at `:1188`. ⚠ The `assert` is what would fail if `construct`'s
/// `ensures` and `teardown`'s `requires` ever stopped meeting.
fn go(req: usize, len: usize) -> (r: usize)
    ensures
        r == req,
{
    let mut m: MaybeUninit<Pr> = unconstructed();
    assert(!m.mem_contents().is_init());
    construct(&mut m, Pr { req, len });
    assert(m.mem_contents().is_init());
    let p: Pr = teardown(&m);
    p.req
}

fn main() {
    let r = go(31, 14);
    assert(r == 31);
}

} // verus!
