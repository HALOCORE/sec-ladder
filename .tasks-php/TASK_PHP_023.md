# TASK_PHP_023 — review the nine new rows, then land them

**Role:** research **reviewer**. **One agent, alone.** `PROTOCOL.md` rule 1 — you
are **not** the agent that adjudicated these rows (`_019`) or the one that
trigger-tested them (`_021`).
**Report:** `.tasks-php/TASK_PHP_023_REPORT.md` — **write the FILE** (rule 10).

Read `.tasks/PROTOCOL.md`, **`.memory-php/`** (authoritative), **`PLAN_PHP.md`
§3 and §3.1** (the bar), `.tasks-php/PROTOCOL_PHP.md`, `patterns-php/CATALOGUE.md`
Part C, and **all three of** `.tasks-php/TASK_PHP_019_REPORT.md` (including §10),
`TASK_PHP_020_REPORT.md` and `TASK_PHP_021_REPORT.md`.

⚠⚠ **`RECAP_PHP.md` and `.memory-php/` ARE MANAGER-ONLY FOR WRITING.**
⚠⚠⚠ **NO EDITS under `harness/`, `common/`, `patterns/`, `results/`, `pilot/`.**
⚠ **Do not edit `patterns-php/ph07-strcut-cursor/`** — `TASK_PHP_024` owns it.
⚠ **No `git add` / `git commit`.** Never touch `.web/`.
⚠ Scratch under `.temp/php23/`. **Never `/tmp`.** `.temp/php19/`, `.temp/php20/`
and `.temp/php21/` hold the probes and `.temp/mgr165/count_ent.py` the entity
counter — **reuse them.**
⚠⚠ **`grep -a` ALWAYS** (41 corpus files are invisible to plain `grep`, including
`string.c` and `html.c`); **ask about a FUNCTION, not about text**; and **a probe
that CANNOT EVALUATE must say so, never `ok`.**

---

## §1 Why this exists

`TASK_PHP_021` was told to land nine new rows and **stopped itself**: 3 of 9
trigger lines failed, against its own rule of *"more than two → stop"*. **The
catalogue is byte-unchanged at 93.** `.tasks-php/land_019_020.py` is written,
45 anchors each resolving exactly once, verified on a scratch copy, **with the
three corrected triggers already in its text.**

⚠ **So the landing is one command. What is missing is that NOBODY HAS REVIEWED
the nine rows** — `_019` adjudicated them and `_021` checked their triggers, and
neither reviewed the other's admission reasoning. **93 → 102 on one agent's
judgement is what this task exists to prevent.**

## §2 The review

**For each of `ph94`–`ph102`** (`_019` §5 has the Part A rows and Part B blocks;
§10 has the `ph32`/`ph102` split):

1. ⚠⚠⚠ **THE BAR IS C-SIDE ONLY** (`CLAUDE.md` rule 6, `PLAN_PHP.md` §3). *"A
   worse kernel"*, *"needs a big input"*, *"safe Rust can't express it"*, *"no
   cost gradient"* are **findings, never kills**, and **mechanism *quality* is
   not a criterion — only *distinctness* is.** ⚠ **`patterns-php/` is FRESH:
   duplication with `patterns/` is NOT a filter.**
2. **Does the C support the admission?** `_019`'s rule was: `EXACT` if the two
   sites agree on the unchecked predicate, the attacker quantity **and** the
   fault primitive; `SLIGHT VARIATION` if exactly one differs (**§3.1 admits
   it**); `DIFFERENT MECHANISM` if two differ **or** the two defects have
   different upstream fixes each leaving the other standing. **Attack the rule
   as well as its application.**
3. **Do the citations resolve?** `_019` reports 13/13 in both directions.
   **Spot-check, and check the ones it called correct** — a survey that verifies
   only its exceptions measures its own priors (F21, F37).
4. ⚠ **Re-check the three corrected triggers specifically** (`ph94`, `ph98`,
   `ph101`), because they are the newest text and have had one pair of eyes.
   ⭐ **`ph94`'s correction is the one to attack**: `_021` measured that gcc
   narrows the 16-byte return through `mov %esi,%eax` at every `-O` level,
   *zeroing the padding the row is about*, so the read lands **inside** the
   string. **If that is right, is `ph94` still admissible at all, and on what?**
   The row's answer is that the kernel takes the un-written half from the blob —
   **is that a faithful extraction or an invented defect** (`PLAN_PHP.md` §4.2)?
5. ⚠ **`_019` flagged its own `echoes` as *"a reading — no `pNN` was opened"*
   and its `inv/obl` labels as derived.** Land them marked as derived; **do not
   upgrade them by fiat, and do not demand it opens the `pNN`s either** —
   duplication with PAT is not a filter here.

## §3 Then land, and only if §2 clears it

`python3 .tasks-php/land_019_020.py --check` then `--apply`. **It refuses unless
every anchor is present exactly once, and refuses on re-application.**

- **Verify after**: 102 rows in Part A **and** 102 blocks in Part B; the three
  section headings sum to 102 (the landing moves `ph92`/`ph93`, which are
  `spatial` rows sitting under the `Temporal` heading); `coverage.py` still
  **166/166**; every withdrawn `C.1` kill still **present, in place, marked
  re-adjudicated** — *a kill that vanishes is worse than a kill that was wrong.*
- ⚠ **`coverage.py`'s row regex is `ph\d\d` and is blind to `ph100`–`ph102`**,
  and its `gaps:` set is built from its own hit count, so it prints
  `99 … gaps: none` and **cannot report the blindness** (F49). **Its `166/166`
  is unaffected and is the number that matters** — but say what it does print,
  and **do not repair `coverage.py` in this task**; `_021`'s landing records it
  in `C.7`.
- ⚠ **If §2 does not clear a row, land the other eight and say which one you
  held and why.** A partial landing that is disclosed beats a whole one that is
  not. **The manager would rather have eight rows and a written objection.**

## §4 What I am least sure of

1. ⚠⚠ **That `ph101` should have counted as a failed trigger at all.** `_021`
   disclosed that its verdict on this row alone decided the stop — *"scoring it
   'additive' would give 2/9 and let the landing proceed"* — and I upheld it on
   the reading that a trigger raising `E_ERROR` and naming an undeclared class
   is *failed*, not *incomplete*. **If you think that was wrong, say so**: it
   cost a task, and I would rather know the stop condition is mis-calibrated now
   than at the next batch of nine.
2. ⚠ **That nine rows is a reviewable unit.** If the honest answer is that a
   proper C-side review of nine admissions is two tasks, **say that and do the
   first five** rather than thinning all nine.
3. ⚠⚠ **That `_019`'s `EXACT`/`SLIGHT VARIATION`/`DIFFERENT MECHANISM` rule is
   sound.** It is one agent's construction, it decided 10 of 13 reversals, and
   **the manager adopted it without review** — including its second disjunct,
   which I then used myself to overturn a verdict. **Attack the rule.**
