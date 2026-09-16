//! ph66 rung R4 -- `unsafe` Rust. `safe_tuned.rs`'s algorithm with the bucket
//! arena's bounds checks removed, and NOTHING ELSE removed.
//!
//! ⚠⚠ THIS FILE IS THE EXEC HALF OF `verus.rs`, LINE FOR LINE. ../spec.md's
//! `identity` entry pins the two cells against each other at both optimisation
//! levels, so a divergence here is a gate failure and not a reading.
//!
//! ============================================================================
//! THE TEN TRUSTED ITEMS, AND WHAT EACH ONE ASSUMES
//! ============================================================================
//! Every one is an arena or window access whose only precondition is an INDEX
//! BOUND. `verus.rs` discharges each bound from `wf`, and each carries a
//! `slb_twin_*` verified twin with the same contract character for character.
//!
//!   nref / set_{nxt,lst,lnxt,llst,data}    the bucket arena
//!   aget / aset                            `ht->arBuckets` AND the size-class
//!                                          cache counters -- both are
//!                                          `Vec<u32>` indexed under a bound
//!                                          `wf` already carries
//!   wsub / wb                              the window
//!
//! ⚠⚠⚠ WHAT IS **NOT** HERE, AND IT IS THE ROW'S POINT. There is no trusted
//! item that could make this kernel unsound in the way the C is WRONG: the C's
//! defect is `:464`'s disjunct, a pure boolean, and no amount of `unsafe`
//! creates it and no amount of safety removes it. R4 reproduces the defect
//! exactly, as R2 and R3 do. ../NOTES.md section 7.
//!
//! ⛔ AND THERE IS NO USE-AFTER-FREE TO REPRODUCE. `zend_hash_del_key_or_index`
//! unlinks a bucket from the chain, from the global list and from
//! `pInternalPointer` before freeing it; this rung's arena slot is simply no
//! longer reachable from any link. Miri has nothing to report and ../NOTES.md
//! section 3 records that it reported nothing.

#[path = "../../common/driver.rs"]
mod driver;

const REC: usize = 4;
const NKEY: u32 = 64;
/// `sizeof(Bucket) - 1` on LP64, asserted at compile time in `../c/kernel.c`.
const BUCKET_BASE: usize = 71;
/// `zend_alloc.h:63-64`.
const MCM: usize = 11;
const MCE: u32 = 256;
/// `NULL`, as an arena index.
const NIL: u32 = u32::MAX;

/// `Bucket` -- zend_hash.h:48-58. `k` is `arKey` packed little-endian into one
/// word, zero-filled past `nKeyLength`; `safe_naive.rs::key_of` carries the
/// equivalence argument and ../spec.md's divergence ledger declares it.
struct Node {
    h: u64,
    nkl: u32,
    k: u64,
    data: u64,
    nxt: u32,
    lst: u32,
    lnxt: u32,
    llst: u32,
}

/// `HashTable` -- zend_hash.h:60-78 -- plus `zend_alloc.c`'s size-class cache
/// counters and the projected `ZVAL_PTR_DTOR` counters.
struct Ht {
    a: Vec<Node>,
    ar: Vec<u32>,
    mask: u64,
    lhead: u32,
    ltail: u32,
    iptr: u32,
    nelem: u64,
    nnext: u64,
    ndtor: u64,
    dfold: u64,
    ndok: u64,
    ndfail: u64,
    cnt: Vec<u32>,
    na: u64,
    nf: u64,
    nh: u64,
    ab: u64,
}

// ------------------------------------------------------ TRUSTED ITEMS ------
#[inline(always)]
fn nref(v: &Vec<Node>, i: u32) -> &Node {
    unsafe { v.get_unchecked(i as usize) }
}

#[inline(always)]
fn set_nxt(v: &mut Vec<Node>, i: u32, x: u32) {
    unsafe {
        v.get_unchecked_mut(i as usize).nxt = x;
    }
}

#[inline(always)]
fn set_lst(v: &mut Vec<Node>, i: u32, x: u32) {
    unsafe {
        v.get_unchecked_mut(i as usize).lst = x;
    }
}

#[inline(always)]
fn set_lnxt(v: &mut Vec<Node>, i: u32, x: u32) {
    unsafe {
        v.get_unchecked_mut(i as usize).lnxt = x;
    }
}

#[inline(always)]
fn set_llst(v: &mut Vec<Node>, i: u32, x: u32) {
    unsafe {
        v.get_unchecked_mut(i as usize).llst = x;
    }
}

#[inline(always)]
fn set_data(v: &mut Vec<Node>, i: u32, x: u64) {
    unsafe {
        v.get_unchecked_mut(i as usize).data = x;
    }
}

#[inline(always)]
fn aget(v: &Vec<u32>, i: usize) -> u32 {
    unsafe { *v.get_unchecked(i) }
}

#[inline(always)]
fn aset(v: &mut Vec<u32>, i: usize, x: u32) {
    unsafe {
        *v.get_unchecked_mut(i) = x;
    }
}

#[inline(always)]
fn wsub(v: &[u8], o: usize, n: usize) -> &[u8] {
    unsafe { v.get_unchecked(o..o + n) }
}

#[inline(always)]
fn wb(v: &[u8], i: usize) -> u8 {
    unsafe { *v.get_unchecked(i) }
}

// ------------------------------------------------------------- helpers -----
/// `_zend_hash_init`'s `while ((1U << i) < nSize) i++;` from `i = 3`.
fn table_size(nrec: usize) -> usize {
    let mut i: u32 = 3;
    while (1usize << i) < nrec {
        i += 1;
    }
    1usize << i
}

/// The `sel`-th string key, packed, and its `nKeyLength` (NUL INCLUDED).
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

fn kbyte(k: u64, i: usize) -> u64 {
    (k >> (8 * i)) & 0xFF
}

/// `zend_inline_hash_func` -- zend_hash.h:243-271, rolled.
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
        let mut t = Ht { a: Vec::new(), ar: vec![NIL; ts], mask: (ts - 1) as u64,
                         lhead: NIL, ltail: NIL, iptr: NIL, nelem: 0, nnext: 0,
                         ndtor: 0, dfold: 0, ndok: 0, ndfail: 0,
                         cnt: vec![0u32; MCM], na: 0, nf: 0, nh: 0, ab: 0 };
        t.alloc(8 * ts); // ecalloc(nTableSize, sizeof(Bucket *))
        t
    }

    /// `_emalloc` -- zend_alloc.c:142-217.
    fn alloc(&mut self, size: usize) {
        let rsz: usize = (size + 7) & !7usize;
        let idx: usize = rsz >> 3;
        self.na = self.na.wrapping_add(1);
        let c: u32 = if idx < MCM { aget(&self.cnt, idx) } else { 0 };
        if idx < MCM && c > 0 {
            aset(&mut self.cnt, idx, c - 1);
            self.nh = self.nh.wrapping_add(1);
        } else {
            self.ab = self.ab.wrapping_add(rsz as u64);
        }
    }

    /// `_efree` -- zend_alloc.c:248-289.
    fn free(&mut self, size: usize) {
        let rsz: usize = (size + 7) & !7usize;
        let idx: usize = rsz >> 3;
        self.nf = self.nf.wrapping_add(1);
        let c: u32 = if idx < MCM { aget(&self.cnt, idx) } else { 0 };
        if idx < MCM && c < MCE {
            aset(&mut self.cnt, idx, c + 1);
        }
    }

    /// `ZVAL_PTR_DTOR` -> `_zval_ptr_dtor`, projected to a count and a fold.
    fn dtor(&mut self, v: u64) {
        self.ndtor = self.ndtor.wrapping_add(1);
        self.dfold = self.dfold.wrapping_mul(31).wrapping_add(v & 0xFFFF);
    }

    /// `CONNECT_TO_BUCKET_DLLIST` + `CONNECT_TO_GLOBAL_DLLIST` -- :24-42.
    fn connect(&mut self, i: u32, n_index: usize) {
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
    }

    /// `_zend_hash_add_or_update(..., HASH_UPDATE)` -- zend_hash.c:192-263.
    fn ins_str(&mut self, key: u64, nkl: u32, data: u64) {
        let h = hash_of(key, nkl);
        let n_index = (h & self.mask) as usize;
        let mut p = aget(&self.ar, n_index);
        let mut hit = false;
        while p != NIL {
            let n = nref(&self.a, p);
            let (eq, nx, dt) = (n.h == h && n.nkl == nkl && n.k == key, n.nxt,
                                n.data);
            if eq {
                self.dtor(dt);
                set_data(&mut self.a, p, data);
                hit = true;
                break;
            }
            p = nx;
        }
        if !hit {
            self.alloc(BUCKET_BASE + nkl as usize);
            let ix: u32 = self.a.len() as u32;
            self.a.push(Node { h, nkl, k: key, data,
                               nxt: NIL, lst: NIL, lnxt: NIL, llst: NIL });
            self.connect(ix, n_index);
        }
    }

    /// `_zend_hash_index_update_or_next_insert(..., HASH_UPDATE)` -- :339-402.
    fn ins_idx(&mut self, h: u64, data: u64) {
        let n_index = (h & self.mask) as usize;
        let mut p = aget(&self.ar, n_index);
        let mut hit = false;
        while p != NIL {
            let n = nref(&self.a, p);
            let (eq, nx, dt) = (n.nkl == 0 && n.h == h, n.nxt, n.data);
            if eq {
                self.dtor(dt);
                set_data(&mut self.a, p, data);
                hit = true;
                break;
            }
            p = nx;
        }
        if !hit {
            self.alloc(BUCKET_BASE);
            let ix: u32 = self.a.len() as u32;
            self.a.push(Node { h, nkl: 0, k: 0, data,
                               nxt: NIL, lst: NIL, lnxt: NIL, llst: NIL });
            self.connect(ix, n_index);
        }
        if (h as i64) >= (self.nnext as i64) {
            self.nnext = h.wrapping_add(1);
        }
    }

    /// `zend_hash_del_key_or_index` -- zend_hash.c:450-503. ⚠⚠⚠ THE PRIMARY
    /// SPAN. `:464`'s DISJUNCT stands exactly as it stands upstream.
    fn del(&mut self, key: u64, nkl: u32, h0: u64, del_key: bool) {
        let h = if del_key { hash_of(key, nkl) } else { h0 };
        let n_index = (h & self.mask) as usize;
        let mut p = aget(&self.ar, n_index);
        let mut done = false;
        while p != NIL {
            let n = nref(&self.a, p);
            // ⛔ THE DEFECT: `n.nkl == 0` is a DISJUNCT, so a NUMERIC bucket
            // matches on hash equality alone and its key is never compared.
            let hit = n.h == h && (n.nkl == 0 || (n.nkl == nkl && n.k == key));
            let nxt = n.nxt;
            let lst = n.lst;
            let lnxt = n.lnxt;
            let llst = n.llst;
            let cnkl = n.nkl;
            let cdata = n.data;
            if hit {
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
                done = true;
                break;
            }
            p = nxt;
        }
        if !done {
            self.ndfail = self.ndfail.wrapping_add(1);
        }
    }

    /// The fold, over the SURVIVING keys, in the global list's own order, then
    /// the counters, then `php_shim_tally()`.
    fn fold(&self) -> u64 {
        let mut acc: u64 = 0;
        let mut p = self.lhead;
        while p != NIL {
            let n = nref(&self.a, p);
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
        acc ^ (self.na.wrapping_mul(1000003) ^ self.nf.wrapping_mul(1000033)
               ^ self.nh.wrapping_mul(1000037) ^ self.ab.wrapping_mul(1000039))
    }

    /// One record of the key stream.
    fn step(&mut self, ctl: u32, b1: u32, val: u64) {
        let sel: u32 = b1 & (NKEY - 1);
        let (key, nkl): (u64, u32) = key_of(sel);
        let data: u64 = 0x10000u64 | val;
        let op: u32 = ctl & 1;
        let kind: u32 = (ctl >> 1) & 1;
        let coll: u32 = (ctl >> 2) & 1;
        if op == 0 {
            if kind == 0 {
                self.ins_str(key, nkl, data);
            } else {
                let idx = if coll == 1 { hash_of(key, nkl) } else { b1 as u64 };
                self.ins_idx(idx, data);
            }
        } else if kind == 0 {
            self.del(key, nkl, 0, true);
        } else {
            let idx = if coll == 1 { hash_of(key, nkl) } else { b1 as u64 };
            self.del(key, 0, idx, false);
        }
    }
}

#[cfg_attr(slb_isolated, inline(never))]
pub fn kernel(buf: &[u8], off: usize, len: usize) -> u64 {
    let win: &[u8] = wsub(buf, off, len);
    let nrec: usize = len / REC;
    let mut t = Ht::new(nrec);
    let mut r: usize = 0;
    while r < nrec {
        let ctl: u32 = wb(win, r * REC) as u32;
        let b1: u32 = wb(win, r * REC + 1) as u32;
        let val: u64 = (wb(win, r * REC + 2) as u64)
            | ((wb(win, r * REC + 3) as u64) << 8);
        t.step(ctl, b1, val);
        r = r + 1;
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
