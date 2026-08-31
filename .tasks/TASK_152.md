# TASK_152 — review `p35`, and attack the "GATE FORCES THE WEAKER PROOF" claim first

**Role: research reviewer.** Adversarial by design. **You do not fix; you
report.** A review that agrees without having tried to break something is a
failed review.

Read first: `.tasks/TASK_148_REPORT.md` **in full**; `patterns/p35-tagged-union/`;
`RECAP.md` finding **58**; `CLAUDE.md` **rule 6**; `.memory/03-measurement.md`
entries **19–22**; `.memory/06-catalogue.md`'s `p35` cell; `.temp/mgr147/NOTES.md`;
`patterns/p38-alias-pun/` (the tree's only other TYPE row) and
`patterns/p42-goto-cleanup/` (the standing precedent for shipping with a
proof-side gap).

## ⚠⚠⚠ THE ONE THING YOU MAY NOT DO

**You may not recommend refusing, shrinking or retiring this row for any
RUST-SIDE, VERUS-SIDE or LADDER-SIDE reason.** *"Safe Rust makes the bug
unreachable"*, *"the R5's obligation is an axiom, not a proof"*, *"the gate
blocks three rows"*, *"no cost gradient"* — **every one is a FINDING, and the
first two are this row's HEADLINE.** ⚠⚠ **This row was refused THREE TIMES and
every refusal was Verus-side or gate-side.** ✅ **A row may fall on ONE ground
only: its C MECHANISM duplicates a built row's.** That is item 1.

## What to attack, in order of what a wrong answer costs

1. ⚠⚠ **THE C-MECHANISM DISTINCTION.** *No free, no lifetime, no aliasing;
   the safety line is a statement ORDERING (`+2/−2`), a third shape after
   `p27`'s conjunct and `p13`'s store.* **Try to show it is `p38`'s** — the
   tree's other TYPE row — **or `p16`'s** (whose selector bounds a LENGTH rather
   than choosing a TYPE), **or `p19`'s**. ⚠ **`p38` is the sharpest attack: it
   is alias-punning, this is union-punning, and both end in "bytes read at the
   wrong type".** **Is the distinction in the C code or only in the vocabulary?**
2. ⚠⚠⚠ **THE HEADLINE: *"the GATE FORCES THE WEAKER OF TWO AVAILABLE PROOFS"*.**
   The claim is that Verus checks a union read **natively** (a language builtin,
   invisible to a `std_specs/` grep), while `_scan_unsafe_sites` requires the
   `unsafe` token inside a trusted body — **which is exactly what converts the
   checked read into an axiom.** ✅ The engineer measured both configurations
   with must-fail arms and ran the real `_scan_unsafe_sites` against a synthetic
   pdir. ⚠⚠ **RE-RUN BOTH CONFIGURATIONS YOURSELF.** Is the stronger proof
   really available and really refused? **Is there a THIRD configuration neither
   of us has found that is both gate-legal and genuinely checked?** ⚠ **If you
   find one, that is a major and it changes what ships.** ⚠⚠ **And check the
   inverse: is the shipped configuration's obligation REALLY an axiom, or is
   something else still checking it?**
3. ⚠⚠ **THE THREE BLOCKED ROWS.** `p35` ships `blocked = 3` — its union readers
   — and the manager has recorded that as *the row's R5 result, not a defect*.
   **Attack that.** Read `blocked` **out of the RECORD**. ⚠ **Is `block` the
   right verdict, or is it a `fail` the gate is being lenient about?** ⚠ **And
   does anything the pattern PUBLISHES depend on a blocked row?**
4. ⚠⚠ **THE SAFETY LINE IS CHEAPER THAN ITS ABSENCE** — `−13.71` to `−215.86`
   `Ir`/call, four figures, mechanism **declared OPEN**. ⚠⚠ **This project has
   published a headline wrong in the FLATTERING direction FIVE times, and
   *"hardening is free, in fact negative"* is the most flattering result
   available.** **Search BOTH spellings and count the levers on each side.**
   ⚠ Same for **`R3 beats R4 by 5.3%`** — `p10` and `p27` both published a
   safe-beats-unsafe headline that turned out to be an unsearched R4 side.
5. ⚠ **`model.py`, and `p35` is the tree's most exposed row to entry 19.** A
   Python model has **no unions**. **Did the engineer decide up front whether
   the harm is representable, and is `sanitizer_expect` DERIVED or DECLARED?**
   ⚠ **If derived, make it fire. If declared, check it says so plainly.** ⚠ And
   check any must-fire arm **REPORTS rather than crashes** when broken.
6. ⚠ **THE PROOF-MUTANT BATTERY (8/8) AND THE `p32` NON-GENERALISATION.** The
   engineer reports that `p32`'s spec-weaken arm does **not** generalise — `p35`
   fails at `wf_cells`. **Verify that**, and then **try the arms the battery
   lacks**: `assume(false)` (⚠ now a gate FAIL unless declared — check it is not
   declared), an unreachable body, a `requires` nothing can discharge, a
   postcondition true of the wrong program.
7. ⚠ **Positive controls, per detector.** ⚠⚠ **This row exists partly because an
   ASan-shaped control cannot license a UBSan column** (`.temp/mgr147/`).
   **Confirm every control executes, and that each licenses the detector column
   it is quoted for.** ⚠ Check clang has not eliminated any of them.

## Deliverables

1. **Per item: `SURVIVES` / `FALLS` / `SURVIVES, NARROWED`**, with the run.
2. **Is `p35` FINISHED?** ⚠ Gate-green is not finished — a pattern is finished
   when a reader can find its result. **Check `results/synthesis.md` carries it
   and that the published table matches a fresh render.**
3. ⚠ **Anything in `RECAP` 58, `CAVEATS["p35"]` or the catalogue cell the manager
   overstated.** ⚠⚠ **The manager has now shipped a wrong or over-general
   sentence into a task file THREE TIMES this session** (`p28d`'s `hp`;
   *"ASan structurally never reports a WRITE"*; repair 3's cost premise).
   **Assume the same here and look for it.**
4. ⚠ **The engineer's own disclosed near-misses** — a Miri call missing `--`
   that scored a non-run as *"no UB"*, and a wait loop that read the previous
   run's record. **Confirm the Miri result stands under a correctly-formed
   invocation**, and that no other number in the report came from a stale read.

## Rules

- `.temp/t152/` only. **You may not edit `.memory/`, `RECAP.md`,
  `results/SYNTHESIS.md` or `patterns/p35-*/`.** No `git add`/`git commit`.
- ✅ **You MAY run `harness/check.py` and `harness/measure.py`** — a single
  pattern, never the tree. ⚠ A single pattern's gate can take **30+ minutes**.
- ⚠⚠ **Read `blocked` and `verdict` out of the RECORD, never `grep` the log —
  and not with a regex alternation either.** `grep -oE 'PASS|FAIL'` reports
  `PASS-WITH-BLOCKED-ROWS` as `PASS`; `grep -c BLOCKED` decodes as `2N+1`; and a
  loop matching `^check.py: ` can read the PREVIOUS run's record. **Three
  mechanisms, one cure** (`.memory/03-measurement.md` entries 21–22, finding 58).
- ⚠ **If you plant into `patterns/p35-*/`, restore in a `finally:` and verify by
  BYTES against HEAD.**
- ⚠ **Do not touch any earlier `.temp/t*/` or `.temp/mgr*/`** — cited evidence.
- Verus via `./verus_run.py`, single-file mode, never `--cargo`. ⚠ **A
  `std_specs/` grep is the WRONG instrument for this row: union support is a
  language builtin.**
- Hand-run sanitisers need `env -u LD_PRELOAD`; never truncate with `head`.
- ⚠ `python3 harness/tools/contract_diff.py p35` says what moved inside the
  hashed block, from `git` alone.
- Report to `.tasks/TASK_152_REPORT.md`. **PROTOCOL rule 2: the count is in
  `TASK_148_REPORT.md`'s closing paragraph — read it there, do not guess.**
