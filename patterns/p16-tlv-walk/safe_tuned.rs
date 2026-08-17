//! p16 rung R3 -- safe-tuned.
//!
//! Same semantics as R2, written the way an experienced Rust programmer writes
//! a parser: reslice the header once and index the 3-byte slice, then reslice
//! the value and fold it with an iterator, so the value fold carries no bounds
//! check at all -- the reslice is the check, and it is outside the loop by
//! construction rather than by the optimiser's goodwill. Still zero `unsafe`.
//!
//! Note what this rung can and cannot buy back. The *fold* is a bulk operation
//! over a contiguous slice and the iterator hands it to LLVM in the shape it
//! wants. The *walk* is not: `p` is loop-carried through a value read out of the
//! buffer, so there is no reslice that covers the whole walk and no trip count
//! to hoist. Whatever R3 does not recover here is therefore a cost the outer
//! loop is paying, which is the question p16 exists to ask -- see NOTES.md 3.
//!
//! `.memory/01-ladder.md`: never publish a safety-cost claim without this rung.
//! Reporting R2 alone overstated safe Rust's cost by ~3.7x on the pilot.

#[path = "../../common/driver.rs"]
mod driver;

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    let mut p: usize = off;
    let end: usize = off + len;
    let mut acc: u64 = 0;
    let mut nrec: u64 = 0;
    while end - p >= 3 {
        let h: &[u8] = &buf[p..p + 3];
        acc = acc.wrapping_mul(31).wrapping_add(h[0] as u64);
        let vlen: usize = h[1] as usize + 256 * (h[2] as usize);
        if vlen > end - (p + 3) {
            break;
        }
        acc = buf[p + 3..p + 3 + vlen]
            .iter()
            .fold(acc, |a, &x| a.wrapping_mul(31).wrapping_add(x as u64));
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
