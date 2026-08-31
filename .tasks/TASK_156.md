# TASK_156 — land `p34`'s review corrections, and FINISH the row

**Role: research engineer.** ⚠⚠ **You are the only agent running.** You own
`harness/check.py`, `harness/measure.py` and the records.

⚠⚠⚠ **BUNDLED BECAUSE THE ITEMS SHARE ONE RE-RUN.** `c/kernel.h` and `model.py`
are in `measure.py::measurement_sources`, so **E1 costs a `p34` RE-MEASURE**;
`spec.md`, `NOTES.md` and `controls/*` cost a **re-gate** only.
**Budget ONE re-measure and ONE re-gate. Do not run either twice.** ⚠ **Make
every measurement-hashed edit BEFORE the measure run** — `measure.py` hashes
`measurement_sources` at line 450, **above** the loop, so a mid-run edit wastes
the whole run (`.memory/03-measurement.md` entry **20**; `TASK_150` paid two).
⚠ **`controls/arm_safe_arena.rs` is NOT measurement-hashed** (only `pdir/*.rs`
is, non-recursively) — verified against `results/p34-refcount-stack.json`. It is
a re-gate, not a re-measure.

Read first: `.tasks/TASK_155_REPORT.md` **in full** (971 lines);
`.tasks/TASK_154_REPORT.md`; `patterns/p34-refcount-stack/`; `RECAP.md` finding
**59**; `.memory/03-measurement.md` entries **19–22**; `PROTOCOL.md` **rule 6**.

## ⚠⚠⚠ E0 — `p34` IS NOT FINISHED, AND THAT IS THIS TASK'S POINT

`results/synthesis.md` says **`Patterns: 30. Gate records: 30.`** against 31 and
mentions `p34` **zero** times. **A pattern is finished when a reader can find its
result, not when its gate is green** — `p19` and `p46` were absent for 45 and 35
tasks under exactly this condition.

**Do, in this order, after the re-gate and re-measure below:**
`python3 synthesis/licence.py --emit synthesis/licence.json` then
`python3 synthesis/synthesize.py`. ⚠⚠ **The licence step is REQUIRED and its
`--emit` TAKES A PATH — bare `--emit` exits `rc=2` and writes nothing.**
⚠⚠ **`results/SYNTHESIS.md` (CAPITALS) is HAND-WRITTEN — NEVER regenerate over
it.** ⚠ It also does not mention `p34`; **report that, do not fix it** (it is
the manager's file).

## ⚠⚠ E1 — three doc comments in HASHED sources cite measurements that do not exist (M4)

1. **`c/kernel.h:112` and `model.py:143` cite `controls/storage_arms.py`. THAT
   FILE DOES NOT EXIST.** ⚠ Both files are **measurement-hashed**.
2. **`controls/arm_safe_arena.rs:34,92`** says `safe_arms.py` records the arena
   high-water mark. **It does not** — the reviewer measured it separately and got
   **16 of 32**.

✅ **Either make the citation true or delete it.** ⚠ **If you make it true,
the measurement must actually be recorded by the control, not by a comment.**
⚠⚠ **`grep` the whole pattern for citations of files that do not exist and for
measurements no control records — the reviewer named three; do not assume that
is all of them.** ⚠ **This is PROTOCOL rule 6's known hole: the hash proves the
declaration has not moved and says nothing about whether it is still TRUE.**

## ⚠⚠ E2 — the hashed `why` contains a FALSE sentence (B1)

`spec.md`'s `slb-contract` `why` asserts *"a borrow cannot be stored in the stack
array because the borrow checker ties it to the array it came from."*
⚠⚠ **The reviewer STORED ONE AND RAN IT.** It is false as written.

⚠⚠ **AND THE SURROUNDING CLAIM IS THIS PROJECT'S THIRD INSTANCE OF THE SAME
DEFECT: A COMPILE ERROR READ AS DISTINGUISHING WHEN IT IS NOT.** The reviewer
printed `E0507`/`E0502` from **12-line programs containing no `Rc` at all**, and
`arm_safe_rc_borrow.rs`'s `E0502` **fires on the NEW path and is identical with
the DUP body deleted** — so it is not evidence about `DUP`. (`p25`'s `E0502` and
`p28`'s `E0382`/`E0499` were the first two.)

**Decide and justify in `NOTES.md`:** rewrite the sentence to what is true, and
✅ **strengthen `controls/safe_arms.py` with a NEGATIVE CONTROL — a program that
CANNOT have the bug and must NOT print the same error.** ⚠ **Without that
control the `Rc`-cannot-express-it half of the headline is unsupported**, and
it is half of the row's biggest result. ⚠ **The arena half is NOT in question**
— it reproduces bit for bit on 8/8 and the reviewer confirmed it.
⚠ A `why` edit moves `contract_sha256`; **disclose it** (below).

## ⚠ E3 — `NOTES.md` §6c mis-states which `p35` arm verified (M5)

§6c says *"`X1` is `p35`'s arm … on `p35` it VERIFIED"*. **Wrong**: `p35`'s
invariant arms (`M3`, `M6`) both **FAILED**; the `p35` arm that verified deletes
a **trusted item's `requires`** — and **on that arm `p34` verifies too, `24/0`**.
✅ **Correct the comparison and say what it actually shows.** ⚠ Re-derive both
sides rather than quoting the reviewer.

## ⚠⚠ E4 — the manager's M1 and M2, so the pattern's own text agrees with the record

The manager has already corrected `composition.py` and `RECAP.md`. **The
pattern's own files must not still carry the withdrawn claims:**

- ⚠ **M1:** anywhere `patterns/p34-*/` says the acquire is the **only** repair
  site, correct it to the **only ZERO-COST** site and **publish the destroy-path
  figures**: matches R1h on 8/8, ASan-clean, `+160.64` Ir/call (`+7.28%`) at
  `-O3`, `+2403.83` (`+21.6%`) at `-O0`. ⚠ **Re-derive them; do not copy them.**
  ✅ **Pricing two repair sites is a better result than asserting one** — say so.
- ✅ **M2 needs NO change to `spec.md`/`README.md`** — the reviewer confirms they
  already carry the correct hedge (*"`0.00` is still MEASURED and not assumed"*).
  **The over-claim was the manager's caveat and it is fixed.** ⚠ **Check
  `NOTES.md` does not carry the absolutist spelling anywhere.**

## ⚠ E5 — the contract disclosure is NOT independently verifiable

The `1fa98c8a… → f1537d7f…` move (stage 5c forced a deletion) **cannot be
reconstructed — the reviewer tried six ways and all failed.** ⚠⚠ **PROTOCOL rule
6 records a HASH, and a hash proves WHEN a declaration was written while letting
nobody reconstruct WHAT IT SAID.**

✅ **For the move you make in this task: record the pre-edit `slb-contract` block
TEXT verbatim in `NOTES.md` (or a `controls/` sidecar), not only its sha256**,
and say plainly that the earlier `1fa98c8a…` move has no recoverable text.
⚠ Use `python3 harness/tools/contract_diff.py p34` for the new move — it says
what changed key by key, **from `git` alone**.

## ⚠ Minors and process notes

1. **Three tracked `controls/*.json` sidecars carry a `measured_utc`**, so
   re-running a control dirties the tree even when nothing else changed.
   ⚠ **Report whether that timestamp earns its place; do not remove it without
   saying what it is for.**
2. **`global layout` is a SIXTH body-less form `vparse.axiom_decls` cannot see.**
   rustc checks it at codegen even on a dead type, **but Verus reports
   `1 verified, 0 errors` on a lie**, so no verify-only stage is protected.
   ⚠⚠ **A `check.py` change is a 31-pattern re-gate. REPORT IT; DO NOT FIX IT.**
3. **Stage 9b hashes a control sidecar and never reads its own verdict.**
   ⚠ Same bundle as item 2, same instruction: **report, do not fix.**

## Then

`harness/check.py p34` → **PASS** (⚠ the reviewer never ran a FULL gate — it
re-derived the stages carrying the row's claims — **so this run is owed and is
the first full one since the build**) · re-measure `p34` · `harness/report.py p34`
if the gate fails on `[tables]` · then `harness/measure.py --check-stale`
(expect **0 STALE**, 62 records), `harness/tools/composition.py --check`,
`harness/tools/temp_citations.py`, **`python3 synthesis/licence.py --emit
synthesis/licence.json`** and then **`python3 synthesis/synthesize.py`**.
⚠ **`rc=$?` after a PIPE reads the LAST command's status, not the script's —
the manager misread a FAILING `composition.py --check` as `rc=0` this session
exactly that way.**

## Rules

- `.temp/t156/` for scratch. **You may not edit `.memory/`, `RECAP.md`, or
  `results/SYNTHESIS.md`.** No `git add`/`git commit`.
- ⚠ **Do not touch any earlier `.temp/t*/` or `.temp/mgr*/`** — cited evidence.
  **Copy from `t155/`; do not modify it.**
- Verus via `./verus_run.py`, single-file mode, never `--cargo`.
- ⚠⚠ **Read `blocked`/`verdict` out of the RECORD — never `grep` the log, not
  with a regex alternation, and not with a loop matching a prefix a log header
  shares with its verdict.** Expect `p34` = `PASS`, `blocked []`.
- Hand-run sanitisers need `env -u LD_PRELOAD`; never truncate with `head`;
  **every harm probe owes a positive control that must fire, in the detector
  whose column it licenses.**
- ⚠ **State your re-measure prediction BEFORE running it**, then compare.
  `TASK_150`'s and `TASK_147`'s were exact hits; `TASK_154`'s 110 moved leaves
  were predicted exactly. **`c/kernel.h` and `model.py` change here — say first
  whether you expect any `Ir`, static count or md5 to move, and why.**
- ⚠ **A re-gate is not value-free**: `marginal_ir_per_call` moved in 673 of 2772
  cells across 18 patterns on an unchanged tree (entry 21). Do not read small
  moves elsewhere as your doing.
- **Keep the generator, delete the artefact.**
- ⚠ **If any item costs more than this file says, STOP AND REPORT rather than
  half-landing it.**
- Report to `.tasks/TASK_156_REPORT.md`.

**PROTOCOL rule 2 running count: launched from 889**
(`.tasks/TASK_155_REPORT.md`'s closing paragraph). Carry it forward in your
closing paragraph. ⚠ **Reconciliation across branches is the manager's job.**
⚠⚠ **Five of the last seven majors were the manager's, and every one was found
by an agent running a measurement against a sentence. Do that here — the named
targets are E2's negative control and E4's destroy-path figures.**
