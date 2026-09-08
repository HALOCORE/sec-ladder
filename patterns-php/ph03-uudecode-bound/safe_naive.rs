//! ph03 rung R2 -- safe-naive.
//!
//! The mechanical port a working Rust programmer writes first: index the length
//! byte and the four characters of each group with `buf[..]`, write the three
//! plaintext bytes with `dest[..]`, fold with a `for` loop. Zero `unsafe`.
//!
//! ⚠⚠ **READ THIS BEFORE COMPARING THIS RUNG TO R1h. IT IS NOT THE SAME
//! ALGORITHM, AND THAT IS THE ROW'S HEADLINE.**
//!
//! `c/kernel_hardened.c` is the real 2004 upstream fix, `f95c1df58349`, and
//! **that fix is incomplete**: `if (ee > e)` bounds where the inner loop
//! *tests*, while the body reads `*(s+3)`, so it still overshoots by up to
//! three bytes. PHP closed that in 2014 with `1e2818b14376` --
//! `if (s + 4 > e) goto err;` inside the loop. Every Rust rung here carries
//! **both** checks, because with only the 2004 pair this rung would panic on an
//! input R1h merely mis-decodes, and a rung that panics is not a translation of
//! the C, it is a crash with better manners. Measured: 144 of 12 600 documents
//! still read past the source end with the 2004 fix alone
//! (`.temp/php13/02-reach.log` Q3, NOTES.md §5).
//!
//! So the ladder for this row reads:
//!
//!     R1   no checks                      -- CRASH-115, both limbs
//!     R1h  + f95c1df58349 (2004)          -- the write closed, a read left
//!     R2-5 + 1e2818b14376 (2014) as well  -- memory-safe
//!
//! Every input this row ships trips a 2004 check first, so R1h and R2-R5 agree
//! on all seven and only R1 diverges; `model.py::selfcheck` asserts that, so the
//! agreement is checked rather than assumed.
//!
//! **Do not read this rung's number as a bounds-check tax without the
//! decomposition in NOTES.md §8.** ph03's kernel does four different things per
//! call -- allocate, decode, fold, free -- and only two of them carry a check
//! that R4 removes.

#[path = "../../common/driver.rs"]
mod driver;

// ------------------------------------------------------- shared arithmetic --
// Identical text in all four Rust rungs and re-derived independently in
// model.py. See ../spec.md for why each is what it is.

/// `PHP_UU_DEC` -- ext/standard/uuencode.c:66. C evaluates `((c) - ' ') & 077`
/// on a signed `char`; the mask makes the sign irrelevant, so a `u8` with
/// `wrapping_sub` is the same function.
#[inline(always)]
fn dec(b: u8) -> u8 {
    b.wrapping_sub(0x20) & 0o77
}

/// `ee - s` at uuencode.c:141: `len == 45 ? 60 : (int) floor(len * 1.33)`.
///
/// ⚠ **THE C IS FLOATING POINT AND STAYS THAT WAY** (c/kernel.c keeps
/// `(int) floor(len * 1.33)`); this is the exact integer form, and the
/// substitution is licensed by an exhaustive check over the whole reachable
/// domain -- `dec` masks with `077`, so `ln` is 0..63 -- with a must-fire
/// control, `.temp/php13/02-reach.log` Q1, re-run per gate by
/// `model.py::selfcheck`. It is a *substitution*, not a tidy-up: Verus has no
/// `f64` arithmetic at all, so the float cannot reach R5 (NOTES.md §9), and
/// spelling it three ways across the ladder would be worse than spelling it
/// once with the equivalence measured.
#[inline(always)]
fn line_len(ln: usize) -> usize {
    if ln == 45 { 60 } else { (ln * 133) / 100 }
}

/// `emalloc(ceil(src_len * 0.75) + 1)` at uuencode.c:131. `0.75` is exact in
/// binary64 and `src_len` is an `int`, so `ceil(3n/4)` is exactly `n - n/4` in
/// integer arithmetic -- an identity, checked over 0..10^5 in
/// `model.py::selfcheck` and preferred over `(3n + 3) / 4` for one reason:
/// `3 * src_len` OVERFLOWS `usize` for a large window and `n - n/4` cannot,
/// which turns an unprovable side condition in R5 into no side condition at
/// all. Same value on every input, including every one this row ships.
#[inline(always)]
fn capacity(src_len: usize) -> usize {
    src_len - src_len / 4 + 1
}

/// `php_shim_tally()` after the one `reset` + `emalloc` + `efree` a kernel call
/// makes. ⚠ The Rust rungs do not link `common-php/emalloc_shim.h`; this
/// reproduces the value ARITHMETICALLY so that the allocation SIZE is pinned
/// across every rung by the checksum the gate compares. It is not evidence that
/// any Rust rung ran PHP's allocator. ../spec.md and NOTES.md §7.
#[inline(always)]
fn tally(cap: usize) -> u64 {
    let real_size: u64 = ((cap + 7) & !7) as u64;
    1000003u64 ^ 1000033u64 ^ real_size.wrapping_mul(1000039)
}

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md. `#[inline(never)]` only in `isolated` builds, so the
// `whole` builds can inline it the way LTO'd C would.
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
            dest[p] = dec(buf[s]) << 2 | dec(buf[s + 1]) >> 4;
            dest[p + 1] = dec(buf[s + 1]) << 4 | dec(buf[s + 2]) >> 2;
            dest[p + 2] = dec(buf[s + 2]) << 6 | dec(buf[s + 3]);
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
        let mut i: usize = 0;
        while i < total_len {
            acc = acc.wrapping_mul(31).wrapping_add(dest[i] as u64);
            i = i + 1;
        }
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
