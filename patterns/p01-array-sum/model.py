#!/usr/bin/env python3
"""p01-array-sum: the independent reference model the gate checks against.

**Every pattern ships one of these.** `harness/check.py` loads
`patterns/pNN-*/model.py` and drives it through the API documented below; before
TASK_003 the model was hard-coded into `check.py` and all 47 patterns would have
had to fork the gate (TASK_002_REVIEW, M8).

The model is a *second implementation* of `spec.md`, written in Python from the
file bytes alone. Its job is to disagree with the rungs when the rungs are
wrong, so it must not share code with them beyond the file-format reader
(`common/slb.py`).

--------------------------------------------------------------------------
The API `harness/check.py` requires
--------------------------------------------------------------------------

    build(path) -> Model

`Model` must expose:

    n_iters          int    -- as declared in the file header
    truncated        bool   -- declared payload_len exceeds the bytes present
    checksum         int|None -- what a conforming driver prints, or None
    expected_exit    int    -- what a conforming driver exits with
    expected_stdout  str    -- exactly what it prints, newline included
    n_calls          int    -- kernel calls the driver makes on this input
    work_per_call    int    -- abstract units of work one kernel call must do
                       on this input, from the file bytes alone. p01: the
                       window length, i.e. elements summed. This is what makes
                       the anti-collapse floor **derived** rather than declared
                       (TASK_005 A1): `check.py` asserts marginal Ir per call
                       >= ALPHA * work_per_call with ALPHA a harness constant,
                       and given two probe inputs of different shape it also
                       asserts d(Ir)/d(work) >= ALPHA. Neither is settable from
                       `spec.md`. Units are the pattern's own -- elements here,
                       bytes copied for p02 -- and only the *ratio* has to be
                       meaningful, so a pattern may not scale one input's units
                       differently from another's.
    sanitizer_expect str    -- "clean" or "fires". `.memory/02-bench-rules.md`
                       says the adversarial row *records* whether the sanitizer
                       fired; p02's adversarial input is defined as the one
                       that trips ASan, so a hit there is the expected result,
                       and silence is the failure. p01 models no memory-safety
                       bug, so every input is "clean".
    iter_calls()     -> iterator of dict, one per kernel call. Each dict binds
                       the names the `requires`/`ensures` expressions in
                       spec.md use, and must contain "result". **Lazy** --
                       `large.bin` alone is 20 000 calls and some patterns will
                       be far worse.
    sample_calls(k)  -> list[dict], <= k calls spread across the whole run.
                       Used for the `ensures` re-derivation, which is O(len)
                       per call and cannot be run on every call.
    helpers          dict[str, callable] -- extra names those expressions may
                       use (p01 supplies `wrapping_sum`).
    describe()       -> str, one line for the gate's log
    selfcheck()      -> list[str] of problems with the model itself, empty when
                       healthy. This is where a pattern proves its model is not
                       circular: p01 simulates with prefix sums and re-derives
                       with literal addition, and reports a disagreement here.

Optional, and added at TASK_006 because the harness constant is unsound for a
byte-denominated unit of work:

    min_ir_per_work     float -- the cheapest legitimate instructions per unit
                       of `work_per_call` for **this algorithm**, replacing the
                       harness default ALPHA = 0.25. It is a claim about the
                       algorithm, not about this kernel, which is why it may be
                       declared at all: a reviewer judges it by reading the
                       argument beside it, without opening a rung. Declaring a
                       rate below the harness default also requires
                       `min_ir_per_work_why`, which the verdict prints on every
                       run, and two probe shapes so that `d(Ir)/d(work) >= rate`
                       still runs. p01 declares neither: 0.25 Ir per 64-bit
                       element summed is sound (measured minimum 1.83), and only
                       a pattern whose unit is *smaller* than a 64-bit lane --
                       p02's byte, where glibc `memcpy` achieves 0.104 -- needs
                       to move it.
    min_ir_per_work_why str  -- the argument for the number above.

Nothing else is assumed. A pattern whose kernel takes different arguments binds
different names; `spec.md`'s contract block and this file must agree, and the
gate fails loudly (NameError) if they do not.
"""

import itertools
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "common"))
import slb  # noqa: E402

MASK = (1 << 64) - 1


class Model:
    """Simulates ../spec.md's driver loop and kernel from the file alone.

    Two independent sum implementations on purpose: `_run` uses prefix sums
    (fast enough for 1.5 M elements) and `naive_sum` literally adds the
    elements. The `ensures` check would be circular without the second one, and
    `selfcheck()` cross-checks them."""

    def __init__(self, path):
        f = slb.read(path)
        self.path = path
        self.n_iters = f.n_iters
        self.declared_len = f.declared_len
        self.truncated = f.truncated
        # The drivers read exactly `payload_len` bytes and reject a short file.
        self.payload = f.payload[: f.declared_len]
        self.win_len, self.vals = slb.head_u64_body(self.payload)
        self.v_len = len(self.vals)
        self.n_calls = 0
        self.checksum = None
        self.entered = False
        self._nwin = None
        if not self.truncated:
            self._run()

    # -- simulation --------------------------------------------------------
    def _run(self):
        head, n_vals = self.win_len, self.v_len
        acc = 0
        if 0 < head <= n_vals:
            self.entered = True
            win = int(head)
            nwin = n_vals - win + 1
            self._nwin = nwin
            prefix = [0]
            prefix.extend(itertools.accumulate(self.vals,
                                               lambda a, b: (a + b) & MASK))
            self._prefix = prefix
            for _ in range(self.n_iters):
                off = (acc * nwin) >> 64
                r = (prefix[off + win] - prefix[off]) & MASK
                acc = (acc * 31 + r) & MASK
            self.n_calls = self.n_iters
        self.checksum = acc

    def iter_calls(self):
        """Replay the driver loop, yielding one binding per kernel call.

        Regenerated rather than stored: `large.bin` is 20 000 calls and a
        pattern with a cheap kernel could have millions."""
        if not self.entered:
            return
        win, nwin, prefix = int(self.win_len), self._nwin, self._prefix
        acc = 0
        for _ in range(self.n_iters):
            off = (acc * nwin) >> 64
            r = (prefix[off + win] - prefix[off]) & MASK
            yield {"off": off, "len": win, "v_len": self.v_len, "v": self.vals,
                   "result": r}
            acc = (acc * 31 + r) & MASK

    def sample_calls(self, k):
        if not self.entered or k <= 0:
            return []
        step = max(1, self.n_calls // k)
        return list(itertools.islice(
            (c for i, c in enumerate(self.iter_calls()) if i % step == 0), k))

    # -- the second, independent summation ---------------------------------
    def naive_sum(self, v, off, ln):
        acc = 0
        for x in v[off:off + ln]:
            acc = (acc + x) & MASK
        return acc

    @property
    def helpers(self):
        return {"wrapping_sum": self.naive_sum}

    # -- what the kernel must do, per call ---------------------------------
    @property
    def work_per_call(self):
        """Elements the kernel sums per call, from the file alone.

        `check.py` derives the anti-collapse floor from this, so it must be a
        lower bound on the real work and must not be inflated: an overstated
        `work_per_call` raises the floor on the *pattern's own* cells and is
        caught the first time a legitimate rung trips it."""
        return int(self.win_len) if self.entered else 0

    # -- sanitizer expectation ---------------------------------------------
    @property
    def sanitizer_expect(self):
        """p01 is the calibration pattern: no memory-safety bug, and its
        adversarial inputs attack the *driver's* input validation rather than
        the kernel (they make zero kernel calls). So ASan and UBSan must be
        silent on every one of them. p02 is where this returns "fires"."""
        return "clean"

    # -- what a conforming driver does -------------------------------------
    @property
    def expected_exit(self):
        return 5 if self.truncated else 0

    @property
    def expected_stdout(self):
        return "" if self.truncated else f"{self.checksum}\n"

    def describe(self):
        return (f"n_iters={self.n_iters} v_len={self.v_len} win={self.win_len} "
                f"calls={self.n_calls} work/call={self.work_per_call} "
                f"truncated={self.truncated} expected={self.checksum}")

    def selfcheck(self):
        """Prefix-sum simulation vs literal addition, on a few calls."""
        problems = []
        for c in self.sample_calls(8):
            if self.naive_sum(c["v"], c["off"], c["len"]) != c["result"]:
                problems.append(
                    f"prefix-sum model disagrees with naive sum at "
                    f"off={c['off']} len={c['len']}")
                break
        return problems


def build(path):
    return Model(path)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        m = build(p)
        print(f"{os.path.basename(p):28s} {m.describe()}  selfcheck={m.selfcheck()}")
