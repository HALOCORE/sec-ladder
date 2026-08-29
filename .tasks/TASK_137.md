# TASK_137 — review `TASK_136`: `p29`'s settled design, before anything is built on it

**Role: research reviewer.** Adversarial by design. **You do not fix; you
report.** A review that agrees without having tried to break something is a
failed review.

⚠⚠ **WHY THIS RUNS BEFORE THE BUILD.** `TASK_136` settled `p29`'s degree split,
its safety line and its four R5 arms — and the project intends to **build the
row on that design**. PROTOCOL rule 1 exists precisely so a build does not rest
on unreviewed engineer work. **If the design is wrong, this is the cheapest
moment in the whole programme to find out.**

Read first: `.tasks/TASK_136_REPORT.md` **in full**; then
`.tasks/TASK_133_REPORT.md` §3a–3c (what `TASK_136` corrects);
`RECAP.md` findings **47, 49 and 51**; `.memory/02-bench-rules.md` last section
(the fourth limb and **the temporal-R5 attack-arm rule**);
`.memory/06-catalogue.md`'s `p29` cell; `patterns/p27-handle-table/` (the only
other temporal row).

✅ **The manager already re-ran the entire pipeline in place**
(`sh .temp/t136/run.sh`, `EXIT=0`, log at `.temp/mgr136.log`) — **the degree
table, the convention census, all four R5 arms, the safe-rung reconciliation and
the reproducibility sweep all reproduce.** ⚠ **So do NOT spend the task
re-deriving the numbers. Reproduction is not the question; INTERPRETATION is.**

## The five things to attack, roughly in order of what a wrong answer costs

1. ⚠⚠⚠ **`H2` OVER `H3` — THE ENGINEER NAMED THIS AS THE CALL IT WOULD MOST
   LIKE ATTACKED, AND THE WHOLE BUILD RESTS ON IT.** `H2` (null the saved
   pointer at the **located victim**) is exact on 1511/1511; `H3` (`&& g_fresh`)
   is exact on the five hand inputs and **conservative** elsewhere.
   **Is `H2` really the safety line, or is it a fix that happens to fit the
   measured inputs?** ⚠ **Try to find an input where `H2` is wrong.** The
   engineer's own `H1` was exact on a smaller set and failed — **that is the
   precedent, and it is one task old.**

2. ⚠⚠ **THE FOUR-MECHANISM TABLE IS THE HEADLINE, SO ATTACK ITS ROWS
   SEPARATELY.** Each row is a different claim and they can fail independently:
   ASan silent on recycle; safe Rust correct 71/71 on leaf; **Verus verifying
   the recycle arm `6/0`**; R1 non-reproducible on leaf only.
   ⚠⚠⚠ **THE VERUS ROW IS THE ONE THAT SCOPES A LANDED FINDING (47), SO IT
   DESERVES THE HARDEST LOOK: is ARM_C really PROVING the recycled value, or is
   it VACUOUS?** **Check for a trivially-satisfiable postcondition, an
   unreachable body, a `requires` nothing can discharge.** ✅ **This project has
   a standing vacuity battery; use it.** **`p42`'s ghost ledger verified `18/0`
   while leaking, and that is the exact shape being claimed here.**

3. ⚠ **THE SAFE-RUNG RECONCILIATION.** `TASK_133` measured *"silently wrong
   where C aborts"*; `TASK_136` measured **correct 71/71** there, and
   reconciled the two by **slot recycling** (four builds of one source,
   `17 → 36` fuzz failures). ⚠⚠ **Does recycling actually explain `TASK_133`'s
   result, or does it merely produce a DIFFERENT failure set that was never
   matched against it?** **The manager landed this reconciliation in `RECAP`
   marked unreviewed; it is the weakest-supported thing in finding 51.**

4. ⚠ **THE CONVENTION CENSUS** — *"one conjunct"* is 4 of 25 — **corrected two
   committed documents on the strength of ONE mechanical classifier.** Read
   `.temp/t136/convention.py` and ask what it MISSES: a hardened cell that adds a
   conjunct **spelled across two lines**, or as an early `return`, would be
   classified `False`. ⚠ **If the true figure is 8 rather than 4 the correction
   still stands, but the sentence built on it may not.**

5. ⚠ **THE ENGINEER'S OWN DISCLOSED DEFECT, because its blast radius may be
   larger than reported:** their first delete-by-substitution re-searched by key
   **and `model.py` mirrored the same error, so the two agreed.** ✅ **Caught by
   one input designed to differ.** ⚠⚠ **Ask whether any OTHER number in the
   report shares that dependency** — a model written by the same author in the
   same session is not obviously independent of the implementation it checks,
   and this is `p23`'s hazard.

## Deliverables

1. **Per item: `SURVIVES` / `FALLS` / `SURVIVES, NARROWED`**, with the run that
   decides it. ⚠ **A `FALLS` on item 1 or 2 should STOP the build**, and saying
   so is the most valuable outcome available here.
2. **A verdict on whether `p29` should be BUILT**, given the remaining cost the
   engineer named: **all 26/26 contracts pin `ensures result == <fold>(...)`, so
   `p29`'s R5 owes a full functional refinement with THREE WALKS where `p27` has
   none.** ⚠ **The user's standing instruction is that temporal proofs will be
   harder and the project should not chicken out — so *"it is hard"* is not a
   reason. *"It is hard AND here is what breaks"* is.**
3. ⚠ **Anything in RECAP findings 47, 49 or 51 that the manager overstated.**
   The manager wrote all three and re-ran the arms, **but re-running an
   engineer's script checks the ARITHMETIC, not the READING** — and this
   project's newest failure class (`.memory/03-measurement.md` entry 12) is
   exactly *a retracted conclusion whose every number is correct*.

## Rules

- `.temp/t137/` only. **You may not edit `.memory/`, `RECAP.md`, or
  `results/SYNTHESIS.md`.** No `git add`/`git commit`. Read-only git is fine.
- ⚠⚠ **Do NOT run `harness/check.py` or `harness/measure.py`** — a concurrent
  agent is re-gating two patterns and those touch shared records. Compiling,
  running, `valgrind`, `miri` and `./verus_run.py` in `.temp/t137/` are fine.
- Verus via `./verus_run.py`, **single-file mode, never `--cargo`**.
- ⚠ Grep `~/tools/verus/vstd/std_specs/` **specifically** before any "no spec
  exists" claim.
- Hand-run sanitisers need `env -u LD_PRELOAD`; **never truncate a sanitiser log
  with `head`**; every harm probe owes a **positive control that must fire**.
- ⚠ **Do not edit `.temp/t136/`** — it is the evidence under review. Copy what
  you need into `.temp/t137/`. **And do not edit a shell script while `sh` is
  executing it**; the engineer corrupted a run that way and the manager hit the
  mirror image.
- Report to `.tasks/TASK_137_REPORT.md`. **PROTOCOL rule 2: you carry 664.**
  Close with your branch delta and the sum. ⚠ **A concurrent branch also carries
  664; reconciliation is the manager's.**
