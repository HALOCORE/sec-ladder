#!/usr/bin/env python3
"""p09-bitset: the independent reference model the gate checks against.

The API is documented at the top of `patterns/p01-array-sum/model.py`; this file
notes only where p09 differs.

    bindings      buf/off/len/buf_len/result, the read-only shape p16, p17, p05,
                  p07, p11 and p03 use.
    work_per_call **bytes of the window** -- `stride`. See the property's
                  docstring for the direction of the error, which is LOOSE here
                  and was STRICT on p03.
    work_unit     "byte"; `work_unit_bits` 8.
    sanitizer     derived, not tabulated: an input is "fires" exactly when the
                  simulated run contains a call in which R1 -- the rung with no
                  `q < nbits` guard -- would read a byte outside the blob. That
                  is a heap read past a `malloc`'d region and ASan reports
                  `heap-buffer-overflow`. **It is NOT the same predicate as "R1
                  disagrees with the checked rungs"**, and p09 is the first
                  pattern here that ships an input where the two differ:
                  `adversarial-edge` makes R1 read words 1 and 2 of a 2-word
                  bitset, both of which are inside the same allocation because
                  the query array follows the word array. Every rung is silent
                  and R1's answer is wrong.

Two independent implementations, as p01, p02, p16, p17, p05, p07, p11 and p03 do:

  * the **simulation** `_window` decodes with `int.from_bytes`, keeps the words
    in a Python list, tests a bit with `(w >> b) & 1` and counts population with
    `bin(w).count("1")` -- none of which the helper below does;
  * the **helper** `bitset_fold` -- the one the derived `ensures` is evaluated
    against -- mirrors the Verus spec function in ../verus.rs: `_u32_at` and
    `_u64_at` written out as `b0 + 256*b1 + ...`, `word_of`/`bit_of` written as
    `q // 64` and `q % 64` (**division, matching the specification and not the
    code, which shifts**), and `_popcnt` as the recursive digit sum
    `x % 2 + popcnt(x // 2)`.

    It is **iterative where the Verus functions are recursive**, and that is a
    deliberate deviation rather than an oversight: `qrun` recurses once per query
    and p09's windows hold up to 830 of them, which would exceed CPython's
    default recursion limit on a bigger window. The two are otherwise
    transliterations.

`selfcheck()` runs them against each other; a disagreement is reported there
rather than being silently absorbed into a green line.

**Both implementations model the CHECKED kernel**, i.e. R1h and R2-R5. R1 is the
rung with the bug and is expected to disagree on `adversarial-oob` and
`adversarial-edge`; the gate records that disagreement in its behaviour table
rather than requiring it to vanish (`.memory/02-bench-rules.md`).

**Neither implementation trusts `nbits` or `nq`**, and neither does ../verus.rs.
What bounds the walk is the length check `8*nwords + 4*nq > avail`, which is in
*every* rung including R1 -- `adversarial-count.bin` is the row that shows it.
The **only** thing R1 omits is `q < nbits`.

Two arithmetic notes that are easy to get wrong and are load-bearing:

  * the result is `(acc*31 + nbits)*31 + nq`, so a rung that probed a different
    number of queries, or read the header differently, cannot produce the same
    checksum even if it folded the same words. Python has no wrap, so every step
    masks explicitly.
  * a query with `q >= nbits` is a **no-op** in the checked semantics -- `acc`
    and `hits` are both unchanged -- and is *not* an error and *not* a
    rejection.
"""

import itertools
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "common"))
import slb  # noqa: E402

MASK = (1 << 64) - 1
HDR = 8                   # nbits:u32 + nq:u32


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
        self.any_oob = False
        self.nwin = 0
        self._work = 0
        self._win = []      # per window: (result, r1_reads_outside_blob, xguard)
        if not self.truncated:
            self._run()

    # -- the window table (computed once) ----------------------------------
    def _window(self, off):
        """(result, R1_reads_outside_the_blob, guarded_queries).

        Implementation 1 of 2. Decodes with `int.from_bytes`, keeps the words in
        a list, tests bits with `(w >> b) & 1` and counts population with
        `bin(w).count("1")` -- none of which `bitset_fold` below does.

        The second element records whether the rung with **no** range guard --
        R1 -- would read a byte outside the blob. That is the ASan predicate and
        it is deliberately NOT "R1 disagrees": `adversarial-edge` makes R1 read
        the word one past the bitset, which is inside the same allocation
        because the query array follows the words. See the module docstring."""
        ln = self.stride
        if ln < HDR:
            return 0, False, 0
        buf = self.buf
        nbits = int.from_bytes(buf[off:off + 4], "little")
        nq = int.from_bytes(buf[off + 4:off + 8], "little")
        if nbits == 0 or nq == 0:
            return 0, False, 0
        nwords = (nbits + 63) >> 6
        if 8 * nwords + 4 * nq > ln - HDR:
            return 0, False, 0
        ws = off + HDR
        qs = ws + 8 * nwords
        wl = [int.from_bytes(buf[ws + 8 * i:ws + 8 * i + 8], "little")
              for i in range(nwords)]
        acc = 0
        hits = 0
        xguard = 0
        oob = False
        for k in range(nq):
            q = int.from_bytes(buf[qs + 4 * k:qs + 4 * k + 4], "little")
            if q < nbits:
                xguard += 1
                w = wl[q >> 6]
                if (w >> (q & 63)) & 1:
                    hits += 1
                acc = (acc * 31 + w) & MASK
            else:
                # what R1 would do, and whether it leaves the allocation
                if ws + 8 * (q >> 6) + 8 > self.n_blob:
                    oob = True
        acc = (acc * 31 + hits) & MASK
        for w in wl:
            acc = (acc * 31 + bin(w).count("1")) & MASK
        return ((acc * 31 + nbits) * 31 + nq) & MASK, oob, xguard

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
                r, oob, _xg = self._win[k]
                if oob:
                    self.any_oob = True
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
            r, _oob, _xg = self._win[k]
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
    # (../verus.rs), including the deliberate use of DIVISION where the code
    # shifts: no `int.from_bytes`, no `bin().count()`, no list of words, no
    # cache.
    def _u32_at(self, buf, p):
        """`u32_at` in ../verus.rs, written out with `+` and `*`."""
        return (buf[p] + 256 * buf[p + 1] + 65536 * buf[p + 2]
                + 16777216 * buf[p + 3])

    def _u64_at(self, buf, p):
        """`u64_at` in ../verus.rs, eight terms, written out."""
        return (buf[p] + 256 * buf[p + 1] + 65536 * buf[p + 2]
                + 16777216 * buf[p + 3] + 4294967296 * buf[p + 4]
                + 1099511627776 * buf[p + 5] + 281474976710656 * buf[p + 6]
                + 72057594037927936 * buf[p + 7])

    @staticmethod
    def _nwords_of(nbits):
        """`nwords_of` in ../verus.rs: `(nbits + 63) / 64`. **Division.** The
        rungs write `(nbits + 63) >> 6`, and that the two agree is a proof
        obligation there rather than an assumption here."""
        return (nbits + 63) // 64

    @staticmethod
    def _word_of(q):
        """`word_of` in ../verus.rs: `q / 64`. The rungs write `q >> 6`."""
        return q // 64

    @staticmethod
    def _bit_of(q):
        """`bit_of` in ../verus.rs: `q % 64`. The rungs write `q & 63`."""
        return q % 64

    @staticmethod
    def _popcnt(x):
        """`popcnt` in ../verus.rs: the recursive base-2 digit sum, written
        iteratively for the reason the module docstring gives. Deliberately not
        `bin(x).count("1")`, which is the simulation's."""
        c = 0
        while x != 0:
            c += x % 2
            x = x // 2
        return c

    def bitset_fold(self, buf, off, ln):
        """`bitset_fold` in ../verus.rs: what the kernel must return."""
        if ln < HDR:
            return 0
        nbits = self._u32_at(buf, off)
        nq = self._u32_at(buf, off + 4)
        if nbits == 0 or nq == 0:
            return 0
        nwords = self._nwords_of(nbits)
        if 8 * nwords + 4 * nq > ln - HDR:
            return 0
        ws = off + HDR
        qs = ws + 8 * nwords
        acc = 0
        hits = 0
        k = 0
        while k < nq:
            q = self._u32_at(buf, qs + 4 * k)
            if q < nbits:
                w = self._u64_at(buf, ws + 8 * self._word_of(q))
                if w & (1 << self._bit_of(q)):
                    hits = (hits + 1) & MASK
                acc = (acc * 31 + w) & MASK
            k = k + 1
        acc = (acc * 31 + hits) & MASK
        i = 0
        while i < nwords:
            acc = (acc * 31
                   + self._popcnt(self._u64_at(buf, ws + 8 * i))) & MASK
            i = i + 1
        return ((acc * 31 + nbits) * 31 + nq) & MASK

    @property
    def helpers(self):
        return {"bitset_fold": self.bitset_fold}

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

        **Which way this estimate errs: LOOSE on every input this pattern
        ships** (`.memory/02-bench-rules.md` asks, so: say it, and say it in
        both directions, because p16 errs strict, p17 loose, p05 strict and p03
        strict -- four patterns, and now a fifth, and they do not agree).

          * *under*-count, and it is the only term that can go that way: a
            guarded query **re-reads** the eight bytes of its word, which the
            popcount pass has already visited. So a window with `xguard` guarded
            queries makes `stride + 8*xguard` byte-visits where `stride` counts
            each byte once. On `small` that is `1108 + 8*239 = 3020`, i.e. 2.73x
            the declared figure; on `large` `4328 + 8*830 = 10968`, 2.53x.
          * *over*-count: **none**. Every byte of a well-formed window is read
            at least once -- the 8 header bytes as two u32s, every word byte by
            the popcount pass, every query byte by the query loop.

        So the derived floor is one the kernel must clear with room to spare,
        which is the only direction that matters: it can never let a collapsed
        kernel through. The measured margin is in ../NOTES.md 8b.

        No `min_ir_per_work` is declared, so the harness default of 0.25 Ir per
        byte applies unchanged. The argument for it here is easy: p09's query
        loop is a data-dependent branch on an attacker word followed by a serial
        dependence through `acc`, and its inner work is a byte-at-a-time
        little-endian assembly, so there is no vector form at any `-march`.
        `.memory/02-bench-rules.md` records that p09 was the pattern
        `MIN_DECLARABLE_IR_PER_WORK` was fixed *for*, on the assumption it would
        be denominated in **bits** and want an AVX-512 `vpopcntq` floor of
        0.0059 Ir/bit. It is not: p09 is denominated in window bytes like p16,
        p05, p11 and p03, it declares no `min_ir_per_work`, and the hatch that
        was built for it is unused. Say so rather than leaving `.memory`'s
        prediction standing."""
        return self._work if self.entered else 0

    # -- sanitizer expectation ---------------------------------------------
    @property
    def sanitizer_expect(self):
        """Derived from the simulated run, never tabulated per file.

        R1 has no `q < nbits` guard, so for a query with `q >= nbits` it reads
        `words + 8*(q >> 6)`. That is a memory error exactly when the read
        leaves the blob, which is what `_window` computes.

        **This predicate is deliberately narrower than "R1 is wrong"**, and p09
        is the first pattern here where the two come apart on a shipped input:

          * `adversarial-oob` -- one query is 0x00FFFFFF, so `q >> 6` is 262143
            and the read is 2 MiB past a 208-byte allocation. ASan
            `heap-buffer-overflow`. **fires.**
          * `adversarial-edge` -- the queries are 99, 100, 127 and 128 against
            `nbits = 100`, `nwords = 2`. R1 reads words 1, 1, 1 and 2; word 2 is
            one past the bitset and **inside the same allocation**, because the
            query array follows it. R1's answer is wrong and every sanitiser is
            silent. **clean**, and that is the point of the row.
          * `adversarial-count` -- the length check is in R1 too, so every rung
            returns 0. **clean.** The control.
          * `small`, `large` -- 100% of queries are in range, so R1 and R1h agree
            (`inputs/gen.py` explains why they must). **clean.**"""
        return "fires" if self.any_oob else "clean"

    # -- what a conforming driver does -------------------------------------
    @property
    def expected_exit(self):
        # p09's payload allocates nothing from an attacker-controlled size --
        # there is no `cap` word and no `slb_zeroed` -- so p02's exit 7 has no
        # analogue here, exactly as for p16, p17, p05, p07, p11 and p03.
        return 5 if self.truncated else 0

    @property
    def expected_stdout(self):
        return "" if self.checksum is None else f"{self.checksum}\n"

    def describe(self):
        xg = self._win[0][2] if self._win and self._win[0] else 0
        return (f"n_iters={self.n_iters} stride={self.stride} "
                f"n_blob={self.n_blob} nwin={self.nwin} calls={self.n_calls} "
                f"work/call={self.work_per_call}B win0_xguard={xg} "
                f"san={self.sanitizer_expect} "
                f"truncated={self.truncated} expected={self.checksum}")

    def shape(self, off):
        """(nbits, nq, nwords, guarded_queries) for the window at `off` -- the
        regressors ../NOTES.md 4's laws are linear in. Exposed so the sweep
        scripts do not have to re-implement the guard or the ceiling."""
        buf = self.buf
        nbits = int.from_bytes(buf[off:off + 4], "little")
        nq = int.from_bytes(buf[off + 4:off + 8], "little")
        return nbits, nq, (nbits + 63) >> 6, self._window(off)[2]

    def selfcheck(self):
        """`int.from_bytes`/`bin().count` simulation vs the written-out walk
        that mirrors the Verus spec functions."""
        problems = []
        for c in self.sample_calls(8):
            want = self.bitset_fold(c["buf"], c["off"], c["len"])
            if want != c["result"]:
                problems.append(
                    f"simulated result {c['result']} != bitset_fold() {want} "
                    f"at off={c['off']}")
                break
        return problems


def build(path):
    return Model(path)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        m = build(p)
        print(f"{os.path.basename(p):30s} {m.describe()}  "
              f"exit={m.expected_exit} selfcheck={m.selfcheck()}")
