//! ph29 rung R5 -- unsafe + Verus.
//!
//! Same exec code as `unsafe.rs`, plus the proof that licenses it. What is
//! proved, and it is a VALUE postcondition rather than a memory-safety-only
//! retreat:
//!
//!     requires  off + len <= buf@.len(),  16 <= len
//!     ensures   r == recv_fold(buf@, off as int, len as int)
//!
//! `recv_fold` is `PHP_FUNCTION(stream_socket_recvfrom)` with the copy bounded
//! by the block `_emalloc` actually returned, spelled as spec functions --
//! `rs_of`, `rec_of`, `foldb`, `tally_of`, `recv_win` -- and `model.py`
//! re-derives the same `u64` from two further decompositions.
//!
//! ⚠⚠ **THE OBLIGATION THIS ROW IS ABOUT IS `n <= cap`, AND `cap` IS A NUMBER
//! PHP COMPUTES AND THEN FORGETS.** `streamsfuncs.c:321` asks for `to_read + 1`
//! bytes; `Zend/zend_alloc.c:129`/`:135` store `REAL_SIZE(size)` into an
//! `unsigned int` and `:182` allocates THAT; `:323` then hands the transport
//! `to_read`. Nothing in PHP ever compares the two. Here `cap` is named, and
//! `vcopy_unchecked`'s and `vset_unchecked`'s `requires` are what force the
//! comparison to exist.
//!
//! ⭐ **AND THAT IS WHY THIS ROW'S PROOF IS NOT `ph16`'s.** `ph16`'s obligation
//! is a single index bound on a straight-line path. This one is a bound
//! **between two derived quantities**, one of which is a 32-bit truncation of
//! the other -- so the proof has to carry `rs_of` through the whole kernel, and
//! the `decreases` on `foldb` is the trivial part. `../NOTES.md` §10.
//!
//! The two unchecked classes in the exec code rest on two independent facts:
//!
//!   * `vcopy_unchecked` / `vset_unchecked` rest on `n <= cap` and
//!     `recvd < cap`, i.e. on the clamp `if n > cap { n = cap; }`. Delete that
//!     line and the calls have no precondition, which is exactly
//!     `c/kernel.c`'s `:323`. `controls/negatives.py --emit noclamp` runs that
//!     mutant and it must FAIL to verify.
//!   * `get_unchecked(win, j)` rests on `16 <= len` and the driver's own
//!     `off + len <= buf@.len()`, plus `navail = want % (n_pay + 1)`. That
//!     fact is not in PHP at all -- it is the harness's structural
//!     precondition -- and it is why the payload index cannot leave the window
//!     however hostile `want` is.
//!
//! ⭐ **THE `%` IS WHAT KEEPS `navail` INSIDE THE WINDOW.** `navail <= n_pay`
//! holds by construction rather than by a check, so no rung ever trusts a
//! length out of the blob -- exactly as PHP never gets one, because a datagram
//! knows its own length.

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

/// The window's head, in bytes -- `PH29_HEAD` in `c/kernel.c`.
pub const HEAD: usize = 12;

// ------------------------------------------------------------------ spec ----

/// `long to_read` as the window carries it -- `streamsfuncs.c:304`/`:309`, the
/// eight bytes `zend_parse_parameters`'s `"l"` yields on a 64-bit build.
/// Carried as its `u64` bit pattern throughout: every use is either
/// `(size_t)to_read` or `to_read + 1` in `size_t`, and neither reads the sign.
pub open spec fn tr_of(win: Seq<u8>) -> u64 {
    (win[0] as u64) | ((win[1] as u64) << 8) | ((win[2] as u64) << 16)
        | ((win[3] as u64) << 24) | ((win[4] as u64) << 32)
        | ((win[5] as u64) << 40) | ((win[6] as u64) << 48)
        | ((win[7] as u64) << 56)
}

/// The two decisions upstream makes from its remaining arguments: whether
/// `zremote` was passed (`:315`) and whether the transport succeeds (`:328`).
pub open spec fn ctl_of(win: Seq<u8>) -> u32 {
    (win[8] as u32) | ((win[9] as u32) << 8)
}

/// What the datagram's length is derived from.
pub open spec fn want_of(win: Seq<u8>) -> u32 {
    (win[10] as u32) | ((win[11] as u32) << 8)
}

/// `Zend/zend_alloc.c:129` + `:135` -- TRUNCATION T1, and it is the STORE into
/// `unsigned int real_size` that truncates, not the macro at `:132`.
/// `:182` allocates `header + padding + real_size`, so THIS is how many bytes
/// the block has.
pub open spec fn rs_of(size: u64) -> u32 {
    ((size.wrapping_add(7)) & !(7u64)) as u32
}

/// `Zend/zend_alloc.h:53` -- TRUNCATION T2, `unsigned int size:31`. A DIFFERENT
/// modulus from T1 and the only size the block itself records; `_efree`
/// recomputes its cache class from this one (`zend_alloc.c:263`).
pub open spec fn rec_of(size: u64) -> u32 {
    ((size as u32) & 0x7FFF_FFFF)
}

/// `php_shim_tally()` after ONE request. `php_shim_reset()` empties the cache
/// at the top of every kernel call, so `n_alloc` is 1 and `n_cache_hit` is 0;
/// `n_free` is 1 exactly when the zval destructor ran.
pub open spec fn tally_of(n_free: u64, rs: u32) -> u64 {
    ((1u64).wrapping_mul(1000003)) ^ (n_free.wrapping_mul(1000033))
        ^ ((0u64).wrapping_mul(1000037)) ^ ((rs as u64).wrapping_mul(1000039))
}

/// The fold over the received bytes -- `RETURN_STRINGL(read_buf, recvd, 0)` at
/// `:340`, read back out of the destination.
///
/// ⚠ It reads the WINDOW, not the destination, and that is sound rather than a
/// shortcut: the copy writes `read_buf[j] == win[HEAD + j]` for every `j < n`
/// and the NUL store touches only index `n`, so the two agree on exactly the
/// range this folds. `lemma_foldb_ext` is what discharges it, and it is the
/// only lemma in this file.
///
/// Recursion is FORWARD with an accumulator so that the exec loop's invariant
/// is `foldb(.., i, n, h) == foldb(.., 0, n, 0)` and not a quantifier.
pub open spec fn foldb(s: Seq<u8>, base: int, i: int, n: int, acc: u64) -> u64
    decreases n - i,
{
    if i >= n {
        acc
    } else {
        foldb(s, base, i + 1, n, acc.wrapping_mul(31).wrapping_add(s[base + i] as u64))
    }
}

/// Two folds over pointwise-equal ranges agree. Induction on `n - i`.
pub proof fn lemma_foldb_ext(
    a: Seq<u8>,
    ba: int,
    b: Seq<u8>,
    bb: int,
    i: int,
    n: int,
    acc: u64,
)
    requires
        0 <= i <= n,
        forall|j: int| #![trigger a[ba + j]] i <= j < n ==> a[ba + j] == b[bb + j],
    ensures
        foldb(a, ba, i, n, acc) == foldb(b, bb, i, n, acc),
    decreases n - i,
{
    if i < n {
        assert(a[ba + i] == b[bb + i]);
        lemma_foldb_ext(
            a,
            ba,
            b,
            bb,
            i + 1,
            n,
            acc.wrapping_mul(31).wrapping_add(a[ba + i] as u64),
        );
    }
}

/// The smallest of three, as the exec's two `if`s compute it.
pub open spec fn min3(a: int, b: int, c: int) -> int {
    let ab = if b < a { b } else { a };
    if ab > c { c } else { ab }
}

/// `PHP_FUNCTION(stream_socket_recvfrom)`'s body, as a function of one window's
/// bytes -- with the copy bounded by the block `_emalloc` returned.
///
/// ⚠ The arms are written out rather than folded, because upstream's control
/// flow is what the corpus has to reach: `if (zremote)` at `:315`,
/// `if (recvd >= 0)` at `:328` and `if (zremote && Z_STRLEN_P(zremote))` at
/// `:329` are three separate tests on three separate quantities.
pub open spec fn recv_win(win: Seq<u8>, ln: int) -> u64 {
    let tr = tr_of(win);
    let ctl = ctl_of(win);
    let want = want_of(win);
    let navail: int = (want as int) % (ln - (HEAD as int) + 1);
    let size = tr.wrapping_add(1);
    let rs = rs_of(size);
    let rec = rec_of(size);
    let failed = (ctl & 2) != 0;
    let n: int = min3(navail, tr as int, rs as int);
    let remote_len: int = if !failed && (ctl & 1) != 0 {
        n % 32
    } else {
        0int
    };
    let ris: u64 = if !failed && (ctl & 1) != 0 && remote_len != 0int {
        1u64
    } else {
        0u64
    };
    let h: u64 = if failed {
        0u64
    } else {
        foldb(win, HEAD as int, 0, n, 0u64)
    };
    let n_free: u64 = if failed {
        0u64
    } else {
        1u64
    };
    let a1 = (0u64).wrapping_mul(31).wrapping_add(h);
    let a2 = a1.wrapping_mul(31).wrapping_add(
        if failed {
            0xFFFF_FFFFu64
        } else {
            n as u64
        },
    );
    let a3 = a2.wrapping_mul(31).wrapping_add(remote_len as u64);
    let a4 = a3.wrapping_mul(31).wrapping_add(ris);
    let a5 = a4.wrapping_mul(31).wrapping_add(rec as u64);
    a5.wrapping_mul(31).wrapping_add(tally_of(n_free, rs))
}

/// What the kernel must return. `model.py::recv_fold` re-derives it.
pub open spec fn recv_fold(buf: Seq<u8>, off: int, ln: int) -> u64 {
    recv_win(buf.subrange(off, off + ln), ln)
}

// ------------------------------------------------------- TRUSTED, item 1/6 --
// `v[i]` with no bounds check. The `requires` is what makes it sound and the
// `ensures` is what makes it useful; both are trusted, and `../NOTES.md` §10
// argues each one.
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

// ------------------------------------------------------- TRUSTED, item 2/6 --
// The unchecked DESTINATION read, for the fold. Same contract, a `Vec`.
#[inline(always)]
#[verifier::external_body]
fn vget_unchecked(v: &Vec<u8>, i: usize) -> (r: u8)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    unsafe { *v.get_unchecked(i) }
}

#[cfg(slb_twin)]
fn slb_twin_vget_unchecked(v: &Vec<u8>, i: usize) -> (r: u8)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    v[i]
}

// ------------------------------------------------------- TRUSTED, item 3/6 --
// The unchecked DESTINATION WRITE -- `read_buf[recvd] = '\0'` at
// `streamsfuncs.c:332`.
//
// ⚠ `x: u8` is a PURE VALUE and needs no precondition; the unchecked
// operation's definedness depends on `i` and on nothing about the byte being
// written. The `ensures` names the WHOLE post-state -- `old(v)@.update(i, x)`
// -- so a body that also clobbered `v[i + 1]` could not satisfy it. That
// completeness is the thing a write wrapper's contract can get wrong, and it is
// why Miri is required on this row (../spec.md `miri`).
#[inline(always)]
#[verifier::external_body]
fn vset_unchecked(v: &mut Vec<u8>, i: usize, x: u8)
    requires
        i < old(v)@.len(),
    ensures
        final(v)@ == old(v)@.update(i as int, x),
{
    unsafe { *v.get_unchecked_mut(i) = x };
}

#[cfg(slb_twin)]
fn slb_twin_vset_unchecked(v: &mut Vec<u8>, i: usize, x: u8)
    requires
        i < old(v)@.len(),
    ensures
        final(v)@ == old(v)@.update(i as int, x),
{
    v.set(i, x);
}

// ------------------------------------------------------- TRUSTED, item 4/6 --
// THE RECEIVE -- `php_stream_xport_recvfrom(stream, read_buf, to_read, ...)` at
// `streamsfuncs.c:323`, reached through `php_stream_read` (transports.c:391).
//
// ⚠⚠ **`n <= old(v)@.len()` IS THE PRECONDITION PHP 5.0.0 DOES NOT HAVE.** C
// passes `to_read`; the block is `real_size` bytes; nothing compares them. Here
// the comparison must exist or this call does not verify.
//
// ⚠⚠ THE `ensures` HAD A THIRD CLAUSE -- `forall|j| n <= j < old(v)@.len()
// ==> final(v)@[j] == old(v)@[j]`, "the suffix is untouched" -- WITH A COMMENT
// SAYING IT WAS WHAT KEPT THE NUL STORE HONEST. `check.py` stage 5b's clause
// deletion PROVED IT IS NOT LOAD-BEARING: with it deleted the file still gives
// `10 verified, 0 errors`, because nothing in this kernel ever reads past
// `recvd`. A trusted item's `ensures` is an AXIOM, and one nothing depends on
// is an unchecked claim about real Rust semantics carried for free -- so it is
// gone rather than kept for its rhetoric. ../NOTES.md's
// `SLB-TRUSTED-ARGUMENT verus.rs vcopy_unchecked` states what the two
// surviving clauses do and do not exclude.
#[inline(always)]
#[verifier::external_body]
fn vcopy_unchecked(v: &mut Vec<u8>, s: &[u8], from: usize, n: usize)
    requires
        n <= old(v)@.len(),
        from + n <= s@.len(),
    ensures
        final(v)@.len() == old(v)@.len(),
        forall|j: int| 0 <= j < n ==> final(v)@[j] == s@[from + j],
{
    unsafe {
        core::ptr::copy_nonoverlapping(s.as_ptr().add(from), v.as_mut_ptr(), n);
    }
}

#[cfg(slb_twin)]
fn slb_twin_vcopy_unchecked(v: &mut Vec<u8>, s: &[u8], from: usize, n: usize)
    requires
        n <= old(v)@.len(),
        from + n <= s@.len(),
    ensures
        final(v)@.len() == old(v)@.len(),
        forall|j: int| 0 <= j < n ==> final(v)@[j] == s@[from + j],
{
    // Ghost only: `spec_slice_len` is what tells the solver a slice length fits
    // in a `usize`, which is what stops `from + i` overflowing below.
    assert(s@.len() == vstd::slice::spec_slice_len(s));
    let mut i: usize = 0;
    while i < n
        invariant
            i <= n,
            n <= v@.len(),
            from + n <= s@.len(),
            s@.len() <= usize::MAX,
            v@.len() == old(v)@.len(),
            forall|j: int| 0 <= j < i ==> v@[j] == s@[from + j],
            forall|j: int| i <= j < v@.len() ==> v@[j] == old(v)@[j],
        decreases n - i,
    {
        let b: u8 = s[from + i];
        v.set(i, b);
        i = i + 1;
    }
}

// ------------------------------------------------------- TRUSTED, item 5/6 --
// Argument parsing, file I/O and little-endian decoding, delegated to
// common/driver.rs so that all six rungs read the file the same way. It states
// **no** `ensures` at all, deliberately: an `ensures` here would be an axiom
// about the contents of a file, which nothing can justify. Every fact the proof
// needs is re-derived at run time from `bytes.len()` inside verified code.
#[verifier::external_body]
fn load_input() -> (r: (u64, u64, Vec<u8>)) {
    let path = driver::arg_path();
    let inp = driver::load(&path);
    let (stride_w, bytes) = driver::head1_u64_bytes(&inp);
    (inp.n_iters, stride_w, bytes)
}

// ------------------------------------------------------- TRUSTED, item 6/6 --
// `println!` is not verifiable; no `ensures`. Counted with the five above --
// every `external_body` item is TCB, not just the interesting ones
// (`.memory/04-verus.md`).
#[verifier::external_body]
fn emit(acc: u64) {
    driver::emit(acc);
}

// ---------------------------------------------------------------- kernel ----

// Same exec code as unsafe.rs. Contract: ../spec.md.
//
// One `ensures`, and it is the VALUE, not the safety property. What makes it
// worth having: it is what stops the proof being vacuous, it is what `model.py`
// re-derives independently, and it is what forces the clamp to be described
// rather than merely present. A kernel that returned 0 unconditionally would
// satisfy every bounds obligation in this file.
//
// ⚠⚠ **THERE IS NO `#[verifier::rlimit]` HERE AND THAT IS MEASURED, NOT AN
// OVERSIGHT.** ph16 needs 30 and ph07 needs 9. This file verifies with the
// attribute DELETED and at `rlimit(1)`, in BOTH the plain and the
// `--cfg slb_twin` builds -- bisected at 30 / 10 / 4 / 2 / 1 / none, every one
// `10 verified, 0 errors` and `15 verified, 0 errors` (../NOTES.md §10b).
// ⭐ That is this row's proof-cost result: the obligation is ONE bound between
// two derived quantities, and naming `cap` is the whole of it.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> (r: u64)
    requires
        off + len <= buf@.len(),
        16 <= len,
    ensures
        r == recv_fold(buf@, off as int, len as int),
{
    // Ghost only: mentioning `spec_slice_len` fires vstd's `axiom_spec_len`,
    // which is what tells the SMT solver a slice length fits in a `usize`.
    assert(buf@.len() == vstd::slice::spec_slice_len(buf));
    let win: &[u8] = &buf[off..off + len];
    assert(win@.len() == vstd::slice::spec_slice_len(win));
    assert(win@ =~= buf@.subrange(off as int, off + len));

    // streamsfuncs.c:309 -- zend_parse_parameters(..., "rl|lz", ...).
    let tr: u64 = (get_unchecked(win, 0) as u64) | ((get_unchecked(win, 1) as u64) << 8)
        | ((get_unchecked(win, 2) as u64) << 16) | ((get_unchecked(win, 3) as u64) << 24)
        | ((get_unchecked(win, 4) as u64) << 32) | ((get_unchecked(win, 5) as u64) << 40)
        | ((get_unchecked(win, 6) as u64) << 48) | ((get_unchecked(win, 7) as u64) << 56);
    let ctl: u32 = (get_unchecked(win, 8) as u32) | ((get_unchecked(win, 9) as u32) << 8);
    let want: u32 = (get_unchecked(win, 10) as u32) | ((get_unchecked(win, 11) as u32) << 8);

    let n_pay: usize = len - HEAD;
    let navail: usize = (want as usize) % (n_pay + 1);

    // streamsfuncs.c:315-319
    let mut remote_len: usize = 0;
    if ctl & 1 != 0 {
        remote_len = 0;
    }

    // streamsfuncs.c:321 -- emalloc(to_read + 1), and what it really returns.
    let size: u64 = tr.wrapping_add(1);
    let real_size: u32 = ((size.wrapping_add(7)) & !(7u64)) as u32;
    let recorded: u32 = (size as u32) & 0x7FFF_FFFF;
    let cap: usize = real_size as usize;
    let mut read_buf: Vec<u8> = vec![0u8; cap];
    assert(read_buf@.len() == cap);

    // streamsfuncs.c:323 -- php_stream_xport_recvfrom -> php_stream_read.
    let recvd: usize;
    let failed: bool = ctl & 2 != 0;
    if failed {
        recvd = 0;
    } else {
        // transports.c:390-392 -- php_stream_read(stream, buf, buflen), and
        // `buflen` is the `size_t` widening of `to_read`. The comparison is
        // done in 64 bits because that is the width PHP does it in.
        // ⚠ It is ALSO what makes this provable without assuming a word
        // size: Verus's default `--arch-word-bits` admits a 32-bit `usize`, so
        // `tr as usize` would be a TRUNCATING cast and `min3`'s second argument
        // would not be `tr`. The row is 64-bit-only (`c/kernel.c` asserts it),
        // but the PROOF does not have to depend on that and does not.
        let mut n64: u64 = navail as u64;
        if tr < n64 {
            n64 = tr;                                  // transports.c:406-407
        }
        let mut n: usize = n64 as usize;
        // ⭐ THE ONE LINE R1 DOES NOT HAVE, AND THE ONE THIS PROOF RESTS ON.
        if n > cap {
            n = cap;
        }
        assert(n as int == min3(navail as int, tr as int, real_size as int));
        assert(HEAD + n <= win@.len());
        vcopy_unchecked(&mut read_buf, win, HEAD, n);
        if ctl & 1 != 0 {
            remote_len = n % 32;                       // transports.c:438-441
        }
        recvd = n;
    }

    let mut h: u64 = 0;
    let mut n_free: u64 = 0;
    let mut remote_is_string: u64 = 0;
    if !failed {
        // streamsfuncs.c:329-330
        if ctl & 1 != 0 && remote_len != 0 {
            remote_is_string = 1;
        }
        // streamsfuncs.c:332 -- read_buf[recvd] = '\0'
        let ghost pre = read_buf@;
        if recvd < cap {
            vset_unchecked(&mut read_buf, recvd, 0);
        }
        assert(forall|j: int| #![trigger read_buf@[j]] 0 <= j < recvd as int ==> read_buf@[j] == pre[j]);
        proof {
            lemma_foldb_ext(
                read_buf@,
                0,
                win@,
                HEAD as int,
                0,
                recvd as int,
                0u64,
            );
        }
        // streamsfuncs.c:340 -- RETURN_STRINGL(read_buf, recvd, 0)
        let ghost target = foldb(read_buf@, 0, 0, recvd as int, 0u64);
        let mut i: usize = 0;
        while i < recvd
            invariant
                i <= recvd,
                recvd <= read_buf@.len(),
                foldb(read_buf@, 0, i as int, recvd as int, h) == target,
            decreases recvd - i,
        {
            h = h.wrapping_mul(31).wrapping_add(vget_unchecked(&read_buf, i) as u64);
            i = i + 1;
        }
        n_free = 1;                                    // the zval's destructor
    }
    // else streamsfuncs.c:344 RETURN_FALSE -- 5.0.0 leaks read_buf and PHP's
    // request shutdown reclaims it, which is why `n_free` stays 0.

    let mut acc: u64 = 0;
    acc = acc.wrapping_mul(31).wrapping_add(h);
    acc = acc.wrapping_mul(31).wrapping_add(
        if failed {
            0xFFFF_FFFFu64
        } else {
            recvd as u64
        },
    );
    acc = acc.wrapping_mul(31).wrapping_add(remote_len as u64);
    acc = acc.wrapping_mul(31).wrapping_add(remote_is_string);
    acc = acc.wrapping_mul(31).wrapping_add(recorded as u64);
    acc = acc.wrapping_mul(31).wrapping_add(
        ((1u64).wrapping_mul(1000003)) ^ (n_free.wrapping_mul(1000033))
            ^ ((0u64).wrapping_mul(1000037)) ^ ((real_size as u64).wrapping_mul(1000039)),
    );
    acc
}

// ---------------------------------------------------------------- driver ----
fn main() {
    let (n_iters, stride_w, bytes) = load_input();
    // SLB-DRIVER-BEGIN
    let n_blob: usize = bytes.len();
    let buf: &[u8] = bytes.as_slice();
    let mut acc: u64 = 0;
    if stride_w >= 16 && stride_w <= n_blob as u64 {
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
                16 <= stride <= n_blob,
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
            assert(r == recv_fold(buf@, (k * stride) as int, stride as int));
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    emit(acc);
}

} // verus!
