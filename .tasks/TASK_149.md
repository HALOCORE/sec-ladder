# TASK_149 — review `p28`, and attack the SAFE-RUST HEADLINE first

**Role: research reviewer.** Adversarial by design. **You do not fix; you
report.** A review that agrees without having tried to break something is a
failed review.

Read first: `.tasks/TASK_146_REPORT.md` **in full** (§1, §3a, §5, §6, §9a
especially); `patterns/p28-intrusive-lists/`; `RECAP.md` finding **56**;
`CLAUDE.md` **rule 6**; `.memory/03-measurement.md` entry **19**;
`.memory/01-ladder.md`'s four-outcome law; `.temp/mgr146/NOTES.md` **including
its retraction**; `patterns/p27-handle-table/`, `patterns/p29-bst-delete/`,
`patterns/p32-free-list-pool/`.

## ⚠⚠⚠ THE ONE THING YOU MAY NOT DO

**You may not recommend refusing, shrinking or retiring this row for any
RUST-SIDE, VERUS-SIDE or LADDER-SIDE reason.** *"Safe Rust cannot express it"*,
*"safe Rust has no bug so there is nothing to compare"*, *"no cost gradient"*,
*"the R5 proves one list and the bug needs two"*, *"the Rust rungs use slot
numbers so it is `p27` again"* — **every one is a FINDING, and the first two are
this row's HEADLINE.** `TASK_093` refused this row on exactly that ground and
**its other stated reason was measured false by its own review.**

✅ **A row may legitimately fall on ONE ground only: its C MECHANISM duplicates a
built row's.** That is item 1.

## What to attack, in order of what a wrong answer costs

1. ⚠⚠⚠ **THE C-MECHANISM DISTINCTION.** The claim: *the read path is CORRECT and
   the DESTROY path is INCOMPLETE — the INVERSION of `p27`, `p29` and `p32`,
   which all keep a correct free discipline and put the missing check on the
   read; and the dangling pointer lives INSIDE ANOTHER HEAP OBJECT's link field.*
   **Try to show it IS one of those three.** ⚠ **`p29` is the sharpest attack**:
   it also frees a real `malloc`'d record and reads through a stale reference.
   **Is "the pointer lives in a heap object rather than a stack local" a real
   distinction or a restatement?**
2. ⚠⚠⚠ **THE SAFE-RUST HEADLINE, WHICH IS THE ROW'S MOST INTERESTING CLAIM AND
   THE ONE MOST EASILY WRONG.** *"Deleting the safety line from safe Rust changes
   NO ANSWER on any input this pattern ships"*, with a **structural** reason (the
   stale entries form a SUFFIX because eviction order and chain order agree).
   ⚠ **The report itself says this is an argument plus a measurement over the
   SHIPPED INPUTS, not a proof.** **So: FIND AN INPUT THAT BREAKS IT.** A window
   where a bucket's chain order and the LRU order disagree; a PUT that walks past
   a stale entry; a re-insertion of an evicted key. **If one exists, the headline
   is scoped to the shipped inputs and must say so.** ⚠ **If you cannot find one
   after real effort, SAY THAT — a failed attack on this claim is worth more than
   a successful one elsewhere.**
3. ⚠⚠ **THE MUST-FIRE ARM, AND `model.py`.** `.memory/03-measurement.md` entry
   **19** exists because `p32` shipped a derived check that could not fire.
   `TASK_146` §3a says its own **first draft failed its own five-mutation test**.
   ✅ **Re-run that test, and then plant mutations IT does not have.** ⚠ **Ask
   the entry-19 question directly: is any predicate here a tautology of the
   model's own representation?** **And check that a broken detector REPORTS
   rather than crashes** — `p32`'s crashes, and this task file asked `p28` to fix
   that.
4. ⚠⚠ **`A6` VERIFIES WHILE LEAKING** — the affine-token family's fourth
   instance. **Verify that, and then ask what ELSE in this R5 is affine rather
   than linear.** ⚠ `p42`'s ghost ledger verified `18/0` while leaking and
   `p32`'s `assume(false)` verifies `15/0`. **Try the arms the battery lacks:
   `assume(false)`, an unreachable body, a `requires` nothing can discharge, a
   postcondition true of the wrong program.**
5. ⚠ **THE SLOT-NUMBER DIVERGENCE.** Every Rust rung stores links as `u8` slot
   numbers, not pointers. The defence is `controls/arm_rawptr.rs` — *"the slot
   table changed the PROOF BURDEN and not the PROGRAM"*, with Miri firing on the
   raw-pointer bug arm and **on nothing else**. **Verify BOTH halves**: that it
   fires where claimed, and that it is silent where claimed. ⚠ **A detector that
   fires on everything is not a detector, and neither is one nobody has seen fire.**
6. ⚠ **THE R1/R1h CONSTRUCTION AND THE `+9/+3` FIGURES.** The manager's own
   `p28d` variant was an **incorrect program** — it never initialised `hp` and
   SEGVed in the HARDENED arm on a BENIGN input, and the manager's verification
   never ran a detector on `fix`. **Diff the PREPROCESSED bodies of the SHIPPED
   rungs and confirm `+9/−0`, and confirm the `+3` shared lines.** ⚠⚠ **AND RUN
   EVERY DETECTOR ON EVERY (ARM × INPUT) CELL, INCLUDING THE HARDENED ARM ON
   BENIGN INPUTS.** That is the cell that was missed.
7. ⚠ **Positive controls.** `TASK_143` had clang **eliminate** one of its
   positive controls via malloc elision. **Confirm every control in the shipped
   tree actually executes**, and that each licenses the detector column it is
   quoted for (a control that fires only under ASan says nothing about UBSan —
   `.temp/mgr147/NOTES.md`).

## Deliverables

1. **Per item: `SURVIVES` / `FALLS` / `SURVIVES, NARROWED`**, with the run.
2. **Is `p28` FINISHED?** ⚠ Gate-green is not finished — a pattern is finished
   when a reader can find its result. **Check `results/synthesis.md` carries it
   and that the published table matches a fresh render.**
3. ⚠ **Anything in `RECAP` 56, `CAVEATS["p28"]` or the catalogue cell the manager
   overstated.** The manager wrote them from the engineer's report plus its own
   re-runs, and **re-running a script checks the ARITHMETIC, not the EXPERIMENT
   DESIGN** — ⚠⚠ **and on this very row the manager already shipped a wrong
   instruction that way** (`.memory/03-measurement.md` entry 12; `TASK_146` §1).
4. ⚠ **The one open number**: the record shows `safe_tuned` **dearer** than
   `safe_naive` in both conventions, direction stated and **mechanism not
   investigated**. **Is the direction real, and is it in-contract?**

## Rules

- `.temp/t149/` only. **You may not edit `.memory/`, `RECAP.md`,
  `results/SYNTHESIS.md` or `patterns/p28-*/`.** No `git add`/`git commit`.
- ✅ **You MAY run `harness/check.py` and `harness/measure.py`** — a single
  pattern, never the tree. ⚠ Records are not byte-reproducible.
- ⚠ **Read `blocked` out of the RECORD, never `grep` the log.**
- ⚠ **If you plant into `patterns/p28-*/`, restore in a `finally:` and verify by
  BYTES against HEAD.**
- ⚠ **Do not touch `.temp/t136/ t137/ t139/ t140/ t141/ t142/ t143/ t144/ t145/
  t146/ t147/ t91/ mgr146/ mgr147/ mgr148/ mgr149/ mgr150/ mgr151/`** — cited
  evidence.
- Verus via `./verus_run.py`, single-file mode, never `--cargo`.
- Hand-run sanitisers need `env -u LD_PRELOAD`; never truncate a sanitiser log
  with `head`; every harm probe owes a positive control that must fire.
- ⚠ `python3 harness/tools/contract_diff.py p28` says what moved inside the
  hashed block, from `git` alone — use it rather than re-deriving.
- Report to `.tasks/TASK_149_REPORT.md`. **PROTOCOL rule 2: the count is in
  `TASK_146_REPORT.md`'s closing paragraph — read it there, do not guess.**
