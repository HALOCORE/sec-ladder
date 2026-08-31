# TASK_158 — review `p25`, and the TREE-WIDE `Ir` finding it turned up

**Role: research reviewer.** Adversarial by design. **You do not fix; you
report.** A review that agrees without having tried to break something is a
failed review.

Read first: `.tasks/TASK_157_REPORT.md` **in full**;
`patterns/p25-realloc-growth/`; `.tasks/TASK_157.md` (what was asked);
`.temp/mgr155/NOTES.md` (**the manager's pre-build verification — §5 and §6 are
already REFUTED by the build; check whether anything else in it is wrong**);
`RECAP.md` findings **53–59**; `CLAUDE.md` **rule 6**;
`.memory/03-measurement.md` entries **19–22**;
`harness/check.py::check_marginal_ir`'s docstring **in full** (item 1).

## ⚠⚠⚠ THE ONE THING YOU MAY NOT DO

**You may not recommend refusing, shrinking or retiring this row for any
RUST-SIDE, VERUS-SIDE or LADDER-SIDE reason.** *"Verus cannot license `*cur`"*,
*"safe Rust's index port has no bug"*, *"the conjunct buys nothing but safety"* —
**every one is a FINDING, and the last is this row's HEADLINE.**
✅ **A row may fall on ONE ground only: its C MECHANISM duplicates a BUILT row's.**

## 1. ⚠⚠⚠ START HERE — IT IS BIGGER THAN `p25` AND IT IS NOT THIS ROW'S DEFECT

The engineer reports that the gate's **`marginal_ir_per_call` is WHOLE-PROGRAM**,
so read as a per-rung cost it publishes an **R4→R5 proof tax that does not
exist**: `+269.52` Ir/call on `large`, while the two kernels cost *exactly* the
same. ✅ **Manager-confirmed from the committed records** —
`unsafe/O3/isolated/large.bin` `5379.39` vs `verus/…` `5648.91` = `+269.52`,
identical at `-O0`, **while `kernel_exclusive_ir` is BIT-IDENTICAL for both
rungs at every measured cell.**

⚠⚠ **AND THE MANAGER THEN EXTENDED IT TREE-WIDE, AND THAT DERIVATION IS
UNREVIEWED — ATTACK IT.** Max `|verus − unsafe|` marginal per pattern:

```
p28 1732.73 · p11 494.00 · p29 465.55 · p25 269.52 · p35 36.47 · p14 34.00
p42 33.00 · p17 30.00 · p18 25.00 · p13 22.00 · then 16.00 and below
```

Spot-checked `kernel_exclusive_ir` for those four: **`p11` and `p25` are
kernel-identical at EVERY cell** (so the whole gap is outside the kernel);
**`p28` and `p29` are identical at `-O3` and DIFFER at `-O0`** (p28 by ~55 M,
p29 by ~24 M), so part of those two is real R5 exec code and part is not.

**What to settle, in this order:**

- ⚠ **Is the manager's derivation sound?** It maxes over cells and mixes
  `isolated` with `whole`; in `whole/O3` the kernel is inlined and
  `kernel_exclusive_ir` is `None`, so the diagnostic is unavailable there.
  **Say what the number means per mode, and whether `whole` belongs in it.**
- ⚠⚠ **Is this NEW, or is it the settled answer restated?** `RECAP.md` already
  records: *"the R4/R5 pair is not a null control — the verus kernel sits at a
  fixed offset from the unsafe one, and that offset is a source-path-length
  artefact… the pair is a biased draw of size one. The floor is the layout
  population."* **If it is the same fact, say so plainly and the finding shrinks
  to a magnitude update.** ⚠ **If it is not — if the mechanism is libc paths
  rather than source-path length — that is a different claim and the two must
  not be merged.** ✅ **`check_marginal_ir`'s own docstring names the p02/p08
  mechanism (glibc `memmove` alignment) and leads with `±0.20`, then warns there
  are patterns at `±7`. p28 is at 1732.73.**
- ⚠⚠⚠ **DOES ANY PUBLISHED NUMBER FALL BELOW ITS OWN PATTERN'S R4/R5 GAP?**
  That is the question that decides whether this is a methodology note or a
  correction. **Check it and report the list, or report that none does.**
- ⚠ **Does the sign-inversion half hold?** The engineer reports R2-vs-R3 at
  `-O0` is ±0.6 % kernel-only but **1.75× dearer** whole-program, because the
  iterator is not inlined there. **Re-derive it.**

⚠ **A `check.py` change is a 32-pattern re-gate and is NOT yours to make.**
**Report the finding and the recommended wording; do not fix it.**

## 2. ⚠⚠ THE C-MECHANISM DISTINCTION — the only ground that can kill the row

*No `free` anywhere; `realloc` retires the old block as a side effect of GROWTH;
the stale reference is an INTERIOR pointer into a container.* ⚠ **`p34` is the
sharpest attack** — it is also "a read of a retired block". The row's answer:
`p34` explicitly `free`s when a refcount hits zero and its repair site is the
ACQUIRE; `p25` never calls `free` and its repair site is the READ.
**Is that distinction in the C code, or in the vocabulary?** ⚠ Also try `p08`
(aliasing), `p27` and `p32`. ✅ `controls/no_reloc.py` is the census behind the
claim that `realloc` appears in 1 of 32 C rungs — **re-derive it**.

## 3. ⚠⚠ THE ROW'S THESIS — *"the conjunct buys memory safety and buys nothing else"*

All seven rungs agree on all eight inputs because `realloc` **copies**, so the
re-derived `toks[curi]` names the same element. ⚠ **That makes the harm
INVISIBLE TO EVERY CHECKSUM, and the row therefore rests entirely on the
DETECTOR.** **Attack that**: is the ASan cell load-bearing after all, given the
engineer's own warning that **ASan is a biased instrument here** (its allocator
moves on every `realloc`)? **What is the unbiased evidence, and is it enough?**
⚠ **And check the `no_stale` / `rederive` controls are not tautologies of the
model's representation** (`.memory/03-measurement.md` entry **19**).

## 4. ⚠⚠ THE COST RESULT, WHICH RUNS THE WRONG WAY AND IS THEREFORE SUSPECT

The **standard-clean** repair (unconditional re-derive) is reported **~2×
CHEAPER** than the idiomatic conjunct at every cell — `+65.67` vs `+164.39`
Ir/call at `large -O3`, `+2/+3` vs `+10/+11` static. **So on the C side this row
has NO trade-off**, which is the opposite of the project's thesis and therefore
needs the hardest look. ⚠⚠ **The flattering-direction trap has now fired SEVEN
times; this is the shape it takes when the flattering direction is *"safety is
free"*.** ⚠ **The engineer searched NO spelling on either repair** and says so.
**Search both sides and name the weaker endpoint.**

## 5. ⚠ THE DR 400 READING — the engineer flags it first and so should you

*"The conjunct `curbase == toks` compares a pointer to a freed object, which
DR 400 makes indeterminate"* is **a standards argument, not a measurement**, and
the engineer says **no tool here can confirm or refute it** (ASan always moves,
so R1h's true branch is only taken when no `realloc` happened). ⚠ **Attack the
ARGUMENT, and check the row does not rest a published claim on it.** ✅ **The
cost half stands independently — confirm that separation is real.**

## 6. ⚠ `model.py`, THE DETERMINISM PIN, AND R1's NON-DETERMINISM

`model.py` cannot represent a dangling pointer. **Is `sanitizer_expect` DERIVED
or DECLARED, and does the row say plainly which?** ⚠ **If derived, make it
fire; if declared, check it says so.** ⚠⚠ **And R1 is NOT deterministic on the
adversarial input** — `min + 31·b` for the stale byte, so `R1 == R1h` about 1 in
256. **Confirm nothing gates on a divergence**, and that the disclosure is
present and correct.

## 7. ⚠ THE R5, AND THE FOURTH `E0502` INSTANCE

`10 verified / 0 errors`, twin `12/0`, 4 TCB items, Miri 8 rows `ub=False`.
Claimed: **the temporal obligation has NO ANALOGUE** — no `PointsTo` for a `Vec`
buffer, and address equality ≠ provenance equality. ⚠ **Verify the mutants
really fail for the reasons given** (ATTACK `precondition not satisfied`, `X1`
`invariant not satisfied`, VACUITY `postcondition not satisfied`, SPEC-WEAKEN
`assertion failed`). ⚠ Try `assume(false)` — must FAIL unless declared.
✅ **`arm_safe_negctl.rs` — 12 lines, no container — prints the same `E0502`,
the FOURTH instance of a rustc code read as distinguishing when it is not.
Confirm it runs and that no claim in the row still rests on the error text.**

## 8. ⚠ Positive controls, detectors, and the gate hygiene the build tripped on

`ctl_asan.c` and `ctl_ubsan.c` both ship. **Confirm each EXECUTES and licenses
the detector column it is quoted for**, and that clang has not eliminated
either. ⚠ **Check the Miri invocation is well-formed** — `TASK_148` shipped one
missing `--` that scored a NON-RUN as *"no UB"*. ⚠ The build hit three
first-run gate failures (`idiom.why` byte-identity, `SLB-TRUSTED-ARGUMENT`
sections, stale `controls/*.json` under stage 9b's separate deadline);
**confirm all three are genuinely closed in the shipped tree.**

## Deliverables

1. **Per item: `SURVIVES` / `FALLS` / `SURVIVES, NARROWED`**, with the run.
2. **Is `p25` FINISHED?** ⚠ Gate-green is not finished. **Check
   `results/synthesis.md` carries it** (it will need regenerating — say so, do
   not do it) **and that the published table matches a fresh render.**
   ⚠ **Use the ANCHORED completeness check** (`PROTOCOL` rule 1) — the
   mention-anywhere form gave a false pass on `p34` one task ago.
3. ⚠⚠ **ANYTHING THE MANAGER OVERSTATED.** Fresh places to look: the
   **`9b06f96` commit message**, **`CAVEATS["p25"]`**, the **`TEMPORAL 6`** edit
   to `.memory/02-bench-rules.md`, and **item 1's tree-wide derivation above**.
   ⚠⚠ **Five of the last seven majors were the manager's, and `TASK_157`
   refuted four more including a census the manager had called "measured".
   Assume the same here.**
4. ✅ **CLEAN NEGATIVES ARE WORTH AS MUCH AS FINDINGS.** ⚠ **Two are already
   recorded by the engineer — the `p34`-distinctness argument and the
   one-growth-wide harm window — do NOT re-run those; check they were checked.**

## Rules

- `.temp/t158/` only. **You may not edit `.memory/`, `RECAP.md`,
  `results/SYNTHESIS.md`, `harness/`, or `patterns/p25-*/`.** No `git add`/`git
  commit`.
- ✅ **You MAY run `harness/check.py` and `harness/measure.py`** — a single
  pattern, never the tree. ⚠ A single pattern's gate can take **30+ minutes**;
  run it in the background and wait on the exact PID.
- ⚠ **If you plant into `patterns/p25-*/`, restore in a `finally:` and verify by
  BYTES against HEAD**, then re-derive the record's `source_sha256`.
- ⚠⚠ **Read `blocked`/`verdict` out of the RECORD, never `grep` the log**, and
  ⚠ **`rc=$?` after a PIPE reads the LAST command's status.**
- ⚠ **Do not touch any earlier `.temp/t*/` or `.temp/mgr*/`** — cited evidence.
- Verus via `./verus_run.py`, single-file mode, never `--cargo`.
- Hand-run sanitisers need `env -u LD_PRELOAD`; never truncate with `head`.
- Report to `.tasks/TASK_158_REPORT.md`.

**PROTOCOL rule 2 running count: launched from 898** — the manager's
reconciliation of `TASK_157_REPORT.md` §12 (892 + four manager claims refuted +
two engineer self-refutations). Carry it forward in your closing paragraph.
⚠ **Reconciliation across branches is the manager's job, not yours.**
