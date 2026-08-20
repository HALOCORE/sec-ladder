#!/usr/bin/env python3
"""p18-varint-shift: the independent reference model the gate checks against.

The API is documented at the top of `patterns/p01-array-sum/model.py`; this file
notes only where p18 differs.

    bindings      buf/off/len/buf_len/result -- the READ-ONLY shape p03, p06,
                  p11, p12, p14, p16, p17, p05 and p07 use, and NOT p02's
                  before/after shape. p18's kernel has no buffer at all: `val`,
                  `shift`, `nb`, `p` and `acc` are scalars, nothing is written
                  anywhere, and no rung of p18 ever reads out of bounds on any
                  input. The security property is therefore NOT carried by a
                  trusted accessor's `requires` -- it is carried by the kernel's
                  own `ensures`, because the bug is arithmetic. See the
                  `sanitizer_expect` docstring and ../NOTES.md 6.
    work_per_call **bytes of the window** -- `stride`. See the property's
                  docstring for which way that errs.
    work_unit     "byte"; `work_unit_bits` 8.
    sanitizer     derived, not tabulated: an input "fires" exactly when the
                  simulated run visits a window holding a varint of **eleven or
                  more** bytes. `shift` is `7 * nb`, so the eleventh byte is
                  shifted by 70 and C99 6.5.7p3 makes that undefined for a
                  64-bit operand. `-fsanitize=undefined` implies
                  `-fsanitize=shift`, so gate stage 7 reports it.

Two independent implementations, as every earlier pattern does:

  * the **simulation** decodes with Python's arbitrary-precision integers and
    masks to 64 bits at the end of each varint -- no `shift < 64` test at all,
    because Python has no width to overflow; the truncation is expressed as
    `& MASK`, which is a different way of saying the same thing and is the point
    of it being independent;
  * the **helper** `varint_fold` -- the one the derived `ensures` is evaluated
    against -- mirrors the Verus spec functions `vdec` / `vbytes` / `vwalk` in
    ../verus.rs, guarding each contribution with an explicit `shift < VBITS`
    exactly as the exec code does.

    So the two implementations disagree about *how the width bound is
    expressed* -- a final mask against a per-byte test -- and agree about the
    answer, which is the only kind of agreement worth having. On `truncating.bin`
    they are the two spellings of the second bug, and they still agree.

    It is **iterative where the Verus functions are recursive**, for p11's
    reason: `vwalk` recurses once per varint and a window may declare more
    varints than CPython's recursion limit allows.

**Both implementations model the CHECKED kernel**, i.e. R1h and R2-R5. R1 is the
rung with the bug and is expected to disagree on every input holding a varint of
eleven or more bytes -- **except where the OR saturates**, which
`adversarial-sat.bin` is built to demonstrate; the gate records that in its
behaviour table rather than requiring it either way
(`.memory/02-bench-rules.md`).

**Why `truncating.bin` and `degenerate.bin` are not named `adversarial-*`.**
Every varint in both is at most ten bytes, so no shift is ever out of range,
R1 agrees with the model on both, and the gate holds all eight cells to the
model's checksum on them -- which is strictly stronger than filing them as
adversarial. `truncating.bin` is where the SECOND bug lives: its varints end at
shift 63 with a `0x7f` payload, of which only bit 0 survives a `u64`, so six
bits of the encoded integer are discarded by the shift itself. Nothing in this
project's toolkit catches that -- not ASan, not UBSan, not `debug-assertions`,
not Miri, and not the proof, because `varint_fold` specifies what the PROGRAM
does and the program does it. ../NOTES.md 7b.
"""

import itertools
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "common"))
import slb  # noqa: E402

MASK = (1 << 64) - 1
U32 = (1 << 32) - 1
HDR = 4                   # nv:u32
VBITS = 64                # must equal every rung's VBITS
OVER_BYTES = 11           # 7*(11-1) == 70 >= VBITS: the first undefined shift


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
        self.any_overshift = False
        self.nwin = 0
        self._work = 0
        self._win = []          # per window: (result, r1_would_shift_past_64)
        if not self.truncated:
            self._run()

    # -- the window table (computed once) ----------------------------------
    def _window(self, off):
        """(result, R1_would_shift_by_64_or_more) for the window at `off`.

        Implementation 1 of 2. Accumulates in Python's unbounded integers with
        **no width test at all** and masks to 64 bits once per varint, which is
        a different route to the same answer from the helper's explicit
        `shift < VBITS` -- and is why the two are worth running against each
        other.

        The second element records whether the rung with **no** shift bound
        would execute `x << s` with `s >= 64`. `shift` is `7 * nb`, so the
        predicate is `nb >= 11` on some varint of this window -- and **not**
        `nb > 11`: at exactly eleven bytes the last shift is 70."""
        ln = self.stride
        if ln < HDR:
            return 0, False
        buf = self.buf
        nv = int.from_bytes(buf[off:off + 4], "little")
        if nv == 0:
            return 0, False
        acc, p, over = 0, HDR, False
        for _ in range(nv):
            if p == ln:
                break
            val, nb = 0, 0
            while p < ln:
                c = buf[off + p]
                p += 1
                nb += 1
                # No `shift < VBITS` here: Python's `<<` has no width, so the
                # bits above 63 simply exist and are discarded by the mask
                # below. That IS the truncating semantics, expressed the other
                # way round.
                val |= (c & 0x7f) << (7 * (nb - 1))
                if not (c & 0x80):
                    break
            if nb >= OVER_BYTES:
                over = True                  # what R1 would do, recorded
            acc = (acc * 31 + (val & MASK)) & MASK
            acc = (acc * 31 + nb) & MASK
        return (acc * 31 + nv) & MASK, over

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
                    self.any_overshift = True
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
    # (../verus.rs `vdec` / `vbytes` / `vwalk`) and, crucially, carries the
    # explicit per-byte `shift < VBITS` test the exec code carries rather than
    # masking at the end.
    def _u32_at(self, buf, p):
        """`u32_at` in ../verus.rs, written out with `+` and `*` exactly as the
        rungs write it -- not `int.from_bytes`, which is the simulation's."""
        return (buf[p] + 256 * buf[p + 1] + 65536 * buf[p + 2]
                + 16777216 * buf[p + 3])

    def _vdec(self, buf, at, end, p, shift, val):
        """`vdec` in ../verus.rs: the value one varint decodes to, walking a
        cursor from `p` with the explicit width test. Iterative -- see the
        module docstring."""
        while p < end:
            c = buf[at + p]
            p += 1
            if shift < VBITS:
                val = (val | ((c & 0x7f) << shift)) & MASK
            shift = (shift + 7) & U32
            if not (c & 0x80):
                break
        return val

    def _vbytes(self, buf, at, end, p):
        """`vbytes` in ../verus.rs: how many bytes that varint consumes."""
        nb = 0
        while p < end:
            c = buf[at + p]
            p += 1
            nb += 1
            if not (c & 0x80):
                break
        return nb

    def _vwalk(self, buf, off, ln, v, nv, p, acc):
        """`vwalk` in ../verus.rs. Iterative rather than recursive."""
        while v < nv:
            if p == ln:
                break
            val = self._vdec(buf, off, ln, p, 0, 0)
            nb = self._vbytes(buf, off, ln, p)
            p += nb
            acc = (acc * 31 + val) & MASK
            acc = (acc * 31 + nb) & MASK
            v += 1
        return acc

    def varint_fold(self, buf, off, ln):
        """`varint_fold` in ../verus.rs: what the kernel must return."""
        if ln < HDR:
            return 0
        nv = self._u32_at(buf, off)
        if nv == 0:
            return 0
        return (self._vwalk(buf, off, ln, 0, nv, HDR, 0) * 31 + nv) & MASK

    @property
    def helpers(self):
        return {"varint_fold": self.varint_fold}

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

        **Which way this estimate errs: HIGH, by exactly the four header bytes,
        on every matrix input this pattern ships** (`.memory/02-bench-rules.md`
        asks, so: say it, and say it in the direction it really goes rather than
        claiming the comfortable one).

          * the 4 window-header bytes are decoded as a `u32` and are not
            scanned, so `stride` counts 4 bytes the varint loop never touches;
          * every other window byte is visited **exactly once** -- `nv` is
            honest on `small`, `large`, `truncating` and every sweep blob, so
            the cursor reaches `len`;
          * `degenerate.bin` declares `nv = 9` against 5 varints, but its five
            varints consume all 18 of its non-header bytes, so the outer guard
            fires with nothing left and the count is again `stride - 4`.

        So the derived floor is `stride * 0.25` Ir/call = 29.00 on `small`,
        against a kernel that executes about 11 instructions per scanned byte:
        it is cleared by roughly 40x, and the 4-byte overstatement is 1.00 Ir of
        a 29.00 floor. The exact per-input arithmetic is in ../NOTES.md 3.
        **A floor that errs high is the direction that can produce a false
        FAILURE and never a false pass**, which is the safe direction for this
        check, and the margin above says by how much.

        No `min_ir_per_work` is declared, so the harness default of 0.25 Ir per
        byte applies unchanged. The argument is p12's, p06's and p14's: the fold
        is a **serial Horner chain**, `acc = acc*31 + x`, so varint `i+1`'s
        multiply depends on varint `i`'s; and the scan is inherently scalar and
        serial in a way no earlier pattern's is -- **a varint's length is not
        known until its last byte has been read**, so there is no vector form of
        this loop at any `-march` and no compiler emitted one (measured on the
        disassembly of all eight cells, ../NOTES.md 1)."""
        return self._work if self.entered else 0

    # -- sanitizer expectation ---------------------------------------------
    @property
    def sanitizer_expect(self):
        """Derived from the simulated run, never tabulated per file.

        R1 does not bound the shift count, so it executes undefined behaviour
        exactly when some visited window holds a varint of **eleven or more**
        bytes: `shift` is `7 * nb`, so byte eleven is shifted by 70 and C99
        6.5.7p3 makes `x << s` undefined for `s >= 64` on a 64-bit operand.
        Note what this does NOT include: a **ten**-byte varint ends at shift 63
        and is the boundary from the safe side, on which R1 and R1h agree
        exactly -- `degenerate.bin`'s third varint is that case.

          `adversarial-shift11`  one 11-byte varint: the minimal divergence,
                                 one byte and one bit (0 against 64).
          `adversarial-shift20`  one 20-byte varint: ten oversized bytes at ten
                                 DISTINCT masked shifts.
          `adversarial-many`     six 11-byte varints: the undefined shift
                                 repeats within one call.
          `adversarial-sat`      one 20-byte varint of `0x7f` payloads. **UB
                                 executes on ten bytes and R1 and R1h return
                                 the SAME value**, because `|=` into a bit that
                                 is already set is a no-op. The sanitizer fires
                                 and the checksum cannot see it -- which is why
                                 this row exists.

        **This is the first pattern here whose sanitizer row is UBSan's and not
        ASan's.** ASan is silent on every input of p18, on every rung, because
        nothing is ever accessed out of bounds. ../NOTES.md 7 records what each
        row does at the gate's flags."""
        return "fires" if self.any_overshift else "clean"

    # -- what a conforming driver does -------------------------------------
    @property
    def expected_exit(self):
        # p18's payload allocates nothing from an attacker-controlled size --
        # there is no `cap` word and no `slb_zeroed` -- so p02's exit 7 has no
        # analogue here, exactly as for p03, p06, p11, p12, p14, p16, p17, p05
        # and p07. The kernel has no buffer at all. `slb_load` rejecting a short
        # file is the only non-zero exit this driver produces.
        #
        # This is the CHECKED rungs' exit, and on p18 it is ALSO R1's on every
        # input: R1's undefined behaviour is a masked shift, which faults
        # nothing and aborts nothing, so every C cell exits 0 on every row
        # including the adversarial ones. That is the whole point of the
        # pattern and it is why `check.py`'s adversarial table records the
        # VALUE rather than the exit code here.
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
        """unbounded-then-mask against the explicit per-byte width test."""
        problems = []
        for c in self.sample_calls(8):
            want = self.varint_fold(c["buf"], c["off"], c["len"])
            if want != c["result"]:
                problems.append(
                    f"simulated result {c['result']} != varint_fold() {want} "
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
