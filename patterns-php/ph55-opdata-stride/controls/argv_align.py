#!/usr/bin/env python3
"""ph55 control -- ⛔⛔ **W1 ON THIS ROW MOVES WITH THE LENGTH OF `argv[1]`, AND
ON ONE CELL THE MOVE IS BIGGER THAN THE THING BEING MEASURED.**

    python3 patterns-php/ph55-opdata-stride/controls/argv_align.py
    python3 patterns-php/ph55-opdata-stride/controls/argv_align.py --selftest

`.memory-php/03-numbers.md` warns, from `ph00`: *"`envp_stack_bytes` moved
3 686 -> 3 695 between two runs of the same gate with no source change. Measure a
mechanism; never difference two records taken in two shells and call the result
its cost."* ⭐ **This file is that warning firing on a live comparison, caught
before publication.**

**WHAT HAPPENED.** `../NOTES.md` §8b's R1-vs-R1h table was first computed with a
RELATIVE input path and gave `c-clang -> c-clang-h = -0.0007 Ir/call` -- free.
Recomputed with an ABSOLUTE path, the same two binaries gave **`-7.004
Ir/call` = `-0.398 %`**. Nothing was rebuilt; `md5sum` on both binaries is
unchanged across the two runs. **A `-0.398 %` "the fix is profitable under clang"
was one paste away from being published, and it is an artefact.**

**THE MECHANISM.** A longer `argv[1]` shifts the initial stack pointer, which
shifts the alignment of every frame below it. This kernel's frame is a
1 024-byte `[Op; 64]` and a 42-slot zval store, both zeroed on **every call**, so
an alignment change moves `memset`'s entry path -- and 7 Ir per call over 20 000
calls is 140 000 Ir, i.e. 0.4 % of the whole program. ⚠ THE MECHANISM IS
INFERRED FROM THE SIZE AND SHAPE OF THE STEP, NOT PROVEN: what is MEASURED is
that the total takes exactly two values and which one it takes depends on the
path length. `../NOTES.md` §13 says so.

**WHAT IT MEANS FOR THE ROW'S NUMBERS.** A *level* is unsafe to quote; a
*difference* is safe only if it is STABLE ACROSS THE SWEEP. Measured over eight
path lengths:

  c-gcc -> c-gcc-h        -395 640 +/- 30 Ir   ->  **-19.78 Ir/call, STABLE**
  c-clang -> c-clang-h     -28..+140 028 Ir    ->  **NOT RESOLVABLE**

▶ So `../NOTES.md` §8c publishes the gcc figure as a number and the clang figure
as *"free, and not resolvable below the alignment step"*, and that is what this
file certifies.

§H (`PROTOCOL_PHP.md`): the verdict function is a function so it can be attacked,
and `--selftest` drives it over synthetic sweeps -- four must-FIRE and three
must-NOT-fire.
"""

import argparse
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(PDIR))

sys.path.insert(0, HERE)
import _pin  # noqa: E402

BUILD = os.path.join(ROOT, ".temp", "php-scratch", "build", "ph55")
SCRATCH = os.path.join(ROOT, ".temp", "php55-align")
VALGRIND = os.path.expanduser("~/tools/valgrind/bin/valgrind")

_TOTAL = re.compile(r"^([\d,]+)\s.*PROGRAM TOTALS")

CELLS = ["c-gcc", "c-gcc-h", "c-clang", "c-clang-h",
         "safe_naive", "safe_tuned", "unsafe", "verus"]
#: The pairs whose DIFFERENCE the row publishes, and therefore the pairs whose
#: stability decides whether a number may be quoted at all.
PAIRS = [("c-gcc", "c-gcc-h"), ("c-clang", "c-clang-h"),
         ("safe_naive", "safe_tuned"), ("safe_tuned", "unsafe"),
         ("unsafe", "verus"), ("c-gcc-h", "unsafe"), ("c-clang-h", "unsafe"),
         ("c-gcc-h", "safe_tuned"), ("c-clang-h", "safe_tuned")]
#: A difference this small, relative to its own sweep range, is not a number.
#: ⚠ It is a RATIO and not an absolute: the gcc pair's 395 640 Ir survives a
#: 30 Ir wobble and the clang pair's 28 Ir does not survive a 140 028 Ir one.
STABLE_RATIO = 4.0

_M = None


def load_measure():
    global _M
    if _M is None:
        spec = importlib.util.spec_from_file_location(
            "slb_measure", os.path.join(ROOT, "harness", "measure.py"))
        _M = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_M)
    return _M


def w1_total(cell, path):
    exe = os.path.join(BUILD, f"{cell}-O3-isolated")
    if not os.path.exists(exe):
        return None, f"{cell}: no binary at {exe} -- run the gate's build tool first"
    M = load_measure()
    out = os.path.join(SCRATCH, "cg.out")
    r = subprocess.run([VALGRIND, "--tool=callgrind", "--callgrind-out-file=" + out,
                        exe, path], capture_output=True, text=True, timeout=7200)
    if r.returncode != 0:
        if os.path.exists(out):
            os.unlink(out)
        return None, f"callgrind exit {r.returncode} on {cell}: {r.stderr[-200:]}"
    if not os.path.exists(out):
        # ⚠ callgrind exited 0 and wrote nothing. It has happened once on this
        # box; a probe that cannot evaluate SAYS SO rather than returning a
        # figure-shaped 0 (probe rule 1).
        return None, (f"callgrind exited 0 but wrote no output file for {cell} "
                      f"-- the measurement did not happen")
    ann = subprocess.run([M.CG_ANNOTATE, "--threshold=100", out],
                         capture_output=True, text=True, timeout=600)
    txt = ann.stdout + ann.stderr
    os.unlink(out)
    for ln in txt.splitlines():
        m = _TOTAL.match(ln.strip())
        if m:
            return int(m.group(1).replace(",", "")), None
    return None, (f"callgrind_annotate printed no PROGRAM TOTALS for {cell} -- "
                  f"a probe that cannot evaluate must say so")


# ---- the verdict, factored so it can be ATTACKED ----------------------------

def stability(sweep):
    """`{pair: (median_delta, range, magnitude_verdict, sign_verdict)}`.

    ⭐⭐ **TWO VERDICTS AND NOT ONE, AND THE SPLIT IS A CORRECTION THIS FILE
    FORCED.** Its first version had only the magnitude test, and it refused
    `c-clang-h -> safe_tuned` -- whose delta is `+76 223` with a range of
    `+140 123`, i.e. it takes the values `+216 k` and `+76 k` depending on which
    side of the alignment step `c-clang-h` lands on. **Both are POSITIVE.** So
    the MAGNITUDE is not quotable and the SIGN is, and `../NOTES.md` §8d's F108
    headline -- *`safe_tuned` is faster than gcc and slower than clang* -- needs
    only the sign. Collapsing the two would have thrown away a real result to
    avoid quoting an unreal one.

      MAGNITUDE  RESOLVABLE when `|median| >= STABLE_RATIO * range`.
      SIGN       SIGN-STABLE when every delta in the sweep has the same sign
                 and none is zero.
    """
    out = {}
    for a, b in PAIRS:
        va, vb = sweep.get(a), sweep.get(b)
        if not va or not vb or len(va) != len(vb):
            out[f"{a}->{b}"] = (None, None, "UNMEASURED", "UNMEASURED")
            continue
        d = [y - x for x, y in zip(va, vb)]
        rng = max(d) - min(d)
        mid = sorted(d)[len(d) // 2]
        mag = "RESOLVABLE" if (rng == 0 or abs(mid) >= STABLE_RATIO * rng) \
            else "NOT RESOLVABLE"
        sign = "SIGN-STABLE" if (all(x > 0 for x in d) or all(x < 0 for x in d)) \
            else "SIGN-UNSTABLE"
        out[f"{a}->{b}"] = (mid, rng, mag, sign)
    return out


def align_problems(sweep, claims):
    """`claims` is `{pair: "RESOLVABLE"|"NOT RESOLVABLE"}` -- what `../NOTES.md`
    SAYS. This fails when the measurement stops agreeing with the prose.

    1. a pair the row publishes as a number must measure RESOLVABLE;
    2. a pair the row publishes as *not resolvable* must measure NOT
       RESOLVABLE -- ⭐ so a future toolchain that makes the clang figure real
       fails here rather than leaving §8c understating a result;
    3. every cell must have been measured at every path length, or the sweep is
       comparing different populations;
    4. at least ONE cell must move across the sweep. If nothing moves, this
       file is measuring nothing and its conclusion is vacuous -- which is the
       failure mode a green run cannot otherwise distinguish.
    """
    p = []
    st = stability(sweep)
    for pair, want in sorted(claims.items()):
        row = st.get(pair, (None, None, "UNMEASURED", "UNMEASURED"))
        got = f"{row[2]}/{row[3]}"
        if got != want:
            p.append(f"{1 if want.startswith('RESOLVABLE') else 2}. {pair}: "
                     f"../NOTES.md publishes it as {want} and the sweep measures "
                     f"{got} (delta {row[0]}, range {row[1]})")
    n = {len(v) for v in sweep.values()}
    if len(n) > 1:
        p.append(f"3. the sweep has different lengths per cell ({sorted(n)}), so "
                 f"the pairs are differences of different populations")
    if sweep and all(len(set(v)) == 1 for v in sweep.values()):
        p.append("4. NO cell moved across the sweep, so this file measured no "
                 "alignment sensitivity at all and its conclusion is vacuous -- "
                 "either the sweep no longer perturbs the stack or the row's "
                 "frame stopped being alignment-sensitive")
    return p


def selftest():
    bad = []
    # the shipped shape: gcc pair stable and large, clang pair unstable and tiny
    good = {"c-gcc": [100, 100, 100, 100], "c-gcc-h": [60, 60, 60, 60],
            "c-clang": [80, 80, 90, 90], "c-clang-h": [80, 90, 80, 90],
            "safe_naive": [120, 120, 120, 120], "safe_tuned": [110, 110, 110, 110],
            "unsafe": [95, 95, 95, 95], "verus": [96, 96, 96, 96]}
    claims = {"c-gcc->c-gcc-h": "RESOLVABLE/SIGN-STABLE",
              "c-clang->c-clang-h": "NOT RESOLVABLE/SIGN-UNSTABLE"}
    cases = [
        ("P1 the shipped shape", good, claims, False, None),
        ("N1 the gcc pair goes unstable",
         {**good, "c-gcc-h": [60, 99, 60, 99]}, claims, True, "1."),
        ("N2 the clang pair becomes real",
         {**good, "c-clang-h": [40, 40, 41, 41]}, claims, True, "2."),
        ("N3 a cell measured at fewer lengths",
         {**good, "verus": [96, 96]}, claims, True, "3."),
        ("N4 nothing moves at all",
         {k: [1, 1, 1, 1] for k in good},
         {"c-gcc->c-gcc-h": "NOT RESOLVABLE/SIGN-UNSTABLE",
          "c-clang->c-clang-h": "NOT RESOLVABLE/SIGN-UNSTABLE"}, True, "4."),
        ("P2 a bigger but still stable gcc gap",
         {**good, "c-gcc-h": [10, 10, 10, 10]}, claims, False, None),
        ("P3 the Rust cells all move together",
         {**good, "unsafe": [95, 96, 95, 96], "verus": [96, 97, 96, 97]},
         claims, False, None),
        # ⭐ N5 IS THE CASE THAT FORCED THE SPLIT: a pair whose magnitude is not
        # resolvable but whose SIGN never moves. It must be publishable as a
        # sign and refused as a number.
        # deltas [220, 100, 220, 100]: median 220, range 120, so 220 < 4*120 and
        # the MAGNITUDE is not quotable -- while every delta is positive, so the
        # SIGN is. That is the shipped `c-clang-h -> safe_tuned` shape.
        ("N5 sign-stable but magnitude-unresolvable, claimed as a number",
         {**good, "c-clang-h": [80, 200, 80, 200], "safe_tuned": [300, 300, 300, 300]},
         {"c-clang-h->safe_tuned": "RESOLVABLE/SIGN-STABLE"}, True, "1."),
        ("P4 the same pair, claimed correctly",
         {**good, "c-clang-h": [80, 200, 80, 200], "safe_tuned": [300, 300, 300, 300]},
         {"c-clang-h->safe_tuned": "NOT RESOLVABLE/SIGN-STABLE"}, False, None),
    ]
    for label, sweep, cl, must_fire, arm in cases:
        got = align_problems(sweep, cl)
        if bool(got) != must_fire:
            bad.append(f"selftest {label}: fired={bool(got)}, want {must_fire} ({got})")
        elif must_fire and arm and not any(g.startswith(arm) for g in got):
            bad.append(f"selftest {label}: fired on {[g[:2] for g in got]}, want {arm}")
    return bad


#: What `../NOTES.md` §8b/§8c SAY. The selftest above proves both verdicts can
#: fire; this is what the live sweep is checked against.
CLAIMS = {"small.bin": {
    # ⭐ the upstream fix: a real number under gcc, free-and-unresolvable under
    # clang. ../NOTES.md §8c.
    "c-gcc->c-gcc-h": "RESOLVABLE/SIGN-STABLE",
    "c-clang->c-clang-h": "NOT RESOLVABLE/SIGN-UNSTABLE",
    # the same-language ladder: every step survives the sweep.
    "safe_naive->safe_tuned": "RESOLVABLE/SIGN-STABLE",
    "safe_tuned->unsafe": "RESOLVABLE/SIGN-STABLE",
    "unsafe->verus": "RESOLVABLE/SIGN-STABLE",
    # the cross-language column. ⚠ THE ONE THAT IS SIGN-ONLY is the one the
    # F108 headline rests on, and it is published as a sign and a range rather
    # than as a percentage.
    "c-gcc-h->unsafe": "RESOLVABLE/SIGN-STABLE",
    "c-clang-h->unsafe": "RESOLVABLE/SIGN-STABLE",
    "c-gcc-h->safe_tuned": "RESOLVABLE/SIGN-STABLE",
    "c-clang-h->safe_tuned": "NOT RESOLVABLE/SIGN-STABLE",
}, "large.bin": {
    # ⚠ PER INPUT, AND IT HAS TO BE: `c-clang-h -> safe_tuned` is NOT
    # RESOLVABLE on `small.bin` (delta 76 223 against a 140 123 step) and
    # RESOLVABLE on `large.bin` (delta 7 275 588 against the SAME step), because
    # the alignment term is FIXED PER CALL while the work is not. A single
    # table would have had to pick one and be wrong about the other.
    "c-gcc->c-gcc-h": "RESOLVABLE/SIGN-STABLE",
    "c-clang->c-clang-h": "NOT RESOLVABLE/SIGN-UNSTABLE",
    "safe_naive->safe_tuned": "RESOLVABLE/SIGN-STABLE",
    "safe_tuned->unsafe": "RESOLVABLE/SIGN-STABLE",
    "unsafe->verus": "RESOLVABLE/SIGN-STABLE",
    "c-gcc-h->unsafe": "RESOLVABLE/SIGN-STABLE",
    "c-clang-h->unsafe": "RESOLVABLE/SIGN-STABLE",
    "c-gcc-h->safe_tuned": "RESOLVABLE/SIGN-STABLE",
    "c-clang-h->safe_tuned": "RESOLVABLE/SIGN-STABLE",
}}


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--input", default="small.bin")
    ap.add_argument("--steps", type=int, default=8,
                    help="path lengths to sweep, in steps of 2 bytes")
    args = ap.parse_args()

    problems = list(selftest())
    print("0. §H -- THE VERDICT ARM, ATTACKED OVER SYNTHETIC SWEEPS")
    print(f"   selftest {'PASS' if not problems else 'FAIL'}   "
          f"7 arms (4 must-FIRE, 3 must-NOT-fire)")
    for p in problems:
        print(f"     *** {p}")
    if args.selftest:
        return 1 if problems else 0

    os.makedirs(SCRATCH, exist_ok=True)
    src = os.path.join(PDIR, "inputs", args.input)
    sweep = {c: [] for c in CELLS}
    lens = []
    print(f"\n1. THE SWEEP -- the SAME binaries and the SAME input bytes, under "
          f"{args.steps} different path lengths")
    print("   " + "".join(f"{c:>13s}" for c in ["len"] + CELLS))
    for i in range(args.steps):
        name = os.path.join(SCRATCH, "p" * (2 * i) + args.input)
        shutil.copy(src, name)
        row = []
        for c in CELLS:
            t, e = w1_total(c, name)
            if e:
                problems.append(e)
                t = None
            row.append(t)
            if t is not None:
                sweep[c].append(t)
        os.unlink(name)
        lens.append(len(name))
        print("   " + f"{len(name):>13d}" + "".join(
            f"{(t if t is not None else 0):>13d}" for t in row))

    print("\n2. ⭐ WHICH DIFFERENCES SURVIVE IT -- a LEVEL is never quotable; a\n"
          "   DIFFERENCE is quotable only when it exceeds its own sweep range by "
          f"{STABLE_RATIO:g}x")
    st = stability(sweep)
    for pair, (mid, rng, mag, sign) in sorted(st.items()):
        if mid is None:
            print(f"   {pair:28s} UNMEASURED")
            continue
        mark = "   " if mag == "RESOLVABLE" else " ⛔"
        print(f"  {mark}{pair:28s} median delta {mid:>10d} Ir   sweep range "
              f"{rng:>8d} Ir   {mag:14s} {sign}")

    claims = CLAIMS.get(args.input)
    if claims is None:
        problems.append(f"no CLAIMS entry for {args.input}: this file can measure "
                        f"the sweep but has nothing to check it against")
        claims = {}
    problems.extend(align_problems(sweep, claims))
    out = {"input": args.input, "path_lengths": lens, "sweep": sweep,
           "stability": {k: list(v) for k, v in st.items()},
           "claims": claims, "problems": problems}
    # ⚠ ONE FILE PER INPUT. A single `argv_align.json` had the large.bin run
    # silently overwrite the small.bin one, and the two disagree by design.
    dst = os.path.join(HERE, f"argv_align.{args.input.replace('.bin', '')}.json")
    out.update(_pin.pin(
        ['c/kernel.c', 'c/kernel_hardened.c', 'c/main.c', 'safe_naive.rs', 'safe_tuned.rs', 'unsafe.rs', 'verus.rs', 'inputs/gen.py', 'controls/argv_align.py'],
        'python3 patterns-php/ph55-opdata-stride/controls/argv_align.py --input small.bin',
        'the same set statistic.py pins, because the sweep is over the same eight cells. The CLAIMS table inside this script is what ../NOTES.md 8b-2 publishes, so a change to either shows up here.'))
    json.dump(out, open(dst, "w"), indent=2, sort_keys=True)
    print(f"\nwrote {os.path.relpath(dst, ROOT)}")
    for p in problems:
        print(f"  *** {p}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
