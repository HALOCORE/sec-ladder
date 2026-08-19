//! p11 rung R5 -- unsafe + Verus proof.
//!
//! R4's exec code verbatim, plus the specs and proofs that discharge every
//! unchecked read in it.
//!
//! **What is new here is that the loop has no closed form for where it stops.**
//! p05's index is `i*ncol + j`, p07's is `off + 8 + 4*mid`; both are arithmetic
//! and both are *computable* before the loop runs. p11's scan stops at the first
//! zero byte, which is data, so there is no formula for `q` at all. The
//! invariant therefore has to be the "*the scan from here is the whole scan*"
//! shape p16 found for its walk -- `scan_end(q) == scan_end(p)` -- and the same
//! shape appears twice more, once for the fold and once for the string walk.
//! Three loops, three relational invariants, zero nonlinear arithmetic: every
//! multiplication in this kernel is by a literal.
//!
//! **The `requires` is ONE clause -- and getting it down to one is a result.**
//! The natural cursor step is
//!
//!     p = q + 1;
//!     if p >= len { break; }
//!
//! and it **cannot be proved overflow-free**. The scan may legitimately stop at
//! `q == len` -- that is what a window with no terminator left does -- so `q + 1`
//! is `len + 1`; vstd has no axiom that a slice is at most `isize::MAX` bytes
//! (`.memory/04-verus.md`) and models `usize` as possibly 32-bit, so nothing
//! bounds `len` below `usize::MAX`. p17 bought its way out of the analogous
//! problem with a second `requires` and a third driver conjunct. **p11 does not
//! need to**: adding
//!
//!     if q >= len { break; }
//!
//! *before* the step makes `q < len` and the overflow goes away at zero cost in
//! preconditions, in driver statements and (measured: NOTES.md 3) in
//! instructions. And the added line is not a prover concession -- it is the
//! sentence "a string whose terminator is missing is the last string in the
//! window", which is precisely the case R1 cannot represent. **The spelling that
//! makes the proof go through is the one that names the bug**, which is p07's
//! finding about half-open bounds arriving on a completely different kernel.
//!
//!     requires  off + len <= buf@.len()
//!
//! It is structural -- about the shape of the buffer the driver built, not about
//! its contents -- so it holds on *every* input this benchmark runs,
//! `adversarial-*` included, and the gate checks it call by call. `nstr`, all
//! 2^32 values of it, and every byte of the window are attacker data and none of
//! them is an assumption.
//!
//! Note what the spec does **not** assume: that `nstr` is honest, that the
//! strings are terminated, or that the window ends on a terminator. `str_walk`
//! is defined as the *program's* walk -- stop at the first zero byte or at the
//! window end, whichever comes first -- so `adversarial-count.bin` and
//! `adversarial-zerotail.bin`, whose headers both declare 4096 strings against
//! three written, are inside the verified domain and the kernel agrees with
//! `model.py` on both.
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
// needs; the KERNEL needs none of it, exactly as on p07.
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

/// How many strings the window at `off` declares: a little-endian u32 at window
/// bytes 0..4. **Declared, and it bounds nothing** -- see `str_walk`.
pub open spec fn nstr_at(buf: Seq<u8>, off: int) -> int {
    u32_at(buf, off)
}

/// THE SCAN: the index of the first zero byte at or after `q`, **capped at the
/// window end**.
///
/// This is the one function in the file that R1 does not implement. R1 calls
/// `strlen`, which is `if buf[off + q] == 0 { q } else { scan_end(q + 1) }` with
/// no first branch at all -- so it has no `decreases` measure either, and that
/// is not a coincidence: a scan with no bound is a recursion with no termination
/// argument. The `q >= len` arm is simultaneously the bounds check, the
/// termination measure and the fix.
pub open spec fn scan_end(buf: Seq<u8>, off: int, len: int, q: int) -> int
    decreases len - q,
{
    if q >= len {
        len
    } else if buf[off + q] == 0 {
        q
    } else {
        scan_end(buf, off, len, q + 1)
    }
}

/// The Horner fold over the string's bytes, `[i, q)`.
pub open spec fn fold_str(buf: Seq<u8>, off: int, i: int, q: int, h: u64) -> u64
    decreases q - i,
{
    if i >= q {
        h
    } else {
        fold_str(buf, off, i + 1, q, h.wrapping_mul(31).wrapping_add(buf[off + i] as u64))
    }
}

/// Strings `s .. nstr`, carrying the u64 accumulator and the cursor `p`.
///
/// `h ^ slen` is what is folded, so a rung that folded the same bytes but found
/// a different terminator cannot produce the same checksum.
///
/// **The walk stops at `q + 1 >= len` whatever `nstr` says**, which is the exec
/// rungs' `if q >= len { break; } p = q + 1; if p >= len { break; }` -- the two
/// guards together are exactly `q + 1 >= len`, and the first of them is what
/// makes `q + 1` provably free of `usize` overflow (see this file's header).
/// That is why an inflated `nstr` is inside this specification rather than
/// rejected by it, and why `adversarial-zerotail.bin` -- 4096 declared strings,
/// three written, a NUL tail -- is a row on which every rung agrees.
pub open spec fn str_walk(
    buf: Seq<u8>,
    off: int,
    len: int,
    s: int,
    nstr: int,
    p: int,
    acc: u64,
) -> u64
    decreases nstr - s,
{
    if s >= nstr {
        acc
    } else {
        let q = scan_end(buf, off, len, p);
        let acc2 = acc.wrapping_mul(31).wrapping_add(
            fold_str(buf, off, p, q, 0) ^ ((q - p) as u64),
        );
        if q + 1 >= len {
            acc2
        } else {
            str_walk(buf, off, len, s + 1, nstr, q + 1, acc2)
        }
    }
}

/// What the kernel returns: every declared string walked from window byte 4,
/// with `nstr` mixed into the checksum so that a rung which walked a *different
/// number of strings* cannot produce the same answer.
///
/// The two early exits are the tests every rung keeps, R1 included: a window too
/// short to hold the header, and a zero count. **R1 keeps both.** What R1 omits
/// is the `q >= len` arm of `scan_end`, and that is the only thing it omits.
pub open spec fn nul_scan_fold(buf: Seq<u8>, off: int, len: int) -> u64 {
    if len < 4 {
        0
    } else if nstr_at(buf, off) == 0 {
        0
    } else {
        str_walk(buf, off, len, 0, nstr_at(buf, off), 4, 0).wrapping_mul(31).wrapping_add(
            nstr_at(buf, off) as u64,
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
// It is the *whole* security argument on p11, as it was on p16, p05 and p07 and
// unlike p17. p11's harm is an ordinary out-of-bounds read -- the scan runs past
// the end of the allocation looking for a sentinel that is not there -- so
// `i < v@.len()`, discharged at every call site, is exactly what rules it out.
// The functional `ensures` on `kernel` is what keeps the proof honest about
// *which* bytes were scanned and folded; it is not carrying the memory-safety
// claim here.
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
// **The twin is idle again, for the sixth pattern running, and p11 does not
// change that.** `.memory/04-verus.md` records that what the twin uniquely
// catches is a *missing conjunct* in a multi-clause trusted `requires`, and that
// its value accrues from the first pattern needing a multi-clause trusted
// accessor -- a property of the *intrinsic being wrapped*, not of the pattern
// number. p11 wraps the same single-clause `<[u8]>::get_unchecked` that p01,
// p02, p16, p17, p05 and p07 wrap. Manufacturing a multi-clause accessor to
// exercise the mechanism would be gaming the gate; NOTES.md 8 reports "still
// idle" instead.
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
        r == nul_scan_fold(buf@, off as int, len as int),
{
    // Ghost only: mentioning `spec_slice_len` fires vstd's `axiom_spec_len`,
    // which is what tells the SMT solver a slice length fits in a `usize` --
    // needed to rule out `off + len` overflowing. Erases at compile time.
    assert(buf@.len() == vstd::slice::spec_slice_len(buf));
    if len < 4 {
        return 0;
    }
    let nstr: usize = get_unchecked(buf, off) as usize + 256 * (get_unchecked(
        buf,
        off + 1,
    ) as usize) + 65536 * (get_unchecked(buf, off + 2) as usize) + 16777216 * (
    get_unchecked(buf, off + 3) as usize);
    if nstr == 0 {
        return 0;
    }
    let mut acc: u64 = 0;
    let mut p: usize = 4;
    let mut s: usize = 0;
    // "The strings from here, with what we have accumulated and where the cursor
    // is, are all the strings." Same shape as p16's walk invariant and p07's
    // query invariant -- but this loop exits TWO ways (`s == nstr` and
    // `p >= len`), and only the second one is reachable on a well-formed window,
    // so it needs `invariant_except_break` plus a loop `ensures`.
    while s < nstr
        invariant_except_break
            s <= nstr,
            0 < nstr,
            nstr == nstr_at(buf@, off as int),
            4 <= len,
            4 <= p <= len,
            off + len <= buf@.len(),
            buf@.len() <= usize::MAX,
            str_walk(buf@, off as int, len as int, s as int, nstr as int, p as int, acc)
                == str_walk(buf@, off as int, len as int, 0, nstr as int, 4, 0),
        ensures
            acc == str_walk(buf@, off as int, len as int, 0, nstr as int, 4, 0),
        decreases nstr - s,
    {
        let ghost p_before = p as int;
        let ghost acc_before = acc;
        let ghost s_before = s as int;
        let mut q: usize = p;
        // "The scan from here is the whole scan." There is no closed form for
        // where a NUL scan stops -- the path is the data -- so this is the only
        // shape the invariant can take, and it is p16's.
        while q < len
            invariant_except_break
                p <= q <= len,
                4 <= len,
                off + len <= buf@.len(),
                buf@.len() <= usize::MAX,
                scan_end(buf@, off as int, len as int, q as int) == scan_end(
                    buf@,
                    off as int,
                    len as int,
                    p as int,
                ),
            ensures
                p <= q <= len,
                q as int == scan_end(buf@, off as int, len as int, p as int),
            decreases len - q,
        {
            if get_unchecked(buf, off + q) == 0 {
                break;
            }
            q = q + 1;
        }
        let slen: usize = q - p;
        let mut h: u64 = 0;
        let mut i: usize = p;
        // "The fold from here is the whole fold."
        while i < q
            invariant
                p <= i <= q,
                q <= len,
                off + len <= buf@.len(),
                buf@.len() <= usize::MAX,
                fold_str(buf@, off as int, i as int, q as int, h) == fold_str(
                    buf@,
                    off as int,
                    p as int,
                    q as int,
                    0,
                ),
            decreases q - i,
        {
            h = h.wrapping_mul(31).wrapping_add(get_unchecked(buf, off + i) as u64);
            i = i + 1;
        }
        acc = acc.wrapping_mul(31).wrapping_add(h ^ (slen as u64));
        // Ghost only: unfold `str_walk` once at the value it had on entry to
        // this iteration. Its `q` IS the scan loop's `q` and its inner fold IS
        // the fold loop's `h`, so the accumulator this iteration produced is the
        // one the spec produces -- and the spec's `q + 1 >= len` test is the
        // `break` two lines below.
        assert(str_walk(buf@, off as int, len as int, s_before, nstr as int, p_before, acc_before)
            == if q as int + 1 >= len as int {
            acc
        } else {
            str_walk(buf@, off as int, len as int, s_before + 1, nstr as int, q as int + 1, acc)
        });
        if q >= len {
            break;
        }
        p = q + 1;
        if p >= len {
            break;
        }
        s = s + 1;
    }
    acc.wrapping_mul(31).wrapping_add(nstr as u64)
}

// ---------------------------------------------------------------- driver ----
fn main() {
    let (n_iters, stride_w, bytes) = load_input();
    // SLB-DRIVER-BEGIN
    let n_blob: usize = bytes.len();
    let buf: &[u8] = bytes.as_slice();
    let mut acc: u64 = 0;
    if stride_w >= 4 && stride_w <= n_blob as u64 {
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
                4 <= stride <= n_blob,
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
            assert(r == nul_scan_fold(buf@, (k * stride) as int, stride as int));
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    emit(acc);
}

} // verus!
