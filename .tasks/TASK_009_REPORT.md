# TASK_009 — report (assembled by the manager)

The engineer completed Parts A–H but was killed by transient API 529 errors four
times, three of them on resume, before it could write its own report. Its durable
notes are `.temp/p009/NOTES.md` and they are the primary record. This file adds
what **the manager verified directly** afterwards, so nothing here rests on an
unreported claim.

## Verified by the manager

**Both gates green on the delivered tree, complete runs.**
`.temp/mgr-gate-p01.log`, `.temp/mgr-gate-p02.log` — `check.py: PASS` both.

**The verified twin costs zero instructions.** R4≡R5 unchanged:

| pair | O3 | O0 |
|---|---|---|
| p02 unsafe vs verus | `exact`, `md5_fn 0e5b59364bb6` | `norel`, `5c0d4e0be96b` |
| p01 unsafe vs verus | `exact`, `md5_fn 619b1d1b6561` | `norel`, `78b8c557c474` |
| p01 safe_naive vs safe_naive_verus | `exact`, `12d307f2b9d1` | `exact`, `bf555ac41318` |

p02's O3 digest is bit-identical to the value measured before TASK_009, so
established result 1 is unaffected. The `#[cfg(slb_twin)]` makes this structural.

**The twin's contract is derived, not declared.** `check.py:2155` compares
`vparse.norm_clause(twin.sig)` against the trusted item's and fails on any
difference — and in Verus the `requires`/`ensures` are part of the signature, so
the author controls **only the body**. Weakening the trusted item and leaving the
twin alone is a signature mismatch, which matters because *Verus alone passes
that mutant* at 12 verified / 0 errors. That was the property the mechanism rests
on and it holds.

**b9, the toothless twin — finished by the manager, two independent attacks,
both caught.** See `.memory/04-verus.md` for the writeup. Mutants in
`.temp/mgr-b9/` and `.temp/p009/b9/`:

- the engineer's: a trusted item with a `requires` and **no `ensures`** (the shape
  `.memory/04-verus.md` recommends) twinned by an **empty body**.
- the manager's: a twin body of `loop { }` under
  `#[verifier::exec_allows_no_decreases_clause]`, which never returns and so
  satisfies any postcondition vacuously — 13 verified, 0 errors. Without the
  attribute Verus rejects it outright and then names the attribute that disables
  the check.

Both produce `FAIL [twin] … still verifies with the precondition DELETED`. **The
load-bearing check is the per-run deletion test, not the twin verifying** — and
because it tests the twin's *dependence* on the precondition rather than
enumerating bad shapes, it caught an attack its author had not thought of.

## Delivered, per the engineer's notes

- **A** — bracket-stripped conjunct splitting; "atomic" is now a positive claim.
  Also found and fixed an **unsound** split: a `forall` body split at its inner
  `&&` left the bound variable free, so the mutant failed to *compile* and that
  was read as "load-bearing". Fail-open in the direction of health.
- **B** — the verified twin, stage `5c-twin`; 8 mutants failing for 8 distinct
  reasons, two beyond the design (twin missing its `#[cfg]`; twin calling the
  trusted item and re-using the axiom it exists to check).
- **C+D** — probe carries generics/`where`/lifetimes, synthesises inside `impl`
  for `self`, gains the call site's ambient facts, and escalates
  Z3 → `nonlinear_arith` → `bit_vector`. `v@.len() <= usize::MAX` and both
  bitwise rows are now correctly reported as tautologies.
- **E** — `resolved` flag distinguishes "no verified body" from "could not
  resolve the name"; a mod-nested driver now gets its certificate via
  `--verify-only-module`.
- **F** — bound is unit-aware (`work_unit_bits`) plus a hatch capped at 64×.
  p09's bit-denominated shape passes; `1e-9` still fails even with a hatch.
- **G** — three minors.
- **H** — **the decoy driver region LANDS.** Not fixed; TASK_009 scoped it as an
  investigation. Full gate PASS with the payload live. See
  `.memory/06-catalogue.md`.

## Open, and owned by the next task

1. **Part H's fix.** The driver diff pins a *file*, not the code that executes.
2. **Whether the decoy trick also works against the C rung** — I asked and the
   agent died before answering. It determines whether H is one fix or two.
3. The tension recorded in `.memory/04-verus.md`: "prefer trusted wrappers with
   no `ensures`" and "a twin needs an `ensures` to have teeth" pull opposite ways.

## Caveat on this report

Assembled from another agent's notes plus my own verification. Everything under
"Verified by the manager" I ran; everything under "Delivered" is the engineer's
claim, cross-checked only to the extent that both gates pass and the stage output
matches the description. **A reviewer should treat the "Delivered" section with
the same suspicion as any engineer report** — arguably more, since its author
never got to state its own caveats.
