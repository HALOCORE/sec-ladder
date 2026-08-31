//! p25 CONTROL ARM A -- **safe Rust holding `&toks[curi]` across `toks.push(a)`.**
//! MUST NOT COMPILE.
//!
//! This is the spelling `c/kernel.c` uses, transliterated: take a reference into
//! the token vector, keep parsing, push, then read through the saved reference.
//! The borrow checker refuses it, and `safe_arms.py` records the error code.
//!
//! ⚠⚠ **THE ERROR CODE IS NOT THE EVIDENCE.** `arm_safe_negctl.rs` is a program
//! that CANNOT have p25's bug -- no container, no growth, no saved interior
//! pointer -- and it prints the SAME code with the SAME message.
//! `arm_safe_ptr_nopush.rs` is the attribution arm: the same file with the push
//! deleted, which COMPILES, so the diagnostic really is caused by the two lines
//! that were edited and not by the shape of the program.
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
                // THE MUTATION the saved borrow cannot survive.
                toks.push(a);
                acc = acc.wrapping_mul(31).wrapping_add(a as u64);
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
                // THE INTERIOR POINTER, c/kernel.c's `cur = &toks[curi];`.
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
