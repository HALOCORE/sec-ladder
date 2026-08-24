#!/usr/bin/env python3
"""p19-state-machine: the independent reference model the gate checks against.

A *second* implementation of ../spec.md, in Python, from the file bytes alone.
It shares no code with the rungs beyond `common/slb.py`. The API `check.py`
requires is documented at the top of `patterns/p01-array-sum/model.py`.

--------------------------------------------------------------------------
Bindings
--------------------------------------------------------------------------

Each `iter_calls()` dict binds `buf` (the whole blob), `off`, `len`, `buf_len`
and `result`, and `helpers` supplies `st_fold`. That is p01's set plus the blob,
because p19's kernel takes a *window* of an attacker-supplied blob and its
`requires` is about the window's placement inside it.

--------------------------------------------------------------------------
`work_per_call`, and the argument for its unit
--------------------------------------------------------------------------

**Bytes touched per call, minimised over the windows of the blob.** A call
reads the 2048-byte table (to validate it) and then folds `stride - 2048`
message bytes, so a conforming window touches `stride` bytes. It is a LOWER
bound and not an average: a window whose table is invalid stops at the first bad
entry, and a window shorter than the table does nothing at all, so those windows
contribute their real, smaller counts and the minimum is taken.

The unit is a byte, and `.memory/05-layout.md` step 2 says that has to be
argued rather than assumed, because the harness constant ALPHA = 0.25 Ir per
unit is justified in 64-bit-lane terms. p19 does one indexed load, one multiply
and one add per message byte and one compare per table byte: measured
6.75 Ir/byte on the unsafe rung and 9.9 on the naive safe one, i.e. 27x the
floor. So `min_ir_per_work` is NOT declared and the harness default stands.

--------------------------------------------------------------------------
Two implementations, cross-checked in `selfcheck()`
--------------------------------------------------------------------------

`_fold_rows()` splits the table into eight 256-byte rows and indexes a row per
byte; `st_fold()` -- the helper the `ensures` is re-derived through -- indexes
the flat 2048-byte table. Same function, different arithmetic; `selfcheck()`
fails if they ever disagree.

--------------------------------------------------------------------------
`sanitizer_expect` is COMPUTED, not declared by name
--------------------------------------------------------------------------

The model simulates `c/kernel.c` -- the rung with no validation pass -- and
reports whether any window drives a read outside `[0, n_blob)`. That is the
whole of p19's harm, and computing it means the two adversarial rows cannot be
mislabelled: `adversarial-oob` (a table entry of 255, 65 280 bytes past the
window) reports "fires", and `adversarial-confuse` (an entry of 8, whose row
lands inside the window's own message region) reports "clean" **because it
really is memory-safe** -- defined behaviour, no diagnostic, wrong answer. The
pair is the pattern's sharpest measurement and neither half is asserted here.
"""

import itertools
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "common"))
import slb  # noqa: E402

MASK = (1 << 64) - 1

#: Must equal `SLB_P19_NST` in c/kernel.h and `NST` in every Rust rung.
NST = 8
#: Bytes of transition table: NST rows of 256 columns.
TBL = NST * 256
#: What an invalid table folds to.
REJ = 0xD1B54A32D192ED03


def st_fold(buf, off, ln):
    """../spec.md's kernel, on the flat table. This is the helper the `ensures`
    is re-derived through, so it must not share code with `_fold_rows`."""
    if ln <= TBL:
        return 0
    w = buf[off:off + ln]
    for i in range(TBL):
        if w[i] >= NST:
            return REJ
    st = 0
    acc = 0
    for p in range(TBL, ln):
        st = w[st * 256 + w[p]]
        acc = (acc * 31 + st) & MASK
    return (acc * 31 + st) & MASK


def _fold_rows(buf, off, ln):
    """The same function, computed by splitting the table into eight rows."""
    if ln <= TBL:
        return 0
    w = buf[off:off + ln]
    rows = [w[r * 256:(r + 1) * 256] for r in range(NST)]
    for r in rows:
        for e in r:
            if e >= NST:
                return REJ
    st = 0
    acc = 0
    for b in w[TBL:ln]:
        st = rows[st][b]
        acc = (acc * 31 + st) & MASK
    return (acc * 31 + st) & MASK


def _unvalidated(buf, off, ln, n_blob):
    """`c/kernel.c`: the fold WITHOUT the validation pass.

    Returns `(result_or_None, oob)`. `oob` is True as soon as a read leaves
    `[0, n_blob)`; the simulation then stops, because what a real run would
    have read there is not defined. This is the only place the model describes
    the buggy rung, and it exists so that `sanitizer_expect` is a measurement."""
    if ln <= TBL:
        return 0, False
    st = 0
    acc = 0
    for p in range(off + TBL, off + ln):
        idx = off + st * 256 + buf[p]
        if idx >= n_blob:
            return None, True
        st = buf[idx]
        acc = (acc * 31 + st) & MASK
    return (acc * 31 + st) & MASK, False


def _work(buf, off, ln):
    """Bytes a conforming kernel really touches on this window."""
    if ln <= TBL:
        return 0
    w = buf[off:off + ln]
    for i in range(TBL):
        if w[i] >= NST:
            return i + 1
    return ln


class Model:
    """Simulates ../spec.md's driver loop and kernel from the file alone.

    The kernel is evaluated once per *window* and memoised: the driver makes up
    to 20 000 calls but a blob has only a handful of distinct windows, and the
    window index is a pure function of `acc`."""

    def __init__(self, path):
        f = slb.read(path)
        self.path = path
        self.n_iters = f.n_iters
        self.declared_len = f.declared_len
        self.truncated = f.truncated
        # The drivers read exactly `payload_len` bytes and reject a short file.
        self.payload = f.payload[:f.declared_len]
        self.stride_w, self.blob = slb.head1_u64_bytes(self.payload)
        self.n_blob = len(self.blob)
        self.n_calls = 0
        self.checksum = None
        self.entered = False
        self._nwin = 0
        self._stride = 0
        self._res = []
        self._oob = False
        if not self.truncated:
            self._run()

    # -- simulation --------------------------------------------------------
    def _run(self):
        if not (0 < self.stride_w <= self.n_blob):
            self.checksum = 0
            return
        self.entered = True
        stride = int(self.stride_w)
        nwin = self.n_blob // stride
        self._stride, self._nwin = stride, nwin
        self._res = [st_fold(self.blob, k * stride, stride) for k in range(nwin)]
        self._work = min(_work(self.blob, k * stride, stride)
                         for k in range(nwin))
        self._oob = any(_unvalidated(self.blob, k * stride, stride,
                                     self.n_blob)[1] for k in range(nwin))
        acc = 0
        for _ in range(self.n_iters):
            k = (acc * nwin) >> 64
            acc = (acc * 31 + self._res[k]) & MASK
        self.n_calls = self.n_iters
        self.checksum = acc

    def iter_calls(self):
        """Replay the driver loop, one binding per kernel call. Regenerated
        rather than stored: `small.bin` alone is 8 000 calls."""
        if not self.entered:
            return
        stride, nwin = self._stride, self._nwin
        acc = 0
        for _ in range(self.n_iters):
            k = (acc * nwin) >> 64
            r = self._res[k]
            yield {"buf": self.blob, "off": k * stride, "len": stride,
                   "buf_len": self.n_blob, "result": r}
            acc = (acc * 31 + r) & MASK

    def sample_calls(self, k):
        if not self.entered or k <= 0:
            return []
        step = max(1, self.n_calls // k)
        return list(itertools.islice(
            (c for i, c in enumerate(self.iter_calls()) if i % step == 0), k))

    @property
    def helpers(self):
        return {"st_fold": st_fold}

    # -- what the kernel must do, per call ---------------------------------
    @property
    def work_per_call(self):
        """Bytes touched per call, minimised over windows -- see the module
        docstring. A lower bound on the real work, never inflated: an
        overstated `work_per_call` raises the anti-collapse floor on the
        pattern's own cells."""
        return int(self._work) if self.entered else 0

    # -- sanitizer expectation ---------------------------------------------
    @property
    def sanitizer_expect(self):
        """Computed from the bytes: does `c/kernel.c` read outside the blob on
        any window of this input? See the module docstring."""
        return "fires" if self._oob else "clean"

    # -- what a conforming driver does -------------------------------------
    @property
    def expected_exit(self):
        return 5 if self.truncated else 0

    @property
    def expected_stdout(self):
        return "" if self.truncated else f"{self.checksum}\n"

    def describe(self):
        return (f"n_iters={self.n_iters} n_blob={self.n_blob} "
                f"stride={self.stride_w} nwin={self._nwin} "
                f"calls={self.n_calls} work/call={self.work_per_call} "
                f"san={self.sanitizer_expect} truncated={self.truncated} "
                f"expected={self.checksum}")

    def selfcheck(self):
        """Flat-table fold vs row-split fold, on every distinct window."""
        problems = []
        if not self.entered:
            return problems
        stride = self._stride
        for k in range(self._nwin):
            a = self._res[k]
            b = _fold_rows(self.blob, k * stride, stride)
            if a != b:
                problems.append(
                    f"flat-table fold {a} disagrees with row-split fold {b} "
                    f"at window {k} (off={k * stride} len={stride})")
                break
        return problems


def build(path):
    return Model(path)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        m = build(p)
        print(f"{os.path.basename(p):30s} {m.describe()}  "
              f"selfcheck={m.selfcheck()}")
