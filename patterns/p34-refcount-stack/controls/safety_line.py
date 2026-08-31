#!/usr/bin/env python3
"""p34 CONTROLS: **is `c/kernel_hardened.c` `c/kernel.c` plus the safety line and
nothing else?** Measured on the SHIPPED files, by preprocessing both and
diffing -- and then measured a SECOND way, against the include-twice
construction in `arm_body.inc`.

    python3 patterns/p34-refcount-stack/controls/safety_line.py

WHY THERE ARE TWO MEASUREMENTS AND NOT ONE
------------------------------------------
`.memory/02-bench-rules.md`'s admission criterion 5 is *"`c/kernel_hardened.c`
differs from `c/kernel.c` by the SAFETY LINE and nothing else"*. `TASK_143` made
that claim mechanical by writing ONE kernel body and `#include`-ing it twice with
`SLB_HARDEN` 0 and 1. ⚠ **That construction is not available to a shipped rung**,
and the reason is a gate check rather than a convention: `harness/check.py`'s
`forbidden` audit reads the rung sources as TEXT (`rung_sources` -> `exec_code`
-> `spelling_matches`), and a `forbidden` hit is one of the few things in stage
0b that can FAIL the gate; a kernel body moved into an `.inc` would be in neither
C rung's text, so a forbidden spelling could sit in it unseen.

So the two C rungs are written out in full. p32 stops there and diffs them, which
proves the difference is SMALL but not that it is the INTENDED one. p34 adds the
second half:

  A. the preprocessed diff of the two SHIPPED files is a pure ADDITION of the
     retain, `+1 / -0` lines -- **the smallest safety line in this tree**;
  B. `arm_body.inc` preprocessed at `SLB_HARDEN 0` equals `c/kernel.c`
     preprocessed, and at `SLB_HARDEN 1` equals `c/kernel_hardened.c`
     preprocessed, **line for line**.

B is what says the two hand-written files really are one body plus one `#if`,
which A alone cannot say and the include-twice form alone cannot fail.

WHAT IT ASSERTS, and it exits non-zero if any of it stops holding
----------------------------------------------------------------
  * A's diff is a pure ADDITION -- `+N / -0`;
  * every added line is the retain itself: `t->rc = t->rc + 1;`;
  * the hardened file adds that statement exactly ONCE. ⚠ The N is printed and
    recorded but not pinned in `spec.md`, because a number a rebuild produces
    must not sit in a file the rebuild re-hashes (`.memory/02-bench-rules.md`);
  * B's two equalities hold exactly.
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
CDIR = os.path.join(PDIR, "c")
GCC = os.environ.get("SLB_GCC", "/usr/bin/gcc")

SHIPPED = [os.path.join(CDIR, "kernel.c"),
           os.path.join(CDIR, "kernel_hardened.c")]


def _cpp(path, defines=()):
    """`cc -E -P`, then drop blank lines. `-P` already suppresses line markers;
    the compiler's own preprocessor is used rather than a regex so that what is
    diffed is what the compiler compiles."""
    cmd = [GCC, "-std=c99", "-E", "-P", "-I", COMMON, "-I", CDIR]
    cmd += [f"-D{d}" for d in defines]
    cmd += [path]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        raise SystemExit(f"safety_line.py: cc -E failed on {path}:\n{r.stderr}")
    return [ln.rstrip() for ln in r.stdout.splitlines() if ln.strip()]


def _inc(harden, tmpdir):
    """Preprocess `arm_body.inc` at one `SLB_HARDEN` value, through a two-line
    wrapper written into `.temp/` (`CLAUDE.md` rule 1) rather than beside the
    control."""
    w = os.path.join(tmpdir, f"wrap_{harden}.c")
    with open(w, "w") as f:
        f.write(f"#define SLB_HARDEN {harden}\n")
        f.write(f'#include "{os.path.join(HERE, "arm_body.inc")}"\n')
    out = _cpp(w)
    os.unlink(w)
    return out


def derived_from():
    out = {}
    for rel in ("patterns/p34-refcount-stack/c/kernel.c",
                "patterns/p34-refcount-stack/c/kernel_hardened.c",
                "patterns/p34-refcount-stack/c/kernel.h",
                "patterns/p34-refcount-stack/controls/arm_body.inc",
                "patterns/p34-refcount-stack/controls/safety_line.py"):
        p = os.path.join(REPO, rel)
        out[rel] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return out


def main():
    tmpdir = os.path.join(REPO, ".temp", "p34ctl")
    os.makedirs(tmpdir, exist_ok=True)

    a, b = (_cpp(s) for s in SHIPPED)
    added, removed = [], []
    for ln in difflib.unified_diff(a, b, "kernel.c", "kernel_hardened.c",
                                   lineterm="", n=0):
        if ln.startswith("+++") or ln.startswith("---") or ln.startswith("@@"):
            continue
        if ln.startswith("+"):
            added.append(ln[1:].strip())
        elif ln.startswith("-"):
            removed.append(ln[1:].strip())

    print("A. the two SHIPPED files, preprocessed")
    print(f"     kernel.c          {len(a)} line(s)")
    print(f"     kernel_hardened.c {len(b)} line(s)")
    print(f"     diff  +{len(added)} / -{len(removed)}")
    for ln in added:
        print(f"       + {ln}")
    for ln in removed:
        print(f"       - {ln}")

    problems = []
    if removed:
        problems.append(f"the diff is not a pure ADDITION: {len(removed)} "
                        f"line(s) REMOVED, so the hardened cell is a rewrite "
                        f"and not the same kernel plus the retain")
    allowed = ("t->rc = t->rc + 1;",)
    stray = [ln for ln in added if ln not in allowed]
    if stray:
        problems.append(f"added line(s) outside the safety line: {stray}")
    nret = sum(1 for ln in added if "t->rc = t->rc + 1" in ln)
    if nret != 1:
        problems.append(f"the hardened cell adds `t->rc = t->rc + 1` "
                        f"{nret} time(s), expected exactly 1 -- DUP is the one "
                        f"site at which a reference is published")

    print("B. the include-twice construction reproduces both shipped files")
    inc0, inc1 = _inc(0, tmpdir), _inc(1, tmpdir)
    for tag, got, want in (("SLB_HARDEN 0 vs c/kernel.c", inc0, a),
                           ("SLB_HARDEN 1 vs c/kernel_hardened.c", inc1, b)):
        same = got == want
        print(f"     {tag:42s} {'IDENTICAL' if same else 'DIFFERS'} "
              f"({len(got)} vs {len(want)} line(s))")
        if not same:
            d = [ln for ln in difflib.unified_diff(want, got, "shipped",
                                                   "arm_body.inc", lineterm="",
                                                   n=0)][:20]
            for ln in d:
                print(f"       {ln}")
            problems.append(
                f"{tag}: arm_body.inc no longer reproduces the shipped file. "
                f"The two are kept byte-parallel BY HAND, so this is either an "
                f"edit made in one and not the other, or the shipped pair has "
                f"stopped being one body plus one `#if` -- which is the claim "
                f"this control exists to check")

    doc = {"pin": {"regenerate": "python3 patterns/p34-refcount-stack/controls/"
                                 "safety_line.py"},
           "derived_from_sha256": derived_from(),
           "measured_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "preprocessed_lines": {"kernel.c": len(a),
                                  "kernel_hardened.c": len(b),
                                  "arm_body.inc@0": len(inc0),
                                  "arm_body.inc@1": len(inc1)},
           "added": added,
           "removed": removed,
           "retain_sites": nret,
           "include_twice_reproduces_shipped": [inc0 == a, inc1 == b],
           "problems": problems,
           "invariant": "The preprocessed difference between the two shipped C "
                        "rungs is a pure ADDITION consisting of the retain "
                        "alone, added at exactly ONE site; and the "
                        "include-twice body in arm_body.inc preprocesses to "
                        "each shipped file exactly. The line COUNT is printed "
                        "and recorded, never pinned in spec.md."}
    out = os.path.join(HERE, "safety_line.json")
    json.dump(doc, open(out, "w"), indent=2)
    print(f"wrote {out}")
    for p in problems:
        print(f"  *** {p}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
