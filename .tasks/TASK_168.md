# TASK_168 — the backlog bundle: one sweep, one batched re-measure, and a static question answered before anything is spent on it

**Role: research engineer.** You are the only agent running.

⚠⚠⚠ **THIS IS THE LAST STRUCTURED WORK IN THE PROGRAMME.** All 33 patterns are
built, reviewed, corrected and have findings; both scheduled research items are
done (`TASK_164`–`167`). **What remains is a backlog the manager has triaged in
`.temp/mgr164/QUEUE_TRIAGE.md`** — read it first, and ⚠ **note it already
carries two corrections to itself, one of them found by `TASK_167` and one by
the manager, so treat it as evidence and not as authority.**

Read first: **`.temp/mgr164/QUEUE_TRIAGE.md` in full**; `RECAP.md` **Immediate
queue** items **12, 15, 16, 28, 31, 33**; `PROTOCOL.md` **rule 6** (the digest
cost table and the measured re-measure figures); `.memory/05-layout.md`'s
*"a `check.py` edit … IS NOT THE WHOLE COST"* section; `.memory/02-bench-rules.md`
on the citation convention.

---

## ⚠⚠⚠ THE BUDGET, DERIVED, AND IT IS BIGGER THAN THE TRIAGE FILE FIRST SAID

**ONE 33-pattern sweep + ONE batched re-measure of FOUR patterns + TWO `p35`
control-generator re-runs.**

```
harness/*.py            -> gate digest        -> 33-pattern sweep
patterns/*/model.py     -> MEASUREMENT digest -> re-measure that pattern
patterns/*/inputs/gen.py-> MEASUREMENT digest -> re-measure that pattern
patterns/*/controls/*.py-> gate digest only
3 of 46 controls/*.json pin files under harness/ -> p23 (untouched here),
   p35's proof_mutants.json and union_oracle.json MUST be regenerated
```

⚠⚠ **The manager's own triage put item 12 in the "one sweep" group and that was
WRONG** — five of its six sites are `model.py`/`inputs/gen.py`, both
measurement-hashed. ✅ **`PROTOCOL` rule 6 measured the re-measure and it is
cheap and moves nothing published**: `p19` took **1 m 17 s**; `p46` moved
**111 of 1371 leaves** — 102 wall-clock, 6 source hashes, a timestamp, git
metadata — **zero `Ir`, zero md5, zero identity, zero checksum**. **Rule 6's own
advice is to BATCH doc fixes rather than avoid them, which is what this task
is.**

⚠ **ORDER MATTERS AND IT IS NOT NEGOTIABLE: make EVERY measurement-hashed edit
BEFORE the measure run** (`measure.py` hashes above the loop, so a mid-run edit
wastes the run), **then re-measure, then sweep, then regenerate `p35`'s two
sidecars, then sweep `p35` again if 9b complains.**
⚠ **Freeze every `check.py`/`vparse.py` edit before the sweep starts.**
`TASK_164` lost a 22-pattern sweep to a late docstring fix and disclosed it;
**do not repeat it.**
⚠ **If any item costs more than this file says, STOP AND REPORT.**

---

## A. ⚠⚠ ITEM 28 FIRST — IT IS A STATIC QUESTION AND IT MAY COST NOTHING

**Answer this before you edit anything, because the answer may add work to the
re-measure batch or may close the item for free.**

`.memory/03-measurement.md` records that glibc's byte-wise `rep` paths cost
**≈1 `Ir` per byte** against the vector path's **0.104** — a **10×** inflation —
and that the crossover is **exactly 8192 bytes** (`TASK_090`, with a
`GLIBC_TUNABLES` control). The blast radius was checked at `TASK_074`, when
`p02`'s 61 B and 4092 B copies were the evidence.

⚠⚠ **The queue item names TEN patterns built since; SEVEN MORE have landed, so
the re-check set is SEVENTEEN** — `p13 p14 p18 p10 p27 p47 p38 p22 p36 p19`
plus `p29 p32 p28 p35 p34 p25 p49`. ⚠ **Do all 33 rather than seventeen; it is
the same command and the set has been miscounted twice.**

⚠⚠⚠ **THE DISTINCTION THAT THE ITEM'S OWN WORRY BLURRED, AND IT IS THE WHOLE
QUESTION: what matters is the size of an INDIVIDUAL
`memcpy`/`memmove`/`memset` CALL inside the measured window — NOT the size of
the input file.** The shipped 16 KB and 12 MB blobs are **not themselves
copied**.

✅ **Answer it statically and from the committed tree**: for each pattern, what
is the largest single `mem*` length any measured cell can pass? `model.py` knows
the shapes; `c/kernel.c` and the rung sources have the call sites;
`synthesis/outward_ir.json` **names the callee and counts the calls per kernel
call**, which is new since the item was written and may settle it directly.
⚠ **If NOTHING exceeds 8192, the item CLOSES for free and no number moves —
say so and move on.** ⚠ **If something does, report it and STOP; do not
re-measure to chase it in this task.**

## B. ITEM 12 — the citation rot, and it has grown

```
check.py:1249-1278  p12/inputs/gen.py:30 · p13/model.py:50 · p13/inputs/gen.py:30
check.py:625        p16/model.py:19 · p16/model.py:181
check.py:8841       p35/controls/rust_bug.py:163
check.py:469        p13/model.py:52
check.py:459-460    p38/inputs/gen.py:28
```

**Eight citations, five patterns, and ALL FIVE distinct targets were dead at
`HEAD` before `TASK_164` moved anything** (`:1249` a blank line; `:625` a
`Report` method; `:8841` a `MIRI_BIN` argument list; `:469` `#`; `:459` a
comment about row counts). ⚠ **`check.py` grew again, so they are now rotten in
a NEW way — do not "verify" one by reading the current line.**

✅ **The convention is `.memory/02-bench-rules.md`'s: name the FUNCTION and give
NO LINE NUMBER AT ALL, because a function name cannot decay.** **Rewrite each to
name the function (and, where the citation is about a specific rule, quote the
sentence it is pointing at rather than a coordinate).**

⚠⚠ **AND THE SHARP PART, WHICH IS WHY THIS IS NOT JUST HYGIENE: `p35`'s
citation was written at `TASK_148`, AFTER the convention was recorded, and was
already rotten ~16 tasks later. A documented convention did not stop it.**
✅ **So propose the check**: a `check.py` stage that fails on `check\.py:\d+`
anywhere under `patterns/`. ⚠ **It is gate-only and free on this sweep.**
**Build it, with a must-fire arm, and say what it would have cost historically.**

⚠ **`.memory/` has SIX of its own and at least two are rotten now**
(`03-measurement.md:3146` → `check.py:2387`; `:3375` → `check.py:2805`).
**`.memory/` is the manager's — REPORT them, do not edit.**
⚠ **The manager's own triage said *"`.memory/` is genuinely clean"* and that was
false; `TASK_167` caught it.**

## C. ITEM 31 — a 250-line docstring nobody reaches

`check_marginal_ir`'s docstring is **250 lines, 1.5× the next longest in the
file (164)**, with the **second mechanism at 60%** of it and the **operative
rule at 87%**. ⚠⚠ **A warning nobody reaches is not a warning**, and it now
documents two unrelated effects whose magnitudes differ by 38×.

✅ **Hoist a four-line header** naming both mechanisms and pointing at the two
tables. ⚠ **Do NOT rewrite the body** — every number in it was re-derived at
`TASK_164` and confirmed at `TASK_165`.

## D. ITEM 33 — `vparse`'s unclassified-`global` fallback is line-anchored

An unknown `global` form written on the **same line** as something else is
invisible, and **the `_selftest` cell that guards it uses the own-line
spelling**, so the arm cannot see the gap. **Prospective — no shipped source
spells one.**

✅ **Fix it and add the arm in the shape the gap has**, i.e. a cell whose
fixture puts the unknown `global` where the current matcher misses it.
⚠ **Confirm the new arm FAILS against the OLD matcher** — otherwise you have
added a cell that could never fire, which is `.memory/03-measurement.md` entry
19 one level down and is the exact defect this item is about.

## E. ITEM 16(b) — `CODEGEN_CFGS` is a whitelist coupled to nothing

A new `--cfg` in `build.py` **silently leaves the idiom audit**. ⚠ **The queue
item says this is the expensive class because `build.py` is measurement-hashed;
that is wrong about its own cost** — **a cross-check that READS `build.py` and
fails on a mismatch lives in `check.py`, which is gate-only.**

✅ **Build it with a must-fire arm.** ⚠ **Do not edit `build.py`.**

## F. ITEM 15 — a judgement the manager owns, so give it the measurement

`p01` (1 entry) and `p05` (2 entries) ship `forbidden` entries with **zero
backticked spellings**, so their *"forbidden: 0 hits"* audits an **empty set**.
Both currently **shout**. It was left a shout deliberately because backticking
is a **declaration** edit and owes the direction test.

⚠ **Do NOT change the severity and do NOT backtick anything.** ✅ **Report:**
what would each of the three entries have to say to be auditable; whether
`forbidden_hits`' hard fail changes the argument; and **what backticking them
would cost** (it moves `contract_sha256`, so price the report/sweep chain).
**The manager decides.**

## Then, in this order

1. **Item A answered** — before any edit.
2. **Every measurement-hashed edit** (item B's five pattern files), frozen.
3. ⚠ **State your re-measure prediction BEFORE running it** — which leaves move
   and why. `TASK_154` predicted 110 exactly; `TASK_156` predicted 103.
   **These are comment-only edits to `model.py`/`inputs/gen.py`; say whether you
   expect ANY `Ir`, static count, checksum or md5 to move, and why.**
4. **Re-measure `p12 p13 p16 p38`**, then compare against the prediction.
5. **Every `check.py`/`vparse.py` edit** (items B's new stage, C, D, E), frozen.
6. **The 33-pattern sweep**, once, in the background, waiting on the exact PID.
7. **Regenerate `p35`'s `proof_mutants.json` and `union_oracle.json`** — both
   pin `harness/` files — then re-gate `p35`.
8. `harness/measure.py --check-stale` (⚠ **66 examined = gate PLUS measurement;
   33 records of each**) · `harness/tools/composition.py --check` ·
   `harness/tools/temp_citations.py` ·
   `python3 synthesis/licence.py --emit synthesis/licence.json` ·
   `python3 synthesis/synthesize.py`.
9. ⚠⚠ **CHECK EACH SCRIPT'S OWN EXIT STATUS, NOT A PIPELINE'S OR AN `echo`'s.**

## ⚠ NOT in this task

- **`.memory/`, `RECAP.md`, `results/SYNTHESIS.md`, `harness/tools/composition.py`**
  — manager-owned. **Report; do not edit.** ⚠ **NEVER regenerate over
  `results/SYNTHESIS.md` (CAPITALS); `results/synthesis.md` (lower case) is the
  generated one and you may regenerate it.**
- **`build.py`** — measurement-hashed, and item E does not need it.
- **Queue items 35 and 36** (auditing the 14 `undeclared` rows; promoting
  `TASK_129`/`TASK_131`'s instruments out of `.temp/`). **Neither needs a sweep
  or a re-measure, so they are the NEXT task and must not be started here.**
- **Queue groups C, D and E** — the spelling-search debt, the curiosities and
  the declined items. **Their RETIREMENT as stated limitations is the manager's
  and is also the next task.**

## Rules

- `.temp/t168/` for scratch. ⚠ **Do not modify any earlier `.temp/t*/` or
  `.temp/mgr*/`** — cited evidence; you may read them. **No `git add`/`git commit`.**
- ⚠⚠ **DO NOT LEAVE A `pgrep -f` WAITER RUNNING** — a waiter's own command line
  contains the string it greps for, so its exit condition can never be true, and
  the enclosing tool `bash -c` matches too. **Use `wait <pid>` or a `.done`
  sentinel.**
- ⚠⚠ **Read `blocked`/`verdict` out of the RECORD, never `grep` the log.**
  ⚠ **Expected: `30 PASS + 3 PASS-WITH-BLOCKED-ROWS`, 0 failures, `blocked`
  `p01` 1 / `p35` 3 / `p42` 1** — ⚠ `p42`'s may legitimately be 2 (the Miri
  slowdown is selected by the environment, not the gate).
- Verus via `./verus_run.py`, single-file mode, never `--cargo`.
- Hand-run sanitisers need `env -u LD_PRELOAD`; never truncate with `head`.
- **Keep the generator, delete the artefact.** A generator that edits source by
  string substitution **MUST ASSERT ITS SUBSTITUTION COUNT**.
- Report to `.tasks/TASK_168_REPORT.md`. **Write the file before citing it.**

**PROTOCOL rule 2 running count: launched from 942**
(`.tasks/TASK_167_REPORT.md`). ⚠ **Reconciliation is the manager's job.**

⚠⚠ **The manager has now been refuted in ELEVEN of the last eleven tasks, and
`TASK_167` killed five claims in one pass including one marked
`✅ manager-re-derived`. The call to attack here is item A's framing: I have
asserted that *"what matters is the size of an individual `mem*` call, not the
input file"* and that the question is answerable STATICALLY. Both are the
manager's, and if a static answer is not sound, say so before spending anything
on it.**
