#!/usr/bin/env python3
"""p10-fir-stencil: the independent reference model the gate checks against.

The API is documented at the top of `patterns/p01-array-sum/model.py`; this file
notes only where p10 differs.

    bindings      buf/off/len/buf_len/result -- the READ-ONLY shape p03, p06,
                  p11, p12, p14, p16, p17, p05, p07 and p18 use, and NOT p02's
                  before/after shape. p10's kernel WRITES NOTHING ANYWHERE: it
                  has no destination buffer, no scratch and no table, and `s`,
                  `acc`, `i` and `j` are scalars.
    work_per_call **taps** -- one multiply-accumulate -- i.e. `nout * taps` for
                  the window. See the property's docstring for which way that
                  errs and why the unit is not bytes.
    work_unit     "tap"; `work_unit_bits` 16 (one sample byte + one coefficient
                  byte are consumed per tap).
    sanitizer     derived, not tabulated, and it needs TWO facts and not one:
                  R1 reads a byte out of the WINDOW exactly when a visited
                  window has `last == len`, and that byte is out of the
                  ALLOCATION only when the window is the last one in the blob.
                  `adversarial-fenceslack.bin` exists to separate the two.

Two independent implementations, as every earlier pattern does:

  * the **simulation** computes each output as
    `sum(a * b for a, b in zip(window, coeffs))` over Python's unbounded
    integers and masks to 32 bits ONCE per output -- no per-tap wrap at all,
    because Python has no width to overflow;
  * the **helper** `fir_fold` -- the one the derived `ensures` is evaluated
    against -- mirrors the Verus spec functions `dotp` / `fwalk` in
    ../verus.rs, wrapping at 32 bits after EVERY tap exactly as the exec code
    does, and walking a cursor rather than slicing.

    So the two implementations disagree about *where the width bound is
    applied* -- once per output against once per tap -- and agree about the
    answer, which is the only kind of agreement worth having. They are also
    written against different views of the buffer: the simulation slices the
    window out, the helper indexes `buf` absolutely the way `unsafe.rs` does.

    The helper is **iterative where the Verus functions are recursive**, for
    p11's reason: `dotp` recurses once per tap and `fwalk` once per output, and
    a window may declare more of either than CPython's recursion limit allows.

**Both implementations model the CHECKED kernel**, i.e. R1h and R2-R5. R1 is the
rung with the fencepost and is expected to disagree on exactly those inputs
where some visited window has `last == len` -- there and nowhere else, which is
why `inputs/gen.py` packs every benign window exactly full and why R1 is held to
the model's checksum on every non-`adversarial-*` stem.

**Why `degenerate.bin` is not named `adversarial-*`.** Its three windows are
`r = 0` (a one-tap FIR), `n == taps` (exactly one output, the window does not
slide) and `n < taps` (the window guard fires). All three are well-formed, no
window has `last == len`, R1 agrees with the model on all of them, and the gate
holds all eight cells to the model's checksum -- which is strictly stronger than
filing it as adversarial.
"""

import itertools
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "common"))
import slb  # noqa: E402

MASK = (1 << 64) - 1
M32 = (1 << 32) - 1
HDR = 8                   # n:u32, r:u32


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
        self.oob_window = False     # R1 reads past the WINDOW
        self.oob_alloc = False      # ...and past the ALLOCATION
        self._win = []              # per window: (result, r1_reads_past_window)
        self._work = 0
        if not self.truncated:
            self._run()

    # -- the window table (computed once) ----------------------------------
    def _window(self, off):
        """(result, R1_reads_one_byte_past_the_window) for the window at `off`.

        Implementation 1 of 2. Slices the window's coefficient and sample arrays
        out and reduces each position with `sum(a * b for a, b in zip(...))` in
        Python's unbounded integers, masking to 32 bits ONCE per output. The
        helper below wraps after every tap instead, which is a different route
        to the same answer and is why the two are worth running against each
        other.

        The second element records whether the rung with the WRONG fencepost --
        `last > len` rather than `last >= len` -- would accept this window. It
        does so exactly when `last == len`, i.e. when the window is one byte
        short of holding the samples it declares."""
        ln = self.stride
        if ln < HDR:
            return 0, False
        b = self.buf
        n = int.from_bytes(b[off:off + 4], "little")
        r = int.from_bytes(b[off + 4:off + 8], "little")
        taps = 2 * r + 1
        if n < taps:
            return 0, False
        last = 8 + taps + n - 1
        if last >= ln:
            # The checked rungs reject. R1 accepts iff `last == len` exactly:
            # anything beyond that its own `last > len` still rejects, which is
            # what makes the harm exactly one byte.
            return 0, last == ln
        coef = b[off + 8:off + 8 + taps]
        samp = b[off + 8 + taps:off + 8 + taps + n]
        acc = 0
        for i in range(n - 2 * r):
            s = sum(a * c for a, c in zip(samp[i:i + taps], coef)) & M32
            acc = (acc * 31 + s) & MASK
        return (acc * 31 + (n - 2 * r)) & MASK, False

    def _shape(self, off):
        """(nout, taps) for the window at `off`, 0 if the guards reject it."""
        ln = self.stride
        if ln < HDR:
            return 0, 0
        b = self.buf
        n = int.from_bytes(b[off:off + 4], "little")
        r = int.from_bytes(b[off + 4:off + 8], "little")
        taps = 2 * r + 1
        if n < taps or 8 + taps + n - 1 >= ln:
            return 0, taps
        return n - 2 * r, taps

    # -- simulation --------------------------------------------------------
    def _run(self):
        acc = 0
        if HDR <= self.stride <= self.n_blob:
            self.entered = True
            self.nwin = self.n_blob // self.stride
            self._win = [None] * self.nwin
            shapes = [self._shape(k * self.stride) for k in range(self.nwin)]
            self._work = min(a * b for a, b in shapes) if shapes else 0
            for _ in range(self.n_iters):
                k = (acc * self.nwin) >> 64
                if self._win[k] is None:
                    self._win[k] = self._window(k * self.stride)
                r, past = self._win[k]
                if past:
                    self.oob_window = True
                    # ...and out of the C driver's `bytes` malloc only if the
                    # stolen byte, at blob offset (k+1)*stride, is not in it.
                    if (k + 1) * self.stride >= self.n_blob:
                        self.oob_alloc = True
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
            r, _past = self._win[k]
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
    # (../verus.rs `dotp` / `fwalk`), indexes `buf` absolutely the way
    # `unsafe.rs` does rather than slicing, and wraps at 32 bits after EVERY tap.
    def _u32_at(self, buf, p):
        """`u32_at` in ../verus.rs, written out with `+` and `*` exactly as the
        rungs write it -- not `int.from_bytes`, which is the simulation's."""
        return (buf[p] + 256 * buf[p + 1] + 65536 * buf[p + 2]
                + 16777216 * buf[p + 3])

    def _dotp(self, buf, off, sb, i, taps):
        """`dotp` in ../verus.rs: one output, wrapping after every tap.
        Iterative -- see the module docstring."""
        s = 0
        j = 0
        while j < taps:
            s = (s + ((buf[off + sb + i + j] * buf[off + 8 + j]) & M32)) & M32
            j = j + 1
        return s

    def _fwalk(self, buf, off, sb, nout, taps):
        """`fwalk` in ../verus.rs. Iterative rather than recursive."""
        acc = 0
        i = 0
        while i < nout:
            acc = (acc * 31 + self._dotp(buf, off, sb, i, taps)) & MASK
            i = i + 1
        return acc

    def fir_fold(self, buf, off, ln):
        """`fir_fold` in ../verus.rs: what the kernel must return."""
        if ln < HDR:
            return 0
        n = self._u32_at(buf, off)
        r = self._u32_at(buf, off + 4)
        taps = 2 * r + 1
        if n < taps:
            return 0
        if 8 + taps + n - 1 >= ln:
            return 0
        nout = n - 2 * r
        return (self._fwalk(buf, off, 8 + taps, nout, taps) * 31 + nout) & MASK

    @property
    def helpers(self):
        return {"fir_fold": self.fir_fold}

    # -- what the kernel must do, per call ---------------------------------
    @property
    def work_unit(self):
        return "tap"

    @property
    def work_unit_bits(self):
        """One unit is one tap: one sample byte times one coefficient byte,
        accumulated. Two bytes are consumed per unit, so 16 bits."""
        return 16

    @property
    def work_per_call(self):
        """`nout * taps` -- the multiply-accumulates one call performs.

        **The unit is a TAP and not a BYTE, deliberately.** p10's kernel reads
        every sample byte `taps` times and every coefficient byte `nout` times,
        so a floor denominated in window bytes would understate the work by a
        factor of `taps` and would be trivially cleared on every input -- which
        is exactly the "skipping walker denominated in buffer bytes" failure
        `harness/check.py` names. A tap is the unit the kernel's inner loop
        iterates over.

        **Which way this estimate errs: it is EXACT on every input the gate
        reads it from, and LOW elsewhere.** It is `min` over the windows of the
        blob, because the driver's `k` is pseudo-random and the model cannot
        know which windows a given `n_iters` visits. `inputs/gen.py` emits
        `small.bin` and `large.bin` -- the two `collapse.probe_inputs` -- with
        every window carrying the same `(n, r)`, so the minimum IS the value for
        every call, and the two shapes differ from each other (which
        `check.py`'s `d(Ir)/d(work)` assertion requires). On the heterogeneous
        sweep blobs the minimum understates, and no gate check reads it there.
        The exact per-input arithmetic is in ../NOTES.md 3.

        No `min_ir_per_work` is declared, so the harness default of 0.25 Ir per
        tap applies unchanged, and it is cleared by an order of magnitude:
        p10's tap loop VECTORISES at `-O3` to an SSE2 body of 17 instructions
        per 8 taps, i.e. **2.125 Ir/tap**, which is the smallest per-tap figure
        any p10 cell reaches and is 8.5x the floor (../NOTES.md 8). That is
        stated as the measurement it is, not as an argument that the loop
        cannot vectorise -- unlike p18, p10's loop demonstrably does."""
        return self._work if self.entered else 0

    # -- sanitizer expectation ---------------------------------------------
    @property
    def sanitizer_expect(self):
        """Derived from the simulated run, never tabulated per file.

        R1 writes `last > len` where `last` is an INDEX, so it accepts a window
        whose declared samples run exactly one byte past the window's end, and
        reads that byte. **Whether a sanitizer sees it is a property of the
        ALLOCATION and not of the program**, which is p02's result arriving on
        the read side at the smallest possible magnitude:

          `adversarial-fencepost`  the malformed window is the LAST one in the
                                   blob, so the stolen byte is one past the C
                                   driver's `bytes` malloc. **ASan fires.**
          `adversarial-fenceslack` the SAME window, with three trailing payload
                                   bytes that do not form a further window. The
                                   identical off-by-one reads a byte that is
                                   merely the wrong one. **Nothing fires** --
                                   ASan clean, UBSan clean, exit 0, wrong
                                   answer.
          `adversarial-farover`    a window declaring `n` far beyond what it
                                   holds. R1 and R1h reject it ALIKE, because
                                   an off-by-one buys exactly one byte.
                                   **Nothing fires, and the checksums agree.**

        UBSan has nothing to report on any p10 input: every arithmetic operation
        in every rung is unsigned and wrapping, and the two `size_t` guards make
        `n - 2*r` and `8 + taps + n - 1` both well-defined. p10's sanitizer row
        is ASan's alone. ../NOTES.md 7."""
        return "fires" if self.oob_alloc else "clean"

    # -- what a conforming driver does -------------------------------------
    @property
    def expected_exit(self):
        # p10's payload allocates nothing from an attacker-controlled size --
        # there is no `cap` word and no `slb_zeroed` -- so p02's exit 7 has no
        # analogue here. `slb_load` rejecting a short file is the only non-zero
        # exit this driver produces.
        #
        # This is the CHECKED rungs' exit, and on p10 it is ALSO R1's on every
        # input: a one-byte overread faults nothing on a heap allocation of any
        # realistic size, so every C cell exits 0 on every row including the
        # adversarial ones.
        return 5 if self.truncated else 0

    @property
    def expected_stdout(self):
        return "" if self.checksum is None else f"{self.checksum}\n"

    def describe(self):
        return (f"n_iters={self.n_iters} stride={self.stride} "
                f"n_blob={self.n_blob} nwin={self.nwin} calls={self.n_calls} "
                f"work/call={self.work_per_call}taps "
                f"san={self.sanitizer_expect} "
                f"oob_win={self.oob_window} oob_alloc={self.oob_alloc} "
                f"truncated={self.truncated} expected={self.checksum}")

    def selfcheck(self):
        """sum-then-mask-once against wrap-after-every-tap."""
        problems = []
        for c in self.sample_calls(8):
            want = self.fir_fold(c["buf"], c["off"], c["len"])
            if want != c["result"]:
                problems.append(
                    f"simulated result {c['result']} != fir_fold() {want} "
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
