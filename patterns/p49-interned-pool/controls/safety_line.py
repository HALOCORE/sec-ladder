#!/usr/bin/env python3
"""p49 CONTROLS: **is `c/kernel_hardened.c` `c/kernel.c` plus the safety line and
nothing else?** Measured on the SHIPPED files, by preprocessing both and
diffing.

    python3 patterns/p49-interned-pool/controls/safety_line.py

`.memory/02-bench-rules.md`'s admission criterion 5 is *"`c/kernel_hardened.c`
differs from `c/kernel.c` by the SAFETY LINE and nothing else"*. p32 measures it
by preprocessing both shipped files and diffing, and that is what this does.
⚠ p34 additionally ships an `arm_body.inc` include-twice construction; p49 does
not, and the reason is stated rather than left implicit: p34's safety line is ONE
STATEMENT, so a single body plus one `#if` is a faithful model of it. p49's is a
nine-line nested block that changes the CONTROL FLOW of the `else` arm around it
-- the `else { mem[roff[t]] = 0; v = 2; }` in `c/kernel.c` becomes the inner
`else` of the hardened block -- so an include-twice body would need the `#if` to
straddle a brace, which is exactly the construction that makes a preprocessed
diff unreadable. **The diff below is therefore NOT a pure addition, and this
control asserts what it IS instead.**

WHAT IT ASSERTS, and it exits non-zero if any of it stops holding
----------------------------------------------------------------
  * every REMOVED line is one of the two statements the hardened rung re-indents
    into its inner `else` (`mem[roff[t]] = 0;` and `v = 2;`) -- i.e. nothing is
    deleted, only moved;
  * every ADDED line belongs to the copy-on-write block;
  * the ownership test `if (rshd[t])` appears **exactly once** in
    `c/kernel_hardened.c` and **not at all** in `c/kernel.c`;
  * the write `mem[roff[t]] = 0;` appears in BOTH rungs -- the bug is not that
    the buggy rung writes somewhere else, it is that it does not ask first;
  * no line is added or removed outside the BREAK arm, which is checked by
    requiring the two files to be character-identical once the marked block is
    removed from the hardened one.
  * ⚠ The `+N / -M` counts are printed and recorded but **not pinned in
    `spec.md`**, because a number a rebuild produces must not sit in a file the
    rebuild re-hashes (`.memory/02-bench-rules.md`).
"""

import difflib
import hashlib
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
COMMON = os.path.join(REPO, "common")
CDIR = os.path.join(PDIR, "c")
GCC = os.environ.get("SLB_GCC", "/usr/bin/gcc")

BUG = os.path.join(CDIR, "kernel.c")
FIX = os.path.join(CDIR, "kernel_hardened.c")

#: The two statements the hardened rung MOVES rather than deletes: they are
#: re-indented into the inner `else` of the copy-on-write block.
MOVED = ("mem[roff[t]] = 0;", "v = 2;")

#: The ONE declaration the safety line adds: `j`, the copy loop's index. It is a
#: `-` line as well as a `+` line because C declares the whole list on one line,
#: so the pair is named here rather than counted as a deletion.
DECL_BUG = "uint8_t c, a, key, w;"
DECL_FIX = "uint8_t c, a, key, w, j;"


def _cpp(path):
    """`cc -E -P`, then drop blank lines. `-P` already suppresses line markers;
    the compiler's own preprocessor is used rather than a regex so that what is
    diffed is what the compiler compiles."""
    cmd = [GCC, "-std=c99", "-E", "-P", "-I", COMMON, "-I", CDIR, path]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        raise SystemExit(f"safety_line.py: cc -E failed on {path}:\n{r.stderr}")
    return [ln.rstrip() for ln in r.stdout.splitlines() if ln.strip()]


def _blank_comments(txt):
    """Blank C comments so a token census counts CODE. Same convention as
    `harness/check.py::exec_code`."""
    out, i, n = [], 0, len(txt)
    while i < n:
        if txt.startswith("/*", i):
            j = txt.find("*/", i + 2)
            j = n if j < 0 else j + 2
            out.append(" " * (j - i))
            i = j
        elif txt.startswith("//", i):
            j = txt.find("\n", i)
            j = n if j < 0 else j
            out.append(" " * (j - i))
            i = j
        else:
            out.append(txt[i])
            i += 1
    return "".join(out)


def _count(path, needle):
    code = _blank_comments(open(path).read())
    return len(re.findall(re.escape(needle), code.replace(" ", "")))


def derived_from():
    out = {}
    for rel in ("patterns/p49-interned-pool/c/kernel.c",
                "patterns/p49-interned-pool/c/kernel_hardened.c",
                "patterns/p49-interned-pool/c/kernel.h",
                "patterns/p49-interned-pool/controls/safety_line.py"):
        p = os.path.join(REPO, rel)
        out[rel] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return out


def main():
    a, b = _cpp(BUG), _cpp(FIX)
    added, removed = [], []
    for ln in difflib.unified_diff(a, b, "kernel.c", "kernel_hardened.c",
                                   lineterm="", n=0):
        if ln[:3] in ("+++", "---", "@@ ") or ln.startswith("@@"):
            continue
        if ln.startswith("+"):
            added.append(ln[1:].strip())
        elif ln.startswith("-"):
            removed.append(ln[1:].strip())

    print("the two SHIPPED files, preprocessed")
    print(f"     kernel.c          {len(a)} line(s)")
    print(f"     kernel_hardened.c {len(b)} line(s)")
    print(f"     diff  +{len(added)} / -{len(removed)}")
    for ln in added:
        print(f"       + {ln}")
    for ln in removed:
        print(f"       - {ln}")

    problems = []
    stray_removed = [ln for ln in removed if ln not in MOVED and ln != DECL_BUG]
    if DECL_BUG in removed and DECL_FIX not in added:
        problems.append(f"the declaration line changed from {DECL_BUG!r} but "
                        f"not to {DECL_FIX!r}")
    if stray_removed:
        problems.append(
            f"the hardened rung REMOVES line(s) that are not the two it "
            f"re-indents into its inner `else`: {stray_removed}. Nothing may be "
            f"deleted -- the safety line is an addition around a moved pair")

    # The ownership test: exactly one site in the hardened rung, none in the bug.
    guard = "if(rshd[t]){"
    n_fix = _count(FIX, guard)
    n_bug = _count(BUG, guard)
    write = "mem[roff[t]]=0;"
    w_fix, w_bug = _count(FIX, write), _count(BUG, write)
    print(f"\n     `if (rshd[t]) {{`  sites:  kernel.c {n_bug}   "
          f"kernel_hardened.c {n_fix}")
    print(f"     `mem[roff[t]] = 0;` sites: kernel.c {w_bug}   "
          f"kernel_hardened.c {w_fix}")
    if n_fix != 1:
        problems.append(f"the ownership test appears {n_fix} time(s) in "
                        f"c/kernel_hardened.c, expected exactly 1 -- BREAK is "
                        f"the one site at which the pool writes through a "
                        f"record's buffer")
    if n_bug != 0:
        problems.append(f"the ownership test appears {n_bug} time(s) in "
                        f"c/kernel.c, which is the rung that is supposed to "
                        f"omit it")
    if w_bug != 1 or w_fix != 2:
        problems.append(
            f"the write `mem[roff[t]] = 0;` appears {w_bug} time(s) in "
            f"c/kernel.c and {w_fix} in c/kernel_hardened.c; expected 1 and 2 "
            f"(the hardened rung writes it in both arms of the ownership test). "
            f"The bug is NOT that R1 writes somewhere else -- both rungs write "
            f"the same byte of the same array; it is that R1 does not ask "
            f"whether that byte is its to write")

    # Everything OUTSIDE the BREAK arm must be character-identical. Checked by
    # deleting the marked block from the hardened source and comparing the rest.
    fix_txt = open(FIX).read()
    # Replace the WHOLE ownership test -- `if (rshd[t]) { .. } else { BODY }` --
    # with BODY alone, which is exactly "delete the safety line". Anything left
    # over is a difference the safety line does not account for.
    m = re.search(r"\n( *)if \(rshd\[t\]\) \{\n.*?\n\1\} else \{\n(.*?)\n\1\}\n",
                  fix_txt, re.S)
    if m is None:
        problems.append("could not locate the marked copy-on-write block in "
                        "c/kernel_hardened.c, so the outside-the-arm equality "
                        "was not checked")
        outside_equal = None
    else:
        body = "\n".join(ln[4:] if ln.startswith("    ") else ln
                         for ln in m.group(2).splitlines())
        stripped = fix_txt[:m.start()] + "\n" + body + "\n" + fix_txt[m.end():]
        # The two files also differ in their header comments and in the `j`
        # declaration the copy loop needs; compare the STATEMENT text only.
        def stmts(t):
            t = _blank_comments(t)
            t = t.replace(DECL_FIX, DECL_BUG)
            return [ln.strip() for ln in t.splitlines() if ln.strip()]
        outside_equal = stmts(stripped) == stmts(open(BUG).read())
        print(f"     outside the BREAK arm, statement text identical: "
              f"{outside_equal}")
        if not outside_equal:
            d = [ln for ln in difflib.unified_diff(
                stmts(open(BUG).read()), stmts(stripped), "kernel.c",
                "kernel_hardened.c minus the block", lineterm="", n=0)][:24]
            for ln in d:
                print(f"       {ln}")
            problems.append(
                "with the copy-on-write block removed, c/kernel_hardened.c is "
                "NOT statement-identical to c/kernel.c -- so the two rungs "
                "differ somewhere other than the safety line, which is the "
                "claim this control exists to check")

    doc = {"pin": {"regenerate": "python3 patterns/p49-interned-pool/controls/"
                                 "safety_line.py"},
           "derived_from_sha256": derived_from(),
           "measured_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "preprocessed_lines": {"kernel.c": len(a),
                                  "kernel_hardened.c": len(b)},
           "added": added,
           "removed": removed,
           "guard_sites": {"kernel.c": n_bug, "kernel_hardened.c": n_fix},
           "write_sites": {"kernel.c": w_bug, "kernel_hardened.c": w_fix},
           "identical_outside_the_break_arm": outside_equal,
           "problems": problems,
           "invariant": "The preprocessed difference between the two shipped C "
                        "rungs is the copy-on-write block at the ONE site where "
                        "the cycle-breaker writes; nothing is deleted (the two "
                        "removed lines are re-indented into the block's inner "
                        "`else`, and the one further `-`/`+` pair is the copy "
                        "loop's index declaration); the ownership test appears "
                        "exactly once in the "
                        "hardened rung and never in the buggy one; the write "
                        "itself appears in BOTH; and with the block removed the "
                        "two files are statement-identical. The line COUNTS are "
                        "printed and recorded, never pinned in spec.md."}
    out = os.path.join(HERE, "safety_line.json")
    json.dump(doc, open(out, "w"), indent=2)
    print(f"wrote {out}")
    for p in problems:
        print(f"  *** {p}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
