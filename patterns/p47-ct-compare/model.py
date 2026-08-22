#!/usr/bin/env python3
"""p47-ct-compare: the independent reference model the gate checks against.

The API is documented at the top of `patterns/p01-array-sum/model.py`; this
file notes only where p47 differs.

    bindings      buf/off/len/buf_len/result -- the READ-ONLY shape p03, p06,
                  p11, p12, p14, p16, p17, p05, p07, p10 and p27 use. p47's
                  kernel writes nothing and allocates nothing.
    work_per_call **bytes of the window** -- `stride`.
    work_unit     "byte"; `work_unit_bits` 8.
    sanitizer     **"clean" on every input, always, and that is the pattern.**

**p47 IS THE FIRST PATTERN HERE WHOSE R1 IS MEMORY-SAFE.** Every other pattern's
`c/kernel.c` gets a *wrong answer* or reads out of bounds on some input, and
`harness/check.py` can see it -- stage 2 as a checksum disagreement, stage 7 as
an ASan report. p47's R1 gets the *right answer on every input this benchmark
will ever run*, is ASan- and UBSan-clean, is Miri-clean, and satisfies the
`ensures` that R5 proves. Its bug is that the number of instructions it
executes is a function of a secret. **No oracle in this file can see that, and
no oracle in `harness/check.py` can either.** That is p47's whole result and it
is why this docstring says so rather than leaving it to be inferred.

Two independent implementations, as every earlier pattern does:

  * the **simulation** decides each comparison with Python's own
    `bytes.__eq__` on two slices -- which is R2's `a == b`, i.e. the LEAKING
    spelling, and it early-exits inside CPython exactly as `bcmp` does;
  * the **helper** `tag_fold` -- the one the derived `ensures` is evaluated
    against -- mirrors the Verus spec function in ../verus.rs and decides each
    comparison by the CONSTANT-TIME or-accumulate, byte by byte, with no early
    exit anywhere.

    So the two implementations disagree about *how long they take* and agree
    about *what they return*, on every input. That is not a decorative
    difference here: it is the pattern's subject, stated in the one place a
    reader is guaranteed to look at both.

`selfcheck()` runs them against each other.
"""

import itertools
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "common"))
import slb  # noqa: E402

MASK = (1 << 64) - 1
HDR = 8                   # ntag:u32, tlen:u32
MATCH = 7                 # must equal every rung's MATCH
MISS = 251                # must equal every rung's MISS


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
        self._win = []          # per window: (result, [k per comparison])
        self._cmp = []          # per window: byte comparisons the kernel does
        if not self.truncated:
            self._run()

    # -- the window table (computed once) ----------------------------------
    def _window(self, off):
        """(result, first-mismatch position per comparison) for the window.

        Implementation 1 of 2, and it is the LEAKING one on purpose: the
        verdict comes out of Python's `bytes.__eq__`, which is `memcmp` under
        the hood and stops at the first differing byte -- R1's and R2's
        spelling. `tag_fold` below is the constant-time one.

        The second element is the list of `k` values (the first-mismatch
        position of each comparison, `None` when the two tags are equal). It
        is what the leaking rungs' instruction count is a function of, so the
        model computes it and `describe()` reports it: p47's harm is not
        visible in the checksum and has to be visible SOMEWHERE."""
        ln = self.stride
        if ln < HDR:
            return 0, []
        buf = self.buf
        ntag = int.from_bytes(buf[off:off + 4], "little")
        tlen = int.from_bytes(buf[off + 4:off + 8], "little")
        if ntag == 0 or tlen == 0:
            return 0, []
        acc, p, o, ks = 0, HDR, 0, []
        while o < ntag and ln - p >= 2 * tlen:
            a = buf[off + p:off + p + tlen]
            b = buf[off + p + tlen:off + p + 2 * tlen]
            eq = a == b                       # THE LEAKING SPELLING
            ks.append(None if eq else next(i for i in range(tlen)
                                           if a[i] != b[i]))
            acc = (acc * 31 + (MATCH if eq else MISS)) & MASK
            p += 2 * tlen
            o += 1
        return (acc * 31 + o) & MASK, ks

    def _ncmp(self, off):
        """Byte comparisons the CHECKED kernel performs in this window.

        `ncmp * tlen`, where `ncmp` is how many of the declared `ntag`
        comparisons the window guard actually admits. Derived from the file
        alone, by the same walk the kernel performs -- no rung is asked."""
        ln = self.stride
        if ln < HDR:
            return 0
        buf = self.buf
        ntag = int.from_bytes(buf[off:off + 4], "little")
        tlen = int.from_bytes(buf[off + 4:off + 8], "little")
        if ntag == 0 or tlen == 0:
            return 0
        p, o = HDR, 0
        while o < ntag and ln - p >= 2 * tlen:
            p += 2 * tlen
            o += 1
        return o * tlen

    # -- simulation --------------------------------------------------------
    def _run(self):
        acc = 0
        if HDR <= self.stride <= self.n_blob:
            self.entered = True
            self.nwin = self.n_blob // self.stride
            self._win = [None] * self.nwin
            # `work_per_call` is the MINIMUM over every window of the byte
            # comparisons the checked kernel performs there -- see the
            # property's docstring for why the minimum and not window 0's.
            self._cmp = [self._ncmp(w * self.stride) for w in range(self.nwin)]
            self._work = min(self._cmp)
            for _ in range(self.n_iters):
                k = (acc * self.nwin) >> 64
                if self._win[k] is None:
                    self._win[k] = self._window(k * self.stride)
                r, _ks = self._win[k]
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
            r, _ks = self._win[k]
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
    # This is what the derived `ensures` is evaluated against, so it must not
    # be the simulation in disguise. It mirrors the *Verus* spec functions in
    # ../verus.rs and decides each comparison the CONSTANT-TIME way: an
    # or-accumulate over every byte, with no early exit and no `==` on a
    # slice anywhere.
    def _u32_at(self, buf, p):
        """`u32_at` in ../verus.rs, written out with `+` and `*` exactly as
        the rungs write it -- not `int.from_bytes`, which is the
        simulation's."""
        return (buf[p] + 256 * buf[p + 1] + 65536 * buf[p + 2]
                + 16777216 * buf[p + 3])

    def _xacc(self, buf, base, tlen):
        """`xacc` in ../verus.rs: the or-accumulate of the byte-wise xor.

        Iterative where the Verus function is recursive, for p11's, p14's and
        p27's reason: `xacc` recurses once per byte and a tag may be longer
        than CPython's recursion limit."""
        d = 0
        for i in range(tlen):
            d |= buf[base + i] ^ buf[base + tlen + i]
        return d

    def _twalk(self, buf, off, ln, tlen, o, ntag, p, acc):
        """`twalk` in ../verus.rs. Iterative, same reason."""
        while o < ntag and ln - p >= 2 * tlen:
            d = self._xacc(buf, off + p, tlen)
            acc = (acc * 31 + (MATCH if d == 0 else MISS)) & MASK
            p += 2 * tlen
            o += 1
        return (acc * 31 + o) & MASK

    def tag_fold(self, buf, off, ln):
        """`tag_fold` in ../verus.rs: what the kernel must return."""
        if ln < HDR:
            return 0
        ntag = self._u32_at(buf, off)
        tlen = self._u32_at(buf, off + 4)
        if ntag == 0 or tlen == 0:
            return 0
        return self._twalk(buf, off, ln, tlen, 0, ntag, HDR, 0)

    @property
    def helpers(self):
        return {"tag_fold": self.tag_fold}

    # -- what the kernel must do, per call ---------------------------------
    @property
    def work_unit(self):
        return "byte comparison"

    @property
    def work_unit_bits(self):
        """One unit is one byte of one tag tested against its counterpart --
        two window bytes read, one xor. 8 bits of secret."""
        return 8

    @property
    def work_per_call(self):
        """`ncmp * tlen` -- the byte comparisons the CHECKED kernel performs,
        minimised over the windows of the blob, from the file alone.

        ⚠ **NOT `stride`, and the reason is a measurement rather than a
        preference.** Every other pattern here denominates in window bytes.
        p47 cannot: **each unit of its work consumes TWO window bytes** (a
        secret byte and a candidate byte) and produces one xor, so a window
        byte is half a unit by construction, and the vectorised rungs then land
        at 0.21-0.24 Ir per window byte -- *under* the harness's 0.25 default,
        on kernels that are demonstrably doing the whole job. Measured on the
        first gate run: `unsafe -O3 isolated` read `d(Ir)/d(work) = 0.206`
        against 434 -> 606 Ir. Denominated in byte comparisons the same two
        points give **0.413**, and every one of the sixteen O3 cells clears
        0.25 with margin. `.memory/02-bench-rules.md`'s own warning applies --
        *a floor that forbids the fastest correct implementation is not a
        floor* -- and the repair it points at is the denominator, not a
        declared `min_ir_per_work`. No `min_ir_per_work` is declared here.

        **Which way this estimate errs: STRICT, in three independent ways.**

          * The **minimum** over windows, not window 0's and not the mean. On
            a length-heterogeneous blob (`degenerate.bin`, `sweep-h*`) the
            driver may visit a window that does more; it can never visit one
            that does less.
          * It counts the 8 header bytes, the `2*tlen`-per-comparison guard
            arithmetic, the verdict fold and the Horner chain as **zero**.
          * It ignores window padding entirely.

        ⚠ **And there is one direction in which it is NOT strict, which has to
        be said rather than hidden: the leaking rungs do not perform this much
        work.** That is the bug. `c-gcc`, `c-clang` and `safe_naive` stop at
        the first differing 32-byte block, so on a blob whose comparisons all
        mismatch at byte 0 they touch 32 bytes per comparison however long the
        tag is, and their Ir per declared unit falls as `1/tlen`. Both
        `collapse.probe_inputs` are chosen so that this cannot fire: `small`
        has `tlen = 24 < 32`, so even `bcmp` reads the whole tag, and `large`
        has two of its eight comparisons EQUAL, which forces a full scan of
        those two in every rung. `sweep-t384` is the extreme case and it is a
        `sweep-*` blob, which `check.py` and `measure.py` both drop.

        What the floor still catches is the failure it exists to catch -- a
        kernel the optimiser collapsed to nothing. ../NOTES.md 3 has the
        per-cell margins."""
        return self._work if self.entered else 0

    # -- sanitizer expectation ---------------------------------------------
    @property
    def sanitizer_expect(self):
        """**"clean", on every input, unconditionally -- and that is the
        result, not a gap.**

        p47's R1 is memory-safe. It reads only inside the window the guard
        `len - p >= 2*tlen` has already proved is present, it writes nothing,
        it allocates nothing, and it returns the same value as every other
        rung on every input. ASan, UBSan, Miri and the `ensures` R5 proves are
        all silent about the difference between `c/kernel.c` and
        `c/kernel_hardened.c`, because that difference is not in the value
        domain at all -- it is in the trace.

        `.memory/02-bench-rules.md` calls a hard-coded per-file table a smell;
        this is the other extreme and it is honest: there is nothing to
        tabulate."""
        return "clean"

    # -- what a conforming driver does -------------------------------------
    @property
    def expected_exit(self):
        # p47's payload allocates nothing from an attacker-controlled size --
        # there is no `cap` word and no `slb_zeroed` -- so p02's exit 7 has no
        # analogue. `slb_load` rejecting a short file is the only non-zero
        # exit this driver produces.
        return 5 if self.truncated else 0

    @property
    def expected_stdout(self):
        return "" if self.checksum is None else f"{self.checksum}\n"

    def describe(self):
        ks = self._win[0][1] if self._win and self._win[0] else []
        return (f"n_iters={self.n_iters} stride={self.stride} "
                f"n_blob={self.n_blob} nwin={self.nwin} calls={self.n_calls} "
                f"work/call={self.work_per_call}cmp "
                f"k(win0)={ks[:8]} "
                f"san={self.sanitizer_expect} "
                f"truncated={self.truncated} expected={self.checksum}")

    def selfcheck(self):
        """`bytes.__eq__` (early-exit) vs the or-accumulate that mirrors
        Verus. They must agree on every value and differ in nothing but the
        number of byte reads they perform."""
        problems = []
        for c in self.sample_calls(8):
            want = self.tag_fold(c["buf"], c["off"], c["len"])
            if want != c["result"]:
                problems.append(
                    f"simulated result {c['result']} != tag_fold() {want} "
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
