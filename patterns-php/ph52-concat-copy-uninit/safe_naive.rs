//! ph52 rung R2 -- safe-naive.
//!
//! The mechanical port a working Rust programmer writes first: keep the C's
//! shape -- `concat_function` with two caller-owned slots, `make_printable`
//! writing through a `&mut`, a `zval_dtor` that dispatches on what the slot
//! holds -- and make the UNCONSTRUCTED slot REPRESENTABLE, because safe Rust has
//! no other option. `Option<Pr>`, `slot.take()`, `while` loops. Zero `unsafe`.
//!
//! ⭐⭐ **THE ROW'S LADDER RESULT, STATED UP FRONT: THE C's SLOT HAS FOUR STATES
//! AND SAFE RUST HAS THREE.**
//!
//!     C                                  this rung
//!     -------------------------------    ---------------------------------
//!     UNCONSTRUCTED (the stack byte)     `None`
//!     IS_STRING + empty_string           `Some(Pr { req: 0, .. })`
//!     IS_STRING + a live emalloc block   `Some(Pr { req: n, .. })`
//!     IS_STRING + a pointer :1188 FREED  ⛔ UNREPRESENTABLE
//!
//! The fourth state is the defect. `zval_dtor` here is `slot.take()`, and
//! `take()` leaves `None` -- so the moment `zend_operators.c:1188` releases the
//! block, the slot stops naming it. There is no expression in safe Rust that
//! produces the state `zend.c:243` reads. ⚠ **That is a FINDING and never a
//! kill** (`CLAUDE.md` rule 6): the row's C is admitted on the C, and what safe
//! Rust can and cannot say about it is the result. `../NOTES.md` §10.
//!
//! ⚠⚠ **AND IT IS NOT *"`Option` reinvents the upstream fix"*.**
//! `7412202c43e7` DELETES the teardown on the early-exit path and leaves the
//! four states intact everywhere else; `Option` keeps the teardown and deletes
//! the fourth STATE. Different repairs, and only one of them is available to the
//! C. `../NOTES.md` §10 measures both.
//!
//! ⚠ **WHAT THIS RUNG PAYS FOR IT.** `Pr` is two `usize`s, so `Option<Pr>` has
//! no niche and costs a whole extra word plus a discriminant test on every
//! teardown
//! -- and `take()` is a write-back the C does not perform. The teardowns are
//! three per op against the C's two, so do not read this rung's number as a
//! bounds-check tax: `../NOTES.md` §8 reads the decomposition off the
//! disassembly.
//!
//! ⚠⚠ **AND EVERY CROSS-LANGUAGE FIGURE ON THIS ROW INCLUDES ALLOCATOR WORK**
//! (`PROTOCOL_PHP.md` §B1a.3): the kernel makes O(n_ops) allocations per call, so
//! §B1a's precondition does NOT hold here and `ph53` is the exception, not this
//! row. The SAME-LANGUAGE ratios -- this rung against `safe_tuned.rs`, and
//! `unsafe.rs` against `verus.rs` -- are unaffected, because the four Rust rungs
//! allocate identically and the term cancels (§B1a.4).

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

#[inline(always)]
fn rd32(w: &[u8], o: usize) -> u32 {
    (w[o] as u32) | ((w[o + 1] as u32) << 8) | ((w[o + 2] as u32) << 16)
        | ((w[o + 3] as u32) << 24)
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

/// `_zval_dtor` -- `Zend/zend_variables.c:36-80`, as safe Rust can spell it.
///
/// ⭐⭐ **THIS IS THE ROW.** The C dispatches on a `zend_uchar` tag that nothing
/// may have written; here the discriminant IS the `Option` and `take()` is what
/// makes the fourth state unreachable. There is no tag byte to read out of turn
/// and no pointer to release twice.
#[inline(always)]
fn zval_dtor(slot: &mut Option<Pr>, al: &mut Alloc) {
    if let Some(p) = slot.take() {
        if p.req != 0 {
            al.free(p.req);                                  // :45 STR_FREE_REL
        }
    }
}

/// `zend_make_printable_zval` -- `Zend/zend.c:188-265`, narrowed to five arms.
///
/// Writes the slot through `expr_copy` and returns `(use_copy, len, dig)`.
/// ⚠⚠ **THE WRITE ORDER IS THE C's: the VALUE first, and the thing that decides
/// the teardown arm LAST.** Here the "tag" is the `Option`'s own discriminant,
/// so `*expr_copy = Some(..)` is `:263`.
#[inline(always)]
fn make_printable_zval(arm: u32, aux: u32, expr_copy: &mut Option<Pr>,
                       al: &mut Alloc) -> (bool, usize, u64) {
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
        // ⭐ `:243 zval_dtor(expr_copy)` IS HERE, and on this rung it is SOUND
        // for a reason the C cannot have: the slot is an `Option`, so "has it
        // been constructed?" is a question the value itself answers.
        zval_dtor(expr_copy, al);                  // :243
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
    *expr_copy = Some(pr);                         // :263  THE TAG, WRITTEN LAST
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
fn concat_function(op1_copy: &mut Option<Pr>, op2_copy: &mut Option<Pr>,
                   a1: u32, x1: u32, a2: u32, x2: u32,
                   al: &mut Alloc) -> (usize, u64, u64) {
    let (uc1, n1, g1) = make_printable_zval(a1, x1, op1_copy, al);   // :1152
    let (uc2, n2, g2) = make_printable_zval(a2, x2, op2_copy, al);   // :1153

    // :1179-1186 -- the `result != op1` arm.
    let total: usize = n1 + n2;                                      // :1180
    al.alloc(total + 1);                                             // :1181

    if uc1 {
        zval_dtor(op1_copy, al);                                     // :1188
    }
    if uc2 {
        zval_dtor(op2_copy, al);                                     // :1191
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
    // :1148 -- the two caller slots. ⭐ `None` is safe Rust's spelling of "the
    // stack byte nobody wrote", and it is the only one available.
    let mut op1_copy: Option<Pr> = None;
    let mut op2_copy: Option<Pr> = None;
    let mut o: usize = 0;
    while o < n_ops {
        let p: usize = OPS_OFF + OP_BYTES * o;
        let a1: u32 = (win[p] as u32) % NARM;
        let x1: u32 = win[p + 1] as u32;
        let a2: u32 = (win[p + 2] as u32) % NARM;
        let x2: u32 = win[p + 3] as u32;

        let (total, g1, g2) = concat_function(&mut op1_copy, &mut op2_copy,
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
