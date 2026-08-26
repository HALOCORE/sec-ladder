//! p23 rung R4 -- unsafe.
//!
//! R2's algorithm with every bounds check removed: the four header bytes, the
//! five bytes of each record header this kernel reads and every byte the two
//! scans and the swap touch go through `get_unchecked` / `get_unchecked_mut`.
//! **What does NOT go away is the `i < j` conjunct on either scan** -- that is
//! not a bounds check, it is the kernel's semantics, and a rung without it
//! would be R1's bug written in Rust rather than an unsafe rung. This rung is
//! correct; it just has nothing checking that it is. R5 (verus.rs) is this exec
//! code with the SAFETY comments below turned into obligations a verifier
//! discharges.
//!
//! SAFETY (1): `off + len <= buf.len()` is the caller's structural
//!   precondition. Unchecked here; discharged at the call site by Verus in
//!   verus.rs.
//! SAFETY (2): `len >= 4` guards the window header, so
//!   `off + 3 < off + len <= buf.len()`.
//! SAFETY (3): the record header is read only under `len - p >= 8` with
//!   `p <= len`, so `off + p + 4 < off + len <= buf.len()`.
//! SAFETY (4): **the two scans read `scr[i]` and `scr[j - 1]` only under
//!   `i < j <= m <= SCR`.** `j` starts at `m = min(nelem, SCR)` and only
//!   decreases; `i` starts at 0 and only increases while `i < j`. So `i < SCR`
//!   and `j - 1 < SCR` at every read, and `j >= 1` so `j - 1` does not wrap.
//!   That is the obligation p23 is about, and it is the pair of conjuncts R1
//!   deletes.
//! SAFETY (5): the swap writes `scr[i]` and `scr[j - 1]` only under `i < j`,
//!   which is the same fact one line later.
//! SAFETY (6): the fold reads `scr[q]` only under `q < m <= SCR`.
//!
//! **(4) is where the whole pattern lives, and it is a bound of a NEW KIND for
//! this tree: each cursor's bound is THE OTHER CURSOR.** Every earlier
//! obligation here bounds an index by something outside the loop -- a header
//! field, a capacity, a live length. `i < j` is a mutual bound between two
//! variables that both move, and the fact that makes it sufficient (`j <= SCR`)
//! is established once, before the loop, and then never re-read. R2 pays a
//! bounds check per scan step; R3 hands the swap's half to `<[T]>::swap`; this
//! rung asserts it in a comment; R5 proves it. ../NOTES.md 6.
//!
//! **The copy into the scratch is `copy_from_slice`, the same bulk spelling R2
//! and R3 use and the same one `memcpy` gives the C rungs.** It is left
//! CHECKED on purpose: ../spec.md pins the load identical across all seven
//! rungs so the measured difference is the partition, and a
//! `copy_nonoverlapping` here would make R4's load a different program from
//! R2's and R3's. The price is one length check per record on the unsafe side
//! and it is measured rather than waved at (../NOTES.md 3).
//!
//! **An R4-side lever that was measured and NOT taken**, declared here rather
//! than hidden: resliced-window addressing -- `buf.split_at(off).1
//! .split_at(len).0` and then `w.get_unchecked(p)` -- is **6.00 probe-`Ir`/call
//! cheaper than this rung at all three probe bands** (../NOTES.md 9; the figure
//! is a PROBE's, `.temp/t101/cost23.rs`, and the transferable part is the SIGN,
//! not the 6.00). It is not shipped because R4 must be byte-identical to R5 and
//! `split_at` on the window has not been shown to verify at the pinned vstd. So
//! p23's R4 endpoint is held fixed BY FIAT and sits above the cheapest R4
//! found, which is what `.memory/01-ladder.md` asks a pattern to say instead of
//! publishing a pair interval.
//!
//! The cursor guards are subtraction-first for the reason in this pattern's
//! other rungs: `p <= len` is maintained by the guards, the subtraction cannot
//! wrap, and the additive form does not verify.

#[path = "../../common/driver.rs"]
mod driver;

const SCR: usize = 64;

// THE BULK LOAD, and the one place all seven rungs are held to the same
// spelling: `memcpy` in C and `.copy_from_slice(&src[from..from + n]);` in all
// four Rust rungs. ../spec.md pins that call, so that the measured difference
// between rungs is the PARTITION and not the load.
//
// ** The RECEIVER is scoped 2-and-2. ** safe_naive.rs and safe_tuned.rs write
// `dst[..n]`; this rung and verus.rs write the three exec lines below,
// character for character, because `..n` is a `RangeTo<usize>` and `RangeTo`
// has NO `SliceIndexSpecImpl` at the pinned vstd -- so `dst[..n]` cannot be
// VERIFIED at all, and R4 follows R5 because the `identity` pin makes them one
// program. p06 measured the price of that receiver at ZERO at -O3.
//
// It is a `#[inline(always)]` free function rather than an inline expression
// because R4 must be byte-identical to R5 and R5's copy is a free function; a
// call boundary changes LLVM's inlining order.
#[inline(always)]
fn scr_load(dst: &mut [u8; SCR], src: &[u8], from: usize, n: usize) {
    let s: &mut [u8] = dst;
    let (a, _b) = s.split_at_mut(n);
    a.copy_from_slice(&src[from..from + n]);
}

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    if len < 4 {
        return 0;
    }
    let nrec: usize = unsafe { *buf.get_unchecked(off) } as usize
        + 256 * (unsafe { *buf.get_unchecked(off + 1) } as usize)
        + 65536 * (unsafe { *buf.get_unchecked(off + 2) } as usize)
        + 16777216 * (unsafe { *buf.get_unchecked(off + 3) } as usize);
    if nrec == 0 {
        return 0;
    }
    let mut scr: [u8; SCR] = [0; SCR];
    let mut acc: u64 = 0;
    let mut p: usize = 4;
    let mut rec: usize = 0;
    while rec < nrec {
        if len - p < 8 {
            break;
        }
        let nelem: usize = unsafe { *buf.get_unchecked(off + p) } as usize
            + 256 * (unsafe { *buf.get_unchecked(off + p + 1) } as usize)
            + 65536 * (unsafe { *buf.get_unchecked(off + p + 2) } as usize)
            + 16777216 * (unsafe { *buf.get_unchecked(off + p + 3) } as usize);
        let pv: u8 = unsafe { *buf.get_unchecked(off + p + 4) };
        p = p + 8;
        let m: usize = if nelem < SCR { nelem } else { SCR };
        if len - p < nelem {
            break;
        }
        scr_load(&mut scr, buf, off + p, m);
        p = p + nelem;
        let mut i: usize = 0;
        let mut j: usize = m;
        while i < j {
            // THE SAFETY LINE, half 1. c/kernel.c omits the `i < j &&`.
            while i < j && unsafe { *scr.get_unchecked(i) } <= pv {
                i = i + 1;
            }
            // THE SAFETY LINE, half 2. c/kernel.c omits the `i < j &&`.
            while i < j && unsafe { *scr.get_unchecked(j - 1) } >= pv {
                j = j - 1;
            }
            if i < j {
                let t: u8 = unsafe { *scr.get_unchecked(i) };
                let u: u8 = unsafe { *scr.get_unchecked(j - 1) };
                unsafe { *scr.get_unchecked_mut(i) = u; }
                unsafe { *scr.get_unchecked_mut(j - 1) = t; }
                i = i + 1;
                j = j - 1;
            }
        }
        let mut q: usize = 0;
        while q < m {
            acc = acc.wrapping_mul(31)
                .wrapping_add(unsafe { *scr.get_unchecked(q) } as u64);
            q = q + 1;
        }
        acc = acc.wrapping_mul(31).wrapping_add(i as u64);
        rec = rec + 1;
    }
    acc.wrapping_mul(31).wrapping_add(nrec as u64)
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
    if stride_w >= 4 && stride_w <= n_blob as u64 {
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
