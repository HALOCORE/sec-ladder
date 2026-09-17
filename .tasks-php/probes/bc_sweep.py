#!/usr/bin/env python3
# =============================================================================
# bc_sweep.py -- THE MEASUREMENT BEHIND F84
#
# ⛔⛔ WHY THIS FILE IS COMMITTED, AND IT IS NOT TIDINESS. It was written under
# `.temp/mgr172/`, which is GITIGNORED, and **F84 is PUBLISHED** --
# `RECAP_PHP.md`: *"family B can MISS real work as well as invent it -- ⛔ my
# `-1.00` mechanism REFUTED by the review: it is one instruction per call in
# `main`"*. ▶ A PUBLISHED FINDING WHOSE ONLY EVIDENCE IS A GITIGNORED PROBE IS A
# FINDING THAT WILL NOT SURVIVE A CLEAN CHECKOUT: `.memory-php/04-process.md`
# LAW 11.
#
# RUN IT:  python3 .tasks-php/probes/bc_sweep.py --selftest   # the negatives
#          python3 .tasks-php/probes/bc_sweep.py              # the 12-cell table
#
# ⛔⛔ WHAT IT NEEDS THAT IS *NOT* COMMITTED, stated rather than discovered, and
# UNLIKE ITS SIBLINGS THE ANSWER HERE IS NOT "NOTHING":
#   1. `.temp/mgr172/cg/<row>.{unsafe,verus}.{small,large}.out` -- 24 cached
#      callgrind profiles. GITIGNORED, and that is THE RULE (CLAUDE.md
#      constraint 6, *keep the generator, delete the artefact*). ▶ THE GENERATOR
#      IS `.tasks-php/probes/sweep_cg.sh`, PROMOTED IN THE SAME PASS AS THIS
#      FILE -- promoting a probe and leaving the script that rebuilds its input
#      in deletable scratch would not survive a clean checkout either.
#   2. `.temp/php-root/.temp/build/<row>/{unsafe,verus}-O3-isolated` -- the built
#      binaries, GITIGNORED. Rebuild with
#      `harness-php/gate.py --tool build <row> --all`.
# ▶ So on a CLEAN CHECKOUT THIS SCRIPT CANNOT PRODUCE F84's TABLE, and the
# honest behaviour is to SAY SO. See `missing_inputs` / `report_not_run` below:
# it reports *"the check could not run, which is itself a result to report"* and
# exits 0 WITHOUT CHECKING ANYTHING. ⚠ That rc=0 IS NOT A PASS, which is why
# this file is filed `kind="tool"` in `.tasks-php/checkers.py` and deliberately
# kept OUT of the routine sweep.
#
# WHAT IT FOUND (F84), and note that it REFINES a finding published off two
# rows: F83's *"B is measuring real work"* holds on 6 of these 12 cells and
# FAILS ON 6 -- in BOTH DIRECTIONS, which no two-row sample could have shown.
# ⛔ THE DOCSTRING BELOW SAID `7 AND 5` AND THE SCRIPT'S OWN `report()` HAS
# ALWAYS PRINTED `6 of 12`; corrected at promotion, with the reason, in place.
# ⭐ `ph29/large` reads C `+2.383`/call against B `+0.000`: B reports a clean
# null over a real call-tree difference, so its error is not one-directional as
# every prior treatment (F74's included) assumed. ⭐⭐ And `ph00` reads B
# `-1.000` on both inputs while C reads `0.000` on both, which puts a whole
# class of `check.py`'s unexplained PAT null table (*"34 cells at exactly
# -1.00"*) in the SLOPE rather than in the program.
# =============================================================================

"""FAMILY B against FAMILY C on every PHP row's R4/R5 pair — 12 cells.

⚠⚠ THIS REFINES F83, WHICH I PUBLISHED OFF TWO ROWS. F83's headline is *"B is
measuring real work"*, and on `ph03` it is: B `+266.000` against C `+265.924`.
Across 12 cells that statement is TRUE ON 6 AND FALSE ON 6 — and the 6 fail in
BOTH DIRECTIONS, which no two-row sample could have shown.

⛔⛔ THIS LINE READ *"TRUE ON 7 AND FALSE ON 5"* UNTIL THE PROMOTION OF
2026-09-17, AND THE SCRIPT'S OWN `report()` DISAGREED WITH IT ON EVERY RUN. The
printed summary reads `B and C agree (< 5 %) : 6 of 12`, and
`.temp/mgr172/NOTES.md` §9 — the round's own record — says *"TRUE ON 6 AND FALSE
ON 6"*. ▶ The disputed cell is `ph64/small` at **10.05 %**, which the prose below
counts among *"`ph03`, `ph16` and `ph64` agree closely"* while the `< 5 %` rule
the script prints counts it as a disagreement. ⚠ NOTHING MEASURED CHANGED: the
table is identical, only a count in prose was wrong. ⭐ And note which arm did
not catch it — `N4` asserts merely that AT LEAST ONE cell disagrees, so the
split was never derived from the data the way `checkers.py`'s `N12` derives an
arm count. That is law 6's class inside a probe's own docstring.

    family A   kernel EXCLUSIVE Ir    inside the kernel symbol only
    family C   kernel INCLUSIVE Ir    the kernel's whole CALL TREE, ONE run
    family B   marginal_ir_per_call   whole program, a SLOPE, TWO runs differenced

The decomposition the numbers force:

    B  =  C  +  work OUTSIDE the kernel's call tree  +  slope-method effects

⭐⭐ THREE RESULTS, none of which the two-row version could reach:

1. **THE UBIQUITOUS `-1.00` IS A SLOPE ARTEFACT.** `harness/check.py`'s own PAT
   null table records *"1.00 <= |null| < 2 in 35 cells (34 of them exactly
   -1.00)"* and offers no mechanism. Here `ph00` reads **B `-1.000` on both
   inputs while C reads `0.000` on both.** A whole class of that table is the
   slope, not the program.

2. ⚠⚠ **B CAN MISS REAL WORK, NOT ONLY INVENT IT.** `ph29/large`: **C
   `+2.383`/call and B `+0.000`.** B reports a clean null over a real call-tree
   difference. Every prior treatment of B — F74's included — assumed its error
   was one-directional.

3. **THE DISAGREEMENT IS NOT CONFINED TO ONE ODD ROW.** `ph29/small` B `+8.830`
   against C `+0.061` (**99.31 %** of the larger); `ph07/small` B `+37.340`
   against C `+17.624` (**52.80 %**). `ph03` and `ph16` agree closely, and so
   does `ph64/large` (1.79 %) — ⛔ but NOT `ph64/small`, which is **10.05 %** and
   is a disagreement under the `< 5 %` rule this script prints. This sentence
   read *"`ph03`, `ph16` and `ph64` agree closely"* and that is the cell the
   `7-and-5` count above was built on.

⚠ WHAT C IS AND IS NOT. C is not "the truth" — it is the kernel's CALL TREE, and
that is the right unit for *"what does one call cost"* only because `main` here
is the harness rather than the program. Where B and C differ, the difference is
work in `main` and the driver, plus the slope's own effects; C excludes both by
construction and B charges both.

⚠⚠ AND C DOES NOT FIX ATTRIBUTION — F83 retracts that claim inside itself. On
`ph03` the two kernels are BYTE-IDENTICAL (`md5_fn`
338505795ee18db952aafcdaec522df4) and C still reads `+265.924`, because the
allocator work really is in the call tree. Attribution is a property of the
COMPARISON, not of the column.

⛔ `ph45` IS EXCLUDED. `TASK_PHP_037` is rebuilding it, so its binaries could
move mid-sweep. Re-add it after that task lands: `sweep_cg.sh` and this script
both key off the row list below.

Run:  python3 .tasks-php/probes/bc_sweep.py --selftest
      python3 .tasks-php/probes/bc_sweep.py
Profiles come from `.tasks-php/probes/sweep_cg.sh` (it was `.temp/mgr172/
sweep_cg.sh` when this line was written and is promoted alongside this file).
They are re-derivable; they are artefacts, these scripts are the evidence —
`CLAUDE.md` constraint 6. ⛔ When they are ABSENT this script reports that it
could not run and exits 0 without checking anything; see the header.
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CGA = os.path.expanduser("~/tools/valgrind/bin/callgrind_annotate")
CGDIR = os.path.join(ROOT, ".temp/mgr172/cg")
ROW = re.compile(r"^\s*([\d,]+)\s+\(?[\d.]*%?\)?\s*(.*)$")

ROWS = [("ph00", "ph00-smoke"), ("ph03", "ph03-uudecode-bound"),
        ("ph07", "ph07-strcut-cursor"), ("ph16", "ph16-fdset-index"),
        ("ph29", "ph29-recvfrom-alloc"), ("ph64", "ph64-callback-frees-cursor")]
INPUTS = ("small", "large")
NULL_LEVELS = ("exact", "multiset")


# ---------------------------------------------------------------------------
# ⛔⛔ THE NOT-COMMITTED-INPUTS GUARD. READ WHAT IT IS FOR BEFORE "FIXING" IT.
#
# ⚠ THE GITIGNORED CACHE IS NOT THE DEFECT -- IT IS THE RULE. `CLAUDE.md`
# constraint 6 is *keep the generator, delete the artefact*: a callgrind profile
# and a build tree are artefacts, `probes/sweep_cg.sh` and `harness-php/gate.py
# --tool build` are their generators. ▶ THE DEFECT WAS THAT THIS SCRIPT
# **CRASHED** WHEN THEY WERE ABSENT INSTEAD OF SAYING SO. Measured 2026-09-17 by
# moving `CGDIR` aside: `--selftest` died with `KeyError: 'small'` at N7, having
# first printed FAIL on five arms that had nothing to read -- ⛔⛔ AND THAT IS
# THE WORSE HALF: five arms REPORTED FAILURE over an empty collection, which
# says *"F84 is refuted"* when the truth is *"the profiles are gone"*. A missing
# input is not a refutation.
#
# ⭐ THE PRECEDENT IS `.tasks-php/width.py`'s `X3`: when its cross-session
# profiles are absent it reports *"the check could not run, which is itself a
# result to report"*. This does the same.
# ⛔ AND THE rc IS 0 BECAUSE NOTHING WAS CHECKED, NOT BECAUSE ANYTHING PASSED.
# The banner says so in capitals, and this file is filed `kind="tool"` in
# `.tasks-php/checkers.py` and kept OUT of the routine sweep precisely so a
# green NOT-RUN line can never be counted as a checker passing (F135's class).
#
# ⚠ THE SET IS DELIBERATELY WIDER THAN `CGDIR`: the BUILD TREES are gitignored
# too, and `fresh()` raises on an absent binary just as surely as N7 raised on
# an absent profile. One list covers both.
# ---------------------------------------------------------------------------
def missing_inputs():
    """Every path this script READS that is NOT committed, and is absent.

    Pure over the filesystem; returns repo-relative paths, sorted, no side
    effects. Empty list == everything needed is present.
    """
    miss = []
    for short, _slug in ROWS:
        for cell in ("unsafe", "verus"):
            b = os.path.join(ROOT, ".temp/php-root/.temp/build",
                             short, f"{cell}-O3-isolated")
            if not os.path.exists(b):
                miss.append(os.path.relpath(b, ROOT))
            for inp in INPUTS:
                p = os.path.join(CGDIR, f"{short}.{cell}.{inp}.out")
                if not os.path.exists(p):
                    miss.append(os.path.relpath(p, ROOT))
    return sorted(set(miss))


def report_not_run(miss):
    """⛔ NOT A PASS. Print what is absent and why that is itself a result."""
    print("=" * 92)
    print("⛔⛔ NOT RUN -- NO VERDICT WAS REACHED. THIS IS NOT A PASS.")
    print("=" * 92)
    print(f"  {len(miss)} input(s) this script reads are ABSENT. Every one of")
    print("  them is GITIGNORED and RE-DERIVABLE, so their absence is the")
    print("  expected state of a clean checkout and not a fault -- but it means")
    print("  THE CHECK COULD NOT RUN, WHICH IS ITSELF A RESULT TO REPORT")
    print("  (the rule .tasks-php/width.py's X3 already follows).")
    print()
    for p in miss:
        print(f"    missing  {p}")
    print()
    print("  REBUILD THEM (none of this is committed, by design):")
    print("    sh .tasks-php/probes/sweep_cg.sh          -- the 24 profiles")
    print("    python3 harness-php/gate.py --tool build <row> --all  -- binaries")
    print()
    print("  ⚠ F84's published table is NOT reproduced by this run and must not")
    print("    be quoted from it.")
    return 0


def needle(path, inclusive, name="kernel"):
    out = subprocess.run(
        [CGA, "--threshold=100", f"--inclusive={'yes' if inclusive else 'no'}", path],
        capture_output=True, text=True).stdout
    tot, hit = 0, False
    for line in out.splitlines():
        m = ROW.match(line)
        if not m:
            continue
        rest = m.group(2)
        if ":" not in rest:
            continue
        f = rest.split(":", 1)[1].split(" [")[0].strip()
        if re.search(r"(?:^|::)" + name + r"(?:$|[^A-Za-z0-9_])", f):
            tot += int(m.group(1).replace(",", ""))
            hit = True
    return tot if hit else None


def fresh(short, slug):
    """⚠ A STALE BINARY MAKES EVERY NUMBER BELOW A MEASUREMENT OF ANOTHER
    PROGRAM. `.temp/build/` is gitignored scratch that outlives sessions."""
    sys.path.insert(0, os.path.join(ROOT, "harness"))
    import asm
    m = json.load(open(os.path.join(ROOT, f"results-php/{slug}.json")))
    for cell in ("unsafe", "verus"):
        want = [c["static"]["md5_fn"] for c in m["cells"]
                if c["cell"] == cell and c["opt"] == "O3" and c["mode"] == "isolated"]
        got = asm.kernel(os.path.join(
            ROOT, f".temp/php-root/.temp/build/{short}/{cell}-O3-isolated")).md5_fn
        if not want or got != want[0]:
            return False
    return True


def level(gate):
    for e in gate.get("identity") or []:
        p = str(e.get("pair", ""))
        if e.get("opt") == "O3" and "unsafe" in p and "verus" in p:
            return e.get("level")
    return "?"


def collect():
    rows = []
    for short, slug in ROWS:
        m = json.load(open(os.path.join(ROOT, f"results-php/{slug}.json")))
        g = json.load(open(os.path.join(ROOT, f"results-php/gate/{slug}.json")))
        ok = fresh(short, slug)
        lv = level(g)
        for inp in INPUTS:
            k = inp + ".bin"
            if k not in m.get("inputs", {}):
                continue
            pu = os.path.join(CGDIR, f"{short}.unsafe.{inp}.out")
            pv = os.path.join(CGDIR, f"{short}.verus.{inp}.out")
            if not (os.path.exists(pu) and os.path.exists(pv)):
                continue
            n = m["inputs"][k]["n_iters"]
            A = (needle(pv, False) - needle(pu, False)) / n
            C = (needle(pv, True) - needle(pu, True)) / n
            bu = g["marginal_ir_per_call"].get(f"unsafe/O3/isolated/{k}")
            bv = g["marginal_ir_per_call"].get(f"verus/O3/isolated/{k}")
            if bu is None:
                continue
            rows.append({"row": short, "inp": inp, "level": lv, "fresh": ok,
                         "A": A, "C": C, "B": bv - bu, "n": n})
    return rows


def report(rows):
    print("=" * 92)
    print("R4/R5 pair · O3/isolated · per call.   ph45 EXCLUDED (being rebuilt)")
    print("=" * 92)
    print(f"{'row':6s} {'inp':6s} {'lvl':7s} {'fresh':6s} {'A':>9s} {'C':>11s} "
          f"{'B':>11s} {'|B-C|':>9s} {'disagree':>9s}")
    agree, over, under = [], [], []
    for r in rows:
        den = max(abs(r["B"]), abs(r["C"]))
        pct = 100.0 * abs(r["B"] - r["C"]) / den if den > 1e-9 else 0.0
        print(f"{r['row']:6s} {r['inp']:6s} {r['level']:7s} "
              f"{'ok' if r['fresh'] else '*STALE*':6s} "
              f"{r['A']:+9.3f} {r['C']:+11.3f} {r['B']:+11.3f} "
              f"{abs(r['B'] - r['C']):9.3f} {pct:8.2f}%")
        if pct < 5.0:
            agree.append(r)
        elif abs(r["B"]) > abs(r["C"]):
            over.append(r)
        else:
            under.append(r)
    print()
    print(f"  B and C agree (< 5 %)                 : {len(agree):2d} of {len(rows)}")
    print(f"  B LARGER than C  (B charges extra)    : {len(over):2d}  "
          + " . ".join(f"{r['row']}/{r['inp']}" for r in over))
    print(f"  ⚠⚠ C LARGER than B (B MISSES work)    : {len(under):2d}  "
          + " . ".join(f"{r['row']}/{r['inp']}" for r in under))
    print()

    # family A on the true nulls -- F82's claim, re-derived here off a different
    # code path than F82 used, as a cross-check rather than a repeat.
    nulls = [r for r in rows if r["level"] in NULL_LEVELS]
    print(f"  family A over the {len(nulls)} true-null cells: "
          f"max |A| = {max(abs(r['A']) for r in nulls):.6f}")
    nonnull = [r for r in rows if r["level"] not in NULL_LEVELS]
    if nonnull:
        print(f"  family A over the {len(nonnull)} others: "
              + " . ".join(f"{r['row']}/{r['inp']} {r['A']:+.3f}" for r in nonnull))

    # the -1.00 class
    ones = [r for r in rows if abs(abs(r["B"]) - 1.0) < 1e-9]
    if ones:
        print()
        print("  ⭐ THE `-1.00` CLASS -- `check.py` records 34 PAT cells at exactly")
        print("     -1.00 and gives no mechanism. Here:")
        for r in ones:
            print(f"       {r['row']}/{r['inp']}: B {r['B']:+.3f} but C {r['C']:+.3f} "
                  f"-> the -1.00 is the SLOPE, not the program")
    return agree, over, under


def selftest():
    fails = []

    def check(tag, cond, msg):
        print(f"  {'PASS' if cond else 'FAIL'}  {tag}: {msg}")
        if not cond:
            fails.append(tag)

    # ⛔ FIRST, BEFORE ANY ARM: every arm below reads a gitignored profile or a
    # gitignored binary. With them absent the arms do not FAIL, they report
    # failure over an EMPTY COLLECTION -- see `missing_inputs`'s comment block.
    miss = missing_inputs()
    if miss:
        return report_not_run(miss)

    print("SELFTEST -- must-fire negatives")
    rows = collect()

    check("N1", len(rows) == 12, f"12 cells collected, got {len(rows)}")

    check("N2", all(r["fresh"] for r in rows),
          "every binary matches its published record's md5_fn -- a stale one "
          "would make these numbers a measurement of a different program")

    # N3 the inclusive flag must change the answer somewhere, or C is silently A.
    diff = [r for r in rows if abs(r["C"] - r["A"]) > 1e-9]
    check("N3", len(diff) >= 3,
          f"C differs from A on {len(diff)} cells -- if this were 0, "
          f"`--inclusive=yes` is being ignored and C is A under another name")

    # N4 ⚠⚠ THE F52 CONTROL, AND IT IS THE WHOLE POINT OF THIS SCRIPT.
    #    F83 was published off ph03, where B and C agree to 0.03 %. If every
    #    cell agreed, this sweep would be a repeat rather than a test. Assert
    #    that the tree supplies DISAGREEMENT -- otherwise the refinement below
    #    is unfalsifiable and must not be published.
    dis = [r for r in rows
           if max(abs(r["B"]), abs(r["C"])) > 1e-9
           and 100.0 * abs(r["B"] - r["C"]) / max(abs(r["B"]), abs(r["C"])) >= 5.0]
    check("N4", len(dis) >= 1,
          f"{len(dis)} of {len(rows)} cells DISAGREE by >= 5 % -- so the sweep "
          f"could have refuted F83's generalisation and did not merely echo it")

    # N5 and the disagreement must run BOTH ways, which is result 2. A
    #    one-directional error is a bias with a sign; a two-directional one is
    #    not correctable by any constant.
    under = [r for r in dis if abs(r["C"]) > abs(r["B"])]
    over = [r for r in dis if abs(r["B"]) > abs(r["C"])]
    check("N5", under and over,
          f"disagreements run BOTH ways -- {len(over)} where B is larger, "
          f"{len(under)} where C is larger; B does not merely over-charge")

    # N6 family A must still read 0 on every true null. This is F82's result
    #    re-derived through a DIFFERENT code path (callgrind profiles here,
    #    the measurement record there). Agreement is the cross-check.
    nulls = [r for r in rows if r["level"] in NULL_LEVELS]
    check("N6", nulls and max(abs(r["A"]) for r in nulls) < 1e-9,
          f"family A is exactly 0 on all {len(nulls)} true-null cells, "
          f"re-derived off the profiles rather than off results-php/")

    # N7 ph03 must still show the agreement F83 was built on. If this fails,
    #    F83's own headline has moved and the finding needs revisiting, not
    #    refining.
    p3 = {r["inp"]: r for r in rows if r["row"] == "ph03"}
    ok = (abs(p3["small"]["B"] - 266.0) < 1e-6
          and abs(p3["small"]["C"] - 265.924) < 0.01)
    check("N7", ok,
          f"ph03/small still reads B {p3['small']['B']:+.3f} and "
          f"C {p3['small']['C']:+.3f} -- F83's headline is reproduced here")

    print()
    print("SELFTEST " + ("PASS" if not fails else f"FAIL {fails}"))
    return 1 if fails else 0


def main():
    if "--selftest" in sys.argv:
        return selftest()
    miss = missing_inputs()
    if miss:
        return report_not_run(miss)
    report(collect())
    return 0


if __name__ == "__main__":
    sys.exit(main())
