//! p32 rung R3 -- safe Rust, tuned.
//!
//! R2's algorithm, respelled the way a Rust programmer would actually write it,
//! and **the point of the rung is what does NOT change**:
//!
//!   * the pool becomes `[[u8; BLK]; SLOTS]`, so a payload access is `pool[h][1]`
//!     and the `h * BLK + 1` arithmetic is gone;
//!   * the handle registers become `[Option<(u8, u32)>; NREG]`, so the NIL
//!     sentinel test becomes an `Option` discriminant -- **which is the ONE half
//!     of the safety line the language will write for you here**;
//!   * `h` is widened to `usize` once per operation instead of at each use;
//!   * the opcode is a `match` rather than an `if` chain.
//!
//! ⚠⚠ **AND THE GENERATION CONJUNCT IS STILL WRITTEN OUT BY HAND**, `gen[h] != g`,
//! in the most idiomatic safe Rust available. That is the row: `Option` knows
//! whether the register holds a handle; nothing in the type system knows whether
//! the BLOCK that handle names is still the same incarnation, because the block
//! is a range of bytes in an array that is alive from the first instruction to
//! the last. `p29` gets its first conjunct free from `Option` for the same
//! reason and its SECOND written out for this one; `p32` gets the same split
//! with the free half moved to a different question.
//!
//! ⚠ **No cost claim is made for any of the four changes above.** This pattern
//! publishes no rung-to-rung cost headline (`../NOTES.md` 8); the levers on both
//! sides were not counted, and `.memory/02-bench-rules.md` forbids publishing a
//! spread as a safety number. The absence is declared, not a measured zero.

#[path = "../../common/driver.rs"]
mod driver;

const SLOTS: usize = 8;
const BLK: usize = 4;
const NREG: usize = 8;
const NIL: u8 = 255;
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
    let mut pool: [[u8; BLK]; SLOTS] = [[0u8; BLK]; SLOTS];
    let mut nx: [u8; SLOTS] = [0u8; SLOTS];
    let mut gen: [u32; SLOTS] = [0u32; SLOTS];
    let mut reg: [Option<(u8, u32)>; NREG] = [None; NREG];
    let mut j: usize = 0;
    while j < SLOTS {
        nx[j] = if j + 1 < SLOTS { (j + 1) as u8 } else { NIL };
        j = j + 1;
    }
    let mut freehead: u8 = 0;
    let mut nalloc: usize = 0;
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
        let r: usize = (a % NREG as u8) as usize;
        let v: u64 = if c % 4 == 0 {
            // ALLOC. **Nothing is allocated** -- the block already exists.
            if freehead == NIL {
                SENT
            } else {
                let s: usize = freehead as usize;
                freehead = nx[s];
                pool[s][0] = a;
                pool[s][1] = a.wrapping_mul(7).wrapping_add(1);
                let gs: u32 = gen[s];
                reg[r] = Some((s as u8, gs));
                nalloc = nalloc + 1;
                (s as u64).wrapping_add((gs as u64).wrapping_mul(8))
            }
        } else {
            // THE SAFETY LINE. The `Some` arm is the `Option` discriminant --
            // the half the language writes for you -- and `gen[h] != g` is the
            // half it does not and cannot.
            match reg[r] {
                None => SENT,
                Some((hb, g)) => {
                    let h: usize = hb as usize;
                    if gen[h] != g {
                        SENT
                    } else if c % 4 == 1 {
                        gen[h] = gen[h].wrapping_add(1);
                        nx[h] = freehead;
                        freehead = hb;
                        1
                    } else if c % 4 == 2 {
                        pool[h][1] as u64
                    } else {
                        pool[h][1] = a.wrapping_mul(13).wrapping_add(3);
                        3
                    }
                }
            }
        };
        acc = acc.wrapping_mul(31).wrapping_add(v);
        o = o + 1;
    }
    acc.wrapping_mul(31).wrapping_add(nalloc as u64)
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
