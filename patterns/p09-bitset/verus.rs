//! p09 rung R5 -- unsafe + Verus proof.
//!
//! R4's exec code verbatim, plus the specs and proofs that discharge every
//! unchecked read in it.
//!
//! **What is new here is that the safety check is not a bounds check.** Every
//! pattern before p09 guards a *range*: p16 `end - p >= 3`, p17 `start < end`,
//! p05 `i*ncol + j < avail`, p07 `lo < hi`, p11 `q < len`, p03 `sp > 0`. p09's
//! guard is
//!
//!     q < nbits
//!
//! and the *access* is `words[q >> 6]`. The bound the access needs --
//! `q >> 6 < nwords` -- is therefore **derived through a shift**, and neither
//! the guard nor the array length appears in it directly. That is p05's
//! question (`.memory/01-ladder.md` finding 6) on a **different operator**, and
//! it is the third data point after p03 showed the same class of failure is not
//! Rust-specific.
//!
//! **Z3 discharges it in three ghost lines with no new trusted item**:
//! `lemma_u64_shr_is_div` (broadcast) turns `>> 6` into `/ pow2(6)`,
//! `lemma2_to64()` evaluates `pow2(6)` to 64, and monotonicity of integer
//! division does the rest. NOTES.md 5 has the exact text and NOTES.md 4 what
//! LLVM does with the same fact.
//!
//!     requires  off + len <= buf@.len()
//!     ensures   r == bitset_fold(buf@, off as int, len as int)
//!
//! It is ONE clause, structural -- about the shape of the buffer the driver
//! built, not about its contents -- so it holds on *every* input this benchmark
//! runs, `adversarial-*` included, and the gate checks it call by call.
//! `nbits`, `nq` and every query word are attacker data and none of them is an
//! assumption.
//!
//! **THE SPECIFICATION IS WRITTEN IN DIVISION AND THE CODE IN SHIFTS, ON
//! PURPOSE.** `word_of(q)` is `q as int / 64` and `bit_of(q)` is
//! `(q as int % 64) as u64`; the exec code writes `q >> 6` and `q & 63`. So the
//! postcondition is not a transliteration of the code -- Verus has to *prove*
//! that the shift implements the division and that the mask implements the
//! remainder, and the two arithmetic bugs NOTES.md 6 builds (`q >> 5`,
//! `q & 31`) fail it for a semantic reason rather than because two copies of one
//! string differ. That is the strongest form of this pattern's second axis and
//! it is why the `forbidden` entry on `/ 64` costs zero instructions and still
//! buys something: a rung that spelled the exec side `q / 64` would need no
//! bridge at all.
//!
//! TCB tally: NOTES.md 5b. **Four `external_body` items, ONE of them `unsafe`**
//! -- and the interesting one is `popcount64`, which is *safe* and trusted only
//! because vstd ships no specification for `u64::count_ones`. p08's `copy_in` is
//! the precedent (`.memory/04-verus.md`: "trusted means unchecked by the
//! verifier, not unsafe"), but p09 is the first pattern where a trusted item
//! exists to model a **CPU instruction** rather than a memory operation.

use vstd::prelude::*;

// Plain-Rust I/O helpers. Outside `verus!`, so Verus treats the whole module as
// external (external-by-default). Reached only through `load_input`/`emit`.
#[path = "../../common/driver.rs"]
mod driver;

verus! {

// `group_slice_axioms` gives `slice@.len() == spec_slice_len(slice)`, hence
// `slice@.len() <= usize::MAX` -- without it `off + len` cannot be shown not to
// overflow `usize`. `lemma_u64_shr_is_div` is THE lemma of this pattern: it is
// what takes `q >> 6` to `q / 64`, and it is broadcast because both the index
// and the word count need it. `lemma_u128_shr_is_div` and the mul group are the
// driver's, exactly as on p03, p07 and p11; the KERNEL needs neither.
broadcast use {
    vstd::slice::group_slice_axioms,
    vstd::bits::lemma_u64_shr_is_div,
};

// ------------------------------------------------------------------ spec ----
/// The little-endian u32 at absolute byte position `p`, written out the way
/// every rung writes it: `b0 + 256*b1 + 65536*b2 + 16777216*b3`.
///
/// Spelled with `+` and `*` rather than `|` and `<<` on purpose
/// (`.memory/04-verus.md`): the two are the same function on bytes and compile
/// to the same instruction, but only the first is linear arithmetic.
#[verifier::opaque]
pub open spec fn u32_at(buf: Seq<u8>, p: int) -> u64 {
    (buf[p] as int + 256 * (buf[p + 1] as int) + 65536 * (buf[p + 2] as int) + 16777216 * (
    buf[p + 3] as int)) as u64
}

/// The little-endian u64 at absolute byte position `p`. Eight terms, written
/// out for the same reason as `u32_at` -- and because `from_le_bytes` and the
/// `try_into`/`TryFromSliceError` route to it are both `is not supported` at the
/// pinned vstd, so a rung that used one could not have an R4/R5 twin at all.
#[verifier::opaque]
pub open spec fn u64_at(buf: Seq<u8>, p: int) -> u64 {
    (buf[p] as int + 256 * (buf[p + 1] as int) + 65536 * (buf[p + 2] as int) + 16777216 * (
    buf[p + 3] as int) + 4294967296 * (buf[p + 4] as int) + 1099511627776 * (buf[p + 5] as int)
        + 281474976710656 * (buf[p + 6] as int) + 72057594037927936 * (buf[p + 7] as int)) as u64
}

/// How many 64-bit words hold `nbits` bits: `ceil(nbits / 64)`.
///
/// **Division, not a shift.** The exec code writes `(nbits + 63) >> 6`. Keeping
/// the specification in division is what makes "the shift implements the
/// division" an obligation rather than a tautology.
pub open spec fn nwords_of(nbits: u64) -> int {
    (nbits as int + 63) / 64
}

/// Which word holds bit `q`. The exec code writes `q >> 6`.
pub open spec fn word_of(q: u64) -> int {
    q as int / 64
}

/// Which bit of that word. The exec code writes `q & 63`.
pub open spec fn bit_of(q: u64) -> u64 {
    (q as int % 64) as u64
}

/// Population count, defined mathematically as the sum of the base-2 digits.
///
/// vstd ships **no** specification for `u64::count_ones` (checked by grep of
/// `vstd/std_specs/bits.rs`, which has only `trailing_zeros`/`leading_zeros`),
/// so this is the meaning `popcount64`'s trusted `ensures` claims and
/// `slb_twin_popcount64` implements in checked code.
pub open spec fn popcnt(x: u64) -> int
    decreases x,
{
    if x == 0 {
        0
    } else {
        (x % 2) as int + popcnt(x / 2)
    }
}

/// THE POPCOUNT PASS: words `i .. nwords`, folded.
///
/// Separate from the query walk on purpose. It reads every word unconditionally
/// and its index is `ws + 8*i` -- **linear in the loop counter, with no shift**
/// -- so it is the pattern's own negative control for the query loop's derived
/// bound. Same array, same byte-at-a-time assembly, same fold; the only
/// difference is where the index came from.
pub open spec fn wrun(buf: Seq<u8>, ws: int, i: int, nwords: int, acc: u64) -> u64
    decreases nwords - i,
{
    if i >= nwords {
        acc
    } else {
        wrun(
            buf,
            ws,
            i + 1,
            nwords,
            acc.wrapping_mul(31).wrapping_add(popcnt(u64_at(buf, ws + 8 * i)) as u64),
        )
    }
}

/// THE QUERY WALK: queries `k .. nq`, carrying the accumulator and the hit
/// count, and finishing into the popcount pass.
///
/// This is the one function whose *shape* R1 does not implement. R1 has no
/// `q < nbits` test, so its `q >> 6` can name any word index up to 2^26 and the
/// read lands arbitrarily far past the blob -- an index this specification
/// cannot express, because `Seq::index` outside `0 .. len` is unspecified.
pub open spec fn qrun(
    buf: Seq<u8>,
    ws: int,
    qs: int,
    k: int,
    nq: int,
    nbits: u64,
    acc: u64,
    hits: u64,
) -> u64
    decreases nq - k,
{
    if k >= nq {
        wrun(buf, ws, 0, nwords_of(nbits), acc.wrapping_mul(31).wrapping_add(hits))
    } else {
        let q = u32_at(buf, qs + 4 * k);
        if q < nbits {
            let w = u64_at(buf, ws + 8 * word_of(q));
            qrun(
                buf,
                ws,
                qs,
                k + 1,
                nq,
                nbits,
                acc.wrapping_mul(31).wrapping_add(w),
                if w & (1u64 << bit_of(q)) != 0 {
                    hits.wrapping_add(1)
                } else {
                    hits
                },
            )
        } else {
            qrun(buf, ws, qs, k + 1, nq, nbits, acc, hits)
        }
    }
}

/// What the kernel returns.
///
/// The four early exits are the tests every rung keeps, R1 included: a window
/// too short to hold the header, a zero bit count, a zero query count, and a
/// declared shape the window cannot hold. **R1 keeps all four.** What R1 omits
/// is the `q < nbits` arm of `qrun`, and that is the only thing it omits.
pub open spec fn bitset_fold(buf: Seq<u8>, off: int, len: int) -> u64 {
    if len < 8 {
        0
    } else if u32_at(buf, off) == 0 || u32_at(buf, off + 4) == 0 {
        0
    } else if 8 * nwords_of(u32_at(buf, off)) + 4 * (u32_at(buf, off + 4) as int) > len - 8 {
        0
    } else {
        let nbits = u32_at(buf, off);
        let nq = u32_at(buf, off + 4);
        let acc = qrun(
            buf,
            off + 8,
            off + 8 + 8 * nwords_of(nbits),
            0,
            nq as int,
            nbits,
            0,
            0,
        );
        acc.wrapping_mul(31).wrapping_add(nbits).wrapping_mul(31).wrapping_add(nq)
    }
}

// ------------------------------------------------------------------ proof ---
/// `q & 63 == q % 64`, the bridge the MASK spelling needs.
///
/// vstd's `lemma_u64_low_bits_mask_is_mod` is `broadcast`, but its trigger is
/// `x & (low_bits_mask(n) as u64)` and nothing makes Z3 see the literal `63` as
/// `low_bits_mask(6)`, so the lemma has to be called by hand.
pub proof fn lemma_and63_is_mod64(q: u64)
    ensures
        (q & 63) == q % 64,
        (q & 63) == bit_of(q),
        (q & 63) < 64,
{
    assert(vstd::bits::low_bits_mask(6) == 0x3f) by {
        vstd::bits::lemma_low_bits_mask_values();
    }
    assert(vstd::arithmetic::power2::pow2(6) == 64) by {
        vstd::arithmetic::power2::lemma2_to64();
    }
    vstd::bits::lemma_u64_low_bits_mask_is_mod(q, 6);
}

/// `x >> 6 == x / 64`, the bridge the INDEX spelling needs. One line of vstd
/// plus the evaluation of `pow2(6)`; `lemma_u64_shr_is_div` is broadcast above,
/// so all this does is put `pow2(6) == 64` in scope.
pub proof fn lemma_shr6_is_div64(x: u64)
    ensures
        (x >> 6) == x as int / 64,
{
    assert(vstd::arithmetic::power2::pow2(6) == 64) by {
        vstd::arithmetic::power2::lemma2_to64();
    }
}

/// **THE OBLIGATION THE PATTERN IS ABOUT.** The guard is on the bit index and
/// the access is on the word index, so this is the whole memory-safety step.
pub proof fn lemma_guard_bounds_word(q: u64, nbits: u64)
    requires
        q < nbits,
    ensures
        (q >> 6) == word_of(q),
        (q >> 6) < nwords_of(nbits),
{
    lemma_shr6_is_div64(q);
}

/// `popcnt` is non-negative and bounded by its argument. `popcnt(x) <= 64` is
/// the tight bound and is NOT provable by this induction (it would need the
/// bit width as a parameter); `popcnt(x) <= x` is, and it is all the twin needs.
pub proof fn lemma_popcnt_le(x: u64)
    ensures
        0 <= popcnt(x) <= x,
    decreases x,
{
    if x != 0 {
        lemma_popcnt_le(x / 2);
    }
}

/// A non-zero word has at least one bit set.
pub proof fn lemma_popcnt_pos(x: u64)
    requires
        x != 0,
    ensures
        popcnt(x) >= 1,
    decreases x,
{
    if x % 2 == 0 {
        assert(x >= 2);
        assert(x / 2 >= 1);
        lemma_popcnt_pos(x / 2);
    } else {
        lemma_popcnt_le(x / 2);
    }
}

// ------------------------------------------------------------------- TCB ----
// TRUSTED ITEM 1 of 4. vstd ships no specification for `<[T]>::get_unchecked`,
// so this is the axiom that licenses every unchecked read. It is sound because
// the standard library's documented contract for `get_unchecked` is exactly
// this: if the caller guarantees `i < v.len()`, the call is defined and yields
// `v[i]`. Identical, character for character, to the accessor p01, p02, p03,
// p05, p07, p11, p16 and p17 ship.
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

// THE VERIFIED TWIN of trusted item 1 (`harness/check.py` step 5c-twin). Same
// signature and same contract, character for character, implemented in
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

// TRUSTED ITEM 2 of 4, and the first trusted item in this project that models a
// **CPU instruction** rather than a memory operation. It contains no `unsafe`
// and it is not dangerous; it is trusted because vstd ships no specification for
// `u64::count_ones` (`vstd/std_specs/bits.rs` has `trailing_zeros` and
// `leading_zeros` and nothing else), exactly as p08's `copy_in` is trusted for
// wrapping a perfectly safe `copy_from_slice`.
//
// Its `ensures` is the mathematical definition of population count, so the
// axiom it introduces is "`u64::count_ones` returns the number of set bits" --
// which is the documented contract of the function. The twin below is the proof
// that a program CAN meet it.
#[inline(always)]
#[verifier::external_body]
fn popcount64(x: u64) -> (r: u64)
    ensures
        r == popcnt(x),
{
    x.count_ones() as u64
}

// THE VERIFIED TWIN of trusted item 2. Written with `/ 2` and `% 2` so it is a
// direct implementation of `popcnt` rather than a second bit-twiddling program
// that would need its own bridge.
#[cfg(slb_twin)]
fn slb_twin_popcount64(x: u64) -> (r: u64)
    ensures
        r == popcnt(x),
{
    let mut y: u64 = x;
    let mut c: u64 = 0;
    proof {
        lemma_popcnt_le(x);
    }
    while y != 0
        invariant
            c + popcnt(y) == popcnt(x),
            popcnt(x) <= x,
            popcnt(y) >= 0,
        decreases y,
    {
        proof {
            lemma_popcnt_le(y / 2);
            lemma_popcnt_pos(y);
        }
        c = c + y % 2;
        y = y / 2;
    }
    c
}

// TRUSTED ITEM 3 of 4. Argument parsing, file I/O and little-endian decoding,
// delegated to common/driver.rs so that all six rungs read the file the same
// way. It states **no** `ensures` at all, deliberately: an `ensures` here would
// be an axiom about the contents of a file, which nothing can justify. It
// contains no `unsafe`, so it stays outside the twin regime.
#[verifier::external_body]
fn load_input() -> (r: (u64, u64, Vec<u8>)) {
    let path = driver::arg_path();
    let inp = driver::load(&path);
    let (stride_w, bytes) = driver::head1_u64_bytes(&inp);
    (inp.n_iters, stride_w, bytes)
}

// TRUSTED ITEM 4 of 4. `println!` is not verifiable; no `ensures`.
#[verifier::external_body]
fn emit(acc: u64) {
    driver::emit(acc);
}

// --------------------------------------------------------------- decoders ---
// The two little-endian decoders, shared by both loops. Verified, not trusted.
#[inline(always)]
fn load_u32(buf: &[u8], p: usize) -> (r: u64)
    requires
        p + 4 <= buf@.len(),
    ensures
        r == u32_at(buf@, p as int),
        r <= 0xffff_ffff,
{
    reveal(u32_at);
    assert(buf@.len() == vstd::slice::spec_slice_len(buf));
    buf_get_unchecked(buf, p) as u64 + 256 * (buf_get_unchecked(buf, p + 1) as u64) + 65536 * (
    buf_get_unchecked(buf, p + 2) as u64) + 16777216 * (buf_get_unchecked(buf, p + 3) as u64)
}

#[inline(always)]
fn load_u64(buf: &[u8], p: usize) -> (r: u64)
    requires
        p + 8 <= buf@.len(),
    ensures
        r == u64_at(buf@, p as int),
{
    reveal(u64_at);
    assert(buf@.len() == vstd::slice::spec_slice_len(buf));
    buf_get_unchecked(buf, p) as u64 + 256 * (buf_get_unchecked(buf, p + 1) as u64) + 65536 * (
    buf_get_unchecked(buf, p + 2) as u64) + 16777216 * (buf_get_unchecked(buf, p + 3) as u64)
        + 4294967296 * (buf_get_unchecked(buf, p + 4) as u64) + 1099511627776 * (
    buf_get_unchecked(buf, p + 5) as u64) + 281474976710656 * (buf_get_unchecked(buf, p + 6)
        as u64) + 72057594037927936 * (buf_get_unchecked(buf, p + 7) as u64)
}

// ---------------------------------------------------------------- kernel ----
// Same exec code as unsafe.rs. Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> (r: u64)
    requires
        off + len <= buf@.len(),
    ensures
        r == bitset_fold(buf@, off as int, len as int),
{
    // Ghost only: mentioning `spec_slice_len` fires vstd's `axiom_spec_len`,
    // which is what tells the SMT solver a slice length fits in a `usize`.
    assert(buf@.len() == vstd::slice::spec_slice_len(buf));
    if len < 8 {
        return 0;
    }
    let nbits: u64 = load_u32(buf, off);
    let nq: u64 = load_u32(buf, off + 4);
    if nbits == 0 || nq == 0 {
        return 0;
    }
    let nwords: u64 = (nbits + 63) >> 6;
    // Ghost only: the exec `>> 6` is the spec's `/ 64`.
    proof {
        lemma_shr6_is_div64((nbits + 63) as u64);
    }
    if 8 * nwords + 4 * nq > (len - 8) as u64 {
        return 0;
    }
    let ws: usize = off + 8;
    let qs: usize = ws + (8 * nwords) as usize;
    let mut acc: u64 = 0;
    let mut hits: u64 = 0;
    let mut k: u64 = 0;
    // "The queries from here, with the accumulator and the hit count we have,
    // are the whole walk." p16's, p03's, p07's and p11's relational shape.
    while k < nq
        invariant
            k <= nq,
            8 <= len,
            nwords == nwords_of(nbits),
            8 * nwords + 4 * nq <= len - 8,
            nbits == u32_at(buf@, off as int),
            nq == u32_at(buf@, off + 4),
            nbits > 0,
            nq > 0,
            nq <= 0xffff_ffff,
            ws == off + 8,
            qs == ws + 8 * nwords,
            off + len <= buf@.len(),
            buf@.len() <= usize::MAX,
            qrun(buf@, ws as int, qs as int, k as int, nq as int, nbits, acc, hits) == qrun(
                buf@,
                ws as int,
                qs as int,
                0,
                nq as int,
                nbits,
                0,
                0,
            ),
        decreases nq - k,
    {
        let q: u64 = load_u32(buf, qs + (4 * k) as usize);
        if q < nbits {
            // Ghost only: THE STEP. `q < nbits` is a fact about the BIT index;
            // the access needs a fact about the WORD index, and the two are a
            // shift apart. NOTES.md 5.
            proof {
                lemma_guard_bounds_word(q, nbits);
                lemma_and63_is_mod64(q);
            }
            let w: u64 = load_u64(buf, ws + (8 * (q >> 6)) as usize);
            if w & (1u64 << (q & 63)) != 0 {
                hits = hits.wrapping_add(1);
            }
            acc = acc.wrapping_mul(31).wrapping_add(w);
        }
        k = k + 1;
    }
    acc = acc.wrapping_mul(31).wrapping_add(hits);
    let mut i: u64 = 0;
    // THE POPCOUNT PASS. Its index is linear in `i` -- no shift, no guard, no
    // derived bound. It is the control for the loop above.
    while i < nwords
        invariant
            i <= nwords,
            8 <= len,
            nwords == nwords_of(nbits),
            8 * nwords + 4 * nq <= len - 8,
            nbits == u32_at(buf@, off as int),
            nq == u32_at(buf@, off + 4),
            nbits > 0,
            nq > 0,
            ws == off + 8,
            off + len <= buf@.len(),
            buf@.len() <= usize::MAX,
            wrun(buf@, ws as int, i as int, nwords as int, acc) == qrun(
                buf@,
                ws as int,
                (ws + 8 * nwords) as int,
                0,
                nq as int,
                nbits,
                0,
                0,
            ),
        decreases nwords - i,
    {
        let w: u64 = load_u64(buf, ws + (8 * i) as usize);
        acc = acc.wrapping_mul(31).wrapping_add(popcount64(w));
        i = i + 1;
    }
    acc.wrapping_mul(31).wrapping_add(nbits).wrapping_mul(31).wrapping_add(nq)
}

// ---------------------------------------------------------------- driver ----
fn main() {
    let (n_iters, stride_w, bytes) = load_input();
    // SLB-DRIVER-BEGIN
    let n_blob: usize = bytes.len();
    let buf: &[u8] = bytes.as_slice();
    let mut acc: u64 = 0;
    if stride_w >= 8 && stride_w <= n_blob as u64 {
        let stride: usize = stride_w as usize;
        let nwin: u64 = (n_blob / stride) as u64;
        let mut it: u64 = 0;
        // Ghost only: at least one whole window is present.
        proof {
            vstd::arithmetic::div_mod::lemma_div_non_zero(n_blob as int, stride as int);
        }
        while it < n_iters
            invariant
                8 <= stride <= n_blob,
                buf@.len() == n_blob,
                nwin == n_blob / stride,
                nwin >= 1,
            decreases n_iters - it,
        {
            // Ghost only: `k` must land inside the blob. Two nonlinear steps.
            proof {
                // Scoped to the DRIVER's loop body. `lemma_u128_shr_is_div` is
                // what the multiply-shift barrier needs and
                // `lemma_mul_inequality` what the window-offset bound needs;
                // broadcasting either at FILE scope pushes the KERNEL's query
                // loop past the solver's rlimit (NOTES.md 5c) -- that loop
                // multiplies by variables in a way p03's did not.
                broadcast use {
                    vstd::bits::lemma_u128_shr_is_div,
                    vstd::arithmetic::mul::lemma_mul_inequality,
                };

                let p: int = (acc as int) * (nwin as int);
                assert((acc as u128) * (nwin as u128) <= (u64::MAX as u128) * (u64::MAX
                    as u128)) by (nonlinear_arith)
                    requires
                        acc <= u64::MAX,
                        nwin <= u64::MAX,
                ;
                assert(vstd::arithmetic::power2::pow2(64) == 0x1_0000_0000_0000_0000nat) by {
                    vstd::arithmetic::power2::lemma2_to64_rest();
                }
                assert(p < (nwin as int) * 0x1_0000_0000_0000_0000int) by (nonlinear_arith)
                    requires
                        p == (acc as int) * (nwin as int),
                        acc <= u64::MAX,
                        nwin >= 1,
                ;
            }
            let k: usize = ((acc as u128 * nwin as u128) >> 64) as usize;
            // Ghost only: the window index `k` names a window that is entirely
            // present, so the kernel's structural precondition is discharged.
            proof {
                broadcast use {
                    vstd::bits::lemma_u128_shr_is_div,
                    vstd::arithmetic::mul::lemma_mul_inequality,
                };

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
            assert(r == bitset_fold(buf@, (k * stride) as int, stride as int));
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    emit(acc);
}

} // verus!
