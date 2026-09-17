#!/usr/bin/env python3
# =============================================================================
# callee_share.py -- THE PROBE **F85** AND **F74** BOTH REST ON
#
# ⛔⛔ WHY IT IS COMMITTED. It was written under `.temp/mgr170/`, which is
# GITIGNORED, and it is named as evidence by TWO published findings:
#
#   F74 (RECAP_PHP.md:7396, landed 2026-09-11, commit 26af8e3) -- one of the
#       three probes that settled item 52 in favour of family A.
#   F85 (RECAP_PHP.md:6986, landed 2026-09-12, commit fb49a3e) -- *the
#       programme's central claim*, that the CROSS-LANGUAGE column carries
#       29 of 38 family-A/family-B sign flips. **F85 is UNREVIEWED.**
#
# `.memory-php/04-process.md` LAW 11: a published finding whose only evidence
# is a gitignored probe will not survive a clean checkout. Promoted out of
# scratch by `TASK_PHP_064` on 2026-09-17, repo at commit f4bda71.
#
# ⭐⭐ THE SIBLING LESSON THAT PUT IT HERE. F74 names THREE probes in one
# sentence -- `spread_stat.py`, `callee_share.py`, `null_control.py`. A previous
# promotion (`PROMOTE_001`, 2026-09-17) took `null_control.py` and left the
# other two, and `null_control.py`'s own docstring still points at this file as
# *"UNCOMMITTED SCRATCH"*. That pointer is now stale in the good direction; it
# is left in place rather than edited, because editing it would cost nothing and
# teach nothing, and the record of how the gap survived is worth more.
#
# ⚠⚠⚠ IT CARRIES A POPULATION, AND THE POPULATION HAS MOVED. F85's `38 flips /
# 366 comparisons` was measured on the SIX php rows gated on 2026-09-12. This
# file globs `results-php/ph*.json`, so it prices WHATEVER IS GATED TODAY.
# Re-run by `TASK_PHP_064` on 2026-09-17 over **14 rows**:
#
#       758 comparisons · 141 sign flips · 111 of them cross-language
#
# ▶ So the COUNT `29 of 38` is a 2026-09-12 fact and is NOT what this file
#   prints now, while the RATIO F85 leads with is: 76.3 % then, **78.7 % now**,
#   on a corpus 2.3x larger. ⛔ Quote the count with its date and its row set;
#   quoting `29 of 38` off a fresh run of this file is wrong.
#
# ⚠ AND ONE OF ITS OWN CONCLUSIONS NO LONGER HOLDS AS WRITTEN. `--flips` ends
# with *"RULE: where |Δinside_share| <= 0.02 the two families agree on
# DIRECTION"*. On the 14-row corpus the script itself prints **13 flips with
# Δshare <= 0.02** under the banner `⚠⚠ THESE REFUTE THE MECHANISM`. The
# published trajectory of that one number is **0 -> 6 -> 13**: 0 over the
# 310-comparison sweep the rule was written on, **6** once `ph45` gated (F74
# records that correction in place, `RECAP_PHP.md:7463`), **13** today over 758.
# ▶ The script is honest -- it prints the refutation of its own rule -- but a
# reader must not lift the closing RULE line without the counter-line four lines
# above it. ⓘ This is F86/`flip_exact.py`'s result arriving from the other side:
# the exact flip condition is geometric and no function of the shares alone can
# certify family A.
#
# RUN IT:  python3 .tasks-php/probes/callee_share.py --selftest   # 4 negatives
#          python3 .tasks-php/probes/callee_share.py              # the shares
#          python3 .tasks-php/probes/callee_share.py --flips      # the A/B flips
# ⚠ Its negatives are INLINE as well as flag-gated: every non-selftest arm runs
# `selftest()` FIRST and refuses to print if one fails.
#
# ✅ WHAT IT NEEDS THAT IS NOT COMMITTED: NOTHING. `results-php/ph*.json` and
# `results-php/gate/ph*.json` are both committed; it builds nothing, runs no
# binary and WRITES NOTHING. Measured on a warm tree 2026-09-17: 0.2 s.
#
# ⛔ WHAT IS STILL OWED: (1) **F85 has never been reviewed** and the review is
# the debt, not this promotion. (2) One docstring citation below still points at
# `.temp/mgr170/NOTES.md`, which is gitignored and was NOT promoted -- it is
# marked in place rather than silently repaired, the same call `null_control.py`
# made. (3) Its `C4` negative pins `ph64`'s C-rung share below 0.95 against item
# 54's ~60 %-in-libc figure; that is a check on ONE row and nothing re-derives
# the 60 %.
# =============================================================================

"""Are items 52 and 54 the SAME fact? Measure how much work happens in CALLEES.

CLAIM UNDER TEST (mine, from `.temp/mgr170/NOTES.md` §2 -- ⛔ WHICH IS
UNCOMMITTED SCRATCH: `.temp/` is gitignored and that file was NOT promoted with
this one, so on a clean checkout it does not exist. The citation records where
the claim was made; it is not a path you can follow. -- and asserted before it
was measured, which is what this script exists to repair):

    item 52 (which statistic is "the bound") and item 54 (§B2's O(1)-allocation
    condition) are the same underlying fact seen twice: work that happens in
    CALLEES is INVISIBLE to family A and CHARGED by family B.

If that is right, the A/B gap should be large exactly on the rows and rungs that
call out a lot -- and item 54 has already measured one instance of it, **60 % of
`ph64`'s C-rung instructions in libc `malloc`/`free`**. If it is wrong, the gap
will be flat across rows and the two items are unrelated.

METHOD, and why it is a RATIO rather than a difference:

    A_per_call = kernel_exclusive_ir / n_iters    (inside the symbol only)
    B_per_call = marginal_ir_per_call             (whole-program slope)
    inside_share = A_per_call / B_per_call

`inside_share` near 1.0 means the kernel symbol IS the whole cell, so A and B
must agree and the choice of statistic cannot matter. Well below 1.0 means the
cell's work is mostly in callees, so A is blind to it. ⭐ `1 - inside_share` is
directly comparable to item 54's 60 % figure.

⚠⚠ THE SHARE IS NOT A PERCENTAGE OF A CLEAN WHOLE, and saying so matters.
`marginal_ir_per_call` is a two-point SLOPE and `kernel_exclusive_ir/n_iters` is
an AVERAGE including fixed setup, so their ratio can exceed 1.0 legitimately
(fixed cost inside the symbol inflates the average above the slope). A value
> 1.0 is therefore NOT a bug and NOT evidence of callee work -- it is evidence
that per-call fixed cost dominates. Read the DIRECTION of departure from 1.0,
not the magnitude as if it were a share of instructions. The script prints both
and refuses to call anything > 1.0 a callee share.

Read-only.
"""
import argparse
import glob
import itertools
import json
import os
import statistics
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RES = os.path.join(ROOT, "results-php")
GATE = os.path.join(RES, "gate")

OPT, MODE, INP = "O3", "isolated", "large.bin"   # large: fixed cost amortised
RUNGS = ("c-gcc", "safe_naive", "safe_tuned", "unsafe", "verus")


def row_shares(res_path):
    d = json.load(open(res_path))
    name = os.path.basename(res_path)[:-5]
    gp = os.path.join(GATE, name + ".json")
    if not os.path.exists(gp):
        return None
    m = json.load(open(gp)).get("marginal_ir_per_call") or {}
    n_iters = ((d.get("inputs") or {}).get(INP) or {}).get("n_iters")
    if not n_iters:
        return None
    out = {}
    for c in d["cells"]:
        if c["opt"] != OPT or c["mode"] != MODE or c["cell"] not in RUNGS:
            continue
        kx = ((c.get("ir") or {}).get(INP) or {}).get("kernel_exclusive_ir")
        b = m.get(f"{c['cell']}/{OPT}/{MODE}/{INP}")
        if kx is None or not b:
            continue
        out[c["cell"]] = (kx / n_iters) / b
    return {"name": name, "short": name.split("-")[0],
            "n_iters": n_iters, "shares": out}


def selftest():
    """Must-fire negatives.

    C1 the ratio is A/B and not B/A -- inverted, every conclusion reverses.
    C2 a cell present in the record but absent from the gate map yields no row
       rather than a silent 1.0.
    C3 at least 4 rows and 3 rungs actually resolve, so an empty sweep cannot
       print a flat table and read as "no effect".
    C4 ⭐ THE CLAIM-UNDER-TEST CONTROL. `ph64`'s C rung must come out clearly
       BELOW 1.0, because item 54 independently measured ~60 % of it in libc.
       If it does not, either this method or item 54 is wrong, and the script
       must say so rather than quietly reporting a flat table.
    """
    fails = []

    def ck(name, got, want):
        if got != want:
            fails.append(f"{name}: got {got!r}, want {want!r}")

    ck("C1 ratio orientation", round((50.0 / 10) / (100.0 / 10), 3), 0.5)
    rows = [r for r in (row_shares(f) for f in
                        sorted(glob.glob(os.path.join(RES, "ph*.json")))) if r]
    ck("C2 absent cell is absent",
       any("__nope__" in r["shares"] for r in rows), False)
    if len(rows) < 4:
        fails.append(f"C3: only {len(rows)} row(s) resolved, expected >= 4")
    rungs = {k for r in rows for k in r["shares"]}
    if len(rungs) < 3:
        fails.append(f"C3: only {len(rungs)} rung(s) resolved, expected >= 3")
    ph64 = next((r for r in rows if r["short"] == "ph64"), None)
    if ph64 is None:
        fails.append("C4: ph64 row missing -- the claim-under-test control cannot run")
    else:
        c = ph64["shares"].get("c-gcc")
        if c is None:
            fails.append("C4: ph64 has no c-gcc cell")
        elif c >= 0.95:
            fails.append(f"C4: ph64's C rung inside_share is {c:.3f}, but item 54 "
                         f"measured ~60 % of it in libc -- expected well below 1.0. "
                         f"Either this method or item 54 is wrong.")
    for f in fails:
        print("  FAIL " + f)
    print(f"selftest: {'PASS' if not fails else 'FAIL'} ({len(fails)} failure(s))")
    return not fails


#: Every rung a row may ship, for the `--flips` sweep.
ALL_CELLS = ("c-gcc", "c-clang", "c-gcc-h", "c-clang-h",
             "safe_naive", "safe_tuned", "unsafe", "verus")
FLIP_MIN = 0.2      # pp; below this a "sign flip" is two numbers that are ~0
SHARE_THR = 0.02    # the separation threshold the sweep tests


def flip_sweep():
    """⭐ Do family-A/family-B SIGN FLIPS track callee-share ASYMMETRY?

    The hypothesis: A is blind to callee work, so A and B can only disagree
    about DIRECTION when the two compared cells do DIFFERENT amounts of their
    work in callees. If true, `|Δinside_share|` separates flips from non-flips,
    and it gives an operational rule for which family a comparison may be
    published in. If false -- if any flip has a tiny asymmetry -- the whole
    callee explanation is wrong and item 52 needs a different account.
    """
    out = []
    for f in sorted(glob.glob(os.path.join(RES, "ph*.json"))):
        name = os.path.basename(f)[:-5]
        short = name.split("-")[0]
        d = json.load(open(f))
        gp = os.path.join(GATE, name + ".json")
        if not os.path.exists(gp):
            continue
        m = json.load(open(gp)).get("marginal_ir_per_call") or {}
        for inp in ("small.bin", "large.bin"):
            n = ((d.get("inputs") or {}).get(inp) or {}).get("n_iters")
            if not n:
                continue
            A, B = {}, {}
            for c in d["cells"]:
                if c["opt"] != OPT or c["mode"] != MODE:
                    continue
                kx = ((c.get("ir") or {}).get(inp) or {}).get("kernel_exclusive_ir")
                b = m.get(f"{c['cell']}/{OPT}/{MODE}/{inp}")
                if kx is not None and b:
                    A[c["cell"]], B[c["cell"]] = kx, b
            share = {k: (A[k] / n) / B[k] for k in A}
            for x, y in itertools.combinations(ALL_CELLS, 2):
                if x not in A or y not in A:
                    continue
                a = (A[x] - A[y]) / A[y] * 100
                b = (B[x] - B[y]) / B[y] * 100
                out.append({"row": short, "inp": inp, "x": x, "y": y,
                            "a": a, "b": b,
                            "asym": abs(share[x] - share[y]),
                            "flip": (a > 0) != (b > 0)
                                    and max(abs(a), abs(b)) > FLIP_MIN})
    return out


def show_flips():
    sw = flip_sweep()
    fl = [r for r in sw if r["flip"]]
    nf = [r for r in sw if not r["flip"]]
    print(f"{len(sw)} (row x cell-pair x input) comparisons at {OPT}/{MODE}")
    print(f"{len(fl)} SIGN FLIPS between family A and family B\n")
    print(f"{'row':<7}{'input':<11}{'comparison':<28}{'A':>10}{'B':>10}{'Δshare':>9}")
    print("-" * 75)
    for r in fl:
        print(f"{r['row']:<7}{r['inp']:<11}{r['x'] + ' vs ' + r['y']:<28}"
              f"{r['a']:+9.2f}%{r['b']:+9.2f}%{r['asym']:>9.3f}")

    print(f"\n--- does |Δinside_share| separate flips from non-flips? ---")
    print(f"{'group':<13}{'n':>5}{'median Δshare':>16}{'median |A-B| pp':>18}")
    for lbl, g in (("FLIPPED", fl), ("not flipped", nf)):
        if not g:
            continue
        print(f"{lbl:<13}{len(g):>5}"
              f"{statistics.median(r['asym'] for r in g):>16.3f}"
              f"{statistics.median(abs(r['a'] - r['b']) for r in g):>18.2f}")

    below = [r for r in fl if r["asym"] <= SHARE_THR]
    print(f"\n  flips with Δshare <= {SHARE_THR}: {len(below)}"
          f"   {'⚠⚠ THESE REFUTE THE MECHANISM' if below else '✅ none'}")
    print(f"  non-flips with Δshare > {SHARE_THR}: "
          f"{sum(1 for r in nf if r['asym'] > SHARE_THR)}"
          f"   -- so asymmetry is NECESSARY, not SUFFICIENT")
    print(f"\n  ▶ RULE: where |Δinside_share| <= {SHARE_THR} the two families "
          f"agree on DIRECTION.\n    Where they do not, A and B measure "
          f"different things and BOTH must be published.")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--flips", action="store_true",
                    help="sweep every rung pair for family-A/B sign flips")
    a = ap.parse_args()
    if a.selftest:
        return 0 if selftest() else 1
    if a.flips:
        if not selftest():
            print("\n⚠ selftest FAILED -- nothing below is believable")
            return 1
        print()
        show_flips()
        return 0
    if not selftest():
        print("\n⚠ selftest FAILED -- nothing below is believable")
        return 1
    print()

    rows = [r for r in (row_shares(f) for f in
                        sorted(glob.glob(os.path.join(RES, "ph*.json")))) if r]
    print(f"inside_share = (kernel_exclusive_ir / n_iters) / marginal_ir_per_call")
    print(f"  band {OPT}/{MODE}/{INP};  1.00 = the symbol IS the cell;  "
          f"below 1.00 = work in CALLEES")
    hdr = "".join(f"{r:>12}" for r in RUNGS)
    print(f"\n{'row':<7}{hdr}")
    print("-" * (7 + 12 * len(RUNGS)))
    for r in sorted(rows, key=lambda x: x["short"]):
        line = ""
        for rung in RUNGS:
            v = r["shares"].get(rung)
            line += "         n/a" if v is None else f"{v:11.3f} "
        print(f"{r['short']:<7}{line}")

    print("\n--- Q: is the A/B gap CONCENTRATED, or flat? ---")
    for r in sorted(rows, key=lambda x: x["short"]):
        vs = [v for v in r["shares"].values() if v is not None]
        if not vs:
            continue
        lo, hi = min(vs), max(vs)
        below = [k for k, v in r["shares"].items() if v is not None and v < 0.95]
        note = ("  ⚠ CALLEE-HEAVY: " + ", ".join(sorted(below))) if below else ""
        print(f"  {r['short']:<7} {lo:.3f} .. {hi:.3f}{note}")

    print("\n⚠ Values > 1.00 are NOT callee shares -- an AVERAGE (with fixed")
    print("  per-call cost) over a SLOPE (without it) exceeds 1 legitimately.")
    print("  Only departures BELOW 1.00 are evidence of work in callees.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
