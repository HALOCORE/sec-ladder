#!/usr/bin/env python3
# =============================================================================
# samefunc_hole.py -- ⭐⭐ **THE REVIEWER'S OWN COUNTEREXAMPLE**, AND THE ONLY
# COPY OF IT
#
# ⛔⛔ WHY IT IS COMMITTED, AND IT IS THE SHARPEST CASE IN THIS BATCH. Written
# under `.temp/php43/`, which is GITIGNORED. **F95** cites it BY PATH at
# `RECAP_PHP.md:6020` (landed 2026-09-13, commit 691b2cf) inside the clause that
# is the finding's own teeth: *"⛔⛔ **AND THE MANAGER'S `same_function` GUARD IS
# NECESSARY, NOT SUFFICIENT: the reviewer MADE IT ACCEPT A ZERO-LEADING-CONTEXT
# HUNK AS PROOF** (`.temp/php43/samefunc_hole.py`)."*
# ▶ `.memory-php/04-process.md` **LAW 12**: **the reviewer's INDEPENDENCE is the
# product.** A reviewer's counterexample against the manager's own guard, left
# in a directory `CLAUDE.md` constraint 6 schedules for deletion, is the one
# artefact in this tree that cannot be reconstructed by the party it was aimed
# at. `.memory-php/04-process.md` LAW 11. Promoted by `TASK_PHP_064`,
# 2026-09-17, repo at commit f4bda71.
#
# ⭐⭐⭐ ITS MEANING HAS CHANGED AND THAT IS THE RESULT, NOT A COMPLICATION.
# **The guard was repaired.** Re-run 2026-09-17, all four cases come out as
# wanted and the script prints `✅ no hole found by these four cases`:
#
#     CASE 1 CROSSES            want False  got False   the ph53 shape
#     CASE 2 NO LEADING CONTEXT want False  got False   ⛔ was the HOLE
#     CASE 3 PURE ADDITION      want False  got False   ⛔ was the HOLE
#     CASE 4 HONEST             want True   got True    must NOT be demoted
#
# `same_function` now returns the evidence dict *"the matched hunk has 0 leading
# context line(s) … so it is NO evidence either way, and a screen may not
# promote that to a proof"*. ▶ **So this file is no longer a hole-finder; it is
# a REGRESSION TEST for the repair, and CASE 4 is what stops the repair being
# over-corrected into demoting honest hunks.** ⚠ A counterexample whose target
# has been fixed is the one people delete, and it is the one that has to stay:
# nothing else in the tree pins that `same_function` still refuses a
# zero-context hunk.
#
# RUN IT:  python3 .tasks-php/probes/samefunc_hole.py     # 4 cases, rc 0
# ⓘ Its negatives are the run: there is no `--selftest` flag because the whole
# file IS four must-fire/must-NOT-fire cases against a committed validator.
# `PROTOCOL_PHP.md` §H applied to `preimage_screen.py` -- *a gate run EXERCISES
# a validator on the rows that pass; it does not ATTACK it*, and this is the
# attack.
#
# ✅ WHAT IT NEEDS THAT IS NOT COMMITTED: NOTHING. It imports
# `.tasks-php/preimage_screen.py` and calls `same_function` directly on
# SYNTHETIC hunk text. No corpus record is touched, nothing is edited, nothing
# is built, it WRITES NOTHING. 0.3 s, 2026-09-17.
# ⚠ `ROOT` is a HARDCODED ABSOLUTE PATH to this checkout -- same class as
# `probes/item83_sim.py` and `probes/sweep_cg.sh`; reported, not repaired.
#
# ⛔ WHAT IS STILL OWED, AND THE FIRST ONE IS A DEFECT IN THIS FILE.
# (1) ⚠⚠ **IT PROMISES A COUNT IT DOES NOT PRINT.** The last two lines of
#     `main` say *"⭐ REACH ON THE REAL CORPUS … counted below over every
#     screened record's matched hunks"* and then the function RETURNS. Nothing
#     is counted below. ▶ The promise is left in place, with a line saying it
#     is unkept, rather than deleted (which hides the gap) or implemented here
#     (which would attribute a new measurement to the reviewer).
#     ⭐ **BUT THE NUMBER ITSELF IS SOURCED, AND I ALMOST WROTE THAT IT WAS
#     NOT.** The first draft of this header said F95's *"✅ Live reach on the
#     real corpus is `0`"* had *"no producer in this tree at all"*. **FALSE.**
#     `.tasks-php/preimage_screen.py --selftest` carries **`N13 MUST-NOT-FIRE:
#     the zero-context branch must reach NOTHING in the real corpus`**, which
#     walks every screened record's `same_function_evidence` and FAILS the
#     checker if any hits it. Measured 2026-09-17: `records hitting the
#     zero-context branch: 0 []`, `--selftest` rc 0. That checker is committed
#     AND in the routine sweep. ▶ So the defect is a DANGLING PROMISE in this
#     file, not an unsourced published claim -- and the difference was found by
#     grepping the code instead of trusting a header, which is the only reason
#     this file does not now ship a confident wrong negative about its own
#     sibling.
# (2) F95 is UPHELD but item **87** is still open.
# (3) `N10e`'s `43` inside `preimage_screen.py` is an external historical
#     constant that F95 itself says *"will move at row 9"*; nothing here
#     watches it.
# =============================================================================

"""TASK_PHP_043 §4.2 -- IS `preimage_screen.py::same_function`'s SOUNDNESS GUARD
SUFFICIENT, OR ONLY NECESSARY?

The guard (`preimage_screen.py:632-645`): *the matched hunk must contain no
function-definition header BEFORE its first changed line.* It exists because
git's `xfuncname` scans BACKWARDS from a hunk's first line, so a hunk starting
just before a definition is LABELLED with the preceding function while editing
only the next one -- `ph53/be8daf1f47fa`, which had promoted an exclusion to a
proof.

⛔ THE ATTACK: the guard inspects ONLY the context lines that precede the first
changed line. If there are NONE, there is nothing to inspect and the function
returns True. A hunk whose first line is already a `+`/`-` therefore passes the
guard with ZERO evidence -- the exact configuration the guard exists to detect,
in the one shape it cannot see.

This is `PROTOCOL_PHP.md` §H applied to a committed validator: a must-fire
negative that does NOT fire. It calls `same_function` DIRECTLY with synthetic
hunk text -- no corpus record is touched and nothing is edited.

Run: python3 .tasks-php/probes/samefunc_hole.py
"""
import importlib.util
import os
import sys

ROOT = "/home/apt/repos_common/sec-ladder"


def load():
    p = os.path.join(ROOT, ".tasks-php/preimage_screen.py")
    spec = importlib.util.spec_from_file_location("ps", p)
    m = importlib.util.module_from_spec(spec)
    sys.modules["ps"] = m
    spec.loader.exec_module(m)
    return m


# A synthetic 5.0.0 file. Line 4 is inside `void fn_A(void)`; line 9 is inside
# `void fn_B(void)`. `enclosing_header` finds the nearest preceding line that
# starts at column 0 with [A-Za-z_$].
SRC = [
    "void fn_A(void)",          # 1
    "{",                        # 2
    "\tint a = 1;",             # 3
    "\tCITED_LINE_A(a);",       # 4  <-- the cited site
    "}",                        # 5
    "",                         # 6
    "void fn_B(void)",          # 7
    "{",                        # 8
    "\tint b = 2;",             # 9
    "}",                        # 10
]

CITED = [4]          # the corpus cites line 4, enclosed by `void fn_A(void)`

# ---- CASE 1: the ph53 shape the guard was built for. Leading context crosses
#      into fn_B, so the guard MUST fire (same_function -> False).
HUNK_CROSSES = (
    "@@ -5,6 +5,7 @@ void fn_A(void)\n"
    " }\n"
    " \n"
    " void fn_B(void)\n"
    " {\n"
    "-\tint b = 2;\n"
    "+\tint b = 3;\n"
    " }\n")

# ---- CASE 2: THE HOLE. Identical situation -- the change is in fn_B and the
#      label names fn_A -- but the hunk has NO leading context line, so the
#      guard has nothing to inspect.
HUNK_NO_CONTEXT = (
    "@@ -9,1 +9,1 @@ void fn_A(void)\n"
    "-\tint b = 2;\n"
    "+\tint b = 3;\n")

# ---- CASE 3: THE HOLE, pure addition. git emits `-a,0` for an insertion; the
#      label is whatever precedes the insertion point.
HUNK_PURE_ADD = (
    "@@ -8,0 +9,1 @@ void fn_A(void)\n"
    "+\tint b_new = 99;\n")

# ---- CASE 4: the honest case the guard must NOT break -- the change really is
#      inside fn_A, with leading context inside fn_A.
HUNK_HONEST = (
    "@@ -3,3 +3,3 @@ void fn_A(void)\n"
    " \tint a = 1;\n"
    "-\tCITED_LINE_A(a);\n"
    "+\tCITED_LINE_A(a + 1);\n")


def main():
    ps = load()
    cases = [
        ("1 CROSSES (the ph53 shape)", HUNK_CROSSES, False,
         "the guard's own case: leading context contains `void fn_B(void)`"),
        ("2 NO LEADING CONTEXT", HUNK_NO_CONTEXT, False,
         "⛔ SAME SITUATION, no context to inspect"),
        ("3 PURE ADDITION", HUNK_PURE_ADD, False,
         "⛔ SAME SITUATION, git's `-a,0` insertion shape"),
        ("4 HONEST (must NOT be demoted)", HUNK_HONEST, True,
         "the change really is in fn_A"),
    ]
    print("same_function(SRC, [<hunk>], cited_nums=[4]);  cited line 4 is "
          "enclosed by `void fn_A(void)`")
    print("=" * 100)
    holes = []
    for tag, hunk, want, why in cases:
        got, ev = ps.same_function(SRC, [hunk], CITED)
        ok = (got is want)
        print(f"  CASE {tag:32s} want={want!s:5s} got={got!s:5s} "
              f"{'✅' if ok else '⛔ HOLE'}")
        print(f"       {why}")
        if ev:
            print(f"       evidence: {ev.get('crossed_into') or ev}")
        if not ok:
            holes.append(tag)
    print("=" * 100)
    if holes:
        print(f"⛔⛔ {len(holes)} HOLE(S): {holes}")
        print("   ▶ THE GUARD IS NECESSARY, NOT SUFFICIENT. `same_function` "
              "returns True -- i.e. 'the commit's window PROVABLY REACHES the "
              "site' -- for a hunk that supplies no evidence at all, whenever "
              "the hunk's first line is already a changed line.")
    else:
        print("✅ no hole found by these four cases")
    print()
    # ⚠⚠ THE PROMISE THIS FILE DOES NOT KEEP, KEPT VISIBLE ON PURPOSE. These
    # two lines announce a corpus count and the function then RETURNS.
    # Promoting the file unchanged would ship the appearance of evidence;
    # implementing it here would attribute a new measurement to the reviewer.
    # So it says what it is -- and it says where the number DOES come from,
    # because that was grepped rather than assumed (see the header, owed (1)).
    print("⭐ REACH ON THE REAL CORPUS, so this is not a theoretical hole "
          "reported as a live one:")
    print("   counted below over every screened record's matched hunks.")
    print()
    print("⛔ NOT COUNTED HERE. The two lines above are a PROMISE THIS FILE "
          "DOES NOT KEEP --")
    print("   nothing below them counts anything. ✅ The NUMBER is sourced "
          "elsewhere, and")
    print("   that was checked rather than assumed: "
          "`.tasks-php/preimage_screen.py --selftest`")
    print("   carries N13 MUST-NOT-FIRE, which walks every screened record's")
    print("   same_function_evidence and FAILS if the zero-context branch is "
          "reached.")
    print("   Measured 2026-09-17: `records hitting the zero-context branch: "
          "0 []`, rc 0.")
    print("   ▶ So F95's `Live reach on the real corpus is 0` IS re-derivable, "
          "by a")
    print("     committed checker that the routine sweep runs. Open item 87 "
          "is the residue.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
