//! p25 CONTROL ARM B -- **the ATTRIBUTION arm.** `arm_safe_ptr.rs` with the ONE
//! mutation the saved borrow cannot survive replaced by the SENT fold the same
//! file already writes when its capacity guard fails. MUST COMPILE.
//!
//! ⚠ Everything else is character-identical, including the saved `&u8` and the
//! read through it. So if this compiles and `arm_safe_ptr.rs` does not, the
//! diagnostic is caused by **the push**, not by "safe Rust dislikes saved
//! references" -- which is the claim `../spec.md` makes and the one a reader
//! would otherwise have to take on trust. p34's `safe_arms.py` does the same
//! thing to its own DUP arm.
#![allow(dead_code, unused_variables, unused_mut)]

const MAXCAP: usize = 64;
const SENT: u64 = 251;

pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    if len < 4 {
        return 0;
    }
    let nops: usize = buf[off] as usize + 256 * (buf[off + 1] as usize) + 65536 * (buf[off + 2]
        as usize) + 16777216 * (buf[off + 3] as usize);
    let mut toks: Vec<u8> = Vec::new();
    let mut strs: Vec<u8> = Vec::new();
    let mut cur: Option<&u8> = None;
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
            if toks.len() < MAXCAP {
                // THE EDITED LINES, and the only ones: the push is gone and the
                // rejected-op fold this file already writes takes its place.
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else if c % 4 == 1 {
            if strs.len() < MAXCAP {
                strs.push(a);
                acc = acc.wrapping_mul(31).wrapping_add(a as u64);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else if c % 4 == 2 {
            if toks.len() > 0 {
                let curi = (a as usize) % toks.len();
                cur = Some(&toks[curi]);
                acc = acc.wrapping_mul(31).wrapping_add(2);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else {
            match cur {
                Some(r) => {
                    acc = acc.wrapping_mul(31).wrapping_add(*r as u64);
                },
                None => {
                    acc = acc.wrapping_mul(31).wrapping_add(SENT);
                },
            }
        }
        o = o + 1;
    }
    acc.wrapping_mul(31).wrapping_add((toks.len() + strs.len()) as u64)
}

fn main() {
    let b = [4u8, 0, 0, 0, 0, 9, 2, 0, 0, 8, 3, 0];
    println!("{}", kernel(&b, 0, b.len()));
}
