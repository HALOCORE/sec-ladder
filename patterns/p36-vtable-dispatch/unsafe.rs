//! p36 rung R4 -- unsafe Rust.
//!
//! **R3's loop structure with every window read and the table access spelled
//! unchecked**, so that `R3 - R4` differs in the bounds checks and in nothing
//! else. ⚠ That is a DECISION and it is disclosed: the R2-shaped unsafe rung --
//! the one that keeps the per-record cursor test, which is what every other
//! pattern in this tree ships as its R4 -- also verifies as an R5 twin and is
//! **1022 / 8190 Ir per call DEARER**. Shipping it would have made p36 publish
//! *safe Rust beats unsafe Rust by 1007 / 8175 Ir per call*, all of it loop
//! structure and none of it safety. It is the measured control `r4_cursor` and ../NOTES.md 8b
//! publishes both numbers and the span they bound.
//!
//! **What does NOT go away is `op < NOPS`** -- that is not a bounds
//! check in this rung, it is the kernel's semantics (the hardened C cell folds
//! SENT on an out-of-table opcode and ../spec.md pins that answer). A rung
//! without it would be `c/kernel.c`'s bug written in Rust rather than an unsafe
//! rung. R5 (verus.rs) is this exec code with the SAFETY comments below turned
//! into obligations a verifier discharges.
//!
//! ⚠ **THE TABLE IS `[&'static dyn Op; NOPS]`, NOT `[fn(u64) -> u64; NOPS]`,
//! AND THAT IS FORCED BY THE `identity` PIN RATHER THAN CHOSEN.** ../spec.md
//! pins `unsafe == verus`, so an R4 must have an R5 twin that Verus verifies
//! and that erases to the same machine code. At the pinned Verus,
//!
//! ```text
//! error: The verifier does not yet support the following Rust feature:
//!        function pointer types
//! ```
//!
//! on the declaration itself, so C's own mechanism is **not an admissible R4**.
//! This is the sixth instance of the *EVERY RUNG IS A SPELLING* finding (RECAP
//! finding 14; in `.memory/01-ladder.md` that number is p13 and this one is not
//! numbered -- name the finding, never the number) -- the
//! unsafe class is chained to the prover -- and the sharpest, because what the
//! prover cannot reach is not a *spelling* of the kernel but the kernel's
//! central *mechanism*. The `fn`-pointer spelling is measured as the control
//! `r_fnptr`, and the difference is exactly **3.00000 Ir per dispatch** --
//! same intercept, slope 13.00000 against 10.00000 (../NOTES.md 8a).
//!
//! **What the unchecked spelling buys here, precisely: 15.00 Ir per CALL and
//! 0.00000 per record.** The table read loses a bounds check against 8 that is
//! **already dead** under `op < NOPS` -- measured at exactly zero by the control
//! `r2_nodead`, which is R2 with only the table access unchecked and is
//! Ir-identical to R2 on both blobs. The two window reads lose checks LLVM has
//! already hoisted out of R3's loop. ../NOTES.md 4.
//!
//! SAFETY (1): `off + len <= buf.len()` is the caller's structural
//!   precondition. Unchecked here; discharged at the call site by Verus in
//!   verus.rs.
//! SAFETY (2): `len >= 4` guards the window header, so
//!   `off + 3 < off + len <= buf.len()`.
//! SAFETY (3): a record is read only under `len - p >= 2` with `p <= len`, so
//!   `off + p + 1 < off + len <= buf.len()`.
//! SAFETY (4): the table is read only under `op < NOPS`, and `NOPS` is
//!   `TABLE.len()`.

#[path = "../../common/driver.rs"]
mod driver;

/// The table's extent. Must equal `SLB_P36_NOPS` in c/kernel.h and `NOPS` in
/// model.py.
const NOPS: usize = 8;

/// What a rejected opcode folds.
const SENT: u64 = 251;

// ------------------------------------------------------------------- ops ----
pub trait Op {
    fn apply(&self, x: u64) -> u64;
}

/// The eight op types. **ONE `impl` block, eight monomorphisations** --
/// `OpTag<0>` .. `OpTag<7>` are eight distinct types with eight distinct
/// vtables and eight distinct code addresses, so the dispatch below really does
/// have eight targets.
///
/// ⚠ **Eight separate `impl Op for OpN` blocks were written first and the GATE
/// REFUSES THEM**: `harness/vparse.py::duplicate_names` fails any pinned file
/// that defines one name more than once, and eight impls define `apply` eight
/// times (`check.py::check_verus_contract`: *"the gate used to key items by
/// name and keep the last, so a decoy could supply the pinned contract for the
/// real item"*). The const-generic shape is what makes p36 expressible inside
/// the existing gate, with no `harness/` change. ../NOTES.md 9b.
pub struct OpTag<const K: u8>;

impl<const K: u8> Op for OpTag<K> {
    fn apply(&self, x: u64) -> u64 {
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
}

/// THE TABLE.
const TABLE: [&'static dyn Op; NOPS] = [
    &OpTag::<0>,
    &OpTag::<1>,
    &OpTag::<2>,
    &OpTag::<3>,
    &OpTag::<4>,
    &OpTag::<5>,
    &OpTag::<6>,
    &OpTag::<7>,
];

// The unchecked window read. Same accessor every unsafe rung in this project
// ships; in verus.rs it is trusted item 1 of 4.
#[inline(always)]
fn buf_get_unchecked(v: &[u8], i: usize) -> u8 {
    unsafe { *v.get_unchecked(i) }
}

// The unchecked TABLE read. verus.rs's trusted item 2 of 4. It closes over
// `TABLE` rather than taking it as a parameter because `&dyn Op` cannot be a
// `T: Copy` type parameter at the pinned Verus without dragging the `dyn`
// support into a generic position; the concrete signature is what verifies.
#[inline(always)]
fn tab_get_unchecked(i: usize) -> &'static dyn Op {
    unsafe { *TABLE.get_unchecked(i) }
}

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md. Every unchecked access below is discharged in
// ../verus.rs; the exec code there is this code, character for character.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    if len < 4 {
        return 0;
    }
    let nrec: usize = buf_get_unchecked(buf, off) as usize
        + 256 * (buf_get_unchecked(buf, off + 1) as usize)
        + 65536 * (buf_get_unchecked(buf, off + 2) as usize)
        + 16777216 * (buf_get_unchecked(buf, off + 3) as usize);
    if nrec == 0 {
        return 0;
    }
    // The record count is hoisted, exactly as R3 hoists it: record `t` is read
    // iff `t < nrec` and `len - (4 + 2t) >= 2`, i.e. iff
    // `t < min(nrec, (len - 4) / 2)`. Same records, same answer, no
    // per-record cursor test.
    let room: usize = (len - 4) / 2;
    let nw: usize = if nrec < room { nrec } else { room };
    let mut acc: u64 = 0;
    let mut p: usize = 4;
    let mut t: usize = 0;
    while t < nw {
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
    let path = driver::arg_path();
    let inp = driver::load(&path);
    let (stride_w, bytes) = driver::head1_u64_bytes(&inp);
    let n_iters: u64 = inp.n_iters;
    // SLB-DRIVER-BEGIN
    let n_blob: usize = bytes.len();
    let buf: &[u8] = bytes.as_slice();
    let mut acc: u64 = 0;
    if stride_w >= 6 && stride_w <= n_blob as u64 {
        let stride: usize = stride_w as usize;
        let nwin: u64 = (n_blob / stride) as u64;
        let mut it: u64 = 0;
        while it < n_iters {
            let k: usize = ((acc as u128 * nwin as u128) >> 64) as usize;
            let r: u64 = kernel(buf, k * stride, stride);
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    driver::emit(acc);
}
