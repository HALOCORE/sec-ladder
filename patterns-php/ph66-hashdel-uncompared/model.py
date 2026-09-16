#!/usr/bin/env python3
"""ph66-hashdel-uncompared: the independent reference model the gate checks
against.

The API is documented at the top of `patterns/p01-array-sum/model.py`; this file
notes only where ph66 differs.

    bindings      buf/off/len/buf_len/result. The kernel owns its whole
                  HashTable and destroys it before returning, so there is no
                  destination to bind before and after.
    work_per_call the WINDOW, in bytes -- `stride`, constant across every call
                  on a given input. Argued below.
    sanitizer     always `clean`, and that is this row's headline rather than an
                  omission. ph66's target error is a WRONG ANSWER: every free in
                  `zend_hash_del_key_or_index` is a correct free, so there is
                  nothing for ASan, UBSan or Miri to see. `../NOTES.md` section 3.

⚠⚠ WHICH ALGORITHM THIS MODEL IMPLEMENTS -- AND HERE IT IS **R1's**, WHICH IS
THE OPPOSITE OF ph96 AND ph64:

    R1     `Zend/zend_hash.c` as shipped in 5.0.0 -- LOGIC-001. `:464`'s
           disjunct settles a bucket's key KIND, so a string-key delete matches
           a NUMERIC bucket on hash equality alone.
    R1h    + b73349dbe4e9 (Zeev Suraski, 2006-02-01), applied VERBATIM: the
           length test is hoisted into a required conjunct.
    R2-R5  **R1's function, not R1h's.** The defect is a wrong boolean, not a
           memory error: safe Rust, `unsafe` Rust and Verus all express it
           exactly, and none of them has any reason to refuse it. That is the
           row's registered prediction P1 and `../NOTES.md` section 7 scores it.

    THIS MODEL IMPLEMENTS R1 = R2 = R3 = R4 = R5, i.e. FIVE of the six rungs.

⭐ On the whole BENIGN domain R1h coincides with them exactly -- `inputs/gen.py`
refuses a measured corpus in which any delete would take the defective arm, and
asserts it -- so the model and R1h agree on every input the gate measures. They
differ on `inputs/adversarial-*.bin`, which is what those files are for.

Three independent implementations, as p01/p02/p16, ph03, ph07, ph56, ph96 and
ph97 do:

  * the **simulation** (`_window`) walks each window once with imperative loops
    over integer cursors through a real bucket ARENA with real chain and global
    links, mirroring `c/kernel.c`'s own control flow statement for statement.
    Per-window results go in a table, which is what makes 20 000 driver
    iterations tractable;
  * the **helper** `hash_fold` -- the one the derived `ensures` is evaluated
    against -- is built out of RECURSIVE walks with no `while` and no mutation,
    mirroring the Verus spec functions `s_run` / `s_rec` / `s_ins_str` /
    `s_ins_idx` / `s_del` / `s_chain` / `s_fold` in `../verus.rs` one unfolding
    at a time;
  * `_dumb`, a third spelling with **no links at all**. It keeps a flat list of
    buckets tagged with an insertion sequence number and resolves every lookup
    by `max(seq)` over the live buckets in the slot whose predicate holds. That
    is sound because `CONNECT_TO_BUCKET_DLLIST` prepends at the HEAD and the
    delete only short-circuits `pLast -> pNext`, so chain order IS descending
    insertion order -- a theorem about the structure, derived once here and
    checked on every run instead of being assumed. It is the one spelling that
    cannot share a link-manipulation mistake with the other two, and link
    manipulation is half of what this row's delete does.

`selfcheck()` runs them against each other -- on the shipped inputs AND on
synthetic records it builds itself over a domain no input file contains -- and a
disagreement is reported there rather than absorbed into a green line.

⚠⚠ **THE SYNTHETIC SWEEP IS NOT DECORATION.** `PROTOCOL_PHP.md` §A2a rule 2: a
second implementation is only as strong as the domain it is exercised over, and
`inputs/` is not a domain -- it is six files. ph03 shipped for a full task with
its two implementations computing different functions because its corpus took
one arm of a two-armed branch.
"""

import itertools
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "common-php"))
import slb  # noqa: E402

MASK = (1 << 64) - 1

REC = 4
KMAX = 7        # max key CHARACTERS
NKEY = 64       # sel = b[1] & 63

#: `sizeof(Bucket) - 1` on LP64 -- 8 + 4(+4 pad) + 8 + 8 + 4*8 + 1 = 72, minus
#: one for the `char arKey[1]` flexible tail. `c/kernel.c::ph66_layout_assert`
#: holds the C to exactly this number at COMPILE time, so a padding change on
#: another ABI is a build failure and never a silent model disagreement.
BUCKET_BASE = 71

#: `Zend/zend_alloc.h:63-64`, via `common-php/emalloc_shim.h:190-191`.
MAX_CACHED_MEMORY = 11
MAX_CACHED_ENTRIES = 256

NIL = -1


def key_of(sel):
    """The `sel`-th string key, NUL INCLUDED -- `nKeyLength` is `len()`.

    `kl = 1 + (sel % 7)` characters and `key[i] = 'a' + ((sel//7)*5 + i*7) % 26`.
    ⚠ `nKeyLength` includes the NUL because `Zend/zend_execute.c:3612` passes
    `varname->value.str.len + 1`, so this returns `kl + 1` bytes."""
    kl = 1 + (sel % 7)
    return bytes(ord('a') + (((sel // 7) * 5 + i * 7) % 26) for i in range(kl)) \
        + b"\x00"


def djbx33a(key):
    """`zend_inline_hash_func`, Zend/zend_hash.h:243-271, over `len(key)` bytes.

    ⚠ Upstream accumulates in a `ulong`, i.e. 64-bit on LP64, and reads a plain
    (signed) `char`. Every byte here is 'a'..'z' or NUL, so the sign never
    bites; `inputs/gen.py::_check_keys` asserts it."""
    h = 5381
    for b in key:
        h = (h * 33 + b) & MASK
    return h


def table_size(nrec):
    """`_zend_hash_init`'s `while ((1U << i) < nSize) i++;` from `i = 3`."""
    i = 3
    while (1 << i) < nrec:
        i += 1
    return 1 << i


def decode(b):
    """(op, kind, coll, sel, val) for one 4-byte record.

    `op`/`kind`/`coll` are three independent BITS of `b[0]` and `sel` is
    `b[1] & 63`; for a NON-colliding index record the index is `b[1]` itself, so
    one byte carries the selector in both readings and the `coll` bit alone
    decides which. ⭐ That is the whole trigger: `coll` turns the index into
    `djbx33a(key_of(sel))`, which is the value
    `_zend_hash_index_update_or_next_insert` stores verbatim in `p->h`."""
    return (b[0] & 1, (b[0] >> 1) & 1, (b[0] >> 2) & 1, b[1] & (NKEY - 1),
            b[2] | (b[3] << 8))


def plain_index(b):
    """The index a NON-colliding index record names: `b[1]`, 0..255."""
    return b[1]


class Alloc:
    """`zend_alloc.c`'s size-class cache, counters only -- the same model all
    four Rust rungs carry, and `controls/differential.py` checks all five
    against the SHIPPED C rather than against each other."""

    __slots__ = ("cnt", "n_alloc", "n_free", "n_hit", "bytes")

    def __init__(self):
        self.cnt = [0] * MAX_CACHED_MEMORY
        self.n_alloc = 0
        self.n_free = 0
        self.n_hit = 0
        self.bytes = 0

    def alloc(self, size):
        rsz = (size + 7) & ~7
        idx = rsz >> 3
        self.n_alloc += 1
        if idx < MAX_CACHED_MEMORY and self.cnt[idx] > 0:
            self.cnt[idx] -= 1
            self.n_hit += 1
        else:
            self.bytes += rsz

    def free(self, size):
        rsz = (size + 7) & ~7
        idx = rsz >> 3
        self.n_free += 1
        if idx < MAX_CACHED_MEMORY and self.cnt[idx] < MAX_CACHED_ENTRIES:
            self.cnt[idx] += 1

    def tally(self):
        return ((self.n_alloc * 1000003) ^ (self.n_free * 1000033)
                ^ (self.n_hit * 1000037) ^ (self.bytes * 1000039)) & MASK


def _sgn(x):
    """`(long)x` on LP64 -- the cast `_zend_hash_index_update_or_next_insert`
    makes at `:378` and `:401`."""
    return x - (1 << 64) if x >= (1 << 63) else x


# ==========================================================================
# implementation 1 of 3: the imperative simulation, with real links
# ==========================================================================
class _Node:
    __slots__ = ("h", "nkl", "key", "data", "req", "nxt", "lst", "lnxt", "llst")

    def __init__(self, h, nkl, key, data, req):
        self.h, self.nkl, self.key, self.data, self.req = h, nkl, key, data, req
        self.nxt = self.lst = self.lnxt = self.llst = NIL


class _Table:
    """`HashTable` plus the projected `ZVAL_PTR_DTOR` counters."""

    def __init__(self, nrec):
        self.al = Alloc()
        self.ts = table_size(nrec)
        self.mask = self.ts - 1
        self.ar = [NIL] * self.ts
        self.a = []                       # the bucket arena
        self.lhead = self.ltail = self.iptr = NIL
        self.nelem = 0
        self.nnext = 0
        self.ndtor = 0
        self.dfold = 0
        self.ndok = 0
        self.ndfail = 0
        self.arms = set()
        self.al.alloc(8 * self.ts)        # ecalloc(nTableSize, sizeof(Bucket*))

    # -- the projected destructor, `ZVAL_PTR_DTOR` -> a count and a fold ----
    def _dtor(self, v):
        self.ndtor += 1
        self.dfold = (self.dfold * 31 + (v & 0xFFFF)) & MASK

    def _connect(self, i, nIndex):
        a = self.a
        a[i].nxt = self.ar[nIndex]                     # CONNECT_TO_BUCKET_DLLIST
        a[i].lst = NIL
        if a[i].nxt != NIL:
            a[a[i].nxt].lst = i
        a[i].llst = self.ltail                         # CONNECT_TO_GLOBAL_DLLIST
        self.ltail = i
        a[i].lnxt = NIL
        if a[i].llst != NIL:
            a[a[i].llst].lnxt = i
        if self.lhead == NIL:
            self.lhead = i
        if self.iptr == NIL:
            self.iptr = i
        self.ar[nIndex] = i
        self.nelem += 1

    def ins_str(self, key, data):
        """`_zend_hash_add_or_update(..., HASH_UPDATE)`, zend_hash.c:192-263."""
        nkl = len(key)
        h = djbx33a(key)
        nIndex = h & self.mask
        p = self.ar[nIndex]
        while p != NIL:
            n = self.a[p]
            if n.h == h and n.nkl == nkl and n.key == key:
                self.arms.add("ins_str_update")
                self._dtor(n.data)
                n.data = data
                return
            p = n.nxt
        req = BUCKET_BASE + nkl
        self.al.alloc(req)
        self.a.append(_Node(h, nkl, key, data, req))
        self._connect(len(self.a) - 1, nIndex)

    def ins_idx(self, h, data):
        """`_zend_hash_index_update_or_next_insert(..., HASH_UPDATE)`, :339-402."""
        nIndex = h & self.mask
        p = self.ar[nIndex]
        while p != NIL:
            n = self.a[p]
            if n.nkl == 0 and n.h == h:
                self.arms.add("ins_idx_update")
                self._dtor(n.data)
                n.data = data
                if _sgn(h) >= _sgn(self.nnext):
                    self.nnext = (h + 1) & MASK
                return
            p = n.nxt
        self.al.alloc(BUCKET_BASE)
        self.a.append(_Node(h, 0, b"", data, BUCKET_BASE))
        self._connect(len(self.a) - 1, nIndex)
        if _sgn(h) >= _sgn(self.nnext):
            self.nnext = (h + 1) & MASK

    def delete(self, key, nkl, h, hardened):
        """`zend_hash_del_key_or_index`, zend_hash.c:450-503. THE PRIMARY SPAN.

        `key is None` is the `HASH_DEL_INDEX` call (`arKey == NULL`,
        `nKeyLength == 0`); otherwise `h` is recomputed from the key, exactly as
        `:457-459` does."""
        if key is not None:
            h = djbx33a(key)
        nIndex = h & self.mask
        p = self.ar[nIndex]
        a = self.a
        while p != NIL:
            n = a[p]
            if hardened:
                hit = (n.h == h and n.nkl == nkl
                       and (n.nkl == 0 or n.key == key))
            else:
                hit = (n.h == h and (n.nkl == 0
                                     or (n.nkl == nkl and n.key == key)))
            if hit:
                if key is not None and n.nkl == 0:
                    self.arms.add("DEFECT_left_disjunct_on_string_delete")
                elif key is not None:
                    self.arms.add("del_str_memcmp")
                else:
                    self.arms.add("del_idx")
                if p == self.ar[nIndex]:
                    self.ar[nIndex] = n.nxt
                else:
                    a[n.lst].nxt = n.nxt
                if n.nxt != NIL:
                    a[n.nxt].lst = n.lst
                if n.llst != NIL:
                    a[n.llst].lnxt = n.lnxt
                else:
                    self.lhead = n.lnxt
                if n.lnxt != NIL:
                    a[n.lnxt].llst = n.llst
                else:
                    self.ltail = n.llst
                if self.iptr == p:
                    self.iptr = n.lnxt
                self._dtor(n.data)
                self.al.free(n.req)
                self.nelem -= 1
                self.ndok += 1
                return
            if n.nxt != NIL:
                self.arms.add("chain_walk_step")
            p = n.nxt
        self.ndfail += 1
        self.arms.add("del_miss")

    def fold(self):
        acc = 0
        p = self.lhead
        while p != NIL:
            n = self.a[p]
            acc = (acc * 31 + n.nkl) & MASK
            acc = (acc * 31 + n.h) & MASK
            for i in range(n.nkl):
                acc = (acc * 31 + n.key[i]) & MASK
            acc = (acc * 31 + (n.data & 0xFFFF)) & MASK
            p = n.lnxt
        acc = (acc * 31 + self.nelem) & MASK
        acc = (acc * 31 + self.nnext) & MASK
        acc = (acc * 31 + self.ndtor) & MASK
        acc = (acc * 31 + self.dfold) & MASK
        acc = (acc * 31 + self.ndok) & MASK
        acc = (acc * 31 + self.ndfail) & MASK
        return (acc ^ self.al.tally()) & MASK


def simulate(win, hardened=False, want_arms=False):
    """One window, R1 (`hardened=False`) or R1h (`hardened=True`)."""
    nrec = len(win) // REC
    t = _Table(nrec)
    for r in range(nrec):
        b = win[r * REC:(r + 1) * REC]
        op, kind, coll, sel, val = decode(b)
        key = key_of(sel)
        idx = djbx33a(key) if coll else plain_index(b)
        data = 0x10000 | val
        if op == 0:
            if kind == 0:
                t.arms.add("ins_str")
                t.ins_str(key, data)
            else:
                t.arms.add("ins_idx_coll" if coll else "ins_idx_plain")
                t.ins_idx(idx, data)
        else:
            if kind == 0:
                t.delete(key, len(key), 0, hardened)
            else:
                t.delete(None, 0, idx, hardened)
        if len(key) >= 8:
            t.arms.add("hash_unrolled")
        else:
            t.arms.add("hash_switch")
    return (t.fold(), t.arms) if want_arms else t.fold()


# ==========================================================================
# implementation 3 of 3: NO LINKS AT ALL -- resolve by max(insertion seq)
# ==========================================================================
def _dumb(win, hardened=False):
    """A third spelling of one window's answer, with no chain and no list.

    ⭐ THE THEOREM IT RESTS ON, DERIVED ONCE HERE: `CONNECT_TO_BUCKET_DLLIST`
    prepends at the head and `ht->arBuckets[nIndex] = p` makes the new bucket
    the head, while the delete only ever short-circuits `pLast -> pNext`. So a
    bucket chain is EXACTLY the live buckets of that slot in DESCENDING
    insertion order, and "the first match walking the chain" is "the matching
    live bucket with the largest sequence number". The global list is the
    mirror image -- `CONNECT_TO_GLOBAL_DLLIST` appends at the tail -- so the
    fold order is ASCENDING sequence.

    That is a claim about the two macros, and `selfcheck` is what makes it a
    checked claim rather than a comment."""
    nrec = len(win) // REC
    ts = table_size(nrec)
    mask = ts - 1
    al = Alloc()
    al.alloc(8 * ts)
    bs = []                       # (h, nkl, key, data, req, live)
    nnext, ndtor, dfold, ndok, ndfail = 0, 0, 0, 0, 0

    def live_in_slot(nIndex):
        return [i for i, b in enumerate(bs) if b[5] and (b[0] & mask) == nIndex]

    for r in range(nrec):
        rb = win[r * REC:(r + 1) * REC]
        op, kind, coll, sel, val = decode(rb)
        key = key_of(sel)
        data = 0x10000 | val
        if op == 0 and kind == 0:                       # insert by string key
            h, nkl = djbx33a(key), len(key)
            cand = [i for i in live_in_slot(h & mask)
                    if bs[i][0] == h and bs[i][1] == nkl and bs[i][2] == key]
            if cand:
                i = max(cand)
                ndtor += 1
                dfold = (dfold * 31 + (bs[i][3] & 0xFFFF)) & MASK
                bs[i] = (h, nkl, key, data, bs[i][4], True)
            else:
                req = BUCKET_BASE + nkl
                al.alloc(req)
                bs.append((h, nkl, key, data, req, True))
        elif op == 0:                                   # insert by index
            h = djbx33a(key) if coll else plain_index(rb)
            cand = [i for i in live_in_slot(h & mask)
                    if bs[i][1] == 0 and bs[i][0] == h]
            if cand:
                i = max(cand)
                ndtor += 1
                dfold = (dfold * 31 + (bs[i][3] & 0xFFFF)) & MASK
                bs[i] = (h, 0, b"", data, bs[i][4], True)
            else:
                al.alloc(BUCKET_BASE)
                bs.append((h, 0, b"", data, BUCKET_BASE, True))
            if _sgn(h) >= _sgn(nnext):
                nnext = (h + 1) & MASK
        else:                                           # delete
            if kind == 0:
                h, nkl, k = djbx33a(key), len(key), key
            else:
                h, nkl, k = (djbx33a(key) if coll else plain_index(rb)), 0, None
            if hardened:
                cand = [i for i in live_in_slot(h & mask)
                        if bs[i][0] == h and bs[i][1] == nkl
                        and (bs[i][1] == 0 or bs[i][2] == k)]
            else:
                cand = [i for i in live_in_slot(h & mask)
                        if bs[i][0] == h and (bs[i][1] == 0
                                              or (bs[i][1] == nkl
                                                  and bs[i][2] == k))]
            if cand:
                i = max(cand)
                ndtor += 1
                dfold = (dfold * 31 + (bs[i][3] & 0xFFFF)) & MASK
                al.free(bs[i][4])
                bs[i] = bs[i][:5] + (False,)
                ndok += 1
            else:
                ndfail += 1

    acc = 0
    for b in bs:
        if not b[5]:
            continue
        acc = (acc * 31 + b[1]) & MASK
        acc = (acc * 31 + b[0]) & MASK
        for i in range(b[1]):
            acc = (acc * 31 + b[2][i]) & MASK
        acc = (acc * 31 + (b[3] & 0xFFFF)) & MASK
    acc = (acc * 31 + sum(1 for b in bs if b[5])) & MASK
    acc = (acc * 31 + nnext) & MASK
    acc = (acc * 31 + ndtor) & MASK
    acc = (acc * 31 + dfold) & MASK
    acc = (acc * 31 + ndok) & MASK
    acc = (acc * 31 + ndfail) & MASK
    return (acc ^ al.tally()) & MASK


class Model:
    """Simulates ../spec.md's driver loop and kernel from the file alone."""

    def __init__(self, path):
        f = slb.read(path)
        self.path = path
        self.n_iters = f.n_iters
        self.declared_len = f.declared_len
        self.truncated = f.truncated
        # The drivers read exactly `payload_len` bytes and reject a short file.
        self.payload = f.payload[: f.declared_len]
        self.stride, self.buf = slb.head1_u64_bytes(self.payload)
        self.n_blob = len(self.buf)
        self.n_calls = 0
        self.checksum = None
        self.entered = False
        self.nwin = 0
        self._win = []
        self._visited = set()
        self.any_defect = False   # some call the driver makes takes `:464`'s
                                  # left disjunct on a STRING-key delete
        if not self.truncated:
            self._run()

    # -- implementation 1 of 3 ---------------------------------------------
    def _window(self, off):
        """(result, does R1 differ from R1h on this window?)."""
        win = self.buf[off: off + self.stride]
        r1 = simulate(win, hardened=False)
        r1h = simulate(win, hardened=True)
        return r1, r1 != r1h

    def _run(self):
        acc = 0
        if REC <= self.stride <= 268435456 and self.stride <= self.n_blob:
            self.entered = True
            self.nwin = self.n_blob // self.stride
            self._win = [self._window(k * self.stride) for k in range(self.nwin)]
            for _ in range(self.n_iters):
                k = (acc * self.nwin) >> 64
                self._visited.add(k)
                r, d = self._win[k]
                if d:
                    self.any_defect = True
                acc = (acc * 31 + r) & MASK
            self.n_calls = self.n_iters
        self.checksum = acc

    def iter_calls(self):
        """Replay the driver loop, yielding one binding per kernel call."""
        if not self.entered:
            return
        acc = 0
        for _ in range(self.n_iters):
            k = (acc * self.nwin) >> 64
            r = self._win[k][0]
            yield {"buf": self.buf, "off": k * self.stride, "len": self.stride,
                   "buf_len": self.n_blob, "result": r}
            acc = (acc * 31 + r) & MASK

    def sample_calls(self, k):
        if not self.entered or k <= 0:
            return []
        step = max(1, self.n_calls // k)
        return list(itertools.islice(
            (c for i, c in enumerate(self.iter_calls()) if i % step == 0), k))

    # ------------------------------------------------------------------
    # implementation 2 of 3: the RECURSIVE one the `ensures` is checked
    # against. It mirrors ../verus.rs's spec functions one unfolding at a
    # time -- no `while`, no mutation, one immutable state tuple -- and must
    # NOT be the simulation in disguise.
    # ------------------------------------------------------------------
    #: The immutable ghost state, in ../verus.rs's own field order:
    #: (nodes, ar, lhead, ltail, iptr, nelem, nnext, ndtor, dfold, ndok,
    #:  ndfail, cnt, n_alloc, n_free, n_hit, abytes)
    #: a node is (h, nkl, key, data, req, nxt, lst, lnxt, llst)

    @staticmethod
    def _s_hash(key, i=0, h=5381):
        """`s_hash` -- one unfolding per byte, no loop."""
        if i >= len(key):
            return h
        return Model._s_hash(key, i + 1, (h * 33 + key[i]) & MASK)

    @staticmethod
    def _s_alloc(st, size):
        rsz = (size + 7) & ~7
        idx = rsz >> 3
        cnt, na, nf, nh, ab = st[11], st[12], st[13], st[14], st[15]
        if idx < MAX_CACHED_MEMORY and cnt[idx] > 0:
            cnt = cnt[:idx] + (cnt[idx] - 1,) + cnt[idx + 1:]
            return st[:11] + (cnt, na + 1, nf, nh + 1, ab)
        return st[:11] + (cnt, na + 1, nf, nh, ab + rsz)

    @staticmethod
    def _s_free(st, size):
        rsz = (size + 7) & ~7
        idx = rsz >> 3
        cnt, na, nf, nh, ab = st[11], st[12], st[13], st[14], st[15]
        if idx < MAX_CACHED_MEMORY and cnt[idx] < MAX_CACHED_ENTRIES:
            cnt = cnt[:idx] + (cnt[idx] + 1,) + cnt[idx + 1:]
        return st[:11] + (cnt, na, nf + 1, nh, ab)

    @staticmethod
    def _s_chain_find(nodes, p, pred):
        """`s_chain` -- walk one bucket chain by recursion, NIL-terminated."""
        if p == NIL:
            return NIL
        if pred(nodes[p]):
            return p
        return Model._s_chain_find(nodes, nodes[p][5], pred)

    @staticmethod
    def _s_upd(st, i, field, v):
        n = st[0][i]
        n = n[:field] + (v,) + n[field + 1:]
        return (st[0][:i] + (n,) + st[0][i + 1:],) + st[1:]

    @staticmethod
    def _s_dtor(st, v):
        return st[:7] + (st[7] + 1, (st[8] * 31 + (v & 0xFFFF)) & MASK) + st[9:]

    @staticmethod
    def _s_connect(st, i, nIndex):
        """CONNECT_TO_BUCKET_DLLIST then CONNECT_TO_GLOBAL_DLLIST, :24-42."""
        st = Model._s_upd(st, i, 5, st[1][nIndex])            # nxt
        st = Model._s_upd(st, i, 6, NIL)                      # lst
        if st[0][i][5] != NIL:
            st = Model._s_upd(st, st[0][i][5], 6, i)
        st = Model._s_upd(st, i, 8, st[3])                    # llst = ltail
        st = st[:3] + (i,) + st[4:]                           # ltail = i
        st = Model._s_upd(st, i, 7, NIL)                      # lnxt
        if st[0][i][8] != NIL:
            st = Model._s_upd(st, st[0][i][8], 7, i)
        if st[2] == NIL:
            st = st[:2] + (i,) + st[3:]                       # lhead
        if st[4] == NIL:
            st = st[:4] + (i,) + st[5:]                       # iptr
        ar = st[1][:nIndex] + (i,) + st[1][nIndex + 1:]
        st = (st[0], ar) + st[2:]
        return st[:5] + (st[5] + 1,) + st[6:]                 # nelem

    @staticmethod
    def _s_ins_str(st, key, data, mask):
        h, nkl = Model._s_hash(key), len(key)
        nIndex = h & mask
        hit = Model._s_chain_find(
            st[0], st[1][nIndex],
            lambda n: n[0] == h and n[1] == nkl and n[2] == key)
        if hit != NIL:
            st = Model._s_dtor(st, st[0][hit][3])
            return Model._s_upd(st, hit, 3, data)
        req = BUCKET_BASE + nkl
        st = Model._s_alloc(st, req)
        st = ((st[0] + ((h, nkl, key, data, req, NIL, NIL, NIL, NIL),),) + st[1:])
        return Model._s_connect(st, len(st[0]) - 1, nIndex)

    @staticmethod
    def _s_ins_idx(st, h, data, mask):
        nIndex = h & mask
        hit = Model._s_chain_find(st[0], st[1][nIndex],
                                  lambda n: n[1] == 0 and n[0] == h)
        if hit != NIL:
            st = Model._s_dtor(st, st[0][hit][3])
            st = Model._s_upd(st, hit, 3, data)
        else:
            st = Model._s_alloc(st, BUCKET_BASE)
            st = ((st[0] + ((h, 0, b"", data, BUCKET_BASE,
                             NIL, NIL, NIL, NIL),),) + st[1:])
            st = Model._s_connect(st, len(st[0]) - 1, nIndex)
        if _sgn(h) >= _sgn(st[6]):
            st = st[:6] + ((h + 1) & MASK,) + st[7:]
        return st

    @staticmethod
    def _s_del(st, key, nkl, h, mask, hardened):
        if key is not None:
            h = Model._s_hash(key)
        nIndex = h & mask
        if hardened:
            def pred(n):
                return n[0] == h and n[1] == nkl and (n[1] == 0 or n[2] == key)
        else:
            def pred(n):
                return n[0] == h and (n[1] == 0
                                      or (n[1] == nkl and n[2] == key))
        p = Model._s_chain_find(st[0], st[1][nIndex], pred)
        if p == NIL:
            return st[:10] + (st[10] + 1,) + st[11:]
        n = st[0][p]
        if p == st[1][nIndex]:
            ar = st[1][:nIndex] + (n[5],) + st[1][nIndex + 1:]
            st = (st[0], ar) + st[2:]
        else:
            st = Model._s_upd(st, n[6], 5, n[5])
        if n[5] != NIL:
            st = Model._s_upd(st, n[5], 6, n[6])
        if n[8] != NIL:
            st = Model._s_upd(st, n[8], 7, n[7])
        else:
            st = st[:2] + (n[7],) + st[3:]
        if n[7] != NIL:
            st = Model._s_upd(st, n[7], 8, n[8])
        else:
            st = st[:3] + (n[8],) + st[4:]
        if st[4] == p:
            st = st[:4] + (n[7],) + st[5:]
        st = Model._s_dtor(st, n[3])
        st = Model._s_free(st, n[4])
        st = st[:5] + (st[5] - 1,) + st[6:]
        return st[:9] + (st[9] + 1,) + st[10:]

    @staticmethod
    def _s_rec(win, r, nrec, st, mask):
        """`s_run` -- one unfolding per record."""
        if r >= nrec:
            return st
        b = win[r * REC:(r + 1) * REC]
        op, kind, coll, sel, val = decode(b)
        key = key_of(sel)
        data = 0x10000 | val
        if op == 0 and kind == 0:
            st = Model._s_ins_str(st, key, data, mask)
        elif op == 0:
            st = Model._s_ins_idx(
                st, Model._s_hash(key) if coll else plain_index(b), data, mask)
        elif kind == 0:
            st = Model._s_del(st, key, len(key), 0, mask, False)
        else:
            st = Model._s_del(
                st, None, 0,
                Model._s_hash(key) if coll else plain_index(b), mask, False)
        return Model._s_rec(win, r + 1, nrec, st, mask)

    @staticmethod
    def _s_fold_key(key, nkl, i, acc):
        if i >= nkl:
            return acc
        return Model._s_fold_key(key, nkl, i + 1, (acc * 31 + key[i]) & MASK)

    @staticmethod
    def _s_fold(st, p, acc):
        """Walk the GLOBAL list by recursion and fold each surviving bucket."""
        if p == NIL:
            return acc
        n = st[0][p]
        acc = (acc * 31 + n[1]) & MASK
        acc = (acc * 31 + n[0]) & MASK
        acc = Model._s_fold_key(n[2], n[1], 0, acc)
        acc = (acc * 31 + (n[3] & 0xFFFF)) & MASK
        return Model._s_fold(st, n[7], acc)

    def hash_fold(self, buf, off, ln):
        """`hash_fold` in ../verus.rs: what the kernel must return."""
        win = buf[off: off + ln]
        nrec = ln // REC
        ts = table_size(nrec)
        st = ((), (NIL,) * ts, NIL, NIL, NIL, 0, 0, 0, 0, 0, 0,
              (0,) * MAX_CACHED_MEMORY, 0, 0, 0, 0)
        st = Model._s_alloc(st, 8 * ts)
        st = Model._s_rec(win, 0, nrec, st, ts - 1)
        acc = Model._s_fold(st, st[2], 0)
        for v in (st[5], st[6], st[7], st[8], st[9], st[10]):
            acc = (acc * 31 + v) & MASK
        tally = ((st[12] * 1000003) ^ (st[13] * 1000033)
                 ^ (st[14] * 1000037) ^ (st[15] * 1000039)) & MASK
        return (acc ^ tally) & MASK

    @property
    def helpers(self):
        return {"hash_fold": self.hash_fold}

    # -- what the kernel must do, per call ---------------------------------
    @property
    def work_per_call(self):
        """The window, in bytes -- `stride` -- from the file alone.

        **Why the window and not the record count.** `check.py::
        check_marginal_ir` needs one scalar per input and hard-fails on
        `work_per_call = 0`. The record count IS `stride // 4`, an exact
        (floor-)linear function of the stride, so the two denominators differ by
        a constant factor and the stride is the one the payload header fixes and
        the attacker cannot move.

        ⚠ The per-record work is NOT constant and this row says so rather than
        presenting the marginal as a per-byte rate: an insert of a NEW key walks
        its chain, allocates a bucket and links it into two lists; an insert of
        an EXISTING key walks the chain and writes one word; a failing delete
        walks the chain and does nothing. The bucket TABLE is also sized from
        `nrec`, so the chain lengths -- and therefore the walk cost -- are a
        function of the same denominator. `../NOTES.md` section 9 decomposes it."""
        return self.stride if self.entered else 0

    # -- sanitizer expectation ---------------------------------------------
    @property
    def sanitizer_expect(self):
        """⛔ ALWAYS `clean`, ON EVERY INPUT, INCLUDING THE ADVERSARIAL ONES.

        That is the row's whole point and it is a DERIVATION, not a default:
        `zend_hash_del_key_or_index` unlinks the bucket from the bucket chain,
        from the global list and from `ht->pInternalPointer` before
        `pefree(p, ...)`, and the payload is never NULL so
        `if (!p->pDataPtr) pefree(p->pData, ...)` is never taken -- so no free
        in this kernel is followed by any read of what it freed. The harm is
        that the WRONG bucket was chosen. ASan, UBSan and Miri all have nothing
        to report, and the u64 is the only instrument that does.
        `../NOTES.md` section 3; predictions P1 and P2 in section 7."""
        return "clean"

    # -- what a conforming driver does -------------------------------------
    @property
    def expected_exit(self):
        # ph66's payload declares no destination capacity -- the bucket table is
        # sized from the record count -- so p02's exit 7 has no analogue here.
        # `slb_load` rejecting a short file is the only non-zero exit.
        return 5 if self.truncated else 0

    @property
    def expected_stdout(self):
        return "" if self.checksum is None else f"{self.checksum}\n"

    def describe(self):
        return (f"n_iters={self.n_iters} stride={self.stride} "
                f"n_blob={self.n_blob} nwin={self.nwin} "
                f"recs/win={self.stride // REC} "
                f"tablesize={table_size(self.stride // REC) if self.entered else 0} "
                f"calls={self.n_calls} work/call={self.work_per_call}B "
                f"san={self.sanitizer_expect} defect={self.any_defect} "
                f"truncated={self.truncated} expected={self.checksum}")

    # -- driving ALL THREE implementations over a domain no file contains --
    @staticmethod
    def _rec(op, kind, coll, sel, val=0x2A):
        return bytes([(op & 1) | ((kind & 1) << 1) | ((coll & 1) << 2),
                      sel & 0xFF, val & 0xFF, (val >> 8) & 0xFF])

    @staticmethod
    def _synthetic_windows():
        """Windows built HERE, spanning arms `inputs/` cannot all carry.

        `inputs/` ships one stride per file and a benign corpus by construction,
        so it reaches neither the defect arm nor the short chains a one-record
        window has. These do."""
        out = []
        # every (op, kind, coll) triple on one selector, alone
        for op in (0, 1):
            for kind in (0, 1):
                for coll in (0, 1):
                    out.append(Model._rec(op, kind, coll, 3))
        # the four orderings of {string insert, colliding index insert} followed
        # by each of the two deletes -- cells A and D of the oracle matrix
        for first, second in ((0, 1), (1, 0)):
            for dk in (0, 1):
                out.append(Model._rec(0, first, 1, 5)
                           + Model._rec(0, second, 1, 5)
                           + Model._rec(1, dk, 1, 5))
        # a deep chain: many plain indices that share a slot, then a delete
        out.append(b"".join(Model._rec(0, 1, 0, 0, i) for i in range(13))
                   + Model._rec(1, 1, 0, 0))
        # duplicate inserts (the UPDATE arm of both insert functions)
        out.append(Model._rec(0, 0, 0, 9, 1) + Model._rec(0, 0, 0, 9, 2)
                   + Model._rec(0, 1, 1, 9, 3) + Model._rec(0, 1, 1, 9, 4)
                   + Model._rec(1, 0, 0, 9))
        # every key length, so `zend_inline_hash_func`'s unrolled arm AND its
        # switch tail are both driven
        out.append(b"".join(Model._rec(0, 0, 0, s) for s in range(NKEY)))
        out.append(b"".join(Model._rec(1, 0, 0, s) for s in range(NKEY)))
        # deletes that miss entirely
        out.append(Model._rec(1, 0, 0, 17) + Model._rec(1, 1, 0, 17)
                   + Model._rec(1, 1, 1, 17))
        # a longer pseudo-random stream, deterministic
        st = 0x9E3779B97F4A7C15
        rnd = bytearray()
        for _ in range(64):
            st = (st * 6364136223846793005 + 1442695040888963407) & MASK
            rnd += bytes([(st >> 13) & 0xFF, (st >> 21) & 0xFF,
                          (st >> 29) & 0xFF, (st >> 37) & 0xFF])
        out.append(bytes(rnd))
        return out

    def selfcheck(self):
        """Drive the three implementations against each other. `[]` is PASS."""
        bad = []
        wins = list(Model._synthetic_windows())
        if self.entered:
            wins += [self.buf[k * self.stride:(k + 1) * self.stride]
                     for k in range(min(self.nwin, 24))]
        for w in wins:
            if len(w) < REC:
                continue
            a = simulate(w, hardened=False)
            b = self.hash_fold(w, 0, len(w))
            c = _dumb(w, hardened=False)
            if not (a == b == c):
                bad.append(f"R1 disagreement on {w.hex()[:48]}: "
                           f"sim={a} recursive={b} dumb={c}")
            ah = simulate(w, hardened=True)
            ch = _dumb(w, hardened=True)
            if ah != ch:
                bad.append(f"R1h disagreement on {w.hex()[:48]}: "
                           f"sim={ah} dumb={ch}")
        # the arms the fixture must reach (PROTOCOL_PHP.md A2a rule 1)
        bad += self._visited_arms()
        return bad

    def _visited_arms(self):
        """Which arms the calls the driver ACTUALLY makes reach.

        ⚠ "the driver makes": windows are picked from a checksum-derived index,
        so an arm reached only by a window nothing selects has not been
        reached. `PROTOCOL_PHP.md` A2a rule 1 is what this discharges, and the
        arms are collected BY THE SIMULATION ITSELF rather than re-derived from
        the bytes -- a second derivation of "which arm ran" is a second place to
        be wrong."""
        if not self.entered:
            return []
        seen = set()
        for k in sorted(self._visited):
            win = self.buf[k * self.stride:(k + 1) * self.stride]
            _, arms = simulate(win, hardened=False, want_arms=True)
            seen |= arms
        bad = []
        adversarial = os.path.basename(self.path).startswith("adversarial")
        # ⚠ The ARM CENSUS binds the MEASURED corpus and not the adversarial
        # files. A2a rule 1's subject is the fixture the gate measures and the
        # model is checked against; an adversarial input is a single hand-built
        # window that exists to reach ONE state, and requiring it to reach
        # eleven would force decoy records into the file whose whole value is
        # that it carries none. What IS required of an adversarial input is the
        # defect arm, below.
        want = ["ins_str", "ins_idx_plain", "ins_idx_coll", "ins_str_update",
                "ins_idx_update", "del_str_memcmp", "del_idx", "del_miss",
                "chain_walk_step", "hash_unrolled", "hash_switch"]
        if not adversarial:
            for a in want:
                if a not in seen:
                    bad.append(f"the VISITED calls never reach arm `{a}`")
        # ⛔ AND THE ONE ARM A *MEASURED* CORPUS MUST NOT REACH. The gate's
        # stage 7h requires R1 and R1h to agree on every non-adversarial input,
        # and they agree exactly when no string-key delete takes `:464`'s left
        # disjunct. inputs/gen.py asserts the same thing from the other side.
        if not adversarial:
            if "DEFECT_left_disjunct_on_string_delete" in seen:
                bad.append("a NON-adversarial input reaches the defect arm; "
                           "R1 and R1h would disagree and stage 7h would fail")
        elif "DEFECT_left_disjunct_on_string_delete" not in seen:
            # ⭐ THE ONE DERIVED EXEMPTION, AND IT IS NOT BY NAME. A row needs a
            # must-NOT-fire adversarial input -- the SAME two keys in the OTHER
            # order, where the string-key delete finds the bucket it named and
            # R1 agrees with R1h. Such a window is recognisable from the ARMS it
            # reaches and from nothing else: it builds the collision
            # (`ins_idx_coll`) and the string delete still takes the memcmp arm
            # (`del_str_memcmp`). ⛔ Keying this on the FILENAME would be the
            # kind of exemption that survives a file being renamed into
            # something it is not.
            if not ("ins_idx_coll" in seen and "del_str_memcmp" in seen):
                bad.append("an ADVERSARIAL input neither reaches the defect arm "
                           "nor is an order control (it does not build a "
                           "collision that a string-key delete then resolves "
                           "correctly), so it demonstrates nothing")
        return bad


def build(path):
    return Model(path)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        m = build(p)
        print(f"{os.path.basename(p):32s} {m.describe()}  "
              f"exit={m.expected_exit} selfcheck={m.selfcheck()}")
