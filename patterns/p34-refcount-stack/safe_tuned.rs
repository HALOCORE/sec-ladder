//! p34 rung R3 -- safe Rust, tuned. Same representation as R2, the same
//! allocations, the same answer; three spellings changed, none of which touches
//! the ownership discipline.
//!
//!   * **the op walk:** `chunks_exact(2).take(nops)` instead of a cursor and two
//!     checked window reads, so the bounds check on the op pair is done once by
//!     the iterator rather than twice per operation by the indexer.
//!   * **the opcode:** `match c % 4 { .. }` instead of a chain of `if`s.
//!   * **READ:** `match &stk[j] { Some(r) => .., None => .. }` -- one
//!     discriminant test where R2 asks `as_ref()` and then `unwrap()`s, which is
//!     a test plus a panicking unwrap on the same slot.
//!
//! All three are ordinary idiomatic safe Rust with no `unsafe`, no proof and no
//! extra trusted item; ../spec.md's `idiom` block pins the operations and
//! deliberately does not pin how the walk is spelled, exactly as p32 leaves its
//! handle-register spelling unpinned and p14 leaves its fold loop. A second
//! in-contract R3 spelling and its cost are in ../NOTES.md 5 -- "cheapest FOUND,
//! on this input", never "minimum" (`.memory/01-ladder.md` finding 14).
//!
//! ⚠⚠ **WHAT DOES NOT CHANGE, AND CANNOT: THE RETAIN.** `Rc::clone` is still the
//! only way to publish a second reference, and it still increments. There is no
//! tuning lever anywhere in safe Rust that separates the publication from the
//! count, which is why p34's safety line has no site in R2 or R3. See R2's
//! header and ../controls/safe_arms.py.
//!
//! **There is no epilogue in this rung either.** Dropping the stack releases
//! every reference still held.

#[path = "../../common/driver.rs"]
mod driver;

use std::rc::Rc;

const CAP: usize = 16;
const DLEN: usize = 8;
const SENT: u64 = 251;

/// The object, WITHOUT a reference count -- `Rc` owns the count. R2's header
/// says why that is the whole finding.
pub struct Obj {
    pub len: usize,
    pub data: [u8; DLEN],
}

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
    let mut stk: [Option<Rc<Obj>>; CAP] = [const { None }; CAP];
    let mut ntop: usize = 0;
    let mut nnew: usize = 0;
    let mut acc: u64 = 0;
    for op in buf[off + 4..off + len].chunks_exact(2).take(nops) {
        let c: u8 = op[0];
        let a: u8 = op[1];
        match c % 4 {
            0 => {
                if ntop < CAP {
                    let mut d: [u8; DLEN] = [0u8; DLEN];
                    d[0] = a.wrapping_mul(7).wrapping_add(1);
                    stk[ntop] = Some(Rc::new(Obj { len: DLEN, data: d }));
                    ntop = ntop + 1;
                    nnew = nnew + 1;
                    acc = acc.wrapping_mul(31).wrapping_add(a as u64);
                } else {
                    acc = acc.wrapping_mul(31).wrapping_add(SENT);
                }
            },
            1 => {
                if ntop > 0 && ntop < CAP {
                    // THE RETAIN. Still `Rc::clone`, still unforgettable.
                    let t: Rc<Obj> = Rc::clone(stk[ntop - 1].as_ref().unwrap());
                    stk[ntop] = Some(t);
                    ntop = ntop + 1;
                    acc = acc.wrapping_mul(31).wrapping_add(1);
                } else {
                    acc = acc.wrapping_mul(31).wrapping_add(SENT);
                }
            },
            2 => {
                if ntop > 0 {
                    // THE RELEASE, in one visit to the slot: `take()` moves the
                    // `Rc` out and drops it, which decrements and frees at zero.
                    ntop = ntop - 1;
                    stk[ntop].take();
                    acc = acc.wrapping_mul(31).wrapping_add(2);
                } else {
                    acc = acc.wrapping_mul(31).wrapping_add(SENT);
                }
            },
            _ => {
                if ntop > 0 {
                    match &stk[(a as usize) % ntop] {
                        Some(r) => {
                            acc = acc.wrapping_mul(31).wrapping_add(r.data[0] as u64);
                        },
                        None => {
                            acc = acc.wrapping_mul(31).wrapping_add(SENT);
                        },
                    }
                } else {
                    acc = acc.wrapping_mul(31).wrapping_add(SENT);
                }
            },
        }
    }
    // No epilogue: `stk` is dropped here and that releases every reference still
    // held, freeing every object whose count reaches zero.
    acc.wrapping_mul(31).wrapping_add(nnew as u64)
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
