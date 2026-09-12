//! ph53 rung R2 -- safe-naive.
//!
//! The mechanical port a working Rust programmer writes first: keep the C's
//! shape -- an array sized to `ce->num_interfaces`, scanned in full by both
//! consumers -- and make the unwritten slot REPRESENTABLE, because safe Rust
//! has no other option. `Vec<Option<u32>>`, `vec![None; n_decl]`, index with
//! `slots[i]`, `while` loops. Zero `unsafe`.
//!
//! ⚠⚠ **READ THIS BEFORE COMPARING THIS RUNG TO R1h.** This rung is NOT a port
//! of `c/kernel_hardened.c`, and it cannot be:
//! `d09cdd9f71f34deab4b99f4e63523fb94164a724` zeroes the array and adds **no
//! consumer guard**, so R1h still NULL-dereferences an unwritten slot at
//! `zend_operators.c:1535`. A safe-Rust rung built to it would have to panic
//! there, and *"a rung that panics is not a translation of the C"*
//! (`.memory-php/02-ladder.md`). So the hardened C rung carries the historical
//! fix and the four Rust rungs carry what is actually memory-safe:
//!
//!     R1    zend_compile.c:2569-2572 as shipped 5.0.0 -- CRASH-158, CWE-824
//!     R1h   + d09cdd9f71f3: `emalloc` + `memset(.., 0, ..)`.  STILL FAULTS,
//!           deterministically, on the dereferencing consumer
//!     R2    `Option<u32>` -- the unwritten slot is a VALUE, and the consumer
//!           cannot reach past it without handling it
//!     R3    `push`-as-you-go -- there is no unwritten slot to represent
//!     R4-5  `MaybeUninit<u32>` + a one-byte-per-slot witness
//!
//! ⭐⭐ **AND THAT IS THIS ROW'S LADDER RESULT, STATED UP FRONT.** R2 is not
//! *"PHP 5.0.5's repair reinvented"*: 5.0.5 zeroes the storage and leaves the
//! consumer unguarded, where `Option` makes the consumer's guard
//! **unskippable** -- `if let Some(p) = slots[i]` is the only way to get at the
//! value at all. What R2 reinvents is 5.0.5's `memset` **plus the guard
//! upstream never added**, and it gets the second half for free from the type.
//! `../NOTES.md` §10.
//!
//! ⚠ **WHAT THIS RUNG PAYS FOR THAT, AND IT IS TWO THINGS, NOT ONE.**
//! `Option<u32>` is **8 bytes** on this platform -- a `u32` has no niche, so
//! the discriminant costs a whole word -- so the `vec![None; n]` fill moves
//! exactly as many bytes as R1h's `memset`, and then **every slot READ costs a
//! discriminant load and a branch that R1h does not pay.** The query loops
//! dominate the fill (`n_ops x n_decl` reads against `n_decl` writes), so do
//! not read this rung's number as a bounds-check tax: `../NOTES.md` §8 reads
//! the decomposition off the disassembly.

#[path = "../../common/driver.rs"]
mod driver;

// ------------------------------------------------------- shared arithmetic --
// Identical text in all four Rust rungs and re-derived independently in
// model.py. See ../spec.md for why each is what it is.

/// `c/kernel.h` `PH53_MAXD` -- the largest `ce->num_interfaces` this row
/// admits, and the bound the window's first head word is reduced modulo.
const MAXD: usize = 16;
/// `c/kernel.h` `PH53_MAXP` -- interfaces in scope. The pool is NOT allocated:
/// at `zend_compile.c:2571` every interface an `implements` clause names is an
/// existing `zend_class_entry`.
const MAXP: usize = 8;
const HDR: usize = 12;
const POOL_OFF: usize = HDR;
const OPS_OFF: usize = POOL_OFF + 8 * MAXP;     // 76
const OP_BYTES: usize = 9;

/// `common-php/emalloc_shim.h:642-648`, reproduced ARITHMETICALLY.
///
/// `PROTOCOL_PHP.md` §B forbids a Rust rung from linking the shim and §B1.2
/// requires the tally in the `u64`, so the rung computes what the C's
/// allocator would have counted. ⭐ **§B1a's precondition HOLDS on this row**:
/// the kernel makes exactly ONE allocation per call and NONE at all when
/// `n_decl == 0`, so this is O(1) in the input and the cross-language column
/// needs no allocator caveat -- unlike `ph64`'s `2n+2`.
///
/// ⭐ And it makes **both arms of `zend_compile.c:2570` visible in the u64**:
/// the dead arm allocates nothing, so the tally is 0.
#[inline(always)]
fn tally(n_decl: usize) -> u64 {
    if n_decl == 0 {
        0
    } else {
        // one `_emalloc` (malloc arm: `php_shim_reset()` wiped the cache), one
        // `_efree`, no cache hit, and `REAL_SIZE(8 * n_decl)` bytes reaching
        // `malloc` (`emalloc_shim.h:217`, `:182`).
        let real_size: u64 = ((8 * n_decl as u64) + 7) & !7u64;
        (1u64.wrapping_mul(1000003))
            ^ (1u64.wrapping_mul(1000033))
            ^ (0u64.wrapping_mul(1000037))
            ^ real_size.wrapping_mul(1000039)
    }
}

#[inline(always)]
fn rd32(w: &[u8], o: usize) -> u32 {
    (w[o] as u32) | ((w[o + 1] as u32) << 8) | ((w[o + 2] as u32) << 16)
        | ((w[o + 3] as u32) << 24)
}

#[inline(always)]
fn rd64(w: &[u8], o: usize) -> u64 {
    (rd32(w, o) as u64) | ((rd32(w, o + 4) as u64) << 32)
}

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md. `#[inline(never)]` only in `isolated` builds, so the
// `whole` builds can inline it the way LTO'd C would.

/// `instanceof_function_ex`'s interface loop -- `Zend/zend_operators.c`
/// `:1530-1538`, narrowed. **THE FAULTING CONSUMER.**
///
/// Returns `(hit, matched_id, examined)`. ⚠ `examined` is set at the TOP of
/// every iteration, unwritten slots included, exactly as the C writes
/// `*examined = i + 1` before looking at the slot.
#[inline(always)]
fn instanceof_ex(slots: &Vec<Option<u32>>, pool: &[u64; MAXP], target_id: u64)
                 -> (u64, u64, u64) {
    let n: usize = slots.len();
    let mut examined: u64 = 0;
    let mut i: usize = 0;
    while i < n {
        examined = (i + 1) as u64;
        // ⭐ THE GUARD THE TYPE FORCES. `zend_operators.c:1535` dereferences
        // the slot with nothing between; here there is no expression that
        // reaches the value without this `if let`.
        if let Some(p) = slots[i] {
            let id: u64 = pool[p as usize];
            if id == target_id {
                return (1, id, examined);
            }
        }
        i = i + 1;
    }
    (0, 0, examined)
}

/// `zend_do_inherit_interfaces`'s dedup scan -- `Zend/zend_compile.c:1951`,
/// narrowed. **THE COMPARE-ONLY CONSUMER**, which reads the slot and does not
/// dereference it. Returns the index it stopped at, or `slots.len()`.
#[inline(always)]
fn inherit_scan(slots: &Vec<Option<u32>>, target: u32) -> usize {
    let n: usize = slots.len();
    let mut i: usize = 0;
    while i < n {
        if let Some(p) = slots[i] {
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
    // ⚠⚠ `idx[k]` is `opline->extended_value` and it is `k` because the count
    // starts at zero. It is written out rather than folded away because the
    // row is about the count moving with nothing written.
    let mut idx: [usize; MAXD] = [0usize; MAXD];
    let mut num_interfaces: usize = 0;
    let mut d0: usize = 0;
    while d0 < n_decl {
        idx[d0] = num_interfaces;                   // :2591
        num_interfaces = num_interfaces + 1;
        d0 = d0 + 1;
    }

    // phase 2, zend_compile.c:2569-2572. Sized to the COUNT.
    // ⭐ `None` is the whole rung: safe Rust cannot have a `Vec` of length n
    // whose elements are uninitialised, so the tail has to be a VALUE.
    let mut slots: Vec<Option<u32>> = vec![None; num_interfaces];

    // phase 3: the op stream. THE BLOB IS THE OPCODE STREAM.
    let mut acc: u64 = 0;
    let mut o: usize = 0;
    while o < n_ops {
        let p: usize = OPS_OFF + OP_BYTES * o;
        let op: u32 = (win[p] as u32) % 3;
        let a: u32 = rd32(win, p + 1);
        let b: u32 = rd32(win, p + 5);
        if op == 0 {
            // ZEND_ADD_INTERFACE's runtime half.
            let d: usize = if n_decl > 0 { (a as usize) % n_decl } else { 0 };
            let pi: u32 = (b % (n_pool as u32)) as u32;
            if n_decl > 0 {
                slots[idx[d]] = Some(pi);
            }
            acc = acc.wrapping_mul(31).wrapping_add(d as u64);
        } else if op == 1 {
            let t: usize = (a as usize) % n_pool;
            let (hit, matched, examined) = instanceof_ex(&slots, &pool, pool[t]);
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

    // teardown -- zend_opcode.c:161-162. The `Vec` is dropped here; the tally
    // below is what stands in for the allocator having seen it.
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
