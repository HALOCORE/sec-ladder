# TASK_120 — attack FINDING 40, the manager's replacement for the finding that died

**Role: research reviewer.** Adversarial by design. **You do not fix; you
report.** A review that agrees without having tried to break something is a
failed review.

Read `.tasks/PROTOCOL.md`, then this file, then **`RECAP.md` finding 40 in
full**, then **finding 37** (the one it replaces, now annotated DISPUTED), then
`.memory/06-catalogue.md`'s status cells for the 22 non-built rows, then
`.tasks/TASK_115_REPORT.md` §C.

Scratch in **`.temp/r120/`**.

---

## Why this task exists, in one sentence

⚠⚠ **FINDING 37 DIED BECAUSE A MANAGER GENERALISED FROM A REFUSAL SET AND
PUBLISHED IT AS A LAW. FINDING 40 IS A MANAGER GENERALISING FROM A REFUSAL SET.**
**PROTOCOL rule 3 forbids the manager clearing its own design, and this is that
design.** ✅ **The manager marked it PROVISIONAL and wrote *"ATTACK IT"* into the
box. Do that.**

## The claim under test

> **The remaining rows fail because they RE-DERIVE A MECHANISM one of the built
> 26 already carries, not because they have nothing to measure.**

**Its evidence is a tally of seven rows:** `p20`→`p16`/`p02`/`p17`, `p21`→`p14`,
`p26`→`p13`, `p37`→`p08`, `p39`→`p09`, `p41`→`p07`+`p10`, `p43`→`p16`.

## §A — ⚠⚠ SEVEN OF TWENTY-TWO IS NOT "THE REMAINING ROWS". THIS IS THE DELIVERABLE.

**The catalogue has 22 non-built rows. The finding tallies SEVEN.** The other
fifteen are waved at as *"the allocator/recycling family, gate-policy blocks,
false novelty claims, and one-rung kills."*

1. ⚠ **Is "duplication" actually the dominant reason, or is it the reason the
   manager could name fastest?** **Go through all 22 cells and classify each by
   its OWN stated reason.** **If duplication is 7 of 22, the finding's word
   *"the remaining rows"* is false and the honest form is much weaker.**
2. ⚠⚠ **IS "DUPLICATION" EVEN ONE CATEGORY?** **`p37` duplicates `p08`
   STRUCTURALLY — the bug is unrepresentable in safe Rust.** **`p26` duplicates
   `p13`'s FINDING — a different kind of sameness entirely.** **`p41` duplicates
   `p07`'s bug class AND separately repeats `p10`'s spelling error.** ⚠ **If
   these are three different relations wearing one word, the finding is a
   category error and that is a real defect.**
3. ⚠ **SELECTION EFFECT, and it is the same one that killed finding 37.** Every
   refusal reason was written by an agent who already knew the built tree.
   *"It duplicates `pNN`"* is the **cheapest available reason to write** and it
   is always *available*. **Ask whether it is the TRUE reason or the FIRST
   reason** — a row refused on a measurement that ALSO happens to resemble a
   built pattern is not a row refused FOR duplication.

## §B — ⚠⚠ DOES THE FINDING LICENSE THE CONCLUSION IT IS USED FOR?

**Finding 40 exists to answer *"why is the catalogue exhausted"*, and that
question exists to answer *"should this project build a 27th pattern"*.**

⚠⚠ **BUT THE FINDING'S OWN LAST PARAGRAPH SAYS THE ADMISSION BAR STILL STANDS —
*a row is admissible whenever it brings a NEW MECHANISM* — AND THAT IF THE
REMAINING ROWS FAIL BY DUPLICATION, THAT IS A STATEMENT ABOUT THESE 48 ROWS AND
NOT ABOUT THE SUPPLY OF C PATTERNS.**

**So push on the gap:**

- **"The 48-row catalogue is spent" and "there is nothing left worth building"
  are DIFFERENT CLAIMS.** ⚠ **Does anything in the record support the second?**
- ⚠ **The 48 rows were written PRE-PROJECT, before any of the 26 patterns
  existed.** **A pre-project list being exhausted is close to expected and may
  say nothing about the domain.**
- ⚠⚠ **THE STANDING USER MANDATE IS *"as many realistic C patterns as
  possible"*.** **If finding 40 supports *"go find new rows"* rather than
  *"stop"*, THAT IS THE MOST IMPORTANT THING YOU CAN REPORT**, and it reverses
  the project's current direction. ⚠ **Do not soften it to be agreeable — but do
  not manufacture it either. If the honest answer is "the domain really does look
  worked out", say that.**

## §C — spot-check the reasons themselves, because reasons get REUSED

⚠ **`p28` is the precedent: right verdict, wrong reason** — and `.memory/` says a
refusal's reason is what the next row gets judged against, so **a wrong reason
propagates in a way a wrong verdict does not.**

**Pick the THREE load-bearing cells and check them against their artefacts, not
their prose.** Suggested, but choose your own and say why:

- **`p43`** — *"`p16` verbatim, `+3.00 Ir`/call flat"*. ⚠ **Its cell already
  records ONE struck citation** (it cited `p20`, an UNBUILT row, and the
  catalogue notes that corroborating one unbuilt row with another is circular).
  **Is the surviving `p16` corroboration real?**
- **`p39`** — *"`p09`'s sentence with the mask on the other side, the bug is one
  immediate `$0x1ff` → `$0x3ff`"*. **PROVISIONAL, unreviewed.**
- **`p26`** — the newest, and the one whose *previous* two stated mechanisms were
  both wrong (`TASK_086`'s `5.33×` invalid pair; `TASK_092`'s idiom split and its
  false *"neither has a panic edge"*). ⚠ **Two wrong mechanisms on one row is a
  reason to check the third.**

## §D — clean negatives are wanted, and one is cheap

✅ **The MEASURED half of finding 40 is not in dispute and you should confirm it
rather than re-derive it:** `48 = 26 + 17 + 3 + 2`, zero unadjudicated rows.
**Run `python3 .temp/mgr115/census.py` and its `--naive` arm.** ⚠ **If the census
disagrees with the finding, the finding is wrong on a fact and that outranks
everything above.**

⚠ **Also confirm or refute the one row-level claim the manager singled out:
`p40`'s *"21 `Ir` out of 360 million while LLd read misses differ 4.20×"*.** **It
is the finding's only instrument-level claim and it rests on a single
`TASK_086` measurement that `TASK_115` quoted but did not re-run.**

---

## Constraints

- **`.temp/r120/` only. No `/tmp`.** Keep the generator, delete the artefact.
- **No `git add` / `git commit`.** Read-only git is fine.
- ⚠ **Do not edit `.memory/`, `RECAP.md`, `results/`, `synthesis/`, `harness/`,
  `pilot/` or any `patterns/*/` file. You are a reviewer.**
- ⚠⚠ **DO NOT RUN `harness/check.py`, `build.py` or `measure.py`** (except
  `measure.py --check-stale`) **unless the manager tells you the tree is free** —
  `TASK_118` and `TASK_119` may be running and both rewrite gate records.
  **Build any probe with direct `clang`/`gcc`/`rustc` under `.temp/r120/`.**
- ⚠ **Callgrind `Ir` is deterministic and immune to concurrent load; wall clock
  is not.**
- ⚠ **Every probe needs an arm that MUST FIRE.** The list at the end of
  `.memory/03-measurement.md` holds **six live entries numbered 1–7** (entry 5 is
  retracted). ⚠ **Do not quote its ordinal.**
- ⚠⚠ **Probe 2 has SIX known defects and the tool the catalogue recommends
  (`.temp/t104/probe2.py`) carries the sixth — it truncates at the last `ret`.**
  **If you use probe 2 at all, take the symbol extent from the ELF symbol table.**
- Hand-run ASan needs `env -u LD_PRELOAD`; never truncate a sanitiser log with
  `head`.
- `timeout <N> <cmd>`; never `pkill`/`killall`.

Write your report to `.tasks/TASK_120_REPORT.md` as well as returning it.

---

⚠ **PROTOCOL rule 2's running count is 466.** The calls I am least sure of:

1. ⚠⚠ **That finding 40 is any better than finding 37.** Both are a manager
   reading a refusal set. **The differences I claim are that finding 40's
   measured half is a census rather than an inference, and that its
   generalisation is marked PROVISIONAL instead of published as a law.** ⚠ **If
   you think that is a distinction without a difference, SAY SO — that would mean
   the project should carry the census and NO generalisation at all, which is a
   perfectly respectable outcome.**
2. **That §A's count matters.** ⚠ **Maybe 7 of 22 is fine, because the other
   fifteen were refused for reasons that are individually sound and simply
   various. *"The rows fail for many different good reasons"* is a legitimate
   answer and would still close the catalogue** — it would just mean finding 40
   should be a LIST, not a LAW.
3. ⚠⚠ **That the catalogue being spent means the project should stop.** **This is
   the one with real consequences: the standing user mandate is *"as many
   realistic C patterns as possible"*, and §B is where I think the current
   direction is most likely to be wrong.** **I have written the box to say the
   decision now has no stated reason. If you find one — in either direction —
   that is the highest-value output of this task.**

Carry **466** forward, incremented by what you find.
