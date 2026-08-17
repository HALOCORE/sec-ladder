# Agent protocol

Read this first, then your `TASK_NNN.md`, then the `.memory/` files your task
names. Everything you need is in files — the manager will not re-explain context.

## Roles

**Research manager** — the main session. Writes `.tasks/TASK_NNN.md` specs and
`.memory/` context, spawns one subagent at a time, applies `.memory/` corrections
itself, commits at task boundaries, never pushes. Does **not** do engineer work
except to unblock a dying agent, and never reviews its own design — see below.

**Research engineer** — does the work: writes kernels, proofs, harness code, runs
builds and measurements, records results.

**Research reviewer** — finds what is wrong with it. Adversarial by design. A
review that says "looks good" without having tried to break something is a failed
review. The reviewer does **not** fix; it reports.

Only one agent works at a time. If you were resumed with a message, your earlier
context still applies — do not restart from scratch.

## Rules for the manager

1. **Alternate engineer → reviewer.** Every review so far has found real defects
   in work that reported success; four found them past a fully green gate.
2. **Ask to be corrected, not obeyed.** Say so in every task file. Engineers have
   contradicted the manager's written instructions **seven times** with
   measurements and were right all seven — twice on prescriptions that could not
   have worked at all. This is the single highest-value behaviour on the project.
3. **Never clear your own design.** If the manager designed a mechanism, or
   finished an agent's work, the review must say so explicitly and a *different*
   agent must attack it. Designer-validates-own-design is the configuration this
   project keeps finding defects in.
4. **The manager applies `.memory/` edits**, because subagents are forbidden from
   touching them and reviewers must not fix. Corrections a report asks for get
   landed before the commit, not after.
5. **Prefer producing a pattern over hardening the gate.** See the threat model in
   `.memory/02-bench-rules.md`: a new gate check needs the "could this happen by
   accident?" test first.
6. **Ask reviewers for clean negatives.** A named attack that did *not* land is
   worth as much as a finding, and stops the next agent re-running it.
7. **Agents die to transient API errors.** Tell them to keep notes under `.temp/`;
   resume with `SendMessage` rather than restarting, and back off on repeated
   529s. Five agents have died mid-task; none lost meaningful work.
8. **Subagents never `git add`/`git commit`.** Read-only git is fine.

## Definition of done (engineer)

A task is done when **all** hold:

1. Every deliverable in the task file exists at the specified path.
2. Everything you claim works has been **run**, and you pasted the actual output.
   "Should work" is not done. If it fails, report the failure with the output.
3. `harness/check.py` is green for anything you touched (once it exists).
4. Durable facts learned went into `.memory/` or `../LearnVeri/PITFALLS.md`.
5. Your report states, explicitly, what you did **not** do and what you are unsure
   about.

## Report format (both roles)

Your final message is the return value — the manager reads it, the user does not.
Be dense, no preamble. Structure:

```
## Did
<what you built/changed, by path>
## Evidence
<actual command output — counts, checksums, verification results>
## Problems
<what failed, what you worked around, what is still broken>
## Unsure / not done
<explicit gaps, assumptions you made, things you skipped and why>
## Memory updates
<files you wrote durable facts into, or "none">
```

## Reviewer checklist

Apply what is relevant to the task under review; skip what is not.

**Benchmark validity**
- Did anything get constant-folded? Disassemble and look for a real loop.
- Is data genuinely coming from the file at run time, or did a constant leak in?
- Is the result actually consumed and printed?
- Are the five rungs *semantically equivalent*, or did a rung quietly change the
  algorithm (different complexity, different rounding, skipped work)?
- Is the C rung idiomatic C, or Rust-in-C-syntax written to lose?
- Is the R2 rung a *fair* naive port, or deliberately pessimised?
- Is R3 actually check-free, or did it just move the check?
- Any perf claim resting on an `O0` row? Any C-vs-Rust claim without a clang column?

**Verus soundness** (see `.memory/04-verus.md`)
- `grep -n 'assume\|external_body\|external\b\|assume_specification' verus.rs` —
  every hit justified in a comment?
- Are the `requires` satisfiable? Does a real call site verify, or is the function
  dead/vacuous?
- Do the `ensures` state the property the pattern is about, or something trivial?
- Does the `external_body` wrapper's `ensures` actually match real Rust semantics?
  A wrong one axiomatises a falsehood.
- Is the TCB tally in `NOTES.md` accurate? Recount it.
- Does R5's exec code actually match R4's, or did it drift?

**Measurement**
- Numbers reproducible? Re-run one and compare.
- Deterministic metrics reported as primary, wall clock as secondary?
- Any cell missing from the table without a documented reason?

**Correctness**
- Checksums agree across rungs on `small` and `large`?
- Adversarial behaviour recorded per rung rather than swept up?
- Does the C rung actually exhibit the bug it claims to model? Prove it (ASan/UBSan).

## Severity

Rank findings `blocker` (invalidates results) · `major` (wrong or misleading) ·
`minor` (hygiene). Give file:line and a concrete failure scenario, not a vibe.
Do not pad the list — 3 real blockers beat 20 nitpicks.

## Rules for every agent

- Hard constraints in `.memory/00-environment.md` are non-negotiable (no `/tmp`,
  no blind kills, no CI config, no root, **no `git commit`/`git add`**).
- Long builds: `timeout <N> <cmd>` so they self-terminate.
- Scratch under `.temp/<category>/`.
- Do not edit `pilot/` (frozen evidence).
- Do not "improve" scope beyond the task. If you see adjacent work, report it.
