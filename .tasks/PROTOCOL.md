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
2. **Ask to be corrected, not obeyed.** Say so in every task file, and **name the
   call you are least sure of, by name, and ask for the measurement.** Every
   agent that has contradicted the manager's written instructions with a
   measurement has been right — twice on prescriptions that could not have worked
   at all, once on three separate premises in one task. This is the single
   highest-value behaviour on the project.
   ⚠ **The running count lives in ONE place: the closing paragraph of the newest
   `.tasks/TASK_NNN*.md`.** Increment it there when you write the next task file
   and nowhere else. It used to be duplicated here and in `RECAP.md`, where both
   copies went stale and disagreed with the task files by 48 and 42.
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
9. **Do not write a finding into `.memory/` before its review lands.** This is a
   measured process defect, not advice: **four consecutive reviews (p16, p17
   ×2, p05) found the manager's `.memory/` write-up overclaiming**, every time
   from the same cause — the manager wrote the finding from the engineer's report
   without re-measuring, and the engineer's own `NOTES.md` sometimes contained the
   correction one paragraph below the headline the manager copied.

   The ordering that fixes it, at no cost:

   - the **engineer** writes measured claims into the pattern's `NOTES.md` — they
     ran the experiment, and the gate certifies the tree;
   - the **manager** commits that as-is, *without* adding a `.memory/` finding;
   - the **reviewer** attacks the claim;
   - **only then** does the manager write `.memory/`, from the reviewed text.

   `.memory/` is the layer that outlives every task and is described as
   authoritative. A number that has not survived a review does not belong in it.
   If a finding must be recorded before review, mark it **PROVISIONAL — not yet
   reviewed** in the text itself.
10. **Write the report file BEFORE citing it.** A subagent's report exists only in
    its return message; if the manager lands the corrections and moves on, the
    `.tasks/TASK_NNN_REVIEW_REPORT.md` everything now points at was never created.
    This happened at TASK_027_REVIEW — three dangling citations, two of them in
    `.memory/`, the layer this project calls authoritative — and it was found by
    the next engineer, not by the manager. The check is one command and costs
    nothing:

    ```bash
    grep -rho '\.tasks/TASK_[A-Za-z0-9_]*\.md' .memory/ .tasks/ RECAP.md \
      | sort -u | while read p; do [ -e "$p" ] || echo "MISSING: $p"; done
    ```

    Run it before every commit that cites a report. (`TASK_NNN.md` in this file is
    a placeholder and will always show up; ignore that one.)
11. **Never `git add -A` while a subagent is working.** Stage explicit paths.
    The manager did it at `e9d4271` and swept **23 files of an in-progress
    pattern** into a commit whose message is about something else entirely — so
    p10 has no commit message describing p10, and the history says a catalogue
    edit created a pattern. Nothing was lost and the tree is green, but the
    record is wrong and **it is not fixable by rewriting**: `97286d2` registers
    p10's predictions and must keep *preceding* the measurement commit for that
    registration to mean anything. Correct in a following commit, the way
    `bb36e2f`'s message error was corrected. `git add <path> …`, always.
12. **Ask the review for the mechanism, not just the number.** p05's review was
   asked "if five rungs emit identical mnemonics, where did the bounds check go?"
   and came back with the hoisted trip-count computation, the surviving scalar
   epilogue, the `cmove` that forces a zero remainder to a full vector width, and
   a zero-parameter derivation of a model the delivery had fitted. "It vanished"
   is not a mechanism, and a finding without one is the finding a reader
   disbelieves.

## Definition of done (engineer)

A task is done when **all** hold:

1. Every deliverable in the task file exists at the specified path.
2. Everything you claim works has been **run**, and you pasted the actual output.
   "Should work" is not done. If it fails, report the failure with the output.
3. `harness/check.py` is green for anything you touched (once it exists).
4. Durable facts learned went into `.memory/` or `../LearnVeri/PITFALLS.md`.
5. Your report states, explicitly, what you did **not** do and what you are unsure
   about.
6. **Record the `slb-contract` block's sha256 in `NOTES.md` the moment you first
   write it, before building any cell.** One line: the hash, and "as first
   written, before any measurement".

   This exists because a pattern lands in **one commit**, so "no `required` or
   `forbidden` entry moved after I measured" is **not independently checkable** —
   a reviewer has no pre-edit snapshot to diff against (TASK_051_REVIEW, on p18,
   where the engineer disclosed a `why` correction honestly and the reviewer
   still could not verify the scope of it). The recorded hash is the snapshot,
   and it costs one line.

   ⚠ **AND VERIFY YOUR OWN DISCLOSURE AGAINST `git`, because a FALSE disclosure
   is worse than the stale thing it describes.** p47 shipped a table saying a
   pinned note *had been changed* when `git show HEAD:` proves it had not
   (TASK_064_REVIEW M3). **A disclosure is what a reviewer trusts INSTEAD of
   re-checking**, so a wrong one removes the check it was meant to enable. The
   test costs one command:

   ```bash
   git show HEAD:patterns/pNN-name/spec.md | diff - patterns/pNN-name/spec.md
   ```

   ⚠ **THAT COMMAND IS VACUOUS ON A NEW PATTERN, and this instruction said so
   nowhere until TASK_070_REVIEW.** It compares the **working tree to HEAD** —
   not *first written* to *shipped*. A pattern lands in **one commit**, so on a
   clean tree it always prints nothing and **always looks like it passed**. p22
   ran it, got silence, and its `1f29b02e… → 044f02cd…` disclosure **still has no
   artefact behind it.**

   - **New pattern** → the command proves nothing. **The recorded first hash is
     the ONLY evidence** — which is exactly why rule 6 opens by demanding you
     write it down *before building any cell*. Say in `NOTES.md` that the diff is
     unavailable and why, rather than citing a command that cannot fire.
   - **Existing pattern** → the command is real; use `git show <commit>:` for the
     commit the pattern landed in, not `HEAD`, once anything else has touched it.

   ⚠ **The same applies to the ARTEFACT-vs-GENERATOR skew**: if a `spec.md` is
   generated, fix the generator too and re-run it. Three tasks in a row shipped
   an edit the generator would have silently reverted
   (`.memory/05-layout.md`), and one of them was the task fixing that defect.

   ⚠⚠ **RULE 6 HAS A HOLE, AND `p46` IS THE FIRST PATTERN TO DEMONSTRATE IT
   WITH A MATCHING HASH (TASK_089_REVIEW).** This rule protects against a
   declaration **edited AFTER measuring**. It does **NOTHING** about a
   declaration that **measurement has since FALSIFIED**.

   p46's Rule 6 disclosure verified *perfectly* — the reviewer reconstructed the
   recorded pre-build sha256 **exactly**, proving no `required` / `forbidden` /
   `identity` / `why` had moved. **And that is precisely WHY the hashed `why`
   still asserted `"NEITHER SIDE IS DEGENERATE"` with two numbers that appear
   nowhere in the pattern's own `NOTES.md`**, plus three rung sources quoting
   retracted pre-build figures — one of them citing, as its authority, the very
   section that retracts it.

   **So Rule 6 is necessary and not sufficient. Add this step, and it costs one
   `grep`:**

   > **Before you finish, re-read the hashed `why` and every rung-source doc
   > comment AGAINST YOUR OWN MEASURED NUMBERS.** A frozen declaration is
   > evidence about *when* it was written, **not about whether it is still
   > true.** Anything the build refuted must be struck **even though — indeed
   > especially because — the hash still matches.**

   ⚠ **Budget it:** `spec.md`'s fenced block is contract-hashed, so a `why` fix
   moves `contract_sha256`; `c/kernel.{c,h}` are **measurement**-hashed, so even
   a comment fix there costs a re-measure. **Doc comments in `.rs` rung sources
   and `NOTES.md`/`README.md` cost only a gate re-run.**

   **If the hash changes later, say so and say why** — a declaration edit made
   after a measurement is exactly what the direction test governs
   (`.memory/01-ladder.md`), and disclosing one has twice been upheld on review.
   Editing the declaration is not the problem; an unverifiable claim about it is.

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
