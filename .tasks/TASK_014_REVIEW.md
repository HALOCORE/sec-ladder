# TASK_014_REVIEW — a bug that cannot fire, a sanitiser told to expect nothing, and a threat to p05

**Role:** research reviewer
**Read first:** `.tasks/PROTOCOL.md`, then `.tasks/TASK_014.md` (the spec I
wrote), `patterns/p08-overlap-move/NOTES.md` (1095 lines — the delivery),
`git show 3b5283e`, and `.memory/01-ladder.md` **finding 12** (p05's causal
claim), which one of p08's measurements may undermine.

**There is no `.memory/` write-up to attack this time** — PROTOCOL rule 9 now
holds it until your review lands. So the usual question ("does the manager's
finding overclaim?") is instead: **what should finding 7 say, and what must it
not say?** Answer that in one line at the top of your report.

## Context you need

TASK_014 commissioned p08 to show a structural Rust win: overlapping `memcpy`
is UB in C and the borrow checker rejects it at compile time. The engineer
refuted three of my premises with measurements and the pattern still went green
first run. What it found:

- **glibc 2.39 x86-64 `memcpy` *is* `memmove`** — same function address, with a
  `dst-src < n → backward copy` branch. So the UB **never manifests on this
  box**, in 320 runs across every size regime.
- **ASan catches it** (`memcpy-param-overlap`) — but **not** in the
  configuration the gate builds, because this box's default `_FORTIFY_SOURCE=3`
  rewrites the call to `__memcpy_chk`, which ASan does not intercept.
- Consequently `model.py` declares **`sanitizer_expect = "clean"` on
  `adversarial-overlap`, the input that executes the bug.**

Five things to attack, in this order. The third is the one I most want an
answer to.

## Part 1 — `sanitizer_expect = "clean"`, which the engineer nominated itself

`patterns/p08-overlap-move/model.py:290`. The gate is being told to expect
silence from a sanitiser on the one input that commits UB.

- **Re-run the isolating experiment.** Same source, `-D_FORTIFY_SOURCE=0` vs
  the gate's default, gcc and clang. Does ASan really fire in one and not the
  other, and is `__memcpy_chk` really the discriminator? Paste both.
- **Is "clean" the right declaration, or is it a green gate bought by pointing
  the gate at a build that cannot see?** Consider the alternatives the engineer
  did not take: declare the *expectation* the unfortified build produces and
  let the row fail loudly; mark it a documented blocked row (p01's Miri
  precedent); or leave it clean and rely on prose. Argue which is right.
  "The engineer's call is fine" is a welcome answer.
- **The generalisation is the real risk**: does any *other* pattern in this repo
  have a `mem*`/`str*` call that gcc rewrites to a `_chk` form, so that its
  sanitiser row is also certifying a build that cannot see? Check p02 in
  particular — it is the pattern whose whole result is a `memcpy` with an
  attacker length. If p02's stage-7 row is blind too, that is a **blocker**
  against an existing published finding, not a p08 issue.

## Part 2 — does p08 still support the claim it was commissioned for?

The bug cannot fire on this platform. That is a fine result, but it changes
what may be said.

- Read `README.md` and `NOTES.md` §1c, §5d, §7 as a **hostile reader**. Do they
  claim a Rust safety win whose C harm is, on this box, unreachable? Is the
  distinction between *"the UB is real and a sanitiser sees it"* and *"the
  program computes the wrong answer"* held consistently, or does it slip?
- **R1 vs R1h = 0.00 Ir/call** because both call the same libc function. Is
  that written as a **libc property** — which is what it is — or does it read
  as "memmove is free", which would be false on a libc that implements them
  separately? This is the p02 "gcc-only measurement generalised to C" mistake
  in a new costume; check for it specifically.
- Given all this: **is p08 carrying its weight in the catalogue**, or does it
  need a second platform to mean anything? Say so plainly.

## Part 3 — the threat to p05, which is why this review matters most

`NOTES.md` §3c reports **R3 − R4 = 26.00 Ir/call flat**, attributed to a
**provably dead range-check pair per round that LLVM keeps** — and the engineer
notes it is **linear**, offering that as *sharpening* p05.

I think it may do the opposite, and I want this chased hard.

`.memory/01-ladder.md` finding 12 says p05's `O(nrow)` safety cost exists
because `nrow*ncol <= avail ⟹ i*ncol+j < avail` is **nonlinear**, i.e. *"the
safety cost is the price of the optimiser failing the lemma the proof proves"*.
That story needs LLVM to fail at nonlinear implications specifically. **If LLVM
also keeps a provably dead check whose implication is purely linear, then
nonlinearity is not the mechanism** — it is just "LLVM does not eliminate dead
bounds checks", and p05's headline is a much weaker and more ordinary claim.

- **Verify the 26.00 and verify that the retained check is genuinely linear** —
  from the disassembly and the source, not from the engineer's description.
- **Then adjudicate finding 12.** Does it survive as written, does it need
  narrowing, or is it refuted? If it needs narrowing, propose the exact
  replacement sentence. Do not re-measure p05 to do this; reason from p08's
  evidence plus what p05's `NOTES.md` already records, and say what a decisive
  experiment *would* be if the two cannot be reconciled from existing data.

## Part 4 — the `rep`-string measurement claim, which touches every pattern

`NOTES.md` §4a: **callgrind counts a `rep`-string instruction once per
iteration**, so `rep stosb` reads 1.006 Ir/byte where gcc's inlined
`rep stos %rax` reads 0.126 — and on `small`, `Ir` says c-gcc is 33% *cheaper*
while wall clock says 2.9% *dearer*. **`Ir` and ns disagreeing in direction with
a named mechanism** is a strong methodological finding.

- **Verify the counting behaviour directly** with a minimal callgrind run, not
  from inference over p08's numbers.
- **Then check the blast radius**, which is the part that matters: does any
  *previously published* number in `results/` sit downstream of a `rep`-string
  instruction inside a measured kernel? p02 copies buffers; p05 and p16 fold.
  If any past `Ir` comparison is contaminated, that is a **blocker** and it
  outranks everything else in this review.

## Part 5 — the proof, the twin, and my own two errors

- The twin verified first try, and its **unique** catch is M2 (a weakened
  `requires`), not M4 (a dropped `ensures` conjunct) — `NOTES.md` §8 says so.
  Confirm M2 really passes the shipped configuration and fails only under
  `--cfg slb_twin`; that single fact is the entire case for keeping the twin,
  and it is the first time in six patterns it has been demonstrated. If it does
  not reproduce, the twin has still never earned its keep and I need to know.
- **My four-clause `ensures` sketch shipped as three**, on the ground that the
  length clause is not load-bearing when the caller holds a fixed-size array.
  Attack that: construct a wrong trusted body that the three-clause contract
  admits and the four-clause one would have caught, or show none exists.
- Stage 5a rejects `&mut [u8; SCR]` — a claimed **false positive** in the gate,
  worked around by widening to `&mut [u8]`. Confirm it is a false positive
  rather than the rule doing its job, and say whether the widening cost the
  contract anything.
- `grep -n 'assume\|external_body\|external\b\|assume_specification' verus.rs`
  and recount the TCB tally against `NOTES.md` §8.

## Part 6 — standard validity, briefly

`PROTOCOL.md`'s checklist; skip what the gate certifies. Priorities: R2 is a
*fair* naive port and not a pessimisation; the three controls do what they say
(especially that Control 3 — safe, compiles, does not panic, wrong — actually
produces a wrong answer); the manifestation table's "all 8 builds, model's
answer, exit 0" reproduces on at least one cell you pick yourself; and
`model.py` is genuinely independent rather than a transliteration.

Adjacent, if cheap: `patterns/p05-index-flatten/NOTES.md:13` references a §12
that does not exist.

## Part 7 — clean negatives

Name what you tried that did not land. A named attack that failed is worth as
much as a finding and stops the next agent re-running it.

## Not in scope

Not a gate-bypass hunt. Do not modify `harness/` — the engineer already
identified a stage-7 change and I will spec it separately. Do not re-measure
p16 or p17. p08's gitignored `inputs/` blobs are known and fine.

## Deliverable

`.tasks/TASK_014_REVIEW_REPORT.md` + `PROTOCOL.md`'s format. Severities with
file:line and a concrete failure scenario. **One line at the top: what should
`.memory/01-ladder.md` finding 7 say about p08, and what must it not say?**

## Constraints

No root; no `/tmp` (scratch `.temp/review014/`); **no `git add`/`git commit`**;
do not edit `pilot/`, `.memory/`, `harness/`, or `patterns/`. Verus only via
`./verus_run.py`. clang `~/tools/llvm/bin/clang`, valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none on PATH.
`timeout <N> <cmd>`. Check `git status` before finishing and move anything you
created under `results/gate/` into `.temp/review014/`.

Notes to `.temp/review014/NOTES.md` as you go.

**If a prescription here is wrong, say so with the measurement.** Fourteen
agents have contradicted my written instructions and all fourteen were right —
the last one refuted three of my premises in a single Part 0. The claim in
*this* file I am least sure of is **Part 3's suspicion that p08 undermines
p05**; I would rather be shown it is wrong with a disassembly than have it
agreed with politely.
