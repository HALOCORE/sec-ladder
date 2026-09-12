//! ph53 rung R4 -- unsafe.
//!
//! The allocation is sized to `ce->num_interfaces` and the tail is honestly
//! typed as uninitialised -- `Vec<MaybeUninit<u32>>` -- with a **one-byte
//! per-slot witness**, `[bool; MAXD]`, saying which slots a `FILL` wrote. The
//! window, the slot array and the interface pool are all reached through
//! `get_unchecked`.
//!
//! ⚠⚠⚠ **WHY THERE IS A WITNESS AT ALL, AND IT IS THE ROW'S VERUS-SIDE RESULT
//! RATHER THAN A DESIGN CHOICE.** The faithful unsafe port of `c/kernel.c` has
//! no witness: it scans `0..num_interfaces` and `assume_init()`s every slot,
//! which is exactly `zend_operators.c:1535`. **That program cannot be
//! verified, and not because Verus is weak.** `MaybeUninit::assume_init`'s
//! precondition is `m.mem_contents().is_init()`
//! (`~/tools/verus/vstd/std_specs/maybe_uninit.rs`), and whether slot `i` was
//! written is a property of the **op stream**, i.e. of attacker data. The
//! driver loop is pinned canonical in ../spec.md and calls
//! `kernel(buf, k * stride, stride)` with no test, so there is no call site at
//! which coverage could be established and no `requires` that could carry it.
//! ▶ **So a rung that reproduces the defect is unverifiable, and a rung that
//! verifies does not reproduce it.** The faithful one is measured, Miri'd and
//! put through Verus in `controls/r4_nowitness.rs`, with the error text;
//! `../NOTES.md` §11 has it.
//!
//! ⭐ **AND THE WITNESS IS WHAT THE LADDER IS ABOUT.** R2 answers *"was this
//! slot written?"* with `Option<u32>` -- **8 bytes per slot**, because a `u32`
//! has no niche -- and a discriminant load on every read. This rung answers it
//! with **one byte per slot in a stack array** and a `test`/`jz`. R3 does not
//! answer it at all, because `Vec::len()` already carries it. R1h answers it
//! by zeroing the storage and **still faults**. Four answers to one question,
//! and the row prices them: `../NOTES.md` §8 and §10.
//!
//! ⚠⚠ **THE THREE PRECONDITIONS THE `unsafe` HERE RESTS ON, AND THEY COME
//! FROM THREE DIFFERENT PLACES:**
//!
//!   * `win_get_unchecked(win, j)` rests on `j < win.len()`, which comes from
//!     the driver's `off + len <= buf.len()` plus `cap = (len - 76) / 9` --
//!     the harness's structural precondition, not PHP's.
//!   * `slot_read_unchecked` / `slot_set_unchecked` rest on `i < slots.len()`,
//!     which comes from `slots.len() == n_decl` and the loop bound.
//!   * `MaybeUninit::assume_init()` rests on the slot being INITIALISED, which
//!     comes from `wrote[i]` -- and that is the row's own obligation.
//!   * `pool_get_unchecked(pool, p)` rests on `p < MAXP`, which comes from the
//!     `FILL`s having written `b % n_pool` with `n_pool <= MAXP`. ⚠ **That
//!     fourth one is the PRICE OF THE REPRESENTATION and not part of the C's
//!     obligation**: the C stores a `zend_class_entry *` and needs only that
//!     the pointer be valid; safe Rust cannot store an address in a slot it
//!     owns, so the four Rust rungs store an INDEX (ph45's precedent) and an
//!     index needs a RANGE as well as an initialisedness. ../NOTES.md §11.
//!
//! ⭐⭐ **ONE OF THESE UNSAFE OPERATIONS COSTS A TRUSTED ITEM AND ONE DOES NOT,
//! IN THE SAME LINE, AND THE GATE MAKES THE ROW PAY FOR BOTH ANYWAY.** The
//! pinned vstd has **no spec for `get_unchecked` at all** -- 0 files under
//! `~/tools/verus/vstd/` mention it -- while `assume_init` IS
//! `assume_specification`'d in `std_specs/maybe_uninit.rs` and in ordinary exec
//! code costs nothing. ⛔ But `check.py::_scan_unsafe_sites` requires every
//! `unsafe` token in a Verus source to sit inside an `external_body` body, and
//! 5c-twin then demands a verified twin that cannot exist for a `MaybeUninit`
//! read -- so `verus.rs` folds the two operations into ONE trusted item and
//! this rung matches it. `../NOTES.md` §11.
//!
//! ⚠ R4 and R5 must produce the same machine code; see `../NOTES.md` §10 and
//! ../spec.md's `identity`. The only differences are R5's `verus!` block, its
//! spec/proof items and the `requires`/`ensures` on these wrappers.

use core::mem::MaybeUninit;

#[path = "../../common/driver.rs"]
mod driver;

// ------------------------------------------------------- shared arithmetic --
const MAXD: usize = 16;
const MAXP: usize = 8;
const HDR: usize = 12;
const POOL_OFF: usize = HDR;
const OPS_OFF: usize = POOL_OFF + 8 * MAXP;     // 76
const OP_BYTES: usize = 9;

/// `common-php/emalloc_shim.h:642-648`, reproduced ARITHMETICALLY (§B, §B1.2).
#[inline(always)]
fn tally(n_decl: usize) -> u64 {
    if n_decl == 0 {
        0
    } else {
        let real_size: u64 = ((8 * n_decl as u64) + 7) & !7u64;
        (1u64.wrapping_mul(1000003))
            ^ (1u64.wrapping_mul(1000033))
            ^ (0u64.wrapping_mul(1000037))
            ^ real_size.wrapping_mul(1000039)
    }
}

// ------------------------------------------------------- unchecked access ---
// The three operations verus.rs makes TRUSTED. Same names, same signatures,
// same bodies; there they carry a `requires`/`ensures` pair and here they
// carry this comment.

/// `v[i]` with no bounds check. Sound iff `i < v.len()`.
#[inline(always)]
fn win_get_unchecked(v: &[u8], i: usize) -> u8 {
    unsafe { *v.get_unchecked(i) }
}

/// `v[i].assume_init()` with no bounds check and no initialisedness check.
/// Sound iff `i < v.len()` AND slot `i` was written.
/// ⚠⚠ THE TWO PRECONDITIONS COME FROM DIFFERENT PLACES and only one of them is
/// this row's: `i < v.len()` is the harness's structural precondition and the
/// initialisedness is the defect. ⭐ `assume_init` is the one unsafe operation
/// here that the pinned vstd ALREADY SPECIFIES, so in ordinary exec code it
/// needs no trusted item -- but `harness/check.py::_scan_unsafe_sites` requires
/// every `unsafe` token in a Verus source to sit inside an `external_body`
/// body, and 5c-twin then demands a verified twin that cannot exist. The two
/// operations are folded into one item for that reason, and NOTES.md 11
/// reports it.
#[inline(always)]
fn slot_read_unchecked(v: &Vec<MaybeUninit<u32>>, i: usize) -> u32 {
    unsafe { (*v.get_unchecked(i)).assume_init() }
}

/// `v[i] = x` with no bounds check. Sound iff `i < v.len()`.
#[inline(always)]
fn slot_set_unchecked(v: &mut Vec<MaybeUninit<u32>>, i: usize,
                      x: MaybeUninit<u32>) {
    unsafe { *v.get_unchecked_mut(i) = x };
}

/// `a[i]` with no bounds check. Sound iff `i < MAXP`.
#[inline(always)]
fn pool_get_unchecked(a: &[u64; MAXP], i: usize) -> u64 {
    unsafe { *a.get_unchecked(i) }
}

#[inline(always)]
fn rd32(w: &[u8], o: usize) -> u32 {
    (win_get_unchecked(w, o) as u32)
        | ((win_get_unchecked(w, o + 1) as u32) << 8)
        | ((win_get_unchecked(w, o + 2) as u32) << 16)
        | ((win_get_unchecked(w, o + 3) as u32) << 24)
}

#[inline(always)]
fn rd64(w: &[u8], o: usize) -> u64 {
    (rd32(w, o) as u64) | ((rd32(w, o + 4) as u64) << 32)
}

// ---------------------------------------------------------------- kernel ----

/// `instanceof_function_ex`'s interface loop -- `Zend/zend_operators.c`
/// `:1530-1538`, narrowed. **THE FAULTING CONSUMER.**
#[inline(always)]
fn instanceof_ex(slots: &Vec<MaybeUninit<u32>>, wrote: &[bool; MAXD],
                 pool: &[u64; MAXP], target_id: u64) -> (u64, u64, u64) {
    let n: usize = slots.len();
    let mut examined: u64 = 0;
    let mut i: usize = 0;
    while i < n {
        examined = (i + 1) as u64;
        // ⚠ `wrote` is indexed SAFELY and deliberately: it is this rung's own
        // safety mechanism, and reaching it with `get_unchecked` would make
        // the witness rest on the thing it exists to establish.
        if wrote[i] {
            let p: u32 = slot_read_unchecked(slots, i);
            let id: u64 = pool_get_unchecked(pool, p as usize);
            if id == target_id {
                return (1, id, examined);
            }
        }
        i = i + 1;
    }
    (0, 0, examined)
}

/// `zend_do_inherit_interfaces`'s dedup scan -- `Zend/zend_compile.c:1951`,
/// narrowed. **THE COMPARE-ONLY CONSUMER**: it reads the slot and does not
/// reach the pool at all.
#[inline(always)]
fn inherit_scan(slots: &Vec<MaybeUninit<u32>>, wrote: &[bool; MAXD],
                target: u32) -> usize {
    let n: usize = slots.len();
    let mut i: usize = 0;
    while i < n {
        if wrote[i] {
            let p: u32 = slot_read_unchecked(slots, i);
            if p == target {
                return i;
            }
        }
        i = i + 1;
    }
    n
}

#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    let win: &[u8] = &buf[off..off + len];

    let cap: usize = (len - OPS_OFF) / OP_BYTES;
    let n_decl: usize = (rd32(win, 0) as usize) % (MAXD + 1);
    let n_pool: usize = 1 + (rd32(win, 4) as usize) % MAXP;
    let n_ops: usize = (rd32(win, 8) as usize) % (cap + 1);

    let mut pool: [u64; MAXP] = [0u64; MAXP];
    let mut k: usize = 0;
    while k < n_pool {
        pool[k] = rd64(win, POOL_OFF + 8 * k);
        k = k + 1;
    }

    // zend_compile.c:3747-3748, then phase 1's :2591 n_decl times.
    let mut idx: [usize; MAXD] = [0usize; MAXD];
    let mut num_interfaces: usize = 0;
    let mut d0: usize = 0;
    while d0 < n_decl {
        idx[d0] = num_interfaces;                   // :2591
        num_interfaces = num_interfaces + 1;
        d0 = d0 + 1;
    }

    // phase 2, zend_compile.c:2569-2572. Sized to the COUNT, nothing written.
    // ⭐ `MaybeUninit::uninit()` rather than `Vec::set_len` +
    // `spare_capacity_mut`: that shape is R4's most natural one and the pinned
    // vstd specifies NEITHER of those two, so it is unverifiable at R5 and
    // R4 and R5 must be the same program (../spec.md `identity`).
    let mut slots: Vec<MaybeUninit<u32>> = Vec::with_capacity(num_interfaces);
    let mut u: usize = 0;
    while u < num_interfaces {
        slots.push(MaybeUninit::uninit());
        u = u + 1;
    }
    let mut wrote: [bool; MAXD] = [false; MAXD];

    let mut acc: u64 = 0;
    let mut o: usize = 0;
    while o < n_ops {
        let p: usize = OPS_OFF + OP_BYTES * o;
        let op: u32 = (win_get_unchecked(win, p) as u32) % 3;
        let a: u32 = rd32(win, p + 1);
        let b: u32 = rd32(win, p + 5);
        if op == 0 {
            let d: usize = if n_decl > 0 { (a as usize) % n_decl } else { 0 };
            let pi: u32 = (b % (n_pool as u32)) as u32;
            if n_decl > 0 {
                slot_set_unchecked(&mut slots, idx[d], MaybeUninit::new(pi));
                wrote[idx[d]] = true;
            }
            acc = acc.wrapping_mul(31).wrapping_add(d as u64);
        } else if op == 1 {
            let t: usize = (a as usize) % n_pool;
            let tid: u64 = pool_get_unchecked(&pool, t);
            let (hit, matched, examined) =
                instanceof_ex(&slots, &wrote, &pool, tid);
            acc = acc.wrapping_mul(31).wrapping_add(hit);
            acc = acc.wrapping_mul(31).wrapping_add(matched);
            acc = acc.wrapping_mul(31).wrapping_add(examined);
        } else {
            let t: u32 = (a % (n_pool as u32)) as u32;
            let i: usize = inherit_scan(&slots, &wrote, t);
            acc = acc.wrapping_mul(31)
                     .wrapping_add((i != slots.len()) as u64);
            acc = acc.wrapping_mul(31).wrapping_add(i as u64);
        }
        o = o + 1;
    }

    acc ^ tally(n_decl)
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
    if stride_w >= 76 && stride_w <= n_blob as u64 {
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
