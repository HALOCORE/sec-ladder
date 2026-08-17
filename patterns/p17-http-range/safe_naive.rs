//! p17 rung R2 -- safe-naive.
//!
//! The mechanical port a working Rust programmer writes first: index `buf[..]`
//! for the header and for every served byte, compute the range in `i64` exactly
//! as the C does, and fold with `for j in 0..n`. Zero `unsafe`.
//!
//! The two-part test is the *same* test R1h, R3, R4 and R5 write, and the
//! `start >= 0` conjunct is the same conjunct. **Safe Rust does not make it
//! unnecessary, and on this pattern it does not even make omitting it safe.**
//! Delete it and:
//!
//!   * on `adversarial-oob.bin` (`s > len`) this rung panics, because
//!     `(base + j) as usize` on a negative value is a huge index -- the C reads
//!     six bytes before the allocation and this rung refuses to. That is the
//!     usual win;
//!   * on `adversarial-leak.bin` (`content_len < s <= len`) this rung
//!     **prints C's wrong answer**, silently, with no panic and no diagnostic,
//!     because the index is 0 and 0 is a perfectly good index into the buffer.
//!
//! The second bullet is measured in NOTES.md 1a, with the actual stdout beside
//! C's, and it is the first *limit* of memory safety this project has recorded
//! rather than a cost. Bounds checking cannot see a read that is in bounds.
//!
//! **Do not read this rung's number as a bounds-check tax without the
//! decomposition in NOTES.md 3.** That mistake was made on p02 and retracted,
//! and it was nearly made again on p16. One loop at a time.

#[path = "../../common/driver.rs"]
mod driver;

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md. `#[inline(never)]` only in `isolated` builds, so the
// `whole` builds can inline it the way LTO'd C would.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    if len < 2 {
        return 0;
    }
    let nsuf: usize = buf[off] as usize + 256 * (buf[off + 1] as usize);
    if 2 + 2 * nsuf > len {
        return 0;
    }
    let body_start: usize = 2 + 2 * nsuf;
    let content_len: i64 = (len - body_start) as i64;
    let mut acc: u64 = 0;
    let mut nserved: u64 = 0;
    for i in 0..nsuf {
        let s: i64 = buf[off + 2 + 2 * i] as i64 + 256 * (buf[off + 3 + 2 * i] as i64);
        let start: i64 = content_len - s;
        let end: i64 = content_len;
        if start < end && start >= 0 {
            let base: i64 = (off + body_start) as i64 + start;
            let n: i64 = end - start;
            for j in 0..n {
                acc = acc.wrapping_mul(31).wrapping_add(buf[(base + j) as usize] as u64);
            }
            nserved = nserved.wrapping_add(1);
        }
    }
    acc.wrapping_mul(31).wrapping_add(nserved)
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
    if stride_w >= 2 && stride_w <= n_blob as u64 && n_blob as u64 <= 9223372036854775807 {
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
