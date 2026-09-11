//! ph64 rung R3 -- safe Rust, tuned. The same list, the same walk, the same
//! visit order, the same allocator arithmetic and the same u64 as R2; no
//! `unsafe`. Four levers, all of them representation and none of them algorithm:
//!
//!   1. **`u32` NIL sentinel instead of `Option<u32>`.** `Option<u32>` has no
//!      niche, so it is 8 bytes where a `u32` is 4 -- and `Node` is touched
//!      three times per visited entry. `u32::MAX` is not a reachable index here
//!      because `n <= (len - 16) / 4` and `len` is a window.
//!   2. **`name: u64` instead of `[u8; 8]`.** `user_tick_function_compare`'s
//!      `zend_binary_zval_strcmp(func1, func2) == 0` on two 8-byte strings IS a
//!      64-bit equality; R2 spells it as the byte loop the C writes, R3 spells
//!      it as the comparison that loop computes. ⚠ The BYTE ORDER is fixed
//!      little-endian in both, so the two rungs agree on every window and not
//!      merely on this box.
//!   3. **`Vec::with_capacity(n)`.** `zend_llist_add_element` `pemalloc`s each
//!      element separately and R2's `Vec::new()` reallocates `log2(n)` times;
//!      the count is known before the first `register`. ⚠ This changes NO
//!      allocator counter: the modelled `Alloc` is `zend_alloc.c`'s cache and is
//!      driven by the SAME request sequence in every rung. What it changes is
//!      Rust's own heap traffic, which the C rung does not have at all.
//!   4. **the loop bodies hoist the arena index once** instead of re-indexing
//!      `self.arena[e]` three times per visit.
//!
//! ⚠ NOT a lever, deliberately: the walk still follows `next`. Replacing it
//! with `for i in 0..n { if live[i] { .. } }` -- which computes the same answer,
//! because arena indices ascend along the list -- would be a DIFFERENT ALGORITHM
//! and would make the R1-vs-R3 comparison meaningless. `../NOTES.md` §8 records
//! that scan as an unbuilt R3 candidate and says why it is out of contract.

#[path = "../../common/driver.rs"]
mod driver;

const HEAD: usize = 16;
const SLOT: usize = 4;
const SZ_NAME: usize = 8;
const REQ_ELEM: usize = 39;
const MAX_CACHED_MEMORY: usize = 11;
const MAX_CACHED_ENTRIES: u32 = 256;
const NIL: u32 = u32::MAX;

const UNREG_SELF: u32 = 1;
const UNREG_AHEAD: u32 = 2;
const UNREG_BEHIND: u32 = 3;

/// `zend_alloc.c`'s size-class cache, counters only. Identical arithmetic to
/// R2's; see that file for the line citations.
struct Alloc {
    cnt: [u32; MAX_CACHED_MEMORY],
    n_alloc: u64,
    n_free: u64,
    n_hit: u64,
    bytes: u64,
}

impl Alloc {
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
    #[inline(always)]
    fn free(&mut self, size: usize) {
        let rsz: usize = (size + 7) & !7usize;
        let idx: usize = rsz >> 3;
        self.n_free = self.n_free.wrapping_add(1);
        if idx < MAX_CACHED_MEMORY && self.cnt[idx] < MAX_CACHED_ENTRIES {
            self.cnt[idx] += 1;
        }
    }
    #[inline(always)]
    fn tally(&self) -> u64 {
        self.n_alloc.wrapping_mul(1000003)
            ^ self.n_free.wrapping_mul(1000033)
            ^ self.n_hit.wrapping_mul(1000037)
            ^ self.bytes.wrapping_mul(1000039)
    }
}

struct Node {
    next: u32,
    prev: u32,
    name: u64,
    calling: bool,
}

struct Ticks {
    arena: Vec<Node>,
    head: u32,
    tail: u32,
    count: u64,
    al: Alloc,
    fold: u64,
    visits: u64,
    dtors: u64,
    refusals: u64,
    n: u32,
    trigger: u32,
    mode: u32,
    reuse: bool,
    reuse_done: bool,
}

#[inline(always)]
fn rd32(win: &[u8], i: usize) -> u32 {
    (win[i] as u32) | ((win[i + 1] as u32) << 8)
        | ((win[i + 2] as u32) << 16) | ((win[i + 3] as u32) << 24)
}

/// Entry `id`'s `arguments[0]` as the 64-bit value the comparison really is:
/// the low half is the id, the high half is the window slot.
#[inline(always)]
fn name_of(win: &[u8], id: u32) -> u64 {
    let s: usize = HEAD + (id as usize - 1) * SLOT;
    (id as u64) | ((rd32(win, s) as u64) << 32)
}

impl Ticks {
    fn new(n: u32, trigger: u32, mode: u32, reuse: bool) -> Ticks {
        Ticks { arena: Vec::with_capacity(n as usize), head: NIL, tail: NIL,
                count: 0,
                al: Alloc { cnt: [0u32; MAX_CACHED_MEMORY], n_alloc: 0,
                            n_free: 0, n_hit: 0, bytes: 0 },
                fold: 0, visits: 0, dtors: 0, refusals: 0,
                n, trigger, mode, reuse, reuse_done: false }
    }

    fn register(&mut self, win: &[u8], id: u32) {
        self.al.alloc(SZ_NAME);
        let name = name_of(win, id);
        self.al.alloc(REQ_ELEM);
        let ix: u32 = self.arena.len() as u32;
        let t = self.tail;
        self.arena.push(Node { next: NIL, prev: t, name, calling: false });
        if t != NIL {
            self.arena[t as usize].next = ix;
        } else {
            self.head = ix;
        }
        self.tail = ix;
        self.count = self.count.wrapping_add(1);
    }

    /// `zend_llist_del_element` + `DEL_LLIST_ELEMENT` + the comparator,
    /// INCLUDING `562f886ecb14`'s guard.
    fn del_element(&mut self, key: u64) {
        let mut current = self.head;
        while current != NIL {
            let c = current as usize;
            let next = self.arena[c].next;
            let ret: bool = self.arena[c].name == key;
            if ret && self.arena[c].calling {
                self.refusals = self.refusals.wrapping_add(1);
                current = next;
            } else if ret {
                let p = self.arena[c].prev;
                let nx = self.arena[c].next;
                if p != NIL {
                    self.arena[p as usize].next = nx;
                } else {
                    self.head = nx;
                }
                if nx != NIL {
                    self.arena[nx as usize].prev = p;
                } else {
                    self.tail = p;
                }
                self.dtors = self.dtors.wrapping_add(1);
                self.al.free(SZ_NAME);
                self.al.free(REQ_ELEM);
                self.count = self.count.wrapping_sub(1);
                return;
            } else {
                current = next;
            }
        }
    }

    fn unregister(&mut self, win: &[u8], id: u32) {
        self.al.alloc(SZ_NAME);
        let key = name_of(win, id);
        self.del_element(key);
        self.al.free(SZ_NAME);
    }

    fn userland(&mut self, win: &[u8], nm: u64) {
        let me: u32 = nm as u32;
        self.fold = self.fold.wrapping_mul(31).wrapping_add(me as u64);
        self.fold = self.fold.wrapping_mul(31).wrapping_add(nm >> 32);
        self.visits = self.visits.wrapping_add(1);
        if me != self.trigger {
            return;
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

    /// `zend_llist_apply` -- zend_llist.c:186-193. THE PRIMARY SPAN.
    fn apply(&mut self, win: &[u8]) {
        let mut element = self.head;
        while element != NIL {
            let e = element as usize;
            if !self.arena[e].calling {
                self.arena[e].calling = true;
                let nm = self.arena[e].name;
                self.userland(win, nm);
                self.arena[e].calling = false;
            }
            element = self.arena[e].next;
        }
    }

    fn destroy(&mut self) {
        let mut current = self.head;
        while current != NIL {
            let next = self.arena[current as usize].next;
            self.al.free(SZ_NAME);
            self.al.free(REQ_ELEM);
            current = next;
        }
        self.count = 0;
    }
}

#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    let win: &[u8] = &buf[off..off + len];
    let nmax: u32 = ((len - HEAD) / SLOT) as u32;
    let n: u32 = 1 + (rd32(win, 0) % nmax);
    let trigger: u32 = rd32(win, 4) % (n + 1);
    let mode_w: u32 = rd32(win, 8);
    let post: u32 = rd32(win, 12) % (n + 1);

    let mut t = Ticks::new(n, trigger, mode_w % 4, (mode_w >> 16) & 1 == 1);
    let mut i: u32 = 1;
    while i <= n {
        t.register(win, i);
        i += 1;
    }

    t.apply(win);

    if post != 0 {
        t.unregister(win, post);
    }

    let mut acc: u64 = t.fold;
    acc = acc.wrapping_mul(31).wrapping_add(t.count);
    acc = acc.wrapping_mul(31).wrapping_add(t.dtors);
    acc = acc.wrapping_mul(31).wrapping_add(t.visits);
    acc = acc.wrapping_mul(31).wrapping_add(t.refusals);
    acc = acc.wrapping_mul(31).wrapping_add(n as u64);

    if t.reuse_done {
        t.al.free(REQ_ELEM);
    }
    t.destroy();
    acc ^ t.al.tally()
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
    if stride_w >= 24 && stride_w <= 268435456 && stride_w <= n_blob as u64 {
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
