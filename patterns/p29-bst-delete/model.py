#!/usr/bin/env python3
"""p29-bst-delete: the independent reference model the gate checks against.

The API is documented at the top of `patterns/p01-array-sum/model.py`; this file
notes only where p29 differs.

    bindings      buf/off/len/buf_len/result -- the READ-ONLY shape p03, p06,
                  p11, p12, p14, p16, p17, p05, p07 and p27 use, and NOT p02's
                  before/after shape. p29's records are allocated **and freed**
                  inside the kernel, so no buffer crosses the signature and
                  there is nothing for an `after` binding to name.
    work_per_call **bytes of the window** -- `stride`, p27's denomination. See
                  the property's docstring for which way that errs.
    work_unit     "byte"; `work_unit_bits` 8.
    sanitizer     derived, not tabulated: an input "fires" exactly when the
                  simulated run performs a USE whose cached record has been
                  FREED. R1 then loads through a dangling pointer. A USE whose
                  cached record was OVERWRITTEN IN PLACE by the two-child splice
                  is a wrong answer and **not** a memory error, so it does not
                  set this flag -- which is the pattern's whole subject.

TWO INDEPENDENT IMPLEMENTATIONS, AND THEY ARE OF DIFFERENT SHAPES ON PURPOSE.
`TASK_137` item 5 found the previous draft's REMOVE to be a line-by-line
transliteration of its own `kernel.c` -- same variable names, same loop guard,
same cursor move -- which satisfies check.py's model-sandbox rule mechanically
and defeats it in substance, because a model that mirrors the implementation
agrees with it by construction. So:

  * the **simulation** (`_window`) is a PURELY FUNCTIONAL BST. Records are
    objects with identity; the tree SHAPE is a separate immutable triple
    `(rec, left, right)`, so the shape is *not* stored inside the record the way
    every rung stores it. INSERT, FIND and REMOVE are RECURSIVE -- no cursor, no
    parent variable, no `goleft` flag, no step counter, no loop guard -- and
    REMOVE is the textbook three-case delete with a separate `_del_min` helper,
    not a cursor that re-enters one loop. **The USE test is a REACHABILITY WALK
    over the tree**, which is the contract's own words -- *the record is still
    in the tree* -- and this implementation has no liveness array at all;
  * the **helper** `bst_fold` -- the one the derived `ensures` is evaluated
    against -- mirrors the Verus spec function `run` in ../verus.rs, carrying
    the five parallel slot sequences `ky`, `vl`, `lt`, `rt`, `lv` exactly as the
    proof does, with the same walk fuel the exec rungs carry.

    So the two implementations disagree about *where the tree is* and about
    *how liveness is decided* -- by walking the tree, or by reading a bit beside
    it -- and agree about the answer. That is not a decorative difference here:
    R1's bug is precisely that C's third representation, a raw pointer, can fall
    out of step with both.

    `bst_fold` is **iterative where the Verus function is recursive**, for p11's,
    p14's and p27's reason: `run` recurses once per operation and a window may
    declare more operations than CPython's recursion limit allows. The
    functional simulation recurses only over the TREE, whose depth is at most
    TABCAP = 32.

`selfcheck()` runs them against each other.

**Both implementations model the CHECKED kernel**, i.e. R1h and R2-R5. R1 is the
rung with the bug and is expected to disagree on every input whose USE names a
record that has been freed *or* overwritten; the gate records that disagreement
in its behaviour table rather than requiring it to vanish
(`.memory/02-bench-rules.md`).

**Why the benign inputs never USE a stale record.** They cannot: the moment one
does, R1 leaves the defined path (or returns a different number) and the cell no
longer agrees with any other, and `harness/check.py` stage 2 requires every
non-adversarial cell to agree with this file *and with each other*.
`inputs/gen.py` therefore emits op streams in which every USE names a record
that is still in the tree under the key it was found by, and checks that
property by running a copy of the model over every window of every blob it
writes. The two bug classes live on the `adversarial-*` rows alone.
"""

import itertools
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "common"))
import slb  # noqa: E402

MASK = (1 << 64) - 1
HDR = 4                   # nops:u32
OPSZ = 2                  # opcode byte + operand byte
TABCAP = 32               # must equal every rung's TABCAP
RECSZ = 4                 # must equal every rung's RECSZ
NIL = 255                 # must equal every rung's NIL
SENT = 251                # must equal every rung's SENT


def _val_of(k):
    """A record's value is a function of its key, in every rung: `a * 7 + 1`
    truncated to a byte. So a USE that returns the wrong record's value returns
    a value no honest read of THIS key could produce."""
    return (k * 7 + 1) & 0xFF


# --------------------------------------------------------------------------
# Implementation 1 of 2 -- the functional tree. See the module docstring.
# --------------------------------------------------------------------------
class Rec:
    """One ALLOCATION. Identity is what this pattern is about: the two-child
    splice keeps the object and changes its contents."""
    __slots__ = ("key", "val")

    def __init__(self, k, v):
        self.key, self.val = k, v


def _ins(t, k, st):
    """Textbook recursive insert. `st[0]` is the allocation budget (the rungs'
    `ntab`, which only ever grows) and `st[1]` reports what happened."""
    if t is None:
        if st[0] < TABCAP:
            st[0] += 1
            st[1] = "new"
            return (Rec(k, _val_of(k)), None, None)
        st[1] = "full"
        return None
    rec, l, r = t
    if k < rec.key:
        return (rec, _ins(l, k, st), r)
    if k > rec.key:
        return (rec, l, _ins(r, k, st))
    rec.val = _val_of(k)
    st[1] = "dup"
    return t


def _find(t, k):
    if t is None:
        return None
    rec, l, r = t
    if k < rec.key:
        return _find(l, k)
    if k > rec.key:
        return _find(r, k)
    return rec


def _min_rec(t):
    rec, l, _r = t
    return rec if l is None else _min_rec(l)


def _del_min(t):
    """Drop the leftmost node. Its record is DESTROYED -- that is the `free`."""
    rec, l, r = t
    if l is None:
        return r
    return (rec, _del_min(l), r)


def _rem(t, k, st):
    """Textbook three-case delete.

    0 or 1 child : the node leaves the tree and its record is destroyed.
    2 children   : the in-order successor's payload is copied INTO the victim's
                   record -- the victim's allocation survives with a different
                   occupant -- and the SUCCESSOR's record is destroyed."""
    if t is None:
        return None
    rec, l, r = t
    if k < rec.key:
        return (rec, _rem(l, k, st), r)
    if k > rec.key:
        return (rec, l, _rem(r, k, st))
    st[2] = True
    if l is None:
        return r
    if r is None:
        return l
    s = _min_rec(r)
    rec.key, rec.val = s.key, s.val
    return (rec, l, _del_min(r))


def _reach(t, rec):
    """Is this RECORD still a node of the tree? The contract's own test, and the
    reason this implementation needs no liveness array."""
    if t is None:
        return False
    n, l, r = t
    return n is rec or _reach(l, rec) or _reach(r, rec)


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
        self.any_uaf = False
        self.nwin = 0
        self._work = 0
        self._win = []          # per window: (result, r1_reads_a_freed_record)
        if not self.truncated:
            self._run()

    # -- the window table (computed once) ----------------------------------
    def _window(self, off):
        """(result, R1_reads_a_freed_record) for the window at `off`.

        Implementation 1 of 2 -- the functional tree; see the module docstring.

        The second element records whether the rung with **no** safety line
        would dereference a freed record: a USE whose cached record is no longer
        reachable from the root. A USE whose cached record is still reachable
        but no longer holds the key it was found under is the OTHER bug class --
        a wrong answer inside a live allocation -- and is deliberately not
        counted here."""
        ln = self.stride
        if ln < HDR:
            return 0, False
        buf = self.buf
        nops = int.from_bytes(buf[off:off + 4], "little")
        if nops == 0:
            return 0, False
        root = None
        st = [0, "", False]          # [ntab, insert status, remove found]
        saved, skey = None, 0
        acc, p, uaf = 0, HDR, False
        for _ in range(nops):
            if ln - p < OPSZ:
                break
            c = buf[off + p]
            a = buf[off + p + 1]
            p += OPSZ
            op = c % 4
            if op == 0:
                st[1] = ""
                root = _ins(root, a, st)
                acc = (acc * 31 + (SENT if st[1] == "full" else a)) & MASK
            elif op == 1:
                got = _find(root, a)
                if got is not None:
                    saved, skey = got, a
                    acc = (acc * 31 + 1) & MASK
                else:
                    acc = (acc * 31 + SENT) & MASK
            elif op == 2:
                st[2] = False
                root = _rem(root, a, st)
                acc = (acc * 31 + (2 if st[2] else SENT)) & MASK
            else:
                here = saved is not None and _reach(root, saved)
                if saved is not None and not here:
                    uaf = True      # what R1 would do, recorded
                if here and saved.key == skey:
                    acc = (acc * 31 + saved.val) & MASK
                else:
                    acc = (acc * 31 + SENT) & MASK
        return (acc * 31 + st[0]) & MASK, uaf

    # -- simulation --------------------------------------------------------
    def _run(self):
        acc = 0
        if HDR <= self.stride <= self.n_blob:
            self.entered = True
            self.nwin = self.n_blob // self.stride
            self._win = [None] * self.nwin
            self._work = self.stride
            for _ in range(self.n_iters):
                k = (acc * self.nwin) >> 64
                if self._win[k] is None:
                    self._win[k] = self._window(k * self.stride)
                r, uaf = self._win[k]
                if uaf:
                    self.any_uaf = True
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
            if self._win[k] is None:
                self._win[k] = self._window(k * self.stride)
            r, _uaf = self._win[k]
            yield {"buf": self.buf, "off": k * self.stride, "len": self.stride,
                   "buf_len": self.n_blob, "result": r}
            acc = (acc * 31 + r) & MASK

    def sample_calls(self, k):
        if not self.entered or k <= 0:
            return []
        step = max(1, self.n_calls // k)
        return list(itertools.islice(
            (c for i, c in enumerate(self.iter_calls()) if i % step == 0), k))

    # -- the second, independent implementation ----------------------------
    # This is what the derived `ensures` is evaluated against, so it must not be
    # the simulation in disguise. It mirrors the *Verus* spec function
    # (../verus.rs `run`) and keeps the tree in five parallel slot sequences
    # with liveness beside the payload, which is the unsafe rungs'
    # representation rather than the safe rungs'.
    def _u32_at(self, buf, p):
        """`u32_at` in ../verus.rs, written out with `+` and `*` exactly as the
        rungs write it -- not `int.from_bytes`, which is the simulation's."""
        return (buf[p] + 256 * buf[p + 1] + 65536 * buf[p + 2]
                + 16777216 * buf[p + 3])

    def _run_spec(self, buf, off, ln):
        """`run` in ../verus.rs. Iterative rather than recursive -- see the
        module docstring."""
        nops = self._u32_at(buf, off)
        if nops == 0:
            return 0
        ky = [0] * TABCAP
        vl = [0] * TABCAP
        lt = [NIL] * TABCAP
        rt = [NIL] * TABCAP
        lv = [0] * TABCAP
        ntab, root = 0, NIL
        has, gslot, gkey = False, 0, 0
        acc, p, o = 0, HDR, 0
        while o < nops:
            if ln - p < OPSZ:
                break
            c = buf[off + p]
            a = buf[off + p + 1]
            p += OPSZ
            o += 1
            m = c % 4
            if m == 0:
                cur, par, goleft, dup, steps = root, NIL, False, False, 0
                while cur != NIL and lv[cur] == 1 and steps < TABCAP:
                    steps += 1
                    if a < ky[cur]:
                        par, goleft, cur = cur, True, lt[cur]
                    elif a > ky[cur]:
                        par, goleft, cur = cur, False, rt[cur]
                    else:
                        vl[cur] = _val_of(a)
                        dup = True
                        break
                if dup:
                    acc = (acc * 31 + a) & MASK
                elif ntab < TABCAP:
                    ky[ntab], vl[ntab] = a, _val_of(a)
                    lt[ntab], rt[ntab] = NIL, NIL
                    lv[ntab] = 1
                    if par == NIL:
                        root = ntab
                    elif goleft:
                        lt[par] = ntab
                    else:
                        rt[par] = ntab
                    ntab += 1
                    acc = (acc * 31 + a) & MASK
                else:
                    acc = (acc * 31 + SENT) & MASK
            elif m == 1:
                cur, steps, found = root, 0, False
                while cur != NIL and lv[cur] == 1 and steps < TABCAP:
                    steps += 1
                    if a < ky[cur]:
                        cur = lt[cur]
                    elif a > ky[cur]:
                        cur = rt[cur]
                    else:
                        found = True
                        break
                if found:
                    has, gslot, gkey = True, cur, a
                    acc = (acc * 31 + 1) & MASK
                else:
                    acc = (acc * 31 + SENT) & MASK
            elif m == 2:
                cur, par, goleft, steps, found = root, NIL, False, 0, False
                while cur != NIL and lv[cur] == 1 and steps < TABCAP:
                    steps += 1
                    if a < ky[cur]:
                        par, goleft, cur = cur, True, lt[cur]
                    elif a > ky[cur]:
                        par, goleft, cur = cur, False, rt[cur]
                    else:
                        found = True
                        break
                if found:
                    guard = 0
                    while guard < TABCAP:
                        guard += 1
                        if (lt[cur] != NIL and lv[lt[cur]] == 1
                                and rt[cur] != NIL and lv[rt[cur]] == 1):
                            sp, s, sgoleft, sst = cur, rt[cur], False, 0
                            while lt[s] != NIL and lv[lt[s]] == 1 and sst < TABCAP:
                                sst += 1
                                sp, s, sgoleft = s, lt[s], True
                            ky[cur], vl[cur] = ky[s], vl[s]
                            cur, par, goleft = s, sp, sgoleft
                            continue
                        ch = lt[cur] if lt[cur] != NIL else rt[cur]
                        if par == NIL:
                            root = ch
                        elif goleft:
                            lt[par] = ch
                        else:
                            rt[par] = ch
                        lv[cur] = 0
                        break
                    acc = (acc * 31 + 2) & MASK
                else:
                    acc = (acc * 31 + SENT) & MASK
            else:
                if has and lv[gslot] == 1 and ky[gslot] == gkey:
                    acc = (acc * 31 + vl[gslot]) & MASK
                else:
                    acc = (acc * 31 + SENT) & MASK
        return (acc * 31 + ntab) & MASK

    def bst_fold(self, buf, off, ln):
        """`bst_fold` in ../verus.rs: what the kernel must return."""
        if ln < HDR:
            return 0
        return self._run_spec(buf, off, ln)

    @property
    def helpers(self):
        return {"bst_fold": self.bst_fold}

    # -- what the kernel must do, per call ---------------------------------
    @property
    def work_unit(self):
        return "byte"

    @property
    def work_unit_bits(self):
        """One unit is one window byte. 8 bits."""
        return 8

    @property
    def work_per_call(self):
        """`stride` -- the bytes of the window, from the file alone, which is
        p27's denomination and p16's, p05's, p11's, p12's, p06's and p14's.

        **Which way this estimate errs: STRICT** (`.memory/02-bench-rules.md`
        asks, so: say it). Two corrections, and the net is strict on every
        matrix input this pattern ships:

          * *over*-count: the 4 window-header bytes are decoded as a `u32` and
            are not operations;
          * *under*-count, and it dominates by more than an order of magnitude:
            **each 2 window bytes is one OPERATION**, and an operation here is a
            TREE WALK -- up to TABCAP steps, each a table index, a liveness test
            and a record load -- plus, for two of the four opcodes, a `malloc`
            or a `free`, which are tens of instructions each in glibc.

        So `stride` is far below the number of instructions the kernel must
        execute, the derived floor is one it clears by orders of magnitude, and
        it can never let a collapsed kernel through -- the only direction that
        matters.

        No `min_ir_per_work` is declared, so the harness default of 0.25 Ir per
        byte applies unchanged. It is not a tight floor here and is not meant to
        be: a kernel that walks a tree and calls the allocator cannot be
        denominated like a fold. What it still catches is the failure it exists
        to catch -- a kernel the optimiser collapsed to nothing."""
        return self._work if self.entered else 0

    # -- sanitizer expectation ---------------------------------------------
    @property
    def sanitizer_expect(self):
        """Derived from the simulated run, never tabulated per file.

        R1 has no safety line on the USE path, so it is a MEMORY error exactly
        when some visited window performs a USE whose cached record has been
        freed -- i.e. is no longer reachable from the root. Note the two things
        this does NOT include, and the second is the pattern's subject:

          * a USE with no successful FIND behind it folds SENT in every rung
            (R1 keeps the `g_saved != NULL` test);
          * **a USE whose cached record was overwritten in place by the
            two-child splice is NOT a memory error at all.** The record is
            live, the read is in bounds, ASan is silent, and R1 simply returns
            the successor's value. That input is `adversarial-recycle.bin` and
            its `sanitizer_expect` is `clean` while its checksum row diverges.

          `adversarial-uaf`      FIND a leaf, REMOVE it, USE: the record is
                                 freed and R1 reads it.
          `adversarial-succ`     FIND the in-order SUCCESSOR of a two-child key,
                                 then REMOVE that key: the successor is the
                                 record the splice frees.
          `adversarial-recycle`  FIND a two-child key, REMOVE it, USE: nothing
                                 is freed, ASan is silent, R1 is wrong.
          `adversarial-many`     both classes, repeatedly, in one window.

        ../NOTES.md 7 records what each does at the gate's flags."""
        return "fires" if self.any_uaf else "clean"

    # -- what a conforming driver does -------------------------------------
    @property
    def expected_exit(self):
        # p29's payload allocates nothing from an attacker-controlled size --
        # there is no `cap` word and no `slb_zeroed` -- so p02's exit 7 has no
        # analogue here, exactly as for p27. `slb_load` rejecting a short file
        # is the only non-zero exit this driver produces.
        #
        # This is the CHECKED rungs' exit. R1's exit on the adversarial rows is
        # recorded in the adversarial table rather than required.
        return 5 if self.truncated else 0

    @property
    def expected_stdout(self):
        return "" if self.checksum is None else f"{self.checksum}\n"

    def describe(self):
        return (f"n_iters={self.n_iters} stride={self.stride} "
                f"n_blob={self.n_blob} nwin={self.nwin} calls={self.n_calls} "
                f"work/call={self.work_per_call}B "
                f"san={self.sanitizer_expect} "
                f"truncated={self.truncated} expected={self.checksum}")

    def selfcheck(self):
        """The functional tree vs the five slot sequences that mirror Verus."""
        problems = []
        for c in self.sample_calls(8):
            want = self.bst_fold(c["buf"], c["off"], c["len"])
            if want != c["result"]:
                problems.append(
                    f"simulated result {c['result']} != bst_fold() {want} "
                    f"at off={c['off']}")
                break
        return problems


def build(path):
    return Model(path)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        m = build(p)
        print(f"{os.path.basename(p):28s} {m.describe()}  "
              f"exit={m.expected_exit} selfcheck={m.selfcheck()}")
