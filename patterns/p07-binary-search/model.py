#!/usr/bin/env python3
"""p07-binary-search: the independent reference model the gate checks against.

The API is documented at the top of `patterns/p01-array-sum/model.py`; this file
notes only where p07 differs.

    bindings      buf/off/len/buf_len/result, the read-only shape p16, p17 and
                  p05 use. p07's kernel writes nothing.
    work_per_call **PROBES, not bytes** -- `nq * ceil(log2(n+1))`, the number of
                  element comparisons the checked kernel can make on one call.
                  This is the first pattern in the project that cannot be
                  denominated in bytes; the argument is in the property's own
                  docstring and it is the reason p07 exists.
    work_unit     "probe"; `work_unit_bits` 32, one u32 element compared.
    sanitizer     derived, not tabulated: an input is "fires" exactly when the
                  simulated run contains a call in which R1 -- the rung that
                  omits `4*n + 4*nq > avail` -- would index past the end of the
                  blob, i.e. when `off + 8 + 4*n + 4*nq > n_blob` for a window
                  the driver actually selects.

Two independent implementations, as p01, p02, p16, p17 and p05 do:

  * the **simulation** decodes each window's element array once with
    `struct.unpack` into a list of Python ints and runs an iterative half-open
    search per query, caching one result per window -- which is what makes
    8000 driver iterations tractable;
  * the **helper** `search_fold` -- the one the derived `ensures` is evaluated
    against -- is a *recursive* walk mirroring the Verus spec functions
    `bsearch` / `query_walk` in ../verus.rs: one query at a time, one probe at a
    time, each u32 decoded byte-by-byte out of the raw blob at the written-out
    index `off + 8 + 4*mid`, with no `unpack`, no list and no cache.

`selfcheck()` runs them against each other; a disagreement is reported there
rather than being silently absorbed into a green line.

**Both implementations model the CHECKED kernel**, i.e. R1h and R2-R5. R1 is the
rung with the bug and is expected to disagree on `adversarial-count` and
`adversarial-width`; the gate records that disagreement in its behaviour table
rather than requiring it to vanish (`.memory/02-bench-rules.md`).

**Neither implementation assumes the elements are sorted**, and neither does
../verus.rs. The specification is *what the search returns*, not "the position
of the key", so `adversarial-unsorted.bin` is inside the verified domain and
every rung must agree with this file on it. That is what makes that input a
correctness row rather than a safety row.

Two arithmetic notes that are easy to get wrong and are load-bearing:

  * `found` is `u64::MAX` when the key is absent, and **`found + 1` is folded**,
    so an absent key folds as 0 and element 0 folds as 1. Python has no wrap, so
    the fold masks explicitly.
  * the length check is `4*n + 4*nq > avail` in **64 bits**. `n` and `nq` are
    u32 fields, so the left side reaches 34 359 738 360 and does not fit 32
    bits -- unlike p05, whose u16 dimensions keep `nrow*ncol` inside `uint32_t`.
    `adversarial-width.bin` is the input that separates the two widths and
    ../NOTES.md 6 builds the narrow cell.
"""

import itertools
import os
import struct
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "common"))
import slb  # noqa: E402

MASK = (1 << 64) - 1
NOT_FOUND = MASK          # u64::MAX
HDR = 8                   # n:u32 + nq:u32


def _ceil_log2_plus1(n):
    """Max iterations of a half-open binary search over `n` elements.

    `lo`/`hi` start `0`/`n` and the loop runs while `lo < hi`, halving
    `hi - lo` each step, so the trip count is `ceil(log2(n + 1))`: 1 at n = 1,
    2 at n = 2 and 3, 3 at n = 4..7, and so on. Exact, and computed from the
    file's own header rather than measured."""
    k, span = 0, 1
    while span < n + 1:
        span *= 2
        k += 1
    return k


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

        Implementation 1 of 2. Decodes the whole element array in one
        `struct.unpack` and runs an iterative half-open search per query, which
        is a different code path from the recursive byte-at-a-time
        `search_fold` below in every respect that matters.

        The second element records whether the rung with **no** length check --
        R1 -- would index past the end of the whole blob. Note it is about the
        blob, not about the window: an overrun from a middle window stays inside
        the allocation and is a silent wrong answer rather than a memory error,
        which is exactly why `inputs/gen.py` builds every adversarial input with
        a single window."""
        ln = self.stride
        if ln < HDR:
            return 0, False
        n = int.from_bytes(self.buf[off:off + 4], "little")
        nq = int.from_bytes(self.buf[off + 4:off + 8], "little")
        if n == 0 or nq == 0:
            return 0, False
        avail = ln - HDR
        # R1 omits exactly the next line, and only it. `over` is what R1 would
        # do without it: its highest index is the last query's last byte.
        over = off + HDR + 4 * n + 4 * nq > self.n_blob
        if 4 * n + 4 * nq > avail:
            return 0, over
        base = off + HDR
        elems = struct.unpack_from("<%dI" % n, self.buf, base)
        keys = struct.unpack_from("<%dI" % nq, self.buf, base + 4 * n)
        acc = 0
        for key in keys:
            lo, hi, found = 0, n, NOT_FOUND
            while lo < hi:
                mid = lo + (hi - lo) // 2
                v = elems[mid]
                if v == key:
                    found = mid
                    break
                if v < key:
                    lo = mid + 1
                else:
                    hi = mid
            acc = (acc * 31 + ((found + 1) & MASK)) & MASK
        return (acc * 31 + ((n * nq) & MASK)) & MASK, over

    # -- simulation --------------------------------------------------------
    def _run(self):
        acc = 0
        if HDR <= self.stride <= self.n_blob:
            self.entered = True
            self.nwin = self.n_blob // self.stride
            self._win = [self._window(k * self.stride) for k in range(self.nwin)]
            self._work = self._probes(0)
            for _ in range(self.n_iters):
                k = (acc * self.nwin) >> 64
                r, over = self._win[k]
                if over:
                    self.any_overrun = True
                acc = (acc * 31 + r) & MASK
            self.n_calls = self.n_iters
        self.checksum = acc

    def _probes(self, off):
        """`nq * ceil(log2(n+1))` for the window at `off`, or 0 if the checked
        kernel rejects it. Read straight out of the window header."""
        if self.stride < HDR:
            return 0
        n = int.from_bytes(self.buf[off:off + 4], "little")
        nq = int.from_bytes(self.buf[off + 4:off + 8], "little")
        if n == 0 or nq == 0 or 4 * n + 4 * nq > self.stride - HDR:
            return 0
        return nq * _ceil_log2_plus1(n)

    def iter_calls(self):
        """Replay the driver loop, yielding one binding per kernel call.

        Regenerated rather than stored: `small.bin` is 8000 calls. `buf` is the
        whole blob and is yielded by reference, so this costs nothing per call
        beyond the dict."""
        if not self.entered:
            return
        acc = 0
        for _ in range(self.n_iters):
            k = (acc * self.nwin) >> 64
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
    # (../verus.rs `bsearch` / `query_walk`): recursive over the queries and
    # over the search, one u32 decoded byte-by-byte per probe, index spelled
    # `off + 8 + 4*mid` with no unpack, no element list and no cache.
    def _u32_at(self, buf, p):
        """`u32_at` in ../verus.rs, written out with `+` and `*` exactly as the
        rungs write it -- not `int.from_bytes`, which is the simulation's."""
        return (buf[p] + 256 * buf[p + 1] + 65536 * buf[p + 2]
                + 16777216 * buf[p + 3])

    def _elem_at(self, buf, off, i):
        """`elem_at` in ../verus.rs."""
        return self._u32_at(buf, off + HDR + 4 * i)

    def _key_at(self, buf, off, n, q):
        """`key_at` in ../verus.rs."""
        return self._u32_at(buf, off + HDR + 4 * n + 4 * q)

    def _bsearch(self, buf, off, key, lo, hi):
        """`bsearch` in ../verus.rs: the half-open search, recursive, with the
        midpoint spelled `lo + (hi - lo) // 2` -- the overflow-safe form. It
        does NOT assume the elements are sorted; it returns what the program
        returns."""
        if hi <= lo:
            return NOT_FOUND
        mid = lo + (hi - lo) // 2
        v = self._elem_at(buf, off, mid)
        if v == key:
            return mid
        if v < key:
            return self._bsearch(buf, off, key, mid + 1, hi)
        return self._bsearch(buf, off, key, lo, mid)

    def _query_walk(self, buf, off, n, nq, q, acc):
        """`query_walk` in ../verus.rs, returning the u64 accumulator."""
        if q >= nq:
            return acc
        found = self._bsearch(buf, off, self._key_at(buf, off, n, q), 0, n)
        return self._query_walk(buf, off, n, nq, q + 1,
                                (acc * 31 + ((found + 1) & MASK)) & MASK)

    def search_fold(self, buf, off, ln):
        """`search_fold` in ../verus.rs: what the kernel must return."""
        if ln < HDR:
            return 0
        n = self._u32_at(buf, off)
        nq = self._u32_at(buf, off + 4)
        if n == 0 or nq == 0:
            return 0
        if 4 * n + 4 * nq > ln - HDR:
            return 0
        acc = self._query_walk(buf, off, n, nq, 0, 0)
        return (acc * 31 + ((n * nq) & MASK)) & MASK

    @property
    def helpers(self):
        return {"search_fold": self.search_fold}

    # -- what the kernel must do, per call ---------------------------------
    @property
    def work_unit(self):
        return "probe"

    @property
    def work_unit_bits(self):
        """One probe compares one u32 element against the key. 32 bits."""
        return 32

    @property
    def work_per_call(self):
        """`nq * ceil(log2(n+1))` probes, from the file alone.

        **p07 is the first pattern in this project that cannot be denominated
        in bytes, and that is the whole point of the pattern.** Every earlier
        kernel folds every byte of its window, so `work_per_call = stride` is
        both honest and roughly proportional to the work. Binary search reads
        `4 * ceil(log2 n)` bytes out of a `4*n`-byte array: on `large.bin`
        (`n = 262 135`, `nq = 92`) that is `92 * 18 = 1656` probes = 6624 bytes
        touched out of a 1 048 916-byte window, 0.63%. A byte-denominated unit
        would put the derived floor at `0.25 * 1048916 = 262 229` Ir/call
        against a kernel that legitimately executes ~21 400 (kernel-exclusive
        `Ir`), and the gate would fail a perfectly healthy pattern --
        the same shape as `MIN_DECLARABLE_IR_PER_WORK` forbidding p09's
        bit-denominated model (`.memory/02-bench-rules.md`). The unit has to be
        the thing the kernel actually does once per unit of input it actually
        looks at, and here that is the **probe**.

        **Which way this estimate errs: STRICT, and by a bounded factor.**
        `.memory/02-bench-rules.md` asks, so: `ceil(log2(n+1))` is the *maximum*
        trip count of the half-open search, and a query that hits exits early,
        so the kernel makes at most this many probes and typically fewer. On the
        shipped 50/50 hit/miss workload the measured ratio is in ../NOTES.md 4.
        p16 and p05 err strict too (by their header bytes); p17 errs loose. This
        one errs strict by up to a factor of ~2 in the limit and ~1.15 in
        practice, which only makes the floor easier to clear -- it can never
        make the gate pass a collapsed kernel it should have failed.

        No `min_ir_per_work` is declared, so the harness default of 0.25 Ir per
        **probe** applies unchanged, and the argument for it is different from
        every earlier pattern's and much easier: a probe must load 4 bytes,
        assemble them, compare, and update a bound -- there is no vector form of
        a *dependent* search step, because probe `i+1`'s address is not known
        until probe `i`'s comparison retires. The cheapest imaginable correct
        implementation is therefore several instructions per probe, not a
        fraction of one, and 0.25 is two orders of magnitude below it. Measured
        margins are in ../NOTES.md 4."""
        return self._work if self.entered else 0

    # -- sanitizer expectation ---------------------------------------------
    @property
    def sanitizer_expect(self):
        """Derived from the simulated run, never tabulated per file.

        R1 omits `4*n + 4*nq > avail`, so it searches `n` declared elements and
        reads `nq` declared queries whatever the window holds. Its highest index
        is the last query's last byte, `off + 8 + 4*n + 4*nq - 1`, so it is a
        memory error exactly when `off + 8 + 4*n + 4*nq > n_blob` -- and note it
        is the blob and not the window, because an overrun from a middle window
        lands in the next window and is a silent wrong answer rather than
        something a sanitizer can see. `inputs/gen.py` builds every adversarial
        input with a single window so the two coincide.

        This returns "fires" for **two** inputs and that is not an accident of
        one of them. `adversarial-count` (n = 4096 declared, 16 present) is the
        pattern's own overrun and lands ~16 KiB out. `adversarial-width`
        (n = 2^30) is aimed at the *width the length check is written in* rather
        than at R1 -- every 64-bit check rejects it and a 32-bit unsigned one
        waves it through -- but R1 has no check of any width, so it overruns
        there too, by 4 GiB, and the property is computed rather than tabulated
        so it says so. What distinguishes the two inputs is the *hardened*
        cells: `count` is rejected by every check of every width and `width` is
        rejected only by the 64-bit ones, which is the variant ../NOTES.md 6
        builds."""
        return "fires" if self.any_overrun else "clean"

    # -- what a conforming driver does -------------------------------------
    @property
    def expected_exit(self):
        # p07's payload allocates nothing from an attacker-controlled size --
        # there is no `cap` word and no `slb_zeroed` -- so p02's exit 7 has no
        # analogue here, exactly as for p16, p17 and p05. `slb_load` rejecting a
        # short file is the only non-zero exit this pattern's driver produces.
        return 5 if self.truncated else 0

    @property
    def expected_stdout(self):
        return "" if self.checksum is None else f"{self.checksum}\n"

    def describe(self):
        return (f"n_iters={self.n_iters} stride={self.stride} "
                f"n_blob={self.n_blob} nwin={self.nwin} calls={self.n_calls} "
                f"work/call={self.work_per_call}probe "
                f"san={self.sanitizer_expect} "
                f"truncated={self.truncated} expected={self.checksum}")

    def selfcheck(self):
        """`struct.unpack` + iterative search simulation vs the recursive
        byte-at-a-time walk that mirrors the Verus spec functions."""
        problems = []
        for c in self.sample_calls(8):
            want = self.search_fold(c["buf"], c["off"], c["len"])
            if want != c["result"]:
                problems.append(
                    f"simulated result {c['result']} != search_fold() {want} at "
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
