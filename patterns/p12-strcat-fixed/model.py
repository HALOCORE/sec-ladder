#!/usr/bin/env python3
"""p12-strcat-fixed: the independent reference model the gate checks against.

The API is documented at the top of `patterns/p01-array-sum/model.py`; this file
notes only where p12 differs.

    bindings      buf/off/len/buf_len/result -- the READ-ONLY shape p03, p11,
                  p16, p17, p05 and p07 use, and NOT p02's before/after shape.
                  p12's destination is a **local** `dst[DST_CAP]` inside the
                  kernel, so no buffer crosses the signature and there is
                  nothing for a `dst_after` binding to name. The security
                  property is therefore the trusted write accessor's
                  `i < v@.len()`, discharged at every store -- p03's shape
                  exactly, and p03 is the only earlier pattern that writes into
                  a fixed-size local.
    work_per_call **bytes of the window** -- `stride`. See the property's
                  docstring for which way that errs.
    work_unit     "byte"; `work_unit_bits` 8.
    sanitizer     derived, not tabulated: an input "fires" exactly when the
                  simulated run contains a call in which R1 -- the rung with no
                  capacity check -- would write at or past `dst[DST_CAP]`.

Two independent implementations, as every earlier pattern does:

  * the **simulation** finds each terminator with `bytes.find(0, lo, hi)` -- one
    bulk search per string, bounded by the window -- and copies with a slice
    assignment;
  * the **helper** `strcat_fold` -- the one the derived `ensures` is evaluated
    against -- mirrors the Verus spec functions `scan_end` / `copy_into` /
    `fold_dst` / `walk` in ../verus.rs: one byte at a time, every index written
    out as `off + q` / `off + i`, no `find`, no slicing and no bulk anything.
    The header is decoded by `_u32_at`'s written-out `b0 + 256*b1 + ...` rather
    than by `int.from_bytes`.

    It is **iterative where the Verus functions are recursive**, for p11's
    reason: `walk` recurses once per string and a window may declare more
    strings than CPython's recursion limit allows.

`selfcheck()` runs them against each other.

**Both implementations model the CHECKED kernel**, i.e. R1h and R2-R5. R1 is the
rung with the bug and is expected to disagree on every input where the capacity
check fires; the gate records that disagreement in its behaviour table rather
than requiring it to vanish (`.memory/02-bench-rules.md`).

**Why there is no `adversarial-zerotail` analogue here.** p11 ships a row on
which its header lies and every rung including R1 still agrees, because a READ
bug only shows up when the read leaves the allocation. A WRITE bug has no such
row: the moment the capacity check would have fired, R1 has copied bytes the
checked rungs skipped and ends with a larger `dlen`, and both are folded. So
`small` and `large` are necessarily 100% accept -- see `inputs/gen.py`.
"""

import itertools
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "common"))
import slb  # noqa: E402

MASK = (1 << 64) - 1
HDR = 4                   # nstr:u32
DST_CAP = 128             # must equal every rung's DST_CAP


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
        """(result, R1_would_write_past_dst) for the window at `off`.

        Implementation 1 of 2. Finds each terminator with one `bytes.find`
        bounded by the window and copies with a slice assignment, which is a
        different code path from the byte-at-a-time `strcat_fold` below in
        every respect that matters.

        The second element records whether the rung with **no** capacity check
        would write at or past `dst[DST_CAP]`. Unlike p11's, this predicate is
        about the DESTINATION and not about the source blob, so it does not
        depend on where the window sits -- a p12 overrun leaves the kernel's own
        stack frame wherever the window is, which is why the failure mode is a
        function of the overflow magnitude rather than of the layout."""
        ln = self.stride
        if ln < HDR:
            return 0, False
        buf = self.buf
        nstr = int.from_bytes(buf[off:off + 4], "little")
        if nstr == 0:
            return 0, False
        dst, dlen, r1_dlen, acc, p, s = bytearray(DST_CAP), 0, 0, 0, HDR, 0
        while s < nstr:
            z = buf.find(0, off + p, off + ln)   # bounded by the WINDOW
            q = ln if z < 0 else z - off
            slen = q - p
            r1_dlen += slen                      # R1 copies unconditionally
            if dlen + slen <= DST_CAP:
                dst[dlen:dlen + slen] = buf[off + p:off + q]
                dlen += slen
            acc = (acc * 31 + slen) & MASK
            if q >= ln:
                break
            p = q + 1
            if p >= ln:
                break
            s += 1
        for b in dst[:dlen]:
            acc = (acc * 31 + b) & MASK
        return ((acc * 31 + dlen) * 31 + nstr) & MASK, r1_dlen > DST_CAP

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
    # (../verus.rs `scan_end` / `copy_into` / `fold_dst` / `walk`): one byte at
    # a time, every index written out, no `find`, no slice, no cache.
    def _u32_at(self, buf, p):
        """`u32_at` in ../verus.rs, written out with `+` and `*` exactly as the
        rungs write it -- not `int.from_bytes`, which is the simulation's."""
        return (buf[p] + 256 * buf[p + 1] + 65536 * buf[p + 2]
                + 16777216 * buf[p + 3])

    def _scan_end(self, buf, off, ln, q):
        """`scan_end` in ../verus.rs: the index of the first zero byte at or
        after `q`, capped at `ln`. Bounded by the window in EVERY rung -- p12's
        bug is not in the scan."""
        while q < ln and buf[off + q] != 0:
            q += 1
        return q

    def _copy_into(self, dst, d, buf, off, p, q):
        """`copy_into` in ../verus.rs: append `buf[off+p .. off+q]` at `dst[d]`,
        one byte at a time. Returns the new destination sequence."""
        out = bytearray(dst)
        while p < q:
            out[d] = buf[off + p]
            d += 1
            p += 1
        return out

    def _fold_dst(self, dst, i, dlen, acc):
        """`fold_dst` in ../verus.rs: the Horner fold over `dst[i .. dlen)`."""
        while i < dlen:
            acc = (acc * 31 + dst[i]) & MASK
            i += 1
        return acc

    def _fin(self, dst, dlen, acc, nstr):
        """`fin` in ../verus.rs: fold the destination, then mix in `dlen` and
        the declared count, so a rung that truncated differently cannot produce
        the same checksum."""
        return ((self._fold_dst(dst, 0, dlen, acc) * 31 + dlen) * 31 + nstr) & MASK

    def _walk(self, buf, off, ln, s, nstr, p, dst, dlen, acc):
        """`walk` in ../verus.rs. Iterative rather than recursive -- see the
        module docstring; the exit condition `q + 1 >= ln` is transliterated
        from the exec rungs' `if q >= len { break }` / `p = q + 1` /
        `if p >= len { break }` pair."""
        while s < nstr:
            q = self._scan_end(buf, off, ln, p)
            slen = q - p
            if dlen + slen <= DST_CAP:
                dst = self._copy_into(dst, dlen, buf, off, p, q)
                dlen += slen
            acc = (acc * 31 + slen) & MASK
            if q + 1 >= ln:
                return self._fin(dst, dlen, acc, nstr)
            p = q + 1
            s += 1
        return self._fin(dst, dlen, acc, nstr)

    def strcat_fold(self, buf, off, ln):
        """`strcat_fold` in ../verus.rs: what the kernel must return."""
        if ln < HDR:
            return 0
        nstr = self._u32_at(buf, off)
        if nstr == 0:
            return 0
        return self._walk(buf, off, ln, 0, nstr, HDR, bytearray(DST_CAP), 0, 0)

    @property
    def helpers(self):
        return {"strcat_fold": self.strcat_fold}

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

        **Which way this estimate errs: STRICT** (`.memory/02-bench-rules.md`
        asks, so: say it). Three corrections, and the net is strict on every
        input this pattern ships:

          * *over*-count: the 4 header bytes are read as a `u32` and are neither
            scanned nor copied, and each terminator is scanned but never copied;
          * *over*-count on a REJECTING window: a rejected string's bytes are
            scanned but not copied and not folded. `small` and `large` accept
            everything, so this term is zero on both probe inputs and non-zero
            only on the adversarial rows and `sweep-a*`;
          * *under*-count, and it dominates on the probe inputs: every accepted
            byte is **scanned, copied and folded**, i.e. visited three times.

        On `small` the visits are 133 scanned + 123 copied + 123 folded = 379
        against a declared 133, and on `large` 159 + 124 + 124 = 407 against
        159. So `stride` is well under the number of byte-visits, the derived
        floor is one the kernel must clear, and it can never let a collapsed
        kernel through -- which is the only direction that matters.

        No `min_ir_per_work` is declared, so the harness default of 0.25 Ir per
        byte applies unchanged. The argument is p11's and it is easier here:
        the destination fold is a **serial Horner chain**, `acc = acc*31 + b`,
        so byte `i+1`'s multiply depends on byte `i`'s and there is no vector
        form at any `-march`. The *copy* alone can go far below 0.25 -- it is a
        `memcpy` in the rungs that spell it as one -- which is exactly why the
        unit is denominated over the whole window and not over the copy."""
        return self._work if self.entered else 0

    # -- sanitizer expectation ---------------------------------------------
    @property
    def sanitizer_expect(self):
        """Derived from the simulated run, never tabulated per file.

        R1 has no capacity check, so it is a memory error exactly when the
        strings of some visited window total more than `DST_CAP` bytes. Note
        what this does NOT depend on: which window, and where in the blob it
        sits. p11's overrun had to leave the whole allocation to be visible;
        p12's leaves the kernel's own frame no matter where the window is, so
        every row here is deterministic in a way p11's and p03's are not.

        Four inputs are relevant and they form a ladder in overflow magnitude:
        `adversarial-exact` totals exactly `DST_CAP` and is **clean in every
        rung**; `adversarial-off1` is the same four strings plus one more byte
        and R1 writes `dst[DST_CAP]`; `adversarial-nonul` reaches the same place
        through an unterminated last string; `adversarial-overflow` writes 128
        bytes past. ../NOTES.md 7 records what each does at the gate's flags."""
        return "fires" if self.any_overrun else "clean"

    # -- what a conforming driver does -------------------------------------
    @property
    def expected_exit(self):
        # p12's payload allocates nothing from an attacker-controlled size --
        # there is no `cap` word and no `slb_zeroed` -- so p02's exit 7 has no
        # analogue here, exactly as for p03, p11, p16, p17, p05 and p07. The
        # destination is a fixed-size local in every rung. `slb_load` rejecting
        # a short file is the only non-zero exit this driver produces.
        #
        # This is the CHECKED rungs' exit. R1 exits 134 (gcc, canary) or 139
        # (clang, smashed return address) on `adversarial-overflow` and 0 with a
        # wrong answer on `off1` and `nonul`; `check.py` records that in the
        # adversarial table rather than requiring it.
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
            want = self.strcat_fold(c["buf"], c["off"], c["len"])
            if want != c["result"]:
                problems.append(
                    f"simulated result {c['result']} != strcat_fold() {want} "
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
