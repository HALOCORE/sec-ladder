# TASK_163 — land `p49`'s corrections, and FINISH the row

**Role: research engineer.** ⚠⚠ **You are the only agent running.** You own
`harness/check.py`, `harness/measure.py` and the records.

⚠⚠⚠ **BUDGET, AND IT IS BIGGER THAN THE LAST TWO BECAUSE E2 TOUCHES THE HASHED
`why`: ONE re-measure and TWO gate runs.** `c/kernel.c` and
`c/kernel_hardened.c` are in `measure.py::measurement_sources` → **E1b costs a
re-measure**. A `why` edit moves `contract_sha256`, the published table cites
it, and `report.py` cannot precede a gate → **E2 costs TWO gate runs**
(`TASK_156` measured exactly this). ⚠ **Make every measurement-hashed edit
BEFORE the measure run** — `measure.py` hashes above the loop, so a mid-run edit
wastes the whole run.

Read first: `.tasks/TASK_162_REPORT.md` **in full**; `.tasks/TASK_161_REPORT.md`;
`patterns/p49-interned-pool/`; `RECAP.md` finding **62**;
`.memory/03-measurement.md` entries **19–23**; `PROTOCOL.md` **rule 6**.

## ⚠⚠⚠ E1 — a REFUTED mechanism is restated in three shipped files

The manager's pre-build claim — *"the guard `if (r_shared[i])` could never be
false"* — **was refuted by measurement** (TRUE 67 195 / FALSE 30 263, 31.1 % of
97 458 evaluations; the COW body itself clears the flag). **The real defect was
that no record is ever born owned.** Three files still carry the wrong reason:

- **(a) `README.md:73-78`** restates it verbatim. **Gate-hashed only → a gate
  re-run.** ⚠ **This is the one file the rule-6 second-half pass missed.**
- **(b) `c/kernel.c:202` and `c/kernel_hardened.c:205`** carry the *item-7*
  causal claim (below). ⚠⚠ **Both are MEASUREMENT-HASHED.**
- ✅ **`spec.md`'s hashed `why` is CLEAN on this** — reviewer-verified. Do not
  disturb it for E1.

✅ **Write the corrected reason, not just a deletion:** the guard is real and
fires; what was wrong is *why* it matters. ⚠ **Sweep the whole pattern for the
refuted sentence rather than fixing the three the reviewer named** — `TASK_156`
found three more on `p34` after its review, so *"the reviewer already swept"* is
not evidence.

## ⚠⚠⚠ E2 — *"the two `Rc` arms differ in ONE TYPE"* IS FALSE, and it is in the HASHED `why`

Strip arm C's 20-line `Rc::strong_count(..) > 1` + budget-refusal + flag-clear
block and **it matches NEITHER C rung on all 5 discriminating inputs.** So the
headline *"safe Rust expresses both sides one type apart"* is **not** what was
measured. It appears in **`spec.md`'s hashed `why`**, `controls/safe_arms.py:28`
and `:234`, `NOTES.md:73`, and `TASK_161_REPORT.md` §3d.
⚠ **The arm file itself discloses the extra block — header rot** (`PROTOCOL`
rule 13: in a long doc item only the body gets maintained).

✅ **Say what IS true and measure it**: the two arms differ by a type *and* a
20-line block, and **the honest claim is whatever that block turns out to be
doing.** ⚠⚠ **Do not simply weaken the sentence — establish what the block is
for and whether an arm without it can be made to match by any other means.**
⚠ A `why` edit moves `contract_sha256`: **record the pre-edit block TEXT
verbatim, not only its hash** (`TASK_156`'s standard), and use
`python3 harness/tools/contract_diff.py p49` for the disclosure.

## ⚠⚠ E3 — a published hedge is SUPERSEDED, and this is the good half

`NOTES.md` §4c says *"the decomposition does NOT close"*. ✅ **It closes
exactly**: line-level callgrind gives `+8.43 −4.62 −4.62 −1.00 −1.00 = −2.81` on
gcc/`-O3`/`small`, the guard costs a **constant `2.00` `Ir` per evaluation**
(gcc-O3 2.00, clang-O3 2.00, clang-O0 3.00, gcc-O0 6.00), and the offset is gcc
emitting one fewer instruction at each of two sites per intern-creation, exactly
**9 237 each**. ⚠⚠⚠ **SO THE SIGN IS SET BY THE EVENT MIX, NOT BY THE
COMPILER — gcc ALONE reverses between its own two inputs. The manager's task
file called it *"a reversal between COMPILERS, which is new"* and that framing is
withdrawn.** **Re-derive it and land the closed decomposition.**
⚠ **The clang-side line decomposition is UNTRUSTWORTHY** — 19 % of the kernel
lands in `<unidentified lines>`; the reviewer did not pursue it and neither
should you without saying so.

## ⚠⚠ E4 — a figure that inverts its own headline

`NOTES.md:433` prints `small.bin c-gcc 0.99`; **the record gives `1.00`**
(1974.41 / 1971.63). ⚠ **That inverts §4b's own `−2.79` headline.** Fix the
figure and check every ratio in that table against the record.

## ⚠ E5 — the row's structural headline has NO MUST-FIRE ARM INSIDE THE GATE

Of 8 planted `model.py` defects, **6 REPORT and 0 CRASH** — better than `p32`'s
arm, and worth keeping. **Two are silent**, and one of them matters:
**`W1-share-break-census`** — the row's own structural claim — has no must-fire
arm the gate runs. ⚠⚠ **`.memory/03-measurement.md` entry 19 one level up: a
CENSUS with no must-fire arm is the same defect as a check that cannot fire.**
✅ **Add one.** ⚠ Also: **`S3-sim-arena-cap`'s condition `abump + w > ARENA`
fires 0 times on every shipped window** — either give it an input that reaches
it or say plainly that it is unreachable and why.

## ⚠ E6 — minors, all from `TASK_162_REPORT.md`

1. **`9/9` is really 5 of 9 discriminating** — say which.
2. ⚠ **The manager wrote *"34 obligations, the LARGEST in the tree"* into finding
   62 and the catalogue on the strength of two comparisons (`p29` 25, `p32` 15),
   and the reviewer notes `p34`'s `verus.rs` is LONGER (1183 vs 1126).**
   **Derive the obligation count across ALL 33 patterns and report it** — line
   count and obligation count are different quantities and the claim was made on
   one while quoting the other.
3. **`controls/detectors.py:49-51`'s *"same flags"* is loose** — tighten or drop.

## ⚠⚠ E7 — `p49` IS NOT FINISHED

`results/synthesis.md` and `results/SYNTHESIS.md` have **zero** mentions, and the
**anchored** completeness check prints `p49`. **After the re-gate and
re-measure:** `python3 synthesis/licence.py --emit synthesis/licence.json` then
`python3 synthesis/synthesize.py`. ⚠⚠ **`--emit` TAKES A PATH.**
⚠⚠ **`results/SYNTHESIS.md` (CAPITALS) is HAND-WRITTEN — NEVER regenerate over
it; report that it lacks `p49` and `p25` and leave it to the manager.**

## ⚠ NOT in this task

- **The three-item `check.py` gate bundle** (stage 9b's unread sidecar verdict;
  `global layout` as a sixth body-less form; `check_marginal_ir`'s docstring).
  **A 33-pattern re-gate. Report only.**
- **`.memory/` and `RECAP.md`** — the manager owns them and has already landed
  the `CAVEATS["p49"]` corrections and finding 62.

## Then

`harness/check.py p49` → **PASS** (`blocked []`) · re-measure `p49` ·
`harness/report.py p49` if the gate fails on `[tables]` · second gate ·
then `harness/measure.py --check-stale` (⚠ **it prints GATE PLUS MEASUREMENT —
66 examined against 33 measurement records; a commit message has already misread
that**), `harness/tools/composition.py --check`,
`harness/tools/temp_citations.py`, `synthesis/licence.py --emit …`, then
`synthesis/synthesize.py`.
⚠⚠ **CHECK EACH SCRIPT'S OWN EXIT STATUS, NOT A PIPELINE'S OR AN `echo`'s** —
the manager committed on a FAILING `temp_citations.py` this session by chaining
`&&` from an `echo` rather than from the check, and separately misread `rc=$?`
after a pipe. **Three instances, one cure: read the status of the thing you ran.**

## Rules

- `.temp/t163/` for scratch. **You may not edit `.memory/`, `RECAP.md`,
  `results/SYNTHESIS.md`, `harness/check.py`, `harness/measure.py`, or
  `harness/tools/composition.py`.** No `git add`/`git commit`.
- ⚠ **Do not touch any earlier `.temp/t*/` or `.temp/mgr*/`** — cited evidence.
  **Copy from `t162/`; do not modify it.**
- ⚠⚠ **DO NOT LEAVE A `pgrep -f` WAITER RUNNING** — its own command line
  contains the string it greps for, so its exit condition can never be true.
  **Use `wait <pid>` or a `.done` sentinel** (`.memory/00-environment.md`).
- ⚠⚠ **Read `blocked`/`verdict` out of the RECORD, never `grep` the log.**
- Verus via `./verus_run.py`, single-file mode, never `--cargo`.
- Hand-run sanitisers need `env -u LD_PRELOAD`; never truncate with `head`.
  ⚠ **On this row every detector is expected SILENT, so the positive controls
  are the only thing separating *silent* from *not linked in*.**
- ⚠ **Generate control JSONs AFTER the sources are final**, and note **stage
  9b's sidecar deadline is SEPARATE from `measure.py`'s**.
- ⚠ **State your re-measure prediction BEFORE running it**, then compare.
  `TASK_154` predicted 110 moved leaves exactly; `TASK_156` predicted 103.
  **`c/kernel.c` and `c/kernel_hardened.c` change here — say first whether you
  expect any `Ir`, static count or md5 to move, and why.**
- **Keep the generator, delete the artefact.**
- ⚠ **If any item costs more than this file says, STOP AND REPORT.**
- Report to `.tasks/TASK_163_REPORT.md`.

**PROTOCOL rule 2 running count: launched from 920**
(`.tasks/TASK_162_REPORT.md`'s closing paragraph). Carry it forward.
⚠ **Reconciliation across branches is the manager's job.**
⚠⚠ **The manager has been refuted in every one of the last eight tasks. The
call to attack here is E6.2 — the *"largest obligation count in the tree"* claim
the manager published on two comparisons.**
