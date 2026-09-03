# TASK_171 — the closing review: `TASK_170`, the manager's fold, AND the retirement

**Role: research reviewer.** Adversarial by design. **You do not fix; you
report.** A review that agrees without having tried to break something is a
failed review.

⚠⚠⚠ **THIS IS THE LAST STRUCTURED TASK IN THE PROGRAMME, WHICH IS EXACTLY WHY
IT MATTERS MOST.** Everything downstream of it is what a reader sees:
`results/SYNTHESIS.md` is now the finished argument, the queue is closed, and
the backlog is retired **as stated limitations**. **If a claim in any of that is
wrong, nothing after this will catch it.**

⚠⚠ **THE PRECEDENT IS THREE FOR THREE.** `TASK_165`, `TASK_167` and `TASK_169`
each found a `✅ manager-re-derived` mark the manager had not earned — the last
found **three in one bullet**. **Assume a fourth exists.**

Read first: `.tasks/TASK_170_REPORT.md` **in full**;
`git show d6aa844` and `git show 87baad7` (**the manager's two folds — read the
diffs, not the files**); `RECAP.md` **finding 66** and the START HERE box;
`results/SYNTHESIS.md` §1, §2, §7 (**especially the new *"What is deliberately
NOT done"* subsection**); `.temp/mgr164/QUEUE_TRIAGE.md`.

✅ **NO SWEEP, NO RE-MEASURE, NO CALLGRIND RUN IS NEEDED FOR ANY ITEM.**
⚠ **If you believe one is, say so and STOP.**

✅ **Pre-settled by the manager — do not spend the review re-deriving these:**
the tree is `30 PASS + 3 PASS-WITH-BLOCKED-ROWS`, 0 failures, `blocked` `p01` 1
/ `p35` 3 / `p42` 1; the search-state column now reads `undeclared` on **zero of
33**; `composition.py --check`, `temp_citations.py` and `--check-stale` are all
`rc=0`.

---

## 1. ⚠⚠⚠ THE `§` REGIME CENSUS — its first spelling gave the flattering answer

`synthesize.py::regime_crossing` marks a row when a bulk routine contributes
**asymmetrically across the pair by ≥ 2.00 `Ir`** *and* **one side is in the
byte-wise regime**. It marks **`p08 gcc-clang` (both blobs)** and
**`p42 large R2−R4`**.

- ⚠⚠ **The engineer disclosed that its FIRST spelling found `p42` and nothing
  else — the flattering answer — because glibc's routines carry no symbol in
  `outward_ir.json` and a name regex misses every one.** ✅ **That disclosure is
  the good half. Now attack the SECOND spelling: what does IT miss?** An
  inlined `rep` (no callee edge at all); a routine reached through a PLT thunk;
  a pair where **both** sides are byte-wise (asymmetry ≈ 0, so no mark — **is
  that right, or is a symmetric byte-wise pair also incomparable?**); a
  contribution just under 2.00.
- ⚠⚠⚠ **AND SETTLE THE DISAGREEMENT THE MANAGER RECORDED AS OPEN:**
  `TASK_169` claimed **`p27 gcc-clang`** carries gcc's 32-`Ir` `rep stos`
  against clang's 19-`Ir` vector spelling — *"over half its magnitude"* of a
  `LICENSED` published row. **`TASK_170`'s census does NOT mark it.** **One of
  the two is wrong, or the threshold is. Which?**
- ⚠ **`p08 gcc-clang` is a row this document has published since its first
  version.** **Does marking it change anything §2 or §7 says about `p08`?**
  `p08` is also the pattern `.memory/` names as the original `Ir`-vs-`ns`
  direction disagreement — **check the two accounts are consistent.**

## 2. ⚠⚠ THE BUILD-DETERMINANT PIN — `0 of 33`, and a revert that was one call away

The engineer refuted the manager's pin **and** its replacement, landing a third:
pin the **build determinants**, `0 of 33` STALE, **at no callgrind cost** because
the old key was never one hash but the whole `path → sha256` map.

- ✅ **Re-derive the `0 of 33`**, and ⚠ **re-derive the claim that `--emit` no
  longer silently reverts the re-pin** — that is rule 6's artefact-vs-generator
  skew, which this project has shipped **three times**.
- ⚠⚠ **Attack `is_build_determinant` itself.** What decides a determinant? **Is
  the set complete** — does it include everything `measure.py` builds from, and
  exclude everything it does not? **A pin that is too narrow reads FRESH when
  the numbers are wrong, which is worse than the false STALE it replaced.**
- ⚠ **The values in the sidecar are `TASK_166`'s and were NOT re-emitted.**
  **Confirm the re-pin did not change a single measured value.**

## 3. ⚠⚠⚠ THE 14 SEARCH-STATE ENTRIES — the largest claim in the fold

**`undeclared` was 100% bookkeeping, at 26 and at 33: 14 / 0 / 0.** The manager
has published that in `results/SYNTHESIS.md` §7 **and** rewritten §2's
cross-reference around it.

- ⚠⚠ **Each of the 14 entries must cite a REVIEWED artefact**, the way the
  original twelve do. **Check every one against the `NOTES.md` or report it
  names.** **An entry that overstates what its row actually searched is worse
  than the `undeclared` it replaced**, because `undeclared` was at least honest
  about being a bookkeeping state.
- ⚠⚠⚠ **AND CHECK THE FOUR THE MANAGER PROMOTED INTO THE PUBLISHED PROSE**:
  `p16`'s `R3 − R4` *"flips sign, `+27/+77 → −199/−2545`"*; `p09`'s *"65× R3-side
  span"*; `p14` *"overstates the safe side by 88.9% on `large`"*; `p42`'s *"sign
  flipped and the cheaper rung WAS shipped"*. **Those are now published
  numbers and the manager did not re-derive any of them.**
- ⚠ **`p42`'s entry says BOTH sides were searched TWICE and the sign flipped —
  and `p42` is also the row carrying the new `§` marker.** **Are those two
  statements about the same cells?**

## 4. ⚠⚠ THE RETIREMENT — `git show 87baad7`

`results/SYNTHESIS.md` §7 now carries *"What is deliberately NOT done, and what
each omission costs a reader"* — five headings, eleven retired items.

- ⚠⚠⚠ **THE CLAIM MOST LIKELY TO BE WRONG IS THE REFRAMING.** The manager
  **withdrew** *"not every rung's cheapest admissible spelling has been
  searched"* and replaced it with *"four named levers are untried, and the
  per-row search state is documented on all 33"*. ⚠ **Is that reframing
  honest, or is it the flattering direction?** **A documented search is not an
  exhaustive one**, and several of the 14 entries say so in their own text
  (*"the R4 side is explicitly UNsearched"*). **Settle it.**
- ⚠ **The count in that subsection was DERIVED after the manager caught itself
  inventing one** (the first version said *"43 items, 25 closed, 18 retired"*).
  **Re-derive: 44 numbered items, 16 closed with a run, 1 investigated, 11
  retired.** **Check every membership list.**
- ⚠ **Each of the eleven retired items must carry enough for a reader to pick it
  up.** **Is any retired with a reason that is itself unverified?** — this
  project's own record is that *a refusal's REASON is what gets reused*, and
  that **three of four refusal reasons ever checked did not survive.**

## 5. ⚠⚠⚠ WHAT THE MANAGER OVERSTATED — mandatory, and it is where the last three reviews scored

Landed from an unreviewed report, same day: **`RECAP` finding 66** and its
`✅`/`⊘` marks; the START HERE box's rewrite; `PROTOCOL` rule 6's new *"loud is
rendered"* paragraph; `results/SYNTHESIS.md` §1's `p08` paragraph and §7's two
rewrites; the two commit messages `d6aa844` and `87baad7`.

⚠ **In particular the manager marked `✅` on:** the gate verdicts; *"the column
now reads `undeclared` on ZERO of 33"*; and the `§` census being *"DERIVED, not
listed"*. **Check each was actually run.**

## 6. ⚠ ITEM 43's ACCUSATION NEEDS A RUN BEHIND IT

`TASK_170` reports that `asm.py`'s `main` needle **masks a real stage-3a failure
on `p01 safe_tuned -O0 isolated`** and that **`p05/NOTES.md` §1a invented a
mechanism** for the artefact. ⚠⚠ **The second is an accusation against a shipped
pattern doc and it is now retired into `results/SYNTHESIS.md` as a stated
limitation.** **Verify both, or say they are unverified.** ⚠ **Do NOT touch
`asm.py`** — it is measurement-hashed.

## Deliverables

1. **Per item: `SURVIVES` / `FALLS` / `SURVIVES, NARROWED`**, with the run.
2. ⚠⚠ **A verdict on the `p27` disagreement** (item 1) — `TASK_169` says the row
   is contaminated, `TASK_170`'s census does not mark it.
3. ⚠⚠ **A verdict on the retirement's reframing** (item 4) — honest, or
   flattering?
4. ✅ **CLEAN NEGATIVES, NAMED.** Earlier reviews left ten, fifteen and
   twenty-one; **do not repeat any of them.**
5. ⚠⚠⚠ **AND THE CLOSING QUESTION, WHICH ONLY THIS REVIEW CAN ANSWER: is
   `results/SYNTHESIS.md` SAFE TO PUBLISH?** Not *"is it current"* — **is there
   a sentence in it a reader would act on that no artefact backs?**

## ⚠ NOT in this task

- **Any fix.** You report; the manager lands.
- **A sweep, a re-measure, or a re-emit of `outward_ir.json`.**
- **`harness/asm.py`.**

## Rules

- `.temp/t171/` for scratch. ⚠ **Do not modify any earlier `.temp/t*/` or
  `.temp/mgr*/`**; copy out. **No `git add`/`git commit`.**
- ⚠⚠ **DO NOT LEAVE A `pgrep -f` WAITER RUNNING** — a waiter's own command line
  contains the string it greps for. **Use `wait <pid>` or a `.done` sentinel.**
- ⚠⚠ **Read `blocked`/`verdict` out of the RECORD, never `grep` the log**, and
  ⚠ **`rc=$?` after a PIPE reads the LAST command's status.**
- Verus via `./verus_run.py`, single-file mode, never `--cargo`.
- Hand-run sanitisers need `env -u LD_PRELOAD`; never truncate with `head`.
- ⚠ **If you plant into a tracked file, restore in a `finally:` and verify by
  BYTES against `git show HEAD:`.**
- Report to `.tasks/TASK_171_REPORT.md`. **Write the file before citing it.**

**PROTOCOL rule 2 running count: launched from 948**
(`.tasks/TASK_169_REPORT.md`; `TASK_170` refuted the manager's `outward_ir` pin,
its replacement, item F's cost, the *"6 `RECAP` citations"* figure and the
`§`-census's first spelling). ⚠ **Reconciliation is the manager's job.**

⚠⚠ **The one I want attacked by name is item 4's reframing. I withdrew *"not
every rung's cheapest spelling has been searched"* on the strength of
`TASK_170`'s 14/0/0 — and 14/0/0 says every row's search state is DOCUMENTED,
which is not the same claim at all. If I have quietly converted a limitation
into a boast, that is the single most damaging thing in this session's output,
because it is the sentence a reader takes away.**
