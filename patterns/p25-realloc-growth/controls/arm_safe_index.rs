//! p25 CONTROL ARM D -- **the INDEX port, which COMPILES and HAS NO BUG.**
//!
//! ⚠⚠ **THIS IS THE ROW'S SAFE-RUST RESULT, AND IT IS A FINDING RATHER THAN A
//! FAILURE.** The catalogue already records it, so it is here to stop anybody
//! rediscovering it as new: `realloc` COPIES, so after a growth `toks[curi]`
//! names the same element the interior pointer named. The safe port is not
//! "prevented from having the bug" -- **it does not have one**, and it is
//! character-for-character what `c/kernel_hardened.c` computes.
//!
//! `safe_arms.py` feeds this program the SHIPPED adversarial windows as hex and
//! compares its answer against `../model.py::parse_fold` on the same bytes, so
//! the claim is a measurement over the inputs on which R1 reads retired storage,
//! not an argument.
//!
//! It takes the window as hex on the command line rather than reading a `.bin`,
//! so it depends on no driver and leaves no blob behind
//! (`.memory/00-environment.md` constraint 6).

const MAXCAP: usize = 64;
const SENT: u64 = 251;

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
                curi = (a as usize) % toks.len();
                have = true;
                acc = acc.wrapping_mul(31).wrapping_add(2);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else {
            if have {
                // THE READ, and it is correct BY CONSTRUCTION: `realloc` copied,
                // so this is the element the interior pointer named.
                let v: u8 = toks[curi];
                acc = acc.wrapping_mul(31).wrapping_add(v as u64);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        }
        o = o + 1;
    }
    acc.wrapping_mul(31).wrapping_add((toks.len() + strs.len()) as u64)
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.len() < 2 {
        eprintln!("usage: arm_safe_index <hex-window>");
        std::process::exit(2);
    }
    let h = args[1].as_bytes();
    let mut b: Vec<u8> = Vec::new();
    let mut i = 0usize;
    while i + 1 < h.len() {
        let hi = (h[i] as char).to_digit(16).expect("bad hex");
        let lo = (h[i + 1] as char).to_digit(16).expect("bad hex");
        b.push((hi * 16 + lo) as u8);
        i += 2;
    }
    let n = b.len();
    println!("{}", kernel(&b, 0, n));
}
