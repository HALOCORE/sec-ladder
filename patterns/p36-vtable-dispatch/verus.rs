//! p36 rung R5 -- unsafe + Verus proof.
//!
//! R4's exec code verbatim, plus the specs and proofs that discharge every
//! unchecked read in it -- including the one that licenses **a computed-target
//! indirect call**, which is the thing no other pattern in this tree has.
//!
//! ⚠⚠ **THE HEADLINE OF THIS FILE IS WHAT IT COULD NOT BE WRITTEN AS.** C's
//! own mechanism -- `static uint64_t (*const TABLE[8])(uint64_t)` -- has no
//! spelling here at all:
//!
//! ```text
//! $ ./verus_run.py probe_a1.rs
//! error: The verifier does not yet support the following Rust feature:
//!        function pointer types
//!   --> probe_a1.rs:20:1
//! 20 | const TABLE: [fn(u64) -> u64; 2] = [op_inc, op_dbl];
//! error: The verifier does not yet support the following Rust feature:
//!        function pointer types
//!   --> probe_a1.rs:25:13
//! 25 |     let f = TABLE[op];
//! ```
//!
//! ../spec.md pins `identity: unsafe == verus` at `norel` (../NOTES.md 5a says
//! why `exact` is unavailable and it has nothing to do with the proof), so an
//! R4 is a program that must have an R5 twin Verus verifies and that erases to
//! the same instruction stream (`.memory/01-ladder.md` finding 14). A bare `fn`-pointer table has no such
//! twin, so **the four Rust rungs dispatch through a single-trait object
//! instead** -- a real vtable and a real computed-target call, but two loads
//! where C has one. That is the sixth instance of finding 14 and the sharpest:
//! elsewhere the prover has excluded a *spelling* of the kernel (p16's
//! `chunks_exact`, p11's `memchr`, p05's and p16's header reads); here it
//! excludes the kernel's central *mechanism*, and the price is exactly
//! **3.00000 Ir per dispatch** (../NOTES.md 8a).
//!
//! **What DOES work, measured before a rung was written** (`.temp/p36/probe_a*.rs`):
//!
//! | shape | result |
//! |---|---|
//! | `const [fn(u64)->u64; N]` | `does not yet support ... function pointer types` |
//! | `&[&dyn Fn(u64)->u64]` | `does not yet support ... dyn with more that one trait` |
//! | `static [&'static dyn Op; N]` | rustc `E0277`: needs `Sync`; adding it gives `dyn with more that one trait` |
//! | **`const [&'static dyn Op; N]`** | **verifies** |
//!
//! So the table is a `const` and not a `static`, and that is forced by two
//! independent constraints meeting, not chosen.
//!
//! **THE PROOF'S ONE REAL DIFFICULTY** is that the postcondition is functional
//! -- the kernel must checksum -- so the proof has to know *which* function sits
//! in slot `op` of the table. `call_ensures`-style reasoning gives only "the
//! result satisfies the callee's postcondition, whatever the callee is"; what is
//! needed is `TABLE@[op].spec_apply(x) == op_spec(op, x)`, i.e. the DYNAMIC TYPE
//! of a trait object read out of a `const` array at a runtime index. Verus does
//! keep it, through the array literal and through the `external_body` accessor's
//! `ensures r == TABLE@[i as int]` -- probed and mutation-tested before this file
//! existed (../NOTES.md 0a), because the alternative was that p36 has no R5.
//!
//! Everything else is ordinary. The header is decoded with `+` and `*` rather
//! than `|` and `<<` (`.memory/04-verus.md`), the eight ops use only `^` with a
//! literal and wrapping `+`/`-`, and there is no shift, mask or `%` anywhere in
//! the fold -- so this file carries no `by (bit_vector)` at all.
//!
//! TCB tally: ../NOTES.md 7. **Four** `external_body` items, **two** of them
//! with contracts.
//!
//! SAFETY (1): `off + len <= buf.len()` is the caller's structural
//!   precondition. Discharged at the call site by the driver's proof below.
//! SAFETY (2): `len >= 4` guards the window header.
//! SAFETY (3): a record is read only under `len - p >= 2` with `p <= len`.
//! SAFETY (4): **the table is read, and its contents CALLED, only under
//!   `op < NOPS`.** This is the obligation `c/kernel.c` walks through, and it
//!   is the only obligation in this tree whose violation is a control transfer
//!   rather than a value.

// Plain-Rust I/O helpers. Outside `verus!`, so Verus treats the whole module as
// external (external-by-default). Reached only through `load_input`/`emit`.
#[path = "../../common/driver.rs"]
mod driver;

use vstd::prelude::*;

verus! {

// p36 targets x86-64 only (`.memory/00-environment.md`). Verus treats `usize`
// as architecture-independent by default, so the header decode's
// `16777216 * b3` is `possible arithmetic overflow` on a hypothetical 32-bit
// target. This declaration is CHECKED by Verus against the actual compilation
// target rather than assumed, so it is not an axiom and adds nothing to the TCB.
global size_of usize == 8;

// `group_slice_axioms` gives `slice@.len() == spec_slice_len(slice)`, hence
// `slice@.len() <= usize::MAX` -- without it `off + len` cannot be shown not to
// overflow `usize`. `lemma_u128_shr_is_div` turns `x >> 64` into `x / 2^64`,
// the driver's multiply-shift barrier bound, and the mul group is what the
// driver's window-offset bound needs; the KERNEL needs neither.
broadcast use {
    vstd::slice::group_slice_axioms,
    vstd::bits::lemma_u128_shr_is_div,
    vstd::arithmetic::mul::lemma_mul_inequality,
};

/// The table's extent, a compile-time constant in every rung: a bytecode
/// interpreter has a fixed number of opcodes.
///
/// A `const` inside `verus!` is its own obligation (`.memory/04-verus.md`,
/// measured on p08's `SCR`), so this contributes 1 to the count pinned in
/// ../spec.md and the decomposition there says so.
pub const NOPS: usize = 8;

/// What a rejected opcode folds. A compile-time constant in every rung.
pub const SENT: u64 = 251;

// ------------------------------------------------------------------- ops ----
/// THE OP INTERFACE. One trait and nothing else: `dyn Op + anything` is
/// `does not yet support ... dyn with more that one trait` at the pinned Verus,
/// which is also why the table below cannot be a `static`.
pub trait Op {
    // ⚠⚠ **`apply` IS DECLARED FIRST AND THAT IS LOAD-BEARING, NOT STYLE.**
    // A Verus `spec fn` declared in a trait STILL OCCUPIES A VTABLE SLOT in the
    // erased build, in declaration order. With `spec_apply` written first, R5's
    // dispatch is `call *0x20(%rcx)` where R4's is `call *0x18(%rcx)` -- same
    // 60 instructions, same 193 bytes, same normalised text, and **not**
    // byte-identical even after pc-relative masking, which would be the first
    // time in this project that a proof moved the object code. Measured both
    // ways (../NOTES.md 5), and swapping the two declarations is the whole fix.
    fn apply(&self, x: u64) -> (r: u64)
        ensures
            r == self.spec_apply(x),
    ;

    spec fn spec_apply(&self, x: u64) -> u64;
}

/// The eight op types. **ONE `impl` block, eight monomorphisations** --
/// `OpTag<0>` .. `OpTag<7>` are eight distinct types with eight distinct
/// vtables and eight distinct code addresses, so the dispatch really does have
/// eight targets.
///
/// ⚠ **Eight separate `impl Op for OpN` blocks were written first, they
/// VERIFIED (19/0), and the GATE REFUSES THEM**:
/// `harness/vparse.py::duplicate_names` fails any pinned file that defines one
/// name more than once, and eight impls define `apply` eight times. That check
/// exists for a real reason (`check.py::check_verus_contract`: *"the gate used
/// to key items by name and keep the last, so a decoy could supply the pinned
/// contract for the real item"*), and the const-generic shape is what makes p36
/// expressible inside the existing gate **with no `harness/` change**.
/// ../NOTES.md 9b has both versions and their Verus output.
pub struct OpTag<const K: u8>;

impl<const K: u8> Op for OpTag<K> {
    fn apply(&self, x: u64) -> (r: u64) {
        if K == 0 {
            x ^ 0x9e3779b97f4a7c15
        } else if K == 1 {
            x ^ 0xff51afd7ed558ccd
        } else if K == 2 {
            x.wrapping_add(0x2545f4914f6cdd1d)
        } else if K == 3 {
            x.wrapping_add(0xc4ceb9fe1a85ec53)
        } else if K == 4 {
            x.wrapping_sub(0x61c8864680b583eb)
        } else if K == 5 {
            x.wrapping_sub(0xbf58476d1ce4e5b9)
        } else if K == 6 {
            x ^ 0x94d049bb133111eb
        } else {
            x.wrapping_add(0x9e6c63d0676a9a99)
        }
    }

    open spec fn spec_apply(&self, x: u64) -> u64 {
        op_spec(K as int, x)
    }
}

/// THE TABLE. A `const`, because a `static` needs `dyn Op + Sync` and Verus
/// rejects `dyn` with a second trait. C's is a `static` and this is the one
/// place a p36 rung does not spell C's mechanism.
pub const TABLE: [&'static dyn Op; NOPS] = [
    &OpTag::<0>,
    &OpTag::<1>,
    &OpTag::<2>,
    &OpTag::<3>,
    &OpTag::<4>,
    &OpTag::<5>,
    &OpTag::<6>,
    &OpTag::<7>,
];

// ------------------------------------------------------------------ spec ----
/// The little-endian u32 at absolute byte position `p`, written out the way
/// every rung writes it: `b0 + 256*b1 + 65536*b2 + 16777216*b3`.
pub open spec fn u32_at(buf: Seq<u8>, p: int) -> int {
    buf[p] as int + 256 * (buf[p + 1] as int) + 65536 * (buf[p + 2] as int) + 16777216 * (
    buf[p + 3] as int)
}

/// How many records the window at `off` declares. **Declared, and it bounds
/// nothing** -- the `len - p < 2` cursor guard is what stops the walk.
pub open spec fn nrec_at(buf: Seq<u8>, off: int) -> int {
    u32_at(buf, off)
}

/// THE TABLE AT THE SPECIFICATION LEVEL, and the only place p36's proof is
/// interesting: this if-chain has to be shown equal to
/// `TABLE@[i].spec_apply(x)` for a RUNTIME `i`, i.e. the verifier has to keep
/// the dynamic type of each trait object in a `const` array.
pub open spec fn op_spec(i: int, x: u64) -> u64 {
    if i == 0 {
        x ^ 0x9e3779b97f4a7c15
    } else if i == 1 {
        x ^ 0xff51afd7ed558ccd
    } else if i == 2 {
        x.wrapping_add(0x2545f4914f6cdd1d)
    } else if i == 3 {
        x.wrapping_add(0xc4ceb9fe1a85ec53)
    } else if i == 4 {
        x.wrapping_sub(0x61c8864680b583eb)
    } else if i == 5 {
        x.wrapping_sub(0xbf58476d1ce4e5b9)
    } else if i == 6 {
        x ^ 0x94d049bb133111eb
    } else {
        x.wrapping_add(0x9e6c63d0676a9a99)
    }
}

/// THE ABSTRACT MACHINE, and the whole functional specification.
///
/// Note what it says and does not say: it describes the PROGRAM -- stop when
/// the declared count runs out or the window does, dispatch an in-table opcode
/// and fold the sentinel otherwise -- and it says nothing about `nrec` being
/// honest or about the opcode stream being well formed. Every adversarial input
/// is inside this domain (../spec.md).
pub open spec fn run(
    buf: Seq<u8>,
    off: int,
    len: int,
    t: int,
    nrec: int,
    p: int,
    acc: u64,
) -> u64
    decreases nrec - t,
{
    if t >= nrec || len - p < 2 {
        acc.wrapping_mul(31).wrapping_add(t as u64)
    } else {
        let op = buf[off + p] as int;
        let arg = buf[off + p + 1] as u64;
        if op < NOPS as int {
            run(buf, off, len, t + 1, nrec, p + 2, op_spec(op, acc ^ arg))
        } else {
            run(
                buf,
                off,
                len,
                t + 1,
                nrec,
                p + 2,
                acc.wrapping_mul(31).wrapping_add(SENT),
            )
        }
    }
}

/// What the kernel must return.
pub open spec fn op_fold(buf: Seq<u8>, off: int, len: int) -> u64 {
    if len < 4 {
        0
    } else if nrec_at(buf, off) == 0 {
        0
    } else {
        run(buf, off, len, 0, nrec_at(buf, off), 4, 0)
    }
}

// --------------------------------------------------------------- trusted ----
// TRUSTED ITEM 1 of 4. The unchecked window read. vstd ships no specification
// for `<[T]>::get_unchecked`, and the standard library's documented contract is
// exactly this `requires`/`ensures` pair.
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

// THE VERIFIED TWIN of trusted item 1. Same signature, same contract, body the
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

// TRUSTED ITEM 2 of 4. **THE UNCHECKED TABLE READ -- the one that licenses a
// computed-target indirect call, and the only item of its kind in this tree.**
//
// It closes over `TABLE` instead of taking it as a parameter because
// `&'static dyn Op` in a `T: Copy` type-parameter position drags the `dyn`
// support into a generic instantiation; the concrete signature is the one that
// verifies, and p22's and p27's generic `arr_get_unchecked` is therefore not
// reusable here.
//
// ⚠ **What the `ensures` claims is the SLOT'S IDENTITY, not the callee's
// behaviour.** `r == TABLE@[i as int]` says the reference returned is the one
// the table holds at `i`; everything about what calling it does then comes from
// `Op::apply`'s own `ensures`, which is VERIFIED for each of the eight impls.
// A wrapper that instead axiomatised "calling slot `i` yields `op_spec(i, x)`"
// would have put all eight function bodies inside the TCB; that alternative is
// built and measured as the control `r5_extbody` (../NOTES.md 8c).
#[inline(always)]
#[verifier::external_body]
fn tab_get_unchecked(i: usize) -> (r: &'static dyn Op)
    requires
        i < NOPS,
    ensures
        r == TABLE@[i as int],
{
    unsafe { *TABLE.get_unchecked(i) }
}

// THE VERIFIED TWIN of trusted item 2.
#[cfg(slb_twin)]
fn slb_twin_tab_get_unchecked(i: usize) -> (r: &'static dyn Op)
    requires
        i < NOPS,
    ensures
        r == TABLE@[i as int],
{
    TABLE[i]
}

// TRUSTED ITEM 3 of 4. Argument parsing, file I/O and little-endian decoding,
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

// TRUSTED ITEM 4 of 4. `println!` is not verifiable; no `ensures`. Counted with
// the three above -- every `external_body` item is TCB, not just the interesting
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
        r == op_fold(buf@, off as int, len as int),
{
    // Ghost only: mentioning `spec_slice_len` fires vstd's `axiom_spec_len`,
    // which is what tells the SMT solver a slice length fits in a `usize`.
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
    // The record count is hoisted, exactly as R3 hoists it: record `t` is read
    // iff `t < nrec` and `len - (4 + 2t) >= 2`, i.e. iff
    // `t < min(nrec, (len - 4) / 2)`. Same records, same answer, no
    // per-record cursor test.
    //
    // ⚠ **THIS IS AN R4 SPELLING THAT WAS CHOSEN AFTER SEARCHING THE R4 SIDE,
    // AND SAYING SO IS THE POINT.** The R2-shaped unsafe rung -- the one that
    // keeps the per-record cursor test, which is what every other pattern in
    // this tree ships as its R4 -- also verifies (`12 verified, 0 errors`) and
    // costs **1022 / 8190 MORE** Ir per call. Shipping that one would have made
    // p36 publish *safe Rust beats unsafe Rust*, which would have been true of
    // the two spellings and false of the safety axis. It is measured as the
    // control `r4_cursor` and ../NOTES.md 8b publishes both numbers.
    let room: usize = (len - 4) / 2;
    let nw: usize = if nrec < room { nrec } else { room };
    let mut acc: u64 = 0;
    let mut p: usize = 4;
    let mut t: usize = 0;
    while t < nw
        invariant
            off + len <= buf@.len(),
            buf@.len() <= usize::MAX,
            len >= 4,
            room == (len - 4) / 2,
            nw <= room,
            nw <= nrec,
            nrec == nrec_at(buf@, off as int),
            nrec > 0,
            p == 4 + 2 * t,
            t <= nw,
            run(buf@, off as int, len as int, t as int, nrec as int, p as int, acc) == run(
                buf@,
                off as int,
                len as int,
                0,
                nrec as int,
                4,
                0,
            ),
        decreases nw - t,
    {
        let op: usize = buf_get_unchecked(buf, off + p) as usize;
        let arg: u64 = buf_get_unchecked(buf, off + p + 1) as u64;
        p = p + 2;
        // THE SAFETY LINE. c/kernel.c omits exactly this test and dispatches
        // unconditionally; every other rung writes it by hand.
        if op < NOPS {
            acc = tab_get_unchecked(op).apply(acc ^ arg);
        } else {
            acc = acc.wrapping_mul(31).wrapping_add(SENT);
        }
        t = t + 1;
    }
    acc.wrapping_mul(31).wrapping_add(t as u64)
}

// ---------------------------------------------------------------- driver ----
fn main() {
    let (n_iters, stride_w, bytes) = load_input();
    // SLB-DRIVER-BEGIN
    let n_blob: usize = bytes.len();
    let buf: &[u8] = bytes.as_slice();
    let mut acc: u64 = 0;
    if stride_w >= 6 && stride_w <= n_blob as u64 {
        let stride: usize = stride_w as usize;
        let nwin: u64 = (n_blob / stride) as u64;
        let mut it: u64 = 0;
        // Ghost only: at least one whole window is present.
        proof {
            vstd::arithmetic::div_mod::lemma_div_non_zero(n_blob as int, stride as int);
        }
        while it < n_iters
            invariant
                6 <= stride <= n_blob,
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
            assert(r == op_fold(buf@, (k * stride) as int, stride as int));
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    emit(acc);
}

} // verus!
