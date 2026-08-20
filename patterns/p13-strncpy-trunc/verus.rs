//! p13 rung R5 -- unsafe + Verus proof.
//!
//! R4's exec code verbatim, plus the specs and proofs that discharge every
//! unchecked read and every unchecked write in it.
//!
//! **What is new here is that the obligation and the fact that discharges it
//! are at DIFFERENT SITES.** Every earlier pattern's unchecked access is
//! licensed by a guard on the same value: p03's `sp < STACK_CAP` is in the same
//! basic block as the store, p12's `dlen + slen <= DST_CAP` is one loop level
//! above it, p11's scan terminates because the caller *gave* it a sentinel.
//! p13's consumer
//!
//!     let mut d: usize = 0;
//!     while dst_get_unchecked(&dst, d) != 0 { d = d + 1; }
//!
//! has **no bound at all** -- it is character for character C's runaway scan.
//! What makes it defined is a fact about the *contents* of the array, put there
//! by a different statement one line above:
//!
//!     dst[DST_CAP - 1] == 0   and   d < DST_CAP   =>   the read is in bounds
//!
//! and `d < DST_CAP` is re-established each iteration only because the body
//! runs under `dst@[d] != 0`, which with `dst@[DST_CAP - 1] == 0` gives
//! `d != DST_CAP - 1`. **The sentinel is not given; it is established, and it
//! has to be carried across a store into a loop.** That is the whole proof, and
//! it is why deleting the termination store does not merely weaken this file --
//! it makes the consumer loop unverifiable, which is the correct relation
//! between an omitted line and a proof.
//!
//!     requires  off + len <= buf@.len()
//!
//! ONE clause, as on p03, p11 and p12 and unlike p17. It is structural -- about
//! the shape of the buffer the driver built, not about its contents -- so it
//! holds on *every* input this benchmark runs, `adversarial-*` included, and
//! the gate checks it call by call. `nstr`, all 2^32 values of it, and every
//! byte of the window are attacker data and none of them is an assumption.
//!
//! **One program line exists to keep it at one clause**, and it is priced in
//! ../NOTES.md rather than described as free: `if q >= len { break; }` before
//! the cursor step, which is p11's line for p11's reason (`q + 1` is `len + 1`
//! when the window ends without a terminator, and vstd has no axiom that a
//! slice is at most `isize::MAX` bytes). Every p13 rung carries it, so no rung
//! comparison here moves on it. **p12's second line has no analogue here**:
//! p13's `n = min(slen, DST_CAP)` bounds the copy by a constant before any
//! addition happens, so there is no `dlen + slen` to overflow and no
//! `slen <= DST_CAP` conjunct to buy -- the `min` the C library performs for
//! you is, on this pattern, also the proof obligation it discharges for you.
//!
//! **The destination is threaded through `walk` as a `Seq<u8>`** even though
//! the copy plus the zero-fill overwrite all `DST_CAP` bytes on every string,
//! so the carried value is dead. Threading it keeps the spec a
//! *transliteration* of the program rather than an argument about it; the
//! independence is a consequence, not an assumption. (It is also what makes C's
//! uninitialised `uint8_t dst[32];` harmless: no byte is read before the copy
//! and the fill between them have written every one.)
//!
//! Note what the spec does **not** assume: that `nstr` is honest, that the
//! strings are terminated, or that they fit. `walk` is defined as the
//! *program's* walk, so `adversarial-truncate`, `adversarial-truncate-alt`,
//! `adversarial-nonul-dst` and `adversarial-nonul-src` are all inside the
//! verified domain and the kernel agrees with `model.py` on all four.
//!
//! TCB tally: NOTES.md 6. Five `external_body` items, three of them accessors
//! with a `requires`, all listed there individually, because an under-counted
//! TCB is how the pilot's fatal defect hid in plain sight
//! (`.memory/04-verus.md`).

use vstd::prelude::*;

// Plain-Rust I/O helpers. Outside `verus!`, so Verus treats the whole module as
// external (external-by-default). Reached only through `load_input`/`emit`.
#[path = "../../common/driver.rs"]
mod driver;

verus! {

// `group_slice_axioms` gives `slice@.len() == spec_slice_len(slice)`, hence
// `slice@.len() <= usize::MAX` -- without it `off + len` cannot be shown not to
// overflow `usize`. `group_array_axioms` gives `dst@.len() == DST_CAP` for a
// `[u8; DST_CAP]` and the fill axiom for `[0; DST_CAP]`; p03 needed it first
// and p12 second. `lemma_u128_shr_is_div` turns `x >> 64` into `x / 2^64`,
// which is what the driver's multiply-shift barrier bound is about, and the mul
// group is what the driver's window-offset bound `k * stride + stride <=
// n_blob` needs; the KERNEL needs neither.
broadcast use {
    vstd::slice::group_slice_axioms,
    vstd::array::group_array_axioms,
    vstd::bits::lemma_u128_shr_is_div,
    vstd::arithmetic::mul::lemma_mul_inequality,
};

/// The destination's capacity, a compile-time constant in every rung, and the
/// `n` every rung passes to `strncpy`.
///
/// A `const` inside `verus!` is its own obligation (`.memory/04-verus.md`,
/// measured on p08's `SCR` and again on p03's `STACK_CAP`), so this contributes
/// 1 to the count pinned in ../spec.md and the decomposition there says so.
pub const DST_CAP: usize = 32;

// ------------------------------------------------------------------ spec ----
/// The little-endian u32 at absolute byte position `p`, written out the way
/// every rung writes it: `b0 + 256*b1 + 65536*b2 + 16777216*b3`.
///
/// Spelled with `+` and `*` rather than `|` and `<<` on purpose
/// (`.memory/04-verus.md`): the two are the same function on bytes and compile
/// to the same instruction, but only the first is linear arithmetic.
pub open spec fn u32_at(buf: Seq<u8>, p: int) -> int {
    buf[p] as int + 256 * (buf[p + 1] as int) + 65536 * (buf[p + 2] as int)
        + 16777216 * (buf[p + 3] as int)
}

/// How many strings the window at `off` declares. **Declared, and it bounds
/// nothing** -- see `walk`.
pub open spec fn nstr_at(buf: Seq<u8>, off: int) -> int {
    u32_at(buf, off)
}

/// The destination every Rust rung starts from. C's `uint8_t dst[32];` is not
/// initialised, and that is harmless here for a reason the spec makes visible:
/// the copy and the zero-fill together write **every** slot before the consumer
/// reads any of them, so the carried value never reaches the result.
pub open spec fn zero_dst() -> Seq<u8> {
    Seq::new(DST_CAP as nat, |i: int| 0u8)
}

/// THE SOURCE SCAN: the index of the first zero byte at or after `q`, **capped
/// at the window end**. Bounded by the window in every rung, R1 included --
/// p13's bug is not here. p11 is the pattern that varies this function.
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

/// THE COPY, `strncpy`'s first half: `buf[off+p .. off+p+n)` into `dst[0..n)`,
/// one byte at a time, where `n == min(slen, DST_CAP)`.
///
/// Note there is no guard and no rejection: `strncpy` **always** copies `n`
/// bytes and `n` is capped by the destination's capacity, which is exactly why
/// this pattern's bug is not p12's. What is lost is everything past `n`, and
/// nothing in this function records that it existed.
pub open spec fn copy_into(dst: Seq<u8>, buf: Seq<u8>, off: int, p: int, i: int, n: int)
    -> Seq<u8>
    decreases n - i,
{
    if i >= n {
        dst
    } else {
        copy_into(dst.update(i, buf[off + p + i]), buf, off, p, i + 1, n)
    }
}

/// THE ZERO-FILL, `strncpy`'s second half and the one nobody expects:
/// `dst[i .. DST_CAP)` is set to zero. This is why `strncpy` costs
/// `O(DST_CAP)` per string however short the source is (../NOTES.md 3), and it
/// is also the only reason a short string ends up terminated at all -- the
/// terminator R1 relies on is a *side effect of the padding*, not something
/// `strncpy` wrote on purpose.
pub open spec fn fill_zero(dst: Seq<u8>, i: int) -> Seq<u8>
    decreases DST_CAP - i,
{
    if i >= DST_CAP as int {
        dst
    } else {
        fill_zero(dst.update(i, 0u8), i + 1)
    }
}

/// THE CONSUMER: the index of the first zero byte of `dst` at or after `d`,
/// **capped at `DST_CAP`**.
///
/// The cap is what makes this a total spec function. **The exec rungs have no
/// cap at all** -- `while dst[d] != 0 { d += 1 }` -- and are defined only
/// because `dst@[DST_CAP - 1] == 0` holds when they run it. That gap is the
/// pattern: R1 executes the uncapped scan on a destination where the fact does
/// not hold, and the cap here is never reached in any verified execution.
pub open spec fn scan_dst(dst: Seq<u8>, d: int) -> int
    decreases DST_CAP - d,
{
    if d >= DST_CAP as int {
        DST_CAP as int
    } else if dst[d] == 0 {
        d
    } else {
        scan_dst(dst, d + 1)
    }
}

/// What the kernel returns once the walk is over: mix in the declared count, so
/// a rung that walked a different number of strings cannot produce the same
/// checksum.
pub open spec fn fin(acc: u64, nstr: int) -> u64 {
    acc.wrapping_mul(31).wrapping_add(nstr as u64)
}

/// THE MACHINE. Strings `s .. nstr`, carrying the destination contents, the
/// cursor and the accumulator.
///
/// **The walk stops at `q + 1 >= len` whatever `nstr` says**, which is the exec
/// rungs' `if q >= len { break; } p = q + 1; if p >= len { break; }` -- the two
/// guards together are exactly `q + 1 >= len`, and the first of them is what
/// makes `q + 1` provably free of `usize` overflow (see this file's header).
///
/// **The termination store is here, and it is the line R1 omits.** Note where
/// it sits: *after* the copy and the fill, *before* the consumer. Remove
/// `.update(DST_CAP - 1, 0)` and this spec still type-checks and still means
/// something -- `scan_dst`'s cap keeps it total -- but the exec code that
/// implements it can no longer be verified, because nothing then bounds `d`.
pub open spec fn walk(
    buf: Seq<u8>,
    off: int,
    len: int,
    s: int,
    nstr: int,
    p: int,
    dst: Seq<u8>,
    acc: u64,
) -> u64
    decreases nstr - s,
{
    if s >= nstr {
        fin(acc, nstr)
    } else {
        let q = scan_end(buf, off, len, p);
        let slen = q - p;
        let n = if slen < DST_CAP as int {
            slen
        } else {
            DST_CAP as int
        };
        let dst2 = fill_zero(copy_into(dst, buf, off, p, 0, n), n).update(DST_CAP - 1, 0u8);
        let d = scan_dst(dst2, 0);
        let acc2 = acc.wrapping_mul(31).wrapping_add(d as u64).wrapping_mul(31).wrapping_add(
            dst2[0] as u64,
        );
        if q + 1 >= len {
            fin(acc2, nstr)
        } else {
            walk(buf, off, len, s + 1, nstr, q + 1, dst2, acc2)
        }
    }
}

/// What the kernel returns.
///
/// The two early exits are the tests every rung keeps, R1 included: a window
/// too short to hold the header, and a zero count. **R1 keeps both.** What R1
/// omits is the `.update(DST_CAP - 1, 0)` in `walk`, and that is the only thing
/// it omits.
pub open spec fn strncpy_fold(buf: Seq<u8>, off: int, len: int) -> u64 {
    if len < 4 {
        0
    } else if nstr_at(buf, off) == 0 {
        0
    } else {
        walk(buf, off, len, 0, nstr_at(buf, off), 4, zero_dst(), 0)
    }
}

// ------------------------------------------------------------------- TCB ----
// TRUSTED ITEM 1 of 5. vstd ships no specification for `<[T]>::get_unchecked`,
// so this is the axiom that licenses the unchecked read of the SOURCE window.
// It is sound because the standard library's documented contract for
// `get_unchecked` is exactly this: if the caller guarantees `i < v.len()`, the
// call is defined and yields `v[i]`. Identical, character for character, to the
// accessor p01, p02, p03, p05, p07, p11, p12, p16 and p17 ship.
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

// TRUSTED ITEM 2 of 5, and **the item p13 exists for**: the DESTINATION read
// performed by the consumer scan. p03's `stack_get_unchecked` and p12's
// `dst_get_unchecked` are the same item on `[u64; 64]` and `[u8; 128]`.
//
// What is different is not the item, it is where its `requires` comes from. On
// p03 and p12 every call site is inside an `if` or a loop whose *bound* is the
// discharging fact. Here the only call site that matters is inside a loop with
// no bound at all, and `i < v@.len()` is discharged from `v@[DST_CAP - 1] == 0`
// -- a fact about the array's CONTENTS, established by trusted item 3 one
// statement earlier.
//
// The `requires` is ONE conjunct and NOT `i < v@.len(), v@.len() == 32`: for a
// `&[u8; 32]` the second is a TAUTOLOGY, discharged from the parameter type
// alone by vstd's `array_len_matches_n`, and p03's gate run caught exactly that
// draft (`.memory/04-verus.md`; p03 NOTES.md 5b).
#[inline(always)]
#[verifier::external_body]
fn dst_get_unchecked(v: &[u8; 32], i: usize) -> (r: u8)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    unsafe { *v.get_unchecked(i) }
}

// THE VERIFIED TWIN of trusted item 2.
#[cfg(slb_twin)]
fn slb_twin_dst_get_unchecked(v: &[u8; 32], i: usize) -> (r: u8)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    v[i]
}

// TRUSTED ITEM 3 of 5: the unchecked STORE into the fixed destination. It
// performs the copy, the zero-fill AND the termination store -- so the line R1
// omits goes through this item too, which is why its `ensures` has to be a
// whole-sequence equality and not a statement about slot `i` alone.
//
// `update` says both "slot `i` became `x`" and "nothing else moved", the shape
// `.memory/02-bench-rules.md` argues for in its p02 worked example. On p13 the
// second half is what carries the sentinel: after
// `dst_set_unchecked(&mut dst, DST_CAP - 1, 0)` the proof needs
// `dst@[DST_CAP - 1] == 0`, and an `ensures` that only constrained the written
// slot would give exactly that -- but the *copy* loop's `ensures` would then
// not constrain the rest of the array and the sentinel could not survive to the
// consumer. p12's justification for the same shape was about bytes appearing at
// slots the caller never asked for; p13's is about a byte still being where a
// previous store put it.
//
// `x` is a pure VALUE parameter -- stored, never used as an address or a length
// -- so it has no precondition, and `../spec.md`'s
// `verus.unsafe_justifications` says so and the gate shouts it every run.
// `.memory/04-verus.md` names this false positive of the parameter-coverage
// rule; p03 was the first pattern to exercise it, p12 the second.
#[inline(always)]
#[verifier::external_body]
fn dst_set_unchecked(v: &mut [u8; 32], i: usize, x: u8)
    requires
        i < old(v)@.len(),
    ensures
        final(v)@ == old(v)@.update(i as int, x),
{
    unsafe {
        *v.get_unchecked_mut(i) = x;
    }
}

// THE VERIFIED TWIN of trusted item 3. `v[i] = x` is the checked stand-in for
// `*v.get_unchecked_mut(i) = x`; weaken the shared `requires` and Verus rejects
// the indexed store.
#[cfg(slb_twin)]
fn slb_twin_dst_set_unchecked(v: &mut [u8; 32], i: usize, x: u8)
    requires
        i < old(v)@.len(),
    ensures
        final(v)@ == old(v)@.update(i as int, x),
{
    v[i] = x;
}

// TRUSTED ITEM 4 of 5. Argument parsing, file I/O and little-endian decoding,
// delegated to common/driver.rs so that all eight rungs read the file the same
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
        r == strncpy_fold(buf@, off as int, len as int),
{
    // Ghost only: mentioning `spec_slice_len` fires vstd's `axiom_spec_len`,
    // which is what tells the SMT solver a slice length fits in a `usize` --
    // needed to rule out `off + len` overflowing. Erases at compile time.
    assert(buf@.len() == vstd::slice::spec_slice_len(buf));
    if len < 4 {
        return 0;
    }
    let nstr: usize = buf_get_unchecked(buf, off) as usize + 256 * (buf_get_unchecked(
        buf,
        off + 1,
    ) as usize) + 65536 * (buf_get_unchecked(buf, off + 2) as usize) + 16777216 * (
    buf_get_unchecked(buf, off + 3) as usize);
    if nstr == 0 {
        return 0;
    }
    let mut dst: [u8; DST_CAP] = [0; DST_CAP];
    // Ghost only: `[0; 32]`'s view IS the all-zeros sequence. vstd's
    // `axiom_spec_array_fill_for_copy_type` gives it pointwise; `=~=` lifts
    // that to sequence equality.
    assert(dst@ =~= zero_dst());
    let mut acc: u64 = 0;
    let mut p: usize = 4;
    let mut s: usize = 0;
    // "The strings from here, with the destination we have built and where the
    // cursor is, are all the strings." p16's/p11's/p12's relational shape. This
    // loop exits TWO ways (`s == nstr` and the window running out), so it needs
    // `invariant_except_break` plus a loop `ensures`.
    while s < nstr
        invariant_except_break
            s <= nstr,
            0 < nstr,
            nstr == nstr_at(buf@, off as int),
            4 <= len,
            4 <= p <= len,
            dst@.len() == DST_CAP,
            off + len <= buf@.len(),
            buf@.len() <= usize::MAX,
            walk(buf@, off as int, len as int, s as int, nstr as int, p as int, dst@, acc)
                == walk(buf@, off as int, len as int, 0, nstr as int, 4, zero_dst(), 0),
        ensures
            walk(buf@, off as int, len as int, 0, nstr as int, 4, zero_dst(), 0) == fin(
                acc,
                nstr as int,
            ),
        decreases nstr - s,
    {
        let ghost p_before = p as int;
        let ghost s_before = s as int;
        let ghost acc_before = acc;
        let ghost dst_before = dst@;
        let mut q: usize = p;
        // "The scan from here is the whole scan." p11's invariant verbatim:
        // there is no closed form for where a NUL scan stops, so this is the
        // only shape it can take.
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
            if buf_get_unchecked(buf, off + q) == 0 {
                break;
            }
            q = q + 1;
        }
        let slen: usize = q - p;
        // `strncpy`'s `n`. It is a `min` against a compile-time constant, so
        // unlike p12's `dlen + slen <= DST_CAP` there is no addition to prove
        // overflow-free and no extra conjunct to buy.
        let n: usize = if slen < DST_CAP {
            slen
        } else {
            DST_CAP
        };
        let mut i: usize = 0;
        // "The copy from here is the whole copy." p12's copy invariant with the
        // destination cursor replaced by `i` -- p13 always starts at slot 0,
        // which is what makes this the easy half of the proof.
        while i < n
            invariant
                i <= n <= DST_CAP,
                n as int <= q as int - p as int,
                p <= q <= len,
                dst@.len() == DST_CAP,
                off + len <= buf@.len(),
                buf@.len() <= usize::MAX,
                copy_into(dst@, buf@, off as int, p as int, i as int, n as int) == copy_into(
                    dst_before,
                    buf@,
                    off as int,
                    p as int,
                    0,
                    n as int,
                ),
            decreases n - i,
        {
            let b: u8 = buf_get_unchecked(buf, off + p + i);
            dst_set_unchecked(&mut dst, i, b);
            i = i + 1;
        }
        let ghost dst_copied = dst@;
        let mut j: usize = n;
        // "The fill from here is the whole fill." Same shape, on the half of
        // `strncpy` that costs `DST_CAP - n` bytes of writing nobody asked for.
        while j < DST_CAP
            invariant
                n <= j <= DST_CAP,
                dst@.len() == DST_CAP,
                fill_zero(dst@, j as int) == fill_zero(dst_copied, n as int),
            decreases DST_CAP - j,
        {
            dst_set_unchecked(&mut dst, j, 0);
            j = j + 1;
        }
        // THE TERMINATION, and the line R1 omits. Everything below depends on
        // it: it is what puts a zero byte in the last slot, and the zero byte
        // is what bounds the consumer.
        dst_set_unchecked(&mut dst, DST_CAP - 1, 0);
        let mut d: usize = 0;
        // THE CONSUMER, unbounded, and the obligation this pattern exists for.
        // `d < DST_CAP` is not a loop bound -- there is none -- it is an
        // invariant re-established from the CONTENTS of the array: the body
        // runs only when `dst@[d] != 0`, and `dst@[DST_CAP - 1] == 0`, so
        // `d != DST_CAP - 1` and `d + 1 < DST_CAP`.
        while dst_get_unchecked(&dst, d) != 0
            invariant
                d < DST_CAP,
                dst@.len() == DST_CAP,
                dst@[DST_CAP - 1] == 0u8,
                scan_dst(dst@, d as int) == scan_dst(dst@, 0),
            decreases DST_CAP - d,
        {
            assert(dst@[d as int] != 0u8);
            assert(d != DST_CAP - 1);
            d = d + 1;
        }
        assert(d as int == scan_dst(dst@, 0));
        acc = acc.wrapping_mul(31).wrapping_add(d as u64);
        acc = acc.wrapping_mul(31).wrapping_add(dst_get_unchecked(&dst, 0) as u64);
        // Ghost only: unfold `walk` once at the value it had on entry to this
        // iteration. Its `q` IS the scan loop's `q`, its `n` IS the `min` above,
        // its `copy_into`/`fill_zero`/`update` IS what the three loops and the
        // termination store built, and its `scan_dst` IS what the consumer
        // found -- so the state this iteration produced is the one the spec
        // produces, and the spec's `q + 1 >= len` test is the two `break`s
        // below.
        assert(walk(buf@, off as int, len as int, s_before, nstr as int, p_before, dst_before,
            acc_before) == if q as int + 1 >= len as int {
            fin(acc, nstr as int)
        } else {
            walk(buf@, off as int, len as int, s_before + 1, nstr as int, q as int + 1, dst@,
                acc)
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
            assert(r == strncpy_fold(buf@, (k * stride) as int, stride as int));
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    emit(acc);
}

} // verus!
