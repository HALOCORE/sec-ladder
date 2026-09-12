#!/usr/bin/env python3
"""ph53-iface-tail-uninit: the independent reference model the gate checks
against.

    python3 patterns-php/ph53-iface-tail-uninit/model.py inputs/*.bin

`harness/check.py` imports `build(path)` and uses the object it returns as the
oracle for every rung: `expected_stdout`, `expected_exit`, `sanitizer_expect`,
`work_per_call`, `iter_calls()` and the `helpers` the derived `ensures` is
evaluated against.

============================================================================
TWO IMPLEMENTATIONS, AND WHY THE SECOND ONE IS NOT THE FIRST IN DISGUISE
============================================================================
`PROTOCOL_PHP.md` §A2a rule 2. ph03 shipped for a whole task with its two
implementations computing DIFFERENT functions, because its corpus took one arm
of a two-armed branch and `inputs/` is not a domain.

  * `_window()` is an IMPERATIVE transcription of `c/kernel_hardened.c`, with
    the cursors named as the C names them and a mutable `slots` list whose
    unwritten entries are `None`.
  * `iface_fold()` is a RECURSIVE transcription of `verus.rs`'s spec functions
    -- `scan_d`, `scan_c`, `run_ops` -- carrying `(slots, acc)` as a returned
    pair rather than as mutated state, and reached only through the derived
    `ensures`.
  * `_dumb()` is a THIRD, deliberately naive spelling: materialise the final
    slot array first, then answer every query against it from scratch. It
    shares no code with either of the other two and it is what catches a fold
    that silently changed its range.

⚠⚠ **AND `None` IS WHERE THIS MODEL IS NOT THE C.** The C's unwritten slot
holds whatever `malloc` left there (R1) or NULL (R1h); this model's holds
`None`, which is *skipped*. So the model is the SAFE semantics -- what R2, R3,
R4 and R5 all implement -- and it agrees with both C rungs exactly where the
defect is not exercised, which is every measured window and three of the five
adversarial ones. On the two where it is not exercised-but-reached, the C's
answer is RECORDED by `check.py` stage 4 rather than required to agree, and
that difference is the row's result. ../NOTES.md §5.

⚠ **THIS MODEL CANNOT EXPRESS THE DEFECT AND THAT IS THE POINT.** There is no
Python spelling of "read a slot nobody wrote", so the second opinion is
genuinely independent of the mechanism -- and its inability to express it is a
small statement of the row's own ladder result.

============================================================================
THE u64
============================================================================
⛔ `CATALOGUE.md`'s `▸ benign` line for ph53 says the checksum is *"a fold of
the interface pointers read"*. **It cannot be**: a pointer is an ADDRESS, so
that fold differs between rungs and between runs for reasons no rung chose,
which is precisely what a cross-rung checksum exists to rule out
(`TASK_PHP_041.md` §2.3, `RECAP_PHP.md` open item 74). Every term below is an
index, an id or a count, plus `php_shim_tally()`:

    FILL         the decl index `d`
    QUERY_DEREF  the return value, then the matched pool `id` (0 if no match),
                 then the number of slots examined
    QUERY_CMP    whether it matched, then the decl INDEX it stopped at
    finally      xor php_shim_tally()

`php_shim_tally()` is reproduced ARITHMETICALLY (`_tally`) rather than by
linking the shim, because no Rust rung may link it (§B) -- and on this row the
reproduction is exact and O(1), because the kernel makes exactly one
allocation per call and none at all when `n_decl == 0`.
"""

import itertools
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "common-php"))
import slb  # noqa: E402

MASK = (1 << 64) - 1

#: `c/kernel.h` PH53_MAXD / PH53_MAXP. Check 5 parses the C and compares, so
#: the two cannot drift apart in this file's head.
MAXD = 16
MAXP = 8
HDR = 12
POOL_OFF = HDR
OPS_OFF = POOL_OFF + 8 * MAXP        # 76
OP_BYTES = 9

OP_FILL, OP_QD, OP_QC = 0, 1, 2

#: `common-php/emalloc_shim.h:642-648`. The four mixing constants and the four
#: fields, as `php_shim_tally()` writes them.
TALLY_ALLOC = 1000003
TALLY_FREE = 1000033
TALLY_CACHE_HIT = 1000037
TALLY_BYTES = 1000039


def _real_size(n):
    """`PHP_SHIM_REAL_SIZE`, `emalloc_shim.h:217`. Truncation T1's own
    rounding; `8 * n_decl` is already 8-aligned, so this is the identity here
    and is written out anyway because a reader should not have to check."""
    return (n + 7) & ~7


def _tally(n_decl):
    """`php_shim_tally()` after ONE kernel call, derived rather than measured.

    The kernel calls `php_shim_reset()` first, so every counter starts at
    zero; then `php_shim_erealloc(NULL, 8*n)` takes `_emalloc`'s malloc arm
    (`emalloc_shim.h:316-318` -> `:182`) because the cache was just wiped, and
    the teardown `php_shim_efree`s it. So:

        n_decl == 0   no allocation at all      -> 0
        n_decl >  0   n_alloc = n_free = 1, n_cache_hit = 0,
                      bytes_mallocked = REAL_SIZE(8 * n_decl)

    ⭐ **BOTH ARMS OF `zend_compile.c:2570` ARE THEREFORE VISIBLE IN THE u64**,
    which is a property of this row rather than of the rule that asked for the
    fold (`PROTOCOL_PHP.md` §B1.2) -- the defect's own branch lands in the
    checksum for free."""
    if n_decl == 0:
        return 0
    return ((1 * TALLY_ALLOC)
            ^ (1 * TALLY_FREE)
            ^ (0 * TALLY_CACHE_HIT)
            ^ (_real_size(8 * n_decl) * TALLY_BYTES)) & MASK


def _rd32(w, o):
    return w[o] | (w[o + 1] << 8) | (w[o + 2] << 16) | (w[o + 3] << 24)


def _rd64(w, o):
    return _rd32(w, o) | (_rd32(w, o + 4) << 32)


def cap_of(stride):
    """Ops the window has room for. Derived from the LENGTH, never trusted out
    of the blob -- the same discipline ph16 applies to its split."""
    return (stride - OPS_OFF) // OP_BYTES


def unpack(win):
    """(n_decl, n_pool, n_ops, pool, ops) exactly as every rung derives it."""
    cap = cap_of(len(win))
    n_decl = _rd32(win, 0) % (MAXD + 1)
    n_pool = 1 + _rd32(win, 4) % MAXP
    n_ops = _rd32(win, 8) % (cap + 1)
    pool = [_rd64(win, POOL_OFF + 8 * j) for j in range(MAXP)]
    ops = []
    for o in range(n_ops):
        p = OPS_OFF + OP_BYTES * o
        ops.append((win[p] % 3, _rd32(win, p + 1), _rd32(win, p + 5)))
    return n_decl, n_pool, n_ops, pool, ops


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
        self._win = []          # per window: (result, n_uninit_read, n_uninit_deref)
        self.any_uninit_read = False    # some call reads a slot nobody wrote
        self.any_uninit_deref = False   # ... and DEREFERENCES it
        if not self.truncated:
            self._run()

    # -- implementation 1: an imperative transcription of the C --------------
    @staticmethod
    def _instanceof_ex(slots, pool, target_id):
        """`instanceof_function_ex`'s interface loop -- zend_operators.c
        :1534-1535, the FAULTING consumer. Returns
        (hit, matched_id, examined, n_uninit).

        `None` is a slot nobody wrote. The C DEREFERENCES it; this model
        cannot, so it counts it and moves on -- see the module docstring."""
        n_uninit = 0
        examined = 0
        for i in range(len(slots)):
            examined = i + 1
            p = slots[i]
            if p is None:
                n_uninit += 1
                continue
            if pool[p] == target_id:
                return 1, pool[p], examined, n_uninit
        return 0, 0, examined, n_uninit

    @staticmethod
    def _inherit_scan(slots, target):
        """`zend_do_inherit_interfaces`'s dedup scan -- zend_compile.c:1951,
        the COMPARE-ONLY consumer. Returns (i, n_uninit).

        ⚠ It reads the slot and does NOT dereference it, which is why
        `d09cdd9f71f3` lands here at a different severity from the loop
        above."""
        n_uninit = 0
        i = 0
        for i in range(len(slots)):
            if slots[i] is None:
                n_uninit += 1
                continue
            if slots[i] == target:
                return i, n_uninit
        return len(slots), n_uninit

    def _window(self, off):
        """(result, n_uninit_read, n_uninit_deref) for one window."""
        win = self.buf[off: off + self.stride]
        n_decl, n_pool, n_ops, pool, ops = unpack(win)

        # zend_compile.c:3747-3748, then phase 1's :2591 n_decl times. `idx[k]`
        # is `opline->extended_value`, and it is k because the count starts at
        # zero -- written out because the row is about the count moving.
        num_interfaces = 0
        idx = []
        for _k in range(n_decl):
            idx.append(num_interfaces)
            num_interfaces += 1

        # phase 2, :2569-2572. Sized to the count; nothing written.
        slots = [None] * num_interfaces

        acc = 0
        n_read = n_deref = 0
        for (op, a, b) in ops:
            if op == OP_FILL:
                d = (a % n_decl) if n_decl else 0
                if n_decl:
                    slots[idx[d]] = b % n_pool
                acc = (acc * 31 + d) & MASK
            elif op == OP_QD:
                t = a % n_pool
                hit, matched, examined, nu = self._instanceof_ex(
                    slots, pool, pool[t])
                n_read += nu
                n_deref += nu
                acc = (acc * 31 + hit) & MASK
                acc = (acc * 31 + matched) & MASK
                acc = (acc * 31 + examined) & MASK
            else:
                t = a % n_pool
                i, nu = self._inherit_scan(slots, t)
                n_read += nu
                acc = (acc * 31 + int(i != num_interfaces)) & MASK
                acc = (acc * 31 + i) & MASK
        acc ^= _tally(n_decl)
        return acc & MASK, n_read, n_deref

    # -- simulation ---------------------------------------------------------
    def _run(self):
        acc = 0
        if OPS_OFF <= self.stride <= self.n_blob:
            self.entered = True
            self.nwin = self.n_blob // self.stride
            self._win = [self._window(k * self.stride) for k in range(self.nwin)]
            for _ in range(self.n_iters):
                k = (acc * self.nwin) >> 64
                r, nr, nd = self._win[k]
                if nr:
                    self.any_uninit_read = True
                if nd:
                    self.any_uninit_deref = True
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

    # -- implementation 2: verus.rs's spec functions, recursively ------------
    # ⚠ Written as loops over PURE transitions rather than as Python recursion:
    # `large.bin` carries 40 ops and 6 slots, which would be fine, but the
    # synthetic sweep goes to 16 slots x 40 ops and the shape should not depend
    # on `sys.setrecursionlimit`. Each step is exactly one unfolding of the
    # corresponding spec function.
    @staticmethod
    def _scan_d(slots, pool, i, n, t):
        """One application of ../verus.rs's `scan_d`, driven to its fixpoint.
        Returns (hit, matched_id, stop) where `stop` is the number of slots
        examined."""
        while i < n:
            s = slots[i]
            if s is not None and pool[s] == t:
                return 1, pool[s], i + 1
            i += 1
        return 0, 0, n

    @staticmethod
    def _scan_c(slots, i, n, t):
        """../verus.rs's `scan_c`: the index it stops at, or `n`."""
        while i < n:
            s = slots[i]
            if s is not None and s == t:
                return i
            i += 1
        return n

    @classmethod
    def _run_ops(cls, ops, k, no, n_decl, n_pool, pool, slots, acc):
        """../verus.rs's `run_ops`, one op per unfolding."""
        while k < no:
            (op, a, b) = ops[k]
            if op == OP_FILL:
                d = (a % n_decl) if n_decl else 0
                if n_decl:
                    slots = slots[:d] + (b % n_pool,) + slots[d + 1:]
                acc = (acc * 31 + d) & MASK
            elif op == OP_QD:
                t = pool[a % n_pool]
                hit, matched, stop = cls._scan_d(slots, pool, 0, len(slots), t)
                acc = (acc * 31 + hit) & MASK
                acc = (acc * 31 + matched) & MASK
                acc = (acc * 31 + stop) & MASK
            else:
                t = a % n_pool
                i = cls._scan_c(slots, 0, len(slots), t)
                acc = (acc * 31 + int(i != len(slots))) & MASK
                acc = (acc * 31 + i) & MASK
            k += 1
        return slots, acc

    def iface_fold(self, buf, off, ln):
        """`iface_fold` in ../verus.rs: what the kernel must return."""
        win = buf[off: off + ln]
        n_decl, n_pool, n_ops, pool, ops = unpack(win)
        slots = (None,) * n_decl
        _slots, acc = self._run_ops(ops, 0, n_ops, n_decl, n_pool, pool,
                                    slots, 0)
        return (acc ^ _tally(n_decl)) & MASK

    @property
    def helpers(self):
        return {"iface_fold": self.iface_fold}

    # -- implementation 3: a third, deliberately naive spelling -------------
    @staticmethod
    def _dumb(win):
        """Materialise the final slot array first, then answer every query
        against a snapshot taken at that query's position. Shares no code with
        `_window` or `iface_fold`."""
        n_decl, n_pool, n_ops, pool, ops = unpack(win)
        # snapshots[k] = the slot array as it stands just before op k
        snap = []
        cur = {}
        for (opc, a, b) in ops:
            snap.append(dict(cur))
            if opc == OP_FILL and n_decl:
                cur[a % n_decl] = b % n_pool
        terms = []
        for k, (opc, a, b) in enumerate(ops):
            s = snap[k]
            if opc == OP_FILL:
                terms.append((a % n_decl) if n_decl else 0)
            elif opc == OP_QD:
                tid = pool[a % n_pool]
                hit, mid, ex = 0, 0, n_decl
                for i in range(n_decl):
                    if i in s and pool[s[i]] == tid:
                        hit, mid, ex = 1, pool[s[i]], i + 1
                        break
                terms += [hit, mid, ex]
            else:
                t = a % n_pool
                stop = n_decl
                for i in range(n_decl):
                    if s.get(i) == t:
                        stop = i
                        break
                terms += [int(stop != n_decl), stop]
        acc = 0
        for v in terms:
            acc = (acc * 31 + v) & MASK
        return (acc ^ _tally(n_decl)) & MASK

    # -- what the kernel must do, per call ----------------------------------
    @property
    def work_per_call(self):
        """The window, in bytes -- `stride` -- from the file alone.

        `check.py::check_marginal_ir` needs one scalar per input and hard-fails
        on `work_per_call = 0`. The op count IS `(stride - 76) / 9`, i.e. an
        affine function of the stride, so the two denominators differ by a
        constant factor and the stride is the one the payload header fixes and
        an attacker cannot move. It is a strict over-estimate -- a call reads
        12 header bytes, 64 pool bytes and 9 bytes per op, and does
        `n_ops x n_decl` slot reads on top -- and an over-estimate raises the
        derived floor, which is the direction a floor should err.

        ⚠ The fixed per-call term is REAL and is not hidden: the 8-entry pool
        read and R1h's `memset` do not scale with the op count, and
        ../NOTES.md §8 decomposes the marginal rather than presenting it as a
        pure op rate."""
        return self.stride if self.entered else 0

    # -- sanitizer expectation ---------------------------------------------
    @property
    def sanitizer_expect(self):
        """⚠⚠ **EVERY INPUT IN `inputs/` IS `clean`, AND THAT IS THE ROW'S OWN
        RESULT RATHER THAN A CONCESSION.**

        The obvious adversarial input for this row is a `QUERY_DEREF` over a
        slot nobody wrote, and it is not in `inputs/`. `d09cdd9f71f3` zeroes
        the array and adds no consumer guard, so **every blob on which R1
        dereferences an unwritten slot is a blob on which R1h dereferences
        NULL** -- and `check.py` stage 7h requires R1h clean on every input in
        this directory, in terms, and says a per-input declaration there "would
        let a pattern declare its way out of the only thing this stage asks".
        That is `.memory-php/02-ladder.md` F31's standing limitation binding on
        a real row for the first time, and the resolution F31 itself prescribes
        is the one taken: the dereference evidence lives in
        `controls/r1h_consumers.py`, which builds both C arms and generates its
        own blobs. ../NOTES.md §5.

        What `inputs/` does carry is the half that is safe under every
        detector: `adversarial-cmp` reads an unwritten slot through the
        COMPARE-ONLY consumer, which does not dereference it, so no rung
        faults -- and `adversarial-shadowed` and `adversarial-covered` are its
        must-NOT-fire controls.

        ⚠ ASan does not detect an uninitialised read of an in-bounds slot at
        all -- that is MSan's job, and this row's read IS in bounds (CWE-824,
        not CWE-125). So even a `QUERY_DEREF` blob would not be reported by
        ASan *as an uninitialised read*; what ASan sees is the SEGV that
        follows, because ASan fills fresh allocations with `0xbe` and
        `0xbebebebebebebebe` is not a canonical address. `controls/` records
        that distinction rather than eliding it."""
        return "clean"

    # -- what a conforming driver does -------------------------------------
    @property
    def expected_exit(self):
        # ph53's payload allocates nothing from an attacker-controlled size --
        # the one allocation is inside the kernel and its size is
        # `8 * n_decl <= 128` -- so p02's exit 7 has no analogue here.
        # `slb_load` rejecting a short file is the only non-zero exit this
        # pattern's driver produces.
        return 5 if self.truncated else 0

    @property
    def expected_stdout(self):
        return "" if self.checksum is None else f"{self.checksum}\n"

    def describe(self):
        return (f"n_iters={self.n_iters} stride={self.stride} "
                f"n_blob={self.n_blob} nwin={self.nwin} calls={self.n_calls} "
                f"work/call={self.work_per_call}B "
                f"san={self.sanitizer_expect} "
                f"uninit_read={self.any_uninit_read} "
                f"uninit_deref={self.any_uninit_deref} "
                f"truncated={self.truncated} expected={self.checksum}")

    # -- driving BOTH implementations on windows no input file contains -----
    @staticmethod
    def _both(win):
        """(simulated, iface_fold) for an arbitrary window, off-corpus.

        `Model.__new__` skips `__init__` deliberately: `_window` and
        `iface_fold` read only `buf` and `stride`, so this drives the SHIPPED
        code paths on bytes chosen here rather than on bytes `inputs/` happens
        to carry."""
        m = Model.__new__(Model)
        m.buf, m.stride = win, len(win)
        return m._window(0)[0], m.iface_fold(win, 0, len(win))

    @staticmethod
    def _mkwin(stride, nd_w, np_w, no_w, pool_ids, ops):
        """Assemble a window from raw head words -- RAW, so the `%`s are
        exercised, including past a wrap."""
        def u32(v):
            return bytes((v & 0xFF, (v >> 8) & 0xFF, (v >> 16) & 0xFF,
                          (v >> 24) & 0xFF))
        out = [u32(nd_w), u32(np_w), u32(no_w)]
        for j in range(MAXP):
            v = pool_ids[j] if j < len(pool_ids) else 0
            out.append(u32(v & 0xFFFFFFFF) + u32((v >> 32) & 0xFFFFFFFF))
        for (o, a, b) in ops:
            out.append(bytes((o & 0xFF,)) + u32(a) + u32(b))
        body = b"".join(out)
        assert len(body) <= stride, (len(body), stride)
        return body + bytes(stride - len(body))

    @staticmethod
    def _synthetic_windows():
        """Windows spanning a domain `inputs/` cannot, built here, yielded as
        (label, bytes). ⚠ **`inputs/` is not the domain and must never be
        mistaken for it.**

        Six families, each isolating one thing the implementations could
        disagree about:

          a. ⭐ `n_decl_w = 0 .. 32` -- the whole of `PH53_MAXD`'s range and
             **past one wrap of the `% (MAXD + 1)`**, which is _040 §5.5's
             sweep. It reaches `n_decl == 0` (the dead arm of `:2570`), every
             count up to 16, and the wrap that makes 17 read as 0;
          b. `n_pool_w = 0 .. 15`, i.e. `n_pool` 1..8 and past one wrap;
          c. op ORDERINGS: fills-then-queries, queries-then-fills, interleaved,
             out-of-order fills, repeated fills of one slot, and no fills at
             all -- i.e. the uninitialised-slot cases the measured corpus is
             forbidden to contain;
          d. the four scan arms explicitly: match on the first slot, on the
             last, in the middle, and no match;
          e. duplicate pool ids, so the `id` identity test and the pool-index
             identity test are driven where they could disagree;
          f. `n_ops_w` past a wrap, and `n_ops == 0` (the whole op stream
             empty, so the u64 is the tally alone).
        """
        S = 221                      # cap_of(221) == 16
        ids = tuple(0x0C1A55_000000_01 + j for j in range(MAXP))
        F, D, C = OP_FILL, OP_QD, OP_QC

        # (a) + (f): every n_decl_w, with a stream that fills everything it can
        for nd_w in range(0, 33):
            nd = nd_w % (MAXD + 1)
            ops = [(F + 3, d, d) for d in range(min(nd, 12))]
            ops += [(D + 3, 0, 0), (C + 3, 1, 0), (D + 6, 7, 0), (C, 3, 0)]
            yield (f"n_decl_w={nd_w}",
                   Model._mkwin(S, nd_w, 7, len(ops), ids, ops))

        # (b): every n_pool_w
        for np_w in range(0, 16):
            ops = [(F, 0, 0), (F, 1, 3), (F, 2, 9), (D, 0, 0), (C, 3, 0),
                   (D, 9, 0), (C, 1, 0)]
            yield (f"n_pool_w={np_w}",
                   Model._mkwin(S, 3, np_w, len(ops), ids, ops))

        # (c): the op orderings, including every uninitialised-slot shape
        orders = {
            "fills-then-queries": [(F, 0, 0), (F, 1, 1), (F, 2, 2),
                                   (D, 0, 0), (C, 1, 0), (D, 2, 0), (C, 7, 0)],
            "queries-then-fills": [(D, 0, 0), (C, 1, 0), (F, 0, 0), (F, 1, 1),
                                   (F, 2, 2), (D, 0, 0), (C, 1, 0)],
            "interleaved": [(F, 0, 0), (D, 0, 0), (F, 1, 1), (C, 1, 0),
                            (F, 2, 2), (D, 2, 0), (C, 0, 0)],
            "fills-out-of-order": [(F, 2, 2), (F, 0, 0), (F, 1, 1),
                                   (D, 1, 0), (C, 2, 0)],
            "fill-repeated": [(F, 0, 0), (F, 0, 5), (F, 0, 1),
                              (D, 5, 0), (C, 5, 0), (D, 1, 0)],
            "no-fills": [(D, 0, 0), (C, 0, 0), (D, 7, 0), (C, 7, 0)],
            "empty-stream": [],
        }
        for nd in (0, 1, 3, 16):
            for label, ops in orders.items():
                yield (f"order={label} n_decl={nd}",
                       Model._mkwin(S, nd, 7, len(ops), ids, ops))

        # (d): the four scan arms, on both consumers, with n_decl = 4
        arms = {"first": 0, "last": 3, "mid": 2, "none": 6}
        for label, t in arms.items():
            ops = [(F, 0, 0), (F, 1, 1), (F, 2, 2), (F, 3, 3),
                   (D, t, 0), (C, t, 0)]
            yield (f"arm={label}", Model._mkwin(S, 4, 7, len(ops), ids, ops))

        # (e): duplicate pool ids -- the id test and the index test can only
        # disagree here, and the measured corpus deliberately has none
        dup = (7, 7, 7, 7, 9, 9, 0, 0)
        for nd in (0, 2, 5):
            ops = [(F, d, d) for d in range(nd)]
            ops += [(D, 0, 0), (C, 0, 0), (D, 4, 0), (C, 4, 0), (D, 6, 0)]
            yield (f"dup-ids n_decl={nd}",
                   Model._mkwin(S, nd, 7, len(ops), dup, ops))

        # (f): n_ops_w past a wrap, and n_ops == 0
        for no_w in (0, 1, 16, 17, 33, 0xFFFFFFFF):
            ops = [(F, 0, 0), (F, 1, 1), (D, 0, 0), (C, 1, 0)] * 4
            yield (f"n_ops_w={no_w}",
                   Model._mkwin(S, 2, 7, no_w, ids, ops))

    def selfcheck(self):
        """Five checks, four of them about this row specifically.

        1a. the imperative simulation against the recursive `iface_fold`, on
            the calls this input actually makes;
        1b. ⚠⚠ the same two implementations on **synthetic windows this file
            builds**, spanning `n_decl_w` 0..32 (past one wrap), `n_pool_w`
            0..15, seven op orderings x four counts, the four scan arms,
            duplicate pool ids and an empty op stream.
            `PROTOCOL_PHP.md` §A2a rule 2 -- 1a alone is what let ph03 ship a
            model that computed a different function from its own proof;
        1c. ⭐ **MUST-FIRE AND MUST-NOT-FIRE CONTROLS ON THE SWEEP ITSELF.**
            A sweep that cannot fail is not a check. Two mutants of
            `iface_fold` are driven over the same windows and each must be
            caught, and one deliberately EQUIVALENT rewrite must NOT be;
        2.  ⚠⚠ **THE ARM TABLE, OVER THE CALLS THE DRIVER ACTUALLY MAKES.**
            `inputs/gen.py::_check_arms` asserts the same table over EVERY
            window in the file, which is a superset condition: the driver picks
            windows from a checksum-derived index and need not visit them all.
            This is the sharper half and the one that is true of the
            measurement. It also re-asserts, negatively, that no VISITED
            benign call reads a slot nobody wrote;
        3.  every window's result is reproduced by a THIRD, deliberately dumb
            spelling (`_dumb`), which shares no code with either of the two;
        4.  the constants this row turns on -- `PH53_MAXD`, `PH53_MAXP`,
            `PH53_OPS_OFF`, `PH53_OP_BYTES` -- still equal what `c/kernel.h`
            compiles against. This file writes them as Python integers and
            check 4 parses the header's own `#define`s and compares, so the
            two cannot drift apart in this file's head;
        5.  `_tally()` against the shim's own mixing constants, parsed out of
            `common-php/emalloc_shim.h` rather than remembered.
        """
        problems = []

        # 1a
        for c in self.sample_calls(8):
            want = self.iface_fold(c["buf"], c["off"], c["len"])
            if want != c["result"]:
                problems.append(
                    f"simulated result {c['result']} != iface_fold() {want} "
                    f"at off={c['off']}")
                break

        # 1b
        wins = list(self._synthetic_windows())
        for label, win in wins:
            sim, helper = self._both(win)
            if sim != helper:
                problems.append(
                    f"synthetic window [{label}]: simulated {sim} != "
                    f"iface_fold() {helper}. The two implementations have come "
                    f"apart OFF the corpus; inputs/ cannot see this and it is "
                    f"why this sweep exists (PROTOCOL_PHP.md A2a rule 2)")
                break

        # 1c: the sweep's own controls
        problems += self._sweep_controls(wins)

        # 2
        adversarial = os.path.basename(self.path).startswith("adversarial")
        if not adversarial and self.entered:
            problems += self._arm_table()

        # 3
        for k in range(self.nwin):
            got = self._win[k][0]
            want = self._dumb(self.buf[k * self.stride:(k + 1) * self.stride])
            if got != want:
                problems.append(f"window {k}: {got} != third spelling {want}")
                break

        # 4
        cconst = _c_constants()
        want = {"PH53_MAXD": MAXD, "PH53_MAXP": MAXP, "PH53_OP_BYTES": OP_BYTES,
                "PH53_HDR_BYTES": HDR}
        for k, v in want.items():
            if cconst.get(k) != v:
                problems.append(
                    f"c/kernel.h compiles against {k}={cconst.get(k)}, this "
                    f"model uses {v}; every index in this row means something "
                    f"else under that constant")
        if cconst.get("OPS_OFF") != OPS_OFF:
            problems.append(
                f"c/kernel.h's PH53_OPS_OFF derives to {cconst.get('OPS_OFF')}, "
                f"this model uses {OPS_OFF}")

        # 5
        sconst = _shim_constants()
        for name, v in (("n_alloc", TALLY_ALLOC), ("n_free", TALLY_FREE),
                        ("n_cache_hit", TALLY_CACHE_HIT),
                        ("bytes_mallocked", TALLY_BYTES)):
            if sconst.get(name) != v:
                problems.append(
                    f"php_shim_tally() mixes {name} with {sconst.get(name)}, "
                    f"this model uses {v} -- the arithmetic reproduction the "
                    f"four Rust rungs carry would be wrong too")
        return problems

    def _sweep_controls(self, wins):
        """⭐ MUST-FIRE and MUST-NOT-FIRE on check 1b itself.

        `PROTOCOL_PHP.md` §H: a check that cannot fail is not a check, and
        *"three green rows say nothing about what the validator does to a row
        that should fail"*. Each mutant is a one-line change to `iface_fold`'s
        recursive half, applied by monkey-patching the pure static methods the
        sweep drives, and each must be caught by at least one synthetic window
        -- including M3, whose whole point is that the measured corpus CANNOT
        catch it because it has no uninitialised slot."""
        bad = []
        orig_d, orig_c = Model._scan_d, Model._scan_c

        def sweep_catches():
            for label, win in wins:
                sim, helper = self._both(win)
                if sim != helper:
                    return label
            return None

        try:
            # M1: `scan_c` returns the count instead of the index on a match --
            # the "no match" and "match on the last slot" answers collide.
            Model._scan_c = staticmethod(lambda slots, i, n, t: n)
            m1 = sweep_catches()
            Model._scan_c = orig_c

            # M2: `scan_d` forgets to stop, so `examined` is always `n`.
            def d_noscan(slots, pool, i, n, t):
                h, mid = 0, 0
                while i < n:
                    s = slots[i]
                    if s is not None and pool[s] == t and h == 0:
                        h, mid = 1, pool[s]
                    i += 1
                return h, mid, n
            Model._scan_d = staticmethod(d_noscan)
            m2 = sweep_catches()
            Model._scan_d = orig_d

            # M3 ⭐: treat an UNWRITTEN slot as a match candidate holding pool
            # index 0. This is the mutant the measured corpus cannot see -- it
            # has no unwritten slot at query time, by construction -- so it is
            # the one that measures whether the sweep buys anything at all.
            def d_uninit_is_zero(slots, pool, i, n, t):
                while i < n:
                    s = slots[i] if slots[i] is not None else 0
                    if pool[s] == t:
                        return 1, pool[s], i + 1
                    i += 1
                return 0, 0, n
            Model._scan_d = staticmethod(d_uninit_is_zero)
            m3 = sweep_catches()
            Model._scan_d = orig_d

            # N1 MUST-NOT-FIRE: an equivalent rewrite of `scan_c` -- the same
            # predicate with the two conjuncts swapped and an explicit
            # `enumerate`. If this one "fires", the sweep is detecting the
            # SPELLING and not the function.
            def c_equiv(slots, i, n, t):
                for j in range(i, n):
                    if t == slots[j] and slots[j] is not None:
                        return j
                return n
            Model._scan_c = staticmethod(c_equiv)
            n1 = sweep_catches()
            Model._scan_c = orig_c
        finally:
            Model._scan_d, Model._scan_c = orig_d, orig_c

        for tag, hit in (("M1 scan_c returns n on a match", m1),
                         ("M2 scan_d never stops early", m2),
                         ("M3 an unwritten slot reads as pool index 0", m3)):
            if hit is None:
                bad.append(f"sweep control {tag}: MUST-FIRE mutant was NOT "
                           f"caught by any of the {len(wins)} synthetic "
                           f"windows, so check 1b is not checking it")
        if n1 is not None:
            bad.append(f"sweep control N1: an EQUIVALENT rewrite of scan_c was "
                       f"reported as a disagreement at [{n1}], so check 1b is "
                       f"keyed on the spelling and not on the function")
        return bad

    def _arm_table(self):
        """`PROTOCOL_PHP.md` §A2a rule 1, over the VISITED calls."""
        decl_arms, ops_seen, q_arms, consumers = set(), set(), set(), set()
        uncovered = 0
        seen = set()
        for c in self.iter_calls():
            if c["off"] in seen:
                continue
            seen.add(c["off"])
            win = self.buf[c["off"]:c["off"] + c["len"]]
            n_decl, n_pool, n_ops, pool, ops = unpack(win)
            decl_arms.add(n_decl > 0)
            written = [None] * n_decl
            for (op, a, b) in ops:
                ops_seen.add(op)
                if op == OP_FILL:
                    if n_decl:
                        written[a % n_decl] = b % n_pool
                    continue
                consumers.add(op)
                if any(w is None for w in written):
                    uncovered += 1
                t = a % n_pool
                if n_decl == 0:
                    q_arms.add("zero")
                elif written[0] == t:
                    q_arms.add("first")
                elif t not in written:
                    q_arms.add("none")
                elif written[n_decl - 1] == t and t not in written[:n_decl - 1]:
                    q_arms.add("last")
                else:
                    q_arms.add("mid")
        bad = []
        if decl_arms != {False, True}:
            bad.append(f"the VISITED calls reach `ce->num_interfaces > 0` == "
                       f"{sorted(decl_arms)}, want both -- the false arm "
                       f"allocates nothing at all")
        if ops_seen != {OP_FILL, OP_QD, OP_QC}:
            bad.append(f"the VISITED calls reach op codes {sorted(ops_seen)}, "
                       f"want all of [0 FILL, 1 QUERY_DEREF, 2 QUERY_CMP]")
        if consumers != {OP_QD, OP_QC}:
            bad.append(f"the VISITED calls reach consumers {sorted(consumers)}, "
                       f"want both -- d09cdd9f71f3 lands at two different "
                       f"severities on them and that is the row")
        want_q = {"zero", "first", "last", "none", "mid"}
        if q_arms != want_q:
            bad.append(f"the VISITED calls reach scan arms {sorted(q_arms)}, "
                       f"want {sorted(want_q)}")
        if uncovered:
            bad.append(f"{uncovered} VISITED QUERY op(s) run with a slot still "
                       f"unwritten, i.e. ON THE DEFECT. check.py stage 7h "
                       f"requires R1h clean on every input in inputs/, and R1h "
                       f"still NULL-dereferences an unwritten slot")
        return [f"visited-call arm coverage: {b}" for b in bad]


def _c_constants():
    """`c/kernel.h`'s own `#define`s. Parsed rather than trusted: check 4."""
    import re
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "c", "kernel.h")
    txt = open(p).read()
    out = {}
    for k in ("PH53_MAXD", "PH53_MAXP", "PH53_HDR_BYTES", "PH53_OP_BYTES"):
        m = re.search(r"#define\s+" + k + r"\s+(\d+)", txt)
        if m:
            out[k] = int(m.group(1))
    # PH53_OPS_OFF is derived in the header; re-derive it the same way rather
    # than hard-coding 76 in two places.
    if re.search(r"#define\s+PH53_POOL_OFF\s+PH53_HDR_BYTES", txt) and \
       re.search(r"#define\s+PH53_POOL_BYTES\s+\(8\s*\*\s*PH53_MAXP\)", txt) and \
       re.search(r"#define\s+PH53_OPS_OFF\s+\(PH53_POOL_OFF\s*\+\s*PH53_POOL_BYTES\)",
                 txt):
        out["OPS_OFF"] = out.get("PH53_HDR_BYTES", 0) + 8 * out.get("PH53_MAXP", 0)
    return out


def _shim_constants():
    """`php_shim_tally()`'s four mixing constants, keyed by the field each one
    multiplies. Parsed out of `common-php/emalloc_shim.h`: check 5."""
    import re
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "..", "..", "common-php", "emalloc_shim.h")
    txt = open(p).read()
    m = re.search(r"php_shim_tally\(void\)\s*\{(.*?)\n\}", txt, re.S)
    if not m:
        return {}
    return {f: int(c) for f, c in
            re.findall(r"php_shim_ag\.(\w+)\s*\*\s*(\d+)u?", m.group(1))}


def build(path):
    return Model(path)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        m = build(p)
        probs = m.selfcheck()
        n = len(list(Model._synthetic_windows()))
        print(f"{os.path.basename(p):28s} {m.describe()}  "
              f"exit={m.expected_exit} "
              f"selfcheck={'ok (%d synthetic windows, 3 must-fire, 1 '
                          'must-NOT-fire)' % n if not probs else probs}")
