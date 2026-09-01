//! p49 rung R4 -- unsafe.
//!
//! R2's algorithm with every array access unchecked. **What does NOT go away is
//! the safety line**, `rshd[t] == 1` at the one site where the cycle-breaker
//! writes. That is not a bounds check -- `roff[t] + rlen[t] <= MEM` holds in
//! every rung including R1, so no index here can ever be out of range and there
//! is no bounds check to remove there. It is the kernel's SEMANTICS: the
//! hardened cell un-shares before writing and ../spec.md pins that answer. A
//! rung without it would be R1's bug written in Rust rather than an unsafe rung
//! -- and ../controls/rust_bug.py builds exactly that rung, **in SAFE Rust**,
//! because the alias here is an integer and the borrow checker has nothing to
//! say about it.
//!
//! ⚠⚠ **WHAT THIS RUNG'S `unsafe` BUYS IS BOUNDS CHECKS AND NOTHING ELSE, AND
//! THAT IS A RESULT ABOUT THE PATTERN.** `p27`'s and `p29`'s unsafe rungs hold
//! raw pointers to individually allocated records and call `allocate` /
//! `deallocate` by hand -- seven trusted items, two of them the allocation API.
//! **p49 allocates nothing.** Its storage is `[u8; MEM]`, alive for the whole
//! call, so there is no pointer to hold, no `PointsTo` to consume, no `Dealloc`
//! token, and no `global layout` declaration. **TCB: five items**, and all five
//! are the ones every unsafe rung in this project already ships. ../NOTES.md 6
//! counts them.
//!
//! **The pool stays ONE flat byte array with parallel `u8` side tables** rather
//! than R3's iterators and `Option`, because verus.rs's abstract machine carries
//! them as seven `Seq`s and R4 ships R5's exec code. R3's spellings are the R3
//! lever and ../NOTES.md 5 prices them.
//!
//! SAFETY (1): `off + len <= buf.len()` is the caller's structural
//!   precondition. Unchecked here; discharged at the call site in verus.rs.
//! SAFETY (2): `len >= 4` guards the window header.
//! SAFETY (3): the op is read only under `len - p >= 2` with `p <= len`.
//! SAFETY (4): `w = 1 + a % MAXW` is in `1 ..= MAXW` for every `a`, and
//!   `key = a % NKEY` is in `0 ..< NKEY`.
//! SAFETY (5): `nent <= NENT` and `nrec <= NREC` are maintained by the two
//!   capacity guards, so `ekey[nent]`, `elen[nent]`, `eoff[nent]`,
//!   `roff[nrec]`, `rlen[nrec]` and `rshd[nrec]` are written only under
//!   `nent < NENT` / `nrec < NREC`.
//! SAFETY (6): `find` returns a value in `0 ..= nent`, and it is used to index
//!   `eoff` only under `f != nent`, i.e. `f < nent <= NENT`.
//! SAFETY (7): `t = a % nrec` runs only under `nrec > 0`, so `t < nrec <= NREC`.
//! SAFETY (8): **the provenance invariant, and it is the one this row is
//!   about.** For every record `t < nrec`:
//!     * `1 <= rlen[t] <= MAXW`;
//!     * `rshd[t] == 1 ==> roff[t] + rlen[t] <= ARENA` -- a SHARED buffer lives
//!       wholly inside the interning arena;
//!     * `rshd[t] == 0 ==> ARENA <= roff[t] && roff[t] + rlen[t] <= pbump` -- an
//!       OWNED buffer lives wholly inside the private region, below the bump.
//!   Either way `roff[t] + rlen[t] <= MEM`, which is what licenses every
//!   unchecked `mem[..]`. ⚠ **And the first clause is what makes the
//!   copy-on-write copy's source and destination DISJOINT**: `src + w <= ARENA
//!   <= pbump = dst`. In verus.rs that is a `requires` on `copy_bytes` and it
//!   has to be discharged; see that file's module note.
//! SAFETY (9): **there is no temporal obligation here at all**, and that is the
//!   pattern. The pool is a local array; nothing is allocated, nothing is freed,
//!   nothing dangles, and `rshd[t] == 1` is an OWNERSHIP condition on live
//!   storage rather than a licence to dereference. What the omission costs is a
//!   wrong answer, never undefined behaviour. ../NOTES.md 6b says what that
//!   does to R5.

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

// The unchecked window read. Same accessor every unsafe rung in this project
// ships; in verus.rs it is trusted item 1 of 5.
#[inline(always)]
fn buf_get_unchecked(v: &[u8], i: usize) -> u8 {
    unsafe { *v.get_unchecked(i) }
}

// The unchecked ARRAY read and store, generic over the element type so that the
// pool, the dedup table and the record table share one accessor. verus.rs's
// trusted items 2 and 3.
#[inline(always)]
fn arr_get_unchecked<T: Copy, const N: usize>(v: &[T; N], i: usize) -> T {
    unsafe { *v.get_unchecked(i) }
}

#[inline(always)]
fn arr_set_unchecked<T: Copy, const N: usize>(v: &mut [T; N], i: usize, x: T) {
    unsafe {
        *v.get_unchecked_mut(i) = x;
    }
}

/// A content byte. `(key, w)` names the string; R2's header says why.
#[inline(always)]
fn cbyte(key: u8, j: u8) -> u8 {
    key.wrapping_mul(7).wrapping_add(j.wrapping_mul(13)).wrapping_add(1)
}

/// THE DEDUP LOOKUP. Returns `nent` when the string is absent.
#[inline(always)]
fn find(ekey: &[u8; NENT], elen: &[u8; NENT], nent: usize, key: u8, w: u8) -> usize {
    let mut k: usize = 0;
    while k < nent {
        if arr_get_unchecked(ekey, k) == key && arr_get_unchecked(elen, k) == w {
            break;
        }
        k = k + 1;
    }
    k
}

/// Materialise a string into the pool.
#[inline(always)]
fn fill(mem: &mut [u8; MEM], base: usize, key: u8, w: u8) {
    let mut j: u8 = 0;
    while j < w {
        arr_set_unchecked(mem, base + j as usize, cbyte(key, j));
        j = j + 1;
    }
}

/// THE COPY-ON-WRITE COPY. `dst` and `src` name DISJOINT ranges -- SAFETY (8).
#[inline(always)]
fn copy_bytes(mem: &mut [u8; MEM], dst: usize, src: usize, w: u8) {
    let mut j: u8 = 0;
    while j < w {
        let x: u8 = arr_get_unchecked(mem, src + j as usize);
        arr_set_unchecked(mem, dst + j as usize, x);
        j = j + 1;
    }
}

/// Fold a string out of the pool.
#[inline(always)]
fn fold_bytes(mem: &[u8; MEM], base: usize, w: u8, acc: u64) -> u64 {
    let mut j: u8 = 0;
    let mut x: u64 = acc;
    while j < w {
        x = x.wrapping_mul(31).wrapping_add(arr_get_unchecked(mem, base + j as usize) as u64);
        j = j + 1;
    }
    x
}

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    if len < 4 {
        return 0;
    }
    let nops: usize = buf_get_unchecked(buf, off) as usize + 256 * (buf_get_unchecked(
        buf,
        off + 1,
    ) as usize) + 65536 * (buf_get_unchecked(buf, off + 2) as usize) + 16777216 * (
    buf_get_unchecked(buf, off + 3) as usize);
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
        let c: u8 = buf_get_unchecked(buf, off + p);
        let a: u8 = buf_get_unchecked(buf, off + p + 1);
        p = p + 2;
        let w: u8 = 1 + a % MAXW;
        let key: u8 = a % NKEY;
        let v: u64 = if c % 4 == 0 || c % 4 == 1 {
            if nrec >= NREC {
                SENT
            } else if w < THRESH {
                let f: usize = find(&ekey, &elen, nent, key, w);
                if f == nent {
                    if nent >= NENT || abump + (w as usize) > ARENA {
                        SENT
                    } else {
                        fill(&mut mem, abump, key, w);
                        arr_set_unchecked(&mut ekey, nent, key);
                        arr_set_unchecked(&mut elen, nent, w);
                        arr_set_unchecked(&mut eoff, nent, abump as u8);
                        arr_set_unchecked(&mut roff, nrec, abump as u8);
                        arr_set_unchecked(&mut rlen, nrec, w);
                        arr_set_unchecked(&mut rshd, nrec, 1);
                        nent = nent + 1;
                        abump = abump + w as usize;
                        nrec = nrec + 1;
                        a as u64
                    }
                } else {
                    let e: u8 = arr_get_unchecked(&eoff, f);
                    arr_set_unchecked(&mut roff, nrec, e);
                    arr_set_unchecked(&mut rlen, nrec, w);
                    arr_set_unchecked(&mut rshd, nrec, 1);
                    nrec = nrec + 1;
                    a as u64
                }
            } else {
                if pbump + (w as usize) > MEM {
                    SENT
                } else {
                    fill(&mut mem, pbump, key, w);
                    arr_set_unchecked(&mut roff, nrec, pbump as u8);
                    arr_set_unchecked(&mut rlen, nrec, w);
                    arr_set_unchecked(&mut rshd, nrec, 0);
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
                // THE SAFETY LINE. c/kernel.c omits this whole block.
                if arr_get_unchecked(&rshd, t) == 1 {
                    let rl: u8 = arr_get_unchecked(&rlen, t);
                    if pbump + (rl as usize) > MEM {
                        SENT
                    } else {
                        let ro: u8 = arr_get_unchecked(&roff, t);
                        copy_bytes(&mut mem, pbump, ro as usize, rl);
                        arr_set_unchecked(&mut roff, t, pbump as u8);
                        arr_set_unchecked(&mut rshd, t, 0);
                        arr_set_unchecked(&mut mem, pbump, 0);
                        pbump = pbump + rl as usize;
                        2
                    }
                } else {
                    let ro: u8 = arr_get_unchecked(&roff, t);
                    arr_set_unchecked(&mut mem, ro as usize, 0);
                    2
                }
            }
        } else {
            if nrec == 0 {
                SENT
            } else {
                let t: usize = (a as usize) % nrec;
                let ro: u8 = arr_get_unchecked(&roff, t);
                let rl: u8 = arr_get_unchecked(&rlen, t);
                fold_bytes(&mem, ro as usize, rl, 0)
            }
        };
        acc = acc.wrapping_mul(31).wrapping_add(v);
        o = o + 1;
    }
    // Fold EVERY record, so a corrupted neighbour cannot hide, and fold each
    // record's ownership flag beside its content.
    let mut t: usize = 0;
    while t < nrec {
        let ro: u8 = arr_get_unchecked(&roff, t);
        let rl: u8 = arr_get_unchecked(&rlen, t);
        acc = fold_bytes(&mem, ro as usize, rl, acc);
        acc = acc.wrapping_mul(31).wrapping_add(arr_get_unchecked(&rshd, t) as u64);
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
