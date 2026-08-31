//! p34 CONTROL ARM: **can safe Rust publish a second reference WITHOUT counting
//! it, by storing a BORROW instead of an `Rc`?** Attempt 2 of 2. Not a rung, and
//! **it is expected NOT TO COMPILE.** Driven by `controls/safe_arms.py`.
//!
//! Attempt 1 (`arm_safe_rc_move.rs`) tried to move the `Rc` out of the stack's
//! own borrow. This one tries the other route: keep the owners in one array and
//! make the STACK hold plain `&Obj` borrows, so that a "second reference" is a
//! second borrow and nothing is counted. That is the closest safe Rust gets to
//! C's `stk[ntop] = t;`.
//!
//! **Expected: a borrow-checker error** -- the stack borrows `objs` immutably
//! while `NEW` needs to write to it, so `objs` cannot be both. `safe_arms.py`
//! asserts the compile FAILS and records the error code; a build that succeeded
//! would refute this row's safe-Rust finding.
//!
//! ⚠ **Why this arm exists beside attempt 1.** A single must-fail arm shows one
//! spelling is rejected; it does not show the SEPARATION is unavailable. The two
//! together cover the two ways a program could hold a second reference at all --
//! own it, or borrow it -- and safe Rust closes both, for two different reasons.

#![forbid(unsafe_code)]

#[path = "../../../common/driver.rs"]
mod driver;

const CAP: usize = 16;
const DLEN: usize = 8;
const SENT: u64 = 251;

pub struct Obj {
    pub rc: usize,
    pub len: usize,
    pub data: [u8; DLEN],
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
    // The owners, and a stack of BORROWS into them. This is C's shape exactly:
    // the object lives somewhere and the stack merely names it.
    let mut objs: Vec<Obj> = Vec::new();
    let mut stk: [Option<&Obj>; CAP] = [None; CAP];
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
                let mut d: [u8; DLEN] = [0u8; DLEN];
                d[0] = a.wrapping_mul(7).wrapping_add(1);
                // error[E0502]/[E0506]: `objs` is borrowed by `stk` and cannot
                // be mutated while those borrows are live.
                objs.push(Obj { rc: 1, len: DLEN, data: d });
                stk[ntop] = Some(&objs[objs.len() - 1]);
                ntop = ntop + 1;
                nnew = nnew + 1;
                acc = acc.wrapping_mul(31).wrapping_add(a as u64);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else if c % 4 == 1 {
            if ntop > 0 && ntop < CAP {
                // THE ATTEMPT: a second reference, published and not counted.
                // As a BORROW this line is exactly `stk[ntop] = t;` in C.
                let t = stk[ntop - 1];
                stk[ntop] = t;
                ntop = ntop + 1;
                acc = acc.wrapping_mul(31).wrapping_add(1);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else if c % 4 == 2 {
            if ntop > 0 {
                ntop = ntop - 1;
                stk[ntop] = None;
                acc = acc.wrapping_mul(31).wrapping_add(2);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else {
            if ntop > 0 {
                let v: u8 = stk[(a as usize) % ntop].unwrap().data[0];
                acc = acc.wrapping_mul(31).wrapping_add(v as u64);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        }
        o = o + 1;
    }
    acc.wrapping_mul(31).wrapping_add(nnew as u64)
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
