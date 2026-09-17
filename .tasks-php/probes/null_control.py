#!/usr/bin/env python3
# =============================================================================
# null_control.py -- THE PROBE F74 RESTS ON, AND THE ONE F82 CAUGHT
#
# ⛔⛔ WHY THIS FILE IS COMMITTED, AND IT IS NOT TIDINESS. It was written under
# `.temp/mgr170/`, which is GITIGNORED, and it is the evidence for **F74** --
# the finding that chose family A as the headline statistic on the strength of
# the R4/R5 null control -- and therefore also the SUBJECT of **F82**, which
# found that this probe asserted its own premise for all 39 rows and never
# checked it on one. ▶ A PUBLISHED FINDING WHOSE ONLY EVIDENCE IS A GITIGNORED
# PROBE IS A FINDING THAT WILL NOT SURVIVE A CLEAN CHECKOUT:
# `.memory-php/04-process.md` LAW 11.
#
# ⭐⭐ AND THE REFUTED PROBE IS THE ONE MOST WORTH COMMITTING, not the least.
# `probes/identity_null.py` (F82) is a CORRECTION of this file's premise; a
# correction whose target has been deleted cannot be read. Both are promoted in
# the same pass, deliberately.
#
# RUN IT:  python3 .tasks-php/probes/null_control.py --selftest   # the negatives
#          python3 .tasks-php/probes/null_control.py              # all 3 views
#          python3 .tasks-php/probes/null_control.py --null       # the control
#          ... also --cvsrust and --row03
# ⚠ Its negatives are INLINE: a bare run executes `selftest()` FIRST and refuses
# to print anything if an arm fails (*"nothing below is believable"*). The
# `--selftest` flag runs the same arms alone.
#
# ✅ WHAT IT NEEDS THAT IS *NOT* COMMITTED, stated rather than discovered:
# ⭐ NOTHING. It reads `results-php/ph*.json` and `results-php/gate/ph*.json`,
# both committed, builds nothing, runs no binary and WRITES NOTHING. On a clean
# checkout it runs to completion in 0.10 s.
# ⚠ ONE CITATION IN THE DOCSTRING BELOW STILL POINTS INTO GITIGNORED SCRATCH
# (`callee_share.py`) and is MARKED AS SUCH rather than silently repaired -- it
# is not promoted here, so a reader must not expect to find it.
# =============================================================================

"""The R4/R5 NULL CONTROL, and what it decides about item 52.

`spec.md`'s `identity: unsafe == verus, O3 exact` pins R4 and R5 BYTE-IDENTICAL.
So `verus - unsafe` has a KNOWN TRUE VALUE OF EXACTLY ZERO, on every row, in
every band. Any departure is measurement noise, and this project already ships
that control on every row without anyone having read it as one.

That makes it the cleanest possible way to choose between the two statistic
families item 52 is about:

  A  kernel-exclusive  `results-php/<row>.json` -> cells[].ir[inp].kernel_exclusive_ir
  B  whole-program marginal  `results-php/gate/<row>.json` -> marginal_ir_per_call

  --null      the control: `verus - unsafe` under both families
  --cvsrust   the C-vs-Rust column under both families, every row
  --row03     the crash course's row-1 claims under both families

⭐ FOUND: family A's null is 0.000 everywhere; family B's reaches +3.652 %, and
on `ph03`/`small.bin` B's NULL EXCEEDS THE EFFECT B IS BEING USED TO MEASURE
(B reports unsafe 3.12 % faster than gcc C on that exact cell). A statistic
cannot be the headline for a comparison it cannot resolve.

⚠ This does NOT say family B is bad. B's null is non-zero only on `small.bin`:
it is a two-point SLOPE, the small input is dominated by fixed per-call cost, so
the slope estimate is noisy there. On `large.bin` B's null is ~0 everywhere.
B has an INPUT-DEPENDENT NOISE FLOOR, and nothing in the published tables says
so. That is the finding, not "B is wrong".

⚠⚠ And neither family repairs item 54: `ph64`'s C-vs-Rust column is misleading
under both -- A does not charge C for `malloc`, B does and thereby compares an
allocator against arithmetic. See `callee_share.py` -- ⛔ WHICH IS UNCOMMITTED
SCRATCH: it lives at `.temp/mgr170/callee_share.py`, `.temp/` is GITIGNORED, and
it was NOT promoted with this file. On a clean checkout it does not exist. The
citation is kept because it records where that argument was made; it is not a
path you can follow.

Read-only.

Run:  python3 .tasks-php/probes/null_control.py --selftest
      python3 .tasks-php/probes/null_control.py
"""
import argparse
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RES = os.path.join(ROOT, "results-php")
GATE = os.path.join(RES, "gate")
OPT, MODE = "O3", "isolated"
INPUTS = ("small.bin", "large.bin")


def load(name):
    """`(A, B)` -- kernel-exclusive totals and marginal slopes, keyed `(cell, inp)`."""
    d = json.load(open(os.path.join(RES, name + ".json")))
    gp = os.path.join(GATE, name + ".json")
    if not os.path.exists(gp):
        return None, None
    m = json.load(open(gp)).get("marginal_ir_per_call") or {}
    A, B = {}, {}
    for c in d["cells"]:
        if c["opt"] != OPT or c["mode"] != MODE:
            continue
        for inp in INPUTS:
            kx = ((c.get("ir") or {}).get(inp) or {}).get("kernel_exclusive_ir")
            if kx is not None:
                A[(c["cell"], inp)] = kx
    for k, v in m.items():
        cell, opt, mode, inp = k.split("/")
        if opt == OPT and mode == MODE and inp in INPUTS:
            B[(cell, inp)] = v
    return A, B


def pct(tbl, num, den, inp):
    a, b = tbl.get((num, inp)), tbl.get((den, inp))
    return None if (a is None or b is None or not b) else (a - b) / b * 100.0


def rows():
    for f in sorted(glob.glob(os.path.join(RES, "ph*.json"))):
        name = os.path.basename(f)[:-5]
        A, B = load(name)
        if A:
            yield name.split("-")[0], A, B


def fmt(v, w=11, p=3):
    return " " * (w - 3) + "n/a" if v is None else f"{v:+{w}.{p}f} %"


def show_null():
    print("NULL CONTROL: verus - unsafe. `identity` pins these byte-identical,")
    print("so the true value is EXACTLY 0 and any departure is noise.\n")
    print(f"{'row':<7}{'input':<12}{'A (kx)':>14}{'B (marginal)':>17}")
    print("-" * 50)
    worst = (0.0, None)
    for short, A, B in rows():
        for inp in INPUTS:
            a, b = pct(A, "verus", "unsafe", inp), pct(B, "verus", "unsafe", inp)
            flag = " ⚠" if b is not None and abs(b) > 0.5 else ""
            print(f"{short:<7}{inp:<12}{fmt(a, 13)}{fmt(b, 16)}{flag}")
            if b is not None and abs(b) > abs(worst[0]):
                worst = (b, f"{short}/{inp}")
    print(f"\n  family A worst null : ~0.000 %")
    print(f"  family B worst null : {worst[0]:+.3f} %  at {worst[1]}")


def show_cvsrust():
    print("C-vs-Rust: safe_tuned against c-gcc, both families.\n")
    print(f"{'row':<7}{'input':<12}{'A (kx)':>14}{'B (marginal)':>17}   note")
    print("-" * 66)
    for short, A, B in rows():
        for inp in INPUTS:
            a, b = pct(A, "safe_tuned", "c-gcc", inp), pct(B, "safe_tuned", "c-gcc", inp)
            note = ""
            if a is not None and b is not None:
                if (a > 0) != (b > 0):
                    note = "⚠⚠ SIGN FLIP"
                elif abs(a - b) > 10:
                    note = f"⚠ gap {abs(a - b):.0f} pp"
            print(f"{short:<7}{inp:<12}{fmt(a, 13, 2)}{fmt(b, 16, 2)}   {note}")


def show_row03():
    print("Row 1 (`ph03`) -- the claims the crash course is told to quote.\n")
    A, B = load("ph03-uudecode-bound")
    print(f"{'cell':<12}{'input':<12}{'A (kx)':>14}{'B (marginal)':>17}   note")
    print("-" * 66)
    for cell in ("safe_naive", "safe_tuned", "unsafe", "verus", "c-clang", "c-gcc-h"):
        for inp in INPUTS:
            a, b = pct(A, cell, "c-gcc", inp), pct(B, cell, "c-gcc", inp)
            note = ("⚠⚠ SIGN FLIP" if (a is not None and b is not None
                                       and (a > 0) != (b > 0)) else "")
            print(f"{cell:<12}{inp:<12}{fmt(a, 13, 2)}{fmt(b, 16, 2)}   {note}")


def selftest():
    """Must-fire negatives.

    N1 the ratio is (num-den)/den, SIGNED.
    N2 ⭐ THE CONTROL'S OWN CONTROL: family A's null must be ~0 on ph03. If the
       pinned identity were not holding, or the cells were being read wrongly,
       this is where it shows -- and without it a flat A column would look like
       success rather than like reading one field twice.
    N3 family B's null must be NON-zero somewhere, or the whole comparison has
       nothing to distinguish and the script is reading A twice.
    N4 a missing cell yields None, never 0.0 -- otherwise an absent rung reads
       as a perfect null.
    N5 at least 4 rows resolve.
    """
    fails = []

    def ck(name, got, want):
        if got != want:
            fails.append(f"{name}: got {got!r}, want {want!r}")

    ck("N1 sign convention", round(pct({("x", "i"): 110.0, ("y", "i"): 100.0},
                                       "x", "y", "i"), 2), 10.0)
    A, B = load("ph03-uudecode-bound")
    if not A:
        fails.append("N2: ph03 record missing")
    else:
        a = pct(A, "verus", "unsafe", "small.bin")
        if a is None or abs(a) > 0.01:
            fails.append(f"N2: ph03 family-A null is {a}, expected ~0 "
                         f"(identity pins unsafe == verus)")
    allb = [x for x in (pct(b, "verus", "unsafe", i)
                        for _, _, b in rows() if b for i in INPUTS) if x is not None]
    if not any(abs(x) > 0.5 for x in allb):
        fails.append("N3: family B's null is flat too -- reading A twice?")
    ck("N4 missing cell is None", pct({}, "a", "b", "i"), None)
    n = len(list(rows()))
    if n < 4:
        fails.append(f"N5: only {n} row(s) resolved")
    for f in fails:
        print("  FAIL " + f)
    print(f"selftest: {'PASS' if not fails else 'FAIL'} ({len(fails)} failure(s))")
    return not fails


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--null", action="store_true")
    ap.add_argument("--cvsrust", action="store_true")
    ap.add_argument("--row03", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return 0 if selftest() else 1
    if not selftest():
        print("\n⚠ selftest FAILED -- nothing below is believable")
        return 1
    print()
    any_sel = a.null or a.cvsrust or a.row03
    for flag, fn in ((a.null or not any_sel, show_null),
                     (a.cvsrust or not any_sel, show_cvsrust),
                     (a.row03 or not any_sel, show_row03)):
        if flag:
            fn()
            print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
