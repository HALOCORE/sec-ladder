//! p23 rung R5 -- unsafe + Verus proof.
//!
//! R4's exec code verbatim, plus the specs and proofs that discharge every
//! unchecked read AND every unchecked WRITE in it.
//!
//! **The obligation is a PARTITION, and the postcondition is the FUNCTIONAL
//! one.** The kernel's `ensures` says the scratch ends up exactly where Hoare's
//! scheme puts it and the returned index is exactly the meeting point -- not
//! merely that nothing was accessed out of bounds.
//!
//! **The specification and the code are DIFFERENT ALGORITHMS.** `part` below is
//! the SINGLE-LOOP three-way step -- advance `i`, or retreat `j`, or swap --
//! and the kernel is the NESTED-SCAN form, two inner scan loops inside an outer
//! loop. Each inner scan step is one of `part`'s first two cases and the swap is
//! its third, so the two agree on every input while being different programs;
//! that is the same "independent implementation" property `model.py` is held to.
//! ⚠ It is also the answer to `TASK_086`'s named kill risk for this row --
//! *"p23's verified spelling is not the spelling its cost kernels implement"*.
//! Both spellings verify: the single-loop form at `.temp/t86/v23_partition.rs`
//! (`4 verified, 0 errors`) and the nested-scan form at
//! `.temp/t101/pA_hoare_nested.rs` (`6 verified, 0 errors`), both first attempt.
//!
//! **The proof is ZERO lemmas.** `part` is a recursion whose three cases are
//! literally the three things the loop nest can do, so every loop invariant is
//! the same sentence -- *"the partition from here is the whole partition"* --
//! and Z3 discharges each step by unfolding `part` once. p06 needed three
//! lemmas for its rotation because three reverses are not syntactically a
//! rotation; here the spec is written in the shape the code moves in.
//!
//! **`decreases j - i` is the measure at all three loops**, and the third case
//! of `part` is where it is interesting: `part(swap2(s,i,j-1), pv, i+1, j-1)`
//! shrinks the measure by TWO, which is only non-negative because that case is
//! unreachable at `j == i + 1` -- there `s[j-1]` and `s[i]` are the same slot
//! and the case's guards say it is both `> pv` and `< pv`. Z3 gets that from
//! congruence; nothing is asserted by hand.
//!
//!     requires  off + len <= buf@.len()
//!
//! ONE clause, as on p03, p06, p11 and p12 and unlike p17. It is structural --
//! about the shape of the buffer the driver built, not about its contents -- so
//! it holds on *every* input this benchmark runs, `adversarial-*` included, and
//! the gate checks it call by call. `nrec`, `nelem`, `pv` -- all values of each
//! -- and every byte of the window are attacker data and none of them is an
//! assumption. **In particular the proof assumes NOTHING about the pivot**, and
//! that is the point of the row: `pv == 0` and `pv == 255` are exactly the two
//! values on which R1 leaves the scratch, and both are inside R5's verified
//! domain.
//!
//! **The cursor guards are SUBTRACTION-FIRST and that is what keeps the clause
//! count at one.** `len - p < 8` needs `p <= len`, which the guards themselves
//! maintain; the additive `p + 8 > len` is a `usize` overflow Verus rejects, and
//! buying it back would cost either a second `requires` (p17's route) or a
//! second driver conjunct. All seven rungs use it, so no rung comparison moves
//! on it.
//!
//! TCB tally: NOTES.md 6. **Five** `external_body` items, three of them with a
//! `requires`, all listed there individually, because an under-counted TCB is
//! how the pilot's fatal defect hid in plain sight (`.memory/04-verus.md`).
//! `scr_load` is VERIFIED, not trusted -- p06's TASK_048 route, reused here.

use vstd::prelude::*;

// Plain-Rust I/O helpers. Outside `verus!`, so Verus treats the whole module as
// external (external-by-default). Reached only through `load_input`/`emit`.
#[path = "../../common/driver.rs"]
mod driver;

verus! {

// `group_slice_axioms` gives `slice@.len() == spec_slice_len(slice)`, hence
// `slice@.len() <= usize::MAX` -- without it `off + len` cannot be shown not to
// overflow `usize`. `group_array_axioms` gives `scr@.len() == SCR` for a
// `[u8; SCR]` and the fill axiom for `[0; SCR]`. `lemma_u128_shr_is_div` turns
// `x >> 64` into `x / 2^64`, which is what the driver's multiply-shift barrier
// bound is about, and the mul group is what the driver's window-offset bound
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
/// exactly as p03, p06 and p12 do: **the scratch is not re-zeroed between
/// records**, so a record with `nelem < SCR` leaves the previous record's bytes
/// in `scr[m .. SCR)` -- which is exactly the region R1's unguarded upward scan
/// walks through before it leaves the array at all.
pub open spec fn zero_scr() -> Seq<u8> {
    Seq::new(SCR as nat, |i: int| 0u8)
}

/// THE BULK LOAD: `scr` with its prefix `[0, m)` replaced by `buf[at .. at+m)`.
/// `scr_load` is verified against exactly this.
pub open spec fn load_into(scr: Seq<u8>, buf: Seq<u8>, at: int, m: int) -> Seq<u8> {
    Seq::new(scr.len(), |i: int| if 0 <= i < m { buf[at + i] } else { scr[i] })
}

/// Exchange two slots. One `update` composed with another, so it composes with
/// a positional argument the way `part`'s third case needs.
pub open spec fn swap2(s: Seq<u8>, a: int, b: int) -> Seq<u8> {
    s.update(a, s[b]).update(b, s[a])
}

/// THE PARTITION: Hoare's scheme as a SINGLE-LOOP three-way step, returning the
/// final sequence and the meeting point.
///
///   * `s[i] <= pv`      -- the upward scan's step;
///   * `s[j-1] >= pv`    -- the downward scan's step;
///   * otherwise         -- the exchange, and both cursors move.
///
/// The kernel writes the same three things as two inner scan loops plus a swap.
/// **`<=` and `>=`, not `<` and `>`**: with these a run of elements equal to the
/// pivot is consumed by whichever case reaches it first, so the cursors meet
/// instead of crossing and `i <= j` is an invariant rather than a hope.
///
/// **`decreases j - i` and the third case shrinks it by two.** That is only
/// non-negative because the case cannot fire at `j == i + 1`: `s[j - 1]` is then
/// `s[i]`, and the case's own guards say it is both greater and less than `pv`.
pub open spec fn part(s: Seq<u8>, pv: u8, i: int, j: int) -> (Seq<u8>, int)
    decreases j - i,
{
    if i >= j {
        (s, i)
    } else if s[i] <= pv {
        part(s, pv, i + 1, j)
    } else if s[j - 1] >= pv {
        part(s, pv, i, j - 1)
    } else {
        part(swap2(s, i, j - 1), pv, i + 1, j - 1)
    }
}

/// The Horner fold over the scratch's live prefix, `scr[i .. m)`.
///
/// **Order-sensitive, over the FULL live extent, and both are load-bearing.**
/// TASK_004_REVIEW's reason for the full-extent rule is elision -- a fold that
/// reads part of the result lets the optimiser delete the rest. p06 supplied a
/// second one and p23 inherits it in a sharper form: a partition is a
/// PERMUTATION of the loaded prefix, so the partitioned and the unpartitioned
/// scratch are the same MULTISET on every input, and a sum- or xor-fold could
/// not tell them apart AT ALL -- not merely on some regime. ../NOTES.md 2.
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
/// **The PARTITION POINT is folded, not just the bytes.** `acc*31 + idx` is
/// what makes the returned index observable at all; without it a rung could
/// return any index and no checksum would move.
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
        let pv = buf[off + p + 4];
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
            let r = part(scr1, pv, 0, m);
            let acc2 = fold_scr(r.0, 0, m, acc).wrapping_mul(31).wrapping_add(r.1 as u64);
            walk(buf, off, len, rec + 1, nrec, p2 + nelem, r.0, acc2)
        }
    }
}

/// What the kernel returns.
///
/// The two early exits are the tests every rung keeps, R1 included: a window too
/// short to hold the header, and a zero count. **R1 keeps both.** What R1 omits
/// is the `i < j` conjunct on each of the two scans inside `part`'s domain, and
/// that is the only thing it omits.
pub open spec fn partition_fold(buf: Seq<u8>, off: int, len: int) -> u64 {
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

// ------------------------------------------------------------------- TCB ----
// TRUSTED ITEM 1 of 5. vstd ships no specification for `<[T]>::get_unchecked`
// (`grep -rn get_unchecked ~/tools/verus/vstd/` -> 0 hits, re-run at TASK_101),
// so this is the axiom that licenses the unchecked read of the SOURCE window.
// It is sound because the standard library's documented contract for
// `get_unchecked` is exactly this: if the caller guarantees `i < v.len()`, the
// call is defined and yields `v[i]`. Identical, character for character, to the
// accessor p01, p02, p03, p05, p06, p07, p11, p12, p13, p16 and p17 ship.
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

// TRUSTED ITEM 2 of 5. The SCRATCH read, performed by both scans, by the swap
// and by the fold. The scratch is a fixed-size `[u8; 64]`, so the bound is the
// array's type-level length rather than a runtime `len()`; p03's
// `stack_get_unchecked`, p06's `scr_get_unchecked` and p12's `dst_get_unchecked`
// are the same item.
//
// The `requires` is ONE conjunct and NOT `i < v@.len(), v@.len() == 64`: for a
// `&[u8; 64]` the second is a TAUTOLOGY, discharged from the parameter type
// alone by vstd's `array_len_matches_n`, and p03's gate run caught exactly that
// draft (`.memory/04-verus.md`).
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

// TRUSTED ITEM 3 of 5, and **the item that carries p23's write half**: the
// unchecked STORE into the fixed scratch. It is called TWICE per exchange, at
// `i` and at `j - 1`, and the `requires` is what excludes R1's out-of-bounds
// store -- the one R1 reaches after its downward scan has WRAPPED `j`, which is
// why the read guard R1 omits also stops a write.
//
// The `ensures` is a whole-sequence equality (`update`), not a statement about
// slot `i` alone, so it says both "slot `i` became `x`" and "nothing else
// moved" -- the shape `.memory/02-bench-rules.md` argues for. That matters here
// for the same reason it did on p06: `swap2` is a composition of two `update`s,
// so an `ensures` that only pinned slot `i` would not compose at all.
//
// `x` is a pure VALUE parameter -- stored, never used as an address or a length
// -- so it has no precondition, and `../spec.md`'s `verus.unsafe_justifications`
// says so and the gate shouts it every run. `.memory/04-verus.md` names this
// false positive of the parameter-coverage rule.
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

// THE BULK LOAD -- and it is NOT a trusted item. p06's TASK_048 route, reused
// verbatim: three vstd facts do the work and the axiom RELOCATES into vstd
// rather than vanishing (../NOTES.md 6 names them).
//
//   1. `vstd::array::ref_mut_array_unsizing_coercion`, which Verus inserts for
//      the implicit `&mut [u8; 64]` -> `&mut [u8]` reborrow on the line below;
//   2. `<[T]>::split_at_mut`, whose `ensures` spells the halves' write-back out;
//   3. `<[T]>::copy_from_slice`, which the pinned vstd DOES specify.
//
// The spelling is forced: the old `dst[..n]` receiver is a `RangeTo<usize>`,
// which has NO `SliceIndexSpecImpl` at the pinned vstd, so it cannot verify at
// all. `split_at_mut` is the only route that closes both ends. It is a free
// function rather than an expression inside `kernel` because R4 has to be
// byte-identical to it and a call boundary changes LLVM's inlining order.
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

// TRUSTED ITEM 4 of 5. Argument parsing, file I/O and little-endian decoding,
// delegated to common/driver.rs so that all seven rungs read the file the same
// way. It states **no** `ensures` at all, deliberately: an `ensures` here would
// be an axiom about the contents of a file, which nothing can justify. Every
// fact the proof needs is re-derived at run time from `bytes.len()` inside
// verified code.
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
        r == partition_fold(buf@, off as int, len as int),
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
    // Ghost only: `[0; 64]`'s view IS the all-zeros sequence.
    assert(scr@ =~= zero_scr());
    let mut acc: u64 = 0;
    let mut p: usize = 4;
    let mut rec: usize = 0;
    // "The records from here, with the scratch we have built and where the
    // cursor is, are all the records." p06's and p12's relational shape, with
    // the mutated SEQUENCE in the carried state. This loop exits THREE ways
    // (`rec == nrec` and the two window-exhausted breaks), so it needs
    // `invariant_except_break` plus a loop `ensures`.
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
        let pv: u8 = buf_get_unchecked(buf, off + p + 4);
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
        let mut i: usize = 0;
        let mut j: usize = m;
        // THE PARTITION. Every one of the three invariants below is the same
        // sentence -- "the partition from here is the whole partition" -- and
        // each loop's step is one case of `part`.
        while i < j
            invariant
                i <= j,
                j <= m <= SCR,
                scr@.len() == SCR,
                part(scr@, pv, i as int, j as int) == part(scr_loaded, pv, 0, m as int),
            decreases j - i,
        {
            let ghost i_entry = i as int;
            let ghost j_entry = j as int;
            // THE SAFETY LINE, half 1. c/kernel.c omits the `i < j &&`.
            // Step: `part`'s first case, `s[i] <= pv`.
            while i < j && scr_get_unchecked(&scr, i) <= pv
                invariant
                    i_entry <= i <= j <= j_entry,
                    j <= m <= SCR,
                    scr@.len() == SCR,
                    part(scr@, pv, i as int, j as int) == part(scr_loaded, pv, 0, m as int),
                decreases j - i,
            {
                i = i + 1;
            }
            // THE SAFETY LINE, half 2. c/kernel.c omits the `i < j &&`.
            // Step: `part`'s second case, `s[j-1] >= pv` -- which is only that
            // case because the scan above has already established `s[i] > pv`
            // whenever `i < j`. That is the extra conjunct in this invariant
            // and the only asymmetry between the two scans.
            while i < j && scr_get_unchecked(&scr, j - 1) >= pv
                invariant
                    i_entry <= i <= j <= j_entry,
                    j <= m <= SCR,
                    scr@.len() == SCR,
                    i == j || scr@[i as int] > pv,
                    part(scr@, pv, i as int, j as int) == part(scr_loaded, pv, 0, m as int),
                decreases j - i,
            {
                j = j - 1;
            }
            if i < j {
                // Step: `part`'s third case. Both guards hold here -- the first
                // scan left `scr[i] > pv`, the second left `scr[j-1] < pv` --
                // so the exchange and the two cursor moves are exactly what the
                // spec does, including the two-step shrink of `j - i`.
                let ghost s_pre = scr@;
                let t: u8 = scr_get_unchecked(&scr, i);
                let u: u8 = scr_get_unchecked(&scr, j - 1);
                scr_set_unchecked(&mut scr, i, u);
                scr_set_unchecked(&mut scr, j - 1, t);
                assert(scr@ =~= swap2(s_pre, i as int, j as int - 1));
                assert(part(s_pre, pv, i as int, j as int) == part(
                    scr@,
                    pv,
                    i as int + 1,
                    j as int - 1,
                ));
                i = i + 1;
                j = j - 1;
            }
        }
        let ghost acc_pre_fold = acc;
        let mut q: usize = 0;
        // "The fold from here is the whole fold." The scratch does not change in
        // this loop; what has to be carried is that `m` never left the array.
        while q < m
            invariant
                q <= m <= SCR,
                scr@.len() == SCR,
                fold_scr(scr@, q as int, m as int, acc) == fold_scr(
                    scr@,
                    0,
                    m as int,
                    acc_pre_fold,
                ),
            decreases m - q,
        {
            acc = acc.wrapping_mul(31).wrapping_add(scr_get_unchecked(&scr, q) as u64);
            q = q + 1;
        }
        acc = acc.wrapping_mul(31).wrapping_add(i as u64);
        // Ghost only: unfold `walk` once at the value it had on entry to this
        // iteration. Its `nelem`, `pv` and `m` ARE the exec values, its
        // `load_into` IS what `scr_load` did, and its `part` IS what the loop
        // nest built. So the state this iteration produced is the one the spec
        // produces.
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
            // Ghost only: `k` must land inside the blob. Two nonlinear steps.
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
            assert(r == partition_fold(buf@, (k * stride) as int, stride as int));
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    emit(acc);
}

} // verus!
