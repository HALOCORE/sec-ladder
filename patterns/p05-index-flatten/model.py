#!/usr/bin/env python3
"""p05-index-flatten: the independent reference model the gate checks against.

The API is documented at the top of `patterns/p01-array-sum/model.py`; this file
notes only where p05 differs.

    bindings      buf/off/len/buf_len/result, the read-only shape p16 and p17
                  use. p05's kernel writes nothing.
    work_per_call the WINDOW, in bytes -- i.e. `stride`, constant across every
                  call on a given input. Argued below. Unlike p17's, and like
                  p16's, this is a strict OVER-estimate: the kernel folds
                  `nrow * ncol == stride - 4` bytes, so the derived floor errs
                  strict, by exactly the four header bytes.
    sanitizer     derived, not tabulated: an input is "fires" exactly when the
                  simulated run contains a call in which R1 -- the rung that
                  omits `nrow * ncol > avail` -- would index past the end of
                  the blob, i.e. when `off + 4 + nrow*ncol > n_blob` for a
                  window the driver actually selects.

Two independent implementations, as p01, p02, p16 and p17 do:

  * the **simulation** parses each window once and folds its matrix with a
    per-row `sum()` over a slice, caching one result per window -- which is
    what makes 25 000 driver iterations tractable;
  * the **helper** `grid_fold` -- the one the derived `ensures` is evaluated
    against -- is a recursive walk mirroring the *Verus* spec functions
    `row_fold` / `grid_walk` in ../verus.rs: element at a time, index computed
    as `4 + i*ncol + j` with no slicing and no cache.

`selfcheck()` runs them against each other; a disagreement is reported there
rather than being silently absorbed into a green line.

**Both implementations model the CHECKED kernel**, i.e. R1h and R2-R5. R1 is the
rung with the bug and is expected to disagree on `adversarial-dims`; the gate
records that disagreement in its behaviour table rather than requiring it to
vanish (`.memory/02-bench-rules.md`).

One arithmetic note that is easy to get wrong and is load-bearing for
`adversarial-ovf`: **`row` is a u32 accumulator and `acc` is u64**. The row sum
wraps mod 2^32 and is then widened; `acc` wraps mod 2^64. Python has neither, so
every fold here masks explicitly. See ../spec.md for why the row accumulator is
32 bits -- it is the one deviation from TASK_013's pseudocode and NOTES.md 1 has
the measurement that forced it.
"""

import itertools
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "common"))
import slb  # noqa: E402

MASK = (1 << 64) - 1
MASK32 = (1 << 32) - 1
HDR = 4


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
        self._win = []          # per window: (result, r1_would_overrun)
        if not self.truncated:
            self._run()

    # -- the window table (computed once) ----------------------------------
    def _window(self, off):
        """(result, R1_would_read_past_the_blob) for the window at `off`.

        Implementation 1 of 2. Slices each row out of the blob and sums it with
        Python's `sum`, which is a different code path from the recursive
        `grid_fold` below in every respect that matters.

        The second element records whether the rung with **no** size check --
        R1 -- would index past the end of the whole blob. Note it is about the
        blob, not about the window: an overrun from a middle window stays
        inside the allocation and is a silent wrong answer rather than a memory
        error, which is exactly why `inputs/gen.py` builds every adversarial
        input with a single window."""
        ln = self.stride
        if ln < HDR:
            return 0, False
        nrow = self.buf[off] + 256 * self.buf[off + 1]
        ncol = self.buf[off + 2] + 256 * self.buf[off + 3]
        if nrow == 0 or ncol == 0:
            return 0, False
        avail = ln - HDR
        # R1 omits exactly the next line, and only it.
        over = off + HDR + nrow * ncol > self.n_blob
        if nrow * ncol > avail:
            return 0, over
        acc = 0
        base = off + HDR
        for i in range(nrow):
            row = sum(self.buf[base + i * ncol: base + i * ncol + ncol]) & MASK32
            acc = (acc * 31 + row) & MASK
        return (acc * 31 + nrow * ncol) & MASK, over

    # -- simulation --------------------------------------------------------
    def _run(self):
        acc = 0
        if HDR <= self.stride <= self.n_blob:
            self.entered = True
            self.nwin = self.n_blob // self.stride
            self._win = [self._window(k * self.stride) for k in range(self.nwin)]
            for _ in range(self.n_iters):
                k = (acc * self.nwin) >> 64
                r, over = self._win[k]
                if over:
                    self.any_overrun = True
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
    # (../verus.rs `row_fold` / `grid_walk`): recursive over the rows,
    # element-at-a-time over each row, index spelled `4 + i*ncol + j` with no
    # slicing and no per-window cache.
    def _nrow_at(self, buf, off):
        """`nrow_at` in ../verus.rs."""
        return buf[off] + 256 * buf[off + 1]

    def _ncol_at(self, buf, off):
        """`ncol_at` in ../verus.rs."""
        return buf[off + 2] + 256 * buf[off + 3]

    def _row_fold(self, buf, off, ncol, i, j, acc):
        """`row_fold` in ../verus.rs: the u32 row accumulator over row `i`,
        columns `0 .. j`. Indices are `off + 4 + i*ncol + c` -- the flattened
        2-D index this pattern is named after, written out rather than
        strength-reduced to a moving pointer."""
        for c in range(j):
            acc = (acc + buf[off + HDR + i * ncol + c]) & MASK32
        return acc

    def _grid_walk(self, buf, off, nrow, ncol, i, acc):
        """`grid_walk` in ../verus.rs, returning the u64 accumulator."""
        if i >= nrow:
            return acc
        row = self._row_fold(buf, off, ncol, i, ncol, 0)
        return self._grid_walk(buf, off, nrow, ncol, i + 1,
                               (acc * 31 + row) & MASK)

    def grid_fold(self, buf, off, ln):
        """`grid_fold` in ../verus.rs: what the kernel must return."""
        if ln < HDR:
            return 0
        nrow = self._nrow_at(buf, off)
        ncol = self._ncol_at(buf, off)
        if nrow == 0 or ncol == 0:
            return 0
        if nrow * ncol > ln - HDR:
            return 0
        acc = self._grid_walk(buf, off, nrow, ncol, 0, 0)
        return (acc * 31 + nrow * ncol) & MASK

    @property
    def helpers(self):
        return {"grid_fold": self.grid_fold}

    # -- what the kernel must do, per call ---------------------------------
    @property
    def work_per_call(self):
        """The window, in bytes -- `stride` -- from the file alone.

        **Why the window, and which way the estimate errs.** `check.py` needs
        one scalar per input and hard-fails on `work <= 0`. The bytes the kernel
        actually folds are `nrow * ncol`, which is attacker data; the window is
        the unit that does not move, being fixed by the payload header and
        identical on every call of a given input. On the two measured inputs the
        matrix tiles the window exactly (19 x 26 = 494 = 498 - 4 and
        65 x 61 = 3965 = 3969 - 4), so `work_per_call = stride` **over**-states
        the bytes folded by exactly the four header bytes and the derived floor
        errs strict. That is p16's direction. p17's went the other way and its
        `model.py` says so; `.memory/02-bench-rules.md` asks which way it errs,
        so: strict, by 0.8% on `small` and 0.1% on `large`.

        No `min_ir_per_work` is declared, so the harness default of 0.25 Ir per
        byte applies unchanged -- **and on p05 that argument has to be made
        differently from p16's and p17's, because p05's inner loop is the first
        in this project that vectorises.** p16 and p17 could say "the fold is a
        serial Horner chain, so there is no vector form that could undercut the
        default". Here there is one, and it is what shipped. The default is
        nonetheless sound at the flags this project builds with (`-O3`, no
        `-march`, i.e. baseline x86-64 SSE2), measured at TASK_013:

            rustc / clang   VW 4 x interleave 2 = 8 bytes per iteration in
                            12 instructions  ->  1.50 Ir/byte
            gcc             16 bytes per iteration in 17 instructions
                            ->  1.06 Ir/byte

        i.e. 4.2x above the floor at the worst, before the per-row Horner step
        and the scalar epilogue are counted. An AVX-512 `vpsadbw` form would do
        64 bytes in ~4 instructions (0.0625 Ir/byte, p02's declared floor) and
        would need a declaration -- but this project passes no `-march`, and
        `harness/build.py` is what decides that, so a rung cannot reach it.
        NOTES.md 4 has the measured margins."""
        return self.stride if self.entered else 0

    # -- sanitizer expectation ---------------------------------------------
    @property
    def sanitizer_expect(self):
        """Derived from the simulated run, never tabulated per file.

        R1 omits `nrow * ncol > avail`, so it folds `nrow * ncol` bytes starting
        at `off + 4` whatever the header says. That is a memory error exactly
        when it runs past the **blob**, `off + 4 + nrow*ncol > n_blob` -- and
        note it is the blob and not the window, because an overrun from a middle
        window lands in the next window and is a silent wrong answer rather than
        something a sanitizer can see. `inputs/gen.py` builds every adversarial
        input with a single window so the two coincide.

        Note that this derivation returns "fires" for **two** inputs, and that
        is not an accident of one of them. `adversarial-dims` (8 x 64 = 512
        against `avail` 64) is the pattern's own overrun. `adversarial-ovf`
        (65535 x 65535) is aimed at the *width the check is written in* rather
        than at R1 -- but R1 has no check of any width, so it overruns there
        too, and the property is computed rather than tabulated so it says so.
        What distinguishes the two inputs is the *hardened* cells: `dims` is
        rejected by every 64-bit check and `ovf` is rejected by every 64-bit
        check **and waved through by a 32-bit signed one**, which is the
        variant NOTES.md 6 builds."""
        return "fires" if self.any_overrun else "clean"

    # -- what a conforming driver does -------------------------------------
    @property
    def expected_exit(self):
        # p05's payload allocates nothing from an attacker-controlled size --
        # there is no `cap` word and no `slb_zeroed` -- so p02's exit 7 has no
        # analogue here, exactly as for p16 and p17. `slb_load` rejecting a
        # short file is the only non-zero exit this pattern's driver produces.
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
        """Row-slice-and-`sum` simulation vs the recursive element-at-a-time
        walk that mirrors the Verus spec functions."""
        problems = []
        for c in self.sample_calls(8):
            want = self.grid_fold(c["buf"], c["off"], c["len"])
            if want != c["result"]:
                problems.append(
                    f"simulated result {c['result']} != grid_fold() {want} at "
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
