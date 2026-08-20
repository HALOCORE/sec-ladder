# TASK_051_REVIEW — p18 says R4's advantage over R2 vanishes under a build flag, and that claim is about every pattern here

**Role:** research reviewer. **You find what is wrong; you do not fix.**
**Read first:** `.tasks/PROTOCOL.md` (reviewer checklist, severity rules), then
**`.tasks/TASK_051.md`** (what was asked) and **`.tasks/TASK_051_REPORT.md`**
(what came back), then `patterns/p18-varint-shift/NOTES.md` **§0 first** and
`spec.md` in full, then `.memory/01-ladder.md` **findings 15 and 16** and **the
direction-test "IT FIRED" block**, `.memory/02-bench-rules.md`'s **"never compare
COST on an input where the unhardened rung commits UB"** and the threshold table,
`.memory/03-measurement.md`'s **null-control section and the hold-out rank rule**,
`.memory/04-verus.md`.

⚠ **The manager proposed p18's whole framing and got two of its surrounding
claims wrong** (it said ASan/Miri/a proof are all blind; UBSan and Miri both
catch it). PROTOCOL rule 3: it also designed the pattern. **Attack the design and
the §0 rejections, not just the execution.**

**A green gate is evidence about the gate.** `check.py p18` is PASS on a complete
run, 32/32 cells, Verus 12/0, Miri 9/9. Four reviews have found real defects past
exactly that — and **this pattern's own report shows the gate's Miri stage would
miss its bug if it keyed on the `ub` flag alone**, which is a fact about the gate.

## The six things most worth your time

### 1. "R4's law becomes character-for-character `safe_naive`'s" — this is a claim about EVERY pattern

p18 reports that `-C debug-assertions=on` **also turns on
`assert_unsafe_precondition!` inside `get_unchecked`** (named function
`…get_unchecked::precondition_check`, 14.00 `Ir`/byte at O0), so under `O0d`/`O3d`
**R4's fitted law equals `safe_naive`'s** and R4's advantage over R2 disappears.

**Almost every R4 in this project is built on `get_unchecked`.** If this holds it
is not a p18 fact — it is a statement about what R4 *is*, conditional on a flag,
and it belongs in `.memory/01-ladder.md` beside the R4-is-defined-by-permission
material. **Verify it, and compute its blast radius**: on how many of the 16
patterns does R4 rest on `get_unchecked` / `get_unchecked_mut`, and does the
collapse reproduce on a second pattern? **This is the highest-value item here.**

⚠ Also check the sub-claim that keeps it honest: *only 7.00 of 23.00 (safe) /
38.00 (unsafe) `Ir`/byte is the shift check, and 5 of those 7 are `-O0` spill
code.* If that decomposition is wrong, "O0d is not a shift check" is wrong.

### 2. The hold-out was replaced with a hashed pre-registration — is the new thing sound?

The engineer **reported its own design goal as failed**: p18's leave-one-band-out
**cannot fail** because the design has **3 columns** and stays rank 3 after
dropping any band. That is the third pattern in a row (p13, p14, p18). It
replaced the hold-out with a **hashed pre-registered extrapolation** — band `y`,
outside the convex hull 4× in both regressors, **24 predictions committed at
`sha256 ca0bbe26…` before measurement**, worst error 0.026.

**Attack the new method, because if it is sound it should become the project's
standard and if it is not, three patterns now have no valid out-of-sample test.**
Specifically: **is the hash actually verifiable from the committed tree** (can
you recompute it over the registered predictions and confirm it predates the
measurement), **could the extrapolation have failed**, and does "outside the
convex hull" mean anything for a design that is rank 3 in 3 columns?

⚠ And check the **column-count caveat** the report proposes: with 3 columns,
*every* leave-one-band-out is unable to fail. Is that right? p06's LOLO *does*
fail (−48.000 at `m=3`) — how many columns does p06 have?

### 3. The two claims the manager got wrong — verify the corrections

**UBSan catches it** (`-fsanitize=undefined` implies `-fsanitize=shift`; gate
stage 7 fires on all four adversarial blobs, ASan silent) and **Miri catches it,
as a PANIC rather than `Undefined Behavior`**. Both re-set p18's headline from
"nothing sees it" to "four catchers, all outside the 24-cell matrix". Re-run
both. **The Miri detail is a gate finding**: if `check.py`'s Miri stage keys on
the `ub` flag, it would record this bug as clean. Check what the stage actually
keys on and say whether the gate would have missed it.

### 4. `wrapping_shl` verifies — so "Verus catches this bug" is spelling-conditional

`checked_shl` / `overflowing_shl` / `unchecked_shl` are `is not supported`, but
**`wrapping_shl` VERIFIES at the pinned vstd**, so the obligation attaches to the
**operator spelling**, not the operation. The report prices it as a fiat with a
domain.

**Price it yourself and run the direction test in writing.** A pattern whose
headline is "the proof is one of only four things that catch this" while a
one-identifier respelling makes the proof silent is exactly the shape p13's
blocker 1 had. Is the fiat's price published beside the number it protects?

### 5. §0's rejections, and an adversarial row where every rung agrees

§0 **upheld** the catalogue row — the first in five patterns — and rejected four
candidates. **Attack the rejections**; they leave no artefact. In particular
`unbnd` *"is identical to guarded on all four blobs; it is p11"* — check that.

Then: **`adversarial-sat.bin` has ten undefined shifts execute, UBSan fire, and
all eight cells print the same number.** No fold can see the bug on that input.
**Is that row doing any work, or is it a row that cannot discriminate?** The
report calls it a property of the bug; decide whether that is a finding or a
gap, and whether a fold exists that *would* see it.

### 6. The self-corrected declaration, and the weak row

- **The engineer corrected its own `why` prose after building a control**
  (`NOTES.md` 12): a sentence said the scan-loop spelling was unpinned while
  `required[2]` pins `while p < len`. It says **no entry moved**. **Verify that**
  — a `why` edit is a declaration edit, and p14's equivalent disclosure was
  reviewed and upheld, so there is precedent either way. Run the direction test.
- **`large`'s `ns` row is weak** (P = 0.676 gcc / 0.829 clang, 48–65% within-cell
  spread) and the report says it is quoted with its P and not leaned on.
  **Check every place it appears** — including `README.md` and the results
  table — and confirm nothing quotes it as if it were the `small` row, whose
  P is 0.976/0.998.

## Also check, briefly

- **`R1h − R1 = 2.00·bytes`, zero intercept, zero per-varint, zero fitted
  parameters**, giving *"the safety line does not amortise"* at 11.89% / 11.11%.
  That is p07's never-amortises result on a new axis. Re-derive one coefficient
  from the listing.
- **`c_mask` has R1's cost law and R1's wrong answer, and UBSan is silent on it**
  — *"the sanitizer catches the undefinedness, not the wrongness"*. Strong if
  true; verify.
- **`m_wshl_ms` is not a memory-safety-only configuration** and its number is
  withdrawn — p17's control-2 lesson, **third instance**. Confirm the withdrawal
  is complete, i.e. no number derived from it survives anywhere.
- **p18's R4/R5 pair lands at offset 0**, not p06's and p14's 0x20. ⚠ The
  manager has **already written the 0x20 into `.memory/03-measurement.md`** and
  has softened it to "the offset is fixed per pattern, not that it is 0x20",
  marked PROVISIONAL pending you. **Confirm or correct that wording** — it is in
  the authoritative layer now.
- **`R3 − R4 = +1·b − 6·v + 7`** with R3 cheaper on both matrix inputs, reported
  as a **fixed-R4** reading with **no pair interval and no in-contract R4
  search**. Confirm nothing in the file reads as "safe beats unsafe".

## Clean negatives are worth as much as findings

PROTOCOL rule 6. **Name every attack that did NOT land.** p06's and p14's reviews
each built the thing the report said was missing and the headline survived; those
negatives are now the strongest evidence those patterns have.

## Deliverable

**Write `.tasks/TASK_051_REVIEW_REPORT.md` yourself, before your final message**
(PROTOCOL rule 10). Findings ranked `blocker` / `major` / `minor`, each with
**file:line and a concrete failure scenario**, plus the clean-negatives section.

## Constraints

No root; no `/tmp` (scratch `.temp/r51/`, **per-PID paths** — a shared path
corrupted a whole sweep on p14); **no `git add`/`git commit`**; do not edit
`pilot/`, `.memory/`, `harness/`, `common/`, **or any pattern.** Item 1 requires
measuring **other patterns' R4 cells** — that is building under `.temp/r51/`, not
editing them. Verus only via `./verus_run.py`. clang `~/tools/llvm/bin/clang`,
valgrind `~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none on
PATH. `timeout <N> <cmd>`. Never `pkill`/`killall`; **no `nohup … &`**; no
self-matching `pgrep` wait-loops. **Measurements in the FOREGROUND, interleaved
by cell.** ⚠ `check.py` rewrites its pattern's gate JSON; restore with
`git checkout --`. Notes to `.temp/r51/NOTES.md`.

⚠ **`.temp/p18/` was already in use by an earlier task** before this one started
(`bak-p*.md`, `gate-p*.log`, Aug 18). Do not assume everything under it is p18's.

**If a prescription here is wrong, say so with the measurement.** Seventy-eight
agents have contradicted the manager and all seventy-eight were right.
**What I am least sure of is item 1's blast radius**: I am asserting that
"R4 collapses to R2 under debug-assertions" is a project-wide fact because most
R4s here use `get_unchecked`. It may be narrower — p18's R4 may be unusual in how
much of its work sits inside the unchecked accessor — in which case the honest
statement is much smaller and belongs in p18's own file. **Measure it on at least
one other pattern before I write anything into `.memory/`.**
