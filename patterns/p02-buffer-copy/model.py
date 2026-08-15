#!/usr/bin/env python3
"""p02-buffer-copy: the independent reference model the gate checks against.

The API is documented at the top of `patterns/p01-array-sum/model.py`; this
file only notes where p02 differs from it, because p02 is the first pattern
that is not p01-shaped and every difference is a place the harness's genericity
was being asserted rather than tested.

    bindings      p01 binds v/off/len/v_len/result. p02 binds
                  src/src_off/src_len/dst_len/dst_before/dst_after/result --
                  `dst_before` and `dst_after` because this kernel *writes*, and
                  the security property ("no byte outside the copied prefix is
                  touched") is a statement about the whole destination buffer
                  before and after the call. They are `bytes`, so the Python
                  `ensures` compares them with `==` and the slicing underneath
                  is at C speed.
    work_per_call bytes copied -- and, since TASK_006, a declared
                  `min_ir_per_work` beside it, because the harness's default
                  rate is derived in 64-bit-lane terms and is unsound for a
                  byte. The pair is the one thing in this file a reviewer should
                  argue with; the argument and the measurements behind it are on
                  the properties below.
    sanitizer     derived, not tabulated: an input is declared "fires" exactly
                  when the simulated run contains a call the rejection test
                  rejects, because that is precisely a call on which R1 (which
                  has no rejection test) runs off the end of a buffer.

Two independent implementations again, as p01 does with prefix sums vs literal
addition:

  * the simulation mutates a `bytearray` destination in place and reads the
    per-record sums out of a table computed once, which is what makes 200 000
    iterations tractable;
  * the helpers `copy_dst` / `copy_sum` -- the ones the derived `ensures` is
    evaluated against -- build the result by concatenating subranges and by
    literally adding bytes, mirroring the shape of the Verus spec functions.

`selfcheck()` runs them against each other; a disagreement is reported there
rather than being silently absorbed into a green line.
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
        self.cap, self.stride, self.src = slb.head2_u64_bytes(self.payload)
        self.n_src = len(self.src)
        self.n_calls = 0
        self.checksum = None
        self.entered = False
        self.any_rejected = False
        self.nrec = 0
        self._rec = []          # per record: (off, copied_len or -1, sum)
        # `slb_zeroed` / `driver::zeroed` reject the capacity before allocating,
        # in both languages, so this is a driver-level rejection and not a
        # kernel behaviour (common/driver.h, SLB_MAX_CAP).
        self.cap_bad = self.cap == 0 or self.cap > slb.MAX_CAP
        if not self.truncated and not self.cap_bad:
            self._run()

    # -- the record table (computed once) ----------------------------------
    def _records(self):
        """(offset, accepted length or -1, wrapping sum) for every record.

        The kernel is a pure function of the record it is pointed at, so the
        whole simulation is a table lookup once this exists. Building it costs
        one pass over the source blob."""
        rec = []
        for k in range(self.nrec):
            off = k * self.stride
            ln = self.src[off] + 256 * self.src[off + 1]
            if ln <= self.cap and ln <= self.n_src - (off + 2):
                rec.append((off, ln, sum(self.src[off + 2: off + 2 + ln]) & MASK))
            else:
                rec.append((off, -1, 0))
        return rec

    # -- simulation --------------------------------------------------------
    def _run(self):
        acc = 0
        if 2 <= self.stride <= self.n_src:
            self.entered = True
            self.nrec = self.n_src // self.stride
            self._rec = self._records()
            # The destination really is a buffer that persists across calls:
            # a rejected record leaves the previous record's bytes in place,
            # and `dst_before` in the bindings below is that state.
            buf = bytearray(self.cap)
            for _ in range(self.n_iters):
                k = (acc * self.nrec) >> 64
                off, ln, s = self._rec[k]
                if ln < 0:
                    self.any_rejected = True
                    r = 0
                else:
                    buf[0:ln] = self.src[off + 2: off + 2 + ln]
                    r = s
                acc = (acc * 31 + r) & MASK
            self.n_calls = self.n_iters
        self.checksum = acc

    def iter_calls(self):
        """Replay the driver loop, yielding one binding per kernel call.

        Regenerated rather than stored: `small.bin` is 200 000 calls."""
        if not self.entered:
            return
        buf = bytearray(self.cap)
        acc = 0
        for _ in range(self.n_iters):
            k = (acc * self.nrec) >> 64
            off, ln, s = self._rec[k]
            before = bytes(buf)
            if ln >= 0:
                buf[0:ln] = self.src[off + 2: off + 2 + ln]
                r = s
            else:
                r = 0
            after = bytes(buf)
            yield {"src": self.src, "src_off": off, "src_len": self.n_src,
                   "dst_len": self.cap, "dst_after_len": len(after),
                   "dst_before": before, "dst_after": after, "result": r}
            acc = (acc * 31 + r) & MASK

    def sample_calls(self, k):
        if not self.entered or k <= 0:
            return []
        step = max(1, self.n_calls // k)
        return list(itertools.islice(
            (c for i, c in enumerate(self.iter_calls()) if i % step == 0), k))

    # -- the second, independent implementation ----------------------------
    # These are what the derived `ensures` is evaluated against, so they must
    # not be the simulation in disguise. They mirror the *Verus* spec functions
    # (../verus.rs `copy_dst` / `copy_sum`): pure, built from subranges, no
    # mutation and no precomputed table.
    def rec_len(self, src, off):
        return src[off] + 256 * src[off + 1]

    def fits(self, src, off, cap):
        ln = self.rec_len(src, off)
        return ln <= cap and off + 2 + ln <= len(src)

    def copy_dst(self, dst0, src, off):
        if not self.fits(src, off, len(dst0)):
            return dst0
        ln = self.rec_len(src, off)
        return src[off + 2: off + 2 + ln] + dst0[ln:]

    def copy_sum(self, src, off, cap):
        if not self.fits(src, off, cap):
            return 0
        acc = 0
        for b in src[off + 2: off + 2 + self.rec_len(src, off)]:
            acc = (acc + b) & MASK
        return acc

    @property
    def helpers(self):
        return {"copy_dst": self.copy_dst, "copy_sum": self.copy_sum}

    # -- what the kernel must do, per call ---------------------------------
    @property
    def work_per_call(self):
        """Bytes the kernel copies per call, from the file alone.

        The minimum over records, so it is a lower bound on the real work and is
        not inflated: an overstated `work_per_call` raises the floor on the
        pattern's own cells and is caught the first time a legitimate rung trips
        it. A record the rejection test rejects contributes 0 -- the kernel
        genuinely does no copying on it.

        Measured, `-O3 isolated`, marginal Ir per byte copied:

            c-gcc 3.80 / safe_naive 6.67 / safe_tuned 3.92 / unsafe 3.75  (small)
            c-gcc 2.25 / safe_naive 2.74 / safe_tuned 2.50 / unsafe 2.49  (large)

        Those are all far above `min_ir_per_work` below, and the reason is that
        the fold -- widening `u8` to `u64` and wrapping-adding -- does not
        vectorise in rustc and only partly in gcc. **That is a fact about these
        rungs, not about the algorithm**, which is exactly why the floor is
        derived from `min_ir_per_work` and not from them."""
        if not self.entered:
            return 0
        return min(0 if ln < 0 else ln for _, ln, _ in self._rec)

    # -- the cheapest legitimate cost of *this algorithm*, per unit ---------
    # TASK_006 D, from TASK_004_REVIEW. The harness default (ALPHA = 0.25 Ir per
    # unit) is derived in 64-bit-lane terms and is **unsound for a byte**: this
    # box moves a byte with glibc `memcpy` in 0.104 instructions (re-measured at
    # TASK_006: 4092 bytes cost 425.7 Ir, isolated by differencing a rung that
    # copies-then-folds-8-bytes against the identical rung with the copy
    # deleted, 483.7 vs 58.0). A kernel that is mostly a bulk copy therefore
    # scores 0.118 Ir/byte and 0.25 would fail it at 0.47x the floor while it is
    # the fastest correct implementation available. A floor that forbids the
    # fastest correct implementation is not a floor.
    #
    # The number below is a lower bound on the *algorithm*: copy n bytes, then
    # fold every one of them into a u64. The cheapest conceivable form of that
    # on this box (Cascade Lake, AVX-512) fuses the two loops and needs, per
    # 64-byte lane, at least
    #
    #     vmovdqu64  load        1
    #     vmovdqu64  store       1
    #     vpsadbw    widen+sum   1
    #     vpaddq     accumulate  1
    #                          ---
    #                            4 instructions per 64 bytes = 0.0625 Ir/byte
    #
    # ignoring loop overhead, which only makes a real implementation dearer.
    # Nothing correct can be below it: every byte must be read once, written
    # once, and included in the sum. Achieved by the shipped rungs: 2.25 ... 6.67
    # Ir/byte, i.e. 36x ... 107x clear.
    #
    # What this floor does NOT do, and no floor of this shape can: certify that
    # the *copy* happened. p02 clears it on the fold alone. The copy is
    # certified by `check.py` step 2 instead -- `checksum` here folds the bytes
    # the copy is supposed to have moved, so a kernel that skips it prints a
    # different number.
    min_ir_per_work = 0.0625
    min_ir_per_work_why = (
        "work is BYTES COPIED. Cheapest correct implementation of "
        "copy-then-fold-every-byte on this box: a fused AVX-512 loop needs at "
        "least a 64-byte load, a 64-byte store, a vpsadbw and a vpaddq per "
        "lane = 4 instructions / 64 bytes = 0.0625 Ir per byte. glibc memcpy "
        "alone measures 0.104 Ir/byte here, so the harness default of 0.25 "
        "would forbid a bulk-copy kernel outright.")

    # -- sanitizer expectation ---------------------------------------------
    @property
    def sanitizer_expect(self):
        """Derived from the simulated run, never tabulated per file.

        A call the rejection test rejects is exactly a call on which R1 -- which
        has no rejection test -- copies past the end of `dst`, reads past the
        end of `src`, or both. So "the simulation rejected at least one of the
        calls this input actually makes" *is* the definition of "ASan must
        report on this input", and `.memory/02-bench-rules.md` then makes
        sanitizer silence the failure.

        Note "actually makes": the driver picks records from a checksum-derived
        index, so a bad record that is never selected must not be declared, and
        an adversarial input that makes zero kernel calls (p01's whole
        adversarial set) is clean by construction."""
        return "fires" if self.any_rejected else "clean"

    # -- what a conforming driver does -------------------------------------
    @property
    def expected_exit(self):
        # Order matters and mirrors the drivers: slb_load rejects a short file
        # before slb_zeroed ever sees the capacity.
        if self.truncated:
            return 5
        if self.cap_bad:
            return 7
        return 0

    @property
    def expected_stdout(self):
        return "" if self.checksum is None else f"{self.checksum}\n"

    def describe(self):
        return (f"n_iters={self.n_iters} cap={self.cap} stride={self.stride} "
                f"n_src={self.n_src} nrec={self.nrec} calls={self.n_calls} "
                f"work/call={self.work_per_call}B san={self.sanitizer_expect} "
                f"truncated={self.truncated} cap_bad={self.cap_bad} "
                f"expected={self.checksum}")

    def selfcheck(self):
        """Table-driven simulation vs the pure subrange/literal-sum helpers."""
        problems = []
        for c in self.sample_calls(8):
            want_d = self.copy_dst(c["dst_before"], c["src"], c["src_off"])
            if want_d != c["dst_after"]:
                problems.append(
                    f"simulated destination disagrees with copy_dst() at "
                    f"src_off={c['src_off']}")
                break
            want_r = self.copy_sum(c["src"], c["src_off"], c["dst_len"])
            if want_r != c["result"]:
                problems.append(
                    f"simulated result {c['result']} != copy_sum() {want_r} at "
                    f"src_off={c['src_off']}")
                break
        return problems


def build(path):
    return Model(path)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        m = build(p)
        print(f"{os.path.basename(p):28s} {m.describe()}  "
              f"exit={m.expected_exit} selfcheck={m.selfcheck()}")
