//! p47 rung R4 -- unsafe.
//!
//! R3's algorithm with every bounds check removed: `get_unchecked` on the
//! header and on both tags. **The obligation it takes on is a SPATIAL one** --
//! that `off + p + tlen + i` is inside `buf` -- and `verus.rs` discharges it
//! from the guard `len - p >= 2 * tlen` plus the kernel's one structural
//! precondition.
//!
//! ⚠ **AND THAT IS THE PATTERN'S POINT, STATED FROM THE UNSAFE SIDE.** The
//! obligation this rung takes on, and that rung 5 discharges, has **nothing to
//! do with p47's bug**. `c/kernel.c` violates no bound; it leaks. Every other
//! pattern in this tree can say "the proof rules out the C rung's defect"; p47
//! cannot, and the reason is not that the proof is weak. Verus has no cost
//! model and no notion of a trace, so the property is not expressible in it at
//! all. ../NOTES.md 9 states precisely what *can* be proved and what cannot.
//!
//! **This rung is CONSTANT-TIME, and it is constant-time for the same reason
//! R3 is: it reads every byte.** Removing the bounds checks moved no part of
//! the timing property in either direction. The security column of this
//! pattern is `{R1 leaks, R1h no, R2 leaks, R3 no, R4 no, R5 no}` and the
//! safety column is `{R1 safe, R1h safe, R2 safe, R3 safe, R4 unsafe+proved,
//! R5 unsafe+proved}`. **The two columns are uncorrelated, and that is the
//! finding.**
//!
//! ⚠ **THE INDEXED SAFE LOOP UNROLLS WIDER THAN THIS ONE.** In the isolated
//! probe (../NOTES.md 0) LLVM gave a safe `for i in 0..n { d |= a[i]^b[i] }`
//! a 2x16-byte body and gave this spelling a 1x16-byte one -- 22 Ir/call
//! *against* the unsafe rung at n = 256. The shipped R3 is the `zip`+`fold`
//! spelling rather than that one, so the shipped comparison is not that
//! comparison; both are measured in ../NOTES.md 8 and the R3-side span is
//! published beside the headline. `.memory/01-ladder.md` finding 18 (p10) and
//! finding 19 (p27) are the two patterns where an unsearched R4 side flattered
//! the safe rung, so ../NOTES.md 8b searches this one and says what it found.
//!
//! **`#[cfg(slb_isolated)] inline(never)`** matches every other rung, so the
//! `isolated` column measures a real call in all eight cells.

#[path = "../../common/driver.rs"]
mod driver;

const MATCH: u64 = 7;
const MISS: u64 = 251;

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    if len < 8 {
        return 0;
    }
    let ntag: usize = unsafe { *buf.get_unchecked(off) } as usize
        + 256 * (unsafe { *buf.get_unchecked(off + 1) } as usize)
        + 65536 * (unsafe { *buf.get_unchecked(off + 2) } as usize)
        + 16777216 * (unsafe { *buf.get_unchecked(off + 3) } as usize);
    let tlen: usize = unsafe { *buf.get_unchecked(off + 4) } as usize
        + 256 * (unsafe { *buf.get_unchecked(off + 5) } as usize)
        + 65536 * (unsafe { *buf.get_unchecked(off + 6) } as usize)
        + 16777216 * (unsafe { *buf.get_unchecked(off + 7) } as usize);
    if ntag == 0 || tlen == 0 {
        return 0;
    }
    let mut acc: u64 = 0;
    let mut p: usize = 8;
    let mut o: usize = 0;
    while o < ntag && len - p >= 2 * tlen {
        // THE TIMING LINE. Every byte is read on every call; the accumulator
        // is tested once, after the fold.
        let mut d: u8 = 0;
        let mut i: usize = 0;
        while i < tlen {
            d = d
                | (unsafe { *buf.get_unchecked(off + p + i) }
                    ^ unsafe { *buf.get_unchecked(off + p + tlen + i) });
            i = i + 1;
        }
        acc = if d == 0 {
            acc.wrapping_mul(31).wrapping_add(MATCH)
        } else {
            acc.wrapping_mul(31).wrapping_add(MISS)
        };
        p = p + 2 * tlen;
        o = o + 1;
    }
    acc.wrapping_mul(31).wrapping_add(o as u64)
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
