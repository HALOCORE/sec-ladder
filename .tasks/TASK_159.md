# TASK_159 — land `p25`'s corrections, and REPAIR A PUBLISHED CLAIM

**Role: research engineer.** ⚠⚠ **You are the only agent running.** You own
`harness/`, `synthesis/` and the records.

⚠⚠⚠ **THE BIGGEST ITEM IS NOT `p25`'s.** E1 corrects a claim
`results/synthesis.md` publishes today, and the reviewer showed it is **already
false independently of `p25`**. ✅ **It is `synthesis/`-only, so it costs NO
re-gate and NO re-measure.**

⚠ **BUDGET: ONE re-gate, and NO re-measure.** Nothing below should need to
touch a measurement-hashed file (`c/*`, top-level `*.rs`, `model.py`,
`inputs/gen.py`). ⚠⚠ **IF AN ITEM DOES, STOP AND REPORT rather than half-landing
it** — a re-measure is a separate budget and the manager will decide.

Read first: `.tasks/TASK_158_REPORT.md` **in full, and §13 especially — it
carries TEN recommended wordings**; `.tasks/TASK_157_REPORT.md`;
`patterns/p25-realloc-growth/`; `RECAP.md` finding **60**;
`.memory/03-measurement.md` entry **23** (the reviewed write-up of E1).

## ⚠⚠⚠ E1 — the CONFIDENT band promotes corrections smaller than their own null

The gate's `marginal_ir_per_call` is a **whole-program** slope. `identity` forces
R4's and R5's kernels to agree, so **their difference is a measured null** — and
it is not zero:

```
R4/R5 null, -O3 ISOLATED (the published column)
  p28 1732.73 · p29 425.80 · p25 269.52 · p42 31.00 · everything else <= 6.00
```

**Three published numbers sit below their own pattern's null**:
`p25 large gcc-clang` `+19.42` — which the calibration places in the **`≥ 16.00`
band labelled *"every one is real"*** — against `+269.52`, **13.9× larger**;
`p42 large gcc-clang` `+5.00` against `−31.00`; `p02` `+2.00` against `−2.00`.

⚠⚠ **AND §5's FIRST CLAIM IS ALREADY FALSE WITHOUT `p25`**: it lists seven rows
including `p42 −31.00`, asserts *"every one is in the `2.00 … 16.00` band"* when
`p42` is `≥ 16` **and printed bold**, then resolves *"all six"*. **Three
internal disagreements in one claim.**

✅ **Land the reviewer's §13 repair: a `synthesis/`-only rule that REFUSES to
promote a correction to the CONFIDENT band when `|correction|` is below that
pattern's own `R5 − R4` null**, and correct the false claim. ⚠⚠ **The rule owes
a MUST-FIRE arm** — a planted row that should be refused and is. ⚠ **Derive each
pattern's null from `results/gate/*.json`, `-O3 isolated` ONLY**: `check_identity`
compares `isolated` digests (`check.py:3303`), so **`whole` is not a null and
must be excluded** — that mistake is what made the manager's first derivation
say *"ten patterns"* when it is **four**.

⚠ **Do NOT change `check.py` or `measure.py`.** A gate-digest edit is a
32-pattern re-gate and is a different bundle.

## ⚠⚠ E2 — `p25` IS NOT FINISHED

`results/synthesis.md` mentions `p25` **zero** times, and the **anchored**
completeness check (`PROTOCOL` rule 1 — headers, not mentions) prints it.

**After E1 and the re-gate:** `python3 synthesis/licence.py --emit
synthesis/licence.json` then `python3 synthesis/synthesize.py`.
⚠⚠ **The licence step is REQUIRED and its `--emit` TAKES A PATH — bare `--emit`
exits `rc=2` and writes nothing.** ⚠⚠ **`results/SYNTHESIS.md` (CAPITALS) is
HAND-WRITTEN — NEVER regenerate over it.** ⚠ It also does not mention `p25`;
**report that, do not fix it** (manager's file).

## ⚠⚠ E3 — the cost headline's magnitude and class claim (M5, M6)

The **direction** survives; two claims around it do not.

- **M5: *"about HALF … on BOTH compilers"* is unsupported — `controls/rederive.py`
  builds `gcc` ONLY**, and the measured clang ratio is **`5.0–5.5×`, not `2×`**.
  ✅ **Either add the clang arm to the control and publish both ratios, or drop
  the words *"on both compilers"*.** ⚠ **Adding the arm is the better answer and
  is a `controls/` change — a re-gate, not a re-measure.**
- **M6: a THIRD repair site (fix at the growth) beats the published
  standard-clean one by `3.3×` at `-O0` and LOSES at `-O3`.** **The ordering
  REVERSES between levels**, so *"the safer repair dominates"* is **false of the
  class** even though it is true of the published pair. ⚠ **Re-derive it, publish
  all three sites, and give every figure at BOTH levels** — `p35`'s lesson,
  now on a third axis. ✅ **Both published endpoints ARE respelling-robust
  (`TERN ≡ R1h`, `PTR ≡ RD`) — that clean negative stands; do not re-run it.**

## ⚠ E4 — `NOTES.md` §0's rule-6 disclosure is false as worded

It says *"no entry moved"*. ⚠ **The `identity`, `collapse` and `miri` entries'
PROSE moved at step 2**, even though no pin VALUE did. ✅ **Say exactly that —
"no pin value moved; three entries' prose did, and here is the diff"** — and use
`python3 harness/tools/contract_diff.py p25`, which says what moved key by key
from `git` alone. ⚠ **A disclosure is what a reviewer trusts INSTEAD of
re-checking, so a wrong one removes the check it was meant to enable.**

## ⚠ E5 — the rest of `TASK_158_REPORT.md` §13

**Read §13 and land what belongs to the pattern.** ⚠ **Three items there are the
MANAGER's and are already fixed — do not re-land them**: `CAVEATS["p25"]`'s
inverted census attribution, the *"one of SIX doubling growths"* figure, and the
`min + 31·b` over-generalisation. ⚠ **If §13 recommends anything requiring
`check.py`, REPORT IT; do not fix it.**

## ⚠ NOT in this task — recorded so it is not silently absorbed

- **`global layout` is a sixth body-less form `vparse.axiom_decls` cannot see**,
  live on four patterns. **A `check.py` change; report only.**
- **Stage 9b hashes a control sidecar and never reads its own verdict**, and its
  sidecar deadline is distinct from `measure.py`'s. **Same bundle; report only.**
- **The DR 400 reading** is a standards argument no tool here can settle. **Leave
  it disclosed as such.**

## Then

`harness/check.py p25` → **PASS** (expect `blocked []`) · `harness/report.py p25`
if the gate fails on `[tables]` · then `harness/measure.py --check-stale`
(⚠ **expect `64 record(s) examined, 0 STALE` — 64 is GATE PLUS MEASUREMENT, and
there are only 32 measurement records; a commit message has already misread
that**), `harness/tools/composition.py --check`,
`harness/tools/temp_citations.py`, **`synthesis/licence.py --emit
synthesis/licence.json`**, then **`synthesis/synthesize.py`**.
⚠ **`rc=$?` after a PIPE reads the LAST command's status, not the script's.**

## Rules

- `.temp/t159/` for scratch. **You may not edit `.memory/`, `RECAP.md`,
  `results/SYNTHESIS.md`, `harness/check.py`, `harness/measure.py`, or
  `harness/tools/composition.py`.** No `git add`/`git commit`.
- ⚠ **Do not touch any earlier `.temp/t*/` or `.temp/mgr*/`** — cited evidence.
  **Copy from `t158/`; do not modify it.**
- ⚠⚠ **DO NOT LEAVE A `pgrep -f` WAITER RUNNING.** `TASK_157` left five that
  would have polled forever, because **a waiter's own command line contains the
  string it greps for** — and the manager reproduced it and found the enclosing
  tool shell matches too. ✅ **Use `wait <pid>` on the exact PID, or a `.done`
  sentinel.** `.memory/00-environment.md` has the entry and the reproduction.
- ⚠⚠ **Read `blocked`/`verdict` out of the RECORD, never `grep` the log.**
- Verus via `./verus_run.py`, single-file mode, never `--cargo`.
- Hand-run sanitisers need `env -u LD_PRELOAD`; never truncate with `head`;
  **every harm probe owes a positive control that must fire, in the detector
  whose column it licenses.**
- ⚠ **Generate control JSONs AFTER the sources are final**, and note **stage 9b's
  sidecar deadline is separate from `measure.py`'s** — `TASK_157` lost a gate run
  to exactly that.
- **Keep the generator, delete the artefact.**
- ⚠ **If any item costs more than this file says — in particular if it needs a
  re-measure — STOP AND REPORT.**
- Report to `.tasks/TASK_159_REPORT.md`.

**PROTOCOL rule 2 running count: launched from 906**
(`.tasks/TASK_158_REPORT.md`'s closing paragraph). Carry it forward.
⚠ **Reconciliation across branches is the manager's job.**
⚠⚠ **The manager has now been refuted in every one of the last four tasks —
including twice inside the derivation E1 rests on. E1's null table is the thing
to attack here: check the mode split, check the four-pattern figure, and check
that the three affected numbers are the only three.**
