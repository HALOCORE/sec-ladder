# TASK_126 — can ANY input separate the four Rust rungs? The harm matrix's own validity.

**Role: research engineer.** ⚠ **Deliverable is a MEASUREMENT and a verdict, not
a pattern.** **Do not build a pattern. Do not add a catalogue row.**

Read `.tasks/PROTOCOL.md`, then this file, then **`RECAP.md` finding 43 in
full**, then **`.tasks/TASK_124_REPORT.md`'s census section** (the finding's
origin), then `.memory/02-bench-rules.md`'s adversarial-input rules.

Scratch in **`.temp/t126/`**.

---

## The question, and it is about the instrument rather than any row

**`TASK_124` ran the cheapest census in the project and found:**

```
129  adversarial (pattern, input) pairs in results/gate/*.json
 58  with ANY cell divergence
  0  where safe_naive / safe_tuned / unsafe / verus differ from ONE ANOTHER
```

**Every behavioural divergence in this tree is among the C variants.**
✅ **Manager-re-ran it; the zero is exact.**

⚠⚠ **Finding 43 records TWO readings and only the first has been used.**

1. ✅ **DEFENSIVE, and it already earned its keep:** a proposed row whose headline
   is *"R2 panics, R3 is correct, R4 is silently wrong"* is claiming something
   that has never happened here — **which is how `CVE-2021-23017` was refused.**
2. ⚠⚠ **UNTESTED, AND IT IS A CLAIM ABOUT THIS WHOLE BENCHMARK: a tree with 129
   adversarial pairs and ZERO Rust-rung divergences may be telling you THE HARM
   INPUTS ARE NOT ADVERSARIAL ENOUGH.** **If the harm matrix cannot separate the
   Rust rungs on ANY input, then that column is not measuring what its name
   says.**

## §A — ⚠⚠ THE DECIDING EXPERIMENT, AND IT IS CHEAP

> **Construct an input that makes two of `safe_naive` / `safe_tuned` / `unsafe` /
> `verus` DISAGREE OBSERVABLY on an EXISTING built pattern — or establish that
> the tree's structure forbids it.**

⚠ **You may NOT change any rung's source.** The point is whether the *inputs* are
weak, not whether a different program would differ.

**Two outcomes, both valuable, and say which BEFORE you start hunting:**

- ✅ **YOU FIND ONE.** **Then the harm matrix has a real gap, finding 43's second
  reading is right, and the fix is more adversarial inputs — cheap, and it would
  strengthen every pattern.** ⚠ **Report the input and the pattern; do NOT land
  it as a new committed blob in this task** (`inputs/gen.py` is
  measurement-hashed — see Constraints).
- ✅ **YOU CANNOT, AND THE REASON IS STRUCTURAL.** ⚠⚠ **Then say WHY, precisely,
  because the reason is the finding.** **The candidate explanation the manager
  believes — ⚠ and it is a guess, so attack it — is that the `identity` pin makes
  `unsafe == verus` BYTE-IDENTICAL by construction (26 of 26), which collapses
  two of the four rungs a priori; and that R2/R3 are pinned to the same
  `required` idiom, so they differ in SPELLING and not in SEMANTICS.** **If that
  is the reason, the honest statement is *the tree has TWO behavioural Rust
  rungs, not four*, and finding 43's zero is a TAUTOLOGY rather than a
  measurement.** ⚠⚠ **THAT WOULD BE A MUCH MORE IMPORTANT RESULT THAN THE
  CENSUS, AND IT WOULD PARTLY RETRACT FINDING 43. Do not soften it.**

**Where to hunt, if you hunt** — pick two or three, say why:

- ⚠ **`p04` (ring buffer)** — its bug is IN BOUNDS and *"both guards are
  invisible to a memory-safety proof"*, so the rungs might differ on a wrap.
- ⚠ **`p13`/`p16`** — truncation and TLV walking, where R2 and R3 take different
  code paths on a malformed length.
- ⚠ **`p03` and `p23`** — `TASK_125` measured that their *"N distinct
  behaviours"* notes line MOVES BETWEEN RUNS because **those cells read
  uninitialised memory**. ⚠⚠ **NONDETERMINISM IS NOT DIVERGENCE — but a cell
  printing garbage is the most likely place for an apparent divergence, so
  check it and rule it out explicitly.**

## §B — ⚠ CHECK THE CENSUS ITSELF BEFORE BUILDING ON IT

**Three ways the zero could be an artefact of the CENSUS rather than of the
tree. Rule each out or report it:**

1. ⚠⚠ **Does the gate RECORD what it would take to see a divergence?** The census
   compares `(exit, stdout, signal)`. **If two rungs differ only in `stderr`, or
   in a value the driver folds into a checksum, the record cannot show it.**
   **Read `check.py`'s adversarial stage and say what it captures.**
2. ⚠ **Are all four rungs actually RUN on every adversarial input?** **If some
   pattern runs only C variants adversarially, its inputs contribute zero
   Rust rows and inflate the denominator.** **Count the rows per rung.**
3. ⚠ **`skipped_inputs`** — a gate record has that key. **Are adversarial inputs
   being skipped anywhere, and does the census see the skip?**

## §C — the cheap clean negative that is worth having regardless

**Count, per pattern, how many adversarial inputs exist and how many produce ANY
divergence at all.** ⚠ **If a pattern has adversarial inputs on which NOTHING
diverges — not even the C variants — those inputs are doing no work and the
pattern's harm column is thinner than it looks.** ✅ **That is a per-pattern
quality number nobody has computed, and it is one pass over committed records.**

---

## Constraints

- **`.temp/t126/` only. No `/tmp`.** **Notes in `.temp/t126/NOTES.md` AS YOU GO.**
  Keep the generator, delete the artefact.
- **No `git add` / `git commit`.** Read-only git is fine.
- ⚠ **Do not edit `.memory/`, `RECAP.md`, `results/SYNTHESIS.md`.**
  ⚠⚠ **`results/synthesis.md` (lower case) is GENERATED — never hand-edit it.**
- ⚠⚠ **DO NOT EDIT ANY `patterns/*/{*.rs,c/*,model.py,inputs/gen.py}`** — all
  measurement-hashed, and a re-measure is not in this budget. **So: generate
  candidate inputs into `.temp/t126/` and run the EXISTING binaries against them
  by hand.** ⚠ **If you find a separating input, REPORT IT; landing it is a
  separate task that pays for the re-measure.**
- ✅ **You MAY run `harness/build.py` to get binaries** and read anything.
  ⚠ **`harness/check.py` is not needed and would cost a sweep — do not run it
  unless you explain why.**
- Hand-run ASan needs `env -u LD_PRELOAD`; ⚠ **never truncate a sanitiser log
  with `head`.**
- ⚠ **Every probe needs an arm that MUST FIRE.** **Read the failure-class list at
  the end of `.memory/03-measurement.md` — ⚠ it carries no usable count.**
  ⚠⚠ **In THIS task the must-fire arm is unusually important and unusually easy:
  plant a divergence you KNOW exists (a C variant against a Rust one) and show
  your comparison SEES it. A hunt that finds nothing is worthless unless you have
  proved the detector works.**
- ⚠ **Gate records are NOT byte-reproducible** (`.memory/03-measurement.md`):
  diff them modulo sanitizer strings, `miri.runs[].seconds`, adversarial group
  order, and the `N distinct behaviours` notes line.
- `timeout <N> <cmd>`; never `pkill`/`killall`.

Write your report to `.tasks/TASK_126_REPORT.md` as well as returning it.

---

⚠ **PROTOCOL rule 2's running count is 583** (`TASK_125` carried 551 → 566;
⚠ **a rigour signal, not a ledger — do not re-add it**). The calls I am least
sure of:

1. ⚠⚠ **That the `identity` pin explanation is right.** **It is the manager's
   guess and the manager's guesses on this class have been wrong repeatedly this
   week — most recently mapping a CVE onto `p12`, refuted by one census.**
   **If `unsafe` and `verus` are byte-identical by pin, the census was comparing
   three things and calling them four, and I want that stated plainly if true.**
2. ⚠ **That a separating input would be a GOOD result.** **It would mean the harm
   matrix has a gap — but it would also mean 26 patterns shipped with inputs that
   under-test them, which is a large retroactive claim.** ⚠ **Do not inflate a
   single find into that claim; one input on one pattern is one input on one
   pattern.**
3. ⚠⚠ **That this is worth a task at all rather than a footnote.** **The census
   is already doing useful defensive work as it stands.** ⚠ **The argument FOR is
   that finding 43 is currently published with two readings and only one tested,
   which is exactly the shape (*"a claim with an untested alternative reading"*)
   that killed findings 37, 40 and 41.** **If you think that argument is thin,
   say so and close it in one page.**

Carry **583** forward, incremented by what you find.
