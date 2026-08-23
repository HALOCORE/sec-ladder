//! p22 rung R2 -- safe Rust, naive. **NOT immune, and that is the pattern.**
//!
//! Every other pattern in this tree has the shape *C omits a bounds check, safe
//! Rust puts it back by construction, and the ladder prices the difference*.
//! p22 does not. The line `c/kernel.c` omits is
//!
//!     nfill < TABCAP
//!
//! and **no Rust rung gets it from the language.** It is not a bounds check: the
//! probe index is reduced modulo `TABCAP` on entry and on every step, so
//! `tab[i]` is in bounds in this rung and in `c/kernel.c` alike, and rustc's
//! bounds check on it is dead code LLVM removes. What `nfill < TABCAP` buys is
//! **termination**, and safety in the Rust sense says nothing about that.
//!
//! Delete the conjunct below and this file hangs on `adversarial-full.bin` at
//! `-O0` and at `-O3`, with **Miri silent** -- measured, at
//! `controls/gen_controls.py --run r2_noguard`, which builds exactly that file
//! from this one by an asserted single-string substitution. It is the closest
//! thing this project has to a control for *"what does safe Rust actually
//! buy?"*, and on this pattern the answer is *nothing*.
//!
//! The naive spelling: every access to the window and to the table is a
//! bounds-checked index, and the walk is a counted `while` over `t`. R3
//! reslices the window and iterates it; R4 uses `get_unchecked`; and the
//! difference between them is p22's safety column, which is an ordinary one and
//! has nothing to do with the bug.

#[path = "../../common/driver.rs"]
mod driver;

/// The table's extent. Must equal `SLB_P22_TABCAP` in c/kernel.h and `TABCAP`
/// in model.py.
const TABCAP: usize = 64;

/// The EMPTY sentinel, and what a rejected key folds.
const EMPTY: u8 = 0;
const SENT: u64 = 251;

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    if len < 4 {
        return 0;
    }
    let nkey: usize = buf[off] as usize + 256 * (buf[off + 1] as usize)
        + 65536 * (buf[off + 2] as usize) + 16777216 * (buf[off + 3] as usize);
    if nkey == 0 {
        return 0;
    }
    let mut tab: [u8; TABCAP] = [EMPTY; TABCAP];
    let mut nfill: usize = 0;
    let mut acc: u64 = 0;
    let mut p: usize = 4;
    let mut t: usize = 0;
    while t < nkey {
        if len - p < 1 {
            break;
        }
        let k: u8 = buf[off + p];
        p = p + 1;
        // >>> THE SAFETY LINE. `&& nfill < TABCAP` is what c/kernel.c omits,
        // and safe Rust does not supply it. <<<
        if k != EMPTY && nfill < TABCAP {
            let mut i: usize = (k as usize) * 2654435761 / 16777216 % TABCAP;
            // THE PROBE LOOP. Unbounded by construction; it stops because some
            // slot is EMPTY, which is exactly what the conjunct above asserts.
            while tab[i] != EMPTY && tab[i] != k {
                i = (i + 1) % TABCAP;
            }
            if tab[i] == EMPTY {
                tab[i] = k;
                nfill = nfill + 1;
            }
            acc = acc.wrapping_mul(31).wrapping_add(i as u64);
        } else {
            acc = acc.wrapping_mul(31).wrapping_add(SENT);
        }
        t = t + 1;
    }
    acc.wrapping_mul(31).wrapping_add(nfill as u64)
}

// ---------------------------------------------------------------- driver ----
fn main() {
    let path = driver::arg_path();
    let inp = driver::load(&path);
    let (stride_w, bytes) = driver::head1_u64_bytes(&inp);
    let n_iters: u64 = inp.n_iters;
    // SLB-DRIVER-BEGIN
    let n_blob: usize = bytes.len();
    let buf: &[u8] = bytes.as_slice();
    let mut acc: u64 = 0;
    if stride_w >= 4 && stride_w <= n_blob as u64 {
        let stride: usize = stride_w as usize;
        let nwin: u64 = (n_blob / stride) as u64;
        let mut it: u64 = 0;
        while it < n_iters {
            let k: usize = ((acc as u128 * nwin as u128) >> 64) as usize;
            let r: u64 = kernel(buf, k * stride, stride);
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    driver::emit(acc);
}
