//! ph55 control -- **VERUS DOES NOT SUPPORT FUNCTION POINTER TYPES, AND THAT IS
//! THIS ROW'S OWN DISPATCH MECHANISM.**
//!
//!     ./verus_run.py patterns-php/ph55-opdata-stride/controls/fnptr.rs
//!
//! ⛔⛔ **THIS FILE MUST FAIL TO VERIFY.** It is a MUST-FIRE negative, not a
//! rung and not an aspiration: `controls/negatives.py --verus` runs it on every
//! invocation and fails if Verus ever accepts it, because the day Verus grows
//! function pointers is the day four of this row's files should be rewritten and
//! a stale comment is how that gets missed.
//!
//! The expected output, measured 2026-09-14 against Verus
//! `0.2026.08.09.92f466f`:
//!
//!     error: The verifier does not yet support the following Rust feature:
//!            function pointer types
//!       --> .../fnptr.rs:NN:NN
//!        |
//!     NN | fn dispatch(t: &[Option<H>; 4], i: usize, x: u64) -> (r: u64)
//!        |             ^^^^^^^^^^^^^^^^^^
//!
//! ⚠ IT IS A TYPE-LEVEL REFUSAL AND NOT A PROOF FAILURE, which is the part that
//! decides the row. `.memory/04-verus.md`'s rule is to read the ERROR TEXT and
//! not the exit code: `postcondition not satisfied` disqualifies nothing, while
//! `is not supported` forces a NEW TRUSTED ITEM -- and here there is nothing to
//! make trusted, because the refusal is on the PARAMETER'S TYPE. A
//! `#[verifier::external_body]` wrapper around the call does not help: any
//! Verus-visible signature mentioning `[Option<fn(..)>; N]` is refused, so the
//! op_array itself would have to become opaque, and an opaque op_array cannot
//! carry `ok_from` or the value postcondition.
//!
//! ▶ **CONSEQUENCE, AND IT IS DECLARED IN `../spec.md`
//! `provenance.divergences`:** every Rust rung stores an `Option<u8>` handler ID
//! and dispatches with a `match`. ⚠ It is not a choice R4 could have made
//! differently: `../spec.md`'s `identity` pins R4 == R5, so a representation R5
//! cannot express is one R4 may not use either.
//!
//! ⭐ **AND THE SUBSTITUTION IS PRICED, NOT WAVED AT:**
//! `controls/fnptr_dispatch.rs` is `safe_naive.rs` with the real function-
//! pointer table -- legal in plain Rust, illegal here -- and
//! `controls/fnptr_cost.py` measures the difference in `Ir`. It changes NO
//! answer, because `Option<fn>` and `Option<u8>` are `None` for exactly the same
//! opcode, so what moves is instructions and not behaviour.

use vstd::prelude::*;

verus! {

/// `opcode_handler_t` -- Zend/zend_execute.h. THE TYPE VERUS REFUSES.
type H = fn(u64) -> u64;

fn h_add(x: u64) -> (r: u64) {
    if x < 1000 {
        x + 1
    } else {
        x
    }
}

fn h_nop(x: u64) -> (r: u64) {
    x
}

/// `zend_opcode_handlers[512]` narrowed to four entries, and the dispatch the
/// executor performs through `opline->handler` (zend_execute.c:1391). The
/// `requires` is even the RIGHT one -- `t[i].is_some()` is exactly what
/// `ok_from` gives `hunwrap` in `../verus.rs` -- and Verus never gets far
/// enough to look at it.
fn dispatch(t: &[Option<H>; 4], i: usize, x: u64) -> (r: u64)
    requires
        i < 4,
        t[i as int].is_some(),
{
    let f = t[i].unwrap();
    f(x)
}

fn main() {
}

} // verus!
