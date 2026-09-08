//! ph03 rung R5 -- unsafe + Verus proof.
//!
//! R4's exec code verbatim, plus the specs and proofs that discharge every
//! unchecked read and every unchecked write in it. What the proof is about, in
//! one line: **the three runtime tests this decoder keeps are jointly
//! sufficient, and the two the 2004 upstream fix ships are not.**
//!
//! Read that literally. `c/kernel_hardened.c` is the real `fix_commit`,
//! `f95c1df58349`, and it carries `len > src_len` and `ee > e`. Delete the third
//! test from the exec code below -- `if s + 4 > e`, which is PHP's own 2014
//! commit `1e2818b14376` -- and this file does not verify: the three source
//! reads `buf[s+1..s+3]` lose their bound, because `ee > e` bounds where the
//! loop TESTS and the body reads three bytes further. **The verifier's refusal
//! is the same fact ASan reports on 144 of 12 600 documents**
//! (`.temp/php13/02-reach.log` Q3), and it is the row's headline: a proof
//! obligation caught in 2026 what a patch missed for ten years.
//!
//! **What carries the memory safety, and it is not the `ensures`.** The kernel
//! writes, but into a buffer it allocates and frees itself, so "nothing outside
//! the destination moved" is not observable in the return value any more than
//! p16's "no byte outside the window was read" was. The safety claim rests
//! **entirely on the discharged `requires` of the three trusted accessors**:
//! `get_unchecked` (`i < v@.len()`), `vget_unchecked` and `vset_unchecked`
//! (`i < v@.len()`). Those, proved at every call site for indices the
//! attacker's own length bytes chose, ARE the security property. The `ensures`
//! exists to make the proof non-vacuous, to tie the value to `model.py`, and to
//! force the invariants to describe the walk rather than merely bound the
//! indices -- a kernel returning a constant satisfies every bounds obligation
//! in this file.
//!
//! The `requires` is
//!
//!     off + len <= buf@.len()
//!
//! and nothing else: the window is inside the blob. That is structural -- about
//! the shape of the buffer the driver built, not its contents -- so it holds on
//! every input this benchmark runs, `adversarial-*` included, and the gate
//! checks it call by call. Every value the length byte can take is an argument
//! of the problem, not an assumption.
//!
//! **The one obligation that is not a loop invariant.** The final fold reads
//! `dest[0 .. total_len)`, and `total_len` is a sum of DECLARED line lengths
//! while `dest`'s bound comes from bytes EMITTED. They are related by
//!
//!     ln <= 3 * ceil(line_len(ln) / 4)      for every ln in 1..=63
//!
//! which is an arithmetic fact about `(ln * 133) / 100` with **equality at every
//! multiple of 3** (3, 6, ..., 63) -- so it is tight, cannot be slackened, and
//! is not derivable from the loop shape. `lemma_emit_covers_declared` proves it
//! by bounded evaluation over the 64 values `PHP_UU_DEC`'s `& 077` can produce.
//!
//! TCB tally: NOTES.md §10. Five `external_body` items, all listed there
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
/// `PHP_UU_DEC` -- ext/standard/uuencode.c:66. The `& 077` is what makes `ln`
/// range over exactly 0..=63, which is what `lemma_emit_covers_declared` needs
/// and what makes the C's signed-`char` subtraction irrelevant.
pub open spec fn dec_of(b: u8) -> u8 {
    (b.wrapping_sub(0x20)) & 0o77
}

/// `ee - s` at uuencode.c:141. ⚠ The C is `(int) floor(len * 1.33)` in binary64
/// and stays that way; **Verus has no `f64` arithmetic at all**, so the float
/// cannot cross to this rung and the exact integer form is what the ladder
/// carries above R1h. The equivalence is exhaustive over 0..=63 with a
/// must-fire control (`.temp/php13/02-reach.log` Q1) and re-checked every gate
/// run by `model.py::selfcheck`. NOTES.md §9.
pub open spec fn line_len_of(ln: int) -> int {
    if ln == 45 { 60 } else { ln * 133 / 100 }
}

/// `emalloc(ceil(src_len * 0.75) + 1)` at uuencode.c:131, as `n - n/4 + 1`.
pub open spec fn cap_of(n: int) -> int {
    n - n / 4 + 1
}

/// `php_shim_tally()` after one reset + one `emalloc(cap)` + one `efree`
/// (`common-php/emalloc_shim.h:642-648`). `n_alloc = n_free = 1`,
/// `n_cache_hit = 0` because the reset empties the size-class cache, and
/// `bytes_mallocked` is the TRUNCATED `real_size = (cap + 7) & ~7`.
///
/// The bitand is spelled on `usize` rather than on `int` because Verus has no
/// `&` on `int`; the `as usize` cast is exact here for every `cap` this kernel
/// can produce (`cap <= 3 * 2^62`, from `cap_of`).
pub open spec fn tally_of(cap: int) -> u64 {
    let rs: usize = ((cap + 7) as usize) & !7usize;
    ((1000003u64 ^ 1000033u64) ^ (rs as u64).wrapping_mul(1000039))
}

/// The three plaintext bytes one 4-character group emits (uuencode.c:144-146).
pub open spec fn grp(b0: u8, b1: u8, b2: u8, b3: u8) -> Seq<u8> {
    seq![
        (dec_of(b0) << 2) | (dec_of(b1) >> 4),
        (dec_of(b1) << 4) | (dec_of(b2) >> 2),
        (dec_of(b2) << 6) | dec_of(b3),
    ]
}

/// How many 4-character groups the inner loop runs: `ceil(fl / 4)`.
///
/// ⚠ The loop tests `s < ee` and steps by 4, so it OVERSHOOTS `ee` by up to 3
/// whenever `fl` is not a multiple of 4 -- and `fl` is a multiple of 4 only for
/// the `len == 45` case and a minority of the others. **That overshoot IS the
/// defect `f95c1df58349` did not close**, and it is why this function exists
/// instead of `ee`: a spec that resumed the outer walk at `ee` would model a
/// decoder PHP has never shipped.
pub open spec fn nsteps(fl: int) -> int {
    (fl + 3) / 4
}

/// The inner loop, uuencode.c:143-148 plus `1e2818b14376`. Returns the emitted
/// bytes appended to `out`, and `false` when the 2014 check refused.
pub open spec fn fold_line(src: Seq<u8>, s: int, ee: int, e: int, out: Seq<u8>) -> (Seq<u8>, bool)
    decreases e - s,
{
    if s >= ee {
        (out, true)
    } else if e - s < 4 {
        (out, false)
    } else {
        fold_line(src, s + 4, ee, e, out + grp(src[s], src[s + 1], src[s + 2], src[s + 3]))
    }
}

/// The outer loop, uuencode.c:135-156 plus both fixes. Returns
/// `(emitted bytes, total_len, ok)`.
///
/// Recursive rather than a fold over a known range, because the number of steps
/// and the position of every step come from bytes inside the buffer.
/// `decreases e - s` is well founded because the walk resumes at
/// `s + 1 + 4*nsteps(fl) + 1 >= s + 2`: a line always spends its length byte,
/// whatever the length byte says.
///
/// ⚠ `total + ln` is added AFTER the line is folded, where uuencode.c:139 adds
/// it before `:141`. Observationally identical -- every path that skips it
/// returns `false` and the value is discarded -- and it is what makes
/// `total_len <= p` a loop invariant rather than one that holds "except between
/// two statements". R2-R5 and `model.py` all do the same; ../spec.md pins it.
pub open spec fn uu_walk(
    src: Seq<u8>,
    s: int,
    e: int,
    src_len: int,
    out: Seq<u8>,
    total: int,
) -> (Seq<u8>, int, bool)
    decreases e - s,
{
    if s >= e {
        (out, total, true)
    } else {
        let ln = dec_of(src[s]) as int;
        if ln == 0 {
            (out, total, true)
        } else if ln > src_len {
            (out, total, false)
        } else {
            let fl = line_len_of(ln);
            if fl > e - (s + 1) {
                (out, total, false)
            } else {
                let r = fold_line(src, s + 1, s + 1 + fl, e, out);
                let s_end = s + 1 + 4 * nsteps(fl);
                if !r.1 {
                    (r.0, total, false)
                } else if ln < 45 {
                    (r.0, total + ln, true)
                } else if s_end >= e {
                    (r.0, total + ln, true)
                } else {
                    uu_walk(src, s_end + 1, e, src_len, r.0, total + ln)
                }
            }
        }
    }
}

/// `acc`, with `s[0 .. n)` folded into it left to right. Horner with a
/// multiplier of 31; `wrapping_mul`/`wrapping_add` are usable in spec position
/// because vstd marks them `#[verifier::allow_in_spec]`.
pub open spec fn fold_bytes(s: Seq<u8>, n: int, acc: u64) -> u64
    decreases n,
{
    if n <= 0 {
        acc
    } else {
        fold_bytes(s, n - 1, acc).wrapping_mul(31).wrapping_add(s[n - 1] as u64)
    }
}

/// What the kernel returns.
pub open spec fn uu_fold(buf: Seq<u8>, off: int, len: int) -> u64 {
    let w = uu_walk(buf, off, off + len, len, Seq::empty(), 0);
    let base = if !w.2 {
        0xFFFF_FFFFu64
    } else {
        fold_bytes(w.0, w.1, 0).wrapping_mul(31).wrapping_add(w.1 as u64)
    };
    base ^ tally_of(cap_of(len))
}

// ------------------------------------------------------------------ proof ---
/// `fold_bytes` reads only the first `n` elements, so two sequences that agree
/// there fold to the same value. Needed because the exec folds `dest`, whose
/// tail is whatever `vec![0u8; cap]` left there, against a spec sequence that
/// has exactly `p` elements.
pub proof fn lemma_fold_prefix(a: Seq<u8>, b: Seq<u8>, n: int, acc: u64)
    requires
        0 <= n <= a.len(),
        n <= b.len(),
        forall|i: int| 0 <= i < n ==> a[i] == b[i],
    ensures
        fold_bytes(a, n, acc) == fold_bytes(b, n, acc),
    decreases n,
{
    if n > 0 {
        lemma_fold_prefix(a, b, n - 1, acc);
    }
}

/// `cap_of` cannot overflow a `usize`, at any word width. `4*cap_of(n) =
/// 3n + n%4 + 4 <= 3n + 7`, and `3M + 7 <= 4M - 28` whenever `M >= 35`. This is
/// why `capacity` is spelled `n - n/4 + 1` and not `(3n + 3)/4 + 1`: the second
/// form's `3*n` overflows and no precondition available at the call site rules
/// it out.
pub proof fn lemma_cap_bound(n: int)
    requires
        0 <= n <= usize::MAX,
    ensures
        1 <= cap_of(n) <= usize::MAX - 7,
        4 * cap_of(n) >= 3 * n + 4,
{
    vstd::arithmetic::div_mod::lemma_fundamental_div_mod(n, 4);
    assert(0 <= n % 4 < 4);
    assert(4 * (n / 4) == n - n % 4);
    assert(4 * cap_of(n) == 3 * n + n % 4 + 4);
}

/// The inner loop steps by 4 and stops at the first position at or past `ee`,
/// so it lands exactly on `s0 + 4*nsteps(fl)`. Both `d` and `4*nsteps(fl)` are
/// multiples of 4 inside the window `[fl, fl+3]`, which holds exactly one.
pub proof fn lemma_nsteps_exact(fl: int, d: int)
    requires
        0 <= fl,
        0 <= d,
        d % 4 == 0,
        d >= fl,
        d <= 4 * nsteps(fl),
    ensures
        d == 4 * nsteps(fl),
{
    vstd::arithmetic::div_mod::lemma_fundamental_div_mod(fl + 3, 4);
    assert(0 <= (fl + 3) % 4 < 4);
    assert(4 * nsteps(fl) == fl + 3 - (fl + 3) % 4);
    assert(fl <= d <= fl + 3);
    assert(fl <= 4 * nsteps(fl) <= fl + 3);
    assert((d - 4 * nsteps(fl)) % 4 == 0) by {
        vstd::arithmetic::div_mod::lemma_sub_mod_noop(d, 4 * nsteps(fl), 4);
    }
}

/// **SAFETY (4) of unsafe.rs, as one lemma.** The three destination stores are
/// in bounds. `4*p <= 3*(s - off)` is the loop invariant -- every group spends
/// four source bytes and emits three -- and `s + 4 <= e` is the 2014 check, so
///
///     4*(p + 2) = 4p + 8 <= 3*(s - off) + 8 <= 3*(len - 4) + 8 = 3*len - 4
///
/// while `4*cap = 4*(len - len/4 + 1) >= 4*len - len + 4 = 3*len + 4`, because
/// `4*(len/4) <= len`. So `p + 2 < cap` with eight to spare, and the slack does
/// not depend on the length byte at all -- which is why this half needs no
/// bounded case analysis where the `total_len` half does.
pub proof fn lemma_store_in_bounds(len: int, p: int, s: int, off: int)
    requires
        len >= 0,
        p >= 0,
        s >= off,
        4 * p <= 3 * (s - off),
        s + 4 <= off + len,
    ensures
        p + 2 < cap_of(len),
{
    vstd::arithmetic::div_mod::lemma_fundamental_div_mod(len, 4);
    assert(4 * (len / 4) <= len);
    assert(4 * cap_of(len) >= 3 * len + 4);
    assert(4 * (p + 2) <= 3 * len - 4);
}

/// `dec_of` masks with `077`, so a length byte is always in 0..=63.
pub proof fn lemma_dec_range(b: u8)
    ensures
        dec_of(b) <= 63,
{
    assert((b.wrapping_sub(0x20)) & 0o77 <= 63) by (bit_vector);
}

/// ⚠⚠ **THE ONE OBLIGATION THAT IS NOT A LOOP INVARIANT.**
///
/// A line declares `ln` plaintext bytes and emits `3 * ceil(line_len(ln) / 4)`
/// of them. The final fold reads `total_len` bytes out of a buffer bounded by
/// what was emitted, so the fold is in bounds only if the second quantity is at
/// least the first, for every length byte an attacker can write.
///
/// It is TIGHT: equality holds at ln = 3, 6, 9, ..., 63 -- twenty-one of the
/// sixty-three cases -- so no slack argument works and the bound cannot be
/// weakened. `by (compute_only)` evaluates the recursive conjunction over the
/// whole domain, which is finite precisely because `dec_of` ends in `& 077`.
pub open spec fn emit_ok(ln: int) -> bool {
    ln <= 3 * ((line_len_of(ln) + 3) / 4)
}

pub open spec fn emit_ok_upto(n: nat) -> bool
    decreases n,
{
    if n == 0 {
        true
    } else {
        emit_ok(n as int) && emit_ok_upto((n - 1) as nat)
    }
}

pub proof fn lemma_emit_upto_elim(n: nat, k: int)
    requires
        emit_ok_upto(n),
        1 <= k <= n,
    ensures
        emit_ok(k),
    decreases n,
{
    if k < n {
        lemma_emit_upto_elim((n - 1) as nat, k);
    }
}

pub proof fn lemma_emit_covers_declared(ln: int)
    requires
        1 <= ln <= 63,
    ensures
        emit_ok(ln),
{
    assert(emit_ok_upto(63)) by (compute_only);
    lemma_emit_upto_elim(63, ln);
}

// ------------------------------------------------------------------- TCB ----
// TRUSTED ITEM 1 of 5, and half of this row's security argument. vstd ships no
// specification for `<[T]>::get_unchecked`, so this is the axiom that licenses
// the unchecked SOURCE read. It is sound because the standard library's
// documented contract for `get_unchecked` is exactly this: if the caller
// guarantees `i < v.len()`, the call is defined and yields `v[i]`.
//
// FIVE call sites (`:602`, `:676`, `:677`, `:678`, `:679`): the length byte,
// discharged from the outer loop's own condition `s < e`; and `buf[s]`,
// `buf[s+1]`, `buf[s+2]`, `buf[s+3]` inside the group, discharged from
// `s + 4 <= e` -- the 2014 check, which is the line c/kernel_hardened.c does
// NOT have. (This said "Four" over a list of five until TASK_PHP_015;
// TASK_PHP_014 m2. NOTES.md §10 always said five.)
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
// from `get_unchecked` above and refuses a twin whose signature differs -- but
// implemented in *checked* code. A `requires` too weak to license
// `*v.get_unchecked(i)` is too weak to license `v[i]`, and Verus can see the
// second one. `#[cfg(slb_twin)]` is a cfg no build ever sets, so rustc strips
// this before codegen: the twin costs zero instructions structurally.
#[cfg(slb_twin)]
fn slb_twin_get_unchecked(v: &[u8], i: usize) -> (r: u8)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    v[i]
}

// TRUSTED ITEM 2 of 5 -- the unchecked DESTINATION read, for the final fold.
// Same contract, a `Vec` rather than a slice.
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

// TRUSTED ITEM 3 of 5, and the OTHER half of the security argument -- the
// unchecked DESTINATION WRITE. This is the limb the corpus's `root_cause_id`
// names ("writes past emalloc") and the one `harness/check.py` cannot hold as
// gate evidence, because R1h closes it while leaving the read (NOTES.md §5).
//
// The `ensures` is the *whole* new state, `old(v)@.update(i, x)`, not just
// `v@[i] == x`: an `ensures` naming only the written element would let a body
// that also clobbered `v[i+1]` through, which is precisely the class
// `.memory/04-verus.md` records as the most dangerous vacuity mode.
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

// TRUSTED ITEM 4 of 5. Argument parsing, file I/O and little-endian decoding,
// delegated to common/driver.rs so that all six rungs read the file the same
// way. It states **no** `ensures` at all, deliberately: an `ensures` here would
// be an axiom about the contents of a file, which nothing can justify. Every
// fact the proof needs is re-derived at run time from `bytes.len()` inside
// verified code. It contains no `unsafe`, so it stays outside the twin regime.
#[verifier::external_body]
fn load_input() -> (r: (u64, u64, Vec<u8>)) {
    let path = driver::arg_path();
    let inp = driver::load(&path);
    let (stride_w, bytes) = driver::head1_u64_bytes(&inp);
    (inp.n_iters, stride_w, bytes)
}

// TRUSTED ITEM 5 of 5. `println!` is not verifiable; no `ensures`. Counted with
// the four above -- every `external_body` item is TCB, not just the interesting
// ones (`.memory/04-verus.md`: the pilot was published as "one 3-line wrapper"
// and the true tally was three items, one of which was `main`).
#[verifier::external_body]
fn emit(acc: u64) {
    driver::emit(acc);
}

// -------------------------------------------------------- exec arithmetic ---
// Same text as unsafe.rs. Each carries the `ensures` that ties the machine
// arithmetic to the spec function above it, so none of them is trusted.

#[inline(always)]
fn dec(b: u8) -> (r: u8)
    ensures
        r == dec_of(b),
{
    b.wrapping_sub(0x20) & 0o77
}

#[inline(always)]
fn line_len(ln: usize) -> (r: usize)
    requires
        ln <= 63,
    ensures
        r == line_len_of(ln as int),
{
    if ln == 45 {
        60
    } else {
        (ln * 133) / 100
    }
}

#[inline(always)]
fn capacity(src_len: usize) -> (r: usize)
    ensures
        r == cap_of(src_len as int),
        1 <= r <= usize::MAX - 7,
{
    proof {
        lemma_cap_bound(src_len as int);
        vstd::arithmetic::div_mod::lemma_fundamental_div_mod(src_len as int, 4);
    }
    src_len - src_len / 4 + 1
}

#[inline(always)]
fn tally(cap: usize) -> (r: u64)
    requires
        cap <= usize::MAX - 7,
    ensures
        r == tally_of(cap as int),
{
    let real_size: u64 = ((cap + 7) & !7) as u64;
    1000003u64 ^ 1000033u64 ^ real_size.wrapping_mul(1000039)
}

// ---------------------------------------------------------------- kernel ----
// Same exec code as unsafe.rs. Contract: ../spec.md.
//
// One `ensures`, and it is the VALUE, not the safety property -- see the module
// comment. What makes it worth having anyway: it is what stops the proof being
// vacuous, it is what `model.py` re-derives independently, and it is what forces
// the invariants to describe the walk rather than merely bound the indices. A
// kernel that returned 0 unconditionally would satisfy every bounds obligation
// in this file.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> (r: u64)
    requires
        off + len <= buf@.len(),
    ensures
        r == uu_fold(buf@, off as int, len as int),
{
    // Ghost only: mentioning `spec_slice_len` fires vstd's `axiom_spec_len`,
    // which is what tells the SMT solver a slice length fits in a `usize`.
    assert(buf@.len() == vstd::slice::spec_slice_len(buf));
    let src_len: usize = len;
    let e: usize = off + len;
    proof {
        lemma_cap_bound(len as int);
    }
    let cap: usize = capacity(src_len);
    let mut dest: Vec<u8> = vec![0u8; cap];
    let mut p: usize = 0;
    let mut total_len: usize = 0;
    let mut s: usize = off;
    let mut err: bool = false;
    let ghost g0 = uu_walk(buf@, off as int, e as int, len as int, Seq::<u8>::empty(), 0);
    let ghost mut out: Seq<u8> = Seq::<u8>::empty();
    // `invariant_except_break` + `ensures`, because the walk exits five ways and
    // Verus cannot assume the loop condition is false after a `break`. The
    // interesting invariant is the last one: *the walk from here, with what we
    // have accumulated, is the whole walk*. That is the only form it can take,
    // because there is no closed-form description of where the walk will be
    // after i lines -- the positions are the data.
    while s < e
        invariant_except_break
            off <= s <= e,
            e == off + len,
            e <= buf@.len(),
            buf@.len() <= usize::MAX,
            src_len == len,
            cap == cap_of(len as int),
            cap >= 1,
            dest@.len() == cap,
            !err,
            out.len() == p,
            4 * (p as int) <= 3 * (s - off),
            total_len <= p,
            dest@.subrange(0, p as int) == out,
            uu_walk(buf@, s as int, e as int, len as int, out, total_len as int) == g0,
        ensures
            dest@.len() == cap,
            cap == cap_of(len as int),
            cap >= 1,
            err == !g0.2,
            out.len() == p,
            4 * (p as int) <= 3 * (len as int),
            total_len <= p,
            dest@.subrange(0, p as int) == out,
            !err ==> total_len == g0.1,
            !err ==> out == g0.0,
        decreases e - s,
    {
        let ghost s_top = s;
        let ghost out_top = out;
        let ghost tl_top = total_len as int;
        let b: u8 = get_unchecked(buf, s);
        let ln: usize = dec(b) as usize;
        proof {
            lemma_dec_range(b);
        }
        s = s + 1;
        if ln == 0 {
            break;
        }
        if ln > src_len {
            err = true;
            break;
        }
        let fl: usize = line_len(ln);
        if fl > e - s {
            err = true;
            break;
        }
        let ee: usize = s + fl;
        let ghost out0 = out;
        let ghost p0 = p;
        let ghost s0 = s;
        while s < ee
            invariant_except_break
                s0 <= s <= e,
                s0 == s_top + 1,
                ee == s0 + fl,
                ee <= e,
                e == off + len,
                e <= buf@.len(),
                off <= s0,
                cap == cap_of(len as int),
                dest@.len() == cap,
                !err,
                out.len() == p,
                (s - s0) % 4 == 0,
                s - s0 <= 4 * nsteps(fl as int),
                p == p0 + 3 * ((s - s0) / 4),
                4 * (p as int) <= 3 * (s - off),
                total_len <= p0 <= p,
                dest@.subrange(0, p as int) == out,
                fold_line(buf@, s as int, ee as int, e as int, out) == fold_line(
                    buf@,
                    s0 as int,
                    ee as int,
                    e as int,
                    out0,
                ),
            ensures
                dest@.len() == cap,
                cap == cap_of(len as int),
                e == off + len,
                off <= s0 <= s <= e,
                s0 == s_top + 1,
                ee == s0 + fl,
                out.len() == p,
                total_len <= p0 <= p,
                dest@.subrange(0, p as int) == out,
                err ==> !fold_line(buf@, s0 as int, ee as int, e as int, out0).1,
                !err ==> fold_line(buf@, s0 as int, ee as int, e as int, out0) == (out, true),
                !err ==> s >= ee,
                !err ==> (s - s0) % 4 == 0,
                !err ==> s - s0 <= 4 * nsteps(fl as int),
                4 * (p as int) <= 3 * (s - off),
                !err ==> p == p0 + 3 * ((s - s0) / 4),
            decreases e - s,
        {
            if e - s < 4 {
                err = true;
                break;
            }
            proof {
                lemma_store_in_bounds(len as int, p as int, s as int, off as int);
            }
            let b0: u8 = get_unchecked(buf, s);
            let b1: u8 = get_unchecked(buf, s + 1);
            let b2: u8 = get_unchecked(buf, s + 2);
            let b3: u8 = get_unchecked(buf, s + 3);
            vset_unchecked(&mut dest, p, dec(b0) << 2 | dec(b1) >> 4);
            vset_unchecked(&mut dest, p + 1, dec(b1) << 4 | dec(b2) >> 2);
            vset_unchecked(&mut dest, p + 2, dec(b2) << 6 | dec(b3));
            proof {
                let ghost out_new = out + grp(b0, b1, b2, b3);
                assert(dest@.subrange(0, (p + 3) as int) == out_new) by {
                    assert(dest@.subrange(0, (p + 3) as int).len() == out_new.len());
                    assert forall|i: int| 0 <= i < out_new.len() implies dest@.subrange(
                        0,
                        (p + 3) as int,
                    )[i] == out_new[i] by {
                        if i < p as int {
                            assert(out[i] == dest@.subrange(0, p as int)[i]);
                        }
                    }
                    assert(dest@.subrange(0, (p + 3) as int) =~= out_new);
                }
                out = out_new;
            }
            p = p + 3;
            s = s + 4;
        }
        if err {
            break;
        }
        proof {
            // The inner loop lands exactly on `s0 + 4*nsteps(fl)`, so `p` grew
            // by `3*nsteps(fl)`; and `ln <= 3*nsteps(fl)` is the bounded fact.
            // Together they re-establish `total_len <= p`, which is what makes
            // the final fold's reads in bounds.
            lemma_nsteps_exact(fl as int, (s - s0) as int);
            lemma_emit_covers_declared(ln as int);
        }
        total_len = total_len + ln;
        if ln < 45 {
            break;
        }
        if s >= e {
            break;
        }
        s = s + 1;
    }
    let mut acc: u64 = 0;
    if err {
        acc = 0xFFFF_FFFF;
    } else {
        proof {
            assert forall|i: int| 0 <= i < total_len as int implies #[trigger] dest@[i]
                == out[i] by {
                assert(0 <= i < p as int);
                assert(out[i] == dest@.subrange(0, p as int)[i]);
            }
            lemma_fold_prefix(dest@, out, total_len as int, 0);
        }
        let mut i: usize = 0;
        while i < total_len
            invariant
                i <= total_len <= p <= dest@.len(),
                out.len() == p,
                acc == fold_bytes(dest@, i as int, 0),
            decreases total_len - i,
        {
            acc = acc.wrapping_mul(31).wrapping_add(vget_unchecked(&dest, i) as u64);
            i = i + 1;
        }
        acc = acc.wrapping_mul(31).wrapping_add(total_len as u64);
    }
    acc ^ tally(cap)
}

// ---------------------------------------------------------------- driver ----
fn main() {
    let (n_iters, stride_w, bytes) = load_input();
    // SLB-DRIVER-BEGIN
    let n_blob: usize = bytes.len();
    let buf: &[u8] = bytes.as_slice();
    let mut acc: u64 = 0;
    if stride_w >= 1 && stride_w <= n_blob as u64 {
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
                1 <= stride <= n_blob,
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
            assert(r == uu_fold(buf@, (k * stride) as int, stride as int));
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    emit(acc);
}

} // verus!
