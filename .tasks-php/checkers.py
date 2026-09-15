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

⛔ That is not style. **FIVE hardcoded figures in `.tasks-php/` validators went
stale in this programme** — `task_cost.py`'s `owed = 34` (item 93), its
`total/rows ≈ 6.5` (three times inside one hour), `preimage_screen.py`'s `N10e`,
`task_cost.py`'s `EMPTY_FAMILIES = 14`, and its `ROWS` at 8 — and
`.memory-php/04-process.md` law 6 forbids the class. ⚠⚠ **`EMPTY_FAMILIES` is
the one to learn from: its guard `0 <= EMPTY_FAMILIES <= owed` was satisfied
forever by downward drift. A BOUND IS NOT A DERIVATION.**

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
        kind="checker", argv=[], expect=0, negatives="none", st_expect=None,
        why="RECAP_PHP.md's own invariants, incl. the 20-line START HERE box. "
            "No §H arms: every assertion IS a must-fire arm against a live file."),
    "citecheck.py": dict(
        kind="checker", argv=[], expect=1, negatives="flag", st_expect=1,
        why="⛔⛔ RED, AND **NOT** FOR THE REASON EVERY DOCUMENT GIVES. It exits "
            "`1 if rot else 0`, so ONLY the rooted-path rot count sets the code; "
            "item 97's §H material is a separate WARNING block that never "
            "touches it. The one standing rot is TASK_PHP_048.md:337's "
            "`TASK_PHP_005/006/008_REPORT` -- three files written as one path, "
            "in a paragraph headed 'NAME COLLISION, DO NOT BE MISLED'. A FALSE "
            "POSITIVE, adjudicated and NOT repaired: silencing a checker by "
            "editing its input is the opposite of the ratchet. ⚠ `rot` also "
            "rises transiently per in-flight task, because a task file cites its "
            "report before the report exists -- so READ THE COUNT, never the "
            "exit code. ▶ Both arms are red for this same one cause: --selftest "
            "fails N5d/N4, which assert rot == 0."),
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
            "9 arms, RATCHET=69 hand-adjudicated hits. ⛔ A bare run REPORTS and "
            "does not check -- the sweep must run the flag arm too."),
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
            "files unclassified). 15 arms; N1 also caught ROWS stale at 8 the "
            "moment it was first run."),
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
        kind="checker", argv=[], expect=0, negatives="none", st_expect=None,
        why="Has any php family-B figure been compared against its own R5-R4 "
            "null? Cites harness/check.py's null-control rule that no php "
            "document carried."),
    "width.py": dict(
        kind="checker", argv=[], expect=0, negatives="none", st_expect=None,
        why="F92: the probe_iters lever's gain is W^(-0.5), which settled item "
            "68 NO and refuted F90's operative half. ⚠ ~27 s -- the slowest "
            "entry, and the only reason the sweep is not instant."),
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
        if neg not in ("inline", "flag", "none"):
            problems.append(f"{name}: negatives {neg!r} is not one of "
                            f"inline/flag/none")
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
    return sorted(f for f in os.listdir(TASKS) if f.endswith(".py"))


def _run(name, argv):
    try:
        r = subprocess.run([sys.executable, os.path.join(TASKS, name)] + list(argv),
                           capture_output=True, timeout=600, cwd=ROOT)
        return r.returncode
    except subprocess.TimeoutExpired:
        return "TIMEOUT"


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

    print()
    print("SELFTEST " + ("PASS" if not fails else f"FAIL {fails}"))
    return 1 if fails else 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    sys.exit(report(do_run="--audit" not in sys.argv))
