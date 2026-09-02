#!/usr/bin/env python3
"""p13-strncpy-trunc: the independent reference model the gate checks against.

The API is documented at the top of `patterns/p01-array-sum/model.py`; this file
notes only where p13 differs.

    bindings      buf/off/len/buf_len/result -- the READ-ONLY shape p03, p11,
                  p12, p16, p17, p05 and p07 use, and NOT p02's before/after
                  shape. p13's destination is a **local** `dst[DST_CAP]` inside
                  the kernel, so no buffer crosses the signature and there is
                  nothing for a `dst_after` binding to name. p12's shape
                  exactly.
    work_per_call **`DST_CAP * strings-walked + source-bytes-scanned`**, and
                  NOT `stride`. p13 is the first pattern here whose per-call
                  cost is not monotone in the window length -- `strncpy` writes
                  `DST_CAP` bytes per string however short the source is -- and
                  the gate's `d(Ir)/d(work)` assertion caught the `stride`
                  denomination going NEGATIVE in 16 of 32 cells. See the
                  property's docstring.
    sanitizer     derived, not tabulated: an input "fires" exactly when the
                  simulated run contains a call in which some string has
                  `slen >= DST_CAP`, because that is exactly when the zero-fill
                  does not run, `dst` holds no NUL, and R1's consumer scan
                  leaves the array.

Two independent implementations, as every earlier pattern does:

  * the **simulation** finds each terminator with `bytes.find(0, lo, hi)` -- one
    bulk search per string, bounded by the window -- copies with a slice
    assignment and finds the destination terminator with `bytes.index(0)`;
  * the **helper** `strncpy_fold` -- the one the derived `ensures` is evaluated
    against -- mirrors the Verus spec functions `scan_end` / `copy_into` /
    `fill_zero` / `scan_dst` / `walk` in ../verus.rs: one byte at a time, every
    index written out, no `find`, no slicing and no bulk anything. The header is
    decoded by `_u32_at`'s written-out `b0 + 256*b1 + ...` rather than by
    `int.from_bytes`.

    It is **iterative where the Verus functions are recursive**, for p11's
    reason: `walk` recurses once per string and a window may declare more
    strings than CPython's recursion limit allows.

`selfcheck()` runs them against each other.

**Both implementations model the CHECKED kernel**, i.e. R1h and R2-R5. R1 is the
rung with the bug and is expected to disagree on every input where some string
reaches `DST_CAP`; the gate records that disagreement in its behaviour table
rather than requiring it to vanish (`.memory/02-bench-rules.md`).

**Why `small` and `large` are 100% NON-TRUNCATING, and why that is not a
choice.** `harness/check.py::check_checksums` requires every cell, R1 included,
to print this model's checksum on every non-adversarial **matrix** input
(`sweep-*` is dropped by `check.py::inputs_of`, whose comment reads *"`sweep-*`
files are diagnostic ... They are not part of the matrix"*). R1 omits the
termination store, so on
any window holding a string of `DST_CAP` bytes or more its consumer reads past
`dst[31]` -- and under `gcc -O3` the value it reads is not even stable across
runs (../NOTES.md 0). So a p13 row on which the bug fires cannot also be a
checksum-agreeing perf row, exactly as on p12 and for a related but distinct
reason: p12's is the FOLD, p13's is that the harm is an out-of-bounds READ of
memory outside the program's control. The truncation axis therefore lives in
`sweep-t*` and in the adversarial rows, and R1 is absent from the truncating
part of both.

**What this model DOES discriminate, and what it once did not.** ../spec.md's
fold is **full-extent**: `d`, then every one of the `DST_CAP` destination
bytes. Until TASK_046 it took `d` and `dst[0]` only -- TASK_043 specified that
and `.memory/02-bench-rules.md` has said "keep the full-extent fold" since
TASK_004_REVIEW -- and ../controls/oracle_hole.py measured the hole: a rung that
copied `0xFF` into every slot `1 .. n` instead of the source bytes printed the
identical checksum on all nine shipped inputs. Under the full-extent fold it
does not. The narrow fold's two worries were both measured and both unfounded:
the `exact`/`truncate`/`truncate-alt` triple still prints ONE checksum (the
copy is capped at `n = min(slen, DST_CAP)` and `dst[31] = 0` overwrites the
last slot, so `dst` is byte-identical across the three), and no C cell elides
the copy in `whole` mode. ../NOTES.md 6a.
"""

import itertools
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "common"))
import slb  # noqa: E402

MASK = (1 << 64) - 1
HDR = 4                   # nstr:u32
DST_CAP = 32              # must equal every rung's DST_CAP


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
        self._win = []          # per window: (result, r1_reads_past_dst)
        if not self.truncated:
            self._run()

    # -- the window table (computed once) ----------------------------------
    def _window(self, off):
        """(result, R1_reads_past_dst) for the window at `off`.

        Implementation 1 of 2. Finds each source terminator with one
        `bytes.find` bounded by the window, copies with a slice assignment and
        finds the destination terminator with `bytes.index` -- a different code
        path from the byte-at-a-time `strncpy_fold` below in every respect that
        matters.

        The second element records whether the rung with **no** termination
        store would read at or past `dst[DST_CAP]`. That happens exactly when
        some string has `slen >= DST_CAP`: the source scan stops at the first
        zero byte, so every copied byte is non-zero, and the zero-fill
        `for i in n .. DST_CAP` is empty precisely then. Like p12's and unlike
        p11's, the predicate is about the DESTINATION and does not depend on
        where the window sits in the blob."""
        ln = self.stride
        if ln < HDR:
            return 0, False
        buf = self.buf
        nstr = int.from_bytes(buf[off:off + 4], "little")
        if nstr == 0:
            return 0, False
        dst, acc, p, s, over = bytearray(DST_CAP), 0, HDR, 0, False
        nwalk, scanned = 0, 0
        while s < nstr:
            z = buf.find(0, off + p, off + ln)   # bounded by the WINDOW
            q = ln if z < 0 else z - off
            slen = q - p
            nwalk += 1
            # the source scan reads slen non-zero bytes plus, unless it stopped
            # at the window end, the terminator it stopped on
            scanned += slen + (1 if q < ln else 0)
            n = min(slen, DST_CAP)
            dst[0:n] = buf[off + p:off + p + n]
            dst[n:DST_CAP] = bytes(DST_CAP - n)
            if n >= DST_CAP:
                over = True                       # no NUL anywhere in dst
            dst[DST_CAP - 1] = 0                  # THE TERMINATION. R1 omits it.
            d = dst.index(0)
            acc = (acc * 31 + d) & MASK
            for fi in range(DST_CAP):             # THE FULL-EXTENT FOLD
                acc = (acc * 31 + dst[fi]) & MASK
            if q >= ln:
                break
            p = q + 1
            if p >= ln:
                break
            s += 1
        return (acc * 31 + nstr) & MASK, over, DST_CAP * nwalk + scanned

    # -- simulation --------------------------------------------------------
    def _run(self):
        acc = 0
        if HDR <= self.stride <= self.n_blob:
            self.entered = True
            self.nwin = self.n_blob // self.stride
            self._win = [None] * self.nwin
            work = None
            for _ in range(self.n_iters):
                k = (acc * self.nwin) >> 64
                if self._win[k] is None:
                    self._win[k] = self._window(k * self.stride)
                r, over, w = self._win[k]
                if over:
                    self.any_overrun = True
                # the MINIMUM over the windows actually visited: `work_per_call`
                # is a floor and a window nobody reaches cannot raise it
                work = w if work is None else min(work, w)
                acc = (acc * 31 + r) & MASK
            self.n_calls = self.n_iters
            self._work = work or 0
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
            r, _over, _w = self._win[k]
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
    # (../verus.rs `scan_end` / `copy_into` / `fill_zero` / `scan_dst` / `walk`):
    # one byte at a time, every index written out, no `find`, no slice, no cache.
    def _u32_at(self, buf, p):
        """`u32_at` in ../verus.rs, written out with `+` and `*` exactly as the
        rungs write it -- not `int.from_bytes`, which is the simulation's."""
        return (buf[p] + 256 * buf[p + 1] + 65536 * buf[p + 2]
                + 16777216 * buf[p + 3])

    def _scan_end(self, buf, off, ln, q):
        """`scan_end` in ../verus.rs: the index of the first zero byte at or
        after `q`, capped at `ln`. THE SOURCE SCAN, bounded by the window in
        EVERY rung -- p13's bug is not here."""
        while q < ln and buf[off + q] != 0:
            q += 1
        return q

    def _copy_into(self, dst, buf, off, p, i, n):
        """`copy_into` in ../verus.rs: `buf[off+p .. off+p+n)` into `dst[0..n)`,
        one byte at a time. `n` is `strncpy`'s `min(slen, DST_CAP)`."""
        out = bytearray(dst)
        while i < n:
            out[i] = buf[off + p + i]
            i += 1
        return out

    def _fill_zero(self, dst, i):
        """`fill_zero` in ../verus.rs: `strncpy`'s ZERO-FILL of `dst[i..DST_CAP)`.
        This is the half of `strncpy` nobody expects, and it is what makes the
        per-string cost O(DST_CAP) rather than O(slen)."""
        out = bytearray(dst)
        while i < DST_CAP:
            out[i] = 0
            i += 1
        return out

    def _scan_dst(self, dst, d):
        """`scan_dst` in ../verus.rs: THE CONSUMER. The index of the first zero
        byte of `dst` at or after `d`, **capped at DST_CAP**.

        The cap is what makes this a total function; the exec rungs have no cap
        at all and are defined only because `dst[DST_CAP - 1] == 0` holds when
        they run it. That gap IS the pattern: R1 executes the uncapped scan on a
        destination where the fact does not hold."""
        while d < DST_CAP and dst[d] != 0:
            d += 1
        return d

    def _fold_dst(self, acc, dst, i):
        """`fold_dst` in ../verus.rs: THE FULL-EXTENT FOLD. Every one of the
        `DST_CAP` destination bytes is mixed into the accumulator, in order.

        `.memory/02-bench-rules.md` has required the full-extent fold since
        TASK_004_REVIEW; p13 shipped a two-term one (`d` and `dst[0]`) at
        TASK_043's instruction and ../controls/oracle_hole.py measured what that
        cost -- a rung copying `0xFF` into every slot but the first agreed with
        this model on all nine shipped inputs. It does not now."""
        while i < DST_CAP:
            acc = (acc * 31 + dst[i]) & MASK
            i += 1
        return acc

    def _fin(self, acc, nstr):
        """`fin` in ../verus.rs: mix in the declared count."""
        return (acc * 31 + nstr) & MASK

    def _walk(self, buf, off, ln, s, nstr, p, dst, acc):
        """`walk` in ../verus.rs. Iterative rather than recursive -- see the
        module docstring; the exit condition `q + 1 >= ln` is transliterated
        from the exec rungs' `if q >= len { break }` / `p = q + 1` /
        `if p >= len { break }` pair.

        `dst` is threaded exactly as the exec rungs thread the array, even
        though the copy plus the zero-fill overwrite every one of its
        `DST_CAP` bytes and the carried value is therefore dead. Threading it
        is what makes the spec a transliteration rather than an argument."""
        while s < nstr:
            q = self._scan_end(buf, off, ln, p)
            slen = q - p
            n = slen if slen < DST_CAP else DST_CAP
            dst = self._copy_into(dst, buf, off, p, 0, n)
            dst = self._fill_zero(dst, n)
            dst[DST_CAP - 1] = 0
            d = self._scan_dst(dst, 0)
            acc = self._fold_dst((acc * 31 + d) & MASK, dst, 0)
            if q + 1 >= ln:
                return self._fin(acc, nstr)
            p = q + 1
            s += 1
        return self._fin(acc, nstr)

    def strncpy_fold(self, buf, off, ln):
        """`strncpy_fold` in ../verus.rs: what the kernel must return."""
        if ln < HDR:
            return 0
        nstr = self._u32_at(buf, off)
        if nstr == 0:
            return 0
        return self._walk(buf, off, ln, 0, nstr, HDR, bytearray(DST_CAP), 0)

    @property
    def helpers(self):
        return {"strncpy_fold": self.strncpy_fold}

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
        """**`DST_CAP * K + S`** -- destination bytes written plus source bytes
        scanned, minimised over the windows the driver actually visits, where
        `K` is the number of strings the kernel walks and `S` the bytes the
        source scan reads. From the file alone.

        ⚠ **`stride` -- the window's byte length, which p11, p12, p16, p05 and
        p07 all use -- is WRONG for p13, and the gate caught it.** `strncpy`
        writes `DST_CAP` bytes per string whatever the source length is, so the
        cost is dominated by `DST_CAP * K` and not by the window. p13's two
        probe inputs are built at opposite ends of the length/count trade
        (`small` 20 strings of mean 6.35 in a 151-byte window, `large` 10 of
        mean 23.60 in a 250-byte window), so on `stride` the work goes UP
        151 -> 250 while the measured `Ir` per call goes DOWN, and
        `check_marginal_ir`'s `d(Ir)/d(work)` came out **negative in 16 of the
        32 cells** (-2.09 to -10.83; `.temp/p13/gate1.log`). That is the gate
        doing exactly its job: the denomination, not the kernel, was the defect.
        The failure is worth keeping in the record because it is the first time
        this project has had a kernel whose per-call cost is **not** monotone in
        the window length.

        **Which way the estimate errs: STRICT** (`.memory/02-bench-rules.md`
        asks, so: say it). Per string the kernel visits

            (slen + 1) source bytes scanned      <-- counted, as S
          +  n         copied                    <-- counted, in DST_CAP
          + (DST_CAP - n) zero-filled             <-- counted, in DST_CAP
          +  1         termination store          <-- NOT counted
          + (d + 1)    consumer bytes             <-- NOT counted

        with `n = min(slen, DST_CAP)` and `d = min(slen, DST_CAP - 1)`, so the
        declared work omits the store and the whole consumer pass. On `small`
        the visits are 147 scanned + 127 copied + 513 filled + 20 stored + 147
        consumed = 954 against a declared 640 + 147 = 787; on `large` they are
        246 + 236 + 84 + 10 + 246 = 822 against 320 + 246 = 566. Over-counting
        terms exist -- the 4 header bytes are read as a `u32` and are in neither
        column -- and they are tiny beside that. So the declared work is under
        the number of byte-visits on every input, the derived floor is one the
        kernel must clear, and it can never let a collapsed kernel through,
        which is the only direction that matters.

        The **minimum** over visited windows rather than the maximum or the
        mean, for the same reason: a floor may not be raised by a window the
        driver never reaches. On every input this pattern ships all windows have
        the same shape, so the three agree.

        No `min_ir_per_work` is declared, so the harness default of 0.25 Ir per
        byte applies unchanged. The argument is p11's and p12's: the outer fold
        is a **serial Horner chain**, `acc = acc*31 + x` twice per string, so
        string `i+1`'s multiply depends on string `i`'s and there is no vector
        form at any `-march`. The *copy* and the *fill* alone go far below
        0.25 -- rustc turns both into `memcpy`/`memset` even in the rungs whose
        source is a byte loop -- which is exactly why the unit is not
        denominated over them alone."""
        return self._work if self.entered else 0

    # -- sanitizer expectation ---------------------------------------------
    @property
    def sanitizer_expect(self):
        """Derived from the simulated run, never tabulated per file.

        R1 omits the termination store, so it is a memory error exactly when
        some visited window holds a string of `DST_CAP` bytes or more: the
        source scan stops at the first zero byte, so the `n` copied bytes are
        all non-zero, and the zero-fill is empty precisely when `n == DST_CAP`.
        `dst` then contains no zero byte at all and R1's consumer walks out of
        the array.

        Note what this does NOT depend on: which window, and where in the blob
        it sits. Like p12's and unlike p11's, the overrun leaves the kernel's
        own stack frame wherever the window is.

        The ladder of adversarial rows is a ladder in **how far past** the read
        goes and in **whether the answer is stable**, not in overflow magnitude:
        `adversarial-exact` (31-byte strings) is clean in every rung and is the
        boundary from the safe side; `adversarial-truncate` (32) and
        `adversarial-truncate-alt` (40) are one byte over and far over, and
        print the SAME checksum as `exact` in every checked rung;
        `adversarial-nonul-dst` is the same harm at full stretch;
        `adversarial-nonul-src` reaches it through an unterminated source
        string. ../NOTES.md 0 and 7 record what each does at the gate's flags."""
        return "fires" if self.any_overrun else "clean"

    # -- what a conforming driver does -------------------------------------
    @property
    def expected_exit(self):
        # p13's payload allocates nothing from an attacker-controlled size --
        # there is no `cap` word and no `slb_zeroed` -- so p02's exit 7 has no
        # analogue here, exactly as for p03, p11, p12, p16, p17, p05 and p07.
        # The destination is a fixed-size local in every rung. `slb_load`
        # rejecting a short file is the only non-zero exit this driver produces.
        #
        # This is the CHECKED rungs' exit. R1 exits 0 with a wrong answer on
        # every truncating row -- its overread is 1 to 7 bytes into its own
        # frame and never reaches an unmapped page (../NOTES.md 0), so unlike
        # p12 there is no abort and no SIGSEGV anywhere in this pattern.
        # `check.py` records that in the adversarial table rather than
        # requiring it.
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
        """`bytes.find` + slice-copy simulation vs the byte-at-a-time walk that
        mirrors the Verus spec functions."""
        problems = []
        for c in self.sample_calls(8):
            want = self.strncpy_fold(c["buf"], c["off"], c["len"])
            if want != c["result"]:
                problems.append(
                    f"simulated result {c['result']} != strncpy_fold() {want} "
                    f"at off={c['off']}")
                break
        return problems


def build(path):
    return Model(path)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        m = build(p)
        print(f"{os.path.basename(p):32s} {m.describe()}  "
              f"exit={m.expected_exit} selfcheck={m.selfcheck()}")
