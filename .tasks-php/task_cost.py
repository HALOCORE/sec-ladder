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

def row_family():
    """`{row: family}` parsed from CATALOGUE.md's Part B section headers.

    Derived, so a catalogue change moves it with no edit here."""
    fam, cur = {}, None
    path = os.path.join(ROOT, "patterns-php", "CATALOGUE.md")
    with open(path, encoding="utf-8", errors="replace") as fh:
        for ln in fh:
            m = re.match(r"### ([SET]\d+) —", ln)
            if m:
                cur = m.group(1)
            m2 = re.match(r"\*\*(ph\d+) ·", ln)
            if m2 and cur:
                fam[m2.group(1)] = cur
    return fam

ROWS = ["ph03", "ph07", "ph16", "ph29", "ph64", "ph45", "ph53",
        "ph52", "ph55", "ph56", "ph97"]  # BUILD order

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
    "056": {"ph97": 1.0},      # BUILD row 11 = ph97, T6's first row. ONE task:
                               # five rungs + R1h, gated PASS, no resume needed.
                               # ⚠ The FIRST-IN-FAMILY premium applies (T6 is
                               # family 8 of 20), which is the projection's
                               # stated risk driver -- not the axis. ⭐ And it
                               # came in at 1.00 anyway, the joint-cheapest row
                               # in the series, which is EVIDENCE AGAINST the
                               # premium rather than for it -- n=1, and ph64 is
                               # the row that argued for it.
                               #
                               # ⭐⭐ THE ENGINEER REFUSED TO WRITE THIS LINE AND
                               # WAS RIGHT. _056 reported N14 red, named the
                               # exact two-line edit, and declined to make it:
                               # "the remedy's second half is a cost claim about
                               # my own task in the ledger the published ~94-127
                               # projection comes from". ▶ A cost ledger is not
                               # a build artefact; the party whose work it prices
                               # must not price it. Landed by the manager,
                               # 2026-09-15, from the gate record.
    "057": "METH",             # THE review round: F114-F122 (NINE findings, the
                               # largest backlog since the mining wave) plus
                               # F96's R2/R4/R5. Corpus-wide, charged to no row.
                               # ⚠ CLASSIFIED WHILE _056 WAS STILL RUNNING, and
                               # that is a deliberate exception to PROTOCOL rule
                               # 11 (do not edit what a running agent reads).
                               # `task_ids()` globs the DISK, so merely WRITING
                               # TASK_PHP_057.md already made N1 red -- and a
                               # running engineer that sweeps the checkers would
                               # have chased a failure with nothing to do with
                               # its work. ⭐ A certain harm beats a negligible
                               # race. ▶ The general rule: writing the NEXT task
                               # file is not free while an agent runs; either
                               # classify it in the same breath, or do not write
                               # it until the agent lands.

    # --- 2026-09-15, item 127 ----------------------------------------------
    # ⭐ THE PRECEDENT IS `_028` AND IT IS THE SAME THREE ROWS. That task added
    #    `spellings` to ph03/ph16/ph29 and split 1/3 each; this one adds the
    #    `inside_share` matrix those three never got, and the split is copied
    #    rather than re-argued.
    # ⚠ WHY NOT `METH`, when the question it answers (is A1 admissible
    #    cross-language?) is the statistic thread's. Because `_046` -- "search
    #    ph52's endpoints + its MISSING CONTROL" -- set the rule that a control
    #    a row should have shipped with is THAT ROW's debt, not methodology's.
    #    The thread asked the question; the rows owe the measurement.
    # ⚠ `ph97` IS RE-GATED BY THIS TASK TOO (its template hardcodes `n_iters`
    #    where `slb.read` would derive it) AND IS DELIBERATELY NOT CHARGED. A
    #    two-line fix plus a re-gate is not a quarter of this task, and charging
    #    the row that DONATED the template would make being the template look
    #    expensive. ⓘ Said here because an uncommented 1/3 split over four
    #    re-gated rows is exactly the kind of silent judgement `PESSIMISM` exists
    #    to be tested against.
    "058": {"ph03": 1 / 3, "ph16": 1 / 3, "ph29": 1 / 3},

    # --- 2026-09-15 ---------------------------------------------------------
    # ⭐ CLASSIFIED IN THE SAME BREATH AS BEING WRITTEN, WHICH IS THE RULE `_057`
    #    WROTE FOR ITSELF SIX LINES UP: `task_ids()` globs the DISK, so merely
    #    WRITING the file makes `N1` red, and a later agent sweeping the checkers
    #    would chase a failure that has nothing to do with its work. ⓘ Unlike
    #    `_057` this costs no rule-11 exception -- nothing is running yet, which
    #    is the whole point of doing it before dispatch rather than after.
    "059": "METH",             # THE review round: F129/F130/F127/F128 (the 8th),
                               # with item 132 folded in. Corpus-wide, charged to
                               # no row -- the same call as _043/_047/_053/_055/
                               # _057, and the reason the per-row series cannot
                               # see what a row OPENS.
                               # ⚠ WHY ITEM 132 DOES NOT MAKE IT ROW-CHARGEABLE,
                               # given `_058`'s rule that a control a row should
                               # have shipped with is THAT ROW's debt: item 132
                               # pins the THRESHOLD of F74's admissibility bar
                               # over the whole corpus from committed records. It
                               # is not any row's missing control -- it is the
                               # rule every row is judged by. ⓘ The residue it
                               # may expose (ph07/ph53/ph64 still have no measured
                               # share) IS row debt, and will be charged to those
                               # rows by whatever task measures them.
    "060": "PENDING",          # BUILD row 12 = ph96, T6's second, which CLOSES
                               # the family. DISPATCHED, NOT LANDED.
                               # ⛔⛔ I FIRST WROTE `{"ph96": 1.0}` AND `N14`
                               # REFUSED IT -- correctly, and the crash was the
                               # cheapest possible way to be told: `ph96` is not
                               # in `ROWS` because it has no GATE RECORD, and
                               # "a row in ROWS that is NOT gated charges cost
                               # to something that does not exist". ⭐ `_040`
                               # set the precedent: a build brief for an unbuilt
                               # row is PENDING, not row cost.
                               # ▶ WHEN THE ROW GATES, do BOTH in one edit:
                               # append "ph96" to `ROWS` and reclassify this to
                               # {"ph96": 1.0}. Doing one without the other is
                               # what N14 exists to catch.
                               # ⓘ It will then carry two extras the row did not
                               # strictly owe -- the second repair strategy
                               # priced as a control (§2.6) and the `:427-429`
                               # limb recorded (§2.5) -- and they are still THIS
                               # row's cost under `_058`'s rule: a control a row
                               # should have shipped with is that row's debt.
                               # ph97 came in at 1.00; that is the comparison to
                               # watch, same family and same shape.
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
    print("  --- AND THE FIRST-IN-FAMILY SPLIT, which is now MEASURED rather")
    print("      than pinned. ⛔ The old OPENER_RATE = 4.00 came from ONE row")
    print("      (ph64) and is refuted in SIGN at n = 8 --")
    fseries, oseries = opener_split(per)
    orate = opener_rate(per)
    print(f"      first-in-family {orate:.2f} (n={len(fseries)}) · follow-on "
          f"{(sum(oseries)/len(oseries)) if oseries else float('nan'):.2f} "
          f"(n={len(oseries)}) · all-rows {marg:.2f}")
    print(f"      ⭐ openers are {'CHEAPER' if orate < marg else 'dearer'} than "
          f"the all-rows marginal, not dearer by 2x as 4.00 assumed")
    first = EMPTY_FAMILIES
    follow = owed - first
    print(f"      {first} FIRST-IN-FAMILY at {orate:.2f} + {follow} follow-on "
          f"at {marg:.2f}")
    print(f"      =  ~{first * orate + follow * marg:.0f} more tasks   "
          f"<-- the weighted middle")
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
    mid = first * orate + follow * cmarg + owed_searches
    print()
    print(f"  ⚠⚠ CORRECTED, on the SEARCHED-ONLY marginal {cmarg:.2f} and with the")
    print(f"     {owed_searches} endpoint search(es) STILL OWED BY BUILT ROWS "
          f"{inc} added --")
    print(f"     those are real tasks and appear in NO floor estimate so far:")
    # ⛔⛔ THE THREE ESTIMATES ARE SORTED, NOT ASSUMED TO BE ORDERED.
    #   The old code called the opener-weighted one "the middle" and printed
    #   `lo .. hi, middle mid`. That LABEL encoded the premium just as
    #   OPENER_RATE did: with openers measured CHEAPER than the marginal, the
    #   opener-weighted estimate is the LOW end and "middle ~70" printed below
    #   a low of ~73 -- an incoherent range that no arm caught, because N11
    #   asserted the very ordering that was wrong.
    named = sorted([(lo, "uniform searched-marginal"),
                    (hi, "worst classification reading"),
                    (mid, "family-weighted (openers at their measured rate)")])
    print(f"  ▶ PUBLISH THE RANGE: ~{named[0][0]:.0f} .. ~{named[-1][0]:.0f}, "
          f"middle ~{named[1][0]:.0f}")
    for v, lbl in named:
        print(f"       ~{v:5.0f}   {lbl}")
    print(f"     (uncorrected, for comparison: ~{owed * marg:.0f} .. "
          f"~{owed * worst:.0f}, middle "
          f"~{first * orate + follow * marg:.0f})")
    print(f"     ⚠ At the OLD pinned OPENER_RATE = {OPENER_RATE:.2f} the middle "
          f"would read ~{first * OPENER_RATE + follow * cmarg + owed_searches:.0f}"
          f" -- the difference is the refuted premium, shown so the change to a")
    print(f"     PUBLISHED figure is visible rather than silent.")
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
QUOTA_MIN_PER_FAMILY = 2     # QUOTA_001: "min 2, cap 4"


def _quota_floor():
    """`sum(min(2, |family|))` over CATALOGUE.md's Part B sections. DERIVED.

    ⛔⛔ THIS WAS `20 * 2 = 40` AND IT WAS A PIN WEARING A FORMULA'S CLOTHES.
    `ADJUDICATION_003` / open item 121: `S5`, `S6` and `T4` hold ONE catalogued
    row each, so a flat min-2 counts SIX rows that cannot exist unless the
    catalogue grows. Derived here and in `quota.py`, from the same parse, so
    the two cannot disagree -- and if the catalogue grows, both move with it.

    ⚠ The floor falling 40 -> 37 is a CONCESSION, not a saving: three families
    can never produce the within-family control min-2 exists to buy. See
    `ADJUDICATION_003` §2 and `quota.py`'s `N5b`.
    """
    fam = {}
    for r, f in row_family().items():
        fam.setdefault(f, []).append(r)
    return sum(min(QUOTA_MIN_PER_FAMILY, len(v)) for v in fam.values())


QUOTA_FAMILIES = len({f for f in row_family().values()})
FLOOR = _quota_floor()

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



def opener_split(per):
    """`(first, follow)` -- per-row costs split by FIRST-IN-FAMILY, in build order.

    ⛔⛔ THIS REPLACES A PINNED `OPENER_RATE = 4.00`, AND THE PIN WAS WRONG IN
    SIGN. It came from ONE row: `ph64` measured 2.00 by the per-row series and
    was charged ~4.00 for "what it opened" -- it broke §B1a's O(1)-allocation
    precondition, published the only B1 headline and triggered the whole
    statistic thread, whose tasks are charged to METH and not to it. The comment
    said `n = 1` and said it honestly. **Nobody re-derived it for ten rows.**

    ⭐⭐ MEASURED at n = 8 when `ph97` landed (2026-09-15):

        first-in-family  2.188  (n=8)     follow-on  3.167  (n=3)

    **First-in-family rows are CHEAPER than follow-on rows**, which is the
    opposite of the premium the published projection was built on, and `4.00` is
    nearly double the measured opener mean.

    ⚠⚠ TWO HONEST QUALIFICATIONS, BOTH POINTING THE SAME WAY:
      * `follow` is n = 3 and is dominated by `ph07` at 5.50 -- **the only
        REBUILT row**, named as atypical by `N6`'s control BEFORE it ran.
        Excluding it, follow-on is 2.00 against openers' 2.19, so openers are
        dearer by **0.19**. **Either way `4.00` is not supported.**
      * The ARGUMENT for 4.00 survives its own refutation and must be said: the
        per-row measure **cannot see the methodology a row OPENS**. That is a
        claim about the measure's blindness, not about its output, so no
        measurement can refute it. ⛔ **But it was applied to exactly ONE row and
        never to another, and `ph97` opened `T6` at 1.00 while spinning off no
        methodology at all.** ▶ A credit granted once and never again is not a
        rate; it is an adjustment to one row, and it belongs in that row's cell.
    """
    fam, seen, first, follow = row_family(), set(), [], []
    for r in ROWS:
        f = fam.get(r, "?")
        (follow if f in seen else first).append(per[r])
        seen.add(f)
    return first, follow


OPENER_RATE = 4.00   # ⛔ LEGACY, KEPT ONLY SO `N15` CAN ASSERT AGAINST IT.
                     #   Never used in a projection -- `opener_rate(per)` is.


def opener_rate(per):
    """The DERIVED first-in-family rate, with the all-rows marginal as fallback."""
    first, _ = opener_split(per)
    return (sum(first) / len(first)) if first else (sum(per.values()) / len(ROWS))


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
    #    if every row cost the same the claim would be unfalsifiable.
    #
    # ⛔⛔ THIS ARM ASSERTED A DIRECTION TOO, AND IT IS THE **THIRD** IN THIS FILE
    #    (`N11`/F126, `N13`/F128, this). It read
    #        check("N5", not rising and max(ser) - min(ser) > 1.0, ...)
    #    -- and the two conjuncts are DIFFERENT IN KIND, which is the defect:
    #      * `max - min > 1.0` is a VARIATION FLOOR. Legitimate: without spread
    #        the trend claim is unfalsifiable and the arm should say so.
    #      * `not rising` is a DIRECTION ASSERTION. If rows 12-14 happened to
    #        cost 3, 4 and 5 tasks the series becomes monotone rising, N5 FIRES,
    #        and the ledger is reported as BROKEN when the truth is that the
    #        published trend claim needs restating.
    #
    # ⛔⛔ AND THIS FILE IS WHAT **PRODUCES** THE TREND CLAIM. An arm inside it
    #    that enforces the claim's conclusion cannot notice the conclusion has
    #    changed -- it can only report the change as a tool failure. RECAP_PHP.md
    #    publishes "flat if anything FALLING" from this very series, so the arm
    #    and the claim would go stale TOGETHER, silently: the one configuration
    #    in which nothing catches it.
    #
    # ⭐ THE RULE THE ITEM-130 SWEEP EARNED, and it is narrower than F128's first
    #    wording (which would have damaged five correct arms): an arm MAY assert
    #    a direction when the direction is a PUBLISHED FINDING it exists to
    #    defend -- and then it must PRINT THE MEASURED MARGIN beside the floor,
    #    so the margin is visible shrinking (`width.py` N4/N3b are the model).
    #    It must NOT assert a direction still being ESTIMATED.
    ser = [per[r] for r in ROWS]
    rising = all(ser[i] <= ser[i + 1] for i in range(len(ser) - 1))
    check("N5", max(ser) - min(ser) > 1.0,
          f"the per-row series has real spread ({max(ser) - min(ser):.2f} > 1.0), "
          f"so a flat-vs-rising claim about it is falsifiable at all: "
          f"{[round(v, 2) for v in ser]}")
    print(f"  ⓘ  N5b REPORT (no verdict): the series is "
          f"{'MONOTONE RISING' if rising else 'not monotone rising'}. ⛔ The "
          f"direction is NOT asserted -- if it ever turns, that is a RESULT to "
          f"restate the published trend from, not a failure of this file.")

    # N6 ⚠⚠ E3 — THE F52 CONTROL. If the dearest row were one of the RECENT ones
    #    the flat-trend reading would be luck. It must be `ph07`, the one row
    #    that was rebuilt, and that is a claim about a specific row that can
    #    come out wrong.
    #
    # ⚠⚠ RETIREMENT CONDITION, ADDED 2026-09-15 (item 130's sweep). This arm is
    #    a REGISTERED PREDICTION, not an invariant: E3 named `ph07` BEFORE the
    #    run, and that is exactly what makes it evidence. ⛔ But a prediction
    #    with no expiry becomes a PIN -- the day a genuinely hard row honestly
    #    costs more than `ph07`'s 5.50, this arm fires on CORRECT data, which is
    #    the `N11`/`N13`/`N5` failure mode arriving by a slower road.
    # ▶ RETIRE IT, do not "fix" it, when EITHER holds:
    #      (a) a row other than `ph07` is dearest AND its task list has been
    #          read by hand and found legitimate -- then the E3 control has
    #          SERVED ITS PURPOSE and the finding is that the trend reading
    #          needs restating; or
    #      (b) `ph07` stops being the only REBUILT row, which is the entire
    #          reason it was predicted dearest.
    #    In both cases the replacement is an `ⓘ` REPORT of the dearest row and
    #    its margin -- never a re-pin to whichever row happens to lead.
    # ⓘ The margin is PRINTED so it is visible shrinking: that is the property
    #    `width.py`'s N4/N3b have and the three broken arms did not.
    dear = max(ROWS, key=lambda r: per[r])
    runner = max((r for r in ROWS if r != dear), key=lambda r: per[r])
    check("N6", dear == "ph07",
          f"the dearest row is `{dear}` at {per[dear]:.2f}, ahead of `{runner}` "
          f"at {per[runner]:.2f} (margin {per[dear] - per[runner]:+.2f}) — E3 "
          f"named `ph07` (the only REBUILT row) before running; if it were a "
          f"recent row the flat trend would be luck. ⚠ REGISTERED PREDICTION, "
          f"NOT AN INVARIANT — see the retirement condition above")

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
    #
    # ⛔⛔ AND N9 ITSELF CARRIED A PIN. It read
    #     `owed_now == FLOOR - len(ROWS) and owed_now == 40 - len(ROWS)`
    # -- the second clause hardcoding the 40-row floor INSIDE THE ARM WHOSE
    # WHOLE PURPOSE IS TO STOP FIGURES BEING PINNED. It went stale the moment
    # ADJUDICATION_003 derived the floor as 37, and it is the EIGHTH stale
    # literal in a `.tasks-php/` validator. ⭐ The pin was there to stop FLOOR
    # drifting silently; the right way to say that is to re-derive FLOOR here,
    # independently, and compare -- which tests the same property with no
    # constant to age.
    owed_now = owed_rows()
    floor_again = _quota_floor()
    check("N9", owed_now == FLOOR - len(ROWS) and FLOOR == floor_again
          and FLOOR <= QUOTA_FAMILIES * QUOTA_MIN_PER_FAMILY,
          f"owed={owed_now} is COMPUTED from FLOOR={FLOOR} minus the "
          f"{len(ROWS)} rows in ROWS, and FLOOR re-derives to {floor_again} "
          f"(<= the flat {QUOTA_FAMILIES * QUOTA_MIN_PER_FAMILY}) -- a pinned "
          f"literal fails here the moment a row lands, which is how "
          f"`owed = 34` survived ph53 and how this arm's own `40` survived "
          f"item 121")

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

    # ⛔⛔ N11 REWRITTEN 2026-09-15, AND THE OLD ONE WAS A BOUND THAT ENCODED A
    #   HYPOTHESIS. It asserted `mg <= mid <= wr` -- the family-weighted rate
    #   sits ABOVE the marginal -- which can only hold if openers are DEARER.
    #   ⭐ It could not express "openers are cheaper", so when `ph97` landed and
    #   made that true at n = 8, the arm reported the DATA as the failure.
    #   `.memory-php/04-process.md` law 6's sentence, one level up: a bound is
    #   not a derivation, and a bound whose direction is the hypothesis under
    #   test is not even a bound.
    #
    #   ▶ What N11 must actually assert is that the family-weighted estimate is
    #   a REWEIGHTING of the same per-row costs -- so it cannot escape the
    #   [opener, follow-on] interval it mixes, in EITHER order.
    mg = rowsum / len(ROWS)
    wr = max(worsts)
    orate = opener_rate(per)
    fseries, oseries = opener_split(per)
    mid = (EMPTY_FAMILIES * orate + (owed_now - EMPTY_FAMILIES) * mg) / owed_now
    check("N11", min(orate, mg) - 1e-9 <= mid <= max(orate, mg) + 1e-9,
          f"the family-weighted rate {mid:.2f} lies between the opener rate "
          f"{orate:.2f} and the marginal {mg:.2f} in whichever order they fall "
          f"-- it is a REWEIGHTING of those two and cannot escape them")

    # ⛔⛔ N15 MUST FIRE WHILE THE PINNED `OPENER_RATE` DISAGREES WITH THE
    #   MEASURED ONE. It is the ratchet on the constant that N11 used to assume.
    #   ⭐ Today it fires: pinned 4.00 against a measured 2.19 at n = 8, a
    #   premium refuted in SIGN. The pin is kept ONLY so this arm has something
    #   to compare against; delete the pin and delete this arm together.
    fmean = sum(fseries) / len(fseries) if fseries else float("nan")
    omean = sum(oseries) / len(oseries) if oseries else float("nan")
    print(f"  ⓘ  N15: first-in-family {fmean:.2f} (n={len(fseries)}) · "
          f"follow-on {omean:.2f} (n={len(oseries)}) · pinned OPENER_RATE "
          f"{OPENER_RATE:.2f}")
    check("N15", len(fseries) >= 2,
          f"the opener rate is derived from n={len(fseries)} rows, not from one "
          f"-- at n=1 it is a row's cost wearing a rate's name, which is exactly "
          f"how OPENER_RATE=4.00 stood for ten rows")
    # ⛔ AND THIS IS AN `ⓘ`, NOT A `check`. The first draft wrote it as
    #   `check("N15b", <cond> or True, ...)`, which PRINTS "PASS" while being
    #   unfalsifiable -- a check that cannot fail, which is `PROTOCOL_PHP.md`
    #   §H's own target and F10's rule. ⭐ `quota.py`'s discipline is the right
    #   one: a REPORT must not wear a VERDICT's clothes.
    print(f"  ⓘ  N15b REPORT (no verdict): pinned OPENER_RATE {OPENER_RATE:.2f} "
          f"vs measured {fmean:.2f}, delta {OPENER_RATE - fmean:+.2f}. The pin "
          f"is used in NO projection -- `opener_rate(per)` is. Kept only so the "
          f"gap stays visible; delete the pin and N15b together.")

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
    #
    # ⛔⛔ THIS ARM ASSERTED A DIRECTION UNTIL 2026-09-15 AND THE DIRECTION IS
    #    FALSE. It read `rowsum/len(ROWS) <= cmarg <= max(worsts)`, justified as
    #    *"an unsearched row can only make the all-rows figure LOOK cheaper,
    #    never dearer"* -- and `_058` refuted it the day it was written, by
    #    charging 1/3 of a task to `ph03`, which is UNSEARCHED. An unsearched row
    #    is not an intrinsically CHEAP row; it is a row missing ONE KIND of task,
    #    and any other task charged to it raises the all-rows figure ABOVE the
    #    searched-only one. Measured: all-rows 2.55, searched-only 2.54.
    #
    # ⭐⭐ SECOND ARM IN THIS FILE TO ASSERT AN EFFECT'S SIGN AND THEREFORE
    #    REPORT THE DATA AS THE FAILURE -- `N11` was the first (F126, the
    #    first-in-family premium, refuted in sign at n=8 after standing on n=1).
    #    ⚠ AND THE TELL WAS VISIBLE WITHOUT THE REFUTATION: the comment above
    #    said the arm was for *"must not EXCEED the worst reading"* -- ONE bound
    #    -- while the code asserted TWO. **When a check's prose and its predicate
    #    disagree about how many conditions there are, the extra one is usually
    #    the unmeasured assumption.**
    #
    # ▶ Repaired the same way N11 was: assert the bound the comment actually
    #   justifies, and REPORT the ordering instead of requiring it.
    if inc:
        csum = sum(v for k, v in per.items() if k not in inc)
        cmarg = csum / (len(ROWS) - len(inc))
        amarg = rowsum / len(ROWS)
        check("N13", cmarg <= max(worsts),
              f"the searched-only marginal {cmarg:.2f} does not exceed the worst "
              f"reading {max(worsts):.2f} -- past that the two estimates have "
              f"swapped roles and the published range is upside down")
        print(f"  ⓘ  N13b REPORT (no verdict): searched-only {cmarg:.2f} vs "
              f"all-rows {amarg:.2f}, delta {cmarg - amarg:+.2f}. ⛔ The SIGN is "
              f"NOT asserted: unsearched rows {inc} carry non-search cost too, "
              f"so either ordering is legitimate and neither is evidence.")

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
