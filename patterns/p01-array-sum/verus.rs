//! p01 rung R5 -- unsafe + Verus proof.
//!
//! R4's exec code verbatim, plus the specs and proofs that discharge the
//! `get_unchecked` precondition. The point of this rung is not that it verifies
//! (a proof of nothing verifies too) but that:
//!
//!   * `main` is *inside* `verus!` and is *not* `external_body`, so the call
//!     `kernel(vs, off, win_len)` is a real, verified call site and its
//!     `requires off + len <= v.len()` is genuinely discharged
//!     (`.memory/02-bench-rules.md` rule 2 -- the defect that made the pilot's
//!     R5 decorative), and
//!   * the contract is total on values -- there is no `requires` on the array
//!     contents, so every input the benchmark measures is inside the verified
//!     domain by construction, `adversarial-*` included (rules 1 and 3).
//!
//! TCB tally: NOTES.md. Three `external_body` items, all listed there.

use vstd::prelude::*;

// Plain-Rust I/O helpers. Outside `verus!`, so Verus treats the whole module as
// external (external-by-default). Reached only through `load_input`/`emit`.
#[path = "../../common/driver.rs"]
mod driver;

verus! {

// Gives `slice@.len() == spec_slice_len(slice)`, hence `slice@.len() <= usize::MAX`
// -- without it `off + i` cannot be shown not to overflow `usize`.
broadcast use vstd::slice::group_slice_axioms;

// ------------------------------------------------------------------ spec ----
/// The wrapping sum of `v[off .. off+len)`, i.e. exactly what all five rungs
/// compute (../spec.md). `u64::wrapping_add` is usable in spec position because
/// vstd marks it `#[verifier::allow_in_spec]`.
pub open spec fn sum_wrap(v: Seq<u64>, off: int, len: int) -> u64
    decreases len,
{
    if len <= 0 {
        0u64
    } else {
        sum_wrap(v, off, len - 1).wrapping_add(v[off + len - 1])
    }
}

// ------------------------------------------------------------------- TCB ----
// TRUSTED ITEM 1 of 3. vstd ships no specification for `<[T]>::get_unchecked`,
// so this is the axiom that licenses the unsafe read. It is sound because the
// standard library's documented contract for `get_unchecked` is exactly this:
// if the caller guarantees `i < v.len()`, the call is defined and yields
// `v[i]`. The `requires` is not decoration -- `kernel` has to prove it on every
// iteration, and `main` has to prove `kernel`'s in turn.
#[inline(always)]
#[verifier::external_body]
fn get_unchecked(v: &[u64], i: usize) -> (r: u64)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    unsafe { *v.get_unchecked(i) }
}

// TRUSTED ITEM 2 of 3. Argument parsing, file I/O and little-endian decoding,
// delegated to common/driver.rs so that all five rungs read the file the same
// way. It states **no** `ensures` at all, deliberately: an `ensures` here would
// be an axiom about the contents of a file, which nothing can justify. Every
// fact the proof needs is re-derived at run time from `vals.len()`.
#[verifier::external_body]
fn load_input() -> (r: (u64, u64, Vec<u64>)) {
    let path = driver::arg_path();
    let inp = driver::load(&path);
    let (win_len_w, vals) = driver::head_u64_body(&inp);
    (inp.n_iters, win_len_w, vals)
}

// TRUSTED ITEM 3 of 3. `println!` is not verifiable; no `ensures`.
#[verifier::external_body]
fn emit(acc: u64) {
    driver::emit(acc);
}

// ---------------------------------------------------------------- kernel ----
// Same exec code as unsafe.rs. Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(v: &[u64], off: usize, len: usize) -> (r: u64)
    requires
        off + len <= v@.len(),
    ensures
        r == sum_wrap(v@, off as int, len as int),
{
    let mut acc: u64 = 0;
    // Ghost only: mentioning `spec_slice_len` fires vstd's `axiom_spec_len`,
    // which is what tells the SMT solver a slice length fits in a `usize` --
    // needed to rule out `off + i` overflowing. Erases at compile time.
    assert(v@.len() == vstd::slice::spec_slice_len(v));
    for i in 0..len
        invariant
            off + len <= v@.len(),
            v@.len() <= usize::MAX,
            acc == sum_wrap(v@, off as int, i as int),
    {
        acc = acc.wrapping_add(get_unchecked(v, off + i));
    }
    acc
}

// ---------------------------------------------------------------- driver ----
fn main() {
    let (n_iters, win_len_w, vals) = load_input();
    // SLB-DRIVER-BEGIN
    let n_vals: usize = vals.len();
    let vs: &[u64] = vals.as_slice();
    let mut acc: u64 = 0;
    if win_len_w > 0 && win_len_w <= n_vals as u64 {
        let win_len: usize = win_len_w as usize;
        let nwin: u64 = (n_vals - win_len + 1) as u64;
        let mut it: u64 = 0;
        while it < n_iters
            invariant
                1 <= win_len <= n_vals,
                vs@.len() == n_vals,
                nwin == n_vals - win_len + 1,
            decreases n_iters - it,
        {
            let off: usize = (acc % nwin) as usize;
            let r: u64 = kernel(vs, off, win_len);
            // Ghost only: this is what *consumes* the kernel's `ensures`.
            // Without it the postcondition is decoration -- deleting it
            // entirely still gives "5 verified, 0 errors", so nothing but
            // mutation testing defends it (TASK_002_REVIEW). Ghost code erases,
            // so the driver loop stays byte-identical to R4's; `harness/dloop.py`
            // exempts ghost statements from the driver diff exactly as it
            // exempts `invariant`/`decreases`.
            assert(r == sum_wrap(vs@, off as int, win_len as int));
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    emit(acc);
}

} // verus!
