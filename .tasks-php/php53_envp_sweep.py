#!/usr/bin/env python3
"""TASK_PHP_053 §1 -- ⛔⛔⛔ **CLOSE THE ONE UNPROVEN LINK UNDER `PROTOCOL_PHP.md`
§B5 AND `.memory-php/03-numbers.md`: THE SWEEP THAT LANDED THE RULE PERTURBS
`argv`, WHILE THE BIMODALITY THE GATE OBSERVES IS ACROSS `envp`.**

    python3 .tasks-php/php53_envp_sweep.py --selftest
    python3 .tasks-php/php53_envp_sweep.py --row ph64-callback-frees-cursor \
            --inputs small.bin --pads 32
    python3 .tasks-php/php53_envp_sweep.py --row ph55-opdata-stride \
            --inputs small.bin --cells c-clang,c-clang-h --pads 32

--------------------------------------------------------------------------------
WHAT THIS IS, AND WHY IT IS NOT A NEW SWEEP
--------------------------------------------------------------------------------

⭐⭐ **IT IS `.tasks-php/php50_align_sweep.py`, IMPORTED AND UNMODIFIED, DRIVEN
ON THE OTHER KNOB.** `_050`'s file is the instrument the rule was landed with; a
second implementation of the same measurement would make a disagreement
uninterpretable (is it the knob, or is it the code?). So this file imports it and
reuses **`_probe`, `_total`, `dcalls_of`, `build_dir`, `sweep_row`, `step_of`,
`sweep_completeness`, `verdicts` and `problems_of` verbatim**, and changes
exactly one thing:

    `php50_align_sweep.py`   pad  -> `argv[1]`   (the probe FILENAME grows)
    `php53_envp_sweep.py`    pad  -> `envp`      (one filler VARIABLE grows)

⭐ **THE argv STRING IS HELD AT THE GATE'S OWN LENGTH AT EVERY POINT.** This file
calls `sweep_row(..., pads=[0])` once per envp pad, so the probe file is always
named `probe.<inp>.<n>.bin` -- byte-for-byte the name `harness/check.py` uses.
**Exactly one knob moves.** (§H arm `N5` refuses a run in which it does not.)

**HOW THE envp PAD IS APPLIED.** One variable, `PH53PAD`, always present, value
`"x" * pad`. `nvars` is therefore CONSTANT and the block length moves by exactly
one byte per step, so pads `0..31` cover 32 consecutive values of
`envp_stack_bytes` -- a full period of the 32-byte lever. ⚠ **`nvars` is held
constant on purpose**: `harness/check.py::_env_block` records that a sweep in the
*variable count* has period **4**, because one variable costs an envp POINTER
SLOT of 8 bytes as well as its text, and mixing the two axes would alias a
32-byte period against an 8-byte one.

⚠⚠ **THE BLOCK LENGTH IS READ FROM A REAL CHILD, NEVER COMPUTED FROM
`os.environ`.** That is `harness/check.py::_env_block` note 1 and control entry 7
of `.memory/03-measurement.md` -- `TASK_099`'s `a3_launcher.py` measured it from
a Python dict and was wrong by the four terms a variable actually costs. §H arm
`N2` is that check, and it fails on a dict-shaped answer.

--------------------------------------------------------------------------------
⛔ WHAT A GREEN RUN HERE DOES AND DOES NOT LICENSE
--------------------------------------------------------------------------------

A row measuring `0.00` under this file is **not** evidence of absence unless the
instrument is shown to be live **in the same session, on the same box, through
the same valgrind**. That is what `knob_verdict` is for: it takes a POSITIVE
CONTROL (a cell with a known non-zero `argv` step -- `ph55`'s clang cells, `7.00`
per `.temp/php50/sw_ph55.json`) beside the SUBJECT (`ph64`, `0.00` on every cell
per `.temp/php50/ph64_full.json`) and **refuses to return a clearance when the
control did not move**. `php50_align_sweep.problems_of` arm 5 is the same idea
inside one row; this is the cross-row form the §1 question needs.

--------------------------------------------------------------------------------
§H -- THE MUST-FIRE NEGATIVES LIVE IN THIS FILE
--------------------------------------------------------------------------------

`PROTOCOL_PHP.md` §H. `--selftest` drives the pure verdict arm over synthetic
inputs. **Six arms must FIRE and four must NOT**, plus the whole of
`php50_align_sweep.selftest()` (10 arms + 9 unit arms), re-run here because this
file's conclusions are computed by that file's code. They run on EVERY
invocation: a broken verdict arm REFUSES to measure rather than measuring anyway.

⚠ **`N1` FIRED AGAINST THE FIRST DRAFT OF THIS FILE.** The first version set the
pad with `subprocess.run(env=...)` on a wrapper that then re-exec'd, and the
variable did not reach the client under valgrind at all -- every cell read
`0.00`, which would have been reported as *"envp is a different knob"*. It is
not: the instrument was disconnected. The arm stayed and the plumbing changed.

⚠ **THIS FILE IS READ-ONLY WITH RESPECT TO THE CORPUS.** It runs already-built
binaries out of `.temp/php-scratch/build/<row>/` and writes only under
`.temp/php53/`. It is not a gate, a measure or a re-gate; nothing under
`patterns-php/`, `results-php/`, `harness/` or `harness-php/` is opened for
writing.
"""

import argparse
import importlib.util
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, ".temp", "php53")

#: the padding variable. Fixed NAME (so `nvars` and the name's own bytes are
#: constant); only the VALUE grows, one byte per pad.
PADVAR = "PH53PAD"


def _load_050():
    """`php50_align_sweep.py`, imported rather than reimplemented."""
    p = os.path.join(HERE, "php50_align_sweep.py")
    spec = importlib.util.spec_from_file_location("php50_align_sweep", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


A = _load_050()


# ---------------------------------------------------------------------------
# the knob
# ---------------------------------------------------------------------------

def child_env_block(pad):
    """`envp_stack_bytes` as a REAL CHILD sees it at this pad -- the same two
    numbers `harness/check.py::_env_block` reads, from the same blob, in the same
    way (`/proc/self/environ` in the child, plus `8 * nvars` for the pointer
    array `bytes` drops).

    ⛔ Not `len(os.environ)` arithmetic: see the module docstring."""
    old = os.environ.get(PADVAR)
    os.environ[PADVAR] = "x" * pad
    try:
        r = subprocess.run(
            [sys.executable, "-c",
             "import sys;b=open('/proc/self/environ','rb').read();"
             "sys.stdout.write('%d %d' % (len(b), b.count(b'\\x00')))"],
            capture_output=True, text=True, timeout=60)
        n, nvars = (int(x) for x in r.stdout.split())
    finally:
        if old is None:
            os.environ.pop(PADVAR, None)
        else:
            os.environ[PADVAR] = old
    return {"bytes": n, "nvars": nvars, "envp_stack_bytes": n + 8 * nvars}


def reaches_client_under_valgrind(pad=17):
    """⭐ **DOES THE PAD REACH THE PROGRAM CALLGRIND IS MEASURING?**

    `valgrind` synthesises the client's initial stack itself
    (`harness/check.py::_env_block`, *"WHAT THE INTEGER IS NOT"*), so *"I set an
    environment variable"* is not the same statement as *"the measured child's
    stack moved"*. This runs `printenv` **under the same callgrind invocation
    shape `php50_align_sweep._total` uses** and requires the exact value back.

    Returns `(ok, detail)`. ⛔ A `False` here invalidates every `0.00` this file
    would otherwise report -- it means the instrument is disconnected, not that
    the row is clean."""
    exe = None
    for c in ("/usr/bin/printenv", "/bin/printenv"):
        if os.path.exists(c):
            exe = c
    if exe is None:
        return False, "no printenv on this box, so the plumbing is untestable"
    old = os.environ.get(PADVAR)
    os.environ[PADVAR] = "x" * pad
    try:
        r = subprocess.run(
            [A.VALGRIND, "--tool=callgrind",
             f"--callgrind-out-file={os.path.join(OUT, 'cg.plumbing.out')}",
             exe, PADVAR],
            capture_output=True, text=True, timeout=300)
    finally:
        if old is None:
            os.environ.pop(PADVAR, None)
        else:
            os.environ[PADVAR] = old
    got = (r.stdout or "").strip()
    if got != "x" * pad:
        return False, (f"{PADVAR} did not reach the client under callgrind: "
                       f"printenv returned {got!r} (rc {r.returncode})")
    return True, f"{PADVAR} reached the client under callgrind at pad {pad}"


def sweep_row_argv0(row, inp, pads, cells, verbose=True):
    """`{cell: [slope at argv[0] pad 0, ...]}`, with `argv[1]` and the whole
    environment held FIXED.

    ⭐⭐ **THE THIRD AXIS, AND IT EXISTS BECAUSE THE FIRST TWO DISAGREED.**
    `_050`'s sweep grows `argv[1]` -- the probe path the driver opens and the
    only argument it reads -- so it moves the initial stack offset AND the
    length of a string the program itself handles. `php53_envp_sweep`'s `envp`
    axis moves only the stack offset. On `ph07`'s `verus` cell those two
    disagree completely (34.49 against 0.00), so a third axis is needed that
    moves the stack offset WITHOUT touching `argv[1]`.

    **The knob: invoke the binary through a symlink whose NAME grows.**
    `argv[0]` and `AT_EXECFN` grow by one byte per pad; `argv[1]` is
    byte-identical at every point; the environment is untouched.

    ⚠ An earlier attempt padded `argv[2]` instead. **The driver refuses a second
    argument** (`exited 2`, usage line), so that probe measured nothing and said
    so rather than printing a flat line. A symlink is a knob the driver cannot
    refuse because it never sees it."""
    src = os.path.join(ROOT, "patterns-php", row, "inputs", inp)
    if not os.path.exists(src):
        return {}, [f"{row}: no input {inp}"], None
    dc = A.dcalls_of(row, inp)
    d = os.path.join(A.SCRATCH, row)
    paths = {n: A._probe(src, n, os.path.join(d, f"probe.{inp}.{n}.bin"))
             for n in (100, 200)}
    out, problems, argv1_lens = {c: [] for c in cells}, [], set()
    linkdir = os.path.join(OUT, "argv0", row)
    os.makedirs(linkdir, exist_ok=True)
    for pad in pads:
        for c in cells:
            exe = os.path.join(A.build_dir(row), f"{c}-{A.OPT}-{A.MODE}")
            if not os.path.exists(exe):
                problems.append(f"{row}/{c}: no binary at {exe}")
                continue
            link = os.path.join(linkdir, "L" * pad + "run")
            if os.path.islink(link):
                os.unlink(link)
            os.symlink(exe, link)
            # §H's live form: the link must resolve to the cell we mean.
            if os.path.realpath(link) != os.path.realpath(exe):
                problems.append(f"6. symlink {link} does not resolve to {exe}")
            vals = {}
            for n in (100, 200):
                v, e = A._total(link, paths[n], os.path.join(
                    A.SCRATCH, f"cg.{row}.{c}.{n}.out"))
                if e:
                    problems.append(e)
                vals[n] = v
                argv1_lens.add(len(paths[n]))
            os.unlink(link)
            if vals[100] is None or vals[200] is None:
                continue
            out[c].append(round((vals[200] - vals[100]) / dc, 2))
        if verbose:
            print(f"   argv0 pad {pad:>3d}  " + "".join(
                f"{(out[c][-1] if out[c] else 0):>13.2f}" for c in cells),
                flush=True)
    for p in paths.values():
        os.unlink(p)
    # `argv[1]` takes two values here (the 100 and 200 probe names) and they are
    # the SAME two at every pad, which is what must be constant.
    if len(argv1_lens) != 2:
        problems.append(f"5. argv[1] lengths were {sorted(argv1_lens)}, want "
                        f"exactly the two probe names -- two knobs moved at once")
    return {k: v for k, v in out.items() if v}, problems, dc


def sweep_row_envp(row, inp, pads, cells, verbose=True):
    """`{cell: [slope at envp pad 0, ...]}` in Ir/call, `argv` held FIXED.

    ⭐ Every point is `php50_align_sweep.sweep_row(..., pads=[0])`, i.e. the
    other file's measurement, unmodified, at its own zero-pad point. The only
    thing this function does is set `PH53PAD` around each call."""
    out = {c: [] for c in cells}
    problems, dc, argv_lens = [], None, set()
    old = os.environ.get(PADVAR)
    try:
        for pad in pads:
            os.environ[PADVAR] = "x" * pad
            sw, probs, d = A.sweep_row(row, inp, [0], cells=cells, verbose=False)
            dc = d if dc is None else dc
            if d != dc:
                problems.append(f"dcalls moved between pads ({dc} -> {d})")
            problems += probs
            # N5's live form: argv must be identical at every point.
            argv_lens.add(len(os.path.join(
                A.SCRATCH, row, f"probe.{inp}.100.bin")))
            for c in cells:
                if sw.get(c):
                    out[c].append(sw[c][0])
            if verbose:
                eb = child_env_block(pad)["envp_stack_bytes"]
                print(f"   envp pad {pad:>3d}  block {eb:>6d}  " + "".join(
                    f"{(out[c][-1] if out[c] else 0):>13.2f}" for c in cells),
                    flush=True)
    finally:
        if old is None:
            os.environ.pop(PADVAR, None)
        else:
            os.environ[PADVAR] = old
    if len(argv_lens) != 1:
        problems.append(f"5. argv length was NOT constant across the envp "
                        f"sweep ({sorted(argv_lens)}) -- two knobs moved at "
                        f"once and no step can be attributed to either")
    return {k: v for k, v in out.items() if v}, problems, dc


#: ⭐ THE THREE AXES, AND THE POINT OF THIS FILE IS THAT THEY DISAGREE.
#: `argv1` is `_050`'s own sweep, reached through the IMPORTED module, so all
#: three verdicts are produced by one code path and a disagreement between axes
#: cannot be an artefact of two implementations of the same measurement.
AXES = {"envp": sweep_row_envp, "argv0": sweep_row_argv0,
        "argv1": (lambda r, i, p, c, verbose=True:
                  A.sweep_row(r, i, p, cells=c, verbose=verbose))}


# ---------------------------------------------------------------------------
# the verdict arm -- a pure function, so it can be attacked
# ---------------------------------------------------------------------------

def axis_report(steps):
    """⛔⛔ **IS THE ALIGNMENT STEP A PROPERTY OF THE CELL, OR OF THE
    (CELL, AXIS) PAIR?** `steps` is `{axis: step}` for ONE cell.

    `PROTOCOL_PHP.md` §B5 and `.memory-php/03-numbers.md` speak of *"the measured
    step"* of a cell as though a cell has one. This function is the place that
    claim is decided, and it returns exactly one of:

      `ONE-KNOB`            every axis measured the same step (within
                            `SAME_TOL`). §B5's phrase is well formed.
      `AXIS-MAGNITUDE`      every axis moves the cell, by MATERIALLY DIFFERENT
                            amounts. *"The step"* is under-specified: it names a
                            quantity that depends on which axis you picked.
      `AXIS-PRESENCE`       ⛔⛔ at least one axis moves the cell and at least
                            one does not. **An `argv` sweep reading `0.00` is
                            then not evidence that the cell is insensitive.**
      `NO-MOTION`           no axis moved it. Clean on everything measured.
      `UNMEASURED`          fewer than two axes were measured, so there is no
                            comparison to make.
    """
    have = {k: v for k, v in (steps or {}).items() if v is not None}
    if len(have) < 2:
        return "UNMEASURED", f"only {sorted(have)} measured"
    nz = {k: v for k, v in have.items() if v != 0}
    if not nz:
        return "NO-MOTION", f"all of {sorted(have)} measured 0.00"
    if len(nz) != len(have):
        zero = sorted(k for k in have if have[k] == 0)
        return ("AXIS-PRESENCE",
                f"{sorted(nz)} move the cell ({nz}) and {zero} do not")
    lo, hi = min(nz.values()), max(nz.values())
    if (hi - lo) / max(abs(hi), 1e-9) > SAME_TOL:
        return ("AXIS-MAGNITUDE",
                f"every axis moves the cell but by different amounts ({nz})")
    return "ONE-KNOB", f"every axis measured the same step ({nz})"

#: two steps count as "the same size" within this relative tolerance. Chosen so
#: the corpus's four measured argv steps (0.00, 0.02, 7.00, 34.49) are four
#: distinct classes and nothing else is.
SAME_TOL = 0.25


def knob_verdict(ctrl_argv, ctrl_envp, subj_argv, subj_envp):
    """⛔⛔⛔ **THE §B5 RULING, AS A FUNCTION OF FOUR MEASURED STEPS.**

    `ctrl_*` is a POSITIVE CONTROL: a cell whose `argv` step `_050` measured
    NON-ZERO. `subj_*` is the SUBJECT: a cell whose `argv` step `_050` measured
    `0.00`, which is exactly what §B5 accepts as a licence to publish.

    Returns `(verdict, why)`; verdicts are exactly:

      `CONTROL-NOT-A-CONTROL`   the caller handed a control with a zero `argv`
                                step. Refused: there is nothing to calibrate.
      `INSTRUMENT-DEAD`         the control moves under `argv` and NOT under
                                `envp`. ⛔ **No clearance can be read off this
                                run**, because a subject reading `0.00` is
                                indistinguishable from a disconnected knob.
      `B5-UNSOUND`              ⛔⛔ the subject's `argv` step is `0.00` and its
                                `envp` step is NOT. **A rule in the
                                authoritative layer admits a pair that moves.**
      `SAME-KNOB`               control steps the same size on both axes, and
                                the subject is `0.00` on both. §B5 stands and
                                the caveat comes out.
      `SECOND-AXIS-NEEDED`      the control moves on both axes but by
                                MATERIALLY DIFFERENT amounts. §B5 is not wrong,
                                but an `argv`-only sweep does not bound the
                                `envp` axis and the rule needs both.

    ⚠ **`SAME-KNOB` IS THE ONLY VERDICT THAT CLEARS THE SUBJECT, AND IT IS THE
    HARDEST TO EARN ON PURPOSE.** Everything else either refuses or widens the
    rule."""
    if ctrl_argv is None or ctrl_envp is None or subj_argv is None \
            or subj_envp is None:
        return "UNMEASURED", "one of the four steps was not measured"
    if ctrl_argv == 0:
        return ("CONTROL-NOT-A-CONTROL",
                "the control's own argv step is 0.00, so this run calibrates "
                "nothing")
    if subj_argv != 0:
        return ("SUBJECT-NOT-A-SUBJECT",
                f"the subject's argv step is {subj_argv}, not 0.00, so it is "
                f"not a cell §B5 would clear")
    # ⚠⚠ ORDER MATTERS AND THE FIRST DRAFT HAD IT BACKWARDS -- §H arm `N8`
    # fired and the code changed, which is the way round §H requires. A subject
    # that MOVED demonstrates the knob is live all by itself, so `B5-UNSOUND`
    # must outrank `INSTRUMENT-DEAD`; the reverse order would have let a
    # control that happened not to move SUPPRESS a live refutation of the rule.
    if subj_envp != 0:
        return ("B5-UNSOUND",
                f"the subject's argv step is 0.00 -- which §B5 accepts as a "
                f"licence to publish -- and its envp step is {subj_envp}")
    if ctrl_envp == 0:
        return ("INSTRUMENT-DEAD",
                f"the control steps {ctrl_argv} under argv and 0.00 under "
                f"envp, so a 0.00 subject reading is not evidence of absence")
    rel = abs(ctrl_envp - ctrl_argv) / max(abs(ctrl_argv), 1e-9)
    if rel > SAME_TOL:
        return ("SECOND-AXIS-NEEDED",
                f"the control moves on both axes but by different amounts "
                f"(argv {ctrl_argv}, envp {ctrl_envp}, rel {rel:.2f}), so an "
                f"argv sweep does not bound the envp axis")
    return ("SAME-KNOB",
            f"the control steps {ctrl_argv} under argv and {ctrl_envp} under "
            f"envp, and the subject is 0.00 under both")


# ---------------------------------------------------------------------------
# §H
# ---------------------------------------------------------------------------

def selftest(live=False):
    """`live=True` additionally runs the two PLUMBING arms, which cost one
    callgrind run and one python run. They are the arms that cannot be faked
    with synthetic data, and `main()` always runs them."""
    bad = []
    # the imported file's own 19 arms, re-run: this file's numbers are its code.
    for b in A.selftest():
        bad.append(f"php50_align_sweep: {b}")

    # ---- knob_verdict: 6 must-FIRE (non-SAME-KNOB) and 4 must-NOT ----------
    cases = [
        # (label, ctrl_argv, ctrl_envp, subj_argv, subj_envp, want)
        ("P1 the clearance shape", 7.0, 7.0, 0.0, 0.0, "SAME-KNOB"),
        ("P2 a control that steps 34.49 on both", 34.49, 34.49, 0.0, 0.0,
         "SAME-KNOB"),
        # ⭐⭐ N1 IS THE ARM §1 EXISTS TO TEST.
        ("N1 a 0.00-argv subject that steps under envp", 7.0, 7.0, 0.0, 7.0,
         "B5-UNSOUND"),
        ("N2 the same, at a tiny envp step", 7.0, 7.0, 0.0, 0.02,
         "B5-UNSOUND"),
        # ⭐⭐ N3 IS THE ARM THAT STOPS A DISCONNECTED KNOB READING AS A PASS.
        ("N3 control moves on argv only", 7.0, 0.0, 0.0, 0.0,
         "INSTRUMENT-DEAD"),
        ("N4 control moves by a different amount", 7.0, 34.49, 0.0, 0.0,
         "SECOND-AXIS-NEEDED"),
        ("N5 a control that is not one", 0.0, 0.0, 0.0, 0.0,
         "CONTROL-NOT-A-CONTROL"),
        ("N6 a subject that §B5 would not clear anyway", 7.0, 7.0, 7.0, 7.0,
         "SUBJECT-NOT-A-SUBJECT"),
        ("P3 a step that differs inside tolerance still clears",
         7.0, 7.5, 0.0, 0.0, "SAME-KNOB"),
        ("P4 unmeasured stays unmeasured", 7.0, None, 0.0, 0.0, "UNMEASURED"),
    ]
    for label, ca, ce, sa, se, want in cases:
        got = knob_verdict(ca, ce, sa, se)[0]
        if got != want:
            bad.append(f"{label}: got {got}, want {want}")

    # ⭐ N7 the cross-check that INSTRUMENT-DEAD outranks a clean subject: the
    # same subject reading must NOT clear when the control is dead.
    if knob_verdict(7.0, 0.0, 0.0, 0.0)[0] == "SAME-KNOB":
        bad.append("N7: a dead instrument cleared a subject")
    # ⭐ N8 B5-UNSOUND must outrank a dead instrument's ambiguity: if the
    # subject MOVED, the instrument is demonstrably live whatever the control
    # did, and the rule is refuted.
    if knob_verdict(7.0, 0.0, 0.0, 7.0)[0] != "B5-UNSOUND":
        bad.append("N8: a subject that moved under envp did not refute B5 "
                   "merely because the control happened not to move")

    # ---- axis_report: 3 must-FIRE (non-ONE-KNOB) and 2 must-NOT ------------
    axis_cases = [
        ("P5 one knob", {"argv1": 7.0, "argv0": 7.0, "envp": 7.0}, "ONE-KNOB"),
        ("P6 clean on every axis",
         {"argv1": 0.0, "argv0": 0.0, "envp": 0.0}, "NO-MOTION"),
        # ⭐⭐ N13 IS `ph07`'s MEASURED SHAPE, AND IT IS THE §1 HEADLINE.
        ("N13 an axis that does not move a cell the others do",
         {"argv1": 34.49, "argv0": 20.08, "envp": 0.0}, "AXIS-PRESENCE"),
        ("N14 every axis moves it, by different amounts",
         {"argv1": 34.49, "argv0": 20.08, "envp": 18.0}, "AXIS-MAGNITUDE"),
        ("N15 one axis is not a comparison", {"argv1": 7.0}, "UNMEASURED"),
    ]
    for label, st, want in axis_cases:
        got = axis_report(st)[0]
        if got != want:
            bad.append(f"{label}: got {got}, want {want}")
    # ⭐ N16 AXIS-PRESENCE must outrank AXIS-MAGNITUDE: a cell that one axis
    # cannot see at all is a worse defect in the rule than one the axes merely
    # scale differently, and the reverse order would report the milder verdict.
    if axis_report({"argv1": 34.49, "argv0": 0.0, "envp": 7.0})[0] \
            != "AXIS-PRESENCE":
        bad.append("N16: a zero axis beside two non-zero ones must read "
                   "AXIS-PRESENCE, not AXIS-MAGNITUDE")
    # ⭐ N17 the axis table must cover every axis `--axis` offers, or a run
    # could name an axis that silently falls back to another one.
    if set(AXES) != {"envp", "argv0", "argv1"}:
        bad.append(f"N17: AXES covers {sorted(AXES)}, want the three --axis "
                   f"choices")

    # ---- N9/N10: the pad set is the same detector php50 requires -----------
    if not A.sweep_completeness(list(range(32)), "pair")[0]:
        bad.append("N9: 0..31 envp pads must be a complete detector for a PAIR")
    if A.sweep_completeness([0, 16], "pair")[0]:
        bad.append("N10: a two-pad envp screen must NOT be a detector for a "
                   "PAIR (php50_align_sweep's own N7, restated on this axis)")

    if live:
        os.makedirs(OUT, exist_ok=True)
        # ⭐⭐ N11 THE PLUMBING ARM. See `reaches_client_under_valgrind`.
        ok, why = reaches_client_under_valgrind()
        if not ok:
            bad.append(f"N11 plumbing: {why}")
        # ⭐⭐ N12 THE KNOB ARM, measured in a real child, never from a dict:
        # consecutive pads must move `envp_stack_bytes` by exactly 1, and
        # `nvars` must not move at all.
        blocks = [child_env_block(p) for p in (0, 1, 2, 3)]
        deltas = [blocks[i + 1]["envp_stack_bytes"] - blocks[i]["envp_stack_bytes"]
                  for i in range(3)]
        if deltas != [1, 1, 1]:
            bad.append(f"N12 knob: envp_stack_bytes deltas {deltas}, want "
                       f"[1,1,1] -- the pad is not a one-byte-per-step lever")
        if len({b["nvars"] for b in blocks}) != 1:
            bad.append(f"N12 knob: nvars moved "
                       f"({sorted({b['nvars'] for b in blocks})}) -- a variable "
                       f"COUNT sweep has period 4, not 32, and would alias")
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--row")
    ap.add_argument("--cells", default=",".join(A.CELLS))
    ap.add_argument("--pads", type=int, default=32)
    ap.add_argument("--inputs", default="small.bin")
    ap.add_argument("--tag", default="envp")
    ap.add_argument("--axis", default="envp",
                    choices=["envp", "argv0", "argv1"])
    args = ap.parse_args()

    os.makedirs(OUT, exist_ok=True)
    bad = selftest(live=True)
    print(f"0. §H selftest {'PASS' if not bad else 'FAIL'}  "
          f"(10 knob_verdict arms + 5 axis_report arms + N7..N17, "
          f"+ php50_align_sweep's 19)")
    for b in bad:
        print(f"   *** {b}")
    if args.selftest:
        return 1 if bad else 0
    if bad:
        print("refusing to measure with a broken verdict arm", file=sys.stderr)
        return 1

    # ⭐ `--pads N` is N CONSECUTIVE byte values, never a decimated set. A
    # decimated set cannot distinguish "period 32" from "one 16-wide bump in a
    # longer period", and `--pads 64` exists precisely to test that: a cell that
    # is flat over 64 CONSECUTIVE values of `envp_stack_bytes` cannot be sitting
    # inside one state of a period-32 lever, and cannot be sitting inside one
    # state of a period-64 lever whose window is 32 either.
    pads = list(range(args.pads))
    cells = args.cells.split(",")
    result = {}
    for inp in args.inputs.split(","):
        print(f"\n=== {args.row} / {inp} / {A.OPT} {A.MODE} / "
              f"{args.axis.upper()} pads {pads}")
        print("   " + "".join(f"{c:>13s}" for c in cells))
        sw, probs, dc = AXES[args.axis](args.row, inp, pads, cells)
        v = A.verdicts(sw)
        steps = {c: A.step_of(s) for c, s in sw.items()}
        print(f"   dcalls={dc}  {args.axis.upper()} STEP PER CELL (Ir/call): " +
              ", ".join(f"{c}={steps[c]}" for c in sorted(steps)))
        for pair, (mid, rng, mag, sign, ratio) in sorted(v.items()):
            if mid is None:
                continue
            print(f"     {pair:26s} median {mid:>12.2f}  range {rng:>10.2f}"
                  f"  {mag:15s} {sign}")
        probs += A.problems_of(sw, pads)
        for p in probs:
            print(f"     *** {p}")
        result[f"{args.row}/{inp}"] = {
            "axis": args.axis, "pads": pads, "dcalls": dc, "sweep": sw,
            "steps": steps,
            "env_blocks": ({p: child_env_block(p) for p in pads}
                           if args.axis == "envp" else None),
            "verdicts": {k: list(x) for k, x in v.items()}, "problems": probs}
    dst = os.path.join(OUT, f"{args.tag}.json")
    json.dump(result, open(dst, "w"), indent=1, sort_keys=True)
    print(f"\nwrote {os.path.relpath(dst, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
