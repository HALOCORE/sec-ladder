//! p22 rung R3 -- safe Rust, tuned. Still **zero** `unsafe`.
//!
//! Two levers, and both are about the WINDOW rather than about the table:
//!
//!   1. **one reslice** -- `&buf[off..off + len]` is bounds-checked once per
//!      call instead of once per key, so the header reads and the key reads are
//!      all against a slice whose length rustc already knows;
//!   2. **an iterator over the keys** -- `w[4..].iter().take(nkey)` yields
//!      exactly `min(nkey, len - 4)` bytes, which is the same set the naive
//!      rung's `t < nkey` / `len - p < 1` pair walks, with no per-key index.
//!
//! **There is no third lever, and the reason is the point of the pattern.** The
//! table index is `i % TABCAP` with `TABCAP` a power-of-two constant, so
//! `tab[i]` carries no live bounds check at `-O3` in ANY of the four Rust rungs
//! -- R2's, this one's and R4's `get_unchecked` all lower to the same load. The
//! only thing on this ladder that the table access costs is at `-O0`.
//! ../NOTES.md 4 has the disassembly.
//!
//! **And neither lever touches the bug.** `nfill < TABCAP` is written out below
//! exactly as it is in R2, R4, R5 and `c/kernel_hardened.c`. A `for _ in
//! 0..TABCAP` probe with a bounded trip count would ALSO make this rung
//! terminate on a full table, it is idiomatic safe Rust, and it is **not** what
//! ships: it is a different function (it finds a key that is present in a full
//! table, where the shipped semantics rejects every operation once the table is
//! full), it would put R3 out of step with the other five rungs, and it is
//! measured as a control instead -- `controls/gen_controls.py --run
//! r3_bounded`, ../NOTES.md 8.

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
    let w: &[u8] = &buf[off..off + len];
    let nkey: usize = w[0] as usize + 256 * (w[1] as usize) + 65536 * (w[2] as usize)
        + 16777216 * (w[3] as usize);
    if nkey == 0 {
        return 0;
    }
    let mut tab: [u8; TABCAP] = [EMPTY; TABCAP];
    let mut nfill: usize = 0;
    let mut acc: u64 = 0;
    for &k in w[4..].iter().take(nkey) {
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
