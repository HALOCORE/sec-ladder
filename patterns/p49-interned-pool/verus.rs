//! p49 rung R5 -- unsafe Rust + a Verus proof.
//!
//! This is unsafe.rs's exec code with the SAFETY comments turned into
//! obligations a verifier discharges. **Two things are new here, and they point
//! in opposite directions.**
//!
//! ⚠⚠ **NEW, AND IT IS WHAT `TASK_160` §8 PREDICTED NOTHING IN THE TREE STATES:
//! A DISJOINTNESS / PROVENANCE PRECONDITION.** `copy_bytes` -- the copy the
//! safety line performs -- carries
//!
//!     requires src + w <= dst,
//!
//! and that conjunct has to be DISCHARGED at the call site. It is discharged out
//! of `wf_prov`, the invariant that says **a SHARED buffer lives wholly inside
//! the interning arena while the private bump is at or above it**:
//! `roff[t] + rlen[t] <= ARENA <= pbump`. No other pattern in this tree states a
//! disjointness fact about two ranges of one object, because no other pattern
//! has two owners of one range.
//!
//! ⚠⚠ **AND WHAT IS *NOT* PROVED HERE IS THE ROW'S OTHER R5 RESULT, AND IT IS
//! `p32`'s FINDING IN A DIFFERENT CURRENCY.** The safety line itself --
//! `rshd[t] == 1` -- is discharged as an ORDINARY FUNCTIONAL POSTCONDITION. Both
//! arms of that `if` type-check without it, `roff[t] as usize` is in range either
//! way, and no permission is consumed anywhere in this function. What fails
//! without the test is the POSTCONDITION: the loop stops computing `run`.
//! **Linearity has nothing to say about this bug, because the bug does not touch
//! an allocation.** The pool is `[u8; MEM]`, a local array alive from the first
//! instruction of the kernel to the last; there is no `allocate`, no
//! `deallocate`, no `PointsTo`, no `Dealloc` token and no `global layout`
//! directive. ../NOTES.md 6b.
//!
//! ⚠ **AND THE `ensures` DOES NOT SAY "NO RECORD'S CONTENT ALIASES ANOTHER'S" --
//! BECAUSE THAT IS FALSE BY DESIGN.** Deduplication is the contract. What the
//! specification says is that the ANSWER is what the abstract machine computes,
//! and the abstract machine shares buffers exactly where the kernel does. The
//! disjointness that IS stated is narrower and is about the COPY: its source and
//! its destination do not overlap. ⚠ Saying it the other way round would be the
//! easy mistake and it would specify a different program.
//!
//! **TCB: five items** -- `buf_get_unchecked`, `arr_get_unchecked`,
//! `arr_set_unchecked`, `load_input`, `emit`. `p27` and `p29` ship SEVEN; the
//! two p49 does not need are `vstd::raw_ptr::allocate` and `deallocate`, because
//! **p49 allocates nothing**. Every one of the five is an item this project's
//! other unsafe rungs already ship, and three of them carry verified twins.
//!
//! SAFETY (1): `off + len <= buf.len()` is the caller's structural
//!   precondition. Unchecked in unsafe.rs; discharged at the call site here.
//! SAFETY (2): `len >= 4` guards the window header.
//! SAFETY (3): the op is read only under `len - p >= 2` with `p <= len`.
//! SAFETY (4): `w = 1 + a % MAXW` is in `1 ..= MAXW`, `key = a % NKEY` is in
//!   `0 ..< NKEY`.
//! SAFETY (5): `nent <= NENT` and `nrec <= NREC` -- `wf_sizes`.
//! SAFETY (6): `find` returns a value in `0 ..= nent` -- `lemma_find`.
//! SAFETY (7): `t = a % nrec` runs only under `nrec > 0`.
//! SAFETY (8): the provenance invariant -- `wf_prov`. See the note above.
//! SAFETY (9): **there is no temporal obligation, and that is the pattern.**

// Plain-Rust I/O helpers. Outside `verus!`, so Verus treats the whole module as
// external (external-by-default). Reached only through `load_input`/`emit`.
#[path = "../../common/driver.rs"]
mod driver;

use vstd::prelude::*;

verus! {

// `group_slice_axioms` gives `slice@.len() == spec_slice_len(slice)`, hence
// `slice@.len() <= usize::MAX`. `group_array_axioms` gives `v@.len() == N` and
// the fill axiom for `[0u8; N]`. `lemma_u128_shr_is_div` and
// `lemma_mul_inequality` are the DRIVER's. **No `raw_ptr` and no `layout` group
// here: p49 has no pointers and no allocation.**
broadcast use {
    vstd::slice::group_slice_axioms,
    vstd::array::group_array_axioms,
    vstd::bits::lemma_u128_shr_is_div,
    vstd::arithmetic::mul::lemma_mul_inequality,
};

/// The pool's extent, a compile-time constant in every rung.
pub const MEM: usize = 64;

/// Where the SHARED interning arena ends and the PRIVATE region begins.
pub const ARENA: usize = 20;

/// Dedup-table entries, a compile-time constant in every rung.
pub const NENT: usize = 8;

/// Records per window, a compile-time constant in every rung.
pub const NREC: usize = 12;

/// The content alphabet: `key = a % NKEY`.
pub const NKEY: u8 = 7;

/// The content widths: `w = 1 + a % MAXW`.
pub const MAXW: u8 = 6;

/// THE INLINE THRESHOLD. Content narrower than this is INTERNED and may be
/// shared; content at or above it is copied and is owned.
pub const THRESH: u8 = 4;

/// What a rejected operation folds. A compile-time constant in every rung.
pub const SENT: u64 = 251;

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

/// The width of the string an operand names.
pub open spec fn width_of(a: u8) -> u8 {
    ((a % MAXW) + 1) as u8
}

/// The key of the string an operand names.
pub open spec fn key_of(a: u8) -> u8 {
    a % NKEY
}

/// A content byte, in every rung. The string a record holds is
/// `cbyte(key,0) .. cbyte(key,w-1)`, so `(key, w)` names the string and nothing
/// else does -- which is why the dedup table's `(ekey, elen)` comparison is an
/// EXACT content comparison and not a hash with a collision story.
pub open spec fn cbyte_of(key: u8, j: u8) -> u8 {
    key.wrapping_mul(7).wrapping_add(j.wrapping_mul(13)).wrapping_add(1)
}

/// The pool after `w` bytes of the string `(key, ..)` are materialised at
/// `base`.
pub open spec fn filled(m: Seq<u8>, base: int, key: u8, w: int) -> Seq<u8>
    decreases w,
{
    if w <= 0 {
        m
    } else {
        filled(m, base, key, w - 1).update(base + w - 1, cbyte_of(key, (w - 1) as u8))
    }
}

/// The pool after `w` bytes are copied from `src` to `dst`. ⚠ Every byte is read
/// out of the ORIGINAL `m`, which is the same thing only because the two ranges
/// are disjoint -- `copy_bytes` below `requires` exactly that.
pub open spec fn copied(m: Seq<u8>, dst: int, src: int, w: int) -> Seq<u8>
    decreases w,
{
    if w <= 0 {
        m
    } else {
        copied(m, dst, src, w - 1).update(dst + w - 1, m[src + w - 1])
    }
}

/// The fold of `w` bytes of the pool starting at `base`.
pub open spec fn folded(m: Seq<u8>, base: int, w: int, acc: u64) -> u64
    decreases w,
{
    if w <= 0 {
        acc
    } else {
        folded(m, base, w - 1, acc).wrapping_mul(31).wrapping_add(m[base + w - 1] as u64)
    }
}

/// THE DEDUP LOOKUP: the first entry in `k .. nent` whose `(key, w)` matches, or
/// `nent`.
pub open spec fn find_from(
    ekey: Seq<u8>,
    elen: Seq<u8>,
    k: int,
    nent: int,
    key: u8,
    w: u8,
) -> int
    decreases nent - k,
{
    if k >= nent {
        nent
    } else if ekey[k] == key && elen[k] == w {
        k
    } else {
        find_from(ekey, elen, k + 1, nent, key, w)
    }
}

/// THE ABSTRACT MACHINE'S STATE, and it is the exec arrays and nothing else.
/// ⚠ Note what is NOT here and what `p27`'s and `p29`'s states do have: a
/// liveness sequence. **Nothing in p49 is ever allocated or freed**, so there is
/// no liveness to carry. `mem` is the pool, `ekey`/`elen`/`eoff` the dedup
/// table, `roff`/`rlen`/`rshd` the records, and `abump`/`pbump` the two bumps.
/// ⚠⚠ **Two records with the same `roff` is a perfectly well-formed value of
/// this type, and that is the CONTRACT rather than an omission.**
pub ghost struct St {
    pub mem: Seq<u8>,
    pub ekey: Seq<u8>,
    pub elen: Seq<u8>,
    pub eoff: Seq<u8>,
    pub roff: Seq<u8>,
    pub rlen: Seq<u8>,
    pub rshd: Seq<u8>,
    pub nent: int,
    pub nrec: int,
    pub abump: int,
    pub pbump: int,
}

/// The shape invariant: every array has its declared length and every counter is
/// inside its bound.
pub open spec fn wf_sizes(st: St) -> bool {
    &&& st.mem.len() == MEM as int
    &&& st.ekey.len() == NENT as int
    &&& st.elen.len() == NENT as int
    &&& st.eoff.len() == NENT as int
    &&& st.roff.len() == NREC as int
    &&& st.rlen.len() == NREC as int
    &&& st.rshd.len() == NREC as int
    &&& 0 <= st.nent <= NENT as int
    &&& 0 <= st.nrec <= NREC as int
    &&& 0 <= st.abump <= ARENA as int
    &&& ARENA as int <= st.pbump <= MEM as int
}

/// ⚠⚠ **THE PROVENANCE INVARIANT, AND IT IS THE ONE THIS ROW IS ABOUT.**
/// A SHARED buffer lives wholly inside the interning arena; an OWNED one lives
/// wholly inside the private region, below the bump. Either way a record's
/// content is inside the pool, which is what licenses every unchecked `mem[..]`
/// -- and the first clause is additionally what makes the copy-on-write copy's
/// source and destination DISJOINT, because `roff[t] + rlen[t] <= ARENA <=
/// pbump`.
pub open spec fn wf_prov(st: St) -> bool {
    &&& forall|k: int|
        0 <= k < st.nent ==> (#[trigger] st.eoff[k]) as int + (st.elen[k] as int) <= ARENA as int
    &&& forall|k: int| 0 <= k < st.nent ==> 1 <= (#[trigger] st.elen[k]) as int <= MAXW as int
    &&& forall|t: int| 0 <= t < st.nrec ==> 1 <= (#[trigger] st.rlen[t]) as int <= MAXW as int
    &&& forall|t: int|
        0 <= t < st.nrec ==> ((#[trigger] st.rshd[t]) == 0u8 || st.rshd[t] == 1u8)
    &&& forall|t: int|
        0 <= t < st.nrec && (#[trigger] st.rshd[t]) == 1u8 ==> (st.roff[t] as int) + (
        st.rlen[t] as int) <= ARENA as int
    &&& forall|t: int|
        0 <= t < st.nrec && (#[trigger] st.rshd[t]) == 0u8 ==> ARENA as int <= (
        st.roff[t] as int) && (st.roff[t] as int) + (st.rlen[t] as int) <= st.pbump
}

pub open spec fn wf(st: St) -> bool {
    wf_sizes(st) && wf_prov(st)
}

/// ONE OPERATION: the new state and what it folds.
///
/// **The `BREAK` arm is the whole pattern.** `c/kernel.c` writes
/// `mem[roff[t]] = 0` unconditionally; this machine asks whether the buffer is
/// the record's to write and takes a private copy first, and folds SENT when
/// there is no room for one.
pub open spec fn step(st: St, c: u8, a: u8) -> (St, u64) {
    let w = width_of(a);
    let key = key_of(a);
    if c % 4 == 0 || c % 4 == 1 {
        if st.nrec >= NREC as int {
            (st, SENT)
        } else if w < THRESH {
            let f = find_from(st.ekey, st.elen, 0, st.nent, key, w);
            if f == st.nent {
                if st.nent >= NENT as int || st.abump + (w as int) > ARENA as int {
                    (st, SENT)
                } else {
                    (
                        St {
                            mem: filled(st.mem, st.abump, key, w as int),
                            ekey: st.ekey.update(st.nent, key),
                            elen: st.elen.update(st.nent, w),
                            eoff: st.eoff.update(st.nent, st.abump as u8),
                            roff: st.roff.update(st.nrec, st.abump as u8),
                            rlen: st.rlen.update(st.nrec, w),
                            rshd: st.rshd.update(st.nrec, 1u8),
                            nent: st.nent + 1,
                            nrec: st.nrec + 1,
                            abump: st.abump + (w as int),
                            ..st
                        },
                        a as u64,
                    )
                }
            } else {
                (
                    St {
                        roff: st.roff.update(st.nrec, st.eoff[f]),
                        rlen: st.rlen.update(st.nrec, w),
                        rshd: st.rshd.update(st.nrec, 1u8),
                        nrec: st.nrec + 1,
                        ..st
                    },
                    a as u64,
                )
            }
        } else {
            if st.pbump + (w as int) > MEM as int {
                (st, SENT)
            } else {
                (
                    St {
                        mem: filled(st.mem, st.pbump, key, w as int),
                        roff: st.roff.update(st.nrec, st.pbump as u8),
                        rlen: st.rlen.update(st.nrec, w),
                        rshd: st.rshd.update(st.nrec, 0u8),
                        nrec: st.nrec + 1,
                        pbump: st.pbump + (w as int),
                        ..st
                    },
                    a as u64,
                )
            }
        }
    } else if c % 4 == 2 {
        if st.nrec == 0 {
            (st, SENT)
        } else {
            let t = (a as int) % st.nrec;
            if st.rshd[t] == 1u8 {
                if st.pbump + (st.rlen[t] as int) > MEM as int {
                    (st, SENT)
                } else {
                    (
                        St {
                            mem: copied(
                                st.mem,
                                st.pbump,
                                st.roff[t] as int,
                                st.rlen[t] as int,
                            ).update(st.pbump, 0u8),
                            roff: st.roff.update(t, st.pbump as u8),
                            rshd: st.rshd.update(t, 0u8),
                            pbump: st.pbump + (st.rlen[t] as int),
                            ..st
                        },
                        2u64,
                    )
                }
            } else {
                (St { mem: st.mem.update(st.roff[t] as int, 0u8), ..st }, 2u64)
            }
        }
    } else {
        if st.nrec == 0 {
            (st, SENT)
        } else {
            let t = (a as int) % st.nrec;
            (st, folded(st.mem, st.roff[t] as int, st.rlen[t] as int, 0))
        }
    }
}

/// The epilogue: fold every record's content and its ownership flag.
/// ⚠ The flag is in the answer on purpose -- it is this kernel's reduction of
/// the port's `"interned":true/false` API field, and it is what makes the
/// PROVENANCE repair benign-observable while copy-on-write is not.
pub open spec fn fold_recs(st: St, t: int, acc: u64) -> u64
    decreases st.nrec - t,
{
    if t >= st.nrec {
        acc
    } else {
        fold_recs(
            st,
            t + 1,
            folded(st.mem, st.roff[t] as int, st.rlen[t] as int, acc).wrapping_mul(
                31,
            ).wrapping_add(st.rshd[t] as u64),
        )
    }
}

/// The empty machine: a zeroed pool, an empty dedup table, no records, the arena
/// bump at 0 and the private bump at `ARENA`.
pub open spec fn st0() -> St {
    St {
        mem: Seq::new(MEM as nat, |i: int| 0u8),
        ekey: Seq::new(NENT as nat, |i: int| 0u8),
        elen: Seq::new(NENT as nat, |i: int| 0u8),
        eoff: Seq::new(NENT as nat, |i: int| 0u8),
        roff: Seq::new(NREC as nat, |i: int| 0u8),
        rlen: Seq::new(NREC as nat, |i: int| 0u8),
        rshd: Seq::new(NREC as nat, |i: int| 0u8),
        nent: 0,
        nrec: 0,
        abump: 0,
        pbump: ARENA as int,
    }
}

/// THE ABSTRACT MACHINE. It describes the PROGRAM -- stop when the window runs
/// out, fold SENT for a DEFINE past the record table, past the dedup table, past
/// the arena or past the private region, fold SENT for a BREAK or a READ with no
/// records, fold SENT for a BREAK that cannot un-share -- and it says nothing
/// about `nops` being honest or about the op stream being well formed. Every
/// adversarial input is inside this domain (../spec.md).
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
        fold_recs(st, 0, acc).wrapping_mul(31).wrapping_add(st.nrec as u64)
    } else {
        let s = step(st, buf[off + p], buf[off + p + 1]);
        run(buf, off, len, o + 1, nops, p + 2, s.0, acc.wrapping_mul(31).wrapping_add(s.1))
    }
}

/// What the kernel must return.
pub open spec fn intern_fold(buf: Seq<u8>, off: int, len: int) -> u64 {
    if len < 4 {
        0
    } else if nops_at(buf, off) == 0 {
        0
    } else {
        run(buf, off, len, 0, nops_at(buf, off), 4, st0(), 0)
    }
}

// ----------------------------------------------------------------- proof ----
/// `find_from` returns an index in `k ..= nent`, and when it is below `nent` the
/// entry it names really matches. Both halves are needed: the first to index
/// `eoff` safely, the second to inherit `eoff[f] + elen[f] <= ARENA` for the
/// record the dedup HIT creates.
pub proof fn lemma_find(ek: Seq<u8>, el: Seq<u8>, k: int, n: int, key: u8, w: u8)
    requires
        0 <= k <= n,
    ensures
        k <= find_from(ek, el, k, n, key, w) <= n,
        find_from(ek, el, k, n, key, w) < n ==> ek[find_from(ek, el, k, n, key, w)] == key,
        find_from(ek, el, k, n, key, w) < n ==> el[find_from(ek, el, k, n, key, w)] == w,
    decreases n - k,
{
    if k < n && !(ek[k] == key && el[k] == w) {
        lemma_find(ek, el, k + 1, n, key, w);
    }
}

/// Every record's content is inside the pool, and a SHARED record's content is
/// inside the ARENA. Both follow from `wf_prov` by a case split on the ownership
/// flag, and this lemma exists to force that case split -- the quantifiers are
/// triggered on `st.rshd[t]`, so something has to mention it.
///
/// ⚠⚠ **IT IS A SOLVER HINT AND NOT A LOAD-BEARING LEMMA, AND THAT IS
/// MEASURED**: `../controls/proof_mutants.py`'s `M4` deletes both calls to it
/// and the file still verifies. The reason is `M5`: the SAME solver blow-up is
/// cured independently by spelling `lemma_find`'s second `ensures` as TWO
/// clauses instead of one `&&`-joined clause, and the shipped file carries both
/// cures, so neither is necessary given the other. Delete both and the kernel's
/// op loop reports `Resource limit (rlimit) exceeded` at the default budget.
/// ../NOTES.md 8c.
pub proof fn lemma_rec_in_pool(st: St, t: int)
    requires
        wf(st),
        0 <= t < st.nrec,
    ensures
        1 <= st.rlen[t] as int <= MAXW as int,
        (st.roff[t] as int) + (st.rlen[t] as int) <= MEM as int,
        st.rshd[t] == 1u8 ==> (st.roff[t] as int) + (st.rlen[t] as int) <= ARENA as int,
{
    assert(st.rshd[t] == 0u8 || st.rshd[t] == 1u8);
}

/// A copy into `dst .. dst+w` leaves everything below `dst` alone. That is what
/// lets `copy_bytes` read its source out of the pool it is writing to, and it
/// needs the DISJOINTNESS the caller supplies.
pub proof fn lemma_copied_below(m: Seq<u8>, dst: int, src: int, w: int, i: int)
    requires
        0 <= w,
        0 <= i < dst,
    ensures
        copied(m, dst, src, w)[i] == m[i],
        copied(m, dst, src, w).len() == m.len(),
    decreases w,
{
    if w > 0 {
        lemma_copied_below(m, dst, src, w - 1, i);
    }
}

// ------------------------------------------------------------------- TCB ----
// TRUSTED ITEM 1 of 5. vstd ships no specification for `<[T]>::get_unchecked`,
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

// TRUSTED ITEM 4 of 5: the input loader. Plain Rust I/O, no `unsafe`, no
// `ensures` -- it is outside the memory-safety argument entirely.
#[verifier::external_body]
fn load_input() -> (r: (u64, u64, Vec<u8>)) {
    let path = driver::arg_path();
    let inp = driver::load(&path);
    let (stride_w, bytes) = driver::head1_u64_bytes(&inp);
    (inp.n_iters, stride_w, bytes)
}

// TRUSTED ITEM 5 of 5: the output. Same shape, same reason.
#[verifier::external_body]
fn emit(acc: u64) {
    driver::emit(acc);
}

// TRUSTED ITEMS 2 and 3 of 5: the unchecked ARRAY read and store, generic over
// the element type so that the pool, the dedup table and the record table share
// one accessor. Same documented `get_unchecked` contract as item 1.
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

// --------------------------------------------------------------- helpers ----
/// A content byte. `(key, w)` names the string; ../safe_naive.rs says why.
#[inline(always)]
fn cbyte(key: u8, j: u8) -> (r: u8)
    ensures
        r == cbyte_of(key, j),
{
    key.wrapping_mul(7).wrapping_add(j.wrapping_mul(13)).wrapping_add(1)
}

/// THE DEDUP LOOKUP. Returns `nent` when the string is absent.
#[inline(always)]
fn find(ekey: &[u8; NENT], elen: &[u8; NENT], nent: usize, key: u8, w: u8) -> (r: usize)
    requires
        nent <= NENT,
    ensures
        r as int == find_from(ekey@, elen@, 0, nent as int, key, w),
        r <= nent,
{
    let mut k: usize = 0;
    while k < nent
        invariant_except_break
            k <= nent,
            nent <= NENT,
            ekey@.len() == NENT as int,
            elen@.len() == NENT as int,
            find_from(ekey@, elen@, k as int, nent as int, key, w) == find_from(
                ekey@,
                elen@,
                0,
                nent as int,
                key,
                w,
            ),
        ensures
            k <= nent,
            k as int == find_from(ekey@, elen@, 0, nent as int, key, w),
        decreases nent - k,
    {
        if arr_get_unchecked(ekey, k) == key && arr_get_unchecked(elen, k) == w {
            break;
        }
        k = k + 1;
    }
    k
}

/// Materialise a string into the pool.
#[inline(always)]
fn fill(mem: &mut [u8; MEM], base: usize, key: u8, w: u8)
    requires
        base + w <= MEM,
    ensures
        final(mem)@ == filled(old(mem)@, base as int, key, w as int),
{
    let ghost m0 = mem@;
    let mut j: u8 = 0;
    while j < w
        invariant
            j <= w,
            base + w <= MEM,
            mem@.len() == MEM as int,
            mem@ == filled(m0, base as int, key, j as int),
        decreases w - j,
    {
        arr_set_unchecked(mem, base + j as usize, cbyte(key, j));
        j = j + 1;
    }
}

/// THE COPY-ON-WRITE COPY.
///
/// ⚠⚠ **`src + w <= dst` IS THE DISJOINTNESS / PROVENANCE PRECONDITION, AND IT
/// IS THE OBLIGATION `TASK_160` §8 PREDICTED NOTHING IN THIS TREE STATES.** It
/// is what makes reading the source out of the pool this call is writing to the
/// same thing as reading it out of the pool as it was; `lemma_copied_below` is
/// the step that uses it. It is discharged at the call site out of `wf_prov`:
/// the record is SHARED, so its content lies inside `mem[0 .. ARENA)` and the
/// private bump is at or above `ARENA`.
#[inline(always)]
fn copy_bytes(mem: &mut [u8; MEM], dst: usize, src: usize, w: u8)
    requires
        src + w <= dst,
        dst + w <= MEM,
    ensures
        final(mem)@ == copied(old(mem)@, dst as int, src as int, w as int),
{
    let ghost m0 = mem@;
    let mut j: u8 = 0;
    while j < w
        invariant
            j <= w,
            src + w <= dst,
            dst + w <= MEM,
            mem@.len() == MEM as int,
            mem@ == copied(m0, dst as int, src as int, j as int),
        decreases w - j,
    {
        proof {
            lemma_copied_below(m0, dst as int, src as int, j as int, src + j as int);
        }
        let x: u8 = arr_get_unchecked(mem, src + j as usize);
        arr_set_unchecked(mem, dst + j as usize, x);
        j = j + 1;
    }
}

/// Fold a string out of the pool.
#[inline(always)]
fn fold_bytes(mem: &[u8; MEM], base: usize, w: u8, acc: u64) -> (r: u64)
    requires
        base + w <= MEM,
    ensures
        r == folded(mem@, base as int, w as int, acc),
{
    let mut j: u8 = 0;
    let mut x: u64 = acc;
    while j < w
        invariant
            j <= w,
            base + w <= MEM,
            mem@.len() == MEM as int,
            x == folded(mem@, base as int, j as int, acc),
        decreases w - j,
    {
        x = x.wrapping_mul(31).wrapping_add(arr_get_unchecked(mem, base + j as usize) as u64);
        j = j + 1;
    }
    x
}

// ---------------------------------------------------------------- kernel ----
// Same exec code as unsafe.rs. Contract: ../spec.md.
#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> (r: u64)
    requires
        off + len <= buf@.len(),
    ensures
        r == intern_fold(buf@, off as int, len as int),
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
    let mut mem: [u8; MEM] = [0u8; MEM];
    let mut ekey: [u8; NENT] = [0u8; NENT];
    let mut elen: [u8; NENT] = [0u8; NENT];
    let mut eoff: [u8; NENT] = [0u8; NENT];
    let mut roff: [u8; NREC] = [0u8; NREC];
    let mut rlen: [u8; NREC] = [0u8; NREC];
    let mut rshd: [u8; NREC] = [0u8; NREC];
    let mut nent: usize = 0;
    let mut nrec: usize = 0;
    let mut abump: usize = 0;
    let mut pbump: usize = ARENA;
    let mut acc: u64 = 0;
    let mut p: usize = 4;
    let mut o: usize = 0;
    proof {
        assert(mem@ =~= st0().mem);
        assert(ekey@ =~= st0().ekey);
        assert(elen@ =~= st0().elen);
        assert(eoff@ =~= st0().eoff);
        assert(roff@ =~= st0().roff);
        assert(rlen@ =~= st0().rlen);
        assert(rshd@ =~= st0().rshd);
        assert(St {
            mem: mem@,
            ekey: ekey@,
            elen: elen@,
            eoff: eoff@,
            roff: roff@,
            rlen: rlen@,
            rshd: rshd@,
            nent: nent as int,
            nrec: nrec as int,
            abump: abump as int,
            pbump: pbump as int,
        } =~= st0());
    }
    while o < nops
        invariant_except_break
            o <= nops,
            p <= len,
            4 <= len,
            off + len <= buf@.len(),
            buf@.len() <= usize::MAX,
            nent <= NENT,
            nrec <= NREC,
            abump <= ARENA,
            ARENA <= pbump <= MEM,
            wf(
                St {
                    mem: mem@,
                    ekey: ekey@,
                    elen: elen@,
                    eoff: eoff@,
                    roff: roff@,
                    rlen: rlen@,
                    rshd: rshd@,
                    nent: nent as int,
                    nrec: nrec as int,
                    abump: abump as int,
                    pbump: pbump as int,
                },
            ),
            run(
                buf@,
                off as int,
                len as int,
                o as int,
                nops as int,
                p as int,
                St {
                    mem: mem@,
                    ekey: ekey@,
                    elen: elen@,
                    eoff: eoff@,
                    roff: roff@,
                    rlen: rlen@,
                    rshd: rshd@,
                    nent: nent as int,
                    nrec: nrec as int,
                    abump: abump as int,
                    pbump: pbump as int,
                },
                acc,
            ) == run(buf@, off as int, len as int, 0, nops as int, 4, st0(), 0),
        ensures
            o >= nops || len - p < 2,
            nrec <= NREC,
            wf(
                St {
                    mem: mem@,
                    ekey: ekey@,
                    elen: elen@,
                    eoff: eoff@,
                    roff: roff@,
                    rlen: rlen@,
                    rshd: rshd@,
                    nent: nent as int,
                    nrec: nrec as int,
                    abump: abump as int,
                    pbump: pbump as int,
                },
            ),
            run(
                buf@,
                off as int,
                len as int,
                o as int,
                nops as int,
                p as int,
                St {
                    mem: mem@,
                    ekey: ekey@,
                    elen: elen@,
                    eoff: eoff@,
                    roff: roff@,
                    rlen: rlen@,
                    rshd: rshd@,
                    nent: nent as int,
                    nrec: nrec as int,
                    abump: abump as int,
                    pbump: pbump as int,
                },
                acc,
            ) == run(buf@, off as int, len as int, 0, nops as int, 4, st0(), 0),
        decreases nops - o,
    {
        if len - p < 2 {
            break;
        }
        let c: u8 = buf_get_unchecked(buf, off + p);
        let a: u8 = buf_get_unchecked(buf, off + p + 1);
        let ghost st_in = St {
            mem: mem@,
            ekey: ekey@,
            elen: elen@,
            eoff: eoff@,
            roff: roff@,
            rlen: rlen@,
            rshd: rshd@,
            nent: nent as int,
            nrec: nrec as int,
            abump: abump as int,
            pbump: pbump as int,
        };
        let ghost acc_in = acc;
        let ghost p_in = p as int;
        let ghost o_in = o as int;
        p = p + 2;
        let w: u8 = 1 + a % MAXW;
        let key: u8 = a % NKEY;
        let v: u64 = if c % 4 == 0 || c % 4 == 1 {
            if nrec >= NREC {
                SENT
            } else if w < THRESH {
                let f: usize = find(&ekey, &elen, nent, key, w);
                proof {
                    lemma_find(ekey@, elen@, 0, nent as int, key, w);
                }
                if f == nent {
                    if nent >= NENT || abump + (w as usize) > ARENA {
                        SENT
                    } else {
                        fill(&mut mem, abump, key, w);
                        arr_set_unchecked(&mut ekey, nent, key);
                        arr_set_unchecked(&mut elen, nent, w);
                        arr_set_unchecked(&mut eoff, nent, abump as u8);
                        arr_set_unchecked(&mut roff, nrec, abump as u8);
                        arr_set_unchecked(&mut rlen, nrec, w);
                        arr_set_unchecked(&mut rshd, nrec, 1);
                        nent = nent + 1;
                        abump = abump + w as usize;
                        nrec = nrec + 1;
                        a as u64
                    }
                } else {
                    let e: u8 = arr_get_unchecked(&eoff, f);
                    arr_set_unchecked(&mut roff, nrec, e);
                    arr_set_unchecked(&mut rlen, nrec, w);
                    arr_set_unchecked(&mut rshd, nrec, 1);
                    nrec = nrec + 1;
                    a as u64
                }
            } else {
                if pbump + (w as usize) > MEM {
                    SENT
                } else {
                    fill(&mut mem, pbump, key, w);
                    arr_set_unchecked(&mut roff, nrec, pbump as u8);
                    arr_set_unchecked(&mut rlen, nrec, w);
                    arr_set_unchecked(&mut rshd, nrec, 0);
                    pbump = pbump + w as usize;
                    nrec = nrec + 1;
                    a as u64
                }
            }
        } else if c % 4 == 2 {
            if nrec == 0 {
                SENT
            } else {
                let t: usize = (a as usize) % nrec;
                proof {
                    lemma_rec_in_pool(st_in, t as int);
                }
                // THE SAFETY LINE. c/kernel.c omits this whole block.
                //
                // ⚠ Nothing about this `if` is forced by the proof system for
                // MEMORY safety: both arms type-check without it and
                // `roff[t] as usize` is in range either way. What fails without
                // it is the POSTCONDITION -- the loop stops computing `run`.
                // ⚠⚠ What IS forced is the `requires` on `copy_bytes`, which is
                // a DISJOINTNESS obligation and is discharged out of `wf_prov`.
                // See the module note and ../NOTES.md 6b.
                if arr_get_unchecked(&rshd, t) == 1 {
                    let rl: u8 = arr_get_unchecked(&rlen, t);
                    if pbump + (rl as usize) > MEM {
                        SENT
                    } else {
                        let ro: u8 = arr_get_unchecked(&roff, t);
                        copy_bytes(&mut mem, pbump, ro as usize, rl);
                        arr_set_unchecked(&mut roff, t, pbump as u8);
                        arr_set_unchecked(&mut rshd, t, 0);
                        arr_set_unchecked(&mut mem, pbump, 0);
                        pbump = pbump + rl as usize;
                        2
                    }
                } else {
                    let ro: u8 = arr_get_unchecked(&roff, t);
                    arr_set_unchecked(&mut mem, ro as usize, 0);
                    2
                }
            }
        } else {
            if nrec == 0 {
                SENT
            } else {
                let t: usize = (a as usize) % nrec;
                proof {
                    lemma_rec_in_pool(st_in, t as int);
                }
                let ro: u8 = arr_get_unchecked(&roff, t);
                let rl: u8 = arr_get_unchecked(&rlen, t);
                fold_bytes(&mem, ro as usize, rl, 0)
            }
        };
        acc = acc.wrapping_mul(31).wrapping_add(v);
        proof {
            let st_out = St {
                mem: mem@,
                ekey: ekey@,
                elen: elen@,
                eoff: eoff@,
                roff: roff@,
                rlen: rlen@,
                rshd: rshd@,
                nent: nent as int,
                nrec: nrec as int,
                abump: abump as int,
                pbump: pbump as int,
            };
            assert(st_out =~= step(st_in, c, a).0);
            assert(v == step(st_in, c, a).1);
            assert(run(buf@, off as int, len as int, o_in, nops as int, p_in, st_in, acc_in)
                == run(
                buf@,
                off as int,
                len as int,
                o_in + 1,
                nops as int,
                p_in + 2,
                st_out,
                acc,
            ));
        }
        o = o + 1;
    }
    // The epilogue: fold every record's content and its ownership flag.
    let ghost st_end = St {
        mem: mem@,
        ekey: ekey@,
        elen: elen@,
        eoff: eoff@,
        roff: roff@,
        rlen: rlen@,
        rshd: rshd@,
        nent: nent as int,
        nrec: nrec as int,
        abump: abump as int,
        pbump: pbump as int,
    };
    let mut t: usize = 0;
    let ghost acc0 = acc;
    while t < nrec
        invariant
            t <= nrec,
            nrec <= NREC,
            st_end.nrec == nrec as int,
            st_end.mem == mem@,
            st_end.roff == roff@,
            st_end.rlen == rlen@,
            st_end.rshd == rshd@,
            wf(st_end),
            fold_recs(st_end, t as int, acc) == fold_recs(st_end, 0, acc0),
        decreases nrec - t,
    {
        proof {
            lemma_rec_in_pool(st_end, t as int);
        }
        let ro: u8 = arr_get_unchecked(&roff, t);
        let rl: u8 = arr_get_unchecked(&rlen, t);
        acc = fold_bytes(&mem, ro as usize, rl, acc);
        acc = acc.wrapping_mul(31).wrapping_add(arr_get_unchecked(&rshd, t) as u64);
        t = t + 1;
    }
    acc.wrapping_mul(31).wrapping_add(nrec as u64)
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
            assert(r == intern_fold(buf@, (k * stride) as int, stride as int));
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    emit(acc);
}

} // verus!
