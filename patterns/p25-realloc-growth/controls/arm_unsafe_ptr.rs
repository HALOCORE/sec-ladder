//! p25 CONTROL -- **THE R4 THAT DOES HOLD THE INTERIOR POINTER. THE MUST-FIRE
//! ARM FOR MIRI, AND THE ARM `../spec.md`'s `identity` PIN EXCLUDES.**
//!
//! `../unsafe.rs` saves an INDEX, and `../unsafe.rs`'s header says why: R4 and
//! R5 are pinned to the same machine code, R5 has to verify, and **Verus cannot
//! license `*cur`** -- the read needs a `PointsTo` permission that no vstd API
//! yields for a `Vec`'s buffer, and `curbase == toks.as_ptr()` is an ADDRESS
//! comparison while Verus's pointers carry PROVENANCE.
//!
//! ⚠⚠ **A CLAIM OF THE FORM "THE UNSAFE RUNG CANNOT EXPRESS THIS" IS A CLAIM
//! ABOUT THE PROOF RUNG, NOT ABOUT RUST, AND THIS FILE IS THE DIFFERENCE.**
//! Unsafe Rust expresses `c/kernel.c`'s bug perfectly well: take
//! `toks.as_ptr().add(curi)`, keep pushing, and dereference. This file is
//! `../unsafe.rs` with exactly that substitution and nothing else, so what
//! `../spec.md` says is *"the identity pin excludes it"* rather than *"Rust
//! cannot say it"* -- and `rust_bug.py` MEASURES the consequence under Miri
//! instead of asserting it.
//!
//! Expected: `Undefined Behavior` from Miri on an adversarial input, and
//! NOTHING from Miri on the shipped `../unsafe.rs` on the same input. Both rows
//! are in `../NOTES.md` 7.
//!
//! ⚠ It is NOT a rung: it is not in `harness/build.py`'s cell tables, it is
//! never measured, and it exists to be run by `rust_bug.py`.

#[path = "../../../common/driver.rs"]
mod driver;

const MAXCAP: usize = 64;
const SENT: u64 = 251;

#[inline(always)]
fn buf_get_unchecked(v: &[u8], i: usize) -> u8 {
    unsafe { *v.get_unchecked(i) }
}

// ---------------------------------------------------------------- kernel ----
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
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
    let mut toks: Vec<u8> = Vec::new();
    let mut strs: Vec<u8> = Vec::new();
    // THE SUBSTITUTION: a raw INTERIOR POINTER where ../unsafe.rs keeps `curi`.
    let mut cur: *const u8 = core::ptr::null();
    let mut acc: u64 = 0;
    let mut p: usize = 4;
    let mut o: usize = 0;
    while o < nops {
        if len - p < 2 {
            break;
        }
        let c: u8 = buf_get_unchecked(buf, off + p);
        let a: u8 = buf_get_unchecked(buf, off + p + 1);
        p = p + 2;
        if c % 4 == 0 {
            if toks.len() < MAXCAP {
                // The growth that retires the block `cur` points into.
                toks.push(a);
                acc = acc.wrapping_mul(31).wrapping_add(a as u64);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else if c % 4 == 1 {
            if strs.len() < MAXCAP {
                strs.push(a);
                acc = acc.wrapping_mul(31).wrapping_add(a as u64);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else if c % 4 == 2 {
            if toks.len() > 0 {
                let curi = (a as usize) % toks.len();
                cur = unsafe { toks.as_ptr().add(curi) };
                acc = acc.wrapping_mul(31).wrapping_add(2);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else {
            if !cur.is_null() {
                // c/kernel.c's READ, in Rust. THIS is what Miri must report.
                let v: u8 = unsafe { *cur };
                acc = acc.wrapping_mul(31).wrapping_add(v as u64);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        }
        o = o + 1;
    }
    acc.wrapping_mul(31).wrapping_add((toks.len() + strs.len()) as u64)
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
    if stride_w >= 4 && stride_w <= n_blob as u64 {
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
