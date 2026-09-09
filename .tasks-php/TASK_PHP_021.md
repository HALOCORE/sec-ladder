# TASK_PHP_021 — land `_019` and `_020` into `CATALOGUE.md`, and trigger-test the nine rows they create

**Role:** research **engineer**. **One agent, alone.**
**Report:** `.tasks-php/TASK_PHP_021_REPORT.md` — **write the FILE** (rule 10).

Read `.tasks/PROTOCOL.md`, **`.memory-php/`** (authoritative), `PLAN_PHP.md` §3
and §4, `.tasks-php/PROTOCOL_PHP.md`, and **both reports in full**:
`.tasks-php/TASK_PHP_019_REPORT.md` (including **§10**, appended on resume) and
`.tasks-php/TASK_PHP_020_REPORT.md`.

⚠⚠ **`RECAP_PHP.md` and `.memory-php/` ARE MANAGER-ONLY FOR WRITING.**
⚠⚠⚠ **NO EDITS under `harness/`, `common/`, `patterns/`, `results/`, `pilot/`.**
⚠ **`.web/` belongs to a CONCURRENT SESSION — never `git add -A`, never touch it.**
⚠ **No `git add` / `git commit`.** Read-only git is fine.
⚠ Scratch under `.temp/php21/`. **Never `/tmp`.**
⚠⚠ **`grep -a` ALWAYS** — plain `grep` here is silently blind to 41 corpus files
including `ext/standard/string.c` and `ext/standard/html.c`, **both of which
this task must read.** Use `.temp/php17/r1h/fn.py` to extract functions.

**Bracket**: `harness/measure.py --check-stale` → **`66/0`**, first and last.
The php bracket is `harness-php/gate.py --tool measure --check-stale`; **record
what it says rather than what you expect** — `TASK_PHP_018` has been rebuilding
`ph07` and may have moved it.

---

## §1 The landing — mechanical, and it must REFUSE rather than guess

**`patterns-php/CATALOGUE.md` goes 93 → 102 rows.** Follow `land_m4.py`'s
precedent (`.tasks-php/land_m4.py`): **write a script with `--check` and
`--apply`, and make it refuse unless every anchor it expects is present exactly
once.** A landing that silently half-applies is worse than one that stops.

**From `TASK_PHP_019_REPORT.md`:**
1. **§5** — nine new rows `ph94`–`ph102`: Part A rows and Part B blocks, in the
   file's live format, under the right family headings.
2. **§4** — the `C.1` table rewritten. ⚠⚠ **Every withdrawn kill stays IN PLACE
   with its note**, marked re-adjudicated (`TASK_PHP_012` M1: *a kill that
   vanishes is worse than a kill that was wrong*). **Do not delete a row from
   Part C.**
3. **§10** — `ph32` rewritten (it keeps three tables sharing one fix) and
   **`ph102`** takes `ent_uni_punct`. ⚠ **`ph32`'s R1h is TWO commits** and the
   block must say so.
4. **`corpus rows` MOVES**: `CRASH-101` → `ph41` (not `ph39`), `LOGIC-014` →
   `ph48` (not `ph47`). ⚠ **`coverage.py` must still report every corpus id
   covered** — run it before and after and put both numbers in the report.

**From `TASK_PHP_020_REPORT.md`:** §7.1 (`ph21`), §7.2 (`ph93`), §7.3 (the seven
additive one-liners), and **§4's three strengthenings to `ph29`**.

**Mine, and they are small:** Part A's section headers read `Spatial (38)` ·
`Type / initialisation (22)` · `Temporal (31)` and sum to **91**. Recount all
three from the table itself. **Two rows carry an empty `tier` cell** — find them
and fill them, or say why they cannot be filled.

## §2 ⭐ THEN TRIGGER-TEST THE NINE NEW ROWS — this is the point of the task

`TASK_PHP_020` measured which half of a catalogue row is load-bearing, and the
answer was **not** the half anyone was auditing:

> **The defect site was wrong in 0 of 19 rows. The `▸ trigger` line would have
> cost an engineer time in 3.** Reachability is a build task's deliverable #1;
> an engineer starts by *running the stated trigger*. **Any follow-up audit
> should test `▸ trigger` lines only — 2–4 min/row once the file is open.**

**So apply it immediately, to the nine rows this same batch creates**, before
anyone builds against them. For each of `ph94`–`ph102`:

- **Does the `▸ trigger` reach the cited line, and does it produce the stated
  harm?** Read the C; where arithmetic decides it, **write the probe** —
  `TASK_PHP_020`'s `.temp/php20/ph29_probe.c` is the worked example, and it
  settled `ph29` by replicating the allocator's own lines verbatim.
- ⚠ **Three specific failure shapes to look for, because all three already
  happened**: a trigger the surviving guard *refuses* (`ph21`), one that reaches
  the line and *produces nothing* (`ph93`), one that fires *only through UB*
  (`ph29` — a `LONG_MAX + 1` gcc may fold). **A trigger that needs UB must be
  replaced with one that does not, and the row must say so.**
- ⚠ `TASK_PHP_019` §9 flags its own tiers as **placeholders** — *"every one of
  the eight is `narrowed`, which is a suspiciously uniform answer"*. **Re-derive
  each from the source.** A tier is a cost statement and **never a filter**.

**Report a rate**, in the same shape `_020` used: how many of nine needed a
trigger correction. ⭐ **A clean nine-for-nine is a real result** — it would say
the adjudicator's triggers are better than the catalogue's, which is worth
knowing before the next adjudication.

## §3 What NOT to do

1. ⚠⚠⚠ **Do NOT re-adjudicate.** Both reports' verdicts stand. If you think one
   is wrong, **land it anyway and say so in your report** — a landing task that
   silently overrules an adjudication destroys the audit trail, and the manager
   would rather have the disagreement in writing.
2. ⚠ **Do not touch `.memory-php/` or `RECAP_PHP.md`** (rule 4/9). Findings
   reach the authoritative layer through the manager, after review.
3. ⚠ `TASK_PHP_019` §9 also flags **`echoes` is a reading, no `pNN` was
   opened** and **`inv/obl` labels are derived, not the corpus's**. **Land them
   marked as derived**; do not upgrade them by fiat.

## §4 What I am least sure of

1. ⚠⚠ **That landing nine unreviewed rows is right at all.** Neither report has
   had a second pair of eyes; `_019`'s §10 was corrected by me mid-flight, and
   correcting is not reviewing. **The counter-argument is that `CATALOGUE.md`
   has been labelled UNREVIEWED since Phase 1 and this changes nothing** —
   ⚠ but it takes the corpus from 93 to 102 on one agent's judgement. **If §2's
   trigger test fails on more than two of the nine, STOP the landing and report;
   that is the signal the batch needs a review cycle, not a landing.**
2. ⚠ **That `coverage.py` can still see what it needs to after the moves.**
   `TASK_PHP_019` found it *"counts a mention in the KILL TABLE as coverage"*
   and that it **cannot detect an id merged into the wrong row by
   construction**. **Its 166/166 is therefore necessary and not sufficient — do
   not report it as if it certified the moves.**
3. ⚠ **That the two empty `tier` cells are a defect and not a deliberate blank.**
   Find out before filling them.
