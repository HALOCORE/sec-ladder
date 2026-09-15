#!/usr/bin/env python3
"""ph97-optarg-unwritten: the independent reference model the gate checks against.

The API is documented at the top of `patterns/p01-array-sum/model.py`; this file
notes only where ph97 differs.

    bindings      buf/off/len/buf_len/result. The kernel writes only into a
                  21-byte frame of its own and returns a `u64`, so there is no
                  destination to bind before and after.
    work_per_call the WINDOW, in bytes -- `stride`, constant across every call
                  on a given input. Argued below.
    sanitizer     derived, not tabulated -- "fires" exactly when some call the
                  driver makes reaches `mbstring.c:3219` with `typ == NULL`.

⚠⚠ WHICH ALGORITHM THIS MODEL IMPLEMENTS, BECAUSE IT IS NOT R1's. It is
`PHP_FUNCTION(mb_get_info)` **with the upstream fix applied**, which is exactly
`c/kernel_hardened.c` and exactly R2-R5:

    R1     mbstring.c:3209-3252 as shipped in 5.0.0 -- CRASH-126
    R1h    + f7326d627962 (Antony Dovgal, 2005-01-28, "MFB: fix #31732"),
           ONE LINE: `if (!typ || !strcasecmp("all", typ))`
    R2-R5  the same function, memory-safe

⭐ The fix is COMPLETE: it removes the only dereference of the unwritten
out-parameter and changes no benign answer, so R1h and R2-R5 implement one
function and only R1 diverges -- and it diverges on ONE input, the one R1 faults
on. `controls/widened_domain.py` measures that rather than asserting it.

Three independent implementations, as p01/p02/p16, ph03, ph07 and ph56 do:

  * the **simulation** (`_window`) walks each window once with imperative loops
    over integer cursors, mirroring `c/kernel.c`'s own control flow. Per-window
    results go in a table, which is what makes 20 000 driver iterations
    tractable;
  * the **helper** `ph97_fold` -- the one the derived `ensures` is evaluated
    against -- is built out of RECURSIVE walks with no cursor variable and no
    table, mirroring the Verus spec functions `s_run` / `s_step` / `s_cmp` /
    `s_fold_str` in `../verus.rs` one unfolding at a time;
  * `_dumb`, a third spelling that decides the selector by **dict lookup on the
    decoded, case-folded, NUL-truncated argument** rather than by walking the
    five-arm `strcasecmp` chain. That is the one spelling that cannot share a
    chain-order mistake with the other two -- and chain ORDER is load-bearing
    here, because upstream tries `all` first.

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

REC = 24
STRMAX = 20
NTYP = 21

IS_NULL, IS_BOOL, IS_STRING, IS_ARRAY = 0, 1, 2, 3

TAG_FALSE = 0x0F
TAG_ALL = 0x0A
TAG_SEL = (0x10, 0x11, 0x12, 0x13)

# ⚠ TRANSCRIBED FROM `../verus.rs`'s `SELS` / `NAMES` AND `c/kernel.c`'s
# `ph97_sels` / `ph97_enc_name`, and `controls/tables.py` diffs all three on
# every invocation -- a typo here would otherwise be a silent disagreement the
# gate's cross-rung checksum would blame on a rung.
SELS = (b"all", b"internal_encoding", b"http_input", b"http_output",
        b"func_overload")
NAMES = (b"", b"pass", b"ISO-8859-1")

ENC_INVALID, ENC_PASS, ENC_8859_1 = 0, 1, 2
G_INTERNAL, G_HTTP_IN, G_HTTP_OUT, G_OVERLOAD = (ENC_8859_1, ENC_INVALID,
                                                 ENC_PASS, ENC_PASS)

# `mb_get_info`'s type spec -- mbstring.c:3215. The `|` is FIRST.
SPEC = b"|s"


def _pad(s):
    """NUL-pad a body out to the frame width, as every rung's frame is."""
    return bytes(s) + b"\0" * (NTYP - len(s))


def _lower(c):
    return c + 32 if 65 <= c <= 90 else c


def _cmp(a, b):
    """`strcasecmp(3)` over two frame-width operands, iteratively."""
    for i in range(NTYP):
        ca, cb = _lower(a[i]), _lower(b[i])
        if ca != cb:
            return ca - cb
        if ca == 0:
            return 0
    return 0


def _fold_str(acc, s):
    """Fold one NUL-terminated name, terminator included."""
    for c in s:
        if c == 0:
            break
        acc = (acc * 31 + c) & MASK
    return (acc * 31 + 1) & MASK


def decode(b):
    """(num_args, ty, arg_len, lval, payload) for one 24-byte record."""
    return (b[0] % 3, b[1] % 4, b[2] % 21, b[3], b[4:4 + STRMAX])


def _scan(spec):
    """`zend_parse_va_args`'s spec scanner -- zend_API.c:474-509.

    ⛔ Returns `(min_num_args, max_num_args)` or `None` for the bad-specifier
    arm at `:503`. It is written out rather than hardcoded to `(0, 1)` because
    the ORDER of the characters is the defect: `'|'` FIRST sets `min` from a
    `max` that is still zero."""
    mn, mx = -1, 0
    for c in spec:
        if c in b"ldsbraoOzZ":
            mx += 1
        elif c == ord("|"):
            mn = mx
        elif c in b"/!":
            pass
        else:
            return None
    if mn < 0:
        mn = mx
    return (mn, mx)


def _body(ty, lval, ln, payload):
    """`convert_to_string_ex`'s result -- zend_API.c:302-317.

    ⭐ The IS_NULL arm FALLS THROUGH, because `"|s"` carries no `!` and so
    `return_null` is 0 at `:303`. The null VALUE therefore becomes the EMPTY
    STRING and not NULL -- which is why `mb_get_info(null)` answers `bool(false)`
    on the measured 5.0.0 CLI while `mb_get_info()` faults."""
    if ty == IS_STRING:
        return payload[:ln]
    if ty == IS_BOOL:
        return b"1" if (lval % 2 == 1) else b""
    return b""  # IS_NULL


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
        self._win = []            # per window: (result, any_null_deref)
        self.any_absent = False   # some call the driver makes reaches :3219
                                  # with typ == NULL
        if not self.truncated:
            self._run()

    # -- implementation 1 of 3: the imperative simulation -------------------
    @staticmethod
    def _call(b, acc, falses):
        """One `mb_get_info(...)`, R1h. Returns (acc, falses, null_deref).

        Transcribed from `c/kernel_hardened.c`'s control flow, cursors named as
        the C names them. `null_deref` records what R1 -- which has no
        `!typ ||` -- would do here, and this model does not."""
        num_args, ty, ln, lval, payload = decode(b)

        # zend_parse_va_args, zend_API.c:463-549
        mm = _scan(SPEC)
        if mm is None:
            return (acc * 31 + TAG_FALSE) & MASK, falses + 1, False
        mn, mx = mm
        if num_args < mn or num_args > mx:                 # :511
            return (acc * 31 + TAG_FALSE) & MASK, falses + 1, False
        typ = None                                         # mbstring.c:3211
        for _ in range(num_args):                          # :537
            if ty == IS_ARRAY:                             # zend_API.c:330
                return (acc * 31 + TAG_FALSE) & MASK, falses + 1, False
            typ = _pad(_body(ty, lval, ln, payload))       # :315-316

        # mbstring.c:3219 -- and THE DEFECT is that R1 has no `typ is None` arm
        null_deref = typ is None
        if typ is None or _cmp(_pad(SELS[0]), typ) == 0:
            acc = (acc * 31 + TAG_ALL) & MASK              # :3220
            for k, enc in ((1, G_INTERNAL), (2, G_HTTP_IN), (3, G_HTTP_OUT),
                           (4, G_OVERLOAD)):
                acc = _fold_str((acc * 31 + k) & MASK, _pad(SELS[k]))
                acc = _fold_str(acc, _pad(NAMES[enc]))
            return acc, falses, null_deref
        for k, enc in ((1, G_INTERNAL), (2, G_HTTP_IN), (3, G_HTTP_OUT),
                       (4, G_OVERLOAD)):
            if _cmp(_pad(SELS[k]), typ) == 0:              # :3233 .. :3245
                return (_fold_str((acc * 31 + TAG_SEL[k - 1]) & MASK,
                                  _pad(NAMES[enc])), falses, null_deref)
        return (acc * 31 + TAG_FALSE) & MASK, falses + 1, null_deref  # :3250

    def _window(self, off):
        """(result, any null dereference R1 would perform) for one window."""
        win = self.buf[off: off + self.stride]
        nrec = self.stride // REC
        acc, falses, nd = 0, 0, False
        for r in range(nrec):
            acc, falses, d = self._call(win[r * REC:(r + 1) * REC], acc, falses)
            nd = nd or d
        return (acc * 31 + falses) & MASK, nd

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
                    self.any_absent = True
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
    def _s_cmp(a, b, i=0):
        """../verus.rs `s_cmp`, recursive."""
        if i >= NTYP:
            return 0
        ca, cb = _lower(a[i]), _lower(b[i])
        if ca != cb:
            return ca - cb
        if ca == 0:
            return 0
        return Model._s_cmp(a, b, i + 1)

    @staticmethod
    def _s_fold_str(acc, s, i=0):
        """../verus.rs `s_fold_str`, recursive."""
        if i >= NTYP or s[i] == 0:
            return (acc * 31 + 1) & MASK
        return Model._s_fold_str((acc * 31 + s[i]) & MASK, s, i + 1)

    @staticmethod
    def _s_frame(b):
        """../verus.rs `s_frame`."""
        num_args, ty, ln, lval, payload = decode(b)
        return _pad(_body(ty, lval, ln, payload))

    @staticmethod
    def _s_ok(b):
        """../verus.rs `s_ok` -- what the `:3215` guard decides."""
        num_args, ty, _, _, _ = decode(b)
        return num_args <= 1 and (num_args == 0 or ty != IS_ARRAY)

    @staticmethod
    def _s_wrote(b):
        """../verus.rs `s_wrote` -- what `:3219` NEEDS decided, and does not."""
        return decode(b)[0] == 1

    @staticmethod
    def _s_all(acc):
        """../verus.rs `s_all`."""
        a = (acc * 31 + TAG_ALL) & MASK
        for k, enc in ((1, G_INTERNAL), (2, G_HTTP_IN), (3, G_HTTP_OUT),
                       (4, G_OVERLOAD)):
            a = Model._s_fold_str((a * 31 + k) & MASK, _pad(SELS[k]))
            a = Model._s_fold_str(a, _pad(NAMES[enc]))
        return a

    @staticmethod
    def _s_step(b, acc):
        """../verus.rs `s_step`."""
        if not Model._s_ok(b):
            return (acc * 31 + TAG_FALSE) & MASK
        t = Model._s_frame(b)
        if (not Model._s_wrote(b)) or Model._s_cmp(_pad(SELS[0]), t) == 0:
            return Model._s_all(acc)
        for k, enc in ((1, G_INTERNAL), (2, G_HTTP_IN), (3, G_HTTP_OUT),
                       (4, G_OVERLOAD)):
            if Model._s_cmp(_pad(SELS[k]), t) == 0:
                return Model._s_fold_str((acc * 31 + TAG_SEL[k - 1]) & MASK,
                                         _pad(NAMES[enc]))
        return (acc * 31 + TAG_FALSE) & MASK

    @staticmethod
    def _s_false(b):
        """../verus.rs `s_false`."""
        if not Model._s_ok(b):
            return True
        t = Model._s_frame(b)
        if not Model._s_wrote(b):
            return False
        return all(Model._s_cmp(_pad(s), t) != 0 for s in SELS)

    @staticmethod
    def _s_run(win, r):
        """../verus.rs `s_run`, written as a loop over the same BACKWARD
        recursion. ⚠ A loop rather than Python recursion because `large.bin`'s
        window carries 43 records and the sweep drives far more; each step is
        exactly one unfolding of the spec function."""
        acc = 0
        for i in range(r):
            acc = Model._s_step(win[i * REC:(i + 1) * REC], acc)
        return acc

    @staticmethod
    def _s_nfalse(win, r):
        n = 0
        for i in range(r):
            if Model._s_false(win[i * REC:(i + 1) * REC]):
                n = (n + 1) & MASK
        return n

    def ph97_fold(self, buf, off, ln):
        """`s_fold` in ../verus.rs: what the kernel must return."""
        win = buf[off: off + ln]
        nrec = ln // REC
        return ((self._s_run(win, nrec) * 31) + self._s_nfalse(win, nrec)) & MASK

    @property
    def helpers(self):
        return {"ph97_fold": self.ph97_fold}

    # -- implementation 3 of 3: decide the selector by LOOKUP, not by chain --
    @staticmethod
    def _dumb(win, stride):
        """A third spelling of one window's answer.

        Deliberately does NOT walk the five-arm chain: it decodes the argument,
        truncates it at its first NUL the way `strcasecmp` does, lower-cases it
        and looks it up in a dict. ⚠ Chain ORDER is load-bearing upstream --
        `all` is tried first -- and the five selectors are pairwise distinct, so
        a lookup and a chain agree; a rung that reordered the chain would not
        show up here, and `controls/tables.py` is what pins the order."""
        table = {s.lower(): i for i, s in enumerate(SELS)}
        assert len(table) == len(SELS), "the selectors are not pairwise distinct"
        nrec = stride // REC
        acc, falses = 0, 0
        for r in range(nrec):
            b = win[r * REC:(r + 1) * REC]
            num_args, ty, ln, lval, payload = decode(b)
            if num_args > 1 or (num_args == 1 and ty == IS_ARRAY):
                acc = (acc * 31 + TAG_FALSE) & MASK
                falses += 1
                continue
            if num_args == 0:
                key = None
            else:
                s = _body(ty, lval, ln, payload)
                key = s.split(b"\0", 1)[0].lower()
            k = None if key is None else table.get(key)
            if key is None or k == 0:
                acc = (acc * 31 + TAG_ALL) & MASK
                for j, enc in ((1, G_INTERNAL), (2, G_HTTP_IN), (3, G_HTTP_OUT),
                               (4, G_OVERLOAD)):
                    acc = _fold_str((acc * 31 + j) & MASK, _pad(SELS[j]))
                    acc = _fold_str(acc, _pad(NAMES[enc]))
            elif k is not None:
                enc = (G_INTERNAL, G_HTTP_IN, G_HTTP_OUT, G_OVERLOAD)[k - 1]
                acc = _fold_str((acc * 31 + TAG_SEL[k - 1]) & MASK,
                                _pad(NAMES[enc]))
            else:
                acc = (acc * 31 + TAG_FALSE) & MASK
                falses += 1
        return (acc * 31 + falses) & MASK

    # -- what the kernel must do, per call ---------------------------------
    @property
    def work_per_call(self):
        """The window, in bytes -- `stride` -- from the file alone.

        **Why the window and not the record count.** `check.py::
        check_marginal_ir` needs one scalar per input and hard-fails on
        `work_per_call = 0`. The record count IS `stride // 24`, an exact
        (floor-)linear function of the stride, so the two denominators differ by
        a constant factor and the stride is the one the payload header fixes and
        the attacker cannot move. It is a strict over-estimate -- a call touches
        24 bytes per record and does between one and five 21-byte compares --
        and an over-estimate raises the derived floor, which is the direction a
        floor should err.

        ⚠ The per-record work is NOT constant: a record whose argument matches
        `all` does one compare and eight folds, one that matches nothing does
        five compares and no fold. `../NOTES.md` §8 decomposes the marginal
        rather than presenting it as a per-byte rate."""
        return self.stride if self.entered else 0

    # -- sanitizer expectation ---------------------------------------------
    @property
    def sanitizer_expect(self):
        """Derived from the simulated run, never tabulated per file.

        "fires" iff some call **the driver actually makes** reaches
        `mbstring.c:3219` with `typ == NULL` -- i.e. some visited window carries
        a record with `num_args == 0` that gets past the `:3215` guard. R1 then
        reads address 0 and ASan reports `SEGV on unknown address
        0x000000000000`; every other rung answers.

        ⚠ Note "the driver makes": windows are picked from a checksum-derived
        index, so a hostile window that is never selected must not be declared.
        That is why every adversarial input has exactly one window --
        `inputs/gen.py`. (`adversarial-nowin.bin` has ZERO, which is its whole
        point, and declares `clean`.)

        ⭐ There is no redzone question on this row and no silent variant: the
        fault address is 0, it is unmapped on every platform this tree builds
        for, and `../NOTES.md` §1 records the same address coming out of a real
        PHP 5.0.0 CLI."""
        return "fires" if self.any_absent else "clean"

    # -- what a conforming driver does -------------------------------------
    @property
    def expected_exit(self):
        # ph97's payload allocates nothing -- the frame and both tables are
        # fixed-size objects -- so p02's exit 7 has no analogue here.
        # `slb_load` rejecting a short file is the only non-zero exit this
        # pattern's driver produces.
        return 5 if self.truncated else 0

    @property
    def expected_stdout(self):
        return "" if self.checksum is None else f"{self.checksum}\n"

    def describe(self):
        return (f"n_iters={self.n_iters} stride={self.stride} "
                f"n_blob={self.n_blob} nwin={self.nwin} recs/win={self.stride // REC} "
                f"calls={self.n_calls} work/call={self.work_per_call}B "
                f"san={self.sanitizer_expect} absent={self.any_absent} "
                f"truncated={self.truncated} expected={self.checksum}")

    # -- driving ALL THREE implementations on records no input file contains --
    @staticmethod
    def _both(win, stride):
        """(simulated, ph97_fold, dumb) for an arbitrary window, off-corpus.

        `Model.__new__` skips `__init__` deliberately: `_window` and
        `ph97_fold` read only `buf` and `stride`, so this drives the SHIPPED
        code paths on bytes chosen here rather than on bytes `inputs/` happens
        to carry."""
        m = Model.__new__(Model)
        m.buf, m.stride = win, stride
        return (m._window(0)[0], m.ph97_fold(win, 0, stride),
                Model._dumb(win, stride))

    @staticmethod
    def _rec(num_args, ty, s=b"", lval=0, pad=0xAA):
        """One 24-byte record with the residues named directly."""
        assert len(s) <= STRMAX
        return (bytes((num_args, ty, len(s), lval)) + s
                + bytes((pad,)) * (STRMAX - len(s)))

    @staticmethod
    def _synthetic_windows():
        """Records spanning a domain `inputs/` cannot, built here, yielded as
        (label, window, stride). ⚠ **`inputs/` is not the domain and must never
        be mistaken for it** -- see the module docstring.

        Six families, each isolating one thing the implementations could
        disagree about:

          a. the WHOLE (num_args x type) cross product, 3 x 4 = 12 -- which is
             the row's own independence claim driven exhaustively;
          b. every selector, in five casings, plus every one-character mutation
             of `all` -- so the chain's first arm and its neighbours are
             separated;
          c. the length domain end to end, `arg_len` 0..20, on a payload that
             spells a selector and then continues, so truncation is what decides;
          d. embedded NULs at every position 0..20 of a payload that would
             otherwise match `internal_encoding`;
          e. both IS_BOOL values and IS_NULL, whose bodies are `"1"`, `""` and
             `""` -- three ways to reach the unmatched arm and one to reach
             nothing else;
          f. degenerate strides: one record, two, and a stride with a large
             trailing partial record that no rung may read.
        """
        R = Model._rec

        def w(recs, stride=None):
            b = b"".join(recs)
            return b + b"\xAA" * ((stride or len(b) + 2) - len(b))

        # a. the whole (num_args x type) cross product
        for na in range(3):
            for ty in range(4):
                yield (f"argc={na} ty={ty}",
                       w([R(na, ty, b"all", 1), R(na, ty, b"", 0),
                          R(1, IS_STRING, b"http_input")]), 74)

        # b. every selector, five casings, and one-character mutations of `all`
        for s in SELS:
            for lab, v in (("lower", s.lower()), ("upper", s.upper()),
                           ("title", s.title()), ("mixed", bytes(
                               c ^ 0x20 if i % 2 else c for i, c in enumerate(s))),
                           ("swap", s.swapcase())):
                yield (f"sel={s.decode()} case={lab}",
                       w([R(1, IS_STRING, v), R(1, IS_STRING, b"all")]), 50)
        for i in range(3):
            for c in (b"a", b"l", b"A", b"L", b"z", b"\x00"):
                v = b"all"[:i] + c + b"all"[i + 1:]
                yield (f"mutate all[{i}]={c!r}",
                       w([R(1, IS_STRING, v), R(0, IS_STRING, b"all")]), 50)

        # c. the length domain, on a payload that spells a selector then goes on
        base = b"internal_encodingXYZ"
        for ln in range(STRMAX + 1):
            yield (f"len={ln}",
                   w([bytes((1, IS_STRING, ln, 0)) + base,
                      R(2, IS_STRING, b"all")]), 50)

        # d. an embedded NUL at every position
        for p in range(STRMAX):
            v = bytearray(b"internal_encodingQQQ")
            v[p] = 0
            yield (f"nul@{p}",
                   w([bytes((1, IS_STRING, STRMAX, 0)) + bytes(v),
                      R(1, IS_NULL, b"")]), 50)

        # e. the three empty-ish bodies
        for ty, lval in ((IS_BOOL, 0), (IS_BOOL, 1), (IS_NULL, 0), (IS_NULL, 1)):
            yield (f"ty={ty} lval={lval}",
                   w([R(1, ty, b"", lval), R(0, IS_BOOL, b"", lval)]), 50)

        # f. degenerate strides, including a long trailing partial record
        for stride in (24, 25, 47, 48, 49, 71, 95):
            recs = [R(k % 3, (k + 1) % 4, SELS[k % len(SELS)])
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
                    bad.append(f"window {k}: simulation {a}, ph97_fold {b}, "
                               f"dumb {c}")
                    break

        # 2. ... and on a domain the corpus cannot reach (A2a rule 2)
        n_syn = 0
        for lab, win, stride in self._synthetic_windows():
            n_syn += 1
            a, b, c = self._both(win, stride)
            if not (a == b == c):
                bad.append(f"synthetic [{lab}]: simulation {a}, ph97_fold {b}, "
                           f"dumb {c}")
                break
        if n_syn < 100:
            bad.append(f"the synthetic sweep built only {n_syn} windows; that "
                       f"is not a domain")

        # 3. the spec scanner really does what the row says it does. ⛔ THIS IS
        #    THE DEFECT, AS AN ASSERTION: `"|s"` gives min 0 and max 1, so a
        #    call with ZERO arguments passes the count test at zend_API.c:511.
        if _scan(b"|s") != (0, 1):
            bad.append(f'_scan(b"|s") == {_scan(b"|s")}, want (0, 1) -- the '
                       f'`|` is FIRST, so min_num_args is set from a '
                       f'max_num_args that is still zero (zend_API.c:486)')
        if _scan(b"s|") != (1, 1):
            bad.append(f'_scan(b"s|") == {_scan(b"s|")}, want (1, 1) -- the '
                       f'control: with the `|` LAST there is no defect, and a '
                       f'scanner that ignored order would give (0, 1) here too')
        if _scan(b"s") != (1, 1) or _scan(b"") != (0, 0) or _scan(b"|") != (0, 0):
            bad.append("_scan disagrees with zend_API.c:507 on a spec with no "
                       "`|`, an empty spec, or a spec that is only `|`")
        if _scan(b"x") is not None:
            bad.append("_scan accepts a bad type specifier; zend_API.c:503 "
                       "returns FAILURE")

        # 4. arm coverage over the calls the DRIVER MAKES, which is sharper
        #    than inputs/gen.py's per-file assertion (A2a rule 1)
        bad += self._visited_arms()

        # 5. the null VALUE and the absent ARGUMENT are different states, which
        #    is the row's claim at run time. Measured on the 5.0.0 CLI in
        #    ../NOTES.md §1; asserted here so a model that conflated them fails.
        absent = self._rec(0, IS_STRING, b"all")
        nullv = self._rec(1, IS_NULL, b"")
        if self._s_wrote(absent) or not self._s_wrote(nullv):
            bad.append("the model conflates `mb_get_info()` with "
                       "`mb_get_info(null)`; only the first leaves typ unwritten")
        if self._s_frame(nullv) != _pad(b""):
            bad.append("IS_NULL does not become the EMPTY STRING; the `!` "
                       "modifier is absent from \"|s\", so zend_API.c:302-308 "
                       "falls through to convert_to_string_ex")
        return bad

    def _visited_arms(self):
        """Every arm the VISITED calls reach -- the sharper half of A2a rule 1."""
        if not self.entered:
            return []
        seen = set()
        counts, types, lens, bools = set(), set(), set(), set()
        upper = False
        for c in self.sample_calls(4096):
            win = self.buf[c["off"]:c["off"] + c["len"]]
            for r in range(c["len"] // REC):
                b = win[r * REC:(r + 1) * REC]
                na, ty, ln, lv, pay = decode(b)
                counts.add(na)
                types.add(ty)
                lens.add(ln)
                if ty == IS_BOOL:
                    bools.add(lv % 2)
                if ty == IS_STRING and pay[:ln] != pay[:ln].lower():
                    upper = True
                if na > 1 or (na == 1 and ty == IS_ARRAY):
                    seen.add("RETURN_FALSE-guard")
                    continue
                if na == 0:
                    seen.add("NULL-DEREF")
                    continue
                key = _body(ty, lv, ln, pay).split(b"\0", 1)[0].lower()
                seen.add(key.decode("latin-1")
                         if key in [s.lower() for s in SELS] else "else")
        bad = []
        want = {s.decode() for s in SELS} | {"else", "RETURN_FALSE-guard"}
        # ⚠ MEASURED CORPUS ONLY. The adversarial files have exactly ONE
        # window each by construction (`inputs/gen.py`), so they cannot span the
        # arm table and must not be asked to: a one-window probe is not a
        # corpus. `nwin >= 2` is the test, not the stride -- `small.bin` and
        # `adversarial-absent.bin` share a stride and differ in windows.
        if self.nwin >= 2:
            if not want <= seen:
                bad.append(f"the VISITED calls miss arms {sorted(want - seen)}")
            if counts != {1, 2}:
                bad.append(f"the VISITED calls reach num_args {sorted(counts)}, "
                           f"want exactly {{1, 2}} -- 0 is ADVERSARIAL")
            if types != {0, 1, 2, 3}:
                bad.append(f"the VISITED calls reach Z_TYPE {sorted(types)}, "
                           f"want all four")
            if 0 not in lens or STRMAX not in lens:
                bad.append("the VISITED calls do not reach both ends of the "
                           "Z_STRLEN domain")
            if bools != {0, 1}:
                bad.append("the VISITED calls reach only one IS_BOOL value")
            if not upper:
                bad.append("no VISITED call spells a selector in another case, "
                           "so a rung using `strcmp` would agree")
        return bad


def build(path):
    return Model(path)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        m = build(p)
        print(f"{os.path.basename(p):30s} {m.describe()}  "
              f"exit={m.expected_exit} selfcheck={m.selfcheck()}")
