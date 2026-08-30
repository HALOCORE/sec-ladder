# TASK_145 — review `p32`/`p33`, and attack its C-mechanism claim first

**Role: research reviewer.** Adversarial by design. **You do not fix; you
report.** A review that agrees without having tried to break something is a
failed review.

⚠⚠ **DO NOT START THIS UNTIL `.tasks/TASK_144_REPORT.md` EXISTS.**

Read first: `.tasks/TASK_144_REPORT.md` in full; `patterns/p32-*/`;
`.tasks/TASK_143_REPORT.md`'s `p32` section (the admission evidence);
`RECAP.md` findings **53** and **54**; `CLAUDE.md` **rule 6**;
`.memory/02-bench-rules.md`'s *THE ADMISSION BAR IS C-SIDE ONLY*;
`patterns/p27-handle-table/` and `patterns/p29-bst-delete/`.

## ⚠⚠⚠ THE ONE THING YOU MAY NOT DO

**You may not recommend refusing, shrinking or retiring this row for any
RUST-SIDE, VERUS-SIDE or LADDER-SIDE reason.** *"Safe Rust reproduces the bug
bit-identically"*, *"there is no cost gradient"*, *"the R5 cannot state the
obligation"*, *"no published column moves"*, *"Miri does not see it"* — **every
one is a FINDING. The first of them is this row's HEADLINE**, and it was
previously used to delete the row. **That deletion is the defect this whole
branch of work repairs.**

✅ **A row may legitimately fall on ONE ground only: its C MECHANISM duplicates a
built row's.** That is item 1.

## What to attack, in order of what a wrong answer costs

1. ⚠⚠⚠ **THE C-MECHANISM DISTINCTION, WHICH IS THE ONLY THING HOLDING THE ROW
   UP.** The claim: *nothing is malloc'd or freed per use; a stale FREE
   self-loops the list (`nx[h] = freehead` with `freehead == h`) so **two live
   handles ALIAS one block**; and that aliasing harm has no analogue in `p27` or
   `p29`.* **Try to show it IS `p27`'s or `p29`'s C mechanism.** ⚠ Note the
   shipped `spec.md` also says *"two bug classes, one omitted conjunct, selected
   by the input"* — **which is `p29`'s stated shape in words.** **Is the
   resemblance superficial or real?**
2. ⚠⚠ **THE HEADLINE'S CONTROL.** *"Safe Rust reproduces the buggy C bit for bit
   while the same source with `malloc` storage aborts"* is a two-cell
   experiment. **Verify the two cells differ ONLY in storage** — if anything
   else moved, it is an anecdote, not a controlled result. **Check the `malloc`
   arm's abort is the bug and not an unrelated fault.**
3. ⚠ **VACUITY AND THE ATTACK ARM.** The R5 owes an arm that must FAIL and a
   vacuity arm. ⚠ **`p42`'s ghost ledger verified `18/0` while leaking;
   `TASK_136`'s ARM_C was discharged by `fn arm_c() -> u8 { 9 }`.** **Try the
   ones the battery does not have**: unreachable body, a `requires` nothing can
   discharge, a postcondition true of the wrong program.
4. ⚠ **`model.py`'s INDEPENDENCE — verify it structurally, not from its
   docstring.** `TASK_136`'s model was a line-by-line transliteration of its own
   kernel and its bug went undetected because the two mirrored each other.
5. ⚠ **The R1/R1h construction.** `body.inc` is included twice so the two rungs
   provably differ by the safety line alone. **Diff the PREPROCESSED bodies and
   confirm.** ⚠ **Check the `+9/−0` figure and that nothing else drifted in.**
6. ⚠ **Positive controls.** `TASK_143` had **clang eliminate one of its positive
   controls** via malloc elision — `p31`'s artefact. **Confirm every control in
   the shipped tree actually executes.**

## Deliverables

1. **Per item: `SURVIVES` / `FALLS` / `SURVIVES, NARROWED`**, with the run.
2. **Is `p32` FINISHED?** ⚠ Gate-green is not finished — a pattern is finished
   when a reader can find its result. **Check `results/synthesis.md` carries it**
   (it was one pattern stale twice before) **and that the published table
   matches a fresh render.**
3. ⚠ **Anything in RECAP 54 or the catalogue cells the manager overstated.**
   The manager wrote both from the engineer's report plus its own re-runs, and
   **re-running a script checks the ARITHMETIC, not the EXPERIMENT DESIGN**
   (`.memory/03-measurement.md` entry 12 — the manager is the second instance).

## Rules

- `.temp/t145/` only. **You may not edit `.memory/`, `RECAP.md`,
  `results/SYNTHESIS.md` or `patterns/p32-*/`.** No `git add`/`git commit`.
- ✅ **You MAY run `harness/check.py` and `harness/measure.py`** — gate a single
  pattern, never the tree. ⚠ Records are not byte-reproducible.
- ⚠ **Read `blocked` out of the RECORD, never `grep` the log.**
- ⚠ **If you plant into `patterns/p32-*/`, restore in a `finally:` and verify by
  bytes against HEAD.**
- Verus via `./verus_run.py`, single-file mode, never `--cargo`.
- Hand-run sanitisers need `env -u LD_PRELOAD`; never truncate with `head`;
  every harm probe owes a positive control that must fire.
- Report to `.tasks/TASK_145_REPORT.md`. **PROTOCOL rule 2: the count is in
  `TASK_144_REPORT.md`'s closing paragraph — read it there, do not guess.**
