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
                off = acc % nwin
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
            off = acc % nwin
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

    # -- what a conforming driver does -------------------------------------
    @property
    def expected_exit(self):
        return 5 if self.truncated else 0

    @property
    def expected_stdout(self):
        return "" if self.truncated else f"{self.checksum}\n"

    def describe(self):
        return (f"n_iters={self.n_iters} v_len={self.v_len} win={self.win_len} "
                f"calls={self.n_calls} truncated={self.truncated} "
                f"expected={self.checksum}")

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
