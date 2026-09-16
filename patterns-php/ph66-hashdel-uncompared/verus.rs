//! ph66 rung R5 -- `unsafe.rs`'s exec code with a Verus proof.
//!
//! ============================================================================
//! ⭐⭐⭐ WHAT IS PROVED HERE, AND WHAT IT DOES *NOT* BUY
//! ============================================================================
//! `kernel` returns `hash_fold(buf@, off, len)` -- the fold the whole ladder
//! computes -- and every one of the ten trusted accessors' index preconditions
//! is discharged from `wf`.
//!
//! `wf` is the structural invariant this row's REPRESENTATION has and C's does
//! not: every link is `NIL` or an in-range arena index, a bucket chain's `pNext`
//! strictly DESCENDS (`CONNECT_TO_BUCKET_DLLIST` prepends at the head) and the
//! global list's `pListNext` strictly ASCENDS (`CONNECT_TO_GLOBAL_DLLIST`
//! appends at the tail). ⭐ Those two orderings are what give both walks a
//! `decreases` clause; `zend_hash.c` has no analogue of either, which is why
//! its walks have no termination measure.
//!
//! ⛔⛔⛔ **AND `wf` HOLDS WITH THE DEFECT IN PLACE. THAT IS THE ROW'S RESULT,
//! NOT A GAP IN THE PROOF.** `zend_hash.c:464`'s disjunct is a WRONG BOOLEAN,
//! not a memory error: it picks a bucket that is perfectly in range, unlinks it
//! correctly, and frees it correctly. No safety property excludes it. What
//! excludes it is a VALUE property -- the corpus's own labeller wrote it as
//! `NEW:container-key-identity`, *"a hash-table operation acts on the bucket
//! whose key equals the requested key in both key kind and key bytes, and on no
//! other bucket"* -- and `../controls/key_identity.py` builds exactly that
//! obligation in Verus, twice: it VERIFIES against the hardened predicate and
//! FAILS against the shipped one. ../NOTES.md sections 6 and 7 carry both.
//!
//! ⚠ So `r == hash_fold(...)` is a proof that this rung computes the SAME
//! WRONG ANSWER as `c/kernel.c`, exactly. That is what every rung below R1h
//! does on this row, and it is the finding (`CLAUDE.md` Don't 6).

use vstd::prelude::*;

// Plain-Rust I/O helpers. Outside `verus!`, so Verus treats the whole module as
// external and the two `external_body` wrappers below are the only way in.
#[path = "../../common/driver.rs"]
mod driver;

verus! {

// `group_slice_axioms` gives `slice@.len() == spec_slice_len(slice)`, hence
// `slice@.len() <= usize::MAX`, without which `off + len` cannot be shown not to
// overflow. `lemma_u128_shr_is_div` turns `x >> 64` into `x / 2^64` for the
// driver's multiply-shift barrier bound.
broadcast use {
    vstd::slice::group_slice_axioms,
    vstd::bits::lemma_u128_shr_is_div,
    vstd::arithmetic::mul::lemma_mul_inequality,
};

pub const REC: usize = 4;
pub const NKEY: u32 = 64;
/// `sizeof(Bucket) - 1` on LP64, asserted at compile time in `../c/kernel.c`.
pub const BUCKET_BASE: usize = 71;
/// `zend_alloc.h:63-64`.
pub const MCM: usize = 11;
pub const MCE: u32 = 256;
pub const NIL: u32 = 0xFFFF_FFFF;

/// `Bucket` -- zend_hash.h:48-58. `k` is `arKey` packed little-endian into one
/// word, zero-filled past `nKeyLength`.
pub struct Node {
    pub h: u64,
    pub nkl: u32,
    pub k: u64,
    pub data: u64,
    pub nxt: u32,
    pub lst: u32,
    pub lnxt: u32,
    pub llst: u32,
}

// ---------------------------------------------------------------- spec ------
/// `_emalloc`'s `REAL_SIZE(size)` -- zend_alloc.c:132, `(size + 7) & ~7`.
pub open spec fn real_of(size: usize) -> usize {
    ((size + 7) as usize) & !(7usize)
}

/// `cache_index = real_size >> 3` -- zend_alloc.c:136.
pub open spec fn idx_of(size: usize) -> usize {
    real_of(size) >> 3
}

/// Byte `i` of a packed key -- what `p->arKey[i]` reads.
pub open spec fn s_kbyte(k: u64, i: nat) -> u64 {
    (k >> ((8 * i) as u64)) & 0xFF
}

/// `zend_inline_hash_func` over the first `n` bytes -- zend_hash.h:243-271.
pub open spec fn s_hash(k: u64, n: nat) -> u64
    decreases n,
{
    if n == 0 {
        5381u64
    } else {
        s_hash(k, (n - 1) as nat).wrapping_mul(33).wrapping_add(s_kbyte(k, (n - 1) as nat))
    }
}

pub open spec fn s_kl(sel: u32) -> nat {
    (1 + (sel % 7)) as nat
}

pub open spec fn s_keyw(sel: u32, i: nat) -> u64
    decreases i,
{
    if i == 0 {
        0u64
    } else {
        s_keyw(sel, (i - 1) as nat) | (((97 + (((sel / 7) * 5 + ((i - 1) as u32) * 7) % 26))
            as u64) << ((8 * (i - 1)) as u64))
    }
}

pub open spec fn s_key(sel: u32) -> u64 {
    s_keyw(sel, s_kl(sel))
}

/// `nKeyLength` INCLUDES the NUL -- `Zend/zend_execute.c:3612`.
pub open spec fn s_nkl(sel: u32) -> u32 {
    (s_kl(sel) + 1) as u32
}

/// `_zend_hash_init`'s `while ((1U << i) < nSize) i++;` from `i = 3`.
pub open spec fn s_ts_from(nrec: nat, cur: nat) -> nat
    decreases if cur >= nrec {
        0nat
    } else {
        (nrec - cur) as nat
    },
{
    if cur >= nrec || cur == 0 {
        cur
    } else {
        s_ts_from(nrec, 2 * cur)
    }
}

pub open spec fn s_ts(nrec: nat) -> nat {
    s_ts_from(nrec, 8)
}

/// The kernel's whole observable state: `HashTable` (zend_hash.h:60-78), the
/// bucket arena, `zend_alloc.c`'s per-class cache depth, the four tally fields
/// and the projected `ZVAL_PTR_DTOR` counters.
pub struct G {
    pub nodes: Seq<Node>,
    pub ar: Seq<u32>,
    pub mask: u64,
    pub lhead: u32,
    pub ltail: u32,
    pub iptr: u32,
    pub nelem: u64,
    pub nnext: u64,
    pub ndtor: u64,
    pub dfold: u64,
    pub ndok: u64,
    pub ndfail: u64,
    pub cnt: Seq<u32>,
    pub na: u64,
    pub nf: u64,
    pub nh: u64,
    pub ab: u64,
}

/// ⭐ THE ROW'S SAFETY INVARIANT, PER NODE. The bucket chain DESCENDS and the
/// global list ASCENDS, because one macro prepends and the other appends.
pub open spec fn node_ok(a: Seq<Node>, i: int) -> bool {
    &&& a[i].nkl <= 8
    &&& (a[i].nxt == NIL || ((a[i].nxt as int) < i))
    &&& (a[i].lst == NIL || ((a[i].lst as int) > i && (a[i].lst as int) < a.len()))
    &&& (a[i].lnxt == NIL || ((a[i].lnxt as int) > i && (a[i].lnxt as int) < a.len()))
    &&& (a[i].llst == NIL || ((a[i].llst as int) < i))
}

pub open spec fn wf(g: G) -> bool {
    &&& g.cnt.len() == MCM as int
    &&& g.ar.len() == g.mask as int + 1
    &&& g.mask < 0x1000_0000
    &&& g.nodes.len() < 0x4000_0000
    &&& (g.lhead == NIL || (g.lhead as int) < g.nodes.len())
    &&& (g.ltail == NIL || (g.ltail as int) < g.nodes.len())
    &&& (g.iptr == NIL || (g.iptr as int) < g.nodes.len())
    &&& forall|j: int|
        0 <= j < g.ar.len() ==> (#[trigger] g.ar[j]) == NIL || (g.ar[j] as int) < g.nodes.len()
    &&& forall|i: int| 0 <= i < g.nodes.len() ==> #[trigger] node_ok(g.nodes, i)
}

pub open spec fn s_alloc(g: G, size: usize) -> G {
    let idx = idx_of(size);
    let g1 = G { na: g.na.wrapping_add(1), ..g };
    if idx < MCM && g1.cnt[idx as int] > 0 {
        G {
            cnt: g1.cnt.update(idx as int, (g1.cnt[idx as int] - 1) as u32),
            nh: g1.nh.wrapping_add(1),
            ..g1
        }
    } else {
        G { ab: g1.ab.wrapping_add(real_of(size) as u64), ..g1 }
    }
}

pub open spec fn s_free(g: G, size: usize) -> G {
    let idx = idx_of(size);
    let g1 = G { nf: g.nf.wrapping_add(1), ..g };
    if idx < MCM && g1.cnt[idx as int] < MCE {
        G { cnt: g1.cnt.update(idx as int, (g1.cnt[idx as int] + 1) as u32), ..g1 }
    } else {
        g1
    }
}

/// `ZVAL_PTR_DTOR` -> `_zval_ptr_dtor`, projected to a count and a fold.
pub open spec fn s_dtor(g: G, v: u64) -> G {
    G {
        ndtor: g.ndtor.wrapping_add(1),
        dfold: g.dfold.wrapping_mul(31).wrapping_add(v & 0xFFFF),
        ..g
    }
}

/// `CONNECT_TO_BUCKET_DLLIST` then `CONNECT_TO_GLOBAL_DLLIST` then
/// `ht->arBuckets[nIndex] = p` -- zend_hash.c:24-42, in the C's own order.
pub open spec fn s_connect(g: G, i: u32, ni: int) -> G {
    let head = g.ar[ni];
    let tail = g.ltail;
    let a0 = g.nodes.update(
        i as int,
        Node { nxt: head, lst: NIL, llst: tail, lnxt: NIL, ..g.nodes[i as int] },
    );
    let a1 = if head != NIL {
        a0.update(head as int, Node { lst: i, ..a0[head as int] })
    } else {
        a0
    };
    let a2 = if tail != NIL {
        a1.update(tail as int, Node { lnxt: i, ..a1[tail as int] })
    } else {
        a1
    };
    G {
        nodes: a2,
        ar: g.ar.update(ni, i),
        ltail: i,
        lhead: if g.lhead == NIL {
            i
        } else {
            g.lhead
        },
        iptr: if g.iptr == NIL {
            i
        } else {
            g.iptr
        },
        nelem: g.nelem.wrapping_add(1),
        ..g
    }
}

/// `_zend_hash_add_or_update`'s chain walk -- zend_hash.c:213-225. ⭐ Its
/// predicate is the REPAIR'S OWN FORM already: two required conjuncts.
pub open spec fn s_find_str(a: Seq<Node>, p: u32, h: u64, nkl: u32, k: u64, fuel: nat) -> u32
    decreases fuel,
{
    if fuel == 0 || p == NIL || p as int >= a.len() {
        NIL
    } else if a[p as int].h == h && a[p as int].nkl == nkl && a[p as int].k == k {
        p
    } else {
        s_find_str(a, a[p as int].nxt, h, nkl, k, (fuel - 1) as nat)
    }
}

/// `_zend_hash_index_update_or_next_insert`'s chain walk -- zend_hash.c:354-380.
pub open spec fn s_find_idx(a: Seq<Node>, p: u32, h: u64, fuel: nat) -> u32
    decreases fuel,
{
    if fuel == 0 || p == NIL || p as int >= a.len() {
        NIL
    } else if a[p as int].nkl == 0 && a[p as int].h == h {
        p
    } else {
        s_find_idx(a, a[p as int].nxt, h, (fuel - 1) as nat)
    }
}

/// ⛔⛔⛔ THE DEFECT, AS A SPEC FUNCTION. `zend_hash_del_key_or_index`'s chain
/// walk, `zend_hash.c:463-465`: `a[p].nkl == 0` is a DISJUNCT, so a NUMERIC
/// bucket matches on hash equality alone and its key is never compared.
pub open spec fn s_find_del(a: Seq<Node>, p: u32, h: u64, nkl: u32, k: u64, fuel: nat) -> u32
    decreases fuel,
{
    if fuel == 0 || p == NIL || p as int >= a.len() {
        NIL
    } else if a[p as int].h == h && (a[p as int].nkl == 0 || (a[p as int].nkl == nkl && a[p
        as int].k == k)) {
        p
    } else {
        s_find_del(a, a[p as int].nxt, h, nkl, k, (fuel - 1) as nat)
    }
}

pub open spec fn s_ins_str(g: G, key: u64, nkl: u32, data: u64) -> G {
    let h = s_hash(key, nkl as nat);
    let ni = (h & g.mask) as int;
    let p = s_find_str(g.nodes, g.ar[ni], h, nkl, key, g.nodes.len());
    if p != NIL {
        let g1 = s_dtor(g, g.nodes[p as int].data);
        G { nodes: g1.nodes.update(p as int, Node { data: data, ..g1.nodes[p as int] }), ..g1 }
    } else {
        let g1 = s_alloc(g, (BUCKET_BASE + nkl as usize) as usize);
        let g2 = G {
            nodes: g1.nodes.push(
                Node { h: h, nkl: nkl, k: key, data: data, nxt: NIL, lst: NIL, lnxt: NIL, llst: NIL },
            ),
            ..g1
        };
        s_connect(g2, g1.nodes.len() as u32, ni)
    }
}

pub open spec fn s_ins_idx(g: G, h: u64, data: u64) -> G {
    let ni = (h & g.mask) as int;
    let p = s_find_idx(g.nodes, g.ar[ni], h, g.nodes.len());
    let g2 = if p != NIL {
        let g1 = s_dtor(g, g.nodes[p as int].data);
        G { nodes: g1.nodes.update(p as int, Node { data: data, ..g1.nodes[p as int] }), ..g1 }
    } else {
        let g1 = s_alloc(g, BUCKET_BASE);
        let ga = G {
            nodes: g1.nodes.push(
                Node { h: h, nkl: 0, k: 0, data: data, nxt: NIL, lst: NIL, lnxt: NIL, llst: NIL },
            ),
            ..g1
        };
        s_connect(ga, g1.nodes.len() as u32, ni)
    };
    if (h as i64) >= (g2.nnext as i64) {
        G { nnext: h.wrapping_add(1), ..g2 }
    } else {
        g2
    }
}

/// `zend_hash_del_key_or_index` -- zend_hash.c:450-503. ⚠⚠⚠ THE PRIMARY SPAN.
pub open spec fn s_del(g: G, key: u64, nkl: u32, h0: u64, del_key: bool) -> G {
    let h = if del_key {
        s_hash(key, nkl as nat)
    } else {
        h0
    };
    let ni = (h & g.mask) as int;
    let p = s_find_del(g.nodes, g.ar[ni], h, nkl, key, g.nodes.len());
    if p == NIL {
        G { ndfail: g.ndfail.wrapping_add(1), ..g }
    } else {
        let nd = g.nodes[p as int];
        let ar1 = if g.ar[ni] == p {
            g.ar.update(ni, nd.nxt)
        } else {
            g.ar
        };
        let a1 = if g.ar[ni] != p && nd.lst != NIL {
            g.nodes.update(nd.lst as int, Node { nxt: nd.nxt, ..g.nodes[nd.lst as int] })
        } else {
            g.nodes
        };
        let a2 = if nd.nxt != NIL {
            a1.update(nd.nxt as int, Node { lst: nd.lst, ..a1[nd.nxt as int] })
        } else {
            a1
        };
        let a3 = if nd.llst != NIL {
            a2.update(nd.llst as int, Node { lnxt: nd.lnxt, ..a2[nd.llst as int] })
        } else {
            a2
        };
        let lh = if nd.llst != NIL {
            g.lhead
        } else {
            nd.lnxt
        };
        let a4 = if nd.lnxt != NIL {
            a3.update(nd.lnxt as int, Node { llst: nd.llst, ..a3[nd.lnxt as int] })
        } else {
            a3
        };
        let lt = if nd.lnxt != NIL {
            g.ltail
        } else {
            nd.llst
        };
        let ip = if g.iptr == p {
            nd.lnxt
        } else {
            g.iptr
        };
        let g1 = G { nodes: a4, ar: ar1, lhead: lh, ltail: lt, iptr: ip, ..g };
        let g2 = s_dtor(g1, nd.data);
        let g3 = s_free(g2, (BUCKET_BASE + nd.nkl as usize) as usize);
        G { nelem: g3.nelem.wrapping_sub(1), ndok: g3.ndok.wrapping_add(1), ..g3 }
    }
}

/// The key half of the surviving-bucket fold: bytes 0..n of the packed key.
pub open spec fn s_foldk(k: u64, n: nat, acc: u64) -> u64
    decreases n,
{
    if n == 0 {
        acc
    } else {
        s_foldk(k, (n - 1) as nat, acc).wrapping_mul(31).wrapping_add(s_kbyte(k, (n - 1) as nat))
    }
}

/// The fold over the SURVIVING keys, in the global list's own order.
pub open spec fn s_fold(g: G, p: u32, acc: u64, fuel: nat) -> u64
    decreases fuel,
{
    if fuel == 0 || p == NIL || p as int >= g.nodes.len() {
        acc
    } else {
        let n = g.nodes[p as int];
        let a1 = acc.wrapping_mul(31).wrapping_add(n.nkl as u64);
        let a2 = a1.wrapping_mul(31).wrapping_add(n.h);
        let a3 = s_foldk(n.k, n.nkl as nat, a2);
        let a4 = a3.wrapping_mul(31).wrapping_add(n.data & 0xFFFF);
        s_fold(g, n.lnxt, a4, (fuel - 1) as nat)
    }
}

pub open spec fn s_tail(g: G) -> u64 {
    let a0 = s_fold(g, g.lhead, 0, g.nodes.len());
    let a1 = a0.wrapping_mul(31).wrapping_add(g.nelem);
    let a2 = a1.wrapping_mul(31).wrapping_add(g.nnext);
    let a3 = a2.wrapping_mul(31).wrapping_add(g.ndtor);
    let a4 = a3.wrapping_mul(31).wrapping_add(g.dfold);
    let a5 = a4.wrapping_mul(31).wrapping_add(g.ndok);
    let a6 = a5.wrapping_mul(31).wrapping_add(g.ndfail);
    a6 ^ (g.na.wrapping_mul(1000003) ^ g.nf.wrapping_mul(1000033) ^ g.nh.wrapping_mul(1000037)
        ^ g.ab.wrapping_mul(1000039))
}

pub open spec fn s_step(g: G, ctl: u32, b1: u32, val: u64) -> G {
    let sel = b1 & (NKEY - 1) as u32;
    let key = s_key(sel);
    let nkl = s_nkl(sel);
    let data = 0x10000u64 | val;
    let op = ctl & 1;
    let kind = (ctl >> 1u32) & 1;
    let coll = (ctl >> 2u32) & 1;
    if op == 0 {
        if kind == 0 {
            s_ins_str(g, key, nkl, data)
        } else {
            s_ins_idx(
                g,
                if coll == 1 {
                    s_hash(key, nkl as nat)
                } else {
                    b1 as u64
                },
                data,
            )
        }
    } else if kind == 0 {
        s_del(g, key, nkl, 0, true)
    } else {
        s_del(
            g,
            key,
            0,
            if coll == 1 {
                s_hash(key, nkl as nat)
            } else {
                b1 as u64
            },
            false,
        )
    }
}

pub open spec fn s_run(win: Seq<u8>, r: nat, nrec: nat, g: G) -> G
    decreases nrec - r,
{
    if r >= nrec {
        g
    } else {
        let ctl = win[(r * 4) as int] as u32;
        let b1 = win[(r * 4 + 1) as int] as u32;
        let val = (win[(r * 4 + 2) as int] as u64) | ((win[(r * 4 + 3) as int] as u64) << 8u64);
        s_run(win, (r + 1) as nat, nrec, s_step(g, ctl, b1, val))
    }
}

pub open spec fn g_init(ts: nat) -> G {
    G {
        nodes: Seq::empty(),
        ar: Seq::new(ts, |i: int| NIL),
        mask: (ts - 1) as u64,
        lhead: NIL,
        ltail: NIL,
        iptr: NIL,
        nelem: 0,
        nnext: 0,
        ndtor: 0,
        dfold: 0,
        ndok: 0,
        ndfail: 0,
        cnt: Seq::new(MCM as nat, |i: int| 0u32),
        na: 0,
        nf: 0,
        nh: 0,
        ab: 0,
    }
}

/// What the kernel must return. ⚠ `../model.py::Model.hash_fold` is an
/// INDEPENDENT transcription of this and the gate evaluates the derived
/// `ensures` against it.
pub open spec fn hash_fold(buf: Seq<u8>, off: int, len: int) -> u64 {
    let win = buf.subrange(off, off + len);
    let nrec = (len / 4) as nat;
    let ts = s_ts(nrec);
    s_tail(s_run(win, 0, nrec, s_alloc(g_init(ts), (8 * ts) as usize)))
}

/// `x & m <= m` -- the one bit fact the whole bucket-index bound rests on. It
/// needs NO power-of-two hypothesis, which is why `wf` carries only
/// `ar.len() == mask + 1`.
pub proof fn lemma_mask_le(h: u64, m: u64)
    ensures
        (h & m) <= m,
{
    assert((h & m) <= m) by (bit_vector);
}

// ------------------------------------------------------ TRUSTED ITEMS ------
// Ten of them, every one an arena or window access whose only precondition is
// an INDEX BOUND that `wf` discharges. Each carries a verified twin.

// -------------------------------------------------------- TRUSTED, 1/10 ----
#[verifier::external_body]
#[inline(always)]
fn nref(v: &Vec<Node>, i: u32) -> (r: &Node)
    requires
        (i as int) < v@.len(),
    ensures
        *r == v@[i as int],
{
    unsafe { v.get_unchecked(i as usize) }
}

#[cfg(slb_twin)]
#[inline(always)]
fn slb_twin_nref(v: &Vec<Node>, i: u32) -> (r: &Node)
    requires
        (i as int) < v@.len(),
    ensures
        *r == v@[i as int],
{
    &v[i as usize]
}

// -------------------------------------------------------- TRUSTED, 2/10 ----
#[verifier::external_body]
#[inline(always)]
fn set_nxt(v: &mut Vec<Node>, i: u32, x: u32)
    requires
        (i as int) < old(v)@.len(),
    ensures
        final(v)@ == old(v)@.update(i as int, Node { nxt: x, ..old(v)@[i as int] }),
{
    unsafe {
        v.get_unchecked_mut(i as usize).nxt = x;
    }
}

#[cfg(slb_twin)]
#[inline(always)]
fn slb_twin_set_nxt(v: &mut Vec<Node>, i: u32, x: u32)
    requires
        (i as int) < old(v)@.len(),
    ensures
        final(v)@ == old(v)@.update(i as int, Node { nxt: x, ..old(v)@[i as int] }),
{
    let n = Node { nxt: x, ..*(&v[i as usize]) };
    v.set(i as usize, n);
}

// -------------------------------------------------------- TRUSTED, 3/10 ----
#[verifier::external_body]
#[inline(always)]
fn set_lst(v: &mut Vec<Node>, i: u32, x: u32)
    requires
        (i as int) < old(v)@.len(),
    ensures
        final(v)@ == old(v)@.update(i as int, Node { lst: x, ..old(v)@[i as int] }),
{
    unsafe {
        v.get_unchecked_mut(i as usize).lst = x;
    }
}

#[cfg(slb_twin)]
#[inline(always)]
fn slb_twin_set_lst(v: &mut Vec<Node>, i: u32, x: u32)
    requires
        (i as int) < old(v)@.len(),
    ensures
        final(v)@ == old(v)@.update(i as int, Node { lst: x, ..old(v)@[i as int] }),
{
    let n = Node { lst: x, ..*(&v[i as usize]) };
    v.set(i as usize, n);
}

// -------------------------------------------------------- TRUSTED, 4/10 ----
#[verifier::external_body]
#[inline(always)]
fn set_lnxt(v: &mut Vec<Node>, i: u32, x: u32)
    requires
        (i as int) < old(v)@.len(),
    ensures
        final(v)@ == old(v)@.update(i as int, Node { lnxt: x, ..old(v)@[i as int] }),
{
    unsafe {
        v.get_unchecked_mut(i as usize).lnxt = x;
    }
}

#[cfg(slb_twin)]
#[inline(always)]
fn slb_twin_set_lnxt(v: &mut Vec<Node>, i: u32, x: u32)
    requires
        (i as int) < old(v)@.len(),
    ensures
        final(v)@ == old(v)@.update(i as int, Node { lnxt: x, ..old(v)@[i as int] }),
{
    let n = Node { lnxt: x, ..*(&v[i as usize]) };
    v.set(i as usize, n);
}

// -------------------------------------------------------- TRUSTED, 5/10 ----
#[verifier::external_body]
#[inline(always)]
fn set_llst(v: &mut Vec<Node>, i: u32, x: u32)
    requires
        (i as int) < old(v)@.len(),
    ensures
        final(v)@ == old(v)@.update(i as int, Node { llst: x, ..old(v)@[i as int] }),
{
    unsafe {
        v.get_unchecked_mut(i as usize).llst = x;
    }
}

#[cfg(slb_twin)]
#[inline(always)]
fn slb_twin_set_llst(v: &mut Vec<Node>, i: u32, x: u32)
    requires
        (i as int) < old(v)@.len(),
    ensures
        final(v)@ == old(v)@.update(i as int, Node { llst: x, ..old(v)@[i as int] }),
{
    let n = Node { llst: x, ..*(&v[i as usize]) };
    v.set(i as usize, n);
}

// -------------------------------------------------------- TRUSTED, 6/10 ----
#[verifier::external_body]
#[inline(always)]
fn set_data(v: &mut Vec<Node>, i: u32, x: u64)
    requires
        (i as int) < old(v)@.len(),
    ensures
        final(v)@ == old(v)@.update(i as int, Node { data: x, ..old(v)@[i as int] }),
{
    unsafe {
        v.get_unchecked_mut(i as usize).data = x;
    }
}

#[cfg(slb_twin)]
#[inline(always)]
fn slb_twin_set_data(v: &mut Vec<Node>, i: u32, x: u64)
    requires
        (i as int) < old(v)@.len(),
    ensures
        final(v)@ == old(v)@.update(i as int, Node { data: x, ..old(v)@[i as int] }),
{
    let n = Node { data: x, ..*(&v[i as usize]) };
    v.set(i as usize, n);
}

// -------------------------------------------------------- TRUSTED, 7/10 ----
#[verifier::external_body]
#[inline(always)]
fn aget(v: &Vec<u32>, i: usize) -> (r: u32)
    requires
        (i as int) < v@.len(),
    ensures
        r == v@[i as int],
{
    unsafe { *v.get_unchecked(i) }
}

#[cfg(slb_twin)]
#[inline(always)]
fn slb_twin_aget(v: &Vec<u32>, i: usize) -> (r: u32)
    requires
        (i as int) < v@.len(),
    ensures
        r == v@[i as int],
{
    v[i]
}

// -------------------------------------------------------- TRUSTED, 8/10 ----
#[verifier::external_body]
#[inline(always)]
fn aset(v: &mut Vec<u32>, i: usize, x: u32)
    requires
        (i as int) < old(v)@.len(),
    ensures
        final(v)@ == old(v)@.update(i as int, x),
{
    unsafe {
        *v.get_unchecked_mut(i) = x;
    }
}

#[cfg(slb_twin)]
#[inline(always)]
fn slb_twin_aset(v: &mut Vec<u32>, i: usize, x: u32)
    requires
        (i as int) < old(v)@.len(),
    ensures
        final(v)@ == old(v)@.update(i as int, x),
{
    v.set(i, x);
}

// -------------------------------------------------------- TRUSTED, 9/10 ----
#[verifier::external_body]
#[inline(always)]
fn wsub(v: &[u8], o: usize, n: usize) -> (r: &[u8])
    requires
        o + n <= v@.len(),
    ensures
        r@ == v@.subrange(o as int, (o + n) as int),
{
    unsafe { v.get_unchecked(o..o + n) }
}

#[cfg(slb_twin)]
#[inline(always)]
fn slb_twin_wsub(v: &[u8], o: usize, n: usize) -> (r: &[u8])
    requires
        o + n <= v@.len(),
    ensures
        r@ == v@.subrange(o as int, (o + n) as int),
{
    // `o + n <= v@.len()` alone does not stop `o + n` overflowing a `usize`:
    // the broadcast group is what says a slice's length IS a `usize`.
    assert(v@.len() == vstd::slice::spec_slice_len(v));
    vstd::slice::slice_subrange(v, o, o + n)
}

// ------------------------------------------------------- TRUSTED, 10/10 ----
#[verifier::external_body]
#[inline(always)]
fn wb(v: &[u8], i: usize) -> (r: u8)
    requires
        (i as int) < v@.len(),
    ensures
        r == v@[i as int],
{
    unsafe { *v.get_unchecked(i) }
}

#[cfg(slb_twin)]
#[inline(always)]
fn slb_twin_wb(v: &[u8], i: usize) -> (r: u8)
    requires
        (i as int) < v@.len(),
    ensures
        r == v@[i as int],
{
    v[i]
}

// ----------------------------------------------- untrusted I/O boundary ----
// Argument parsing, file I/O and little-endian decoding. It states **no**
// `ensures` at all, deliberately: an `ensures` here would be an axiom about the
// contents of a file.
#[verifier::external_body]
fn load_input() -> (r: (u64, u64, Vec<u8>)) {
    let path = driver::arg_path();
    let inp = driver::load(&path);
    let (stride_w, bytes) = driver::head1_u64_bytes(&inp);
    (inp.n_iters, stride_w, bytes)
}

#[verifier::external_body]
fn emit(acc: u64) {
    driver::emit(acc);
}

// ---------------------------------------------------------------- exec ------
pub struct Ht {
    pub a: Vec<Node>,
    pub ar: Vec<u32>,
    pub mask: u64,
    pub lhead: u32,
    pub ltail: u32,
    pub iptr: u32,
    pub nelem: u64,
    pub nnext: u64,
    pub ndtor: u64,
    pub dfold: u64,
    pub ndok: u64,
    pub ndfail: u64,
    pub cnt: Vec<u32>,
    pub na: u64,
    pub nf: u64,
    pub nh: u64,
    pub ab: u64,
}

impl Ht {
    pub open spec fn g(&self) -> G {
        G {
            nodes: self.a@,
            ar: self.ar@,
            mask: self.mask,
            lhead: self.lhead,
            ltail: self.ltail,
            iptr: self.iptr,
            nelem: self.nelem,
            nnext: self.nnext,
            ndtor: self.ndtor,
            dfold: self.dfold,
            ndok: self.ndok,
            ndfail: self.ndfail,
            cnt: self.cnt@,
            na: self.na,
            nf: self.nf,
            nh: self.nh,
            ab: self.ab,
        }
    }
}

/// `_zend_hash_init`'s table sizing.
fn table_size(nrec: usize) -> (r: usize)
    requires
        nrec <= 0x400_0000,
    ensures
        r as nat == s_ts(nrec as nat),
        8 <= r <= 0x800_0000,
        nrec <= r,
{
    let mut ts: usize = 8;
    while ts < nrec
        invariant
            8 <= ts <= 0x800_0000,
            nrec <= 0x400_0000,
            s_ts(nrec as nat) == s_ts_from(nrec as nat, ts as nat),
        decreases 0x800_0000int - ts as int,
    {
        ts = ts * 2;
    }
    ts
}

/// The `sel`-th string key, packed, and its `nKeyLength` (NUL INCLUDED).
fn key_of(sel: u32) -> (r: (u64, u32))
    requires
        sel < NKEY,
    ensures
        r.0 == s_key(sel),
        r.1 == s_nkl(sel),
        r.1 >= 2,
        r.1 <= 8,
{
    let kl: usize = 1 + (sel % 7) as usize;
    let mut k: u64 = 0;
    let mut i: usize = 0;
    while i < kl
        invariant
            i <= kl,
            kl == s_kl(sel),
            kl <= 7,
            k == s_keyw(sel, i as nat),
            sel < NKEY,
        decreases kl - i,
    {
        let c: u64 = (97u32 + (((sel / 7) * 5 + (i as u32) * 7) % 26)) as u64;
        k = k | (c << ((8 * i) as u64));
        i = i + 1;
    }
    (k, (kl + 1) as u32)
}

/// Byte `i` of a packed key -- what `p->arKey[i]` reads.
#[inline(always)]
fn kbyte(k: u64, i: usize) -> (r: u64)
    requires
        i < 8,
    ensures
        r == s_kbyte(k, i as nat),
{
    (k >> ((8 * i) as u64)) & 0xFF
}

/// `zend_inline_hash_func` -- zend_hash.h:243-271, rolled.
fn hash_of(k: u64, nkl: u32) -> (r: u64)
    requires
        nkl <= 8,
    ensures
        r == s_hash(k, nkl as nat),
{
    let mut h: u64 = 5381;
    let mut i: usize = 0;
    while i < nkl as usize
        invariant
            i <= nkl,
            nkl <= 8,
            h == s_hash(k, i as nat),
        decreases nkl as int - i as int,
    {
        h = h.wrapping_mul(33).wrapping_add(kbyte(k, i));
        i = i + 1;
    }
    h
}

impl Ht {
    /// `_emalloc` -- zend_alloc.c:142-217.
    fn alloc(&mut self, size: usize)
        requires
            old(self).cnt@.len() == MCM as int,
            size <= 0x4000_0000,
        ensures
            final(self).g() == s_alloc(old(self).g(), size),
            final(self).cnt@.len() == MCM as int,
    {
        let rsz: usize = (size + 7) & !7usize;
        let idx: usize = rsz >> 3;
        self.na = self.na.wrapping_add(1);
        let c: u32 = if idx < MCM {
            aget(&self.cnt, idx)
        } else {
            0
        };
        if idx < MCM && c > 0 {
            aset(&mut self.cnt, idx, c - 1);
            self.nh = self.nh.wrapping_add(1);
        } else {
            self.ab = self.ab.wrapping_add(rsz as u64);
        }
        assert(self.g().cnt =~= s_alloc(old(self).g(), size).cnt);
    }

    /// `_efree` -- zend_alloc.c:248-289.
    fn free(&mut self, size: usize)
        requires
            old(self).cnt@.len() == MCM as int,
            size <= 0x4000_0000,
        ensures
            final(self).g() == s_free(old(self).g(), size),
            final(self).cnt@.len() == MCM as int,
    {
        let rsz: usize = (size + 7) & !7usize;
        let idx: usize = rsz >> 3;
        self.nf = self.nf.wrapping_add(1);
        let c: u32 = if idx < MCM {
            aget(&self.cnt, idx)
        } else {
            0
        };
        if idx < MCM && c < MCE {
            aset(&mut self.cnt, idx, c + 1);
        }
        assert(self.g().cnt =~= s_free(old(self).g(), size).cnt);
    }

    /// `ZVAL_PTR_DTOR` -> `_zval_ptr_dtor`, projected to a count and a fold.
    fn dtor(&mut self, v: u64)
        ensures
            final(self).g() == s_dtor(old(self).g(), v),
    {
        self.ndtor = self.ndtor.wrapping_add(1);
        self.dfold = self.dfold.wrapping_mul(31).wrapping_add(v & 0xFFFF);
    }

    /// `CONNECT_TO_BUCKET_DLLIST` + `CONNECT_TO_GLOBAL_DLLIST` -- :24-42.
    fn connect(&mut self, i: u32, n_index: usize)
        requires
            wf(old(self).g()),
            (i as int) == old(self).a@.len() - 1,
            (n_index as int) < old(self).ar@.len(),
            old(self).lhead == NIL || (old(self).lhead as int) < i as int,
            old(self).ltail == NIL || (old(self).ltail as int) < i as int,
            old(self).iptr == NIL || (old(self).iptr as int) < i as int,
            forall|j: int|
                0 <= j < old(self).ar@.len() ==> (#[trigger] old(self).ar@[j]) == NIL || (
                old(self).ar@[j] as int) < i as int,
        ensures
            final(self).g() == s_connect(old(self).g(), i, n_index as int),
            wf(final(self).g()),
            final(self).a@.len() == old(self).a@.len(),
            final(self).cnt@.len() == MCM as int,
    {
        let ghost g0 = self.g();
        let head = aget(&self.ar, n_index);
        let tail = self.ltail;
        set_nxt(&mut self.a, i, head);
        set_lst(&mut self.a, i, NIL);
        set_llst(&mut self.a, i, tail);
        set_lnxt(&mut self.a, i, NIL);
        if head != NIL {
            set_lst(&mut self.a, head, i);
        }
        self.ltail = i;
        if tail != NIL {
            set_lnxt(&mut self.a, tail, i);
        }
        if self.lhead == NIL {
            self.lhead = i;
        }
        if self.iptr == NIL {
            self.iptr = i;
        }
        aset(&mut self.ar, n_index, i);
        self.nelem = self.nelem.wrapping_add(1);
        proof {
            let gs = s_connect(g0, i, n_index as int);
            assert(self.a@ =~= gs.nodes);
            assert(self.ar@ =~= gs.ar);
            assert(self.g() == gs);
            assert forall|q: int| 0 <= q < self.a@.len() implies #[trigger] node_ok(
                self.a@,
                q,
            ) by {
                assert(node_ok(g0.nodes, q));
                if q == i as int {
                } else if head != NIL && q == head as int {
                } else if tail != NIL && q == tail as int {
                } else {
                    assert(self.a@[q] == g0.nodes[q]);
                }
            }
            assert forall|j: int| 0 <= j < self.ar@.len() implies (#[trigger] self.ar@[j]) == NIL
                || (self.ar@[j] as int) < self.a@.len() by {
                assert(g0.ar[j] == NIL || (g0.ar[j] as int) < i as int);
            }
        }
    }

    /// `_zend_hash_add_or_update`'s chain walk -- zend_hash.c:213-225.
    fn find_str(&self, n_index: usize, h: u64, nkl: u32, key: u64) -> (r: u32)
        requires
            wf(self.g()),
            (n_index as int) < self.ar@.len(),
        ensures
            r == s_find_str(self.a@, self.ar@[n_index as int], h, nkl, key, self.a@.len()),
            r == NIL || (r as int) < self.a@.len(),
    {
        let ghost target = s_find_str(
            self.a@,
            self.ar@[n_index as int],
            h,
            nkl,
            key,
            self.a@.len(),
        );
        let mut p: u32 = aget(&self.ar, n_index);
        let mut res: u32 = NIL;
        let ghost mut fuel: nat = self.a@.len();
        while p != NIL
            invariant_except_break
                p == NIL || ((p as int) < self.a@.len() && fuel >= p as int + 1),
                target == s_find_str(self.a@, p, h, nkl, key, fuel),
                res == NIL,
            invariant
                wf(self.g()),
            ensures
                res == target,
                res == NIL || (res as int) < self.a@.len(),
            decreases if p == NIL {
                0int
            } else {
                p as int + 1
            },
        {
            let n = nref(&self.a, p);
            let (eq, nx) = (n.h == h && n.nkl == nkl && n.k == key, n.nxt);
            if eq {
                res = p;
                break;
            }
            assert(node_ok(self.a@, p as int));
            proof {
                fuel = (fuel - 1) as nat;
            }
            p = nx;
        }
        res
    }

    /// `_zend_hash_index_update_or_next_insert`'s chain walk -- :354-380.
    fn find_idx(&self, n_index: usize, h: u64) -> (r: u32)
        requires
            wf(self.g()),
            (n_index as int) < self.ar@.len(),
        ensures
            r == s_find_idx(self.a@, self.ar@[n_index as int], h, self.a@.len()),
            r == NIL || (r as int) < self.a@.len(),
    {
        let ghost target = s_find_idx(self.a@, self.ar@[n_index as int], h, self.a@.len());
        let mut p: u32 = aget(&self.ar, n_index);
        let mut res: u32 = NIL;
        let ghost mut fuel: nat = self.a@.len();
        while p != NIL
            invariant_except_break
                p == NIL || ((p as int) < self.a@.len() && fuel >= p as int + 1),
                target == s_find_idx(self.a@, p, h, fuel),
                res == NIL,
            invariant
                wf(self.g()),
            ensures
                res == target,
                res == NIL || (res as int) < self.a@.len(),
            decreases if p == NIL {
                0int
            } else {
                p as int + 1
            },
        {
            let n = nref(&self.a, p);
            let (eq, nx) = (n.nkl == 0 && n.h == h, n.nxt);
            if eq {
                res = p;
                break;
            }
            assert(node_ok(self.a@, p as int));
            proof {
                fuel = (fuel - 1) as nat;
            }
            p = nx;
        }
        res
    }

    /// ⛔⛔⛔ THE DEFECT'S OWN WALK. `zend_hash_del_key_or_index`, :463-465.
    fn find_del(&self, n_index: usize, h: u64, nkl: u32, key: u64) -> (r: u32)
        requires
            wf(self.g()),
            (n_index as int) < self.ar@.len(),
        ensures
            r == s_find_del(self.a@, self.ar@[n_index as int], h, nkl, key, self.a@.len()),
            r == NIL || (r as int) < self.a@.len(),
    {
        let ghost target = s_find_del(
            self.a@,
            self.ar@[n_index as int],
            h,
            nkl,
            key,
            self.a@.len(),
        );
        let mut p: u32 = aget(&self.ar, n_index);
        let mut res: u32 = NIL;
        let ghost mut fuel: nat = self.a@.len();
        while p != NIL
            invariant_except_break
                p == NIL || ((p as int) < self.a@.len() && fuel >= p as int + 1),
                target == s_find_del(self.a@, p, h, nkl, key, fuel),
                res == NIL,
            invariant
                wf(self.g()),
            ensures
                res == target,
                res == NIL || (res as int) < self.a@.len(),
            decreases if p == NIL {
                0int
            } else {
                p as int + 1
            },
        {
            let n = nref(&self.a, p);
            // ⛔ THE DEFECT: `n.nkl == 0` is a DISJUNCT, so a NUMERIC bucket
            // matches on hash equality alone and its key is never compared.
            let eq = n.h == h && (n.nkl == 0 || (n.nkl == nkl && n.k == key));
            let nx = n.nxt;
            if eq {
                res = p;
                break;
            }
            assert(node_ok(self.a@, p as int));
            proof {
                fuel = (fuel - 1) as nat;
            }
            p = nx;
        }
        res
    }

    /// `_zend_hash_add_or_update(..., HASH_UPDATE)` -- zend_hash.c:192-263.
    fn ins_str(&mut self, key: u64, nkl: u32, data: u64)
        requires
            wf(old(self).g()),
            nkl <= 8,
            old(self).a@.len() < 0x3FFF_FFFF,
        ensures
            final(self).g() == s_ins_str(old(self).g(), key, nkl, data),
            wf(final(self).g()),
            final(self).a@.len() <= old(self).a@.len() + 1,
    {
        let ghost g0 = self.g();
        let h = hash_of(key, nkl);
        proof {
            lemma_mask_le(h, self.mask);
        }
        let n_index = (h & self.mask) as usize;
        let p = self.find_str(n_index, h, nkl, key);
        if p != NIL {
            let d = nref(&self.a, p).data;
            self.dtor(d);
            set_data(&mut self.a, p, data);
            proof {
                let gs = s_ins_str(g0, key, nkl, data);
                assert(self.a@ =~= gs.nodes);
                assert(self.g() == gs);
                assert forall|q: int| 0 <= q < self.a@.len() implies #[trigger] node_ok(
                    self.a@,
                    q,
                ) by {
                    assert(node_ok(g0.nodes, q));
                }
            }
        } else {
            self.alloc(BUCKET_BASE + nkl as usize);
            let ix: u32 = self.a.len() as u32;
            self.a.push(
                Node { h: h, nkl: nkl, k: key, data: data, nxt: NIL, lst: NIL, lnxt: NIL, llst: NIL },
            );
            proof {
                assert forall|q: int| 0 <= q < self.a@.len() implies #[trigger] node_ok(
                    self.a@,
                    q,
                ) by {
                    if q < g0.nodes.len() {
                        assert(node_ok(g0.nodes, q));
                    }
                }
                assert forall|j: int| 0 <= j < self.ar@.len() implies (#[trigger] self.ar@[j])
                    == NIL || (self.ar@[j] as int) < ix as int by {
                    assert(g0.ar[j] == NIL || (g0.ar[j] as int) < g0.nodes.len());
                }
            }
            self.connect(ix, n_index);
        }
    }

    /// `_zend_hash_index_update_or_next_insert(..., HASH_UPDATE)` -- :339-402.
    fn ins_idx(&mut self, h: u64, data: u64)
        requires
            wf(old(self).g()),
            old(self).a@.len() < 0x3FFF_FFFF,
        ensures
            final(self).g() == s_ins_idx(old(self).g(), h, data),
            wf(final(self).g()),
            final(self).a@.len() <= old(self).a@.len() + 1,
    {
        let ghost g0 = self.g();
        proof {
            lemma_mask_le(h, self.mask);
        }
        let n_index = (h & self.mask) as usize;
        let p = self.find_idx(n_index, h);
        if p != NIL {
            let d = nref(&self.a, p).data;
            self.dtor(d);
            set_data(&mut self.a, p, data);
            proof {
                assert forall|q: int| 0 <= q < self.a@.len() implies #[trigger] node_ok(
                    self.a@,
                    q,
                ) by {
                    assert(node_ok(g0.nodes, q));
                }
            }
        } else {
            self.alloc(BUCKET_BASE);
            let ix: u32 = self.a.len() as u32;
            self.a.push(
                Node { h: h, nkl: 0, k: 0, data: data, nxt: NIL, lst: NIL, lnxt: NIL, llst: NIL },
            );
            proof {
                assert forall|q: int| 0 <= q < self.a@.len() implies #[trigger] node_ok(
                    self.a@,
                    q,
                ) by {
                    if q < g0.nodes.len() {
                        assert(node_ok(g0.nodes, q));
                    }
                }
                assert forall|j: int| 0 <= j < self.ar@.len() implies (#[trigger] self.ar@[j])
                    == NIL || (self.ar@[j] as int) < ix as int by {
                    assert(g0.ar[j] == NIL || (g0.ar[j] as int) < g0.nodes.len());
                }
            }
            self.connect(ix, n_index);
        }
        let ghost gm = self.g();
        if (h as i64) >= (self.nnext as i64) {
            self.nnext = h.wrapping_add(1);
        }
        proof {
            let gs = s_ins_idx(g0, h, data);
            assert(self.a@ =~= gs.nodes);
            assert(self.ar@ =~= gs.ar);
            assert(self.g() == gs);
        }
    }

    /// `zend_hash_del_key_or_index` -- zend_hash.c:450-503. THE PRIMARY SPAN.
    #[verifier::rlimit(120)]
    fn del(&mut self, key: u64, nkl: u32, h0: u64, del_key: bool)
        requires
            wf(old(self).g()),
            nkl <= 8,
        ensures
            final(self).g() == s_del(old(self).g(), key, nkl, h0, del_key),
            wf(final(self).g()),
            final(self).a@.len() == old(self).a@.len(),
    {
        let ghost g0 = self.g();
        let h = if del_key {
            hash_of(key, nkl)
        } else {
            h0
        };
        proof {
            lemma_mask_le(h, self.mask);
        }
        let n_index = (h & self.mask) as usize;
        let p = self.find_del(n_index, h, nkl, key);
        if p == NIL {
            self.ndfail = self.ndfail.wrapping_add(1);
        } else {
            let n = nref(&self.a, p);
            let nxt = n.nxt;
            let lst = n.lst;
            let lnxt = n.lnxt;
            let llst = n.llst;
            let cnkl = n.nkl;
            let cdata = n.data;
            assert(node_ok(g0.nodes, p as int));
            if aget(&self.ar, n_index) == p {
                aset(&mut self.ar, n_index, nxt);
            } else if lst != NIL {
                set_nxt(&mut self.a, lst, nxt);
            }
            if nxt != NIL {
                set_lst(&mut self.a, nxt, lst);
            }
            if llst != NIL {
                set_lnxt(&mut self.a, llst, lnxt);
            } else {
                self.lhead = lnxt;
            }
            if lnxt != NIL {
                set_llst(&mut self.a, lnxt, llst);
            } else {
                self.ltail = llst;
            }
            if self.iptr == p {
                self.iptr = lnxt;
            }
            self.dtor(cdata);
            self.free(BUCKET_BASE + cnkl as usize);
            self.nelem = self.nelem.wrapping_sub(1);
            self.ndok = self.ndok.wrapping_add(1);
            proof {
                let gs = s_del(g0, key, nkl, h0, del_key);
                assert(self.a@ =~= gs.nodes);
                assert(self.ar@ =~= gs.ar);
                assert(self.g() == gs);
                assert forall|q: int| 0 <= q < self.a@.len() implies #[trigger] node_ok(
                    self.a@,
                    q,
                ) by {
                    assert(node_ok(g0.nodes, q));
                }
                assert forall|j: int| 0 <= j < self.ar@.len() implies (#[trigger] self.ar@[j])
                    == NIL || (self.ar@[j] as int) < self.a@.len() by {
                    assert(g0.ar[j] == NIL || (g0.ar[j] as int) < g0.nodes.len());
                }
            }
        }
    }

    /// The fold over the SURVIVING keys, then the counters, then the tally.
    fn fold(&self) -> (r: u64)
        requires
            wf(self.g()),
        ensures
            r == s_tail(self.g()),
    {
        let ghost target = s_fold(self.g(), self.lhead, 0, self.a@.len());
        let mut acc: u64 = 0;
        let mut p: u32 = self.lhead;
        let ghost mut fuel: nat = self.a@.len();
        while p != NIL
            invariant
                wf(self.g()),
                p == NIL || ((p as int) < self.a@.len() && fuel + (p as int)
                    >= self.a@.len()),
                fuel <= self.a@.len(),
                target == s_fold(self.g(), p, acc, fuel),
            decreases if p == NIL {
                0int
            } else {
                self.a@.len() - p as int
            },
        {
            let n = nref(&self.a, p);
            let nkl = n.nkl;
            let hh = n.h;
            let kk = n.k;
            let dd = n.data;
            let ln = n.lnxt;
            assert(node_ok(self.a@, p as int));
            acc = acc.wrapping_mul(31).wrapping_add(nkl as u64);
            acc = acc.wrapping_mul(31).wrapping_add(hh);
            let ghost acc0 = acc;
            let mut i: usize = 0;
            while i < nkl as usize
                invariant
                    i <= nkl,
                    nkl <= 8,
                    acc == s_foldk(kk, i as nat, acc0),
                decreases nkl as int - i as int,
            {
                acc = acc.wrapping_mul(31).wrapping_add(kbyte(kk, i));
                i = i + 1;
            }
            acc = acc.wrapping_mul(31).wrapping_add(dd & 0xFFFF);
            proof {
                fuel = (fuel - 1) as nat;
            }
            p = ln;
        }
        acc = acc.wrapping_mul(31).wrapping_add(self.nelem);
        acc = acc.wrapping_mul(31).wrapping_add(self.nnext);
        acc = acc.wrapping_mul(31).wrapping_add(self.ndtor);
        acc = acc.wrapping_mul(31).wrapping_add(self.dfold);
        acc = acc.wrapping_mul(31).wrapping_add(self.ndok);
        acc = acc.wrapping_mul(31).wrapping_add(self.ndfail);
        acc ^ (self.na.wrapping_mul(1000003) ^ self.nf.wrapping_mul(1000033)
            ^ self.nh.wrapping_mul(1000037) ^ self.ab.wrapping_mul(1000039))
    }

    /// One record of the key stream.
    fn step(&mut self, ctl: u32, b1: u32, val: u64)
        requires
            wf(old(self).g()),
            old(self).a@.len() < 0x3FFF_FFFF,
        ensures
            final(self).g() == s_step(old(self).g(), ctl, b1, val),
            wf(final(self).g()),
            final(self).a@.len() <= old(self).a@.len() + 1,
    {
        let sel: u32 = b1 & (NKEY - 1);
        assert(sel < 64) by (bit_vector)
            requires
                sel == b1 & 63u32,
        ;
        let (key, nkl): (u64, u32) = key_of(sel);
        let data: u64 = 0x10000u64 | val;
        let op: u32 = ctl & 1;
        let kind: u32 = (ctl >> 1) & 1;
        let coll: u32 = (ctl >> 2) & 1;
        if op == 0 {
            if kind == 0 {
                self.ins_str(key, nkl, data);
            } else {
                let idx = if coll == 1 {
                    hash_of(key, nkl)
                } else {
                    b1 as u64
                };
                self.ins_idx(idx, data);
            }
        } else if kind == 0 {
            self.del(key, nkl, 0, true);
        } else {
            let idx = if coll == 1 {
                hash_of(key, nkl)
            } else {
                b1 as u64
            };
            self.del(key, 0, idx, false);
        }
    }
}

#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> (r: u64)
    requires
        off + len <= buf@.len(),
        4 <= len,
        len <= 268435456,
    ensures
        r == hash_fold(buf@, off as int, len as int),
{
    // Ghost only: `spec_slice_len` is what tells the solver a slice length fits
    // in a `usize`, which with `off + len <= buf@.len()` is what stops
    // `off + len` overflowing below.
    assert(buf@.len() == vstd::slice::spec_slice_len(buf));
    let win: &[u8] = wsub(buf, off, len);
    // Ghost only: `nrec` is a `usize` division and the whole record loop rests
    // on `nrec * 4 <= len`, which is a division fact Z3 needs named.
    proof {
        vstd::arithmetic::div_mod::lemma_div_decreases(len as int, 4);
        vstd::arithmetic::div_mod::lemma_fundamental_div_mod(len as int, 4);
    }
    let nrec: usize = len / REC;
    let ts = table_size(nrec);
    let mut t = Ht {
        a: Vec::new(),
        ar: vec![NIL;ts],
        mask: (ts - 1) as u64,
        lhead: NIL,
        ltail: NIL,
        iptr: NIL,
        nelem: 0,
        nnext: 0,
        ndtor: 0,
        dfold: 0,
        ndok: 0,
        ndfail: 0,
        cnt: vec![0u32;MCM],
        na: 0,
        nf: 0,
        nh: 0,
        ab: 0,
    };
    proof {
        assert(t.a@ =~= Seq::<Node>::empty());
        assert(t.ar@ =~= Seq::new(ts as nat, |i: int| NIL));
        assert(t.cnt@ =~= Seq::new(MCM as nat, |i: int| 0u32));
        assert(t.g() == g_init(ts as nat));
    }
    t.alloc(8 * ts);
    let ghost g0 = t.g();
    let ghost target = s_run(win@, 0, nrec as nat, g0);
    let mut r: usize = 0;
    while r < nrec
        invariant
            r <= nrec,
            nrec * 4 <= win@.len(),
            nrec <= 0x400_0000,
            wf(t.g()),
            t.a@.len() <= r,
            target == s_run(win@, r as nat, nrec as nat, t.g()),
        decreases nrec - r,
    {
        let ctl: u32 = wb(win, r * REC) as u32;
        let b1: u32 = wb(win, r * REC + 1) as u32;
        let val: u64 = (wb(win, r * REC + 2) as u64) | ((wb(win, r * REC + 3) as u64) << 8);
        t.step(ctl, b1, val);
        r = r + 1;
    }
    t.fold()
}

// ---------------------------------------------------------------- driver ----
fn main() {
    let (n_iters, stride_w, bytes) = load_input();
    // SLB-DRIVER-BEGIN
    let n_blob: usize = bytes.len();
    let buf: &[u8] = bytes.as_slice();
    let mut acc: u64 = 0;
    if stride_w >= 4 && stride_w <= 268435456 && stride_w <= n_blob as u64 {
        let stride: usize = stride_w as usize;
        let nwin: u64 = (n_blob / stride) as u64;
        let mut it: u64 = 0;
        proof {
            vstd::arithmetic::div_mod::lemma_div_non_zero(n_blob as int, stride as int);
        }
        while it < n_iters
            invariant
                4 <= stride <= n_blob,
                stride <= 268435456,
                buf@.len() == n_blob,
                nwin == n_blob / stride,
                nwin >= 1,
            decreases n_iters - it,
        {
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
            assert(r == hash_fold(buf@, (k * stride) as int, stride as int));
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    emit(acc);
}

} // verus!
