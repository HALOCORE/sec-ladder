//! p02 rung R4 -- unsafe.
//!
//! R3's algorithm with every bounds check removed: the prefix is read with
//! `get_unchecked`, the copy is a raw `copy_nonoverlapping`, and the fold
//! indexes the destination unchecked. The one thing that survives is the
//! *rejection test* -- this rung is correct, it just has nothing checking that
//! it is. R5 (verus.rs) is this exec code with the three SAFETY comments below
//! turned into obligations a verifier discharges.
//!
//! Note what the check has to be sufficient *for*: after `len` is accepted, the
//! copy writes `dst[0..len]` and reads `src[src_off+2 .. src_off+2+len]`, and
//! nothing re-examines either bound. Delete the `if` and this file is C.

#[path = "../../common/driver.rs"]
mod driver;

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md.
//
// SAFETY (1): `src_off + 2 <= src.len()` is the caller's structural
//   precondition, so the two prefix reads are in bounds. Unchecked here;
//   discharged at the call site by Verus in verus.rs.
// SAFETY (2): the `if` rejects every `len` for which the copy would leave
//   `dst[0..len]` or `src[src_off+2 .. src_off+2+len]`. The subtraction cannot
//   underflow, again by the structural precondition.
// SAFETY (3): `src` and `dst` are distinct allocations -- `&[u8]` and
//   `&mut [u8]` cannot alias -- so `copy_nonoverlapping` is the right call.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(src: &[u8], src_off: usize, dst: &mut [u8]) -> u64 {
    let len: usize = unsafe { *src.get_unchecked(src_off) } as usize
        + 256 * (unsafe { *src.get_unchecked(src_off + 1) } as usize);
    if len > dst.len() || len > src.len() - (src_off + 2) {
        return 0;
    }
    unsafe {
        core::ptr::copy_nonoverlapping(src.as_ptr().add(src_off + 2), dst.as_mut_ptr(), len);
    }
    let mut acc: u64 = 0;
    for i in 0..len {
        acc = acc.wrapping_add(unsafe { *dst.get_unchecked(i) } as u64);
    }
    acc
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
