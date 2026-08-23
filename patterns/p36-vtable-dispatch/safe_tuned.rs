//! p36 rung R3 -- safe Rust, tuned. Same algorithm, same trait-object table,
//! same answer on every input; what changes is the ordinary safety column.
//!
//! Two levers, both named in `.memory/01-ladder.md`'s R3 definition, both zero
//! `unsafe` and zero trusted items:
//!
//!   * **the record count is hoisted**: `nw = min(nrec, (len - 4) / 2)` is
//!     computed once, so the per-record `len - p < 2` cursor test is gone from
//!     the loop entirely. It is exactly the same set of records -- record `t`
//!     is read iff `t < nrec` and `len - (4 + 2t) >= 2`, i.e. iff
//!     `t < min(nrec, (len - 4) / 2)`;
//!   * **the window is resliced once** (`&buf[off + 4..off + 4 + 2 * nw]`), so
//!     each opcode and operand is indexed against a 2·nw-byte slice instead of
//!     against the whole blob.
//!
//! **THE SAFETY LINE AND THE DISPATCH ARE CHARACTER-IDENTICAL TO R2's**, which
//! is deliberate: p36's cost story is about the indirect call, and pinning the
//! dispatch spelling across all four Rust rungs is what keeps the R2/R3/R4
//! comparison about bounds checking rather than about dispatch.
//!
//! The table is a `const` of `&'static dyn Op` for the reason safe_naive.rs
//! gives at length: at the pinned Verus a bare `fn`-pointer table is
//! `error: ... does not yet support ... function pointer types`, so it has no
//! verifying twin and is not an admissible rung.

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
    // The hoisted record count: the same records the per-record cursor test
    // would have admitted, computed once.
    let room: usize = (len - 4) / 2;
    let nw: usize = if nrec < room { nrec } else { room };
    let rec: &[u8] = &buf[off + 4..off + 4 + 2 * nw];
    let mut acc: u64 = 0;
    let mut t: usize = 0;
    while t < nw {
        let op: usize = rec[2 * t] as usize;
        let arg: u64 = rec[2 * t + 1] as u64;
        // THE SAFETY LINE, character-identical to R2's.
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
