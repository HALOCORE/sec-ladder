//! ph52 rung R4 -- unsafe.
//!
//! The faithful port of `Zend/zend_operators.c:1148`: the two caller slots are
//! typed as UNINITIALISED -- `MaybeUninit<Pr>` -- with a **one-bit witness each**
//! recording whether `zend.c:263` has written the tag. Byte-identical exec code
//! to `verus.rs`, which proves it.
//!
//! ⭐⭐⭐ **AND THE WITNESS IS ONE BIT PER SLOT, WHICH IS WHAT MAKES `ph53`'s
//! `+21.775 %` FALSIFIABLE.** `ph53`'s witness is `[bool; MAXD]` -- one byte per
//! slot, `n` of them, re-read on every consumer iteration -- and F98 priced the
//! shipped R4/R5's extra work at `+21.775 %` in W1 on `small.bin` at
//! `O3/isolated` against `controls/r4_nowitness.rs`. ph52's is **two `bool`s for
//! the whole kernel**, tested twice per op and never indexed. ▶ If ph53's witness
//! is dear and this one is free, the cost of a safety witness is O(the number of
//! slots) and not a constant. `../NOTES.md` §11 has the measurement and says
//! which way it went.
//!
//! ⚠⚠ **THE WITNESS IS NOT IN THE C AND IT IS NOT UPSTREAM.** It is what makes
//! `:243`'s read dischargeable at R5, and it is declared in ../spec.md's
//! divergence ledger. The faithful WITNESS-FREE port -- which reads the
//! `MaybeUninit` with no test at all, exactly as `zend.c:243` does -- is
//! `controls/r4_nowitness.rs`: measured, run under Miri, and put through Verus
//! with its error text. ⭐ **That program is a CONTROL and not a rung, and why is
//! this row's Verus-side result** (`../NOTES.md` §11).
//!
//! **Where the trusted surface is, and it is ONE item at THREE call sites.**
//!   * `slot_read_unchecked(&MaybeUninit<Pr>) -> Pr` -- `assume_init_ref` plus a
//!     copy. `requires` the slot to be initialised, which the witness supplies.
//!     ⚠ `MaybeUninit::assume_init_ref` IS specified by the pinned vstd
//!     (`~/tools/verus/vstd/std_specs/maybe_uninit.rs:45-49`), so in ordinary
//!     exec code it would cost NO trusted item -- `controls/mu_unwrapped.rs`
//!     verifies exactly that. What forces the wrapper is
//!     `harness/check.py::_scan_unsafe_sites`, which requires every `unsafe`
//!     token in a Verus source to sit inside an `external_body` body. ph53
//!     reported that collision first (F97); this row is its second instance and
//!     `../NOTES.md` §11 says what is the same and what is not.
//!   * `win_get_unchecked(&[u8], usize) -> u8` -- the window read, the way the C
//!     reads it. ⚠ It is a FIDELITY REPAIR and not an optimisation: every window
//!     access in the C is unchecked, so a safe-indexed R4 would pay a bounds check
//!     the C does not. `verus.rs` gives it a VERIFIED TWIN, so its `requires` is
//!     checked against a safe implementation rather than asserted.
//!   * there is NO unchecked SLOT indexing, because the slots are two named locals
//!     and not an array. ⭐ That is half of why the witness is cheaper here, and it
//!     is a consequence of the C, not a choice.
//!
//! ⚠⚠ **AND EVERY CROSS-LANGUAGE FIGURE ON THIS ROW INCLUDES ALLOCATOR WORK**
//! (`PROTOCOL_PHP.md` §B1a.3): O(n_ops) allocations per kernel call. The
//! R4-vs-R5 ratio is unaffected -- the two rungs allocate identically (§B1a.4).

use core::mem::MaybeUninit;

#[path = "../../common/driver.rs"]
mod driver;

// ------------------------------------------------------- shared arithmetic --
// Identical text in all four Rust rungs and re-derived independently in
// model.py. See ../spec.md for why each is what it is.

/// `c/kernel.h`.
const OPS_OFF: usize = 8;
const OP_BYTES: usize = 4;
const NARM: u32 = 5;
const A_STRING: u32 = 0;
const A_NULL: u32 = 1;
const A_BOOL: u32 = 2;
const A_ARRAY: u32 = 3;
/// `zend.c:249` -- `sizeof("Object id #")-1 + MAX_LENGTH_OF_LONG`, with
/// `zend_operators.h:37 MAX_LENGTH_OF_LONG 20`.
const OBJ_PREFIX_LEN: usize = 11;
const OBJ_REQ: usize = OBJ_PREFIX_LEN + 20;
/// ⚠⚠ THE CONTENT DIGESTS, AND THEY ARE INSTRUMENTATION -- not fields of `zval`.
/// `zend.c:250` and `zend_operators.c:1182-1184`'s store lines are NOT lifted:
/// the bytes they move are a pure function of the two operand descriptors, so
/// every rung allocates exactly the blocks upstream allocates and folds the same
/// content as a 131-digest instead of materialising it. ⭐ Keeping the stores
/// would put a `Seq<u8>` concatenation in `verus.rs`'s postcondition and make the
/// cross-language column a comparison of `rep movsb` against a Rust `while` loop
/// -- a memcpy comparison, not a safety comparison (`ph64`'s lesson one level
/// over). `../spec.md`'s divergence ledger has the argument and
/// `controls/digest.py` checks each constant against the literal it stands for.
const DIG_PREFIX: u64 = 18136473400329561039;   // fold131("Object id #")
const DIG_ARRAY: u64 = 19400746421;             // fold131("Array")
const DIG_ONE: u64 = 49;                        // fold131("1")

/// `zend_alloc.h:63-64` via `emalloc_shim.h:190-191`.
const MAX_CACHED_MEMORY: usize = 11;
const MAX_CACHED_ENTRIES: u32 = 256;

/// `zend_alloc.c`'s size-class cache, counters only -- `emalloc_shim.h:346-435`.
///
/// `PROTOCOL_PHP.md` §B forbids a Rust rung from linking the shim and §B1.2
/// requires the tally in the `u64`, so the rung computes what the C's allocator
/// would have counted. ⚠⚠ **§B1a's PRECONDITION DOES NOT HOLD ON THIS ROW** --
/// up to five `emalloc`s and three `efree`s per op, i.e. O(n_ops) per call -- so
/// the cache is EVOLVING and the counters cannot be closed-form. `ph64`'s
/// `safe_naive.rs::Alloc` is the precedent.
struct Alloc {
    cnt: [u32; MAX_CACHED_MEMORY],
    n_alloc: u64,
    n_free: u64,
    n_hit: u64,
    bytes: u64,
}

impl Alloc {
    #[inline(always)]
    fn new() -> Alloc {
        Alloc { cnt: [0u32; MAX_CACHED_MEMORY], n_alloc: 0, n_free: 0, n_hit: 0,
                bytes: 0 }
    }
    /// `_emalloc` -- `zend_alloc.c:142-217`.
    #[inline(always)]
    fn alloc(&mut self, size: usize) {
        let rsz: usize = (size + 7) & !7usize;
        let idx: usize = rsz >> 3;
        self.n_alloc = self.n_alloc.wrapping_add(1);
        if idx < MAX_CACHED_MEMORY && self.cnt[idx] > 0 {
            self.cnt[idx] -= 1;
            self.n_hit = self.n_hit.wrapping_add(1);
        } else {
            self.bytes = self.bytes.wrapping_add(rsz as u64);
        }
    }
    /// `_efree` -- `zend_alloc.c:248-289`. ⚠ The class comes from the RECORDED
    /// size (`p->size`, `zend_alloc.h:53`), which for every request this kernel
    /// makes is the size that was asked for.
    #[inline(always)]
    fn free(&mut self, size: usize) {
        let rsz: usize = (size + 7) & !7usize;
        let idx: usize = rsz >> 3;
        self.n_free = self.n_free.wrapping_add(1);
        if idx < MAX_CACHED_MEMORY && self.cnt[idx] < MAX_CACHED_ENTRIES {
            self.cnt[idx] += 1;
        }
    }
    /// `php_shim_tally()` -- `emalloc_shim.h:642-648`.
    #[inline(always)]
    fn tally(&self) -> u64 {
        self.n_alloc.wrapping_mul(1000003)
            ^ self.n_free.wrapping_mul(1000033)
            ^ self.n_hit.wrapping_mul(1000037)
            ^ self.bytes.wrapping_mul(1000039)
    }
}

/// `v[i]` with no bounds check.
///
/// ⚠⚠ **WHY R4/R5 HAVE THIS AND R2/R3 DO NOT, AND IT IS A FIDELITY REPAIR RATHER
/// THAN AN OPTIMISATION.** Every window read in the C is an UNCHECKED array
/// access: C has no bounds check, and nothing in `concat_function` or
/// `zend_make_printable_zval` verifies that the op record is inside the window.
/// The kernel's structural precondition (`8 <= len`, `off + len <= buf_len`) is
/// what makes it sound, and it is discharged at the CALL SITE. ▶ A safe-indexed R4
/// would pay a bounds check the C does not. In `verus.rs` this is
/// `#[verifier::external_body]` with `requires i < v@.len()` AND a verified twin.
#[inline(always)]
fn win_get_unchecked(v: &[u8], i: usize) -> u8 {
    unsafe { *v.get_unchecked(i) }
}

#[inline(always)]
fn rd32(w: &[u8], o: usize) -> u32 {
    (win_get_unchecked(w, o) as u32) | ((win_get_unchecked(w, o + 1) as u32) << 8)
        | ((win_get_unchecked(w, o + 2) as u32) << 16)
        | ((win_get_unchecked(w, o + 3) as u32) << 24)
}

/// What a constructed slot holds. ⚠ `req == 0` IS `empty_string`
/// (`zend_variables.c:29`), and `zend.h:469 STR_FREE` is what makes that state
/// safe to tear down for ever: `if (ptr && ptr != empty_string) efree(ptr)`.
/// `len` is what `value.str.len` ends up carrying.
///
/// ⚠ THE CONTENT DIGEST IS **NOT** A FIELD OF THIS STRUCT, because it is not a
/// field of `zval`. It is an out-value of `make_printable_zval`, exactly as
/// ph53's `*examined` / `*matched_id` are out-parameters of its consumers.
#[derive(Clone, Copy)]
struct Pr {
    req: usize,
    len: usize,
}

// ---------------------------------------------------------------- kernel ----
// Contract: ../spec.md. `#[inline(never)]` only in `isolated` builds, so the
// `whole` builds can inline it the way LTO'd C would.

/// `(*m).assume_init_ref()` with no initialisedness check, then a copy.
///
/// ⚠ **THE ONLY TRUSTED ITEM ON THIS RUNG.** `MaybeUninit::assume_init_ref`'s own
/// precondition is `m.mem_contents().is_init()` and the pinned vstd states it
/// (`std_specs/maybe_uninit.rs:45-49`); here the caller's witness is what
/// discharges it. In `verus.rs` this is `#[verifier::external_body]` with the
/// same `requires`, and `controls/mu_unwrapped.rs` verifies the UNWRAPPED shape
/// at no trusted cost, so the wrapper is the gate's requirement and not Verus's.
#[inline(always)]
fn slot_read_unchecked(m: &MaybeUninit<Pr>) -> Pr {
    unsafe { *m.assume_init_ref() }
}

/// `_zval_dtor` -- `Zend/zend_variables.c:36-80`.
///
/// ⭐⭐ **THIS IS THE ROW, AND HERE THE TAG IS EXPLICIT.** The C dispatches on
/// `zvalue->type`, a `zend_uchar` that nothing may have written. This rung reads
/// the slot through `slot_read_unchecked` and `constructed` is the one bit that
/// says it may. ⚠ Deleting the `if` is `zend.c:243` exactly, and that program is
/// `controls/r4_nowitness.rs`.
#[inline(always)]
fn zval_dtor(slot: &MaybeUninit<Pr>, constructed: &mut bool, al: &mut Alloc) {
    if *constructed {
        let p: Pr = slot_read_unchecked(slot);
        if p.req != 0 {
            al.free(p.req);                                  // :45 STR_FREE_REL
        }
        *constructed = false;
    }
}

/// `zend_make_printable_zval` -- `Zend/zend.c:188-265`, narrowed to five arms.
///
/// Writes the slot through `expr_copy` and the witness through `constructed`,
/// and returns `(use_copy, len, dig)`. ⚠⚠ **THE WRITE ORDER IS THE C's: the
/// VALUE first, and the thing that decides the teardown arm LAST** -- which here
/// is the witness bit.
#[inline(always)]
fn make_printable_zval(arm: u32, aux: u32, expr_copy: &mut MaybeUninit<Pr>,
                       constructed: &mut bool, al: &mut Alloc)
                       -> (bool, usize, u64) {
    if arm == A_STRING {
        // :190-193  expr_copy NEVER WRITTEN; the operand is one attacker byte.
        return (false, 1, (b'a' + (aux % 26) as u8) as u64);
    }
    let pr: Pr;
    let mut dig: u64 = 0;
    if arm == A_NULL {
        pr = Pr { req: 0, len: 0 };                // :195-197
    } else if arm == A_BOOL {
        if aux & 1 == 1 {
            al.alloc(2);                           // :202  estrndup("1", 1)
            dig = DIG_ONE;
            pr = Pr { req: 2, len: 1 };
        } else {
            pr = Pr { req: 0, len: 0 };            // :204-205
        }
    } else if arm == A_ARRAY {
        al.alloc(6);                               // :214  estrndup("Array", 5)
        dig = DIG_ARRAY;
        pr = Pr { req: 6, len: 5 };
    } else if aux & 1 == 1 {
        // :242  EG(exception) -- THE EARLY EXIT.
        // ⭐ `:243 zval_dtor(expr_copy)` IS HERE, and the `constructed` witness
        // is the ONE BIT that makes it dischargeable. Deleting the test is
        // `controls/r4_nowitness.rs`.
        zval_dtor(expr_copy, constructed, al);     // :243
        pr = Pr { req: 0, len: 0 };                // :244-245
    } else {
        al.alloc(OBJ_REQ);                         // :249
        // :250  `sprintf(val, "Object id #%ld", handle)`, NARROWED: the prefix is
        // a constant digest and the handle's decimal digits are folded in the same
        // least-significant-first order `sprintf`'s own loop produces them in.
        // ⚠ `aux` is ONE WINDOW BYTE -- the kernel's projection of
        // `zend_object_handle`, which `zend.h:265` makes an `unsigned int` -- so
        // the handle has AT MOST THREE decimal digits and `sprintf`'s own
        // `do { } while (d)` is narrowed to an exhaustive three-way case.
        let nd: usize;
        dig = DIG_PREFIX;
        dig = dig.wrapping_mul(131).wrapping_add((48 + aux % 10) as u64);
        if aux < 10 {
            nd = 1;
        } else {
            dig = dig.wrapping_mul(131).wrapping_add((48 + (aux / 10) % 10) as u64);
            if aux < 100 {
                nd = 2;
            } else {
                dig = dig.wrapping_mul(131).wrapping_add((48 + aux / 100) as u64);
                nd = 3;
            }
        }
        pr = Pr { req: OBJ_REQ, len: OBJ_PREFIX_LEN + nd };
    }
    // :263  THE TAG, WRITTEN LAST. ⚠ `value` first (the write below), then the
    // thing that decides the teardown arm -- which on this rung is the witness,
    // set AFTER the slot exactly as `:263` follows the switch.
    *expr_copy = MaybeUninit::new(pr);
    *constructed = true;
    (true, pr.len, dig)                            // :264  *use_copy = 1
}

/// `concat_function` -- `Zend/zend_operators.c:1146-1194`, narrowed.
/// The two slots are the caller's, exactly as `:1148` declares them.
/// Returns `(total, dig1, dig2)`.
///
/// ⚠ `:1182-1184`'s three `memcpy`/store lines are NOT lifted: the bytes they
/// move are a function of the two operand descriptors and the digests carry them
/// into the u64 instead. ../spec.md's divergence ledger has the argument.
#[inline(always)]
fn concat_function(op1_copy: &mut MaybeUninit<Pr>, c1: &mut bool,
                   op2_copy: &mut MaybeUninit<Pr>, c2: &mut bool,
                   a1: u32, x1: u32, a2: u32, x2: u32,
                   al: &mut Alloc) -> (usize, u64, u64) {
    let (uc1, n1, g1) = make_printable_zval(a1, x1, op1_copy, c1, al);  // :1152
    let (uc2, n2, g2) = make_printable_zval(a2, x2, op2_copy, c2, al);  // :1153

    // :1179-1186 -- the `result != op1` arm.
    let total: usize = n1 + n2;                                      // :1180
    al.alloc(total + 1);                                             // :1181

    if uc1 {
        zval_dtor(op1_copy, c1, al);                                 // :1188
    }
    if uc2 {
        zval_dtor(op2_copy, c2, al);                                 // :1191
    }
    (total, g1, g2)
}

#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    let win: &[u8] = &buf[off..off + len];

    let cap: usize = (len - OPS_OFF) / OP_BYTES;
    let n_ops: usize = (rd32(win, 0) as usize) % (cap + 1);
    let mut acc: u64 = rd32(win, 4) as u64;

    let mut al: Alloc = Alloc::new();
    // :1148 -- the two caller slots, TYPED AS UNINITIALISED. ⭐ This is the only
    // Rust spelling of `zval op1_copy;` that does not forge a value for the state
    // the C actually has, and the two `bool`s are the whole witness.
    let mut op1_copy: MaybeUninit<Pr> = MaybeUninit::uninit();
    let mut op2_copy: MaybeUninit<Pr> = MaybeUninit::uninit();
    let mut c1: bool = false;
    let mut c2: bool = false;
    let mut o: usize = 0;
    while o < n_ops {
        let p: usize = OPS_OFF + OP_BYTES * o;
        let a1: u32 = (win_get_unchecked(win, p) as u32) % NARM;
        let x1: u32 = win_get_unchecked(win, p + 1) as u32;
        let a2: u32 = (win_get_unchecked(win, p + 2) as u32) % NARM;
        let x2: u32 = win_get_unchecked(win, p + 3) as u32;

        let (total, g1, g2) = concat_function(&mut op1_copy, &mut c1,
                                             &mut op2_copy, &mut c2,
                                             a1, x1, a2, x2, &mut al);

        acc = acc.wrapping_mul(31).wrapping_add(total as u64);
        acc = acc.wrapping_mul(31).wrapping_add(g1);
        acc = acc.wrapping_mul(31).wrapping_add(g2);

        al.free(total + 1);            // the executor releases the temporary
        o = o + 1;
    }

    acc ^ al.tally()
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
    if stride_w >= 8 && stride_w <= n_blob as u64 {
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
