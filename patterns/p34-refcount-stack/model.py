#!/usr/bin/env python3
"""p34-refcount-stack: the independent reference model the gate checks against.

The API is documented at the top of `patterns/p01-array-sum/model.py`; this file
notes only where p34 differs.

    bindings      buf/off/len/buf_len/result -- the READ-ONLY shape p03, p06,
                  p11, p12, p14, p16, p17, p05, p07, p27, p29, p32 and p35 use,
                  and NOT p02's before/after shape. p34's stack is a LOCAL of the
                  kernel and every object it allocates is released before the
                  call returns, so no buffer crosses the signature and there is
                  nothing for an `after` binding to name.
    work_per_call **bytes of the window** -- `stride`, p27's, p29's and p32's
                  denomination. See the property's docstring for which way it
                  errs.
    sanitizer     **DERIVED, by SIMULATING THE BUGGY RUNG, and the derivation is
                  one that CAN FIRE.** ⚠⚠ `TASK_154` deliverable 2 predicted the
                  opposite -- *"Python has no dangling pointers, so p34's harm is
                  very likely UNREPRESENTABLE in the model by construction"* --
                  and asked for the answer to be decided first and written down.
                  **THE ANSWER IS THAT IT IS REPRESENTABLE, and `sanitizer_expect`
                  is derived rather than declared.** What ASan reports on this
                  pattern is not a dangling *pointer*, it is *a touch of an
                  object whose storage has been returned to the allocator*, and
                  that is a property of the OBJECT, which Python models exactly:
                  `Obj.freed` is set by `Pool.release` when the count reaches
                  zero, and every field access the buggy rung performs goes
                  through `Pool.touch`, which raises `_Escape` the moment it
                  reaches a freed object. ⚠ **Being representable is not the same
                  as being live**, which is `.memory/03-measurement.md` entry 19's
                  point, so `detector_selftest()` is the must-fire arm and
                  `selfcheck()` runs it on every gate invocation.

    ⚠⚠ `selfcheck()` ALSO enforces `p34`'s structural constraint mechanically:
    **no NON-adversarial input may contain an executed `DUP` op.** That is the
    corollary of the row's headline -- the safety line cannot execute on an input
    R1 and R1h agree about (../c/kernel.h's two-line proof) -- and it is checked
    on the SHIPPED blob rather than assumed. `inputs/gen.py` refuses to write one
    and `controls/no_dup.py` censuses every blob in the directory.

TWO INDEPENDENT IMPLEMENTATIONS, AND THEY ARE OF DIFFERENT SHAPES ON PURPOSE.
`TASK_136`'s model was a line-by-line transliteration of its own kernel -- same
variable names, same guard -- which satisfies check.py's model-sandbox rule
mechanically and defeats it in substance, and is how its delete bug went
undetected. p34's two implementations disagree about what a reference IS:

  * the **simulation** (`_sim_window`) is OBJECT-BASED. An object is a Python
    object with identity, its own `rc` and its own `freed` flag; the stack holds
    direct references to those objects; `free` is `Obj.freed = True` and the
    storage is a `bytearray` that is NEVER cleared, because that is what a freed
    heap block is. It is the only one of the two that can represent the bug, and
    the only one the detector watches.
  * the **helper** `rc_fold` -- the one the derived `ensures` is evaluated
    against -- mirrors the Verus spec function `run` in ../verus.rs and **HAS NO
    REFERENCE COUNT ANYWHERE**. It carries a stack of integer object IDs and a
    sequence of payload bytes indexed by ID, exactly as `run` does, because in
    the CHECKED semantics the answer does not depend on the counts at all: an
    object is alive exactly while some stack entry names it, and its payload
    never changes. ⚠ **That is a real independence and not a cosmetic one** --
    R1's bug is precisely that a third representation, the count stored in the
    object's own first word, can fall out of step with the stack the other two
    agree about.

    `rc_fold` is **iterative where the Verus function is recursive**, for p11's,
    p14's, p27's, p29's and p32's reason: `run` recurses once per operation and a
    window may declare more operations than CPython's recursion limit allows.

`selfcheck()` runs them against each other, runs the must-fire arm, and runs the
no-DUP census on the input it was handed.

**Both implementations model the CHECKED kernel**, i.e. R1h and R2-R5. R1 is the
rung with the bug and is expected to touch freed storage on every input whose
window executes a `DUP`; the gate records that behaviour in its adversarial table
rather than requiring it to vanish (`.memory/02-bench-rules.md`).
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
CAP = 16                  # must equal every rung's CAP
DLEN = 8                  # must equal every rung's DLEN
SENT = 251                # must equal every rung's SENT

NEW, DUP, POP, READ = 0, 1, 2, 3


def _val_of(a):
    """An object's payload byte is a function of the operand that created it, in
    every rung: `a * 7 + 1` truncated to a byte. So a READ that returns a
    recycled block's payload returns a value no honest read of the reference's
    own object could produce."""
    return (a * 7 + 1) & 0xFF


# --------------------------------------------------------------------------
# Implementation 1 of 2 -- objects with identity. See the module docstring.
# --------------------------------------------------------------------------
class Obj:
    """ONE HEAP OBJECT. Identity is what this pattern is about: a stack entry is
    a direct reference to one of these, and `freed` records whether its storage
    has been handed back to the allocator. **The storage (`mem`) is deliberately
    NOT cleared on a free** -- a freed block still holds its bytes, which is
    exactly why R1's stale READ returns the right answer until something
    recycles the block."""

    __slots__ = ("rc", "mem", "freed", "oid")

    def __init__(self, oid, payload):
        self.oid = oid
        self.rc = 1
        self.mem = bytearray(DLEN)
        self.mem[0] = payload
        self.freed = False


class _Escape(Exception):
    """Raised the instant the simulated BUGGY rung touches a freed object.

    ⚠ **It exists so the detector can REPORT rather than CRASH**, which is
    `TASK_154` deliverable 2's requirement and `TASK_145_REPORT` §4b's finding on
    p32: a must-fire arm whose failure mode is an exception loses the
    diagnostic. The buggy run's RESULT is discarded (`Model._window` keeps only
    its `uaf` flag), so abandoning the window at the first touch of freed storage
    costs nothing and is what a detector, rather than an interpreter, does."""


class Pool:
    """The heap, as this pattern uses it: a set of objects, each of which the
    allocator either owns or has handed back.

    ⚠ `recycle` is what makes this a simulation of glibc rather than of an
    abstract heap. `free` pushes the block onto a LIFO list and the next
    allocation POPS it, which is the tcache's discipline -- and it is the whole
    of the difference between p34's checksum-blind shapes and its divergent one.
    `../controls/storage_arms.py` measures that the real allocator agrees."""

    def __init__(self):
        self.objs = []        # every object ever created, in creation order
        self.tcache = []      # freed blocks, LIFO, as glibc's tcache is
        self.uaf = False      # did the BUGGY rung touch freed storage?
        self.uaf_sites = []

    def new(self, payload):
        if self.tcache:
            # RECYCLE: the freed block comes back and the new occupant writes
            # its own payload over the old one. Stale references now see it.
            o = self.tcache.pop()
            o.freed = False
            o.rc = 1
            o.mem[0] = payload
            o.oid = len(self.objs)
            self.objs.append(o)
            return o
        o = Obj(len(self.objs), payload)
        self.objs.append(o)
        return o

    def free(self, o):
        o.freed = True
        self.tcache.append(o)

    # -- the use-after-free detector ---------------------------------------
    def touch(self, site, o):
        """Record whether ONE field access the BUGGY rung performs reaches an
        object whose storage has been freed.

        ⚠ **This is a check about the OBJECT the rung reaches, not about the
        simulation's own bookkeeping** -- `.memory/03-measurement.md` entry 19's
        rule. The caller hands over the object a stack entry names; nothing here
        consults the reference count, and the guard is false for every object the
        CHECKED semantics can reach. Raises `_Escape` so the caller stops rather
        than continuing to interpret a program the allocator no longer owns."""
        if not o.freed:
            return
        self.uaf = True
        self.uaf_sites.append(f"{site} on object {o.oid}, freed")
        raise _Escape(self.uaf_sites[-1])

    def release(self, o):
        """The release path, spelled as both C rungs spell it: read `rc`,
        decrement, free at zero. **The read and the write are BOTH accesses to
        the object**, which is why a release through a stale reference is the
        first of p34's two harms."""
        self.touch("o->rc (release)", o)
        o.rc = (o.rc - 1) & MASK
        if o.rc == 0:
            self.free(o)

    def retain(self, o):
        """THE SAFETY LINE, and the only increment anywhere in this pattern."""
        self.touch("t->rc (retain)", o)
        o.rc = (o.rc + 1) & MASK

    def read(self, o):
        self.touch("o->data[0] (read)", o)
        return o.mem[0]


def _sim_window(buf, off, ln, harden):
    """`(result, touched_freed_storage)` for one window, simulated with objects.

    `harden` selects the CHECKED semantics (R1h and R2-R5) or the BUGGY one
    (R1): it is exactly whether `DUP` retains. That single boolean IS the safety
    line, and it is the knob `detector_selftest()` turns."""
    if ln < HDR:
        return 0, False
    nops = int.from_bytes(buf[off:off + 4], "little")
    if nops == 0:
        return 0, False
    pool = Pool()
    stk = []
    acc, p = 0, HDR
    try:
        for _ in range(nops):
            if ln - p < OPSZ:
                break
            c = buf[off + p]
            a = buf[off + p + 1]
            p += OPSZ
            op = c % 4
            if op == NEW:
                if len(stk) < CAP:
                    stk.append(pool.new(_val_of(a)))
                    v = a
                else:
                    v = SENT
            elif op == DUP:
                if 0 < len(stk) < CAP:
                    t = stk[-1]
                    if harden:
                        pool.retain(t)
                    stk.append(t)
                    v = 1
                else:
                    v = SENT
            elif op == POP:
                if stk:
                    pool.release(stk.pop())
                    v = 2
                else:
                    v = SENT
            else:
                v = pool.read(stk[a % len(stk)]) if stk else SENT
            acc = (acc * 31 + v) & MASK
        while stk:
            pool.release(stk.pop())
    except _Escape:
        # The buggy rung has touched storage the allocator owns; its answer past
        # this point is not a thing this simulation can compute, and nobody reads
        # it (`Model._window` keeps only the flag).
        return (acc * 31 + len(pool.objs)) & MASK, True
    return (acc * 31 + len(pool.objs)) & MASK, pool.uaf


def window_ops(buf, off, ln):
    """The op codes the window at `off` actually EXECUTES, in order.

    Used by `no_dup_problems` below, by `inputs/gen.py` and by
    `controls/no_dup.py`. It walks the same cursor the rungs walk, so an op the
    `nops` counter declares but the window cannot hold is not counted."""
    if ln < HDR:
        return []
    nops = int.from_bytes(buf[off:off + 4], "little")
    out, p = [], HDR
    for _ in range(nops):
        if ln - p < OPSZ:
            break
        out.append(buf[off + p] % 4)
        p += OPSZ
    return out


# --------------------------------------------------------------------------
# THE MUST-FIRE ARM. `selfcheck()` runs it, so the gate re-derives it once per
# input on every run -- not once, by whoever wrote it.
# --------------------------------------------------------------------------
# Three windows, written out as bytes so they depend on nothing in `inputs/`.
# None is ever fed to a rung. Op encoding: c % 4 = 0 NEW, 1 DUP, 2 POP, 3 READ.
_PROBE_NODUP = bytes([4, 0, 0, 0, 0, 5, 0, 9, 2, 0, 2, 0])          # NEW NEW POP POP
_PROBE_RELEASE = bytes([4, 0, 0, 0, 0, 5, 1, 0, 2, 0, 2, 0])        # NEW DUP POP POP
_PROBE_READ = bytes([4, 0, 0, 0, 0, 5, 1, 0, 2, 0, 3, 0])           # NEW DUP POP READ


def detector_selftest():
    """Show that `Pool.touch` CAN FIRE, and that THE SAFETY LINE is what stops it.

    Six cells, and the pairing is the point -- the same window under both
    semantics:

      * `_PROBE_NODUP`  hardened -> silent   buggy -> silent   (no DUP, no harm)
      * `_PROBE_RELEASE` hardened -> silent  buggy -> **fires**, `o->rc (release)`
      * `_PROBE_READ`    hardened -> silent  buggy -> **fires**, `o->data[0] (read)`

    The two firing arms are p34's two bug classes, and they are the two the
    shipped adversarial inputs carry. ⚠ The `_PROBE_NODUP` pair is the control
    that stops a detector which fires on everything from passing this test."""
    problems = []
    arms = ((("no-DUP"), _PROBE_NODUP, False, None),
            (("DUP POP POP"), _PROBE_RELEASE, True, "o->rc (release)"),
            (("DUP POP READ"), _PROBE_READ, True, "o->data[0] (read)"))
    for shape, blob, want_fire, site in arms:
        _, quiet = _sim_window(blob, 0, len(blob), True)
        if quiet:
            problems.append(
                f"the use-after-free detector FIRED on the `{shape}` probe under "
                f"the HARDENED semantics, which no shipped rung can do -- the "
                f"probe or `Pool.touch` is wrong")
        _, loud = _sim_window(blob, 0, len(blob), False)
        if loud != want_fire:
            if want_fire:
                problems.append(
                    f"MUST-FIRE ARM DEAD: the `{shape}` probe did NOT make the "
                    f"use-after-free detector fire under the BUGGY semantics "
                    f"(expected {site}). `sanitizer_expect` is then a "
                    f"declaration wearing a derivation's clothes -- do not "
                    f"quote this pattern's `fires` as DERIVED until it fires "
                    f"again")
            else:
                problems.append(
                    f"the detector fired on the `{shape}` probe under the BUGGY "
                    f"semantics, and that probe contains no DUP -- the detector "
                    f"is firing on something other than the missing retain")
    return problems


def no_dup_problems(path, buf, stride, n_blob):
    """**No NON-adversarial input may contain an executed `DUP` op.**

    ⚠⚠ This is `p34`'s headline stated as a mechanical check on the shipped blob
    rather than as an argument about the generator. ../c/kernel.h proves that a
    DUP in R1 always ends in a use-after-free, so a window containing one cannot
    be a row where R1 and R1h agree -- and `harness/check.py` stage 2 requires
    every non-adversarial cell to agree with this file and with every other cell.
    The benign cost gradient across the safety line is `0.00` because of this
    property, so the property is what has to be checked."""
    if os.path.basename(path).startswith("adversarial-"):
        return []
    if not (HDR <= stride <= n_blob):
        return []
    out = []
    for w in range(n_blob // stride):
        ops = window_ops(buf, w * stride, stride)
        if DUP in ops:
            out.append(f"window {w} executes a DUP op, so R1 would free an "
                       f"object a live stack entry still names -- that belongs "
                       f"on an `adversarial-*` row and nowhere else")
            break
    return out


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
        self._win = []
        if not self.truncated:
            self._run()

    # -- the window table (computed once) ----------------------------------
    def _window(self, off):
        """(result, R1_touches_freed_storage) for the window at `off`.

        Implementation 1 of 2 -- objects with identity; see the module
        docstring. The second element is computed under the BUGGY semantics,
        because the question it answers is what the rung with no safety line
        would do."""
        r_ok, _ = _sim_window(self.buf, off, self.stride, True)
        _, uaf = _sim_window(self.buf, off, self.stride, False)
        return r_ok, uaf

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
    # (../verus.rs `run`) and carries **no reference count at all** -- a stack of
    # integer object IDs and a payload sequence indexed by ID.
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
        stk = []          # object IDs, one per live reference
        vals = []         # payload byte per object ID
        acc, p, o = 0, HDR, 0
        while o < nops:
            if ln - p < OPSZ:
                break
            c = buf[off + p]
            a = buf[off + p + 1]
            p += OPSZ
            o += 1
            m = c % 4
            if m == NEW:
                if len(stk) < CAP:
                    stk.append(len(vals))
                    vals.append(_val_of(a))
                    acc = (acc * 31 + a) & MASK
                else:
                    acc = (acc * 31 + SENT) & MASK
            elif m == DUP:
                if 0 < len(stk) < CAP:
                    stk.append(stk[-1])
                    acc = (acc * 31 + 1) & MASK
                else:
                    acc = (acc * 31 + SENT) & MASK
            elif m == POP:
                if stk:
                    stk.pop()
                    acc = (acc * 31 + 2) & MASK
                else:
                    acc = (acc * 31 + SENT) & MASK
            else:
                if stk:
                    acc = (acc * 31 + vals[stk[a % len(stk)]]) & MASK
                else:
                    acc = (acc * 31 + SENT) & MASK
        return (acc * 31 + len(vals)) & MASK

    def rc_fold(self, buf, off, ln):
        """`rc_fold` in ../verus.rs: what the kernel must return."""
        if ln < HDR:
            return 0
        return self._run_spec(buf, off, ln)

    @property
    def helpers(self):
        return {"rc_fold": self.rc_fold}

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
        p27's, p29's and p32's denomination and p16's, p05's, p11's, p12's,
        p06's and p14's.

        **Which way this estimate errs: STRICT** (`.memory/02-bench-rules.md`
        asks, so: say it). Two corrections, and the net is strict on every matrix
        input this pattern ships:

          * *over*-count: the 4 window-header bytes are decoded as a `u32` and
            are not operations;
          * *under*-count: **each 2 window bytes is one OPERATION**, and every
            operation does a modulo, a compare chain and a multiply-add, while a
            `NEW` also calls `malloc`, zeroes `DLEN` bytes and writes two words,
            and a `POP` reads, decrements and stores a word and may call `free`.

        p34's under-count is the largest in the temporal family, because an
        allocator call is not O(1) in instructions and the matrix inputs are
        NEW/POP-heavy by construction. No `min_ir_per_work` is declared, so the
        harness default of 0.25 Ir per byte applies unchanged, and what it
        catches is the failure it exists to catch -- a kernel the optimiser
        collapsed to nothing."""
        return self._work if self.entered else 0

    # -- sanitizer expectation ---------------------------------------------
    @property
    def sanitizer_expect(self):
        """**DERIVED by simulating the buggy rung, and the derivation FIRES.**

        `fires` on exactly the inputs whose windows execute a `DUP`, `clean`
        everywhere else -- and `inputs/gen.py` puts a `DUP` on the
        `adversarial-*` rows and nowhere else, which `no_dup_problems` re-checks
        on the shipped blob at every gate invocation.

        ⚠⚠ **WHAT MAKES THAT A MEASUREMENT AND NOT A RESTATEMENT.** The
        simulation runs each window under the semantics with the safety line
        DELETED, and every field access it performs goes through `Pool.touch`,
        which fires the instant it reaches an object the simulated allocator has
        taken back. Turning the safety line back on silences it, on the same
        window: `detector_selftest()` runs both halves of that pair on both bug
        classes plus a no-DUP control, and `selfcheck()` runs it once per input
        on every gate invocation.

        ⚠ **What it does NOT derive, said so nobody reads it as more.** It
        derives that the buggy rung TOUCHES FREED STORAGE, which is what ASan
        reports. It says nothing about UBSan, and it should not: p34's undefined
        behaviour is purely temporal -- every index the kernel forms is inside
        `stk[]` in both rungs -- so **UBSan is silent on every input at both
        optimisation levels on both compilers**, and that silence needs its own
        positive control rather than this one (../controls/detectors.py, RECAP
        trap 5). Miri's answer is derived one level up and needs no simulation:
        p34 allocates, so Miri has something to see, and ../spec.md's
        `miri.reason` states what it finds on the SHIPPED unsafe rung."""
        return "fires" if self.any_uaf else "clean"

    # -- what a conforming driver does -------------------------------------
    @property
    def expected_exit(self):
        # p34's payload allocates nothing from an attacker-controlled size --
        # there is no `cap` word and no `slb_zeroed` -- so p02's exit 7 has no
        # analogue here, exactly as for p27, p29 and p32. `slb_load` rejecting a
        # short file is the only non-zero exit this driver produces.
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
        """The object simulation vs the count-free ID stack that mirrors Verus,
        plus the must-fire arm that proves the detector is alive, plus the
        no-DUP census on this input."""
        problems = list(detector_selftest())
        problems += no_dup_problems(self.path, self.buf, self.stride,
                                    self.n_blob)
        for c in self.sample_calls(8):
            want = self.rc_fold(c["buf"], c["off"], c["len"])
            if want != c["result"]:
                problems.append(
                    f"simulated result {c['result']} != rc_fold() {want} "
                    f"at off={c['off']}")
                break
        return problems


def build(path):
    return Model(path)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        m = build(p)
        print(f"{os.path.basename(p):32s} {m.describe()}  "
              f"exit={m.expected_exit} selfcheck={m.selfcheck()}")
