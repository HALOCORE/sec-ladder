//! p02 rung R5 -- unsafe + Verus proof.
//!
//! R4's exec code verbatim, plus the specs and proofs that discharge every
//! unchecked operation in it. What the proof is *about*, in one line: the
//! kernel's runtime rejection test is sufficient, so the raw copy that follows
//! it cannot write outside `dst`.
//!
//! Read `.memory/02-bench-rules.md`, "The precondition must be structural. The
//! attack must be data.", beside this file. The `requires` is
//!
//!     src_off + 2 <= src@.len()
//!
//! and nothing else: the two prefix bytes are inside the source buffer. That
//! holds on *every* input this benchmark runs, `adversarial-*` included, and
//! the gate checks it call by call. The attacker-controlled length is an
//! argument of the problem, not an assumption -- `kernel` is total in it, and
//! the security property lives in the `ensures`:
//!
//!     dst@ =~= copy_dst(old(dst)@, src@, src_off as int)
//!
//! which pins the *entire* final destination buffer, so it says both "the
//! record landed where it should" and "not one byte outside it moved". A
//! `requires` that excluded the over-long length would verify, would pass the
//! gate, and would be worthless.
//!
//! TCB tally: NOTES.md. Four `external_body` items -- 10 lines -- all listed
//! there individually, because an under-counted TCB is how the pilot's fatal
//! defect hid in plain sight (`.memory/04-verus.md`).

use vstd::prelude::*;

// Plain-Rust I/O helpers. Outside `verus!`, so Verus treats the whole module as
// external (external-by-default). Reached only through `load_input`/`emit`.
#[path = "../../common/driver.rs"]
mod driver;

verus! {

// `group_slice_axioms` gives `slice@.len() == spec_slice_len(slice)`, hence
// `slice@.len() <= usize::MAX` -- without it `src_off + 2` cannot be shown not
// to overflow `usize`. `lemma_u128_shr_is_div` turns `x >> 64` into `x / 2^64`,
// which is what the driver's multiply-shift barrier bound is about. The mul and
// div groups are what the record-offset bound `k * stride + 2 <= n_src` needs:
// both steps of it are nonlinear.
broadcast use {
    vstd::slice::group_slice_axioms,
    vstd::bits::lemma_u128_shr_is_div,
    vstd::arithmetic::mul::lemma_mul_inequality,
};

// ------------------------------------------------------------------ spec ----
/// The length the record at `off` declares: a little-endian u16 prefix.
/// Attacker data. Every value in `0 ..= 65535` is possible and the kernel is
/// total on all of them.
pub open spec fn rec_len(src: Seq<u8>, off: int) -> int {
    src[off] as int + 256 * (src[off + 1] as int)
}

/// Whether the record at `off` may be copied into a buffer of `cap` bytes:
/// it fits the destination, and its body is entirely inside the source. These
/// are exactly the two terms of the runtime test every rung but R1 writes.
pub open spec fn fits(src: Seq<u8>, off: int, cap: int) -> bool {
    &&& rec_len(src, off) <= cap
    &&& off + 2 + rec_len(src, off) <= src.len()
}

/// The destination buffer after the call -- *all* of it. Below `rec_len` it is
/// the record; from `rec_len` up it is whatever was there before; and a record
/// that does not fit leaves the buffer untouched. This one function is the
/// security property, which is why the `ensures` states it as an equality on
/// the whole sequence rather than as a property of the copied prefix.
pub open spec fn copy_dst(dst0: Seq<u8>, src: Seq<u8>, off: int) -> Seq<u8> {
    if fits(src, off, dst0.len() as int) {
        src.subrange(off + 2, off + 2 + rec_len(src, off)) + dst0.subrange(
            rec_len(src, off),
            dst0.len() as int,
        )
    } else {
        dst0
    }
}

/// Wrapping sum of `s[from .. from+n)`. `u64::wrapping_add` is usable in spec
/// position because vstd marks it `#[verifier::allow_in_spec]`.
pub open spec fn sum_bytes(s: Seq<u8>, from: int, n: int) -> u64
    decreases n,
{
    if n <= 0 {
        0u64
    } else {
        sum_bytes(s, from, n - 1).wrapping_add(s[from + n - 1] as u64)
    }
}

/// What the kernel returns: the wrapping sum of the bytes it copied, or 0 for a
/// record it rejected. Stated over `src`, not over the destination, so the
/// postcondition can only hold if the copy actually happened and was correct.
pub open spec fn copy_sum(src: Seq<u8>, off: int, cap: int) -> u64 {
    if fits(src, off, cap) {
        sum_bytes(src, off + 2, rec_len(src, off))
    } else {
        0u64
    }
}

/// Equal elements give equal sums. This is the one real induction in the file:
/// the loop accumulates over `dst` (which is what it can read) while the
/// postcondition is stated over `src` (which is what a caller can reason
/// about), and the copy is what makes the two agree.
proof fn lemma_sum_congruent(a: Seq<u8>, b: Seq<u8>, fa: int, fb: int, n: int)
    requires
        0 <= n,
        forall|j: int| 0 <= j < n ==> #[trigger] a[fa + j] == b[fb + j],
    ensures
        sum_bytes(a, fa, n) == sum_bytes(b, fb, n),
    decreases n,
{
    if n > 0 {
        lemma_sum_congruent(a, b, fa, fb, n - 1);
        assert(a[fa + (n - 1)] == b[fb + (n - 1)]);
    }
}

// ------------------------------------------------------------------- TCB ----
// TRUSTED ITEM 1 of 4. vstd ships no specification for `<[T]>::get_unchecked`,
// so this is the axiom that licenses the unchecked read. It is sound because
// the standard library's documented contract for `get_unchecked` is exactly
// this: if the caller guarantees `i < v.len()`, the call is defined and yields
// `v[i]`. The `requires` is not decoration -- for the two prefix bytes it is
// discharged from the kernel's own precondition, and for the fold it is
// discharged from the rejection test, which is the whole point of the pattern.
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

// THE VERIFIED TWIN of trusted item 1 (`harness/check.py` step 5c-twin).
//
// Same signature and same contract, character for character -- the gate lifts
// both from `get_unchecked` above and refuses a twin whose signature differs --
// but implemented in *checked* code. A `requires` too weak to license
// `*v.get_unchecked(i)` is too weak to license `v[i]`, and Verus can see the
// second one. Weaken the pair to `i <= v@.len()` and this fails with
// `precondition not met: index in bounds for this access`; that off-by-one
// passed the entire gate before this stage existed (TASK_008_REVIEW), because
// 5a only asks whether the clause mentions every parameter and 5c-req only
// whether it is a tautology, and `i <= v@.len()` is neither trivial nor silent.
//
// `#[cfg(slb_twin)]` is a cfg no build ever sets, so rustc strips this before
// codegen: the twin costs zero instructions structurally, and the pinned
// obligation count stays 9 (the `--cfg slb_twin` run reports 12).
#[cfg(slb_twin)]
fn slb_twin_get_unchecked(v: &[u8], i: usize) -> (r: u8)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    v[i]
}

// TRUSTED ITEM 2 of 4, and the one this pattern is about. `copy_nonoverlapping`
// has three documented preconditions and the `requires` below carries two of
// them; the third -- that the regions do not overlap -- is discharged by Rust's
// own aliasing rules rather than by the verifier, because `&[u8]` and
// `&mut [u8]` cannot name the same allocation.
//
// **One `ensures`, deliberately.** It says exactly what the intrinsic does: `n`
// bytes land at `dst[0..n)` and **every byte from `n` up is the byte that was
// already there**. It is the clause a reviewer should attack first: if it were
// wrong, everything above it would be worthless.
//
// It used to be two, the second being `final(dst)@.len() == old(dst)@.len()`
// ("`copy_nonoverlapping` does not reallocate"). That clause is *entailed* by
// this one -- a subrange of length `n` concatenated with a subrange of length
// `old(dst).len() - n` has length `old(dst).len()` -- so it was an axiom the
// TCB tally counted, a reviewer had to judge, and nothing depended on. The gate
// derives that now (`check.py` step 5c: delete each `ensures` clause of each
// `external_body` item and fail if the file still verifies) and it fired here:
// deleting the length clause left `9 verified, 0 errors`. Prefer one strong
// clause to several overlapping ones -- an overlapping pair can also hide a
// later weakening of the strong half behind the weak half.
#[inline(always)]
#[verifier::external_body]
fn copy_bytes(src: &[u8], from: usize, dst: &mut [u8], n: usize)
    requires
        from + n <= src@.len(),
        n <= old(dst)@.len(),
    ensures
        final(dst)@ =~= src@.subrange(from as int, from + n as int) + old(dst)@.subrange(
            n as int,
            old(dst)@.len() as int,
        ),
{
    unsafe {
        core::ptr::copy_nonoverlapping(src.as_ptr().add(from), dst.as_mut_ptr(), n);
    }
}

// THE VERIFIED TWIN of trusted item 2 (`harness/check.py` step 5c-twin).
//
// The interesting one: the checked equivalent of THIS bulk copy cannot be
// another bulk copy -- it has to be the indexed loop below.
//
// ** The reason recorded here until TASK_048 was FALSE.** It read "there is no
// vstd spec for `copy_from_slice` (`.memory/04-verus.md`)", and the pinned vstd
// DOES specify it, at `vstd/std_specs/slice.rs:205`. Measured at TASK_048: with
// the body respelled `let (a, b) = dst.split_at_mut(n);
// a.copy_from_slice(&src[from..from + n]);` the item above needs no
// `external_body` at all and the file verifies `10 verified, 0 errors`
// (twin `13 verified, 0 errors`).
//
// ** p02 keeps the trusted wrapper anyway, and the price of NOT keeping it is
// measured** (../NOTES.md 5b): the verified spelling is 81/79 instructions
// against R4's 72/70, `md5_fn 90b5fba6bc35` against `0e5b59364bb6`, +5.00
// executed `Ir` per call flat, one surviving panic pad -- so it BREAKS
// `identity: unsafe == verus, O3 exact`. The discriminator is what R4's body is:
// `core::ptr::copy_nonoverlapping`, `<[T]>::as_ptr`, `<[T]>::as_mut_ptr` and
// `<*const T>::add` are all `is not supported` at the pinned vstd, so R5 cannot
// verify R4's spelling and cannot match R4's bytes without this wrapper.
// (p06's R4 writes `copy_from_slice` already, so p06 DID land the same removal
// at zero cost -- p06 NOTES.md 6.)
//
// That the loop verifying is what rules out the false-failure reading is
// unchanged: if the twin failed for want of a spec rather than for want of a
// precondition, the stage would be worse than useless. It verifies (12
// verified, 0 errors with `--cfg slb_twin`), so the failures it reports are
// about the precondition.
//
// Weaken `from + n <= src@.len()` to `from + n <= src@.len() + 1` -- the copy's
// form of the same off-by-one, which passed the whole gate at TASK_008_REVIEW --
// and this fails at `src[from + j]` with `precondition not met: index in bounds
// for this access`, because reading `src[src@.len()]` is exactly what the
// weakened clause would license `copy_nonoverlapping` to do.
//
// The `assert` and the `src@.len() <= usize::MAX` invariant are the ambient
// fact `vstd::slice::axiom_spec_len` supplies, fired the same way the kernel
// fires it; they are ghost and this whole item is cfg'd out of every build.
#[cfg(slb_twin)]
fn slb_twin_copy_bytes(src: &[u8], from: usize, dst: &mut [u8], n: usize)
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
            from + n <= src@.len(),
            src@.len() <= usize::MAX,
            dst@.len() == old(dst)@.len(),
            forall|q: int| 0 <= q < j ==> dst@[q] == src@[from + q],
            forall|q: int| j <= q < dst@.len() ==> dst@[q] == old(dst)@[q],
        decreases n - j,
    {
        dst[j] = src[from + j];
        j = j + 1;
    }
}

// TRUSTED ITEM 3 of 4. Argument parsing, file I/O, little-endian decoding and
// the destination allocation, delegated to common/driver.rs so that all six
// rungs read the file and size the buffer the same way. It states **no**
// `ensures` at all, deliberately: an `ensures` here would be an axiom about the
// contents of a file, which nothing can justify. Every fact the proof needs is
// re-derived at run time from `bytes.len()` inside verified code.
#[verifier::external_body]
fn load_input() -> (r: (u64, u64, Vec<u8>, Vec<u8>)) {
    let path = driver::arg_path();
    let inp = driver::load(&path);
    let (cap_w, stride_w, bytes) = driver::head2_u64_bytes(&inp);
    let dbuf = driver::zeroed(cap_w);
    (inp.n_iters, stride_w, bytes, dbuf)
}

// TRUSTED ITEM 4 of 4. `println!` is not verifiable; no `ensures`. Counted with
// the three above -- every `external_body` item is TCB, not just the
// interesting one.
#[verifier::external_body]
fn emit(acc: u64) {
    driver::emit(acc);
}

// ---------------------------------------------------------------- kernel ----
// Same exec code as unsafe.rs. Contract: ../spec.md.
//
// Two `ensures`, not three. The third used to be
// `final(dst)@.len() == old(dst)@.len()`, and `copy_dst` returns a sequence of
// `dst0`'s length on both branches, so the security clause already says it.
// `check.py` step 5c derives that -- deleting it left `9 verified, 0 errors`,
// i.e. nothing in the file, the driver's consuming asserts included, depended
// on it. A postcondition nothing depends on is decoration
// (`.memory/04-verus.md`), and here it was decoration that made the published
// contract look like three obligations when it is two.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(src: &[u8], src_off: usize, dst: &mut [u8]) -> (r: u64)
    requires
        src_off + 2 <= src@.len(),
    ensures
        r == copy_sum(src@, src_off as int, final(dst)@.len() as int),
        final(dst)@ =~= copy_dst(old(dst)@, src@, src_off as int),
{
    // Ghost only: mentioning `spec_slice_len` fires vstd's `axiom_spec_len`,
    // which is what tells the SMT solver a slice length fits in a `usize` --
    // needed to rule out `src_off + 2` overflowing. Erases at compile time.
    assert(src@.len() == vstd::slice::spec_slice_len(src));
    let len: usize = get_unchecked(src, src_off) as usize + 256 * (get_unchecked(
        src,
        src_off + 1,
    ) as usize);
    if len > dst.len() || len > src.len() - (src_off + 2) {
        return 0;
    }
    copy_bytes(src, src_off + 2, dst, len);
    let mut acc: u64 = 0;
    for i in 0..len
        invariant
            len <= dst@.len(),
            forall|j: int| 0 <= j < len ==> #[trigger] dst@[j] == src@[src_off + 2 + j],
            acc == sum_bytes(dst@, 0, i as int),
    {
        acc = acc.wrapping_add(get_unchecked(dst, i) as u64);
    }
    proof {
        lemma_sum_congruent(dst@, src@, 0, src_off + 2, len as int);
    }
    acc
}

// ---------------------------------------------------------------- driver ----
fn main() {
    let (n_iters, stride_w, bytes, mut dbuf) = load_input();
    // SLB-DRIVER-BEGIN
    let n_src: usize = bytes.len();
    let src: &[u8] = bytes.as_slice();
    let dst: &mut [u8] = dbuf.as_mut_slice();
    let mut acc: u64 = 0;
    if stride_w >= 2 && stride_w <= n_src as u64 {
        let stride: usize = stride_w as usize;
        let nrec: u64 = (n_src / stride) as u64;
        let mut it: u64 = 0;
        // Ghost only: at least one whole record is present. `stride <= n_src`
        // is the guard immediately above, and integer division only rounds
        // down, so `n_src / stride >= 1` -- but that is a fact about division
        // and Z3 needs the lemma named.
        proof {
            vstd::arithmetic::div_mod::lemma_div_non_zero(n_src as int, stride as int);
        }
        while it < n_iters
            invariant
                2 <= stride <= n_src,
                src@.len() == n_src,
                nrec == n_src / stride,
                nrec >= 1,
            decreases n_iters - it,
        {
            // Ghost only: `k` must land inside the record blob. Two nonlinear
            // steps, so Z3 needs both spelled out. (1) `(acc * nrec) >> 64 <
            // nrec` because `acc <= u64::MAX` implies `acc * nrec < nrec *
            // 2^64`; `lemma_u128_shr_is_div` turns the shift into the division
            // the argument is about. (2) `k * stride + 2 <= n_src` because
            // `k <= nrec - 1` and `nrec * stride <= n_src`. Erases at compile
            // time -- R4 and R5 stay byte-identical.
            proof {
                let p: int = (acc as int) * (nrec as int);
                assert((acc as u128) * (nrec as u128) <= (u64::MAX as u128) * (u64::MAX
                    as u128)) by (nonlinear_arith)
                    requires
                        acc <= u64::MAX,
                        nrec <= u64::MAX,
                ;
                assert(vstd::arithmetic::power2::pow2(64) == 0x1_0000_0000_0000_0000nat) by {
                    vstd::arithmetic::power2::lemma2_to64_rest();
                }
                assert(p < (nrec as int) * 0x1_0000_0000_0000_0000int) by (nonlinear_arith)
                    requires
                        p == (acc as int) * (nrec as int),
                        acc <= u64::MAX,
                        nrec >= 1,
                ;
            }
            let k: usize = ((acc as u128 * nrec as u128) >> 64) as usize;
            // Ghost only: the record index `k` names a record that is entirely
            // present, so `k * stride + 2 <= n_src` and the kernel's structural
            // precondition is discharged. `nrec * stride <= n_src` because
            // division rounds down; `k * stride <= (nrec - 1) * stride` because
            // `k < nrec`. Both are nonlinear.
            proof {
                assert(k < nrec);
                vstd::arithmetic::div_mod::lemma_fundamental_div_mod(
                    n_src as int,
                    stride as int,
                );
                assert((nrec as int) * (stride as int) <= n_src as int);
                assert((k as int) * (stride as int) <= ((nrec as int) - 1) * (stride as int));
                assert(((nrec as int) - 1) * (stride as int) == (nrec as int) * (stride as int)
                    - (stride as int)) by (nonlinear_arith);
                assert((k as int) * (stride as int) + 2 <= n_src as int);
            }
            // Ghost only: the destination as it was before the call, so that
            // the security postcondition below has something to be stated
            // against. `let ghost` erases exactly as `assert` does.
            let ghost d0: Seq<u8> = dst@;
            let r: u64 = kernel(src, k * stride, dst);
            // Ghost only: this is what *consumes* the kernel's `ensures`.
            // Without it the postcondition is decoration -- deleting it
            // entirely still verifies, so nothing but mutation testing defends
            // it (`.memory/04-verus.md`). Ghost code erases, so the driver loop
            // stays byte-identical to R4's; `harness/dloop.py` exempts ghost
            // statements from the driver diff exactly as it exempts
            // `invariant`/`decreases`.
            assert(r == copy_sum(src@, (k * stride) as int, dst@.len() as int));
            // ... and this consumes the *security* clause, which nothing else
            // would. Without it, replacing `dst@ =~= copy_dst(...)` with a
            // tautology still verifies -- the return value does not depend on
            // it -- so the one postcondition this whole pattern exists to state
            // would have been defended by mutation testing alone.
            assert(dst@ =~= copy_dst(d0, src@, (k * stride) as int));
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    emit(acc);
}

} // verus!
