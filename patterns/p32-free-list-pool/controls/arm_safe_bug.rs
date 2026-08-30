// p32 CONTROLS -- the SAFE RUST arm of the storage experiment, kernel for
// kernel with `../safe_naive.rs` and with `harden` selecting whether the safety
// line is there.
//
// ⚠⚠ **THIS FILE IS A CONTROL AND NOT A RUNG**, and the arm that matters
// is `bug`. The shipped safe rungs (`../safe_naive.rs`, `../safe_tuned.rs`)
// carry the safety line and are CORRECT. This one deletes it, under
// `#![forbid(unsafe_code)]`, and the question it answers is the one that was
// used TWICE to refuse this row:
//
//     does safe Rust reproduce the buggy C bit for bit?
//
// It does, on every input and on both arms -- `storage_arms.py` measures it --
// and under the corrected, C-side-only admission bar that is the row's HEADLINE
// (`CLAUDE.md` rule 6, RECAP findings 53 and 54). There is nothing for safe
// Rust to catch: the pool is `[u8; SLOTS * BLK]`, nothing is allocated, nothing
// is dropped, every index is in range, and `#![forbid(unsafe_code)]` is
// satisfied while the answer is wrong and two handles alias one block.
//
// Build: ~/.cargo/bin/rustc -O --edition 2021 -o safe arm_safe_bug.rs
// Run:   ./safe <bug|fix> <hex>
#![forbid(unsafe_code)]

const SLOTS: usize = 8;
const BLK: usize = 4;
const NREG: usize = 8;
const NIL: u8 = 255;
const SENT: u64 = 251;

fn kernel(buf: &[u8], off: usize, len: usize, harden: bool) -> u64 {
    if len < 4 {
        return 0;
    }
    let nops: usize = buf[off] as usize
        + 256 * (buf[off + 1] as usize)
        + 65536 * (buf[off + 2] as usize)
        + 16777216 * (buf[off + 3] as usize);
    if nops == 0 {
        return 0;
    }
    let mut pool = [0u8; SLOTS * BLK];
    let mut nx = [0u8; SLOTS];
    let mut gen = [0u32; SLOTS];
    let mut regs = [NIL; NREG];
    let mut regg = [0u32; NREG];
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
            if freehead == NIL {
                SENT
            } else {
                let s: usize = freehead as usize;
                freehead = nx[s];
                pool[s * BLK] = a;
                pool[s * BLK + 1] = a.wrapping_mul(7).wrapping_add(1);
                regs[r] = s as u8;
                let gs: u32 = gen[s];
                regg[r] = gs;
                nalloc = nalloc + 1;
                (s as u64).wrapping_add((gs as u64).wrapping_mul(8))
            }
        } else {
            let h: u8 = regs[r];
            let g: u32 = regg[r];
            // THE SAFETY LINE. `harden == false` is c/kernel.c's bug, written in
            // safe Rust, and nothing in the language notices.
            if h == NIL {
                SENT
            } else if harden && gen[h as usize] != g {
                SENT
            } else if c % 4 == 1 {
                gen[h as usize] = gen[h as usize].wrapping_add(1);
                nx[h as usize] = freehead;
                freehead = h;
                1
            } else if c % 4 == 2 {
                pool[h as usize * BLK + 1] as u64
            } else {
                pool[h as usize * BLK + 1] = a.wrapping_mul(13).wrapping_add(3);
                3
            }
        };
        acc = acc.wrapping_mul(31).wrapping_add(v);
        o = o + 1;
    }
    acc.wrapping_mul(31).wrapping_add(nalloc as u64)
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.len() != 3 {
        eprintln!("usage: safe <bug|fix> <hex>");
        std::process::exit(2);
    }
    let harden = args[1] == "fix";
    let hex = &args[2];
    let buf: Vec<u8> = (0..hex.len() / 2)
        .map(|i| u8::from_str_radix(&hex[2 * i..2 * i + 2], 16).unwrap())
        .collect();
    let n = buf.len();
    println!("{} {}", args[1], kernel(&buf, 0, n, harden));
}
