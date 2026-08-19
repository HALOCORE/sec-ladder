//! p07 rung R5 -- unsafe + Verus proof.
//!
//! R4's exec code verbatim, plus the specs and proofs that discharge every
//! unchecked read in it.
//!
//! **What is new here is the control flow, not the arithmetic.** p05's index is
//! `i*ncol + j` -- a product of two *variables* -- so its proof needs
//! `lemma_mul_inequality` and two `by (nonlinear_arith)` blocks. Every
//! multiplication in p07 is by the literal 4, so every index obligation is
//! linear and Z3 discharges it for free. What p07 pays instead is:
//!
//!   * a loop with a `break`, so `invariant_except_break` + a loop `ensures`
//!     (p16's shape, `.memory/04-verus.md`); and
//!   * an invariant that cannot be a closed form. There is no formula for where
//!     a binary search will be after `i` steps -- the path is the data -- so the
//!     invariant is the same "*the search from here is the whole search*" shape
//!     p16 found for its walk: `bsearch(lo, hi) == bsearch(0, n)`.
//!
//! **And the `requires` is one clause, exactly as p05's.** The kernel is total
//! in `n`, `nq`, every element and every query value -- all of them attacker
//! data, none of them assumptions:
//!
//!     off + len <= buf@.len()
//!
//! It is structural -- about the shape of the buffer the driver built, not
//! about its contents -- so it holds on *every* input this benchmark runs,
//! `adversarial-*` included, and the gate checks it call by call.
//!
//! Note what the spec does **not** assume: that the elements are sorted.
//! `bsearch` is defined as the *program's* search, not as "the index of `key`",
//! so `adversarial-unsorted.bin` is inside the verified domain and the kernel
//! agrees with `model.py` on it. Sortedness is a property of the file, and a
//! `requires` about it would be a precondition no honest loader could
//! discharge (`.memory/02-bench-rules.md`). A functional spec that said "finds
//! the key iff it is present" would need sortedness and would have made the
//! adversarial row unverifiable; this one states what the search returns.
//!
//! p17 needed a second clause, `buf@.len() <= i64::MAX`, because it cast to
//! `i64` and vstd has no axiom that a slice is at most `isize::MAX` bytes. p07
//! is unsigned end to end, so that clause would constrain nothing this proof
//! uses and it is deliberately absent -- along with the driver conjunct that
//! discharged it.
//!
//! TCB tally: NOTES.md 5. Three `external_body` items, all listed there
//! individually, because an under-counted TCB is how the pilot's fatal defect
//! hid in plain sight (`.memory/04-verus.md`).

use vstd::prelude::*;

// Plain-Rust I/O helpers. Outside `verus!`, so Verus treats the whole module as
// external (external-by-default). Reached only through `load_input`/`emit`.
#[path = "../../common/driver.rs"]
mod driver;

verus! {

// `group_slice_axioms` gives `slice@.len() == spec_slice_len(slice)`, hence
// `slice@.len() <= usize::MAX` -- without it `off + len` cannot be shown not to
// overflow `usize`. `lemma_u128_shr_is_div` turns `x >> 64` into `x / 2^64`,
// which is what the driver's multiply-shift barrier bound is about. The mul
// group is what the driver's window-offset bound `k * stride + stride <= n_blob`
// needs; the KERNEL needs none of it, which is p07's difference from p05.
broadcast use {
    vstd::slice::group_slice_axioms,
    vstd::bits::lemma_u128_shr_is_div,
    vstd::arithmetic::mul::lemma_mul_inequality,
};

// ------------------------------------------------------------------ spec ----
/// The little-endian u32 at absolute byte position `p`, written out the way
/// every rung writes it: `b0 + 256*b1 + 65536*b2 + 16777216*b3`.
///
/// Spelled with `+` and `*` rather than `|` and `<<` on purpose
/// (`.memory/04-verus.md`): the two are the same function on bytes and compile
/// to the same instruction, but only the first is linear arithmetic. The
/// alternative drags in `by (bit_vector)` for no gain.
pub open spec fn u32_at(buf: Seq<u8>, p: int) -> int {
    buf[p] as int + 256 * (buf[p + 1] as int) + 65536 * (buf[p + 2] as int)
        + 16777216 * (buf[p + 3] as int)
}

/// How many elements the window at `off` declares: a little-endian u32 at
/// window bytes 0..4. Declared, not derived -- that is the pattern.
pub open spec fn n_at(buf: Seq<u8>, off: int) -> int {
    u32_at(buf, off)
}

/// How many queries the window at `off` declares: a little-endian u32 at window
/// bytes 4..8.
pub open spec fn nq_at(buf: Seq<u8>, off: int) -> int {
    u32_at(buf, off + 4)
}

/// Element `i` of the window's array, at window byte `8 + 4*i`.
///
/// **Nothing here says the elements are sorted.** `bsearch` below is defined as
/// what the program does, not as "the position of `key`", so an unsorted window
/// is inside the specification rather than outside it.
pub open spec fn elem_at(buf: Seq<u8>, off: int, i: int) -> int {
    u32_at(buf, off + 8 + 4 * i)
}

/// Query `q`, at window byte `8 + 4*n + 4*q` -- i.e. immediately after the
/// declared array.
pub open spec fn key_at(buf: Seq<u8>, off: int, n: int, q: int) -> int {
    u32_at(buf, off + 8 + 4 * n + 4 * q)
}

/// The search itself, over the **half-open** range `[lo, hi)`, returning the
/// index it found or `u64::MAX`.
///
/// Three things about this function are load-bearing.
///
/// * `mid` is `lo + (hi - lo) / 2`, the overflow-safe spelling, and it is the
///   same characters the exec code uses. `(lo + hi) / 2` is in `../spec.md`'s
///   `forbidden` list; with `size_t` indices and a u32 count field the two are
///   equal on every representable input (NOTES.md 0), so the pin is about the
///   spelling and the grep is what settles it.
/// * The range is **half-open**. The textbook `hi = n - 1` / `while lo <= hi` /
///   `hi = mid - 1` form underflows at `mid == 0`, which any key below
///   `elem_at(0)` reaches -- on well-formed input. Here `hi = mid` and `hi - lo`
///   is the `decreases` measure, so the recursion is total with no side
///   condition at all.
/// * It returns the index the *program* returns, not "the index of `key`".
///   Sortedness is a property of the file and this spec does not assume it.
pub open spec fn bsearch(buf: Seq<u8>, off: int, key: int, lo: int, hi: int) -> u64
    decreases hi - lo,
{
    if hi <= lo {
        0xffff_ffff_ffff_ffffu64
    } else if elem_at(buf, off, lo + (hi - lo) / 2) == key {
        (lo + (hi - lo) / 2) as u64
    } else if elem_at(buf, off, lo + (hi - lo) / 2) < key {
        bsearch(buf, off, key, lo + (hi - lo) / 2 + 1, hi)
    } else {
        bsearch(buf, off, key, lo, lo + (hi - lo) / 2)
    }
}

/// Queries `q .. nq`, carrying the u64 accumulator.
///
/// `found + 1` is what is folded, so `u64::MAX` ("not found") folds as 0 and
/// element 0 folds as 1 -- a rung that returned a different index cannot
/// produce the same checksum.
pub open spec fn query_walk(
    buf: Seq<u8>,
    off: int,
    n: int,
    nq: int,
    q: int,
    acc: u64,
) -> u64
    decreases nq - q,
{
    if q >= nq {
        acc
    } else {
        query_walk(
            buf,
            off,
            n,
            nq,
            q + 1,
            acc.wrapping_mul(31).wrapping_add(
                bsearch(buf, off, key_at(buf, off, n, q), 0, n).wrapping_add(1),
            ),
        )
    }
}

/// What the kernel returns: every declared query searched over the declared
/// array, with `n * nq` mixed into the checksum so that a rung which runs a
/// *different number of searches* cannot produce the same answer.
///
/// The three early exits are the tests every rung keeps except where marked: a
/// window too short to hold the header, a zero count, and -- **the one R1 omits,
/// and the only one it omits** -- a declared array bigger than the bytes that
/// arrived. That third test is written over `int` here, which is unbounded, and
/// in `u64` in the exec rungs; `4*n + 4*nq` needs 35 bits, so the 32-bit
/// spelling of it is the pattern's second bug (c/kernel_hardened.c).
pub open spec fn search_fold(buf: Seq<u8>, off: int, len: int) -> u64 {
    if len < 8 {
        0
    } else if n_at(buf, off) == 0 || nq_at(buf, off) == 0 {
        0
    } else if 4 * n_at(buf, off) + 4 * nq_at(buf, off) > len - 8 {
        0
    } else {
        query_walk(buf, off, n_at(buf, off), nq_at(buf, off), 0, 0).wrapping_mul(
            31,
        ).wrapping_add((n_at(buf, off) as u64).wrapping_mul(nq_at(buf, off) as u64))
    }
}

// ------------------------------------------------------------------- TCB ----
// TRUSTED ITEM 1 of 3. vstd ships no specification for `<[T]>::get_unchecked`,
// so this is the axiom that licenses the unchecked read. It is sound because
// the standard library's documented contract for `get_unchecked` is exactly
// this: if the caller guarantees `i < v.len()`, the call is defined and yields
// `v[i]`.
//
// It is the *whole* security argument on p07, as it was on p16 and p05 and
// unlike p17. p07's harm is an ordinary out-of-bounds read -- the declared
// element count is bigger than the buffer -- so `i < v@.len()`, discharged at
// every call site, is exactly what rules it out. The functional `ensures` on
// `kernel` is what keeps the proof honest about *which* bytes were probed; it
// is not carrying the memory-safety claim here.
#[inline(always)]
#[verifier::external_body]
fn get_unchecked(v: &[u8], i: usize) -> (r: u8)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    unsafe { *v.get_unchecked(i) }
}

// THE VERIFIED TWIN of trusted item 1 (`harness/check.py` step 5c-twin).
//
// Same signature and same contract, character for character -- the gate lifts
// both from `get_unchecked` above and refuses a twin whose signature differs --
// but implemented in *checked* code. A `requires` too weak to license
// `*v.get_unchecked(i)` is too weak to license `v[i]`, and Verus can see the
// second one. Weaken the pair to `i <= v@.len()` and this fails with
// `precondition not met: index in bounds for this access`.
//
// **The twin is idle again, for the fifth pattern running, and p07 does not
// change that.** `.memory/04-verus.md` records that what the twin uniquely
// catches is a *missing conjunct* in a multi-clause trusted `requires`, and
// that its value accrues from the first pattern needing a multi-clause trusted
// accessor -- a property of the *intrinsic being wrapped*, not of the pattern
// number. p07 wraps the same single-clause `<[u8]>::get_unchecked` that p01,
// p02, p16, p17 and p05 wrap. Manufacturing a multi-clause accessor to exercise
// the mechanism would be gaming the gate; NOTES.md 8 reports "still idle"
// instead.
//
// `#[cfg(slb_twin)]` is a cfg no measured build ever sets, so rustc strips this
// before codegen: the twin costs zero instructions structurally.
#[cfg(slb_twin)]
fn slb_twin_get_unchecked(v: &[u8], i: usize) -> (r: u8)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    v[i]
}

// TRUSTED ITEM 2 of 3. Argument parsing, file I/O and little-endian decoding,
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

// TRUSTED ITEM 3 of 3. `println!` is not verifiable; no `ensures`. Counted with
// the two above -- every `external_body` item is TCB, not just the interesting
// one (`.memory/04-verus.md`: the pilot was published as "one 3-line wrapper"
// and the true tally was three items, one of which was `main`).
#[verifier::external_body]
fn emit(acc: u64) {
    driver::emit(acc);
}

// ---------------------------------------------------------------- kernel ----
// Same exec code as unsafe.rs. Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> (r: u64)
    requires
        off + len <= buf@.len(),
    ensures
        r == search_fold(buf@, off as int, len as int),
{
    // Ghost only: mentioning `spec_slice_len` fires vstd's `axiom_spec_len`,
    // which is what tells the SMT solver a slice length fits in a `usize` --
    // needed to rule out `off + len` overflowing. Erases at compile time.
    assert(buf@.len() == vstd::slice::spec_slice_len(buf));
    if len < 8 {
        return 0;
    }
    let n: usize = get_unchecked(buf, off) as usize + 256 * (get_unchecked(
        buf,
        off + 1,
    ) as usize) + 65536 * (get_unchecked(buf, off + 2) as usize) + 16777216 * (
    get_unchecked(buf, off + 3) as usize);
    let nq: usize = get_unchecked(buf, off + 4) as usize + 256 * (get_unchecked(
        buf,
        off + 5,
    ) as usize) + 65536 * (get_unchecked(buf, off + 6) as usize) + 16777216 * (
    get_unchecked(buf, off + 7) as usize);
    if n == 0 || nq == 0 {
        return 0;
    }
    let avail: usize = len - 8;
    if 4 * (n as u64) + 4 * (nq as u64) > avail as u64 {
        return 0;
    }
    let mut acc: u64 = 0;
    let mut q: usize = 0;
    // "The queries from here, with what we have accumulated, are all the
    // queries." Same shape as p16's walk invariant and p05's row invariant.
    while q < nq
        invariant
            q <= nq,
            0 < n,
            0 < nq,
            n == n_at(buf@, off as int),
            nq == nq_at(buf@, off as int),
            avail == len - 8,
            8 <= len,
            4 * n + 4 * nq <= avail,
            off + len <= buf@.len(),
            buf@.len() <= usize::MAX,
            query_walk(buf@, off as int, n as int, nq as int, q as int, acc)
                == query_walk(buf@, off as int, n as int, nq as int, 0, 0),
        decreases nq - q,
    {
        let kp: usize = off + 8 + 4 * n + 4 * q;
        let key: u32 = get_unchecked(buf, kp) as u32 + 256 * (get_unchecked(
            buf,
            kp + 1,
        ) as u32) + 65536 * (get_unchecked(buf, kp + 2) as u32) + 16777216 * (
        get_unchecked(buf, kp + 3) as u32);
        let mut lo: usize = 0;
        let mut hi: usize = n;
        let mut found: u64 = 0xffff_ffff_ffff_ffff;
        // "The search from here is the whole search." There is no closed form
        // for where a binary search is after `i` steps -- the path is the data
        // -- so this is the only shape the invariant can take, and it is p16's.
        // `invariant_except_break` + `ensures` because the loop exits two ways:
        // Verus cannot assume `lo >= hi` after a `break`.
        while lo < hi
            invariant_except_break
                lo <= hi,
                hi <= n,
                found == 0xffff_ffff_ffff_ffffu64,
                key as int == key_at(buf@, off as int, n as int, q as int),
                bsearch(buf@, off as int, key as int, lo as int, hi as int)
                    == bsearch(buf@, off as int, key as int, 0, n as int),
                4 * n + 4 * nq <= avail,
                avail == len - 8,
                off + len <= buf@.len(),
                buf@.len() <= usize::MAX,
            ensures
                found == bsearch(buf@, off as int, key as int, 0, n as int),
            decreases hi - lo,
        {
            let mid: usize = lo + (hi - lo) / 2;
            let ep: usize = off + 8 + 4 * mid;
            let v: u32 = get_unchecked(buf, ep) as u32 + 256 * (get_unchecked(
                buf,
                ep + 1,
            ) as u32) + 65536 * (get_unchecked(buf, ep + 2) as u32) + 16777216 * (
            get_unchecked(buf, ep + 3) as u32);
            // Ghost only: the byte quadruple this iteration read IS
            // `elem_at(mid)`, which is what lets the three arms below be matched
            // against `bsearch`'s three arms.
            assert(v as int == elem_at(buf@, off as int, mid as int));
            if v == key {
                found = mid as u64;
                break;
            }
            if v < key {
                lo = mid + 1;
            } else {
                hi = mid;
            }
        }
        acc = acc.wrapping_mul(31).wrapping_add(found.wrapping_add(1));
        q = q + 1;
    }
    acc.wrapping_mul(31).wrapping_add((n as u64).wrapping_mul(nq as u64))
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
        // Ghost only: at least one whole window is present. `stride <= n_blob`
        // is the guard immediately above, and integer division only rounds
        // down, so `n_blob / stride >= 1` -- but that is a fact about division
        // and Z3 needs the lemma named.
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
            // Ghost only: `k` must land inside the blob. Two nonlinear steps, so
            // Z3 needs both spelled out. (1) `(acc * nwin) >> 64 < nwin` because
            // `acc <= u64::MAX` implies `acc * nwin < nwin * 2^64`;
            // `lemma_u128_shr_is_div` turns the shift into the division the
            // argument is about. (2) `k * stride + stride <= n_blob` because
            // `k <= nwin - 1` and `nwin * stride <= n_blob`. Erases at compile
            // time -- R4 and R5 stay byte-identical.
            proof {
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
            // present, so `k * stride + stride <= n_blob` and the kernel's
            // structural precondition is discharged. `nwin * stride <= n_blob`
            // because division rounds down; `k * stride <= (nwin - 1) * stride`
            // because `k < nwin`. Both are nonlinear.
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
            assert(r == search_fold(buf@, (k * stride) as int, stride as int));
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    emit(acc);
}

} // verus!
