# TASK_169 — review `TASK_168` and the manager's fold, and attack the TWO NEW GATE STAGES first

**Role: research reviewer.** Adversarial by design. **You do not fix; you
report.** A review that agrees without having tried to break something is a
failed review.

⚠⚠⚠ **`TASK_168` ADDED TWO NEW GATE STAGES (`0c`, `0d`) AND WIDENED A PARSER.**
The gate is the instrument all 33 records rest on; a defect there does not spoil
one row, it spoils the certificate on every row. **And every review in this
session has found real defects past a fully green sweep** — `TASK_165` found
three majors, `TASK_167` found nine and killed five manager claims including one
marked `✅ manager-re-derived`.

⚠⚠ **`PROTOCOL` rule 3: the manager wrote `TASK_168`'s spec AND has already
landed its fold into `.memory/03-measurement.md`, `.memory/05-layout.md`,
`PROTOCOL.md` rule 6 and `RECAP` finding 65 + queue items 37–39 — from an
unreviewed report, the same day.** Item 5 is that half and it is mandatory.

Read first: `.tasks/TASK_168_REPORT.md` **in full**; `.tasks/TASK_168.md`;
`git show 0678b2d` (**the whole landing — read the diff, not the files**);
`RECAP.md` **finding 65** and queue items **37, 38, 39**;
`.memory/03-measurement.md`'s `rep`-string sections;
`.memory/05-layout.md`'s digest-cost section; `PROTOCOL.md` **rule 6**.

✅ **NO SWEEP AND NO RE-MEASURE IS NEEDED FOR ANY ITEM.** Every arm is a pure
function or a selftest cell and can be driven **in process**. ⚠ **If you believe
one is needed, say so and STOP.**

✅ **Pre-settled by the manager — do not spend the review on these:** the tree is
`30 PASS + 3 PASS-WITH-BLOCKED-ROWS`, 0 failures, `blocked` `p01` 1 / `p35` 3 /
`p42` 1, read from the records; `synthesis/outward_ir.json` is **33 of 33 stale**
against its own gate pin; `results/synthesis.md` prints `p42`'s `+4160.00` in
bold in the `≥ CONFIDENT` band; `.memory/` already stated the `memset` crossover
at **2–4 KiB** and the `memcpy` one at **8192** in two different sections.

---

## 1. ⚠⚠⚠ THE TWO NEW STAGES — do they FAIL OPEN?

`0c` (a `check\.py:\d+` scan under `patterns/`) and `0d` (the
`CODEGEN_CFGS`↔`build.py` cross-check), **six must-fire arms each**, placed
**above** `check_selftests`' `fixture.ensure()` early return.

- ⚠ **Drive every arm and break each one.** The engineer says it saw them fail;
  **see them fail yourself.** An arm nobody has watched fail is not an arm.
- ⚠⚠ **Attack `0c`'s REGEX, not its arms.** It fires on `check\.py:\d+`.
  **What does it miss?** `check.py:1249-1278` (a RANGE — the tree had one);
  `` `check.py` line 1249 ``; `harness/check.py:1249`; a citation in a `.md`
  rather than a `.py`; a citation inside a string literal or a docstring the
  scan should *not* flag. **Where is the line between a citation and a mention,
  and does the stage draw it in the right place?**
- ⚠⚠⚠ **AND THE ONE THE MANAGER MOST SUSPECTS: `0c` SCANS `patterns/` ONLY.**
  `.memory/` has **six** of its own and at least two are rotten
  (`03-measurement.md:3146 → check.py:2387`; `:3375 → check.py:2805`).
  **Is excluding `.memory/` right, or is it the stage's blind spot?** ⚠ **The
  manager decided `.memory/` is its own to fix; say whether the GATE should
  enforce the convention there too, and what it would cost.**
- ⚠ **`0d`**: `CODEGEN_CFGS` is a whitelist. **Does the cross-check actually
  read `build.py`'s live flag list, or a copy of it?** **A cross-check against a
  second hand-maintained list is the defect it was built to close.**
- ⚠ **Placement above `fixture.ensure()`** — confirm both stages really run when
  the fixture is missing, and that they cannot make a fixture-less run look
  green.

## 2. ⚠⚠ THE PARSER WIDENING — `vparse`'s `global` anchor

Three new arms, *"confirmed to fail against the old matcher"*, and **0 of 152
shipped `.rs` moved**.

- ✅ **Re-derive the 0-of-152**, and ⚠ **re-derive the "fails against the old
  matcher" claim** — that is the property that makes them arms rather than
  decoration, and it is exactly what `TASK_168`'s own item D warned about.
- ⚠⚠ **Now break the NEW matcher.** The old one was line-anchored; what is the
  new one anchored on, and what does *it* miss? **A `global` split across two
  lines; one inside a macro; one preceded by an attribute; one in a raw string;
  `global` as an identifier** (the old selftest has a case for that — does it
  still pass?).

## 3. ⚠⚠ ITEM A's ANSWER — the part that reached a PUBLISHED number

- ✅ **Re-derive `p42`'s `+4160.00` and its `1.0156 Ir`/byte**, and the
  **≈426 `Ir`** vector-path figure the *"~90% is counter"* claim rests on.
  ⚠⚠ **That second number is the load-bearing one and the manager did NOT
  re-derive it.** **Where does `426` come from, and is it the right
  counterfactual?** `safe_naive` zeroes and `unsafe` does not — **so is the
  honest correction *"divide by ten"*, or *"this row is comparing two different
  programs"*?**
- ⚠ **Re-derive the `rep` census** — 26 of 1052 windows, nine patterns, all
  `c-gcc`/`c-gcc-h` at `-O3`, all word-wise. **Does the scan see inlined `rep`
  in Rust cells at all, or only where it looked?** ⚠ **A scan that examines only
  C cells and reports *"zero Rust windows"* is `check_miri`'s
  whitelist-grep-called-a-census, third instance.**
- ⚠ **`p08` was the ONE pattern the old claim named. Is `p08` still in the
  set, and does the new nine-pattern figure CONTRADICT the old finding or
  WIDEN it?** The manager wrote *"widen"*; check.

## 4. ⚠ THE CITATION REWRITES — eight of them, in measurement-hashed files

`0` `check.py:NNNN` remain under `patterns/`. ⚠⚠ **But a rewrite that names the
WRONG function is worse than a rotten line number, because a function name reads
as durable.** **Check each of the eight against what `check.py` actually does
now**, and confirm the surrounding sentence still says something true.
⚠ **`p38`'s was rotten in BOTH coordinates** (`check.py:459-460`), so its
replacement had the least to go on.

## 5. ⚠⚠⚠ WHAT THE MANAGER OVERSTATED — mandatory, and it is where the last two reviews scored

Landed from an unreviewed report, same day:

- **`RECAP` finding 65** and its `✅`/`⊘` marks. ⚠ **`TASK_167` found a `✅` the
  manager had not earned. Check every one.** In particular the manager marked
  `✅` on: *"`.memory/` states the memset crossover three lines above the 8192
  figure"*; *"33 of 33 outward_ir stale"*; *"`results/synthesis.md` prints
  `+4160.00` in bold in the `every row is real` band"*; and the gate verdicts.
- **`.memory/03-measurement.md`'s rewritten blast-radius section** — especially
  *"roughly 90% of the term is COUNTER, not code"* and *"key on the signature,
  not the callee"*.
- **`.memory/05-layout.md`'s three new costs** and **`PROTOCOL` rule 6's new
  paragraphs**, including the prediction lesson.
- **Queue items 37, 38, 39** — ⚠ **item 37 asserts the repair is
  `synthesis/`-only and costs no sweep. Verify that before it becomes a task**,
  the way `TASK_167` verified `QUEUE_TRIAGE.md` and found an error.
- **The commit message `0678b2d`.**

## 6. ⚠ THE TWO DISCLOSED OVERRUNS AND THE PREDICTION

- **A re-measure stales the published table and stage 9c hard-fails it**
  (+5 renders, +6 gate runs). ✅ **Verify from `git show 0678b2d --stat`**, not
  from the report.
- **`p35` had THREE stale sidecars because a `controls/*.json` pins its own
  generator.** ⚠ **Is that true of all 46, or only of `p35`'s?** — the manager
  wrote the general form into `.memory/`.
- ⚠ **The prediction's wall-clock half was wrong because `reps`/`timing_cpu`
  are `argparse` arguments and the records were taken at non-default values.**
  **Confirm, and say whether any PUBLISHED number was taken at a non-default
  `--reps` or `--cpu`** — because if one was, the rule is bigger than a
  prediction lesson.

## Deliverables

1. **Per item: `SURVIVES` / `FALLS` / `SURVIVES, NARROWED`**, with the run.
2. ⚠⚠ **A verdict on `p42`'s `+4160.00`**: what should
   `results/SYNTHESIS.md`/`results/synthesis.md` say about it? **It is a
   published bold number in the confident band and the manager has not decided.**
3. ✅ **CLEAN NEGATIVES, NAMED.** `TASK_166` left ten and `TASK_167` fifteen —
   **do not repeat either set.**
4. ⚠ **Is the GATE finished?** Not *"is it green"* — **is there a stage whose
   arms could not fire, or a convention the gate states and does not enforce?**

## ⚠ NOT in this task

- **Any fix.** You report; the manager lands.
- **A sweep, a re-measure, or re-emitting `outward_ir.json`.**
- **Queue items 35 and 36** (auditing the 14 `undeclared` rows; promoting the
  two `.temp/` instruments) — the NEXT task. ⚠ **You MAY read
  `.temp/mgr164/QUEUE_TRIAGE.md`, and an error found there is worth more than
  most because it is about to become a task file.**

## Rules

- `.temp/t169/` for scratch. ⚠ **Do not modify any earlier `.temp/t*/` or
  `.temp/mgr*/`**; copy out. **No `git add`/`git commit`.**
- ⚠⚠ **DO NOT LEAVE A `pgrep -f` WAITER RUNNING** — a waiter's own command line
  contains the string it greps for, so its exit condition can never be true.
  **Use `wait <pid>` or a `.done` sentinel.**
- ⚠⚠ **Read `blocked`/`verdict` out of the RECORD, never `grep` the log**, and
  ⚠ **`rc=$?` after a PIPE reads the LAST command's status.**
- Verus via `./verus_run.py`, single-file mode, never `--cargo`.
- Hand-run sanitisers need `env -u LD_PRELOAD`; never truncate with `head`.
- ⚠ **If you plant into a tracked file, restore in a `finally:` and verify by
  BYTES against `git show HEAD:`.**
- Report to `.tasks/TASK_169_REPORT.md`. **Write the file before citing it.**

**PROTOCOL rule 2 running count: launched from 948**
(`.tasks/TASK_168_REPORT.md`, which carried 942 → 948 on six refuted manager
claims — the `8192` bar, the *"individual `mem*` CALL"* scoping, *"answerable
statically"*, *"names the callee"*, *"two `p35` re-runs"*, and the budget's
omission of the table/re-gate chain and of `outward_ir.json`).
⚠ **Reconciliation is the manager's job, not yours.**

⚠⚠ **The one I want attacked by name is item 1's last bullet: `0c` scans
`patterns/` ONLY, and I decided `.memory/`'s six citations are the manager's to
fix rather than the gate's to enforce. That is a scoping decision I made while
writing the fold, with nothing run, and it is exactly the shape of decision this
session has been wrong about repeatedly.**
