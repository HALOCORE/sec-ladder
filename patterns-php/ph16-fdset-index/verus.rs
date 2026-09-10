//! ph16 rung R5 -- unsafe + Verus.
//!
//! Same exec code as `unsafe.rs`, plus the proof that licenses it. What is
//! proved, and it is a VALUE postcondition rather than a memory-safety-only
//! retreat:
//!
//!     requires  off + len <= buf@.len(),  8 <= len
//!     ensures   r == fdset_fold(buf@, off as int, len as int)
//!
//! `fdset_fold` is `stream_array_to_fd_set` with the POSIX branch of
//! `99e290f882c9` applied, spelled as two recursive spec functions -- `walk`
//! and `fold16` -- and `model.py` re-derives the same `u64` from a different
//! decomposition.
//!
//! ⚠⚠ **THE OBLIGATION THIS ROW IS ABOUT IS ONE LINE, AND IT IS AN INDEX
//! BOUND WITH NO LOOP IN IT.** `streamsfuncs.c:541` is
//! `FD_SET(this_fd, fds)`; `FD_SET` expands to
//! `fds->__fds_bits[d / 64] |= 1UL << (d % 64)`, and `d` is an `int` the
//! caller never bounds. So unlike ph03 and ph07 -- whose obligations are
//! *termination* obligations about a cursor advanced by data -- this row's is
//! a single `w < NW` on a straight-line path. **That is the finding the proof
//! makes visible**: the whole of `walk`'s `decreases` is the trivial
//! `n - i` over a counted loop, and the one thing that needs an argument is
//! the array index. `../NOTES.md` §10.
//!
//! The two unchecked classes in the exec code rest on two independent facts:
//!
//!   * `aset_unchecked(fds, w, ...)` rests on `w < NW`, which is
//!     **`99e290f882c9` guard (b)** -- `PHP_SAFE_FD_SET`'s POSIX branch,
//!     spelled in the word index. Delete that line and the call has no
//!     precondition, which is exactly `c/kernel.c:541`.
//!     `controls/negatives.py --emit noguard` runs that mutant and it must
//!     FAIL to verify.
//!   * `get_unchecked(win, j)` rests on `m = (len - 6) / 2` and the driver's
//!     own `off + len <= buf@.len()`. That fact is not in PHP at all -- it is
//!     the harness's structural precondition -- and it is why the entry index
//!     cannot leave the window however hostile the two split words are.
//!
//! ⭐ **THE `%` IS WHAT KEEPS THE SPLIT TOTAL.** `n_r + n_w + n_e == m` holds
//! by construction rather than by a check, so no rung ever trusts a length out
//! of the blob -- exactly as PHP never gets one, because a `zend_hash` knows
//! its own count.

use vstd::prelude::*;

// Plain-Rust I/O helpers. Outside `verus!`, so Verus treats the whole module as
// external (external-by-default). Reached only through `load_input`/`emit`.
#[path = "../../common/driver.rs"]
mod driver;

verus! {

// `group_slice_axioms` gives `slice@.len() == spec_slice_len(slice)`, hence
// `slice@.len() <= usize::MAX`, without which `off + len` cannot be shown not
// to overflow. `lemma_u128_shr_is_div` turns `x >> 64` into `x / 2^64` for the
// driver's multiply-shift barrier bound; the mul group is what the window-offset
// bound `k * stride + stride <= n_blob` needs.
broadcast use {
    vstd::slice::group_slice_axioms,
    vstd::bits::lemma_u128_shr_is_div,
    vstd::arithmetic::mul::lemma_mul_inequality,
};

/// `FD_SETSIZE` -- `<sys/select.h>`, and the bound `streamsfuncs.c:541` never
/// mentions. `c/kernel.c` carries a C99 compile-time assertion that the
/// platform really is this shape.
pub const FD_SETSIZE: u32 = 1024;

/// `sizeof(fd_set) / sizeof(long)` -- the sixteen 64-bit words glibc's
/// `fd_set` is.
pub const NW: usize = 16;

// ------------------------------------------------------------------ spec ----

/// Entry `k` of a window, exactly as every rung decodes it.
pub open spec fn ent_of(win: Seq<u8>, k: int) -> u32 {
    (win[6 + 2 * k] as u32) | ((win[7 + 2 * k] as u32) << 8)
}

/// `php_stream_from_zval_no_verify` / `php_stream_cast`, as the blob encodes
/// their two decisions.
pub open spec fn tag_of(e: u32) -> u32 {
    e >> 14
}

/// `this_fd` -- what `php_stream_cast` writes through its out-parameter.
pub open spec fn fd_of(e: u32) -> u32 {
    e & 0x3FFF
}

/// The `fd_set` word an index names: `__FDELT(d)` in `<sys/select.h>`.
pub open spec fn word_of(f: u32) -> int {
    (f / 64) as int
}

/// The bit an index names: `__FDMASK(d)`.
pub open spec fn mask_of(f: u32) -> u64 {
    1u64 << (f % 64)
}

/// `stream_array_to_fd_set`'s loop, R1h -- one entry at a time.
///
/// ⚠ The guard is `word_of(f) < NW`, which is `99e290f882c9`'s
/// `if (fd < FD_SETSIZE)` written in the word index; `f < 1024` and
/// `f / 64 < 16` are one predicate on a `u32` and
/// `controls/guard_equiv.py` demonstrates it exhaustively over all 16 384
/// reachable values rather than asserting it.
///
/// ⚠ The tag test is written as the C writes it -- `!= 0` then `!= 1`, two
/// nested `if`s -- and NOT as `>= 2`. The two are equivalent only because a
/// two-byte entry has `e <= 65535`, which is a fact about the decoder rather
/// than about the loop, and a spec that assumed it would be proving a
/// different program.
pub open spec fn walk(win: Seq<u8>, base: int, i: int, n: int, fds: Seq<u64>, mx: u32) -> (
    Seq<u64>,
    u32,
)
    decreases n - i,
{
    if i >= n {
        (fds, mx)
    } else {
        let e = ent_of(win, base + i);
        if tag_of(e) != 0 && tag_of(e) != 1 {
            let f = fd_of(e);
            let fds2 = if word_of(f) < NW as int {
                fds.update(word_of(f), fds[word_of(f)] | mask_of(f))
            } else {
                fds
            };
            let mx2 = if f > mx {
                f
            } else {
                mx
            };
            walk(win, base, i + 1, n, fds2, mx2)
        } else {
            walk(win, base, i + 1, n, fds, mx)
        }
    }
}

/// One `fd_set`, folded at its own word granularity. Recursion is BACKWARDS so
/// that a forward loop's invariant is `h == fold16(fds, i, 0)` and not a
/// quantifier.
pub open spec fn fold16(fds: Seq<u64>, e: int, acc: u64) -> u64
    decreases e,
{
    if e <= 0 {
        acc
    } else {
        fold16(fds, e - 1, acc).wrapping_mul(31).wrapping_add(fds[e - 1])
    }
}

/// A zeroed `fd_set` -- `FD_ZERO`.
pub open spec fn zero16() -> Seq<u64> {
    Seq::new(NW as nat, |i: int| 0u64)
}

/// What ONE of `stream_select`'s three calls leaves behind.
///
/// ⚠ `dead` folds two different upstream tests that have the same effect here:
/// `stream_select`'s `if (X_array != NULL)` (`:670-672`), which skips the call
/// entirely, and `stream_array_to_fd_set`'s `Z_TYPE_P(...) != IS_ARRAY`
/// (`:524-526`), which returns 0 before touching the set. Both leave the
/// `fd_set` zeroed and `max_fd` unmoved and both add 0 to `sets`.
pub open spec fn arm_state(win: Seq<u8>, base: int, n: int, dead: bool, fds: Seq<u64>, mx: u32)
    -> (Seq<u64>, u32) {
    if dead {
        (fds, mx)
    } else {
        walk(win, base, 0, n, fds, mx)
    }
}

/// What that call contributes to `sets`.
pub open spec fn arm_sets(dead: bool) -> u64 {
    if dead {
        0u64
    } else {
        1u64
    }
}

/// `PHP_FUNCTION(stream_select)`'s frame, as a function of one window's bytes.
///
/// ⚠ The three arms are written out rather than folded into a loop, because
/// upstream writes three separate calls on three separate objects and the
/// SEPARATENESS is the row: an over-index in the first lands in the second.
pub open spec fn fdset_win(win: Seq<u8>, ln: int) -> u64 {
    let ctl = (win[0] as u32) | ((win[1] as u32) << 8);
    let sr = (win[2] as u32) | ((win[3] as u32) << 8);
    let sw = (win[4] as u32) | ((win[5] as u32) << 8);
    let m = (ln - 6) / 2;
    let n_r = (sr as int) % (m + 1);
    let rem = m - n_r;
    let n_w = (sw as int) % (rem + 1);
    let n_e = rem - n_w;
    let dead_r = (ctl & 1) != 0 || (ctl & 8) != 0;
    let dead_w = (ctl & 2) != 0 || (ctl & 16) != 0;
    let dead_e = (ctl & 4) != 0 || (ctl & 32) != 0;
    let ar = arm_state(win, 0, n_r, dead_r, zero16(), 0u32);
    let aw = arm_state(win, n_r, n_w, dead_w, zero16(), ar.1);
    let ae = arm_state(win, n_r + n_w, n_e, dead_e, zero16(), aw.1);
    // ⚠ `int`, not `u64`: spec-mode `+` on two `u64`s has type `int`, and the
    // sum is in 0..=3 so the cast below is exact.
    let sets: int = arm_sets(dead_r) + arm_sets(dead_w) + arm_sets(dead_e);
    let mx: u32 = if ae.1 >= FD_SETSIZE {
        (FD_SETSIZE - 1) as u32
    } else {
        ae.1
    };
    if sets == 0int {
        0xFFFF_FFFFu64
    } else {
        let a1 = (0u64).wrapping_mul(31).wrapping_add(sets as u64);
        let a2 = a1.wrapping_mul(31).wrapping_add(mx as u64);
        let a3 = a2.wrapping_mul(31).wrapping_add(fold16(ar.0, NW as int, 0u64));
        let a4 = a3.wrapping_mul(31).wrapping_add(fold16(aw.0, NW as int, 0u64));
        a4.wrapping_mul(31).wrapping_add(fold16(ae.0, NW as int, 0u64))
    }
}

/// What the kernel must return. `model.py::fdset_fold` re-derives it.
pub open spec fn fdset_fold(buf: Seq<u8>, off: int, ln: int) -> u64 {
    fdset_win(buf.subrange(off, off + ln), ln)
}

// ------------------------------------------------------- TRUSTED, item 1/5 --
// `v[i]` with no bounds check. The `requires` is what makes it sound and the
// `ensures` is what makes it useful; both are trusted, and `../NOTES.md` §10
// argues each one.
#[verifier::external_body]
fn get_unchecked(v: &[u8], i: usize) -> (r: u8)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    unsafe { *v.get_unchecked(i) }
}

// THE VERIFIED TWIN of trusted item 1 (`harness/check.py` step 5c-twin). Same
// signature and same contract, character for character -- the gate lifts both
// and diffs them, so a trusted item whose contract drifted from what a safe
// implementation can meet is caught.
#[cfg(slb_twin)]
fn slb_twin_get_unchecked(v: &[u8], i: usize) -> (r: u8)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    v[i]
}

// ------------------------------------------------------- TRUSTED, item 2/5 --
#[verifier::external_body]
fn aget_unchecked(a: &[u64; NW], i: usize) -> (r: u64)
    requires
        i < NW,
    ensures
        r == a@[i as int],
{
    unsafe { *a.get_unchecked(i) }
}

#[cfg(slb_twin)]
fn slb_twin_aget_unchecked(a: &[u64; NW], i: usize) -> (r: u64)
    requires
        i < NW,
    ensures
        r == a@[i as int],
{
    a[i]
}

// ------------------------------------------------------- TRUSTED, item 3/5 --
// ⚠ `x: u64` is a PURE VALUE and needs no precondition; the unchecked
// operation's definedness depends on `i` and on nothing about the word being
// written. The `ensures` names the WHOLE post-state --
// `old(a)@.update(i, x)` -- so a body that also clobbered `a[i + 1]` could not
// satisfy it. That completeness is the thing a write wrapper's contract can
// get wrong, and it is why Miri is required on this row (../spec.md `miri`).
#[verifier::external_body]
fn aset_unchecked(a: &mut [u64; NW], i: usize, x: u64)
    requires
        i < NW,
    ensures
        final(a)@ == old(a)@.update(i as int, x),
{
    unsafe { *a.get_unchecked_mut(i) = x };
}

#[cfg(slb_twin)]
fn slb_twin_aset_unchecked(a: &mut [u64; NW], i: usize, x: u64)
    requires
        i < NW,
    ensures
        final(a)@ == old(a)@.update(i as int, x),
{
    a[i] = x;
}

// ------------------------------------------------------- TRUSTED, item 4/5 --
#[verifier::external_body]
fn load_input() -> (r: (u64, u64, Vec<u8>)) {
    let path = driver::arg_path();
    let inp = driver::load(&path);
    let (stride_w, bytes) = driver::head1_u64_bytes(&inp);
    (inp.n_iters, stride_w, bytes)
}

// ------------------------------------------------------- TRUSTED, item 5/5 --
// `println!` is not verifiable; no `ensures`. Counted with the four above --
// every `external_body` item is TCB, not just the interesting ones
// (`.memory/04-verus.md`).
#[verifier::external_body]
fn emit(acc: u64) {
    driver::emit(acc);
}

// ---------------------------------------------------------------- kernel ----

/// `stream_array_to_fd_set` -- ext/standard/streamsfuncs.c:518-548, narrowed,
/// with `99e290f882c9`'s POSIX branch. Same exec code as `unsafe.rs`.
#[inline(always)]
fn to_fd_set(
    win: &[u8],
    base: usize,
    n: usize,
    not_an_array: bool,
    fds: &mut [u64; NW],
    max_fd: &mut u32,
) -> (r: u64)
    requires
        6 + 2 * (base + n) <= win@.len(),
    ensures
        r == arm_sets(not_an_array),
        (final(fds)@, *final(max_fd)) == arm_state(win@, base as int, n as int, not_an_array, old(fds)@, *old(max_fd)),
{
    if not_an_array {
        return 0;                       // Z_TYPE_P(stream_array) != IS_ARRAY
    }
    // Ghost only: `spec_slice_len` is what tells the solver a slice length fits
    // in a `usize`, which is what bounds `6 + 2 * (base + i)` below.
    assert(win@.len() == vstd::slice::spec_slice_len(win));
    let ghost target = walk(win@, base as int, 0, n as int, old(fds)@, *old(max_fd));
    let mut i: usize = 0;
    while i < n
        invariant
            i <= n,
            6 + 2 * (base + n) <= win@.len(),
            win@.len() <= usize::MAX,
            fds@.len() == NW,
            walk(win@, base as int, i as int, n as int, fds@, *max_fd) == target,
        decreases n - i,
    {
        assert(6 + 2 * (base + i) <= win@.len());
        let j: usize = 6 + 2 * (base + i);
        let e: u32 = (get_unchecked(win, j) as u32) | ((get_unchecked(win, j + 1) as u32) << 8);
        if e >> 14 != 0 {               // php_stream_from_zval_no_verify != NULL
            if e >> 14 != 1 {           // SUCCESS == php_stream_cast(...)
                let this_fd: u32 = e & 0x3FFF;
                let w: usize = (this_fd / 64) as usize;
                if w < NW {             // 99e290f882c9 guard (b)
                    aset_unchecked(fds, w, aget_unchecked(fds, w) | (1u64 << (this_fd % 64)));
                }
                if this_fd > *max_fd {
                    *max_fd = this_fd;
                }
            }
        }
        i = i + 1;
    }
    1
}

/// One `fd_set`, folded at its own word granularity.
#[inline(always)]
fn fold_set(s: &[u64; NW]) -> (r: u64)
    ensures
        r == fold16(s@, NW as int, 0u64),
{
    let mut h: u64 = 0;
    let mut i: usize = 0;
    while i < NW
        invariant
            i <= NW,
            s@.len() == NW,
            h == fold16(s@, i as int, 0u64),
        decreases NW - i,
    {
        h = h.wrapping_mul(31).wrapping_add(aget_unchecked(s, i));
        i = i + 1;
    }
    h
}

// Same exec code as unsafe.rs. Contract: ../spec.md.
//
// One `ensures`, and it is the VALUE, not the safety property. What makes it
// worth having: it is what stops the proof being vacuous, it is what `model.py`
// re-derives independently, and it is what forces the invariants to describe
// the three walks rather than merely bound the word index. A kernel that
// returned 0 unconditionally would satisfy every bounds obligation in this file.
// ⚠⚠ **THE ONE PROOF-BUDGET OVERRIDE IN THIS ROW, DISCLOSED WITH ITS NUMBERS,
// AND THE EXPENSIVE SIDE IS THE TWIN.** Verus's default rlimit is 10. Bisected
// on this box (../NOTES.md §10):
//
//     as first written          16 plain (FAILED at 14),   1 under --cfg slb_twin
//     + the ghost bindings       6 plain (FAILED at  4),   1 twin
//     + arm_state / arm_sets     2 plain (passes at  2),  10 twin (FAILED at 8)
//
// ⭐ The cost was ATTACKED FIRST and the attack worked: naming every quantity
// `fdset_win` names, and hiding the three arms' `if` behind two spec functions,
// took the plain requirement from 16 to <= 2. What it did NOT do is help the
// twin build, where the three verified twins add to the module's SMT context
// and the kernel needs the whole default. **A proof that passes on one side of
// a coin flip is not a proof**, so the budget is 30 -- 3x the worst measured
// requirement -- rather than the default it would just scrape.
// `harness/check.py::_verus` passes no `--rlimit`, so this has to be an
// attribute rather than a flag.
#[verifier::rlimit(30)]
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> (r: u64)
    requires
        off + len <= buf@.len(),
        8 <= len,
    ensures
        r == fdset_fold(buf@, off as int, len as int),
{
    // Ghost only: mentioning `spec_slice_len` fires vstd's `axiom_spec_len`,
    // which is what tells the SMT solver a slice length fits in a `usize`.
    assert(buf@.len() == vstd::slice::spec_slice_len(buf));
    let win: &[u8] = &buf[off..off + len];
    assert(win@.len() == vstd::slice::spec_slice_len(win));
    assert(win@ =~= buf@.subrange(off as int, off + len));

    let ctl: u32 = (get_unchecked(win, 0) as u32) | ((get_unchecked(win, 1) as u32) << 8);
    let split_r: u32 = (get_unchecked(win, 2) as u32) | ((get_unchecked(win, 3) as u32) << 8);
    let split_w: u32 = (get_unchecked(win, 4) as u32) | ((get_unchecked(win, 5) as u32) << 8);

    let m: usize = (len - 6) / 2;
    let n_r: usize = (split_r as usize) % (m + 1);
    let rem: usize = m - n_r;
    let n_w: usize = (split_w as usize) % (rem + 1);
    let n_e: usize = rem - n_w;
    // Ghost only: the split partitions the window, so every entry index the
    // three walks reach is inside it. `2 * m + 6 <= len` is what discharges
    // `to_fd_set`'s `requires`.
    assert(n_r + n_w + n_e == m);
    assert(2 * m + 6 <= len) by (nonlinear_arith)
        requires
            m == (len - 6) / 2,
            8 <= len,
    ;

    let mut rfds: [u64; NW] = [0u64; NW];
    let mut wfds: [u64; NW] = [0u64; NW];
    let mut efds: [u64; NW] = [0u64; NW];
    let mut max_fd: u32 = 0;
    let mut sets: u64 = 0;
    assert(rfds@ =~= zero16());
    assert(wfds@ =~= zero16());
    assert(efds@ =~= zero16());
    // Ghost only: name every quantity `fdset_win` names, so the postcondition
    // is a chain of one-step equalities rather than one search over a spec
    // function with three nested `let`s and three `if`s.
    // ⚠ MEASURED, not stylistic: without these the kernel needs `rlimit` 16
    // and with them it needs 3. ../NOTES.md §10.
    let ghost dead_r = (ctl & 1) != 0 || (ctl & 8) != 0;
    let ghost dead_w = (ctl & 2) != 0 || (ctl & 16) != 0;
    let ghost dead_e = (ctl & 4) != 0 || (ctl & 32) != 0;
    let ghost ar = arm_state(win@, 0, n_r as int, dead_r, zero16(), 0u32);

    if ctl & 1 == 0 {
        sets = sets + to_fd_set(win, 0, n_r, ctl & 8 != 0, &mut rfds, &mut max_fd);
    }
    assert(rfds@ == ar.0 && max_fd == ar.1);
    let ghost aw = arm_state(win@, n_r as int, n_w as int, dead_w, zero16(), ar.1);
    if ctl & 2 == 0 {
        sets = sets + to_fd_set(win, n_r, n_w, ctl & 16 != 0, &mut wfds, &mut max_fd);
    }
    assert(wfds@ == aw.0 && max_fd == aw.1);
    let ghost ae = arm_state(win@, (n_r + n_w) as int, n_e as int, dead_e, zero16(), aw.1);
    if ctl & 4 == 0 {
        sets = sets + to_fd_set(win, n_r + n_w, n_e, ctl & 32 != 0, &mut efds, &mut max_fd);
    }
    assert(efds@ == ae.0 && max_fd == ae.1);
    assert(sets as int == arm_sets(dead_r) + arm_sets(dead_w) + arm_sets(dead_e));

    // 99e290f882c9 guard (c): PHP_SAFE_MAX_FD's POSIX branch, in the CALLER.
    if max_fd >= FD_SETSIZE {
        max_fd = FD_SETSIZE - 1;
    }
    if sets == 0 {
        return 0xFFFF_FFFFu64;                       // RETURN_FALSE
    }

    let mut acc: u64 = 0;
    acc = acc.wrapping_mul(31).wrapping_add(sets);
    acc = acc.wrapping_mul(31).wrapping_add(max_fd as u64);
    acc = acc.wrapping_mul(31).wrapping_add(fold_set(&rfds));
    acc = acc.wrapping_mul(31).wrapping_add(fold_set(&wfds));
    acc = acc.wrapping_mul(31).wrapping_add(fold_set(&efds));
    acc
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
            // Z3 needs both spelled out. Erases at compile time -- R4 and R5
            // stay byte-identical.
            proof {
                let pr: int = (acc as int) * (nwin as int);
                assert((acc as u128) * (nwin as u128) <= (u64::MAX as u128) * (u64::MAX
                    as u128)) by (nonlinear_arith)
                    requires
                        acc <= u64::MAX,
                        nwin <= u64::MAX,
                ;
                assert(vstd::arithmetic::power2::pow2(64) == 0x1_0000_0000_0000_0000nat) by {
                    vstd::arithmetic::power2::lemma2_to64_rest();
                }
                assert(pr < (nwin as int) * 0x1_0000_0000_0000_0000int) by (nonlinear_arith)
                    requires
                        pr == (acc as int) * (nwin as int),
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
            // (`.memory/04-verus.md`).
            assert(r == fdset_fold(buf@, (k * stride) as int, stride as int));
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    emit(acc);
}

} // verus!
