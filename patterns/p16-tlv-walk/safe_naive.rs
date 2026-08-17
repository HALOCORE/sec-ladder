//! p16 rung R2 -- safe-naive.
//!
//! The mechanical port a working Rust programmer writes first: index the tag
//! and the two length bytes with `buf[..]`, reject a value that does not fit,
//! then fold the value a byte at a time with `for j in 0..vlen`. Zero `unsafe`.
//!
//! The two-part test is the *same* test R1h, R3, R4 and R5 write. Safe Rust
//! does not make it unnecessary; it makes omitting it a panic instead of an
//! out-of-bounds read that keeps walking. That difference is the pattern.
//!
//! **Do not read this rung's number as a bounds-check tax without the
//! decomposition in NOTES.md 3.** That mistake was made on p02 and retracted:
//! its whole delta turned out to be a lost `memcpy` idiom, not a check. p16 was
//! built precisely because it removes the escape route -- there is no bulk-
//! memory idiom for a walk whose trip count comes from the data -- but "there is
//! no memcpy to lose" is an argument, and the table in NOTES.md 3 is the
//! measurement. One loop at a time.

#[path = "../../common/driver.rs"]
mod driver;

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md. `#[inline(never)]` only in `isolated` builds, so the
// `whole` builds can inline it the way LTO'd C would.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    let mut p: usize = off;
    let end: usize = off + len;
    let mut acc: u64 = 0;
    let mut nrec: u64 = 0;
    while end - p >= 3 {
        acc = acc.wrapping_mul(31).wrapping_add(buf[p] as u64);
        let vlen: usize = buf[p + 1] as usize + 256 * (buf[p + 2] as usize);
        if vlen > end - (p + 3) {
            break;
        }
        for j in 0..vlen {
            acc = acc.wrapping_mul(31).wrapping_add(buf[p + 3 + j] as u64);
        }
        p = p + 3 + vlen;
        nrec = nrec.wrapping_add(1);
    }
    acc.wrapping_mul(31).wrapping_add(nrec)
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
    if stride_w >= 3 && stride_w <= n_blob as u64 {
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
