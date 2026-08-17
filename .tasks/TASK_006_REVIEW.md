# TASK_006_REVIEW — review of the p02 remediation, the new gate stage, and the floor

**Role:** research reviewer
**Read first:** `.tasks/PROTOCOL.md`, then `.tasks/TASK_006.md` (the spec under
review), then `.memory/02-bench-rules.md` and `.memory/04-verus.md` (the manager
corrected both during TASK_006 — they are authoritative and supersede any task
report).

The engineer reported both gates green on complete runs. **Six reviews have now
found real defects in work that reported success, twice in work certified by a
fully green gate.** Assume the same here until you have tried to break it.

## What changed (the surface under review)

- `patterns/p02-buffer-copy/NOTES.md` + `README.md` — perf claim retracted and
  restated as codegen fragility; variant table; swept residue curve.
- `patterns/p02-buffer-copy/gen.py` — residue pinning extended to mod 16, `--sweep`.
- `harness/dloop.py` — `_GHOST_RE` gated on the `verus!` span, not on `lang`.
- `harness/check.py` — new clause-deletion stage (5c) + `assert(false)` probe.
- `harness/check.py` (floor stage) + `spec.md` — `min_ir_per_work` declarable.
- `harness/asm.py` — `is_bulk_symbol` recognises `__*_chk` and the ifunc variants.
- `patterns/p02-buffer-copy/verus.rs` — `copy_bytes`'s `ensures` reworked.

## Attacks worth trying first

These are the ones I expect to land. Do not stop at them.

1. **Conjunction defeats clause deletion.** Stage 5c deletes whole `ensures`
   clauses. If a redundant clause is merged into a neighbour — `ensures a == b &&
   old_len == new_len` — deleting the *clause* removes the load-bearing conjunct
   too, so the file fails to verify and the stage reports healthy. The redundancy
   is unchanged; the check has been satisfied by reformatting. **Check whether the
   engineer's fix to `copy_bytes` did exactly this.** If so, the stage rewards the
   wrong edit. Try splitting at `&&` and deleting conjuncts.
2. **`min_ir_per_work` is a declared pin again.** The self-certification argument
   from TASK_003_REVIEW applies verbatim: the pattern author writes the number the
   pattern is judged against. Try declaring a floor low enough to pass with the
   kernel body deleted down to the fold, or `0.0`, and see whether anything
   objects. Is `min_ir_per_work_why` inspected by anything, or is it a comment
   field? Is there an upper bound on what may be declared?
3. **The `verus!` span is now a safe harbour.** `_GHOST_RE` still strips inside
   `verus! {}`. R5 is Rust; a `verus!` block contains **live** Rust as well as
   ghost. Specifically test, inside the span: `assert!(...)` (bang — live in
   release), `let ghost = <expr>;` (a binding *named* ghost, not `let ghost x`),
   and anything with an `unsafe` block. Measure marginal `Ir`. If a payload
   survives with the statement count unchanged, the M9 hole moved rather than
   closed.
4. **Does 5c cover `requires`?** TASK_005 made an empty `requires` on an
   `unsafe`-containing `external_body` a hard failure, but a *weak* one is the
   real risk. Deleting a `requires` should make the file verify *more* easily —
   the deletion test for `requires` has to be the mirror image (delete it and
   check that some call site now fails). Was that implemented, or does 5c only
   handle `ensures`?
5. **Did the `is_bulk_symbol` widening create false negatives?** It now matches
   more names. Confirm nothing that is legitimately part of the kernel is now
   classified as a bulk call, and that the selftest cases were actually added and
   run.

## Then the standard checklist

Apply `PROTOCOL.md`'s reviewer checklist. Emphasis for this task:

- **Re-run both gates yourself** on complete runs. Do not trust
  `results/gate/*.json`; check `complete_run` and that the recorded source
  hashes match the working tree.
- **Reproduce one number from the variant table** in `TASK_006.md:27-31`
  independently. If the retraction rests on those four rows, one of them should
  be reproducible by you from the shipped sources.
- **Re-derive the residue curve at three points of your own choosing**, including
  one the sweep did not sample. The claim is amplitude ~179 Ir resetting at
  `len ≡ 1 (mod 16)` on a 0.21 Ir/byte linear term. A sawtooth fitted to a sweep
  is easy to over-read; check it predicts.
- **Recount p02's TCB** from `verus.rs` as it now stands.
- **Confirm R5's kernel is still byte-identical to R4's** after the `copy_bytes`
  rework (`md5_raw` on the `nm --print-size` extent). The rework touched the
  proof; if it moved exec code, established result #1 is affected.

## Two follow-ups the engineer flagged and did not do

Verify whether they are still open, and whether either invalidates anything
published:

- `patterns/p01-array-sum/NOTES.md:137` publishes a stale digest (`f8e1fe32…`;
  claimed actual `12d307f2b9d1` since the barrier swap).
- `measure.py` / `report.py` were not re-run since the barrier swap. The argument
  that the numbers stand is "the kernels are byte-identical". **Test that
  argument** rather than accepting it: are the published p01 numbers reproducible
  today, and is the `work/call` label correct after the `describe()` change?

## Finally — is the template ready to clone?

Wave 1's remaining patterns (p16 TLV walker, p17 HTTP `Range` parser) will be
built by cloning `patterns/p01-array-sum/`. One scoped question, answered from
evidence, not opinion: **what in the current template will not survive a pattern
whose kernel is a parser** — variable work per call, early exit on malformed
input, a result that is a struct rather than a `u64`, input that is bytes rather
than records? Name the harness assumptions that will break, with file:line. This
is the only forward-looking item; keep it short.

## Output

`PROTOCOL.md` report format. Severity-ranked, file:line, concrete failure
scenario. **You report; you do not fix.** If an attack above does not land, say
so explicitly — a negative result on a named attack is worth as much as a
finding, and I will not re-run it.

## Constraints

No root; no `/tmp` (use `.temp/review006/`); **no `git add`/`git commit`**; do not
edit `pilot/`. You may write scratch variants under `.temp/` and run builds. Do
not modify anything under `patterns/` or `harness/` — if you need a mutated
source to demonstrate a bypass, copy it to `.temp/` or restore it afterwards and
say so.
