#!/usr/bin/env python3
"""p32 CONTROLS: **is `c/kernel_hardened.c` `c/kernel.c` plus the safety line and
nothing else?** Measured on the SHIPPED files, by preprocessing both and
diffing.

    python3 patterns/p32-free-list-pool/controls/safety_line.py

WHY THIS EXISTS AND WHY IT IS NOT AN `#include`
-----------------------------------------------
`.memory/02-bench-rules.md`'s admission criterion 5 is *"`c/kernel_hardened.c`
differs from `c/kernel.c` by the SAFETY LINE and nothing else"*, and `TASK_143`
made that claim mechanical by writing ONE kernel body and `#include`-ing it
twice with `SLB_HARDEN` 0 and 1. ⚠ **That construction is not available to
a shipped rung, and the reason is a gate check rather than a convention:**
`harness/check.py`'s `forbidden` audit reads the rung sources as TEXT
(`rung_sources` -> `exec_code` -> `spelling_matches`), and a `forbidden` hit is
one of the few things in stage 0b that can FAIL the gate. A kernel body moved
into an `.inc` would be in neither C rung's text, so a forbidden spelling could
sit in it unseen -- which is exactly the honest-refactor escape route
`harness/check.py::forbidden_only_sources` names and closes for `c/kernel.h`.

So the two C rungs are written out in full, and this control makes the same
claim by MEASUREMENT instead: it preprocesses both with `cc -E -P`, strips
comments and blank lines, and diffs. That is strictly stronger than the
include-twice construction, which makes the property true by fiat and therefore
cannot fail. **`controls/arm_body.inc` still ships the include-twice spelling**,
for the storage experiment, where nothing depends on it being the rung.

WHAT IT ASSERTS, and it exits non-zero if any of it stops holding
----------------------------------------------------------------
  * the preprocessed diff is a pure ADDITION -- `+N / -0`;
  * every added line is inside the safety line: the `gen[h] != g` test, its
    `v = SENT;`, and the braces that carry them;
  * the hardened file adds the token `gen[h] != g` exactly ONCE. ⚠ The
    N is printed and recorded but not pinned in `spec.md`, because a number a
    rebuild produces must not sit in a file the rebuild re-hashes
    (`.memory/02-bench-rules.md`).
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
    for rel in ("patterns/p32-free-list-pool/c/kernel.c",
                "patterns/p32-free-list-pool/c/kernel_hardened.c",
                "patterns/p32-free-list-pool/c/kernel.h",
                "patterns/p32-free-list-pool/controls/safety_line.py"):
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
    # `SENT` is a macro, so the preprocessed text says `251`.
    allowed = ("} else if (gen[h] != g) {", "else if (gen[h] != g)",
               "{", "}", "v = 251;")
    stray = [ln for ln in added if ln not in allowed]
    if stray:
        problems.append(f"added line(s) outside the safety line: {stray}")
    ngen = sum(1 for ln in added if "gen[h] != g" in ln)
    if ngen != 1:
        problems.append(f"the hardened cell adds `gen[h] != g` {ngen} time(s), "
                        f"expected exactly 1 -- FREE, READ and WRITE share the "
                        f"handle decode, so the omission is ONE source line")

    doc = {"pin": {"regenerate": "python3 patterns/p32-free-list-pool/controls/"
                                 "safety_line.py"},
           "derived_from_sha256": derived_from(),
           "measured_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "preprocessed_lines": {"kernel.c": len(a),
                                  "kernel_hardened.c": len(b)},
           "added": added,
           "removed": removed,
           "gen_conjunct_sites": ngen,
           "problems": problems,
           "invariant": "The preprocessed difference between the two C rungs is "
                        "a pure ADDITION consisting of the safety line alone, "
                        "and it adds `gen[h] != g` at exactly ONE site. The "
                        "line COUNT is printed and recorded, never pinned in "
                        "spec.md."}
    out = os.path.join(HERE, "safety_line.json")
    json.dump(doc, open(out, "w"), indent=2)
    print(f"wrote {out}")
    for p in problems:
        print(f"  *** {p}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
