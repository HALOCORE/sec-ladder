# TASK_071 — land p22's review: a false headline is shipped inside the contract

**Role:** research engineer (you built p22; this is its corrections task).
**Read first:** `.tasks/PROTOCOL.md`, then **`.tasks/TASK_070_REVIEW_REPORT.md`
in full**, then your own `patterns/p22-hash-probe/NOTES.md`.

**The review ran 54 named attacks and returned 1 blocker, 3 majors, 4 minors.**
Do not re-measure what reproduced.

✅ **Your two §0 answers were UPHELD, both by counting rather than argument.**

- **A0**: 73 exec-loop measures across the tree, 56 spec/proof-fn measures, and
  **exactly one exec-loop measure mentioning a ghost binding — yours.** Every
  candidate was checked individually (p07 `hi - lo`, p06 `decreases b`, p16
  `end - p`, p38 `2*n - k`, p14 `m + 1 - i`, p13 `DST_CAP - d`) and all are
  arithmetic over exec bindings.
- **A1**: the headline is a **finding, not a tautology**. `r3_bounded` differs on
  `adversarial-full.bin` and agrees on the other seven — genuinely a different
  function, so the forbid is legitimate *for that spelling*.
- **A2 and A3 are clean negatives**: the R4 disclosure is complete and reaches
  `README.md:107-114`; the termination argument is real (two reviewer-built
  mutants fail with `decreases not satisfied at end of loop` **at the probe
  loop**), the lemma is sound rather than self-assuming, and the TCB recount of
  **5** matches.

## F1 — BLOCKER. The manager's false premise is shipped, twice inside the pin.

*"THE FIRST TERMINATION PROOF IN THE PROJECT"* ships in **eight places**:
`verus.rs:5,8`, `spec.md:192,532`, `NOTES.md:258`, `README.md:47`,
`controls/mkcontract.py:239,306`, and the catalogue.

**It is false.** There were **72 prior exec-loop termination obligations**,
because **Verus demands a `decreases` on every exec loop by default**.
⚠ **This is the manager's error, written into `TASK_070.md` and copied through.**
✅ **`.memory/06-catalogue.md` is already corrected** — the manager fixed it.

> ⚠ **`spec.md:192` and `:532` are INSIDE `contract_sha256`** (the block spans
> `:182-548` and hashes to the recorded `044f02cd…`), so this **moves the pin**.
> **Edit `controls/mkcontract.py`, re-run it, and re-gate.** Disclose the move
> with the new hash, and ⚠ **note that the `git show HEAD:` check is vacuous
> here and say why** — PROTOCOL's definition-of-done 6 has just been corrected on
> exactly this point.
>
> **Replace it with the claim the review actually established, which is
> better because it is counted:** *p22 carries the tree's only exec-loop measure
> **not expressible in the loop's own exec variables** — `i0 as int + d - u`,
> where `i` wraps and appears nowhere in the measure. One of 73.*
>
> ⚠ **`NOTES.md:157-163` already carries the true statement one paragraph below
> the false one.** That is PROTOCOL rule 9's exact shape, and it is the third
> time on this project that the correct sentence sat directly beneath the
> headline someone shipped. **Say so in the correction.**

## The three majors

**F2 — the `--multiple-errors` probe was never run, on the one pattern whose
result IS a claim about which obligation fires.** `.memory/04-verus.md` §2b
prescribes it; Verus printed *"not all errors may have been reported"* on both
runs and nobody re-ran with the flag.

- **`m3_noempty` actually fails FIRST on the `decreases` at `verus.rs:592`** —
  **your `NOTES.md` undersells your own battery**: the mutant the task asked for
  was already there.
- **`m1_noguard` has a THIRD error**, `nfill <= TABCAP` at `:516`, which is not a
  termination obligation.
- ⚠ **The review's `rev_m14`** (conjunct deleted from exec *and* from the spec
  `run`) **still fails on it — so no shipped mutant shows the conjunct is
  required ONLY for termination.** **Re-run the battery with
  `--multiple-errors`, report the full error list per mutant, and either build
  the mutant that isolates the termination obligation or say plainly that it
  cannot be isolated.**

**F3 — the forbid's stated reason is false of one spelling.** `spec.md:265` /
`NOTES.md:95-99` justify forbidding the bounded loop because it is *"a DIFFERENT
FUNCTION"*. True of `r3_bounded` (bound **instead of** the conjunct — differs on
`adversarial-full.bin`). **False of `r3_bounded_kept`** (bound **plus** conjunct),
which **agrees on all 8 inputs** and is therefore the same function.

> **Admitting it would widen the published in-contract R3 span from width 10.00
> to 167.65 / 1235.96 — 16.8×.** ⚠ **The direction does NOT flatter** (it is
> dearer, so `R3 − R4 = +2.00` is unaffected) — **say that explicitly**, because
> a 16.8× span movement reads like a retraction and is not one.
> **Two honest routes; pick one and argue it**: admit `r3_bounded_kept` and
> republish the span, **or** split the `why` into two reasons so the forbid says
> what it actually excludes. **Do not leave a `why` that is false of a spelling
> the contract forbids.**

**F4 — `check_miri`'s block reason is structurally false for EVERY pattern
here, not just p22.** `check.py:6086-6090` says *"R4 does not return under Miri
either"*; measured, `miri` on the shipped `unsafe.rs` gives `rc=0 UB=False`.
**`.memory/01-ladder.md` puts the bug in R1 only, so `miri.sources` always names
a rung carrying the fix.** ⚠ **This is a gate defect, not a p22 note** — it needs
a per-rung axis on `expected_hang`. **Do NOT fix `harness/` in this task**;
record it in `NOTES.md` with the widened scope and the manager will queue it.

## The four minors

**F5** `_confirm_hang` confirms `c-clang O0` and **never an `-O3` cell** — the one
C11 6.8.5p6 puts at risk. ⚠ **Your proposed strengthening (per distinct *rung*)
is refuted**: it would still pick two `O0` cells and **would have caught nothing
here**. **The right axis is (rung × opt).** Record that; the change is the
manager's to queue.
**F6** `inputs/gen.py:344`'s residue diagnostic uses `stride - 4` — **the exact
regressor your own `sweep_ir.py:84` warns against** — so it prints one residue for
the whole off-residue band.
**F7** `NOTES.md:403`'s clang explanation is **wrong**, and the review
disassembled it: clang's **+5.00/key is `setne`/`setb`/`and`** — it refuses to
short-circuit the `&&` — **not loop restructuring**; gcc's +1.00/key is a second
branch plus a Horner re-association. ✅ **You labelled it a presumption, which is
why this is a minor and not a major** — now replace it with the derivation.
**F8** `verus.rs:608`'s invariant `u - i0 as int <= d` is **not load-bearing** —
deleting it still gives 20/0.

## Also record (not a defect)

⚠ **`NOTES.md` §11c points at a `git show HEAD:` check that CANNOT FIRE.** On a
one-commit pattern it compares the working tree to HEAD, not first-written to
shipped, so on a clean tree it always prints nothing and always looks like it
passed. **PROTOCOL definition-of-done 6 has just been corrected on this point.**
**Rewrite §11c to say the diff is unavailable and that the recorded first hash is
the only evidence** — do not cite a command that cannot fail.

## Done when

Every item corrected in `NOTES.md`, `README.md`, `verus.rs`, `spec.md` **and
`controls/mkcontract.py`** (the generator — `spec.md` is generated);
`check.py p22` green (**`PASS-WITH-BLOCKED-ROWS`, 0 failures**);
`measure.py --check-stale` clean; `mkcontract.py --check` reports up to date.
**Paste actual output.** ⚠ The `contract_sha256` **will** move — disclose it.

## Constraints

No root; no `/tmp` (scratch `.temp/p22c/`; `.temp/p22/` and `.temp/p22rev/` are
readable, not writable); **no `git add`/`git commit`**; do not edit `pilot/`,
`.memory/`, `harness/`, `common/`, or any pattern other than **p22**. ⚠ **p22
builds programs that never return — always `timeout <N>`, never background.**
⚠ **No self-matching `pgrep` wait-loops** — six of them cost you real time last
task and the rule is now `.memory/00-environment.md` constraint 2. Verus only via
`./verus_run.py`. clang `~/tools/llvm/bin/clang`, gcc `/usr/bin/gcc`, valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none but gcc on
PATH. **You are the only agent running.**

**If a prescription here is wrong, say so with the measurement.** ⚠ **Running
count 153** — 151, plus the review refuting the *"per distinct rung"*
strengthening you proposed and the manager repeated (it would have caught
nothing; the axis is rung × opt), and PROTOCOL's own `git show HEAD:` check,
which the manager added this arc and which is **vacuous on a new pattern**.

**What I am least sure of, by name: F3's remedy.** I do not know whether
`r3_bounded_kept` should be admitted — widening a published span 16.8× — or
whether the `why` should simply be split so it stops asserting something false.
**Both are honest; they are not equally informative.** Argue it and choose; the
one thing that cannot stand is a `why` that is false of what it forbids.

---

## Outcome (recorded by the manager at the task boundary)

**Landed** in `050228d`; `.memory/` in `2bd4a03`; RECAP in `a4db0a9`/`8f2b763`.
**21 patterns, all green, all 21 reviewed. 42 records, 0 STALE, 0 failures.**

**Four manager decisions taken across this arc:**

1. **PROTOCOL rule 5 was OVERRIDDEN deliberately** to do batched gate work
   (`TASK_068`) before another pattern. Reason, recorded in RECAP at the time:
   three of the four edits were fixes to **measured** defects rather than
   speculative hardening, and the fourth **unblocked p22**, which could not
   otherwise be built. **The override was right and the review vindicated it** —
   it found 2 blockers in that work, both of which would have hit p22 directly.
2. **`p48` was added to the catalogue as a seventh axis** (initialisation),
   proposed by the manager from source reads and `vstd` greps. ⚠ **Rule 3 is
   flagged against it in the catalogue itself**: the manager both wrote the slate
   and moved it, so **a different agent must attack the proposal before it is
   scheduled.** It is still unattacked.
3. **F4 and F5 (two gate defects) were NOT fixed inline**, on the engineer's
   correct judgement that they need `harness/` edits out of task scope. Queued as
   RECAP "Owed" 19, which makes the pending `check.py` batch **three** items.
4. **The "line as a hint" citation convention, introduced at TASK_066, was
   RETRACTED at TASK_071** after failing inside a single session.

⚠ **PROTOCOL rule 2's running count is 155, arithmetic written out so the next
manager can audit rather than inherit it:** 130 at TASK_065, **+6** (p38's
engineer, including the load-bearing probe-4 mechanism), **+4** (p38's review,
refuting the manager's inverted A5 direction and the *"add `nw` and refit"*
prescription), **+3** (TASK_067 refuting the **review's** blast radius, its
`opaque_off` construction, and `rlen == 1` as an anomaly), **+2** (TASK_068's
engineer on `expected_exit = None` and the overstated guard), **+2**
(TASK_068_REVIEW on the manager's `183` premise and the six-vs-seven citation
list), **+3** (p22's engineer on the hung-cell count, the Verus route, and
*"the careful programmer pays for the bound"*), **+3** (p22's review, including
the `per-distinct-rung` refutation and PROTOCOL's own vacuous `git show HEAD:`
check), **+2** (TASK_071 refuting the **review's** gcc derivation and its
assumption about which spellings the `forbidden` entries exclude).
**Carry 155 forward.**

**The single most useful thing in this block, and it is about the manager, not
the agents.** ⚠ **A false premise written in a task file shipped into a
pattern's HASHED CONTRACT.** *"The first termination proof in the project"* was
the manager's sentence in `TASK_070.md`; the engineer propagated it to eight
places, two inside `contract_sha256`, and it took a review and a re-gate to
remove. **PROTOCOL rule 9 protects `.memory/` from unreviewed findings and
protects nothing from the task file itself** — the engineer has no reason to
doubt a premise the manager states as fact. **State novelty claims as questions
to be measured** (*"is this the first X? count it"*), never as fact. p22's own
`§0` counted 73 measures in one command when finally asked.
