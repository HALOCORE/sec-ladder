#!/usr/bin/env python3
"""p42-goto-cleanup: the independent reference model the gate checks against.

The API `harness/check.py` requires is documented in
`patterns/p01-array-sum/model.py`; this file adds three members of its own and
computes `sanitizer_expect` rather than declaring it.

    n_ok      int  -- kernel calls that took the SUCCESS path on this input
    n_err     int  -- kernel calls that took the ERROR path (tag mismatch).
                      Each one of those is a `malloc` the C rung never frees.
    leak_bytes int -- bytes the C rung leaks on this input: `n_err * win_len`,
                      because the digest is one byte per window element and the
                      error path releases none of it. ⚠ This is a DERIVED
                      INVARIANT, not a transcribed measurement: nothing here
                      records what LeakSanitizer printed, so re-running the gate
                      cannot move it (`.tasks/PROTOCOL.md` rule 6's newest
                      lesson -- a number only a rebuild can produce must not
                      live in a file the rebuild re-hashes).

⚠ `sanitizer_expect` is COMPUTED, not declared by name: it is "fires" exactly
when `n_err > 0`, i.e. when this input drives the kernel down the path that
leaks. p38 shipped a hand-written `"clean"` on every input and had to be
repaired at TASK_077; a derived expectation cannot go stale against its own
inputs.

--------------------------------------------------------------------------
Two implementations, and which one is which
--------------------------------------------------------------------------

`_run` / `_kernel_fast` simulate the whole driver loop, using a prefix-sum table
and a per-`off` memo. `digest_fold` re-derives one call the way the C rung does
it -- literally accumulating `run`, taking `(run >> 24) & 0xff`, and folding the
digest backwards. The `ensures` check and `selfcheck` use the SECOND one, so the
gate's correctness check is not this file agreeing with itself.

The memo is sound because a kernel call's result is a pure function of `off`
(and of `win_len`, which is fixed per file). It is worth having: `small.bin`
makes 60 000 calls over 4 000 distinct windows.
"""

import array
import itertools
import operator
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "common"))
import slb  # noqa: E402

MASK = (1 << 64) - 1
M32 = (1 << 32) - 1
TAG = 0xA7
MIX = 0x9E3779B97F4A7C15
# The driver's ceiling on the window length -- ../spec.md "Driver loop". Every
# rung carries it; a window above it makes zero kernel calls.
MAXWIN = 65536


class Model:
    def __init__(self, path):
        f = slb.read(path)
        self.path = path
        self.name = os.path.basename(path)
        self.n_iters = f.n_iters
        self.declared_len = f.declared_len
        self.truncated = f.truncated
        # The drivers read exactly `payload_len` bytes and reject a short file.
        self.payload = f.payload[: f.declared_len]
        self.win_len, self.vals = slb.head_u64_body(self.payload)
        self.v_len = len(self.vals)
        self.n_calls = 0
        self.n_ok = 0
        self.n_err = 0
        self.checksum = None
        self.entered = False
        self._nwin = None
        self._memo = {}
        if not self.truncated:
            self._prepare()
            self._run()

    # -- simulation --------------------------------------------------------
    def _prepare(self):
        """`p32[k]` = the low 32 bits of the wrapping sum of `v[j] ^ MIX` for
        `j < k`. The kernel's digest byte is bits 24..31 of a running sum, and
        a difference of two wrapping sums is exact modulo any power of two, so
        32 bits is all the state a digest byte can need."""
        p32 = array.array("Q", [0])   # "Q" is 8 bytes everywhere; the values
        acc = 0                       # are masked to 32 bits regardless
        ap = p32.append
        for x in self.vals:
            acc = (acc + (x ^ MIX)) & M32
            ap(acc)
        self._p32 = p32
        # 31**k mod 2^64, k = 0 .. win_len-1: the Horner fold of the digest read
        # backwards is exactly sum_k dig[k] * 31^k.
        w = int(self.win_len) if 0 < self.win_len <= min(MAXWIN, self.v_len) else 0
        pw, t = [], 1
        for _ in range(w):
            pw.append(t)
            t = (t * 31) & MASK
        self._pw = pw

    def _kernel_fast(self, off):
        r = self._memo.get(off)
        if r is not None:
            return r
        if (self.vals[off] & 0xFF) != TAG:
            r = 0
        else:
            w = int(self.win_len)
            c = self._p32[off]
            seg = self._p32[off + 1: off + w + 1]
            digs = [((x - c) & M32) >> 24 for x in seg]
            r = sum(map(operator.mul, digs, self._pw)) & MASK
        self._memo[off] = r
        return r

    def _run(self):
        head, n_vals = self.win_len, self.v_len
        acc = 0
        if 0 < head <= MAXWIN and head <= n_vals:
            self.entered = True
            win = int(head)
            nwin = n_vals - win + 1
            self._nwin = nwin
            for _ in range(self.n_iters):
                off = (acc * nwin) >> 64
                if (self.vals[off] & 0xFF) != TAG:
                    self.n_err += 1
                else:
                    self.n_ok += 1
                r = self._kernel_fast(off)
                acc = (acc * 31 + r) & MASK
            self.n_calls = self.n_iters
        self.checksum = acc

    def iter_calls(self):
        """Replay the driver loop, yielding one binding per kernel call."""
        if not self.entered:
            return
        nwin = self._nwin
        win = int(self.win_len)
        acc = 0
        for _ in range(self.n_iters):
            off = (acc * nwin) >> 64
            r = self._kernel_fast(off)
            yield {"off": off, "len": win, "v_len": self.v_len, "v": self.vals,
                   "result": r}
            acc = (acc * 31 + r) & MASK

    def sample_calls(self, k):
        if not self.entered or k <= 0:
            return []
        step = max(1, self.n_calls // k)
        return list(itertools.islice(
            (c for i, c in enumerate(self.iter_calls()) if i % step == 0), k))

    # -- the second, independent implementation ----------------------------
    def digest_fold(self, v, off, ln):
        """One kernel call, done the way ../c/kernel.c does it: no prefix table,
        no memo, no powers of 31 -- accumulate, truncate, fold backwards.

        This is what the `ensures` clause and `selfcheck` are evaluated against.
        A prefix-sum simulation checked against itself proves nothing."""
        if (v[off] & 0xFF) != TAG:
            return 0
        dig = bytearray(ln)
        run = 0
        for i in range(ln):
            run = (run + (v[off + i] ^ MIX)) & MASK
            dig[i] = (run >> 24) & 0xFF
        acc = 0
        for i in range(ln):
            acc = (acc * 31 + dig[ln - 1 - i]) & MASK
        return acc

    @property
    def helpers(self):
        return {"digest_fold": self.digest_fold}

    # -- what the kernel must do, per call ---------------------------------
    @property
    def work_per_call(self):
        """Window elements the kernel actually scans, AVERAGED over the calls
        this input makes -- the error path allocates and returns without
        scanning anything, so an input that only ever errors does zero work per
        call and must not be given a floor as though it did `win_len`.

        On both measured inputs every call succeeds, so this is exactly
        `win_len` there and the derived anti-collapse floor is the ordinary
        one."""
        if not self.entered or self.n_calls == 0:
            return 0
        return (int(self.win_len) * self.n_ok) // self.n_calls

    # -- the leak, as an invariant rather than a transcript -----------------
    @property
    def leak_bytes(self):
        """What the UNHARDENED C rung leaks on this input. One byte per window
        element per erroring call, because the digest is `win_len` bytes and the
        error path releases none of it."""
        return self.n_err * int(self.win_len) if self.entered else 0

    # -- sanitizer expectation, DERIVED ------------------------------------
    @property
    def sanitizer_expect(self):
        """"fires" exactly on the inputs that reach the error path.

        There is no third state to get wrong: an input either drives the kernel
        past the tag test on every call (clean) or does not (the C rung leaks,
        LeakSanitizer reports, `check.py::check_sanitizers` requires it). The
        degenerate driver inputs make no calls at all and are clean by the same
        rule."""
        return "fires" if self.n_err > 0 else "clean"

    # -- what a conforming driver does -------------------------------------
    @property
    def expected_exit(self):
        return 5 if self.truncated else 0

    @property
    def expected_stdout(self):
        return "" if self.truncated else f"{self.checksum}\n"

    def describe(self):
        return (f"n_iters={self.n_iters} v_len={self.v_len} win={self.win_len} "
                f"calls={self.n_calls} ok={self.n_ok} err={self.n_err} "
                f"leak_bytes={self.leak_bytes} work/call={self.work_per_call} "
                f"sanitizer={self.sanitizer_expect} truncated={self.truncated} "
                f"expected={self.checksum}")

    def selfcheck(self):
        problems = []
        # 1. the two implementations must agree
        for c in self.sample_calls(8):
            if self.digest_fold(c["v"], c["off"], c["len"]) != c["result"]:
                problems.append(
                    f"prefix-table simulation disagrees with the literal "
                    f"digest fold at off={c['off']} len={c['len']}")
                break
        # 2. a MEASURED input must never reach the error path. If it did, the
        #    C rung would leak on a row declared clean -- and, worse, every
        #    measured number would be a leaking program's.
        if not self.name.startswith("adversarial") and self.n_err:
            problems.append(
                f"{self.name} is a measured input and reaches the error path "
                f"{self.n_err} times; measured cells must not leak")
        # 3. ../spec.md forbids an error path no committed input reaches, and
        #    `-mixed` is the row that has to reach BOTH. See inputs/gen.py's
        #    module docstring, point 3: an all-error trace looks like a mixed
        #    one until you count.
        if "mixed" in self.name and not (self.n_ok and self.n_err):
            problems.append(
                f"{self.name} must exercise BOTH paths; got ok={self.n_ok} "
                f"err={self.n_err}")
        return problems


def build(path):
    return Model(path)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        m = build(p)
        print(f"{os.path.basename(p):28s} {m.describe()}  selfcheck={m.selfcheck()}")
