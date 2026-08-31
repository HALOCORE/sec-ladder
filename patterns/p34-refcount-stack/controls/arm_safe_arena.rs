//! p34 CONTROL ARM: **the OTHER branch of `.memory/01-ladder.md`'s law, in safe
//! Rust.** Not a rung -- a control. Driven by `controls/safe_arms.py`.
//!
//! The law is: *safe Rust's temporal guarantee is a guarantee about the
//! ALLOCATOR; a structure that recycles its own storage gets no guarantee at
//! all.* p28 is the branch where safe Rust CANNOT reproduce the C bug and p32 is
//! the branch where it reproduces it bit for bit, and until now those were two
//! different rows. **p34 has both branches, selected by the port**, and this
//! file is the second one.
//!
//!   * `arm_safe_rc_move.rs` / `arm_safe_rc_borrow.rs` -- the `Rc` port, which
//!     is what the shipped R2 and R3 are. The bug is **not expressible**:
//!     `Rc::clone` publishes the second reference and increments in ONE
//!     operation, and the two ways of getting a second reference without it
//!     DO NOT COMPILE. p28's shape.
//!   * **this file** -- an INDEX-ARENA port, which is equally safe Rust,
//!     `#![forbid(unsafe_code)]`, and which **reproduces `c/kernel.c` bit for
//!     bit** because the arena recycles its own storage and the allocator is
//!     never involved. p32's shape.
//!
//! Two builds, and the `#[cfg]` is the whole difference:
//!
//!     rustc --cfg slb_arm_retain   the RETAIN present  -- must equal ../model.py
//!     rustc                        the RETAIN absent   -- must equal c/kernel.c
//!
//! ⚠ **The free list is LIFO and that is load-bearing, not incidental.** glibc's
//! tcache is LIFO, so in C the `NEW` after a `POP` gets the freed block back;
//! this arm's `free[]` stack does the same, which is why the recycle-divergent
//! input lands on the same number. A FIFO free list would not reproduce it and
//! would be measuring a different allocator.
//!
//! ⚠ `ARENA` is 32 where the stack holds 16, which is headroom that is never
//! reached: at most `ntop <= CAP` distinct slots can be allocated at once and a
//! `NEW` runs only under `ntop < CAP`. `safe_arms.py` records the high-water
//! mark so the headroom is a measured claim rather than an assumption.

#![forbid(unsafe_code)]

#[path = "../../../common/driver.rs"]
mod driver;

const CAP: usize = 16;
const DLEN: usize = 8;
const SENT: u64 = 251;
const ARENA: usize = 32;

#[derive(Clone, Copy)]
struct Slot {
    rc: usize,
    len: usize,
    data: [u8; DLEN],
}

// ---------------------------------------------------------------- kernel ----
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
    // The arena. `data` is NEVER cleared on a free -- that is what a recycled
    // block is, and it is why a stale index reads the previous tenant's byte
    // until something writes over it.
    let mut pool: [Slot; ARENA] = [Slot { rc: 0, len: 0, data: [0u8; DLEN] }; ARENA];
    // The free list, LIFO, most-recently-freed first. Initialised so that the
    // first NEW takes slot 0, the second slot 1, ... as glibc's fresh chunks do.
    let mut free: [usize; ARENA] = [0usize; ARENA];
    let mut nfree: usize = ARENA;
    for j in 0..ARENA {
        free[j] = ARENA - 1 - j;
    }
    let mut stk: [usize; CAP] = [0usize; CAP];
    let mut ntop: usize = 0;
    let mut nnew: usize = 0;
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
        if c % 4 == 0 {
            if ntop < CAP {
                // POP the free list. The headroom claim is that this cannot
                // underflow; `safe_arms.py` records the high-water mark.
                nfree = nfree - 1;
                let s = free[nfree];
                pool[s].rc = 1;
                pool[s].len = DLEN;
                pool[s].data = [0u8; DLEN];
                pool[s].data[0] = a.wrapping_mul(7).wrapping_add(1);
                stk[ntop] = s;
                ntop = ntop + 1;
                nnew = nnew + 1;
                acc = acc.wrapping_mul(31).wrapping_add(a as u64);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else if c % 4 == 1 {
            if ntop > 0 && ntop < CAP {
                let t = stk[ntop - 1];
                // THE SAFETY LINE, in SAFE Rust and therefore forgettable --
                // which is the whole point of this arm. An index is not an
                // owning handle, so nothing in the type system is watching.
                #[cfg(slb_arm_retain)]
                {
                    pool[t].rc = pool[t].rc.wrapping_add(1);
                }
                stk[ntop] = t;
                ntop = ntop + 1;
                acc = acc.wrapping_mul(31).wrapping_add(1);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else if c % 4 == 2 {
            if ntop > 0 {
                ntop = ntop - 1;
                let s = stk[ntop];
                pool[s].rc = pool[s].rc.wrapping_sub(1);
                if pool[s].rc == 0 {
                    free[nfree] = s;
                    nfree = nfree + 1;
                }
                acc = acc.wrapping_mul(31).wrapping_add(2);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else {
            if ntop > 0 {
                let v: u8 = pool[stk[(a as usize) % ntop]].data[0];
                acc = acc.wrapping_mul(31).wrapping_add(v as u64);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        }
        o = o + 1;
    }
    // The epilogue. The arena arm HAS one, where the `Rc` rungs do not: an index
    // owns nothing, so nothing is dropped when the stack goes out of scope.
    while ntop > 0 {
        ntop = ntop - 1;
        let s = stk[ntop];
        pool[s].rc = pool[s].rc.wrapping_sub(1);
        if pool[s].rc == 0 {
            free[nfree] = s;
            nfree = nfree + 1;
        }
    }
    acc.wrapping_mul(31).wrapping_add(nnew as u64)
}

// ---------------------------------------------------------------- driver ----
fn main() {
    let path = driver::arg_path();
    let inp = driver::load(&path);
    let (stride_w, bytes) = driver::head1_u64_bytes(&inp);
    let n_iters: u64 = inp.n_iters;
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
    driver::emit(acc);
}
