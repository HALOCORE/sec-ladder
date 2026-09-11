#!/usr/bin/env python3
"""ph64-callback-frees-cursor: the independent reference model the gate checks.

The API is documented at the top of `patterns/p01-array-sum/model.py`; this file
notes only where ph64 differs.

    bindings      buf/off/len/buf_len/result. The kernel builds and destroys its
                  whole tick list inside one call and writes nothing the caller
                  can see; what escapes is the u64.
    work_per_call the WINDOW, in bytes -- `stride`, constant across every call
                  on a given input. Argued below.
    sanitizer     derived, not tabulated: an input "fires" exactly when some
                  call the driver actually makes leaves R1's cursor pointing at
                  a block that has been freed AND handed back out, so that
                  `element->next` is a value the WINDOW chose.

⚠⚠ WHICH ALGORITHM THIS MODEL IMPLEMENTS, BECAUSE IT IS NOT R1's. It is the
5.0.0 tick dispatch **with `562f886ecb14` applied**, which is exactly
`c/kernel_hardened.c` and exactly R2-R5:

    R1     Zend/zend_llist.c:186-193 + basic_functions.c:2102-2161 as shipped
           5.0.0 .. master -- CRASH-086
    R1h    + `if (ret && tick_fe1->calling) { <warn>; return 0; }` in
           `user_tick_function_compare`  <- 562f886ecb14, php-5.2.2 .. master
    R2-R5  the same function, memory-safe

⭐ The fix is CORRECT on the tick list and this model can say why in one line:
`zend_llist_apply` advances only after `func` returns, and
`user_tick_function_call` holds `calling == 1` for exactly the duration of that
call, so **every element any live walk's cursor points at has `calling == 1`** --
which is precisely the set the guard refuses to free. Elements the guard does
NOT protect need no protection, because `DEL_LLIST_ELEMENT` repairs both
neighbours' links. TASK_PHP_031_REPORT §4.2; NOTES.md §4.

⚠ **The fix is in a THIRD function** -- `user_tick_function_compare`, which is
neither the loop that faults nor the statement the corpus cites -- so this model
puts the guard in `_compare`, where upstream put it, and NOT at either
dereference. `zend_llist_apply`'s body is unchanged at every tag from php-5.0.0
to master.

Two independent implementations, as p01/p02/p16 and ph03/ph07 do:

  * the **structural simulation** (`_window`) builds a real doubly-linked list
    of `_Node`s with `head`/`tail`/`next`/`prev`, walks it with a cursor, runs
    `_del_element`'s comparator loop, and drives a **per-size-class LIFO
    allocator** that reproduces `zend_alloc.c`'s cache -- including handing the
    just-freed element back to the next same-class request, which is the whole
    mechanism. It is parameterised by the rung, so it computes R1 as well as
    R1h and the difference between them is a measurement rather than a claim;
  * the **closed form** `llist_fold` -- the one the derived `ensures` is
    evaluated against -- derives the visited set, the deletion schedule and all
    four allocator counters ARITHMETICALLY, with no list, no nodes, no cursor
    and no event replay, mirroring the Verus spec functions `visit_fold`,
    `sched_of` and `tally_of` in ../verus.rs.

`selfcheck()` runs them against each other -- on the shipped inputs AND on
synthetic windows it builds itself over a domain no input file contains -- and a
disagreement is reported there rather than absorbed into a green line.

⚠⚠ **THE SYNTHETIC SWEEP IS NOT DECORATION.** `PROTOCOL_PHP.md` §A2a rule 2:
*a second implementation is only as strong as the domain it is exercised over,
and `inputs/` is not a domain.* ph03 shipped for a full task with its two
implementations computing different functions. Here the branch is
`DEL_LLIST_ELEMENT`'s FOUR arms (`prev`/no `prev` x `next`/no `next`) crossed
with four `mode`s and the reuse flag; this sweep drives both implementations
over every combination at list lengths a fixed stride cannot carry.
"""

import itertools
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "common"))
import slb  # noqa: E402

MASK = (1 << 64) - 1

# `php_shim_tally()`'s multipliers -- common-php/emalloc_shim.h:642-648.
T_ALLOC, T_FREE, T_HIT, T_BYTES = 1000003, 1000033, 1000037, 1000039

# `zend_alloc.h:63-64` via common-php/emalloc_shim.h:190-191.
MAX_CACHED_MEMORY, MAX_CACHED_ENTRIES = 11, 256

# ⚠ THE LAYOUT IS THE ORACLE, so these three numbers are load-bearing and they
# are NOT asserted here -- they are asserted IN THE C, at compile time, by
# `c/kernel.c`'s `ph64_layout_assert`, which is stronger than anything this file
# could parse. `sizeof(zend_llist_element) == 24` (two pointers plus `char
# data[1]` padded), `sizeof(user_tick_function_entry) == 16`, and
# `zend_llist_add_element` requests `24 + 16 - 1 = 39`, whose `REAL_SIZE` is 40
# and whose cache index is `40 >> 3 = 5 < 11`. THAT is why a freed element is
# handed straight back out instead of returned to malloc, and it is why
# `crashes_pristine_5_0_0` is False on this row.
SZ_ELEM, SZ_ENTRY, SZ_NAME = 24, 16, 8
REQ_ELEM = SZ_ELEM + SZ_ENTRY - 1                       # 39
SLOT = 4                        # window bytes per registered tick function

HEAD = 16                       # [u32 nent][u32 trig][u32 mode][u32 post]
UNREG_NONE, UNREG_SELF, UNREG_AHEAD, UNREG_BEHIND = 0, 1, 2, 3

# The four `DEL_LLIST_ELEMENT` arms -- zend_llist.c:73-88. `inputs/gen.py`
# asserts the measured corpus reaches all four (PROTOCOL_PHP.md A2a rule 1).
ARMS = ("mid", "head", "tail", "only")


def _rd32(b, i):
    return b[i] | (b[i + 1] << 8) | (b[i + 2] << 16) | (b[i + 3] << 24)


def _name_of(win, i):
    """Entry `i`'s 8-byte `arguments` block: `[u32 le id][4 window bytes]`.

    The id half is what makes names unique BY CONSTRUCTION, so "unregister my
    own name" cannot silently mean somebody else's -- the way TASK_PHP_031's own
    first probe was wrong (its report §8.8)."""
    src = HEAD + (i - 1) * SLOT
    return bytes((i & 0xFF, (i >> 8) & 0xFF, (i >> 16) & 0xFF, (i >> 24) & 0xFF,
                  win[src], win[src + 1], win[src + 2], win[src + 3]))


def _decode(win, ln):
    """The window's four head words, resolved. Shared by BOTH implementations
    because it is parsing and not semantics -- it is `c/kernel.c`'s own six
    lines, and a second spelling of `%` would test Python, not the row."""
    nmax = (ln - HEAD) // SLOT
    n = 1 + (_rd32(win, 0) % nmax)
    return {"nmax": nmax, "n": n,
            "trigger": _rd32(win, 4) % (n + 1),
            "mode": _rd32(win, 8) % 4,
            "reuse": (_rd32(win, 8) >> 16) & 1,
            "post": _rd32(win, 12) % (n + 1)}


class Wild(Exception):
    """R1's cursor pointed at a block that had been freed AND handed back out,
    so `element->next` is a value the window chose. The C dereferences it; this
    model refuses to invent a trajectory for it and reports the fact."""


class _Alloc:
    """`zend_alloc.c`'s size-class cache, counters only.

    `emalloc(size)` rounds to `REAL_SIZE = (size + 7) & ~7`, indexes
    `real >> 3`, and takes the LIFO top of that class if there is one;
    `efree` pushes it back unless the class already holds `MAX_CACHED_ENTRIES`.
    `bytes_mallocked` counts only what actually reached `malloc`, i.e. the
    misses -- common-php/emalloc_shim.h:384 and its own §"THE FOURTH FIELD"
    warning.

    ⚠ The stacks hold the freed OBJECT, not just a count, because this row's
    oracle IS the identity of the block handed back."""

    def __init__(self):
        self.stack = [[] for _ in range(MAX_CACHED_MEMORY)]
        self.n_alloc = self.n_free = self.n_hit = self.bytes = 0

    def alloc(self, size):
        real = (size + 7) & ~7
        idx = real >> 3
        self.n_alloc += 1
        if idx < MAX_CACHED_MEMORY and self.stack[idx]:
            self.n_hit += 1
            return self.stack[idx].pop()        # the recycled block
        self.bytes += real
        return None

    def free(self, size, obj=None):
        real = (size + 7) & ~7
        idx = real >> 3
        self.n_free += 1
        if idx < MAX_CACHED_MEMORY and len(self.stack[idx]) < MAX_CACHED_ENTRIES:
            self.stack[idx].append(obj)

    def tally(self):
        return (((self.n_alloc * T_ALLOC) & MASK)
                ^ ((self.n_free * T_FREE) & MASK)
                ^ ((self.n_hit * T_HIT) & MASK)
                ^ ((self.bytes * T_BYTES) & MASK)) & MASK


class _Node:
    """`zend_llist_element` plus the `user_tick_function_entry` in its `data`."""
    __slots__ = ("next", "prev", "name", "calling", "freed", "recycled")

    def __init__(self, name):
        self.next = self.prev = None
        self.name = name
        self.calling = 0
        self.freed = False
        self.recycled = False       # freed AND handed back to a later emalloc


class _List:
    __slots__ = ("head", "tail", "count")

    def __init__(self):
        self.head = self.tail = None
        self.count = 0


class Model:
    """Simulates ../spec.md's driver loop and kernel from the file alone."""

    def __init__(self, path):
        f = slb.read(path)
        self.path = path
        self.n_iters = f.n_iters
        self.declared_len = f.declared_len
        self.truncated = f.truncated
        self.payload = f.payload[: f.declared_len]
        self.stride, self.buf = slb.head1_u64_bytes(self.payload)
        self.n_blob = len(self.buf)
        self.n_calls = 0
        self.checksum = None
        self.entered = False
        self.any_wild = False
        self.nwin = 0
        self._win = []              # per window: (result, r1_state, info)
        if not self.truncated:
            self._run()

    # -- implementation 1 of 2: the structural simulation -------------------
    @staticmethod
    def _simulate(win, ln, hardened):
        """One window, one rung. A transcription of `c/kernel*.c`.

        Returns `(u64, info)` and raises `Wild` when R1's cursor lands on a
        recycled block. `hardened=False` is R1 (5.0.0), `True` is R1h
        (`562f886ecb14`)."""
        d = _decode(win, ln)
        n, trigger, mode, reuse, post = (d["n"], d["trigger"], d["mode"],
                                         d["reuse"], d["post"])
        al = _Alloc()
        lst = _List()
        st = {"fold": 0, "visits": 0, "dtors": 0, "refusals": 0,
              "arms": set(), "reuse_block": None}

        def compare(node, key_name):
            """basic_functions.c:2146-2161, plus 562f886ecb14 when hardened."""
            ret = 1 if node.name == key_name else 0
            if hardened and ret and node.calling:
                st["refusals"] += 1          # PROJECTED php_error_docref
                return 0
            return ret

        def del_element(key_name):
            """zend_llist.c:91-104 expanding DEL_LLIST_ELEMENT (:73-88)."""
            current = lst.head
            while current is not None:
                nxt = current.next
                if compare(current, key_name):
                    if current.prev is not None:
                        current.prev.next = current.next
                        arm = "tail" if current.next is None else "mid"
                    else:
                        lst.head = current.next
                        arm = "only" if current.next is None else "head"
                    if current.next is not None:
                        current.next.prev = current.prev
                    else:
                        lst.tail = current.prev
                    st["arms"].add(arm)
                    st["dtors"] += 1
                    al.free(SZ_NAME)                  # dtor: efree(arguments)
                    current.freed = True
                    al.free(REQ_ELEM, current)        # pefree(current)
                    lst.count -= 1
                    return
                current = nxt

        def unregister(i):
            """basic_functions.c:2840-2862, narrowed."""
            al.alloc(SZ_NAME)
            del_element(_name_of(win, i))
            al.free(SZ_NAME)

        def userland(node):
            """basic_functions.c:2111-2116, projected."""
            nm = node.name                            # copied before any free
            me = _rd32(nm, 0)
            st["fold"] = (st["fold"] * 31 + me) & MASK
            st["fold"] = (st["fold"] * 31 + _rd32(nm, 4)) & MASK
            st["visits"] += 1
            if me != trigger:
                return
            if mode == UNREG_SELF:
                unregister(me)
            elif mode == UNREG_AHEAD:
                if me < n:
                    unregister(me + 1)
            elif mode == UNREG_BEHIND:
                if me > 1:
                    unregister(me - 1)
            if reuse and st["reuse_block"] is None:
                got = al.alloc(REQ_ELEM)
                if got is not None:
                    got.recycled = True               # the fill overwrites next
                st["reuse_block"] = got if got is not None else True

        # ---- register_tick_function x N  (basic_functions.c:2799-2835) ----
        for i in range(1, n + 1):
            al.alloc(SZ_NAME)
            node = _Node(_name_of(win, i))
            al.alloc(REQ_ELEM)
            node.prev = lst.tail
            node.next = None
            if lst.tail is not None:
                lst.tail.next = node
            else:
                lst.head = node
            lst.tail = node
            lst.count += 1

        # ---- zend_llist_apply(&list, user_tick_function_call)  :186-193 ----
        element = lst.head
        while element is not None:
            if element.recycled:
                raise Wild("the walk's cursor is a block that was freed and "
                           "handed back out; element->next is window data")
            if not element.calling:                   # :2108
                element.calling = 1                   # :2109
                userland(element)                     # :2111-2116
                element.calling = 0                   # :2135  <== SITE C
            if element.recycled:
                raise Wild("the callback's own allocation recycled the block "
                           "the cursor holds; element->next is window data")
            element = element.next                    # :190  <== SITE L

        # ---- top-level unregister_tick_function(post) ----------------------
        if post:
            unregister(post)

        count_after = lst.count
        acc = st["fold"]
        for v in (count_after, st["dtors"], st["visits"], st["refusals"], n):
            acc = (acc * 31 + v) & MASK
        if st["reuse_block"] is not None:
            al.free(REQ_ELEM)
        cur = lst.head                                # zend_llist_destroy
        while cur is not None:
            nxt = cur.next
            st["dtors"] += 1
            al.free(SZ_NAME)
            al.free(REQ_ELEM, cur)
            cur = nxt
        info = dict(d, visits=st["visits"], count_after=count_after,
                    refusals=st["refusals"], arms=frozenset(st["arms"]),
                    n_alloc=al.n_alloc, n_free=al.n_free, n_hit=al.n_hit,
                    bytes=al.bytes)
        return (acc ^ al.tally()) & MASK, info

    def _window(self, off):
        """(result, r1_state, info) for the window at `off`.

        `result` is R1h's -- the function R1h and R2-R5 all compute.
        `r1_state` says what R1 does with the same window:

          "same"    identical u64: nothing was freed under the cursor;
          "latent"  R1 completes and its u64 DIFFERS. The block went into
                    `AG(cache)[5]`, nothing scribbled the payload, the walk
                    visited the same entries in the same order -- but `l->count`
                    and the allocator tally record a free R1h refused. THIS IS
                    THE CORPUS'S OWN TRIGGER and it is why
                    `crashes_pristine_5_0_0` is False;
          "wild"    the same free plus one same-class `emalloc` inside the same
                    callback: the block comes straight back out, the callback's
                    own bytes land in `element->next`, and R1 follows them."""
        win = self.buf[off: off + self.stride]
        r1h, info = self._simulate(win, self.stride, True)
        try:
            r1, _ = self._simulate(win, self.stride, False)
            state = "same" if r1 == r1h else "latent"
        except Wild:
            state = "wild"
        return r1h, state, info

    def r1_result(self, off):
        """R1's own u64, or None when R1 goes wild. Not used by the gate; it is
        what `controls/oracle.py` compares against."""
        try:
            return self._simulate(self.buf[off: off + self.stride],
                                  self.stride, False)[0]
        except Wild:
            return None

    # -- simulation --------------------------------------------------------
    def _run(self):
        acc = 0
        if 24 <= self.stride <= 268435456 and self.stride <= self.n_blob:
            self.entered = True
            self.nwin = self.n_blob // self.stride
            self._win = [self._window(k * self.stride) for k in range(self.nwin)]
            for _ in range(self.n_iters):
                k = (acc * self.nwin) >> 64
                r, state, _ = self._win[k]
                if state == "wild":
                    self.any_wild = True
                acc = (acc * 31 + r) & MASK
            self.n_calls = self.n_iters
        self.checksum = acc

    def iter_calls(self):
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

    # -- implementation 2 of 2: the closed form ----------------------------
    # This is what the derived `ensures` is evaluated against, so it must not be
    # the simulation in disguise. It has NO list, NO nodes, NO cursor and NO
    # event replay: it derives the schedule and then counts. It mirrors
    # ../verus.rs's `sched_of` / `visit_fold` / `tally_of`.
    @staticmethod
    def _sched(win, ln):
        """Who is deleted, when, and how many blocks move -- arithmetically.

        Under R1h the ONLY deletion the walk can make is of an element that is
        not executing, and `DEL_LLIST_ELEMENT` repairs both neighbours, so the
        visited set is `1..n` minus at most one entry AHEAD of the cursor."""
        d = _decode(win, ln)
        n, trig, mode, reuse, post = (d["n"], d["trigger"], d["mode"],
                                      d["reuse"], d["post"])
        acts = 1 <= trig <= n
        walk_call = acts and (mode == UNREG_SELF
                              or (mode == UNREG_AHEAD and trig < n)
                              or (mode == UNREG_BEHIND and trig > 1))
        if not acts or mode == UNREG_SELF or mode == UNREG_NONE:
            walk_del = 0                       # SELF is REFUSED by 562f886ecb14
        elif mode == UNREG_AHEAD:
            walk_del = trig + 1 if trig < n else 0
        else:
            walk_del = trig - 1 if trig > 1 else 0
        refusals = 1 if (acts and mode == UNREG_SELF) else 0
        skipped = walk_del if walk_del > trig else 0      # deleted ahead of us
        post_del = post if (post and post != walk_del) else 0
        return dict(d, acts=acts, walk_call=walk_call, walk_del=walk_del,
                    refusals=refusals, skipped=skipped, post_del=post_del,
                    reuse_hit=1 if (reuse and acts and walk_del) else 0)

    def llist_fold(self, buf, off, ln):
        """`llist_fold` in ../verus.rs: what the kernel must return."""
        win = buf[off: off + ln]
        s = self._sched(win, ln)
        n = s["n"]

        acc = 0
        for i in range(1, n + 1):
            if i == s["skipped"]:
                continue
            nm = _name_of(win, i)
            acc = (acc * 31 + _rd32(nm, 0)) & MASK
            acc = (acc * 31 + _rd32(nm, 4)) & MASK
        visits = n - (1 if s["skipped"] else 0)
        dels = (1 if s["walk_del"] else 0) + (1 if s["post_del"] else 0)
        for v in (n - dels, dels, visits, s["refusals"], n):
            acc = (acc * 31 + v) & MASK

        # ---- the four allocator counters, counted rather than replayed -----
        reuse_alloc = 1 if (s["reuse"] and s["acts"]) else 0
        post_call = 1 if s["post"] else 0
        n_alloc = 2 * n + s["walk_call"] + reuse_alloc + post_call
        n_free = ((2 if s["walk_del"] else 0) + s["walk_call"]
                  + (2 if s["post_del"] else 0) + post_call
                  + reuse_alloc + 2 * (n - dels))
        # A class-1 (8-byte) request hits iff the walk's own key block has
        # already been pushed back; a class-5 (40-byte) request hits iff the
        # walk really freed an element, which is exactly what R1h refuses to let
        # SELF do. Registration is always a miss: `php_shim_reset` empties the
        # cache and no free precedes it.
        post_hit = 1 if (post_call and s["walk_call"]) else 0
        n_hit = s["reuse_hit"] + post_hit
        by = (SZ_NAME + 40) * n
        by += 8 * s["walk_call"]
        by += 40 * (reuse_alloc - s["reuse_hit"])
        by += 8 * (post_call - post_hit)
        tal = (((n_alloc * T_ALLOC) & MASK) ^ ((n_free * T_FREE) & MASK)
               ^ ((n_hit * T_HIT) & MASK) ^ ((by * T_BYTES) & MASK)) & MASK
        return (acc ^ tal) & MASK

    @property
    def helpers(self):
        return {"llist_fold": self.llist_fold}

    # -- what the kernel must do, per call ---------------------------------
    @property
    def work_per_call(self):
        """The window, in bytes -- `stride` -- from the file alone.

        **Why the window and not `n`.** `check.py::check_marginal_ir` needs one
        scalar per input and hard-fails on `work_per_call = 0`. The quantity the
        kernel's cost really scales with is `n`, the number of tick functions
        registered -- and `n` is read OUT OF THE DATA (`1 + nent % nmax`), so
        denominating in it would put the unit under the attacker's control and
        collapse it on a window that registers one entry.

        The window is the unit that does not move: it is fixed by the payload
        header, identical on every call of a given input, and it BOUNDS `n`
        (`n <= (stride - 16) / 8`). `inputs/gen.py` draws `n` as a fixed
        FRACTION of that bound, so the work really does scale with the
        denominator. It is a strict over-estimate -- eight window bytes buy one
        entry, and one entry is far more than eight instructions -- and an
        over-estimate raises the derived floor, which is the direction a floor
        should err."""
        return self.stride if self.entered else 0

    # -- sanitizer expectation ---------------------------------------------
    @property
    def sanitizer_expect(self):
        """Derived from the simulated run, never tabulated per file.

        ⚠⚠ AND THE ANSWER IS A FINDING, NOT A MATCH (PROTOCOL_PHP.md §A4). The
        corpus records `asan_kind: heap-use-after-free` for CRASH-086. On the
        FAITHFUL 5.0.0 allocator that is NOT reproducible and cannot be: for
        ASan to say *use-after-free* the block must have reached `free()`, and a
        39-byte `zend_llist_element` never does -- `REAL_SIZE(39) >> 3 = 5 <
        MAX_CACHED_MEMORY`, on 32- and 64-bit builds alike. It is handed
        straight back out instead.

        So this row fires the sanitizer on exactly the windows where the freed
        block is handed back out INSIDE the same callback, and what ASan reports
        there is `SEGV on unknown address` and not `heap-use-after-free`. The
        `latent` windows -- the corpus's own trigger -- are SILENT under every
        detector and still return a different u64, which is why the oracle is in
        the checksum and not only in a sanitizer (§B1 rule 2).
        `controls/asan_fidelity.py` records both, and the plain-malloc build
        that DOES produce `heap-use-after-free` is what says the recorded
        category is real. NOTES.md §6."""
        return "fires" if self.any_wild else "clean"

    # -- what a conforming driver does -------------------------------------
    @property
    def expected_exit(self):
        # ph64's payload allocates nothing from an attacker-controlled size --
        # every allocation is inside the kernel and bounded by the window -- so
        # p02's exit 7 has no analogue here. `slb_load` rejecting a short file is
        # the only non-zero exit this pattern's driver produces.
        return 5 if self.truncated else 0

    @property
    def expected_stdout(self):
        return "" if self.checksum is None else f"{self.checksum}\n"

    def describe(self):
        states = {}
        for _, s, _ in self._win:
            states[s] = states.get(s, 0) + 1
        return (f"n_iters={self.n_iters} stride={self.stride} "
                f"n_blob={self.n_blob} nwin={self.nwin} calls={self.n_calls} "
                f"work/call={self.work_per_call}B san={self.sanitizer_expect} "
                f"r1={states} truncated={self.truncated} "
                f"expected={self.checksum}")

    # -- driving BOTH implementations off the corpus ------------------------
    @staticmethod
    def _both(win):
        """(simulated, llist_fold) for an arbitrary window, off-corpus.

        `Model.__new__` skips `__init__` deliberately: neither implementation
        reads anything but `buf` and `stride`, so this drives the SHIPPED code
        paths on bytes chosen here rather than on bytes `inputs/` happens to
        carry. That is the whole mechanism behind `selfcheck` check 1b."""
        m = Model.__new__(Model)
        m.buf, m.stride = win, len(win)
        return m._simulate(win, len(win), True)[0], m.llist_fold(win, 0, len(win))

    @staticmethod
    def _mkwin(n_slots, nent, trig, mode, post, fill=0x11):
        w = bytearray()
        for v in (nent, trig, mode, post):
            w += (v & 0xFFFFFFFF).to_bytes(4, "little")
        for i in range(n_slots):
            w += bytes(((i * 7 + 1) & 0xFF, fill, (i * 13) & 0xFF, 0x00))
        return bytes(w)

    @staticmethod
    def _synthetic_windows():
        """Windows spanning a domain `inputs/` cannot, built here, yielded as
        (label, bytes). ⚠ **`inputs/` is not the domain** -- see the docstring.

        Four families, each isolating one thing the two implementations could
        disagree about:

          a. every `mode` x every `trigger` in `0 ..= n`, at list lengths
             1, 2, 3, 5 and 8 -- which is the axis the corpus cannot span,
             because a window's stride is fixed and `n` is bounded by it;
          b. every `post` in `0 ..= n`, which is what reaches all FOUR
             `DEL_LLIST_ELEMENT` arms including `only` (`n == 1`), the arm a
             corpus of long lists never sees;
          c. the reuse flag, on and off, on every one of the above -- the flag
             that separates a latent read-after-free from a wild one;
          d. `n == nmax` and `n == 1`, the two ends of the head word's range."""
        for slots in (1, 2, 3, 5, 8):
            for mode in range(4):
                for reuse in (0, 1):
                    for trig in range(0, slots + 1):
                        for post in range(0, slots + 1):
                            for nent in (0, slots - 1):
                                yield (f"slots={slots} n={1 + nent % slots} "
                                       f"trig={trig} mode={mode} "
                                       f"reuse={reuse} post={post}",
                                       Model._mkwin(slots, nent, trig,
                                                    mode | (reuse << 16), post))

    def selfcheck(self):
        """Five checks, and four of them are about this row specifically.

        1a. the structural simulation against the closed form `llist_fold`, on
            the calls this input actually makes;
        1b. ⚠⚠ the same two implementations on **synthetic windows this file
            builds** -- every (list length x mode x trigger x post x reuse)
            combination up to eight entries. `PROTOCOL_PHP.md` §A2a rule 2: 1a
            alone is what let ph03 ship a model computing a different function
            from its own proof for a whole task;
        2.  ⚠⚠ every window of a NON-adversarial input leaves R1 and R1h
            AGREEING (`r1_state == "same"`). That is what "benign" means on this
            row and it is what `check.py` stage 7h requires -- and, positively,
            that the corpus DOES delete elements, because a corpus in which
            `DEL_LLIST_ELEMENT` never runs would measure the walk and never the
            mechanism;
        3.  ⚠ the FOUR `DEL_LLIST_ELEMENT` arms are all reached by the measured
            corpus (§A2a rule 1). `inputs/gen.py::_check_arms` asserts the same
            thing at generation time, from what it just emitted;
        4.  the walk's termination premise: every registered entry is visited at
            most once and `visits + skipped == n`. It is what ../verus.rs's
            `decreases` rests on, and a model that lost it would be simulating
            a diverged walk as if it were a converged one;
        5.  ⚠ the closed form's allocator arithmetic against the structural
            simulation's replayed counters, field by field -- so the two cannot
            agree on the u64 by cancelling two errors in the tally."""
        problems = []
        for c in self.sample_calls(8):
            want = self.llist_fold(c["buf"], c["off"], c["len"])
            if want != c["result"]:
                problems.append(
                    f"simulated result {c['result']} != llist_fold() {want} "
                    f"at off={c['off']}")
                break
        for label, win in self._synthetic_windows():
            sim, helper = self._both(win)
            if sim != helper:
                problems.append(
                    f"synthetic window [{label}]: simulated {sim} != "
                    f"llist_fold() {helper}. The two implementations have come "
                    f"apart OFF the corpus; inputs/ cannot see this and it is "
                    f"why this sweep exists (PROTOCOL_PHP.md A2a rule 2)")
                break
        adversarial = os.path.basename(self.path).startswith("adversarial")
        arms, dels = set(), 0
        for k in range(self.nwin):
            _, state, info = self._win[k]
            arms |= info["arms"]
            dels += len(info["arms"]) > 0
            if not adversarial and state != "same":
                problems.append(
                    f"window {k}: R1 is `{state}` on a NON-adversarial input. "
                    f"562f886ecb14's guard fires there, so R1 and R1h return "
                    f"different u64s and check.py stage 7h requires them to "
                    f"agree wherever the bug is not exercised. Move the window "
                    f"to an adversarial input; do not weaken the check")
                break
        if not adversarial and self.nwin and not dels:
            problems.append(
                f"no window of {self.nwin} ever reaches DEL_LLIST_ELEMENT. The "
                f"row would measure `zend_llist_apply` walking a list nothing "
                f"ever unlinks, which is the one shape in which the mechanism "
                f"cannot appear at all")
        if not adversarial and self.nwin and set(ARMS) - arms:
            problems.append(
                f"the corpus reaches DEL_LLIST_ELEMENT arms {sorted(arms)} and "
                f"misses {sorted(set(ARMS) - arms)}. PROTOCOL_PHP.md A2a rule 1: "
                f"the fixture must reach EVERY arm of the branch the defect "
                f"lives on, and the four arms are not interchangeable -- the "
                f"`tail` arm's `element->next` is NULL, so a recycled block "
                f"CREATES a successor where the loop would have ended")
        for k in range(self.nwin):
            _, _, info = self._win[k]
            s = self._sched(self.buf[k * self.stride:(k + 1) * self.stride],
                            self.stride)
            if info["visits"] + (1 if s["skipped"] else 0) != info["n"]:
                problems.append(
                    f"window {k}: visits={info['visits']} + skipped != "
                    f"n={info['n']}; the walk did not converge and "
                    f"../verus.rs's `decreases` is false")
                break
        for k in range(self.nwin):
            _, _, info = self._win[k]
            s = self._sched(self.buf[k * self.stride:(k + 1) * self.stride],
                            self.stride)
            n, dl = s["n"], ((1 if s["walk_del"] else 0)
                             + (1 if s["post_del"] else 0))
            reuse_alloc = 1 if (s["reuse"] and s["acts"]) else 0
            post_call = 1 if s["post"] else 0
            want = (2 * n + s["walk_call"] + reuse_alloc + post_call,
                    (2 if s["walk_del"] else 0) + s["walk_call"]
                    + (2 if s["post_del"] else 0) + post_call
                    + reuse_alloc + 2 * (n - dl),
                    s["reuse_hit"] + (1 if (post_call and s["walk_call"]) else 0))
            got = (info["n_alloc"], info["n_free"], info["n_hit"])
            if want != got:
                problems.append(
                    f"window {k}: the closed form counts (n_alloc, n_free, "
                    f"n_hit) = {want} and the replayed allocator got {got}. The "
                    f"two implementations agree on the fold and disagree on the "
                    f"tally, which is exactly the way a u64 can match by "
                    f"accident")
                break
        return problems


def build(path):
    return Model(path)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        m = build(p)
        print(f"{os.path.basename(p):32s} {m.describe()}  "
              f"exit={m.expected_exit} selfcheck={m.selfcheck()}")
