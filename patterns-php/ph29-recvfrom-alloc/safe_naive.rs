//! ph29 rung R2 -- safe Rust, naive. A direct transcription of
//! `PHP_FUNCTION(stream_socket_recvfrom)` (ext/standard/streamsfuncs.c:300-345)
//! with no `unsafe`, written the way somebody porting the C would write it:
//! index by index, bound by bound, no iterator adaptors and no subslicing.
//!
//! ============================================================================
//! ⚠⚠⚠ WHAT R2-R5 ARE, AND WHY THEY ARE NOT PORTS OF R1h
//! ============================================================================
//! `.memory-php/02-ladder.md`: *"the hardened C rung carries the historical
//! fix, the Rust rungs carry whatever is actually memory-safe."* Here that
//! distinction is unusually sharp, because **R1h's guard does not remove this
//! row's defect** (`../c/kernel_hardened.c`, `../controls/fix_scope.py`): it
//! refuses `to_read <= 0` and lets `to_read = 4294967295` through to the same
//! truncated allocation. A Rust rung built to the 2004 fix would still write
//! out of bounds, so there would be nothing memory-safe about it.
//!
//! ⭐ **WHAT THE RUST RUNGS DO INSTEAD, AND IT IS ONE LINE.** Every rung --
//! C and Rust alike -- computes PHP's own allocator arithmetic explicitly:
//!
//!     size      = to_read + 1                      streamsfuncs.c:321
//!     real_size = (size + 7) & ~7, stored in 32 bits    zend_alloc.c:129/:135
//!     recorded  = size, stored in 31 bits               zend_alloc.h:53
//!
//! `real_size` is **the number of bytes the block actually has**. That is not a
//! modelling choice: it is what `_emalloc` returns (`zend_alloc.c:182`
//! allocates `header + padding + real_size`). R1 then hands
//! `php_stream_xport_recvfrom` the number it ASKED for -- `to_read` -- and the
//! gap between the two is the whole defect. In Rust a buffer's length is its
//! length, so the copy is bounded by `read_buf.len()` and there is no gap.
//!
//! ⚠ **THE ALTERNATIVE READING, STATED SO A READER CAN DISAGREE.** One could
//! argue the safe port of `emalloc(to_read + 1)` is `vec![0u8; to_read + 1]`,
//! since Rust's allocator has no 32-bit truncation -- and then safe Rust simply
//! does not have the bug. That is true and it is unmeasurable: it allocates
//! 4 GiB per kernel call on the row's own trigger. Modelling the truncation in
//! every rung is what makes R1..R5 differ in exactly ONE thing. ../NOTES.md §6.
//!
//! ⚠ `vec![0u8; cap]` ZEROES; `emalloc` does not. That is a real cost the four
//! Rust rungs all pay and the two C rungs do not, it is the same spelling ph03
//! and ph07 ship, and ../NOTES.md §8 prices it rather than hiding it.

#[path = "../../common/driver.rs"]
mod driver;

/// The window's head, in bytes.
const HEAD: usize = 12;

/// `Zend/zend_alloc.c:132` -- and the rounding is done in 64 bits.
#[inline(always)]
fn real_size_of(size: u64) -> u32 {
    // `zend_alloc.c:129` declares `unsigned int real_size` and `:135` assigns
    // `REAL_SIZE(size)` into it. THE STORE is truncation T1.
    (size.wrapping_add(7) & !7u64) as u32
}

/// `Zend/zend_alloc.h:53` -- `unsigned int size:31`, truncation T2, a
/// DIFFERENT modulus from T1 and the only size the block itself records.
#[inline(always)]
fn recorded_size_of(size: u64) -> u32 {
    (size as u32) & 0x7FFF_FFFF
}

/// `php_shim_tally()` -- `common-php/emalloc_shim.h`. After
/// `php_shim_reset()` the cache is empty, so one request means
/// `n_alloc == 1`, `n_cache_hit == 0` and `bytes_mallocked == real_size`;
/// `n_free` is 1 exactly when the zval destructor ran.
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

    // streamsfuncs.c:309 -- zend_parse_parameters(..., "rl|lz", ...).
    let mut tr: u64 = 0;
    let mut b: usize = 0;
    while b < 8 {
        tr |= (win[b] as u64) << (8 * b);
        b += 1;
    }
    let to_read: i64 = tr as i64;
    let ctl: u32 = (win[8] as u32) | ((win[9] as u32) << 8);
    let want: u32 = (win[10] as u32) | ((win[11] as u32) << 8);

    let n_pay: usize = len - HEAD;
    let navail: usize = (want as usize) % (n_pay + 1);

    // streamsfuncs.c:315-319
    let mut remote_len: usize = 0;
    if ctl & 1 != 0 {
        remote_len = 0;
    }

    // streamsfuncs.c:321 -- emalloc(to_read + 1), and what it really returns.
    let size: u64 = (to_read as u64).wrapping_add(1);
    let real_size: u32 = real_size_of(size);
    let recorded: u32 = recorded_size_of(size);
    let cap: usize = real_size as usize;
    let mut read_buf: Vec<u8> = vec![0u8; cap];

    // streamsfuncs.c:323 -- php_stream_xport_recvfrom -> php_stream_read.
    let recvd: i32;
    if ctl & 2 != 0 {
        recvd = -1;
    } else {
        let buflen: usize = to_read as u64 as usize;   // (size_t)to_read
        let mut n: usize = navail;
        if buflen < n {
            n = buflen;                                // transports.c:406-407
        }
        // ⭐ THE ONE LINE R1 DOES NOT HAVE. C copies `n` bytes into a block of
        // `real_size`; nothing tells it the two differ. Here the buffer knows.
        if n > cap {
            n = cap;
        }
        let mut i: usize = 0;
        while i < n {
            read_buf[i] = win[HEAD + i];
            i += 1;
        }
        if ctl & 1 != 0 {
            remote_len = n % 32;            // transports.c:438-441
        }
        recvd = n as i32;
    }

    let mut h: u64 = 0;
    let mut n_free: u64 = 0;
    let mut remote_is_string: u64 = 0;
    if recvd >= 0 {
        // streamsfuncs.c:329-330
        if ctl & 1 != 0 && remote_len != 0 {
            remote_is_string = 1;
        }
        // streamsfuncs.c:332 -- read_buf[recvd] = '\0'
        if (recvd as usize) < cap {
            read_buf[recvd as usize] = 0;
        }
        // streamsfuncs.c:340 -- RETURN_STRINGL(read_buf, recvd, 0)
        let mut i: usize = 0;
        while i < recvd as usize {
            h = h.wrapping_mul(31).wrapping_add(read_buf[i] as u64);
            i += 1;
        }
        n_free = 1;                                    // the zval's destructor
    }
    // else streamsfuncs.c:344 RETURN_FALSE -- 5.0.0 leaks read_buf and PHP's
    // request shutdown reclaims it, which is why `n_free` stays 0.

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
