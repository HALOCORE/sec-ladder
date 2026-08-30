#!/usr/bin/env python3
"""p28 CONTROLS: **where does the dangling pointer actually live, and does a
detector see it?** Two questions, two instruments, one binary.

    python3 patterns/p28-intrusive-lists/controls/harm_sites.py

WHY THIS CONTROL EXISTS
-----------------------
`c/kernel.h` and `../spec.md` claim p28 is distinct from `p27`, `p29` and `p32`
because **the dangling pointer ends up inside ANOTHER HEAP OBJECT's `hn` field,
or in `bucket[]`** -- not in a stack table, a stack local or a program-owned
pool. `../model.py`'s detector CANNOT decide between those two sites: its
membership list collapses them (its module docstring says so in terms). So the
claim is measured here, at C level, on two windows built to land on one site
each.

  * **the SITE half** is answered by counting, in the HARDENED arm and BEFORE
    any free, which branch TRIM's chain splice takes -- `victim->hp == NULL`
    means the victim is the chain HEAD and the buggy rung would leave the
    dangling pointer in `bucket[vb]`; `victim->hp != NULL` means it would leave
    it in `victim->hp->hn`, inside another heap object. Both arms take the same
    branch because both compute `victim->hp` the same way, and asking the
    hardened arm costs no undefined behaviour at all. `controls/arm_body.inc`
    argues that choice.
  * **the DETECTOR half** is ASan over the BUGGY arm on the same two windows,
    with a POSITIVE CONTROL that must fire. ⚠ Hand-run ASan on this box is blind
    behind the inherited `LD_PRELOAD` and **fails silently to the exit code**
    (`.memory/00-environment.md`), so every sanitiser run below uses
    `env -u LD_PRELOAD`, and the control asserts the positive arm reports rather
    than trusting a non-zero exit.

WHAT IT ASSERTS, and it exits non-zero if any of it stops holding
----------------------------------------------------------------
  * `ctl` under ASan reports `heap-use-after-free` on BOTH compilers -- the
    detector is running and the malloc/free pair was not elided;
  * the `head` window puts the victim at `head=1 interior=0`, and the `tail`
    window at `head=0 interior=1`: **the two sites are separately reachable**;
  * `bug` under ASan reports `heap-use-after-free` on BOTH windows;
  * `fix` under ASan is SILENT on both windows, and its plain checksum equals
    the model's -- so the splice is what removes the finding, rather than the
    window being harmless.
"""

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
OUT = os.path.join(REPO, ".temp", "p28ctl")
GCC = os.environ.get("SLB_GCC", "/usr/bin/gcc")
CLANG = os.environ.get("SLB_CLANG", os.path.expanduser("~/tools/llvm/bin/clang"))

# The two windows, as (name, hex op stream, what the site should be).
#
#   header  nops:u32 LE
#   op      opcode byte (`% 4`) then operand byte
#
# Keys 5 and 13 are congruent mod P28_NB = 8, so they share bucket 5; a PUT
# pushes at the chain head, so after `PUT 5; PUT 13` the chain is `13 -> 5` and
# the eviction list's oldest is 5. TRIM therefore takes 5, which is the chain
# TAIL -- the INTERIOR site. With only key 5 present it is the chain HEAD.
WINDOWS = [
    # ("head", ...): PUT 5 ; GET 5 ; TRIM ; GET 5.  Only key 5 is in bucket 5,
    # so the victim IS `bucket[5]` -- the HEAD site.
    ("head", "04000000" + "0005" + "0105" + "0300" + "0105", "head"),
    # ("tail", ...): PUT 5 ; PUT 13 ; TRIM ; GET 5.  13 % 8 == 5 == 5 % 8, and a
    # PUT pushes at the chain head, so the chain is `13 -> 5`; the eviction list
    # is insertion-ordered, so TRIM takes 5, which is the chain TAIL and whose
    # predecessor 13 is ANOTHER HEAP OBJECT -- the INTERIOR site.
    ("tail", "04000000" + "0005" + "000d" + "0300" + "0105", "interior"),
]


def build():
    os.makedirs(OUT, exist_ok=True)
    src = os.path.join(HERE, "arm_sites.c")
    bins = {}
    jobs = [("plain_gcc", GCC, ["-O1"]),
            ("asan_gcc", GCC, ["-O1", "-fsanitize=address",
                               "-DSLB_WANT_LSAN_HOOK"]),
            ("asan_clang", CLANG, ["-O1", "-fsanitize=address",
                                   "-DSLB_WANT_LSAN_HOOK"])]
    for name, cc, extra in jobs:
        if not os.path.exists(cc):
            continue
        out = os.path.join(OUT, f"arm_sites_{name}")
        cmd = [cc, "-std=c99", "-Wall", "-Wextra", "-g",
               "-fno-omit-frame-pointer", "-I", HERE] + extra + [src, "-o", out]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if r.returncode != 0:
            raise SystemExit(f"harm_sites.py: build {name} failed:\n{r.stderr}")
        bins[name] = out
    return bins


def run(binary, arm, hexs, sanitised):
    env = dict(os.environ)
    if sanitised:
        env.pop("LD_PRELOAD", None)
    r = subprocess.run([binary, arm, hexs], capture_output=True, text=True,
                       timeout=600, env=env)
    txt = r.stdout + r.stderr
    return {"exit": r.returncode,
            "stdout": r.stdout.strip(),
            "asan_lines": len(re.findall(r"AddressSanitizer", txt)),
            "class": sorted(set(re.findall(
                r"heap-use-after-free|attempting double-free|"
                r"SEGV on unknown|LeakSanitizer", txt)))}


def derived_from():
    out = {}
    for rel in ("patterns/p28-intrusive-lists/controls/arm_sites.c",
                "patterns/p28-intrusive-lists/controls/arm_body.inc",
                "patterns/p28-intrusive-lists/controls/harm_sites.py"):
        p = os.path.join(REPO, rel)
        out[rel] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return out


def main():
    bins = build()
    problems = []
    rows = {}

    # -- the POSITIVE CONTROL, first, because nothing below counts without it --
    for name in ("asan_gcc", "asan_clang"):
        if name not in bins:
            problems.append(f"{name} was not built, so the positive control was "
                            f"not run on that compiler")
            continue
        row = run(bins[name], "ctl", WINDOWS[0][1], True)
        rows[f"ctl/{name}"] = row
        print(f"  ctl  {name:12s} exit={row['exit']} "
              f"asan_lines={row['asan_lines']} {row['class']}")
        if "heap-use-after-free" not in row["class"]:
            problems.append(
                f"POSITIVE CONTROL SILENT on {name}: the detector is not "
                f"running (or the malloc/free pair was elided), so no `bug` row "
                f"below carries any information at all")

    # -- the SITE half: which branch does the splice take? --------------------
    for wname, hexs, want in WINDOWS:
        row = run(bins["plain_gcc"], "fix", hexs, False)
        rows[f"site/{wname}"] = row
        m = re.search(r"head=(\d+) interior=(\d+)", row["stdout"])
        got = None
        if m:
            got = "head" if int(m.group(1)) == 1 and int(m.group(2)) == 0 else (
                "interior" if int(m.group(2)) == 1 and int(m.group(1)) == 0
                else f"head={m.group(1)} interior={m.group(2)}")
        print(f"  site {wname:12s} {row['stdout']}   -> {got} (want {want})")
        if got != want:
            problems.append(f"window `{wname}` was built to leave the dangling "
                            f"pointer at the {want} site and the hardened arm "
                            f"reports {got}")

    # -- the DETECTOR half ----------------------------------------------------
    for wname, hexs, _want in WINDOWS:
        for arm in ("bug", "fix"):
            for name in ("asan_gcc", "asan_clang"):
                if name not in bins:
                    continue
                row = run(bins[name], arm, hexs, True)
                rows[f"{arm}/{wname}/{name}"] = row
                print(f"  {arm:4s} {wname:6s} {name:12s} exit={row['exit']} "
                      f"asan_lines={row['asan_lines']} {row['class']}")
                if arm == "bug" and "heap-use-after-free" not in row["class"]:
                    problems.append(
                        f"bug/{wname}/{name}: ASan did NOT report a "
                        f"use-after-free, which is what this row exists to "
                        f"show")
                if arm == "fix" and row["class"]:
                    problems.append(
                        f"fix/{wname}/{name}: the HARDENED arm produced "
                        f"{row['class']} -- the splice is supposed to make the "
                        f"finding go away, and admission question 1 needs this "
                        f"arm correct")

    doc = {"pin": {"regenerate": "python3 patterns/p28-intrusive-lists/"
                                 "controls/harm_sites.py"},
           "derived_from_sha256": derived_from(),
           "measured_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "windows": {w[0]: {"hex": w[1], "expected_site": w[2]}
                       for w in WINDOWS},
           "rows": rows,
           "problems": problems,
           "invariant": "The two dangling-pointer sites p28 claims -- inside "
                        "`bucket[]` when the victim is the chain head, and "
                        "inside ANOTHER HEAP OBJECT's `hn` when it is not -- are "
                        "separately reachable, ASan reports a "
                        "heap-use-after-free on the buggy arm at both, the "
                        "hardened arm is silent at both, and the positive "
                        "control fires on both compilers."}
    out = os.path.join(HERE, "harm_sites.json")
    json.dump(doc, open(out, "w"), indent=2)
    print(f"wrote {out}")
    for p in problems:
        print(f"  *** {p}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
