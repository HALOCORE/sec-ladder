//! p17 rung R5 -- unsafe + Verus proof.
//!
//! R4's exec code verbatim, plus the specs and proofs that discharge every
//! unchecked read in it. What the proof is *about* is different from every
//! earlier pattern in this repo, and the difference is the reason p17 exists.
//!
//! **p17 has two harms and the memory-safety half of the proof only catches
//! one of them.** The kernel serves the last `s` bytes of a window, `s` being
//! an attacker-controlled `u16`, and the identity `abs = body_start + start =
//! len - s` means the served range is always `[len - s, len)`. So:
//!
//!   * `s > len`  --  `abs` is negative and the read leaves the allocation.
//!     That is a memory-safety failure, and it is exactly what
//!     `get_unchecked`'s `requires i < v@.len()` forbids. Discharging that
//!     precondition at the call site rules this out, and it is what safe Rust's
//!     bounds check rules out too.
//!   * `content_len < s <= len`  --  `abs` lands between 0 and `body_start`,
//!     i.e. *inside the window's own `nsuf` word and suffix table*. The read is
//!     **in bounds**. `i < v@.len()` holds. Safe Rust does not panic. ASan does
//!     not fire. A proof of memory safety does not exclude it, **because it is
//!     not a memory-safety violation** -- it is a legal read of the wrong
//!     bytes, Heartbleed's shape.
//!
//! The only thing in this file that excludes the second harm is the functional
//! postcondition
//!
//!     ensures r == range_fold(buf@, off as int, len as int)
//!
//! because `range_fold` -- like `model.py`, and unlike a bounds property --
//! *says which bytes* the result is a fold of. Delete the `start >= 0` conjunct
//! and this file fails on the `ensures` and **not** on any accessor
//! precondition; NOTES.md 7 has the exact Verus error for both, side by side.
//!
//! That makes p17 the pattern where "proved memory-safe" and "proved right"
//! come apart with a measurement rather than an assertion. p16's `NOTES.md` §5
//! argued that a read-only kernel's whole security claim is the accessor's
//! `requires`; p17 is the counter-example, and the two together are the result.
//!
//! The `requires` is
//!
//!     off + len <= buf@.len(),
//!     buf@.len() <= 9223372036854775807        // i64::MAX
//!
//! Both are structural -- they are about the shape of the buffer the driver
//! built, not about its contents -- so they hold on *every* input this
//! benchmark runs, `adversarial-*` included, and the gate checks them call by
//! call. Every suffix value a `u16` can express is an argument of the problem,
//! not an assumption. The second clause is new for this pattern and is not
//! bureaucracy: p17 does its index arithmetic in `i64`, so the proof needs
//! `len` and `off + body_start` to be representable there, and **vstd has no
//! axiom that a slice's length is at most `isize::MAX`** -- `axiom_spec_len`
//! gives `<= usize::MAX` and nothing more. The driver therefore *checks* it,
//! once, outside the measured loop, rather than assuming it. See NOTES.md 9.
//!
//! TCB tally: NOTES.md 4. Three `external_body` items, all listed there
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
// group is what the window-offset bound `k * stride + stride <= n_blob` needs:
// both steps of it are nonlinear.
broadcast use {
    vstd::slice::group_slice_axioms,
    vstd::bits::lemma_u128_shr_is_div,
    vstd::arithmetic::mul::lemma_mul_inequality,
};

// ------------------------------------------------------------------ spec ----
/// How many suffix requests the window at `off` declares: a little-endian u16
/// at window bytes 0..2. Attacker data, like everything else in the header.
pub open spec fn nsuf_at(buf: Seq<u8>, off: int) -> int {
    buf[off] as int + 256 * (buf[off + 1] as int)
}

/// The `i`'th suffix request: `Range: bytes=-s`, a little-endian u16.
///
/// **This is the attacker's number and the whole pattern is what the kernel
/// does with it.** Every value in `0 ..= 65535` is possible and the kernel is
/// total on all of them -- including the ones that make `content_len - s`
/// negative, which is CVE-2017-7529.
pub open spec fn suf_at(buf: Seq<u8>, off: int, i: int) -> int {
    buf[off + 2 + 2 * i] as int + 256 * (buf[off + 3 + 2 * i] as int)
}

/// `acc`, with `s[from .. from+n)` folded into it left to right. Horner with a
/// multiplier of 31; `u64::wrapping_mul`/`wrapping_add` are usable in spec
/// position because vstd marks them `#[verifier::allow_in_spec]`.
pub open spec fn fold_bytes(s: Seq<u8>, from: int, n: int, acc: u64) -> u64
    decreases n,
{
    if n <= 0 {
        acc
    } else {
        fold_bytes(s, from, n - 1, acc).wrapping_mul(31).wrapping_add(
            s[from + n - 1] as u64,
        )
    }
}

/// The suffix-range walk: requests `i .. nsuf`, carrying `(acc, nserved)`.
///
/// The arithmetic is deliberately **signed at the `int` level**, mirroring the
/// `i64` the exec code uses, because a spec written in `nat` would make
/// `start < 0` unrepresentable and would therefore prove a different program.
/// `start = content_len - suf_at(..)` can be negative here exactly as it can in
/// C, and the guard is the *pair* `start < content_len && start >= 0`. Deleting
/// the second conjunct from the exec code alone makes this postcondition fail,
/// which is the measurement in NOTES.md 7.
///
/// `decreases nsuf_at(buf, off) - i`: the trip count is a `u16` read out of the
/// buffer, so it is attacker data, but it does not move during the walk -- and
/// that is the one thing p17 is *easier* about than p16, whose position was
/// data-dependent at every step.
pub open spec fn range_walk(
    buf: Seq<u8>,
    off: int,
    len: int,
    i: int,
    acc: u64,
    nserved: u64,
) -> (u64, u64)
    decreases nsuf_at(buf, off) - i,
{
    if i >= nsuf_at(buf, off) {
        (acc, nserved)
    } else {
        let body_start = 2 + 2 * nsuf_at(buf, off);
        let content_len = len - body_start;
        let start = content_len - suf_at(buf, off, i);
        if start < content_len && start >= 0 {
            range_walk(
                buf,
                off,
                len,
                i + 1,
                fold_bytes(buf, off + body_start + start, content_len - start, acc),
                nserved.wrapping_add(1),
            )
        } else {
            range_walk(buf, off, len, i + 1, acc, nserved)
        }
    }
}

/// What the kernel returns: the walk over the window's suffix table, with the
/// served count mixed into the checksum so that a server which serves a
/// different *set* of ranges cannot produce the same answer even if the bytes
/// happened to fold the same way.
///
/// The two early exits are the checks **every** rung keeps, R1 included: a
/// window too short to hold `nsuf`, and a `nsuf` whose suffix table does not
/// fit in the window.
pub open spec fn range_fold(buf: Seq<u8>, off: int, len: int) -> u64 {
    if len < 2 {
        0
    } else if 2 + 2 * nsuf_at(buf, off) > len {
        0
    } else {
        range_walk(buf, off, len, 0, 0, 0).0.wrapping_mul(31).wrapping_add(
            range_walk(buf, off, len, 0, 0, 0).1,
        )
    }
}

// ------------------------------------------------------------------- TCB ----
// TRUSTED ITEM 1 of 3. vstd ships no specification for `<[T]>::get_unchecked`,
// so this is the axiom that licenses the unchecked read. It is sound because
// the standard library's documented contract for `get_unchecked` is exactly
// this: if the caller guarantees `i < v.len()`, the call is defined and yields
// `v[i]`.
//
// **On p16 this item was the whole security argument. On p17 it is half of
// one.** `i < v@.len()`, discharged at every call site, rules out the read that
// leaves the allocation -- the `s > len` regime. It says nothing whatever about
// the `content_len < s <= len` regime, where the index is a small non-negative
// number and the read is in bounds of the very same slice. That harm is
// excluded by `kernel`'s `ensures` and by nothing else in this file. See the
// module comment; NOTES.md 5 is the long form.
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
// **The twin is still idle, and p17 does not change that.** `.memory/04-verus.md`
// records that what the twin uniquely catches is a *missing conjunct* in a
// multi-clause trusted `requires`, and says its value "accrues from p17 on".
// It does not: p17's trusted accessor is the same single-clause
// `i < v@.len()` p01, p02 and p16 ship, because p17's second harm is not a
// memory error and therefore cannot be a conjunct of an accessor precondition
// at all. A green 5c-twin here proves nothing that it did not prove on p16.
// Manufacturing a multi-clause accessor to exercise the mechanism would be
// gaming the gate; NOTES.md 8 reports "still idle" instead.
//
// `#[cfg(slb_twin)]` is a cfg no build ever sets, so rustc strips this before
// codegen: the twin costs zero instructions structurally.
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
// fact the proof needs -- including `n_blob <= i64::MAX`, which vstd cannot
// supply -- is re-derived at run time from `bytes.len()` inside verified code.
// It contains no `unsafe`, so it stays outside the twin regime
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
//
// **Read the `ensures` as the security property here, not as decoration.** On
// p16 the `ensures` existed to keep the proof non-vacuous while the accessor's
// `requires` carried the safety claim. On p17 the two are genuinely different
// properties and the pattern is the gap between them: `requires i < v@.len()`
// excludes the read that leaves the allocation, `r == range_fold(..)` excludes
// the read that stays inside it and returns the wrong bytes, and no amount of
// the first implies the second.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> (r: u64)
    requires
        off + len <= buf@.len(),
        buf@.len() <= 9223372036854775807,
    ensures
        r == range_fold(buf@, off as int, len as int),
{
    // Ghost only: mentioning `spec_slice_len` fires vstd's `axiom_spec_len`,
    // which is what tells the SMT solver a slice length fits in a `usize` --
    // needed to rule out `off + len` overflowing. Erases at compile time.
    assert(buf@.len() == vstd::slice::spec_slice_len(buf));
    if len < 2 {
        return 0;
    }
    let nsuf: usize = get_unchecked(buf, off) as usize + 256 * (get_unchecked(
        buf,
        off + 1,
    ) as usize);
    if 2 + 2 * nsuf > len {
        return 0;
    }
    let body_start: usize = 2 + 2 * nsuf;
    let content_len: i64 = (len - body_start) as i64;
    let mut acc: u64 = 0;
    let mut nserved: u64 = 0;
    let mut i: usize = 0;
    // The invariant is the same shape p16 found and this file re-uses: *the
    // walk from here, with what we have accumulated, is the whole walk.* Unlike
    // p16 there is no `break`, so a plain `invariant` suffices -- the trip
    // count is `nsuf`, which is attacker data but is fixed before the loop
    // starts, where p16's position was recomputed from the data at every step.
    while i < nsuf
        invariant
            i <= nsuf,
            nsuf == nsuf_at(buf@, off as int),
            body_start == 2 + 2 * nsuf,
            body_start <= len,
            content_len == len - body_start,
            off + len <= buf@.len(),
            buf@.len() <= usize::MAX,
            buf@.len() <= 9223372036854775807,
            range_walk(buf@, off as int, len as int, i as int, acc, nserved) == range_walk(
                buf@,
                off as int,
                len as int,
                0,
                0,
                0,
            ),
        decreases nsuf - i,
    {
        // Ghost only: the suffix table is inside the window. `i < nsuf` and
        // `body_start == 2 + 2*nsuf` give `3 + 2*i <= body_start - 1`, so both
        // header reads land strictly below `off + len`. Linear, but Verus will
        // not find it without being told which sum to bound.
        assert(off + 3 + 2 * i < off + len);
        let s: i64 = get_unchecked(buf, off + 2 + 2 * i) as i64 + 256 * (get_unchecked(
            buf,
            off + 3 + 2 * i,
        ) as i64);
        let start: i64 = content_len - s;
        let end: i64 = content_len;
        if start < end && start >= 0 {
            let base: i64 = (off + body_start) as i64 + start;
            let n: i64 = end - start;
            // Ghost only: the accumulator this served range starts from, which
            // is what `fold_bytes` in `range_walk` is applied to.
            let ghost a1: u64 = acc;
            let mut j: i64 = 0;
            while j < n
                invariant
                    0 <= j <= n,
                    0 <= base,
                    base + n == off + len,
                    off + len <= buf@.len(),
                    buf@.len() <= usize::MAX,
                    buf@.len() <= 9223372036854775807,
                    acc == fold_bytes(buf@, base as int, j as int, a1),
                decreases n - j,
            {
                acc = acc.wrapping_mul(31).wrapping_add(
                    get_unchecked(buf, (base + j) as usize) as u64,
                );
                j = j + 1;
            }
            nserved = nserved.wrapping_add(1);
        }
        i = i + 1;
    }
    acc.wrapping_mul(31).wrapping_add(nserved)
}

// ---------------------------------------------------------------- driver ----
fn main() {
    let (n_iters, stride_w, bytes) = load_input();
    // SLB-DRIVER-BEGIN
    let n_blob: usize = bytes.len();
    let buf: &[u8] = bytes.as_slice();
    let mut acc: u64 = 0;
    if stride_w >= 2 && stride_w <= n_blob as u64 && n_blob as u64 <= 9223372036854775807 {
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
                2 <= stride <= n_blob,
                buf@.len() == n_blob,
                n_blob <= 9223372036854775807,
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
            // (`.memory/04-verus.md`). On p17 that matters more than anywhere
            // else in the repo, because this postcondition is the *only* thing
            // that excludes the in-bounds leak. Ghost code erases, so the
            // driver loop stays byte-identical to R4's.
            assert(r == range_fold(buf@, (k * stride) as int, stride as int));
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    emit(acc);
}

} // verus!
