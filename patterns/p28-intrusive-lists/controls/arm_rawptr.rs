//! p28 CONTROLS -- **the faithful RAW-POINTER port of both C arms**, in unsafe
//! Rust, with the two intrusive link sets stored as `*mut Obj` INSIDE the
//! object exactly as `c/kernel.c` stores them.
//!
//! Built and run by `controls/rust_arms.py`. Not a rung, not in the matrix, not
//! measured.
//!
//! ⚠⚠ **WHY IT EXISTS.** The shipped `unsafe.rs` and `verus.rs` do NOT store the
//! links as pointers: they store SLOT NUMBERS into a table, because that is the
//! representation the Verus proof can carry without the full doubly-linked-list
//! well-formedness argument (`unsafe.rs`'s header says so, and ../NOTES.md 5
//! prices it). That is a real divergence from the C mechanism the row is
//! admitted on, and a divergence disclosed in prose is a divergence nobody has
//! measured. **This file is the measurement.** It answers two questions:
//!
//!   1. does the raw-pointer port AGREE with the shipped rungs on every input?
//!      -- if it does, the slot-table representation changed the proof burden
//!      and not the program;
//!   2. does a DETECTOR see the bug in the raw-pointer port? -- Miri, which the
//!      slot-table rungs cannot exercise for this bug at all, because in them
//!      the stale link is a `u8` and reading a `u8` is never UB.
//!
//! **THE TWO ARMS COME FROM ONE MACRO EXPANSION**, which is the Rust spelling of
//! `controls/arm_body.inc`'s include-twice construction: `kernel_bug` and
//! `kernel_fix` are the same token stream with `$harden` false and true, so
//! *"they differ by the safety line and nothing else"* is true by construction
//! here rather than by inspection.
//!
//! usage: `P28_ARM=bug|fix ./arm_rawptr <input-file>`   (default `bug`)

#[path = "../../../common/driver.rs"]
mod driver;

const NB: usize = 8;
const SLOTS: usize = 48;
const SENT: u64 = 251;

/// The C object, field for field and in the C order: **links first**, which is
/// what `c/kernel.h`'s LAYOUT NOTE is about.
#[repr(C)]
struct Obj {
    lp: *mut Obj,
    ln: *mut Obj,
    hn: *mut Obj,
    hp: *mut Obj,
    key: u8,
    val: u8,
}

macro_rules! p28_kernel {
    ($name:ident, $harden:expr) => {
        #[inline(never)]
        pub fn $name(buf: &[u8], off: usize, len: usize) -> u64 {
            if len < 4 {
                return 0;
            }
            let nops: usize = buf[off] as usize + 256 * (buf[off + 1] as usize)
                + 65536 * (buf[off + 2] as usize) + 16777216 * (buf[off + 3] as usize);
            if nops == 0 {
                return 0;
            }
            let mut bucket: [*mut Obj; NB] = [core::ptr::null_mut(); NB];
            let mut head: *mut Obj = core::ptr::null_mut();
            let mut tail: *mut Obj = core::ptr::null_mut();
            let mut nmade: usize = 0;
            let mut acc: u64 = 0;
            let mut p: usize = 4;
            let mut o: usize = 0;
            while o < nops {
                if len - p < 2 {
                    break;
                }
                let c: u8 = buf[off + p];
                let a: u8 = buf[off + p + 1];
                p += 2;
                let b: usize = (a % NB as u8) as usize;
                unsafe {
                    if c % 4 == 3 {
                        // TRIM
                        if !tail.is_null() {
                            let victim: *mut Obj = tail;
                            if !(*victim).lp.is_null() {
                                (*(*victim).lp).ln = core::ptr::null_mut();
                            } else {
                                head = core::ptr::null_mut();
                            }
                            tail = (*victim).lp;
                            if $harden {
                                // THE SAFETY LINE.
                                let vb: usize = ((*victim).key % NB as u8) as usize;
                                if !(*victim).hp.is_null() {
                                    (*(*victim).hp).hn = (*victim).hn;
                                } else {
                                    bucket[vb] = (*victim).hn;
                                }
                                if !(*victim).hn.is_null() {
                                    (*(*victim).hn).hp = (*victim).hp;
                                }
                            }
                            drop(Box::from_raw(victim));
                            acc = acc.wrapping_mul(31).wrapping_add(3);
                        } else {
                            acc = acc.wrapping_mul(31).wrapping_add(SENT);
                        }
                        o += 1;
                        continue;
                    }
                    // the chain walk, shared by PUT, GET and DEL
                    let mut n: *mut Obj = bucket[b];
                    let mut steps: usize = 0;
                    let mut found: bool = false;
                    while !n.is_null() && steps < SLOTS {
                        steps += 1;
                        if (*n).key == a {
                            found = true;
                            break;
                        }
                        n = (*n).hn;
                    }
                    if c % 4 == 0 {
                        // PUT
                        if found {
                            (*n).val = a.wrapping_mul(7).wrapping_add(1);
                            acc = acc.wrapping_mul(31).wrapping_add(a as u64);
                        } else if nmade < SLOTS {
                            let q: *mut Obj = Box::into_raw(
                                Box::new(Obj {
                                    lp: core::ptr::null_mut(),
                                    ln: head,
                                    hn: bucket[b],
                                    hp: core::ptr::null_mut(),
                                    key: a,
                                    val: a.wrapping_mul(7).wrapping_add(1),
                                }),
                            );
                            if !head.is_null() {
                                (*head).lp = q;
                            } else {
                                tail = q;
                            }
                            head = q;
                            if !bucket[b].is_null() {
                                (*bucket[b]).hp = q;
                            }
                            bucket[b] = q;
                            nmade += 1;
                            acc = acc.wrapping_mul(31).wrapping_add(a as u64);
                        } else {
                            acc = acc.wrapping_mul(31).wrapping_add(SENT);
                        }
                    } else if c % 4 == 1 {
                        // GET
                        if found {
                            acc = acc.wrapping_mul(31).wrapping_add((*n).val as u64);
                        } else {
                            acc = acc.wrapping_mul(31).wrapping_add(SENT);
                        }
                    } else {
                        // DEL
                        if found {
                            if !(*n).hp.is_null() {
                                (*(*n).hp).hn = (*n).hn;
                            } else {
                                bucket[b] = (*n).hn;
                            }
                            if !(*n).hn.is_null() {
                                (*(*n).hn).hp = (*n).hp;
                            }
                            if !(*n).lp.is_null() {
                                (*(*n).lp).ln = (*n).ln;
                            } else {
                                head = (*n).ln;
                            }
                            if !(*n).ln.is_null() {
                                (*(*n).ln).lp = (*n).lp;
                            } else {
                                tail = (*n).lp;
                            }
                            drop(Box::from_raw(n));
                            acc = acc.wrapping_mul(31).wrapping_add(2);
                        } else {
                            acc = acc.wrapping_mul(31).wrapping_add(SENT);
                        }
                    }
                }
                o += 1;
            }
            // the epilogue, through the eviction list, exactly as C walks it
            unsafe {
                let mut n: *mut Obj = head;
                while !n.is_null() {
                    let nx: *mut Obj = (*n).ln;
                    drop(Box::from_raw(n));
                    n = nx;
                }
            }
            acc.wrapping_mul(31).wrapping_add(nmade as u64)
        }
    };
}

p28_kernel!(kernel_bug, false);
p28_kernel!(kernel_fix, true);

fn main() {
    let arm = std::env::var("P28_ARM").unwrap_or_else(|_| "bug".to_string());
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
            let r: u64 = if arm == "fix" {
                kernel_fix(buf, k * stride, stride)
            } else {
                kernel_bug(buf, k * stride, stride)
            };
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    driver::emit(acc);
}
