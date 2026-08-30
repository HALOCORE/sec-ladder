#!/usr/bin/env python3
"""Derive the corpus composition table, and check the published copy against it.

WHY THIS EXISTS
---------------
The user's priority shift (`.memory/02-bench-rules.md`, last section) rests on
one table. It was **15 of 26 spatial against ONE temporal and ONE type** when
that priority was set; `p29` landed at TASK_139 and the temporal count is now 2.
⚠ **Do not maintain a count in this docstring -- run the script.** That table was
hand-audited by the manager and published in three places with no derivation. A hand-audited table over a growing tree is
the exact shape that rots -- RECAP's `p23` row sat wrong for about fifteen
tasks -- and this one is load-bearing for what gets built next.

WHAT IS MEASURED AND WHAT IS DECLARED, because the distinction is the point
---------------------------------------------------------------------------
MEASURED, from the tree, every run:

  * the POPULATION -- which patterns are built -- from TWO independent sources,
    `patterns/*/` and `results/gate/*.json`. They must agree exactly.
  * the BUG COLUMN per pattern, joined out of `.memory/06-catalogue.md`.
  * COMPLETENESS in both directions: every built pattern classified exactly
    once, and no classification naming a pattern that is not built.

DECLARED, by hand, in CLASSES below:

  * the CATEGORY each pattern's bug falls in.

⚠ **The category is a JUDGEMENT and this script does not launder it into a
measurement.** There is no machine-readable bug-class field to derive it from:
`spec.md`'s hashed `slb-contract` carries `requires`/`ensures`, and TASK_126
established that `requires` is a LENGTH bound in 26 of 26 and never mentions
buffer contents -- so the contract cannot discriminate spatial from temporal.
Adding a field to `spec.md` would change `contract_sha256` and cost a full
re-gate of every pattern.

So the honest artefact is this one: the judgement is written down once, printed
next to the catalogue's own bug text so a reader can audit it in one command,
and mechanically prevented from going stale as the tree grows.

WHAT WOULD MAKE THIS FAIL -- ask this before believing any check here
--------------------------------------------------------------------
  * a newly built pattern directory, unclassified        -> exit 1
    (this FIRED as designed when `p29` landed at TASK_139)
  * a classification naming a pattern that is not built  -> exit 1
  * `patterns/` and `results/gate/` disagreeing           -> exit 1
  * a pattern with no catalogue row                       -> exit 1
  * `--check`: the counts or the MEMBERSHIP published in
    `.memory/02-bench-rules.md` differing from the derived
    ones                                                  -> exit 1

The last arm is the anti-rot one, and it compares membership rather than only
totals: two errors that cancel in a total do not cancel in a set.

⚠ This file lives under `harness/tools/`, which `check.py`'s gate digest globs
NON-RECURSIVELY and therefore does not cover. Nothing here may be imported by
`check.py`/`measure.py`/`build.py` or it silently joins the digest and every
edit costs a sweep.

Usage:
  harness/tools/composition.py             # print the table
  harness/tools/composition.py --check     # + verify the published copy, exit 1 on drift
  harness/tools/composition.py --evidence  # + print each pattern's catalogue bug text
"""

import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CATALOGUE = os.path.join(ROOT, ".memory", "06-catalogue.md")
BENCH_RULES = os.path.join(ROOT, ".memory", "02-bench-rules.md")

# ---------------------------------------------------------------------------
# DECLARED. The judgement, and the only hand-written thing here.
#
# The category names the bug the pattern's spec.md actually SHIPS -- the thing
# c/kernel.c gets wrong that c/kernel_hardened.c gets right -- not the
# vocabulary of the pattern's title. `p36` is a function-pointer table and its
# bug is `op < NOPS`, an index out of a table, so it is spatial. `p22` walks a
# hash table and never leaves the object, so it is not.
# ---------------------------------------------------------------------------
CLASSES = {
    "spatial": (
        "an access outside the object: OOB read/write, index >= len, "
        "a length or offset check",
        ["p02", "p03", "p05", "p07", "p09", "p10", "p11", "p12", "p13",
         "p14", "p16", "p17", "p23", "p36", "p46"],
    ),
    "logical": (
        "wrong answer, memory-safe throughout: no rung leaves its object",
        ["p04", "p06", "p19"],
    ),
    "temporal": (
        "the ACCESS OUTLIVES THE OBJECT'S LIFETIME. ⚠ Not necessarily its "
        "STORAGE: the block may still be live and merely RECYCLED, or "
        "program-owned throughout. ⚠⚠ AND THE STATED TEST -- 'what does the "
        "SAFETY LINE ask?' -- DOES NOT REACH EVERY ROW HERE: p28's safety line "
        "asks nothing, it is a maintaining WRITE, so its class is read off the "
        "HARM instead. See CAVEATS['p28']",
        ["p27", "p28", "p29", "p32"],
    ),
    "type": (
        "the bytes are read at a type they were not written at",
        ["p38"],
    ),
    "resource": (
        "a resource acquired and not released; memory-safe while it happens",
        ["p42"],
    ),
    "side-channel": (
        "the answer is right and the way it was computed leaks it",
        ["p47"],
    ),
    "ub-not-mem": (
        "undefined behaviour that is not a memory-safety violation",
        ["p18"],
    ),
    "non-termination": (
        "the kernel does not stop",
        ["p22"],
    ),
    "aliasing": (
        "two live references to overlapping storage, one of them mutable",
        ["p08"],
    ),
    "calibration": (
        "no bug: the ladder measuring itself",
        ["p01"],
    ),
}

# Order the table prints in. Spatial first because its size is the result.
ORDER = ["spatial", "logical", "temporal", "type", "resource", "side-channel",
         "ub-not-mem", "non-termination", "aliasing", "calibration"]

# ---------------------------------------------------------------------------
# CAVEATS. Rows whose classification is defensible but not the whole story.
# Found by reading `--evidence`, which is what that arm is for.
#
# ⚠ The table counts SAFETY LINES -- the one conjunct `c/kernel.c` omits and
# `c/kernel_hardened.c` spells -- not bugs. A pattern can ship a second bug
# that the safety line does not name, and `p09` does.
# ---------------------------------------------------------------------------
CAVEATS = {
    "p28": "the safety line is NOT A TEST, it is a nine-line SPLICE -- a WRITE "
           "on the DESTROY path that maintains 'membership implies ownership' "
           "across two intrusive lists. ⚠⚠ So this table's own stated test "
           "(what does the safety line ASK?) DOES NOT APPLY, and `temporal` is "
           "read off the HARM instead: a real free() followed by a read or a "
           "write through a link naming the freed object -- ASan "
           "heap-use-after-free on both compilers, Miri UB on the faithful "
           "raw-pointer port. p28 is the first row whose safety line is a "
           "maintaining write rather than a guard. ⚠ The harm has an ALIASING "
           "limb and it is p32's caveat MIRRORED: here the aliasing (one "
           "object on two lists, p08's class) is the SETUP that makes the "
           "omission possible and the use-after-free is the HARM, where in p32 "
           "the aliasing IS the harm. ⚠⚠ And the row is the tree's first "
           "INVERSION: p27, p29 and p32 all keep a correct free discipline and "
           "put the missing check on the READ; p28's read path is correct and "
           "its DESTROY path is incomplete.",
    "p32": "the storage is NEVER deallocated -- a fixed pool with a LIFO free "
           "list, owned by the program from start to finish -- so 'temporal' "
           "here is about the OBJECT's lifetime, not the allocation's. Counted "
           "temporal because its SAFETY LINE is a generation test (`gen[h] != "
           "g`), which asks a lifetime question. ⚠ Its stale-FREE consequence "
           "is ALIASING (two live handles naming one block), overlapping p08's "
           "class; the aliasing is the HARM, the stale generation is the BUG.",
    "p09": "ships TWO bugs. The safety line is the omitted `q < nbits`, which "
           "is spatial and caught everywhere; the second is `q & 31`, which is "
           "invisible to a memory-safety proof and is NOT spatial. Counted "
           "spatial on its safety line.",
}


def fail(msg):
    print("FAIL: " + msg, file=sys.stderr)
    sys.exit(1)


def built_from_dirs():
    d = os.path.join(ROOT, "patterns")
    return {n.split("-")[0] for n in os.listdir(d)
            if re.fullmatch(r"p\d+-.+", n) and os.path.isdir(os.path.join(d, n))}


def built_from_gate():
    d = os.path.join(ROOT, "results", "gate")
    if not os.path.isdir(d):
        return None
    return {n.split("-")[0] for n in os.listdir(d) if re.fullmatch(r"p\d+-.+\.json", n)}


def catalogue_bugs():
    """pNN -> the catalogue's own bug text. The join is on the row id."""
    bugs = {}
    with open(CATALOGUE) as f:
        for line in f:
            m = re.match(r"\|\s*(p\d+)\s*\|", line)
            if not m:
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 3:
                bugs[m.group(1)] = cells[2]
    return bugs


def derive():
    dirs = built_from_dirs()
    gate = built_from_gate()
    if gate is not None and gate != dirs:
        fail("patterns/ and results/gate/ disagree on the population: "
             "only in patterns/ = %s, only in gate = %s"
             % (sorted(dirs - gate), sorted(gate - dirs)))

    declared = {}
    for cat, (_desc, ids) in CLASSES.items():
        for pid in ids:
            if pid in declared:
                fail("%s is classified twice: %s and %s" % (pid, declared[pid], cat))
            declared[pid] = cat

    missing = sorted(dirs - set(declared))
    if missing:
        fail("built but unclassified: %s -- add them to CLASSES in %s"
             % (missing, os.path.relpath(__file__, ROOT)))
    phantom = sorted(set(declared) - dirs)
    if phantom:
        fail("classified but not built: %s" % phantom)

    bugs = catalogue_bugs()
    nocat = sorted(p for p in dirs if p not in bugs)
    if nocat:
        fail("built with no catalogue row: %s" % nocat)

    return dirs, declared, bugs


def render(dirs, declared):
    lines = []
    width = max(len(c) for c in ORDER)
    for cat in ORDER:
        ids = sorted(p for p in dirs if declared[p] == cat)
        if not ids:
            continue
        lines.append("%-*s %3d   %s" % (width, cat, len(ids), " ".join(ids)))
    return lines


def published():
    """Parse the table published in .memory/02-bench-rules.md.

    Its rows are `label  N   p.. p.. ..` inside a fenced block; the label is
    prose ("spatial (OOB read/write, index/bound)"), so the join is on the
    MEMBERSHIP, not on the label. A published row is (label, count, set(ids)).

    ⚠ The parse is SCOPED to the one fenced block that contains a `spatial`
    row. The first version of this function scanned the whole file, and matched
    a kernel-variant line elsewhere in it whose sha256 the `(?P<n>\\d+)` group
    happily read as a count of 9617137326358488304. A loose regex over a
    5000-line prose file finds something; scope it to the block or it lies.
    """
    if not os.path.exists(BENCH_RULES):
        return None
    with open(BENCH_RULES) as f:
        text = f.read()

    block = None
    for cand in re.findall(r"^```[^\n]*\n(.*?)^```", text, re.M | re.S):
        if re.search(r"^spatial\b", cand, re.M):
            if block is not None:
                fail("more than one fenced block in %s has a `spatial` row -- "
                     "the composition table is no longer unique"
                     % os.path.relpath(BENCH_RULES, ROOT))
            block = cand
    if block is None:
        return None

    rows = []
    cur = None
    for line in block.splitlines():
        m = re.match(r"^(?P<label>\S.*?)\s{2,}(?P<n>\d{1,3})\s+"
                     r"(?P<ids>p\d+(?:\s+p\d+)*)\s*$", line)
        if m:
            if cur:
                rows.append(cur)
            cur = [m.group("label").strip(), int(m.group("n")),
                   set(m.group("ids").split())]
            continue
        m2 = re.match(r"^\s{4,}(?P<ids>p\d+(?:\s+p\d+)*)\s*$", line)
        if m2 and cur:
            cur[2].update(m2.group("ids").split())
            continue
        if line.strip():
            fail("unparsed line in the published composition table: %r" % line)
    if cur:
        rows.append(cur)
    return rows or None


def check(dirs, declared):
    pub = published()
    if pub is None:
        fail("no composition table found in %s" % os.path.relpath(BENCH_RULES, ROOT))

    derived = {}
    for cat in ORDER:
        ids = frozenset(p for p in dirs if declared[p] == cat)
        if ids:
            derived[ids] = (cat, len(ids))

    problems = []
    seen = set()
    for label, n, ids in pub:
        key = frozenset(ids)
        if key not in derived:
            problems.append("published row %r (%d: %s) matches no derived class"
                            % (label, n, " ".join(sorted(ids))))
            continue
        cat, cnt = derived[key]
        seen.add(key)
        if n != cnt:
            problems.append("published row %r says %d, derived %s has %d"
                            % (label, n, cat, cnt))
    for key, (cat, cnt) in derived.items():
        if key not in seen:
            problems.append("derived class %s (%d: %s) is not published"
                            % (cat, cnt, " ".join(sorted(key))))

    if problems:
        for p in problems:
            print("FAIL: " + p, file=sys.stderr)
        print("FAIL: the published composition table has drifted from the tree.",
              file=sys.stderr)
        sys.exit(1)
    print("OK: published composition table matches the tree (%d patterns, %d classes)"
          % (len(dirs), len(derived)))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true",
                    help="verify .memory/02-bench-rules.md's copy; exit 1 on drift")
    ap.add_argument("--evidence", action="store_true",
                    help="print each pattern's catalogue bug text next to its class")
    ap.add_argument("--json", action="store_true", help="emit the table as JSON")
    args = ap.parse_args()

    dirs, declared, bugs = derive()

    if args.json:
        out = {"patterns": len(dirs),
               "classes": {cat: sorted(p for p in dirs if declared[p] == cat)
                           for cat in ORDER
                           if any(declared[p] == cat for p in dirs)}}
        print(json.dumps(out, indent=2))
    else:
        print("composition of the %d BUILT patterns, by the bug each spec.md ships"
              % len(dirs))
        print()
        for line in render(dirs, declared):
            print("  " + line)
        print()
        print("  derived from patterns/*/ and results/gate/*.json (which must agree);")
        print("  the CATEGORY per pattern is declared in CLASSES and audited with --evidence.")
        print("  the table counts SAFETY LINES, not bugs -- see the caveats below.")
        for pid in sorted(CAVEATS):
            if pid in dirs:
                print()
                print("  caveat %s: %s" % (pid, CAVEATS[pid]))

    if args.evidence:
        print()
        print("evidence -- the catalogue's own bug text, so the judgement is auditable:")
        print()
        for cat in ORDER:
            ids = sorted(p for p in dirs if declared[p] == cat)
            if not ids:
                continue
            print("  %s -- %s" % (cat, CLASSES[cat][0]))
            for pid in ids:
                txt = re.sub(r"\s+", " ", bugs[pid])
                txt = re.sub(r"[*`⚠✅~]", "", txt).strip()
                print("    %-5s %s" % (pid, txt[:96]))
            print()

    if args.check:
        check(dirs, declared)


if __name__ == "__main__":
    main()
