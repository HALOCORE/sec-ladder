//! ph66 rung R2 -- safe Rust, naive. A direct transcription of PHP 5.0.0's
//! `Zend/zend_hash.c` container, with no `unsafe`, written the way somebody
//! porting the C would write it: a real bucket arena with real chain and global
//! links, `Option<u32>` for every link, index by index, no iterator adaptors
//! and no subslicing.
//!
//! ============================================================================
//! ⚠⚠⚠ WHAT R2-R5 ARE, AND WHAT SAFE RUST BUYS ON *THIS* ROW
//! ============================================================================
//! `.memory-php/02-ladder.md`: *"the hardened C rung carries the historical fix,
//! the Rust rungs carry whatever is actually memory-safe."*
//!
//! ⭐⭐⭐ **ON THIS ROW THAT SENTENCE HAS A STARK ANSWER: `c/kernel.c` IS
//! ALREADY MEMORY-SAFE.** Its defect is a WRONG BOOLEAN. Every free in
//! `zend_hash_del_key_or_index` is a correct free of a bucket that has just
//! been unlinked from both lists and from `pInternalPointer`; nothing reads it
//! afterwards. So there is nothing here for safe Rust to refuse, and R2, R3, R4
//! and R5 all implement **`c/kernel.c`'s function** -- the DEFECTIVE predicate
//! included -- and only `c/kernel_hardened.c` differs.
//!
//! ⚠⚠ *"Safe Rust reproduces the bug bit-identically"* is a **FINDING, never a
//! kill** (`CLAUDE.md` Don't 6, `PROTOCOL_PHP.md`), and on this row it is the
//! result the row exists to produce: ../NOTES.md section 7 puts R1..R5's
//! adversarial folds side by side, and `../controls/ladder.py` measures them
//! rather than asserting them. A ladder whose every rung buys safety is a
//! ladder that has never measured a defect the rungs do not address.
//!
//! ⚠ WHAT THE ARENA DOES CHANGE, DECLARED. C's `Bucket *pNext` is a raw
//! pointer; safe Rust cannot express two intrusive doubly-linked lists over one
//! heap without `Rc`, `RefCell` or raw pointers, so the faithful safe port owns
//! an arena and links by `u32` index, and "free" becomes "unlink and stop being
//! reachable". ⭐ That substitution is INVISIBLE HERE in a way it was not on
//! `ph64`: that row's cursor read a link out of a freed block, so the arena
//! changed what the read returned. This row never reads a freed bucket at all,
//! so the arena changes nothing observable and the two rungs compute the same
//! function for the same reason. ../spec.md's `provenance.divergences` says so.
//!
//! ⚠ The Rust rungs do NOT link `emalloc_shim.h`. They reproduce
//! `php_shim_tally()` ARITHMETICALLY from the same request sequence, and they
//! must model the SIZE-CLASS CACHE because the u64 carries `n_cache_hit` and
//! `bytes_mallocked`. ⭐ What they do NOT need is the block's IDENTITY: which
//! block comes back out of the cache is observable only through a dangling
//! pointer, and this row has none on any rung.

#[path = "../../common/driver.rs"]
mod driver;

/// Bytes per key-stream record -- `../c/kernel.h`'s `PH66_REC`.
const REC: usize = 4;
/// `sel = b[1] & 63` -- 64 distinct string keys.
const NKEY: u32 = 64;
/// `sizeof(Bucket) - 1` on LP64, asserted at compile time in `../c/kernel.c`.
const BUCKET_BASE: usize = 71;
/// `zend_alloc.h:63-64`.
const MAX_CACHED_MEMORY: usize = 11;
const MAX_CACHED_ENTRIES: u32 = 256;

/// `zend_alloc.c`'s size-class cache, counters only. `php_shim_reset()` at the
/// top of every kernel call empties it, so an `Ht` starts here.
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

/// `Bucket` (zend_hash.h:48-58). ⚠ There is no `req` field and there does not
/// need to be: `_efree` classes a block by its RECORDED size, and both of this
/// kernel's allocation sites request `sizeof(Bucket) - 1 + nKeyLength` --
/// `:239` explicitly, `:383` as the `nKeyLength == 0` case of the same
/// expression -- so the recorded size is `BUCKET_BASE + nkl` on every bucket.
struct Node {
    h: u64,
    nkl: u32,
    k: u64,
    data: u64,
    nxt: Option<u32>,
    lst: Option<u32>,
    lnxt: Option<u32>,
    llst: Option<u32>,
}

/// `HashTable` (zend_hash.h:60-78) plus the projected `ZVAL_PTR_DTOR` counters.
struct Ht {
    a: Vec<Node>,
    ar: Vec<Option<u32>>,
    mask: u64,
    lhead: Option<u32>,
    ltail: Option<u32>,
    iptr: Option<u32>,
    nelem: u64,
    nnext: u64,
    ndtor: u64,
    dfold: u64,
    ndok: u64,
    ndfail: u64,
    al: Alloc,
}

/// `_zend_hash_init`'s `while ((1U << i) < nSize) i++;` from `i = 3`.
fn table_size(nrec: usize) -> usize {
    let mut i: u32 = 3;
    while (1usize << i) < nrec {
        i += 1;
    }
    1usize << i
}

/// The `sel`-th string key, packed little-endian into one `u64`, and its
/// `nKeyLength` -- NUL INCLUDED (`Zend/zend_execute.c:3612` passes
/// `varname->value.str.len + 1`).
///
/// ⚠⚠ THE PACKING IS A DECLARED DIVERGENCE AND IT IS EXACT. C carries
/// `char arKey[1]` and compares with `memcmp(p->arKey, arKey, nKeyLength)`;
/// here the key is one word, ZERO-FILLED past `nKeyLength`, and the comparison
/// is `==` on the word. The two agree because every site that compares keys --
/// `:215`, `:465`, and the hardened `:463` -- already requires
/// `p->nKeyLength == nKeyLength` first, and two zero-filled words with equal
/// length agree on all eight bytes exactly when they agree on the first
/// `nKeyLength`. `../spec.md`'s `provenance.divergences` states it and
/// `../controls/differential.py` measures the whole rung against the C.
fn key_of(sel: u32) -> (u64, u32) {
    let kl: usize = 1 + (sel % 7) as usize;
    let mut k: u64 = 0;
    let mut i: usize = 0;
    while i < kl {
        let c: u64 = (97u32 + (((sel / 7) * 5 + (i as u32) * 7) % 26)) as u64;
        k |= c << (8 * i);
        i += 1;
    }
    (k, (kl + 1) as u32)
}

/// Byte `i` of a packed key -- what `p->arKey[i]` reads.
fn kbyte(k: u64, i: usize) -> u64 {
    (k >> (8 * i)) & 0xFF
}

/// `zend_inline_hash_func` (zend_hash.h:243-271), rolled. ⚠ `hash * 33` IS
/// `(hash << 5) + hash`, and upstream's eightfold unrolling is an unrolling and
/// not a different function -- ../spec.md's divergence ledger says so and
/// `../controls/differential.py` measures the two against each other.
fn hash_of(k: u64, nkl: u32) -> u64 {
    let mut h: u64 = 5381;
    let mut i: usize = 0;
    while i < nkl as usize {
        h = h.wrapping_mul(33).wrapping_add(kbyte(k, i));
        i += 1;
    }
    h
}

impl Ht {
    /// `_zend_hash_init` -- zend_hash.c:135-174.
    fn new(nrec: usize) -> Ht {
        let ts = table_size(nrec);
        let mut al = Alloc::new();
        al.alloc(8 * ts); // ecalloc(nTableSize, sizeof(Bucket *))
        Ht { a: Vec::new(), ar: vec![None; ts], mask: (ts - 1) as u64,
             lhead: None, ltail: None, iptr: None, nelem: 0, nnext: 0,
             ndtor: 0, dfold: 0, ndok: 0, ndfail: 0, al }
    }

    /// `ZVAL_PTR_DTOR` -> `_zval_ptr_dtor`, projected to a count and a fold.
    fn dtor(&mut self, v: u64) {
        self.ndtor = self.ndtor.wrapping_add(1);
        self.dfold = self.dfold.wrapping_mul(31).wrapping_add(v & 0xFFFF);
    }

    /// `CONNECT_TO_BUCKET_DLLIST` then `CONNECT_TO_GLOBAL_DLLIST` then
    /// `ht->arBuckets[nIndex] = p` -- zend_hash.c:24-42, in the C's own order.
    fn connect(&mut self, i: u32, n_index: usize) {
        let head = self.ar[n_index];
        self.a[i as usize].nxt = head;
        self.a[i as usize].lst = None;
        match head {
            Some(x) => self.a[x as usize].lst = Some(i),
            None => {}
        }
        let tail = self.ltail;
        self.a[i as usize].llst = tail;
        self.ltail = Some(i);
        self.a[i as usize].lnxt = None;
        match tail {
            Some(x) => self.a[x as usize].lnxt = Some(i),
            None => {}
        }
        if self.lhead.is_none() {
            self.lhead = Some(i);
        }
        if self.iptr.is_none() {
            self.iptr = Some(i);
        }
        self.ar[n_index] = Some(i);
        self.nelem = self.nelem.wrapping_add(1);
    }

    /// `_zend_hash_add_or_update(..., HASH_UPDATE)` -- zend_hash.c:192-263.
    /// ⭐ Its predicate is the REPAIR'S OWN FORM already: `p->h == h` AND
    /// `p->nKeyLength == nKeyLength` as required conjuncts.
    fn ins_str(&mut self, key: u64, nkl: u32, data: u64) {
        let h = hash_of(key, nkl);
        let n_index = (h & self.mask) as usize;
        let mut p = self.ar[n_index];
        while let Some(c) = p {
            if self.a[c as usize].h == h && self.a[c as usize].nkl == nkl
                && self.a[c as usize].k == key
            {
                let old = self.a[c as usize].data;
                self.dtor(old);
                self.a[c as usize].data = data;
                return;
            }
            p = self.a[c as usize].nxt;
        }
        self.al.alloc(BUCKET_BASE + nkl as usize);
        let ix: u32 = self.a.len() as u32;
        self.a.push(Node { h, nkl, k: key, data,
                           nxt: None, lst: None, lnxt: None, llst: None });
        self.connect(ix, n_index);
    }

    /// `_zend_hash_index_update_or_next_insert(..., HASH_UPDATE)` -- :339-402.
    /// ⭐⭐ `p->h = h` at `:388` stores THE RAW USER INDEX, which is what makes
    /// the collision constructible by running the hash FORWARDS.
    fn ins_idx(&mut self, h: u64, data: u64) {
        let n_index = (h & self.mask) as usize;
        let mut p = self.ar[n_index];
        let mut hit = false;
        while let Some(c) = p {
            if self.a[c as usize].nkl == 0 && self.a[c as usize].h == h {
                let old = self.a[c as usize].data;
                self.dtor(old);
                self.a[c as usize].data = data;
                hit = true;
                break;
            }
            p = self.a[c as usize].nxt;
        }
        if !hit {
            self.al.alloc(BUCKET_BASE);
            let ix: u32 = self.a.len() as u32;
            self.a.push(Node { h, nkl: 0, k: 0, data,
                               nxt: None, lst: None, lnxt: None, llst: None });
            self.connect(ix, n_index);
        }
        if (h as i64) >= (self.nnext as i64) {
            self.nnext = h.wrapping_add(1);
        }
    }

    /// `zend_hash_del_key_or_index` -- zend_hash.c:450-503. ⚠⚠⚠ THE PRIMARY
    /// SPAN, and `:464`'s DISJUNCT is transcribed exactly as it stands.
    /// `del_key == false` is the `HASH_DEL_INDEX` call (`arKey == NULL`,
    /// `nKeyLength == 0`).
    fn del(&mut self, key: u64, nkl: u32, h0: u64, del_key: bool) {
        let h = if del_key { hash_of(key, nkl) } else { h0 };
        let n_index = (h & self.mask) as usize;
        let mut p = self.ar[n_index];
        while let Some(c) = p {
            // ⛔ THE DEFECT. `p->nKeyLength == 0` is a DISJUNCT, so a numeric
            // bucket matches on hash equality alone and the key is never
            // compared. `c/kernel_hardened.c` hoists the length test in front
            // of the `||`; this rung does not, because this rung is R1's
            // function.
            let hit = self.a[c as usize].h == h
                && (self.a[c as usize].nkl == 0
                    || (self.a[c as usize].nkl == nkl
                        && self.a[c as usize].k == key));
            if hit {
                let nxt = self.a[c as usize].nxt;
                let lst = self.a[c as usize].lst;
                let lnxt = self.a[c as usize].lnxt;
                let llst = self.a[c as usize].llst;
                if self.ar[n_index] == Some(c) {
                    self.ar[n_index] = nxt;
                } else {
                    match lst {
                        Some(x) => self.a[x as usize].nxt = nxt,
                        None => {}
                    }
                }
                match nxt {
                    Some(x) => self.a[x as usize].lst = lst,
                    None => {}
                }
                match llst {
                    Some(x) => self.a[x as usize].lnxt = lnxt,
                    None => self.lhead = lnxt,
                }
                match lnxt {
                    Some(x) => self.a[x as usize].llst = llst,
                    None => self.ltail = llst,
                }
                if self.iptr == Some(c) {
                    self.iptr = lnxt;
                }
                let old = self.a[c as usize].data;
                self.dtor(old);
                let nkl_c = self.a[c as usize].nkl as usize;
                self.al.free(BUCKET_BASE + nkl_c);
                self.nelem = self.nelem.wrapping_sub(1);
                self.ndok = self.ndok.wrapping_add(1);
                return;
            }
            p = self.a[c as usize].nxt;
        }
        self.ndfail = self.ndfail.wrapping_add(1);
    }

    /// The fold, over the SURVIVING keys, in the global list's own order.
    fn fold(&self) -> u64 {
        let mut acc: u64 = 0;
        let mut p = self.lhead;
        while let Some(c) = p {
            let n = &self.a[c as usize];
            acc = acc.wrapping_mul(31).wrapping_add(n.nkl as u64);
            acc = acc.wrapping_mul(31).wrapping_add(n.h);
            let mut i: usize = 0;
            while i < n.nkl as usize {
                acc = acc.wrapping_mul(31).wrapping_add(kbyte(n.k, i));
                i += 1;
            }
            acc = acc.wrapping_mul(31).wrapping_add(n.data & 0xFFFF);
            p = n.lnxt;
        }
        acc = acc.wrapping_mul(31).wrapping_add(self.nelem);
        acc = acc.wrapping_mul(31).wrapping_add(self.nnext);
        acc = acc.wrapping_mul(31).wrapping_add(self.ndtor);
        acc = acc.wrapping_mul(31).wrapping_add(self.dfold);
        acc = acc.wrapping_mul(31).wrapping_add(self.ndok);
        acc = acc.wrapping_mul(31).wrapping_add(self.ndfail);
        acc ^ self.al.tally()
    }
}

#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    let win: &[u8] = &buf[off..off + len];
    let nrec: usize = len / REC;
    let mut t = Ht::new(nrec);
    let mut r: usize = 0;
    while r < nrec {
        let ctl: u32 = win[r * REC] as u32;
        let b1: u32 = win[r * REC + 1] as u32;
        let val: u64 = (win[r * REC + 2] as u64) | ((win[r * REC + 3] as u64) << 8);
        let sel: u32 = b1 & (NKEY - 1);
        let (key, nkl): (u64, u32) = key_of(sel);
        let data: u64 = 0x10000u64 | val;
        let op: u32 = ctl & 1;
        let kind: u32 = (ctl >> 1) & 1;
        let coll: u32 = (ctl >> 2) & 1;
        if op == 0 {
            if kind == 0 {
                t.ins_str(key, nkl, data);
            } else {
                let idx = if coll == 1 { hash_of(key, nkl) } else { b1 as u64 };
                t.ins_idx(idx, data);
            }
        } else if kind == 0 {
            t.del(key, nkl, 0, true);
        } else {
            let idx = if coll == 1 { hash_of(key, nkl) } else { b1 as u64 };
            t.del(key, 0, idx, false);
        }
        r += 1;
    }
    t.fold()
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
    if stride_w >= 4 && stride_w <= 268435456 && stride_w <= n_blob as u64 {
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
