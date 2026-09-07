//! p01 rung R4 -- unsafe.
//!
//! R2's loop with the bounds check removed by `get_unchecked`. Correct, but
//! nothing checks that it is: the caller's `off + len <= v.len()` is a comment.
//! R5 (verus.rs) is this exec code with that comment turned into an obligation.

#[path = "../../common/driver.rs"]
mod driver;

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md.
//
// SAFETY: `off + i < off + len <= v.len()` for every i in 0..len. Unchecked
// here; discharged by Verus in verus.rs.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(v: &[u64], off: usize, len: usize) -> u64 {
    let mut acc: u64 = 0;
    for i in 0..len {
        acc = acc.wrapping_add(unsafe { *v.get_unchecked(off + i) });
    }
    acc
}

// ---------------------------------------------------------------- driver ----
fn main() {
    let path = driver::arg_path();
    let inp = driver::load(&path);
    let (win_len_w, vals) = driver::head_u64_body(&inp);
    let n_iters: u64 = inp.n_iters;
    // SLB-DRIVER-BEGIN
    let n_vals: usize = vals.len();
    let vs: &[u64] = vals.as_slice();
    let mut acc: u64 = 0;
    if win_len_w > 0 && win_len_w <= n_vals as u64 {
        let win_len: usize = win_len_w as usize;
        let nwin: u64 = (n_vals - win_len + 1) as u64;
        let mut it: u64 = 0;
        while it < n_iters {
            let off: usize = ((acc as u128 * nwin as u128) >> 64) as usize;
            let r: u64 = kernel(vs, off, win_len);
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    driver::emit(acc);
}
