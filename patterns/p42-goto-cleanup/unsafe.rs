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
//! reproduced it by writing it BACKWARDS first: ../NOTES.md 8. ✅ **Re-measured
//! at TASK_110 against this tree, both arms, and both still fire**
//! (`.temp/t110/idprobe.py`).
//!
//! ⚠ **THE FOLD LOOP MOVED AT TASK_110 AND THE ROW'S COMPARATIVE HEADLINE MOVED
//! WITH IT.** This rung used to fold by reverse INDEX -- two induction
//! variables in the fold loop -- and TASK_104 published *"safe-tuned Rust beats
//! unsafe Rust here"* off an R4 side searched at four spellings. TASK_109 found
//! a fifth: a do-while over a descending cursor, which uses nothing the pinned
//! vstd does not already specify, verifies at the same obligation count, and is
//! cheaper than **every** R3 spelling p42 measured. **The sign of `min(R3 found)
//! - min(R4 found)` flips, so the published claim was refuted and the cheaper
//! spelling is what ships.** ../NOTES.md 11b, and read what that section now
//! says about differencing two minima -- it is the construction ../spec.md's own
//! hashed `why` retracts.
//!
//! SAFETY (1): `off + len <= v.len()` and `1 <= len <= isize::MAX` are the
//!   caller's structural preconditions -- the driver's `win_len_w > 0 &&
//!   win_len_w <= MAXWIN && win_len_w <= n_vals` guard plus `off < nwin`.
//!   Unchecked here; discharged at the call site by Verus in verus.rs.
//! SAFETY (2): `dig_alloc` is called with `size == len >= 1` and `align == 1`,
//!   so the layout is valid and the size is non-zero, which is what
//!   `std::alloc::alloc` requires. It aborts rather than returning null, so
//!   every later use has a live allocation.
//! SAFETY (3): every store is at `base + i` with `i < len`, inside the `len`
//!   bytes just allocated. `base + i` cannot wrap: the allocator returned
//!   `base` for a `len`-byte block, so `base + len <= usize::MAX + 1`.
//!   ⚠ **The loads are a DESCENDING CURSOR since TASK_110**, not an index: `q`
//!   starts at `base + len - 1` (in range, because `len >= 1`) and is
//!   decremented only after the `q == p` test fails, so it is never moved below
//!   `base` and never reaches one past the end. That last part is why this
//!   shape is the one that has a verifiable twin at all -- `../NOTES.md` 9a.
//! SAFETY (4): every byte the cursor reads was written by the first loop, which
//!   wrote every `i < len`. The cursor visits exactly `base + len - 1` down to
//!   `base`, so nothing reads uninitialised memory.
//! SAFETY (5): `dig_free` is called exactly once on every path that reaches
//!   `dig_alloc` -- once on the error path and once on the success path -- and
//!   nothing dereferences `p` afterwards. ⚠ **THIS IS THE PATTERN'S OWN
//!   OBLIGATION, AND ON THIS RUNG NOTHING MECHANICAL DISCHARGES IT.** The
//!   backstop here is Miri's leak report at process exit, which is why
//!   `../spec.md` sets `miri.required` and why `controls/miri_seeds.sh` ships a
//!   positive control that deletes this file's error-path release.
//!   ⚠⚠ **AND NOTHING MECHANICAL DISCHARGES IT ON R5 EITHER. THE TASK_110
//!   RETRACTION PRINTED HERE IS ITSELF RETRACTED, AT TASK_118.** From TASK_110
//!   to TASK_118 this note said the sentence *"AND VERUS DOES NOT DISCHARGE
//!   IT"* was false, on the ground that R5 escrows the token in a ghost ledger
//!   whose emptiness is a postcondition. **A leaking R5 satisfies that
//!   postcondition**: one proof line on the error path, `18 verified, 0
//!   errors`, `model.py::leak_bytes` leaked, and the resulting binary is
//!   byte-identical to THIS file with its error-path release deleted
//!   (`md5_fn d3f1194cb10bce2057e0e1f3e28c1e21` at -O3). A privacy-scoped third
//!   encoding, built at TASK_118, fails the same way at `19 verified, 0
//!   errors`. ../NOTES.md 6, ../spec.md `idiom.why`.
//!   ⚠ **The affineness half stands**: a `Tracked<Dealloc>` is AFFINE and not
//!   linear, so dropping one verifies clean (`controls/affine_leak.rs`). What
//!   does not stand is that a MAP fixes it.
//!   ⚠ **So the backstop for this obligation is Miri, on this rung AND on R5**,
//!   which is where it stood before TASK_110. And the `identity` pin is what
//!   protects the tree: a byte-identical twin carrying a proof is not a proof
//!   about the twin that does not, but a planted leak DOES move `md5_fn`, so
//!   the pin catches an R5-only leak at both pinned levels. ⚠ **A leak planted
//!   in BOTH rungs passes the pin and is caught only by Miri.**

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
        // LLVM's induction-variable strength reduction, R5 keeps `%r9` as a
        // byte cursor where R4 keeps an index, and the `identity` pin drops
        // from `exact` to `differ`. Re-measured at TASK_110, since the fold
        // loop below moved underneath this note: 127 against 128 instructions,
        // in `%r9`. It read `%r8` and `two instructions` before that, which was
        // right for the pre-TASK_110 fold. Both figures: ../NOTES.md 8.
        let q: *mut u8 = dig_at(p, base, i);
        run = run.wrapping_add(v_get_unchecked(v, off + i) ^ MIX);
        let b: u8 = (run >> 24) as u8;
        dig_write(q, b);
        i = i + 1;
    }
    // THE FOLD, as a do-while over a DESCENDING CURSOR: one induction variable
    // per loop instead of two, and it never forms the one-past-the-end pointer
    // that would put R5 out of reach. R5's is the same loop with the ghost
    // bookkeeping added; see verus.rs.
    let mut acc: u64 = 0;
    let mut q: *mut u8 = dig_at(p, base, len - 1);
    loop {
        acc = acc.wrapping_mul(31).wrapping_add(dig_read(q) as u64);
        if q == p {
            break;
        }
        q = q.with_addr(q.addr() - 1);
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
