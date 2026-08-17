# TASK_009_REVIEW — review the verified twin, and the parts the manager finished

**Role:** research reviewer
**Read first:** `.tasks/PROTOCOL.md`, then `.tasks/TASK_009.md` (the spec),
`.tasks/TASK_009_REPORT.md` (**read its closing caveat first**),
`.temp/p009/NOTES.md` (the engineer's own durable notes — the primary record),
then `.memory/04-verus.md` and `.memory/02-bench-rules.md`.

**Two reasons to be more suspicious than usual.**

1. The engineer was killed by transient API errors four times and **never wrote
   its own report**. `TASK_009_REPORT.md` was assembled by the manager from the
   engineer's notes. Its "Delivered" section is an unreviewed claim whose author
   never got to state its own caveats.
2. **The manager finished Part B's self-check (b9) itself and wrote the
   `.memory/` entry for it.** Nobody has independently checked the mechanism the
   manager designed, using a test the manager also designed. That is exactly the
   configuration this project keeps finding defects in.

## What changed

`harness/check.py` (+832 lines), `harness/vparse.py` (+428), `harness/measure.py`,
`patterns/p0{1,2}/{verus.rs,spec.md,NOTES.md}`, and `chmod +x` on five harness
files. New gate stage **5c-twin**. Obligation counts p02 9 → 12, p01 7 → 8.

## Attacks worth trying first

1. **Break the twin mechanism.** The claim is that a trusted `requires` too weak
   to license the real operation is too weak to license a *checked*
   implementation of the same contract. The load-bearing check is not the twin
   verifying — it is the twin **failing when the trusted precondition is
   deleted**. Two toothless-twin attacks are already caught (empty body on a
   no-`ensures` item; `loop { }` under
   `#[verifier::exec_allows_no_decreases_clause]`). **Find a third.** Ideas worth
   trying: a twin whose body uses the precondition for something *other* than the
   operation (so the deletion test fires but the operation is unchecked); a twin
   that indexes a *different* slice; recursion; `#[verifier::truncate]` or other
   attributes that relax a check; a twin whose `ensures` is satisfied through a
   spec function that is itself vacuous.
2. **Can the signature comparison be satisfied while the twin's obligation is
   weaker?** `check.py:2155` compares `vparse.norm_clause(twin.sig)` to the
   trusted item's. Attack `norm_clause` itself: whitespace, comments, `&&` vs
   comma, clause *order*, a `where` clause, a differently-named parameter bound
   to the same position, `int` vs `nat` vs `usize`. If two different obligations
   normalise equal, the mechanism's foundation is gone.
3. **Does 5c-twin have an off switch?** It is skipped under
   `--no-verus-mutants` (which `rep.fail`s — check that it really does). Look for
   any other route: a pattern with no `verus.obligations`, a trusted item whose
   body's `unsafe` is spelled so `_UNSAFE_RE` misses it (macro, `unsafe` inside a
   nested fn, `r#unsafe`), `verus.twin_justifications` (is the shout loud, and is
   there a cap on how many items may be justified away?).
4. **Part C/D's probe.** The tactic battery now escalates to `by (bit_vector)`.
   Does that create *false* tautology reports — a clause that `bit_vector`
   "proves" but that genuinely constrains callers? A false tautology is a hard
   failure on an honest pattern, which is how a stage gets switched off.
5. **The C rung and Part H.** The manager asked whether the decoy-region trick
   works against the **C** rung and the agent died before answering. **Answer
   it** — it decides whether the H fix is one mechanism or two. Then say what a
   fix must pin: the region has to be tied to the code the benchmark executes,
   and "executed" needs an operational definition the gate can check.

## Then the standard checklist

- **Re-run both gates on complete runs.** The manager's runs are in
  `.temp/mgr-gate-p0{1,2}.log`; do not trust them, and verify source hashes.
- **Re-verify the zero-instruction claim independently** — p02 R4≡R5 at O3 should
  be `md5_fn 0e5b59364bb6`, i.e. bit-identical to before TASK_009. If the twins
  perturbed exec code, established result 1 is affected and that is a blocker.
- **Recount both patterns' TCB.** The twins are new items; confirm they are *not*
  counted as TCB (they are verified, not trusted) and that `NOTES.md` says so.
- **Check the obligation-count moves are honest**: p02 9 → 12 and p01 7 → 8.
  Per `.memory/04-verus.md` the count is one query per function plus one per loop
  body — do the deltas match the twins actually added, or did something else move?
- **Verify the p01/p02 `verus.rs` and `spec.md` edits** did not weaken anything
  while adding twins.

## Finally

`.tasks/TASK_007.md` (p16) is next and was blocked on this task. **Is the strength
problem now closed well enough for a pattern whose entire security argument is
the accessor's `requires`?** Short answer from evidence, and name the residual a
human must still read.

## Output

`PROTOCOL.md` report format, severity-ranked, file:line, concrete failure
scenario. **State every attack that did not land** — clean negatives will not be
re-run. You report; you do not fix.

## Constraints

No root; no `/tmp` (use `.temp/review009/`); **no `git add`/`git commit`**; do not
edit `pilot/`, `patterns/` or `harness/`. Mutate copies under `.temp/` —
`.temp/p009/mkmirror.sh <tag>` builds a repo-layout mirror and prints its path.
**Running the gate on a mirror writes a record into the tracked `results/gate/`**
— move it out and say so; the manager committed two by accident this task and had
to amend.

Save findings to `.temp/review009/NOTES.md` as you go: four agents in a row died
to transient API errors, and notes make a resume cheap.
