//! ph53 CONTROL — **the FAITHFUL unsafe port, which cannot be verified.**
//!
//! ⚠⚠⚠ **THIS IS NOT A RUNG AND IT MUST NEVER BECOME ONE.** It is `unsafe.rs`
//! with the `wrote[]` witness deleted: the query loops scan
//! `0..num_interfaces` and `assume_init()` every slot, which is exactly what
//! `Zend/zend_operators.c:1535` does. It therefore **reproduces the defect in
//! Rust** — on a blob whose `QUERY` reaches a slot no `FILL` wrote it reads an
//! uninitialised `u32` and uses it as an unchecked index into an eight-entry
//! pool.
//!
//! `controls/negatives.py` drives it three ways:
//!
//!   * **Verus MUST REFUSE IT.** `MaybeUninit::assume_init`'s precondition is
//!     `m.mem_contents().is_init()` (`~/tools/verus/vstd/std_specs/maybe_uninit.rs`),
//!     and whether slot `i` was written is a property of the OP STREAM, i.e.
//!     of attacker data. `../spec.md`'s driver loop is pinned canonical and
//!     calls `kernel(buf, k * stride, stride)` with no test, so there is no
//!     call site at which coverage could be established and no `requires` that
//!     could carry it. ▶ **A rung that reproduces the defect cannot be
//!     verified and a rung that verifies does not reproduce it**, and that is
//!     the row's Verus-side result rather than a limitation of the prover.
//!   * **Miri MUST REPORT IT** on an uncovered blob and must be **silent on
//!     the measured corpus** — and Miri is the only detector in this tree that
//!     sees the read ITSELF, because an uninitialised read of an in-bounds
//!     slot is CWE-824 and ASan's class is CWE-125.
//!   * **its `Ir` is measured beside the shipped R4's**, so the row can say
//!     what the witness costs instead of asserting that it is cheap.
//!
//! ⚠ Everything else is `unsafe.rs` byte for byte: same decode, same phases,
//! same fold, same trusted accessors, same driver loop. The only deletions are
//! the `wrote` array, its two writes and the two `if wrote[i]` guards.
//!
//! Compiled by `controls/negatives.py`; it is deliberately NOT one of
//! `build.py`'s cells and there is no `RUST_SRC` entry for it.

use core::mem::MaybeUninit;

#[path = "../../../common/driver.rs"]
mod driver;

// ------------------------------------------------------- shared arithmetic --
const MAXD: usize = 16;
const MAXP: usize = 8;
const HDR: usize = 12;
const POOL_OFF: usize = HDR;
const OPS_OFF: usize = POOL_OFF + 8 * MAXP;     // 76
const OP_BYTES: usize = 9;

#[inline(always)]
fn tally(n_decl: usize) -> u64 {
    if n_decl == 0 {
        0
    } else {
        let real_size: u64 = 8 * (n_decl as u64);
        (1000003u64 ^ 1000033u64 ^ 0u64) ^ real_size.wrapping_mul(1000039)
    }
}

// ------------------------------------------------------- unchecked access ---
#[inline(always)]
fn win_get_unchecked(v: &[u8], i: usize) -> u8 {
    unsafe { *v.get_unchecked(i) }
}

#[inline(always)]
fn slot_read_unchecked(v: &Vec<MaybeUninit<u32>>, i: usize) -> u32 {
    unsafe { (*v.get_unchecked(i)).assume_init() }
}

#[inline(always)]
fn slot_set_unchecked(v: &mut Vec<MaybeUninit<u32>>, i: usize,
                      x: MaybeUninit<u32>) {
    unsafe { *v.get_unchecked_mut(i) = x };
}

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

/// `instanceof_function_ex`'s interface loop, with NO WITNESS — this is
/// `zend_operators.c:1534-1535` and nothing between the loop and the read.
#[inline(always)]
fn instanceof_ex(slots: &Vec<MaybeUninit<u32>>, pool: &[u64; MAXP],
                 target_id: u64) -> (u64, u64, u64) {
    let n: usize = slots.len();
    let mut examined: u64 = 0;
    let mut i: usize = 0;
    while i < n {
        examined = (i + 1) as u64;
        // ⚠⚠ THE DEFECT, IN RUST. `assume_init()` on a slot no `FILL` wrote is
        // undefined behaviour, and the u32 that comes out is then used as an
        // unchecked index into an 8-entry array.
        let p: u32 = slot_read_unchecked(slots, i);
        let id: u64 = pool_get_unchecked(pool, p as usize);
        if id == target_id {
            return (1, id, examined);
        }
        i = i + 1;
    }
    (0, 0, examined)
}

/// `zend_do_inherit_interfaces`'s dedup scan, with NO WITNESS.
#[inline(always)]
fn inherit_scan(slots: &Vec<MaybeUninit<u32>>, target: u32) -> usize {
    let n: usize = slots.len();
    let mut i: usize = 0;
    while i < n {
        let p: u32 = slot_read_unchecked(slots, i);
        if p == target {
            return i;
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
    while k < MAXP {
        pool[k] = rd64(win, POOL_OFF + 8 * k);
        k = k + 1;
    }

    let mut idx: [usize; MAXD] = [0usize; MAXD];
    let mut num_interfaces: usize = 0;
    let mut d0: usize = 0;
    while d0 < n_decl {
        idx[d0] = num_interfaces;                   // :2591
        num_interfaces = num_interfaces + 1;
        d0 = d0 + 1;
    }

    let mut slots: Vec<MaybeUninit<u32>> = Vec::with_capacity(num_interfaces);
    let mut u: usize = 0;
    while u < num_interfaces {
        slots.push(MaybeUninit::uninit());
        u = u + 1;
    }

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
            }
            acc = acc.wrapping_mul(31).wrapping_add(d as u64);
        } else if op == 1 {
            let t: usize = (a as usize) % n_pool;
            let tid: u64 = pool_get_unchecked(&pool, t);
            let (hit, matched, examined) = instanceof_ex(&slots, &pool, tid);
            acc = acc.wrapping_mul(31).wrapping_add(hit);
            acc = acc.wrapping_mul(31).wrapping_add(matched);
            acc = acc.wrapping_mul(31).wrapping_add(examined);
        } else {
            let t: u32 = (a % (n_pool as u32)) as u32;
            let i: usize = inherit_scan(&slots, t);
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
