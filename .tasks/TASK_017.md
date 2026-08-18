# TASK_017 — say what the idiom key actually does, and fix three declarations

**Role:** research engineer
**Read first:** `.tasks/PROTOCOL.md`, then `.tasks/TASK_016_REVIEW_REPORT.md`
in full — **B1, M1, M2, M3 and the Part 5 adjudication are the whole of this
task** — plus `.memory/06-catalogue.md`'s first open cross-cutting issue and
`.memory/03-measurement.md`'s two-conventions section, both already corrected.

This is repair, not design. Everything here has been measured and adjudicated;
none of it is open.

## Part 1 — the false mechanism sentence

`harness/check.py:564-566` (and `TASK_016.md:61-63`) claim *"changing a rung's
idiom must move `contract_sha256`"*. **It must not**, and the review proved it by
experiment: a p05 fork with `safe_tuned.rs` swapped for the **forbidden**
`chunks_exact` variant gate-passes with `contract_sha256` byte-identical,
certifying `R3 − R4 = −12/−58` as green p05.

Replace it with what is true, in the docstring and anywhere else it appears:

- the key makes the declaration **required, visible in the verdict, and hashed**,
  so **weakening or editing the declaration** moves `contract_sha256`;
- **rung sources are covered by `source_sha256`**, not by this key;
- **nothing here prevents a forbidden respelling**, and nothing can without
  semantic checking, which the threat model forbids.

Do not "fix" it by adding a semantic check. If you think the key is not worth
keeping given what it actually does, **say so with the argument** — that is a
live option and I would rather hear it than have the key kept out of momentum.

## Part 2 — the one change that would have helped, if it is cheap

The failure was people **quoting p05's number without reading `spec.md`**.
`report.py` prints no `idiom` at all, so `results/tables/*.md` — the artefact a
writeup reads from — carries no trace of what a pattern forbids.

**Print each pattern's `forbidden` list in its results table**, and in
`check.py`'s failure summary as well as its verdict. You are authorised to touch
`harness/report.py` for this and nothing else. If it turns out not to be cheap,
report that and skip it rather than growing the change.

## Part 3 — three declaration defects

1. **p16's hashed block contradicts itself.** `spec.md:269` requires
   `end - p >= 3` and `vlen > end - (p+3)` "in every rung"; `:278` asserts
   `split_first_chunk::<3>()` is admissible, and that variant
   (`.temp/p05r3/v16/tuned_split.rs:14-16`) contains **neither** comparison.
   **Disambiguate `required[0]`** — decide whether it names *tokens* or a
   *semantic property* (no additive comparison), and say which in the `why`.
   **Whichever you choose, do not choose it by which answer makes the cheaper
   spelling inadmissible**: a `forbidden` entry picked after seeing which
   spelling is cheaper is self-certification in its purest form, and the review
   was explicit that declining to add one was right.
2. **p02's `required[0]` and `[3]` are false of its own R1** (`c/kernel.c:28-31`
   has no fit check and is not total in `len` — *that is the bug the pattern
   models*). p16 (`spec.md:272`) and p17 (`spec.md:385`) both carve R1 out; p02,
   retrofitted the same day, does not. Carve it out the same way.
3. **p05's retrofit dropped a bullet** — "`nrow * ncol` is folded into the
   result" (`spec.md:83-85`), which p16 and p17 both kept. Restore it.

Also noted at review and worth doing while you are here: the retrofit
**duplicated** the prose into the JSON rather than moving it
(`git show 4bd7deb -- patterns/*/spec.md` is +0/−0 on prose), so each pattern now
states its idiom twice and the two copies can drift. Either make the prose point
at the block or delete the duplicate — your call, argued in the report.

## Part 4 — state the R3 limitation on p16 and p17

Adjudicated at review: **state it, swap neither cell.** p17's cheaper spelling is
admissible but also beats **its own R4** by 19.00, so swapping R3 alone
re-commits the unmatched-pair defect as a shipped cell, and `inf(R4) <= inf(R3)`
means no swap terminates. p16's premise is broken until Part 3.1 lands.

One paragraph in each `NOTES.md`, next to the R3 number: the shipped R3 is **not
the cheapest admissible spelling**, here is the cheaper one and its delta, and
here is why it is not shipped. p16's paragraph must be written **after**
Part 3.1, and must be consistent with whichever reading you chose.

## Part 5 — gate re-runs

`harness/check.py` is inside `source_sha256`, so **any** edit to it invalidates
all six records. Re-run all six to green. **The invariant from TASK_016 must hold
again: every `md5_fn` unchanged and every `marginal_ir_per_call` cell unchanged**
— no cell source changes in this task. `contract_sha256` moves only for the
patterns whose `spec.md` you edit (p02, p05, p16, and p17 if Part 4 touches its
block).

Order matters and cost an hour last time: **all prose edits first, gates last.**
`source_sha256` globs `patterns/*.md`, so any `NOTES.md` edit after a run
staleness that record.

## Done when

The false sentence is gone everywhere it appears; the three declarations are
fixed; the duplication is resolved one way or the other; p16's and p17's
`NOTES.md` state the R3 limitation; all six gates green with the invariant
confirmed; Part 2 done or explicitly skipped with a reason. Report the total
`harness/` diff size.

## Constraints

No root; no `/tmp` (scratch `.temp/p17fix/`); **no `git add`/`git commit`**; do
not edit `pilot/` or `.memory/` (report durable facts; I land them). You may edit
`harness/check.py` and `harness/report.py` **only**. No cell source may change —
if you believe one must, stop and report. Verus only via `./verus_run.py`. clang
`~/tools/llvm/bin/clang`, valgrind `~/tools/valgrind/bin/valgrind`, rustc
`~/.cargo/bin/rustc` — none on PATH. `timeout <N> <cmd>`. Check `git status`
before finishing.

Notes to `.temp/p17fix/NOTES.md` as you go.

**If a prescription here is wrong, say so with the measurement.** Nineteen agents
have contradicted my written instructions and all nineteen were right; the last
one disproved a mechanism I had just shipped and had described in three files.
The thing I am least sure of here is **Part 1's final question** — whether a key
that cannot prevent what it was built to prevent earns its 145 lines. I lean
keep, because a hashed declaration a reviewer can diff is worth more than prose
at line 69 was. I am not confident, and a well-argued "delete it" is a perfectly
acceptable deliverable.
