# `.tasks-php/` — task files for the PHP programme

Mirrors `.tasks/` exactly. **`.tasks/PROTOCOL.md` is the protocol and is reused
unchanged** — roles, the manager's own rules, the definition of done and the
reviewer checklist are programme-independent. **`PROTOCOL_PHP.md` is the
addendum carrying what is new here** — §A extraction tiers · §B the allocator
rule and §B1a's O(1) precondition · §B5 family-B publishability · §C R1h · §D
provenance · §E the six-command sequence · §F what a php row owes · §G
duplication · §H validators land with their negatives.

> ⛔ **THIS PARAGRAPH SAID `PROTOCOL_PHP.md` WAS *"a Phase 0 deliverable, not yet
> written"* UNTIL 2026-09-15.** It is 1243 lines and is the most-cited document
> in the programme. **Stale since Phase 0, in the README of the directory it
> lives in** — `PROTOCOL.md` rule 13, and the same class as the RECAP cells that
> warn about themselves.

## The checkers

**`python3 .tasks-php/checkers.py`** — the register of every `.py` here, what it
is, and **the argv the sweep must use**. Run that rather than a hand-written
shell loop over each checker in turn. ⛔ **Several checkers run their §H
negatives only under `--selftest`, and a bare sweep runs their REPORT and reads
it as a VERDICT** — the tool prints how many on every run, under *"of which
FLAG-GATED negatives"*. It files itself, so the registry *is* the ratchet and
there is no count to go stale.

> ⛔⛔ **AND THIS PARAGRAPH CARRIED ONE ANYWAY** — it read *"5 of the 14
> checkers"* until 2026-09-15, when adding a sixteenth entry made it wrong in
> the same edit that added it. ⭐ **That is the day's third instance of the
> identical class**: `task_cost.py`'s `why` said *"15 arms"* with 14,
> `cbaseline_check.py`'s said *"9"* with 10 **and printed no arm names at all**,
> and this line. **The structures carry no literals; the PROSE ABOUT them did.**
> ▶ `checkers.py` **N12** now derives every `"<n> arms"` claim from what the
> checker actually prints — **and the fix here is not a better number, it is no
> number**: the count is one the tool reports.

> ⚠ **The old hand-written shell loop is deliberately NOT spelled out above, and
> the reason is worth one line.** It contained a shell variable inside a path
> under this directory. `citecheck.py` reads that as a rooted path citation and
> reports it as **rot** — so writing the loop out here added a rot entry **in the
> edit that documented the rot problem**, and the first attempt to explain the
> entry *in prose* added a **second** one, because the explanation quoted the
> string. ⭐ **Both removed the same day; the note survives without the string.**
> ⓘ **Fourth instance of *a check that reads prose and calls it code*** (item
> 115's class), and the *transient* half of F117 in miniature.

## Naming

| | |
|---|---|
| spec | `TASK_PHP_NNN.md` — written by the manager **before** the agent starts |
| report | `TASK_PHP_NNN_REPORT.md` — the agent's return message, landed by the manager |
| review | `TASK_PHP_NNN_REVIEW.md` / `_REVIEW_REPORT.md` |

⚠ **`PROTOCOL.md` rule 10: write the report file BEFORE citing it.** A
subagent's report exists only in its return message; if the manager lands the
corrections and moves on, the `_REPORT.md` everything now points at was never
created. Check before every commit that cites one:

```sh
grep -rhoa '\.tasks-php/TASK_PHP_[A-Za-z0-9_]*\.md' .memory-php/ .tasks-php/ RECAP_PHP.md PLAN_PHP.md \
  | sort -u | while read p; do [ -e "$p" ] || echo "MISSING: $p"; done
```

⚠ **One expected hit, and it is what a working check looks like, not a defect:**
a spec names its own report in its header before that report exists, so an
*unfinished* task always shows `MISSING: …_REPORT.md`. The PAT side has the same
exception for its `TASK_NNN.md` placeholder (`PROTOCOL.md` rule 10). **Ignore a
MISSING report for a task that is still open; investigate one for a task that is
closed.** ⚠ Silence, by contrast, is what a *broken* check looks like — the
`grep` matching nothing at all would also print nothing. ⚠ **`-a` added
2026-09-15** — it was missing, which is F35's rule broken inside the check that
enforces citation hygiene.

> ⛔⛔ **AND THE EXCEPTION IN THE PARAGRAPH ABOVE WAS NEVER INHERITED BY THE
> CHECKER THAT REPLACED THIS GREP.** `citecheck.py` exits `1 if rot else 0` and
> counted an in-flight task's not-yet-written report as `rot`, **so it could not
> tell *a task is running* from *a citation rotted*** — the distinction this
> README states in words. ⓘ **Third un-inherited caution in three rounds**
> (F108's C-compiler rule and `_env_block`'s three-equal-fields caution were the
> first two) — which makes it a rate, not a coincidence.
>
> ✅ **CLOSED 2026-09-15 — and the claim above was narrower than anyone wrote.**
> `benign()` whitelisted `endswith('_REPORT.md')` all along, so a task with a
> **plain** report never moved the count. What moved it was the **SPLIT**
> naming: `TASK_PHP_054` returned `_REPORT_E2E3E4.md`, `_REPORT_E5E6E7E8.md` and
> `_REPORT_S4S5S6T2T4T6.md`, none of which ends in `_REPORT.md` — **that** is why
> rot read `1 → 4 → 1`. Measured by citing both spellings from the same live
> file: **1 and 2.** ▶ **Repaired, not documented**: `benign()` now matches both,
> with must-fire arms `N6a`/`N6b` and a `N6c` that keeps a missing task *spec*
> rot. ⚠ **Still read the COUNT, never the exit code** — the one standing rot is
> an adjudicated false positive and the exit code cannot say so.

## Sibling directory convention

`.tasks-php/` is dotted and `results-php/` is not — **because `.tasks/` is dotted
and `results/` is not.** The point of the mirror is auditability, so the php
tree matches the PAT tree name for name rather than being internally tidy.

## ~~The running count~~ — ⛔ **THE CONVENTION IS DEAD, AND SAYING SO IS THE POINT**

`PROTOCOL.md` rule 2's *"number of times an agent refuted the manager with a
measurement"* was to live in the closing paragraph of the newest
`TASK_PHP_NNN*.md` and **nowhere else**.

⛔ **Measured 2026-09-15: NO php task file carries it, and the phrase appears
nowhere in `.tasks-php/` or `RECAP_PHP.md` at all.** The convention lapsed
silently and this README went on describing it.

▶ **It is recorded as lapsed rather than deleted, and NOT revived**, because the
thing it was a proxy for is now measured directly and far better: the **RULE-9
table in `RECAP_PHP.md`** verdicts every finding, and the programme's standing
record — *SIX consecutive review rounds refuted manager or engineer claims; in
`_053` not one finding survived as written, and in `_055` three of four
conclusions survived while ZERO of four REASONS did* — is a stronger rigour
signal than a counter nobody incremented. ⚠ **A lapsed convention left described
as live is worse than no convention**: it makes a reader think the signal exists.
