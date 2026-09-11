//! ph64 rung R4 -- R3 with the arena's bounds checks removed. Same list, same
//! walk, same visit order, same allocator arithmetic, same u64.
//!
//! ⚠⚠ WHAT IS ACTUALLY UNCHECKED HERE, AND IT IS THE ROW'S POINT.
//! Every `unsafe` in this file is ONE fact: `i < arena.len()`. There is nothing
//! to make unsafe about the thing R1 gets wrong -- `element->next` after the
//! callback freed `element` -- because in an index arena that read is in bounds
//! WHATEVER the callback did. ⭐ So R4 is not "R3 with the dangerous check
//! removed": on this row there is no such check to remove, and the fact R1
//! violates is a LIFETIME fact that safe Rust removed by changing the
//! representation, not by testing anything. `../NOTES.md` §9.
//!
//! The seven arena accessors below are the exact shape `verus.rs` wraps, one for one,
//! so R4 and R5 differ in the proof and in nothing else. Their preconditions --
//! `i < arena.len()` for every one -- are what R5 discharges, and they are
//! discharged from a SINGLE invariant: every live link is an index below
//! `arena.len()`, and `arena` only ever grows.

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

pub struct Node {
    pub next: u32,
    pub prev: u32,
    pub name: u64,
    pub calling: bool,
}

// ------------------------------------------------------- the seven accessors
// Each one's obligation is `i < v.len()`. verus.rs wraps exactly these bodies.
#[inline(always)]
fn nnext(v: &Vec<Node>, i: usize) -> u32 {
    unsafe { v.get_unchecked(i).next }
}
#[inline(always)]
fn nprev(v: &Vec<Node>, i: usize) -> u32 {
    unsafe { v.get_unchecked(i).prev }
}
#[inline(always)]
fn nname(v: &Vec<Node>, i: usize) -> u64 {
    unsafe { v.get_unchecked(i).name }
}
#[inline(always)]
fn ncalling(v: &Vec<Node>, i: usize) -> bool {
    unsafe { v.get_unchecked(i).calling }
}
#[inline(always)]
fn set_next(v: &mut Vec<Node>, i: usize, x: u32) {
    unsafe { v.get_unchecked_mut(i).next = x; }
}
#[inline(always)]
fn set_prev(v: &mut Vec<Node>, i: usize, x: u32) {
    unsafe { v.get_unchecked_mut(i).prev = x; }
}
#[inline(always)]
fn set_calling(v: &mut Vec<Node>, i: usize, x: bool) {
    unsafe { v.get_unchecked_mut(i).calling = x; }
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
            set_next(&mut self.arena, t as usize, ix);
        } else {
            self.head = ix;
        }
        self.tail = ix;
        self.count = self.count.wrapping_add(1);
    }

    /// The registration phase. Its own method so R4 and R5 are one program;
    /// see `../verus.rs::register_all` for why the proof wants it split out.
    fn register_all(&mut self, win: &[u8], n: u32) {
        let mut i: u32 = 1;
        while i <= n {
            self.register(win, i);
            i = i + 1;
        }
    }

    /// `zend_llist_del_element` -- zend_llist.c:91-104. `break`, not `return`:
    /// `:101` breaks out of its own `while`, which is also the single exit
    /// `../verus.rs`'s loop `ensures` needs.
    fn del_element(&mut self, key: u64) {
        let mut current = self.head;
        while current != NIL {
            let c = current as usize;
            let next = nnext(&self.arena, c);
            let ret: bool = nname(&self.arena, c) == key;
            if ret && ncalling(&self.arena, c) {
                self.refusals = self.refusals.wrapping_add(1);                   // 562f886ecb14
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
                break;
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
            if !ncalling(&self.arena, e) {
                set_calling(&mut self.arena, e, true);
                let nm = nname(&self.arena, e);
                self.userland(win, nm);
                set_calling(&mut self.arena, e, false);
            }
            element = nnext(&self.arena, e);
        }
    }

    fn destroy(&mut self) {
        let mut current = self.head;
        while current != NIL {
            let next = nnext(&self.arena, current as usize);
            self.al.free(SZ_NAME);
            self.al.free(REQ_ELEM);
            current = next;
        }
        self.count = 0;
    }
}

/// The kernel once the four head words are decoded. Its own function so that
/// R4 and R5 are one program; see `../verus.rs::run` for why the proof wants
/// the split. At `-O3` it inlines into `kernel`.
#[inline(always)]
fn run(win: &[u8], n: u32, trigger: u32, mode: u32, reuse: bool, post: u32) -> u64 {
    let mut t = Ticks::new(n, trigger, mode, reuse);
    t.register_all(win, n);

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

#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    let win: &[u8] = &buf[off..off + len];
    let nmax: u32 = ((len - HEAD) / SLOT) as u32;
    let n: u32 = 1 + (rd32(win, 0) % nmax);
    let trigger: u32 = rd32(win, 4) % (n + 1);
    let mode_w: u32 = rd32(win, 8);
    let post: u32 = rd32(win, 12) % (n + 1);
    run(win, n, trigger, mode_w % 4, (mode_w >> 16) & 1 == 1, post)
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
