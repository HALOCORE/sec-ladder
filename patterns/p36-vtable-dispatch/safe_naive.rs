//! p36 rung R2 -- safe Rust, naive.
//!
//! The same bytecode interpreter, dispatching through a table of **trait
//! objects** rather than a table of bare function pointers.
//!
//! ⚠⚠ **WHY THE TABLE IS `[&'static dyn Op; NOPS]` AND NOT
//! `[fn(u64) -> u64; NOPS]`, WHICH IS WHAT C WRITES.** This is the one place
//! where a p36 rung does not spell the C mechanism, and it is forced, measured,
//! and itself a result:
//!
//! ```text
//! $ ./verus_run.py probe.rs
//! error: The verifier does not yet support the following Rust feature:
//!        function pointer types
//!   --> probe.rs:20:1
//! 20 | const TABLE: [fn(u64) -> u64; 2] = [op_inc, op_dbl];
//! ```
//!
//! ../spec.md pins `identity: unsafe == verus`, so an R4 is not a program that
//! *may* use `unsafe` -- it is a program that must have an R5 twin Verus
//! verifies and that erases to the same machine code (`.memory/01-ladder.md`
//! finding 14). A bare `fn`-pointer table has no such twin at the pinned Verus, so it
//! is **not an admissible rung**, and the four Rust rungs use the closest thing
//! that is: a single-trait object, which is a real vtable dispatch and a real
//! computed-target indirect call. **The `fn`-pointer spelling ships as the
//! measured control `r_fnptr`** with the Verus error text beside it, so what
//! the prover costs here is a number and not an adjective: **3.00000 Ir per
//! dispatch, exactly** (../NOTES.md 8a).
//!
//! ⚠ **And `static` is impossible too, for two reasons that stack**: rustc
//! demands `dyn Op + Sync` for a `static`, and Verus then reports
//! `does not yet support ... dyn with more that one trait`. The table is a
//! `const` in all four Rust rungs; C's is a `static`.
//!
//! The naive spelling: every window read is a bounds-checked index against the
//! whole blob, and the table access is a bounds-checked index too -- which is
//! **dead**, because `op < NOPS` has already been tested one line above. R3
//! reslices the window; R4 spells both accesses unchecked. That difference is
//! p36's safety column and it is an ordinary one.

#[path = "../../common/driver.rs"]
mod driver;

/// The table's extent. Must equal `SLB_P36_NOPS` in c/kernel.h and `NOPS` in
/// model.py.
const NOPS: usize = 8;

/// What a rejected opcode folds.
const SENT: u64 = 251;

// ------------------------------------------------------------------- ops ----
// One 64-bit constant and one of `^`, `+`, `-` each. Identical, constant for
// constant, to c/kernel.c's op0..op7 and to model.py's OPS.
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

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    if len < 4 {
        return 0;
    }
    let nrec: usize = buf[off] as usize + 256 * (buf[off + 1] as usize)
        + 65536 * (buf[off + 2] as usize) + 16777216 * (buf[off + 3] as usize);
    if nrec == 0 {
        return 0;
    }
    let mut acc: u64 = 0;
    let mut p: usize = 4;
    let mut t: usize = 0;
    while t < nrec {
        if len - p < 2 {
            break;
        }
        let op: usize = buf[off + p] as usize;
        let arg: u64 = buf[off + p + 1] as u64;
        p = p + 2;
        // THE SAFETY LINE. c/kernel.c omits exactly this test and dispatches
        // unconditionally; every other rung writes it by hand.
        if op < NOPS {
            acc = TABLE[op].apply(acc ^ arg);
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
