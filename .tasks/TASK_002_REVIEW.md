# TASK_002_REVIEW — adversarial review of the harness and p01

**Role:** research reviewer
**Read first:** `.tasks/PROTOCOL.md`, `.tasks/TASK_002.md`, then the new code.

This is **the template 47 patterns will clone**. A defect here multiplies by 47.
Weight your effort accordingly: correctness of the *method* matters more than
polish of the code.

## Priority 1 — the anti-collapse mechanism may have replaced one artefact with another

The driver defeats CSE with a serial dependency: `acc → div → off → kernel → acc`.
It demonstrably works (the loop survives; disassembly is in the report). But:

- **A hardware `div` is 20–40 cycles and one `Ir`.** So the mechanism is nearly
  free in our *primary* metric and potentially dominant in wall clock. Does the
  dependency chain compress the measured differences between rungs? Quantify: what
  fraction of the loop's latency is the `div`? Is a cheaper barrier (multiply-shift
  modulo, mask when `nwin` is a power of two, LCG) equally collapse-proof? Note the
  power-of-two mask would reintroduce the `n mod 4` residue trap by construction —
  weigh that.
- Is the mechanism *equally* strong in all six cells, or does one rung's codegen
  get more relief from it than another's?
- If you conclude the `div` is fine for `Ir` but poisons wall clock, say so
  explicitly — `.memory/03-measurement.md` still lists wall clock as a metric.

## Priority 2 — `whole` mode is no longer the same experiment across languages

`-C lto=fat` is impossible for R5 (vstd rlib ships no bitcode), so `whole` was
redefined for Rust as "single crate, cgu=1, no `inline(never)`" while C keeps
`-flto` across three TUs. Assess whether these are comparable enough to publish
side by side, or whether C should drop `-flto` for symmetry. This is a
methodological choice that will be inherited 47 times.

## Priority 3 — is the p01 proof actually load-bearing?

The engineer reports the `requires` **is** discharged at a verified call site
(mutating the driver's guard produces `precondition not satisfied ... at
kernel(...)`), which satisfies `.memory/02-bench-rules.md` rule 2. But it also
reports the `ensures` is **not consumed** by any caller, so functional correctness
rests only on mutation M4.

- Verify the call site really is verified — re-run a mutant yourself.
- Is an unconsumed `ensures` acceptable, or does it make the functional half of the
  spec decorative? Would a ghost assertion in the driver be worth breaking loop
  byte-identity for? Recommend a policy for all 47 patterns.
- Recount the TCB (claimed: **6 lines across 3 `external_body` items**). Confirm
  only `get_unchecked` carries a safety claim and the other two state no `ensures`.
- The report notes deleting a `requires` from an `external_body` wrapper **verifies
  cleanly**. Confirm this, because it is now the project's most dangerous known
  failure mode and `.memory/04-verus.md` documents it as such. Is there any
  mechanical check that would catch it? If so, `check.py` should have it.

## Priority 4 — verify the numbers, independently

- `harness/asm.py selftest` claims to re-derive the pilot's 32/30, 33/31, 57/46,
  37/33 and both byte-identities. Run it. Then check whether `asm.py`'s extraction
  convention is *sound*, not merely self-consistent — it replaced
  TASK_001_REVIEW's digests (`e5310297…`/`a23e076c…`) with new ones
  (`935221a8…`/`98e4a665…`) on the grounds that the old convention was never
  recorded. Was that legitimate, or did the convention quietly change meaning?
- p01's static counts (33/38/59/58/39) differ from the pilot's (32/33/57/37).
  Confirm this is fully explained by the changed kernel signature
  (`(v, off, len)` vs `(v, n)`) and not by a regression in extraction.
- **The striking claim**: after subtracting each cell's own isolated `main` figure,
  clang C and unsafe Rust are equal "to within 1 instruction over 82M additions",
  and the apparent 8% clang win in raw whole-mode `main`-exclusive Ir is an artefact
  of Rust inlining the loader into `main`. Verify the correction and the residual.
  If true this is a headline result and must be airtight.
- The `+340/call` inlined-R2 observation on `large` — reproduce or refute. The
  report already labels it an observation; decide whether it survives.
- Confirm `inputs/gen.py` now gives `small` and `large` **different residues mod 4**
  and that the sweep covers all four.

## Priority 5 — does `check.py` enforce what it claims?

It reports 28/28 PASS. Verify each of the four "Proof domain must cover the measured
domain" rules is genuinely enforced, not merely present as a stage name. Try to
sneak past it: an `external_body main`, an input violating `requires`, a rung whose
kernel got constant-folded, two rungs with divergent driver loops. It should catch
all four. Anything it misses is a blocker, because 47 patterns will trust it.

Also: the C-vs-Rust driver-loop equivalence is checked by **required substrings**
rather than a mechanical diff. Is that strong enough to catch a real divergence?

## Also

- Scope/hygiene: nothing staged or committed, `pilot/` untouched, `PLAN.md` and
  `pilot/README.md` untouched, no writes outside the sanctioned paths.
- `.memory/` edits the engineer made — are they accurate, or did any overreach?
- Self-reported gaps: no Miri on R4/R5, `panic=abort` and `O0d` unmeasured, no
  `Ir` for `O0 × large`. Correctly out of scope, or does one undermine a
  conclusion? Miri specifically: R4 is unverified unsafe code that 47 patterns will
  imitate — is shipping it without a UB check defensible?

## Deliverable

Findings ranked `blocker`/`major`/`minor` with file:line and a concrete failure
scenario, plus the explicit "verified correct" list. Do not fix anything.
