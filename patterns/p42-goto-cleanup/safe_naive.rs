//! p42 rung R2 -- safe-naive.
//!
//! The mechanical port a working Rust programmer writes first: `vec![0u8; len]`
//! for the digest, counted `for` loops, `v[..]` and `dig[..]` indexing. Zero
//! `unsafe`.
//!
//! **THE ERROR PATH IS THE POINT, AND IN THIS RUNG IT IS ONE `return`.** The C
//! rung's error branch has to jump into a cleanup chain and does not; this
//! rung's `return 0` needs no chain, because `dig` is an owned `Vec` and the
//! compiler emits its `Drop` glue on every path out of the function -- the
//! early return included. There is no second spelling of "release it" to get
//! wrong, and no place a `goto` could aim at the wrong label. That is the whole
//! rung boundary this pattern measures.
//!
//! **The order of the allocation and the tag test is pinned** (../spec.md
//! `required[0]`): take the working storage, THEN parse. Hoisting the test
//! above the allocation is the ordinary way to make this class of bug
//! impossible in C too, and a rung that did it would not be a port of the C
//! rung, it would be the fix.
//!
//! `vec![0u8; len]` zeroes what it allocates and the C rung does not, because
//! safe Rust has no way to hand out uninitialised bytes. That cost is real,
//! it is R2's to pay, and R3 is where it is avoided without leaving the safe
//! subset. ../NOTES.md 5.
//!
//! The digest byte is `(run >> 24) as u8` in all six rungs. The shift is
//! load-bearing rather than decorative: `run` is a wrapping sum, so bits 0..7
//! of it depend only on bits 0..7 of the inputs -- and those carry the record
//! tag, which is constant on every well-formed window. `(run) as u8` would
//! therefore make the digest a function of `len` alone and the kernel would
//! stop reading its input. Measured, not argued: the first version of
//! `c/kernel.c` had it and `inputs/gen.py`'s data-dependence control is what
//! stands between the pattern and a constant-folded checksum (../NOTES.md 4).

#[path = "../../common/driver.rs"]
mod driver;

/// The low byte of a well-formed record header. ../spec.md "Payload layout".
const TAG: u64 = 0xA7;
/// The decode constant. Arbitrary and shared by all six rungs.
const MIX: u64 = 0x9E37_79B9_7F4A_7C15;
/// The driver's ceiling on the window length, and therefore on the digest
/// allocation. Outside the measured loop and carried by every rung; R5 needs it
/// to discharge `valid_layout`. See verus.rs's module comment.
const MAXWIN: u64 = 65536;

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md. `#[inline(never)]` only in `isolated` builds, so the
// `whole` builds can inline it the way LTO'd C would.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(v: &[u64], off: usize, len: usize) -> u64 {
    let mut dig: Vec<u8> = vec![0u8; len];
    if v[off] & 0xff != TAG {
        // The error path. `dig` is dropped here -- by the compiler, on the way
        // out, with nothing written down.
        return 0;
    }
    let mut run: u64 = 0;
    for i in 0..len {
        run = run.wrapping_add(v[off + i] ^ MIX);
        dig[i] = (run >> 24) as u8;
    }
    let mut acc: u64 = 0;
    for i in 0..len {
        acc = acc.wrapping_mul(31).wrapping_add(dig[len - 1 - i] as u64);
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
    if win_len_w > 0 && win_len_w <= MAXWIN && win_len_w <= n_vals as u64 {
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
