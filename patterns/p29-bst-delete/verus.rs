//! p29 rung R5 -- unsafe Rust + a Verus proof.
//!
//! This is unsafe.rs's exec code with the SAFETY comments turned into
//! obligations a verifier discharges. **What is new here is the SHAPE of the
//! obligation.** `p27` -- the project's other temporal row -- proves *at the
//! moment of the read, the record still exists*, and one linear `PointsTo`
//! carries the whole of it. `p29` has to prove **two** things at the moment of
//! the read:
//!
//!   1. the record still exists    -- `perms.dom().contains(g_slot)`, which is
//!      what `live[g_slot] == 1` converts into, and which `rec_close` consumes;
//!   2. the record is still the one FIND returned -- `ky[g_slot] == g_key`,
//!      which is an ordinary VALUE equality and has nothing to do with
//!      linearity, because the two-child splice deallocates nothing.
//!
//! ⚠⚠ **AND AT THIS RUNG THE ORDER OF THE TWO IS NOT A CONVENTION, IT IS
//! FORCED.** In C the safety line is one `if` with `&&` and the short-circuit is
//! what keeps the identity test from being a use-after-free. Here the identity
//! test cannot even be WRITTEN before the liveness test: reading the record
//! needs `perms.tracked_borrow(g_slot)`, and `tracked_borrow` has
//! `self.dom().contains(key)` as a precondition. So the C rung's `&&` ordering
//! is, at R5, a type-system consequence. ../NOTES.md 6.
//!
//! **The proof forces the line the C rung forgot**, exactly as `p27`'s does:
//! without `live[cur] = 0` after the free the loop invariant cannot be
//! re-established, because `rec_free` has consumed slot `cur`'s permission while
//! the liveness array would still claim it exists.
//!
//! **WHAT THE PROOF COSTS, AND IT IS NOT THE SAFETY LINE.** Every walk in every
//! rung carries `live[cur] == 1` and an explicit step bound, and the two-child
//! test asks liveness of both children. **Counted in c/kernel_hardened.c: SIX
//! liveness conjuncts and FIVE step bounds, eleven terms, and not one of them
//! can fire.** They are here because the alternative is to prove that the link
//! structure IS A TREE -- unique parents and acyclicity -- which is what
//! "every link points at a live slot" needs, and which no per-slot invariant
//! gives you. With them, the licence for every record read is `p27`'s own `wf`:
//! `live[i] == 1 <==> perms.dom().contains(i)`, a per-slot fact. ../NOTES.md 4
//! counts them and ../spec.md pins them in every rung.
//!
//! **TCB: seven items** -- `buf_get_unchecked`, `arr_get_unchecked`,
//! `arr_set_unchecked`, `rec_alloc`, `rec_free`, `load_input`, `emit`. The same
//! seven `p27` ships, and **the second obligation costs none of them**: the
//! occupant-identity conjunct is discharged by the functional postcondition, not
//! by a new axiom. Two of the seven are the allocation API, and they are here
//! for a CODEGEN reason rather than a trust reason -- they are
//! `vstd::raw_ptr::allocate` / `deallocate` copied into this crate so the call
//! is direct and `#[inline(always)]`, because vstd carries no `#[inline]` and R4
//! cannot emit a GOT-indirect cross-crate call. **Their verified twins are
//! vstd's own `allocate` and `deallocate`.**
//!
//! **`global layout Rec is size == 4, align == 1;`** is the one declaration this
//! rung adds that `p27` does not need. `p27`'s record is a `u8`, whose layout
//! vstd axiomatises (`layout_of_primitives`, `align_of_u8`); `p29`'s record is a
//! four-byte `#[repr(C)]` struct, because the tree's LINKS live inside it, and
//! Verus gets no layout information from `#[repr(C)]`. The directive both
//! exports the axioms and **emits a static check at codegen**, so it is checked
//! by the compiler on this platform rather than assumed
//! (`_VERUS_DOC_/guide/src/reference-global.md`). ⚠ It is nevertheless an axiom
//! for the verifier and ../NOTES.md 6 counts it as such.
//!
//! SAFETY (1): `off + len <= buf.len()` is the caller's structural
//!   precondition. Unchecked in unsafe.rs; discharged at the call site here.
//! SAFETY (2): `len >= 4` guards the window header.
//! SAFETY (3): the op is read only under `len - p >= 2` with `p <= len`.
//! SAFETY (4): every record read happens under `live[i] == 1`, and `live[i] == 1`
//!   implies the permission for slot `i` is still in the map. That is the
//!   conjunct `p27` also has.
//! SAFETY (5): the read through the CACHED POINTER happens under
//!   `live[g_slot] == 1` **and** `g_saved == tab[g_slot]`, the second being an
//!   invariant that nothing has to re-establish because `tab[]` is written once
//!   per slot and never reset. That is why `tab[cur]` is not nulled on the free
//!   -- see c/kernel.h, where it is argued from `p27`'s bug-class reason as
//!   well.
//! SAFETY (6): `rec_free` is called at most once per record -- the splice clears
//!   `live[cur]` before anything can reach the slot again, and the epilogue frees
//!   only slots still marked alive -- so there is no double free, and every slot
//!   alive at the end is freed, so there is no leak.

// Plain-Rust I/O helpers. Outside `verus!`, so Verus treats the whole module as
// external (external-by-default). Reached only through `load_input`/`emit`.
#[path = "../../common/driver.rs"]
mod driver;

use vstd::layout::valid_layout;
use vstd::map::*;
use vstd::prelude::*;
use vstd::raw_ptr::*;

verus! {

// `group_slice_axioms` gives `slice@.len() == spec_slice_len(slice)`, hence
// `slice@.len() <= usize::MAX`. `group_array_axioms` gives `tab@.len() ==
// TABCAP` and the fill axiom for `[null_mut(); TABCAP]`. `group_layout_axioms`
// + `align_of_u8` are what `into_typed` needs at align 1.
// `group_raw_ptr_axioms` turns `ptr_mut_from_data(p@) == p` into a usable fact.
// `lemma_u128_shr_is_div` and `lemma_mul_inequality` are the DRIVER's.
broadcast use {
    vstd::slice::group_slice_axioms,
    vstd::array::group_array_axioms,
    vstd::layout::group_layout_axioms,
    vstd::layout::align_of_u8,
    vstd::raw_ptr::group_raw_ptr_axioms,
    vstd::bits::lemma_u128_shr_is_div,
    vstd::arithmetic::mul::lemma_mul_inequality,
};

/// The slot table's extent, a compile-time constant in every rung. It is also
/// the walk fuel: at most TABCAP records exist, so no path is longer.
pub const TABCAP: usize = 32;

/// One record, one allocation, `RECSZ` bytes: `key, val, left, right`. The
/// tree's LINKS are inside the record, which is what makes the two-child delete
/// copy the payload rather than move a pointer.
pub const RECSZ: usize = 4;

/// The null link. Outside `0 .. TABCAP`, so `alive(st, NIL)` is false for free.
pub const NIL: u8 = 255;

/// What a rejected operation folds. A compile-time constant in every rung.
pub const SENT: u64 = 251;

/// A record: four bytes, one allocation. `#[repr(C)]` for a stable layout, and
/// the `global layout` directive below is what tells Verus what that layout is.
#[repr(C)]
#[derive(Clone, Copy)]
pub struct Rec {
    pub key: u8,
    pub val: u8,
    pub l: u8,
    pub r: u8,
}

global layout Rec is size == 4, align == 1;

// ------------------------------------------------------------------ spec ----
/// The little-endian u32 at absolute byte position `p`, written out the way
/// every rung writes it. Spelled with `+` and `*` rather than `|` and `<<` on
/// purpose (`.memory/04-verus.md`): the two are the same function on bytes and
/// compile to the same instruction, but only the first is linear arithmetic.
pub open spec fn u32_at(buf: Seq<u8>, p: int) -> int {
    buf[p] as int + 256 * (buf[p + 1] as int) + 65536 * (buf[p + 2] as int) + 16777216 * (
    buf[p + 3] as int)
}

/// How many operations the window at `off` declares. **Declared, and it bounds
/// nothing** -- the cursor guard is what stops the walk.
pub open spec fn nops_at(buf: Seq<u8>, off: int) -> int {
    u32_at(buf, off)
}

/// A record's value is a function of its key, in every rung. So a USE that
/// returns the wrong record's value returns a value no honest read of THIS key
/// could produce, which is what makes the second bug class visible in the
/// checksum at all.
pub open spec fn val_of(a: u8) -> u8 {
    a.wrapping_mul(7).wrapping_add(1)
}

/// THE ABSTRACT MACHINE'S STATE. Five parallel sequences of length `ntab` --
/// the number of slots ever opened, which only grows -- plus the root link and
/// the cached lookup result. `lv` is where the temporal property lives and
/// `ky` is where the OCCUPANT-IDENTITY property lives; the whole of `p29`'s
/// headline is that those are two different sequences.
pub ghost struct St {
    pub ky: Seq<u8>,
    pub vl: Seq<u8>,
    pub lt: Seq<u8>,
    pub rt: Seq<u8>,
    pub lv: Seq<bool>,
    pub root: u8,
    pub gh: bool,
    pub gs: u8,
    pub gk: u8,
}

/// Is slot `x` a live slot? `NIL` is 255 and `lv.len() <= TABCAP == 32`, so
/// this is false for `NIL` without a special case.
pub open spec fn alive(st: St, x: u8) -> bool {
    (x as int) < st.lv.len() && st.lv[x as int]
}

/// THE WALK, shared by INSERT, FIND and REMOVE. Returns
/// `(cur, par, goleft, found)` -- the same four variables the exec loop carries.
/// `fuel` is the exec loop's `TABCAP - steps`.
pub open spec fn descend(st: St, cur: u8, par: u8, gl: bool, k: u8, fuel: nat) -> (u8, u8, bool, bool)
    decreases fuel,
{
    if fuel == 0 || !alive(st, cur) {
        (cur, par, gl, false)
    } else if k < st.ky[cur as int] {
        descend(st, st.lt[cur as int], cur, true, k, (fuel - 1) as nat)
    } else if k > st.ky[cur as int] {
        descend(st, st.rt[cur as int], cur, false, k, (fuel - 1) as nat)
    } else {
        (cur, par, gl, true)
    }
}

/// THE SUCCESSOR DESCENT: leftmost node of the subtree rooted at `s`. Returns
/// `(s, sp, sgoleft)`.
pub open spec fn succ_walk(st: St, s: u8, sp: u8, sgl: bool, fuel: nat) -> (u8, u8, bool)
    decreases fuel,
{
    if fuel == 0 || !alive(st, st.lt[s as int]) {
        (s, sp, sgl)
    } else {
        succ_walk(st, st.lt[s as int], s, true, (fuel - 1) as nat)
    }
}

/// THE DELETION, delete-by-substitution.
///
/// Two children: the successor's key and val are copied INTO the victim's
/// record and the cursor moves to the successor. **`lv` does not change here**
/// -- nothing is deallocated -- and that is the whole reason `p29`'s safety
/// line needs a second conjunct.
///
/// Zero or one child: the node is unlinked and its record is freed, which is
/// the `lv.update(cur, false)`.
pub open spec fn del_walk(st: St, cur: u8, par: u8, gl: bool, guard: nat) -> St
    decreases guard,
{
    if guard == 0 {
        st
    } else if alive(st, st.lt[cur as int]) && alive(st, st.rt[cur as int]) {
        let sd = succ_walk(st, st.rt[cur as int], cur, false, TABCAP as nat);
        let st2 = St {
            ky: st.ky.update(cur as int, st.ky[sd.0 as int]),
            vl: st.vl.update(cur as int, st.vl[sd.0 as int]),
            ..st
        };
        del_walk(st2, sd.0, sd.1, sd.2, (guard - 1) as nat)
    } else {
        let ch = if st.lt[cur as int] != NIL {
            st.lt[cur as int]
        } else {
            st.rt[cur as int]
        };
        let st2 = if par == NIL {
            St { root: ch, ..st }
        } else if gl {
            St { lt: st.lt.update(par as int, ch), ..st }
        } else {
            St { rt: st.rt.update(par as int, ch), ..st }
        };
        St { lv: st2.lv.update(cur as int, false), ..st2 }
    }
}

/// A fresh record, linked where the walk stopped.
pub open spec fn ins_new(st: St, par: u8, gl: bool, a: u8) -> St {
    let n = st.ky.len();
    let st2 = St {
        ky: st.ky.push(a),
        vl: st.vl.push(val_of(a)),
        lt: st.lt.push(NIL),
        rt: st.rt.push(NIL),
        lv: st.lv.push(true),
        ..st
    };
    if par == NIL {
        St { root: n as u8, ..st2 }
    } else if gl {
        St { lt: st2.lt.update(par as int, n as u8), ..st2 }
    } else {
        St { rt: st2.rt.update(par as int, n as u8), ..st2 }
    }
}

/// ONE OPERATION: the new state and what it folds.
///
/// **The last arm is the whole pattern.** A USE folds the cached record's `val`
/// only when `lv[gs]` AND `ky[gs] == gk`; a rung that folds it under either
/// condition alone is not this function, and `c/kernel.c` folds it under
/// neither.
pub open spec fn step(st: St, c: u8, a: u8) -> (St, u64) {
    if c % 4 == 0 {
        let d = descend(st, st.root, NIL, false, a, TABCAP as nat);
        if d.3 {
            (St { vl: st.vl.update(d.0 as int, val_of(a)), ..st }, a as u64)
        } else if st.ky.len() < TABCAP as int {
            (ins_new(st, d.1, d.2, a), a as u64)
        } else {
            (st, SENT)
        }
    } else if c % 4 == 1 {
        let d = descend(st, st.root, NIL, false, a, TABCAP as nat);
        if d.3 {
            (St { gh: true, gs: d.0, gk: a, ..st }, 1u64)
        } else {
            (st, SENT)
        }
    } else if c % 4 == 2 {
        let d = descend(st, st.root, NIL, false, a, TABCAP as nat);
        if d.3 {
            (del_walk(st, d.0, d.1, d.2, TABCAP as nat), 2u64)
        } else {
            (st, SENT)
        }
    } else {
        if st.gh && st.lv[st.gs as int] && st.ky[st.gs as int] == st.gk {
            (st, st.vl[st.gs as int] as u64)
        } else {
            (st, SENT)
        }
    }
}

/// The empty machine.
pub open spec fn st0() -> St {
    St {
        ky: Seq::empty(),
        vl: Seq::empty(),
        lt: Seq::empty(),
        rt: Seq::empty(),
        lv: Seq::empty(),
        root: NIL,
        gh: false,
        gs: 0,
        gk: 0,
    }
}

/// THE ABSTRACT MACHINE. It describes the PROGRAM -- stop when the window runs
/// out, reject an INSERT past TABCAP, reject a FIND or a REMOVE of an absent
/// key, fold SENT for a USE whose cached record is gone or re-occupied -- and it
/// says nothing about `nops` being honest or about the op stream being well
/// formed. Every adversarial input is inside this domain (../spec.md).
pub open spec fn run(
    buf: Seq<u8>,
    off: int,
    len: int,
    o: int,
    nops: int,
    p: int,
    st: St,
    acc: u64,
) -> u64
    decreases nops - o,
{
    if o >= nops || len - p < 2 {
        acc.wrapping_mul(31).wrapping_add(st.ky.len() as u64)
    } else {
        let s = step(st, buf[off + p], buf[off + p + 1]);
        run(buf, off, len, o + 1, nops, p + 2, s.0, acc.wrapping_mul(31).wrapping_add(s.1))
    }
}

/// What the kernel must return.
pub open spec fn bst_fold(buf: Seq<u8>, off: int, len: int) -> u64 {
    if len < 4 {
        0
    } else if nops_at(buf, off) == 0 {
        0
    } else {
        run(buf, off, len, 0, nops_at(buf, off), 4, st0(), 0)
    }
}

/// THE TEMPORAL INVARIANT, one slot of it -- the PERMISSION half. A slot the
/// exec array calls alive has a permission naming that slot's pointer, and the
/// four bytes behind the pointer are the four the abstract machine says.
pub open spec fn rec_ok(
    tab: Seq<*mut Rec>,
    st: St,
    perms: Map<int, PointsTo<Rec>>,
    j: int,
) -> bool {
    &&& perms.dom().contains(j)
    &&& perms[j].ptr() == tab[j]
    &&& perms[j].is_init()
    &&& perms[j].value() == (Rec { key: st.ky[j], val: st.vl[j], l: st.lt[j], r: st.rt[j] })
}

/// The DEALLOC half, kept separate so that the walk -- which reads records and
/// frees nothing -- needs only the half above.
pub open spec fn dal_ok(tab: Seq<*mut Rec>, dal: Map<int, Dealloc>, j: int) -> bool {
    &&& dal.dom().contains(j)
    &&& dal[j].addr() == tab[j].addr()
    &&& dal[j].size() == RECSZ
    &&& dal[j].align() == 1
    &&& dal[j].provenance() == tab[j]@.provenance
}

/// THE READ-SIDE INVARIANT.
///
/// The length block is bookkeeping. The two `lt`/`rt` blocks are what license
/// `live[cur]` to be INDEXED at all -- every link is `NIL` or a real slot -- and
/// note what they are NOT: they say nothing about a link pointing at a LIVE
/// slot, which is the tree invariant (unique parents, acyclicity) and which no
/// per-slot fact gives you. That is what the walks' `live[cur] == 1` conjunct
/// buys instead. The last block is `p27`'s temporal invariant.
pub open spec fn base(
    tab: Seq<*mut Rec>,
    live: Seq<u8>,
    st: St,
    ntab: int,
    perms: Map<int, PointsTo<Rec>>,
) -> bool {
    &&& 0 <= ntab <= TABCAP
    &&& tab.len() == TABCAP
    &&& live.len() == TABCAP
    &&& st.ky.len() == ntab
    &&& st.vl.len() == ntab
    &&& st.lt.len() == ntab
    &&& st.rt.len() == ntab
    &&& st.lv.len() == ntab
    &&& forall|j: int| 0 <= j < ntab ==> ((#[trigger] st.lv[j]) <==> live[j] == 1u8)
    &&& forall|j: int| 0 <= j < ntab ==> (#[trigger] st.lt[j]) == NIL || (st.lt[j] as int) < ntab
    &&& forall|j: int| 0 <= j < ntab ==> (#[trigger] st.rt[j]) == NIL || (st.rt[j] as int) < ntab
    &&& st.root == NIL || (st.root as int) < ntab
    &&& forall|j: int| 0 <= j < ntab && st.lv[j] ==> #[trigger] rec_ok(tab, st, perms, j)
}

/// THE WHOLE INVARIANT: the read side, the dealloc tokens, and **`p29`'s own two
/// conjuncts** -- the cached slot is a real slot, and the cached ADDRESS is that
/// slot's record. The second is an invariant that **no operation has to
/// re-establish**, because `tab[]` is written once per slot and never reset;
/// that is the proof-side reason `tab[cur]` is not nulled on the free, and
/// c/kernel.h gives `p27`'s bug-class reason for the same decision.
pub open spec fn wf(
    tab: Seq<*mut Rec>,
    live: Seq<u8>,
    st: St,
    ntab: int,
    perms: Map<int, PointsTo<Rec>>,
    dal: Map<int, Dealloc>,
    g_saved: *mut Rec,
) -> bool {
    &&& base(tab, live, st, ntab, perms)
    &&& forall|j: int| 0 <= j < ntab && st.lv[j] ==> #[trigger] dal_ok(tab, dal, j)
    &&& st.gh ==> (st.gs as int) < ntab
    &&& st.gh ==> g_saved == tab[st.gs as int]
}

// ------------------------------------------------------------------- TCB ----
// TRUSTED ITEM 1 of 7. vstd ships no specification for `<[T]>::get_unchecked`,
// so this is the axiom that licenses the unchecked read of the window. It is
// sound because the standard library's documented contract for `get_unchecked`
// is exactly this: if the caller guarantees `i < v.len()`, the call is defined
// and returns `v[i]`. Every unsafe rung in this project ships it.
#[inline(always)]
#[verifier::external_body]
fn buf_get_unchecked(v: &[u8], i: usize) -> (r: u8)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    unsafe { *v.get_unchecked(i) }
}

// THE VERIFIED TWIN of trusted item 1.
#[cfg(slb_twin)]
fn slb_twin_buf_get_unchecked(v: &[u8], i: usize) -> (r: u8)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    v[i]
}

// TRUSTED ITEM 6 of 7: the input loader. Plain Rust I/O, no `unsafe`, no
// `ensures` -- it is outside the memory-safety argument entirely.
#[verifier::external_body]
fn load_input() -> (r: (u64, u64, Vec<u8>)) {
    let path = driver::arg_path();
    let inp = driver::load(&path);
    let (stride_w, bytes) = driver::head1_u64_bytes(&inp);
    (inp.n_iters, stride_w, bytes)
}

// TRUSTED ITEM 7 of 7: the output. Same shape, same reason.
#[verifier::external_body]
fn emit(acc: u64) {
    driver::emit(acc);
}

// TRUSTED ITEMS 2 and 3 of 7: the unchecked ARRAY read and store, generic over
// the element type so that the pointer table and the liveness array share one
// accessor. Same documented `get_unchecked` contract as item 1.
#[inline(always)]
#[verifier::external_body]
fn arr_get_unchecked<T: Copy, const N: usize>(v: &[T; N], i: usize) -> (r: T)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    unsafe { *v.get_unchecked(i) }
}

#[cfg(slb_twin)]
fn slb_twin_arr_get_unchecked<T: Copy, const N: usize>(v: &[T; N], i: usize) -> (r: T)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int],
{
    v[i]
}

#[inline(always)]
#[verifier::external_body]
fn arr_set_unchecked<T: Copy, const N: usize>(v: &mut [T; N], i: usize, x: T)
    requires
        i < old(v)@.len(),
    ensures
        final(v)@ == old(v)@.update(i as int, x),
{
    unsafe {
        *v.get_unchecked_mut(i) = x;
    }
}

#[cfg(slb_twin)]
fn slb_twin_arr_set_unchecked<T: Copy, const N: usize>(v: &mut [T; N], i: usize, x: T)
    requires
        i < old(v)@.len(),
    ensures
        final(v)@ == old(v)@.update(i as int, x),
{
    v[i] = x;
}

// TRUSTED ITEM 4 of 7. `vstd::raw_ptr::allocate` with vstd's `requires`
// verbatim, THREE of vstd's FIVE `ensures`, and vstd's body with
// `alloc::alloc::` respelled `std::alloc::` -- copied into this crate for ONE
// reason, which is codegen: vstd carries no `#[inline]` on `allocate`, so a rung
// that called it would emit a GOT-indirect cross-crate `call` that unsafe.rs
// cannot produce. The two dropped `ensures` are vstd's
// `pt.0.addr() + size <= usize::MAX + 1` and `pt.0.addr() % align == 0`; at
// `align == 1` the second is trivial and neither is used here. Dropping them
// makes the item strictly WEAKER, which is the direction the gate asks for.
// **Its verified twin is vstd's `allocate` itself.**
#[inline(always)]
#[verifier::external_body]
fn rec_alloc(size: usize, align: usize) -> (pt: (*mut u8, Tracked<PointsToRaw>, Tracked<Dealloc>))
    requires
        valid_layout(size, align),
        size != 0,
    ensures
        pt.1@.is_range(pt.0.addr() as int, size as int),
        pt.2@@ == (DeallocData {
            addr: pt.0.addr(),
            size: size as nat,
            align: align as nat,
            provenance: pt.1@.provenance(),
        }),
        pt.0@.provenance == pt.1@.provenance(),
    opens_invariants none
{
    // SAFETY: valid_layout is a precondition
    let layout = unsafe { std::alloc::Layout::from_size_align_unchecked(size, align) };
    // SAFETY: size != 0
    let p = unsafe { std::alloc::alloc(layout) };
    if p == core::ptr::null_mut() {
        std::process::abort();
    }
    (p, Tracked::assume_new(), Tracked::assume_new())
}

// THE VERIFIED TWIN of trusted item 4, and it is vstd's own `allocate`.
#[cfg(slb_twin)]
fn slb_twin_rec_alloc(size: usize, align: usize) -> (pt: (*mut u8, Tracked<PointsToRaw>, Tracked<Dealloc>))
    requires
        valid_layout(size, align),
        size != 0,
    ensures
        pt.1@.is_range(pt.0.addr() as int, size as int),
        pt.2@@ == (DeallocData {
            addr: pt.0.addr(),
            size: size as nat,
            align: align as nat,
            provenance: pt.1@.provenance(),
        }),
        pt.0@.provenance == pt.1@.provenance(),
    opens_invariants none
{
    allocate(size, align)
}

// TRUSTED ITEM 5 of 7, and THE REAL `free`. `vstd::raw_ptr::deallocate`: all six
// of vstd's `requires` and no `ensures`, local for the same codegen reason as
// item 4, with vstd's own `deallocate` as its twin.
//
// **It CONSUMES the `PointsToRaw` and the `Dealloc`**, and that is half of the
// temporal argument: after this call the caller has no permission to present, so
// a later read of the same address is unprovable. ⚠ **It is only half.** The
// two-child splice calls this on the SUCCESSOR and not on the victim, so the
// victim's permission survives and a stale read of the victim IS provable --
// which is exactly why the safety line has a second conjunct that has nothing to
// do with linearity. ../NOTES.md 2.
#[inline(always)]
#[verifier::external_body]
fn rec_free(
    p: *mut u8,
    size: usize,
    align: usize,
    pt: Tracked<PointsToRaw>,
    dealloc: Tracked<Dealloc>,
)
    requires
        dealloc@.addr() == p.addr(),
        dealloc@.size() == size,
        dealloc@.align() == align,
        dealloc@.provenance() == pt@.provenance(),
        pt@.is_range(dealloc@.addr() as int, dealloc@.size() as int),
        p@.provenance == dealloc@.provenance(),
    opens_invariants none
{
    // SAFETY: ensured by the dealloc token
    let layout = unsafe { std::alloc::Layout::from_size_align_unchecked(size, align) };
    unsafe {
        std::alloc::dealloc(p, layout);
    }
}

// THE VERIFIED TWIN of trusted item 5, and it is vstd's own `deallocate`.
#[cfg(slb_twin)]
fn slb_twin_rec_free(
    p: *mut u8,
    size: usize,
    align: usize,
    pt: Tracked<PointsToRaw>,
    dealloc: Tracked<Dealloc>,
)
    requires
        dealloc@.addr() == p.addr(),
        dealloc@.size() == size,
        dealloc@.align() == align,
        dealloc@.provenance() == pt@.provenance(),
        pt@.is_range(dealloc@.addr() as int, dealloc@.size() as int),
        p@.provenance == dealloc@.provenance(),
    opens_invariants none
{
    deallocate(p, size, align, pt, dealloc)
}

// --------------------------------------------------------- the record ops ---
// **NOT trusted items.** `rec_open`, `rec_close`, `rec_read` and `rec_write` are
// ordinary verified functions. Everything unchecked they do happens either
// inside vstd -- `ptr_ref` and `ptr_mut_write` are `external_body` there,
// `into_typed`, `into_raw` and `leak_contents` are vstd `axiom fn`s -- or inside
// items 4 and 5, whose twins are vstd's own allocation API.
#[inline(always)]
fn rec_open(v: Rec) -> (r: (*mut Rec, Tracked<PointsTo<Rec>>, Tracked<Dealloc>))
    ensures
        r.1@.ptr() == r.0,
        r.1@.is_init(),
        r.1@.value() == v,
        r.2@.addr() == r.0.addr(),
        r.2@.size() == RECSZ,
        r.2@.align() == 1,
        r.2@.provenance() == r.0@.provenance,
{
    assert(valid_layout(RECSZ, 1));
    let (base, Tracked(raw), Tracked(dealloc)) = rec_alloc(RECSZ, 1);
    let tracked mut pt = raw.into_typed::<Rec>(base.addr());
    let q: *mut Rec = base as *mut Rec;
    assert(pt.ptr() == q);
    ptr_mut_write(q, Tracked(&mut pt), v);
    (q, Tracked(pt), Tracked(dealloc))
}

// THE REAL `free`.
#[inline(always)]
fn rec_close(p: *mut Rec, Tracked(pt): Tracked<PointsTo<Rec>>, Tracked(dl): Tracked<Dealloc>)
    requires
        pt.ptr() == p,
        dl.addr() == p.addr(),
        dl.size() == RECSZ,
        dl.align() == 1,
        dl.provenance() == p@.provenance,
{
    let tracked mut q = pt;
    proof {
        q.leak_contents();
    }
    let tracked raw = q.into_raw();
    let base: *mut u8 = p as *mut u8;
    rec_free(base, RECSZ, 1, Tracked(raw), Tracked(dl));
}

#[inline(always)]
fn rec_read(p: *mut Rec, Tracked(pt): Tracked<&PointsTo<Rec>>) -> (r: Rec)
    requires
        pt.ptr() == p,
        pt.is_init(),
    ensures
        r == pt.value(),
{
    *ptr_ref(p, Tracked(pt))
}

#[inline(always)]
fn rec_write(p: *mut Rec, Tracked(pt): Tracked<&mut PointsTo<Rec>>, v: Rec)
    requires
        old(pt).ptr() == p,
    ensures
        final(pt).ptr() == p,
        final(pt).is_init(),
        final(pt).value() == v,
{
    ptr_mut_write(p, Tracked(pt), v);
}

// THE WALK, shared by INSERT, FIND and REMOVE, and written once because all
// three spell it identically in every rung. Its `ensures` is the refinement:
// what the loop computes is exactly what the abstract machine's `descend` says.
//
// ⚠ **The `live[cur] == 1` conjunct in the loop condition is what licenses the
// record read**, through `base`'s `lv[j] ==> rec_ok(..)`. Without it the read
// would need "every link points at a live slot", which is the tree invariant.
// The `steps < TABCAP` conjunct is the `decreases` measure. Neither ever fires.
#[inline(always)]
fn walk(
    tab: &[*mut Rec; TABCAP],
    live: &[u8; TABCAP],
    Tracked(perms): Tracked<&Map<int, PointsTo<Rec>>>,
    Ghost(st): Ghost<St>,
    Ghost(ntab): Ghost<int>,
    root: u8,
    k: u8,
) -> (r: (u8, u8, bool, bool))
    requires
        base(tab@, live@, st, ntab, *perms),
        root == st.root,
    ensures
        r == descend(st, st.root, NIL, false, k, TABCAP as nat),
        r.0 == NIL || (r.0 as int) < ntab,
        r.1 == NIL || alive(st, r.1),
        r.3 ==> alive(st, r.0),
{
    let mut cur: u8 = root;
    let mut par: u8 = NIL;
    let mut gl: bool = false;
    let mut found: bool = false;
    let mut steps: usize = 0;
    while cur != NIL && arr_get_unchecked(live, cur as usize) == 1u8 && steps < TABCAP
        invariant_except_break
            !found,
            steps <= TABCAP,
            cur == NIL || (cur as int) < ntab,
            par == NIL || alive(st, par),
            base(tab@, live@, st, ntab, *perms),
            descend(st, cur, par, gl, k, (TABCAP - steps) as nat) == descend(
                st,
                st.root,
                NIL,
                false,
                k,
                TABCAP as nat,
            ),
        ensures
            (cur, par, gl, found) == descend(st, st.root, NIL, false, k, TABCAP as nat),
            cur == NIL || (cur as int) < ntab,
            par == NIL || alive(st, par),
            found ==> alive(st, cur),
        decreases TABCAP - steps,
    {
        assert(alive(st, cur));
        assert(rec_ok(tab@, st, *perms, cur as int));
        let rec: Rec = {
            let tracked t = perms.tracked_borrow(cur as int);
            rec_read(arr_get_unchecked(tab, cur as usize), Tracked(t))
        };
        steps = steps + 1;
        if k < rec.key {
            par = cur;
            gl = true;
            cur = rec.l;
        } else if k > rec.key {
            par = cur;
            gl = false;
            cur = rec.r;
        } else {
            found = true;
            break;
        }
    }
    (cur, par, gl, found)
}

// ---------------------------------------------------------------- kernel ----
// Same exec code as unsafe.rs. Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> (r: u64)
    requires
        off + len <= buf@.len(),
    ensures
        r == bst_fold(buf@, off as int, len as int),
{
    // Ghost only: mentioning `spec_slice_len` fires vstd's `axiom_spec_len`,
    // which is what tells the SMT solver a slice length fits in a `usize`.
    assert(buf@.len() == vstd::slice::spec_slice_len(buf));
    if len < 4 {
        return 0;
    }
    let nops: usize = buf_get_unchecked(buf, off) as usize + 256 * (buf_get_unchecked(
        buf,
        off + 1,
    ) as usize) + 65536 * (buf_get_unchecked(buf, off + 2) as usize) + 16777216 * (
    buf_get_unchecked(buf, off + 3) as usize);
    if nops == 0 {
        return 0;
    }
    let mut tab: [*mut Rec; TABCAP] = [core::ptr::null_mut(); TABCAP];
    let mut live: [u8; TABCAP] = [0u8; TABCAP];
    let tracked mut perms = Map::<int, PointsTo<Rec>>::tracked_empty();
    let tracked mut dal = Map::<int, Dealloc>::tracked_empty();
    let ghost mut st: St = st0();
    let mut ntab: usize = 0;
    let mut root: u8 = NIL;
    let mut g_saved: *mut Rec = core::ptr::null_mut();
    let mut g_has: bool = false;
    let mut g_slot: u8 = 0;
    let mut g_key: u8 = 0;
    let mut acc: u64 = 0;
    let mut p: usize = 4;
    let mut o: usize = 0;
    while o < nops
        invariant_except_break
            o <= nops,
            p <= len,
            off + len <= buf@.len(),
            buf@.len() <= usize::MAX,
            root == st.root,
            g_has == st.gh,
            g_slot == st.gs,
            g_key == st.gk,
            wf(tab@, live@, st, ntab as int, perms, dal, g_saved),
            run(buf@, off as int, len as int, o as int, nops as int, p as int, st, acc)
                == run(buf@, off as int, len as int, 0, nops as int, 4, st0(), 0),
        ensures
            wf(tab@, live@, st, ntab as int, perms, dal, g_saved),
            acc.wrapping_mul(31).wrapping_add(ntab as u64) == run(
                buf@,
                off as int,
                len as int,
                0,
                nops as int,
                4,
                st0(),
                0,
            ),
        decreases nops - o,
    {
        if len - p < 2 {
            break;
        }
        let c: u8 = buf_get_unchecked(buf, off + p);
        let a: u8 = buf_get_unchecked(buf, off + p + 1);
        let ghost st_in = st;
        let ghost acc_in = acc;
        let ghost p_in = p as int;
        let ghost o_in = o as int;
        p = p + 2;
        if c % 4 == 0 {
            let (cur, par, gl, found) = walk(&tab, &live, Tracked(&perms), Ghost(st), Ghost(ntab as int), root, a);
            if found {
                // A DUPLICATE key updates the record's val IN PLACE. One write
                // to a live record, and the only proof it needs is that the
                // permission it borrows is the one the invariant names.
                let ghost jj = cur as int;
                let ghost st0v = st;
                let ghost perms0 = perms;
                assert(alive(st, cur));
                assert(rec_ok(tab@, st, perms, jj));
                let tracked t = perms.tracked_borrow_mut(jj);
                let cb = arr_get_unchecked(&tab, cur as usize);
                let co = rec_read(cb, Tracked(&*t));
                rec_write(
                    cb,
                    Tracked(t),
                    Rec {
                        key: co.key,
                        val: a.wrapping_mul(7).wrapping_add(1),
                        l: co.l,
                        r: co.r,
                    },
                );
                proof {
                    st = St { vl: st.vl.update(jj, val_of(a)), ..st };
                    assert forall|j: int| 0 <= j < ntab as int && st.lv[j] implies rec_ok(
                        tab@,
                        st,
                        perms,
                        j,
                    ) by {
                        if j != jj {
                            assert(rec_ok(tab@, st0v, perms0, j));
                        }
                    }
                    assert forall|j: int| 0 <= j < ntab as int && st.lv[j] implies dal_ok(
                        tab@,
                        dal,
                        j,
                    ) by {
                        assert(st0v.lv[j]);
                    }
                }
                acc = acc.wrapping_mul(31).wrapping_add(a as u64);
            } else if ntab < TABCAP {
                let ghost n0 = ntab as int;
                let ghost st0v = st;
                let ghost perms0 = perms;
                let ghost dal0 = dal;
                let ghost tab0 = tab@;
                let (q, Tracked(pt), Tracked(dd)) = rec_open(
                    Rec { key: a, val: a.wrapping_mul(7).wrapping_add(1), l: NIL, r: NIL },
                );
                proof {
                    perms.tracked_insert(n0, pt);
                    dal.tracked_insert(n0, dd);
                    st = St {
                        ky: st.ky.push(a),
                        vl: st.vl.push(val_of(a)),
                        lt: st.lt.push(NIL),
                        rt: st.rt.push(NIL),
                        lv: st.lv.push(true),
                        ..st
                    };
                }
                arr_set_unchecked(&mut tab, ntab, q);
                arr_set_unchecked(&mut live, ntab, 1u8);
                let newslot: u8 = ntab as u8;
                ntab = ntab + 1;
                proof {
                    assert forall|j: int| 0 <= j < ntab as int && st.lv[j] implies rec_ok(
                        tab@,
                        st,
                        perms,
                        j,
                    ) by {
                        if j < n0 {
                            assert(st0v.lv[j]);
                            assert(rec_ok(tab0, st0v, perms0, j));
                        }
                    }
                    assert forall|j: int| 0 <= j < ntab as int && st.lv[j] implies dal_ok(
                        tab@,
                        dal,
                        j,
                    ) by {
                        if j < n0 {
                            assert(st0v.lv[j]);
                            assert(dal_ok(tab0, dal0, j));
                        }
                    }
                }
                if par == NIL {
                    let ghost st1v = st;
                    let ghost perms1 = perms;
                    root = newslot;
                    proof {
                        st = St { root: newslot, ..st };
                        assert forall|j: int| 0 <= j < ntab as int && st.lv[j] implies rec_ok(
                            tab@,
                            st,
                            perms,
                            j,
                        ) by {
                            assert(rec_ok(tab@, st1v, perms1, j));
                        }
                        assert forall|j: int| 0 <= j < ntab as int && st.lv[j] implies dal_ok(
                            tab@,
                            dal,
                            j,
                        ) by {
                            assert(st1v.lv[j]);
                        }
                    }
                } else {
                    let ghost pj = par as int;
                    let ghost st1v = st;
                    let ghost perms1 = perms;
                    assert(alive(st, par));
                    assert(rec_ok(tab@, st, perms, pj));
                    let tracked t = perms.tracked_borrow_mut(pj);
                    let pb = arr_get_unchecked(&tab, par as usize);
                    let po = rec_read(pb, Tracked(&*t));
                    if gl {
                        rec_write(
                            pb,
                            Tracked(t),
                            Rec { key: po.key, val: po.val, l: newslot, r: po.r },
                        );
                        proof {
                            st = St { lt: st.lt.update(pj, newslot), ..st };
                        }
                    } else {
                        rec_write(
                            pb,
                            Tracked(t),
                            Rec { key: po.key, val: po.val, l: po.l, r: newslot },
                        );
                        proof {
                            st = St { rt: st.rt.update(pj, newslot), ..st };
                        }
                    }
                    proof {
                        assert forall|j: int| 0 <= j < ntab as int && st.lv[j] implies rec_ok(
                            tab@,
                            st,
                            perms,
                            j,
                        ) by {
                            if j != pj {
                                assert(rec_ok(tab@, st1v, perms1, j));
                            }
                        }
                        assert forall|j: int| 0 <= j < ntab as int && st.lv[j] implies dal_ok(
                            tab@,
                            dal,
                            j,
                        ) by {
                            assert(st1v.lv[j]);
                        }
                    }
                }
                acc = acc.wrapping_mul(31).wrapping_add(a as u64);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else if c % 4 == 1 {
            let (cur, _par, _gl, found) = walk(&tab, &live, Tracked(&perms), Ghost(st), Ghost(ntab as int), root, a);
            if found {
                // THE CACHED POINTER. `tab[cur]` is written once per slot and
                // never reset, so `g_saved == tab[g_slot]` is an invariant that
                // no later operation has to re-establish -- which is the
                // proof-side reason the free does not null `tab[cur]`.
                let ghost st1v = st;
                let ghost perms1 = perms;
                g_saved = arr_get_unchecked(&tab, cur as usize);
                g_has = true;
                g_slot = cur;
                g_key = a;
                proof {
                    st = St { gh: true, gs: cur, gk: a, ..st };
                    assert forall|j: int| 0 <= j < ntab as int && st.lv[j] implies rec_ok(
                        tab@,
                        st,
                        perms,
                        j,
                    ) by {
                        assert(rec_ok(tab@, st1v, perms1, j));
                    }
                    assert forall|j: int| 0 <= j < ntab as int && st.lv[j] implies dal_ok(
                        tab@,
                        dal,
                        j,
                    ) by {
                        assert(st1v.lv[j]);
                    }
                }
                acc = acc.wrapping_mul(31).wrapping_add(1);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else if c % 4 == 2 {
            let (cur0, par0, gl0, found) = walk(&tab, &live, Tracked(&perms), Ghost(st), Ghost(ntab as int), root, a);
            if found {
                let mut cur: u8 = cur0;
                let mut par: u8 = par0;
                let mut gl: bool = gl0;
                let mut guard: usize = 0;
                let ghost st_d = st;
                while guard < TABCAP
                    invariant_except_break
                        guard <= TABCAP,
                        alive(st, cur),
                        par == NIL || alive(st, par),
                        root == st.root,
                        g_has == st.gh,
                        g_slot == st.gs,
                        g_key == st.gk,
                        wf(tab@, live@, st, ntab as int, perms, dal, g_saved),
                        del_walk(st, cur, par, gl, (TABCAP - guard) as nat) == del_walk(
                            st_d,
                            cur0,
                            par0,
                            gl0,
                            TABCAP as nat,
                        ),
                    ensures
                        root == st.root,
                        g_has == st.gh,
                        g_slot == st.gs,
                        g_key == st.gk,
                        wf(tab@, live@, st, ntab as int, perms, dal, g_saved),
                        st == del_walk(st_d, cur0, par0, gl0, TABCAP as nat),
                    decreases TABCAP - guard,
                {
                    assert(rec_ok(tab@, st, perms, cur as int));
                    let cb = arr_get_unchecked(&tab, cur as usize);
                    let crec: Rec = {
                        let tracked t = perms.tracked_borrow(cur as int);
                        rec_read(cb, Tracked(t))
                    };
                    guard = guard + 1;
                    if crec.l != NIL && arr_get_unchecked(&live, crec.l as usize) == 1u8
                        && crec.r != NIL && arr_get_unchecked(&live, crec.r as usize) == 1u8 {
                        // TWO CHILDREN. The in-order successor's key and val are
                        // copied INTO the victim's record and the SUCCESSOR is
                        // the record the next turn frees. **Nothing is
                        // deallocated here**, so no permission is consumed and
                        // the victim's slot stays in the map -- which is exactly
                        // the bug class a linear resource cannot see.
                        let mut sp: u8 = cur;
                        let mut s: u8 = crec.r;
                        let mut sgl: bool = false;
                        let mut sst: usize = 0;
                        let ghost s_in = s;
                        while sst < TABCAP
                            invariant_except_break
                                sst <= TABCAP,
                                alive(st, s),
                                alive(st, sp),
                                base(tab@, live@, st, ntab as int, perms),
                                succ_walk(st, s, sp, sgl, (TABCAP - sst) as nat) == succ_walk(
                                    st,
                                    s_in,
                                    cur,
                                    false,
                                    TABCAP as nat,
                                ),
                            ensures
                                alive(st, s),
                                alive(st, sp),
                                (s, sp, sgl) == succ_walk(st, s_in, cur, false, TABCAP as nat),
                            decreases TABCAP - sst,
                        {
                            assert(rec_ok(tab@, st, perms, s as int));
                            let sb = arr_get_unchecked(&tab, s as usize);
                            let srec: Rec = {
                                let tracked t = perms.tracked_borrow(s as int);
                                rec_read(sb, Tracked(t))
                            };
                            if srec.l == NIL
                                || arr_get_unchecked(&live, srec.l as usize) != 1u8 {
                                break;
                            }
                            sst = sst + 1;
                            sp = s;
                            s = srec.l;
                            sgl = true;
                        }
                        assert(rec_ok(tab@, st, perms, s as int));
                        let sb = arr_get_unchecked(&tab, s as usize);
                        let srec: Rec = {
                            let tracked t = perms.tracked_borrow(s as int);
                            rec_read(sb, Tracked(t))
                        };
                        let ghost jj = cur as int;
                        let ghost sj = s as int;
                        let ghost st0v = st;
                        let ghost perms0 = perms;
                        let tracked t = perms.tracked_borrow_mut(jj);
                        let cb2 = arr_get_unchecked(&tab, cur as usize);
                        let co = rec_read(cb2, Tracked(&*t));
                        rec_write(
                            cb2,
                            Tracked(t),
                            Rec { key: srec.key, val: srec.val, l: co.l, r: co.r },
                        );
                        proof {
                            st = St {
                                ky: st.ky.update(jj, st.ky[sj]),
                                vl: st.vl.update(jj, st.vl[sj]),
                                ..st
                            };
                            assert forall|j: int| 0 <= j < ntab as int && st.lv[j] implies rec_ok(
                                tab@,
                                st,
                                perms,
                                j,
                            ) by {
                                if j != jj {
                                    assert(rec_ok(tab@, st0v, perms0, j));
                                }
                            }
                            assert forall|j: int| 0 <= j < ntab as int && st.lv[j] implies dal_ok(
                                tab@,
                                dal,
                                j,
                            ) by {
                                assert(st0v.lv[j]);
                            }
                        }
                        cur = s;
                        par = sp;
                        gl = sgl;
                        continue;
                    }
                    // ZERO OR ONE CHILD: unlink, then FREE. This is the arm that
                    // consumes the permission, and it is the ONLY one.
                    let ch: u8 = if crec.l != NIL { crec.l } else { crec.r };
                    if par == NIL {
                        let ghost st1v = st;
                        let ghost perms1 = perms;
                        root = ch;
                        proof {
                            st = St { root: ch, ..st };
                            assert forall|j: int|
                                0 <= j < ntab as int && st.lv[j] implies rec_ok(
                                tab@,
                                st,
                                perms,
                                j,
                            ) by {
                                assert(rec_ok(tab@, st1v, perms1, j));
                            }
                            assert forall|j: int|
                                0 <= j < ntab as int && st.lv[j] implies dal_ok(
                                tab@,
                                dal,
                                j,
                            ) by {
                                assert(st1v.lv[j]);
                            }
                        }
                    } else {
                        let ghost pj = par as int;
                        let ghost st1v = st;
                        let ghost perms1 = perms;
                        assert(rec_ok(tab@, st, perms, pj));
                        let tracked t = perms.tracked_borrow_mut(pj);
                        let pb = arr_get_unchecked(&tab, par as usize);
                        let po = rec_read(pb, Tracked(&*t));
                        if gl {
                            rec_write(
                                pb,
                                Tracked(t),
                                Rec { key: po.key, val: po.val, l: ch, r: po.r },
                            );
                            proof {
                                st = St { lt: st.lt.update(pj, ch), ..st };
                            }
                        } else {
                            rec_write(
                                pb,
                                Tracked(t),
                                Rec { key: po.key, val: po.val, l: po.l, r: ch },
                            );
                            proof {
                                st = St { rt: st.rt.update(pj, ch), ..st };
                            }
                        }
                        proof {
                            assert forall|j: int|
                                0 <= j < ntab as int && st.lv[j] implies rec_ok(
                                tab@,
                                st,
                                perms,
                                j,
                            ) by {
                                if j != pj {
                                    assert(rec_ok(tab@, st1v, perms1, j));
                                }
                            }
                            assert forall|j: int|
                                0 <= j < ntab as int && st.lv[j] implies dal_ok(
                                tab@,
                                dal,
                                j,
                            ) by {
                                assert(st1v.lv[j]);
                            }
                        }
                    }
                    let ghost jj = cur as int;
                    let ghost st2v = st;
                    let ghost perms2 = perms;
                    let ghost dal2 = dal;
                    assert(rec_ok(tab@, st, perms, jj));
                    assert(dal_ok(tab@, dal, jj));
                    let tracked pt = perms.tracked_remove(jj);
                    let tracked dd = dal.tracked_remove(jj);
                    rec_close(arr_get_unchecked(&tab, cur as usize), Tracked(pt), Tracked(dd));
                    // THE LINE THE C RUNG DOES NOT FORGET, and the proof forces
                    // it: without it the invariant cannot be re-established,
                    // because `rec_free` has consumed slot `cur`'s permission
                    // while the liveness array would still claim it exists.
                    arr_set_unchecked(&mut live, cur as usize, 0u8);
                    proof {
                        st = St { lv: st.lv.update(jj, false), ..st };
                        assert forall|j: int| 0 <= j < ntab as int && st.lv[j] implies rec_ok(
                            tab@,
                            st,
                            perms,
                            j,
                        ) by {
                            assert(j != jj);
                            assert(rec_ok(tab@, st2v, perms2, j));
                        }
                        assert forall|j: int| 0 <= j < ntab as int && st.lv[j] implies dal_ok(
                            tab@,
                            dal,
                            j,
                        ) by {
                            assert(j != jj);
                            assert(dal_ok(tab@, dal2, j));
                        }
                    }
                    break;
                }
                acc = acc.wrapping_mul(31).wrapping_add(2);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else {
            // THE SAFETY LINE. c/kernel.c omits both conjuncts.
            //
            // ⚠ The nesting is not a style choice: `perms.tracked_borrow` has
            // `dom().contains(g_slot)` as a precondition, and the only thing
            // that discharges it is `live[g_slot] == 1` through the invariant.
            // So the identity test CANNOT be written before the liveness test at
            // this rung -- C's `&&` ordering is a type-system consequence here.
            let v: u64 = if g_has && arr_get_unchecked(&live, g_slot as usize) == 1u8 {
                assert(alive(st, g_slot));
                assert(rec_ok(tab@, st, perms, g_slot as int));
                let tracked t = perms.tracked_borrow(g_slot as int);
                let rr = rec_read(g_saved, Tracked(t));
                if rr.key == g_key {
                    rr.val as u64
                } else {
                    SENT
                }
            } else {
                SENT
            };
            acc = acc.wrapping_mul(31).wrapping_add(v);
        }
        proof {
            assert(st == step(st_in, c, a).0);
            assert(acc == acc_in.wrapping_mul(31).wrapping_add(step(st_in, c, a).1));
            assert(run(buf@, off as int, len as int, o_in, nops as int, p_in, st_in, acc_in)
                == run(
                buf@,
                off as int,
                len as int,
                o_in + 1,
                nops as int,
                p_in + 2,
                st,
                acc,
            ));
        }
        o = o + 1;
    }
    // ------- the epilogue: free every record still alive -------------------
    // R2 and R3 do not have this loop: dropping the table IS this loop, written
    // by the language. The invariant is `wf` weakened to the SUFFIX `[j, ntab)`,
    // which is what lets the epilogue skip a dead liveness store -- p27's
    // measured shape.
    let mut j: usize = 0;
    while j < ntab
        invariant
            j <= ntab,
            0 <= ntab <= TABCAP,
            tab@.len() == TABCAP,
            live@.len() == TABCAP,
            st.ky.len() == ntab as int,
            st.vl.len() == ntab as int,
            st.lt.len() == ntab as int,
            st.rt.len() == ntab as int,
            st.lv.len() == ntab as int,
            forall|k: int| j as int <= k < ntab as int ==> ((#[trigger] st.lv[k]) <==> live@[k]
                == 1u8),
            forall|k: int| j as int <= k < ntab as int && st.lv[k] ==> #[trigger] rec_ok(
                tab@,
                st,
                perms,
                k,
            ),
            forall|k: int| j as int <= k < ntab as int && st.lv[k] ==> #[trigger] dal_ok(
                tab@,
                dal,
                k,
            ),
        decreases ntab - j,
    {
        if arr_get_unchecked(&live, j) == 1u8 {
            assert(st.lv[j as int]);
            assert(rec_ok(tab@, st, perms, j as int));
            assert(dal_ok(tab@, dal, j as int));
            let ghost perms0 = perms;
            let ghost dal0 = dal;
            let tracked pt = perms.tracked_remove(j as int);
            let tracked dd = dal.tracked_remove(j as int);
            rec_close(arr_get_unchecked(&tab, j), Tracked(pt), Tracked(dd));
            proof {
                assert forall|k: int| j as int + 1 <= k < ntab as int && st.lv[k] implies rec_ok(
                    tab@,
                    st,
                    perms,
                    k,
                ) by {
                    assert(k != j as int);
                    assert(rec_ok(tab@, st, perms0, k));
                }
                assert forall|k: int| j as int + 1 <= k < ntab as int && st.lv[k] implies dal_ok(
                    tab@,
                    dal,
                    k,
                ) by {
                    assert(k != j as int);
                    assert(dal_ok(tab@, dal0, k));
                }
            }
        }
        j = j + 1;
    }
    acc.wrapping_mul(31).wrapping_add(ntab as u64)
}

// ---------------------------------------------------------------- driver ----
fn main() {
    let (n_iters, stride_w, bytes) = load_input();
    // SLB-DRIVER-BEGIN
    let n_blob: usize = bytes.len();
    let buf: &[u8] = bytes.as_slice();
    let mut acc: u64 = 0;
    if stride_w >= 4 && stride_w <= n_blob as u64 {
        let stride: usize = stride_w as usize;
        let nwin: u64 = (n_blob / stride) as u64;
        let mut it: u64 = 0;
        // Ghost only: at least one whole window is present.
        proof {
            vstd::arithmetic::div_mod::lemma_div_non_zero(n_blob as int, stride as int);
        }
        while it < n_iters
            invariant
                4 <= stride <= n_blob,
                buf@.len() == n_blob,
                nwin == n_blob / stride,
                nwin >= 1,
            decreases n_iters - it,
        {
            // Ghost only: `k` must land inside the blob. Two nonlinear steps, so
            // Z3 needs both spelled out. Erases at compile time.
            proof {
                let pp: int = (acc as int) * (nwin as int);
                assert((acc as u128) * (nwin as u128) <= (u64::MAX as u128) * (u64::MAX
                    as u128)) by (nonlinear_arith)
                    requires
                        acc <= u64::MAX,
                        nwin <= u64::MAX,
                ;
                assert(vstd::arithmetic::power2::pow2(64) == 0x1_0000_0000_0000_0000nat) by {
                    vstd::arithmetic::power2::lemma2_to64_rest();
                }
                assert(pp < (nwin as int) * 0x1_0000_0000_0000_0000int) by (nonlinear_arith)
                    requires
                        pp == (acc as int) * (nwin as int),
                        acc <= u64::MAX,
                        nwin >= 1,
                ;
            }
            let k: usize = ((acc as u128 * nwin as u128) >> 64) as usize;
            proof {
                assert(k < nwin);
                vstd::arithmetic::div_mod::lemma_fundamental_div_mod(
                    n_blob as int,
                    stride as int,
                );
                assert((nwin as int) * (stride as int) <= n_blob as int);
                assert((k as int) * (stride as int) <= ((nwin as int) - 1) * (stride as int));
                assert(((nwin as int) - 1) * (stride as int) == (nwin as int) * (stride as int)
                    - (stride as int)) by (nonlinear_arith);
                assert((k as int) * (stride as int) + (stride as int) <= n_blob as int);
            }
            let r: u64 = kernel(buf, k * stride, stride);
            // Ghost only: this is what *consumes* the kernel's `ensures`.
            assert(r == bst_fold(buf@, (k * stride) as int, stride as int));
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    emit(acc);
}

} // verus!
