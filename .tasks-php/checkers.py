#!/usr/bin/env python3
"""⛔⛔⛔ **DOES THE ROUTINE SWEEP ACTUALLY RUN THE NEGATIVES?** — the register of
every `.tasks-php/*.py`, what it is, and the argv the manager's sweep must use.

    python3 .tasks-php/checkers.py            # audit + run the sweep
    python3 .tasks-php/checkers.py --audit    # registry only, runs nothing
    python3 .tasks-php/checkers.py --selftest # the §H negatives

--------------------------------------------------------------------------------
WHY THIS FILE EXISTS
--------------------------------------------------------------------------------

**The manager's routine sweep was a shell loop running each checker in this
directory with NO ARGUMENTS, reporting *"twelve checkers green"*. Measured
2026-09-15: FOUR of them do not run their §H negatives on a bare invocation.**

⚠ The loop is described rather than quoted on purpose: spelled out, it contains a
shell variable inside a path under this directory, which `citecheck.py` reads as
a rooted path citation and reports as ROT. **It cost two spurious rot entries on
2026-09-15 before the string was removed** -- see `.tasks-php/README.md`.

    contract_audit.py   negatives INLINE  -- 8 arms on every run     <- the right design
    preimage_screen.py  negatives behind  --selftest
    cbaseline_check.py  negatives behind  --selftest
    fixsurvey.py        negatives behind  --selftest
    task_cost.py        negatives behind  --selftest

`task_cost.py` is the live instance: a bare run exits **0** while `--selftest`
exits **1**. ⭐ So *"all checkers pass"* was a statement about the arm that does
the least work, and `PROTOCOL_PHP.md` §H — *a validator lands with its must-fire
negatives* — says nothing about whether anybody RUNS them.

⚠⚠ **THIS IS THE THIRD TIME *"ALL CHECKERS PASS"* HAS BEEN FALSE.**
`coverage.py` had exited 1 since 2026-09-10 on duplicates it adjudicates as
correct; the pre-handoff audit of 2026-09-14 found six stale things behind a
green sweep; and now the sweep turns out not to exercise four checkers' arms.
**It is `RECAP_PHP.md` F14's class — `0 STALE` does not mean everything is
pinned — one level up: `rc=0` does not mean everything was checked.**

--------------------------------------------------------------------------------
⭐⭐ THERE IS NO `RATCHET` LITERAL IN THIS FILE, AND THAT IS DELIBERATE
--------------------------------------------------------------------------------

**`REGISTRY` IS the ratchet.** The audit is `set(disk) == set(REGISTRY)`, so a
new `.py` fails as UNFILED and a deleted one fails as STALE, and **no count is
written down anywhere to go stale.**

⛔ That is not style. **SIX hardcoded figures in `.tasks-php/` validators went
stale in this programme** — `task_cost.py`'s `owed = 34` (item 93), its
`total/rows ≈ 6.5` (three times inside one hour), `preimage_screen.py`'s `N10e`,
`task_cost.py`'s `EMPTY_FAMILIES = 14`, its `ROWS` at 8 — and
`.memory-php/04-process.md` law 6 forbids the class. ⚠⚠ **`EMPTY_FAMILIES` is
the one to learn from: its guard `0 <= EMPTY_FAMILIES <= owed` was satisfied
forever by downward drift. A BOUND IS NOT A DERIVATION.**

⛔⛔ **AND THE SIXTH WAS IN THIS FILE, IN A `why`.** `task_cost.py`'s entry read
*"15 arms"* while the file had **14** — measured 2026-09-15 by counting, and it
became true only by accident when `N14` was added in the same edit. ⭐ **The
structure carried no literal and the PROSE ABOUT the structure carried one**, so
the ratchet's own law had a hole exactly one level up from where it was written.
▶ **`N12` closes it: every `"<n> arms"` claim in a `why` is now CHECKED against
the arm names the checker actually prints when it runs.** ⚠ Note what this is
not: it does not forbid the literal, it *derives* it. A number a reader can
check is worth keeping; a number nobody recomputes is the defect.

--------------------------------------------------------------------------------
⛔⛔ AND THE FIRST RUN FOUND ONE — `citecheck` IS **NOT** RED FOR THE REASON
EVERY DOCUMENT SAYS IT IS
--------------------------------------------------------------------------------

`RECAP_PHP.md` and the manager's handoff both record *"`citecheck` red on item
97's known §H debt"*. **Measured 2026-09-15, it is false.**

    citecheck.py's last line:   sys.exit(1 if rot else 0)

**The exit code is driven SOLELY by `rot`, the rooted-path rot count.** Item
97's §H material — *13 §H-at-risk citations across 4 rows* — is printed as a
**separate warning block and does not touch the exit code at all**, by design,
*"so the 17 historical hits do not drown it"* (item 97's own repair note).

**The one standing `rot` entry is `TASK_PHP_048.md:337`** — a prose line reading
`` `.tasks-php/TASK_PHP_005/006/008_REPORT` ``, a **three-files-as-one-path
shorthand inside a paragraph whose own heading is "NAME COLLISION, DO NOT BE
MISLED".** It is a **false positive**, adjudicated below and **not repaired**,
because silencing a checker by editing its input is the opposite of the ratchet.

⚠ **`rot` also rises transiently while a task is in flight**, because every task
file cites its own report file before that report exists. ▶ **So `citecheck`
rc=1 is ambiguous between *a task is running* and *a citation rotted*, and the
count must be read, never the exit code.**

⭐⭐ **That is a CONCLUSION (*citecheck is red and it is expected*) that survived
while its REASON (*because of item 97*) was false — the programme's
characteristic failure mode, found by demanding that every adjudicated red state
its reason.**

--------------------------------------------------------------------------------
THE RULE THIS FILE ENFORCES
--------------------------------------------------------------------------------

**If a checker's negatives are flag-gated, the sweep MUST run the flag arm too.**
Otherwise the sweep runs the checker's report and calls it a verdict. That is
`N3`, and it is the reason this file exists rather than a note.

⚠ **EVERY ENTRY IS ADJUDICATED BY HAND, with a `why`.** This is the ratchet
pattern (`RECAP_PHP.md`, the `coverage.py`/`cbaseline_check.py` precedent):
a discovery-based checker files each hit with a reason and fails on UNFILED or
STALE entries — **it never tunes the pattern to make a hit go away.**
"""

import os
import re
import subprocess
import sys

# ⭐ F20: find the root by MARKER, not by counting `..`. One `..` too few bit
#    the manager's own first probe script and cost a task.
def _repo_root(start=None):
    d = os.path.dirname(os.path.abspath(start or __file__))
    while True:
        if os.path.isdir(os.path.join(d, "harness")) and \
           os.path.isfile(os.path.join(d, "CLAUDE.md")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            raise SystemExit("REFUSED: no repo root above " + (start or __file__))
        d = parent


ROOT = _repo_root()
TASKS = os.path.join(ROOT, ".tasks-php")

# ---------------------------------------------------------------------------
# THE REGISTRY -- one entry per `.tasks-php/*.py`, adjudicated by hand.
#
#   kind      "checker"  has a verdict; belongs in the routine sweep
#             "tool"     produces data or a table on demand; no standing verdict
#             "landing"  a one-shot that has already run and must REFUSE to re-run
#   argv      the STANDING-VERDICT invocation -- None for non-checkers
#   expect    its steady-state exit code, with `why` saying WHY it is not 0
#   negatives "inline"   §H arms run on a bare invocation        <- the right design
#             "flag"     §H arms run only under `--selftest`
#             "none"     the file has no §H arms
#   st_expect expected rc of `--selftest`, or None if the file HAS no selftest.
#             ⭐ A `flag` checker with `st_expect=None` is the defect this file
#             exists for: its arms would never run in the sweep at all.
# ---------------------------------------------------------------------------
REGISTRY = {
    "boxcheck.py": dict(
        kind="checker", argv=[], expect=0, negatives="probe", st_expect=None,
        probe="probes/rule9_mustfire.py",
        why="RECAP_PHP.md's own invariants, incl. the 20-line START HERE box. "
            "⭐⭐ 2026-09-15 (F131) IT GAINED THE ONE ARM IT MOST NEEDED AND THE "
            "`negatives` FIELD MOVED `none` -> `probe`: the RULE-9 table is an "
            "INDEX, so it must have ONE ROW PER KEY, and it had SIX keys on two "
            "rows at once because _057 verdicted a BATCH that was APPENDED below "
            "instead of APPLIED above. ⛔ The old `why` said *every assertion IS "
            "a must-fire arm against a live file*, and that was the exact reason "
            "this defect was invisible: an assertion about the live file cannot "
            "be shown FAILING without breaking the live file. ▶ `rule9_rows()` is "
            "now PURE over the text, and probes/rule9_mustfire.py plants the "
            "defect in a STRING. ⭐⭐⭐ IT ALSO DERIVES THE BACKLOG -- the open "
            "cycles are printed and written down nowhere else."),
    "citecheck.py": dict(
        kind="checker", argv=[], expect=1, negatives="flag", st_expect=0,
        why="⛔⛔ THE BARE RUN IS RED, AND **NOT** FOR THE REASON EVERY DOCUMENT "
            "GIVES. It exits `1 if rot else 0`, so ONLY the rooted-path rot "
            "count sets the code; item 97's §H material is a separate WARNING "
            "block that never touches it. The one standing rot is "
            "TASK_PHP_048.md:337's `TASK_PHP_005/006/008_REPORT` -- three files "
            "written as one path, in a paragraph headed 'NAME COLLISION, DO NOT "
            "BE MISLED'. A FALSE POSITIVE, adjudicated and NOT repaired: "
            "silencing a checker by editing its input is the opposite of the "
            "ratchet. READ THE COUNT, never the exit code. "
            "⛔⛔⛔ THIS ENTRY SAID `st_expect=1` AND *'Both arms are red for "
            "this same one cause: --selftest fails N5d/N4, which assert "
            "rot == 0'* -- AND THAT REASONING WAS FALSE, SO THE SWEEP PRINTED "
            "`ok` OVER TWO GENUINELY FAILING ARMS FOR 43 COMMITS. The arms did "
            "NOT inherit the false positive's benignness: they were defective "
            "on their own, pinning the ABSOLUTE literal `rot == 0` for a "
            "RELATIVE claim their own message makes ('untouched by this "
            "extension'). The standing rot merely MOVED the number and revealed "
            "them. ▶ A BENIGN CAUSE DOES NOT MAKE A FAILING ARM BENIGN. "
            "⭐⭐ And the mechanism is the ratchet's own, one level up: the "
            "ratchet forbids silencing a checker by editing its INPUT, and this "
            "silenced one by editing its EXPECTATION. ✅ REPAIRED 2026-09-15 "
            "(RECAP_PHP.md F135): N5d/N4 now assert the STRUCTURAL disjointness "
            "of the rot-bearing LIVE set from the extensions' inputs, which is "
            "true at any rot value, and `--selftest` exits on ARM STATE ALONE "
            "(`sys.exit(selftest())`, which it always did) -- so `st_expect=0` "
            "is now DERIVED FROM INTENT rather than captured from observation, "
            "and a future arm failure is visible again. ⚠ `expect=1` on the "
            "BARE run stays: that one really is the adjudicated rot. "
            "⭐ 2026-09-15: the `rot rises transiently per in-flight task` "
            "caveat was NARROWED AND THEN REPAIRED -- it only ever rose for a "
            "task whose report is SPLIT (`_REPORT_E2E3E4.md` did not match "
            "`endswith('_REPORT.md')`); measured at 1 vs 2, then fixed with "
            "N6a-c so BOTH spellings are benign."),
    "coverage.py": dict(
        kind="checker", argv=[], expect=0, negatives="none", st_expect=None,
        why="166 corpus rows accounted for in CATALOGUE.md. ⚠ Carries its own "
            "ratchet; `bad` no longer counts adjudicated duplicates (it exited 1 "
            "from 2026-09-10 on duplicates it adjudicates as CORRECT)."),
    "quota.py": dict(
        kind="checker", argv=[], expect=0, negatives="inline", st_expect=None,
        why="Re-derives QUOTA_001's numbers from CATALOGUE.md. Prints its four "
            "§H arms on a bare run; N1 declares itself VACUOUS rather than "
            "passing silently when no row is half-built."),
    "contract_audit.py": dict(
        kind="checker", argv=[], expect=0, negatives="inline", st_expect=0,
        why="⭐ THE REFERENCE DESIGN: 8 arms incl. an N8 ratchet, all on a bare "
            "invocation -- the only checker here whose sweep arm and verdict arm "
            "are the same run. Items 91/98/103."),
    "cbaseline_check.py": dict(
        kind="checker", argv=[], expect=0, negatives="flag", st_expect=0,
        why="F108: every cross-language percentage must name WHICH C COMPILER. "
            "12 arms over a hand-adjudicated hit ratchet, PLUS an `ⓘ` ONE-COLUMN "
            "REPORT that deliberately carries no verdict. ⭐⭐ N2b/N2c ARE NEW AT "
            "TASK_PHP_059 (item 134): BASE was LOOSENED to accept the `gcc-C` / "
            "`clang-C` word order, because it was flagging `ph29` NOTES 1157 -- "
            "the best-labelled sentence in the corpus -- on a spelling. N2c is "
            "the arm that keeps that honest, asserting the loosened BASE still "
            "flags a claim naming NO compiler. ⛔ The OTHER half of item 134, "
            "making BASE DEMAND both columns, was REFUSED an eighth time: the "
            "rule is a DISJUNCTION (`both columns, OR an explicit statement that "
            "only one was measured`) and the second branch is not "
            "regex-decidable -- so it is the REPORT arm instead. ⛔ N2's own "
            "exemplar used to be a ONE-COLUMN sentence held up as correctly "
            "labelled; the enforcer's model of compliance was itself one item "
            "short of the rule. ⛔⛔ THIS ENTRY SAID "
            "`A bare run REPORTS and does not check -- the sweep must run the "
            "flag arm too`, AND THE FLAG IT MEANT WAS THE WRONG ONE: the ratchet "
            "was gated on `--ratchet`, which NOTHING passed -- not this registry, "
            "not the sweep. Measured at `1cc2c0e`: the corpus already stood at 70 "
            "hits against a ratchet of 69, un-run and unnoticed. ⭐ A ratchet you "
            "must opt into is not a ratchet: the BARE run now enforces, so "
            "`argv=[]` is the enforcing arm and no new argv is filed. ⛔ The "
            "count is NOT repeated here -- it was `RATCHET=69` and went stale "
            "the moment the ratchet was raised, which is item 73's class in a "
            "registry entry ABOUT a ratchet. ⛔⛔ This entry also said `9 arms` "
            "until N12 measured it: N8b was never counted, and the arms printed "
            "NOTHING on pass, so the claim was uncheckable as well as wrong."),
    "preimage_screen.py": dict(
        kind="checker", argv=[], expect=0, negatives="flag", st_expect=0,
        why="F64/F68/F95: the R1h pre-image screen and its FOUR outcomes, of "
            "which only NOT-THE-REPAIR is a proof. N10a-N10e. ⛔ Flag-gated."),
    "fixsurvey.py": dict(
        kind="checker", argv=["--offline"], expect=0, negatives="flag",
        st_expect=0,
        why="F40: every catalogued row's upstream fix, surveyed once. ⛔⛔ THE "
            "STANDING ARM MUST CARRY --offline OR IT REACHES THE NETWORK; the "
            "patch cache under .temp/mgr/batch/patches/ makes it free. "
            "⚠ FIXSURVEY_001.md's own caution: a `same-file` verdict is a "
            "STARTING POINT, NEVER A LICENCE (F38: 3 of 5 hand-checked commits "
            "are LATER fixes)."),
    "task_cost.py": dict(
        kind="checker", argv=[], expect=0, negatives="flag", st_expect=0,
        why="⛔ THE LIVE INSTANCE THAT PROVES THIS FILE'S POINT: on 2026-09-15 a "
            "bare run exited 0 while --selftest exited 1 on N1 (two new task "
            "files unclassified). 19 arms; N1 also caught ROWS stale at 8 the "
            "moment it was first run, and N1 caught row 13's task file within "
            "a minute of my writing it. ⭐⭐⭐ N8b/N8c/N8d (2026-09-16) EXIST "
            "BECAUSE N8 WAS WATCHING THE WRONG PROPERTY: it bounds the SIZE of "
            "the PENDING pile, and `\"040\"` -- the R1h hunt for ph52 AND ph53, "
            "the entry the PENDING block cites as setting the precedent -- sat "
            "there for ~20 tasks after BOTH its rows gated, understating the "
            "PUBLISHED projection (~61..~77 -> ~63..~79, marginal 2.42 -> "
            "2.50). ▶ A PENDING entry now NAMES its rows and N8b re-derives the "
            "answer from the gated corpus; N8c refuses the bare spelling that "
            "would make N8b vacuous; N8d proves N8b's silence means 'nothing "
            "is wrong' and not 'nothing was read'. ⭐ F132's class one level "
            "up: a cardinality was checked where the property was about "
            "MEMBERS. "
            "moment it was first run. ⭐ N14 (2026-09-15) makes ROWS itself "
            "derived-and-checked against results-php/gate/, which is the one "
            "staleness N1 cannot see; its must-fire evidence is the committed "
            "probes/n14_mustfire.py. ⭐⭐ N15 (same day) DERIVES the opener rate "
            "instead of pinning it, after the pinned OPENER_RATE=4.00 was "
            "refuted IN SIGN at n=8 by ph97 landing -- and N11, which asserted "
            "the premium's DIRECTION, had to be rewritten because it could not "
            "express the answer. ⚠ This `why` said 15 twice: at 14 arms and "
            "again at 16 -- N12 derives it now, and caught both."),
    "php50_align_sweep.py": dict(
        kind="checker", argv=["--selftest"], expect=0, negatives="inline",
        st_expect=0,
        why="§B5's instrument (item 112 / F110). Its own docstring: the arms "
            "'run on every invocation, not only under --selftest; a broken "
            "verdict arm REFUSES to measure rather than measuring anyway'. "
            "⚠ A bare run with no --row/--all measures nothing, so the standing "
            "arm IS the selftest here."),
    "php53_envp_sweep.py": dict(
        kind="checker", argv=["--selftest"], expect=0, negatives="inline",
        st_expect=0,
        why="F113's instrument -- the envp axis, which refuted §B5's stated "
            "ground (argv and envp are NOT the same knob). Same inline-arms "
            "design as php50_align_sweep.py, same bare-run caveat."),
    "php_null.py": dict(
        kind="checker", argv=[], expect=0, negatives="none", st_expect=0,
        why="Has any php family-B figure been compared against its own R5-R4 "
            "null? Cites harness/check.py's null-control rule that no php "
            "document carried. ⛔ `st_expect` WAS `None` over a PASSING "
            "`--selftest` the registry never ran (TASK_PHP_061 §4.2); the "
            "other file law 16 calls the model. Measured 2026-09-16: rc=0 "
            "SELFTEST PASS, 0.08 s -- free."),
    "width.py": dict(
        kind="checker", argv=[], expect=0, negatives="none", st_expect=0,
        why="F92: the probe_iters lever's gain is W^(-0.5), which settled item "
            "68 NO and refuted F90's operative half. ⚠ ~27 s -- the slowest "
            "entry, and the only reason the sweep is not instant. "
            "⛔⛔ `st_expect` WAS `None` AND THIS FILE HAS A PASSING "
            "`--selftest` THE REGISTRY NEVER RAN -- found by TASK_PHP_061 §4.2, "
            "and this is one of the TWO FILES LAW 16 NAMES AS THE MODEL. "
            "A passing self-test nobody runs is F135's class exactly: it will "
            "go red and nothing will say so. Measured 2026-09-16: rc=0 "
            "SELFTEST PASS, 33.3 s -- which roughly DOUBLES the sweep, and the "
            "cost is accepted deliberately at a task-boundary check. "
            "⚠ `st_expect=None` STILL CONFLATES *has none* WITH *has one, "
            "unfiled* -- that is the design residue, open item 140."),
    "php50_table.py": dict(
        kind="tool", argv=None, expect=None, negatives="none", st_expect=None,
        why="Renders the item-112 sweep table from .temp/php50/*.json. A "
            "RENDERER over gitignored scratch: it has no standing verdict and "
            "must not be read as one."),
    "php50_ub_repro.py": dict(
        kind="tool", argv=None, expect=None, negatives="none", st_expect=None,
        why="Reproduces F109's quotable sentence (unsafe Rust with the bug is "
            "STRICTLY WORSE THAN C) on adversarial-nullcall.bin. A reproducer, "
            "run on demand."),
    "land_019_020.py": dict(
        kind="landing", argv=None, expect=2, negatives="none", st_expect=None,
        why="⭐ ALREADY LANDED (CATALOGUE.md 93 -> 102 rows). rc=2 is the script "
            "REFUSING to re-run, which is correct. ⚠ It carries two sentences "
            "measured FALSE and corrected in place (F52, F53) -- a landing "
            "script left holding a refuted claim is a cited artefact."),
    "land_m4.py": dict(
        kind="landing", argv=None, expect=2, negatives="none", st_expect=None,
        why="⭐ ALREADY LANDED (TASK_PHP_012 M4: 12 rows re-tiered verbatim -> "
            "narrowed per §A1). rc=2 is the refusal to re-run."),
    "checkers.py": dict(
        kind="checker", argv=["--audit"], expect=0, negatives="inline",
        st_expect=0,
        why="⭐ THIS FILE. Files itself so the ratchet is total. ⛔ Its standing "
            "arm is --audit, NOT a bare run, because a bare run executes the "
            "whole sweep -- and the sweep must not run it recursively (N10)."),
    "refetch.sh": dict(
        kind="tool", argv=None, expect=None, negatives="none", st_expect=None,
        why="⛔ NETWORK. Regenerates the manager's gitignored scratch downloads "
            "under .temp/mgr/ -- mbfl sources at three tags, two patches, and "
            "the UPSTREAM_001 batch (F34/F36). ⚠⚠ NEVER IN A SWEEP: it curls "
            "github, and the standing rule on the patch cache is REPORT, DO NOT "
            "GUESS, NEVER RE-FETCH (F115 -- 3 of 163 cached patches do not bind "
            "to their filename sha, and re-fetching would destroy the evidence "
            "for that). ⭐ Committed as CLAUDE.md rule 1's generator; run it only "
            "if the scratch is gone AND you have decided you need it. ⓘ It sat "
            "outside the ratchet until 2026-09-15."),
    "probes/fdset_census.sh": dict(
        kind="tool", argv=None, expect=None, negatives="none", st_expect=None,
        why="ph16's 7-site FD_SET census, run once when the row was built. A "
            "shell probe over the pristine tarball with no standing verdict. "
            "ⓘ It sat OUTSIDE the ratchet until 2026-09-15, because _disk() "
            "globbed `.py` only."),
    "probes/rebuild_hardened_php.sh": dict(
        kind="tool", argv=None, expect=None, negatives="none", st_expect=None,
        why="⭐⭐ PROTOCOL_PHP §A3a obligation 5's generator: build PHP 5.0.0, "
            "apply the row's R1h, rebuild, and run the trigger against both. "
            "Measured 30 s cold / 683 ms incremental / 60 MB, no sudo, no "
            "network -- the number that turned §A3a's fifth obligation from "
            "REFUSED to REQUIRED (F123). ⛔ NOT in the sweep: it is 30 s and it "
            "answers a per-row question, not a standing one. "
            "✅ GENERALISED 2026-09-16 (row 13): `--patch/--trigger/--label/"
            "--workdir`, ph97's values still the defaults. ⭐⭐ AND THE "
            "GENERALISATION FOUND A GAP -- steps 3/5 asserted `rc=139` then "
            "`rc=0` and discarded stdout, which is unreadable for a row whose "
            "target error is a WRONG ANSWER at rc=0. It now prints rc AND "
            "stdout for both images and adjudicates nothing (F141). "
            "ⓘ st_expect=None is HONEST here, not unfiled (item 140): "
            "`--dry-run` prints the resolved settings so the "
            "defaults-unchanged claim is checkable in a second, but it "
            "ASSERTS nothing, so it is not a self-test."),
    "probes/ph96_arrayaccess_matrix.sh": dict(
        kind="tool", argv=None, expect=None, negatives="none", st_expect=None,
        why="⭐⭐⭐ ROW 12's criterion-2 instrument, and the row's whole research "
            "ground in one table: the FOUR ArrayAccess handlers of "
            "`Zend/zend_object_handlers.c` share one helper, and the file "
            "carries BOTH correct spellings (`:384` tests the out-parameter, "
            "`:413` declines it by passing NULL) and BOTH wrong ones (`:427`, "
            "`:512`). Prints a 2x2 with a per-cell expectation. ⭐ The two "
            "faulting cells land on DISTINCT addresses -- 0x14 = "
            "offsetof(zval,type) via `i_zend_is_true`, 0x10 = "
            "offsetof(zval,refcount) via `_zval_ptr_dtor` -- so the fault "
            "address alone says WHICH site ran, and both follow from the "
            "`Zend/zend.h:287-293` layout rather than being fitted to the "
            "observation. ⛔ NOT IN THE SWEEP, and the reason is not cost "
            "(~2 s): it needs the 5.0.0 oracle binary, which lives in ANOTHER "
            "project's gitignored scratch. A checker that reddens when a "
            "sibling repo is cleaned is reporting on that repo, not this one "
            "-- same call as `probes/rebuild_hardened_php.sh`. ▶ Run it by "
            "hand; it exits non-zero if any cell deviates, and a deviation is "
            "a RESULT to report, never an expectation to edit (F43/F47)."),
    "probes/item139_sibling_census.py": dict(
        kind="checker", argv=["--selftest"], expect=0, negatives="flag",
        st_expect=0,
        why="⭐⭐⭐ ITEM 139 — `F133`(i) across all 13 rows AS A GREP (the `_061` "
            "reviewer's binding form: one grep per row, NOT ten censuses). "
            "6 arms, 5 must-fire. **The result is not a tally**: `F133`(i) — "
            "*the R1h's strategy was already present elsewhere in the same "
            "construct* — is only a WELL-FORMED question for repairs that ADD "
            "A GUARD (8 of 13 rows; it holds on 7). For the rest the repair "
            "changes a STRUCT (ph45 adds the field it then uses), DELETES a "
            "line (ph52's whole patch is one removal), alters the BUILD (ph16, "
            "10 files + configure.in) or imports a TREE-WIDE api (ph29, ph53) "
            "— and the question has NO ANSWER rather than a NO. ⭐⭐ Every "
            "positive is a SIBLING: ph64's `calling` flag was declared, set "
            "and cleared by the same file three years before the fix that "
            "READS it; ph55's repair text is already in the file verbatim. "
            "⛔⛔ AND SCOPE DOES REAL WORK: on ph29 the answer is NO in-file "
            "(`safe_emalloc` 0x) and YES tree-wide (250 sites / 78 files) — "
            "'the same construct' is undefined and the answer flips with it. "
            "⚠⚠ The `tok` column is a TRIPWIRE, NOT the claim: it does not "
            "compute the `claim` beside it (ph96's claim is 7-of-23, the token "
            "reads 3). The first draft printed it under a bare `n` heading — "
            "law 6's defect — and said '7 of 13' while the table computed 8. "
            "N6 now pins the prose to the table permanently."),
    "probes/ph66_key_identity.sh": dict(
        kind="tool", argv=None, expect=None, negatives="none", st_expect=None,
        why="⭐⭐⭐ ROW 13's criterion-2 instrument, and THE ROW IN THE CORPUS "
            "WHERE EVERY CELL EXITS 0 ON PURPOSE. `zend_hash.c:464` settles a "
            "bucket's key KIND with a DISJUNCT, so for a numeric bucket the "
            "key is never compared; the collision needs no preimage because a "
            "numeric bucket stores the raw index (run DJBX33A FORWARDS -- "
            "`probes/ph66_djbx33a_collide.py`). 5 cells, each printing its "
            "SURVIVOR LIST because the target error is a wrong ANSWER, not a "
            "signal. ⭐ Cell D is the headline: `unset($a['abc'])` leaves "
            "'abc' IN the array and destroys the unrelated live element -- "
            "both halves wrong at once. ⛔⛔ CELLS A-C REFUTE `ROW13_001.md` "
            "§4's 'the harm is selectable between silent and ASan-visible': "
            "all three are silent, because `pDestructor` frees only at count 0 "
            "and the bucket's one external alias (`pInternalPointer`) is "
            "repaired four lines above the free. The catalogue's own risk note "
            "had it right and §4 was a second, disagreeing home (F131). "
            "⛔ NOT IN THE SWEEP, same call as `ph96_arrayaccess_matrix.sh`: "
            "it needs the 5.0.0 oracle binary, which lives in ANOTHER "
            "project's gitignored scratch, and a checker that reddens when a "
            "sibling repo is cleaned is reporting on that repo. Exits non-zero "
            "on any deviation, and a deviation is a RESULT (F43/F47)."),
    "cbaseline_diff.py": dict(
        kind="checker", argv=["--selftest"], expect=0, negatives="flag",
        st_expect=0,
        why="⛔⛔⛔ THE RATCHET COUNT IS NOT A MEASURE OF CORPUS HEALTH, AND THIS "
            "IS THE TOOL THAT SHOWS IT. `cbaseline_check.units()` splits on "
            "BLANK LINES, so a unit is a PARAGRAPH -- and an ordinary prose edit "
            "near a hit can move the count with nothing repaired and nothing "
            "broken. THREE MEASURED INSTANCES (F132): the Index unit silenced by "
            "a finding TITLE gaining the literal `c-gcc`; `02-ladder.md`'s "
            "FOURTH-FLAG blockquote silenced by an inserted block carrying "
            "`c-gcc`; and `ph16`'s NOTES unit SPLIT by an added blank line so "
            "the first half lost the bare `C`. ⭐⭐ In the last two the manager "
            "was editing the very finding about the ratchet, and the net read "
            "+1 while THREE had arrived. ▶ ADJUDICATE THE SET, BY UNIT TEXT, "
            "NEVER THE NUMBER -- a line-keyed diff cannot do it either, because "
            "line numbers move under every edit. ⓘ Takes an optional git ref "
            "(default HEAD); it reproduces the 70-at-`1cc2c0e` baseline F130 "
            "rests on, without a worktree. READ-ONLY: writes nothing, builds "
            "nothing."),

    # --- TASK_PHP_059, the reviewer's own generators, RESCUED FROM `.temp/` ---
    # ⛔⛔ THEY WERE WRITTEN INTO GITIGNORED `.temp/rev059/` AND THE REVIEWER
    #    FLAGGED IT RATHER THAN HIDING IT: *"every number in this report that is
    #    not a `git show` or a quotation comes from one of them, and if `.temp/`
    #    is cleared they are not re-derivable."* That is F51/F99/F116's defect --
    #    the committed claim layer resting on deletable scratch -- and F116 was
    #    UPHELD-with-its-REASON-REFUTED at `_057` for exactly this. A reviewer
    #    may not `git add`, so rescuing them is the manager's job and it is the
    #    FIRST thing done with the report.
    "php59_share.py": dict(
        kind="checker", argv=["--selftest"], expect=0, negatives="flag",
        st_expect=0,
        why="⭐⭐⭐ THE REVIEWER's INDEPENDENT re-derivation of F74's share, and "
            "it SHARES NO CODE with php58_record_share.py by construction: "
            "n_iters parsed from the .bin header with `struct` instead of via "
            "common-php/slb.py, the record walk written from the schema, and "
            "the pair enumeration is ALL unordered cell pairs instead of a "
            "hand-written list of nine -- so it cannot inherit the manager's "
            "choice of which pairs count. ⭐ It REPRODUCED the manager's tally "
            "exactly (x-lang 17/71, same-lang 99/11) and then showed the shape "
            "survives the wider population (65/287, 203/61), which is what made "
            "`19.3 %` safe to keep and the SENTENCE built on it unsafe. "
            "⭐⭐ Subcommands beyond the arms: `pairs`, `sweep` (condition (i) "
            "thresholds -- this is what CLOSED item 132), `over1`, `flip`, "
            "`named`, `cells`. ⚠ Two independent tools computing one quantity "
            "is not duplication here, it is the second method rule 9 asks for."),
    "php59_marginal_at_n.py": dict(
        kind="tool", argv=None, expect=None, negatives="none", st_expect=None,
        why="⭐⭐ §1.4's CHEAP DISCRIMINATOR: recomputes marginal_ir_per_call at "
            "an n_iters-scale probe window instead of collapse.probe_iters "
            "[100,200], to test whether F74's share exceeding 1.0 is a slope "
            "artefact. It SETTLED ph07 (1.0353 -> 0.9569) and did NOT settle "
            "ph16, where the five-window series is NON-MONOTONE with [100,200] "
            "the lowest -- so there the slope and transient candidates are the "
            "SAME phenomenon and the discriminator cannot discriminate. "
            "⛔⛔ NOT A CHECKER AND MUST NOT BECOME ONE WITHOUT ARMS -- the "
            "reviewer said so unprompted: it takes positional args, runs "
            "valgrind, and its kernel-exclusive column is KNOWN BAD (returned 0 "
            "on ph07, over-counted on ph45; the reviewer discarded it and used "
            "callgrind_annotate for every W figure). Its whole-program totals "
            "ARE sound -- they reproduce two committed marginals to the digit. "
            "▶ Use the summary column, never the kernel one."),
    "probes/rule9_mustfire.py": dict(
        kind="checker", argv=[], expect=0, negatives="inline", st_expect=None,
        why="⭐⭐⭐ §H EVIDENCE FOR boxcheck.py's RULE-9 ARM, AND THE REASON THAT "
            "ARM COULD BE WRITTEN AT ALL. F131: the table that decides what may "
            "enter .memory-php/ listed SIX findings as BOTH UNREVIEWED and "
            "verdicted. An assertion about a LIVE document cannot be shown "
            "failing without breaking the live document -- so boxcheck's "
            "`rule9_rows()` was made PURE over the text and this plants the "
            "defect in a STRING (F52: the probe made the state it was "
            "measuring, twice in one week). ⭐ DIFFERENTIAL, not absolute: each "
            "arm asserts the mutation moves rule9_rows's OWN output by exactly "
            "the planted key, relative to whatever the baseline is -- the "
            "repair n14_mustfire.py needed after it broke the first time a real "
            "defect went live. ⭐⭐ Arm (b) is the one that earns its keep: it "
            "plants a duplicate key WITHOUT ADDING A LINE, so a row-count check "
            "would pass it. ⓘ Its own first draft picked a victim row from the "
            "`_047` DATED SNAPSHOT table and all four arms went FAIL -- kept in "
            "the docstring, because that is a free demonstration that the "
            "table-scoping regex holds. "
            "⛔⛔⛔ TWO OF ITS OWN ARMS WERE FOUND BROKEN ON 2026-09-16 WHILE "
            "LANDING _063, AND BOTH WERE THE SAME CLASS -- AN ARM PINNED TO A "
            "POPULATION INSTEAD OF A PROPERTY (F132). (1) It kept a PRIVATE "
            "COPY of boxcheck's router regex and the copy was the NARROW "
            "pre-widening form, so the arm that exists to prove the widening "
            "catches a route naming a ROUND passed WITHOUT the widening -- it "
            "matched `is a REVIEWER` in the same sentence. Row 908 now says "
            "ONLY a round name, and the regex is imported (bc.ROUTE), not "
            "duplicated: F131 and F138 at once, inside the harness that "
            "polices this arm. (2) `open-cycle set is ... non-empty at "
            "baseline` FAILED the first time the backlog reached ZERO, which "
            "is the GOAL STATE -- an arm that can only pass while the tree is "
            "UNHEALTHY is not a must-fire arm. It now plants an UNREVIEWED row "
            "in a STRING, which is what this file's own docstring prescribes. "
            "⭐ Rows 906/907 were added in the same pass: a STRUCK route is "
            "HISTORICAL and must not print, and striking one route must NOT "
            "mask a second live one -- or `unstruck()` would be a licence to "
            "hide."),
    "probes/ph70_overdec.sh": dict(
        kind="tool", argv=None, expect=None, negatives="none", st_expect=None,
        why="⭐ ROW 14's CRITERION-2 INSTRUMENT (`ph70`, E3, `array.c:3804` "
            "`array_reduce`). Three cells, REPEAT=3 each: adversarial with an "
            "ALLOCATED payload -> SIGSEGV rc=139 on all three; benign (no third "
            "argument, the other arm of the same `if`) -> correct; and ⭐⭐⭐ THE "
            "NEGATIVE CONTROL, an IS_LONG seed, which takes the SAME defective "
            "arm and is ALSO correct because a long has no allocated payload to "
            "free early. ▶ The row's blob MUST emit payload-bearing values or it "
            "measures nothing. "
            "⛔⛔ TWO DEFECTS IN THIS PROBE WERE FOUND BY RUNNING IT AND BOTH "
            "WERE THE AUTHOR'S. (1) Cell A was copied from a hand-run script "
            "FROM MEMORY and dropped the trailing read of `$seed`, so it "
            "returned rc=0 against a hand run that faulted 3/3 -- and the "
            "MECHANISM the author had written down was wrong: the churn only "
            "RECYCLES the block, the fault is the READ THROUGH THE DANGLING "
            "OWNER. (2) ⛔⛔⛔ THE HARNESS REPORTED rc=0 FOR A PROCESS THAT "
            "SEGFAULTED, because `$?` after a pipeline is `tr`'s status -- a "
            "criterion-2 probe whose entire claim is an exit status reported "
            "the WRONG exit status, in the direction that kills a row. Swept "
            "the committed probes: none has that shape."),
    "probes/ph69_refcount.sh": dict(
        kind="tool", argv=None, expect=None, negatives="none", st_expect=None,
        why="⭐ ROW 15's CRITERION-2 INSTRUMENT (`ph69`, E3, `php_pcre.c:590`). "
            "⛔⛔ EVERY CELL EXITS 0 ON PURPOSE -- like `ph66`, the target error "
            "is a WRONG ANSWER and the observable is the VALUE, not `rc` "
            "(`_062` §3.1). Cell C: `$m[1]` holds an ARRAY, `unset($m['word'])` "
            "drops the shared zval 1->0 and FREES it, and the surviving owning "
            "slot reads back as an INTEGER. ⭐⭐ `F133`(i) IS A YES HERE WITH A "
            "STRUCTURALLY MATCHED COMPARATOR: 5.0.0's SAME FILE already carries "
            "`(*entry)->refcount++` at `:1533`, guarding the same operation 943 "
            "lines away, and the correct site does the HARDER version. ⚠ Do not "
            "add it to item139's census until `_063` §7.1's `same_construct?` "
            "column lands -- the fourth column changes what `held` counts."),
    "probes/item125_extract.py": dict(
        kind="checker", argv=[], expect=0, negatives="none", st_expect=None,
        why="⭐ ITEM 125's POPULATION, AND IT IS PROMOTED OUT OF `.temp/` ON "
            "PURPOSE. `_063` §7.2 ruled that the genuinely uncovered citation "
            "case is a GENERATOR in `.temp/` with no committed twin and no "
            "validator role -- neither citecheck's §F6 arm nor its §H arm sees "
            "one. This produced the 27-item census that item125_demoted.py "
            "adjudicates, so leaving it in auto-`rm`-able scratch would make "
            "that 27 a number nobody can re-derive (F51/F99). ⛔⛔ AND THE "
            "ITEM-LEVEL GRANULARITY IS THE WHOLE POINT: a LINE-based grep "
            "misses F123's OWN FOUNDING INSTANCE, because `_051_REPORT.md` "
            "§8.1 straddles a line break (`cheapest remaining` on :440, `and "
            "it is not done` on :441). ▶ A count done the way item 125 "
            "SPECIFIES returns a set that excludes the one member we know is a "
            "member -- which is why the item as specified is REFUTED and the "
            "census had to be re-run at item granularity."),
    "probes/item125_demoted.py": dict(
        kind="checker", argv=[], expect=0, negatives="flag", st_expect=0,
        why="⭐⭐⭐ ITEM 125 ADJUDICATED -- and it is THE WORKED INSTANCE OF "
            "F139's CORRECTED AXIS. `_063` §6.1 refuted *location is not the "
            "variable*: the axis is TEXT vs AN INVOKED ARM. F123's repair was "
            "a PROSE BOX, three rounds carried it in capitals, and none did "
            "the work -- while F140's printing arm scoped the item on its "
            "first run. This file is that arm for item 125. "
            "⛔ ⓘ REPORT ONLY, rc=0 ALWAYS: a member sitting undone for six "
            "rounds is a FINDING, not a build error, and a checker that went "
            "red on it would be re-classified as noise inside a week (F135). "
            "⚠ ITS TRACKING TEST IS A PROXY AND SAYS SO: token recurrence is "
            "weaker than an answer, so it can only move a row OUT -- the "
            "printed member set is a LOWER BOUND. ⭐⭐ N4 EARNED ITS PLACE "
            "IMMEDIATELY: it refused its own author's hand verdict on `_035` "
            "within minutes, because the token chosen (`four spellings`) was "
            "generic enough to match unrelated text in three earlier reports "
            "and manufacture tracking that did not exist. ⭐ N2 RUNS the "
            "extractor rather than trusting a typed 27 (F138). ⭐ N3 forbids "
            "deleting the census's own false positives -- a census that hides "
            "its misses cannot be audited, and deleting them is the cheapest "
            "way to make this report look better than it is."),
    "probes/ph66_djbx33a_collide.py": dict(
        kind="checker", argv=["--selftest"], expect=0, negatives="inline",
        st_expect=0,
        why="ROW-13 SCOPING for ph66. ⭐ CATALOGUE.md's ph66 block says *the "
            "DJBX33A preimage the fixture needs was never computed; compute it "
            "before building* -- ⛔⛔ AND THAT NAMES THE WRONG DIRECTION. A "
            "preimage is a 64-bit zend_ulong target and every 33^k is a UNIT "
            "mod 2^64, so there is no digit structure to lift and 2^64 is not "
            "searchable. ⭐ But no preimage is needed: a NUMERIC bucket's `h` "
            "IS the user-chosen index, so run the hash FORWARDS and use the "
            "result as the index. Five arms; N2 and N4 are MUST-FIRE (the NUL "
            "is load-bearing; 33 is a unit) so the docstring's argument is "
            "CHECKED rather than asserted. ⚠ C-side scoping only -- it is NOT "
            "an admission argument and may never refuse a candidate "
            "(CLAUDE.md rule 6). ⓘ Promoted out of gitignored .temp/ the same "
            "day it was written, because the START HERE box cited it and a "
            "committed doc pointing at deletable scratch is F51/F99."),
    "probes/n14_mustfire.py": dict(
        kind="checker", argv=[], expect=0, negatives="inline", st_expect=None,
        why="⭐ §H EVIDENCE, COMMITTED RATHER THAN RUN ONCE AND DISCARDED: shows "
            "task_cost.py's N14 arm FAILING in both directions (ROWS stale "
            "against the gated corpus; a phantom row in ROWS). An arm that "
            "passes is not an arm that works -- F10. ⚠ It monkeypatches "
            "task_cost's ROWS/CLASS in-process and never writes; rc=0 means the "
            "demonstration held. ⓘ It is the first `.py` in probes/ and the "
            "reason _disk() now looks there at all."),

    # --- TASK_PHP_058, adjudicated BY HAND by the manager -------------------
    "php58_mutate_arms.py": dict(
        kind="checker", argv=[], expect=0, negatives="inline", st_expect=None,
        why="⭐⭐ §H DONE PROPERLY -- it ATTACKS the shipped control instead of "
            "exercising it. It mutates `controls/inside_share.py`'s four "
            "decisions in-process and asserts the control's own 7 must-fire "
            "arms CATCH each one: 5 must-fire mutations all caught, 1 "
            "must-NOT-fire clean. ⚠ `PROTOCOL_PHP.md` §H's own words -- *a gate "
            "run EXERCISES a validator on the rows that pass; it does not "
            "ATTACK it* -- and this is the attack. ▶ SWEPT: it builds nothing, "
            "runs in a second and never writes to a row."),
    "php58_record_share.py": dict(
        kind="checker", argv=["--selftest"], expect=0, negatives="flag",
        st_expect=0,
        why="⭐⭐⭐ COMPUTES F74's SHARE -- the OTHER quantity called "
            "`inside_share` -- for every built row from the COMMITTED records, "
            "running nothing. `(kernel_exclusive_ir / n_iters) / "
            "marginal_ir_per_call`, which is what every figure in RECAP_PHP.md "
            "and .memory-php/03-numbers.md actually is, and NOT what the rows' "
            "`controls/inside_share.py` computes. ⛔⛔ IT IS DELIBERATELY NOT A "
            "ROW CONTROL: it derives from the gate record, which every gate run "
            "rewrites, so it could never be pinned -- a sidecar that cannot be "
            "pinned is a number with no staleness signal. ⚠ Swept under "
            "`--selftest` and NOT bare: the bare run is a 360-cell REPORT, and "
            "a bare sweep reading a report as a verdict is the defect this "
            "registry's own header warns about. ⛔ THIS ENTRY CARRIED THE ARM "
            "COUNT AND N12 REFUSED IT -- correctly in form, wrongly in "
            "substance: the tool DOES run its arms and prints them, in the "
            "`ok <n> <name>` dialect `controls/inside_share.py` uses, which "
            "N12's `PASS|FAIL|OK` + `N<d>` pattern cannot read. ▶ The count is "
            "REMOVED rather than the regex widened (the registry's own rule), "
            "and the blind spot is open item 131 -- three tools now speak that "
            "dialect and N12 could not tell if any went silent."),
}


# ---------------------------------------------------------------------------
# The verdict arms are PURE FUNCTIONS of (disk listing, registry) so the
# selftest can drive them over synthetic inputs. `PROTOCOL_PHP.md` §H.
# ---------------------------------------------------------------------------
def audit(disk, registry):
    """Returns a list of problem strings. Empty list == clean."""
    problems = []

    unfiled = sorted(set(disk) - set(registry))
    for f in unfiled:
        problems.append(f"UNFILED: .tasks-php/{f} is on disk and not in REGISTRY "
                        f"-- adjudicate it BY HAND, never widen a pattern")

    stale = sorted(set(registry) - set(disk))
    for f in stale:
        problems.append(f"STALE: REGISTRY files .tasks-php/{f} and it is not on "
                        f"disk -- delete the entry or restore the file")

    for name, e in sorted(registry.items()):
        kind, argv, neg = e["kind"], e["argv"], e["negatives"]
        exp, st = e["expect"], e["st_expect"]

        if kind not in ("checker", "tool", "landing"):
            problems.append(f"{name}: kind {kind!r} is not one of "
                            f"checker/tool/landing")
        if neg not in ("inline", "flag", "none", "probe"):
            problems.append(f"{name}: negatives {neg!r} is not one of "
                            f"inline/flag/none/probe")

        # ⭐⭐ `probe` WAS ADDED 2026-09-15 FOR F131, AND IT IS LOAD-BEARING, NOT
        #    A LOOPHOLE. It means: this checker's must-fire negatives live in a
        #    SEPARATE committed file, because its assertions are about a LIVE
        #    document and cannot be shown failing without breaking that
        #    document. ⛔ A fourth enum value that merely PERMITTED a new shape
        #    would be regex-tuning by another name, so the entry must NAME its
        #    probe and the probe must itself be a registered, swept checker.
        #    Without that, `negatives="probe"` would be a stronger `none`.
        if neg == "probe":
            pr = e.get("probe")
            if not pr:
                problems.append(f"{name}: negatives='probe' but no `probe` key "
                                f"names the file that demonstrates the failure")
            elif pr not in registry:
                problems.append(f"{name}: names probe {pr!r}, which is NOT in "
                                f"this registry -- an unregistered probe is not "
                                f"swept, so it is evidence nobody runs")
            elif registry[pr].get("kind") != "checker":
                problems.append(f"{name}: probe {pr!r} is filed kind="
                                f"{registry[pr].get('kind')!r}, so the sweep "
                                f"never runs it")
        elif e.get("probe"):
            problems.append(f"{name}: carries a `probe` key but negatives is "
                            f"{neg!r} -- say which it is")
        if not e.get("why", "").strip():
            problems.append(f"{name}: no `why` -- every entry is adjudicated BY "
                            f"HAND and an entry without a reason is not one")

        # ⭐⭐ N3, THE ARM THIS FILE EXISTS FOR. A flag-gated checker whose
        #    selftest arm is not in the sweep runs its REPORT and is read as a
        #    VERDICT -- which is exactly what happened to task_cost.py.
        if kind == "checker" and neg == "flag" and st is None:
            problems.append(
                f"{name}: negatives are FLAG-GATED and `st_expect` is None, so "
                f"the sweep would run its REPORT and call it a VERDICT. File "
                f"`st_expect` or re-file `negatives`.")

        if kind == "checker" and argv is None:
            problems.append(f"{name}: kind=checker with argv=None -- a checker "
                            f"the sweep cannot run is not in the sweep")
        if kind != "checker" and argv is not None:
            problems.append(f"{name}: kind={kind} must not carry a sweep argv")
        if kind != "checker" and st is not None:
            problems.append(f"{name}: kind={kind} must not carry `st_expect`")

        # A non-zero steady state is allowed, but only WITH a reason that says
        # so -- otherwise a red checker becomes furniture, which is how
        # `citecheck` came to be red "for item 97" when it is not.
        for label, val in (("expect", exp), ("st_expect", st)):
            if val not in (None, 0) and "⛔" not in e.get("why", "") \
                    and "ALREADY LANDED" not in e.get("why", ""):
                problems.append(f"{name}: {label}={val} (non-zero) with no ⛔ in "
                                f"its `why` -- an adjudicated red must SAY it "
                                f"is one, and say WHY it is red")

    return problems


_ARMS_CLAIM = re.compile(r"(\d+)\s+arms\b")
# ⭐ AN ARM IS A LINE THAT CARRIES A VERDICT. A checker also prints `ⓘ` REPORT
#   lines that name themselves (`task_cost.py`'s `N15b`, `quota.py`'s VACUOUS
#   `N1`), and counting those inflates the total -- the first draft of this
#   scanned every `N<n>` token anywhere in the output and read 17 where there
#   were 16. ⛔ The question this arm exists to answer is "HOW MANY THINGS CAN
#   FAIL", so a report must not count. ⓘ Caught within hours of N12 landing, by
#   N12, on its own author's file.
#   ⚠ TWO LINE SHAPES EXIST IN THIS CORPUS and a derivation must take both:
#     verdict-FIRST   `  PASS  N1: ...`          (task_cost, cbaseline, checkers)
#     verdict-LAST    `  N1 MUST-FIRE  ... OK`   (contract_audit, quota)
#   ⛔ A pattern anchored on one of them reads the other as ZERO ARMS, which the
#   first attempt did to contract_audit -- and "observed 0" is exactly the
#   silent-checker failure N12c exists to catch, so a narrow pattern here would
#   have manufactured the defect it was written to detect.
_ARM_NAME = re.compile(r"\bN\d+[a-z]*\b")
_ARM_VERDICT = re.compile(r"(?<![A-Za-z])(?:PASS|FAIL|OK)(?![A-Za-z])")
_NOT_AN_ARM = "REPORT (no verdict)"


def _arms_in(text):
    """Arm names on lines that CARRY A VERDICT. A report is not an arm."""
    out = set()
    for ln in text.splitlines():
        if _NOT_AN_ARM in ln or not _ARM_VERDICT.search(ln):
            continue
        out.update(_ARM_NAME.findall(ln))
    return out


def arm_count_problems(registry, observed):
    """Every `"<n> arms"` claim in a `why`, checked against what the checker PRINTS.

    `observed` maps a registry name to the SET of arm tokens (`N1`, `N10b`, …)
    seen on that checker's own output across all the argv the sweep gave it.
    Pure, so the selftest can drive it over a synthetic map.

    ⛔⛔ THE DEFECT THIS EXISTS FOR, measured 2026-09-15: `task_cost.py`'s entry
    said *"15 arms"* and the file had **14**. The registry deliberately carries
    no count literal; its PROSE did, and nothing recomputed it. A `why` is read
    by a human deciding whether a sweep is thorough, so a count in one is load
    bearing.

    ⚠ A checker with no `"<n> arms"` claim is silently fine -- this arm polices
    claims that exist, it does not require one.
    """
    problems = []
    for name, e in sorted(registry.items()):
        m = _ARMS_CLAIM.search(e.get("why", ""))
        if not m:
            continue
        claimed = int(m.group(1))
        seen = observed.get(name)
        if seen is None:
            problems.append(f"{name}: `why` claims {claimed} arms and the sweep "
                            f"captured no output for it -- an unrunnable claim "
                            f"is the same defect one step earlier")
            continue
        if len(seen) != claimed:
            problems.append(f"{name}: `why` claims {claimed} arms; its own "
                            f"output names {len(seen)} "
                            f"({', '.join(sorted(seen)) or 'none'}). "
                            f"Recount and re-file -- a bound is not a derivation")
    return problems


def sweep(registry, runner):
    """Run every `kind == "checker"`'s STANDING arm and, where it has one, its
    SELFTEST arm. `runner(name, argv) -> rc`. ⛔ Skips this file (N10)."""
    out = []
    for name, e in sorted(registry.items()):
        if e["kind"] != "checker" or name == "checkers.py":
            continue
        rc = runner(name, e["argv"])
        out.append((name, e["argv"], rc, e["expect"], rc == e["expect"]))
        if e["st_expect"] is not None and e["argv"] != ["--selftest"]:
            rc = runner(name, ["--selftest"])
            out.append((name, ["--selftest"], rc, e["st_expect"],
                        rc == e["st_expect"]))
    return out


def _disk():
    """Every `.py` the ratchet is responsible for, as a flat list of names.

    ⛔⛔ THIS USED TO BE `.tasks-php/*.py` ONLY, AND `probes/` WAS A BLIND SPOT.
    It agreed with the truth for as long as `probes/` held nothing but C
    sources -- F49's shape and item 114's exactly: *a checker can agree with the
    truth for a long time because the state that would separate them has never
    occurred.* `n14_mustfire.py` is the first `.py` to land there, and it HAS a
    standing verdict, so without this it would have been a checker no ratchet
    could see. ⭐ Caught while adding it, not after.

    ⛔⛔ AND `.sh` WAS THE SECOND HALF OF THE SAME BLIND SPOT, LEFT OPEN FOR
    HALF A DAY. The first pass widened `.py` only, and `probes/fdset_census.sh`
    had been sitting outside the ratchet the whole time -- then the manager
    added `probes/rebuild_hardened_php.sh`, a script `PROTOCOL_PHP.md` §A3a now
    REQUIRES a row to run, and it landed outside the ratchet too. ⭐ This is
    exactly the defect `TASK_PHP_057` caught in `citecheck.py`: **a repair that
    fixes one limb of its own mechanism is worse than no repair, because the
    gap reads as closed.** ▶ Extensions live in ONE tuple now.
    """
    exts = (".py", ".sh")
    flat = [f for f in os.listdir(TASKS) if f.endswith(exts)]
    pdir = os.path.join(TASKS, "probes")
    if os.path.isdir(pdir):
        flat += ["probes/" + f for f in os.listdir(pdir) if f.endswith(exts)]
    return sorted(flat)


# Arm tokens seen on each checker's own output, accumulated by `_run` across
# every argv the sweep gives it. ⚠ It is a SET, not a count: `--selftest` and a
# bare run often print overlapping arms, and adding them would double-count.
_OBSERVED = {}


def _run(name, argv):
    try:
        r = subprocess.run([sys.executable, os.path.join(TASKS, name)] + list(argv),
                           capture_output=True, timeout=600, cwd=ROOT)
    except subprocess.TimeoutExpired:
        return "TIMEOUT"
    text = (r.stdout or b"").decode("utf-8", "replace") + \
        (r.stderr or b"").decode("utf-8", "replace")
    _OBSERVED.setdefault(name, set()).update(_arms_in(text))
    return r.returncode


def report(do_run=True):
    disk = _disk()
    problems = audit(disk, REGISTRY)

    print(f"REGISTRY: {len(REGISTRY)} filed, {len(disk)} on disk "
          f"(no literal -- the registry IS the ratchet)")
    n_flag = sum(1 for e in REGISTRY.values()
                 if e["kind"] == "checker" and e["negatives"] == "flag")
    n_chk = sum(1 for e in REGISTRY.values() if e["kind"] == "checker")
    print(f"  checkers {n_chk} · of which FLAG-GATED negatives {n_flag} "
          f"-- these are the ones a bare sweep does not check")
    print()

    if problems:
        print("⛔ PROBLEMS")
        for p in problems:
            print("   " + p)
        print()

    rows = []
    if do_run:
        print("SWEEP -- each checker with its FILED argv")
        rows = sweep(REGISTRY, _run)
        for name, argv, rc, exp, ok in rows:
            mark = "ok " if ok else "⛔ "
            print(f"  {mark}{name:24s} {' '.join(argv):12s} rc={rc} "
                  f"(expect {exp})")
        print()

        # ⭐ N12, and it can only run once the sweep has actually run: every
        # `"<n> arms"` claim in a `why`, checked against the arm names the
        # checker printed. Derived, not pinned -- see this file's header.
        claims = [(n, _ARMS_CLAIM.search(e["why"]).group(1))
                  for n, e in sorted(REGISTRY.items())
                  if _ARMS_CLAIM.search(e.get("why", ""))]
        print("ARM-COUNT CLAIMS -- `why` prose vs what the checker PRINTS")
        for n, c in claims:
            seen = _OBSERVED.get(n, set())
            mark = "ok " if len(seen) == int(c) else "⛔ "
            print(f"  {mark}{n:24s} claims {c:>3s}  observed {len(seen):>3d}")
        if not claims:
            print("  ⓘ VACUOUS TODAY -- no `why` states an arm count, so this "
                  "arm cannot fire. It is not passing.")
        print()
        problems += arm_count_problems(REGISTRY, _OBSERVED)
        if problems:
            print("⛔ PROBLEMS (after the sweep)")
            for p in problems:
                print("   " + p)
            print()

    bad = [r for r in rows if not r[4]]
    if bad:
        print("⛔ SWEEP MISMATCHES -- adjudicate each BY HAND, then re-file:")
        for name, argv, rc, exp, _ in bad:
            print(f"   {name}: got rc={rc}, filed expect={exp}")
        print()

    ok = not problems and not bad
    print("CHECKERS " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


# ---------------------------------------------------------------------------
# §H -- the must-fire negatives live in this file and feed `problems`.
# ---------------------------------------------------------------------------
def selftest():
    fails = []

    def check(tag, cond, msg):
        print(f"  {'PASS' if cond else 'FAIL'}  {tag}: {msg}")
        if not cond:
            fails.append(tag)

    print("SELFTEST — must-fire negatives")
    disk = _disk()

    # N1 MUST-FIRE: a new .py on disk is UNFILED.
    p = audit(disk + ["brand_new_probe.py"], REGISTRY)
    check("N1", any("UNFILED" in x for x in p),
          f"an unfiled .py on disk is caught: {len(p)} problem(s)")

    # N2 MUST-FIRE: a filed .py that has been deleted is STALE.
    p = audit([f for f in disk if f != "boxcheck.py"], REGISTRY)
    check("N2", any("STALE" in x for x in p),
          "a filed-but-absent .py is caught")

    # ⭐⭐ EVERY MUTATION ARM BELOW SCOPES ITS ASSERTION TO THE MUTATED ENTRY.
    #    An arm written as `any("X" in p for p in problems)` over the WHOLE list
    #    is satisfied by an unrelated real problem elsewhere -- which is how the
    #    first draft of N4 "failed" on `citecheck`'s genuine defect. A
    #    MUST-NOT-FIRE arm that another entry can satisfy is not an arm.
    def about(problems, name, needle):
        return any(p.startswith(name + ":") and needle in p for p in problems)

    # N3 MUST-FIRE ⭐ THE ARM THIS FILE EXISTS FOR: a flag-gated checker whose
    #    selftest arm is not in the sweep runs its REPORT and is read as a
    #    VERDICT.
    r = dict(REGISTRY)
    r["task_cost.py"] = dict(REGISTRY["task_cost.py"], st_expect=None)
    p = audit(disk, r)
    check("N3", about(p, "task_cost.py", "FLAG-GATED"),
          "a flag-gated checker whose selftest arm is NOT swept is caught "
          "-- this is the defect measured on 2026-09-15")

    # N4 MUST-NOT-FIRE: inline negatives need no selftest arm to be legal.
    r = dict(REGISTRY)
    r["quota.py"] = dict(REGISTRY["quota.py"], st_expect=None)
    p = audit(disk, r)
    check("N4", not about(p, "quota.py", "FLAG-GATED"),
          "an INLINE-negatives checker with no selftest arm is NOT flagged "
          "-- quota.py runs its arms on a bare run and must stay legal")

    # ⭐⭐ N4b/N4c/N4d MUST-FIRE: `negatives="probe"` was added 2026-09-15 (F131),
    #    and a new enum value that only PERMITS a shape is regex-tuning. These
    #    three assert it COSTS something: name a probe, have it registered, and
    #    have it swept.
    r = dict(REGISTRY)
    r["boxcheck.py"] = {k: v for k, v in REGISTRY["boxcheck.py"].items()
                        if k != "probe"}
    p = audit(disk, r)
    check("N4b", about(p, "boxcheck.py", "no `probe` key"),
          "negatives='probe' with no probe named is caught -- otherwise the "
          "value would be a stronger `none`")

    r = dict(REGISTRY)
    r["boxcheck.py"] = dict(REGISTRY["boxcheck.py"], probe="probes/nope.py")
    p = audit(disk, r)
    check("N4c", about(p, "boxcheck.py", "NOT in this registry"),
          "a named probe that is not registered is caught -- an unregistered "
          "probe is evidence nobody runs")

    r = dict(REGISTRY)
    r["quota.py"] = dict(REGISTRY["quota.py"], probe="probes/n14_mustfire.py")
    p = audit(disk, r)
    check("N4d", about(p, "quota.py", "carries a `probe` key"),
          "a `probe` key on a non-probe entry is caught -- say which it is")

    # N5 MUST-FIRE: an adjudicated non-zero expectation with no ⛔ in its reason
    #    turns a red checker into furniture. ⭐ This is the arm that exposed
    #    `citecheck` being red for a reason nobody had checked.
    r = dict(REGISTRY)
    r["citecheck.py"] = dict(REGISTRY["citecheck.py"], why="red, known debt")
    p = audit(disk, r)
    check("N5", about(p, "citecheck.py", "no ⛔ in its `why`"),
          "a non-zero expectation without a stated reason is caught")

    # N6 MUST-FIRE: an entry with no `why` at all.
    r = dict(REGISTRY)
    r["quota.py"] = dict(REGISTRY["quota.py"], why="   ")
    p = audit(disk, r)
    check("N6", about(p, "quota.py", "no `why`"),
          "an entry with an empty adjudication is caught")

    # N7 MUST-FIRE: a checker the sweep cannot run.
    r = dict(REGISTRY)
    r["quota.py"] = dict(REGISTRY["quota.py"], argv=None)
    p = audit(disk, r)
    check("N7", about(p, "quota.py", "argv=None"),
          "kind=checker with no runnable argv is caught")

    # N8 MUST-FIRE: a tool or landing script handed a sweep argv -- that is how
    #    a one-shot gets re-run by a routine sweep.
    r = dict(REGISTRY)
    r["land_m4.py"] = dict(REGISTRY["land_m4.py"], argv=[])
    p = audit(disk, r)
    check("N8", about(p, "land_m4.py", "must not carry a sweep argv"),
          "a landing script given a sweep argv is caught -- a one-shot in a "
          "routine sweep is a re-run waiting to happen")

    # N8b MUST-FIRE: the same one level over -- a non-checker with a selftest
    #    expectation would put a one-shot's arms in the routine sweep.
    r = dict(REGISTRY)
    r["php50_table.py"] = dict(REGISTRY["php50_table.py"], st_expect=0)
    p = audit(disk, r)
    check("N8b", about(p, "php50_table.py", "must not carry `st_expect`"),
          "a tool carrying a selftest expectation is caught")

    # N9 MUST-NOT-FIRE: the real registry is internally consistent. This is the
    #    arm that goes red when a NEW .py lands unfiled, which is the point.
    p = audit(disk, REGISTRY)
    check("N9", not p, f"the shipped registry is clean: {p}")

    # N10 MUST-FIRE: `sweep` must skip this file, or the sweep recurses.
    got = [n for n, *_ in sweep(REGISTRY, lambda n, a: 0)]
    check("N10", "checkers.py" not in got,
          f"the sweep does NOT run checkers.py recursively ({len(got)} arms)")

    # N10b MUST-FIRE ⭐ the selftest arm of every flag-gated checker is actually
    #    IN the sweep -- the whole point. A registry that files `st_expect` and
    #    a sweep that never runs it would satisfy N3 and check nothing.
    arms = sweep(REGISTRY, lambda n, a: 0)
    flagged = {n for n, e in REGISTRY.items()
               if e["kind"] == "checker" and e["negatives"] == "flag"
               and n != "checkers.py"}
    swept = {n for n, argv, *_ in arms if argv == ["--selftest"]}
    check("N10b", flagged <= swept,
          f"every flag-gated checker's --selftest arm is in the sweep: "
          f"{len(flagged)} flagged, missing={sorted(flagged - swept)}")

    # N11 ⭐ the registry must actually file every checker the manager's old
    #    hand-written sweep knew about, or this file narrows the sweep it
    #    replaces. The old sweep is quoted in the docstring of RECAP_PHP.md.
    old = {"boxcheck.py", "citecheck.py", "coverage.py", "quota.py",
           "contract_audit.py", "cbaseline_check.py", "preimage_screen.py",
           "fixsurvey.py"}
    missing = sorted(old - set(REGISTRY))
    check("N11", not missing,
          f"every checker in the manager's previous hand-sweep is filed: "
          f"missing={missing}")

    # ⭐ N12 -- the arm-count claims. `arm_count_problems` is PURE, so these run
    #   over a synthetic observation map and need no sweep.
    #   ⛔ THE DEFECT IT IS FOR: `task_cost.py`'s `why` said `15 arms` while the
    #   file had 14, and `cbaseline_check.py`'s said `9` while it had 10 AND
    #   printed no arm names at all. The registry carries no count literal; its
    #   PROSE did, and nothing recomputed it.
    r = {"x.py": dict(REGISTRY["quota.py"], why="⭐ 3 arms, all inline")}
    check("N12a", arm_count_problems(r, {"x.py": {"N1", "N2", "N3"}}) == [],
          "a `why` claiming 3 arms passes when the checker prints exactly 3")
    check("N12b", any("claims 3 arms" in p
                      for p in arm_count_problems(r, {"x.py": {"N1", "N2"}})),
          "⭐ a `why` that OVERSTATES its arm count is caught -- the "
          "task_cost.py `15 vs 14` defect, measured 2026-09-15")
    check("N12c", any("captured no output" in p
                      for p in arm_count_problems(r, {})),
          "⭐⭐ a `why` claiming arms for a checker that PRINTS NO ARM NAMES is "
          "caught -- the cbaseline_check.py defect: a silent pass makes the "
          "claim uncheckable, which is worse than wrong")
    check("N12d", arm_count_problems(
              {"y.py": dict(REGISTRY["quota.py"], why="no count here")}, {}) == [],
          "MUST-NOT-FIRE: a `why` with no arm-count claim is silently legal -- "
          "this arm polices claims that exist, it does not mandate one")

    print()
    print("SELFTEST " + ("PASS" if not fails else f"FAIL {fails}"))
    return 1 if fails else 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    sys.exit(report(do_run="--audit" not in sys.argv))
