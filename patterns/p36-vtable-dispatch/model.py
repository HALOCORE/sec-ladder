#!/usr/bin/env python3
"""p36-vtable-dispatch: the independent reference model the gate checks against.

The API is documented at the top of `patterns/p01-array-sum/model.py`; this
file notes only where p36 differs.

    bindings      buf/off/len/buf_len/result -- the READ-ONLY shape p03, p06,
                  p11, p12, p14, p16, p17, p05, p07, p10, p22, p27, p38 and p47
                  use. p36's kernel writes nothing at all.
    work_per_call `stride` -- window bytes, the denomination fourteen other
                  patterns use.
    work_unit     "window byte"; `work_unit_bits` 8.
    sanitizer     **"fires" on the two out-of-table rows and "clean" everywhere
                  else**, and it is DERIVED FROM THE BYTES (`_oob`), never from
                  the file name -- `harness/check.py` rebuilds the model from a
                  REWRITTEN COPY for the Miri stage, whose basename is
                  `miri.<name>.bin`, so a name-keyed declaration disagrees with
                  itself between stages (p22 measured that the hard way).

**WHAT THIS MODEL COMPUTES IS THE DEFINED SEMANTICS**, i.e. what
`c/kernel_hardened.c` and all four Rust rungs do. `c/kernel.c` omits
`op < NOPS`, so on an out-of-table opcode it loads a code pointer from past the
end of `TABLE` and calls it; on this box that is a SIGSEGV in 8 of 8 plain
cells. There is no "wrong answer" to model there, only an absent one, and
`harness/check.py::check_adversarial` records the divergence against the
CONFORMING answer this file computes.

Two independent implementations, as every earlier pattern does:

  * the **simulation** (`_window`) walks the records with an explicit `while`
    and an explicit cursor guard, exactly as `c/kernel.c` and R2/R4 do;
  * the **helper** `op_fold` -- the one the derived `ensures` is evaluated
    against -- mirrors the Verus spec functions in ../verus.rs term for term:
    `u32_at` written with `+` and `*`, and `run` as the abstract machine over
    (t, p, acc) with `op_spec` as its table.

`selfcheck()` runs them against each other.
"""

import itertools
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "common"))
import slb  # noqa: E402

MASK = (1 << 64) - 1
HDR = 4                   # nrec:u32 LE
NOPS = 8                  # must equal SLB_P36_NOPS and every rung's const
SENT = 251

#: THE OP SET, constant for constant identical to c/kernel.c's op0..op7, to the
#: four Rust rungs' `impl Op for OpN`, and to ../verus.rs's `op_spec`. One
#: 64-bit constant and one of `^`, `+`, `-` each: the finding is the CALL, not
#: the callee, so no op may be dear enough to drown the dispatch.
OPS = [
    lambda x: x ^ 0x9E3779B97F4A7C15,
    lambda x: x ^ 0xFF51AFD7ED558CCD,
    lambda x: (x + 0x2545F4914F6CDD1D) & MASK,
    lambda x: (x + 0xC4CEB9FE1A85EC53) & MASK,
    lambda x: (x - 0x61C8864680B583EB) & MASK,
    lambda x: (x - 0xBF58476D1CE4E5B9) & MASK,
    lambda x: x ^ 0x94D049BB133111EB,
    lambda x: (x + 0x9E6C63D0676A9A99) & MASK,
]


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
        self._win = []          # per window: (result, nrec_walked, n_oob)
        self._oob = False
        if not self.truncated:
            self._run()

    # -- the window table (computed once) ----------------------------------
    def _window(self, off):
        """(result, records walked, out-of-table opcodes seen). Implementation
        1 of 2: an explicit cursor and an explicit subtraction-first guard, the
        way `c/kernel.c` and R2/R4 are written. `op_fold` below builds the same
        answer the way ../verus.rs's spec functions do.

        The third element is what `sanitizer_expect` is derived from: it counts
        the opcodes for which `c/kernel.c` loads a code pointer from past the
        end of `TABLE` and calls it. That is a question about the bytes, not
        about the file name."""
        if self.stride < HDR:
            return 0, 0, 0
        b = self.buf
        nrec = int.from_bytes(b[off:off + HDR], "little")
        if nrec == 0:
            return 0, 0, 0
        acc = 0
        p = HDR
        t = 0
        noob = 0
        while t < nrec:
            if self.stride - p < 2:
                break
            op = b[off + p]
            arg = b[off + p + 1]
            p += 2
            if op < NOPS:
                acc = OPS[op](acc ^ arg)
            else:
                noob += 1
                acc = (acc * 31 + SENT) & MASK
            t += 1
        return (acc * 31 + t) & MASK, t, noob

    # -- simulation --------------------------------------------------------
    def _run(self):
        acc = 0
        if 6 <= self.stride <= self.n_blob:
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
            # Over the windows the driver ACTUALLY VISITED -- an out-of-table
            # opcode in a window the Lemire index never selects is never
            # dispatched and no sanitizer can see it.
            self._oob = any(w is not None and w[2] for w in self._win)
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
    # ../verus.rs: `u32_at` with + and *, `op_spec` as an if-chain over the
    # opcode, and `run` as the abstract machine.
    def _u32_at(self, buf, p):
        return (buf[p] + 256 * buf[p + 1] + 65536 * buf[p + 2]
                + 16777216 * buf[p + 3])

    def _op_spec(self, i, x):
        """`op_spec` in ../verus.rs: the table AT THE SPECIFICATION LEVEL.

        The proof's whole difficulty is relating this if-chain to
        `TABLE@[i].spec_apply(x)`, i.e. to the dynamic type of the trait object
        sitting in slot `i` of a `const` array. ../NOTES.md 9 has the Verus
        errors that say so."""
        if i == 0:
            return x ^ 0x9E3779B97F4A7C15
        if i == 1:
            return x ^ 0xFF51AFD7ED558CCD
        if i == 2:
            return (x + 0x2545F4914F6CDD1D) & MASK
        if i == 3:
            return (x + 0xC4CEB9FE1A85EC53) & MASK
        if i == 4:
            return (x - 0x61C8864680B583EB) & MASK
        if i == 5:
            return (x - 0xBF58476D1CE4E5B9) & MASK
        if i == 6:
            return x ^ 0x94D049BB133111EB
        return (x + 0x9E6C63D0676A9A99) & MASK

    def _run_spec(self, buf, off, ln, t, nrec, p, acc):
        """`run` in ../verus.rs: the abstract machine. Iterative where the Verus
        function is recursive, for p11's, p14's, p27's, p47's, p38's and p22's
        reason (CPython's recursion limit)."""
        while not (t >= nrec or ln - p < 2):
            op = buf[off + p]
            arg = buf[off + p + 1]
            if op < NOPS:
                acc = self._op_spec(op, acc ^ arg)
            else:
                acc = (acc * 31 + SENT) & MASK
            t, p = t + 1, p + 2
        return (acc * 31 + t) & MASK

    def op_fold(self, buf, off, ln):
        """`op_fold` in ../verus.rs: what the kernel must return."""
        if ln < HDR:
            return 0
        nrec = self._u32_at(buf, off)
        if nrec == 0:
            return 0
        return self._run_spec(buf, off, ln, 0, nrec, HDR, 0)

    @property
    def helpers(self):
        return {"op_fold": self.op_fold}

    # -- what the kernel must do, per call ---------------------------------
    @property
    def work_unit(self):
        return "window byte"

    @property
    def work_unit_bits(self):
        return 8

    @property
    def work_per_call(self):
        """`stride` -- window bytes, the denomination fourteen other patterns
        use.

        **Which way this estimate errs: it OVER-counts on a window that
        declares fewer records than it carries**, because the kernel then stops
        at `nrec` and never reads the tail. `degenerate.bin`'s fourth window is
        the only shipped blob with that shape and it is not a
        `collapse.probe_input`; on `small.bin` and `large.bin` `nrec` equals the
        number of records present, so the kernel reads all `stride - 4` record
        bytes plus the 4-byte header, i.e. exactly `stride`."""
        return self._work if self.entered else 0

    # -- sanitizer expectation ---------------------------------------------
    @property
    def sanitizer_expect(self):
        """**"fires" on a window carrying an out-of-table opcode, "clean"
        elsewhere** -- and the DIAGNOSTIC IS ABOUT THE ARRAY READ, which is
        p36's central measurement rather than a footnote.

        Measured on the gate's own build (gcc -O1
        `-fsanitize=address,undefined -static-libasan -static-libubsan`,
        ../NOTES.md 0b): an out-of-table opcode produces

            runtime error: index 8 out of bounds for type '<unknown> *[8]'
            runtime error: load of address 0x... with insufficient space for an
                           object of type '<unknown> *'
            ERROR: AddressSanitizer: global-buffer-overflow ...
            0x... is located 0 bytes after global variable 'TABLE' ... of size 64

        Every line names the LOAD. **Nothing on this box names the control
        transfer**: clang's `-fsanitize=function` does, and gcc 13.3.0 does not
        implement it at all (`unrecognized argument to '-fsanitize=' option`),
        and even under clang it is defeated here because the loaded garbage is
        not a function and its prologue-signature read faults first.

        ⚠ **The declaration is "a sanitizer fires", NOT "the harm is
        identical".** It cannot be the second: under ASan the redzones move what
        is adjacent to `TABLE`, so one of the two out-of-table opcodes shipped
        returns normally with a wrong answer and exit 0 under the sanitizer
        build while the same opcode SIGSEGVs on all 8 plain cells. Stage 7's
        `expect == "fires"` branch requires only that a sanitizer reported, and
        that is exactly the bar the evidence supports."""
        return "fires" if self._oob else "clean"

    # -- what a conforming driver does -------------------------------------
    @property
    def expected_exit(self):
        return 5 if self.truncated else 0

    @property
    def expected_stdout(self):
        return "" if self.checksum is None else f"{self.checksum}\n"

    def describe(self):
        w0 = self._win[0] if self._win and self._win[0] else (0, 0, 0)
        return (f"n_iters={self.n_iters} stride={self.stride} "
                f"n_blob={self.n_blob} nwin={self.nwin} calls={self.n_calls} "
                f"work/call={self.work_per_call}B "
                f"nrec(w0)={w0[1]} oob(w0)={w0[2]} "
                f"san={self.sanitizer_expect} "
                f"truncated={self.truncated} expected={self.checksum}")

    def selfcheck(self):
        """The simulation against `op_fold`. They share no code: the simulation
        dispatches through the `OPS` lambda table with an explicit cursor, the
        helper walks an if-chain over the opcode the way the Verus spec function
        does and recomputes the header with `+`/`*`."""
        problems = []
        for c in self.sample_calls(8):
            want = self.op_fold(c["buf"], c["off"], c["len"])
            if want != c["result"]:
                problems.append(
                    f"simulated result {c['result']} != op_fold() {want} "
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
