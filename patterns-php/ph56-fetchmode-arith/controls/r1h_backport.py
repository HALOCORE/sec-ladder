#!/usr/bin/env python3
"""ph56 control -- **R1h APPLIES, AND `git apply --check` STILL LIES.**

    python3 patterns-php/ph56-fetchmode-arith/controls/r1h_backport.py
    python3 patterns-php/ph56-fetchmode-arith/controls/r1h_backport.py --selftest

`1e708a5aeb30711f8b7b2a811377a13f2b23a8c9` (Marcus Boerger, 2004-08-29,
*"Bugfix #29882 isset crashes on arrays"*) is ONE FILE, THREE INSERTIONS, ZERO
DELETIONS -- the three lines are `BP_VAR_R`'s own guard copied onto `BP_VAR_IS`,
error message and all. Nothing is invented.

⭐⭐ **AND IT PLACES ON 5.0.0, WHICH IS THE OPPOSITE OF `ph55`.** The commit is
six weeks after 5.0.0 shipped and `zend_do_end_variable_parse` had not drifted,
so `git apply` lands the hunk. This file RUNS it against the pristine tarball's
own `Zend/zend_compile.c` on every invocation, because *"git apply succeeds"* is
exactly the kind of claim that decays into folklore if nobody re-runs it.

⛔⛔ **AND IT MEASURES THE `_048` §4d TRAP RATHER THAN CITING IT.**
`git apply --check` returns **0** on a patch whose target path is GITIGNORED in
the enclosing repository, and `.temp/` is gitignored here -- so the naive check
says *success* on a run in which **nothing was applied**. `gitignore_trap()`
reproduces that on every invocation, so a future `git` which fixed the behaviour
shows up as a changed number rather than as a stale paragraph.
▶ **`--check` is not the test; THE BYTES ARE.**

⚠⚠ **AND THE MANAGER'S STATED *REASON* FOR THE PREDICTION IS REFUTED HERE.**
`TASK_PHP_051` §2.3 argues the patch applies because *"THE HUNK HEADER IS
`@@ -763,6 +763,9 @@` -- THE SAME LINE NUMBER AS 5.0.0's `:763`"*. Those are
**two different lines that happen to share a number**: the hunk's first context
line is `opline->opcode += 3;`, which the 2004-08-30 HEAD puts at 763 and 5.0.0
puts at **761**. `git` reports `Hunk #1 succeeded at 761 (offset -2 lines)`. The
patch applies DESPITE a two-line offset, not because of an exact match, and
`legs()` below measures the offset rather than asserting the coincidence.

§H (`PROTOCOL_PHP.md`): the verdict function is a FUNCTION so that it can be
attacked, and `--selftest` drives it over synthetic evidence -- **six must-FIRE
and four must-NOT-fire** cases.
"""

import argparse
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(PDIR))
sys.path.insert(0, HERE)
import _pin  # noqa: E402

PATCH = os.path.join(HERE, "1e708a5aeb30.patch")
PATCH_SHA = "9e86b04f294c451670a238b803f7331610098b5e4f58174d7a5454f74b98d5f2"
SCRATCH = os.path.join(ROOT, ".temp", "php56-r1h")

TARBALL_SHA = "5783e0c0ba94f165633a565fe73a83e59cf17b6880ef95fa8f936dc6301d6919"
CFILE = "Zend/zend_compile.c"

# The three lines the commit inserts, stripped of the leading `+`.
INSERTED = [
    "if (opline->opcode == ZEND_FETCH_DIM_W && opline->op2.op_type == IS_UNUSED) {",
    'zend_error(E_COMPILE_ERROR, "Cannot use [] for reading");',
    "}",
]


def _tarball():
    p = os.environ.get("PHP500_TARBALL")
    if p and os.path.exists(p):
        return p
    for cand in (
        "/home/apt/repos_common/php-in-safe-rust/.app-tests/.temp/oracle/"
        "build-5.0.0/php-5.0.0.tar.gz",
        "/home/apt/repos_common/php-in-safe-rust/.temp/san_tests/oracle/"
        "build-5.0.0/php-5.0.0.tar.gz",
    ):
        if os.path.exists(cand):
            return cand
    return None


def pristine():
    """`Zend/zend_compile.c` out of the PINNED tarball, or None."""
    t = _tarball()
    if not t:
        return None
    r = subprocess.run(["sha256sum", t], capture_output=True, text=True)
    if r.stdout.split()[0] != TARBALL_SHA:
        return None
    r = subprocess.run(["tar", "-xzOf", t, f"php-5.0.0/{CFILE}"],
                       capture_output=True)
    return r.stdout.decode("utf-8", "replace") if r.returncode == 0 else None


# ---------------------------------------------------------------- the runs --
def apply_run(src_text, own_repo):
    """Apply the patch to a scratch copy and REPORT WHETHER THE BYTES MOVED.

    `own_repo` is the half that matters: run inside the enclosing (gitignored)
    repository and `git apply` prints `Skipped patch` and exits **0**; `git init`
    the scratch first and the same command lands the hunk. Returns
    `(bytes_moved, message, added_lines)`."""
    root = os.path.join(SCRATCH, "own" if own_repo else "ignored")
    if os.path.isdir(root):
        import shutil
        shutil.rmtree(root)
    os.makedirs(os.path.join(root, "Zend"))
    dst = os.path.join(root, CFILE)
    open(dst, "w", encoding="utf-8").write(src_text)
    if own_repo:
        subprocess.run(["git", "init", "-q", "."], cwd=root, capture_output=True)
    before = open(dst, encoding="utf-8").read()
    r = subprocess.run(["git", "apply", "-v", PATCH], cwd=root,
                       capture_output=True, text=True)
    after = open(dst, encoding="utf-8").read()
    msg = re.sub(r"\s+", " ", (r.stdout + r.stderr).strip())[:300]
    # ⭐⭐ A MULTISET DIFFERENCE, AND THE REASON IS THE FIX ITSELF. The three
    # inserted lines are `BP_VAR_R`'s OWN GUARD COPIED ACROSS, so every one of
    # them ALREADY OCCURS in the pre-image. A set difference returns the empty
    # list here and would read as *"nothing was added"* on a patch that added
    # three lines. Counting occurrences is what distinguishes *"this text is
    # present"* from *"this text is present one more time than it was"* -- and
    # that distinction is this row's fix in one sentence.
    from collections import Counter
    ca = Counter(ln.strip() for ln in after.splitlines())
    cb = Counter(ln.strip() for ln in before.splitlines())
    added = sorted((ca - cb).elements())
    return after != before, msg, added


def gitignore_trap(src_text):
    """⭐ THE TRAP, REPRODUCED, not cited. `--check` under a gitignored path."""
    root = os.path.join(SCRATCH, "trap")
    os.makedirs(os.path.join(root, "Zend"), exist_ok=True)
    dst = os.path.join(root, CFILE)
    open(dst, "w", encoding="utf-8").write(src_text)
    ign = subprocess.run(["git", "check-ignore", "-q", CFILE], cwd=root,
                         capture_output=True)
    chk = subprocess.run(["git", "apply", "--check", PATCH], cwd=root,
                         capture_output=True, text=True)
    before = open(dst, encoding="utf-8").read()
    subprocess.run(["git", "apply", PATCH], cwd=root, capture_output=True)
    moved = open(dst, encoding="utf-8").read() != before
    return {"path_is_gitignored": ign.returncode == 0,
            "check_rc": chk.returncode, "bytes_moved": moved}


def legs(src_text, apply_msg):
    """The evidence that identifies WHICH ARM the three lines belong to, and
    the offset the hunk really lands at. Raw facts; `verdict()` reads them."""
    lines = src_text.splitlines()

    def lineno(needle, start=0):
        for i in range(start, len(lines)):
            if lines[i].strip() == needle:
                return i + 1
        return None

    m = re.search(r"Hunk #1 succeeded at (\d+) \(offset (-?\d+) lines?\)",
                  apply_msg or "")
    return {
        # LEG 1 -- the hunk's own function-context line
        "hunk_context_names_fn":
            "zend_do_end_variable_parse" in open(PATCH, encoding="utf-8").read(),
        # LEG 2 -- `case BP_VAR_IS:` occurs EXACTLY ONCE in this file
        "case_bp_var_is_count":
            sum(1 for ln in lines if ln.strip() == "case BP_VAR_IS:"),
        "case_bp_var_is_line": lineno("case BP_VAR_IS:"),
        # LEG 3 -- the two arms that ALREADY carry the guard at 5.0.0, so a
        # patch adding it there would be adding a duplicate
        "existing_guards":
            sum(1 for ln in lines
                if "Cannot use [] for reading" in ln
                or "Cannot use [] for unsetting" in ln),
        # the hunk header's own claim, and where it REALLY lands
        "hunk_header_old_start":
            int(re.search(r"@@ -(\d+),", open(PATCH, encoding="utf-8").read())
                .group(1)),
        "first_context_line": "opline->opcode += 3;",
        "first_context_line_at_5_0_0": lineno("opline->opcode += 3;"),
        "applied_at": int(m.group(1)) if m else None,
        "applied_offset": int(m.group(2)) if m else None,
    }


def kernel_delta():
    """The difference between `c/kernel.c` and `c/kernel_hardened.c`, INSIDE the
    mode switch, reduced to the lines R1h adds. ⭐ This is what makes the
    upstream patch and the row's own R1h the SAME change rather than two
    changes that are described the same way."""
    a = open(os.path.join(PDIR, "c", "kernel.c"), encoding="utf-8").read()
    b = open(os.path.join(PDIR, "c", "kernel_hardened.c"),
             encoding="utf-8").read()

    def arm(txt):
        m = re.search(r"case PH56_BP_VAR_IS:(.*?)break;", txt, re.S)
        return [ln.strip() for ln in m.group(1).splitlines()
                if ln.strip() and not ln.strip().startswith(("/*", "*", "//"))]

    ra, rb = arm(a), arm(b)
    added = [ln for ln in rb if ln not in ra]
    return {"r1_arm": ra, "r1h_arm": rb, "added": added,
            "guards_on_opcode_and_op2_type":
                any("PH56_FETCH_DIM_W" in ln for ln in added)
                and any("PH56_IS_UNUSED" in ln for ln in added)}


# ------------------------------------------------------------- the verdict --
def verdict(ev):
    """⚠ A FUNCTION so that `--selftest` can attack it. Returns `problems`."""
    p = []
    if ev["patch_sha256"] != PATCH_SHA:
        p.append(f"controls/1e708a5aeb30.patch sha256 is {ev['patch_sha256']}, "
                 f"want {PATCH_SHA}")
    if ev["pristine"] is False:
        p.append("the pinned 5.0.0 tarball was not found or did not hash; "
                 "every leg below is UNMEASURED (SOURCES.md §1)")
        return p
    if not ev["applied"]["bytes_moved"]:
        p.append("PREDICTION 1 REFUTED: git apply did NOT move the bytes of "
                 f"pristine {CFILE} -- {ev['applied']['message']}")
    if sorted(x.strip() for x in ev["applied"]["added"]) != sorted(INSERTED):
        p.append(f"the applied hunk added {ev['applied']['added']}, want the "
                 f"three lines of 1e708a5aeb30")
    t = ev["trap"]
    if not t["path_is_gitignored"]:
        p.append("the trap scratch is NOT gitignored, so the trap was not "
                 "exercised and `check_rc` means nothing")
    elif t["check_rc"] == 0 and not t["bytes_moved"]:
        pass  # the trap fired, as _048 §4d measured. Expected.
    else:
        p.append(f"⚠ THE GITIGNORE TRAP DID NOT REPRODUCE: check_rc="
                 f"{t['check_rc']} bytes_moved={t['bytes_moved']}. _048 §4d "
                 f"measured rc=0 with no bytes moved; if git changed, say so "
                 f"rather than deleting the check")
    lg = ev["legs"]
    if lg["case_bp_var_is_count"] != 1:
        p.append(f"`case BP_VAR_IS:` occurs {lg['case_bp_var_is_count']} times "
                 f"in {CFILE}; preimage_screen.py's 1/1 is only discriminating "
                 f"because it occurs ONCE")
    if lg["case_bp_var_is_line"] != 763:
        p.append(f"`case BP_VAR_IS:` is at :{lg['case_bp_var_is_line']}, want "
                 f":763")
    if lg["existing_guards"] != 2:
        p.append(f"{lg['existing_guards']} arms already carry the guard at "
                 f"5.0.0, want 2 (BP_VAR_R and BP_VAR_UNSET)")
    if lg["applied_offset"] not in (None, -2):
        p.append(f"the hunk landed at offset {lg['applied_offset']}, and this "
                 f"row's NOTES.md §5 publishes -2")
    if lg["hunk_header_old_start"] == lg["first_context_line_at_5_0_0"]:
        p.append("the hunk header's start line now EQUALS 5.0.0's own line for "
                 "the first context line; NOTES.md §5 says they differ by 2 and "
                 "that the agreement at :763 is a coincidence of two different "
                 "lines. Re-read it")
    kd = ev["kernel_delta"]
    if not kd["guards_on_opcode_and_op2_type"]:
        p.append("c/kernel_hardened.c's BP_VAR_IS arm does not add a test on "
                 "BOTH the opcode and the op2 type; upstream's three lines test "
                 "both")
    return p


def gather():
    src = pristine()
    ev = {
        "patch_sha256": subprocess.run(["sha256sum", PATCH], capture_output=True,
                                       text=True).stdout.split()[0],
        "pristine": src is not None,
        "kernel_delta": kernel_delta(),
    }
    if src is None:
        ev["applied"] = {"bytes_moved": False, "message": "no tarball",
                         "added": []}
        ev["trap"] = {"path_is_gitignored": False, "check_rc": None,
                      "bytes_moved": False}
        ev["legs"] = {}
        return ev
    os.makedirs(SCRATCH, exist_ok=True)
    moved, msg, added = apply_run(src, own_repo=True)
    ev["applied"] = {"bytes_moved": moved, "message": msg, "added": added}
    ev["trap"] = gitignore_trap(src)
    ev["legs"] = legs(src, msg)
    return ev


# -------------------------------------------------------------- --selftest --
def _selftest():
    """⚠⚠ §H: SIX must-FIRE and FOUR must-NOT-fire. A gate run EXERCISES a
    validator on evidence that passes; it does not ATTACK it."""
    good = gather()
    if not good["pristine"]:
        print("SKIP: no pinned tarball on this box; --selftest needs one")
        return 2
    assert verdict(good) == [], f"the real evidence must pass: {verdict(good)}"

    def mut(**kw):
        import copy
        e = copy.deepcopy(good)
        for k, v in kw.items():
            cur, *rest = k.split(".")
            tgt = e[cur]
            for r in rest[:-1]:
                tgt = tgt[r]
            if rest:
                tgt[rest[-1]] = v
            else:
                e[cur] = v
        return e

    fire = [
        ("patch bytes changed", mut(patch_sha256="deadbeef")),
        ("git apply did nothing",
         mut(**{"applied.bytes_moved": False})),
        ("the trap stopped reproducing",
         mut(**{"trap.check_rc": 1})),
        ("`case BP_VAR_IS:` stopped being unique",
         mut(**{"legs.case_bp_var_is_count": 3})),
        ("an existing guard disappeared",
         mut(**{"legs.existing_guards": 1})),
        ("the hunk landed somewhere else",
         mut(**{"legs.applied_offset": 0})),
    ]
    notfire = [
        ("the real evidence", good),
        ("a longer but still correct apply message",
         mut(**{"applied.message": good["applied"]["message"] + "  (verbose)"})),
        ("the trap fired with a different rc spelling but no bytes",
         mut(**{"trap.bytes_moved": False})),
        ("no tarball -- reported, and every other leg suppressed",
         mut(pristine=False)),
    ]
    bad = 0
    for name, e in fire:
        got = verdict(e)
        ok = len(got) > 0
        print(f"  must-FIRE     {'OK ' if ok else 'MISS'}  {name}")
        bad += 0 if ok else 1
    for name, e in notfire:
        got = verdict(e)
        # the no-tarball case is EXPECTED to report exactly one thing
        ok = (len(got) == 1 and "UNMEASURED" in got[0]) if name.startswith("no tarball") \
            else (got == [])
        print(f"  must-NOT-fire {'OK ' if ok else 'FIRED'}  {name}"
              + ("" if ok else f"  -> {got}"))
        bad += 0 if ok else 1
    print(f"\n--selftest: {bad} problem(s)")
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(_selftest())

    ev = gather()
    probs = verdict(ev)
    out = {"control": "r1h_backport",
           "row": "ph56-fetchmode-arith",
           "fix_commit": "1e708a5aeb30711f8b7b2a811377a13f2b23a8c9",
           "evidence": ev,
           "problems": probs}
    out.update(_pin.pin(["c/kernel.c", "c/kernel_hardened.c",
                         "controls/1e708a5aeb30.patch"],
                        "python3 controls/r1h_backport.py",
                        "re-runs `git apply` against the pinned tarball and "
                        "re-derives the R1 -> R1h delta"))
    with open(os.path.join(HERE, "r1h_backport.json"), "w") as f:
        json.dump(out, f, indent=2, sort_keys=True)
        f.write("\n")
    print(json.dumps({k: ev[k] for k in ("pristine", "applied", "trap")},
                     indent=2)[:1600])
    print(f"\nlegs: {json.dumps(ev['legs'])}")
    print(f"R1 -> R1h adds: {ev['kernel_delta']['added']}")
    print(f"\nproblems: {probs if probs else 'none'}")
    sys.exit(1 if probs else 0)


if __name__ == "__main__":
    main()
