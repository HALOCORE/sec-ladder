//! p49 rung R2 -- safe Rust, naive.
//!
//! ⚠⚠ **THE ROW'S SAFE-RUST RESULT IS THAT SAFE RUST OFFERS BOTH THE BUG AND
//! THE REPAIR, AND WHICH ONE YOU GET IS A CHOICE OF CONTAINER.** That is the
//! opposite of `p34`, where safe Rust cannot express the bug at all, and it is
//! why `../controls/safe_arms.py` builds THREE ports rather than one:
//!
//!   1. **the index arena, shipped here.** Content lives in one `[u8; MEM]` and a
//!      record names a byte offset into it. This is C's representation, arrived
//!      at because it is the natural safe one for a pool, and it can express
//!      **both** semantics: this rung writes the safe one and
//!      `../controls/rust_bug.py` writes the buggy one, in safe Rust, with no
//!      `unsafe` anywhere. **The borrow checker has nothing to say: the alias is
//!      an integer.**
//!   2. `Rc<RefCell<Buf>>` -- an idiomatic shared mutable buffer (`Buf` carries
//!      the width as a field, so the two `Rc` arms differ in ONE type and
//!      nothing else). **Reproduces `c/kernel.c` bit for bit on all nine
//!      inputs**, safely, because `RefCell` is exactly the "shared and mutable"
//!      the pattern is about and the runtime borrow check passes: there is only
//!      ever one borrow at a time.
//!   3. `Rc<Buf>` with `Rc::make_mut`. ⚠⚠ **THE SAFETY LINE IS THE STANDARD
//!      LIBRARY'S**: `make_mut` IS copy-on-write -- it clones when the strong
//!      count exceeds one and hands back a unique reference -- so the repair is
//!      spelled by a library call and cannot be forgotten. It reproduces
//!      `c/kernel_hardened.c` bit for bit on all nine inputs. **That is the only
//!      one of the three in which the safe language rules the bug out**, and it
//!      does it with an API choice rather than with the type system.
//!
//! `CLAUDE.md` rule 6: *"safe Rust reproduces the bug bit-identically" is a
//! FINDING, never a kill.* Here it is the finding, it is measured in three
//! arms, and it is the reason this row's shipped R2 is the INDEX arena: the
//! index arena is the representation all seven rungs can share, so the ladder
//! compares like with like and the `Rc` arms are priced beside it.
//!
//! Naive in the three places R3 tunes: the op walk is a cursor and an `if`
//! chain, the dedup lookup is a `while` with an early `break`, and every index
//! is a plain `mem[i]` / `buf[off + p]`, so rustc emits its own bounds check on
//! top of the guard the algorithm already has. ../NOTES.md 5 is what that costs.
//!
//! Wrapping arithmetic is spelled `wrapping_mul` / `wrapping_add` because
//! `-C debug-assertions=on` would otherwise panic on the fold, and the C rungs
//! wrap by definition (C99 6.2.5p9).

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

/// A content byte. The string a record holds is `cbyte(key,0) ..
/// cbyte(key,w-1)`, so the pair `(key, w)` names the string and nothing else
/// does -- which is why the dedup table's `(ekey, elen)` comparison is an EXACT
/// content comparison and not a hash with a collision story.
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
    let mut p: usize = 4;
    let mut o: usize = 0;
    while o < nops {
        if len - p < 2 {
            break;
        }
        let c: u8 = buf[off + p];
        let a: u8 = buf[off + p + 1];
        p = p + 2;
        let w: u8 = 1 + a % MAXW;
        let key: u8 = a % NKEY;
        let v: u64 = if c % 4 == 0 || c % 4 == 1 {
            if nrec >= NREC {
                SENT
            } else if w < THRESH {
                // THE DEDUP LOOKUP, and the branch is a real test: `w` comes
                // from the file, so this arm and the one below are both live.
                let mut k: usize = 0;
                while k < nent {
                    if ekey[k] == key && elen[k] == w {
                        break;
                    }
                    k = k + 1;
                }
                if k == nent {
                    if nent >= NENT || abump + (w as usize) > ARENA {
                        SENT
                    } else {
                        let mut j: u8 = 0;
                        while j < w {
                            mem[abump + j as usize] = cbyte(key, j);
                            j = j + 1;
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
                } else {
                    // A DEDUP HIT: the new record BORROWS the buffer an earlier
                    // record already holds. Correct, intended, and the contract.
                    roff[nrec] = eoff[k];
                    rlen[nrec] = w;
                    rshd[nrec] = 1;
                    nrec = nrec + 1;
                    a as u64
                }
            } else {
                if pbump + (w as usize) > MEM {
                    SENT
                } else {
                    let mut j: u8 = 0;
                    while j < w {
                        mem[pbump + j as usize] = cbyte(key, j);
                        j = j + 1;
                    }
                    roff[nrec] = pbump as u8;
                    rlen[nrec] = w;
                    rshd[nrec] = 0;
                    pbump = pbump + w as usize;
                    nrec = nrec + 1;
                    a as u64
                }
            }
        } else if c % 4 == 2 {
            if nrec == 0 {
                SENT
            } else {
                let t: usize = (a as usize) % nrec;
                // THE SAFETY LINE. Is this buffer mine to write? c/kernel.c
                // omits this whole block; every Rust rung has it, because every
                // Rust rung computes the CHECKED answer.
                if rshd[t] == 1 {
                    if pbump + (rlen[t] as usize) > MEM {
                        SENT
                    } else {
                        let mut j: u8 = 0;
                        while j < rlen[t] {
                            mem[pbump + j as usize] = mem[roff[t] as usize + j as usize];
                            j = j + 1;
                        }
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
        } else {
            if nrec == 0 {
                SENT
            } else {
                let t: usize = (a as usize) % nrec;
                let mut x: u64 = 0;
                let mut j: u8 = 0;
                while j < rlen[t] {
                    x = x.wrapping_mul(31).wrapping_add(mem[roff[t] as usize + j as usize] as u64);
                    j = j + 1;
                }
                x
            }
        };
        acc = acc.wrapping_mul(31).wrapping_add(v);
        o = o + 1;
    }
    // Fold EVERY record, so a corrupted neighbour cannot hide, and fold each
    // record's ownership flag beside its content: `rshd[t]` is this kernel's
    // reduction of the port's `"interned":true/false` field.
    let mut t: usize = 0;
    while t < nrec {
        let mut j: u8 = 0;
        while j < rlen[t] {
            acc = acc.wrapping_mul(31).wrapping_add(mem[roff[t] as usize + j as usize] as u64);
            j = j + 1;
        }
        acc = acc.wrapping_mul(31).wrapping_add(rshd[t] as u64);
        t = t + 1;
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
