//! p18 rung R5 -- unsafe + Verus proof.
//!
//! R4's exec code verbatim, plus the specs and proofs that discharge every
//! unchecked read in it **and the arithmetic obligation that is the pattern's
//! whole subject**.
//!
//! **THE OBLIGATION THAT MATTERS HERE IS NOT A MEMORY-SAFETY OBLIGATION, AND
//! p18 IS THE FIRST PATTERN IN THIS PROJECT WHERE THAT IS TRUE.** Every earlier
//! rung's trusted `requires` and R1's missing line are about the same fact: an
//! index against an extent. Here they are about different facts. The trusted
//! accessor demands `i < v@.len()`, which is spatial; R1's bug is `shift < 64`,
//! which is arithmetic. Delete the safety line from this file and the trusted
//! item's `requires` still discharges exactly as before -- what fails is
//!
//!     error: possible bit shift underflow/overflow
//!
//! raised by Verus on `val | (((c & 0x7f) as u64) << shift)` itself, with no
//! accessor and no `ensures` involved. ../NOTES.md 10 has the mutant and the
//! exact error text; ../NOTES.md 6 has the three trusted bases side by side.
//!
//! **The specification is written with the SAME bit operators the exec code
//! uses** -- `&`, `|`, `<<` -- so no bit-vector reasoning is needed anywhere in
//! this file and there is not one `by (bit_vector)` in it. That is a deliberate
//! choice and it is what makes a bit-twiddling kernel provable in one session:
//! `vdec` is not "the mathematical value of the varint", it is *the fold the
//! program performs*, and the width truncation is in the spec because it is in
//! the program. `model.py` is the independent check on that -- it accumulates in
//! Python's unbounded integers with **no width test at all** and masks once at
//! the end, which is the other way of saying the same thing, and the two agree
//! on every input.
//!
//! **What that costs, stated here rather than left to be found:** it means the
//! proof cannot see `truncating.bin`'s bug, because `varint_fold` specifies the
//! truncation. That is p17's limit, on arithmetic instead of on a range, and it
//! is exactly the honest thing a functional postcondition can and cannot buy.
//! ../NOTES.md 7b.
//!
//!     requires  off + len <= buf@.len()
//!
//! ONE clause, as on p03, p06, p11, p12 and p14 and unlike p17. It is
//! structural -- about the shape of the buffer the driver built, not about its
//! contents -- so it holds on *every* input this benchmark runs,
//! `adversarial-*` included, and the gate checks it call by call. `nv` and every
//! byte of the window including every continue bit in it are attacker data and
//! none of them is an assumption.
//!
//! **The cursor guards are DIRECT COMPARISONS and that is what keeps the clause
//! count at one.** p07's and p14's subtraction-first idiom exists because their
//! cursors advance by a *declared* length and the additive form `p + 4 > len`
//! can overflow `usize`. p18's cursor advances by ONE, so `p < len` and
//! `p == len` need no arithmetic at all and there is nothing to overflow. All
//! seven rungs use it, so no rung comparison moves on it. ../NOTES.md 5.
//!
//! TCB tally: NOTES.md 6. **Three** `external_body` items, **one** of them with
//! a `requires` -- the smallest trusted base of any pattern in this project, and
//! for a structural reason worth naming: p18's kernel performs exactly ONE kind
//! of memory access, a byte read of the input window, so there is exactly one
//! accessor to trust. There is no scratch, no output buffer, no bulk copy and
//! no write of any kind.

use vstd::prelude::*;

// Plain-Rust I/O helpers. Outside `verus!`, so Verus treats the whole module as
// external (external-by-default). Reached only through `load_input`/`emit`.
#[path = "../../common/driver.rs"]
mod driver;

verus! {

// `group_slice_axioms` gives `slice@.len() == spec_slice_len(slice)`, hence
// `slice@.len() <= usize::MAX` -- without it `off + len` cannot be shown not to
// overflow `usize`. `lemma_u128_shr_is_div` turns `x >> 64` into `x / 2^64`,
// which is what the driver's multiply-shift barrier bound is about, and the mul
// group is what the driver's window-offset bound `k * stride + stride <= n_blob`
// needs; the KERNEL needs neither. p18 needs NO array group -- it has no array.
broadcast use {
    vstd::slice::group_slice_axioms,
    vstd::bits::lemma_u128_shr_is_div,
    vstd::arithmetic::mul::lemma_mul_inequality,
};

/// The accumulator's width, a compile-time constant in every rung. **This is
/// the bound R1 omits**, and it is a bound on a SHIFT COUNT rather than on a
/// length or an index -- the first of its kind in this project.
pub const VBITS: u32 = 64;

// ------------------------------------------------------------------ spec ----
/// The little-endian u32 at absolute byte position `p`, written out the way
/// every rung writes it: `b0 + 256*b1 + 65536*b2 + 16777216*b3`.
///
/// Spelled with `+` and `*` rather than `|` and `<<` on purpose
/// (`.memory/04-verus.md`): the two are the same function on bytes and compile
/// to the same instruction, but only the first is linear arithmetic. **On p18
/// that choice is doing real work**, because the varint decode below is the one
/// place this project genuinely needs `|` and `<<` in a spec, and confining
/// them to that one place is what keeps the solver out of bit-vector territory.
pub open spec fn u32_at(buf: Seq<u8>, p: int) -> int {
    buf[p] as int + 256 * (buf[p + 1] as int) + 65536 * (buf[p + 2] as int)
        + 16777216 * (buf[p + 3] as int)
}

/// How many varints the window at `off` declares. **Declared, and it bounds
/// nothing** -- see `vwalk`.
pub open spec fn nv_at(buf: Seq<u8>, off: int) -> int {
    u32_at(buf, off)
}

/// THE DECODE: the value one varint accumulates to, starting at cursor `p` with
/// shift `shift` and accumulator `val`.
///
/// **The `if shift < VBITS` here IS the safety line**, in the specification,
/// in the same position and with the same spelling as in the exec code. That is
/// what makes it a proof obligation rather than a convention: strip it from the
/// exec code and Verus raises `possible bit shift underflow/overflow` on the
/// `<<` itself.
///
/// A recursion and not a closed form, because a varint's length is not known
/// until its last byte has been read -- which is also why no rung of p18 can
/// vectorise and why the scan is inherently serial.
pub open spec fn vdec(buf: Seq<u8>, off: int, len: int, p: int, shift: u32, val: u64) -> u64
    decreases len - p,
{
    if p >= len {
        val
    } else {
        let c = buf[off + p];
        let v2 = if shift < VBITS {
            val | (((c & 0x7f) as u64) << shift)
        } else {
            val
        };
        if c & 0x80 == 0 {
            v2
        } else {
            vdec(buf, off, len, p + 1, shift.wrapping_add(7), v2)
        }
    }
}

/// How many bytes that varint consumes: bytes with the continue bit set, plus
/// the terminator, bounded by the window. **The scan is bounded in the SPEC
/// exactly as in every rung** -- `p >= len` stops it -- which is why p18 has no
/// out-of-bounds read to prove anything about.
pub open spec fn vbytes(buf: Seq<u8>, off: int, len: int, p: int) -> int
    decreases len - p,
{
    if p >= len {
        0
    } else if buf[off + p] & 0x80 == 0 {
        1
    } else {
        1 + vbytes(buf, off, len, p + 1)
    }
}

/// THE MACHINE. Varints `v .. nv`, carrying the cursor and the accumulator.
///
/// **The walk stops when the window runs out, whatever `nv` says** -- the
/// `p == len` guard is in the spec because it is in every rung.
///
/// The fold is `val` then `nb`, in that order, per varint. `val` is what makes a
/// wrong SHIFT visible; `nb` is what makes a wrong CURSOR visible -- a rung that
/// capped the varint at ten bytes instead of guarding the shift consumes
/// different bytes and cannot produce this checksum. ../NOTES.md 2 tabulates
/// which mutation each catches.
pub open spec fn vwalk(
    buf: Seq<u8>,
    off: int,
    len: int,
    v: int,
    nv: int,
    p: int,
    acc: u64,
) -> u64
    decreases nv - v,
{
    if v >= nv {
        acc
    } else if p == len {
        acc
    } else {
        let val = vdec(buf, off, len, p, 0, 0);
        let nb = vbytes(buf, off, len, p);
        vwalk(
            buf,
            off,
            len,
            v + 1,
            nv,
            p + nb,
            acc.wrapping_mul(31).wrapping_add(val).wrapping_mul(31).wrapping_add(nb as u64),
        )
    }
}

/// What the kernel returns.
///
/// The two early exits are the tests every rung keeps, R1 included: a window too
/// short to hold the header, and a zero count. **R1 keeps both.** What R1 omits
/// is the `shift < VBITS` test inside `vdec`, and that is the only thing it
/// omits.
pub open spec fn varint_fold(buf: Seq<u8>, off: int, len: int) -> u64 {
    if len < 4 {
        0
    } else if nv_at(buf, off) == 0 {
        0
    } else {
        vwalk(buf, off, len, 0, nv_at(buf, off), 4, 0).wrapping_mul(31).wrapping_add(
            nv_at(buf, off) as u64,
        )
    }
}

// ------------------------------------------------------------------- TCB ----
// TRUSTED ITEM 1 of 3, and **the only one with a `requires`**. vstd ships no
// specification for `<[T]>::get_unchecked`, so this is the axiom that licenses
// the unchecked read of the window. It is sound because the standard library's
// documented contract for `get_unchecked` is exactly this: if the caller
// guarantees `i < v.len()`, the call is defined and yields `v[i]`. Identical,
// character for character, to the accessor p01, p02, p03, p05, p06, p07, p11,
// p12, p13, p14, p16 and p17 ship.
//
// **On p18 this item has nothing to do with the pattern's bug**, and that is
// the point. It excludes an out-of-bounds READ; R1's defect is an out-of-range
// SHIFT. Weakening or deleting its `requires` does not admit R1's bug and
// keeping it does not exclude it. ../NOTES.md 6.
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

// TRUSTED ITEM 2 of 3. Argument parsing, file I/O and little-endian decoding,
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

// TRUSTED ITEM 3 of 3. `println!` is not verifiable; no `ensures`. Counted with
// the two above -- every `external_body` item is TCB, not just the interesting
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
        r == varint_fold(buf@, off as int, len as int),
{
    // Ghost only: mentioning `spec_slice_len` fires vstd's `axiom_spec_len`,
    // which is what tells the SMT solver a slice length fits in a `usize` --
    // needed to rule out `off + p` overflowing. Erases at compile time.
    assert(buf@.len() == vstd::slice::spec_slice_len(buf));
    if len < 4 {
        return 0;
    }
    let nv: usize = buf_get_unchecked(buf, off) as usize + 256 * (buf_get_unchecked(
        buf,
        off + 1,
    ) as usize) + 65536 * (buf_get_unchecked(buf, off + 2) as usize) + 16777216 * (
    buf_get_unchecked(buf, off + 3) as usize);
    if nv == 0 {
        return 0;
    }
    let mut acc: u64 = 0;
    let mut p: usize = 4;
    let mut v: usize = 0;
    // "The varints from here, with where the cursor is, are all the varints."
    // p06's, p12's and p14's relational shape. This loop exits TWO ways
    // (`v == nv` and the window-exhausted break), so it needs
    // `invariant_except_break` plus a loop `ensures`.
    while v < nv
        invariant_except_break
            v <= nv,
            0 < nv,
            nv == nv_at(buf@, off as int),
            4 <= len,
            4 <= p <= len,
            off + len <= buf@.len(),
            buf@.len() <= usize::MAX,
            vwalk(buf@, off as int, len as int, v as int, nv as int, p as int, acc)
                == vwalk(buf@, off as int, len as int, 0, nv as int, 4, 0),
        ensures
            vwalk(buf@, off as int, len as int, 0, nv as int, 4, 0) == acc,
        decreases nv - v,
    {
        if p == len {
            break;
        }
        let ghost p_before = p as int;
        let ghost acc_before = acc;
        let mut val: u64 = 0;
        let mut shift: u32 = 0;
        let mut nb: usize = 0;
        // THE SCAN. It exits two ways -- cursor off the end of the window, or
        // the continue bit clear -- and both must land on the same `ensures`,
        // so the invariant is carried `except_break` and the postcondition is
        // stated once. The invariant is one unfolding of `vdec` per step; there
        // is no lemma anywhere in this file.
        while p < len
            invariant_except_break
                4 <= p_before <= p <= len,
                off + len <= buf@.len(),
                buf@.len() <= usize::MAX,
                p_before + nb == p,
                // `nb == p - p_before` and `p_before >= 4`, so `nb < len`. It is
                // spelled out because it is what stops `nb = nb + 1` from being
                // a possible `usize` overflow -- the ONE obligation this file
                // failed on its first run (../NOTES.md 5).
                nb < len,
                vdec(buf@, off as int, len as int, p_before, 0, 0) == vdec(
                    buf@,
                    off as int,
                    len as int,
                    p as int,
                    shift,
                    val,
                ),
                vbytes(buf@, off as int, len as int, p_before) == nb + vbytes(
                    buf@,
                    off as int,
                    len as int,
                    p as int,
                ),
            ensures
                p_before <= p <= len,
                p_before + nb == p,
                nb <= len,
                vdec(buf@, off as int, len as int, p_before, 0, 0) == val,
                vbytes(buf@, off as int, len as int, p_before) == nb,
            decreases len - p,
        {
            let c: u8 = buf_get_unchecked(buf, off + p);
            p = p + 1;
            nb = nb + 1;
            // THE SAFETY LINE. c/kernel.c omits exactly this.
            if shift < VBITS {
                val = val | (((c & 0x7f) as u64) << shift);
            }
            shift = shift.wrapping_add(7);
            if c & 0x80 == 0 {
                break;
            }
        }
        acc = acc.wrapping_mul(31).wrapping_add(val);
        acc = acc.wrapping_mul(31).wrapping_add(nb as u64);
        // Ghost only: unfold `vwalk` once at the value it had on entry to this
        // iteration. Its `vdec` IS the value the scan built and its `vbytes` IS
        // the number of bytes the scan consumed.
        assert(vwalk(buf@, off as int, len as int, v as int, nv as int, p_before, acc_before)
            == vwalk(buf@, off as int, len as int, v as int + 1, nv as int, p as int, acc));
        v = v + 1;
    }
    acc.wrapping_mul(31).wrapping_add(nv as u64)
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
            // Z3 needs both spelled out. Erases at compile time -- R4 and R5
            // stay byte-identical.
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
            assert(r == varint_fold(buf@, (k * stride) as int, stride as int));
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    emit(acc);
}

} // verus!
