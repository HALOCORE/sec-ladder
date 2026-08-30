#!/usr/bin/env python3
"""p28 CONTROLS: **is `c/kernel_hardened.c` `c/kernel.c` plus the safety line and
nothing else?** Measured on the SHIPPED files, by preprocessing both and
diffing.

    python3 patterns/p28-intrusive-lists/controls/safety_line.py

WHY THIS EXISTS AND WHY IT IS NOT AN `#include`
-----------------------------------------------
`.memory/02-bench-rules.md`'s admission criterion 5 is *"`c/kernel_hardened.c`
differs from `c/kernel.c` by the SAFETY LINE and nothing else"*, and `TASK_143`
made that claim mechanical by writing ONE kernel body and `#include`-ing it twice
with `SLB_HARDEN` 0 and 1. ⚠ **That construction is not available to a shipped
rung**, and the reason is a gate check rather than a convention:
`harness/check.py`'s `forbidden` audit reads the rung sources as TEXT
(`rung_sources` -> `exec_code` -> `spelling_matches`), and a `forbidden` hit is
one of the few things in stage 0b that can FAIL the gate. A kernel body moved
into an `.inc` would be in neither C rung's text, so a forbidden spelling could
sit in it unseen.

So the two C rungs are written out in full, and this control makes the same claim
by MEASUREMENT instead: it preprocesses both with `cc -E -P`, strips comments and
blank lines, and diffs. That is strictly stronger than the include-twice
construction, which makes the property true by fiat and therefore cannot fail.
**`controls/arm_body.inc` still ships the include-twice spelling**, for
`controls/harm_sites.py`, where nothing depends on it being the rung.

WHAT IT ASSERTS, and it exits non-zero if any of it stops holding
----------------------------------------------------------------
  * the preprocessed diff is a pure ADDITION -- `+N / -0`;
  * every added line is inside the safety line: the `vb` binding, the two
    `victim->hp` / `victim->hn` tests, their three assignments, the `else` and
    the braces;
  * the hardened file adds `victim->hp` exactly THREE times and `victim->hn`
    exactly FOUR -- the splice reads the victim's two chain links, tests each
    for `NULL`, and writes through both neighbours, at exactly ONE site because
    TRIM is the only path that forgets. ⚠ The first draft of this control said
    TWO and THREE and was wrong: `victim->hn->hp = victim->hp;` mentions each
    once more. The counts are transcribed from the measured diff below, which is
    what the control prints. ⚠ The N is printed and recorded but **not pinned
    in `spec.md`**, because a number a rebuild produces must not sit in a file
    the rebuild re-hashes (`.memory/02-bench-rules.md`).
"""

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
    for rel in ("patterns/p28-intrusive-lists/c/kernel.c",
                "patterns/p28-intrusive-lists/c/kernel_hardened.c",
                "patterns/p28-intrusive-lists/c/kernel.h",
                "patterns/p28-intrusive-lists/controls/safety_line.py"):
        p = os.path.join(REPO, rel)
        out[rel] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return out


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
    for ln in added:
        print(f"    + {ln}")
    for ln in removed:
        print(f"    - {ln}")

    problems = []
    if removed:
        problems.append(f"the diff is not a pure ADDITION: {len(removed)} "
                        f"line(s) REMOVED, so the hardened cell is a rewrite "
                        f"and not the same kernel plus a guard")
    # `P28_NB` is a macro, so the preprocessed text says `8`.
    allowed = ("{", "}", "else",
               "size_t vb = (size_t)(victim->key % 8);",
               "if (victim->hp != ((void *)0))",
               "victim->hp->hn = victim->hn;",
               "bucket[vb] = victim->hn;",
               "if (victim->hn != ((void *)0))",
               "victim->hn->hp = victim->hp;")
    stray = [ln for ln in added if ln not in allowed]
    if stray:
        problems.append(f"added line(s) outside the safety line: {stray}")
    nhp = sum(1 for ln in added if "victim->hp" in ln)
    nhn = sum(1 for ln in added if "victim->hn" in ln)
    if nhp != 3:
        problems.append(f"the hardened cell mentions `victim->hp` {nhp} "
                        f"time(s), expected 3 -- the predecessor test, the "
                        f"write THROUGH the predecessor, and the value handed "
                        f"to the successor")
    if nhn != 4:
        problems.append(f"the hardened cell mentions `victim->hn` {nhn} "
                        f"time(s), expected 4 -- the successor test, the two "
                        f"places the successor is spliced past the victim "
                        f"(`hp->hn` and `bucket[vb]`), and the write THROUGH "
                        f"the successor")

    doc = {"pin": {"regenerate": "python3 patterns/p28-intrusive-lists/"
                                 "controls/safety_line.py"},
           "derived_from_sha256": derived_from(),
           "measured_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "preprocessed_lines": {"kernel.c": len(a),
                                  "kernel_hardened.c": len(b)},
           "added": added,
           "removed": removed,
           "victim_hp_sites": nhp,
           "victim_hn_sites": nhn,
           "problems": problems,
           "invariant": "The preprocessed difference between the two C rungs is "
                        "a pure ADDITION consisting of the hash-chain splice "
                        "alone, at exactly ONE site -- TRIM. The line COUNT is "
                        "printed and recorded, never pinned in spec.md."}
    out = os.path.join(HERE, "safety_line.json")
    json.dump(doc, open(out, "w"), indent=2)
    print(f"wrote {out}")
    for p in problems:
        print(f"  *** {p}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
