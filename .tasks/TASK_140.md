# TASK_140 — review `p29`, the 27th pattern and the second temporal row

**Role: research reviewer.** Adversarial by design. **You do not fix; you
report.** A review that agrees without having tried to break something is a
failed review.

`p29` is **built and green** (`TASK_139`) and **unreviewed**, which is the only
thing standing between the tree and *"27 patterns, all built, all reviewed"*.

Read first: `.tasks/TASK_139_REPORT.md` in full; `patterns/p29-bst-delete/`
(`spec.md`, `NOTES.md`, `model.py`, the seven rungs, `controls/`);
`RECAP.md` finding **52** and the corrected **47/49/51**;
`.tasks/TASK_137_REPORT.md` (the review that shaped this design);
`.memory/02-bench-rules.md` last section; `patterns/p27-handle-table/`.

✅ **Already manager-verified — do not re-derive:** verdict/`failures`/`blocked`
read out of `results/gate/p29-bst-delete.json` (`PASS`, `[]`, `[]`), verus
`25/0`, and the **ten-mutant battery re-run, 10 of 10 as expected**.

## What to attack, in order of what a wrong answer costs

1. ⚠⚠⚠ **THE HEADLINE IS LIMB 1 AND IT IS A COUNTING CLAIM:** *"`p27`'s
   read-path safety line needs ONE conjunct (liveness); `p29`'s needs TWO
   (liveness AND occupant identity)."* **Try to spell `p29`'s check with ONE.**
   If a single conjunct — a generation tag, a slot-versioned handle, a different
   record layout — is exact, **the row's headline collapses to `p27`'s** and it
   is a duplicate. ⚠ **The engineer searched ONE C shape and ONE Verus encoding
   and says so; a record with links in slot arrays was rejected as making the
   two-child splice a choice rather than a consequence. Test that reasoning.**

2. ⚠⚠ **THE ENGINEER NAMED THIS AS THE CALL A REVIEWER SHOULD ATTACK: the safe
   rungs are CORRECT here by design**, with the wrong-by-one-conjunct arm shipped
   as a **control** rather than as the safe rung. **Is that the right call?**
   It is one conjunct in two files plus a re-gate. ⚠ **Weigh it against
   `TASK_137`'s finding that the third safe spelling is bit-identical to buggy C
   on both halves — which is verbatim `p32`/`p33`'s REFUSED result. Getting this
   wrong in either direction changes what the row IS.**

3. ⚠⚠ **THE INSTRUMENT CLAIM, WHICH IS BIGGER THAN THE ROW:** *"the gate's Miri
   stage runs the CORRECT rung, so it can never substantiate a 'Miri sees / does
   not see' row for ANY pattern."* ✅ **If true this is a limitation of the whole
   harness and belongs in `.memory/03-measurement.md`.** **Verify it against
   `check.py` and against another pattern's record**, and check whether any
   SHIPPED pattern already leans on Miri in a way this undermines.

4. ⚠ **VACUITY BEYOND `M6`.** The battery has a constant-body arm and it fails —
   good, and it is the hole `TASK_137` found in the previous design. **Now try
   the ones the battery does not have**: an unreachable body, a `requires`
   nothing can discharge, a postcondition true of the wrong program.
   ⚠ **`p42`'s ghost ledger verified `18/0` while leaking.**

5. ⚠ **`identity: differ`, the tree's first.** `-O0` differs, `-O3` is `norel`.
   **Is `differ` legitimate here or is it a defect being pinned?**
   ⚠ **`.memory/02-bench-rules.md` allows it and said one real run was owed — but
   *allowed* is not *correct for this row*.** Check `p27`'s `-O0` fix really does
   not transfer (the engineer says `870 / 886 / 900`).

6. ⚠ **`model.py`'s independence** — it is meant to be a reachability walk with
   no cursor, `par`, `goleft`, guard or liveness array. **Verify that structurally,
   not by reading the docstring.** ⚠ **This is `p23`'s hazard and the previous
   attempt failed it by transliteration.**

7. ⚠ **NO COST AXIS IS PUBLISHED and neither rung's spellings were searched.**
   **Is that the honest call, or is a cost claim available and being avoided?**
   ⚠ **The absence must not read as a zero** — and if a difference IS publishable,
   the count-the-levers rule applies to both sides.

## Deliverables

1. **Per item: `SURVIVES` / `FALLS` / `SURVIVES, NARROWED`**, with the run.
   ⚠ **A `FALLS` on item 1 retires the row's novelty and is the most valuable
   outcome available.**
2. **A verdict on whether `p29` is FINISHED** — gate-green is not finished; a
   pattern is finished when a reader can find its result.
3. ⚠ **Anything in RECAP 52 or the `p29` catalogue cell the manager overstated.**
   The manager wrote both from the engineer's report plus its own re-runs, and
   **re-running a script checks the ARITHMETIC, not the READING**
   (`.memory/03-measurement.md` entry 12).
4. **The five `.memory/` updates the report says are owed (§6)** — say which you
   endorse. ⚠ **Item 1, *"a `struct` inside `verus!` is its own obligation,
   exactly as a `const` is"*, is a claim about the OBLIGATIONS COLUMN this
   project publishes for every pattern. If true it changes how that column is
   read tree-wide. Verify it.**

## Rules

- `.temp/t140/` only. **You may not edit `.memory/`, `RECAP.md`,
  `results/SYNTHESIS.md`, or `patterns/p29-bst-delete/`** — report, do not fix.
  No `git add`/`git commit`.
- ✅ **You MAY run `harness/check.py` and `harness/measure.py`** — you are the
  only agent running. ⚠ **Gate a single pattern, not the tree** (a full sweep is
  ~57 min). ⚠ **A gate record is not byte-reproducible** — `diagnostic` strings,
  `miri.runs[].seconds`, adversarial group order and the `N distinct behaviours`
  note move on their own.
- ⚠ **Read `blocked` out of the RECORD, never `grep` the log.** Expect
  `p01 = 1`, `p42 = 1`, `p29 = 0`.
- Verus via `./verus_run.py`, single-file mode, never `--cargo`. ⚠ Grep
  `~/tools/verus/vstd/std_specs/` specifically before any "no spec exists".
- Hand-run sanitisers need `env -u LD_PRELOAD`; **never truncate a sanitiser log
  with `head`**; every harm probe owes a **positive control that must fire**.
- ⚠ **If you plant into `patterns/p29-bst-delete/`, restore it in a `finally:`
  and verify by bytes** — the tree is committed at `d41ba6c`; check against it.
- Report to `.tasks/TASK_140_REPORT.md`. **PROTOCOL rule 2: you carry 679.**
