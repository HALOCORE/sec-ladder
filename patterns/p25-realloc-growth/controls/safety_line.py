#!/usr/bin/env python3
"""p25 CONTROLS: **is `c/kernel_hardened.c` `c/kernel.c` plus the safety line and
nothing else?** Measured on the SHIPPED files, by preprocessing both and
diffing -- and then measured a SECOND way, against the include-twice
construction in `arm_body.inc`.

    python3 patterns/p25-realloc-growth/controls/safety_line.py

WHY THERE ARE TWO MEASUREMENTS AND NOT ONE
------------------------------------------
`.memory/02-bench-rules.md`'s admission criterion 5 is *"`c/kernel_hardened.c`
differs from `c/kernel.c` by the SAFETY LINE and nothing else"*. `TASK_143` made
that claim mechanical by writing ONE kernel body and `#include`-ing it twice with
`SLB_HARDEN` 0 and 1. ⚠ **That construction is not available to a shipped rung**
(`arm_body.inc`'s header says why), so the two C rungs are written out in full.
p32 stops there and diffs them, which proves the difference is SMALL but not that
it is the INTENDED one. p34 and p25 add the second half:

  A. the preprocessed diff of the two SHIPPED files is exactly the conjunct, the
     read moving inside it, and the re-derive it guards -- `+3 / -1`, net `+2`.
     ⚠ NOT a pure addition; see "WHAT IT ASSERTS" below, which is the body this
     header must keep matching (PROTOCOL rule 13);
  B. `arm_body.inc` preprocessed at `SLB_HARDEN 0` equals `c/kernel.c`
     preprocessed, and at `SLB_HARDEN 1` equals `c/kernel_hardened.c`
     preprocessed, **line for line**.

B is what says the two hand-written files really are one body plus one `#if`,
which A alone cannot say and the include-twice form alone cannot fail.

WHAT IT ASSERTS, and it exits non-zero if any of it stops holding
----------------------------------------------------------------
⚠⚠ **THE DIFF IS NOT A PURE ADDITION, AND THE FIRST VERSION OF THIS CONTROL
ASSERTED THAT IT WAS AND FAILED.** It is `+3 / -1`, net `+2`, and the removal is
not a deletion: **the read `v = (uint64_t)*cur;` MOVES** out of an unguarded
`else` and into the branch the conjunct guards. So what is checked is the exact
line multiset, which says more than a `+N / -0` shape would:

  * exactly ONE line is removed and it is the unguarded read
    `v = (uint64_t)*cur;`;
  * exactly THREE lines are added: the conjunct `} else if (curbase == toks) {`,
    that SAME read (now guarded), and the re-derive `v = (uint64_t)toks[curi];`;
  * the conjunct appears exactly ONCE. ⚠ The counts are printed and recorded but
    not pinned in `spec.md`, because a number a rebuild produces must not sit in
    a file the rebuild re-hashes (`.memory/02-bench-rules.md`);
  * B's two equalities hold exactly.

⚠ **`.temp/mgr155/` measured `+4 / -1` for a DIFFERENT hardened cell** -- the one
whose `else` folded a sentinel, which `../spec.md` refuses because it makes the
kernel's answer a function of the allocator. The shipped re-deriving cell is
`+3 / -1`. Quote this file's number, not that one.

⚠⚠ **WHAT THIS CONTROL DOES NOT SAY, and `../NOTES.md` 3c says it instead:** that
the shipped conjunct is a *sufficient* repair under the C standard. It is not --
C11 7.22.3.5p4 with DR 400 makes `cur` indeterminate after any `realloc`,
whether or not the block moved -- and `rederive.py` builds and prices the
unconditional re-derive that is.
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

# The exact preprocessed line multisets. `EXPECT_REMOVED` is the read LEAVING
# the unguarded `else`; the same text reappears in `EXPECT_ADDED`, guarded.
CONJUNCT = "} else if (curbase == toks) {"
UNGUARDED_READ = "v = (uint64_t)*cur;"
REDERIVE = "v = (uint64_t)toks[curi];"
EXPECT_REMOVED = [UNGUARDED_READ]
EXPECT_ADDED = [CONJUNCT, UNGUARDED_READ, REDERIVE]


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
    for rel in ("patterns/p25-realloc-growth/c/kernel.c",
                "patterns/p25-realloc-growth/c/kernel_hardened.c",
                "patterns/p25-realloc-growth/c/kernel.h",
                "patterns/p25-realloc-growth/controls/arm_body.inc",
                "patterns/p25-realloc-growth/controls/safety_line.py"):
        p = os.path.join(REPO, rel)
        out[rel] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return out


def main():
    tmpdir = os.path.join(REPO, ".temp", "p25ctl")
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
    if sorted(removed) != sorted(EXPECT_REMOVED):
        problems.append(f"the hardened cell REMOVES {removed!r}, and the only "
                        f"line it may remove is the unguarded read "
                        f"{EXPECT_REMOVED!r} -- which it removes because that "
                        f"read MOVES into the branch the conjunct guards. "
                        f"Anything else means the hardened cell is a rewrite "
                        f"rather than the same kernel plus the conjunct")
    if sorted(added) != sorted(EXPECT_ADDED):
        problems.append(f"the hardened cell ADDS {added!r}, and the only lines "
                        f"it may add are {EXPECT_ADDED!r} -- the conjunct, the "
                        f"read it now guards, and the re-derive")
    nconj = added.count(CONJUNCT)
    if nconj != 1:
        problems.append(f"the conjunct `{CONJUNCT}` is added {nconj} time(s), "
                        f"not once -- the safety line is supposed to be at ONE "
                        f"site")

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

    doc = {"pin": {"regenerate": "python3 patterns/p25-realloc-growth/controls/"
                                 "safety_line.py"},
           "derived_from_sha256": derived_from(),
           "measured_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "preprocessed_lines": {"kernel.c": len(a),
                                  "kernel_hardened.c": len(b),
                                  "arm_body.inc@0": len(inc0),
                                  "arm_body.inc@1": len(inc1)},
           "added": added,
           "removed": removed,
           "conjunct_sites": nconj,
           "include_twice_reproduces_shipped": [inc0 == a, inc1 == b],
           "problems": problems,
           "net_lines": len(added) - len(removed),
           "invariant": "The preprocessed difference between the two shipped C "
                        "rungs is exactly: the unguarded read leaves, and the "
                        "conjunct `curbase == toks`, that same read (now "
                        "guarded) and the re-derive `toks[curi]` arrive -- "
                        "+3 / -1, net +2, at exactly ONE site. It is NOT a "
                        "pure addition, because the read MOVES. And the "
                        "include-twice body in arm_body.inc preprocesses to "
                        "each shipped file exactly. The counts are printed and "
                        "recorded, never pinned in spec.md."}
    out = os.path.join(HERE, "safety_line.json")
    json.dump(doc, open(out, "w"), indent=2)
    print(f"wrote {out}")
    for p in problems:
        print(f"  *** {p}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
