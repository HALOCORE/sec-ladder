//! p25 rung R3 -- safe Rust, tuned. Same representation as R2, the same two
//! `Vec<u8>`s, the same allocator calls, the same answer; two spellings changed,
//! neither of which touches the saved reference.
//!
//!   * **the op walk:** `chunks_exact(2).take(nops)` instead of a cursor and two
//!     checked window reads, so the bounds check on the op pair is done once by
//!     the iterator rather than twice per operation by the indexer.
//!   * **the opcode:** `match c % 4 { .. }` instead of a chain of `if`s.
//!
//! Both are ordinary idiomatic safe Rust with no `unsafe`, no proof and no extra
//! trusted item; ../spec.md's `idiom` block pins the operations and deliberately
//! does not pin how the walk is spelled, exactly as p32 leaves its
//! handle-register spelling unpinned, p34 leaves its op walk and p14 leaves its
//! fold loop. A second in-contract R3 spelling and its cost are in ../NOTES.md 5
//! -- "cheapest FOUND, on this input", never "minimum"
//! (`.memory/01-ladder.md` finding 14).
//!
//! ⚠⚠ **WHAT DOES NOT CHANGE, AND CANNOT: THE SAVED REFERENCE IS STILL AN
//! INDEX.** There is no tuning lever anywhere in safe Rust that turns it back
//! into an interior pointer held across a `push`, which is why p25's safety line
//! has no site in R2 or R3 -- and why both rungs are, by construction, what
//! `c/kernel_hardened.c` computes. See R2's header and
//! ../controls/safe_arms.py, which measures that claim rather than asserting it
//! and ships the negative control the claim needs.
//!
//! **There is no epilogue in this rung either.** Dropping the two vectors frees
//! both blocks.

#[path = "../../common/driver.rs"]
mod driver;

const MAXCAP: usize = 64;
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
    let mut toks: Vec<u8> = Vec::new();
    let mut strs: Vec<u8> = Vec::new();
    let mut curi: usize = 0;
    let mut have: bool = false;
    let mut acc: u64 = 0;
    for op in buf[off + 4..off + len].chunks_exact(2).take(nops) {
        let c: u8 = op[0];
        let a: u8 = op[1];
        match c % 4 {
            0 => {
                if toks.len() < MAXCAP {
                    toks.push(a);
                    acc = acc.wrapping_mul(31).wrapping_add(a as u64);
                } else {
                    acc = acc.wrapping_mul(31).wrapping_add(SENT);
                }
            },
            1 => {
                if strs.len() < MAXCAP {
                    strs.push(a);
                    acc = acc.wrapping_mul(31).wrapping_add(a as u64);
                } else {
                    acc = acc.wrapping_mul(31).wrapping_add(SENT);
                }
            },
            2 => {
                if toks.len() > 0 {
                    curi = (a as usize) % toks.len();
                    have = true;
                    acc = acc.wrapping_mul(31).wrapping_add(2);
                } else {
                    acc = acc.wrapping_mul(31).wrapping_add(SENT);
                }
            },
            _ => {
                if have {
                    let v: u8 = toks[curi];
                    acc = acc.wrapping_mul(31).wrapping_add(v as u64);
                } else {
                    acc = acc.wrapping_mul(31).wrapping_add(SENT);
                }
            },
        }
    }
    acc.wrapping_mul(31).wrapping_add((toks.len() + strs.len()) as u64)
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
