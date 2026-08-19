//! p11 rung R4 -- unsafe.
//!
//! R2's algorithm with every bounds check removed: the four header bytes, every
//! byte the scan looks at and every byte the fold reads are read with
//! `get_unchecked`. **What does NOT go away is the `q < len` test** -- that is
//! not a bounds check, it is the loop's bound, and a rung without it would be
//! R1's bug written in Rust rather than an unsafe rung. This rung is correct; it
//! just has nothing checking that it is. R5 (verus.rs) is this exec code with
//! the SAFETY comments below turned into obligations a verifier discharges.
//!
//! SAFETY (1): `off + len <= buf.len()` is the caller's structural
//!   precondition. Unchecked here; discharged at the call site by Verus in
//!   verus.rs.
//! SAFETY (2): `len >= 4` guards the header, so `off + 3 < off + len <=
//!   buf.len()`.
//! SAFETY (3): the scan reads `off + q` only under `q < len`, so
//!   `off + q < off + len <= buf.len()`.
//! SAFETY (4): the fold reads `off + i` only under `i < q`, and `q <= len` on
//!   exit from the scan loop (it starts at `p <= len` and increments only under
//!   `q < len`), so `off + i < off + len <= buf.len()`.
//!
//! **Every one of those steps is linear**, which is p11's contrast with p05 --
//! no `i*ncol + j`, no `lemma_mul_inequality`, no `by (nonlinear_arith)` in the
//! kernel. What p11 pays instead is that **there is no closed form for `q`**:
//! the scan's trip count is the data, so the invariant has to be the "*the scan
//! from here is the whole scan*" shape p16 found for its walk, and the kernel
//! carries three loops rather than p07's two. NOTES.md 5 has the tally.
//!
//! **One overflow obligation has no analogue in any earlier pattern, and the
//! line that discharges it is `if q >= len { break; }`.** The cursor step is
//! `p = q + 1`, and the scan may legitimately stop at `q == len` (a window with
//! no terminator left), so `q + 1` is `len + 1`. Proving that does not overflow
//! `usize` needs `len < usize::MAX`, and vstd has **no axiom that a slice is at
//! most `isize::MAX` bytes** (`.memory/04-verus.md`), so it is not derivable:
//! p17 bought its way out of the analogous obligation with a second `requires`
//! and a third driver conjunct. p11 does not, because the guard above the cursor
//! step makes `q < len` -- at zero preconditions, zero driver statements and
//! zero instructions beyond the one compare. And that guard is not a prover
//! concession: it is the sentence *"a string whose terminator is missing is the
//! last string in the window"*, i.e. the case R1 cannot represent, which is why
//! it is in `idiom.required` rather than being conventional. NOTES.md 5a.

#[path = "../../common/driver.rs"]
mod driver;

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    if len < 4 {
        return 0;
    }
    let nstr: usize = unsafe { *buf.get_unchecked(off) } as usize
        + 256 * (unsafe { *buf.get_unchecked(off + 1) } as usize)
        + 65536 * (unsafe { *buf.get_unchecked(off + 2) } as usize)
        + 16777216 * (unsafe { *buf.get_unchecked(off + 3) } as usize);
    if nstr == 0 {
        return 0;
    }
    let mut acc: u64 = 0;
    let mut p: usize = 4;
    let mut s: usize = 0;
    while s < nstr {
        let mut q: usize = p;
        while q < len {
            if unsafe { *buf.get_unchecked(off + q) } == 0 {
                break;
            }
            q = q + 1;
        }
        let slen: usize = q - p;
        let mut h: u64 = 0;
        let mut i: usize = p;
        while i < q {
            h = h.wrapping_mul(31).wrapping_add(unsafe { *buf.get_unchecked(off + i) } as u64);
            i = i + 1;
        }
        acc = acc.wrapping_mul(31).wrapping_add(h ^ (slen as u64));
        if q >= len {
            break;
        }
        p = q + 1;
        if p >= len {
            break;
        }
        s = s + 1;
    }
    acc.wrapping_mul(31).wrapping_add(nstr as u64)
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
