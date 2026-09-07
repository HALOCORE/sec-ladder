//! ph03 rung R4 -- unsafe.
//!
//! R2's algorithm with every bounds check on the SOURCE and the DESTINATION
//! removed: the length byte, the four characters of each group, the three
//! destination stores and every byte of the final fold are reached with
//! `get_unchecked` / `get_unchecked_mut`. What survives is the three *runtime
//! tests* -- this rung is correct, it just has nothing checking that it is.
//! R5 (verus.rs) is this exec code with the SAFETY comments below turned into
//! obligations a verifier discharges.
//!
//! The allocation is NOT removed: `vec![0u8; cap]` still runs, because `cap` is
//! `php_uudecode`'s own `emalloc(ceil(src_len*0.75)+1)` and dropping it would
//! be a different program. So R2-vs-R4 on this row prices *checks*, not
//! *allocation*; NOTES.md §8 separates the two.
//!
//! What the three tests have to be sufficient for, because on this row it is a
//! chain and not a single load:
//!
//! SAFETY (1): `off + len <= buf.len()` is the caller's structural
//!   precondition, so `e = off + len <= buf.len()`. Unchecked here; discharged
//!   at the call site by Verus in verus.rs.
//! SAFETY (2): the outer loop's own condition `s < e` puts the length-byte read
//!   `buf[s]` in bounds. That test is the one `c/kernel.c` KEEPS.
//! SAFETY (3): `if s + 4 > e { err }` -- `1e2818b14376`, 2014 -- is what puts
//!   `buf[s+1]`, `buf[s+2]` and `buf[s+3]` in bounds. ⚠ **`if ee > e`, the 2004
//!   fix that `c/kernel_hardened.c` carries, is NOT sufficient for this**: it
//!   bounds where the loop *tests* and the body reads three bytes further, so
//!   with only the 2004 pair this rung would read `buf[s+3]` past the end on
//!   144 of 12 600 documents (`.temp/php13/02-reach.log` Q3). That is the row's
//!   headline and it is why R4 cannot be a port of R1h.
//! SAFETY (4): the destination stores. `dest` has `cap = src_len - src_len/4 + 1`
//!   bytes -- `ceil(3*src_len/4) + 1`, uuencode.c:131 -- and the invariant that
//!   bounds `p` is
//!
//!       4 * (p - 0) <= 3 * (s - off)
//!
//!   -- every group advances `s` by 4 and `p` by 3, and every line spends one
//!   further source byte on the length prefix, so `p` can never overtake three
//!   quarters of the source consumed. With (3)'s `s + 4 <= e` that gives
//!   `4*(p+3) <= 3*(s+4) < 4*cap`, i.e. all three stores are in bounds. R5
//!   carries exactly this as a loop invariant.
//! SAFETY (5): the final fold reads `dest[0 .. total_len)`. `total_len` is a sum
//!   of DECLARED line lengths, so it is bounded by `p` only because every line
//!   emits `3*ceil(line_len(ln)/4) >= ln` bytes -- an arithmetic fact about
//!   `line_len`, exhaustive over `ln` in 0..63 and NOT derivable from the loop
//!   shape. R5 proves it with `lemma_emit_covers_declared`; it is the one
//!   obligation on this row that needed a bounded case analysis rather than an
//!   invariant.

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
        let ln: usize = dec(unsafe { *buf.get_unchecked(s) }) as usize;
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
            let b0: u8 = unsafe { *buf.get_unchecked(s) };
            let b1: u8 = unsafe { *buf.get_unchecked(s + 1) };
            let b2: u8 = unsafe { *buf.get_unchecked(s + 2) };
            let b3: u8 = unsafe { *buf.get_unchecked(s + 3) };
            unsafe { *dest.get_unchecked_mut(p) = dec(b0) << 2 | dec(b1) >> 4 };
            unsafe { *dest.get_unchecked_mut(p + 1) = dec(b1) << 4 | dec(b2) >> 2 };
            unsafe { *dest.get_unchecked_mut(p + 2) = dec(b2) << 6 | dec(b3) };
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
            acc = acc
                .wrapping_mul(31)
                .wrapping_add(unsafe { *dest.get_unchecked(i) } as u64);
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
