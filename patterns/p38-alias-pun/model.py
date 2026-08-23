#!/usr/bin/env python3
"""p38-alias-pun: the independent reference model the gate checks against.

The API is documented at the top of `patterns/p01-array-sum/model.py`; this
file notes only where p38 differs.

    bindings      buf/off/len/buf_len/result -- the READ-ONLY shape p03, p06,
                  p11, p12, p14, p16, p17, p05, p07, p10, p27 and p47 use.
                  p38's kernel writes only its own local scratch, which is not
                  a binding: nothing the caller can observe is written.
    work_per_call `stride` -- window bytes, the denomination eleven other
                  patterns use. p38's kernel touches every window byte once in
                  the decode loop before it walks a single record, so the
                  estimate is tight from below and strict.
    work_unit     "window byte"; `work_unit_bits` 8.
    sanitizer     derived, not tabulated: an input **"fires"** exactly when the
                  miscompiled walk indexes the `uint16_t[256]` scratch at or
                  past 256, which is `adversarial-huge` and `adversarial-oob`.
                  ⚠ **This read `"clean" on every input` until TASK_077**, and
                  that was a fact about the GATE's build flags -- stage 7 built
                  at `-O1` with no `-fstrict-aliasing`, so the UB was not
                  exploited in the binary the sanitizers ran on. The token is
                  in `check.py::check_sanitizers` now. **`adversarial-stale`
                  stays "clean" and is the interesting row**: its checksum
                  changes with no diagnostic from either sanitizer, because the
                  over-read stays inside the array. See `sanitizer_expect`.

**WHAT THIS MODEL COMPUTES IS THE DEFINED SEMANTICS, WHICH IS WHAT EVERY RUNG
EXCEPT ONE PRODUCES.** p38's C rung executes undefined behaviour, and on
gcc 13.3.0 at `-O2`/`-O3` the compiler answers a `uint32_t` load from the value
it read *before* a clamp written through `uint16_t` lvalues. The clamped length
is what this file models, because it is what the source says and what every
other rung does; the divergence is recorded in stage 4 and in ../NOTES.md 2.

Two independent implementations, as every earlier pattern does:

  * the **simulation** (`_window`) walks the record stream with Python
    `int.from_bytes` on a `bytes` object and a `min()` for the clamp;
  * the **helper** `rec_fold` -- the one the derived `ensures` is evaluated
    against -- mirrors the Verus spec functions in ../verus.rs term for term:
    the same `+`/`*` header decode the rungs write, an explicit word list, and
    the clamp spelled as the comparison the kernels write.

`selfcheck()` runs them against each other.
"""

import itertools
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "common"))
import slb  # noqa: E402

MASK = (1 << 64) - 1
HDR = 4                   # nrec:u32 LE
SCRATCH_W = 256           # must equal SLB_P38_SCRATCH_W and every rung's const


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
        self._work = 0
        self._win = []          # per window: (result, [(declared, used) ...])
        if not self.truncated:
            self._run()

    # -- the window table (computed once) ----------------------------------
    def _words(self, off):
        """The decoded scratch: `(len-4)/2` little-endian words, truncated to
        SCRATCH_W. Implementation 1 of 2; `rec_fold` builds the same list the
        way ../verus.rs's spec functions do."""
        nw = (self.stride - HDR) // 2
        if nw > SCRATCH_W:
            nw = SCRATCH_W
        b = self.buf
        return [b[off + HDR + 2 * j] | (b[off + HDR + 2 * j + 1] << 8)
                for j in range(nw)]

    def _window(self, off):
        """(result, [(declared rlen, rlen actually used) per record]).

        The second element is what makes p38's harm visible somewhere: a record
        whose declared length exceeds `room` is the one the clamp rewrites, and
        it is the one gcc -O3 then ignores. Nothing in the checksum shows it,
        so `describe()` reports it."""
        if self.stride < HDR:
            return 0, []
        b = self.buf
        nrec = int.from_bytes(b[off:off + 4], "little")
        if nrec == 0:
            return 0, []
        sc = self._words(off)
        nw = len(sc)
        acc, i, o, recs = 0, 0, 0, []
        while o < nrec and i + 2 <= nw:
            room = (nw - i - 2) // 2
            declared = sc[i] | (sc[i + 1] << 16)
            if declared > room:                       # THE CLAMP
                sc[i] = room & 0xFFFF
                sc[i + 1] = (room >> 16) & 0xFFFF
            n = sc[i] | (sc[i + 1] << 16)
            recs.append((declared, n))
            for k in range(2 * n):
                acc = (acc * 31 + sc[i + 2 + k]) & MASK
            i = i + 2 + 2 * n
            o = o + 1
        return (acc * 31 + o) & MASK, recs

    # -- simulation --------------------------------------------------------
    def _run(self):
        acc = 0
        if 8 <= self.stride <= self.n_blob:
            self.entered = True
            self.nwin = self.n_blob // self.stride
            self._win = [None] * self.nwin
            self._work = self.stride
            for _ in range(self.n_iters):
                k = (acc * self.nwin) >> 64
                if self._win[k] is None:
                    self._win[k] = self._window(k * self.stride)
                r, _recs = self._win[k]
                acc = (acc * 31 + r) & MASK
            self.n_calls = self.n_iters
        self.checksum = acc

    def iter_calls(self):
        """Replay the driver loop, yielding one binding per kernel call."""
        if not self.entered:
            return
        acc = 0
        for _ in range(self.n_iters):
            k = (acc * self.nwin) >> 64
            if self._win[k] is None:
                self._win[k] = self._window(k * self.stride)
            r, _recs = self._win[k]
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
    # What the derived `ensures` is evaluated against. It must not be the
    # simulation in disguise, so it mirrors the *Verus* spec functions in
    # ../verus.rs: `u32_at` written with + and * exactly as the rungs write it,
    # `dec` building the word list, and `rwalk` doing the clamp with the same
    # comparison the kernels write.
    def _u32_at(self, buf, p):
        return (buf[p] + 256 * buf[p + 1] + 65536 * buf[p + 2]
                + 16777216 * buf[p + 3])

    def _dec(self, buf, off, ln):
        """`dec` in ../verus.rs: the decoded scratch, word by word."""
        nw = (ln - HDR) // 2
        if nw > SCRATCH_W:
            nw = SCRATCH_W
        return [buf[off + HDR + 2 * j] + 256 * buf[off + HDR + 2 * j + 1]
                for j in range(nw)]

    def _rwalk(self, sc, nrec, i, o, acc):
        """`rwalk` in ../verus.rs. Iterative where the Verus function is
        recursive, for p11's, p14's, p27's and p47's reason: the recursion is
        once per record and per payload word, and a blob may carry more of
        either than CPython's recursion limit."""
        nw = len(sc)
        while o < nrec and i + 2 <= nw:
            room = (nw - i - 2) // 2
            if sc[i] + 65536 * sc[i + 1] > room:
                sc[i] = room % 65536
                sc[i + 1] = room // 65536
            n = sc[i] + 65536 * sc[i + 1]
            for k in range(2 * n):
                acc = (acc * 31 + sc[i + 2 + k]) & MASK
            i = i + 2 + 2 * n
            o = o + 1
        return (acc * 31 + o) & MASK

    def rec_fold(self, buf, off, ln):
        """`rec_fold` in ../verus.rs: what the kernel must return."""
        if ln < HDR:
            return 0
        nrec = self._u32_at(buf, off)
        if nrec == 0:
            return 0
        return self._rwalk(self._dec(buf, off, ln), nrec, 0, 0, 0)

    @property
    def helpers(self):
        return {"rec_fold": self.rec_fold}

    # -- what the kernel must do, per call ---------------------------------
    @property
    def work_unit(self):
        return "window byte"

    @property
    def work_unit_bits(self):
        return 8

    @property
    def work_per_call(self):
        """`stride` -- window bytes, the denomination p16, p05, p11, p12, p06,
        p14, p27 and p10 use.

        **Which way this estimate errs: strict.** The decode loop touches every
        window byte from `data_start` once before a single record is walked, so
        `stride` undercounts by the 4 header bytes it also reads and by every
        payload word the fold reads a *second* time. It over-counts only the
        tail of a window past SCRATCH_W words, which no shipped blob has, and
        the bytes of a record the `nrec` guard stops short of, which
        `degenerate.bin` has and which is not a `collapse.probe_input`."""
        return self._work if self.entered else 0

    # -- sanitizer expectation ---------------------------------------------
    def _ub_scratch_overrun(self, off):
        """Does the MISCOMPILED walk of the window at `off` index the scratch
        at or past `SCRATCH_W`?

        This is a model of the *undefined* execution, which nothing else in
        this file models: `_window`/`_rwalk` compute the DEFINED semantics --
        what the source says and what all seven other rungs produce. Here the
        clamp is written to `sc[i]`/`sc[i+1]` through `uint16_t` lvalues, and
        the re-read through the `uint32_t` pun is answered from the value the
        compiler already had, so `n` keeps its **declared** value while the
        stored words really are clamped. The fold then reads `sc[i+2+k]` for
        `k < 2*declared`, and `sc` is a `uint16_t[SCRATCH_W]`.

        Two outcomes, and p38's shipped inputs contain both:

          index >= SCRATCH_W   out of the array. UBSan says `index 256 out of
                               bounds for type 'uint16_t [256]'` and ASan says
                               `stack-buffer-overflow READ of size 2`. This is
                               `sanitizer_expect: "fires"`.
          index in [nw, SCRATCH_W)  past the DECODED words but still inside the
                               array. Uninitialised scratch, a wrong checksum,
                               and **no diagnostic from either sanitizer** --
                               `adversarial-stale.bin`'s shape, still "clean",
                               and the row that shows a sanitizer is not a
                               miscompile detector.

        The walk position `i` is exact up to and including the FIRST clamped
        record, because the two executions agree exactly while no clamp fires;
        after one, the defined walk's `i` and the miscompiled one's diverge, so
        this continues with the miscompiled `i` rather than the model's."""
        if self.stride < HDR:
            return False
        b = self.buf
        nrec = int.from_bytes(b[off:off + 4], "little")
        if nrec == 0:
            return False
        sc = self._words(off)
        nw = len(sc)
        i = o = 0
        while o < nrec and i + 2 <= nw:
            room = (nw - i - 2) // 2
            declared = sc[i] | (sc[i + 1] << 16)
            if declared > room:                       # the clamp is STORED...
                sc[i] = room & 0xFFFF
                sc[i + 1] = (room >> 16) & 0xFFFF
            n = declared                              # ...and IGNORED here
            if n and i + 2 + 2 * n - 1 >= SCRATCH_W:
                return True
            i = i + 2 + 2 * n
            o = o + 1
        return False

    @property
    def sanitizer_expect(self):
        """**"fires" exactly where the type pun walks the scratch out of the
        array, and "clean" everywhere else** -- derived from the simulated run,
        never tabulated per file (p18's rule).

        ⚠ **THIS PROPERTY RETURNED `"clean"` UNCONDITIONALLY UNTIL TASK_077,
        and that was a fact about the GATE'S BUILD FLAGS rather than about the
        kernel.** `harness/check.py`'s stage 7 builds `c/kernel.c` with gcc at
        `-O1 -fsanitize=address,undefined`; gcc enables `-fstrict-aliasing` at
        `-O2` and above and not at `-O1`, so the stage-7 binary was one in
        which p38's undefined behaviour is not exploited -- it clamps, it stays
        inside the scratch, and both sanitizers had nothing to report. **The
        hole was one FLAG wide, not one optimisation level wide** (a distinction
        this docstring got wrong until TASK_067, TASK_066_REVIEW M2: read
        literally the old wording said the repair was to RAISE stage 7's
        optimisation level, which would perturb every other pattern's sanitizer
        rows to fix this one). TASK_077 added the token
        `-fstrict-aliasing` to `check.py::check_sanitizers`, so stage 7 now
        sees p38 **at `-O1`** and this declaration has to describe what it
        sees.

        **What the token changes, re-derived at TASK_077 by building gate stage
        7's own command line twice -- with and without the token -- for all 22
        patterns and running both on every input**: **158 rows, 3 differ, all 3
        on p38.** Exactly one pattern moves. Of p38's three:

          adversarial-huge   declared record length 268435455 at word 0 with
                             room 48 -> `"fires"`, UBSan `index 256 out of
                             bounds for type 'uint16_t [256]'`
          adversarial-oob    declared 200, room 48, same diagnostic -> `"fires"`
          adversarial-stale  declared 60, room 48 -- the unclamped extent
                             reaches word 121, past the 98 decoded words and
                             **inside** the 256-word array. Checksum
                             10509230270850152637 -> 16931469174358590653 with
                             **no diagnostic at all**, so it stays `"clean"`.
                             That row is the pattern's point: the harm is a
                             MISCOMPILE, and a sanitizer is not a miscompile
                             detector.

        The remaining five inputs (`small`, `large`, `degenerate`,
        `adversarial-nrec`, `adversarial-stride7`) clamp nothing, and the
        sweep blobs clamp nothing either -- 0 clamped records across all 30 of
        them -- so the two builds are bit-identical in behaviour there.

        **Why this is derived and not a filename table**: the condition is a
        property of the *blob*, computed by `_ub_scratch_overrun` from the same
        decode the rungs perform, so appending a sweep band cannot silently
        acquire or lose a declaration. p18's `sanitizer_expect` is written the
        same way and for the same reason.

        `../controls/gen_controls.py --run s_asan_O3` is the `-O3` ASan build
        and `--run s_asan_O1_sa` the one-flag `-O1` one; ../NOTES.md 6 records
        both. Both now agree with gate stage 7 rather than standing in for it.
        """
        if not self.entered or self.truncated:
            return "clean"
        for k, w in enumerate(self._win):
            if w is None:           # a window the driver loop never visits
                continue
            if self._ub_scratch_overrun(k * self.stride):
                return "fires"
        return "clean"

    # -- what a conforming driver does -------------------------------------
    @property
    def expected_exit(self):
        return 5 if self.truncated else 0

    @property
    def expected_stdout(self):
        return "" if self.checksum is None else f"{self.checksum}\n"

    def describe(self):
        recs = self._win[0][1] if self._win and self._win[0] else []
        clamped = sum(1 for d, u in recs if d != u)
        return (f"n_iters={self.n_iters} stride={self.stride} "
                f"n_blob={self.n_blob} nwin={self.nwin} calls={self.n_calls} "
                f"work/call={self.work_per_call}B "
                f"rec(win0)={recs[:6]} clamped={clamped} "
                f"san={self.sanitizer_expect} "
                f"truncated={self.truncated} expected={self.checksum}")

    def selfcheck(self):
        """The simulation against `rec_fold`. They share no code: the
        simulation slices `bytes` and uses `int.from_bytes` and `//`, the
        helper builds a word list with `+`/`*` and uses `%`/`//` the way the
        Verus spec functions do."""
        problems = []
        for c in self.sample_calls(8):
            want = self.rec_fold(c["buf"], c["off"], c["len"])
            if want != c["result"]:
                problems.append(
                    f"simulated result {c['result']} != rec_fold() {want} "
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
