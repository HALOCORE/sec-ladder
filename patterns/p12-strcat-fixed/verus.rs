//! p12 rung R5 -- unsafe + Verus proof.
//!
//! R4's exec code verbatim, plus the specs and proofs that discharge every
//! unchecked read AND every unchecked WRITE in it.
//!
//! **What is new here is the obligation on the store.** p03 is the only earlier
//! pattern with a trusted item that writes, and its guard `sp < STACK_CAP` sits
//! in the same basic block as the store it licenses. p12's guard
//! `dlen + slen <= DST_CAP` is one loop level ABOVE the store: it is tested
//! once per string and then has to survive `slen` increments of `dlen` inside
//! the copy loop. So the fact the prover needs is
//!
//!     dlen == dlen0 + (i - p)   and   dlen0 + (q - p) <= DST_CAP   and   i < q
//!     =>  dlen < DST_CAP == dst@.len()
//!
//! which is a loop-carried invariant about a *destination cursor*, not about
//! the source. Every step of it is linear -- no `by (nonlinear_arith)` anywhere
//! in this kernel, the same as p11 and p03 and unlike p05.
//!
//! **The specification threads the destination as a sequence**, p03's shape:
//! `walk` carries `(dst: Seq<u8>, dlen: int, acc: u64)` and `copy_into` is the
//! byte-at-a-time append. That is what makes the postcondition say *which bytes
//! ended up in `dst`* and not merely that the kernel did not crash -- and it is
//! why deleting the capacity check from the exec code cannot verify: the spec
//! would then have to update a sequence outside its own length.
//!
//!     requires  off + len <= buf@.len()
//!
//! ONE clause, as on p03 and p11 and unlike p17. It is structural -- about the
//! shape of the buffer the driver built, not about its contents -- so it holds
//! on *every* input this benchmark runs, `adversarial-*` included, and the gate
//! checks it call by call. `nstr`, all 2^32 values of it, and every byte of the
//! window are attacker data and none of them is an assumption.
//!
//! **Two program lines exist to keep it at one clause, and both are priced in
//! ../NOTES.md rather than described as free:**
//!
//!   * `if q >= len { break; }` before the cursor step, which is p11's line for
//!     p11's reason (`q + 1` is `len + 1` when the window ends without a
//!     terminator, and vstd has no axiom that a slice is at most `isize::MAX`
//!     bytes). p11 measured it at 1.00000 Ir per scanned byte. Every p12 rung
//!     carries it, so no rung comparison here moves on it.
//!   * `slen <= DST_CAP` as the first conjunct of the capacity test. Without it
//!     `dlen + slen` is `usize`-addition on a `slen` that nothing bounds below
//!     `usize::MAX`, and Verus rejects it as a possible overflow -- the exact
//!     obligation p17 bought with a second `requires` and a third driver
//!     conjunct. Written as a short-circuiting `&&` it costs neither: the sum is
//!     evaluated only when `slen <= 128`, so it is provably at most 256.
//!     **The additive spelling the pattern is about survives verbatim** on the
//!     right of the `&&`. ../NOTES.md 5 prices all three routes.
//!
//! Note what the spec does **not** assume: that `nstr` is honest, that the
//! strings are terminated, or that they fit. `walk` is defined as the
//! *program's* walk, so `adversarial-off1`, `adversarial-nonul` and
//! `adversarial-overflow` are all inside the verified domain and the kernel
//! agrees with `model.py` on all three.
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
// `[u8; DST_CAP]` and the fill axiom for `[0; DST_CAP]`; p03 is the pattern
// that first needed it and p12 is the second. `lemma_u128_shr_is_div` turns
// `x >> 64` into `x / 2^64`, which is what the driver's multiply-shift barrier
// bound is about, and the mul group is what the driver's window-offset bound
// `k * stride + stride <= n_blob` needs; the KERNEL needs neither.
broadcast use {
    vstd::slice::group_slice_axioms,
    vstd::array::group_array_axioms,
    vstd::bits::lemma_u128_shr_is_div,
    vstd::arithmetic::mul::lemma_mul_inequality,
};

/// The destination's capacity, a compile-time constant in every rung.
///
/// A `const` inside `verus!` is its own obligation (`.memory/04-verus.md`,
/// measured on p08's `SCR` and again on p03's `STACK_CAP`), so this contributes
/// 1 to the count pinned in ../spec.md and the decomposition there says so.
pub const DST_CAP: usize = 128;

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

/// The destination every rung starts from. Safe Rust has no uninitialised
/// array, so all four Rust rungs write `[0u8; DST_CAP]`; C's `uint8_t dst[128];`
/// is not initialised. The initial contents are in the specification rather
/// than quantified away, exactly as p03 does for its stack: it makes the proof
/// independent of whether the destination fold can reach a slot no copy wrote.
/// (It cannot -- `dlen` only rises past `i` after slot `i` is written -- but
/// that is an extra invariant nobody has to state if the spec threads the
/// sequence.)
pub open spec fn zero_dst() -> Seq<u8> {
    Seq::new(DST_CAP as nat, |i: int| 0u8)
}

/// THE SCAN: the index of the first zero byte at or after `q`, **capped at the
/// window end**. Bounded by the window in every rung, R1 included -- p12's bug
/// is not here. p11 is the pattern that varies this function.
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

/// THE COPY: `buf[off+p .. off+q)` appended to `dst` starting at `d`, one byte
/// at a time.
///
/// **This is the one function R1 executes without its guard**, and the
/// specification cannot follow it there: `Seq::update` outside `0 .. len` is
/// unspecified rather than growing, so a rung that writes past `DST_CAP` is not
/// a rung with a different `ensures`, it is a rung with no meaning in this
/// spec at all. That is the same relation p03's `sp > 0` has to `Seq::index`.
pub open spec fn copy_into(dst: Seq<u8>, d: int, buf: Seq<u8>, off: int, p: int, q: int)
    -> Seq<u8>
    decreases q - p,
{
    if p >= q {
        dst
    } else {
        copy_into(dst.update(d, buf[off + p]), d + 1, buf, off, p + 1, q)
    }
}

/// The Horner fold over the destination's live prefix, `dst[i .. dlen)`.
pub open spec fn fold_dst(dst: Seq<u8>, i: int, dlen: int, acc: u64) -> u64
    decreases dlen - i,
{
    if i >= dlen {
        acc
    } else {
        fold_dst(dst, i + 1, dlen, acc.wrapping_mul(31).wrapping_add(dst[i] as u64))
    }
}

/// What the kernel returns once the walk is over: the destination fold, then
/// `dlen`, then the declared count.
///
/// `dlen` is mixed in so that a rung which truncated a string instead of
/// skipping it -- or which copied one byte more than it should -- cannot
/// produce the same checksum even when the bytes it folded happen to agree.
pub open spec fn fin(dst: Seq<u8>, dlen: int, acc: u64, nstr: int) -> u64 {
    fold_dst(dst, 0, dlen, acc).wrapping_mul(31).wrapping_add(dlen as u64).wrapping_mul(
        31,
    ).wrapping_add(nstr as u64)
}

/// THE MACHINE. Strings `s .. nstr`, carrying the whole state: the destination
/// contents, how much of it is live, the cursor and the accumulator.
///
/// **The walk stops at `q + 1 >= len` whatever `nstr` says**, which is the exec
/// rungs' `if q >= len { break; } p = q + 1; if p >= len { break; }` -- the two
/// guards together are exactly `q + 1 >= len`, and the first of them is what
/// makes `q + 1` provably free of `usize` overflow (see this file's header).
///
/// **The capacity test is here, and it is the line R1 omits.** A rejected
/// string still contributes its LENGTH to `acc`, so the checksum records that
/// the string was seen; what it does not record is any of its bytes.
pub open spec fn walk(
    buf: Seq<u8>,
    off: int,
    len: int,
    s: int,
    nstr: int,
    p: int,
    dst: Seq<u8>,
    dlen: int,
    acc: u64,
) -> u64
    decreases nstr - s,
{
    if s >= nstr {
        fin(dst, dlen, acc, nstr)
    } else {
        let q = scan_end(buf, off, len, p);
        let slen = q - p;
        let fits = dlen + slen <= DST_CAP as int;
        let dst2 = if fits {
            copy_into(dst, dlen, buf, off, p, q)
        } else {
            dst
        };
        let dlen2 = if fits {
            dlen + slen
        } else {
            dlen
        };
        let acc2 = acc.wrapping_mul(31).wrapping_add(slen as u64);
        if q + 1 >= len {
            fin(dst2, dlen2, acc2, nstr)
        } else {
            walk(buf, off, len, s + 1, nstr, q + 1, dst2, dlen2, acc2)
        }
    }
}

/// What the kernel returns.
///
/// The two early exits are the tests every rung keeps, R1 included: a window
/// too short to hold the header, and a zero count. **R1 keeps both.** What R1
/// omits is the `fits` test in `walk`, and that is the only thing it omits.
pub open spec fn strcat_fold(buf: Seq<u8>, off: int, len: int) -> u64 {
    if len < 4 {
        0
    } else if nstr_at(buf, off) == 0 {
        0
    } else {
        walk(buf, off, len, 0, nstr_at(buf, off), 4, zero_dst(), 0, 0)
    }
}

// ------------------------------------------------------------------- TCB ----
// TRUSTED ITEM 1 of 5. vstd ships no specification for `<[T]>::get_unchecked`,
// so this is the axiom that licenses the unchecked read of the SOURCE window.
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

// TRUSTED ITEM 2 of 5. The DESTINATION read, performed by the final fold. The
// destination is a fixed-size `[u8; 128]`, so the bound is the array's
// type-level length rather than a runtime `len()`; p03's `stack_get_unchecked`
// is the same item on `[u64; 64]`.
//
// The `requires` is ONE conjunct and NOT `i < v@.len(), v@.len() == 128`: for a
// `&[u8; 128]` the second is a TAUTOLOGY, discharged from the parameter type
// alone by vstd's `array_len_matches_n`, and p03's gate run caught exactly that
// draft (`.memory/04-verus.md`; p03 NOTES.md 5b).
#[inline(always)]
#[verifier::external_body]
fn dst_get_unchecked(v: &[u8; 128], i: usize) -> (r: u8)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    unsafe { *v.get_unchecked(i) }
}

// THE VERIFIED TWIN of trusted item 2.
#[cfg(slb_twin)]
fn slb_twin_dst_get_unchecked(v: &[u8; 128], i: usize) -> (r: u8)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    v[i]
}

// TRUSTED ITEM 3 of 5, and **the item p12 exists for**: the unchecked STORE
// into the fixed destination. p03's `stack_set_unchecked` is the same shape on
// `[u64; 64]` and it is the only precedent in this project -- so p12 is the
// second pattern with a trusted write and the first whose guard is a loop level
// above the store.
//
// The `ensures` is a whole-sequence equality (`update`), not a statement about
// slot `i` alone, so it says both "slot `i` became `x`" and "nothing else
// moved" -- the shape `.memory/02-bench-rules.md` argues for in its p02 worked
// example, where stating the property over the written prefix only would have
// proved the easy half. That matters more here than on p03: p12's whole bug is
// bytes appearing at slots the caller never asked for.
//
// `x` is a pure VALUE parameter -- stored, never used as an address or a length
// -- so it has no precondition, and `../spec.md`'s
// `verus.unsafe_justifications` says so and the gate shouts it every run.
// `.memory/04-verus.md` names this false positive of the parameter-coverage
// rule; p03 was the first pattern to exercise it and p12 is the second.
#[inline(always)]
#[verifier::external_body]
fn dst_set_unchecked(v: &mut [u8; 128], i: usize, x: u8)
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
fn slb_twin_dst_set_unchecked(v: &mut [u8; 128], i: usize, x: u8)
    requires
        i < old(v)@.len(),
    ensures
        final(v)@ == old(v)@.update(i as int, x),
{
    v[i] = x;
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
        r == strcat_fold(buf@, off as int, len as int),
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
    // Ghost only: `[0; 128]`'s view IS the all-zeros sequence. vstd's
    // `axiom_spec_array_fill_for_copy_type` gives it pointwise; `=~=` lifts
    // that to sequence equality.
    assert(dst@ =~= zero_dst());
    let mut dlen: usize = 0;
    let mut acc: u64 = 0;
    let mut p: usize = 4;
    let mut s: usize = 0;
    // "The strings from here, with the destination we have built and where the
    // cursor is, are all the strings." p16's/p11's relational shape, with p03's
    // mutated SEQUENCE in the carried state -- and one extra clause,
    // `dlen <= DST_CAP`, which is the memory-safety invariant the whole pattern
    // is about. This loop exits TWO ways (`s == nstr` and the window running
    // out), so it needs `invariant_except_break` plus a loop `ensures`.
    while s < nstr
        invariant_except_break
            s <= nstr,
            0 < nstr,
            nstr == nstr_at(buf@, off as int),
            4 <= len,
            4 <= p <= len,
            dlen <= DST_CAP,
            dst@.len() == DST_CAP,
            off + len <= buf@.len(),
            buf@.len() <= usize::MAX,
            walk(buf@, off as int, len as int, s as int, nstr as int, p as int, dst@,
                dlen as int, acc) == walk(buf@, off as int, len as int, 0, nstr as int, 4,
                zero_dst(), 0, 0),
        ensures
            dlen <= DST_CAP,
            dst@.len() == DST_CAP,
            walk(buf@, off as int, len as int, 0, nstr as int, 4, zero_dst(), 0, 0) == fin(
                dst@,
                dlen as int,
                acc,
                nstr as int,
            ),
        decreases nstr - s,
    {
        let ghost p_before = p as int;
        let ghost s_before = s as int;
        let ghost acc_before = acc;
        let ghost dst_before = dst@;
        let ghost dlen_before = dlen as int;
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
        // THE CAPACITY CHECK, and the line R1 omits. `slen <= DST_CAP` is the
        // left conjunct only so that the additive test on the right is provably
        // free of `usize` overflow -- see this file's header; it is redundant
        // as a *test* (`dlen >= 0`) and necessary as a *proof obligation*.
        if slen <= DST_CAP && dlen + slen <= DST_CAP {
            let mut i: usize = p;
            // "The copy from here is the whole copy", plus the arithmetic that
            // bounds the destination cursor: `dlen` is `dlen_before` plus how
            // far the source cursor has come, and the guard above bounds the
            // sum. Together they give `dlen < DST_CAP` at every store, which is
            // trusted item 3's precondition.
            while i < q
                invariant
                    p <= i <= q,
                    q <= len,
                    dlen as int == dlen_before + (i as int - p as int),
                    dlen_before + (q as int - p as int) <= DST_CAP,
                    dst@.len() == DST_CAP,
                    off + len <= buf@.len(),
                    buf@.len() <= usize::MAX,
                    copy_into(dst@, dlen as int, buf@, off as int, i as int, q as int)
                        == copy_into(dst_before, dlen_before, buf@, off as int,
                        p as int, q as int),
                decreases q - i,
            {
                let b: u8 = buf_get_unchecked(buf, off + i);
                dst_set_unchecked(&mut dst, dlen, b);
                dlen = dlen + 1;
                i = i + 1;
            }
        }
        acc = acc.wrapping_mul(31).wrapping_add(slen as u64);
        // Ghost only: unfold `walk` once at the value it had on entry to this
        // iteration. Its `q` IS the scan loop's `q`, its `fits` IS the capacity
        // test above and its `copy_into` IS what the copy loop built, so the
        // state this iteration produced is the one the spec produces -- and the
        // spec's `q + 1 >= len` test is the two `break`s below.
        assert(walk(buf@, off as int, len as int, s_before, nstr as int, p_before,
            dst_before, dlen_before, acc_before) == if q as int + 1 >= len as int {
            fin(dst@, dlen as int, acc, nstr as int)
        } else {
            walk(buf@, off as int, len as int, s_before + 1, nstr as int, q as int + 1,
                dst@, dlen as int, acc)
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
    let ghost acc_pre_fold = acc;
    let mut i: usize = 0;
    // "The fold from here is the whole fold." The destination does not change
    // in this loop; what has to be carried is that `dlen` never left the array,
    // which is the same invariant the copy loop maintained.
    while i < dlen
        invariant
            i <= dlen,
            dlen <= DST_CAP,
            dst@.len() == DST_CAP,
            fold_dst(dst@, i as int, dlen as int, acc) == fold_dst(
                dst@,
                0,
                dlen as int,
                acc_pre_fold,
            ),
        decreases dlen - i,
    {
        acc = acc.wrapping_mul(31).wrapping_add(dst_get_unchecked(&dst, i) as u64);
        i = i + 1;
    }
    acc.wrapping_mul(31).wrapping_add(dlen as u64).wrapping_mul(31).wrapping_add(
        nstr as u64,
    )
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
            assert(r == strcat_fold(buf@, (k * stride) as int, stride as int));
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    emit(acc);
}

} // verus!
