#!/usr/bin/env python3
"""p35 CONTROLS: **is `c/kernel_hardened.c` `c/kernel.c` with two statements
REORDERED and nothing else?** Measured on the SHIPPED files, by preprocessing
both and diffing.

    python3 patterns/p35-tagged-union/controls/safety_line.py

WHY THIS EXISTS AND WHY IT IS NOT AN `#include`
-----------------------------------------------
`.memory/02-bench-rules.md`'s admission criterion 5 is *"`c/kernel_hardened.c`
differs from `c/kernel.c` by the SAFETY LINE and nothing else"*, and `TASK_143`
made that claim mechanical by writing ONE kernel body and `#include`-ing it
twice with `SLB_HARDEN` 0 and 1 (`.temp/t143/p35/body.inc`). ⚠ **That
construction is not available to a shipped rung, and the reason is a gate check
rather than a convention** (`p32` found it first): `harness/check.py`'s
`forbidden` audit reads the rung sources as TEXT (`rung_sources` -> `exec_code`
-> `spelling_matches`), and a `forbidden` hit is one of the few things in stage
0b that can FAIL the gate. A kernel body moved into an `.inc` would be in
neither C rung's text, so a forbidden spelling could sit in it unseen -- the
honest-refactor escape route `harness/check.py::forbidden_only_sources` names
and closes for `c/kernel.h`.

So the two C rungs are written out in full and this control makes the claim by
MEASUREMENT instead. That is strictly stronger than the include-twice
construction, which makes the property true by fiat and therefore cannot fail.

⚠⚠ **p35's SAFETY LINE IS A SEQUENCING CONSTRAINT, WHICH IS A THIRD SHAPE FOR
THIS TREE** -- `p27`'s is a CONJUNCT and `p13`'s is a STORE -- so the invariant
this control asserts is NOT `p32`'s *"a pure ADDITION, `+N / -0`"*. It is a
**PURE REORDER**: the two preprocessed files have the SAME MULTISET of lines,
the diff is `+2 / -2`, and each moved line is a tag store.

WHAT IT ASSERTS, and it exits non-zero if any of it stops holding
----------------------------------------------------------------
  * the two preprocessed files have the same LINE COUNT;
  * their line MULTISETS are equal, i.e. nothing was added or deleted;
  * the diff is `+2 / -2`, at two sites;
  * every moved line is a tag store, `cells[idx].tag = <n>;` -- and the tag
    values are `2` (`P35_T_PTR`) and `3` (`P35_T_DBL`), which is the two SET
    arms that have a failure path and not the one that has none;
  * in the HARDENED file each moved line sits AFTER a payload store and inside
    the `if (navail > 0)` block, and in the BUGGY file it sits BEFORE that
    `if`. ⚠ This is the part a line-count check cannot see, and it is the whole
    property, so it is checked positionally against the preprocessed text.

⚠ The line COUNT is printed and recorded but not pinned in `spec.md`, because a
number a rebuild produces must not sit in a file the rebuild re-hashes
(`.memory/02-bench-rules.md`).
"""

import collections
import difflib
import hashlib
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
COMMON = os.path.join(REPO, "common")
GCC = os.environ.get("SLB_GCC", "/usr/bin/gcc")

SRCS = [os.path.join(PDIR, "c", "kernel.c"),
        os.path.join(PDIR, "c", "kernel_hardened.c")]


def preprocessed(path):
    """`cc -E -P`, then drop blank lines. `-P` already suppresses line markers;
    the compiler's own preprocessor is used rather than a regex so that what is
    diffed is what the compiler compiles."""
    r = subprocess.run([GCC, "-std=c99", "-E", "-P", "-I", COMMON,
                        "-I", os.path.join(PDIR, "c"), path],
                       capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        raise SystemExit(f"safety_line.py: cc -E failed on {path}:\n{r.stderr}")
    return [ln.rstrip() for ln in r.stdout.splitlines() if ln.strip()]


def derived_from():
    out = {}
    for rel in ("patterns/p35-tagged-union/c/kernel.c",
                "patterns/p35-tagged-union/c/kernel_hardened.c",
                "patterns/p35-tagged-union/c/kernel.h",
                "patterns/p35-tagged-union/controls/safety_line.py"):
        p = os.path.join(REPO, rel)
        out[rel] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return out


def _tag_sites(lines):
    """Every `cells[idx].tag = <n>;` line, as `(index, stripped text)`."""
    return [(i, ln.strip()) for i, ln in enumerate(lines)
            if ln.strip().startswith("cells[idx].tag =")]


def _context(lines, i, back=4, fwd=2):
    lo, hi = max(0, i - back), min(len(lines), i + fwd + 1)
    return [lines[k].strip() for k in range(lo, hi)]


def tag_context(lines):
    """`{tag store text: [surrounding stripped lines]}` for the two tag stores
    that move. Pure, so `--selftest` can drive it."""
    out = {}
    for i, txt in _tag_sites(lines):
        if txt in ("cells[idx].tag = 2;", "cells[idx].tag = 3;"):
            out[txt] = _context(lines, i)
    return out


def positional_problems(buggy, hardened):
    """**The half a line count cannot see: WHERE each moved line sits.**

    A pure function of the two preprocessed line lists, so `--selftest` can
    feed it the pair the other way round and require it to complain -- which is
    the must-fire arm this check would otherwise not have.

      BUGGY     each moved tag store is IMMEDIATELY FOLLOWED by the budget test
                `if (navail > 0)`, i.e. published before the payload can land.
      HARDENED  each moved tag store is IMMEDIATELY PRECEDED by a payload store
                `cells[idx].u.*`, i.e. published after it.
    """
    probs = []
    for txt in ("cells[idx].tag = 2;", "cells[idx].tag = 3;"):
        for label, lines, want in (("kernel.c", buggy, "buggy"),
                                   ("kernel_hardened.c", hardened, "hardened")):
            hit = [i for i, s in _tag_sites(lines) if s == txt]
            if len(hit) != 1:
                probs.append(f"{label}: `{txt}` appears {len(hit)} time(s), "
                             f"expected exactly 1")
                continue
            i = hit[0]
            nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
            prv = lines[i - 1].strip() if i > 0 else ""
            if want == "buggy" and not nxt.startswith("if (navail > 0)"):
                probs.append(
                    f"kernel.c: `{txt}` is NOT immediately before "
                    f"`if (navail > 0)` (next line {nxt!r}), so the BUGGY "
                    f"ordering -- publish the tag, THEN test the budget -- is "
                    f"not what this rung spells")
            if want == "hardened" and not prv.startswith("cells[idx].u."):
                probs.append(
                    f"kernel_hardened.c: `{txt}` is NOT immediately preceded by "
                    f"a payload store `cells[idx].u.*` (previous line {prv!r}), "
                    f"so the tag is not published AFTER the payload and the "
                    f"safety line is absent")
    return probs


def selftest():
    """MUST-FIRE ARM. Feed `positional_problems` the two files the OTHER way
    round: the hardened text presented as the buggy rung and vice versa. A
    check that cannot fail is not a check (`.memory/03-measurement.md` entry
    19), and the multiset/line-count half above is BLIND to a swap -- both
    files have the same lines, so `+2 / -2` and `multiset_equal` hold in either
    direction. Only the positional half sees it.

    ⚠ A cell that RAISES is reported as a failed cell with its exception text,
    never allowed to crash."""
    a, b = (preprocessed(s) for s in SRCS)
    cells = []
    try:
        good = positional_problems(a, b)
    except Exception as e:                                  # noqa: BLE001
        good = [f"RAISED {type(e).__name__}: {e}"]
    cells.append(("shipped order (must NOT fire)", len(good) == 0, good[:2]))
    try:
        swapped = positional_problems(b, a)
    except Exception as e:                                  # noqa: BLE001
        swapped = [f"RAISED {type(e).__name__}: {e}"]
        cells.append(("SWAPPED order (must FIRE)", False, swapped))
    else:
        cells.append(("SWAPPED order (must FIRE)", len(swapped) == 4,
                      swapped[:2]))
    # the line-count half is deliberately shown to be BLIND to the same swap
    import collections as _c
    blind = (_c.Counter(x.strip() for x in a) == _c.Counter(x.strip()
                                                            for x in b))
    cells.append(("multiset check is BLIND to the swap (must be True)",
                  blind, []))
    ok = 0
    for label, good_cell, ev in cells:
        print(f"  {'ok  ' if good_cell else 'FAIL'} {label:52s} {ev}")
        ok += bool(good_cell)
    print(f"{ok}/{len(cells)} cell(s) as designed")
    return 0 if ok == len(cells) else 1


def main():
    a, b = (preprocessed(s) for s in SRCS)
    added, removed = [], []
    for ln in difflib.unified_diff(a, b, "kernel.c", "kernel_hardened.c",
                                   lineterm="", n=0):
        if ln.startswith("+++") or ln.startswith("---") or ln.startswith("@@"):
            continue
        if ln.startswith("+"):
            added.append(ln[1:].strip())
        elif ln.startswith("-"):
            removed.append(ln[1:].strip())

    print(f"  preprocessed kernel.c          {len(a)} line(s)")
    print(f"  preprocessed kernel_hardened.c {len(b)} line(s)")
    print(f"  diff  +{len(added)} / -{len(removed)}")
    for ln in removed:
        print(f"    - {ln}")
    for ln in added:
        print(f"    + {ln}")

    problems = []
    ma = collections.Counter(ln.strip() for ln in a)
    mb = collections.Counter(ln.strip() for ln in b)
    if ma != mb:
        problems.append(
            f"the two preprocessed files do NOT have the same multiset of "
            f"lines, so the difference is not a pure REORDER: "
            f"only in kernel.c {sorted((ma - mb).elements())}, "
            f"only in kernel_hardened.c {sorted((mb - ma).elements())}")
    if (len(added), len(removed)) != (2, 2):
        problems.append(f"the diff is +{len(added)} / -{len(removed)}, expected "
                        f"+2 / -2 -- one moved tag store per SET arm with a "
                        f"failure path, and there are two such arms")
    want = {"cells[idx].tag = 2;", "cells[idx].tag = 3;"}
    if set(added) != want or set(removed) != want:
        problems.append(f"the moved lines are not the two tag stores: "
                        f"added {sorted(set(added))}, removed "
                        f"{sorted(set(removed))}, expected {sorted(want)} on "
                        f"both sides. `2` is P35_T_PTR and `3` is P35_T_DBL; "
                        f"`1` (P35_T_INT) must NOT move, because SET_INT has "
                        f"no failure path")

    problems += positional_problems(a, b)
    ctx = {"kernel.c": tag_context(a), "kernel_hardened.c": tag_context(b)}

    doc = {"pin": {"regenerate": "python3 patterns/p35-tagged-union/controls/"
                                 "safety_line.py"},
           "derived_from_sha256": derived_from(),
           "measured_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "preprocessed_lines": {"kernel.c": len(a),
                                  "kernel_hardened.c": len(b)},
           "added": added,
           "removed": removed,
           "multiset_equal": ma == mb,
           "context_buggy": ctx["kernel.c"],
           "context_hardened": ctx["kernel_hardened.c"],
           "selftest": "python3 patterns/p35-tagged-union/controls/safety_line.py --selftest -- the must-fire arm: the positional check FIRES on the two files presented the other way round, and the multiset half is blind to that swap",
           "problems": problems,
           "invariant": "The preprocessed difference between the two C rungs is "
                        "a PURE REORDER: same line multiset, +2 / -2, and the "
                        "two moved lines are the P35_T_PTR and P35_T_DBL tag "
                        "stores. In c/kernel.c each sits immediately BEFORE the "
                        "`if (navail > 0)`; in c/kernel_hardened.c each sits "
                        "immediately AFTER the payload store inside it. The "
                        "line COUNT is printed and recorded, never pinned in "
                        "spec.md."}
    out = os.path.join(HERE, "safety_line.json")
    json.dump(doc, open(out, "w"), indent=2)
    print(f"wrote {out}")
    for p in problems:
        print(f"  *** {p}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
        sys.exit(selftest())
    sys.exit(main())
