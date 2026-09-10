//! ph16 rung R3 -- safe-tuned. Still zero `unsafe`; three changes from R2, each
//! of which is a RESPELLING and not a different algorithm.
//!
//! 1. ⭐ **THE GUARD IS SPELLED IN THE WORD INDEX.** R2 writes the C's own
//!    `if this_fd < FD_SETSIZE { fds[(this_fd / 64) as usize] |= … }`, which
//!    leaves rustc a second, redundant bounds check on `fds[..]` -- the
//!    compiler is not told that `this_fd < 1024` implies `this_fd / 64 < 16`.
//!    R3 writes `let w = (this_fd / 64) as usize; if w < NW { fds[w] |= … }`,
//!    which is **the same predicate** on a `u32` and makes the index provably
//!    in range at the point of use. `controls/guard_equiv.py` demonstrates the
//!    equivalence exhaustively over all 16 384 reachable `this_fd` values,
//!    against a build of the C itself, with must-fire mutants.
//!    ⚠ This is a MOVED check, not a deleted one, and `../NOTES.md` §8 says so:
//!    the reviewer's question is *"is R3 actually check-free, or did it just
//!    move the check?"* and here the honest answer is that one of two checks
//!    became zero and the other is `PHP_SAFE_FD_SET` itself, which no rung may
//!    remove.
//! 2. the entry run is taken as a SUBSLICE once and walked with
//!    `chunks_exact(2)`, so the per-entry index computation and its bounds
//!    check leave the loop.
//! 3. the 16-word fold is an iterator rather than an index walk.
//!
//! Everything else -- the split arithmetic, the three `fd_set`s, `max_fd`,
//! `sets`, the `RETURN_FALSE` arm and the fold's shape -- is byte-for-byte R2.
//! ../spec.md's `identity` records what that buys and what it does not.

#[path = "../../common/driver.rs"]
mod driver;

// ------------------------------------------------------- shared arithmetic --
const FD_SETSIZE: u32 = 1024;
const NW: usize = 16;

// ---------------------------------------------------------------- kernel ----

/// `stream_array_to_fd_set` -- ext/standard/streamsfuncs.c:518-548, narrowed.
#[inline(always)]
fn to_fd_set(run: &[u8], not_an_array: bool,
             fds: &mut [u64; NW], max_fd: &mut u32) -> u64 {
    if not_an_array {
        return 0;                       // Z_TYPE_P(stream_array) != IS_ARRAY
    }
    for c in run.chunks_exact(2) {
        let e: u32 = (c[0] as u32) | ((c[1] as u32) << 8);
        if e >> 14 != 0 {               // php_stream_from_zval_no_verify != NULL
            if e >> 14 != 1 {           // SUCCESS == php_stream_cast(...)
                let this_fd: u32 = e & 0x3FFF;
                // 99e290f882c9 guard (b), in the word index. See the module
                // comment: `w < NW` and `this_fd < FD_SETSIZE` are one
                // predicate, and only this spelling lets the index be proved.
                let w: usize = (this_fd / 64) as usize;
                if w < NW {
                    fds[w] |= 1u64 << (this_fd % 64);
                }
                if this_fd > *max_fd {
                    *max_fd = this_fd;
                }
            }
        }
    }
    1
}

#[inline(always)]
fn fold_set(s: &[u64; NW]) -> u64 {
    let mut h: u64 = 0;
    for v in s.iter() {
        h = h.wrapping_mul(31).wrapping_add(*v);
    }
    h
}

#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    let win: &[u8] = &buf[off..off + len];

    let ctl: u32 = (win[0] as u32) | ((win[1] as u32) << 8);
    let split_r: u32 = (win[2] as u32) | ((win[3] as u32) << 8);
    let split_w: u32 = (win[4] as u32) | ((win[5] as u32) << 8);

    let m: usize = (len - 6) / 2;
    let n_r: usize = (split_r as usize) % (m + 1);
    let rem: usize = m - n_r;
    let n_w: usize = (split_w as usize) % (rem + 1);
    let n_e: usize = rem - n_w;
    let ents: &[u8] = &win[6..6 + 2 * m];

    let mut rfds: [u64; NW] = [0u64; NW];
    let mut wfds: [u64; NW] = [0u64; NW];
    let mut efds: [u64; NW] = [0u64; NW];
    let mut max_fd: u32 = 0;
    let mut sets: u64 = 0;

    if ctl & 1 == 0 {
        sets += to_fd_set(&ents[0..2 * n_r], ctl & 8 != 0, &mut rfds, &mut max_fd);
    }
    if ctl & 2 == 0 {
        sets += to_fd_set(&ents[2 * n_r..2 * (n_r + n_w)], ctl & 16 != 0,
                          &mut wfds, &mut max_fd);
    }
    if ctl & 4 == 0 {
        sets += to_fd_set(&ents[2 * (n_r + n_w)..2 * (n_r + n_w + n_e)],
                          ctl & 32 != 0, &mut efds, &mut max_fd);
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
