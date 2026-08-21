//! p08 rung R5 -- unsafe + Verus proof.
//!
//! R4's exec code verbatim, plus the specs and proofs that discharge its one
//! `unsafe` operation.
//!
//! **What is new here is not the arithmetic, it is the shape of the trusted
//! contract.** p01, p02, p16, p17 and p05 all wrap the same single-clause
//! `<[T]>::get_unchecked` -- `requires i < v@.len()`, `ensures r == v@[i]` --
//! and `.memory/04-verus.md` records that the verified-twin mechanism has
//! therefore *never been exercised on the case it was built for*: a
//! **multi-clause** trusted `ensures`, where the archetypal honest mistake is a
//! missing conjunct rather than a weakened one.
//!
//! `move_right` is that case. A move has three regions and the `ensures` needs
//! one conjunct for each:
//!
//!     [dr, m)     took the bytes from [0, m - dr)     <- what the move DID
//!     [0, dr)     unchanged                           <- what it did NOT touch
//!     [m, len)    unchanged                           <- ditto, above the window
//!
//! **Drop either of the last two and the proof stops going through**, because
//! the loop invariant `scr@ == shift_rounds(...)` is an equality on the *whole*
//! 4096-element sequence and the three conjuncts partition it. That is what
//! makes all three load-bearing under gate step 5c, and it is why the shape
//! matters -- a one-conjunct move contract saying only "the moved range is
//! right" would verify, would pass every mechanical check in the gate, and would
//! be an axiom that `ptr::copy` may scribble anywhere outside `[dr, m)`.
//!
//! **Three, not four: the length conjunct a move contract usually carries is
//! measurably NOT load-bearing here, and the gate said so.** With
//! `final(v)@.len() == old(v)@.len()` present, step 5c reports
//! *"ensures[0] is NOT load-bearing: deleting it still gives 11 verified, 0
//! errors"* -- because the only caller passes `&mut scr` where `scr` is a
//! `[u8; SCR]`, and Verus's array-to-slice coercion carries `final(out)@ ===
//! final(r)@` with the array's length fixed by its type. The length is known at
//! the call site whatever the contract says, so stating it would be an axiom
//! about real Rust semantics carried for free -- exactly what
//! `.memory/04-verus.md` says a trusted `ensures` must not be. The commissioning
//! sketch asked for four clauses; three is the measured number. NOTES.md 6a.
//! Read NOTES.md 8 (b) beside it: three clauses partition `old(v)@.len()`, not
//! `final(v)@.len()`, so the contract is complete *relative to this pattern's
//! one call site* and not as a contract on a general `&mut [u8]`.
//!
//! **The parameter is `&mut [u8]` and not `&mut [u8; SCR]`, and that was forced
//! by the gate rather than chosen.** With the array type, vstd's
//! `array_len_matches_n` gives `v@.len() == SCR` from the type alone, so there
//! is no non-tautological precondition to state about `v` at all -- and
//! `check.py` stage 5a's parameter-coverage rule (*every parameter a trusted
//! body uses must appear in its `requires`*) fails outright:
//! *"demands ... which constrains nothing about ['v']"*. The slice type makes
//! `m <= old(v)@.len()` a real constraint. **It is a workaround, not a fix: the
//! array type carries the length and the slice type does not, so the widened
//! contract is the weaker one** (TASK_014_REVIEW, measured -- NOTES.md 6a and
//! 8 (b)). NOTES.md 6a records this as the first false positive of that
//! rule found in the tree; `.memory/04-verus.md` predicted a different one (a
//! pure value parameter) and said nothing exercised it yet.
//!
//! The `requires` is
//!
//!     0 < dr <= m,  m <= old(v)@.len()
//!
//! and it is the whole safety contract of `core::ptr::copy(p, p.add(dr), m-dr)`:
//! `p.add(dr)` must stay inside the object, and both the `m - dr` source bytes
//! and the `m - dr` destination bytes must too.
//! `0 < dr` is not needed for memory safety -- it comes from the kernel's own
//! `d == 0` rejection and it is what lets the third conjunct's range `[0, dr)`
//! be non-degenerate. **`ptr::copy` is `memmove`, so no non-overlap
//! precondition exists to state**; swap it for `copy_nonoverlapping` and one
//! appears, unstatable from anything the kernel knows, which is exactly the C
//! bug re-opened. `controls/gen_controls.py` builds that mutant.
//!
//! The kernel's `requires` is
//!
//!     off + len <= buf@.len()
//!
//! and that is all of it -- structural, about the shape of the buffer the
//! driver built and not about its contents, so it holds on *every* input this
//! benchmark runs, `adversarial-*` included, and the gate checks it call by
//! call. `d` and `nrep_w`, all 2^32 pairs, are arguments of the problem.
//!
//! TCB tally: NOTES.md 8. **Three** `external_body` items, all listed there
//! individually, because an under-counted TCB is how the pilot's fatal defect
//! hid in plain sight (`.memory/04-verus.md`). It was **four** until TASK_056,
//! when `copy_in` was de-trusted -- the recorded reason for trusting it was
//! false and the price of the respelling that made it verifiable is published
//! in NOTES.md 6d, both halves.

use vstd::prelude::*;

// Plain-Rust I/O helpers. Outside `verus!`, so Verus treats the whole module as
// external (external-by-default). Reached only through `load_input`/`emit`.
#[path = "../../common/driver.rs"]
mod driver;

verus! {

// `group_slice_axioms` gives `slice@.len() == spec_slice_len(slice)`, hence
// `slice@.len() <= usize::MAX` -- without it `off + len` cannot be shown not to
// overflow `usize`. `group_array_axioms` is p08's addition to the template and
// carries the whole scratch: `array_len_matches_n` (so `scr@.len() == SCR` from
// the type), `lemma_array_index`, `axiom_spec_array_update` (so `scr[j] = b` has
// a meaning) and `axiom_spec_array_fill_for_copy_type` (so `[0u8; SCR]` is known
// to be all zeros). `lemma_u128_shr_is_div` turns `x >> 64` into `x / 2^64`,
// which is what the driver's multiply-shift barrier bound is about; the mul
// group is what the window-offset bound `k * stride + stride <= n_blob` needs.
broadcast use {
    vstd::slice::group_slice_axioms,
    vstd::array::group_array_axioms,
    vstd::bits::lemma_u128_shr_is_div,
    vstd::arithmetic::mul::lemma_mul_inequality,
};

/// The scratch capacity. A compile-time constant, like p02's destination
/// buffer -- but `m = min(avail, SCR)` and `avail` comes from the file, so the
/// measured length is attacker data and nothing is constant-folded.
pub const SCR: usize = 4096;

// ------------------------------------------------------------------ spec ----
/// The shift distance the window at `off` declares: a little-endian u16 at
/// window bytes 0..2. **This is the attacker's number and the whole pattern is
/// what the kernel does with it**: `d` decides whether the move's source and
/// destination ranges overlap, and therefore whether R1's `memcpy` is defined.
pub open spec fn d_at(buf: Seq<u8>, off: int) -> int {
    buf[off] as int + 256 * (buf[off + 1] as int)
}

/// How many framing layers the window at `off` declares: a little-endian u16 at
/// window bytes 2..4. Only the low two bits are used -- `1 + (x % 4)` is a mask
/// and not a check, so every value is legal and there is no rejection path.
pub open spec fn nrepw_at(buf: Seq<u8>, off: int) -> int {
    buf[off + 2] as int + 256 * (buf[off + 3] as int)
}

/// The scratch as the kernel builds it: `SCR` bytes, the window's first `m`
/// data bytes copied in and the rest zero.
///
/// The zeros are part of the specification, not an implementation detail. Every
/// rung zero-initialises (safe Rust cannot do otherwise, and C is made to match
/// so that the memset is a uniform per-call constant), and the moves below can
/// only ever read indices below `m`, so the tail's value never reaches the
/// result -- but it is *stated*, so that `shift_round`'s third conjunct has
/// something to preserve and the whole-sequence invariant is an equality rather
/// than a partial one.
pub open spec fn init_scr(buf: Seq<u8>, off: int, m: int) -> Seq<u8> {
    Seq::new(SCR as nat, |j: int| if j < m { buf[off + 4 + j] } else { 0u8 })
}

/// ONE move: `s[dr..m] <- s[0..m-dr]`, as a whole-sequence rebuild.
///
/// Read the three cases and compare them with `move_right`'s three `ensures`
/// conjuncts -- they are the same three regions, which is the point of writing
/// the spec this way rather than as a `subrange` concatenation. `[0, dr)` and
/// `[m, s.len())` keep `s[j]`; `[dr, m)` takes `s[j - dr]`.
///
/// **This is `memmove` semantics and not `memcpy` semantics**, and the two
/// differ exactly when `dr < m - dr`. Nothing in this file can express the
/// `memcpy` version: a spec function is a mathematical function of the whole
/// input sequence, so "read a byte you already overwrote" has no spelling here.
/// That is a real property of the specification language and it is worth
/// stating -- the C bug is not merely unproved in R5, it is *inexpressible* in
/// the logic the proof is written in, in the same way it is inexpressible in
/// safe Rust's type system.
pub open spec fn shift_round(s: Seq<u8>, dr: int, m: int) -> Seq<u8> {
    Seq::new(s.len(), |j: int| if dr <= j < m { s[j - dr] } else { s[j] })
}

/// `r` rounds, round `q` shifting by `d + q`.
///
/// `dr = d + r` rather than a fixed `d` is load-bearing (../spec.md): with a
/// fixed `d >= m/2` every round after the first would rewrite the same bytes
/// with the same values, so the result would stop depending on `nrep` and a
/// rung that skipped rounds would still produce the right checksum.
pub open spec fn shift_rounds(s: Seq<u8>, d: int, m: int, r: int) -> Seq<u8>
    decreases r,
{
    if r <= 0 {
        s
    } else {
        shift_round(shift_rounds(s, d, m, r - 1), d + r - 1, m)
    }
}

/// The u64 Horner fold over `s[0..j]`. Serial, so it has no vector form -- see
/// `model.py`'s `work_per_call` for why that matters to the `Ir` floor.
pub open spec fn fold_scr(s: Seq<u8>, j: int) -> u64
    decreases j,
{
    if j <= 0 {
        0
    } else {
        fold_scr(s, j - 1).wrapping_mul(31).wrapping_add(s[j - 1] as u64)
    }
}

/// What the kernel returns.
///
/// The three early exits are the bounds guard **every rung carries, R1
/// included** -- p08 is not a bounds pattern, and `c/kernel.c` omits nothing
/// from this. `m` is mixed into the checksum so that a rung which moved a
/// different number of bytes cannot produce the same answer even if the bytes
/// happened to fold the same way.
pub open spec fn shift_fold(buf: Seq<u8>, off: int, len: int) -> u64 {
    if len < 4 {
        0
    } else {
        let d = d_at(buf, off);
        let avail = len - 4;
        let m = if avail < SCR { avail } else { SCR as int };
        let nrep = 1 + nrepw_at(buf, off) % 4;
        if m < 2 || d == 0 || d + nrep > m {
            0
        } else {
            fold_scr(shift_rounds(init_scr(buf, off, m), d, m, nrep), m).wrapping_mul(
                31,
            ).wrapping_add(m as u64)
        }
    }
}

// ------------------------------------------------------------------- TCB ----
// TRUSTED ITEM 1 of 4, and **the pattern itself**. `core::ptr::copy` is
// `memmove`: it is defined for overlapping ranges, which is exactly what the C
// rung gets wrong. vstd ships no specification for it, so this is the axiom
// that licenses the raw pointer arithmetic.
//
// It is sound because the standard library's documented contract for
// `ptr::copy(src, dst, count)` is: both `src` and `dst` must be valid for
// `count` reads/writes, and the regions **may** overlap, in which case the
// destination gets the values the source held *before* the copy. With
// `p = v.as_mut_ptr()`, `0 < dr <= m <= v@.len()` and `count = m - dr`, the
// source `[p, p+m-dr)` and the destination `[p+dr, p+m)` are both inside the
// slice, and the three conjuncts below are that documented before-state
// semantics written out region by region.
//
// See NOTES.md's SLB-TRUSTED-ARGUMENT block for (a)(b)(c), and note in
// particular that this is the project's **first multi-clause trusted
// `ensures`** -- the case `.memory/04-verus.md` says the verified twin was
// built for and has never met.
#[inline(always)]
#[verifier::external_body]
fn move_right(v: &mut [u8], dr: usize, m: usize)
    requires
        0 < dr <= m,
        m <= old(v)@.len(),
    ensures
        forall|j: int| dr <= j < m ==> final(v)@[j] == old(v)@[j - dr],
        forall|j: int| 0 <= j < dr ==> final(v)@[j] == old(v)@[j],
        forall|j: int| m <= j < old(v)@.len() ==> final(v)@[j] == old(v)@[j],
{
    unsafe {
        let p = v.as_mut_ptr();
        core::ptr::copy(p, p.add(dr), m - dr);
    }
}

// THE VERIFIED TWIN of trusted item 1 (`harness/check.py` step 5c-twin).
//
// Same signature and same contract, character for character -- the gate lifts
// both from `move_right` above and refuses a twin whose signature differs --
// but implemented in *checked* code.
//
// **This is the first twin on this project that is not a one-liner, and the
// first that has anything to prove.** p01/p02/p16/p17/p05 all twin
// `get_unchecked` with `{ v[i] }`. The checked stand-in for a move is the
// reverse indexed loop, and getting it right *is* the exercise: the loop must
// run high-to-low, because the ranges overlap when `2*dr < m` and a forward
// loop would read a byte it had already written. The invariant says so
// directly -- indices `[j, m)` are already moved, indices `[0, j)` are still
// original -- and the read `v[j - dr]` is licensed by the second conjunct of
// that invariant, i.e. by the fact that the loop has not reached it yet.
//
// A `requires` too weak to license `ptr::copy` is too weak to license this, and
// Verus can see the second one: weaken `0 < dr <= m` to `0 < dr <= m + 1` and
// the write `v[j]` fails with `precondition not met`; delete `m <= old(v)@.len()`
// and it fails the same way.
//
// `#[cfg(slb_twin)]` is a cfg no measured build ever sets, so rustc strips this
// before codegen: the twin costs zero instructions structurally.
#[cfg(slb_twin)]
fn slb_twin_move_right(v: &mut [u8], dr: usize, m: usize)
    requires
        0 < dr <= m,
        m <= old(v)@.len(),
    ensures
        forall|j: int| dr <= j < m ==> final(v)@[j] == old(v)@[j - dr],
        forall|j: int| 0 <= j < dr ==> final(v)@[j] == old(v)@[j],
        forall|j: int| m <= j < old(v)@.len() ==> final(v)@[j] == old(v)@[j],
{
    let mut j: usize = m;
    while j > dr
        invariant
            dr <= j <= m,
            m <= v@.len(),
            v@.len() == old(v)@.len(),
            forall|q: int| j <= q < m ==> v@[q] == old(v)@[q - dr],
            forall|q: int| 0 <= q < j ==> v@[q] == old(v)@[q],
            forall|q: int| m <= q < v@.len() ==> v@[q] == old(v)@[q],
        decreases j - dr,
    {
        j = j - 1;
        v[j] = v[j - dr];
    }
}

// `copy_in` IS NO LONGER A TRUSTED ITEM (TASK_056). It was trusted item 2 of 4
// until this task, and the reason recorded for it was FALSE: it said *"vstd
// ships no specification for `copy_from_slice`"*, and the pinned vstd specifies
// it at `std_specs/slice.rs:205` and has done since before p08 was built. The
// same false sentence was corrected in `.memory/04-verus.md` and on p06 at
// TASK_048 and stood here in four places until now.
//
// **The real gap was the INDEX TYPE, not the copy.** `RangeTo<usize>` has no
// `SliceIndexSpecImpl<[T]>` at the pinned vstd (only `usize` at
// `std_specs/slice.rs:14` and `Range<usize>` at `:31`), so `dst[..n]` -- what
// every rung used to spell -- is unverifiable as written; and `dst[0..n]`, which
// *is* specified, gets past the precondition and then fails its postcondition,
// because `index_mut`'s `call_ensures` is never instantiated so the write-back
// is not available. `split_at_mut` (`std_specs/slice.rs:185`) is the route, and
// with it the contract below discharges with no trusted wrapper at all.
//
// **THE TRUST DOES NOT DISAPPEAR, IT RELOCATES INTO VSTD** -- two
// `assume_specification`s, for `<[T]>::split_at_mut` and `<[T]>::copy_from_slice`.
// What changes is *whose* axiom it is: an author-written `ensures` invented in
// this pattern and read by nobody else (a **V-gap** item, `.memory/04-verus.md`)
// becomes a vstd specification every Verus user shares and reviews. p08's TCB
// goes **4 items / 10 lines -> 3 items / 9 lines**, and the three left are
// **1 U-license (`move_right`) + 0 V-gap + 2 infra (`load_input`, `emit`)**.
// The `&mut [u8; 4096] -> &mut [u8]` coercion is NOT new exposure: it happens at
// the call site inside the verified `kernel` and the shipped 11/0 already relied
// on it (this is where p08 is cheaper than p06, whose `scr_load` took
// `&mut [u8; 64]` and newly relied on `vstd/array.rs:175`).
//
// **THE DIRECTION TEST, in writing** (`.memory/01-ladder.md`). Removing a
// trusted item makes the trusted base smaller, which is the direction that
// flatters this project's thesis, so the justification has to be the
// measurement and not the argument. It is: `-O3` is **byte-identical**
// (`md5_raw 44b63d20ccf1`, 168/166, 5 pads, **+0.00 `Ir`/call**), and `-O0`
// costs **+2 static instructions, +2.00 `Ir`/call exclusive of `kernel` and
// +27.00 `Ir`/call whole-program** -- the gate records the last of the three --
// on `unsafe.rs` and this file and on nothing else. `idiom.required` pins no copy spelling on p08
// (its six entries pin the memmove, the guard, `dr = d + r`, `%` vs `&` and the
// scratch), so no declaration moved with the measurement. ../NOTES.md 6d.
#[inline(always)]
fn copy_in(dst: &mut [u8], src: &[u8], from: usize, n: usize)
    requires
        from + n <= src@.len(),
        n <= old(dst)@.len(),
    ensures
        final(dst)@ =~= src@.subrange(from as int, from + n as int) + old(dst)@.subrange(
            n as int,
            old(dst)@.len() as int,
        ),
{
    // Without this the `from + n` in the index expression below reports
    // "possible arithmetic underflow/overflow": nothing else ties `src@.len()`
    // to a `usize`.
    assert(src@.len() == vstd::slice::spec_slice_len(src));
    let (a, _b) = dst.split_at_mut(n);
    a.copy_from_slice(&src[from..from + n]);
}

// `copy_in` is no longer trusted, so `check.py`'s 5c-twin stage no longer
// REQUIRES this twin -- `_is_trusted` is keyed on `external_body` + (`ensures`
// or `unsafe`) and `copy_in` is now none of those. **It is kept anyway,
// deliberately, and p06 kept its orphaned `slb_twin_scr_load` for the same
// reason**: it is a second and independent derivation of the same
// postcondition, from an element-wise indexed loop rather than from vstd's bulk
// specifications, so both routes are in the tree and both are checked. It still
// contributes `2 verified` under `--cfg slb_twin` (the loop body is its own
// query), which is part of the twin count pinned in ../spec.md.
#[cfg(slb_twin)]
fn slb_twin_copy_in(dst: &mut [u8], src: &[u8], from: usize, n: usize)
    requires
        from + n <= src@.len(),
        n <= old(dst)@.len(),
    ensures
        final(dst)@ =~= src@.subrange(from as int, from + n as int) + old(dst)@.subrange(
            n as int,
            old(dst)@.len() as int,
        ),
{
    assert(src@.len() == vstd::slice::spec_slice_len(src));
    let mut j: usize = 0;
    while j < n
        invariant
            j <= n,
            n <= dst@.len(),
            dst@.len() == old(dst)@.len(),
            from + n <= src@.len(),
            src@.len() <= usize::MAX,
            forall|q: int| 0 <= q < j ==> dst@[q] == src@[from + q],
            forall|q: int| j <= q < dst@.len() ==> dst@[q] == old(dst)@[q],
        decreases n - j,
    {
        dst[j] = src[from + j];
        j = j + 1;
    }
}

// TRUSTED ITEM 3 of 4. Argument parsing, file I/O and little-endian decoding,
// delegated to common/driver.rs so that all six rungs read the file the same
// way. It states **no** `ensures` at all, deliberately: an `ensures` here would
// be an axiom about the contents of a file, which nothing can justify. Every
// fact the proof needs is re-derived at run time from `bytes.len()` inside
// verified code. It contains no `unsafe` and no `ensures`, so it stays outside
// the twin regime.
#[verifier::external_body]
fn load_input() -> (r: (u64, u64, Vec<u8>)) {
    let path = driver::arg_path();
    let inp = driver::load(&path);
    let (stride_w, bytes) = driver::head1_u64_bytes(&inp);
    (inp.n_iters, stride_w, bytes)
}

// TRUSTED ITEM 4 of 4. `println!` is not verifiable; no `ensures`. Counted with
// the three above -- every `external_body` item is TCB, not just the
// interesting one (`.memory/04-verus.md`: the pilot was published as "one
// 3-line wrapper" and the true tally was three items, one of which was `main`).
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
        r == shift_fold(buf@, off as int, len as int),
{
    // Ghost only: mentioning `spec_slice_len` fires vstd's `axiom_spec_len`,
    // which is what tells the SMT solver a slice length fits in a `usize` --
    // needed to rule out `off + len` overflowing. Erases at compile time.
    assert(buf@.len() == vstd::slice::spec_slice_len(buf));
    if len < 4 {
        return 0;
    }
    let d: usize = buf[off] as usize + 256 * (buf[off + 1] as usize);
    let nrep_w: usize = buf[off + 2] as usize + 256 * (buf[off + 3] as usize);
    let avail: usize = len - 4;
    let m: usize = if avail < SCR { avail } else { SCR };
    let nrep: usize = 1 + nrep_w % 4;
    if m < 2 || d == 0 || d + nrep > m {
        return 0;
    }
    let mut scr: [u8; SCR] = [0u8; SCR];
    copy_in(&mut scr, buf, off + 4, m);
    // Ghost only: name the state the rounds start from, so the loop invariant
    // can say "what we have is the first `r` rounds of it". `init_scr`'s two
    // cases -- the copied prefix and the zero tail -- are exactly `copy_in`'s
    // one `ensures` clause read region by region.
    let ghost init: Seq<u8> = scr@;
    assert(init =~= init_scr(buf@, off as int, m as int));
    for r in 0..nrep
        invariant
            0 < d,
            d + nrep <= m,
            2 <= m <= SCR,
            init =~= init_scr(buf@, off as int, m as int),
            scr@ == shift_rounds(init, d as int, m as int, r as int),
    {
        let dr: usize = d + r;
        // Ghost only: hold the pre-move state so the trusted `ensures` can be
        // turned into one `shift_round` step. `=~=` is what does the work: the
        // three conjuncts cover `[0, dr)`, `[dr, m)` and `[m, scr.len())`, which
        // partition the whole array, so extensional equality closes it. Delete
        // any one conjunct and this assert fails -- which is what makes all
        // three load-bearing under gate step 5c.
        let ghost s0: Seq<u8> = scr@;
        move_right(&mut scr, dr, m);
        assert(scr@ =~= shift_round(s0, dr as int, m as int));
    }
    let mut acc: u64 = 0;
    for j in 0..m
        invariant
            m <= SCR,
            acc == fold_scr(scr@, j as int),
    {
        acc = acc.wrapping_mul(31).wrapping_add(scr[j] as u64);
    }
    acc.wrapping_mul(31).wrapping_add(m as u64)
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
            assert(r == shift_fold(buf@, (k * stride) as int, stride as int));
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    emit(acc);
}

} // verus!
