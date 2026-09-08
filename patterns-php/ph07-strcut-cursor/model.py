#!/usr/bin/env python3
"""ph07-strcut-cursor: the independent reference model the gate checks against.

The API is documented at the top of `patterns/p01-array-sum/model.py`; this file
notes only where ph07 differs.

    bindings      buf/off/len/buf_len/result. The kernel writes only into its
                  own `mbfl_malloc`'d result, which is freed before the kernel
                  returns, so there is no destination to bind before and after.
                  What escapes the call is the u64.
    work_per_call the WINDOW, in bytes -- `stride`, constant across every call
                  on a given input. Argued below.
    sanitizer     derived, not tabulated: an input "fires" exactly when some
                  call the driver actually makes would make R1's START WALK
                  read past `string->val[string->len]`.

⚠⚠ WHICH ALGORITHM THIS MODEL IMPLEMENTS, BECAUSE IT IS NOT R1's. It is
`mbfl_strcut`'s mblen_table arm **with `cb3cca21b345` applied in the caller**,
which is exactly `c/kernel_hardened.c` and exactly R2-R5:

    R1     mbfilter.c:1179-1259 as shipped 5.0.0 .. 5.3.2 -- CRASH-124
    R1h    + cb3cca21b345 (2005-12-15, ext/mbstring/mbstring.c), both guards
    R2-R5  the same function, memory-safe

⭐ Unlike ph03, the upstream fix here is COMPLETE: over 133 932 interpreted
calls its hunk (a) removes every one of the 15 333 out-of-bounds reads and
leaves no residue (controls/fix_scope.py). So R1h and R2-R5 implement one
function and only R1 diverges.

⚠ **The fix is in the CALLER, in another file** -- `PHP_FUNCTION(mb_strcut)`,
not `mbfl_strcut` -- which is why `mbfl_strcut`'s body is byte-identical from
php-5.0.0 to php-5.3.2. This model puts both guards where `guard()` already
put mbstring.c's other two, because that function is a frame this row lifts.
NOTES.md §4.

Two independent implementations, as p01/p02/p16 and ph03 do:

  * the **simulation** (`_window`) walks each window once with imperative
    loops over integer cursors and returns the folded result. Per-window
    results go in a table, which is what makes 25 000 driver iterations
    tractable;
  * the **helper** `strcut_fold` -- the one the derived `ensures` is evaluated
    against -- is built out of RECURSIVE walks with no cursor variable and no
    table, mirroring the Verus spec functions `walk_start` / `walk_end` /
    `fold_out` in ../verus.rs.

`selfcheck()` runs them against each other -- on the shipped inputs AND on
synthetic windows it builds itself over a domain no input file contains --
and a disagreement is reported there rather than absorbed into a green line.

⚠⚠ **THE SYNTHETIC SWEEP IS NOT DECORATION.** `PROTOCOL_PHP.md` §A2a rule 2:
*a second implementation is only as strong as the domain it is exercised over,
and `inputs/` is not a domain -- it is a handful of files.* ph03 shipped for a
full task with its two implementations computing different functions because
its corpus took one arm of a two-armed branch. Here the branch is
`m = mbtab[*p]`, whose arms are the lead-byte classes; `inputs/gen.py` asserts
the corpus reaches all six, and this sweep drives both implementations over
`from` and `length` ranges the corpus cannot carry at a fixed stride.
"""

import itertools
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "common"))
import slb  # noqa: E402

MASK = (1 << 64) - 1

# `php_shim_tally()`'s multipliers -- common-php/emalloc_shim.h:644-647.
T_ALLOC, T_FREE, T_HIT, T_BYTES = 1000003, 1000033, 1000037, 1000039

# ext/mbstring/libmbfl/filters/mbfilter_utf8.c:39-56, as the run-length the
# literal table encodes. `selfcheck()` check 5 re-derives the 256 entries from
# c/kernel.c's own text, so this cannot drift away from the C.
MBTAB = tuple(([1] * 192) + ([2] * 32) + ([3] * 16)
              + ([4] * 8) + ([5] * 4) + ([6] * 2) + ([1] * 2))
assert len(MBTAB) == 256


def guard(slen, frm, length):
    """`PHP_FUNCTION(mb_strcut)`'s two clamps -- ext/mbstring/mbstring.c:1787-1805.

    ⚠ This is the GUARD frame, not the defect frame (`.memory-php/01` F1). It
    clamps `from` FROM BELOW and never from above, which is the whole reason
    CRASH-124 exists. It lives in the kernel wrapper (c/kernel.c) because it
    decides the kernel's domain: without it a negative `from` would reach the
    walk, which `mb_strcut` cannot produce.

    ⭐ It is also the function `cb3cca21b345` PATCHES: the real upstream fix
    adds two more lines immediately after these, in this same function, in
    ext/mbstring/mbstring.c -- not in `mbfl_strcut`. So the repair site and the
    guard site are the SAME frame here, and neither is the defect site."""
    if frm < 0:
        frm = slen + frm
        if frm < 0:
            frm = 0
    if length < 0:
        length = (slen - frm) + length
        if length < 0:
            length = 0
    return frm, length


def tally(cap):
    """`php_shim_tally()` after one `php_shim_reset` + one `emalloc(cap)` + one
    `efree`, which is exactly what one kernel call does.

    `n_alloc = 1`, `n_free = 1`, `n_cache_hit = 0` (the reset empties the
    size-class cache, so the request always misses), and `bytes_mallocked` is
    the TRUNCATED `real_size`, i.e. `(cap + 7) & ~7` --
    `common-php/emalloc_shim.h:217`, `:352`, truncation T1. `cap = n + 8` with
    `n <= string->len`, so `cap` never approaches 2^32 and T1/T2/T3 do not
    fire; that is the row's `emalloc_dependent: false` (../spec.md)."""
    real_size = (cap + 7) & ~7
    return ((1 * T_ALLOC) ^ (1 * T_FREE) ^ (0 * T_HIT)
            ^ ((real_size * T_BYTES) & MASK)) & MASK


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
        self.any_oob = False          # some call makes R1 read past val[slen]
        self.nwin = 0
        self._win = []                # per window: (result, r1_oob)
        if not self.truncated:
            self._run()

    # -- the window table (computed once) ----------------------------------
    @staticmethod
    def _unpack(win):
        """(from, length, s, slen) for one window's bytes.

        `s` is the whole zval buffer -- `slen` string bytes plus the NUL
        terminator at index `slen` -- because that is what `string->val`
        points at in PHP and the terminator is a byte the walk may legally
        read (c/kernel.h)."""
        frm = int.from_bytes(win[0:4], "little", signed=True)
        length = int.from_bytes(win[4:8], "little", signed=True)
        s = win[8:]
        return frm, length, s, len(s) - 1

    def _window(self, off):
        """(result, r1_reads_oob) for the window at `off`.

        Implementation 1 of 2. An imperative transcription of
        `c/kernel_hardened.c` -- cursors `n`, `start`, `end` exactly as the C
        names them -- plus a second pass that asks whether **R1**, which has no
        clamp, would have read past `s[slen]`."""
        win = self.buf[off: off + self.stride]
        frm, length, s, slen = self._unpack(win)
        frm, length = guard(slen, frm, length)

        r1_oob = self._r1_reads_oob(s, slen, frm)

        # ---- cb3cca21b345, mbstring.c, THE REAL UPSTREAM FIX -------------
        if frm > slen:                                   # hunk (a) RETURN_FALSE
            return 0xFFFFFFFF, r1_oob                    # tally is 0: no alloc
        if frm + length > slen:                          # hunk (b)
            length = slen - frm
        # ---- mbfilter.c:1196-1223, the two walks ------------------------
        n = 0
        start = 0
        while True:
            m = MBTAB[s[n]]
            n += m
            if n > frm:
                break
            start = n
        k = start + length
        if k >= slen:
            end = slen
        else:
            end = start
            while n <= k:
                end = n
                m = MBTAB[s[n]]
                n += m
        # ---- mbfilter.c:1227-1241, the clamps ---------------------------
        if start > slen:
            start = slen
        if start < 0:
            start = 0
        if end > slen:
            end = slen
        if end < 0:
            end = 0
        if start > end:
            start = end
        # ---- mbfilter.c:1243-1256, allocate and copy --------------------
        n = end - start
        cap = n + 8
        acc = 0
        for b in s[start:end]:
            acc = (acc * 31 + b) & MASK
        acc = (acc * 31 + n) & MASK
        return acc ^ tally(cap), r1_oob

    @staticmethod
    def _r1_reads_oob(s, slen, frm):
        """Would R1 -- the unclamped 5.0.0 walk -- read past `s[slen]`?

        ⚠ This is the ONE place the model reasons about R1 rather than about
        the function every other rung implements, and it is what makes
        `sanitizer_expect` a derivation instead of a table. It walks with
        OFFSETS, so it records an access it does not perform.

        ⚠⚠ It is also why the answer is well defined at all. Past `s[slen]` the
        C reads whatever the heap holds, so R1's *trajectory* depends on
        uninitialised memory -- but only its trajectory. `start` is assigned
        the cursor of the iteration BEFORE the break, so the first
        out-of-bounds read at index `i > slen` happens with `start == i > slen`
        already set, and `start` only grows; the clamp at mbfilter.c:1227 then
        forces `start = slen`, `end = slen` and an empty result. **So R1's
        RETURN VALUE is deterministic on every input, over-reading or not** --
        which is exactly why this defect survived six releases, and why the
        gate can compare R1's checksum at all. NOTES.md §6."""
        n = 0
        while True:
            if n > slen:
                return True
            m = MBTAB[s[n]]
            n += m
            if n > frm:
                return False

    # -- simulation --------------------------------------------------------
    def _run(self):
        acc = 0
        if 9 <= self.stride <= self.n_blob:
            self.entered = True
            self.nwin = self.n_blob // self.stride
            self._win = [self._window(k * self.stride) for k in range(self.nwin)]
            for _ in range(self.n_iters):
                k = (acc * self.nwin) >> 64
                r, oob = self._win[k]
                if oob:
                    self.any_oob = True
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
    # This is what the derived `ensures` is evaluated against, so it must not be
    # the simulation in disguise. It mirrors the *Verus* spec functions
    # (../verus.rs `walk_start` / `walk_end` / `fold_out`): RECURSIVE where
    # `_window` is iterative, carrying `(n, start)` as a returned pair rather
    # than as mutable cursors, and with the two walks split into two functions
    # so that the second one's BOUND -- the thing the first walk does not have
    # -- is a parameter and not a comment.
    @staticmethod
    def _fix(step, state):
        """Drive a TAIL-RECURSIVE spec function to its fixpoint.

        ⚠ Why this and not Python recursion. ../verus.rs's `walk_start` and
        `walk_end` are tail-recursive `spec fn`s and each recursive call is one
        application of a transition; writing the transitions as pure functions
        and driving them here mirrors those definitions one for one, and it
        does not recurse `from` deep -- `large.bin`'s window is 4 065 string
        bytes, which would be 4 065 Python frames and a `RecursionError` on the
        default limit. The state's last element is the terminal flag."""
        while not state[-1]:
            state = step(state)
        return state

    @staticmethod
    def _start_step(s, frm):
        """One application of `walk_start` -- mbfilter.c:1202-1210, clamped.

        Terminates because every table entry is >= 1, so `n` strictly
        increases and `frm + 1 - n` strictly decreases. In Verus that is a
        `decreases` clause and `lemma_mbtab_pos` is what discharges it."""
        def step(st):
            n, start, _ = st
            m = MBTAB[s[n]]
            if n + m > frm:
                return (n + m, start, True)
            return (n + m, n + m, False)
        return step

    @staticmethod
    def _end_step(s, k):
        """One application of `walk_end` -- mbfilter.c:1217-1222.

        ⭐ The bound is `k`, and the caller only enters this at all when
        `k < string->len`, so every `s[n]` it reads is in range. **This walk is
        guarded and the start walk is not**, in adjacent lines of one function.
        That asymmetry is the row (NOTES.md §5)."""
        def step(st):
            n, end, _ = st
            if n > k:
                return (n, end, True)
            return (n + MBTAB[s[n]], n, False)
        return step

    def strcut_fold(self, buf, off, ln):
        """`strcut_fold` in ../verus.rs: what the kernel must return."""
        frm, length, s, slen = self._unpack(buf[off: off + ln])
        frm, length = guard(slen, frm, length)
        if frm > slen:
            return 0xFFFFFFFF
        if frm + length > slen:
            length = slen - frm
        n, start, _ = self._fix(self._start_step(s, frm), (0, 0, False))
        k = start + length
        if k >= slen:
            end = slen
        else:
            _, end, _ = self._fix(self._end_step(s, k), (n, start, False))
        start = min(max(start, 0), slen)
        end = min(max(end, 0), slen)
        start = min(start, end)
        acc = 0
        for b in s[start:end]:
            acc = (acc * 31 + b) & MASK
        acc = (acc * 31 + (end - start)) & MASK
        return acc ^ tally((end - start) + 8)

    @property
    def helpers(self):
        return {"strcut_fold": self.strcut_fold}

    # -- what the kernel must do, per call ---------------------------------
    @property
    def work_per_call(self):
        """The window, in bytes -- `stride` -- from the file alone.

        **Why the window and not `from + length`.**
        `check.py::check_marginal_ir` needs one scalar per input and hard-fails
        on `work_per_call = 0`. The bytes this kernel actually touches are
        `from` (the start walk) plus up to `length` (the end walk) plus
        `end - start` (the copy), and all three are read OUT OF THE DATA --
        denominating in them would put the unit under the attacker's control
        and collapse it to a constant on `adversarial-nowin.bin`.

        The window is the unit that does not move. It is fixed by the payload
        header, identical on every call of a given input, and `inputs/gen.py`
        draws `from` and `length` as FIXED FRACTIONS of the window so the work
        really does scale with it. It is a strict over-estimate -- no call
        walks the whole window twice -- and an over-estimate raises the derived
        floor, which is the direction a floor should err."""
        return self.stride if self.entered else 0

    # -- sanitizer expectation ---------------------------------------------
    @property
    def sanitizer_expect(self):
        """Derived from the simulated run, never tabulated per file.

        A call on which R1's start walk passes `s[slen]` is exactly a call on
        which R1 -- which has no clamp -- reads past the zval buffer. So "the
        simulation says some call this input actually makes over-reads" *is*
        "ASan must report on this input".

        Note "actually makes": the driver picks windows from a checksum-derived
        index, so a hostile window that is never selected must not be declared.
        That is why every adversarial input that declares `fires` has exactly
        one window -- see inputs/gen.py. (`adversarial-nowin.bin` has ZERO,
        which is its whole point, and declares `clean`.)

        ⚠ There is no ph03-style residue here: the clamp closes every case, so
        this property is about R1 alone and `check.py` stage 7h's demand that
        R1h be clean on every input is a demand this row can meet."""
        return "fires" if self.any_oob else "clean"

    # -- what a conforming driver does -------------------------------------
    @property
    def expected_exit(self):
        # ph07's payload allocates nothing from an attacker-controlled size --
        # `mbfl_malloc((n + 8))` is bounded by the window because `n` is clamped
        # first -- so p02's exit 7 has no analogue here. `slb_load` rejecting a
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

    # -- driving BOTH implementations on a window no input file contains ----
    @staticmethod
    def _both(win):
        """(simulated, strcut_fold) for an arbitrary window, off-corpus.

        `Model.__new__` skips `__init__` deliberately: `_window` and
        `strcut_fold` read only `buf` and `stride`, so this drives the SHIPPED
        code paths on bytes chosen here rather than on bytes `inputs/` happens
        to carry. That is the entire mechanism behind `selfcheck` check 1b."""
        m = Model.__new__(Model)
        m.buf, m.stride = win, len(win)
        return m._window(0)[0], m.strcut_fold(win, 0, len(win))

    @staticmethod
    def _synthetic_windows():
        """Windows spanning a domain `inputs/` cannot, built here, yielded as
        (label, bytes). ⚠ **`inputs/` is not the domain and must never be
        mistaken for it** -- see the module docstring.

        Four families, each isolating one thing the two implementations could
        disagree about:

          a. every lead-byte CLASS the table has (1,2,3,4,5,6 bytes) crossed
             with every `from` in `0 ..= slen + 3` -- the axis the corpus
             cannot span, because a window's stride is fixed and `from` is
             drawn as a fraction of it;
          b. `length` across the `k >= string->len` / `k < string->len` split,
             which is the *guarded* walk's branch and therefore the one place a
             recursive `walk_end` and an iterative one can come apart;
          c. the empty string, `slen = 0`, where `s` is one NUL byte and the
             walk's first read is already the terminator;
          d. negative `from` and negative `length`, which the wrapper's
             mbstring.c clamps are supposed to absorb -- so a model that
             forgot one of them shows up here and nowhere else."""
        fams = {
            "asc": bytes(0x41 + (i % 26) for i in range(24)),
            "b2":  bytes((0xC3, 0xA9) * 12),
            "b3":  bytes((0xE3, 0x81, 0x82) * 8),
            "b4":  bytes((0xF0, 0x9F, 0x98, 0x80) * 6),
            "b5":  bytes((0xF8, 1, 2, 3, 4) * 5),
            "b6":  bytes((0xFC, 1, 2, 3, 4, 5) * 4),
            "mix": bytes(b"a\xc3\xa9\xe3\x81\x82b\xf0\x9f\x98\x80c" * 2),
        }
        for name, body in fams.items():
            for slen in (0, 1, 3, 7, 12, 24):
                s = bytes(body[:slen]) + b"\0"
                for frm in range(0, slen + 4):
                    for length in (0, 1, slen // 2, slen, slen + 2):
                        yield (f"{name} slen={slen} from={frm} len={length}",
                               frm.to_bytes(4, "little", signed=True)
                               + length.to_bytes(4, "little", signed=True) + s)
                for frm, length in ((-1, 2), (-slen, -1), (-slen - 3, -slen - 3),
                                    (2, -1), (0, -slen - 1)):
                    yield (f"{name} slen={slen} NEG from={frm} len={length}",
                           frm.to_bytes(4, "little", signed=True)
                           + length.to_bytes(4, "little", signed=True) + s)

    def selfcheck(self):
        """Five checks, and four of them are about this row specifically.

        1a. the imperative simulation against the recursive `strcut_fold`, on
            the calls this input actually makes;
        1b. ⚠⚠ the same two implementations on **synthetic windows this file
            builds**, spanning every lead-byte class, `from` past the end, and
            both signs of both parameters. `PROTOCOL_PHP.md` §A2a rule 2 --
            1a alone is what let ph03 ship a model that computed a different
            function from its own proof for a whole task;
        2.  every window's `(from, length)` is non-negative AND satisfies
            `from + length <= string->len` after the wrapper's mbstring.c
            clamps, which is what makes `d9dda48f8a7e`'s
            `from < 0 || length < 0` hunk dead rather than merely unexercised;
        3.  every window's result is reproduced by a THIRD, deliberately dumb
            spelling of the answer -- `s[start:end]` recomputed from the walk's
            own definition of `start` -- so a fold that silently changed range
            is caught;
        4.  the walk's termination premise, `MBTAB[b] >= 1 for every b`. It is
            what `../verus.rs::lemma_mbtab_pos` proves and what the whole
            `decreases` argument rests on; a table with a zero entry makes the
            start walk spin forever and the model recurse to death;
        5.  ⚠ `MBTAB` here still equals the 256 numbers in `c/kernel.c`. This
            file writes the table as a run-length and the C writes it as a
            literal; check 5 parses the C and compares, so the two spellings
            cannot drift apart in this file's own head."""
        problems = []
        for c in self.sample_calls(8):
            want = self.strcut_fold(c["buf"], c["off"], c["len"])
            if want != c["result"]:
                problems.append(
                    f"simulated result {c['result']} != strcut_fold() {want} "
                    f"at off={c['off']}")
                break
        for label, win in self._synthetic_windows():
            sim, helper = self._both(win)
            if sim != helper:
                problems.append(
                    f"synthetic window [{label}]: simulated {sim} != "
                    f"strcut_fold() {helper}. The two implementations have come "
                    f"apart OFF the corpus; inputs/ cannot see this and it is "
                    f"why this sweep exists (PROTOCOL_PHP.md A2a rule 2)")
                break
        adversarial = os.path.basename(self.path).startswith("adversarial")
        for k in range(0 if adversarial else self.nwin):
            frm, length, s, slen = self._unpack(
                self.buf[k * self.stride:(k + 1) * self.stride])
            frm, length = guard(slen, frm, length)
            if frm < 0 or length < 0 or frm + length > slen:
                problems.append(
                    f"window {k}: from={frm} length={length} slen={slen} makes "
                    f"a cb3cca21b345 guard FIRE; ../spec.md pins both dead on "
                    f"the measured corpus, because hunk (b) changes the answer "
                    f"and check.py stage 7h requires R1h == R1 on every "
                    f"non-adversarial input")
                break
        for k in range(self.nwin):
            got = self._win[k][0]
            want = self._dumb(self.buf[k * self.stride:(k + 1) * self.stride])
            if got != want:
                problems.append(f"window {k}: {got} != third spelling {want}")
                break
        for b in range(256):
            if MBTAB[b] < 1:
                problems.append(
                    f"MBTAB[{b}] = {MBTAB[b]} < 1; the start walk does not "
                    f"terminate and ../verus.rs::lemma_mbtab_pos is false")
                break
        for b, v in enumerate(_c_table()):
            if v != MBTAB[b]:
                problems.append(
                    f"MBTAB[{b}] = {MBTAB[b]} but c/kernel.c's literal says "
                    f"{v}; the model and the C rung disagree about "
                    f"mbfilter_utf8.c:39-56")
                break
        return problems

    @staticmethod
    def _dumb(win):
        """A third spelling of one window's answer: run the walks with a plain
        list of cursor positions and slice the string. Deliberately naive, and
        deliberately NOT sharing `_window`'s or `strcut_fold`'s code."""
        frm, length, s, slen = Model._unpack(win)
        frm, length = guard(slen, frm, length)
        if frm > slen:
            return 0xFFFFFFFF
        if frm + length > slen:
            length = slen - frm
        cur = [0]
        while cur[-1] <= frm:
            cur.append(cur[-1] + MBTAB[s[cur[-1]]])
        start = cur[-2] if len(cur) >= 2 else 0
        k = start + length
        if k >= slen:
            end = slen
        else:
            end = start
            n = cur[-1]
            while n <= k:
                end = n
                n += MBTAB[s[n]]
        start = min(max(start, 0), slen)
        end = min(max(end, 0), slen)
        start = min(start, end)
        acc = 0
        for b in s[start:end]:
            acc = (acc * 31 + b) & MASK
        acc = (acc * 31 + (end - start)) & MASK
        return acc ^ tally((end - start) + 8)


def _c_table():
    """The 256 entries of `mblen_table_utf8` as c/kernel.c literally spells
    them. Parsed rather than trusted: check 5."""
    import re
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "c", "kernel.c")
    txt = open(p).read()
    m = re.search(r"static const unsigned char mblen_table_utf8\[\] = \{(.*?)\};",
                  txt, re.S)
    if not m:
        return ()
    return tuple(int(x) for x in re.findall(r"\d+", m.group(1)))


def build(path):
    return Model(path)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        m = build(p)
        print(f"{os.path.basename(p):28s} {m.describe()}  "
              f"exit={m.expected_exit} selfcheck={m.selfcheck()}")
