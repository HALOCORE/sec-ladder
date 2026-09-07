//! ph03 rung R3 -- safe-tuned.
//!
//! Same semantics as R2, written the way an experienced Rust programmer writes
//! a codec: **reslice once per group, then index the reslice**. The 4-byte
//! source group and the 3-byte destination group each become a slice whose
//! bounds check happens once, so the seven source loads and three destination
//! stores inside the group carry none; and the final plaintext fold becomes an
//! iterator over `dest[..total_len]`, whose bound is likewise checked once.
//! Still zero `unsafe`.
//!
//! ⚠ **What R3 can and cannot buy back on this row, stated before the numbers**
//! (`.memory/01-ladder.md`: never publish a safety-cost claim without this
//! rung; reporting R2 alone overstated safe Rust's cost by ~3.7x on the pilot).
//!
//!   * the *group* is a bulk shape and reslicing hands it to LLVM whole -- this
//!     is where R3 should recover;
//!   * the *walk* is not. `s` advances by a value read out of the data
//!     (`line_len(dec(buf[s]))`), so no reslice covers the outer loop and there
//!     is no trip count to hoist. Whatever R3 does not recover is the outer
//!     loop's;
//!   * and the *allocation* is neither. `vec![0u8; cap]` is one `alloc` +
//!     `memset` per call in every Rust rung, R4 included, so it cancels out of
//!     every Rust-vs-Rust comparison and does NOT cancel out of the C one --
//!     C's `emalloc` does not zero. NOTES.md §8 decomposes it.
//!
//! The algorithm is `php_uudecode` + BOTH upstream fixes; see safe_naive.rs's
//! header for why the 2014 one is not optional here.

#[path = "../../common/driver.rs"]
mod driver;

// ------------------------------------------------------- shared arithmetic --
// Byte-identical to safe_naive.rs; see that file for the citations.

#[inline(always)]
fn dec(b: u8) -> u8 {
    b.wrapping_sub(0x20) & 0o77
}

#[inline(always)]
fn line_len(ln: usize) -> usize {
    if ln == 45 { 60 } else { (ln * 133) / 100 }
}

#[inline(always)]
fn capacity(src_len: usize) -> usize {
    src_len - src_len / 4 + 1
}

#[inline(always)]
fn tally(cap: usize) -> u64 {
    let real_size: u64 = ((cap + 7) & !7) as u64;
    1000003u64 ^ 1000033u64 ^ real_size.wrapping_mul(1000039)
}

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    let src_len: usize = len;
    let e: usize = off + len;
    let cap: usize = capacity(src_len);
    let mut dest: Vec<u8> = vec![0u8; cap];
    let mut p: usize = 0;
    let mut total_len: usize = 0;
    let mut s: usize = off;
    let mut err: bool = false;
    while s < e {
        let ln: usize = dec(buf[s]) as usize;
        s = s + 1;
        if ln == 0 {
            break;
        }
        if ln > src_len {
            err = true;
            break;
        }
        let fl: usize = line_len(ln);
        if fl > e - s {
            err = true;
            break;
        }
        let ee: usize = s + fl;
        while s < ee {
            if e - s < 4 {
                err = true;
                break;
            }
            let q: &[u8] = &buf[s..s + 4];
            let d: &mut [u8] = &mut dest[p..p + 3];
            d[0] = dec(q[0]) << 2 | dec(q[1]) >> 4;
            d[1] = dec(q[1]) << 4 | dec(q[2]) >> 2;
            d[2] = dec(q[2]) << 6 | dec(q[3]);
            p = p + 3;
            s = s + 4;
        }
        if err {
            break;
        }
        total_len = total_len + ln;
        if ln < 45 {
            break;
        }
        if s >= e {
            break;
        }
        s = s + 1;
    }
    let mut acc: u64 = 0;
    if err {
        acc = 0xFFFF_FFFF;
    } else {
        acc = dest[..total_len]
            .iter()
            .fold(acc, |a, &x| a.wrapping_mul(31).wrapping_add(x as u64));
        acc = acc.wrapping_mul(31).wrapping_add(total_len as u64);
    }
    acc ^ tally(cap)
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
    if stride_w >= 1 && stride_w <= n_blob as u64 {
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
