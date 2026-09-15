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

ROWS = ["ph03", "ph07", "ph16", "ph29", "ph64", "ph45", "ph53",
        "ph52", "ph55", "ph56"]  # BUILD order

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
    "041": {"ph53": 1.0},      # BUILD row 7 = ph53 -- row LANDED, so charged
    "042": {"ph53": 1.0},      # search ph53's endpoints + its batched debt (DONE)
    # ⭐ THE REVIEW ROUNDS ARE `METH` AND THAT IS THE WHOLE POINT OF THE
    #    CORRECTION RECAP_PHP.md's tasks cell carries: a review round is charged
    #    to METHODOLOGY, not to the rows it reviews, which is precisely why the
    #    per-row series cannot see the methodology a row OPENS. _043 reviewed 12
    #    findings from ph53's and ph45's rounds and retracted F100's R4 half --
    #    none of that cost lands on ph53 here.
    "043": "METH",             # THE review round, F88-F101 (DONE)
    # ⚠ _044 IS CHARGED TO `ph53` AND NOT TO METH, and the call is arguable:
    #    it is a REPAIR of ph53's shipped contract (the pin item 83 ruled, plus
    #    four batched debts), so it is that row's cost in the same way _042's
    #    endpoint search was. ⭐ But it ALSO refuted three of _043's claims and
    #    opened items 97/98/100, which is methodology. Charged to the row
    #    because the row is what it re-gated; the PESSIMISM ladder below is
    #    where that judgement gets its sensitivity.
    "044": {"ph53": 1.0},      # the five-debt ph53 re-gate (DONE)
    "045": {"ph52": 1.0},      # BUILD row 8 = ph52 -- row LANDED, so charged
    "046": {"ph52": 1.0},      # search ph52's endpoints + its missing control

    # --- 2026-09-13/14 -----------------------------------------------------
    # ⚠ N1 CAUGHT THESE SEVEN UNCLASSIFIED, which is exactly what it is for:
    # ROWS had gone stale at 8 while ph55 and ph56 were built and gated.
    "047": "METH",             # THE review round, F96/F97/F102-F106 (DONE)
    "048": {"ph55": 1.0},      # BUILD row 9 = ph55 -- row LANDED, so charged
    "049": "METH",             # attack item 111: is the C BASELINE a free
                               # parameter? corpus-wide, charged to no row
    "050": "METH",             # the item-112 family-B alignment sweep + review;
                               # produced PROTOCOL_PHP §B5, a corpus-wide rule
    # ⚠⚠ ROW 10 COST TWO TASKS AND BOTH ARE CHARGED TO IT. _051 stopped
    # mid-row by design and _052 resumed; splitting 0.5/0.5 would hide that the
    # row cost two, which is the only honest reading of a resumed build.
    "051": {"ph56": 1.0},      # BUILD row 10 = ph56, stopped at 5 of 6 rungs
    "052": {"ph56": 1.0},      # FINISH row 10: R5, spec.md, gate, statistic
    "053": "METH",             # THE review round, F96/F110/F111/F112 (DONE)

    # --- 2026-09-15 --------------------------------------------------------
    # ⚠ N1 CAUGHT BOTH OF THESE the moment it was run after they were written,
    # which is the second time this arm has done exactly its job.
    "054": "ONCE",             # SCREEN ROW 11: all 13 unentered families, 45
                               # candidate rows, THREE agents in parallel. A
                               # one-time survey like the mining wave -- it
                               # prices no row and is not repeated per row.
                               # ⭐ It also produced the ORACLE finding (a
                               # working PHP 5.0.0 CLI + per-id reproducers,
                               # cited by no manager document), which is
                               # corpus-wide and charged to no row.
    "055": "METH",             # THE review round: F96 DECOMPOSED, F113, and
                               # the manager's own M4 (made and refuted before
                               # dispatch -- and the REFUTATION was wrong too).
                               # ⭐ It CLOSED item 117 at zero measurement cost
                               # from an artefact _050 had already written and
                               # three committed gate runs nobody had read.
                               # Corpus-wide, charged to no row.
    "056": "PENDING",          # BUILD row 11 = ph97, T6's first row. IN FLIGHT.
                               # ⛔ It is `PENDING` and NOT `{"ph97": 1.0}` for a
                               # mechanical reason worth stating: `ROWS` below is
                               # the BUILT corpus, `ph97` is not in it yet, and
                               # charging an unbuilt row raises `KeyError`. ▶ On
                               # landing: add `ph97` to `ROWS` AND change this to
                               # `{"ph97": 1.0}` -- N14 fails until the first half
                               # is done, and N1 never saw the second half.
                               # ⚠ The FIRST-IN-FAMILY premium applies (T6 is
                               # family 8 of 20), which is the projection's
                               # stated risk driver -- not the axis.
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


def incomplete_rows():
    """Rows whose ENDPOINT SEARCH has not been run, read off the FILESYSTEM.

    ⛔⛔ WHY THIS EXISTS. Every row's cost figure except one includes a spelling
    search -- `ph45` = build (_036) + search (_037), `ph53` = build (_041) +
    search (_042) -- and the search is where `r{3,4}_endpoint_degenerate` and
    the in-contract spread come from. `ph52` landed at **1.00**, the cheapest
    figure in the series, WITH NO SEARCH: `TASK_PHP_045` §23 names the missing
    `controls/spellings.py` as the row's clearest omission.

    ▶ So 1.00 is NOT COMPARABLE with the rest of the series and the marginal
    rate computed over it is OPTIMISTIC. A per-row series is a trend claim, and
    a trend claim over entries that measure different amounts of work is the
    defect `N5` exists to catch -- one level down, where N5 could not see it.

    ⭐ Detected MECHANICALLY rather than by a maintained list, for the reason
    `.memory-php/04-process.md` law 6 gives: the moment a search lands, the file
    appears and this stops firing with no edit here.
    """
    return [r for r in ROWS
            if not glob.glob("patterns-php/%s-*/controls/spellings.py" % r)]


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
          f"= {rowsum / len(ROWS):.2f}   <- what the next row costs")
    inc = incomplete_rows()
    if inc:
        csum = sum(v for k, v in per.items() if k not in inc)
        cn = len(ROWS) - len(inc)
        print()
        print(f"  ⚠⚠ BUT {len(inc)} ROW(S) HAVE NO `controls/spellings.py`, i.e. NO")
        print(f"     ENDPOINT SEARCH, so their cost is INCOMPLETE and the series")
        print(f"     mixes two different amounts of work: {inc}")
        print(f"  ⭐ MARGINAL over SEARCHED rows only  = {csum:.0f}/{cn} "
              f"= {csum / cn:.2f}   <- the comparable figure")
        print(f"     ▶ Quote the SEARCHED figure for projection; the other is "
              f"optimistic by {csum / cn - rowsum / len(ROWS):+.2f} tasks/row.")
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
    owed = owed_rows()
    marg = rowsum / len(ROWS)
    print(f"  ▶ THE {FLOOR}-ROW FLOOR ({owed} rows still owed, `quota.py`):")
    print(f"      at the PUBLISHED 6.2 :  ~{owed * tot / len(ROWS):.0f} more tasks")
    print(f"      at the MARGINAL      :  ~{owed * marg:.0f} more tasks")
    print(f"      at the WORST reading :  ~{owed * worst:.0f} more tasks")
    print()
    print("  --- AND THE FIRST-IN-FAMILY SPLIT, because the marginal rate cannot")
    print("      see the methodology a row OPENS (ph64 cost 2.00 built, ~4.00")
    print("      charged what it opened) ---")
    first = EMPTY_FAMILIES
    follow = owed - first
    print(f"      {first} FIRST-IN-FAMILY at {OPENER_RATE:.2f} + {follow} follow-on "
          f"at {marg:.2f}")
    print(f"      =  ~{first * OPENER_RATE + follow * marg:.0f} more tasks   "
          f"<-- the premium-weighted middle")
    # ⛔⛔ TWO CORRECTIONS THE ROW COUNT ALONE CANNOT SEE.
    #  (1) The marginal must be the SEARCHED-ONLY one, or the projection inherits
    #      the optimism of rows that skipped their endpoint search.
    #  (2) ⭐ THE 40-ROW FLOOR COUNTS *ROWS*, NOT WORK OWED BY ROWS ALREADY
    #      BUILT. Each unsearched row still owes its endpoint search, and those
    #      tasks are in NO floor estimate published so far.
    cmarg = (sum(v for k, v in per.items() if k not in inc)
             / (len(ROWS) - len(inc))) if inc else marg
    owed_searches = len(inc)
    lo = owed * cmarg + owed_searches
    hi = owed * worst + owed_searches
    mid = first * OPENER_RATE + follow * cmarg + owed_searches
    print()
    print(f"  ⚠⚠ CORRECTED, on the SEARCHED-ONLY marginal {cmarg:.2f} and with the")
    print(f"     {owed_searches} endpoint search(es) STILL OWED BY BUILT ROWS "
          f"{inc} added --")
    print(f"     those are real tasks and appear in NO floor estimate so far:")
    print(f"  ▶ PUBLISH THE RANGE: ~{lo:.0f} .. ~{hi:.0f}, middle ~{mid:.0f}")
    print(f"     (uncorrected, for comparison: ~{owed * marg:.0f} .. "
          f"~{owed * worst:.0f}, middle "
          f"~{first * OPENER_RATE + follow * marg:.0f})")
    return per


# --- THE FLOOR, COMPUTED AND NOT PINNED -------------------------------------
#
# ⛔⛔ `owed` USED TO BE THE LITERAL `34`, commented "floor 40 - built 6".
# `built` became 7 when ph53 landed and the literal did not move, so this tool
# printed ~97 more tasks while RECAP_PHP.md's own prose said 33 rows were owed
# -- a cell that stated the right count and published a figure from the wrong
# one (RECAP_PHP.md open item 93).
#
# ⭐ THE FOURTH HARDCODED FIGURE IN A VALIDATOR TO GO STALE IN ONE SESSION,
# after preimage_screen.py's N10e ("26/17"), this file's own N7
# ("total/rows ~ 6.5", stale THREE TIMES WITHIN THE HOUR) and citecheck.py's
# N1. Every one of the four was repaired the same way and it is the rule now:
# A FIGURE A VALIDATOR ASSERTS IS COMPUTED FROM THE TREE, OR IT IS NOT
# ASSERTED. N9 below is what stops this one coming back.
QUOTA_FAMILIES = 20          # QUOTA_001: the 20 families in patterns-php/CATALOGUE.md
QUOTA_MIN_PER_FAMILY = 2     # QUOTA_001: "min 2, cap 4"
FLOOR = QUOTA_FAMILIES * QUOTA_MIN_PER_FAMILY

# Families with ZERO built rows. One FIRST-IN-FAMILY row is owed by each.
#
# ⛔⛔ WAS `EMPTY_FAMILIES = 14`, HARDCODED, AND IT WENT STALE THE MOMENT `ph55`
# ENTERED T5 -- the FIFTH stale literal in a `.tasks-php/` validator, and the
# one law 6 (`.memory-php/04-process.md`) exists to forbid: A FIGURE A VALIDATOR
# ASSERTS IS COMPUTED FROM THE TREE, OR IT IS NOT ASSERTED.
# ⚠⚠ AND N10 DID NOT CATCH IT: it asserts `0 <= EMPTY_FAMILIES <= owed`, which
# a value drifting DOWNWARD satisfies forever. A bound is not a derivation.
# ⭐ Now computed the way `quota.py` computes it -- Part A's family sections
# against the GATE RECORDS (not the row directories; item 114).
def _empty_families():
    import os as _os, re as _re, glob as _glob
    root = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
    cat = _os.path.join(root, "patterns-php", "CATALOGUE.md")
    built = {m.group(1) for f in _glob.glob(_os.path.join(root, "results-php", "gate", "ph*.json"))
             for m in [_re.match(r".*/(ph\d+)", f)] if m and "smoke" not in f}
    fam, cur = {}, None
    for line in open(cat, encoding="utf-8", errors="replace"):
        h = _re.match(r"^###\s+([STE]\d+)\b", line)
        if h:
            cur = h.group(1); fam.setdefault(cur, set()); continue
        r = _re.match(r"^\*\*(ph\d+)\s", line)
        if r and cur:
            fam[cur].add(r.group(1))
    if not fam:
        raise SystemExit("task_cost: no `### <FAM>` sections in CATALOGUE.md -- "
                         "the format changed and this count would be silently wrong")
    return sum(1 for rs in fam.values() if not (rs & built)), fam


EMPTY_FAMILIES, _FAM_TABLE = _empty_families()

# ph64's cost CHARGED WHAT IT OPENED (RECAP_PHP.md's tasks cell): it measured
# 2.00 by the per-row series while breaking §B1a's O(1)-allocation
# precondition, publishing the only B1 headline and triggering the whole
# statistic thread. ⚠⚠ n = 1. IT IS ONE ROW'S EVIDENCE AND IS LABELLED SO
# EVERYWHERE IT IS QUOTED.
OPENER_RATE = 4.00


def owed_rows():
    """Rows still owed to reach the QUOTA_001 floor. COMPUTED, never pinned."""
    return FLOOR - len(ROWS)


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

    # N7 ⚠⚠ THE TWO QUANTITIES MUST MATERIALLY DIFFER, or this file has nothing
    #    to say. ⛔ ITS FIRST VERSION PINNED `total/rows ~ 6.5` AS A LITERAL --
    #    "reproduce the published figure" -- and it went STALE within the hour,
    #    twice: 39 files -> 6.50, 40 -> 6.67, 41 -> 6.83, then 42 files over 7
    #    rows -> 6.00. `RECAP_PHP.md` open item 73's class, in a validator, for
    #    the third time in one session (see also `preimage_screen.py`'s N10e).
    #    ▶ The CHECKABLE claim is the RATIO of the two quantities, which is
    #    scale-free: the total-cost figure must be at least 1.5x the marginal
    #    one, or the correction this file exists to make is not worth making.
    pub = len(ids) / len(ROWS)
    check("N7", pub >= 1.5 * marg,
          f"total/rows = {len(ids)}/{len(ROWS)} = {pub:.2f} is at least 1.5x "
          f"the marginal {marg:.2f} ({pub / marg:.2f}x), so the two quantities "
          f"answer materially different questions -- computed, NOT pinned")

    # N8 ⚠⚠ THE PENDING PILE MUST STAY SMALL, or the marginal figure quietly
    #    understates: every PENDING task is real cost waiting for a row to land
    #    on. A check that FAILS if the pile grows past a quarter of the
    #    row-attributable total -- at which point the figure needs restating,
    #    not defending.
    rowsum = sum(per.values())
    # ⛔ N9 MUST FIRE IF `owed` IS EVER RE-PINNED. It is the negative item 93
    # exists to install: the figure has to move when a row lands.
    owed_now = owed_rows()
    check("N9", owed_now == FLOOR - len(ROWS) and owed_now == 40 - len(ROWS),
          f"owed={owed_now} is COMPUTED from FLOOR={FLOOR} minus the "
          f"{len(ROWS)} rows in ROWS -- a pinned literal fails here the moment "
          f"a row lands, which is exactly how `owed = 34` survived ph53")

    # ⛔ N10: the split must PARTITION the owed rows, or the middle estimate
    # double-counts. Catches EMPTY_FAMILIES drifting past `owed` as rows land.
    # ⭐ N10b: the count must be DERIVED, not pinned. If CATALOGUE.md's family
    # sections stop parsing this reads 0 or 20 and the arm says so.
    check("N10b", 0 < len(_FAM_TABLE) == QUOTA_FAMILIES,
          f"parsed {len(_FAM_TABLE)} family sections from CATALOGUE.md, want "
          f"{QUOTA_FAMILIES}; EMPTY_FAMILIES={EMPTY_FAMILIES} is derived from them")
    check("N10", 0 <= EMPTY_FAMILIES <= owed_now,
          f"EMPTY_FAMILIES={EMPTY_FAMILIES} must be within owed={owed_now}, so "
          f"first-in-family + follow-on partitions it rather than overlapping")

    # ⚠ N11: the premium must lie between the marginal and the worst reading.
    # If it escapes that interval it is not a premium, it is a third estimate,
    # and the range stops meaning what the tasks cell says it means.
    mg = rowsum / len(ROWS)
    wr = max(worsts)
    mid = (EMPTY_FAMILIES * OPENER_RATE + (owed_now - EMPTY_FAMILIES) * mg) / owed_now
    check("N11", mg <= mid <= wr,
          f"the premium-weighted rate {mid:.2f} sits inside "
          f"[marginal {mg:.2f}, worst {wr:.2f}] -- outside it, the published "
          f"range is three estimates and not a range")

    # ⛔ N12 MUST-FIRE WHILE ANY ROW IS UNSEARCHED, and it is derived from the
    #    filesystem so it stops on its own when the search lands. Without it the
    #    series silently mixes build-only rows with build+search rows and the
    #    marginal rate drifts DOWN while nothing improves.
    inc = incomplete_rows()
    print(f"  ⓘ  N12: rows with no `controls/spellings.py` (no endpoint "
          f"search) = {inc or 'none'}")
    check("N12", all(glob.glob("patterns-php/%s-*" % r) for r in inc),
          f"every row flagged INCOMPLETE exists on disk, so the flag is a "
          f"MISSING SEARCH and not a typo in ROWS: {inc or 'none flagged'}")

    # ⚠ N13 MUST-NOT-FIRE: the searched-only marginal must not EXCEED the worst
    #   reading, or the two estimates have swapped roles and the range is wrong.
    if inc:
        csum = sum(v for k, v in per.items() if k not in inc)
        cmarg = csum / (len(ROWS) - len(inc))
        check("N13", rowsum / len(ROWS) <= cmarg <= max(worsts),
              f"the searched-only marginal {cmarg:.2f} sits between the all-rows "
              f"marginal {rowsum / len(ROWS):.2f} and the worst reading "
              f"{max(worsts):.2f} -- an unsearched row can only make the "
              f"all-rows figure LOOK cheaper, never dearer")

    check("N8", pend <= 0.25 * rowsum,
          f"PENDING={pend:.0f} is at most a quarter of ROW={rowsum:.0f} — past "
          f"that, the marginal figure understates and must be restated rather "
          f"than quoted")

    # ⛔⛔ N14 MUST FIRE IF `ROWS` GOES STALE AGAINST THE BUILT CORPUS, and it
    #    exists because `ROWS` ALREADY DID: it sat at 8 while `ph55` and `ph56`
    #    were built and gated (the comment above the 2026-09-14 block), and
    #    nothing here noticed -- `N1` watches TASK files, not ROWS. Every number
    #    this file publishes divides by `len(ROWS)`, so a stale list makes the
    #    marginal rate, the projection and the whole per-row series wrong at
    #    once, silently, in the forgiving direction.
    #
    # ⭐ DERIVED, NOT PINNED. `.memory-php/04-process.md` law 6 and item 114's
    #    lesson: `quota.py` counted a DIRECTORY as a built row and agreed with
    #    the truth for nine rows because no row had ever been half-built. The
    #    authority is the GATE RECORD -- a row with a directory and no record is
    #    in progress, and must NOT be in `ROWS`.
    #    ⚠ `ph00-smoke` is a relocated PAT calibration kernel with no PHP
    #    provenance; it prices nothing and is excluded, the same exclusion
    #    `quota.py` and the RECAP's count command make.
    gated = {os.path.basename(p).split("-")[0]
             for p in glob.glob(os.path.join(ROOT, "results-php/gate/ph*.json"))}
    gated.discard("ph00")
    missing = sorted(gated - set(ROWS))
    phantom = sorted(set(ROWS) - gated)
    print(f"  ⓘ  N14: gated rows = {len(gated)} · ROWS = {len(ROWS)} · "
          f"missing from ROWS = {missing or 'none'} · "
          f"in ROWS but not gated = {phantom or 'none'}")
    check("N14", not missing and not phantom,
          f"`ROWS` equals the gated corpus -- missing {missing or 'none'}, "
          f"phantom {phantom or 'none'}. A row that is BUILT but absent from "
          f"ROWS divides every published rate by too small a number; a row in "
          f"ROWS that is NOT gated charges cost to something that does not "
          f"exist")

    print()
    print("SELFTEST " + ("PASS" if not fails else f"FAIL {fails}"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv else (report(), 0)[1])
