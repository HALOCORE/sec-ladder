# TASK_070 — p22, hash probe: the first pattern where SAFE RUST DOES NOT HELP

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then **`.tasks/TASK_026.md`'s `§0` block**,
then **`.memory/06-catalogue.md`'s p22 triage** (it carries a harness analysis
that is now *implemented*), then `.memory/04-verus.md` (**`decreases` on
two-cursor loops**), `.memory/03-measurement.md` (**the two `Ir` conventions, the
INLINE-MODE rule, the DOMAIN rule, and the RESIDUE-CLASS rule from p38**), and
`.memory/02-bench-rules.md`'s **last two sections** — `forbidden_hits` now
**hard-fails**, and `run.timeout_s` is the mechanism you are about to be the
first user of. Templates: `patterns/p38-alias-pun/` and
`patterns/p27-handle-table/`.

## Why this pattern is the sharpest one left

**Every other pattern here asks what safety costs. p22 asks what safety does not
buy, and the answer is "this".**

- The bug is an **open-addressing probe loop that never terminates** on a full
  table. It is **memory-safe** — every access in bounds, no UB, Miri silent.
- ⚠ **Safe Rust does not prevent it either.** R2, R3 **and R4 all hang.** There
  is no bounds check, no lifetime, no `unsafe` to point at. **This is the first
  pattern where the safe rungs are not better.**
- **Only R5 catches it, as a `decreases` obligation** — a *termination* proof,
  which no R5 here has ever had. Every existing R5 proves safety.
- **It is the exact mirror of p09** (a bug the proof could not see) and of p47
  (a property the proof could not state). **Here the proof is the only thing that
  sees it.** That three-way contrast is the finding.

⚠ **Treat the catalogue row as a PRIOR.** Bug classes here have been overturned
on four patterns and upheld on two, and **p47 overturned its own**. §0 settles it.

## §0 — settle the bug class AND the hang, first

`.memory/06-catalogue.md` predicts *"R2, R3 and R4 all hang, only R5 catches
it"*. **That is four claims and none has been measured.** §0's deliverable is a
written decision in `NOTES.md` §0 with the measurements behind it.

⚠ **The specific way this collapses, and it is likely:** a probe loop written
`i = (i + 1) % cap` over a **full** table hangs, but the same loop written with a
**bounded trip count** (`for _ in 0..cap`) is what a careful programmer writes and
does **not** hang. **So "safe Rust does not help" may be a claim about a
SPELLING, not about safe Rust** — which is exactly p10's failure mode in a new
costume. **Settle it:** is the hanging spelling the *idiomatic* one, or the one
you chose? If a bounded-trip-count R3 is natural and terminates, **say so plainly
and re-frame the pattern around what the proof buys over the bound** — that is a
smaller but honest result.

⚠ **And the hang must be a REAL infinite loop, deterministic across cells.** Not
"slow", not "very large table". `_confirm_hang` re-runs at
`min(10 × budget, RUN_TIMEOUT)` and **fails if the cell terminates** — you cannot
declare a slow cell as hung, by construction.

## What is NEW here: you are the first user of the hang machinery

Built at TASK_068 and hardened at TASK_069 after a review found it accepted a
3.5 s terminating cell as a hang.

- **Two declarations are required and both are enforced**: `model.expected_hang`
  (the *prediction*, derived from the blob's bytes) **and** the contract's
  `run: {timeout_s, why}` (the *budget*, a `contract_sha256` pin). Neither alone
  goes green.
- ⚠ **`RUN_BUDGET_FLOOR = 1.0 s`.** The slowest shipped `O0` cell on `large.bin`
  is 198 ms, so 1.0 s is ~5× that. **If p22 needs a budget below the floor, that
  is a finding — report it, do not work around it.**
- ⚠ **`_confirm_hang` verifies ONE cell**, the first in sorted matrix order.
  **p22 hangs 12–20 cells and is the pattern that must decide this** (RECAP
  "Owed" 17). Checking all costs `10 × budget × n_hung`. **Make the call with the
  measurement and say what you chose.**
- ⚠ **A declared-hang input is a BLOCKED Miri row**, so **p22 will land
  `PASS-WITH-BLOCKED-ROWS`, not `PASS`** — p01 is the only other one. **Say so in
  `NOTES.md` up front**; a reader who expects `PASS` will think something broke.
  `MIRI_PROBE_ITERS` cannot help: it clamps kernel *calls*, and the first call is
  the one that never returns.

## Verus — this is the hard part, and the budget is MORE than one session

**The `decreases` measure is the pattern.** `.memory/04-verus.md`: **`decreases
b - a` fails on two-cursor loops**, and a probe sequence's natural measure is the
set of **unvisited slots**, which needs a ghost set rather than an arithmetic
expression.

> **Two routes, and I do not know which is right — that is my least certain call,
> named.** (a) A **ghost set** of probed indices, `decreases cap - |visited|`,
> which is faithful but needs set reasoning in the loop invariant. (b) A **bounded
> probe counter** carried in exec code, `decreases cap - probes`, which is trivial
> to prove — **but it may be proving termination of a loop that was already
> obviously terminating**, i.e. the proof would be circular with the fix.
> ⚠ **If (b) is what works, the honest finding is that R5 does not "catch" the
> bug so much as REQUIRE THE FIX**, which is a weaker and more interesting claim
> than the catalogue's. **Say which happened.**

**Two proof mutants that FAIL**, and here at least one should fail on the
`decreases`, not on a safety clause — that is what makes it a termination result.
Use `~/tools/verus/vstd/` — **not** `../LearnVeri/_VERUS_DOC_/vstd/`.
`global size_of usize == 8;` may be needed.

## What p22 must have regardless

- **Record the `slb-contract` sha256 in `NOTES.md` before building any cell**, and
  ⚠ **read the shared named-spelling paragraph from a DONOR `spec.md` if you
  write a contract generator — never embed it.** If `spec.md` is generated, **fix
  the generator and re-run it.**
- ⚠ **`forbidden_hits` now HARD-FAILS.** `exec_code` blanks ghost code, so your
  `proof {}` and `assert(…)` are safe — **but three false-positive shapes
  survive**: substring, whitespace-collapse, and an entry that backticks the
  *replacement*. **Prefer longer, more specific spellings.**
- **Search the R4 side.** *"Degenerate as far as this task searched"* has been
  **false on four consecutive patterns**, and every time it flattered a rung.
  Publish the fixed-R4 bound **and** the span, "cheapest found", input named.
- **NAME THE INLINE MODE at every figure.**
- ⚠ **If you fit a law, CHECK THE RESIDUE CLASS of any parameter your bands hold
  constant** — p38's additivity miss was two-thirds a band sitting at
  `nw ≡ 0 (mod 8)` while the others sat at `0`. Fits in sample, misses out of it,
  and nothing in-sample warns you.
- **Adversarial rows per rung.** ⚠ Here the harm is a **hang**, so say what an
  adversarial row means when four rungs never return.
- **No `ns` claim without a layout population**; port `controls/clayout.py` and
  ⚠ **point `OUT` and its scratch default at `.temp/p22/`** — p27's copy still
  said `.temp/p14/` and overwrote p14's `meta.json`.
- **TCB: one number plus the U-license / V-gap / infra classification.**

## Done when

The p38 checklist plus §0's decisions; complete `check.py p22` (expect
**`PASS-WITH-BLOCKED-ROWS`**, 0 failures); checksums against an independent
`model.py`; two failing proof mutants; `measure.py --check-stale` clean.
**Paste actual output.** ⚠ Doc edits make a gate record STALE — re-run after.

## Constraints

No root; no `/tmp` (scratch `.temp/p22/`); **no `git add`/`git commit`**; do not
edit `pilot/`, `.memory/`, `harness/`, `common/`, or any existing pattern.
**If p22 seems to need a `harness/` change, STOP and report it** — the hang
machinery was just built for you and a second change costs another 20-gate sweep.
Verus only via `./verus_run.py`. clang `~/tools/llvm/bin/clang`, gcc
`/usr/bin/gcc`, valgrind `~/tools/valgrind/bin/valgrind`, rustc
`~/.cargo/bin/rustc` — none but gcc on PATH. `timeout <N> <cmd>`. Never
`pkill`/`killall`; **no `nohup … &`**. ⚠ **This pattern deliberately builds
programs that never return — always run them under `timeout`, and never in the
background.** Measurements in the FOREGROUND. **You are the only agent running.**

Notes to `.temp/p22/NOTES.md` as you go.

**If a prescription here is wrong, say so with the measurement.** ⚠ **Running
count 148.**

**What I am least sure of, by name: the Verus route (a) vs (b) above, and
whether "safe Rust does not help" survives §0.** If a bounded-trip-count R3 is
the idiomatic spelling and terminates, the headline collapses to a spelling
result — **that is p10's failure mode and I would rather find it in §0 than in
review.** Measure it first, before building six rungs on it.
