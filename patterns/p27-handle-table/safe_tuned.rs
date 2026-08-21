//! p27 rung R3 -- safe Rust, tuned. Same representation as R2, same
//! allocations, same answer; two spellings changed, both of which fuse a
//! liveness test with the operation it guards.
//!
//!   * **CLOSE:** `tab[h].take().is_some()` -- one visit to the slot does the
//!     free, the invalidation and the test. R2 tests, then assigns, which is two
//!     visits and two discriminant loads.
//!   * **READ:** `match &tab[h] { Some(rec) => .., None => .. }` -- one
//!     discriminant test. R2 asks `is_some()` and then `unwrap()`s, which is
//!     two.
//!
//! Both are ordinary idiomatic safe Rust with no `unsafe`, no proof and no extra
//! trusted item; ../spec.md's `idiom` block pins the operations and deliberately
//! does not pin how the test is spelled, exactly as p14 leaves its fold loop
//! unpinned. A second in-contract R3 spelling and its cost are in
//! ../NOTES.md 8 -- "cheapest FOUND, on this input", never "minimum"
//! (`.memory/01-ladder.md` finding 14).
//!
//! **There is no epilogue in this rung either.** Dropping the table frees every
//! record still alive.

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
                tab[ntab] = Some(Box::new(a));
                ntab = ntab + 1;
                acc = acc.wrapping_mul(31).wrapping_add(a as u64);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else if c % 4 == 1 {
            // THE FREE, THE INVALIDATION and THE TEST, in one visit.
            if h < ntab && tab[h].take().is_some() {
                acc = acc.wrapping_mul(31).wrapping_add(1);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else {
            // THE SAFETY LINE, and c/kernel.c omits exactly the liveness half
            // of it -- here spelled as the `None` arm.
            if h < ntab {
                match &tab[h] {
                    Some(rec) => {
                        acc = acc.wrapping_mul(31).wrapping_add(**rec as u64);
                    },
                    None => {
                        acc = acc.wrapping_mul(31).wrapping_add(SENT);
                    },
                }
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
