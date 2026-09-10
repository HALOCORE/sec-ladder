//! ph29 rung R3 -- safe-tuned. Still zero `unsafe`; three changes from R2, each
//! of which is a RESPELLING and not a different algorithm.
//!
//! 1. ⭐ **THE COPY IS ONE `copy_from_slice` OVER TWO SUBSLICES.** R2 writes
//!    `read_buf[i] = win[HEAD + i]` in a loop, which leaves rustc two bounds
//!    checks per byte. R3 takes `&mut read_buf[..n]` and `&win[HEAD..HEAD + n]`
//!    once and lets `copy_from_slice` do the move -- the same two bounds, hoisted
//!    out of the loop, plus `copy_from_slice`'s own length equality, which is
//!    provable from the two slicings. ⚠ **This is a MOVED check, not a deleted
//!    one**, and the reviewer's question -- *"is R3 actually check-free, or did
//!    it just move the check?"* -- has the honest answer that `n <= cap` is
//!    still tested, once, and no rung may remove it: it is the whole difference
//!    from R1.
//! 2. the fold is an iterator over `&read_buf[..recvd]` rather than an index
//!    walk, so the per-byte bound leaves the loop as well.
//! 3. the eight bytes of `to_read` are decoded with `from_le_bytes` over a
//!    fixed-size array rather than a shift loop.
//!
//! Everything else -- the allocator arithmetic, the transport's clamp, the
//! `recvd >= 0` arm, the tally and the fold's shape -- is byte-for-byte R2.
//! ../spec.md's `identity` records what that buys and what it does not.

#[path = "../../common/driver.rs"]
mod driver;

const HEAD: usize = 12;

#[inline(always)]
fn real_size_of(size: u64) -> u32 {
    (size.wrapping_add(7) & !7u64) as u32
}

#[inline(always)]
fn recorded_size_of(size: u64) -> u32 {
    (size as u32) & 0x7FFF_FFFF
}

#[inline(always)]
fn tally(n_free: u64, real_size: u32) -> u64 {
    (1u64.wrapping_mul(1000003))
        ^ (n_free.wrapping_mul(1000033))
        ^ (0u64.wrapping_mul(1000037))
        ^ ((real_size as u64).wrapping_mul(1000039))
}

#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    let win: &[u8] = &buf[off..off + len];

    let mut head8: [u8; 8] = [0u8; 8];
    head8.copy_from_slice(&win[0..8]);
    let to_read: i64 = i64::from_le_bytes(head8);
    let ctl: u32 = (win[8] as u32) | ((win[9] as u32) << 8);
    let want: u32 = (win[10] as u32) | ((win[11] as u32) << 8);

    let n_pay: usize = len - HEAD;
    let navail: usize = (want as usize) % (n_pay + 1);

    let mut remote_len: usize = 0;
    if ctl & 1 != 0 {
        remote_len = 0;
    }

    let size: u64 = (to_read as u64).wrapping_add(1);
    let real_size: u32 = real_size_of(size);
    let recorded: u32 = recorded_size_of(size);
    let cap: usize = real_size as usize;
    let mut read_buf: Vec<u8> = vec![0u8; cap];

    let recvd: i32;
    if ctl & 2 != 0 {
        recvd = -1;
    } else {
        let buflen: usize = to_read as u64 as usize;
        let mut n: usize = navail;
        if buflen < n {
            n = buflen;
        }
        if n > cap {
            n = cap;
        }
        read_buf[..n].copy_from_slice(&win[HEAD..HEAD + n]);
        if ctl & 1 != 0 {
            remote_len = n % 32;
        }
        recvd = n as i32;
    }

    let mut h: u64 = 0;
    let mut n_free: u64 = 0;
    let mut remote_is_string: u64 = 0;
    if recvd >= 0 {
        if ctl & 1 != 0 && remote_len != 0 {
            remote_is_string = 1;
        }
        if (recvd as usize) < cap {
            read_buf[recvd as usize] = 0;
        }
        for v in read_buf[..recvd as usize].iter() {
            h = h.wrapping_mul(31).wrapping_add(*v as u64);
        }
        n_free = 1;
    }

    let mut acc: u64 = 0;
    acc = acc.wrapping_mul(31).wrapping_add(h);
    acc = acc.wrapping_mul(31).wrapping_add(recvd as u32 as u64);
    acc = acc.wrapping_mul(31).wrapping_add(remote_len as u64);
    acc = acc.wrapping_mul(31).wrapping_add(remote_is_string);
    acc = acc.wrapping_mul(31).wrapping_add(recorded as u64);
    acc = acc.wrapping_mul(31).wrapping_add(tally(n_free, real_size));
    acc
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
    if stride_w >= 16 && stride_w <= n_blob as u64 {
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
