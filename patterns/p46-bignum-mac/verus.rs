//! p46 rung R5 -- unsafe + Verus proof.
//!
//! R4's exec code verbatim, plus the specs and proofs that discharge every
//! unchecked access in it. **Two things are new here and neither is the bug
//! class.**
//!
//! **1. THE OBLIGATION IS A NONLINEAR FACT ABOUT DATA, NOT ABOUT AN ADDRESS.**
//! `lemma_mac_fits` proves `a*b + c + d <= 2^128 - 1` for u64 `a, b, c, d` --
//! exactly, since `(2^64-1)^2 + 2*(2^64-1) == 2^128 - 1` -- and that is what
//! licenses treating `t as u64` and `(t >> 64) as u64` as the low and high
//! limbs. Every other kernel-level `by (nonlinear_arith)` in this tree (p05,
//! p22, p38) bounds an INDEX; this one bounds a VALUE, and the values are the
//! attacker's. p46's own index arithmetic, `i + j`, is purely LINEAR -- which
//! is the precise sense in which p46 is the mirror image of p05 and not a
//! repeat of it.
//!
//! ⚠ **This is also the tree's first `by (bit_vector)` and first
//! `by (compute)` in executable position.** Counted, not asserted: 0 hits for
//! either across all 23 `patterns/*/verus.rs` before this file, and ten of them
//! carry a comment saying they deliberately avoid `bit_vector`. It is NOT a
//! stronger `ensures` than the tree has -- ../NOTES.md 6d counts 159 `ensures`
//! conjuncts of which 151 are equalities and all 23 kernels already carry a
//! full functional postcondition, so the claim that p46's `mac` clause is
//! *"stronger than any ensures currently in the tree, all of which are bounds
//! facts"* is **false and is not made here**.
//!
//! **2. THE HARDEST OBLIGATION IS NOT THE ONE THE RUNGS DIFFER ON.** The MAC's
//! no-overflow fact costs a lemma, a `nonlinear_arith`, a `compute` and a
//! `bit_vector` -- and **zero instructions at every rung**, because no rung
//! ever checks it and none has to. The obligation the rungs DO differ on,
//! `i + j < OUTCAP`, is trivial to prove and is what all three per-step bounds
//! checks cost money for. p46 separates proof burden from runtime cost inside
//! one kernel (../NOTES.md 6, 9).
//!
//! ⚠ **THE OBLIGATION IS EXACTLY WHAT `c/kernel.c` WALKS THROUGH.** That rung
//! is this program with the output-side bound deleted; the invariant
//! `n + m <= OUTCAP` then has no establishing step and the whole nest fails.
//! Demonstrated rather than argued: deleting those three lines from a copy of
//! this file gives `14 verified, 1 errors`, *"invariant not satisfied before
//! loop"* on `n + m <= OUTCAP` (../NOTES.md 6a).
//!
//! **What is NOT proved, said here rather than left implied.** The
//! postcondition is `r == bn_fold(buf@, off, len)`, where `bn_fold` is a
//! recursive specification of the schoolbook ALGORITHM. It is the same shape as
//! every other kernel's in this tree and it is a full functional postcondition.
//! It is **not** a proof that the limbs of `out` denote the mathematical
//! product `sum a_i b_j 2^(64(i+j))` -- that needs a limbs-to-`nat` valuation
//! and a nested partial-sum induction, and it was deliberately not attempted
//! (../NOTES.md 6b). What IS proved at the value level is the single MAC step:
//! `lo + hi*2^64 == a*b + c + carry`, exactly.
//!
//! TCB tally: ../NOTES.md 7. **Five** `external_body` items, **three** of them
//! with a contract.
//!
//! SAFETY (1): `off + len <= buf.len()` is the caller's structural
//!   precondition. Discharged at the call site by the driver's proof below.
//! SAFETY (2): `load_u64` reads `w[p .. p+8]` under `p + 8 <= w@.len()`.
//! SAFETY (3): `bl` is indexed by `j < m <= 255 < BCAP`.
//! SAFETY (4): **`out` is indexed by `i + j` under `n + m <= OUTCAP`**, the
//!   test the buggy C rung omits. This is the one.

// Plain-Rust I/O helpers. Outside `verus!`, so Verus treats the whole module as
// external (external-by-default). Reached only through `load_input`/`emit`.
#[path = "../../common/driver.rs"]
mod driver;

use vstd::prelude::*;
use vstd::slice::slice_subrange;

verus! {

// p46 targets x86-64 only (`.memory/00-environment.md`). Verus treats `usize`
// as architecture-independent by default, so `8 + 8 * (n + m)` and `off + len`
// would carry hypothetical 32-bit overflow obligations. This declaration is
// CHECKED by Verus against the actual compilation target rather than assumed,
// so it is not an axiom and adds nothing to the TCB.
global size_of usize == 8;

// `group_slice_axioms` gives `slice@.len() == spec_slice_len(slice)`, hence
// `slice@.len() <= usize::MAX` -- without it `off + len` cannot be shown not to
// overflow `usize`. `group_array_axioms` gives `out@.len() == OUTCAP` for a
// `[u64; OUTCAP]` and the fill axiom for `[0u64; OUTCAP]`.
// `lemma_u128_shr_is_div` turns `x >> 64` into `x / 2^64`, which the KERNEL
// needs here as well as the driver -- p46 is the first pattern whose kernel
// splits a 128-bit value. The mul group is what the driver's window-offset
// bound needs.
broadcast use {
    vstd::slice::group_slice_axioms,
    vstd::array::group_array_axioms,
    vstd::bits::lemma_u128_shr_is_div,
    vstd::arithmetic::mul::lemma_mul_inequality,
};

/// The product scratch capacity, in 64-bit limbs: the buffer the product has to
/// fit into. A compile-time constant in every rung.
///
/// A `const` inside `verus!` is its own obligation (`.memory/04-verus.md`,
/// measured on p08's `SCR`), so the three constants here contribute 3 to the
/// count pinned in ../spec.md.
pub const OUTCAP: usize = 96;

/// The b-operand scratch, in 64-bit limbs. Sized for the DECLARED TYPE's full
/// range (`m` is a byte), so the pre-decode can never leave it and the
/// pre-decode is not part of the bug.
pub const BCAP: usize = 256;

/// What an over-long product folds to. A compile-time constant in every rung.
pub const REJ: u64 = 0x9e37_79b9_7f4a_7c15;

// ------------------------------------------------------------------ spec ----
/// Little-endian limb decode, additively. The exec `load_u64` below is this
/// expression with the reads made unchecked.
pub open spec fn u64_at(w: Seq<u8>, p: int) -> u64 {
    (w[p] as int + 256 * (w[p + 1] as int) + 65536 * (w[p + 2] as int) + 16777216 * (
    w[p + 3] as int) + 4294967296 * (w[p + 4] as int) + 1099511627776 * (w[p + 5] as int)
        + 281474976710656 * (w[p + 6] as int) + 72057594037927936 * (w[p + 7] as int)) as u64
}

/// Limb `k` of the window: `a[0..n]` then `b[0..m]`, both after the 8-byte
/// header.
pub open spec fn limb(w: Seq<u8>, k: int) -> u64 {
    u64_at(w, 8 + 8 * k)
}

/// **THE VALUE THE MAC STEP COMPUTES**, in unbounded arithmetic. `lemma_mac_fits`
/// is the proof that it fits in 128 bits.
pub open spec fn mac_t(a: u64, b: u64, c: u64, k: u64) -> nat {
    (a as nat) * (b as nat) + (c as nat) + (k as nat)
}

/// The low limb of the step: the value modulo `2^64`.
pub open spec fn mac_lo(a: u64, b: u64, c: u64, k: u64) -> u64 {
    (mac_t(a, b, c, k) % 0x1_0000_0000_0000_0000nat) as u64
}

/// The carry out of the step: the value divided by `2^64`.
pub open spec fn mac_hi(a: u64, b: u64, c: u64, k: u64) -> u64 {
    (mac_t(a, b, c, k) / 0x1_0000_0000_0000_0000nat) as u64
}

/// One schoolbook ROW: `out[i..i+m] += a_i * b[0..m]`, carry propagated, the
/// final carry landing in `out[i+m]`. The abstract machine the inner loop
/// implements.
pub open spec fn row(
    w: Seq<u8>,
    n: int,
    m: int,
    ai: u64,
    out: Seq<u64>,
    i: int,
    j: int,
    carry: u64,
) -> Seq<u64>
    decreases m - j,
{
    if j >= m {
        out.update(i + m, carry)
    } else {
        let bj = limb(w, n + j);
        let c = out[i + j];
        row(
            w,
            n,
            m,
            ai,
            out.update(i + j, mac_lo(ai, bj, c, carry)),
            i,
            j + 1,
            mac_hi(ai, bj, c, carry),
        )
    }
}

/// All `n` rows. The abstract machine the outer loop implements.
pub open spec fn rows(w: Seq<u8>, n: int, m: int, out: Seq<u64>, i: int) -> Seq<u64>
    decreases n - i,
{
    if i >= n {
        out
    } else {
        rows(w, n, m, row(w, n, m, limb(w, i), out, i, 0, 0), i + 1)
    }
}

/// The checksum fold over the product limbs.
pub open spec fn ofold(out: Seq<u64>, k: int, kn: int, acc: u64) -> u64
    decreases kn - k,
{
    if k >= kn {
        acc
    } else {
        ofold(out, k + 1, kn, acc.wrapping_mul(31).wrapping_add(out[k]))
    }
}

/// The scratch as the kernel starts it: `OUTCAP` zero limbs.
pub open spec fn zeros() -> Seq<u64> {
    Seq::new(OUTCAP as nat, |j: int| 0u64)
}

/// What one window folds to. Total: every adversarial input is inside this
/// domain (../spec.md).
pub open spec fn window_fold(w: Seq<u8>) -> u64 {
    if w.len() < 8 {
        0
    } else {
        let n = w[0] as int;
        let m = w[1] as int;
        if n == 0 || m == 0 {
            0
        } else if 8 + 8 * (n + m) > w.len() {
            0
        } else if n + m > OUTCAP as int {
            REJ
        } else {
            ofold(rows(w, n, m, zeros(), 0), 0, n + m, 0).wrapping_mul(31).wrapping_add(
                n as u64,
            ).wrapping_mul(31).wrapping_add(m as u64)
        }
    }
}

/// What the kernel must return.
pub open spec fn bn_fold(buf: Seq<u8>, off: int, len: int) -> u64 {
    window_fold(buf.subrange(off, off + len))
}

// --------------------------------------------------------------- trusted ----
// TRUSTED ITEM 1 of 5. The unchecked byte read. vstd ships no specification for
// `<[T]>::get_unchecked` (0 hits at the pinned version), and the standard
// library's documented contract is exactly this `requires`/`ensures` pair.
#[inline(always)]
#[verifier::external_body]
fn buf_get_unchecked(v: &[u8], i: usize) -> (r: u8)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    unsafe { *v.get_unchecked(i) }
}

// THE VERIFIED TWIN of trusted item 1. Same signature, same contract, body the
// *checked* code: a `requires` too weak to license `*v.get_unchecked(i)` is too
// weak to license `v[i]`, and Verus can see the second one. `#[cfg(slb_twin)]`
// is a cfg no measured build ever sets, so rustc strips it before codegen.
#[cfg(slb_twin)]
fn slb_twin_buf_get_unchecked(v: &[u8], i: usize) -> (r: u8)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    v[i]
}

// TRUSTED ITEM 2 of 5. The unchecked limb read from a fixed-capacity array.
#[inline(always)]
#[verifier::external_body]
fn arr_get_unchecked<T: Copy, const N: usize>(v: &[T; N], i: usize) -> (r: T)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    unsafe { *v.get_unchecked(i) }
}

// THE VERIFIED TWIN of trusted item 2.
#[cfg(slb_twin)]
fn slb_twin_arr_get_unchecked<T: Copy, const N: usize>(v: &[T; N], i: usize) -> (r: T)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    v[i]
}

// TRUSTED ITEM 3 of 5. **The unchecked limb WRITE.** p46's out-of-bounds access
// is a write, which is what separates its bug from p05's read, and this is the
// item that licenses it.
#[inline(always)]
#[verifier::external_body]
fn arr_set_unchecked<T: Copy, const N: usize>(v: &mut [T; N], i: usize, x: T)
    requires
        i < old(v)@.len(),
    ensures
        final(v)@ == old(v)@.update(i as int, x),
{
    unsafe {
        *v.get_unchecked_mut(i) = x;
    }
}

// THE VERIFIED TWIN of trusted item 3.
#[cfg(slb_twin)]
fn slb_twin_arr_set_unchecked<T: Copy, const N: usize>(v: &mut [T; N], i: usize, x: T)
    requires
        i < old(v)@.len(),
    ensures
        final(v)@ == old(v)@.update(i as int, x),
{
    v[i] = x;
}

// TRUSTED ITEM 4 of 5. Argument parsing, file I/O and little-endian decoding,
// delegated to common/driver.rs so that all six rungs read the file the same
// way. It states **no** `ensures` at all, deliberately: an `ensures` here would
// be an axiom about the contents of a file, which nothing can justify. Every
// fact the proof needs is re-derived at run time from `bytes.len()` inside
// verified code. It contains no `unsafe`, so it stays outside the twin regime
// (`.memory/04-verus.md`: the regime is keyed on `external_body` + a non-empty
// `ensures` OR `unsafe`).
#[verifier::external_body]
fn load_input() -> (r: (u64, u64, Vec<u8>)) {
    let path = driver::arg_path();
    let inp = driver::load(&path);
    let (stride_w, bytes) = driver::head1_u64_bytes(&inp);
    (inp.n_iters, stride_w, bytes)
}

// TRUSTED ITEM 5 of 5. `println!` is not verifiable; no `ensures`. Counted with
// the four above -- every `external_body` item is TCB, not just the interesting
// one (`.memory/04-verus.md`).
#[verifier::external_body]
fn emit(acc: u64) {
    driver::emit(acc);
}

// ----------------------------------------------------------------- lemma ----
/// **THE LOAD-BEARING FACT, AND IT IS TIGHT**: for u64 `a, b, c, d`,
/// `a*b + c + d <= u128::MAX`, because
/// `(2^64-1)^2 + 2*(2^64-1) == 2^128 - 1` **exactly**. One more `+ 1` anywhere
/// and the schoolbook step would not fit in 128 bits and the whole algorithm
/// would need a third limb.
///
/// `by (nonlinear_arith)` for the product bound and `by (compute)` for the
/// 128-bit identity. Neither proof mode appears in any other pattern in this
/// tree (../NOTES.md 2).
pub proof fn lemma_mac_fits(a: u64, b: u64, c: u64, d: u64)
    ensures
        mac_t(a, b, c, d) <= u128::MAX as nat,
{
    assert((a as nat) * (b as nat) <= (u64::MAX as nat) * (u64::MAX as nat)) by (nonlinear_arith);
    assert((u64::MAX as nat) * (u64::MAX as nat) + (u64::MAX as nat) + (u64::MAX as nat)
        == u128::MAX as nat) by (compute);
}

// ------------------------------------------------------------------ exec ----
/// One schoolbook multiply-accumulate step, exact in 128 bits.
///
/// The postcondition is stated three ways on purpose: the first clause is the
/// VALUE-LEVEL identity a reader wants (`lo + hi*2^64 == a*b + c + carry`), and
/// the other two are the div/mod form the loop invariants are written in.
#[inline(always)]
fn mac(ai: u64, bj: u64, c: u64, carry: u64) -> (r: (u64, u64))
    ensures
        (r.0 as nat) + (r.1 as nat) * 0x1_0000_0000_0000_0000nat == mac_t(ai, bj, c, carry),
        r.0 == mac_lo(ai, bj, c, carry),
        r.1 == mac_hi(ai, bj, c, carry),
{
    proof {
        lemma_mac_fits(ai, bj, c, carry);
    }
    let t: u128 = (ai as u128) * (bj as u128) + (c as u128) + (carry as u128);
    // ⚠ BOTH casts need `#[verifier::truncate]`; without it Verus rejects the
    // narrowing rather than modelling it as `% 2^64`.
    let lo: u64 = #[verifier::truncate] (t as u64);
    let hi: u64 = #[verifier::truncate] ((t >> 64) as u64);
    // ⚠ THE SPELLING MATTERS: the `u128` + `requires` form below passes, and
    // the `nat`-cast form of the same identity FAILS `by (bit_vector)` --
    // measured at TASK_086, re-confirmed here.
    assert(t == (hi as u128) * 0x1_0000_0000_0000_0000u128 + (lo as u128)) by (bit_vector)
        requires
            lo == t as u64,
            hi == (t >> 64) as u64,
    ;
    proof {
        vstd::arithmetic::div_mod::lemma_fundamental_div_mod_converse(
            mac_t(ai, bj, c, carry) as int,
            0x1_0000_0000_0000_0000int,
            hi as int,
            lo as int,
        );
    }
    (lo, hi)
}

/// Little-endian limb decode, unchecked. The ADDITIVE spelling, byte-for-byte
/// the other rungs'.
#[inline(always)]
fn load_u64(w: &[u8], p: usize) -> (r: u64)
    requires
        p + 8 <= w@.len(),
    ensures
        r == u64_at(w@, p as int),
{
    assert(w@.len() == vstd::slice::spec_slice_len(w));
    buf_get_unchecked(w, p) as u64 + 256 * (buf_get_unchecked(w, p + 1) as u64) + 65536 * (
    buf_get_unchecked(w, p + 2) as u64) + 16777216 * (buf_get_unchecked(w, p + 3) as u64)
        + 4294967296 * (buf_get_unchecked(w, p + 4) as u64) + 1099511627776 * (
    buf_get_unchecked(w, p + 5) as u64) + 281474976710656 * (buf_get_unchecked(w, p + 6) as u64)
        + 72057594037927936 * (buf_get_unchecked(w, p + 7) as u64)
}

// ---------------------------------------------------------------- kernel ----
// Same exec code as unsafe.rs. Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> (r: u64)
    requires
        off + len <= buf@.len(),
    ensures
        r == bn_fold(buf@, off as int, len as int),
{
    // Ghost only: mentioning `spec_slice_len` fires vstd's `axiom_spec_len`,
    // which is what tells the SMT solver a slice length fits in a `usize`.
    assert(buf@.len() == vstd::slice::spec_slice_len(buf));
    if len < 8 {
        assert(buf@.subrange(off as int, off + len).len() < 8);
        return 0;
    }
    let w = slice_subrange(buf, off, off + len);
    let n: usize = buf_get_unchecked(w, 0) as usize;
    let m: usize = buf_get_unchecked(w, 1) as usize;
    if n == 0 || m == 0 {
        return 0;
    }
    if 8 + 8 * (n + m) > len {
        return 0;
    }
    // >>> THE SAFETY LINE, as an obligation. `c/kernel.c` is this program
    // without it, and without it the loop invariant `n + m <= OUTCAP` below has
    // no establishing step. <<<
    if n + m > OUTCAP {
        return REJ;
    }
    // ---- pre-decode the b operand, O(m). `bl` is sized by the TYPE of `m`. --
    let mut bl: [u64; BCAP] = [0u64; BCAP];
    let mut jd: usize = 0;
    while jd < m
        invariant
            0 <= jd <= m,
            1 <= n <= 255,
            1 <= m <= 255,
            n + m <= OUTCAP,
            w@.len() == len,
            8 + 8 * (n + m) <= len,
            bl@.len() == BCAP,
            forall|q: int| 0 <= q < jd ==> #[trigger] bl@[q] == limb(w@, n + q),
        decreases m - jd,
    {
        arr_set_unchecked(&mut bl, jd, load_u64(w, 8 + 8 * (n + jd)));
        jd = jd + 1;
    }
    // ---- the schoolbook nest. Every access unchecked, licensed by the test
    //      above; every MAC step exact, licensed by `lemma_mac_fits`. ---------
    let mut out: [u64; OUTCAP] = [0u64; OUTCAP];
    assert(out@ =~= zeros());
    let mut i: usize = 0;
    while i < n
        invariant
            0 <= i <= n,
            1 <= n <= 255,
            1 <= m <= 255,
            n + m <= OUTCAP,
            w@.len() == len,
            w@ == buf@.subrange(off as int, off + len),
            n == w@[0] as int,
            m == w@[1] as int,
            8 + 8 * (n + m) <= len,
            out@.len() == OUTCAP,
            bl@.len() == BCAP,
            forall|q: int| 0 <= q < m ==> #[trigger] bl@[q] == limb(w@, n + q),
            rows(w@, n as int, m as int, zeros(), 0) == rows(w@, n as int, m as int, out@, i as int),
        decreases n - i,
    {
        let ghost out0 = out@;
        let ai: u64 = load_u64(w, 8 + 8 * i);
        let mut carry: u64 = 0;
        let mut j: usize = 0;
        while j < m
            invariant
                0 <= j <= m,
                0 <= i < n,
                1 <= n <= 255,
                1 <= m <= 255,
                n + m <= OUTCAP,
                w@.len() == len,
                w@ == buf@.subrange(off as int, off + len),
                n == w@[0] as int,
                m == w@[1] as int,
                8 + 8 * (n + m) <= len,
                out@.len() == OUTCAP,
                bl@.len() == BCAP,
                forall|q: int| 0 <= q < m ==> #[trigger] bl@[q] == limb(w@, n + q),
                ai == limb(w@, i as int),
                row(w@, n as int, m as int, ai, out0, i as int, 0, 0) == row(
                    w@,
                    n as int,
                    m as int,
                    ai,
                    out@,
                    i as int,
                    j as int,
                    carry,
                ),
            decreases m - j,
        {
            let bj: u64 = arr_get_unchecked(&bl, j);
            // THE SAFETY LINE, as an obligation. `i <= n - 1` and `j <= m - 1`
            // are the loop conditions and `n + m <= OUTCAP` is the test
            // `c/kernel.c` omits, so `i + j <= n + m - 2 < OUTCAP`. Purely
            // LINEAR -- p05's counterpart is not, and that is the difference.
            let c: u64 = arr_get_unchecked(&out, i + j);
            let (lo, hi) = mac(ai, bj, c, carry);
            arr_set_unchecked(&mut out, i + j, lo);
            carry = hi;
            j = j + 1;
        }
        arr_set_unchecked(&mut out, i + m, carry);
        i = i + 1;
    }
    // ---- the checksum fold. -----------------------------------------------
    let mut acc: u64 = 0;
    let mut k: usize = 0;
    while k < n + m
        invariant
            0 <= k <= n + m,
            1 <= n <= 255,
            1 <= m <= 255,
            n + m <= OUTCAP,
            w@.len() == len,
            w@ == buf@.subrange(off as int, off + len),
            n == w@[0] as int,
            m == w@[1] as int,
            8 + 8 * (n + m) <= len,
            out@.len() == OUTCAP,
            out@ == rows(w@, n as int, m as int, zeros(), 0),
            ofold(out@, 0, (n + m) as int, 0) == ofold(out@, k as int, (n + m) as int, acc),
        decreases n + m - k,
    {
        acc = acc.wrapping_mul(31).wrapping_add(arr_get_unchecked(&out, k));
        k = k + 1;
    }
    acc.wrapping_mul(31).wrapping_add(n as u64).wrapping_mul(31).wrapping_add(m as u64)
}

// ---------------------------------------------------------------- driver ----
fn main() {
    let (n_iters, stride_w, bytes) = load_input();
    // SLB-DRIVER-BEGIN
    let n_blob: usize = bytes.len();
    let buf: &[u8] = bytes.as_slice();
    let mut acc: u64 = 0;
    if stride_w > 0 && stride_w <= n_blob as u64 {
        let stride: usize = stride_w as usize;
        let nwin: u64 = (n_blob / stride) as u64;
        let mut it: u64 = 0;
        // Ghost only: at least one whole window is present.
        proof {
            vstd::arithmetic::div_mod::lemma_div_non_zero(n_blob as int, stride as int);
        }
        while it < n_iters
            invariant
                1 <= stride <= n_blob,
                buf@.len() == n_blob,
                nwin == n_blob / stride,
                nwin >= 1,
            decreases n_iters - it,
        {
            // Ghost only: `k` must land inside the blob. Two nonlinear steps, so
            // Z3 needs both spelled out. Erases at compile time.
            proof {
                let pp: int = (acc as int) * (nwin as int);
                assert((acc as u128) * (nwin as u128) <= (u64::MAX as u128) * (u64::MAX
                    as u128)) by (nonlinear_arith)
                    requires
                        acc <= u64::MAX,
                        nwin <= u64::MAX,
                ;
                assert(vstd::arithmetic::power2::pow2(64) == 0x1_0000_0000_0000_0000nat) by {
                    vstd::arithmetic::power2::lemma2_to64_rest();
                }
                assert(pp < (nwin as int) * 0x1_0000_0000_0000_0000int) by (nonlinear_arith)
                    requires
                        pp == (acc as int) * (nwin as int),
                        acc <= u64::MAX,
                        nwin >= 1,
                ;
            }
            let k: usize = ((acc as u128 * nwin as u128) >> 64) as usize;
            // Ghost only: the window index `k` names a window that is entirely
            // present, so `k * stride + stride <= n_blob` and the kernel's
            // structural precondition is discharged. Both steps are nonlinear.
            proof {
                assert(k < nwin);
                vstd::arithmetic::div_mod::lemma_fundamental_div_mod(
                    n_blob as int,
                    stride as int,
                );
                assert((nwin as int) * (stride as int) <= n_blob as int);
                assert((k as int) * (stride as int) <= ((nwin as int) - 1) * (stride as int));
                assert(((nwin as int) - 1) * (stride as int) == (nwin as int) * (stride as int)
                    - (stride as int)) by (nonlinear_arith);
                assert((k as int) * (stride as int) + (stride as int) <= n_blob as int);
            }
            let r: u64 = kernel(buf, k * stride, stride);
            // Ghost only: this is what *consumes* the kernel's `ensures`.
            // Without it the postcondition is decoration -- deleting it entirely
            // still verifies, so nothing but mutation testing defends it
            // (`.memory/04-verus.md`). Ghost code erases, so the driver loop
            // stays byte-identical to R4's.
            assert(r == bn_fold(buf@, (k * stride) as int, stride as int));
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    emit(acc);
}

} // verus!
