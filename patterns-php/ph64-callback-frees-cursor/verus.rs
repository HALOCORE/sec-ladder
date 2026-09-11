//! ph64 rung R5 -- unsafe + Verus.
//!
//! Same exec code as `unsafe.rs`, plus the proof that licenses it:
//!
//!     requires  off + len <= buf@.len(),  24 <= len,  len <= 268435456
//!     ensures   r == llist_fold(buf@, off as int, len as int)
//!
//! ============================================================================
//! ⚠⚠⚠ WHAT THE PROOF IS ABOUT, AND WHY IT IS NOT A BOUNDS PROOF
//! ============================================================================
//! Every other row in this programme proves an INDEX is in range. This one
//! cannot: R1's defect is that `element` OUTLIVES the callback that freed it,
//! and a lifetime is not an index. What the four Rust rungs do instead is change
//! the REPRESENTATION -- `zend_llist_element *next` becomes a `u32` into an
//! arena the kernel owns -- and the proof obligation that survives that change
//! is the one this file discharges:
//!
//!   **`wf`**: every link is either `NIL` or an index BELOW the arena's length,
//!   `next` strictly ASCENDS and `prev` strictly DESCENDS. It is preserved by
//!   `register` (append at the tail) and by `del_element` (which only ever
//!   short-circuits `prev -> next`, and `prev < c < next`).
//!
//! ⭐ From `wf` alone come BOTH halves of what R1 loses: every one of the eight
//! unchecked accessors is in bounds, and every walk TERMINATES -- `decreases
//! arena.len() - element` is exactly the `next`-ascends fact. In C the wild
//! `element->next` destroys both at once, which is why `inputs/adversarial-reuse-*`
//! SIGSEGV rather than merely answering wrongly.
//!
//! ⚠⚠ AND THAT IS THE ROW'S HONEST LADDER RESULT, STATED HERE RATHER THAN IN A
//! FOOTNOTE: `562f886ecb14`'s guard -- `if (ret && tick_fe1->calling)` -- IS NOT
//! WHAT DISCHARGES ANY OF IT. `wf` holds with the guard deleted. The guard buys
//! the VALUE: without it the walk still terminates and still reads in bounds,
//! and it returns a different `u64` (see `../controls/arena_r1.py`). So on this
//! row memory safety and the upstream fix are ORTHOGONAL, and the fix is a
//! logical invariant that only the value postcondition can see. `../NOTES.md`
//! §9.
//!
//! ============================================================================
//! HOW THE VALUE POSTCONDITION IS DISCHARGED
//! ============================================================================
//! By a LOCKSTEP GHOST MIRROR, which is `ph07`'s `walk_start`/`walk_end`
//! technique scaled up to a mutable structure. `G` is a pure-value copy of the
//! exec state (`Seq<Node>` for the arena, plain integers for everything else);
//! `Ticks::g()` projects the exec state into it; and every exec method carries
//! `ensures self.g() == s_<method>(old(self).g(), ..)` where `s_<method>` is a
//! spec function written in the same order as the code. The three loops --
//! `del_element`, `apply`, `destroy` -- each carry the "remaining computation"
//! invariant `s_X(g_at_entry, cur_at_entry, fuel_at_entry) == s_X(self.g(),
//! cur, fuel)`, so at loop exit the equality collapses to the whole
//! computation. `llist_fold` is the composition, and `../model.py` re-derives
//! the same `u64` from a CLOSED FORM with no list, no cursor and no event
//! replay -- three independent spellings, and the gate drives the first against
//! the third.
//!
//! ⚠ The spec walks are FUEL-bounded (`decreases fuel`) because a `Seq<Node>`
//! carries no ordering fact by itself. The exec loops keep `fuel >= arena.len()
//! - cur`, which `wf` makes true, so the fuel never runs out on any reachable
//! state. A fuel that COULD run out would make the postcondition weaker than it
//! looks, so the invariant is stated and not assumed.

use vstd::prelude::*;

// Plain-Rust I/O helpers. Outside `verus!`, so Verus treats the whole module as
// external and the two `external_body` wrappers below are the only way in.
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

pub const HEAD: usize = 16;
pub const SLOT: usize = 4;
pub const SZ_NAME: usize = 8;
pub const REQ_ELEM: usize = 39;
pub const MAX_CACHED_MEMORY: usize = 11;
pub const MAX_CACHED_ENTRIES: u32 = 256;
pub const NIL: u32 = 0xFFFF_FFFF;

pub const UNREG_SELF: u32 = 1;
pub const UNREG_AHEAD: u32 = 2;
pub const UNREG_BEHIND: u32 = 3;

pub struct Node {
    pub next: u32,
    pub prev: u32,
    pub name: u64,
    pub calling: bool,
}

// ---------------------------------------------------------------- spec ------
/// `_emalloc`'s `REAL_SIZE(size)` -- zend_alloc.c:132, `(size + 7) & ~7`. The
/// exec code writes exactly this expression, so no bit-vector reasoning is
/// needed to connect them.
pub open spec fn real_of(size: usize) -> usize {
    ((size + 7) as usize) & !(7usize)
}

/// `cache_index = real_size >> 3` -- zend_alloc.c:136.
pub open spec fn idx_of(size: usize) -> usize {
    real_of(size) >> 3
}

pub open spec fn rd32_s(win: Seq<u8>, i: int) -> u32 {
    (win[i] as u32) | ((win[i + 1] as u32) << 8) | ((win[i + 2] as u32) << 16) | ((win[i + 3]
        as u32) << 24)
}

/// Entry `id`'s `arguments[0]`, as the 64-bit value the comparison is:
/// `[u32 le id][u32 le slot]`.
pub open spec fn name_of_s(win: Seq<u8>, id: u32) -> u64 {
    (id as u64) | ((rd32_s(win, HEAD + (id as int - 1) * SLOT) as u64) << 32)
}

pub open spec fn mix(a: u64, b: u64) -> u64 {
    a.wrapping_mul(31).wrapping_add(b)
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

/// The kernel's whole observable state. `n` / `trigger` / `mode` / `reuse` are
/// decoded once from the window and never change; they ride along so the
/// transition functions take one argument instead of five.
pub struct G {
    pub arena: Seq<Node>,
    pub head: u32,
    pub tail: u32,
    pub count: u64,
    pub al: A,
    pub fold: u64,
    pub visits: u64,
    pub dtors: u64,
    pub refusals: u64,
    pub reuse_done: bool,
    pub n: u32,
    pub trigger: u32,
    pub mode: u32,
    pub reuse: bool,
}

/// ⭐ THE ROW'S SAFETY INVARIANT. Every link is `NIL` or an in-range index,
/// `next` strictly ASCENDS and `prev` strictly DESCENDS. `zend_llist` gets the
/// first for free (a pointer is a pointer) and has NO analogue of the second --
/// which is exactly why the C walk has no termination measure and this one does.
pub open spec fn node_ok(a: Seq<Node>, i: int, n: u32) -> bool {
    &&& (a[i].next == NIL || ((a[i].next as int) > i && (a[i].next as int) < a.len()))
    &&& (a[i].prev == NIL || ((a[i].prev as int) < i))
    &&& 1 <= (a[i].name as u32) <= n
}

pub open spec fn wf(g: G) -> bool {
    &&& g.al.cnt.len() == MAX_CACHED_MEMORY as int
    &&& g.arena.len() < 0x4000_0000
    &&& 1 <= g.n <= 0x1000_0000
    &&& (g.head == NIL || (g.head as int) < g.arena.len())
    &&& (g.tail == NIL || (g.tail as int) < g.arena.len())
    &&& forall|i: int| 0 <= i < g.arena.len() ==> #[trigger] node_ok(g.arena, i, g.n)
}

/// The low half of a name IS the entry id -- which is what makes names unique
/// and what lets the walk hand `userland` an id it can act on. One bit-vector
/// fact, isolated so nothing else needs bit reasoning.
pub proof fn lemma_name_id(id: u32, hi: u32)
    ensures
        (((id as u64) | ((hi as u64) << 32)) as u32) == id,
{
    assert((((id as u64) | ((hi as u64) << 32)) as u32) == id) by (bit_vector);
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

pub open spec fn s_alloc(g: G, size: usize) -> G {
    G { al: s_alloc_a(g.al, size), ..g }
}

pub open spec fn s_free(g: G, size: usize) -> G {
    G { al: s_free_a(g.al, size), ..g }
}

/// `DEL_LLIST_ELEMENT(current, l)` -- zend_llist.c:73-88, in the code's own
/// order: unlink `prev`, unlink `next`, run the dtor, `pefree`, `--l->count`.
pub open spec fn s_unlink(g: G, c: int) -> G {
    let nd = g.arena[c];
    let a1 = if nd.prev != NIL {
        g.arena.update(nd.prev as int, Node { next: nd.next, ..g.arena[nd.prev as int] })
    } else {
        g.arena
    };
    let h1 = if nd.prev != NIL {
        g.head
    } else {
        nd.next
    };
    let a2 = if nd.next != NIL {
        a1.update(nd.next as int, Node { prev: nd.prev, ..a1[nd.next as int] })
    } else {
        a1
    };
    let t1 = if nd.next != NIL {
        g.tail
    } else {
        nd.prev
    };
    let g1 = G { arena: a2, head: h1, tail: t1, dtors: g.dtors.wrapping_add(1), ..g };
    let g2 = s_free(g1, SZ_NAME);
    let g3 = s_free(g2, REQ_ELEM);
    G { count: g3.count.wrapping_sub(1), ..g3 }
}

/// `zend_llist_del_element` -- zend_llist.c:91-104, with the comparator
/// (basic_functions.c:2146-2161) and `562f886ecb14`'s guard inlined.
pub open spec fn s_del(g: G, key: u64, cur: u32, fuel: nat) -> G
    decreases fuel,
{
    if fuel == 0 || cur == NIL || cur as int >= g.arena.len() {
        g
    } else {
        let nd = g.arena[cur as int];
        let ret = nd.name == key;
        if ret && nd.calling {
            s_del(
                G { refusals: g.refusals.wrapping_add(1), ..g },
                key,
                nd.next,
                (fuel - 1) as nat,
            )
        } else if ret {
            s_unlink(g, cur as int)
        } else {
            s_del(g, key, nd.next, (fuel - 1) as nat)
        }
    }
}

/// `PHP_FUNCTION(unregister_tick_function)` -- basic_functions.c:2840-2862.
pub open spec fn s_unreg(g: G, win: Seq<u8>, id: u32) -> G {
    let g1 = s_alloc(g, SZ_NAME);
    let g2 = s_del(g1, name_of_s(win, id), g1.head, g1.arena.len());
    s_free(g2, SZ_NAME)
}

/// `call_user_function` -- basic_functions.c:2111-2116, projected.
pub open spec fn s_userland(g: G, win: Seq<u8>, nm: u64) -> G {
    let me = nm as u32;
    let g2 = G {
        fold: mix(mix(g.fold, me as u64), nm >> 32),
        visits: g.visits.wrapping_add(1),
        ..g
    };
    if me != g2.trigger {
        g2
    } else {
        let g3 = if g2.mode == UNREG_SELF {
            s_unreg(g2, win, me)
        } else if g2.mode == UNREG_AHEAD {
            if me < g2.n {
                s_unreg(g2, win, (me + 1) as u32)
            } else {
                g2
            }
        } else if g2.mode == UNREG_BEHIND {
            if me > 1 {
                s_unreg(g2, win, (me - 1) as u32)
            } else {
                g2
            }
        } else {
            g2
        };
        if g3.reuse && !g3.reuse_done {
            G { reuse_done: true, ..s_alloc(g3, REQ_ELEM) }
        } else {
            g3
        }
    }
}

/// One iteration of `zend_llist_apply`'s body -- `user_tick_function_call`,
/// basic_functions.c:2102-2137. `:2109` sets the flag, `:2135` clears it, and
/// `:2135` IS SITE C.
pub open spec fn s_visit(g: G, win: Seq<u8>, e: u32) -> G {
    let nd = g.arena[e as int];
    if !nd.calling {
        let g1 = G { arena: g.arena.update(e as int, Node { calling: true, ..nd }), ..g };
        let g2 = s_userland(g1, win, g1.arena[e as int].name);
        G {
            arena: g2.arena.update(e as int, Node { calling: false, ..g2.arena[e as int] }),
            ..g2
        }
    } else {
        g
    }
}

/// ⚠⚠ `zend_llist_apply` -- zend_llist.c:186-193, THE PRIMARY SPAN. The cursor
/// is re-read from the arena AFTER `s_visit`, which is the `for` header running
/// after the callback returned.
pub open spec fn s_apply(g: G, win: Seq<u8>, cur: u32, fuel: nat) -> G
    decreases fuel,
{
    if fuel == 0 || cur == NIL || cur as int >= g.arena.len() {
        g
    } else {
        let g1 = s_visit(g, win, cur);
        s_apply(g1, win, g1.arena[cur as int].next, (fuel - 1) as nat)
    }
}

/// `zend_llist_destroy` -- zend_llist.c:107-121.
pub open spec fn s_destroy(g: G, cur: u32, fuel: nat) -> G
    decreases fuel,
{
    if fuel == 0 || cur == NIL || cur as int >= g.arena.len() {
        G { count: 0, ..g }
    } else {
        let nd = g.arena[cur as int];
        let g2 = s_free(s_free(g, SZ_NAME), REQ_ELEM);
        s_destroy(g2, nd.next, (fuel - 1) as nat)
    }
}

/// `PHP_FUNCTION(register_tick_function)` -- basic_functions.c:2799-2835, with
/// `zend_llist_add_element` (zend_llist.c:37-52) inlined.
pub open spec fn s_reg(g: G, win: Seq<u8>, id: u32) -> G {
    let g2 = s_alloc(s_alloc(g, SZ_NAME), REQ_ELEM);
    let ix = g2.arena.len();
    let a1 = g2.arena.push(Node { next: NIL, prev: g2.tail, name: name_of_s(win, id), calling: false });
    let a2 = if g2.tail != NIL {
        a1.update(g2.tail as int, Node { next: ix as u32, ..a1[g2.tail as int] })
    } else {
        a1
    };
    let h1 = if g2.tail != NIL {
        g2.head
    } else {
        ix as u32
    };
    G { arena: a2, head: h1, tail: ix as u32, count: g2.count.wrapping_add(1), ..g2 }
}

pub open spec fn s_regloop(g: G, win: Seq<u8>, i: u32, n: u32, fuel: nat) -> G
    decreases fuel,
{
    if fuel == 0 || i > n {
        g
    } else {
        s_regloop(s_reg(g, win, i), win, (i + 1) as u32, n, (fuel - 1) as nat)
    }
}

pub open spec fn tally_of(a: A) -> u64 {
    a.n_alloc.wrapping_mul(1000003) ^ a.n_free.wrapping_mul(1000033) ^ a.n_hit.wrapping_mul(
        1000037,
    ) ^ a.bytes.wrapping_mul(1000039)
}

pub open spec fn g_init(n: u32, trigger: u32, mode: u32, reuse: bool) -> G {
    G {
        arena: Seq::empty(),
        head: NIL,
        tail: NIL,
        count: 0,
        al: A {
            cnt: Seq::new(MAX_CACHED_MEMORY as nat, |i: int| 0u32),
            n_alloc: 0,
            n_free: 0,
            n_hit: 0,
            bytes: 0,
        },
        fold: 0,
        visits: 0,
        dtors: 0,
        refusals: 0,
        reuse_done: false,
        n,
        trigger,
        mode,
        reuse,
    }
}

/// ⭐ WHAT THE KERNEL RETURNS. `../model.py`'s `llist_fold` computes the same
/// `u64` from a closed form with no list and no cursor, and the gate evaluates
/// this row's `ensures` against THAT -- so the two must agree on every window
/// the corpus makes, and `model.py::selfcheck` drives a third spelling over a
/// domain `inputs/` cannot carry.
/// The whole kernel, once the four head words are decoded: register, walk,
/// top-level unregister, fold, free, destroy, tally. Split out from
/// `llist_fold` so that the DECODE and the RUN are two proof obligations
/// instead of one -- `kernel` discharges them separately and Z3's budget is
/// not asked to carry both term trees at once.
#[verifier::opaque]
pub open spec fn run_spec(
    win: Seq<u8>,
    n: u32,
    trigger: u32,
    mode: u32,
    reuse: bool,
    post: u32,
) -> u64 {
    let g1 = s_regloop(g_init(n, trigger, mode, reuse), win, 1, n, n as nat);
    let g2 = s_apply(g1, win, g1.head, g1.arena.len());
    let g3 = if post != 0 {
        s_unreg(g2, win, post)
    } else {
        g2
    };
    let acc = mix(
        mix(mix(mix(mix(g3.fold, g3.count), g3.dtors), g3.visits), g3.refusals),
        n as u64,
    );
    let g4 = if g3.reuse_done {
        s_free(g3, REQ_ELEM)
    } else {
        g3
    };
    let g5 = s_destroy(g4, g4.head, g4.arena.len());
    acc ^ tally_of(g5.al)
}

/// ⭐ WHAT THE KERNEL RETURNS. `../model.py`'s `llist_fold` computes the same
/// `u64` from a closed form with no list and no cursor, and the gate evaluates
/// this row's `ensures` against THAT -- so the two must agree on every window
/// the corpus makes, and `model.py::selfcheck` drives a third spelling over a
/// domain `inputs/` cannot carry.
pub open spec fn llist_fold(buf: Seq<u8>, off: int, len: int) -> u64 {
    let win = buf.subrange(off, off + len);
    let nmax: int = (len - 16) / 4;
    let n: int = 1 + (rd32_s(win, 0) as int) % nmax;
    let trigger: int = (rd32_s(win, 4) as int) % (n + 1);
    let mode: int = (rd32_s(win, 8) as int) % 4;
    let reuse: bool = ((rd32_s(win, 8) >> 16) & 1) == 1;
    let post: int = (rd32_s(win, 12) as int) % (n + 1);
    run_spec(win, n as u32, trigger as u32, mode as u32, reuse, post as u32)
}

// -------------------------------------------------- TRUSTED, items 1..7/10 --
// The arena accessors. Every one's obligation is `i < v.len()` and nothing
// else; `wf` is what discharges all seven arena accessors. `../NOTES.md` §10
// argues each of the eight trusted items that has an `ensures`.
#[inline(always)]
#[verifier::external_body]
fn nnext(v: &Vec<Node>, i: usize) -> (r: u32)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int].next,
{
    unsafe { v.get_unchecked(i).next }
}

#[cfg(slb_twin)]
fn slb_twin_nnext(v: &Vec<Node>, i: usize) -> (r: u32)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int].next,
{
    v[i].next
}

#[inline(always)]
#[verifier::external_body]
fn nprev(v: &Vec<Node>, i: usize) -> (r: u32)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int].prev,
{
    unsafe { v.get_unchecked(i).prev }
}

#[cfg(slb_twin)]
fn slb_twin_nprev(v: &Vec<Node>, i: usize) -> (r: u32)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int].prev,
{
    v[i].prev
}

#[inline(always)]
#[verifier::external_body]
fn nname(v: &Vec<Node>, i: usize) -> (r: u64)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int].name,
{
    unsafe { v.get_unchecked(i).name }
}

#[cfg(slb_twin)]
fn slb_twin_nname(v: &Vec<Node>, i: usize) -> (r: u64)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int].name,
{
    v[i].name
}

#[inline(always)]
#[verifier::external_body]
fn ncalling(v: &Vec<Node>, i: usize) -> (r: bool)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int].calling,
{
    unsafe { v.get_unchecked(i).calling }
}

#[cfg(slb_twin)]
fn slb_twin_ncalling(v: &Vec<Node>, i: usize) -> (r: bool)
    requires
        i < v@.len(),
    ensures
        r == v@[i as int].calling,
{
    v[i].calling
}

// ⚠ The three write wrappers name the WHOLE post-state -- `old(v)@.update(i,
// Node { field: x, ..old(v)@[i] })` -- so a body that also moved a NEIGHBOUR's
// link could not satisfy its own postcondition. That completeness is what a
// write wrapper's contract can get wrong, and it is why Miri is required on this
// row (../spec.md `miri`): unlinking is exactly a neighbour write.
#[inline(always)]
#[verifier::external_body]
fn set_next(v: &mut Vec<Node>, i: usize, x: u32)
    requires
        i < old(v)@.len(),
    ensures
        final(v)@ == old(v)@.update(i as int, Node { next: x, ..old(v)@[i as int] }),
{
    unsafe { v.get_unchecked_mut(i).next = x; }
}

#[cfg(slb_twin)]
fn slb_twin_set_next(v: &mut Vec<Node>, i: usize, x: u32)
    requires
        i < old(v)@.len(),
    ensures
        final(v)@ == old(v)@.update(i as int, Node { next: x, ..old(v)@[i as int] }),
{
    let p = v[i].prev;
    let nm = v[i].name;
    let c = v[i].calling;
    v.set(i, Node { next: x, prev: p, name: nm, calling: c });
}

#[inline(always)]
#[verifier::external_body]
fn set_prev(v: &mut Vec<Node>, i: usize, x: u32)
    requires
        i < old(v)@.len(),
    ensures
        final(v)@ == old(v)@.update(i as int, Node { prev: x, ..old(v)@[i as int] }),
{
    unsafe { v.get_unchecked_mut(i).prev = x; }
}

#[cfg(slb_twin)]
fn slb_twin_set_prev(v: &mut Vec<Node>, i: usize, x: u32)
    requires
        i < old(v)@.len(),
    ensures
        final(v)@ == old(v)@.update(i as int, Node { prev: x, ..old(v)@[i as int] }),
{
    let nx = v[i].next;
    let nm = v[i].name;
    let c = v[i].calling;
    v.set(i, Node { next: nx, prev: x, name: nm, calling: c });
}

#[inline(always)]
#[verifier::external_body]
fn set_calling(v: &mut Vec<Node>, i: usize, x: bool)
    requires
        i < old(v)@.len(),
    ensures
        final(v)@ == old(v)@.update(i as int, Node { calling: x, ..old(v)@[i as int] }),
{
    unsafe { v.get_unchecked_mut(i).calling = x; }
}

#[cfg(slb_twin)]
fn slb_twin_set_calling(v: &mut Vec<Node>, i: usize, x: bool)
    requires
        i < old(v)@.len(),
    ensures
        final(v)@ == old(v)@.update(i as int, Node { calling: x, ..old(v)@[i as int] }),
{
    let nx = v[i].next;
    let p = v[i].prev;
    let nm = v[i].name;
    v.set(i, Node { next: nx, prev: p, name: nm, calling: x });
}

// ------------------------------------------------------- TRUSTED, item 8/10 --
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

// ------------------------------------------------------- TRUSTED, item 9/10 --
#[verifier::external_body]
fn emit(acc: u64) {
    driver::emit(acc);
}

// ---------------------------------------------------------------- exec ------
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

    /// `_emalloc` -- zend_alloc.c:142-217.
    #[inline(always)]
    fn alloc(&mut self, size: usize)
        requires
            size == SZ_NAME || size == REQ_ELEM,
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

    /// `_efree` -- zend_alloc.c:248-289.
    #[inline(always)]
    fn free(&mut self, size: usize)
        requires
            size == SZ_NAME || size == REQ_ELEM,
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

pub struct Ticks {
    pub arena: Vec<Node>,
    pub head: u32,
    pub tail: u32,
    pub count: u64,
    pub al: Alloc,
    pub fold: u64,
    pub visits: u64,
    pub dtors: u64,
    pub refusals: u64,
    pub n: u32,
    pub trigger: u32,
    pub mode: u32,
    pub reuse: bool,
    pub reuse_done: bool,
}

impl Ticks {
    pub open spec fn g(&self) -> G {
        G {
            arena: self.arena@,
            head: self.head,
            tail: self.tail,
            count: self.count,
            al: self.al.a(),
            fold: self.fold,
            visits: self.visits,
            dtors: self.dtors,
            refusals: self.refusals,
            reuse_done: self.reuse_done,
            n: self.n,
            trigger: self.trigger,
            mode: self.mode,
            reuse: self.reuse,
        }
    }
}

#[inline(always)]
fn rd32(win: &[u8], i: usize) -> (r: u32)
    requires
        i + 4 <= win@.len(),
    ensures
        r == rd32_s(win@, i as int),
{
    (win[i] as u32) | ((win[i + 1] as u32) << 8) | ((win[i + 2] as u32) << 16) | ((win[i + 3]
        as u32) << 24)
}

#[inline(always)]
fn name_of(win: &[u8], id: u32) -> (r: u64)
    requires
        1 <= id <= 0x1000_0000,
        HEAD + (id as int - 1) * SLOT + 4 <= win@.len(),
    ensures
        r == name_of_s(win@, id),
{
    let s: usize = HEAD + (id as usize - 1) * SLOT;
    (id as u64) | ((rd32(win, s) as u64) << 32)
}

impl Ticks {
    fn register(&mut self, win: &[u8], id: u32)
        requires
            wf(old(self).g()),
            1 <= id <= old(self).n,
            HEAD + (id as int - 1) * SLOT + 4 <= win@.len(),
            old(self).arena@.len() < 0x3FFF_FFFF,
        ensures
            final(self).g() == s_reg(old(self).g(), win@, id),
            final(self).n == old(self).n,
            final(self).trigger == old(self).trigger,
            final(self).mode == old(self).mode,
            final(self).reuse == old(self).reuse,
            wf(final(self).g()),
            final(self).arena@.len() == old(self).arena@.len() + 1,
    {
        let ghost a0 = self.arena@;
        self.al.alloc(SZ_NAME);
        let name = name_of(win, id);
        self.al.alloc(REQ_ELEM);
        let ix: u32 = self.arena.len() as u32;
        let t = self.tail;
        self.arena.push(Node { next: NIL, prev: t, name, calling: false });
        if t != NIL {
            set_next(&mut self.arena, t as usize, ix);
        } else {
            self.head = ix;
        }
        self.tail = ix;
        self.count = self.count.wrapping_add(1);
        proof {
            lemma_name_id(id, rd32_s(win@, HEAD + (id as int - 1) * SLOT));
        }
        assert forall|i: int| 0 <= i < self.arena@.len() implies #[trigger] node_ok(
            self.arena@,
            i,
            self.n,
        ) by {
            if i < a0.len() {
                assert(node_ok(a0, i, self.n));
            }
        }
    }

    /// The registration phase -- `register_tick_function` once per entry. Its
    /// own method so that `kernel`'s proof context does not carry this loop's
    /// invariants as well as the walk's; the two are independent and Z3's
    /// budget is not.
    fn register_all(&mut self, win: &[u8], n: u32)
        requires
            wf(old(self).g()),
            old(self).arena@.len() == 0,
            old(self).n == n,
            1 <= n <= 0x1000_0000,
            HEAD + (n as int) * SLOT <= win@.len(),
        ensures
            final(self).g() == s_regloop(old(self).g(), win@, 1, n, n as nat),
            wf(final(self).g()),
            final(self).n == old(self).n,
            final(self).trigger == old(self).trigger,
            final(self).mode == old(self).mode,
            final(self).reuse == old(self).reuse,
    {
        let ghost g0 = self.g();
        let mut i: u32 = 1;
        let ghost mut fuel: nat = n as nat;
        while i <= n
            invariant
                wf(self.g()),
                1 <= i <= n + 1,
                1 <= n <= 0x1000_0000,
                HEAD + (n as int) * SLOT <= win@.len(),
                self.arena@.len() == i - 1,
                self.n == n,
                self.trigger == g0.trigger,
                self.mode == g0.mode,
                self.reuse == g0.reuse,
                fuel == n - i + 1,
                s_regloop(g0, win@, 1, n, n as nat) == s_regloop(self.g(), win@, i, n, fuel),
            decreases n - i + 1,
        {
            self.register(win, i);
            proof {
                fuel = (fuel - 1) as nat;
            }
            i = i + 1;
        }
    }

    /// `zend_llist_del_element` -- zend_llist.c:91-104.
    fn del_element(&mut self, key: u64)
        requires
            wf(old(self).g()),
        ensures
            final(self).g() == s_del(old(self).g(), key, old(self).head, old(self).arena@.len()),
            final(self).n == old(self).n,
            final(self).trigger == old(self).trigger,
            final(self).mode == old(self).mode,
            final(self).reuse == old(self).reuse,
            wf(final(self).g()),
            final(self).arena@.len() == old(self).arena@.len(),
    {
        let ghost g0 = self.g();
        let ghost head0 = self.head;
        let ghost f0 = self.arena@.len();
        let mut current: u32 = self.head;
        let ghost mut fuel: nat = f0;
        let ghost mut a_in = self.arena@;
        while current != NIL
            // ⚠ `invariant_except_break` is the half that is FALSE at the
            // `break`: the deletion branch mutates the arena and then leaves,
            // so `a_in == self.arena@` and the "remaining computation" equality
            // are properties of the SEARCH, not of the exit. The `invariant`
            // block below is the half that holds at both exits, and `ensures`
            // is what the two exits have to agree on.
            invariant_except_break
                a_in == self.arena@,
                current == NIL || ((current as int) < self.arena@.len() && fuel + (
                current as int) >= self.arena@.len()),
                fuel <= f0,
                s_del(g0, key, head0, f0) == s_del(self.g(), key, current, fuel),
            invariant
                wf(self.g()),
                self.arena@.len() == g0.arena.len(),
                self.n == g0.n,
                self.trigger == g0.trigger,
                self.mode == g0.mode,
                self.reuse == g0.reuse,
            ensures
                self.g() == s_del(g0, key, head0, f0),
            decreases
                if current == NIL {
                    0int
                } else {
                    self.arena@.len() - current as int
                },
        {
            let ghost gb = self.g();
            let c = current as usize;
            assert(node_ok(self.arena@, c as int, self.n));
            let next = nnext(&self.arena, c);
            let ret: bool = nname(&self.arena, c) == key;
            if ret && ncalling(&self.arena, c) {
                self.refusals = self.refusals.wrapping_add(1);  // 562f886ecb14
                proof {
                    fuel = (fuel - 1) as nat;
                }
                current = next;
            } else if ret {
                let p = nprev(&self.arena, c);
                let nx = next;
                if p != NIL {
                    set_next(&mut self.arena, p as usize, nx);
                } else {
                    self.head = nx;
                }
                if nx != NIL {
                    set_prev(&mut self.arena, nx as usize, p);
                } else {
                    self.tail = p;
                }
                self.dtors = self.dtors.wrapping_add(1);
                self.al.free(SZ_NAME);
                self.al.free(REQ_ELEM);
                self.count = self.count.wrapping_sub(1);
                assert(fuel > 0);
                assert(gb.arena[c as int].name == key);
                assert(!gb.arena[c as int].calling);
                assert(s_del(gb, key, current, fuel) == s_unlink(gb, c as int));
                assert(self.g().arena =~= s_unlink(gb, c as int).arena);
                assert(self.g().al == s_unlink(gb, c as int).al);
                assert(self.g() == s_unlink(gb, c as int));
                assert(self.arena@.len() == g0.arena.len());
                assert(self.g() == s_del(g0, key, head0, f0));
                assert forall|i: int| 0 <= i < self.arena@.len() implies #[trigger] node_ok(
                    self.arena@,
                    i,
                    self.n,
                ) by {
                    assert(node_ok(a_in, i, self.n));
                }
                // `break`, not `return`: `zend_llist_del_element:101` breaks out
                // of its own `while`, and the loop's `ensures` above is where
                // the deletion branch and the exhausted-list branch meet.
                break ;
            } else {
                proof {
                    fuel = (fuel - 1) as nat;
                }
                current = next;
            }
        }
    }

    /// `PHP_FUNCTION(unregister_tick_function)` -- basic_functions.c:2840-2862.
    fn unregister(&mut self, win: &[u8], id: u32)
        requires
            wf(old(self).g()),
            1 <= id <= old(self).n,
            HEAD + (id as int - 1) * SLOT + 4 <= win@.len(),
        ensures
            final(self).g() == s_unreg(old(self).g(), win@, id),
            final(self).n == old(self).n,
            final(self).trigger == old(self).trigger,
            final(self).mode == old(self).mode,
            final(self).reuse == old(self).reuse,
            wf(final(self).g()),
            final(self).arena@.len() == old(self).arena@.len(),
    {
        self.al.alloc(SZ_NAME);
        let key = name_of(win, id);
        self.del_element(key);
        self.al.free(SZ_NAME);
    }

    /// `call_user_function` -- basic_functions.c:2111-2116, projected.
    fn userland(&mut self, win: &[u8], nm: u64)
        requires
            wf(old(self).g()),
            HEAD + (old(self).n as int) * SLOT <= win@.len(),
            1 <= (nm as u32) <= old(self).n,
        ensures
            final(self).g() == s_userland(old(self).g(), win@, nm),
            final(self).n == old(self).n,
            final(self).trigger == old(self).trigger,
            final(self).mode == old(self).mode,
            final(self).reuse == old(self).reuse,
            wf(final(self).g()),
            final(self).arena@.len() == old(self).arena@.len(),
    {
        let me: u32 = nm as u32;
        self.fold = self.fold.wrapping_mul(31).wrapping_add(me as u64);
        self.fold = self.fold.wrapping_mul(31).wrapping_add(nm >> 32);
        self.visits = self.visits.wrapping_add(1);
        if me != self.trigger {
            return ;
        }
        if self.mode == UNREG_SELF {
            self.unregister(win, me);
        } else if self.mode == UNREG_AHEAD {
            if me < self.n {
                self.unregister(win, me + 1);
            }
        } else if self.mode == UNREG_BEHIND {
            if me > 1 {
                self.unregister(win, me - 1);
            }
        }
        if self.reuse && !self.reuse_done {
            self.al.alloc(REQ_ELEM);
            self.reuse_done = true;
        }
    }

    /// ⚠⚠ `zend_llist_apply` -- zend_llist.c:186-193. THE PRIMARY SPAN.
    fn apply(&mut self, win: &[u8])
        requires
            wf(old(self).g()),
            HEAD + (old(self).n as int) * SLOT <= win@.len(),
            old(self).n >= 1,
        ensures
            final(self).g() == s_apply(old(self).g(), win@, old(self).head, old(self).arena@.len()),
            final(self).n == old(self).n,
            final(self).trigger == old(self).trigger,
            final(self).mode == old(self).mode,
            final(self).reuse == old(self).reuse,
            wf(final(self).g()),
            final(self).arena@.len() == old(self).arena@.len(),
    {
        let ghost g0 = self.g();
        let ghost head0 = self.head;
        let ghost f0 = self.arena@.len();
        let mut element: u32 = self.head;
        let ghost mut fuel: nat = f0;
        while element != NIL
            invariant
                wf(self.g()),
                self.arena@.len() == g0.arena.len(),
                self.n == g0.n,
                self.trigger == g0.trigger,
                self.mode == g0.mode,
                self.reuse == g0.reuse,
                self.n >= 1,
                HEAD + (self.n as int) * SLOT <= win@.len(),
                element == NIL || ((element as int) < self.arena@.len() && fuel + (
                element as int) >= self.arena@.len()),
                fuel <= f0,
                s_apply(g0, win@, head0, f0) == s_apply(self.g(), win@, element, fuel),
            decreases
                if element == NIL {
                    0int
                } else {
                    self.arena@.len() - element as int
                },
        {
            let e = element as usize;
            assert(node_ok(self.arena@, e as int, self.n));
            if !ncalling(&self.arena, e) {
                let ghost a0b = self.arena@;
                set_calling(&mut self.arena, e, true);
                assert forall|i: int| 0 <= i < self.arena@.len() implies #[trigger] node_ok(
                    self.arena@,
                    i,
                    self.n,
                ) by {
                    assert(node_ok(a0b, i, self.n));
                }
                let nm = nname(&self.arena, e);
                self.userland(win, nm);
                let ghost a1b = self.arena@;
                set_calling(&mut self.arena, e, false);
                assert forall|i: int| 0 <= i < self.arena@.len() implies #[trigger] node_ok(
                    self.arena@,
                    i,
                    self.n,
                ) by {
                    assert(node_ok(a1b, i, self.n));
                }
            }
            // ⭐ THE LINE R1 CANNOT HAVE. `zend_llist.c:190` re-reads
            // `element->next` here with no claim that `element` is still a live
            // element at all; `wf` is that claim, and it survives the callback
            // because the arena outlives every entry in it.
            assert(node_ok(self.arena@, e as int, self.n));
            proof {
                fuel = (fuel - 1) as nat;
            }
            element = nnext(&self.arena, e);
        }
    }

    /// `zend_llist_destroy` -- zend_llist.c:107-121.
    fn destroy(&mut self)
        requires
            wf(old(self).g()),
        ensures
            final(self).g() == s_destroy(old(self).g(), old(self).head, old(self).arena@.len()),
    {
        let ghost g0 = self.g();
        let ghost head0 = self.head;
        let ghost f0 = self.arena@.len();
        let mut current: u32 = self.head;
        let ghost mut fuel: nat = f0;
        while current != NIL
            invariant
                wf(self.g()),
                self.arena@.len() == g0.arena.len(),
                current == NIL || ((current as int) < self.arena@.len() && fuel + (
                current as int) >= self.arena@.len()),
                fuel <= f0,
                s_destroy(g0, head0, f0) == s_destroy(self.g(), current, fuel),
            decreases
                if current == NIL {
                    0int
                } else {
                    self.arena@.len() - current as int
                },
        {
            assert(node_ok(self.arena@, current as int, self.n));
            let next = nnext(&self.arena, current as usize);
            self.al.free(SZ_NAME);
            self.al.free(REQ_ELEM);
            proof {
                fuel = (fuel - 1) as nat;
            }
            current = next;
        }
        self.count = 0;
    }
}

// ---------------------------------------------------------------- kernel ----
/// The kernel once the four head words are decoded. Its own function so that
/// the DECODE obligation and the RUN obligation are two proof contexts rather
/// than one; `../unsafe.rs` carries the same split so R4 and R5 stay one
/// program. At `-O3` it inlines into `kernel`, which is the symbol the
/// `isolated` cells measure.
#[inline(always)]
fn run(win: &[u8], n: u32, trigger: u32, mode: u32, reuse: bool, post: u32) -> (r: u64)
    requires
        1 <= n <= 0x1000_0000,
        trigger <= n,
        post <= n,
        HEAD + (n as int) * SLOT <= win@.len(),
    ensures
        r == run_spec(win@, n, trigger, mode, reuse, post),
{
    // ⚠ `run_spec` is OPAQUE (`#[verifier::opaque]`) and revealed HERE and
    // nowhere else. Without that, `kernel`'s one-line body -- decode, then call
    // this -- blows the solver's budget: Z3 unfolds `llist_fold` into the whole
    // composition, unfolds four recursive spec functions inside it once each by
    // default fuel, and then tries to match that term tree against the same tree
    // with differently-spelled arguments. Opaque, the match is six arguments.
    proof {
        reveal(run_spec);
    }
    let mut t = Ticks {
        arena: Vec::with_capacity(n as usize),
        head: NIL,
        tail: NIL,
        count: 0,
        al: Alloc { cnt: [0u32; MAX_CACHED_MEMORY], n_alloc: 0, n_free: 0, n_hit: 0, bytes: 0 },
        fold: 0,
        visits: 0,
        dtors: 0,
        refusals: 0,
        n,
        trigger,
        mode,
        reuse,
        reuse_done: false,
    };
    let ghost g0 = t.g();
    // ⚠ `[0u32; 11]@` and `Seq::new(11, |i| 0u32)` are EXTENSIONALLY equal and
    // not syntactically, so the extensional step has to come FIRST or the
    // struct equality below cannot close.
    assert(t.al.cnt@ =~= Seq::new(MAX_CACHED_MEMORY as nat, |i: int| 0u32));
    assert(g0 == g_init(n, trigger, mode, reuse));
    assert(wf(g0));

    t.register_all(win, n);
    let ghost g1 = t.g();
    assert(g1 == s_regloop(g0, win@, 1, n, n as nat));

    t.apply(win);
    let ghost g2 = t.g();
    assert(g2 == s_apply(g1, win@, g1.head, g1.arena.len()));

    if post != 0 {
        t.unregister(win, post);
    }
    let ghost g3 = t.g();
    assert(g3 == if post != 0 {
        s_unreg(g2, win@, post)
    } else {
        g2
    });

    let mut acc: u64 = t.fold;
    acc = acc.wrapping_mul(31).wrapping_add(t.count);
    acc = acc.wrapping_mul(31).wrapping_add(t.dtors);
    acc = acc.wrapping_mul(31).wrapping_add(t.visits);
    acc = acc.wrapping_mul(31).wrapping_add(t.refusals);
    acc = acc.wrapping_mul(31).wrapping_add(n as u64);

    if t.reuse_done {
        t.al.free(REQ_ELEM);
    }
    let ghost g4 = t.g();
    assert(g4 == if g3.reuse_done {
        s_free(g3, REQ_ELEM)
    } else {
        g3
    });
    t.destroy();
    assert(t.g() == s_destroy(g4, g4.head, g4.arena.len()));
    acc ^ t.al.tally()
}

#[cfg_attr(slb_isolated, inline(never))]
fn kernel(buf: &[u8], off: usize, len: usize) -> (r: u64)
    requires
        off + len <= buf@.len(),
        24 <= len,
        len <= 268435456,
    ensures
        r == llist_fold(buf@, off as int, len as int),
{
    // Ghost only: `spec_slice_len` is what tells the solver a slice length fits
    // in a `usize`, which with `off + len <= buf@.len()` is what stops
    // `off + len` overflowing below.
    assert(buf@.len() == vstd::slice::spec_slice_len(buf));
    let win: &[u8] = subwin(buf, off, off + len);
    // Ghost only. `nmax` is a `usize` division cast to `u32`, and the whole
    // decode rests on that cast being LOSSLESS and on `nmax != 0` -- both of
    // which are division facts Z3 needs named. `lemma_div_decreases` gives
    // `nmax < len - 16 <= 268435440 < 2^32`; `lemma_div_is_ordered` gives
    // `2 = 8/4 <= (len - 16)/4` from `len >= 24`.
    proof {
        vstd::arithmetic::div_mod::lemma_div_decreases((len - HEAD) as int, SLOT as int);
        vstd::arithmetic::div_mod::lemma_div_is_ordered(8, (len - HEAD) as int, SLOT as int);
    }
    let nmax: u32 = ((len - HEAD) / SLOT) as u32;
    assert(nmax as int == ((len as int) - 16) / 4);
    assert(nmax >= 2);
    let n: u32 = 1 + (rd32(win, 0) % nmax);
    let trigger: u32 = rd32(win, 4) % (n + 1);
    let mode_w: u32 = rd32(win, 8);
    let post: u32 = rd32(win, 12) % (n + 1);
    run(win, n, trigger, mode_w % 4, (mode_w >> 16) & 1 == 1, post)
}

// ------------------------------------------------------ TRUSTED, item 10/10 --
// `&buf[off..off + len]`, spelled so Verus knows the view.
//
// ⚠ IT IS CALLED `subwin` AND NOT `slice_subrange`, AND THE NAME IS THE POINT.
// `check.py` step 5c-twin refuses a twin whose body CALLS the trusted item --
// it would re-use the axiom instead of re-deriving it -- and it matches by
// identifier, so a twin calling `vstd::slice::slice_subrange` reads as calling a
// trusted `slice_subrange` if the row's own item shares that name. Renaming the
// row's item is the repair; the twin below then really does re-derive the view
// equation from vstd's own CHECKED `&slice[i..j]`.
#[inline(always)]
#[verifier::external_body]
fn subwin(v: &[u8], i: usize, j: usize) -> (r: &[u8])
    requires
        i <= j <= v@.len(),
    ensures
        r@ == v@.subrange(i as int, j as int),
{
    &v[i..j]
}

#[cfg(slb_twin)]
fn slb_twin_subwin(v: &[u8], i: usize, j: usize) -> (r: &[u8])
    requires
        i <= j <= v@.len(),
    ensures
        r@ == v@.subrange(i as int, j as int),
{
    vstd::slice::slice_subrange(v, i, j)
}

// ---------------------------------------------------------------- driver ----
fn main() {
    let (n_iters, stride_w, bytes) = load_input();
    // SLB-DRIVER-BEGIN
    let n_blob: usize = bytes.len();
    let buf: &[u8] = bytes.as_slice();
    let mut acc: u64 = 0;
    if stride_w >= 24 && stride_w <= 268435456 && stride_w <= n_blob as u64 {
        let stride: usize = stride_w as usize;
        let nwin: u64 = (n_blob / stride) as u64;
        let mut it: u64 = 0;
        proof {
            vstd::arithmetic::div_mod::lemma_div_non_zero(n_blob as int, stride as int);
        }
        while it < n_iters
            invariant
                24 <= stride <= n_blob,
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
            assert(r == llist_fold(buf@, (k * stride) as int, stride as int));
            acc = acc.wrapping_mul(31).wrapping_add(r);
            it = it + 1;
        }
    }
    // SLB-DRIVER-END
    emit(acc);
}

} // verus!
