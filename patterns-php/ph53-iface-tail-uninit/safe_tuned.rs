//! ph53 rung R3 -- safe-tuned.
//!
//! ⭐⭐ **THIS RUNG IS PHP 5.2.0's OWN REPAIR, AND IT IS THE SAFE ONE.** Upstream
//! restructured the whole thing after 5.1: `ce->interfaces = NULL;
//! ce->num_interfaces = 0;` at declaration, and `zend_do_implement_interface`
//! grows the array **one slot at a time at run time** --
//! `erealloc(..., ++current_iface_num)` then
//! `ce->interfaces[ce->num_interfaces++] = iface`. The count and the slots
//! written move together, so *"sized to the count with the tail never
//! written"* is not expressible any more. That is exactly what
//! `Vec::push` does, and it is what this rung does.
//!
//!     R2  `Vec<Option<u32>>`  -- the unwritten slot is a VALUE, 8 bytes each,
//!                                and every read costs a discriminant branch
//!     R3  `Vec<u32>` + push   -- THERE IS NO UNWRITTEN SLOT TO REPRESENT
//!
//! ⭐ **PREDICTION UNDER TEST** (`TASK_PHP_040_REPORT.md` §5.6): *"R3 is the
//! cheapest rung on the row -- the safe restructuring is also the fastest,
//! because it deletes both the discriminant check and the zeroing."*
//! `../NOTES.md` §8 reports whether it held.
//!
//! ⚠ **WHAT `Vec::with_capacity(n_decl)` BUYS AND WHAT IT COSTS.** 5.2.0
//! `erealloc`s on **every** `ADD_INTERFACE`, i.e. O(n) allocations per
//! declaration; this rung reserves the count once and pushes into it, i.e.
//! **one** allocation, the same count as R1 and R1h and as every other rung
//! here. That keeps `PROTOCOL_PHP.md` §B1a's precondition true of the whole
//! row rather than of five sixths of it, which is what lets the cross-language
//! column go out without an allocator caveat. It is declared in ../spec.md's
//! `provenance.divergences` rather than left to be noticed.
//!
//! ⚠ **AND IT DOES NOT ANSWER THE SAME AS THE OTHER FIVE RUNGS EVERYWHERE.**
//! On a benign window the `FILL`s cover `0..n_decl-1` in increasing order, so
//! arrival order is index order and `slots.len() == n_decl` before the first
//! query -- every rung agrees, which is what `check.py` stage 2 checks. On
//! `inputs/adversarial-cmp.bin` the coverage is incomplete and **this rung
//! examines ONE slot where the other five examine two**, because its array is
//! only as long as the fills it saw. `check.py` stage 4 records that, and
//! `inputs/adversarial-covered.bin` is the must-NOT-fire control beside it.

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
/// O(1) in the input, so §B1a's precondition holds and this row's
/// cross-language column needs no allocator caveat.
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

/// `instanceof_function_ex`'s interface loop -- `Zend/zend_operators.c`
/// `:1530-1538`, narrowed. **THE FAULTING CONSUMER.**
///
/// ⭐ No `if let` and no discriminant: the loop bound IS the witness. Every
/// element of `slots` was written, by construction.
#[inline(always)]
fn instanceof_ex(slots: &Vec<u32>, pool: &[u64; MAXP], target_id: u64)
                 -> (u64, u64, u64) {
    let n: usize = slots.len();
    let mut examined: u64 = 0;
    let mut i: usize = 0;
    while i < n {
        examined = (i + 1) as u64;
        let id: u64 = pool[slots[i] as usize];
        if id == target_id {
            return (1, id, examined);
        }
        i = i + 1;
    }
    (0, 0, examined)
}

/// `zend_do_inherit_interfaces`'s dedup scan -- `Zend/zend_compile.c:1951`,
/// narrowed. **THE COMPARE-ONLY CONSUMER.**
#[inline(always)]
fn inherit_scan(slots: &Vec<u32>, target: u32) -> usize {
    let n: usize = slots.len();
    let mut i: usize = 0;
    while i < n {
        if slots[i] == target {
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
    while k < n_pool {
        pool[k] = rd64(win, POOL_OFF + 8 * k);
        k = k + 1;
    }

    // zend_compile.c:3747-3748, and then phase 1 -- which in 5.2.0 is ONE
    // STATEMENT, not a loop.
    // ⚠⚠ THERE IS NO `idx[]` IN THIS RUNG, AND ITS ABSENCE IS PART OF THE
    // REPAIR. 5.0.0's `zend_do_implements_interface` writes
    // `opline->extended_value = CG(active_class_entry)->num_interfaces++;`
    // (`:2591`) -- a COMPILE-TIME index the runtime half then has to honour.
    // 5.2.0 deleted the coupling and left `num_interfaces++` alone, which is
    // also, later and independently, exactly what the corpus's own (excluded)
    // `be8daf1f47fa` did in 2008. So this rung carries no per-declaration
    // index array and its phase 1 is O(1) where every other rung's is
    // O(n_decl). Declared in ../spec.md's `provenance.divergences` and priced
    // in ../NOTES.md §8 rather than left to be noticed.
    let num_interfaces: usize = n_decl;

    // phase 2, zend_compile.c:2569-2572 -- and there is nothing to zero.
    // ⭐ The capacity is the count; the LENGTH is the slots written.
    let mut slots: Vec<u32> = Vec::with_capacity(num_interfaces);

    let mut acc: u64 = 0;
    let mut o: usize = 0;
    while o < n_ops {
        let p: usize = OPS_OFF + OP_BYTES * o;
        let op: u32 = (win[p] as u32) % 3;
        let a: u32 = rd32(win, p + 1);
        let b: u32 = rd32(win, p + 5);
        if op == 0 {
            // 5.2.0's `ce->interfaces[ce->num_interfaces++] = iface`. `d` is
            // still computed and folded, because the u64 is the same function
            // of the blob on every rung; what this rung does NOT do is use it
            // as a destination.
            let d: usize = if n_decl > 0 { (a as usize) % n_decl } else { 0 };
            let pi: u32 = (b % (n_pool as u32)) as u32;
            if slots.len() < num_interfaces {
                slots.push(pi);
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
