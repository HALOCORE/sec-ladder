//! p14 rung R3 -- safe-tuned.
//!
//! Same semantics as R2, written the way an experienced Rust programmer writes
//! a field splitter that must fill a fixed table: reslice the window once so
//! the per-access bounds checks are against a slice whose length LLVM already
//! knows, keep the delimiter scan explicit, and fold each field through
//! `iter().fold()` over `scr[cur..cur + tj]` rather than by indexing. Zero
//! `unsafe`.
//!
//! **The window reslice is the TWO-STEP form** (`.memory/01-ladder.md`
//! finding 3, the p04 lever): `buf.split_at(off).1.split_at(len).0` rather than
//! `&buf[off..off + len]`. Both keep both bounds checks; the two-step form is
//! one instruction cheaper because `buf_len - off` is computed in place in a
//! register that is dead afterwards while `off + len` needs a scratch one.
//! ../NOTES.md 9 reports what it is worth here.
//!
//! **What is deliberately NOT reached for: `<[T]>::split()`.**
//! `scr[..m].split(|&b| b == DELIM)` is the one-line spelling of this whole
//! kernel and ../spec.md forbids it **in every rung** rather than in some -- a
//! whole-pattern exclusion, which keeps the two sides of the comparison equal,
//! unlike the scoped kind `.memory/01-ladder.md` caught on p13. The exclusion
//! is priced and its prover disposition is measured rather than asserted
//! (../NOTES.md 8): `<[T]>::split` has no `assume_specification` at the pinned
//! vstd, so an R4 cannot have it and R3-with-it would compare a safe cell
//! against an unsafe cell that cannot exist -- p11's R4-by-permission result,
//! third instance.
//!
//! **The second in-contract R3 spelling is measured and published beside this
//! one** (`.memory/01-ladder.md` finding 3, which four patterns have now got
//! wrong): `t_pos`, whose scan is `rest.iter().position(|&b| b == DELIM)`
//! instead of an indexed `while`. ../NOTES.md 8 quotes both with the input
//! named, and the cheaper of the two is the number the headline uses.
//!
//! **The copy into the scratch is the same bulk `copy_from_slice` as R2's**, so
//! R2-vs-R3 is the scan and the fold and nothing else.
//!
//! `tl[..nt].iter()` rather than `0..nt` indexing is not a defensive extra: it
//! is the one place where a *safe* spelling removes a check that R2 pays, and
//! ../NOTES.md 4a checks the panic pads before calling the difference a safety
//! cost -- p06's lesson, where 2.00 Ir/byte of a "safety" term turned out to be
//! `zip`/`Rev` exhaustion tests containing no bounds check at all.

#[path = "../../common/driver.rs"]
mod driver;

const SCR: usize = 64;
const MAXTOK: usize = 16;
const DELIM: u8 = b',';

// THE BULK LOAD -- see safe_naive.rs; this rung shares its receiver spelling.
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
    let w: &[u8] = buf.split_at(off).1.split_at(len).0;
    let nline: usize = w[0] as usize + 256 * (w[1] as usize)
        + 65536 * (w[2] as usize) + 16777216 * (w[3] as usize);
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
        let llen: usize = w[p] as usize + 256 * (w[p + 1] as usize)
            + 65536 * (w[p + 2] as usize) + 16777216 * (w[p + 3] as usize);
        p = p + 4;
        let m: usize = if llen < SCR { llen } else { SCR };
        if len - p < llen {
            break;
        }
        scr_load(&mut scr, w, p, m);
        p = p + llen;
        let mut nt: usize = 0;
        let mut s: usize = 0;
        let mut i: usize = 0;
        while i <= m {
            if i == m || scr[i] == DELIM {
                // THE SAFETY LINE. c/kernel.c omits exactly this.
                if nt == MAXTOK {
                    break;
                }
                let flen: usize = i - s;
                tl[nt] = flen;
                nt = nt + 1;
                s = i + 1;
            }
            i = i + 1;
        }
        let mut cur: usize = 0;
        for &tj in tl[..nt].iter() {
            acc = acc.wrapping_mul(31).wrapping_add(tj as u64);
            acc = scr[cur..cur + tj]
                .iter()
                .fold(acc, |h, &e| h.wrapping_mul(31).wrapping_add(e as u64));
            cur = cur + tj + 1;
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
