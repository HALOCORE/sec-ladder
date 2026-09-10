#!/usr/bin/env python3
"""ph16-fdset-index: the independent reference model the gate checks against.

The API is documented at the top of `patterns/p01-array-sum/model.py`; this file
notes only where ph16 differs.

    bindings      buf/off/len/buf_len/result. The kernel writes only into three
                  `fd_set`s of its own frame, all three of which it folds before
                  returning, so there is no destination to bind before and
                  after. What escapes the call is the u64.
    work_per_call the WINDOW, in bytes -- `stride`, constant across every call
                  on a given input. Argued below.
    sanitizer     derived, not tabulated -- and here that derivation is about
                  ASan's REDZONE and not only about the defect. See
                  `sanitizer_expect`; this is the one place this row's model is
                  a statement about the toolchain as well as about PHP.

⚠⚠ WHICH ALGORITHM THIS MODEL IMPLEMENTS, BECAUSE IT IS NOT R1's. It is
`stream_array_to_fd_set` **with the POSIX branch of the real upstream fix
applied**, which is exactly `c/kernel_hardened.c` and exactly R2-R5:

    R1     streamsfuncs.c:518-548 as shipped in 5.0.0 -- CRASH-098
    R1h    + 99e290f882c9 (Wez Furlong, 2004-09-17, "Bug #24189: possibly
           unsafe select(2) usage"), POSIX branch, which is THREE guards:
             (a) `&& this_fd >= 0`                       -- DEAD in this kernel
             (b) PHP_SAFE_FD_SET's `if (fd < FD_SETSIZE)` -- the memory-safety half
             (c) PHP_SAFE_MAX_FD's clamp on `max_fd`      -- in the CALLER's frame
    R2-R5  the same function, memory-safe

⭐ The fix is COMPLETE: guard (b) removes every out-of-range `FD_SET` and
changes no benign answer, so R1h and R2-R5 implement one function and only R1
diverges. `controls/fix_scope.py` prices each guard separately rather than
asserting this.

⚠ Guard (c) is NOT about the write. `*max_fd = this_fd` sits inside the arm
guard (b) protects but is not itself bounded by it, so without (c) `php_select`
is still handed an `nfds` past `FD_SETSIZE`. This model carries it because this
row's `u64` folds `max_fd`, which is what `php_select` reads.

Three independent implementations, as p01/p02/p16, ph03 and ph07 do:

  * the **simulation** (`_window`) walks each window once with imperative loops
    over integer cursors and returns the folded result. Per-window results go
    in a table, which is what makes 25 000 driver iterations tractable;
  * the **helper** `fdset_fold` -- the one the derived `ensures` is evaluated
    against -- is built out of RECURSIVE walks with no cursor variable and no
    table, mirroring the Verus spec functions `walk` / `fold16` in ../verus.rs;
  * `_dumb`, a third spelling that builds the set of indices first and then
    materialises the words from it.

`selfcheck()` runs them against each other -- on the shipped inputs AND on
synthetic windows it builds itself over a domain no input file contains -- and a
disagreement is reported there rather than absorbed into a green line.

⚠⚠ **THE SYNTHETIC SWEEP IS NOT DECORATION.** `PROTOCOL_PHP.md` §A2a rule 2: a
second implementation is only as strong as the domain it is exercised over, and
`inputs/` is not a domain -- it is a handful of files. ph03 shipped for a full
task with its two implementations computing different functions because its
corpus took one arm of a two-armed branch.
"""

import itertools
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "common"))
import slb  # noqa: E402

MASK = (1 << 64) - 1

#: <sys/select.h> on the box this row is measured on. `c/kernel.c` carries a
#: C99 compile-time assertion that the platform really is this shape, so a
#: change of platform is a build failure and not a silently wrong number.
FD_SETSIZE = 1024
NW = 16                       # sizeof(fd_set) / sizeof(long)

#: ⚠⚠ THE ONE ENVIRONMENT-SPECIFIC BAND IN THIS FILE, AND IT IS MEASURED.
#: Under `-fsanitize=address` every stack object gets a redzone; on this frame
#: it is exactly 32 bytes, so a write at byte offset 128..159 past `rfds` is
#: REPORTED and one at 160 and beyond lands in the next `fd_set` -- a live
#: object, with nothing for a sanitizer to say. In index terms that is
#: [1024, 1280). Measured with one FD_SET per process, gcc -O1 -fsanitize=
#: address,undefined, flips at exactly 1279/1280:
#: `.tasks-php/TASK_PHP_025_REPORT.md` §3, `.temp/php25/asan_sweep.c`.
#: ⚠ It is a claim about THIS TOOLCHAIN, not about PHP
#: (`.memory-php/02-ladder.md`), and it is written here rather than tabulated
#: per file so that changing an adversarial index moves the expectation.
ASAN_REDZONE = range(FD_SETSIZE, 1280)


def _entry(win, k):
    """Entry `k` of a window, as every rung decodes it."""
    return win[6 + 2 * k] | (win[7 + 2 * k] << 8)


def split_of(stride, sr, sw):
    """(n_r, n_w, n_e). Derived, never trusted: the kernel gets no length out
    of the blob, exactly as PHP gets none -- a zend_hash knows its own count."""
    m = (stride - 6) // 2
    n_r = sr % (m + 1)
    rem = m - n_r
    n_w = sw % (rem + 1)
    return n_r, n_w, rem - n_w


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
        self.nwin = 0
        self._win = []                # per window: (result, worst_oob_index)
        self.any_oob = False          # some call the driver makes writes OOB
        self.any_redzone = False      # ... and lands where ASan can see it
        if not self.truncated:
            self._run()

    # -- the window table (computed once) ----------------------------------
    @staticmethod
    def _unpack(win):
        """(ctl, n_r, n_w, n_e, entries) for one window's bytes."""
        stride = len(win)
        ctl = win[0] | (win[1] << 8)
        sr = win[2] | (win[3] << 8)
        sw = win[4] | (win[5] << 8)
        m = (stride - 6) // 2
        n_r, n_w, n_e = split_of(stride, sr, sw)
        return ctl, n_r, n_w, n_e, [_entry(win, k) for k in range(m)]

    @staticmethod
    def _to_fd_set(run, not_an_array, fds, mx):
        """`stream_array_to_fd_set`, R1h. Returns (sets, max_fd).

        Implementation 1 of 3: an imperative transcription of
        `c/kernel_hardened.c`, cursors named as the C names them."""
        if not_an_array:
            return 0, mx
        for e in run:
            if e >> 14 != 0:                     # stream != NULL
                if e >> 14 != 1:                 # SUCCESS == php_stream_cast
                    this_fd = e & 0x3FFF
                    if this_fd < FD_SETSIZE:     # guard (b)
                        fds[this_fd // 64] |= 1 << (this_fd % 64)
                    if this_fd > mx:
                        mx = this_fd
        return 1, mx

    @staticmethod
    def _fold_set(fds):
        h = 0
        for w in fds:
            h = (h * 31 + w) & MASK
        return h

    def _window(self, off):
        """(result, worst out-of-range index R1 would write) for one window.

        The second element is what makes `sanitizer_expect` a derivation: it
        records the access R1 performs and this model does not."""
        win = self.buf[off: off + self.stride]
        ctl, n_r, n_w, n_e, es = self._unpack(win)

        sets = 0
        max_fd = 0
        worst = -1
        pos = 0
        sets_arr = []
        for b, n in enumerate((n_r, n_w, n_e)):
            run = es[pos:pos + n]
            pos += n
            fds = [0] * NW
            if ctl & (1 << b):                   # X_array == NULL
                sets_arr.append(fds)
                continue
            s, max_fd = self._to_fd_set(run, bool(ctl & (8 << b)), fds, max_fd)
            sets += s
            sets_arr.append(fds)
            if not (ctl & (8 << b)):
                for e in run:
                    if (e >> 14) >= 2 and (e & 0x3FFF) >= FD_SETSIZE:
                        worst = max(worst, e & 0x3FFF)

        if max_fd >= FD_SETSIZE:                 # guard (c), PHP_SAFE_MAX_FD
            max_fd = FD_SETSIZE - 1
        if sets == 0:
            return 0xFFFFFFFF, worst             # RETURN_FALSE

        acc = 0
        acc = (acc * 31 + sets) & MASK
        acc = (acc * 31 + max_fd) & MASK
        for fds in sets_arr:
            acc = (acc * 31 + self._fold_set(fds)) & MASK
        return acc, worst

    # -- simulation --------------------------------------------------------
    def _run(self):
        acc = 0
        if 8 <= self.stride <= self.n_blob:
            self.entered = True
            self.nwin = self.n_blob // self.stride
            self._win = [self._window(k * self.stride) for k in range(self.nwin)]
            for _ in range(self.n_iters):
                k = (acc * self.nwin) >> 64
                r, worst = self._win[k]
                if worst >= 0:
                    self.any_oob = True
                    if worst in ASAN_REDZONE:
                        self.any_redzone = True
                acc = (acc * 31 + r) & MASK
            self.n_calls = self.n_iters
        self.checksum = acc

    def iter_calls(self):
        """Replay the driver loop, yielding one binding per kernel call."""
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
    # (../verus.rs `walk` / `fold16`): RECURSIVE where `_window` is iterative,
    # carrying `(fds, max_fd)` as a returned pair rather than as a mutated list.
    @staticmethod
    def _walk(run, i, fds, mx):
        """One application of ../verus.rs's `walk`, driven to its fixpoint.

        ⚠ Written as a loop over a pure transition rather than as Python
        recursion: `large.bin`'s window carries 2 035 entries, which would be
        2 035 frames and a `RecursionError` on the default limit. Each step is
        exactly one unfolding of the spec function."""
        while i < len(run):
            e = run[i]
            if (e >> 14) >= 2:
                f = e & 0x3FFF
                if f // 64 < NW:                 # guard (b), in the word index
                    w = f // 64
                    fds = fds[:w] + (fds[w] | (1 << (f % 64)),) + fds[w + 1:]
                mx = f if f > mx else mx
            i += 1
        return fds, mx

    @staticmethod
    def _fold16(fds, i, acc):
        """../verus.rs's `fold16`, one word at a time."""
        while i < NW:
            acc = (acc * 31 + fds[i]) & MASK
            i += 1
        return acc

    def fdset_fold(self, buf, off, ln):
        """`fdset_fold` in ../verus.rs: what the kernel must return."""
        win = buf[off: off + ln]
        ctl, n_r, n_w, n_e, es = self._unpack(win)
        sets = 0
        mx = 0
        pos = 0
        folded = []
        for b, n in enumerate((n_r, n_w, n_e)):
            run = es[pos:pos + n]
            pos += n
            fds = (0,) * NW
            if not (ctl & (1 << b)):
                if ctl & (8 << b):
                    pass                          # Z_TYPE_P(...) != IS_ARRAY
                else:
                    fds, mx = self._walk(run, 0, fds, mx)
                    sets += 1
            folded.append(self._fold16(fds, 0, 0))
        if mx >= FD_SETSIZE:
            mx = FD_SETSIZE - 1
        if sets == 0:
            return 0xFFFFFFFF
        acc = 0
        acc = (acc * 31 + sets) & MASK
        acc = (acc * 31 + mx) & MASK
        for h in folded:
            acc = (acc * 31 + h) & MASK
        return acc

    @property
    def helpers(self):
        return {"fdset_fold": self.fdset_fold}

    # -- what the kernel must do, per call ---------------------------------
    @property
    def work_per_call(self):
        """The window, in bytes -- `stride` -- from the file alone.

        **Why the window and not the entry count.**
        `check.py::check_marginal_ir` needs one scalar per input and hard-fails
        on `work_per_call = 0`. The entry count IS `(stride - 6) / 2`, i.e. an
        affine function of the stride, so the two denominators differ by a
        constant factor and the stride is the one the payload header fixes and
        the attacker cannot move. It is a strict over-estimate -- a call
        touches two bytes per entry plus a fixed 3 x 128-byte zero and a
        48-word fold -- and an over-estimate raises the derived floor, which is
        the direction a floor should err.

        ⚠ The fixed per-call term is REAL and is not hidden: ../NOTES.md §8
        decomposes the marginal rather than presenting it as a pure walk
        rate."""
        return self.stride if self.entered else 0

    # -- sanitizer expectation ---------------------------------------------
    @property
    def sanitizer_expect(self):
        """Derived from the simulated run, never tabulated per file.

        ⚠⚠ **THIS ROW'S DERIVATION HAS TWO PARTS AND ONLY ONE OF THEM IS ABOUT
        PHP.** A call on which R1 -- which has no guard -- writes at an index
        >= FD_SETSIZE is a call that writes outside the `fd_set`. Whether ASan
        *reports* it is a further question, and the answer is no unless the
        write lands in a redzone: past 32 bytes it lands in the NEXT `fd_set`,
        a live object of the same frame, and there is nothing for a sanitizer
        to say. So the expectation is

            "fires" iff some call the driver makes writes into ASAN_REDZONE

        and NOT "iff some call writes out of bounds". ⚠ **That is a weaker
        claim than every other row in this corpus makes, and it is the row's
        headline result rather than a concession**: `adversarial-silent.bin`
        writes 128 bytes further out than `adversarial-redzone.bin`, is
        declared `clean`, and corrupts a live neighbouring object that the
        function's own return value depends on. `controls/oracle.py` is what
        witnesses that one, and `../NOTES.md` §3 has the sweep.

        Note "the driver makes": windows are picked from a checksum-derived
        index, so a hostile window that is never selected must not be declared.
        That is why every adversarial input has exactly one window --
        `inputs/gen.py`. (`adversarial-nowin.bin` has ZERO, which is its whole
        point, and declares `clean`.)"""
        return "fires" if self.any_redzone else "clean"

    # -- what a conforming driver does -------------------------------------
    @property
    def expected_exit(self):
        # ph16's payload allocates nothing -- the three `fd_set`s are stack
        # objects of a size the platform fixes -- so p02's exit 7 has no
        # analogue here. `slb_load` rejecting a short file is the only non-zero
        # exit this pattern's driver produces.
        return 5 if self.truncated else 0

    @property
    def expected_stdout(self):
        return "" if self.checksum is None else f"{self.checksum}\n"

    def describe(self):
        return (f"n_iters={self.n_iters} stride={self.stride} "
                f"n_blob={self.n_blob} nwin={self.nwin} calls={self.n_calls} "
                f"work/call={self.work_per_call}B san={self.sanitizer_expect} "
                f"oob={self.any_oob} truncated={self.truncated} "
                f"expected={self.checksum}")

    # -- driving BOTH implementations on a window no input file contains ----
    @staticmethod
    def _both(win):
        """(simulated, fdset_fold) for an arbitrary window, off-corpus.

        `Model.__new__` skips `__init__` deliberately: `_window` and
        `fdset_fold` read only `buf` and `stride`, so this drives the SHIPPED
        code paths on bytes chosen here rather than on bytes `inputs/` happens
        to carry."""
        m = Model.__new__(Model)
        m.buf, m.stride = win, len(win)
        return m._window(0)[0], m.fdset_fold(win, 0, len(win))

    @staticmethod
    def _synthetic_windows():
        """Windows spanning a domain `inputs/` cannot, built here, yielded as
        (label, bytes). ⚠ **`inputs/` is not the domain and must never be
        mistaken for it** -- see the module docstring.

        Five families, each isolating one thing the implementations could
        disagree about:

          a. every `ctl` value in 0..63, so every combination of "array is
             NULL" and "array is not an array" is driven -- 64 windows, and the
             corpus can carry at most one per window;
          b. every entry TAG, and both success encodings;
          c. the index boundary, `this_fd` in {0, 1, 63, 64, 1022, 1023, 1024,
             1025, 2048, 16383} -- which spans guard (b)'s test, both sides of
             a word boundary, and the out-of-range region no benign input may
             contain;
          d. degenerate splits: every array empty, one array taking everything,
             and `m` itself as small as the driver admits;
          e. `max_fd` in both directions, including the descending sequence
             that makes `if (this_fd > *max_fd)` take its false arm."""
        def w(stride, ctl, sr, sw, es):
            m = (stride - 6) // 2
            es = (list(es) + [0] * m)[:m]
            return (bytes((ctl & 0xFF, ctl >> 8, sr & 0xFF, sr >> 8,
                           sw & 0xFF, sw >> 8))
                    + b"".join(bytes((e & 0xFF, e >> 8)) for e in es))

        idxs = (0, 1, 63, 64, 1022, 1023, 1024, 1025, 2048, 16383)
        for ctl in range(64):
            yield (f"ctl={ctl}",
                   w(30, ctl, 3, 3, [(2 << 14) | 5, (1 << 14), 0,
                                     (3 << 14) | 900, (2 << 14) | 1023,
                                     (2 << 14) | 7, (3 << 14) | 1,
                                     (2 << 14) | 300, (0 << 14) | 9,
                                     (2 << 14) | 64, (2 << 14) | 63,
                                     (3 << 14) | 0]))
        for tag in range(4):
            for i in idxs:
                yield (f"tag={tag} idx={i}",
                       w(30, 0, 4, 4, [(tag << 14) | i, (2 << 14) | 3,
                                       (tag << 14) | i, (3 << 14) | 4,
                                       (tag << 14) | i, (2 << 14) | 5,
                                       (1 << 14) | i, 0,
                                       (2 << 14) | 1023, (2 << 14) | 0,
                                       (3 << 14) | i, (2 << 14) | 1]))
        for stride in (8, 10, 12, 30, 64):
            m = (stride - 6) // 2
            for sr in range(0, m + 1):
                for sw in range(0, m - sr + 1):
                    yield (f"stride={stride} split=({sr},{sw})",
                           w(stride, 0, sr, sw,
                             [(2 << 14) | (7 * (k + 1) % 1024) for k in range(m)]))
        # descending indices: the FALSE arm of `if (this_fd > *max_fd)`
        yield ("descending",
               w(30, 0, 12, 0, [(2 << 14) | (1000 - 80 * k) for k in range(12)]))
        # every entry out of range: R1h must set no bit at all and clamp max_fd
        yield ("all-out-of-range",
               w(30, 0, 12, 0, [(2 << 14) | (1024 + 100 * k) for k in range(12)]))
        # the `%` on the split words, driven past one wrap
        for sr in (0, 13, 26, 39, 65535):
            yield (f"split-wrap sr={sr}",
                   w(30, 0, sr, 65535, [(2 << 14) | (k * 37 % 1024)
                                        for k in range(12)]))

    def selfcheck(self):
        """Six checks, five of them about this row specifically.

        1a. the imperative simulation against the recursive `fdset_fold`, on
            the calls this input actually makes;
        1b. ⚠⚠ the same two implementations on **synthetic windows this file
            builds**, spanning every `ctl`, every tag, both sides of guard
            (b)'s boundary and every split of five strides.
            `PROTOCOL_PHP.md` §A2a rule 2 -- 1a alone is what let ph03 ship a
            model that computed a different function from its own proof;
        2.  ⚠⚠ **THE ARM TABLE, OVER THE CALLS THE DRIVER ACTUALLY MAKES.**
            `inputs/gen.py::_check_span` asserts the same table over EVERY
            window in the file, which is a superset condition: the driver picks
            windows from a checksum-derived index and need not visit them all.
            This is the sharper half and the one that is true of the
            measurement;
        3.  ⚠ every window's result is reproduced by a THIRD, deliberately dumb
            spelling -- collect the set of indices first, then materialise the
            words from it -- so a fold that silently changed range is caught;
        4.  no window of a NON-adversarial input makes any of `99e290f882c9`'s
            three guards fire. That is what "benign" means here and it is what
            `check.py` stage 7h requires of R1h;
        5.  the two constants this row turns on -- `FD_SETSIZE` and `NW` --
            still equal what `c/kernel.c` compiles against. This file writes
            them as Python integers and the C gets them from `<sys/select.h>`;
            check 5 parses the C's own compile-time assertion and compares, so
            the two cannot drift apart in this file's head.
        """
        problems = []
        for c in self.sample_calls(8):
            want = self.fdset_fold(c["buf"], c["off"], c["len"])
            if want != c["result"]:
                problems.append(
                    f"simulated result {c['result']} != fdset_fold() {want} "
                    f"at off={c['off']}")
                break
        for label, win in self._synthetic_windows():
            sim, helper = self._both(win)
            if sim != helper:
                problems.append(
                    f"synthetic window [{label}]: simulated {sim} != "
                    f"fdset_fold() {helper}. The two implementations have come "
                    f"apart OFF the corpus; inputs/ cannot see this and it is "
                    f"why this sweep exists (PROTOCOL_PHP.md A2a rule 2)")
                break

        adversarial = os.path.basename(self.path).startswith("adversarial")
        if not adversarial and self.entered:
            problems += self._arm_table()

        for k in range(self.nwin):
            got = self._win[k][0]
            want = self._dumb(self.buf[k * self.stride:(k + 1) * self.stride])
            if got != want:
                problems.append(f"window {k}: {got} != third spelling {want}")
                break

        if not adversarial:
            for k in range(self.nwin):
                if self._win[k][1] >= 0:
                    problems.append(
                        f"window {k}: an entry's index is >= FD_SETSIZE, so "
                        f"99e290f882c9's guard (b) FIRES. ../spec.md pins all "
                        f"three guards dead on the measured corpus, because "
                        f"check.py stage 7h requires R1h == R1 on every "
                        f"non-adversarial input and a window R1h refuses is one "
                        f"R1 writes out of bounds on")
                    break

        cfd, cnw = _c_constants()
        if (cfd, cnw) != (FD_SETSIZE, NW):
            problems.append(
                f"c/kernel.c compiles against FD_SETSIZE={cfd} NW={cnw}, this "
                f"model uses {FD_SETSIZE}/{NW}; every index in this row means "
                f"something else on such a platform")
        return problems

    def _arm_table(self):
        """`PROTOCOL_PHP.md` §A2a rule 1, over the VISITED calls."""
        tags, idxs, nulls, notarr, sets_seen = set(), set(), set(), set(), set()
        empty_run = full_run = mx_false = False
        seen = set()
        for c in self.iter_calls():
            if c["off"] in seen:
                continue
            seen.add(c["off"])
            win = self.buf[c["off"]:c["off"] + c["len"]]
            ctl, n_r, n_w, n_e, es = self._unpack(win)
            sets = 0
            pos = 0
            for b, n in enumerate((n_r, n_w, n_e)):
                run = es[pos:pos + n]
                pos += n
                if ctl & (1 << b):
                    nulls.add(b)
                    continue
                if ctl & (8 << b):
                    notarr.add(b)
                    continue
                sets += 1
                mx = 0
                for e in run:
                    tags.add(e >> 14)
                    if (e >> 14) >= 2:
                        f = e & 0x3FFF
                        idxs.add(f)
                        if not f > mx:
                            mx_false = True
                        mx = max(mx, f)
            sets_seen.add(sets)
            empty_run |= min(n_r, n_w, n_e) == 0
            full_run |= min(n_r, n_w, n_e) > 0
        bad = []
        if tags != {0, 1, 2, 3}:
            bad.append(f"the VISITED calls reach entry tags {sorted(tags)}, "
                       f"want all of [0, 1, 2, 3]")
        if 0 not in idxs or (FD_SETSIZE - 1) not in idxs:
            bad.append(f"the VISITED calls do not reach both ends of the "
                       f"benign index domain (0 and {FD_SETSIZE - 1})")
        if nulls != {0, 1, 2} or notarr != {0, 1, 2}:
            bad.append(f"the VISITED calls reach `X_array == NULL` for "
                       f"{sorted(nulls)} and `!= IS_ARRAY` for "
                       f"{sorted(notarr)}, want all three of each")
        if 0 not in sets_seen or 3 not in sets_seen:
            bad.append(f"the VISITED calls reach sets == {sorted(sets_seen)}, "
                       f"want both 0 (RETURN_FALSE) and 3 (all three filled)")
        if not (empty_run and full_run):
            bad.append(f"the VISITED calls do not reach both an empty array "
                       f"(got {empty_run}) and three non-empty ones "
                       f"(got {full_run})")
        if not mx_false:
            bad.append("`if (this_fd > *max_fd)` never takes its FALSE arm on a "
                       "VISITED call -- a rung that dropped the test would agree")
        return [f"visited-call arm coverage: {b}" for b in bad]

    @staticmethod
    def _dumb(win):
        """A third spelling of one window's answer: collect the set of indices
        each array legitimately sets, then materialise the sixteen words from
        that set. Deliberately naive, and deliberately NOT sharing `_window`'s
        or `fdset_fold`'s code."""
        ctl, n_r, n_w, n_e, es = Model._unpack(win)
        pos = 0
        sets = 0
        mx = 0
        words = []
        for b, n in enumerate((n_r, n_w, n_e)):
            run = es[pos:pos + n]
            pos += n
            live = set()
            if not (ctl & (1 << b)) and not (ctl & (8 << b)):
                sets += 1
                for e in run:
                    if (e >> 14) in (2, 3):
                        f = e & 0x3FFF
                        if f < FD_SETSIZE:
                            live.add(f)
                        if f > mx:
                            mx = f
            words.append([sum(1 << (f % 64) for f in live if f // 64 == i)
                          for i in range(NW)])
        if mx >= FD_SETSIZE:
            mx = FD_SETSIZE - 1
        if sets == 0:
            return 0xFFFFFFFF
        acc = (0 * 31 + sets) & MASK
        acc = (acc * 31 + mx) & MASK
        for ws in words:
            h = 0
            for v in ws:
                h = (h * 31 + v) & MASK
            acc = (acc * 31 + h) & MASK
        return acc


def _c_constants():
    """(FD_SETSIZE, NW) as `c/kernel.c` literally pins them. Parsed rather than
    trusted: check 5. The C's own compile-time assertion is the source."""
    import re
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "c", "kernel.c")
    txt = open(p).read()
    m = re.search(r"sizeof\(fd_set\)\s*==\s*(\d+)\s*\*\s*sizeof\(unsigned long\)"
                  r"\s*\n?\s*&&\s*FD_SETSIZE\s*==\s*(\d+)", txt)
    n = re.search(r"#define\s+PH16_NWORDS\s+(\d+)", txt)
    if not m or not n or int(m.group(1)) != int(n.group(1)):
        return (None, None)
    return int(m.group(2)), int(n.group(1))


def build(path):
    return Model(path)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        m = build(p)
        print(f"{os.path.basename(p):28s} {m.describe()}  "
              f"exit={m.expected_exit} selfcheck={m.selfcheck()}")
