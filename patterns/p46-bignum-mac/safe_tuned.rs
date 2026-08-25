//! p46 rung R3 -- safe Rust, tuned. **This is the rung the pattern is for, and
//! it is the rung that beats the unsafe one.**
//!
//! One lever, zero `unsafe`, zero trusted items: walk the output row and the b
//! operand as ITERATORS instead of indexing them.
//!
//!     for (o, &bj) in out[i..i + m].iter_mut().zip(bl[..m].iter()) { ... }   // R3
//!     while j < m { ... bl[j] ... out[i + j] ... }                           // R2
//!
//! ⚠⚠ **THAT LEVER IS A SPELLING AND NOT AN ASYMPTOTIC, AND THE PARAGRAPH
//! THAT SAID OTHERWISE IS RETRACTED** (TASK_089_REVIEW M2, re-derived at
//! TASK_092). It used to read *"the reslice `out[i..i + m]` is one bounds check
//! per ROW -- `O(n)` -- where R2 pays three per MAC step, `O(n*m)`; that
//! asymptotic change is the whole lever."* **There is no such check in either
//! rung's machine code.** The two safe rungs have the *identical*
//! conditional-branch multiset -- `ja:2 jae:2 jb:1 jbe:1 je:6 jne:5`, plus
//! `jmp:6` on both, from
//! `harness/asm.py show <cell>-O3-isolated | grep -oE '^j[a-z]+' | sort | uniq -c`
//! run on both binaries -- and R2's three per-step checks were already gone
//! (../NOTES.md 0b, 8a).
//!
//! What the measured `R3 - R2 = 2n - 2` (m even) / `-2` (m odd) actually is:
//! **address arithmetic.** This rung hoists the row base `lea (%rsp,%r13,8),%r8
//! ; add $0x8,%r8` into the row header, +2 instructions per row; `safe_naive`
//! computes the same base inside its ODD-`m` remainder block, which is exactly
//! why the law has two branches on `m` parity -- when `m` is odd the two
//! cancel, when `m` is even only this rung pays. The `-2` is a once-per-call
//! `lea`/`add` pair this rung does not need. Derived from both sides in
//! ../NOTES.md 8e, and checked by one committed command --
//! `controls/sweep_ir.py --check`, which re-derives the law over **48 sweep
//! blobs, max |residual| 0.00000**, and exits non-zero on any residual.
//!
//! ⚠⚠ **AND IT MAKES SAFE RUST CHEAPER THAN THE UNSAFE RUNG. READ THE NEXT
//! PARAGRAPH BEFORE QUOTING THAT.**
//!
//! ⚠⚠ **NONE OF IT IS SAFETY, AND THE R4 SIDE WAS SEARCHED FIRST**
//! (`.memory/01-ladder.md`; the p10/p27/p38/p22 trap). Three admissible R4
//! spellings and three R3 spellings were measured **on the shipped shape**, on
//! five shapes of the shipped sweep band, from `controls/mkvariants.py`'s
//! output built with the shipped flag set; both sides are flat and degenerate
//! (../NOTES.md 8b).
//! ⚠ An earlier version of this paragraph cited a *"2x2 `(n, m)` grid"* -- that
//! was `.temp/t89/cost.rs`, the PRE-BUILD probe whose slope ../NOTES.md 0b
//! retracts, and it is not a p46 measurement.
//!
//! **The cheapest unsafe spelling found** -- a checked per-row reslice with
//! unchecked indexing inside it, `r4_mutreslice` -- is `1.5` Ir/MAC cheaper
//! than **R4** (against this rung, `1.0`), and it is **still not an admissible
//! R4**, but ⚠ **NOT for the reason this comment used to give.** It said the
//! pinned vstd cannot specify a mutable sub-slice. It can, at the value level
//! (`~/tools/verus/vstd/std_specs/slice.rs`), and its **full R5 verifies,
//! `21 verified, 0 errors`.** What disqualifies it is measured instead: it
//! needs **two new trusted items** (the pinned vstd has zero `get_unchecked`
//! specifications anywhere), and its R4/R5 pair is `differ` at `-O3` --
//! `R5 - R4 = 15n + 1` Ir/call -- against this pattern's pinned
//! `identity: unsafe == verus, O3 exact`. ../NOTES.md 0c has all of it.
//!
//! So p46's "safe beats unsafe" is still `.memory/01-ladder.md` finding 14's
//! shape -- *the unsafe class is chained to the prover* -- but the chain here
//! is the **TCB and the identity pin**, not a missing specification, and
//! ../NOTES.md 0c says what happens to this rung's headline if either is
//! relaxed.

#[path = "../../common/driver.rs"]
mod driver;

/// The product scratch capacity, in 64-bit limbs. Must equal
/// `SLB_P46_OUTCAP` in c/kernel.h and `OUTCAP` in model.py.
const OUTCAP: usize = 96;

/// The b-operand scratch, in 64-bit limbs. Sized for the DECLARED TYPE's full
/// range (`m` is a byte), so the pre-decode below can never leave it.
const BCAP: usize = 256;

/// What an over-long product folds to.
const REJ: u64 = 0x9e37_79b9_7f4a_7c15;

/// Little-endian limb decode. Byte-for-byte R2's, so that the ONLY difference
/// between the two safe rungs is the MAC loop's addressing.
#[inline(always)]
fn ld64(w: &[u8], p: usize) -> u64 {
    w[p] as u64 + 256 * (w[p + 1] as u64) + 65536 * (w[p + 2] as u64)
        + 16777216 * (w[p + 3] as u64) + 4294967296 * (w[p + 4] as u64)
        + 1099511627776 * (w[p + 5] as u64) + 281474976710656 * (w[p + 6] as u64)
        + 72057594037927936 * (w[p + 7] as u64)
}

/// p46's kernel. Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    if len < 8 {
        return 0;
    }
    let w: &[u8] = &buf[off..off + len];
    let n: usize = w[0] as usize;
    let m: usize = w[1] as usize;
    if n == 0 || m == 0 {
        return 0;
    }
    if 8 + 8 * (n + m) > len {
        return 0;
    }
    // >>> THE SAFETY LINE. c/kernel.c omits this test. <<<
    if n + m > OUTCAP {
        return REJ;
    }
    let mut bl: [u64; BCAP] = [0u64; BCAP];
    let mut jd: usize = 0;
    while jd < m {
        bl[jd] = ld64(w, 8 + 8 * (n + jd));
        jd = jd + 1;
    }
    let mut out: [u64; OUTCAP] = [0u64; OUTCAP];
    let bs: &[u64] = &bl[0..m];
    let mut i: usize = 0;
    while i < n {
        let ai: u64 = ld64(w, 8 + 8 * i);
        let mut carry: u64 = 0;
        for (o, &bj) in out[i..i + m].iter_mut().zip(bs.iter()) {
            let t: u128 = (ai as u128) * (bj as u128) + (*o as u128) + (carry as u128);
            *o = t as u64;
            carry = (t >> 64) as u64;
        }
        out[i + m] = carry;
        i = i + 1;
    }
    let mut acc: u64 = 0;
    let mut k: usize = 0;
    while k < n + m {
        acc = acc.wrapping_mul(31).wrapping_add(out[k]);
        k = k + 1;
    }
    acc.wrapping_mul(31).wrapping_add(n as u64).wrapping_mul(31).wrapping_add(m as u64)
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
    if stride_w > 0 && stride_w <= n_blob as u64 {
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
