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
   ⚠⚠ **AND THE LOOP HAS A FOURTH STEP THAT WAS MISSING FROM IT UNTIL TASK_100:
   build → review → land corrections → WRITE THE FINDING.** `p19` and `p46` — the
   23rd and 24th patterns, both gate-green, both reviewed, both corrected — were
   absent from `RECAP.md`'s findings section for **45 and 35 tasks**, while the
   START HERE box counted them as done. **Nothing in the loop pointed at the
   gap**: the gate was green, `.memory/` had rows, the reports existed, and the
   one artefact a reader actually reads had no entry. ⚠ **A pattern is finished
   when a reader can find its result, not when its gate is green.** The check is
   one loop, and ⚠ **the obvious spelling of it is WRONG** — `ls -d patterns/p*/
   | grep -o 'p[0-9]*'` also matches the `p` in `patterns/`, so it reports every
   pattern missing and reads as a catastrophe. Use `basename`:

   ⚠⚠⚠ **AND THE CHECK AS FIRST WRITTEN GIVES A FALSE PASS. FOUND AT
   `TASK_155` M6, ON `p34`, BY THE REVIEWER — AND THE MANAGER HAD RUN IT, SEEN
   SILENCE, AND MOVED ON THE SAME SESSION.** The struck spelling greps the
   **whole findings section** for a mention, and a pattern is mentioned there
   long before it is built: `p34` appeared **six** times in pre-build catalogue
   findings, so the loop stayed silent while `p34` had no finding, was absent
   from `results/synthesis.md`, and `RECAP.md`'s own box still said its build
   task did not exist. ⚠ **A MENTION IS NOT AN ANCHOR.** ✅ **The repair is to
   grep only the finding HEADERS** — the numbered lines, which is where a row's
   own result is announced:

   ```sh
   awk '/^## The findings so far/,/^## Retracted/' RECAP.md \
     | grep -E '^[0-9]+\. ' > .temp/h.$$
   for d in patterns/p*/; do id=$(basename "$d" | cut -d- -f1)
     grep -q "\b$id\b" .temp/h.$$ || echo "MISSING: $id"; done; rm -f .temp/h.$$
   ```

   ✅ **Manager-verified: on a tree where the old form printed NOTHING, this one
   prints `p34` (correct — it had no finding) and `p01` (correct and benign —
   the calibration row models no bug and announces no result).** ⚠ **One known
   benign exception is what a working check looks like; silence is what a broken
   one looks like.** ⚠ **`.temp/`, not `/tmp` — constraint 1, and the manager
   broke it writing this very check.**
   ⚠⚠ **THE GENERAL LESSON, AND IT IS THE THIRD TIME THIS PROJECT HAS PAID IT:
   *before believing a check, ask what would make it FAIL.* Here nothing would
   have, for any pattern the catalogue had ever discussed.**
   ⚠⚠ **THE RUNNING COUNT BREAKS UNDER CONCURRENCY, AND IT BROKE AT TASK_099.**
   Rule 2 puts the count in **one** place — the newest task file's closing
   paragraph. **Three agents running at once means three task files, each written
   before the others reported**, so `TASK_100` pre-committed **301** while
   `TASK_099` was independently carrying 299 → **307**, and the two cannot both
   be the newest. ⚠ **The count is a rigour signal, not a ledger, so do not
   reconstruct it by addition across concurrent branches — that double-counts a
   manager claim refuted by two agents.** **The rule under concurrency:** every
   concurrent task file states the count **it was launched from** and says so
   explicitly; **the manager reconciles once, at the commit that lands them, and
   writes the reconciled figure into the next task file it launches.** ⚠ **Say in
   each concurrent task file that reconciliation is the manager's job and not the
   agent's** — otherwise two agents each try to carry a number forward and
   neither is right.
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

   ⚠⚠ **THE MANAGER TOOK A DELIBERATE EXCEPTION TO THIS AT TASK_099 AND IT WENT
   WRONG — AND THE FAILURE IS FINER AND MORE USEFUL THAN "RULE 9 WAS BROKEN".**
   The argument for the exception was reasonable: an engineer had returned a
   blocker showing a `.memory/` sentence was false, and **leaving a known-false
   claim in the authoritative layer seemed worse than landing a PROVISIONAL
   correction.** `TASK_103` then showed **the struck sentence was TRUE and the
   replacement was FALSE.**

   **The actual defect was not the timing. It was that the finding had TWO PARTS
   and the manager landed them as ONE:**

   - a **conclusion** — *"re-run the gate and compare is not a reproduction
     test"* — which was **true, important, and independent of the mechanism**; and
   - a **mechanism** — *"the launching method selects the phase"* — which was
     **false**, and which ⚠ **the engineer's own report had explicitly declined
     to name** (*"I am deliberately not naming one"*).

   ⚠⚠ **The manager's write-up named a mechanism the engineer had refused to
   name, and did it in a STRIKETHROUGH, which reads as settled rather than
   open.** That is rule 9's original cause exactly — *writing the finding from
   the report rather than from the measurement* — **except sharper, because the
   manager made the claim STRONGER than the engineer had.**

   **So the rule, refined:** when a result has a conclusion and a mechanism,
   ⚠ **they have different evidence and they need different treatment. Land the
   conclusion if it stands on its own; mark the mechanism OPEN.** **Never
   strike an existing `.memory/` sentence on the strength of an unreviewed
   mechanism** — a strikethrough is an assertion that the matter is closed, and
   it is much harder to un-strike than to annotate. ⚠ **If you must record a
   contradiction pre-review, ANNOTATE the sentence as DISPUTED and name the
   evidence on both sides. Do not delete, and do not replace.**

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

    ⚠⚠ **AND DO NOT "IMPROVE" THIS CHECK INTO A SCAN FOR TASK FILES WITH NO
    `_REPORT.md` — THE MANAGER DID THAT AT `TASK_163` AND GOT 73 FALSE ALARMS.**
    Early tasks pair `TASK_NNN.md` with **`TASK_NNN_REVIEW_REPORT.md`**, and
    many produced no separate report file at all: there are **204** task files
    against **135** reports, and that gap is history, not debt. ✅ **The check
    above is the right one because it starts from what is CITED rather than from
    a naming convention** — a citation that dangles is a real defect; a report
    that was never written is not.
11. **Never `git add -A` while a subagent is working.** Stage explicit paths.
    The manager did it at `e9d4271` and swept **23 files of an in-progress
    pattern** into a commit whose message is about something else entirely — so
    p10 has no commit message describing p10, and the history says a catalogue
    edit created a pattern. Nothing was lost and the tree is green, but the
    record is wrong and **it is not fixable by rewriting**: `97286d2` registers
    p10's predictions and must keep *preceding* the measurement commit for that
    registration to mean anything. Correct in a following commit, the way
    `bb36e2f`'s message error was corrected. `git add <path> …`, always.

    ⚠⚠⚠ **AND THE RULE AS WRITTEN ABOVE IS TOO NARROW. IT HAS BEEN COMPLIED
    WITH TO THE LETTER AND VIOLATED IN SUBSTANCE TWICE, ONE REVIEW APART.**
    ✅ **WIDENED: while a subagent runs, do not EDIT — and do not COMMIT — any
    file that subagent READS or WRITES.** That includes `RECAP.md`, `.memory/`,
    the baseline JSONs, and **the subagent's own report**.
    ⚠ **Committing is not a read-only act**: it fixes a moving file at an
    arbitrary point and publishes it as the record. At `TASK_149` the manager
    committed a report at **970 lines** that finished at **1025**, and edited
    `RECAP.md`, `temp_citations_baseline.json` and the next task file underneath
    the same running reviewer. **The reviewer reported all of it.**

    ⚠⚠ **THE PROXIMATE CAUSE IS ABOUT THIS HARNESS AND IS WORTH KNOWING: A
    COMPLETION NOTIFICATION MEANS THE AGENT STOPPED, NOT THAT IT IS FINISHED.**
    An agent that spawned a background child — a long `check.py`, say — notifies
    when it stops, then **RESUMES when the child exits**, and the same task id
    notifies again. `TASK_149` did exactly that: it resumed after a **33-minute**
    gate run, added 92 lines, corrected its own running count and recorded a new
    finding. **Before treating a report as final, confirm the agent has no
    running child** (`ps` on the exact PID it named, or `ListAgents`).
    ⚠ **The manager DID wait on that PID before launching the next task, so the
    pattern files were never contended — the wait covered the artefact the next
    task would WRITE and not the one it would READ.**

    ⚠ **AND DO NOT FIX A FINDING OUT FROM UNDER A RUNNING REVIEW.** The same
    session's citation-baseline repair was correct in substance and wrongly
    timed: the reviewer had to withdraw a live finding and keep only its
    mechanism. **Collect while a review runs; fix after it reports.**
    ✅ **If an edit does land underneath a running agent, TELL THE AGENT**
    (`SendMessage`) — cheap insurance against it working from a stale input.
12. **Ask the review for the mechanism, not just the number.** p05's review was
   asked "if five rungs emit identical mnemonics, where did the bounds check go?"
   and came back with the hoisted trip-count computation, the surviving scalar
   epilogue, the `cmove` that forces a zero remainder to a full vector width, and
   a zero-parameter derivation of a model the delivery had fitted. "It vanished"
   is not a mechanism, and a finding without one is the finding a reader
   disbelieves.

13. ⚠⚠ **IN A LONG DOC ITEM, ONLY THE BODY GETS MAINTAINED — THE HEADER ROTS.**
    ⚠⚠⚠ **AND AT `TASK_171` IT ESCAPED THE BACKLOG INTO A PUBLISHED DOCUMENT
    FOR THE FIRST TIME.** The manager retired `RECAP`'s queue item 11 into
    `results/SYNTHESIS.md` as a priced limitation — *"no pattern ships a
    length-heterogeneous sweep band"* — **by copying the queue header. Four
    patterns ship one, `p06`'s input generator cites that very item as its
    motive and hard-asserts the opposite in its own selfcheck, and `RECAP` had
    ALREADY retired the item in a FINDING while the QUEUE entry still said *"no
    pattern has one"*.** ⚠⚠ **So the project published a LIMITATION THAT DOES
    NOT EXIST — the mirror image of publishing a result that does not, and just
    as damaging, because a reader treats a stated limitation as measured.**
    ✅ **THE RULE: before retiring a backlog item into a published document,
    CHECK THE ITEM AGAINST THE TREE, not against its own header.** ⚠ **One
    `ls patterns/*/inputs/ | grep sweep-h` would have caught it.**


    Found twice in one pass over `RECAP.md`'s owed queue, and the second case is
    the sharp one. **Item 27's header read *"the authoritative layer cites 34
    `.temp/` paths, and NONE of them exists in a fresh clone"* while its own next
    paragraph said all 34 exist and there are ZERO broken citations.** The header
    was not merely stale, it asserted **the opposite of the body underneath it**,
    and anyone skimming the queue by header would have scheduled a fix for a
    problem that did not exist. **Item 12 had the same shape** — *"22 of them
    across 12 patterns"* over a body that already carried the correct
    `p12 / p13 ×3 / p16 ×2 / p38` breakdown (**seven, across four patterns**).
    ⚠ **The mechanism is obvious in hindsight: an update lands where the detail
    is, and the summary line above it is not where anyone is looking.**
    **So: when you correct a doc item, re-read its header and make it match, and
    when you READ one, trust the body over the header.** ⚠ **This is the same
    class as the `check.py:NNNN` citation rot the project already has a rule for
    — a pointer that decays away from the thing it points at — and it deserves
    the same reflex.**
14. ⚠ **Run the premise before you write it into a task file.** Rule 2 asks to be
    corrected *after* the fact; this is the cheaper half. Three manager premises
    were checked against a run before `TASK_100`/`TASK_101` were written, and
    **two of the three changed what got written**: *"no built pattern has a
    multiset obligation"* survived only after two false-alarm `grep` hits were
    chased down (`p07`, `p14`, both comments), and *"valgrind's failure is the
    `LD_PRELOAD` blindness"* was **refuted** — it is genuinely `libc6-dbg`. ⚠ **A
    premise stated as fact in a task file is one an engineer has no reason to
    doubt**, and the *"first termination proof in the project"* sentence shipped
    into eight places, two of them inside `contract_sha256`, exactly that way.
    **Cost of checking: about a minute each. Cost of not checking: a review and a
    re-gate.**

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

   ⚠ **Budget it, and the first version of this note was WRONG — corrected at
   TASK_092, manager-verified:**

   | file | hashed into | a comment-only fix costs |
   |---|---|---|
   | `spec.md` **inside** the fence | contract + gate | **a `contract_sha256` move** |
   | `spec.md` prose, `NOTES.md`, `README.md` | gate | **a gate re-run** |
   | `c/kernel.{c,h}` | **measurement** | **a re-measure** |
   | ⚠ **`safe_naive.rs`, `safe_tuned.rs`, `unsafe.rs`, `verus.rs`** | ⚠ **MEASUREMENT** | ⚠ **a re-measure** |

   ⚠⚠ **THERE IS NO CHEAP DOC FIX IN ANY RUNG SOURCE.** This note previously
   said *"doc comments in `.rs` rung sources … cost only a gate re-run"*, and
   that is **false**: `harness/measure.py::measurement_sources` **globs
   `pdir/*.rs`**, and every rung `.rs` appears in the measurement record's
   `source_sha256`. ✅ **Verified by reading `results/pNN-*.json`.**

   ✅ **The good news, measured twice (p19 and p46): the re-measure is cheap and
   moves nothing you publish.** p19's took **1 m 17 s**; p46's moved **111 of
   1371 leaf values — 102 wall-clock, 6 source hashes, a timestamp and git
   metadata. ZERO `Ir`, zero md5, zero identity, zero checksum.** ⚠ **So batch
   every rung-source doc fix into ONE pass rather than avoiding them** — fixing
   `c/kernel.c` alongside them is then free at the margin.

   ⚠⚠⚠ **AND A GATE-ONLY CHANGE CAN COST THE SAME CHAIN, WHICH IS THE ROW
   NOBODY HAD: `report.py` RENDERS THE `loud` SECTION, so turning a `rep.note`
   into a `rep.shout` STALES EVERY TABLE IT FIRES ON.** `TASK_170` added one
   shout, it fired on **seven** patterns, and stage 9c hard-failed all seven:
   **+7 renders and +7 re-gates for a change that touched only `check.py`.**
   ✅ **The rule: `gate → report → gate` per pattern whose RENDERED output moves
   — and `loud` is rendered.** ⚠ **Smoke-test one pattern before committing a
   tree-wide sweep to it; `TASK_170` did, on `p12`, and the sweep was not
   wasted.**

   ⚠⚠⚠ **AND THE TABLE ABOVE OMITS A COST THAT IS NOT OPTIONAL, FOUND AT
   `TASK_168`: A RE-MEASURE STALES THAT PATTERN'S PUBLISHED TABLE, AND STAGE 9c
   HARD-FAILS ON IT.** `results/tables/pNN.md` cites the measurement record, so
   every re-measured pattern owes **`harness/report.py pNN` plus a SECOND gate
   run** — and a pattern whose `controls_json` also moved owes two.
   `TASK_168` re-measured four patterns and paid **+5 renders and +6 gate runs**
   that this rule's cost table does not mention. ✅ **Budget
   `re-measure → report.py → gate` per pattern, not `re-measure` alone.**

   ⚠⚠ **A PREDICTION LESSON FROM THE SAME TASK, AND IT IS RULE 14's SHAPE ONE
   LEVEL DOWN: PREDICT FROM THE COMMAND'S DEFAULTS, NOT FROM THE RECORD'S
   VALUES.** `TASK_168` predicted its re-measure's deterministic half **exactly**
   — zero `Ir`, checksum, md5, static or input-hash movement on all four
   patterns, and `source_sha256` movers exactly the five edited files — and got
   the wall-clock half wrong, because **two record fields are `argparse`
   arguments** (`reps`, `timing_cpu`): `p12`/`p13` had been taken at
   `--reps 31` and `p16` at `--cpu 5`, and a re-run at the defaults silently
   retired both. ⚠ **A record field that is a command-line argument moves
   whenever the argument does, and the record is exactly where you cannot see
   that.**

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
