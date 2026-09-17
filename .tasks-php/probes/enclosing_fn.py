#!/usr/bin/env python3
# =============================================================================
# enclosing_fn.py -- ⭐⭐ THE SIBLING THE BRIEF DID NOT NAME. **F69's OTHER
# HEADLINE NUMBER, `24 of 30 BY ENCLOSING FUNCTION`, IS THIS FILE'S OUTPUT.**
#
# ⛔⛔ WHY IT IS COMMITTED, AND WHY IT IS HERE AT ALL. `TASK_PHP_064` was
# dispatched to promote 14 files that 13 findings rest on, and told to *"check
# the siblings in the same citing sentence"* -- because `PROMOTE_001` had taken
# one probe of three out of F74's sentence and left two behind. **Applying that
# rule to `item48_decide.py` found this file.** F69 states TWO numbers in ONE
# sentence (`RECAP_PHP.md:1622`):
#
#     "at `file:line` **29 of 30** rows have every id at a distinct line,
#      and by **enclosing function 24 of 30**."
#
# The first is `item48_decide.py`'s. **The second is this file's, and nothing
# in the tree re-derives it.** Re-run on promotion 2026-09-17: `fns==ids
# **24 of 30**`, `fns<ids 6 of 30`, `unresolved 0 of 30` -- the published number,
# to the digit.
#
# ⛔⛔⛔ AND THE LAW-11 CENSUS COULD NOT HAVE FOUND IT. Two independent reasons,
# both worth writing down:
#   (1) **F69's section names no file.** `probes/scratchdeps.py` keys on
#       CITATIONS, so a published number whose probe is never named is invisible
#       to it by construction. `F132`'s *"the census prints a CANDIDATE SET"* --
#       this is the set's complement.
#   (2) The one place it IS cited beside its siblings, retired item 48
#       (`RECAP_PHP.md:9616`), spells them
#       `.temp/mgr168/{item48_decide,enclosing_fn,spread_axis,sha_norm}.py` --
#       a BRACE EXPANSION. `scratchdeps.PATH_RE` matches only `.temp/mgr168/`,
#       which has no evidence suffix and is dropped. **Four citations register
#       as zero.** ⚠ Measured, not argued: `PATH_RE.findall` on that line
#       returns `['.temp/mgr168/']`.
#
# `.memory-php/04-process.md` LAW 11. Promoted by `TASK_PHP_064`, 2026-09-17,
# repo at commit f4bda71. Written under `.temp/mgr168/` (2026-09-10, the
# item-48 round, landed at commit 89008e3).
#
# ⛔ IT NEEDS THREE THINGS A CLEAN CHECKOUT DOES NOT HAVE:
#   (1) the PINNED php-5.0.0 tarball, in ANOTHER repo, sha256-verified below;
#   (2) the corpus index `vuln-corpus-5.0/index.csv`, also in that repo
#       (imported through `item48_decide.load_index`);
#   (3) `.temp/mgr/batch/fixsurvey.json` -- GITIGNORED, generator committed at
#       `.tasks-php/fixsurvey.py`. `CLAUDE.md` Don't #1 being FOLLOWED.
# ▶ When any is absent it **REPORTS AND RETURNS 0 saying `NOT RUN -- NOT A
#   PASS`** (item 149). ⚠ As written, a missing tarball made `selftest()` return
#   **2** under the words *"CANNOT SELFTEST"* -- honest in prose and unreadable
#   as an exit code, since 2 is neither the filed pass nor an adjudicated red.
#
# RUN IT:  python3 .tasks-php/probes/enclosing_fn.py --selftest
#          python3 .tasks-php/probes/enclosing_fn.py           # the 30-row table
# ⓘ Six arm names, N1..N6, in the two-line `N1 …` / `  [PASS] …` dialect that
# `checkers.py::_arms_in` reads as ZERO arms (open item 131). No count is filed.
#
# ⛔ WHAT IS STILL OWED. (1) **F69 is UNREVIEWED.** (2) ⚠⚠ **THE FINDER IS A
# HEURISTIC AND THAT IS THE POINT, not a caveat**: it scans backwards for a
# column-0 definition header, so it gets macro-generated bodies (ZEND_VM
# handlers) wrong and cannot see functions defined inside macros at all. Every
# verdict prints the FUNCTION NAME so a reader can check it by eye -- an unnamed
# count would be an assertion. (3) Its N1/N2 calibration is a SINGLE pair
# (`_safe_emalloc`/`_ecalloc`, the pair F7 caught the manager confusing); no arm
# measures the heuristic's error rate over the 30 rows it reports on.
# (4) `24 of 30` is the input open item 35's unpaid audit needs, and that audit
# is still unpaid.
# =============================================================================

"""
Item 48 evidence, part 3 -- ask the question at the granularity the answer
actually lives in.

`item48_decide.py` brackets the 30 spread rows two ways and neither is the
right question:

    file:line   too FINE   -- two lines can be in one function
    file        too COARSE -- two ids in one file can be two functions

F35's standing lesson on this programme is *"ask a question about a FUNCTION,
not about text"*.  §G1 asks whether the ids share a MECHANISM, and the nearest
mechanical proxy available is the enclosing function of each cited line.

So: resolve each spread row's ids to (file, enclosing function) against the
PINNED 5.0.0 tarball, and count distinct functions.

⚠ THE ENCLOSING-FUNCTION FINDER IS A HEURISTIC AND ITS LIMITS ARE THE POINT.
It scans backwards from the cited line for a plausible K&R/ANSI definition
header at column 0.  It will get macro-generated bodies (ZEND_VM handlers)
wrong, and it cannot see functions defined inside macros at all.  Every
verdict it produces is therefore REPORTED WITH THE FUNCTION NAME so a reader
can check it by eye -- an unnamed count would be an assertion.

Reads the tarball read-only, via the SOURCES.md recipe.  Writes only .temp/.

Usage: python3 .temp/mgr168/enclosing_fn.py [--selftest]
"""
import hashlib
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from item48_decide import load_index                       # noqa: E402

SURVEY = os.path.join(ROOT, ".temp", "mgr", "batch", "fixsurvey.json")


def CSV_PATH():
    """The corpus index, as `item48_decide.py` resolves it. ⚠ Read through the
    module so the two files cannot drift apart on the path."""
    import item48_decide
    return item48_decide.CSV

TARBALL = os.environ.get(
    "PHP500_TARBALL",
    "/home/apt/repos_common/php-in-safe-rust/.app-tests/.temp/oracle/"
    "build-5.0.0/php-5.0.0.tar.gz")
TARBALL_SHA = ("5783e0c0ba94f165633a565fe73a83e59cf17b6880ef95fa8f936dc"
               "6301d6919")

# A definition header at column 0: an identifier followed by `(`, not ending in
# `;` (that would be a prototype), not a control keyword.
DEFN = re.compile(r"^([A-Za-z_][\w \t\*]*?)\b([A-Za-z_]\w*)\s*\(")
NOT_A_FN = {"if", "for", "while", "switch", "return", "else", "do", "sizeof"}

_cache = {}


def check_tarball():
    if not os.path.exists(TARBALL):
        return f"MISSING: {TARBALL}"
    h = hashlib.sha256()
    with open(TARBALL, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    got = h.hexdigest()
    return "ok" if got == TARBALL_SHA else f"SHA MISMATCH: {got}"


def read_file(path):
    """The SOURCES.md recipe, cached in-process."""
    if path in _cache:
        return _cache[path]
    try:
        out = subprocess.run(
            ["tar", "-xzOf", TARBALL, f"php-5.0.0/{path}"],
            capture_output=True, timeout=120)
        lines = out.stdout.decode("utf-8", "replace").splitlines() if out.returncode == 0 else None
    except Exception:
        lines = None
    _cache[path] = lines
    return lines


def enclosing_fn(path, line):
    """Best-effort enclosing function name for `path:line`, or None."""
    lines = read_file(path)
    if not lines or line < 1 or line > len(lines):
        return None
    for i in range(min(line, len(lines)) - 1, -1, -1):
        m = DEFN.match(lines[i])
        if not m:
            continue
        name = m.group(2)
        if name in NOT_A_FN:
            continue
        if lines[i].rstrip().endswith(";"):
            continue                       # a prototype, not a definition
        return name
    return None


def main():
    if "--selftest" in sys.argv:
        return selftest()

    status = check_tarball()
    print(f"tarball: {status}")
    # ⛔ item 149: report and return 0, in capitals. The REFUSAL is still a
    # refusal -- every citation must resolve against the pinned tarball and
    # nothing else (SOURCES.md) -- but the exit code now says "no verdict"
    # rather than an unfiled 2.
    miss = ([] if status.startswith("ok") else [f"the pinned tarball: {status}"])
    if not os.path.exists(CSV_PATH()):
        miss.append(f"{CSV_PATH()}  (the corpus index, in php-in-safe-rust)")
    if not os.path.exists(SURVEY):
        miss.append(f"{SURVEY}  (gitignored; regenerate with "
                    f"`python3 .tasks-php/fixsurvey.py`)")
    if miss:
        print("=" * 78)
        print("⛔⛔ NOT RUN -- NOT A PASS. NO VERDICT WAS REACHED.")
        print("=" * 78)
        for m in miss:
            print(f"    missing  {m}")
        print("  ⚠ F69's `24 of 30 by enclosing function` is NOT reproduced by")
        print("    this run and must not be quoted from it.")
        print("  ⛔ A MISSING INPUT IS NOT A REFUTATION (item 149).")
        return 0

    idx = load_index()
    rows = json.load(open(SURVEY))["rows"]
    spread = {ph: recs for ph, recs in rows.items()
              if len({r["sha"] for r in recs if r.get("sha")}) > 1}

    print("\n" + "=" * 78)
    print("SPREAD ROWS BY ENCLOSING FUNCTION  (the §G1 question, asked properly)")
    print("=" * 78)
    print(f"\n{'row':7} {'ids':>4} {'fix':>4} {'file':>5} {'fn':>4}  {'verdict':22} functions")
    print("-" * 78)

    tally = {"fns==ids": [], "fns<ids": [], "unresolved": []}
    detail = {}
    for ph in sorted(spread, key=lambda p: int(re.sub(r"\D", "", p))):
        recs = spread[ph]
        ids = [r["id"] for r in recs if r.get("id")]
        fixes = {r["sha"] for r in recs if r.get("sha")}
        files, fns, misses = set(), set(), 0
        names = []
        for i in ids:
            rec = idx.get(i)
            if not rec or not rec[1]:
                misses += 1
                names.append(f"{i}=?")
                continue
            f, ln = rec[1].rsplit(":", 1)
            files.add(f)
            fn = enclosing_fn(f, int(ln))
            if fn:
                fns.add((f, fn))
                names.append(fn)
            else:
                misses += 1
                names.append(f"{os.path.basename(f)}:{ln}=?")
        if misses:
            v, key = f"⚠ {misses} unresolved", "unresolved"
        elif len(fns) == len(ids):
            v, key = "✅ distinct functions", "fns==ids"
        else:
            v, key = f"⚠ {len(fns)} fns / {len(ids)} ids", "fns<ids"
        tally[key].append(ph)
        detail[ph] = names
        print(f"{ph:7} {len(ids):4} {len(fixes):4} {len(files):5} {len(fns):4}  "
              f"{v:22} {' '.join(sorted(set(names)))[:70]}")

    print("\n" + "=" * 78)
    print("SUMMARY")
    print("=" * 78)
    tot = sum(len(v) for v in tally.values())
    for k in ("fns==ids", "fns<ids", "unresolved"):
        print(f"  {k:12} {len(tally[k]):3} of {tot}   {' '.join(tally[k])}")

    print("\n⚠ `fns==ids` means EVERY id on that row sits in a DIFFERENT")
    print("  function of 5.0.0.  Under PROTOCOL_PHP.md §G1 -- a distinct fix is")
    print("  evidence for DIFFERENT -- those rows assert one mechanism across")
    print("  N functions AND N upstream fixes.  That is not a kill (admission")
    print("  is C-side only) and not automatically a split; it is an UNPAID")
    print("  AUDIT, and open item 35 already names it.")

    print("\n-- the two rows that gate the temporal axis --")
    for ph in ("ph61", "ph73", "ph64"):
        if ph in detail:
            print(f"  {ph}: {' | '.join(detail[ph])}")
        else:
            recs = rows.get(ph, [])
            ids = [r["id"] for r in recs if r.get("id")]
            got = []
            for i in ids:
                rec = idx.get(i)
                if rec and rec[1]:
                    f, ln = rec[1].rsplit(":", 1)
                    got.append(enclosing_fn(f, int(ln)) or f"{f}:{ln}=?")
            print(f"  {ph}: {' | '.join(got)}   (not a spread row)")
    return 0


def selftest():
    ok = True

    def check(name, got, want):
        nonlocal ok
        if got != want:
            ok = False
        print(f"  [{'PASS' if got == want else '**FAIL**'}] {name}: "
              f"got {got!r}, want {want!r}")

    status = check_tarball()
    print(f"tarball: {status}")
    if not status.startswith("ok"):
        # ⛔⛔ ITEM 149. This used to `return 2` under the words "CANNOT
        # SELFTEST". 2 is neither the filed pass nor an adjudicated red, and a
        # reader sees an exit code before prose. The pinned tarball lives in
        # ANOTHER repo's scratch, so its absence is the EXPECTED state of a
        # clean checkout -- a check that reddens when a sibling repo is cleaned
        # is reporting on that repo (probes/ph66_djbx33a_collide.py's argument).
        # ⚠⚠ AND rc=0 HERE IS NOT A PASS. It is "no verdict was reached", which
        # is why the message says so in capitals. A silent 0 would be the worse
        # of the two defects.
        print("=" * 74)
        print("⛔⛔ NOT RUN -- NOT A PASS. NO VERDICT WAS REACHED.")
        print("=" * 74)
        print("  The pinned php-5.0.0 tarball is unavailable, so no arm ran.")
        print("  It lives in php-in-safe-rust's gitignored scratch; set")
        print("  $PHP500_TARBALL to point at a copy whose sha256 is the pin.")
        print("  ⚠ F69's `24 of 30 by enclosing function` is NOT reproduced by")
        print("    this run and must not be quoted from it.")
        print("  ⛔ A MISSING INPUT IS NOT A REFUTATION (item 149).")
        return 0

    print("\nN1  MUST-NOT-FIRE: a known function resolves to its own name.")
    print("    zend_alloc.c:234 is _safe_emalloc -- the SECOND")
    print("    ZEND_SIGNED_MULTIPLY_LONG call site, the one F7 corrected the")
    print("    manager on (:295 is _ecalloc, a DIFFERENT function).")
    check("zend_alloc.c:234", enclosing_fn("Zend/zend_alloc.c", 234), "_safe_emalloc")

    print("N2  MUST-FIRE: the two lines F7 confused MUST come back as two")
    print("    DIFFERENT functions -- if they do not, this probe cannot see")
    print("    the exact distinction it exists to make")
    a = enclosing_fn("Zend/zend_alloc.c", 234)
    b = enclosing_fn("Zend/zend_alloc.c", 295)
    check("different fns", a != b, True)
    check(":295 is _ecalloc", b, "_ecalloc")

    print("N3  MUST-NOT-FIRE: a control keyword is never returned as a function")
    check("no keywords", bool(set(NOT_A_FN) & {enclosing_fn('Zend/zend_alloc.c', 234)}), False)

    print("N4  MUST-FIRE: a nonexistent file returns None, not a guess")
    check("bogus file", enclosing_fn("Zend/no_such_file.c", 10), None)

    print("N5  MUST-FIRE: a line past EOF returns None")
    check("past EOF", enclosing_fn("Zend/zend_alloc.c", 10**7), None)

    print("N6  MUST-FIRE: the tarball read is not silently empty (F35's shape --")
    print("    'found nothing' and 'looked in the wrong place' look identical)")
    check("file has lines", len(read_file("Zend/zend_alloc.c") or []) > 100, True)

    print("\n" + ("ALL PASS" if ok else "**SOME FAILED -- do not trust the run**"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main() or 0)
