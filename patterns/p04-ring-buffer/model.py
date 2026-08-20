#!/usr/bin/env python3
"""p04-ring-buffer: the independent reference model the gate checks against.

The API is documented at the top of `patterns/p01-array-sum/model.py`; this file
notes only where p04 differs.

    bindings      buf/off/len/buf_len/result, the read-only shape p16, p17, p05,
                  p07, p11 and p03 use. p04's kernel writes only its own local
                  ring.
    work_per_call **bytes of the window** -- `stride`. Every byte of a
                  well-formed window is read exactly once: the 4 header bytes as
                  a u32, then the op byte and the four value bytes of each
                  operation. See the property's docstring for the direction of
                  the error.
    work_unit     "byte"; `work_unit_bits` 8.
    sanitizer     derived, not tabulated -- and the derivation returns "clean"
                  on **every** input this pattern can express, which is the
                  finding rather than an oversight. See `sanitizer_expect`.

Two independent implementations, as p01, p02, p16, p17, p05, p07, p11 and p03 do:

  * the **simulation** `_window` keeps the queue as a Python **list** with
    `append` and `pop(0)`, tests fullness with `len(q) == RING_CAP - 1` and
    emptiness with `if q:`, and decodes the value with `int.from_bytes`. It has
    no cursors at all, so it cannot share a modular-arithmetic mistake with the
    rungs;
  * the **helper** `ring_fold` -- the one the derived `ensures` is evaluated
    against -- mirrors the Verus spec function `run` in ../verus.rs: a
    fixed-length list of `RING_CAP` slots, two explicit integer cursors, every
    `% RING_CAP` written out, and the header and value decoded by `_u32_at`'s
    written-out `b0 + 256*b1 + 65536*b2 + 16777216*b3` rather than by
    `int.from_bytes`.

    It is **iterative where the Verus function is recursive**, for p03's reason:
    `run` recurses once per operation and p04's windows hold up to 830
    operations, which would exceed CPython's default recursion limit on a bigger
    window. The two are otherwise transliterations.

`selfcheck()` runs them against each other; a disagreement is reported there
rather than being silently absorbed into a green line.

**Both implementations model the CHECKED kernel**, i.e. R1h and R2-R5. R1 is the
rung with the bug and is expected to disagree on `adversarial-overwrite`; the
gate records that disagreement in its behaviour table rather than requiring it
to vanish (`.memory/02-bench-rules.md`).

**Neither implementation trusts `nops`**, and neither does ../verus.rs. What
bounds the walk is the length check `5*nops > avail`, which is in *every* rung
including R1 -- `adversarial-count.bin` is the row that shows it. The **only**
thing R1 omits is the fullness test `(tail + 1) % RING_CAP != head`.

Three arithmetic notes that are easy to get wrong and are load-bearing:

  * the ring holds `RING_CAP - 1 = 63` elements, not 64. `(tail + 1) % RING_CAP
    == head` is the fullness test, so one slot is always reserved; a model that
    allowed 64 would disagree with every rung on `adversarial-overwrite`.
  * the result is `((acc*31 + head)*31 + tail)*31 + nops`, so a rung whose
    cursors ended anywhere else -- which is exactly what a wrong wrap produces
    -- cannot land on the same checksum even if it folded the same values.
    Python has no wrap, so every step masks explicitly.
  * a POP on an empty ring and a PUSH onto a full one are both **no-ops** in the
    checked semantics: `acc`, `head` and `tail` are all unchanged, and neither
    is an error and neither is a rejection of the window.
"""

import itertools
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "common"))
import slb  # noqa: E402

MASK = (1 << 64) - 1
HDR = 4                   # nops:u32
OPLEN = 5                 # op:u8 + val:u32
RING_CAP = 64             # the same compile-time constant every rung carries


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
        self.any_overwrite = False
        self.nwin = 0
        self._work = 0
        self._win = []          # per window: (result, r1_overwrites, counts)
        if not self.truncated:
            self._run()

    # -- the window table (computed once) ----------------------------------
    def _window(self, off):
        """(result, R1_pushes_onto_a_full_ring, counts) for the window at `off`.

        Implementation 1 of 2. The queue is a Python **list** with `append` and
        `pop(0)`, the value is decoded with `int.from_bytes`, fullness is
        `len(q) == RING_CAP - 1` and emptiness is `if q:` -- there are no
        cursors here at all, so this implementation cannot share a modular
        mistake with the cursor walk below or with any rung. `head` and `tail`
        are reconstructed at the end from the same two quantities the rungs
        carry, which is the one place the two shapes have to meet.

        The second element records whether the rung with **no** fullness guard
        -- R1 -- would push onto a full ring. That is a store into the one slot
        the checked kernel keeps reserved: it is **in bounds**, it corrupts no
        neighbouring object, and no sanitiser can see it. What it does is
        advance `tail` onto `head`, which makes the ring read EMPTY and loses
        all 63 live elements. `sanitizer_expect` is derived from a different
        predicate (`any_oob`) precisely so that this one cannot be mistaken for
        a memory error."""
        ln = self.stride
        if ln < HDR:
            return 0, False, dict(xpush=0, dpush=0, xpop=0, epop=0)
        buf = self.buf
        nops = int.from_bytes(buf[off:off + 4], "little")
        c = dict(xpush=0, dpush=0, xpop=0, epop=0)
        if nops == 0:
            return 0, False, c
        if OPLEN * nops > ln - HDR:
            return 0, False, c
        q = []
        acc = 0
        base_head = 0      # how many elements have LEFT the queue
        pushed = 0         # how many have ENTERED it
        overwrite = False
        for k in range(nops):
            base = off + HDR + OPLEN * k
            if buf[base] == 0:
                if len(q) == RING_CAP - 1:
                    c["dpush"] += 1
                    overwrite = True
                else:
                    q.append(int.from_bytes(buf[base + 1:base + 5], "little"))
                    pushed += 1
                    c["xpush"] += 1
            else:
                if q:
                    acc = (acc * 31 + q.pop(0)) & MASK
                    base_head += 1
                    c["xpop"] += 1
                else:
                    c["epop"] += 1
        head = base_head % RING_CAP
        tail = pushed % RING_CAP
        r = ((((acc * 31 + head) & MASK) * 31 + tail) & MASK) * 31 + nops
        return r & MASK, overwrite, c

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
                r, over, _c = self._win[k]
                if over:
                    self.any_overwrite = True
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
            r, _over, _c = self._win[k]
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
    # the simulation in disguise. It mirrors the *Verus* spec function
    # (../verus.rs `run`): a fixed-length slot list, two explicit cursors, every
    # `% RING_CAP` written out, no `append`, no `pop`, no `int.from_bytes`, no
    # cache.
    def _u32_at(self, buf, p):
        """`u32_at` in ../verus.rs, written out with `+` and `*` exactly as the
        rungs write it -- not `int.from_bytes`, which is the simulation's."""
        return (buf[p] + 256 * buf[p + 1] + 65536 * buf[p + 2]
                + 16777216 * buf[p + 3])

    def _run_spec(self, buf, off, nops):
        """`run` in ../verus.rs. Iterative rather than recursive -- see the
        module docstring; every other line is a transliteration."""
        ring = [0] * RING_CAP
        head = 0
        tail = 0
        acc = 0
        k = 0
        while k < nops:
            val = self._u32_at(buf, off + 5 + 5 * k)
            if buf[off + 4 + 5 * k] == 0:
                if (tail + 1) % RING_CAP != head:
                    ring[tail] = val
                    tail = (tail + 1) % RING_CAP
            else:
                if head != tail:
                    acc = (acc * 31 + ring[head]) & MASK
                    head = (head + 1) % RING_CAP
            k = k + 1
        return ((((acc * 31 + head) & MASK) * 31 + tail) & MASK) * 31 + nops \
            & MASK

    def ring_fold(self, buf, off, ln):
        """`ring_fold` in ../verus.rs: what the kernel must return."""
        if ln < HDR:
            return 0
        nops = self._u32_at(buf, off)
        if nops == 0:
            return 0
        if 5 * nops > ln - 4:
            return 0
        return self._run_spec(buf, off, nops)

    @property
    def helpers(self):
        return {"ring_fold": self.ring_fold}

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

        **Which way this estimate errs: STRICT on every input this pattern
        ships** (`.memory/02-bench-rules.md` asks, so: say it, and say it in
        both directions because p16 errs strict, p17 loose, p05 strict and p03
        strict -- four patterns, and the direction is not inheritable).

          * *over*-count, and it is the only term that can go that way: a
            **POP** operation reads its op byte and does not read its four value
            bytes at all -- rustc, clang and gcc all sink that load into the
            push arm, which ../NOTES.md 1 checked on the disassembly before this
            file was written. So a window whose ops are all POPs visits
            `4 + nops` bytes where `stride` counts `4 + 5*nops`.
          * *under*-count: none. Every other byte is read exactly once and the
            ring traffic is not counted at all.

        The over-count is bounded by the pop density, ~50% on both `small` and
        `large`, so `stride` is at most 2x the number of byte-visits and the
        derived floor is one the kernel must clear. It can therefore never let a
        collapsed kernel through, which is the only direction that matters.

        No `min_ir_per_work` is declared, so the harness default of 0.25 Ir per
        byte applies unchanged. The argument for it: p04's inner loop is a
        **data-dependent two-way branch on an attacker byte** followed by a
        serial dependence through `head`, `tail` and `acc`, so there is no
        vector form at any `-march` -- operation `k+1` cannot even be decoded
        into the right arm until operation `k`'s effect on the cursors is
        known."""
        return self._work if self.entered else 0

    # -- sanitizer expectation ---------------------------------------------
    @property
    def sanitizer_expect(self):
        """Derived from the simulated run, never tabulated per file -- and the
        derivation is **identically "clean"**, which is p04's headline rather
        than a gap.

        The predicate is `any_oob`: does any rung, R1 included, form a ring
        index outside `[0, RING_CAP)`? It is False on every input, and that is
        arithmetic and not luck. Every index either rung forms is `head` or
        `tail`; both start at 0 and every update is `(x + 1) % RING_CAP`, whose
        result is in `[0, RING_CAP)` for every input value. **Deleting the
        fullness check changes which slot is written and never whether the write
        is in bounds.**

        So `adversarial-overwrite.bin` -- the input this pattern exists for --
        is a `"clean"` row: ASan sees nothing, UBSan sees nothing, Miri sees
        nothing, safe Rust's bounds check sees nothing, and ../NOTES.md 6
        measures that the memory-safety half of the R5 proof discharges it too.
        What catches it is the checksum, i.e. the functional specification.

        Contrast p03, whose `sp - 1` at `sp == 0` left the array and fired both
        sanitisers, and p12, whose write left the destination object. p04's
        guard's threshold is a **live length below the allocation's extent**, so
        `.memory/02-bench-rules.md`'s write rule does not reach it: "the guard
        fired" and "the unguarded rung committed UB" are independent events
        here, and only the first ever happens."""
        return "fires" if self.any_oob else "clean"

    # -- what a conforming driver does -------------------------------------
    @property
    def expected_exit(self):
        # p04's payload allocates nothing from an attacker-controlled size --
        # there is no `cap` word and no `slb_zeroed` -- so p02's exit 7 has no
        # analogue here, exactly as for p16, p17, p05, p07, p11 and p03.
        # `slb_load` rejecting a short file is the only non-zero exit this
        # driver produces.
        return 5 if self.truncated else 0

    @property
    def expected_stdout(self):
        return "" if self.checksum is None else f"{self.checksum}\n"

    def describe(self):
        c = self._win[0][2] if self._win and self._win[0] else {}
        return (f"n_iters={self.n_iters} stride={self.stride} "
                f"n_blob={self.n_blob} nwin={self.nwin} calls={self.n_calls} "
                f"work/call={self.work_per_call}B "
                f"win0={c} r1_overwrites={self.any_overwrite} "
                f"san={self.sanitizer_expect} "
                f"truncated={self.truncated} expected={self.checksum}")

    def op_counts(self, off):
        """`{xpush, dpush, xpop, epop}` for the window at `off` -- the four
        regressors ../NOTES.md 4's laws are linear in. Exposed so the sweep
        scripts do not have to re-implement the two guards."""
        return self._window(off)[2]

    def r1_result(self, off):
        """What R1 -- the rung with NO fullness check -- returns for the window
        at `off`. Exposed so ../NOTES.md 7's divergence is a number from this
        file rather than from a binary. Written with the cursors, because
        without the fullness test there is no list-shaped way to say it."""
        ln = self.stride
        if ln < HDR:
            return 0
        buf = self.buf
        nops = self._u32_at(buf, off)
        if nops == 0 or 5 * nops > ln - 4:
            return 0
        ring = [0] * RING_CAP
        head = tail = acc = 0
        for k in range(nops):
            val = self._u32_at(buf, off + 5 + 5 * k)
            if buf[off + 4 + 5 * k] == 0:
                ring[tail] = val                      # NO FULLNESS TEST
                tail = (tail + 1) % RING_CAP
            else:
                if head != tail:
                    acc = (acc * 31 + ring[head]) & MASK
                    head = (head + 1) % RING_CAP
        return ((((acc * 31 + head) & MASK) * 31 + tail) & MASK) * 31 + nops \
            & MASK

    def selfcheck(self):
        """list/append/pop simulation vs the two-cursor walk that mirrors the
        Verus spec function."""
        problems = []
        for c in self.sample_calls(8):
            want = self.ring_fold(c["buf"], c["off"], c["len"])
            if want != c["result"]:
                problems.append(
                    f"simulated result {c['result']} != ring_fold() {want} "
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
