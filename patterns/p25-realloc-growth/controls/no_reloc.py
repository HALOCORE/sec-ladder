#!/usr/bin/env python3
"""p25 CONTROLS: **the C-mechanism novelty claim, re-derived from the tree.**

    python3 patterns/p25-realloc-growth/controls/no_reloc.py

`../c/kernel.h` and `../spec.md` both assert that no OTHER built row has an
allocation that MOVES while logically live, and that none holds a stale INTERIOR
pointer. ⚠ **Both manager axis claims previously written into a task file as fact
were FALSE** (`RECAP` item 4), so this row's is a census rather than a sentence,
and it is re-derived on every run rather than measured once by whoever wrote it.

WHAT IT COUNTS, over `patterns/*/c/*.c` and `patterns/*/c/*.h`, with comments
and string literals blanked so a `realloc` inside a doc comment cannot make the
census lie:

  * files that call `realloc` -- expected: **p25 only**;
  * files that call `malloc`, `calloc` or `aligned_alloc` -- reported, because
    "which rows allocate at all" is the honest denominator for the claim;
  * files that call `free` -- reported, because p25's distinction from p27, p29
    and p34 is that ITS retirement is not a `free` the program calls. ⚠ p25
    calls `free` twice, in the epilogue, and on the two CURRENT blocks; the
    retired ones are retired by `realloc`. That is the point and the census
    prints it rather than hiding it.

⚠ **A grep is not a semantic analysis and this file does not pretend otherwise.**
It settles "does any other C rung call `realloc`", which is decidable by token,
and it does NOT settle "does any other rung have an allocation that moves" --
that is an argument, it is in `../spec.md`, and the census is its load-bearing
premise rather than its whole content.
"""

import glob
import hashlib
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
PATTERNS = os.path.join(REPO, "patterns")

ME = "p25-realloc-growth"

_BLOCK = re.compile(r"/\*.*?\*/", re.S)
_LINE = re.compile(r"//[^\n]*")
_STR = re.compile(r'"(?:[^"\\\n]|\\.)*"')
_CHR = re.compile(r"'(?:[^'\\\n]|\\.)*'")


def exec_text(path):
    """The file with comments and string/char literals blanked, so a token in
    prose cannot be counted as a call. Same rule `harness/check.py::exec_code`
    applies to the rung sources."""
    s = open(path, encoding="utf-8", errors="replace").read()
    s = _BLOCK.sub(lambda m: "\n" * m.group(0).count("\n"), s)
    s = _LINE.sub("", s)
    s = _STR.sub('""', s)
    s = _CHR.sub("''", s)
    return s


def calls(text, name):
    return len(re.findall(r"\b%s\s*\(" % re.escape(name), text))


def derived_from():
    out = {"patterns/p25-realloc-growth/controls/no_reloc.py":
           hashlib.sha256(open(os.path.join(HERE, "no_reloc.py"), "rb").read())
           .hexdigest()}
    return out


def main():
    rows = []
    for d in sorted(glob.glob(os.path.join(PATTERNS, "p*", "c"))):
        pat = os.path.basename(os.path.dirname(d))
        r = {"pattern": pat, "realloc": 0, "malloc": 0, "calloc": 0,
             "aligned_alloc": 0, "free": 0, "files": 0}
        for f in sorted(glob.glob(os.path.join(d, "*.c"))
                        + glob.glob(os.path.join(d, "*.h"))):
            t = exec_text(f)
            r["files"] += 1
            for k in ("realloc", "malloc", "calloc", "aligned_alloc", "free"):
                r[k] += calls(t, k)
        rows.append(r)

    n_pat = len(rows)
    reloc = [r["pattern"] for r in rows if r["realloc"]]
    allocs = [r["pattern"] for r in rows
              if r["malloc"] or r["calloc"] or r["aligned_alloc"]]
    frees = [r["pattern"] for r in rows if r["free"]]

    print(f"  {n_pat} pattern(s) with a c/ directory")
    print(f"  call `realloc`                    : {len(reloc)}  {reloc}")
    print(f"  call malloc/calloc/aligned_alloc  : {len(allocs)}  {allocs}")
    print(f"  call `free`                       : {len(frees)}  {frees}")
    for r in rows:
        if r["realloc"] or r["malloc"] or r["calloc"] or r["free"]:
            print(f"    {r['pattern']:24s} realloc={r['realloc']} "
                  f"malloc={r['malloc']} calloc={r['calloc']} "
                  f"aligned_alloc={r['aligned_alloc']} free={r['free']}")

    problems = []
    if reloc != [ME]:
        problems.append(
            f"`realloc` is called by {reloc}, and p25's C-mechanism claim needs "
            f"it to be called by p25 alone. If another row has legitimately "
            f"grown one, p25's `spec.md` C-mechanism section and `c/kernel.h` "
            f"both have to be re-argued -- this is the census that says so")
    me = [r for r in rows if r["pattern"] == ME]
    if not me:
        problems.append(f"{ME} has no c/ directory in this tree")
    elif me[0]["realloc"] == 0:
        problems.append(f"{ME} itself calls `realloc` zero times, so this "
                        f"census is measuring the wrong tree")

    doc = {"pin": {"regenerate": "python3 patterns/p25-realloc-growth/controls/"
                                 "no_reloc.py"},
           "derived_from_sha256": derived_from(),
           "measured_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "n_patterns_with_c": n_pat,
           "realloc_callers": reloc,
           "allocating_patterns": allocs,
           "freeing_patterns": frees,
           "per_pattern": rows,
           "problems": problems,
           "invariant": "Exactly one pattern's C rungs call `realloc`, and it "
                        "is p25. Comments and string literals are blanked "
                        "first, so a `realloc` in prose cannot satisfy or "
                        "break the census. ⚠ This settles the TOKEN question, "
                        "not the semantic one: 'no other row has an allocation "
                        "that moves while live' is an argument in spec.md and "
                        "this is its load-bearing premise."}
    out = os.path.join(HERE, "no_reloc.json")
    json.dump(doc, open(out, "w"), indent=2)
    print(f"wrote {out}")
    for p in problems:
        print(f"  *** {p}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
