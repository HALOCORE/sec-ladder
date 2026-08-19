//! p03 rung R5 -- unsafe + Verus proof.
//!
//! R4's exec code verbatim, plus the specs and proofs that discharge every
//! unchecked read and write in it.
//!
//! **What is new here is that the obligation is a loop invariant over a branch
//! the ATTACKER chooses.** p05's index is `i*ncol + j`, nonlinear but computable
//! before the loop; p07's is `off + 8 + 4*mid`; p11's scan has no closed form
//! but its *sequence of operations* is still fixed by the code. p03's is not:
//! the file decides, per step, whether `sp` goes up or down, so
//!
//!     sp <= STACK_CAP
//!
//! has to survive a two-armed branch whose condition is a byte of the input,
//! and the back edge. **Z3 discharges it in one invariant clause with no lemma,
//! no `by (nonlinear_arith)` and no proof block. LLVM does not discharge it at
//! all**, and that gap is p03's published number: 3.00000 Ir per executed pop in
//! both safe rungs (NOTES.md 4). This is p05's *"the price of the optimiser
//! failing the lemma the proof proves"* on a fact that is **linear** -- p05's
//! excuse was nonlinearity and p03 does not have that excuse. p08 is the other
//! precedent: a provably-dead, purely linear range check that LLVM keeps because
//! the fact it needs is relational across the loop.
//!
//! **The other half of the same sentence is that the PUSH side is free.** The
//! push's `stack[sp]` sits inside `if sp < STACK_CAP` in the same basic block,
//! so LLVM deletes that check and the safe rungs' push path is
//! instruction-identical to this one's. One array, one constant bound, one
//! function, two answers, and the discriminator is whether the guard is in the
//! same block as the index or a loop invariant away from it.
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
//! **p03 needs neither**, and the reason is worth stating because it is not
//! virtue: every index this kernel forms is `off + 4 + 5*k` with
//! `5*k < 5*nops <= len - 4`, so it is bounded by `off + len` and the
//! structural `requires` already bounds that by `buf@.len()`. The length check
//! every rung carries is what makes the arithmetic total. p03's hard obligation
//! is somewhere else entirely, and it is `sp`.
//!
//! Note what the spec does **not** assume: that `nops` is honest, that the
//! stack is non-empty when a POP arrives, or that any push ever happened.
//! `run` is defined as the *program's* run -- take the guard, or do not, exactly
//! as the exec code does -- so `adversarial-underflow.bin` and
//! `adversarial-allpop.bin` are inside the verified domain and the kernel agrees
//! with `model.py` on both. A `requires` that the opcode stream is well bracketed
//! would be a precondition about the contents of a file that no honest loader
//! can discharge (`.memory/02-bench-rules.md`), and it would delete the rows
//! that are the pattern.
//!
//! TCB tally: NOTES.md 5b. **Five `external_body` items, three of them
//! `unsafe`** -- p01, p02, p05, p07, p11, p16 and p17 each have exactly one
//! unsafe accessor, and p03 has three because the kernel has *two* buffers and
//! one of them is written. NOTES.md 5b reports what that costs.

use vstd::prelude::*;

// Plain-Rust I/O helpers. Outside `verus!`, so Verus treats the whole module as
// external (external-by-default). Reached only through `load_input`/`emit`.
#[path = "../../common/driver.rs"]
mod driver;

verus! {

// `group_slice_axioms` gives `slice@.len() == spec_slice_len(slice)`, hence
// `slice@.len() <= usize::MAX` -- without it `off + len` cannot be shown not to
// overflow `usize`. `group_array_axioms` gives `stack@.len() == STACK_CAP` for a
// `[u64; STACK_CAP]` and the fill axiom for `[0; STACK_CAP]`; p03 is the first
// pattern in this project with a fixed-size array, so it is the first to need
// it. `lemma_u128_shr_is_div` turns `x >> 64` into `x / 2^64`, which is what the
// driver's multiply-shift barrier bound is about, and the mul group is what the
// driver's window-offset bound `k * stride + stride <= n_blob` needs; the KERNEL
// needs neither, exactly as on p07 and p11.
broadcast use {
    vstd::slice::group_slice_axioms,
    vstd::array::group_array_axioms,
    vstd::bits::lemma_u128_shr_is_div,
    vstd::arithmetic::mul::lemma_mul_inequality,
};

/// The stack's capacity, a compile-time constant in every rung.
///
/// A `const` inside `verus!` is its own obligation (`.memory/04-verus.md`,
/// measured on p08's `SCR`), so this contributes 1 to the count pinned in
/// ../spec.md and the decomposition there says so.
pub const STACK_CAP: usize = 64;

// ------------------------------------------------------------------ spec ----
/// The little-endian u32 at absolute byte position `p`, written out the way
/// every rung writes it: `b0 + 256*b1 + 65536*b2 + 16777216*b3`.
///
/// Spelled with `+` and `*` rather than `|` and `<<` on purpose
/// (`.memory/04-verus.md`): the two are the same function on bytes and compile
/// to the same instruction -- clang and rustc both fold this back into one
/// unaligned 32-bit `mov` (NOTES.md 0) -- but only the first is linear
/// arithmetic. The alternative drags in `by (bit_vector)` for no gain.
pub open spec fn u32_at(buf: Seq<u8>, p: int) -> int {
    buf[p] as int + 256 * (buf[p + 1] as int) + 65536 * (buf[p + 2] as int)
        + 16777216 * (buf[p + 3] as int)
}

/// How many operations the window at `off` declares: a little-endian u32 at
/// window bytes 0..4. **Declared, and bounded only by the length check** -- see
/// `stack_fold`.
pub open spec fn nops_at(buf: Seq<u8>, off: int) -> int {
    u32_at(buf, off)
}

/// The stack every rung starts from. Safe Rust has no uninitialised array, so
/// all four Rust rungs write `[0u64; STACK_CAP]`; C's `uint64_t stack[64];` is
/// not initialised. The initial contents are in the specification rather than
/// quantified away, which is what makes the proof independent of whether a POP
/// can reach a slot no PUSH wrote. (It cannot -- `sp` only rises past `i` after
/// slot `i` is written -- but that is an extra invariant nobody has to state if
/// the spec simply threads the sequence.)
pub open spec fn zero_stack() -> Seq<u64> {
    Seq::new(STACK_CAP as nat, |i: int| 0u64)
}

/// THE MACHINE. Operations `k .. nops`, carrying the whole state: the stack
/// contents, the stack pointer and the accumulator.
///
/// This is the one function in the file whose *shape* R1 does not implement.
/// R1's POP arm has no `sp > 0` test, so its `sp - 1` is `SIZE_MAX` and its
/// `stack[sp]` is a read 8 bytes below the array -- an index this specification
/// cannot even express, because `Seq::index` outside `0 .. len` is unspecified
/// rather than wrapping. The guard is simultaneously the memory-safety check,
/// the thing that keeps `sp` a `nat`, and the reason the fold is a function of
/// the input at all.
///
/// **Both guards are here, and only one is the variable.** `sp < STACK_CAP` is
/// in every rung including R1, so a rung that overflowed the array would fail
/// the checksum on `adversarial-overflow.bin` rather than being a second bug.
pub open spec fn run(
    buf: Seq<u8>,
    off: int,
    k: int,
    nops: int,
    stack: Seq<u64>,
    sp: int,
    acc: u64,
) -> u64
    decreases nops - k,
{
    if k >= nops {
        acc.wrapping_mul(31).wrapping_add(sp as u64).wrapping_mul(31).wrapping_add(
            nops as u64,
        )
    } else {
        let val = u32_at(buf, off + 5 + 5 * k) as u64;
        if buf[off + 4 + 5 * k] == 0 {
            if sp < STACK_CAP as int {
                run(buf, off, k + 1, nops, stack.update(sp, val), sp + 1, acc)
            } else {
                run(buf, off, k + 1, nops, stack, sp, acc)
            }
        } else {
            if sp > 0 {
                run(
                    buf,
                    off,
                    k + 1,
                    nops,
                    stack,
                    sp - 1,
                    acc.wrapping_mul(31).wrapping_add(stack[sp - 1]),
                )
            } else {
                run(buf, off, k + 1, nops, stack, sp, acc)
            }
        }
    }
}

/// What the kernel returns.
///
/// The three early exits are the tests every rung keeps, R1 included: a window
/// too short to hold the header, a zero count, and a declared count the window
/// cannot hold. **R1 keeps all three.** What R1 omits is the `sp > 0` arm of
/// `run`, and that is the only thing it omits.
pub open spec fn stack_fold(buf: Seq<u8>, off: int, len: int) -> u64 {
    if len < 4 {
        0
    } else if nops_at(buf, off) == 0 {
        0
    } else if 5 * nops_at(buf, off) > len - 4 {
        0
    } else {
        run(buf, off, 0, nops_at(buf, off), zero_stack(), 0, 0)
    }
}

// ------------------------------------------------------------------- TCB ----
// TRUSTED ITEM 1 of 5. vstd ships no specification for `<[T]>::get_unchecked`,
// so this is the axiom that licenses the unchecked read of the OPCODE STREAM.
// It is sound because the standard library's documented contract for
// `get_unchecked` is exactly this: if the caller guarantees `i < v.len()`, the
// call is defined and yields `v[i]`. Identical, character for character, to the
// accessor p01, p02, p05, p07, p11, p16 and p17 ship.
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

// TRUSTED ITEM 2 of 5, and the first accessor in this project that is NOT the
// slice one. The stack is a fixed-size `[u64; STACK_CAP]`, so the bound is the
// array's type-level length rather than a runtime `len()`. `requires` names
// both parameters the body uses.
//
// **This is the read the pattern is about.** R1's missing `sp > 0` makes its
// argument `SIZE_MAX`; `i < v@.len()` is exactly what excludes it, and
// NOTES.md 6c is the mutant that shows the obligation is load-bearing rather
// than decorative.
//
// The `requires` is ONE conjunct and NOT `i < v@.len(), v@.len() == 64`. The
// second clause was there in the first draft and the gate refused it: for a
// `&[u64; 64]` it is a **tautology**, discharged from the parameter type alone
// by vstd's `array_len_matches_n`, so it demanded nothing of any caller and
// stage 5c-req's tautology probe said so (`10 verified, 0 errors -- control 9`)
// while 5c-twin's per-conjunct deletion showed the twin never used it. NOTES.md
// 5b records it, because a tautological conjunct on a TRUSTED item is exactly
// the shape `.memory/04-verus.md` warns about.
#[inline(always)]
#[verifier::external_body]
fn stack_get_unchecked(v: &[u64; 64], i: usize) -> (r: u64)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    unsafe { *v.get_unchecked(i) }
}

// THE VERIFIED TWIN of trusted item 2.
#[cfg(slb_twin)]
fn slb_twin_stack_get_unchecked(v: &[u64; 64], i: usize) -> (r: u64)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    v[i]
}

// TRUSTED ITEM 3 of 5, and the project's first trusted item that WRITES through
// an unchecked index. p02's `copy_bytes` writes, but through
// `copy_nonoverlapping` into a `&mut [u8]` whose length is a runtime value; this
// one is an indexed store into a fixed-size array.
//
// The `ensures` is a whole-sequence equality (`update`), not a statement about
// slot `i` alone, so it says both "slot `i` became `x`" and "nothing else
// moved" -- the shape `.memory/02-bench-rules.md` argues for in its p02 worked
// example, where stating the property over the written prefix only would have
// proved the easy half.
//
// `x` is a pure VALUE parameter -- written, never used as an address or a
// length -- so it has no precondition, and `../spec.md`'s
// `verus.unsafe_justifications` says so and the gate shouts it every run.
// `.memory/04-verus.md` names this exact false positive of the
// parameter-coverage rule and records that nothing in the tree exercised it;
// p03 is the first pattern that does. NOTES.md 5b.
#[inline(always)]
#[verifier::external_body]
fn stack_set_unchecked(v: &mut [u64; 64], i: usize, x: u64)
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
fn slb_twin_stack_set_unchecked(v: &mut [u64; 64], i: usize, x: u64)
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
        r == stack_fold(buf@, off as int, len as int),
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
    let mut stack: [u64; STACK_CAP] = [0; STACK_CAP];
    // Ghost only: `[0; 64]`'s view IS the all-zeros sequence. vstd's
    // `axiom_spec_array_fill_for_copy_type` gives it pointwise; `=~=` lifts that
    // to sequence equality.
    assert(stack@ =~= zero_stack());
    let mut acc: u64 = 0;
    let mut sp: usize = 0;
    let mut k: usize = 0;
    // "The operations from here, with the stack, the stack pointer and the
    // accumulator we have, are the whole run." Same relational shape as p16's
    // walk, p07's query loop and p11's scan -- but the state it carries is a
    // SEQUENCE the loop mutates, not just a scalar, and the clause that does the
    // memory-safety work is the plain `sp <= STACK_CAP` beside it.
    while k < nops
        invariant
            k <= nops,
            sp <= STACK_CAP,
            stack@.len() == STACK_CAP,
            4 <= len,
            5 * nops <= len - 4,
            nops == nops_at(buf@, off as int),
            off + len <= buf@.len(),
            buf@.len() <= usize::MAX,
            run(buf@, off as int, k as int, nops as int, stack@, sp as int, acc) == run(
                buf@,
                off as int,
                0,
                nops as int,
                zero_stack(),
                0,
                0,
            ),
        decreases nops - k,
    {
        let op: u8 = buf_get_unchecked(buf, off + 4 + 5 * k);
        let val: u64 = buf_get_unchecked(buf, off + 5 + 5 * k) as u64 + 256 * (
        buf_get_unchecked(buf, off + 6 + 5 * k) as u64) + 65536 * (buf_get_unchecked(
            buf,
            off + 7 + 5 * k,
        ) as u64) + 16777216 * (buf_get_unchecked(buf, off + 8 + 5 * k) as u64);
        if op == 0 {
            if sp < STACK_CAP {
                stack_set_unchecked(&mut stack, sp, val);
                sp = sp + 1;
            }
        } else {
            if sp > 0 {
                sp = sp - 1;
                acc = acc.wrapping_mul(31).wrapping_add(stack_get_unchecked(&stack, sp));
            }
        }
        k = k + 1;
    }
    acc.wrapping_mul(31).wrapping_add(sp as u64).wrapping_mul(31).wrapping_add(nops as u64)
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
            assert(r == stack_fold(buf@, (k * stride) as int, stride as int));
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    emit(acc);
}

} // verus!
