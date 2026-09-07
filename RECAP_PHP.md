# RECAP_PHP — the handoff document for the PHP programme (`patterns-php/`)

**Read this first, always.** The manager updates it at every task boundary.
For the *other* programme (`patterns/`) read `RECAP_PAT.md`; for the split
between them read `CLAUDE.md`'s top table.

> ⚠⚠ **SIZE DISCIPLINE, AND IT IS A MEASURED LESSON, NOT A PREFERENCE.**
> `RECAP_PAT.md` reached **560 KB** and one pattern's `why` field became a
> single ~7,000-word JSON string. **Both stopped being read**, which is how a
> published limitation that did not exist got copied out of a stale header
> (`.tasks/PROTOCOL.md` rule 13). **The START HERE box stays ≤ 20 lines. A
> `spec.md` `why` stays ≤ 200 words.** If something needs more room it goes in
> `.memory-php/` or the row's `NOTES.md`, not here.

---

## ▶ START HERE — the next action, in ≤ 20 lines

```
STATE      NOTHING BUILT. The programme opened 2026-09-07.
           Renames landed (RECAP_PAT.md / PLAN_PAT.md); PLAN_PHP.md written.
           patterns-php/ harness-php/ results-php/ .tasks-php/ .memory-php/
           common-php/ DO NOT EXIST YET -- Phase 0 creates them.

RUNNING    3 read-only mining agents over the PHP 5.0.0 corpus (temporal,
           spatial, type), writing to .temp/php-mine/<axis>/.
           Their reports are NOT IN YET. Do not predict them.

NEXT       (1) TASK_PHP_002 -- Phase 0 foundation. WRITTEN AND COMMITTED,
               NOT YET LAUNCHED. Construction is 1-agent-at-a-time, so it
               waits for the miners to finish. Launch it first.
           (2) land the miners' output into patterns-php/CATALOGUE.md
               -> adjudicate + review, ONE agent at a time

BAR        C-SIDE ONLY. Nothing about Rust/Verus/Miri/cost may kill a row.
           patterns-php/ is FRESH: duplication with patterns/ is NOT a filter.

READ       PLAN_PHP.md (the design + all 10 decisions), then
           .tasks/PROTOCOL.md (reused unchanged), then .memory-php/.
```

---

## What is true now

| | |
|---|---|
| **rows built** | **0** |
| **tasks** | `TASK_PHP_001` mining wave RUNNING · `TASK_PHP_002` Phase 0 written, not launched |
| **catalogue** | not yet written — Phase 1 |
| **infrastructure** | not yet built — Phase 0 |
| **citation base** | PHP 5.0.0, pristine tarball, sha256 `5783e0c0…d6919`, 5595997 B, 3815 entries. **4.0.x ignored** (`DP-06`) |
| **rungs** | all five, R4/R5 may land as findings (`DP-02`) |
| **PAT tree** | untouched and must stay so — `harness/*.py` and `common/*.py` are hashed into all 33 gate records (`PLAN_PHP.md` §2.1) |

### The rename, and what it cost

`RECAP.md` → `RECAP_PAT.md`, `PLAN.md` → `PLAN_PAT.md`.

- ✅ **Zero gate runs, zero re-measures.** Measured: `grep -nE
  '(grep|awk|sed)[^|]*\b(RECAP|PLAN)\.md' harness/*.py` → **0 hits**, so no
  *runnable* citation lived in a hashed file. The prose mentions that do live
  there were deliberately left alone.
- ✅ **Seven runnable-command citations repaired and RE-RUN**, in
  `.tasks/PROTOCOL.md` (rules 1 and 10), `.memory/01-ladder.md`,
  `.memory/02-bench-rules.md`, `.memory/03-measurement.md` and `RECAP_PAT.md`
  ×2. Rule 1's loop prints only `p01` (the documented benign exception) and
  rule 10's prints only the three `TASK_NNN` placeholders — both exactly as
  `PROTOCOL.md` predicts, which is what a working check looks like.
- ⚠ **Two pre-existing drifts surfaced and were NOT repaired**, because they
  are numbers inside findings rather than paths:
  `.memory/03-measurement.md` says *"13 PROVISIONAL lines"* and the count is
  now **16**; `.memory/01-ladder.md`'s `NR>109 && NR<930` window is stale
  against a file this long and returns finding **21**, not the highest.
  Recorded here so they are not mistaken for rename damage.
- ⚠ Historical citations of the old names in `.tasks/`, `patterns/*/`,
  `pilot/` and inside findings are **left on purpose** and resolve to the
  `_PAT` files. Do not "fix" them.

---

## Findings

*(none yet — the first row has not been built)*

---

## Open items — carried, not closed

| # | item | note |
|---|---|---|
| 1 | The pristine tarball lives under **another project's gitignored `.temp/`** and is deletable at any time | Phase 0 must land `patterns-php/SOURCES.md` with the sha256 + a per-file manifest before anything cites it |
| 2 | *"Where does the existing Rust port land on these scales?"* | **deferred, not deleted** (`DP-05`). Well-posed once the corpus exists |
| 3 | `.web/` does not know `results-php/` exists | deliberate. Do not teach it until there is something worth publishing |
