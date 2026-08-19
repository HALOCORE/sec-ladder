#!/usr/bin/env python3
"""p11-nul-scan: the independent reference model the gate checks against.

The API is documented at the top of `patterns/p01-array-sum/model.py`; this file
notes only where p11 differs.

    bindings      buf/off/len/buf_len/result, the read-only shape p16, p17, p05
                  and p07 use. p11's kernel writes nothing.
    work_per_call **bytes of the window** -- `stride`. Every byte of a
                  well-formed window is scanned once and every non-terminator
                  byte is folded once, so the kernel touches the whole window
                  twice; `stride` is the smaller of the two counts and is what
                  is declared. See the property's docstring for the direction of
                  the error.
    work_unit     "byte"; `work_unit_bits` 8.
    sanitizer     derived, not tabulated: an input is "fires" exactly when the
                  simulated run contains a call in which R1 -- the rung whose
                  scan is bounded by the sentinel and not by the window -- would
                  read at or past `n_blob`, i.e. when some string's scan finds no
                  zero byte anywhere in the remainder of the blob.

Two independent implementations, as p01, p02, p16, p17, p05 and p07 do:

  * the **simulation** finds each terminator with `bytes.find(0, lo, hi)` -- one
    bulk search per string, bounded by the window -- and folds with a slice
    iteration;
  * the **helper** `nul_scan_fold` -- the one the derived `ensures` is evaluated
    against -- mirrors the Verus spec functions `scan_end` / `fold_str` /
    `str_walk` in ../verus.rs: one byte at a time, every index written out as
    `off + q` / `off + i`, no `find`, no slicing and no bulk anything. The
    header is decoded by `_u32_at`'s written-out `b0 + 256*b1 + ...` rather than
    by `int.from_bytes`.

    It is **iterative where the Verus functions are recursive**, and that is a
    deliberate deviation rather than an oversight: `str_walk` recurses once per
    string and p11's windows hold up to 4096 declared strings, which is four
    times CPython's default recursion limit. The three functions are otherwise
    transliterations, including `str_walk`'s `q + 1 >= len` exit, which is what
    the exec rungs spell `p = q + 1; if p >= len { break; }`.

`selfcheck()` runs them against each other; a disagreement is reported there
rather than being silently absorbed into a green line.

**Both implementations model the CHECKED kernel**, i.e. R1h and R2-R5. R1 is the
rung with the bug and is expected to disagree on `adversarial-nonul` and
`adversarial-count`; the gate records that disagreement in its behaviour table
rather than requiring it to vanish (`.memory/02-bench-rules.md`).

**Neither implementation trusts `nstr`,** and neither does ../verus.rs. The walk
is bounded by the terminator and by `p >= len`, so a window declaring 4096
strings and holding 3 is *inside* the specification -- which is why
`adversarial-zerotail.bin` is a row where every rung agrees rather than a row
where anything is rejected. See ../NOTES.md 7.

Two arithmetic notes that are easy to get wrong and are load-bearing:

  * the per-string hash is folded as `h ^ slen`, so a rung that finds a
    different terminator cannot produce the same checksum even if it folds the
    same bytes. Python has no wrap, so every fold masks explicitly.
  * a string whose terminator is missing has `slen == len - p`, i.e. the scan
    stops at the window end. That is the checked semantics; R1 has no such stop.
"""

import itertools
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "common"))
import slb  # noqa: E402

MASK = (1 << 64) - 1
HDR = 4                   # nstr:u32


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
        self._win = []          # per window: (result, r1_would_overrun)
        if not self.truncated:
            self._run()

    # -- the window table (computed once) ----------------------------------
    def _window(self, off):
        """(result, R1_would_read_past_the_blob) for the window at `off`.

        Implementation 1 of 2. Finds each terminator with one `bytes.find`
        bounded by the window and folds with a slice iteration, which is a
        different code path from the byte-at-a-time `nul_scan_fold` below in
        every respect that matters.

        The second element records whether the rung whose scan has **no** window
        bound -- R1, which calls `strlen` -- would read at or past the end of the
        whole blob. Note it is about the blob, not about the window: a scan that
        runs out of a *middle* window lands in the next one and is a silent wrong
        answer rather than a memory error, which is exactly why `inputs/gen.py`
        builds every adversarial input with a single window."""
        ln = self.stride
        if ln < HDR:
            return 0, False
        buf = self.buf
        nstr = int.from_bytes(buf[off:off + 4], "little")
        if nstr == 0:
            return 0, False
        over = self._r1_overruns(off, nstr)
        acc, p, s = 0, HDR, 0
        while s < nstr:
            z = buf.find(0, off + p, off + ln)   # bounded by the WINDOW
            q = ln if z < 0 else z - off
            slen = q - p
            h = 0
            for b in buf[off + p:off + q]:
                h = (h * 31 + b) & MASK
            acc = (acc * 31 + ((h ^ slen) & MASK)) & MASK
            p = q + 1
            if p >= ln:
                break
            s += 1
        return (acc * 31 + nstr) & MASK, over

    def _r1_overruns(self, off, nstr):
        """Would R1's `strlen` read at or past `n_blob` on this window?

        R1's scan is bounded by the sentinel alone, so it stops at the first zero
        byte *anywhere in the blob*; `bytes.find(0, off + p)` with no upper bound
        is exactly that search, and `-1` means there is no zero byte left, i.e.
        the next read is `buf[n_blob]`. R1 keeps the outer bound `p >= len`, so
        it can overrun at most once per call -- the finding recorded in
        ../NOTES.md 7."""
        ln, p = self.stride, HDR
        while True:
            z = self.buf.find(0, off + p)         # NO upper bound: the sentinel
            if z < 0:
                return True
            p = (z - off) + 1
            if p >= ln:
                return False
        # `p` strictly increases, so this terminates in at most `ln` steps and
        # `nstr` never bounds it -- which is the point of adversarial-zerotail.

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

        Regenerated rather than stored: `small.bin` is 6000 calls. `buf` is the
        whole blob and is yielded by reference, so this costs nothing per call
        beyond the dict."""
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
    # (../verus.rs `scan_end` / `fold_str` / `str_walk`): one byte at a time,
    # every index written out, no `find`, no slice, no cache.
    def _u32_at(self, buf, p):
        """`u32_at` in ../verus.rs, written out with `+` and `*` exactly as the
        rungs write it -- not `int.from_bytes`, which is the simulation's."""
        return (buf[p] + 256 * buf[p + 1] + 65536 * buf[p + 2]
                + 16777216 * buf[p + 3])

    def _scan_end(self, buf, off, ln, q):
        """`scan_end` in ../verus.rs: the index of the first zero byte at or
        after `q`, capped at `ln`. THE SCAN, with the window bound."""
        while q < ln and buf[off + q] != 0:
            q += 1
        return q

    def _fold_str(self, buf, off, i, q, h):
        """`fold_str` in ../verus.rs: the Horner fold over `[i, q)`."""
        while i < q:
            h = (h * 31 + buf[off + i]) & MASK
            i += 1
        return h

    def _str_walk(self, buf, off, ln, s, nstr, p, acc):
        """`str_walk` in ../verus.rs. Iterative rather than recursive -- see the
        module docstring; the exit condition `q + 1 >= ln` is transliterated."""
        while s < nstr:
            q = self._scan_end(buf, off, ln, p)
            h = self._fold_str(buf, off, p, q, 0)
            acc = (acc * 31 + ((h ^ (q - p)) & MASK)) & MASK
            if q + 1 >= ln:
                return acc
            p = q + 1
            s += 1
        return acc

    def nul_scan_fold(self, buf, off, ln):
        """`nul_scan_fold` in ../verus.rs: what the kernel must return."""
        if ln < HDR:
            return 0
        nstr = self._u32_at(buf, off)
        if nstr == 0:
            return 0
        return (self._str_walk(buf, off, ln, 0, nstr, HDR, 0) * 31 + nstr) & MASK

    @property
    def helpers(self):
        return {"nul_scan_fold": self.nul_scan_fold}

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

        **Which way this estimate errs: STRICT, like p16's and p05's and unlike
        p17's** (`.memory/02-bench-rules.md` asks, so: say it). Two corrections
        pull in opposite directions and the net is strict:

          * *over*-count: the 4 header bytes are read as a `u32` and never
            scanned or folded, and each string's terminator is scanned but never
            folded, so a well-formed window folds `stride - 4 - nstr` bytes and
            not `stride`;
          * *under*-count: every folded byte is also **scanned**, so the kernel
            visits the window's bytes about twice.

        The under-count is the larger of the two on every input here (the
        terminators are 12.6% of `small` and 1.0% of `large`), so `stride` is at
        most the number of byte-visits and the floor it derives is one the kernel
        must clear. It can therefore never let a collapsed kernel through, which
        is the only direction that matters.

        No `min_ir_per_work` is declared, so the harness default of 0.25 Ir per
        byte applies unchanged. The argument for it here is easier than p02's
        (which had to declare 0.0625 because a bulk `memcpy` beats 0.25): p11's
        fold is a **serial Horner chain**, `h = h*31 + b`, so it cannot be
        vectorised at any `-march` -- byte `i+1`'s multiply depends on byte
        `i`'s. The scan alone could go below 0.25 (glibc's AVX2 `strlen`
        measures 0.078125 Ir/byte, ../NOTES.md 2), which is precisely why the
        unit is denominated over the whole window rather than over the scan."""
        return self._work if self.entered else 0

    # -- sanitizer expectation ---------------------------------------------
    @property
    def sanitizer_expect(self):
        """Derived from the simulated run, never tabulated per file.

        R1's scan is `strlen`, bounded by the sentinel; it is a memory error
        exactly when some string's scan finds no zero byte in the rest of the
        blob. Note it is the blob and not the window, because a scan that runs
        out of a *middle* window lands in the next one and is a silent wrong
        answer rather than something a sanitizer can see. `inputs/gen.py` builds
        every adversarial input with a single window so the two coincide.

        This returns "fires" for **two** inputs and the pair is the point.
        `adversarial-nonul` has an HONEST `nstr` and a declared string with no
        terminator. `adversarial-count` declares 4096 strings against 3 written
        and a non-zero tail, so R1 walks into bytes that were never a string.
        `adversarial-zerotail` has the IDENTICAL header lie with a NUL tail and
        is **clean in every rung** -- the two differ in the tail bytes and in
        nothing else, which is what makes "the sentinel, not the count, is the
        bound" a measurement."""
        return "fires" if self.any_overrun else "clean"

    # -- what a conforming driver does -------------------------------------
    @property
    def expected_exit(self):
        # p11's payload allocates nothing from an attacker-controlled size --
        # there is no `cap` word and no `slb_zeroed` -- so p02's exit 7 has no
        # analogue here, exactly as for p16, p17, p05 and p07. `slb_load`
        # rejecting a short file is the only non-zero exit this driver produces.
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
        """`bytes.find` + slice-fold simulation vs the byte-at-a-time walk that
        mirrors the Verus spec functions."""
        problems = []
        for c in self.sample_calls(8):
            want = self.nul_scan_fold(c["buf"], c["off"], c["len"])
            if want != c["result"]:
                problems.append(
                    f"simulated result {c['result']} != nul_scan_fold() {want} "
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
