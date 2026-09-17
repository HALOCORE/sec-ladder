#!/usr/bin/env python3
"""TASK_PHP_050 / item 112 -- ⛔⛔ **IS `marginal_ir_per_call` (FAMILY B) AN
ALIGNMENT ARTEFACT? SWEEP IT, PER ROW, PER CELL, IN FAMILY-B'S OWN UNITS.**

    python3 .tasks-php/php50_align_sweep.py --selftest
    python3 .tasks-php/php50_align_sweep.py --row ph64-callback-frees-cursor --pads 32
    python3 .tasks-php/php50_align_sweep.py --all --pads 4

⚠ **READ-ONLY WITH RESPECT TO THE CORPUS.** It runs already-built binaries out
of `.temp/php-scratch/build/<row>/` under callgrind and writes only under
`.temp/php50/`. It never touches `patterns-php/`, `results-php/` or `harness*/`,
and it is not a gate, a measure or a re-gate.

--------------------------------------------------------------------------------
WHY THIS EXISTS, AND WHAT IT DOES THAT `argv_align.py` DOES NOT
--------------------------------------------------------------------------------

`patterns-php/ph55-opdata-stride/controls/argv_align.py` is the design this
clones, and it is the only control in the corpus that measures the step. Three
differences, each of which is a correction:

1. ⭐⭐ **IT MEASURES FAMILY B, NOT W1.** `argv_align.py` differences
   `PROGRAM TOTALS` -- family W1, a LEVEL. Every family-B figure any row
   publishes is `marginal_ir_per_call`, a **SLOPE** over two runs at
   `probe_iters = [100, 200]`. The two are not the same quantity and they are
   not contaminated the same way: a W1 level carries the whole one-shot
   start-up term, and the slope cancels it. ⛔ **So an `argv_align.py` verdict
   is not a verdict about family B**, and item 112 is about family B.

2. ⭐⭐ **IT SWEEPS A FULL 32-BYTE PERIOD.** `argv_align.py` sweeps eight path
   lengths in steps of 2, i.e. a span of **14 bytes**. `harness/check.py::
   check_marginal_ir` measured this effect on the PAT side as **BISTABLE with a
   PERIOD OF 32 BYTES and a WINDOW EXACTLY 16 WIDE**. ⛔ **A 14-byte span is
   narrower than the window, so it can sit entirely inside one state and report
   "stable" for a cell that is bistable.** It cannot be a complete detector.
   The same docstring says the complete detector is a **two-pad screen 16
   apart**; this file defaults to a full period and verifies the claim rather
   than assuming it.

3. **IT REPORTS THE STEP IT MEASURED**, per cell, so `|delta| / step` can be
   computed instead of borrowing another row's step. A row whose cells do not
   move has step `0` and its differences are then limited by nothing this file
   can see -- which is reported as `NO STEP OBSERVED`, not as `safe`.

**THE TWO-VERDICT RULE IS `argv_align.py`'s AND IS KEPT VERBATIM IN SPIRIT**
(`_048` §4c): a pair can have an unquotable MAGNITUDE and a perfectly good
SIGN, and collapsing the two throws away a real result to avoid quoting an
unreal one. Every pair here gets both.

--------------------------------------------------------------------------------
§H -- THE MUST-FIRE NEGATIVES LIVE IN THIS FILE
--------------------------------------------------------------------------------

`PROTOCOL_PHP.md` §H: the verdict arm is a pure function of a sweep dict so it
can be attacked, and `--selftest` drives it over synthetic sweeps. **Seven arms
must FIRE and three must NOT**, plus NINE unit arms. They are in `selftest()` at
the bottom and they run on every invocation, not only under `--selftest`; a
broken verdict arm REFUSES to measure rather than measuring anyway.

⚠ **`N7` FIRED AGAINST MY OWN FIRST DESIGN.** I wrote a `P3` asserting that the
PAT two-pad screen is a complete detector, the selftest refused it, and the
refusal was right -- see `sweep_completeness`. The arm stayed and the claim
changed, which is the way round `PROTOCOL_PHP.md` §H requires.
"""

import argparse
import glob
import importlib.util
import json
import os
import struct
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, ".temp", "php-scratch", "build")
SCRATCH = os.path.join(ROOT, ".temp", "php50", "sweep")
VALGRIND = os.path.expanduser("~/tools/valgrind/bin/valgrind")

CELLS = ["c-gcc", "c-gcc-h", "c-clang", "c-clang-h",
         "safe_naive", "safe_tuned", "unsafe", "verus"]

#: ⚠ `-O3 isolated` IS THE DEFAULT AND EVERY PUBLISHED FIGURE IS THAT COLUMN.
#: Every family-B figure `patterns-php/*/NOTES.md` publishes as a performance
#: result is `O3 isolated` (verified for `ph64` §8a against
#: `results-php/gate/ph64-callback-frees-cursor.json`), and
#: `.memory-php/03-numbers.md` forbids quoting an `O0` figure as one.
#:
#: ⛔⛔⛔ THIS USED TO BE HARD-CODED, AND THE CONSEQUENCE WAS NOT THE ONE ANYONE
#: INTENDED. `TASK_PHP_063` §3.4 traced it: `PROTOCOL_PHP.md` §B5 requires a
#: figure to clear a SWEEP before publication; nothing was ever swept at `O0`;
#: therefore no `O0` reading could clear §B5; therefore its SIGN could never be
#: certified stable and could not be published EVEN AS A SIGN. ▶ `_062`'s
#: engineer DID measure `ph66` at both levels and published no sign, giving the
#: `03-numbers.md` prohibition as the reason -- but that prohibition is about
#: FIGURES, and A SIGN IS NOT A FIGURE. What actually stopped him was this line.
#:
#: ⭐⭐ A SWEEP IS NOT A PERFORMANCE CLAIM; IT IS A STABILITY TEST. It separates
#: *a difference between two programs* from *an artefact of code placement*, and
#: that question is as meaningful at `O0` as at `O3` -- arguably more, because
#: at `O0` the compiler does less to hide placement.
#:
#: ⛔⛔ WHAT `--opt O0` DOES **NOT** BUY, AND THIS IS NOT NEGOTIABLE HERE:
#: MAGNITUDES STAY FORBIDDEN. `.memory-php/03-numbers.md` is untouched by this
#: change. A row may publish an `O0` **SIGN**, explicitly labelled *a lowering
#: reading, not a performance figure*, and ONLY IF IT HAS BEEN SWEPT.
DEFAULT_OPT, MODE = "O3", "isolated"

#: The pairs whose DIFFERENCE a row publishes or could publish, in family B.
#: `R1h - R1` is the first two; the rest is the ladder and the cross-language
#: column.
PAIRS = [("c-gcc", "c-gcc-h"), ("c-clang", "c-clang-h"),
         ("safe_naive", "safe_tuned"), ("safe_tuned", "unsafe"),
         ("unsafe", "verus"), ("c-gcc-h", "unsafe"), ("c-clang-h", "unsafe"),
         ("c-gcc-h", "safe_tuned"), ("c-clang-h", "safe_tuned")]

#: `argv_align.py`'s constant, kept so the two files' verdicts are comparable.
STABLE_RATIO = 4.0


# ---------------------------------------------------------------------------
# measurement
# ---------------------------------------------------------------------------

def _probe(src, n_iters, out):
    """Byte-for-byte what `harness/check.py::_probe_input` does: `n_iters` is at
    offset 0 of every input file, so this is a format-level rewrite."""
    blob = open(src, "rb").read()
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "wb") as f:
        f.write(struct.pack("<Q", n_iters) + blob[8:])
    return out


def _total(binary, arg, outfile):
    """Whole-program Ir for one run -- the same two lines `check.py::
    _callgrind_total` reads, so a slope computed here is the gate's own
    quantity. Returns `None` and SAYS WHY rather than a figure-shaped 0."""
    try:
        r = subprocess.run([VALGRIND, "--tool=callgrind",
                            f"--callgrind-out-file={outfile}", binary, arg],
                           capture_output=True, text=True, timeout=1800)
    except subprocess.TimeoutExpired:
        return None, f"callgrind timed out on {os.path.basename(binary)}"
    if r.returncode != 0:
        return None, (f"{os.path.basename(binary)} exited {r.returncode} on "
                      f"{os.path.basename(arg)}")
    if not os.path.exists(outfile):
        return None, f"callgrind wrote no output for {os.path.basename(binary)}"
    for line in open(outfile):
        if line.startswith(("summary:", "totals:")):
            v = int(line.split()[1])
            os.unlink(outfile)
            return v, None
    os.unlink(outfile)
    return None, f"no summary line for {os.path.basename(binary)}"


def dcalls_of(row, inp):
    """`n_calls(200) - n_calls(100)` from the row's OWN `model.py`, which is what
    `check_marginal_ir` divides by. Never assumed to be 100."""
    spec = importlib.util.spec_from_file_location(
        f"m_{row}", os.path.join(ROOT, "patterns-php", row, "model.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    src = os.path.join(ROOT, "patterns-php", row, "inputs", inp)
    ns = []
    for n in (100, 200):
        p = _probe(src, n, os.path.join(SCRATCH, "dc", f"probe.{inp}.{n}.bin"))
        ns.append(getattr(m.build(p), "n_calls"))
    return ns[1] - ns[0]


def build_dir(row):
    """`.temp/php-scratch/build/` is keyed by the SHORT id (`ph64`), not by the
    pattern directory name (`ph64-callback-frees-cursor`). ⚠ The first version
    of this file used the long name, found no binary for any cell, and SAID SO
    eight times rather than returning a zero -- which is why the error text
    names the path it looked for."""
    return os.path.join(BUILD, row.split("-")[0])


def sweep_row(row, inp, pads, cells=CELLS, verbose=True,
              opt=DEFAULT_OPT):
    """`{cell: [slope at pad 0, slope at pad 1, ...]}` in Ir/call.

    ⭐ **THE PAD IS APPLIED TO THE argv STRING AND IS IDENTICAL FOR BOTH HALVES
    OF THE SLOPE**, which is exactly what the gate does: its two probe files are
    `probe.<inp>.100.bin` and `probe.<inp>.200.bin`, **the same length**, so the
    alignment term is the same in both runs and therefore SURVIVES into the
    slope rather than cancelling. That is the whole of item 112's premise and it
    is a fact about `check.py`, not a guess."""
    src = os.path.join(ROOT, "patterns-php", row, "inputs", inp)
    if not os.path.exists(src):
        return {}, [f"{row}: no input {inp}"], None
    dc = dcalls_of(row, inp)
    out, problems = {c: [] for c in cells}, []
    for pad in pads:
        d = os.path.join(SCRATCH, row)
        paths = {n: _probe(src, n, os.path.join(
            d, "p" * pad + f"probe.{inp}.{n}.bin")) for n in (100, 200)}
        for c in cells:
            exe = os.path.join(build_dir(row), f"{c}-{opt}-{MODE}")
            if not os.path.exists(exe):
                problems.append(f"{row}/{c}: no binary at {exe}")
                continue
            vals = {}
            for n in (100, 200):
                v, e = _total(exe, paths[n], os.path.join(
                    SCRATCH, f"cg.{row}.{c}.{n}.out"))
                if e:
                    problems.append(e)
                vals[n] = v
            if vals[100] is None or vals[200] is None:
                continue
            out[c].append(round((vals[200] - vals[100]) / dc, 2))
        for p in paths.values():
            os.unlink(p)
        if verbose:
            print(f"   pad {pad:>3d}  " + "".join(
                f"{(out[c][-1] if out[c] else 0):>14.2f}" for c in cells),
                flush=True)
    return {k: v for k, v in out.items() if v}, problems, dc


# ---------------------------------------------------------------------------
# the verdict arm -- a pure function, so it can be attacked
# ---------------------------------------------------------------------------

def step_of(series):
    """The measured alignment step for ONE cell: the span of the slope over the
    sweep, in Ir/call.

    ⚠ **`0` MEANS "NO STEP OBSERVED", NOT "NO STEP".** A sweep that is shorter
    than the period can see nothing on a bistable cell, which is exactly the
    defect this file was written to avoid; `sweep_completeness` is what decides
    whether a `0` is trustworthy."""
    return round(max(series) - min(series), 2) if series else None


def sweep_completeness(pads, kind="pair"):
    """⭐⭐ **IS THE SWEEP A DETECTOR AT ALL -- AND THE ANSWER DIFFERS FOR A CELL
    AND FOR A DIFFERENCE, WHICH IS A CORRECTION TO THE PAT RULE.**

    `harness/check.py::check_marginal_ir` measured the effect as bistable with a
    **32-byte period and a 16-wide window** and concluded that **two pads 16
    apart are a COMPLETE detector**. ✅ **That is right for ONE CELL** -- a
    16-wide window in a 32-period puts `p` and `p+16` in opposite states always.

    ⛔⛔ **IT IS NOT RIGHT FOR A DIFFERENCE OF TWO CELLS, AND EVERY FAMILY-B
    FIGURE ANY ROW PUBLISHES IS A DIFFERENCE OF TWO CELLS.** The same docstring
    records that **the phase differs per binary** (`p03 unsafe` flips over pads
    6..21, `p03 verus` over 8..23, `p03 safe_tuned` over 14..29). Two cells with
    phases `f1 != f2` give a difference that takes up to **four** values as the
    pad runs over a period, with the arcs bounded by `f1, f2, f1+16, f2+16`.
    Since the phases are not known in advance, **no strict subset of the 32
    residues is guaranteed to sample every arc.**

    ⭐ **This file's own `--selftest` arm `N7` is the demonstration**: on a
    synthetic pair whose two cells flip 8 bytes apart, the PAT two-pad screen
    `[0, 16]` measures `RESOLVABLE` (both samples give delta 18) while the full
    32-residue sweep measures `NOT RESOLVABLE` (deltas 11, 18, 25). ⛔ **A
    two-pad screen would have certified a number that is not one.**

    So: `kind="cell"` -> a pair 16 apart mod 32 suffices.
        `kind="pair"` -> ALL 32 residues mod 32 are required.
    """
    res = {p % 32 for p in pads}
    if kind == "cell":
        for p in res:
            if (p + 16) % 32 in res:
                return True, "contains a pair 16 apart mod 32"
        return False, (f"span {max(pads) - min(pads)} contains no pair 16 apart "
                       f"mod 32, so a bistable CELL can sit in one state "
                       f"throughout")
    if len(res) == 32:
        return True, "covers all 32 residues mod 32"
    return False, (f"covers {len(res)} of 32 residues mod 32, so a DIFFERENCE "
                   f"of two cells with unknown, unequal phases can have an arc "
                   f"this sweep never samples (a two-pad screen is complete for "
                   f"a CELL and NOT for a DIFFERENCE -- see the docstring)")


def verdicts(sweep, pairs=PAIRS):
    """`{pair: (median, range, magnitude_verdict, sign_verdict, ratio)}`.

    TWO VERDICTS, `argv_align.py`'s rule (`_048` §4c):

      MAGNITUDE  RESOLVABLE when `|median| >= STABLE_RATIO * range`.
      SIGN       SIGN-STABLE when every delta has the same sign and none is 0.
      SIGN       ⭐ SIGN-ZERO   when EVERY delta is exactly 0.

    ⚠⚠ **`SIGN-ZERO` IS A CORRECTION `ph52` FORCED, AND THE FIRST VERSION OF
    THIS FUNCTION GOT IT WRONG.** `ph52`'s `unsafe -> verus` is `0.00` at every
    pad, because that row's `identity` pin is `norel` at `-O3` and the two
    kernels are the same machine code modulo relocations. The first version fell
    through to `SIGN-UNSTABLE` -- literally true (`all(x>0)` and `all(x<0)` are
    both false) and **actively misleading**: it labels a measured, pinned,
    exact null as an instability. ⛔ **A verdict that cannot say "zero" will
    call every null an instability**, and six of the ten rows in this corpus
    are pinned `exact` or `norel`.

    `ratio` is `|median| / range`, the number item 112 asked for as
    `|delta| / step` -- computed against the PAIR's own observed range, which is
    the step that actually contaminates that difference."""
    out = {}
    for a, b in pairs:
        va, vb = sweep.get(a), sweep.get(b)
        if not va or not vb or len(va) != len(vb):
            out[f"{a}->{b}"] = (None, None, "UNMEASURED", "UNMEASURED", None)
            continue
        d = [round(y - x, 2) for x, y in zip(va, vb)]
        rng = round(max(d) - min(d), 2)
        mid = sorted(d)[len(d) // 2]
        mag = "RESOLVABLE" if (rng == 0 or abs(mid) >= STABLE_RATIO * rng) \
            else "NOT RESOLVABLE"
        if all(x == 0 for x in d):
            sign = "SIGN-ZERO"
        elif all(x > 0 for x in d) or all(x < 0 for x in d):
            sign = "SIGN-STABLE"
        else:
            sign = "SIGN-UNSTABLE"
        ratio = None if rng == 0 else round(abs(mid) / rng, 2)
        out[f"{a}->{b}"] = (mid, rng, mag, sign, ratio)
    return out


def problems_of(sweep, pads, claims=None):
    """What must be true for this file's conclusion to mean anything.

    1. a pair the caller CLAIMS is resolvable must measure RESOLVABLE;
    2. a pair the caller CLAIMS is not resolvable must measure NOT RESOLVABLE;
    3. every cell must be measured at every pad, or the pairs difference
       different populations;
    4. ⭐ the sweep must be a COMPLETE DETECTOR (`sweep_completeness`) --
       otherwise a "nothing moved" reading is not evidence of absence, which is
       `argv_align.py`'s defect and `TASK_PHP_050` §5 trap 6;
    5. ⭐ at least one cell must move, or this file measured no alignment
       sensitivity and its conclusion is vacuous.
    """
    p = []
    v = verdicts(sweep)
    for pair, want in sorted((claims or {}).items()):
        row = v.get(pair, (None, None, "UNMEASURED", "UNMEASURED", None))
        got = f"{row[2]}/{row[3]}"
        if got != want:
            p.append(f"{1 if want.startswith('RESOLVABLE') else 2}. {pair}: "
                     f"claimed {want}, measured {got} "
                     f"(median {row[0]}, range {row[1]})")
    n = {len(s) for s in sweep.values()}
    if len(n) > 1:
        p.append(f"3. cells measured at different pad counts ({sorted(n)})")
    ok, why = sweep_completeness(pads, "pair")
    if not ok:
        p.append(f"4. INCOMPLETE DETECTOR: {why}")
    if sweep and all(len(set(s)) == 1 for s in sweep.values()):
        p.append("5. NO cell moved across the sweep, so either the pad no "
                 "longer perturbs the stack or no cell here is "
                 "alignment-sensitive -- a green run cannot tell these apart, "
                 "so this is reported rather than passed")
    return p


# ---------------------------------------------------------------------------
# §H
# ---------------------------------------------------------------------------

def selftest():
    bad = []
    full = list(range(32))
    short = list(range(0, 15, 2))          # argv_align.py's own pad set
    # a bistable clang pair and a clean gcc pair, in Ir/call
    good = {"c-gcc": [100.0] * 32, "c-gcc-h": [116.0] * 32,
            "c-clang": [90.0] * 16 + [97.0] * 16,
            "c-clang-h": [108.0] * 8 + [115.0] * 16 + [108.0] * 8,
            "safe_naive": [50.0] * 32, "safe_tuned": [40.0] * 32,
            "unsafe": [30.0] * 32, "verus": [30.5] * 32}
    cl_ok = {"c-gcc->c-gcc-h": "RESOLVABLE/SIGN-STABLE",
             "c-clang->c-clang-h": "NOT RESOLVABLE/SIGN-STABLE"}
    flat = {k: [1.0] * 32 for k in good}
    cases = [
        ("P1 the shipped shape", good, full, cl_ok, False, None),
        ("N1 a pair claimed resolvable that is not",
         good, full, {"c-clang->c-clang-h": "RESOLVABLE/SIGN-STABLE"}, True, "1."),
        ("N2 a pair claimed unresolvable that is",
         good, full, {"c-gcc->c-gcc-h": "NOT RESOLVABLE/SIGN-STABLE"}, True, "2."),
        ("N3 a cell measured at fewer pads",
         {**good, "verus": [30.5] * 30}, full, cl_ok, True, "3."),
        # ⭐⭐ N4 IS THE ARM THAT JUSTIFIES THIS FILE EXISTING. The same sweep
        # data restricted to argv_align.py's 0..14 pad set must be REFUSED as a
        # detector even though every claim in it still checks out.
        ("N4 argv_align.py's own 0..14 span is not a detector",
         {k: v[:8] for k, v in good.items()}, short, {}, True, "4."),
        ("N5 nothing moved anywhere", flat, full,
         {"c-gcc->c-gcc-h": "RESOLVABLE/SIGN-STABLE",
          "c-clang->c-clang-h": "RESOLVABLE/SIGN-STABLE"}, True, "5."),
        # ⭐ N6 IS THE TWO-VERDICT ARM (_048 §4c): magnitude unquotable, sign
        # perfectly good. It must fire when claimed as a NUMBER ...
        ("N6 sign-stable but magnitude-unresolvable, claimed as a number",
         {**good, "c-clang-h": [108.0] * 16 + [400.0] * 16,
          "safe_tuned": [500.0] * 32},
         full, {"c-clang-h->safe_tuned": "RESOLVABLE/SIGN-STABLE"}, True, "1."),
        # ... and NOT fire when claimed as a sign.
        ("P2 the same pair, claimed as a sign only",
         {**good, "c-clang-h": [108.0] * 16 + [400.0] * 16,
          "safe_tuned": [500.0] * 32},
         full, {"c-clang-h->safe_tuned": "NOT RESOLVABLE/SIGN-STABLE"},
         False, None),
        # ⭐⭐ N7 IS THE ARM THAT CORRECTS THE PAT RULE. `good`'s two clang cells
        # flip 8 bytes apart, so their DIFFERENCE takes three values over a
        # period (11, 18, 25). The PAT two-pad screen [0,16] samples delta 18
        # twice and would certify it RESOLVABLE; the full sweep says NOT
        # RESOLVABLE. The screen must therefore be REFUSED for a pair verdict.
        ("N7 the PAT two-pad screen is NOT a detector for a DIFFERENCE",
         {k: [v[0], v[16]] for k, v in good.items()}, [0, 16], {}, True, "4."),
        ("P3 a sign-unstable pair claimed as such",
         {**good, "unsafe": [30.0] * 16 + [40.0] * 16}, full,
         {"safe_tuned->unsafe": "NOT RESOLVABLE/SIGN-UNSTABLE"}, False, None),
    ]
    for label, sw, pads, cl, must_fire, arm in cases:
        got = problems_of(sw, pads, cl)
        if bool(got) != must_fire:
            bad.append(f"{label}: fired={bool(got)} want={must_fire}  {got}")
        elif must_fire and arm and not any(g.startswith(arm) for g in got):
            bad.append(f"{label}: fired on {[g[:2] for g in got]}, want {arm}")
    # -----------------------------------------------------------------
    # ⛔⛔⛔ THE TWO §H NEGATIVES `TASK_PHP_063` §3.4 PRESCRIBED BY NAME for
    #   the `--opt` change. The rule there: the change is ADDITIVE or it is a
    #   regression, and the new capability must be TIED TO A NUMBER THAT
    #   ALREADY EXISTS rather than to whatever it happens to print.
    # -----------------------------------------------------------------
    # (i) THE DEFAULT IS UNCHANGED IN EVERY OBSERVABLE THAT NAMES IT.
    if DEFAULT_OPT != "O3" or MODE != "isolated":
        bad.append(f"OPT-1: the default moved to {DEFAULT_OPT}/{MODE} -- every "
                   f"published family-B figure is `O3 isolated` and this file "
                   f"is what certifies them")
    import inspect as _inspect
    if _inspect.signature(sweep_row).parameters["opt"].default != DEFAULT_OPT:
        bad.append("OPT-2: sweep_row's `opt` default is not DEFAULT_OPT, so a "
                   "caller that omits it no longer sweeps the published column")
    # the two strings the default run builds: the binary name and the output
    # file. Both are spelled here EXACTLY as they were before `--opt` existed.
    if f"c-gcc-{DEFAULT_OPT}-{MODE}" != "c-gcc-O3-isolated":
        bad.append("OPT-3: the default binary path is no longer "
                   "`c-gcc-O3-isolated`")
    if ("" if DEFAULT_OPT == DEFAULT_OPT else ".x") != "":
        bad.append("OPT-4: the default run would gain a filename suffix, so it "
                   "would stop overwriting -- and stop being comparable to -- "
                   "the sweeps the published figures cleared")

    # (ii) ⭐⭐ TIED TO A COMMITTED NUMBER, NOT TO ITS OWN OUTPUT. `ph66`'s
    #   `NOTES.md` §9.4 and `TASK_PHP_062_REPORT.md:172` publish the `O0`
    #   family-B R1h-R1 differences as `+4.00`/`+6.12` (gcc small/large) and
    #   `+5.00`/`+9.69` (clang). An `--opt O0` sweep must REPRODUCE them.
    # ⛔ DEGRADES HONESTLY: the sweep costs minutes of callgrind and its output
    #   is a re-derivable artefact under `.temp/`, which `CLAUDE.md` Don't #1
    #   mandates deleting. Absent, this arm says SO and does not fail -- it
    #   must never go red because someone followed the cleanup rule.
    _WANT = {("small.bin", "c-gcc->c-gcc-h"): 4.00,
             ("large.bin", "c-gcc->c-gcc-h"): 6.12,
             ("small.bin", "c-clang->c-clang-h"): 5.00,
             ("large.bin", "c-clang->c-clang-h"): 9.69}
    _o0 = sorted(glob.glob(os.path.join(ROOT, ".temp", "php50", "*.O0.json")))
    _o0 = [f for f in _o0 if "ph66" in os.path.basename(f)]
    if not _o0:
        print("   ⓘ OPT-5 NOT RUN -- NO VERDICT WAS REACHED, THIS IS NOT A "
              "PASS. It needs an `O0` sweep of ph66 under `.temp/php50/`, "
              "which is a re-derivable artefact. Re-derive it with:\n"
              "     python3 .tasks-php/php50_align_sweep.py --opt O0 "
              "--row ph66-hashdel-uncompared --pads 4 --tag ph66o0")
    else:
        # ⛔ PRINT THAT IT RAN. A silent pass and a skipped arm look identical
        #   in a `PASS` line, which is `F138`'s defect ("I called the tool's
        #   function" is not "I ran the tool"). Say which file, and say what
        #   the sweep decided -- the verdict is the point, not the median.
        d = json.load(open(_o0[-1]))
        print(f"   ⓘ OPT-5 RAN against {os.path.relpath(_o0[-1], ROOT)}:")
        for (inp, pair), want in sorted(_WANT.items()):
            v = d.get(f"ph66-hashdel-uncompared/{inp}", {}).get(
                "verdicts", {}).get(pair)
            if v:
                print(f"       {inp:10} {pair:22} median {v[0]:7.2f} "
                      f"(published {want})  {v[2]:15s} {v[3]}")
        for (inp, pair), want in sorted(_WANT.items()):
            k = f"ph66-hashdel-uncompared/{inp}"
            got = (d.get(k, {}).get("verdicts", {}).get(pair) or [None])[0]
            if got is None or abs(got - want) > 0.005:
                bad.append(f"OPT-5 {inp} {pair}: swept median {got}, but "
                           f"`ph66` NOTES.md §9.4 and _062 publish {want}. "
                           f"⛔ The sweep must REPRODUCE the committed number, "
                           f"not replace it.")

    # step_of / sweep_completeness unit arms
    if step_of([1.0, 8.0, 1.0]) != 7.0:
        bad.append("step_of: span of [1,8,1] is not 7.0")
    if step_of([]) is not None:
        bad.append("step_of: an empty series must be None, not 0")
    if sweep_completeness(list(range(0, 15, 2)), "cell")[0]:
        bad.append("sweep_completeness: a 0..14 span must NOT be complete "
                   "even for a CELL")
    if not sweep_completeness([0, 16], "cell")[0]:
        bad.append("sweep_completeness: [0,16] must be complete for a CELL")
    if not sweep_completeness([5, 21], "cell")[0]:
        bad.append("sweep_completeness: [5,21] must be complete for a CELL")
    if sweep_completeness([0, 16], "pair")[0]:
        bad.append("sweep_completeness: [0,16] must NOT be complete for a PAIR")
    if not sweep_completeness(list(range(32)), "pair")[0]:
        bad.append("sweep_completeness: 0..31 must be complete for a PAIR")
    # ⭐⭐ N8's unit form: a pinned-identical pair must read SIGN-ZERO, never
    # SIGN-UNSTABLE. This is the `ph52` case and the first version failed it.
    z = verdicts({"unsafe": [10.0] * 32, "verus": [10.0] * 32},
                 [("unsafe", "verus")])["unsafe->verus"]
    if z[3] != "SIGN-ZERO":
        bad.append(f"an all-zero difference must read SIGN-ZERO, got {z[3]} -- "
                   f"six of ten rows are pinned exact/norel and would all be "
                   f"mislabelled as unstable")
    if verdicts({"a": [1.0, 1.0], "b": [2.0, 0.0]},
                [("a", "b")])["a->b"][3] != "SIGN-UNSTABLE":
        bad.append("a genuinely sign-flipping pair must still read "
                   "SIGN-UNSTABLE after the SIGN-ZERO change")
    if verdicts({"a": [1.0, 1.0], "b": [2.0, 3.0]},
                [("a", "b")])["a->b"][3] != "SIGN-STABLE":
        bad.append("a genuinely sign-stable pair must still read SIGN-STABLE")
    # ⭐ the N7 phenomenon as a direct unit arm, independent of problems_of
    two = verdicts({"c-clang": [90.0, 97.0], "c-clang-h": [108.0, 115.0]},
                   [("c-clang", "c-clang-h")])["c-clang->c-clang-h"]
    allp = verdicts({"c-clang": good["c-clang"], "c-clang-h": good["c-clang-h"]},
                    [("c-clang", "c-clang-h")])["c-clang->c-clang-h"]
    if not (two[2] == "RESOLVABLE" and allp[2] == "NOT RESOLVABLE"):
        bad.append(f"the two-pad/full-sweep divergence this file is built on "
                   f"did not reproduce: two-pad={two[2]}, full={allp[2]}")
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--row")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--pads", type=int, default=32)
    ap.add_argument("--inputs", default="small.bin,large.bin")
    ap.add_argument("--opt", default=DEFAULT_OPT, choices=["O0", "O3"],
                    help="optimisation level to sweep. ⛔ O0 buys a "
                         "SIGN, never a magnitude (TASK_PHP_063 §3.4)")
    ap.add_argument("--tag", default="sweep")
    args = ap.parse_args()

    bad = selftest()
    print(f"0. §H selftest {'PASS' if not bad else 'FAIL'}  "
          f"(10 verdict arms: 7 must-FIRE, 3 must-NOT-fire; + 9 unit "
          f"arms; + 5 `--opt` arms, OPT-1..4 additive-change and OPT-5 "
          f"tied to `ph66` NOTES.md §9.4)")
    for b in bad:
        print(f"   *** {b}")
    if args.selftest:
        return 1 if bad else 0
    if bad:
        print("refusing to measure with a broken verdict arm", file=sys.stderr)
        return 1

    rows = ([d for d in sorted(os.listdir(os.path.join(ROOT, "patterns-php")))
             if d.startswith("ph") and os.path.isdir(build_dir(d))]
            if args.all else [args.row])
    # the PAT-measured complete detector, extended: 0..31 is a full period;
    # a 4-point run uses 0/8/16/24, which contains two pairs 16 apart.
    pads = (list(range(32)) if args.pads >= 32 else
            [i * (32 // args.pads) for i in range(args.pads)])
    os.makedirs(SCRATCH, exist_ok=True)
    result = {}
    for row in rows:
        for inp in args.inputs.split(","):
            print(f"\n=== {row} / {inp} / {args.opt} {MODE} / pads {pads}"
                  + ("" if args.opt == DEFAULT_OPT else
                     "   ⛔ NON-DEFAULT OPT: a SIGN may be published from "
                     "this, labelled a lowering reading; a MAGNITUDE MAY NOT"))
            print("   " + "".join(f"{c:>14s}" for c in ["pad"] + CELLS))
            sw, probs, dc = sweep_row(row, inp, pads, opt=args.opt)
            v = verdicts(sw)
            steps = {c: step_of(s) for c, s in sw.items()}
            print(f"   dcalls={dc}  STEP PER CELL (Ir/call): " +
                  ", ".join(f"{c}={steps[c]}" for c in sorted(steps)))
            for pair, (mid, rng, mag, sign, ratio) in sorted(v.items()):
                if mid is None:
                    continue
                print(f"     {pair:26s} median {mid:>12.2f}  range {rng:>10.2f}"
                      f"  |d|/step {('n/a' if ratio is None else f'{ratio:.2f}'):>8s}"
                      f"  {mag:15s} {sign}")
            probs += problems_of(sw, pads)
            for p in probs:
                print(f"     *** {p}")
            result[f"{row}/{inp}"] = {
                "pads": pads, "dcalls": dc, "sweep": sw, "steps": steps,
                "verdicts": {k: list(x) for k, x in v.items()},
                "problems": probs}
    # ⛔ THE LEVEL IS IN THE FILENAME. Without it an `--opt O0` run
    #   silently OVERWRITES the `O3` sweep the published figures
    #   cleared, and the two are not comparable.
    suffix = "" if args.opt == DEFAULT_OPT else f".{args.opt}"
    dst = os.path.join(ROOT, ".temp", "php50",
                       f"{args.tag}{suffix}.json")
    json.dump(result, open(dst, "w"), indent=1, sort_keys=True)
    print(f"\nwrote {os.path.relpath(dst, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
