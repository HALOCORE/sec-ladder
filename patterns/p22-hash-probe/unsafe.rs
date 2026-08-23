//! p22 rung R4 -- unsafe.
//!
//! R2's algorithm with every window read and every table access spelled
//! unchecked. **What does NOT go away is `nfill < TABCAP`** -- that is not a
//! bounds check, it is the kernel's semantics (the hardened C cell folds SENT
//! once the table is full and ../spec.md pins that answer) and, uniquely in this
//! tree, it is also what makes the function TERMINATE. A rung without it would
//! be `c/kernel.c`'s bug written in Rust rather than an unsafe rung. This rung
//! is correct; it just has nothing checking that it is. R5 (verus.rs) is this
//! exec code with the SAFETY comments below turned into obligations a verifier
//! discharges -- **and with one obligation the comments cannot express, which is
//! the `decreases` on the probe loop.**
//!
//! **The table is indexed UNCHECKED here**, through `arr_get_unchecked` /
//! `arr_set_unchecked`, for uniformity with p27 and because that is what R5
//! needs to be byte-identical to. ⚠ Unlike p27, it is **worth nothing at
//! `-O3`**: `i` is `% TABCAP` with `TABCAP` a power-of-two constant, so rustc's
//! check on `tab[i]` is already dead in R2 and R3. The measured value of the
//! unchecked table spelling is `-O0`-only. ../NOTES.md 4 has the control and the
//! disassembly, and the number is published there rather than hidden in this
//! comment.
//!
//! SAFETY (1): `off + len <= buf.len()` is the caller's structural
//!   precondition. Unchecked here; discharged at the call site by Verus in
//!   verus.rs.
//! SAFETY (2): `len >= 4` guards the window header, so
//!   `off + 3 < off + len <= buf.len()`.
//! SAFETY (3): a key is read only under `len - p >= 1` with `p <= len`, so
//!   `off + p < off + len <= buf.len()`.
//! SAFETY (4): every table index is `% TABCAP`, so `i < TABCAP` holds on entry
//!   to the probe loop and after every step of it, unconditionally.
//! SAFETY (5): **the probe loop terminates.** `nfill < TABCAP` holds when it is
//!   entered, `nfill` is the number of non-EMPTY slots, and therefore some slot
//!   is EMPTY; the cursor visits distinct slots until it reaches one. ⚠ **This
//!   is the only SAFETY note in this project that is not about memory**, and it
//!   is the only one no `unsafe` block would have needed. Nothing in Rust checks
//!   it at any optimisation level, Miri does not check it, and the sanitizers do
//!   not check it. Verus does, and refuses to compile verus.rs without it:
//!   `error: loop must have a decreases clause`.

#[path = "../../common/driver.rs"]
mod driver;

/// The table's extent. Must equal `SLB_P22_TABCAP` in c/kernel.h and `TABCAP`
/// in model.py.
const TABCAP: usize = 64;

/// The EMPTY sentinel, and what a rejected key folds.
const EMPTY: u8 = 0;
const SENT: u64 = 251;

// The unchecked window read. Same accessor every unsafe rung in this project
// ships; in verus.rs it is trusted item 1 of 5.
#[inline(always)]
fn buf_get_unchecked(v: &[u8], i: usize) -> u8 {
    unsafe { *v.get_unchecked(i) }
}

// The unchecked TABLE read and store. verus.rs's trusted items 2 and 3.
#[inline(always)]
fn arr_get_unchecked<T: Copy, const N: usize>(v: &[T; N], i: usize) -> T {
    unsafe { *v.get_unchecked(i) }
}

#[inline(always)]
fn arr_set_unchecked<T: Copy, const N: usize>(v: &mut [T; N], i: usize, x: T) {
    unsafe {
        *v.get_unchecked_mut(i) = x;
    }
}

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    if len < 4 {
        return 0;
    }
    let nkey: usize = buf_get_unchecked(buf, off) as usize
        + 256 * (buf_get_unchecked(buf, off + 1) as usize)
        + 65536 * (buf_get_unchecked(buf, off + 2) as usize)
        + 16777216 * (buf_get_unchecked(buf, off + 3) as usize);
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
        let k: u8 = buf_get_unchecked(buf, off + p);
        p = p + 1;
        // >>> THE SAFETY LINE. `&& nfill < TABCAP` is what c/kernel.c omits,
        // and unsafe Rust does not supply it either. <<<
        if k != EMPTY && nfill < TABCAP {
            let mut i: usize = (k as usize) * 2654435761 / 16777216 % TABCAP;
            // THE PROBE LOOP. Unbounded by construction; it stops because some
            // slot is EMPTY, which is exactly what the conjunct above asserts.
            while arr_get_unchecked(&tab, i) != EMPTY && arr_get_unchecked(&tab, i) != k {
                i = (i + 1) % TABCAP;
            }
            if arr_get_unchecked(&tab, i) == EMPTY {
                arr_set_unchecked(&mut tab, i, k);
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
