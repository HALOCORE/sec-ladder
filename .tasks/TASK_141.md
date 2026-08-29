# TASK_141 — the three repairs that need a sweep, done together, then the final sweep

**Role: research engineer.** ⚠⚠ **You are the only agent running.** You own
`harness/check.py`, `harness/measure.py` and the records.

⚠ **These three are bundled because each one costs a re-run, and doing them
separately costs three.** `.memory/00-environment.md`: a full 27-pattern sweep is
~57 min. **Budget for it and do not run it twice.**

Read first: `RECAP.md` findings **46** and **52** and the START HERE box;
`.tasks/TASK_140_REPORT.md` (§8 item 8, §9, §11 especially);
`.memory/03-measurement.md` entries **15, 16, 17**; `.tasks/PROTOCOL.md`.

## Repair 1 — `p29`'s false headline, in ten committed files

⚠⚠⚠ **`p29` ships a sentence that is FALSE and `TASK_140` measured it so:**

> ~~**`p27`'s read-path safety line needs ONE conjunct (LIVENESS); `p29`'s needs
> TWO (LIVENESS *and* OCCUPANT IDENTITY).**~~

✅ **ONE CONJUNCT IS ENOUGH** — two single-conjunct arms built from the shipped
`c/kernel.c` by substitution score **0 wrong / 0 ASan lines** with the positive
control firing, and one of them **adds no state** (it widens `live[]` from a bit
to the occupant tag, which `p27`'s own kernel calls a degenerated generation
counter). ✅ **Manager-re-run.** ⚠ **`NOTES.md` §6c's *"the `&&` ordering is
FORCED at R5"* falls with it.**

✅✅ **WHAT REPLACES IT — the row is NOT a duplicate and must not read as
retracted:** *one source line carries **TWO BUG CLASSES SELECTED BY THE
INPUT** — a use-after-**free** on leaf victims and an in-bounds
use-after-**recycle** on two-child ones, because the in-order-successor splice
overwrites its victim in place and frees the successor.* ⚠ **And the half every
detector sees is the half that CANNOT BE GATED** (R1's checksum is 19-of-20
distinct on the UAF half and reproducible on the recycle half).

**Sites** (`TASK_140` §1 lists them): `spec.md` prose **and its hashed `why`**,
`c/kernel.h`, `c/kernel_hardened.c`, `README.md`, `NOTES.md` §6c.
⚠⚠ **`c/*` IS MEASUREMENT-HASHED** (`measure.py::measurement_sources`), **so this
costs a RE-MEASURE of `p29`, not just a re-gate.** ⚠ **A comment-only edit to a
measurement-hashed file stales the record — that is expected here, not a defect.**

⚠ **Also fix the hashed `obligations_note`'s attribution:** it calls a struct
carrying `#[derive(Clone, Copy)]` *"bare"*. ✅ **The measured rule is that a bare
`struct` carries ZERO and `#[derive(Clone)]` carries the obligation** (`p36`'s
bare `OpTag` counts zero and sums exactly). **The NUMBER 25 is right; only the
stated cause is wrong.**

## Repair 2 — stage `9c`'s one-run lag. ⚠ THIS ONE BIT TWICE IN ONE SESSION.

**Stage 9c compares `results/tables/pNN.md` against a render built from the
PREVIOUS run's record**, so **a run that changes `controls_json`, `loud` or
`idiom_audit` passes itself and poisons the next.** ⚠⚠ **`p29` shipped
`check.py: FAIL [tables]` while its own record said `PASS`, and the manager
published *"green"* off that record.** ⚠ **It also cost `p16` a run two tasks
earlier.**

**Make stage 9c compare the table against the record THIS RUN WRITES**, or fail
loudly when it cannot. ⚠⚠ **`check.py` IS in the gate digest, so this is a
27-pattern re-gate — which is why it is bundled here.**

⚠⚠⚠ **AND IT OWES A MUST-FIRE ARM, because a forward-only fix is one somebody
later "confirms" by finding nothing.** ✅ **You have a real reproduction to build
it from: `p29` at commit `d41ba6c` had a record saying all four sidecars `FRESH`
and a table saying all four `STALE`. Reconstruct that state synthetically and
show the new stage 9c FAILS on it and the old one PASSES.**

## Repair 3 — the unpinned sidecars

`RECAP` records **21 unpinned sidecars** as owed. ⚠ **Re-derive the count; do not
trust it** — `p29` shipped four with JSON pins, so the figure has moved.
**Pin what is unpinned, using the mechanism the pinned ones already use
(`derived_from_sha256`).** ⚠ **`controls/*.py` is NOT measurement-hashed
(`patterns/*/controls/*` is outside the non-recursive glob), so this is gate
re-runs, not a re-measure — verify that rather than assuming it.**

## Then — the final sweep

**Run the full gate over all 27 patterns and record the result.** Expected:
`25 PASS + 2 PASS-WITH-BLOCKED-ROWS`, `p01 = 1`, `p42 = 1`, every other pattern
`0`. ⚠ **Read `blocked` out of each RECORD, never `grep` the log** —
`grep -c BLOCKED` matches `PASS-WITH-BLOCKED-ROWS` and decodes as `2N+1`.
⚠ **`p42`'s blocked count may legitimately be 2: the Miri slowdown is selected by
the ENVIRONMENT. Do not read that as a regression.**

**Finish with:** `harness/measure.py --check-stale` (expect 0 STALE),
`harness/tools/composition.py --check`, `harness/tools/temp_citations.py`, and
`python3 synthesis/synthesize.py` so the generated `results/synthesis.md` matches
the final tree. ⚠⚠ **`results/SYNTHESIS.md` (CAPITALS) is HAND-WRITTEN — NEVER
regenerate over it.**

## Rules

- `.temp/t141/` for scratch. **You may not edit `.memory/`, `RECAP.md`, or
  `results/SYNTHESIS.md`** — the manager applies those. No `git add`/`git commit`.
- ⚠ **Do not touch `.temp/t136/`, `t137/`, `t139/`, `t140/`** — all are cited
  evidence.
- ⚠ **Nothing under `harness/tools/` may be imported by
  `check.py`/`measure.py`/`build.py`** or it silently joins the gate digest.
- Verus via `./verus_run.py`, single-file mode, never `--cargo`.
- Hand-run sanitisers need `env -u LD_PRELOAD`; never truncate a sanitiser log
  with `head`; every harm probe owes a positive control that must fire.
- No blind process killing; prefer `timeout <N> <cmd>`.
- ⚠ **If a repair turns out to cost more than this file says, STOP AND REPORT
  rather than half-landing it.** A tree with one pattern re-measured and 26 not
  is worse than a tree with none.
- Report to `.tasks/TASK_141_REPORT.md`. **PROTOCOL rule 2: you carry 687.**
