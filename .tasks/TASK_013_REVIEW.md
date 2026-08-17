# TASK_013_REVIEW — is the check really free, and is the model really predictive?

**Role:** research reviewer
**Read first:** `.tasks/PROTOCOL.md`, then `.tasks/TASK_013.md` (the spec),
`patterns/p05-index-flatten/NOTES.md` (884 lines — the delivery),
`git show a02d282`, and **`.memory/01-ladder.md` finding 6**, the manager's
write-up, which is itself under review. The last three reviews each found the
manager's write-up overclaiming; assume the same risk.

## Context you need

p05 was commissioned to test whether a bounds check *blocks vectorisation* and
costs a multiple. The measurement **inverted** that: with vectorisation on, the
check costs `0.0000` Ir/element; with it off, exactly `4.2500`. The engineer also
**changed the kernel** from the commissioned `u64` row accumulator to `u32`,
because at this project's flags no LLVM rung vectorises with `u64`. The manager
endorsed that deviation.

Three claims carry the finding. Attack them in this order.

## Part 1 — "the bounds check costs 0.0000 Ir per element"

- **Re-derive the per-element rates yourself** from raw callgrind, on your own
  zero-residue lag pair. The claim is six decimals (`1.375000` = 11/8,
  `1.062500` = 17/16). A rate that lands exactly on a simple ratio is either
  beautiful or a sign the denominator was chosen to make it so — **check the
  denominator**: is "elements" counting header bytes, the `nrow*ncol` fold, the
  per-row Horner step?
- **Is `0.0000` a measurement or a subtraction of two numbers that were rounded
  first?** Show the raw counts.
- **Identical mnemonics across c-clang / safe_naive / safe_tuned / unsafe /
  verus** is a strong claim. Diff the actual kernel disassembly of all five. If
  they are identical, where did the bounds check *go*? A vectorised loop still
  needs a trip-count guard — find it, and say why it is free (hoisted? folded
  into the existing trip count? merged with the `nrow*ncol <= avail` check the
  kernel already does?). **"It vanished" is not a mechanism.** This is the part
  of the finding with no explanation attached, and it is the part a reader will
  disbelieve.

## Part 2 — the deviation, which is the most attackable decision here

The kernel was changed to make the phenomenon appear. That is exactly the shape
of a result fitted to its hypothesis, and it needs an independent judgement.

- **Confirm the `u64` claim.** Build the `u64` form and check it really does not
  vectorise in any LLVM rung at `-O3` without `-march`. Paste the remark.
- **Does the `u32` narrowing change the pattern's semantics or its realism?**
  A row sum of bytes into `u32` overflows at ~16.7 M elements per row. Is that
  reachable for any shipped input, and is the model consistent with the rungs?
  If `model.py` and the kernels agree only because no input gets near the bound,
  say so.
- **The judgement call:** is p05-with-`u32` still a fair representative of the C
  pattern it claims to model, or has it become a kernel designed to vectorise?
  Argue it. "The deviation is fine" is a welcome answer; so is "this measures a
  narrower thing than the write-up says".
- The engineer notes the vectorisation-off control **moves both sides**, unlike
  p16's `-unroll-count=1` which was a bit-for-bit no-op on R2. Does that weaken
  the `4.2500` attribution? p16's constant was confirmed by a no-op control; this
  one is not.

## Part 3 — the predictive model

`R2−R4 = 35 + nrow·f(ncol mod 8)`, `f = [84,32,35,38,41,44,47,50]`, claimed
128/128 exact with 112 points out of sample and a held-out band at max error
0.0000.

- **Re-run the held-out prediction yourself** at an `nrow`/`ncol` the engineer
  never measured. One point is enough if it is genuinely new.
- 16 parameters is a lot. Is `f` doing real work, or is it absorbing whatever is
  left over? The step-3 arithmetic run for residues 1–7 suggests structure;
  **`f(0) = 84` against an extrapolated 29 is unexplained.** Find the mechanism —
  it should be visible in the disassembly as a different trip-count split or an
  extra scalar remainder block. If you find it, that is the review's best
  contribution.
- Does the model hold for **c-gcc** too, with its period-16 claim? The write-up
  says periods are back-end specific; confirm on both.

## Part 4 — standard validity, briefly

`PROTOCOL.md`'s checklist; skip what the gate certifies. Priorities:
- R1 vs R1h really one line apart; the `int`-width check variant genuinely fires
  UBSan then ASan as reported.
- `adversarial-zero` with the guard removed: gcc 43 → 786,482 Ir/call (18,290×)
  while clang deletes the loop. Verify — an 18,000× is worth a second look.
- The 19/32 vectorised-cell count, and specifically that the 3 `O0 whole` hits
  really are an aggregate stack move rather than the fold.
- `+34.4% Ir → +30.5% time`: spreads, and whether the conclusion survives them.

## Part 5 — clean negatives

Name what you tried that did not land.

## Not in scope

Not a gate-bypass hunt. Nothing in `harness/` or `common/`. Do not re-measure
p16 or p17. p05's 189 MB of gitignored sweep inputs are known and fine.

## Deliverable

`.tasks/TASK_013_REVIEW_REPORT.md` + `PROTOCOL.md`'s format. Severities with
file:line and a concrete failure scenario. **One line at the top: does
`.memory/01-ladder.md` finding 6 overclaim, underclaim, or is it right?**

## Constraints

No root; no `/tmp` (scratch `.temp/review013/`); **no `git add`/`git commit`**; do
not edit `pilot/`, `.memory/`, `harness/`, or `patterns/`. Verus only via
`./verus_run.py`. clang `~/tools/llvm/bin/clang`, valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none on PATH.
`timeout <N> <cmd>`. Check `git status` before finishing and move anything you
created in `results/gate/` into `.temp/review013/`.

Notes to `.temp/review013/NOTES.md` as you go.

**If a prescription here is wrong, say so with the measurement.** Twelve agents
have contradicted the manager's written instructions and all twelve were right.
