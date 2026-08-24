# TASK_081 — REVIEW: does the `assume_specification` escape reach finding 14, or stop short of it?

**Role:** research reviewer. **You do not fix. You report.**
**Read first:** `.tasks/PROTOCOL.md` (**the reviewer checklist and the Severity
section**), then **`.tasks/TASK_080.md` in full, including its Outcome block**,
then `.memory/04-verus.md`'s **final section** — *"PROVISIONAL — `is not
supported` may be ESCAPABLE at +1 trusted item"* — which is the thing under
review. Then `.memory/01-ladder.md` **finding 14** (*"every rung is a spelling"*,
the programme's central methodological result) and **finding 17** (p11), and
`RECAP.md`'s **finding 14** and its *"settled answers"* block. Evidence to read,
**not** to trust: `.temp/p45pat/NOTES.md` and `.temp/p45pat/v_unchecked*.rs`
(**readable, NOT writable**).

⚠ **PROTOCOL rule 3 is flagged against TWO things in this task, and they are the
manager's.** The manager wrote the objections that refused p45, and the manager
adopted the **LADDER TEST** as a selection rule **one commit ago with no review
at all**. *Designer-validates-own-design is the configuration this project keeps
finding defects in.* **Attack both.**

⚠ **A review that says "looks good" without having tried to break something is a
failed review.** ⚠ **And rule 6: a named attack that did NOT land is worth as
much as a finding** — it stops the next agent re-running it. **Report your clean
negatives explicitly.**

## What is already established, and what you may not re-assume

✅ **Manager-verified, both runs — do not spend time reproducing these:**

- `i32::unchecked_add` at the pin gives `error: ... is not supported`, **and Verus
  prints the resolving `assume_specification` declaration in its own help text.**
- With that declaration (`requires i32::MIN <= a + b <= i32::MAX`,
  `ensures r == a + b`, `opens_invariants none`, `no_unwind`):
  **`2 verified, 1 errors`**, the one error being a deliberately bad call site
  failing `precondition not satisfied`. **The escape works and the `requires`
  bites.**
- The same shape works for `u64::unchecked_shl`.

⚠ **What is NOT established is everything that makes this matter.**

## The review, in priority order

### R1 — ⚠⚠ THE QUESTION THAT DECIDES THE WHOLE FINDING. Run it first.

**Both verified escapes are ARITHMETIC intrinsics whose contract is one line
(`r == a + b`) and obviously right. Finding 14's six items are mostly MEMORY
operations:** `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`,
`TryFromSliceError`, `from_le_bytes`.

**A sound `assume_specification` for `read_unaligned` must express a PERMISSION
precondition** — *"the caller holds a `PointsTo` covering these bytes"* — which
is a different order of difficulty from an arithmetic bound and **may not be
expressible at all at this pin.**

> **So: does the escape reach the memory items, or does it stop exactly where
> finding 14's claim lives?** Take them **one at a time**, write the declaration,
> run `./verus_run.py`, and report per item: **(a)** does Verus accept the
> declaration at all; **(b)** does a *correct* call site verify; **(c)** does an
> *incorrect* call site **fail** — because a declaration whose `requires` does
> not bite is worse than no escape, it is a **vacuous** one; **(d)** how many
> trusted items did it cost.
>
> ⚠ **(c) is the one to spend effort on.** The reviewer checklist's own words:
> *"Does the `external_body` wrapper's `ensures` actually match real Rust
> semantics? A wrong one axiomatises a falsehood."* **An `assume_specification`
> is exactly that risk with a friendlier syntax and a help message that invites
> you to paste it in.**

### R2 — The biggest number in the tree on this axis: p11's `r4_cstr`.

`.memory/01-ladder.md` finding 17 records `r4_cstr` as worth
**−17 526 `Ir`/call (−35%)** on `large` and *"rejected with **four**
`is not supported` errors"*. **Under the escape, is that "+4 author-written V-gap
items" rather than a wall?**

- **Name the four items** and try the escape on each.
- ⚠ **If it works, p11's finding does NOT simply flip** — p11's whole claim is
  *"the safe class reaches `core::slice::memchr` at ZERO TCB; the unsafe class
  cannot reach it at all"*. **"Cannot reach it at all"** and **"reaches it at +4
  hand-written axioms on a pattern whose claim rests on one"** are different
  sentences with different strengths. **Say which one the measurement supports**,
  and do not let the number decide the sentence.
- ⚠ **And the `identity` pin still applies**: a rung is not a rung without a
  byte-identical verifying twin. **Does `r4_cstr` hold the pin?** Finding 14's
  argument runs through that, not through the error count.

### R3 — ⚠ A GATE QUESTION WITH A PUBLISHED COLUMN BEHIND IT.

**Does `check.py`'s trusted-item accounting recognise an `assume_specification`
at all?** Read `check.py::_trusted_items` and `harness/vparse.py`, and check
against a real pattern's record.

> ⚠ **Why this is not hygiene.** **TCB size is a published column** of this
> project, and `RECAP.md`'s settled answers say *"prospectively the column IS
> gameable."* If `assume_specification` items are **not counted**, then a pattern
> can add trusted axioms that **do not appear in its own TCB tally** — and the
> escape above is precisely the mechanism that makes someone want to.
> **Report the answer either way**; a clean negative here is valuable and closes
> a question nobody has asked.
> **If it needs a `check.py` change, SAY SO AND DO NOT MAKE IT** — reviewers do
> not fix, rule 5's default is back, and a new gate check owes the *"could this
> happen by accident?"* test.

### R4 — Attack the p45 refusal. The manager wrote the objections that landed.

The refusal's core is **"p45 has no unsafe rung with a job"**, under two
contracts. ⚠ **TASK_080's engineer says explicitly it did not search for a fourth
framing** — *"I could not construct one that gives R4 work to do."* **Try.**

- Is there a contract under which `unchecked_add` does real work and the harm is
  not p18's? (Consider: does the overflow have to be *detected* by the kernel at
  all, or could the obligation live in a `requires` the way p11's overflow guard
  does?)
- ⚠ **The refusal's `readelf` evidence is the load-bearing part.** *Two symbols on
  one section* and *a 155-byte section that md5s identically to another* — **check
  both.** If they hold, the ladder really is one rung and the refusal stands
  regardless of framing.
- **Clean negative wanted:** if you cannot construct a fourth framing either, say
  so **and say what you tried**. Two independent failures to find one is worth
  recording; it is what closes the row.

### R5 — Attack the LADDER TEST itself. It is one commit old and unreviewed.

`.memory/06-catalogue.md`'s new *"THE LADDER TEST"* says: **a pattern needs a bug
that R4 can reintroduce and R3 cannot, and a cost that differs between them.**

⚠ **The manager's own strongest objection to it, which is why it is in this task:
would it have refused patterns this project was RIGHT to build?**

- **p47** — its published result is *"the proof certifies a LEAKING kernel"*, and
  its timing axis is `Ir(k=0) − Ir(k=n−1) = 0` **exactly**. **Does p47 pass the
  "a cost that differs" half?** If it does not, **the rule as written would have
  refused p47, and the rule is wrong.**
- **p16** — its per-byte R3−R4 is **0.00000**, published as the headline. The
  ladder-test block claims p16's zero is *"genuine because it has a mechanism"*
  and distinguishable from p45's artefact. ⚠ **Is that distinction real, or is it
  a rationalisation available after the fact?** Run the block's own two commands
  (`readelf -sW`, `md5sum` of extracted kernel bytes) **on p16** and report what
  they say. **If p16's rungs are also two symbols on one section, the test cannot
  tell the two cases apart and the block is wrong.**
- **p08** — its bug *cannot* be expressed in R3 at all, which the ladder test
  treats as a failure mode (it is how p48 died). **p08 shipped and is a
  finding.** **Is the test's first half therefore also wrong, or is p08 a stated
  exception?** The block does not say.

**If the test survives, say under what restatement.** If it does not, **say so
plainly — it is one commit old and cheap to retract**, and it is currently
sitting in RECAP's START HERE box as guidance.

### R6 — Check the manager's landed corrections.

Three things were landed in the last two commits **from agent reports, and two of
those were wrong the first time**:

- `.memory/03-measurement.md` — **`12.30×`** replacing the manager's wrong
  `8.6×`. **Re-derive it** (15,565,615 / 1,265,467 from
  `.temp/p31pat/cost_functions.log`), and check the entry's claim that **three
  ratios exist and only two are real** (level 12.30×, marginal 14.00×).
- `.memory/03-measurement.md` — the **p27 `0.00 allocator` answer**. It is
  recorded as **GENUINE** on the strength of `NOTES.md:793`'s
  `malloc 421.1211 / 421.1211`. ⚠ **Check the rule the entry extracts from it** —
  *"check whether the SYMBOL IS PRESENT, not whether the difference is zero"* —
  and say whether it generalises or is p27-specific.
- `.memory/00-environment.md` — the **`|delta| == 16`** adjacency refinement.
  It says a `y - x == +16` probe reports gcc *"notadjacent"* **with no sanitizer
  at all**, i.e. it manufactures its own result. **Confirm or refute.**

## Done when

`.tasks/TASK_081_REVIEW_REPORT.md` **exists** — ⚠ **PROTOCOL rule 10: write the
report file BEFORE anything cites it.** Three dangling citations once shipped in
`.memory/`, the layer this project calls authoritative, because a manager landed
corrections and moved on. Check yourself before finishing:

```bash
grep -rho '\.tasks/TASK_[A-Za-z0-9_]*\.md' .memory/ .tasks/ RECAP.md \
  | sort -u | while read p; do [ -e "$p" ] || echo "MISSING: $p"; done
```

(`TASK_NNN.md` and `TASK_NNN_REVIEW_REPORT.md` are documented placeholders;
ignore those two. ⚠ **`TASK_081_REVIEW_REPORT.md` will ALSO show as MISSING until
you write it** — that is this task's own deliverable and every review task file
in this project has that transient. **It must not still be missing when you
finish.**)

⚠ **On the naming, so nobody thinks the convention broke:** reviews of a
*deliverable* are `TASK_NNN_REVIEW.md`. This is **not** that — `TASK_080`'s
deliverable was a **refusal**, which the manager **accepted** without review
(TASK_074's precedent). This task exists because that refusal threw off a
**positive finding of project-wide reach** which rule 9 forbids landing
unreviewed, and because it must also attack a **manager rule adopted in a
different commit**. It is a standalone numbered task that happens to have the
reviewer role.

The report must carry, per PROTOCOL Severity: findings ranked
`blocker`/`major`/`minor`, each with **file:line and a concrete failure
scenario**, **plus an explicit clean-negatives list**. **Do not pad — 3 real
blockers beat 20 nitpicks.** For **R1** the deliverable is a **per-item table**
(item × accepted? × correct call verifies? × **bad call fails?** × TCB cost), and
for **R5** a **verdict on the rule with a restatement if it needs one**.

⚠ **Paste actual `./verus_run.py` output.** *"Should verify"* is not a result.

## Constraints

**You are a reviewer: you do not fix, and you do not build a pattern.**
⚠ **`ls` any scratch path before you name it** — `.temp/pNN/` is a live
PATTERN-vs-TASK collision (`.temp/p31/` is TASK_031's evidence, `.temp/p48/` is
TASK_048's, and both were nearly destroyed by a manager prescription). Suggested
scratch: **`.temp/r81/`** — `ls` it first. `.temp/p45pat/` and `.temp/p31pat/`
are **readable, NOT writable.**

No root; no `/tmp`; **no `git add`/`git commit`** (read-only git is fine); do not
edit `pilot/`, `.memory/`, `harness/`, `common/`, `results/`, or any pattern
directory. ⚠ **Editing any `patterns/*/*.md` makes that pattern's gate record
STALE** — so if a finding needs a doc change, **report it, do not make it.**
Verus only via `./verus_run.py`; `~/tools/verus/vstd/` for vstd source —
**never** `../LearnVeri/_VERUS_DOC_/vstd/`, an older snapshot that caused one
false *"no spec exists"* that stood for 44 tasks. clang `~/tools/llvm/bin/clang`,
gcc `/usr/bin/gcc`, valgrind `~/tools/valgrind/bin/valgrind`, rustc
`~/.cargo/bin/rustc` — **none but gcc on PATH**. `timeout <N> <cmd>`. Never
`pkill`/`killall`; **no `nohup … &`**; ⚠ **no self-matching `pgrep` wait-loops**.
**You are the only agent running.**

⚠ **A probe hazard found one task ago, so you do not rediscover it:**
`grep -E "$SYM"` over `callgrind_annotate` output **matches the echoed command
line** when a kernel name is an `argv`. **Parse the table, do not grep it.**

Notes to your scratch `NOTES.md` as you go, so a transient API death loses
nothing.

**If a prescription here is wrong, say so with the measurement.** ⚠ **Running
count 214** — **+6 from the last task, FOUR of them manager errors, and two of
those four were landed one commit before being caught.** The count is the
evidence that this instruction is not a courtesy.

**What I am least sure of, by name: R5 — the LADDER TEST is mine, it is one
commit old, and I think its second half is WRONG AS WRITTEN.** *"A cost that
differs between them"* would have refused **p47**, whose entire finding needs no
cost gap, and its first half would have refused **p08**, whose bug cannot be
expressed in R3 **and which shipped as a finding**. **I believe the honest rule is
narrower — something like *"either the ladder separates the rungs or the pattern
states in advance which single axis carries it"* — but I have not tested that
against the 22 built patterns and I am not confident in the wording.** ⚠ **The
rule is currently in RECAP's START HERE box as guidance for the next agent, so a
wrong version of it is expensive. Attack it hard, and if it needs retracting, say
so.**

**Second-least sure: R3.** I do not know whether the gate counts an
`assume_specification` as a trusted item, and **TCB size is a published column
this project has already called prospectively gameable.** If the answer is "it
does not count them", that is a real finding and it arrives at exactly the moment
someone has a reason to want the escape.

---

## Outcome (recorded by the manager at the task boundary)

⚠ **The review landed TWO BLOCKERS, both against manager-written text, and one of
them retracts a rule the manager adopted ONE COMMIT EARLIER and put in RECAP's
START HERE box.** Report: `.tasks/TASK_081_REVIEW_REPORT.md` (700 lines);
evidence and `repro.sh` at `.temp/r81/`. **Nine ranked findings, eleven named
clean negatives.** ⚠ **Two prior attempts at this task died to API 529s having
produced nothing**; the third was given explicit resilience instructions (notes
appended per measurement, report written incrementally) and completed.

**BLOCKER 1 — the gate counts no `assume_specification`, and TCB size is a
PUBLISHED column.** ✅ **Manager-verified.** `vparse.py`'s matcher needs a body,
so `assume_specification`, `broadcast axiom fn` and `uninterp spec fn` are all
invisible; `check.py::_is_trusted` additionally requires `external_body`.
Demonstrated on `patterns/p01-array-sum/verus.rs` with **two deliberately FALSE
axioms on safe std functions**: `7 verified, 0 errors`, **identical parsed item
list, identical TCB, byte-identical kernel** (`md5 e3e4441313c93057…`). Blind to
it: the synthesis TCB column, the obligation count, the `identity` pin,
`check_miri`, and stages 5c/5c-req/5c-twin. ⚠ **Correctly scoped by the
reviewer — the hole is axioms on SAFE functions**, and those are exactly finding
14's list. **Landed as RECAP "Owed" 0 and it is now the top of the queue.**

**BLOCKER 2 — the LADDER TEST's first half is wrong in BOTH directions.**
`p08` **satisfies** it and shipped as finding 7; `p47` **violates** it and
shipped. ⚠⚠ **And the manager's own least-sure call was aimed at the wrong
half**: the manager predicted p47 would fail the **cost** half, and ✅
**manager-re-measured it passes comfortably — `R3 − R4 = +90.0 / +142.0`**
(524.0/747.7 against 434.0/605.7, O3/isolated). The rule also never named its
`Ir` convention (p08: level differs, slope does not — **opposite verdicts**), and
its `readelf` half **cannot fire on a shipped pattern**, because every rung here
is its own binary. **Retracted and restated as three probes**, keeping the
`md5`-the-extracted-kernel-bytes half, which is the part that would have caught
p45 — and which ✅ **does not false-positive on p16** (410 B vs 324 B, different
digests).

**MAJOR 3 — the escape as the manager recorded it is VACUOUS for the memory
items, which are the ones that matter.** ✅ **Manager-verified**: the declaration
shaped like Verus's own printed help text gives `4 verified, 0 errors` **while a
1 MiB out-of-bounds read and a null dereference both verify.** ⚠ **And the same
hazard is one omitted line from TASK_080's "safe" arithmetic case** — delete the
`requires` and `assert(false)` verifies; compiled, the binary aborts on
`unsafe precondition(s) violated`. **Verus verified a program that hits real UB on
its first call, and nothing checks an `assume_specification` against anything.**
The honest price is **1 / 4 / 6 trusted items**, not `+1`, and `from_le_bytes` is
**unreachable**. **Rewritten in `.memory/04-verus.md`, trap first.**

**MAJOR 4 — RECAP finding 14's *"every route to respelling a header read needs a
new trusted item"* is REFUTED.** ✅ **Manager-re-run:**
`vstd::slice::slice_subrange` + `vstd::bytes::u64_from_le_bytes` gives an
arbitrary-offset LE `u64` **with its value** at **zero** author-written trusted
items, `2 verified, 0 errors`. ⚠ **The six `is not supported` items are still
correct — the error was inferring a universal from a list.** ⚠ **And it refutes
the REASON, not necessarily the conclusion: that route's `Ir` cost is unmeasured
and may be dearer than the shipped spelling.** Landed as the weaker sentence the
evidence supports.

**MAJOR 5 — the p27 rule the manager extracted does not generalise.** *"Check
whether the symbol is PRESENT"* is refuted by one escaping allocation outside the
loop: symbols all present, loop allocations still elided, **exactly the artefact
rate**. **Presence is necessary, not sufficient; the test is a RATE**, which is
what p27 had all along (421.1211 `Ir`/call in both rungs).

**MINOR 6 — the adjacency per-compiler attribution was wrong**: gcc `-O0` is
`+16`, and a `.bss` variant flips clang. The sign is a function of **opt level
and storage class**, not compiler. Retracted; `|delta| == 16` upheld and
strengthened.

⚠ **MINORS 7 AND 8 ARE THE MANAGER'S OWN CITATIONS, IN THE TASK FILE THAT
FORWARDS THE RULE AGAINST THEM.** This file's reading list cites
*"`.memory/01-ladder.md` findings 14/17"* using **RECAP's** numbering — the live
collision this project documents in three places and warns about in every task
file (**ladder 14 is p13; p11 is ladder 9**). And this file points at
`cost_functions.log` for `15,565,615 / 1,265,467`, which contains **neither
number** — they are in `.temp/p45pat/NOTES.md`. **Both are left in place and
recorded here rather than silently edited**, per rule 11's precedent: correct in
a following commit, do not rewrite the record. **This is the third time the
manager has mis-cited across the two numbering schemes.**

**Manager decisions:**

1. **All six corrections landed before this commit** (rule 4). The LADDER TEST is
   **retracted in place with the retraction kept**, not deleted — how it was
   wrong is the reusable part, and it is the second manager rule this project has
   had to retract within two tasks of adopting.
2. ⚠ **"Owed" 0 is the next task, and NO NEW PATTERN until it closes.** Rule 5's
   *"prefer producing a pattern over hardening the gate"* is **overridden on the
   TASK_068 standard** — a measured defect in a published column, demonstrated on
   a real pattern's own file, not speculative hardening.
3. **The escape is NOT recorded as a lever anyone should reach for.**
   `.memory/04-verus.md` now leads with the vacuity trap and prices the honest
   route at 4–6 hand-written axioms **that no gate stage checks** — which is
   worse than the wall it replaces, not better, and is the correct reading.
4. **p11's sentence is narrowed, not flipped**: *"reaches `core::slice::memchr`
   at four hand-written axioms that no gate stage checks"* — ⚠ and two of the
   four are **types**, both functions are **safe**, so **there is no `requires` to
   bite at all.** `patterns/p11-nul-scan/NOTES.md` contains both the old and the
   new sentence; **queued, not silently fixed** — it is a pattern doc and editing
   it stales p11's gate record.

⚠ **PROTOCOL rule 2's running count is 223:** 214 at TASK_081's writing, **+9** —
the nine ranked findings, **seven of them against manager-written text**, and
**two of those inside the task file that forwards the rule against them.**
**Carry 223 forward.**

**The single most useful thing in this block.** ⚠ **The manager adopted a
selection rule and put it in the handoff document in the SAME COMMIT, and it
survived one task.** The rule was reasoned from three refusals — real evidence —
and was still wrong on the two patterns most available to test it against, both
of which are *already built and already written up*. **The manager did not check
it against the tree before shipping it as guidance**, which is the same failure as
*"the six original axes are complete"* and *"183 forbidden spellings"*: **a claim
about the corpus asserted instead of run against the corpus.** ⚠ **The one thing
that worked is that the manager named the rule as its own least-sure call and
told the reviewer to attack it — and the reviewer found the defence was aimed at
the wrong half.** That is rule 2 paying for itself: **being wrong in public and
early cost one task; the rule sitting in the START HERE box unchallenged would
have cost every pattern selected under it.**
