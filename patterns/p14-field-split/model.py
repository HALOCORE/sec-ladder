#!/usr/bin/env python3
"""p14-field-split: the independent reference model the gate checks against.

The API is documented at the top of `patterns/p01-array-sum/model.py`; this file
notes only where p14 differs.

    bindings      buf/off/len/buf_len/result -- the READ-ONLY shape p03, p06,
                  p11, p12, p16, p17, p05 and p07 use, and NOT p02's
                  before/after shape. p14's destinations are two **locals**
                  inside the kernel, `scr[SCR]` and `tl[MAXTOK]`, so no buffer
                  crosses the signature and there is nothing for an `after`
                  binding to name. The security property is carried by the
                  trusted write accessor's `i < old(v)@.len()`, discharged at
                  the one store in the scan loop.
    work_per_call **bytes of the window** -- `stride`. See the property's
                  docstring for which way that errs.
    work_unit     "byte"; `work_unit_bits` 8.
    sanitizer     derived, not tabulated: an input "fires" exactly when the
                  simulated run visits a window holding a line whose UNCAPPED
                  field count exceeds MAXTOK -- i.e. a line with at least
                  MAXTOK delimiters inside its first SCR bytes. R1 then stores
                  `tl[MAXTOK]` and beyond.

Two independent implementations, as every earlier pattern does:

  * the **simulation** splits with Python's own `bytes.split(b",")` and takes
    the first MAXTOK fields -- a library partition, no cursor, no index;
  * the **helper** `split_fold` -- the one the derived `ensures` is evaluated
    against -- mirrors the Verus spec functions `toks` / `fold_bytes` /
    `fold_toks` / `walk` in ../verus.rs, walking a cursor and building the field
    table one descriptor at a time.

    So the two implementations disagree about *how the partition is found* and
    agree about the answer, which is the only kind of agreement worth having.

    It is **iterative where the Verus functions are recursive**, for p11's
    reason: `walk` recurses once per line and a window may declare more lines
    than CPython's recursion limit allows.

`selfcheck()` runs them against each other.

**Both implementations model the CHECKED kernel**, i.e. R1h and R2-R5. R1 is the
rung with the bug and is expected to disagree on every input where some line has
at least MAXTOK delimiters; the gate records that disagreement in its behaviour
table rather than requiring it to vanish (`.memory/02-bench-rules.md`).

**Why `degenerate.bin` is not named `adversarial-*`.** Its lines are `m == 0`,
`m == 1` with no delimiter, a leading delimiter, a trailing delimiter, a line
with exactly MAXTOK-1 delimiters (the boundary from the safe side) and a line
with `llen > SCR`. R1 agrees with the model on every one of them, so it is a
full-agreement row and the gate holds all eight cells to the model on it, which
is strictly stronger than filing it as adversarial.
"""

import itertools
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "common"))
import slb  # noqa: E402

MASK = (1 << 64) - 1
HDR = 4                   # nline:u32
LINE_HDR = 4              # llen:u32
SCR = 64                  # must equal every rung's SCR
MAXTOK = 16               # must equal every rung's MAXTOK
DELIM = 0x2C              # ','  -- must equal every rung's DELIM


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
        self._win = []          # per window: (result, r1_would_overflow_tl)
        if not self.truncated:
            self._run()

    # -- the window table (computed once) ----------------------------------
    def _window(self, off):
        """(result, R1_would_store_past_tl[MAXTOK]) for the window at `off`.

        Implementation 1 of 2. Partitions with `bytes.split(b",")` -- the
        library's own splitter -- and truncates to MAXTOK fields, which is a
        different code path from `split_fold`'s cursor walk in every respect
        that matters.

        The second element records whether the rung with **no** field-count
        bound would store `tl[MAXTOK]` or beyond. The uncapped field count of a
        line is `(number of DELIM bytes in scr[0:m]) + 1`, so the predicate is
        `ndelim >= MAXTOK` -- and **not** `> MAXTOK`: at exactly MAXTOK
        delimiters the uncapped rung records MAXTOK+1 descriptors, one past the
        end."""
        ln = self.stride
        if ln < HDR:
            return 0, False
        buf = self.buf
        nline = int.from_bytes(buf[off:off + 4], "little")
        if nline == 0:
            return 0, False
        acc, p, over = 0, HDR, False
        for _ in range(nline):
            if ln - p < LINE_HDR:
                break
            llen = int.from_bytes(buf[off + p:off + p + 4], "little")
            p += LINE_HDR
            m = min(llen, SCR)
            if ln - p < llen:
                break
            scr = bytes(buf[off + p:off + p + m])
            p += llen
            if scr.count(DELIM) >= MAXTOK:       # what R1 would do, recorded
                over = True
            fields = scr.split(bytes([DELIM]))[:MAXTOK]
            for fld in fields:
                acc = (acc * 31 + len(fld)) & MASK
                for b in fld:
                    acc = (acc * 31 + b) & MASK
            acc = (acc * 31 + len(fields)) & MASK
        return (acc * 31 + nline) & MASK, over

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
    # (../verus.rs `toks` / `fold_bytes` / `fold_toks` / `walk`) and, crucially,
    # finds the partition with a CURSOR rather than with a library splitter.
    def _u32_at(self, buf, p):
        """`u32_at` in ../verus.rs, written out with `+` and `*` exactly as the
        rungs write it -- not `int.from_bytes`, which is the simulation's."""
        return (buf[p] + 256 * buf[p + 1] + 65536 * buf[p + 2]
                + 16777216 * buf[p + 3])

    def _toks(self, scr, m):
        """`toks` in ../verus.rs: the UNCAPPED sequence of field lengths, found
        by walking a cursor and treating `i == m` as a virtual delimiter."""
        out, s, i = [], 0, 0
        while i <= m:
            if i == m or scr[i] == DELIM:
                out.append(i - s)
                s = i + 1
            i += 1
        return out

    def _fold_bytes(self, scr, q, end, acc):
        """`fold_bytes` in ../verus.rs."""
        while q < end:
            acc = (acc * 31 + scr[q]) & MASK
            q += 1
        return acc

    def _fold_toks(self, scr, tk, j, nt, cur, acc):
        """`fold_toks` in ../verus.rs: length, then content, per field, in
        order, with the cursor stepping over the delimiter."""
        while j < nt:
            acc = (acc * 31 + tk[j]) & MASK
            acc = self._fold_bytes(scr, cur, cur + tk[j], acc)
            cur = cur + tk[j] + 1
            j += 1
        return acc

    def _walk(self, buf, off, ln, line, nline, p, acc):
        """`walk` in ../verus.rs. Iterative rather than recursive -- see the
        module docstring."""
        while line < nline:
            if ln - p < LINE_HDR:
                break
            llen = self._u32_at(buf, off + p)
            p += LINE_HDR
            m = min(llen, SCR)
            if ln - p < llen:
                break
            scr = [buf[off + p + i] for i in range(m)]
            p += llen
            tk = self._toks(scr, m)
            nt = min(len(tk), MAXTOK)
            acc = self._fold_toks(scr, tk, 0, nt, 0, acc)
            acc = (acc * 31 + nt) & MASK
            line += 1
        return (acc * 31 + nline) & MASK

    def split_fold(self, buf, off, ln):
        """`split_fold` in ../verus.rs: what the kernel must return."""
        if ln < HDR:
            return 0
        nline = self._u32_at(buf, off)
        if nline == 0:
            return 0
        return self._walk(buf, off, ln, 0, nline, HDR, 0)

    @property
    def helpers(self):
        return {"split_fold": self.split_fold}

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

          * *over*-count: the 4 window-header bytes and the 4 bytes of each line
            header are decoded as `u32`s and are neither copied, scanned nor
            folded;
          * *over*-count on a line with `llen > SCR`: the undeclared tail is
            skipped by the cursor and never read, and on a line with more than
            MAXTOK fields the checked rungs fold only the first MAXTOK.
            `degenerate` is the only matrix input with such a line;
          * *under*-count, and it dominates on every perf input: every copied
            byte is **copied, scanned and folded**, i.e. visited three times,
            and the scan runs `m + 1` times per line rather than `m`.

        So `stride` is at or below the number of byte-visits on `small` and
        `large`, the derived floor is one the kernel must clear, and it can
        never let a collapsed kernel through -- which is the only direction that
        matters. The exact per-input arithmetic is in ../NOTES.md 3.

        No `min_ir_per_work` is declared, so the harness default of 0.25 Ir per
        byte applies unchanged. The argument is p12's and p06's: the fold is a
        **serial Horner chain**, `acc = acc*31 + b`, so byte `i+1`'s multiply
        depends on byte `i`'s and there is no vector form at any `-march`, and
        the scan is a scalar byte loop with two exit tests in every rung and
        every compiler (measured on the disassembly, ../NOTES.md 1). The *copy*
        alone can go far below 0.25 -- it is a `memcpy` in every rung -- which is
        exactly why the unit is denominated over the whole window and not over
        the copy."""
        return self._work if self.entered else 0

    # -- sanitizer expectation ---------------------------------------------
    @property
    def sanitizer_expect(self):
        """Derived from the simulated run, never tabulated per file.

        R1 does not bound the field count, so it is a memory error exactly when
        some visited window holds a line with **at least MAXTOK delimiters** in
        its first `SCR` bytes: the uncapped rung then stores `tl[MAXTOK]`, one
        `size_t` past a 16-entry table. Note what this does NOT include: a line
        with MAXTOK-1 delimiters produces exactly MAXTOK fields and is the
        boundary from the safe side, on which R1 and R1h agree exactly.

          `adversarial-run17`    one line, 16 adjacent delimiters: 17 fields
                                 under this partition and **2** under
                                 `strtok`'s, which collapses runs. The
                                 library-contract row.
          `adversarial-alt33`    one line, 32 alternating delimiters: 33 fields
                                 under BOTH partitions -- collapse does not
                                 save it.
          `adversarial-full65`   one line, 64 delimiters: 65 fields, 49
                                 descriptors and 392 bytes past the table.
          `adversarial-many`     eight lines each with 20 delimiters: the store
                                 repeats, so a rung that survives one line has
                                 to survive eight.

        ../NOTES.md 7 records what each does at the gate's flags."""
        return "fires" if self.any_overrun else "clean"

    # -- what a conforming driver does -------------------------------------
    @property
    def expected_exit(self):
        # p14's payload allocates nothing from an attacker-controlled size --
        # there is no `cap` word and no `slb_zeroed` -- so p02's exit 7 has no
        # analogue here, exactly as for p03, p06, p11, p12, p16, p17, p05 and
        # p07. Both the scratch and the field table are fixed-size locals in
        # every rung. `slb_load` rejecting a short file is the only non-zero
        # exit this driver produces.
        #
        # This is the CHECKED rungs' exit. R1's exit on the adversarial rows is
        # a function of the overflow magnitude and of the compiler; `check.py`
        # records it in the adversarial table rather than requiring it.
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
        """library partition vs the cursor walk that mirrors the Verus spec."""
        problems = []
        for c in self.sample_calls(8):
            want = self.split_fold(c["buf"], c["off"], c["len"])
            if want != c["result"]:
                problems.append(
                    f"simulated result {c['result']} != split_fold() {want} "
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
