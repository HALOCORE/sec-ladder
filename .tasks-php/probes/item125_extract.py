#!/usr/bin/env python3
"""ITEM 125's CENSUS, AT *ITEM* GRANULARITY -- the population `item125_demoted.py`
adjudicates.  Written by `TASK_PHP_063` §6.3 and PROMOTED out of `.temp/` when
`_063` landed.

⚠⚠ PROMOTED ON PURPOSE, AND THE PROMOTION IS THE POINT.  `_063` §7.2 ruled that
the genuinely uncovered case is **a GENERATOR in `.temp/` with no committed twin
and no validator role** -- neither `citecheck.py`'s §F6 arm nor its §H arm can
see one.  This file produced the 27-item population that `item125_demoted.py`
hard-codes; leaving it in auto-`rm`-able scratch would make that 27 a number
nobody can re-derive, which is `F51`/`F99` exactly.

    python3 .tasks-php/probes/item125_extract.py


⛔ A LINE-based grep misses `F123`'s own founding instance (`_051_REPORT.md`
§8.1: "cheapest remaining" on line 440, "and it is not done" on line 441).  So
this parses each report's uncertainty SECTION into ITEMS and applies the two
predicates to the whole item text.

Prints the SET with its members (F132), never just a count.

"""
import glob, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REPORTS = [p for p in sorted(glob.glob(os.path.join(ROOT, ".tasks-php", "TASK_PHP_*REPORT*.md")))
           if "063" not in os.path.basename(p)]

HEAD = re.compile(r'^(#{1,4}) .*?(UNSURE|UNCERTAIN|DID NOT DO|DIDN.T DO|NOT DONE|'
                  r'WHAT I (COULD|CANNOT|DID)|LEFT UNDONE|WHAT REMAINS|'
                  r'NOT \*\*IN\*\* THIS REPORT|IS \*\*NOT\*\* IN THIS REPORT)', re.I)
ANY  = re.compile(r'^#{1,4} ')
CHEAP  = re.compile(r'\b(cheap(est|ly)?|one (grep|command|line|read|run|probe)|'
                    r'a single (grep|command|run)|\d+ ?(seconds?|minutes?|min\b)|'
                    r'trivial|costs? (only|about|nothing|~)|free\b|minutes)', re.I)
UNDONE = re.compile(r'\b(not (yet )?(done|run|built|measured|checked|tried|verified|'
                    r'reproduced|attempted)|nobody has|no ?one has|never (been )?(done|run)|'
                    r'i did not|i have not|i could not|was not done|is not done|'
                    r'remains? (undone|open|owed)|still (owed|open|unmeasured)|'
                    r'un(run|measured|tested|checked|verified))', re.I)

def sections(path):
    lines = open(path, errors="replace").read().splitlines()
    out, cur, lvl = [], None, 0
    for ln in lines:
        m = HEAD.match(ln)
        if m:
            if cur is not None: out.append(cur)
            cur, lvl = [ln], len(m.group(1)); continue
        if cur is not None and ANY.match(ln):
            h = len(ln) - len(ln.lstrip('#'))
            if h <= lvl:
                out.append(cur); cur = None; continue
        if cur is not None: cur.append(ln)
    if cur is not None: out.append(cur)
    return out

def items(sec):
    """split a section body into numbered / bulleted items"""
    out, cur = [], []
    for ln in sec[1:]:
        if re.match(r'^\s{0,3}(\d+\.|[-*•]|\|)\s', ln) and cur:
            out.append("\n".join(cur)); cur = [ln]
        else:
            cur.append(ln)
    if cur: out.append("\n".join(cur))
    return [t for t in out if len(t.strip()) > 30]

members, nsec, nitem = [], 0, 0
for p in REPORTS:
    name = os.path.basename(p)
    for sec in sections(p):
        nsec += 1
        for it in items(sec):
            nitem += 1
            if CHEAP.search(it) and UNDONE.search(it):
                members.append((name, sec[0].strip()[:56], " ".join(it.split())[:200]))

print(f"reports scanned            : {len(REPORTS)}")
print(f"uncertainty SECTIONS found : {nsec}")
print(f"ITEMS inside them          : {nitem}")
print(f"MEMBERS (cheap AND undone) : {len(members)}")
print()
cur = None
for name, head, txt in members:
    if name != cur: print(f"\n=== {name} ==="); cur = name
    print(f"  [{head}]")
    print(f"     {txt}")
