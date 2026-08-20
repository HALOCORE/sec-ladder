//! p13 rung R3 -- safe-tuned.
//!
//! Same semantics as R2, written the way an experienced Rust programmer writes
//! a bounded copy into a fixed buffer: reslice the window once so every later
//! index is against a slice of known length, do the copy with
//! `copy_from_slice` and the zero-fill with `fill(0)` (one bounds check per
//! string instead of one per byte, and both lower to `memcpy`/`memset`), and
//! find the terminator with `position`. Still zero `unsafe`.
//!
//! **The reslice is spelled the CHEAP way and that was decided before it was
//! measured.** `.memory/01-ladder.md` finding 3 measured a two-step reslice --
//! `buf.split_at(off).1.split_at(len).0` -- at **−1 Ir/call** against
//! `&buf[off..off + len]`, with the same two panic paths, and the mechanism is
//! **register allocation, not bounds-check removal**: `off + len` needs a
//! scratch register while `buf_len - off` is computed in place in `%rsi`, which
//! is dead after. It was 20% of p04's whole published tax and it is untried on
//! every pattern before p04, so p13 spells it that way from the start rather
//! than owing a correction. ../NOTES.md 10a re-measures it here.
//!
//! **`position` is where "what does safe Rust return when C runs away?" is
//! answered.** `dst.iter().position(|&b| b == 0)` returns `Option<usize>`: on a
//! destination with no NUL it is `None`, and `.unwrap_or(DST_CAP)` turns that
//! into `32`. So safe Rust's three answers to the missing terminator are, in
//! ascending order of how much the language helps: R2 **panics** (an indexed
//! read past `dst[31]`), R3 **returns `DST_CAP`** (a total function with an
//! explicit default), C **reads the frame**. That is a SEMANTICS difference and
//! ../NOTES.md 4 reports it as one, not as a safety cost
//! (`.memory/01-ladder.md` finding 9's rule). The `unwrap_or` arm is dead in
//! every shipped cell -- `dst[DST_CAP - 1] = 0;` runs first -- and it is
//! written because the type demands it, which is the whole observation.
//!
//! **What is deliberately NOT varied here: the source scan.** p11 exists to
//! compare `strlen` / `memchr` / `CStr::from_bytes_until_nul` /
//! `iter().position()` on exactly that loop, and it measured a 12x library term
//! and a 5.3x spelling term. If R3 reached for `from_bytes_until_nul` on the
//! source, p13's headline would be p11's finding wearing p13's label. So the
//! source scan is the same indexed byte loop in R2, R3, R4 and R5 -- over the
//! reslice rather than over `buf` -- and the COPY, the FILL and the CONSUMER
//! are what move.
//!
//! **So R3 − R4 here is a SPELLING difference and must not be quoted as a
//! safety tax.** The matched-spelling safety number on this pattern is
//! `R2 − R4`: byte-loop copy against byte-loop copy, indexed against unchecked,
//! nothing else different. ../NOTES.md 4 gives both and says which is which.

#[path = "../../common/driver.rs"]
mod driver;

const DST_CAP: usize = 32;

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    if len < 4 {
        return 0;
    }
    let w: &[u8] = buf.split_at(off).1.split_at(len).0;
    let nstr: usize = w[0] as usize + 256 * (w[1] as usize)
        + 65536 * (w[2] as usize) + 16777216 * (w[3] as usize);
    if nstr == 0 {
        return 0;
    }
    let mut dst: [u8; DST_CAP] = [0; DST_CAP];
    let mut acc: u64 = 0;
    let mut p: usize = 4;
    let mut s: usize = 0;
    while s < nstr {
        let mut q: usize = p;
        while q < len {
            if w[q] == 0 {
                break;
            }
            q = q + 1;
        }
        let slen: usize = q - p;
        let n: usize = if slen < DST_CAP { slen } else { DST_CAP };
        dst[..n].copy_from_slice(&w[p..p + n]);
        dst[n..].fill(0);
        dst[DST_CAP - 1] = 0;
        let d: usize = dst.iter().position(|&b| b == 0).unwrap_or(DST_CAP);
        acc = acc.wrapping_mul(31).wrapping_add(d as u64);
        acc = acc.wrapping_mul(31).wrapping_add(dst[0] as u64);
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
