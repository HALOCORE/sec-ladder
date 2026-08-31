//! p34 NEGATIVE CONTROL: **is it the DUPLICATION that safe Rust refuses, or the
//! OWNER MUTATION?** Not a rung, not an attempt at the bug, and **it is expected
//! TO COMPILE AND RUN.** Driven by `controls/safe_arms.py`.
//!
//! `arm_safe_rc_borrow.rs` tries to publish a second reference by storing a
//! plain `&Obj` in the stack array, and rustc rejects it with `E0502`. Until
//! `TASK_156` the row read that rejection as *"a borrow cannot be stored in the
//! stack array because the borrow checker ties it to the array it came from"*
//! — a sentence that was hashed into `spec.md`'s `slb-contract` `why` and is
//! **false** (`TASK_155_REPORT` B1). This file is the control that shows why.
//!
//! **The DUP line, character for character `arm_safe_rc_borrow.rs`'s:**
//!
//! ```text
//!     let t = stk[ntop - 1];
//!     stk[ntop] = t;
//! ```
//!
//! Here the owners are built FIRST and never touched again, so no mutable
//! borrow of `objs` ever coexists with the shared ones — and the same two lines
//! **compile and run**. A second `&Obj` in the stack array is perfectly legal
//! safe Rust.
//!
//! ⚠ **What safe Rust refuses is mutating the owner while the borrows are
//! live**, which in `arm_safe_rc_borrow.rs` is the `objs.push` on the `NEW`
//! path — and which is where a `free` would have to happen. So the borrow route
//! to `p34`'s bug is closed **at the destruction, not at the duplication**.
//!
//! ⚠⚠ **THIS PROGRAM CANNOT HAVE `p34`'s BUG**, which is what makes it a
//! negative control rather than an arm: nothing is ever freed, because the
//! owners outlive every borrow by construction. It is evidence about **where**
//! the borrow checker objects, not about whether the bug is expressible.
//!
//! `safe_arms.py` asserts this COMPILES and that its output is the value
//! derived below; a rejection here would mean the sentence in `spec.md`'s `why`
//! and in `arm_safe_rc_borrow.rs`'s header had become wrong again, in the other
//! direction.

#![forbid(unsafe_code)]

const CAP: usize = 16;
const DLEN: usize = 8;

pub struct Obj {
    pub rc: usize,
    pub len: usize,
    pub data: [u8; DLEN],
}

fn main() {
    // The owners, built once and then FROZEN -- this is the whole difference
    // from `arm_safe_rc_borrow.rs`, which grows `objs` inside the op walk.
    let objs: Vec<Obj> = (0..4u8)
        .map(|i| Obj { rc: 1, len: DLEN, data: [i; DLEN] })
        .collect();

    let mut stk: [Option<&Obj>; CAP] = [None; CAP];
    let mut ntop: usize = 0;

    // NEW: publish the first reference.
    stk[ntop] = Some(&objs[0]);
    ntop = ntop + 1;

    // DUP: publish a SECOND reference and do not count it. `arm_safe_rc_move.rs`
    // cannot spell this at all (`E0507`); as a BORROW it is accepted.
    let t = stk[ntop - 1];
    stk[ntop] = t;
    ntop = ntop + 1;

    // Both entries name the same object, and `rc` is still 1 -- exactly p34's
    // uncounted-alias state. It is harmless HERE only because nothing frees.
    let a = stk[0].unwrap();
    let b = stk[1].unwrap();
    let acc: usize = ntop * 100 + (a.data[0] as usize) * 10 + b.rc;
    println!("{}", acc);
}
