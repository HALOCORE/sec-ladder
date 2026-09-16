#!/usr/bin/env python3
"""ITEM 125 — how many *"cheapest remaining check"* items were demoted once and
never revisited?  ⭐ PRINTS THE SET WITH ITS ADJUDICATION; NEVER A BARE COUNT.

    python3 .tasks-php/probes/item125_demoted.py            # the report
    python3 .tasks-php/probes/item125_demoted.py --selftest  # the must-fire arms

⚠⚠ **THIS IS AN `ⓘ` REPORT AND IT MUST NEVER FAIL A RUN.**  A member sitting
undone for six rounds is a *finding*, not a build error, and a checker that goes
red on it would be re-classified as noise within a week (`F135`).  The only thing
`--selftest` can fail is the instrument.

========================= WHY THIS FILE EXISTS ==============================
`F123`: `TASK_PHP_051_REPORT.md` §8.1 called the PHP-rebuild check *"the cheapest
remaining"*; `_052` §1.5 demoted it to *"nice to have, skip it"*; two rounds
later a different agent said *"I cannot"*; and it was absent from a protocol
section.  **No step was a lie, and nothing in this repo would have caught it.**
It turned out to cost **30 seconds**.

⭐⭐⭐ `_063` §6.3 PROVED THE POINT ON `F123` ITSELF: **`F123`'s repair was a PROSE
BOX, three rounds carried it in capitals, and NONE DID THE WORK — while
`F140`'s printing ARM scoped the item on its first run.**  ▶ That is `F139`'s
CORRECTED axis: not *which document*, but **TEXT vs AN INVOKED ARM.**  This file
is the arm.

================== HOW THE POPULATION IS DERIVED, AND ITS LIMIT ==============
`_063` §6.3(a) measured three independent under-counts and the third is the one
that decides the item:

  1. HEADING     -- ~56 distinct spellings under a wide match, and 7 landed
                    reports match none at all.
  2. SECTION     -- some reports file it under *"WHAT I DID NOT REACH"*.
  3. ⭐⭐⭐ LINE   -- **`F123`'s OWN FOUNDING INSTANCE STRADDLES A LINE BREAK**
                    (`_051` §8.1 `:440`/`:441`), so **no line-level grep can see
                    both predicates**, and a count done the way item 125
                    specifies returns a set that EXCLUDES the one member we know
                    is a member.  ▶ The item as specified is REFUTED; the census
                    must run at ITEM granularity.

⛔⛔ AND THE TRACKING TEST BELOW IS A PROXY, STATED AS ONE.  `tracked` means
*a distinctive token recurs in a later task file, report, or open item* — which
is **weaker than "the question was answered"**.  It is the right direction for a
report that must not over-claim: it can only move a member OUT of the set, so
the printed set is a **LOWER BOUND** on the class.  ⚠ The `verdict` column is
therefore HAND-ADJUDICATED and recorded here as data, not inferred.
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RECAP = os.path.join(ROOT, "RECAP_PHP.md")
TASKDIR = os.path.join(ROOT, ".tasks-php")

# ── the census, adjudicated BY HAND at `_063`'s landing, 2026-09-16 ──────────
# (report, label, tokens, verdict)
#   MEMBER  -- cheap, undone, and nothing anywhere picked it up
#   TRACKED -- a later task/report/open item took it up (not necessarily done)
#   NOT-AN-ITEM -- the extractor's predicates matched HOUSEKEEPING, a DISCLOSURE
#                  or a RESULT.  ⭐ Kept in the table on purpose: a census that
#                  silently drops its own false positives cannot be audited, and
#                  `N3` asserts they are still here.
CENSUS = [
 ("006", "#error guard for -m32 in emalloc_shim.h", ["m32", "#error"], "TRACKED"),
 ("006", "--audit is run by nothing automatically", ["--audit"], "TRACKED"),
 ("007", "did not run a full gate.py ph00", ["gate.py ph00"], "TRACKED"),
 ("010", "did not run a full gate or re-measure", ["29 source keys"], "NOT-AN-ITEM"),
 ("029", "everything I read was read-only", ["read-only except"], "NOT-AN-ITEM"),
 ("030", "fetched from the network for ph95", ["6d98fc38b53", "db420cb6a14"], "NOT-AN-ITEM"),
 ("031", "which ASan build crashes_pristine", ["crashes_pristine"], "TRACKED"),
 ("032", "the index-scan R3 that forbidden[2] pins absent", ["index-scan"], "MEMBER"),
 ("034", "mbfl_convert_filter_copy aliasing unmeasured", ["mbfl_convert_filter_copy"], "TRACKED"),
 # ⛔⛔ THIS ROW READ `TRACKED` IN THE HAND PASS AND `N4` REFUSED IT. The hand
 # pass used the token "four spellings", which recurs in `_005`/`_006`/`_018`
 # about entirely unrelated things -- a GENERIC token manufacturing tracking
 # that does not exist. ⭐ The arm caught its own author's adjudication within
 # minutes of being written, which is the whole argument of `_063` §6.3(c):
 # an invoked arm beats a prose box. ⚠ The programme DOES track *"is this row's
 # R4 endpoint searched at all?"* (item 58's residue, `task_cost.py`'s `N12`) --
 # but NOT *"is there a fifth spelling for THIS row?"*, which is what was raised.
 ("035", "a fifth R4 spelling for this row -- class tracked by item 58/N12, "
         "this question is not", ["seven from two agents"], "MEMBER"),
 ("037", "r3_namecmp_fn vs r4_buf_slice_inline", ["r3_namecmp_fn"], "NOT-AN-ITEM"),
 ("039", "probe_iters already runs at full n_iters", ["probe_iters"], "TRACKED"),
 ("041", "MAXD = 16 restriction", ["MAXD"], "TRACKED"),
 ("041", "wrote[] indexed SAFELY, unchecked unmeasured", ["get_unchecked"], "TRACKED"),
 ("046", "Pr {req:u32,len:u32} cheaper candidate unbuilt", ["MaybeUninit<Pr>"], "TRACKED"),
 ("049", "main_exclusive_ir as a cheap family-C proxy", ["main_exclusive_ir"], "TRACKED"),
 ("051", "rebuild PHP 5.0.0 with the patch", ["obligation 5"], "TRACKED"),
 ("052", "R1h still not verified against a rebuilt PHP", ["obligation 5"], "TRACKED"),
 ("055", "the period-16 finding is ONE series, unreproduced", ["period-16"], "MEMBER"),
 ("057", "the count over landed reports (= item 125 itself)", ["| 125 |"], "TRACKED"),
 ("058", "ph29 controls/spellings.py docstring unrepaired", ["spellings.py"], "TRACKED"),
 ("058", "do the two inside_share definitions disagree in SIGN?", ["disagree in SIGN"], "MEMBER"),
 ("058", "'byte-identical in all four rows' is enforced by nothing", ["byte-identical in all four"], "MEMBER"),
 ("059", "whether the sweep's 59 was ever right", ["was ever right"], "MEMBER"),
 ("061", "si_addr (nil)->0x1 is an inference, not a measurement", ["si_addr"], "TRACKED"),
 ("062", "is obligation_note the right home for §7.3?", ["obligation_note"], "TRACKED"),
 ("062", "is the two-level inside_share sweep too slow to re-run?", ["16 callgrind runs"], "MEMBER"),
]


def _num(p):
    m = re.search(r"TASK_PHP_(\d+)", os.path.basename(p))
    return int(m.group(1)) if m else -1


def _read(p):
    try:
        return open(p, encoding="utf-8", errors="replace").read()
    except OSError:
        return ""


def tracked_after(rep, tokens):
    """PURE-ish. -> (later files mentioning a token, is it in an OPEN ITEM row).

    ⚠ A PROXY, and the docstring says so: token recurrence is weaker than an
    answer, so this can only move a member OUT.  The printed set is a LOWER
    BOUND on the class.
    """
    n = int(rep)
    later = [p for p in sorted(glob.glob(os.path.join(TASKDIR, "TASK_PHP_*.md")))
             if _num(p) > n]
    where = []
    for p in later:
        t = _read(p)
        if any(tok in t for tok in tokens):
            where.append(os.path.basename(p))
    recap = _read(RECAP)
    sec = recap[recap.index("## Open items"):] if "## Open items" in recap else ""
    return where, any(tok in sec for tok in tokens)


def main():
    by = {}
    for rep, label, tokens, verdict in CENSUS:
        by.setdefault(verdict, []).append((rep, label, tokens))

    print("ITEM 125 -- 'cheapest remaining check' items, demoted and never revisited")
    print(f"  census candidates (`_063` §6.3, item granularity) : {len(CENSUS)}")
    for v in ("MEMBER", "TRACKED", "NOT-AN-ITEM"):
        print(f"  {v:<12}                                      : {len(by.get(v, []))}")

    print("\n" + "=" * 76)
    print("⛔ MEMBERS -- raised once, in a section nothing reads, still undone")
    print("=" * 76)
    for rep, label, tokens in by.get("MEMBER", []):
        where, in_items = tracked_after(rep, tokens)
        flag = ""
        if where or in_items:
            # ⭐ NOT a failure: it means the world moved since the hand pass.
            flag = ("   ⓘ TOKEN NOW RECURS -- re-adjudicate this row: "
                    + ("OPEN ITEM " if in_items else "")
                    + " ".join(sorted(set(where))[:2]))
        print(f"  _{rep}  {label}{flag}")

    print("\n" + "=" * 76)
    print("ⓘ NOT-AN-ITEM -- the extractor matched housekeeping, a disclosure or a")
    print("   RESULT.  Kept in the table so the census stays auditable (N3).")
    print("=" * 76)
    for rep, label, _ in by.get("NOT-AN-ITEM", []):
        print(f"  _{rep}  {label}")

    print("\n⭐⭐ THE SHAPE, AND IT IS WHY THIS IS NOT A HISTORICAL ARTEFACT:")
    recent = [r for r, _, _ in by.get("MEMBER", []) if int(r) >= 58]
    print(f"   {len(recent)} of {len(by.get('MEMBER', []))} members come from `_058` or later"
          f" ({' '.join('_' + r for r in recent)}).")
    print("   ▶ The class is still FORMING, not a backlog left over from the")
    print("     mining wave.")
    print("\n⭐⭐⭐ AND ONE MEMBER IS LOAD-BEARING FOR `_063`'s OWN RULINGS:")
    print("   `_062`'s *is the two-level inside_share sweep too slow to re-run?*")
    print("   `F146` and item 137 both push toward REQUIRING a row-level")
    print("   two-level matrix, and whether a row can AFFORD one has never been")
    print("   measured. ▶ A cost nobody has measured is how `F123` happened.")
    print("\nⓘ REPORT ONLY -- this never fails a run. rc=0 always.")
    return 0


# ============================ MUST-FIRE (§H) =================================
def selftest():
    checks = []

    # N1 -- the table must not silently shrink: every verdict is one of three.
    checks.append(("N1: every census row carries a known verdict",
                   all(v in ("MEMBER", "TRACKED", "NOT-AN-ITEM")
                       for _, _, _, v in CENSUS)))

    # N2 -- ⭐⭐ THE POPULATION IS NOT PINNED TO A LITERAL, IT IS RE-DERIVED BY
    #       RUNNING THE EXTRACTOR. `F138`: *"I called the tool's function" is
    #       not "I ran the tool"* -- so this RUNS `item125_extract.py` and
    #       compares. ⛔ Its first draft asserted `len(CENSUS) == 27` against a
    #       number typed by hand, which would have stayed green if the reports
    #       changed underneath it: a literal is not a measurement.
    #       ⚠ And this is why the extractor had to be promoted out of `.temp/`:
    #       an arm cannot run a generator that auto-`rm` may have deleted.
    import subprocess
    ex = os.path.join(ROOT, ".tasks-php", "probes", "item125_extract.py")
    n_ex = None
    if os.path.exists(ex):
        out = subprocess.run([sys.executable, ex], capture_output=True,
                             text=True, timeout=600).stdout
        m = re.search(r"MEMBERS \(cheap AND undone\)\s*:\s*(\d+)", out)
        n_ex = int(m.group(1)) if m else None
    checks.append((f"N2: the census population is RE-DERIVED by running "
                   f"item125_extract.py, not typed -- extractor says {n_ex}, "
                   f"this table holds {len(CENSUS)}",
                   n_ex is not None and n_ex == len(CENSUS)))

    # N3 -- ⛔ THE FALSE POSITIVES MUST STAY IN THE TABLE. A census that drops
    #       its own misses cannot be audited, and dropping them is the cheapest
    #       way to make this report look better than it is.
    checks.append(("N3: the extractor's false positives are RETAINED, not "
                   "deleted -- a census that hides its misses is unauditable",
                   len([1 for *_, v in CENSUS if v == "NOT-AN-ITEM"]) >= 4))

    # N4 -- non-vacuity against the real tree: a MEMBER's token must actually be
    #       absent from later task files, or `tracked_after` is measuring
    #       nothing. ⭐ This is the arm that catches a typo'd token, which would
    #       silently turn every row into a MEMBER.
    bad = []
    for rep, label, tokens, verdict in CENSUS:
        if verdict != "TRACKED":
            continue
        where, in_items = tracked_after(rep, tokens)
        if not where and not in_items:
            bad.append(f"_{rep} {label}")
    checks.append(("N4: every TRACKED row's token really does recur later "
                   f"-- else the token is wrong, not the world ({len(bad)} bad)",
                   not bad))

    # N5 -- and the converse, which is the one with teeth: a MEMBER's token must
    #       be ABSENT. If it now recurs the world has moved and the hand
    #       adjudication is stale -- ⚠ REPORTED, NOT FAILED, because a member
    #       being picked up is GOOD NEWS and must never read as an error.
    moved = []
    for rep, label, tokens, verdict in CENSUS:
        if verdict != "MEMBER":
            continue
        where, in_items = tracked_after(rep, tokens)
        if where or in_items:
            moved.append(f"_{rep} {label}")
    print(f"  ⓘ  N5: MEMBERS whose token now recurs (re-adjudicate, NOT a "
          f"failure): {len(moved)}")
    for m in moved:
        print(f"        {m}")

    for label, ok in checks:
        print(f"  {'PASS' if ok else 'FAIL'}  {label}")
    for m in bad:
        print(f"        bad token: {m}")
    rc = 0 if all(ok for _, ok in checks) else 1
    print(f"\nITEM-125 CENSUS SELFTEST: {'PASS' if rc == 0 else 'FAIL'}")
    return rc


if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv else main())
