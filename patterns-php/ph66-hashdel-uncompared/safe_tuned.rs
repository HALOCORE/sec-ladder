//! ph66 rung R3 -- safe Rust, tuned. The SAME algorithm as `safe_naive.rs`,
//! statement for statement, with three changes and no fourth:
//!
//!   1. `Option<u32>` -> a bare `u32` with `NIL = u32::MAX`. The links are an
//!      arena index or nothing, which is exactly what C's `Bucket *` is, and
//!      `Option`'s niche makes every read a discriminant test the C does not do.
//!   2. ONE bound-checked index per chain step. R2 writes
//!      `self.a[c as usize].h`, `self.a[c as usize].nkl`, ... -- a separate
//!      `Vec` index (and therefore a separate panic edge) per field. R3 binds
//!      `let n = &self.a[c as usize];` once and reads the fields off it.
//!   3. the key comparison is ONE `u64` equality, `n.k == key` -- R2 spells the
//!      byte loop out. (Both rungs carry the key PACKED; that representation is
//!      shared by all four Rust rungs and declared once in `../spec.md`'s
//!      divergence ledger, so it is not one of R3's three changes.)
//!
//! ⚠ WHAT IS **NOT** DONE HERE, AND WHY IT IS NOT A MISSED OPTIMISATION.
//! `key_of(sel)` is recomputed per record and could be memoised in a 64-entry
//! table, which would be the largest single win available on this row. It is
//! refused because it is a DIFFERENT PROGRAM: `zend_hash_del(ht, arKey, n)`
//! receives the key BYTES from its caller and hashes them itself at `:458`, and
//! a rung that looks a key up by its selector has stopped comparing keys --
//! which is the one thing this row measures. `../spec.md`'s `idiom.forbidden`
//! pins it absent and `../NOTES.md` section 9 prices what the row is giving up.
//!
//! ⚠⚠ R3 COMPUTES R1's FUNCTION, DEFECT INCLUDED. See `safe_naive.rs`'s header
//! for why every rung below R1h does.

#[path = "../../common/driver.rs"]
mod driver;

const REC: usize = 4;
const NKEY: u32 = 64;
const BUCKET_BASE: usize = 71;
const MAX_CACHED_MEMORY: usize = 11;
const MAX_CACHED_ENTRIES: u32 = 256;
/// `NULL`, as an arena index. `Vec<Node>` can never reach `u32::MAX` entries
/// here: the driver caps the window at 2^28 bytes and a record is 4 of them, so
/// the arena holds at most 2^26 buckets.
const NIL: u32 = u32::MAX;

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
    /// `_emalloc` -- zend_alloc.c:142-217.
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
    /// `_efree` -- zend_alloc.c:248-289.
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

/// `Bucket` -- zend_hash.h:48-58.
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

/// `HashTable` -- zend_hash.h:60-78 -- plus the projected dtor counters.
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
    al: Alloc,
}

fn table_size(nrec: usize) -> usize {
    let mut i: u32 = 3;
    while (1usize << i) < nrec {
        i += 1;
    }
    1usize << i
}

/// The `sel`-th string key, packed little-endian into one `u64`, and its
/// `nKeyLength` -- NUL INCLUDED. The packing is a declared divergence and is
/// exact; `safe_naive.rs`'s copy of this function carries the argument.
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
    fn new(nrec: usize) -> Ht {
        let ts = table_size(nrec);
        let mut al = Alloc::new();
        al.alloc(8 * ts);
        Ht { a: Vec::new(), ar: vec![NIL; ts], mask: (ts - 1) as u64,
             lhead: NIL, ltail: NIL, iptr: NIL, nelem: 0, nnext: 0,
             ndtor: 0, dfold: 0, ndok: 0, ndfail: 0, al }
    }

    fn dtor(&mut self, v: u64) {
        self.ndtor = self.ndtor.wrapping_add(1);
        self.dfold = self.dfold.wrapping_mul(31).wrapping_add(v & 0xFFFF);
    }

    /// `CONNECT_TO_BUCKET_DLLIST` + `CONNECT_TO_GLOBAL_DLLIST` -- :24-42.
    fn connect(&mut self, i: u32, n_index: usize) {
        let head = self.ar[n_index];
        let tail = self.ltail;
        {
            let n = &mut self.a[i as usize];
            n.nxt = head;
            n.lst = NIL;
            n.llst = tail;
            n.lnxt = NIL;
        }
        if head != NIL {
            self.a[head as usize].lst = i;
        }
        self.ltail = i;
        if tail != NIL {
            self.a[tail as usize].lnxt = i;
        }
        if self.lhead == NIL {
            self.lhead = i;
        }
        if self.iptr == NIL {
            self.iptr = i;
        }
        self.ar[n_index] = i;
        self.nelem = self.nelem.wrapping_add(1);
    }

    /// `_zend_hash_add_or_update(..., HASH_UPDATE)` -- zend_hash.c:192-263.
    fn ins_str(&mut self, key: u64, nkl: u32, data: u64) {
        let h = hash_of(key, nkl);
        let n_index = (h & self.mask) as usize;
        let mut p = self.ar[n_index];
        while p != NIL {
            let n = &self.a[p as usize];
            if n.h == h && n.nkl == nkl && n.k == key {
                let old = n.data;
                self.dtor(old);
                self.a[p as usize].data = data;
                return;
            }
            p = n.nxt;
        }
        self.al.alloc(BUCKET_BASE + nkl as usize);
        let ix: u32 = self.a.len() as u32;
        self.a.push(Node { h, nkl, k: key, data,
                           nxt: NIL, lst: NIL, lnxt: NIL, llst: NIL });
        self.connect(ix, n_index);
    }

    /// `_zend_hash_index_update_or_next_insert(..., HASH_UPDATE)` -- :339-402.
    fn ins_idx(&mut self, h: u64, data: u64) {
        let n_index = (h & self.mask) as usize;
        let mut p = self.ar[n_index];
        let mut hit = false;
        while p != NIL {
            let n = &self.a[p as usize];
            if n.nkl == 0 && n.h == h {
                let old = n.data;
                self.dtor(old);
                self.a[p as usize].data = data;
                hit = true;
                break;
            }
            p = n.nxt;
        }
        if !hit {
            self.al.alloc(BUCKET_BASE);
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
        let mut p = self.ar[n_index];
        while p != NIL {
            let (hit, nxt, lst, lnxt, llst, cnkl, cdata) = {
                let n = &self.a[p as usize];
                // ⛔ THE DEFECT: `n.nkl == 0` is a DISJUNCT, so a NUMERIC
                // bucket matches on hash equality alone and its key is never
                // compared.
                (n.h == h && (n.nkl == 0 || (n.nkl == nkl && n.k == key)),
                 n.nxt, n.lst, n.lnxt, n.llst, n.nkl, n.data)
            };
            if hit {
                if self.ar[n_index] == p {
                    self.ar[n_index] = nxt;
                } else if lst != NIL {
                    self.a[lst as usize].nxt = nxt;
                }
                if nxt != NIL {
                    self.a[nxt as usize].lst = lst;
                }
                if llst != NIL {
                    self.a[llst as usize].lnxt = lnxt;
                } else {
                    self.lhead = lnxt;
                }
                if lnxt != NIL {
                    self.a[lnxt as usize].llst = llst;
                } else {
                    self.ltail = llst;
                }
                if self.iptr == p {
                    self.iptr = lnxt;
                }
                self.dtor(cdata);
                self.al.free(BUCKET_BASE + cnkl as usize);
                self.nelem = self.nelem.wrapping_sub(1);
                self.ndok = self.ndok.wrapping_add(1);
                return;
            }
            p = nxt;
        }
        self.ndfail = self.ndfail.wrapping_add(1);
    }

    fn fold(&self) -> u64 {
        let mut acc: u64 = 0;
        let mut p = self.lhead;
        while p != NIL {
            let n = &self.a[p as usize];
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
        let b: &[u8] = &win[r * REC..r * REC + REC];
        let ctl: u32 = b[0] as u32;
        let b1: u32 = b[1] as u32;
        let val: u64 = (b[2] as u64) | ((b[3] as u64) << 8);
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
