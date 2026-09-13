//! ph52 rung R5 -- unsafe + Verus.
//!
//! Same exec code as `unsafe.rs`, plus the proof that licenses it.
//!
//!     requires  off + len <= buf@.len(),  8 <= len
//!     ensures   r == concat_fold(buf@, off as int, len as int)
//!
//! `concat_fold` is the concat op stream as a pure function of the window's
//! bytes, spelled as a state machine over `St { al, s1, s2, acc }` -- `s_print`,
//! `s_dtor`, `s_op`, `s_run` -- and `model.py` re-derives the same `u64` from two
//! other decompositions.
//!
//! ============================================================================
//! ⭐⭐ WHAT THE PROOF RESTS ON, AND THE THREE THINGS IT SAYS ABOUT THIS ROW
//! ============================================================================
//! **1. `mem_contents()` IS THE GHOST STATE FOR INITIALISEDNESS.** The pinned
//! vstd's `std_specs/maybe_uninit.rs` ships `assume_specification` for
//! `MaybeUninit::{new, uninit, assume_init, assume_init_ref, assume_init_mut}`,
//! with `uninit()` ensuring `MemContents::Uninit` and every `assume_init*`
//! carrying `requires m.mem_contents().is_init()`. **The obligation this row is
//! about is literally that `requires`**, and the `constructed` witness is what
//! discharges it.
//!
//! **2. ⚠⚠ AND THE SPEC-LEVEL SLOT IS *NOT* A `MaybeUninit`.** A spec function
//! cannot construct one (`mem_contents` is `uninterp`), so `Sl { c, req }` is the
//! abstraction and `K::st()` is the abstraction function onto it. ⭐ But it is
//! **ONE `bool` AND ONE `usize` PER SLOT, TWO SLOTS** -- where `ph53` needed a
//! whole `Seq<Option<u32>>` -- and that is the same O(slots) story the runtime
//! witness tells, one level up. `../NOTES.md` §11.
//!
//! **3. ⚠⚠⚠ THE COLLISION `ph53` FOUND (F97) RECURS, AND IT IS NARROWER HERE.**
//! `harness/check.py::_scan_unsafe_sites` requires every `unsafe` token in a
//! pinned Verus source to sit inside an `external_body` body, and 5c-twin then
//! requires every trusted item to have a VERIFIED twin -- which for a
//! `MaybeUninit` read would itself need `unsafe`, because there is no safe exec
//! route from `MaybeUninit<T>` to `T`. Two sound rules, jointly unsatisfiable for
//! this operation, a second time. ⭐ **What is NARROWER: ph52 has exactly ONE
//! trusted item and ph53 has four, because ph52's slots are two named locals and
//! not an array -- so there is no unchecked INDEXING to fold in.**
//! `controls/mu_unwrapped.rs` verifies the unwrapped shape at no trusted cost and
//! `controls/negatives.py --verus` runs it, so the fact about Verus is committed
//! and re-checked rather than cited.
//!
//! ⚠ `controls/r4_nowitness.rs` is the FAITHFUL witness-free R4 -- `zend.c:243`
//! with no test at all -- measured, Miri'd and put through Verus with its error
//! text. It is a CONTROL and not a rung, and why is this row's Verus-side result.

use vstd::prelude::*;
use core::mem::MaybeUninit;

// Plain-Rust I/O helpers. Outside `verus!`, so Verus treats the whole module as
// external (external-by-default). Reached only through `load_input`/`emit`.
#[path = "../../common/driver.rs"]
mod driver;

verus! {

// `group_slice_axioms` gives `slice@.len() == spec_slice_len(slice)`, hence
// `slice@.len() <= usize::MAX`, without which `off + len` cannot be shown not to
// overflow. `lemma_u128_shr_is_div` turns `x >> 64` into `x / 2^64` for the
// driver's multiply-shift barrier bound; the mul group is what the window-offset
// bound `k * stride + stride <= n_blob` needs.
broadcast use {
    vstd::slice::group_slice_axioms,
    vstd::bits::lemma_u128_shr_is_div,
    vstd::arithmetic::mul::lemma_mul_inequality,
};

// ------------------------------------------------------- shared arithmetic --
pub const OPS_OFF: usize = 8;

pub const OP_BYTES: usize = 4;

pub const NARM: u32 = 5;

pub const A_STRING: u32 = 0;

pub const A_NULL: u32 = 1;

pub const A_BOOL: u32 = 2;

pub const A_ARRAY: u32 = 3;

pub const OBJ_PREFIX_LEN: usize = 11;

pub const OBJ_REQ: usize = 31;           // OBJ_PREFIX_LEN + MAX_LENGTH_OF_LONG

pub const DIG_PREFIX: u64 = 18136473400329561039;   // fold131("Object id #")

pub const DIG_ARRAY: u64 = 19400746421;             // fold131("Array")

pub const DIG_ONE: u64 = 49;                        // fold131("1")

pub const MAX_CACHED_MEMORY: usize = 11;

pub const MAX_CACHED_ENTRIES: u32 = 256;

/// What a constructed slot holds. `req == 0` IS `empty_string`.
#[derive(Clone, Copy)]
pub struct Pr {
    pub req: usize,
    pub len: usize,
}

// ------------------------------------------------------------------ spec ----

/// `_emalloc`'s `REAL_SIZE(size)` -- `zend_alloc.c:132`, `(size + 7) & ~7`. The
/// exec code writes exactly this expression, so no bit-vector reasoning is
/// needed to connect them.
pub open spec fn real_of(size: usize) -> usize {
    ((size + 7) as usize) & !(7usize)
}

/// `cache_index = real_size >> 3` -- `zend_alloc.c:136`.
pub open spec fn idx_of(size: usize) -> usize {
    real_of(size) >> 3
}

pub open spec fn rd32s(w: Seq<u8>, o: int) -> u32 {
    (w[o] as u32) | ((w[o + 1] as u32) << 8) | ((w[o + 2] as u32) << 16) | ((w[o + 3] as u32)
        << 24)
}

pub open spec fn mix(a: u64, b: u64) -> u64 {
    a.wrapping_mul(31).wrapping_add(b)
}

pub open spec fn mix131(a: u64, b: u64) -> u64 {
    a.wrapping_mul(131).wrapping_add(b)
}

/// The allocator's whole observable state -- `zend_alloc.c`'s per-class cache
/// depth plus the four tally fields.
pub struct A {
    pub cnt: Seq<u32>,
    pub n_alloc: u64,
    pub n_free: u64,
    pub n_hit: u64,
    pub bytes: u64,
}

pub open spec fn s_alloc_a(a: A, size: usize) -> A {
    let idx = idx_of(size);
    let a1 = A { n_alloc: a.n_alloc.wrapping_add(1), ..a };
    if idx < MAX_CACHED_MEMORY && a1.cnt[idx as int] > 0 {
        A {
            cnt: a1.cnt.update(idx as int, (a1.cnt[idx as int] - 1) as u32),
            n_hit: a1.n_hit.wrapping_add(1),
            ..a1
        }
    } else {
        A { bytes: a1.bytes.wrapping_add(real_of(size) as u64), ..a1 }
    }
}

pub open spec fn s_free_a(a: A, size: usize) -> A {
    let idx = idx_of(size);
    let a1 = A { n_free: a.n_free.wrapping_add(1), ..a };
    if idx < MAX_CACHED_MEMORY && a1.cnt[idx as int] < MAX_CACHED_ENTRIES {
        A { cnt: a1.cnt.update(idx as int, (a1.cnt[idx as int] + 1) as u32), ..a1 }
    } else {
        a1
    }
}

/// `php_shim_tally()` -- `common-php/emalloc_shim.h:642-648`.
pub open spec fn tally_of(a: A) -> u64 {
    a.n_alloc.wrapping_mul(1000003) ^ a.n_free.wrapping_mul(1000033) ^ a.n_hit.wrapping_mul(
        1000037,
    ) ^ a.bytes.wrapping_mul(1000039)
}

/// The SPEC-LEVEL slot. ⚠ `c` is the witness -- `zend.c:263` has written the tag
/// -- and `req` is the allocation `zend_operators.c:1188` will have to release.
/// ⭐ It is NOT a `MaybeUninit`: a spec function cannot construct one.
pub struct Sl {
    pub c: bool,
    pub req: usize,
}

/// The whole kernel state between ops.
pub struct St {
    pub al: A,
    pub s1: Sl,
    pub s2: Sl,
    pub acc: u64,
}

/// `_zval_dtor` -- `Zend/zend_variables.c:36-80`, narrowed. ⚠ `req == 0` is
/// `empty_string` and `zend.h:469 STR_FREE` skips it.
pub open spec fn s_dtor(a: A, sl: Sl) -> (A, Sl) {
    if sl.c {
        if sl.req != 0 {
            (s_free_a(a, sl.req), Sl { c: false, ..sl })
        } else {
            (a, Sl { c: false, ..sl })
        }
    } else {
        (a, sl)
    }
}

/// `zend.c:250`'s digits, least-significant-first, from `DIG_PREFIX`. ⚠ `aux` is
/// one window byte, so at most three decimal digits and the case analysis is
/// exhaustive.
pub open spec fn obj_dig(aux: u32) -> u64 {
    let d0 = mix131(DIG_PREFIX, (48 + aux % 10) as u64);
    if aux < 10 {
        d0
    } else {
        let d1 = mix131(d0, (48 + (aux / 10) % 10) as u64);
        if aux < 100 {
            d1
        } else {
            mix131(d1, (48 + aux / 100) as u64)
        }
    }
}

pub open spec fn obj_nd(aux: u32) -> usize {
    if aux < 10 {
        1
    } else if aux < 100 {
        2
    } else {
        3
    }
}

/// `zend_make_printable_zval` -- `Zend/zend.c:188-265`, narrowed to five arms,
/// as a pure transition. Returns `(al', sl', use_copy, len, dig)`.
///
/// ⚠ **`opaque`, AND THAT IS A PROOF-BUDGET DECISION WITH A MEASUREMENT BEHIND
/// IT.** Left transparent, the solver unfolds this and `s_concat` under `s_run`'s
/// own recursion and `lemma_run_step` blows the rlimit -- measured, on the first
/// complete draft of this file. It is revealed exactly where it is proved
/// (`make_printable_zval`) and nowhere else.
#[verifier::opaque]
pub open spec fn s_print(a: A, sl: Sl, arm: u32, aux: u32) -> (A, Sl, bool, usize, u64) {
    if arm == A_STRING {
        // :190-193  expr_copy NEVER WRITTEN
        (a, sl, false, 1usize, (97 + aux % 26) as u64)
    } else if arm == A_NULL {
        (a, Sl { c: true, req: 0 }, true, 0usize, 0u64)            // :195-197
    } else if arm == A_BOOL {
        if aux % 2 == 1 {
            (s_alloc_a(a, 2), Sl { c: true, req: 2 }, true, 1usize, DIG_ONE)   // :202
        } else {
            (a, Sl { c: true, req: 0 }, true, 0usize, 0u64)        // :204-205
        }
    } else if arm == A_ARRAY {
        (s_alloc_a(a, 6), Sl { c: true, req: 6 }, true, 5usize, DIG_ARRAY)     // :214
    } else if aux % 2 == 1 {
        // :242-246  THE EARLY EXIT.  `:243` tears down a slot nothing may have
        // constructed; `s_dtor` is what the witness makes sound.
        let d = s_dtor(a, sl);
        (d.0, Sl { c: true, req: 0 }, true, 0usize, 0u64)
    } else {
        (
            s_alloc_a(a, OBJ_REQ),
            Sl { c: true, req: OBJ_REQ },
            true,
            (OBJ_PREFIX_LEN + obj_nd(aux)) as usize,
            obj_dig(aux),
        )                                                          // :249-250
    }
}

/// `concat_function` -- `Zend/zend_operators.c:1146-1194`, narrowed, plus the
/// kernel's own fold. Returns `(state, total)` -- ⚠ WITHOUT the release of the
/// temporary, which the KERNEL does and `s_op` adds, because that `efree` is the
/// executor's and not `concat_function`'s.
/// ⚠ `opaque` for the same reason as `s_print`; revealed in `concat_function`.
#[verifier::opaque]
pub open spec fn s_concat(st: St, arm1: u32, aux1: u32, arm2: u32, aux2: u32) -> (St, usize) {
    let p1 = s_print(st.al, st.s1, arm1, aux1);                    // :1152
    let p2 = s_print(p1.0, st.s2, arm2, aux2);                     // :1153
    let total = (p1.3 + p2.3) as usize;                            // :1180
    let a3 = s_alloc_a(p2.0, (total + 1) as usize);                // :1181
    let acc1 = mix(st.acc, total as u64);
    let acc2 = mix(acc1, p1.4);
    let acc3 = mix(acc2, p2.4);
    let t1 = if p1.2 {
        s_dtor(a3, p1.1)                                           // :1188
    } else {
        (a3, p1.1)
    };
    let t2 = if p2.2 {
        s_dtor(t1.0, p2.1)                                         // :1191
    } else {
        (t1.0, p2.1)
    };
    (St { al: t2.0, s1: t1.1, s2: t2.1, acc: acc3 }, total)
}

/// One loop iteration of the kernel: `s_concat` plus the executor's release of
/// the temporary (`php_shim_efree(result.value.str.val)`).
pub open spec fn s_op(st: St, arm1: u32, aux1: u32, arm2: u32, aux2: u32) -> St {
    let c = s_concat(st, arm1, aux1, arm2, aux2);
    St { al: s_free_a(c.0.al, (c.1 + 1) as usize), ..c.0 }
}

pub open spec fn arm_at(win: Seq<u8>, o: int) -> u32 {
    (win[OPS_OFF + OP_BYTES * o] as u32) % NARM
}

pub open spec fn aux_at(win: Seq<u8>, o: int) -> u32 {
    win[OPS_OFF + OP_BYTES * o + 1] as u32
}

pub open spec fn arm2_at(win: Seq<u8>, o: int) -> u32 {
    (win[OPS_OFF + OP_BYTES * o + 2] as u32) % NARM
}

pub open spec fn aux2_at(win: Seq<u8>, o: int) -> u32 {
    win[OPS_OFF + OP_BYTES * o + 3] as u32
}

pub open spec fn s_run(st: St, win: Seq<u8>, o: int, n: int) -> St
    decreases n - o,
{
    if o >= n {
        st
    } else {
        s_run(
            s_op(st, arm_at(win, o), aux_at(win, o), arm2_at(win, o), aux2_at(win, o)),
            win,
            o + 1,
            n,
        )
    }
}

pub open spec fn st_init(win: Seq<u8>) -> St {
    St {
        al: A {
            cnt: Seq::new(MAX_CACHED_MEMORY as nat, |_i: int| 0u32),
            n_alloc: 0,
            n_free: 0,
            n_hit: 0,
            bytes: 0,
        },
        s1: Sl { c: false, req: 0 },
        s2: Sl { c: false, req: 0 },
        acc: rd32s(win, 4) as u64,
    }
}

pub open spec fn cap_of(len: int) -> int {
    (len - OPS_OFF) / (OP_BYTES as int)
}

pub open spec fn n_ops_of(win: Seq<u8>, len: int) -> int {
    (rd32s(win, 0) as int) % (cap_of(len) + 1)
}

pub open spec fn concat_win(win: Seq<u8>, len: int) -> u64 {
    let f = s_run(st_init(win), win, 0, n_ops_of(win, len));
    f.acc ^ tally_of(f.al)
}

pub open spec fn concat_fold(buf: Seq<u8>, off: int, len: int) -> u64 {
    concat_win(buf.subrange(off, off + len), len)
}

// ------------------------------------------------------------------ exec ----

/// The file, the head word and the blob. `external_body` because it is I/O: it
/// is not a function of its arguments and there is no `ensures` to check.
#[verifier::external_body]
fn load_input() -> (r: (u64, u64, Vec<u8>)) {
    let path = driver::arg_path();
    let inp = driver::load(&path);
    let (stride_w, bytes) = driver::head1_u64_bytes(&inp);
    (inp.n_iters, stride_w, bytes)
}

/// `external_body` for the same reason: `println!` is not verifiable, and the
/// item exists so that the kernel's result is CONSUMED.
#[verifier::external_body]
fn emit(acc: u64) {
    driver::emit(acc);
}

pub struct Alloc {
    pub cnt: [u32; MAX_CACHED_MEMORY],
    pub n_alloc: u64,
    pub n_free: u64,
    pub n_hit: u64,
    pub bytes: u64,
}

impl Alloc {
    pub open spec fn a(&self) -> A {
        A {
            cnt: self.cnt@,
            n_alloc: self.n_alloc,
            n_free: self.n_free,
            n_hit: self.n_hit,
            bytes: self.bytes,
        }
    }

    #[inline(always)]
    fn new() -> (r: Alloc)
        ensures
            r.a() == st_init(Seq::empty()).al,
            r.cnt@.len() == MAX_CACHED_MEMORY as int,
    {
        let r = Alloc { cnt: [0u32; MAX_CACHED_MEMORY], n_alloc: 0, n_free: 0, n_hit: 0, bytes: 0 };
        assert(r.cnt@ =~= Seq::new(MAX_CACHED_MEMORY as nat, |_i: int| 0u32));
        r
    }

    /// `_emalloc` -- `zend_alloc.c:142-217`.
    #[inline(always)]
    fn alloc(&mut self, size: usize)
        requires
            size <= 64,
            old(self).cnt@.len() == MAX_CACHED_MEMORY as int,
        ensures
            final(self).a() == s_alloc_a(old(self).a(), size),
            final(self).cnt@.len() == MAX_CACHED_MEMORY as int,
    {
        let rsz: usize = (size + 7) & !7usize;
        let idx: usize = rsz >> 3;
        self.n_alloc = self.n_alloc.wrapping_add(1);
        if idx < MAX_CACHED_MEMORY && self.cnt[idx] > 0 {
            self.cnt[idx] = self.cnt[idx] - 1;
            self.n_hit = self.n_hit.wrapping_add(1);
        } else {
            self.bytes = self.bytes.wrapping_add(rsz as u64);
        }
    }

    /// `_efree` -- `zend_alloc.c:248-289`. ⚠ The class comes from the RECORDED
    /// size (`p->size`, `zend_alloc.h:53`), which for every request this kernel
    /// makes is the size that was asked for.
    #[inline(always)]
    fn free(&mut self, size: usize)
        requires
            size <= 64,
            old(self).cnt@.len() == MAX_CACHED_MEMORY as int,
        ensures
            final(self).a() == s_free_a(old(self).a(), size),
            final(self).cnt@.len() == MAX_CACHED_MEMORY as int,
    {
        let rsz: usize = (size + 7) & !7usize;
        let idx: usize = rsz >> 3;
        self.n_free = self.n_free.wrapping_add(1);
        if idx < MAX_CACHED_MEMORY && self.cnt[idx] < MAX_CACHED_ENTRIES {
            self.cnt[idx] = self.cnt[idx] + 1;
        }
    }

    #[inline(always)]
    fn tally(&self) -> (r: u64)
        ensures
            r == tally_of(self.a()),
    {
        self.n_alloc.wrapping_mul(1000003) ^ self.n_free.wrapping_mul(1000033)
            ^ self.n_hit.wrapping_mul(1000037) ^ self.bytes.wrapping_mul(1000039)
    }
}

// --------------------------------------------------- TRUSTED, item 1 of 2 --
/// `v[i]` with no bounds check.
///
/// ⚠⚠ **WHY R4/R5 HAVE THIS AND R2/R3 DO NOT, AND IT IS A FIDELITY REPAIR RATHER
/// THAN AN OPTIMISATION.** Every window read in the C -- `win[p]`, `ph52_rd32`'s
/// four bytes -- is an UNCHECKED array access: C has no bounds check, and nothing
/// in `concat_function` or `zend_make_printable_zval` verifies that the op record
/// is inside the window. The kernel's structural precondition (`8 <= len`,
/// `off + len <= buf_len`) is what makes it sound, and it is discharged at the
/// CALL SITE in `main`. ▶ A safe-indexed R4 would pay a bounds check the C does
/// not, so the unsafe rung reads the window the way the C reads it and the two
/// safe rungs keep their checks -- which is exactly the R2/R3-vs-R4/R5 distinction
/// this ladder exists to price. `ph53`'s `win_get_unchecked` is the precedent.
///
/// The `requires` is what makes it sound and the `ensures` is what makes it
/// useful; both are trusted, and the twin below is what checks that the
/// `requires` is strong enough to license a CHECKED implementation of the same
/// contract. ⚠ The pinned vstd ships NO spec for `get_unchecked` -- grepped
/// `~/tools/verus/vstd/` entire -- so the wrapper is the trusted boundary.
#[verifier::external_body]
#[inline(always)]
fn win_get_unchecked(v: &[u8], i: usize) -> (r: u8)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    unsafe { *v.get_unchecked(i) }
}

// THE VERIFIED TWIN of trusted item 1 (`harness/check.py` step 5c-twin). Same
// signature and same contract, character for character -- the gate lifts both and
// diffs them, so a trusted item whose contract drifted from what a safe
// implementation can meet is caught. `#[cfg(slb_twin)]`, so no build compiles it.
#[cfg(slb_twin)]
fn slb_twin_win_get_unchecked(v: &[u8], i: usize) -> (r: u8)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    v[i]
}

/// A little-endian u32 at `o`, read the way the C reads it.
#[inline(always)]
fn rd32(w: &[u8], o: usize) -> (r: u32)
    requires
        o + 4 <= w@.len(),
    ensures
        r == rd32s(w@, o as int),
{
    // Ghost only: `spec_slice_len` is what tells the solver a slice length fits in
    // a `usize`, which is what keeps `o + 3` from overflowing.
    assert(w@.len() == vstd::slice::spec_slice_len(w));
    (win_get_unchecked(w, o) as u32) | ((win_get_unchecked(w, o + 1) as u32) << 8)
        | ((win_get_unchecked(w, o + 2) as u32) << 16)
        | ((win_get_unchecked(w, o + 3) as u32) << 24)
}

// --------------------------------------------------- TRUSTED, item 2 of 2 --
/// `(*m).assume_init_ref()` with no initialisedness check, then a copy.
///
/// ⚠⚠ **THE ONLY UNTWINNABLE TRUSTED ITEM ON THIS RUNG, AND `ph53` HAS ONE TOO.** Its `requires`
/// is `MaybeUninit::assume_init_ref`'s OWN precondition, which the pinned vstd
/// states at `std_specs/maybe_uninit.rs:45-49`; in ordinary exec code this costs
/// NO trusted item at all -- `controls/mu_unwrapped.rs` verifies exactly that
/// shape at 0 trusted items and `controls/negatives.py --verus` runs it. What
/// forces the wrapper is `harness/check.py::_scan_unsafe_sites`, and 5c-twin then
/// demands a twin that cannot exist, because there is NO safe exec route from
/// `MaybeUninit<T>` to `T`. See `verus.twin_justifications` in ../spec.md.
#[verifier::external_body]
#[inline(always)]
fn slot_read_unchecked(m: &MaybeUninit<Pr>) -> (r: Pr)
    requires
        m.mem_contents().is_init(),
    ensures
        r == m.mem_contents().value(),
{
    unsafe { *m.assume_init_ref() }
}

/// `_zval_dtor` -- `Zend/zend_variables.c:36-80`.
///
/// ⭐⭐ **THIS IS THE ROW.** `constructed` is the one bit that licenses the read,
/// and deleting the `if` is `zend.c:243` exactly -- which is
/// `controls/r4_nowitness.rs`, the program Verus refuses.
#[inline(always)]
fn zval_dtor(slot: &MaybeUninit<Pr>, constructed: &mut bool, al: &mut Alloc, Ghost(sl): Ghost<Sl>)
    requires
        sl.c == *old(constructed),
        *old(constructed) ==> slot.mem_contents().is_init() && slot.mem_contents().value().req
            == sl.req,
        sl.req <= 64,
        old(al).cnt@.len() == MAX_CACHED_MEMORY as int,
    ensures
        final(al).a() == s_dtor(old(al).a(), sl).0,
        *final(constructed) == s_dtor(old(al).a(), sl).1.c,
        final(al).cnt@.len() == MAX_CACHED_MEMORY as int,
{
    if *constructed {
        let p: Pr = slot_read_unchecked(slot);
        if p.req != 0 {
            al.free(p.req);                                      // :45 STR_FREE_REL
        }
        *constructed = false;
    }
}

/// `zend_make_printable_zval` -- `Zend/zend.c:188-265`, narrowed to five arms.
/// ⚠⚠ **THE WRITE ORDER IS THE C's: the VALUE first, then the thing that decides
/// the teardown arm** -- which on this rung is the witness bit.
#[inline(always)]
fn make_printable_zval(
    arm: u32,
    aux: u32,
    expr_copy: &mut MaybeUninit<Pr>,
    constructed: &mut bool,
    al: &mut Alloc,
    Ghost(sl): Ghost<Sl>,
) -> (r: (bool, usize, u64))
    requires
        arm < NARM,
        aux <= 255,
        sl.c == *old(constructed),
        *old(constructed) ==> old(expr_copy).mem_contents().is_init()
            && old(expr_copy).mem_contents().value().req == sl.req,
        sl.req <= 64,
        old(al).cnt@.len() == MAX_CACHED_MEMORY as int,
    ensures
        ({
            let s = s_print(old(al).a(), sl, arm, aux);
            &&& final(al).a() == s.0
            &&& *final(constructed) == s.1.c
            &&& (s.1.c ==> final(expr_copy).mem_contents().is_init()
                && final(expr_copy).mem_contents().value().req == s.1.req)
            &&& r.0 == s.2
            &&& r.1 == s.3
            &&& r.2 == s.4
            &&& s.1.req <= 64
            &&& s.3 <= 14
        }),
        final(al).cnt@.len() == MAX_CACHED_MEMORY as int,
{
    reveal(s_print);
    if arm == A_STRING {
        // :190-193  expr_copy NEVER WRITTEN; the operand is one attacker byte.
        return (false, 1, (97 + aux % 26) as u64);
    }
    let pr: Pr;
    let mut dig: u64 = 0;
    if arm == A_NULL {
        pr = Pr { req: 0, len: 0 };                // :195-197
    } else if arm == A_BOOL {
        if aux % 2 == 1 {
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
    } else if aux % 2 == 1 {
        // :242  EG(exception) -- THE EARLY EXIT.
        // ⭐ `:243 zval_dtor(expr_copy)` IS HERE, and the `constructed` witness
        // is the ONE BIT that makes it dischargeable. Deleting the test is
        // `controls/r4_nowitness.rs`.
        zval_dtor(expr_copy, constructed, al, Ghost(sl));   // :243
        pr = Pr { req: 0, len: 0 };                // :244-245
    } else {
        al.alloc(OBJ_REQ);                         // :249
        // :250  `sprintf(val, "Object id #%ld", handle)`, NARROWED: the prefix is
        // a constant digest and the handle's decimal digits are folded in the same
        // least-significant-first order `sprintf`'s own loop produces them in.
        // ⚠ `aux` is ONE WINDOW BYTE -- the kernel's projection of
        // `zend_object_handle`, which `zend.h:265` makes an `unsigned int` -- so
        // the handle has AT MOST THREE decimal digits and the case is exhaustive.
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
    // :263  THE TAG, WRITTEN LAST.
    let l: usize = pr.len;
    *expr_copy = MaybeUninit::new(pr);
    *constructed = true;
    (true, l, dig)                                 // :264  *use_copy = 1
}

/// `concat_function` -- `Zend/zend_operators.c:1146-1194`, narrowed.
/// The two slots are the caller's, exactly as `:1148` declares them.
#[inline(always)]
fn concat_function(
    op1_copy: &mut MaybeUninit<Pr>,
    c1: &mut bool,
    op2_copy: &mut MaybeUninit<Pr>,
    c2: &mut bool,
    a1: u32,
    x1: u32,
    a2: u32,
    x2: u32,
    al: &mut Alloc,
    Ghost(st): Ghost<St>,
) -> (r: (usize, u64, u64))
    requires
        a1 < NARM,
        a2 < NARM,
        x1 <= 255,
        x2 <= 255,
        st.al == old(al).a(),
        st.s1.c == *old(c1),
        st.s2.c == *old(c2),
        *old(c1) ==> old(op1_copy).mem_contents().is_init()
            && old(op1_copy).mem_contents().value().req == st.s1.req,
        *old(c2) ==> old(op2_copy).mem_contents().is_init()
            && old(op2_copy).mem_contents().value().req == st.s2.req,
        st.s1.req <= 64,
        st.s2.req <= 64,
        old(al).cnt@.len() == MAX_CACHED_MEMORY as int,
    ensures
        ({
            let c = s_concat(st, a1, x1, a2, x2);
            let n = c.0;
            &&& final(al).a() == n.al
            &&& *final(c1) == n.s1.c
            &&& *final(c2) == n.s2.c
            &&& (n.s1.c ==> final(op1_copy).mem_contents().is_init()
                && final(op1_copy).mem_contents().value().req == n.s1.req)
            &&& (n.s2.c ==> final(op2_copy).mem_contents().is_init()
                && final(op2_copy).mem_contents().value().req == n.s2.req)
            &&& n.s1.req <= 64
            &&& n.s2.req <= 64
            &&& n.acc == mix(mix(mix(st.acc, r.0 as u64), r.1), r.2)
            &&& r.0 == c.1
            &&& r.0 <= 28
        }),
        final(al).cnt@.len() == MAX_CACHED_MEMORY as int,
{
    reveal(s_concat);
    let ghost p1 = s_print(st.al, st.s1, a1, x1);
    let (uc1, n1, g1) = make_printable_zval(a1, x1, op1_copy, c1, al, Ghost(st.s1));  // :1152
    let ghost p2 = s_print(p1.0, st.s2, a2, x2);
    let (uc2, n2, g2) = make_printable_zval(a2, x2, op2_copy, c2, al, Ghost(st.s2));  // :1153

    // :1179-1186 -- the `result != op1` arm.
    let total: usize = n1 + n2;                                      // :1180
    al.alloc(total + 1);                                             // :1181

    if uc1 {
        zval_dtor(op1_copy, c1, al, Ghost(p1.1));                    // :1188
    }
    if uc2 {
        zval_dtor(op2_copy, c2, al, Ghost(p2.1));                    // :1191
    }
    (total, g1, g2)
}

#[cfg_attr(slb_isolated, inline(never))]
#[verifier::rlimit(120)]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> (r: u64)
    requires
        off + len <= buf@.len(),
        8 <= len,
    ensures
        r == concat_fold(buf@, off as int, len as int),
{
    // Ghost only: mentioning `spec_slice_len` fires vstd's `axiom_spec_len`, which
    // is what tells the SMT solver a slice length fits in a `usize`.
    assert(buf@.len() == vstd::slice::spec_slice_len(buf));
    let win: &[u8] = &buf[off..off + len];
    assert(win@ =~= buf@.subrange(off as int, off + len));
    // ... and the window is exactly `len` bytes, which is a `usize` -- that is what
    // bounds `OP_BYTES * o` without needing a second slice axiom.
    assert(win@.len() == len);

    let cap: usize = (len - OPS_OFF) / OP_BYTES;
    let n_ops: usize = (rd32(win, 0) as usize) % (cap + 1);
    let mut acc: u64 = rd32(win, 4) as u64;
    assert(n_ops as int == n_ops_of(win@, len as int));

    // Ghost only: `n_ops <= cap` and `OP_BYTES * cap <= len - OPS_OFF`, so every
    // op record the loop reads is inside the window. Two div/mul facts, named
    // because Z3 does not get either for free.
    proof {
        vstd::arithmetic::div_mod::lemma_fundamental_div_mod(
            (len - OPS_OFF) as int,
            OP_BYTES as int,
        );
        assert(OP_BYTES * (cap as int) <= (len - OPS_OFF) as int);
        assert(n_ops <= cap);
        vstd::arithmetic::mul::lemma_mul_inequality(
            n_ops as int,
            cap as int,
            OP_BYTES as int,
        );
    }
    assert(OPS_OFF + OP_BYTES * (n_ops as int) <= len);

    let mut al: Alloc = Alloc::new();
    // :1148 -- the two caller slots, TYPED AS UNINITIALISED. ⭐ This is the only
    // Rust spelling of `zval op1_copy;` that does not forge a value for the state
    // the C actually has, and the two `bool`s are the whole witness.
    let mut op1_copy: MaybeUninit<Pr> = MaybeUninit::uninit();
    let mut op2_copy: MaybeUninit<Pr> = MaybeUninit::uninit();
    let mut c1: bool = false;
    let mut c2: bool = false;
    let mut o: usize = 0;
    let ghost mut st: St = st_init(win@);
    assert(st.acc == acc);
    while o < n_ops
        invariant
            o <= n_ops,
            n_ops as int == n_ops_of(win@, len as int),
            OPS_OFF + OP_BYTES * (n_ops as int) <= len,
            win@.len() == len,
            st == s_run(st_init(win@), win@, 0, o as int),
            st.al == al.a(),
            st.acc == acc,
            st.s1.c == c1,
            st.s2.c == c2,
            c1 ==> op1_copy.mem_contents().is_init() && op1_copy.mem_contents().value().req
                == st.s1.req,
            c2 ==> op2_copy.mem_contents().is_init() && op2_copy.mem_contents().value().req
                == st.s2.req,
            st.s1.req <= 64,
            st.s2.req <= 64,
            al.cnt@.len() == MAX_CACHED_MEMORY as int,
        decreases n_ops - o,
    {
        // Ghost only: this op record is inside the window.
        proof {
            vstd::arithmetic::mul::lemma_mul_inequality(
                (o + 1) as int,
                n_ops as int,
                OP_BYTES as int,
            );
            assert(OP_BYTES * ((o + 1) as int) == OP_BYTES * (o as int) + OP_BYTES)
                by (nonlinear_arith);
            assert(OPS_OFF + OP_BYTES * (o as int) + OP_BYTES <= len);
        }
        let p: usize = OPS_OFF + OP_BYTES * o;
        let a1: u32 = (win_get_unchecked(win, p) as u32) % NARM;
        let x1: u32 = win_get_unchecked(win, p + 1) as u32;
        let a2: u32 = (win_get_unchecked(win, p + 2) as u32) % NARM;
        let x2: u32 = win_get_unchecked(win, p + 3) as u32;

        let (total, g1, g2) = concat_function(
            &mut op1_copy,
            &mut c1,
            &mut op2_copy,
            &mut c2,
            a1,
            x1,
            a2,
            x2,
            &mut al,
            Ghost(st),
        );

        acc = acc.wrapping_mul(31).wrapping_add(total as u64);
        acc = acc.wrapping_mul(31).wrapping_add(g1);
        acc = acc.wrapping_mul(31).wrapping_add(g2);

        al.free(total + 1);            // the executor releases the temporary
        proof {
            st = s_op(st, a1, x1, a2, x2);
            lemma_run_step(st_init(win@), win@, 0, o as int);
        }
        o = o + 1;
    }
    assert(st == s_run(st_init(win@), win@, 0, n_ops as int));

    let t: u64 = al.tally();
    acc ^ t
}

/// `s_run(st, win, a, o + 1) == s_op(s_run(st, win, a, o), ...at o...)`.
///
/// ⚠ **Verus does not get this for free and the reason is worth the line:**
/// `s_run` recurses on the FRONT of the range, so unfolding it reaches the op at
/// `a`, while the loop invariant needs the op at `o` -- the BACK. One induction on
/// `o - a`, and it is the only lemma this rung has.
#[verifier::rlimit(60)]
pub proof fn lemma_run_step(st: St, win: Seq<u8>, a: int, o: int)
    requires
        a <= o,
    ensures
        s_run(st, win, a, o + 1) == s_op(
            s_run(st, win, a, o),
            arm_at(win, o),
            aux_at(win, o),
            arm2_at(win, o),
            aux2_at(win, o),
        ),
    decreases o - a,
{
    let st1 = s_op(st, arm_at(win, a), aux_at(win, a), arm2_at(win, a), aux2_at(win, a));
    if a == o {
        // `s_run(st, win, a, a)` is `st`, and `s_run(st, win, a, a + 1)` unfolds
        // once to `s_run(st1, win, a + 1, a + 1)`, i.e. `st1`.
        assert(s_run(st, win, a, o) == st);
        assert(s_run(st, win, a, o + 1) == s_run(st1, win, a + 1, o + 1));
        assert(s_run(st1, win, a + 1, o + 1) == st1);
    } else {
        assert(s_run(st, win, a, o) == s_run(st1, win, a + 1, o));
        assert(s_run(st, win, a, o + 1) == s_run(st1, win, a + 1, o + 1));
        lemma_run_step(st1, win, a + 1, o);
    }
}

// ---------------------------------------------------------------- driver ----
fn main() {
    let (n_iters, stride_w, bytes) = load_input();
    // SLB-DRIVER-BEGIN
    let n_blob: usize = bytes.len();
    let buf: &[u8] = bytes.as_slice();
    let mut acc: u64 = 0;
    if stride_w >= 8 && stride_w <= n_blob as u64 {
        let stride: usize = stride_w as usize;
        let nwin: u64 = (n_blob / stride) as u64;
        let mut it: u64 = 0;
        // Ghost only: at least one whole window is present. `stride <= n_blob` is
        // the guard immediately above and integer division only rounds down, so
        // `n_blob / stride >= 1` -- but that is a fact about division and Z3 needs
        // the lemma named.
        proof {
            vstd::arithmetic::div_mod::lemma_div_non_zero(n_blob as int, stride as int);
        }
        while it < n_iters
            invariant
                8 <= stride <= n_blob,
                buf@.len() == n_blob,
                nwin == n_blob / stride,
                nwin >= 1,
            decreases n_iters - it,
        {
            // Ghost only: `k` must land inside the blob. Two nonlinear steps, so
            // Z3 needs both spelled out. Erases at compile time -- R4 and R5 stay
            // byte-identical.
            proof {
                let pr: int = (acc as int) * (nwin as int);
                assert((acc as u128) * (nwin as u128) <= (u64::MAX as u128) * (u64::MAX
                    as u128)) by (nonlinear_arith)
                    requires
                        acc <= u64::MAX,
                        nwin <= u64::MAX,
                ;
                assert(vstd::arithmetic::power2::pow2(64) == 0x1_0000_0000_0000_0000nat) by {
                    vstd::arithmetic::power2::lemma2_to64_rest();
                }
                assert(pr < (nwin as int) * 0x1_0000_0000_0000_0000int) by (nonlinear_arith)
                    requires
                        pr == (acc as int) * (nwin as int),
                        acc <= u64::MAX,
                        nwin >= 1,
                ;
            }
            let k: usize = ((acc as u128 * nwin as u128) >> 64) as usize;
            // Ghost only: the window index `k` names a window that is entirely
            // present, so `k * stride + stride <= n_blob` and the kernel's
            // structural precondition is discharged. Both steps are nonlinear.
            proof {
                assert(k < nwin);
                vstd::arithmetic::div_mod::lemma_fundamental_div_mod(n_blob as int, stride as int);
                assert((nwin as int) * (stride as int) <= n_blob as int);
                assert((k as int) * (stride as int) <= ((nwin as int) - 1) * (stride as int));
                assert(((nwin as int) - 1) * (stride as int) == (nwin as int) * (stride as int)
                    - (stride as int)) by (nonlinear_arith);
                assert((k as int) * (stride as int) + (stride as int) <= n_blob as int);
            }
            let r: u64 = kernel(buf, k * stride, stride);
            // Ghost only: this is what *consumes* the kernel's `ensures`. Without
            // it the postcondition is decoration -- deleting it entirely still
            // verifies, so nothing but mutation testing defends it
            // (`.memory/04-verus.md`).
            assert(r == concat_fold(buf@, (k * stride) as int, stride as int));
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    emit(acc);
}

} // verus!
