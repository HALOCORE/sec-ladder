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
    the shape of the Verus spec functions `uu_walk` / `fold_line` in ../verus.rs.

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

# `php_shim_tally()`'s multipliers -- common-php/emalloc_shim.h:642-648.
T_ALLOC, T_FREE, T_HIT, T_BYTES = 1000003, 1000033, 1000037, 1000039


def dec(b):
    """`PHP_UU_DEC` -- ext/standard/uuencode.c:66, `((c) - ' ') & 077`.

    C evaluates it on a (signed) `char`, so the subtraction can go negative;
    the `& 077` makes the sign irrelevant, which is why every rung can spell it
    on a `u8`. Range is exactly 0..63, and that is what bounds `len`."""
    return (b - 0x20) & 0o77


def line_len(ln):
    """`ee - s` at uuencode.c:141: `len == 45 ? 60 : (int) floor(len * 1.33)`.

    ⚠ The C is FLOATING POINT and stays that way (c/kernel.c). This integer
    form is the model's, and the two are equal over the whole reachable domain
    -- `len` is `dec(...)`, so 0..63 -- verified exhaustively with a must-fire
    control in `.temp/php13/02-reach.log` Q1 and re-verified per run by
    `selfcheck()`'s `_FLOOR_TABLE` comparison below."""
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
    # (../verus.rs `uu_walk` / `fold_line`): recursive over the line chain, no
    # collected bytearray, no table, and the same (acc, total_len) pair threaded
    # through the recursion.
    def _fold_line(self, src, s, ee, e, acc):
        """`fold_line` in ../verus.rs: the inner loop, as a fold. Returns
        (acc, ok) where `ok` is False when 1e2818b14376's check fired."""
        while s < ee:
            if e - s < 4:
                return acc, False
            acc = (acc * 31 + ((dec(src[s]) << 2 | dec(src[s + 1]) >> 4) & 0xFF)) & MASK
            acc = (acc * 31 + ((dec(src[s + 1]) << 4 | dec(src[s + 2]) >> 2) & 0xFF)) & MASK
            acc = (acc * 31 + ((dec(src[s + 2]) << 6 | dec(src[s + 3])) & 0xFF)) & MASK
            s += 4
        return acc, True

    def _uu_walk(self, src, s, e, acc, total_len):
        """`uu_walk` in ../verus.rs, returning (acc, total_len, ok).

        ⚠ The walk resumes at `s + 1 + 4*nsteps(fl) + 1`, NOT at `ee + 1`. The
        inner loop tests `s < ee` and steps by 4, so it OVERSHOOTS `ee` by up to
        3 whenever `fl` is not a multiple of 4 -- which is every `len` but 45 and
        a minority of the rest. That overshoot is the second, distinct defect
        `f95c1df58349` leaves reachable (NOTES.md §5), and a model that resumed
        at `ee + 1` would describe a decoder PHP has never shipped. It would also
        agree with the simulation on every input this row ships, because every
        line here declares 45 and `60 % 4 == 0` -- so `selfcheck()` could not
        have caught it."""
        if s >= e:
            return acc, total_len, True
        ln = dec(src[s])
        if ln <= 0:
            return acc, total_len, True
        if ln > e:
            return acc, total_len, False
        fl = line_len(ln)
        if fl > e - (s + 1):
            return acc, total_len, False
        ee = s + 1 + fl
        acc, ok = self._fold_line(src, s + 1, ee, e, acc)
        if not ok:
            return acc, total_len, False
        total_len += ln
        s_end = s + 1 + 4 * ((fl + 3) // 4)
        if ln < 45 or s_end >= e:
            return acc, total_len, True
        return self._uu_walk(src, s_end + 1, e, acc, total_len)

    def uu_fold(self, buf, off, ln):
        """`uu_fold` in ../verus.rs: what the kernel must return.

        ⚠ Note that the fold here is over the plaintext bytes IN EMISSION ORDER
        and the simulation folds `out[:total_len]`. Those are the same sequence
        only because `total_len` never exceeds the number of bytes emitted --
        which is a real fact about this decoder (every line emits
        `3*ceil(line_len(ln)/4) >= ln` bytes) and is exactly the fact R5's write
        bound rests on. `selfcheck()` compares the two implementations, so if it
        ever stopped holding this file would say so."""
        src = buf[off: off + ln]
        acc, total_len, ok = self._uu_walk(src, 0, len(src), 0, 0)
        if not ok:
            acc = 0xFFFFFFFF
        else:
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
        declared. That is why every adversarial input here has exactly one
        window -- see inputs/gen.py.

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

    def selfcheck(self):
        """Four checks, and three of them are about this row specifically.

        1. the imperative simulation against the recursive `uu_fold`;
        2. no window reaches the 2014-only class, which is what keeps
           `sanitizer_expect` honest and stage 7h green (see that property);
        3. `uuencode.c:158`'s tail block stays dead on every window;
        4. the integer `line_len` still equals `(int) floor(len * 1.33)` over
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
