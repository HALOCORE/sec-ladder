//! p06 rung R5 -- unsafe + Verus proof.
//!
//! R4's exec code verbatim, plus the specs and proofs that discharge every
//! unchecked read AND every unchecked WRITE in it.
//!
//! **The obligation is a rotation, and the postcondition is the FUNCTIONAL one.**
//! The kernel's `ensures` says the scratch ends up rotated left by `r mod m` --
//! not merely that nothing was accessed out of bounds. That distinction is the
//! whole of p06: `controls/gen_controls.py` builds the same kernel with the
//! reduction deleted, and the memory-safety-only spec ACCEPTS it in regime 1
//! (`m <= r <= SCR`) while this postcondition rejects it in both regimes.
//! ../NOTES.md 7. p09 is the complement -- there the bug went invisible even to
//! the spec, once the spec moved with it.
//!
//! **The proof is three lemmas and no nonlinear arithmetic.**
//!
//!   * `rev_range(s, lo, hi)` is a CLOSED FORM -- `Seq::new` with an index
//!     reflection -- and not a recursive definition. That is what makes the rest
//!     cheap: every step below is a pointwise argument that `=~=` discharges.
//!   * `lemma_rev_step` is the two-cursor loop's step: swapping `s[a]` with
//!     `s[b-1]` and moving both cursors inward leaves `rev_range` invariant. It
//!     is the relational invariant TASK_047 predicted would be the work, and it
//!     is nine lines.
//!   * `lemma_three_reverses` is the composition:
//!     `rev(rev(rev(s,0,r),r,m),0,m) == rot_left(s,m,r)` for `0 <= r <= m`. Also
//!     pointwise: for `i < m` the outer reverse reads index `m-1-i`, which lands
//!     in the second reverse's range iff `i + r < m`, and the two branches give
//!     `s[i+r]` and `s[i+r-m]`. **`rot_left` is stated WITHOUT a modulo** -- the
//!     branch on `i + r < m` is the modulo, unrolled -- which keeps the whole
//!     specification inside linear arithmetic.
//!
//! All three verified first try (`5 verified, 0 errors` on the standalone
//! scaffolding, ../NOTES.md 5).
//!
//!     requires  off + len <= buf@.len()
//!
//! ONE clause, as on p03, p11 and p12 and unlike p17. It is structural -- about
//! the shape of the buffer the driver built, not about its contents -- so it
//! holds on *every* input this benchmark runs, `adversarial-*` included, and the
//! gate checks it call by call. `nrec`, `nelem`, `r` -- all 2^32 values of each
//! -- and every byte of the window are attacker data and none of them is an
//! assumption.
//!
//! **The cursor guards are SUBTRACTION-FIRST and that is what keeps the clause
//! count at one.** `len - p < 8` needs `p <= len`, which the guards themselves
//! maintain; the additive `p + 8 > len` is a `usize` overflow Verus rejects, and
//! buying it back would cost either a second `requires` (p17's route) or a
//! second driver conjunct. p07's lesson, on a second pattern: the spelling that
//! makes the proof trivial is the one that makes the bug impossible. All seven
//! rungs use it, so no rung comparison moves on it. ../NOTES.md 5 prices the
//! alternative.
//!
//! Note what the spec does **not** assume: that `nrec` is honest, that `nelem`
//! fits the window, or that `r` is in range. `walk` is defined as the
//! *program's* walk, so `adversarial-inarray`, the three `adversarial-past*`
//! rows and `degenerate` are all inside the verified domain and the kernel
//! agrees with `model.py` on all five.
//!
//! TCB tally: NOTES.md 6. **Five** `external_body` items, three of them with a
//! `requires`, all listed there individually, because an under-counted TCB is
//! how the pilot's fatal defect hid in plain sight (`.memory/04-verus.md`). It
//! was SIX until TASK_048: `scr_load` is now verified rather than trusted, and
//! the axiom it used to state relocates into vstd -- see its comment below and
//! ../NOTES.md 6, which names the three vstd items that take it over.

use vstd::prelude::*;

// Plain-Rust I/O helpers. Outside `verus!`, so Verus treats the whole module as
// external (external-by-default). Reached only through `load_input`/`emit`.
#[path = "../../common/driver.rs"]
mod driver;

verus! {

// `group_slice_axioms` gives `slice@.len() == spec_slice_len(slice)`, hence
// `slice@.len() <= usize::MAX` -- without it `off + len` cannot be shown not to
// overflow `usize`. `group_array_axioms` gives `scr@.len() == SCR` for a
// `[u8; SCR]` and the fill axiom for `[0; SCR]`; p03 is the pattern that first
// needed it and p06 is the third. `lemma_u128_shr_is_div` turns `x >> 64` into
// `x / 2^64`, which is what the driver's multiply-shift barrier bound is about,
// and the mul group is what the driver's window-offset bound
// `k * stride + stride <= n_blob` needs; the KERNEL needs neither.
broadcast use {
    vstd::slice::group_slice_axioms,
    vstd::array::group_array_axioms,
    vstd::bits::lemma_u128_shr_is_div,
    vstd::arithmetic::mul::lemma_mul_inequality,
};

/// The scratch's extent, a compile-time constant in every rung.
///
/// A `const` inside `verus!` is its own obligation (`.memory/04-verus.md`,
/// measured on p08's `SCR` and again on p03's `STACK_CAP`), so this contributes
/// 1 to the count pinned in ../spec.md and the decomposition there says so.
pub const SCR: usize = 64;

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

/// How many records the window at `off` declares. **Declared, and it bounds
/// nothing** -- see `walk`.
pub open spec fn nrec_at(buf: Seq<u8>, off: int) -> int {
    u32_at(buf, off)
}

/// The scratch every rung starts from. Safe Rust has no uninitialised array, so
/// all four Rust rungs write `[0u8; SCR]` and both C rungs `memset` it. The
/// initial contents are in the specification rather than quantified away,
/// exactly as p03 and p12 do: **it is what makes REGIME 1 deterministic.** With
/// `m <= r <= SCR` the unreduced triple reads `scr[m .. r)`, which no record
/// wrote; zero-initialising it is what makes every rung -- and every
/// delete-the-check control -- print the *same* wrong answer.
pub open spec fn zero_scr() -> Seq<u8> {
    Seq::new(SCR as nat, |i: int| 0u8)
}

/// THE REVERSE: `s` with the half-open range `[lo, hi)` reflected.
///
/// Closed form, not a recursion. Everything else in this proof is a pointwise
/// argument over this definition, which is why there is no `by (nonlinear_arith)`
/// anywhere in the file.
pub open spec fn rev_range(s: Seq<u8>, lo: int, hi: int) -> Seq<u8> {
    Seq::new(s.len(), |i: int| if lo <= i < hi { s[lo + hi - 1 - i] } else { s[i] })
}

/// THE ROTATION: `s` with its prefix `[0, m)` rotated left by `r`, for
/// `0 <= r <= m`.
///
/// **Stated without a modulo.** `if i + r < m { s[i + r] } else { s[i + r - m] }`
/// *is* `s[(i + r) mod m]` on this domain, and writing it as a branch keeps the
/// specification inside linear arithmetic -- p07's zero-nonlinear-arithmetic
/// property, reached here by choosing the spelling rather than by luck.
pub open spec fn rot_left(s: Seq<u8>, m: int, r: int) -> Seq<u8> {
    Seq::new(
        s.len(),
        |i: int|
            if 0 <= i < m {
                if i + r < m {
                    s[i + r]
                } else {
                    s[i + r - m]
                }
            } else {
                s[i]
            },
    )
}

/// THE BULK LOAD: `scr` with its prefix `[0, m)` replaced by `buf[at .. at+m)`.
/// The trusted item `scr_load` is specified against exactly this.
pub open spec fn load_into(scr: Seq<u8>, buf: Seq<u8>, at: int, m: int) -> Seq<u8> {
    Seq::new(scr.len(), |i: int| if 0 <= i < m { buf[at + i] } else { scr[i] })
}

/// The Horner fold over the scratch's live prefix, `scr[i .. m)`.
///
/// **Order-sensitive, over the FULL live extent, and both are load-bearing.**
/// TASK_004_REVIEW's reason for the full-extent rule is elision -- a fold that
/// reads part of the result lets the optimiser delete the rest. p06 supplies a
/// second and independent one: three reverses compose to a PERMUTATION, so the
/// buggy and the correct scratch are the same MULTISET whenever `r < SCR`, and a
/// sum- or xor-fold could not tell them apart at all. ../NOTES.md 2.
pub open spec fn fold_scr(scr: Seq<u8>, i: int, m: int, acc: u64) -> u64
    decreases m - i,
{
    if i >= m {
        acc
    } else {
        fold_scr(scr, i + 1, m, acc.wrapping_mul(31).wrapping_add(scr[i] as u64))
    }
}

/// THE MACHINE. Records `rec .. nrec`, carrying the scratch contents, the
/// cursor and the accumulator.
///
/// **The walk stops when the window runs out, whatever `nrec` says** -- the two
/// `break`s are `len - p < 8` and `len - p < nelem`, and both are in the spec.
///
/// **The REDUCTION is here, and it is the line R1 omits.** `if m != 0 { r % m }
/// else { 0 }` -- the `m != 0` arm is not decoration, it is a division by zero
/// in the hardened C rung and `degenerate.bin` declares a record with
/// `nelem == 0`.
pub open spec fn walk(
    buf: Seq<u8>,
    off: int,
    len: int,
    rec: int,
    nrec: int,
    p: int,
    scr: Seq<u8>,
    acc: u64,
) -> u64
    decreases nrec - rec,
{
    if rec >= nrec {
        acc
    } else if len - p < 8 {
        acc
    } else {
        let nelem = u32_at(buf, off + p);
        let r0 = u32_at(buf, off + p + 4);
        let p2 = p + 8;
        let m = if nelem < SCR as int {
            nelem
        } else {
            SCR as int
        };
        if len - p2 < nelem {
            acc
        } else {
            let scr1 = load_into(scr, buf, off + p2, m);
            let rr = if m != 0 {
                r0 % m
            } else {
                0
            };
            let scr2 = rot_left(scr1, m, rr);
            let acc2 = fold_scr(scr2, 0, m, acc).wrapping_mul(31).wrapping_add(m as u64);
            walk(buf, off, len, rec + 1, nrec, p2 + nelem, scr2, acc2)
        }
    }
}

/// What the kernel returns.
///
/// The two early exits are the tests every rung keeps, R1 included: a window too
/// short to hold the header, and a zero count. **R1 keeps both.** What R1 omits
/// is the reduction inside `walk`, and that is the only thing it omits.
pub open spec fn rotate_fold(buf: Seq<u8>, off: int, len: int) -> u64 {
    if len < 4 {
        0
    } else if nrec_at(buf, off) == 0 {
        0
    } else {
        walk(buf, off, len, 0, nrec_at(buf, off), 4, zero_scr(), 0).wrapping_mul(
            31,
        ).wrapping_add(nrec_at(buf, off) as u64)
    }
}

// ----------------------------------------------------------------- proof ----
/// A reverse of an empty or inverted range is the identity. This is what the
/// three reverse loops' exit condition buys, and it is also why the second
/// reverse `[r, m)` is a no-op in R1 when `r > m`.
pub proof fn lemma_rev_noop(s: Seq<u8>, lo: int, hi: int)
    requires
        hi <= lo,
    ensures
        rev_range(s, lo, hi) == s,
{
    assert(rev_range(s, lo, hi) =~= s);
}

/// THE TWO-CURSOR STEP. Swap the ends of `[a, b)` and move both cursors inward:
/// the reverse of what is left is the reverse of what there was.
///
/// This is the relational invariant the three reverse loops carry, proved once
/// and used three times.
pub proof fn lemma_rev_step(s: Seq<u8>, a: int, b: int)
    requires
        0 <= a,
        a < b,
        b <= s.len(),
    ensures
        rev_range(s.update(a, s[b - 1]).update(b - 1, s[a]), a + 1, b - 1) == rev_range(
            s,
            a,
            b,
        ),
{
    let s2 = s.update(a, s[b - 1]).update(b - 1, s[a]);
    assert(rev_range(s2, a + 1, b - 1) =~= rev_range(s, a, b));
}

/// THE COMPOSITION, and the reason p06's postcondition is functional rather
/// than memory-safety-only: three reverses ARE a rotation.
///
/// For `i < m` the outer reverse reads `m-1-i`, which is inside the second
/// reverse's range `[r, m)` exactly when `i + r < m`; the two branches then read
/// `s[i+r]` and `s[i+r-m]`. Pointwise, no modulo, no nonlinear arithmetic.
pub proof fn lemma_three_reverses(s: Seq<u8>, m: int, r: int)
    requires
        0 <= r <= m <= s.len(),
    ensures
        rev_range(rev_range(rev_range(s, 0, r), r, m), 0, m) == rot_left(s, m, r),
{
    let a = rev_range(s, 0, r);
    let b = rev_range(a, r, m);
    let c = rev_range(b, 0, m);
    assert(c =~= rot_left(s, m, r));
}

// ------------------------------------------------------------------- TCB ----
// TRUSTED ITEM 1 of 5. vstd ships no specification for `<[T]>::get_unchecked`,
// so this is the axiom that licenses the unchecked read of the SOURCE window.
// It is sound because the standard library's documented contract for
// `get_unchecked` is exactly this: if the caller guarantees `i < v.len()`, the
// call is defined and yields `v[i]`. Identical, character for character, to the
// accessor p01, p02, p03, p05, p07, p11, p12, p13, p16 and p17 ship.
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

// TRUSTED ITEM 2 of 5. The SCRATCH read, performed by the reverses and by the
// fold. The scratch is a fixed-size `[u8; 64]`, so the bound is the array's
// type-level length rather than a runtime `len()`; p03's `stack_get_unchecked`
// and p12's `dst_get_unchecked` are the same item.
//
// The `requires` is ONE conjunct and NOT `i < v@.len(), v@.len() == 64`: for a
// `&[u8; 64]` the second is a TAUTOLOGY, discharged from the parameter type
// alone by vstd's `array_len_matches_n`, and p03's gate run caught exactly that
// draft (`.memory/04-verus.md`; p03 NOTES.md 5b).
#[inline(always)]
#[verifier::external_body]
fn scr_get_unchecked(v: &[u8; 64], i: usize) -> (r: u8)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    unsafe { *v.get_unchecked(i) }
}

// THE VERIFIED TWIN of trusted item 2.
#[cfg(slb_twin)]
fn slb_twin_scr_get_unchecked(v: &[u8; 64], i: usize) -> (r: u8)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    v[i]
}

// TRUSTED ITEM 3 of 5, and **the item p06 exists for**: the unchecked STORE into
// the fixed scratch. It is called TWICE per swap, at `a` and at `b - 1`, and the
// `requires` is what excludes both of R1's out-of-bounds stores.
//
// The `ensures` is a whole-sequence equality (`update`), not a statement about
// slot `i` alone, so it says both "slot `i` became `x`" and "nothing else
// moved" -- the shape `.memory/02-bench-rules.md` argues for. That matters more
// here than on p03 or p12: `lemma_rev_step` is stated as a composition of two
// `update`s, so an `ensures` that only pinned slot `i` would not compose at all.
//
// `x` is a pure VALUE parameter -- stored, never used as an address or a length
// -- so it has no precondition, and `../spec.md`'s `verus.unsafe_justifications`
// says so and the gate shouts it every run. `.memory/04-verus.md` names this
// false positive of the parameter-coverage rule; p03 was the first pattern to
// exercise it, p12 the second and p06 the third.
#[inline(always)]
#[verifier::external_body]
fn scr_set_unchecked(v: &mut [u8; 64], i: usize, x: u8)
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
fn slb_twin_scr_set_unchecked(v: &mut [u8; 64], i: usize, x: u8)
    requires
        i < old(v)@.len(),
    ensures
        final(v)@ == old(v)@.update(i as int, x),
{
    v[i] = x;
}

// THE BULK LOAD -- and it is NOT a trusted item. It was one until TASK_048,
// and the reason recorded for keeping it was FALSE.
//
// Until TASK_048 this item carried `#[verifier::external_body]` and this
// comment said that `<[T]>::split_at_mut` "is the route that would delete this
// item; taking it changes the exec text of four rungs". **Measured at
// TASK_047_REVIEW and re-measured at TASK_048: it changes the exec text of
// NOTHING.** With the body below, `verus.rs` verifies `18 verified, 0 errors`
// (twin `23 verified, 0 errors`) and the compiled kernel is BYTE-IDENTICAL to
// the trusted spelling and to R4 -- `md5_raw 6608a63b5c52`, `md5_fn
// 897c52ff4005`, 216/208 instructions, `identity: unsafe == verus, O3 exact`
// holding, checksums unchanged on every input. So this is a MEASUREMENT and
// not a re-ship: no rung's machine code moved and no published `Ir` moved
// (`.memory/02-bench-rules.md`'s "NEVER re-ship a rung" is about spellings that
// change a cost; nothing here changes one).
//
// Three vstd facts do the work, and NAMING them is the point -- the axiom
// RELOCATES into vstd, it does not vanish (../NOTES.md 6):
//
//   1. `vstd::array::ref_mut_array_unsizing_coercion` (`vstd/array.rs:175`),
//      which Verus inserts for the implicit `&mut [u8; 64]` -> `&mut [u8]`
//      reborrow on the line below, and whose `ensures` is exactly the write-back
//      this item used to axiomatise: `out.view() == old(r).view()` **and**
//      `final(out).view() == final(r).view()`. It is itself `external_body`
//      INSIDE vstd.
//   2. `<[T]>::split_at_mut` (`vstd/std_specs/slice.rs:185`), whose `ensures`
//      spells the halves' write-back out: `final(slice)@ == final(ret.0)@ +
//      final(ret.1)@`.
//   3. `<[T]>::copy_from_slice` (`vstd/std_specs/slice.rs:205`), which the
//      pinned vstd DOES specify, against what `.memory/04-verus.md:133` and
//      `:813` say.
//
// **Why the spelling had to change, measured rather than assumed.** The old
// body was `dst[..n].copy_from_slice(&src[from..from + n]);`. `..n` is a
// `RangeTo<usize>`, and at the pinned vstd `RangeTo` has **no**
// `SliceIndexSpecImpl` at all -- only `usize` and `Range<usize>` do
// (`vstd/std_specs/slice.rs:14,30`) -- so that line cannot verify: it reports
// `precondition not satisfied` at `vstd/std_specs/core.rs:69` (`index_req`).
// Respelling it `dst[0..n]` on the reborrowed slice discharges the
// preconditions and then fails the POSTcondition, because
// `<[T] as IndexMut<I>>::index_mut`'s `ensures` is a `call_ensures(...)` that Z3
// does not instantiate. `split_at_mut` is the only route that closes both ends.
// Probes: `.temp/p48/vstd/keepspell.rs`, `keepspell2.rs`.
//
// It is a free function rather than an expression inside `kernel` because R4
// has to be byte-identical to it: written inline, R4 is 179 instructions and R5
// 208, and the difference is entirely LLVM's inlining order.
//
// One `ensures`, and it is the whole array: `load_into` says the prefix
// `[0, n)` becomes `src[from .. from+n)` **and every byte from `n` up is the
// byte that was already there**. The second half is not decoration here -- the
// scratch is NOT re-zeroed between records, and regime 1 reads exactly those
// untouched bytes. It is now a PROVED postcondition rather than an axiom.
#[inline(always)]
fn scr_load(dst: &mut [u8; 64], src: &[u8], from: usize, n: usize)
    requires
        n <= old(dst)@.len(),
        from + n <= src@.len(),
    ensures
        final(dst)@ == load_into(old(dst)@, src@, from as int, n as int),
{
    assert(src@.len() == vstd::slice::spec_slice_len(src));
    let ghost d0 = dst@;
    let s: &mut [u8] = dst;
    let (a, _b) = s.split_at_mut(n);
    a.copy_from_slice(&src[from..from + n]);
    assert(dst@ =~= load_into(d0, src@, from as int, n as int));
}

// `scr_load` IS NO LONGER A TRUSTED ITEM (TASK_048), so `check.py`'s 5c-twin
// stage no longer requires this twin -- `_is_trusted` is keyed on
// `external_body` + (`ensures` or `unsafe`), and `scr_load` is now none of
// those. **It is kept anyway, deliberately**, and it is worth one sentence why:
// it is a SECOND and INDEPENDENT derivation of `load_into`, from an ELEMENT-WISE
// indexed loop rather than from vstd's three bulk specifications, so the two
// routes to the same postcondition are both in the tree and both checked. It
// still carries `2 verified` under `--cfg slb_twin` (the loop body is its own
// query), which is the +2 in the twin count pinned in ../spec.md.
#[cfg(slb_twin)]
fn slb_twin_scr_load(dst: &mut [u8; 64], src: &[u8], from: usize, n: usize)
    requires
        n <= old(dst)@.len(),
        from + n <= src@.len(),
    ensures
        final(dst)@ == load_into(old(dst)@, src@, from as int, n as int),
{
    assert(src@.len() == vstd::slice::spec_slice_len(src));
    let ghost d0 = dst@;
    let mut j: usize = 0;
    while j < n
        invariant
            j <= n,
            n <= dst@.len(),
            dst@.len() == d0.len(),
            from + n <= src@.len(),
            src@.len() <= usize::MAX,
            forall|q: int| 0 <= q < j ==> dst@[q] == src@[from + q],
            forall|q: int| j <= q < dst@.len() ==> dst@[q] == d0[q],
        decreases n - j,
    {
        dst[j] = src[from + j];
        j = j + 1;
    }
    assert(dst@ =~= load_into(d0, src@, from as int, n as int));
}

// TRUSTED ITEM 4 of 5. Argument parsing, file I/O and little-endian decoding,
// delegated to common/driver.rs so that all seven rungs read the file the same
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
        r == rotate_fold(buf@, off as int, len as int),
{
    // Ghost only: mentioning `spec_slice_len` fires vstd's `axiom_spec_len`,
    // which is what tells the SMT solver a slice length fits in a `usize` --
    // needed to rule out `off + len` overflowing. Erases at compile time.
    assert(buf@.len() == vstd::slice::spec_slice_len(buf));
    if len < 4 {
        return 0;
    }
    let nrec: usize = buf_get_unchecked(buf, off) as usize + 256 * (buf_get_unchecked(
        buf,
        off + 1,
    ) as usize) + 65536 * (buf_get_unchecked(buf, off + 2) as usize) + 16777216 * (
    buf_get_unchecked(buf, off + 3) as usize);
    if nrec == 0 {
        return 0;
    }
    let mut scr: [u8; SCR] = [0; SCR];
    // Ghost only: `[0; 64]`'s view IS the all-zeros sequence. vstd's
    // `axiom_spec_array_fill_for_copy_type` gives it pointwise; `=~=` lifts that
    // to sequence equality.
    assert(scr@ =~= zero_scr());
    let mut acc: u64 = 0;
    let mut p: usize = 4;
    let mut rec: usize = 0;
    // "The records from here, with the scratch we have built and where the
    // cursor is, are all the records." p12's relational shape, with the mutated
    // SEQUENCE in the carried state. This loop exits THREE ways (`rec == nrec`
    // and the two window-exhausted breaks), so it needs `invariant_except_break`
    // plus a loop `ensures`.
    while rec < nrec
        invariant_except_break
            rec <= nrec,
            0 < nrec,
            nrec == nrec_at(buf@, off as int),
            4 <= len,
            4 <= p <= len,
            scr@.len() == SCR,
            off + len <= buf@.len(),
            buf@.len() <= usize::MAX,
            walk(buf@, off as int, len as int, rec as int, nrec as int, p as int, scr@, acc)
                == walk(buf@, off as int, len as int, 0, nrec as int, 4, zero_scr(), 0),
        ensures
            walk(buf@, off as int, len as int, 0, nrec as int, 4, zero_scr(), 0) == acc,
        decreases nrec - rec,
    {
        let ghost p_before = p as int;
        let ghost rec_before = rec as int;
        let ghost acc_before = acc;
        let ghost scr_before = scr@;
        if len - p < 8 {
            break;
        }
        let nelem: usize = buf_get_unchecked(buf, off + p) as usize + 256 * (
        buf_get_unchecked(buf, off + p + 1) as usize) + 65536 * (buf_get_unchecked(
            buf,
            off + p + 2,
        ) as usize) + 16777216 * (buf_get_unchecked(buf, off + p + 3) as usize);
        let mut r: usize = buf_get_unchecked(buf, off + p + 4) as usize + 256 * (
        buf_get_unchecked(buf, off + p + 5) as usize) + 65536 * (buf_get_unchecked(
            buf,
            off + p + 6,
        ) as usize) + 16777216 * (buf_get_unchecked(buf, off + p + 7) as usize);
        p = p + 8;
        let m: usize = if nelem < SCR {
            nelem
        } else {
            SCR
        };
        if len - p < nelem {
            break;
        }
        scr_load(&mut scr, buf, off + p, m);
        let ghost scr_loaded = scr@;
        p = p + nelem;
        // THE SAFETY LINE. c/kernel.c omits exactly this. The `m != 0` arm is
        // not decoration: `r % 0` is a division by zero, and `degenerate.bin`
        // declares a record with `nelem == 0`.
        if m != 0 {
            r = r % m;
        } else {
            r = 0;
        }
        let mut a: usize = 0;
        let mut b: usize = r;
        let ghost s0 = scr@;
        // REVERSE 1 of 3, over `[0, r)`. The invariant is `lemma_rev_step`'s
        // conclusion carried across the loop: the reverse of what is left to do
        // equals the reverse of what there was. `a + b == a0 + b0` is what keeps
        // the two cursors symmetric and is the only arithmetic in it.
        while a < b
            invariant
                a + b == r,
                b <= r <= SCR,
                scr@.len() == SCR,
                rev_range(scr@, a as int, b as int) == rev_range(s0, 0, r as int),
            decreases b,
        {
            let t: u8 = scr_get_unchecked(&scr, a);
            let u: u8 = scr_get_unchecked(&scr, b - 1);
            proof {
                lemma_rev_step(scr@, a as int, b as int);
            }
            scr_set_unchecked(&mut scr, a, u);
            scr_set_unchecked(&mut scr, b - 1, t);
            a = a + 1;
            b = b - 1;
        }
        proof {
            lemma_rev_noop(scr@, a as int, b as int);
        }
        let ghost s1 = scr@;
        a = r;
        b = m;
        // REVERSE 2 of 3, over `[r, m)`. In this rung `r <= m` always, because
        // the reduction above put it there; in R1 it is `r > m` on every regime-1
        // input and the loop is a no-op, which is what makes the buggy triple
        // compose to `scr[i] = old[r - m + i]` instead of failing.
        while a < b
            invariant
                a + b == r + m,
                r <= a,
                b <= m <= SCR,
                scr@.len() == SCR,
                rev_range(scr@, a as int, b as int) == rev_range(s1, r as int, m as int),
            decreases b,
        {
            let t: u8 = scr_get_unchecked(&scr, a);
            let u: u8 = scr_get_unchecked(&scr, b - 1);
            proof {
                lemma_rev_step(scr@, a as int, b as int);
            }
            scr_set_unchecked(&mut scr, a, u);
            scr_set_unchecked(&mut scr, b - 1, t);
            a = a + 1;
            b = b - 1;
        }
        proof {
            lemma_rev_noop(scr@, a as int, b as int);
        }
        let ghost s2 = scr@;
        a = 0;
        b = m;
        // REVERSE 3 of 3, over `[0, m)`.
        while a < b
            invariant
                a + b == m,
                b <= m <= SCR,
                scr@.len() == SCR,
                rev_range(scr@, a as int, b as int) == rev_range(s2, 0, m as int),
            decreases b,
        {
            let t: u8 = scr_get_unchecked(&scr, a);
            let u: u8 = scr_get_unchecked(&scr, b - 1);
            proof {
                lemma_rev_step(scr@, a as int, b as int);
            }
            scr_set_unchecked(&mut scr, a, u);
            scr_set_unchecked(&mut scr, b - 1, t);
            a = a + 1;
            b = b - 1;
        }
        proof {
            lemma_rev_noop(scr@, a as int, b as int);
            lemma_three_reverses(scr_loaded, m as int, r as int);
        }
        let ghost acc_pre_fold = acc;
        let mut i: usize = 0;
        // "The fold from here is the whole fold." The scratch does not change in
        // this loop; what has to be carried is that `m` never left the array.
        while i < m
            invariant
                i <= m <= SCR,
                scr@.len() == SCR,
                fold_scr(scr@, i as int, m as int, acc) == fold_scr(
                    scr@,
                    0,
                    m as int,
                    acc_pre_fold,
                ),
            decreases m - i,
        {
            acc = acc.wrapping_mul(31).wrapping_add(scr_get_unchecked(&scr, i) as u64);
            i = i + 1;
        }
        acc = acc.wrapping_mul(31).wrapping_add(m as u64);
        // Ghost only: unfold `walk` once at the value it had on entry to this
        // iteration. Its `nelem`, `r0` and `m` ARE the exec values, its
        // `load_into` IS what `scr_load` did, its `rr` IS the reduction above and
        // its `rot_left` IS what the three reverses built -- by
        // `lemma_three_reverses`. So the state this iteration produced is the one
        // the spec produces.
        assert(walk(buf@, off as int, len as int, rec_before, nrec as int, p_before,
            scr_before, acc_before) == walk(buf@, off as int, len as int, rec_before + 1,
            nrec as int, p as int, scr@, acc));
        rec = rec + 1;
    }
    acc.wrapping_mul(31).wrapping_add(nrec as u64)
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
        // is the guard immediately above, and integer division only rounds down,
        // so `n_blob / stride >= 1` -- but that is a fact about division and Z3
        // needs the lemma named.
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
            assert(r == rotate_fold(buf@, (k * stride) as int, stride as int));
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    emit(acc);
}

} // verus!
