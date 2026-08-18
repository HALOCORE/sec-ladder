# TASK_015 — the R3 audit: are we pricing safety, or pricing our own spelling?

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then `.tasks/TASK_014_REVIEW_REPORT.md`
**blocker B1** (the measurement this whole task exists because of),
`.memory/01-ladder.md` — finding 6 and the **corollary rule** under "R3 is the
honest comparison" — and `.memory/06-catalogue.md`'s first open cross-cutting
issue.

This is **not** a new pattern. It is the correction owed across the existing
result set before more results are added to it.

## Why

Three times now this project has written one plausible "tuned safe Rust"
spelling, measured it, and published its cost as **what safe Rust costs**:

- **p02** — a lost `memcpy` idiom. Retracted.
- **p16** — "only the naive indexed spelling is O(n)". Caught at review.
- **p05** — caught at TASK_014_REVIEW, and this one is the worst, because the
  better spelling beats the **unsafe** rung: `data.chunks_exact(ncol)` is
  `nrow − 7` instructions per call cheaper than R4, exactly, on every input in
  both residue classes, with identical stdout and exit against R4 on all **150**
  committed p05 inputs. Zero `unsafe`, no proof, no lemma.

A safety-cost claim is a claim about the **language**, so it is only as good as
the best spelling anyone can find. p16's and p17's R3 numbers are load-bearing
in two published findings and **have never had a second spelling written**.

## Part 1 — the audit, and do this first

For **p16, p17 and p05**, write a *second* idiomatic safe-Rust spelling of the
tuned rung and measure it against the shipped one and against R4. Measure only;
land nothing in Part 1.

The spellings that keep winning are the ones that hand the optimiser a length it
does not have to re-derive — `chunks_exact`, `split_at`, `iter().zip()`,
`windows`, consuming a slice rather than indexing one. p05's shipped R3 reslices
*by hand*, which is exactly the thing `chunks_exact` does better.

Deliver, per pattern: marginal `Ir` per call at `-O3 isolated` on the shipped
inputs, the shipped-R3-minus-new figure, whether output is identical to R4 on
**every** committed input, and — where there is a difference — **the mechanism
from the listing**, not a guess. B1's write-up is the model: no `cmov` against
five, split computed once per call rather than once per row, R4's unchecked
epilogue.

**Report Part 1 before starting Part 2**, in your notes if not to me: it decides
how big the problem is, and it is the part I most need even if the session ends
early. **If p16's or p17's R3 is also beaten, say so plainly and do not land it
here** — that is its own task, because each landing costs a re-measure.

Timebox: if a pattern resists after a genuine attempt, record the attempt and
move on. A clean negative — *"I tried `split_at` and `iter().zip()` on p16 and
both are within 2 Ir of the shipped R3"* — is a real result and stops the next
agent re-running it.

## Part 2 — land `chunks_exact` as p05's R3

The variant is in `.temp/review014/p05lin/safe_tuned_chunks.rs` and is **not**
gate-ready. Make it so:

1. Replace `patterns/p05-index-flatten/safe_tuned.rs`'s inner loop with it.
   The kernel signature, the driver region and every `spec.md` pin should be
   untouched — **confirm that rather than assuming it**, and if a pin does move,
   stop and report which.
2. **Keep the hand-resliced version as a committed control.** The *contrast* is
   the finding, and the mechanism analysis is meaningless without both. Use p08's
   arrangement — a generator under `patterns/p05-index-flatten/controls/` writing
   into `.temp/` — unless you find controls may live in-tree, in which case say
   so.
3. Re-measure p05 and re-run `harness/check.py p05` to a complete green record.
4. **Correct p05's `NOTES.md` and `README.md`.** They currently headline "R3 is
   *not* free here" and "the `29 + 3r` Ir per row is the price of the optimiser
   failing the lemma the proof proves". Both are retracted; `.memory/01-ladder.md`
   finding 6 now carries the replacement text — follow it rather than inventing
   new wording. What **survives** and must not be thrown out with it: the
   `1.375000` steady state, the `29 + 3r` model *as a model of R2 and of the
   shipped spelling*, the AVX2 result, the `f(0) = 84` mechanism, and the
   nonlinearity claim **as a statement about the obligation** (TASK_014_REVIEW
   Part 3 confirmed it with a linearisation counterfactual).
   Also: `NOTES.md:13` references a **§12 that does not exist** — the file ends
   at §11.

## Part 3 — p08's prose corrections, and a gate re-run

All three are review findings, and none can be fixed without re-running the gate
because **`NOTES.md` and `README.md` are inside `results/gate/*.json`'s
`source_sha256`** — which is why I did not fix them myself.

1. **`README.md:31` is wrong.** The "full arc" table says the bug is *"not even
   expressible in the spec logic"* at R5. Measured: substituting
   `core::ptr::copy` → `copy_nonoverlapping` in the trusted body gives
   **`11 verified, 0 errors`** shipped and **`15 verified, 0 errors`** under
   `--cfg slb_twin` — invisible to Verus, the twin, the contract pin and stages
   5c/5c-req; only Miri and the O3 identity pin catch it. `NOTES.md:965` already
   says the correct thing, so the README contradicts its own NOTES. The right
   claim is that the **caller's** obligation is discharged and the trusted body
   is trusted.
2. **`NOTES.md:955-958` claims the three `ensures` conjuncts "partition the
   buffer, no index left unconstrained".** False for a general `&mut [u8]`: a
   real-slice caller cannot prove `v@.len()` survives the call (`assertion
   failed`, 1 verified 1 errors), where the array signature gives it free
   (`3 verified, 0 errors`). Consequently **`NOTES.md:706-710` is backwards** —
   widening `&mut [u8; SCR]` → `&mut [u8]` to get past stage 5a is a
   *workaround*, not "a fix", and the more general contract is here the
   **weaker** one. (Stage 5a's rejection is a genuine false positive; it is
   recorded in `.memory/04-verus.md` and is **not** yours to fix.)
3. **`NOTES.md` §4a's "+2.9% ns" is 2.2× over-precise** — the review measures
   +1.29% against a 0.37% noise floor. The direction holds; the number does not.
   Four dangling cross-references also need repointing: `verus.rs:39,49,76` say
   "NOTES.md 4" and mean §6a/§8; `model.py:257` says "NOTES.md 7" and means §9.
   **Editing `verus.rs`/`model.py` moves hashes too** — fold them into the same
   re-run, and if touching `verus.rs` perturbs an obligation count, stop and
   report rather than adjusting a pin to match.

Then `harness/check.py p08` to a complete green record, and paste the verdict.

## Done when

Part 1's audit reported for all three patterns with mechanisms; p05 landed,
re-measured and green; p08's three corrections landed and green; and both gate
records refreshed and consistent with the tree. **State explicitly** whether any
`spec.md` pin moved in either pattern and why.

## Constraints

No root; no `/tmp` (scratch `.temp/p05r3/`); **no `git add`/`git commit`**; do
not edit `pilot/` or `.memory/` (report durable facts; I land them); do not touch
`harness/` or `common/` — if this task seems to need a change there, **stop and
report it**. Do not edit p01/p02/p16/p17 sources — **Part 1 is measure-only for
p16 and p17**, and its variants live under `.temp/`. Verus only via
`./verus_run.py`. clang `~/tools/llvm/bin/clang`, valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none on PATH.
`timeout <N> <cmd>`. Check `git status` before finishing and move anything you
created under `results/gate/` for a *mirror* run into `.temp/p05r3/`.

Notes to `.temp/p05r3/NOTES.md` as you go.

**If a prescription here is wrong, say so with the measurement.** Fifteen agents
have contradicted my written instructions and all fifteen were right; the last
one refuted three of my premises in a single Part 0, and the one before it
refuted my headline. The thing I am least sure of here is **whether replacing
p05's R3 is even the right response** — the alternative is to keep the shipped
spelling as R3 and publish `chunks_exact` as a documented fourth safe cell,
which would preserve every existing p05 number instead of invalidating them.
I chose replacement because R3 is *defined* as the best idiomatic safe spelling,
so a beaten R3 is simply not R3. **If the re-measure turns out to cost more than
that argument is worth, say so and stop at Part 1 plus the prose fixes.**
