# TASK_083 — REVIEW `TASK_082`, then CHOOSE THE NEXT PATTERN with the three probes

**Role:** research reviewer. **You do not fix. You report.**
**Read first:** `.tasks/PROTOCOL.md` (**the reviewer checklist and Severity**),
then **`.tasks/TASK_082.md` in full, including its Outcome block**, then
`.memory/06-catalogue.md`'s **"THE LADDER TEST"** section (the retraction *and*
the three probes that replaced it), `.memory/05-layout.md`'s new
**`vparse.parse()` drops body-less items** section, and
`patterns/p17-http-range/NOTES.md` **§10b**.

⚠ **This task has TWO halves and the second is the one that matters most.**

⚠ **PROTOCOL rule 3 is flagged against the whole of part B.** **Three catalogue
rows in a row were refused** — `p48`, `p31`, `p45` — and **all three were chosen
by the manager.** The rule that came out of that was **itself retracted one task
later** and replaced with three probes **that have never been used to choose
anything.** So: **the manager is not choosing this one.** Part B's shortlist is
offered to be disagreed with, and *"none of these, build X instead"* is the
outcome the manager most wants.

---

# PART A — review `TASK_082`

**Context you may take as established (manager-verified, do not re-derive):**
22 verdicts identical with 0 failures; TCB total **92 → 92**; `axiom_decls`
present and empty in all 22; `--check-stale` **0 STALE**; `licence.json`
re-emitted with **0 of 88 verdicts changed**; `results/synthesis.md` regenerates
**byte-identical**; `vparse.py selftest` PASS.

### A1 — ⚠ Attack the new gate stage. It is 127 new lines in a 7164-line file that nothing else checks.

- **Can it be bypassed?** The matcher is keyword-keyed (`assume_specification`,
  `axiom fn` incl. `broadcast axiom fn`, `uninterp spec fn`). **Find a body-less
  trusted declaration Verus accepts that the matcher does NOT count.** Line
  continuations, `#[verifier::…]` attributes between the keyword and the name,
  `pub(crate)`, generics with `where` clauses on their own line, a declaration
  inside a `mod`, macro-generated ones — **try them and paste what Verus says.**
  ⚠ **A false negative here is the whole defect coming back**, so this is where
  to spend effort.
- **Can it FALSE-POSITIVE?** It ran clean on 22 patterns and on 400 vstd
  declarations — but **find something legal it miscounts**. A `broadcast proof fn`
  *with* a body is deliberately not counted (it is proved, not axiomatised);
  **check that boundary is drawn where the engineer says.**
- ⚠ **`_is_trusted` was deliberately NOT fed.** The stated reason is that stage
  5c-twin would demand a twin of a body-less item, making a legal declaration
  unpassable. **Is that reason true?** Read `check_trusted_twins`. **If it is
  false, the TCB column is still under-counting and blocker 1 is only half
  fixed** — which would be a blocker of your own.
- **Is `verus.axioms` defaulting to 0 the right default?** It means a pattern that
  adds an axiom **fails** until it declares one. Check that the failure message
  tells an author what to write.

### A2 — ⚠ Attack p17's new law. It is PROVISIONAL and rule 9 keeps it out of `.memory/` until you land.

`patterns/p17-http-range/NOTES.md` §10b claims `R3ship − R4` over `nsuf = 1..8`
is **18, 23, 30, 37, 44, 49, 56, 63**, that `≈7·nsuf + 9` is *"a straight line
through a staircase"* (max residual 0.81), and that **lag-4 differencing gives 26
four times with zero residual = 6.50 `Ir` per request**, a mod-4 sawtooth from
the 4×-unrolled table walk.

- **Re-measure at least two points independently** and say whether they agree.
- ⚠ **The mechanism is the claim, not the arithmetic.** *Any* 8-point sequence
  can be lag-4 differenced; **that four differences are equal is a fact about
  these numbers, not evidence of a 4× unroll.** **Go to the disassembly and say
  whether the table walk is unrolled 4×.** If it is not, the *law* may survive
  while its *explanation* dies — say which.
- ⚠ **Out-of-sample or it is a fit.** `nsuf = 9..12` is one `gen.py` flag away.
  **Does `6.50/request` predict them?** This project's own rule is that
  additivity extrapolation is the only out-of-sample test here that can fail, and
  it **has** failed once.
- **Check the disclosure**: the claim is that no published p17 number is wrong
  because `+32` is the shipped pair at `nsuf = 3` and the band gives **30**.
  ⚠ **30 ≠ 32.** **Is the difference explained, or is a published number off by
  2?**

### A3 — the two things `TASK_082` reported but did not do

- `patterns/p01-array-sum/spec.md` still carries the retracted
  `| identity | recorded as a **result**, not a gate condition`. **Confirm it is
  only p01**, and confirm the sentence is genuinely retracted (`check.py` stage
  3c says so).
- ⚠ **The substring-grep lesson**: a deferred item sat for **fifty tasks** because
  the correction *appended* rather than replaced, so `grep 'recorded as a result'`
  kept hitting the fixed line. **Is anything else in `.memory/` or `RECAP.md`
  being kept alive by the same trick?** One pass, report what you find.

---

# PART B — choose the next pattern, and run the three probes on it

**This is a selection deliverable, not a build.** Run the probes,
report a ranked recommendation with the measurements behind it, and **name what
would kill each candidate.** ⚠ **You are not building anything.**

### The three probes (from `.memory/06-catalogue.md`, restated at TASK_081_REVIEW)

1. **A rung boundary must exist somewhere, and the row must NAME it.** ⚠ **Not
   necessarily R3-vs-R4** — p08's runs at compile time, p47's runs *inside* the
   safe class, p16's is a slope. **Fatal is no boundary anywhere.**
2. **The rungs must differ AS MACHINE CODE** — extract each kernel's bytes and
   `md5` them. **Collide ⇒ the pattern is one rung.** (This is what would have
   caught `p45`.)
3. **Any published `0.00` must name its axis and `Ir` convention IN ADVANCE.**

⚠ **Probe 2 needs real rungs, which do not exist before the pattern is built.**
**Approximate it on throwaway probes** the way `p45` was killed — two small
kernels in one object file is fine for a *pre*-check, and say that is what you
did. **Do not report a probe-2 result as if it came from built rungs.**

### The manager's shortlist — offered to be disagreed with

**All four are `planned` rows. The reasoning is the manager's and is stated as
questions.**

- ⚠ **`p15` — UTF-8 validation + decode. The manager's pick, and here is why and
  what would kill it.** The rung boundary looks **unambiguous**:
  `str::from_utf8` (R3, validates) against **`from_utf8_unchecked`** (R4, a real
  unsafe fn whose safety precondition is *exactly* the validation). The cost axis
  is **the** canonical *"what does Rust's safety cost"* argument and the tree has
  nothing like it. ⚠ **And the harm may be a genuinely new CLASS: a VALIDITY
  INVARIANT violation** — `from_utf8_unchecked` on invalid bytes is instant UB
  with **no bounds violation at all**, which is not any of the tree's twelve
  `index >= len`. **Questions: (i)** is `from_utf8_unchecked` supported at the
  pinned vstd, or is it `is not supported` like four previous R4 candidates —
  **run that first, it can end the row**; **(ii)** can Verus even *state* "valid
  UTF-8", or is R5 a stall? **(iii)** what is the C rung's harm — if it is a
  decoder walking continuation bytes past the end, that is the **thirteenth**
  `index >= len` and the validity story has to carry the pattern alone.
- **`p25` — dynamic array with `realloc` growth** (growth overflow, **stale
  pointer**). The stale-pointer half is a harm the tree does not have: `realloc`
  moves the buffer and every saved pointer dangles. Safe Rust's `Vec` forbids it
  **by construction**; unsafe Rust reintroduces it exactly. ⚠ **Is that p27's UAF
  in a costume?** And ⚠ **TASK_079 measured that both compilers DELETE a
  non-escaping `malloc`/`free` pair at `-O2`** — an allocator in the kernel needs
  `-fno-builtin-*` or it measures nothing.
- **`p42` — `goto cleanup`, leak on the error path.** Rung boundary is clean
  (safe Rust's `Drop` cannot leak here; C's error path can). ⚠ **Is a LEAK a harm
  this ladder can price at all?** It is not memory-unsafety, `Ir` will not see
  it, and the catcher is Miri's leak check or valgrind. **And p27 already
  measured drop glue at 120.42 `Ir`** — is p42 just that number again?
- **`p23` — in-place quicksort partition.** The **permutation invariant** would
  be the tree's first proof obligation that is not a bound — genuinely new for
  R5. ⚠ Rated `hard`; the budget is one engineer session for the R5 cell, then
  report where it stuck.

⚠ **A fifth option that is NOT on the shortlist and may beat all of it: propose
your own row and argue it.** 24 rows are unbuilt. **The manager has now chosen
three losers in a row and the selection rule has never been exercised — treat the
shortlist as a prior, not a menu.**

## Done when

`.tasks/TASK_083_REVIEW_REPORT.md` **exists** — ⚠ **PROTOCOL rule 10: write it
before anything cites it**, and it will show as `MISSING` in the check below
until you do:

```bash
grep -rho '\.tasks/TASK_[A-Za-z0-9_]*\.md' .memory/ .tasks/ RECAP.md \
  | sort -u | while read p; do [ -e "$p" ] || echo "MISSING: $p"; done
```

(`TASK_NNN.md` and `TASK_NNN_REVIEW_REPORT.md` are documented placeholders.)

The report carries: **Part A** findings ranked `blocker`/`major`/`minor` with
file:line and a concrete failure scenario, **plus an explicit clean-negatives
list** (rule 6); **Part B** a ranked recommendation with the probe results per
candidate and **the named kill-risk for the one you recommend**.
⚠ **Paste actual output.** *"Should verify"* is not a result.

## Constraints

**You are a reviewer: you do not fix, and you do not build a pattern.**
⚠ **`ls` any scratch path before you name it** — `.temp/pNN/` is a live
PATTERN-vs-TASK collision (`.temp/p31/` is TASK_031's evidence, `.temp/p48/` is
TASK_048's). Suggested: **`.temp/r83/`** — `ls` it first. `.temp/t82/`,
`.temp/r81/`, `.temp/p45pat/`, `.temp/p31pat/` are **readable, NOT writable.**

No root; no `/tmp`; **no `git add`/`git commit`** (read-only git is fine); do not
edit `pilot/`, `.memory/`, `harness/`, `common/`, `results/`, `synthesis/`, or
any pattern directory. ⚠ **Editing any `patterns/*/*.md` makes that pattern's
gate record STALE** — report, do not fix. ⚠ **A `gen.py --sweep` run for A2's
out-of-sample points writes BLOBS, which are gitignored and skipped by both
`check.py` and `measure.py`** — that is allowed; **`gen.py` itself is
measurement-hashed, so do not edit it.** If out-of-sample needs a generator
change, **say so and skip it.**

Verus only via `./verus_run.py`; `~/tools/verus/vstd/` for vstd source —
**never** `../LearnVeri/_VERUS_DOC_/vstd/`. clang `~/tools/llvm/bin/clang`, gcc
`/usr/bin/gcc`, valgrind `~/tools/valgrind/bin/valgrind`, rustc
`~/.cargo/bin/rustc` — **none but gcc on PATH**. `timeout <N> <cmd>`. Never
`pkill`/`killall`; **no `nohup … &`**; ⚠ **no self-matching `pgrep` wait-loops**.
Measurements in the **FOREGROUND**. **You are the only agent running.**

⚠ **A probe hazard, so you do not rediscover it:** `grep -E "$SYM"` over
`callgrind_annotate` output **matches the echoed command line** when a kernel
name is an `argv`. **Parse the table.** ⚠ **And `check.py`'s stdout is
block-buffered when redirected — a stalled log is not a stalled process.**

⚠ **Write `.temp/r83/NOTES.md` per step and start the report early** — two agents
died to API 529s at TASK_081 having produced nothing, and the third completed
only after being told to write incrementally.

**If a prescription here is wrong, say so with the measurement.** ⚠ **Running
count 227** — **+4 from the last task alone, including the manager naming a
hazard, pointing at the exact repair that triggers it, and asserting it could not
fire, all in one paragraph.**

**What I am least sure of, by name: `p15`'s bug class (Part B, question iii).**
I think the validity-invariant story is new and carries the pattern. **But the C
rung's harm is probably a decoder running off the end, which would be the
thirteenth `index >= len` — and "the harm is a duplicate but the mechanism is
new" is exactly what I argued for `p31`, where it was wrong.** p36 made that
argument and was right; p31 made it and was refused. **Decide which one p15 is,
with a measurement, before recommending it.**

**Second-least sure: A1's `_is_trusted` exclusion.** The engineer gave a specific
reason (5c-twin would demand a twin of a body-less item) and I did not verify it.
**If that reason is wrong, the TCB column is still under-counting and TASK_082
only half-closed the blocker it was written for.**
