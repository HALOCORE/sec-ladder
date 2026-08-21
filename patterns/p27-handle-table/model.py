#!/usr/bin/env python3
"""p27-handle-table: the independent reference model the gate checks against.

The API is documented at the top of `patterns/p01-array-sum/model.py`; this file
notes only where p27 differs.

    bindings      buf/off/len/buf_len/result -- the READ-ONLY shape p03, p06,
                  p11, p12, p14, p16, p17, p05 and p07 use, and NOT p02's
                  before/after shape. p27's records are allocated **and freed**
                  inside the kernel, so no buffer crosses the signature and
                  there is nothing for an `after` binding to name. The security
                  property is carried by the liveness conjunct on the READ path,
                  which is what the `PointsTo` permission discharges in R5.
    work_per_call **bytes of the window** -- `stride`. See the property's
                  docstring for which way that errs.
    work_unit     "byte"; `work_unit_bits` 8.
    sanitizer     derived, not tabulated: an input "fires" exactly when the
                  simulated run performs a READ of a slot that is in range
                  (`h < ntab`) and **not alive**. R1 then loads through a
                  pointer whose record has been `free`d.

Two independent implementations, as every earlier pattern does:

  * the **simulation** keeps the table as a Python list of `Optional[int]` --
    `None` for a closed slot -- which is the safe rungs' `Option<Box<u8>>` and
    carries no separate liveness array at all;
  * the **helper** `op_fold` -- the one the derived `ensures` is evaluated
    against -- mirrors the Verus spec function `run` in ../verus.rs, carrying
    the two parallel sequences `vals` and `lv` exactly as the proof does.

    So the two implementations disagree about *where liveness is stored* -- in
    the value's own representation, or beside it -- and agree about the answer.
    That is not a decorative difference here: it is the pattern's whole subject,
    and R1's bug is precisely that C's second representation can fall out of
    step with the first.

    `op_fold` is **iterative where the Verus function is recursive**, for p11's
    and p14's reason: `run` recurses once per operation and a window may declare
    more operations than CPython's recursion limit allows.

`selfcheck()` runs them against each other.

**Both implementations model the CHECKED kernel**, i.e. R1h and R2-R5. R1 is the
rung with the bug and is expected to disagree on every input that reads a closed
handle; the gate records that disagreement in its behaviour table rather than
requiring it to vanish (`.memory/02-bench-rules.md`).

**Why the benign inputs never read a closed handle.** They cannot: the moment
one does, R1 leaves the defined path and the cell no longer agrees with any
other, and `harness/check.py` stage 2 requires every non-adversarial cell to
agree with this file *and with each other*. `inputs/gen.py` therefore emits op
streams whose every READ names a live slot, and checks that property by running
a copy of the model over every window of every blob it writes. The
use-after-free lives on the `adversarial-*` rows alone -- which is also what
TASK_055_REVIEW's blocker B1 requires, for a second and independent reason: at
`-O3` the stores into a recycled record can be dead-store-eliminated, so the two
optimisation levels do not agree about *what a stale read returns*.
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
RECSZ = 1                 # must equal every rung's RECSZ
SENT = 251                # must equal every rung's SENT


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
        self._win = []          # per window: (result, r1_would_read_a_freed_record)
        if not self.truncated:
            self._run()

    # -- the window table (computed once) ----------------------------------
    def _window(self, off):
        """(result, R1_would_read_a_freed_record) for the window at `off`.

        Implementation 1 of 2. The table is a list of `Optional[int]`: `None`
        *is* the closed state, exactly as the safe rungs' `Option<Box<u8>>`
        makes it, and there is no separate liveness array to fall out of step.

        The second element records whether the rung with **no** liveness
        conjunct on the READ path would dereference a freed record: that is a
        READ naming a slot with `h < ntab` whose entry is `None`."""
        ln = self.stride
        if ln < HDR:
            return 0, False
        buf = self.buf
        nops = int.from_bytes(buf[off:off + 4], "little")
        if nops == 0:
            return 0, False
        tab = []                     # one Optional[int] per slot ever opened
        acc, p, uaf = 0, HDR, False
        for _ in range(nops):
            if ln - p < OPSZ:
                break
            c = buf[off + p]
            a = buf[off + p + 1]
            p += OPSZ
            h = a
            op = c % 4
            if op == 0:
                if len(tab) < TABCAP:
                    tab.append(a)
                    acc = (acc * 31 + a) & MASK
                else:
                    acc = (acc * 31 + SENT) & MASK
            elif op == 1:
                if h < len(tab) and tab[h] is not None:
                    tab[h] = None
                    acc = (acc * 31 + 1) & MASK
                else:
                    acc = (acc * 31 + SENT) & MASK
            else:
                if h < len(tab) and tab[h] is not None:
                    acc = (acc * 31 + tab[h]) & MASK
                else:
                    if h < len(tab):
                        uaf = True   # what R1 would do, recorded
                    acc = (acc * 31 + SENT) & MASK
        return (acc * 31 + len(tab)) & MASK, uaf

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
    # (../verus.rs `run`) and, crucially, keeps liveness in a SEPARATE sequence
    # `lv` beside the values `vals`, which is the unsafe rungs' representation
    # rather than the safe rungs'.
    def _u32_at(self, buf, p):
        """`u32_at` in ../verus.rs, written out with `+` and `*` exactly as the
        rungs write it -- not `int.from_bytes`, which is the simulation's."""
        return (buf[p] + 256 * buf[p + 1] + 65536 * buf[p + 2]
                + 16777216 * buf[p + 3])

    def _run_spec(self, buf, off, ln, o, nops, p, vals, lv, acc):
        """`run` in ../verus.rs. Iterative rather than recursive -- see the
        module docstring."""
        while True:
            if o >= nops or ln - p < OPSZ:
                return (acc * 31 + len(vals)) & MASK
            c = buf[off + p]
            a = buf[off + p + 1]
            h = a
            if c % 4 == 0:
                if len(vals) < TABCAP:
                    vals = vals + [a]
                    lv = lv + [True]
                    acc = (acc * 31 + a) & MASK
                else:
                    acc = (acc * 31 + SENT) & MASK
            elif c % 4 == 1:
                if h < len(vals) and lv[h]:
                    lv = lv[:h] + [False] + lv[h + 1:]
                    acc = (acc * 31 + 1) & MASK
                else:
                    acc = (acc * 31 + SENT) & MASK
            else:
                if h < len(vals) and lv[h]:
                    acc = (acc * 31 + vals[h]) & MASK
                else:
                    acc = (acc * 31 + SENT) & MASK
            o += 1
            p += OPSZ

    def op_fold(self, buf, off, ln):
        """`op_fold` in ../verus.rs: what the kernel must return."""
        if ln < HDR:
            return 0
        nops = self._u32_at(buf, off)
        if nops == 0:
            return 0
        return self._run_spec(buf, off, ln, 0, nops, HDR, [], [], 0)

    @property
    def helpers(self):
        return {"op_fold": self.op_fold}

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
        """`stride` -- the bytes of the window, from the file alone.

        **Which way this estimate errs: STRICT** (`.memory/02-bench-rules.md`
        asks, so: say it). Two corrections, and the net is strict on every
        matrix input this pattern ships:

          * *over*-count: the 4 window-header bytes are decoded as a `u32` and
            are not operations;
          * *under*-count, and it dominates by an order of magnitude: **each 2
            window bytes is one OPERATION**, and an operation is a table index,
            a liveness test and -- for two of the four opcodes -- a `malloc` or
            a `free`, which are tens of instructions each in glibc. The measured
            figure is 100+ Ir per 2 bytes on every rung (../NOTES.md 3).

        So `stride` is far below the number of instructions the kernel must
        execute, the derived floor is one it clears by two orders of magnitude,
        and it can never let a collapsed kernel through -- which is the only
        direction that matters.

        No `min_ir_per_work` is declared, so the harness default of 0.25 Ir per
        byte applies unchanged. It is not a tight floor here and is not meant to
        be: p27's kernel calls the allocator, so a per-byte floor tuned to a
        fold would be meaningless. What it still catches is the failure it
        exists to catch -- a kernel the optimiser collapsed to nothing."""
        return self._work if self.entered else 0

    # -- sanitizer expectation ---------------------------------------------
    @property
    def sanitizer_expect(self):
        """Derived from the simulated run, never tabulated per file.

        R1 has no liveness conjunct on the READ path, so it is a memory error
        exactly when some visited window performs a READ whose slot number is in
        range and whose record has been freed. Note what this does NOT include:
        a READ of a slot that was never opened (`h >= ntab`) is rejected by R1
        too -- R1 keeps that bound -- and folds SENT in every rung.

          `adversarial-uaf`      open, close, open (the tcache hands the same
                                 chunk back), then read the CLOSED handle: R1
                                 discloses the NEWER record's byte under the
                                 older record's handle.
          `adversarial-noreuse`  open, close, read -- with no intervening open,
                                 so the chunk is still in the tcache and R1
                                 reads glibc's own safe-linked `next` word.
                                 The row that shows the harm is not always a
                                 disclosure.
          `adversarial-many`     the stale read repeats 24 times in one window,
                                 so a rung that survives one has to survive 24.

        ../NOTES.md 7 records what each does at the gate's flags."""
        return "fires" if self.any_uaf else "clean"

    # -- what a conforming driver does -------------------------------------
    @property
    def expected_exit(self):
        # p27's payload allocates nothing from an attacker-controlled size --
        # there is no `cap` word and no `slb_zeroed` -- so p02's exit 7 has no
        # analogue here. The records the kernel allocates are RECSZ bytes each,
        # a compile-time constant, and at most TABCAP of them are alive at once.
        # `slb_load` rejecting a short file is the only non-zero exit this
        # driver produces.
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
        """`Optional[int]` table vs the (vals, lv) pair that mirrors Verus."""
        problems = []
        for c in self.sample_calls(8):
            want = self.op_fold(c["buf"], c["off"], c["len"])
            if want != c["result"]:
                problems.append(
                    f"simulated result {c['result']} != op_fold() {want} "
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
