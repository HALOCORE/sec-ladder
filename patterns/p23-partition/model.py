#!/usr/bin/env python3
"""p23-partition: the independent reference model the gate checks against.

The API is documented at the top of `patterns/p01-array-sum/model.py`; this file
notes only where p23 differs.

    bindings      buf/off/len/buf_len/result -- the READ-ONLY shape p03, p06,
                  p11, p12, p16, p17, p05 and p07 use, and NOT p02's
                  before/after shape. p23's destination is a **local**
                  `scr[SCR]` inside the kernel, so no buffer crosses the
                  signature and there is nothing for a `scr_after` binding to
                  name. The security property is carried by the trusted read and
                  write accessors' `i < v@.len()`, discharged at every scan step
                  and at both stores of the exchange.
    work_per_call **bytes of the window** -- `stride`. See the property's
                  docstring for which way that errs.
    work_unit     "byte"; `work_unit_bits` 8.
    sanitizer     derived, not tabulated: an input "fires" exactly when the
                  simulated run contains a call in which R1 -- the rung with no
                  `i < j` conjunct on either scan -- would have to read
                  `scr[SCR]` or `scr[-1]`. Both directions are simulated
                  separately, because they are different bug classes: the first
                  is a forward overrun of a stack array and the second wraps
                  `size_t` and walks AWAY from the frame.

Two independent implementations, as every earlier pattern does:

  * the **simulation** partitions with the NESTED-SCAN loop nest -- an outer
    loop, an upward scan, a downward scan, an exchange -- which is what the
    seven rungs execute;
  * the **helper** `partition_fold` -- the one the derived `ensures` is
    evaluated against -- mirrors the Verus spec functions `part` / `swap2` /
    `fold_scr` / `walk` in ../verus.rs, and `part` there is the SINGLE-LOOP
    three-way step: advance `i`, or retreat `j`, or exchange, one at a time,
    with no nesting at all. So the two implementations disagree about the
    *algorithm* and agree about the answer, which is the only kind of agreement
    worth having. (That is also this pattern's answer to TASK_086's named kill
    risk -- both spellings exist, both verify, and one of them is the spec.)

    Both are **iterative where the Verus functions are recursive**, for p11's
    reason: `walk` recurses once per record and a window may declare more
    records than CPython's recursion limit allows.

`selfcheck()` runs them against each other.

**Both implementations model the CHECKED kernel**, i.e. R1h and R2-R5. R1 is the
rung with the bug and is expected to disagree on every input where some record's
scratch has no element strictly above the pivot at or after the upward cursor,
or none strictly below it before the downward one; the gate records that
disagreement in its behaviour table rather than requiring it to vanish
(`.memory/02-bench-rules.md`).

**Why `degenerate.bin` is not named `adversarial-*`.** Its four records are
`m == 0`, `nelem > SCR`, the two-element minimum and one ordinary record, and R1
agrees with the model on every one of them -- `m == 0` because the outer
`while (i < j)` never runs, and the other three because each carries a byte
strictly below its pivot and one strictly above. `inputs/gen.py` checks that
agreement by simulating R1, rather than asserting it. So it is a full-agreement
row and the gate holds all eight cells to the model on it, which is strictly
stronger than filing it as adversarial.

**And `m == 1` is NOT in that file**, because it cannot be made to agree: one
byte cannot be both strictly above and strictly below the pivot, so R1 leaves
the scratch on every one-element record whatever its contents. It ships as
`adversarial-single`, and it is the sharpest row here -- nothing about the input
is malformed.
"""

import itertools
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "common"))
import slb  # noqa: E402

MASK = (1 << 64) - 1
HDR = 4                   # nrec:u32
REC_HDR = 8               # nelem:u32 ; pivot:u8 ; pad:u8[3]
SCR = 64                  # must equal every rung's SCR


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
        self.any_overrun = False
        self.nwin = 0
        self._work = 0
        self._win = []          # per window: (result, r1_would_leave_scr)
        if not self.truncated:
            self._run()

    # -- the window table (computed once) ----------------------------------
    @staticmethod
    def _r1_would_leave(scr, m, pv):
        """Would R1 -- no `i < j` on either scan -- read outside `scr[0, SCR)`?

        Implemented by running R1's loop nest with the two reads BOUNDED and
        reporting the first step at which the unbounded rung would have gone
        past. The upward scan needs `scr[SCR]` exactly when every byte from the
        cursor to the end of the SCRATCH (not the live prefix -- R1 walks
        through the previous record's bytes first) is `<= pv`; the downward
        scan needs `scr[-1]` exactly when every byte below its cursor is
        `>= pv`, and that read wraps `size_t`.

        `scr` is copied, so the caller's scratch is untouched."""
        s = bytearray(scr)
        i, j = 0, m
        while i < j:
            while i < SCR and s[i] <= pv:
                i += 1
            if i == SCR:
                return True                     # would read scr[SCR]
            while j > 0 and s[j - 1] >= pv:
                j -= 1
            if j == 0:
                return True                     # would read scr[-1], j wraps
            if i < j:
                s[i], s[j - 1] = s[j - 1], s[i]
                i += 1
                j -= 1
        return False

    def _window(self, off):
        """(result, R1_would_leave_the_scratch) for the window at `off`.

        Implementation 1 of 2. Partitions with the NESTED-SCAN loop nest, which
        is a different code path from the single-step `_part` below in every
        respect that matters."""
        ln = self.stride
        if ln < HDR:
            return 0, False
        buf = self.buf
        nrec = int.from_bytes(buf[off:off + 4], "little")
        if nrec == 0:
            return 0, False
        scr, acc, p, over = bytearray(SCR), 0, HDR, False
        for _ in range(nrec):
            if ln - p < REC_HDR:
                break
            nelem = int.from_bytes(buf[off + p:off + p + 4], "little")
            pv = buf[off + p + 4]
            p += REC_HDR
            m = min(nelem, SCR)
            if ln - p < nelem:
                break
            scr[:m] = buf[off + p:off + p + m]
            p += nelem
            if self._r1_would_leave(scr, m, pv):    # what R1 would do, recorded
                over = True
            i, j = 0, m
            while i < j:
                while i < j and scr[i] <= pv:
                    i += 1
                while i < j and scr[j - 1] >= pv:
                    j -= 1
                if i < j:
                    scr[i], scr[j - 1] = scr[j - 1], scr[i]
                    i += 1
                    j -= 1
            for q in range(m):
                acc = (acc * 31 + scr[q]) & MASK
            acc = (acc * 31 + i) & MASK
        return (acc * 31 + nrec) & MASK, over

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
                r, over = self._win[k]
                if over:
                    self.any_overrun = True
                acc = (acc * 31 + r) & MASK
            self.n_calls = self.n_iters
        self.checksum = acc

    def iter_calls(self):
        """Replay the driver loop, yielding one binding per kernel call.

        Regenerated rather than stored. `buf` is the whole blob and is yielded
        by reference, so this costs nothing per call beyond the dict."""
        if not self.entered:
            return
        acc = 0
        for _ in range(self.n_iters):
            k = (acc * self.nwin) >> 64
            if self._win[k] is None:
                self._win[k] = self._window(k * self.stride)
            r, _over = self._win[k]
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
    # the simulation in disguise. It mirrors the *Verus* spec functions
    # (../verus.rs `part` / `swap2` / `fold_scr` / `walk`) and, crucially,
    # partitions with the SINGLE-STEP three-way rule rather than with two nested
    # scans.
    def _u32_at(self, buf, p):
        """`u32_at` in ../verus.rs, written out with `+` and `*` exactly as the
        rungs write it -- not `int.from_bytes`, which is the simulation's."""
        return (buf[p] + 256 * buf[p + 1] + 65536 * buf[p + 2]
                + 16777216 * buf[p + 3])

    def _part(self, scr, pv, i, j):
        """`part` in ../verus.rs: Hoare's scheme as ONE three-way step, applied
        until the cursors meet. Returns `(sequence, meeting point)`.

            i >= j        -> stop
            s[i]   <= pv  -> i += 1
            s[j-1] >= pv  -> j -= 1
            otherwise     -> exchange, i += 1, j -= 1

        Iterative here, recursive there -- see the module docstring."""
        s = bytearray(scr)
        while i < j:
            if s[i] <= pv:
                i += 1
            elif s[j - 1] >= pv:
                j -= 1
            else:
                s[i], s[j - 1] = s[j - 1], s[i]
                i += 1
                j -= 1
        return s, i

    def _fold_scr(self, scr, i, m, acc):
        """`fold_scr` in ../verus.rs: the Horner fold over `scr[i .. m)`."""
        while i < m:
            acc = (acc * 31 + scr[i]) & MASK
            i += 1
        return acc

    def _walk(self, buf, off, ln, rec, nrec, p, scr, acc):
        """`walk` in ../verus.rs. Iterative rather than recursive -- see the
        module docstring."""
        while rec < nrec:
            if ln - p < REC_HDR:
                break
            nelem = self._u32_at(buf, off + p)
            pv = buf[off + p + 4]
            p += REC_HDR
            m = min(nelem, SCR)
            if ln - p < nelem:
                break
            scr = bytearray(scr)
            for i in range(m):
                scr[i] = buf[off + p + i]
            p += nelem
            scr, idx = self._part(scr, pv, 0, m)
            acc = self._fold_scr(scr, 0, m, acc)
            acc = (acc * 31 + idx) & MASK
            rec += 1
        return (acc * 31 + nrec) & MASK

    def partition_fold(self, buf, off, ln):
        """`partition_fold` in ../verus.rs: what the kernel must return."""
        if ln < HDR:
            return 0
        nrec = self._u32_at(buf, off)
        if nrec == 0:
            return 0
        return self._walk(buf, off, ln, 0, nrec, HDR, bytearray(SCR), 0)

    @property
    def helpers(self):
        return {"partition_fold": self.partition_fold}

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
        asks, so: say it). Three corrections, and the net is strict on every
        matrix input this pattern ships:

          * *over*-count: the 4 header bytes and the 8 bytes of each record
            header are decoded and are neither copied, partitioned nor folded;
          * *over*-count on a record with `nelem > SCR`: the undeclared tail is
            skipped by the cursor and never read. `degenerate` is the only
            matrix input with such a record;
          * *under*-count, and it dominates: every copied byte is **copied,
            visited by at least one scan and folded**, i.e. touched at least
            three times. A partition's scans together visit each live byte
            exactly once (the two cursors meet), so the visit count is `m` per
            record and not `2m`; p06's rotate visits about twice that. The
            floor is therefore TIGHTER here than on p06, which is the safe
            direction.

        On `small` the visits are 157 copied + 157 scanned + 157 folded = 471
        against a declared stride of 201, and on `large` 54 + 54 + 54 = 162
        against 154. So `stride` is at or below the number of byte-visits on
        both and the derived floor is one the kernel must clear. (`large`'s
        margin is thin *by design*: its records are 2..8 bytes, so the
        per-record header is 8 of every ~12.8 window bytes and the window is
        mostly header. That makes the floor tighter there than on any earlier
        pattern, which is the safe direction.)

        No `min_ir_per_work` is declared, so the harness default of 0.25 Ir per
        byte applies unchanged. The argument is p12's and p06's: the fold is a
        **serial Horner chain**, `acc = acc*31 + b`, so byte `q+1`'s multiply
        depends on byte `q`'s and there is no vector form at any `-march`; and
        the two scans are data-dependent while loops, which no compiler
        vectorises. The *copy* alone can go far below 0.25 -- it is a `memcpy`
        in every rung -- which is exactly why the unit is denominated over the
        whole window and not over the copy."""
        return self._work if self.entered else 0

    # -- sanitizer expectation ---------------------------------------------
    @property
    def sanitizer_expect(self):
        """Derived from the simulated run, never tabulated per file.

        R1 has no `i < j` conjunct on either scan, so it is a memory error
        exactly when some visited window holds a record on which one of the two
        scans has no sentinel inside the scratch:

          `adversarial-allbelow`   `pv = 255`. No `uint8_t` is above 255, so
                                   the UPWARD scan consumes the live prefix,
                                   consumes the stale tail, and then reads
                                   `scr[64]`. Forward overrun of a stack array.
          `adversarial-allabove`   `pv = 0`. No `uint8_t` is below 0, so the
                                   DOWNWARD scan reaches `j == 0` and reads
                                   `scr[-1]`; `j - 1` wraps `size_t`, so the
                                   scan then walks away from the frame and the
                                   exchange that follows writes there.
          `adversarial-both`       one record of each, in one window.

        ../NOTES.md 7 records what each does at the gate's flags."""
        return "fires" if self.any_overrun else "clean"

    # -- what a conforming driver does -------------------------------------
    @property
    def expected_exit(self):
        # p23's payload allocates nothing from an attacker-controlled size --
        # there is no `cap` word and no `slb_zeroed` -- so p02's exit 7 has no
        # analogue here, exactly as for p03, p06, p11, p12, p16, p17, p05 and
        # p07. The scratch is a fixed-size local in every rung. `slb_load`
        # rejecting a short file is the only non-zero exit this driver produces.
        #
        # This is the CHECKED rungs' exit. R1's exit on the adversarial rows is
        # a function of what the scan finds outside the frame and of the
        # compiler; `check.py` records it in the adversarial table rather than
        # requiring it.
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
        """nested-scan simulation vs the single-step rule that mirrors the Verus
        spec functions."""
        problems = []
        for c in self.sample_calls(8):
            want = self.partition_fold(c["buf"], c["off"], c["len"])
            if want != c["result"]:
                problems.append(
                    f"simulated result {c['result']} != partition_fold() {want} "
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
