//! p04 rung R5 -- unsafe + Verus proof.
//!
//! R4's exec code verbatim, plus the specs and proofs that discharge every
//! unchecked read and write in it.
//!
//! **What is new here is that the memory-safety obligation is NOT relational,
//! on the first kernel in this project that has a relation to state.** `head`
//! and `tail` are both live state and the program's two guards are relations
//! between them -- `head != tail` is "non-empty", `(tail + 1) % RING_CAP ==
//! head` is "full". TASK_042 predicted that the R5 invariant would be the work.
//! It is not, and the reason is the pattern's headline: what the accessors need
//! is
//!
//!     head < RING_CAP,
//!     tail < RING_CAP,
//!
//! two INDEPENDENT one-variable facts, each maintained by its own
//! `(x + 1) % RING_CAP` and by nothing else. **Neither guard participates.**
//! Z3 takes the whole file first try, with no lemma, no `by (nonlinear_arith)`
//! and no proof block beyond the two the driver already needs.
//!
//! That is not a convenience, it *is* the security result. Because the guards
//! are absent from the memory-safety argument, deleting one is invisible to it:
//! NOTES.md 6 measures `m_nofull_msonly` at `9 verified, 0 errors` in the
//! shipped configuration and `12 verified, 0 errors` under `--cfg slb_twin`
//! (the twin adds the three `_twin` items) -- R1's bug transplanted into R5
//! with the functional specification stripped -- against a positive control
//! (`tail = tail + 1` with the `%` removed) that fails on the very same
//! invariant. Both numbers are printed there; the citation used to name only
//! the 12 and NOTES.md 6 used to print only the 9 (TASK_042_REVIEW minor 7). **Memory safety is not the property that catches this**,
//! for the second time in this project after p09, and here the mechanism is
//! visible in the invariant rather than inferred from a probe.
//!
//! What DOES catch it is the functional half, and it is the relational
//! invariant below: `run(from here) == run(the whole thing)`. Delete the
//! fullness check with the specification in place and that clause fails
//! (`invariant not satisfied at end of loop body`, NOTES.md 6).
//!
//!     requires  off + len <= buf@.len()
//!
//! It is ONE clause, structural -- about the shape of the buffer the driver
//! built, not about its contents -- so it holds on *every* input this benchmark
//! runs, `adversarial-*` included, and the gate checks it call by call. `nops`,
//! all 2^32 values of it, and every byte of the window are attacker data and
//! none of them is an assumption.
//!
//! p11 and p17 both had to buy a second fact (`buf@.len() <= isize::MAX`), one
//! with a precondition and one with a program change (`.memory/04-verus.md`).
//! **p04 needs neither**, for p03's reason on the buffer side -- every index it
//! forms is `off + 4 + 5*k` with `5*k < 5*nops <= len - 4` -- and for a new one
//! on the ring side: `%` bounds its own result, so the ring index needs no
//! reasoning about the loop at all.
//!
//! Note what the spec does **not** assume: that `nops` is honest, that the ring
//! is non-empty when a POP arrives, or that it is non-full when a PUSH does.
//! `run` is defined as the *program's* run -- take each guard, or do not,
//! exactly as the exec code does -- so `adversarial-overwrite.bin` is inside
//! the verified domain and the kernel agrees with `model.py` on it. A
//! `requires` that the opcode stream never overfills would be a precondition
//! about the contents of a file that no honest loader can discharge
//! (`.memory/02-bench-rules.md`), and it would delete the row that is the
//! pattern.
//!
//! TCB tally: NOTES.md 5b. **Five `external_body` items, three of them
//! `unsafe`** -- p03's shape, for p03's reason: the kernel has two buffers and
//! one of them is written.

use vstd::prelude::*;

// Plain-Rust I/O helpers. Outside `verus!`, so Verus treats the whole module as
// external (external-by-default). Reached only through `load_input`/`emit`.
#[path = "../../common/driver.rs"]
mod driver;

verus! {

// `group_slice_axioms` gives `slice@.len() == spec_slice_len(slice)`, hence
// `slice@.len() <= usize::MAX` -- without it `off + len` cannot be shown not to
// overflow `usize`. `group_array_axioms` gives `ring@.len() == RING_CAP` for a
// `[u64; RING_CAP]` and the fill axiom for `[0; RING_CAP]`.
// `lemma_u128_shr_is_div` turns `x >> 64` into `x / 2^64`, which is what the
// driver's multiply-shift barrier bound is about, and the mul group is what the
// driver's window-offset bound `k * stride + stride <= n_blob` needs; the
// KERNEL needs neither, exactly as on p07, p11 and p03.
broadcast use {
    vstd::slice::group_slice_axioms,
    vstd::array::group_array_axioms,
    vstd::bits::lemma_u128_shr_is_div,
    vstd::arithmetic::mul::lemma_mul_inequality,
};

/// The ring's capacity, a compile-time constant in every rung, **and a POWER OF
/// TWO** -- which is the pattern's independent variable. `controls/` ships the
/// same sources at 60.
///
/// The ring holds `RING_CAP - 1` elements, not `RING_CAP`: the fullness test is
/// `(tail + 1) % RING_CAP == head`, so one slot is always reserved and
/// `head == tail` is unambiguously *empty*.
///
/// A `const` inside `verus!` is its own obligation (`.memory/04-verus.md`,
/// measured on p08's `SCR` and again on p03's `STACK_CAP`), so this contributes
/// 1 to the count pinned in ../spec.md and the decomposition there says so.
pub const RING_CAP: usize = 64;

// ------------------------------------------------------------------ spec ----
/// The little-endian u32 at absolute byte position `p`, written out the way
/// every rung writes it: `b0 + 256*b1 + 65536*b2 + 16777216*b3`.
///
/// Spelled with `+` and `*` rather than `|` and `<<` on purpose
/// (`.memory/04-verus.md`): the two are the same function on bytes and compile
/// to the same instruction -- clang and rustc both fold this back into one
/// unaligned 32-bit `mov` (NOTES.md 2) -- but only the first is linear
/// arithmetic. The alternative drags in `by (bit_vector)` for no gain.
pub open spec fn u32_at(buf: Seq<u8>, p: int) -> int {
    buf[p] as int + 256 * (buf[p + 1] as int) + 65536 * (buf[p + 2] as int)
        + 16777216 * (buf[p + 3] as int)
}

/// How many operations the window at `off` declares: a little-endian u32 at
/// window bytes 0..4. **Declared, and bounded only by the length check** -- see
/// `ring_fold`.
pub open spec fn nops_at(buf: Seq<u8>, off: int) -> int {
    u32_at(buf, off)
}

/// The ring every rung starts from. Safe Rust has no uninitialised array, so
/// all four Rust rungs write `[0u64; RING_CAP]`; C's `uint64_t ring[64];` is
/// not initialised. The initial contents are in the specification rather than
/// quantified away, which is what makes the proof independent of whether a POP
/// can reach a slot no PUSH wrote. (It cannot -- `head` only advances toward
/// `tail`, and every slot strictly between them was written -- but that is an
/// extra invariant nobody has to state if the spec simply threads the
/// sequence.)
pub open spec fn zero_ring() -> Seq<u64> {
    Seq::new(RING_CAP as nat, |i: int| 0u64)
}

/// THE MACHINE. Operations `k .. nops`, carrying the whole state: the ring
/// contents, both cursors and the accumulator.
///
/// This is the one function in the file whose *shape* R1 does not implement.
/// R1's PUSH arm has no `(tail + 1) % RING_CAP != head` test, so on a full ring
/// it writes the reserved slot and moves `tail` onto `head` -- **an entirely
/// in-bounds store** that makes the ring read empty. Unlike p03's `sp - 1` at
/// `sp == 0`, this is an index `Seq::index` can express perfectly well; what it
/// cannot express is the *right answer*, which is why the divergence shows up
/// in the postcondition and nowhere else.
///
/// **Both guards are here, and only one is the variable.** `head != tail` is in
/// every rung including R1, so a rung that popped an empty ring would fail the
/// checksum on `adversarial-wrap.bin` rather than being a second bug.
pub open spec fn run(
    buf: Seq<u8>,
    off: int,
    k: int,
    nops: int,
    ring: Seq<u64>,
    head: int,
    tail: int,
    acc: u64,
) -> u64
    decreases nops - k,
{
    if k >= nops {
        acc.wrapping_mul(31).wrapping_add(head as u64).wrapping_mul(31).wrapping_add(
            tail as u64,
        ).wrapping_mul(31).wrapping_add(nops as u64)
    } else {
        let val = u32_at(buf, off + 5 + 5 * k) as u64;
        if buf[off + 4 + 5 * k] == 0 {
            if (tail + 1) % (RING_CAP as int) != head {
                run(
                    buf,
                    off,
                    k + 1,
                    nops,
                    ring.update(tail, val),
                    head,
                    (tail + 1) % (RING_CAP as int),
                    acc,
                )
            } else {
                run(buf, off, k + 1, nops, ring, head, tail, acc)
            }
        } else {
            if head != tail {
                run(
                    buf,
                    off,
                    k + 1,
                    nops,
                    ring,
                    (head + 1) % (RING_CAP as int),
                    tail,
                    acc.wrapping_mul(31).wrapping_add(ring[head]),
                )
            } else {
                run(buf, off, k + 1, nops, ring, head, tail, acc)
            }
        }
    }
}

/// What the kernel returns.
///
/// The three early exits are the tests every rung keeps, R1 included: a window
/// too short to hold the header, a zero count, and a declared count the window
/// cannot hold. **R1 keeps all three.** What R1 omits is the fullness arm of
/// `run`, and that is the only thing it omits.
pub open spec fn ring_fold(buf: Seq<u8>, off: int, len: int) -> u64 {
    if len < 4 {
        0
    } else if nops_at(buf, off) == 0 {
        0
    } else if 5 * nops_at(buf, off) > len - 4 {
        0
    } else {
        run(buf, off, 0, nops_at(buf, off), zero_ring(), 0, 0, 0)
    }
}

// ------------------------------------------------------------------- TCB ----
// TRUSTED ITEM 1 of 5. vstd ships no specification for `<[T]>::get_unchecked`,
// so this is the axiom that licenses the unchecked read of the OPCODE STREAM.
// It is sound because the standard library's documented contract for
// `get_unchecked` is exactly this: if the caller guarantees `i < v.len()`, the
// call is defined and yields `v[i]`. Identical, character for character, to the
// accessor p01, p02, p03, p05, p07, p11, p16 and p17 ship.
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

// TRUSTED ITEM 2 of 5: the ring READ, at `head`. The bound is the array's
// type-level length rather than a runtime `len()`, as on p03.
//
// **This is the read the pattern is about, and the interesting thing is what
// its precondition does NOT need.** `i < v@.len()` here reads `head < 64`, and
// the caller discharges it from `head = (head + 1) % RING_CAP` alone -- not
// from the emptiness guard beside it, not from any relation to `tail`. Delete
// the guard and this precondition still holds. NOTES.md 6 is the measurement.
#[inline(always)]
#[verifier::external_body]
fn ring_get_unchecked(v: &[u64; 64], i: usize) -> (r: u64)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    unsafe { *v.get_unchecked(i) }
}

// THE VERIFIED TWIN of trusted item 2.
#[cfg(slb_twin)]
fn slb_twin_ring_get_unchecked(v: &[u64; 64], i: usize) -> (r: u64)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    v[i]
}

// TRUSTED ITEM 3 of 5: the ring WRITE, at `tail`. p03 is the only other pattern
// here with a trusted item that stores through an unchecked index.
//
// The `ensures` is a whole-sequence equality (`update`), not a statement about
// slot `i` alone, so it says both "slot `i` became `x`" and "nothing else
// moved" -- the shape `.memory/02-bench-rules.md` argues for in its p02 worked
// example, where stating the property over the written prefix only would have
// proved the easy half. On p04 that clause is doing more work than usual: R1's
// bug IS a write to a slot the checked kernel does not write, and a
// slot-`i`-only `ensures` would have been silent about it in the twin as well
// as in the proof.
//
// `x` is a pure VALUE parameter -- written, never used as an address or a
// length -- so it has no precondition, and `../spec.md`'s
// `verus.unsafe_justifications` says so and the gate shouts it every run.
// `.memory/04-verus.md` names this exact false positive of the
// parameter-coverage rule; p03 was the first pattern to exercise it and p04 is
// the second. NOTES.md 5b.
#[inline(always)]
#[verifier::external_body]
fn ring_set_unchecked(v: &mut [u64; 64], i: usize, x: u64)
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
fn slb_twin_ring_set_unchecked(v: &mut [u64; 64], i: usize, x: u64)
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
        r == ring_fold(buf@, off as int, len as int),
{
    // Ghost only: mentioning `spec_slice_len` fires vstd's `axiom_spec_len`,
    // which is what tells the SMT solver a slice length fits in a `usize` --
    // needed to rule out `off + len` overflowing. Erases at compile time.
    assert(buf@.len() == vstd::slice::spec_slice_len(buf));
    if len < 4 {
        return 0;
    }
    let nops: usize = buf_get_unchecked(buf, off) as usize + 256 * (buf_get_unchecked(
        buf,
        off + 1,
    ) as usize) + 65536 * (buf_get_unchecked(buf, off + 2) as usize) + 16777216 * (
    buf_get_unchecked(buf, off + 3) as usize);
    if nops == 0 {
        return 0;
    }
    if 5 * (nops as u64) > (len - 4) as u64 {
        return 0;
    }
    let mut ring: [u64; RING_CAP] = [0; RING_CAP];
    // Ghost only: `[0; 64]`'s view IS the all-zeros sequence. vstd's
    // `axiom_spec_array_fill_for_copy_type` gives it pointwise; `=~=` lifts that
    // to sequence equality.
    assert(ring@ =~= zero_ring());
    let mut acc: u64 = 0;
    let mut head: usize = 0;
    let mut tail: usize = 0;
    let mut k: usize = 0;
    // "The operations from here, with the ring, the two cursors and the
    // accumulator we have, are the whole run." Same relational shape as p16's
    // walk, p07's query loop, p11's scan and p03's machine. The two clauses that
    // do the MEMORY-SAFETY work are `head < RING_CAP` and `tail < RING_CAP`, and
    // they are the two that are NOT relational -- see the module comment.
    while k < nops
        invariant
            k <= nops,
            head < RING_CAP,
            tail < RING_CAP,
            ring@.len() == RING_CAP,
            4 <= len,
            5 * nops <= len - 4,
            nops == nops_at(buf@, off as int),
            off + len <= buf@.len(),
            buf@.len() <= usize::MAX,
            run(
                buf@,
                off as int,
                k as int,
                nops as int,
                ring@,
                head as int,
                tail as int,
                acc,
            ) == run(buf@, off as int, 0, nops as int, zero_ring(), 0, 0, 0),
        decreases nops - k,
    {
        let op: u8 = buf_get_unchecked(buf, off + 4 + 5 * k);
        let val: u64 = buf_get_unchecked(buf, off + 5 + 5 * k) as u64 + 256 * (
        buf_get_unchecked(buf, off + 6 + 5 * k) as u64) + 65536 * (buf_get_unchecked(
            buf,
            off + 7 + 5 * k,
        ) as u64) + 16777216 * (buf_get_unchecked(buf, off + 8 + 5 * k) as u64);
        if op == 0 {
            if (tail + 1) % RING_CAP != head {
                ring_set_unchecked(&mut ring, tail, val);
                tail = (tail + 1) % RING_CAP;
            }
        } else {
            if head != tail {
                acc = acc.wrapping_mul(31).wrapping_add(ring_get_unchecked(&ring, head));
                head = (head + 1) % RING_CAP;
            }
        }
        k = k + 1;
    }
    acc.wrapping_mul(31).wrapping_add(head as u64).wrapping_mul(31)
        .wrapping_add(tail as u64).wrapping_mul(31).wrapping_add(nops as u64)
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
            assert(r == ring_fold(buf@, (k * stride) as int, stride as int));
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    emit(acc);
}

} // verus!
