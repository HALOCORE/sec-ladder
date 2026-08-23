#!/usr/bin/env python3
"""p22-hash-probe: the independent reference model the gate checks against.

The API is documented at the top of `patterns/p01-array-sum/model.py`; this
file notes only where p22 differs.

    bindings      buf/off/len/buf_len/result -- the READ-ONLY shape p03, p06,
                  p11, p12, p14, p16, p17, p05, p07, p10, p27, p47 and p38 use.
                  p22's kernel writes only its own local table, which is not a
                  binding: nothing the caller can observe is written.
    work_per_call `stride` -- window bytes, the denomination twelve other
                  patterns use.
    work_unit     "window byte"; `work_unit_bits` 8.
    sanitizer     **"clean" on every input, including the hanging one.** p22's
                  bug is not a memory-safety bug: every table access is
                  `tab[i % 64]`. There is nothing for ASan or UBSan to find, and
                  measuring that is half the pattern (see `sanitizer_expect`).
    expected_hang **True on `adversarial-full.bin` and nowhere else** -- the
                  declaration TASK_068 added, and p22 is its first user. It is
                  DERIVED from the blob's bytes (see the note below the
                  constants), never from the file name.

**WHAT THIS MODEL COMPUTES IS THE DEFINED SEMANTICS**, i.e. what
`c/kernel_hardened.c` and all four Rust rungs do. `c/kernel.c` omits
`&& nfill < TABCAP` and therefore does not return at all on
`adversarial-full.bin`; there is no "wrong answer" to model, only an absent one,
which is why `expected_hang` is a separate field from `expected_exit` and why
`expected_exit` keeps describing the CONFORMING behaviour (`harness/check.py`
`check_adversarial`).

Two independent implementations, as every earlier pattern does:

  * the **simulation** (`_window`) keeps the table as a Python `list` and finds
    the slot with an explicit `while`, exactly as the exec rungs do;
  * the **helper** `key_fold` -- the one the derived `ensures` is evaluated
    against -- mirrors the Verus spec functions in ../verus.rs term for term:
    `u32_at` written with `+`/`*`, `hash_s` with `//`/`%`, and a FUEL-BOUNDED
    `probe` that walks at most TABCAP steps because a spec function must
    terminate to be a function at all.

**That asymmetry is the pattern.** The specification's probe is bounded and the
implementation's is not; ../verus.rs's `decreases` is precisely what says the
two land in the same slot.

`selfcheck()` runs them against each other.
"""

import itertools
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "common"))
import slb  # noqa: E402

MASK = (1 << 64) - 1
HDR = 4                   # nkey:u32 LE
TABCAP = 64               # must equal SLB_P22_TABCAP and every rung's const
EMPTY = 0
SENT = 251

#: ⚠ **`expected_hang` is DERIVED FROM THE BYTES, not from the file name**, and
#: the first draft of this file got that wrong in a way a gate run caught.
#: `harness/check.py::run_budgets` states the division of labour: *which inputs
#: do not terminate is a SEMANTIC PREDICTION, derivable from the blob's own
#: bytes, and it is model.py's job to derive it*. A name-keyed set violates it
#: silently: `check_miri` does not build the model from the input file, it builds
#: it from a REWRITTEN COPY at `.temp/check/p22/miri/miri.<name>.bin` (n_iters
#: clamped to MIRI_PROBE_ITERS), whose basename is `miri.adversarial-full.bin`.
#: A name-keyed declaration returns False there, so the same blob was declared
#: non-terminating in stage 4 and terminating in stage 8 -- measured, in the
#: first p22 gate run. `_hangs_unguarded` below simulates the rung WITHOUT the
#: capacity conjunct over every window the driver actually visits, so the two
#: stages cannot disagree.


class Model:
    """Simulates ../spec.md's driver loop and kernel from the file alone."""

    def __init__(self, path):
        f = slb.read(path)
        self.path = path
        self.name = os.path.basename(path)
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
        self._win = []          # per window: (result, nfill, maxprobe, hang)
        self._hangs = False
        if not self.truncated:
            self._run()

    # -- the window table (computed once) ----------------------------------
    def _window(self, off):
        """(result, nfill, max probe steps, hangs-unguarded). Implementation 1
        of 2: an explicit table and an explicit unbounded `while`, the way the
        exec rungs are written. `key_fold` below builds the same answer the way
        ../verus.rs's spec functions do.

        The fourth element is what `expected_hang` is derived from: it is True
        when the rung WITHOUT `nfill < TABCAP` -- i.e. `c/kernel.c` -- would
        reach its probe loop with a full table and a key that is not in it. This
        model computes the DEFINED semantics and additionally answers "would the
        undefended spelling have got stuck here?", which is a question about the
        bytes and not about the file name."""
        if self.stride < HDR:
            return 0, 0, 0, False
        b = self.buf
        nkey = int.from_bytes(b[off:off + HDR], "little")
        if nkey == 0:
            return 0, 0, 0, False
        tab = [EMPTY] * TABCAP
        nfill = acc = maxpr = 0
        hang = False
        p = HDR
        for _ in range(nkey):
            if self.stride - p < 1:
                break
            k = b[off + p]
            p += 1
            if k != EMPTY and nfill < TABCAP:
                i = k * 2654435761 // 16777216 % TABCAP
                pr = 0
                while tab[i] != EMPTY and tab[i] != k:
                    i = (i + 1) % TABCAP
                    pr += 1
                if pr > maxpr:
                    maxpr = pr
                if tab[i] == EMPTY:
                    tab[i] = k
                    nfill += 1
                acc = (acc * 31 + i) & MASK
            else:
                if k != EMPTY and nfill == TABCAP and k not in tab:
                    # The unguarded rung enters its probe loop here with no
                    # EMPTY slot and no matching key: it never leaves it.
                    hang = True
                acc = (acc * 31 + SENT) & MASK
        return (acc * 31 + nfill) & MASK, nfill, maxpr, hang

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
                r = self._win[k][0]
                acc = (acc * 31 + r) & MASK
            self.n_calls = self.n_iters
            # Over the windows the driver ACTUALLY VISITED -- a hanging window
            # the Lemire index never selects makes no cell hang.
            self._hangs = any(w is not None and w[3] for w in self._win)
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
            r = self._win[k][0]
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
    # What the derived `ensures` is evaluated against. It must not be the
    # simulation in disguise, so it mirrors the *Verus* spec functions in
    # ../verus.rs: `u32_at` with + and *, `hash_s` with // and %, and a
    # FUEL-BOUNDED probe.
    def _u32_at(self, buf, p):
        return (buf[p] + 256 * buf[p + 1] + 65536 * buf[p + 2]
                + 16777216 * buf[p + 3])

    def _hash_s(self, k):
        return k * 2654435761 // 16777216 % TABCAP

    def _probe(self, tab, i, k, fuel):
        """`probe` in ../verus.rs. Fuel-bounded, because a spec function must
        terminate; iterative where the Verus function is recursive, for p11's,
        p14's, p27's, p47's and p38's reason (CPython's recursion limit)."""
        while fuel > 0 and tab[i] != EMPTY and tab[i] != k:
            i = (i + 1) % TABCAP
            fuel -= 1
        return i

    def _run_spec(self, buf, off, ln, t, nkey, p, tab, nfill, acc):
        """`run` in ../verus.rs: the abstract machine."""
        while not (t >= nkey or ln - p < 1):
            k = buf[off + p]
            if k != EMPTY and nfill < TABCAP:
                i = self._probe(tab, self._hash_s(k), k, TABCAP)
                if tab[i] == EMPTY:
                    tab = tab[:i] + [k] + tab[i + 1:]
                    nfill = nfill + 1
                acc = (acc * 31 + i) & MASK
            else:
                acc = (acc * 31 + SENT) & MASK
            t, p = t + 1, p + 1
        return (acc * 31 + nfill) & MASK

    def key_fold(self, buf, off, ln):
        """`key_fold` in ../verus.rs: what the kernel must return."""
        if ln < HDR:
            return 0
        nkey = self._u32_at(buf, off)
        if nkey == 0:
            return 0
        return self._run_spec(buf, off, ln, 0, nkey, HDR,
                              [EMPTY] * TABCAP, 0, 0)

    @property
    def helpers(self):
        return {"key_fold": self.key_fold}

    # -- what the kernel must do, per call ---------------------------------
    @property
    def work_unit(self):
        return "window byte"

    @property
    def work_unit_bits(self):
        return 8

    @property
    def work_per_call(self):
        """`stride` -- window bytes, the denomination p16, p05, p11, p12, p06,
        p14, p27, p10, p38 and p47 use.

        **Which way this estimate errs: strict.** The kernel clears 64 table
        bytes on every call before it reads a single key, so the true work is
        `stride + 64` at least and this undercounts by that whole clear. It
        over-counts only the padding past `nkey` in a window whose declared
        count is short of the window -- `degenerate.bin`'s third and fourth
        windows have some, and neither is a `collapse.probe_input`."""
        return self._work if self.entered else 0

    # -- sanitizer expectation ---------------------------------------------
    @property
    def sanitizer_expect(self):
        """**"clean", on every input including the hanging one -- and that is
        the pattern's central measurement rather than a gap.**

        p22's bug is a non-terminating loop. Every access it makes is `tab[i]`
        with `i` reduced modulo TABCAP on entry and on every step, so there is
        no out-of-bounds access, no use-after-free, no uninitialised read and no
        undefined behaviour for a sanitizer to report. Measured
        (`controls/gen_controls.py --run c_asan`): gcc -O1
        `-fsanitize=address,undefined -static-libasan -static-libubsan` on
        `c/kernel.c` exits 0 with an empty stderr on every terminating input,
        and on `adversarial-full.bin` produces **no diagnostic at all** -- it
        spins until the timeout kills it.

        Miri says the same thing about the safe-Rust port of the same omission:
        no UB, no output, killed by the timeout
        (`controls/gen_controls.py --run r2_noguard`).

        Declaring "fires" anywhere here would be false. `harness/check.py`
        additionally REFUSES the combination `sanitizer_expect: "fires"` with
        `expected_hang` on one input, for the good reason that a sanitizer which
        fires aborts the process and the two cannot both be observed."""
        return "clean"

    # -- what a conforming driver does -------------------------------------
    @property
    def expected_hang(self):
        """**The PREDICTION: this input makes some cell run for ever**, derived
        from the blob's bytes by `_window`'s fourth element.

        True on `adversarial-full.bin` alone, of everything this pattern ships.
        Its single window carries the 64 distinct keys that fill the table and
        then a 65th that is absent from it, so `c/kernel.c` -- the rung without `nfill < TABCAP` -- enters its
        probe loop with no EMPTY slot to stop at and no matching key to find.
        `c/kernel_hardened.c` and all four Rust rungs see `nfill == TABCAP` and
        fold SENT, so **8 of the 32 built cells hang and 24 do not**: `c-gcc`
        and `c-clang` at both optimisation levels and in both link modes.

        This is a prediction and the gate falsifies it two ways. Stage 4 fails
        the pattern if EVERY cell terminates inside the budget pinned in
        ../spec.md's `run.timeout_s`, and `_confirm_hang` re-runs one hung cell
        at ten times that budget and fails if it terminates -- so a merely SLOW
        cell cannot be passed off as a hung one.

        `adversarial-nearfull.bin` is the negative control: 63 distinct keys and
        then 64 more from the same 63, so `nfill` stops one short of TABCAP and
        **every cell terminates, `c/kernel.c` included.** It carries no
        `expected_hang`, and the gate would fail if it did."""
        return self._hangs

    @property
    def expected_exit(self):
        return 5 if self.truncated else 0

    @property
    def expected_stdout(self):
        return "" if self.checksum is None else f"{self.checksum}\n"

    def describe(self):
        w0 = self._win[0] if self._win and self._win[0] else (0, 0, 0, False)
        return (f"n_iters={self.n_iters} stride={self.stride} "
                f"n_blob={self.n_blob} nwin={self.nwin} calls={self.n_calls} "
                f"work/call={self.work_per_call}B "
                f"nfill(w0)={w0[1]} maxprobe(w0)={w0[2]} "
                f"san={self.sanitizer_expect} hang={self.expected_hang} "
                f"truncated={self.truncated} expected={self.checksum}")

    def selfcheck(self):
        """The simulation against `key_fold`. They share no code: the
        simulation mutates one `list` in place and tracks a probe count, the
        helper rebuilds the table with slicing and walks a FUEL-BOUNDED probe
        the way the Verus spec functions do."""
        problems = []
        for c in self.sample_calls(8):
            want = self.key_fold(c["buf"], c["off"], c["len"])
            if want != c["result"]:
                problems.append(
                    f"simulated result {c['result']} != key_fold() {want} "
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
