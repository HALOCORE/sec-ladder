#!/usr/bin/env python3
"""ph03-uudecode-bound: the independent reference model the gate checks against.

The API is documented at the top of `patterns/p01-array-sum/model.py`; this file
notes only where ph03 differs.

    bindings      buf/off/len/buf_len/result. The kernel *writes* -- into its own
                  `emalloc`'d destination -- but that buffer is private to the
                  call and freed before the kernel returns, so unlike p02 there
                  is no destination to bind before and after. What escapes the
                  call is the u64, and that is what the `ensures` is about.
    work_per_call the WINDOW, in bytes -- `stride`, constant across every call on
                  a given input. Argued below.
    sanitizer     derived, not tabulated: an input "fires" exactly when some call
                  the driver actually makes would trip one of the two 2004
                  checks, because those are precisely the calls on which R1 --
                  which has neither -- walks off the end.

⚠⚠ WHICH ALGORITHM THIS MODEL IMPLEMENTS, BECAUSE IT IS NOT R1's AND IT IS NOT
R1h's EITHER. It is `php_uudecode` with **both** upstream fixes:

    f95c1df58349 (2004)  `len > src_len` and `ee > e`      -- R1h has these
    1e2818b14376 (2014)  `s + 4 > e` inside the inner loop -- R1h does NOT

and that is forced, not chosen: the 2004 fix is incomplete (NOTES.md §5), so a
memory-safe rung cannot stop there. R2-R5 implement exactly this function; R1h
implements the 2004 half; R1 implements neither. On every input this row ships
the 2004 checks fire first, so R1h and the model agree everywhere and only R1
diverges -- `selfcheck()` asserts that, so an input edit cannot silently make
`harness/check.py` stage 7h fail instead.

Two independent implementations, as p01/p02/p16 do:

  * the **simulation** (`_window`) decodes each window once with an imperative
    loop that collects the plaintext bytes, and folds them with a single Horner
    pass. Per-window results go in a table, which is what makes 25 000 driver
    iterations tractable;
  * the **helper** `uu_fold` -- the one the derived `ensures` is evaluated
    against -- is a recursive walk over the line chain with no table, mirroring
    the Verus spec functions `uu_walk` / `fold_line` / `fold_bytes` in
    ../verus.rs: it accumulates the emitted bytes and folds the FIRST
    `total_len` of them, exactly as `fold_bytes(w.0, w.1, 0)` does.

`selfcheck()` runs them against each other -- on the shipped inputs AND on
synthetic windows it builds itself over the whole `ln` domain -- and a
disagreement is reported there rather than being silently absorbed into a green
line.

⚠⚠ **THE SYNTHETIC SWEEP IS NOT DECORATION AND IT IS THE REASON THIS FILE'S
DOCSTRING USED TO BE FALSE.** Until TASK_PHP_015 `uu_fold` folded EVERY emitted
byte where verus.rs folds the first `total_len`, and the two are the same
sequence only when `total_len == p` -- true at multiples of 3 and false for 42
of the 63 length bytes. It passed for one reason: `inputs/gen.py` emitted length
45 exclusively, and `45 % 3 == 0`. Found by TASK_PHP_014 M1. **A second
implementation checked only against the corpus is a second implementation
checked on one diagonal**, so `selfcheck` now constructs its own windows and
`inputs/gen.py` asserts that the shipped corpus reaches the strict case as well.
"""

import itertools
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "common"))
import slb  # noqa: E402

MASK = (1 << 64) - 1

# `php_shim_tally()`'s multipliers -- common-php/emalloc_shim.h:642-648.
T_ALLOC, T_FREE, T_HIT, T_BYTES = 1000003, 1000033, 1000037, 1000039


def dec(b):
    """`PHP_UU_DEC` -- ext/standard/uuencode.c:66, `((c) - ' ') & 077`.

    C evaluates it on a (signed) `char`, so the subtraction can go negative;
    the `& 077` makes the sign irrelevant, which is why every rung can spell it
    on a `u8`. Range is exactly 0..63, and that is what bounds `len`."""
    return (b - 0x20) & 0o77


def enc(v):
    """`PHP_UU_ENC` -- ext/standard/uuencode.c:62, `((c) ? ((c) & 077) + ' ' : '`')`.

    The inverse of `dec` on 1..63 and the encoder `inputs/gen.py` uses. It is
    here so that `selfcheck()` can BUILD windows rather than only read them --
    see the docstring at the top of this file."""
    return ((v & 0o77) + 0x20) if (v & 0xFF) else 0x60


def line_len(ln):
    """`ee - s` at uuencode.c:141: `len == 45 ? 60 : (int) floor(len * 1.33)`.

    ⚠ The C is FLOATING POINT and stays that way (c/kernel.c). This integer
    form is the model's, and the two are equal over the whole reachable domain
    -- `len` is `dec(...)`, so 0..63 -- verified exhaustively with a must-fire
    control in `.temp/php13/02-reach.log` Q1 and re-verified per run by
    `selfcheck()`'s check 4, which computes `int(math.floor(ln * 1.33))` from
    the float itself so the two spellings cannot drift apart in this file's own
    head. (This cited a `_FLOOR_TABLE` that has never existed in this file --
    corrected at TASK_PHP_015 while the row was being re-measured anyway.)"""
    return 60 if ln == 45 else (ln * 133) // 100


def capacity(src_len):
    """`emalloc(ceil(src_len * 0.75) + 1)` at uuencode.c:131, exactly.

    `0.75` is a power of two over a power of two and `src_len` is an `int`, so
    the double product is exact and `ceil(3n/4)` is `n - n // 4` -- an identity
    over the integers, which `selfcheck()` re-derives against `(3n + 3) // 4`.
    The Rust rungs use this spelling rather than `(3n + 3) // 4` because
    `3 * src_len` overflows `usize` for a large window and this does not; see
    safe_naive.rs."""
    return src_len - src_len // 4 + 1


def tally(cap):
    """`php_shim_tally()` after one `php_shim_reset` + one `emalloc(cap)` + one
    `efree`, which is exactly what one kernel call does.

    `n_alloc = 1`, `n_free = 1`, `n_cache_hit = 0` (the reset empties the
    size-class cache, so the request always misses), and `bytes_mallocked` is
    the TRUNCATED `real_size`, i.e. `(cap + 7) & ~7` -- `emalloc_shim.h:135`,
    truncation T1. `cap` never approaches 2^32 here, so T1 and T2 do not fire;
    that is the row's `emalloc_dependent: false` (../spec.md), and it is why
    this is a closed form rather than a simulation of the allocator."""
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
        self.any_2004 = False       # some call trips f95c1df58349's checks
        self.any_2014_only = False  # some call trips ONLY 1e2818b14376's check
        self.nwin = 0
        self._win = []              # per window: (result, err2004, err2014only)
        if not self.truncated:
            self._run()

    # -- the window table (computed once) ----------------------------------
    def _window(self, off):
        """(result, err2004, err2014only) for the window at `off`.

        Implementation 1 of 2. An imperative transcription of
        `php_uudecode` + both upstream fixes, collecting the plaintext into a
        bytearray and folding it in one pass at the end.

        `err2004` is what R1h also refuses; `err2014only` is the case the 2004
        fix lets through and the 2014 one catches -- the row's headline, and the
        thing `selfcheck` asserts no shipped input reaches."""
        src = self.buf[off: off + self.stride]
        src_len = len(src)
        cap = capacity(src_len)
        out = bytearray()
        total_len = 0
        s, e = 0, src_len
        err2004 = err2014 = False
        while s < e:
            ln = dec(src[s])
            s += 1
            if ln <= 0:
                break
            if ln > src_len:                       # f95c1df58349 hunk 1
                err2004 = True
                break
            fl = line_len(ln)
            if fl > e - s:                         # f95c1df58349 hunk 2
                err2004 = True
                break
            ee = s + fl
            stop = False
            while s < ee:
                if e - s < 4:                      # 1e2818b14376
                    err2014 = True
                    stop = True
                    break
                out.append((dec(src[s]) << 2 | dec(src[s + 1]) >> 4) & 0xFF)
                out.append((dec(src[s + 1]) << 4 | dec(src[s + 2]) >> 2) & 0xFF)
                out.append((dec(src[s + 2]) << 6 | dec(src[s + 3])) & 0xFF)
                s += 4
            if stop:
                break
            # `total_len += ln` sits AFTER the inner loop, where uuencode.c:139
            # has it before `:141`. Observationally identical -- every path that
            # skips it returns -1 and discards `total_len` -- and it is what
            # makes `total_len <= p` a real loop invariant rather than one that
            # holds "except between two statements". ../spec.md pins the
            # reordering and the reason; R2-R5 do the same.
            total_len += ln
            if ln < 45:
                break
            if s >= e:
                break
            s += 1                                 # skip \n
        acc = 0
        if err2004 or err2014:
            acc = 0xFFFFFFFF                       # (u64)(unsigned int)(-1)
        else:
            # uuencode.c:158's tail block is DEAD -- `>` binds tighter than `=`
            # so `len` is 0 or 1, and measured over 12 600 documents the
            # condition was true zero times (.temp/php13/02-reach.log Q2).
            # `selfcheck` re-asserts it per input rather than trusting that.
            for b in out[:total_len]:
                acc = (acc * 31 + b) & MASK
            acc = (acc * 31 + total_len) & MASK
        return acc ^ tally(cap), err2004, (err2014 and not err2004)

    # -- simulation --------------------------------------------------------
    def _run(self):
        acc = 0
        if 1 <= self.stride <= self.n_blob:
            self.entered = True
            self.nwin = self.n_blob // self.stride
            self._win = [self._window(k * self.stride) for k in range(self.nwin)]
            for _ in range(self.n_iters):
                k = (acc * self.nwin) >> 64
                r, e04, e14 = self._win[k]
                if e04:
                    self.any_2004 = True
                if e14:
                    self.any_2014_only = True
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
    # (../verus.rs `uu_walk` / `fold_line` / `fold_bytes`): RECURSIVE over the
    # line chain where `_window` is iterative, no per-window table, `src_len`
    # threaded separately from `e`, and the Horner pass split out of the walk so
    # that it can be applied to the `total_len` PREFIX -- which is the whole
    # point and is what TASK_PHP_014 M1 found missing.
    #
    # ⚠ What makes it independent is the SHAPE of the walk, not the absence of a
    # buffer. The two disagree on `s_end` vs `ee + 1` (TASK_PHP_013 §6) and on
    # `out[:total_len]` vs `out` (TASK_PHP_014 M1) -- two real modelling errors,
    # one caught by each direction of the comparison.
    def _fold_line(self, src, s, ee, e, out):
        """`fold_line` in ../verus.rs: the inner loop, appending each group's
        three bytes to `out`. Returns (out, ok), where `ok` is False when
        1e2818b14376's check fired.

        ⚠ It APPENDS rather than folding, because verus.rs's `fold_line` does:
        it returns `out + grp(...)` and the Horner pass is a separate function
        (`fold_bytes`) applied to a PREFIX of the result. Threading an
        accumulator here would fold every emitted byte, which is a different
        function whenever `total_len < out.len()` -- TASK_PHP_014 M1."""
        while s < ee:
            if e - s < 4:
                return out, False
            out.append((dec(src[s]) << 2 | dec(src[s + 1]) >> 4) & 0xFF)
            out.append((dec(src[s + 1]) << 4 | dec(src[s + 2]) >> 2) & 0xFF)
            out.append((dec(src[s + 2]) << 6 | dec(src[s + 3])) & 0xFF)
            s += 4
        return out, True

    def _uu_walk(self, src, s, e, src_len, out, total_len):
        """`uu_walk` in ../verus.rs, returning (out, total_len, ok).

        ⚠ The walk resumes at `s + 1 + 4*nsteps(fl) + 1`, NOT at `ee + 1`. The
        inner loop tests `s < ee` and steps by 4, so it OVERSHOOTS `ee` by up to
        3 whenever `fl` is not a multiple of 4 -- which is every `len` but 45 and
        a minority of the rest. That overshoot is the second, distinct defect
        `f95c1df58349` leaves reachable (NOTES.md §5), and a model that resumed
        at `ee + 1` would describe a decoder PHP has never shipped.

        ⚠⚠ This docstring used to end *"it would also agree with the simulation
        on every input this row ships, because every line here declares 45 and
        `60 % 4 == 0` -- so `selfcheck()` could not have caught it"*, and
        TASK_PHP_015 makes that FALSE in the good direction: the corpus now
        carries a short final line, so `nsteps(fl) != fl/4` on every window, and
        `selfcheck()`'s synthetic sweep catches `ee + 1` in 65 of 896 windows
        with the corpus set aside entirely (`.temp/php15/03-sweep-mustfire.log`,
        mutant `resume_ee`). ⚠ **It was true when written**, which is the point:
        a modelling error found only by writing a termination argument is one
        the corpus was too narrow to see, and the repair is to widen the
        corpus and to stop depending on it."""
        if s >= e:
            return out, total_len, True
        ln = dec(src[s])
        if ln <= 0:
            return out, total_len, True
        if ln > src_len:
            return out, total_len, False
        fl = line_len(ln)
        if fl > e - (s + 1):
            return out, total_len, False
        ee = s + 1 + fl
        out, ok = self._fold_line(src, s + 1, ee, e, out)
        if not ok:
            return out, total_len, False
        total_len += ln
        s_end = s + 1 + 4 * ((fl + 3) // 4)
        if ln < 45 or s_end >= e:
            return out, total_len, True
        return self._uu_walk(src, s_end + 1, e, src_len, out, total_len)

    def uu_fold(self, buf, off, ln):
        """`uu_fold` in ../verus.rs: what the kernel must return.

        ⚠⚠ **THE FOLD IS OVER THE FIRST `total_len` EMITTED BYTES, NOT OVER ALL
        OF THEM**, because that is what `verus.rs::uu_fold` does --
        `fold_bytes(w.0, w.1, 0)`, where `w.1` is `total_len` -- and because
        that is what PHP returns: `:202 RETURN_STRINGL(dst, dst_len, 0)` makes a
        zval string of exactly `dst_len` bytes over a buffer that holds more.

        ⚠ The two are DIFFERENT sequences whenever a line declares an `ln` that
        is not a multiple of 3: the line emits `3*ceil(line_len(ln)/4)` bytes and
        contributes only `ln` to `total_len`, and the row's own
        `lemma_emit_covers_declared` proves `ln <= 3*ceil(line_len(ln)/4)` with
        equality **only at multiples of 3** -- so the inequality is STRICT for 42
        of the 63 length bytes. Folding all of them was this file's bug until
        TASK_PHP_015 (TASK_PHP_014 M1); `selfcheck()`'s synthetic sweep is what
        makes it impossible to reintroduce silently."""
        src = buf[off: off + ln]
        out, total_len, ok = self._uu_walk(src, 0, len(src), len(src), [], 0)
        if not ok:
            acc = 0xFFFFFFFF
        else:
            acc = 0
            for b in out[:total_len]:
                acc = (acc * 31 + b) & MASK
            acc = (acc * 31 + total_len) & MASK
        return acc ^ tally(capacity(len(src)))

    @property
    def helpers(self):
        return {"uu_fold": self.uu_fold}

    # -- what the kernel must do, per call ---------------------------------
    @property
    def work_per_call(self):
        """The window, in bytes -- `stride` -- from the file alone.

        **Why the window and not the decoded length, and not the lines.**
        `check.py::check_marginal_ir` needs one scalar per input and hard-fails
        on `work_per_call=0`. A decoder has a *distribution* of work per call:
        it stops early on a malformed line, and denominating in decoded bytes
        collapses to 0 the moment a probe input's window refuses at its first
        length byte -- which is exactly what `adversarial-*` contains. The
        number of lines has the same problem and a worse one: the line count is
        read out of the data, so the unit would move with the attacker.

        The window is the unit that does not move. It is fixed by the payload
        header, identical on every call of a given input, and a strict
        over-estimate of the bytes the kernel touches -- the '\\n' of every line
        is skipped and the terminator's is never read. An over-estimate raises
        the derived floor, which is the direction a floor should err."""
        return self.stride if self.entered else 0

    # -- sanitizer expectation ---------------------------------------------
    @property
    def sanitizer_expect(self):
        """Derived from the simulated run, never tabulated per file.

        A call refused by one of the 2004 checks is exactly a call on which R1
        -- which has neither -- computes `ee > e` and lets the inner loop walk
        past the source. So "the simulation refused at least one of the calls
        this input actually makes" *is* "ASan must report on this input".

        Note "actually makes": the driver picks windows from a checksum-derived
        index, so a malformed window that is never selected must not be
        declared. That is why every adversarial input that declares `fires`
        has exactly one window -- see inputs/gen.py. (`adversarial-nowin.bin`
        has ZERO, which is its whole point, and declares `clean`.)

        ⚠ It is derived from `any_2004` and NOT from `any_2014_only`, and the
        difference is the row's headline. A call in the 2014-only class makes R1
        **and R1h** read out of bounds, and `check.py`'s stage 7h hard-fails on
        any R1h diagnostic -- so such an input could not be shipped here at all.
        `selfcheck()` asserts none is."""
        return "fires" if self.any_2004 else "clean"

    # -- what a conforming driver does -------------------------------------
    @property
    def expected_exit(self):
        # ph03's payload allocates nothing from an attacker-controlled size --
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

    # -- driving BOTH implementations on a window no input file contains ----
    @staticmethod
    def _both(src):
        """(simulated, uu_fold) for an arbitrary window, off-corpus.

        `Model.__new__` skips `__init__` deliberately: `_window` and `uu_fold`
        read only `buf` and `stride`, so this drives the SHIPPED code paths on
        bytes chosen here rather than on bytes `inputs/` happens to carry. That
        is the entire mechanism behind `selfcheck` check 1b."""
        m = Model.__new__(Model)
        m.buf, m.stride = src, len(src)
        return m._window(0)[0], m.uu_fold(src, 0, len(src))

    @staticmethod
    def _synthetic_windows():
        """Windows spanning the whole `ln` domain, built here, yielded as
        (label, bytes). ⚠ **`inputs/` is not the domain and must never be
        mistaken for it** -- see the module docstring.

        Three families, chosen because each isolates one thing the two
        implementations could disagree about:

          a. `ln` alone, 1..63, one line with plenty of payload behind it --
             this is the axis on which `total_len` and the emitted-byte count
             come apart, and the axis `inputs/` cannot span (a window's stride
             is fixed, so its lines' lengths are constrained);
          b. `ln` at the buffer's edge, so `fl > e - (s+1)` and `e - s < 4`
             both fire -- the two refusal paths, where a walk that resumed at
             the wrong offset shows up as a different `ok`;
          c. two-line chains `45 -> ln`, which is the only shape in which the
             resume point `s_end + 1` is exercised at all (a walk stops at
             `ln < 45`), and is where TASK_PHP_013 §6's `ee + 1` error lived."""
        for ln in range(0, 64):
            for pad in (0, 1, 2, 3, 7):
                yield (f"single ln={ln} pad={pad}",
                       bytes([enc(ln)]) + bytes(
                           enc(1 + (i % 63)) for i in range(
                               4 * ((line_len(ln) + 3) // 4) + pad)))
        for ln in range(0, 64):
            for n in range(0, 6):
                yield (f"edge ln={ln} n={n}",
                       bytes([enc(ln)]) + bytes(enc(1 + i) for i in range(n)))
        for ln in range(0, 64):
            for pad in (0, 1, 4):
                first = bytes([enc(45)]) + bytes(enc(1 + (i % 63))
                                                 for i in range(60)) + b"\n"
                yield (f"chain 45->{ln} pad={pad}",
                       first + bytes([enc(ln)]) + bytes(
                           enc(1 + (i % 63)) for i in range(
                               4 * ((line_len(ln) + 3) // 4) + pad)))

    def selfcheck(self):
        """Five checks, and four of them are about this row specifically.

        1a. the imperative simulation against the recursive `uu_fold`, on the
            calls this input actually makes;
        1b. ⚠⚠ the same two implementations on **synthetic windows this file
            builds**, spanning `ln = 0..63` in three families. **1a alone is
            what let TASK_PHP_014 M1 stand**: every line the corpus carried
            declared 45, `45 % 3 == 0` is exactly the equality case, and a
            helper that folded every emitted byte instead of the first
            `total_len` agreed on the whole corpus and on nothing else. A
            second implementation is only as strong as the domain it is
            exercised over, and `inputs/` is not a domain -- it is seven files;
        2.  no window reaches the 2014-only class, which is what keeps
            `sanitizer_expect` honest and stage 7h green (see that property);
        3.  `uuencode.c:158`'s tail block stays dead on every window;
        4.  the integer `line_len` still equals `(int) floor(len * 1.33)` over
            the whole reachable domain, computed here from the float so the two
            spellings cannot drift apart in this file's own head."""
        import math
        problems = []
        for c in self.sample_calls(8):
            want = self.uu_fold(c["buf"], c["off"], c["len"])
            if want != c["result"]:
                problems.append(
                    f"simulated result {c['result']} != uu_fold() {want} at "
                    f"off={c['off']}")
                break
        for label, src in self._synthetic_windows():
            sim, helper = self._both(src)
            if sim != helper:
                problems.append(
                    f"synthetic window [{label}]: simulated {sim} != uu_fold() "
                    f"{helper}. The two implementations have come apart OFF the "
                    f"corpus; inputs/ cannot see this and it is why this sweep "
                    f"exists (TASK_PHP_014 M1)")
                break
        if self.any_2014_only:
            problems.append(
                "a window reaches the 1e2818b14376-only class, on which R1h "
                "also reads out of bounds; check.py stage 7h hard-fails on any "
                "R1h diagnostic, so this input cannot ship in inputs/. Move it "
                "to controls/ (NOTES.md §5).")
        for k in range(self.nwin):
            if self._tail_reachable(k * self.stride):
                problems.append(f"uuencode.c:158's tail block is LIVE on window "
                                f"{k}; ../spec.md pins it dead")
                break
        for n in range(0, 100000):
            if capacity(n) != (3 * n + 3) // 4 + 1:
                problems.append(f"capacity({n}) = {capacity(n)} != "
                                f"ceil(3*{n}/4) + 1 = {(3 * n + 3) // 4 + 1}")
                break
        for ln in range(0, 64):
            if ln != 45 and line_len(ln) != int(math.floor(ln * 1.33)):
                problems.append(f"line_len({ln}) = {line_len(ln)} != "
                                f"(int) floor({ln} * 1.33) = "
                                f"{int(math.floor(ln * 1.33))}")
                break
        return problems

    def _tail_reachable(self, off):
        """Re-derive `total_len > (p - *dest)` at uuencode.c:158 for one window.

        ⚠ Scoped to the algorithm THIS MODEL implements -- both upstream fixes
        -- because that is the only one it can evaluate: on a window R1 walks
        out of, `p - *dest` is a value the model has no buffer to produce. A
        `goto err` returns before `:158`, so an errored window is not a
        reachable tail. The claim that the tail is dead for **R1** is measured
        elsewhere, over 12 600 (src_len, len) documents, in
        `.temp/php13/02-reach.log` Q2 and NOTES.md §6 -- a model cannot check
        it and this method does not pretend to."""
        src = self.buf[off: off + self.stride]
        src_len = len(src)
        total_len = written = 0
        s, e = 0, src_len
        while s < e:
            ln = dec(src[s])
            s += 1
            if ln <= 0:
                break
            if ln > src_len:
                return False                       # goto err, before :158
            total_len += ln
            fl = line_len(ln)
            if fl > e - s:
                return False                       # goto err, before :158
            ee = s + fl
            while s < ee:
                if e - s < 4:
                    return False                   # goto err, before :158
                written += 3
                s += 4
            if ln < 45:
                break
            if s >= e:
                break
            s += 1
        return total_len > written


def build(path):
    return Model(path)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        m = build(p)
        print(f"{os.path.basename(p):28s} {m.describe()}  "
              f"exit={m.expected_exit} selfcheck={m.selfcheck()}")
