# TASK_008_REVIEW — review the two blocker fixes, the new mutation stages, and the floor bounds

**Role:** research reviewer
**Read first:** `.tasks/PROTOCOL.md`, then `.tasks/TASK_008.md` (the spec),
`.tasks/TASK_006_REVIEW.md` (the review it remediates — the original mutants and
the mirror harness are described there and live in `.temp/review006/`), then
`.memory/02-bench-rules.md` and `.memory/04-verus.md`, which the manager has
already corrected from this engineer's report.

**This task changed the gate's soundness machinery.** Every previous review found
real defects; two found defects in work certified by a fully green gate. A fix to
a soundness check deserves harder scrutiny than the bug did, because a *broken*
check that reports healthy is worse than a missing one.

## What changed

- `harness/dloop.py` — `GhostHarbourError`; `normalise_file(..., verus_verified=)`
  fails closed. `region_in_verus` demoted to a *claim*.
- `harness/check.py` — `_verus_verified_files()` issues a certificate only from
  Verus's own verdict (in `verus.obligations` **and** `N verified, 0 errors`
  **and** `--verify-function <enclosing item> --verify-root` reports a verified
  body). `check_driver_identity` now takes it.
- `harness/check.py` — **new stage 5c-req** (`check_requires_strength`):
  a synthesised-`proof fn` tautology probe per conjunct, plus deletion for
  *verified* items only. Plus a third rule in 5a: every parameter a trusted
  `unsafe` body uses must appear in its `requires`.
- `harness/vparse.py` — `top_level_ops` / `conjunct_spans` / `delete_conjunct`;
  5c mutates conjuncts, and refuses clauses with top-level `==>` / `||` / `<==>`.
- `harness/check.py` — `MIN_DECLARABLE_IR_PER_WORK = 0.015625` hard floor,
  `LOOSE_FLOOR_MARGIN = 100` shout, margin printed, stage renamed.
- `_mutant_path` fix, `report.py` disambiguation, p01 digests, `measure.py p01`
  re-run, `results/tables/` regenerated, three p02 overstatements corrected.

## The engineer contradicted the spec and I accepted it — check that I was right

TASK_008 Part B prescribed "delete the `requires`, confirm some call site now
fails". The engineer measured that this is impossible for an `external_body`
item — deleting a trusted precondition only removes obligations from callers, so
**nothing anywhere fails** (all three mutants: 9 verified, 0 errors, control 9).
Only the *verified*-item row moves (kernel `requires[0]`: 8 verified, 1 error).

I have written that into `.memory/04-verus.md` as established. **Verify the
measurement yourself before it hardens into doctrine** — it is now the
justification for a three-check design that is considerably more complex than
what it replaced. If the engineer is right, say so explicitly and I will stop
re-litigating it.

## Attacks worth trying first

1. **Is the tautology probe sound in both directions?** It synthesises
   `proof fn <params verbatim> ensures <conjunct>, { }`. Two failure modes:
   *false positive* — a conjunct that is not a tautology but that the probe
   proves anyway because the synthesised signature carries extra facts (type
   invariants on `usize`, `old()`/`final()` handling, a `&mut` prophecy) or
   because the probe body inherits something the real call site does not;
   *false negative* — a genuinely tautological conjunct the probe fails to prove
   because the synthesised `fn` lost context, which reports healthy. The
   engineer flags the probe as untested on generics, `self` receivers and
   lifetime parameters. Construct one of each that the tree does not contain.
2. **Does parameter coverage actually mean anything?** The rule is "every
   parameter the `unsafe` body *uses* appears in the `requires`". Try:
   a `requires` that mentions every parameter in a way that constrains nothing
   (`src@.len() >= 0 && n >= 0 && from >= 0` — is that caught by the tautology
   probe once conjunct-split, or does mentioning the parameter satisfy 5a while
   each conjunct individually escapes?); and the engineer's own named gap, a
   `requires` that is non-trivial, mentions everything, and is still too weak
   (`from + n <= src@.len() + 1`). Confirm whether that last one passes the whole
   gate. If it does, that is the honest residual and it should be stated as one.
3. **Can the Verus certificate be forged or starved?** `_verus_verified_files`
   is now the single point on which ghost stripping depends. Try: a rung listed
   in `verus.obligations` whose `verus!` block is real but whose *driver region*
   sits in an item with no verified body; an item name that `--verify-function`
   resolves to something other than the enclosing item (two items, one name — is
   `vparse`'s duplicate-name failure reached first?); and the reverse denial —
   can a *legitimate* R5 be made to lose its certificate and fail spuriously?
   Fail-closed is right, but it must not be brittle.
4. **Conjunct splitting.** `top_level_ops` refuses `==>` / `||` / `<==>`. Check
   the refusal is not bypassable: `&&` nested inside a `forall|j: int| ... ==>`
   body, a conjunct containing `&&&`, an `&&` inside a function-call argument
   list or a subrange index, and operator precedence around `==` and `=~=`.
   A wrongly-split conjunct produces a mutant that fails to verify for a
   *syntactic* reason, which the stage would read as "load-bearing".
5. **The floor's new bound.** `MIN_DECLARABLE_IR_PER_WORK = 0.015625` is 1/4 of
   p02's declared 0.0625. Is there a legitimate kernel below it? More useful:
   the engineer reports `work_per_call` is still unbounded and a 16× shrink
   passes with a shout. **Confirm that shrink passes**, and judge whether the
   shout is discoverable in a real run's output or lost among the others.

## Then the standard checklist

`PROTOCOL.md`'s reviewer checklist. Emphasis:

- **Re-run both gates on complete runs** and confirm the recorded source hashes
  match the tree. Do not trust `results/gate/*.json`.
- **Independently re-derive two of the five p01 digests** the engineer
  re-measured, and say which convention each is.
- **Spot-check the `measure.py p01` re-run**: the claim is that all 42
  `kernel_exclusive_ir` figures are unchanged while `binary_text_bytes` moved in
  exactly 5 C cells. Verify a couple of each.
- **Check the three p02 overstatement corrections landed accurately** — in
  particular that R3 is now stated as +8 at `len ≡ 0 (mod 8)` consistently
  across `README.md`, `NOTES.md` §3 and §3b, and that the sweep is described as
  two runs of 34 rather than "72".
- **Confirm no measured behaviour changed**: R4≡R5 identity on p02, obligation
  counts, checksums. The new stages must not have perturbed the thing they judge.

## Two the engineer reported and did not fix

Judge whether either invalidates anything published:

- `p02/NOTES.md` §3c's "with `memcpy`" row does not reproduce: 9200.3 / 10204.3
  published against 9200.74 / 10204.74 measured on the gate's own `c-gcc-h` /
  `c-clang-h` cells, `-O3 isolated`, `large`. 44 instructions over a 100-call
  probe — a build difference, not noise. Is the table's *conclusion* affected?
- `results/p02-buffer-copy.json` still records a commit four back.
  `measure.py p02` was deliberately not re-run because it would move numbers
  quoted in three `NOTES.md` tables. Say whether it must be re-run before p16,
  and what specifically is at risk if it is not.

## Finally

`.tasks/TASK_007.md` (p16, the TLV walker) is queued next and clones this
template. **One scoped question:** does anything you found here change what p16
should do — in particular, p16's entire security argument is the trusted
accessor's `requires`, so stage 5c-req and the parameter-coverage rule are
load-bearing for it in a way they are not for p02. Are they good enough to carry
that weight? Short answer, from evidence.

## Output

`PROTOCOL.md` report format, severity-ranked, file:line, concrete failure
scenario. **You report; you do not fix.** State every attack that did *not*
land — a clean negative is worth as much as a finding and I will not re-run it.

## Constraints

No root; no `/tmp` (use `.temp/review008/`); **no `git add`/`git commit`**; do
not edit `pilot/`, `patterns/` or `harness/`. Mutate copies under `.temp/`.
Note that running the gate on a mirror writes a record into the tracked
`results/gate/` — move it out and say so, as the last engineer did.
