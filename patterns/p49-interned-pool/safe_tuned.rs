//! p49 rung R3 -- safe Rust, tuned. Same representation as R2, the same pool,
//! the same answer; four spellings changed, none of which touches the ownership
//! discipline.
//!
//!   * **the op walk:** `chunks_exact(2).take(nops)` instead of a cursor and two
//!     checked window reads, so the bounds check on the op pair is done once by
//!     the iterator rather than twice per operation by the indexer.
//!   * **the opcode:** `match c % 4 { 0 | 1 => .., 2 => .., _ => .. }` instead of
//!     a chain of `if`s.
//!   * **the dedup lookup:** `iter().zip().position()` instead of an indexed
//!     `while` with a `break`.
//!   * **the byte loops:** slice iterators -- `iter_mut().enumerate()` to
//!     materialise, `iter().fold()` to fold, and `copy_within` for the
//!     copy-on-write copy.
//!
//! ⚠ **`copy_within` IS `memmove`, and that is worth saying out loud on this
//! row of all rows.** It is CORRECT under overlap, which is exactly the
//! difference between p49 and p08: p08's bug is that its one copy overlaps and
//! is spelled `memcpy`; p49's copy-on-write copy CANNOT overlap in any rung
//! (`../c/kernel.h`; `../controls/no_overlap.py` re-derives it from the shipped
//! blobs), so the choice between `copy_within` and a byte loop is a TUNING
//! decision here and a CORRECTNESS one there.
//!
//! All four are ordinary idiomatic safe Rust with no `unsafe`, no proof and no
//! extra trusted item; ../spec.md's `idiom` block pins the operations and
//! deliberately does not pin how the walk, the lookup or the byte loops are
//! spelled, exactly as p32 leaves its handle-register spelling unpinned, p34 its
//! op walk and p14 its fold loop. A second in-contract R3 spelling and its cost
//! are in ../NOTES.md 5 -- "cheapest FOUND, on this input", never "minimum"
//! (`.memory/01-ladder.md` finding 14).
//!
//! ⚠⚠ **WHAT DOES NOT CHANGE: THE SAFETY LINE.** `if rshd[t] == 1` is still
//! there and still un-shares before writing. Safe Rust supplies no tuning lever
//! that removes it, because in the index-arena representation the alias is an
//! INTEGER and the borrow checker has nothing to say about it. R2's header has
//! the three-arm measurement.

#[path = "../../common/driver.rs"]
mod driver;

const MEM: usize = 64;
const ARENA: usize = 20;
const NENT: usize = 8;
const NREC: usize = 12;
const NKEY: u8 = 7;
const MAXW: u8 = 6;
const THRESH: u8 = 4;
const SENT: u64 = 251;

/// A content byte -- R2's header says why `(key, w)` names the string.
fn cbyte(key: u8, j: u8) -> u8 {
    key.wrapping_mul(7).wrapping_add(j.wrapping_mul(13)).wrapping_add(1)
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
    let mut mem: [u8; MEM] = [0u8; MEM];
    let mut ekey: [u8; NENT] = [0u8; NENT];
    let mut elen: [u8; NENT] = [0u8; NENT];
    let mut eoff: [u8; NENT] = [0u8; NENT];
    let mut roff: [u8; NREC] = [0u8; NREC];
    let mut rlen: [u8; NREC] = [0u8; NREC];
    let mut rshd: [u8; NREC] = [0u8; NREC];
    let mut nent: usize = 0;
    let mut nrec: usize = 0;
    let mut abump: usize = 0;
    let mut pbump: usize = ARENA;
    let mut acc: u64 = 0;
    for op in buf[off + 4..off + len].chunks_exact(2).take(nops) {
        let c: u8 = op[0];
        let a: u8 = op[1];
        let w: u8 = 1 + a % MAXW;
        let key: u8 = a % NKEY;
        let v: u64 = match c % 4 {
            0 | 1 => {
                if nrec >= NREC {
                    SENT
                } else if w < THRESH {
                    // THE DEDUP LOOKUP, tuned: one pass, no index arithmetic.
                    match ekey[..nent].iter().zip(elen[..nent].iter())
                        .position(|(&x, &y)| x == key && y == w) {
                        Some(k) => {
                            // A DEDUP HIT: the new record BORROWS the buffer an
                            // earlier record already holds. Correct, intended,
                            // and the contract.
                            roff[nrec] = eoff[k];
                            rlen[nrec] = w;
                            rshd[nrec] = 1;
                            nrec = nrec + 1;
                            a as u64
                        },
                        None => {
                            if nent >= NENT || abump + (w as usize) > ARENA {
                                SENT
                            } else {
                                for (j, s) in mem[abump..abump + w as usize]
                                    .iter_mut().enumerate() {
                                    *s = cbyte(key, j as u8);
                                }
                                ekey[nent] = key;
                                elen[nent] = w;
                                eoff[nent] = abump as u8;
                                roff[nrec] = abump as u8;
                                rlen[nrec] = w;
                                rshd[nrec] = 1;
                                nent = nent + 1;
                                abump = abump + w as usize;
                                nrec = nrec + 1;
                                a as u64
                            }
                        },
                    }
                } else if pbump + (w as usize) > MEM {
                    SENT
                } else {
                    for (j, s) in mem[pbump..pbump + w as usize].iter_mut().enumerate() {
                        *s = cbyte(key, j as u8);
                    }
                    roff[nrec] = pbump as u8;
                    rlen[nrec] = w;
                    rshd[nrec] = 0;
                    pbump = pbump + w as usize;
                    nrec = nrec + 1;
                    a as u64
                }
            },
            2 => {
                if nrec == 0 {
                    SENT
                } else {
                    let t: usize = (a as usize) % nrec;
                    // THE SAFETY LINE. Unchanged from R2: no tuning lever in
                    // safe Rust removes it.
                    if rshd[t] == 1 {
                        if pbump + (rlen[t] as usize) > MEM {
                            SENT
                        } else {
                            let s: usize = roff[t] as usize;
                            mem.copy_within(s..s + rlen[t] as usize, pbump);
                            roff[t] = pbump as u8;
                            rshd[t] = 0;
                            mem[pbump] = 0;
                            pbump = pbump + rlen[t] as usize;
                            2
                        }
                    } else {
                        mem[roff[t] as usize] = 0;
                        2
                    }
                }
            },
            _ => {
                if nrec == 0 {
                    SENT
                } else {
                    let t: usize = (a as usize) % nrec;
                    let s: usize = roff[t] as usize;
                    mem[s..s + rlen[t] as usize].iter()
                        .fold(0u64, |x, &b| x.wrapping_mul(31).wrapping_add(b as u64))
                }
            },
        };
        acc = acc.wrapping_mul(31).wrapping_add(v);
    }
    // Fold EVERY record, so a corrupted neighbour cannot hide, and fold each
    // record's ownership flag beside its content.
    for t in 0..nrec {
        let s: usize = roff[t] as usize;
        acc = mem[s..s + rlen[t] as usize].iter()
            .fold(acc, |x, &b| x.wrapping_mul(31).wrapping_add(b as u64));
        acc = acc.wrapping_mul(31).wrapping_add(rshd[t] as u64);
    }
    acc.wrapping_mul(31).wrapping_add(nrec as u64)
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
