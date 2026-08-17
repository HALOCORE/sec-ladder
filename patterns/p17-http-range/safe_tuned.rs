//! p17 rung R3 -- safe-tuned.
//!
//! Same semantics as R2, written the way an experienced Rust programmer writes
//! a range server: reslice the header once and index the small slice, then
//! reslice the served range and fold it with an iterator, so the fold carries
//! no per-byte bounds check at all -- the reslice is the check, and it is
//! outside the loop by construction rather than by the optimiser's goodwill.
//! Still zero `unsafe`.
//!
//! Note the one place the signedness has to be dealt with, because it is the
//! sub-question p17 asks that p16 could not. `&buf[a..b]` needs `usize`
//! endpoints, so the reslice has to convert `base` and `n` back from `i64`.
//! That conversion is *sound* precisely because of the `start >= 0` conjunct --
//! the same conjunct the C rung omits -- and it is free at run time
//! (`as usize` truncates; it emits no check). NOTES.md 3 measures whether the
//! signed/unsigned round trip costs anything in the safe rungs specifically.
//!
//! `.memory/01-ladder.md`: never publish a safety-cost claim without this rung.
//! Reporting R2 alone overstated safe Rust's cost by ~3.7x on the pilot, and
//! p16's first write-up broke the same rule on the next pattern.

#[path = "../../common/driver.rs"]
mod driver;

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    if len < 2 {
        return 0;
    }
    let hdr: &[u8] = &buf[off..off + 2];
    let nsuf: usize = hdr[0] as usize + 256 * (hdr[1] as usize);
    if 2 + 2 * nsuf > len {
        return 0;
    }
    let body_start: usize = 2 + 2 * nsuf;
    let content_len: i64 = (len - body_start) as i64;
    let mut acc: u64 = 0;
    let mut nserved: u64 = 0;
    let tab: &[u8] = &buf[off + 2..off + body_start];
    for i in 0..nsuf {
        let e: &[u8] = &tab[2 * i..2 * i + 2];
        let s: i64 = e[0] as i64 + 256 * (e[1] as i64);
        let start: i64 = content_len - s;
        let end: i64 = content_len;
        if start < end && start >= 0 {
            let base: usize = off + body_start + start as usize;
            let n: usize = (end - start) as usize;
            acc = buf[base..base + n]
                .iter()
                .fold(acc, |a, &x| a.wrapping_mul(31).wrapping_add(x as u64));
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
