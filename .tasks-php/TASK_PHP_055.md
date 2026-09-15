# TASK_PHP_055 — **REVIEW ROUND**: `F96` (decomposed), `F113`, and **five manager claims made while scoping this task**

**Role:** research **reviewer**. **ONE agent, alone.** Nothing else is running.
**Report:** `.tasks-php/TASK_PHP_055_REPORT.md` — **write the FILE** (rule 10).

⭐⭐⭐ **THE PREVIOUS FOUR ROUNDS ALL FOUND THE SAME SHAPE: A CONCLUSION SURVIVED
AND THE REASON GIVEN FOR IT DID NOT** — `_047` (F103's decomposition), `_049`
(item 111's headline), `_050` (my `ph64` two-input defence), `_053` (F113 itself).
F113 draws the moral in terms: ▶ ***review REASONS separately from CONCLUSIONS.***
**This task is built around that.** Every claim below is presented as
**(conclusion, reason)** and **you are asked to verdict each half separately.**

---

## §0 ⛔ READ FIRST, IN THIS ORDER

1. `RECAP_PHP.md` — the **START HERE** box, the **RULE-9 STATE** block (it is the
   index of what may enter `.memory-php/`), **F96**, **F113**, **F112**, **F110**,
   and open items **78 · 80 · 105 · 115 · 117 · 118**.
2. `.tasks-php/PROTOCOL_PHP.md` — **§B5** (family-B publishability), **§C**,
   **§F6a**, **§H**.
3. `.memory-php/` 00–04 — **the authoritative layer, which supersedes any task
   report it contradicts.** In particular `03-numbers.md`'s **five things every
   percentage owes** and the `inside_share` rule.
4. `.tasks/PROTOCOL.md` **rule 9** — nothing reaches `.memory-php/` until it
   survives an **engineer → reviewer** cycle. ⚠⚠ **That distinction is
   load-bearing in this task: a later ENGINEER task supplying a second method is
   NOT the same thing as a REVIEWER verdict, and §1 turns on whether you agree.**
5. `.tasks-php/TASK_PHP_042_REPORT.md` **§3**, and `TASK_PHP_050`/`_053`'s reports
   where they touch `ph53` and `ph56`.

---

## §1 ⭐⭐⭐ `F96`, AND THE CLAIM THAT IT WAS NEVER ONE FINDING

**`F96` has been carried as `UNREVIEWED` for FOUR ROUNDS.** The RULE-9 table
states the ground in these words:

> **F96** — ⛔ **UNREVIEWED, FOURTH ROUND.** ⭐⭐ *And that is now the finding: it
> has **NO cheap second method**.* ▶ *It needs a dedicated task or a permanent
> mark — stop re-scoping it into review rounds.*

⛔⛔ **THE MANAGER NOW BELIEVES THAT GROUND IS WRONG, AND THIS SECTION IS THE
CLAIM. ATTACK IT.**

### 1.1 The decomposition — **manager claim M1**

> **F96 is not one finding. It is FOUR claim-groups wearing one number**, and the
> *"no cheap second method"* verdict is true of **one** of them and was applied
> to all four. **That is F22/F27/F69's shape — *a claim written as a set hides
> its members* — for the fourth time in this programme.**

| group | F96's content | manager's claim about its review state |
|---|---|---|
| **(a) gate-record quotes** | `verdict PASS-WITH-BLOCKED-ROWS`, `failures []`, `complete_run true`, `verus {27,0,27}`, `identity differ/differ`, `forbidden_hits 0`, `skipped_inputs []`, `contract_sha256 7013be6f7c1c`, brackets `66/0`+`16/0` | **cheap — it is a re-read of a committed JSON.** See **M2**: one of the eight is **stale** |
| **(b) the 4-prediction ledger** (R2/R3/R4/R5 vs `_040` §5.6) | *"3 of 4 REFUTED"* | ⭐ **R3 ALREADY REVIEWED by `TASK_PHP_042` §3** — *"the prediction's MECHANISM was wrong"*, with the disassembly, and `_042` §3.2 names `_040` §5.6 as the prediction under test. **R2/R4/R5 unreviewed** |
| **(c) result 2** (A and B agree on every cross-language cell of `ph53`; **because** §B1a's O(1)-allocation precondition holds) | the mechanism claim behind item 78 | ⭐⭐⭐ **TWO REVIEWER VERDICTS, BOTH LANDED, and they split exactly along conclusion/reason**: `_050`/F110 #4 — *"which **confirms** F96's result 2 on its own stated falsifier"*; `_053`/F113 — *"6 of 12 pairs disagree in sign between A1 and B1 on a NON-ALLOCATING kernel, which **refutes** F96 result 2's stated REASON"* |
| **(d) results 1, 3, 4 + the NOVELTY claim** (*"the first IN-BOUNDS uninitialised read … no built row priced that"*) | | ⛔ **the novelty claim is the ONE clause with no cheap second method** — and that is precisely what `_047`'s reviewer checked when it asked whether `ph52` supplies one and found it does not |

### 1.1a ⛔⛔⛔ AND THE PART THAT IS WORSE — **FOUR REVIEWER ROUNDS, TWO VERDICTS, AND THE ATOM STAYED RED**

⚠ **The manager's first draft of this section said `_042` and `_050` were
ENGINEER tasks and that only `_053` was a reviewer verdict. That was wrong and is
corrected here before dispatch.** Checked, header by header:

| task | role, from its own header | F96 in scope? |
|---|---|---|
| `_042` | research **engineer** | ⛔ no — but §3 reviews `_040` §5.6's R3 prediction by name |
| `_043` | research **reviewer** | ✅ yes → returned **UNREVIEWED** |
| `_047` | research **reviewer** | ✅ yes → returned **UNREVIEWED** |
| `_050` | research **reviewer** | ✅✅ **NAMED IN ITS TITLE** — *"and review `F109` · `F107` · `F96` behind it"* → returned **UNREVIEWED**, ⭐ **and produced F110 #4, a verdict on result 2** |
| `_053` | research **reviewer** | ✅ yes → returned **UNREVIEWED**, ⭐ **and produced F113's refutation of result 2's reason** |

> ⭐⭐⭐ **FOUR REVIEWER ROUNDS HAD `F96` IN SCOPE. TWO OF THEM PRODUCED
> SUBSTANTIVE VERDICTS ON ITS RESULT 2 — one CONFIRMING it on its own stated
> falsifier, one REFUTING its stated reason — AND BOTH FILED THOSE VERDICTS
> UNDER THEIR OWN FINDING NUMBERS (F110, F113) WHILE REPORTING `F96` ITSELF AS
> `UNREVIEWED`.**
>
> **The atom was never the unit of review. The CLAUSES were reviewed and the
> ATOM stayed red** — and *"it has no cheap second method"* was written on the
> fourth round by a reviewer that had just supplied one.

▶ **VERDICT REQUIRED, separately:**
- **M1-conclusion:** *is F96 decomposable as above?* (Is the table's grouping
  faithful to F96's text?)
- **M1-reason:** *does the decomposition actually discharge anything?*
  ⚠⚠ **Press the residual objection, which survives the correction above: rule 9
  says engineer → REVIEWER, and a verdict filed under ANOTHER finding's number is
  not obviously a verdict ON F96.** Is *"`_050` confirmed result 2 while calling
  F96 unreviewed"* a **discharge**, or a **bookkeeping failure that leaves the
  cycle genuinely open**? ▶ **The manager's position is that it is a discharge
  for that clause and a bookkeeping failure for the finding. Say whether you
  agree, and write what the RULE-9 table cell should read instead.**
- ⭐ **And the question worth more than either: SHOULD a finding that bundles a
  build record, a prediction ledger and four independent results be admissible as
  one finding at all?** If the answer is no, that is a rule for
  `PROTOCOL_PHP.md` or `04-process.md`, and it needs §H treatment to land.

### 1.2 ⭐ Manager claim **M2** — one of the eight gate quotes is **STALE**

Measured by the manager, 2026-09-15, from `results-php/gate/ph53-iface-tail-uninit.json`:

```
F96 says      contract_sha256 7013be6f7c1c
record says   contract_sha256 6924e66fde49946399dc8e3f312c954b77494666897c8a4e4e692050d55f1da1
```
`git log -- results-php/gate/ph53-iface-tail-uninit.json` shows **three** commits:
`4297b1d` (the build, F96's own), then **`bee710e` (`_042`)** and **`b754da4`
(`_044`)** — so the row has been **re-gated twice since F96 was written**.

✅ The other seven reproduce (`forbidden_hits` lives nested under `idiom_audit`,
not at top level — check that rather than taking the manager's word).

▶ **VERDICT REQUIRED:** is this (i) a **defect in F96**, (ii) a **normal
consequence of a finding being a historical record**, or (iii) a **defect in how
the RECAP presents findings** — as current claims, with no marker that a quoted
record has since moved? ⭐ **And the operative question: what should a finding
that quotes a re-gateable record DO about it?** A rule here would be worth more
than this row's verdict. ⚠ **If your answer is a rule, it needs `§H` treatment
to land — a checker with its must-fire negatives, not a sentence.**

### 1.3 Manager claim **M3** — F96's headline percentage **reproduces**

From the committed `results-php/ph53-iface-tail-uninit.json`, A1 =
`ir.<input>.kernel_exclusive_ir / inputs.<input>.n_iters`:

```
O3/isolated  small.bin  n_iters=25000  unsafe 1116.947 -> verus 1102.947   -1.253 %
```
✅ **`−1.253 %` is exact.** ⛔ **But check the FIVE things it owes**
(`03-numbers.md`): STATISTIC · INPUT · OPT/MODE · BASE · and **if the base is a C
cell, WHICH COMPILER, with both columns**. ▶ **Does F96 state them? Does the
sentence *"the proved rung is cheaper than the unsafe one"* state them?** This is
a **same-language** pair, so the C-compiler clause may not apply — **say so
explicitly rather than skipping it**, because *"it does not apply here"* is the
answer F108 wishes someone had written down the first time.

### 1.4 ⭐ The one clause that is genuinely hard — and a route `_047` did not have

The novelty claim — *"the first IN-BOUNDS uninitialised read … no built row
priced that"* — is **(d)**'s hard half. `_047`'s reviewer checked `ph52` and
found it is a different row with a different kernel.

▶ ⭐ **But THREE more rows have been built since `_047` ran** (`ph55`, `ph56`,
and `ph52` was the row it checked). **And the claim is over the CATALOGUE, not
over the built corpus** — *"no built row priced that"* is a statement about 10
rows and *"the first in-bounds uninitialised read"* is a statement about what the
**102-row catalogue** contains. ▶ **Is the catalogue itself a cheap second
method for this clause?** If yes, run it and verdict the claim. If no, say why in
one sentence — **and then recommend the PERMANENT MARK**, with its exact wording.

⛔⛔ **DO NOT RE-SCOPE THIS INTO A FIFTH ROUND.** The RULE-9 table's own
instruction is *"a dedicated task or a permanent mark"*. **This task is the
dedicated one. It must end with F96 either VERDICTED per group or PERMANENTLY
MARKED per group — never `UNREVIEWED` again as one word.**

---

## §2 ⭐⭐ `F113` — the round that refuted its own ground

`F113` is `_053`'s own finding and has never been reviewed. **Its structure is
already conclusion/reason split, which makes it the cleanest thing in this task
to verdict.**

1. ✅ **CONCLUSION: `§B5`'s verdicts survive** — 12 `0.00`-`argv` cells swept on
   `envp` and `argv[0]`, **24 cell-sweeps, no counterexample**; `ph64` flat on
   all three. ▶ **Re-derive the 24 from the committed sweep artefacts**
   (`.tasks-php/php50_align_sweep.py`, `php53_envp_sweep.py`). ⚠ **If the
   artefacts are in gitignored `.temp/`, that is F99/F51's defect and a finding
   in itself** — **say so, and say whether the generator alone rebuilds them.**
2. ⛔ **GROUND: `argv` and `envp` are NOT the same knob** — `ph07`'s `verus` cell
   steps `34.49` / `20.08` / `0.00` on the three axes. ▶ ⚠⚠ **The scope is ONE
   ROW AGAINST THREE THAT AGREE, and F113 says so.** The reviewer of `_053` added
   that scope *after* the manager shipped it without (item 118). ▶ **Press the
   `iff` argument: F113 says one counterexample breaks an `iff` and §B5 is an
   `iff`. IS §B5 an `iff`? Read §B5's actual text and say.** If it is not, the
   refutation weakens to *"one row disagrees"* and the headline changes.
3. ⚠ **THE MECHANISM IS UNEXPLAINED and the reviewer says so.** Four rival
   explanations were ruled out by measurement (dead instrument, added variable,
   longer period, *"the program reads `argv[1]`"*). ▶ **Is there a FIFTH?**
   ⭐ **The manager's candidate, offered to be shot down: the three axes differ in
   where the bytes land relative to the stack-guard/`AT_RANDOM` block, so a
   `(cell, axis)` step could be a property of the cell's ALIGNMENT SENSITIVITY
   TIMES the axis's REACH, not of the pair.** If that is testable cheaply, test
   it; if it is not, say so and why.
4. ✅ **The inherited caution** — `harness/check.py::_env_block`'s *"three equal
   fields mean **this record cannot tell the two draws apart**, not **the two
   draws are the same**"*. F113 calls this the **second un-inherited caution in
   three rounds** (F108 was the first). ▶ **VERIFY THE CLAIM THAT IT NOW IS
   inherited** — read `§B5` and confirm the caution is present **as applied text,
   not appended** (item 73). ⭐ **And then the question worth more than the
   verdict: are there OTHER cautions in `harness/*.py` that the php layer has not
   inherited? Two in three rounds is a rate, not a coincidence.** ⚠ **Bound this
   — a full sweep of `harness/` is a task, not a section. Sample it, report the
   sample size, and recommend.**

---

## §3 ⭐⭐⭐ ITEM 117 — **A MANAGER CLAIM MADE AND THEN REFUTED BY THE MANAGER, BOTH BEFORE DISPATCH**

**Item 117 is the one load-bearing uncertainty left from `_050`:** `ph53`'s A1
`unsafe→verus` is **exactly `−14.000`** and `14 = 2 × 7`, and F96's headline
`−1.253 %` rests on it. The item records that **no tool here can test it** — the
sweep measures the family-B slope, not `kernel_exclusive_ir`.

⭐⭐⭐ **THIS SECTION IS WRITTEN AS A WORKED INSTANCE OF THE FAILURE MODE THE
WHOLE TASK IS ABOUT.** I formed a claim, wrote it down, and killed it forty
minutes later on the sweep tool's own docstring. **Both halves are below and you
are asked to verdict BOTH — including my refutation, which is also one person's
argument and has had no reviewer.**

### ⛔ Manager claim **M4** — *made, then WITHDRAWN*

Measured 2026-09-15 from the committed `results-php/ph53-iface-tail-uninit.json`:

```
O3/isolated  small.bin  n_iters=25000   27 923 681 -> 27 573 681   Δ = -350 000 = -14.000/call
O3/isolated  large.bin  n_iters=10000   28 359 515 -> 28 219 515   Δ = -140 000 = -14.000/call
```

> **~~The `−14.000` is a per-call constant reproduced on two inputs with
> DIFFERENT `n_iters`. An alignment offset `κ` divides to `κ/25000` and
> `κ/10000` — two different per-call values. Getting exactly `−14.000` on both
> forces `κ = 0`, so the saving is real and item 117 closes at zero cost.~~**

### ⛔⛔ AND HERE IS WHY IT IS WRONG — **manager refutation M4R**

**It rests on modelling the alignment artefact as a WHOLE-PROGRAM ADDITIVE
CONSTANT that divides by `n_iters`. The sweep tool says it is not one.**
`.tasks-php/php50_align_sweep.py`'s docstring, point 1, in its own words:

> *"Every family-B figure any row publishes is `marginal_ir_per_call`, a **SLOPE**
> over two runs at `probe_iters = [100, 200]` … a W1 level carries the whole
> one-shot start-up term, and **the slope cancels it**."*

▶ **So the `0.00`/`0.02`/`7.00`/`34.49 Ir/call` steps are measured in a
statistic that has already cancelled every one-shot term. They are therefore
PER-CALL effects — and a per-call artefact `a` does NOT divide by `n_iters`.**

⛔⛔⛔ **WITH THAT CORRECTION THE OBSERVATION HAS NO POWER AT ALL.** Both inputs
are passed as `…/small.bin` and `…/large.bin`, **both 9 bytes**, so the argv
block is the same length and **both runs sit at the SAME alignment state.** A
per-call artefact `a` is then the *same number* on both, and
`s + a = −14.000` twice is **one draw reported twice.**

⭐⭐ **AND IT IS THE `ph64` DEFECT EXACTLY — SAME SHAPE, SAME ROW PAIR, SAME
MANAGER, TWO ROUNDS APART.** `_050`'s *"two compilers **and two inputs**"*
defence died because the two probe filenames were the same length. **I wrote
M4b arguing the same-length property HELPED here** — that it pinned `κ` to one
unknown and forced it to zero. **That is backwards: it does not pin the
artefact, it makes the second input carry no information.**

### ⛔⛔ AND THE COUNTER-EVIDENCE I SHOULD HAVE LOOKED FOR FIRST — **`14` IS AN ALIGNMENT NUMBER ON THIS EXACT RUNG PAIR**

`.memory-php/03-numbers.md:222-236`, already in the authoritative layer:

- **`ph45`'s `unsafe → verus` is `+106.25` and carries a measured `14.00`
  RANGE** because its two cells have **different phases** — ⭐⭐ **the SAME rung
  pair as `ph53`'s `−14.000`.**
- **`ph55`'s clang cells step `7.00` each, so `14` is what a floor would need to
  protect their DIFFERENCE.**
- and `_050`'s own headline is that **exactly two of `ph45`'s differences carry
  a `14.00` range — the same two.**

▶ **Three `14`s in alignment contexts, one of them on the identical rung pair.
Item 117 worried that `14 = 2 × 7`. The sharper worry is that `14.00` is a
measured alignment RANGE on `unsafe → verus` one row over.**

### ⭐ WHAT ACTUALLY SURVIVES — **manager claim M4S, and it is much weaker**

> The two inputs do **2.5× different per-call work** (A1(unsafe) = **1116.947**
> on `small`, **2835.952** on `large`). So an artefact that scaled with per-call
> work would differ between them. Equality at exactly `−14.000` therefore says
> **any contaminant is per-CALL-constant, not per-window** — ⚠ **a constraint on
> the artefact's SHAPE, not evidence that there is none.**

▶ **VERDICT REQUIRED, and verdict my refutation as hard as you would verdict the
claim:**
1. **Is M4R right?** Is the family-B step per-call, and does that really void
   M4? ⚠ **Check the A1 side separately: `kernel_exclusive_ir / n_iters` is a
   LEVEL over `n_iters`, not a slope, so a one-shot term inside the kernel
   symbol WOULD divide.** ▶ **So M4's arithmetic may still exclude a one-shot
   contaminant while being powerless against the per-call one. Say exactly which
   contaminants each argument does and does not reach** — that distinction is
   the whole value of this section.
2. **Is `s` independently arguable as input-constant** — from the R4/R5 source
   diff or the disassembly — rather than inferred from the equality it is being
   used to explain?
3. ⭐⭐ **ITEM 117'S ROUTE.** The item says *"no tool here"* measures A1 under an
   argv sweep. **But `php50_align_sweep.py` already runs the built binaries under
   callgrind and parses the output** — reporting `kernel_exclusive_ir` per pad
   alongside the family-B slope looks like an extension, not a new tool.
   ▶ **Is it? Price it.** ⛔ **If it is, it lands with its must-fire negatives
   INSIDE it (§H) and never in gitignored `.temp/`.**
4. ▶ **Item 117 CLOSES or STAYS OPEN, with the reason.** ⓘ The manager's
   position after M4R is that **it stays open** and M4 must not be cited.

### ⭐ Manager claim **M5**

> **Only ONE of F96's four groups genuinely lacks a cheap second method** — the
> novelty claim of **(d)**. ▶ **Verdict it, and if you disagree, name the group.**

---

## §4 ⭐ THE PREDICTION THIS TASK REGISTERS

⚠ **M4 is already dead by my own hand, so *"at least one is refuted"* is no
longer a prediction — it is a fact before you start.** The registered
predictions are therefore sharper:

- **P1 — at least one of `M1`, `M2`, `M3`, `M5` is refuted**, and I expect it to
  be a **REASON** rather than a **CONCLUSION**. Base rate: **four consecutive
  rounds, and not one finding survived as written in the last one.**
- **P2 — `M4R` (my refutation of my own claim) survives, but NOT AS STATED** —
  I expect its scope to be narrowed by the level-vs-slope distinction in §3's
  question 1, which I noticed only while writing the question.
- **P3 — `M1`'s CONCLUSION survives and `M1`'s REASON is narrowed**, on §1.1a's
  residual objection (a verdict filed under another finding's number may be a
  bookkeeping failure rather than a discharge). ⚠ **I have already had to correct
  §1.1's first draft once, before dispatch, on exactly this distinction — which
  is itself evidence that it is the fragile part.**

▶ **Score all three. If all four of M1/M2/M3/M5 survive, say so — that is the
most interesting outcome available here and it breaks a four-round run.**

---

## §5 ⛔ TRAPS

1. ⚠⚠⚠ **`grep -a` ALWAYS** (F35). A line-grep misses a phrase that wraps, and
   `RECAP_PHP.md` wraps constantly.
2. ⛔⛔ **APPENDING A CORRECTION LEAVES THE OLD NUMBER STANDING** — item 73, now
   **five instances**, the last one in the RULE-9 table itself. ▶ **When you
   recommend a change to a table or a rule, write the REPLACEMENT TEXT, not an
   addendum.**
3. ⛔ **Never quote an `O0` figure as a performance result**, and **every
   percentage owes five things** (`03-numbers.md`). ⓘ `ph53`'s `O0` cells read
   `−16.870 %` for the same pair that reads `−1.253 %` at `O3` — **a 13× spread
   between opt levels on one pair**, which is exactly why the rule exists.
4. ⛔ **`inside_share` is PER CELL, and a HIGH share is NOT a certificate** —
   `ph55`'s C cells are 74–83 % while A1 reads `0.000 %` on its own defect site.
5. ⛔ **`preimage_screen.py` has four outcomes and only `NOT-THE-REPAIR` is a
   proof** — if you touch it at all.
6. ⛔ **No `/tmp` scratch — use `.temp/php55/`.** Keep the generator, delete the
   artefact. ⛔ **A validator or probe that feeds a verdict lands with its
   must-fire negatives INSIDE it** (§H), **never in gitignored `.temp/`**.
7. ⛔ **No `git add` / `git commit`.** ⚠⚠ **NO EDITS to `RECAP_PHP.md`,
   `.memory-php/`, `harness/`, `common/`, `patterns/`, `results/`, `pilot/`,
   `common-php/`, `.web/`.** ⚠ **You may READ anything.** The manager lands.
8. ⛔ **Never `pkill`/`killall`/substring-match a process.** Confirm an exact
   PID's full command line. Prefer `timeout <N> <cmd>`.
9. ⚠ **A comment is not code** — fourth instance this programme. **Test behaviour.**
10. ⚠⚠ **NEVER refuse or down-rank anything for a Rust-side, Verus-side or
    ladder-side reason** (`CLAUDE.md` rule 6). *"Safe Rust can't express it"*,
    *"no column moves"*, *"Miri doesn't see it"*, *"the R5 can't state the
    obligation"* are **FINDINGS, NEVER KILLS**.
11. **Brackets, first and last, and they must not move — this task measures
    nothing and re-gates nothing:** `python3 harness/measure.py --check-stale`
    → **`66/0`**; `python3 harness-php/gate.py --tool measure --check-stale`
    → **`22/0`**. ⛔⛔ **NEVER run `harness/check.py` directly on a php row** —
    the shim lengthens every repo-relative path by exactly 15 bytes against a
    16-wide alignment window, so a direct run measures a different state.

---

## §6 DEFINITION OF DONE

1. **`M1` · `M2` · `M3` · `M4` · `M4R` · `M4S` · `M5` verdicted, CONCLUSION and
   REASON separately**, in a table. ⚠ **`M4R` and `M4S` are the manager's
   refutation and residue and they get the same scrutiny as the claim** — a
   self-refutation is still a one-person argument.
2. **F96 ends VERDICTED PER GROUP or PERMANENTLY MARKED PER GROUP** — with the
   **replacement text** for the RULE-9 table cell written out. ⛔ **`UNREVIEWED`
   as one undifferentiated word is not an acceptable outcome of this task.**
3. **F113 verdicted** on all four points of §2, including an explicit reading of
   whether **§B5 is an `iff`**.
4. **Item 117 either CLOSED or routed**, with the reason.
5. **The §4 prediction scored.**
6. ⭐ **What you are UNSURE of, in its own section** — named, not omitted.
7. ⭐⭐ **If your depth runs out, STOP AND SAY EXACTLY WHERE.** `_051` did that
   and it cost the programme one task and nothing else. **A truncated report with
   an honest boundary beats a complete one with an invented cell.**
8. **Anything you find that is NOT on this list** goes in a section called
   **"not on the list"**. Every round that had one found something there —
   `_043` found nine defects that way, `_049` found F108.
9. **Brackets quoted first and last.**
