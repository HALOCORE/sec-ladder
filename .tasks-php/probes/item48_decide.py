#!/usr/bin/env python3
# =============================================================================
# item48_decide.py -- THE MEASUREMENT THAT **DECIDED ITEM 48**, AND THE PROBE
# **F69**'s `29 of 30` COMES OUT OF
#
# ⛔⛔ WHY IT IS COMMITTED. Written under `.temp/mgr168/`, which is GITIGNORED.
# Cited at `RECAP_PHP.md:1611` inside **F70**'s section (landed 2026-09-10,
# commit 89008e3), and its output is **F69**'s headline: *"at `file:line`
# **29 of 30** rows have every id at a distinct line"*. `.memory-php/
# 04-process.md` LAW 11. Promoted by `TASK_PHP_064`, 2026-09-17, commit f4bda71.
#
# ⚠⚠ THE OTHER HALF OF THAT HEADLINE IS A DIFFERENT FILE, AND THE SIBLING RULE
# IS WHY IT IS HERE TOO. F69 states TWO numbers in one sentence -- *"at
# `file:line` 29 of 30 … and by **enclosing function 24 of 30**"*. The second is
# `enclosing_fn.py`'s output, promoted beside this one. ⛔ **The law-11 census
# could not see it**: F69's section names no file at all, and retired item 48's
# citation is written `.temp/mgr168/{item48_decide,enclosing_fn,spread_axis,
# sha_norm}.py`, a BRACE EXPANSION that `scratchdeps.py::PATH_RE` matches only
# as the bare directory `.temp/mgr168/` and then discards for having no
# evidence suffix. **Four probe citations register as zero.**
#
# ⭐ WHAT IT MEASURED, re-run on promotion 2026-09-17 and UNCHANGED:
#       files==fixes  27 of 30 · in-between  3 of 30 · one-file  0 of 30
#       (the `f:l` column gives the published 29 of 30; `ph71` alone collides)
# The hypothesis that would have broken §F5's singular R1h spelling -- *one site
# upstream patched N times* -- is dead, and option (a) has a spelling on all 30.
#
# ⛔ IT NEEDS TWO THINGS A CLEAN CHECKOUT DOES NOT HAVE, and they differ:
#   (1) the corpus index `vuln-corpus-5.0/index.csv`, which lives in ANOTHER
#       repo (`php-in-safe-rust`) and is authoritative per
#       `.memory-php/00-corpus.md`. Not re-derivable from here at all.
#   (2) `.temp/mgr/batch/fixsurvey.json` -- GITIGNORED, and its generator IS
#       committed: `python3 .tasks-php/fixsurvey.py`. `CLAUDE.md` Don't #1
#       being FOLLOWED (keep the generator, delete the artefact).
# ▶ When either is absent it now **REPORTS AND RETURNS 0 saying `NOT RUN -- NOT
#   A PASS`**, having checked nothing (item 149; `.tasks-php/width.py`'s `X3` is
#   the rule). ⚠ As written it raised `FileNotFoundError` instead, which reads
#   as a broken probe rather than as an absent cache. **A MISSING INPUT IS NOT A
#   REFUTATION.** ⓘ `--selftest`'s N1/N2/N3/N4b/N4c/N4d are PURE over strings
#   and still run without either input; only N4/N5/N6 need the CSV.
#
# RUN IT:  python3 .tasks-php/probes/item48_decide.py --selftest
#          python3 .tasks-php/probes/item48_decide.py              # the table
# ⓘ Nine arm names -- N1 N2 N3 N4 N4b N4c N4d N5 N6 -- six of them PURE. ⚠ It
# prints them in the `N1  MUST-FIRE: …` / `  [PASS] …` two-line dialect, so the
# arm name and the verdict are on DIFFERENT lines and `checkers.py::_arms_in`
# reads this file as **zero arms**. That is open item 131's dialect blind spot,
# and it is why no arm count is filed in the registry `why`.
#
# ⛔ WHAT IS STILL OWED: (1) `F70` and `F69` are both **UNREVIEWED**. (2) The
# `file` granularity is a LOWER bound on distinctness and this file says so;
# `enclosing_fn.py` is the sharper question and its finder is a HEURISTIC whose
# limits are stated in its own header. (3) Nothing here re-derives the corpus
# index; if that other repo moves, this probe reports NOT RUN and F69's number
# has no second source in this tree.
# =============================================================================

"""
Item 48, the decisive question -- run before the decision is written
(PROTOCOL.md rule 14).

Item 48 offers three options for a row whose ids name several fix_commits:
  (a) ship the fix for the id the catalogue's `c_file_line` names
  (b) ship the union
  (c) split the row

(a) only HAS a spelling if the row's cited defect site identifies exactly ONE
of its ids.  So: for each of the 30 spread rows, how many DISTINCT
`c_file_line` values do its ids carry?

  N distinct sites == N ids  -> the row merged N different SITES.  The kernel
                               extracts one of them; R1h is that one's fix.
                               Option (a) has a spelling.  Clean.
  1 distinct site,  N fixes  -> ONE site, upstream patched it N times over
                               several releases.  Option (a) is AMBIGUOUS and
                               item 48 is a real gap for this row.
  in between                 -> partly both; report exactly.

Reads: the corpus index.csv (authoritative -- .memory-php/00-corpus.md) and the
survey cache.  Writes nothing outside .temp/.

⚠ `grep -a` discipline does not apply here: this reads the CSV with python,
which is not blind the way this box's `grep` is (F35).

Usage: python3 .tasks-php/probes/item48_decide.py [--selftest]
"""
import csv
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CSV = ("/home/apt/repos_common/php-in-safe-rust/paper/evaluation/security/"
       "vuln-corpus-5.0/index.csv")
SURVEY = os.path.join(ROOT, ".temp", "mgr", "batch", "fixsurvey.json")


def defect_file_line(cell):
    """The `|`/`:0` sentinel, exactly as .tasks-php/fixsurvey.py::_defect_file
    resolves it -- a cell may hold several `file:line` alternatives separated
    by `|`, and a `:0` line number is a sentinel meaning 'no line', so a real
    one wins.  Kept character-for-character consistent with the survey tool so
    the two cannot disagree the way _030 and the screen did."""
    parts = [p.strip() for p in cell.split("|") if p.strip()]
    real = [p for p in parts if not re.search(r":0\s*$", p)]
    return (real or parts or [""])[0].strip()


# ⚠⚠ THE FIRST VERSION OF THIS PROBE COMPARED THE RAW CELL AND RETURNED 30/30.
# That is F52's shape -- the SETUP encoded the answer.  Many of these cells
# carry PROSE after the line number:
#
#   "Zend/zend_builtin_functions.c:621 (and :619 for is_subclass_of) - deref
#    of the argument-stack-resident `obj` after the userland-re-entrant ..."
#
# Distinct prose guarantees distinct "sites", so a string compare could not
# have returned anything BUT sites == ids.  The question has to be asked at a
# granularity the answer does not live in -- and per F35, the useful question
# is about a FUNCTION, not about text.  We cannot get the function from the
# CSV, so we bracket it: file:line (finest available) and file (coarsest).
SITE = re.compile(r"([A-Za-z0-9_./+-]+\.(?:c|h|y|re|cpp))\s*:\s*(\d+)")


def site_keys(cell):
    """(file:line, file) for the first real `file:line` in the cell, with the
    prose stripped.  Returns (None, None) if no site can be extracted."""
    chosen = defect_file_line(cell)
    m = SITE.search(chosen)
    if not m:
        m = SITE.search(cell)          # fall back to anywhere in the cell
    if not m:
        return None, None
    return f"{m.group(1)}:{m.group(2)}", m.group(1)


def load_index():
    """id -> (raw_cell, file:line, file), over all THREE id namespaces plus
    merged_members (the corpus's fourth, F62)."""
    out = {}
    with open(CSV, encoding="utf-8", errors="replace") as fh:
        for row in csv.DictReader(fh):
            cell = row.get("c_file_line", "") or ""
            fl, f = site_keys(cell)
            rec = (defect_file_line(cell), fl, f)
            for col in ("input_id", "v5c_id"):
                v = (row.get(col) or "").strip()
                if v:
                    out[v] = rec
            for m in re.split(r"[;,\s]+", (row.get("merged_members") or "")):
                if m.strip():
                    out.setdefault(m.strip(), rec)
    return out


def missing_inputs():
    """The two inputs a clean checkout does not have. ⛔ Absence is EXPECTED."""
    miss = []
    if not os.path.exists(CSV):
        miss.append(f"{CSV}\n             the corpus index, in ANOTHER repo "
                    f"(php-in-safe-rust); authoritative per "
                    f".memory-php/00-corpus.md and NOT re-derivable from here")
    if not os.path.exists(SURVEY):
        miss.append(f"{SURVEY}\n             gitignored; REGENERATE with "
                    f"`python3 .tasks-php/fixsurvey.py`")
    return miss


def report_not_run(miss):
    """⛔ NOT A PASS. `.tasks-php/width.py`'s X3 rule, item 149."""
    print("=" * 78)
    print("⛔⛔ NOT RUN -- NOT A PASS. NO VERDICT WAS REACHED.")
    print("=" * 78)
    print(f"  {len(miss)} input(s) are ABSENT. Their absence is the EXPECTED")
    print("  state of a clean checkout -- one is gitignored with a committed")
    print("  generator (CLAUDE.md Don't #1 being OBEYED) and one lives outside")
    print("  this repo -- but it means THE CHECK COULD NOT RUN, which is itself")
    print("  a result to report (item 149).")
    print()
    for p in miss:
        print(f"    missing  {p}")
    print()
    print("  ⚠ F69's `29 of 30 at file:line` is NOT reproduced by this run and")
    print("    must not be quoted from it. A MISSING INPUT IS NOT A REFUTATION.")
    return 0


def main():
    if "--selftest" in sys.argv:
        return selftest()

    miss = missing_inputs()
    if miss:
        return report_not_run(miss)

    idx = load_index()
    rows = json.load(open(SURVEY))["rows"]

    spread = {}
    for ph, recs in rows.items():
        shas = {r["sha"] for r in recs if r.get("sha")}
        if len(shas) > 1:
            spread[ph] = recs

    print("=" * 74)
    print("ITEM 48: DOES OPTION (a) EVEN HAVE A SPELLING?")
    print("  for each spread row -- how many distinct FIXES, against how many")
    print("  distinct defect sites at THREE granularities?")
    print("    raw   = the whole cell, PROSE INCLUDED (the wrong question --")
    print("            kept so the size of the artefact is visible)")
    print("    f:l   = file:line, prose stripped")
    print("    file  = file only (coarsest; two ids in one file may still be")
    print("            two functions, so this is a LOWER bound on distinctness)")
    print("=" * 74)

    buckets = {"one-file": [], "files==fixes": [], "in-between": []}
    unresolved = []

    print(f"\n{'row':7} {'ids':>4} {'fixes':>6} {'raw':>5} {'f:l':>5} {'file':>5}  verdict")
    print("-" * 74)
    for ph in sorted(spread, key=lambda p: int(re.sub(r"\D", "", p))):
        recs = spread[ph]
        ids = [r["id"] for r in recs if r.get("id")]
        fixes = {r["sha"] for r in recs if r.get("sha")}
        raw, fl, fo, miss = set(), set(), set(), []
        for i in ids:
            rec = idx.get(i)
            if not rec:
                miss.append(i)
                continue
            raw.add(rec[0])
            if rec[1]:
                fl.add(rec[1])
            if rec[2]:
                fo.add(rec[2])
            else:
                miss.append(i)
        if miss:
            unresolved.append((ph, miss))
        nf = len(fixes)
        if len(fo) == 1 and nf > 1:
            v, key = "⚠ ONE FILE, MANY FIXES", "one-file"
        elif len(fo) == nf:
            v, key = "✅ files == fixes", "files==fixes"
        else:
            v, key = f"~ {len(fo)} files / {nf} fixes", "in-between"
        buckets[key].append(ph)
        print(f"{ph:7} {len(ids):4} {nf:6} {len(raw):5} {len(fl):5} {len(fo):5}  {v}")

    print("\n" + "=" * 74)
    print("SUMMARY  (bucketed on the FILE granularity -- the conservative one)")
    print("=" * 74)
    tot = sum(len(v) for v in buckets.values())
    for k in ("files==fixes", "in-between", "one-file"):
        print(f"  {k:14} {len(buckets[k]):3} of {tot}   {' '.join(buckets[k])}")
    if unresolved:
        print(f"\n⚠ ids with no extractable file:line: {unresolved}")
    else:
        print("\n✅ every id on every spread row yielded a file:line.")

    # The rows that decide the FIRST temporal build, specifically.
    print("\n" + "=" * 74)
    print("THE ROWS THAT MATTER NEXT")
    print("=" * 74)
    for ph in ("ph64", "ph61", "ph73"):
        recs = rows.get(ph, [])
        fixes = {r["sha"] for r in recs if r.get("sha")}
        ids = [r["id"] for r in recs if r.get("id")]
        files = {idx[i][2] for i in ids if idx.get(i) and idx[i][2]}
        owes = "OWES item 48" if len(fixes) > 1 else "does NOT owe item 48"
        print(f"  {ph:6} {len(ids)} id(s), {len(fixes)} fix(es), "
              f"{len(files)} file(s)  -> {owes}")
        for r in recs:
            rec = idx.get(r.get("id", ""))
            print(f"         {r.get('id',''):12} {r.get('sha','')[:14]:16} "
                  f"{rec[1] if rec else '?'}")


def selftest():
    ok = True

    def check(name, got, want):
        nonlocal ok
        if got != want:
            ok = False
        print(f"  [{'PASS' if got == want else '**FAIL**'}] {name}: "
              f"got {got!r}, want {want!r}")

    print("N1  MUST-FIRE: the `:0` sentinel loses to a real line")
    check("sentinel", defect_file_line("a.c:0 | b.c:132"), "b.c:132")

    print("N2  MUST-NOT-FIRE: a lone real line is returned unchanged")
    check("lone", defect_file_line("Zend/zend_execute.c:141"),
          "Zend/zend_execute.c:141")

    print("N3  MUST-FIRE: all-sentinel falls back rather than returning empty")
    check("all zero", defect_file_line("a.c:0"), "a.c:0")

    # ⛔⛔ THE SPLIT ITEM 149 FORCES: N1/N2/N3/N4b/N4c/N4d are PURE over strings
    # and run anywhere. N4/N5/N6 read the corpus index, which lives in another
    # repo. Without it the honest answer is NOT A VERDICT, not a FAIL -- so the
    # pure arms still run and report, and the impure ones say they did not.
    if not os.path.exists(CSV):
        print()
        print("  " + "=" * 70)
        print("  ⛔⛔ N4/N5/N6 NOT RUN -- NOT A PASS. NO VERDICT WAS REACHED.")
        print("  " + "=" * 70)
        print(f"     missing  {CSV}")
        print("     The corpus index lives in php-in-safe-rust and is not")
        print("     re-derivable from this repo. The six arms above DID run and")
        print("     their verdicts stand; the three below did not run at all.")
        print("     (item 149; .tasks-php/width.py's X3 is the rule.)")
        print()
        print("ALL PASS (6 of 9 arms; 3 NOT RUN -- NOT A PASS)" if ok
              else "**SOME FAILED**")
        return 0 if ok else 1

    print("N4  MUST-FIRE: the index must resolve the V5C ids that live ONLY in")
    print("    merged_members (F62) -- if it does not, this probe is blind")
    idx = load_index()
    for i in ("V5C-015", "V5C-116", "V5C-173"):
        check(f"{i} resolves", bool(idx.get(i)), True)

    print("N4b MUST-FIRE: prose must be STRIPPED -- this is the defect that")
    print("    made the first run of this probe return 30/30")
    cell = ("Zend/zend_builtin_functions.c:621 (and :619 for is_subclass_of) "
            "- deref of the argument-stack-resident `obj`")
    check("f:l", site_keys(cell)[0], "Zend/zend_builtin_functions.c:621")
    check("file", site_keys(cell)[1], "Zend/zend_builtin_functions.c")

    print("N4c MUST-FIRE: two ids in one file at two lines must AGREE on file")
    print("    and DISAGREE on file:line -- otherwise the two granularities")
    print("    are the same question asked twice")
    a, b = site_keys("ext/standard/array.c:1036"), site_keys("ext/standard/array.c:3938")
    check("files agree", a[1] == b[1], True)
    check("lines differ", a[0] != b[0], True)

    print("N4d MUST-NOT-FIRE: a cell with no file:line yields None, not a guess")
    check("no site", site_keys("bison-regeneration; no single commit"), (None, None))

    print("N5  MUST-FIRE: the index is populated at all")
    check("index > 150 ids", len(idx) > 150, True)

    print("N6  MUST-NOT-FIRE: a fabricated id must NOT resolve")
    check("bogus", idx.get("CRASH-99999"), None)

    print("\n" + ("ALL PASS" if ok else "**SOME FAILED**"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main() or 0)
