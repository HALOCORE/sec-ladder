# TASK_020 — make the audit reproducible from the tree

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then `.temp/p19/NOTES.md` (the audit and
its recommendations), `.tasks/TASK_018_REVIEW_REPORT.md`, and
`.memory/01-ladder.md`'s named-spelling-standard block, which now carries the
direction test.

## Part 1 — the reporting line, and why I was wrong to forbid it

TASK_019 measured **20 raw / 15 comment-stripped / 9 normalised** violations of
the six declarations, and repaired them to **0 of 82**. But that audit lives in a
hand-transcribed table in **gitignored** `.temp/p19/pins.py`, so **"0 of 82" is a
claim nothing in the tree reproduces.** That is precisely the trap `RECAP.md`
lists as recurring: *declared pins are self-certifying*.

I forbade semantic checking on the ground that a grep-the-rungs check fails open.
**That was the right objection to the wrong proposal.** A **reporting-only,
never-failing** line is not a check that can fail open — it is an observation
printed into the record, where a reviewer can read it. The "could this happen by
accident?" test passes trivially: **it happened twenty times.**

Build it:

- Stage `0b` emits, per pattern, `N spellings × M rungs, K matched`, and **lists
  every miss** with the spelling, the rung and the language.
- It goes into `results/gate/<pattern>.json` so the count is a committed artefact
  and a diff shows when it moves.
- **It never fails and never blocks.** Not a `shout` either if that would read as
  an error; this is data. Use `check.spelling_matches` — the matching rule
  TASK_019 already defined and selftested.
- Scope: which rungs an entry applies to is currently English prose in each
  entry. **Do not invent a scope language.** Apply each entry to every rung of
  the languages it declares, report the misses, and let the reader judge — a
  miss with a reason beside it is worth more than a scope DSL nobody can check.
  If that produces false positives, **print them and say they are expected**; the
  hardened-C comment cases in TASK_019's notes are the model.

Expect the line to be non-zero on some patterns for honest reasons. **That is
fine and is the point** — a visible, explained non-zero beats an invisible zero.

## Part 2 — two corrections that need the same gate runs

1. **`harness/check.py:~873` quotes the p08 environment interval as
   `7292.14 … 7292.30`, and *both* endpoints are unreproduced.** Two independent
   probes give a union of `7292.10 … 7292.22`, and TASK_019 measured the scatter
   as scatter, not trend. Requote it from measurement, or drop the numeric
   interval and describe the effect qualitatively.
2. **A marginal `Ir`/call is exact only within one build and one session.**
   TASK_019 found a *second* non-cancelling term, distinct from the environment
   block: the same source at two build paths gives 10210.82 vs 10210.84 with a
   **byte-identical kernel** (`md5_fn e207ec6c…`, `kernel` self-cost 9783.00 in
   both) — the whole delta is in libc's AVX `memmove`, from 64 bytes of path
   length changing heap alignment. Write that into `patterns/p02-buffer-copy/NOTES.md`
   beside its marginals, and report it for `.memory/03-measurement.md`.

## Part 3 — p16 sweep inputs for the `nrec` axis

p16's §10a now rests on swept `nrec` laws (11 values × 2 residues, zero residual)
whose **only inputs are 22 gitignored files**. p16's committed `SWEEP_BANDS` has
both bands at `nrec` 2 and 4, so the tree cannot reproduce its own load-bearing
statement. Add a third band — roughly 11 blobs — so it can. This moves
`inputs_checked` and p16's gate record; that is expected.

## Part 4 — p05's in-contract spelling spread, if the session allows

p02, p16 and p17 have one; **p05 does not**, and p05's `6·nrow + 9` is quoted in
`.memory/01-ladder.md` finding 6 as though it were the number. Until p05 has a
spread it is an upper bound with **no measured floor** — the same state p16's
`+27/+77` was in before TASK_018.

Use the §10a shape. Remember p05's declaration forbids `chunks_exact` and the
running row pointer, so the variants must be **in contract** — that is the whole
point, and it is the constraint two earlier tasks violated.

**Drop this part if time runs short and say so.** Parts 1–3 are the priority.

## Done when

The reporting line ships and its count appears in all six gate records; the two
corrections land; p16 can reproduce its own `nrec` laws from committed inputs;
all six gates green; `md5_fn` unchanged 28/28. Paste the reporting line's output
for all six.

Prose first, gates last.

## Constraints

No root; no `/tmp` (scratch `.temp/p20/`); **no `git add`/`git commit`**; do not
edit `pilot/` or `.memory/`. You may edit `harness/check.py` and
`harness/report.py`, and `patterns/p16-tlv-walk/inputs/gen.py` for Part 3 —
nothing else in `harness/`, and **no cell source may change**. Verus only via
`./verus_run.py`. clang `~/tools/llvm/bin/clang`, valgrind
`~/tools/valgrind/bin/valgrind`, rustc `~/.cargo/bin/rustc` — none on PATH.
`timeout <N> <cmd>`. Check `git status` before finishing.

Notes to `.temp/p20/NOTES.md` as you go.

**If a prescription here is wrong, say so with the measurement.** Twenty-four
agents have contradicted my written instructions and all twenty-four were right;
the last one replaced a safeguard I had written with a better one and proved my
violation count was less than half the real figure. What I am least sure of here
is **Part 1's scope decision** — applying every entry to every rung of its
declared languages will produce misses that are not defects, and if the noise
swamps the signal the line teaches a reader to ignore it, which is worse than not
having it. If you find that, say so and propose the smallest thing that fixes it.
