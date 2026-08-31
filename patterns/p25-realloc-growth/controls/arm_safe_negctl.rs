//! p25 CONTROL ARM C -- **THE NEGATIVE CONTROL, and `TASK_157` deliverable 4
//! demands it by name.**
//!
//! ⚠⚠ **A PROGRAM THAT CANNOT HAVE p25's BUG, AND IT PRINTS THE SAME `E0502`.**
//! There is no container here, nothing grows, nothing is reallocated, and no
//! interior pointer is saved across anything. It is twelve lines with a struct
//! and a `&mut`. If the same error code comes out of this file and out of
//! `arm_safe_ptr.rs`, then **the code carries no information about interior
//! pointers or about `realloc`**, and any claim of the form *"safe Rust rejects
//! p25's bug, look at the E0502"* is unsupported.
//!
//! **FOURTH TIME THIS PROJECT HAS READ A rustc CODE AS DISTINGUISHING WHEN IT
//! WAS NOT:** p25's own `E0502` (`.memory/06-catalogue.md`, seven controls),
//! p28's `E0382`/`E0499`, p34's `E0507`.
//!
//! What p25's safe rungs actually establish is a different and stronger thing:
//! the port that DOES compile -- the index one -- **has no bug at all**, because
//! `realloc` copies. `arm_safe_index.rs` measures that.
#![allow(dead_code)]

struct S {
    v: u32,
}

fn bump(s: &mut S) {
    s.v += 1;
}

fn main() {
    let mut s = S { v: 1 };
    let r = &s.v;
    bump(&mut s);
    println!("{}", *r);
}
