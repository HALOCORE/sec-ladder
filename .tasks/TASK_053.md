# TASK_053 — sweep EVERY gate stage for the "skips a comparison in one branch" defect. AUDIT ONLY.

**Role:** research reviewer (adversarial, against the manager's own tooling)
**Read first:** `.tasks/PROTOCOL.md`, then `.tasks/TASK_051_REVIEW_REPORT.md`
**M6**, then `.tasks/TASK_052.md` **Part B** and its outcome block, then
`.memory/02-bench-rules.md`'s **threat model** (the "could this happen by
accident?" test) and **rule 5**, and `.memory/05-layout.md`.

## Why

Two instances of one defect shape have now been found in `check.py`, in a single
review, by an agent that was not looking for them:

1. **`check_miri`** — never compared exit code or stdout when
   `expected_exit != 0`, and the `ok` line asserted a match it had not made.
   Demonstrated with a real Miri run (rc=101, no UB) reported green. **Fixed at
   TASK_052**, regression check at
   `patterns/p18-varint-shift/controls/miri_exit_hole.py`.
2. **`check_sanitizers` (`check.py:4405`)** — binds the ASan+UBSan build's
   **stdout** and the name occurs exactly once in the function: never compared to
   `expected_stdout`, never stored, never in the gate JSON. **Reported, not
   fixed, no reproduction built.**

**Nobody has swept the other stages.** Two found by accident is the argument for
looking on purpose. `check.py` is ~5060 lines and 17 stages, and it is the thing
this project points at when it says a result is certified.

## The defect shape, stated precisely

> A stage computes a value that *could* discriminate, and then a branch, a guard,
> or a bare `else` lets a case through without comparing it — while the `ok`
> line, the gate JSON, or the verdict implies the comparison happened.

Three sub-shapes seen or suspected; look for all of them:

- **Value computed, never compared** (the `so` binding at `:4405`).
- **Comparison guarded by a condition that excludes the interesting case**
  (`expected_exit != 0` in `check_miri`).
- **An `ok` message that claims more than the code checked** — this is what made
  both instances *invisible*: the transcript said "matches the model".

## What to do

1. **Enumerate every stage** and, for each, list what it *could* compare and what
   it *does* compare. A table. This is the deliverable even where nothing is
   wrong.
2. For each candidate defect, apply **`.memory/02-bench-rules.md`'s threat
   model**: *could this happen by accident?* A hole only an adversarial author
   could reach is **not** a finding here — say so and move on. State the verdict
   per candidate; do not pad the list.
3. **Build a reproduction for every candidate that passes the accident test**,
   under `.temp/p53/`. A mutant or fixture that the current gate reports GREEN
   and that a correct gate would fail. **A candidate with no reproduction is a
   suspicion, not a finding** — label it as such.
4. **Check the `ok` strings across all stages** for the "claims more than it
   checked" shape specifically. That is cheap and it is what hid both known
   instances.
5. **Rank by blast radius**: which patterns and which rows are reachable today.
   `check.py:4405`'s known reachability argument is that the sanitizer build is a
   separate `-O1 -fsanitize=…` binary that stage 2's checksum agreement does not
   cover — **verify that** and do the equivalent for anything else you find.

## ⚠ AUDIT ONLY — do not fix anything

**Do not edit `harness/`, `common/`, `.memory/`, `pilot/`, or any pattern.**
Editing `check.py` makes all 16 gate records stale and forces a ~30-minute
re-run; the manager will batch every fix from this audit into **one** change so
that cost is paid **once**. Your deliverable is the report and the
reproductions.

**For each finding, include the fix you would make** (as a diff in the report,
not applied) so the batch is mechanical.

## Deliverable

**Write `.tasks/TASK_053_REPORT.md` yourself before your final message**
(PROTOCOL rule 10). Structure: the full stage table; then findings ranked
`blocker` / `major` / `minor`, each with `file:line`, the accident-test verdict,
the reproduction path, the blast radius, and the proposed diff; then
**clean negatives — every stage you checked and cleared, by name**, because that
list is what stops the next agent re-running this.

## Constraints

No root; no `/tmp` (scratch `.temp/p53/`, **per-PID paths**); **no `git
add`/`git commit`**. **Read-only on the whole tree except `.temp/p53/`.**
⚠ **Do not run `harness/check.py` on a pattern in a way that rewrites its gate
JSON** — if you must invoke it, copy what you need into `.temp/p53/` and run it
there, or use `git checkout --` afterwards and say so. Verus only via
`./verus_run.py`. clang `~/tools/llvm/bin/clang`, valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none on PATH.
`timeout <N> <cmd>`. Never `pkill`/`killall`; **no `nohup … &`**; no
self-matching `pgrep` wait-loops. ⚠ **Other agents are running concurrently on
other files. Do not touch anything outside `.temp/p53/`.**

Notes to `.temp/p53/NOTES.md` as you go.

**If a prescription here is wrong, say so with the measurement.** Eighty agents
have contradicted the manager and all eighty were right.
**What I am least sure of is whether this sweep is worth its cost at all** —
`.memory/02-bench-rules.md` rule 5 says *prefer producing a pattern over
hardening the gate*, and six tasks already went to gate work before the user
called it. My argument for overriding that is only "two instances, found by
accident, in one review". **If the sweep comes back with nothing that passes the
accident test, say so plainly and say the rule was right** — a clean bill of
health for 17 stages, with the table to back it, is a perfectly good result and I
would rather have it than a padded list.
