//! p47 rung R2 -- safe-naive.
//!
//! **THE SAFE LANGUAGE'S DEFAULT IS THE LEAKING ONE, and this rung is the
//! measurement of it.** `a == b` on two `&[u8]` is what every Rust programmer
//! writes to compare two byte strings. It is memory-safe, it is
//! borrow-checked, it panics on nothing, and it is exactly as insecure as
//! `c/kernel.c`: `<[u8] as PartialEq>::eq` lowers to a **`bcmp`** call --
//! `R_X86_64_GLOB_DAT bcmp` on the shipped binary -- and glibc's `bcmp` stops
//! at the first differing 32-byte block.
//!
//! ⚠ **THE ROUTINE IS THE SAME ONE `c-clang` CALLS.** clang -O3 rewrites
//! `memcmp(a,b,n) == 0` to `bcmp`, so the C rung and this rung enter the
//! identical glibc IFUNC. Any `Ir` difference between them is therefore a
//! difference in what the *caller* does around the call and not a language
//! difference at all (`.memory/03-measurement.md`, "name the routine"; p11 and
//! p13 are the two patterns that learned this the hard way). ../NOTES.md 4
//! separates the two.
//!
//! **What is naive here is the SLICING, not the comparison.** This rung
//! reslices the window with `&buf[a..b]` twice per comparison -- four bounds
//! checks and their panic pads -- where R3 does the same and R4 does neither.
//! That is the safety axis. The timing axis is orthogonal to it and runs the
//! other way: **this rung is FASTER than R3 and R4 on every mismatching
//! input**, because it stops early. Speed and security point in opposite
//! directions on p47 and the two columns have to be read together.
//!
//! **Bounds checks and panics.** `&buf[off + p .. off + p + tlen]` panics if
//! the range is out of bounds or inverted. The guard
//! `len - p >= 2 * tlen` plus the kernel's structural precondition
//! `off + len <= buf.len()` make both unreachable, exactly as R5 proves -- but
//! rustc does not know that and the checks stay. ../NOTES.md 6 counts the pads.

#[path = "../../common/driver.rs"]
mod driver;

const MATCH: u64 = 7;
const MISS: u64 = 251;

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    if len < 8 {
        return 0;
    }
    let ntag: usize = buf[off] as usize + 256 * (buf[off + 1] as usize)
        + 65536 * (buf[off + 2] as usize) + 16777216 * (buf[off + 3] as usize);
    let tlen: usize = buf[off + 4] as usize + 256 * (buf[off + 5] as usize)
        + 65536 * (buf[off + 6] as usize) + 16777216 * (buf[off + 7] as usize);
    if ntag == 0 || tlen == 0 {
        return 0;
    }
    let mut acc: u64 = 0;
    let mut p: usize = 8;
    let mut o: usize = 0;
    while o < ntag && len - p >= 2 * tlen {
        // THE TIMING LINE. This is the idiomatic safe-Rust comparison and it
        // is the LEAKING one: `==` on slices is `bcmp`.
        let a: &[u8] = &buf[off + p..off + p + tlen];
        let b: &[u8] = &buf[off + p + tlen..off + p + 2 * tlen];
        acc = if a == b {
            acc.wrapping_mul(31).wrapping_add(MATCH)
        } else {
            acc.wrapping_mul(31).wrapping_add(MISS)
        };
        p = p + 2 * tlen;
        o = o + 1;
    }
    acc.wrapping_mul(31).wrapping_add(o as u64)
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
    if stride_w >= 8 && stride_w <= n_blob as u64 {
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
