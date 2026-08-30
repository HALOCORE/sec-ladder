//! p28 rung R5 -- unsafe Rust + a Verus proof.
//!
//! This is unsafe.rs's exec code with the SAFETY comments turned into
//! obligations a verifier discharges. **What is new here is not the machinery --
//! it is `p29`'s -- it is WHAT THE PROOF TURNS OUT TO FORCE, and the answer is
//! not the one the row's C side would suggest.** ../NOTES.md 6 states it as a
//! result; the short version is here because it is what a reader of this file
//! needs first:
//!
//!   * `rec_close` CONSUMES the object's `PointsTo` and its `Dealloc`, so after
//!     TRIM has freed the victim nothing in this rung can read it. That is the
//!     temporal guarantee, and it is real.
//!   * **But the thing `c/kernel.c` forgets is not a READ, it is a LINK**, and a
//!     link in this rung is a `u8`. Deleting the safety line here leaves a `u8`
//!     naming a slot whose permission has gone -- and the walk's
//!     `live[cur] == 1u8` conjunct and `alive_link` simply refuse to follow it.
//!     **The memory-safety obligation does not force the safety line.**
//!   * **The FUNCTIONAL postcondition does.** `run` is an abstract machine that
//!     carries the bucket array and both link sets, and it says TRIM splices the
//!     victim out of its chain. A kernel that skips the splice computes a
//!     different fold and `r == cache_fold(..)` fails.
//!     `controls/proof_mutants.py` demonstrates all of it with SEVEN arms
//!     rather than asserting it, and two of them changed what this header says.
//!
//! ⚠ **That is the same shape `p32` reported and the OPPOSITE of what `p27` and
//! `p29` report, and p28 sharpens it**: `p32` had no linear resource at all
//! (nothing is ever allocated), so *of course* nothing linear forced its
//! conjunct. **p28 HAS the linear resources -- a `PointsTo` and a `Dealloc` per
//! object, consumed by a real `free` -- and they still do not force this
//! conjunct**, because the omission is in the DESTROY path and the linear
//! argument only ever bites at a READ. ../NOTES.md 6.
//!
//! **WHAT THE PROOF COSTS, AND IT IS `p29`'s COST ONE LIST OVER.** Every walk
//! carries `live[cur] == 1u8` and a `steps < SLOTS` bound, and every splice site
//! asks `alive_link(&live, x)` where the C rungs ask `x != NULL`. **Counted in
//! this file: one liveness conjunct in the walk plus TEN `alive_link` sites,
//! and not one of them can fire** -- a correct chain holds only live objects and
//! no chain is longer than the fuel. They are here because the
//! alternative is to prove that the two link sets are WELL-FORMED DOUBLY LINKED
//! LISTS -- `hn[hp[j]] == j`, `hp[hn[j]] == j` and the same pair for the eviction
//! list -- which is what *"every link names a live slot"* needs and which no
//! per-slot invariant gives you. With them, the licence for every object read is
//! `p27`'s own `wf`: `live[i] == 1 <==> perms.dom().contains(i)`, a per-slot
//! fact. ⚠⚠ **`p29` could put its liveness conjuncts in its C rungs too. p28
//! CANNOT, and the reason is the row's own headline: p28's C links are POINTERS
//! and there is no slot number and no `live[]` bit anywhere in either C rung.
//! The property that makes the row distinct at C level is the property that
//! makes this conjunct unspellable there.** ../NOTES.md 5 counts the asymmetry;
//! no cost claim rests on it because this pattern publishes none (../NOTES.md 8).
//!
//! **TCB: seven items** -- `buf_get_unchecked`, `arr_get_unchecked`,
//! `arr_set_unchecked`, `rec_alloc`, `rec_free`, `load_input`, `emit`. The same
//! seven `p27` and `p29` ship. Two of them are the allocation API, and they are
//! here for a CODEGEN reason rather than a trust reason -- they are
//! `vstd::raw_ptr::allocate` / `deallocate` copied into this crate so the call is
//! direct and `#[inline(always)]`, because vstd carries no `#[inline]` and R4
//! cannot emit a GOT-indirect cross-crate call. **Their verified twins are
//! vstd's own `allocate` and `deallocate`.**
//!
//! **`global layout Obj is size == 6, align == 1;`** is the one declaration this
//! rung adds that `p27` does not need, and it is `p29`'s: the object is a
//! six-byte `#[repr(C)]` struct because BOTH LINK SETS live inside it, and Verus
//! gets no layout information from `#[repr(C)]`. The directive both exports the
//! axioms and **emits a static check at codegen**, so it is checked by the
//! compiler on this platform rather than assumed
//! (`_VERUS_DOC_/guide/src/reference-global.md`). ⚠ It is nevertheless an axiom
//! for the verifier and ../NOTES.md 6 counts it as such.
//!
//! SAFETY (1): `off + len <= buf.len()` is the caller's structural
//!   precondition. Unchecked in unsafe.rs; discharged at the call site here.
//! SAFETY (2): `len >= 4` guards the window header.
//! SAFETY (3): the op is read only under `len - p >= 2` with `p <= len`.
//! SAFETY (4): every object read or write of slot `i` happens under
//!   `live[i] == 1`, and `live[i] == 1` implies the permission for slot `i` is
//!   still in the map. That is the conjunct `p27` and `p29` also have.
//! SAFETY (5): every slot number this kernel forms is `NIL` or below `nmade`,
//!   because the only slot number ever stored into a link, a bucket, `head` or
//!   `tail` is `nmade` at the moment it is allocated. `base` carries it as
//!   `links_ok` (one quantifier over the four link fields), the bucket
//!   quantifier, and one conjunct each for `head` and `tail` -- and it is what
//!   licenses every `arr_get_unchecked`.
//! SAFETY (6): `rec_close` is called at most once per object -- DEL and TRIM
//!   each clear `live[cur]` before anything can reach the slot again, and the
//!   epilogue frees only slots still marked alive -- so there is no double free
//!   and no use after free. ⚠⚠ **AND THAT IS ALL THE LINEAR RESOURCES BUY: THEY
//!   DO NOT FORCE THE EPILOGUE, AND THE SENTENCE THAT USED TO STAND HERE --
//!   *"this is the half the linear resources DO force"* -- IS RETRACTED.**
//!   `controls/proof_mutants.py`'s `A6-epilogue-dead` makes the epilogue's
//!   `live[j] == 1` test unreachable, so every surviving object leaks, and the
//!   file still verifies `23/0`. `Tracked<Dealloc>` is AFFINE, not linear:
//!   dropping a token is legal, so a proof built on it shows deallocation is
//!   LEGAL and never that it HAPPENS. `.memory/04-verus.md` carries that result
//!   for `p42` (`TASK_104`, with a committed must-fail control); p28 is the
//!   fourth pattern to show it and the first whose C rungs really do free
//!   everything. What stands behind the epilogue here is
//!   `controls/rust_arms.py`'s Miri arm, not this proof.

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
// `slice@.len() <= usize::MAX`. `group_array_axioms` gives `tab@.len() == SLOTS`
// and the fill axiom for `[null_mut(); SLOTS]`. `group_layout_axioms` +
// `align_of_u8` are what `into_typed` needs at align 1.
// `group_raw_ptr_axioms` turns `ptr_mut_from_data(p@) == p` into a usable fact.
// `lemma_u128_shr_is_div` and `lemma_mul_inequality` are the DRIVER's, and
// ⚠ **on this pattern they belong at FILE scope, which is the OPPOSITE of what
// `p09` measured** (its NOTES.md 5c scopes them into the driver's loop body to
// keep the kernel's query inside the rlimit). Scoping them here makes the
// KERNEL's query WORSE: the minimum workable `rlimit` goes from 120 to above
// 120. Measured both ways, ../NOTES.md 6a.
broadcast use {
    vstd::slice::group_slice_axioms,
    vstd::array::group_array_axioms,
    vstd::layout::group_layout_axioms,
    vstd::layout::align_of_u8,
    vstd::raw_ptr::group_raw_ptr_axioms,
    vstd::bits::lemma_u128_shr_is_div,
    vstd::arithmetic::mul::lemma_mul_inequality,
};

/// Hash buckets. A compile-time constant in every rung.
pub const NB: usize = 8;

/// The slot table's extent, i.e. the objects one window may make. Both C rungs
/// carry it too (c/kernel.h says why) so all seven agree. **It is also the chain
/// walk's fuel and R5's `decreases` measure**: a chain holds only live objects
/// and at most `SLOTS` are ever made, so it cannot truncate one.
pub const SLOTS: usize = 48;

/// One object, one allocation, `OBJSZ` bytes: `key, val, lp, ln, hn, hp`. BOTH
/// LINK SETS are inside it, which is what "intrusive" means and what makes the
/// object aliased by two lists at once.
pub const OBJSZ: usize = 6;

/// The null link. Outside `0 .. SLOTS`, so `alive(st, NIL)` is false for free.
pub const NIL: u8 = 255;

/// What a rejected operation folds. A compile-time constant in every rung.
pub const SENT: u64 = 251;

#[repr(C)]
#[derive(Clone, Copy)]
pub struct Obj {
    pub key: u8,
    pub val: u8,
    pub lp: u8,
    pub ln: u8,
    pub hn: u8,
    pub hp: u8,
}

global layout Obj is size == 6, align == 1;

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

/// An object's payload is a function of the key that created it, in every rung.
pub open spec fn val_of(a: u8) -> u8 {
    a.wrapping_mul(7).wrapping_add(1)
}

/// THE ABSTRACT MACHINE'S STATE.
///
/// ⚠ **`ob` is ONE sequence of whole objects, not six parallel sequences of
/// fields, and that is a PROOF-ENGINEERING decision with a measured reason.**
/// `p29` carries five parallel sequences and re-establishes its record
/// invariant after every mutation; p28 mutates far more often -- a DEL splices
/// FOUR links and a TRIM THREE -- and with parallel sequences every one of
/// those, plus every `bk`/`head`/`tail` write, produces a fresh `St` term that
/// the record invariant has to be re-proved against. With one `ob` sequence,
/// `rec_ok` and `links_ok` are stated over `st.ob` alone, so a write to `bk`,
/// `head` or `tail` leaves their terms unchanged and the invariant survives for
/// free. ../NOTES.md 6a records what that cost before the change: `Resource
/// limit (rlimit) exceeded` on the kernel's own loop.
///
/// **`bk`, `hn` and `hp` are the hash chain; `head`, `tail`, `lp` and `ln` are
/// the eviction list; `lv` is ownership. The whole of p28 is that MEMBERSHIP OF
/// EITHER LIST IS NOT `lv`.**
pub ghost struct St {
    pub ob: Seq<Obj>,
    pub lv: Seq<bool>,
    pub bk: Seq<u8>,
    pub head: u8,
    pub tail: u8,
}

/// Is slot `x` a live slot? `NIL` is 255 and `lv.len() <= SLOTS == 48`, so this
/// is false for `NIL` without a special case.
pub open spec fn alive(st: St, x: u8) -> bool {
    (x as int) < st.lv.len() && st.lv[x as int]
}

/// THE CHAIN WALK, shared by PUT, GET and DEL. Returns `(cur, found)` -- the two
/// variables the exec loop carries out. `fuel` is the exec loop's
/// `SLOTS - steps`.
pub open spec fn descend(st: St, cur: u8, k: u8, fuel: nat) -> (u8, bool)
    decreases fuel,
{
    if fuel == 0 || !alive(st, cur) {
        (cur, false)
    } else if st.ob[cur as int].key == k {
        (cur, true)
    } else {
        descend(st, st.ob[cur as int].hn, k, (fuel - 1) as nat)
    }
}

/// The bucket an operand lands in.
pub open spec fn bkt(a: u8) -> int {
    (a % (NB as u8)) as int
}

/// ⚠⚠ **WHY THE MACHINE ASKS `alive` WHERE C ASKS `!= NULL`, AND IT IS THE ONE
/// PLACE THIS SPECIFICATION IS NOT LITERALLY THE C PROGRAM.** Every splice arm
/// below tests `alive(st, x)` rather than `x != NIL`. **In the checked kernel
/// the two are the same test** -- every link names a live object, which is the
/// invariant `c/kernel_hardened.c`'s header states -- and neither can fire. They
/// are spelled `alive` because this file's exec code spells them
/// `alive_link(&live, x)`, and it spells them that way because the alternative
/// is to carry the doubly-linked-list invariant (`hn[hp[j]] == j` and its three
/// siblings) that would let `x != NIL` DISCHARGE `alive(st, x)`. See `base`'s
/// docstring, this file's header and ../NOTES.md 5. **The difference is stated
/// rather than hidden, and it is the same trade `p29` made one list over.**
///
/// PUT'S ALLOCATION: a fresh object pushed on the FRONT of both lists.
#[verifier::opaque]
pub open spec fn put_new(st: St, b: int, a: u8) -> St {
    let s = st.ob.len() as u8;
    let fresh = Obj { key: a, val: val_of(a), lp: NIL, ln: st.head, hn: st.bk[b], hp: NIL };
    let st1 = St { ob: st.ob.push(fresh), lv: st.lv.push(true), ..st };
    let st2 = if alive(st, st.head) {
        St {
            ob: st1.ob.update(st.head as int, Obj { lp: s, ..st1.ob[st.head as int] }),
            ..st1
        }
    } else {
        St { tail: s, ..st1 }
    };
    let st3 = St { head: s, ..st2 };
    let st4 = if alive(st, st.bk[b]) {
        St {
            ob: st3.ob.update(st.bk[b] as int, Obj { hp: s, ..st3.ob[st.bk[b] as int] }),
            ..st3
        }
    } else {
        st3
    };
    St { bk: st4.bk.update(b, s), ..st4 }
}

/// DEL'S SPLICE: out of BOTH lists, then the free. DEL arrives ALONG the hash
/// chain, so it holds a chain cursor -- which is why DEL is not the path that
/// forgets.
#[verifier::opaque]
pub open spec fn del_at(st: St, b: int, cur: u8) -> St {
    let i = cur as int;
    let v = st.ob[i];
    let s1 = if alive(st, v.hp) {
        St { ob: st.ob.update(v.hp as int, Obj { hn: v.hn, ..st.ob[v.hp as int] }), ..st }
    } else {
        St { bk: st.bk.update(b, v.hn), ..st }
    };
    let s2 = if alive(st, v.hn) {
        St { ob: s1.ob.update(v.hn as int, Obj { hp: v.hp, ..s1.ob[v.hn as int] }), ..s1 }
    } else {
        s1
    };
    let s3 = if alive(st, v.lp) {
        St { ob: s2.ob.update(v.lp as int, Obj { ln: v.ln, ..s2.ob[v.lp as int] }), ..s2 }
    } else {
        St { head: v.ln, ..s2 }
    };
    let s4 = if alive(st, v.ln) {
        St { ob: s3.ob.update(v.ln as int, Obj { lp: v.lp, ..s3.ob[v.ln as int] }), ..s3 }
    } else {
        St { tail: v.lp, ..s3 }
    };
    St { lv: s4.lv.update(i, false), ..s4 }
}

/// TRIM'S RECLAIM. **The two blocks below are the row.** The first leaves the
/// EVICTION list, which `c/kernel.c` also does; the second leaves the HASH
/// CHAIN, and `c/kernel.c` omits exactly that and nothing else. A kernel that
/// skips it does not compute this function.
#[verifier::opaque]
pub open spec fn trim(st: St) -> St {
    let x = st.tail;
    let i = x as int;
    let v = st.ob[i];
    let vb = bkt(v.key);
    let s1 = if alive(st, v.lp) {
        St { ob: st.ob.update(v.lp as int, Obj { ln: NIL, ..st.ob[v.lp as int] }), ..st }
    } else {
        St { head: NIL, ..st }
    };
    let s2 = St { tail: v.lp, ..s1 };
    // THE SAFETY LINE, in the abstract machine.
    let s3 = if alive(st, v.hp) {
        St { ob: s2.ob.update(v.hp as int, Obj { hn: v.hn, ..s2.ob[v.hp as int] }), ..s2 }
    } else {
        St { bk: s2.bk.update(vb, v.hn), ..s2 }
    };
    let s4 = if alive(st, v.hn) {
        St { ob: s3.ob.update(v.hn as int, Obj { hp: v.hp, ..s3.ob[v.hn as int] }), ..s3 }
    } else {
        s3
    };
    St { lv: s4.lv.update(i, false), ..s4 }
}

/// ONE OPERATION: the new state and what it folds.
#[verifier::opaque]
pub open spec fn step(st: St, c: u8, a: u8) -> (St, u64) {
    let b = bkt(a);
    if c % 4 == 0 {
        let d = descend(st, st.bk[b], a, SLOTS as nat);
        if d.1 {
            (
                St {
                    ob: st.ob.update(d.0 as int, Obj { val: val_of(a), ..st.ob[d.0 as int] }),
                    ..st
                },
                a as u64,
            )
        } else if st.ob.len() < SLOTS as int {
            (put_new(st, b, a), a as u64)
        } else {
            (st, SENT)
        }
    } else if c % 4 == 1 {
        let d = descend(st, st.bk[b], a, SLOTS as nat);
        if d.1 {
            (st, st.ob[d.0 as int].val as u64)
        } else {
            (st, SENT)
        }
    } else if c % 4 == 2 {
        let d = descend(st, st.bk[b], a, SLOTS as nat);
        if d.1 {
            (del_at(st, b, d.0), 2u64)
        } else {
            (st, SENT)
        }
    } else {
        if alive(st, st.tail) {
            (trim(st), 3u64)
        } else {
            (st, SENT)
        }
    }
}

/// The empty machine.
pub open spec fn st0() -> St {
    St {
        ob: Seq::empty(),
        lv: Seq::empty(),
        bk: Seq::new(NB as nat, |i: int| NIL),
        head: NIL,
        tail: NIL,
    }
}

/// THE ABSTRACT MACHINE. It describes the PROGRAM -- stop when the window runs
/// out, reject a PUT past the budget, fold SENT for an absent key, fold SENT for
/// a TRIM of an empty cache -- and it says nothing about `nops` being honest or
/// about the op stream being well formed. Every adversarial input is inside this
/// domain (../spec.md).
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
        acc.wrapping_mul(31).wrapping_add(st.ob.len() as u64)
    } else {
        let s = step(st, buf[off + p], buf[off + p + 1]);
        run(buf, off, len, o + 1, nops, p + 2, s.0, acc.wrapping_mul(31).wrapping_add(s.1))
    }
}

/// What the kernel must return.
pub open spec fn cache_fold(buf: Seq<u8>, off: int, len: int) -> u64 {
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
/// six bytes behind the pointer are the six the abstract machine says.
///
/// ⚠ It takes `ob` and NOT the whole `St`, which is what makes it survive a
/// `bk`/`head`/`tail` write with no proof at all. See `St`'s docstring.
pub open spec fn rec_ok(
    tab: Seq<*mut Obj>,
    ob: Seq<Obj>,
    perms: Map<int, PointsTo<Obj>>,
    j: int,
) -> bool {
    &&& perms.dom().contains(j)
    &&& perms[j].ptr() == tab[j]
    &&& perms[j].is_init()
    &&& perms[j].value() == ob[j]
}

/// The DEALLOC half, kept separate so that the walk -- which reads objects and
/// frees nothing -- needs only the half above. ⚠ It mentions no ghost state at
/// all, so **every splice leaves it untouched** and only the two frees, the
/// allocation and the epilogue have to re-establish it.
pub open spec fn dal_ok(tab: Seq<*mut Obj>, dal: Map<int, Dealloc>, j: int) -> bool {
    &&& dal.dom().contains(j)
    &&& dal[j].addr() == tab[j].addr()
    &&& dal[j].size() == OBJSZ
    &&& dal[j].align() == 1
    &&& dal[j].provenance() == tab[j]@.provenance
}

/// The four links of ONE slot are each `NIL` or a real slot. Bundled into one
/// predicate so that `base` carries ONE quantifier here instead of four -- the
/// loop body re-establishes the invariant a dozen times and the solver's rlimit
/// is a real constraint (`p09`'s NOTES.md 5c is the precedent).
pub open spec fn links_ok(ob: Seq<Obj>, j: int, nmade: int) -> bool {
    &&& ob[j].lp == NIL || (ob[j].lp as int) < nmade
    &&& ob[j].ln == NIL || (ob[j].ln as int) < nmade
    &&& ob[j].hn == NIL || (ob[j].hn as int) < nmade
    &&& ob[j].hp == NIL || (ob[j].hp as int) < nmade
}

/// THE READ-SIDE INVARIANT.
///
/// The length block is bookkeeping. The RANGE blocks -- every link, every
/// bucket, `head` and `tail` are `NIL` or a real slot -- are what license
/// `live[x]` to be INDEXED at all. **Note what they are NOT: they say nothing
/// about a link naming a LIVE slot**, which is the doubly-linked-list invariant
/// (`hn[hp[j]] == j` and its three siblings) and which no per-slot fact gives
/// you. That is what the walk's `live[cur] == 1` conjunct and `alive_link` buy
/// instead, and it is `p29`'s trade one list over. The last block is `p27`'s
/// temporal invariant.
///
/// ⚠ **The last two quantifiers are guarded by `live[j] == 1u8` -- the EXEC
/// array -- and not by the ghost `st.lv[j]`.** Same reason as `St`'s one-`ob`
/// shape: `live@` does not move during a splice, so the guard term is stable and
/// the invariant does not have to be re-derived through the ghost state at every
/// site. ../NOTES.md 6a.
pub open spec fn base(
    tab: Seq<*mut Obj>,
    live: Seq<u8>,
    bucket: Seq<u8>,
    st: St,
    nmade: int,
    perms: Map<int, PointsTo<Obj>>,
) -> bool {
    &&& 0 <= nmade <= SLOTS
    &&& tab.len() == SLOTS
    &&& live.len() == SLOTS
    &&& bucket.len() == NB
    &&& st.ob.len() == nmade
    &&& st.lv.len() == nmade
    &&& st.bk.len() == NB
    &&& forall|j: int| 0 <= j < nmade ==> ((#[trigger] st.lv[j]) <==> live[j] == 1u8)
    &&& forall|j: int|
        0 <= j < NB as int ==> (#[trigger] st.bk[j]) == bucket[j] && (st.bk[j] == NIL || (
        st.bk[j] as int) < nmade)
    &&& forall|j: int| 0 <= j < nmade ==> #[trigger] links_ok(st.ob, j, nmade)
    &&& st.head == NIL || (st.head as int) < nmade
    &&& st.tail == NIL || (st.tail as int) < nmade
    &&& forall|j: int|
        0 <= j < nmade && live[j] == 1u8 ==> #[trigger] rec_ok(tab, st.ob, perms, j)
}

/// THE WHOLE INVARIANT: the read side plus the dealloc tokens. p28 adds no third
/// block -- unlike `p29`, it caches no pointer across operations, which is the
/// difference the row is about: **the stale reference is in a link field, and a
/// link field is inside `base`.**
pub open spec fn wf(
    tab: Seq<*mut Obj>,
    live: Seq<u8>,
    bucket: Seq<u8>,
    st: St,
    nmade: int,
    perms: Map<int, PointsTo<Obj>>,
    dal: Map<int, Dealloc>,
) -> bool {
    &&& base(tab, live, bucket, st, nmade, perms)
    &&& forall|j: int| 0 <= j < nmade && live[j] == 1u8 ==> #[trigger] dal_ok(tab, dal, j)
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
// the element type so that the pointer table, the liveness array and the bucket
// array share one accessor. Same documented `get_unchecked` contract as item 1.
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
// **It CONSUMES the `PointsToRaw` and the `Dealloc`**, and that is the temporal
// argument: after this call the caller has no permission to present, so a later
// READ of the same object is unprovable. ⚠⚠ **And that is ALL it is.** p28's
// omitted line is not a read, it is a LINK LEFT BEHIND, and no linear resource
// is consumed by leaving a `u8` in a chain. See this file's header and
// ../NOTES.md 6.
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

// --------------------------------------------------------- the object ops ---
// **NOT trusted items.** `rec_open`, `rec_close`, `rec_read` and `rec_write` are
// ordinary verified functions. Everything unchecked they do happens either
// inside vstd -- `ptr_ref` and `ptr_mut_write` are `external_body` there,
// `into_typed`, `into_raw` and `leak_contents` are vstd `axiom fn`s -- or inside
// items 4 and 5, whose twins are vstd's own allocation API.
#[inline(always)]
fn rec_open(v: Obj) -> (r: (*mut Obj, Tracked<PointsTo<Obj>>, Tracked<Dealloc>))
    ensures
        r.1@.ptr() == r.0,
        r.1@.is_init(),
        r.1@.value() == v,
        r.2@.addr() == r.0.addr(),
        r.2@.size() == OBJSZ,
        r.2@.align() == 1,
        r.2@.provenance() == r.0@.provenance,
{
    assert(valid_layout(OBJSZ, 1));
    let (base, Tracked(raw), Tracked(dealloc)) = rec_alloc(OBJSZ, 1);
    let tracked mut pt = raw.into_typed::<Obj>(base.addr());
    let q: *mut Obj = base as *mut Obj;
    assert(pt.ptr() == q);
    ptr_mut_write(q, Tracked(&mut pt), v);
    (q, Tracked(pt), Tracked(dealloc))
}

// THE REAL `free`.
#[inline(always)]
fn rec_close(p: *mut Obj, Tracked(pt): Tracked<PointsTo<Obj>>, Tracked(dl): Tracked<Dealloc>)
    requires
        pt.ptr() == p,
        dl.addr() == p.addr(),
        dl.size() == OBJSZ,
        dl.align() == 1,
        dl.provenance() == p@.provenance,
{
    let tracked mut q = pt;
    proof {
        q.leak_contents();
    }
    let tracked raw = q.into_raw();
    let base: *mut u8 = p as *mut u8;
    rec_free(base, OBJSZ, 1, Tracked(raw), Tracked(dl));
}

#[inline(always)]
fn rec_read(p: *mut Obj, Tracked(pt): Tracked<&PointsTo<Obj>>) -> (r: Obj)
    requires
        pt.ptr() == p,
        pt.is_init(),
    ensures
        r == pt.value(),
{
    *ptr_ref(p, Tracked(pt))
}

#[inline(always)]
fn rec_write(p: *mut Obj, Tracked(pt): Tracked<&mut PointsTo<Obj>>, v: Obj)
    requires
        old(pt).ptr() == p,
    ensures
        final(pt).ptr() == p,
        final(pt).is_init(),
        final(pt).value() == v,
{
    ptr_mut_write(p, Tracked(pt), v);
}

/// **THE LIVENESS HALF OF A LINK TEST, and the one exec conjunct in this rung
/// that the C rungs cannot spell.** C writes `x != NULL`; this rung writes
/// `alive_link(&live, x)`, which is `x != NIL && live[x] == 1u8`. The second
/// half CANNOT FIRE in a correct rung -- every link names a live object -- and
/// it is here because it is what licenses `perms.tracked_borrow_mut(x)` at the
/// nine splice sites. The alternative is the doubly-linked-list invariant; see
/// `base`'s docstring and this file's header. ../NOTES.md 5.
#[inline(always)]
fn alive_link(live: &[u8; SLOTS], x: u8) -> (r: bool)
    requires
        live@.len() == SLOTS,
        x == NIL || (x as int) < SLOTS as int,
    ensures
        r == (x != NIL && live@[x as int] == 1u8),
{
    x != NIL && arr_get_unchecked(live, x as usize) == 1u8
}

// THE CHAIN WALK, shared by PUT, GET and DEL, and written once because all three
// spell it identically in every rung. Its `ensures` is the refinement: what the
// THE CHAIN WALK, shared by PUT, GET and DEL, and written once because all three
// spell it identically in every rung. Its `ensures` is the refinement: what the
// loop computes is exactly what the abstract machine's `descend` says.
//
// ⚠ **The `live[cur] == 1` conjunct in the loop condition is what licenses the
// object read**, through `base`'s `live[j] == 1 ==> rec_ok(..)`. Without it the
// read would need "every link names a live slot", which is the list invariant.
// The `steps < SLOTS` conjunct is the `decreases` measure. Neither ever fires.
#[inline(always)]
fn walk(
    tab: &[*mut Obj; SLOTS],
    live: &[u8; SLOTS],
    Tracked(perms): Tracked<&Map<int, PointsTo<Obj>>>,
    Ghost(st): Ghost<St>,
    Ghost(nmade): Ghost<int>,
    Ghost(bucket): Ghost<Seq<u8>>,
    start: u8,
    k: u8,
) -> (r: (u8, bool))
    requires
        base(tab@, live@, bucket, st, nmade, *perms),
        start == NIL || (start as int) < nmade,
    ensures
        r == descend(st, start, k, SLOTS as nat),
        r.0 == NIL || (r.0 as int) < nmade,
        r.1 ==> alive(st, r.0),
{
    let mut cur: u8 = start;
    let mut found: bool = false;
    let mut steps: usize = 0;
    while cur != NIL && arr_get_unchecked(live, cur as usize) == 1u8 && steps < SLOTS
        invariant_except_break
            !found,
            steps <= SLOTS,
            cur == NIL || (cur as int) < nmade,
            base(tab@, live@, bucket, st, nmade, *perms),
            descend(st, cur, k, (SLOTS - steps) as nat) == descend(st, start, k, SLOTS as nat),
        ensures
            (cur, found) == descend(st, start, k, SLOTS as nat),
            cur == NIL || (cur as int) < nmade,
            found ==> alive(st, cur),
        decreases SLOTS - steps,
    {
        assert(alive(st, cur));
        assert(rec_ok(tab@, st.ob, *perms, cur as int));
        let ob: Obj = {
            let tracked t = perms.tracked_borrow(cur as int);
            rec_read(arr_get_unchecked(tab, cur as usize), Tracked(t))
        };
        steps = steps + 1;
        // `ob.hn` is `st.ob[cur].hn`, and `links_ok` is what says it is `NIL` or
        // a real slot. The instantiation has to be asked for by name: `base`
        // triggers on `links_ok(st.ob, j, nmade)` and nothing else in this loop
        // mentions it.
        assert(links_ok(st.ob, cur as int, nmade));
        if ob.key == k {
            found = true;
            break;
        }
        cur = ob.hn;
    }
    (cur, found)
}

// ---------------------------------------------------------------- kernel ----
// Same exec code as unsafe.rs. Contract: ../spec.md.
//
// ⚠ **`#[verifier::rlimit(400)]` is a SOLVER BUDGET, not a soundness knob**, and
// it is here because this loop body carries four opcode arms, ten `alive_link`
// sites and a dozen invariant re-establishments in ONE query. The default is 10.
// Raising it does not weaken any obligation -- every one is still discharged --
// it only lets Z3 work longer before giving up. ../NOTES.md 6a records what the
// query cost before the `St` and guard changes above (it did not finish at all)
// and what it costs now.
#[verifier::rlimit(400)]
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> (r: u64)
    requires
        off + len <= buf@.len(),
    ensures
        r == cache_fold(buf@, off as int, len as int),
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
    let mut tab: [*mut Obj; SLOTS] = [core::ptr::null_mut(); SLOTS];
    let mut live: [u8; SLOTS] = [0u8; SLOTS];
    let mut bucket: [u8; NB] = [NIL; NB];
    let tracked mut perms = Map::<int, PointsTo<Obj>>::tracked_empty();
    let tracked mut dal = Map::<int, Dealloc>::tracked_empty();
    let ghost mut st: St = st0();
    let mut head: u8 = NIL;
    let mut tail: u8 = NIL;
    let mut nmade: usize = 0;
    let mut acc: u64 = 0;
    let mut p: usize = 4;
    let mut o: usize = 0;
    while o < nops
        invariant_except_break
            o <= nops,
            p <= len,
            off + len <= buf@.len(),
            buf@.len() <= usize::MAX,
            head == st.head,
            tail == st.tail,
            nmade == st.ob.len(),
            wf(tab@, live@, bucket@, st, nmade as int, perms, dal),
            run(buf@, off as int, len as int, o as int, nops as int, p as int, st, acc)
                == run(buf@, off as int, len as int, 0, nops as int, 4, st0(), 0),
        ensures
            nmade == st.ob.len(),
            wf(tab@, live@, bucket@, st, nmade as int, perms, dal),
            acc.wrapping_mul(31).wrapping_add(nmade as u64) == run(
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
        let b: usize = (a % NB as u8) as usize;
        assert(b as int == bkt(a));
        if c % 4 == 0 {
            let bh: u8 = arr_get_unchecked(&bucket, b);
            let (cur, found) = walk(
                &tab,
                &live,
                Tracked(&perms),
                Ghost(st),
                Ghost(nmade as int),
                Ghost(bucket@),
                bh,
                a,
            );
            if found {
                // A HIT updates the object's `val` IN PLACE. One write to a live
                // object; the only proof it needs is that the permission it
                // borrows is the one the invariant names.
                let ghost jj = cur as int;
                let ghost stv = st;
                let ghost permsv = perms;
                assert(rec_ok(tab@, st.ob, perms, jj));
                let tracked t = perms.tracked_borrow_mut(jj);
                let cb = arr_get_unchecked(&tab, cur as usize);
                let co = rec_read(cb, Tracked(&*t));
                rec_write(
                    cb,
                    Tracked(t),
                    Obj {
                        key: co.key,
                        val: a.wrapping_mul(7).wrapping_add(1),
                        lp: co.lp,
                        ln: co.ln,
                        hn: co.hn,
                        hp: co.hp,
                    },
                );
                proof {
                    st = St { ob: st.ob.update(jj, Obj { val: val_of(a), ..st.ob[jj] }), ..st };
                    assert forall|j: int|
                        0 <= j < nmade as int implies #[trigger] links_ok(
                        st.ob,
                        j,
                        nmade as int,
                    ) by { assert(links_ok(stv.ob, j, nmade as int)); }
                    assert forall|j: int|
                        0 <= j < nmade as int && live@[j] == 1u8 implies rec_ok(
                        tab@,
                        st.ob,
                        perms,
                        j,
                    ) by { if j != jj { assert(rec_ok(tab@, stv.ob, permsv, j)); } }
                }
                acc = acc.wrapping_mul(31).wrapping_add(a as u64);
            } else if nmade < SLOTS {
                let ghost n0 = nmade as int;
                let ghost stv = st;
                let ghost permsv = perms;
                let ghost dalv = dal;
                let ghost tabv = tab@;
                let ghost livev = live@;
                let s: u8 = nmade as u8;
                let (q, Tracked(pt), Tracked(dd)) = rec_open(
                    Obj {
                        key: a,
                        val: a.wrapping_mul(7).wrapping_add(1),
                        lp: NIL,
                        ln: head,
                        hn: bh,
                        hp: NIL,
                    },
                );
                proof {
                    perms.tracked_insert(n0, pt);
                    dal.tracked_insert(n0, dd);
                    st = St {
                        ob: st.ob.push(
                            Obj { key: a, val: val_of(a), lp: NIL, ln: st.head, hn: st.bk[b as int], hp: NIL },
                        ),
                        lv: st.lv.push(true),
                        ..st
                    };
                }
                arr_set_unchecked(&mut tab, nmade, q);
                arr_set_unchecked(&mut live, nmade, 1u8);
                nmade = nmade + 1;
                proof {
                    assert forall|j: int|
                        0 <= j < nmade as int implies #[trigger] links_ok(
                        st.ob,
                        j,
                        nmade as int,
                    ) by { if j < n0 { assert(links_ok(stv.ob, j, n0)); } }
                    assert forall|j: int|
                        0 <= j < nmade as int && live@[j] == 1u8 implies rec_ok(
                        tab@,
                        st.ob,
                        perms,
                        j,
                    ) by { if j < n0 { assert(rec_ok(tabv, stv.ob, permsv, j)); } }
                    assert forall|j: int|
                        0 <= j < nmade as int && live@[j] == 1u8 implies dal_ok(tab@, dal, j) by {
                        if j < n0 {
                            assert(dal_ok(tabv, dalv, j));
                        }
                    }
                }
                // the EVICTION list
                if alive_link(&live, head) {
                    let ghost pj = head as int;
                    let ghost stw = st;
                    let ghost permsw = perms;
                    assert(rec_ok(tab@, st.ob, perms, pj));
                    let tracked t = perms.tracked_borrow_mut(pj);
                    let pb = arr_get_unchecked(&tab, head as usize);
                    let po = rec_read(pb, Tracked(&*t));
                    rec_write(
                        pb,
                        Tracked(t),
                        Obj { key: po.key, val: po.val, lp: s, ln: po.ln, hn: po.hn, hp: po.hp },
                    );
                    proof {
                        st = St { ob: st.ob.update(pj, Obj { lp: s, ..st.ob[pj] }), ..st };
                        assert forall|j: int|
                            0 <= j < nmade as int implies #[trigger] links_ok(
                            st.ob,
                            j,
                            nmade as int,
                        ) by { assert(links_ok(stw.ob, j, nmade as int)); }
                        assert forall|j: int|
                            0 <= j < nmade as int && live@[j] == 1u8 implies rec_ok(
                            tab@,
                            st.ob,
                            perms,
                            j,
                        ) by { if j != pj { assert(rec_ok(tab@, stw.ob, permsw, j)); } }
                    }
                } else {
                    tail = s;
                    proof {
                        st = St { tail: s, ..st };
                    }
                }
                head = s;
                proof {
                    st = St { head: s, ..st };
                }
                // the HASH CHAIN
                if alive_link(&live, bh) {
                    let ghost hj = bh as int;
                    let ghost stw = st;
                    let ghost permsw = perms;
                    assert(rec_ok(tab@, st.ob, perms, hj));
                    let tracked t = perms.tracked_borrow_mut(hj);
                    let hb = arr_get_unchecked(&tab, bh as usize);
                    let ho = rec_read(hb, Tracked(&*t));
                    rec_write(
                        hb,
                        Tracked(t),
                        Obj { key: ho.key, val: ho.val, lp: ho.lp, ln: ho.ln, hn: ho.hn, hp: s },
                    );
                    proof {
                        st = St { ob: st.ob.update(hj, Obj { hp: s, ..st.ob[hj] }), ..st };
                        assert forall|j: int|
                            0 <= j < nmade as int implies #[trigger] links_ok(
                            st.ob,
                            j,
                            nmade as int,
                        ) by { assert(links_ok(stw.ob, j, nmade as int)); }
                        assert forall|j: int|
                            0 <= j < nmade as int && live@[j] == 1u8 implies rec_ok(
                            tab@,
                            st.ob,
                            perms,
                            j,
                        ) by { if j != hj { assert(rec_ok(tab@, stw.ob, permsw, j)); } }
                    }
                }
                arr_set_unchecked(&mut bucket, b, s);
                proof {
                    st = St { bk: st.bk.update(b as int, s), ..st };
                }
                acc = acc.wrapping_mul(31).wrapping_add(a as u64);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else if c % 4 == 1 {
            let bh: u8 = arr_get_unchecked(&bucket, b);
            let (cur, found) = walk(
                &tab,
                &live,
                Tracked(&perms),
                Ghost(st),
                Ghost(nmade as int),
                Ghost(bucket@),
                bh,
                a,
            );
            if found {
                assert(rec_ok(tab@, st.ob, perms, cur as int));
                let co = {
                    let tracked t = perms.tracked_borrow(cur as int);
                    rec_read(arr_get_unchecked(&tab, cur as usize), Tracked(t))
                };
                acc = acc.wrapping_mul(31).wrapping_add(co.val as u64);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else if c % 4 == 2 {
            let bh: u8 = arr_get_unchecked(&bucket, b);
            let (cur, found) = walk(
                &tab,
                &live,
                Tracked(&perms),
                Ghost(st),
                Ghost(nmade as int),
                Ghost(bucket@),
                bh,
                a,
            );
            if found {
                assert(rec_ok(tab@, st.ob, perms, cur as int));
                assert(links_ok(st.ob, cur as int, nmade as int));
                let cb = arr_get_unchecked(&tab, cur as usize);
                let co = {
                    let tracked t = perms.tracked_borrow(cur as int);
                    rec_read(cb, Tracked(t))
                };
                // out of the HASH CHAIN
                if alive_link(&live, co.hp) {
                    let ghost pj = co.hp as int;
                    let ghost stw = st;
                    let ghost permsw = perms;
                    assert(rec_ok(tab@, st.ob, perms, pj));
                    let tracked t = perms.tracked_borrow_mut(pj);
                    let pb = arr_get_unchecked(&tab, co.hp as usize);
                    let po = rec_read(pb, Tracked(&*t));
                    rec_write(
                        pb,
                        Tracked(t),
                        Obj {
                            key: po.key,
                            val: po.val,
                            lp: po.lp,
                            ln: po.ln,
                            hn: co.hn,
                            hp: po.hp,
                        },
                    );
                    proof {
                        st = St { ob: st.ob.update(pj, Obj { hn: co.hn, ..st.ob[pj] }), ..st };
                        assert forall|j: int|
                            0 <= j < nmade as int implies #[trigger] links_ok(
                            st.ob,
                            j,
                            nmade as int,
                        ) by { assert(links_ok(stw.ob, j, nmade as int)); }
                        assert forall|j: int|
                            0 <= j < nmade as int && live@[j] == 1u8 implies rec_ok(
                            tab@,
                            st.ob,
                            perms,
                            j,
                        ) by { if j != pj { assert(rec_ok(tab@, stw.ob, permsw, j)); } }
                    }
                } else {
                    arr_set_unchecked(&mut bucket, b, co.hn);
                    proof {
                        st = St { bk: st.bk.update(b as int, co.hn), ..st };
                    }
                }
                if alive_link(&live, co.hn) {
                    let ghost nj = co.hn as int;
                    let ghost stw = st;
                    let ghost permsw = perms;
                    assert(rec_ok(tab@, st.ob, perms, nj));
                    let tracked t = perms.tracked_borrow_mut(nj);
                    let nb = arr_get_unchecked(&tab, co.hn as usize);
                    let no = rec_read(nb, Tracked(&*t));
                    rec_write(
                        nb,
                        Tracked(t),
                        Obj {
                            key: no.key,
                            val: no.val,
                            lp: no.lp,
                            ln: no.ln,
                            hn: no.hn,
                            hp: co.hp,
                        },
                    );
                    proof {
                        st = St { ob: st.ob.update(nj, Obj { hp: co.hp, ..st.ob[nj] }), ..st };
                        assert forall|j: int|
                            0 <= j < nmade as int implies #[trigger] links_ok(
                            st.ob,
                            j,
                            nmade as int,
                        ) by { assert(links_ok(stw.ob, j, nmade as int)); }
                        assert forall|j: int|
                            0 <= j < nmade as int && live@[j] == 1u8 implies rec_ok(
                            tab@,
                            st.ob,
                            perms,
                            j,
                        ) by { if j != nj { assert(rec_ok(tab@, stw.ob, permsw, j)); } }
                    }
                }
                // out of the EVICTION list
                if alive_link(&live, co.lp) {
                    let ghost pj = co.lp as int;
                    let ghost stw = st;
                    let ghost permsw = perms;
                    assert(rec_ok(tab@, st.ob, perms, pj));
                    let tracked t = perms.tracked_borrow_mut(pj);
                    let pb = arr_get_unchecked(&tab, co.lp as usize);
                    let po = rec_read(pb, Tracked(&*t));
                    rec_write(
                        pb,
                        Tracked(t),
                        Obj {
                            key: po.key,
                            val: po.val,
                            lp: po.lp,
                            ln: co.ln,
                            hn: po.hn,
                            hp: po.hp,
                        },
                    );
                    proof {
                        st = St { ob: st.ob.update(pj, Obj { ln: co.ln, ..st.ob[pj] }), ..st };
                        assert forall|j: int|
                            0 <= j < nmade as int implies #[trigger] links_ok(
                            st.ob,
                            j,
                            nmade as int,
                        ) by { assert(links_ok(stw.ob, j, nmade as int)); }
                        assert forall|j: int|
                            0 <= j < nmade as int && live@[j] == 1u8 implies rec_ok(
                            tab@,
                            st.ob,
                            perms,
                            j,
                        ) by { if j != pj { assert(rec_ok(tab@, stw.ob, permsw, j)); } }
                    }
                } else {
                    head = co.ln;
                    proof {
                        st = St { head: co.ln, ..st };
                    }
                }
                if alive_link(&live, co.ln) {
                    let ghost nj = co.ln as int;
                    let ghost stw = st;
                    let ghost permsw = perms;
                    assert(rec_ok(tab@, st.ob, perms, nj));
                    let tracked t = perms.tracked_borrow_mut(nj);
                    let nb = arr_get_unchecked(&tab, co.ln as usize);
                    let no = rec_read(nb, Tracked(&*t));
                    rec_write(
                        nb,
                        Tracked(t),
                        Obj {
                            key: no.key,
                            val: no.val,
                            lp: co.lp,
                            ln: no.ln,
                            hn: no.hn,
                            hp: no.hp,
                        },
                    );
                    proof {
                        st = St { ob: st.ob.update(nj, Obj { lp: co.lp, ..st.ob[nj] }), ..st };
                        assert forall|j: int|
                            0 <= j < nmade as int implies #[trigger] links_ok(
                            st.ob,
                            j,
                            nmade as int,
                        ) by { assert(links_ok(stw.ob, j, nmade as int)); }
                        assert forall|j: int|
                            0 <= j < nmade as int && live@[j] == 1u8 implies rec_ok(
                            tab@,
                            st.ob,
                            perms,
                            j,
                        ) by { if j != nj { assert(rec_ok(tab@, stw.ob, permsw, j)); } }
                    }
                } else {
                    tail = co.lp;
                    proof {
                        st = St { tail: co.lp, ..st };
                    }
                }
                let ghost jj = cur as int;
                let ghost stw = st;
                let ghost permsw = perms;
                let ghost dalw = dal;
                let ghost livew = live@;
                assert(rec_ok(tab@, st.ob, perms, jj));
                assert(dal_ok(tab@, dal, jj));
                let tracked pt = perms.tracked_remove(jj);
                let tracked dd = dal.tracked_remove(jj);
                rec_close(cb, Tracked(pt), Tracked(dd));
                arr_set_unchecked(&mut live, cur as usize, 0u8);
                proof {
                    st = St { lv: st.lv.update(jj, false), ..st };
                    assert forall|j: int|
                        0 <= j < nmade as int && live@[j] == 1u8 implies rec_ok(
                        tab@,
                        st.ob,
                        perms,
                        j,
                    ) by {
                        assert(j != jj);
                        assert(rec_ok(tab@, stw.ob, permsw, j));
                    }
                    assert forall|j: int|
                        0 <= j < nmade as int && live@[j] == 1u8 implies dal_ok(tab@, dal, j) by {
                        assert(j != jj);
                        assert(dal_ok(tab@, dalw, j));
                    }
                }
                acc = acc.wrapping_mul(31).wrapping_add(2);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        } else {
            if alive_link(&live, tail) {
                let v: u8 = tail;
                assert(rec_ok(tab@, st.ob, perms, v as int));
                assert(links_ok(st.ob, v as int, nmade as int));
                let vp = arr_get_unchecked(&tab, v as usize);
                let vo = {
                    let tracked t = perms.tracked_borrow(v as int);
                    rec_read(vp, Tracked(t))
                };
                // leave the EVICTION list
                if alive_link(&live, vo.lp) {
                    let ghost pj = vo.lp as int;
                    let ghost stw = st;
                    let ghost permsw = perms;
                    assert(rec_ok(tab@, st.ob, perms, pj));
                    let tracked t = perms.tracked_borrow_mut(pj);
                    let pb = arr_get_unchecked(&tab, vo.lp as usize);
                    let po = rec_read(pb, Tracked(&*t));
                    rec_write(
                        pb,
                        Tracked(t),
                        Obj { key: po.key, val: po.val, lp: po.lp, ln: NIL, hn: po.hn, hp: po.hp },
                    );
                    proof {
                        st = St { ob: st.ob.update(pj, Obj { ln: NIL, ..st.ob[pj] }), ..st };
                        assert forall|j: int|
                            0 <= j < nmade as int implies #[trigger] links_ok(
                            st.ob,
                            j,
                            nmade as int,
                        ) by { assert(links_ok(stw.ob, j, nmade as int)); }
                        assert forall|j: int|
                            0 <= j < nmade as int && live@[j] == 1u8 implies rec_ok(
                            tab@,
                            st.ob,
                            perms,
                            j,
                        ) by { if j != pj { assert(rec_ok(tab@, stw.ob, permsw, j)); } }
                    }
                } else {
                    head = NIL;
                    proof {
                        st = St { head: NIL, ..st };
                    }
                }
                tail = vo.lp;
                proof {
                    st = St { tail: vo.lp, ..st };
                }
                // THE SAFETY LINE. c/kernel.c omits exactly this and nothing
                // else. What FORCES it here is `run`, not the permissions --
                // see this file's header and ../NOTES.md 6.
                let vb: usize = (vo.key % NB as u8) as usize;
                if alive_link(&live, vo.hp) {
                    let ghost pj = vo.hp as int;
                    let ghost stw = st;
                    let ghost permsw = perms;
                    assert(rec_ok(tab@, st.ob, perms, pj));
                    let tracked t = perms.tracked_borrow_mut(pj);
                    let pb = arr_get_unchecked(&tab, vo.hp as usize);
                    let po = rec_read(pb, Tracked(&*t));
                    rec_write(
                        pb,
                        Tracked(t),
                        Obj {
                            key: po.key,
                            val: po.val,
                            lp: po.lp,
                            ln: po.ln,
                            hn: vo.hn,
                            hp: po.hp,
                        },
                    );
                    proof {
                        st = St { ob: st.ob.update(pj, Obj { hn: vo.hn, ..st.ob[pj] }), ..st };
                        assert forall|j: int|
                            0 <= j < nmade as int implies #[trigger] links_ok(
                            st.ob,
                            j,
                            nmade as int,
                        ) by { assert(links_ok(stw.ob, j, nmade as int)); }
                        assert forall|j: int|
                            0 <= j < nmade as int && live@[j] == 1u8 implies rec_ok(
                            tab@,
                            st.ob,
                            perms,
                            j,
                        ) by { if j != pj { assert(rec_ok(tab@, stw.ob, permsw, j)); } }
                    }
                } else {
                    arr_set_unchecked(&mut bucket, vb, vo.hn);
                    proof {
                        st = St { bk: st.bk.update(vb as int, vo.hn), ..st };
                    }
                }
                if alive_link(&live, vo.hn) {
                    let ghost nj = vo.hn as int;
                    let ghost stw = st;
                    let ghost permsw = perms;
                    assert(rec_ok(tab@, st.ob, perms, nj));
                    let tracked t = perms.tracked_borrow_mut(nj);
                    let nb = arr_get_unchecked(&tab, vo.hn as usize);
                    let no = rec_read(nb, Tracked(&*t));
                    rec_write(
                        nb,
                        Tracked(t),
                        Obj {
                            key: no.key,
                            val: no.val,
                            lp: no.lp,
                            ln: no.ln,
                            hn: no.hn,
                            hp: vo.hp,
                        },
                    );
                    proof {
                        st = St { ob: st.ob.update(nj, Obj { hp: vo.hp, ..st.ob[nj] }), ..st };
                        assert forall|j: int|
                            0 <= j < nmade as int implies #[trigger] links_ok(
                            st.ob,
                            j,
                            nmade as int,
                        ) by { assert(links_ok(stw.ob, j, nmade as int)); }
                        assert forall|j: int|
                            0 <= j < nmade as int && live@[j] == 1u8 implies rec_ok(
                            tab@,
                            st.ob,
                            perms,
                            j,
                        ) by { if j != nj { assert(rec_ok(tab@, stw.ob, permsw, j)); } }
                    }
                }
                let ghost jj = v as int;
                let ghost stw = st;
                let ghost permsw = perms;
                let ghost dalw = dal;
                assert(rec_ok(tab@, st.ob, perms, jj));
                assert(dal_ok(tab@, dal, jj));
                let tracked pt = perms.tracked_remove(jj);
                let tracked dd = dal.tracked_remove(jj);
                rec_close(vp, Tracked(pt), Tracked(dd));
                arr_set_unchecked(&mut live, v as usize, 0u8);
                proof {
                    st = St { lv: st.lv.update(jj, false), ..st };
                    assert forall|j: int|
                        0 <= j < nmade as int && live@[j] == 1u8 implies rec_ok(
                        tab@,
                        st.ob,
                        perms,
                        j,
                    ) by {
                        assert(j != jj);
                        assert(rec_ok(tab@, stw.ob, permsw, j));
                    }
                    assert forall|j: int|
                        0 <= j < nmade as int && live@[j] == 1u8 implies dal_ok(tab@, dal, j) by {
                        assert(j != jj);
                        assert(dal_ok(tab@, dalw, j));
                    }
                }
                acc = acc.wrapping_mul(31).wrapping_add(3);
            } else {
                acc = acc.wrapping_mul(31).wrapping_add(SENT);
            }
        }
        proof {
            // ⚠⚠ `put_new`, `del_at`, `trim` and `step` are `#[verifier::opaque]`
            // and revealed HERE and nowhere else. They are needed by exactly one
            // obligation -- this refinement assert -- and carrying their bodies
            // through the other ~200 statements of the loop is what the solver's
            // budget was being spent on. MEASURED, and it is the difference
            // between a file that verifies and one that does not: with them
            // TRANSPARENT the `--cfg slb_twin` configuration -- which is where
            // `check.py`'s twin stage runs, and which adds five more verified
            // functions and vstd's allocation axioms to the shared context --
            // reports `Resource limit (rlimit) exceeded` on this loop at 400 AND
            // at 2000, the second run killed at 9m43s and so already past
            // `check.py`'s 900 s per-run timeout. OPAQUE, both configurations
            // verify at rlimit 80 (`23/0` and `28/0`) and fail at 60, so the
            // shipped 400 is a 5x margin. ../NOTES.md 6b.
            reveal(step);
            reveal(put_new);
            reveal(del_at);
            reveal(trim);
            assert(st == step(st_in, c, a).0);
            assert(acc == acc_in.wrapping_mul(31).wrapping_add(step(st_in, c, a).1));
            assert(run(buf@, off as int, len as int, o_in, nops as int, p_in, st_in, acc_in)
                == run(buf@, off as int, len as int, o_in + 1, nops as int, p_in + 2, st, acc));
        }
        o = o + 1;
    }
    // ------- the epilogue: free every object still alive --------------------
    // R2 and R3 do not have this loop: dropping the table IS this loop, written
    // by the language. ⚠ It walks the SLOT TABLE where the C rungs walk the
    // EVICTION LIST; both free each live object exactly once, and ../NOTES.md 5
    // records the difference. The invariant is `wf` weakened to the SUFFIX
    // `[j, nmade)`, which is what lets the epilogue skip a dead liveness store
    // -- p27's measured shape.
    let mut j: usize = 0;
    while j < nmade
        invariant
            j <= nmade,
            0 <= nmade <= SLOTS,
            tab@.len() == SLOTS,
            live@.len() == SLOTS,
            forall|k: int|
                j as int <= k < nmade as int && live@[k] == 1u8 ==> #[trigger] rec_ok(
                    tab@,
                    st.ob,
                    perms,
                    k,
                ),
            forall|k: int|
                j as int <= k < nmade as int && live@[k] == 1u8 ==> #[trigger] dal_ok(
                    tab@,
                    dal,
                    k,
                ),
        decreases nmade - j,
    {
        if arr_get_unchecked(&live, j) == 1u8 {
            assert(rec_ok(tab@, st.ob, perms, j as int));
            assert(dal_ok(tab@, dal, j as int));
            let ghost permsv = perms;
            let ghost dalv = dal;
            let tracked pt = perms.tracked_remove(j as int);
            let tracked dd = dal.tracked_remove(j as int);
            rec_close(arr_get_unchecked(&tab, j), Tracked(pt), Tracked(dd));
            proof {
                assert forall|k: int|
                    j as int + 1 <= k < nmade as int && live@[k] == 1u8 implies rec_ok(
                    tab@,
                    st.ob,
                    perms,
                    k,
                ) by {
                    assert(k != j as int);
                    assert(rec_ok(tab@, st.ob, permsv, k));
                }
                assert forall|k: int|
                    j as int + 1 <= k < nmade as int && live@[k] == 1u8 implies dal_ok(
                    tab@,
                    dal,
                    k,
                ) by {
                    assert(k != j as int);
                    assert(dal_ok(tab@, dalv, k));
                }
            }
        }
        j = j + 1;
    }
    acc.wrapping_mul(31).wrapping_add(nmade as u64)
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
            assert(r == cache_fold(buf@, (k * stride) as int, stride as int));
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    emit(acc);
}

} // verus!
