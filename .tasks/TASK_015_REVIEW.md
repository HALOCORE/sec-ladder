# TASK_015_REVIEW — is there a stable safety number at all?

**Role:** research reviewer
**Read first:** `.tasks/PROTOCOL.md`, then `.tasks/TASK_015.md` (the spec),
`.tasks/TASK_014_REVIEW_REPORT.md` **blocker B1**, `git show ad661ed` and
`git show 37c30e6`, `patterns/p05-index-flatten/NOTES.md` **§12** (new — it
carries both prior reviews and this audit), and `.memory/01-ladder.md`
finding 6 plus the **corollary rule**, both of which now carry text marked
**PROVISIONAL — not yet reviewed**. That text is what you are reviewing.

The engineer's variants are in `.temp/p05r3/`.

## Context

I asked for p05's R3 to be replaced by `chunks_exact`. The engineer **declined**
and produced a control I had not asked for: apply the same consumed-slice idiom
to the **unsafe** rung (`unsafe_consume.rs`, ~10 lines) and unsafe goes back on
top — p05 **+11.00 Ir/call, flat in `nrow`**; p16 `nrec + 3`. On that basis
"safe Rust beat unsafe Rust" became an idiom mismatch rather than a language
fact, and the project acquired a proposed methodological rule: **compare
idiom-matched rungs, or publish the spread rather than a cell.**

**That control is now load-bearing for the whole result set, and it is its
author's own design.** `PROTOCOL.md` rule 3 says a different agent attacks it.
That is Part 1, and it outranks everything else here.

## Part 1 — is R4′ a fair unsafe rung, and is +11.00 real?

- **Rebuild `unsafe_consume.rs` and re-derive the number yourself.** Do not take
  the table on trust.
- **Is it a *fair* R4, or an artificial best case?** The checklist question
  `PROTOCOL.md` asks about C ("idiomatic C, or Rust-in-C-syntax written to
  lose?") applies here in reverse: is this what an unsafe-Rust author would
  actually write, or is it tuned to win a comparison the engineer had just
  framed? Check it does the same work — same bounds semantics, same trip counts,
  no skipped operation — and that the checksum equality on 150/73 inputs is
  against the **shipped** R4 and not merely against itself.
- **+11.00 flat rests on three points** (nrow 19, 41, 65). `.memory`'s own
  residue rule says sweep two full cycles and never sample two points; p05's
  residue modulus is 8 and the gate ships 144 sweep blobs. **Sweep it.** If +11
  is flat in `nrow` but moves with `ncol` residue, the "O(1) not O(nrow)" claim
  needs restating.
- **Does the same move work on the *safe* side one more time?** If R3″ can
  chase R4′, and R4‴ can chase that, then the gap is not converging and the
  honest conclusion is stronger and stranger than "compare idiom-matched
  rungs". **Try at least one more round on p05 and report where it lands.**
  This is the question I most want answered.

## Part 2 — the policy, and I want your recommendation not just a critique

Three candidates are on the table for how the ladder reports a rung whose number
depends on spelling as much as on the rung:

1. **Idiom-matched pairs** — every rung written in one declared style per
   pattern, so the delta is attributable.
2. **A published spread per rung** — N spellings, report min/max, no single cell.
3. **A declared canonical idiom** per pattern, pinned in `spec.md` like every
   other contract term.

Each has a cost. (1) needs a definition of "same idiom" that a gate can check,
and it is not obvious one exists. (2) makes the headline table unreadable and
invites "you picked N". (3) is self-certifying in exactly the way
`.memory/02-bench-rules.md` warns about — the author declares the idiom and then
measures it.

**Recommend one, argue it, and say what it would cost to retrofit across the six
existing patterns.** If you think the right answer is a fourth thing, say that.
This decision shapes every remaining pattern and the writeup, so a clear
recommendation is worth more than a balanced survey.

## Part 3 — the audit numbers, which are thinner than they read

The engineer flagged these itself; confirm or bound them.

- **p16's `R3′ − R4` is fitted over 6 points across 2 residue classes**, not
  swept. p16 ships sweep blobs — use them.
- **p17 has no sweep inputs at all**, and its `−19.00` is a constant over two
  bands that both happen to have `nsuf = 3`. It is **not** established as
  independent of `nsuf`. Either establish it or say the number is unsupported.
- **The `div` finding.** `chunks_exact` with a runtime chunk size emits a
  hardware `div` that callgrind prices at 1 `Ir`. Verify directly, and say
  whether p16's and p17's beating spellings carry the same defect — if they do,
  three "cheaper" results are all instruction-count artefacts and the audit's
  headline changes again.

## Part 4 — did the landed corrections land correctly?

Both gates went green with `contract_sha256` unchanged, which is the right
outcome; check the prose actually says the right thing now.

- p05's `NOTES.md`/`README.md` retractions, and the new **§12**. Does anything
  refuted survive anywhere in the file? Grep, do not recall.
- p08's four corrections, especially the `README.md` "full arc" row — the claim
  it replaced was *"the bug is not expressible at R5"*, and the replacement must
  not overcorrect into implying R5 is worthless.
- **A fifth dangling cross-reference the engineer found and correctly did not
  fix**: `patterns/p08-overlap-move/spec.md:383` says "NOTES.md 7" and means §9.
  It is **inside the hashed contract block**. Confirm that is the only remaining
  one; I will fold it into the next task that re-runs p08's gate.

## Part 5 — clean negatives

Name what you tried that did not land. The engineer left one worth extending:
`split_at` and `split_first_chunk` are **indistinguishable** on p16 — identical
marginal `Ir` on all six inputs, same 92-instruction count, different `md5_fn`.
So the `Option` shape is not what does the work; consuming the slice is.

## Not in scope

Not a gate-bypass hunt. Do not modify `harness/`. Do not land any cell swap —
if the policy you recommend implies one, say so and stop. Do not re-measure p02
or p01.

## Deliverable

`.tasks/TASK_015_REVIEW_REPORT.md` + `PROTOCOL.md`'s format. Severities with
file:line and a concrete failure scenario. **Two lines at the top: (a) is R4′ a
fair unsafe rung, yes or no; (b) which reporting policy, in one sentence.**

## Constraints

No root; no `/tmp` (scratch `.temp/review015/`); **no `git add`/`git commit`**;
do not edit `pilot/`, `.memory/`, `harness/`, or `patterns/`. Verus only via
`./verus_run.py`. clang `~/tools/llvm/bin/clang`, valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none on PATH.
`timeout <N> <cmd>`. Check `git status` before finishing and move anything you
created under `results/gate/` into `.temp/review015/`.

Notes to `.temp/review015/NOTES.md` as you go.

**If a prescription here is wrong, say so with the measurement.** Sixteen agents
have contradicted my written instructions and all sixteen were right — the last
one declined the central deliverable I specced and was right to. What I am least
sure of here is **whether the gap converges at all** (Part 1's last bullet): I
have assumed one more round of chasing settles it, and I have no evidence for
that.
