//! p05 rung R3 -- safe-tuned.
//!
//! Same semantics as R2, written the way an experienced Rust programmer writes
//! a matrix fold: reslice the header once and index the small slice, then
//! reslice each **row** and sum it with an iterator, so the inner loop carries
//! no per-element bounds check at all -- the reslice is the check, it happens
//! once per row, and it is outside the fold by construction rather than by the
//! optimiser's goodwill. Still zero `unsafe`.
//!
//! `chunks_exact(ncol)` would be the more idiomatic spelling still, and it is
//! deliberately *not* used: it would delete the flattened index `i * ncol + j`,
//! which is the pattern. Reslicing `[base .. base + ncol]` with
//! `base = off + 4 + i * ncol` keeps the multiply where the C rung has it and
//! moves only the per-element check.
//!
//! **This rung doubles as the decomposition control** TASK_013 asks for
//! (`.memory/01-ladder.md` finding 4's rule: confirm by construction, never by
//! reading two disassemblies). R2 and R3 differ in the inner loop and in
//! nothing else -- same header handling, same size check, same outer Horner
//! step, same flattened index -- so R2 - R3 *is* the cost of the per-element
//! check on the vectorised loop, measured rather than attributed. NOTES.md 3.
//!
//! `.memory/01-ladder.md`: never publish a safety-cost claim without this rung.
//! Reporting R2 alone overstated safe Rust's cost by ~3.7x on the pilot, and
//! p16's first write-up broke the same rule on the next pattern.

#[path = "../../common/driver.rs"]
mod driver;

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    if len < 4 {
        return 0;
    }
    let hdr: &[u8] = &buf[off..off + 4];
    let nrow: usize = hdr[0] as usize + 256 * (hdr[1] as usize);
    let ncol: usize = hdr[2] as usize + 256 * (hdr[3] as usize);
    if nrow == 0 || ncol == 0 {
        return 0;
    }
    let avail: usize = len - 4;
    if nrow * ncol > avail {
        return 0;
    }
    let mut acc: u64 = 0;
    for i in 0..nrow {
        let base: usize = off + 4 + i * ncol;
        let row: u32 = buf[base..base + ncol]
            .iter()
            .fold(0u32, |a, &x| a.wrapping_add(x as u32));
        acc = acc.wrapping_mul(31).wrapping_add(row as u64);
    }
    acc.wrapping_mul(31).wrapping_add((nrow * ncol) as u64)
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
