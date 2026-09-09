# TASK_PHP_019 — the MECHANISM test on every surviving duplication kill

**Role:** research **investigator / adjudicator**. **One agent, alone.**
**Report:** `.tasks-php/TASK_PHP_019_REPORT.md` — **write the FILE** (rule 10).
⚠⚠ **READ-ONLY OUTSIDE YOUR REPORT AND `.temp/php19/`.** You may not edit
`CATALOGUE.md`, `.memory-php/`, `RECAP_PHP.md`, `PROTOCOL_PHP.md`, `PLAN_PHP.md`
or anything under `patterns/`, `patterns-php/`, `harness*/`, `results*/`.
**Two other agents are running and one of them writes `patterns-php/ph07-*` and
`harness-php/provenance.py`** — stay out of both. **No `git add` / `git commit`.**
⚠ **`.web/` belongs to a CONCURRENT SESSION — never touch it.**
⚠ Scratch under `.temp/php19/`. **Never `/tmp`.**

Read `.tasks/PROTOCOL.md`, **`.memory-php/`** (authoritative), **`PLAN_PHP.md`
§3 and §3.1** (the bar), `patterns-php/CATALOGUE.md` Part C, and
`.tasks-php/ADJUDICATION_001.md` + `ADJUDICATION_002.md` (including
`ADJUDICATION_002` §5, which is a review of §2 by `TASK_PHP_017`).

⚠⚠ **`grep -a` ALWAYS** against the pinned tarball — plain `grep` in a `Bash`
call is a shell function dispatching to `ugrep`, which exits **1 with no output**
on any of the **41** corpus files holding a non-UTF-8 byte, **including
`ext/standard/string.c` and `ext/standard/html.c`, which this task must read.**
A probe script run under `sh` does **not** reproduce the failure. `/usr/bin/grep`
and the `Grep` tool are also safe. (F35, `PROTOCOL_PHP.md` §F6.)

---

## §1 The task, in one sentence

**`ADJUDICATION_002` audited the kill notes for a COST WORD. That test is
exhausted. Run the test it never ran, on every row it never ran it on: *does the
C support the mechanism claim?***

`TASK_PHP_017` §2.2 stated it as the general lesson and it indicts the manager's
method directly:

> *"ZERO of the remaining `C.1` notes contains a cost word, so
> `ADJUDICATION_002`'s predicted re-read finds nothing. The two that DO reverse
> need a different test — does the C support the mechanism claim? — which that
> document never runs on anything, including on its own two admissions."*

⚠ **It then ran that test on the 12 and reversed two** (`CRASH-126`,
`CRASH-163`) **in a review whose main job was something else.** Nobody has run
it deliberately. That is this task.

## §2 The population — `CATALOGUE.md` §C.1, every row, no exceptions

| kill | merged into | status coming in |
|---|---|---|
| `CRASH-090` | `ph32` | ✅ upheld with the C by `TASK_PHP_017` — **re-check it anyway**, briefly |
| `V5C-116` | `ph03` | *"merged by the corpus itself"* — `merged_members` confirms the MERGE, **not the mechanism** |
| `V5C-173` | `ph11` | same |
| `V5C-015` | `ph22` | same |
| `CRASH-037` | `ph39` | ✅ upheld with the C by `TASK_PHP_017` |
| **`CRASH-101`** | `ph39` | ⚠ **called a *slight variation*, which §3.1 ADMITS. Nobody has looked.** |
| **`CRASH-061`** | `ph60` | ⚠ **same. Nobody has looked.** |
| **`CRASH-126`** | `ph60` | ⚠⚠ **REVERSES** (`ADJUDICATION_002` §5). **Confirm or refute it, and if it stands, deliver the row.** |
| **`CRASH-163`** | `ph60` | ⚠⚠ **REVERSES.** Same. |
| `LOGIC-003` `-008` `-014` `-018` | `ph47` | ⚠⚠ a **four-row set kill** — F22/F27's shape, three instances already. `TASK_PHP_012` **M2 says 3 of 4 are refuted by the catalogue's OWN discriminator** and the finding is still owed. **Settle all four.** |

⚠⚠ **AND `C.4`'s SET KILL.** `CRASH-126` and `CRASH-163` were killed **twice** —
once under `C.1`, and once inside `C.4`'s *"ordinary null-deref set"*, which is
`F22`'s shape (**a kill written as a set hides its members**). **Enumerate `C.4`'s
set against `index.csv` and say how many members it has and whether each was
ever individually adjudicated.** ⭐ **Three prior instances make this a rule, not
a hunch** (F27): *a rejection covering N rows must enumerate the N against the
corpus index, not against the prose.*

## §3 The test, and it is C-side only

For each row, at the **pinned 5.0.0 tarball** (`patterns-php/SOURCES.md` gives
the sha256 and the manifest):

1. **Open the kill's cited lines and the surviving row's cited lines.** Quote
   both. ⚠ **Check the citations resolve** — `ADJUDICATION_001` was off by one on
   three of its own (F23), inside the passage arguing about citations.
2. **State each side's mechanism in C terms**: what is unchecked, what the
   attacker controls, where the write or read lands, what type the arithmetic is
   done in and where it is truncated.
3. **Verdict — and only these three are available**: `EXACT` (kill stands) ·
   `SLIGHT VARIATION` (**§3.1 ADMITS it as its own row — deliver it**) ·
   `DIFFERENT MECHANISM` (kill reverses).
4. ⚠⚠⚠ **THE BAR IS C-SIDE ONLY** (`CLAUDE.md` rule 6, `PLAN_PHP.md` §3). *"A
   worse kernel"*, *"muddies the extraction"*, *"needs a big input"*, *"safe Rust
   can't express it"*, *"no cost gradient"* are **findings, never kills.** ⚠ And
   **mechanism *quality* is not a criterion either** — only *distinctness* is.
   **`patterns-php/` is FRESH: duplication with `patterns/` is NOT a filter.**

## §4 Deliverables

1. **A verdict table**, all 13+ rows, with the C quoted for each.
2. **For every admission: a full Part A row and a full Part B block**, in
   `CATALOGUE.md`'s exact format — id, family, mechanism, tier, I/O class,
   corpus id, echo, status, then the ~150-word block with `▸ trigger`,
   `▸ benign`, `▸ blob`, `⚠ risk`. **New ids continue from `ph93`.**
   ⚠ **Do NOT edit `CATALOGUE.md`.** Deliver the text; the manager lands it.
3. **For every kill that stands: the note rewritten to say the mechanism reason**,
   because the current notes say a cost reason for a mechanism verdict even where
   the verdict is right.
4. ⚠ **The `C.4` enumeration**, against `index.csv`, with a count.
5. ⭐ **A base rate.** How many of the 13 reverse? `ADJUDICATION_001` predicted
   ~17 reversals and got them; `ADJUDICATION_002` predicted a cost-word re-read
   would find more and it **cannot**. **Say what fraction of a kill list this
   corpus's kill lists have historically got wrong**, and whether the remaining
   Part C sections (`C.2`, `C.3`) deserve the same pass. ⚠ **A LOW number is
   just as much a result as a high one** — this project has twice found that an
   audit which re-examines only what it doubts measures its own priors (F21,
   F37). **Do not go looking for reversals.**

## §5 What I am least sure of

1. ⚠⚠ **That *"merged by the corpus itself"* means anything at all.** Three
   kills rest on it and `merged_members` confirms the merge. **But the corpus's
   merge criterion is not this project's bar, and nobody has read it.**
   ⭐ **Find out what `merged_members` actually means** — if the corpus merged on
   *crash signature* rather than on *C mechanism*, those three kills rest on the
   wrong predicate and the strongest-looking evidence in `C.1` is the weakest.
   **This is the single question in this task I most want answered.**
2. ⚠ **That the four-`LOGIC` set kill is really one question and not four.**
   `TASK_PHP_012` M2 said 3 of 4 reverse; that finding has never been reviewed
   and is a manager-adjacent claim. **Attack it, do not apply it.**
3. ⚠ **That I am asking for the right lens.** *"Does the C support the mechanism
   claim?"* is `TASK_PHP_017`'s phrasing, not mine, and I am handing it on
   without having tested that it is decidable. **If it turns out to be a
   question that cannot be answered crisply for some row, say which row and
   why** — that is more useful than a forced verdict.
