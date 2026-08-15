//! p01 **control** rung R2v -- safe-naive + Verus proof. NOT one of the five
//! ladder rungs and NOT part of the measured 6-cell matrix; build it with
//! `harness/build.py --cell safe_naive_verus`.
//!
//! It exists to hold up half of the project's headline structural finding
//! (`.memory/01-ladder.md`, finding 2): proving safe code panic-free buys
//! *nothing*. The exec code below is character-for-character `safe_naive.rs`'s
//! kernel, so if the proof cost anything, `md5_raw` would move. It does not:
//! rustc never learns what Z3 knew and emits the same bounds check either way.
//!
//! The proof here is not vacuous -- it discharges exactly the same
//! `off + len <= v.len()` obligation as verus.rs. The difference is that in
//! verus.rs that obligation *licenses* `get_unchecked`, and here it licenses
//! nothing, because safe indexing was going to check at run time regardless.

use vstd::prelude::*;

#[path = "../../common/driver.rs"]
mod driver;

verus! {

// `group_slice_axioms` gives `slice@.len() == spec_slice_len(slice)`, hence
// `slice@.len() <= usize::MAX` -- without it `off + i` cannot be shown not to
// overflow `usize`. `lemma_u128_shr_is_div` turns `x >> 64` into `x / 2^64`,
// which is what the driver's multiply-shift barrier bound is about.
broadcast use {
    vstd::slice::group_slice_axioms,
    vstd::bits::lemma_u128_shr_is_div,
};

/// Identical to verus.rs's spec.
pub open spec fn sum_wrap(v: Seq<u64>, off: int, len: int) -> u64
    decreases len,
{
    if len <= 0 {
        0u64
    } else {
        sum_wrap(v, off, len - 1).wrapping_add(v[off + len - 1])
    }
}

// TRUSTED 1 of 2: argument parsing, file I/O, decoding. No `ensures`.
#[verifier::external_body]
fn load_input() -> (r: (u64, u64, Vec<u64>)) {
    let path = driver::arg_path();
    let inp = driver::load(&path);
    let (win_len_w, vals) = driver::head_u64_body(&inp);
    (inp.n_iters, win_len_w, vals)
}

// TRUSTED 2 of 2: `println!`. No `ensures`.
#[verifier::external_body]
fn emit(acc: u64) {
    driver::emit(acc);
}

// ---------------------------------------------------------------- kernel ----
// Exec body identical to safe_naive.rs. Zero `unsafe` anywhere in this file.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(v: &[u64], off: usize, len: usize) -> (r: u64)
    requires
        off + len <= v@.len(),
    ensures
        r == sum_wrap(v@, off as int, len as int),
{
    let mut acc: u64 = 0;
    assert(v@.len() == vstd::slice::spec_slice_len(v));
    for i in 0..len
        invariant
            off + len <= v@.len(),
            v@.len() <= usize::MAX,
            acc == sum_wrap(v@, off as int, i as int),
    {
        acc = acc.wrapping_add(v[off + i]);
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
            // Ghost only, and the reason the barrier could be swapped from a
            // `%` to a multiply-shift at TASK_005: `off` must still be in
            // range. `(acc * nwin) >> 64 < nwin` because `acc <= u64::MAX`
            // implies `acc * nwin < nwin * 2^64`. Both steps are nonlinear, so
            // Z3 needs them spelled out; `lemma_u128_shr_is_div` is what turns
            // the shift into the division the arithmetic is about. Erases at
            // compile time -- R4 and R5 stay byte-identical.
            proof {
                let p: int = (acc as int) * (nwin as int);
                assert((acc as u128) * (nwin as u128)
                       <= (u64::MAX as u128) * (u64::MAX as u128))
                    by (nonlinear_arith)
                    requires acc <= u64::MAX, nwin <= u64::MAX;
                assert(vstd::arithmetic::power2::pow2(64)
                       == 0x1_0000_0000_0000_0000nat) by {
                    vstd::arithmetic::power2::lemma2_to64_rest();
                }
                assert(p < (nwin as int) * 0x1_0000_0000_0000_0000int)
                    by (nonlinear_arith)
                    requires p == (acc as int) * (nwin as int),
                             acc <= u64::MAX, nwin >= 1;
            }
            let off: usize = ((acc as u128 * nwin as u128) >> 64) as usize;
            let r: u64 = kernel(vs, off, win_len);
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    emit(acc);
}

} // verus!
