//! p49 CONTROL ARM: **`Rc<Buf>` with `Rc::make_mut` -- the repair, supplied by
//! the STANDARD LIBRARY.**
//!
//! ⚠⚠ **THIS ARM REPRODUCES `c/kernel_hardened.c` BIT FOR BIT, AND IT CONTAINS
//! NO SAFETY LINE.** It is `arm_rc_refcell.rs` with `Rc<RefCell<Buf>>` changed
//! to `Rc<Buf>`, the write spelled `Rc::make_mut(&mut recs[t].0).data[0] = 0;`
//! -- **and the 20-line accounting block below, which `arm_rc_refcell.rs` does
//! not have.**
//!
//! ⚠ **THE SENTENCE THAT SAID *"with ONE TYPE CHANGED"* FULL STOP IS
//! WITHDRAWN** (`TASK_162` MAJOR 3, decomposed at `TASK_163`). Strip the block
//! and this arm matches NEITHER C rung on all five discriminating inputs; keep
//! only the flag clear and it matches `R1h` 4 of 5; keep only the budget, 1 of
//! 5. ✅ **What IS true, and it is the better claim:** with the block deleted,
//! this arm and `arm_rc_refcell.rs` are literally one type apart and they still
//! disagree on exactly those five inputs and agree on the other four -- **so
//! the TYPE carries the safety and the BLOCK carries the C kernel's
//! accounting.** `../NOTES.md` 3e.
//!
//! `Rc::make_mut` **IS** copy-on-write: it clones the value when the strong
//! count exceeds one and hands back a unique `&mut`. So the mutation cannot
//! reach a buffer another record (or the dedup table) still names, and the bug
//! is not expressible in this port at all. ✅ **That is the only one of this
//! row's three safe-Rust ports in which the language rules the bug out, and it
//! does it with an API CHOICE rather than with the type system**: swap `Rc<T>`
//! for `Rc<RefCell<T>>` and the same program is `c/kernel.c`.
//!
//! ⚠ **The one explicit test below is a BUDGET test and not a safety test, and
//! saying so matters.** This kernel's copy-on-write draws its private copy from
//! a fixed pool and REFUSES when the pool is exhausted, so to reproduce
//! `c/kernel_hardened.c`'s answer this arm has to ask `Rc::strong_count(..) > 1`
//! and charge the copy against the same budget. **A real `Rc`-based pool would
//! have no such test** -- it would allocate -- and would then have no refusal
//! path either. The safety is `make_mut`'s; the accounting is this benchmark's.
//!
//! Not a rung: it is never built by `harness/build.py` and never measured.

#[path = "../../../common/driver.rs"]
mod driver;

use std::rc::Rc;

const MEM: usize = 64;
const ARENA: usize = 20;
const NENT: usize = 8;
const NREC: usize = 12;
const NKEY: u8 = 7;
const MAXW: u8 = 6;
const THRESH: u8 = 4;
const SENT: u64 = 251;

/// One BUFFER. `Clone` is what `Rc::make_mut` needs, and it is the whole of the
/// difference between this arm and `arm_rc_refcell.rs`.
#[derive(Clone)]
pub struct Buf {
    pub len: u8,
    pub data: [u8; MAXW as usize],
}

fn cbyte(key: u8, j: u8) -> u8 {
    key.wrapping_mul(7).wrapping_add(j.wrapping_mul(13)).wrapping_add(1)
}

fn make(key: u8, w: u8) -> Buf {
    let mut d = [0u8; MAXW as usize];
    let mut j: u8 = 0;
    while j < w {
        d[j as usize] = cbyte(key, j);
        j = j + 1;
    }
    Buf { len: w, data: d }
}

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
    let mut table: Vec<(u8, u8, Rc<Buf>)> = Vec::new();
    let mut recs: Vec<(Rc<Buf>, u8)> = Vec::new();
    let mut arena_used: usize = 0;
    let mut priv_used: usize = 0;
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
            if recs.len() >= NREC {
                SENT
            } else if w < THRESH {
                match table.iter().position(|e| e.0 == key && e.1 == w) {
                    Some(k) => {
                        recs.push((Rc::clone(&table[k].2), 1));
                        a as u64
                    },
                    None => {
                        if table.len() >= NENT || arena_used + (w as usize) > ARENA {
                            SENT
                        } else {
                            let b = Rc::new(make(key, w));
                            table.push((key, w, Rc::clone(&b)));
                            recs.push((b, 1));
                            arena_used = arena_used + w as usize;
                            a as u64
                        }
                    },
                }
            } else if priv_used + (w as usize) > MEM - ARENA {
                SENT
            } else {
                recs.push((Rc::new(make(key, w)), 0));
                priv_used = priv_used + w as usize;
                a as u64
            }
        } else if c % 4 == 2 {
            if recs.is_empty() {
                SENT
            } else {
                let t: usize = (a as usize) % recs.len();
                // The BUDGET test -- NOT the safety test. See the header: the
                // safety is `make_mut`'s, and this arm asks `strong_count` only
                // so that it charges the private copy against the same fixed
                // pool `c/kernel_hardened.c` charges it against, and refuses in
                // the same place.
                let shared: bool = Rc::strong_count(&recs[t].0) > 1;
                let need: usize = recs[t].0.len as usize;
                if shared && priv_used + need > MEM - ARENA {
                    SENT
                } else {
                    if shared {
                        priv_used = priv_used + need;
                        recs[t].1 = 0;
                    }
                    // >>> THE WRITE. `Rc::make_mut` clones when the count
                    // exceeds one, so this `&mut` never names storage anybody
                    // else holds. THE SAFETY LINE IS THE STANDARD LIBRARY'S. <<<
                    Rc::make_mut(&mut recs[t].0).data[0] = 0;
                    2
                }
            }
        } else {
            if recs.is_empty() {
                SENT
            } else {
                let t: usize = (a as usize) % recs.len();
                let b = &recs[t].0;
                let mut x: u64 = 0;
                let mut j: u8 = 0;
                while j < b.len {
                    x = x.wrapping_mul(31).wrapping_add(b.data[j as usize] as u64);
                    j = j + 1;
                }
                x
            }
        };
        acc = acc.wrapping_mul(31).wrapping_add(v);
        o = o + 1;
    }
    let nrec = recs.len();
    for (b, shd) in recs.iter() {
        let mut j: u8 = 0;
        while j < b.len {
            acc = acc.wrapping_mul(31).wrapping_add(b.data[j as usize] as u64);
            j = j + 1;
        }
        acc = acc.wrapping_mul(31).wrapping_add(*shd as u64);
    }
    acc.wrapping_mul(31).wrapping_add(nrec as u64)
}

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
