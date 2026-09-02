#!/usr/bin/env python3
"""p16-tlv-walk: the independent reference model the gate checks against.

The API is documented at the top of `patterns/p01-array-sum/model.py`; this file
notes only where p16 differs.

    bindings      p01 binds v/off/len/v_len/result; p02 adds the destination
                  buffer before and after because its kernel writes. p16's
                  kernel writes nothing at all -- the harm it models is a READ --
                  so the bindings are back to a read-only shape:
                  buf/off/len/buf_len/result. That is not a simplification, it
                  is the whole reason this pattern's security argument cannot
                  live in an `ensures`: "no byte outside the window was read" is
                  not a property of the return value, because a kernel could
                  read out of bounds and discard the byte. See ../spec.md.
    work_per_call the WINDOW, in bytes -- i.e. `stride`, constant across every
                  call on a given input. Argued below; the short version is that
                  a parser has a *distribution* of work per call and
                  `check.py::check_marginal_ir` needs one scalar, and
                  denominating in records
                  or in bytes-actually-folded collapses to 0 the moment a probe
                  input contains a rejected record.
    sanitizer     derived, not tabulated: an input is "fires" exactly when the
                  simulated run contains a call whose walk was stopped by the
                  fit test, because that is precisely a call on which R1 (which
                  has no fit test) folds its way off the end of the blob.

Two independent implementations, as p01 and p02 do:

  * the **simulation** walks each window once, collecting the byte *slices* it
    visits (the tag byte, then the value) and folding the concatenation with a
    single Horner pass. Per-window results go in a table, which is what makes
    25 000 driver iterations tractable;
  * the **helper** `tlv_fold` -- the one the derived `ensures` is evaluated
    against -- is a byte-at-a-time recursive walk with no slicing and no table,
    mirroring the shape of the Verus spec functions `tlv_walk` / `fold_bytes`
    in ../verus.rs.

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
        self.stride, self.buf = slb.head1_u64_bytes(self.payload)
        self.n_blob = len(self.buf)
        self.n_calls = 0
        self.checksum = None
        self.entered = False
        self.any_rejected = False
        self.nwin = 0
        self._win = []          # per window: (result, stopped_by_fit_test)
        if not self.truncated:
            self._run()

    # -- the window table (computed once) ----------------------------------
    def _window(self, off):
        """(result, stopped_by_fit_test) for the window at `off`.

        Implementation 1 of 2. Walks the chain collecting the *slices* it
        folds -- one tag byte, then the whole value -- and folds the
        concatenation in one Horner pass at the end. `stopped` records whether
        the walk ended on the fit test rather than on the header test, which is
        what `sanitizer_expect` below is derived from."""
        end = off + self.stride
        p = off
        nrec = 0
        seen = bytearray()
        stopped = False
        while end - p >= 3:
            seen.append(self.buf[p])
            vlen = self.buf[p + 1] + 256 * self.buf[p + 2]
            if vlen > end - (p + 3):
                stopped = True
                break
            seen += self.buf[p + 3: p + 3 + vlen]
            p = p + 3 + vlen
            nrec = (nrec + 1) & MASK
        acc = 0
        for b in seen:
            acc = (acc * 31 + b) & MASK
        return (acc * 31 + nrec) & MASK, stopped

    # -- simulation --------------------------------------------------------
    def _run(self):
        acc = 0
        if 3 <= self.stride <= self.n_blob:
            self.entered = True
            self.nwin = self.n_blob // self.stride
            self._win = [self._window(k * self.stride) for k in range(self.nwin)]
            for _ in range(self.n_iters):
                k = (acc * self.nwin) >> 64
                r, stopped = self._win[k]
                if stopped:
                    self.any_rejected = True
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
            r, _stopped = self._win[k]
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
    # (../verus.rs `tlv_walk` / `fold_bytes`): recursive over the record chain,
    # byte-at-a-time over the value, no slicing, no table, and the same
    # (acc, nrec) pair threaded through the recursion.
    def _fold_bytes(self, buf, frm, n, acc):
        """`fold_bytes` in ../verus.rs: acc, folded left over buf[frm..frm+n)."""
        for i in range(n):
            acc = (acc * 31 + buf[frm + i]) & MASK
        return acc

    def _tlv_walk(self, buf, p, end, acc, nrec):
        """`tlv_walk` in ../verus.rs, returning (acc, nrec)."""
        if end - p < 3:
            return acc, nrec
        a1 = (acc * 31 + buf[p]) & MASK
        vlen = buf[p + 1] + 256 * buf[p + 2]
        if vlen > end - (p + 3):
            return a1, nrec
        return self._tlv_walk(buf, p + 3 + vlen, end,
                              self._fold_bytes(buf, p + 3, vlen, a1),
                              (nrec + 1) & MASK)

    def tlv_fold(self, buf, off, ln):
        """`tlv_fold` in ../verus.rs: what the kernel must return."""
        acc, nrec = self._tlv_walk(buf, off, off + ln, 0, 0)
        return (acc * 31 + nrec) & MASK

    @property
    def helpers(self):
        return {"tlv_fold": self.tlv_fold}

    # -- what the kernel must do, per call ---------------------------------
    @property
    def work_per_call(self):
        """The window, in bytes -- `stride` -- from the file alone.

        **Why the window and not the records, and not the bytes folded.**
        `check.py::check_marginal_ir` needs one scalar per input and hard-fails
        with `rep.fail("collapse-ir", ...)` on `model.py reports
        work_per_call=...; a probe input on which the kernel has nothing to do
        cannot bound anything`.
        A parser has a *distribution* of work per call: it early-exits
        on a malformed record, and p02's convention (the minimum over records)
        collapses to 0 the moment a probe input contains one rejected record --
        which is exactly what a TLV corpus contains. Denominating in *records*
        has the same problem and a worse one: the record count is itself
        attacker-controlled, so the unit would move with the data.

        The window is the unit that does not move. It is fixed by the payload
        header, it is identical on every call of a given input, and it is a
        strict over-estimate of the bytes the kernel actually folds -- two of
        every record's three header bytes are read but not folded, and a
        rejected record ends the walk early. An over-estimate raises the floor
        on the pattern's own cells, so the derived floor errs *strict*, which is
        the direction a floor should err.

        Measured, `-O3 isolated`, marginal Ir per window byte: see NOTES.md 2 and 3b.
        All the shipped rungs sit far above the harness default of 0.25, which
        p16 therefore uses unchanged -- the fold is a serial
        `acc = acc*31 + byte` dependence chain, so unlike p02's copy there is no
        bulk-memory instruction that could undercut the default and no reason to
        declare a lower `min_ir_per_work`."""
        return self.stride if self.entered else 0

    # -- sanitizer expectation ---------------------------------------------
    @property
    def sanitizer_expect(self):
        """Derived from the simulated run, never tabulated per file.

        A call whose walk was stopped by the **fit test** is exactly a call on
        which R1 -- which has no fit test -- folds `vlen` bytes starting past
        what remains, i.e. reads off the end of the window and (on
        `adversarial-overrun`, where the window is the whole blob) off the end
        of the allocation. So "the simulation was stopped by the fit test on at
        least one of the calls this input actually makes" *is* the definition of
        "ASan must report on this input", and `.memory/02-bench-rules.md` then
        makes sanitizer silence the failure.

        Note "actually makes": the driver picks windows from a checksum-derived
        index, so a malformed window that is never selected must not be
        declared. That is why `adversarial-overrun.bin` is built with exactly
        one window -- see inputs/gen.py.

        A walk stopped by the *header* test (`adversarial-trunc.bin`, whose
        windows end in a 2-byte tail) is NOT a rejection: R1 keeps that test, so
        every rung stops in the same place and the input is clean."""
        return "fires" if self.any_rejected else "clean"

    # -- what a conforming driver does -------------------------------------
    @property
    def expected_exit(self):
        # p16's payload allocates nothing from an attacker-controlled size --
        # there is no `cap` word and no `slb_zeroed` -- so p02's exit 7 has no
        # analogue here. `slb_load` rejecting a short file is the only non-zero
        # exit this pattern's driver can produce.
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
        """Slice-and-Horner simulation vs the recursive byte-at-a-time walk."""
        problems = []
        for c in self.sample_calls(8):
            want = self.tlv_fold(c["buf"], c["off"], c["len"])
            if want != c["result"]:
                problems.append(
                    f"simulated result {c['result']} != tlv_fold() {want} at "
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
