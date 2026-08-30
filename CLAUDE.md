# sec-ladder

Micro-benchmark for the performance ↔ memory-safety tension: each common C pattern
built at five rungs (C, safe Rust naive, safe Rust tuned, unsafe Rust, unsafe Rust +
Verus proof) × two optimisation levels, compared on assembly, instruction count,
timing, proof burden and trusted-base size.

## Where things are

**Start here, in this order** — the three files below carry the live state; the
rest is reference.

- `RECAP.md` — **the handoff document.** Its START HERE box is the next action.
  Read it first, always.
- `.tasks/PROTOCOL.md` — the agent protocol: roles, the manager's own rules,
  definition of done, the reviewer checklist. One agent works at a time.
- `.memory/` 00–06 — **the authoritative layer, and it supersedes any task report
  it contradicts.** 00 environment, 01 ladder + per-pattern findings, 02 bench
  rules, 03 measurement, 04 Verus, 05 repo layout, 06 the pattern catalogue
  (**48 rows** since TASK_066 added `p48`; count it with
  `grep -c '^| p[0-9]' .memory/06-catalogue.md` rather than trusting this line).

- `PLAN.md` — the original plan and feasibility argument. ⚠ **Historical**: its
  pattern table is a pre-project proposal with its own numbering and at least one
  bug class the project has since retracted. `.memory/06-catalogue.md` is the
  catalogue.
- `TOOLCHAIN.md` — running Verus (`./verus_run.py`), version pins, Verus conventions, what's missing on this box.
- `pilot/README.md` — calibration kernel at all five rungs; the evidence behind the plan.
- `harness/` — `asm.py` (**the only objdump caller in `harness/`** — ⚠ this line
  said "the only objdump caller" full stop, and **six patterns' `controls/`
  disassemble directly**: p08, p10, p12, p14 ×2, p16. They agree with `asm.py`
  exactly where checked, so the rule is *the gate* has one pipeline, not *the
  tree*), `vparse.py` (Verus items and
  clauses), `dloop.py` (driver loop → language-neutral tokens), `fixture.py`,
  `build.py`, `check.py` (the gate), `measure.py`, `report.py`. Run
  `harness/check.py pNN` before believing anything.
- `patterns/p01-array-sum/` — the template every later pattern clones. `spec.md`
  carries the kernel contract *and* the machine-readable pins the gate enforces
  (obligation count, every `requires`/`ensures`, the driver loop, the `Ir`
  floor, identity levels, Miri policy); `model.py` is the independent reference
  implementation the gate drives. Both are mandatory per pattern.
- `../LearnVeri/PITFALLS.md` — Verus gotchas; read before debugging.
- `~/tools/verus/vstd/` — **the PINNED vstd, and the only one that decides
  anything.** Grep it before claiming "no spec exists". ⚠⚠ **AND GREP
  `~/tools/verus/vstd/std_specs/` SPECIFICALLY, because that is where the specs
  for std types live and a `vstd/<mod>.rs` TRAIT DECLARATION IS NOT THE
  SPECIFICATION.** This exact confusion has now produced a false "no spec
  exists" claim **twice**: `copy_from_slice` (stood TASK_004→048) and
  **`index_mut` for a mutable sub-slice at TASK_089** — where `vstd/slice.rs`'s
  `ExSliceIndex` trait carries a `requires` and no `ensures`, while
  `std_specs/slice.rs` ships
  `assume_specification[ <Range<usize> as SliceIndex<[T]>>::index_mut ]` with a
  full **value-level** `final(r)@ == final(slice)@.subrange(...)`. ⚠ **Grep the
  INHERENT spelling as well as the free one** — `core::str::from_utf8_unchecked`
  is `is not supported` while `str::from_utf8_unchecked` verifies.
- `../LearnVeri/_VERUS_DOC_/` — Verus guide, plus a vstd source tree that is a
  **DIFFERENT, OLDER SNAPSHOT**. ⚠ Use it for the *guide*, never to settle
  whether a spec exists: it has **no `copy_from_slice` and no `copy_within` at
  all**, both of which the pinned vstd does have. *"vstd has no spec for
  `copy_from_slice`"* was false, stood from TASK_004 to TASK_048, and propagated
  into two patterns' comments — and this line, which pointed only here, is the
  most likely way it happened.
- `../LearnVeri/microbench/` — 20 CVE ports with security proofs; reusable kernels.

## Don't

1. **No `/tmp` scratch files** — use `.temp/` (gitignored), a subdir per category. `rm`
   is auto-permitted only under `.temp/`; elsewhere it stalls on human review.
   **Keep the generator, delete the artefact**: binaries, `.o`, `.pyc` and `.bin`
   blobs under `.temp/` are re-derivable (`harness/build.py`, `inputs/gen.py`) and
   get deleted once your gates are green; the `NOTES.md`, `.py` probe, `.rs`/`.c`
   source, `.json` and `.log` are the evidence and stay. If a blob has no script
   that rebuilds it, write one before finishing. Full rule and rationale:
   `.memory/00-environment.md` constraint 6.
2. **No blind process killing** — never `pkill`/`killall`/substring match. Confirm the
   full command line of an exact PID, then kill that PID. Prefer `timeout <N> <cmd>`.
3. **No GitHub-specific infrastructure** — no `.github/`, no CI config, no badges.
   Checks run locally, on request. Suggest automation; don't wire it up.
4. **Subagents never run `git commit`/`git add`** or any history-mutating git command.
   Read-only git is fine; the manager agent commits at task boundaries.
5. **Don't bump the Verus/vstd pin** without checking crates.io first — a driver whose
   vstd was never published panics `cargo verus` (`TOOLCHAIN.md`).
6. ⚠⚠⚠ **NEVER REFUSE OR REMOVE A PATTERN FOR A RUST-SIDE, VERUS-SIDE OR
   LADDER-SIDE REASON.** **Admission is decided SOLELY on the C program**: is it
   correct on benign inputs (so performance is measurable), does it exhibit the
   target error on an adversarial input, and is its **C mechanism** distinct
   from a built row's? **The Rust and Verus rungs are the NEXT step — do the
   best possible there, and whatever they land on is a RESULT to report.**
   ⚠ ***"Safe Rust can't express it"*, *"safe Rust reproduces the bug
   bit-identically"*, *"there's no cost gradient"*, *"the R5 can't state the
   obligation"*, *"no column moves"*, *"Miri doesn't see it"* and *"the bug is
   in-bounds so it's logical, not temporal"* are ALL FINDINGS, NEVER KILLS.**
   ⚠⚠ **This bias has shaped real refusals — six of ten temporal ones — and it
   went uncaught for many sessions because it lived IN THE ADMISSION BAR rather
   than in any single row, so row-level review could not see it.** Full rule and
   the audit: `.memory/02-bench-rules.md`, *THE ADMISSION BAR IS C-SIDE ONLY*,
   and `RECAP.md` finding 53. ✅ **C-side DUPLICATION remains a legitimate kill.**
