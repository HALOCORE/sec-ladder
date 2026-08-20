#!/usr/bin/env python3
"""p06-rotate: the independent reference model the gate checks against.

The API is documented at the top of `patterns/p01-array-sum/model.py`; this file
notes only where p06 differs.

    bindings      buf/off/len/buf_len/result -- the READ-ONLY shape p03, p11,
                  p12, p16, p17, p05 and p07 use, and NOT p02's before/after
                  shape. p06's destination is a **local** `scr[SCR]` inside the
                  kernel, so no buffer crosses the signature and there is nothing
                  for a `scr_after` binding to name. That is p03's and p12's
                  shape. The security property is carried by the trusted write
                  accessor's `i < old(v)@.len()`, discharged at every store in
                  the three reverse loops.
    work_per_call **bytes of the window** -- `stride`. See the property's
                  docstring for which way that errs.
    work_unit     "byte"; `work_unit_bits` 8.
    sanitizer     derived, not tabulated: an input "fires" exactly when the
                  simulated run contains a call in which R1 -- the rung with no
                  reduction of the rotate amount -- would touch `scr[SCR]` or
                  beyond. That is `r > SCR`, and **not** `r >= SCR`: the first
                  reverse's highest index is `r - 1`.

Two independent implementations, as every earlier pattern does:

  * the **simulation** rotates with Python slice reversal (`s[::-1]`) on a
    `bytearray`, three slice assignments per record;
  * the **helper** `rotate_fold` -- the one the derived `ensures` is evaluated
    against -- mirrors the Verus spec functions `rev_range` / `rot_left` /
    `fold_scr` / `walk` in ../verus.rs. It does **not** reverse anything: it
    computes the rotation in CLOSED FORM, `scr[i] = old[i + r]` or
    `old[i + r - m]`, which is the postcondition `lemma_three_reverses`
    establishes for the triple. So the two implementations disagree about the
    *algorithm* and agree about the answer, which is the only kind of agreement
    worth having.

    It is **iterative where the Verus functions are recursive**, for p11's
    reason: `walk` recurses once per record and a window may declare more
    records than CPython's recursion limit allows.

`selfcheck()` runs them against each other.

**Both implementations model the CHECKED kernel**, i.e. R1h and R2-R5. R1 is the
rung with the bug and is expected to disagree on every input where some record
has `r >= m` and `m > 1`; the gate records that disagreement in its behaviour
table rather than requiring it to vanish (`.memory/02-bench-rules.md`).

**Why `degenerate.bin` is not named `adversarial-*`.** Its four records are
`m == 0`, `r == 0`, `r == m` and `nelem > SCR`, and R1 agrees with the model on
every one of them -- on `r == m` by composition (the unreduced triple is
`reverse(0,m) ; no-op ; reverse(0,m)` = the identity) rather than by luck. So it
is a full-agreement row and the gate holds all eight cells to the model on it,
which is strictly stronger than filing it as adversarial.
"""

import itertools
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "common"))
import slb  # noqa: E402

MASK = (1 << 64) - 1
HDR = 4                   # nrec:u32
REC_HDR = 8               # nelem:u32 ; r:u32
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
    def _window(self, off):
        """(result, R1_would_touch_scr[SCR]_or_beyond) for the window at `off`.

        Implementation 1 of 2. Rotates by literally performing the three
        reverses with Python slice reversal, which is a different code path from
        the closed-form `rotate_fold` below in every respect that matters.

        The second element records whether the rung with **no** reduction would
        touch `scr[SCR]` or past it. `reverse(scr, 0, r)` swaps `scr[i]` with
        `scr[r-1-i]`, so its highest index is `r - 1` and the predicate is
        `r > SCR`. At `r == SCR` exactly the rung is still inside the array and
        the harm is a wrong answer, not a memory-safety event -- which is the
        distinction p06 exists to draw and is one step from where its task file
        put the boundary."""
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
            r = int.from_bytes(buf[off + p + 4:off + p + 8], "little")
            p += REC_HDR
            m = min(nelem, SCR)
            if ln - p < nelem:
                break
            scr[:m] = buf[off + p:off + p + m]
            p += nelem
            if r > SCR:                          # what R1 would do, recorded
                over = True
            r = r % m if m else 0
            scr[:r] = scr[:r][::-1]              # reverse [0, r)
            scr[r:m] = scr[r:m][::-1]            # reverse [r, m)
            scr[:m] = scr[:m][::-1]              # reverse [0, m)
            for i in range(m):
                acc = (acc * 31 + scr[i]) & MASK
            acc = (acc * 31 + m) & MASK
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
    # (../verus.rs `rot_left` / `fold_scr` / `walk`) and, crucially, computes
    # the rotation in CLOSED FORM rather than by reversing anything.
    def _u32_at(self, buf, p):
        """`u32_at` in ../verus.rs, written out with `+` and `*` exactly as the
        rungs write it -- not `int.from_bytes`, which is the simulation's."""
        return (buf[p] + 256 * buf[p + 1] + 65536 * buf[p + 2]
                + 16777216 * buf[p + 3])

    def _rot_left(self, scr, m, r):
        """`rot_left` in ../verus.rs: the closed form of the rotation, with no
        modulo and no reversal --

            out[i] = scr[i + r]       for i + r <  m
            out[i] = scr[i + r - m]   for i + r >= m
            out[i] = scr[i]           for i >= m

        This is the postcondition `lemma_three_reverses` proves for
        reverse(0,r);reverse(r,m);reverse(0,m), and stating it this way is what
        makes the model an independent implementation rather than a second copy
        of the kernel."""
        out = bytearray(scr)
        for i in range(m):
            out[i] = scr[i + r] if i + r < m else scr[i + r - m]
        return out

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
            r = self._u32_at(buf, off + p + 4)
            p += REC_HDR
            m = min(nelem, SCR)
            if ln - p < nelem:
                break
            scr = bytearray(scr)
            for i in range(m):
                scr[i] = buf[off + p + i]
            p += nelem
            r = r % m if m else 0
            scr = self._rot_left(scr, m, r)
            acc = self._fold_scr(scr, 0, m, acc)
            acc = (acc * 31 + m) & MASK
            rec += 1
        return (acc * 31 + nrec) & MASK

    def rotate_fold(self, buf, off, ln):
        """`rotate_fold` in ../verus.rs: what the kernel must return."""
        if ln < HDR:
            return 0
        nrec = self._u32_at(buf, off)
        if nrec == 0:
            return 0
        return self._walk(buf, off, ln, 0, nrec, HDR, bytearray(SCR), 0)

    @property
    def helpers(self):
        return {"rotate_fold": self.rotate_fold}

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
            header are decoded as `u32`s and are neither copied, rotated nor
            folded;
          * *over*-count on a record with `nelem > SCR`: the undeclared tail is
            skipped by the cursor and never read. `degenerate` is the only
            matrix input with such a record;
          * *under*-count, and it dominates: every copied byte is **copied,
            swapped about once and folded**, i.e. visited at least three times.

        On `small` the visits are 157 copied + ~157 swapped + 157 folded = 471
        against a declared stride of 201, and on `large` 52 + ~52 + 52 = 156
        against 152. So `stride` is at or below the number of byte-visits on
        both, the derived floor is one the kernel must clear, and it can never
        let a collapsed kernel through -- which is the only direction that
        matters. (`large`'s margin is thin *by design*: its records are 1..8
        bytes, so the per-record header is 8 of every ~12.7 window bytes and the
        window is mostly header. That makes the floor tighter there than on any
        earlier pattern, which is the safe direction.)

        No `min_ir_per_work` is declared, so the harness default of 0.25 Ir per
        byte applies unchanged. The argument is p12's: the fold is a **serial
        Horner chain**, `acc = acc*31 + b`, so byte `i+1`'s multiply depends on
        byte `i`'s and there is no vector form at any `-march`, and the three
        reverses are scalar swap loops in every rung and every compiler
        (measured on the disassembly, ../NOTES.md 1). The *copy* alone can go
        far below 0.25 -- it is a `memcpy` in every rung -- which is exactly why
        the unit is denominated over the whole window and not over the copy."""
        return self._work if self.entered else 0

    # -- sanitizer expectation ---------------------------------------------
    @property
    def sanitizer_expect(self):
        """Derived from the simulated run, never tabulated per file.

        R1 does not reduce the rotate amount, so it is a memory error exactly
        when some visited window holds a record with `r > SCR` -- REGIME 2. Note
        what this does NOT include: regime 1, `m <= r <= SCR`, where R1 computes
        a different rotation entirely and stays inside the array. That is p06's
        whole point and it is why the two regimes get separate rows:

          `adversarial-inarray`  three records at `r` = 40, 50 and 64 against
                                 `m` = 16, 32 and 8. Wrong answer in both C
                                 rungs, **clean** under ASan+UBSan, no panic in
                                 any Rust rung and no panic in the
                                 delete-the-check controls either.
          `adversarial-past1`    `r = 65`: R1 touches `scr[64]`, exactly one
                                 byte past.
          `adversarial-past48`   `r = 112`: 48 bytes past.
          `adversarial-pastfar`  `r = 100000`: the frame is gone.

        ../NOTES.md 7 records what each does at the gate's flags."""
        return "fires" if self.any_overrun else "clean"

    # -- what a conforming driver does -------------------------------------
    @property
    def expected_exit(self):
        # p06's payload allocates nothing from an attacker-controlled size --
        # there is no `cap` word and no `slb_zeroed` -- so p02's exit 7 has no
        # analogue here, exactly as for p03, p11, p12, p16, p17, p05 and p07.
        # The scratch is a fixed-size local in every rung. `slb_load` rejecting
        # a short file is the only non-zero exit this driver produces.
        #
        # This is the CHECKED rungs' exit. R1's exit on the three `past` rows is
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
        """three-reverse simulation vs the closed-form rotation that mirrors the
        Verus spec functions."""
        problems = []
        for c in self.sample_calls(8):
            want = self.rotate_fold(c["buf"], c["off"], c["len"])
            if want != c["result"]:
                problems.append(
                    f"simulated result {c['result']} != rotate_fold() {want} "
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
