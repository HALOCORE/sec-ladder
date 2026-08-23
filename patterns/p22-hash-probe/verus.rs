//! p22 rung R5 -- unsafe + Verus proof.
//!
//! R4's exec code verbatim, plus the specs and proofs that discharge every
//! unchecked read and write in it -- **and one obligation that is not about
//! memory at all and that no other R5 in this tree has: `decreases` on the
//! probe loop.**
//!
//! ⚠⚠ **THIS IS THE FIRST TERMINATION PROOF IN THE PROJECT.** Every other R5
//! here proves that an access is in bounds, that a pointer is live, or that a
//! fold computes the declared function. p22's bug is none of those: `c/kernel.c`
//! reads nothing out of bounds, frees nothing twice and executes no undefined
//! behaviour. It simply never returns. So the interesting question is not
//! *"does the proof catch the bug?"* but *"is there an obligation for the bug to
//! violate at all?"*, and the answer is measured rather than argued:
//!
//! ```text
//! error: loop must have a decreases clause
//!     = help: to disable this check, use #[verifier::exec_allows_no_decreases_clause]
//! ```
//!
//! **Verus demands a termination measure for every exec loop by default**, and
//! the opt-out is a named attribute that a reader and a grep can both see.
//! Delete `&& nfill < TABCAP` from the exec code below -- the one conjunct
//! `c/kernel.c` omits -- and this file stops verifying: `precondition not
//! satisfied` on `lemma_exists_empty`, whose precondition is exactly *"some slot
//! is still EMPTY"*, plus `invariant not satisfied` on the functional
//! invariant. ../NOTES.md 10 has all of the mutants and their output.
//!
//! **HOW THE MEASURE WORKS, because the obvious two both fail.**
//!
//!   * `decreases TABCAP - i` is wrong: `i` WRAPS, so it does not decrease.
//!     `.memory/04-verus.md` already records that `decreases b - a` fails on
//!     two-cursor loops; a ring cursor is that failure in its purest form.
//!   * A ghost SET of visited slots with `decreases TABCAP - |visited|` is
//!     faithful but needs set-cardinality reasoning inside the invariant.
//!   * A probe COUNTER in the exec code, `decreases TABCAP - probes`, is trivial
//!     -- and would be the fix wearing the proof's clothes: the exec code would
//!     then be bounded and the `decreases` would be proving something the loop
//!     no longer needed proved. **That route is not taken here** and ../NOTES.md
//!     8 measures what it would have cost.
//!
//! What ships is neither: a **ghost UNWRAPPED cursor** `u` with the invariant
//! `i == u % TABCAP`, and a **ghost witness** `e` for an EMPTY slot obtained
//! from `nfill < TABCAP` through a counting lemma. `d` is the distance from the
//! starting slot to `e`, and the measure is `h + d - u`. Every one of `u`, `e`
//! and `d` is ghost, so **the exec code is byte-identical to unsafe.rs** and
//! ../spec.md pins that it is. The proof consumes the guard the hardened rung
//! needs anyway; it does not add anything to the program.
//!
//!     requires  off + len <= buf@.len()
//!
//! ONE clause, as on p03, p06, p10, p11, p12, p14, p18, p27, p38 and p47 and
//! unlike p17. It is structural -- about the shape of the buffer the driver
//! built, not about its contents -- so it holds on *every* input this benchmark
//! runs, `adversarial-*` included, and the gate checks it call by call. `nkey`
//! and every key byte are attacker data and none of them is an assumption. In
//! particular **there is no `requires` that the window has fewer than TABCAP
//! distinct keys**; a precondition about the contents of a file is one no loader
//! can discharge (`.memory/02-bench-rules.md`), and it would delete the whole
//! pattern. `nfill < TABCAP` is a fact the kernel MAINTAINS, not one it assumes.
//!
//! **THE SPECIFICATION'S PROBE IS BOUNDED AND THE IMPLEMENTATION'S IS NOT**, and
//! that asymmetry is deliberate. `probe` below carries `fuel` and `decreases
//! fuel`, because a spec function must terminate to be a function at all; the
//! exec loop carries no bound. The `decreases` on the exec loop is exactly what
//! says the two land in the same slot. `model.py`'s `_probe` mirrors the
//! fuel-bounded one, step for step.
//!
//! The little-endian header is decoded with `+` and `*` rather than `|` and
//! `<<`, and the hash with `/` and `%` rather than `>>` and `&`
//! (`.memory/04-verus.md`): each pair is the same function on unsigned values
//! and compiles to the same instruction, but only the first of each is linear
//! arithmetic. **There is no bit operation anywhere in this file**, so there is
//! no `by (bit_vector)`.
//!
//! TCB tally: ../NOTES.md 7. **Five** `external_body` items, **three** of them
//! with contracts -- p27's shape minus the two allocator items, because p22
//! allocates nothing.
//!
//! SAFETY (1): `off + len <= buf.len()` is the caller's structural
//!   precondition. Discharged at the call site by the driver's proof below.
//! SAFETY (2): `len >= 4` guards the window header.
//! SAFETY (3): a key is read only under `len - p >= 1` with `p <= len`.
//! SAFETY (4): every table index is `% TABCAP`, so `i < TABCAP` unconditionally.
//! SAFETY (5): the probe loop terminates -- the `decreases` above.

// Plain-Rust I/O helpers. Outside `verus!`, so Verus treats the whole module as
// external (external-by-default). Reached only through `load_input`/`emit`.
#[path = "../../common/driver.rs"]
mod driver;

use vstd::prelude::*;

verus! {

// p22 targets x86-64 only (`.memory/00-environment.md`). Verus treats `usize`
// as architecture-independent by default, so `(k as usize) * 2654435761` on a
// byte read from a file is `possible arithmetic overflow` on a hypothetical
// 32-bit target. This declaration is CHECKED by Verus against the actual
// compilation target rather than assumed, so it is not an axiom and adds
// nothing to the TCB.
global size_of usize == 8;

// `group_slice_axioms` gives `slice@.len() == spec_slice_len(slice)`, hence
// `slice@.len() <= usize::MAX` -- without it `off + len` cannot be shown not to
// overflow `usize`. `group_array_axioms` gives `tab@.len() == TABCAP` for a
// `[u8; TABCAP]` and the fill axiom for `[EMPTY; TABCAP]`.
// `lemma_u128_shr_is_div` turns `x >> 64` into `x / 2^64`, the driver's
// multiply-shift barrier bound, and the mul group is what the driver's
// window-offset bound needs; the KERNEL needs neither.
broadcast use {
    vstd::slice::group_slice_axioms,
    vstd::array::group_array_axioms,
    vstd::bits::lemma_u128_shr_is_div,
    vstd::arithmetic::mul::lemma_mul_inequality,
};

/// The table's extent, a compile-time constant in every rung. A power of two,
/// so `% TABCAP` lowers to a mask.
///
/// A `const` inside `verus!` is its own obligation (`.memory/04-verus.md`,
/// measured on p08's `SCR`), so this contributes 1 to the count pinned in
/// ../spec.md and the decomposition there says so.
pub const TABCAP: usize = 64;

/// The EMPTY sentinel. Key 0 is therefore not storable and folds SENT.
pub const EMPTY: u8 = 0;

/// What a rejected key folds. A compile-time constant in every rung.
pub const SENT: u64 = 251;

// ------------------------------------------------------------------ spec ----
/// The little-endian u32 at absolute byte position `p`, written out the way
/// every rung writes it: `b0 + 256*b1 + 65536*b2 + 16777216*b3`.
pub open spec fn u32_at(buf: Seq<u8>, p: int) -> int {
    buf[p] as int + 256 * (buf[p + 1] as int) + 65536 * (buf[p + 2] as int) + 16777216 * (
    buf[p + 3] as int)
}

/// How many keys the window at `off` declares. **Declared, and it bounds
/// nothing** -- the `len - p < 1` cursor guard is what stops the walk.
pub open spec fn nkey_at(buf: Seq<u8>, off: int) -> int {
    u32_at(buf, off)
}

/// The hash, written `/` and `%` rather than `>>` and `&` so that the whole
/// specification stays inside linear arithmetic.
pub open spec fn hash_s(k: u8) -> int {
    (k as int * 2654435761) / 16777216 % (TABCAP as int)
}

/// How many of `s[0..n]` are not EMPTY. **This is what `nfill` counts**, and
/// the outer loop carries the equality as an invariant.
pub open spec fn count_ne(s: Seq<u8>, n: int) -> int
    decreases n,
{
    if n <= 0 {
        0
    } else {
        count_ne(s, n - 1) + if s[n - 1] != EMPTY {
            1int
        } else {
            0int
        }
    }
}

/// Where a linear probe from slot `i` for key `k` lands.
///
/// ⚠ **`fuel` is what makes this a FUNCTION.** A spec function must terminate,
/// and the exec loop it describes need not; `TABCAP` steps is enough because the
/// exec loop is only ever entered when an EMPTY slot exists, and the proof in
/// `kernel` is what establishes that. `model.py`'s `_probe` is the same walk.
pub open spec fn probe(tab: Seq<u8>, i: int, k: u8, fuel: nat) -> int
    decreases fuel,
{
    if fuel == 0 {
        i
    } else if tab[i] == EMPTY || tab[i] == k {
        i
    } else {
        probe(tab, (i + 1) % (TABCAP as int), k, (fuel - 1) as nat)
    }
}

/// The table as the kernel starts it: TABCAP EMPTY slots.
pub open spec fn empty_tab() -> Seq<u8> {
    Seq::new(TABCAP as nat, |j: int| EMPTY)
}

/// THE ABSTRACT MACHINE, and the whole functional specification.
///
/// Note what it says and does not say: it describes the PROGRAM -- stop when
/// the window runs out, reject the EMPTY sentinel as a key, reject everything
/// once the table is full, otherwise probe and insert -- and it says nothing
/// about `nkey` being honest or about the key stream being well formed. Every
/// adversarial input is inside this domain (`../spec.md`).
pub open spec fn run(
    buf: Seq<u8>,
    off: int,
    len: int,
    t: int,
    nkey: int,
    p: int,
    tab: Seq<u8>,
    nfill: int,
    acc: u64,
) -> u64
    decreases nkey - t,
{
    if t >= nkey || len - p < 1 {
        acc.wrapping_mul(31).wrapping_add(nfill as u64)
    } else {
        let k = buf[off + p];
        if k != EMPTY && nfill < TABCAP as int {
            let i = probe(tab, hash_s(k), k, TABCAP as nat);
            if tab[i] == EMPTY {
                run(
                    buf,
                    off,
                    len,
                    t + 1,
                    nkey,
                    p + 1,
                    tab.update(i, k),
                    nfill + 1,
                    acc.wrapping_mul(31).wrapping_add(i as u64),
                )
            } else {
                run(
                    buf,
                    off,
                    len,
                    t + 1,
                    nkey,
                    p + 1,
                    tab,
                    nfill,
                    acc.wrapping_mul(31).wrapping_add(i as u64),
                )
            }
        } else {
            run(
                buf,
                off,
                len,
                t + 1,
                nkey,
                p + 1,
                tab,
                nfill,
                acc.wrapping_mul(31).wrapping_add(SENT),
            )
        }
    }
}

/// What the kernel must return.
pub open spec fn key_fold(buf: Seq<u8>, off: int, len: int) -> u64 {
    if len < 4 {
        0
    } else if nkey_at(buf, off) == 0 {
        0
    } else {
        run(buf, off, len, 0, nkey_at(buf, off), 4, empty_tab(), 0, 0)
    }
}

// ---------------------------------------------------------------- lemmas ----
/// An all-EMPTY prefix counts 0. Establishes the outer invariant at entry.
proof fn lemma_count_zero(s: Seq<u8>, n: int)
    requires
        0 <= n <= s.len(),
        forall|j: int| 0 <= j < n ==> s[j] == EMPTY,
    ensures
        count_ne(s, n) == 0,
    decreases n,
{
    if n > 0 {
        lemma_count_zero(s, n - 1);
    }
}

/// A prefix with no EMPTY slot counts its own length. The contrapositive of
/// this is the whole termination argument.
proof fn lemma_all_ne(s: Seq<u8>, n: int)
    requires
        0 <= n <= s.len(),
        forall|j: int| 0 <= j < n ==> s[j] != EMPTY,
    ensures
        count_ne(s, n) == n,
    decreases n,
{
    if n > 0 {
        lemma_all_ne(s, n - 1);
    }
}

/// **THE TERMINATION LEMMA.** `nfill < TABCAP` -- which is exactly
/// `count_ne(tab, TABCAP) < TABCAP` under the outer invariant -- yields a slot
/// that is EMPTY, and an EMPTY slot is what stops the probe.
proof fn lemma_exists_empty(s: Seq<u8>)
    requires
        s.len() == TABCAP as int,
        count_ne(s, TABCAP as int) < TABCAP as int,
    ensures
        exists|j: int| 0 <= j < TABCAP as int && s[j] == EMPTY,
{
    if !(exists|j: int| 0 <= j < TABCAP as int && s[j] == EMPTY) {
        assert(forall|j: int| 0 <= j < TABCAP as int ==> s[j] != EMPTY);
        lemma_all_ne(s, TABCAP as int);
        assert(false);
    }
}

/// `count_ne` depends only on the prefix it counts.
proof fn lemma_count_congr(s: Seq<u8>, t: Seq<u8>, n: int)
    requires
        0 <= n <= s.len(),
        n <= t.len(),
        forall|j: int| 0 <= j < n ==> s[j] == t[j],
    ensures
        count_ne(s, n) == count_ne(t, n),
    decreases n,
{
    if n > 0 {
        lemma_count_congr(s, t, n - 1);
    }
}

/// Filling one EMPTY slot raises the count by exactly one. Re-establishes the
/// outer invariant after an insert.
proof fn lemma_count_update(s: Seq<u8>, i: int, x: u8, n: int)
    requires
        0 <= i < n <= s.len(),
        s[i] == EMPTY,
        x != EMPTY,
    ensures
        count_ne(s.update(i, x), n) == count_ne(s, n) + 1,
    decreases n,
{
    if i == n - 1 {
        lemma_count_congr(s, s.update(i, x), n - 1);
    } else {
        lemma_count_update(s, i, x, n - 1);
    }
}

// ------------------------------------------------------------------- TCB ----
// TRUSTED ITEM 1 of 5. vstd ships no specification for `<[T]>::get_unchecked`,
// so this is the axiom that licenses the unchecked read of the window. It is
// sound because the standard library's documented contract for `get_unchecked`
// is exactly this: if the caller guarantees `i < v.len()`, the call is defined
// and yields `v[i]`. Identical, character for character, to the accessor p01,
// p02, p03, p05, p06, p07, p11, p12, p13, p14, p16, p17, p27, p38 and p47 ship.
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

// TRUSTED ITEM 2 of 5. The unchecked TABLE read, generic over the element type
// for uniformity with p27's pair. vstd ships no specification for
// `<[T; N]>::get_unchecked`, and the standard library's documented contract is
// exactly this `requires`/`ensures` pair.
//
// ⚠ **Unlike p27's, it is worth NOTHING at `-O3`** -- `i` is `% TABCAP` with
// TABCAP a power-of-two constant, so rustc's check on `tab[i]` is already dead
// in the safe rungs. It is here for R4/R5 identity and for `-O0`. The measured
// figure is in ../NOTES.md 4 rather than in this comment.
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

// TRUSTED ITEM 3 of 5. The unchecked TABLE store, same shape. The `ensures` is a
// whole-sequence equality (`update`), not a statement about slot `i` alone, so
// it says both "slot `i` became `x`" and "nothing else moved" -- and the second
// half is load-bearing here in a way it is not elsewhere: `count_ne` quantifies
// over the WHOLE table, so a store that could disturb another slot would break
// the fullness invariant and with it the termination argument.
//
// `x` is a pure VALUE parameter -- stored, never used as an address or a length
// -- so it has no precondition, and `../spec.md`'s `verus.unsafe_justifications`
// says so and the gate shouts it every run. `.memory/04-verus.md` names this
// false positive of the parameter-coverage rule; p03 was the first pattern to
// exercise it, p12 the second, p06 the third, p14 the fourth and p27 the fifth.
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

// ---------------------------------------------------------------- kernel ----
// Same exec code as unsafe.rs. Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> (r: u64)
    requires
        off + len <= buf@.len(),
    ensures
        r == key_fold(buf@, off as int, len as int),
{
    // Ghost only: mentioning `spec_slice_len` fires vstd's `axiom_spec_len`,
    // which is what tells the SMT solver a slice length fits in a `usize`.
    assert(buf@.len() == vstd::slice::spec_slice_len(buf));
    if len < 4 {
        return 0;
    }
    let nkey: usize = buf_get_unchecked(buf, off) as usize + 256 * (buf_get_unchecked(
        buf,
        off + 1,
    ) as usize) + 65536 * (buf_get_unchecked(buf, off + 2) as usize) + 16777216 * (
    buf_get_unchecked(buf, off + 3) as usize);
    if nkey == 0 {
        return 0;
    }
    let mut tab: [u8; TABCAP] = [EMPTY; TABCAP];
    let mut nfill: usize = 0;
    let mut acc: u64 = 0;
    let mut p: usize = 4;
    let mut t: usize = 0;
    proof {
        assert(tab@ =~= empty_tab());
        lemma_count_zero(tab@, TABCAP as int);
    }
    // "The keys from here, with the table we have built, are all the keys."
    // p14's, p06's and p27's relational shape. This loop exits TWO ways
    // (`t == nkey` and the window-exhausted break), so it needs
    // `invariant_except_break` plus a loop `ensures`.
    while t < nkey
        invariant_except_break
            t <= nkey,
            4 <= p <= len,
            off + len <= buf@.len(),
            buf@.len() <= usize::MAX,
            tab@.len() == TABCAP as int,
            nfill <= TABCAP,
            // THE FULLNESS INVARIANT. `nfill` is not a hint: it is exactly the
            // number of non-EMPTY slots, and that is what makes
            // `nfill < TABCAP` mean "an EMPTY slot exists".
            count_ne(tab@, TABCAP as int) == nfill as int,
            run(
                buf@,
                off as int,
                len as int,
                t as int,
                nkey as int,
                p as int,
                tab@,
                nfill as int,
                acc,
            ) == run(
                buf@,
                off as int,
                len as int,
                0,
                nkey as int,
                4,
                empty_tab(),
                0,
                0,
            ),
        ensures
            acc.wrapping_mul(31).wrapping_add(nfill as u64) == run(
                buf@,
                off as int,
                len as int,
                0,
                nkey as int,
                4,
                empty_tab(),
                0,
                0,
            ),
        decreases nkey - t,
    {
        if len - p < 1 {
            break;
        }
        let k: u8 = buf_get_unchecked(buf, off + p);
        p = p + 1;
        // >>> THE SAFETY LINE. `&& nfill < TABCAP` is what c/kernel.c omits.
        // Here it is also the hypothesis of `lemma_exists_empty` below, i.e.
        // the whole termination argument. <<<
        if k != EMPTY && nfill < TABCAP {
            let i0: usize = (k as usize) * 2654435761 / 16777216 % TABCAP;
            assert(i0 as int == hash_s(k));
            // Ghost only: an EMPTY slot exists, because `nfill < TABCAP` and
            // `nfill` counts the non-EMPTY ones.
            proof {
                lemma_exists_empty(tab@);
            }
            let ghost e: int = choose|j: int| 0 <= j < TABCAP as int && tab@[j] == EMPTY;
            let ghost d: int = if e >= i0 as int {
                e - i0 as int
            } else {
                e + TABCAP as int - i0 as int
            };
            let ghost mut u: int = i0 as int;
            let mut i: usize = i0;
            assert((i0 as int + d) % (TABCAP as int) == e) by {
                if e < i0 as int {
                    assert((e + TABCAP as int) % (TABCAP as int) == e) by (nonlinear_arith)
                        requires
                            0 <= e < TABCAP as int,
                    ;
                }
            }
            // THE PROBE LOOP. Byte-identical to unsafe.rs's: `u`, `e` and `d`
            // are ghost and erase. It is UNBOUNDED in the exec code, and the
            // `decreases` is what says it stops -- the cursor cannot pass `e`,
            // and `e` is EMPTY.
            while arr_get_unchecked(&tab, i) != EMPTY && arr_get_unchecked(&tab, i) != k
                invariant
                    0 <= i < TABCAP,
                    0 <= d < TABCAP as int,
                    i0 as int <= u <= i0 as int + d,
                    i as int == u % (TABCAP as int),
                    (i0 as int + d) % (TABCAP as int) == e,
                    0 <= e < TABCAP as int,
                    tab@[e] == EMPTY,
                    tab@.len() == TABCAP as int,
                    probe(tab@, i0 as int, k, TABCAP as nat) == probe(
                        tab@,
                        i as int,
                        k,
                        (TABCAP as int - (u - i0 as int)) as nat,
                    ),
                    u - i0 as int <= d,
                decreases i0 as int + d - u,
            {
                i = (i + 1) % TABCAP;
                proof {
                    u = u + 1;
                }
            }
            assert(i as int == probe(tab@, hash_s(k), k, TABCAP as nat));
            if arr_get_unchecked(&tab, i) == EMPTY {
                proof {
                    lemma_count_update(tab@, i as int, k, TABCAP as int);
                }
                arr_set_unchecked(&mut tab, i, k);
                nfill = nfill + 1;
            }
            acc = acc.wrapping_mul(31).wrapping_add(i as u64);
        } else {
            acc = acc.wrapping_mul(31).wrapping_add(SENT);
        }
        t = t + 1;
    }
    acc.wrapping_mul(31).wrapping_add(nfill as u64)
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
        // Ghost only: at least one whole window is present.
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
            assert(r == key_fold(buf@, (k * stride) as int, stride as int));
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    emit(acc);
}

} // verus!
