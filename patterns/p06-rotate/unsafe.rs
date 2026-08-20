//! p06 rung R4 -- unsafe.
//!
//! R2's algorithm with every bounds check removed: the four header bytes, the
//! eight bytes of each record header and every byte the three reverses read or
//! write go through `get_unchecked` / `get_unchecked_mut`. **What does NOT go
//! away is `if m != 0 { r = r % m } else { r = 0 }`** -- that is not a bounds
//! check, it is the kernel's semantics, and a rung without it would be R1's bug
//! written in Rust rather than an unsafe rung. This rung is correct; it just
//! has nothing checking that it is. R5 (verus.rs) is this exec code with the
//! SAFETY comments below turned into obligations a verifier discharges.
//!
//! SAFETY (1): `off + len <= buf.len()` is the caller's structural
//!   precondition. Unchecked here; discharged at the call site by Verus in
//!   verus.rs.
//! SAFETY (2): `len >= 4` guards the window header, so
//!   `off + 3 < off + len <= buf.len()`.
//! SAFETY (3): the record header is read only under `len - p >= 8` with
//!   `p <= len`, so `off + p + 7 < off + len <= buf.len()`.
//! SAFETY (4): **the three reverses touch `scr[a]` and `scr[b - 1]` only under
//!   `a < b <= SCR`.** `b` starts at `r` or at `m`, and after the reduction
//!   `r < m <= SCR` when `m != 0` and `r == 0` when `m == 0`, so every `b` in
//!   this kernel is at most `SCR == scr.len()`. That is the obligation p06 is
//!   about, and it is the one line R1 deletes.
//! SAFETY (5): the fold reads `scr[i]` only under `i < m <= SCR`.
//!
//! **(4) is the DISJOINTNESS fact spelled a third way.** R2 pays four bounds
//! checks per swap; R3 hands the question to `split_at_mut`, which answers it
//! with `core`'s own `unsafe`; this rung asserts it in a comment; R5 proves it.
//! The four trusted bases for the one fact are tabulated in ../NOTES.md 6, and
//! that -- not a speed number -- is p06's structural result.
//!
//! **The copy into the scratch is `copy_from_slice`, the same bulk spelling R2
//! and R3 use and the same one `memcpy` gives the C rungs.** It is left
//! CHECKED on purpose: ../spec.md pins the load identical across all seven
//! rungs so the measured difference is the rotate, and a `copy_nonoverlapping`
//! here would make R4's load a different program from R2's and R3's. The price
//! of that decision is one length check per record on the unsafe side, and it
//! is measured rather than waved at (../NOTES.md 3).
//!
//! The cursor guards are subtraction-first for the reason in this pattern's
//! other rungs: `p <= len` is maintained by the guards, the subtraction cannot
//! wrap, and the additive form does not verify.

#[path = "../../common/driver.rs"]
mod driver;

const SCR: usize = 64;

// THE BULK LOAD, and the one place all seven rungs are held to the same
// spelling: `memcpy` in C, this in all four Rust rungs, and verus.rs's trusted
// `scr_load` wrapper -- whose body is exactly this line -- in R5. ../spec.md
// pins it, so that the measured difference between rungs is the ROTATE and not
// the load. p02's retraction is the precedent: one operator flips `bulk_calls`
// and 100% of the delta.
//
// It is a `#[inline(always)]` free function rather than an inline expression
// because R5's copy has to be inside an `#[verifier::external_body]` item
// (there is no vstd spec for `copy_from_slice`), and R4 must be byte-identical
// to R5 at -O3. Written inline in `kernel` instead, R4 is 179 instructions;
// written this way it is 208, because the call boundary changes LLVM's
// inlining order. That 29-instruction delta is the `identity` pin's price on
// this pattern and ../NOTES.md 3 measures what it costs in executed `Ir`.
#[inline(always)]
fn scr_load(dst: &mut [u8; SCR], src: &[u8], from: usize, n: usize) {
    dst[..n].copy_from_slice(&src[from..from + n]);
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
        let mut r: usize = unsafe { *buf.get_unchecked(off + p + 4) } as usize
            + 256 * (unsafe { *buf.get_unchecked(off + p + 5) } as usize)
            + 65536 * (unsafe { *buf.get_unchecked(off + p + 6) } as usize)
            + 16777216 * (unsafe { *buf.get_unchecked(off + p + 7) } as usize);
        p = p + 8;
        let m: usize = if nelem < SCR { nelem } else { SCR };
        if len - p < nelem {
            break;
        }
        scr_load(&mut scr, buf, off + p, m);
        p = p + nelem;
        // THE SAFETY LINE. c/kernel.c omits exactly this.
        if m != 0 {
            r = r % m;
        } else {
            r = 0;
        }
        let mut a: usize = 0;
        let mut b: usize = r;
        while a < b {
            let t: u8 = unsafe { *scr.get_unchecked(a) };
            let u: u8 = unsafe { *scr.get_unchecked(b - 1) };
            unsafe { *scr.get_unchecked_mut(a) = u; }
            unsafe { *scr.get_unchecked_mut(b - 1) = t; }
            a = a + 1;
            b = b - 1;
        }
        a = r;
        b = m;
        while a < b {
            let t: u8 = unsafe { *scr.get_unchecked(a) };
            let u: u8 = unsafe { *scr.get_unchecked(b - 1) };
            unsafe { *scr.get_unchecked_mut(a) = u; }
            unsafe { *scr.get_unchecked_mut(b - 1) = t; }
            a = a + 1;
            b = b - 1;
        }
        a = 0;
        b = m;
        while a < b {
            let t: u8 = unsafe { *scr.get_unchecked(a) };
            let u: u8 = unsafe { *scr.get_unchecked(b - 1) };
            unsafe { *scr.get_unchecked_mut(a) = u; }
            unsafe { *scr.get_unchecked_mut(b - 1) = t; }
            a = a + 1;
            b = b - 1;
        }
        let mut i: usize = 0;
        while i < m {
            acc = acc.wrapping_mul(31)
                .wrapping_add(unsafe { *scr.get_unchecked(i) } as u64);
            i = i + 1;
        }
        acc = acc.wrapping_mul(31).wrapping_add(m as u64);
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
