#!/usr/bin/env python3
"""p35 -- the independent reference implementation.

`harness/check.py` drives this: the checksum every cell must print, the
`requires`/`ensures` re-derivation, the work-per-call denominator, the
sanitizer expectation and the conforming exit code all come from here and from
the input file alone. It never reads a rung's source and never runs a binary.

TWO IMPLEMENTATIONS, DELIBERATELY DIFFERENT IN SHAPE
====================================================
`TASK_136`'s model was a line-by-line transliteration of its own kernel, which
is how its bug went undetected, and `.memory/03-measurement.md` entry 19 adds
the second failure mode: a derived check that is a TAUTOLOGY of the model's own
representation. Both are addressed here on purpose.

  1. `_sim_window` -- **objects with identity.** A cell is a `TaggedCell`: a
     mutable object with a `tag`, a payload, and -- the whole point -- an
     explicit record of WHICH TYPE THE PAYLOAD ACTUALLY IS. A read at a type the
     payload is not raises `TypeConfusion` at the read site. This is what
     produces `checksum` / `expected_stdout` and the per-call `result`.

  2. `_run_spec` -- **the flat machine that mirrors `../verus.rs`'s `run`**: two
     parallel sequences (`tags`, `pays`) stepped by a pure function, with no
     objects, no identity and no confusion detection at all. This is what
     `cell_fold` -- the `ensures` -- is evaluated against.

`selfcheck()` runs the two against each other on sampled calls, so a bug that is
not in BOTH shapes is caught by the gate on every run.

⚠⚠ WHAT THIS MODEL CANNOT REPRESENT, DECIDED BEFORE ANY CELL WAS BUILT
======================================================================
**A Python model has no unions.** A `(tag, payload)` pair cannot reinterpret one
object's storage at a second type, because the payload object carries its own
type with it. So p35's HARM -- the bytes of a `uint64_t` read back as a `double`
or as a `uint8_t *` -- is **unrepresentable here by construction**, and this file
does not pretend otherwise: `_sim_window` under the buggy semantics returns
`acc = None` from the confusion onward, because it does not know and cannot know
what the C program folded.

**What IS representable, and is a measurement rather than a restatement, is the
TRIGGER.** `TaggedCell` keeps `tag` and `kind` as two separate facts, so
`tag != kind` is a state this file can reach -- and it reaches it exactly when
the safety line is absent and the budget is exhausted. Under the hardened
semantics it is unreachable, and `detector_selftest()` demonstrates BOTH
directions on the same probe blob rather than asserting either.

So `sanitizer_expect` below is split, and the split is stated in its docstring:

    DERIVED   does a type-confused read happen at all, and at which TYPE
    DECLARED  what each detector does when one does

The declared half is licensed by `../controls/detectors.py`, which ships a
POSITIVE CONTROL PER DETECTOR -- one that fires in ASan and a different one that
fires in UBSan -- because a control that fires only in ASan says nothing about a
UBSan column (`.memory/03-measurement.md` entry 14 one level down;
`.temp/mgr147/NOTES.md`, which is where that gap was found and closed).
"""

import itertools
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "common"))
import slb  # noqa: E402

MASK = (1 << 64) - 1

HDR = 4                   # nops:u32
OPSZ = 2                  # opcode byte + operand byte
CELLS = 8                 # must equal every rung's CELLS
BUDGET = 4                # must equal every rung's BUDGET
SENT = 251                # must equal every rung's SENT

T_UNSET = 0
T_INT = 1
T_PTR = 2
T_DBL = 3

#: The arena, byte for byte, as every rung initialises it: `(j * 11 + 5) & 255`.
#: The C rungs hold a POINTER into it and the four Rust rungs hold the OFFSET;
#: both name the same byte, which is why every checksum agrees. ../NOTES.md 5.
ARENA = [(j * 11 + 5) & 0xFF for j in range(BUDGET)]


def int_payload(a):
    """What SET_INT stores, in every rung: `a * 2654435761` as a u64."""
    return (a * 2654435761) & MASK


def dbl_payload(a):
    """What SET_DBL stores, in every rung.

    ⚠ **Two LITERALS, not `(double)a + 0.5`, and the reason is a measurement.**
    At the pinned Verus/vstd, `f64` arithmetic carries an `add_req` precondition
    nothing discharges (`vstd/std_specs/ops.rs`) and `u8 as f64` is specified as
    a *"(possibly) non-deterministic Rust cast"* (`vstd/float.rs`), while an
    `f64` LITERAL verifies. ../NOTES.md 6c has the four probes. The C rungs
    spell the same conditional, so no rung is disadvantaged."""
    return 0.25 if a % 2 == 0 else 2.5


class TypeConfusion(Exception):
    """A `GET` read a cell at the type its TAG claims, and the payload is a
    different type. Raised at the read site by implementation 1.

    `claimed` is the tag; `actual` is what the payload really is. p35's two harm
    classes are exactly the two values `claimed` can take here."""

    def __init__(self, claimed, actual):
        super().__init__(f"tag says {claimed}, payload is {actual}")
        self.claimed = claimed
        self.actual = actual


class TaggedCell:
    """IMPLEMENTATION 1's cell: a tag, a payload, and the payload's OWN TYPE.

    ⚠⚠ **The third field is what a C union does not have, and it is the whole
    reason this model can see anything at all.** In C, `cells[k].u` is eight
    bytes with no record of which member was last stored; the tag is the only
    claim about it, and when the tag is wrong there is nothing to compare it
    against. Here `kind` is that record, kept beside the payload and never read
    by the fold -- only by the check."""

    __slots__ = ("tag", "kind", "payload")

    def __init__(self):
        self.tag = T_UNSET
        self.kind = T_UNSET
        self.payload = None

    def store(self, kind, payload):
        """Write the payload. Does NOT publish the tag -- that is the other
        half, and keeping them apart is what makes the ordering visible."""
        self.kind = kind
        self.payload = payload

    def publish(self, tag):
        """Publish the tag. The buggy rung does this BEFORE `store`, on a path
        where `store` may not happen."""
        self.tag = tag

    def read(self):
        """Dispatch on the tag, the way `GET` does."""
        if self.tag == T_UNSET:
            return SENT
        if self.tag != self.kind:
            raise TypeConfusion(self.tag, self.kind)
        if self.tag == T_INT:
            return self.payload & 0xFF
        if self.tag == T_PTR:
            return ARENA[self.payload]
        return 1 if self.payload > 1.0 else 0


def _sim_window(buf, off, ln, harden):
    """IMPLEMENTATION 1. One window, simulated with objects that have identity.

    Returns `(acc, confusion)`:

      acc         the checksum, or **None** if a type-confused read happened --
                  see the module docstring: this model cannot know what the C
                  program folded from reinterpreted bytes, and says so rather
                  than guessing.
      confusion   None, `T_PTR` or `T_DBL` -- the TAG the confused read used.

    `harden` selects the SAFETY LINE. With it, the tag is published only after
    the payload lands; without it, the tag is published before the `navail`
    test, which is `c/kernel.c`."""
    if ln < HDR:
        return 0, None
    nops = (buf[off] + 256 * buf[off + 1] + 65536 * buf[off + 2]
            + 16777216 * buf[off + 3])
    if nops == 0:
        return 0, None

    cells = [TaggedCell() for _ in range(CELLS)]
    navail = BUDGET
    acc = 0
    p = HDR
    for _ in range(nops):
        if ln - p < OPSZ:
            break
        c = buf[off + p]
        a = buf[off + p + 1]
        p += OPSZ
        idx = a % CELLS
        m = c % 4
        if m == 0:
            cells[idx].publish(T_INT)
            cells[idx].store(T_INT, int_payload(a))
            acc = (acc * 31 + a) & MASK
        elif m == 1:
            if not harden:
                cells[idx].publish(T_PTR)
            if navail > 0:
                cells[idx].store(T_PTR, BUDGET - navail)
                if harden:
                    cells[idx].publish(T_PTR)
                navail -= 1
                acc = (acc * 31 + 1) & MASK
            else:
                acc = (acc * 31 + SENT) & MASK
        elif m == 2:
            if not harden:
                cells[idx].publish(T_DBL)
            if navail > 0:
                cells[idx].store(T_DBL, dbl_payload(a))
                if harden:
                    cells[idx].publish(T_DBL)
                navail -= 1
                acc = (acc * 31 + 2) & MASK
            else:
                acc = (acc * 31 + SENT) & MASK
        else:
            try:
                v = cells[idx].read()
            except TypeConfusion as e:
                return None, e.claimed
            acc = (acc * 31 + v) & MASK
    return (acc * 31 + navail) & MASK, None


#: The must-fire probe. SET_INT into cell 0; four stores that succeed and
#: exhaust the budget; a fifth store into cell 0 that FAILS; then GET cell 0.
#: Operand bytes are chosen so that `a % CELLS` picks the intended cell.
def _probe(final_op):
    ops = [(0, 0)]                       # SET_INT  cell 0
    ops += [(1, 1), (1, 2), (1, 3), (1, 4)]  # four SET_PTRs -> budget exhausted
    ops += [(final_op, 8)]               # the failing store, back into cell 0
    ops += [(3, 0)]                      # GET cell 0
    body = bytes([len(ops), 0, 0, 0])
    for c, a in ops:
        body += bytes([c, a])
    return body


_PROBE_PTR = _probe(1)     # the failing store claims PTR
_PROBE_DBL = _probe(2)     # the failing store claims DBL


def detector_selftest():
    """Show that the type-confusion detector CAN FIRE, and that the SAFETY LINE
    is the only thing that stops it. Four cells, two per probe.

    ⚠ `.memory/03-measurement.md` entry 19, found on `p32` at `TASK_145`: a
    derived `sanitizer_expect` whose derivation cannot fire is a declaration
    wearing a derivation's clothes. This is the arm that stops that being true
    here, and it is run by `selfcheck()` on every input on every gate run.

    ⚠⚠ **A cell that RAISES is reported as a failed cell with its exception
    text, never allowed to crash** -- `p32`'s `detector_selftest` failed by
    crashing and the diagnostic was lost (`TASK_151_REPORT` §5). Fixing it there
    costs a re-measure; here it was free, so it is done."""
    problems = []
    arms = ((_PROBE_PTR, T_PTR, "SET_PTR"), (_PROBE_DBL, T_DBL, "SET_DBL"))
    for blob, want, label in arms:
        try:
            acc_h, conf_h = _sim_window(blob, 0, len(blob), True)
        except Exception as e:                      # noqa: BLE001
            problems.append(f"{label}: the HARDENED arm of the probe RAISED "
                            f"{type(e).__name__}: {e} -- the probe or "
                            f"`TaggedCell` is wrong, and this cell tested "
                            f"nothing")
            acc_h, conf_h = None, None
        else:
            if conf_h is not None or acc_h is None:
                problems.append(
                    f"{label}: the type-confusion detector FIRED on the probe "
                    f"WITH the safety line present (confusion={conf_h}), which "
                    f"no shipped rung can do -- the probe or `TaggedCell` is "
                    f"wrong")
        try:
            acc_b, conf_b = _sim_window(blob, 0, len(blob), False)
        except Exception as e:                      # noqa: BLE001
            problems.append(f"{label}: the BUGGY arm of the probe RAISED "
                            f"{type(e).__name__}: {e} -- this cell tested "
                            f"nothing")
            continue
        if conf_b != want:
            problems.append(
                f"MUST-FIRE ARM DEAD: {label}: deleting the safety line from "
                f"the simulated rung did NOT produce a tag-{want} confused read "
                f"(got confusion={conf_b}, acc={acc_b}). `sanitizer_expect` is "
                f"then a declaration wearing a derivation's clothes -- do not "
                f"quote this pattern's expectation as DERIVED until it fires "
                f"again")
    return problems


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
        self.confusions = set()
        self._work = 0
        self._win = []
        if not self.truncated:
            self._run()

    # -- the window table (computed once) ----------------------------------
    def _window(self, off):
        """(result, confusion-under-the-BUGGY-semantics) for the window at
        `off`.

        Implementation 1 of 2 -- objects with identity; see the module
        docstring. The second element is computed under the BUGGY semantics,
        because the question it answers is what the rung with no safety line
        would do."""
        r_ok, conf_ok = _sim_window(self.buf, off, self.stride, True)
        _, conf_bug = _sim_window(self.buf, off, self.stride, False)
        assert conf_ok is None, "the hardened semantics cannot confuse a type"
        return r_ok, conf_bug

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
                r, conf = self._win[k]
                if conf is not None:
                    self.confusions.add(conf)
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
            if self._win[k] is None:
                self._win[k] = self._window(k * self.stride)
            r, _conf = self._win[k]
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
    # (../verus.rs `run`) and keeps the cells in TWO PARALLEL SEQUENCES -- a tag
    # sequence and a payload sequence whose elements are `(field, value)` pairs
    # standing for a `Pay` union value -- which is the RUNGS' representation and
    # not the simulation's. It has no confusion detection and needs none: it
    # models the CORRECT semantics only.
    def _u32_at(self, buf, p):
        """`u32_at` in ../verus.rs, written out with `+` and `*` exactly as the
        rungs write it -- not `int.from_bytes`, which is the simulation's."""
        return (buf[p] + 256 * buf[p + 1] + 65536 * buf[p + 2]
                + 16777216 * buf[p + 3])

    def _run_spec(self, buf, off, ln):
        """`run` in ../verus.rs. Iterative rather than recursive."""
        nops = self._u32_at(buf, off)
        if nops == 0:
            return 0
        tags = [T_UNSET] * CELLS
        pays = [("i", 0)] * CELLS
        navail = BUDGET
        acc, p, o = 0, HDR, 0
        while o < nops:
            if ln - p < OPSZ:
                break
            c = buf[off + p]
            a = buf[off + p + 1]
            p += OPSZ
            o += 1
            k = a % CELLS
            m = c % 4
            if m == 0:
                pays[k] = ("i", int_payload(a))
                tags[k] = T_INT
                acc = (acc * 31 + a) & MASK
            elif m == 1:
                if navail > 0:
                    pays[k] = ("o", BUDGET - navail)
                    tags[k] = T_PTR
                    navail -= 1
                    acc = (acc * 31 + 1) & MASK
                else:
                    acc = (acc * 31 + SENT) & MASK
            elif m == 2:
                if navail > 0:
                    pays[k] = ("d", dbl_payload(a))
                    tags[k] = T_DBL
                    navail -= 1
                    acc = (acc * 31 + 2) & MASK
                else:
                    acc = (acc * 31 + SENT) & MASK
            else:
                t = tags[k]
                if t == T_INT:
                    acc = (acc * 31 + (pays[k][1] & 0xFF)) & MASK
                elif t == T_PTR:
                    acc = (acc * 31 + ARENA[pays[k][1]]) & MASK
                elif t == T_DBL:
                    acc = (acc * 31 + (1 if pays[k][1] > 1.0 else 0)) & MASK
                else:
                    acc = (acc * 31 + SENT) & MASK
        return (acc * 31 + navail) & MASK

    def cell_fold(self, buf, off, ln):
        """`cell_fold` in ../verus.rs: what the kernel must return."""
        if ln < HDR:
            return 0
        return self._run_spec(buf, off, ln)

    @property
    def helpers(self):
        return {"cell_fold": self.cell_fold}

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
        """`stride` -- the bytes of the window, from the file alone, which is
        p27's, p29's, p32's, p38's, p16's, p05's, p11's, p12's, p06's and p14's
        denomination.

        **Which way this estimate errs: STRICT** (`.memory/02-bench-rules.md`
        asks, so: say it). Two corrections, and the net is strict on every
        matrix input this pattern ships:

          * *over*-count: the 4 window-header bytes are decoded as a `u32` and
            are not operations;
          * *under*-count: **each 2 window bytes is one OPERATION**, and every
            operation does at least a modulo, a tag load, a compare chain and a
            multiply-add on the accumulator, while every SET also stores a
            payload and a tag.

        p35's under-count is small: an operation here is O(1) with no loop and
        no call inside it, exactly as in p32. It is still an under-count on
        every shipped input.

        No `min_ir_per_work` is declared, so the harness default of 0.25 Ir per
        byte applies unchanged. What it catches is the failure it exists to
        catch -- a kernel the optimiser collapsed to nothing."""
        return self._work if self.entered else 0

    # -- sanitizer expectation ---------------------------------------------
    @property
    def sanitizer_expect(self):
        """**DERIVED down to the TRIGGER; DECLARED for the one step from the
        trigger to the detector's verdict.** The split is deliberate, it is
        stated here so nobody reads the value as more than it is, and it is the
        answer to the question the build task asked to be decided FIRST.

        DERIVED, by `_sim_window` under the BUGGY semantics, on every window the
        driver actually visits: does a `GET` ever dispatch on a tag that names a
        different type from the one the payload was last written at, and which
        tag was it? `TaggedCell` keeps `tag` and `kind` as two separate facts,
        so this is a state the model can reach -- and `detector_selftest()`
        shows it reaching it, and shows the safety line being the only thing
        that stops it.

        DECLARED, because **a Python model has no unions** and therefore cannot
        evaluate what the C program does with reinterpreted bytes:

          tag PTR over an int payload   the dereference of an attacker-derived
                                        integer. **ASan reports it**; UBSan has
                                        no wild-pointer check and reports
                                        nothing, which is why this pattern owes
                                        -- and ships -- a UBSan-SPECIFIC
                                        positive control as well as an ASan one
                                        (`../controls/detectors.py`).
          tag DBL over an int payload   a garbage `double` compared against
                                        1.0. **SILENT in every detector this
                                        project has**: ASan, UBSan, both
                                        compilers at `-Wall -Wextra`, and Miri
                                        on the Rust reproduction. Reading a
                                        union member other than the one last
                                        stored is DEFINED in C99 (6.2.6.1p7),
                                        so there is nothing for a sanitizer to
                                        report; the value is simply wrong.

        ⚠⚠ **THE ROW ABOVE IS SCOPED TO `over an int payload` AND THAT SCOPE IS
        LOAD-BEARING (measured at TASK_153).** The same ordering also reaches
        `tag DBL over a PTR payload` (`adversarial-exhaust.bin`), and in C that
        is another 8-byte-over-8-byte reinterpretation and equally silent --
        `uint8_t *` is 8 bytes here, so C's union has no narrow member at all.
        **In the RUST rungs it is not**: they carry `o: u32` instead of a
        pointer, so the same confusion reads 8 bytes where 4 were written and
        **Miri REPORTS it** as uninitialised memory. That is a consequence of
        the disclosed offset-for-pointer substitution, not of the C program,
        and `../NOTES.md` 5 and 7 measure it.

        ⚠ **That asymmetry is the row's result, not a gap in the run.** One
        statement ordering, two harms, and the detector coverage differs by the
        TYPE the tag happens to name."""
        return "fires" if T_PTR in self.confusions else "clean"

    # -- what a conforming driver does -------------------------------------
    @property
    def expected_exit(self):
        # p35's payload allocates nothing from an attacker-controlled size --
        # there is no `cap` word and no `slb_zeroed` -- so p02's exit 7 has no
        # analogue here, exactly as for p27, p29, p32 and p38. `slb_load`
        # rejecting a short file is the only non-zero exit this driver produces.
        #
        # This is the CHECKED rungs' exit. R1's exit on the adversarial rows is
        # RECORDED in the adversarial table rather than required, and on
        # `adversarial-ptr-confusion` it is a SIGSEGV.
        return 5 if self.truncated else 0

    @property
    def expected_stdout(self):
        return "" if self.checksum is None else f"{self.checksum}\n"

    def describe(self):
        return (f"n_iters={self.n_iters} stride={self.stride} "
                f"n_blob={self.n_blob} nwin={self.nwin} calls={self.n_calls} "
                f"work/call={self.work_per_call}B "
                f"san={self.sanitizer_expect} "
                f"confusions={sorted(self.confusions)} "
                f"truncated={self.truncated} expected={self.checksum}")

    def selfcheck(self):
        """The object-identity simulation against the two parallel sequences
        that mirror Verus, plus the type-confusion detector's own must-fire
        arm."""
        problems = list(detector_selftest())
        for c in self.sample_calls(8):
            want = self.cell_fold(c["buf"], c["off"], c["len"])
            if want != c["result"]:
                problems.append(
                    f"simulated result {c['result']} != cell_fold() {want} "
                    f"at off={c['off']}")
                break
        return problems


def build(path):
    return Model(path)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        m = build(p)
        print(f"{os.path.basename(p):32s} {m.describe()}  "
              f"exit={m.expected_exit} selfcheck={m.selfcheck()}")
