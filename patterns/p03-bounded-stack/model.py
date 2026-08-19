#!/usr/bin/env python3
"""p03-bounded-stack: the independent reference model the gate checks against.

The API is documented at the top of `patterns/p01-array-sum/model.py`; this file
notes only where p03 differs.

    bindings      buf/off/len/buf_len/result, the read-only shape p16, p17, p05,
                  p07 and p11 use. p03's kernel writes only its own local stack.
    work_per_call **bytes of the window** -- `stride`. Every byte of a
                  well-formed window is read exactly once: the 4 header bytes as
                  a u32, then the op byte and the four value bytes of each
                  operation. See the property's docstring for the direction of
                  the error.
    work_unit     "byte"; `work_unit_bits` 8.
    sanitizer     derived, not tabulated: an input is "fires" exactly when the
                  simulated run contains a call in which R1 -- the rung with no
                  `sp > 0` guard -- would execute a POP with `sp == 0`. That
                  read is `stack[SIZE_MAX]`, which wraps to `stack - 1`: 8 bytes
                  below a 512-byte stack array, inside the kernel's own frame.
                  It does not fault (../NOTES.md 7) and ASan reports
                  `stack-buffer-underflow`.

Two independent implementations, as p01, p02, p16, p17, p05, p07 and p11 do:

  * the **simulation** `_window` keeps the stack as a Python **list** with
    `append` and `pop`, decodes the value with `int.from_bytes`, and is written
    the way one would write the kernel if one had a growable stack -- a
    different code path in every respect that matters;
  * the **helper** `stack_fold` -- the one the derived `ensures` is evaluated
    against -- mirrors the Verus spec function `run` in ../verus.rs: a
    fixed-length list of `STACK_CAP` slots, an explicit integer `sp`, every
    index written out, and the header and value decoded by `_u32_at`'s
    written-out `b0 + 256*b1 + 65536*b2 + 16777216*b3` rather than by
    `int.from_bytes`.

    It is **iterative where the Verus function is recursive**, and that is a
    deliberate deviation rather than an oversight: `run` recurses once per
    operation and p03's windows hold up to 830 operations, which is close to
    CPython's default recursion limit and would exceed it on a bigger window.
    The two are otherwise transliterations, including `run`'s ordering of the
    two guards.

`selfcheck()` runs them against each other; a disagreement is reported there
rather than being silently absorbed into a green line.

**Both implementations model the CHECKED kernel**, i.e. R1h and R2-R5. R1 is the
rung with the bug and is expected to disagree on `adversarial-underflow` and
`adversarial-allpop`; the gate records that disagreement in its behaviour table
rather than requiring it to vanish (`.memory/02-bench-rules.md`).

**Neither implementation trusts `nops`**, and neither does ../verus.rs. What
bounds the walk is the length check `5*nops > avail`, which is in *every* rung
including R1 -- `adversarial-count.bin` is the row that shows it -- and what
bounds the stack is `sp < STACK_CAP` on the push, also in every rung
(`adversarial-overflow.bin`). The **only** thing R1 omits is `sp > 0`.

Two arithmetic notes that are easy to get wrong and are load-bearing:

  * the result is `(acc*31 + sp)*31 + nops`, so a rung that ended at a different
    stack depth, or ran a different number of operations, cannot produce the
    same checksum even if it folded the same values. Python has no wrap, so
    every step masks explicitly.
  * a POP on an empty stack is a **no-op** in the checked semantics -- `acc` and
    `sp` are both unchanged -- and is *not* an error and *not* a rejection.
    `adversarial-allpop.bin` is the row where every checked rung therefore
    returns `(0*31 + 0)*31 + nops == nops`.
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
STACK_CAP = 64            # the same compile-time constant every rung carries


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
        self.any_underflow = False
        self.nwin = 0
        self._work = 0
        self._win = []          # per window: (result, r1_would_underflow, xpops)
        if not self.truncated:
            self._run()

    # -- the window table (computed once) ----------------------------------
    def _window(self, off):
        """(result, R1_would_pop_an_empty_stack, executed_pops) for the window.

        Implementation 1 of 2. The stack is a Python **list** with `append` and
        `pop`, the value is decoded with `int.from_bytes`, and emptiness is
        tested with `if st:` -- none of which the byte-at-a-time `stack_fold`
        below does.

        The second element records whether the rung with **no** emptiness guard
        -- R1 -- would execute `sp -= 1` at `sp == 0`. That is a read 8 bytes
        below a local array and is what ASan reports; it is a property of the
        *op stream*, not of the buffer, so unlike p11's overrun it does not
        depend on where the window sits in the blob."""
        ln = self.stride
        if ln < HDR:
            return 0, False, 0
        buf = self.buf
        nops = int.from_bytes(buf[off:off + 4], "little")
        if nops == 0:
            return 0, False, 0
        if OPLEN * nops > ln - HDR:
            return 0, False, 0
        st = []
        acc = 0
        xpops = 0
        under = False
        for k in range(nops):
            base = off + HDR + OPLEN * k
            if buf[base] == 0:
                if len(st) < STACK_CAP:
                    st.append(int.from_bytes(buf[base + 1:base + 5], "little"))
            else:
                if st:
                    acc = (acc * 31 + st.pop()) & MASK
                    xpops += 1
                else:
                    under = True
        return ((acc * 31 + len(st)) * 31 + nops) & MASK, under, xpops

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
                r, under, _xp = self._win[k]
                if under:
                    self.any_underflow = True
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
            r, _under, _xp = self._win[k]
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
    # (../verus.rs `run`): a fixed-length slot list, an explicit `sp`, every
    # index written out, no `append`, no `pop`, no `int.from_bytes`, no cache.
    def _u32_at(self, buf, p):
        """`u32_at` in ../verus.rs, written out with `+` and `*` exactly as the
        rungs write it -- not `int.from_bytes`, which is the simulation's."""
        return (buf[p] + 256 * buf[p + 1] + 65536 * buf[p + 2]
                + 16777216 * buf[p + 3])

    def _run_spec(self, buf, off, nops):
        """`run` in ../verus.rs. Iterative rather than recursive -- see the
        module docstring; every other line is a transliteration."""
        stack = [0] * STACK_CAP
        sp = 0
        acc = 0
        k = 0
        while k < nops:
            val = self._u32_at(buf, off + 5 + 5 * k)
            if buf[off + 4 + 5 * k] == 0:
                if sp < STACK_CAP:
                    stack[sp] = val
                    sp = sp + 1
            else:
                if sp > 0:
                    sp = sp - 1
                    acc = (acc * 31 + stack[sp]) & MASK
            k = k + 1
        return ((acc * 31 + sp) * 31 + nops) & MASK

    def stack_fold(self, buf, off, ln):
        """`stack_fold` in ../verus.rs: what the kernel must return."""
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
        return {"stack_fold": self.stack_fold}

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
        both directions because p16 errs strict, p17 loose and p05 strict, and
        three patterns gave three answers).

          * *over*-count, and it is the only term that can go that way: a
            **POP** operation reads its op byte and does not read its four value
            bytes at all -- LLVM and gcc both sink that load into the push arm,
            which ../NOTES.md 0 checked on the disassembly before this file was
            written. So a window whose ops are all POPs visits `4 + nops` bytes
            where `stride` counts `4 + 5*nops`.
          * *under*-count: none. Every other byte is read exactly once and the
            stack traffic is not counted at all.

        The over-count is bounded by the pop density, which is 50% on `small`
        and 25% on `large`, so `stride` is at most 2x the number of byte-visits
        and the derived floor is one the kernel must clear. It can therefore
        never let a collapsed kernel through, which is the only direction that
        matters -- and the measured margin (../NOTES.md 8b) says by how much.

        No `min_ir_per_work` is declared, so the harness default of 0.25 Ir per
        byte applies unchanged. The argument for it here is the easiest of any
        pattern so far: p03's inner loop is a **data-dependent two-way branch on
        an attacker byte** followed by a serial dependence through `sp` and
        `acc`, so there is no vector form at any `-march` -- operation `k+1`
        cannot even be *decoded* into the right arm until operation `k`'s effect
        on `sp` is known. The measured rate is 12.50 Ir per 5-byte operation on
        the unsafe rung, i.e. 2.50 Ir/byte, 10x the floor."""
        return self._work if self.entered else 0

    # -- sanitizer expectation ---------------------------------------------
    @property
    def sanitizer_expect(self):
        """Derived from the simulated run, never tabulated per file.

        R1 has no `sp > 0` guard, so it is a memory error exactly when some
        operation is a POP at `sp == 0`. `sp` is `size_t`, so `sp - 1` is
        `SIZE_MAX` and `stack + SIZE_MAX` wraps to `stack - 1`: the read is 8
        bytes below a 512-byte local array, **inside the kernel's own stack
        frame**. ../NOTES.md 0 establishes that arithmetic on the disassembly
        and ../NOTES.md 7 records what each build does with it.

        Unlike p11's, this predicate is a property of the **op stream alone**
        and not of where the window sits in the blob, because the address that
        goes out of range is on the stack rather than in the payload. Every
        adversarial input is still a single window, for the reason
        `inputs/gen.py` records.

        This returns "fires" for **two** inputs and they are different harms.
        `adversarial-underflow` pops once at `sp == 0` and thereby disables the
        stack for the rest of the call -- `sp` becomes `SIZE_MAX`, so
        `sp < STACK_CAP` is false for every later PUSH. `adversarial-allpop`
        does it `nops` times and walks one slot further down the stack each
        time. `adversarial-overflow` and `adversarial-count` are the controls:
        both attack a check that IS in R1, and both are clean in every rung."""
        return "fires" if self.any_underflow else "clean"

    # -- what a conforming driver does -------------------------------------
    @property
    def expected_exit(self):
        # p03's payload allocates nothing from an attacker-controlled size --
        # there is no `cap` word and no `slb_zeroed` -- so p02's exit 7 has no
        # analogue here, exactly as for p16, p17, p05, p07 and p11. `slb_load`
        # rejecting a short file is the only non-zero exit this driver produces.
        return 5 if self.truncated else 0

    @property
    def expected_stdout(self):
        return "" if self.checksum is None else f"{self.checksum}\n"

    def describe(self):
        xp = self._win[0][2] if self._win and self._win[0] else 0
        return (f"n_iters={self.n_iters} stride={self.stride} "
                f"n_blob={self.n_blob} nwin={self.nwin} calls={self.n_calls} "
                f"work/call={self.work_per_call}B win0_xpops={xp} "
                f"san={self.sanitizer_expect} "
                f"truncated={self.truncated} expected={self.checksum}")

    def executed_pops(self, off):
        """Executed POPs in the window at `off` -- the regressor ../NOTES.md 4's
        laws are linear in. Exposed so the sweep scripts do not have to
        re-implement the guard."""
        return self._window(off)[2]

    def selfcheck(self):
        """list/append/pop simulation vs the fixed-slot walk that mirrors the
        Verus spec function."""
        problems = []
        for c in self.sample_calls(8):
            want = self.stack_fold(c["buf"], c["off"], c["len"])
            if want != c["result"]:
                problems.append(
                    f"simulated result {c['result']} != stack_fold() {want} "
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
