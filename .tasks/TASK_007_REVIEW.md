# TASK_007_REVIEW — p16's O(n) claim, and whether the fold really is the cause

**Role:** research reviewer
**Read first:** `.tasks/PROTOCOL.md` (reviewer checklist + severity), then
`.tasks/TASK_007.md` (the spec), `patterns/p16-tlv-walk/NOTES.md` (756 lines, the
delivery), `git show c623b22`, and `.memory/01-ladder.md` finding 4 — which is the
manager's write-up of this result and is **itself under review**.

## Why this one matters more than the last six reviews

This is the first review of a *pattern* in four tasks, and p16 carries the
project's **first positive safety-cost result**. Everything before it said
"safety is cheap"; p16 says safe-naive Rust costs +69% instructions on a
data-dependent walk. A wrong positive result is far more damaging to this project
than a wrong negative one, and **this project has already published and retracted
exactly one perf headline** (p02's O(n) bounds-check tax, refuted at
TASK_004_REVIEW) for skipping the decomposition step.

The engineer did decompose, and the decomposition is the strongest part of the
delivery. Your job is to try to break it anyway.

## Part 1 (blocker-hunting) — is the +4.25 Ir/byte real, and is the cause right?

The claim chain, each link separately attackable:

1. R2 is 10.00 Ir/folded byte, R3/R4 are 5.75, difference **exactly 4.25**, in
   two bands 18× apart over 68 consecutive lengths.
2. Changing **only the fold** removes 98.0% / 99.3%; changing **only the walk**
   removes 1.5% / 0.5%; the two sum to 2091 vs the whole gap's 2085.
3. From the disassembly, R2's fold is a rolled 10-instruction body and R4's is
   4×-unrolled at 23 insns / 4 bytes.
4. Therefore **2.00 of the 4.25 is the check and 2.25 is the foreclosed unroll.**

Link 4 is the headline and the least defended. Specifically:

- **Where does "2.00 is the check" come from?** Recount it from the
  disassembly yourself. In a rolled 10-instruction body containing a `cmp`+`je`,
  calling the check exactly 2 instructions is arithmetically obvious *and* it is
  suspiciously exactly the two instructions you can point at. Is the 2.25
  residual really "the unroll", or is it a bucket for everything unaccounted?
  A cleaner control exists: **force R4's fold to stay rolled** (e.g.
  `#[inline(never)]` on a per-byte step, or `-C llvm-args` / `#[optimize(size)]`,
  or an opaque per-iteration barrier) and measure a rolled-vs-rolled gap. If that
  gap is 2.00, link 4 is confirmed by construction. If it is not, the attribution
  is wrong and the finding needs restating. **This is the single most valuable
  thing you can do in this review.**
- **`shl $0x5` site counting** (3 vs 7) is offered as independent corroboration.
  Is it? Both counts are consequences of the same unroll factor, so it may be the
  same observation twice. Say which.
- **10.00 and 5.75 are suspiciously round.** Verify they are measured, not
  fitted — re-derive at least one from a raw callgrind run yourself.
- Check the **`Ir`-per-byte denominator**: is "folded bytes" counting header
  bytes, skipped records, the `nrec` fold? A denominator off by the 3-byte header
  per record would shift both numbers and could manufacture the clean 4.25.

## Part 2 — the wall-clock null, which is the most over-claimable thing here

**+70% `Ir` → 0% time** is a striking result and the write-up explains it as a
latency-bound Horner chain at ~3 cycles/byte. IPC was **not** measurable (no
hardware counters), so the explanation is an inference and is labelled as one.

- Is the null result *measured well enough to state*? `.memory/06-catalogue.md`
  records that 18 of 28 wall-clock cells on an earlier pattern exceeded the 10%
  spread threshold and were discarded. What is p16's spread, per cell? If the
  timing noise floor is wider than the effect being denied, "0% time" is
  unsupported and must be restated as "below our resolution".
- The cycle arithmetic: does ~3 cycles/byte × the fold length actually reconcile
  with the measured ms at this box's clock? Do that arithmetic. If it does not
  reconcile, the latency-bound story is wrong even if the null is real.
- Is there a *second* explanation the write-up does not consider — e.g. the
  benchmark being memory-bandwidth-bound on `large`, which would also hide a
  +70% `Ir` difference and has nothing to do with Horner latency? `small` is
  L1-resident, so the two inputs should discriminate. Check whether they do.

## Part 3 — standard pattern validity

Apply `PROTOCOL.md`'s reviewer checklist. Do not re-run what the gate already
certifies; go after what it cannot see. In particular:

- **Are the six rungs semantically equivalent?** R2's fold being rolled and R4's
  unrolled is fine; a rung that folds a *different set of bytes* is not. All
  variants printing the same checksum is good evidence — check it covers the
  adversarial inputs too, not just `small`/`large`.
- **Is R2 a fair naive port or pessimised into losing?** This is the crux of a
  +69% claim. Would a competent Rust programmer write p16's `safe_naive.rs`? If
  the answer is "no, they'd write R3", the finding is still true but the framing
  must lead with R3. Conversely — is **R3 tuned in a way that quietly restores
  unsafety** or changes the algorithm?
- **Is the C rung idiomatic C**, or C written to lose? gcc is 35% worse than
  clang here (4062 vs 2993); that is a large gap and worth a sanity check that
  it is a real codegen difference and not a build-flag artefact.
- The `7 + 7·nrec` fit for R3 "predicts both shipped numbers without being fitted
  to them". Verify that — a two-parameter fit over a sweep that then reproduces
  two in-sample points is not a prediction.

## Part 4 — the security half

- `adversarial-overrun` fires ASan and SIGSEGVs both C compilers. Confirm the
  **unbounded walk** claim specifically: the write-up says `end - p` underflows
  and the loop never terminates, which is a stronger and different claim than
  "reads past the end". Prove it or correct it.
- Confirm the delete-the-check controls are honest: safe Rust exits 101 with an
  index-out-of-bounds panic. Does the *panic* happen at the point the write-up
  says, and does the R5 "will not compile" claim reproduce with the actual error?

## Part 5 — clean negatives

Name the attacks that did **not** land. Rule 6 of `PROTOCOL.md`: worth as much as
a finding, and it stops the next agent re-running them.

## What I am NOT asking for

Not a gate-bypass hunt. The threat model is settled
(`.memory/02-bench-rules.md`, top). If you find a bypass incidentally, one line
in the residuals list. **Do not spend this review on `harness/`** — including
Part 0's two fixes, which TASK_010_REVIEW already specified and which the
engineer widened sensibly. Spend it on whether p16's *numbers and their causal
story* would survive publication.

## Deliverable

`.tasks/TASK_007_REVIEW_REPORT.md` + the `PROTOCOL.md` report format. Severities
with file:line and a concrete failure scenario. State explicitly, in one line at
the top: **does `.memory/01-ladder.md` finding 4 overclaim, underclaim, or is it
right?** I wrote it from the engineer's report without re-measuring, so it is
exactly the kind of second-hand claim this project keeps having to retract.

## Constraints

No root; no `/tmp` (scratch `.temp/review007/`); **no `git add`/`git commit`**; do
not edit `pilot/`, `.memory/`, `harness/`, or `patterns/` — you report, I fix. You
may build variants under `.temp/review007/`. Verus only via `./verus_run.py`.
clang `~/tools/llvm/bin/clang`, valgrind `~/tools/valgrind/bin/valgrind`, rustc
`~/.cargo/bin/rustc` — none on PATH. `timeout <N> <cmd>`.
**A gate run on a mirror writes into the tracked `results/gate/`** — check
`git status` before finishing and move anything you created into
`.temp/review007/`.

Notes to `.temp/review007/NOTES.md` as you go; agents here die to transient API
errors and notes make a resume cheap.

**If a prescription here is wrong, say so with the measurement.** Eight agents
have contradicted my written instructions and all eight were right — the last one
overturned three premises in a single review.
