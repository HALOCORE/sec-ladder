# TASK_151 — the three owed GATE repairs, done together, then the full sweep

**Role: research engineer.** ⚠⚠ **You are the only agent running.** You own
`harness/check.py`, `harness/report.py`, `harness/measure.py` and the records.

⚠⚠⚠ **THESE THREE ARE BUNDLED BECAUSE EACH ONE COSTS A FULL RE-GATE AND DOING
THEM SEPARATELY COSTS THREE.** `check.py` and `report.py` are both inside the
gate digest (`source_sha` globs `harness/*.py`, non-recursively). ✅ **NONE of
them is in `measure.py::measurement_sources`, so this costs NO RE-MEASURE** —
verify that before you start rather than taking it from this file.
**Budget one full sweep and do not run it twice.** (`TASK_141` is the precedent.)

⚠ **Run this BEFORE `TASK_148` (build `p35`).** Two of the three repairs are
**detection** gaps: a new pattern could ship a vacuous proof or a broken
hardened arm and the gate would not say so. Three rows remain to build, and they
should be built under the repaired gate. **The re-gate costs the same whenever
it is paid.**

Read first: `RECAP.md` finding **46 (iii)**; `.tasks/TASK_145_REPORT.md` §3
(arm `X4`); `.tasks/TASK_149_REPORT.md` §6's opening and its `B1`;
`.memory/05-layout.md`'s digest section; `.memory/03-measurement.md` entries
**11, 15**; `PROTOCOL.md`.

## Repair 1 — the self-reference detector is a DENY-LIST, not a census

`RECAP` finding **46 (iii)**, recommended and never built.

**`report.py`'s `--selfref` rests on a HAND-WRITTEN 9-key tuple, and 25 of the
record's 34 keys are unclassified.** ⚠⚠ **A `report.py` that rendered
`table_render` — stage 9c's OWN VERDICT — measures `26/26 READ` while
`--selfref` prints `0` and exits `PASS`.** **This project's most-named failure,
inside the detector built to prevent it.**

✅ **Recommended repair, from the finding: INVERT IT TO AN ALLOW-LIST** over the
already-measured read set `{contract_sha256, controls_json, idiom_audit, loud}`.

⚠⚠ **AND IT OWES A MUST-FIRE ARM.** A forward-only fix is one somebody later
"confirms" by finding nothing (`TASK_141` repair 2, and `TASK_147`'s
`detector_selftest()` is the good recent example — **four cells, two per guard,
run by the gate on every invocation**). ✅ **You have a real reproduction to
build it from: a `report.py` that reads `table_render`.** Show the new detector
FAILS on it and the old one PASSES.

✅ **CLEAN NEGATIVES from finding 46 — do not re-run these:** `RENDER-ERROR` IS
a failing verdict (all six 9c branches driven, four force `FAIL`); the
`--selfref` must-fire arm DOES fire and independently reproduces the `19 of 26`;
grepped `verdict` and FAIL-count agree with the record `130/130`; three fresh
draws of `p03` move exactly the four keys the docstring names.

## Repair 2 — `assume(false)` VERIFIES and the gate only SHOUTS

`TASK_145` §3 arm `X4` on `p32` (`15/0`) and `TASK_149`'s `B1` on `p28`
(`23/0`). **`check.py` prints `[tcb-axiom]` as a SHOUT, and a shout is not a
failure.** So a rung can ship a **vacuous proof** and pass.

✅ **EXPOSURE TODAY IS ZERO, MEASURED: `grep -c '\bassume('` over all shipped
`patterns/*/verus.rs` is `0` for all 29.** ⚠ **So this is a PROSPECTIVE repair
and there is no shipped row to break — which is exactly why it needs a
must-fire arm rather than a green sweep as its evidence.**

⚠⚠ **DECIDE AND JUSTIFY, do not reflexively promote the shout to a failure.**
The honest options:

- **FAIL on `assume(` in a shipped `verus.rs`** — simple, and it forecloses a
  legitimate use nobody has needed yet.
- **FAIL unless the contract DECLARES it**, the way `miri.blocked_reason` and
  the trusted-item machinery already work — a pattern that wants an `assume`
  must say so inside `contract_sha256`, which makes it a **visible one-line
  diff in review** rather than a silent shout.
- **Leave it a shout and record why**, with the exposure figure.

✅ **The second is the manager's guess and the manager may be wrong — measure the
cost of each and say which you took.**

## Repair 3 — the gate NEVER runs a detector on the HARDENED arm, for ANY pattern

`TASK_149` §6: **`check_sanitizers` builds `c/kernel.c` / gcc / `-O1` ONLY.**
`c/kernel_hardened.c` is never put under ASan or UBSan by the gate, in any
pattern.

⚠⚠ **THIS IS THE CELL THAT ALREADY COST A WRONG MANAGER INSTRUCTION.** The
manager's `p28d` variant SEGVed **in the hardened arm on a benign input** and
its verification never looked (`TASK_146` §1) — **admission question 1 is a
question about exactly that arm.**

✅ **`p28`'s own missed cell is CLEAN** — `TASK_149` measured 0 defects over 88
cells with positive controls licensing each column — **so this is a gate gap,
not a live defect.** ⚠ **But you do not know that about the other 28 rows, and
this repair is how anyone would find out.**

⚠⚠ **COST IS THE RISK HERE, AND IT IS THE ONE MOST LIKELY TO BLOW THE BUDGET:**
adding a second sanitizer build per pattern roughly **doubles stage 7**.
**Measure that on ONE pattern first and report the projected sweep cost BEFORE
committing to it.** ✅ **If it is too dear, the fallback is legitimate and
should be taken rather than half-landing the repair: run the hardened arm on
NON-adversarial inputs only** — which is where admission question 1 lives and
where the `p28d` defect was — **and record the narrowing.**

⚠ **What the expectation must be: the hardened arm is `sanitizer_expect: clean`
on EVERY input, adversarial included, in every pattern.** That is what R1h
*means*. **A row that fires there is a real finding — report it, do not fix the
pattern in this task.**

## ⚠ NOT in this task, recorded so it is not silently absorbed

- **Masking the ASan pid and the Miri `seconds` to make gate records exact.**
  `TASK_149` measured the record as **materially reproducible already** — 5 of
  1296 leaves, four ASan `diagnostic` pids and one Miri float — and noted that
  `check.py:7267`'s own blast-radius probe already masks the pid. ⚠ **Tempting
  and in the same file, but it is a FOURTH repair with its own must-fire arm, it
  changes recorded evidence rather than a check, and the standing note it would
  correct lives in `.memory/`, which is the manager's.** **Leave it. Say if you
  disagree.**
- **`p32`'s `detector_selftest()` fails by CRASHING rather than reporting**
  (`.temp/mgr151/`). `model.py` is measurement-hashed, so it is a re-measure,
  not a re-gate. **Different bundle.**

## Then — the full sweep

**Run the gate over all 29 patterns and record the result.** Expected:
`27 PASS + 2 PASS-WITH-BLOCKED-ROWS`, `p01 = 1`, `p42 = 1`, every other pattern
`0`. ⚠ **Read `blocked` out of each RECORD, never `grep` the log** —
`grep -c BLOCKED` matches `PASS-WITH-BLOCKED-ROWS` and decodes as `2N+1`.
⚠ **`p42`'s blocked count may legitimately be 2** (environment-selected Miri
slowdown); that is not a regression. ⚠ **`check.py p28` alone took 33 minutes
for `TASK_149` — budget the sweep accordingly and do not read a long run as a
hang.**

**Finish with:** `harness/measure.py --check-stale` (expect **0 STALE** — and if
anything IS stale, STOP: nothing here should touch `measurement_sources`),
`harness/tools/composition.py --check`, `harness/tools/temp_citations.py`, and
`python3 synthesis/synthesize.py`. ⚠⚠ **`results/SYNTHESIS.md` (CAPITALS) is
HAND-WRITTEN — NEVER regenerate over it.**

## Rules

- `.temp/t151/` for scratch. **You may not edit `.memory/`, `RECAP.md`, or
  `results/SYNTHESIS.md`.** No `git add`/`git commit`.
- ⚠ **Do not touch any earlier `.temp/t*/` or `.temp/mgr*/`** — all cited
  evidence.
- ⚠ **Nothing under `harness/tools/` may be imported by
  `check.py`/`measure.py`/`build.py`** or it silently joins the gate digest.
- Verus via `./verus_run.py`, single-file mode, never `--cargo`.
- Hand-run sanitisers need `env -u LD_PRELOAD`; never truncate a sanitiser log
  with `head`; every harm probe owes a positive control that must fire, **in the
  detector whose column it licenses**.
- No blind process killing; prefer `timeout <N> <cmd>` with a generous timeout.
- ⚠⚠ **If a repair turns out to cost more than this file says, STOP AND REPORT
  rather than half-landing it.** A tree with one repair landed and two not is
  worse than a tree with none — **and each of these three is independently
  landable, so say which you took and which you left.**
- Report to `.tasks/TASK_151_REPORT.md`. **PROTOCOL rule 2: the count is in
  `TASK_150_REPORT.md`'s closing paragraph — read it there, do not guess.**
