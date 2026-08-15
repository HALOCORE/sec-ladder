//! p02 rung R3 -- safe-tuned.
//!
//! Same semantics as R2, written the way an experienced Rust programmer writes
//! it: reslice both sides once, `copy_from_slice` (which lowers to `memcpy`),
//! then fold the destination with an iterator. Still zero `unsafe`. The two
//! reslices are the only bounds checks and they are outside the copy by
//! construction rather than by the optimiser's goodwill.
//!
//! `.memory/01-ladder.md`: never publish a safety-cost claim without this rung.
//! Reporting R2 alone overstated safe Rust's cost by ~3.7x on the pilot.

#[path = "../../common/driver.rs"]
mod driver;

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(src: &[u8], src_off: usize, dst: &mut [u8]) -> u64 {
    let len: usize = src[src_off] as usize + 256 * (src[src_off + 1] as usize);
    if len > dst.len() || len > src.len() - (src_off + 2) {
        return 0;
    }
    let d: &mut [u8] = &mut dst[..len];
    d.copy_from_slice(&src[src_off + 2..src_off + 2 + len]);
    d.iter().fold(0u64, |acc, &x| acc.wrapping_add(x as u64))
}

// ---------------------------------------------------------------- driver ----
fn main() {
    let path = driver::arg_path();
    let inp = driver::load(&path);
    let (cap_w, stride_w, bytes) = driver::head2_u64_bytes(&inp);
    let n_iters: u64 = inp.n_iters;
    let mut dbuf: Vec<u8> = driver::zeroed(cap_w);
    // SLB-DRIVER-BEGIN
    let n_src: usize = bytes.len();
    let src: &[u8] = bytes.as_slice();
    let dst: &mut [u8] = dbuf.as_mut_slice();
    let mut acc: u64 = 0;
    if stride_w >= 2 && stride_w <= n_src as u64 {
        let stride: usize = stride_w as usize;
        let nrec: u64 = (n_src / stride) as u64;
        let mut it: u64 = 0;
        while it < n_iters {
            let k: usize = ((acc as u128 * nrec as u128) >> 64) as usize;
            let r: u64 = kernel(src, k * stride, dst);
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    driver::emit(acc);
}
