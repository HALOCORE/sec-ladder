# TASK_167 — review `TASK_166` AND the manager's `SYNTHESIS.md` fold, and attack the FOLD first

**Role: research reviewer.** Adversarial by design. **You do not fix; you
report.** A review that agrees without having tried to break something is a
failed review.

⚠⚠⚠ **THE FOLD IS THE PRIORITY, NOT THE PACK.** `TASK_166`'s numbers came with
their runs. **The manager then rewrote `results/SYNTHESIS.md` — 246 insertions
across seven sections, hand-written, unreviewed — and every number in it is
QUOTED FROM `TASK_166_REPORT.md` RATHER THAN RE-DERIVED.** `PROTOCOL` rule 3
forbids the manager clearing its own design, and rule 9's whole point is that
`.memory/` gained **three new sections from an unreviewed report**.

⚠⚠ **THE PRECEDENT IS EXACT AND IT WORKED.** `TASK_165` reviewed `TASK_164`
*plus* the manager's fold and found, **in the fold**, a sentence marked
`✅ manager-re-derived` that **contradicted the table eight lines above it**.
**Assume the same here.**

Read first: `.tasks/TASK_166_REPORT.md` **in full**; `.tasks/TASK_166.md`;
`git show 7b5822a` (**the fold — read the diff, not the file**);
`git show 6f5674f` (the pack + the `.memory/` additions);
`results/SYNTHESIS.md` §§0–5, §6 trap 1, §7; `RECAP.md` **finding 64**;
`.memory/03-measurement.md`'s three newest sections and entry **23**;
`.temp/mgr164/NOTES.md`.

✅ **NO SWEEP IS NEEDED FOR ANY ITEM HERE.** ⚠ **If you believe one is, say so
and STOP; do not start one.**

---

## 1. ⚠⚠⚠ THE FOLD — every number in `SYNTHESIS.md` that moved

`git show 7b5822a` is the whole surface. **Re-derive, do not re-read.** The
manager applied every substitution by a script that asserted its own count, so
*"the edit landed where it was aimed"* is established; **what is NOT established
is that the numbers are right or that the prose around them survives them.**

Specific claims to attack, each of which the manager typed rather than computed:

- **§1** — `28 exact / 5 norel`; `30 PASS + 3 PWBR`; `66 examined, 0 STALE`
  (**33 of each**); `10 048`-line gate; **`TEN of the 33 R3−R4 rows are not
  licensed … it was FOUR of 26 (15%) and is now TEN of 33 (30%)`**.
  ⚠ **The 15%→30% framing is the manager's, not the report's. Is it fair?**
  4/26 unlicensed is 15.4% and 10/33 is 30.3% — **but is the comparison
  like-for-like, given `UNDEC` is not `NOT-LIC`?** `p36` and `p42` are `UNDEC`.
  **Say whether lumping them changes the sentence.**
- **§2** — buckets `9 / 4 / 10`; *"`p32` is the single new entrant"*; the median
  `7.26× → 6.75×` with `p05` 10th of 18 and 11th of 20; *"3 → 4 not
  overstatements"*. ⚠⚠ **AND THE SENTENCE THE MANAGER ADDED WITHOUT A RUN:**
  *"R2-is-dearer-than-R3 is a bounds-check-family property, and the row that
  weakened it came from outside that family."* **That is a generalisation from
  ONE row (`p32`). Attack it** — `p47`, `p09` and `p14` are the other three
  non-overstatements; **are they inside the bounds-check family or not?** If
  three of the four are spatial, the sentence is false.
- **§3** — the new four-row temporal table (`p32` / `p28` / `p34` / `p35`) and
  the new `p49` entry. ⚠ **`216 sanitizer cells and 18 Miri cells produce 0
  diagnostics`** and ⚠ **`the exact inverse of p34`** are both quoted from
  memory of earlier reports. **Check them against `results/gate/p49-*.json` and
  `p34`'s record.** ⚠ **The repair-site sentence names FOUR sites across FIVE
  rows** (`p27`/`p29`/`p32` READ, `p28` DESTROY, `p34` ACQUIRE, `p49`
  WRITE-THROUGH) — **but `p25` is a temporal row and is NOT in that list.
  Where does `p25`'s repair site go, and is the list therefore incomplete?**
- **§4** — `0.920` / `0.805`; **`152 trusted items, 333 trusted lines`**;
  and the new `global` paragraph. ⚠ **The manager wrote *"twelve probes"* for
  the `global` evidence; `TASK_164` ran four and `TASK_165` ran eight.
  Confirm the arithmetic and that no probe is double-counted.**
- **§5** — the type-law scope note. ✅ **`TASK_166` measured this and the
  manager did not soften it.** ⚠ **Check the manager did not ACCIDENTALLY
  strengthen it either.**
- **§6** — *"Five" → "SEVEN"*, and the trend sentence.
- **§7** — `166/85/0`; the `83`-is-wrong paragraph; `0 of 464` in 40 functions
  with `p = 0.0123`; temporal `FIVE → SIX`; the search-state paragraph.
  ⚠ **`p = 0.0123` is the ENGINEER'S OWN, flagged in its report as unreviewed.
  The manager published it anyway. Re-derive it or say it cannot be.**
- **The TITLE.** *"What 26 kernels say"* → *"What 33 kernels say"*.
  ⚠⚠ **Is that honest, given §2 can price only 23 of the 33 and §1's own
  licence rule excludes ten?** **The manager decided yes because the four
  Results were re-derived at 33. Attack that.**

## 2. ⚠⚠ THE THREE NEW `.memory/03-measurement.md` SECTIONS — rule 9's exposure

All three landed from an unreviewed report. The manager marked which half it
re-derived; **check the marks are honest, exactly as `TASK_165` item 5 was
scoped, because that is where the last one broke.**

- **`norel` is a LINK-ADDRESS property.** ✅ Manager re-derived on `p28`: of 371
  instructions and 71 differing lines, **69 differ only in the absolute target
  objdump prints for an identical encoded field**, and **2 are `lea`s to the
  same address differing by the `0x20` base shift**; zero `call`s differ.
  ⚠ **The manager's FIRST classifier for this said `64` real byte differences
  and was wrong** — it treated objdump's printed absolute as an encoded operand.
  **The second classifier is in the commit message and in `.memory/`.
  Re-derive it and confirm `2`, not `64`.** ⚠ **The mechanism is marked OPEN
  (3 of 5 pairs diffed). Confirm the OPEN mark is still needed, or close it.**
- **The null is ANTI-correlated with call volume.** ✅ Manager re-derived:
  `p36` at **1024** outward calls per kernel call has a null of **exactly
  `0.00`**, while `p25` at 7 calls has `+269.52`. ⚠ **Attack the direction:
  is "anti-correlated" the right word for a relation with n=33 and one
  enormous outlier, or is the honest statement just *"call volume does not
  predict the null"*?**
- **The band re-scoring.** ⚠⚠ **Only its load-bearing half is manager-checked**
  (the `p03`/`p04` oracle `moves_by = −7.00` against a derived correction of
  exactly `0.00`, so no positive threshold can catch them). **The scoring table
  itself is the engineer's.** **Re-derive it.**

## 3. ⚠ FINDING 64's ✅/⊘ SEPARATION

Same scope as `TASK_165` item 5, which found a `✅` the manager had not earned.
⚠ **Anything marked ✅ that the manager did not actually re-run is the defect
this item exists for.** Also check the **two commit messages** `6f5674f` and
`7b5822a`, and the **`.temp/mgr164/NOTES.md` correction** the manager applied
after `TASK_165` flagged its superseded null figures.

## 4. ⚠⚠ `TASK_166`'s OWN THREE JUDGEMENT CALLS — it flagged them, so settle them

1. **The three `⊘ NO SEARCH` `SEARCH_REVIEWED` entries.** They take `undeclared`
   from 21 to 14 while only **4** of the 7 rows had a real search. The engineer
   published the split explicitly for that reason. ⚠ **Should a reviewed
   declaration of *no search* count as `declared`?** **It changes a published
   count either way, so decide it rather than noting it.**
2. **`p ≈ 0.0123`.** The engineer's own, unreviewed, reproducing the published
   `0.0612` at 26 exactly as a control. ⚠ **The manager published it into §7.**
3. **The `global` reporting design** — a column beside `axioms` rather than
   folded into it. ⚠ **`TASK_165` MAJOR 1 recommended option B and the manager
   took it. Is the landed shape what B meant?**

## 5. ⚠ THE PACK ITSELF — spot-check, do not re-run

`TASK_166` came with its runs and ten named clean negatives. **Do not re-run
what it already did.** ⚠ **Two things it did NOT do and flagged:**
`p49` as the second `aliasing` row bearing on §5's title question (**nothing
run**), and the `13 449`-input fuzz half of §7's control arm (**26-pattern
figure, not re-run at 33**). **Say whether either is load-bearing for anything
now published.**

## Deliverables

1. **Per item: `SURVIVES` / `FALLS` / `SURVIVES, NARROWED`**, with the run.
2. ⚠⚠ **A verdict on the TITLE and on the `15% → 30%` framing** — the two
   places the manager editorialised rather than reported.
3. ✅ **CLEAN NEGATIVES, NAMED** — `TASK_166` left ten; add yours and do not
   repeat its.
4. ⚠ **Is `results/SYNTHESIS.md` FINISHED?** Not *"is it current"* — **is there
   a claim in it a reader would need that no artefact backs?**

## ⚠ NOT in this task

- **Any fix.** You report; the manager lands.
- **A 33-pattern sweep**, a re-measure, or re-emitting `outward_ir.json`.
- **`RECAP`'s queue triage** (`.temp/mgr164/QUEUE_TRIAGE.md`) — that is the next
  task. ⚠ **You MAY read it, and an error found there is worth more than most,
  because it is about to become a task file.**

## Rules

- `.temp/t167/` for scratch. ⚠ **Do not modify any earlier `.temp/t*/` or
  `.temp/mgr*/`** — cited evidence; copy out. **No `git add`/`git commit`.**
- ⚠⚠ **DO NOT LEAVE A `pgrep -f` WAITER RUNNING** — a waiter's own command line
  contains the string it greps for, so its exit condition can never be true.
  **Use `wait <pid>` or a `.done` sentinel.**
- ⚠⚠ **Read `blocked`/`verdict` out of the RECORD, never `grep` the log**, and
  ⚠ **`rc=$?` after a PIPE reads the LAST command's status.**
- Verus via `./verus_run.py`, single-file mode, never `--cargo`.
- Hand-run sanitisers need `env -u LD_PRELOAD`; never truncate with `head`.
- ⚠ **If you plant into a tracked file, restore in a `finally:` and verify by
  BYTES against `git show HEAD:`.**
- Report to `.tasks/TASK_167_REPORT.md`. **Write the file before citing it.**

**PROTOCOL rule 2 running count: launched from 933**
(`.tasks/TASK_166_REPORT.md`, which carried 929 → 933 on four refuted manager
claims). ⚠ **Reconciliation across branches is the manager's job, not yours.**

⚠⚠ **The one I want attacked by name is §2's new sentence — *"R2-is-dearer-than-R3
is a bounds-check-family property, and the row that weakened it came from outside
that family."* I wrote it from ONE row while folding, with nothing run. It is
exactly the shape of the hypothesis `TASK_166` just refuted, written one commit
later.**
