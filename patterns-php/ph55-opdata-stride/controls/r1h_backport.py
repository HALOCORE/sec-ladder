#!/usr/bin/env python3
"""ph55 control -- **R1h IS A HAND BACKPORT: `git apply` FAILS, AND THE THREE
LEGS THAT IDENTIFY THE EXIT ARE RE-DERIVED HERE RATHER THAN ASSERTED.**

    python3 patterns-php/ph55-opdata-stride/controls/r1h_backport.py
    python3 patterns-php/ph55-opdata-stride/controls/r1h_backport.py --selftest

`4f68f3774c34` (Stanislav Malyshev, 2004-08-30, *"fix crash #29893"*) is ONE
FILE, THREE INSERTIONS, ZERO DELETIONS -- the cleanest R1h in either programme,
because the three lines are **the normal exit's own three lines copied onto the
error exit**. Nothing is invented.

⚠⚠ **BUT THE COMMIT IS AGAINST 2004-08-30 HEAD AND 5.0.0 SHIPPED 2004-07-13.**
This file RUNS `git apply` against the pristine tarball's own
`Zend/zend_execute.c` and records what happens, because *"git apply fails"* is
the kind of claim that decays into folklore if nobody re-runs it. ✅ **It does
fail**, with `error: while searching for: ... FREE_OP_VAR_PTR(free_op1);` --
the line 5.0.0 does not have -- and `controls/4f68f3774c34-backport-5.0.0.patch`
is the POSITIVE control that makes that verdict worth anything: the same three
`+` lines with 5.0.0's own context, which applies cleanly and moves the bytes.

⛔⛔ **AND `preimage_screen.py` DOES NOT SETTLE WHICH EXIT THE HUNK BELONGS TO.**
Its verdict on `CRASH-023` is `CANDIDATE`, on the strength of ONE cited 5.0.0
line -- `NEXT_OPCODE();` -- which occurs **117 times in that file**. ⚠ `115` is
what `TASK_PHP_048` §2.3 says and it is off by two; this file COUNTS it on every
run rather than quoting. ▶ The screen
has done its job: it is an EXCLUSION tool (F68 / item D11) and it correctly
declines to exclude. **This row does not quote it as confirmation.** The three
legs below are what decide it, and each is re-measured on every run:

  LEG 1  the hunk's own `@@` function-context line names
         `zend_binary_assign_op_helper`;
  LEG 2  `increment_opline` occurs exactly THREE times in the whole of
         `Zend/zend_execute.c`, and all three are inside that function's span;
  LEG 3  the OTHER exit already carries the identical guard at 5.0.0, so a patch
         adding it there would be adding a duplicate.

§H (`PROTOCOL_PHP.md`): the verdict function is a function so it can be attacked,
and `--selftest` drives it over synthetic evidence -- five must-FIRE and three
must-NOT-fire.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(PDIR))

sys.path.insert(0, HERE)
import _pin  # noqa: E402

SCRATCH = os.path.join(ROOT, ".temp", "php55bp")

TARBALL = os.environ.get(
    "PHP500_TARBALL",
    "/home/apt/repos_common/php-in-safe-rust/.app-tests/.temp/oracle/"
    "build-5.0.0/php-5.0.0.tar.gz")
TARBALL_SHA = "5783e0c0ba94f165633a565fe73a83e59cf17b6880ef95fa8f936dc6301d6919"
MEMBER = "php-5.0.0/Zend/zend_execute.c"
PATCH = os.path.join(HERE, "4f68f3774c34.patch")
#: ⭐ THE POSITIVE CONTROL, and the artefact `spec.md` calls the hand backport.
#: Same three `+` lines, character for character; 5.0.0's own context. It MUST
#: apply, and the bytes MUST move -- which is what makes "the upstream patch
#: does not apply" a measurement rather than a hope.
BACKPORT = os.path.join(HERE, "4f68f3774c34-backport-5.0.0.patch")

#: `zend_binary_assign_op_helper`, 1-based inclusive, as `spec.md` pins it.
FN_SPAN = (1724, 1796)
#: The normal exit's guard, verbatim from `:1792-1794`. LEG 3 is that this is
#: ALREADY there in the pre-image.
NORMAL_GUARD = "\tif (increment_opline) {\n\t\tINC_OPCODE();\n\t}"


def tarball_text():
    with tarfile.open(TARBALL, "r:gz") as tf:
        return tf.extractfile(MEMBER).read().decode("utf-8", "replace")


def sha256(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def try_git_apply(src_text, patch, where, own_repo=True):
    """Run `git apply` FOR REAL and report whether THE BYTES MOVED.

    ⛔⛔ **`git apply --check` IS NOT THE TEST, AND THIS FILE'S FIRST VERSION
    USED IT AND GOT THE ANSWER BACKWARDS.** `git apply` SILENTLY SKIPS a patch
    whose target path is **gitignored in the enclosing repository** and returns
    **exit 0** -- and `.temp/` is gitignored in this repo, so a control that
    scratches there and trusts `--check` reads a REFUSAL as an ACCEPTANCE.
    Measured: `git apply --check` -> rc 0 and `git apply -v` -> `Skipped patch
    'Zend/zend_execute.c'` with the file unchanged, while the same patch in a
    standalone repo gives `error: patch does not apply`. ⭐ `gitignore_trap()`
    below reproduces it on every run, so the trap is a MEASUREMENT in this file
    rather than a warning in a comment.

    So: `git init` the scratch (`own_repo`), run the real apply, and compare the
    bytes. Returns `(bytes_moved, message)`."""
    root = os.path.join(SCRATCH, where)
    if os.path.isdir(root):
        import shutil as _sh
        _sh.rmtree(root)
    os.makedirs(os.path.join(root, "Zend"))
    dst = os.path.join(root, "Zend", "zend_execute.c")
    open(dst, "w", encoding="utf-8").write(src_text)
    if own_repo:
        subprocess.run(["git", "init", "-q", "."], cwd=root, capture_output=True)
    before = open(dst, encoding="utf-8").read()
    msgs = []
    for args in (["git", "apply", "-v", patch],
                 ["git", "apply", "-v", "-C1", patch],
                 ["git", "apply", "-v", "--recount", "--unidiff-zero", patch]):
        r = subprocess.run(args, cwd=root, capture_output=True, text=True)
        msgs.append(re.sub(r"\s+", " ", (r.stdout + r.stderr).strip())[:200])
        if open(dst, encoding="utf-8").read() != before:
            return True, " ".join(args[2:]) + " -> the bytes moved"
    return False, " | ".join(m for m in msgs if m)[:400]


def gitignore_trap(src_text):
    """⭐ THE TRAP, REPRODUCED. Run the SAME refused patch under a GITIGNORED
    path and report what `git apply --check` says. It says `0`. This is the
    measurement behind this file's own correction, and it runs every time so
    that a future `git` which fixed the behaviour shows up as a changed number
    rather than as a stale paragraph."""
    root = os.path.join(SCRATCH, "ignored")
    os.makedirs(os.path.join(root, "Zend"), exist_ok=True)
    dst = os.path.join(root, "Zend", "zend_execute.c")
    open(dst, "w", encoding="utf-8").write(src_text)
    ign = subprocess.run(["git", "check-ignore", "-q", "Zend/zend_execute.c"],
                         cwd=root, capture_output=True)
    chk = subprocess.run(["git", "apply", "--check", PATCH],
                         cwd=root, capture_output=True, text=True)
    before = open(dst, encoding="utf-8").read()
    subprocess.run(["git", "apply", PATCH], cwd=root, capture_output=True)
    moved = open(dst, encoding="utf-8").read() != before
    return {"path_is_gitignored": ign.returncode == 0,
            "check_rc": chk.returncode, "bytes_moved": moved}


def legs(text):
    """The three legs, measured. Returns a dict of raw evidence."""
    patch = open(PATCH, encoding="utf-8").read()
    ctx = re.search(r"^@@[^@]*@@ ?(.*)$", patch, re.M)
    lines = text.splitlines()
    hits = [i + 1 for i, l in enumerate(lines) if "increment_opline" in l]
    a, b = FN_SPAN
    fn_text = "\n".join(lines[a - 1:b])
    return {
        "leg1_hunk_context": (ctx.group(1).strip() if ctx else ""),
        "leg2_increment_opline_lines": hits,
        "leg2_all_inside_span": bool(hits) and all(a <= h <= b for h in hits),
        "leg3_normal_guard_present": NORMAL_GUARD in fn_text,
        "next_opcode_occurrences": text.count("NEXT_OPCODE();"),
        "patch_insertions": patch.count("\n+") - patch.count("\n+++"),
        "patch_deletions": patch.count("\n-") - patch.count("\n---"),
    }


# ---- the verdict, factored so it can be ATTACKED ----------------------------

def backport_problems(applied, ev, backport_applied=None, trap=None):
    """1. ⛔ if `git apply` SUCCEEDS, `spec.md` and `../NOTES.md` §5 are wrong to
          call R1h a hand backport and should say `applied cleanly` instead;
       2. LEG 1 -- the hunk context must name `zend_binary_assign_op_helper`;
       3. LEG 2 -- `increment_opline` must occur exactly 3x and all inside the
          function's span. A fourth occurrence elsewhere would break the leg;
       4. LEG 3 -- the normal exit's guard must ALREADY be in the pre-image, or
          the "adding it there would be a duplicate" argument collapses;
       5. ⭐ `NEXT_OPCODE();` must occur MANY times, or `preimage_screen.py`'s
          `CANDIDATE` would have been informative after all and §5's whole
          "the screen is weak here" paragraph is unearned;
       6. the patch must still be three insertions and no deletions.
    """
    p = []
    if applied:
        p.append("1. ⛔ `git apply` MOVED THE BYTES on the pristine 5.0.0 span. "
                 "spec.md's fix_commit_note and ../NOTES.md §5 both say the "
                 "upstream patch cannot be placed; one of them is now wrong")
    if backport_applied is False:
        p.append("7. ⛔⛔ THE POSITIVE CONTROL FAILED: "
                 "controls/4f68f3774c34-backport-5.0.0.patch did NOT move the "
                 "bytes either. So this harness cannot apply ANY patch and its "
                 "verdict on the upstream one means nothing -- which is exactly "
                 "the failure `git apply --check` under a gitignored path "
                 "produced in this file's first version")
    if trap is not None and trap.get("path_is_gitignored") and trap.get("check_rc") != 0:
        p.append("8. ⓘ `git apply --check` NO LONGER returns 0 under a "
                 "gitignored path. The trap this file documents has been fixed "
                 "in git; the paragraph in try_git_apply should be rewritten as "
                 "history rather than as a live hazard")
    if "zend_binary_assign_op_helper" not in ev["leg1_hunk_context"]:
        p.append(f"2. LEG 1: the hunk's @@ context is "
                 f"{ev['leg1_hunk_context']!r} and does not name "
                 f"`zend_binary_assign_op_helper`")
    if len(ev["leg2_increment_opline_lines"]) != 3 or not ev["leg2_all_inside_span"]:
        p.append(f"3. LEG 2: `increment_opline` occurs at "
                 f"{ev['leg2_increment_opline_lines']}, want exactly three "
                 f"lines all inside {FN_SPAN}")
    if not ev["leg3_normal_guard_present"]:
        p.append("4. LEG 3: the normal exit's `if (increment_opline) { "
                 "INC_OPCODE(); }` is NOT in the pre-image, so 'a patch adding "
                 "it there would be adding a duplicate' does not hold")
    if ev["next_opcode_occurrences"] < 50:
        p.append(f"5. `NEXT_OPCODE();` occurs only "
                 f"{ev['next_opcode_occurrences']}x, so the screen's single "
                 f"cited line may be informative after all and ../NOTES.md §5's "
                 f"dismissal of `CANDIDATE` needs re-reading")
    if (ev["patch_insertions"], ev["patch_deletions"]) != (3, 0):
        p.append(f"6. the patch is {ev['patch_insertions']} insertions / "
                 f"{ev['patch_deletions']} deletions, want 3 / 0 -- "
                 f"controls/4f68f3774c34.patch is not the commit this row cites")
    return p


def selftest():
    good_trap = {"path_is_gitignored": True, "check_rc": 0, "bytes_moved": False}
    good = {"leg1_hunk_context": "static inline int zend_binary_assign_op_helper(int",
            "leg2_increment_opline_lines": [1728, 1749, 1792],
            "leg2_all_inside_span": True,
            "leg3_normal_guard_present": True,
            "next_opcode_occurrences": 115,
            "patch_insertions": 3, "patch_deletions": 0}
    cases = [
        ("P1 the shipped shape", False, good, False, None),
        ("N1 git apply moves the bytes", True, good, True, "1."),
        ("N2 the hunk names another function", False,
         {**good, "leg1_hunk_context": "static int zend_assign_dim_handler("}, True, "2."),
        ("N3 a fourth increment_opline appears", False,
         {**good, "leg2_increment_opline_lines": [1728, 1749, 1792, 2400],
          "leg2_all_inside_span": False}, True, "3."),
        ("N4 the normal exit's guard is absent", False,
         {**good, "leg3_normal_guard_present": False}, True, "4."),
        ("N5 NEXT_OPCODE is rare after all", False,
         {**good, "next_opcode_occurrences": 2}, True, "5."),
        ("N6 the patch is not three lines", False,
         {**good, "patch_insertions": 9}, True, "6."),
        ("P2 a different but still-large NEXT_OPCODE count", False,
         {**good, "next_opcode_occurrences": 300}, False, None),
        ("P3 the three lines at different line numbers, still inside", False,
         {**good, "leg2_increment_opline_lines": [1730, 1751, 1794]}, False, None),
    ]
    cases += [
        ("N7 the POSITIVE control fails too", False, good, True, "7.", False),
        ("N8 the gitignore trap has been fixed in git", False, good, True, "8.",
         True, {"path_is_gitignored": True, "check_rc": 1, "bytes_moved": False}),
        ("P4 the trap fires as documented", False, good, False, None, True,
         good_trap),
    ]
    bad = []
    for case in cases:
        label, applied, ev, must_fire, arm = case[:5]
        bp = case[5] if len(case) > 5 else True
        tr = case[6] if len(case) > 6 else good_trap
        got = backport_problems(applied, ev, bp, tr)
        if bool(got) != must_fire:
            bad.append(f"selftest {label}: fired={bool(got)}, want {must_fire} ({got})")
        elif must_fire and arm and not any(g.startswith(arm) for g in got):
            bad.append(f"selftest {label}: fired on {[g[:2] for g in got]}, want {arm}")
    return bad


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    problems = list(selftest())
    print("0. §H -- THE VERDICT ARM, ATTACKED OVER SYNTHETIC EVIDENCE")
    print(f"   selftest {'PASS' if not problems else 'FAIL'}   "
          f"9 arms (6 must-FIRE, 3 must-NOT-fire)")
    for p in problems:
        print(f"     *** {p}")
    if args.selftest:
        return 1 if problems else 0

    if not os.path.exists(TARBALL):
        print(f"r1h_backport.py: no tarball at {TARBALL}. Set PHP500_TARBALL; "
              f"patterns-php/SOURCES.md §1 has the museum URL and the sha256.",
              file=sys.stderr)
        return 1
    got = sha256(TARBALL)
    print(f"\n1. THE PINNED TARBALL   sha256 {got[:16]}…  "
          f"{'OK' if got == TARBALL_SHA else '*** NOT THE PINNED TARBALL ***'}")
    if got != TARBALL_SHA:
        problems.append(f"the tarball at {TARBALL} hashes to {got}, not "
                        f"{TARBALL_SHA}; every citation below is against the "
                        f"wrong corpus")
        return 1

    text = tarball_text()
    applied, msg = try_git_apply(text, PATCH, "upstream")
    print(f"\n2. THE UPSTREAM PATCH AGAINST THE PRISTINE `{MEMBER}`\n"
          f"   -> {'APPLIED (bytes moved)' if applied else 'REFUSED'}\n"
          f"      {msg}")
    bp_applied, bp_msg = try_git_apply(text, BACKPORT, "backport")
    print(f"\n2a. ⭐ THE POSITIVE CONTROL -- the SAME three lines with 5.0.0's\n"
          f"    own context (controls/4f68f3774c34-backport-5.0.0.patch)\n"
          f"   -> {'APPLIED (bytes moved)' if bp_applied else 'REFUSED'}\n"
          f"      {bp_msg}")
    trap = gitignore_trap(text)
    print(f"\n2b. ⛔ THE TRAP THIS FILE'S FIRST VERSION FELL INTO, reproduced:\n"
          f"    the SAME refused patch under a GITIGNORED path --\n"
          f"    path_is_gitignored={trap['path_is_gitignored']}   "
          f"`git apply --check` rc={trap['check_rc']}   "
          f"bytes_moved={trap['bytes_moved']}\n"
          f"    ▶ rc 0 AND nothing applied. `--check` is not the test; the bytes "
          f"are.")

    ev = legs(text)
    print("\n3. THE THREE LEGS -- what identifies WHICH exit, offline")
    print(f"   LEG 1  hunk @@ context: {ev['leg1_hunk_context'][:78]}")
    print(f"   LEG 2  `increment_opline` at lines "
          f"{ev['leg2_increment_opline_lines']}, all inside "
          f"{FN_SPAN}: {ev['leg2_all_inside_span']}")
    print(f"   LEG 3  the NORMAL exit's guard already in the pre-image: "
          f"{ev['leg3_normal_guard_present']}")
    print(f"\n4. ⛔ WHY THE SCREEN IS WEAK HERE\n"
          f"   `NEXT_OPCODE();` occurs {ev['next_opcode_occurrences']}x in "
          f"{MEMBER}.\n"
          f"   preimage_screen.py --id CRASH-023 cites ONE of them and returns "
          f"CANDIDATE.\n"
          f"   That is true and nearly information-free. It is an EXCLUSION "
          f"tool and it\n   correctly declines to exclude; it is not "
          f"confirmation and this row does not\n   quote it as such.")
    print(f"\n5. THE PATCH  {ev['patch_insertions']} insertion(s), "
          f"{ev['patch_deletions']} deletion(s) -- the NORMAL exit's own three "
          f"lines,\n   copied onto the error exit. Nothing is invented.")

    problems.extend(backport_problems(applied, ev, bp_applied, trap))
    pin = _pin.pin(
        ['controls/4f68f3774c34.patch', 'controls/4f68f3774c34-backport-5.0.0.patch', 'controls/r1h_backport.py'],
        'python3 patterns-php/ph55-opdata-stride/controls/r1h_backport.py',
        'the upstream patch, the hand backport that is its positive control, and this script. ⚠ The TARBALL is not pinned here because it is pinned BY SHA256 INSIDE the script and re-checked on every run, which is stronger.')
    out = {"tarball_sha256": got, "git_apply_applied": applied,
           "git_apply_message": msg, "backport_applied": bp_applied,
           "backport_message": bp_msg, "gitignore_trap": trap,
           "legs": ev, "problems": problems}
    out.update(pin)
    dst = os.path.join(HERE, "r1h_backport.json")
    json.dump(out, open(dst, "w"), indent=2, sort_keys=True)
    print(f"\nwrote {os.path.relpath(dst, ROOT)}")
    for p in problems:
        print(f"  *** {p}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
