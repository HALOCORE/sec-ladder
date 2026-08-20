//! p14 rung R4 -- unsafe.
//!
//! R2's algorithm with every bounds check removed: the four window-header
//! bytes, the four bytes of each line header, every byte the scan and the fold
//! read out of `scr`, and every field descriptor written to or read from `tl`
//! go through `get_unchecked` / `get_unchecked_mut`. **What does NOT go away is
//! `if nt == MAXTOK { break; }`** -- that is not a bounds check, it is the
//! kernel's semantics (the hardened cell TRUNCATES at 16 fields and `spec.md`
//! pins that answer), and a rung without it would be R1's bug written in Rust
//! rather than an unsafe rung. This rung is correct; it just has nothing
//! checking that it is. R5 (verus.rs) is this exec code with the SAFETY
//! comments below turned into obligations a verifier discharges.
//!
//! SAFETY (1): `off + len <= buf.len()` is the caller's structural
//!   precondition. Unchecked here; discharged at the call site by Verus in
//!   verus.rs.
//! SAFETY (2): `len >= 4` guards the window header, so
//!   `off + 3 < off + len <= buf.len()`.
//! SAFETY (3): the line header is read only under `len - p >= 4` with
//!   `p <= len`, so `off + p + 3 < off + len <= buf.len()`.
//! SAFETY (4): the scan reads `scr[i]` only under `i < m <= SCR`, because the
//!   `i == m` disjunct short-circuits at the top of the range.
//! SAFETY (5): **the field table is written at `tl[nt]` only under
//!   `nt < MAXTOK`**, because the line immediately above breaks at
//!   `nt == MAXTOK` and `nt` grows by one per store. That is the obligation p14
//!   is about, and it is the one line R1 deletes.
//! SAFETY (6): the fold reads `tl[j]` only under `j < nt <= MAXTOK`, and
//!   `scr[cur + q]` only under `cur + q < m <= SCR` -- `cur` is the start
//!   offset of field `j`, which is `sum(tl[0..j]) + j`, and every recorded
//!   field satisfies `cur + tl[j] <= m`.
//!
//! **(5) is the whole pattern.** R2 pays a bounds check on `tl[nt]`; this rung
//! asserts it in a comment; R5 proves it; and C does none of the three. The
//! three trusted bases for the one fact are tabulated in ../NOTES.md 6.
//!
//! **The copy into the scratch is `copy_from_slice`, the same bulk spelling R2
//! and R3 use and the same one `memcpy` gives the C rungs.** It is left CHECKED
//! on purpose: ../spec.md pins the load identical across all seven rungs so the
//! measured difference is the split, and a `copy_nonoverlapping` here would
//! make R4's load a different program from R2's and R3's -- and, at the pinned
//! vstd, would drag a trusted wrapper back in (`.memory/04-verus.md`). The
//! price is one length check per line on the unsafe side and it is measured
//! rather than waved at (../NOTES.md 3).
//!
//! The cursor guards are subtraction-first for the reason in this pattern's
//! other rungs: `p <= len` is maintained by the guards, the subtraction cannot
//! wrap, and the additive form does not verify.

#[path = "../../common/driver.rs"]
mod driver;

const SCR: usize = 64;
const MAXTOK: usize = 16;
const DELIM: u8 = b',';

// THE BULK LOAD -- see safe_naive.rs. THE RECEIVER is scoped 2-and-2: this rung
// and verus.rs write the three exec lines below, character for character,
// because `..n` is a `RangeTo<usize>` and `RangeTo` has NO `SliceIndexSpecImpl`
// at the pinned vstd, so `dst[..n]` cannot be VERIFIED at all and R4 follows R5
// because the `identity` pin makes them one program. ../NOTES.md 6a.
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
    let nline: usize = unsafe { *buf.get_unchecked(off) } as usize
        + 256 * (unsafe { *buf.get_unchecked(off + 1) } as usize)
        + 65536 * (unsafe { *buf.get_unchecked(off + 2) } as usize)
        + 16777216 * (unsafe { *buf.get_unchecked(off + 3) } as usize);
    if nline == 0 {
        return 0;
    }
    let mut scr: [u8; SCR] = [0; SCR];
    let mut tl: [usize; MAXTOK] = [0; MAXTOK];
    let mut acc: u64 = 0;
    let mut p: usize = 4;
    let mut ln: usize = 0;
    while ln < nline {
        if len - p < 4 {
            break;
        }
        let llen: usize = unsafe { *buf.get_unchecked(off + p) } as usize
            + 256 * (unsafe { *buf.get_unchecked(off + p + 1) } as usize)
            + 65536 * (unsafe { *buf.get_unchecked(off + p + 2) } as usize)
            + 16777216 * (unsafe { *buf.get_unchecked(off + p + 3) } as usize);
        p = p + 4;
        let m: usize = if llen < SCR { llen } else { SCR };
        if len - p < llen {
            break;
        }
        scr_load(&mut scr, buf, off + p, m);
        p = p + llen;
        let mut nt: usize = 0;
        let mut s: usize = 0;
        let mut i: usize = 0;
        while i <= m {
            if i == m || unsafe { *scr.get_unchecked(i) } == DELIM {
                // THE SAFETY LINE. c/kernel.c omits exactly this.
                if nt == MAXTOK {
                    break;
                }
                let flen: usize = i - s;
                unsafe { *tl.get_unchecked_mut(nt) = flen; }
                nt = nt + 1;
                s = i + 1;
            }
            i = i + 1;
        }
        let mut cur: usize = 0;
        let mut j: usize = 0;
        while j < nt {
            let tj: usize = unsafe { *tl.get_unchecked(j) };
            acc = acc.wrapping_mul(31).wrapping_add(tj as u64);
            let mut q: usize = 0;
            while q < tj {
                acc = acc.wrapping_mul(31)
                    .wrapping_add(unsafe { *scr.get_unchecked(cur + q) } as u64);
                q = q + 1;
            }
            cur = cur + tj + 1;
            j = j + 1;
        }
        acc = acc.wrapping_mul(31).wrapping_add(nt as u64);
        ln = ln + 1;
    }
    acc.wrapping_mul(31).wrapping_add(nline as u64)
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
