#!/usr/bin/env python3
"""p08-overlap-move: the independent reference model the gate checks against.

The API is documented at the top of `patterns/p01-array-sum/model.py`; this file
notes only where p08 differs.

    bindings      buf/off/len/buf_len/result, the read-only shape p16, p17 and
                  p05 use. p08's kernel writes only its own 4096-byte local
                  scratch, which no caller can observe, so the buffer-before /
                  buffer-after bindings p02 needs have nothing to bind to here.
    work_per_call the WINDOW, in bytes -- i.e. `stride`, constant across every
                  call on a given input. **This estimate errs LOOSE, which is
                  p17's direction and NOT p16's or p05's**, and by a lot; the
                  docstring on `work_per_call` does the arithmetic.
    sanitizer     **"clean" on every input, and that is a measured finding
                  rather than a concession.** The overlap predicate itself is
                  derived (`any_overlap`: does some call hand `memcpy` two
                  ranges with `2*dr < m`) and is true on exactly one input --
                  but the gate's stage 7 builds with gcc, this box's gcc
                  default-enables `_FORTIFY_SOURCE=3`, and at that level the
                  move becomes `__memcpy_chk`, which ASan does not intercept.
                  Isolated to that one flag at TASK_014. See the
                  `sanitizer_expect` docstring; NOTES.md 5 carries the two
                  configurations in which the tool does see it.

Two independent implementations, as p01, p02, p16, p17 and p05 do:

  * the **simulation** builds each window's scratch with Python `bytearray`
    slice assignment (`scr[dr:m] = scr[0:m-dr]`, which is memmove semantics)
    and folds it with a loop, caching one result per window -- which is what
    makes 25 000 driver iterations tractable;
  * the **helper** `shift_fold` -- the one the derived `ensures` is evaluated
    against -- is a recursive walk mirroring the *Verus* spec functions
    `shift_round` / `shift_rounds` / `fold_scr` in ../verus.rs: each round
    rebuilds the whole 4096-element sequence element at a time with an
    index-conditional, and the fold is a recursion over the prefix. No slicing,
    no cache, no bytearray.

`selfcheck()` runs them against each other; a disagreement is reported there
rather than being silently absorbed into a green line.

**Both implementations model the CORRECT (memmove) kernel**, i.e. R1h and
R2-R5. R1 is the rung with the bug. It is expected to disagree on
`adversarial-overlap` **and measured not to**, because on glibc 2.39 / x86-64
`memcpy` and `memmove` are the same function (TASK_014 Part 0: `dlsym` returns
one address for both, and that function branches to a backward copy when
`dst - src < n`). The gate records the behaviour per rung rather than requiring
a divergence (`.memory/02-bench-rules.md`), so p08 stays green either way -- and
the *absence* of the divergence is p08's headline, not a defect in this model.

One arithmetic note that is easy to get wrong: `acc` is u64 and wraps mod 2^64;
`m` is folded in at the end so a rung that moved a different number of bytes
cannot land on the same checksum by accident. Python has no wrapping, so every
fold here masks explicitly.
"""

import itertools
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "common"))
import slb  # noqa: E402

MASK = (1 << 64) - 1
HDR = 4
SCR = 4096          # the kernel's scratch capacity; mirrored from ../spec.md


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
        self.any_overlap = False
        self.nwin = 0
        self._win = []          # per window: (result, r1_ranges_overlap)
        if not self.truncated:
            self._run()

    # -- the window table (computed once) ----------------------------------
    def _window(self, off):
        """(result, the_move_ranges_overlap) for the window at `off`.

        Implementation 1 of 2. Builds the scratch as a `bytearray` and does each
        round with a slice assignment, which Python defines as memmove
        semantics -- a completely different code path from the recursive
        `shift_fold` below.

        The second element records whether **any round's** source and
        destination ranges overlap, i.e. `2*dr < m`. That is exactly the
        condition under which R1's `memcpy` is undefined and ASan's
        `memcpy-param-overlap` interceptor fires. It is a property of the
        *arguments*, not of the memory that happens to be nearby, which is why
        it can be derived here at all -- unlike p05's out-of-bounds read, it
        does not depend on the allocator."""
        ln = self.stride
        if ln < HDR:
            return 0, False
        d = self.buf[off] + 256 * self.buf[off + 1]
        nrep_w = self.buf[off + 2] + 256 * self.buf[off + 3]
        avail = ln - HDR
        m = avail if avail < SCR else SCR
        nrep = 1 + nrep_w % 4
        if m < 2 or d == 0 or d + nrep > m:
            return 0, False
        over = any(2 * (d + r) < m for r in range(nrep))
        scr = bytearray(SCR)
        scr[0:m] = self.buf[off + HDR: off + HDR + m]
        for r in range(nrep):
            dr = d + r
            scr[dr:m] = scr[0:m - dr]          # memmove semantics
        acc = 0
        for j in range(m):
            acc = (acc * 31 + scr[j]) & MASK
        return (acc * 31 + m) & MASK, over

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
                    self.any_overlap = True
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
    # (../verus.rs `shift_round` / `shift_rounds` / `fold_scr`): each round
    # rebuilds the entire SCR-element sequence with a per-index conditional
    # rather than assigning a slice, and the fold is a recursion over the
    # prefix. Nothing here is a bytearray and nothing is cached.
    def _init_scr(self, buf, off, m):
        """`init_scr` in ../verus.rs: the zeroed scratch with the window's first
        `m` data bytes copied in."""
        return [buf[off + HDR + j] if j < m else 0 for j in range(SCR)]

    def _shift_round(self, s, dr, m):
        """`shift_round` in ../verus.rs -- ONE move, as a whole-sequence
        rebuild. Note the three regions: `[0, dr)` untouched, `[dr, m)` taking
        `s[j - dr]`, `[m, SCR)` untouched. Those are exactly the three `ensures`
        conjuncts of the trusted `move_right`."""
        return [s[j - dr] if dr <= j < m else s[j] for j in range(len(s))]

    def _shift_rounds(self, s, d, m, r):
        """`shift_rounds` in ../verus.rs: `r` rounds, round `q` shifting by
        `d + q`. Recursive, outermost round last, exactly as the Verus spec
        function recurses."""
        if r <= 0:
            return s
        return self._shift_round(self._shift_rounds(s, d, m, r - 1),
                                 d + r - 1, m)

    def _fold_scr(self, s, j):
        """`fold_scr` in ../verus.rs: the u64 Horner fold over `s[0..j]`.

        Written as a loop rather than a recursion even though the Verus spec
        function recurses, for the reason p05's `_row_fold` does: `j` runs to
        4089 and CPython's default recursion limit is 1000. `_shift_rounds`
        above stays recursive because its depth is `nrep <= 4`. The recursion
        that matters for independence from the simulation is the *shape of the
        computation* -- element at a time over a rebuilt list, with no slice
        assignment anywhere -- not the call mechanism."""
        acc = 0
        for q in range(j):
            acc = (acc * 31 + s[q]) & MASK
        return acc

    def shift_fold(self, buf, off, ln):
        """`shift_fold` in ../verus.rs: what the kernel must return."""
        if ln < HDR:
            return 0
        d = buf[off] + 256 * buf[off + 1]
        nrep_w = buf[off + 2] + 256 * buf[off + 3]
        avail = ln - HDR
        m = avail if avail < SCR else SCR
        nrep = 1 + nrep_w % 4
        if m < 2 or d == 0 or d + nrep > m:
            return 0
        s = self._shift_rounds(self._init_scr(buf, off, m), d, m, nrep)
        return (self._fold_scr(s, m) * 31 + m) & MASK

    @property
    def helpers(self):
        return {"shift_fold": self.shift_fold}

    # -- what the kernel must do, per call ---------------------------------
    @property
    def work_per_call(self):
        """The window, in bytes -- `stride` -- from the file alone.

        **Why the window, and which way the estimate errs.** `check.py` needs
        one scalar per input and hard-fails on `work <= 0`. The window is the
        unit that does not move, being fixed by the payload header and identical
        on every call of a given input; `m`, `d` and `nrep` are all attacker
        data.

        `.memory/02-bench-rules.md` asks which way the estimate errs and warns
        that the three patterns before p08 went three different ways. **p08 errs
        LOOSE, p17's direction, and by more than any of them**, because the
        kernel touches its scratch four times over:

            memset  SCR                       = 4096
            copy in m                         =  498 / 4089
            moves   4*(m - d) - 6             =  982 / 8170
            fold    m                         =  498 / 4089
            ------------------------------------------------
            total bytes touched               = 6074 / 20444
            work_per_call = stride            =  502 /  4093
            ratio                             = 12.1x / 5.0x

        So the derived floor of `0.25 * stride` = 125.5 / 1023.3 Ir per call is
        **12x / 5x looser than a byte-denominated estimate of the real traffic
        would make it**, before the fold's ~6.25 Ir per byte is counted at all.
        NOTES.md 7 reports the measured margin. This is the residual
        `.memory/02-bench-rules.md` documents and declines to close: the floor
        is a smoke test for total collapse, and what certifies that the work
        happened is step 2, the model checksum -- which here folds every byte of
        the scratch and mixes in `m`, so a rung that skipped a round or moved a
        different number of bytes cannot match it.

        No `min_ir_per_work` is declared, so the harness default of 0.25 Ir per
        byte applies unchanged, and on p08 that argument is easy in a way p05's
        was not: **the fold is a serial Horner chain**, `acc = acc*31 + b`, with
        a hard 3-cycle loop-carried dependence and no vector form -- p16's and
        p17's argument, which p05 could not use. Measured at TASK_014, `-O3`,
        the fold alone is 25 instructions per 4 bytes = 6.25 Ir/byte in every
        Rust rung, 25x the floor. The `memmove` calls *are* below the floor
        (glibc moves a byte in ~0.104 Ir, `.memory/03-measurement.md`), which is
        precisely why the floor is denominated in the window rather than in
        bytes moved."""
        return self.stride if self.entered else 0

    # -- sanitizer expectation ---------------------------------------------
    #
    # `self.any_overlap` is the property the pattern is about: **does some call
    # hand `memcpy` two ranges that overlap**, i.e. `2*dr < m` for some round of
    # some window the driver selects. It is a property of the *arguments*, not
    # of the memory that happens to be nearby, which is why it can be derived
    # here at all -- unlike p05's out-of-bounds read it does not depend on the
    # allocator. It is true on exactly one input, `adversarial-overlap`, and it
    # is what `describe()` prints and what NOTES.md 5's detection table is
    # organised around.
    #
    # **It is deliberately NOT what `sanitizer_expect` returns, and the reason
    # is a measurement rather than a judgement.** See the docstring below.
    @property
    def sanitizer_expect(self):
        """"clean" on every input -- **measured, not assumed, and it is a
        finding rather than a concession.**

        `harness/check.py` stage 7 builds `c/kernel.c` with `gcc -O1
        -fsanitize=address,undefined`. This box's gcc default-enables
        `_FORTIFY_SOURCE=3` (`.memory/00-environment.md`), and at fortify level
        3 the move `memcpy(scr + dr, scr, m - dr)` -- whose destination has a
        computable `__builtin_dynamic_object_size` of `4096 - dr` -- is rewritten
        to **`__memcpy_chk`**. ASan's `memcpy-param-overlap` check lives in its
        `memcpy` interceptor, and **ASan does not intercept `__memcpy_chk`**, so
        the check never runs.

        Isolated to that one flag at TASK_014, same source, same everything else:

            gcc -O1 -fsanitize=address,undefined  (fortify 3, the gate's build)
                kernel calls __memcpy_chk@plt      -> SILENT, exit 0
            gcc ... -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=0
                kernel calls __interceptor_memcpy  -> AddressSanitizer:
                                                      memcpy-param-overlap
            clang -O1 -fsanitize=address,undefined (clang does not fortify)
                                                   -> memcpy-param-overlap

        So a **hardening feature disables a sanitiser check**, and stage 7 --
        gcc-only by construction -- is structurally blind to any `mem*`/`str*`
        misuse whose call site gcc rewrites to a `_chk` form. That is a harness
        observation, reported rather than worked around; `controls/
        gen_controls.py` builds the two visible configurations and NOTES.md 5
        carries their output, so the security half of p08 rests on a measurement
        and not on this line.

        Returning "clean" here therefore states what is true of the build the
        gate actually runs. **If the harness ever adds `-D_FORTIFY_SOURCE=0` or
        a clang ASan column to stage 7, this must become
        `"fires" if self.any_overlap else "clean"`** -- the overlap predicate is
        computed above and kept for exactly that reason.

        Note that "clean" is also the *strict* declaration of the two: it makes
        any diagnostic on any input a gate failure, so nothing is being waved
        through. What is lost is the assertion that the bug is exercised, and
        that assertion is made in NOTES.md 5 with tool output instead."""
        return "clean"

    # -- what a conforming driver does -------------------------------------
    @property
    def expected_exit(self):
        # p08's payload allocates nothing from an attacker-controlled size --
        # the scratch is a fixed 4096-byte array local to the kernel, not a
        # driver-owned buffer -- so p02's exit 7 has no analogue here, exactly
        # as for p16, p17 and p05. `slb_load` rejecting a short file is the only
        # non-zero exit this pattern's driver produces.
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
        """bytearray-slice simulation vs the recursive whole-sequence rebuild
        that mirrors the Verus spec functions."""
        problems = []
        for c in self.sample_calls(4):
            want = self.shift_fold(c["buf"], c["off"], c["len"])
            if want != c["result"]:
                problems.append(
                    f"simulated result {c['result']} != shift_fold() {want} at "
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
