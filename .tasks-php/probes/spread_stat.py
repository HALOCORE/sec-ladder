#!/usr/bin/env python3
# =============================================================================
# spread_stat.py -- THE FIRST OF F74's THREE PROBES, AND THE ONE THAT FOUND THE
# START HERE BOX MIXING TWO STATISTICS
#
# ⛔⛔ WHY IT IS COMMITTED. Written under `.temp/mgr170/`, which is GITIGNORED.
# **F74** (`RECAP_PHP.md:7396`, landed 2026-09-11, commit 26af8e3) names it as
# the first of three probes -- `spread_stat.py` · `callee_share.py` ·
# `null_control.py` -- that settled item 52 on family A. `.memory-php/
# 04-process.md` LAW 11. Promoted by `TASK_PHP_064`, 2026-09-17, commit f4bda71.
#
# ⚠ SIBLING HISTORY, AND IT IS THE REASON THIS FILE EXISTS: `PROMOTE_001`
# promoted `null_control.py` alone out of that sentence of three, on 2026-09-17,
# and nobody noticed the other two for five days. **Check a citing sentence's
# siblings.**
#
# ⭐ WHAT IT STILL REPRODUCES, re-run 2026-09-17 over the **14** gated php rows:
# Q3 -- *which statistic is the START HERE box actually quoting?* -- still gives
# `ph03 -> A1`, `ph16 -> A1`, `ph29 -> A1`, **`ph64 -> B1`**. That is F74's
# central observation, reproduced unchanged 6 days and 8 rows later: the box
# mixed families and was FAITHFUL in doing so, because the rows disagree.
#
# ⛔⛔ AND WHAT NO LONGER HOLDS -- READ THIS BEFORE QUOTING Q1.
# `.temp/mgr170/NOTES.md` §1c concluded ***"Not one row flips sign across all
# five statistics"***, and §1h re-asserted it (*"remains true"*). Over the
# 4 rows gated on 2026-09-11 that was right. Over the 14 gated on 2026-09-17
# this file prints:
#
#       ⚠⚠⚠ SIGN FLIPS on: ph45, ph66
#
# ▶ So item 52 IS a direction question on this corpus and not only a precision
#   one. ⚠ **Nothing published is refuted by that** -- I searched
#   `RECAP_PHP.md` and `.memory-php/` and the *"no row flips sign"* sentence
#   never left `.temp/mgr170/NOTES.md`, so there is no finding to correct. What
#   is refuted is the assumption that a probe's own printed conclusion is a
#   fact rather than a reading of one day's corpus. ⓘ `ph45`'s sign reversal is
#   independently on file as **F87** and `ph66` is simply newer than the note.
#
# RUN IT:  python3 .tasks-php/probes/spread_stat.py --selftest   # 5 negatives
#          python3 .tasks-php/probes/spread_stat.py              # the table
# ⚠ Negatives are INLINE as well as flag-gated: a bare run executes `selftest()`
# first and refuses to print if an arm fails.
#
# ✅ WHAT IT NEEDS THAT IS NOT COMMITTED: NOTHING. `results-php/ph*.json` and
# `results-php/gate/ph*.json` only; builds nothing, runs no binary, WRITES
# NOTHING. 0.2 s on a warm tree, 2026-09-17.
#
# ⛔ WHAT IS STILL OWED: (1) F74 is **UNREVIEWED** (rule 9) and that is the debt.
# (2) `BOX` below is a HAND-TRANSCRIBED copy of four figures from
# `RECAP_PHP.md`'s START HERE box -- a literal that can go stale, which is
# `.memory-php/04-process.md` law 6's class. It is kept because the mismatch is
# the point of Q3 (a wrong transcription shows up as `MATCHES NONE OF THE
# FIVE`), but nothing re-derives it from the box and **it is four rows of a
# fourteen-row corpus**. (3) Its `S2` arm pins `ph16`'s A1 at the published
# `-1.22 %`; no arm pins any other row.
# =============================================================================

"""Item 52: how much does the CHOICE OF STATISTIC move the PHP spread table?

Item 52 records that `ph07`'s `fixed-R4 bound` is published from the MARGINAL
statistic and `ph16`'s from the PER-CALL one, and that on `ph16` they differ by
0.72 pp. ⚠ **So the published bounds are not comparable as published**, which is
what `fixed-R4 bound` exists to prevent.

⚠⚠ AND THE MANAGER IS PROPAGATING IT. `RECAP_PHP.md`'s START HERE box quotes

    SPREAD ph03 +12.19 · ph16 -1.22 · ph29 -6.06 · ph64 +17.08 = 2 POS / 2 NEG

and concludes *"safe-tuned cheaper is 2 of 4, NOT a trend"* -- in the one box
every agent reads first. If those figures mix statistics, that sentence
compares incomparable numbers.

⚠⚠⚠ THE RISK IS DOCUMENTED, NOT HYPOTHETICAL. `harness/report.py` (frozen, and
therefore authoritative) records that the two families **reverse real rung
comparisons on two PAT patterns**: *"p11's `safe_tuned` reads 30% cheaper than
`unsafe` here and 21% dearer on the marginal and the wall clock."* And item 54
already measured that **60 % of `ph64`'s C-rung instructions are in libc
malloc/free** -- a row where most of the work is in CALLEES is exactly the shape
where the two families diverge.

TWO FAMILIES, FIVE STATISTICS -- and item 52 says "three", which is why this
script counts them rather than trusting the number:

  A  KERNEL-EXCLUSIVE `Ir`  (`results-php/<row>.json` -> cells[].ir[input])
       counts instructions INSIDE the kernel symbol only; whatever a rung calls
       out to lands in NO column.  A1 small.bin · A2 large.bin
  B  WHOLE-PROGRAM MARGINAL (`results-php/gate/<row>.json`
       -> marginal_ir_per_call) -- a SLOPE, symbol-independent, charges every
       callee.  B1 small.bin · B2 large.bin · B3 d_ir_d_work

⭐ The box quotes **A1**.

This script does NOT argue which family is right. It recomputes the whole table
under each, consistently, and asks the one question that decides how urgent
item 52 is:

    Does the SIGN of any row change with the statistic?

A sign change makes the "2 positive / 2 negative" split an artefact of mixing.
No sign change makes the choice a precision question rather than a direction
question -- still owed, but not load-bearing for the headline.

⚠ `fixed-R4 bound` = `R3ship - R4ship` = `safe_tuned` vs `unsafe`, O3/isolated,
R4 held fixed BY FIAT. That is the only quantity here. No pair interval, and no
`min(R3 found) - min(R4 found)` -- two upper bounds differenced bound nothing.

Read-only.
"""
import argparse
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RES = os.path.join(ROOT, "results-php")
GATE = os.path.join(RES, "gate")

R3, R4 = "safe_tuned", "unsafe"
OPT, MODE = "O3", "isolated"

#: (label, family) in print order. Family A is kernel-exclusive, B is marginal.
STATS = (("A1 kx/small", "A", "small.bin"),
         ("A2 kx/large", "A", "large.bin"),
         ("B1 mg/small", "B", "small.bin"),
         ("B2 mg/large", "B", "large.bin"),
         ("B3 mg/slope", "B", "d_ir_d_work"))

#: Transcribed from RECAP_PHP.md's START HERE box, so a mismatch is visible.
BOX = {"ph03": +12.19, "ph16": -1.22, "ph29": -6.06, "ph64": +17.08}


def kernel_exclusive(path, cell, inp):
    """Family A: instructions inside the kernel symbol, O3/isolated."""
    d = json.load(open(path))
    for c in d["cells"]:
        if c["cell"] == cell and c["opt"] == OPT and c["mode"] == MODE:
            return (c.get("ir") or {}).get(inp, {}).get("kernel_exclusive_ir")
    return None


def rows():
    out = {}
    for f in sorted(glob.glob(os.path.join(RES, "ph*.json"))):
        name = os.path.basename(f)[:-5]
        short = name.split("-")[0]
        gp = os.path.join(GATE, name + ".json")
        if not os.path.exists(gp):
            continue
        m = json.load(open(gp)).get("marginal_ir_per_call") or {}
        vals = {}
        for label, fam, inp in STATS:
            if fam == "A":
                a, b = kernel_exclusive(f, R3, inp), kernel_exclusive(f, R4, inp)
            else:
                a = m.get(f"{R3}/{OPT}/{MODE}/{inp}")
                b = m.get(f"{R4}/{OPT}/{MODE}/{inp}")
            vals[label] = None if (a is None or b is None or not b) \
                else (a - b) / b * 100.0
        out[short] = vals
    return out


def selftest():
    """Must-fire negatives. Without these the table below is decoration.

    S1 the arithmetic is (R3-R4)/R4, SIGNED. A sign error inverts the entire
       conclusion -- the single most damaging failure available here.
    S2 ph16's A1 must reproduce the PUBLISHED -1.22 %. This is the control that
       proves the family, the band and the cells are the right ones. ⚠ It is
       also the control that ALREADY FIRED once: the first draft of this script
       read family B and got -1.25, which is how the two families were found to
       be different quantities rather than two names for one.
    S3 ph16's A1 and B1 must NOT be equal -- item 52's premise is that the
       statistics disagree. Equality would mean one field is being read twice.
    S4 a missing row yields None, so an absent rung cannot masquerade as 0.0.
    S5 at least 4 rows and at least 5 statistics are actually computed, so a
       silently-empty table cannot print "no sign changes" and look green.
    """
    fails = []

    def ck(name, got, want):
        if got != want:
            fails.append(f"{name}: got {got!r}, want {want!r}")

    ck("S1 sign convention", round((110.0 - 100.0) / 100.0 * 100.0, 2), 10.0)
    r = rows()
    if "ph16" not in r:
        fails.append("S2: ph16 record missing")
    else:
        a1 = r["ph16"]["A1 kx/small"]
        ck("S2 ph16 A1 reproduces the published -1.22 %", round(a1, 2), -1.22)
        b1 = r["ph16"]["B1 mg/small"]
        if b1 is not None and round(b1, 2) == round(a1, 2):
            fails.append("S3: A1 == B1 -- one field is being read twice")
    ck("S4 missing row is None", r.get("__nope__"), None)
    live = [k for k in r if any(v is not None for v in r[k].values())]
    if len(live) < 4:
        fails.append(f"S5: only {len(live)} live row(s), expected >= 4")
    nst = len({lab for k in live for lab, v in r[k].items() if v is not None})
    if nst < 5:
        fails.append(f"S5: only {nst} statistic(s) computed, expected 5")
    for f in fails:
        print("  FAIL " + f)
    print(f"selftest: {'PASS' if not fails else 'FAIL'} ({len(fails)} failure(s))")
    return not fails


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return 0 if selftest() else 1
    if not selftest():
        print("\n⚠ selftest FAILED -- nothing below is believable")
        return 1
    print()

    r = rows()
    print(f"`fixed-R4 bound` = (R3ship - R4ship)/R4ship   [{R3} vs {R4}, "
          f"{OPT}/{MODE}]")
    print("  A = kernel-exclusive (inside the symbol)   "
          "B = whole-program marginal (charges callees)")
    hdr = "".join(f"{lab:>13}" for lab, _, _ in STATS)
    print(f"\n{'row':<7}{hdr}   {'box':>9}")
    print("-" * (7 + 13 * len(STATS) + 12))
    signs, inband = {}, {}
    for short in sorted(r):
        cells = ""
        got = []
        for lab, _, _ in STATS:
            v = r[short][lab]
            cells += "          n/a" if v is None else f"{v:+12.2f} "
            if v is not None:
                got.append(v)
        box = BOX.get(short)
        boxs = f"{box:+9.2f}" if box is not None else "       --"
        print(f"{short:<7}{cells}   {boxs}")
        if got:
            signs[short] = {x > 0 for x in got}
            inband[short] = (min(got), max(got))

    print("\n--- Q1: does the SIGN change with the statistic? ---")
    flipped = sorted(k for k, s in signs.items() if len(s) > 1)
    if flipped:
        print(f"  ⚠⚠⚠ SIGN FLIPS on: {', '.join(flipped)}")
        print("      The box's '2 POS / 2 NEG' split is an ARTEFACT of which")
        print("      statistic each row happens to be quoted in. Item 52 is not")
        print("      a precision question -- it decides the headline.")
    else:
        print("  ✅ NO row changes sign across all five statistics.")
        print("     The choice is a PRECISION question, not a DIRECTION one:")
        print("     item 52 is still owed, but the '2 POS / 2 NEG' split holds.")

    print("\n--- Q2: the span between the cheapest and dearest statistic ---")
    for short in sorted(inband):
        lo, hi = inband[short]
        base = abs(r[short]["A1 kx/small"] or 0) or float("inf")
        print(f"  {short:<7} {lo:+8.2f} .. {hi:+8.2f}   span {hi - lo:7.2f} pp"
              f"   ({(hi - lo) / base * 100:6.0f} % of the box figure)")

    print("\n--- Q3: which statistic is the box actually quoting? ---")
    for short, box in sorted(BOX.items()):
        if short not in r:
            print(f"  {short:<7} ⚠ no record")
            continue
        match = [lab for lab, _, _ in STATS
                 if r[short][lab] is not None
                 and round(r[short][lab], 2) == round(box, 2)]
        flag = "" if match else "   ⚠⚠ MATCHES NONE OF THE FIVE"
        print(f"  {short:<7} box {box:+7.2f}  ->  "
              f"{', '.join(match) if match else '(none)'}{flag}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
