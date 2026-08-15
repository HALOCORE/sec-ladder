# TASK_004_REVIEW — the first real result, and the first real test of the harness

**Role:** research reviewer
**Read first:** `.tasks/PROTOCOL.md`, `.tasks/TASK_004.md`, then
`patterns/p02-buffer-copy/` in full — `spec.md`, `model.py`, `NOTES.md`, all rungs.

p02 is the first pattern that produces a **publishable claim** rather than a
calibration number. If a claim here is wrong, it is wrong in a paper. Weight your
effort at the claims, not the code style.

## Priority 1 — is the C rung a fair opponent, or a strawman?

Everything rests on this. The C kernel is passed **both lengths** and R1 ignores
them. The engineer argues that is the more damning CWE-787 shape and that it holds
the calling convention fixed for the R1-vs-R1h comparison.

Attack it: is that idiomatic C, or a caricature written to lose? A C programmer
handed `dst_cap` and told to copy an attacker-controlled length either checks it
or is writing an obvious bug. Consider whether the honest baseline is instead C
that *doesn't receive* the capacity (the length genuinely unavailable — the real
shape of many CVEs), and what that would do to the R1-vs-R1h delta. If the current
shape is defensible, say why; if not, this invalidates the headline comparison.

Also: R2 must be a fair *naive* port, not a pessimised one — its O(n) result is
the most surprising number in the pattern and the one most likely to be an
artefact of how it was written. Rewrite it the way a competent Rust programmer
would and see if the O(n) survives.

## Priority 2 — the fold dominates the kernel. Does the perf half mean anything?

The engineer states plainly that the result fold is **~96% of kernel cost and the
copy ~4%**. So "the cost of a bounds-checked copy" is being measured through a
kernel that mostly isn't copying.

- Are the marginal figures (+5/+12/+10/O(n)) actually isolated from the fold, or
  contaminated by it? Check the derivation.
- The fold is a serial `acc*31 + byte` per byte, which does not vectorise. A
  word-wise XOR/ADD reduction would, taking the fold from ~2.2–6.7 Ir/byte to
  ~0.06 and letting the copy dominate. **Would that be better?** The counter-risk
  is in NOTES §0 and is unmeasured: a cheaper/narrower fold may let LLVM narrow or
  elide the copy entirely, which would destroy the pattern. **Measure it** — this
  is the single highest-value experiment in this review, because the answer sets
  the result-consumption design for all 47 patterns.
- If the fold must stay heavy, is the honest presentation "we report marginal
  cost only", and is that what `results/tables/` actually does?

## Priority 3 — verify the headline claims independently

Re-derive, do not re-read:

- **The one-byte overflow is silent in 7 of 8 R1 builds.** Reproduce. Confirm the
  eighth aborts because of `_FORTIFY_SOURCE` and not the program, and that the
  ASan diagnostic says what NOTES says.
- **R2 is O(n)** (+178 at 61 B, +1025 at 4092 B). Reproduce at a third size and
  check the slope is really linear rather than two points and a line.
- **gcc beats clang by 10% on Ir and loses by 23% on wall clock.** Both directions
  reproduced? This inverts the p01 story and `.memory/03-measurement.md` warns Ir
  is not cycles — confirm and explain if you can.
- **R4 ≡ R5 byte-identical** at O3 (`md5_fn 0e5b59364bb6…`, 72/70 instructions).
- The control — `safe_naive` with the check deleted panicking at exit 101 — is
  what turns "Rust makes it non-optional" from slogan into measurement. Verify it.

## Priority 4 — did the harness get weakened to fit a second pattern?

Seven harness changes were made. For **each**, decide whether it generalises or
whether it loosened a check to accommodate p02:

- Does any change make a p01-era bypass work again? Try two.
- `check_proof_domain` only excludes p01's key `"v"`, and the `off` range line is
  p01-named — how much p01-shape is still baked in?
- `asm.py`'s docstring claims `__memcpy_avx_unaligned_erms` matches `_BULK_MEM_RE`
  and the engineer says it does not. Confirm; if the bulk-memory escape hatch does
  not match real glibc symbols, the anti-collapse relaxation may be both wrong and
  load-bearing.
- `work_per_call` is in bytes and ALPHA is justified in 64-bit-lane terms. The
  engineer measured 2.2–6.7 Ir/byte here but notes a vectorised copy-and-fold
  would run ~0.06 and **fail the floor**. Is the derived floor about to false-fail
  the next pattern, exactly as the old checks false-failed p02?

## Priority 5 — the new vacuity mode

Mutant M7: deleting one of two `ensures` clauses leaves an **inconsistent**
postcondition, so every caller verifies vacuously, and the TASK_005 structural
rule cannot see it because the `requires` is intact. Only the declared pin catches
it — and declared pins are exactly what TASK_003_REVIEW showed are self-certifying.

Is there a mechanical check? Consider: does Verus have a way to detect an
unsatisfiable postcondition (a proof that `ensures` is realisable — e.g. an
`assert(false)` reachability probe after the call, or requiring each `ensures`
clause to be independently consumed somewhere)? Recommend something implementable,
or state clearly that this class is undetectable and must be caught by mutation
testing, which then has to be a gate stage rather than a manual ritual.

## Also

- Is `spec.md`'s Verus contract a faithful description of `copy_nonoverlapping`?
  The engineer says this is argued in prose, not checked, and that it "is the whole
  memory-safety TCB". Read it adversarially.
- No R2v control cell for p02, and `gen.py --sweep` was never run (residue effect
  is two points, not a curve). Do either matter for the published claims?
- Scope/hygiene: nothing staged or committed; `pilot/`, `PLAN.md`,
  `pilot/README.md` untouched.

## Deliverable

Findings ranked `blocker`/`major`/`minor` with file:line and concrete failure
scenarios, plus the explicit "verified correct" list. A refutation of a headline
claim, or a measurement settling the fold question, is worth more than ten style
notes. Do not fix anything.
