#!/usr/bin/env python3
"""p17-http-range: the independent reference model the gate checks against.

The API is documented at the top of `patterns/p01-array-sum/model.py`; this file
notes only where p17 differs.

    bindings      buf/off/len/buf_len/result, the read-only shape p16 uses.
                  p17's kernel writes nothing either -- but unlike p16 the
                  `ensures` here is **not** merely the value. See the note on
                  `range_fold` below and ../spec.md: p17's second harm is a
                  read that is *inside* the allocation, so it is invisible to
                  the trusted accessor's `requires` and only the functional
                  postcondition excludes it.
    work_per_call the WINDOW, in bytes -- i.e. `stride`, constant across every
                  call on a given input. Argued below, and the argument is
                  **weaker than p16's in one direction that must be stated**:
                  here the window is a lower bound on the bytes folded, not an
                  upper one.
    sanitizer     derived, not tabulated: an input is "fires" exactly when the
                  simulated run contains a call whose *unchecked* reading (R1's)
                  would start at a negative ABSOLUTE index, i.e. when
                  `off + len - s < 0` for some suffix `s` of some window the
                  driver actually selects. Note what this deliberately does NOT
                  include: `adversarial-leak.bin`, where `start < 0` but
                  `off + len - s >= 0`, so R1's read is in bounds of the
                  allocation. Declaring that input "fires" would be wrong, and
                  the gate would then fail if ASan stayed silent -- which is the
                  outcome p17 exists to demonstrate.

Two independent implementations, as p01, p02 and p16 do:

  * the **simulation** parses each window once, collecting the byte *slices*
    each served range covers and folding the concatenation with a single Horner
    pass. Per-window results go in a table, which is what makes 25 000 driver
    iterations tractable;
  * the **helper** `range_fold` -- the one the derived `ensures` is evaluated
    against -- is a byte-at-a-time recursive walk over the suffix table with no
    slicing and no table, mirroring the shape of the Verus spec functions
    `range_walk` / `fold_bytes` in ../verus.rs.

`selfcheck()` runs them against each other; a disagreement is reported there
rather than being silently absorbed into a green line.

**Both implementations model the CHECKED kernel**, i.e. R1h and R2-R5. R1 is the
rung with the bug and is expected to disagree on the two adversarial files; the
gate records that disagreement in its behaviour table rather than requiring it
to vanish (`.memory/02-bench-rules.md`).
"""

import itertools
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "common"))
import slb  # noqa: E402

MASK = (1 << 64) - 1


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
        self.any_negative_abs = False
        self.nwin = 0
        self._win = []          # per window: (result, negative_abs_reachable)
        if not self.truncated:
            self._run()

    # -- the window table (computed once) ----------------------------------
    def _window(self, off):
        """(result, any_negative_absolute_index) for the window at `off`.

        Implementation 1 of 2. Walks the suffix table collecting the *slices*
        the served ranges cover and folds the concatenation in one Horner pass
        at the end.

        The second element records whether a suffix in this window would make
        R1 -- the rung with no `start >= 0` test -- index at a negative
        *absolute* offset. That is `off + abs < 0`, i.e. `off + len - s < 0`,
        and it is strictly stronger than `start < 0`: a suffix with
        `content_len < s <= len` gives `start < 0` and an absolute index that is
        still inside the allocation. Only the stronger condition is a memory
        error, and only it may set `sanitizer_expect`."""
        ln = self.stride
        seen = bytearray()
        nserved = 0
        neg = False
        if ln < 2:
            return 0, False
        nsuf = self.buf[off] + 256 * self.buf[off + 1]
        if 2 + 2 * nsuf > ln:
            return 0, False
        body_start = 2 + 2 * nsuf
        content_len = ln - body_start
        for i in range(nsuf):
            s = self.buf[off + 2 + 2 * i] + 256 * self.buf[off + 3 + 2 * i]
            start = content_len - s
            end = content_len
            # `abs = body_start + start == len - s` and `n = end - start == s`
            # -- the identity ../spec.md is built on. The absolute index R1
            # would use is `off + abs`; record it before the check filters it.
            if start < end and off + body_start + start < 0:
                neg = True
            if start < end and start >= 0:
                base = off + body_start + start
                seen += self.buf[base: base + (end - start)]
                nserved += 1
        acc = 0
        for b in seen:
            acc = (acc * 31 + b) & MASK
        return (acc * 31 + nserved) & MASK, neg

    # -- simulation --------------------------------------------------------
    def _run(self):
        acc = 0
        if 2 <= self.stride <= self.n_blob:
            self.entered = True
            self.nwin = self.n_blob // self.stride
            self._win = [self._window(k * self.stride) for k in range(self.nwin)]
            for _ in range(self.n_iters):
                k = (acc * self.nwin) >> 64
                r, neg = self._win[k]
                if neg:
                    self.any_negative_abs = True
                acc = (acc * 31 + r) & MASK
            self.n_calls = self.n_iters
        self.checksum = acc

    def iter_calls(self):
        """Replay the driver loop, yielding one binding per kernel call.

        Regenerated rather than stored: `small.bin` is 25 000 calls. `buf` is
        the whole blob and is yielded by reference, so this costs nothing per
        call beyond the dict."""
        if not self.entered:
            return
        acc = 0
        for _ in range(self.n_iters):
            k = (acc * self.nwin) >> 64
            r, _neg = self._win[k]
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
    # (../verus.rs `range_walk` / `fold_bytes`): recursive over the suffix
    # table, byte-at-a-time over each served range, no slicing, no table, and
    # the same (acc, nserved) pair threaded through the recursion.
    def _fold_bytes(self, buf, frm, n, acc):
        """`fold_bytes` in ../verus.rs: acc, folded left over buf[frm..frm+n)."""
        for i in range(n):
            acc = (acc * 31 + buf[frm + i]) & MASK
        return acc

    def _nsuf_at(self, buf, off):
        """`nsuf_at` in ../verus.rs."""
        return buf[off] + 256 * buf[off + 1]

    def _suf_at(self, buf, off, i):
        """`suf_at` in ../verus.rs -- the i'th suffix request. Attacker data."""
        return buf[off + 2 + 2 * i] + 256 * buf[off + 3 + 2 * i]

    def _range_walk(self, buf, off, ln, i, acc, nserved):
        """`range_walk` in ../verus.rs, returning (acc, nserved)."""
        nsuf = self._nsuf_at(buf, off)
        if i >= nsuf:
            return acc, nserved
        body_start = 2 + 2 * nsuf
        content_len = ln - body_start
        s = self._suf_at(buf, off, i)
        start = content_len - s
        if start < content_len and start >= 0:
            return self._range_walk(
                buf, off, ln, i + 1,
                self._fold_bytes(buf, off + body_start + start,
                                 content_len - start, acc),
                (nserved + 1) & MASK)
        return self._range_walk(buf, off, ln, i + 1, acc, nserved)

    def range_fold(self, buf, off, ln):
        """`range_fold` in ../verus.rs: what the kernel must return."""
        if ln < 2:
            return 0
        if 2 + 2 * self._nsuf_at(buf, off) > ln:
            return 0
        acc, nserved = self._range_walk(buf, off, ln, 0, 0, 0)
        return (acc * 31 + nserved) & MASK

    @property
    def helpers(self):
        return {"range_fold": self.range_fold}

    # -- what the kernel must do, per call ---------------------------------
    @property
    def work_per_call(self):
        """The window, in bytes -- `stride` -- from the file alone.

        **Why the window, and the one way this argument is weaker than p16's.**
        `check.py` needs one scalar per input and hard-fails on `work <= 0`. A
        suffix-range server has a *distribution* of work per call: each request
        serves a different number of bytes, a request with `s == 0` serves none,
        and a request the check rejects serves none either. Denominating in
        *requests* is worse still -- `nsuf` is itself attacker-controlled, so
        the unit would move with the data. The window is the unit that does not
        move: it is fixed by the payload header and identical on every call of a
        given input.

        p16 could add that the window is a strict OVER-estimate of the bytes
        folded, so its derived floor errs strict. **p17 cannot, and the
        difference is real.** Every suffix serves a slice of the *same* body, so
        `nsuf` requests can each serve nearly all of it: the shipped inputs fold
        871 bytes per 506-byte window and 7145 per 4093-byte window, i.e. 1.72x
        and 1.75x the declared unit. The floor is therefore **looser** than the
        work actually done, not stricter, and `.memory/02-bench-rules.md`'s
        standing warning applies with full force -- this stage is a
        NOT-COLLAPSED smoke test and what certifies that the ranges were served
        is step 2, the model checksum, which folds every served byte and the
        served count. The measured margins are in NOTES.md 4.

        No `min_ir_per_work` is declared, so the harness default of 0.25 Ir per
        byte applies unchanged. That is legitimate here for p16's reason: the
        inner loop is a serial `acc = acc*31 + byte` Horner chain -- each byte's
        result feeds the next multiply -- so there is no bulk-memory instruction
        and no vector form that could undercut the default."""
        return self.stride if self.entered else 0

    # -- sanitizer expectation ---------------------------------------------
    @property
    def sanitizer_expect(self):
        """Derived from the simulated run, never tabulated per file.

        **The whole point of p17 is that this is NOT `start < 0`.** R1 omits the
        `start >= 0` test, so it serves every suffix with `s > content_len`. The
        absolute index it reads from is `off + body_start + start == off + len -
        s`, and the three regimes are:

            s <= content_len          in the body            correct
            content_len < s <= len    in the window's own metadata, and
                                      therefore IN BOUNDS of the allocation
            s > len (with off == 0)   before the allocation

        Only the third is a memory error. Declaring the second "fires" would
        make the gate demand a sanitizer report that must not come, and
        declaring it "clean" -- which is what this property does -- is what
        turns ASan's silence on `adversarial-leak.bin` into evidence rather than
        into a missing row.

        Note `off +`: a negative `abs` from a *middle* window would still be a
        valid index into the blob, so the condition is about the absolute index
        and not about `start`. That is also why `inputs/gen.py` builds both
        adversarial files with exactly one window -- with `nwin == 1` the driver
        always picks `k == 0`, so `off` is 0 and the regime is deterministic
        rather than a coin flip on the checksum."""
        return "fires" if self.any_negative_abs else "clean"

    # -- what a conforming driver does -------------------------------------
    @property
    def expected_exit(self):
        # p17's payload allocates nothing from an attacker-controlled size --
        # there is no `cap` word and no `slb_zeroed` -- so p02's exit 7 has no
        # analogue here, exactly as for p16. `slb_load` rejecting a short file is
        # the only non-zero exit this pattern's driver can produce.
        return 5 if self.truncated else 0

    @property
    def expected_stdout(self):
        return "" if self.checksum is None else f"{self.checksum}\n"

    def describe(self):
        return (f"n_iters={self.n_iters} stride={self.stride} "
                f"n_blob={self.n_blob} nwin={self.nwin} calls={self.n_calls} "
                f"work/call={self.work_per_call}B san={self.sanitizer_expect} "
                f"truncated={self.truncated} expected={self.checksum}")

    def selfcheck(self):
        """Slice-and-Horner simulation vs the recursive byte-at-a-time walk."""
        problems = []
        for c in self.sample_calls(8):
            want = self.range_fold(c["buf"], c["off"], c["len"])
            if want != c["result"]:
                problems.append(
                    f"simulated result {c['result']} != range_fold() {want} at "
                    f"off={c['off']}")
                break
        return problems


def build(path):
    return Model(path)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        m = build(p)
        print(f"{os.path.basename(p):28s} {m.describe()}  "
              f"exit={m.expected_exit} selfcheck={m.selfcheck()}")
