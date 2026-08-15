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

broadcast use vstd::slice::group_slice_axioms;

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
            let off: usize = (acc % nwin) as usize;
            let r: u64 = kernel(vs, off, win_len);
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    emit(acc);
}

} // verus!
