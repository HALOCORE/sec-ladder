//! ph16 rung R2 -- safe-naive.
//!
//! The mechanical port a working Rust programmer writes first: index the three
//! head words and every entry with `win[..]`, keep each `fd_set` as a
//! `[u64; 16]` on the stack exactly as the C keeps it, index it with
//! `fds[this_fd / 64]`, fold with `while` loops. Zero `unsafe`.
//!
//! ⚠⚠ **READ THIS BEFORE COMPARING THIS RUNG TO R1h.** The four Rust rungs
//! here implement **exactly** what `c/kernel_hardened.c` implements -- PHP
//! 5.0.0's `stream_array_to_fd_set` plus the POSIX branch of `99e290f882c9`
//! (Wez Furlong, 2004-09-17, *"Bug #24189: possibly unsafe select(2) usage"*)
//! -- because that fix is COMPLETE for the memory-safety defect: it removes
//! every out-of-range `FD_SET` and changes no benign answer
//! (`controls/fix_scope.py`). So no rung has to carry a second fix the way
//! ph03's do. The ladder reads:
//!
//!     R1    streamsfuncs.c:518-548 as shipped 5.0.0 -- CRASH-098
//!     R1h   + 99e290f882c9's POSIX branch: THREE guards, one of them in the
//!           caller's frame
//!     R2-5  the same function, in Rust
//!
//! ⚠ **WHY THERE ARE THREE `fd_set`s AND NOT ONE.** They are
//! `PHP_FUNCTION(stream_select)`'s own (`streamsfuncs.c:658`), in upstream's
//! declaration order, and `php_select(max_fd + 1, &rfds, &wfds, &efds, tv_p)`
//! at `:706` reads all three. In the C rungs that is what an over-index lands
//! in -- a *live neighbouring object*, not a redzone -- and it is why this row
//! has an oracle without a `volatile` canary. In THIS rung nothing can land
//! there, which is the point of the rung; the three sets are kept so that the
//! checksum every rung produces is the same function of the same data.
//! `../NOTES.md` §3.
//!
//! ⚠ **THE GUARD IS SPELLED `this_fd < FD_SETSIZE` HERE AND `w < NW` IN R3-R5.**
//! Both are `PHP_SAFE_FD_SET`'s test; `this_fd < 1024` and `this_fd / 64 < 16`
//! are the same predicate on a `u32`, demonstrated exhaustively over all
//! 16 384 reachable values by `controls/guard_equiv.py` with must-fire
//! mutants. This rung uses the C's own spelling and pays a bounds check on
//! `fds[this_fd / 64]` that R3's spelling makes provable -- that difference is
//! this row's R2->R3 gradient and `../NOTES.md` §8 reads it off the
//! disassembly rather than asserting it.
//!
//! **Do not read this rung's number as a bounds-check tax without the
//! decomposition in `../NOTES.md` §8.** A ph16 call does four different things
//! -- decode the split, walk three runs of entries, zero three 128-byte
//! objects and fold 48 words -- and only the walk carries a check R4 removes.

#[path = "../../common/driver.rs"]
mod driver;

// ------------------------------------------------------- shared arithmetic --
// Identical text in all four Rust rungs and re-derived independently in
// model.py. See ../spec.md for why each is what it is.

/// `FD_SETSIZE` on the platform this row is measured on, and the bound
/// `streamsfuncs.c:541` never mentions. `<sys/select.h>`; `c/kernel.c` carries
/// a C99 compile-time assertion that the platform really is this shape.
const FD_SETSIZE: u32 = 1024;

/// `sizeof(fd_set) / sizeof(long)` -- the sixteen 64-bit words glibc's
/// `fd_set` is, and what the C rungs' fold walks.
const NW: usize = 16;

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md. `#[inline(never)]` only in `isolated` builds, so the
// `whole` builds can inline it the way LTO'd C would.

/// `stream_array_to_fd_set` -- ext/standard/streamsfuncs.c:518-548, narrowed.
///
/// Returns `sets`, which `stream_select` sums: 0 when the zval was not an
/// array, 1 otherwise.
#[inline(always)]
fn to_fd_set(win: &[u8], base: usize, n: usize, not_an_array: bool,
             fds: &mut [u64; NW], max_fd: &mut u32) -> u64 {
    if not_an_array {
        return 0;                       // Z_TYPE_P(stream_array) != IS_ARRAY
    }
    let mut i: usize = 0;
    while i < n {
        let j: usize = 6 + 2 * (base + i);
        let e: u32 = (win[j] as u32) | ((win[j + 1] as u32) << 8);
        if e >> 14 != 0 {               // php_stream_from_zval_no_verify != NULL
            if e >> 14 != 1 {           // SUCCESS == php_stream_cast(...)
                let this_fd: u32 = e & 0x3FFF;
                // 99e290f882c9 guard (b): PHP_SAFE_FD_SET's POSIX branch.
                // Guard (a), `&& this_fd >= 0`, is DEAD here -- `this_fd` is a
                // 14-bit field -- and ../spec.md says so rather than banking it.
                if this_fd < FD_SETSIZE {
                    fds[(this_fd / 64) as usize] |= 1u64 << (this_fd % 64);
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

/// One `fd_set`, folded at its own word granularity -- the stand-in for
/// `php_select(max_fd + 1, &rfds, &wfds, &efds, tv_p)` consuming it.
#[inline(always)]
fn fold_set(s: &[u64; NW]) -> u64 {
    let mut h: u64 = 0;
    let mut i: usize = 0;
    while i < NW {
        h = h.wrapping_mul(31).wrapping_add(s[i]);
        i = i + 1;
    }
    h
}

#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    let win: &[u8] = &buf[off..off + len];

    let ctl: u32 = (win[0] as u32) | ((win[1] as u32) << 8);
    let split_r: u32 = (win[2] as u32) | ((win[3] as u32) << 8);
    let split_w: u32 = (win[4] as u32) | ((win[5] as u32) << 8);

    // How the window's entries divide between the three stream arrays. Derived
    // so that it is TOTAL by construction: the kernel never trusts a length out
    // of the blob, exactly as PHP never gets one -- a zend_hash knows its own
    // count.
    let m: usize = (len - 6) / 2;
    let n_r: usize = (split_r as usize) % (m + 1);
    let rem: usize = m - n_r;
    let n_w: usize = (split_w as usize) % (rem + 1);
    let n_e: usize = rem - n_w;

    // streamsfuncs.c:658-666 -- the frame, and FD_ZERO on each.
    let mut rfds: [u64; NW] = [0u64; NW];
    let mut wfds: [u64; NW] = [0u64; NW];
    let mut efds: [u64; NW] = [0u64; NW];
    let mut max_fd: u32 = 0;
    let mut sets: u64 = 0;

    // streamsfuncs.c:670-672
    if ctl & 1 == 0 {
        sets += to_fd_set(win, 0, n_r, ctl & 8 != 0, &mut rfds, &mut max_fd);
    }
    if ctl & 2 == 0 {
        sets += to_fd_set(win, n_r, n_w, ctl & 16 != 0, &mut wfds, &mut max_fd);
    }
    if ctl & 4 == 0 {
        sets += to_fd_set(win, n_r + n_w, n_e, ctl & 32 != 0, &mut efds, &mut max_fd);
    }

    // 99e290f882c9 guard (c): PHP_SAFE_MAX_FD's POSIX branch, in the CALLER.
    // ⚠ It is NOT about the write -- `*max_fd = this_fd` sits inside the arm
    // guard (b) protects but is not itself bounded by it, so without this
    // `php_select` would still be handed an `nfds` past FD_SETSIZE.
    if max_fd >= FD_SETSIZE {
        max_fd = FD_SETSIZE - 1;
    }

    // streamsfuncs.c:674-677
    if sets == 0 {
        return 0xFFFF_FFFFu64;                       // RETURN_FALSE
    }

    // streamsfuncs.c:706, :718
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
