//! ph29 rung R4 -- unsafe.
//!
//! `get_unchecked` on the window, `vget_unchecked` / `vset_unchecked` on the
//! destination and `vcopy_unchecked` for the receive, in every place R3 indexes
//! or slices. Nothing else changes -- same allocator arithmetic, same transport
//! clamp, same arms, same fold.
//!
//! ⚠⚠ **THE PRECONDITION EVERY DESTINATION ACCESS RESTS ON IS THE ONE LINE R1
//! DOES NOT HAVE**: `if n > cap { n = cap; }`, where `cap` is `real_size` --
//! what `_emalloc` actually returned (`Zend/zend_alloc.c:182`). Without it
//! `vcopy_unchecked(&mut read_buf, …, n)` has no precondition, which is exactly
//! `streamsfuncs.c:323` under a truncating allocator, and exactly the defect.
//! **verus.rs proves that implication**, and
//! `controls/negatives.py --emit noclamp` runs the mutant with that line
//! removed and it must FAIL to verify.
//!
//! ⭐ The WINDOW reads need a different precondition and it comes from
//! somewhere else entirely: `off + len <= buf.len()` and `16 <= len` at the
//! call site, plus `navail = want % (n_pay + 1)`. The two unchecked classes in
//! this rung are licensed by two independent facts -- one about PHP's allocator
//! and one about the driver's own contract -- and `../NOTES.md` §10 keeps them
//! apart.
//!
//! ⚠ R4 and R5 must produce the same machine code; see `../NOTES.md` §10 and
//! ../spec.md's `identity`. The only differences are R5's `verus!` block, its
//! spec/proof items and the `requires`/`ensures` on these wrappers -- so the
//! exec text below is character-for-character `verus.rs`'s.

#[path = "../../common/driver.rs"]
mod driver;

const HEAD: usize = 12;

// ------------------------------------------------------- unchecked access ---
// The four operations verus.rs makes TRUSTED. Same names, same signatures,
// same bodies; there they carry a `requires`/`ensures` pair and here they carry
// this comment.

/// `v[i]` with no bounds check. Sound iff `i < v.len()`.
#[inline(always)]
fn get_unchecked(v: &[u8], i: usize) -> u8 {
    unsafe { *v.get_unchecked(i) }
}

/// `v[i]` on the destination, no bounds check. Sound iff `i < v.len()`.
#[inline(always)]
fn vget_unchecked(v: &Vec<u8>, i: usize) -> u8 {
    unsafe { *v.get_unchecked(i) }
}

/// `v[i] = x` on the destination, no bounds check. Sound iff `i < v.len()`.
#[inline(always)]
fn vset_unchecked(v: &mut Vec<u8>, i: usize, x: u8) {
    unsafe { *v.get_unchecked_mut(i) = x };
}

/// The receive. Sound iff `n <= v.len()` and `from + n <= s.len()`; the first
/// of those is the precondition PHP 5.0.0 does not have.
#[inline(always)]
fn vcopy_unchecked(v: &mut Vec<u8>, s: &[u8], from: usize, n: usize) {
    unsafe {
        core::ptr::copy_nonoverlapping(s.as_ptr().add(from), v.as_mut_ptr(), n);
    }
}

#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    let win: &[u8] = &buf[off..off + len];

    // streamsfuncs.c:309 -- zend_parse_parameters(..., "rl|lz", ...).
    let tr: u64 = (get_unchecked(win, 0) as u64) | ((get_unchecked(win, 1) as u64) << 8)
        | ((get_unchecked(win, 2) as u64) << 16) | ((get_unchecked(win, 3) as u64) << 24)
        | ((get_unchecked(win, 4) as u64) << 32) | ((get_unchecked(win, 5) as u64) << 40)
        | ((get_unchecked(win, 6) as u64) << 48) | ((get_unchecked(win, 7) as u64) << 56);
    let ctl: u32 = (get_unchecked(win, 8) as u32) | ((get_unchecked(win, 9) as u32) << 8);
    let want: u32 = (get_unchecked(win, 10) as u32) | ((get_unchecked(win, 11) as u32) << 8);

    let n_pay: usize = len - HEAD;
    let navail: usize = (want as usize) % (n_pay + 1);

    // streamsfuncs.c:315-319
    let mut remote_len: usize = 0;
    if ctl & 1 != 0 {
        remote_len = 0;
    }

    // streamsfuncs.c:321 -- emalloc(to_read + 1), and what it really returns.
    let size: u64 = tr.wrapping_add(1);
    let real_size: u32 = ((size.wrapping_add(7)) & !(7u64)) as u32;
    let recorded: u32 = (size as u32) & 0x7FFF_FFFF;
    let cap: usize = real_size as usize;
    let mut read_buf: Vec<u8> = vec![0u8; cap];

    // streamsfuncs.c:323 -- php_stream_xport_recvfrom -> php_stream_read.
    let recvd: usize;
    let failed: bool = ctl & 2 != 0;
    if failed {
        recvd = 0;
    } else {
        // transports.c:390-392 -- php_stream_read(stream, buf, buflen), and
        // `buflen` is the `size_t` widening of `to_read`. The comparison is
        // done in 64 bits because that is the width PHP does it in.
        let mut n64: u64 = navail as u64;
        if tr < n64 {
            n64 = tr;                                  // transports.c:406-407
        }
        let mut n: usize = n64 as usize;
        // ⭐ THE ONE LINE R1 DOES NOT HAVE.
        if n > cap {
            n = cap;
        }
        vcopy_unchecked(&mut read_buf, win, HEAD, n);
        if ctl & 1 != 0 {
            remote_len = n % 32;                       // transports.c:438-441
        }
        recvd = n;
    }

    let mut h: u64 = 0;
    let mut n_free: u64 = 0;
    let mut remote_is_string: u64 = 0;
    if !failed {
        // streamsfuncs.c:329-330
        if ctl & 1 != 0 && remote_len != 0 {
            remote_is_string = 1;
        }
        // streamsfuncs.c:332 -- read_buf[recvd] = '\0'
        if recvd < cap {
            vset_unchecked(&mut read_buf, recvd, 0);
        }
        // streamsfuncs.c:340 -- RETURN_STRINGL(read_buf, recvd, 0)
        let mut i: usize = 0;
        while i < recvd {
            h = h.wrapping_mul(31).wrapping_add(vget_unchecked(&read_buf, i) as u64);
            i = i + 1;
        }
        n_free = 1;                                    // the zval's destructor
    }
    // else streamsfuncs.c:344 RETURN_FALSE -- 5.0.0 leaks read_buf and PHP's
    // request shutdown reclaims it, which is why `n_free` stays 0.

    let mut acc: u64 = 0;
    acc = acc.wrapping_mul(31).wrapping_add(h);
    acc = acc.wrapping_mul(31).wrapping_add(
        if failed {
            0xFFFF_FFFFu64
        } else {
            recvd as u64
        },
    );
    acc = acc.wrapping_mul(31).wrapping_add(remote_len as u64);
    acc = acc.wrapping_mul(31).wrapping_add(remote_is_string);
    acc = acc.wrapping_mul(31).wrapping_add(recorded as u64);
    acc = acc.wrapping_mul(31).wrapping_add(
        ((1u64).wrapping_mul(1000003)) ^ (n_free.wrapping_mul(1000033))
            ^ ((0u64).wrapping_mul(1000037)) ^ ((real_size as u64).wrapping_mul(1000039)),
    );
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
