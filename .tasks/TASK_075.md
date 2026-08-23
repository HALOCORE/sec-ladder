# TASK_075 — the cross-pattern synthesis, and the column it cannot trust

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then **`.tasks/TASK_074.md`'s outcome
block** (p48 was refused and its recommendation is why this task exists), then
`.memory/03-measurement.md` — ⚠ **specifically the section *"The kernel-exclusive
column is comparable only when the rungs call the SAME libc routines"* and its
TASK_073 widening**, then `.memory/01-ladder.md` **findings 9 (p11), 14 (p13),
18 (p10) and 23 (p36)**, then `RECAP.md`'s **"Owed" items 13 and 21**.

**This is the project's stated purpose and it has no artefact.** `CLAUDE.md`
describes patterns *"compared on assembly, instruction count, timing, proof
burden and trusted-base size"*. There are **22 per-pattern tables** under
`results/tables/` and **nothing that compares them**. A working probe exists at
**`.temp/synth/aggregate.py`** — it reads only committed records, runs in
seconds, and needs no measurement.

⚠⚠ **PROTOCOL rule 5 (*prefer producing a pattern over hardening the gate*) is
being OVERRIDDEN to run this, deliberately, by the manager.** The standard is
TASK_068's: *fixes to **measured** defects, not speculative hardening*. **If you
think the override is wrong, say so** — it is the manager's call and the manager
has been wrong four times in the last five task files.

## The argument that scheduled this, and your first job is to attack it

From p48's refusal, **PROVISIONAL and unreviewed**:

> `.temp/synth/aggregate.py` reads **`kernel_exclusive_ir`**, and its headline
> provisional finding is *"`R3 − R4` is NEGATIVE on 5 of 20 patterns"* — p10, p11
> (**−5768 / −24503**, the largest magnitude in the table), p12, p13
> (−177 / −1054), p18. ⚠ **p11 and p13 are precisely the two patterns whose
> `.memory/` entries ALREADY SAY their rungs dispatch different work outward** —
> p11's whole finding is a **12.0× library factor** between `strlen` spellings,
> and **p13 is the pattern that ESTABLISHED the rule**. **So the project's only
> synthesis artefact rests, at its two biggest numbers, on the column the tree
> has now caught reversing a comparison three times** (p13 by 190/264; p36, where
> a `match` control flipped from dearer to cheaper *and the false direction was
> quoted inside a hashed `idiom.why`*; p48's probe, where the tax reads **exactly
> zero**).

**Attack it.** It is one agent's reading of a probe nobody has reviewed. **If
`R3 − R4` on those five is fine, or fine for a reason this misses, say so with
the measurement and the task gets smaller.**

## §0 — decide what the fix IS before building it

⚠ **The manager does NOT know the answer here and the p48 report's prescription
(*"add the callee/total column, then synthesise — the order is a dependency"*)
may be the expensive way round.** Three candidates:

- **(a) A recorded column.** `results/*.json` carries callee / whole-program `Ir`
  beside `kernel_exclusive_ir`. ⚠ **Cost, and settle it before recommending
  it: can the column be BACK-FILLED, or does populating it need a re-measure of
  all 22 patterns?** A full re-measure churns every published wall-clock row and
  is the project's single most expensive operation (RECAP settled answer 4). ⚠
  **And `measure.py` sits in the gate's `harness/*.py` glob**, so editing it
  stales **every** gate record for a file the gate never executes (RECAP "Owed"
  5 calls that glob over-broad).
- **(b) An on-demand analysis tool** that computes callee `Ir` from a rebuild
  when asked, recorded nowhere.
- **(c) ⚠ A STATIC LICENCE CHECK, which the manager suspects is the right answer
  and has not verified.** The rule is *"is the outward-dispatched work equal
  across the cells being differenced?"* — and that is answerable from the
  **disassembly**, not from a run. `harness/asm.py` already disassembles and
  `bulk_calls` already exists. **A per-pattern verdict — `kernel column
  LICENSED` / `NOT LICENSED, and here is what differs` — would say which of the
  synthesis's rows are quotable at zero measurement cost.**

> **Pick one, argue it, and say what it cannot do.** ⚠ **Whichever you pick, do
> NOT edit `harness/` in this task** — there is a five-item batch queued and the
> next task lands it; **your §0 answer is what that task will be designed
> against, which is the real reason this ordering was chosen.** A prototype under
> `.temp/` is expected; a `harness/` edit is not.
> ⚠ **(c) has a known blind spot to check: p36's callees were PROJECT-LOCAL**, so
> a check that lists only `@plt`/`@GLIBC` targets reproduces the exact miss that
> caused this. And a devirtualised `match` calls **nothing** — absence of a call
> is the hazard, not presence of a different one.

## The synthesis itself — what it must and must not say

**Where it lives.** ⚠ **NOT `harness/`** (the `harness/*.py` glob stales all 22
gates) and **NOT `common/` or `common/layout/`** (hashed into `source_sha256`).
**Verify what is hashed before choosing** — `check.py::main` is the authority —
and put it somewhere a new file cannot stale a record. Say where and why.

**Three things the probe already exposes, all PROVISIONAL, none reviewed — treat
each as a claim to test, not a result to publish:**

1. **`R5 − R4 = 0.00` on all rows, both inputs, every pattern.** The
   `identity: exact` invariant visible whole for the first time. ⚠ **p36 is
   `norel`, not `exact` — check whether that breaks the row or explains it.**
2. **`R3 − R4` negative on 5 of 20** — the claim above. ⚠ **Several of those
   patterns have an UNSEARCHED R4 side** (the trap in RECAP's START HERE box),
   so the sign may be an artefact of R4's spelling. **What the aggregate
   genuinely adds is making that a SYSTEMATIC problem rather than a per-pattern
   footnote — say it that way.**
3. ⚠ **A cross-pattern `Ir` comparison is available in `isolated` mode ONLY**:
   of 318 `-O3` cell/input pairs, `whole` mode has `kernel_exclusive_ir = None`
   in **302**. And **p10 showed regressors SWAP between modes**. **State that
   limit BEFORE the first number, not after the table.**

**And the standing rules that govern every figure in it:**

- **Never the word "minimum"** — *"cheapest found"*, **naming the input**,
  because on p03 and p16 the cheapest spelling changes with the blob.
- **No pair interval** unless the pattern has an admissible R4 that MOVES; p03
  and p36 do, and both published ones before that were built from rungs that do
  not exist.
- **A law owes its DOMAIN.** ⚠ **New and PROVISIONAL** (`.memory/03-measurement.md`):
  glibc's `rep stosb` threshold at `n ≈ 2048` makes `Ir` report a cost **rising
  6.5× at exactly the size the real cost falls** — so a fit banded below it
  extrapolates into a different regime with no in-sample residual to warn you.
  **If any synthesis row crosses a size threshold, say so.**
- ⚠ **gcc defaults to `-fcf-protection=full`**, so every gcc column carries
  `endbr64` landing pads the others do not — `1.00000·nrw + 1` `Ir` per call on
  p36. **Any cross-pattern gcc-vs-clang statement must name it.**

## Done when

§0's decision is written with its argument and a `.temp/` prototype; the
synthesis exists at a location you justify, runs from committed records only,
and **states its licence per row**; the three provisional claims are each
confirmed, refuted or scoped; and **the `harness/` work it implies is REPORTED,
not built**. `measure.py --check-stale` clean and **no record moved** — this task
should touch no measurement at all. **Paste actual output.**

## Constraints

No root; no `/tmp` (scratch `.temp/p75/`; ⚠ **`ls` any scratch path before
writing to it — `.temp/pNN/` collides between patterns and tasks, and
`.temp/p48/` is TASK_048's evidence**; `.temp/synth/` is readable, **treat it as
read-only**); **no `git add`/`git commit`**; do not edit `pilot/`, `.memory/`,
`harness/`, `common/`, or **any** pattern. clang `~/tools/llvm/bin/clang`, gcc
`/usr/bin/gcc`, valgrind `~/tools/valgrind/bin/valgrind`, rustc
`~/.cargo/bin/rustc` — **none but gcc on PATH**. `timeout <N> <cmd>`. Never
`pkill`/`killall`; **no `nohup … &`**; **no self-matching `pgrep` wait-loops.**
**You are the only agent running.**

Notes to `.temp/p75/NOTES.md` as you go.

**If a prescription here is wrong, say so with the measurement.** ⚠ **Running
count 170**, and **five of the last ten entries are manager errors** — including
*"the six original axes are complete"*, written into the handoff document one
commit before an agent counted the table and found five of seven.

**What I am least sure of, by name: §0's choice, and specifically whether (c)
the static licence check is sufficient.** A licence says *"this row is
quotable"*; it does not say *what the number would be* if you corrected it, and
p13's correction (190/264 of ~1100) and p36's (a reversal) were both worth
knowing. **If a licence alone leaves the synthesis unable to state its most
interesting rows, say so and argue for (a) or (b) with the re-measure cost
attached.**

**Second, unnamed by the p48 report and possibly more important: is `R3 − R4`
the right cross-pattern quantity at all?** It differences two rungs whose
spellings are searched to wildly different depths across the 22 patterns — p47
searched six R4 levers, p36 four R3 and three R4, p01 and p08 owe an R3-side
span entirely. **A table that puts a well-searched pattern beside an unsearched
one and differences both may be measuring search effort.** ⚠ **If that is
right, the synthesis's first column should be the LEVER COUNT, and the manager
did not think of that until writing this sentence.**
