#!/usr/bin/env python3
"""ph96-outparam-unwritten: the independent reference model the gate checks
against.

The API is documented at the top of `patterns/p01-array-sum/model.py`; this file
notes only where ph96 differs.

    bindings      buf/off/len/buf_len/result. The kernel writes only into a
                  zval of its own frame and returns a `u64`, so there is no
                  destination to bind before and after.
    work_per_call the WINDOW, in bytes -- `stride`, constant across every call
                  on a given input. Argued below.
    sanitizer     derived, not tabulated -- "fires" exactly when some call the
                  driver makes reaches an UNGUARDED release of the
                  `zend_execute_API.c:595` sentinel.

⚠⚠ WHICH ALGORITHM THIS MODEL IMPLEMENTS, BECAUSE IT IS NOT R1's -- AND IT IS
NOT EXACTLY R1h's EITHER, WHICH NO EARLIER ROW HAS HAD TO SAY:

    R1     zend_object_handlers.c as shipped in 5.0.0 -- CRASH-061. TWO
           unguarded releases of the sentinel: `:512-513` (offsetunset, the
           row's cited site) and `:427-429` (offsetexists).
    R1h    + cf020f133487 (Marcus Boerger, 2005-03-19, "- Fix #31185"),
           BACKPORTED: three lines, and they repair `:512-513` ONLY.
    R2-R5  R1h **plus the `:385` guard at `:427`**, because `Option<&Zval>`
           cannot be released without being opened and the `None` arm has to go
           somewhere. That is a FINDING about what the type forces and it is
           declared in `../spec.md`'s divergence ledger.

    THIS MODEL IMPLEMENTS R2-R5, i.e. R1h with the second limb guarded.

⭐ On the WHOLE benign domain the three coincide exactly, because the extra
guard is reachable only from the sentinel state and `inputs/gen.py` refuses a
measured corpus that carries one. The model and R1h therefore agree on every
input the gate measures, and they differ on exactly one state, which
`controls/second_limb.py` drives through all six rungs and records.

Three independent implementations, as p01/p02/p16, ph03, ph07, ph56 and ph97 do:

  * the **simulation** (`_window`) walks each window once with imperative loops
    over integer cursors, mirroring `c/kernel_hardened.c`'s own control flow.
    Per-window results go in a table, which is what makes 20 000 driver
    iterations tractable;
  * the **helper** `ph96_fold` -- the one the derived `ensures` is evaluated
    against -- is built out of RECURSIVE walks with no cursor variable and no
    table, mirroring the Verus spec functions `s_run` / `s_step` / `s_rel` /
    `s_core` / `s_fold_zval` in `../verus.rs` one unfolding at a time;
  * `_dumb`, a third spelling that decides each record's outcome by **dict
    lookup on the decoded `(shape, failed, wrote)` triple** rather than by
    simulating the call through the helper and the handler. That is the one
    spelling that cannot share a control-flow mistake with the other two, and
    control flow is where this row's defect lives.

`selfcheck()` runs them against each other -- on the shipped inputs AND on
synthetic records it builds itself over a domain no input file contains -- and a
disagreement is reported there rather than absorbed into a green line.

⚠⚠ **THE SYNTHETIC SWEEP IS NOT DECORATION.** `PROTOCOL_PHP.md` §A2a rule 2: a
second implementation is only as strong as the domain it is exercised over, and
`inputs/` is not a domain -- it is seven files. ph03 shipped for a full task with
its two implementations computing different functions because its corpus took
one arm of a two-armed branch.
"""

import itertools
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "common-php"))
import slb  # noqa: E402

MASK = (1 << 64) - 1

REC = 16
STRMAX = 10

SHAPE_READ, SHAPE_WRITE, SHAPE_EXISTS, SHAPE_UNSET = 0, 1, 2, 3

# ⚠ TRANSCRIBED FROM `../verus.rs`'s `TYTAB` and `c/kernel.c`'s `ph96_tytab`,
# and `controls/tables.py` diffs all three on every invocation -- a typo here
# would otherwise be a silent disagreement the gate's cross-rung checksum would
# blame on a rung. Upstream's own numbering, Zend/zend.h:302-309.
IS_NULL, IS_LONG, IS_BOOL, IS_STRING = 0, 1, 3, 6
TYTAB = (IS_NULL, IS_LONG, IS_BOOL, IS_STRING)

TAG_READ = 0x11
TAG_UNDEF = 0x12
TAG_WRITE = 0x13
TAG_EXISTS = 0x14
TAG_UNSET = 0x15
TAG_CORE = 0x16


def decode(b):
    """(shape, failed, wrote, ty, lval, slen, payload) for one 16-byte record.

    ⭐ `failed` comes from `b[1]` and `wrote` from `b[2]`, and neither is
    computed from the other: `zend_execute_API.c:592-594`'s comment is upstream
    saying in English that the two come apart."""
    return (b[0] % 4, b[1] % 5 == 0, b[2] % 3 != 0, TYTAB[b[3] % 4], b[4],
            b[5] % 11, b[6:6 + STRMAX])


def _is_true(ty, lval, s):
    """`i_zend_is_true` -- Zend/zend_execute.h:68-112, narrowed to four tags."""
    if ty == IS_NULL:
        return 0
    if ty in (IS_LONG, IS_BOOL):
        return 1 if lval else 0
    if ty == IS_STRING:
        if len(s) == 0 or (len(s) == 1 and s[0:1] == b"0"):
            return 0
        return 1
    return 0


def _fold_zval(acc, ty, lval, s):
    """What the VM goes on to read out of the zval `read_dimension` returns."""
    a = (acc * 31 + ty) & MASK
    if ty == IS_STRING:
        for c in s:
            a = (a * 31 + c) & MASK
        return (a * 31 + 1) & MASK
    return (a * 31 + (lval & 0xFF)) & MASK


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
        self._win = []            # per window: (result, any_unguarded_sentinel)
        self.any_sentinel = False  # some call the driver makes releases the
                                   # :595 sentinel at :427-429 or :512-513
        if not self.truncated:
            self._run()

    # -- implementation 1 of 3: the imperative simulation -------------------
    @staticmethod
    def _call(b, acc, n_rel, n_core):
        """One `$obj[...]` operation. Returns (acc, n_rel, n_core, deref).

        Transcribed from `c/kernel_hardened.c`'s control flow, cursors named as
        the C names them. `deref` records what R1 -- which has neither the
        cf020f133487 no-output switch at `:512` nor any test at `:427` -- would
        do here, and this model does not."""
        shape, failed, wrote, ty, lval, slen, payload = decode(b)
        s = payload[:slen]

        if failed:
            # zend_interfaces.c:81-86 -- the STATUS *is* tested, and this arm
            # is E_CORE_ERROR. Projected onto a tag; ../spec.md itemises it.
            return (acc * 31 + TAG_CORE) & MASK, n_rel, n_core + 1, False

        # zend_call_function wrote the :595 sentinel and returned SUCCESS at
        # :873; `wrote` says whether anything replaced it.
        if shape == SHAPE_WRITE:
            # :413 -- the NO-OUTPUT contract. zend_interfaces.c:89 tests the
            # value itself before releasing it, so the sentinel is harmless.
            if wrote:
                n_rel += 1
            return (acc * 31 + TAG_WRITE) & MASK, n_rel, n_core, False
        if shape == SHAPE_READ:
            # :384-395 -- the OUTPUT contract, GUARDED at :385.
            if not wrote:
                return (acc * 31 + TAG_UNDEF) & MASK, n_rel, n_core, False
            acc = _fold_zval(acc, ty, lval, s)
            # :393 `retval->refcount--` undoes PZVAL_LOCK; the VM takes the
            # value, so this is NOT a release.
            return (acc * 31 + TAG_READ) & MASK, n_rel, n_core, False
        if shape == SHAPE_EXISTS:
            # :427-429 -- the OUTPUT contract, UNGUARDED upstream. The guard on
            # the `not wrote` arm is the ROW'S, not upstream's: see the module
            # docstring and ../spec.md's divergence ledger.
            if not wrote:
                return (acc * 31 + TAG_UNDEF) & MASK, n_rel, n_core, True
            res = _is_true(ty, lval, s)
            n_rel += 1                                     # :429
            return (acc * 31 + TAG_EXISTS + res) & MASK, n_rel, n_core, False
        # :506-517 with cf020f133487 -- the NO-OUTPUT contract, same as :413.
        if wrote:
            n_rel += 1
        return (acc * 31 + TAG_UNSET) & MASK, n_rel, n_core, not wrote

    def _window(self, off):
        """(result, any unguarded sentinel release R1 would perform)."""
        win = self.buf[off: off + self.stride]
        nrec = self.stride // REC
        acc, n_rel, n_core, nd = 0, 0, 0, False
        for r in range(nrec):
            acc, n_rel, n_core, d = self._call(win[r * REC:(r + 1) * REC],
                                               acc, n_rel, n_core)
            nd = nd or d
        return ((acc * 31 + n_rel) * 31 + n_core) & MASK, nd

    # -- simulation --------------------------------------------------------
    def _run(self):
        acc = 0
        if REC <= self.stride <= self.n_blob:
            self.entered = True
            self.nwin = self.n_blob // self.stride
            self._win = [self._window(k * self.stride) for k in range(self.nwin)]
            for _ in range(self.n_iters):
                k = (acc * self.nwin) >> 64
                r, nd = self._win[k]
                if nd:
                    self.any_sentinel = True
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

    # -- implementation 2 of 3: the RECURSIVE one the `ensures` is checked
    #    against. It mirrors ../verus.rs's spec functions one unfolding at a
    #    time and must NOT be the simulation in disguise.
    @staticmethod
    def _s_fold_bytes(acc, s, i=0):
        """../verus.rs `s_fold_bytes`, recursive -- one unfolding per byte."""
        if i >= len(s):
            return (acc * 31 + 1) & MASK
        return Model._s_fold_bytes((acc * 31 + s[i]) & MASK, s, i + 1)

    @staticmethod
    def _s_fold_zval(acc, ty, lval, s):
        """../verus.rs `s_fold_zval`."""
        a = (acc * 31 + ty) & MASK
        if ty == IS_STRING:
            return Model._s_fold_bytes(a, s, 0)
        return (a * 31 + (lval & 0xFF)) & MASK

    @staticmethod
    def _s_true(b):
        """../verus.rs `s_true`."""
        _, _, _, ty, lval, slen, payload = decode(b)
        return _is_true(ty, lval, payload[:slen])

    @staticmethod
    def _s_core(b):
        """../verus.rs `s_core` -- the status guard FIRING (the half of I12/O1
        that upstream does discharge)."""
        return decode(b)[1]

    @staticmethod
    def _s_wrote(b):
        """../verus.rs `s_wrote` -- what `:513` NEEDS decided, and does not."""
        return decode(b)[2]

    @staticmethod
    def _s_shape(b):
        return decode(b)[0]

    @staticmethod
    def _s_rel1(b):
        """../verus.rs `s_rel1` -- did this record release a value exactly once?"""
        sh = Model._s_shape(b)
        if Model._s_core(b) or not Model._s_wrote(b):
            return False
        return sh in (SHAPE_WRITE, SHAPE_EXISTS, SHAPE_UNSET)

    @staticmethod
    def _s_step(b, acc):
        """../verus.rs `s_step`."""
        sh, failed, wrote, ty, lval, slen, payload = decode(b)
        if failed:
            return (acc * 31 + TAG_CORE) & MASK
        if sh == SHAPE_WRITE:
            return (acc * 31 + TAG_WRITE) & MASK
        if sh == SHAPE_READ:
            if not wrote:
                return (acc * 31 + TAG_UNDEF) & MASK
            return (Model._s_fold_zval(acc, ty, lval, payload[:slen]) * 31
                    + TAG_READ) & MASK  # noqa: E501
        if sh == SHAPE_EXISTS:
            if not wrote:
                return (acc * 31 + TAG_UNDEF) & MASK
            return (acc * 31 + TAG_EXISTS + Model._s_true(b)) & MASK
        return (acc * 31 + TAG_UNSET) & MASK

    @staticmethod
    def _s_run(win, r):
        """../verus.rs `s_run`, written as a loop over the same BACKWARD
        recursion. ⚠ A loop rather than Python recursion because `large.bin`'s
        window carries 62 records and the sweep drives more; each step is
        exactly one unfolding of the spec function."""
        acc = 0
        for i in range(r):
            acc = Model._s_step(win[i * REC:(i + 1) * REC], acc)
        return acc

    @staticmethod
    def _s_nrel(win, r):
        n = 0
        for i in range(r):
            if Model._s_rel1(win[i * REC:(i + 1) * REC]):
                n = (n + 1) & MASK
        return n

    @staticmethod
    def _s_ncore(win, r):
        n = 0
        for i in range(r):
            if Model._s_core(win[i * REC:(i + 1) * REC]):
                n = (n + 1) & MASK
        return n

    def ph96_fold(self, buf, off, ln):
        """`s_fold` in ../verus.rs: what the kernel must return."""
        win = buf[off: off + ln]
        nrec = ln // REC
        return (((self._s_run(win, nrec) * 31) + self._s_nrel(win, nrec)) * 31
                + self._s_ncore(win, nrec)) & MASK

    @property
    def helpers(self):
        return {"ph96_fold": self.ph96_fold}

    # -- implementation 3 of 3: decide the outcome by LOOKUP, not by call ----
    #: (shape, failed, wrote) -> (tag, releases?, core?, reads the value?)
    #  ⚠ Written out exhaustively, eight rows, so that a reader can check the
    #  2x2 by eye. The four rows with `wrote == False` are the SENTINEL column
    #  and they are the row: in R1, two of them answer and two of them fault.
    _OUTCOME = {
        (SHAPE_READ, False, True): (TAG_READ, False, False, True),
        (SHAPE_WRITE, False, True): (TAG_WRITE, True, False, False),
        (SHAPE_EXISTS, False, True): (TAG_EXISTS, True, False, "istrue"),
        (SHAPE_UNSET, False, True): (TAG_UNSET, True, False, False),
        (SHAPE_READ, False, False): (TAG_UNDEF, False, False, False),
        (SHAPE_WRITE, False, False): (TAG_WRITE, False, False, False),
        (SHAPE_EXISTS, False, False): (TAG_UNDEF, False, False, False),
        (SHAPE_UNSET, False, False): (TAG_UNSET, False, False, False),
    }

    @staticmethod
    def _dumb(win, stride):
        """A third spelling of one window's answer.

        Deliberately does NOT walk the helper and the four handlers: it decodes
        the record, looks the `(shape, failed, wrote)` triple up in a table and
        applies the row it finds. A control-flow mistake in `_call` or in
        `_s_step` -- which is the class this row's defect belongs to -- cannot
        be shared with a lookup."""
        nrec = stride // REC
        acc, n_rel, n_core = 0, 0, 0
        for r in range(nrec):
            b = win[r * REC:(r + 1) * REC]
            sh, failed, wrote, ty, lval, slen, payload = decode(b)
            if failed:
                acc = (acc * 31 + TAG_CORE) & MASK
                n_core += 1
                continue
            tag, rel, _, reads = Model._OUTCOME[(sh, False, wrote)]
            if reads is True:
                acc = _fold_zval(acc, ty, lval, payload[:slen])
            if rel:
                n_rel += 1
            if reads == "istrue":
                tag = tag + _is_true(ty, lval, payload[:slen])
            acc = (acc * 31 + tag) & MASK
        return ((acc * 31 + n_rel) * 31 + n_core) & MASK

    # -- what the kernel must do, per call ---------------------------------
    @property
    def work_per_call(self):
        """The window, in bytes -- `stride` -- from the file alone.

        **Why the window and not the record count.** `check.py::
        check_marginal_ir` needs one scalar per input and hard-fails on
        `work_per_call = 0`. The record count IS `stride // 16`, an exact
        (floor-)linear function of the stride, so the two denominators differ by
        a constant factor and the stride is the one the payload header fixes and
        the attacker cannot move. It is a strict over-estimate -- a call touches
        16 bytes per record and does between one branch and a ten-byte fold --
        and an over-estimate raises the derived floor, which is the direction a
        floor should err.

        ⚠ The per-record work is NOT constant: a record whose call fails does
        one branch, one whose `read_dimension` returns a ten-byte string folds
        ten bytes, and one whose `unset_dimension` succeeds does a refcount
        decrement and nothing else. `../NOTES.md` section 9 decomposes the
        marginal rather than presenting it as a per-byte rate."""
        return self.stride if self.entered else 0

    # -- sanitizer expectation ---------------------------------------------
    @property
    def sanitizer_expect(self):
        """Derived from the simulated run, never tabulated per file.

        "fires" iff some call **the driver actually makes** releases the
        `zend_execute_API.c:595` sentinel through an UNGUARDED site -- i.e. some
        visited window carries a record with `failed == False and wrote ==
        False` whose shape is `exists` (`:427-429`) or `unset` (`:512-513`).
        R1 then writes through address 0x10 (or reads 0x14 first); every other
        rung answers.

        ⚠ Note "the driver makes": windows are picked from a checksum-derived
        index, so a hostile window that is never selected must not be declared.
        That is why every adversarial input has exactly one window --
        `inputs/gen.py`. (`adversarial-nowin.bin` has ZERO, which is its whole
        point, and declares `clean`.)

        ⭐ The fault address is a STRUCT OFFSET rather than zero, and it is
        pinned at build time: `c/kernel.c` carries negative-array-size
        assertions holding `offsetof(zval, refcount) == 0x10` and
        `offsetof(zval, type) == 0x14`, which is what `Zend/zend.h:287-293`
        gives on LP64 and what a real PHP 5.0.0 CLI faults at (`../NOTES.md`
        section 2). A low, unmapped address on every platform this tree builds
        for."""
        return "fires" if self.any_sentinel else "clean"

    # -- what a conforming driver does -------------------------------------
    @property
    def expected_exit(self):
        # ph96's payload allocates nothing -- the zval is a frame object and the
        # type table is static -- so p02's exit 7 has no analogue here.
        # `slb_load` rejecting a short file is the only non-zero exit this
        # pattern's driver produces.
        return 5 if self.truncated else 0

    @property
    def expected_stdout(self):
        return "" if self.checksum is None else f"{self.checksum}\n"

    def describe(self):
        return (f"n_iters={self.n_iters} stride={self.stride} "
                f"n_blob={self.n_blob} nwin={self.nwin} "
                f"recs/win={self.stride // REC} "
                f"calls={self.n_calls} work/call={self.work_per_call}B "
                f"san={self.sanitizer_expect} sentinel={self.any_sentinel} "
                f"truncated={self.truncated} expected={self.checksum}")

    # -- driving ALL THREE implementations on records no input file contains --
    @staticmethod
    def _both(win, stride):
        """(simulated, ph96_fold, dumb) for an arbitrary window, off-corpus.

        `Model.__new__` skips `__init__` deliberately: `_window` and
        `ph96_fold` read only `buf` and `stride`, so this drives the SHIPPED
        code paths on bytes chosen here rather than on bytes `inputs/` happens
        to carry."""
        m = Model.__new__(Model)
        m.buf, m.stride = win, stride
        return (m._window(0)[0], m.ph96_fold(win, 0, stride),
                Model._dumb(win, stride))

    @staticmethod
    def _rec(shape, failed, wrote, ty=0, lval=0, s=b"", pad=0xAA):
        """One 16-byte record with the residues named directly.

        `failed` is `b[1] % 5 == 0` and `wrote` is `b[2] % 3 != 0`, so `0`/`1`
        are the canonical raw bytes for each."""
        assert len(s) <= STRMAX
        return (bytes((shape, 0 if failed else 1, 1 if wrote else 0, ty,
                       lval & 0xFF, len(s))) + s
                + bytes((pad,)) * (STRMAX - len(s)))

    @staticmethod
    def _synthetic_windows():
        """Records spanning a domain `inputs/` cannot, built here, yielded as
        (label, window, stride). ⚠ **`inputs/` is not the domain and must never
        be mistaken for it** -- see the module docstring.

        Five families, each isolating one thing the implementations could
        disagree about:

          a. the WHOLE (shape x failed x wrote) cross product, 4 x 2 x 2 = 16 --
             which is the row's own independence claim driven exhaustively, and
             it INCLUDES the four sentinel cells `inputs/` may not carry;
          b. every Z_TYPE tag against every truth value of `lval`;
          c. the three IS_STRING arms of `i_zend_is_true` and the whole length
             domain 0..10, on payloads whose tail is junk;
          d. a string whose first byte is `'0'` at every length, because
             `zend_execute.h:86` tests `len == 1 && val[0] == '0'` and a rung
             that dropped either conjunct agrees everywhere else;
          e. degenerate strides: one record, two, and a stride with a large
             trailing partial record that no rung may read.
        """
        R = Model._rec

        def w(recs, stride=None):
            b = b"".join(recs)
            return b + b"\xAA" * ((stride or len(b) + 2) - len(b))

        # a. the whole (shape x failed x wrote) cross product
        for sh in range(4):
            for fl in (False, True):
                for wr in (False, True):
                    yield (f"shape={sh} failed={fl} wrote={wr}",
                           w([R(sh, fl, wr, 3, 1, b"abc"),
                              R((sh + 1) % 4, fl, wr, 0, 0, b""),
                              R(sh, not fl, not wr, 2, 7, b"z")]), 50)

        # b. every Z_TYPE tag against every truth value
        for ty in range(4):
            for lval in (0, 1, 255):
                for sh in (SHAPE_READ, SHAPE_EXISTS):
                    yield (f"ty={ty} lval={lval} shape={sh}",
                           w([R(sh, False, True, ty, lval, b"q"),
                              R(sh, False, True, ty, lval, b"")]), 34)

        # c. the length domain end to end
        base = b"0123456789"
        for ln in range(STRMAX + 1):
            yield (f"len={ln}",
                   w([bytes((SHAPE_EXISTS, 1, 1, 3, 0, ln)) + base,
                      bytes((SHAPE_READ, 1, 1, 3, 0, ln)) + base]), 34)

        # d. a payload whose first byte is '0', at every length
        z = b"0aaaaaaaaa"
        for ln in range(STRMAX + 1):
            yield (f"zero-prefix len={ln}",
                   w([bytes((SHAPE_EXISTS, 1, 1, 3, 0, ln)) + z,
                      bytes((SHAPE_EXISTS, 1, 1, 3, 0, ln)) + b"a" + z[1:]]),
                   34)

        # e. degenerate strides, including a long trailing partial record
        for stride in (16, 17, 31, 32, 33, 47, 63, 95):
            recs = [R(k % 4, k % 3 == 0, k % 2 == 1, k % 4, k, b"xy"[:k % 3])
                    for k in range(stride // REC)]
            yield (f"stride={stride}", w(recs, stride), stride)

    def selfcheck(self):
        """Five checks, four of them about this row specifically."""
        bad = []

        # 1. the three implementations agree on every window of this file
        if self.entered:
            for k in range(self.nwin):
                off = k * self.stride
                win = self.buf[off:off + self.stride]
                a, b, c = self._both(win, self.stride)
                if not (a == b == c):
                    bad.append(f"window {k}: simulation {a}, ph96_fold {b}, "
                               f"dumb {c}")
                    break

        # 2. ... and on a domain the corpus cannot reach (A2a rule 2)
        n_syn = 0
        for lab, win, stride in self._synthetic_windows():
            n_syn += 1
            a, b, c = self._both(win, stride)
            if not (a == b == c):
                bad.append(f"synthetic [{lab}]: simulation {a}, ph96_fold {b}, "
                           f"dumb {c}")
                break
        if n_syn < 60:
            bad.append(f"the synthetic sweep built only {n_syn} windows; that "
                       f"is not a domain")

        # 3. ⛔ THE DEFECT, AS AN ASSERTION. `failed` and `wrote` must be able to
        #    take all four combinations, and the one that matters is
        #    SUCCESS-with-nothing-written -- zend_execute_API.c:592-595. A model
        #    that derived either bit from the other would fail here, which is
        #    the catalogue's own `⚠ risk` note turned into a check.
        seen = set()
        for raw1 in range(256):
            for raw2 in range(256):
                seen.add((raw1 % 5 == 0, raw2 % 3 != 0))
        if seen != {(False, False), (False, True), (True, False), (True, True)}:
            bad.append(f"the record encoding reaches only {sorted(seen)} of the "
                       f"four (failed, wrote) combinations; the two bits are "
                       f"not independent and the row has been deleted")
        s_unset = self._rec(SHAPE_UNSET, False, False)
        if self._s_core(s_unset) or self._s_wrote(s_unset):
            bad.append("the model cannot express SUCCESS-with-nothing-written, "
                       "which is zend_execute_API.c:592-595 and the whole row")
        if self._s_rel1(s_unset):
            bad.append("the model releases a value the callee never wrote; "
                       "I16/O2 is *the outputs of an aborted call must not be "
                       "destroyed*")

        # 4. the guarded and unguarded cells of the 2x2 really differ, and the
        #    difference is exactly which shapes fault in R1.
        for sh, want in ((SHAPE_READ, False), (SHAPE_WRITE, False),
                         (SHAPE_EXISTS, True), (SHAPE_UNSET, True)):
            b = self._rec(sh, False, False)
            got = self._call(b, 0, 0, 0)[3]
            if got != want:
                bad.append(f"shape {sh} on the sentinel: model says R1 "
                           f"dereferences={got}, want {want} -- the 2x2 is "
                           f"read :385 GUARDED, write :413 NO-OUTPUT, exists "
                           f":427 UNGUARDED, unset :512 UNGUARDED")

        # 5. arm coverage over the calls the DRIVER MAKES, which is sharper
        #    than inputs/gen.py's per-file assertion (A2a rule 1)
        bad += self._visited_arms()
        return bad

    def _visited_arms(self):
        """Every arm the VISITED calls reach -- the sharper half of A2a rule 1."""
        if not self.entered:
            return []
        shapes, statwrote, tys, scalars, strarms, lens = (set(), set(), set(),
                                                          set(), set(), set())
        for c in self.sample_calls(4096):
            win = self.buf[c["off"]:c["off"] + c["len"]]
            for r in range(c["len"] // REC):
                b = win[r * REC:(r + 1) * REC]
                sh, fl, wr, ty, lv, ln, pay = decode(b)
                shapes.add(sh)
                statwrote.add((fl, wr))
                if not fl and wr:
                    tys.add(ty)
                    lens.add(ln)
                    if ty in (IS_LONG, IS_BOOL):
                        scalars.add(1 if lv else 0)
                    if ty == IS_STRING:
                        s = pay[:ln]
                        strarms.add("empty" if ln == 0 else
                                    "zero" if (ln == 1 and s[0:1] == b"0")
                                    else "other")
        bad = []
        # ⚠ MEASURED CORPUS ONLY. The adversarial files have exactly ONE window
        # each by construction (`inputs/gen.py`), so they cannot span the arm
        # table and must not be asked to: a one-window probe is not a corpus.
        # `nwin >= 2` is the test, not the stride -- `small.bin` and
        # `adversarial-unset.bin` share a stride and differ in windows.
        if self.nwin >= 2:
            if shapes != {0, 1, 2, 3}:
                bad.append(f"the VISITED calls reach shapes {sorted(shapes)}, "
                           f"want all four")
            if statwrote != {(True, False), (True, True), (False, True)}:
                bad.append(f"the VISITED calls reach (failed, wrote) "
                           f"{sorted(statwrote)}, want exactly "
                           f"{{(True, False), (True, True), (False, True)}} -- "
                           f"(False, False) is ADVERSARIAL")
            if tys != set(TYTAB):
                bad.append(f"the VISITED calls reach Z_TYPE {sorted(tys)}, "
                           f"want all four of {sorted(TYTAB)}")
            if scalars != {0, 1}:
                bad.append("the VISITED calls reach only one truth value on "
                           "the IS_LONG/IS_BOOL arm")
            if strarms != {"empty", "zero", "other"}:
                bad.append(f"the VISITED calls reach IS_STRING arms "
                           f"{sorted(strarms)}, want all three")
            if 0 not in lens or STRMAX not in lens:
                bad.append("the VISITED calls do not reach both ends of the "
                           "Z_STRLEN domain")
        return bad


def build(path):
    return Model(path)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        m = build(p)
        print(f"{os.path.basename(p):30s} {m.describe()}  "
              f"exit={m.expected_exit} selfcheck={m.selfcheck()}")
