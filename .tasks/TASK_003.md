# TASK_003 — harden the gate before it is cloned 47 times

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, `.tasks/TASK_002_REVIEW.md` (the full finding
list — this task is its remediation), `.memory/02-bench-rules.md`, `.memory/03-measurement.md`.

## Why

`harness/check.py` reports 28/28 PASS on p01 and the review got **six different
defects past it**, including the pilot's exact fatal defect (`external_body main`).
The gate's only load-bearing check is step 2 (checksum agreement against a Python
model), and that model is hard-coded to p01. Right now the gate mostly certifies
that the gate ran.

Fix the method, not the symptoms. Where a check is textual, ask whether something
*semantic* can replace it.

## Blockers — fix first, each with a demonstrated bypass attempt

**B1 — attribute detection is defeated by a blank line.** `check.py:520-523` reads
attributes from `prefix.split("\n\n")[-1]`, so a blank line (or a comment
paragraph, or `#[cfg_attr(all(), verifier::external_body)]`) hides
`#[verifier::external_body]` on `fn main`. The review's shadow run passed green
while the Verus obligation count silently dropped 5 → 3. The TCB inventory
(`:429-432`) uses the same broken parse, so `main` also vanishes from the tally.
Also `:411` accepts a *comment* containing `kernel(` as proof of a call site.

The robust fix is not a better regex: **pin the expected obligation count in
`spec.md` and fail on any deviation.** An `external_body main` drops the count; so
does most tampering. Keep a structural check too, but make the count the backstop.
`check.py:443` currently only requires `N >= 1`.

**B2 — nothing connects `verus.rs`'s contract to `spec.md`'s.** `check.py:425-426`
tests only that the substring `ensures` appears. Replacing the real postcondition
with `ensures r == r,` gives `5 verified, 0 errors` and a green gate, while the
gate prints that it "re-derived `ensures` independently on 128 sampled calls".

Fix: **pin the exact `requires`/`ensures` text of the kernel *and of every
`external_body` item* in `spec.md`, and diff it mechanically.** The review notes
this single fence also closes the project's most dangerous known vacuity mode —
deleting a `requires` from an `external_body` wrapper still verifies cleanly
(`.memory/04-verus.md`), and no obligation count moves.

**B3 — rules 1 and 3 are never evaluated on `adversarial` inputs.**
`check.py:654` builds the model set from `good` only. `.memory/02-bench-rules.md`
rule 1 says *every* measured input. p01 hides this because its adversarial inputs
make zero kernel calls — but for the 47 downstream patterns the adversarial input
is *by construction* the one aimed at the precondition. Evaluate the contract on
every input, adversarial included.

## Majors

- **M4 — step 3 does not test anti-collapse.** `check.py:274-310` accepts any
  backward branch; with the barrier deleted entirely it still passes in both modes.
  Fix: assert **per-call `kernel_exclusive_ir` against a floor declared in
  `spec.md`**. `measure.py` already computes it; the gate just never asserts it.
- **M6 — `asm.py` reads past the symbol's declared size** into inter-function
  padding, so `md5_raw`/`n_raw` include alignment. Two identical kernels at
  different alignments would get different digests and `check_identity` hard-fails.
  Fix per `.memory/03-measurement.md`: use the `nm --print-size` extent for
  identity, report padding separately. (Both conventions and their pilot digests
  are now documented there — do not re-litigate which is "right", expose both.)
- **M7 — `check_identity` gates on the hypothesis.** `check.py:318-348` *fails the
  pattern* when R4≠R5. For a pattern where the proof legitimately costs something,
  that reports a finding as a harness failure. Fix: record it as a **result** in
  the JSON, not a gate failure. Only a *regression* against a pinned expectation
  in `spec.md` should fail.
- **M8 — the reference model is hard-coded to p01** (`check.py:57-112`). Every one
  of 47 clones would have to fork the gate. Fix: each pattern ships
  `patterns/pNN-*/model.py` exposing a documented function; the harness loads it.
  This is the single most important structural change in the task.
- **M9 — the C driver-loop check is defeated by addition.** `check.py:574-582`
  tests 7 required substrings; inserting `__builtin_prefetch` and an
  `__asm__ __volatile__` memory barrier passed green. That is exactly the
  cross-language asymmetry `.memory/02-bench-rules.md` forbids, and it can make the
  C column faster or slower at will. Fix: compare a normalised token sequence and
  the statement count, not substring presence.
- **M10 — 18 of 28 wall-clock cells exceed the 10% spread threshold** and
  `report.py:82-102` drops the warning `measure.py:294-296` records. The protocol
  says discard and say so. Surface it.
- **M11 — `asm.py selftest` silently no-ops on a fresh checkout** (`asm.py:444-452`
  returns 77; `check.py:213-214` downgrades to a note) because nothing in the repo
  builds the `.temp/build/docrepro` fixture. Commit a script that builds it.
- **M12 — `report.py` pairs static counts from `main` with `Ir` from `kernel`**
  (`report.py:62-79` vs `measure.py:234`), and labels an `O0` section
  "kernel inlined" where nothing inlines. Never mix symbols in one row.

## Method changes the review established (adopt these)

- **Swap the barrier to multiply-shift.** `(acc as u128 * nwin as u128) >> 64` is
  equally collapse-proof, keeps the cache randomisation (which is doing real work —
  a constant `off` runs `large` in 29.3 ms vs 46.3 ms), and is ~5 Ir and ~12
  cycles/iter cheaper than `div`. Do **not** use a power-of-two mask: it
  reintroduces the `n mod 4` residue trap by construction.
- **Define `whole` mode by *effect*, not flags**, in `.memory/01-ladder.md`: "the
  kernel may inline into the driver loop". C keeps `-flto` (verified necessary —
  without it the C kernel survives as its own symbol and `whole` collapses into
  `isolated`); Rust uses cgu=1 with no `inline(never)`. Matched on effect, so
  publishable side by side.
- **R5 must consume its own `ensures`.** Deleting the kernel's postcondition
  entirely still gives `5 verified, 0 errors` — same obligation count — so it is
  currently free decoration. Add a ghost `assert`/`proof` block in the driver that
  uses it, and **exempt ghost lines from the driver-loop diff** exactly as
  `check.py:186` already exempts `invariant`/`decreases`. Ghost code erases, so the
  byte-identity objection dissolves; only the gate's own textual rule stood in the way.
- **Miri policy**: mandatory for any pattern where R4 and R5 are **not**
  byte-identical, because that is precisely when R4 stops inheriting R5's proof.
  p01 is exempt on those grounds. Write this into `.memory/02-bench-rules.md` and
  wire the check.
- Fix `NOTES.md:258` — the published call-site mutant (`nwin + 2`) fails at
  `invariant not satisfied before loop`, not at the call. The real evidence needs
  the invariant repaired too, which then fails at `verus.rs:126:26`. Substance was
  right, evidence was mis-quoted.

## Minors (fix if cheap, list if not)

Sanitizer stage ignores exit codes (`check.py:604-608`); `README.md:58` says win
500 where `gen.py:47` uses 501; `--skip small --skip large` yields a green gate
with zero checksum coverage and no marker; `safe_naive_verus.rs` is built but never
verified; `verus!` block end is found by a literal comment (`check.py:511`);
`common/driver.c:53` mallocs the attacker-declared length where `driver.rs` does
not, so C exits 6 and Rust exits 5 on a huge declared length.

## Done when

Every blocker has a **demonstrated** bypass attempt that now fails — paste the
attempt and the failure. The gate must catch: `external_body main`, a tautological
`ensures`, a deleted `external_body requires`, a deleted barrier, a divergent C
driver loop, and an adversarial input violating `requires`. `check.py p01` still
green afterwards, and `.memory/` updated where behaviour changed.

## Constraints

No root; no `/tmp`; **no `git add`/`git commit`**; do not edit `pilot/`, `PLAN.md`,
`pilot/README.md`. `.memory/01-ladder.md` and `.memory/03-measurement.md` have
already been corrected by the manager for the digest-convention and
"within-1-instruction" errors — do not re-apply those.
