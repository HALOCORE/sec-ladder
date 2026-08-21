//! p27 rung R2 -- safe Rust, naive.
//!
//! **The representation is not a choice.** Safe Rust cannot hold a pointer to a
//! record it has freed, so a slot is `Option<Box<u8>>`: `Some` while the record
//! lives, `None` once it does not. Two consequences, and they are the pattern:
//!
//!   1. `Option<Box<u8>>` is **niche-optimised to one pointer word** -- `None`
//!      *is* the null pointer -- so this table is byte-for-byte C's `tab[]`
//!      minus C's separate `live[]` array. The safe representation IS the
//!      hardened-C representation, arrived at by construction.
//!   2. `tab[h] = None` **frees the record and invalidates the handle in one
//!      operation.** C can do those two things separately, and c/kernel.c's bug
//!      is exactly that separation: it does the free and skips the check.
//!
//! **There is no epilogue in this rung.** Dropping the table frees every record
//! still alive; the loop the C and unsafe rungs write by hand is written by the
//! language. ../NOTES.md 3 prices the difference.
//!
//! Naive in the two places R3 tunes: the READ path asks `is_some()` and then
//! `unwrap()`s -- two discriminant tests on the same slot -- and the CLOSE path
//! asks `is_some()` and then assigns `None`, which is a second visit to the same
//! slot. Every index is a plain `tab[h]` under an explicit `h < ntab`, so rustc
//! emits its own bounds check on top of the semantic one; whether it survives is
//! ../NOTES.md 4.
//!
//! Wrapping arithmetic is spelled `wrapping_mul` / `wrapping_add` because
//! `-C debug-assertions=on` would otherwise panic on the fold, and the C rungs
//! wrap by definition (C99 6.2.5p9).

#[path = "../../common/driver.rs"]
mod driver;

const TABCAP: usize = 32;
const SENT: u64 = 251;

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    if len < 4 {
        return 0;
    }
    let nops: usize = buf[off] as usize + 256 * (buf[off + 1] as usize) + 65536 * (buf[off + 2]
        as usize) + 16777216 * (buf[off + 3] as usize);
    if nops == 0 {
        return 0;
    }
    let mut tab: [Option<Box<u8>>; TABCAP] = [const { None }; TABCAP];
    let mut ntab: usize = 0;
    let mut acc: u64 = 0;
    let mut p: usize = 4;
    let mut o: usize = 0;
    while o < nops {
        if len - p < 2 {
            break;
        }
        let c: u8 = buf[off + p];
        let a: u8 = buf[off + p + 1];
        p = p + 2;
        let h: usize = a as usize;
        if c % 4 == 0 {
            if ntab < TABCAP {
                // THE ALLOCATION: `Box::new(a)` is one `malloc(1)`, the same
                // allocator and the same size class as C's `malloc(RECSZ)`.
                tab[ntab] = Some(Box::new(a));
                ntab = ntab + 1;
                acc = acc.wrapping_mul(31).wrapping_add(a as u64);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else if c % 4 == 1 {
            if h < ntab && tab[h].is_some() {
                // THE FREE **and** THE INVALIDATION, in one operation. This is
                // the line C splits in two and then half-forgets.
                tab[h] = None;
                acc = acc.wrapping_mul(31).wrapping_add(1);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else {
            // THE SAFETY LINE, and c/kernel.c omits exactly the second
            // conjunct. In Rust it is a SEMANTIC line, not a safety line: the
            // borrow checker is what makes this rung safe, and `is_some()` is
            // what makes it CORRECT.
            if h < ntab && tab[h].is_some() {
                let v: u8 = **tab[h].as_ref().unwrap();
                acc = acc.wrapping_mul(31).wrapping_add(v as u64);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        }
        o = o + 1;
    }
    // No epilogue: `tab` is dropped here and that frees every live record.
    acc.wrapping_mul(31).wrapping_add(ntab as u64)
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
