#!/usr/bin/env python3
"""WHAT DOES A ROW ACTUALLY COST? -- and the 6.2 figure is the wrong number.

⚠⚠ WHY THIS EXISTS. `RECAP_PHP.md`'s "What is true now" says, in text I wrote
last session:

    "≈ 6.2 tasks per built row at n = 6, against `PLAN_PHP.md` §8's PAT-measured
     ~3 -- so the php side costs TWICE what the plan assumed ... The ratio has
     gone 3.3 -> 3.5 -> 6.2; it is RISING."

That is `total tasks / built rows`. ⛔ It charges Phase 0, the mining wave and
the whole catalogue construction -- all paid ONCE, for the whole programme -- to
six rows. It is the right number for "what has this programme cost so far" and
the WRONG number for "what will row 7 cost", which is the question it is quoted
to answer (the 40-row floor, `QUOTA_001.md`).

⚠⚠ AND "RISING" IS A DENOMINATOR ARTEFACT. `total/rows` rises whenever one-time
tasks accumulate while rows lag -- it would rise even if every row cost exactly
3. ▶ A trend claim needs the PER-ROW series, not the running mean.

WHAT THIS DOES. Classifies every `.tasks-php/TASK_PHP_NNN.md` as
  ONCE  -- infrastructure / corpus-wide work, paid once for the programme
  ROW   -- attributable to a specific built row (split when a task covers more
           than one, e.g. `_028` discharges the spellings debt on THREE rows)
  METH  -- the statistic-methodology thread, paid once and amortised
and reports the marginal cost per row, the per-row series, and -- because the
classification is JUDGEMENT AND NOT A MEASUREMENT -- a SENSITIVITY ANALYSIS over
three progressively more pessimistic readings.

⚠ THE CLASSIFICATION IS THE ARGUABLE PART AND IT IS WRITTEN OUT IN FULL BELOW SO
IT CAN BE ARGUED WITH. Nothing here is hidden in a heuristic.

DECLARED EXPECTATIONS, BEFORE RUNNING:
  E1 the marginal cost is well under 6.2 -- probably near 3, i.e. near
     `PLAN_PHP.md` §8's PAT figure, which would mean the plan was RIGHT and my
     published sentence is wrong.
  E2 the per-row series is NOT monotonically rising.
  E3 ⚠ the most expensive row is `ph07`, because it is the only row that was
     REBUILT (_015 _016 _017 _018 _022 _024). If the most expensive row is one
     of the recent ones, E1/E2 may be right by luck and the trend claim fails.
  E4 the conclusion survives all three classifications. If it does not, the
     honest output is "the figure depends on a judgement call" and NOT a
     replacement number.

⭐⭐ COMMITTED HERE BECAUSE THE CLASSIFICATION *IS* THE ARGUMENT. A reader cannot
audit "3.0 tasks per row" without seeing which tasks were called one-time -- so
putting the number in a document and the table in gitignored `.temp/` would be
open item 65's defect exactly. Same convention as `quota.py` and `fixsurvey.py`.
⚠ `PROTOCOL_PHP.md` §H binds it: `--selftest` has 8 must-fire negatives.

Run:  python3 .tasks-php/task_cost.py --selftest
      python3 .tasks-php/task_cost.py
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ROWS = ["ph03", "ph07", "ph16", "ph29", "ph64", "ph45"]   # in BUILD order

# ---------------------------------------------------------------------------
# THE CLASSIFICATION. `ONCE` = paid once for the programme. A dict = the row
# shares this task's cost in those weights. ⚠ Every claim below is checkable
# against the task file's own title line.
# ---------------------------------------------------------------------------
CLASS = {
    # Phase 0 and its four review/land cycles -- infrastructure, paid once.
    "002": "ONCE", "003": "ONCE", "004": "ONCE", "005": "ONCE",
    "006": "ONCE", "007": "ONCE", "008": "ONCE", "009": "ONCE", "010": "ONCE",
    # The mining wave and the catalogue -- corpus-wide, paid once.
    "001": "ONCE", "011": "ONCE", "012": "ONCE",
    "019": "ONCE", "020": "ONCE", "021": "ONCE", "023": "ONCE",
    # Corpus-wide METHOD that serves every future row, not one row.
    "026": "ONCE",          # is a fix commit a CENSUS of its defect's siblings?
    "029": "ONCE",          # R1h hunt for ph73/ph21 -- NEITHER was built
    "030": "ONCE",          # the pre-image screen
    # Row work.
    "013": {"ph03": 1.0},                    # build ph03
    "014": {"ph03": 1.0},                    # review ph03
    "015": {"ph03": 0.5, "ph07": 0.5},       # "fix the template, then build ph07"
    "016": {"ph07": 1.0},
    "017": {"ph07": 1.0},
    "018": {"ph07": 1.0},
    "022": {"ph07": 1.0},
    "024": {"ph07": 1.0},
    "025": {"ph16": 1.0},
    "027": {"ph29": 1.0},
    "028": {"ph03": 1 / 3, "ph16": 1 / 3, "ph29": 1 / 3},   # spellings, 3 rows
    "031": {"ph64": 1.0},                    # settle R1h + prepare ph64
    "032": {"ph64": 1.0},                    # BUILD ph64
    "033": {"ph29": 1.0},
    "034": {"ph45": 1.0},                    # R1h hunt + build brief for ph45
    "035": {"ph29": 1.0},
    "036": {"ph45": 1.0},                    # BUILD ph45
    "037": {"ph45": 1.0},                    # search ph45's R4 endpoint
    # The statistic-methodology thread.
    "038": "METH", "039": "METH",
    # ⚠ PENDING -- attributable to a row that is NOT YET BUILT. It belongs in
    #    neither `ONCE` nor the numerator, because the numerator is row cost
    #    over BUILT rows. ⭐ But it must be REPORTED, not hidden: a growing
    #    PENDING pile makes the marginal figure understate. `N8` bounds it.
    "040": "PENDING",          # R1h hunt + build brief for row 7 (ph52/ph53)
    "041": "PENDING",          # BUILD row 7 = ph53
}

# ⚠ THE SENSITIVITY LADDER. Each step moves tasks OUT of `ONCE` and charges them
# to the rows, which can only make the marginal cost WORSE. If the conclusion
# survives the worst reading it does not depend on my classification.
PESSIMISM = [
    ("as classified", []),
    ("+ the three corpus-wide METHOD tasks charged to rows",
     ["026", "029", "030"]),
    ("+ the catalogue construction charged to rows too",
     ["026", "029", "030", "019", "020", "021", "023"]),
]


def task_ids():
    out = []
    for p in sorted(glob.glob(os.path.join(ROOT, ".tasks-php/TASK_PHP_*.md"))):
        b = os.path.basename(p)
        if "REPORT" in b:
            continue
        m = re.match(r"TASK_PHP_(\d+)\.md$", b)
        if m:
            out.append(m.group(1))
    return out


def title(tid):
    p = os.path.join(ROOT, f".tasks-php/TASK_PHP_{tid}.md")
    with open(p, errors="replace") as f:
        return f.readline().strip()


def spread(extra_rows):
    """row -> task-equivalents charged to it, under one pessimism step.

    `extra_rows` are ids moved out of ONCE and spread EQUALLY over all built
    rows (they are corpus-wide, so no row owns them)."""
    per = {r: 0.0 for r in ROWS}
    once = meth = pend = 0.0
    for tid in task_ids():
        c = CLASS.get(tid)
        if c is None:
            continue
        if tid in extra_rows:
            for r in ROWS:
                per[r] += 1.0 / len(ROWS)
        elif c == "ONCE":
            once += 1
        elif c == "METH":
            meth += 1
        elif c == "PENDING":
            pend += 1
        else:
            for r, w in c.items():
                per[r] += w
    return per, once, meth, pend


def report():
    ids = task_ids()
    print("=" * 96)
    print("WHAT A ROW COSTS — marginal, not total")
    print("=" * 96)
    per, once, meth, pend = spread([])
    tot = len(ids)
    rowsum = sum(per.values())
    print(f"  task files                          {tot}")
    print(f"  ONCE  (infrastructure + corpus)     {once:.0f}")
    print(f"  METH  (the statistic thread)        {meth:.0f}")
    print(f"  ⚠ PEND (row 7, NOT YET BUILT)        {pend:.0f}")
    print(f"  ROW   (attributable)                {rowsum:.0f}")
    print(f"  built rows                          {len(ROWS)}")
    print()
    print(f"  ⛔ PUBLISHED: total / rows        = {tot}/{len(ROWS)} "
          f"= {tot / len(ROWS):.2f}   <- the 6.2-class figure")
    print(f"  ⭐ MARGINAL: row-attributable/rows = {rowsum:.0f}/{len(ROWS)} "
          f"= {rowsum / len(ROWS):.2f}   <- what row 7 costs")
    print(f"     PLAN_PHP.md §8's PAT-measured figure: ~3")
    print()
    print("  --- per row, IN BUILD ORDER (the series a trend claim needs) ---")
    for i, r in enumerate(ROWS, 1):
        bar = "#" * int(round(per[r] * 4))
        print(f"  {i}. {r:6s} {per[r]:5.2f}  {bar}")
    print()
    print("  --- SENSITIVITY: the classification is judgement, so here is the "
          "worst reading ---")
    for name, extra in PESSIMISM:
        p2, o2, _, _ = spread(extra)
        s2 = sum(p2.values())
        print(f"  {s2 / len(ROWS):5.2f}  tasks/row   ({name}; ONCE left = "
              f"{o2:.0f})")
    print()
    p3, o3, _, _ = spread(PESSIMISM[-1][1])
    worst = sum(p3.values()) / len(ROWS)
    owed = 34          # QUOTA_001 floor 40 - built 6, re-derived by quota.py
    print(f"  ▶ THE 40-ROW FLOOR ({owed} rows still owed, `quota.py`):")
    print(f"      at the PUBLISHED 6.2 :  ~{owed * tot / len(ROWS):.0f} more tasks")
    print(f"      at the MARGINAL      :  ~{owed * rowsum / len(ROWS):.0f} more tasks")
    print(f"      at the WORST reading :  ~{owed * worst:.0f} more tasks")
    return per


def selftest():
    fails = []

    def check(tag, cond, msg):
        print(f"  {'PASS' if cond else 'FAIL'}  {tag}: {msg}")
        if not cond:
            fails.append(tag)

    print("SELFTEST — must-fire negatives")
    ids = task_ids()

    # N1 every task file is classified exactly once, so nothing is silently
    #    dropped out of the denominator.
    missing = [t for t in ids if t not in CLASS]
    extra = [t for t in CLASS if t not in ids]
    check("N1", not missing and not extra,
          f"all {len(ids)} task files classified; unclassified={missing}, "
          f"classified-but-absent={extra}")

    # N2 ⚠ the weights of a split task must sum to exactly 1, or a row's cost is
    #    invented or lost.
    bad = [(t, round(sum(c.values()), 6)) for t, c in CLASS.items()
           if isinstance(c, dict) and abs(sum(c.values()) - 1.0) > 1e-9]
    check("N2", not bad, f"every split task's weights sum to 1.0: {bad}")

    # N3 ⭐ E1. The marginal figure must be well under the published 6.2, or
    #    there is nothing to correct.
    per, once, meth, pend = spread([])
    marg = sum(per.values()) / len(ROWS)
    pub = len(ids) / len(ROWS)
    check("N3", marg < 0.75 * pub,
          f"marginal {marg:.2f} is well under the published {pub:.2f} "
          f"(ONCE={once:.0f} METH={meth:.0f} PENDING={pend:.0f})")

    # N4 ⭐⭐ E4, AND THE ONE THAT MATTERS. The conclusion must survive the WORST
    #    classification, or the honest answer is "it depends on a judgement
    #    call" and I must publish that instead of a number.
    worsts = [sum(spread(e)[0].values()) / len(ROWS) for _, e in PESSIMISM]
    check("N4", max(worsts) < pub,
          f"every reading of the classification is under the published "
          f"{pub:.2f}: {[round(w, 2) for w in worsts]}")

    # N5 ⚠ E2. A "flat, not rising" claim needs a series with real variation --
    #    if every row cost the same the claim would be unfalsifiable, and if the
    #    series WERE monotone rising the claim is simply false.
    ser = [per[r] for r in ROWS]
    rising = all(ser[i] <= ser[i + 1] for i in range(len(ser) - 1))
    check("N5", not rising and max(ser) - min(ser) > 1.0,
          f"the per-row series is NOT monotone rising and has real spread: "
          f"{[round(v, 2) for v in ser]}")

    # N6 ⚠⚠ E3 — THE F52 CONTROL. If the dearest row were one of the RECENT ones
    #    the flat-trend reading would be luck. It must be `ph07`, the one row
    #    that was rebuilt, and that is a claim about a specific row that can
    #    come out wrong.
    dear = max(ROWS, key=lambda r: per[r])
    check("N6", dear == "ph07",
          f"the dearest row is `{dear}` at {per[dear]:.2f} — E3 named `ph07` "
          f"(the only REBUILT row) before running; if it were a recent row the "
          f"flat trend would be luck")

    # N7 ⚠ reproduce the PUBLISHED figure from its own definition, so the thing
    #    being corrected is the thing that was written.
    check("N7", abs(len(ids) / len(ROWS) - 6.5) < 0.5,
          f"total/rows = {len(ids)}/{len(ROWS)} = {len(ids) / len(ROWS):.2f}, "
          f"which is the 6.2-class figure RECAP publishes (it used 37 reported "
          f"tasks -> 6.17; 39 files -> 6.50; both are 'the total-cost ratio')")

    # N8 ⚠⚠ THE PENDING PILE MUST STAY SMALL, or the marginal figure quietly
    #    understates: every PENDING task is real cost waiting for a row to land
    #    on. A check that FAILS if the pile grows past a quarter of the
    #    row-attributable total -- at which point the figure needs restating,
    #    not defending.
    rowsum = sum(per.values())
    check("N8", pend <= 0.25 * rowsum,
          f"PENDING={pend:.0f} is at most a quarter of ROW={rowsum:.0f} — past "
          f"that, the marginal figure understates and must be restated rather "
          f"than quoted")

    print()
    print("SELFTEST " + ("PASS" if not fails else f"FAIL {fails}"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv else (report(), 0)[1])
