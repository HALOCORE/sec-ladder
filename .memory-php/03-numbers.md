# `.memory-php/03-numbers.md` — what may and may not be compared

> ⚠ **`.memory-php/` is the AUTHORITATIVE layer for the PHP programme, and it
> SUPERSEDES any task report it contradicts** (`.tasks/PROTOCOL.md` rule 9).
> Only findings that have survived a full engineer→reviewer cycle are here.
>
> ⚠⚠ **SCOPE: this carries ONLY what is php-specific.** The PAT `.memory/`
> 00–06 applies unchanged — same harness, same bench rules, same measurement
> discipline, same Verus notes. **Do not restate any of it here; two copies of
> one rule is how both go stale.**
>
> The narrative, the open items and findings **F1–F106** live in `RECAP_PHP.md`
> (⚠ this said *F1–F41* for **forty-nine** findings, then *F1–F90* for **eleven** more — `PROTOCOL.md` rule 13, **and it has now rotted THREE TIMES.** ✅ **`.tasks-php/boxcheck.py` CHECKS THIS LINE against the actual highest finding as of 2026-09-13, so it is the last time.**
> **Count it yourself: `grep -c '^### F' RECAP_PHP.md`.**)
> ⭐ **And the statistic decision — which column every row publishes in — is
> `.tasks-php/STATISTICS_001.md`, committed. It was in gitignored `.temp/`.**

---


- ⚠⚠ **NEVER quote a `phNN` figure against a `pNN` one**, anywhere, including
  in prose. `repo_path_bytes` is **15 B** longer through the shim and
  `gate.py`'s `PYTHONDONTWRITEBYTECODE=1` adds **+34** and one env var.
- ⚠⚠ **And no two php runs are comparable to each other** unless the invoking
  shell matches: `ph00`'s own `envp_stack_bytes` moved **3 686 → 3 695** between
  two runs of the same gate with no source change. **Measure a mechanism; never
  difference two records taken in two shells and call the result its cost.**
- ⚠⚠ **`0 STALE` does NOT mean "everything is pinned".** `measure.py::_compare`
  iterates the **recorded** keys, so an **added** file is invisible — it has no
  key, so it cannot be stale. It means *every source that was pinned still
  matches*. What closes the gap is the **preflight**, not the digest. ⚠ This is
  a `harness/` property and affects all 33 PAT rows identically. (F14.)
- **The allocator is pinned by an UNCONDITIONAL symlink** — every php row
  carries `c/emalloc_shim.h` whether or not it allocates. ⚠ **Do not reintroduce
  a detector**: *"does this row use the allocator?"* was answered twice (a string
  search, then `gcc -MM`) and bypassed twice. **The question is not meant to be
  load-bearing.** (F10, F16.)

---

## Landed 2026-09-13 from `TASK_PHP_043` — which column, and what a figure owes

- ⭐⭐⭐ **WHICH STATISTIC RESOLVES A CODE DIFFERENCE IS DECIDED BY
  `inside_share`, AND IT IS ALREADY COMPUTED FOR EVERY CELL IN EVERY RECORD.**
  **Family A resolves a difference exactly to the extent the difference lands
  INSIDE THE KERNEL SYMBOL.** ▶ **So compute `inside_share` BEFORE choosing the
  column, not after the search disagrees**: `ph45` at **9.5 %** published in
  **W1**, `ph53` at **89.5 %** published in **A1**, and both were right.
  ⛔ **Two earlier candidate axes are REFUTED**: *same-language vs
  cross-language* (all nine of its own cells are same-language and separate by
  `|Δ|`) and *does the callee work diverge* (**a sign flip ENTAILS callee
  divergence, so the variable does not vary**). **Details and scope —
  two rows, nine cells — in `02-ladder.md`.** (F91 narrowed, item 78 answered.)

- ⚠⚠⚠ **A ROW'S SPREAD OVER RESPELLINGS IS A FACT ABOUT THAT ROW'S VARIANTS, NOT
  ABOUT THE STATISTIC.** `ph45`'s A1 spread over nine searched variants is
  **`0.000000` pp** against 66.7/44.5 pp whole-program; **`ph53`'s is `39.9`/`45.3`
  pp over 20.** ▶ **Same statistic, opposite answers, and the difference is
  `inside_share`** — every lever `ph45`'s search found lives in the callee `dec`.
  ⓘ **`ph45`'s `0.000000` is an instance of F86's `BLIND` class** (*A is exactly
  `0` while the whole-program figure is not*, 14 of 366), **which the programme
  already had a name for.** ⛔ **Do not quote either row's spread as evidence
  about family A.** (F100, item 82.)

- ⛔⛔ **EVERY PERCENTAGE OWES FOUR THINGS AND A PUBLISHED FINDING SHIPPED
  WITHOUT ANY OF THEM: THE STATISTIC, THE INPUT, THE OPT/MODE LEVEL, AND THE
  BASE IT IS AGAINST.** F98's *"the shipped R4/R5 carry a coverage witness the C
  rung does not have, and it costs `+21.8 %`"* is **W1**, on **`small.bin`**, at
  **`O3/isolated`**, **against `controls/r4_nowitness.rs` — a RUST control, NOT
  against the C** — and **only ~44 % of it is the witness** (`+101.59` of
  `+228.87` `Ir`/call; the rest is the array being in memory at all).
  ⭐ **The headline invited an R1-vs-R4 reading it could not support, and the
  attribution of a whole difference to one named cause is F83's shape.**
  (F98 narrowed.)

- ⚠ **NAME THE DENOMINATOR.** `ph29`'s family-B draw spread is **`range / mean`**
  — `31.42 %` on an independent 8-span sweep. **A second normalisation, `38.6 %`,
  is also in circulation and neither document said which it used.** (F88 upheld,
  item 92.)

- ⚠⚠ **`probe_iters` CANNOT BE WIDENED OUT OF THE PROBLEM, AND *"HOPELESS"* IS
  TARGET-DEPENDENT.** The width→spread exponent is **≈ −0.5** on both rows, so a
  *relative* target needs an unreachable width — ⚠ **but for an ABSOLUTE 1-pp
  target the probe's own TABLE 7 gives `W ≤ 574` on every pair.** ▶ **The `NO`
  on open item 68 stands anyway, and for a better reason: the lever cannot fix a
  BIAS at any width** — F93's start-of-run transient and F91's bias. ⭐ **And the
  F52 control is what makes the exponent believable: it recovers `−0.5047` from
  i.i.d. noise and `−0.9799` from endpoint noise, so the experiment does
  distinguish *a weak lever* from *measuring its own null*.** (F92 narrowed.)


> ⛔⛔⛔ **EVERYTHING FROM HERE TO THE END OF THIS FILE IS `UNREVIEWED`, MANAGER, 2026-09-13.**
> It comes from `TASK_PHP_044`, `_045` and `_046`, which are **ENGINEER** tasks:
> `PROTOCOL.md` **rule 9** requires an engineer→reviewer cycle and **these have had
> only the engineer half.** ⭐ It is kept here rather than held back, under the same
> convention `02-ladder.md`'s family-B sensitivity paragraph used — **marked, not
> hidden** — because a later session needs the rule and the mark tells it what the
> rule is worth.
>
> ⚠⚠ **AND THE MARK IS HERE BECAUSE I LANDED THIS MATERIAL UNMARKED FIRST.** I
> wrote the RULE-9 STATE block one day earlier, landed `04-process.md` law 12
> (*a manager finding from one probe or two rows should be assumed narrowable until
> a reviewer has had it*) — **and then put seven unreviewed entries into the layer
> that supersedes everything.** ▶ **Caught by auditing before a handoff, which is
> the only reason it is marked at all.** → the RULE-9 STATE block in `RECAP_PHP.md`
> names which findings these are and what a review round owes.

- ⚠⚠ **A IS REPRODUCIBLE AND THE WHOLE-PROGRAM COLUMN IS NOT — SO *"QUOTE BOTH,
  LABELLED"* HAS A REPRODUCIBILITY REASON BESIDE ITS RESOLUTION REASON.** Over
  **four** regenerations of one row's sidecar, **every A1 figure was
  bit-identical** while the whole-program column moved by a constant
  **±14–28 Ir** — the per-call stack-alignment bistability
  `check.py::check_marginal_ir` names, almost certainly the argv/env block, i.e.
  **the path length of whatever invoked the gate.** ▶ **Do not quote a
  whole-program figure to more than 2 dp**, and note that a row publishing **only**
  the whole-program column publishes the unstable one. ⚠ **UNEXPLAINED — the
  cause was not isolated.** (Item 99, `TASK_PHP_044` §8.2.)

- ⭐⭐⭐ **`inside_share` IS PER-**CELL**, NOT PER-**ROW**, AND ONE ROW CAN NEED
  DIFFERENT COLUMNS FOR DIFFERENT COMPARISONS.** `ph52` measures **22.24 %** on its
  **C** rungs — `PH52_NOINLINE` puts three callees in their own symbols, 62.35 % of
  the program — and **≈98.6 %** on its **Rust** rungs, which inline everything
  (`unsafe` A1 `48,846,257` against W1 `49,549,469`). ▶ **So the row publishes its
  **R1-vs-R1h** column in **W1**, correctly, while a **respelling search of its Rust
  rungs** lands in the 98.6 % region where **A1** is the resolving statistic.**
  ⚠⚠ **The rule above is right as written — *to the extent the difference lands
  inside the kernel symbol* — but `ph45` (9.5 %), `ph53` (89.5 %) and `ph52` were all
  first discussed as ONE number per row, and that is the reading to drop.**
  ▶ **Compute `inside_share` for the CELLS the comparison actually spans, then
  choose.** ⓘ And note *why* `ph52`'s C figure is low: the same three-TU boundary
  that makes the defect reproducible at all — **`inside_share` is not independent of
  the extraction's fidelity choices**, so it is a measurement and never a constant.
  (`TASK_PHP_045` §4 + §6.2, manager-verified from `results-php/ph52-…json`.)
