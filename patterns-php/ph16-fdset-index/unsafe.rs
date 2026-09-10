//! ph16 rung R4 -- unsafe.
//!
//! `get_unchecked` on the window, `get_unchecked`/`get_unchecked_mut` on the
//! three `fd_set`s, in every place R3 indexes. Nothing else changes -- same
//! split arithmetic, same three arrays, same guards, same fold.
//!
//! ⚠⚠ **THE PRECONDITION EVERY ONE OF THEM RESTS ON IS `99e290f882c9` GUARD
//! (b)**, `PHP_SAFE_FD_SET`'s POSIX branch, spelled here in the word index:
//! `let w = (this_fd / 64) as usize; if w < NW { … }`. Without it
//! `aset_unchecked(fds, w, …)` has no precondition -- which is exactly
//! `c/kernel.c:541`, and exactly the defect. **verus.rs proves that
//! implication**, and `controls/negatives.py --emit noguard` runs the mutant
//! with the line removed and it must FAIL to verify.
//!
//! ⭐ The window reads need a DIFFERENT precondition and it comes from
//! somewhere else entirely: `off + len <= buf.len()` at the call site, plus
//! `m = (len - 6) / 2`, which is why the entry index can never leave the
//! window however hostile the split words are. The two unchecked classes in
//! this rung are licensed by two independent facts, one from a 2004 security
//! patch and one from the driver's own contract, and `../NOTES.md` §10 keeps
//! them apart.
//!
//! ⚠ R4 and R5 must produce the same machine code; see `../NOTES.md` §10 and
//! ../spec.md's `identity`. The only differences are R5's `verus!` block, its
//! spec/proof items and the `requires`/`ensures` on these wrappers.

#[path = "../../common/driver.rs"]
mod driver;

// ------------------------------------------------------- shared arithmetic --
const FD_SETSIZE: u32 = 1024;
const NW: usize = 16;

// ------------------------------------------------------- unchecked access ---
// The three operations verus.rs makes TRUSTED. Same names, same signatures,
// same bodies; there they carry a `requires`/`ensures` pair and here they carry
// this comment.

/// `v[i]` with no bounds check. Sound iff `i < v.len()`.
#[inline(always)]
fn get_unchecked(v: &[u8], i: usize) -> u8 {
    unsafe { *v.get_unchecked(i) }
}

/// `a[i]` with no bounds check. Sound iff `i < NW`.
#[inline(always)]
fn aget_unchecked(a: &[u64; NW], i: usize) -> u64 {
    unsafe { *a.get_unchecked(i) }
}

/// `a[i] = x` with no bounds check. Sound iff `i < NW`.
#[inline(always)]
fn aset_unchecked(a: &mut [u64; NW], i: usize, x: u64) {
    unsafe { *a.get_unchecked_mut(i) = x };
}

// ---------------------------------------------------------------- kernel ----

/// `stream_array_to_fd_set` -- ext/standard/streamsfuncs.c:518-548, narrowed.
#[inline(always)]
fn to_fd_set(win: &[u8], base: usize, n: usize, not_an_array: bool,
             fds: &mut [u64; NW], max_fd: &mut u32) -> u64 {
    if not_an_array {
        return 0;                       // Z_TYPE_P(stream_array) != IS_ARRAY
    }
    let mut i: usize = 0;
    while i < n {
        let j: usize = 6 + 2 * (base + i);
        let e: u32 = (get_unchecked(win, j) as u32)
                   | ((get_unchecked(win, j + 1) as u32) << 8);
        if e >> 14 != 0 {               // php_stream_from_zval_no_verify != NULL
            if e >> 14 != 1 {           // SUCCESS == php_stream_cast(...)
                let this_fd: u32 = e & 0x3FFF;
                let w: usize = (this_fd / 64) as usize;
                if w < NW {             // 99e290f882c9 guard (b)
                    aset_unchecked(fds, w,
                                   aget_unchecked(fds, w) | (1u64 << (this_fd % 64)));
                }
                if this_fd > *max_fd {
                    *max_fd = this_fd;
                }
            }
        }
        i = i + 1;
    }
    1
}

#[inline(always)]
fn fold_set(s: &[u64; NW]) -> u64 {
    let mut h: u64 = 0;
    let mut i: usize = 0;
    while i < NW {
        h = h.wrapping_mul(31).wrapping_add(aget_unchecked(s, i));
        i = i + 1;
    }
    h
}

#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    let win: &[u8] = &buf[off..off + len];

    let ctl: u32 = (get_unchecked(win, 0) as u32)
                 | ((get_unchecked(win, 1) as u32) << 8);
    let split_r: u32 = (get_unchecked(win, 2) as u32)
                     | ((get_unchecked(win, 3) as u32) << 8);
    let split_w: u32 = (get_unchecked(win, 4) as u32)
                     | ((get_unchecked(win, 5) as u32) << 8);

    let m: usize = (len - 6) / 2;
    let n_r: usize = (split_r as usize) % (m + 1);
    let rem: usize = m - n_r;
    let n_w: usize = (split_w as usize) % (rem + 1);
    let n_e: usize = rem - n_w;

    let mut rfds: [u64; NW] = [0u64; NW];
    let mut wfds: [u64; NW] = [0u64; NW];
    let mut efds: [u64; NW] = [0u64; NW];
    let mut max_fd: u32 = 0;
    let mut sets: u64 = 0;

    if ctl & 1 == 0 {
        sets = sets + to_fd_set(win, 0, n_r, ctl & 8 != 0, &mut rfds, &mut max_fd);
    }
    if ctl & 2 == 0 {
        sets = sets + to_fd_set(win, n_r, n_w, ctl & 16 != 0, &mut wfds, &mut max_fd);
    }
    if ctl & 4 == 0 {
        sets = sets + to_fd_set(win, n_r + n_w, n_e, ctl & 32 != 0, &mut efds, &mut max_fd);
    }

    if max_fd >= FD_SETSIZE {
        max_fd = FD_SETSIZE - 1;                     // PHP_SAFE_MAX_FD
    }
    if sets == 0 {
        return 0xFFFF_FFFFu64;                       // RETURN_FALSE
    }

    let mut acc: u64 = 0;
    acc = acc.wrapping_mul(31).wrapping_add(sets);
    acc = acc.wrapping_mul(31).wrapping_add(max_fd as u64);
    acc = acc.wrapping_mul(31).wrapping_add(fold_set(&rfds));
    acc = acc.wrapping_mul(31).wrapping_add(fold_set(&wfds));
    acc = acc.wrapping_mul(31).wrapping_add(fold_set(&efds));
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
