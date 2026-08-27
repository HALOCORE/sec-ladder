//! p42 rung R4 -- unsafe.
//!
//! R2's algorithm with the `Vec` replaced by a raw allocation and every bounds
//! check removed. **This rung releases the digest on every path, and it does so
//! because the author wrote the release twice.** That is the whole difference
//! between it and the C rung: same obligation, same two exits, and nothing but
//! the author checking that both of them discharge it. `.memory/01-ladder.md`
//! forbids an unsound-by-inspection R4, so the correct one is what ships -- but
//! the shape that makes C's bug possible is present here in full, which is why
//! the boundary this pattern measures runs between R2/R3 and R1/R4 rather than
//! between the languages.
//!
//! The helper bodies below are `vstd::raw_ptr`'s with the ghost arguments
//! deleted, for the reason p27 records: R5 must be byte-identical to this file,
//! R5 calls vstd's, and a body that differs even in inlining attributes moves
//! the `identity` pin.
//!
//! ⚠ **`dig_write` spells the store `*q = b`, NOT `core::ptr::write(q, b)`,
//! and the difference is measured rather than stylistic.** The two are the same
//! operation for a `u8`, but `core::ptr::write` is `#[inline]` and at `-O0`
//! **survives as a CALL** -- `lea RIP,%rdx; movzbl %al,%esi; call
//! core::ptr::write` -- while vstd's `ptr_mut_write`, which R5 uses and which is
//! `#[inline(always)]` over an already-optimised precompiled vstd, becomes a
//! bare `mov %cl,(%rax)`. Two instructions, and `-O0` identity drops from
//! `norel` to `differ`. This is p27's finding (p27/NOTES.md 5) and TASK_104
//! reproduced it by writing it BACKWARDS first: ../NOTES.md 8.
//!
//! SAFETY (1): `off + len <= v.len()` and `1 <= len <= isize::MAX` are the
//!   caller's structural preconditions -- the driver's `win_len_w > 0 &&
//!   win_len_w <= MAXWIN && win_len_w <= n_vals` guard plus `off < nwin`.
//!   Unchecked here; discharged at the call site by Verus in verus.rs.
//! SAFETY (2): `dig_alloc` is called with `size == len >= 1` and `align == 1`,
//!   so the layout is valid and the size is non-zero, which is what
//!   `std::alloc::alloc` requires. It aborts rather than returning null, so
//!   every later use has a live allocation.
//! SAFETY (3): every store and load is at `base + i` with `i < len`, inside the
//!   `len` bytes just allocated. `base + i` cannot wrap: the allocator returned
//!   `base` for a `len`-byte block, so `base + len <= usize::MAX + 1`.
//! SAFETY (4): every byte read back at `base + len - 1 - i` was written by the
//!   first loop, which wrote every `i < len`. Nothing reads uninitialised
//!   memory.
//! SAFETY (5): `dig_free` is called exactly once on every path that reaches
//!   `dig_alloc` -- once on the error path and once on the success path -- and
//!   nothing dereferences `p` afterwards. ⚠ **THIS IS THE PATTERN'S OWN
//!   OBLIGATION AND VERUS DOES NOT DISCHARGE IT.** A `Tracked<Dealloc>` is
//!   AFFINE at the pinned Verus, not linear: dropping one verifies clean, so an
//!   R5 that forgot the error path's `deallocate` would report `0 errors`.
//!   Measured, with a control -- ../NOTES.md 6. So (5) is a comment here and a
//!   comment in R5 too, and that is this pattern's central result.

#[path = "../../common/driver.rs"]
mod driver;

/// The low byte of a well-formed record header. ../spec.md "Payload layout".
const TAG: u64 = 0xA7;
/// The decode constant. Arbitrary and shared by all six rungs.
const MIX: u64 = 0x9E37_79B9_7F4A_7C15;
/// The driver's ceiling on the window length, and therefore on the digest
/// allocation. Outside the measured loop and carried by every rung; R5 needs it
/// to discharge `valid_layout`. See verus.rs's module comment.
const MAXWIN: u64 = 65536;

// `vstd::raw_ptr::allocate` (raw_ptr.rs:908) with the two ghost results
// deleted. A REAL allocation: `std::alloc::alloc`, aborting on null exactly as
// vstd's does, so that the null branch is not a semantic difference between
// this rung and R5.
#[inline(always)]
fn dig_alloc(size: usize, align: usize) -> *mut u8 {
    let layout = unsafe { std::alloc::Layout::from_size_align_unchecked(size, align) };
    let p = unsafe { std::alloc::alloc(layout) };
    if p == core::ptr::null_mut() {
        std::process::abort();
    }
    p
}

// `vstd::raw_ptr::deallocate` (raw_ptr.rs:948) with the two ghost arguments
// deleted. A REAL `free`.
#[inline(always)]
fn dig_free(p: *mut u8, size: usize, align: usize) {
    let layout = unsafe { std::alloc::Layout::from_size_align_unchecked(size, align) };
    unsafe {
        std::alloc::dealloc(p, layout);
    }
}

// The address of digest byte `i`. `with_addr` rather than `add` because it is
// the spelling `vstd::raw_ptr`'s `spec_with_addr` gives R5 an `assume_
// specification` for; `p.add(i)` has no spec at the pinned vstd.
#[inline(always)]
fn dig_at(p: *mut u8, base: usize, i: usize) -> *mut u8 {
    p.with_addr(base + i)
}

// `vstd::raw_ptr::ptr_mut_write` / `ptr_ref` with the permission deleted.
// `*q = b`, not `core::ptr::write(q, b)` -- see the module comment.
#[inline(always)]
fn dig_write(q: *mut u8, b: u8) {
    unsafe {
        *q = b;
    }
}

#[inline(always)]
fn dig_read(q: *mut u8) -> u8 {
    let r: &u8 = unsafe { &*q };
    *r
}

// vstd ships no specification for `<[T]>::get_unchecked`, so R5 wraps it; this
// is the same call without the wrapper's contract.
#[inline(always)]
fn v_get_unchecked(v: &[u64], i: usize) -> u64 {
    unsafe { *v.get_unchecked(i) }
}

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(v: &[u64], off: usize, len: usize) -> u64 {
    let p: *mut u8 = dig_alloc(len, 1);
    let base: usize = p.addr();
    if v_get_unchecked(v, off) & 0xff != TAG {
        // The error path, and the hand-written release the C rung is missing.
        dig_free(p, len, 1);
        return 0;
    }
    let mut run: u64 = 0;
    let mut i: usize = 0;
    while i < len {
        // `q` is bound BEFORE `run` is updated, and `b` is bound before the
        // store, because verus.rs binds them in that order -- R5 has to, since
        // the permission split that licenses the store happens between them.
        // The two are the same program either way, but not the same OBJECT
        // code: folding `dig_at` into the `dig_write` argument list changes
        // LLVM's induction-variable strength reduction, R5 keeps `%r8` as a
        // byte cursor where R4 kept an index, and the `identity` pin drops from
        // `exact` to `differ` on two instructions. Measured, ../NOTES.md 8.
        let q: *mut u8 = dig_at(p, base, i);
        run = run.wrapping_add(v_get_unchecked(v, off + i) ^ MIX);
        let b: u8 = (run >> 24) as u8;
        dig_write(q, b);
        i = i + 1;
    }
    let mut acc: u64 = 0;
    let mut j: usize = 0;
    while j < len {
        let idx: usize = len - 1 - j;
        let q: *mut u8 = dig_at(p, base, idx);
        let b: u8 = dig_read(q);
        acc = acc.wrapping_mul(31).wrapping_add(b as u64);
        j = j + 1;
    }
    dig_free(p, len, 1);
    acc
}

// ---------------------------------------------------------------- driver ----
fn main() {
    let path = driver::arg_path();
    let inp = driver::load(&path);
    let (win_len_w, vals) = driver::head_u64_body(&inp);
    let n_iters: u64 = inp.n_iters;
    // SLB-DRIVER-BEGIN
    let n_vals: usize = vals.len();
    let vs: &[u64] = vals.as_slice();
    let mut acc: u64 = 0;
    if win_len_w > 0 && win_len_w <= MAXWIN && win_len_w <= n_vals as u64 {
        let win_len: usize = win_len_w as usize;
        let nwin: u64 = (n_vals - win_len + 1) as u64;
        let mut it: u64 = 0;
        while it < n_iters {
            let off: usize = ((acc as u128 * nwin as u128) >> 64) as usize;
            let r: u64 = kernel(vs, off, win_len);
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    driver::emit(acc);
}
