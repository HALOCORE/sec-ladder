//! ph64 rung R2 -- safe Rust, naive. A direct transcription of
//! `zend_llist_apply` and the four `basic_functions.c` tick frames, with no
//! `unsafe`, written the way somebody porting the C would write it: a real
//! doubly-linked list, `Option<u32>` links, index by index, no iterator
//! adaptors and no subslicing.
//!
//! ============================================================================
//! ⚠⚠⚠ WHAT R2-R5 ARE, AND WHAT SAFE RUST BUYS ON *THIS* ROW
//! ============================================================================
//! `.memory-php/02-ladder.md`: *"the hardened C rung carries the historical fix,
//! the Rust rungs carry whatever is actually memory-safe."* On this row the fix
//! is COMPLETE on the tick list (`../NOTES.md` §4), so R2-R5 implement exactly
//! `../c/kernel_hardened.c`'s function -- `562f886ecb14`'s guard included --
//! and only R1 diverges.
//!
//! ⭐⭐ **AND THE HONEST ANSWER TO "WHAT DOES SAFE RUST BUY HERE" IS NOT
//! "SAFETY". IT IS A REPRESENTATION CHANGE, AND THE ROW REPORTS THAT RATHER
//! THAN HIDING IT.** C's `zend_llist_element *next` is a raw pointer into the
//! heap, so `element = element->next` after the callback freed `element` is a
//! use-after-free. Safe Rust cannot express that list at all without `Rc`,
//! `RefCell` or raw pointers, so the faithful safe port is an **index arena**:
//! `next` becomes a `u32` into a `Vec<Node>` the kernel owns, and "free"
//! becomes "unlink". A dangling index is then an ORDINARY IN-BOUNDS READ of a
//! slot that is still there -- which is, to the byte, what PHP 5.0.0's
//! size-class cache does with the real block (`../c/kernel.h`).
//!
//! ⚠⚠ So on this row **safe Rust does not turn the defect into a panic. It
//! turns it into a WRONG ANSWER**, and the thing that removes it is
//! `562f886ecb14`'s guard, which is a LOGICAL invariant and not a bounds check.
//! *"Safe Rust reproduces the bug"* is a FINDING, never a kill
//! (`PROTOCOL_PHP.md`, `CLAUDE.md` Don't 6), and it is this row's sharpest
//! result. `../NOTES.md` §9 states it, and `../controls/arena_r1.rs` builds the
//! guard-less safe rung and measures exactly what it returns.
//!
//! ⚠ WHAT THE ARENA DOES CHANGE, DECLARED: `zend_llist_add_element` appends at
//! the tail, so arena indices are ASCENDING along the list and stay ascending
//! under `DEL_LLIST_ELEMENT` (it only ever short-circuits `prev -> next`). The
//! C's element ADDRESSES have no such order -- the size-class cache hands blocks
//! back in LIFO order. The visit sequence, the fold and the allocator tally are
//! identical either way; what the arena buys is a `decreases` clause for R5, and
//! `../spec.md`'s `provenance.divergences` says so rather than leaving it to be
//! noticed.
//!
//! ⚠ The Rust rungs do NOT link `emalloc_shim.h`. They reproduce
//! `php_shim_tally()` ARITHMETICALLY from the same request sequence -- and they
//! must model the SIZE-CLASS CACHE, because this row's u64 depends on
//! `n_cache_hit` and `bytes_mallocked`, i.e. on which requests were served from
//! the cache. ⭐ What they do NOT need is the block's IDENTITY: which block comes
//! back out is observable only through a dangling pointer, and R1h has none.

#[path = "../../common/driver.rs"]
mod driver;

/// The window's head, in bytes: `[u32 nent][u32 trig][u32 mode][u32 post]`.
const HEAD: usize = 16;
/// Window bytes per registered tick function.
const SLOT: usize = 4;
/// `safe_emalloc(sizeof(zval *), 1, 0)` -- basic_functions.c:2811, :2857.
const SZ_NAME: usize = 8;
/// `sizeof(zend_llist_element) + l->size - 1` -- zend_llist.c:39, with
/// `l->size == sizeof(user_tick_function_entry)`. 24 + 16 - 1.
const REQ_ELEM: usize = 39;
/// `zend_alloc.h:63-64`.
const MAX_CACHED_MEMORY: usize = 11;
const MAX_CACHED_ENTRIES: u32 = 256;

const UNREG_SELF: u32 = 1;
const UNREG_AHEAD: u32 = 2;
const UNREG_BEHIND: u32 = 3;

/// `zend_alloc.c`'s size-class cache, counters only. `php_shim_reset()` at the
/// top of every kernel call empties it, so a `Ticks` starts here.
struct Alloc {
    cnt: [u32; MAX_CACHED_MEMORY],
    n_alloc: u64,
    n_free: u64,
    n_hit: u64,
    bytes: u64,
}

impl Alloc {
    fn new() -> Alloc {
        Alloc { cnt: [0u32; MAX_CACHED_MEMORY], n_alloc: 0, n_free: 0, n_hit: 0,
                bytes: 0 }
    }
    /// `_emalloc` -- zend_alloc.c:142-217. `REAL_SIZE(size)` then the cache arm.
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
    /// `_efree` -- zend_alloc.c:248-289. ⚠ The index comes from the RECORDED
    /// size (`p->size`, zend_alloc.h:53), which for every request this kernel
    /// makes is the size that was asked for.
    fn free(&mut self, size: usize) {
        let rsz: usize = (size + 7) & !7usize;
        let idx: usize = rsz >> 3;
        self.n_free = self.n_free.wrapping_add(1);
        if idx < MAX_CACHED_MEMORY && self.cnt[idx] < MAX_CACHED_ENTRIES {
            self.cnt[idx] += 1;
        }
    }
    /// `php_shim_tally()` -- common-php/emalloc_shim.h:642-648.
    fn tally(&self) -> u64 {
        self.n_alloc.wrapping_mul(1000003)
            ^ self.n_free.wrapping_mul(1000033)
            ^ self.n_hit.wrapping_mul(1000037)
            ^ self.bytes.wrapping_mul(1000039)
    }
}

/// `zend_llist_element` (zend_llist.h:25-29) with the
/// `user_tick_function_entry` (basic_functions.c:154-158) that lives in its
/// `data[]`. `arguments` is the 8-byte name; `arg_count` is 1 on every entry
/// this kernel builds and is not carried.
struct Node {
    next: Option<u32>,
    prev: Option<u32>,
    name: [u8; SZ_NAME],
    calling: bool,
}

/// `zend_llist` (zend_llist.h:37-45) plus the projected userland's state.
struct Ticks {
    arena: Vec<Node>,
    head: Option<u32>,
    tail: Option<u32>,
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

fn rd32(win: &[u8], i: usize) -> u32 {
    (win[i] as u32) | ((win[i + 1] as u32) << 8)
        | ((win[i + 2] as u32) << 16) | ((win[i + 3] as u32) << 24)
}

/// Entry `id`'s `arguments[0]`: `[u32 le id][slot id]`. The id half makes names
/// unique BY CONSTRUCTION.
fn name_of(win: &[u8], id: u32) -> [u8; SZ_NAME] {
    let s: usize = HEAD + (id as usize - 1) * SLOT;
    [(id & 0xFF) as u8, ((id >> 8) & 0xFF) as u8, ((id >> 16) & 0xFF) as u8,
     ((id >> 24) & 0xFF) as u8, win[s], win[s + 1], win[s + 2], win[s + 3]]
}

impl Ticks {
    /// `zend_llist_init` -- zend_llist.c:26-34.
    fn new(n: u32, trigger: u32, mode: u32, reuse: bool) -> Ticks {
        Ticks { arena: Vec::new(), head: None, tail: None, count: 0,
                al: Alloc::new(), fold: 0, visits: 0, dtors: 0, refusals: 0,
                n, trigger, mode, reuse, reuse_done: false }
    }

    /// `PHP_FUNCTION(register_tick_function)` -- basic_functions.c:2799-2835,
    /// narrowed to the entry construction and the `add_element`.
    fn register(&mut self, win: &[u8], id: u32) {
        self.al.alloc(SZ_NAME);                       // :2811
        let name = name_of(win, id);
        self.al.alloc(REQ_ELEM);                      // zend_llist.c:39
        let ix: u32 = self.arena.len() as u32;
        self.arena.push(Node { next: None, prev: self.tail, name,
                               calling: false });
        match self.tail {
            Some(t) => self.arena[t as usize].next = Some(ix),
            None => self.head = Some(ix),
        }
        self.tail = Some(ix);
        self.count = self.count.wrapping_add(1);
    }

    /// `zend_llist_del_element` (zend_llist.c:91-104) expanding
    /// `DEL_LLIST_ELEMENT` (:73-88), with `user_tick_function_compare`
    /// (basic_functions.c:2146-2161) inlined -- INCLUDING `562f886ecb14`'s
    /// guard, which is what makes the whole walk safe.
    fn del_element(&mut self, key: [u8; SZ_NAME]) {
        let mut current = self.head;
        while let Some(c) = current {
            let next = self.arena[c as usize].next;
            // user_tick_function_compare, narrowed.
            let mut d: bool = false;
            let mut i: usize = 0;
            while i < SZ_NAME {
                if self.arena[c as usize].name[i] != key[i] {
                    d = true;
                    break;
                }
                i += 1;
            }
            let ret: bool = !d;
            // ⭐ 562f886ecb14, the WHOLE hunk. `tick_fe1` is the LIST element,
            // never the search key -- which is why the predicate is sound.
            if ret && self.arena[c as usize].calling {
                self.refusals = self.refusals.wrapping_add(1);                   // php_error_docref, projected
            } else if ret {
                let p = self.arena[c as usize].prev;
                let nx = self.arena[c as usize].next;
                match p {                             // :74-78
                    Some(pp) => self.arena[pp as usize].next = nx,
                    None => self.head = nx,
                }
                match nx {                            // :79-83
                    Some(nn) => self.arena[nn as usize].prev = p,
                    None => self.tail = p,
                }
                self.dtors = self.dtors.wrapping_add(1);                      // :84-86 l->dtor(data)
                self.al.free(SZ_NAME);                // user_tick_function_dtor
                self.al.free(REQ_ELEM);               // :87 pefree(current)
                self.count = self.count.wrapping_sub(1);                      // :88
                return;
            }
            current = next;
        }
    }

    /// `PHP_FUNCTION(unregister_tick_function)` -- basic_functions.c:2840-2862.
    fn unregister(&mut self, win: &[u8], id: u32) {
        self.al.alloc(SZ_NAME);                       // :2857
        let key = name_of(win, id);
        self.del_element(key);                        // :2860
        self.al.free(SZ_NAME);                        // :2861
    }

    /// `call_user_function` -- basic_functions.c:2111-2116, projected. The name
    /// is passed BY VALUE: a PHP tick function holds its own name in the
    /// executor's frame, not in the tick entry.
    fn userland(&mut self, win: &[u8], nm: [u8; SZ_NAME]) {
        let me: u32 = rd32(&nm, 0);
        self.fold = self.fold.wrapping_mul(31).wrapping_add(me as u64);
        self.fold = self.fold.wrapping_mul(31)
            .wrapping_add(rd32(&nm, 4) as u64);
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

    /// `zend_llist_apply` -- zend_llist.c:186-193. ⚠⚠ THE PRIMARY SPAN. The
    /// cursor advances AFTER the callback, out of the node the callback was
    /// allowed to unlink -- and in C, to free.
    fn apply(&mut self, win: &[u8]) {
        let mut element = self.head;
        while let Some(e) = element {
            if !self.arena[e as usize].calling {      // :2108
                self.arena[e as usize].calling = true;   // :2109
                let nm = self.arena[e as usize].name;
                self.userland(win, nm);               // :2111-2116
                self.arena[e as usize].calling = false;  // :2135  SITE C
            }
            element = self.arena[e as usize].next;    // :190     SITE L
        }
    }

    /// `zend_llist_destroy` -- zend_llist.c:107-121.
    fn destroy(&mut self) {
        let mut current = self.head;
        while let Some(c) = current {
            let next = self.arena[c as usize].next;
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

    t.apply(win);                                     // run_user_tick_functions

    if post != 0 {
        t.unregister(win, post);                      // top-level userland
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
