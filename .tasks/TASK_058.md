# TASK_058 — audit the documentation layer against the records. READ ONLY.

**Role:** research reviewer (adversarial). You do **not** fix; you report.

⚠ **THIS TASK EXECUTES NOTHING.** Another agent is building a pattern in this
tree right now and is taking wall-clock measurements. **You must not run
`harness/check.py`, `harness/measure.py`, `harness/build.py`, `./verus_run.py`,
any compiler, valgrind, Miri, or any binary under `.temp/`.** Reading files with
`grep`, `sed`, `python3 -c` on JSON/markdown, and read-only `git`, is all you may
do. CPU load from this task would corrupt another agent's `ns` column, and
`check.py` rewrites gate JSONs. **If an answer seems to need a run, report the
question instead of running it.**

**Read first:** `.tasks/PROTOCOL.md` (roles, severity, report format), then
`RECAP.md`'s START HERE box, then skim `.memory/` 00–06 for what each file
claims authority over.

## Why this task exists

This project's dominant defect class is **not** wrong measurement — it is
**numbers in prose drifting away from the records that produced them**. The
history is explicit about it: both of the numbering warnings written *to prevent
citation drift* had themselves drifted, in opposite directions, each asserting
the other's number; a layout-mode citation has been made to the wrong `.memory/`
file **27 times**; the gate's stage list said 16 stages when there were 18; and
in the commit immediately before this task the manager found the TCB census still
naming two exposures that had both been closed, five lines under a header that
contradicted it.

Every one of those was found by accident, by an agent doing something else. **Go
looking on purpose.**

## What to check

**C1 — prose numbers vs the records.** For every pattern, reconcile the figures
quoted in `patterns/pNN-*/NOTES.md` and `README.md` and `results/tables/pNN-*.md`
against `results/gate/pNN-*.json` and `results/pNN-*.json`. Mismatches in
`tcb_items`, obligation counts, twin obligation counts, `identity` levels,
`Ir`-per-call figures and checksum counts are the target. **Quote both sides.**

⚠ **Two `Ir` conventions are in play and they diverge by 13× on p08** —
kernel-exclusive (`results/*.json`) vs whole-program marginal
(`marginal_ir_per_call`, which is what the published tables read). See
`.memory/03-measurement.md:479` and `:508`. **A figure is only wrong if it is
wrong in the convention it claims.** Check that each one says which.

**C2 — cross-file contradictions.** `RECAP.md`, `.memory/` 00–06, `PLAN.md`,
`TOOLCHAIN.md`, `CLAUDE.md` and the 16 patterns' docs. Where two files state the
same fact with different values, report both with line numbers. `.memory/` is
**authoritative and supersedes any task report it contradicts** — so a `.memory/`
error is more severe than the same error in a `.tasks/` report.

**C3 — citations that have moved.** Every `file.py:NNN` and `file.md:NNN`
reference in `.memory/` and `RECAP.md`: does that line still say what the citing
sentence claims? Line-number citations rot silently. Report the ones that have
drifted, and say what is at the line now.

**C4 — stale counters.** Any spelled-out or numeric count of patterns, stages,
findings, records, items, or task numbers. The manager just fixed several; find
the rest. **The project's own rule is to print the count rather than trust a
constant** — flag any surviving constant that a command could replace, and give
the command.

**C5 — the two numbering schemes.** `RECAP.md` carries a digest list and
`.memory/01-ladder.md` carries a different one, one entry per pattern, and
RECAP's map table translates between them. **Verify that map row by row.** RECAP
also warns of a live collision at "finding 14" (ladder = p13, RECAP = *"every
rung is a spelling"*) and another at "13". **Check whether any citation anywhere
in the tree actually lands on the wrong one** — two task files have already done
this. That is the single highest-value item in this list if you find a live one.

**C6 — claims a pattern's own `NOTES.md` contradicts.** The known failure mode is
a headline copied from a report while the correction sat one paragraph below it.
Look for headline figures in `README.md`/`RECAP.md` whose own `NOTES.md` says
something weaker, narrower, or opposite.

## What is NOT wanted

- Style, wording, formatting, heading levels, typos. Ignore all of it.
- Suggestions to reorganise files.
- Anything that needs a run. Report the question.
- Padding. **Three real contradictions beat thirty cosmetic ones.**

## Deliverable

Write `.tasks/TASK_058_REPORT.md` **before you finish** (PROTOCOL rule 10), then
return the same content in the report format. For each finding give:
**severity** (`blocker` = a published number is wrong · `major` = two authoritative
files disagree, or a citation lands somewhere false · `minor` = a stale constant
with no consumer), **file:line on both sides**, the two values, and **which one
the records support.** If you cannot tell which side is right without a run, say
so and mark it `needs-measurement` rather than guessing.

Also report, explicitly: **what you checked and found CLEAN.** A named check that
passed stops the next agent re-running it, and this tree has been audited before
— PROTOCOL rule 6.

## Constraints

No root; no `/tmp` (scratch `.temp/t58/`); **no `git add`/`git commit`** — read-only
git only; **do not edit any file outside `.tasks/TASK_058_REPORT.md` and
`.temp/t58/`.** Do not edit `pilot/`, `.memory/`, `harness/`, `common/`, or any
pattern. **Execute nothing** — see the box at the top; that constraint is the one
most likely to be violated by accident here, because several checks would be
easier with a run. Report those as `needs-measurement`.

**If a premise in this task file is wrong, say so.** Eighty-nine agents have
contradicted the manager and all eighty-nine were right.
