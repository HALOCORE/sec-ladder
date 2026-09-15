#!/usr/bin/env python3
"""ph97 — does `f7326d627962` apply to pristine 5.0.0, and WHAT BYTES does it leave?

    python3 patterns-php/ph97-optarg-unwritten/controls/r1h_backport.py

=============================================================================
WHY THIS IS A CONTROL AND NOT A SENTENCE IN `NOTES.md`
=============================================================================
⚠⚠ **`git apply --check` HAS LIED ON THIS PROJECT, LIVE.** `ph55` NOTES §5:
`--check` returned 0 and the real apply returned 0 with *Skipped patch* having
moved no bytes, because the scratch path was **gitignored in the enclosing
repository**. So this control does three things rather than one:

  1. checks that the patch **BINDS** — its `From` sha must match its filename,
     `RECAP_PHP.md` **F115**'s three mis-bound cached patches;
  2. runs `git apply --check` **and** the real apply, in a standalone
     `git init` repo over the pristine file only, and reports the hunk header
     verbatim;
  3. takes the verdict **FROM THE BYTES** — it reads the post-image line back
     and compares it to the patch's own `+` line.

⭐ And it reproduces the gitignore trap on every run (`gitignore_trap`), so a
future `git` that fixes the behaviour surfaces as a CHANGED NUMBER rather than
as a stale paragraph.

⚠ The tarball is read-only here and is never written to.
"""

import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
sys.path.insert(0, HERE)
import _pin  # noqa: E402

SCRATCH = os.path.join(REPO, ".temp", "php97", "r1h")
PATCH = os.path.join(HERE, "f7326d627962.patch")
TARBALL = os.environ.get(
    "PHP500_TARBALL",
    "/home/apt/repos_common/php-in-safe-rust/.app-tests/.temp/oracle/build-5.0.0/php-5.0.0.tar.gz")
CFILE = "ext/mbstring/mbstring.c"
POST_LINE = 3219


def sh(cmd, cwd=None):
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    return r.returncode, (r.stdout + r.stderr)


def pristine():
    r = subprocess.run(["tar", "-xzOf", TARBALL, "php-5.0.0/" + CFILE],
                       capture_output=True)
    assert r.returncode == 0, "cannot read the pristine tarball"
    return r.stdout


def _repo(d, ignore=False):
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(os.path.join(d, os.path.dirname(CFILE)))
    open(os.path.join(d, CFILE), "wb").write(pristine())
    sh(["git", "init", "-q", "."], cwd=d)
    if ignore:
        open(os.path.join(d, ".gitignore"), "w").write("ext/\n")
    sh(["git", "add", "-A", "-f" if ignore else "."], cwd=d)
    sh(["git", "-c", "user.email=x", "-c", "user.name=x", "commit", "-qm", "p"],
       cwd=d)
    return d


def main():
    os.makedirs(SCRATCH, exist_ok=True)
    rec = {"patch": os.path.relpath(PATCH, REPO), "problems": []}

    txt = open(PATCH).read()
    m = re.match(r"From ([0-9a-f]{40}) ", txt)
    rec["from_sha"] = m.group(1) if m else None
    rec["filename_prefix"] = os.path.basename(PATCH).split(".")[0]
    rec["binds"] = bool(m and m.group(1).startswith(rec["filename_prefix"]))
    print(f"  binds        : {rec['binds']}  (From {rec['from_sha']}, file "
          f"{rec['filename_prefix']})")
    if not rec["binds"]:
        rec["problems"].append(
            "the patch does not BIND: its `From` sha does not match its "
            "filename, which is F115's three mis-bound cached patches")

    plus = [l[1:] for l in txt.splitlines()
            if l.startswith("+") and not l.startswith("+++")]
    minus = [l[1:] for l in txt.splitlines()
             if l.startswith("-") and not l.startswith("---")]
    rec["patch_plus_lines"] = plus
    rec["patch_minus_lines"] = minus
    print(f"  hunk size    : {len(plus)} insertion(s), {len(minus)} deletion(s)")
    if len(plus) != 1 or len(minus) != 1:
        rec["problems"].append(
            f"this row's whole claim about the R1h is that it is ONE LINE; the "
            f"patch carries {len(plus)} insertions and {len(minus)} deletions")

    d = _repo(os.path.join(SCRATCH, "d0"))
    rc, out = sh(["git", "apply", "--check", "-v", PATCH], cwd=d)
    rec["check_rc"] = rc
    hh = [l.strip() for l in out.splitlines() if "Hunk #" in l]
    rec["check_hunk"] = hh[0] if hh else None
    print(f"  --check      : rc={rc}  {rec['check_hunk']}")

    before = open(os.path.join(d, CFILE), "rb").read()
    rc2, out2 = sh(["git", "apply", PATCH], cwd=d)
    after = open(os.path.join(d, CFILE), "rb").read()
    rec["apply_rc"] = rc2
    rec["bytes_moved"] = before != after
    line = after.decode("latin-1").splitlines()[POST_LINE - 1]
    rec["post_image_line"] = line
    rec["post_image_lineno"] = POST_LINE
    rec["post_image_matches_patch"] = (line == plus[0]) if plus else False
    print(f"  apply        : rc={rc2}  bytes_moved={rec['bytes_moved']}")
    print(f"  :{POST_LINE} after   : {line!r}")
    print(f"  equals patch + line: {rec['post_image_matches_patch']}")
    if not rec["bytes_moved"]:
        rec["problems"].append("the apply moved NO BYTES -- --check is not the "
                               "test, the bytes are (ph55 NOTES §5)")
    if not rec["post_image_matches_patch"]:
        rec["problems"].append(
            f"the post-image line at :{POST_LINE} is {line!r}, which is not the "
            f"patch's own `+` line {plus[0]!r}")

    # ---- the gitignore trap, reproduced ---------------------------------
    g = _repo(os.path.join(SCRATCH, "d1"), ignore=True)
    # hide the file from git's index the way an enclosing .gitignore does
    sh(["git", "rm", "--cached", "-q", CFILE], cwd=g)
    sh(["git", "-c", "user.email=x", "-c", "user.name=x", "commit", "-qm", "rm"],
       cwd=g)
    b2 = open(os.path.join(g, CFILE), "rb").read()
    rc3, _ = sh(["git", "apply", "--check", PATCH], cwd=g)
    rc4, out4 = sh(["git", "apply", PATCH], cwd=g)
    a2 = open(os.path.join(g, CFILE), "rb").read()
    rec["gitignore_trap"] = {"check_rc": rc3, "apply_rc": rc4,
                             "bytes_moved": b2 != a2,
                             "skipped": "Skipped patch" in out4}
    print(f"  gitignore trap: check_rc={rc3} apply_rc={rc4} "
          f"bytes_moved={b2 != a2} skipped={rec['gitignore_trap']['skipped']}")
    print("  ⚠ the trap is RECORDED, not asserted: whether this git still has "
          "the behaviour ph55 hit is a fact about git, and the number moving is "
          "the signal.")

    rec.update(_pin.pin(["c/kernel.c", "c/kernel_hardened.c"],
                        "python3 controls/r1h_backport.py",
                        "seconds; reads the tarball, writes only under .temp/"))
    with open(os.path.join(HERE, "r1h_backport.json"), "w") as f:
        json.dump(rec, f, indent=1)
        f.write("\n")
    print(f"\nwrote controls/r1h_backport.json -- {len(rec['problems'])} problem(s)")
    for p in rec["problems"]:
        print("  ⛔ " + p)
    return 1 if rec["problems"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
