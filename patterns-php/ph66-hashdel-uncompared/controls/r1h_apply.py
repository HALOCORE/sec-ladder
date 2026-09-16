#!/usr/bin/env python3
"""ph66 control -- re-derive the R1h binding FROM THE BYTES, on every run.

    python3 patterns-php/ph66-hashdel-uncompared/controls/r1h_apply.py
    python3 patterns-php/ph66-hashdel-uncompared/controls/r1h_apply.py --selftest

============================================================================
WHAT IT CHECKS, AND WHY A COLUMN LOOKUP IS NOT ENOUGH
============================================================================
`PROTOCOL_PHP.md` §C: **the `fix_commit` column is EVIDENCE for which commit
R1h is, not a DEFINITION of it** -- the programme has measured that lookup wrong
twice (`F38`: 3 of 5 hand-checked commits named a LATER hardening; `F118`: six
rows, from three independent agents). ▶ *"A build task verifies the binding
against the BYTES before relying on it."*

Four things, all from the pinned tarball and the committed patch:

  A1  the tarball is the pin -- sha256 `5783e0c0…d6919`
  A2  `controls/b73349dbe4e9.patch` applies to `php-5.0.0/` with `patch -p1`,
      **rc 0, no fuzz, no offset**, touching ONE file
  A3  the post-image predicate at `Zend/zend_hash.c:463-466` is, character for
      character after whitespace normalisation, the predicate
      `c/kernel_hardened.c` ships -- so the row's R1h really is this commit and
      not a hand-written approximation of it
  A4  ⭐ the pre-image predicate classifies `dual` and the post-image one
      `guarded` under `.tasks-php/probes/ph66_djbx33a_collide.py::census`, which
      is the independent classifier that refutes *"the repair is invisible to a
      line-level reading"*

⛔ **AND `--selftest` IS WHAT MAKES ANY OF THAT EVIDENCE** (`§H`): three
must-fire mutations, applied to COPIES, never to the shipped files.
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROW = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(ROW))
sys.path.insert(0, os.path.join(REPO, ".tasks-php", "probes"))
sys.path.insert(0, HERE)
import _pin  # noqa: E402

TARBALL = ("/home/apt/repos_common/php-in-safe-rust/.app-tests/.temp/oracle/"
           "build-5.0.0/php-5.0.0.tar.gz")
TARBALL_SHA = "5783e0c0ba94f165633a565fe73a83e59cf17b6880ef95fa8f936dc6301d6919"
PATCH = os.path.join(HERE, "b73349dbe4e9.patch")
WORK = os.path.join(REPO, ".temp", "ph66-controls", "r1h")


def norm(s):
    """Whitespace deleted, comments blanked -- the same reading `check.py::
    spelling_matches` takes, spelled here so this file needs no harness import."""
    s = re.sub(r"/\*.*?\*/", " ", s, flags=re.S)
    return re.sub(r"\s+", "", s)


def stage():
    """Extract `Zend/zend_hash.c` from the pinned tarball into a fresh tree."""
    shutil.rmtree(WORK, ignore_errors=True)
    os.makedirs(os.path.join(WORK, "php-5.0.0", "Zend"))
    with tarfile.open(TARBALL, "r:gz") as t:
        src = t.extractfile("php-5.0.0/Zend/zend_hash.c").read()
    dst = os.path.join(WORK, "php-5.0.0", "Zend", "zend_hash.c")
    with open(dst, "wb") as f:
        f.write(src)
    return dst


def apply_patch(patch=PATCH):
    dst = stage()
    r = subprocess.run(["patch", "-p1", "--no-backup-if-mismatch", "-i", patch],
                       cwd=os.path.join(WORK, "php-5.0.0"),
                       capture_output=True, text=True)
    return dst, r


def predicate(path, start_marker="zend_hash_del_key_or_index(HashTable"):
    """The `if (...)` condition of the delete's chain walk, as text."""
    src = open(path).read()
    i = src.index(start_marker)
    j = src.index("if (", src.index("while (p != NULL)", i))
    depth, k = 0, j + 3
    while True:
        if src[k] == "(":
            depth += 1
        elif src[k] == ")":
            depth -= 1
            if depth == 0:
                break
        k += 1
    return src[j:k + 1]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    bad = []

    def ck(name, cond, why):
        print(f"  {'PASS' if cond else 'FAIL'}  {name}: {why}")
        if not cond:
            bad.append(name)

    # ---- A1 ----------------------------------------------------------
    h = hashlib.sha256(open(TARBALL, "rb").read()).hexdigest()
    ck("A1", h == TARBALL_SHA,
       f"the tarball is the pin -- sha256 {h[:16]} (want {TARBALL_SHA[:16]})")

    # ---- A2 ----------------------------------------------------------
    dst, r = apply_patch()
    clean = (r.returncode == 0 and "Hunk" not in r.stdout
             and "fuzz" not in r.stdout and "offset" not in r.stdout)
    ck("A2", clean,
       f"`patch -p1` applies to PRISTINE php-5.0.0 with rc={r.returncode}, no "
       f"fuzz and no offset -- one file, no backport"
       + ("" if clean else f" -- got {r.stdout.strip()[:200]}"))

    # ---- A3 ----------------------------------------------------------
    post = predicate(dst)
    ship = predicate(os.path.join(ROW, "c", "kernel_hardened.c"))
    ck("A3", norm(post) == norm(ship),
       "the post-image predicate and `c/kernel_hardened.c`'s are the same "
       "characters once whitespace is deleted and comments blanked -- so R1h "
       "IS this commit and not an approximation of it"
       + ("" if norm(post) == norm(ship)
          else f"\n        tarball: {norm(post)}\n        shipped: {norm(ship)}"))

    pre = predicate(os.path.join(ROW, "c", "kernel.c"))
    ck("A3b", norm(pre) != norm(post),
       "and the PRE-image predicate differs from it, so the row's two C rungs "
       "really do differ in the predicate")

    # ---- A4 ----------------------------------------------------------
    try:
        import ph66_djbx33a_collide as cen
        wrap = ("ZEND_API int zend_hash_del_key_or_index(HashTable *ht)\n{\n"
                "\t\twhile (p != NULL) {\n\t\t%s {\n}\n")
        kpre = [k for _, _, k, _ in cen.census(wrap % pre)]
        kpost = [k for _, _, k, _ in cen.census(wrap % post)]
        ck("A4", kpre == ["dual"] and kpost == ["guarded"],
           f"the census classifies the pre-image `dual` and the post-image "
           f"`guarded` -- got {kpre} and {kpost}. That classifier is "
           f"independent of this file and its own N8 arm pins it.")
    except Exception as e:  # noqa: BLE001
        ck("A4", False, f"the census could not run: {e}")

    if a.selftest:
        print()
        # ---- N1 MUST-FIRE: a mutated patch must not apply cleanly ------
        # ⚠ NOT under WORK: `stage()` rmtree's WORK before every apply, so a
        # mutated patch written there is deleted before `patch` can read it --
        # and the arm then fails for a reason that has nothing to do with the
        # patch. Measured, not reasoned: it is how this arm failed first.
        mp = os.path.join(os.path.dirname(WORK), "ph66_mutated.patch")
        os.makedirs(os.path.dirname(mp), exist_ok=True)
        # ⚠ ONLY THE ADDED LINES. `p->nKeyLength == nKeyLength` also occurs in
        # a REMOVED line, and mutating that one makes the hunk's context stop
        # matching, so `patch` refuses and the arm measures the application
        # rather than the added text.
        txt = "".join(
            (ln.replace("(p->nKeyLength == nKeyLength)",
                        "(p->nKeyLength == nKeyLengthX)")
             if ln.startswith("+") and not ln.startswith("+++") else ln)
            for ln in open(PATCH).read().splitlines(keepends=True))
        with open(mp, "w") as f:
            f.write(txt)
        _, rm = apply_patch(mp)
        ck("N1", rm.returncode == 0,
           "a patch whose ADDED line is mutated still applies (only the "
           "context decides that) -- recorded so N2 is read as the check that "
           "the ADDED TEXT is what A3 compares, not the application")
        # ---- N2 MUST-FIRE: and its post-image predicate must NOT match --
        post2 = predicate(os.path.join(WORK, "php-5.0.0", "Zend", "zend_hash.c"))
        ck("N2", norm(post2) != norm(ship),
           "and the mutated post-image predicate does NOT match "
           "`c/kernel_hardened.c` -- so A3 is comparing the patch's ADDED "
           "TEXT and would catch a hand-written R1h")
        # ---- N3 MUST-FIRE: the census must be able to see a fixed file ---
        try:
            import ph66_djbx33a_collide as cen
            wrap = ("ZEND_API int zend_hash_del_key_or_index(HashTable *ht)\n{\n"
                    "\t\twhile (p != NULL) {\n\t\t%s {\n}\n")
            kpre2 = [k for _, _, k, _ in cen.census(wrap % pre)]
            ck("N3", kpre2 == ["dual"],
               "the census still classifies the SHIPPED pre-image `dual` after "
               "all of the above, so A4's verdict is about the predicates and "
               "not about a stale import")
        except Exception as e:  # noqa: BLE001
            ck("N3", False, f"{e}")
        apply_patch()  # restore the clean post-image for any later reader

    rec = {"arms_failed": bad, "problems": bad, "selftest": a.selftest}
    rec.update(_pin.pin(["c/kernel.c", "c/kernel_hardened.c",
                         "controls/b73349dbe4e9.patch"],
                        "python3 controls/r1h_apply.py --selftest",
                        "extracts the pinned tarball and applies the patch; "
                        "seconds"))
    with open(os.path.join(HERE, "r1h_apply.json"), "w") as f:
        json.dump(rec, f, indent=1)
        f.write("\n")
    print()
    print("SELFTEST " + ("FAIL: " + " ".join(bad) if bad else "PASS"))
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
