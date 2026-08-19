//! p07 rung R2 -- safe-naive.
//!
//! The mechanical port a working Rust programmer writes first: index `buf[..]`
//! for the header, for every query key and for every element the search probes,
//! with the flattened byte index spelled `off + 8 + 4 * mid` exactly as the C
//! spells it. Zero `unsafe`.
//!
//! **This is the first rung in this project whose measured loop is neither a
//! linear fold nor vectorisable**, and that is what p07 exists to measure.
//! p01/p02/p05/p08/p16/p17 all fold every byte of their window, so a
//! per-call safety constant divided by `n` bytes goes to zero and "safety is
//! cheap" comes out by construction. Binary search does `ceil(log2 n)` probes
//! per query and touches `4*ceil(log2 n)` bytes of an `4*n`-byte array, so a
//! per-probe check is a *fraction* of the kernel and cannot be amortised by
//! making the input bigger. See NOTES.md 3.
//!
//! Four bounds checks per probe here (one per byte of the little-endian u32),
//! against R3's one and R4's none. NOTES.md 3 decomposes it -- one loop at a
//! time, per `.memory/01-ladder.md` finding 4's rule, never by reading two
//! disassemblies.

#[path = "../../common/driver.rs"]
mod driver;

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md. `#[inline(never)]` only in `isolated` builds, so the
// `whole` builds can inline it the way LTO'd C would.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    if len < 8 {
        return 0;
    }
    let n: usize = buf[off] as usize + 256 * (buf[off + 1] as usize)
        + 65536 * (buf[off + 2] as usize) + 16777216 * (buf[off + 3] as usize);
    let nq: usize = buf[off + 4] as usize + 256 * (buf[off + 5] as usize)
        + 65536 * (buf[off + 6] as usize) + 16777216 * (buf[off + 7] as usize);
    if n == 0 || nq == 0 {
        return 0;
    }
    let avail: usize = len - 8;
    if 4 * (n as u64) + 4 * (nq as u64) > avail as u64 {
        return 0;
    }
    let mut acc: u64 = 0;
    for q in 0..nq {
        let kp: usize = off + 8 + 4 * n + 4 * q;
        let key: u32 = buf[kp] as u32 + 256 * (buf[kp + 1] as u32)
            + 65536 * (buf[kp + 2] as u32) + 16777216 * (buf[kp + 3] as u32);
        let mut lo: usize = 0;
        let mut hi: usize = n;
        let mut found: u64 = 0xffff_ffff_ffff_ffff;
        while lo < hi {
            let mid: usize = lo + (hi - lo) / 2;
            let ep: usize = off + 8 + 4 * mid;
            let v: u32 = buf[ep] as u32 + 256 * (buf[ep + 1] as u32)
                + 65536 * (buf[ep + 2] as u32) + 16777216 * (buf[ep + 3] as u32);
            if v == key {
                found = mid as u64;
                break;
            }
            if v < key {
                lo = mid + 1;
            } else {
                hi = mid;
            }
        }
        acc = acc.wrapping_mul(31).wrapping_add(found.wrapping_add(1));
    }
    acc.wrapping_mul(31).wrapping_add((n as u64).wrapping_mul(nq as u64))
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
