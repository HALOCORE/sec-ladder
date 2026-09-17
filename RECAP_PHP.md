# RECAP_PHP — the handoff document for the PHP programme (`patterns-php/`)

**Read this first, always.** The manager updates it at every task boundary.
For the *other* programme (`patterns/`) read `RECAP_PAT.md`; for the split
between them read `CLAUDE.md`'s top table.

> ⚠⚠ **SIZE DISCIPLINE — AND EVERY NUMBER THIS BOX ONCE GAVE FOR IT WAS WRONG.**
> `RECAP_PAT.md` really did reach **560 KB**, and **the START HERE box stays
> ≤ 20 lines.** Everything else here was invented or miscalibrated:
>
> | this box said | measured |
> |---|---|
> | a `why` became *"a ~7,000-word JSON string"* | **no such row.** `p01`, the row meant, is **2 057**; the largest anywhere is `p16-tlv-walk` at **4 995** |
> | *"a `why` stays ≤ 200 words"* | unsatisfiable — the gate mandates an 11 003-byte shared block |
> | *"the ROW-SPECIFIC half stays ≤ 200 words"* | **30 of 33 PAT rows break it**; `p01`, the template, is 201 |
>
> ✅✅ **SETTLED AT `TASK_PHP_006` §5: THERE IS NO SIZE RULE ON `why`, AND THAT IS
> THE ANSWER, NOT A GAP.** Distribution over 33 PAT rows + `ph00`: **min 197 ·
> median 989 · p90 1817 · max 3140.** Any limit at or under q1544 refuses a
> quarter of the built corpus; any limit the corpus meets permits 3× the median.
> Imposing one on PAT means editing text *inside the hashed block* on 33 rows —
> **33 re-gates for a style rule.** The manager's structural alternative was
> **also** unsatisfiable (**not one `why` in either programme contains a single
> newline**, so no row has a second paragraph). What replaces it:
> `gate.py::why_sizes` **reports** each php row's size on every preflight and
> **cannot fail a run**. A reported size is not a rule — which is why it is safe.
>
> ⚠⚠⚠ **THE LESSON IS THE PROPAGATION, NOT THE ARITHMETIC.** The 7 000 went:
> manager task file (`TASK_PHP_002.md:149`) → this box → an engineer citing it
> back as *"the figure **that motivated the size rule**"*
> (`TASK_PHP_002_REPORT.md:492`). **Three versions of a rule were written, two
> failed, and the justification for all three was a number nobody had measured.**
> `PROTOCOL.md` rule 14, and the **second** time here — the first was *"123 ASan
> reports"* (F4). **A premise in a task file is one an engineer has no reason to
> doubt.**
>
> ⚠ Detail — the 11 003/11 004/11 006 byte count, its withdrawal, and
> `TASK_PHP_005` F-5's own wrong span (it measured the prefix only, making the
> corpus **maximum**, `p16-tlv-walk` at 3 140, look like the minimum at 109) — is
> in `TASK_PHP_005_REPORT.md` §4 and `TASK_PHP_006_REPORT.md` §5. ⚠ **This box
> had grown to 74 lines about keeping documents short.**

---

## ▶ START HERE — the next action, in ≤ 20 lines

```
STATE   ⭐ 13 ROWS; **9/20 fam, 24 owed** to floor 37. ⛔⛔ **BACKLOG 6** (`F147`-`F152`),
        **ALL MINE, ALL UNREVIEWED** -- it DOUBLED today. ⭐ **`RESTS` IS `0`**: law 11's
        14 defects are discharged. ⛔ **`0` IS NOT *"nothing owed"* -- item 155.**
⛔ FIRST **DECIDE: A REVIEW ROUND, OR ROW 14?** I recommend **THE ROUND**, and not as a
        preference -- **9 consecutive rounds have refuted manager claims**, and TODAY the
        engineer filed **5 findings against my brief, 4 changing something published.**
        ⚠ The counter is real: **a round is METH and bills no row**, and 24 are owed.
✅ DONE  **148 ADJUDICATED · 149 SETTLED · 153 DISCHARGED** (`_064`, 15 files promoted).
        ⛔ `F102` was ALREADY promoted under a **RENAME the census cannot see** -- I had
        ruled it a defect. ⛔ **`F150`'s *"11 of 13 UNREVIEWED"* WAS WRONG -- it is 4/4/5
        (reviewed / not / NO MARKER)**, by regex over prose: **`F148` in the session that
        filed `F148`.** Corrected IN PLACE; cause is item **154**.
        ⭐⭐ **2 FIGURES MOVED, both re-verified by me**: `F73` `0 of 6` -> **1 of 14**;
        `F85` `29 of 38` -> **111 of 141** -- ▶ **the RATIO survives a 2.3x corpus
        (76.3->78.7 %), the COUNT does not.**
NEXT    ▶ **ROW 14 = `ph70`** (E3) -- ⭐ **R1h PINNED** (`UPSTREAM_002.md`): `72c6d5cbafc9`,
        **TWO hunks, EACH HARMFUL ALONE**, pre-image NOT 5.0.0 so it needs a BACKPORT.
        ⛔ `ROW14_001` §7 owes the kernel design + an EMPTY-INPUT probe cell.
        ▶ ALSO **154**+**150** (reviewer's) · **155** · **156** · **151** · **152**.
⚠ TRAPS ⛔ **NEVER INFER AN ABSENCE FROM A CLI's SHAPE, A `grep -c`, OR A REGEX OVER PROSE.**
```

---

## What is true now

| | |
|---|---|
| **rows built** | **13 — `ph03` + `ph07` (`S1`), `ph16`, `ph29` SPATIAL · `ph64` (`E1`) + ⭐ `ph66` (`E2`) TEMPORAL · `ph45` (`T1`) + `ph53` + `ph52` (`T3`) + `ph55` + `ph56` (`T5`) + ⭐ `ph97` + `ph96` (`T6`, ✅ **QUOTA MET** — ⚠ **not *exhausted*: 2 of 5 catalogued rows built, and `quota.py` prints `open` for exactly that state**) TYPE. ⭐ ALL THREE AXES OPEN; TYPE has FOUR families; **9** of 20 entered, **24** rows owed to a floor of 37 — ⚠ **this read *“8 … 25”* until 2026-09-17 and `quota.py` had said otherwise since `ph66` gated; count it, do not trust it: `python3 .tasks-php/quota.py`. ⭐⭐ `T6` IS THE THIRD FAMILY CLOSED AND THE FIRST CLOSED BY A ROW THAT PRICED **TWO** UPSTREAM REPAIRS (`F136`).** ⚠⚠ **THE FLOOR IS 37, NOT 40** — `ADJUDICATION_003` / item 121: it is `Σ min(2, |family|)`, because `S5`, `S6` and `T4` hold ONE row each. ⛔ **That is a CONCESSION, not a saving: those three can never produce the within-family control min-2 exists to buy** (`ph55`/`ph56` measured what it buys — one family, one fix shape, TWO different harms). ✅✅ **ROW 13 WAS TEMPORAL — `ph66`, `E2`, GATED `PASS` 2026-09-16 (`_062`), so the axis is at TWO and `E2` is entered.** ⚠ **Still 14 of the 24 owed are temporal and SIX of the eight families have ZERO.** ⭐⭐⭐ **AND `ph66` IS THE CORPUS'S FIRST ROW THE WHOLE SAFETY STACK IS BLIND TO** — `R1`(gcc), `R1`(clang), `R2`, `R3`, `R4`, `R5` return the SAME `u64` on all eight inputs, ASan/UBSan `fired: false`, Miri `ub: false`; only `kernel_hardened.c` moves (`F143`). Each five rungs + R1h. ⛔⛔ **AND THIS CELL SAID *“7”* WHILE TEN WERE GATED — caught 2026-09-14 by a pre-handoff audit, `PROTOCOL.md` rule 13, and THE THIRD TIME for this exact cell.** ⚠⚠ **THIS ROW SAID *"3"* FOR TEN TASKS** — `PROTOCOL.md` rule 13, and the box above warns about exactly this. **Count it: `ls results-php/gate/ | grep -av ph00 | wc -l`.** ⚠ **The lesson that outlived the arithmetic, kept because it did**: at n = 2 both rows were `ph03-uudecode-bound` and `ph07-strcut-cursor`, **the SAME family** (`S1`, unbounded cursor walk, 1 of the catalogue's 20) — and **no document said so for four tasks.** That cost, and the quota rule out of it, are open item 34 and `QUOTA_001.md`. ⓘ `ph00-smoke` is a relocated PAT calibration kernel — throwaway, **no PHP provenance**, and it prices nothing. ⚠ It IS in `results-php/gate/`, which is why the count command excludes it |
| **tasks** | ⛔⛔ **THE COUNT USED TO BE WRITTEN HERE AND IT ROTTED A FOURTH TIME.** It read *“57 written, `_001`–`_057`”* while 58 existed — `_058`, which this same session wrote, dispatched, landed and committed. ⭐⭐ **AND THE PREVIOUS REPAIR IS WHY**: told to stop naming a task's STATE, I stopped naming the state and left the COUNT, and the count is what broke. *Fixing one limb of the mechanism that bit you* — `F122`/`F127`/`F129`'s class, now in the cell whose whole history is this class. ▶ **NO NUMBER LIVES HERE.** ⚠ **Derive it**: `ls .tasks-php/TASK_PHP_*.md | grep -av REPORT | wc -l`, and read the START HERE box for what is in flight — ⛔⛔ **this cell must NOT name a task's state again.** It has gone stale IN THE SAME SESSION THREE TIMES RUNNING — *“`_055` is WRITTEN AND NOT YET DISPATCHED”*, *“`_056` IS RUNNING”*, *“`_057` IS WRITTEN AND HELD”* — each written hours before the action that falsified it. ⭐ **The 2026-09-15 rule *“write it as DISPATCHED, then dispatch”* DID NOT WORK, because the defect is not the tense: a per-task state changes several times a session and a table cell is the wrong home for it. ▶ The count is derivable; the state lives in ONE place, the box.** <br><br>⭐ **WHAT A ROW COSTS — as an EVENT, read from `python3 .tasks-php/task_cost.py` at `67304b3` (the commit that LANDED `ph66`):** marginal **2.38** tasks/row (searched-only **2.35**); first-in-family **2.22** (n=9) vs follow-on **2.75** (n=4); **PUBLISH `~57 .. ~72`, middle `~58`**. ⛔⛔⛔ **AND THIS CELL WENT STALE INSIDE ONE SESSION AGAIN — I WROTE `2.50`/`~63..~79` ONE COMMIT BEFORE `ph66` GATED AND DID NOT RE-RUN.** ⚠⚠ **THE EVENT-DATING DID NOT SAVE IT, AND THAT IS THE NEW PART**: the figures WERE dated, which is `F126`'s prescribed guard — but the sentence called them *"the live figures"*, and **a date makes a number true as HISTORY while the word *live* claims it is true NOW.** ▶ **Dating a figure is necessary and not sufficient; the LABEL has to be historical too.** ⭐ `ph66` came in at **1.00**, joint-cheapest in the series, and it is an **opener** — so first-in-family fell `2.38 → 2.22` at n=9, **`F126`'s refuted opener premium confirmed a third time.** ⛔⛔ **DO NOT QUOTE THESE WITHOUT RE-RUNNING THE COMMAND.** ⛔⛔⛔ **AND THIS MOVE WAS NOT A ROW LANDING — IT WAS A CLASSIFICATION THAT HAD BEEN WRONG FOR ~20 TASKS** (`F142`): `"040"`, the R1h hunt for `ph52` **and** `ph53` plus row 7's build brief, sat classified `PENDING` after both its rows gated, so real row cost was parked outside the numerator and **every figure in this sentence was understating.** ⭐⭐ **`N8` was green throughout, because `N8` bounds the PENDING pile's SIZE and the property is its MEMBERSHIP** — `F132`'s class inside a validator. ✅ Repaired at the data: a `PENDING` entry now spells itself `"PENDING:ph66"` and `N8b`/`N8c`/`N8d` re-derive the answer from the gated corpus every run. ⛔⛔ **AND THEY MOVED AGAIN THE MOMENT `ph96` GATED — from `2.55` / `~65 .. ~85` / `~68` at `6bff271`+`_058`, quoted in this very cell, to the figures above ONE ROW LATER.** ⭐ **`ph96` came in at `1.00`, joint-cheapest with `ph97`, its own sibling — so `T6`'s BOTH rows cost 1.00 and the follow-on premium fell `3.17 → 2.62` while the opener figure did not move at all.** ▶ **That is `F126` confirmed a second time from the other side: the opener premium is refuted in SIGN, and the follow-on number was carrying the noise.** ⚠ **These moved the moment `_058` was classified, which is the whole reason the quote is dated**: at `1cc2c0e` the same command read marginal `2.45` and `~63 .. ~82 / ~66`. ⛔ **`F126`'s defect was writing a range, changing the ledger, and never re-running; the guard is not a better number, it is the date beside it.** ⛔⛔ **DO NOT QUOTE THESE WITHOUT RE-RUNNING THE COMMAND.** This cell previously carried FOUR GENERATIONS of the projection at once — `~81..~101`, `~99..~122`, `~94–127/~110` and `~70..~92/~73` — saying *“PUBLISH `~94–127`”* and *“the figure moved”* in the same breath, so **a reader could not tell which was live.** ⭐ **Rewritten, not appended to** (item 73, ×8). <br><br>⚠⚠ **THE THREE LESSONS THAT OUTLIVED EVERY NUMBER ABOVE, and they are why this cell exists at all:** **(1) `total / rows` IS THE WRONG QUANTITY** for *“what will the next row cost”* — it charges 20 one-time tasks (Phase 0, the mining wave, the whole catalogue) to eleven rows, and answering the marginal question with it is how *“the php side costs TWICE what the plan assumed”* got published and withdrawn. **(2) *“AND RISING”* WAS A DENOMINATOR ARTEFACT** — `total/rows` rises whenever one-time tasks accumulate while rows lag, **so it would rise if every row cost exactly 3.** A trend claim needs the PER-ROW series: `[2.83, 5.50, 1.33, 3.33, 2.00, 3.00, 3.00, 2.00, 1.00, 2.00, 1.00]`, flat if anything FALLING, with one expensive row — and **`N6` is the control, because `ph07` was named as the dearest BEFORE the run, being the only REBUILT row.** **(3) ⛔ THE FIRST-IN-FAMILY PREMIUM IS REFUTED IN SIGN** (F126): `OPENER_RATE = 4.00` was a pin from **n = 1** that nobody re-derived for ten rows, and openers measure **cheaper**, not dearer. ⚠ **The ARGUMENT for it survives its own refutation** — the per-row measure cannot see the methodology a row OPENS — **but it was applied to one row and never again.** <br><br>ⓘ **`_056` was ONE task** (five rungs + R1h, gated PASS, no resume) **and came in at 1.00, joint-cheapest in the series — which is evidence AGAINST the opener premium, not for it.** ⓘ `_057` is `METH`: a review round is charged to methodology, not to the rows it reviews, **which is precisely why the per-row series cannot see what a row opens.** ⭐⭐ **AND THE ENGINEER REFUSED TO CLASSIFY ITS OWN TASK**: *“the remedy's second half is a cost claim about my own task in the ledger the published projection comes from.”* ▶ **A cost ledger is not a build artefact; the party whose work it prices must not price it.** |
| **infrastructure** | **built and reviewed TWICE**: `harness-php/{root,gate,provenance}.py` · `common-php/` · `patterns-php/{SOURCES.md,php-5.0.0.manifest}` (1170 files, 109 KB) · `.tasks-php/PROTOCOL_PHP.md` · `results-php/`. ⚠ **Reviewed is not the same as correct — the second review found a blocker in the first review's own fix.** ⚠ There used to be a SECOND row in this table also labelled `infrastructure` saying *"not yet built — Phase 0"* (`TASK_PHP_003` m1); it is gone |
| **candidates** | **54** delivered across three axes. ⚠ **`.tasks-php/ADJUDICATION_001.md` takes that to ≈ 80**: +6 splits, −2 merges, **+17 kills reversed**, +1 dropped with no reason recorded, +4 that fell between axes. Evidence in `.tasks-php/TASK_PHP_001_MINE/` |
| **catalogue** | ✅ **`patterns-php/CATALOGUE.md` — 102 rows, LANDED AND VERIFIED** by `TASK_PHP_023` (⚠ this line has said **91** and **93**; count it, do not trust it: `python3 .tasks-php/quota.py`). **20 mechanism families**, unchanged by the landing — spatial **42** · type **29** · temporal **31**. ✅ **Part A and Part B agree row-for-row, and every row is filed under the same axis in both** — the `ph92`/`ph93` mismatch is gone. ✅ `coverage.py` **166/166, MISSING 0**; all 8 withdrawn `C.1` kills present in place with their notes. ⚠⚠ **Two landed sentences were measured FALSE and are corrected in `CATALOGUE.md` AND in `land_019_020.py`** (F52 `ph94`'s trigger, F53 `ph32`'s *"one commit"*) — a landing script left carrying a refuted claim is a cited artefact. ⚠ **`_023` reviewed the nine admissions and would overturn NONE of `_019`'s reversals**; ~70 citations opened across 15 files, including the ones `_019` called correct. ⚠ **Parts A/B beyond the nine are still UNREVIEWED**, and `_020` measured the mechanism sentences right and the `▸ trigger` lines wrong (F46). Part A is a scannable table, Part B a ~150-word block per row, Part C the kill list with a re-derived criterion per kill |
| **citation base** | PHP 5.0.0, pristine tarball, sha256 `5783e0c0…d6919`, 5595997 B, 3815 entries. **4.0.x ignored** (`DP-06`) |
| ⭐ **which statistic** | ⚠⚠ **FOUR families are in use and THREE are published** — `ph03`/`ph16`/`ph29` in **A1**, `ph07` in **A3**, `ph64` in **B1**, `ph45` in **A1 + W1** labelled, ⛔⛔⛔ **THIS SAID *“the SIX rows built since all publish BOTH A1 AND W1 labelled”* AND NAMED `ph97` AND `ph96` AMONG THEM. MEASURED 2026-09-16: BOTH PUBLISH `A1` ONLY** — `W1` appears **zero** times in either row's `NOTES.md`. ⭐ **Counted rather than trusted, across all 12 rows: FIVE publish both** — `ph45`, `ph52`, `ph53`, `ph55`, `ph56` (`ph29` has a single `W1` mention and is not one of them). ⛔⛔ **`ph97`'s entry was already false when it was written and I APPENDED `ph96` BESIDE IT WITHOUT CHECKING THE LIST'S OWN PREDICATE** — the fifth rot of this cell, and the first I contributed to. ⛔⛔⛔ **AND I WROTE *“THIS IS NOT A DEFECT IN EITHER ROW … WHICH IS THE DISCIPLINE WORKING”* HERE ON 2026-09-16, AND `TASK_PHP_061` REFUTED IT THE SAME DAY.** `_060` §8 did measure the 16-cell matrix first and did conclude *“A1 is the resolving statistic for this row”* — ⛔ **but it measured it at `O3/isolated` ONLY, and at `O0/isolated` `A1` reads `+0.0000` while `W1` moves `−2.24 … −19.58 Ir/call` across four cells.** ▶ ***That is why `F136`'s headline was refuted***: the row published one statistic, in one optimisation cell, and the claim it published does not hold in the other. ⭐⭐ **SO IT *IS* A DEFECT IN THE ROW, AND IT IS THIS CELL'S RULE EARNING ITS FIRST MEASURED COST** — *publish BOTH, labelled, always* would have caught it. ✅✅ **AND IT EARNED ITS SECOND ON THE VERY NEXT ROW, WHICH IS WHY THIS CLAUSE IS BEING EXTENDED IN THE EDIT THAT GATES THE ROW RATHER THAN LATER** (the omission that rotted this cell five times). **`ph66` (`_062`) publishes BOTH statistics, BOTH C columns and TWO optimisation levels** — and the second level is what caught the engineer's own first reading. ⛔⛔⛔ **`F144`: at `O3/isolated`, `c-clang`, `A1` reads EXACTLY `+0.0000` between `R1` and `R1h` while family B moves `−2.03` and `−12.00 Ir/call`** — because **clang keeps `zend_hash_del_key_or_index` OUT OF LINE** (`0x3a5` vs `0x3a2` bytes) **where gcc INLINES it**, so the entire repair sits in a symbol `A1` does not count. ⭐⭐⭐ **AND `c-clang`'s `inside_share_W` on those cells is a perfectly healthy `65.31 %` / `51.31 %`, which did NOT predict it and COULD NOT**: the share measures *how much of the cell is inside the symbol*, and the question is *whether THE DIFFERENCE is*. ▶ ***That is the sharpest statement of `A1`'s blindness the programme has, and unlike `F125` its cause is a choice the COMPILER makes, not one a person makes — so no row can avoid it by writing its kernel carefully.*** ▶ **Open item 137, which is now ANSWERED (a) and whose routing FAILED — `F140`.** ⛔⛔⛔ **AND `F146`, FILED 2026-09-16 WHILE SCOPING `_063`, SAYS THIS CELL'S RULE HAS A FLOOR IT DID NOT KNOW ABOUT: `A1` IS NEVER MEASURED AT `O0/large.bin` — NOT ON ONE ROW, ON `0 of 263` PAT AND `0 of 111` php ISOLATED CELLS, i.e. ON NONE OF THEM** — because `harness/measure.py`'s `CG_PLAN` adds `large` **only at `O3`**, in one deliberate line commented *"where the perf claims live."* ⛔⛔⛔ **AND THE CLAUSE THAT STOOD HERE FOR ONE DAY — *“so `_061`'s rule CANNOT BE DISCHARGED FROM COMMITTED RECORDS at `O0`”* — WAS REFUTED BY `_063` §3.2, USING `ph66`'s OWN COMMITTED CONTROL.** `controls/inside_share.json` **carries `A1` at `O0/large` on all 8 cells**, and it is committed, pinned and `--selftest`ed. ✅ **WHAT IS TRUE**: `CG_PLAN` omits `O0/large`, so **a row that wants the two-level matrix gets that cell from a ROW-LEVEL CONTROL rather than from the measurement record** — `ph66`'s is the model and the only one so far. ⛔ **That is a note on HOW TO OBEY the rule, not a limit on it.** ⭐⭐ **WHAT SURVIVES SEPARATELY, AND IS SMALLER**: `ph66`'s printed matrix carries **TWO PROVENANCES in adjacent columns** — `A1`/`W`/`share_W` **live**, `share_F74` **committed** — with the blank on exactly the 8 cells `CG_PLAN` never wrote (item 147, **CONFIRMED**), and `_063` rules the fix is a **per-COLUMN provenance label**, `F108` one level down. ⚠ **The *“perf claims no longer live only at `O3`”* clause is DECLINED at `n = 2`** (item 123's rule), **and dissolves anyway** because the row-level control supplies the cell. ⛔ **NO EDIT TO `CG_PLAN` IS PROPOSED — `measure.py` is hashed into all 33 PAT measurement records.** ⭐⭐⭐ **THE REAL LESSON IS NOT ABOUT `A1` AT ALL**: `F146` asserted a property of *committed records* from a census of *`results*/`* — ⛔ **`F142`'s own moral, fired on the finding filed hours after it, and the THIRD instance of that error in one day** (`F141`, `F146`, and the `_063` brief itself). ▶ **See `F142`'s RULE-9 row: `n = 3` is a rate.** ⛔⛔ **THIS LIST HAS NOW GONE STALE TWICE THE SAME WAY** — it stopped at `ph45` for FOUR ROWS (caught 2026-09-14) and then at `ph56` for `ph97` (caught 2026-09-15, the audit before compaction). ▶ **Extend it in the edit that gates the row, or it will happen a third time.** ⭐⭐ **`ph56` is the one to quote: it publishes BOTH C COLUMNS and BOTH SIGNS** (`−8.423 %` vs `c-gcc-h`, `+3.811 %` vs `c-clang-h`, W1, `large.bin`, `O3/isolated`) — **F108's rule working on the first row built after it landed.** ▶ **`.tasks-php/STATISTICS_001.md` is the whole argument and it is COMMITTED** (it was in gitignored `.temp/`). ⛔⛔⛔ **AND `_063` §3.5 RULED THAT THIS CELL'S RULE IS ON THE WRONG AXIS — READ THIS BEFORE THE SENTENCE THAT FOLLOWS IT.** The manager's answer to item 137 was **(a) `ph96` violated *publish both*** and **it is OVERTURNED**: ⭐⭐⭐ `_061`'s own table shows **`W1` at `O3` ALSO reads `+0.0000`**, so *publishing both statistics would NOT have caught `ph96`* — **only the `-O` AXIS catches it.** ▶ ***The matrix is 4-D (statistic × input × opt × mode), and “publish both, labelled” names ONE of the four.*** ⛔ **So the rule below is not wrong, it is UNDER-SPECIFIED, and `ph96` obeyed the part that was specified.** ⚠ **The live successor question — *should a row-level TWO-LEVEL matrix be REQUIRED?* — is where `F146`, item 137 and item 146 all land**, and ⛔ **`_062` asked whether a row can AFFORD one and nobody has measured it** (item 125's census, member 7 of 7). ▶ ***A cost nobody has measured is exactly how `F123` happened.*** **The rule, as far as it goes: publish BOTH, labelled, always** — `inside_share` explains a disagreement and never gates one, because `s ≡ A/B` so certifying A needs B already. ⛔ **BUT IT IS ONLY A RULE WHERE IT WAS MEASURED, AND ON **3 OF 12** ROWS IT STILL IS NOT** — `ph07`, `ph53`, `ph64`, which are exactly the three rows carrying NO `inside_share` in `controls/` OR in `NOTES.md` (re-measured 2026-09-16; the residue is unchanged, only the denominator moved) (F127 opened this at 5 of 11; `_058` measured `ph03`, `ph16`, `ph29`). ⭐⭐ **AND `F125` PRICED WHAT THE SHARE IS FOR**: on `ph97`, moving one ASCII compare from the kernel into libc leaves the checksum **identical** and makes **A1 read `−28.61 %` CHEAPER while the whole program is `+9.39 %` DEARER** (`inside_share` 98.84 % → 64.50 %). ▶ ***A1 can report the SIGN BACKWARDS across a symbol boundary***, so A1's blindness is not noise — **it is a lever an implementation choice can pull, and *“call libc”* pulls it.** ⚠⚠⚠ **THE BIGGEST OPEN THREAD IN THE PROGRAMME: A1 is the WRONG COLUMN for the CROSS-LANGUAGE comparison — 29 of 38 sign flips live there and 28 of 29 survive family C.** ⛔⛔⛔ **RE-RUN 2026-09-17 ON 13 ROWS: `758` comparisons, **141** flips, **111** cross-language — so the COUNT `29 of 38` IS HISTORY and the SHARE ROSE, `76.3 % → 78.7 %`.** ▶ ***The claim survives on 2.3× the evidence; quote the SHARE, never the bare count*** (`law 17`). ⚠ **`28 of 29 survive family C` was NOT re-measured** — that adjudication ran over the old 29 (item 64). On `ph29/large` A says C is **+33 % dearer** than naive safe Rust while three other statistics say **~1 % cheaper**. ⛔⛔⛔ **AND THAT SENTENCE IS PUBLISHED FROM A ROW WHOSE OWN CONTROL DISCLAIMS IT** (**F127**, 2026-09-15): `ph29`'s `controls/spellings.py` says A1 *“is NOT right for this row's C-vs-Rust column (0.927 vs 0.655) and **that comparison is not made here**”* — **and this cell makes it.** ⛔⛔ **THE TWO SENTENCES ABOVE WERE TRUE WHEN WRITTEN AND FALSE BY THE TIME `_058` LANDED** — *“`ph29` has no measured `inside_share` outside that docstring, and five of eleven built rows have none at all”*. ⭐ **`ph29`, `ph03`, `ph16` and `ph97` now each ship a measured 16-cell matrix**; the residue is `ph07`, `ph53`, `ph64`. ⚠⚠ **THIRD ROT OF THIS CELL, AND THIS TIME IT CONTRADICTED ITSELF IN ADJACENT SENTENCES** — the stale claim sat immediately before the *“ITEM 127 LANDED”* line that refutes it, which is `F129`'s own defect for the third time in one day: **a correction written BESIDE a stale claim instead of REPLACING it.** ✅✅ **ITEM 127 LANDED AS `_058`, AND THE `+33 %` IS SETTLED: IT IS TRUE, REPRODUCES TO THE DIGIT, AND IS *ONE C COMPILER'S* NUMBER.** ⛔⛔⛔ **`c-clang` reads `−4.36 %` — THE OPPOSITE SIGN** — and W1 says C is cheaper on **both** columns (`−0.80 %` / `−27.54 %`); the input moves it too (`small.bin` `+39.92 %`). ▶ **NEVER QUOTE IT WITHOUT BOTH C COLUMNS** (**F129**, **F108**'s fifth thing, on the programme's most-cited number). ⛔ **And the caveat that guarded it guarded the WRONG PAIR**: `ph29`'s docstring disclaims C vs `safe_tuned` (Δshare `0.2715`) while this cell publishes C vs `safe_naive` (Δ `0.2355`) — **both exceed `F74`'s `≤ 0.02` condition (ii) by more than eleven times.** ⛔⛔⛔ **AND THE WORD *“INADMISSIBLE”* STOOD HERE AND IS NOW WITHDRAWN — `TASK_PHP_059` REFUTED IT, AND THE REFUTATION WAS ALREADY IN THIS CELL.** Four documents say `F74`'s bar never gates; **one is `.memory-php/02-ladder.md`** (*“NO FUNCTION OF THE SHARES CAN CERTIFY A AT ANY THRESHOLD”*), and **one is the sentence FORTY WORDS ABOVE THIS ONE** — *“`inside_share` explains a disagreement and never gates one.”* ⭐⭐⭐ **TWO SENTENCES IN ONE TABLE CELL, CONTRADICTING EACH OTHER, ONE OF THEM MINE: `F131`'s own class inside the cell `F131` was filed about.** ⭐ **And the reviewer measured a counterexample rather than only citing documents**: on `ph55` `c-gcc` vs `c-gcc-h` (`large.bin`, `O3/isolated`, both C cells, **same compiler**) the two-condition bar **ADMITS** a pair where A1 reads **exactly `+0.0000 %`** against a **66.14 `Ir`/call** whole-program difference. ▶ ***A gate that passes its own documented counterexample is not a gate.*** ✅ **WHAT SURVIVES, AND IT IS THE HONEST SENTENCE**: on **71 of 88** cross-language pairs the two cells' shares differ by more than `0.02`, so A1 and the whole-program column are **in the regime where they are EXPECTED to disagree** — ▶ **a reason to publish BOTH columns labelled, which **five of twelve** rows already do (`ph45`, `ph52`, `ph53`, `ph55`, `ph56` — counted 2026-09-16, not trusted), and NOT a reason to withhold either. ⛔ **This read *“six of eleven”* and BOTH halves were wrong; it is the SAME claim as the corrected list above and it had to be fixed in the SAME edit, because repairing one and leaving the other is this cell's own recurring defect.**** ⚠⚠ **AND THE WORD `inside_share` IS AMBIGUOUS IN THIS VERY SENTENCE**: two quantities wear it (**F129**) — ⛔⛔ **and *“every figure here is `F74`'s”* STOOD HERE AND IS FALSE: the `98.84 % → 64.50 %` pair four sentences up is the `W` one**, which under `F74`'s definition matches **no cell of `ph97`, or of any row, at ±0.0005** (`_059` §1.1). ✅✅ **SETTLED 2026-09-12 — THE REVIEWER WAS RIGHT AND I WAS WRONG.** `TASK_PHP_039` measured the `probe_iters` lever's gain at **`W^(−0.5)`** (F92), so item **68 ANSWERS NO** and **F90 is refuted on its operative half**; **family C (item 62) is the second column.** ⚠ **With one thing added by F91 that neither side had: test C's SENSITIVITY, not just its null** — `|B/A|` is **49.6–393.9×** in the small-Δ regime, and if C fails it too then **C is the second column CROSS-LANGUAGE and A stands alone SAME-LANGUAGE.** ⭐⭐ **THE AXIS: same-language differences are 1–2 instructions under 50–394× of callee noise, so only A resolves them; cross-language the callee work IS the effect. F85's 29-of-38 split is that axis, not just a count** (item **72**). ⚠⚠ **TWO LIVE CAVEATS ON THAT AXIS, BOTH FROM ROWS BUILT SINCE:** (a) **item 78** — on `ph53` A and B **agree** on every cross-language cell, because §B1a's O(1)-allocation precondition holds, so **the axis may be a PROXY for *does the callee work diverge*** and language merely correlates with it; (b) **item 82** — **A is NOT respelling-blind**: `ph53`'s A1 spread is `39.9`/`45.3` pp against `ph45`'s `0.000000`, so **F87 published a row fact as a statistic fact** and one clause of F91's own evidence table is withdrawn |
| **rungs** | all five, R4/R5 may land as findings (`DP-02`). ⚠ **UPDATED — `DP-02` UNDERSTATES IT: the R4 endpoint MOVES on two rows now.** `ph29`'s `r4_fold_iter` is **5.63 pp cheaper** and byte-identical (F77); `ph45`'s `r4_buf_slice_inline` is **−23.47 %** with **10 unchecked-dereference sites against the shipped 12** — cheaper *and* a smaller trusted surface — **and its R3 endpoint moves too, the first row where both do, with the bound's SIGN REVERSING under search** (F87). ⭐ **So a `fixed-R4 bound` over an UNSEARCHED endpoint is a bound over a number nobody has tried to move**; `ph03` and `ph64` are still unsearched (item 58's residue) — ✅ **verified live by `task_cost.py`'s `N12`, which derives it from the filesystem and stops on its own when a search lands.** ⛔⛔ **BUT *“TWO ROWS”* IS AN UNCHECKED COUNT.** `ph53`, `ph52`, `ph55`, `ph56`, `ph97` **and now `ph96`** have all had endpoint searches since this sentence was written, and **nobody has asked whether any of their R4 endpoints moved.** ⭐ **`ph96` is the one row of the six where part of the answer IS on file**: `_060` §9.1 measured **R4 == R5 to the instruction on both inputs**, so that row's R4 endpoint is pinned against R5 — but whether it moved against R3/R2 is exactly as unasked as the other five, and `_060` §13 item 2 flags the R4-vs-R2 `+9.67 %` as **the row's biggest gap, with no mechanism and no disassembly**. ⛔ **This list was extended BY HAND again, 2026-09-16, which is the defect the sentence below already names** — the sixth row arrived and the cell did not notice on its own. ⚠ **Not asserted stale and not asserted current — it is UNCHECKED, and each row's `spellings.json` uses a different schema, so the answer costs a read of five `NOTES.md` rather than a grep.** ▶ **That is the same defect this table has now shown three times** (`which statistic` stopped at `ph45`, then at `ph56`; this cell at `ph45`): **a list of rows that is extended by hand and not by the edit that gates a row.** ⓘ Batch it with item 127, which touches three of the five anyway |
| **PAT tree** | untouched and must stay so — `harness/*.py` and `common/*.py` are hashed into all 33 gate records (`PLAN_PHP.md` §2.1) |

### The rename, and what it cost

`RECAP.md` → `RECAP_PAT.md`, `PLAN.md` → `PLAN_PAT.md`.

- ✅ **Zero gate runs, zero re-measures.** Measured: `grep -nE
  '(grep|awk|sed)[^|]*\b(RECAP|PLAN)\.md' harness/*.py` → **0 hits**, so no
  *runnable* citation lived in a hashed file. The prose mentions that do live
  there were deliberately left alone.
- ✅ **Seven runnable-command citations repaired and RE-RUN**, in
  `.tasks/PROTOCOL.md` (rules 1 and 10), `.memory/01-ladder.md`,
  `.memory/02-bench-rules.md`, `.memory/03-measurement.md` and `RECAP_PAT.md`
  ×2. Rule 1's loop prints only `p01` (the documented benign exception) and
  rule 10's prints only the three `TASK_NNN` placeholders — both exactly as
  `PROTOCOL.md` predicts, which is what a working check looks like.
- ⚠ **Two pre-existing drifts surfaced and were NOT repaired**, because they
  are numbers inside findings rather than paths:
  `.memory/03-measurement.md` says *"13 PROVISIONAL lines"* and the count is
  now **16**; `.memory/01-ladder.md`'s `NR>109 && NR<930` window is stale
  against a file this long and returns finding **21**, not the highest.
  Recorded here so they are not mistaken for rename damage.
- ⚠ Historical citations of the old names in `.tasks/`, `patterns/*/`,
  `pilot/` and inside findings are **left on purpose** and resolve to the
  `_PAT` files. Do not "fix" them.

---

## ⚠⚠⚠ RULE-9 STATE — WHICH FINDINGS MAY ENTER `.memory-php/`

> ⛔⛔ **THIS BLOCK EXISTS BECAUSE THIS STATE WAS LIVING IN GITIGNORED
> `.temp/mgr175/NOTES.md`** — which is **F99's own defect**, applied to the one
> piece of process state that governs what may enter the authoritative layer.
> `PROTOCOL.md` rule 9: **nothing reaches `.memory-php/` until it survives an
> engineer→reviewer cycle.** ⚠ `grep -c UNREVIEWED RECAP_PHP.md` is NOT an index
> — it cannot tell a *closed* cycle from an open one. **This table can.**

> ### ✅✅ STATE AS OF 2026-09-13, AFTER `TASK_PHP_047` — **SIX OF SEVEN CLOSED, AND NOT ONE SURVIVED UNCHANGED**
>
> | | findings | may enter / stay in `.memory-php/`? |
> |---|---|---|
> | ✅ **UPHELD** | **F106** — and **UNDER-STATED** three ways | ✅ **LANDED** as the `tcb_items` entry in `02-ladder.md`, with the *"published axis, not the trusted base"* qualifier in the same sentence |
> | ⚠ **UPHELD-NARROWED** | **F97 · F102 · F104** | ✅ **stays, narrowings APPLIED not appended** (item 73) |
> | ⛔ **REFUTED in part** | **F105** — the `0.82 %` ✅ **UPHELD and GROWS to `1.02 %`**; the **`97.6 %` is GONE** | ⛔ **the `97.6 %` clause was REMOVED from `02-ladder.md` and replaced by the two-input slope** |
> | ⛔ **REFUTED** | **F103**'s `(slots) × (per-slot)` decomposition | ⓘ ✅ **it was never in the layer** — rule 9 working: the refutation cost a RECAP edit and no removal |
> | ⛔ ~~**STILL UNREVIEWED, cycle OPEN**~~ ⚠ **SUPERSEDED — see the `F96` PER-GROUP table below** | **F96** | ⛔ ~~**NO.** A build record plus a four-prediction ledger; the reviewer **checked whether `ph52` supplies the missing second method and it does not** (different row, different kernel)~~ ⛔⛔ **AND THIS CELL CARRIES THE EXACT FALSEHOOD `_055` REFUTED: what `_047` checked `ph52` against was the PREDICTION LEDGER, not the novelty claim, and `_047`'s own §5 says so.** ⭐ **Struck in place rather than rewritten, because it is a dated historical row — but it must not read as live.** |
>
> ### ✅✅ STATE AFTER `TASK_PHP_053` (2026-09-14) — **ONE OPEN CYCLE PLUS `F96`, AND THE TABLE IS THE INDEX**
>
> ⛔⛔ **THIS TABLE WAS REWRITTEN 2026-09-14 BECAUSE IT HAD BECOME SELF-CONTRADICTORY:
> it still listed `F110`/`F111`/`F112` as UNREVIEWED while the prose BELOW it said
> `_053` had closed them.** ⛔⛔ **AND IT HAPPENED AGAIN ON 2026-09-15 — THIRD TIME
> IN THIS BLOCK:** the `_047` row still read *"F96 STILL UNREVIEWED"* and `F113`
> still read `UNREVIEWED` while the table below had verdicted both. **Caught by a
> pre-compact audit, struck in place.** ▶ ⭐ **THE STRUCTURAL LESSON: this block
> keeps DATED SNAPSHOTS above a LIVE table, and a dated snapshot is indistinguishable
> from a live claim unless it is struck. Strike it in the same edit.** ⭐ **That is item 73's shape — a correction APPENDED
> instead of APPLIED — and the START HERE box warns about it in terms.**
>
> ⛔⛔⛔ **FOURTH INSTANCE, 2026-09-15, AND IT WAS SIX ROWS AT ONCE — CAUGHT WHILE
> WRITING THE BRIEF FOR THE ROUND THIS TABLE GOVERNS.** `F120`, `F121`, `F122`,
> `F123`, `F124` and `F125` each appeared **TWICE IN THIS ONE TABLE**: as
> `⛔ UNREVIEWED` in the rows that opened them, and as `✅ UPHELD` / `⚠ NARROWED`
> in the rows `TASK_PHP_057` added underneath. **A table that decides what may
> enter the authoritative layer listed six findings as both unreviewed and
> verdicted.** ⭐⭐ **THE MECHANISM, AND IT IS WHY THIS KEEPS HAPPENING: `_057`
> verdicted a BATCH, and the batch was APPENDED to the bottom instead of APPLIED
> to the rows at the top** — item 73 exactly, in the block whose own preamble
> cites item 73. ⚠ **The previous three instances were ONE row each and were
> repaired by striking. Striking six would have doubled the table to preserve
> nothing**, so they are **MERGED**: one row per finding, carrying the opening
> date *and* the verdict *and* whatever the opening row asked that is still
> live. ▶ ⭐⭐⭐ **THE REAL REPAIR IS THE SHAPE, NOT THE SIX ROWS: this table is
> an INDEX and an index has one row per key. `F96`'s own cell said so —
> *"the table's one-cell-per-finding shape is what forced the mis-filing"* —
> and that sentence was in the table while six keys had two rows.**
> ⛔ **A verdict must REPLACE the row it verdicts. Never add one below it.**
>
> | finding | verdict | what entered `.memory-php/`, and what did NOT |
> |---|---|---|
> | **F107** | ⚠ **UPHELD-NARROWED** (`_053`) | ✅ *option (b) does not exist* **fully upheld**, all three grounds re-derived **plus a FOURTH**. ⛔ its *"three of four refutations"* **count does not reproduce** — the advice may enter, the count may not |
> | **F108** | ✅ **LANDED** | inherited from `.memory/`, not invented here — which is why it did not wait |
> | **F109** | ⚠ **UPHELD-NARROWED** (`_053`) | ⛔⛔ its `inside_share` *"refinement"* **MUST NOT ENTER AS A RULE — `03-numbers.md:44-46` ALREADY SAYS IT.** ✅ **What entered is ONE CLAUSE OF EVIDENCE** appended to the existing rule |
> | **F110** | ⚠ **UPHELD-NARROWED** (`_053`) | ✅ **verdicts CONFIRMED on three axes**; ⛔ its *"same knob"* ground **REFUTED**. **§B5 landed and is now CORRECTED in place** |
> | **F111** | ⚠ **UPHELD offline / UNTESTED on upstream history** (`_053`) | ✅ census re-ran (`problems: none`), `0x14 = offsetof(zval,type)` confirmed by probe. ⛔ **four upstream-history claims UNTESTED (network) and NOT reported as confirmations** |
> | **F112** | ⚠ **UPHELD-NARROWED** (`_053`) | ⛔ the `rlimit` floor is **3**, not 2, so the *"`n = 2`"* coincidence is **REFUTED**; its control is **broken** (item 115). ⚠ *"the row had to buy it"* remains **UNPROVEN** |
> | ⭐ **F113** | ✅ ~~**UNREVIEWED**~~ **VERDICTED ON ALL FOUR POINTS AT `_055`** — headline survives on the measurement, ⛔ **the `iff` argument I gave it is a NON-SEQUITUR**, and the period is `(cell,axis)`-dependent too | `_053`'s own round. ⚠⚠ **Its `§B5` correction DID land**, because it is a measurement, **and its SCOPE (1 row against 3) landed with it** after the manager first shipped it without — item **118** |
> | **F96** | ✅✅ **VERDICTED PER GROUP AT `TASK_PHP_055`. NOT `UNREVIEWED`, AND NOT PERMANENTLY MARKED — EVERY GROUP HAD A CHEAP SECOND METHOD AND THE LAST ONE WAS IN THE ROW'S OWN `spec.md` ALL ALONG** | ⛔ **The *"no cheap second method"* ground was wrong TWICE OVER** — F114 found the first half, `_055` the second. ⚠ **Replaced entirely, not appended** (item 73) |
> | **F126** | ⚠ **UPHELD / REASON REFUTED** (`_057`) | ✅ split + `ph07` sensitivity both reproduce. ⛔ separability named the WRONG PAIR — there are **three** causes — and the published range was **stale within the hour**. **Corrected in place as an EVENT** |
> | **F114** | ⚠ **UPHELD-NARROWED** (`_057`) | ✅ conclusion upheld. ⛔ the one-cell shape is **permissive, not forcing** — it explains why nobody noticed, not why it happened |
> | **F115** | ✅✅ **UPHELD, BOTH HALVES** (`_057`) | ⭐ one of only three clean survivals; second method was an independent 12-line byte reader over all 163 patches |
> | **F116** | ✅ **UPHELD / REASON REFUTED** (`_057`) | ⛔ **its evidence is NOT re-derivable — the log AND its generator are both gitignored.** F51/F99's defect, **fourth instance** |
> | **F117** | ✅✅ **UPHELD, BOTH HALVES** (`_057`) | ⭐ clean survival |
> | **F118** | ✅ decision stands on its OTHER reason | ⛔⛔ **its stated ground is REFUTED AND INVERTED** — F116 helps the **type** axis ~2× more than the temporal one, and `ph97` is a type row |
> | **F119** | ✅ **UPHELD, UNDER-STATED / REASON REFUTED** | ⛔ the `memset` mechanism is a **`p03`** fact and explains the wrong column; the record's own `domain` forbids the comparison. **Re-state on the stronger reading** → item 128 |
> | **F120** | ⓘ opened ⛔ UNREVIEWED (manager, one probe, 2026-09-15) → ✅ **UPHELD (12/12) / NARROWED** (`_057`) | ⛔ **the build label was wrong in four places**; the benign control under-states. ✅ Both repaired. ⚠⚠ **RESIDUE FROM THE OPENING ROW, AND THE VERDICT CELL DOES NOT SAY IT WAS ANSWERED**: it is *a measurement AND a rule written by the same person in the same sitting*, and the rule (`§A3a`) **binds every future row** — ▶ ***attack the rule, not the `si_addr`***. The `12/12` is the MEASUREMENT half |
> | **F121** | ⓘ opened ⛔ UNREVIEWED (manager, 2026-09-15) → ✅✅ **UPHELD, BOTH HALVES** (`_057`) | ⭐ clean survival; `N12` tracked two further count moves while it ran. ⓘ The opening row's doubt — *"it may not need to enter at all: a validator repair, not a research claim"* — stands; its one LAYER-shaped clause is *law 6 covers prose about code, not only code* |
> | **F122** | ⓘ opened ⛔ UNREVIEWED (manager, 2026-09-15) → ⚠ **UPHELD-NARROWED / REASON REFUTED IN PART** (`_057`) | ⛔⛔ **the repair fixed ONE LIMB of its own mechanism** — six reports on the wrong side of the LIVE/HIST split. ✅ Repaired + `N6d`. ⓘ The opening caution is now spent: it narrowed `F117`, and `F117` has since been **UPHELD, BOTH HALVES** |
> | **F123** | ⓘ opened ⛔ UNREVIEWED (manager, **about the manager**, 2026-09-15) → ✅✅ **UPHELD AND UNDER-STATED** (`_057`) | ⭐⭐⭐ **the check costs 30 SECONDS**, measured and reproduced. §A3a obligation 5 is now **REQUIRED**. ⛔⛔ **ITS LAYER-SHAPED CLAUSE IS STILL NOT VERDICTED AND STILL NOT IN THE LAYER**: *an engineer's own uncertainty may be DEFERRED but not DOWNGRADED; the next task inherits its stated priority, not the manager's.* ▶ **That is what item 129's census tests — a verdict on the INSTANCE is not a verdict on the RULE** |
> | **F124** | ⓘ opened ⛔ UNREVIEWED (the row-11 round) → ⚠ **UPHELD-NARROWED / REASON REFUTED** (`_057`) | ⛔ the control priced the **TEST**, not the discriminant; *"by construction"* holds for the **size leg only**. ✅ Corrected in place. ⭐ **The opening row's instinct was right and is worth keeping as method**: *`P1` was the first prediction to survive in both halves for several rounds, which is exactly when to check it hardest* — and checking it hardest is what broke the reason |
> | **F125** | ⓘ opened ⛔ UNREVIEWED → ⚠ **UPHELD-NARROWED / REASON REFUTED** (`_057`) | ⛔⛔ **both clauses of its disclaimer are false** — see **F127**, which is the bigger finding it produced. ⚠⚠ **THE OPENING ROW'S QUESTION WAS NEVER ANSWERED AND IS NOW BIGGER**: *does it change `F91`'s axis, or is it that claim with a number on it at last?* ▶ `F129` lands on the same axis from a third direction, so **answer it in `_059`, not later** |
> | ⭐ **F127** | ⓘ opened ⛔ UNREVIEWED (`_057`'s own round) → ⚠ **UPHELD-NARROWED / REASON REFUTED** (`_059`) | ⭐⭐ **`F127` IS ITSELF A CASUALTY OF `F129`'s NAME COLLISION**: its claim is true of the **`W`** quantity and **FALSE of `F74`'s**, which is arithmetic over committed records and was therefore available for **all 360 cells all along**. ▶ *"Five rows never measured `inside_share`"* means *"five rows ship no `W` control"* — and `_058` measured **the quantity the rule is not stated in**. ⛔ Its *"the EXACT comparison"* identity claim is false (one rung off). ✅ **The CONCLUSION survives on a ground that needs no bar**: `RECAP_PHP.md` published a one-column, opt/mode-unlabelled cross-language `A1` figure — **`F108`'s fifth thing and its third.** ▶ **Re-state `F127` on `F108`, not on `F74`'s bar.** ⓘ The residue (`ph07`, `ph53`, `ph64`) is **bookkeeping**, not a precondition — reading (b) removes the argument that made it load-bearing |
> | **F128** | ⓘ opened ⛔ UNREVIEWED, then **self**-narrowed by its own sweep (manager on manager, **not** a review — the cell that said *"UPHELD-NARROWED BY ITS OWN SWEEP"* scanned as a verdict and made the backlog uncountable, `F131` §2) → ⚠ **UPHELD / REPLACEMENT RULE NARROWED** (`_059`) | ⭐⭐ **THE KIND-A/KIND-B SPLIT IS NOT A PROPERTY OF THE ARM — it is a property of the arm's RELATION to a finding's CURRENT STATUS, and that status changes without the arm changing.** `N11` was a textbook Kind A arm until the first-in-family premium was refuted at `n = 8`, at which point it became a textbook Kind B arm **with no edit to it**. ▶ **So the rule's second half is the whole mechanism, not a nicety**: *an arm that asserts a published direction **without printing the measured margin** is a Kind B arm that has not been caught yet.* ⛔ **A second gap: the rule has no RETIREMENT condition** — the sweep noticed that on `N6` and did not generalise it. ▶ **Land the rule with BOTH sentences in it**, `width.py` `N4`/`N3b` as the model. ⚠ **And the residue stands: FIVE checkers are still unswept** (`quota`, `citecheck`, `contract_audit`, `preimage_screen`, `fixsurvey`) — `_059` swept `cbaseline_check.py` only. ⓘ Below: ✅ The `N13` defect is real and repaired; ⭐ **a THIRD instance found (`N5`)**. ⛔⛔ **But its RULE as worded is WITHDRAWN — too broad: five correct arms assert a direction legitimately.** Replaced by the Kind-A/Kind-B rule, item 130. ⚠ **Still a manager self-finding, and the sweep was the manager's too** |
> | ⭐⭐⭐ **F130** | ⓘ opened ⛔ UNREVIEWED (manager self-finding) → ⚠ **CONCLUSION UPHELD / HEADLINE REFUTED** (`_059`) | ✅ **The DRIFT is upheld and independently reproduced** (70 vs 69 at `1cc2c0e`, by `git show`-ing the 31 scanned files rather than by worktree; 69/69 at the two commits before). ⛔⛔ **The headline *"A RATCHET THAT NOTHING EVER INVOKED"* is REFUTED — it WAS invoked, by hand, by name**: two task files instruct the flag and `TASK_PHP_051_REPORT.md:55` records the run *and its output*. ▶ **The surviving claim is *no AUTOMATED caller passed it*.** ⭐ **And it is a BIRTH DEFECT, not a regression** — the guard is in the file's first commit; the un-enforced window is ~32 hours and three commits, not the open stretch the tone implied. ✅ **The 70th hit is FOUND and BENIGN** (`RECAP_PHP.md:1812`, `F127`'s own body quoting the defect to criticise it — item 115's class, **eighth** instance), so the ratchet is honest **retrospectively** too. ✅ All eight adjudications agreed on verdict, **three corrected on their REASON**. ⛔ **Item 134's widening: REFUSED, an eighth time, as framed** |
> | ⛔ **F131** | ✅✅ **UPHELD, AND VERIFIED LIVE BY THIS ROUND'S OWN SCOPE** (`_061`) | ✅ **The repair held**: `boxcheck.py` printed `33 rows, 33 distinct, 0 duplicate keys`, so `_061` was correctly scoped **by the artefact this finding repaired**. ⭐ **The only one of the four whose lesson lives in an ARM THAT RUNS, and the only one that has not recurred** — which is §5.0's ruling in one row. ✅ **Its layer-shaped clause may enter**: *a verdict-shaped phrase in a verdict column is a verdict, whoever wrote it* |
> | ⭐⭐⭐ **F129** | ⓘ opened ⛔ UNREVIEWED (`_058`'s own round) → ⚠⚠ **UPHELD-NARROWED, AND REFUTED IN TWO CLAUSES** (`_059`) | ✅ **The name collision is UPHELD and UNDER-STATED** — the gap is **8.9 pp on `ph29` and 0.01 pp on `ph45`**, so it is a measurement, never a constant, and `F129` picked the row where they nearly agree. ⛔⛔ **Its CORPUS clause is REFUTED in two documents** — `RECAP_PHP.md`'s `ph97` `98.84 % → 64.50 %` and `.memory-php/03-numbers.md`'s own `ph52` figures are the **`W`** one — **so the two quantities are INTERLEAVED INSIDE SINGLE SENTENCES, not separated between documents.** ⛔⛔⛔ ***"INADMISSIBLE" IS WITHDRAWN***: `F74`'s bar is **not a gate** (four documents, one of them the layer, one of them the same cell), and the conjunction **admits** `ph55` `c-gcc` vs `c-gcc-h` where A1 reads `+0.0000 %` against **66.14 `Ir`/call**. ⛔ **§2 mislabelled family B as W1.** ⛔ **§4a's *"zero of five"* is wrong in the SELF-CRITICAL direction — it is two of five.** ✅ Every arithmetic claim reproduced under a tool sharing no code with the original. ⭐ **The manager's `P2` — written against his own strongest clause, marked low confidence — is the one prediction that held** |
> | ⛔⛔⛔ **F132** | ⚠ **UPHELD-NARROWED** (`_061`) | ✅ **The repair is right and the tool is committed.** ⛔ ***"Never the number"* is over-stated by its own evidence**: the bare run **failed loudly and stopped the manager mid-edit**, which is the count working. ▶ **The count is a valid TRIPWIRE and an invalid ADJUDICATION** — that distinction is what may enter, not the absolute. ⓘ **Its durable home already exists as an arm that prints** (`cbaseline_diff.py`); §5.0 rules that no document would have helped |
> | ⭐⭐⭐ **F133** | ⚠ **UPHELD-NARROWED · ⛔⛔ TITLE REFUTED** (`_061`) | ⛔⛔ ***"BY ONE AUTHOR"* has no support in the record and the record cuts against it** — two named authors on one file, a third as last committer, a different one on the other. ✅ *"In one file"* stands. ▶ **The rule is re-worded to *what was CHOSEN, not always what was DISCOVERED*** and (iii) re-grounded on (i). ✅✅ **(i) GENERALISES: `ph56`'s repair also copies a sibling arm** (`BP_VAR_R`/`BP_VAR_UNSET` already guarded) — **two rows, and the answer was in a committed control's own header at zero cost.** ⛔ A third row has no instrument; **the cheap generalisation is a grep per row, NOT ten censuses** |
> | ⛔⛔ **F146** | ✅ **CENSUS UPHELD** · ⛔⛔ **CONSEQUENCE CLAUSE REFUTED — BY `ph66`'s OWN COMMITTED CONTROL** (`_063`) | ✅ **The census reproduces to the digit** under a re-run of its own command: `0 / 374` `O0/large` isolated cells across both corpora, `O0/small` + `O3/*` complete, cause is `CG_PLAN`. ⛔⛔ **But the census is over ONE record family (`results*/`) and the claim was about *"committed records"* — and `patterns-php/ph66-hashdel-uncompared/controls/inside_share.json` CARRIES `A1` AT `O0/large` ON ALL 8 CELLS.** ▶ ⭐⭐⭐ **The one row in either corpus whose committed artefacts hold the missing cell is THE ROW THE FINDING WAS WRITTEN ABOUT — and the manager had printed those very values in the session that filed it.** ⛔ **The fallback *"not for free"* is also too strong**: `controls/inside_share.py` is committed, pinned and `--selftest`ed, and it ran as part of the row's ordinary build. ✅ **WHAT SURVIVES, AND IT IS ALL OF IT**: *`CG_PLAN` omits `O0/large`, so a row wanting the matrix at two optimisation levels gets it from a **row-level control**, not from the measurement record; `ph66`'s is the model and the only one so far.* ▶ **That is a note on HOW TO OBEY the rule — the brief's own stated condition for the ⭐⭐⭐ being unearned, so it is withdrawn.** ⛔⛔ **AND IT IS `F142`'s MORAL FIRED ON `F146`**: a census that bounds one population, read as a property of another. ⚠ Second clause (*"where the perf claims live" is obsolete*): **DECLINED at n = 2** (item 123's rule) — **and the question dissolves**, because the row-level control already supplies the cell ✅✅ **AND THE SHARED ERROR LANDED 2026-09-17 AS `.memory-php/04-process.md` LAW 17 — *name the population in the sentence*** (reviewer's resume priority 4, the manager's decision). ⛔ **What entered is the FAMILY STATEMENT, not this finding**: the three instances, the table naming each one's two populations, and the point that **law 6 would have caught none of them because every number was correct, current and re-derivable.** ⚠ **The programme-specificity argument that clears `_061` §5.0's bar is the MANAGER'S WORDING and is marked in the layer as owing a reviewer** — `F53`'s shape has bitten twice. |
> | ⭐⭐⭐ **F143** | ✅✅ **UPHELD, AND CORRECTLY SCOPED** · ⚠ **REASON UPHELD-BUT-INCOMPLETE** (`_063`) | ⭐⭐ **ONE OF ONLY TWO OF SEVENTEEN OBJECTS IN `_063` THAT CARRY NO REFUTATION**, and both are engineer-opened and had already scored themselves against their own falsifier. ✅ **The porting attack FAILS and the finding is about `ph66`, not about how `ph66` was ported** — ⭐ **the leg that makes the scope correct was already in the tree and the finding did not cite it**: `model.py`'s WHICH-ALGORITHM header plus gate stage 2, **already gated on 9 of 13 rows**, is what fixes which algorithm an `R2` must mirror. ⛔ **And `_060`'s `P2` — the *"both are legitimate and they are different rows of the ladder's column"* framing the brief asked to be tested against — is REFUTED BY `ph96`'s OWN `model.py`.** ▶ **So the ladder's *"does the defect survive?"* column does NOT take its value from an unconstrained choice: the constraint exists, it is gated, and the rule the brief asked for is ALREADY WRITTEN.** ⓘ What is owed is a citation, not a rule |
> | ⭐⭐⭐ **F144** | ✅ **UPHELD AND UNDER-STATED** · ⛔⛔ **NOVELTY CLAIM REFUTED** (`_063`) | ✅✅ **UNDER-STATED: `A1` is blind in 6 of 8 C cells, not 2.** ⛔⛔ **But *"the FIRST time the mechanism has been named"* is FALSE — `ph55`'s `NOTES.md` §8b names it VERBATIM**, which is `F131`'s one-home rule biting a novelty claim. ⚠ **The distinction from `F125` SURVIVES, re-grounded**: not *person-choice vs compiler-choice* but **DISSOLVABLE vs UNDISSOLVABLE boundary** — `F125`'s libc call can be written out of the kernel, and an inlining decision cannot. ✅ **And the *"does anything still rest on the share?"* question is ANSWERED AND BENIGN**: rows use the share to **REFUSE** `A1`, essentially never to **CERTIFY** it, and the single certification-shaped use (`ph29` §15e) **already ships its own withdrawal**. ▶ ***"Every use is weaker than it reads"* is TRUE AND VACUOUS.** ⚠ **Scope of that sweep: the 13 rows' `NOTES.md` only** — `.memory-php/`, `RECAP_PHP.md` and the 66 reports were NOT swept (`_063` §10.5) |
> | ⭐⭐⭐ **F145** | ⚠ **UPHELD for *REFUSE* · ⛔⛔ REFUTED for *CATCH*** · ⛔⛔ **REASON REFUTED** (`_063`) | ⛔⛔ **THE FINDING CHANGES ITS OWN VERB BETWEEN ITS TITLE AND ITS LAYER-BOUND CLAUSE** — *refuse* in one, *catch* in the other — and they have different truth values. ⭐⭐⭐ **MEASURED IN VERUS, NOT ARGUED**: a defect-carrying spec function and a **verified refutation of that defect** CO-EXIST IN ONE FILE (`4 verified, 0 errors`), and the hardened predicate fails the same theorem on the postcondition. ▶ **So `R5` CAN be made to CATCH the defect while still computing `R1`–`R4`'s function — the brief's question answered YES.** ⛔⛔ **AND THE STATED REASON IS REFUTED: the block is NOT the cross-rung checksum.** Delete the checksum entirely and the block is unchanged — **it is SOUNDNESS.** ▶ **So the tension is real but it is not the one `F145` names**, and the cross-rung identity requirement is exonerated. ⚠ **What may enter is the narrowed claim about *refuse*, with *catch* explicitly excluded in the same sentence.** ⓘ `_063` §10.3-10.4: *N2 proves non-provability, not falsity* is a formal gap the reviewer flags and did not stress-test, and the witness theorem was **not** dropped into the real 1 647-line `verus.rs` (resume item 11) |
> | ⛔⛔⛔ **F142** | ✅ **ADMISSION UPHELD** · ⚠ **CONSEQUENCE UPHELD-BUT-IMMATERIAL** · ⛔ **MORAL REFUTED** (`_063`) | ✅ **The stale classification is real and admitted.** ⚠⚠ **BUT AT THE DEFENSIBLE SPLIT EVERY PUBLISHED FIGURE IS BIT-IDENTICAL** — the `0.5/0.5` the manager assumed rather than measured **does not move a single published number**, so the consequence half is immaterial and the finding's alarm was mis-aimed. ⛔ **THE MORAL IS REFUTED: it is NOT *"`F132`'s class one level up"*, because `F132`'s remedy — adjudicate the SET by unit text — WOULD NOT HAVE CAUGHT `"040"`.** ▶ **They are SIBLINGS, not parent and child**, and ⭐ **the FAMILY statement is the part that may enter the layer**, not the subsumption. ⭐⭐⭐ **AND `F142` IS THE FINDING THAT NAMES `_063`'s OWN HEADLINE ERROR** — a rate or census measured over one population and asserted about another — **which `F146`, `F141` and the `_063` brief itself then each committed, all within one day. n = 3 is a rate (item 123)** ✅✅ **AND THE SHARED ERROR LANDED 2026-09-17 AS `.memory-php/04-process.md` LAW 17 — *name the population in the sentence*** (reviewer's resume priority 4, the manager's decision). ⛔ **What entered is the FAMILY STATEMENT, not this finding**: the three instances, the table naming each one's two populations, and the point that **law 6 would have caught none of them because every number was correct, current and re-derivable.** ⚠ **The programme-specificity argument that clears `_061` §5.0's bar is the MANAGER'S WORDING and is marked in the layer as owing a reviewer** — `F53`'s shape has bitten twice. |
> | ⛔⛔⛔ **F141** | ✅ **UPHELD as an `n = 1` EXISTENCE PROOF** · ⛔⛔ **SCOPE REFUTED** (`_063`) | ✅ **It IS a finding, not a prediction**: the old gate is a predicate, `ph66`'s trigger returns `rc=0`, the predicate returns *skip*. **That is arithmetic over the text.** ⛔⛔ **THE `61.3 %` IS A POPULATION SUBSTITUTION** — it is a rate over *corpus reproducers* asserted about *the row's authored trigger*, two different things — **and the selection-effect test the brief proposed is UNTESTABLE at n = 2 built temporal rows.** ▶ **RE-TITLE IT ON THE `ph66` INSTANCE AND THE PREDICATE, AND DELETE THE AXIS RATE.** ⛔ **The finding had already struck its own uncomputed *"all twelve built rows fault"* sentence AND THEN KEPT A SECOND, LARGER UNCOMPUTED RATE IN ITS TITLE.** ⚠ Denominator note: with `ph66` the census population is **13**, not 12; the *"records a fault marker"* classification is prose-based and the reviewer did not rely on it. ✅ **The DELIVERABLE is unchanged and is item 141: the arm, not the wording** ✅✅ **AND THE SHARED ERROR LANDED 2026-09-17 AS `.memory-php/04-process.md` LAW 17 — *name the population in the sentence*** (reviewer's resume priority 4, the manager's decision). ⛔ **What entered is the FAMILY STATEMENT, not this finding**: the three instances, the table naming each one's two populations, and the point that **law 6 would have caught none of them because every number was correct, current and re-derivable.** ⚠ **The programme-specificity argument that clears `_061` §5.0's bar is the MANAGER'S WORDING and is marked in the layer as owing a reviewer** — `F53`'s shape has bitten twice. |
> | ⛔⛔⛔ **F140** | ✅✅ **UPHELD AND UNDER-STATED** · ✅ **CAUSAL CLAIM UPHELD ON NEW GROUND** · ⭐⭐ **THE ARM IS A REPAIR, MEASURED** (`_063`) | ✅✅ **UNDER-STATED BY 4×: at `_061`'s dispatch commit the arm would have printed FOUR routed items — 125 126 135 137 — and `_061` scoped ONE.** The finding named the instance it noticed. ⭐⭐⭐ **THE REVIEWER BACK-TESTED THE ARM AGAINST HISTORY, WHICH ITS AUTHOR DID NOT** — running BOTH the current regex and the exact pre-widening one (`git show 3f8298e`) at six dispatch commits. **WIDE and NARROW agree at every historical commit (2,2,2,4,4)**, ▶ **so the arm is NOT tuned to the instance that produced it: it reproduces the miss in the form it had BEFORE the tuning.** ⛔ **THE BRIEF'S COUNTER-EVIDENCE IS REFUTED AS A POPULATION SUBSTITUTION** (*"`_059` folded four"* counts items of ANY routing; the arm counts items routed TO A REVIEWER, and only 2 existed then). ▶ **RECALL OVER THE RIGHT POPULATION: `_057` 2/2 = 100 %, `_061` 1/4 = 25 %, `_063` 9/9 by the arm.** ⭐⭐⭐ ***Recall was perfect at a two-item list and fell to a quarter when it doubled*** — a better ground than the finding's own. ⛔⛔ **AND `boxcheck.py:142-147`'s ACCOUNT IS FALSE IN ITS LOAD-BEARING WORD**: *"the arm matched NONE of them"* — **measured, the pre-widening arm matches 145, 146 AND 147; it misses only 144 (and 139). The widening bought TWO items, not four.** ✅ **Corrected in the file** |
> | ⭐⭐⭐ **F139** | ✅ **MEASUREMENT SETTLED** · ⛔⛔ **THE INFERENCE REFUTED** · ✅ **THE ACTION IS RIGHT ANYWAY** (`_063`) | ⛔⛔ ***"FOUR HOMES, FOUR FAILURES, THEREFORE LOCATION IS NOT THE VARIABLE"* IS FALSE.** ▶ **The axis is not *which document* — it is TEXT vs AN INVOKED ARM.** All four failures are **ONE cell** of that split, and **the other cell has ≥ 8 HOLDS — two of them cited in the ruling's own last paragraph.** ⛔ **So the ruling generalised from a single cell while quoting counterexamples from the other.** ✅ **Its ACTION survives on the corrected reason**: an arm that runs beats text, which is what `_061` §5.0 prescribed. ⭐⭐⭐ **AND ITEM 125's CENSUS PROVES IT ON `F123` ITSELF** — `F123`'s repair was a PROSE BOX, three rounds carried it, **none did the work**, and `F140`'s printing ARM scoped it on its first run. ⚠ **`n` discipline, stated**: the eight holds are drawn from this programme's own narrative and so are selected for having been written down — **the reviewer argues the bias cuts toward `_061`'s position, not its own.** ▶ **Item 129 stays CLOSED; its stated reason is refuted and must be re-recorded** (resume item 9) |
> | ⭐⭐⭐ **F137** | ⚠⚠ **CLAUSE 1 UPHELD · ⛔⛔ CLAUSE 2 REFUTED · ⛔ CLAUSE 3 REFUTED-AS-WRITTEN, UPHELD-ON-NEW-GROUND** (`_061`) | ⛔⛔⛔ **Refuted by the row it named as its own falsifier**: `ph97`'s C rung faults in **all eight** builds. ⛔ **And it named the wrong input** — `adversarial-nullvalue.bin` is clean in all eight; the faulting one is `absent`, as the row's own `gen.py` says. ✅ **What may enter is the NARROWED rule, which is stronger as a rule and weaker as a headline**: *an optimiser can convert a detected fault into a silent wrong answer when the UB licenses folding a **branch** whose outcome is the answer, and does not when the faulting load's **value IS** the answer* — with `ph97` as the negative instance **in the same sentence**. ⛔ **NOT the two tables as parallel**: the C row is the shipped R1, the Rust row a guard-deleted **mutant that is no rung**. ⓘ The third outcome (**hung**) is real and is on the Rust side |
> | ⭐⭐⭐ **F136** | ✅ **CONCLUSION UPHELD AS MEASURED · ⛔⛔ HEADLINE REFUTED · ⭐⭐ MECHANISM UPHELD AND UNDER-STATED** (`_061`) | ⛔ ***"IS FREE" IS AN `A1, O3/isolated` FACT.*** At `O0/isolated` in **W1** the two repairs differ by `−2.24`…`−19.58 Ir/call` on four cells while A1 reads `+0.0000`, and **upstream's no-output repair is the DEARER one**. ✅ **The four published cells reproduce to the digit** — it is the TITLE that travels past its cell. ✅ **Mechanism measured per symbol for the first time**: `−83 419` leaves the callee, `+38 581` arrives in the caller, **`+0` in `kernel`**, which is exactly why A1 saw none of it. ▶ **May enter with the INLINING narrowing in the same sentence**; ⛔ not the bare *"free"*. ⚠ **Item 137's live consequence** |
> | ⛔⛔⛔ **F135** | ✅ **CONCLUSION UPHELD · ⛔ *"EXACTLY AS SURELY"* REFUTED** (`_061`) | ✅ **§0.1's population reproduces exactly**; `citecheck.py`'s `expect=1` is the only observation-captured expectation left. ⛔ **The two mechanisms are not equally severe**: editing the INPUT destroys evidence, editing the EXPECTATION leaves the failure fully visible — and this finding was itself recovered from the registry text. ⛔⛔ **A LIVE THIRD MECHANISM FOUND**: `width.py` and `php_null.py` — **the two files law 16 calls the model** — ship passing `--selftest`s the registry never runs, so `st_expect: None` conflates *has none* with *has one, unfiled*. ✅ **Lands as a CLAUSE ON LAW 6, not a new law** |
> | ⛔⛔⛔ **F138** | ⚠ **CONCLUSION UPHELD (keep SEPARATE from `F132`) · ⛔⛔ REASON REFUTED IN ITS LOAD-BEARING WORD** (`_061`) | ⛔⛔ ***"I DID RUN THE TOOL" IS FALSE.*** `boxcheck.py`'s `main()` already prints the members, in a line the manager wrote **the day before** as part of `F131`'s own repair; what ran was a bespoke sweep that reimplemented the reporting path. ⭐⭐ **That makes it MORE distinct from `F132`, on a ground it did not state**: `F132` = *a count standing in for a set* (remedy: **diff the set**); this = *a one-off caller not inheriting the checker's reporting* (remedy: **run the checker**). ▶ **The corrected lesson: *"I called the tool's function" is not "I ran the tool."*** ⛔ Its de-dup rule is the right answer from the wrong rule, and its falsy-return residue is refuted in mechanism (`len(None)` raises) |
> | ⛔⛔⛔ **F134** | ✅ **DISCLAIMER CLEAN · ⛔ ITS REMEDY REFUTED** (`_061`) | ✅ **The body does carry its own caveat and nothing else implies otherwise** — the *"1 of 170"* disclaimer is clean, read end to end. ⛔⛔ **Its remedy — *move the trap to where a PERSON meets it* — is REFUTED BY `F139`**, which is that remedy's experiment: a person-facing protocol section, in capitals, lost by 9h25m to its own author. ✅ **Its core sentence survives as prose** (*a trap documented only where the code meets it is documented for the code*); ⛔ **the converse it implies does not** |
> | ⛔⛔⛔ **F147** | ⛔ **UNREVIEWED** | ⛔ **NOTHING MAY ENTER.** ⚠⚠ **ATTACK THE MECHANISM, NOT THE COUNT**: the claim is that four instruments for the scratch-dependency class in eight days were EACH scoped to the instance that prompted them, and the falsifiable part is **law 11's `F88–F101` capturing 5 of 22 (23 %)** — re-derive it with `python3 .tasks-php/probes/scratchdeps.py`, do not read it here. ⛔ **Row 4 of that table is MINE AND IS NOT EXEMPT**: `scratchdeps.py` resolves by BASENAME, cannot tell a probe I wrote from upstream source I extracted, and scans two document families — **the pattern predicts a row 5 and the reviewer should try to be it.** ⚠ **`LIVE` is a CANDIDATE SET, not a defect count** (`F132`); if this finding is quoted anywhere as *“48 defects”* that is the error to report. ⓘ Parts (c′) and (g) were **found by `PROMOTE_001`'s engineer against my own brief** and are already conceded — the open question is whether (b)'s *booked my false positive against the reviewer* is fair to `_063`, and I am not the one to judge it. |
> | ⛔⛔ **F148** | ⛔ **UNREVIEWED** | ⛔ **NOTHING MAY ENTER.** ⚠ **n = 4 and it says so** — two identifier probes right, two prose probes wrong, verified by reading the matched line; the other six probes that session were never checked and are NOT evidence. **The mechanism is the argument; the count illustrates it.** ▶ The rule it proposes — *never grep prose to decide presence; grep an IDENTIFIER or read the section* — **would forbid checks this programme runs constantly**, so the scope clause (*locating* text is fine, *asserting absence* is not) is the load-bearing part and the place to attack. ⚠ It also supersedes `NULLCTL_001.md` §10's prescription (*“a short unwrappable token”*), which my own `coin flip` homonym refutes — **check that supersession is real and not just a restatement.** |
> | ⛔⛔⛔ **F149** | ⛔ **UNREVIEWED** | ⛔ **NOTHING MAY ENTER.** ⚠⚠ **THE CONTROL IS THE PART TO CHECK FIRST**: all four of `ph66`'s published `O0` family-B numbers reproduce to the digit at BOTH pad resolutions, so `OPT-5` is pinned to a committed figure and not to its own output — **if that is wrong, everything below it is.** ▶ The falsifiable claim is the 32-pad table: re-run `python3 `.tasks-php/php50_align_sweep.py --opt O0 --row ph66-hashdel-uncompared --pads 32`. ⛔ **The `large`/gcc cell is the whole finding** — step `8.89` against an effect of `6.12`, so `|d|/step = 0.69` and the sign is not established. ⚠ **Attack (b) hardest**: I claim a 4-pad screen returned the OPPOSITE verdict on both axes for that cell, which if true means **every sparse sweep in this tree is suspect for a DIFFERENCE** and that is a much larger claim than the row it is about. ⓘ **(d) is a cost statement, not a repair**: `ph66`'s `NOTES.md` is in `source_sha256`, so the summary sentence is batched to that row's next task (item 151) rather than fixed here. |
> | ⛔⛔ **F150** | ⛔ **UNREVIEWED** | ⛔ **NOTHING MAY ENTER.** ⚠⚠ **THE VERDICTS ARE THE CLAIM, NOT THE `17`.** Each row of `scratchdeps.ADJUDICATION` is a reading of ONE citing sentence — ▶ **re-read the sentences, not the table**, and the cheapest attack is the `HISTORY` bucket: I ruled 6 citations *not evidence* and each is a judgement I made about my own prose. ⛔ **ONE ROW WAS ALREADY WRONG** — `F102` was ruled `RESTS` and the generator had been promoted four days earlier under a NEW NAME (`asan_fill_byte.c`), which the basename resolver cannot see; caught by `_064`'s engineer, not by me. ▶ **So ask of every `RESTS`: is there a RENAMED twin?** ⚠⚠ **AND THE SEVERITY CLAUSE WAS WRONG IN PUBLIC** — *"11 of 13 UNREVIEWED"* is **4 reviewed / 4 not / 5 with no marker**, corrected in place; **`F148`'s own defect, by its own author, in its own session.** ⭐ The *"`CLAUDE.md` Don't #1 never says WHERE"* mechanism is the part I most want attacked: it is an argument about why careful people produce this defect, and its first exhibit refuted it |
> | ⛔⛔⛔ **F151** | ⛔ **UNREVIEWED** | ⛔ **NOTHING MAY ENTER.** ⭐ **THE MEASUREMENT IS CHEAP TO REPRODUCE AND THE CLAIM IS NOT THE `118`** — run `citecheck.py` and read the new block. ▶ **The falsifiable half: *both prior repairs were scoped to the file their instance touched.*** That is a claim about `git log` and the comments at `citecheck.py:138` and `:150`, and it is checkable. ⚠ **The `ph53/verus.rs` instance is the load-bearing evidence** — if that citation were NOT the one named in the F99 repair comment, the finding is just a coverage gap. **Check that identity first.** ⛔ **What I did NOT establish**: whether any of the 118 is a real dangling claim rather than a provenance note. **I say so in the finding; verify I say it loudly enough** |
> | ⛔⛔ **F152** | ⛔ **UNREVIEWED** | ⛔ **NOTHING MAY ENTER.** ⚠⚠ **THE SITE IS THE ENGINEER'S, THE CENSUS IS MINE** — `_064` found `PROTOCOL_PHP.md`'s citation while repointing; I measured the other seven documents. ▶ **Attack the `n = 3` claim**, because that is the only part that generalises: is `F147`(d) / `F151` / `F152` really **one** mechanism, or am I grouping three ordinary scope bugs under a slogan? ⛔ **`F53`'s shape is exactly this risk** — *a shared upstream fix is not evidence of a shared mechanism* — **and it is MY finding**, so I have no excuse for the pattern-match. ⚠ **The 9 dead pointers are a fact and the mechanism is an argument; score them separately** |
>
> #### ⭐⭐⭐ `F96`, PER GROUP — **SEVEN groups, not the four I wrote** (`_055` §1.1)
>
> | group | verdict |
> |---|---|
> | **(a)** the eight gate quotes | ✅ **Seven reproduce** (`forbidden_hits` **is** nested under `idiom_audit`; both `identity` rows `differ`/`differ` as pinned). ⛔ **`contract_sha256 7013be6f7c1c` is a STATE quote, two re-gates stale**: correct at `4297b1d` → `c41ffad2b795` at `bee710e` → `6924e66fde49` at `b754da4`. ▶ **Repair is the EVENT form, not deletion** |
> | **(b)** the 4-prediction ledger | ⚠ **R3 VERDICTED by `_042` §3**, and ⛔⛔ **THIS — not the novelty claim — IS THE GROUP `_047` CHECKED.** ⛔ **R2 / R4 / R5 UNREVIEWED, and they are the ONLY clauses of F96 still owed** |
> | **(c)** result 2 | ✅ **VERDICTED TWICE, SPLIT ALONG CONCLUSION/REASON.** `_050`/F110 #4 **confirms the conclusion on its own stated falsifier**; `_053`/F113 **refutes the stated REASON** (§B1a's O(1) precondition). ⓘ ⭐ **A verdict filed under another finding's number is STILL a verdict — the table's one-cell-per-finding shape is what forced the mis-filing** |
> | **(d)** results 1/3/4 | ✅ **`A1 −1.253 %` reproduces exactly**, as do *"largest of the three"* and *"n = 3"*. ⛔ **The sentence owes INPUT and OPT/MODE** (`large.bin` reads `−0.494 %`; `O0` reads `−16.870 %`) and ⭐ **the C-compiler clause DOES NOT APPLY — a Rust→Rust pair, and say so rather than skip it.** ⛔ **It also strips the row's own caution** (`NOTES.md:1118-1123`) |
> | **(d′) the NOVELTY claim** | ⛔⛔ **IT WAS NEVER THE CLAUSE WITHOUT A SECOND METHOD, AND `_047` NEVER CHECKED IT — MY CELL SAID IT DID, AND THAT WAS A FALSEHOOD IN THE BLOCK THAT GOVERNS THE LAYER.** ✅ Mechanism half **UPHELD by three routes that PRE-DATE the build** — `CATALOGUE.md:752`, `spec.md:577`'s `cwe_note`, `index.csv`'s CWE-824 — plus a measurement. ⛔ ***"first in-bounds uninitialised read"* is true only of BUILD ORDER** (T3 is *"initialised before read"* and has five rows); ⛔⛔ ***"no built row priced that"* was true at 6 rows and is FALSE at 10** — `ph52` prices one |
> | **(e)** the bracket event | ✅ **reproduces, and it is the CONTROL for the state-vs-event rule** — `16/0` then, `22/0` now, because a bracket is quoted as an event |
> | **(f)** the `index_mut` settlement | ✅ **reproduces in two minutes** — `~/tools/verus/vstd/std_specs/slice.rs:43-48` |
> | **(g)** the §8 pointer | ⚠ **SUPERSEDED, not unreviewed** — `_042`/F100 searched both endpoints |
> | **(h)** the meta-claim about falsifiers | ⛔ **NOT A MEASURABLE CLAIM** — a methodological opinion inside an evidence-gated finding. **Move it to `04-process.md` or drop it; do not verdict it** |
>
> ▶ **STILL OWED ON `F96`: R2, R4 and R5 of the ledger. Nothing else.**
> ▶ **MAY ENTER `.memory-php/`:** (a) in **event form**, (c) **with BOTH verdicts in
> the same sentence**, (d) **with input + opt/mode + the row's caution**, (d′)
> **mechanism half only, corpus half re-dated**, (e), (f). ⛔ **NOT (b)'s R2/R4/R5. NOT (h).**
>
> ✅✅ **`TASK_PHP_057` CLOSED ALL THIRTEEN PLUS `R2`/`R4`/`R5` IN ONE ROUND —
> the largest backlog since the mining wave, cleared.** ⛔⛔ **AND *"ALL
> THIRTEEN"* IS WHY THE HISTORICAL TREND NUMBERS CANNOT BE READ OFF THIS TABLE:
> `_057`'s verdicts were APPENDED rather than APPLIED, so `F120`–`F125` stayed
> countable as open for six commits afterwards** (`F131`, and **`F138`** for what
> that did to the measurement). ▶ **Any backlog series over commits before
> `c868e60` must be DE-DUPLICATED or labelled unknown; the raw row count there is
> inflated by six.** ⓘ The old *"trend: 14 → 2 → 7 → 1 → 4 → 2 → 6 → 13 → 1"*
> line is **struck**: its later terms are exactly the raw counts `F138`
> refutes, and a series is the one shape where a single bad term poisons the
> reading of every other.
>
> ⛔ ~~**NEXT REVIEW SCOPE, AND IT IS DISPATCHED AS `TASK_PHP_059`: `F129` →
> `F130` → `F127` → `F128`.**~~ **STRUCK 2026-09-16 — `_059` RAN AND LANDED; a
> line that opens *"NEXT REVIEW SCOPE"* scans as live however old it is.**
> ▶ **The scope of the round in flight lives in the START HERE box and nowhere
> else** (`F131`'s rule: one home per fact). ⭐ **The reasoning below is kept as
> a dated example of how a scope is argued, not as an instruction** —
> ⭐⭐⭐ **`F129` outranked all three**: it redefines
> what every published `inside_share` figure means, it withdraws the label from
> the programme's most-cited number, and it rests on a quantity that **exceeds
> 1.0 on 4 % of the corpus** with no explanation.
> ⚠⚠ **And it is the case law 12 is sharpest about — a finding whose numbers the
> MANAGER verified and whose conclusions nobody has challenged.** `F127` is a
> reviewer finding that `_058` tested directly; `F128` is a manager self-finding
> narrowed by a manager sweep, which is not a review.
> ⛔⛔ **THIS LINE SAID *"then `F127`, then `F128`"* AND *"Backlog is 3"* — WRITTEN
> BEFORE `F130` LANDED AND NEVER EXTENDED, so the ⭐⭐⭐ finding in the queue was
> missing from the queue's own scope line.** ▶ **NO COUNT LIVES HERE NOW. The
> backlog is the set of rows in the table above whose verdict column opens
> `⛔ UNREVIEWED` — read them off, do not trust a numeral** (`F121`'s law: a
> count in prose ABOUT a structure rots exactly like one inside it).
>
> ⛔⛔⛔ **AND THIS PARAGRAPH ALREADY PROVED ITS OWN POINT, IN UNDER FIVE MINUTES.**
> It first ended *"today that set is `F127`, `F128`, `F129`, `F130`"* — and then
> `F131` was filed, four minutes later, **by the same person in the same sitting**,
> and the enumeration was stale. ⭐⭐ **THE REPAIR IS TO DELETE THE LIST, NOT TO
> UPDATE IT**: a list one line from the table looked safe precisely because it was
> close, and closeness is not freshness. ▶ **The set is DERIVED, here, every time
> it is read, and it is written down nowhere.** ⓘ `F128` only became derivable at
> all when its verdict cell stopped scanning as a verdict — `F131` §2.
> ⛔ **NOTHING IS OWED ON `F96` ANY MORE.** R2/R4/R5 are verdicted: R2 upheld
> (**0 of F108's 5** things paid), R4 narrowed (*"outside both arms"* is FALSE —
> arm 2 holds on the clang column F96 never looked at), R5's **conclusion
> refuted** (the prediction stands; *"half-refuted"* over-claimed).
>
> ⛔ **SEVEN THINGS `_050` §8.1 FORBIDS THE LAYER**, and they are enumerated in
> its report. ▶ **Read that list before adding anything from `F109`, `F110`,
> `F96` or item 112.**
>
> ⭐⭐ **F109 WAS HELD BACK BECAUSE THE LAST TIME A ROW LANDED I PUT ITS MATERIAL
> IN THE LAYER UNMARKED. HOLDING IT BACK WAS RIGHT: the refinement turned out to
> be a rule the layer already carried.** ▶ **`TASK_PHP_053`'s verdicts are IN THE TABLE ABOVE, not appended here — the table governs** (item 73).
>
> ⭐⭐⭐ **THE ROUND'S OWN HEADLINE: OF THE SIX FINDINGS IT VERDICTED, ONE WAS
> REFUTED OUTRIGHT, ONE LOST ITS HEADLINE CLAUSE, THREE WERE NARROWED AND ONE WAS
> UPHELD-AND-UNDERSTATED. NOT ONE SURVIVED AS WRITTEN.** ▶ **That is the fifth
> consecutive round to refute manager or engineer claims, and it is now the
> strongest evidence on file for `04-process.md` law 12.**
>
> ⛔⛔ **AND IT REFUTED THE ONE THING THAT WAS WAITING ON THE USER.** Item 105's
> recommended **option (b) does not exist** — `harness-php/gate.py` is forbidden by
> its own header from hosting a gate stage, cannot make itself mandatory, and
> `root.py` rebinds **paths, not verdicts**. **I had read `CLAUDE.md`'s banner as a
> verdict override.** ▶ **The question to the user is now (a) or (c), and (c) is
> what `gate.py`'s header itself prescribes.**
>
> ⚠⚠ **THE BANNER STORY, KEPT BECAUSE THE DEFECT WAS MINE.** I landed seven
> entries into the authoritative layer **unmarked**, one day after writing this
> block and after landing law 12. They were marked in a pre-handoff audit, and
> `_047` has now closed the cycle on all but F96. ✅ **The audit is the only reason
> the material was labelled when the reviewer reached it.**
>
> ⓘ ~~**Backlog trend: 14 → 2 → 7 → 1.**~~ ⛔ **STRUCK 2026-09-15: a stale PREFIX
> of the live series eight lines above it** (`14 → 2 → 7 → 1 → 4 → 2 → 6 → 13 → 1`).
> ⭐ **A truncated series is worse than a wrong one — it reads as complete, and
> a reader who scrolls to the nearest copy gets the oldest.** Same block, same
> defect class as the six duplicated rows: **two homes for one fact.**

✅✅ **`TASK_PHP_043` CLOSED THE CYCLE ON 12 OF 14.** 1408 lines; **8 findings got
a genuine second method** (F91 F92 F94 F95 F98 F99 F100 F101), **4 got the bounded
bar** (F88 F89 F90 F93), **2 are UNREVIEWED** (F96 F97). ⛔ **It obeyed the stop
instruction and named where its depth ran out — after §5.7 — which is exactly
what the task asked for and is why the table below can be trusted.**
⚠ ⓘ **§8's own prose says *"9 verdicted, 5 UNREVIEWED"* while its table shows
12 and 2. The TABLE governs** — a stale sentence from an earlier draft, no
research consequence.

| | findings | may enter `.memory-php/`? |
|---|---|---|
| ⭐ **reviewed, eligible AS WRITTEN** | **F93 · F95 · F99** · **F90** (as a struck record) · and the older **F83 · F84 · F85 · F86** | ✅✅ **LANDED 2026-09-13.** The oldest rule-9 debt is discharged |
| ⚠ **reviewed, eligible ONLY WITH THE NARROWING IN THE SAME SENTENCE** | **F88 · F89 · F91 · F92 · F94 · F98 · F100 · F101** | ✅✅ **LANDED 2026-09-13, narrowings APPLIED and not appended** (item 73) — `00-corpus` F94 · `02-ladder` item 83 + the `inside_share` ruling + the endpoint law · `03-numbers` F98's four qualifiers, F88's denominator, F92's target-dependence · `04-process` laws 6–12. ⛔ **The 2026-09-12 *"still a FLAG … nothing below is authoritative yet"* banner in `02-ladder` is REMOVED** |
| ⛔ **cycle still OPEN — THE ONLY THING STILL BARRED** | **F96 · F97** | ⛔ **NO.** F96 is a build record plus a four-prediction ledger with no cheap second method; **F97 needs `verus_run.py` and `controls/r4_nowitness.rs`'s error text, and F100 promotes it from argument to a MEASURED FLOOR on three arms nobody has re-run** |

### ▶ WHAT THE ROUND COST THE PUBLISHED RECORD — **ONE HEADLINE AND FOUR QUALIFIERS**

1. ⛔⛔ **F100's *"BOTH ENDPOINTS MOVE"* loses its R4 half.** Item 83 ruled **(a)**;
   `r4_endpoint_degenerate → true`; every in-contract R4 variant is **dearer**.
2. ⛔ **F94's *"refuted twice independently"* becomes *"refuted once"*** — F95's own
   repair withdrew the screen route and F94 still cited it.
3. ⛔ **F98's `+21.8 %` owes four qualifiers** and is measured **against a Rust
   control, not against the C**; **only ~44 % of it is the witness.**
4. ⛔ **F101's stated consequence is backwards** — **F77 is SAFE**, and the
   defect's direction is why.
5. ⛔ **F91's axis is refuted as a general statement** by its own fifth table row;
   its `|B/A|` ratio survives.

⭐⭐ **AND NINE NEW DEFECTS, NONE OF THEM ON THE TASK'S LIST** — including **a
FIFTH shared-`spellings.py` defect**, which is **item 81's law holding for a
fifth time and predicted in advance.** Items **84–92**.

⚠⚠ **THE ROUND ALSO REFUTED THE MANAGER'S ROUTE TO ITS OWN BIGGEST RESULT.** My
evidence for item 83 was an over-read of a sentence about *polarity*;
`check.py:2198-2212` measures that reading at **41 misses of 158 obligations, all
41 non-defects.** ▶ **The right answer arrived by a clause nobody had read — and
item 83's own summary sentence turned out to be the thing that made it look
undecidable for two tasks.** ⭐ **That is the third review round in a row to
refute manager claims (F80/F82/F83/F84 → F90 → this), and the pattern is stable
enough to plan around: a manager finding from one probe or two rows should be
assumed narrowable until a reviewer has had it.**

---

## Findings

*(no ROW findings yet — the first row has not been built. F1–F7 are the mining
wave's and Phase 0's results; **F8–F10 are new this round.** F8 and F9 are
MANAGER work and are **unreviewed** — `TASK_PHP_008` attacks F8, and F9 is a
measurement anyone can re-run. `PROTOCOL.md` rule 9: none of this reaches
`.memory-php/` until it survives review.)*

> **Index** — F1 citation frames · F2 CSV authoritative · F3 `crashes_pristine`
> not absence · F4 the 123-ASan misread · F5 third allocator truncation · F6 the
> shim invented defects · F7 the digest gap fires · **F8 kills priced at the wrong
> frame** · **F9 no spatial ASan report is in PHP code** · F10 a grepping guard has
> a spelling · F11 ask the compiler · F12 three size rules on an invented number ·
> **F13 a refuted mechanism is not a licence** · F14 `0 STALE` ≠ pinned · F15 the
> cheapest correct design · **F16 wrong enumeration ≠ unboundable** · F17 the
> deadlock that denies itself · F18 whitelists fail on contact · F19 success
> conditions do not travel · F20 one `..` too few · **F21 auditing only what you
> doubt** · **F22 a kill written as a set** · F23 citations inside the citation
> finding · F24 shared header, not directory · F25 the `ph11` measurement · F26
> the fix is a 1.4 KB fetch · F27 set-kills, three instances · F28 demotion cost ·
> **F29 the 2004 fix is dead AND incomplete** · F30 negative-cost safety check ·
> F31 two frozen-harness limits · F32 ⚠ the manager arbitrated the un-arbitrable ·
> **F33 the first ladder** · **F34 the guard moved to the prologue** ·
> **F35 ⚠⚠ this box's `grep` is silently blind to `string.c`** · **F36 the next
> batch's four fixes, and two of them DELETE the guard** · **F37 the kills that
> survived the audit are the ones written down as settled** · **F38 ⚠⚠ the
> `fix_commit` was a column in the corpus index, and it is not always THE fix** ·
> **F39 ⚠⚠ ph03's ladder is a pair of spellings and its own contract says so** ·
> **F40 the fix hunt is done for the whole catalogue, once** · **F41 row 2, and
> the two rows disagree about what safety costs** · **F42 ⚠⚠ row 2's headline
> refuted by construction, and F39's direction withdrawn** · **F43 ⭐⭐⭐ PHP
> deleted half its own security fix, and stage 7h had already said why** ·
> **F44 ⚠⚠⚠ 2 of 13 kills correct as written; the rate tracks the TEST, not the
> rows; and "merged by the corpus itself" is the weakest evidence there was** ·
> **F45 ⭐⭐⭐ a defect made invisible by the commit that fixed its warning** ·
> **F46 ⭐⭐ the catalogue's mechanism sentences hold; its `▸ trigger` lines do
> not, and that is the half a build task runs** · **F47 ⭐⭐⭐ row 2 rebuilt: it
> was shipping a rung PHP itself calls a bug, and no strength of
> memory-safety-only proof would have moved** · **F48 ⚠⚠⚠ I accepted a refusal and then landed the
> same rule with the verbs changed** · **F49 ⭐⭐⭐ the stop condition fired: 3 of
> 9 new rows' triggers failed, and F46 predicted which half would** · **F50 ⭐⭐ a
> fix commit is a CENSUS of its defect's siblings — `ph16`'s patches four sites
> and we catalogued one (MANAGER, UNREVIEWED, n = 1)** · **F51 ⚠⚠ the committed
> claim layer rests on gitignored scratch in ten places, two already gone —
> including the catalogue's own coverage claim** · **F52 ⚠⚠⚠ the probe made the
> state it was measuring, and so did mine, twice, the same week — `ph94`'s
> original claim is restored** · **F53 ⚠⚠⚠ a shared upstream fix is not evidence
> of a shared mechanism; `PROTOCOL_PHP.md` §G replaces the folklore rule** ·
> **F54 ⭐⭐ a declaration can be wrong in every number and right in every verdict** ·
> **F55 ⚠ the preflight record is keyed by the name you typed** ·
> **F56 ⚠⚠⚠ the compiler was already enforcing the bound the row is about, at +60.6 %** ·
> **F57 ⭐⭐⭐ row 3: ASan blind, Miri fires, and the oracle was in upstream's own frame** ·
> **F58 ⭐⭐ the census channel is real — 12 sibling sites from 6 of 12 commits — but
> the ≥5-file selector carries no signal; a NAMED WRAPPER does** ·
> **F59 ⚠⚠ `ext/sockets/` was built and fuzzed and has zero corpus rows** ·
> **F60 ⭐ `ph16` guard (c) measured — and the probe was wrong TWICE, both
> answer-encoding** · **F61 ⚠ the date and id-spread selectors measured,
> NEITHER promoted** · **F62 ⚠⚠ the survey was blind to the corpus's THIRD id
> namespace and printed a clean bill throughout** · **F63 ⚠⚠⚠ item 45's premise
> was wrong, and the cause was a `break` in the manager's own tool** ·
> **F64 ⭐⭐ the PRE-IMAGE SCREEN excludes — ⚠ but cite 26/43, and see F68** ·
> **F65 ⭐⭐ row 4 (`ph29`): the shim is faithful and NEITHER stage of the
> upstream fix removes the defect** · **F66 ⭐⭐⭐ `ph64`'s R1h — the cleanest
> backport yet, the repair is at a THIRD site, and the catalogue's oracle
> MEASURES NOTHING** · **F67 ⭐⭐⭐ `ph16`'s negative `R3−R4` is a RESULT: the two
> rungs are cheapest under DIFFERENT spellings** · **F68 ⚠⚠⚠ `NOT-THE-REPAIR`
> is not a proof of exclusion for 17 of 43, and F64's own figure was wrong** ·
> **F69 ⭐⭐ item 48 was TWO QUESTIONS WEARING ONE NUMBER, and §F5 was right** ·
> **F70 ⚠⚠⚠ a TRUE SENTENCE ON THE WRONG SUBJECT, and nothing about it read as
> invented** · **F71 ⭐⭐⭐ ROW 5 IS THE FIRST TEMPORAL ROW, and safe Rust turns the
> defect into a WRONG ANSWER, not a panic** · **F72 ⭐⭐ item 51 DECIDED: `ph29`'s
> `required` is SPELLINGS WITH THE TICKS DROPPED, and two of eight must NOT be
> quoted as written** · **F73 ⚠⚠ a declared spelling containing a CHARACTER
> LITERAL can never match — latent, 0 of 33 PAT and 0 of 6 PHP (⛔ **`1 of 14` re-measured 2026-09-17**)** · **F74 ⭐⭐⭐
> item 52 SETTLED by the R4/R5 NULL CONTROL the project already ships: quote
> family A and name it** · **F75 ⭐⭐⭐ `ph45`'s `crashes_pristine_5_0_0` is
> BOOKKEEPING, and the forcing mechanism is needed for the BENIGN case** ·
> **F76 ⚠ the `idiom` key whitelist is the backtick trap one level up, and
> `ph29` has now paid for it twice** · **F80 ⭐⭐⭐ ROW 6, the FIRST TYPE ROW:
> `ptr as i32` is SAFE RUST — gcc warns, rustc is silent, only Verus refuses** ·
> **F81 ⚠⚠ the catalogue's proposed oracle has measured NOTHING on 2 rows of 2
> tested — a rule, not a coincidence** · **F77 ⭐⭐⭐ `ph29`'s R4 endpoint MOVES —
> the first in either programme, and a counterexample to a PAT rule's PREMISE**
> · **F78 ⭐⭐ "closes, no residue" was an ARITHMETIC IDENTITY, and the
> falsification instruction is what caught it** · **F79 ⚠⚠ two real defects in
> control machinery, found by its own negatives, one LATENT in `ph16`** ·
> **F82 ⭐⭐⭐ F74's null control had an UNCHECKED PREMISE — every number
> survives, but a null control is ONE-SIDED and family A's SENSITIVITY is now
> measured: 2 instructions/call, resolved exactly, on two inputs** ·
> **F83 ⭐⭐⭐ and the null was MEASURING REAL WORK — B's defect is ATTRIBUTION,
> not noise, and a confound does not shrink with measurement; family C
> (inclusive) dominates B and solves nothing, because attribution belongs to the
> COMPARISON. F74 corrected 3× in 3 rounds, never once on arithmetic** ·
> **F84 ⭐⭐⭐ family B can MISS real work as well as invent it — ⛔ my `−1.00`
> mechanism REFUTED by the review: it is one instruction per call in `main`** ·
> **F85 ⚠⚠⚠ the CROSS-LANGUAGE column carries 29 of 38 sign flips (⛔ **`111 of 141` re-measured 2026-09-17; the SHARE survives, the count does not**) and 28 of 29
> SURVIVE family C — this project's central claim** · **F88 ⭐⭐⭐ family B is ONE
> DRAW of a sampling distribution; `ph29`'s B moves 32 % across draws and
> `inside_share` is interpretively VOID on such a row** · **F86 ⭐⭐ three classes not two (agree/FLIP/BLIND), and the exact
> flip test proves THERE IS NO SHORTCUT: certifying A needs B** ·
> **F87 ⭐⭐⭐ `ph45`'s R4 AND R3 both move, the bound's SIGN REVERSES, and
> `get_unchecked` is the EXPENSIVE spelling — 44 pp dearer** ·
> **F91 ⭐⭐⭐ the null-control RATIO, and family B's SENSITIVITY — `|B/A|` is
> 49.6–393.9× at every small-Δ cell and 0.2–3.0× at every large-Δ one, so B
> loses a small code difference completely. Nothing overturned; smallest margin
> 3.12×. ▶ THE AXIS IS SAME-LANGUAGE vs CROSS-LANGUAGE** ·
> **F92 ⛔⛔⛔ ITEM 68 ANSWERS NO — the width→spread exponent is ≈ −0.5 on both
> rows, so widening `probe_iters` is HOPELESS and MY F90 IS REFUTED on its
> operative half** ·
> **F93 ⭐⭐⭐ on `ph29` the shipped pin is a START-OF-RUN TRANSIENT, not a draw
> (`+6.9σ`, decaying with `n`) — so widening does not even converge; and
> `ph64`'s B1 HEADLINE IS SAFE to `0.0087 pp`, 64× F89's sample** ·
> **F94 ⭐⭐⭐ ROW 7 IS `ph53`: the catalogue's fix_commit is REFUTED (the cited
> line dies at `php-5.0.5`, 2y9m before it), the real R1h is FOUND at
> `d09cdd9f71f3`, and it converts a WILD deref into a NULL deref — one hunk,
> two severities, a shape no built row has** ·
> **F95 ⭐⭐⭐ the pre-image screen's 43 EXCLUSIONS ARE 25 (item D11's third
> label landed), and its soundness test was PROMOTING AN EXCLUSION TO A PROOF —
> reach 1 of 170, repaired, with the regression negative in the COMMITTED
> suite because the finding probe stops firing once the defect is gone** ·
> **F96 ⭐⭐⭐ ROW 7 IS BUILT — `ph53`, the first `T3` row and the first
> IN-BOUNDS uninitialised read, with 3 of 4 predictions REFUTED and R4 landing
> outside BOTH arms of the one that named its own falsifier** ·
> **F97 ⭐⭐⭐ two SOUND gate rules are JOINTLY UNSATISFIABLE for a `MaybeUninit`
> read, and stage 7h forbids shipping the input that shows this row's fault —
> F31 binding on a real row for the first time** ·
> **F98 ⭐⭐⭐ a rung that REPRODUCES this defect cannot be VERIFIED: coverage is
> a property of attacker data, so R4/R5 carry a witness the C does not, at
> +21.8 %** ·
> **F99 ⛔⛔⛔ item 65 is CORPUS-WIDE — 9 `.temp/` citations inside HASHED
> contracts across 6 of 8 rows, ~90 in `NOTES.md`, and 3 ALREADY GONE; `ph53`
> is the sixth row to do it and the only one that noticed** ·
> **F100 ⭐⭐⭐ `ph53`'s BOTH endpoints move; the R3 prediction's MECHANISM was
> wrong (nine window bounds checks, 281.8 Ir/call, bigger than the whole R3−R4
> gap); `r4_bitmask_min` is CHEAPER *AND* smaller-surface; and A1's spread is
> 39.9/45.3 pp here against `0.000000` on `ph45`, so A1 is NOT insensitive to
> respelling** ·
> **F101 ⚠⚠ a FOURTH defect in the shared `spellings.py` machinery —
> `kernel_fingerprint`'s digest is PATH-SENSITIVE, latent here and a LIVE false
> negative on `ph29`, where byte-identity is a bar** ·
> **F102 `ph52` admitted on the C; the defect is SILENT on a clean stack** ·
> **F103 ⛔ row 8 built — and its `(slots)×(per-slot)` decomposition is REFUTED,
> `8.19 / 3` written as a product** ·
> **F104 the gate's `n_twins == 0` hard-fails the row whose TCB is SMALLEST** ·
> **F105 `ph52`'s R3 moves and the gap is a SPELLING — ⛔ its `97.6 %` REFUTED,
> ✅ its `0.82 %` upheld and GROWS to `1.02 %`** ·
> **F106 ⭐⭐ the harness pins a VERIFIED BYTE-IDENTICAL TCB REDUCTION out of the
> corpus** · **F107 the review round: six verdicted, NOT ONE survived as written,
> and ⛔ option (b) DOES NOT EXIST** ·
> **F108 ⭐⭐⭐ two PUBLISHED claims in `.memory-php/` change sign with the C
> compiler, and the rule forbidding that has been in `.memory/` since `TASK_001`,
> UNINHERITED** ·
> **F109 ⭐⭐ row 9 (`ph55`): the `Option` caught the NULL, NOT the wrong PC — safe
> Rust returns C's wrong answer BIT FOR BIT with every sanitizer silent, and
> unsafe Rust is STRICTLY WORSE THAN C** ·
> **F110 the family-B alignment sweep: `ph64` clean, three rows exposed, and NO
> published family-B number is wrong** ·
> **F111 `ph56`'s harm MEASURED (NULL read at `0x14`) — it refuted the catalogue
> AND the manager, and the sibling census came back NON-EMPTY for the first time** ·
> **F112 ⭐ row 10 (`ph56`): `R4 → R5` costs EXACTLY `0.000 Ir/call`, and the row
> had to BUY it** ·
> **F113 ⛔⛔ `argv` and `envp` are NOT the same knob (1 row against 3) — §B5's
> verdicts CONFIRMED on three axes, its stated GROUND refuted** ·
> **F114 ⭐⭐⭐ `F96` was NEVER ONE FINDING: four REVIEWER rounds had it in scope,
> two produced verdicts on its result 2 and filed them under their OWN numbers
> while reporting F96 `UNREVIEWED` — the atom was never the unit of review** ·
> **F115 ⛔⛔ three catalogued `fix_commit` shas do not BIND to the patch GitHub
> returns for them, and the survey's guard checked the header's SHAPE not its
> CONTENT — confirmed three independent ways** ·
> **F116 ⭐⭐⭐ THE C-SIDE BAR CAN BE MEASURED: a working PHP 5.0.0 CLI is on this
> box and NOT ONE manager document points at it — 36 corpus reproducers run, 14
> SIGSEGV, and criterion 2 had been ARGUED on all ten built rows** ·
> **F117 ⛔⛔⛔ `citecheck` has been red for a reason that is FALSE (item 97's §H
> material never touches its exit code), and 5 of 14 checkers ran their negatives
> only under `--selftest` — the third time "all checkers pass" was false** ·
> **F118 ⭐⭐⭐ the row-11 screen: 45 candidates, 13 families, three agents, NO
> KILLS — three different picks each with evidence, my `P2` REFUTED by my own
> control, and SIX rows' recorded `fix_commit` is not the repair of its site** ·
> **F119 ⭐⭐⭐ ITEM 117 CLOSES, and the measurement that closes it was taken by
> `_050`, the task that opened the item — 32 pad residues hold `−14.0` flat on
> both inputs, and three committed gate runs at three `envp_stack_bytes` give
> bit-identical family B. ⛔ Three of four conclusions survived and ZERO of four
> REASONS survived as written; `F96` ends VERDICTED PER GROUP (seven groups, not
> four), and my `M5` is refuted in both halves** ·
> **F120 ⭐⭐⭐ CRITERION 2 IS MEASURED FOR THE FIRST TIME IN THE PROGRAMME:
> `ph97`'s trigger faults at `si_addr=(nil)` on a real PHP 5.0.0 CLI with its
> benign control clean in the same run, and `PROTOCOL_PHP.md` §A3a now REQUIRES
> it where a reproducer exists — item 120 CLOSED** ·
> **F121 ⛔⛔ THE RATCHET'S OWN LAW HAD A HOLE ONE LEVEL UP: the registry carries
> no count literal and the PROSE ABOUT it carried THREE, one of them created by
> the edit that fixed the other two — plus a checker whose arms are silent on
> pass, which is indistinguishable from a checker with no arms** ·
> **F122 ⚠ `F117`'s transient half is NARROWER than every document said — rot
> rose only for a SPLIT report name, never for an in-flight task as such
> (measured 1 vs 2), and the third un-inherited caution is now the third closed** ·
> **F123 ⛔⛔⛔ *"PHP 5.0.0 cannot be rebuilt on this box"* is FALSE, and the
> obligation it excluded from §A3a had been called *"the cheapest remaining
> check"* by an engineer, demoted by the manager, skipped, and re-derived as
> impossible — a four-document chain, and the programme's failure mode RUNNING
> BACKWARDS: the reason decayed while the conclusion hardened** ·
> **F124 ⭐⭐⭐ ROW 11 (`ph97`) — `P1` survives in BOTH halves: the optional's
> discriminant costs `+0.0000 Ir/call` and `Option<&[u8;21]>` is 8 bytes, so the
> null-as-absent idiom is the one C mistake whose safe replacement is FREE BY
> CONSTRUCTION. `P3`'s conclusion survives and its mechanism is refuted; a
> control refuted its own author (even UNSAFE Rust cannot reproduce the fault
> signature)** ·
> **F125 ⭐⭐⭐ `F119`'s exclusion PRICED: moving the compare into libc leaves the
> checksum identical and makes A1 read `−28.61 %` CHEAPER while the program is
> `+9.39 %` DEARER — A1 can report the SIGN BACKWARDS across a symbol boundary** ·
> **F126 ⭐⭐⭐ the first-in-family premium is REFUTED IN SIGN at n = 8 (openers
> 2.19, follow-on 3.17, pin 4.00 from n = 1) — and `N11`, the arm that should
> have caught it, ASSERTED THE PREMIUM'S DIRECTION, so it reported the data as
> the failure** ·
> **F127 ⭐⭐⭐ the SEVENTH consecutive round, and its biggest result is in none
> of the thirteen findings: FIVE built rows never measured `inside_share`, THREE
> of those publish an `A1` headline, and `ph29`'s only figures live in a
> docstring that disclaims the very comparison this file publishes from it.
> Three of sixteen entries had both conclusion and reason upheld. §A3a's fifth
> obligation is now REQUIRED because the cost is THIRTY SECONDS, and four of my
> own same-day repairs were found defective** ·
> **F128 ⭐⭐ a SECOND arm caught asserting an effect's SIGN — `N13` after
> `N11`/`F126` — and this one was legible BEFORE the refutation, because its
> own comment named ONE bound while its predicate asserted TWO. The rule:
> when a check's prose and its predicate disagree about how many conditions
> there are, the extra one is the unmeasured assumption** ·
> **F129 ⭐⭐⭐ TWO DIFFERENT QUANTITIES ARE CALLED `inside_share` AND NO
> DOCUMENT SAID SO — every published figure is `F74`'s `(A1/n_iters) /
> marginal_ir_per_call`, the only shipped control computes `A1 / callgrind
> whole-run total`, they read 0.8045 and 0.8933 on the same cell, and F74's
> exceeds 1.0 on 15 of 360 corpus cells. AND the programme's most-cited
> number — `ph29`'s `+33 %` — exceeds the row's own `≤ 0.02` share condition by
> 11×. ⛔ F129 called that INADMISSIBLE; `_059` WITHDREW the word — the bar is
> not a gate, and F129's corpus clause (*"every published figure is F74's"*) is
> FALSE in two documents** ·
> **F130 ⭐⭐⭐ a RATCHET THAT NOTHING EVER INVOKED — `cbaseline_check.py`'s
> enforcement was gated on a `--ratchet` flag no caller passed, and measured
> at `1cc2c0e` the corpus already stood at 70 hits against a baseline of 69,
> un-run and unnoticed. The bare run now enforces. Eight new hits adjudicated
> by hand, all benign, and one of them is the line that obeys the rule BEST —
> flagged because it writes `gcc-C` where the regex wants `c-gcc`** ·
> **F131 ⛔⛔⛔ THE TABLE THAT DECIDES WHAT MAY ENTER THE AUTHORITATIVE LAYER
> LISTED SIX FINDINGS AS BOTH UNREVIEWED AND VERDICTED — `F120`–`F125`, each
> twice in one table, because `_057` verdicted a BATCH and the batch was
> APPENDED below instead of APPLIED above. Fourth instance of a class the
> block's own preamble documents three times, and the first at scale.
> ⭐ The table contained the sentence that diagnoses it. ⭐⭐ And the backlog
> was not countable from the column that carries it, because one cell read
> *"UPHELD-NARROWED BY ITS OWN SWEEP"* — which is the manager narrowing the
> manager, and it SCANS as a verdict** ·
> **F132 ⛔⛔⛔ A RATCHET'S COUNT IS NOT A MEASURE OF ITS CORPUS: the unit is a
> BLANK-LINE PARAGRAPH, so a finding TITLE gaining the literal `c-gcc`, a block
> inserted into a blockquote, and a blank line SPLITTING a paragraph each moved
> the number with NOTHING repaired. Twice it hid a real arrival — `_058` read a
> departure as progress, and landing `_059` the net said +1 while THREE had
> arrived. ⭐⭐ The manager made two of the three IN THE EDIT LANDING THE REVIEW
> OF THE RATCHET, hours after writing the warning. ▶ Adjudicate the SET, by
> unit text, never the number — `.tasks-php/cbaseline_diff.py`** ·
> **F133 ⭐⭐⭐ BOTH CORRECT SPELLINGS OF AN OBLIGATION AND BOTH WRONG ONES LIVED
> IN ONE FILE, BY ONE AUTHOR — `zend_object_handlers.c` calls one helper from
> four ArrayAccess handlers; `:384` guards the out-parameter, `:413` declines
> it by passing NULL, and `:427`/`:512` do neither and SIGSEGV at `0x14` and
> `0x10`, the two offsets predicted from the struct before the run. The callee
> GUARANTEES the NULL sentinel on purpose with a comment naming the hazard, and
> the unmisusable contract was already supported in the vulnerable tree WITH
> THE VERY NULL TEST `:513` OMITS. Upstream's 2005 fix COPIES the sibling 99
> lines up. ▶ An R1h is evidence about what was CHOSEN, not always about what
> was KNOWN** ·
> **F134 ⛔⛔⛔ A DEFECT REPAIRED IN A TOOL IS NOT REPAIRED IN THE MANAGER — I
> read a `@@ … @@` hunk label as a claim about what a patch changes, which is
> the exact `xfuncname` error `preimage_screen.py::same_function` was measured,
> documented and patched for on 2026-09-12; its docstring describes my error in
> advance. The repair lived in the code path and I was not on it. A trap
> documented only where the CODE meets it is documented for the code, not for
> the person** ·
> **F135 ⛔⛔⛔ A KNOWN ARM FAILURE WAS RE-CLASSIFIED AS AN EXPECTED EXIT CODE —
> `citecheck.py --selftest` failed `N5d`/`N4` for 43 commits while the sweep
> printed `ok`, because `checkers.py` NAMED the failing arms and then set
> `st_expect=1`. The arms pinned `rot == 0`, an absolute literal for a relative
> claim, and were defective before the rot that revealed them. A benign cause
> does not make a failing arm benign — and a ratchet silenced by editing its
> EXPECTATION is silenced as surely as one silenced by editing its INPUT** ·
> **F136 ⭐⭐⭐ THE CONTRACT THAT CANNOT BE MISUSED IS FREE — the two attested
> repairs of `I12/O1` differ by `+0.0000 Ir/call` on both C compilers and both
> inputs, and under `c-clang` they are the SAME PROGRAM (`identity_level=exact`,
> 280/280 insns). Removing the output does not delete the NULL test; it moves
> the call site onto a contract whose test was already written once, in the
> callee, for all seven no-output sites. Refutes `P1` 4 of 4 and BOTH headlines
> the manager offered** ·
> **F137 ⭐⭐⭐ C's DETECTION AND UNSAFE RUST'S ARE BOTH BUILD-DEPENDENT AND FAIL
> THE SAME WAY — gcc faults at every `-O`; clang above `-O1` turns the null
> deref into a SILENT WRONG ANSWER, and unsafe Rust does the same one level
> lower. Safe Rust panics at every level and is the only rung whose detection
> does not move. `F3` firing live on a row that carries a faulting run beside
> it — and safe Rust's advantage stated in a currency the cost columns cannot
> express at all**
>
> ⚠⚠ **This index stopped at F59 while F60–F65 existed, and then AT F101 WHILE
> F113 EXISTED — twelve behind, caught by a pre-handoff audit 2026-09-14.**
> `PROTOCOL.md` rule 13, **and the index that warns about rotting had rotted
> twice.** ▶ **Extend it in the same edit that adds a finding.** ✅ **F114–F118
> were added in the edit that wrote them, 2026-09-15 — the rule obeyed once, and
> F120–F122 make it twice.**

### F1 (PROVISIONAL) — `c_file_line` names the FAULTING FRAME, not the defect

Grouped by mechanism rather than by file, the temporal axis is **23 families,
11 `verbatim` / 10 `narrowed` / 2 `modelled`** — nine in ten lift. ✅
Manager-recomputed. The manager had predicted the opposite and would have
written off the richest axis in the corpus. The defect usually sits one call
below the crash, in a standalone container (`zend_ptr_stack.h`, 68 lines;
`zend_hash.h:88`'s `typedef Bucket* HashPosition;`). → `PLAN_PHP.md` §4.2a.

### F2 (PROVISIONAL) — the CSV is authoritative; the reproducer comment is not

Found independently by two agents on two axes. Every `index.csv` `c_file_line`
resolved exactly; **six `input/crash/*.php` header comments describe 4.0.2**,
and `CRASH-017.php` self-labels as such. ✅ Manager-verified: following it
instead of the CSV **inverts the verdict**. → `PLAN_PHP.md` §1.

### F3 (PROVISIONAL) — `crashes_pristine_5_0_0 = False` is not evidence of absence

40 of 85 temporal rows are `False`, mostly because PHP's size-class cache keeps
**63.5 % of heap traffic away from `malloc`**. A C kernel on plain
`malloc`/`free` reproduces **more** of these than pristine PHP does. **Not an
admission filter.** A second allocator truncation was also found —
`zend_alloc.h:53`'s `unsigned int size:31` (✅ verified). → `PLAN_PHP.md` §4.3.

### F6 — ⚠⚠ THE ALLOCATOR SHIM INVENTED DEFECTS, IN THE FILE WRITTEN TO PREVENT THAT

`common-php/emalloc_shim.h:340` claimed `__builtin_mul_overflow` is the *"same
predicate"* as PHP's `ZEND_SIGNED_MULTIPLY_LONG`. ✅ **Manager-verified false:**
`Zend/zend_multiply.h:22` guards the exact `imul` arm with
`#if defined(__i386__) && defined(__GNUC__)`, so on **x86-64** PHP falls to the
`#else` at `:34` — a **double-precision heuristic** (`__dres + __delta != __dres`),
not an exact test. Measured: **84 523 disagreements in 20 M samples, 100 % one
way — PHP raises `E_ERROR` where the shim allocates.**

⚠⚠⚠ **This is `PLAN_PHP.md` §4.3's own failure mode — a substituted primitive
inventing a defect — inside the file that exists to prevent it**, and it is the
same shape as the earlier PHP effort's `malloc`-for-`emalloc`, which published a
false explanation of an upstream fix.

✅ **CLOSED at `TASK_PHP_004`, and CONFIRMED at `TASK_PHP_005`.**
`PHP_SHIM_SIGNED_MULTIPLY_LONG` is the `#else` arm transcribed character for
character, invoked on `size_t` operands the way `_safe_emalloc` does.
Differential probe over the review's **exact** sample space (same xorshift seed,
same draw, same 20 M): **0 disagreements**, with the `__builtin_mul_overflow`
**must-fire control reporting 84 523** every time.

⚠ **THE CONFIG CLAIM HERE SAID *"gcc/clang × `-O0`/`-O3` ×
`{-DSLB_ISOLATED,-flto}`"* — 8 cells — AND ONLY **5** HAD BEEN RUN
(`TASK_PHP_005` F-3). The same sentence is in `common-php/emalloc_shim.h:462`,
which `digest_bridge.py` pins into every php gate record.** The reviewer ran the
missing three (`gcc-O0-lto`, `clang-O0-lto`, `clang-O3-lto-lld`): **0/20 M,
control firing.** ✅ **The claim is now true and measured** — but it was written
before it was.

⚠⚠ **And `TASK_PHP_004`'s disclosed limitation *"`clang -O3 -flto` cannot link
on this box"* DOES NOT EXIST**: it links with `-fuse-ld=lld`, **the flag
`harness/build.py:169-172` itself inserts for exactly that cell.**
`PROTOCOL.md` rule 13's shape — a published limitation that is not real.

✅ **All four attacks the manager named on B2 were CLEAN NEGATIVES**
(`TASK_PHP_005` §2) and the row is stronger for them: **negative operands** (10 M
signed, control fires 21 170, shim 0); **`dval` compared bit-exactly** (45 M+
samples, 0) — so a `mul_function` row can use the macro as shipped;
**a directed sweep** of 28 900 targeted cases plus 20 M straddling `LONG_MAX`
(controls fire 414 and 3 692, shim 0).

⚠ **The same-TU residual is now PRICED rather than open**: the pristine macro's
whole output stream hashes to `0e813d9ad6308e5a` across **six** configurations —
two compilers × two optimisation levels × `-fwrapv`/`-fno-strict-overflow` — and
`shim == ref` inside each. A shared miscompilation would have to be shared by
gcc and clang *and* be insensitive to `-fwrapv`. **Not zero without a compiled
PHP 5.0.0 binary, but far smaller than "one TU".**

⚠⚠ **THE REUSABLE RULE: *"modelled by an equivalent builtin"* is a claim that
needs a DIFFERENTIAL TEST WITH A MUST-FIRE CONTROL, not a comment.** The shim's
original `SE CONTROL: a true 64-bit overflow IS refused` was a real control and
exercised only the region where the two predicates agree — which is exactly why
it could not see this.

### F7 — the manager's stated expectation was REFUTED, and that is the good news

The manager predicted Phase 0 would fall over on the `common-php/*.h` digest gap
and asked for a constructed case. **It fires**: planting `MAX_CACHED_MEMORY
11→12` makes the preflight refuse (`exit 2`, tool not run), and with `--regen`
the gate record goes `STALE`. ⚠ **What is NOT protected is the second half** —
B1, the unenforced `<row>/c/` symlink.

✅ **And the run of four is broken: `TASK_PHP_003` checked every `file:line` the
manager marked ✅ and found ZERO unearned.** ⚠ The *reasoning* around two of them
was still wrong (the `REAL_SIZE` story, `repo_path_bytes` 20 vs 15) — **the marks
were on the citations, and the citations held.**

⚠⚠ **THE RUN LASTED EXACTLY ONE ROUND. `TASK_PHP_005` F-12 FOUND AN UNEARNED ✅,
AND IT IS THE MANAGER'S.** `TASK_PHP_005.md:51` cites `Zend/zend_alloc.c:295` as
the second `ZEND_SIGNED_MULTIPLY_LONG` call site. It is **`:234`**; `:295` is
`_ecalloc`'s `int final_size`, a *different* mechanism (F5's third truncation).
**The manager's own footnote on the same line had `:234` right**, so this was a
transcription slip between a grep that was run and a sentence that was written —
⚠ **which is the failure mode this project keeps rediscovering: the citation and
the story about it are two separate claims, and running the grep does not check
the prose.** The substance held (there really are exactly two call sites).

### F5 (PROVISIONAL) — a THIRD allocator truncation, and the calloc path

`Zend/zend_alloc.c:295` in `_ecalloc` is `int final_size = size*nmemb;` — a
**signed 32-bit** product passed straight to `_emalloc`, so
`ecalloc(0x40000000, 4)` allocates **0 bytes and succeeds**. ✅ Manager-verified.
With `real_size` (`:129`) and `size:31` (`zend_alloc.h:53`) that is **three**
truncations; the plan knew of one when it was written. → `PLAN_PHP.md` §4.3.

⚠ Demonstrated with controls rather than argued: 18.45 EB → 2 GiB succeeds while
the no-truncation control returns `NULL`, and under ASan **the same UAF is
reported on a 96-byte block and silent on a 24-byte one** — the mechanism behind
F3, measured instead of inferred from a percentage.

### F4 — a manager error, corrected by an agent

The manager told all three agents `.temp/san_tests/` holds *"123 ASan reports"*.
✅ Verified wrong: 123 is one curated pass, the column beside it says **7
distinct sites**, and the real population is **2534 log files**. `PROTOCOL.md`
rule 14's shape — a premise stated as fact in a task file is one an engineer has
no reason to doubt. → `PLAN_PHP.md` §1 corrected.

---

### F8 — ⚠⚠⚠ THE MINING WAVE'S *KILLS* WERE WHERE THE DEFECTS WERE: EXTRACTION COST WAS WRITTEN AS A CRITERION-3 FAILURE

**Manager audit, `.tasks-php/ADJUDICATION_001.md`. UNREVIEWED — `TASK_PHP_008`
attacks it.**

All three miners were scrupulous about the bias `CLAUDE.md` rule 6 names, and
each said so in terms; the reject tables carry a C-side reason for every row.
**But `PLAN_PHP.md` §3's criterion 3 is about the KERNEL SHAPE — flat blob in,
`u64` out. How much C you must carry along is the TIER.** The spatial reject
table's criterion-3 bucket is full of *"the surrounding machinery is the
program"*, *"mutually recursive over a 4000-line file"*, *"the blob would have to
encode a backtrace"* — **tier assignments wearing a kill's clothes.**

✅ **Fourteen were opened in the pristine tarball. TWELVE refute the reason that
killed them, and two of those are FIVE LINES:**

- **CRASH-123**, killed as *"a whole conversion framework"*: `mbfl_convert.h:49`
  `int cache;` · `mbfilter_htmlent.c:161` `filter->cache = (int)mbfl_malloc(…)`
  · `:169` `mbfl_free((void*)filter->cache)` · `:177` `char *buffer =
  (char*)filter->cache;` · `:181` `buffer[0] = '&';` — **a heap pointer stored in
  an `int`, cast back, freed and written through.** The corpus gives it the only
  bespoke invariant in 166 rows (`pointer-value-integrity`), and it was routed to
  the *spatial* miner, so the **type** miner never saw it.
- **CRASH-157**, killed as *"the blob would have to encode a backtrace"*:
  `zend_exceptions.c:310` reserves `+2` for a format string with **four** literal
  characters. **The backtrace is the caller.**

⚠⚠ **THE REUSABLE RULE, AND IT IS F1'S SIBLING: extraction cost, like the
citation, must be priced at the DEFECT SITE, not at the frame the defect flows
into.** F1 says `c_file_line` names the faulting frame; this is the same error
with cost substituted for citation.

✅ **Also measured against the corpus (166 rows in `index.csv`):** the 54
candidates mention **123**; **43** are covered by nothing; and of those 43,
**exactly one — CRASH-008, `datetime.c:359`, `case 'U': size += 10;` — is named
in no axis's `NOTES.md` at all.** ⚠ 42 of 43 carry a recorded reason, so the
silent-skip class fired **once**, not systematically — that is a good rigour
result and is recorded as one. ⚠ Five more rows were **routed** between axes and
never picked up by the receiving axis; **a routing decision is not a kill and is
not a delivery either.**

### F9 — ✅ NOT ONE SPATIAL ASan REPORT IN THE CENSUS IS IN THE CODE THE SPATIAL AXIS MINES

**Manager measurement. This CLOSES open item 7 — and the answer is that the
check cannot be done.**

✅ First, the wave's census is **confirmed exactly**: 2534 log files, **3199
reports** (567 logs hold more than one), split **2450** heap-buffer-overflow /
**490** heap-use-after-free over 336 logs / **189** use-after-poison / **70**
global-buffer-overflow. ⚠ `grep -c` returns **double** these; the wave counted
reports, and reports is right.

⚠⚠⚠ **Then the faulting frame, per report.** Of the 2520 *spatial* reports:
**2156 fault inside `libmysqlclient.so.14` — a different shared object** —
in its XML charset-file parser (`memcmp ← my_xml_scan ← my_xml_parse ←
my_parse_charset_xml ← my_read_charset_file`), and the other **364** in the regex
matcher reached from `ext/pcre/`. ⚠ I could **not** prove which function
`php_pcre_exec` is — it appears nowhere in 5.0.0's `ext/pcre/` sources, so the
name comes from the census build's own configuration. **The claim that does not
depend on that: ZERO of the 2520 spatial reports fault in `Zend/` or
`ext/standard/` — the code every one of the 16 spatial candidates is drawn
from.** The temporal mass, by contrast, is genuinely PHP engine code.

→ **Open item 7's action changes from *"go measure them"* to *"the census cannot
speak to this axis"*.** Every spatial `hotness` stays labelled **reasoned**, and
the census is struck as a possible source of spatial frequency evidence rather
than left as an open promise. ⚠ This is **not** the LTO story — those frames
resolve fine; they resolve to another library.

⚠ **What this does NOT license.** *"A corpus built by reading the source finds
what a sanitizer on real traffic does not"* is a **rhetorical** claim and this
programme has **not** demonstrated it — no php row is built. Keep it out of the
report until rows exist.

### F10 — a guard that is a string search is a guard with a spelling

`TASK_PHP_005` F-1: `gate.py`'s allocator audit decides "this row uses the shim"
by searching `<row>/c/*` for the literal `emalloc_shim.h`. Two spellings get
round it — `#include "emalloc_shim.c"` (the audit knows only the `.h`) and
`c/<subdir>/*` (the glob is non-recursive) — **and both rows build, link and run
a live allocator** (`alloc tally = 7688571`) into **neither digest**, preflight
green. ⚠ It also **false-positives** on a row that merely mentions the header in
a comment — which is the spelling `PLAN_PHP.md` §4.3 *tells* a non-allocating row
to use (F-8).

⚠⚠ **`TASK_PHP_004`'s own `.memory-php/` candidate #2 was *"a word in a document
is not an enforcement mechanism"*. F-10 is the sequel: _a check that greps for a
word is barely more of one._** The audit needs to key on what the *compiler*
sees, not on what the text says.

### F11 — the guard that closed B1 asks the COMPILER, and that is the transferable part

`TASK_PHP_006` closed F-1 by **replacing the string search with `gcc -MM`** over
`build.py`'s own TU list under both `-DSLB_ISOLATED` states, intersected by
`realpath`. ✅ **Priced before it was adopted: 2 calls, ~115 ms/row** — the
manager had worried it would be unaffordable and was wrong. All eight of the
reviewer's fixture rows land from their **unmodified** generator, and **F-8's
false positive closes as a side effect**, because a comment is not an include.

⚠⚠ **The manager's suggested fallback would NOT have worked.** `TASK_PHP_006.md`
called *"require the name inside an `#include` on the same line"* the obvious
repair; it would have left `ph53-subdir` open, because that bypass is about
**where the file is**, not how the include is spelled.

⭐ **The rule: a guard that greps has a spelling, and its spelling is a
vulnerability. Ask the tool that actually decides.** This is the third step of
one staircase — `TASK_PHP_004`: *a word in a document is not an enforcement
mechanism* → `TASK_PHP_005` F-10: *a check that greps for a word is barely more
of one* → here: *ask the compiler.*

### F12 — three size rules were justified by a figure nobody had measured

Detailed in the size box above. ✅ `p01`'s `why` is **2 057 words**, not the
*"~7,000"* the manager wrote into a task file, copied into the state layer, and
an engineer then cited back as the rule's motivation. **The lesson is `PROTOCOL.md`
rule 14 and this is its second instance on this programme** (after F4's *"123
ASan reports"*): a premise stated as fact in a task file is one an engineer has
no reason to doubt, and it comes back as evidence.

⚠ **The reviewer's own correction was also mis-measured** — `TASK_PHP_005` F-5
took the row-specific half as the *prefix only*, so `p16-tlv-walk`, the corpus
**maximum** at 3 140 words, appears in its table as the **minimum** at 109.
**Three parties measured this quantity and all three got a different span.**

### F13 — ⚠⚠⚠ A REFUTED MECHANISM IS NOT A LICENCE FOR THE DESIGN IT ARGUED AGAINST

**The manager's own error, caught by an engineer before it shipped, and the most
useful thing this round produced.**

`TASK_PHP_006` justified *"a missing preflight record is a NOTE, not a failure"*
with an **asserted** deadlock. `TASK_PHP_007` M4 **disproved** it by running it —
and said in terms *"I am not recommending the hard failure."* ⚠ **The manager
asked for the hard failure anyway**, reading a refuted mechanism as a cleared
design.

Composed with M5 (*a record whose every run FAILED counts as no record*) the hard
failure is **self-referential** and deadlocks the **fresh-clone path** for ever,
with no escape flag:

```
run 1  no record          -> coverage problem -> PREFLIGHT FAILED -> writes a record whose only run FAILED
run 2  record exists, only run FAILED (M5) -> coverage problem -> PREFLIGHT FAILED
run N  ... and nothing an operator can do fixes it
```

✅ **The engineer did not find this by reading. It wrote the loop, ran it,
watched six runs never converge, and repaired it before shipping** — by
discounting the audit's *own* coverage problems, on the honest reading that a run
which failed only on another row's paperwork still certified **this** tree. The
naive rule survives as a **must-fire control**, and `_run_is_certifying`'s
docstring forbids simplifying it back.

⚠⚠ **The rule: refuting the ARGUMENT for a decision does not establish its
opposite.** The original engineer's *conclusion* — loud beats unrunnable — had a
real case behind it that its *stated mechanism* got wrong. That is
`PROTOCOL.md` rule 9's conclusion-versus-mechanism split arriving from the other
side, and the manager walked into it while holding a correct refutation.

### F14 — `0 STALE` does not mean "everything is pinned"

`harness/measure.py::_compare` iterates the **recorded** keys, so **a file ADDED
to a row is invisible to `--check-stale`** — it has no key, so it cannot be
stale. ✅ Observed, not reasoned: adding `c/emalloc_shim.h` to `ph00` left the
measurement record `FRESH` while the file sat on disk unrecorded.

⚠⚠ **This is the bracket every task file in this programme mandates twice**, and
its true meaning is *"every source that was pinned still matches"*. What closes
the gap is the **preflight**, not the digest — `shim_link_audit` refuses the row,
so a gate cannot pass in that state.

⚠ It is a `harness/` property and affects **all 33 PAT rows identically**. Not
fixed: the fix is a `harness/` edit and a 33-pattern re-gate. → `PROTOCOL_PHP.md`
§E carries the sentence.

### F15 — the cheapest correct design was the one already in the docstring

✅ **Manager cost claim refuted, in the manager's favour.** *"An `emalloc_shim.h`
edit will re-gate every php row"* — the **gate** half has been unconditional
since `TASK_PHP_002`, because `digest_bridge.py`'s own hash is in every php gate
record. The marginal price of *"every row"* over *"every allocating row"* is the
**measurement** half only: a re-measure (~8 min) plus a render.

⚠ **And the measurement the manager said it had not made is one command**:
`git log -- common-php/emalloc_shim.h` → **3 edits in 7 php tasks, two of the
three for PROSE.** That cuts *against* the design — a comment fix costing a
corpus-wide re-measure — and the mitigation is already protocol: **batch prose
fixes, never land one alone** (`PROTOCOL.md` rule 6, verbatim).

Three cheaper designs were considered and rejected, recorded so nobody
re-derives them. ⚠ **The instructive rejection is versioning the shim**
(`emalloc_shim_v1.h`, each row links what it measured under): correct by
construction *and* cheaper, and **wrong, because it inverts the property we
want** — a shim fix that does not propagate leaves rows measured under a
known-wrong allocator silently and for ever, converting a loud re-measure into a
quiet divergence.

### F16 — ⚠⚠ A WRONG ENUMERATION IS NOT AN UNBOUNDABLE ONE

**The manager had this backwards, and the correction is worth more than the bug
it is about.**

`TASK_PHP_009` M1: a **dotted row directory** hides from `glob("patterns-php/*")`,
so all four audits skip it while `build.py::pattern_dir` (`os.listdir`) and
`provenance.py` both resolve it. ✅ Demonstrated end to end on the real tree —
`gate.py --preflight .ph93` returns **rc=0** on a row carrying a regular-file
allocator copy *and* an unkeyed subdirectory source, printing *"ok every
`patterns-php/*/c/` file has a digest key"*, with the identically-defective
normally-named row refused as the fired control.

⚠ **The manager wrote: *"if a row can hide from `glob`, the whole argument
collapses and we are back to whack-a-mole with a smaller board."* That is
wrong:**

> The idiom detector's defining property was that **no complete enumeration
> existed** — no function anywhere returns "every way to spell an `#include`".
> For rows one **does**, it is a single call, and `build.py:81-89` already uses
> it. The audit and the builder can be made to enumerate **the same set**, and
> that set is provably complete against the only resolver that decides what gets
> compiled.

⚠⚠ **Treating a wrong enumeration and an unboundable one as the same failure is
how a fixable bug gets priced as a phase.** The fix is a substitution
(`os.listdir` for `glob`), not another round of the game — which is exactly the
property the unconditional-link design was adopted for, and it survives.

### F17 — the second deadlock, and its message denies it

`TASK_PHP_009` M3: `preflight_coverage_audit` is a **GLOBAL** stage, so **one**
uncertifiable record fails **every** `gate.py` invocation — including the
bracket every task file mandates twice. An orphan `results-php/<row>.json` (a
retired row whose committed records survive — `PLAN_PHP.md` §3 *expects* rows to
be retired) cannot obtain a certifying run, because the prescribed repair fails
on **provenance**, which is substantive. ✅ Run end to end: three cycles,
non-convergent; the actual fix (delete the record) appears nowhere in the
message.

⚠⚠ **And the message printed at that moment says *"⚠ THERE IS NO DEADLOCK"*** —
the same shape as the *"dead code … Not treated as a shim user"* note that
`TASK_PHP_008` deleted for exactly this reason: **a reassurance that tells the
reader not to look further.** ⚠ It is escapable and destroys nothing, which is
why it is not a blocker.

⭐ **One change closes M3 and M4 together: make the coverage stage report
PER-ROW rather than globally.** The global scope is what turns any single
uncertifiable record into a programme-wide stop, and it is the property §8b's
first deadlock also rode on.

### F18 — both whitelists this manager wrote were wrong on first contact with the corpus

⚠ **`{c, inputs, controls}` as specified refused ALL 33 BUILT PAT ROWS** — every
one carries `__pycache__/`. Measured 33/33 before shipping, and exempted.

That is the **second** whitelist-shaped decision in this programme and the second
to fail: the `c/<subdir>` ban was **both insufficient and over-strict**
(`TASK_PHP_009`), and this one was over-strict the moment it met the tree.
⭐ **The transferable part: a whitelist written from the layouts you INTEND is
not a whitelist over the layouts that EXIST. Run it against the corpus before
shipping it** — which is what caught this, and cost one command.

✅ The manager named it as a least-sure call both times, and both times that was
the right instinct and the wrong artefact.

### F19 — *"show it converges"* was the wrong success condition

⚠ The manager's `TASK_PHP_010` §3 asked the engineer to *"show it converges"*.
**A retired row's orphan record never converges by repetition, and must not** —
the repair is **deletion**, not iteration. The right condition was *"it stops
blocking"*, and the engineer supplied it.

⚠ **This is the same error as F13, one level down.** There the manager read a
refuted mechanism as a cleared design; here it carried a success condition
(*convergence*) from the **fresh-clone** deadlock, where repetition **is** the
repair, into the **orphan-record** one, where it never can be. **A success
condition is part of a design and does not travel with the shape of a bug.**

### F20 — one `..` too few

⚠ `#include "../../shared/x.h"` from `<row>/c/` reaches `patterns-php/shared/`,
**compiles, runs the outside allocator (`tally=7`), and is in neither digest** —
and it is not a directory *under* the row, so `ROW_DIRS` cannot see it. It is
`TASK_PHP_009` M2 with one more `..`.

✅ **Latent on both sides today: no row has such an include.** Reported and
deliberately **not fixed**, because both repairs are worse than the risk: parsing
`#include` targets is the **idiom-enumeration class this programme has deleted
twice**, and the spelling-free version (`-MD`) needs a `harness/` edit and a
33-pattern re-measure. ⚠ **The discipline is written into `PROTOCOL_PHP.md` §B3a
instead — `<row>/c/` holds everything the row compiles, checked by eye at
review** — so the next author is not told the guard is stronger than it is.

### F21 — ⚠⚠⚠ THE AUDIT LOOKED AT THE KILLS IT SUSPECTED AND NEVER AT THE KILLS IT UPHELD

**`ADJUDICATION_001.md` §1's whole finding was that extraction cost had been
written as a criterion-3 failure. The manager wrote `TASK_PHP_011` expecting
that finding to be attacked as an OVER-reach — *"if the distinction does not
hold, ~17 reversals are wrong and the catalogue is inflated by a fifth."*
✅ The distinction holds. The error was the opposite one and it was in where the
lens was pointed.**

The adjudication produced a `§3b Kills UPHELD` list and **never re-opened it at
source**. Doing so reverses **five more**:

| row | the kill said | at source |
|---|---|---|
| **CRASH-097** | *"the quantity comes from a socket"* | ⚠⚠ **it comes from `zend_parse_parameters`.** The kill priced the **wrong operand** — F1 landing on the manager's own upheld list |
| **CRASH-098** | *"needs real file descriptors"* | measured: **`FD_SET` never touches the fd table** |
| **CRASH-135** | *"needs a calendar library"* | `SdnToJulian` is **46 self-contained lines** of a 250-line file |
| **CRASH-133** | *"needs bcmath"* | same shape |
| **CRASH-147** | *"irreducibly ~2 GiB"* | a **resource budget**, not a kernel shape — criterion 3 is about shape |

Plus **six killed on *"mechanism quality"***, which is **not in the bar at all**.
**The catalogue is 91 rows, not the ~80 predicted.**

⚠⚠ **The transferable rule: an audit that only re-examines the decisions it
already doubts measures its own priors.** The adjudication's §6 said *"the thing
to attack first is whether the criterion-3-vs-tier distinction is crisp"* — it
was, and asking that question is what stopped anyone asking the cheaper one:
*did I apply it everywhere, or only where I expected to find something?*

### F22 — ⭐ A KILL WRITTEN AS A SET HIDES ITS MEMBERS

**`CRASH-124`, `CRASH-127` and `CRASH-128` were killed by the SAME SENTENCE as
`CRASH-123`** — the row `ADJUDICATION_001.md` §1b made its **headline
reversal**, the five-line pointer-in-an-`int`. Nobody asked whether the other
three fell the same way. **They do.**

⚠ **This is unfindable by reading reject tables**, which is how both the
adjudication and every review before it worked. It was found by **diffing
catalogue coverage against `index.csv`** — a mechanical set difference.
⭐ **When a rejection covers N rows in one sentence, reversing it must
re-adjudicate all N, and the only reliable way to enumerate them is against the
corpus index, not against the prose.**

### F23 — the document that made the citation point had citation defects

⚠ **Three, in `ADJUDICATION_001.md` itself**: `CRASH-107` off by one on **all
three** lines, and `CRASH-123` off by one and by two — **inside §1b's five-line
headline exhibit**, the very passage arguing that a kill had priced the wrong
frame. ✅ **The CSV and the miners were right both times.**

That is `RECAP_PHP.md`'s own standing lesson — *the citation and the story about
it are two separate claims* — landing on the document that restated it. ⚠ **The
substance survived every time; only the line numbers moved.** ✅ And the
catalogue's own citations were then checked properly: **222/222 resolve against
the pinned tarball across 52 sha256-checked files, 51/53 miner quotes exact, two
correct-line paraphrases, ZERO wrong lines.**

✅ **`§7b`'s mechanism is also corrected**: the NULL test **is** present at
`zend_execute.c:141`; the bug is the `return` at `:147`. **That makes the
`CRASH-053`/`CRASH-056` pairing stronger, not weaker.** And `CRASH-096` gets a
**third** answer — `zend_memnstr`'s `end -= needle_len` underflow, blob-pure,
**not** the stream layer where the manager had left it conditional.

### F24 — ~12 rows need a shared header; none needs a shared directory

The question `TASK_PHP_011` was asked because **a catalogue can answer it and an
infrastructure task cannot**: would any real row want `patterns-php/shared/`?

✅ **Measured: ~12 type rows genuinely need a shared `zval.h` — and none needs a
shared DIRECTORY.** `common-php/x.h` symlinked as `<row>/c/x.h` lands in **both
digests**, which is the mechanism already sanctioned for the allocator.
→ **F20 stays latent and correctly so; what is owed is one clause in
`PROTOCOL_PHP.md` §B2, not an infrastructure task.**

### F25 — ⚠⚠ THE MANAGER'S FIRST-ROW PICK WAS REFUTED BY A MEASUREMENT, AND THE MEASUREMENT IS ITSELF A RESULT

The manager's prior was `ph11` — *"the smallest possible spatial defect, no
arithmetic, no cursor, no allocation"*. ✅ **Measured at `-O3`: safe Rust and
unsafe Rust emit BYTE-IDENTICAL kernel `Ir` (11 010 064), and BOTH BEAT C
(11 534 345).**

**Mechanism:** LLVM folds Rust's `0 ≤ o < len` into **one unsigned compare**,
which C's **one-sided signed** test cannot fold, and then unrolls 2×.

⚠ **So `ph11` would publish ONE number across four rungs** — which is a genuine
finding and a terrible row to prove the pipeline *measures* anything with.
**Keep it; do not build it first.** ⭐ And note what it says on its own: **the
safety check is not merely free, it is faster than the unchecked C**, because a
two-sided unsigned bound is more optimisable than a one-sided signed one.

### F26 — the real upstream fix is a 1.4 KB fetch, not a 1 GB clone

`TASK_PHP_012` M7: **no `php-src` clone exists on this box**, so
`PROTOCOL_PHP.md` §F5's *"sha-pinned `fix_commit`"* was unmeetable and **R1h had
never been built php-side at all** — which would have failed `PLAN_PHP.md` §3
criterion 4 on the first row.

✅ **Manager-resolved, and verified before being written down:**
`https://github.com/php/php-src/commit/<sha>.patch` returns the real commit.
For `ph03`'s `f95c1df58349` that is **Ilia Alshanetsky, 2004-08-24, bug
#29821**, `ext/standard/uuencode.c`, +17 lines — adding exactly:

```c
if (len > src_len) { goto err; }          /* before total_len += len */
ee = s + (len == 45 ? 60 : (int) floor(len * 1.33));
if (ee > e) { goto err; }                 /* <-- the bound the mining report predicted */
```

⚠ Fetching a bare sha by `git fetch` does **not** work (the server refuses
arbitrary-SHA wants); the `.patch` URL does. **R1h is buildable verbatim, for
real, on every row whose `fix_commit` the corpus records.**

### F27 — *"a kill written as a set hides its members"* has now fired THREE times

F22 found it once (`CRASH-124/127/128` behind `CRASH-123`'s sentence).
`TASK_PHP_012` found it **twice more**:

- **M1** — the catalogue's claim that every §3.1 kill *"survives inside another
  row's `corpus rows`"* is **false for 6 of 12**. ⚠⚠ **And the tool built to
  check coverage could not see it, because `coverage.py` counts a mention in the
  KILL TABLE as coverage** — a checker that accepts the artefact it is checking.
- **M2** — the four-`LOGIC` set kill into `ph47` is the same shape re-committed,
  and **3 of 4 are refuted by the catalogue's own discriminator**.

⭐ **Three instances make it a rule, not an anecdote: a rejection covering N rows
must enumerate the N against `index.csv`, and any coverage checker must count
ADMISSIONS ONLY.** → the correction task must fix `coverage.py` first, because
every later count depends on it.

### F28 — demoting the overlap floor cost more than the manager priced

`TASK_PHP_012` M4: **12 of 41 `verbatim` tiers are mis-declared**, measured
mechanically. ⚠⚠ **And the manager's own decision is why that matters now**:
`TASK_PHP_008` demoted `provenance.py`'s overlap check from **enforcing** to
**reporting**, so the **hand-declared tier is the only surviving fidelity
signal** — and it is wrong on 29 % of the rows that claim the strictest tier.

⚠ The demotion itself still looks right (its input space was unbounded). **What
was wrong was pricing it as free.** → the correction task must decide whether
the reported overlap is printed *beside the declared tier* so a mismatch is
visible, which is the cheap half of what the floor used to do.

### F29 — ⭐⭐⭐ THE FIRST ROW'S RESULT: A STATED OBLIGATION CAUGHT IN 2026 WHAT A PATCH MISSED FOR TEN YEARS

**`ph03`'s `c/kernel_hardened.c` is the REAL upstream fix** —
`f95c1df58349`, Ilia Alshanetsky, 2004-08-24, bug #29821 — and **it is
incomplete.** ✅ **REVIEWED at `TASK_PHP_014`: the headline survives every
attack, and got STRONGER** — see the two amendments below the three limbs.

1. **Counted.** Over 12 600 documents the fix closes **every write**
   (3 352 → 0) and leaves **144 over-reads**. `ee` bounds where the loop
   *tests*; the body reads `*(s+3)`. Smallest surviving case: `src_len = 2`,
   `len = 1` → `ee == e`, so hunk 2 never fires.
2. **ASan**, on the *fixed* decoder, at `uuencode.c:144` — with a must-fire
   control proving the detector is live and a benign case staying silent.
3. ⭐ **Verus refuses it in one line.** Deleting **only** the four lines of
   PHP's *2014* check from `verus.rs` — leaving exactly the algorithm the 2004
   fix implements — fails `i < v@.len()` on `get_unchecked(buf, s + 1)`: **the
   same byte ASan reports.**

⚠ PHP did not complete this fix until **2014** (`1e2818b14376`, bug #67252),
and **that commit's own `.phpt` reproducer is the same `fl == 1, ee == e` shape
the count found independently.** Ten years.

⭐⭐ **AMENDMENT 1 — it is worse than incomplete: HALF THE 2004 FIX IS DEAD.**
`TASK_PHP_014` M5 proves hunk 1 (`if (len > src_len) goto err;`) **redundant**
three ways: deleting it from the Verus exec still gives **25/0**, neutralising
it in the spec still gives **25/0**, and **all 1 953 of its C firings would also
be refused by hunk 2.** So of a two-hunk fix, one hunk is dead and the other is
incomplete.

⚠ **AMENDMENT 2 — limb 2 is HARNESS-CONDITIONAL and *"measured twice, two ways"*
over-promised.** With the source allocated the way PHP's `emalloc` actually
allocates a zval string (`ALIGN8(len + 1)`), **ASan is silent** — the over-read
lands in the padding. ✅ **Limbs 1 (the count) and 3 (Verus) are
allocator-independent, so F29 stands** — but the ASan limb says *"a detector
fires under this allocator"*, not *"PHP faults"*.

⭐⭐ **This is the crash course's argument in one row, and it is not "the proof
is cheap": it is that the OBLIGATION IS STATED AT ALL.** A `requires` clause
caught in 2026 what a careful maintainer's patch missed for a decade.

⚠⚠ **And it reshapes the ladder: R2–R5 are NOT ports of R1h.** With only the
2004 pair a safe-Rust rung **panics** on those 144 documents — and *a rung that
panics is not a translation of the C*. So R2–R5 carry **both** fixes, R1h
carries 2004 only, and **only R1 diverges** on the shipped inputs. That is a
general rule for this corpus, not a quirk of `ph03`.

### F30 — the 2004 safety check has a NEGATIVE cost on gcc

✅ Measured on `ph03`: **−3.0 `Ir`/line on gcc**, +3.0 on clang. With the check
present, gcc's `setae` and two `cmove`s **disappear** (3 → 0, counted).
Rung deltas: **R2−R4 = +18.9 `Ir`/group** (one `cmp`/`jae` per checked access);
**R3−R4 = +6.1** (the reslice adds a wrap test R2 never had).

⚠ **Do not quote these against any `pNN` figure** (open item 9). And no ratio
here is *the* cost of safety — `controls/spellings.py` was not built.

### F31 — two frozen-harness limits only a real row could find, and both are DECIDED

**B1 — `harness/build.py` links no `-lm`.** ✅ Manager-verified independently:
`floor()` emits a real call at **-O0** and is inlined at **-O3**, and **libm was
never merged into libc** — so a `verbatim` libm kernel fails to link in the -O0
cells. **Decision: keep `ph03`'s macro substitution** (shipped with a
differential and a must-fire control, and in the deletion ledger), **and BATCH
the `-lm` edit** rather than pay a 33-row re-gate + re-measure now.
⭐ **Worth recording for whoever does it: `-lm` is a LINK-ONLY flag, so for
every pattern that calls no libm function the re-measured numbers must be
byte-identical — which makes that re-measure self-verifying rather than
risky.**

**B2 — `check_sanitizers_hardened` hard-fails on any R1h diagnostic.** That is
right for a hand-written PAT R1h and **wrong for a shipped upstream fix that is
incomplete** — i.e. it structurally forbids a row from carrying
`PROTOCOL_PHP.md` §C's strongest result as *gate* evidence. **Decision: no
harness edit.** The evidence lives in `controls/` and the report, and this is a
**standing limitation of the gate, recorded here**: ⚠ **a green php gate does
not mean the upstream fix is complete, and cannot.**

### F32 — ⚠⚠⚠ THE MANAGER ARBITRATED THE ONE NUMBER THIS FILE SAYS NOT TO ARBITRATE, AND WAS WRONG

**Retracted, and replaced by what actually happened.**

This entry said *"`PROTOCOL_PHP.md` §E says the named-spelling tail is 11 003
bytes; it is 11 004 — a fourth wrong value."* ✅ **Verified independently:
`harness/check.py:1910` is `NAMED_SPELLING_LEN = 11003`. §E was RIGHT. There is
no fourth value.** `TASK_PHP_005_REPORT.md:487-490` had already settled it —
*"both are correct about different cuts"* — and this file's own size box says so
at line 14.

⚠⚠ **So the manager took an engineer's claim on trust, wrote it into the state
layer as a finding, and thereby made this document contradict itself** — line 14
carrying the right number while this entry declared it wrong.

⭐ **The lesson is sharper than the error.** The size box's standing instruction
is *"DO NOT ARBITRATE THAT BYTE COUNT — IT HAS THREE ANSWERS AND THE DISAGREEMENT
IS A DEFINITION, NOT AN ERROR."* **The manager arbitrated it anyway, in the same
document, four sections below the warning.** ⚠ A rule written for other people is
not a rule you have read.

⚠ **And the mechanism is the one this programme already knows**: a claim arrived
in a report, was plausible, matched a pattern the manager was primed for (*"this
number keeps being wrong"*), and went into the authoritative layer **without the
one command that would have checked it** — `grep -n NAMED_SPELLING_LEN
harness/check.py`. That is `PROTOCOL.md` rule 14's shape with the roles
reversed: **an engineer premise the MANAGER had no reason to doubt, and did not
check.**

### F33 — the first PHP ladder, read off the gate's own table

`results-php/tables/ph03-uudecode-bound.md`, **`Ir(kernel)`, `small.bin`,
`O3 / isolated`** — the row's own rungs against each other. ⚠ **These are
within-row ratios only**; open item 9 forbids any comparison with a `pNN`
figure.

| rung | `Ir(kernel)` | vs `c-gcc` | `md5_fn` |
|---|---:|---:|---|
| `c-gcc` | 165 650 000 | — | `a970030d` |
| `c-clang` | 140 125 004 | −15.4 % | `1d3044b1` |
| **`safe_naive`** | 210 100 000 | **+26.8 %** | `59bd6d88` |
| **`safe_tuned`** | 171 700 000 | **+3.7 %** | `9a762cc4` |
| **`unsafe`** | 153 125 000 | **−7.6 %** | `33850579` |
| **`verus`** | 153 125 000 | **−7.6 %** | `33850579` |
| `c-gcc-h` (real 2004 fix) | 165 025 000 | **−0.4 %** | `4224991b` |

**What row 1 says, and it is the shape the crash course needs:**

1. **Naive safe Rust costs +26.8 %. Tuned safe Rust costs +3.7 %** — ✅ the
   tuning recovers **86.4 %** of the naive gap (measured, not estimated), so
   *"safe Rust is 27 % slower"* and *"safe Rust is ~free"* are **the same
   pattern written two ways.**
2. ⭐ **Unsafe Rust is 7.6 % FASTER than gcc C**, and **`verus` is byte-identical
   to `unsafe`** (`md5_fn 33850579` on both) — **the proof costs nothing at
   run time**, which is what R4≡R5 means concretely.
3. ⭐ **The hardened C — carrying the REAL 2004 safety check — is 0.4 % faster
   than the unchecked C.** The safety check is not merely free here; it is
   negative-cost, because it lets gcc drop a `setae` and two `cmove`s (F30).
4. ⚠ **`c-clang` beats `c-gcc` by 15.4 %, which is larger than every safety
   effect on this row.** **A compiler difference, not a safety difference** —
   quote a rung against a rung, never against "C".
5. ⚠ The `vec` column: **both C compilers vectorise (`xmm`); no Rust rung
   does.** That is likely most of the naive gap and is a property of *how the
   translation is written*, not of Rust.

⚠⚠ **CAVEAT, and it is the engineer's own**: `controls/spellings.py` was **not**
built, so **no ratio here is *the* cost of safety** — each is the cost of *these
spellings* of these rungs. A different safe-tuned spelling moves row 2's number
and would move this one.

⚠⚠⚠ **UPGRADED BY F39 — READ THAT BEFORE QUOTING ANY NUMBER ABOVE.** The caveat
is right and it is **weaker than the situation**. Three things it does not say:

1. **These are `fixed-R4 bound`s** — PAT's term (`.memory/02-bench-rules.md`),
   and the rule is that a bound ships **labelled, beside a cheapest-found
   counterpart**. **Above, seven numbers ship unlabelled with no counterpart.**
2. ⚠ **The obligation is inside `ph03`'s OWN hashed `why`**: *"Every pattern
   owes an in-contract spread beside its headline."* This is undischarged, not
   unforeseen.
3. ⚠⚠ **The missing number's direction is not a coin flip.** On the four PAT
   rows where anyone searched the R4 side, **three moved out of their buckets and
   every one moved against safe Rust** — `p22` by **510×** on the large band,
   `p12` and `p13` **sign-flipping**. **So point 1's *"tuning recovers 86.4 %"*
   is the single most likely claim on this row to move**, and it is the one the
   crash course would most want to quote.

### F34 — ⚠ `ph07` DOES have a fix, and the manager found it by disbelieving the engineer

`TASK_PHP_015` stopped before building `ph07` and reported that **no
`fix_commit` could be identified** — that 5.0.0's `for(;;)` survives byte-for-byte
to 5.3.0, that 5.4.0 rewrites it and *"still never consults `string->len`"*, and
that this might be **a stronger finding than `ph03`'s**. It disclosed that it had
**not bisected history**.

✅ **Manager-verified against three upstream tags. The first two claims hold; the
third is wrong, and a fix exists.**

```
php-5.0.0  mbfl_strcut body 4708 B   for(;;) present
php-5.3.0  mbfl_strcut body 4708 B   BYTE-FOR-BYTE IDENTICAL to 5.0.0
php-5.4.0  mbfl_strcut body 7065 B   rewritten
```

The 5.0.0 walk, quoted — **its only exit is `n > from`, and `p` is never compared
against `string->val + string->len`:**

```c
for (;;) { m = mbtab[*p]; n += m; p += m; if (n > from) break; start = n; }
```

⚠ `len = string->len` **is** read at the top, but only for the clamps *after* the
walk (`if (start > len) start = len;`) — **too late; the over-read has happened.**
⭐ And the same function's **second** walk *is* bounded (`if (k >= (int)string->len)`),
so `mbfl_strcut` bounds its end search and not its start search.

**But 5.4.0's prologue carries exactly the missing guard:**

```c
if (from < 0 || length < 0) { return NULL; }
if (from >= string->len)    { from = string->len; }   /* <-- the bound */
```

so `q = p + from` can no longer pass the buffer end. ⚠ **The engineer read the
5.4.0 *walk* (which is still expressed in terms of `from`) and missed the
*prologue* that makes `from` safe** — the guard moved, it did not vanish.

> ⚠⚠⚠ **SUPERSEDED IN PART BY F38 — READ THAT FIRST.** The facts above about
> the 5.0.0/5.3.0/5.4.0 *code* all hold. **The conclusion drawn from them does
> not: the real fix is `cb3cca21b345` (Ilia Alshanetsky, 2005-12-15, *"Fixed
> possible memory corruption inside mb_strcut()"*), and it is in
> `PHP_FUNCTION(mb_strcut)` in `ext/mbstring/mbstring.c` — THE CALLER, IN
> ANOTHER FILE:**
>
> ```c
> if (from > Z_STRLEN_PP(arg1)) { RETURN_FALSE; }
> if (((unsigned) from + (unsigned) len) > Z_STRLEN_PP(arg1)) { len = Z_STRLEN_PP(arg1) - from; }
> ret = mbfl_strcut(&string, &result, from, len);
> ```
>
> ⭐ **That is WHY `mbfl_strcut`'s body is byte-identical 5.0.0 → 5.3.0** — the
> bound was restored one function up and one file away, in 2005, under an
> explicit security subject line. The 5.4.0 prologue clamp is a **second, later**
> restoration of the same bound inside `mbfl_strcut` itself.
> ⚠ **So this finding's own lesson must be widened**: a missing bound is often
> restored in the prologue — **or in the CALLER, in a different file, under the
> caller's name.** A search keyed on the defect's function cannot find it, which
> is exactly what happened (F38).
> ⚠ **And the row must ask whether the caller-side guard is COMPLETE**: with
> `from == string->len` permitted, the start walk still advances `p` by `m` while
> `n <= from`, so `p` can pass the buffer end. **`ph03`'s shape — a real fix that
> is incomplete — is live here and is the row's job to settle by measurement.**

**Decisions:**
1. ⚠ **SUPERSEDED: `ph07`'s R1h is `cb3cca21b345`**, the real 2005 caller-side
   fix — not the 5.4.0 clamp, and not a hand-written control. The running build
   task was sent this correction mid-flight. `PROTOCOL_PHP.md` §F item 5's
   assumption that a `fix_commit` exists **survives, and F38 shows it holds for
   142 of the 145 ids the catalogue cites.**
2. ⚠ **The finding is NOT *"PHP never fixed this"*.** It is weaker and still
   worth having: **the fix arrived inside an unlabelled rewrite, and the
   vulnerable code shipped byte-identical from 5.0.0 through 5.3.x.**
3. ⭐ **The reusable lesson is about where a guard is looked for.** Both the
   engineer and the catalogue characterised this row by *the loop*, so both
   checked the loop in the fixed version. **A missing bound is often restored in
   the PROLOGUE, not at the site** — `F1`'s three-frames problem arriving in the
   *repair* rather than in the defect.

### F35 — ⚠⚠⚠ THIS BOX'S `grep` REPORTS **NOTHING** IN THE CORPUS'S MOST-CITED FILE

⚠ **The mechanism is NOT "the box has a weird grep" — that was the manager's
first framing and it was wrong.** `/usr/bin/grep` is **GNU grep 3.11 and handles
this file perfectly**. What an agent gets in a `Bash` call is a **shell function**
from the interactive profile that dispatches to **`ugrep 7.8.4`**, and *that*
exits **1** with **no stdout and no stderr** on a file holding one non-UTF-8
byte — **indistinguishable from a true absence.** Measured, same file, same
pattern:

```
$ grep       -n "PHP_FUNCTION(str_repeat)" .../ext/standard/string.c ; echo $?
1                                    <-- no output, no stderr, "not found"
$ grep      -an "PHP_FUNCTION(str_repeat)" ...                       ; echo $?
4115:PHP_FUNCTION(str_repeat)                                            0
$ /usr/bin/grep -n "PHP_FUNCTION(str_repeat)" ...                    ; echo $?
4115:PHP_FUNCTION(str_repeat)                                            0
$ rg         -n "PHP_FUNCTION\(str_repeat\)" ...                     ; echo $?
4115:PHP_FUNCTION(str_repeat)                                            0
```

✅ **Trigger isolated to ONE BYTE.** Copy `string.c`, replace `S\xe6ther` with
`Saether`, change nothing else → the wrapper `grep` finds line 4115 and exits 0.

⚠⚠ **Three consequences, and the third is the one that will waste a day:**

1. **The two search tools every agent has disagree**, and the one that fails,
   fails silently. The `Grep` tool is ripgrep-backed and sees the line; `grep`
   in a `Bash` call does not. **An engineer who greps the pinned tarball and
   finds nothing has learned nothing.**
2. **`grep -a` fixes it** through the wrapper, and so does `/usr/bin/grep`.
3. ⚠⚠ **THE SAME COMMAND BEHAVES DIFFERENTLY TYPED THAN IN A SCRIPT.** A shell
   function is not exported to `sh`, so `sh probe.sh` gets GNU grep and
   **succeeds** where the identical line pasted into a `Bash` call **fails**.
   The manager hit this while checking this very finding — `refetch.sh` printed
   a match for the file it had just been told was unsearchable. **A probe script
   is therefore NOT a faithful reproduction of what an agent sees**, which
   undercuts the usual "wrap it in a script and re-run it" repair.

**Priced against the corpus** — `iconv -f UTF-8 -t UTF-8` over all 1 170 `.c`/`.h`:

| | |
|---|---|
| non-UTF-8 files | **41 of 1 170** |
| of those, **cited by `CATALOGUE.md`** | **5**: `ext/standard/{string,html,reg,formatted_print}.c`, `ext/calendar/calendar.c` |
| catalogued rows citing one | **13 of 91** — `ph05 ph06 ph08 ph12 ph18 ph19 ph20 ph21 ph26 ph27 ph31 ph32 ph47` |
| **including, in the next batch** | ⚠ **`ph12` and `ph21`** (both `ext/standard/string.c`) |

✅ **No built row is affected**: `uuencode.c` (`ph03`) and `mbfilter.c` (`ph07`)
are both clean UTF-8, checked.

⭐ **Where the bad bytes are decides how bad this is, and it is two different
problems.** In four of the five files it is **one line of the licence header** —
an author's name in ISO-8859-1 (`Stig S\xe6ther Bakken`, `Jaakko Hyv\xe4tti`,
lines 15–17). **`ext/calendar/calendar.c:123` is the exception and it is live
code**: `static char alef_bet[25] = "0\xe0\xe1\xe2…"`. So:

1. **The search hazard is total** — the header byte poisons the *whole file* for
   `grep`, regardless of where you are looking. **Rule: always `grep -a` against
   the pinned corpus.** Landing in `PROTOCOL_PHP.md` (staged — `TASK_PHP_016`
   is reading that file; `PROTOCOL.md` rule 11).
2. **The decode hazard is narrow and latent** — `harness/check.py` reads row
   sources with **strict** UTF-8 (`open(path).read()`, e.g. `:824`, `:2416`), so
   a row whose extraction *region* contains such a byte raises
   `UnicodeDecodeError` **in the frozen PAT gate we may not edit**. Only
   `calendar.c` (**`ph31`**) has one in code. ⚠ `harness-php/provenance.py` is
   safe — `:478` and `:780` pass `errors="replace"` — **but that means the
   overlap score for an affected file is computed on mangled text on both
   sides**; equal-and-mangled still matches, so it is a hazard only if one side
   is re-typed rather than copied.

⚠ **This is the THIRD silent false negative of the same shape in this project** —
`copy_from_slice` (*"no spec exists"*, stood TASK_004→048), `index_mut`
(TASK_089), and F34's *"no fix exists"*. **The first two needed a human to
misread a tree. This one needs nobody to make a mistake at all.**

### F36 — the next batch's four upstream repairs, found BEFORE the tasks were written

F34 cost a task: `ph07` stalled at *"no `fix_commit` exists"* and the manager had
to overturn it. So the manager surveyed the **whole** next batch first. ✅ **All
four citations verified byte-exact against the pinned tarball, and all four
fixes exist**, each inside the 5.0 → 5.2 window:

| row | 5.0.0 defect (verified line) | fixed by | what upstream actually did |
|---|---|---|---|
| **ph16** | `FD_SET(this_fd, fds)` — `streamsfuncs.c:541` | **5.1.0** | `PHP_SAFE_FD_SET` + `&& this_fd >= 0` |
| **ph29** | `emalloc(to_read + 1)`, `to_read` a `long` — `streamsfuncs.c:321` | **5.1.0** | `if (to_read <= 0) RETURN_FALSE;` — **then 5.3.0 adds** `safe_emalloc(1, to_read, 1)` |
| **ph12** | `if (len && offset >= s1_len)` — `string.c:4786` | **5.2.0** | the `len &&` short-circuit **deleted** → `if ((offset + len) > s1_len)` |
| **ph21** | `int result_len` `:4120` · product `:4144` · dead disjunct `:4145` | **5.2.0** | `int`→`size_t`, **the guard DELETED**, `emalloc`→`safe_emalloc(len, mult, 1)` |

⭐⭐ **Two of the four repairs REMOVE the guard, and that is the finding.**
`ph21`'s `if (result_len < 1 || result_len > 2147483647)` and `ph12`'s
`if (len && …)` are not strengthened upstream — they are **thrown away** and the
obligation moved into a type (`size_t`) or an allocator wrapper
(`safe_emalloc`). **The catalogue called `ph21` *"a guard killed by the type of
the variable it tests"*; upstream's own fix was to change the type and delete the
guard, which is that reading confirmed by the maintainers.**

⭐ **`ph16`'s fix is not a check — it is a check on one platform.** `PHP_SAFE_FD_SET`
is `#ifdef PHP_WIN32` → bare `FD_SET`, `#else` →
`do { if (fd < FD_SETSIZE) FD_SET(fd, set); } while(0)`
(`main/php_network.h:194-204`, 5.1.0). ⚠ **The macro's name promises safety
unconditionally and its POSIX branch alone delivers it** — correctly, because
Win32's `fd_set` is a counted array rather than a bitmap, and the source says so
in a comment. **R1h must state which branch it compiles.**

⚠ **`ph29`'s repair is two-stage** (guard in 5.1, wrapper in 5.3), so *"the
fix"* is a choice the row has to make and justify — like `ph03`'s two hunks.

⚠ **What is NOT done: none of the four commits is pinned**, only the tag window.
That is the row engineer's job, and the window is the expensive half.

> ✅✅ **SETTLED AT `TASK_PHP_020` → F46, AND THE CATALOGUE WAS RIGHT WHILE I
> WAS WRONG. Read that, not this.** This entry said *"`ph29`'s catalogued
> mechanism is not yet verified — `to_read` is a `long` and 5.0.0's `emalloc`
> takes a `size_t`, which on this 64-bit box truncates nothing. **Either the
> mechanism is 32-bit-only, or it is elsewhere, or the row is
> mis-catalogued.**"* **The measurement matched none of the three.**
>
> A probe replicating `zend_alloc.c:129/132/135/182/201` verbatim: `to_read =
> LONG_MAX` → `size = 2^63` → **`real_size = 0`** → a header-sized `malloc`
> **succeeds**. ⚠ **The truncation is `REAL_SIZE` at `:129`** — F5's family,
> already in this file — **and never was at `emalloc`'s signature, which is
> where I looked.** ⚠⚠ **And the row is 64-bit-ONLY: the exact opposite of the
> "32-bit-only" limb I offered.** ⭐ Three strengthenings came with it — a
> **UB-free** trigger (`to_read = 4294967295`, avoiding a `LONG_MAX + 1` gcc
> may fold), it **zeroes `CHECK_MEMORY_LIMIT`'s accumulator**, and it **reaches
> the second truncation** (`zend_alloc.h:53`'s `size:31`).
>
> ⭐ **The transferable part is not the arithmetic.** I doubted a catalogue row
> because *a mechanism I could not see at the frame I was looking at* — and F1
> is this project's oldest finding: **the citation names one frame and the
> defect lives in another.** **I applied F1 to kills and to fixes and did not
> apply it to my own doubt.**

### F70 — ⚠⚠⚠ A **TRUE SENTENCE ON THE WRONG SUBJECT**, AND NOTHING ABOUT IT READ AS INVENTED

`TASK_PHP_028.md` §4.3 warned that *"`ph03`'s declaration backticks nothing, so
`spellings` is 0 … if `ph03` cannot be searched, STOP."* **The sentence is
`p05`'s.** ✅ Measured from `.idiom_audit` in the gate records: `p05` **0**,
`ph00-smoke` **0**, **`ph03` 11** (6 forbidden) and searchable with no `spec.md`
edit, `ph16` **23** (10), **`ph29` 4 — all four `forbidden`, ZERO `required`.**

⚠⚠ **So the hazard is real, is on a DIFFERENT ROW, and is WORSE than described:**
on `ph29` a `spellings.py` cloned from `ph07` would **pass every candidate while
checking nothing** — a validator that cannot fail, §H's exact target. → item 51.

⭐⭐ **This is `PROTOCOL.md` rule 14 in its hardest-to-catch direction.** The
usual shape is a premise nobody measured (F4's *"123 ASan reports"*, F12's
*"~7,000 words"*). **Here both halves were true**: the sentence really is in the
tree — inside `ph16`'s **hashed `why`**, printed by `check.py` on **every**
`ph16` run, which is where I read it — and `spellings: 0` really did happen.
**Only the subject was wrong, and a wrong subject leaves no trace in the
evidence.** ⚠ The engineer caught it by looking up the number instead of
trusting the sentence.

⚠ **Sibling, same week, same class: F52's EIGHTH shape, in a manager probe.**
`.tasks-php/probes/item48_decide.py` v1 compared **prose-bearing** `c_file_line` cells, so
*"distinct sites"* was guaranteed and it returned a perfect **30 of 30**. ⭐ **A
result that is too clean is the only warning this shape gives**; the repaired
probe brackets three granularities and carries must-fires for the prose strip.

### F69 — ⭐⭐ ITEM 48 WAS **TWO QUESTIONS WEARING ONE NUMBER**, AND §F5 WAS RIGHT ALL ALONG

*"The largest unmade decision on the PHP side"* — 30 rows whose ids name several
`fix_commit`s — **decided by measurement, and §F5's singular spelling stands.**
**R1h is the `fix_commit` of the id whose `c_file_line` the row's kernel
EXTRACTS**; a kernel extracts one site, that site is one id, that id has one fix.
The hypothesis that would have broken it is **dead**: at `file:line` **29 of 30**
rows have every id at a distinct line, and by **enclosing function 24 of 30**.
**Nowhere is one site patched N times.** Detail and the refused alternatives:
retired item 48.

⭐ **`_029` had already answered it from the other side** — *"a single `ph73` row
cannot ship a single sha-pinned `kernel_hardened.c`"* — and the two statements
are one: **a row pricing five sites cannot have one R1h; a row extracting one
always can.** ⚠ Its headline says `ph73` spans **four** files; it is **five**
(`zend_execute.c`, `zend_object_handlers.c`, `zend_execute_API.c`,
`zend_objects.c`, `streamsfuncs.c`) — conclusion and all five per-id verdicts
unaffected, *the citation and the story about it are two separate claims* again.

⚠⚠ **WHY IT NEVER BIT: THE SPREAD IS A TEMPORAL-AXIS PROPERTY** — **21 of 31
temporal rows (68 %)** against **6 of 29 type (21 %)** and **3 of 42 spatial
(7 %)**. **All four built rows are spatial and none is in the 30**, so §F5
survived four builds by **sampling**, not by being right.

⚠ **Additive, and a LOWER bound: 11 of 163 `fix_commit`s do not claim to be
repairs** — `07b7ba8b4004` *"Improved ternary operator performance"* (`ph77`,
`ph83`), `ff9d0fcc783c` *"is_numeric_string() optimization"* (`ph23`),
`e155585e6e13` *"Reimplemented date and gmdate"* (`ph24`), and seven more; 18
further commits are ambiguous. **This is §C one step on** — §C says an upstream
fix is not automatically *correct*; this says **it may not be a fix at all**,
which is F45 seen from the repair side. ⚠⚠ **Subject lines only, and a subject
is not a patch — it RANKS and does not decide.** ✅ Clean negative that had to be
checked first: the *"30 rows"* is **not** an artefact of mixed sha lengths
(histogram `{11:1, 12:147, 38:1, 40:15}`; the one prefix pair is **cross-row**,
`ph54`/`ph78`), though corpus distinct fixes is **163, not 164**.

### F68 — ⚠⚠⚠ `NOT-THE-REPAIR` IS NOT A PROOF OF EXCLUSION FOR **17 OF 43**, AND F64's OWN FIGURE WAS WRONG

`TASK_PHP_031` §7.1. `ph64`'s `562f886ecb14` **removes no line at either cited
site, ever** — it repairs a **third function in the same file** — so **no
line-level pre-image screen can find a fix of this shape.** ✅ **Confirmed
mechanically: `defect_file ∈ patch_files` for 17 of 17 non-decisive records,
zero exceptions**, so the whole non-decisive population is **same-file /
different-function**: `INAPPLICABLE`'s mechanism one granularity down.
▶ ✅✅ **LANDED AT `TASK_PHP_040` §4 (F95), WITH SIX NEGATIVES — and the 17
records that moved are EXACTLY this list, reproduced by a different route.**
`170 records · NOT-THE-REPAIR 25 + INAPPLICABLE-SAME-FILE 18 = 43`, 0 partition
violations; the docstring's *"PROOF OF EXCLUSION"* qualified **in the same
edit** as asked. ⛔⛔ **AND ANSWERING *"does either row exercise it?"* EXPOSED A
SOUNDNESS DEFECT ONE LAYER DOWN** — `same_function` was naming a function the
hunk does not touch, promoting an exclusion to a **proof** on 1 of 170 records.
**Repaired by the manager; 25 exclusions, not 26, and not 43.** ▶ **See F95.**
**The original ask:**

⚠⚠ **F64's `33/43` IS NOT REPRODUCIBLE — the tool says `26/43`, and the
predicate is provably identical** (`decisive == (bracketed or same_function)`,
43 of 43, zero mismatches). **Two independent measurements agree on 26**, one of
them `_031`'s by hunk-reading. ⚠ **The manager's hypothesis that his own
`:0`-sentinel repair caused it is MEASURED FALSE** — 0 of the 43 affected, and
only 2 ids corpus-wide move at all. **Cause unknown; cite 26.**

⭐ **A different-file instance exists too, and item 49 predicted the exact row:**
`ph46`/CRASH-053's cited text lives in the pre-image of `Zend/zend_vm_def.h` and
`zend_vm_execute.h` — **the VM-GENERATION BOUNDARY, and it is 5.0.0-specific**,
because 5.0.0's executor *is* `zend_execute.c` and from 5.1 it is **generated**.
So a live R1h candidate sits where the programme recorded an exclusion. ✅ **F64's
careful phrasing already kept it out of the citable set — the guard worked.**

❌ **A manager-proposed extra signal is REFUTED and must not be added.** Scoring
a bug-numbered `.phpt` in `patch_files` as evidence of a repair gives
**53 % / 46 % / 45 %** across non-decisive exclusions, decisive exclusions and
candidates — **no discriminating power**, because nearly every commit in that
column *is* a repair; that is how it got there. **F61's shape, and measuring it
is what stopped it shipping.**

### F67 — ⭐⭐⭐ `ph16`: THE NEGATIVE `R3−R4` SPREAD IS A **RESULT**, AND THE TWO RUNGS ARE CHEAPEST UNDER **DIFFERENT SPELLINGS**

`TASK_PHP_028`, one row, whole task — ⭐ **and stopping after one was authorised
and right.** Manager re-verified: `check.py: PASS`, brackets `66/0` and `10/0`,
**no re-measure** (`controls/*.py` is not among `measure.py`'s 19 pinned
sources), `spec.md` and all four rung `.rs` **byte-identical to dispatch**, **no
rung re-shipped.**

```
                            small/call   large/call   Ir/window byte
fixed-R4 bound  R3ship-R4ship   -1.22 %      -1.84 %       -1.94 %
cheapest-found in-contract      -1.42 %      -1.87 %       -1.94 %   (r3_split_at)
```

**No pair interval.** `r3_split_at`'s win is **entirely fixed-term** (−7.0
Ir/call), so on the marginal statistic **the R3 endpoint is degenerate too.**

⚠⚠ **THE TASK'S OWN HYPOTHESIS IS REFUTED: this is not a spelling artefact.**
The R4 side is **degenerate** — four respellings of the very index the mechanism
blames are all dearer or byte-identical, **including `r4x_subslice`, which is
R3's own spelling, at +1.80 %.** ⭐ **The mirror control settles it**:
`r3_absindex` (R3 given R4's signature) is **byte-identical to `safe_naive.rs`**
at **+33.07 %**. **So the subslice is worth −24.9 % in safe Rust and +1.8 % in
unsafe Rust: the two rungs are cheapest under DIFFERENT spellings, and R3's
minimum sits under R4's.** ⚠⚠ **n = 1 — NOT reported as an effect**, and `ph03`
(+12.19 %) is positive, so there is no run here either.

⭐ **How the candidate set was defended, which is the part that transfers**: a
callgrind `--dump-instr` decomposition that **closes to 0 Ir** — `+1 099 728`,
the record's `unsafe − safe_tuned` **exactly** — attributing the gap to arm 2's
one extra `lea` (+62 Ir/call) against R3's bounds tests (−18 Ir/call). **A
spellings search is chosen by the same person who reports nothing cheaper
exists; an accounting that closes is the answer to that.**

⚠ **Two further corrections it landed**, both now open items: `ph16`'s own
`NOTES.md` §8b **retracted** — the R2→R3 *guard* respelling is byte-identical in
**both** directions, so the gap is the subslice + `chunks_exact`, and the `.rs`
comments still say otherwise (item 53) — and **which statistic a bound is quoted
in is undecided across rows** (item 52).

⭐ **§H worked exactly as designed: 54 negatives, 0 failed, FOUR defects caught**
— including **a wrong claim the row had already published** and a
`per_instruction` stage that returned **zero** on a rebuilt dump and failed
loudly only because stage 6 asserts the sum against `callgrind_annotate`. **Three
of the four were in the reporting, not the numbers, and NONE was reachable
through a gate run** (the gate hashes `controls/*.py` and never runs them).

### F71 — ⭐⭐⭐ ROW 5 IS THE **FIRST TEMPORAL ROW**, AND SAFE RUST TURNS THE DEFECT INTO A **WRONG ANSWER**, NOT A PANIC

`TASK_PHP_032`. **`patterns-php/ph64-callback-frees-cursor/`** — a walk whose
cursor advances **after** a callback that may free the element it holds.
✅ **Manager-verified from the record, not the prose**: `verdict PASS`, **0
failures**, contract `7ec3fc87b309`, `verus.rs` **39 verified / 0 errors** (47
under the twin), brackets **`66/0`** and **`12/0`** — `10` plus the row's two
new measure records, exactly as predicted. Three gate rounds, **19 → 3 → 2 → 0**;
the last two were the irreducible `[tables]` staleness of the
`gate → report → gate` chain, which corrected itself.

⭐⭐⭐ **THE LADDER RESULT, AND IT IS THE MOST INTERESTING ONE THE PROGRAMME HAS
PRODUCED.** `zend_llist_element *next` is a **raw pointer**, and safe Rust
cannot express that list without `Rc`, `RefCell` or raw pointers — so the
faithful safe port is an **INDEX ARENA**, and **a dangling index is an ordinary
in-bounds read of a slot that is still there.** ⭐ **That is, to the byte, what
5.0.0's size-class cache does with the real block.** So **safe Rust does not
turn this defect into a panic; it turns it into a WRONG ANSWER**, and what
removes it is `562f886ecb14`'s **logical** invariant. `verus.rs` proves `wf`
(every link NIL or in range, `next` ascends, `prev` descends) — **and `wf` holds
with the guard DELETED.** ⚠⚠ **Memory safety and the upstream fix are ORTHOGONAL
on this row, and only the value postcondition can see the difference.**
⭐ **`CLAUDE.md` rule 6 in action: this is a FINDING, never a kill** — and it is
the axis where that bias has done the most damage (six of ten refusals).

⭐⭐ **STAGE 7h WAS GREEN FIRST TRY — a falsifiable prediction that held.** `_031`
§6.4 measured R1h as changing nothing on the benign domain, and `TASK_PHP_032`
was told to **stop and report rather than adjust the corpus** if 7h failed.
⚠ `ph07` was rebuilt for exactly the opposite situation.

⭐⭐ **F66's oracle finding CONFIRMED AT SCALE: 213 of 213.** The visit fold is
bit-identical between R1 and R1h on every trigger window, because the freed
39-byte element lands in `AG(cache)[5]` with its **payload intact**. The row
folds `l->count`, the dtor count, the refusal count and the allocator tally
instead, **and those move on all 213.** ⭐ The sharper half is
`inputs/adversarial-reuse-*`: **one same-size-class `emalloc` in the same
callback** LIFO-pops the freed element back out, and **R1 SIGSEGVs at all four
`DEL_LLIST_ELEMENT` arms while R1h is clean.**

⭐⭐ **FIDELITY REPRODUCES THE CORPUS'S OWN RECORDED CATEGORY.** On plain
`malloc`/`free`: `heap-use-after-free`, **`WRITE of size 4`, frame #0 at
`basic_functions.c:2135`** — `index.csv`'s cited line — frame #1 in
`zend_llist_apply`. **Silent on the faithful cached allocator.** ⭐ Measured
rather than quoted, which is what `crashes_pristine_5_0_0 = False` *means*.

⚠⚠ **THE C-vs-RUST COLUMN ON THIS ROW IS NOT A SAFETY COMPARISON — AND THIS IS
THE TRANSFERABLE PART.** §B forbids a Rust rung from linking the shim, so the C
rung **allocates `2n+2` blocks per call** while the Rust rungs **count**:
**60 % of the C's instructions are in libc `malloc`/`free`.**
⭐ **`PROTOCOL_PHP.md` §B2's *"reproduce the tally arithmetically"* is free only
while a row makes O(1) allocations per call, and `ph64` is the first php row
where it is O(n).** → open item **54**.

⚠⚠ **`kernel_exclusive_ir` IS WRONG HERE IN TWO DIRECTIONS**: it **hides
`562f886ecb14` entirely** (identical to the instruction for both C rungs,
because gcc keeps the guard's symbol out of line) **and it reverses R2 vs R3**
(+2.9 % dearer vs −24.6 % cheaper on the marginal). Every published figure is in
`marginal_ir_per_call`, following `p08`/`p11`. **R1h costs +15.98 Ir/call, flat
in list length.**

⭐ **Verus took no `rlimit`.** `kernel` would not verify at **600** as one
function and verifies at the **default 10** once `run_spec` was made
`#[verifier::opaque]`. **Raising the budget was tried first and did nothing** —
worth knowing before anyone reaches for `#[verifier::rlimit]`.

⚠ **TWO OF THE ENGINEER'S OWN DECLARED EXPECTATIONS WERE REFUTED BY ITS OWN
CONTROLS, and both misses are recorded in the controls' headers rather than
rewritten.** ⭐ The better one: the cached-`next` counterfactual is **NOT
strictly weaker** — it removes **189/189** wild walks **and adds 196/196
use-after-frees of the cursor's SUCCESSOR**. **The two hardenings are not
ordered by strength**, which is a stronger finding than the one predicted.

⚠ **DECLARED AND NOT DONE, and both are the right call.** (a) **No
`controls/spellings.py`** — `ph64`'s `fixed-R4 bound` is **+17.08 % / +15.37 %**,
**unsearched on both sides**, and ⚠⚠ **it BREAKS the `ph16`/`ph29` negative
pair.** The spread table is now **`ph03` +12.19 · `ph16` −1.22 · `ph29` −6.06 ·
`ph64` +17.08** — **two positive, two negative**, so *"safe-tuned cheaper than
unsafe"* is **2 of 4, not a trend.** (b) **`_031` §4.3 is NOT measured** and is
carried in `spec.md`/`NOTES.md` as an **OPEN ITEM, not a finding** — ⚠ **so
`ph64` is NOT the fifth of five**; the fix-completeness tally reads **five rows,
five different answers.**

### F72 — ⭐⭐ ITEM 51 DECIDED: `ph29`'s `required` SIDE IS **SPELLINGS WITH THE TICKS DROPPED**, AND TWO OF THE EIGHT MUST NOT BE QUOTED AS WRITTEN

Manager, `.temp/mgr169/NOTES.md` §1, three probes each `--selftest` PASS.
⚠ **UNREVIEWED** (rule 9) — it is the manager's own measurement and is being
executed by `TASK_PHP_033`, which may overturn it.

**The question** was whether `ph29` pinning **zero** required tokens is a defect
or a `p05`-style prose-only declaration — `patterns/p05-index-flatten` backticks
nothing at all, ships, and is documented that way. **Decided: a defect.** ✅ **7 of 8
leading spans already pin at least one rung**, so these were written as
spellings and the quotes were simply dropped. And ⚠ **`ph29` is the only real
PHP row pinning zero** — `ph03` 5, `ph07` 14, `ph16` 13, `ph64` 7, `ph29` **0**
(`ph00-smoke`'s 0 is not a counter-example: relocated PAT calibration kernel, no
PHP provenance, prices nothing).

⚠⚠ **But the repair is NOT "add backticks", and that is the finding.**
**`required[0]` and `required[1]` carry NO ENGLISH AT ALL** — a bare span per
language and nothing else. `required` is given **no verdict by design**,
precisely because *which rungs an entry binds lives in its English*. Quoting
those two as written pins spellings the shipped tree **contradicts**:

* `tr.wrapping_add(1)` pins a **BINDING NAME**. All four Rust rungs compute the
  request, but the safe two spell `(to_read as u64).wrapping_add(1)`. Quoting
  `tr.…` would put two rungs out of their own contract on a variable name —
  **p17's whitespace disaster in a new costume**. ▶ `.wrapping_add(1)` pins all
  four at one line each (100 / 64 / 88 / 450).
* `vset_unchecked(…)` is **genuinely unsafe-side** — the safe rungs spell the
  **checked** `read_buf[recvd as usize] = 0`. No shared span exists and
  per-language keys cannot say it (both are Rust), so ▶ **the entry owes a
  sentence**, or the record carries two absences no reader can adjudicate.

⭐ **The falsifiable prediction** (`.tasks-php/probes/ph29_predict.py` runs the *shipped*
`idiom_audit` on an *in-memory* edit): `spellings` 4 → **12**, `pairs` 12 → **36**,
`present` 0 → **22**, `required_pins_nothing` **0**, `required_absent` 0 → **2**,
`forbidden_hits` **0**. The naive all-eight edit gives `present 20`,
`absent 4` and one dead pin.

⚠ **What it buys, stated honestly: `required` CANNOT FAIL THE GATE and this does
not change that.** It adds no check that can fail. It buys the **spread
search** — the admissible class becomes grep-decidable — which is the whole
reason item 51 blocked the spellings task, and the same limitation TASK_021
recorded for `p05`. ▶ **`ph29` becomes *searchable*, not *enforced*.**

⚠ Also owed in the same hashed block: `forbidden[0]` closes *"NOTE THE ABSENCE
OF BACKTICKS throughout this entry and the three below"* — **false about its own
scope**; `forbidden[2]` carries `` `calloc` `` and `forbidden[3]`
`` `#undef _FORTIFY_SOURCE` ``.

⚠⚠ **THE CAUSE I GAVE HERE WAS A STORY, AND `_033` FOUND THE REAL ONE.** This
paragraph read: *"an over-correction crossed a polarity boundary — `forbidden[0]`
records that the gate refused this row twice for quoting the expression it was
protecting, and the lesson was generalised one step too far into `required`."*
Plausible, and **no evidence was ever offered for it.**

`_033` ran `git show HEAD:` instead. ✅ **Manager-re-verified**, parsing the
previous `spec.md` through `check.py`'s own reader — per language key, and the
common suffix between the two keys:

```
             len(c)   len(rust)   common TAIL
required[0]      20          18             2
required[1]      22          39             0
required[2]     722         713           706      <- ~98 % a SHARED prose block
required[3]     410         405           396      <-  ~97 %
```

⭐⭐ **THE REAL CAUSE: `required[2]` and `[3]` are a short per-language span
followed by a byte-identical ~700 / ~400-byte tail — a folded `why`. A repair
pass folded the two entries that HAD a `why` and left the two bare 18–22-byte
spans that did not.** Nothing noticed, because **`required` has no verdict and
`spellings: 0` prints clean.** ⚠ The over-correction story explains why
*`forbidden`* entries here avoid backticks — which is true, and documented
inside `forbidden[0]` itself — and explains **nothing** about the `required`
side.

⭐ **What survives, because it was measured rather than told:** the manager
reproduced the backtick trap *while writing the task file* — the first draft of
`.tasks-php/probes/ph29_predict.py` put the old span **in backticks** into its explanatory tail,
which would have added a second pin, including the dead char-literal one F73
warns about. Caught before it ran. ⚠ **And `_033` then hit the trap's SIBLING**
(F76 below). *A documented trap that goes on catching its own documentation's
readers is a trap whose write-up is aimed at the wrong half.*

### F76 — ⚠ THE `idiom` KEY WHITELIST IS THE SAME TRAP ONE LEVEL UP, AND THIS ROW HAS PAID FOR IT TWICE

`_033`'s first draft put §2.3's new English under a `"note"` key.
**`idiom_problems` refuses any key outside `IDIOM_LANGS`** — a hard gate
failure. ⚠⚠ **`ph29` had already paid for exactly this** (`NOTES.md` §12 item 0,
a `why` key). ✅ Per `TASK_PHP_033.md` §2.6 the engineer proposed a **prose** fix
and did **not** invent a gate check, which is the right call: the gate already
catches it loudly: the defect is that the entry *shape* is undocumented where an
author reads. ▶ The keys are `c` and `rust`, **and nothing else.**

### F73 — ⚠⚠ A DECLARED SPELLING CONTAINING A **CHARACTER LITERAL** CAN NEVER MATCH — LATENT AT 6 PHP ROWS, ⛔ **AND NO LONGER LATENT AT 14: `0 of 33 PAT` STILL, BUT `1 of 14 PHP`**

Manager, `.tasks-php/probes/charlit_reach.py` (`--selftest` PASS, 6 must-fire
negatives; the detector is **differential** — it asks whether the *shipped*
blanker changes the span, so it cannot drift from the matcher, and P3 confirms
it does **not** trip on Rust lifetimes `&'a [u8]`).

⛔⛔⛔ **RE-MEASURED 2026-09-17 BY `TASK_PHP_064`, WHICH PROMOTED THE PROBE TO
`.tasks-php/probes/charlit_reach.py`: `PAT 0 of 33` UNCHANGED, `PHP` **1 of 14**.**
The hit is `ph52-concat-copy-uninit` `required[0].rust`, spelling `` `ensures` ``,
which the shipped blanker erases to seven spaces — so it **pins nothing**, and
the row's own gate record already says so (`required_pins_nothing`).
⭐⭐ **AND THE MECHANISM IS NOT A CHARACTER LITERAL, WHICH IS WHY THIS FINDING'S
OWN TITLE DOES NOT REACH ITS OWN SUBJECT.** `ensures` is a **Verus clause
keyword**. ▶ **The hazard is *any span the shipped blanker erases*; `character
literal` was the instance that prompted the finding** — `F147`'s mechanism, in a
finding's title rather than in an instrument. ✅ **The `forbidden` half — the ban
that cannot fire and that FAILS the gate — is still `0`, so the RULE's force is
undiminished.** ⚠ Re-spelling the title is a RULE change and is not done here.
⭐ **`F73` NAMED ITS POPULATION (`0 of 6 PHP`), WHICH IS THE ONLY REASON THIS
MOVE IS DETECTABLE AT ALL** — `law 17` earning itself on a finding written
before it existed.

`exec_code` layer 1 blanks *"comments and string/char literals"*. For `"..."`
that is right. For a **C character literal** — an executable operand, not text —
the consequence is that the matcher never sees it:

```
c/kernel.c:247    read_buf[recvd] = '\0';     <- ph29 really does spell its own fault line
exec_code         read_buf[recvd] =     ;     <- what spelling_matches is given
```

* in `required` it reports `pins nothing` — visible, but only to a reader who
  knows to distrust it. **`ph29`'s `required[1].c` is exactly this**, and it
  names the row's own fault line.
* ⚠⚠ in `forbidden` it is **a ban that cannot fire**, and since TASK_068
  `forbidden_hits` is the half that **FAILS** the gate — *a check that silently
  cannot fail*, `PROTOCOL_PHP.md` §H's exact target, sitting inside the frozen
  infrastructure.

✅ **Reach measured: 0 affected spellings across 33 PAT rows and 6 PHP rows, 0 of
them `forbidden`.** So it is **latent, not live** — and that is precisely what
decides the repair: backticking `read_buf[recvd] = '\0'` would **create the
first affected spelling in either programme**. ▶ Respell `read_buf[recvd] =`,
which pins `kernel.c:247` and `hardened:175`, one line each.

⚠⚠ **NOT a bug report against `harness/`, and no edit is proposed or wanted.**
The blanking is deliberate and documented in `exec_code`'s own docstring;
`exec_code` is hashed into all 33 PAT gate records. **The rule this yields is a
WRITING rule: never backtick a span containing a character literal.**

### F152 — ⛔⛔ **EIGHT STANDING CLAIM DOCUMENTS — INCLUDING `PROTOCOL_PHP.md` ITSELF — ARE IN *NEITHER* `.temp/` CENSUS, BECAUSE BOTH SCOPE BY DIRECTORY AND THE PROPERTY IS ABOUT DOCUMENT KIND**

Manager, ⛔ **UNREVIEWED** (rule 9). **The site was found by `TASK_PHP_064`'s
engineer**, while repointing a citation it was told to leave alone; the census
below is mine.

**`citecheck.py`'s `CLAIMS` excludes `.tasks-php/*.md`, and it says why:** task
files *"say `scratch under .temp/phNN/` as an INSTRUCTION TO CREATE"*.
✅ **That reason is correct — and it is a reason about `TASK_PHP_NNN*.md`, not
about a directory.** `scratchdeps.scan_set()` reads only `RECAP_PHP.md` and
`.memory-php/*.md`, so it does not cover them either.

✅ **MEASURED over `.tasks-php/*.md` minus `TASK_PHP_*` and `*_REPORT.md`:
8 standing documents · 35 `.temp/` citations · 9 ALREADY GONE.**

| document | citations | note |
|---|---:|---|
| **`PROTOCOL_PHP.md`** | **18** | ⛔ **the protocol itself** — 3 targets already gone, and `:1401` cited `F73`'s probe in scratch |
| `NULLCTL_001.md` | 5 | the evidence record the *last* promotion produced |
| `ADJUDICATION_001.md` · `ROW13_001.md` · four others | 12 | 6 gone |

⛔⛔ **THE PROTOCOL IS THE WORST PLACE FOR THIS AND THE MOST PREDICTABLE.** It is
where `§H` is defined — *a validator lands with its must-fire negatives or it
does not land* — and it carried a `.temp/mgr169/charlit_reach.py` pointer for
six days, in neither census, next to a figure that had gone false.

⭐⭐ **THE MECHANISM IS THE SESSION'S, FOR THE THIRD TIME: A SCOPE DEFINED BY
DIRECTORY WHERE THE PROPERTY IS ABOUT KIND.** `F147`(d) was *a section-level
property implemented as a file-level exclusion*; `F151` was *a role-set
implemented as a hand-written list*; this is *a document-kind property
implemented as a glob*. ▶ **All three are the same error and none of the three
repairs generalised to the next one** — which is `F147`'s own claim, now with
`n = 3` inside one week, **every instance in a different instrument.**

⚠⚠ **WHAT THIS IS NOT: 35 DEFECTS.** Most are `.log` provenance notes, the
benign class. ▶ **The finding is that nobody was looking**, and that the nine
dead pointers had no reporter. ⛔ **NO REPAIR IS PROPOSED HERE** — widening
either census is a choice between two homes (`F131`), and I have just published
a wrong count by reaching for the nearest instrument. → open item **156**.

### F151 — ⛔⛔⛔ `citecheck.py`'s SCAN SET WAS A **LIST** WHERE THE GATE HAS A **DERIVATION**, SO IT CERTIFIED THREE OF FIFTEEN HASHED ROLE-CLASSES — AND THE LEFTOVER IT MISSED IS THE ONE NAMED IN THE COMMENT DOCUMENTING ITS OWN LAST REPAIR

Manager, ⛔ **UNREVIEWED** (rule 9). Found while adjudicating item 148, which is
the only reason it was found — nobody was looking here.
▶ **Run it, do not quote this row**: `python3 .tasks-php/citecheck.py`.

**WHAT IT SCANNED AND WHAT THE GATE HASHES.** `citecheck.py` read a row's
`spec.md`, `NOTES.md` and `controls/*`. `source_sha256` in every php gate record
hashes **15 role-classes** per row — `verus.rs`, `unsafe.rs`, `safe_naive.rs`,
`safe_tuned.rs`, `model.py`, `inputs/gen.py`, `README.md`, `c/kernel.c`,
`c/kernel.h`, `c/kernel_hardened.c`, `c/main.c`, `c/emalloc_shim.h` and more.
✅ **Measured: 118 `.temp/` citations across 35 hashed files it had never
opened** — 34 row-specific, 84 inherited through shared files, 1 already gone.

⭐⭐ **THE INSTANCE THAT MAKES THIS A FINDING RATHER THAN A GAP.**
`patterns-php/ph53-iface-tail-uninit/verus.rs:24` and `:350` cite
`.temp/php41/probe_wrap.rs` — and the comment at `citecheck.py:139`, which
exists to explain why the `spec.md`/`NOTES.md` scan was added, **names that
exact citation**: *"`_041` … repaired two of the THREE places it had written
it — `verus.obligations_note` survived."* ▶ **The repair for `F99` did not
cover `F99`'s own leftover, because the leftover was in a file the repair did
not think to look at.**

⛔⛔ **AND IT HAPPENED TWICE, BY THE SAME MECHANISM, IN THE CHECKER THAT EXISTS
TO CATCH IT.** The `spec.md`/`NOTES.md` layer was added because `_041` wrote a
path into `ph53`'s contract; the `controls/*` layer was added because `_044`
found one in `ph53/controls/spellings.py`. **Each repair was scoped to the file
class the instance happened to touch** — `F147` stated as a general mechanism,
now demonstrated inside `F147`'s own subject matter. ⚠ **`F147` said four
instruments in eight days; this is a fifth datum and it is the strongest,
because here the scoping is visible in the source comment.**

✅ **REPAIRED, AND THE REPAIR IS THE SHAPE, NOT THE ROLE.** `hashed_sources()`
derives the scan set from `source_sha256` in the gate records, so the checker
**cannot again be narrower than the thing it certifies**. `N7c` asserts the
derivation (a literal list fails it), `N7a` that `verus.rs` is reached, `N7d`
that no file is reported by two layers (`F131`), `N7e` that the inherited split
does work, `N7f` that the layer cannot move the exit code. ⓘ **Free** —
`.tasks-php/*.py` is in no digest; exit code unchanged at `1`.

⚠⚠ **WHAT THIS IS NOT: 118 DEFECTS.** Most are provenance notes in comments
(*"measured at `.temp/php13/02-reach.log`"*), the same benign class as the 32
historical `controls/*` citations. ▶ **The finding is the COVERAGE.** The 34
row-specific ones are open item **152** and cost a RE-GATE each, so they batch
with their row's next task — `citecheck.py`'s own standing rule for `controls/*`.

⭐ **THE GENERAL RULE, and it is worth more than the repair: when a checker and
the artefact it certifies both define a set, the checker must not define its
own.** `F114`'s lesson — *the right definition was already written down in the
repo and the tool used a different one* — and the **fourth** measurement tool in
this programme to be wrong that way.

### F150 — ⛔⛔ ITEM 148 ADJUDICATED: **17 OF 27** LAW-11 CITATIONS ARE DEFECTS OVER **14 FILES AND 13 FINDINGS**, THE CHANNEL IS A MAJORITY AND NOT THE EXPECTED MINORITY — AND **11 OF THE 13 FINDINGS HAVE NEVER BEEN REVIEWED**, SO THE GITIGNORED PROBE IS THE ONLY EVIDENCE THAT EXISTS ANYWHERE

Manager, ⛔ **UNREVIEWED** (rule 9). ▶ **Run it, do not quote this row**:
`python3 .tasks-php/probes/scratchdeps.py` prints the ruling.

**THE METHOD WAS ITEM 125's AND IT COST ABOUT WHAT THE ROW SAID** (~25 min):
the census already existed, so each member needed one read **against its citing
sentence**. ⛔ **The verdicts are in the tool, not in this paragraph** — a table
keyed on `(finding, cited file)` in `scratchdeps.py`, each row carrying its
reason in the citing sentence's own terms.

| verdict | citations | files | findings | what it means |
|---|---:|---:|---:|---|
| **`RESTS`** | **17** | **14** | **13** | the published number IS the gitignored file's output — ▶ **law-11 defect** |
| `HISTORY` | 6 | 4 | 4 | the file is the **subject** of the sentence (a retracted probe being named), and the claim is stated in full where it is made |
| `NOTDEP` | 4 | 1 | 3 | not a dependency at all |

⚠⚠ **THE ROW SAID *"EXPECT A MINORITY"* AND IT IS A MAJORITY — 63 %.** `F21`/`F37`
say report a dead channel plainly; the same duty runs the other way, and this
one is live. ⚠ Nothing has been lost yet — all 17 targets resolve today — so the
exposure is real and the loss is still hypothetical.

⛔⛔⛔ **AND THE SEVERITY SENTENCE THAT STOOD HERE WAS WRONG. IT READ *"only
`F89` and `F95` have been independently reviewed … for 11 of 13 there is no
second method anywhere."* REPLACED, NOT ANNOTATED** (item 73). Caught by
`TASK_PHP_064`'s engineer. **Re-read from each finding's own verdict block:**

| status | findings | n |
|---|---|---:|
| ✅ **REVIEWED** | `F89` `F95` `F100` (all `_043`) · `F102` (`_047`, `UPHELD-NARROWED`) | **4** |
| ⛔ **UNREVIEWED**, marked in the section | `F72` `F74` `F85` `F90` | **4** |
| ⚠ **NO MARKER AT ALL** | `F44` `F50` `F53` `F70` `F73` | **5** |

▶ ***"No marker" is not "unreviewed" — it is UNKNOWN, and that is its own
finding.*** The honest statement is **4 of 13 reviewed, 4 explicitly not, and 5
whose review status the tree does not record.**

⛔⛔ **HOW I GOT IT WRONG, AND IT IS THE SESSION'S OWN LESSON FIRING ON ME.** I
counted with a regex — `REVIEWED AT (\S+ \S+) — ([A-Z-]+)` — over prose. `F100`'s
heading spells it `REVIEWED AT \`TASK_PHP_043\` — **UPHELD-NARROWED.` with the
verdict in markdown bold, so the character class missed it. **`F148` is *"a
`grep -c` over hard-wrapped prose fails in BOTH directions"*, and I published a
count off exactly that instrument in the session that filed it.**

⛔⛔⛔ **AND THE REAL DEFECT IS DEEPER: THE PROGRAMME'S HOME FOR THIS FACT CANNOT
ANSWER THE QUESTION.** `boxcheck.rule9_rows` parses **44 rows and NONE of these
13** — because the RULE-9 block has **two formats**, one finding per row from
`F107` on, and a grouped cell (`F97 · F102 · F104`) for the `_047` era. ▶ **So
review status for pre-`F107` findings is not derivable at all**, and `F102`'s
own section still says `⚠ UNREVIEWED` while the `_047` block files it under
`UPHELD-NARROWED`. **Two homes for one fact, disagreeing** (`F131`), on the
process state that governs what may enter the authoritative layer. → item **154**.

⭐⭐ **THE MECHANISM, AND IT IS NOT CARELESSNESS — IT IS THE RULE BEING OBEYED
TO THE LETTER.** `CLAUDE.md` Don't #1 says **keep the generator, delete the
artefact** — and it **never says WHERE**, while `.temp/` is gitignored. ▶ **So
obeying it precisely still produces a law-11 defect.** That is why the class
recurs under authors following the rules rather than ignoring them.

⚠⚠ **I FIRST ILLUSTRATED THAT WITH `F102`'s *"generator kept, binaries deleted"*
AND `F102` IS THE WRONG EXHIBIT — ITS AUTHOR HAD ALREADY DONE THE WHOLE JOB.**
The generator was promoted on 2026-09-13 as `.tasks-php/asan_fill_byte.c`; only
the citation was never repointed. ⛔ **I picked the exhibit for how well it read
and it was the one case that refutes it.** ▶ The lesson stands on the *other*
thirteen, where the generator genuinely had no committed home — and the example
to quote is **`F50`'s `REFETCH.sh`**, a regenerator named in a finding's own
sentence that could not regenerate anything from a clean checkout.

⭐ **THREE OF THE 27 ARE FALSE POSITIVES OF MY OWN CENSUS, AND THEY ARE RULED
`NOTDEP` RATHER THAN QUIETLY DROPPED.** At `F59` and `F69` the token
`streamsfuncs.c` is a **PHP 5.0.0 source file in a column heading and in a list
of the five files `ph73` spans** — not a citation of the scratch copy at all.
The bare-name resolver, added on 2026-09-17 because the *previous* arm could not
see bare filenames, over-matched in the other direction. ▶ **A census row is a
QUESTION, and *no* is one of its answers** (`F132`) — which is why the ruling
keeps all three verdicts and `N23` fails if any verdict falls out of use.

⛔⛔ **THE KEY IS `(finding, file)` AND NOT THE FILE, AND `N22` PINS WHY.** The
same `.temp/mgr166/asan_reach.c` rules **`RESTS` under `F50`** — it is the
instrument behind the published bytes × ASan × canary table and the *"cliff is
at 32 bytes"* claim — and **`HISTORY` under `F52`**, where it is one row of a
table about probes whose setup encoded their answer. **A ruling filed against
the file would be wrong for one of the two.** `F131`'s one-home rule is about
the FACT, and the fact here is the citation, not the path.

⚠ **THE ARM IS COVERAGE, NOT CARDINALITY, AND THAT IS DELIBERATE.** An arm
asserting *"17 `RESTS`"* goes red the day the promotions land — **the day the
work is done** (`F147`'s sibling lesson, the trap this same file already dodged
in `_section_of`). `N20` instead asserts that **every** law-11 citation has a
ruling, so a new one written into a finding tomorrow is caught by nobody having
read it. `N19` proves that on planted rows, so the arm does not depend on the
live backlog being empty.

▶ **THE REMEDY IS OPEN ITEM 153** — promote the 14, `PROMOTE_001`'s method,
which discharged 6 files in one task. ⛔ **`F85` first**: it is *"the
programme's central claim"* and both of its named probes are still in scratch.

### F149 — ⛔⛔⛔ THE FIRST `O0` SWEEP THIS PROGRAMME HAS EVER RUN SAYS **ONE OF `ph66`'s FOUR `O0` FAMILY-B FIGURES IS SIGN-UNSTABLE** — SO THE SIGN ITEM 146 WANTED TO PUBLISH IS NOT THERE, AND A 4-PAD SCREEN GOT THAT CELL EXACTLY BACKWARDS

Manager, **UNREVIEWED** (rule 9). Instrument:
`.tasks-php/php50_align_sweep.py --opt O0` (new; 5 §H arms, `OPT-1..4`
additive-change and `OPT-5` tied to a committed number).

**WHAT `--opt` WAS FOR.** `_063` §3.4 traced a loop nobody intended:
`PROTOCOL_PHP.md` §B5 requires a figure to clear a **sweep** before
publication; `php50_align_sweep.py:86` hard-coded `OPT = "O3"`, so **nothing
was ever swept at `O0`**; therefore no `O0` reading could clear §B5; therefore
its **sign** could never be certified and could not be published **even as a
sign**. ⭐ `ph66`'s own `NOTES.md:530` states the hard-coding as its reason for
publishing no `O0` sign — **the loop, written down, by the row it trapped.**
▶ `--opt` breaks it. ⛔⛔ **MAGNITUDES STAY FORBIDDEN**;
`.memory-php/03-numbers.md` is untouched.

---

✅ **FIRST, THE CONTROL: ALL FOUR PUBLISHED NUMBERS REPRODUCE EXACTLY.**
`ph66` `NOTES.md` §9.4 and `TASK_PHP_062_REPORT.md:172` publish the `O0`
family-B `R1h − R1` differences as `+4.00`/`+6.12` (gcc small/large) and
`+5.00`/`+9.69` (clang). The sweep returns **`4.00`, `6.12`, `5.00`, `9.69`** —
at 4 pads *and* at 32. ▶ **`OPT-5` is pinned to those published values rather
than to whatever the tool prints**, which is what makes everything below a
result and not a re-labelling.

⛔⛔⛔ **AND NOW THE PART THE ROW COULD NOT HAVE KNOWN. THE CERTIFIED 32-PAD
SWEEP** (`--opt O0 --row ph66-hashdel-uncompared --pads 32`, a full 32-residue
period, `isolated`):

| input | pair | median | range (step) | \|d\|/step | **magnitude** | **sign** |
|---|---|---|---|---|---|---|
| `small` | gcc | `+4.00` | `0.00` | n/a | ✅ **RESOLVABLE** | ✅ SIGN-STABLE |
| `small` | clang | `+5.00` | `1.89` | `2.65` | ⛔ NOT RESOLVABLE | ✅ SIGN-STABLE |
| `large` | clang | `+9.69` | `4.56` | `2.12` | ⛔ NOT RESOLVABLE | ✅ SIGN-STABLE |
| **`large`** | **gcc** | `+6.12` | **`8.89`** | **`0.69`** | ⛔ NOT RESOLVABLE | ⛔⛔⛔ **SIGN-UNSTABLE** |

▶ **ONE of the four is a quotable magnitude. THREE of the four have a
publishable sign. THE FOURTH HAS NEITHER.** On `large`/gcc the alignment step
is **`8.89` Ir/call and the effect is `6.12`** — ⭐ **the difference is SMALLER
THAN THE STEP**, so at some pad values `R1h` is *cheaper*, not dearer.

⚠⚠ **SO `ph66`'s SUMMARY SENTENCE IS OVER-STATED.** `NOTES.md:345-346` reads
*"gcc `+4.00` (`small`) and `+6.12` (`large`); clang `+5.00` and `+9.69`. **The
extra conjunct costs at `O0`.**"* — a claim over all four cells. ✅ It holds on
three. ⛔ **On `large`/gcc it is NOT ESTABLISHED**, and no reading of that cell
can establish it until the effect exceeds the step. ⓘ **The row is not being
accused of over-claiming a performance figure**: it labels the `O0` rows
*"LOWERING READINGS AND NOT PERFORMANCE CLAIMS"* in capitals, which was correct
under the rule as it stood. **The defect is in the SUMMARY, and it is one the
row was structurally unable to detect.**

⭐⭐⭐ **(b) AND THE SHARPEST PART: A 4-PAD SCREEN GOT THAT CELL EXACTLY
BACKWARDS.** The same sweep at `--pads 4` (residues 0/8/16/24) reports
`large`/gcc as **`RESOLVABLE` / `SIGN-STABLE`, range `0.00`** — the opposite
verdict on both axes. The reason is visible in the raw table: at all four
sampled pads **both cells move together**, so the *difference* never varies;
they diverge only at residues the screen never visits. ▶ **THAT IS THE TOOL'S
OWN DOCUMENTED WARNING — *"a two-pad screen is complete for a CELL and NOT for
a DIFFERENCE… two cells with unknown, unequal phases can have an arc this sweep
never samples"* — CONFIRMED ON LIVE DATA FOR THE FIRST TIME.** ⛔⛔ Until today
that warning was an argument; it is now a measurement, and it says a sparse
screen can return `SIGN-STABLE` for a pair whose sign is not stable. ⚠ **Every
`|d|/step = n/a` in a sparse run means *this screen saw no step*, which is not
*there is no step*.**

⚠ **(c) WHAT THIS DOES NOT SAY.** It does **not** refute `F136`, `F143` or
anything at `O3` — the `O3` sweep is unchanged and was always run at 32 pads.
It does **not** say `O0` figures may now be published as performance numbers;
`.memory-php/03-numbers.md` stands. And it does **not** settle whether the
other twelve rows have sign-unstable `O0` cells — **nobody has looked, because
until today nobody could.** ▶ That is open item 151.

⛔ **(d) THE REPAIR COSTS A RE-GATE AND IS THEREFORE NOT DONE HERE.**
`patterns-php/ph66-hashdel-uncompared/NOTES.md` is in the gate record's
`source_sha256` (verified: `19b8d3fa72be0dba…`), so correcting its summary
sentence invalidates `results-php/gate/ph66-hashdel-uncompared.json`. ▶ **Batch
it with `ph66`'s next task** — the practice items 36 and 39(c) already set for
this exact class. **Open item 151 carries it.**

### F148 — ⚠⚠⚠ A `grep -c` OVER HARD-WRAPPED PROSE FAILS IN **BOTH** DIRECTIONS, AND I HIT BOTH IN ONE SESSION WHILE READING THE NOTE THAT WARNS ABOUT THE FIRST

Manager, **UNREVIEWED** (rule 9). No probe — the evidence is the session's own
commands and is reproducible by re-running them.

**THE UNDERLYING LESSON WAS WRITTEN ON 2026-09-12 AND HAS NEVER BEEN
COMMITTED.** `NULLCTL_001.md` §10 (promoted from `.temp/mgr172/NOTES.md` under
`F147`) records it: I told `TASK_PHP_037` its F72 hedge was **absent**, citing
`grep -a -c 'DO NOT QUOTE IT AS A RESULT' … → 0`. **The hedge was there.** The
phrase **wrapped across a line break**, and `grep` matches within a line, so it
returns 0 whether the text is present or not — ▶ **the check could not
distinguish presence from absence, and I read it as absence.** ⭐ The agent
caught it, not me. `grep -ar "wraps across a line break" --include=*.md .`
returns **0 files**: the lesson exists nowhere in the committed tree.

⛔ **(a) FALSE ABSENCE — THE WRAP, REPRODUCED TODAY.** Testing whether
`NULLCTL_001.md` §5's routing note was already published, I ran
`grep -aci "harness/check.py HAS THE SAME UNCHECKED PREMISE" RECAP_PHP.md` →
**0**, and wrote it down as absent. `grep -arl "SAME UNCHECKED PREMISE"` then
returned **`RECAP_PHP.md`**. ▶ **Same file, same session, opposite answers,
because the first pattern was nine words in prose hard-wrapped at ~76 columns.**

⛔⛔ **(b) FALSE PRESENCE — THE HOMONYM, WHICH §10's OWN PRESCRIPTION DOES NOT
COVER.** §10 prescribes *"match a short unwrappable token, or read the
section."* I did exactly that: `grep -ac "coin flip" RECAP_PHP.md` → **1**, and
concluded §10's grep lesson was already published. **Reading the line showed it
is about whether a missing benchmark number's DIRECTION is a coin flip — an
unrelated use of a common phrase.** ▶ **A token short enough never to wrap is
short enough to collide.** ⚠ **The two failure modes push in OPPOSITE
directions, so there is no safe length**: long prose under-reports, short prose
over-reports.

✅ **(c) WHAT ACTUALLY WORKS, AND IT IS A CLASS, NOT A LENGTH: AN IDENTIFIER.**
A symbol, a filename, a hash, a number — **unwrappable because it has no spaces,
and unique because nobody writes it by accident.** Measured in the same session:
`grep -ac "shout_section" RECAP_PHP.md` → **1**, which correctly found §10's
*other* half **published** after my phrase test had implied the whole section
was not; and `ptr_as_i32` → **0**, correctly absent. ▶ **Of the four probes I
went on to VERIFY BY READING the matched line, the two IDENTIFIER probes were
both right and the two PROSE probes were both wrong.** ⚠ **n = 4, and it is
stated as n = 4** — the other six probes in that session were never checked
against the text, so they are not evidence for anything. **The mechanism is the
argument here; the count is only an illustration of it.**

▶ **THE RULE, replacing §10's:** ⛔ **never grep prose to decide presence.**
Grep an **identifier** the claim must contain, or **read the section**. If the
claim contains no identifier, that is itself the finding — **a claim with no
greppable token cannot be checked mechanically and must be read.**

⚠ **SCOPE, and it is narrow on purpose.** This says nothing about `grep` for
*locating* text, which is what it is for and what it does well — every census in
`F147` greps, and each one greps a **path or a filename**. It is specifically
about **asserting an ABSENCE, or confirming a PRESENCE, from a count over
prose.** `F35`'s family at a third joint: **the tool answered a narrower
question than the one I asked it, and the output looks identical either way.**

⚠⚠ **AND THE REASON THIS IS A FINDING RATHER THAN A NOTE:** the defect is
invisible in review. `grep -c … → 0` pasted into a report reads as a
measurement, carries a command anyone can re-run, and **re-running it reproduces
the wrong answer.** ▶ `law 6` says *a figure a validator asserts is computed
from the tree, or it is not asserted* — **this is a figure computed from the
tree that is still wrong**, because the computation answers a different
question. ⭐ **A reproducible number is not a correct one.**

### F147 — ⛔⛔⛔ FOUR INSTRUMENTS HAVE BEEN BUILT FOR THE SCRATCH-DEPENDENCY CLASS IN EIGHT DAYS, **EACH ONE SCOPED TO THE INSTANCE THAT PROMPTED IT**, AND EACH NEXT INSTANCE WAS FOUND OUTSIDE THE LAST ONE'S SCOPE — LAW 11's OWN SCOPE CLAUSE CAPTURES **5 OF 22**

Manager, **UNREVIEWED** (rule 9). Probe:
`.tasks-php/probes/scratchdeps.py` (`--selftest` **PASS, 12 must-fire
negatives**). Read-only; re-derives from the working tree and `git ls-files`.

⚠⚠ **THE FINDING IS THE MECHANISM, NOT THE COUNT.** Every time this class was
rediscovered, someone (twice me) built an instrument, and **generalised it to
the neighbourhood of the instance in front of them**:

| # | date | prompted by | instrument | scoped to | what it captures |
|---|---|---|---|---|---|
| 1 | **2026-09-09** | `F51` — *"the catalogue's coverage claim rested on a script the repo does not carry"* | `citecheck.py` (`ceb40b5`) | the CLAIM layer; ⛔ **excludes `RECAP_PHP.md`** by a reasoned premise | `.temp/` **paths**; no tracked-twin test |
| 2 | **2026-09-13** | `F99` / item 86, promoting `width.py` | `.memory-php/04-process.md` **law 11** | *"every probe behind every finding in **F88–F101**"* | ⛔ **5 of the 22 findings that have the shape — 23 %** |
| 3 | **2026-09-17** | `_063` §7.2 | `boxcheck.py`'s `mem_temp` arm (`604b51a`, **mine**) | `.memory-php/` only | **printed 4 — and 1 of the 4 is a false positive** |
| 4 | **2026-09-17** | this finding | `probes/scratchdeps.py` | + `RECAP_PHP.md`'s finding sections · + **bare-filename** spelling · + tracked-twin resolution | **54 LIVE / 12 AMBIGUOUS / 6 STALE** |

⚠ **ROW 4 IS NOT EXEMPT AND I AM NOT CLAIMING IT IS COMPLETE.** Its known
blind spots are written into its own docstring: it cannot tell a probe I wrote
from upstream source I extracted, it resolves by basename, and it scans two
document families. **The pattern above predicts row 5.**

---

**THE SET, MEASURED — AS A READING TAKEN AT `604b51a`, BEFORE THIS FINDING WAS
WRITTEN.** Over `RECAP_PHP.md` + the five `.memory-php/*.md`:
**94** `.temp/` citations → **54 LIVE** (no tracked file of that basename) ·
**12 AMBIGUOUS** (all `NOTES.md`, across 7 scratch dirs — see (c)) · **6 STALE**
(a tracked twin exists, so the citation points into scratch for a probe that is
committed) · **22 not a dependency** (a re-derivable artefact, or the bare
`.temp/` that is how the RULE itself is spelled).

**22 PUBLISHED FINDINGS CITE A SCRATCH FILE INSIDE THEIR OWN `### F<N>`
SECTION** — F44, F50, F51, F52, F53, F59, F69, F70, F72, F73, F74, F82, F83,
F84, F85, F86, F89, F90, F95, F99, F100, F102 — over **34** citations and
**23** distinct files, all of them in `RECAP_PHP.md`. ⓘ **These four numbers are
what `probes/scratchdeps.py` PRINTS** (its `law 11` block), not a transcription:
an earlier draft of this finding said *"32"* from a one-off script, and the
figure was re-derived from the committed tool before it was published — `law 6`.

✅ **AND THE READING THAT KEEPS THIS HONEST, AS AN EVENT: at `604b51a`,
2026-09-17, ALL 29 TARGETS STILL EXIST — 0 GONE.** ▶ **Nothing has been lost;
the exposure is real and the loss is hypothetical**, and a finding that blurred
those two would be the over-claim `F108` exists to stop. ⚠⚠ **A READING WITH A
DATE, NOT A PROPERTY**: `.temp/` is auto-`rm`-able, `CLAUDE.md` constraint 6
*mandates* deleting its blobs once gates are green, and `citecheck.py` already
reports **4** `controls/*` citations whose targets **are** gone. ▶ **Re-run it;
do not quote the 0.**

---

⛔⛔ **AND THESE FOUR NUMBERS WENT STALE THE MOMENT THIS FINDING LANDED, BY ITS
OWN HAND — WHICH IS THE POINT, NOT AN EMBARRASSMENT.** Publishing `F147` and
`F148` moved the census to **58 LIVE / 14 AMBIGUOUS / 8 STALE of 108**, and
every one of the ten added citations is **inside `F147` or `F148` or items
148/149** — measured, not guessed: `F147` contributes 5 LIVE, 3 AMBIGUOUS and 2
STALE, `F148` one AMBIGUOUS, the two item rows eight. ▶ **They are the
illustrative class, and a reader ruling on them should rule *correct as
written*.** ⭐ **`F147` NOW APPEARS IN ITS OWN `law 11` LIST — 23 findings, not
22 — because the finding that defines the population is inside it.** ✅ **The
adjudication is *correct as written*: `F147` cites scratch as ILLUSTRATION, and
its EVIDENCE is `.tasks-php/probes/scratchdeps.py`, committed and swept.**
▶ **Which is the distinction item 148 exists to make, demonstrated on the first
member anyone will look at.**

⭐⭐⭐ **AND A THIRD READING, WHICH EXPOSES THE TOOL'S OWN SEMANTICS: THE CENSUS
IS A FUNCTION OF `git ls-files`, SO IT MOVES WHEN YOU *COMMIT*, NOT WHEN YOU
WRITE.** Both readings above were taken with the six promoted probes **present
on disk but UNTRACKED**. At `805529b`, the commit that tracked them, the same
command reads **40 LIVE / 14 AMBIGUOUS / 13 STALE of 95** — **19 citations
discharged**, and the LIVE→STALE shift is citations still spelling `.temp/…`
for a probe that is now committed. ▶ **That is deliberate and it is the right
predicate**: the question law 11 asks is *what survives a CLEAN CHECKOUT*, and
only git knows. ⚠⚠ **It also means the two readings above describe a state that
no longer exists and cannot be reproduced** — ⛔ **so the figures in this finding
are HISTORY THREE TIMES OVER, and the only correct way to cite this class is to
run `python3 .tasks-php/probes/scratchdeps.py` and name the commit.** ⚠⚠ **SO DO NOT QUOTE 54/12/6 OR 58/14/8. RUN THE TOOL.** A finding
whose subject is *"an instrument's cardinality was consumed as a set"* has no
business shipping a cardinality that reads as current — ⭐ **and dating it is
necessary and not sufficient: the LABEL has to be historical too** (`F126`'s
lesson, the one a date alone did not save).

⛔ **(a) MY ARM WAS A STRICT DUPLICATE OF A REPORT THAT ALREADY EXISTED, EIGHT
DAYS OLDER.** `citecheck.py` has scanned `.memory-php/*.md` for `.temp/`
citations **since its first commit**, and prints the same three paths under *"a
committed claim should rest on a committed generator"*. I built the second home
**as the remedy produced by a round whose own findings are about facts having
two homes** (`F131`). ▶ The repair is not a third tool: **one census, imported
by whoever displays it** — the `rule9_mustfire.py` → `bc.ROUTE` shape.

⛔⛔ **(b) THE CELEBRATED "FOURTH" IS THE ONE ENTRY IN THE SET THAT IS NOT A
DEPENDENCY AT ALL.** `_063` §9 item 2 reads *"THE THREE LIVE `.temp/`
DEPENDENCIES IN `.memory-php/02-ladder.md` (`:447`, `:451`, `:612`)"* — **scoped
to one file, named member by member, correct on every one.** My arm printed
**4** because it also scanned `04-process.md`. **The fourth is
`04-process.md:165 → .temp/php39/width.py`, and that probe was promoted to
`.tasks-php/width.py` on 2026-09-13 — four days before the arm ran.**

⛔⛔⛔ **AND THE PART THAT IS WORSE THAN THE ARITHMETIC: I BOOKED MY OWN FALSE
POSITIVE AGAINST THE REVIEWER.** I wrote *"the arm found a FOURTH `_063`'s count
missed"* into the START HERE box, **under the line saying the reviewer's order
binds me** (`F123`). The reviewer did not miss a fourth; the reviewer bounded a
different set and said which. ▶ **Two counts over overlapping sets disagreed,
and I read the disagreement as a discovery instead of asking which set each was
over** — `F132`, broken in the act of scheduling the work `F132` exists to make
possible. ⚠⚠ **AN ARM THAT PRINTS BEATS A PROSE BOX ON RECALL AND SAYS NOTHING
WHATEVER ABOUT PRECISION, and I published the recall win as if it settled
both** — `_063` §6.3's experiment over-read by the person who ran it.

⛔⛔⛔ **(c) A BARE FILENAME IS INVISIBLE TO EVERY VALIDATOR, AND THAT IS THE
SPELLING F82–F86's EVIDENCE USES.** Both tools match `` `.temp/<path>` ``.
`.memory-php/02-ladder.md:448` and `:612-613` cite their probes as *"probe
`identity_null.py`"* and *"probes `identity_null.py` · `inclusive_ir.py` ·
`bc_sweep.py` · `flip_exact.py`"* — **no path, therefore no match, therefore
five citations naming four probes behind five published findings counted as
zero.** ▶ **A CITATION'S SPELLING IS NOT A PROPERTY OF THE THING CITED**, and an
arm keyed to one spelling measures the spelling.

⛔⛔⛔ **(c′) AND THE FIFTH INSTANCE OF THIS CLASS IS IN THE FIRST DRAFT OF THIS
FINDING, WHERE THE CORRECT ANSWER WAS ALREADY PRINTED TWENTY LINES ABOVE IT.**
The brief I wrote for the promotion said the probes carry *"six published
findings — **F82–F87**"*. **`F87` is evidenced by none of them**: its tokens
`get_unchecked` and `a1_spread_pp` appear in zero of the six files, and its own
section cites `TASK_PHP_037` and `results-php/gate/ph45-….json` — **all
committed, so F87's law-11 debt was discharged before this task existed.**
▶ **I read the range off `02-ladder.md:612`'s citation line — *"`RECAP_PHP.md`
F83–F87, …, probes X · Y · Z"* — and took the RANGE for the MEMBERSHIP. A
citation line naming a range and a probe list does not assert that every member
of the range rests on every probe.**
⭐⭐⭐ **AND THE CENSUS IN THIS VERY DOCUMENT HAD IT RIGHT: the measured list
above runs *… F82, F83, F84, F85, F86, F89 …* — `F87` IS NOT IN IT.** The tool
printed the correct set, the prose beside it asserted a range, **and I published
the prose.** ▶ `law 6`'s defect in its purest form: **a figure was computed from
the tree and then not used.** ⓘ Caught by the promotion engineer, not by me. ⚠ The same regex blindness runs
the other way into `AMBIGUOUS`: **50 tracked files are called `NOTES.md`**, so a
basename resolver would report `.temp/mgr172/NOTES.md` — the evidence record
behind F82–F86 — as *already promoted*. **Three outcomes, not two, and the third
is printed rather than guessed.**

⛔⛔ **(c″) AND THE SAME MECHANISM FIRED AGAIN, IN A DIFFERENT TOOL, THE SAME
DAY — SO IT IS `n = 2` AND NOT AN ANECDOTE.** Writing item 150 above, I spelled
its route *"▶ **The question **for a reviewer**, and I should not settle it
myself**"*. `boxcheck.py`'s `ROUTE` returned **nothing**: its alternation
enumerates *"is a REVIEWER"*, *"a REVIEWER's"*, *"Give it to a reviewer"* … and
**not** *"for a reviewer"*. ▶ **`F140`'s defect recurring inside `F140`'s own
remedy**, and structurally identical to (c): **A REGEX KEYED TO AN ENUMERATED
SPELLING MEASURES THE SPELLING, NOT THE PROPERTY.** ✅ Widened, with two arms —
`909` for the missed spelling, `910` for the false positive the widening must
not buy. ⛔⛔ **BUT ADDING A SPELLING IS NOT THE FIX AND THE CODE NOW SAYS SO:
every addition is evidence the enumeration cannot be completed by thinking
harder. The durable answer is a ROUTING TOKEN AN AUTHOR MUST TYPE, not a phrase
a reader must guess** — unsettled, deliberately. ⚠ **And the other repair was
refused**: rewording item 150 to suit the regex is *silencing a checker by
editing its input*, which this tree already calls the opposite of the ratchet.

⚠⚠ **(d) `citecheck.py`'s EXCLUSION OF `RECAP_PHP.md` IS REASONED, HALF TRUE,
AND WRONG AT THE WRONG GRANULARITY — SO THE REPAIR NARROWS IT, NOT REVERSES
IT.** Its comment gives the reason: the handoff *"cites the manager's current
scratch on purpose as provenance for work in flight… not a committed claim
resting on deletable evidence, which is the thing being hunted."* Measured over
its 48 LIVE citations: **14 sit in the open-items table**, where that premise is
**exactly right**, and **32 sit inside `### F<N>` finding sections**, where it is
false — F82's evidence line has been a published, cited, five-day-old finding.
▶ **A SECTION-LEVEL PROPERTY IMPLEMENTED AS A FILE-LEVEL EXCLUSION.** Scan the
finding sections; keep excluding the items table. ⭐ **The half that is right is
why this is a narrowing: the exclusion bought something real and was priced at
the wrong unit.**

⚠⚠ **(e) LAW 11's OWN EXAMPLE IS STALE IN THREE WAYS AND ITS PRESCRIBED FIX WAS
ALREADY PERFORMED.** It says F92's measurement *"lives in `.temp/php39/width.py`
— **gitignored**, and its `--selftest` **no longer completes**"*, and *"▶ **The
fix is the one F99 prescribes: commit the probe beside the other checkers.**"*
All three clauses are false today: the probe is `.tasks-php/width.py`, its
`--selftest` returns **0**, and that file's own header records the promotion and
the two `X3b` repairs, **dated 2026-09-13**. ▶ **The law's example is the law's
own remedy, applied and never recorded back — the fix has one home and the rule
has another** (`F131`) — and the tree's arm then reported the law's stale
example back to me as new work.

✅✅ **(e′) THE POSITIVE CONTROL, WHICH IS WHY (e) IS A REPAIRABLE SHAPE AND NOT
A COMPLAINT.** `RECAP_PHP.md:115` faced the identical situation — the rule-9
state had been living in gitignored `.temp/mgr175/NOTES.md` — and its repair
reads *"⛔⛔ **THIS BLOCK EXISTS BECAUSE THIS STATE WAS LIVING IN GITIGNORED
`.temp/mgr175/NOTES.md`** — which is **F99's own defect**…"*. ▶ **The fact moved
into the committed document and the citation stayed, re-spelled as THE REASON
THE BLOCK EXISTS.** That is the form law 11's example owes: not a deleted
pointer and not a live one — **a pointer whose tense says the work is done.**

⭐⭐ **(f) MEASURED, NOT ASSUMED: 2 OF THE 5 PROBES BEHIND F82–F86 CRASH ON A
CLEAN CHECKOUT RATHER THAN DEGRADE.** With `.temp/mgr172/cg/` moved aside,
`inclusive_ir.py --selftest` dies `TypeError: '>' not supported between
instances of 'NoneType' and 'NoneType'` and `bc_sweep.py --selftest` dies
`KeyError: 'small'`; the other three are unaffected because they read only
committed gate records. ▶ **That is law 11's prediction, TESTED for the first
time, with a mechanism — and it is stronger than the law states: the probe does
not merely go missing, it prints a Python traceback where a result should be.**
✅ Repaired on promotion: both now print *"⛔⛔ NOT RUN — NO VERDICT WAS REACHED.
THIS IS NOT A PASS"*, list every missing path, name the generators, and **exit
0**.

⛔⛔⛔ **(g) AND THE PRECEDENT I TOLD THE ENGINEER TO COPY IS ITSELF FALSE — ON
THE SAME FILE AS (e).** `.tasks-php/width.py`'s committed header says of its
cross-session check: *"`X3`/`X3b` … reports **"the check could not run, which is
itself a result to report"** **and does not fail**. ✅ So the selftest degrades
honestly rather than lying."* **It does fail.** With `.temp/mgr173/cg` moved
aside it prints `FAIL X3`, ends `SELFTEST FAIL ['X3']`, **rc=1** — because
`reuse_check` returns `("X3", False, …)` and `selftest`'s `check()` appends every
falsy `cond` to `fails`. ✅ **Verified statically at `width.py:1323` and
`:893-896`**, independently of the engineer's run.

⚠⚠ **THIS IS LIVE, NOT COSMETIC.** `width.py` is filed `st_expect=0`, and the
state that turns it red — an empty `.temp/mgr173/cg` — is the state
**`CLAUDE.md` Don't #1 actively INVITES** (*"blobs … get deleted once your gates
are green"*). ▶ **The routine sweep goes red for following the rules, and no
`why` says so.** ⭐ The engineer refused the instruction and made its guards
return 0, saying in capitals that nothing was checked — **the right call, and it
is why row 4's guards do not inherit the defect.**

▶ ⚠ **MY DECISION, RECORDED HERE BECAUSE IT IS A POLICY CALL AND NOT A REPAIR:
an unrunnable CROSS-SESSION check REPORTS AND RETURNS 0.** The tree already
argues this one directory over — `probes/ph66_djbx33a_collide.py`'s registry
entry says *"a checker that reddens when a sibling repo is cleaned is reporting
on that repo"* — and `X3` is the same shape. ⛔ **Not done here**: `width.py`
carries `F92`, and a validator change lands with its must-fire negatives or it
does not land (`§H`). **Open item 149.**

---

⚠⚠⚠ **WHAT THIS IS NOT, AND THE SENTENCE MATTERS MORE THAN THE TABLE.** `LIVE`
is a **CANDIDATE SET REQUIRING ADJUDICATION BY UNIT TEXT** (`F132`), **not a
defect count**, and this finding must not be quoted as *"54 defects"*. At least
one member is the rule being **FOLLOWED**: `.temp/php27/streamsfuncs.c` is
PHP 5.0.0 source extracted into scratch, re-derivable from
`patterns-php/php-5.0.0.manifest`, and committing it would be the error.
▶ **Adjudicating the remaining 23 is open item 148 and is NOT closed here.**

⛔⛔⛔ **AND THE CLASS IS NOW AT THREE, ALL MINE, INSIDE ONE WEEK.** `F138` —
*"I consumed its CARDINALITY and never printed its MEMBERS"* — is this defect on
the rule-9 backlog. `F142` — *"the arm bounds the pile's SIZE and the property
is about its MEMBERS"* — is this defect on the cost ledger's `PENDING` pile.
**`F147` is this defect on the arm I built four days later AS A REMEDY, and the
number I consumed without checking its members is the one I then wrote into the
START HERE box as the next session's instructions.** ▶ `F138`'s remedy was
*print the members*; **I printed four members and never asked whether the four
were the set.** ⚠ **PRINTING A MEMBERSHIP IS NOT ADJUDICATING ONE.**

### F146 — ⚠ **`A1` IS NEVER MEASURED AT `O0/large.bin` IN EITHER MEASUREMENT-RECORD CORPUS — `0 of 374` ISOLATED CELLS, BY ONE DELIBERATE LINE IN `harness/measure.py`. SO A ROW WANTING THE MATRIX AT TWO OPTIMISATION LEVELS GETS THAT CELL FROM A *ROW-LEVEL CONTROL*, AND `ph66`'s IS THE MODEL AND THE ONLY ONE**

> ⛔⛔ **RE-TITLED AT `_063`, AND THE ⭐⭐⭐ IS WITHDRAWN.** The title used to end
> *"…SO `_061`'s RULE ASKS FOR SOMETHING THE COMMITTED RECORDS CANNOT SUPPLY"*,
> and **that clause is refuted by `ph66`'s own committed control** — see below.
> ▶ **What is left is a note on how to obey a rule, which is exactly what the
> brief said would unearn the stars. Re-titled in place** (item 73), **not
> annotated beside.**

⚠ **Manager, 2026-09-16, found by RUNNING item 147's own *“one read of the
record's keys”* as a rule-14 premise before writing `_063` — not by reading
anything.**

Item 147 reported an unexplained `n/a` in every `O0/large` cell of `ph66`'s
`inside_share` matrix and conjectured *"the likely cause is a `large.bin` `A1`
the record does not carry at `O0`"*, flagging it **not confirmed**.
✅ **The conjecture is CONFIRMED. The SCOPE is the finding.**

Census of `kernel_exclusive_ir` over **every `isolated` cell of both corpora**:

| corpus | rows | `O0/small` | `O0/large` | `O3/small` | `O3/large` |
|---|---|---|---|---|---|
| `results/p*` — **PAT** | 34 | **263** ✅ | ⛔ **0 of 263** | **263** ✅ | **263** ✅ |
| `results-php/ph*` | 14 | **111** ✅ | ⛔ **0 of 111** | **111** ✅ | **111** ✅ |

⭐ **It is not a hole, it is a PLAN** — `harness/measure.py:50-61`, `CG_PLAN`:

> *"Callgrind is a ~50x slowdown, so its plan is explicit rather than
> exhaustive… `large` is added only at O3, **where the perf claims live**."*

⚠⚠ **THE SECOND CLAUSE — *"the php programme has falsified that justification by
its own practice"* — IS DECLINED, NOT REFUTED** (`_063` §3.2). The two instances
are real: `_061` §2.2 **refuted `F136`'s headline at `O0/isolated`**, and
**`F144` was caught precisely because `_062` looked at two levels.** ⛔ **But
`n = 2`, and item 123's own rule binds: *three instances is a rate and one is not
yet a design.*** ⭐ **And the question DISSOLVES anyway — nothing about `CG_PLAN`
needs to change, because the row-level control already supplies the cell.**
▶ **The live question is not *"is `CG_PLAN` wrong?"* but *"should a row-level
two-level matrix be REQUIRED?"* — and that is item 137.**

⛔⛔⛔ **THE CONSEQUENCE CLAUSE — *"`_061`'s rule cannot be discharged from
committed records"* — IS REFUTED, AND BY `ph66`'s OWN COMMITTED CONTROL**
(`_063` §3.2). ~~A row obeying it must run its own callgrind at `O0/large`,
which is exactly what `ph66`'s control did **not**.~~

`patterns-php/ph66-hashdel-uncompared/controls/inside_share.json` **carries `A1`
at `O0/large` on all 8 cells** (`c-gcc` `32428063`, `c-clang` `29004865`, …).
⭐⭐⭐ **The one row in either corpus whose committed artefacts hold the missing
cell is THE ROW THIS FINDING WAS WRITTEN ABOUT — and I had printed those exact
values in the session that filed it.** ⛔ **The fallback *"not for free"* is also
too strong**: `controls/inside_share.py` is committed, pinned and `--selftest`ed,
and it ran as part of the row's ordinary build.

✅ **WHAT SURVIVES, AND IT IS ALL OF IT:**

> *`CG_PLAN` omits `O0/large`, so a row that wants the matrix at two optimisation
> levels gets it from a **ROW-LEVEL CONTROL**, not from the measurement record.
> `ph66`'s `controls/inside_share.py` is the model, and the only one so far.*

▶ **That is a note on HOW TO OBEY the rule — the brief's own stated condition for
the ⭐⭐⭐ being unearned. It is withdrawn.**

⭐⭐ **THE TWO PROVENANCES SURVIVE AS A SEPARATE, SMALLER POINT** (item 147,
confirmed): `ph66`'s printed matrix takes `A1`/`W`/`share_W` from a **live**
callgrind and `share_F74` from the **committed** `results-php/<row>.json`, and
the blank falls on exactly the 8 cells `CG_PLAN` never wrote. ⛔ **A reader of
that one table cannot tell which column was measured today** — and `_063` rules
the fix is a **per-COLUMN** provenance label, not a per-file one.

⚠ **WHAT THIS IS NOT.** Not a `ph66` defect — the control faithfully reports a
hole it inherited. Not an argument for publishing `O0` magnitudes
(`.memory-php/03-numbers.md` forbids it; this finding does not touch that).
⛔⛔ **And NOT a proposal to edit `CG_PLAN`: `harness/measure.py` is hashed into
all 33 PAT measurement records, so changing it costs a full re-measure**
(`CLAUDE.md`, top). **This is a statement about what the records CONTAIN.**

ⓘ **It costs nothing to state, and item 146 is the second direction**:
`.tasks-php/php50_align_sweep.py:86` is `OPT, MODE = "O3", "isolated"`, so `O0`
is under-instrumented by **two independent hard-coded decisions**.

▶ **Commands**: the census is `_063` §0.1's `python3 -c`; the plan is
`sed -n '50,64p' harness/measure.py`; the sweep is one `grep -an '^OPT'`.

### F145 — ⭐⭐⭐ **`R5` CANNOT BOTH COMPUTE THE SAME FUNCTION AS `R1`–`R4` AND REFUSE THE DEFECT, SO THE LADDER'S OWN CROSS-RUNG IDENTITY REQUIREMENT IS WHAT STOPS THE PROOF RUNG FROM CATCHING A LOGIC BUG**

⚠ **Engineer, `TASK_PHP_062` §P3, 2026-09-16, scoring a prediction I registered
and refuting it *by its own stated falsifier*.**

`_062`'s **P3** predicted *"R5 is the only rung that can refuse it"*, falsifier
*"an R5 that verifies with the defective predicate in place."* ⛔ **The shipped
`verus.rs` is exactly that** — **49 verified, 0 errors, with `:464`'s disjunct
in the exec code.** It has to be: the shipped `ensures` is `r == hash_fold(...)`
and **`hash_fold` is a spec function that CARRIES the defect**, which is what
makes `R1`…`R5` comparable at all.

✅ **And the substance is confirmed separately**, `controls/key_identity.py`:

| arm | predicate | obligation | result |
|---|---|---|---|
| N1 | `b73349dbe4e9`'s | `NEW:container-key-identity` | **VERIFIES** |
| N2 | PHP 5.0.0's | same | ⛔ **FAILS — `postcondition not satisfied`** |
| N3 | PHP 5.0.0's | vacuous | **VERIFIES** |

⭐ **N3 is what makes N1-vs-N2 attributable to the PREDICATE and not the file.**

⭐⭐⭐ **THE FINDING IS THE TENSION, NOT THE SPLIT VERDICT.** Verus is not *the
rung that refuses the defect*; it is **the rung that can be ASKED**. `R2`, `R3`
and `R4` have nowhere to put the question. ▶ **But making `verus.rs` itself
refuse would mean stating its `ensures` against a *correct* delete rather than
against `hash_fold` — and then `R5` would no longer compute the same function as
`R1`–`R4`, so the cross-rung checksum would be comparing two different
programs.** ⛔ **The ladder's comparability requirement and the proof rung's
ability to catch a logic bug are in direct conflict, and this row is where it
shows.**

⚠ **Nothing resists at the Verus level** — the obligation is eleven tokens and
verifies by one recursive proof with no lemmas. **What resists is attaching it
to the shipped rung.**

▶ **WHY THIS IS A FINDING AND NOT A ROW NOTE**: it is a claim about the LADDER,
so it would enter `.memory-php/02-ladder.md`, and it re-frames what every `R5`
cell in the corpus has been measuring. ⓘ **The `R5` cells are not wrong** — a
memory-safety row's `ensures` and its correct behaviour coincide, so the tension
is invisible there. **`ph66` is the first row where they come apart.**

### F144 — ⭐⭐⭐ **WHAT DECIDES WHETHER `A1` RESOLVES A DIFFERENCE IS WHETHER *THE DIFFERENCE* LANDS INSIDE THE SYMBOL — NOT HOW MUCH OF THE CELL DOES. A 65 % `inside_share` DID NOT PREDICT A `+0.0000` AND COULD NOT.**

⚠ **Engineer, `TASK_PHP_062` §P4, 2026-09-16 — and it caught its own first
reading before publishing it.**

At `O3/isolated`, `c-clang`, `A1` reads **exactly `+0.0000`** between `R1` and
`R1h` while **family B moves `−2.03` and `−12.00 Ir/call`** on the same two
cells. The first write-up called that *"byte-identical kernels — a 0.00 that is
identity, not noise."* ⛔ **The `kernel` symbols ARE byte-identical; the programs
are not.**

⭐ **One `nm` line explains it**: **clang keeps `zend_hash_del_key_or_index`
OUT OF LINE** (`t zend_hash_del_key_or_index`, **0x3a5** bytes in `R1` against
**0x3a2** in `R1h`) **where gcc INLINES it** — so **the entire repair sits in a
symbol `A1` does not count.**

⭐⭐⭐ **AND THE SHARE WAS HEALTHY THE WHOLE TIME: `c-clang`'s `inside_share_W`
on those cells is `65.31 %` and `51.31 %`.** ▶ **A high share did not predict
the blindness and COULD NOT**, because the share measures *how much of the cell
is inside the symbol* and the question is *whether the DIFFERENCE is*.

⛔⛔ **THIS IS THE THIRD TIME A SHARE HAS BEEN ASKED TO CERTIFY `A1` AND THE
FIRST TIME THE MECHANISM HAS BEEN NAMED.** `F74`'s two-condition bar was refuted
as a gate (`_059`); `F125` measured `A1` reporting the **sign backwards** across
a symbol boundary when an implementation choice moved work into libc. ⭐ **`F125`'s
cause was a CHOICE A PERSON MAKES. This one is a CHOICE THE COMPILER MAKES** —
nobody wrote anything differently, and the two C columns disagree because
**gcc inlined and clang did not.** ▶ ***So the blindness is not something a row
can avoid by writing its kernel carefully.***

✅ **WHAT CAUGHT IT: `_062` §2.8's instruction to show the matrix at MORE THAN
ONE OPTIMISATION LEVEL** — the instruction `_061` added after `ph96`'s headline
was refuted for publishing `A1` at `O3` only. **The rule earned its cost on the
first row built after it.**

### F143 — ⭐⭐⭐ **THE FIRST ROW IN THE CORPUS THAT THE ENTIRE SAFETY STACK IS BLIND TO: `R1`(gcc), `R1`(clang), `R2`, `R3`, `R4` AND `R5` RETURN THE SAME `u64` ON ALL EIGHT INPUTS, ASan AND UBSan NEVER FIRE, AND MIRI REPORTS `ub: false`**

⚠ **Engineer, `TASK_PHP_062` §0/§P1/§P2, 2026-09-16 — the row's reason for
existing, and it came out as registered.**

| instrument | `ph66` | why |
|---|---|---|
| a CLI reproducer | ✅ **the wrong VALUE** | the survivor list differs; `rc=0` |
| **ASan / UBSan** | ⛔ **`fired: false` on every input, both C rungs** | every free is a *correct* free |
| **Miri** | ⛔ **`ub: false` on all eight** | the boolean is wrong; the memory is not |
| **safe Rust `R2`/`R3`** | ⛔ **byte-identical `u64` to C** | a wrong predicate is expressible in safe Rust |
| `R4`, `R5` | ⛔ **same `u64`** | see `F145` |

**Only `c/kernel_hardened.c` moves.**

⭐⭐⭐ **WHY THIS MATTERS MORE THAN ONE ROW.** Twelve of thirteen rows exhibit
their defect as a **signal**, so every instrument in the stack has something to
catch and the ladder's *"does the defect survive?"* column has always had a
non-trivial answer. **`ph66` is the control that shows the column can be
uniformly blank** — and `CLAUDE.md` rule 6 anticipated exactly this: *"safe Rust
reproduces the bug bit-identically"*, *"Miri doesn't see it"* and *"no column
moves"* are **ALL FINDINGS, NEVER KILLS**. ▶ **Six of ten historical temporal
refusals were made on these grounds. This row is what those six would have
produced.**

⚠⚠ **WHAT A REVIEWER SHOULD ATTACK.** The result is only as good as the
*faithfulness* of `R2`: a safe-Rust port that used a real `HashMap` would have
**deleted** the bug, and one that ports the bucket logic reproduces it. ▶ **The
engineer chose the faithful port and said so** — but *"the safety stack is
blind"* is then partly a statement about a **porting choice**, not only about
the defect. ⛔ **Is this finding about `ph66`, or about how `ph66` was ported?**
That is the question that decides whether it may enter `.memory-php/`.

### F142 — ⛔⛔⛔ **A COST CLASSIFICATION ENFORCED ONLY BY SOMEBODY REMEMBERING WENT STALE FOR ~20 TASKS AND UNDERSTATED THE PROGRAMME'S PUBLISHED PROJECTION — AND THE ARM THAT WATCHES THAT PILE COULD NOT SEE IT, BECAUSE IT BOUNDS THE PILE'S *SIZE* AND THE PROPERTY IS ABOUT ITS *MEMBERS***

⚠ **Manager, 2026-09-16, found by a validator firing on something else.**

`task_cost.py` classifies each task as `ONCE`, `METH`, `{row: weight}` or
**`PENDING`** — *"attributable to a row that is NOT YET BUILT"*. The block's own
comment states the hazard exactly: *"a growing PENDING pile makes the marginal
figure understate."*

⛔⛔ **`"040"` WAS THE R1h HUNT FOR `ph52` AND `ph53` PLUS ROW 7's BUILD BRIEF,
AND IT STAYED `PENDING` AFTER BOTH ROWS GATED** — from `_041`/`_042` to here,
roughly **twenty tasks**. It is also the entry the `PENDING` block cites as
*setting the precedent*. **The correction to the published figures:**

| | before | after |
|---|---|---|
| marginal | `2.42` | **`2.50`** |
| searched-only marginal | `2.38` | **`2.48`** |
| first-in-family (n=8) | `2.31` | **`2.38`** |
| follow-on (n=4) | `2.62` | **`2.75`** |
| **PUBLISH** | **`~61 .. ~77`, middle `~62`** | **`~63 .. ~79`, middle `~64`** |

⭐⭐⭐ **THE FINDING IS WHY `N8` DID NOT CATCH IT, AND IT IS `F132`'s CLASS ONE
LEVEL UP.** `N8` reads *"`PENDING` is at most a quarter of `ROW`"* — it bounds
the pile's **cardinality**, and the pile was tiny (1, then 2), so `N8` was green
throughout. ▶ ***The size of the pile was never the property. Its MEMBERSHIP
was*** — *is any member's row now built?* — and no arm asked. **`F132` said
*adjudicate the SET, by unit text, never the number*; this is the same
substitution made inside a validator, by the manager, two days after filing
`F132`.**

⚠⚠ **AND THE CONVENTION HAD NO MACHINE-READABLE HOOK AT ALL**: the row a
`PENDING` task was waiting on lived **in a Python comment**. So even an arm that
wanted to ask the question could not have. ▶ **Repaired at the data, not the
prose**: a `PENDING` entry now spells itself **`"PENDING:ph66"`**, and

- **`N8b`** re-derives, every run, whether any `PENDING` entry names a row that
  is already in the gated corpus — **failing if one does**;
- **`N8c`** refuses the bare `"PENDING"` spelling, **because a bare entry makes
  `N8b` silently vacuous** (`F135`'s class — a benign cause does not make a
  silent arm benign);
- **`N8d`** runs the same predicate over a **synthetic** ledger where the answer
  is known, so `N8b`'s silence means *nothing is wrong* and not *nothing was
  read* (item 131's shape, and `F140`'s own repair arm's shape).

⭐ **HOW IT SURFACED IS THE ARGUMENT FOR KEEPING ARMS CHEAP.** Writing row 13's
task file made `N1` fail — *"all 62 task files classified; unclassified=['062']"*
— which is an arm doing exactly its job on an unrelated question. **Filing `062`
is what put my eyes on the `PENDING` block.** ▶ *The defect was found by an arm
that was not looking for it, which is the only kind of luck a process can
manufacture.*

⛔ **WHAT THIS DOES NOT CLAIM.** It does not claim the projection was *wrong* in
any sense a reader was misled by — `~62` and `~64` are the same answer to one
significant figure, and the range has always been published as a range. ▶ **The
claim is about the MECHANISM**: a figure moved because a classification rotted
silently, and it would have kept rotting. ⚠ **A reviewer should ask whether the
`0.5/0.5` split I gave `"040"` across `ph52`/`ph53` is right** — it was one task
covering two rows' R1h hunts plus one build brief, and I did not measure the
split, I assumed it.

### F141 — ⛔⛔⛔ **THE OBLIGATION THIS PROGRAMME CALLS *"THE MOST VALUABLE IN §A3a"* IS GATED ON *"the pre-image run faulted"*, AND BY THE CORPUS'S OWN NUMBERS THAT GATE IS VACUOUS ON **61.3 %** OF THE TEMPORAL AXIS — WHICH IS WHERE **15 OF THE 25 OWED ROWS** LIVE**

⚠ **Manager, 2026-09-16, found by MEASURING row 13's candidate rather than by
reading the protocol.** The measurement came first; the defect fell out of it.

**§A3a obligation 5** reads, in capitals, in `PROTOCOL_PHP.md`:

> ⭐⭐⭐ **RE-RUN THE TRIGGER AGAINST THE R1h POST-IMAGE BUILD — REQUIRED,
> GATED ON *"the pre-image run faulted"*.** If the row's trigger did **not**
> fault, this is vacuous and you skip it, saying so.

⭐ **I ran it on `ph66` anyway**, `sh .tasks-php/probes/rebuild_hardened_php.sh
--label ph66 --patch b73349dbe4e9.patch --trigger <cell D>` — **cold build 30 s,
incremental rebuild 619 ms, 60 MB, no sudo, no network:**

| | pre-image (pristine 5.0.0) | post-image (R1h) |
|---|---|---|
| adversarial — `$a[6385036779]` live, `unset($a["abc"])` | `count=1`, victim destroyed | `count=2`, **victim survives** |
| benign — every key really present | correct | **identical** |
| **exit status** | **`rc=0`** | **`rc=0`** |

⭐⭐⭐ **THIS IS THE CLEANEST OBLIGATION-5 RESULT THE PROGRAMME HAS, AND THE
PROTOCOL TOLD THE ROW TO SKIP IT.** The repair flips the observable completely
and leaves the benign case byte-identical — a *two-sided* result, which the
`rc 139 → rc 0` shape can never give, because a fault tells you the crash
stopped and nothing about whether the answer became right.

⛔⛔ **THE GATE IS STATED ON THE WRONG PREDICATE.** §A3's criterion 2 is *"does
the C exhibit the target error on an adversarial input"* — **not** *"does it
fault"*. Obligation 5's gate silently narrows criterion 2 to its signal-valued
half, and the section's own rationale box says the point is *"the upstream
fix's efficacy measurable on real PHP"*, which is exactly what `rc=0` on both
sides delivered here. ▶ **The right predicate is *"the pre-image run EXHIBITED
THE TARGET ERROR"*, and the row then compares whatever its observable is.**

⭐⭐ **AND THE SCOPE IS NOT A CORNER CASE — IT IS THE MAJORITY OF THE REMAINING
WORK.** `_057` §3.2's measured rates: executed reproducers fault on **38.7 % of
temporal rows** (the corpus's own `crashes_pristine_5_0_0` column says 32.6 %),
and **95.5 % of temporal ids are filed `build=asan`**. ▶ **So the gate excuses
roughly three rows in five on the axis that owes 15 of the 25 rows left.** The
obligation that cost two false refusals and a whole finding (`F123`) to make
REQUIRED is switched off, quietly, for most of the programme's future.

⚠⚠ **AND THE GENERATOR HAD THE SAME ASSUMPTION BAKED IN, WHICH IS HOW I FOUND
IT.** `rebuild_hardened_php.sh` asserted `rc=139` then `rc=0` and **discarded
stdout**. Pointed at `ph66` it would have printed `pristine rc=0 (expect 139)`
and `hardened rc=0 (expect 0)` — *reporting no change across a repair that
changes everything.* ✅ **Repaired in the same commit**: it now prints rc **and**
stdout for both images, diffs them, and **adjudicates nothing**; the row states
the difference. ⭐ *A generator that encodes one row's notion of "worked"
silently mis-reports every row with a different one.*

⛔ **WHAT THIS FINDING DOES NOT CLAIM.** It does not claim anyone skipped
obligation 5 improperly. ⛔⛔ **AND THE SENTENCE THAT STOOD HERE — *"no row
has yet hit the gate, because all twelve built rows' triggers fault"* — WAS
AN ASSERTION BESIDE A DERIVATION I NEVER RAN**, filed in the same session as
`F142`, which is about exactly that. ✅ **Measured**: **6 of 12** built rows
record a fault marker in `NOTES.md` (`ph45` `ph53` `ph56` `ph64` `ph96`
`ph97`) and **6 record none** (`ph03` `ph07` `ph16` `ph29` `ph52` `ph55`).
⭐ **The six blanks are NOT counterexamples, and the true reason is better for
this finding than my sentence was**: §A3a's own preamble says the first ten
rows **ARGUED** criterion 2 rather than running it, and the run-the-trigger
obligation only became REQUIRED at `_057`. ▶ **So the gate has been REACHABLE
on almost no row, its defect has been latent the whole time, and `ph66` is the
first row to reach it and be excused by it.** ⚠ `ph29` looks like a
counterexample and is not — its two `rc=0` lines are KERNEL rows in the R1h
behaviour table (`NOTES.md:1028-1029`), not a §A3a record. ▶ **A reviewer should attack
exactly that**: is *"the gate would have excused this row"* enough, when the row
in fact discharged it? ⓘ I think yes — the protocol's job is to make the check
happen without the manager noticing it should — but that is the claim to break.

▶ **THE REPAIR IS NOT WRITTEN YET AND MUST NOT BE MINE ALONE**: `PROTOCOL_PHP.md`
is the person-facing document `F139` just measured losing a correction race, and
`_061` §5.0 ruled that **the durable home for a trap is an arm that prints**.
▶ **Open item 141**, and the arm is the deliverable, not the wording.

### F140 — ⛔⛔⛔ **A ROUND'S SCOPE IS *DERIVED* FROM THE RULE-9 TABLE AND *NOTHING* IS DERIVED FROM THE ITEMS TABLE, SO AN ITEM THAT SAYS *"THIS IS A REVIEWER'S"* IS INVISIBLE TO THE PROCESS THAT SCOPES ROUNDS — AND ITEM 137 PROVED IT ON ITSELF IN ONE COMMIT**

⚠ **Manager about the manager, 2026-09-16, found by the pre-compact audit
immediately after `_061` landed. UNREVIEWED.**

**Item 137** was registered 2026-09-16 with an explicit route: *"▶ **It is a
REVIEWER's, and it belongs in the round the backlog already owes.**"* ⛔ **That
round is `TASK_PHP_061`. I wrote its brief — eight sections — one commit later,
and item 137 is not in it.** Measured: `grep -ac "item 137"` over the brief is
**0**, and over the 1079-line report **0**.

⭐⭐⭐ **AND THE ITEM'S OWN CLOSING SENTENCE IS THE DIAGNOSIS, FIRED ON ITSELF:**
*"Registered rather than fixed, because a question routed to nobody is one
nobody answers"* (`F123`). ▶ **It was routed to a PROCESS rather than to a
DOCUMENT SECTION, and a process has no inbox.**

⛔⛔ **THE CAUSE IS STRUCTURAL, NOT FORGETFULNESS, WHICH IS WHY A REMINDER WOULD
NOT HAVE HELPED.** A round's scope is **derived**: the brief is written from the
RULE-9 table's `⛔ UNREVIEWED` rows, and `boxcheck.py` prints that set on every
run. **Nothing whatsoever is derived from the items table.** Rounds have folded
items in before — `_057` folded **2**, `_059` folded **4**, `_061` folded **1** —
▶ ***by the manager remembering, which is exactly the variance.***

**Measured population, `boxcheck.py` at `ce3ba37`:** **FOUR** live items hand a
question to a reviewer — **125, 126, 135, 137** — and **`_061` scoped none of
them.** (It scoped item **129**, which is why the gap was invisible: the round
*did* carry an item, just not these.)

> ⭐⭐⭐ **THE REPAIR IS `_061` §5.0's OWN RULING APPLIED TO ITS NEXT INSTANCE.**
> That round measured **four homes for a trap and four failures**, and concluded
> the durable home is **an arm in a tool that prints**. ✅ **So this is an arm in
> a tool that prints**: `boxcheck.py` now reports
> `items -> a reviewer  4  LIVE, unscheduled: 125 126 135 137`.
> ⛔ **It is an `ⓘ` REPORT AND MUST NEVER GATE** — an item may legitimately wait
> several rounds; what it may not do is wait **invisibly**. Same discipline as
> `quota.py`'s one-column report and `F128`'s Kind-A/Kind-B rule.
> ⚠⚠ **And its failure mode is SILENCE**, so it has four must-fire arms in
> `probes/rule9_mustfire.py` — a planted routed item it must find, a **struck**
> row it must not count, **narration** about a reviewer it must not count, and
> a non-vacuity check against the live table. ⓘ **Item 131's shape is the
> reason**: `N12` scored three tools zero arms because they spoke a different
> dialect, and printed that as success.

ⓘ **AND THE FIRST DRAFT OF THAT MUST-FIRE BLOCK WAS INSERTED *AFTER* THE PRINT
LOOP**, so its four arms were evaluated and never displayed — **the silence
failure mode, inside the arm written to catch the silence failure mode**, caught
within a minute by reading the output instead of the exit code. ⭐ `F135`'s rule
working: *read the count, never the exit code.*

### F139 — ⭐⭐⭐ **A CAUTION WHOSE ENTIRE CONTENT IS *SAY WHICH BUILD* NAMED THE WRONG BUILD, NINE AND A HALF HOURS AFTER ITS OWN AUTHOR CORRECTED THAT EXACT CLAUSE IN THE PROTOCOL — AND IT IS THE EXPERIMENT THAT ANSWERS *WHERE DOES A TRAP LIVE?***

⚠ **`TASK_PHP_061` §3.3, reviewer-found, manager-verified independently
2026-09-16. UNREVIEWED as a finding; its measurement is settled.**

`F133`'s `§A3a` caution read *"the binary is php-in-safe-rust's **oracle** build
(**`-O3 -march=native -flto`**, mysql+webext)"*. ⛔ **It is not.**

| | measured |
|---|---|
| what the probe actually runs | `.tasks-php/probes/ph96_arrayaccess_matrix.sh:63` defaults to the **plain** `php-5.0.0-mysql-webext` |
| which binaries carry those flags | **only** the `-O3lto` and `-maxlto` siblings — they are the only two with a `.buildinfo` |
| the plain binary's own flags | **no `.buildinfo` at all**; its `config.status` says **`-O0`** |

⛔⛔⛔ **AND THE CORRECTION WAS ALREADY IN THE PROTOCOL, IN CAPITALS, IN THE
SECTION `F133` CITES.** `PROTOCOL_PHP.md` §A3a: *"⛔⛔ **THIS CLAUSE SAID
`-O3 -march=native -flto` FOR ONE DAY.** Those flags are the SIBLING variants'
… the plain binary has none and its `config.status` says `-O0`. ⭐ **The caution
whose whole point is *say which build* named the wrong build** — `F127`."*

**Dates, from `git log`:** the protocol correction landed at **`1cc2c0e`,
2026-09-15 07:47**. `F133` landed at **`46560f9`, 2026-09-15 17:12**.
▶ **Nine hours and twenty-five minutes. Same author. Same day.**

⭐⭐⭐ **WHY THIS IS THE ROUND'S BIGGEST RESULT AND IS NOT ABOUT `ph96` AT ALL.**
`F134` proposed a remedy — *move a trap out of the tool docstring to where a
PERSON meets it* — and **`F139` is that remedy's experiment, run by accident.**
The knowledge was in a person-facing prose document, **in capitals**, in the
very section the finding cites, written **that morning** by the person who broke
it **that afternoon**. ▶ **The person-facing document lost.** That is the
evidence `_061` §5.0's ruling rests on, and a ruling whose evidence is buried in
a review report will not survive the next round — which is why this is a finding
and not a footnote.

✅ **REPAIRED IN BOTH HOMES, and the second one is the point**: the `RECAP_PHP.md`
caution **and the probe's own header comment**, which repeated the wrong flags
seven lines above the line that defaults to the right binary. ⛔ **Two homes for
one fact, and both were wrong in the same way** (`F131`).

ⓘ **`F127` is now at three instances**, and this one is the first where the
corrected text and the re-broken text had the **same author within one day**.

### F138 — ⛔⛔⛔ **I RAN THE TOOL AND STILL PUBLISHED A FALSE SUPERLATIVE, BECAUSE I CONSUMED ITS CARDINALITY AND NEVER PRINTED ITS MEMBERS: THE BACKLOG "PEAK 9" IS SIX ROWS OF DOUBLE-COUNTING, AND THE DOUBLE-COUNTING IS `F131`'s OWN DEFECT**

⚠ **Manager about the manager, 2026-09-16, caught while scoping `_061` —
i.e. while writing the brief for the round that reviews `F131` and `F132`.
UNREVIEWED.**

The 2026-09-16 pre-compact audit replaced the START HERE box's unchecked
superlative *"BACKLOG 7, LARGEST EVER"* with what looked like the disciplined
repair: a **measured** series and a **measured** peak, `2 → 4 → 7 (PEAK 9)`,
derived by running `boxcheck.rule9_rows` over 40 `RECAP_PHP.md` commits.
⛔ **The replacement is also false.**

| commit | raw open rows | de-duplicated | what inflates it |
|---|---|---|---|
| `1cc2c0e`, `6bff271` | **7** | **1** | `F120`–`F125` |
| `7c9f1eb`, `cddd82b` | **8** | **2** | `F120`–`F125` |
| `d9652b4`, `f98e716` | **9** | **3** | `F120`–`F125` |

⭐⭐⭐ **`F120`–`F125` HAD ALREADY BEEN VERDICTED BY `_057`.** They scored as open
because each key had **two rows** — the opening `⛔ UNREVIEWED` row and the
verdicted row `_057` appended beneath it. ▶ ***That is exactly the defect `F131`
was filed about***, so the "peak" is a measurement of `F131`'s damage rather
than of any backlog. ⛔ **The corrected maximum in the window is `7`, at
`1db52a3` — which is TODAY's number**, so *"the second-largest ever"* is wrong
in the other direction too: **today ties the record.**

⛔⛔ **THE PART THAT MAKES THIS A FINDING AND NOT AN ERRATUM — AND MY FIRST
STATEMENT OF IT WAS WRONG, REFUTED BY `_061` §5.0a IN ITS LOAD-BEARING WORD.**

> ⛔ ~~*"I DID RUN THE TOOL. `rule9_rows` returns the set; I took `len()` of it.
> One `print` of the set would have ended the question."*~~ **FALSE. THE TOOL
> WAS NOT RUN.** `.tasks-php/boxcheck.py`'s `main()` **already prints the
> members** — `… open cycle(s): {" ".join(open_cycles)}` — and
> `git log -S` dates that line to **`c868e60`, 2026-09-15 14:43**, which is
> **`F131`'s own repair, written by me the day before.** ▶ **What I ran was a
> bespoke sweep that imported `rule9_rows` and reimplemented the reporting path
> badly.**

> ⭐⭐⭐ **THE CORRECTED RULE, AND IT IS SHARPER THAN MINE WAS:
> *"I CALLED THE TOOL'S FUNCTION" IS NOT "I RAN THE TOOL."*** ⭐⭐ **And that
> makes `F138` MORE distinct from `F132`, not less, on a ground it did not
> state**: `F132` is *a count standing in for a set* and its remedy is **diff
> the set**; this is *a one-off caller not inheriting the checker's reporting*
> and its remedy is **run the checker**. ✅ **Verdict: keep them separate.**
> ⛔ **`F132` was written by the manager, about the manager, eight days
> earlier; this instance was made WHILE WRITING THE BRIEF THAT ASKS A REVIEWER
> WHERE `F132`'s LESSON SHOULD LIVE.**

⚠ **Two further corrections from the same round, applied rather than appended:**
**(a)** my de-duplication rule — *a key with two rows has been verdicted in one
of them* — is the **right answer from the wrong rule**; it holds only because
every duplicated key happened to have one verdicted row. ▶ **The structural rule
needs no heuristic: the backlog is the distinct KEYS no row of which carries a
verdict.** **(b)** my *"a tool returning a falsy value for 'cannot answer'
invites the `len()` mistake"* is **refuted in its mechanism** — `rule9_rows`
returns `(None, None)` and **`len(None)` raises**, so it is loud, not silent.
✅ **The recommendation survives for the SERIES** (twelve no-parse commits are
UNKNOWN, never 0) **but not for that reason, and the tool needs no repair for
it.**

⛔⛔ **AND IT PROPAGATED INTO A TASK FILE BEFORE IT WAS CAUGHT** —
`TASK_PHP_061.md` §0 carried *"a measured peak of 9"* as a premise.
`PROTOCOL.md` **rule 14**'s own class: *a premise in a task file is one an
engineer has no reason to doubt.* ✅ **Corrected in place and deliberately left
visible in the brief**, because a reviewer asked to rule on where a trap lives
should be handed a live instance rather than a description of one.

ⓘ **A methodological residue, recorded so nobody re-reads it as zero:** twelve
of the forty commits in the window return **no parse** — the RULE-9 block did
not yet have its current shape. ⛔ **They are UNKNOWN, not 0**, and any series
over this window must say so.

### F137 — ⭐⭐⭐ **C's DETECTION AND UNSAFE RUST'S ARE BOTH BUILD-DEPENDENT AND FAIL THE SAME WAY — DETECTED LOW, SILENT HIGH. SAFE RUST'S IS THE ONLY ONE THAT DOES NOT MOVE.**

⚠ **`TASK_PHP_060` (row 12, `ph96`), measured, UNPREDICTED BY ANYONE.
UNREVIEWED.**

`controls/widened_domain.py`'s optimisation sweep, R1 on the row's own
adversarial input:

| compiler | `-O0` | `-O1` | `-O2` | `-O3` |
|---|---|---|---|---|
| **gcc** | SIGSEGV `0x10` | SIGSEGV `0x10` | SIGSEGV `0x10` | SIGSEGV `0x10` |
| **clang** | SIGSEGV `0x10` | SIGSEGV `0x10` | ⛔ **silent wrong answer** | ⛔ **silent wrong answer** |

Above `-O1`, clang propagates *`retval` is non-NULL* backwards from the
dereference and the sentinel path returns `18121308747923605504` where the
**R1h** answers `15642763268152511488`. **No crash, no diagnostic, a wrong
checksum.** ⚠ **The control's own wording is the one to quote and it is
sharper**: *"SILENT WRONG ANSWER — **UB exploited, not lowered**"*
(`controls/widened_domain.py:202`). ⛔ **Do NOT let this be read as *"clang
miscompiles"*: the C is UB and clang is within its rights** — and *"the correct
answer"* over-states it, because a program with UB has no correct answer. **The
finding is about DETECTION, not correctness.**

⭐⭐ **THAT IS `F3` — *a clean run is not evidence of absence* — FIRING LIVE, on
a row that carries a faulting run to compare it against.** ▶ **A reviewer who
tested only `c-clang -O3` would have concluded the defect was not reachable.**

⭐⭐⭐ **AND THE SAME SHAPE APPEARS ONE LANGUAGE OVER** (`controls/rust_bug.py`):

| variant | `-O0` | `-O1` | `-O2` | `-O3` |
|---|---|---|---|---|
| safe Rust + `unwrap`, guard deleted | panic 101 | panic 101 | panic 101 | panic 101 |
| unsafe Rust + `unwrap_unchecked`, guard deleted | **SIGABRT** | **silent wrong answer** | silent wrong answer | silent wrong answer |
| the SHIPPED `unsafe.rs` | answers | answers | answers | answers |

▶ ⭐⭐⭐ **THE LADDER SENTENCE, AND IT IS A NEW KIND FOR THIS PROGRAMME: the
axis is not COST, it is WHETHER DETECTION SURVIVES THE OPTIMISER.** Unsafe Rust
buys back C's performance **and C's failure mode with it**; safe Rust's
detection is the only one invariant across `-O0..-O3`. ⚠ **This is the first row
where safe Rust's advantage is stated in a currency the ladder's cost columns
cannot express at all** — which is a **finding**, not a gap (`CLAUDE.md` rule 6).

⚠ ~~**What a reviewer owes it**: … `ph97` is the obvious first candidate and was
not swept.~~ ✅✅ **SWEPT AT `_061` §1.2 — AND IT REFUTED THE GENERALISATION.**

> ⛔⛔⛔ **CLAUSE 2 — *"a property of the C-vs-Rust ladder, not of `ph96`"* — IS
> REFUTED BY THE ROW THIS FINDING NAMED AS ITS OWN FALSIFIER.** On `ph97`'s
> `adversarial-absent.bin`, built the same way, the C rung **faults in all eight
> builds**: gcc `SIGSEGV (nil)` at every `-O`, clang `SIGSEGV (nil)` at `-O0`/
> `-O1` and `SIGSEGV 0x1` at `-O2`/`-O3`. **No silent answer anywhere.**
>
> ⛔⛔ **AND THIS FINDING NAMED THE WRONG INPUT.** *"Any row with a
> null-sentinel adversarial input"* pointed at `ph97`'s file literally called
> `adversarial-nullvalue.bin` — **eight builds, eight clean runs.** The faulting
> input is `adversarial-absent.bin`, and `ph97`'s own `inputs/gen.py` says so.
> ▶ **A reviewer picking by NAME would have reported `F137` refuted for the
> wrong reason.** ⭐ `F134`'s class, inside this finding's own falsifier.
>
> ⭐⭐⭐ **WHAT SURVIVES IS STRONGER AS A RULE AND WEAKER AS A HEADLINE — and
> the `-O2` clang boundary is REAL ON BOTH ROWS** (`ph97`'s `si_addr` moves
> `(nil) → 0x1` at exactly `-O2`, where `ph96` goes silent). **What differs is
> the consequence, and the discriminator is where the faulting load sits:**
>
> > *An optimiser can convert a **detected** fault into a **silent wrong
> > answer**, and whether it does is compiler-, level- and **row**-dependent. It
> > happens when the UB licenses folding a **branch** whose outcome is the
> > answer; it does not happen when the faulting load's **value IS** the answer.*
>
> `ph96`'s sentinel feeds `if (!retval)` — a foldable branch. `ph97`'s is passed
> into a byte loop whose result is the answer — **nothing to fold**, so the
> optimiser can only reorder, which is what `si_addr` `0 → 1` looks like.
>
> ⚠⚠ **AND THE TWO TABLES ABOVE ARE NOT PARALLEL, WHICH THIS FINDING MUST SAY.**
> The **C** table's build-dependent rung is the **shipped R1**; the **Rust**
> table's is a **guard-deleted mutant that is no rung of the ladder** — the
> shipped `unsafe.rs` answers correctly at all four levels on both rows. ▶ **So
> *"unsafe Rust buys back C's failure mode"* is a claim about a HYPOTHETICAL R4
> that spells the defect, not about either row's R4 as built.**
> ⓘ ⛔ **The manager's own correction here was ALSO wrong**: `_061` §1.3 shows
> `ph97`'s variant *is* a guard-deleted mutant of the shipped rung, same
> construction as `ph96`'s — the JSON's `source:` field names the **base**, not
> the program. **`F134`'s class three levels deep in one round: the finding, the
> brief's correction of it, and the brief's correction of its own correction.**
>
> ⭐ **And the third outcome the two-way split has no room for is real, on the
> Rust side, in `ph97`'s committed `rust_bug.json`**: `O0` rc `−6`, then
> **`TIMEOUT`** at `O1`/`O2`/`O3`. **Not detected, not silent — hung.**

### F136 — ⭐⭐ **THE CONTRACT THAT CANNOT BE MISUSED IS FREE *ONCE IT INLINES* — AND UN-INLINED IT IS NOT FREE, AND UPSTREAM'S SPELLING IS THE DEARER ONE**

⚠ **`TASK_PHP_060`, measured. ⛔ IT REFUTES THE MANAGER'S `P1` IN FOUR CELLS OF
FOUR **AND** BOTH HEADLINES HE OFFERED.** ⚠ **REVIEWED AT `_061`: conclusion
upheld as measured, MECHANISM upheld and under-stated, ⛔⛔ HEADLINE REFUTED.**

> ⛔⛔⛔ **THE TITLE SAID *"IS FREE"* FULL STOP, AND THAT GENERALISES PAST THE
> CELL IT MEASURED.** `_061` §2.2 took this finding's own closing parenthesis —
> *"and inlining erases even that"* — as the **forward prediction** it is, and
> ran the same control with `-O3` changed to `-O0`. Checksums equal in all 24
> runs, so every difference is a price:
>
> | statistic | cell | `guard − noout`, `c-gcc` `small`/`large` | `c-clang` `small`/`large` |
> |---|---|---|---|
> | **A1** | `O3/isolated` | `+0.0000` / `+0.0000` | `+0.0000` / `+0.0000` |
> | **A1** | `O0/isolated` | `+0.0000` / `+0.0000` | `+0.0000` / `+0.0000` |
> | **W1** | `O3/isolated` | `+0.0000` / `+0.0000` | `+0.0000` / `+0.0000` |
> | ⛔ **W1** | **`O0/isolated`** | **`−2.2419` / `−19.5768`** | **`−0.7397` / `−6.5296`** |
>
> (**`c-gcc`** `−0.1370 %` / `−0.1417 %` and **`c-clang`** `−0.0565 %` /
> `−0.0584 %`, W1, `O0/isolated`, base `noout`, **both C columns named**.)
> ⭐ **It is real work, not startup noise**: the deltas are **not** proportional
> to driver calls but to **records processed** — `0.3203` and `0.3157` Ir/record
> under **`c-gcc`**, `0.1057` and `0.1053` under **`c-clang`**. **Two inputs,
> one constant, per compiler.**
>
> ▶ ⭐⭐⭐ **THE CORRECTED CLAIM: the price is zero BECAUSE BOTH SPELLINGS INLINE
> INTO ONE SYMBOL. Un-inlined they differ — and in the direction the finding
> ruled out: upstream's no-output repair is the DEARER of the two.**
> ✅ **The published figures are NOT wrong** — every one of the four cells
> reproduces to the digit and the finding names its cell. **It is the TITLE and
> the body's *"the price is exactly zero"* that travel past it.**
>
> ⚠⚠ **AND THIS IS OPEN ITEM 137's LIVE CONSEQUENCE, WHICH IT DID NOT HAVE
> WHEN I REGISTERED IT.** `ph96` publishes **`A1` only**. At `O0/isolated` the
> two statistics disagree in the strongest possible way — **A1 reads `+0.0000`
> against a sign-stable, scaling W1 difference on four cells** — which is the
> `ph55` counterexample already on file, **reproduced on `ph96`, on this
> finding's own quantity.**

The two upstream-attested repairs of `I12/O1` (`F133`) priced against each
other — **A1, `O3/isolated`, base = `noout` (upstream's own strategy), BOTH C
COLUMNS**, checksums asserted equal on every input first so the difference is a
price and not a semantics change:

```
c-gcc     small.bin    guard - noout = +0.0000 Ir/call  (+0.0000 %)
c-gcc     large.bin    guard - noout = +0.0000 Ir/call  (+0.0000 %)
c-clang   small.bin    guard - noout = +0.0000 Ir/call  (+0.0000 %)
c-clang   large.bin    guard - noout = +0.0000 Ir/call  (+0.0000 %)
```

⭐⭐⭐ **AND UNDER `c-clang` THE TWO REPAIRS ARE THE SAME PROGRAM** —
`identity_level=exact`, 280 insns and 1070 bytes both ways (`c-gcc`:
`counts`, 207/207 insns, 705/705 bytes).

▶ **THE MECHANISM, AND IT IS STRUCTURAL RATHER THAN AN OPTIMISER ACCIDENT:
*removing the output* does NOT delete the NULL test — it moves the call site
from `zend_interfaces.c:94`'s contract onto `:88-93`'s, where `:89`'s
`if (retval)` does the work.** Both configurations run **one** NULL test and
**one** conditional release; only *where the test is written* differs, and
inlining erases even that. ⭐ **`cf020f133487` is therefore best read not as
*deleting a test* but as *moving a call site onto a contract whose test is
already written*.**

✅✅ **UPHELD AND UNDER-STATED — AND NOW MEASURED PER SYMBOL, WHICH IT NEVER
WAS** (`_061` §2.3, `callgrind_annotate` per function on the two `-O0` builds;
gcc, `small.bin`, 20 000 calls):

| symbol | `noout` | `guard` | delta |
|---|---:|---:|---:|
| `ph96_call_method` — the callee, `:88-93`'s home | 4 977 962 | 4 894 543 | **−83 419** |
| `ph96_unset_dimension` — the caller, `:512` | 873 429 | 912 010 | **+38 581** |
| `kernel` — **the A1 symbol** | — | — | **+0** |
| **whole program** | | | **−44 838** |

**At `-O3`: no symbol differs at all.** ▶ ⭐⭐ **The structural story is now a
number — 83 419 `Ir` leaves the callee and 38 581 arrives in the caller — and
it under-states in one direction: the two contracts are NOT the same amount of
work.** The callee's `:88-93` disposal costs **more** than the caller's guard.
⛔ **And `+0` in `kernel` is exactly why A1 could not see any of it.**

⛔⛔ **BOTH OF THE MANAGER'S OFFERED READINGS ARE UNSUPPORTED**, and he offered
them as a matched pair so that either would be a result: *removing the output is
cheaper* fires `P1`'s own falsifier, and *safety-by-construction had a price
here and upstream paid it* is false too — **the price is exactly zero.**
⚠ **Registering both poles of a disjunction does not make the disjunction
exhaustive**, which is the method lesson and the manager's to carry.

### F135 — ⛔⛔⛔ **A KNOWN ARM FAILURE WAS RE-CLASSIFIED AS AN EXPECTED EXIT CODE: `citecheck.py --selftest` FAILED `N5d`/`N4` FOR 43 COMMITS WHILE THE SWEEP PRINTED `ok`, BECAUSE THE RATCHET WAS SILENCED BY EDITING ITS *EXPECTATION* INSTEAD OF ITS INPUT**

⚠ **Manager, found 2026-09-15 by the five-checker law-16 sweep — which was
looking for something else entirely and found this instead. UNREVIEWED.**

`N5d` and `N4` assert that two warning-only extensions leave the LIVE-doc rot
count *"untouched"*. Written at `4297b1d` when the live rot happened to be **0**,
they encoded that **absolute literal** — `rot == 0` — for a claim their own
message states **relatively**. The standing adjudicated false positive arrived
the next day at `3448a5a`, rot became **1**, and both arms went red, **blaming an
extension that had nothing to do with them.**

⛔⛔⛔ **NOTHING CAUGHT IT FOR 43 COMMITS — five rows, three review rounds and
two pre-compact audits — AND NOT BECAUSE THE INFORMATION WAS MISSING.**
`.tasks-php/checkers.py` **said so, by arm name**: *"▶ Both arms are red for
this same one cause: `--selftest` fails `N5d`/`N4`, which assert `rot == 0`."*
It then set `st_expect=1`, so `rc == expect` held and the sweep reported `ok`.

⭐⭐⭐ **THE LOAD-BEARING ERROR IS THAT ONE SENTENCE, AND IT IS FALSE.** The arms
did **not** inherit the false positive's benignness — **they were defective
before the rot arrived**, and the rot merely *moved the number and revealed
them*. ▶ ***A BENIGN CAUSE DOES NOT MAKE A FAILING ARM BENIGN.***

⭐⭐ **AND THE MECHANISM IS THE RATCHET'S OWN, ONE LEVEL UP.** The ratchet's
standing rule is *never silence a checker by editing its INPUT*. This one was
silenced by **editing its EXPECTATION** — `st_expect` captured from observation
rather than derived from intent. ⚠ **The adjudication it borrowed is itself
correct and is untouched**; what was wrong was extending it to two arms whose
predicate was independently broken.

✅ **REPAIRED, BOTH HALVES.** `N5d` now asserts the **structural disjointness**
of the rot-bearing `LIVE` set from the extensions' inputs (81 live docs vs 203
extension inputs, 0 shared) — true at *any* rot value — and `N4` becomes the
non-vacuity arm that keeps the disjointness a real separation. `--selftest`
already exited on **arm state alone** (`sys.exit(selftest())`), so `st_expect`
is now **`0`, derived from intent**, and a future arm failure is visible again.
⚠ **`expect=1` on the BARE run stays**: that one really is the adjudicated rot,
and *read the COUNT, never the exit code* still governs there.

ⓘ **This is the EIGHTH pinned figure to go stale in a `.tasks-php/` validator**
(`.memory-php/04-process.md` law 6, *a bound is not a derivation*) — and the
first to be hidden by a second validator agreeing with it.

### F134 — ⛔⛔⛔ **A DEFECT REPAIRED IN A TOOL IS NOT REPAIRED IN THE MANAGER: I MADE BY HAND, THREE DAYS LATER, THE EXACT ERROR `preimage_screen.py` WAS PATCHED TO STOP MAKING — AND ITS DOCSTRING DESCRIBES MY ERROR IN ADVANCE**

⚠ **Manager self-finding, 2026-09-15, caught in-flight while scoping row 12.
UNREVIEWED.**

Scoping `ph96` I listed which cached patches touch `zend_object_handlers.c` by
reading each hunk's **`@@ … @@ <function>` trailing label**, and reported that
`235e6c0afe1d` touches `zend_std_unset_dimension`. **It does not.** Its body
edits `zend_std_call_user_call`; the label names the function the hunk **starts
after**. I caught it only because I went on to read the diff body.

⛔⛔ **AND THIS IS A SOLVED PROBLEM IN THIS REPOSITORY.**
`.tasks-php/preimage_screen.py::same_function`'s docstring says it in terms:

> *"git's `xfuncname` scans BACKWARDS FROM THE HUNK'S FIRST LINE, so a hunk that
> begins just before a function definition is labelled with the PRECEDING
> function while editing only the NEXT one."*

Found by `TASK_PHP_040` §4.3, measured on `be8daf1f47fa` (*"the hunk contains
ZERO lines of the function it is labelled with — not one context line"*), and
**repaired by the manager on 2026-09-12 with its own negatives**, because a
false promotion of an exclusion to a proof is the one direction that screen may
not fail in.

⭐⭐⭐ **THE FINDING IS NOT *"I MADE A MISTAKE"*. IT IS THAT THE REPAIR LIVED IN
THE CODE PATH AND I WAS NOT ON IT.** The tool cannot be fooled by `xfuncname`
any more. The manager reading a patch by hand is not the tool, inherits none of
its guards, and has no docstring in front of him. ▶ ***A trap documented only
where the code meets it is documented for the code, not for the person.***

⚠ **SECOND INSTANCE IN THE SAME HOUR, AND IT IS THE SAME SHAPE.** I then ran a
compound `grep -al 'A\|B'`, got a hit, and attributed it to `A`; it had matched
`B`, in a different file that does not contain `A` at all. ▶ ***Never attribute
a compound match.*** Both are **item 115's class** — *a check that reads prose
and calls it code* — with the twist that here the misleading string was
**generated by a tool** and therefore looked authoritative.

▶ **THE REMEDY, AND IT IS NOT *"BE CAREFUL"*:** both now sit in a task file's
`§3 TRAPS` (`_060` trap after §2.5) where a *person* meets them, not only in a
docstring where the *code* does. ⚠ **What a reviewer owes this: is the traps
list the right home, or does this belong in `.memory-php/04-process.md` as a
law?** The manager did not decide, deliberately — ⓘ **it is a claim about how
this programme's knowledge is stored, which is exactly the shape `F123`'s
still-unverdicted clause has, and item 129's census is the instrument.**

⚠ **NOT a claim that the tool's measured reach changed.** `same_function`'s
*"1 of 170"* was measured over one task's screened set; my instance is a **hand**
reading outside the tool's path, and whether `235e6c0afe1d` is even in that 170
**I did not measure.** ⛔ **Do not quote this finding as moving that number.**

### F133 — ⭐⭐⭐ **BOTH CORRECT SPELLINGS OF AN OBLIGATION AND BOTH WRONG ONES LIVED IN ONE FILE: THE 2005 REPAIR OF `ph96` CONSISTS OF COPYING A SIBLING 99 LINES UP, AND THE UNMISUSABLE CONTRACT WAS ALREADY SUPPORTED IN THE VULNERABLE TREE**

> ⛔⛔ **THE TITLE SAID *"IN ONE FILE, BY ONE AUTHOR"* AND THE SECOND HALF IS
> REFUTED FROM THE CITATION BASE** (`_061` §3.2). Measured from the pinned
> tarball: `zend_object_handlers.c` (all four call sites) carries
> **`Authors: Andi Gutmans, Zeev Suraski`** with **`wez`** as last `$Id`
> committer; `zend_interfaces.c` (the contract) carries **`Marcus Boerger`** /
> **`helly`**. **Two named authors on one file, a third as last committer, and a
> different one on the other. There is no git history in a tarball.**
> ✅ ***"IN ONE FILE" IS TRUE*** of the four call sites and is kept.
> ⭐ **What IS establishable is weaker and is the one the bytes support**: the
> **fixer** is Boerger (`cf020f133487`, 2005-03-19), who authored the file the
> contract lives in — **evidence that the person who APPLIED the repair knew the
> contract, not that whoever WROTE the defective call sites did.**
> ▶ ⭐⭐ **SO (iii) IS RE-GROUNDED ON (i) AND THE RULE IS RE-WORDED: an R1h is
> evidence about what was CHOSEN, not always about what was *DISCOVERED*** —
> *"known"* was a claim about minds that the corpus cannot carry.

⚠ **Manager, measured 2026-09-15 while scoping row 12, from the pinned tarball
and the 5.0.0 oracle. UNREVIEWED. This is a C-side finding; it commits the
ladder to nothing.**

`Zend/zend_object_handlers.c` calls **one** helper,
`zend_call_method_with_1_params`, from **four** ArrayAccess handlers. Measured
end to end (`.tasks-php/probes/ph96_arrayaccess_matrix.sh`, one throwing user
method per run, `segaddr` shim, 5.0.0 oracle):

| site | handler | contract | result |
|---|---|---|---|
| `:384` | `offsetGet` | output, **guarded at `:385 if (!retval)`** | `rc=255`, clean `Uncaught exception` |
| `:413` | `offsetSet` | **no-output — passes `NULL`** | `rc=255`, clean `Uncaught exception` |
| `:427` | `offsetExists` | output, **unguarded** | ⛔ `SIGSEGV si_addr=0x14` |
| `:512` | `offsetUnset` | output, **unguarded** | ⛔ `SIGSEGV si_addr=0x10` |

⭐ **Both fault offsets were computed from `Zend/zend.h:287-293` BEFORE the run
and matched**: the `zvalue_value` union is 16 B on LP64, so `0x10` is
`offsetof(zval, refcount)` (`_zval_ptr_dtor`, `zend_execute_API.c:389`) and
`0x14` is `offsetof(zval, type)` (`i_zend_is_true`). ▶ **The fault ADDRESS names
WHICH SITE ran** — §A3a criterion 2 sharpening from *"it faults"* to *"it faults
where the source says it must, and the address discriminates siblings."*

⭐⭐⭐ **THE THREE THINGS THAT MAKE THIS MORE THAN A NULL-DEREF ROW:**

1. **The callee GUARANTEES the sentinel, on purpose, with a comment.**
   `zend_execute_API.c:592-594` reads *"we may return SUCCESS, and yet retval may
   be uninitialized, if there was an exception..."*, and `:595` stores `NULL`
   unconditionally so the hazard is **detectable** — then `:873` returns
   `SUCCESS` anyway with `EG(exception)` set. **The author named the hazard, made
   it observable, and three of four callers did not observe it.**
2. **The unmisusable contract ALREADY EXISTED in the vulnerable tree.**
   `zend_interfaces.c:48` is
   `fci.retval_ptr_ptr = retval_ptr_ptr ? retval_ptr_ptr : &retval;`, and
   `:88-93` disposes of the value **behind its own `if (retval)` NULL test** —
   ⭐⭐ **the very test `:513` omits, written by the same hand, in the function
   being called.** Census of 5.0.0: **23 real call sites, 7 already take the
   no-output contract, 16 take the output contract.**
3. **So upstream's fix did not DISCOVER a strategy — it COPIED one.**
   `cf020f133487` (2005-03-19, *"Fix #31185"*) makes `:512` look exactly like
   `:413`: pass `NULL`, delete the local, delete the dtor.

▶ ⭐⭐ **WHAT THIS CHANGES ABOUT R1h, AND IT IS THE PART WORTH REVIEWING.** The
programme reads an R1h as *the repair upstream eventually found*. Here the repair
was **available, correct, in the same file, and already in use on 7 of 23 call
sites before the bug was filed.** ▶ ***An R1h is evidence about what was CHOSEN,
not always about what was DISCOVERED*** — and row 12 is the first row that can
price **two** upstream-attested repairs of one obligation against each other
(`_060` §2.6: `NULL`-passing vs guarding).

✅✅ **AND (i) GENERALISES TO A SECOND ROW AT ZERO COST** (`_061` §3.4). `ph56`
is the only other row shipping a `census` control, and its `census.json`
`evidence.guards` — measured against the pinned tarball — says **`BP_VAR_R` and
`BP_VAR_UNSET` already carried the guard in pristine 5.0.0**, while
`1e708a5aeb30` adds it to **`BP_VAR_IS` only**. ▶ **On `ph56` too the repair was
already written, in the same `switch`, in the same file, before the bug was
filed: the fix copies a sibling arm.** ⭐⭐ **And `ph56` answers the authorship
half in the OPPOSITE direction, which is why (iii) had to be re-grounded**: its
own docstring records the sibling defect fixed *"11½ months later, at RUNTIME,
in a different file, **by a different author**"* (Dmitry Stogov). ▶ **Where the
corpus can speak about authorship at all, it says the repairs of one construct
come from different hands.** ⛔⛔ **THE ANSWER WAS IN A COMMITTED CONTROL'S OWN
HEADER AND COST NOTHING — `F134`'s class, fourth instance in one round.**
⚠ **A third row has no instrument**: the other ten ship no census, and building
one is **an estimate of one task per row, explicitly not measured.** ▶ **The
cheap half is free and is what to dispatch** — *"was the R1h's strategy already
present elsewhere in the same construct?"* is one `grep` per row against the
pinned tarball. **Do NOT dispatch ten censuses.**

⛔⛔ **TWO THINGS THE CATALOGUE ENTRY GETS INCOMPLETE, BOTH REPORTED NOT
REPAIRED** (`patterns-php/` is the engineer's to edit, and `CATALOGUE.md` is a
landed artefact):

- **`ph96`'s entry names only `:509`/`:512-513`.** The `:427-429`
  `has_dimension` limb is the same defect, derefs the NULL **twice**
  (`i_zend_is_true` then the dtor), and is **not mentioned**.
- **Measured across all 163 cached patches by diff BODY: `:512-513` is repaired
  by `cf020f133487` uniquely, and `:427-429` by NOTHING.** ⚠⚠ **SCOPE, AND IT
  BINDS ANY QUOTE OF THIS**: that is the **screened corpus cache**, not php-src's
  full history. ***"No repair in the cache" is a result (F10); "upstream never
  fixed it" is a claim this box cannot support.***

> ⭐⭐ **CONFIRMED BY EXECUTION AT `_060`, ONE LEVEL STRONGER THAN THE CACHE
> SCAN — recorded here rather than as its own finding (`F131`: one home per
> fact).** This is the engineer's measurement, **not** a verdict on `F133`,
> which remains ⛔ UNREVIEWED. **A real PHP 5.0.0 was rebuilt with
> `cf020f133487` backported** (§A3a obligation 5, 30 s cold / 611 ms
> incremental): the patched build **answers `offsetUnset` correctly and STILL
> FAULTS ON `offsetExists`, rc 139**, and both C rungs of the row fault at
> `0x14` there. ▶ ***The upstream repair is incomplete, and that is now an
> executed fact rather than an absence in a patch cache.*** ⚠ **The scope
> sentence above still binds**: this shows `cf020f133487` does not repair the
> second limb; it still says nothing about whether some *other* commit, outside
> the cache, ever did.
>
> ▶ ⭐ **AND THE SECOND LIMB IS ROUTED TO THE CATALOGUE AS A CANDIDATE ROW, NOT
> KEPT AS A LIMB OF `ph96`** — manager's ruling, 2026-09-15, written in place in
> `patterns-php/ph96-outparam-unwritten/NOTES.md` §5 where the question was
> asked. Same obligation, different site, **no repair IN THE CACHE** — ⚠ **not *no known repair*, which is the phrase that will travel badly: that is the 163-patch screened corpus, not php-src's full history** (`F10`). ⛔⛔ **The ruling
> also records that the tension was the MANAGER'S DEFECT**: `TASK_PHP_060` §2.5
> said *"model the CONTRACT, not the site"* while pinning an R1h that repairs
> one of the two faulting shapes, and those cannot both be honoured. **The rule
> that replaces it: model all four shapes in the BENIGN domain; an ADVERSARIAL
> input may only exercise a shape the row's R1h repairs.**

⚠⚠ **THE TWO §A3a CAUTIONS TRAVEL WITH EVERY NUMBER ABOVE**: the binary is
php-in-safe-rust's **oracle** build — ⛔⛔ **THIS SAID `-O3 -march=native -flto`
AND THAT IS THE WRONG BUILD, SEE `F139`. The probe runs the PLAIN
`php-5.0.0-mysql-webext`, which carries no `.buildinfo` at all; only the
`-O3lto` and `-maxlto` siblings do, and the plain binary's `config.status` says
`-O0`.** ▶ **Quote it as *the oracle build, plain `mysql-webext`, flags not
recorded in a `.buildinfo`*, and say that rather than guessing** — **not** a
museum-default 5.0.0; and **a clean run would NOT have been evidence of
absence** (F3). ⭐ **A faulting run is evidence of presence — and here two
non-faulting cells are evidence that the two correct spellings WORK, in the
vulnerable binary, which is the half that makes this a 2×2 rather than a pair.**

### F132 — ⛔⛔⛔ **A RATCHET'S COUNT IS NOT A MEASURE OF ITS CORPUS. THE UNIT IS A PARAGRAPH, SO ORDINARY PROSE MOVES THE NUMBER WITH NOTHING REPAIRED AND NOTHING BROKEN — AND IT HID A REAL ARRIVAL TWICE IN ONE DAY**

⚠ **`TASK_PHP_059` found the first instance; the manager made the second and
third within the hour, while landing the round. UNREVIEWED.**

The house ratchet pattern is *adjudicate every hit BY HAND with a reason; never
tune the regex*, and its arithmetic is a **count**. ⛔⛔ **`cbaseline_check.py`'s
`units()` splits on BLANK LINES, so its unit is a PARAGRAPH — and the count is
therefore a property of the corpus's PARAGRAPH BOUNDARIES as much as of its
claims.**

| # | what moved the count | and what was actually repaired |
|---|---|---|
| **1** | `RECAP_PHP.md`'s **Index** unit stopped hitting because **a later finding's TITLE added the literal `c-gcc` to it** | **nothing** — found by `_059` |
| **2** | `.memory-php/02-ladder.md`'s FOURTH-FLAG **blockquote** stopped hitting because the item-132 block inserted **into the same unit** carries `c-gcc`, so `BASE` matched | **nothing** — the manager, landing `_059` |
| **3** | `ph16`'s `NOTES.md` *"99.20–99.66 %"* unit stopped hitting because **a blank line SPLIT the unit in two** and the first half lost the bare `C` that `XLANG` was matching | **nothing** — the manager, same edit |

⭐⭐⭐ **AND IN INSTANCE 1 IT HID A REAL ARRIVAL.** The `_058` landing recorded
*"`RECAP_PHP.md` went 35 → 34, so eight arrived and one left"*, and read the
departure as progress. **It was not a repair.** ▶ **The ratchet absorbed one new
hit under cover of an accidental departure.** ⛔ **Instances 2 and 3 did it
again**: the bare run read `78` against a baseline of `77`, so the net was `+1`
— **and THREE had arrived.**

> ⭐⭐⭐ **THE RULE: ADJUDICATE THE SET, BY UNIT TEXT, NEVER THE NUMBER.**
> ⛔ **A line-keyed diff cannot do it either** — line numbers move under every
> edit, which is why every earlier attempt was done by eye. ✅ **Tool committed:
> `.tasks-php/cbaseline_diff.py`, read-only, optional git ref, four must-fire
> arms that plant instances 2 and 3 in a string.** It reproduces `F130`'s
> `70`-at-`1cc2c0e` baseline **without a worktree**.

⚠⚠ **THE UNCOMFORTABLE PART, AND IT IS THE REASON THIS IS A FINDING AND NOT A
FOOTNOTE: instances 2 and 3 were made BY THE MANAGER, IN THE EDIT THAT LANDS THE
REVIEW OF THE RATCHET, ON THE SAME DAY THE REVIEWER NAMED THE MECHANISM.** The
warning had been read, understood, and written into this file **before** the
edit that tripped it twice. ▶ **So *"remember to check"* is refuted as a control
by the strongest available evidence: the person who wrote the reminder.** ⓘ
`F131`'s lesson one layer down — *two homes for one fact* becomes *one number
standing in for a set*.

✅ **What the bare run got right**: it **failed**, loudly, and stopped the
manager mid-edit. ⭐ **That is `F130`'s repair working the first time it was
tested by something real** — an opt-in ratchet would have said nothing.

⛔ **THE RESIDUE, NOT REPAIRED AND DELIBERATELY NOT REGEX-TUNED:** the three
instances all turn on `BASE`'s or `XLANG`'s **spelling** meeting a paragraph
boundary. **Widening either is open item 134, which `_059` ruled on** — and its
ruling is **REFUSE the widening as framed**, so this is not solved by a better
pattern. ▶ **It is solved by diffing the set, which is now one command.**

### F131 — ⛔⛔⛔ **THE TABLE THAT GOVERNS THE AUTHORITATIVE LAYER LISTED SIX FINDINGS AS *BOTH* UNREVIEWED *AND* VERDICTED, AND THE BACKLOG WAS NOT COUNTABLE FROM THE COLUMN THAT CARRIES IT**

⚠ **Manager, 2026-09-15, found while writing the brief for `TASK_PHP_059` — the
review round this very table scopes. UNREVIEWED, and it is a manager self-finding
about a manager artefact, so law 12 cuts the usual way.**

`RECAP_PHP.md`'s **RULE-9 STATE** block is the index of which findings have
survived an engineer→reviewer cycle. `PROTOCOL.md` rule 9: **nothing reaches
`.memory-php/` until it does.** ⭐ The block exists because that state was once
living in gitignored scratch, and its own preamble says *"`grep -c UNREVIEWED` is
NOT an index — it cannot tell a closed cycle from an open one. **This table
can.**"*

#### ⛔⛔ (1) SIX KEYS HAD TWO ROWS

**`F120`, `F121`, `F122`, `F123`, `F124` and `F125` each appeared TWICE in one
table** — as `⛔ UNREVIEWED` in the rows that opened them (2026-09-15, manager),
and as `✅ UPHELD` / `⚠ UPHELD-NARROWED` in the rows `TASK_PHP_057` added
underneath. Both sets were unstruck, undated relative to each other, and
adjacent.

⭐⭐ **THE MECHANISM, AND IT IS WHY THIS KEEPS HAPPENING: `_057` verdicted a
BATCH, and the batch was APPENDED to the bottom of the table instead of APPLIED
to the rows at the top.** That is **item 73** exactly — *a correction appended
instead of applied* — **in the block whose own preamble cites item 73.**

⚠ **FOURTH INSTANCE OF A DOCUMENTED CLASS, AND THE FIRST AT SCALE.** The
preamble records three: 2026-09-14 (`F110`/`F111`/`F112` listed UNREVIEWED while
the prose below said `_053` had closed them), and 2026-09-15 twice (the `_047`
row's *"F96 STILL UNREVIEWED"*, and `F113`). ⛔ **Each of those was ONE row and
was repaired by STRIKING. This was SIX**, and striking six would have doubled the
table to preserve nothing — so they are **MERGED**: one row per finding carrying
the opening date, the verdict, and whatever the opening row asked that is **still
live**.

> ⭐⭐⭐ **THE TABLE CONTAINED THE SENTENCE THAT DIAGNOSES IT.** `F96`'s own cell
> reads *"the table's one-cell-per-finding shape is what forced the mis-filing"*
> — and that sentence sat in the table while **six keys had two rows.** ▶ **The
> repair is the SHAPE, not the six rows: this is an INDEX, and an index has one
> row per key. A verdict must REPLACE the row it verdicts, never be added below
> it.**

#### ⭐⭐ (2) AND THE BACKLOG WAS NOT COUNTABLE FROM THE COLUMN THAT CARRIES IT

`F128`'s verdict cell read **"⚠ UPHELD-NARROWED BY ITS OWN SWEEP, SAME DAY"**.
⛔ **That is the manager narrowing the manager — and it SCANS as a verdict.** A
reader counting open cycles off the verdict column got **three**; the START HERE
box said **four**; and eight lines below the table a closing line said
**"Backlog is 3"**, written before `F130` landed and never extended — **so the
⭐⭐⭐ finding in the queue was missing from the queue's own scope line.**

✅ **Repaired**: `F128`'s cell now opens `⛔ UNREVIEWED` and says why in the same
breath; **no count literal survives anywhere in the block**; the backlog is
defined as *the rows whose verdict column opens `⛔ UNREVIEWED`*, which today
reads off as `F127`, `F128`, `F129`, `F130`.

⭐ **A verdict-shaped phrase in a verdict column is a verdict, whoever wrote it.**
`.memory-php/04-process.md` **law 12** says a manager finding is worth less than a
reviewer's until a reviewer has had it — ▶ **and a table that records
self-narrowing in the same column as review outcomes erases exactly that
distinction.**

#### ⓘ (3) A THIRD, SMALLER LIMB — TWO HOMES FOR ONE FACT

The block carried the backlog trend **twice**: `14 → 2 → 7 → 1 → 4 → 2 → 6 → 13 → 1`
and, eight lines lower, `14 → 2 → 7 → 1`. ⭐ **A truncated series is worse than a
wrong one — it reads as complete, and a reader who scrolls to the nearest copy
gets the oldest.** Struck in place.

> ⭐⭐⭐ **THE SINGLE LESSON, AND IT IS THE SAME ONE IN ALL THREE LIMBS: TWO HOMES
> FOR ONE FACT.** Six findings with two rows; one backlog with two counts; one
> trend with two copies. ⛔ **Every rot this document has suffered this week is
> that shape**, and the cheap test is not *"is this true?"* but ***"is this the
> only place that says it?"***

### F130 — ⭐⭐⭐ **A RATCHET THAT NOTHING EVER INVOKED. `cbaseline_check.py`'s ENFORCEMENT WAS GATED ON A FLAG NO CALLER PASSED, AND THE CORPUS HAD ALREADY DRIFTED PAST IT**

⚠ **Manager, 2026-09-15, found while sweeping item 130. UNREVIEWED.**

`cbaseline_check.py` is `F108`'s enforcer: *every cross-language percentage must
name which C compiler*. Its hit count is a **ratchet** — the house pattern, and
the one `.tasks-php/README.md` calls *"the ratchet"* in terms: **adjudicate every
hit BY HAND with a reason; never tune the regex.**

⛔⛔⛔ ~~**Its enforcement sat behind `if '--ratchet' in argv`, and NOTHING PASSED
IT.**~~ **REFUTED AT `TASK_PHP_059`. IT WAS INVOKED — BY HAND, BY NAME, AND
THERE IS A REPORT OF THE OUTPUT.** `TASK_PHP_051.md` and `TASK_PHP_052.md` both
instruct the flag by name, and **`TASK_PHP_051_REPORT.md:55` records the run**:
*"`--ratchet` | rc 0 — 68 hits, ratchet 69"*, with the agent at `:60` declining
the tool's *"lower RATCHET to 68"* advice **and giving a reason.** ⛔ **I wrote
*"NOTHING PASSED IT"* without grepping the task files for the flag** — the
cheapest possible check, on the load-bearing word of my own headline.

✅ **THE CLAIM THAT SURVIVES IS NARROWER AND STILL WORTH HAVING:** *no
**AUTOMATED** caller passed the flag.* `checkers.py` files the tool with
`argv=[]` and a `--selftest` arm; the sweep runs both; **neither enforces** — so
enforcement depended on **a task file remembering to ask**, and **after `_052` no
task file did.** ⭐ **Measured against `1cc2c0e`, before this session touched
anything: 70 hits against a ratchet of 69** — independently reproduced by the
reviewer, who materialised the 31 scanned files with `git show` and ran the
`1cc2c0e` copy of the tool against them (and got **69/69** at the two commits
before).

⭐⭐ **AND IT IS A BIRTH DEFECT, NOT A REGRESSION.** The guard is present in the
file's **first commit** (`9313449`, `_049`, `RATCHET = 63`) and in every commit
until `d9652b4`. **Nothing unwired it; it was never wired.** ⓘ **The un-enforced
window is about 32 hours and three commits, not the open-ended stretch this
finding's tone implied** — and the ratchet was raised by hand, with
adjudications, **twice inside that window** (63 → 66 → 69). ▶ **A tone is a
claim too.**

> ⭐⭐ **A RATCHET YOU MUST OPT INTO IS NOT A RATCHET.** ▶ The **bare** run now
> enforces; `--ratchet` survives as an accepted no-op for old callers.
> ✅ **Demonstrated failing**: with the baseline lowered by one, the bare run
> returns `1` and prints `RATCHET FAIL: 77 hits > 76`.

⛔⛔ **AND THE REGISTRY ENTRY'S OWN CAUTION NAMED THE WRONG FLAG.** It read
*"a bare run REPORTS and does not check — the sweep must run the flag arm too"*,
and **the flag arm it means is `--selftest`**, which tests the arms, not the
ratchet. ⭐ **The entry was right that something was un-run and wrong about
what.** ⓘ It also carried `RATCHET=69` as a literal — **item 73's class, in a
registry entry about a ratchet.** The count is now stated nowhere but in the
tool.

#### ✅ THE EIGHT NEW HITS, ADJUDICATED BY HAND — **ALL BENIGN, AND TWO INFORMATIVE**

All eight are `_058`'s new `inside_share` sections (`ph03` +3, `ph16` +2, `ph29`
+2, `ph97` +1; `RECAP_PHP.md` went 35 → 34, so eight arrived and one left). Five
are share LEVELS or ranges rather than cross-language magnitudes, an `R1`-vs-`R1h`
line (C against C, same compiler), and a markdown table header. The two that
matter:

* ⭐ **`ph29` NOTES 1145 quotes the defective `RECAP` sentence IN ORDER TO
  CRITICISE IT** — a quotation of a defect scoring as the defect. **Item 115's
  class — *a check that reads prose and calls it code* — seventh instance.**
* ⭐⭐ **`ph29` NOTES 1157 names BOTH columns and is flagged anyway**, because it
  writes them `gcc-C` / `clang-C` while `BASE` matches only `c-gcc` / `c-clang`.
  ⛔ **The checker flags the one line in the corpus that obeys its rule BEST,
  because of a spelling.** `F10`: *a grep has a spelling.* **Eighth
  bare-spelling instance — and the first that cuts in this direction**, which is
  the case the standing note *"still not widening `BASE`"* never considered.

⛔ ~~**ONE of the 70 hits at `1cc2c0e` was ALREADY unadjudicated and is NOT
attributed** — it predates this session and I did not chase it. **Said rather
than smoothed over: the ratchet is honest again from 77, not
retrospectively.**~~

✅✅ **CHASED AND FOUND AT `TASK_PHP_059`, AND IT IS BENIGN.** Diffing the hit
sets by **unit text** rather than line number (`42d66e9` → `1cc2c0e`: NEW 2,
GONE 1, net +1) — one "new" was the `RECAP_PHP.md` **Index** unit merely
shifting. The real arrival is **`RECAP_PHP.md:1812` at `1cc2c0e`: the body of
`F127` itself**, the paragraph that quotes the defective *"+33 % dearer"*
sentence **in order to criticise it**. ⭐ **Adjudication: BENIGN, item 115's
class — a quotation of a defect scoring as the defect — and it is the SAME class
I adjudicated one hit later without noticing it was the eighth instance, not the
seventh.** ▶ **So the ratchet is honest retrospectively too**, and the hedge
above is withdrawn.

ⓘ **One accounting note the reviewer added.** *"`RECAP_PHP.md` went 35 → 34, so
eight arrived and one left"* is arithmetically right, but **the departure is a
checker artefact, not a repair**: the Index unit stopped hitting because a later
finding title added the literal `c-gcc` to it, so `BASE` now matches. ⭐ **The
ratchet absorbed one new hit under cover of an accidental departure** — which is
the one way a net count can hide a real arrival.

### F129 — ⭐⭐⭐ **TWO DIFFERENT QUANTITIES ARE CALLED `inside_share`, NO DOCUMENT SAID SO, AND THE PROGRAMME'S MOST-CITED NUMBER FLIPS SIGN BETWEEN THE TWO C COMPILERS**

`TASK_PHP_058`, the engineer task item 127 dispatched. ⚠ **UNREVIEWED.** Four
rows re-gated PASS. ✅ **Every load-bearing number below was re-derived by the
manager from the committed records with independent code before landing** — the
task's own tooling was not trusted for any of them.

#### ⭐⭐⭐ (1) THE NAME COLLISION

| | definition | on `ph29` `c-gcc`/`small.bin` |
|---|---|---|
| **`F74`'s** | `(kernel_exclusive_ir / n_iters) / marginal_ir_per_call` | **0.8045** |
| **the control's `W`** | `kernel exclusive Ir / callgrind whole-run total Ir` | **0.8933** |

⛔⛔⛔ **THIS PARAGRAPH SAID *"EVERY `inside_share` FIGURE IN `RECAP_PHP.md`, IN
`.memory-php/03-numbers.md` AND IN `ph29`'s `controls/spellings.py` IS `F74`'s"*,
AND IT IS FALSE IN THE FIRST TWO. `TASK_PHP_059` REFUTED IT WITH TWO
COUNTEREXAMPLES.**

* **`RECAP_PHP.md`'s own *which statistic* cell** publishes `ph97`'s
  *"`inside_share` 98.84 % → 64.50 %"*. Those are `inside_share_pct`
  **98.83845934798373** and **64.50051970182074** out of that row's
  `controls/libc_compare.json` — **the `W` quantity.** Searched at ±0.0005 over
  **every computable cell of every built row**, both return **0 hits** under
  `F74`'s definition.
* ⭐⭐ **`.memory-php/03-numbers.md` itself** — the file whose preamble box says
  *"EVERY FIGURE IN THIS FILE IS THE FIRST ONE"* — gives `ph52` at *"22.24 % on
  its C rungs … ≈98.6 % on its Rust rungs (`unsafe` A1 48,846,257 against W1
  49,549,469)"*, **and that parenthesis spells out the `W` arithmetic.** Under
  `F74` the same row reads `0.9892`–`0.9970` and `0.2023`–`0.2269`.

⭐⭐⭐ **SO THE FINDING GETS WORSE, NOT SMALLER: the two quantities are not
*separated* between documents — they are INTERLEAVED INSIDE SINGLE SENTENCES of
the authoritative layer and of this file, with no marker.** ⛔ **And the
`⛔⛔⛔ READ THIS BEFORE ANY inside_share FIGURE BELOW` box that `F129` put at the
head of `.memory-php/03-numbers.md` was therefore factually wrong about the file
it heads.** ✅ Repaired there and here.

⭐ **`cbaseline_check.py`'s hand ledger had already recorded half of it** — it
files `03-numbers.md`'s `ph52` line with the note *"the four C cells actually
span 20.23–22.69 %"*, **which is the `F74` span**. The discrepancy was written
down and nobody read it as a definition mismatch.

⚠ **The DEFINITIONAL half is upheld and UNDER-STATED**: the gap is **8.9 pp on
`ph29`** and **0.01 pp on `ph45`** (reviewer's own `callgrind` run). ▶ **It is a
measurement, never a constant** — which is what the layer already says about
`inside_share` itself. ⓘ `F129` picked the one row where the two nearly agree.

⛔ **FOURTH INSTANCE THIS SESSION OF A REPAIR CARRYING ITS OWN TARGET**, and this
one is the sharpest: the false sentence ships **inside the four-row control whose
entire purpose is to stop the two quantities being confused.**

⭐ **The tell was in the authoritative layer all along**: `.memory-php/03-numbers.md`
says `inside_share` *"IS ALREADY COMPUTED FOR EVERY CELL IN EVERY RECORD"* — which
is true of **F74's** (it is arithmetic over two committed records) and **false of
the control's** (it needs a callgrind run). ⛔⛔ **That is `F88`'s own rule —
*name the denominator* — broken by the quantity `F88`'s neighbours are measured
in, inside the document that states `F88`.**

⚠⚠ **AND `F74`'s EXCEEDS `1.0` ON 15 OF 360 CORPUS CELLS** (`ph07` `c-gcc`/`large`
at `1.0353` is the largest; ✅ manager-reproduced, exactly 15). **A share of the
whole cannot exceed the whole.** The proposed mechanism — a numerator over
`n_iters` calls against a denominator that is a *slope* at `collapse.probe_iters`
— is **consistent with the arithmetic and NOT isolated**; it could equally be a
start-of-run transient (`F93`'s shape). ⛔ **Do not quote the mechanism as
measured.** ⭐ **A quantity that exceeds 1 on 4 % of cells is being used to
decide which statistic may publish.**

#### ⭐⭐⭐ (2) THE `+33 %` HAS A THIRD MOVER AND IT FLIPS THE SIGN

On `ph29`/`large.bin`/`O3`/`isolated`, A1 against `safe_naive`, **manager-recomputed
from `results-php/ph29-recvfrom-alloc.json` and the gate record**:

| | A1 vs `safe_naive` | ⛔ **family B** (labelled *"W1"* here until `_059`) | ✅ the REAL W1 |
|---|---|---|---|
| **`c-gcc`** | **`+33.01 %`** | `−0.80 %` | **`−1.1881 %`** |
| **`c-clang`** | **`−4.36 %`** | `−27.54 %` | **`−27.6121 %`** |

> ⛔ **THE THIRD COLUMN'S HEADER WAS WRONG AND IS CORRECTED IN PLACE** (`_059`
> §1.2). Those numbers are **family B** (`marginal_ir_per_call`), not **W1**
> (program totals / `n_iters`). ⭐ **The verdict does not move** — every column
> still says C is cheaper where A1 says it is `+33 %` dearer — **but a finding
> whose whole subject is that a number owes its STATISTIC must not misname one
> of its own.** ⓘ The real `c-clang` W1 is already published in
> `.memory-php/02-ladder.md`; this table did not inherit it either.

⛔⛔⛔ **The published sentence is `c-gcc`'s. The other C column says C is
CHEAPER, and the whole-program statistic says C is cheaper on BOTH.** ⚠ The input
moves it too (`small.bin`: `+39.92 %`). ⓘ **The `+33.01 %` is not false** — it
reproduces to the digit. **It was never labelled.**

> ⛔⛔ **CORRECTED BY THE MANAGER THE SAME DAY, BEFORE ANY REVIEWER SAW IT — AND
> THE CORRECTION MAKES THE FINDING SHARPER, NOT WEAKER.** This section first
> presented `c-clang`'s `−4.36 %` as a DISCOVERY. **It is not new.** `TASK_PHP_049`
> measured it on **2026-09-13** and filed it in **`.memory-php/02-ladder.md`** —
> which states the swap in full (*"A `−4.36 %`, C `−27.78 %`, W1 `−27.61 %`"*)
> and says in terms that *"A disagrees with three other statistics"* **is a
> `c-gcc` statement** — and in **this file's own item 111**.
>
> ⭐⭐⭐ **SO THE DEFECT WAS NEVER THAT THE SIGN FLIP WAS UNKNOWN. IT IS THAT A
> CORRECTION LANDED IN THE AUTHORITATIVE LAYER *AND* IN THIS FILE'S ITEMS TABLE,
> AND THE HEADLINE CELL EVERYONE ACTUALLY READS NEVER INHERITED IT** — for two
> days, in the same document, one section apart. ⚠ **That is open item 73's class
> running BACKWARDS**: the item warns that a correction can reach `RECAP_PHP.md`
> and not `.memory-php/`; here the layer was right and the SUMMARY was stale.
> ⛔ **And a summary is what gets quoted.**
>
> ⓘ **`CLAUDE.md` names this exact shape on the PAT side** — *"`RECAP_PAT.md`
> twice carried a figure the synthesis had corrected."* **Third instance, first
> on the php side.** ▶ ~~**What `F129` genuinely adds here is the ADMISSIBILITY
> verdict (§3), not the clang number.**~~ ⛔⛔ **STRUCK AT `_059`: THE
> ADMISSIBILITY VERDICT IS THE PART THAT DID NOT SURVIVE.** What `F129`
> genuinely adds is **(1) the name collision** — upheld and under-stated — and
> what it genuinely got wrong is **(1)'s corpus clause**, which is false.
> ⚠ **§2 also mislabels its own second column**: the table below heads it *"W1
> (whole-program marginal)"* and the numbers in it are **family B**. The real
> **W1** for that cell is **`−1.1881 %` (`c-gcc`) / `−27.6121 %` (`c-clang`)** —
> one of which `.memory-php/02-ladder.md` already publishes. ✅ **Corrected in
> the table itself.**

#### ⛔⛔ (3) — **THE ADMISSIBILITY VERDICT, REFUTED AT `TASK_PHP_059`**

> ⛔⛔⛔ **THE WORD *"INADMISSIBLE"* IS WITHDRAWN. `F129` §3 IS UPHELD-NARROWED.**
> The arithmetic is upheld (Δ `0.2355`, min-share `0.6911`, re-derived by an
> independent tool that shares no code with the one that produced it). **The
> INFERENCE is not.** `F74`'s two-condition bar is **not a gate**, and four
> documents say so: `.tasks-php/STATISTICS_001.md` §4 (*"reported beside them as
> the EXPLANATION, never as a gate"*), ⭐ **`.memory-php/02-ladder.md`, the
> authoritative layer** (*"NO FUNCTION OF THE SHARES CAN CERTIFY A AT ANY
> THRESHOLD"*), `.memory-php/03-numbers.md`'s `F109` (*"a high `inside_share` is
> NOT a certificate"*), and ⭐⭐ **the very `RECAP_PHP.md` cell that carried the
> *"inadmissible"* sentence** (*"explains a disagreement and never gates one"*).
>
> ⭐⭐⭐ **AND THE REVIEWER MEASURED A COUNTEREXAMPLE RATHER THAN ONLY CITING
> DOCUMENTS**, which is why this is a refutation and not a disagreement: on
> **`ph55` `c-gcc` vs `c-gcc-h`, `large.bin`, `O3`/`isolated`** — both C cells,
> **same compiler**, so `F108`'s fifth thing does not arise — shares `0.7417` /
> `0.7515` **pass (i) at any threshold ≤ 0.74 and (ii) at `|Δ| = 0.0098`, so the
> conjunction ADMITS the pair** — while **A1 reads exactly `+0.0000 %`** against a
> **`−1.2998 %` / 66.14 `Ir`/call** whole-program difference. ▶ ***A gate that
> passes its own documented counterexample is not a gate.***
>
> ✅ **WHAT REPLACES IT, AND IT IS THE SENTENCE TO QUOTE:** *on 71 of 88
> cross-language pairs the two cells' shares differ by more than `0.02`, so A1 and
> the whole-program column are in the regime where they are **expected to
> disagree** — a reason to publish BOTH columns labelled, and **not** a reason to
> withhold either.* ⚠ **And the rate is CONCENTRATED, which a percentage hides**:
> of the 17 cross-language pairs that pass (ii), **`ph16` alone supplies 8** and
> **six of eleven rows supply ZERO**.
>
> ⓘ **The manager's `P2` predicted exactly this and was the one prediction of
> five to survive as written — and it was the one marked *low confidence*,
> written against his own finding's strongest clause.**
>
> ⛔⛔⛔ **A FOURTH PLACE THE ANSWER ALREADY WAS — AND THIS ONE WAS ADDRESSED TO
> ME. FOUND IN THE PRE-COMPACT AUDIT, 2026-09-15.** `ph03`'s `NOTES.md` carries
> an **independent counterexample** to the gate reading, written by the engineer
> who built that row's share table: *"the null pair failing on `small.bin` is a
> fact about THE RULE, not about the row — `unsafe` vs `verus` is the one
> comparison whose true A1 difference is **known to be exactly 0**, and (ii)
> rejects it."* ⭐⭐ **A condition that rejects a KNOWN-ZERO pair and admits a
> KNOWN-BLIND one (`ph55`) is not a gate, and the row had half of that on file
> before `_059` measured the other half.**
>
> ⛔⛔ **It was routed to me for a ruling — *"reported, not repaired: whether
> `F74`'s rule should exempt an `identity`-pinned pair is the manager's to rule
> on"* — AND I DID NOT RULE. I then published *"inadmissible"*, which is the
> exact reading that paragraph is a counterexample to.** ▶ ⭐⭐⭐ **THE LAW THIS
> SHARPENS (`F123`): a question ROUTED TO THE MANAGER AND NEVER ANSWERED IS NOT
> NEUTRAL — it becomes a claim he is free to contradict without noticing.** An
> open question at least reads as open; an *unanswered* one reads as nothing at
> all. ⓘ **This is a concrete, dated instance for item 129's census, and it is
> the first one where the un-answered item would have PREVENTED a published
> error.** ✅ Ruled now, in place, in `ph03` §8's own paragraph, and `ph29`'s
> §15e gained the `§15f` ruling it asked for. Both rows re-gated PASS.

#### ✅ (3a) `ph29`'s DISCLAIMER IS RIGHT, AND IS ABOUT A DIFFERENT PAIR THAN THE HEADLINE

All four docstring numbers reproduce **exactly**, in **exactly one cell**
(`large.bin`/`O3`/`isolated`, `c-gcc`), under **F74's** definition and **in no
cell** under the control's: `safe_tuned` `0.6551` · `unsafe` `0.6690` · `c-gcc`
`0.9266` · (`c-clang` `0.9122`, which the docstring never named).

`.memory-php/02-ladder.md` states `F74`'s corrected **two-condition** bar — (i)
`min(inside_share)` HIGH **and** (ii) `|Δinside_share| ≤ 0.02`. **The disclaimed
pair's Δ is `0.2715`, 13× condition (ii).** ▶ **The disclaimer must NOT be
narrowed.** ⚠ **But the disclaimer stands on `F108`, not on the bar** — see (3).

⛔ **AND `RECAP_PHP.md` PUBLISHES A PAIR THE DISCLAIMER DOES NOT COVER**: the
docstring disclaims C vs **`safe_tuned`**; the headline compares C vs
**`safe_naive`** (Δ `0.2355`). ⭐ **One rung off — so for as long as the caveat
has been quoted, it has been guarding the wrong comparison, and the one actually
published exceeds the same condition.**

#### ⛔ (4) MY OWN PREDICTION `P5` WAS REFUTED, AND BY THE AUTHORITATIVE LAYER

I predicted *"the comparable-callee-share bar has no written definition anywhere
in this repo."* **It is written, in `.memory-php/02-ladder.md`, which SUPERSEDES
everything** — two conditions, (ii) pinned at `0.02`. ⛔ **I wrote that prediction
into a task file without grepping the layer that outranks me**, which is
`PROTOCOL.md` rule 14 again, by the manager, in the task testing rule 14.
⭐ **Half survives and is worth keeping**: condition (i)'s threshold is *"not
tuned and six rows cannot pin it"* — **there are eleven rows now**, so the sweep
that could pin it is cheap and owed (item 132).

#### ⛔ (4a) THE PREDICTION SCORE: ~~**ZERO OF FIVE SURVIVED AS WRITTEN**~~ → **TWO OF FIVE** (`_059`)

> ⛔⛔ **RE-SCORED BY THE REVIEWER, AND THE CORRECTION GOES AGAINST ME IN THE
> FLATTERING DIRECTION — WHICH IS WHY IT IS WORTH RECORDING.** *"Zero of five"*
> was **too harsh**, and it was too harsh for two specific, avoidable reasons:
> **(a)** two of the scorings crossed the `F74`/`W` **spellings** the finding was
> about, and **(b)** one prediction was scored against the **admissibility
> clause published in the same task** — which `_059` then withdrew.
> ▶ ⭐⭐ **THE METHOD RULE OUT OF IT: do not score a prediction against a finding
> published in the same task. The finding is not evidence yet; it is the thing
> under review, and scoring against it makes the task its own referee.**
> ⓘ **A self-flagellating score is still a wrong score**, and a round whose
> headline number is wrong in the self-critical direction is not more honest than
> one wrong the other way — it is differently wrong, and it invites exactly the
> over-correction the next reader makes.

**Three split, one refuted, one upheld-narrowed.** ⭐ **And the splits are the
informative ones, because in each the conclusion and the reason came apart in
OPPOSITE directions**: `P1`'s conclusion held while its cell was wrong
(`large.bin`, not `small.bin`); `P2`'s **reason** held — the two C columns do
differ and the docstring's figure is `c-gcc`'s alone — **while its conclusion
failed**, because `0.927` is nearer `0.9266` than the gap between the columns is.
⚠ **A right reason that does not entail its conclusion is the case this
programme's conclusion/reason split was built for, and it had not fired this way
before.** `P3` holds at `O3` (where every published figure lives) and collapses
at `O0` (`ph16` `c-gcc` reads `0.0418`).

#### ⛔ (5) AND THE REPAIR SHIPPED THE DEFECT IT REPAIRS

The new control's docstring introduced both quantities and then wrote *"the two
read **80.45 %** and **89.33 %**"* — **two bare numbers, unlabelled, in the one
sentence whose entire purpose is to stop two quantities being confused**, in the
order a reader would most likely map them **backwards**. ⭐ Caught only because
the manager re-derived both from the records rather than reading them.
▶ **Repaired in all four rows (the file is byte-identical across them, one
`sha256`) and re-gated.** ⓘ **Third instance this session of a repair carrying
its own target** (`F122`, `F127`, this).

### F128 — ⭐⭐ **A SECOND ARM ASSERTED AN EFFECT'S *SIGN*, AND THIS ONE WAS LEGIBLE BEFORE THE REFUTATION: ITS COMMENT NAMED ONE BOUND WHILE ITS PREDICATE ASSERTED TWO**

⚠ **Found by the manager, 2026-09-15, while classifying `TASK_PHP_058` in
`task_cost.py`. UNREVIEWED.** It is a self-finding, so `PROTOCOL.md` law 12 cuts
the usual way: it is worth less than a reviewer's until a reviewer sees it.

**What fired.** `N13` read

```
check("N13", rowsum / len(ROWS) <= cmarg <= max(worsts), ...)
```

justified in its own message as *"an unsearched row can only make the all-rows
figure LOOK cheaper, never dearer."* ⛔ **That is a claim about the SIGN of a
difference, and it is false.** Charging `_058` at `1/3` each to `ph03`, `ph16`
and `ph29` — following `_028`'s precedent, the same three rows — put cost on
`ph03`, which is **unsearched**, and the ordering inverted: **all-rows `2.55`,
searched-only `2.54`.** The arm reported the ledger as the failure.

⭐ **An unsearched row is not an intrinsically CHEAP row.** It is a row missing
**one kind** of task. Any other task charged to it raises the all-rows figure
above the searched-only one, and nothing forbids that.

⭐⭐ **THE PART WORTH KEEPING IS THAT IT WAS VISIBLE WITHOUT THE DATA.** The
comment directly above the predicate said the arm existed so that *"the
searched-only marginal must not EXCEED the worst reading"* — **one bound.** The
predicate asserted **two**. The second bound had no stated justification anywhere;
it was reasoning that went into the code and never into the prose, which is the
opposite of the failure this programme usually catches.

> ▶ **THE RULE: when a check's prose and its predicate disagree about HOW MANY
> conditions there are, the extra condition is where the unmeasured assumption
> is.** ⭐ This is cheaper than every other way we have found these — it needs no
> measurement, no second opinion and no refuting datum, only reading the two
> together. ⚠ **It is a hypothesis from n = 1 and is written as one.**

**Relation to `F126`/`N11`.** `N11` asserted the first-in-family premium's
direction and so reported the measured openers (cheaper, not dearer) as a
failure. `N13` is the same defect in the same file, found eight days later by a
different route. ⛔ **`F126`'s repair fixed `N11` and did not ask whether any
OTHER arm asserted a direction** — which is the *"fixed one limb"* class (`F122`,
`F127`) appearing for the third time, now in the repair of a finding ABOUT
incomplete repairs.

▶ **Repaired the way `N11` was**: `N13` now asserts only the bound its comment
justifies, and an `N13b` **`ⓘ` REPORT** prints the ordering and says in terms
that the sign is not asserted and neither ordering is evidence. ⚠ **A report, not
a verdict** — `quota.py`'s discipline, and the reason `N15b` exists. ✅ `N12`'s
arm-count derivation confirms the file still claims 16 arms and prints 16: an
`ⓘ` report correctly does not count as one.

✅✅ **SWEPT THE SAME DAY — see item 130 for the result, which NARROWED THIS
FINDING'S OWN RULE.** A third direction-asserting arm was found (`N5`, same
file), **five arms were cleared as legitimately directional** (they defend a
published finding and print the margin), and **F128's rule as first worded is
WITHDRAWN as too broad.**

> ⛔⛔ **AND THIS PARAGRAPH SAID *"NOT SWEPT … unmeasured"* FOR THE REST OF THE
> SESSION AFTER THE SWEEP HAD RUN AND BEEN WRITTEN UP IN ITEM 130.** It also
> carried *"`checkers.py` registers 22 checkers"* when the registry held 24.
> ⭐⭐ **That is `F129`'s OWN defect, committed by me, in the same file, within
> the hour of publishing it**: a correction landed in one place and the other
> place that states the same thing never inherited it. ▶ **Caught by the
> pre-compact audit, which is the third consecutive audit to find the same
> class.** ⓘ The counts are now stated nowhere but in the tools.

### F127 — ⭐⭐⭐ **THE SEVENTH CONSECUTIVE ROUND, AND ITS BIGGEST RESULT IS NOT ONE OF THE THIRTEEN FINDINGS: FIVE BUILT ROWS NEVER MEASURED `inside_share`, AND THREE OF THEM PUBLISH AN `A1` HEADLINE**

`TASK_PHP_057`, 1112 lines, **reached every section**. ⚠ **UNREVIEWED.**
Brackets `66/0` and `24/0`, first and last, unmoved.

⛔⛔⛔ **THE TASK FILE ASSERTED *"`inside_share` is in every row's `controls/`
already"* AND IT IS IN ONE.** ✅ **Manager-verified across all eleven built
rows**: `ph97` has a dedicated control; `ph29`, `ph45`, `ph52`, `ph55`, `ph56`
carry a value somewhere; and **`ph03`, `ph07`, `ph16`, `ph53`, `ph64` have none
at all.** ⭐⭐ **Three of the rows with no measured `inside_share` publish an
`A1` headline.**

⭐⭐⭐ **AND `ph29` IS WORSE THAN MISSING.** Its only figures — `0.655 / 0.669`
for R3-vs-R4 and `0.927 / 0.655` for C-vs-Rust — live **in a Python docstring in
`controls/spellings.py`**, and **that docstring says in terms that A1 is NOT
right for this row's C-vs-Rust column and *"that comparison is not made here"*.**
⛔ **It is made elsewhere**: this file's *which statistic* cell publishes
*"on `ph29/large` A says C is +33 % dearer than naive safe Rust"* — **the exact
comparison the row's own control disclaims**, on the row at the centre of the
programme's largest open thread.

> ⚠⚠ **CORRECTED 2026-09-15 BY `F129` — *"the EXACT comparison"* IS ONE RUNG OFF
> AND THE TRUTH IS WORSE.** The docstring disclaims C vs **`safe_tuned`**
> (Δshare `0.2715`); the cell publishes C vs **`safe_naive`** (Δ `0.2355`).
> ⛔ **So the caveat everyone has been quoting was guarding a DIFFERENT PAIR than
> the one published** — and the published pair **exceeds `F74`'s `≤ 0.02`
> condition (ii) by more than eleven times too.** ⭐ **The conclusion survives and
> strengthens; the identity claim in its reason does not.** ⓘ Seventh round in
> a row in which a conclusion outlived its stated reason.
>
> > ⛔⛔ **AND THIS BOX SAID *"SO IT IS INADMISSIBLE ON THE ROW'S OWN RULE"*.
> > WITHDRAWN AT `TASK_PHP_059`.** `F74`'s bar is **not a gate** — four documents
> > say so, including `.memory-php/02-ladder.md` and the `RECAP_PHP.md` cell this
> > box is about. ▶ **What is left is `F108`, and it is enough**: the sentence
> > names one C compiler of a pair whose columns have **opposite signs**.
> > ⭐ **`F127` should be re-stated on `F108`, not on `F74`'s bar** — its
> > conclusion needs no bar at all (`_059` §3). ⓘ **A correction written into a
> > correction box, two rounds running, and the second one withdrew the first.**

▶ ✅ **ACTIONED: `TASK_PHP_058` measured `ph03`, `ph16` and `ph29` and rewrote
`ph97`'s template; four rows re-gated PASS. ⛔ It did NOT close item 127 —
`ph07`, `ph53` and `ph64` still have none. And it produced `F129`, which is
larger than this finding was.**

### ⭐⭐ THE ROUND'S SCORE — CONCLUSION AND REASON, SEPARATELY

**Sixteen entries verdicted. THREE had both halves cleanly upheld** (`F115`,
`F117`, `F121`). ⭐ **`F123` is UPHELD AND UNDER-STATED.** Everything else split.

| | |
|---|---|
| ⛔ **REASON refuted, conclusion survived** | `F116` (its evidence is **not** re-derivable — log *and* generator gitignored, **4th instance**), `F118`, `F119`, `F124`, `F125`, `F126`, `F96 R4` |
| ⚠ **narrowed** | `F114`, `F120`, `F122`, `F96 R2` |
| ⛔ **conclusion refuted** | `F96 R5` — the prediction stands and *"half-refuted"* over-claimed |

⭐⭐ **SEVENTH CONSECUTIVE ROUND.** The pattern is now beyond doubt and is the
strongest evidence on file for `04-process.md` law 12: **a conclusion reached by
a manager or an engineer tends to survive; the REASON given for it tends not
to.**

### ⛔⛔ FOUR THINGS IT FOUND IN MY OWN REPAIRS, ALL FROM TODAY

1. ⛔⛔ **`F122`'s repair FIXED ONE LIMB OF ITS OWN MECHANISM.** I widened
   `benign()` to accept split report names and **left `LIVE`/`HIST` on
   `endswith('_REPORT.md')`** — so a split-named report was benign in one half
   and a **live doc** in the other. ⭐ **SIX reports on the wrong side**, not the
   three I would have guessed. **`N6a`/`N6b`/`N6c` all passed throughout,
   because every one tests `benign()` and none tests the PARTITION.**
   ✅ **Repaired: one predicate, one place, plus `N6d` which asserts the two
   halves AGREE.** ▶ ⭐ **THE LESSON: when a repair has two limbs, the arm must
   assert they agree, not that each works.**
2. ⛔⛔ **THE BUILD LABEL WAS WRONG IN FOUR PLACES** — I wrote
   `-O3 -march=native -flto` and **the measured binary is `-O0`**; those flags
   belong to the sibling `-O3lto`/`-maxlto` variants, which carry `.buildinfo`
   files the plain one does not. ⭐⭐ **The caution whose entire point is *say
   which build* named the wrong build.** ✅ **Corrected in `§A3a`, `F120` and
   `segaddr.c`.** ⓘ **Measured on all three tiers: `si_code=1 si_addr=(nil)`
   rc `139` on each, so nothing downstream moved** — *luck, not a reason to
   relax the rule.*
3. ⛔ **`F126`'s published range was stale within the hour** (above).
4. ⛔ **`F124`'s `P1` priced the discriminant TEST, not the discriminant**
   (above).

### ⭐⭐⭐ AND THE FIFTH OBLIGATION IS NOW *REQUIRED*, BECAUSE THE COST IS **30 SECONDS**

The reviewer **ran the hardened build end to end**, and ✅ **the manager
reproduced it**: **cold build 30 s · incremental rebuild after the R1h patch
683 ms · 60 MB · no sudo · no network**; pristine `rc 139` → post-image `rc 0`.

⛔⛔ **SO MY SECOND REASON FOR OMITTING IT WAS AS WRONG AS MY FIRST.** *"Requiring
it makes every row pay for a full PHP compile"* does not survive `30 s`.
⭐ **`F123` is therefore UPHELD AND UNDER-STATED: the engineer's *"cheapest
remaining check"* was not merely defensible, it was an UNDER-STATEMENT** — and
`_057` rules my §1.2a question 1 decidable and answers **NO, the demotion was
not justified**, because *`PROTOCOL.md` rule 14 is run the premise before you
write it into a task file.*

✅ **LANDED: `§A3a` obligation 5 is REQUIRED**, gated on *"the pre-image run
faulted"*, **with the measured cost written into the section so nobody re-derives
it as impossible a third time**, and the generator committed at
`.tasks-php/probes/rebuild_hardened_php.sh`.

⭐ **`§A3a` also gained the obligation NOBODY had thought of: REPEAT THE RUN.**
`ph75`'s trigger returns **`SIGABRT`, `SIGSEGV` or exit `255` depending on the
run**, and `ph79`'s `si_addr` took **four different values in four runs** while
`ph97`'s is `(nil)` every time. **§A3a said *record the exit status* once.**

### ⛔ `F119` MUST BE RE-STATED ON ITS REAL EVIDENCE — AND THE REAL ONE IS STRONGER

`F119`'s conclusion is **UPHELD and UNDER-STATED** (96 cells = 48 `isolated` +
48 `whole`, three draws, bit-identical, md5 reproduced by an independently
chosen recipe). ⛔ **Its REASON is refuted and it is a category error:** the
mechanism *"100 % of the ±7 swing is inside a libc `memset` callee, which
`kernel_exclusive_ir` excludes structurally"* is a claim about **A1**, while
**48 of the 96 cells are the `whole` column, which that immunity cannot
protect.** ▶ **The finding explains the stability of column Y with the immunity
of column X.**

⛔⛔ **AND THE `memset` FACT IS ANOTHER PATTERN'S.** `ph53`'s own `NOTES.md` §8b
says its `memset` of `8·n_decl ≤ 128` bytes is **inlined to `xmm` stores — inside
`kernel`, not a libc callee at all.** The `__memset_avx2_unaligned_erms`
measurement in the layer is a **`p03`, PAT-side** fact.

⚠⚠ **AND THE RECORD'S OWN `domain` FIELD FORBIDS THE COMPARISON F119 MAKES** —
*"comparable ONLY against a record with the same `envp_stack_bytes`"*, and F119
compares across three different values. ⭐ **The honest reading is stronger: the
±7 term did not fire on this row at all, on three draws, INCLUDING in the column
that is supposed to be vulnerable — so the `domain` guard is more conservative
than this row needs.** → item **128**.

### F126 — ⭐⭐⭐ **THE FIRST-IN-FAMILY PREMIUM IS REFUTED IN SIGN AT n = 8, AND THE ARM THAT SHOULD HAVE CAUGHT IT ASSERTED THE PREMIUM'S DIRECTION**

Manager, 2026-09-15, on `ph97` landing. ⚠ **UNREVIEWED.**

`task_cost.py` carried **`OPENER_RATE = 4.00`** — *"`ph64`'s cost charged what it
opened"*. Its comment said **`n = 1`** and said it honestly. **Nobody re-derived
it for ten rows**, and the published projection `~94–127, middle ~110` was built
on it. **Measured when `ph97` became the eighth first-in-family row:**

| | rate | n |
|---|---|---|
| **first-in-family** | **2.19** | 8 |
| follow-on | **3.17** | 3 |
| all-rows marginal | 2.45 | 11 |
| ⛔ **pinned `OPENER_RATE`** | **4.00** | **1** |

⭐⭐ **Openers are CHEAPER than follow-on rows — the opposite of the premium —
and `4.00` is nearly double the measured opener mean.**

⚠⚠ **TWO QUALIFICATIONS, BOTH HONEST, BOTH POINTING THE SAME WAY.** (a) `follow`
is `n = 3` and is dominated by **`ph07` at 5.50, the only REBUILT row**, named as
atypical by `N6`'s control *before* it ran; excluding it, follow-on is 2.00
against openers' 2.19, so openers are dearer by **0.19** — **either way `4.00` is
not supported**. (b) ⭐ **The ARGUMENT for 4.00 survives its own refutation and
must be stated: the per-row measure cannot see the methodology a row OPENS.**
That is a claim about the measure's blindness, so **no measurement can refute
it** — ⛔ **but it was applied to exactly ONE row and never again, and `ph97`
opened `T6` at 1.00 while spinning off no methodology at all. A credit granted
once is not a rate; it is an adjustment to one row's cell.**

⛔⛔ **AND THE REAL FINDING IS `N11`, WHICH IS WHY THIS IS NOT JUST A STALE
NUMBER.** `N11` asserted `marginal ≤ family-weighted ≤ worst` — **which can only
hold if openers are DEARER.** ⭐⭐ **The arm encoded the hypothesis it was
supposed to test, so when the data reversed, the arm reported the DATA as the
failure.** `.memory-php/04-process.md` **law 6 one level up: a bound is not a
derivation, and a bound whose DIRECTION is the hypothesis under test is not even
a bound.**

✅ **REPAIRED:** `opener_rate()` is derived from the build-order family split;
`N11` asserts containment **in whichever order the two rates fall**; **`N15`
fails if the rate is ever derived from fewer than 2 rows**; the pin survives
only so `N15b` can **report** the gap — and `N15b` is printed as an `ⓘ`, **not a
`check`, because the first draft wrote it as `check(cond or True)`, which prints
`PASS` while being unfalsifiable** — §H's own target.

▶ ⚠ **A PUBLISHED FIGURE MOVES.** ⛔⛔ **AND THE FIGURE I WROTE HERE WAS STALE
WITHIN THE HOUR — `TASK_PHP_057` CAUGHT IT.** I ran `task_cost.py`, wrote
`~70 .. ~92, middle ~73` into this file, **then changed the floor 40 → 37 and
never re-ran the report.** ⭐ **That is F119/M2's own rule — quote a re-gateable
reading as an EVENT, never a STATE — broken in the same commit whose trap line
carries it.**

▶ **AS AN EVENT: `~63 .. ~82, middle ~66`, as `python3 .tasks-php/task_cost.py`
printed at `af135f9`.** ⚠ **Do not quote it without re-running it.** The tool
prints what the old pin would have said beside it, so the change stays visible.

⛔ **AND MY SEPARABILITY CLAIM NAMED THE WRONG PAIR** (`_057` §4). I said the
fall was *floor* plus *`ph97` landing*; **there are THREE causes** — the opener
rate, the floor, and the row — and the tool separates a different pair than the
one I named. ▶ **A range that moved for three reasons is exactly what gets
quoted as one.**

ⓘ **`N9` — the arm whose entire purpose is to stop figures being pinned — turned
out to hardcode `40` itself.** **Eighth stale literal in a `.tasks-php/`
validator**, re-derived rather than re-pinned.

### F125 — ⭐⭐⭐ **`F119`'s STRUCTURAL EXCLUSION IS NOW *PRICED*, AND IT IS WORSE THAN `F119` SAID: `A1` CAN REPORT THE SIGN BACKWARDS**

`TASK_PHP_056`, `controls/libc_compare.json`. ⚠ **UNREVIEWED.**
✅ **Manager-verified from the control's own JSON**, not from the report.

`F119` established that `kernel_exclusive_ir` (**A1**) **excludes callee work
structurally**. `ph97`'s task asked for the cheap control that prices it: build
the row's ASCII compare **in the kernel** and **in libc**, and measure both.

| compare lives in | `kernel_exclusive_ir` (A1) | whole-program Ir | `inside_share` |
|---|---|---|---|
| **the kernel** | 38 881 170 | 39 338 098 | **98.84 %** |
| **libc** | 27 756 101 | 43 032 368 | **64.50 %** |

**Same checksum both ways** (`9594554053753204562`) — *the same computation, one
symbol boundary apart.*

⭐⭐⭐ **A1 reads the row `−28.61 %` CHEAPER while the program is `+9.39 %` MORE
EXPENSIVE. The statistic reports the SIGN BACKWARDS.**

▶ **Why this is bigger than one row.** The programme's largest open thread is
*which statistic* — **29 of 38 sign flips live in A1** (⛔ **`111 of 141` at 13 rows, 2026-09-17**), and `F91`/item 72's axis
says *"same-language differences are 1–2 instructions under 50–394× of callee
noise, so only A resolves them; cross-language the callee work IS the effect."*
⭐ **This measures the mechanism directly: A1's blindness is not noise, it is a
lever an implementation choice can pull**, and *"put the work in a callee"* is
not an exotic manoeuvre — **it is what calling libc means.**

⚠⚠ **WHAT IT DOES NOT SAY, and the row says so itself.** It does **not** show any
published figure is wrong: every php row measures a kernel that does its own
work, and `inside_share` is reported per cell precisely so a low one is visible.
⛔ **It shows the FAILURE MODE IS REACHABLE AND CHEAP, which nobody had priced.**
▶ **For the reviewer: does this change `F91`'s axis, or is it the same claim with
a number on it at last?**

### F124 — ⭐⭐⭐ **ROW 11 IS BUILT — `ph97`, `T6`'s FIRST — AND `P1` SURVIVES IN BOTH HALVES: THE SAFETY IS FREE *BY CONSTRUCTION***

`TASK_PHP_056`, 1106-line report, **one task, no resume**. ⚠ **UNREVIEWED.**
✅ **Manager-verified from `results-php/gate/ph97-optarg-unwritten.json`**:
`verdict PASS`, `failures []`, `blocked []`, `complete_run true`,
`contract_sha256 2814106af663…` **AS AT `af135f9`** (⚠ an **EVENT**, F119/M2).
Verus **47/0**, twin **54/0**, Miri clean, identity `norel` at both levels as
pinned. **Brackets `66/0` unmoved; `22/0` → `24/0`.**

⭐⭐ **`P1` HOLDS — NARROWED BY `_057`, AND THE NARROWING IS WORTH MORE THAN THE
HEADLINE.** ⛔ **The control priced the discriminant *TEST*, not the
discriminant**, and the `0.0000` is *stronger* than I wrote: the check is not
made cheap, **it is REMOVED** — a `cmp`+`jne` over 20 000 calls would have cost
40 000 `Ir` and the record shows none. ⛔ **And *"free by construction"* splits
in two**: the SIZE leg is by construction (`Option<&[u8;21]>` is **8 bytes** by
compile-time assertion — a niche optimisation, not a trade); the RUNTIME leg is
**by ELISION**, which is the optimiser's choice and not the type system's.
▶ **State both legs or state neither.** ⭐ **A prediction surviving is rare here
and is reported as plainly as a refutation — but *this* prediction survived on a
measurement of something adjacent to what it claimed.**

⛔ **AND THE ENGINEER REFUSED MY FALSIFIER, RIGHTLY.** I wrote *"any step
attributable to the discriminant"*; **a falsifier containing *"attributable to"*
is not falsifiable from a record.** The `R3 → R4` step is **−20.41 %** and is
**not** the discriminant — the row measured the discriminant directly instead, on
two binaries one function body apart.

**Three more, each a refutation:**

1. ⛔ **`P3`'s CONCLUSION survives and its MECHANISM is refuted** — the `I12/O3`
   obligation is **not** discharged from the parser's post-condition, because
   **that post-condition PROVES the pointer may be absent.** Measured both
   directions. ⭐ **Seventh consecutive round in which a conclusion outlived its
   reason.**
2. ⛔⛔ **A CONTROL REFUTED ITS OWN AUTHOR**: `unwrap_unchecked()` on `None`
   gives **abort at `-O0` and NON-TERMINATION at `-O1`+**, not a null read.
   ▶ ***Even unsafe Rust cannot reproduce this fault signature*** — a `CLAUDE.md`
   rule 6 finding, and a good one.
3. ⚠ **Check `R4`/`R5` identity at `O0` as well as `O3`**: `O3` read `exact`
   while `O0` differed by **144 instructions** from three real exec-text
   divergences the optimiser erased.

ⓘ **Agent C's `_054` caution answered**: `zend_API.c:527-534`'s argument-stack
check is **dead**, so the executor is not needed and the row does not drop
behind `ph60`. ⓘ **`§B5` is not owed** — no family-B figure is published, and the
row states that rather than claiming it cleared the sweep.

⚠ **Its own `§13` lists nine uncertainties.** The largest: **no disassembly
explains why `R3`'s iterator pipelines are `+23 %` over `R2`'s indexed loops** —
a cost with a hypothesis and no mechanism.

### F123 — ⛔⛔⛔ ***"PHP 5.0.0 CANNOT BE REBUILT ON THIS BOX"* IS FALSE, AND THE OBLIGATION IT EXCLUDED HAD ALREADY BEEN CALLED *"THE CHEAPEST REMAINING CHECK"* BY AN ENGINEER**

Manager, 2026-09-15, found while writing `TASK_PHP_057` §1.2. ⚠ **UNREVIEWED**,
and it is **a manager finding about the manager**.

I wrote `PROTOCOL_PHP.md` §A3a with **four** obligations and dropped a fifth —
***re-run the trigger against the R1h POST-IMAGE build***, which would make the
upstream fix's efficacy measurable on real PHP. **It is the most valuable one.**

⛔ **The reason I gave is false.** `php-in-safe-rust` ships a **tracked,
idempotent, documented** build script for PHP 5.0.0 that needs **no sudo and no
system install**, works around the absent `flex`/`bison` with a stub plus a
timestamp guard, and says in its own header *"Idempotent: CLEAN extract+build
each run; reuses the cached tarball."* ⭐ **Four 5.0.0 builds with four different
recorded `cflags` already sit on this box**, two carrying `.buildinfo` files.

### ⭐⭐⭐ THE FINDING IS THE CHAIN, NOT THE ERROR

| # | document | what it says |
|---|---|---|
| 1 | `TASK_PHP_051_REPORT.md` §8.1 — **the ENGINEER's own *"what I am unsure of"*** | *"I did not rebuild PHP 5.0.0 with the patch and re-run the six snippets … **It is the cheapest remaining check and it is not done.**"* |
| 2 | `TASK_PHP_052.md` §1.5 — **the MANAGER, next task** | *"⭐ **Nice to have, not owed. Skip it** rather than leave §1.1–1.4 unfinished."* |
| 3 | `TASK_PHP_054_REPORT_E5E6E7E8.md` — **a DIFFERENT agent, two rounds later** | *"**NOT MEASURED. I cannot rebuild PHP 5.0.0.**"* — meaning *not within this task* |
| 4 | `PROTOCOL_PHP.md` §A3a — **the MANAGER, today** | the obligation **absent**, reason given: **(3)** |

⛔⛔ **A CHECK AN ENGINEER CALLED *"THE CHEAPEST REMAINING"* BECAME, IN FOUR
STEPS, A THING THE PROTOCOL TREATS AS IMPOSSIBLE — AND NO STEP WAS A LIE.**

⭐⭐ **THE PROGRAMME'S CHARACTERISTIC FAILURE MODE, RUNNING BACKWARDS.** The
standing pattern is *a conclusion surviving while its reason dies*. Here a
**reason decayed** — *"I didn't"* → *"not owed"* → *"I can't"* → *"one can't"* —
**while the conclusion hardened into a protocol section.** `PROTOCOL.md` **rule
14** with the manager as the one who doubted too little, **one round after
landing `F120`, itself a rule I wrote about my own measurement.**

✅ **Checked: the false claim is in NO live manager document.** `TASK_PHP_056.md`
never carried it, **so the engineer building row 11 was not misled**, and §A3a is
**incomplete rather than wrong**.

▶ **NOT REPAIRED YET, DELIBERATELY.** `_057` §1.2 asks the reviewer whether the
fifth obligation should be **REQUIRED or merely PERMITTED** — **requiring it
makes every row pay for a full PHP compile, and §A3a's whole merit is being cheap
enough that nobody skips it.** ⛔ **I did not run the build either**: `_056` was
measuring instruction counts and a concurrent compile would have competed for the
machine. **That is the only reason and it is not evidence about the cost.**

⚠ **THE OPEN QUESTION I CANNOT ANSWER ABOUT MYSELF** → item **125**: *how many
other *"cheapest remaining check"* items sit in a `WHAT I AM UNSURE OF` section,
demoted once and never revisited?*

### F120 — ⭐⭐⭐ **CRITERION 2 IS *MEASURED*, FOR THE FIRST TIME IN ELEVEN ROWS — AND THE ROW ABOUT TO BE BUILT IS THE ONE THAT PROVES IT**

Manager, 2026-09-15, **before** `TASK_PHP_056` was written. ⚠ **UNREVIEWED**
(rule 9), and it is a manager finding from one probe — law 12 says assume it
narrowable. Nothing measured or re-gated; brackets `66/0` and `22/0` unmoved.

**F116 said the C-side bar *can* be measured. This is the first time anybody
did it.** On the oracle CLI (`php-in-safe-rust`'s build, mysql + webext, **`-O0`**
— **not** a museum-default one; ⛔ **this said `-O3 -march=native -flto` for one
day, which is the SIBLING variants' flags — F127**), under
`.tasks-php/probes/segaddr.c`:

| run | result |
|---|---|
| `mb_get_info()` — zero arguments, `ph97`'s `▸ trigger` | ⛔ **`SIG11 si_code=1 si_addr=(nil)`, exit `139`** |
| `mb_get_info("internal_encoding")` — the benign control, **same binary, same run** | ✅ `string(10) "ISO-8859-1"`, exit `0` |

⭐⭐ **`si_code=1` is `SEGV_MAPERR` and `si_addr=(nil)` is a dereference at
offset 0 — which is `strcasecmp("all", NULL)` reading its second operand's first
byte. The catalogue's harm claim, AT THE ADDRESS.** ⓘ The reachability chain is
verified at source too (`zend_API.c:485-487` makes `min_num_args = 0`, `:511`
passes, `:537` runs zero times), so **the measurement and the reading agree**,
which is what A4 asks for and what no previous row could offer.

✅ **And the R1h is verified end to end in the same sitting**: `f7326d627962`
binds to its own filename (**not** one of F115's three), `git apply --check`
succeeds at **offset −13**, and the applied post-image at `:3219` reads
`if (!typ || !strcasecmp("all", typ)) {`. **One file, one hunk, one line.**

▶ **WHAT CHANGED STRUCTURALLY: `PROTOCOL_PHP.md` §A3 gained §A3a**, which turns
*"reachability is deliverable #1, **in writing**"* into *"in writing **AND,
where a reproducer exists, EXECUTED**"* — four numbered obligations, the binary
named, the instrument committed. **Open item 120 CLOSED.**

⛔⛔ **THREE THINGS THIS DOES NOT DO, AND THEY ARE THE WHOLE DISCIPLINE:**

1. **It does not validate the ten rows built before it.** Their criterion 2 was
   argued. Re-running them is a separate cheap task — **item 120's residue**.
2. **It does not move the admission bar.** `CLAUDE.md` rule 6 is unchanged and
   ***"the reproducer did not fault" is NOT a kill***. F3 stands: a clean run is
   **not** evidence of absence. ⭐ **What is new is only the converse** — a run
   that faults, executed, is evidence of **presence**, which this programme has
   never had.
3. **It is a property of a BUILD.** A row must say which binary it measured on,
   and this one is not the museum default.

⚠ **The honest size of it**: this is one row, one trigger, one build, one
instrument, measured by the manager who chose the row. ▶ **The reviewer should
ask whether §A3a's four obligations are the right four, and whether a row that
*cannot* run its trigger (no CLI reproducer — most temporal rows) is now
implicitly second class. I do not think it is, but I wrote the rule.**

### F121 — ⛔⛔ **THE RATCHET'S OWN LAW HAD A HOLE ONE LEVEL UP: THE STRUCTURE CARRIED NO COUNT LITERAL AND THE *PROSE ABOUT THE STRUCTURE* CARRIED THREE**

Manager, 2026-09-15. ⚠ **UNREVIEWED.** No measurement, no re-gate.

`checkers.py`'s headline law is *"there is no `RATCHET` literal in this file, and
that is deliberate — **`REGISTRY` IS the ratchet**, and no count is written down
anywhere to go stale."* **Measured: three counts were written down, in the `why`
prose of that same registry and in the README describing it.**

| claim | reality | how it was found |
|---|---|---|
| `task_cost.py`'s `why`: *"15 arms"* | **14** | counted while adding `N14`; **the addition made it true by accident** |
| `cbaseline_check.py`'s `why`: *"9 arms"* | **10** (`N8b` was never counted) | the new `N12` arm, on its first run |
| `.tasks-php/README.md`: *"5 of the **14** checkers"* | **15**, the moment `probes/n14_mustfire.py` was filed | **created by the edit that fixed the first two** |

⛔⛔ **AND THE SECOND ONE HID A WORSE DEFECT THAN A WRONG NUMBER.**
`cbaseline_check.py` printed only `SELFTEST PASS (0 failures)` — **its ten arms
named themselves ONLY WHEN THEY FAILED.** ⭐⭐ **A checker whose arms are silent
on pass is indistinguishable from a checker with no arms**, so the `9` was not
merely wrong, it was **uncheckable**. That is F10's rule (`quota.py` prints
`VACUOUS TODAY` rather than passing silently) one level up, and it is why `N12c`
treats *"claims arms, prints none"* as its own failure mode.

✅ **REPAIRED, AND THE REPAIRS ARE DERIVATIONS, NOT BETTER NUMBERS:**

- ⭐ **`checkers.py` `N12`** — every `"<n> arms"` claim in a `why` is checked
  against **the arm names the checker prints when the sweep runs it**. Four
  must-fire arms (`N12a`–`N12d`), the last a MUST-NOT-FIRE so a `why` with no
  count stays legal. **It polices claims that exist; it does not mandate one.**
- ⭐ **`cbaseline_check.py` now prints `PASS N1 … PASS N9` and a derived
  `(10 arms, 0 failures)`**, with an assertion that no arm can report a failure
  without registering itself.
- ⭐ **The README's number was DELETED rather than corrected** — the tool prints
  it on every run.

⭐⭐ **A SECOND, INDEPENDENT BLIND SPOT FOUND IN THE SAME EDIT, AND IT IS F49's
SHAPE AGAIN.** `checkers.py`'s `_disk()` globbed `.tasks-php/*.py` only, so
`.tasks-php/probes/` was outside the ratchet entirely. **It agreed with the truth
for as long as `probes/` held nothing but C sources** — and `n14_mustfire.py` is
the first `.py` to land there, *with a standing verdict*. ▶ **Widened to include
`probes/*.py`, and the probe filed.** ⓘ **Item 114's exact sentence: a checker
can agree with the truth for a long time because the state that would separate
them has never occurred.**

⚠ **SEVEN hardcoded figures in `.tasks-php/` validators have now gone stale.**
The four already on file were in *code*; **these three were in prose about the
code**, which is the class the law did not cover. ▶ **`.memory-php/04-process.md`
law 6 should be read as covering both — but that is a LAYER edit and it is
UNREVIEWED, so it waits.**

### F122 — ⚠ **`F117`'s TRANSIENT HALF IS NARROWER THAN EVERY DOCUMENT SAID: ROT ROSE FOR A *SPLIT* REPORT NAME, NOT FOR AN IN-FLIGHT TASK**

Manager, 2026-09-15. ⚠ **UNREVIEWED.**

Four documents — `.tasks-php/README.md`, `checkers.py`'s registry entry, F117
itself and my own handoff — all say *"`rot` rises transiently per in-flight task,
because a task file cites its report before the report exists."* **`benign()`
whitelisted `endswith('_REPORT.md')` the whole time, so a task with a PLAIN
report never moved the count.**

⭐ **What moved it was the SPLIT naming.** `TASK_PHP_054` returned three reports
— `_REPORT_E2E3E4.md`, `_REPORT_E5E6E7E8.md`, `_REPORT_S4S5S6T2T4T6.md` — **none
of which ends in `_REPORT.md`.** That, and only that, is why rot read `1 → 4 → 1`.

✅ **MEASURED, not reasoned**: citing both spellings from the same live file, one
at a time, gives **rot 1** for `_REPORT.md` and **rot 2** for `_REPORT_A1A2.md`.

✅ **REPAIRED RATHER THAN DOCUMENTED**, because `.tasks-php/README.md` has stated
the exception in words since Phase 0 — *"Ignore a MISSING report for a task that
is still open"* — and the checker that replaced the grep simply never inherited
it. `benign()` now matches both spellings, with `N6a`/`N6b` must-fire and **`N6c`
MUST-NOT-FIRE so a missing task SPEC or row file is still rot** — the widening
must not swallow the checker.

⭐ **THIRD UN-INHERITED CAUTION, AND THE THIRD TO BE CLOSED.** F108's C-compiler
rule and `_env_block`'s three-equal-fields caution were the first two. ⚠ **The
rate is the finding, not the instance**: a caution written in a README does not
travel into the tool that replaces the README's procedure, and nothing checks
that it did.

⚠⚠ **WHAT DID NOT CHANGE: still read `citecheck`'s COUNT, never its exit code.**
The one standing rot is an adjudicated false positive (`TASK_PHP_005/006/008_REPORT`,
three files written as one path, inside a paragraph headed *"NAME COLLISION, DO
NOT BE MISLED"*), and an exit code cannot say so.

### F119 — ⭐⭐⭐ **ITEM 117 CLOSES, AND THE MEASUREMENT THAT CLOSES IT WAS TAKEN BY THE TASK THAT OPENED THE ITEM**

`TASK_PHP_055`, 776 lines. ⚠ **UNREVIEWED** (rule 9). Brackets `66/0` and `22/0`,
first and last, unmoved; nothing measured or re-gated.

⛔⛔⛔ **ITEM 117's PREMISE — *"the sweep measures the whole-program slope, NOT
`kernel_exclusive_ir`, so it cannot test an A1 figure; no tool here does"* — IS
FALSE, AND `_050` HAD ALREADY RUN THE TOOL.** ✅ **Manager-verified from
`.temp/php50/sw_ph53.json`, written 2026-09-14 by `_050` itself:**

```
ph53  large.bin : 32 pad residues,  (verus − unsafe) distinct values = [−14.0]
ph53  small.bin : 32 pad residues,  (verus − unsafe) distinct values = [−14.0]
            all EIGHT cell steps = 0.00 on both inputs
```

▶ ⭐⭐ **An alignment artefact is PAD-DEPENDENT BY DEFINITION, and sweeping 32
residues IS sweeping the alignment state. The difference is invariant across the
whole period, on both inputs.** ⛔ **This also defeats my own `M4R`**: I objected
that `small.bin`/`large.bin` are both 9 bytes and so are one draw — true, but the
**sweep deliberately varies the pad across 32 residues**, which is 32 draws per
input. **The multi-draw experiment I said did not exist had been run and written
to disk the day item 117 was opened.**

✅✅ **AND THE STRONGEST SUPPORT IS GENUINELY COMMITTED AND NOBODY HAD READ IT** —
manager-verified from git history, `ph53`'s gate record at its **three** re-gates:

| commit | `envp_stack_bytes` | `md5(marginal_ir_per_call)` |
|---|---|---|
| `4297b1d` (the build) | **3686** | `79716501c531` |
| `bee710e` (`_042`) | **3697** | `79716501c531` |
| `b754da4` (`_044`) | **3698** | `79716501c531` |

**Three independent alignment states, all 96 family-B figures BIT-IDENTICAL.**

⚠⚠ **ONE CORRECTION TO THE REVIEWER, AND IT IS F51/F99's OWN CLASS: the report
says *"the evidence has been committed since 2026-09-14"*, and
`.temp/php50/sw_ph53.json` IS GITIGNORED AND NOT COMMITTED** (`git check-ignore`
→ `.gitignore:3`). ✅ It is **re-derivable** — `php50_align_sweep.py` is committed
and is its generator, which is `CLAUDE.md` rule 1's correct arrangement — **but
the durable citation is the THREE GATE RECORDS, not the sweep JSON.** ▶ **Quote
the gate records; cite the sweep as re-derivable.**

▶ ⛔ **DO NOT BUILD THE SWEEP EXTENSION `_055` was asked to price.** It would test
the immune column for a contaminant a **mechanism** says cannot reach it:
`.memory/03-measurement.md` records that **100 % of the ±7 swing is inside a libc
`memset` callee**, which `kernel_exclusive_ir` excludes **structurally**.

### ⛔ AND THE ROUND'S OWN SCORE: **THREE OF FOUR CONCLUSIONS SURVIVED; ZERO OF FOUR REASONS SURVIVED AS WRITTEN**

- **M1** conclusion ✅ **upheld and UNDER-STATED — seven claim-groups, not four**;
  ⛔ **its cell (d) stated a FALSEHOOD: `_047` checked the PREDICTION LEDGER, never
  the novelty claim, and its own text says so.** **I wrote that into the block
  that governs the authoritative layer.**
- **M2** ✅ upheld, ⛔ **under-counted: there are TWO stale `contract_sha256`
  quotes, not one** — F96's `7013be6f7c1c` and **F100's `c41ffad2b795` at
  `RECAP_PHP.md:2922`**. ⭐ **And the rule's control is inside F96's own sentence:
  the BRACKETS aged correctly (`16/0` → `22/0`) because a bracket is quoted as an
  EVENT, and the sha did not because it is quoted as a STATE.**
- **M3** ✅ the number is exact; ⛔ **the sentence states 2 of the 5 things it owes.**
- **M4R** conclusion survives, ⛔ **its reason — *"no power at all"* — is REFUTED:
  M4 excludes the ONE-SHOT class exactly, and that is the class `_044` §8.2
  measured on this row.** `M4S` upheld and under-stated.
- **M5** ⛔⛔ **REFUTED IN BOTH HALVES** — the novelty claim has **three** cheap
  second methods, **two of them written before the row was built**.

✅ **P1, P2 and P3 all scored CORRECT.** ⓘ **Six consecutive rounds AS AT `_055`** — ⚠ **dated, not live: it is SEVEN after `_057`. The RULE-9 table is the index.**

### ⭐⭐ `F113` VERDICTED, AND ONE NEW UNIVERSAL FALLS

1. ✅ **Point 1 upheld** — the 24 cell-sweeps re-derived. ⚠ **Their artefacts are
   in gitignored `.temp/`** — F99's defect again, same class as above.
2. ⚠ **Point 2: `§B5` IS textually an `iff` — but the `iff` argument is a
   NON-SEQUITUR and `ph07` is not a counterexample to it.** The headline survives
   on the measurement; **the reasoning I gave it does not.**
3. ⭐⭐⭐ **Point 3: there is NO fifth explanation — my *"sensitivity × reach"*
   candidate is REFUTED ARITHMETICALLY at zero cost, and the whole SEPARABLE
   family with it**, on `_053`'s own artefacts. ⛔⛔ **And a new one falls out:
   THE PERIOD IS ALSO `(cell, axis)`-DEPENDENT** — one series reads **period 16 /
   window 8** against 29 series at **32/16**, contradicting a universal stated in
   **both `§B5` and the authoritative layer.** ✅ **No published figure is at
   risk**, but the universal is wrong as written.
4. ⚠ **Point 4: the inherited caution is APPENDED, NOT APPLIED, in BOTH homes**
   (item 73 again), **and item 118's scope clause landed in only one of the two.**
   ⓘ **Un-inherited-caution rate on a declared sample: 1 of 5.**

### F118 — ⭐⭐⭐ **THE ROW-11 SCREEN: 45 CANDIDATES, 13 FAMILIES, THREE AGENTS — AND THEY PICKED THREE DIFFERENT ROWS, EACH WITH EVIDENCE. ⛔ MY `P2` IS REFUTED AND MY RANKING WAS OVER 91 OF 102 ROWS**

`TASK_PHP_054`, three parallel investigators, **2 836 report lines**. Every
family screened from its **own Part B entry** and every shortlisted R1h read
**as bytes** — the rule item 94 bought with `ph32`.

| agent | pick | why, in one line | the cost it names |
|---|---|---|---|
| **A** — E2/E3/E4 | **`ph66`** (E2) | *the only row of twelve that owes the manager nothing*: 1 id → 1 commit, R1h one file / one hunk / 4+2−, **the two deleted lines are 5.0.0's cited lines byte-for-byte**; harm is a deterministic **silent wrong answer** in a pure checksum, allocator out of the picture | ⚠ **A predicts a `zend_hash` kernel is O(n)-per-call** — §B1a's precondition, the axis that cost the programme item 54 and the whole statistic thread |
| **B** — E5/E6/E7/E8 | **`ph90`** (E8) | harm **measured**, not argued: deterministic NULL write at **`si_addr = 0x10` = `offsetof(zval, refcount)`**, on the corpus's reproducer *and on a one-element array* | ⛔ **the `fix_commit` column is wrong for its own cited site** — B found the real repair, **`0542a6f2c2a5`** (2005-02-10, 1 file, 3+/1−, at `array.c:1045-1046`), **applied to the pinned tarball with `git apply` strict** |
| **C** — S4/S5/S6/T2/T4/T6 | **`ph97`** (T6) | R1h `f7326d627962` is **one file and ONE LINE** — ✅ manager-verified: `if (!strcasecmp("all", typ))` → `if (!typ \|\| …)`; needs **none** of the nine cost ticks; trigger `mb_get_info()` **verified at source** at `_021` | ⚠ C did not build it: if `zend_parse_parameters` cannot be narrowed without `EG(argument_stack)`, `ph97` drops behind `ph60` |

### ⛔ **P2 IS REFUTED, AND THE CONTROL EARNED IT**

I predicted **row 11 is temporal**. Agent C was dispatched as the control and
**fired**: T6 has **four of five rows with a 1-file, same-file, one-id R1h from
2004–2005, two of them ONE LINE**; **not one T6 row needs** the allocator, a
HashTable, the executor, stack garbage, a hash preimage or userland re-entry;
and **`PROTOCOL_PHP.md` §B1a says in terms to expect the O(1) precondition to
fail on *most* `E*` rows**, while §C measures the multi-commit R1h load at
**68 % temporal against 7 % spatial**.

⛔⛔ **AND P2's GROUNDS WERE WORSE THAN WRONG, THEY WERE UNGROUNDED.** My five
"best mechanical picks" came from `FIXSURVEY_001.md`'s per-row table — **built at
91 rows, containing none of `ph96`–`ph102`.** ⭐ **`ph96`, `ph97` and `ph102` all
have the shape that ranking scored best on and were invisible to it**; `ph102`'s
fix is **2004-07-19, the earliest in C's set.** ▶ **I flagged that gap in the
task file and told the agents to close it — and did not apply the correction to
my own hypothesis. Item 94's defect in a different dress.**

### ▶ **THE DECISION: ROW 11 = `ph97` (T6), ROW 12 = `ph96` TO CLOSE THE FAMILY**

⭐⭐ **The reason is not cheapness — it is that T6 is five rows of ONE obligation
(`I12`, *a fallible call's failure must be tested*) failed five different ways,
and THREE of them have the guard PRESENT AND PASSING**: `ph59` the guard's
*parse* differs from its reading; `ph60` no test at all; **`ph96` the call
returns SUCCESS and the out-parameter is still NULL**; **`ph97` the guard answers
a different proposition** (*"were the args well-typed?"* vs *"was the optional
arg supplied?"*); **`ph98` the test is right and the ERROR BRANCH faults**, on a
global the function itself cleared. ⭐ **And `ph96`'s repair hardens the same
obligation by a DIFFERENT strategy — remove the output rather than test it —
which is a result the programme does not have.** ⓘ `ph96`/`ph97`/`ph98` were all
**re-adjudicated out of the kill list** at `_019` §2.7–2.9, killed as *"ordinary
null-deref"* — **a quality judgement the bar does not carry**, `CLAUDE.md` rule 6.

⚠⚠ **THE COST OF THIS DECISION, STATED SO IT CAN BE HELD AGAINST ME: the
temporal axis stays at ONE row while `quota.py` says 15 of the 30 owed rows are
temporal.** Half the remaining programme has `n = 1` of experience. ▶ **That is
the strongest argument for A's or B's pick and I am overruling it on one ground
only:** ~~F116 landed in the same round, and a measurable C-side bar lowers the
cost of temporal rows specifically.~~ ⭐ ~~Rows 13–14 go temporal, with the
oracle.~~

> ⛔⛔⛔ **THAT GROUND IS REFUTED AND INVERTED, AND THIS TEXT NEVER INHERITED THE
> CORRECTION — CAUGHT 2026-09-15 WHILE DECIDING ROW 12.** `TASK_PHP_057` §3.2
> measured it **two ways that share no code** and got the same ordering both
> times: executed reproducers fault on **78.6 % of type rows, 58.5 % of spatial,
> and only 38.7 % of temporal**; the corpus's own `crashes_pristine_5_0_0`
> column, populated years before this programme, gives **70.6 / 43.2 / 32.6 %**.
> **`95.5 %` of temporal ids are filed `build=asan`.** ⭐ **The mechanism is not
> subtle: a use-after-free reads memory that is STILL MAPPED, so it returns
> stale bytes instead of faulting — `SIGSEGV` + `si_addr` is structurally
> WEAKEST on exactly the axis `F116` claimed it helps most.**
>
> ▶ **SO `F116`/§A3a LOWERS A *TYPE* ROW'S COST BY ABOUT TWICE WHAT IT LOWERS A
> TEMPORAL ROW'S — and `ph97`, the row it was used to justify, IS A TYPE ROW.**
>
> ✅ **THE DECISION SURVIVES; THE GROUND DOES NOT.** The reviewer's own words —
> ***"Replace the ground, keep the decision."*** `F118`'s *other*, research-grade
> reason stands unaided: **T6 is five rows of ONE obligation (`I12`) failed five
> different ways, and three of them have the guard PRESENT AND PASSING.**
> ⭐ **`ph96`'s repair hardens that obligation by a DIFFERENT STRATEGY — remove
> the output rather than test it — which is a result the programme does not
> have.** That is why row 12 is `ph96`, and it never needed `F116`.
>
> ⛔⛔ **WHAT THE REFUTATION ACTUALLY COSTS, AND IT IS NOT A DOWN-RANK**
> (`CLAUDE.md` rule 6, and the reviewer said so in terms): **waiting does not
> make a temporal row cheaper.** The *"rows 13–14 go temporal, **with the
> oracle**"* clause was a promise of a discount that does not exist on that axis.
> ▶ **Temporal rows should expect §A3a criterion 2 to read `NO CLI REPRODUCER`
> more often than not, and to lean on ASan/Miri instead — that is a METHOD
> consequence to plan for, NOT a reason to defer them again.** ⚠⚠ **A low
> executed-fault rate is `F3`: NOT evidence of absence, and NEVER a kill.**
>
> ⭐⭐⭐ **AND THE PROPAGATION IS THE LESSON, AGAIN.** `_057` verdicted this and
> the RULE-9 table has carried *"its stated ground is REFUTED AND INVERTED"*
> ever since — **while the decision text everyone actually reads, the one that
> says what to build next, kept asserting the refuted ground as live.**
> **`F129`'s exact defect — the index corrected, the prose not — FOURTH
> instance**, and this time in the sentence that chooses the next three rows.

▶ **WHAT WOULD OVERTURN THIS**, registered now: if the `ph97` build finds
`zend_parse_parameters` undetachable from `EG(argument_stack)`, T6's row becomes
**`ph60`** (which needs nothing at all) rather than the family being abandoned.

### ⭐ WHAT THE SCREEN FOUND THAT NO LABEL SAID — **and it is mostly bad news about `fix_commit`**

- ⛔ **SIX rows' recorded R1h is not the repair of their cited site**: `ph67` (the
  2014 commit is a **pure refactor** — the destructor still runs on a linked
  bucket), `ph72` (six hunks, all about `userdata`, none touches the cited
  `key`), `ph74` (**`NOT-THE-REPAIR`**; by 2006 the defect was already gone),
  `ph54` (✅ manager-verified: `fc96c7f7fa18` touches **0** occurrences of
  `get_current_data` and **does not touch `zend_execute.c` at all** — it is a
  performance refactor), `ph90` (B found the real one), and `ph101` (⭐ the only
  genuine **`NOT-THE-REPAIR`** exclusion in C's 19). ⚠⚠ **And the pre-image
  screen calls three of them `CANDIDATE`** — `NOT-THE-REPAIR` is the only one of
  its four outcomes that is a proof, and this is what the other three cost.
- ⭐ **`ph66`'s one named unknown is DISCHARGED**: the catalogue says its DJBX33A
  preimage *"was never computed"*; A computed it **both directions with two
  controls** and it is **closed-form arithmetic, not a search** —
  `H("x"+NUL) = 5863869`.
- ⭐ **Two free sibling censuses, both `ph55`'s signature on new rows**:
  `php_ftp_fopen_connect` is called at **7 sites in pristine 5.0.0 and 6 of 7
  guard `!stream`** (`ph60`; `:649` is the single omission); and **4 of 5
  `zend_call_function` sites in `array.c` test the out-parameter** —
  `php_array_walk` is the one that does not (`ph90`).
- ⚠ **`ph59`'s TITLE names the half upstream did NOT fix** — the fix changes
  `&& result` → `|| !result` and leaves the precedence expression verbatim;
  with `SUCCESS 0`/`FAILURE -1` that expression is **accidentally correct**. The
  row's body says so; **its title and Part A cell do not.**
- ⚠ **`ph37`'s `▸ trigger` cannot fire** (C supplies the corrected `%N$` with
  `N == numVars`), and **`ph85`'s fails** (B). ⓘ **P3 scored: 0 of 3, 2 of 7 and
  1 of 4 wrong — pooled `3 of 14 ≈ 21 %`** against F46/F49's 3-of-9. ✅ **Defect
  SITES were wrong in 0 of 19 + 0 of 12** — the mechanism half keeps holding and
  the `▸ trigger` half keeps failing, exactly as F46 said.
- ⛔ **`ph91`, `ph54`, `ph36`, E5 and `ph76` are BLOCKED-ON-A-DECISION, not
  killed.** `ph91` now has a **third** internal inconsistency (`root_cause_id`
  says `-uaf` while `cwe`/`category` say null-deref) and its reproducer segfaults
  at **`si_addr = 0x20`, the exact address its own comment predicts** — offered
  as evidence, explicitly not as an adjudication.
- ⛔ **S5, S6 and T4 have `n = 1` catalogued row each**, so `QUOTA_001`'s min-2
  floor is **arithmetically unreachable** for them. **Stated as programme
  arithmetic, NOT as a down-rank** — all three rows pass the C-side bar.

✅✅ **NO KILLS. All 45 rows pass criteria 1–3; everything above is COST.**
⭐ **Not one agent refused a row for a Rust-side, Verus-side or ladder-side
reason, and agent A says so in terms.** `CLAUDE.md` rule 6 held under three
independent agents.

### F117 — ⛔⛔⛔ **`citecheck` HAS BEEN RED FOR A REASON THAT IS FALSE, AND FOUR OF NINE CHECKERS NEVER RAN THEIR NEGATIVES IN THE ROUTINE SWEEP**

Manager, 2026-09-15, `.tasks-php/checkers.py` (new, 13 §H arms). ⚠ **UNREVIEWED.**

**(1) The false reason.** `RECAP_PHP.md` and the manager's own handoff both said
*"`citecheck` red on item 97's known §H debt"*. **`citecheck.py`'s last line is
`sys.exit(1 if rot else 0)`** — only the rooted-path rot count sets the code, and
**item 97's §H material is a separate warning block that never touches it**, by
design, *"so the 17 historical hits do not drown it"*. ⭐ **The one standing rot
is `TASK_PHP_048.md:337`**, a prose line reading `` `TASK_PHP_005/006/008_REPORT` ``
— three files written as one path, in a paragraph headed *"NAME COLLISION, DO NOT
BE MISLED"*. **A false positive.** ▶ **Adjudicated and NOT repaired: silencing a
checker by editing its input is the opposite of the ratchet.**
⚠ **And `rot` rises transiently per in-flight task**, because a task file cites
its report before the report exists — ⛔ **so `citecheck` rc=1 cannot tell *a
task is running* from *a citation rotted*. READ THE COUNT, NEVER THE EXIT CODE.**

**(2) The sweep was weaker than it sounded.** The manager's routine sweep was
a shell loop over **8** files with **no
arguments**. Measured: **5 of the 14 checkers run their §H negatives only under
`--selftest`** (`citecheck`, `cbaseline_check`, `preimage_screen`, `fixsurvey`,
`task_cost`), and `task_cost.py` is the live proof — **a bare run exited `0`
while `--selftest` exited `1`.** ⭐ **`contract_audit.py` is the reference design
and the only checker whose sweep arm and verdict arm are the same run.**
▶ **`checkers.py` replaces the loop: 18 files filed, 14 checkers, 19 arms.**
⭐ **No `RATCHET` literal — the registry IS the ratchet**, because five hardcoded
figures in this directory have gone stale and `EMPTY_FAMILIES` proved **a bound
is not a derivation**.

⭐⭐ **AND THE PRE-COMPACT AUDIT MEASURED BOTH HALVES OF THIS FINDING, THE HARD WAY.** ✅ **The transient half reproduces**: `rot` went `1 → 4` while `_054`'s three reports were in flight and **fell back to `1` the moment they landed** — so *read the count, not the exit code* is now measured, not argued. ⛔⛔ **And I added FOUR spurious rot entries myself in one session**, every one of them a path-shaped string written *in prose about paths*: the sweep loop in `README.md`, **the note explaining that entry** (which quoted the string), the same loop in `checkers.py`'s docstring, and again in this finding's own text. ⭐ **All four removed; `rot` is back to the single adjudicated false positive.** ▶ **FIFTH INSTANCE OF *A CHECK THAT READS PROSE AND CALLS IT CODE*** (item 115's class), and the first where the *explanation* of an instance created another. ⚠ **The rule that works: describe the command, do not quote it.**

⚠⚠ **THIS IS THE THIRD TIME *"ALL CHECKERS PASS"* HAS BEEN FALSE** — `coverage.py`
exiting 1 since 2026-09-10; the six stale things behind a green sweep on
2026-09-14; and now a sweep that did not exercise four checkers' arms at all.
**F14's class one level up: `rc=0` does not mean everything was checked.**

### F116 — ⭐⭐⭐ **THE C-SIDE BAR CAN BE *MEASURED*, NOT ARGUED — THERE IS A WORKING PHP 5.0.0 CLI ON THIS BOX AND NOT ONE MANAGER DOCUMENT POINTS AT IT**

`TASK_PHP_054` agent B. ⚠ **UNREVIEWED** (rule 9). ✅ **Manager-verified**: the
binary at `…/php-in-safe-rust/.app-tests/.temp/oracle/bin/php-5.0.0-mysql-webext`
answers `PHP 5.0.0 (cli) (built: Aug 5 2026)`, and B's counts reproduce from its
own log — **36 corpus reproducers run, 14 `rc=139` (SIGSEGV)**.

⛔⛔ **`CLAUDE.md`, `PLAN_PHP.md`, `RECAP_PHP.md`, `PROTOCOL_PHP.md`,
`CATALOGUE.md`, `SOURCES.md` and `.memory-php/` mention the binary ZERO times**
(measured). The *reproducers* are mentioned in three documents; **the means to
RUN them is in none.**

⭐⭐⭐ **WHY THIS IS BIGGER THAN ROW 11.** `CLAUDE.md` rule 6's criterion 2 —
*does the C exhibit the target error on an adversarial input?* — **has been
argued from source reading on all ten built rows.** It can be executed. B ran 36
corpus reproducers and 18 transcriptions of the catalogue's own `▸ trigger`
lines under an `LD_PRELOAD` that prints `si_addr` (**no gdb on this box, and
memcheck refuses to start**), and got `ph90`'s fault at **`si_addr = 0x10` =
`offsetof(zval, refcount)`** — deterministic, garbage- and ASLR-independent.
▶ **This lowers the cost of exactly the rows that are half the remaining
programme**, because temporal harms are the hardest to argue and the easiest to
execute. ⚠ **The binary is `php-in-safe-rust`'s oracle build, not a
museum-default one** — B says so, and a row must say which build it measured on.

### F115 — ⛔⛔ **THREE CATALOGUED `fix_commit` SHAS DO NOT BIND TO THE PATCH GITHUB RETURNS FOR THEM — AND THE SURVEY'S GUARD COULD NOT SEE IT**

`TASK_PHP_054` agent A, **independently confirmed by agent B and then by the
manager** — three routes, which is why it is stated this plainly.

`fixsurvey.py` validated a cached patch by `startswith(b"From ")` **alone** — a
check on the *shape* of the header, not its *content*. **F10's class: a guard
that is a string search is a guard with a spelling.** Measured: **3 of 163**
cached patches carry a `From <sha>` that is not the sha they are filed under.

| filed under | row | the patch actually carries |
|---|---|---|
| `49bd45a2c175` | `ph79`/LOGIC-025 | `bc9f2fb8dfad…` |
| `abb09693ac4d` | `ph78`/CRASH-159 | `6a6c27389317…` |
| `ed4c0245c7ca` | `ph75`/CRASH-161 | `9dfa843a386b…` |

✅ **Reproduced live and it is NOT a cache corruption**: a made-up sha → **404**
(GitHub does not substitute); a known-good corpus sha (`4f68f3774c34`, `ph55`'s
R1h) → `From 4f68f3774c34948a…` **matching**; these three → **HTTP 200, no
redirect, different `From`.** ⭐ **And the CONTENT is the right commit anyway** —
subject, file count and (agent B's narrowing, which A did not have) **bug number**
all match the row. ▶ **It looks like a binding over an MFH / cherry-pick twin.**
⚠⚠ **THE MECHANISM IS UNEXPLAINED AND THE REPAIR DOES NOT GUESS AT IT.**
`binding_verdict()` is a pure function with **six §H arms** plus a **derived**
ratchet; it **reports** the class and changes no verdict, and the code says in
terms: **never re-fetch or delete these, that destroys the only evidence there
is.** ▶ **A row whose R1h is one of these owes an R1h DECISION before a build
task** (§C), the same as a row whose ids name several commits.

### F114 — ⭐⭐⭐ **`F96` WAS NEVER ONE FINDING: FOUR REVIEWER ROUNDS HAD IT IN SCOPE, TWO PRODUCED VERDICTS ON IT, AND THE ATOM STAYED RED**

Manager, 2026-09-15, while scoping `TASK_PHP_055`. ⚠ **UNREVIEWED** — and
`_055` is written to attack it.

The RULE-9 table has carried **F96** as *"`UNREVIEWED`, FOURTH ROUND … it has
**NO cheap second method** … stop re-scoping it into review rounds"*. **Checked
header by header, that ground is wrong.**

| task | role, from its own header | F96 in scope? |
|---|---|---|
| `_042` | research **engineer** | ⛔ no — but §3 reviews `_040` §5.6's **R3 prediction** by name: *"the prediction's MECHANISM was wrong"*, with the disassembly |
| `_043` · `_047` | research **reviewer** | ✅ → returned **UNREVIEWED** |
| `_050` | research **reviewer** | ✅✅ **NAMED IN ITS TITLE** — *"and review `F109` · `F107` · `F96` behind it"* → returned UNREVIEWED, **and produced F110 #4, a verdict on result 2** |
| `_053` | research **reviewer** | ✅ → returned UNREVIEWED, **and produced F113's refutation of result 2's reason** |

⭐⭐ **Result 2 has had TWO REVIEWER VERDICTS and they split exactly along
conclusion/reason** — `_050` *confirms it on its own stated falsifier*, `_053`
*refutes its stated REASON*. **Both filed those verdicts under their own finding
numbers while reporting F96 itself as `UNREVIEWED`.**

▶ ⭐⭐⭐ **THE ATOM WAS NEVER THE UNIT OF REVIEW. THE CLAUSES WERE REVIEWED AND
THE ATOM STAYED RED** — and *"it has no cheap second method"* was written on the
fourth round **by a reviewer that had just supplied one.** **F22/F27/F69's shape
— *a claim written as a set hides its members* — for the fourth time.**

⚠ **Measured while checking**: F96's `contract_sha256 7013be6f7c1c` is **stale by
two re-gates** (the record reads `6924e66fde49…`; `_042` and `_044` both re-gated
`ph53`). The other seven gate quotes reproduce. ✅ **Its `A1 −1.253 %` reproduces
exactly** (`O3/isolated`, `small.bin`, unsafe→verus).
⛔ **The ONE clause with no cheap second method is the NOVELTY claim** — *"the
first IN-BOUNDS uninitialised read … no built row priced that"* — which is
precisely what `_047`'s reviewer checked.

### ⛔⛔ AND A MANAGER CLAIM MADE AND REFUTED BY THE MANAGER, BOTH BEFORE DISPATCH — **ITEM 117 STAYS OPEN**

I found that `ph53`'s A1 `unsafe→verus` step is **`−14.000 Ir/call` on BOTH
inputs** (`small` 25 000 iters, `large` 10 000) and argued a whole-program offset
`κ` would divide differently and so must be zero — **closing item 117 free.**

⛔ **It is wrong, twice over.** (a) `php50_align_sweep.py`'s own docstring: every
family-B figure is `marginal_ir_per_call`, **a SLOPE over `probe_iters`
[100, 200], and *"the slope cancels"* the one-shot term** — so the measured
`0.00`/`0.02`/`7.00`/`34.49` steps are **PER-CALL** and never divide by
`n_iters`. (b) `small.bin` and `large.bin` are **both 9 bytes**, so both runs sit
at the **same alignment state** — ⭐⭐ **one draw reported twice, which is the
`ph64` defect EXACTLY, same manager, two rounds later.**
⛔ **And the counter-evidence was already in the authoritative layer**:
`03-numbers.md:234` records **`ph45`'s `unsafe → verus` carrying a measured
`14.00` RANGE** — **the same rung pair** — plus `ph55`'s clang cells needing
`14` to protect their difference. **Three `14`s in alignment contexts.**
✅ **What survives is much weaker** and is filed as `M4S` in `_055`: the two
inputs do **2.5× different per-call work**, so any contaminant is
**per-call-constant, not per-window** — a constraint on the artefact's *shape*,
not evidence there is none.

### F113 — ⭐⭐⭐ **THE DECISIVE TEST WENT BOTH WAYS: `§B5`'s VERDICTS ARE CONFIRMED ON THREE AXES AND ITS STATED GROUND IS REFUTED — `argv` AND `envp` ARE *NOT* THE SAME KNOB**

`TASK_PHP_053`, 808 lines. ⚠ **UNREVIEWED** (rule 9). Brackets **`66/0`** and
**`22/0`**, first and last, unmoved; nothing measured or re-gated.

> ### ✅ THE RULE SURVIVES, AND IT SURVIVES BY MEASUREMENT
>
> **12 `0.00`-`argv` cells swept on `envp` AND on `argv[0]` — 24 cell-sweeps, NO
> COUNTEREXAMPLE.** ⭐ **`ph64` — on which the whole item-112 verdict rests — is
> flat on all three axes**, so its clearance is **confirmed**, not merely
> un-refuted.

> ### ⛔⛔ AND THE GROUND IT WAS GIVEN IS **REFUTED**
>
> `ph07`'s `verus` cell steps **`34.49` under `argv[1]`, `20.08` under
> `argv[0]`, `0.00` under `envp`** — flat over **96 consecutive bytes**.
>
> ⚠⚠⚠ **AND THE SCOPE, WHICH THE MANAGER LANDED WITHOUT AND THE REVIEWER ADDED:
> THE REFUTATION RESTS ON *ONE ROW AGAINST THREE THAT AGREE*.** `ph55`'s clang
> cells agree (same `7.00`, constant `+6` phase); ⭐⭐ **`ph45`'s four Rust cells
> agree to the DIGIT — every median, every range and every verdict string
> identical across the two axes**, including `_050`'s own headline that exactly
> two of its differences carry a `14.00` range (**the same two**); and the 12
> clean cells read `0.00` everywhere. ▶ ⭐ **The refutation still STANDS AS
> STATED, because one counterexample breaks an `iff` and §B5 is an `iff`** —
> **but if `ph07` were an artefact nobody found, §B5's ground would be fine and
> this round's headline would collapse to *"confirmed on three axes"*.**
> ✅ **`ph07` was attacked four ways and survived all four. It is one row.**
> ✅ **Four rival explanations ruled out by measurement**: a dead instrument
> (`ph55` stepped `7.00` under `envp` in the same session, same period and
> window, constant `+6` phase on **both** cells), the added variable (the `argv`
> sweep re-run with it present still reads `34.49`), a longer period, and *"the
> program reads `argv[1]`"*. ▶ ⭐⭐ **THE STEP IS A PROPERTY OF THE
> `(cell, axis)` PAIR, NOT OF A CELL.** ⚠ **The mechanism is UNEXPLAINED and the
> reviewer says so.**
>
> ⚠⚠ **CONSEQUENCE: a `0.00` on the `argv[1]` sweep is NECESSARY and heavily
> corroborated, NOT PROVED SUFFICIENT.** ⭐⭐⭐ **And the right way to say that
> was already written in this project, about this exact quantity** —
> `harness/check.py::_env_block`'s caution that **three equal fields mean *this
> record cannot tell the two draws apart*, not *the two draws are the same*.**
> ⛔ **§B5 did not inherit it. It does now.** ⓘ **Second un-inherited caution in
> three rounds** (F108 was the first).

⭐⭐⭐ **THIS IS THE FOURTH CONSECUTIVE ROUND WHERE A CONCLUSION SURVIVED AND THE
REASON GIVEN FOR IT DID NOT** — `_047` (F103's decomposition), `_049` (item 111's
headline), `_050` (my `ph64` two-input defence), and now `_053`. ▶ **That is no
longer a run of luck; it is the programme's characteristic failure mode, and it
argues for reviewing REASONS separately from CONCLUSIONS.**

**AND IT CORRECTED F112 IN TWO PLACES** — see F112: the `rlimit` floor is **3**,
not 2, so the *"`n = 2` about the proof shape"* coincidence is **refuted**; and
`controls/rlimit_bisect.sh` **cannot run on its own shipped file**.
⛔ **`req-mut` deletes preconditions ONE AT A TIME** (`check.py:6718`) — **a real
hole, since two preconditions can be individually removable and jointly
necessary** — ⓘ **but it does not bite `ph56`, whose shipped file verifies
without both.** ⚠ **A `harness/` finding: reported, not edited.**

⭐ **AND THE REVIEWER REFUSED AN ATTACK I HANDED IT.** I suggested checking
whether `ph55`'s `+0.071 %` clears its own `7.00 Ir/call` step; **it misfires** —
that is an **A1** figure and the pair is `0.00`-step on both axes. ▶ **Reported
as a NON-refutation rather than dressed up as one.** ⚠ **The *"the row had to buy
it"* causal story is still UNPROVEN** — `ph55` never measured a one-spelling
variant — **and `0.000 Ir/call` is EXACT but ENTAILED BY THE `norel` PIN, not
independent of it.** ✅ *"Nine expressions, three files"* is **exactly right**.

**F111's offline half UPHELD** by re-running the row's own `census.py`
(`problems: none`), including the declaration-order asymmetry **measured on a
pristine 5.0.0 CLI**, and `0x14 = offsetof(zval, type)` **confirmed by an
independent probe built from the pinned tarball**. ⛔ **The four
upstream-history claims are UNTESTED (network) and reported as UNTESTED, not as
confirmations.**

⭐⭐ **F96 IS UNREVIEWED FOR THE FOURTH TIME — AND THE ROUND FOUND WHY IT KEEPS
BEING.** `ph56` **is** the cross-language row `_050` §7.3 said was missing, and
**6 of 12 pairs disagree in sign between A1 and B1 on a NON-ALLOCATING kernel**,
which **refutes F96 result 2's stated REASON.** ⭐ **The real mechanism is
`inside_share`, exact to the digit: `+128.179 − (409.666 − 83.617) = −197.87`,
the recorded B1.** ▶ **Fourth honest `UNREVIEWED` is the finding: F96 has no
cheap second method and needs a dedicated task or a permanent mark.**

ⓘ **`_050`'s seven uncertainties triaged: only two are load-bearing. #1 is now
closed (the wrong way). #2 — `ph53`'s A1 `unsafe→verus` being exactly `−14.000`
where `14 = 2 × 7` — is the one thing left to route** (item **117**).

### F112 — ⭐⭐⭐ **ROW 10 IS BUILT — T5 CLOSED AT 2 — AND `R4 → R5` COSTS *EXACTLY NOTHING*, WHICH THE ROW HAD TO *BUY*

`TASK_PHP_052`, 508 lines. ⚠ **UNREVIEWED** (rule 9). ✅ **Manager-verified from
`results-php/gate/ph56-fetchmode-arith.json` and SAYING WHICH**: `verdict PASS`,
`failures []`, `complete_run true`, `contract_sha256 e76ae727f70b`,
`blocked_rows null`, `advisories null`, `identity` **`norel`** as pinned.
**Brackets `66/0` unmoved and `20/0 → 22/0`, the `+2` being exactly this row's
two records — re-run by me.** ⭐ `quota.py`: **10 built, 30 owed, T5 at 2.**

> ### ⭐⭐⭐ `R4 → R5` = **`0.000 Ir/call`, `0.000 %`, ON BOTH INPUTS** — AND IT WAS NOT FREE, IT WAS BOUGHT
>
> `identity` pins **`norel`**, and family B reads **`0.00` across all 32 pad
> residues**. ⛔ **But `ph55` shipped `+0.071 %` on the same step**, and the
> difference is a *representation* choice: **Verus models `usize` as 32 **or**
> 64 bits and will not assume a `u64 → usize` cast is lossless**, so R5 must take
> the modulus **before** the cast. `ph55` resolved that by shipping **two
> spellings** — `(x as usize) % NVAR` in `unsafe.rs`, `(x % (NVAR as u64)) as
> usize` in `verus.rs`. ⭐⭐ **`ph56` NORMALISED ALL FOUR RUST RUNGS ONTO THE
> SECOND SPELLING** (nine expressions, three files), **so R4 and R5 are one exec
> text and the R2→R3 / R3→R4 gradients carry no representation change.**
> ▶ **THE RESULT: *"the proof is free"* is a claim about how the ladder was
> WRITTEN, not only about Verus** — and this row is the first to make it exactly
> zero by construction rather than approximately zero by luck.

> ### ⛔⛔ AND THE CROSS-LANGUAGE **SIGN FLIPS BETWEEN THE TWO C COMPILERS INSIDE ONE STATISTIC**
>
> **R4/R5 against the R1h C cells, W1, `O3/isolated`, `large.bin`:**
> **`−8.423 %` against `c-gcc-h`** and **`+3.811 %` against `c-clang-h`.**
> ⭐⭐⭐ **AND THE ROW PUBLISHES BOTH COLUMNS AND BOTH SIGNS RATHER THAN PICKING
> THE FLATTERING ONE** — **F108's rule working on the FIRST ROW BUILT AFTER IT
> LANDED**, which is the strongest evidence that rule could have.
> ⓘ `inside_share` predicts it: gcc keeps **11–15 %** of per-call work outside
> the `kernel` symbol against Rust's **0.8–2.9 %**, a gap of `0.085–0.137`
> against `STATISTICS_001.md` §1's `0.02` threshold. ⭐ Exactly one pair set is
> narrow (Rust vs `c-clang-h` on `large.bin`, `0.0104–0.0130`), and
> `controls/statistic.py` **checks the wide and narrow halves in OPPOSITE
> directions so neither claim can rot silently.**

⭐⭐ **THE GATE DELETED TWO OF THREE PRECONDITIONS THIS ROW COPIED FROM `ph55`.**
`req-mut` reported `16 <= len` and `len <= 8 * MAX_STMT` **NOT load-bearing**,
and both are gone. ▶ **`ph56` ESTABLISHES IN CODE WHAT `ph55` ASSUMES IN A
SIGNATURE** — the `nstmt` clamp and the `nops` break — and the `noclamp`/`nocap`
mutants measure that nothing else does. ⚠ **The lesson is about CLONING A
SIBLING'S SIGNATURE: a precondition that is not load-bearing narrows the
admissible call sites for nothing, and READING WOULD NOT HAVE CAUGHT IT.**

⛔ **THE MUTATION TEST IS THE ARGUMENT, AND ALL FIVE MUTANTS FAIL.** The one that
matters: **`r1` deletes `1e708a5aeb30`'s three lines and the file STOPS
VERIFYING — at the `assert forall` that re-establishes `operand_present`.**
✅ `pristine` re-verifies the shipped file at **66/0** (and **76/0** twin) on
every run, **so a broken toolchain cannot read as a clean sweep.**

⭐ **AND AN `rlimit` ERROR IS A SYMPTOM, NOT A SIZE.** ⛔⛔ **CORRECTED
`TASK_PHP_053` §2.5: THE FLOOR IS `3`, NOT `2` — `65/1` at rlimit 2 (twice),
`66/0` at 3, with a `pristine` control matching the gate record exactly. `ph55`
verifies at `2`, SO THE *"`n = 2` about the proof SHAPE"* COINCIDENCE IS
REFUTED.** ⚠⚠ **And the control that produced the wrong number CANNOT RUN ON
ITS OWN SHIPPED FILE** — reproduced by the manager: *"insertion matched 2x, want
1 -- verus.rs has been respelled and this script is measuring the wrong file"*.
**Its guard greps `verifier::rlimit` and the file's own COMMENT matches.**
⭐⭐⭐ ***A COMMENT IS NOT CODE*, AGAIN — and `ph55`'s copy is WORSE (two
comments).** ✅ **What survives, and it is the part that mattered:** the first
draft's overrun was **a wrong loop invariant**: two clauses that cannot
hold at a `break` were declared `invariant` instead of `invariant_except_break`,
so Z3 spent the budget failing to prove them. ⛔⛔ **The obvious repair — raise
the limit — would have shipped a WRONG INVARIANT under a 20× budget.**

**PREDICTIONS: 1 ✅ UPHELD** — stage 5c-twin clean, **10/10 twins, none justified
away**, so F97's narrowing survives a second row. **2 ⚠ UPHELD ON MECHANISM** —
the guard costs **1.06–1.55 Ir per emitted statement, FLAT across a 4× change in
statement count** — ⭐ **and the report states explicitly that its percentage is a
loose UPPER BOUND on PHP's, not PHP's**, because this kernel compiles-and-runs in
one loop. **3 ✅ HONOURED** — no endpoint prediction was made, which was the
position.

⚠ **LARGEST DECLARED GAP: the `R3 → R4` step is NOT decomposed** — `zunwrap`
against the nine index accessors is unmeasured, because this row's
`controls/spellings.py` is the contract audit only and not `ph55`'s respelling
search. ⭐ **An endpoint search is a separate task on every row; this is that
task's brief.**

### F111 — ⭐⭐⭐ `ph56`'s HARM IS **MEASURED** AND IT REFUTES THE CATALOGUE **AND** THE MANAGER — AND THE SIBLING CENSUS COMES BACK **NON-EMPTY** FOR THE FIRST TIME

`TASK_PHP_051`. ⚠ **UNREVIEWED** (rule 9). ⛔⛔ **THE ROW IS *NOT* BUILT AND
*NOT* GATED — the engineer ran out of depth and said exactly where.** Five of six
rungs exist and **all agree differentially** (C↔model, 156 windows × 2 configs,
**0 mismatches**); **`verus.rs` and `spec.md` DO NOT EXIST**; nothing was built,
measured or gated. ✅ **Brackets `66/0` and `20/0` — and the task PREDICTED
`22/0`, so the unmoved bracket is the stopping point reporting itself.**
⭐ **No `Ir`, no percentage and no statistic is published by that task.**

> ### ⛔⛔ I WAS WRONG ABOUT THE HARM, AND I NAMED THE RIGHT CODE FOR THE WRONG REASON
>
> `TASK_PHP_051` §2.2 — **my** correction to the catalogue — said the harm is a
> `refcount++` on `EG(uninitialized_zval)` at `zend_execute.c:935-943`.
> ⛔ **`zend_fetch_dim_is_handler` NEVER RUNS on this row's trigger:**
> `zend_do_isset_or_isempty` (`zend_compile.c:3223`) **overwrites the
> `ZEND_FETCH_DIM_IS` opline four lines after it is created.**
> ⛔⛔ **AND THE REFCOUNT IS BALANCED.** `:935-943` is what **`$a[] = 1`** and
> **`$a[] += 1`** reach on **every legal append** — so `new_zval->refcount++` is
> **the implementation of `[]`**, not a defect, and the FAILURE arm decrements it
> again at `:942`. ▶ ⭐ **Upstream is careful there. The carelessness is one file
> away, in the compiler.**

⭐⭐⭐ **THE REAL HARM, MEASURED ON A PRISTINE 5.0.0 CLI UNDER ASan AND
REPRODUCED AT THE SAME OFFSET IN THE KERNEL: a NULL READ AT `0x14`** in
`zend_isset_isempty_dim_prop_obj_handler` (`zend_execute.c:3958`). `:3961` takes
`offset = get_zval_ptr(&opline->op2, …)`, whose `case IS_UNUSED:` is an explicit
`return NULL` (`:118-121`), and **nothing between `:3961` and `:3973` tests it**
before `switch (offset->type)`. `0x14` = 20 = `offsetof(zval, type)`, verified
with a standalone probe. ▶ **A MEMORY ERROR — CWE-476 — reached because the
COMPILER emitted an opcode whose handler's operand contract it did not check.**
⭐ The kernel carries a **C99 compile-time layout assertion** so the offset
cannot drift silently, and faults at the same address in the same enclosing
function: **§A4 discharged by measurement, not by resemblance.**

✅ **AND MY HARM IS REAL — AS THE ROW'S *SECOND* INPUT.** `:3223` rewrites only
the **last** opline of the fetch list, so in **`isset($a[][0])`** the `[]` opline
survives, the append arm *is* reached, and: **`isset()` returns `false`, the
array silently grows `3 → 4`, exit code `0`, and nothing diagnoses it.**
⭐ **The task named that outcome in advance as a RESULT and not a
disqualification, and it is the row's second input, one byte-record from the
first.**

> ### ⭐⭐⭐ THE SIBLING CENSUS IS **NON-EMPTY** — THE FIRST TIME — AND THE ANSWER IS NOT *"AN OVERSIGHT"*
>
> **All six arms run on real PHP.** ⛔ **`BP_VAR_FUNC_ARG` is a LIVE UNCAUGHT
> SIBLING AT 5.0.0 WHOSE REACHABILITY IS *DECLARATION ORDER***
> (`zend_do_pass_param:1411-1427`): **the same `f($a[])` is a fatal error or a
> silent mutation depending on whether `function f` is written above or below the
> call.** ⭐⭐ **AND THE ASYMMETRY IS PERMANENT: upstream NEVER guarded
> `RW`/`FUNC_ARG` at compile time in ANY PHP 5, and the same three-arm asymmetry
> survives into `master`.** `FUNC_ARG` was closed **11½ months later, AT RUNTIME,
> in a different file, by a different author** (bug #34064, 2005-08-10) — and
> **that patch WIDENED the opcode specs**, i.e. **RW-append is a FEATURE, not an
> unfixed bug.** ▶ ⭐ **So the guard MIGRATED LAYERS rather than being forgotten.**
> ⚠⚠ **AND THE BUG THIS ROW IS ABOUT GOT NO REGRESSION TEST; ITS SIBLING'S TEST
> IS STILL IN `master`.**

⭐ **PREDICTIONS: 1 UPHELD and its STATED REASON REFUTED** — `git apply` succeeds,
but at **offset −2**, not because the line numbers matched. ⛔⛔ **AND
`git apply --check` LIED LIVE, exactly as `_048` §4d predicted** — second
instance, now on a different row. **2 UNTESTED** (no gate ran). **3 upheld on
mechanism, untested on the number**, and the task's own caveat fired: this kernel
compiles-and-runs in one loop.

### F110 — ⭐⭐⭐ **THE ALIGNMENT ARTEFACT IS REAL, IT IS ON THREE ROWS NOBODY SUSPECTED, IT DOES NOT TOUCH `ph64`, AND NO PUBLISHED FAMILY-B NUMBER IS WRONG**

`TASK_PHP_050`, 1 133 lines. ⚠ **UNREVIEWED** (rule 9). **Brackets `66/0` and
`20/0` unmoved; no gate, no measure, no re-gate.** ⭐⭐ **THE SWEEP NOBODY HAD
RUN, AND IT COST NOTHING: 5 120 callgrind runs over all ten rows, both inputs,
a FULL 32-byte pad period, `-O3 isolated` — and NO BUILD, because every binary
already existed.** The pipeline reproduces the committed `marginal_ir_per_call`
**exactly** on `ph64` (all 8 cells), `ph52` and `ph55`.

| | step (`Ir/call`) | what it is |
|---|---:|---|
| **`ph64`** | ⛔ **`0.00`** on every cell | **no alignment-sensitive cell at all — the worry is REFUTED** |
| `ph53` · `ph03` · `ph16` · `ph52` · `ph00` | `0.00` | clean |
| **`ph29`** | `0.02` | PAT's heap class |
| ⭐ **`ph55`** | **`7.00`**, period 32, window 16 | the instrument, on the row that found it |
| ⭐⭐ **`ph45`** | **`7.00`** on four **Rust** cells, **UNEQUAL PHASES** | so two of its *differences* carry a **`14.00`** range |
| ⭐⭐⭐ **`ph07`** | **`34.49`** | **the largest in the corpus, and NOT a multiple of 7** |

✅✅ **`4` of `180` family-B differences flagged, all on `ph55` and `ph07`, and
NO PUBLISHED FAMILY-B NUMBER IN THE CORPUS IS WRONG** — the only row that both
publishes family B and owns an exposed cell is `ph55`, which already refuses to
quote it. ▶ **The publication rule is landed in `.memory-php/03-numbers.md`, and
a MAGNITUDE FLOOR is refuted by measurement rather than declined on taste.**

> ### ⛔⛔ AND IT RETRACTED HALF OF MY OWN ARGUMENT — **A CORRECT CONCLUSION ON A WORTHLESS REASON**
>
> I defended `ph64` with *"four cells across **two compilers and two inputs**
> agreeing within `2.4 Ir` — which an alignment artefact would not produce."*
> ⛔ **The two-input half is not evidence at all**: `probe.small.bin.100.bin` and
> `probe.large.bin.100.bin` are **the same length (23)**, so both inputs run at
> the **same** stack alignment — and `ph55`, where the artefact *does* exist,
> agrees across both inputs **perfectly**. ▶ ⭐⭐ **The conclusion was right and
> the support was worthless, which is still a defect, BECAUSE THE REASON IS WHAT
> GETS REUSED.** ⓘ **Same shape as `_049`: the effect upheld, the story refuted.**
> **Third round running where a manager argument dies while its conclusion lives.**

⭐ **FOUR MORE THINGS THE SWEEP FOUND THAT NOBODY WAS LOOKING FOR.**
**(1)** `harness/check.py`'s *"a 16-apart two-pad screen is a COMPLETE detector"*
is **true for a CELL and false for a DIFFERENCE** — ⓘ a PAT-side docstring,
**not edited**, flagged so the php layer does not inherit the wider reading.
**(2)** ⭐ **The shim adds EXACTLY 15 bytes against a 16-wide window**
(`repo_path_bytes` 48 = 33 + `len('/.temp/php-root')`), so `PROTOCOL_PHP.md`
§E's *"never run `check.py` directly on a php row"* **is a MEASUREMENT-STABILITY
rule and not only a provenance convention** — `gate.py` itself calls it *"a
convention, not a mechanism"*. **(3)** **`envp_stack_bytes` is NOT constant
across the ten records** — four values (`3685`/`3695`/`3697`/`3698`) spanning
13 bytes inside a 16-wide window — so **a family-B comparison ACROSS rows is out
of the records' own stated domain.** ✅ **No published figure is affected**;
recorded before someone makes that comparison. **(4)** ⛔ **`ph64`'s B1 for
`unsafe → verus` is `+193.36` on `small` and `−28.77` on `large` while A1 is
`−0.510` on both** — B disagrees with A in **sign** and **flips between inputs**
— which confirms F96's result 2 **on its own stated falsifier**.

⚠⚠ **THE ONE UNPROVEN LINK, DECLARED RATHER THAN FOUND LATER: the sweep perturbs
`argv`, while the bimodality the GATE observes is across `envp`.** Strong
indirect evidence they are the same knob — same stack block, same step, same
32/16 period — **but not proven.** ▶ **Cheap to close: sweep `envp` the same way.**

⭐ **AND IT HIT ITEM 113's MIRROR IMAGE**: a `pgrep` guard that **matched its own
launcher's command text** and span forever. Fixed by confirming
`/proc/<pid>/cmdline` for an exact PID and rewriting the runner with no `pgrep`.
▶ **So item 113's law needs both halves: a liveness check may not be TRUNCATED,
and it may not MATCH ITSELF.**

### F109 — ⭐⭐⭐ **ROW 9 IS BUILT — `ph55`, T5, THE 7th FAMILY — AND THE TWO ADVERSARIAL INPUTS GIVE OPPOSITE ANSWERS, WHICH IS THE POINT**

`TASK_PHP_048`, 765 lines. ⚠ **UNREVIEWED** (rule 9). ✅ **Manager-verified from
`results-php/gate/ph55-opdata-stride.json` and SAYING WHICH**: `verdict PASS`,
`failures []`, `complete_run true`, `contract_sha256 c08504352b33`,
`blocked_rows null`, `advisories null`, identity `O0 differ / O3 differ` as
pinned, **53 verified / 0 errors**, 10 TCB items, Miri on 7 inputs.
**Brackets `66/0` unmoved and `18/0 → 20/0`, the `+2` being exactly this row's
two records — re-run by me.** ⭐ `quota.py`: **9 built, T5 entered, 31 owed.**

> ### ⭐⭐⭐ THE HEADLINE: **THE `Option` CAUGHT THE NULL. IT DID NOT CATCH THE WRONG PC.**
>
> The two adversarial blobs differ in **ONE BYTE** — the opcode field of the
> trailing data word — and `inputs/gen.py` **asserts** that (`diff == [16]`)
> rather than describing it.
>
> | input | C (the bug) | **safe** Rust + the same bug |
> |---|---|---|
> | `adversarial-nullcall.bin` | ⛔ **SIGNAL 11** | ⛔ **PANIC** — a real difference |
> | `adversarial-opdatalive.bin` | wrong answer, **exit 0** | ⛔⛔ **BIT-IDENTICALLY THE SAME WRONG ANSWER** |
>
> ⛔⛔ **On the second input `model.py::sanitizer_expect` declares the run
> `clean`, and it IS: there is no memory error, only a wrong answer. ASan,
> UBSan and Miri all have nothing to say.** ▶ ⭐ **So the row prices what a
> dispatch representation actually buys: it converts a NULL indirect call into a
> panic, and does NOTHING about the wrong program counter that caused it.**
> **That contrast is the best crash-course material in the corpus** and it is
> one byte wide.
>
> ⭐⭐⭐ **AND A THIRD BEHAVIOUR NOBODY PREDICTED: `unsafe.rs` WITH THE BUG DOES
> NOT CRASH ON THE NULL CASE.** `unwrap_unchecked` on a `None` is UB, LLVM took
> it, and the program **ran to completion** printing a **third** value agreeing
> with neither C nor R1h. ▶ ⛔ **On that input, unsafe Rust carrying the bug is
> STRICTLY WORSE THAN C — C at least segfaults.** That is the
> `unwrap_unchecked` lever's real price, and it is why `miri.required` is `true`.

⛔⛔ **AND VERUS DOES NOT SUPPORT FUNCTION POINTER TYPES — *"the verifier does not
yet support the following Rust feature: function pointer types"* — WHICH IS THIS
ROW'S OWN MECHANISM.** It is a **type-level** refusal, not a proof failure: an
`external_body` wrapper does not help, because **any Verus-visible signature
mentioning `[Option<fn(..)>; N]` is refused**, so the op_array would have to be
opaque — and an opaque op_array cannot carry the value postcondition. ▶ **All
four Rust rungs therefore store an `Option<u8>` handler ID and dispatch with a
`match`**, and that is **not a choice R4 could have made differently**: `identity`
pins R4 ≡ R5, so **a representation R5 cannot express is one R4 may not use.**
✅ **It changes no answer** (`Option<fn>` and `Option<u8>` are `None` for exactly
the same opcode, measured on the adversarial pair) and it is **priced**:
`+14.40 %` / `+12.41 %` **W1**, in the direction that **favours** the shipped
rungs. ⭐ `controls/fnptr.rs` is a **must-fire negative** run on every invocation.
ⓘ `CLAUDE.md` rule 6: *"the R5 can't state the obligation"* is a **FINDING**.

**FOUR OF MY FIVE PREDICTIONS REFUTED.** R3/R4 endpoints — **REFUTED IN BOTH
HALVES, signs exactly swapped**. *"The fix costs something"* — **REFUTED: free
under clang, PROFITABLE under gcc** (⭐ `n = 2` with `ph52`, and item 76's column
keeps losing). *"`inside_share` high everywhere, A1 resolves this row"* —
**REFUTED for the C cells**. The catalogue's `narrowed` tier — **REFUTED by
measurement; the row declares `modelled`.** ✅ **Only the twin prediction held**
— `n_twins = 8`, twins verify **61/0**, `twin_justifications` **empty**, **no
hatch and no blocked row** — ⭐ **so `ph55` is the control proving F97's
narrowing: the joint unsatisfiability is a property of the `MaybeUninit` ITEM,
not of php rows.**

> ### ⛔⛔ AND A1 IS **STRUCTURALLY BLIND TO THIS ROW'S OWN DEFECT SITE**, AT `inside_share` **74–83 %**
>
> `c/kernel.c` and `c/kernel_hardened.c` compile to a **byte-identical `kernel`
> symbol** under both compilers (`asm.py` level **`exact`**) — **and one of the
> two binaries SEGVs while the other answers.** The defect lives in
> `ph55_binary_assign_op_helper`, reached through the function-pointer table and
> therefore **not inlinable**. **A1 reports the upstream fix at `0.000 %` on
> every C cell.**
> ▶ ⭐⭐ **THE LESSON IS ABOUT THE RULE: what matters is not how much of the cell
> A1 sees, but whether THE DIFFERENCE lands inside it. `inside_share` at 74–83 %
> is HIGH and A1 is STILL blind.** ⛔ **Do not read a high `inside_share` as a
> certificate.**

### F108 — ⭐⭐⭐ **TWO PUBLISHED CLAIMS IN THE AUTHORITATIVE LAYER CHANGE SIGN WITH THE C COMPILER — AND THE RULE THAT FORBIDS THAT HAS BEEN IN `.memory/` SINCE `TASK_001`, UNINHERITED**

`TASK_PHP_049`. ⚠ **UNREVIEWED** (rule 9). ⓘ **The task was dispatched to
FALSIFY the manager's item 111, and it did — then found something larger.**

> ### ⛔ FIRST, THE MANAGER'S HEADLINE IS **REFUTED**, BY THE ATTACK THE TASK WAS HANDED AS MOST LIKELY TO KILL IT
>
> Item 111 claimed *"A1's cross-language anomaly on `ph29` may be a `gcc`
> property, because against `c-clang` A1 agrees with the three other
> statistics."* ⛔ **The three other statistics were THEMSELVES computed against
> `c-gcc`.** Like-for-like against `c-clang`, C and W1 are **`−27.78 %` /
> `−27.61 %`**, nowhere near ~1 %. ⛔⛔ **And the direction is backwards:**
> F85's 29 cross-language flips split **21 `c-clang` to 8 `c-gcc`** — above a
> 1-pp floor, **17 clang to 0 gcc**. ▶ **If the thread is anyone's property it is
> CLANG's.** ⭐ **Handing over the strongest counter-attack in the task file is
> what made this cheap: the task went to it first.**

**WHAT SURVIVES AND IS WORTH MORE.** The swap flips **10 of 128** A1
cross-language cell-pairs — **15.6 % at `O3/isolated`, `0 %` at `O0`** — across
**four of eight rows**, and all 24 tabulated cells reproduce to the digit.
▶ **So the effect is real, corpus-wide and not cherry-picked; what was wrong was
the STORY about which compiler it indicts.**

> ### ⭐⭐⭐ AND TWO **PUBLISHED** CLAIMS CHANGE SIGN — BOTH IN `.memory-php/`, THE LAYER THAT OUTRANKS EVERYTHING
>
> **1.** `.memory-php/02-ladder.md`'s **`ph03` ROW-1 HEADLINE TABLE**, five
> percentages with **no baseline named**: *"unsafe and verus are **7.6 %
> FASTER** than C"* becomes **`+9.17 %` SLOWER** against `c-clang`, on **both**
> inputs, at 5.7–10.8 pp. ⛔⛔ **`ph03`'s OWN `NOTES.md:692-697` ALREADY SAID SO**
> — *"unsafe Rust beats gcc C on this kernel and loses to clang C, and the clang
> column is why that must be stated as two numbers."* ▶ **The ROW got it right
> and the AUTHORITATIVE LAYER dropped the column**, which is `CLAUDE.md`'s
> `SYNTHESIS`-beats-`RECAP` pattern **one level deeper.**
> ⚠⚠ **And the bullet two lines below that table warns that *"`c-clang` beats
> `c-gcc` by 15.4 %, larger than every safety effect on this row"* — the file
> warned about the effect and then published the table the effect reverses.**
>
> **2.** The **central claim** — *"A says C is +33 % dearer; B, C and W1 all say
> ~1 % cheaper"* — sits in a **182-line unit that contains neither `c-gcc` nor
> `c-clang`** and that says of itself *"THIS is the layer that outranks
> `RECAP_PHP.md`."* ⭐ **I had blamed the RECAP summary cell. The unlabelled
> copy was in the layer above it.**

⭐⭐⭐ **THE ROOT CAUSE IS AN UN-INHERITED RULE, WHICH MAKES THIS A REDISCOVERY
RATHER THAN A DISCOVERY.** `.memory/02-bench-rules.md` has said since `TASK_001`:
*"never report a C-vs-Rust number **without saying which C compiler**"* and
*"**never report a perf number from an `O0` row**"*; `.memory/01-ladder.md`:
*"**always report a clang column**"*, clang being *"the same-backend baseline and
**mandatory for any C-vs-Rust claim**"*, measured on the PAT pilot at **+42.9 %**.
⛔ **`grep -a clang .memory-php/*.md` returned ONE line, and it was an
observation, not a rule.** ▶ ✅ **Landed in `03-numbers.md` as the FIFTH thing
every percentage owes, with `ph03`'s weaker *"quote a rung against a rung"*
RETIRED rather than kept beside it** — *two rules of different strength on one
question is how the weaker one gets cited.*

⭐⭐ **AND THE CONFOUND IS SETTLED WITHOUT BUILDING FAMILY C.** On `ph29` the
gcc→clang gap is **`−28.09 %` (A1) / `−27.01 %` (C) / `−26.74 %` (W1)** — **W1 is
immune to symbol boundaries and still sees it**, which also **refutes the
cold-helper alternative** the task was told would restore the confound. ⚠ **Seven
rows have no C-cell profiles: UNTESTED.** → item **62**'s new requirement.

⛔ **THREE CORRECTIONS TO MY OWN NUMBERS, AND ONE RULE I BROKE WHILE
REDISCOVERING IT:** *"six of eight"* is **five**; the premise was **backwards**
(at `O0` six cells move between `isolated` and `whole` and **all six are
`c-clang`**); the summary triple mixed two populations. ⚠⚠ **And two of my
table's three columns were `O0` — which `.memory/02-bench-rules.md` forbids
reporting a perf number from. I violated the rule inside the item that
rediscovered it.**

### F107 — ⭐⭐⭐ THE REVIEW ROUND: **SIX FINDINGS VERDICTED, NOT ONE SURVIVED AS WRITTEN — AND IT REFUTED THE ONE THING THAT WAS WAITING ON THE USER**

`TASK_PHP_047`, 851 lines, brackets `66/0` and `18/0` unmoved first and last.
⚠ **UNREVIEWED** (rule 9) — ⓘ *a review round is itself a finding and gets the
same treatment; `_043` and `_044` both did.*

| finding | verdict |
|---|---|
| **F106** | ✅ **UPHELD, and UNDER-STATED three ways** |
| **F97 · F102 · F104** | ⚠ **UPHELD-NARROWED** |
| **F105** | ⛔ **REFUTED** in the `97.6 %`; ✅ **UPHELD** in the `0.82 %`, which **grows to `1.02 %`** |
| **F103** | ⛔ **REFUTED** — the decomposition is `8.19 / 3` written as a product |
| **F96** | ⛔ **still UNREVIEWED**, and the reviewer checked first whether `ph52` supplies the missing second method. It does not |

> ### ⛔⛔⛔ THE HEADLINE: **OPTION (b) DOES NOT EXIST**, AND I HAD PUT IT TO THE USER AS MY RECOMMENDATION
>
> Item 105 asked the user to choose between editing `harness/check.py` (a
> 33-pattern re-gate), **overriding the stage in `harness-php/`**, or leaving a
> verified zero-cost TCB reduction out of the corpus. **I recommended the middle
> one.** ⛔ **It is not available, on three independent grounds already written in
> the committed tree** — `harness-php/gate.py`'s own header forbids it hosting a
> gate stage (*"a second, unvalidated gate wearing the first one's name"*); it
> **cannot make itself mandatory** (`grep -c preflight harness/{check,measure,report}.py`
> = `0 0 0`, re-run by the reviewer), so **no gate record could witness the
> exemption**; and `root.py` rebinds **paths**, not verdicts. ⭐⭐ **I read
> `CLAUDE.md`'s *"imports `harness/` and rebinds at run time"* banner as a verdict
> override. It is about path roots.** ▶ **The question is (a) or (c), and (c) is
> what `gate.py`'s header itself prescribes.**

⭐⭐ **AND THE ROUND'S METHOD LESSON IS ONE THE PROGRAMME CAN USE: THREE OF THE
FOUR REFUTATIONS CAME FROM A **SECOND INPUT** OR A **SECOND DOCUMENT**, NOT FROM
A CLEVERER ARGUMENT.** F105's `97.6 %` died on `large.bin` (`102.4 %`, residual
changing sign) — **a slope needs two inputs and one input could not see the
error**; F103's decomposition died on a **second normalisation** (changing only
the input moves `ph52`'s witness cost `12.24 → 28.92`, a `2.36×` comparable to
the `2.73×` the model attributes to a mechanism); F106's relocation objection
died on a **document nobody had cited** (`.memory/04-verus.md`'s census-backed
ruling, with `p06`'s `copy_from_slice` TCB 6 → 5 as an exact precedent).
▶ **Cheapest next method first: another input, another document, another row.**

⭐ **FIFTH CONSECUTIVE ROUND TO REFUTE MANAGER OR ENGINEER CLAIMS** (F80/F82/F83/F84
→ F90 → `_043` → `_044` → this), which makes `04-process.md` **law 12** the
best-supported process law on file. ⚠ **14 uncertainties declared; depth ran out
after §5 plus the §1.7 excursion, and the reviewer said where.** ▶ **Next on that
thread: price option (a)'s PAT-side blast radius.**

### F106 — ⛔⛔⛔ **THE HARNESS PINS A MEASURED TCB REDUCTION *OUT* OF THE CORPUS**: ONE FEWER AXIOM, **BYTE-IDENTICAL**, 34/0 VERIFIED — AND UNSHIPPABLE

`TASK_PHP_046` §4. ✅✅ **REVIEWED `TASK_PHP_047` §1 — UPHELD, AND *UNDER-STATED*,
WHILE ITS RECOMMENDATION IS REFUTED.** The reviewer reproduced all three refusals
from `check.py` **itself** rather than from `spellings.py`'s reimplementation,
confirmed the refusal site at `verus.rs:548`, and corroborated the `33 → 34`
**three independent ways including a negative arm**: deleting the `requires`
drops it back to 33 and errors **at `vstd/std_specs/maybe_uninit.rs:46`** — so an
axiom really did become a proof obligation. ⭐⭐ **UNDER-STATED THREE WAYS: (1)**
the published axis **is** the gate's `tcb_items` and **deliberately does not count
vstd**, by a census-backed decision in `.memory/04-verus.md` **I never cited**,
with `p06`'s `copy_from_slice` (**TCB 6 → 5, byte-identical `-O3`**) as an exact
precedent; **(2)** on `check.py`'s own `_is_trusted` the drop is **2 → 1**, not
4 → 3, because `_is_trusted` excludes trusted I/O — **the security-bearing count
HALVES**; **(3)** removing `external_body` also removes the hole `.memory/04-verus.md`
measured, where a trusted body can commit the pattern's own UB invisibly to Verus,
to the twin, to the contract pin and to stages 5c/5c-req. ⚠ **Quote it as *"a
reduction on the published `tcb_items` axis"*, never *"in the trusted base"* full
stop** — `unsafe_tokens` (2) and `trusted_call_sites` (11) do not move, and the
accounting rule is flagged **PROVISIONAL** in the PAT layer. ⛔⛔ **AND ITEM 105's
OPTION (b) DOES NOT EXIST** — see item 105. ⭐⭐⭐ **THE FIRST TIME EITHER F97
OR F104 HAS BEEN MEASURED ON A *RUNG CANDIDATE* RATHER THAN ARGUED.** `ph52`'s R4
search found **three** variants with a **smaller trusted base**, and
**`harness/check.py` refuses ALL THREE** — measured against its own `_is_trusted`,
`vparse` and `_UNSAFE_RE`:

| variant | trusted base | cost | verus | refused by |
|---|---|---:|---|---|
| ⭐⭐ **`r4_no_wrapper`** | `external_body` **4 → 3** | **`+0.00 %`, BYTE-IDENTICAL `kernel`** | **34 verified / 0 errors** | **F97**'s `_scan_unsafe_sites` (`5-tcb-unsafe`) |
| `r4_win_checked` | smaller | — | — | **F104**'s `n_twins == 0` |
| `r4_win_oprec` | smaller | — | — | **F104**'s `n_twins == 0` |

> ⭐⭐⭐ **`r4_no_wrapper` IS ONE FEWER AXIOM AT ZERO COST AND ZERO BYTES OF
> DIFFERENCE, AND IT CANNOT SHIP.** The trusted base is one of this project's
> **published** axes, and here the gate refuses a strict improvement on it for a
> reason that has nothing to do with the row.

⛔⛔ **SO F104 IS NO LONGER *LATENT*. IT IS PINNING A MEASURABLE, VERIFIED,
ZERO-COST TCB REDUCTION OUT OF THE CORPUS** — and that converts item **105** from a
tidiness question into a **decision with a measured price on both sides.**
✅ **AND NOTHING WAS ADDED TO THE TRUSTED BASE TO ESCAPE IT**, which the task
forbade: the engineer reported the refusals instead. ▶ **That is the right call and
it is what makes the measurement trustworthy.**

### F105 — ⭐⭐⭐ `ph52`'s **R3 MOVES AND ITS R4 IS DEGENERATE**; THE GAP IS A **SPELLING**, NOT A MECHANISM; AND ⭐ **A *SAFE* RESPELLING BEATS THE SAME RUNG WITH EVERY BOUNDS CHECK REMOVED**

`TASK_PHP_046`, 812 lines, **15 variants**, **24 §H arms inside the validator**.
⚠ **UNREVIEWED** (rule 9). ✅ **Manager-verified and SAYING WHICH FILE**: from
**`results-php/gate/ph52-…json`** — `verdict PASS-WITH-BLOCKED-ROWS`, `failures []`,
`complete_run true`, `contract_sha256 d73ab3298ecd` **UNCHANGED**, `controls_json
{} → {"spellings.json": "FRESH"}`, `identity O0 differ / O3 norel`; from
**`controls/spellings.json`** — `problems []`, `r3_endpoint_degenerate false`,
`r4_endpoint_degenerate true`, `cheapest_r3_in_contract r3_chunks_exact`,
`a1_spread_pp {R3: 7.923098, R4: 7.769824}`. **Brackets `66/0` never moved;
`18/0 → 18/1 → 18/0`, the stale record being the GATE record. NO measurement record
went stale and `spec.md` was not touched.**

| side | verdict | |
|---|---|---|
| ⭐ **R3** | **MOVES** | `r3_chunks_exact` **−7.42 % A1** (1930.232 vs 2085.038 `Ir`/call, **`small.bin`, `O3/isolated`, A1**) |
| ⛔ **R4** | **DEGENERATE** | `true` **with AND without** the gate-rule filter — so on **cost** it joins `ph07` and `ph16`. Best R4 variant is a **byte-identical tie**. ✅ **No variant was manufactured** |

⛔⛔ **AND THE `fixed-R4 bound`'s ORDERING REVERSES** — published, R3 is **`+6.71 %`
dearer** than R4; cheapest in-contract R3 is **`−1.21 %` CHEAPER**. ⭐ **Second row
after `ph45` (F87) where search reverses the ordering, so that is now `n = 2` and not
an anecdote.** ⛔ **ORDERING, NEVER AN INTERVAL** — the shared `why` forbids
publishing a pair interval and the report does not compute one.

> ### ⭐⭐ THE R3 ANSWER IS **SPELLING**, WHICH IS THE **OPPOSITE** OF `ph53`'s
>
> ⛔⛔⛔ **THE `97.6 %` IS REFUTED (`TASK_PHP_047` §2, 2026-09-13): IT IS TWO
> ERRORS CANCELLING ON ONE INPUT.** On `large.bin` (cap 43) the same construction
> gives **`102.4 %` with the residual CHANGING SIGN**, and the row's own
> `ctl_r3_unchecked` control measures the same term at **105.8 % / 105.6 %** of
> the gap on the two inputs — the two directions disagree by **9.1 %**, because R4
> carries an opposite-signed second term (R3 with its window checks removed is
> **cheaper than the shipped R4**). ⭐⭐ **WHAT SURVIVES IS BETTER AND IS A
> TWO-INPUT SLOPE: `7.9855 Ir per op` against a predicted `8.00`, plus a fixed
> `+11.1 Ir/call` the model omits.** ▶ ⭐ **A slope needs two inputs, which is
> exactly why one input could not see the error** — and `check.py`'s own *DO NOT
> MAX IT OVER INPUT* is the same lesson in the other direction.
> ⛔ **DO NOT REQUOTE `128.00 of 131.19 = 97.6 %`.**
>
> The 6.71 % R3−R4 gap is **four per-op window bounds checks** — four
> `cmp %rdi,<stack slot>` / `je <panic>` pairs, ~~**8 instructions × 16 ops =
> `128.00 Ir/call` against a measured `131.19`, i.e. 97.6 % attributed**~~.
> Panic-call-site column: R3 **5**, R4 **1**, `r3_chunks_exact` **1**. ✅ **Two
> independent nulls localise it** — `r3_head_slice` is **byte-identical** to the
> shipped rung, and `r4_oprec_checked` puts the same checks back into R4 at
> **`+7.77 %`**. ⛔ **This CORRECTS the row's own §8c/§10 reading**, which framed the
> gap as `Option` vs `MaybeUninit`+witness. ⭐ **`ph53`'s answer was *mechanism* and
> this row's is *spelling*, so the question was worth asking both times.**

⭐⭐⭐ **AND THE RESULT THE PROGRAMME DID NOT HAVE: A SAFE RESPELLING BEATS THE
SAME RUNG WITH EVERY BOUNDS CHECK REMOVED.** `ctl_r3_unchecked` — the shipped R3
with `win.get_unchecked` everywhere — is **`−6.66 %`**, and `r3_chunks_exact` is
**`−7.42 %`**: **the safe spelling wins by `0.82 %`**, because `get_unchecked`
deletes the checks and **leaves the offset arithmetic**. ⛔ **The engineer had built
that control as *"the ceiling of the R3 search"* and retracted the claim in the
sidecar under `ctl_r3_unchecked_is_not_an_upper_bound`.** ✅ **It is still the right
control — it isolates the bounds-check term at the shipped spelling, which is what
makes the 128-of-131 attribution checkable — but it bounds nothing.**

⚠⚠ **AND F101 FIRED *LIVE*, IN BOTH DIRECTIONS, ON A THIRD ROW.** In a fresh clone
the path-sensitive `kernel_fingerprint` produced **one false POSITIVE** (two
different sources reported byte-identical) **and two false NEGATIVES — 3 of 6
compared pairs.** ✅ Repaired in this row's control with a **fixed-width `vNN`
scratch slug plus an asserted equal-path-length invariant**, and exec-vs-twin now
goes through `asm.py::identity_level` at `norel`. ▶ **So F101's *"LATENT on `ph53`,
LIVE on `ph29`"* becomes *LIVE wherever a search compares across directories*, and
the false-POSITIVE direction is new** — **that one CAN manufacture a byte-identity
claim**, which is the direction `_043` §5.1 ruled impossible for `ph29`. ⚠ **`ph29`
is still safe for the reason `_043` gave (its digests are equal), but the general
claim that the defect cannot fabricate identity is WITHDRAWN.** → item **109**.

⭐ **§H: 24 arms in 3 batteries INSIDE the validator** (11 must-fire, 13
must-NOT-fire), all feeding `problems`. ✅ **`citecheck.py`'s §H-at-risk count is
UNCHANGED at 13 across the same 4 rows — `ph52` contributes none**, which is item
97's repair working on the first row built after it.
✅ **§2's statistic call CONFIRMED by the engineer's own measurement**:
`inside_share` **98.56–98.68 %** on all 15 Rust cells against **22.24 %** on
`c-gcc`; **A1 reproduced the shipped record to `0.0000 %`** in four cells, W1 to
`0.0006 %`. ⭐ **Spreads published filtered AND unfiltered, and they are identical
on this row** — which settles `_044` §3.4's open question for this row by measuring
both.

### F104 — ⛔⛔⛔ THE GATE'S `n_twins == 0` RULE **HARD-FAILS THE ROW WHOSE TRUSTED BASE IS SMALLEST**, SO IT PRESSURES A ROW TO **ENLARGE** ITS TCB

`TASK_PHP_045` §8.1. ⚠ **UNREVIEWED** (rule 9). **`ph52`'s first gate run FAILED
at stage 5c-twin**, and the message was right about the row: with
`slot_read_unchecked` as its **only** contract-bearing trusted item, and that item
**genuinely untwinnable**, *"stage 5c-twin checked the strength of NOTHING."*

⛔ **WHY IT IS UNTWINNABLE, AND IT IS NOT INCONVENIENCE.** A twin must be a
**verified exec** function meeting the same contract, whose `ensures` here is
`r == m.mem_contents().value()` — so its body must get a `Pr` **out of** a
`MaybeUninit<Pr>`. **The pinned vstd offers exactly three routes — `assume_init`,
`assume_init_ref`, `assume_init_mut` — and ALL THREE ARE `unsafe fn`.** ⭐ **There
is no safe exec expression from `MaybeUninit<T>` to `T`; that is what the type
MEANS.** So any twin's body carries an `unsafe` token outside a trusted body, which
`check.py::_scan_unsafe_sites` refuses **with no justification hatch.**

> ### ⛔⛔ AND THE PERVERSE INCENTIVE, WHICH IS THE PART THAT MATTERS
>
> **`ph53` PASSES THIS STAGE PRECISELY BECAUSE ITS TRUSTED BASE IS LARGER** — four
> items, three of them twinnable `get_unchecked` accessors on a `Vec`. **`ph52` is
> the first row in either programme to reach the failure, because it is the first
> whose trusted surface is SMALL enough.**
> ▶ ⭐⭐ **So the rule puts pressure on a row to ENLARGE its trusted base** —
> which is `.memory/02-bench-rules.md`'s *a rung is never cost-selected*, one axis
> over, and the trusted surface is one of this project's **published** axes.
> ⚠⚠ **AND IT REPRODUCES AT `n = 1` THE DEFECT `TASK_007` DELETED
> `MAX_TWIN_JUSTIFICATIONS` FOR, WITH `check.py`'s OWN COMMENT SAYING SO:** *"It
> was the only knob in the twin regime that could hard-fail an **honest** pattern
> with no route out. A pattern with two genuinely untwinnable trusted items had no
> legal configuration."* ▶ **A pattern with ONE has no legal configuration
> either.**

✅ **F97's SECOND INSTANCE, AND THAT MAKES IT A PROPERTY OF THE RULE PAIR RATHER
THAN OF A ROW** — found on `ph53` with **four** trusted items, reproduced here with
**one**. ⛔ **NOT worked around**: the fix is a `harness/` edit and a **33-pattern
re-gate**, recorded in the row's `NOTES.md` §11f and here. → item **105**.
⭐ **The pressure is LATENT rather than live on this row**, because the row found a
legitimate way out that it owed anyway — `win_get_unchecked`, **a fidelity repair
worth `−7.12 %`**: every window read in the C is an unchecked array access, and the
Rust rungs had been paying for bounds checks the C never had.

### F103 — ⭐⭐⭐ **ROW 8 IS BUILT** — `ph52`, T3's second row, and it **REFUTED FIVE OF MY STATEMENTS, ITEM 76's COLUMN, AND THE LAW I HOPED FOR**

`TASK_PHP_045`, 1519 lines. ⚠ **UNREVIEWED** (rule 9). ✅ **Manager-verified from
`results-php/gate/ph52-concat-copy-uninit.json` and SAYING WHICH**: `verdict
PASS-WITH-BLOCKED-ROWS`, `failures []`, `complete_run true`, `contract_sha256
d73ab3298ecd`, `identity` **`O0 differ` / `O3 norel`**, **1 blocked row** (F104),
**0 advisories**. **Brackets: `66/0` unmoved and `16/0 → 18/0`, the `+2` being
exactly this row's two records with the other eight rows FRESH — re-run by me.**
⭐ **`quota.py`: 8 built, T3 CLOSED, 32 owed.**

> ### ⭐⭐⭐ ITEM 76 IS **UPHELD IN FAMILY A AND REFUTED IN W1 — AND THE UPSTREAM FIX IS NOT FREE, IT IS *PROFITABLE***
>
> | statistic | R1 | R1h | Δ |
> |---|---:|---:|---:|
> | **A1** | 32,509,505 | 32,509,505 | **0, exactly `0.00 %`** |
> | **W1** ⭐ | 146,152,976 | 145,653,146 | **`−0.342 %`** (clang `−0.740 %`) |
>
> **`small.bin`, `O3/isolated`, R1h against R1** — same language, same allocator, so
> §B1a's caveat does not apply. ⓘ B1 and W1 agree to rounding.
> ⛔⛔ **AND FAMILY A's ZERO IS *BLINDNESS*, NOT ABSENCE, WITH THE MECHANISM NAMED
> BY A PER-FUNCTION SPLIT**: `ph52_zval_dtor` **−382,226**,
> `ph52_make_printable_zval` **−117,608**, `kernel` **0** — summing to the
> −499,834 total. ⭐ **F86's `BLIND` class, on a row where the blind quantity is the
> row's own headline, and the FIRST use of `.memory-php/03-numbers.md`'s new rule:
> `inside_share` was measured FIRST and it chose W1.**
> ▶ ⭐⭐ **WHAT THIS PUBLISHES, with the sign I did not predict:** *the upstream
> fix for a whole CLASS of defect — the unreached-error-path teardown — does not
> merely cost nothing, it PAYS FOR ITSELF*, because R1 calls the teardown once per
> faulting-arm op and R1h does not. ⚠ **Small — a third to three quarters of one
> per cent — and small for a stated reason.** ⛔ A `0.00 %` column would have been
> a finding, not a disqualification (`CLAUDE.md` rule 6); **a negative one is a
> better finding and the row did not have to choose.**

✅✅ **PREDICTION 1 (F97/F98 RECUR) — UPHELD, AND MORE STRONGLY THAN ON `ph53`** →
**F104**. ⚠⚠ **PREDICTION 2 — UPHELD IN DIRECTION, *"~FREE"* REFUTED, AND THE LAW
I HOPED FOR IS REFUTED OUTRIGHT.** The witness costs **`+12.41 Ir/call`
(`+0.632 %`)**, B1 and W1 agreeing to `+0.622 %` — real and reproducible, an order
of magnitude under `ph53`'s, **but not free**:

| | `ph53` | `ph52` | ratio |
|---|---:|---:|---:|
| witness, **Ir per kernel call** | **+101.59** | **+12.41** | **8.19×** |
| slots | 6 typical | 2 | 3× |
| **Ir per slot per call** | 16.93 | 6.21 | **2.73×** |

⛔⛔ **MY *"the cost of a safety witness is O(the number of slots)"* IS REFUTED**:
3× the slots gives **8.19×** the cost, because the **per-slot** term is itself
**2.73×** higher. ✅ **THAT REFUTATION STANDS — `TASK_PHP_047` §3 upheld it.**

> ### ⛔⛔⛔ BUT THE REPLACEMENT IS **REFUTED** (`TASK_PHP_047` §3, 2026-09-13)
>
> The proposed replacement was *"a DECOMPOSITION, not a law — `(slots) × (per-slot
> cost)`"*. ⛔ **It is `8.19 / 3` written as a product: an identity with a free
> parameter fitted from the same two points it explains, carrying ZERO
> information.** A decomposition that cannot fail is not a model.
> ⛔⛔ **AND IT IS WORSE THAN EMPTY — THE NUMBER IT USES CONTRADICTS THE MECHANISM
> IT NAMES.** The `+101.59` is `ph53`'s **`r4_bitmask`, REGISTER-RESIDENT** arm —
> so the *"indexed array read vs register-resident `bool`"* contrast is drawn
> between **two register-resident variants**, and one of the two candidate
> mechanisms is **excluded by the very measurement offered to distinguish them.**
> ⚠ **And *"Ir per kernel call"* is NOT row-invariant**: on `ph52` alone, changing
> only the input moves the witness cost **12.24 → 28.92 (2.36×)**, which is
> comparable to the `2.73×` the decomposition attributes to a mechanism.
> ▶ ⭐ **WHAT SURVIVES: the refutation of my `O(slots)` law, and nothing that
> replaces it.** A third `T3` row is still the route (`ph49`, `ph50`, `ph51`), and
> it must normalise per **call AND per input** before comparing rows.
> ⓘ ✅ **The decomposition was never in `.memory-php/`**, so this cost a RECAP
> edit and no removal from the layer — which is rule 9 working.

⛔⛔ **AND DELIVERABLE #0 SETTLED BY BREAKING FIVE OF MY STATEMENTS** — the defect
is deterministic on **14 of 16 cells** and the fault is a **real double free**, but:
**(1)** *"a clean stack slot reads zero"* is an **ASan** property, **not a property
of the shipped build**; **(2)** the load-bearing boundary is **NOT** the harness's
`isolated`/`whole` — it is the **callee inline boundary**, which `build.py` does not
control, **so my registered TU-boundary prediction was about the wrong boundary**;
**(3)** fallback (a) as I wrote it **does not fire** — the call history needs **two
different arms**, not a repeated one; **(4)** **ASan deletes the defect by
RELOCATING THE FRAME**, not by poisoning; **(5)** F102's *"five named cases out of a
byte"* is **wrong in three ways** (§3.1). ✅ **Only hypothesis 3 — the offset is
exact — survived.**

⭐ **AND THE BACKTICK LAW (item 100) FIRED ON THIS ROW'S OWN DRAFT**, because the
engineer did not run the audit first — *§8.3* — **plus a second, worse one the same
audit found in `required`, where the gate cannot see it** (§8.4). ▶ **Two rounds,
three authors, same defect: the law needs to be a STEP, not a sentence.**

### F102 — ⭐⭐⭐ ROW 8's GROUNDWORK: `ph52` IS ADMITTED ON THE C — AND **THE DEFECT IS SILENT ON A CLEAN STACK**, WHICH IS WHY LOGIC-007 HAS NO CRASH ANCHOR

Manager, 2026-09-13, while `_043` ran. ⚠ **UNREVIEWED** (rule 9).
✅ **Read from the PRISTINE TARBALL** (`5783e0c0ba94f165…`), **not** from
`CATALOGUE.md`, not from `index.csv`, not from the Rust port. Staged notes and the
full build brief: `.temp/mgr176/{NOTES.md,PH52_BUILD_BRIEF.md}`.

**The C.** `Zend/zend_operators.c:1146` `concat_function` declares **`zval
op1_copy, op2_copy;`** — bare stack locals, **no `= {0}`, no `INIT_ZVAL`, no
`memset`** — and passes `&op1_copy` to `zend_make_printable_zval`, which writes
`expr_copy->value.str.*` on every arm and `expr_copy->type` **once, at `:263`,
after the switch**. The faulting arm is `:242-247`:
`if (EG(exception)) { zval_dtor(expr_copy); … break; }` — **a tag-dispatched
teardown over a tag byte nobody has written.** ⓘ On the COMMON path
(`:190-193`, `expr` already a string) **`expr_copy` is never written at all**, so
the function's own convention is *constructed only if `*use_copy`* — and the
early exit destructs it anyway. ✅ **ADMITTED on all three C-side conditions
(`CLAUDE.md` rule 6), and distinct from its own family-mate `ph53` on four
counts**: heap vs **stack** · a pointer value vs a **discriminant** · a fold vs a
**dispatch** · a wild deref vs a **wrong-arm teardown**.

> ### ⛔⛔⛔ THE MEASURED RESULT, AND IT CHANGES THE ROW: **A CLEAN STACK SLOT IS `IS_NULL`, AND `zval_dtor` NO-OPS ON IT**
>
> **Measured on this box** (`.tasks-php/asan_fill_byte.c`, generator kept, binaries
> deleted), `clang -O1 -fsanitize=address`: fresh `malloc(64)` reads
> **`be be be be be be be be`**; an un-initialised `stack[64]` reads
> **`00 00 00 00 00 00 00 00`** — **with and without the sanitizer.**
> **And from the pristine C**: `Zend/zend.h:387-392` gives **`IS_NULL 0`**,
> `IS_STRING 3`, `IS_ARRAY 4`, `IS_OBJECT 5`; `Zend/zend_variables.c:36-57`
> `_zval_dtor` switches on `zvalue->type & ~IS_CONSTANT_INDEX` over
> `IS_STRING`/`IS_CONSTANT`/`IS_ARRAY`/`IS_CONSTANT_ARRAY`/`IS_OBJECT` and has
> **no `case IS_NULL`**.
>
> ▶ **THREE CONSEQUENCES.**
> **(1)** ⛔ **The adversarial input is not a blob property, it is a CALL-HISTORY
> property** — a prior frame must leave a freeing tag at that offset. **That is
> row 8's deliverable #0, and it must hold on all four C cells**, because the
> offset is a compiler layout decision.
> **(2)** ⭐ **It EXPLAINS the missing fidelity anchor rather than excusing it.**
> LOGIC-007 records `uninit-read-silent` **because the real bug usually IS
> silent**: most garbage is zero or is not one of the freeing tags. ▶ **That is a
> better §A4 answer than a divergence note.**
> **(3)** ⭐⭐ **And it gives the row a number no built row has: the harm is
> CONDITIONAL ON THE GARBAGE VALUE, and the condition is small and countable** —
> five named cases out of a byte, widened by the mask. ▶ **A `controls/` sweep
> over the tag byte `0..255` counting which values free is the whole control.**
> ⭐ **That figure is the answer to *why do uninitialised-read bugs survive for
> years in shipped code*** — which is exactly what a reader of this ladder needs.
> ⚠ **UNTESTED: the five-of-256 is read off the `switch` and the mask and has not
> been compiled.**

⛔⛔ **AND `ph53`'s OWN DETERMINISM DID NOT COME FROM THIS TREE EITHER — REPORTED
FOR ROUTING, `ph53` NOT EDITED.** Its R1 reports `0xbebebebebebebebe`, and
**`0xbe` is ASan's malloc fill byte, measured above.** The shim **zeroes** fresh
blocks and poisons **`0x5a` on free**; it has no fresh-garbage pattern. ▶ **So
`ph53`'s `cwe_note` describes a DETECTOR-DEPENDENT observation as a row
property.** → item **96**.

⚠⚠ **TWO EXTRACTION TRAPS `CATALOGUE.md` DOES NOT STATE** (it states only
*"an extraction that zero-initialises the slot for tidiness deletes it"*):
**(a)** ⛔ **the defect lives in the WRITE ORDER** — the tag is written **last**,
so **any kernel that writes it early, which is the tidy ordering a careful author
reaches for, deletes the defect while keeping every line that looks
load-bearing.** ▶ **`value`-first / `tag`-last is a PINNED ORDERING.**
⚠ **And the trap applies to the COMPILER too**: `-ftrivial-auto-var-init` or any
stack-poisoning mode removes it.
**(b)** ⛔ **the faulting operation is a tag-dispatched *FREE*, not a read** —
the freeing arms **release a pointer read out of the same uninitialised slot**, so
a kernel whose teardown merely *branches* has built a weaker row.

⭐⭐ **AND A PREDICTION REGISTERED BEFORE ANY RUNG EXISTS, so it can fail.** The
uninitialised datum here is a **discriminant**, so **F97/F98 should recur**:
R2/R3 cannot reproduce it at all (ⓘ **a FINDING, never a kill**), and R4/R5 need
`MaybeUninit::<Tag>::assume_init`'s `is_init()`, which is a property of the
failure flag — attacker data — exactly as on `ph53`. ⚠⚠ **BUT A WAY IT SHOULD
DIFFER, WHICH IS WHAT MAKES IT FALSIFIABLE: `ph53`'s witness is PER-SLOT (`n`
bits, priced at F98's `+21.775 %`); `ph52`'s is ONE SLOT, ONE BIT —
`constructed: bool`.** ▶ **Predicted ~FREE here.** ⭐ **If free on `ph52` and
dear on `ph53`, the cost of a safety witness is O(the number of slots) and not a
constant — a better statement than either row gives alone.**

⛔⛔ **AND *"CHEAPEST CANDIDATE"* IS WITHDRAWN FROM THE START HERE BOX.** `_040`
§7.2 ranked `ph52` **below** `ph53` on three measured grounds and I carried only
one forward: its R1h is a **hand reconstruction**, not a `patch -p1` (§C owes an
argument), and it has **no fidelity anchor**. ▶ **The honest phrasing is *lowest-risk
R1h, highest-risk adversarial input*.** ⭐ **And the deeper correction is to my own
cost model: `ph52` is SECOND-in-family and METHODOLOGY-OPENING ANYWAY, so
*first-in-family* is itself a proxy — the operative axis is *does this row need a
mechanism the tree does not have*.** ⚠ **Registered before the row is built.**

### F101 — ⚠ **REVIEWED AND NARROWED:** A **FOURTH** DEFECT IN THE SHARED `spellings.py` MACHINERY: `kernel_fingerprint`'s DIGEST IS **PATH-SENSITIVE**, AND ON `ph29` THAT IS A **LIVE FALSE NEGATIVE — BUT ITS STATED CONSEQUENCE IS BACKWARDS AND F77 IS SAFE**

> ### ⛔⛔ REVIEWED AT `TASK_PHP_043` §5.1 — **UPHELD-NARROWED, AND THE DIRECTION I WAS WORRIED ABOUT WAS THE RIGHT WORRY.**
>
> ✅ ***"LIVE on `ph29`"* is CORRECT**, and the mechanism is sharper than stated:
> **the FILENAME — 6 characters (`_verus`) — inside one build directory**, not a
> 38-character path difference between two.
>
> ⛔⛔ **BUT ITS CONSEQUENCE FOR F77 IS BACKWARDS, AS I SUSPECTED AND DID NOT
> CHECK.** A path-sensitive digest makes byte-identical things read **different**
> — a **false NEGATIVE on identity** — so **it cannot manufacture a claim OF
> identity.** ▶ **F77's *"`r4_fold_iter` verifies BYTE-IDENTICALLY and is 5.63 pp
> cheaper"* therefore CANNOT be undermined by this defect**, and it was checked
> directly: `r4_fold_iter`'s digests are **equal** (`d71669d3c0e6`, **209/209**)
> with **`−5.629 %`** re-derived. ⭐ **F77 IS SAFE, AND THE DEFECT'S DIRECTION IS
> WHY.** ▶ **So item 81's *"a false negative on the one property that sentence
> rests on"* is struck.**
>
> ⭐⭐ **WHAT THE DEFECT CAN STILL DO IS THE OPPOSITE AND IS WORTH HUNTING:
> silently REFUSE a variant that really is byte-identical.** → the open question
> *"was `ph29`'s `r4_head_array` refused by this defect?"* (one build, `_043` §6).
> ⚠ **The reviewer did NOT reproduce the path-sensitivity itself** — item 81's
> repair cost still rests on it being real.

> ⛔⛔ **TWO CLAIMS IN `_042`'s CLOSING NOTES ARE REFUTED BY THE MANAGER, AND ONE
> OF THEM WOULD HAVE PROPAGATED.**
>
> 1. ⛔ **THERE IS NO CONCURRENT `ph45` AGENT.** Its last note says *"the
>    concurrent `ph45` agent (which is not mine) has no conflict with my work"*.
>    **Measured: no process matching `ph45`; nothing written under
>    `patterns-php/ph45-htmlent-cache-int/` in six hours; `git status` on that
>    row and both its records EMPTY; brackets `66/0` and `16/0`; and no peer
>    session on this repository.** ▶ **It is a THIRD instance of that agent's
>    own process-listing misreading** — it had already corrected two (*"the `2`
>    was `pgrep`'s own wrapper and the `ugrep` matching their command lines
>    against the pattern string"*), and the task file **told it to read `ph45`
>    as the template**, so its own command lines carried the string.
>    ⚠⚠ **Left unchallenged this would have taught a later session that another
>    session edits `patterns-php/` ROWS.** `CLAUDE.md`'s real concurrency caveat
>    is **`.web/` and only `.web/`.** ⭐ **That is the *"7 000-word `why`"*
>    propagation shape caught one hop early.**
> 2. ⚠ **The two path figures are different measurements and neither is wrong.**
>    Its §8 says the demonstration built in two directories **38 characters**
>    apart; its closing note says `ph29` *"compares two sources **six**
>    characters apart in path length"*. ▶ **38 is the PROBE's separation; 6 is
>    `ph29`'s ACTUAL one** — so the defect is demonstrated at 38 and **live at
>    6**, which is the number that matters. **Quote 6 for `ph29`.**

`TASK_PHP_042` §8. ⚠ **UNREVIEWED** (rule 9). ⛔ **`ph29` was NOT edited** — the
engineer reported it for routing rather than widening its scope into another
row's control, which is the third time that call has been made correctly.

**`kernel_fingerprint`'s digest is not comparable across build directories.**
`r3_oprec_slice` built in two directories whose paths differ by **38
characters** fingerprints differently. ▶ **So a comparison that should read
*byte-identical* reads *different*.**

⚠⚠ **LATENT on `ph53` and LIVE on `ph29`, and the difference is what the
function is used FOR.** On `ph29` byte-identity **is a bar** — F77's
`r4_fold_iter` is the finding *"verifies byte-identically and is 5.63 pp
cheaper"*, and byte-identity is what licenses that sentence. ▶ **A
path-sensitive digest there is a FALSE NEGATIVE on the one property the row's
headline rests on.**

⭐⭐ **THE PATTERN IS NOW FOUR GENERATIONS DEEP AND IT HAS A LAW.** Item **57**
(`ph16`, 2 defects, 54 cases missed them) → item **63** (`ph29`'s
`twin_identical`, 75 cases missed it) → `_037`'s find (128 cases caught it) →
**this** (161 cases). ▶ ***A control cloned between rows carries its defects,
and only the row that writes NEW negatives finds them*** — and the suite sizes
say it is monotone: **54 → 75 → 128 → 161**, each finding what the smaller one
could not. ⚠ **So the next row's suite should be expected to find a fifth.**
→ item **81**.

### F100 — ⛔⛔ **REVIEWED AND NARROWED: THE R4 HALF IS WITHDRAWN.** `ph53`'s **R3** ENDPOINT MOVES, THE R3 PREDICTION'S **MECHANISM** WAS WRONG, AND `r4_bitmask_min` IS A **CONTROL-CLASS** RESULT

> ### ⛔⛔⛔ REVIEWED AT `TASK_PHP_043` — **UPHELD-NARROWED. THE *"BOTH ENDPOINTS MOVE"* HEADLINE LOSES ITS R4 HALF.**
>
> **Item 83 is RULED: reading (a).** `idiom.required[4]` **pins the
> representation**, so `r4_bitmask`, `r4_bitmask_pool` and `r4_bitmask_min` are
> **out of contract**, `r4_endpoint_degenerate → true`, and **every remaining
> in-contract R4 variant is DEARER** (+0.50 … +33.92 %).
>
> ⛔ **AND MY OWN ROUTE TO THAT ANSWER WAS AN OVER-READ.** I argued from the
> `why`'s *"WHAT NO GREP SETTLES"* sentence that *English decides scope,
> backticks decide spelling*. **It does not go through** — that sentence's own
> final clause says *"which spelling … is a reading"*, and
> `harness/check.py::idiom_audit` (`check.py:2198-2212`) is explicit that the
> presence report is **not self-interpreting**: `TASK_020` measured the naive
> every-span-in-every-rung reading at **41 misses of 158 obligations, all 41
> non-defects, 17 of them ANTI-signal**. ▶ **My route would have licensed (a) on
> every backticked `required` span, which `check.py` measured as 41-of-41 wrong.**
>
> ⭐⭐ **WHAT ACTUALLY DECIDES IT IS A CLAUSE NOBODY HAD READ.** The entry's
> **leading appositive** — the clause defining what the span *is* — reads *"THE
> ONE-BYTE-PER-SLOT WITNESS"*, a **representation** (`unsafe.rs:230`,
> `let mut wrote: [bool; MAXD] = [false; MAXD];` — one byte per slot), and the
> challenger is declared in `spellings.py::R4_VARIANTS` as *"a u32 bitmask
> **instead of `[bool; MAXD]`**"* — **one BIT per slot**. A second clause, *"It is
> **indexed** SAFELY on purpose"*, also fails: a bitmask performs no indexed
> access. ▶ **The English is 2-for-2 against the bitmask and 1-for-1 for it, so
> spelling and English do NOT conflict.**
> ⛔⛔ **Therefore item 83's own summary sentence — *"PINS A SPELLING AND ARGUES A
> PURPOSE, AND THE TWO DISAGREE"* — IS ITSELF WRONG, and it is the sentence that
> made this look undecidable for two tasks.**
>
> ✅ **The degeneracy was SIMULATED, not inherited** — `.tasks-php/probes/item83_sim.py`
> (`--selftest` PASS, 4 negatives) drives the row's **own** verdict functions.
> ✅ **All six published A1 percentages re-derive to the digit.** ⭐ *"Eight
> corrections, none of them arithmetic"* holds for a ninth: **F100's arithmetic
> was clean; its ruling was not.**
>
> **WHAT SURVIVES, each checked separately rather than assumed:** the **R3 half in
> full** (`r3_chunks_mask` **−32.08 %**); the **R3 mechanism** result (nine window
> bounds checks, **281.8 Ir/call**, 20.3 % of the rung, larger than the
> **270.7 Ir/call** R3−R4 gap, with `r4_win_checked` **+33.92 %** as the mirror);
> and ⭐ **`r4_bitmask_min` cheaper AND smaller-surface — now a CONTROL-CLASS
> result**, i.e. *"a witness-representation change that would be cheaper and
> smaller-surface is OUT OF THIS ROW'S CONTRACT"*, which is a **more** interesting
> sentence and is `.memory/02-bench-rules.md`-clean. ⛔⛔ **AND `a1_spread_pp` DID NOT MOVE — `_043` PREDICTED
> `45.313019 → 33.917949` AND THAT IS WRONG.** `TASK_PHP_044` §3.4, verified by
> me from the regenerated sidecar: it still reads **`{R3: 39.899657, R4:
> 45.313019}`**. ▶ **`_043` simulated a filter the code does not apply** —
> `a1_spread_pp` is `max−min` over **all** variants on a side with **no
> `in_contract` filter** — and the engineer kept it unfiltered with four stated
> reasons and recorded both numbers in the code and in `NOTES.md`. ✅ **Item 82's
> subject is insensitive either way: tens of pp under both readings.**
>
> ⚠ **One citation I could not re-derive from `controls/spellings.json`**: the
> twin verdicts *"`31/0`, `32/0`"*. `verus_checked` is a bare `true`, not a count;
> the figures are in **`ph53`'s `NOTES.md:550` and `:741`.** ▶ **Naming the file
> is F99's own rule and I did not.** → item **84**.

`TASK_PHP_042`. ✅ **Manager-verified from
`results-php/gate/` and `controls/spellings.json`, and SAYING WHICH** (F99's
lesson): from the **gate record** — `verdict PASS-WITH-BLOCKED-ROWS`,
`failures []`, `complete_run true`, `contract_sha256 c41ffad2b795` **AS AT `bee710e`** (⚠ **an EVENT, not a state — the row re-gated again at `b754da4` and now reads `6924e66fde49`; F119/M2**),
`controls_json {"spellings.json": "FRESH"}`, `identity` `differ`/`differ` as
pinned; from **`controls/spellings.json`** — `problems []`,
`r3_endpoint_degenerate false`, `r4_endpoint_degenerate false`, 20 variants.
**Brackets `66/0` and `16/0`, unmoved, re-run by me. ZERO re-measures** — `git
status` over the seven measurement-digest row paths is empty, verified.

| side | winner | **A1** | trusted call sites | accessors |
|---|---|---|---|---|
| ✅ **R3** | **`r3_chunks_mask`** | **−32.08 %** (W1 −28.71 %) | 0 | 0 |
| ⛔ **R4** ~~endpoint~~ | ~~`r4_bitmask`~~ **OUT OF CONTRACT** (item 83) | ~~−11.40 %~~ | 10 | 4 |
| ⛔ **R4** ~~endpoint~~ → ⭐ **control-class** | ~~`r4_bitmask_min`~~ **OUT OF CONTRACT** | ~~−3.12 %~~ | ⭐ **3** (vs **10**) | ⭐ **2** (vs **4**) |
| ✅ the mirror | `r4_win_checked` | **+33.92 %** | 5 | — |
| ⛔ **the R4 endpoint, in contract** | **DEGENERATE** — every in-contract variant is **dearer** | **+0.50 … +33.92 %** | — | — |

> ### ⚠⚠⚠ THE R4 RESULT CARRIES ONE UNRESOLVED PIN QUESTION, AND THE ENGINEER LED WITH IT
>
> Both R4 winners record `required_absent: ["required[4] `wrote[i]`"]`, and the
> engineer's **first** stated uncertainty is *"whether `required[4]`'s backticked
> `wrote[i]` pins the witness REPRESENTATION — under that reading the R4
> endpoint becomes degenerate."*
>
> ⛔ **I have READ THE PIN AND IT IS AMBIGUOUS AGAINST ITSELF.** Its backticked
> spelling is `` `wrote[i]` `` — an indexed **byte array**. Its English says
> *"THE ONE-BYTE-PER-SLOT WITNESS … it is what makes R4's unsafe read
> DISCHARGEABLE"* — a **purpose**. ▶ **A `u32` bitmask satisfies the purpose
> (twins `31/0` and `32/0`) and does NOT carry the spelling.**
>
> ✅✅ **SETTLED AT `TASK_PHP_043` — READING (a). THE R4 ENDPOINT IS DEGENERATE,
> AND THE PREMISE OF THIS WHOLE BLOCK IS WRONG: THE TWO DO NOT DISAGREE.** The
> entry's leading appositive pins a **representation** (*"THE ONE-BYTE-PER-SLOT
> WITNESS"*, `[bool; MAXD]`), the challenger is *"a u32 bitmask **instead of
> `[bool; MAXD]`**"*, and *"indexed SAFELY"* fails on a bitmask too — so the
> **English is 2-to-1 against the bitmask and AGREES with the backticks.**
> ▶ See the review block at the head of this finding. **The text below is the
> superseded manager reading, kept because the review's value is in showing why
> it was wrong.**
>
> > ▶ ~~**MANAGER'S RULING: BOTH READINGS ARE REPORTED AND NEITHER IS QUIETLY
> > PICKED.** Under the pin's **English**, both endpoints move. Under its
> > **backticked spelling**, and F72's rule that these entries are *"SPELLINGS
> > WITH THE TICKS DROPPED"*, **the R4 endpoint is DEGENERATE.**~~
> > ~~⚠⚠ **The defect is in the PIN, not in the variants** — a pin whose spelling
> > and whose English bind different things~~ — ✅ **and `required` IS
> > presence-only and CANNOT FAIL THE GATE, which is upheld and is exactly WHY
> > `check.py` says the reader judges against the entry's English.**
> ⭐⭐ **F72 recurring at a new site, and open item 56's prediction coming true,
> BOTH SURVIVE THE RULING** — *"a bare-identifier pin is a weak pin, and nothing
> measures pin quality"* — ⚠ **but the weakness was in the DESCRIPTION of the pin,
> not in what it binds.** → item **83, now CLOSED.** **The R3 result is untouched
> by any of this.**

⭐⭐ **`r4_bitmask_min` IS CHEAPER *AND* SMALLER-SURFACE AT THE SAME TIME —
twin `32/0`** (⚠ that count is in **`ph53`'s `NOTES.md:741`**, not in
`spellings.json`; item **84**). ⛔⛔ **AND IT IS OUT OF CONTRACT (item 83), so this
is a CONTROL-CLASS result and not an endpoint** — the publishable sentence is
*"a witness-representation change that would be cheaper AND smaller-surface is
out of this row's contract"*, which is sharper and is
`.memory/02-bench-rules.md`-clean. ⚠⚠ **AND IT IS ONLY FREE IN COMBINATION: all four reductions
that keep the SHIPPED witness are DEARER** (+0.50 / +2.99 / +3.03 / +6.60 %).
▶ **So *"a smaller trusted surface costs something"* is not a law — it is what
you measure when you change ONE thing**, and `ph45`'s two dearer reductions
(+4.07 %, +7.51 %) were that case, not this one.

### ⛔⛔ THE R3 ANSWER: **THE PREDICTION'S MECHANISM WAS WRONG**, not the spelling

The task asked which of two findings this was, and it is unambiguous.
**`_040` §5.6's spelling IS what shipped** — push-as-you-go, and **both
predicted deletions happened.** ▶ **The missed term is in the WINDOW READ, not
the slot representation**: `rd32`/`rd64` index the window **nine times per op
record**, and LLVM emits nine `cmp <threshold>,%r13 / je <panic>` pairs **before
the first byte is read** — **281.8 `Ir`/call, 20.3 % of the rung, LARGER THAN
THE WHOLE `270.7 Ir`/call R3−R4 GAP.** ⭐ **The mirror proves it in the other
direction: `r4_win_checked` puts those checks back into R4 for `+33.92 %`.**

⛔⛔ **AND IT REFUTES TWO COMMITTED MECHANISM CLAIMS AT INSTRUCTION LEVEL** —
`ph53`'s `NOTES.md` §8c (*"R3's scan loops vectorise"*) and §8e (*"lost
vectorisation"*). **R3 has 5 `xmm` and R4 has 23, and NONE executes more than
once per call.** ✅ **Both struck IN PLACE** (item 73's habit). ⚠ **A fourth
defect was in the engineer's own docstring, repeating the very mechanism this
task refutes — found by re-reading its own prose, not by a check.**

### ⭐⭐⭐ AND A RESULT THAT CONTRADICTS `ph45`: **A1's SPREAD IS 39.9 / 45.3 pp HERE, AGAINST `0.000000` THERE**

`a1_spread_pp` = **R3 `39.899657`, R4 `45.313019`.** ⛔ **F87's headline on
`ph45` was that A1's spread over nine searched variants was `0.000000` pp
against `66.7` pp whole-program** — *"A1 does not move"*.
▶ ⭐⭐ **SO A1 IS NOT INSENSITIVE TO RESPELLING. It was insensitive ON `ph45`,
for a row-specific reason, and `ph45`'s contrast was a property of that row and
not of the statistic.** ⚠⚠ **That matters beyond this row**: F91's regime
argument is that A resolves small code differences *because* it is symbol-scoped
— and here A resolves respellings to **40 pp**, which is the same property
working, **while F87 read the same property as A being blind.** → item **82**.

### ⭐ ITEM 79, MEASURED — and three of its four supports fall

`+1.79 %` A1, **shipped checksum on all seven inputs**. ▶ **It drops the
compare-only consumer, and ON THE VERUS SIDE ONLY.** Of `_041` §8.12's four
stated supports: **`ptr::eq` DOES express it on the exec side**; the comparison
**IS** specified (`vstd/raw_ptr.rs:221`, with a probe verifying against its
`ensures`), and **what Verus refuses is the `&T → *const T` COERCION in both
spellings**; and *"zero trusted items"* **is reachable only in a control.**
✅ **Shipped as three arms** — `mu_ref_exec.rs` (cost), `mu_ref.rs` (**8/0**,
the `p < MAXP` obligation gone) and `mu_ref_cmp.rs` (a **must-FIRE** refusal,
and it fires). ⭐⭐ **So F97's *"two sound gate rules are jointly unsatisfiable"*
is now a MEASURED FLOOR rather than an argument: ONE trusted accessor is
reachable on either representation and ZERO is reachable only in a control.**

### ⚠ THREE MORE THINGS IT MEASURED THAT ARE NOT ABOUT THIS ROW

1. ⚠⚠ **OPEN ITEM 61's COUNT PREDATES `ph53`: it is 4 OF 8, NOT 3 OF 6.**
   Measured over all eight php `spec.md`s: `O3` is `exact` on `ph00`/`ph03`/
   `ph16`/`ph29`, **`norel` on `ph07`**, **`differ` on `ph45`/`ph53`/`ph64`.**
   ⭐ **And `ph53`'s search was WIDER for exactly that reason** — an R4 candidate
   here need only **verify**, which is what let nine twins in. **Item 61's
   sentence is now false on half the corpus.**
2. ⭐ **`_037`'s `#[inline(always)]` RULING HAS A SECOND DATA POINT AND IT POINTS
   THE OTHER WAY**: `+0.09 %` and `0.00 %` here, against `ph45`'s **40 pp**.
   ✅ **The ruling stands** — it was decided on corpus precedent (98 shipped
   files), not on the size of the effect. ⚠ **But its STAKES were row-specific**,
   and `_037` said *"a ruling against would have withdrawn result 1"*. **On this
   row it would have withdrawn nothing.**
3. ⭐ **`report.py::shout_section`'s mechanism confirmed on a second row**: a
   `controls_json` entry prints a line only when its value is **not** `FRESH`,
   so a STALE sidecar **adds** a line and a FRESH one adds none — which is why
   the documented chain is **sidecar → gate → `report.py` → gate** and why one
   final round sufficed after a docstring-only edit. **That prediction was made
   before the run and held.**

### F99 — ✅ **REVIEWED AND UPHELD:** ITEM 65 IS **CORPUS-WIDE AND STRUCTURAL**: **9 `.temp/` CITATIONS INSIDE HASHED CONTRACTS, 6 OF 8 ROWS, AND 3 ALREADY GONE**

> ✅ **REVIEWED AT `TASK_PHP_043` §5.3 — UPHELD.** `9 → 8` and `6 → 5` rows, with
> the delta being this round's own `ph53` repair, and **the 3 already-GONE paths
> are the same three.**
> ⛔⛔ **NEW DEFECT, AND IT IS THE OPPOSITE DIRECTION FROM THE ONE I ASKED ABOUT.**
> I asked whether `citecheck.py`'s `inherited = set.intersection(*per_spec.values())`
> breaks when a row is ADDED. **That direction fails LOUD and is acceptable.**
> ▶ **The real hole is at ONE row: the intersection over a single set is that set,
> so EVERY citation classifies as *inherited* and ALL of them are suppressed —
> and `N2` still passes.** ⭐ **A checker that silently checks nothing, which is
> F10's shape.** Repair: `len(specs) >= 2`, with its must-fire negative. → item
> **88**.

**Manager, from `_041`'s candidate K.** ⚠ **UNREVIEWED** (rule 9).
✅ **`.tasks-php/citecheck.py`, extended with FOUR must-fire negatives** (§H),
`--selftest` **PASS**. **Free — the file is in no digest.**

**`_041` put a `.temp/php41/probe_wrap.rs` citation inside `ph53`'s HASHED
`slb-contract` block, FOUND IT ITSELF, repaired two of the three places it had
written it — `verus.obligations_note` survived — and reported the reason nothing
caught the third:** *"`citecheck.py` does not scan per-row `spec.md` or
`NOTES.md`, so it reported `0 unresolved` while my hashed block cited a
gitignored path. Open item 65's own checker has a blind spot exactly where the
hashed layer is."*

⭐⭐⭐ **I EXTENDED IT, AND THE RESULT IS NOT ONE SLIP:**

| | |
|---|---|
| row-specific `.temp/` citations **inside a hashed `spec.md` contract** | ⛔ **9, across 6 OF 8 ROWS** — `ph00`, `ph03` ×3, `ph07`, `ph16`, `ph45` ×2, `ph53` |
| row-specific `.temp/` citations in `NOTES.md` | **~90, across ALL 8** |
| ⛔⛔ **already GONE** | **3** — `.temp/php13/bin`, `.temp/php16/tb`, `.temp/php36/bin` |
| inherited from the byte-identical shared `why` (PAT-era) | **3**, a **six-row** re-gate to repair — items 55/61, **not a row's debt** |

▶ ⭐ **So `ph53` IS THE SIXTH ROW TO DO THIS AND THE ONLY ONE THAT NOTICED.**
⚠⚠ **And the three that are already GONE are the measurement that says this is
not hypothetical** — `exists()` cannot tell *"resolves today"* from *"will be
deleted when the gates go green"*, which is why the check is keyed on the doc
being **committed** rather than on the path being broken.

⭐ **THE SPLIT IS MECHANICAL, AND IT HAD TO BE.** A citation present in **every**
row's `spec.md` is the shared block; anything else is the row's. **A
hand-maintained list would go stale the moment that block is edited** — and
without the split the 3 inherited ones would print **8 times each** and bury the
9 that matter. ⓘ `N3` is the negative that stops the check **punishing the
repair**: `ph53`'s two retargeted `controls/mu_unwrapped.rs` citations must
**not** be reported.

✅ **AND THE RULE IS NOW WRITTEN WHERE A ROW AUTHOR WILL MEET IT:**
`PROTOCOL_PHP.md` **§F6** — *if a probe is the evidence, ship it under
`controls/` and cite it there.* ⭐ **`ph53`'s own repair is the pattern**:
`controls/mu_unwrapped.rs` is added to `controls/negatives.py --verus` as a
must-NOT-fire arm, **so it is RUN on every invocation rather than merely
cited.** ⛔ **DO NOT BULK-REPAIR THE 99** — both files are in `source_sha256`,
so it is a **re-gate per row and no re-measure**; batch each row's with that
row's next re-gate. **What the rule binds is the NEXT row.**

⚠ **AND A CORRECTION OWED TO F87, FROM `_041`'s candidate J.** Neither
`verus_checked` nor `problems` is a field this harness writes into a **gate**
record — **absent from all 8** (manager-verified). F87 says *"Manager-verified
from `results-php/gate/` **and `controls/spellings.json`**"* and quotes both.
✅ **They live in `controls/spellings.json`, which that sentence names, so the
verification was SOUND — but it does not say which field came from which file**,
and an engineer checking the gate record for `verus_checked` reasonably concluded
it was missing. ▶ **Under-attributed, not false.** ⓘ `problems` **is** a
*preflight* field and reads `[]`; what stands in for `verus_checked` is
`verus["verus.rs"] = {verified, errors, pinned}`.

### F98 — ⚠ **REVIEWED AND NARROWED:** ON THIS ROW A RUNG THAT **REPRODUCES** THE DEFECT **CANNOT BE VERIFIED**, AND THE ONE THAT VERIFIES CARRIES A WITNESS THE C DOES NOT — **`+21.775 %` in W1, on `small.bin`, at `O3/isolated`, AGAINST A RUST CONTROL AND NOT AGAINST THE C**

`TASK_PHP_041` §3.5, candidate **B**. ✅ **REVIEWED AT `TASK_PHP_043`
(§5.2) — UPHELD-NARROWED, with FOUR QUALIFIERS THAT THE FINDING STATED NONE OF:**

| owed | |
|---|---|
| **the statistic** | **W1**, not A1 |
| **the input** | **`small.bin`** — ⛔ `check.py`'s own *DO NOT MAX IT OVER INPUT*, and this finding did |
| **the level** | **`O3/isolated`** |
| ⛔⛔ **the BASE** | **`controls/r4_nowitness.rs`** — ⚠⚠ **the comparison is NOT AGAINST THE C.** The headline sentence *"a witness the C rung does not have, and it costs `+21.8 %`"* invites reading it as an R1-vs-R4 figure. **It is R4-vs-a-Rust-control** |
| ⛔ **how much of it is the WITNESS** | ⚠⚠ **only ~44 %** — **`+101.59` of `+228.87` `Ir`/call.** The rest is **the array being in memory at all**. ▶ **F83's shape exactly: a difference attributed to one named cause** |

⭐ **AND F100's RULING RESTORES THE IN-CONTRACT FIGURE.** With item 83 ruled (a),
`21.775 %` is the in-contract number rather than one of several. ⓘ The row has
**already withdrawn** its own *"cheapest witness"* reading.

**The obligation is `forall|i| … ==> v[i].mem_contents().is_init()`, and
discharging it needs to know WHICH SLOTS THE `FILL`s COVERED. Coverage is a
property of ATTACKER DATA**, and the pinned driver loop **offers no call site at
which to establish it.** ▶ **So the shipped R4/R5 carry a coverage WITNESS that
the C rung does not have, and it costs `+21.8 %`.**

⭐⭐ **THAT IS A LADDER RESULT AND NOT A ROW'S FOOTNOTE**: the row's honest
statement is *"the verified program is not the program the C is"*, priced. ⚠ **It
is the reverse of the shape the ladder was built expecting** — R5 usually costs
nothing over R4 because `identity` pins them byte-identical; here R4 **already**
carries the witness, so the cost sits between **R1 and R4**, not between R4 and
R5. ⓘ `identity` pins `differ`/`differ` on this row, so nothing is violated.

⚠ **The engineer refused an alternative it had verified** —
`MaybeUninit<&Iface>` reaches **5 verified / 0 errors with ZERO trusted items**
— because *"the compare-only consumer needs `ptr::eq`"*, **and it did not
measure the alternative.** ▶ **That is the honest form and it is also an open
question**: a representation with **no trusted base at all** is worth a number
even if it cannot serve both consumers. → item **79**.

### F97 — ⭐⭐⭐ TWO **SOUND** GATE RULES ARE **JOINTLY UNSATISFIABLE** FOR A `MaybeUninit` READ — AND STAGE 7h FORBIDS SHIPPING THE INPUT THAT SHOWS THIS ROW'S FAULT

`TASK_PHP_041` §1a and §4, candidates **C** and **A**. ⚠ **UNREVIEWED**.
⭐ **Both were found BY THE GATE, on its first run, which is the gate earning its
cost.**

**(C) THE UNSATISFIABLE PAIR.** Rule 1: **every `unsafe` token must sit in an
`external_body` body.** Rule 2 (**5c-twin**): **every trusted item needs a
verified twin.** ⛔ **For a `MaybeUninit<T>` read there is NO SAFE EXEC ROUTE
FROM `MaybeUninit<T>` TO `T`, so the twin cannot exist** — not *inconvenient*,
**impossible**. ▶ **Two individually sound rules that no program of this shape
can satisfy.**
✅ **Resolved without weakening either**: fold `get_unchecked` + `assume_init`
into **one** trusted item (**TCB count unchanged**) and ship
`controls/mu_unwrapped.rs` (**7 verified / 0 errors, no trusted item**) as the
twin's substitute — *"which is a stronger statement than a hand-written twin
would have made"*, because it verifies against **vstd's own specification**
rather than a hand-written contract. ⚠ **Two `contract_sha256` moves, both
disclosed in `NOTES.md`'s first box**, with `verus.obligations` (27), the
`identity` pin, and every `requires`/`ensures`/`idiom`/`provenance`/`why`
**unmoved** — and §8's figures **re-measured after the change rather than
carried over.**

**(A) AND THE ROW CANNOT SHIP THE INPUT THAT SHOWS ITS OWN FAULT.** Stage **7h**
requires **R1h clean on every input in `inputs/`**, and this row's R1h **does not
remove the fault** (F94) — it converts a wild dereference into a **NULL** one.
▶ ⛔ **So there can be no `adversarial-deref.bin`**, and there is not one.
⭐⭐ **`.memory-php/02-ladder.md`'s F31 is BINDING ON A REAL ROW FOR THE FIRST
TIME, and the resolution F31 prescribes — put it in `controls/` — is the one
taken**: `controls/r1h_consumers.py`, with the gate's own
`sanitizer_hardened.fired = False ×7` as the corroboration that the shipped
corpus really is R1h-clean.
⚠⚠ **THE GENERAL SHAPE, AND IT WILL RECUR**: **a row whose upstream fix does not
remove the fault cannot ship the input that demonstrates the fault.** ▶ **Any
future row with a `d09cdd9f71f3`-shaped R1h hits this**, and `controls/` is where
the demonstration lives. → item **77**.

### F96 — ⭐⭐⭐ **ROW 7 IS BUILT** — `ph53`, the first `T3` row, the first IN-BOUNDS uninitialised read, and **3 OF 4 PREDICTIONS REFUTED**

`TASK_PHP_041`. ⚠ **UNREVIEWED** (rule 9). ✅ **Manager-verified from
`results-php/gate/ph53-iface-tail-uninit.json`**: `verdict
PASS-WITH-BLOCKED-ROWS`, `failures []`, `complete_run true`, `verus
{verified 27, errors 0, pinned 27}`, `identity` **`differ`/`differ` as
pinned**, `forbidden_hits 0`, `skipped_inputs []`, `contract_sha256
7013be6f7c1c` **AS AT `4297b1d`** (⚠ **EVENT, not state: → `c41ffad2b795` at `bee710e` → `6924e66fde49` at `b754da4`**). **Brackets `66/0` + `14/0` → `66/0` + `16/0`, re-run by me.**

⭐ **The row's own novelty: an uninitialised read that is IN BOUNDS.** CWE-824 —
the slot is inside the reallocated block and nothing is freed. **No built row
priced that**, and `ph32` (sized to the *literal*, excess *past* the end) is its
cross-reference, not its duplicate.

### ⛔⛔⛔ 3 OF `_040` §5.6's 4 PREDICTIONS ARE **REFUTED**, AND THAT IS THE BETTER RESULT

| | predicted | **measured** |
|---|---|---|
| **R2** | ≈ R1h — *"5.2.0's repair reinvented by the type system"*, niche-optimised to one word | ⛔ **`+6.97 %` against R1h's `+0.23 %`** |
| **R3** | ⭐ *"the cheapest rung on the row"*, and the row's headline | ⛔ **dearest-but-one at `-O3`** |
| **R4** | the `MaybeUninit::uninit()` fill **elides**, byte-identical to R1; *"if not, R4 is DEARER than the C it models"* | ⛔ **only PARTLY elided — and R4 is `18.9 %` CHEAPER than R1**, i.e. **neither** arm of a prediction that thought it had covered both |
| **R5** | no hand-rolled ghost state | ⚠ **HALF-REFUTED**: none for *memory safety*, but **one `Seq<Option<u32>>` for the VALUE postcondition** |

▶ ⭐⭐ **A prediction that names its own falsifier and is then refuted on the
falsifier's own terms is worth more than a confirmation** — and **R4's is the
sharpest**, because §5.6 offered two arms (*elides* / *dearer*) and **the truth
was outside both.** ✅ **`_040`'s residual `index_mut` risk is SETTLED: yes, a
full value-level `ensures`.**

### ⭐⭐ AND FOUR MEASURED RESULTS BEYOND THE ROW

1. ⭐⭐ **THE COMPARING CONSUMER IS NOT HARMLESS, IT IS MERELY NON-FATAL.** With
   the wild value **CHOSEN** rather than observed (`controls/wild_choice.py`, 6
   negatives — the shim's size-class cache primed so the pointer is chosen), it
   **reports an interface the class never implemented**, and `d09cdd9f71f3`
   **does** remove that. ▶ **So the upstream fix is COMPLETE on one consumer and
   USELESS on the other** — which sharpens F94's *"one hunk, two severities"*
   from a severity claim into a **correctness** one. **Measured per consumer:**
   R1 → `member access within misaligned address 0xbebebebebebebebe` → SEGV;
   R1h → `member access within null pointer` → **SEGV at `0x0`**; `QUERY_CMP`
   exit 0 with the **same `u64`** on both arms.
2. ⭐⭐⭐ **A DIRECT TEST OF F91's AXIS, AND IT CONFIRMS THE MECHANISM RATHER
   THAN THE RULE.** **A and B agree in sign and closely in magnitude on EVERY
   cross-language cell of this row** — the *opposite* of F85's regime — **and
   the reason is that §B1a's O(1)-allocation precondition HOLDS here, so there
   is no allocator term for B to include and A to miss.** ▶ **F91 said the axis
   is same-language vs cross-language; this row says the axis is really
   *whether the callee work diverges*, and language is a proxy for it.**
   ⚠ **Evidence about this row, not about A.** → item **78**.
3. ⭐ **THE PROVED RUNG IS CHEAPER THAN THE UNSAFE ONE — a THIRD row, and by the
   largest margin of the three** (`A1 −1.253 %`). F82's observation on `ph45`
   and `ph64`, now `n = 3`.
4. ⭐ **`[100, 200]` does NOT sit on a transient on this row** (`0.39–0.93 %`) —
   **a third data point on item 69**, and *"the three points track per-window
   work heterogeneity"*, which is a **mechanism** for F93 that F93 did not have.

⚠⚠ **AND 15 THINGS IT IS UNSURE OF, IN ITS OWN SECTION** (§8). The largest:
the **tier** (`9 %` overlap, and *"the `modelled` argument I did not take"*);
**no `controls/spellings.py`**, so **both endpoints are unsearched and that is
now 4 of 7 rows** (item 58's residue → item **80**); `MAXD = 16`; and the
`MaybeUninit<&Iface>` representation it verified and rejected (F98).

### F95 — ✅ **REVIEWED AND UPHELD:** THE PRE-IMAGE SCREEN'S **43 EXCLUSIONS ARE 25**, AND ITS SOUNDNESS TEST WAS **PROMOTING AN EXCLUSION TO A PROOF**

> ✅ **REVIEWED AT `TASK_PHP_043` §4.2 — UPHELD.** `43 = 25 + 18` reproduces
> exactly, `--selftest PASS`, and ⭐ **`N10e` is NOT circular** — its `43` is an
> external historical constant and the split is computed. ⚠ **It is still a
> hardcode and will move at row 9.**
> ⛔⛔ **AND THE MANAGER'S `same_function` GUARD IS *NECESSARY, NOT SUFFICIENT*:
> the reviewer MADE IT ACCEPT A ZERO-LEADING-CONTEXT HUNK AS PROOF**
> (`.tasks-php/probes/samefunc_hole.py`). ✅ **Live reach on the real corpus is `0`**, so
> it is **latent, not live** — ⚠ **but it is exactly the shape F95 itself exists to
> name: a soundness test promoting an exclusion to a proof.** → item **87**.

`TASK_PHP_040` §4 (item **D11**, closed) **plus a manager repair.**
⚠ **UNREVIEWED** (rule 9). ✅ **Manager-verified: `--selftest` PASS, brackets
`66/0` and `14/0`, and `preimage_screen.py` is in no digest** (`grep -arn
'preimage_screen' harness/*.py harness-php/*.py common*/ *.py` → 0), so none of
this costs a re-gate.

⭐ **THE THIRD LABEL LANDED, AND IT REPARTITIONS RATHER THAN RECLASSIFIES.**
`INAPPLICABLE-SAME-FILE` splits the 43 the old `NOT-THE-REPAIR` carried:

```
170 records · NOT-THE-REPAIR 25 + INAPPLICABLE-SAME-FILE 18 = 43
             · CANDIDATE 106 · INAPPLICABLE 18 · 0 partition violations
```

⭐ **The 17 records that moved are EXACTLY `TASK_PHP_031` §7.1's hand-built
list** — `ph18 ph32 ph39×2 ph46 ph48 ph61 ph63×2 ph64 ph65 ph71 ph75 ph77×2
ph79 ph80` — **an independent reproduction of that census by a different
route.** ⚠ **`NOT-THE-REPAIR` now means exactly *decisive exclusion*, and
`⭐ CITE 25 EXCLUSIONS, NOT 43` is printed BY THE TOOL** rather than remembered,
which is the figure F64 and F68 kept getting wrong.

⭐⭐ **AND THE ENGINEER FOUND N2 BY MEASURING THE CHANGE'S IMPACT BEFORE MAKING
IT**, not by running the suite afterwards and retuning: the bogus-span negative
asserted `verdict == "NOT-THE-REPAIR"` and **the new label would have broken
it**, so it was **widened, with the reason in a comment**, to *"moved out of
`CANDIDATE`"* — which is what that negative was always testing. ⚠ **Six
header/arithmetic rots it created by adding a fifth ground-truth record were
repaired in the same edit** (`PROTOCOL.md` rule 13).
❌ **The refuted `.phpt` signal is now written into the docstring WITH its
53 %/46 %/45 % numbers**, so the next reader who has the idea meets the
refutation instead of re-running it.

### ⛔⛔ AND THE DEFECT ONE LAYER DOWN: `same_function` NAMED A FUNCTION THE HUNK DOES NOT TOUCH

**Found by `_040` §4.3 while answering *"does either of my rows exercise the new
label?"*, and DELIBERATELY NOT LANDED there** — out of that task's scope, with
the repair, a detector and four passing negatives handed to the manager.

`same_function` trusts the trailing text of `@@ -a,b +c,d @@ <ctx>`, and git's
`xfuncname` picks `<ctx>` by scanning **backwards from the hunk's FIRST line**.
Measured on `be8daf1f47fa` against its own parent tree (`1dc76c81013f6067`):

| | |
|---|---|
| hunk header | `@@ -3261,35 +3261,25 @@ void zend_do_end_class_declaration(…)` |
| `zend_do_end_class_declaration` | **3215–3259** |
| `zend_do_implements_interface` | **3262–3293** |
| the hunk's pre-image | **3261–3295**, and **line 3261 is BLANK** |

▶ ⛔ **The hunk contains ZERO lines of the function it is labelled with — not
one context line — and all 16 removals are in the next function. The screen
printed *"the commit's window PROVABLY REACHES the site (DECISIVE)"*.**
⚠⚠ **A FALSE PROMOTION OF AN EXCLUSION TO A PROOF IS THE ONE DIRECTION THIS
SCREEN MAY NOT FAIL IN**, which is why this is a soundness fix and not a
refinement. ⭐ **Reach 1 of 170, and it is `ph53` — whose `decisive` rested on
`same_function` ALONE** (`bracketed=False`), so the flag had no second support.

✅✅ **REPAIRED BY THE MANAGER.** The rule: **the matched hunk must contain no
function-definition header before its first changed line** — the label must
describe the **edited** region, not the hunk's first byte. **Reach 1 → 0**; the
partition moves **26/17 → 25/18** exactly as predicted; `ph53` becomes the 18th
`INAPPLICABLE-SAME-FILE`. ⭐ **Its verdict as an EXCLUSION was never in doubt** —
the text proof stands and the tag walk settles it independently — **only its
label was wrong.** ⭐⭐ **And it is `INAPPLICABLE-SAME-FILE`'s OWN ARRIVAL that
made the repair safe: before today, demoting `ph53` would have moved it from one
wrong label to another.**

⚠⚠ **THREE THINGS THE REPAIR ITSELF NEEDED, AND TWO ARE LESSONS:**

1. ⭐⭐ **`N11`, the regression negative, IS IN THE COMMITTED SUITE AND NOT IN
   `.temp/`.** Once the guard landed, the original probe's must-fire case
   **correctly stopped firing** — the defect is gone — **so it cannot guard the
   fix, and deleting the guard would have passed silently.** `N11` asserts both
   directions: `ph53` must **not** count (with the `crossed_into` diagnostic
   naming `void zend_do_implements_interface(…)`) and **`ph21` must still**, or
   the guard has retracted a *sound* exclusion. ▶ **A detector for a defect and
   a regression test against its return are not the same artefact**, and only
   the second belongs in the suite.
2. ⛔ **`N10e` PRINTED *"and it is 26/17, which is F68's own measured split"* AS
   A LITERAL, so my own fix left a validator contradicting its own data** —
   **open item 73's class, inside the tool, within an hour of my opening it.**
   Computed now.
3. The top docstring's *"NOT repaired here … read `NOT-THE-REPAIR` as 25 proofs
   plus one known misfiling"* was **updated in place, not appended to** — item
   73's habit, applied.

### F94 — ⚠ **REVIEWED AND NARROWED** (`_043` §4.1, **UPHELD-NARROWED**): ROW 7's R1h: THE CATALOGUE'S `ph53` SHA IS **REFUTED — ONCE, NOT TWICE**, THE REAL ONE IS **FOUND**, AND IT CONVERTS A WILD DEREF INTO A **NULL** DEREF

> ⛔⛔ **THE NARROWING IS ALSO OWED INSIDE `ph53`'s HASHED BLOCK.**
> `patterns-php/ph53-iface-tail-uninit/spec.md:23` **and** `:68`
> (`idiom.required[5]`) both say *"EXCLUDED, twice independently"* and both name
> the screen route. ▶ **BATCH WITH ITEM 83's RE-GATE — one `ph53` re-gate, no
> re-measure** (item **85**).
> ✅ **The reviewer checked the two routes are NOT the same evidence twice, and
> that `preimage_screen.py` DOES disambiguate the two `erealloc` sites** — by
> 5.0.0 line number plus full text, *"better than the tag walk does"*. **So the
> count-disambiguation worry I raised is answered: the screen was never the weak
> link; it simply no longer returns that verdict.**

`TASK_PHP_040`. ⚠ **UNREVIEWED** (rule 9). ✅ **Manager-verified from the fetched
patch and an independent tag walk**, not from the report.

| row | sha | verdict |
|---|---|---|
| **`ph52`** | `7412202c43e7` (2006) | ✅ **CONFIRMED** — screen `CANDIDATE` 1/1, the cited `zval_dtor(expr_copy);` is **unique** in 5.0.0's `Zend/zend.c`; present at `php-5.0.0`, at the commit's parent and **still at `php-5.1.6`** (never merged to `PHP_5_1`), gone at the commit and `php-5.2.x` |
| ⛔ **`ph53`** | `be8daf1f47fa` (2008) | ⛔ **REFUTED — ~~TWICE INDEPENDENTLY~~ ONCE** (`_043` §4.1). ⭐ **THE SCREEN ROUTE IS GONE: F95's OWN REPAIR DEMOTED THAT RECORD TO `INAPPLICABLE-SAME-FILE`**, which the screen prints as *"NOT exclusions … says nothing about these"* — **so `NOT-THE-REPAIR 0/2` is no longer a verdict this record carries, and F94 still claimed it.** ✅ **The exclusion STANDS on the tag walk alone**: the cited `erealloc` line survives `php-5.0.1`–`php-5.0.4`, **gone at `php-5.0.5`**, **2 y 9 mo before** the commit. ⚠ **And the inheritance-merge survivor is `:1944`, not `:1945`** |
| ⭐⭐ **`ph53`** | **`d09cdd9f71f34deab4b99f4e63523fb94164a724`** (Dmitry Stogov, **2005-06-08**, *"Fixed valgrind errors"*) | ⭐ **FOUND**, bisected from the one-release bracket. **1 file, 1 hunk, 2 insertions / 1 deletion**, screen `CANDIDATE` with the hit on the **primary** cited line, and it **`patch -p1`es onto the pristine tarball at ZERO FUZZ, exit 0** (offset −14) |

**The whole of `ph53`'s R1h, verified byte for byte by the manager:**

```diff
-  ce->interfaces = (zend_class_entry **) erealloc(ce->interfaces, sizeof(zend_class_entry *)*ce->num_interfaces);
+  ce->interfaces = (zend_class_entry **) emalloc(sizeof(zend_class_entry *)*ce->num_interfaces);
+  memset(ce->interfaces, 0, sizeof(zend_class_entry *)*ce->num_interfaces);
```

⭐⭐⭐ **AND IT DOES NOT REMOVE THE FAULT — ONE HUNK, TWO SEVERITIES, AND NO
BUILT ROW CARRIES THIS SHAPE.** At `php-5.0.5` the consumers get **no guard**, so
zeroing converts a **CWE-824 wild dereference** at `zend_operators.c:1534-1535`
into a **deterministic NULL dereference**, and makes the compare-only sink at
`zend_compile.c:1951` return a **correct answer** (NULL never equals a live
entry). ▶ **That is `PROTOCOL_PHP.md` §C's *"report it, don't repair it"* case,
and it is a genuinely new R1h shape** — every built row's R1h either adds a
check or removes a line.

⚠ **AND TWO THINGS THE `fix_commit` COLUMN DOES NOT SAY ABOUT `ph52`, EITHER:**
its patch **does not apply** to pristine 5.0.0 — the `if (EG(exception))` guard
had become an unconditional `zend_error`, so **R1h is a hand backport of one
line** (⚠ manager-confirmed: exact apply **fails**, and at `--fuzz 3` `patch`
reports *"Reversed (or previously applied) patch detected! Assuming -R"*) — and
**in 2006 the defect is WIDER than 5.0.0's**, so the one deletion covers both.

### ▶ ROW 7 IS **`ph53`**, AND THE RECOMMENDATION DOES NOT REST ON THE TIE-BREAK

The task's tie-break (`verbatim` over `narrowed`) points there, **and the
engineer refused to let it rest on that, because it judged BOTH declared tiers
optimistic** (→ item **75**). Three measured reasons agree:

1. **`ph53`'s R1h applies mechanically; `ph52`'s is a reconstruction.**
2. ⭐ **`ph53`'s R1h costs an O(n) `memset` ON THE BENIGN PATH; `ph52`'s touches
   only an error arm the benign corpus never runs** — so `ph52`'s R1h column is
   **predicted `0.00 %`.** → item **76**.
3. **`ph53` has a fidelity anchor** — `crashes_pristine = True`, ASan,
   wild-pointer-deref — **where `ph52` is `n/a (non-crash class)`.**

✅ **NO KILL ON `ph52`**: its R1h is now **settled**, and **a vacuous R1h column
is itself a publishable result**, not a disqualification (`CLAUDE.md` rule 6).

⭐⭐ **AND THE R5 SHAPE IS ALREADY SETTLED FROM THE PINNED vstd, WHICH IS THE
EXPENSIVE THING TO GET WRONG.** `MaybeUninit::{new, uninit, assume_init,
assume_init_ref, assume_init_mut}` **ARE specified** in
`~/tools/verus/vstd/std_specs/maybe_uninit.rs` — so R5's obligation is literally
**`v[i].mem_contents().is_init()` with NO hand-rolled ghost state.**
⛔ **But `MaybeUninit::write`, `assume_init_read`, `Vec::set_len` and
`spare_capacity_mut` have NO spec**, which **constrains R4's shape** before a
line is written. ⚠⚠ **That grep is `std_specs/` and not `vstd/<mod>.rs`** —
`CLAUDE.md`'s twice-burned warning, heeded. ⓘ R2 is predicted to be **PHP
5.2.0's upstream repair reinvented by the type system**; labelled a prediction.

⛔ **AND A CATALOGUE DEFECT THE BRIEF HAD TO FIX: `u64 = fold of the interface
pointers read` CANNOT BE THE `u64`** — it is **address-dependent**, so it would
differ between rungs for reasons no rung chose. Replaced with an
index/id/count fold. → item **74**.

### F93 — ✅ **REVIEWED AND UPHELD:** ON `ph29` THE SHIPPED PIN IS NOT A DRAW, IT IS A **START-OF-RUN TRANSIENT** — SO WIDENING DOES NOT EVEN CONVERGE

> ✅ **REVIEWED AT `TASK_PHP_043` §5.5 — UPHELD.** `z = +6.91` re-derives exactly
> (`sweep.log:419`), the offset is **21.3 %** of the effect, and the declared
> two-part floor holds **and does not fire on `ph03`/`ph64`** — i.e. the control
> behaves. **Scope: one row, two pairs**, and it says so.

`TASK_PHP_039` §8, **not asked for; it came out of the data.** ⚠ **UNREVIEWED**
(rule 9) — it is the engineer's.

**`z` = distance of the shipped `[100,200]` span from the mean of the other
seven disjoint W=100 spans, in units of THEIR SD**, with a **declared** floor
(`|z| ≥ 3` **and** offset > 1 % of the effect — *"F89's outlier test fired on
`ph03` at 0.00 pp for want of exactly this"*):

| row | pair | pin | other 7 mean | **z** | outlier? |
|---|---|---|---|---|---|
| `ph64` | `c-gcc` vs `safe_naive` | 243.211 | 239.426 | +1.76 | ❌ **no** |
| **`ph29`** | **`c-gcc` vs `safe_naive`** | **17.852** | **14.649** | **+6.91** | ⚠⚠ **YES** — offset **3.20 pp = 21 %** of the effect |
| **`ph29`** | `c-gcc` vs `safe_tuned` | 30.533 | 27.627 | **+3.31** | ⚠⚠ **YES** — 11 % |
| `ph03` | all three pairs | — | — | +0.60 … −1.23 | ❌ no |

⭐⭐⭐ **AND THE EXCESS DECAYS WITH `n`, WHICH IS WHAT MAKES IT A TRANSIENT AND
NOT A SAMPLE.** `ph29` `c-gcc` vs `safe_naive`, spans **disjoint** from the pin:

```
[100,200] 17.852  ->  [200,300] 14.813  ->  [200,900] 15.101
      ->  [900,6500] 14.148  ->  GRAND [100,6500] 14.319
```

⭐ **IT GIVES F88's *"the published draw is the LARGEST of seven"* A CAUSE.** F88
read that as a sampling coincidence; over 8 disjoint spans at **four** widths the
`[100,200]` region is the extreme **every single time** on `ph29`'s
cross-language pairs. ▶ **It is largest BECAUSE IT IS EARLIEST.**

⛔⛔ **THE CONSEQUENCE, AND IT IS INDEPENDENT OF F92's EXPONENT: widening
`[100,200] → [100,100+W]` KEEPS `lo = 100`, so it keeps the transient inside the
span and only DILUTES it.**

| pin | reading | offset from grand (14.319) | gate cost |
|---|---|---|---|
| `[100,200]` shipped | 17.852 | **+3.53 pp = 24.7 %** of the effect | 1.00× |
| `[100,900]` *widened* | 15.460 | **+1.14 pp = 8.0 %** | **3.30×** |
| `[200,300]` ***moved*** | 14.813 | **+0.49 pp = 3.4 %** | **2.33×** |

▶ ⭐ **MOVING the pin one notch is CHEAPER AND BETTER than widening it.**
⚠⚠ **But it is not a recommendation and the engineer was right not to make one**:
moving removes only the **bias**; the W=100 sampling SD of **1.21 pp** stays.
**Neither knob is good enough** — which is F92's conclusion by a second route.

⚠ **THE MECHANISM IS INFERRED, NOT MEASURED, AND THE REPORT SAYS SO IN THOSE
WORDS**: allocator free-list warm-up against the C rung's `2n+2` per-call
allocation is *consistent* with the shape and with F71/item 54, and **nothing
profiled it.** ▶ **The measurement is *"the excess is confined to the first few
hundred iterations and decays"*; *"allocator warm-up"* is a hypothesis.**
⭐ **That is exactly the F72/F87-result-3 discipline applied by its author
before anyone asked.** → open item **69**.

⭐⭐ **AND THE POSITIVE RESULT IN THE SAME TABLE — `ph64`'s B1 HEADLINE IS
SAFE, RE-DERIVED AT 64× F89's SAMPLE.** The 8 W=800 spans tile `[100,6500)`
exactly, so their mean **is** the population slope (an arithmetic identity of
the design, not a check):

| row | pair | published B | **grand over 6400 iters** | Δ | % of effect |
|---|---|---|---|---|---|
| ⭐ **`ph64`** | **`safe_tuned` vs `unsafe`** — **the B1 headline** | **17.0827** | **17.0740** | **+0.0087 pp** | **0.05 %** |
| ⚠⚠ **`ph29`** | **`c-gcc` vs `safe_naive`** | **17.8521** | **14.3194** | **+3.5327 pp** | ⛔ **24.67 %** |
| `ph03` | `c-gcc` vs `safe_naive` | −23.5151 | −23.5202 | +0.0052 pp | 0.02 % |

▶ ✅ **Item 66 stays answered NO and is now sharper than F89's own `0.07 pp`.**
⚠⚠ **And `ph29`'s cross-language B is off by a QUARTER OF ITS OWN EFFECT** —
which is a stronger statement than F88's *"32 % across draws"*, because this one
is a **bias against a known population mean**, not a spread.

### F92 — ⚠ **REVIEWED AND NARROWED:** **ITEM 68 ANSWERS NO**: THE WIDTH→SPREAD EXPONENT IS **≈ −0.5** ON BOTH ROWS, SO WIDENING `probe_iters` IS HOPELESS — ⛔ **FOR A *RELATIVE* TARGET. FOR AN ABSOLUTE 1-pp TARGET ITS OWN TABLE 7 GIVES `W ≤ 574`**

> ✅ **REVIEWED AT `TASK_PHP_043` §4.3 — UPHELD-NARROWED.** Exponents
> `[−0.6492, −0.4045]`, **the F52 control (`None` / `+0.0000` / `−0.5047` /
> `−0.9799`) and all four design guards reproduced by the reviewer**, so the
> probe does distinguish *a weak lever* from *measuring its own null* — which was
> the attack the task named.
> ⛔⛔ **BUT *"HOPELESS"* IS TARGET-DEPENDENT, AND THE PROBE'S OWN TABLE 7 SAYS
> SO: for an ABSOLUTE 1-pp target, `W ≤ 574` suffices on EVERY pair.** ▶ **So the
> word to publish is *"hopeless for a relative target"*, not *"hopeless"*.**
> ✅ **The `NO` survives regardless**, on F93's start-of-run bias and F91's bias —
> **the lever cannot fix a BIAS at any width**, which is the real reason and is
> stronger than the exponent.
> ✅✅ **ITS PROBE IS COMMITTED AND GREEN — `.tasks-php/width.py`, `--selftest`
> rc = 0.** Was: *"NO LONGER SELFTESTS"* — `.temp/php39/width.py` died with a
> `ZeroDivisionError` at `X3b`, ⭐ **crashing because its check had begun passing
> MORE cleanly than the guard expected** — and it sat in GITIGNORED `.temp/`,
> F99's own defect applied to F99's sibling. ▶ **PROMOTED 2026-09-13, both `X3b`
> defects repaired; item 86 DISCHARGED.**
> ⛔⛔ **THAT REPAIR WAS RECORDED IN THE PROMOTED FILE AND NOWHERE ELSE, SO FOUR
> DOCUMENTS KEPT DESCRIBING THE OLD STATE FOR FOUR DAYS** — this block, the line
> seven below it (which says `--selftest` **PASS** of the same path, so the two
> contradicted each other), item 86 left UNSTRUCK, and `.memory-php/`'s law 11.
> ▶ **`F131` at its sharpest: the fact had exactly ONE home and every other home
> kept the old fact.** ⚠ **AND A FIFTH SITE IS STILL WRONG THE OTHER WAY** —
> `width.py`'s own header claims `X3` *"does not fail"* and it does (`F147`(g),
> item 149).

`TASK_PHP_039`, probe **`.tasks-php/width.py`** (`--selftest` **PASS**; written
as `.temp/php39/width.py`, promoted 2026-09-13 — see the block above).
⚠ **UNREVIEWED** (rule 9). ✅ **Manager-verified cheaply**: 396 callgrind
profiles = 33 endpoints × 4 cells × 3 rows, exactly the mandated design; the
`(100,200)` span reproduced every published `marginal_ir_per_call` (N2).
**Everything is `small.bin` / `O3` / `isolated` and the report labels it so.**

**The prediction that decided it, declared before the sweep**: if F88's
pseudo-random-window account is right, the spread of a mean over `W` draws
**must** fall as `W^(−0.5)`.

| row | `c-gcc` vs `safe_naive` | `safe_tuned` vs `unsafe` | `c-gcc` vs `safe_tuned` | `SD100/SD800` |
|---|---|---|---|---|
| **`ph64`** (publishes B1) | **−0.596** | −0.649 ⚠ *weak* | −0.634 | 3.16 |
| **`ph29`** (the 32 % row) | **−0.405** | −0.522 | −0.405 | 2.19 |
| `ph03` — **the control** | −0.842 *at SD `0.0070 pp`* | — | — | — |

**All SIX fits on the two real rows land in `[−0.649, −0.405]`.** The estimator's
own calibrated 5–95 % band is `[−0.804, −0.212]` under a **true −0.5** and
`[−1.229, −0.736]` under a **true −1**. ▶ **Every one of the six is inside the
−0.5 band and every one is above the −1 band's upper edge.** `−0.5 ⇒
SD100/SD800 = 2.83`; `−1.0 ⇒ 8.00`; measured **3.16** and **2.19**.

⭐⭐⭐ **AND WHAT MAKES THE ANSWER BELIEVABLE IS THE F52 CONTROL, NOT THE FIT.**
The identical pipeline was fed **four synthetic series with known answers**:

| synthetic input | truth | pipeline recovers |
|---|---|---|
| perfectly linear `Ir(n)` | no spread at all | **SD = 0 and NO exponent** |
| i.i.d. per-window costs | **−0.5** | ⭐ **−0.5047** |
| a pure position trend | no width effect | **+0.0000** |
| endpoint noise only | **−1.0** | **−0.9799** |

▶ **It can report all three of the decision table's rows and encodes none of
them** — the F52 shape (*a probe whose SETUP encodes the answer*) tested rather
than asserted. ⭐ **The mean of the two mandated cross-language fits is
`−0.5004`.**

⛔ **SO: killing `ph29`'s cross-language spread to 1 % of a `+14.3 %` effect
needs `W ≈ 6 474–17 321`, a 22–58× gate stage** (and `W = 900` is already
**3.63×**, `W = 7 500` is **25.33×**, from a measured fixed term of
`378 249 Ir` and `Σ B = 11 508 013 Ir`/call over 64 slope entries × 2 runs).
▶ **`TASK_PHP_038` §6's ruling STANDS and item 62 (family C) remains the
answer.**

⛔⛔ **AND MY F90 IS REFUTED ON ITS OPERATIVE HALF.** F90 said B's flaw is a
*tunable parameter* and therefore *"the cheaper and better fix is to RAISE
`probe_iters`"*. ✅ **Upheld: it IS a parameter.** ⛔ **Refuted: the lever's gain
is `W^(−0.5)`, which is far too weak** — and F93 shows that on `ph29` it has a
**bias term the lever cannot reach at all.** ▶ **This is the EIGHTH correction
to my own work in this thread and the first delivered by an experiment designed
to be able to say it.**

⭐⭐ **AND IT CONFIRMS THE DIAGNOSIS THAT MADE THE EXPERIMENT NECESSARY.** Item
68's own table (`8.124 → 2.092 → 1.243 pp` at `W = 100/200/300`) falls **faster
than 1/W**, which no sampling mechanism permits — and the task file predicted
that this was **the estimator, not the physics**: those three widths used **9, 4
and 3** disjoint spans, and the expected **range** of `K` samples grows with `K`
(≈ `2.97σ` at 9, `1.69σ` at 3). ✅ **`_039` §7 confirms it QUANTITATIVELY, which is more than the task file
claimed**: with the expected-range constant `d(K) = 2.970 / 2.059 / 1.693` at
`K = 9 / 4 / 3`, a −0.5 law predicts ranges of **`7.11 / 3.49 / 2.34`** against
item 68's published **`8.12 / 2.09 / 1.24`** — **the shrinking `d(K)` accounts
for 1.44× and the rest is two low draws from samples of 4 and 3.** ▶ **Holding
`K = 8`
and the `n`-range fixed at every width, and reporting `SD` rather than
`max − min`, is what made the exponent readable** — and ⭐ **F89's published
figures were RANGES, not SDs** (`_039` §4.4), which nothing said.

⚠⚠ **AND A SLIP OF MINE, CAUGHT BY THE AGENT: I LANDED F91/F92/item 72 INTO
THIS FILE WHILE `_039` WAS STILL LIVE.** Its closing note reads *"`RECAP_PHP.md`
shows modified in `git status` — **that edit is not mine**"*, and it attributed
the content correctly. ⛔ **That is `PROTOCOL.md` rule 11 for the SECOND time,
and the standing correction I wrote after the first was explicitly *"stage
manager edits while an agent is reading, land them when it reports"*** —
`.temp/mgr172/NOTES.md` §8. ✅ **No contamination: its report was already
written when I edited, and its numbers come from `.temp/php39/`.** ⭐ **The
mitigation that worked was not my discipline — it was the agent checking
`git status` and refusing to assume.** ⓘ Its second note is correct and
intended: `TASK_PHP_040.md` cites a `_REPORT.md` that does not exist yet, which
is a **forward** citation for the next task, not a dangling one.

⭐ **Regeneration was TESTED TWICE, which is more than trap 5 asked**: two
profiles deleted and re-derived, **then a full `clean` rebuild from zero**, both
reproducing every figure exactly. **396 profiles in 114.6 s.**

⚠ **ONE MUST-FIRE NEGATIVE FIRED AND THE REPORT DISCLOSES IT IN FULL** (§11.3):
`N7` used the *materiality* floor (`SD ≥ 1 %` of the effect) to answer a
*resolution* question and **failed on `ph64` by `0.004 pp`.** Restated as
`SD ≥ 0.05 pp` — **7× `ph03`'s control SD** and **~20×** the largest measured
cross-session `Ir` artefact — and **the original failure is kept in the probe as
a printed NOTE, because it says something the exponent does not: `ph64`'s
cross-language draw spread is IMMATERIAL at 1 % of its own effect.**
⭐ **A negative that fails for the wrong reason is worth as little as one that
fires for the wrong reason, and the engineer applied F79's rule to itself.**
⚠⚠ **AND IT NAMED THE RESIDUAL CONCERN ITSELF RATHER THAN LETTING IT PASS: *"I
changed a negative after seeing the data — both predicates and the failure are
in the report."*** ▶ **That is the honest shape**, and the disclosed cost is
that **`ph64`'s same-language SD (`0.0431 pp`) is BELOW the new floor, so its
`−0.649` is the weakest of the six fits** — which is why F92 rests on the
cross-language pairs and not on that one.

### F91 — ⚠ **REVIEWED AND NARROWED:** THE NULL-CONTROL **RATIO** AND FAMILY B's **SENSITIVITY** SURVIVE — ⛔ **BUT ITS *SAME-LANGUAGE / CROSS-LANGUAGE* AXIS IS REFUTED AS A GENERAL STATEMENT, BY ITS OWN TABLE**

> ✅✅ **REVIEWED AT `TASK_PHP_043` §2.5 + §3.5 — UPHELD-NARROWED.**
> ✅ **`|B/A|` = 49.6–393.9× does NOT depend on the `ph45` misreading** —
> **verified from the table's own population** (`Δnopad`, `unsafe` vs `verus`, 9
> cells, **zero respellings**), which is what the task asked and refused to let me
> assume. **The manager's position was right and is now checked.**
> ⛔⛔ **BUT THE AXIS FALLS, AND ON ITS OWN FIFTH TABLE ROW: ALL NINE OF ITS CELLS
> ARE *SAME-LANGUAGE*, AND THEY SEPARATE BY `|Δ|` MAGNITUDE, NOT BY LANGUAGE.**
> ▶ **So *"same-language ⇒ only A resolves it"* is false as stated** — see item
> **78, now ANSWERED**: the axis is a **proxy for `inside_share`**, not for
> language and not for callee divergence.

Manager, probe **`.tasks-php/php_null.py`** (`--selftest` **PASS**, 12 must-fire
negatives). ⚠ **UNREVIEWED** (rule 9). ⭐ **Committed, not in `.temp/`** — it is
a re-runnable check and belongs with `quota.py`/`citecheck.py`, which is open
item **65**'s defect avoided rather than added to. **Records only: no build, no
callgrind.**

**Why it exists.** `harness/check.py:3655` carries an **operative rule no PHP
document cited**: *"for a cross-RUNG comparison use `kernel_exclusive_ir`; use
`marginal_ir_per_call` for **anti-collapse**, which is what it was built for"* …
*"a published correction must be compared against **that pattern's OWN R5 − R4
null** before it is quoted in a band."* ⚠ **`ph64` publishes its headline in
family B** (F74), and every comparison this programme publishes is cross-rung.

⚠⚠ **FIRST, WHAT IS *NOT* NEW — I nearly published three re-derivations, and a
`grep` caught it, not a measurement.** The identity census (**F82**, to the row),
*"`ph45`/`ph64` are not nulls"* (**F82**), *"B's null can exceed the effect on
`ph03/small`"* (**F74**, `+3.65 %`) and *"B is for anti-collapse"*
(**`STATISTICS_001 §2`**, which `_038` §6.1 calls *"exactly right"*) were all on
file. ⭐ **The cheap check — *does a document already say this?* — came AFTER I
wrote the probe and cut the finding by three quarters. It should come first.**

### ✅ RESULT 1 — NOTHING IS OVERTURNED

`O3/isolated`, ratio = `|published difference| / |own row's null|`, `Ir`/call:

| row | inp | null_B | `c-gcc − safe_naive` | ratio | `safe_tuned − unsafe` | ratio |
|---|---|---|---|---|---|---|
| `ph03` | small | **+266.000** | −2311.41 | **8.69** | +830.83 | ⭐ **3.12** |
| `ph00` | small | −1.000 | +361.42 | 361.42 | +4.00 | **4.00** |
| `ph07` | small | +37.340 | −806.51 | 21.60 | +198.78 | **5.32** |
| `ph29` | small | +8.830 | +295.80 | 33.50 | −70.58 | **7.99** |
| `ph03` | large | −31.000 | −18862.97 | 608.48 | +6076.00 | 196.00 |
| `ph16` ×2 · `ph29` large · `ph07` large | | **0.000** | — | ⚠ `null~0` | — | ⚠ `null~0` |
| `ph45` ×2 · `ph64` ×2 | | ⛔ | — | ⛔ **NO NULL** | — | ⛔ **NO NULL** |

**Not one published PHP figure is inside its own null**; the smallest margin is
**3.12×**. ▶ **The frozen harness's rule, applied to this corpus, changes no
published number.**

### ⭐ RESULT 2 — but the SAME-LANGUAGE margins are the tight ones

**Same-language min `3.12×`; cross-language min `8.69×`.** Five of six
same-language cells are **under 8×**; five of six cross-language cells are **over
21×**. ▶ ⭐⭐ **So the `fixed-R4 bound` — this programme's own headline statistic
— sits an ORDER OF MAGNITUDE CLOSER to its own noise floor than the
cross-language claims do, and nobody had computed that.**

⚠⚠ **A RATIO IS A SIGNAL-TO-NOISE RATIO ONLY WHERE THE NULL IS NOISE, AND IT IS
NOT EVERYWHERE.** `ph00`'s `±1.000` is the **explained** *one instruction per
kernel call in `main`* class (`_038` §4.2) and `ph03/large`'s `−31.000` matches
`p42`'s in `check.py`'s own PAT table — **structural, not noise.** ⭐ **The one
cell where the null is KNOWN to be pure layout noise is also the tightest:
`ph03/small`'s `+266.000`, measured by F83 in libc on a byte-identical pair.
`3.12×` and `8.69×` are the defensible numbers.**

### ⚠⚠ RESULT 3 — `ph45` and `ph64` have NO null at any cell, and `ph64` publishes in B

**5 of 7 rows have a valid null somewhere** (`ph07` by F82's count rescue,
`ph00`/`ph29` also at `-O0` — **which F82 never checked, because F82 measured O3
only**). ⛔ **`ph45` and `ph64` have NONE**, so the frozen harness's *"compare
against that pattern's OWN null first"* **cannot be satisfied on either by this
method** — and **`ph64` is the one row whose headline is family B.** ▶ **The row
that most needs the null is the row that cannot produce one.**
⭐ **This is open item 61's rows arriving from a second direction**: item 61
reads the non-`exact` pins as an **admissibility** problem; they are **also** a
**measurement** problem. ⚠ **Item 61 says three rows; by F82's own predicate it
is TWO** — `ph07` is rescued for measurement and **not** for item 61's
byte-identity argument. **Same pins, two predicates, two counts, both right.**

### ⭐⭐⭐ RESULT 5 — FAMILY B's SENSITIVITY, ON F82's OWN CELLS

F82: *"**A NULL CONTROL IS ONE-SIDED.** A statistic hard-wired to `0` would ace
every null in this tree … the **sensitivity** half was never measured."* ▶ **F82
then measured family A's and never B's.**

| row | opt | inp | Δnopad | **A** Ir/call | rate/insn | **B** Ir/call | **\|B/A\|** | sign |
|---|---|---|---|---|---|---|---|---|
| `ph45` | O3 | small | **−2** | **−2.0000** | **1.0000** | **+99.250** | **49.6×** | ⛔ opposite |
| `ph45` | O3 | large | **−2** | **−2.0000** | **1.0000** | **+787.860** | **393.9×** | ⛔ opposite |
| `ph64` | O3 | small | **−1** | **−0.5093** | 0.5093 | **+193.360** | **379.6×** | ⛔ opposite |
| `ph64` | O3 | large | **−1** | **−0.5100** | 0.5100 | **−28.770** | **56.4×** | same |
| `ph03`·`ph07`·`ph16`·`ph45`·`ph64` | O0 | small | +17 … −170 | — | 1.0 … 190.5 | — | **0.2× … 3.0×** | mixed |

✅ **F82's OWN CONTROL REPRODUCES** (`N7b`): `ph45`'s rate is **exactly 1.0000 on
both inputs, 7.5× apart in call count**, `ph64`'s **0.5093/0.5100** — agreeing to
**0.0007** on a conditional path. **My reading lands on a published finding's
digits, which is what licenses the new column.**

⭐⭐ **THE FINDING IS A REGIME SEPARATION, CLEAN AND WITH NO OVERLAP** (`N8`):
**`|B/A|` is 49.6–393.9× at EVERY small-Δ cell and 0.2–3.0× at EVERY large-Δ
cell.** ▶ **B loses a SMALL code difference completely — and small-Δ is exactly
where a `fixed-R4 bound` operates.**

⚠⚠ **TWO THINGS I MUST NOT CLAIM.** (a) ***"B gets the sign wrong"* is NOT
regime-specific** — `ph16/O0` (Δnopad **−39**) and `ph45/O0` (**−170**) disagree
too, so it is **5 of 9 cells, 3-of-4 small against 2-of-5 large.** **The
MAGNITUDE ratio separates by regime; the SIGN does not**, and `N8`/`N9` test them
separately, with the `1.0 Ir/call` floor, so they cannot be merged. (b) **B is
not *"wrong"* — it is not measuring the kernel.** B is a **whole-program** slope,
so its true value on a pair differing by 2 instructions is **not** `−2`. ▶ **The
defensible statement: at most `|Δnopad|` Ir/call of B's reading can be the code
change, so on `ph45/O3/large` at least `785.86` of `787.86` is something else.**

### ⭐⭐⭐ WHAT IT CHANGES: THE AXIS IS **SAME-LANGUAGE vs CROSS-LANGUAGE**, AND NOW IT HAS A MECHANISM

The harness prefers A because it *"is symbol-scoped so it never charges a
callee"*. **F85 measures that same property as A's defect.** Both are right, on
different comparisons — and Result 5 makes it a **signal-to-noise regime** rather
than a taste:

| comparison | the code difference | the callee/layout term | column | authority |
|---|---|---|---|---|
| **same-language** (R4/R5, R2 vs R3, the `fixed-R4 bound`) | **small** — 1–2 instructions | **50–394× the signal** | ✅ **only A can resolve it** | `check.py`'s operative rule, 66-cell census |
| **cross-language** (R1 vs R2/R3) | **large** — tens of percent | ⭐ **IS the effect** (C calls `malloc` `2n+2`×) | ⛔ **not A** | `_038` §1.5; F85's 29 of 38 |

▶ ⭐ **F85's 29-of-38 split is not just a count — IT IS THE AXIS.** And the
argument for A same-language is now **structural and independent of the sampling
question**: no callee-inclusive statistic can resolve a 2-instruction difference
under 100–800 `Ir`/call of callee and layout work. ⚠ **So `STATISTICS_001 §4`'s
*"publish both, labelled, ALWAYS"* is OVER-BROAD** — A alone suffices where the
comparison does not cross languages. → open item **72**.
⚠ **The calibration's limit, stated: `Δnopad` exists only for the `unsafe vs
verus` pair, so the regime is directly measurable on R4/R5 and INFERRED
elsewhere.**

⚠⚠ **AND IT DEMOTES THE B-vs-C QUESTION WITHOUT SETTLING IT.** Both carry the
same attribution noise — `ph03/small` reads C `+265.924` against B `+266.000`
(F84's own table) — **so the choice between them was never about the null.**
⛔⛔ **I DID NOT MEASURE C's SENSITIVITY**, and the prediction is that **C fails
the small-Δ regime too.** ▶ **Item 62 must test that FIRST** — its own text
already demands *"its own null must be measured before it is believed"*; **Result
5 says measure its SENSITIVITY in the same breath, because the null alone is
one-sided.**

### ⛔⛔ AND TWO ERRORS OF MINE IN ONE PROBE, THE SECOND WORSE THAN THE FIRST

1. `N1` first asserted A's null is `~0` across **all** cells and **FAILED** at
   `ph03 O0/isolated/small +3237.828`. **I had maxed over the OPT LEVEL** — the
   first of the three axes `check.py`'s docstring names one screen up (*⚠⚠⚠ DO
   NOT MAX IT OVER MODE, OVER LEVEL, OR OVER INPUT*).
2. ⛔⛔ **The fix used `identity[opt] == 'exact'` — and F82, MY OWN FINDING ONE
   ROUND OLD, EXISTS TO SAY THE LEVEL IS THE WRONG PREDICATE.** F82's `N6` was
   written because a level-based restriction *"drops PAT's family-B worst by
   5.7×, to a perfectly plausible number, by discarding five valid cells — **I
   would have published it**."* The predicate is `Δnopad == 0 and Δbytes == 0`.

⭐⭐ **Fifth scoping error in this thread, and the FIRST where the document that
already supplied the scoping was my own previous finding.** ✅ **Both caught by
must-fire negatives, not by review** — and `N1b` now makes the scoping
load-bearing (A's null is **>100 Ir/call at 8 of 16 invalid cells**), so `N1`
cannot pass under a wrong scoping the way my first version did.

### F90 — ⛔⛔⛔ **REFUTED ON ITS OPERATIVE HALF BY F92.** Family B's flaw IS a tunable parameter — **but the lever is far too weak, and the review's decision STANDS**

⛔⛔⛔ **READ THIS FIRST. `TASK_PHP_039` MEASURED THE LEVER'S GAIN AND IT IS
`W^(−0.5)`** — six fits on two rows, all in `[−0.649, −0.405]`. **So reaching
1 % of `ph29`'s effect needs `W ≈ 6 474–17 321`, a 22–58× gate stage**, and F93
shows the pin also sits on a **bias the lever cannot reach at all.**
▶ ✅ **UPHELD: `probe_iters` IS a parameter and not a definition.**
▶ ⛔ **REFUTED: *"the cheaper and better fix is to RAISE `probe_iters`"*. Item 68
answers NO, `TASK_PHP_038` §6's ruling STANDS, and item 62 is the answer.**
⚠ **This is the EIGHTH correction to my own work in this thread — and the first
delivered by an experiment written to be able to say it** (`_039` §1's `E5` was
a declared falsifier for its own conclusion; it did not fire, but the
disconfirming arm existed). **The section below is left as written.**

Manager, `.tasks-php/probes/ph64_draws.py`'s data re-sliced. ⚠ **UNREVIEWED**, and it
**disagrees with `TASK_PHP_038` §6**, whose work it rests on.

**F88's draw effect is ORDINARY SAMPLING ERROR AND `probe_iters` IS A LEVER ON
IT.** `ph64/small`, cross-language worst case, **disjoint** spans:

| span width | disjoint spans | `safe_tuned` vs `unsafe` | `c-gcc` vs `safe_naive` |
|---|---|---|---|
| **100** — the shipped pin | 9 | 0.067 pp | **8.124 pp** |
| 200 | 4 | 0.037 pp | **2.092 pp** |
| 300 | 3 | 0.021 pp | **1.243 pp** |

⚠⚠ **I CANNOT PIN THE RATE AND I TRIED TWO WAYS THAT ARE BOTH CONFOUNDED, IN
THE SAME DIRECTION.** Sliding spans share draws (consecutive width-500 windows
share **400 of 500**, so their agreement is partly the shared draws); disjoint
spans leave **fewer samples**, and the observed range of 3 draws is smaller than
that of 9 from the same distribution. **Sliding gave 1.637 pp at width 500 and
1/width predicted 1.625 — that agreement is not evidence, it is two biases
meeting.** ▶ **What survives is the DIRECTION, on which every slicing agrees,
and the width-100 figure of 8.124 pp, which is 9 genuinely disjoint spans.**

⭐⭐⭐ **AND HERE IS WHY IT MATTERS: OF THE FOUR FAMILIES, B IS THE ONLY ONE WITH
NO DEFINITIONAL GAP.**

| | definitional gap | measured |
|---|---|---|
| **A** | ⛔ blind to callees | `inside_share` **0.055** on `ph45` — i.e. **94.5 % of the work is in callees**, which is the load-bearing evidence. ⚠⚠ **The second clause this row used to carry — *"spread `0.000000` pp over 9 variants"* — IS WITHDRAWN as evidence for blindness: `ph53` reads `39.9`/`45.3` pp on the same statistic over 20 variants, so that was a fact about `ph45`'s nine variants and not about A** (item **82**) |
| **C** | ⛔ blind to `main` | the `−1.00` class — **1 insn/call in `main`**, which C cannot see |
| **W1** | ⛔ carries a language-dependent fixed term | **≈176 k `Ir`**, two rows agreeing to 0.45 % |
| **B** | ✅ **none found** — it cancels the fixed term and charges everything | its flaw is **`probe_iters`**, a `spec.md` **parameter** |

▶ **Every documented flaw of B is either SAMPLING (fixable by one pin) or SHARED
WITH C**: F84's *"B misses real work"* is the draw (F88); F83's layout-driven
libc charge applies to **C equally** (`ph03`'s C reads `+265.924` between
**byte-identical** kernels). ⚠⚠ **So `TASK_PHP_038` §6's ruling — *"the second
column MUST be C"* — does not follow from its own findings, and I think it is
wrong.** ⭐ **The cheaper and better fix is to RAISE `probe_iters`.**

⚠ **What the review got right and I am not disturbing:** W1 is **not**
independent of C (§1.3, measured), so *"three independent statistics"* was my
error; and the cross-language flips **do** survive C (§1.1, 28 of 29). **F85 is
untouched by this.**

⚠⚠ **THE COSTS, BOTH REAL:** `probe_iters` lives in `spec.md`, so it is inside
`contract_sha256` — **a re-gate per row**, 7 PHP and 33 PAT, and it moves every
`marginal_ir_per_call` in every gate record. And B needs **two** runs, so
widening multiplies callgrind time (width 500 is ~5× width 100). ⓘ **PAT
publishes in A**, so the PAT side may not need it at all — ⚠ **that is a
PAT-side judgement and `results/SYNTHESIS.md` is its authority, not this file.**

⭐ **The whole argument, with the review's verdicts and the open disagreement, is now in `.tasks-php/STATISTICS_001.md` — COMMITTED, because it had been living in gitignored `.temp/` (item 65's own defect).**

▶ **So item 62 is re-scoped, not closed**: family C is still worth building —
it is the only *attributable* column that sees callees, and it is what
adjudicated F85 — but **it is no longer the answer to B's instability**, and
**the cheapest next experiment is `probe_iters` on ONE row.** → **item 68.**

### F89 — ⚠ **REVIEWED AND NARROWED:** ITEM 66 ANSWERED **NO**, AND IT SHARPENS F88: THE DRAW **CANCELS IN A SAME-LANGUAGE RATIO** AND **DOES NOT** CROSS-LANGUAGE — ⚠ **BUT ITS `0.07 pp` IS NOT *THE* SAME-LANGUAGE SPREAD**

> ⚠ **REVIEWED AT `TASK_PHP_043` §5.7 — UPHELD-NARROWED.** ✅ **The contrast
> reproduces at `55.6×` by a DIFFERENT design**, which is the second method this
> finding needed. ⛔ **But F89's `0.07 pp` is `1.95×` from the reviewer's
> `0.1365 pp`, and the two span sets are DIFFERENT POPULATIONS** — ▶ **so `0.07`
> must be quoted as *that sweep's* same-language spread and never as *the*
> same-language spread.**

Manager, `.tasks-php/probes/ph64_draws.py` (`--selftest` **PASS, 5 negatives**).
⚠ **UNREVIEWED** (rule 9). Nine **100-wide** spans at different offsets, so every
slope is a 100-draw sample and the only thing varying is *which* draws.

✅ **The pipeline reproduces both controls before being used**: `ph03`'s level
spread comes out **0.034 %** against F88's reported **0.03 %** (negative **N4**),
and my `[100,200]` span reproduces the gate's `c-gcc` marginal to **0.12 %**
(**N5**). ⭐ **And the headline figure is reproduced EXACTLY**: `ph64`'s
`safe_tuned` 9351.56 / `unsafe` 7987.14 → **+17.08 %**, the gate record's own
`O3/isolated/small.bin` numbers to the digit.

**`ph64` LEVEL spread across draws: 6.75 – 7.04 %** on all four cells.
⚠ **So BOTH of my declared expectations were wrong.** I predicted **> 10 %**
(E1) and named a falsifier at `ph03`-like **0.03 %** (E5). **The truth is
between the two rows**: ~200× `ph03`, but **4.6× LESS than `ph29`'s 32 %.**
Per-call allocation produces real heterogeneity and **not** as much as
`ph29`'s per-window `navail` draw.

**And the RATIOS, which is what a row publishes:**

| pair | published `[100,200]` | other 8 draws | spread | verdict |
|---|---|---|---|---|
| **`safe_tuned` vs `unsafe`** — ⭐ **ph64's HEADLINE** | **+17.08** | +17.05 .. +17.12 | **0.07 pp** | **INSIDE** |
| `safe_naive` vs `safe_tuned` | +32.68 | +33.04 .. +33.68 | 1.00 pp | ⚠ **OUTLIER** |
| `c-gcc` vs `safe_naive` | +243.21 | +235.09 .. +242.52 | **8.12 pp** | outside by 0.29 % of effect — immaterial |
| `c-gcc` vs `safe_tuned` | +355.38 | +347.95 .. +356.58 | **8.63 pp** | INSIDE |

⭐⭐⭐ **ITEM 66's ANSWER IS NO. `ph64`'s PUBLISHED B1 HEADLINE IS NOT AN
UNSTABLE DRAW** — it moves **0.07 pp** on a **+17.08 %** effect, i.e. **0.4 %
relative**, and the published draw sits inside the range. ▶ **So the reviewer's
conditional — *"if its B moves like `ph29`'s, the ban on family B is not a style
rule, it is a correctness fix"* — does NOT trigger. The disqualification of B
rests on F84's OBSERVATION alone, not on F88.**

⭐⭐ **THE SHARPER STATEMENT, and it is the same row and the same nine draws:
`0.07 pp` same-language against `8.63 pp` cross-language.** Every rung walks the
**same** window sequence, so the sampling error cancels in a ratio **only when
the two cells' cost-vs-window-size curves match** — which they do between two
Rust rungs and do **not** between C and Rust, because the C rung allocates
`2n+2` per call and scales differently. ▶ **This is the reviewer's own Q2
prediction, measured on a second row**, and it is a more useful rule than *"B is
one draw"*: **the draw threatens cross-language B figures and leaves the
`fixed-R4 bound` alone.**

⚠⚠ **AND MY OUTLIER TEST HAD NO MAGNITUDE FLOOR — the third time this round.**
Its first version fired on `ph03` at spreads of **0.02 pp** and **0.00 pp**,
reporting floating-point noise as a finding. **That is the `ph00` near-zero sign
flip (F86) and the `BLIND` class's defect (item 67) a third time: a predicate
that is technically true and carries no information.** ▶ Fixed with a **relative**
floor — *does the draw move the number enough to change what the row claims?* —
and the `ph64` verdicts above are after the fix. ⭐ **A pattern worth naming:
every taxonomy I wrote this round needed a magnitude floor and none of them had
one on the first pass.**

### F88 — ✅ **REVIEWED AND UPHELD:** **FAMILY B IS ONE DRAW OF A SAMPLING DISTRIBUTION**, AND ON `ph29` THAT IS BIGGER THAN EVERY ERROR SOURCE ALREADY ON FILE

> ✅ **REVIEWED AT `TASK_PHP_043` §5.6 — UPHELD.** `ph29`'s **32 %** re-derives as
> `range/mean = 31.42 %` on an **independent 8-span sweep**, with the `ph03`
> control at **0.02–0.03 %**. ⚠ **Two normalisations are in play — `31.4 %` vs
> `38.6 %` — and NEITHER document says which it is using.** ▶ **Owed: name the
> denominator wherever the figure appears.**

> ✅ **UPHELD AND EXTENDED BY `TASK_PHP_039`** — `ph03`'s `0.02–0.03 %` control
> reproduces exactly, and all three drivers are byte-identical in shape with 32
> windows each, so `ph03` is **the same mechanism with uniform work**.
> ⚠⚠ **NARROWED ON ONE POINT: on `ph29` the published draw is not MERELY a
> draw.** F93 shows the `[100,200]` region is the extreme **every time, at all
> four widths**, and the excess **decays with `n`** — so *"the published draw is
> the LARGEST of seven"* is **largest because it is EARLIEST**, and now has a
> cause. ⓘ Also: **F89's spread figures were RANGES, not SDs** (`_039` §4.4),
> which nothing said at the time.

`TASK_PHP_038`, the **reviewer's own** finding. ⚠ **UNREVIEWED — it is the
reviewer's, so rule 9's cycle has not closed on it.** ✅ **Manager-verified where
it is cheap to**: `probe_iters` is `[100, 200]` in **all seven PHP `spec.md`s and
in `p11`**, and the reviewer reports its `[100,200]` slope reproduces every
published `marginal_ir_per_call` **to 0.01 `Ir`** — so the thing it is describing
really is family B.

⚠⚠ **This is in no finding, no `spec.md` note, and not in `check.py`'s
null-control docstring — which corrects that table for mode, opt level, input and
(per F82) identity level, but not for THIS.**

**`Ir(n)` is not linear in `n`.** Adjacent-span slopes over `n = 100..960`:

| row / cell | slopes | spread |
|---|---|---|
| `ph29/small` `c-gcc` | 1576.8 .. 2084.2 | **32.2 %** |
| `ph29/small` `safe_naive` | 1365.9 .. 1794.2 | 31.4 % |
| `ph29/small` `unsafe` | 1278.8 .. 1695.4 | 32.6 % |
| `ph03/small` `c-gcc` | 7516.6 .. 7519.1 | **0.03 %** — the control |

**The mechanism is in committed driver source**, not inferred: `c/main.c`'s
`SLB-DRIVER` loop picks the window index `k` as a **pseudo-random function of the
running accumulator** (`acc * nwin >> 64`, `acc = acc*31 + r`). `ph29/small.bin`
holds 32 windows whose **per-window work varies**, so B is the mean over a
**pseudo-random 100-element sample** of them — deterministic, but a *sample*.
⭐ **`ph03` has 32 windows too and reads 0.03 %, because its per-window work is
uniform. That contrast is the control.**

⚠ **The reviewer's own first hypothesis was WRONG and its negative caught it**: it
predicted plain *aliasing* (spans at exact multiples of the 32-window cycle would
be stable); `alias.py::N3` **FAILED**, because the sequence is not indexed by
iteration so there is no cycle to align to. **It published the refutation instead
of the tidy story.**

⛔⛔ **AND IT MIS-ATTRIBUTES F85's OWN RESIDUAL — MY CLAIM, CORRECTED.** F85 says
*"B and C do differ by 2–3 pp on `small.bin` — the confound is real and
present"*. Across **seven** draws, the published `[100,200]` draw is an
**OUTLIER** and every other draw sits within **0.17–0.22 pp** of family C:

```
ph29/small               F85 B   F85 C   (200,400) (300,600) (400,800) (640,960)
c-clang vs safe_tuned    -2.82   -4.85     -4.18     -4.67     -4.34     -3.88
c-gcc   vs safe_naive   +17.85  +14.55    +15.08    +14.78    +15.12    +15.50
```

▶ **So 90–93 % of that gap is the DRAW, not the attribution confound F83/F84
describe.** ✅ **The SIGN is stable across all seven draws on every pair, so no
flip verdict moves and F85's conclusion is untouched.**

⚠⚠ **Two consequences that are not cosmetic:**

1. ⭐⭐ **`inside_share` IS NOT A SHARE ON `ph29`.** `s = A/B` divides a mean over
   **25 000** calls by a mean over a *different, biased* **100**-call sample.
   ▶ **F80's `min(inside_share)` rule and F86's `r = s_a/s_b` are
   arithmetically fine and INTERPRETIVELY VOID on any row with heterogeneous
   per-window work.**
2. **F84's `ph29` figures inherit it** — *"99.31 % artefact"* and *"`ph29/large`
   C `+2.383` against B `+0.000`"* are readings of this unstable quantity.
   ⭐ **The CONCLUSIONS get STRONGER** (a sampling error is two-directional by
   nature); **the MECHANISM changes.**

▶ **The cheapest next measurement in the programme, and the reviewer flagged it
rather than guessing: `ph64`.** It allocates `2n+2` blocks per call so its
per-window work must vary strongly — **and it is the one row that publishes B1.**
**UNTESTED.** → **item 66.**

### F87 — ⭐⭐⭐ `ph45`'s R4 **AND** R3 ENDPOINTS BOTH MOVE, THE BOUND'S **SIGN REVERSES**, AND `get_unchecked` IS THE **EXPENSIVE** SPELLING

`TASK_PHP_037`. ✅ **Manager-verified, not from the report — and SAYING WHICH
FILE EACH FIELD CAME FROM, which this sentence originally did not.** From
**`results-php/gate/ph45-…json`**: `verdict PASS-WITH-BLOCKED-ROWS`,
`failures []`, `complete_run true`, `controls_json {"spellings.json":
"FRESH"}`, `contract_sha256` **unmoved**. From
**`controls/spellings.json`**: `verus_checked true`, `problems []`,
`r4_endpoint_degenerate false`, `r3_endpoint_degenerate false`.
⚠⚠ **`verus_checked` AND `problems` ARE NOT GATE FIELDS AT ALL** — absent from
**all 8** php gate records (`_041` candidate J, manager-confirmed), so a reader
who looked for them there reasonably concluded the verification was invented.
▶ **It was sound and UNDER-ATTRIBUTED**, and the fix is in this sentence rather
than in a paragraph below it (item **73**). ⓘ `problems` **is** a *preflight*
field; `verus_checked`'s stand-in is `verus["verus.rs"] = {verified, errors,
pinned}`. **Brackets `66/0` and `14/0`, run by the manager
independently — identical to the opening, so no re-measure.**

| side | variant | trusted sites | **W1** |
|---|---|---|---|
| R4 | `v0_shipped` | 12 | +0.00 |
| R4 | **`r4_buf_slice_inline`** | **10** | **−23.47 %** |
| R4 | `r4_buf_array` (**out of contract**) | 10 | −23.48 % |
| R4 | **`r4_mirror_unchecked`** | 12 | **+20.97 %** |
| R3 | `v0_shipped` | 0 | −3.06 |
| R3 | **`r3_namecmp_fn`** | 0 | **−20.66 %** |

1. ⭐⭐⭐ **THE R4 ENDPOINT MOVES** — twin verifies **41/0**, no `assume`, no new
   trusted item, no `is not supported`, **and 10 unchecked-dereference call
   sites against the shipped rung's 12. Cheaper AND a smaller trusted
   surface.** Second row in either programme after `ph29` (F77).
2. ⭐⭐⭐ **SO DOES R3 — the first row where BOTH do**, 18.2 % under shipped R3.
   ⚠⚠ **AND THE SIGN OF THE BOUND REVERSES UNDER SEARCH**: shipped, R3 is
   cheaper; under the cheapest spelling found on each side, **R4 is cheaper by
   3.5 %**. ▶ **So this row is NOT `ph16`'s F67 mechanism — F67 STAYS n = 1.**
3. ⭐⭐⭐ **THE MIRROR CONTROL IS THE SHARPEST RESULT IN THE CORPUS:
   `get_unchecked` IS THE EXPENSIVE SPELLING HERE.** `r4_mirror_unchecked` is
   the winner's shape *exactly* — same signature, same hoist, same attribute,
   same 12 trusted sites — with the arena reads left **unchecked**, and it is
   **44 pp DEARER** than the checked spelling of the same program. ⚠ **The
   conclusion is landed; the MECHANISM is marked OPEN and unverified** under
   rule 9's split, after the engineer re-read its own prose and found it had
   stated a story as fact — **F72's shape, caught by its author.**
4. ⚠⚠ **THE ROW'S OWN STATED R3 MECHANISM IS REFUTED.** `safe_tuned.rs`'s header
   says *"the bound LLVM gets free from the TYPE is worth more than the check it
   removes"*. The `&[u8; REQ]` type is a **TIE** against a plain `&[u8]`
   sub-slice — measured **three** times, twice safe and once unsafe — and the
   array spelling is the one **Verus refuses**. ▶ **The lever is the HOIST, not
   the type**, and §1 of the task file named a lever that could not have shipped.
5. ⚠ **R4 searched, NOT exhausted**: nine spellings shipped, **seven more priced
   and dropped**, including two trusted-surface reductions that came out
   **dearer** (+4.07 %, +7.51 %) — so neither is the *"smaller trusted surface
   at the same price"* they were proposed as.

⭐ **§H: 128 cases, 77 must-FIRE / 51 must-NOT-fire, ALL PASS** (`ph29`'s bar was
75), **and three found real defects** — two in code written that task, one
**latent in `ph29`'s inherited `twin_identical`, which F79's two fixes do NOT
cover: two `(0, md5(""))` rows still compare equal there.** → **item 63.**

✅✅ **MANAGER'S RULING — `#[inline(always)]` IS A LEGITIMATE RESPELLING, AND THE
ENGINEER WAS RIGHT TO FLAG IT.** It asked for a ruling by name, because without
the attribute `r4_buf_slice` is **+16.65 %**, i.e. *dearer* than the shipped R4,
so **a ruling against would have made the endpoint degenerate and withdrawn
result 1.** ▶ **Decided on corpus precedent, not on argument:
`grep -a -rn '#\[inline' patterns/*/[a-z]*.rs patterns-php/*/[a-z]*.rs` →
`#[inline(always)]` is in **98 shipped rung files across BOTH programmes**,
including `unsafe.rs` (`p08`, `p22`) and `verus.rs` (`p01`, `p03`, `p04`), and
`patterns/p06-rotate/safe_tuned.rs:62` documents the choice as a deliberate
spelling: *"It is a `#[inline(always)]` free function rather than an inline
expression"*. **Ruling it out would retroactively invalidate 98 files.**
⚠ **The worry behind the question is real and is already answered elsewhere** —
if attributes count, a rung could be tuned by attribute rather than by safety
strategy. `.memory/02-bench-rules.md`'s standing rule that **a rung is never
cost-selected** is what contains that: the search reports what exists, the
shipped rung stays put. ⭐ And **both variants ship side by side**, so the
attribute's 40-pp contribution is visible rather than buried in one number.

### F84 — ⭐⭐⭐ FAMILY B **CAN MISS REAL WORK AS WELL AS INVENT IT** — ⛔ AND MY `−1.00` MECHANISM WAS **REFUTED BY THE REVIEW**

Manager, `.temp/mgr172/NOTES.md` §9, probe `bc_sweep.py` (`--selftest` **PASS,
7 must-fire negatives**), profiles from `sweep_cg.sh`, **every binary
md5-verified against its published record**. ⚠ **UNREVIEWED** (rule 9).

**F83 says *"B is measuring real work"*, published off two rows. Over the 12
R4/R5 cells of five PHP rows it is TRUE ON 6 AND FALSE ON 6** — ⚠ **and I had
already published F83's generalisation, which makes this the SECOND time in one
round that a two-row sample of mine did not survive a sweep** (the first was
F82's premise). ⛔ **`ph45` is excluded — `TASK_PHP_037` is rebuilding it.**

| row | inp | level | A | **C** inclusive | **B** slope | disagree |
|---|---|---|---|---|---|---|
| `ph00` | small | exact | 0 | **0.000** | **−1.000** | **100 %** |
| `ph00` | large | exact | 0 | **0.000** | **−1.000** | **100 %** |
| `ph03` | small | exact | 0 | +265.924 | +266.000 | 0.03 % |
| `ph03` | large | exact | 0 | −31.000 | −31.000 | 0.00 % |
| `ph07` | small | norel | 0 | +17.624 | **+37.340** | 52.80 % |
| `ph07` | large | norel | 0 | 0.000 | 0.000 | — |
| `ph16` | small/large | exact | 0 | 0.000 | 0.000 | — |
| `ph29` | small | exact | 0 | **+0.061** | **+8.830** | **99.31 %** |
| `ph29` | large | exact | 0 | **+2.383** | **+0.000** | **100 %** |
| `ph64` | small | differ | −0.509 | +214.970 | +193.360 | 10.05 % |
| `ph64` | large | differ | −0.510 | −28.255 | −28.770 | 1.79 % |

**6 agree under 5 % · 4 where B is larger · 2 where C is larger.** The
decomposition the numbers force:

> **B = C + work OUTSIDE the kernel's call tree + slope-method effects**

⛔⛔ **1. I CLAIMED THE UBIQUITOUS `−1.00` IS A SLOPE ARTEFACT. `TASK_PHP_038` §4.2 REFUTED THE MECHANISM.** `harness/check.py`'s PAT
null table records *"1.00 ≤ |null| < 2 in 35 cells (**34 of them exactly
−1.00**)"* and offers **no mechanism for it**. `ph00` reads **B `−1.000` on both
inputs while C reads `0.000` on both.** ▶ I read that as *"a whole documented
class of that table is the measurement method"*.

> ⛔⛔ **IT IS NOT THE SLOPE — AND THE ANSWER WAS IN EVERY COMMITTED RECORD,
> UNREAD, NEEDING NO CALLGRIND. It is exactly ONE INSTRUCTION PER KERNEL CALL
> EXECUTED IN `main`**: `main_exclusive_ir` Δ = **−199 995 at n = 200 000** on
> `ph00` and **−6 001 at n = 6 000** on `p11`, i.e. `Δ/n = −1.0000` —
> **manager-re-verified on both rows.** ▶ **C reads `0.000` because `main` is
> OUTSIDE the kernel's call tree, so B is RIGHT here and C is BLIND to it, which
> is the opposite of what I claimed.** ⭐ **The decomposition below was correct;
> I attributed the instance to the WRONG TERM — out-of-tree work, not slope
> effects.** ✅ The *observation* is upheld, and on a PAT row. ⚠ PAT-side, still
> **reported for routing** — item 60.

⚠⚠ **2. B CAN MISS REAL WORK, NOT ONLY INVENT IT.** `ph29/large`: **C
`+2.383`/call against B `+0.000`.** **B reports a clean null over a real
call-tree difference.** Every prior treatment of B — **F74's and F83's
included** — assumed the error was one-directional. ⭐ **A two-directional error
is not correctable by any constant**, which matters more than its size does.

**3. It is not one odd row.** `ph29/small` **99.31 %**, `ph07/small`
**52.80 %**; `ph03`, `ph16`, `ph64` agree closely. ⚠⚠ **`ph29` is the row
publishing F77's `−5.63 pp` R4 result, and its R4/R5 B reading is 99.31 %
artefact.** ✅ **F77 is quoted in A1, so F77 is unaffected — but that is LUCK,
not design**, and it is the strongest available argument for naming the
statistic beside every figure.

✅ **AND FAMILY A's NULL IS RE-DERIVED THROUGH A DIFFERENT CODE PATH:**
**`max |A| = 0.000000` over all 8 true-null cells**, computed off the
**callgrind profiles** here rather than off `results-php/` as F82 did — two code
paths, one answer. ⭐ And A reads **`−0.509`/`−0.510`** on `ph64`, matching
F82's `exec_rate` **0.5093/0.5100**: *the same conditional path, from the other
direction.*

⚠ **C IS NOT "THE TRUTH".** It is the kernel's **call tree**, the right unit for
*"what does one call cost"* **only because `main` here is the harness** rather
than the program. And **C does not fix attribution** — on `ph03` the two kernels
are byte-identical and C still reads `+265.924` (F83).

### F86 — ⭐⭐ THE A/B DISAGREEMENT HAS **THREE** CLASSES, AND THE EXACT FLIP TEST PROVES **THERE IS NO SHORTCUT**

Manager, `.temp/mgr172/flip_exact.py` (`--selftest` **PASS, 6 negatives**).
⚠ **UNREVIEWED** (rule 9).

**366 comparisons:** **agree 314 · FLIP 38 · ⭐ BLIND 14.**
**BLIND** = *A is exactly `0` while the whole-program figure is not* — **A says
nothing at all.** ⚠⚠ **My probe's first version scored BLIND as FLIP**, inflating
the count to 52 and producing 14 "mispredictions" of a predicate that was right;
caught by its own negative **N5**, phrased *"a number is being read wrong"*
rather than *"the rule is wrong"*, which is what pointed at the real cause.
⭐ **BLIND is the worse failure**: on `ph45` it is **A `+0.000 %` against a
`+23.37 %` effect**, which is F87 result 4's neighbourhood reached independently.
⚠⚠ **BUT THE TAXONOMY INVERTS THE EVIDENCE ON 5 OF THE 14 BLIND CELLS**
(`TASK_PHP_038` §2.4) — the class lumps *A genuinely sees nothing* together with
*A correctly reads a true zero*, and on 5 cells it is the latter. ⭐ **The
reviewer proposed a test and reported that its own negative FAILED, rather than
shipping it**, so BLIND still has **no** working test. → **item 67.**

⚠ **F80's `|Δs| ≤ 0.02`, scored per class, calls 7 real FLIPS and 13 of the 14
BLIND cells "safe", and flags 153 that agree — 20 failures, not the 6 F80
published.** ⓘ 3 of the 7 are between numbers both under **0.2 %** (`ph00`
−0.111 vs +0.046; `ph45`'s R4/R5 twice), which is two ways of measuring
approximately nothing.

**The exact test, and it is algebra rather than a threshold:** since
`inside_share ≡ A/B`, `a_ratio = (s_a/s_b)·b_ratio` **identically** — so *"the
share ratio explains the disagreement"* is **true by definition and explains
nothing** (F78's shape; I had it written as a mechanism before noticing).
**A flip occurs iff `1` lies strictly between the two ratios — 0 mispredictions
over all 366.**

> ⚠⚠ **`TASK_PHP_038` §2.2: *"0 mispredictions over all 366"* IS A LOGICAL
> TAUTOLOGY AND IS NOT EVIDENCE — F78's shape one level up, in the finding that
> cites F78.** The predicate *is* the definition of a sign flip, so it cannot
> fail, and **my negative N5 cannot fire for the reason its message gives.**
> ✅ The algebra is UPHELD (the reviewer checked it by hand on three cells);
> what is withdrawn is treating its own restatement as a measurement.

⚠⚠ **I THEN TRIED TO REDUCE THAT TO A SCALAR `|effect| < |share mismatch|` AND
IT IS REFUTED, 30 OF 346** — the scalar form drops the *side* condition and
fires wherever the effect sits on the far side of 1. **Kept running and labelled
in the probe rather than deleted, because the tidy form is what somebody will
re-derive.**

⭐⭐⭐ **THE CONSEQUENCE IS DEFLATIONARY AND IT IS THE POINT: the exact test needs
BOTH ratios, so deciding whether A is safe to publish REQUIRES COMPUTING THE
STATISTIC THE RULE WOULD LET YOU SKIP.**

> ⚠ **NARROWED by `TASK_PHP_038` §2.3. I wrote *"no function of the shares alone
> can certify A at any threshold"* — TOO STRONG: a certifier from the shares
> **plus a declared minimum effect size** IS constructible, and rows do declare
> `Ir` floors. It fails here only because no such floor exists.**
> ✅ **And the operative conclusion survives for a SIMPLER, UNCONDITIONAL reason
> the finding under-used: `s ≡ A/B`, so computing the share requires B already.**
> ⭐ That holds with no threshold and no effect-size assumption at all. ▶ **F80's rule is not a licence
to publish A alone — it is a way to EXPLAIN a disagreement after seeing both.
The operative rule is the one `ph45` already follows: PUBLISH BOTH, LABELLED,
ALWAYS.**

### F85 — ⚠⚠⚠ THE **CROSS-LANGUAGE** COLUMN CARRIES **29 OF 38** SIGN FLIPS, AND **28 OF THE 29** SURVIVE FAMILY C

Manager, `.tasks-php/STATISTIC_DECISION_001.md` §5, probes `.tasks-php/probes/callee_share.py`
+ `sweep_cg.sh`. ⚠ **UNREVIEWED** (rule 9), **and it needs a reviewer** — this is
the programme's central claim.

**Of the 38 sign flips, 29 (76 %) are C-vs-Rust**, carrying the largest
magnitudes in the corpus. ⚠ **That is the SIX-ROW corpus's number** (`law 17`).

> ⭐⭐⭐ **RE-RUN 2026-09-17 ON 13 ROWS AND THE CLAIM HELD WHILE THE COUNT DID
> NOT — `758` comparisons, `141` flips, `111` cross-language, `78.7 %`.** The
> share **rose** (76.3 → 78.7) on 2.3× the evidence. ▶ ***The cross-language
> column carries the flips: that is what survives, and it is the sentence to
> publish.*** ⛔ **`29 of 38` is now HISTORY and must never be quoted bare.**
>
> ⚠ **Re-run by the manager off `probes/callee_share.py --flips`** — the probe
> `TASK_PHP_064` promoted out of `.temp/mgr170/`, which is why this could be
> checked at all. ▶ **`law 11`'s whole point, demonstrated on the finding that
> most needed it: F85 is *"the programme's central claim"* and until today its
> evidence was one gitignored file.**
>
> ⛔⛔ **WHAT DID *NOT* GET RE-MEASURED: `28 of 29 survive family C`.** That
> adjudication (`_038` §1.1) ran over the OLD 29. **Nobody has run it over the
> new 111**, so it is a claim about a set that is now a fifth of the population.
> ⚠ **Do not restate it as if it covered them** — open item **64**.

> ⚠⚠ **CORRECTED BY `TASK_PHP_038`, AND THE DRAFT CONTRADICTED ITSELF ON IT.**
> The count is **29, not 28** — `38 − 9 = 29`, and the draft's own *"the
> remaining 9 are Rust-vs-Rust"* implies it, while my `mine.txt` already had 29.
> **76 % was right and "28" was not**; the headline mixed two scripts'
> populations. ⚠ The by-column table also sums to 37 and mislabels `ph45`'s
> R3-vs-R5 pair as R2-vs-R3.
> ⭐⭐ **AND THE REVIEW WENT FURTHER THAN ASKED: all 29 are now adjudicated
> against family C, not the 12 I had — `ph03` 6/6, `ph07` 6/6, `ph29` 16/16
> survive; `ph00` 0/1 is REFUTED by C.** So **28 of 29 survive**, and item 64 is
> discharged. ⭐ **The reviewer's own prediction that `ph03`'s would fail was
> refuted — C tracks B there to 0.006 pp.** ⚠ **Every one was measured against family B, which F84
had just shown confounded by up to ~266 `Ir`/call — 17 % of `ph29`'s own
1 566.56 marginal. So I re-derived them against family C rather than publish and
hope:**

| input | comparison | **A** | **B** | **C** | **W1** | |
|---|---|---|---|---|---|---|
| small | `c-clang` vs `safe_tuned` | **+20.88** | −2.82 | **−4.85** | −5.27 | **confirmed** |
| large | `c-gcc` vs `safe_naive` | **+33.01** | −0.80 | **−1.06** | −1.19 | **confirmed** |
| large | `c-clang` vs `safe_tuned` | **+8.87** | −21.81 | **−22.01** | −21.90 | **confirmed** |
| large | `c-clang` vs `unsafe` | +1.85 | −25.30 | **−25.48** | −25.33 | **confirmed** |
| small | `c-gcc` vs `safe_naive` | +39.92 | +17.85 | +14.55 | +13.83 | agree — **control** |
| large | `c-gcc` vs `safe_tuned` | +51.40 | +7.04 | +6.85 | +6.61 | agree — **control** |

⭐⭐⭐ **EVERY `ph29` FLIP SURVIVES.**
⛔ ⚠⚠ **BUT "THREE INDEPENDENT STATISTICS" IS WRONG AND `TASK_PHP_038` §1.3
MEASURED WHY: C AND W1 ARE NESTED SCOPES OF ONE RUN, NOT INDEPENDENT.** The
fixed per-program term **does** differ by language — **≈176 k `Ir`, two rows
agreeing to 0.45 %** — and it fully accounts for the C-vs-W1 gaps. ▶ **The honest
claim is TWO methods (a two-run slope and a one-run call tree), not three.** ✅ **And the two non-flipping comparisons agree across all
four families, which is the control**: a pipeline artefact would have moved them
too. ⛔⛔ **AND MY CLOSING CLAIM THAT THE 2–3 pp GAP ON `small.bin` SHOWS *"the
confound is real and present"* IS MIS-ATTRIBUTED — see F88. Across seven draws
the published `[100,200]` one is an OUTLIER and every other sits within
0.17–0.22 pp of C, so 90–93 % of that gap is the DRAW.** ✅ Signs stable, so no
flip verdict moves.

⚠⚠ **`ph29/large` `O3`/`isolated` vs `safe_naive` is the sentence this is
about — AND IT OWES BOTH C COLUMNS** (`F108`'s fifth thing; this sentence named
only `c-gcc` until `TASK_PHP_059` found it): **A says `c-gcc` is `+33.01 %`
DEARER than naive safe Rust, while `c-clang` is `−4.36 %` CHEAPER** — and on
`c-gcc` three other statistics say **~1 % cheaper**. ⛔⛔ **So the disagreement
this project is about is not only between STATISTICS; it is between the two C
COMPILERS, and the one-column form hid that.** **The `c-gcc` gap is the
difference between *"safe Rust is a third cheaper than C here"* and *"they are
the same"* — and it is this project's central claim.**

⭐ **This GENERALISES open item 54 rather than repeating it.** Item 54 says
`ph64`'s C rung allocates `2n+2` per call with 60 % of its instructions in libc,
so *"the C-vs-Rust column on this row is not a safety comparison"*. ▶ **Measured:
it is not one row.** ⚠ `ph07`'s and `ph03`'s flips are **not** re-derived
against C and remain B-only — the mechanism is the same and `ph29` makes it
likely, **but that is an inference and the rows are named rather than folded
in.** → **item 64.**

### F83 — ⭐⭐⭐ F74's NULL WAS **MEASURING REAL WORK**, SO B's DEFECT IS **ATTRIBUTION, NOT NOISE** — AND A CONFOUND DOES NOT SHRINK WITH MEASUREMENT

Manager, `.temp/mgr172/NOTES.md` §7, probe `inclusive_ir.py` (`--selftest`
**PASS, 6 must-fire negatives**). ⚠ **UNREVIEWED** (rule 9).

**F82 asked whether the null's premise held. It did not ask the obvious next
question — whether the NONZERO READING IS REAL.** It is.

A **third statistic** is computable from the same profiles and **without
touching frozen code**, because the pinned valgrind 3.27.1 ships
`callgrind_annotate --inclusive=yes` (`measure.py::callgrind_ir` records
**exclusive** only, for two needles): **family C = `kernel` INCLUSIVE `Ir`, the
kernel's whole CALL TREE, from ONE run.**

**`ph03-uudecode-bound`, `unsafe` vs `verus`, O3/isolated — and the two kernels
share `md5_fn` `338505795ee18db952aafcdaec522df4`, byte-identical, not merely
equal in count:**

| input | **A** exclusive | **C** inclusive | **B** slope |
|---|---|---|---|
| `small.bin` | **0** | **+265.924/call** `+3.6581 %` | **+266.000/call** `+3.6522 %` |
| `large.bin` | **0** | **−31.000/call** | **−31.000/call** |

⭐⭐⭐ **B AND C AGREE TO 0.03 % ON `small` AND EXACTLY ON `large`, BY TWO
INDEPENDENT METHODS** (a two-run slope against a one-run call tree). **So
`+3.65 %` — the number F74 calls the PHP programme's worst null — IS NOT NOISE.
It is real work, measured twice.**

⚠ **The environment is ruled out, and it had to be**, because `check.py`
documents a mechanism that would explain it away — *"the environment block
shifts the stack pointer → a per-call stack array's alignment → a different tail
in `__memset_avx2_unaligned_erms`"*, ±7, **between two runs of the SAME build**.
One binary, **three** environment sizes spanning 4 000 bytes: kernel inclusive
is **181 733 873 at every one, spread 0** (negative **N6**).

> ⛔⛔ **THE CONTROL IS WORTHLESS AND `TASK_PHP_038` §4.1 SAYS WHY: IT TESTS A
> MECHANISM THAT CANNOT APPLY TO `ph03`.** `check.py` attributes its ±7 to *a
> per-call **stack array**'s alignment*; **`ph03`'s per-call buffer is
> `emalloc` — HEAP.** So three sizes is not too few, it is **irrelevant**, and
> ⚠⚠ **the mechanism F83 itself names — binary layout → heap alignment, and the
> two binaries differ by 48 text bytes — is UNTESTED.**
> ✅ **F83's conclusion survives on the B/C agreement**, which is independent of
> this control. ⚠ But it survives on **one** leg, not two.
⚠ **The work is LOCATED**: **+205.94/call** in one unnamed `libc.so.6` function
and **+56.98** in a second, both **local** symbols the dynamic table does not
name — nearest exported are `__default_morecore` (+2912) and `timer_settime`
(+3488), offsets far too large to be those. `__default_morecore` is in
`malloc.c`, which puts the cost in the **allocator**. ⚠ **A region, not a
function name** — without libc debug symbols it cannot be named and the probe
does not pretend to.

⭐⭐ **SO THE DEFECT IN FAMILY B IS NOT NOISE, IT IS ATTRIBUTION.** The kernels
are **byte-identical**, so neither rung's code can have caused a 3.66 %
allocator difference. B charges the rung for work the rung did not do.
⚠⚠ **That is a CONFOUND, and unlike noise a confound DOES NOT SHRINK WITH MORE
MEASUREMENT** — which is exactly why calling it noise mattered.
✅ **F74's practical advice — headline family A, name the statistic — SURVIVES.
Its stated reason is replaced by a stronger one.**

⚠ **AND THE PAT CELL SPLITS THE DIFFERENCE, SO BOTH READINGS WERE PARTLY
RIGHT.** `p25-realloc-growth/large.bin`: **C +167.872** against **B +269.520**,
agreeing to only **37.71 %**. Of the worst null in either programme, ~**62 % is
real call-tree work** and ~**+101.65/call is a method artefact of the slope**.
⚠⚠ **I have NOT identified the residual and am not inventing a mechanism for
it** — that is F72, where my stated cause was a story and `_033` produced git
evidence against it. ⓘ `p25/small` reads **0 on all three** — the control.

⚠ **SCOPE: ATTRIBUTION IS A PROPERTY OF THE COMPARISON, NOT OF THE STATISTIC.**
On a **C-vs-Rust** comparison callee work often **is** rung-attributable —
`ph64`'s C rung really does call `malloc` `2n+2` times per call, **60 %** of its
instructions in libc (F71, item **54**). The confound is specific to
comparisons where the two rungs' own code is identical or nearly so, **which is
precisely why the R4/R5 pair was picked as a null** and precisely where the
confound is largest relative to signal.

⚠⚠ **AND I GOT FAMILY C WRONG ON THE FIRST PASS, WHICH IS THIS FINDING'S OWN
LESSON LANDING ON ITSELF.** I wrote that C has *"A's attributability and B's
coverage"*, making it the statistic the project wants. **False** — the allocator
work **is** in the call tree, so C includes it and reads B's number. Corrected:

| | coverage | slope artefact | **attributable** |
|---|---|---|---|
| **A** | ⚠ kernel only — misses 91–94 % on `ph45` | none | ✅ yes |
| **C** | ✅ whole call tree | ✅ **none** — one run | ❌ **no** |
| **B** | ✅ whole program | ⚠ **`+101.65/call`** on `p25/large` | ❌ no |

▶ **C strictly DOMINATES B** — same coverage, one fewer error source — **and no
statistic here solves attribution**, because it is not a property of a column.
⭐ **That is why `ph45` publishing "both families, labelled" is the right answer
rather than a compromise.** → **item 62.**

⭐⭐⭐ **THE META-OBSERVATION, AND IT IS THE PART WORTH KEEPING: F74 HAS NOW BEEN
CORRECTED THREE TIMES IN THREE ROUNDS.**

| | what was wrong | found by |
|---|---|---|
| **F80** | the **rule** (one condition) | `ph45`, the very next row built |
| **F82** | the **premise** (never checked per row) | reading a gate record for another purpose |
| **F83** | the **mechanism** (*"noise"*) | a second, independent measurement |

⚠⚠ **F74 was published from ONE script reading ONE field, and not one of its
three errors was arithmetic.** Every one was found by bringing a **second
method** to bear on the same quantity. ▶ **A statistic's own null is not enough
evidence about a statistic.**

### F82 — ⭐⭐⭐ F74's NULL CONTROL HAD AN **UNCHECKED PREMISE**, AND THE HALF IT NEVER MEASURED IS THE HALF THAT MATTERS

Manager, `.temp/mgr172/NOTES.md`, probe `identity_null.py` (`--selftest` **PASS,
9 must-fire negatives**). ⚠ **UNREVIEWED** (rule 9). Found while reading
`ph45`'s gate record to write item 58's task file.

**F74 settled item 52 by a null control**: *"`identity` pins R4 and R5
byte-identical, so `verus − unsafe` has a known true value of 0."*
⚠⚠ **`.temp/mgr170/null_control.py` — my own probe, the one F74 rests on —
NEVER CHECKED THAT PREMISE ON ANY ROW. It asserted it for all 39.** Measured
`unsafe vs verus` level at O3: **`exact` on 4 of 7 PHP rows and 28 of 33 PAT**.
Not exact: **`ph07` norel · `ph45` differ · `ph64` differ**; `p25` `p28` `p29`
`p34` `p36` norel.

⚠⚠ **BUT THE LEVEL IS THE WRONG PREDICATE, AND RESTRICTING ON IT WOULD HAVE
LOOKED RIGHT.** `exact` is **byte**-identity; a *count* statistic needs only the
executed count to agree, and `norel` covers **two** situations — same
instructions at different rip-relative displacements, and genuinely different
code. **The rows say which, in their own `identity` notes**: `p25` *"both
resolving to the same absolute address `0x7910` … the instruction count (189
non-pad at `-O3`) and the byte count are all identical"*; `ph07` *"R4 == R5 at
O3 **UP TO RELOCATIONS** … 251 instructions and 953 bytes in BOTH cells."* So
the predicate is **`Δnopad == 0 and Δbytes == 0`**, read from the identity
entry's own `counts_a`/`counts_b`:

| | true null | level said no, **Δnopad rescues** | **genuinely NOT a null** |
|---|---|---|---|
| PHP | 4 | 1 — `ph07` | **2 — `ph45`, `ph64`** |
| PAT | 28 | 5 — `p25` `p28` `p29` `p34` `p36` | **0** |

✅✅ **ALL 33 PAT ROWS ARE TRUE NULLS, AND EVERY NUMBER F74 PUBLISHED IS
INTACT** — PHP family-B worst **+3.6522 %** (`ph03 small`, and `ph03` *is*
`exact`), PAT **+5.0102 %** (`p25 large`), family A **0.0000 %** on both.
⚠⚠ **The trap is the middle column**: a level-based restriction drops PAT's
family-B worst to **−0.8734 %**, a **5.7×** reduction to a perfectly plausible
number, by discarding **five valid cells**. **I would have published it.** The
negative that stops it is **N6** — `p25`'s `spec.md` contains the literal string
`identity: unsafe == verus, O3 exact` as **shared-block boilerplate** while its
real pin, in a table row, is `` `O0: norel`, `O3: norel` ``. ⭐ **Read the
record, not the `spec.md`.**

⭐⭐⭐ **THE REAL GAP: A NULL CONTROL IS ONE-SIDED, AND F74 ARGUED FROM NOTHING
ELSE.** **A statistic hard-wired to `0` would ace every null in this tree.**
The **sensitivity** half was never measured — and the rows that are *not* nulls
supply it for free, because there the kernels differ by a **known** static count
so family A has a **predicted** nonzero value:

| row | input | Δnopad | Δ(A) | `n_iters` | `exec_rate` |
|---|---|---|---|---|---|
| `ph45` | `large.bin` | −2 | **−400** | 200 | **1.0000** |
| `ph45` | `small.bin` | −2 | **−3000** | 1500 | **1.0000** |
| `ph64` | `large.bin` | −1 | −102 | 200 | 0.5100 |
| `ph64` | `small.bin` | −1 | −764 | 1500 | 0.5093 |

⭐ **Family A resolves a 2-instruction static difference to the instruction**, on
two inputs 7.5× apart in call count. ⚠ **`1.0000` is "too clean" and too-clean
is the only warning F52 gives** — so **`ph64` is the control on `ph45`**: if the
arithmetic were feeding itself every row would read `1.0`, and `ph64`'s
instruction sits on a **conditional** path whose rate the two inputs agree on to
**0.0007**. Three fields, two files, no fitting; negatives **N8** (both `1.0`
and `<1.0` cells must exist or §3 proves nothing) and **N9** guard it.

⭐ **AND THE SIGN: ON `ph45` AND `ph64`, R5 IS CHEAPER THAN R4** — Δnopad −2 and
−1, family A **−0.0383 %** and **−0.0067 %** ⚠ (`small.bin`; `large.bin` is **−0.0054 %** and **−0.0009 %** — 7× apart, and `TASK_PHP_037` §9.3 correctly flagged that I published these UNLABELLED, which is `check.py`'s own *DO NOT MAX IT OVER INPUT* warning landing on me inside the finding that quotes it approvingly). Nothing is violated (both pin
`differ`), but the direction is **F77's shape from a new angle**: F77 found an
admissible R4 cheaper than the shipped one; this is the **shipped R5** cheaper
than the shipped R4, on two of six rows, **with no search at all**.

⚠ **FOR ROUTING — `harness/check.py` HAS THE SAME UNCHECKED PREMISE.** Its null
docstring is *more* careful than my probe was: it corrects for **mode**, **opt
level** and **input**, and warns **⚠⚠⚠ A NULL IS A PROPERTY OF A CELL. DO NOT
MAX IT OVER MODE, OVER LEVEL, OR OVER INPUT.** It does **not** correct for the
**identity level**, and its worst quoted cell — **`p25 large +269.52`** — is the
row pinned `` `O3: norel` ``, while the docstring justifies the whole table by
*"`identity` forces R4's and R5's kernels to agree byte for byte."*
✅ **The number is right and the justification is wrong** (p25 rescues it by the
Δnopad route). ⚠⚠ **`harness/` is FROZEN — reported, NOT fixed**; and
`results/SYNTHESIS.md` is the PAT-side authority, not this file. → **item 60.**

⚠⚠⚠ **AND IT CHANGES ITEM 58, WHICH IS WHY THE DETOUR WAS WORTH IT.** The shared
`why` block — byte-identical across all six PHP rows — argues R4 admissibility
**from the identity pin**: *"All six patterns pin `identity: unsafe == verus, O3
exact`, so an R4 … must have a byte-identical R5 twin that Verus verifies."*
**THAT ANTECEDENT IS FALSE ON THREE OF SIX PHP ROWS.** It is PAT-side
boilerplate carried into a programme where it does not hold. ▶ **So an R4
candidate on `ph45` need NOT be byte-identical to its R5 twin** — `ph45`'s R4
search is **wider** than `ph29`'s, and F77's method (hunt a spelling whose Verus
twin compiles byte-identically) is **not the binding constraint there**. The
binding constraint is only that the candidate **verify**. → **item 61.**

### F80 — ⭐⭐⭐ ROW 6, THE **FIRST TYPE ROW**, AND **gcc WARNS WHERE rustc IS SILENT** — ONLY THE PROVER REFUSES

`TASK_PHP_036`. **`patterns-php/ph45-htmlent-cache-int/`.** ✅ **Manager-verified
from `results-php/gate/`**: `verdict PASS-WITH-BLOCKED-ROWS`, `failures []`,
`complete_run true`. ⚠ **Not bare `PASS`** — one blocked row, `verus.rs`'s
`ent_table` trusted item has no verified twin and **cannot**, justified in
`spec.md`; `p01`, `p35` and `ph00-smoke` carry the same verdict. Brackets
**`66/0`** and **`14/0`** — the predicted figure, since a new row adds **two**
measure records. Verus **41/0**, **43/0** with twins.

⚠⚠⚠ **THE LADDER RESULT CONTRADICTS THE BRIEF, AND I WROTE THE BRIEF.**
`TASK_PHP_036.md` §1 and `_034` §6.8 both asserted *"safe Rust cannot store a
pointer in an `i32` at all"*. **Measured false, and I re-verified it
independently** (`.temp/mgr171/`):

```
rustc -D warnings -O          ZERO diagnostics      0x56016e08bd60 -> 0x6e08bd60 -> wild ptr
gcc  -std=c99 -Wall -Wextra   WARNS, once per cast site   (2 in my probe; 4 on the kernel)
Verus                         REFUSES, and names both cast sites
```

`(&x[0] as *const u8) as i32` is **ordinary safe Rust** — no `unsafe` block
anywhere — it truncates, and the cast back yields a wild pointer. ⭐⭐⭐ **So on
this defect class the C compiler catches what the Rust compiler misses, and
ONLY THE PROVER CATCHES IT.** And **bug #30573 IS that gcc warning** — the
upstream "compiler warning" commit is the fix (F75).

▶ **Consequently all four Rust rungs carry R1's OWN idiom, not R1h's, and are
safe anyway.** What safe Rust refuses is **only the DEREFERENCE** (`error[E0133]`,
and only at O2 in this row's shape): **it prevents the wild WRITE, not the wild
VALUE.** ⭐⭐ **That is F71's shape on a second axis, so it is now TWICE** — safe
Rust turns the defect into a **wrong answer**, not a panic.

⚠ **The upstream fix is 68,613 `Ir` CHEAPER than the defect** — a sign-extending
load removed — **which A1 reports as `0.00 %`.** ⚠ R4 endpoint **unsearched**:
the **third** row owing that debt → open item 58.

⚠ **Tier shipped `narrowed` per the manager's §2.2 call, with the
counter-argument written INTO `spec.md`** — the engineer's objection is that the
`place` word *"has no pre-image in PHP at all"*, and it flags this as the call it
most wants attacked. ▶ **I am not overruling it and it stays open.**

⚠ Found and reported-not-pursued, and it is the engineer's own: a **signed
overflow at `mbfilter_htmlent.c:193`, in the row's own function**, untraced to
any fix → open item 59.

### F81 — ⚠⚠ THE CATALOGUE'S PROPOSED ORACLE HAS NOW MEASURED **NOTHING** ON TWO ROWS OUT OF TWO TESTED — IT IS A RULE, NOT A COINCIDENCE

* `ph64` (F66): the catalogue's `u64` is bit-identical between R1 and R1h.
* `ph45` (F80): the same, **32 of 32 cells**.

⭐ **Two for two.** ▶ **A catalogue `▸ benign` / oracle line is a PROPOSAL and
must be TESTED before a build task commits to it** — both times a real,
non-fatal, deterministic replacement existed and had to be derived from scratch.
⚠ And on `ph45` the replacement's *number* did not transfer either: `_034`
predicted `&amp;` → **674**, `_036` re-derived **65**. **The mechanism
transferred; the number did not** — and the engineer re-derived rather than
transcribing, which is the only reason it was caught.

⚠⚠ **`ph45`'s own `▸ benign` line was worse than useless — it was
UNREACHABLE**, and that is already corrected in `CATALOGUE.md` from F75's hunt.

### F77 — ⭐⭐⭐ `ph29`'s R4 ENDPOINT **MOVES** — THE FIRST ROW IN EITHER PROGRAMME, AND A COUNTEREXAMPLE TO A PAT RULE'S **PREMISE**

`TASK_PHP_035`. ✅ **Manager-verified from `results-php/gate/` and
`controls/spellings.json`, not from the report**: `verdict PASS`, `failures []`,
`controls_json {"spellings.json": "FRESH"}`, `verus_checked true`,
`problems []`, `identity_checked "verifies AND byte-identical kernel at
O3/isolated"`, `r4_endpoint_degenerate **false**`. Brackets `66/0` + `12/0`.

**`r4_fold_iter` has a Verus twin that verifies — `10 verified, 0 errors`, the
shipped rung's own count — with NO `assume`, NO new trusted item and NO
`is not supported`, compiling to a byte-identical kernel (209 insn,
`d71669d3c0e6`, exec == twin).** ⭐ **So `ph29`'s R4 side was UNSEARCHED**, and
`ph07`'s and `ph16`'s degenerate R4s are not the general case.

**A1 — `Ir`/call, `small.bin`, named per F74:**

| | |
|---|---|
| `fixed-R4 bound` `R3ship − R4ship` | **−6.06 %** |
| R3-side span, cheapest→dearest in contract | **−6.06 % .. +5.08 %** |
| `r4_fold_iter` | **−5.63 %**, admissible **and cheaper** |
| `r4_fold_slice` | byte-identical tie (fingerprint == `v0_shipped`'s) |
| `r4_head_array` | **out of contract** — `is not supported` |

⚠⚠ **COUNTEREXAMPLE TO `.memory/02-bench-rules.md` REASON 2's PREMISE** — *"the
R4 side is chained to the prover … so it usually cannot move."* ✅ **The RULE —
never re-ship a rung for a cheaper spelling — is untouched and VINDICATED**: a
cost-selected R4 would have shrunk this row's published gap by **5.63 pp**.
⚠ **That is a PAT-side memory and is NOT edited from here. Reported, for
routing.**

⚠⚠ **`ph29` IS NOT `ph16`'s F67 MECHANISM — F67 STAYS n = 1.** F67 is *two rungs
cheapest under DIFFERENT spellings, with a degenerate R4*; here the **same**
spelling is cheapest on both sides and R4 is not degenerate. ⭐ **The mirror is
symmetric** — R4's fold in R3 gives −0.38 %, R3's in R4 gives −5.63 % — so
**neither rung's `unsafe`-ness contributes measurably to this row's gap.**

⚠ **R4 searched, NOT exhausted** — four spellings. The honest claim is *"an
admissible cheaper R4 exists"*, never *"this is the cheapest"*. ⚠ And the unroll
factor is an **LLVM heuristic**: every number here is about
`rustc 1.97.1 / LLVM 22.1.6`.

### F78 — ⭐⭐ *"CLOSES, NO RESIDUE"* WAS AN **ARITHMETIC IDENTITY**, AND THE FALSIFICATION INSTRUCTION IS WHAT CAUGHT IT

`TASK_PHP_035` was told to **try to break** `TASK_PHP_033` §4.1 rather than build
on it, because *"closes to the digit with no residue"* was **too clean** and
too-clean is the only warning F52 gives. It did:

> ⚠⚠ **The netting is an identity of the class grouping — it holds for ANY input
> pair, INCLUDING a false mechanism**, demonstrated on **four synthetic cases**.
> A sum that is constructed to net cannot also be evidence that it nets.

✅ **The unroll mechanism itself SURVIVES** — two controlled swaps agree to
**0.875 %** — but the disassembly attribution is **2–3 % short**, invisible
precisely because the residual class absorbed it. ▶ **§4.1's *"91.1 % of the
gap"* should read **93.0 %**.**

⭐ **This is the first time an instruction to falsify a prior task's headline has
paid off in this programme**, and the thing it caught was not an arithmetic
error but a **category error about what the arithmetic showed**.

### F79 — ⚠⚠ TWO REAL DEFECTS IN CONTROL MACHINERY, FOUND BY ITS OWN NEGATIVES, AND ONE IS **LATENT IN `ph16`**

`TASK_PHP_035`'s §H suite is **75 cases — 44 must-FIRE, 31 must-NOT-fire, all
pass** (`ph16`'s bar was 54). **Two of them found real defects in machinery the
file had inherited:**

1. ⭐⭐ **`kernel_fingerprint` returned `(0, 'd41d8cd98f00')` — the md5 of the
   EMPTY STRING — for a binary that does not exist**, because `disasm` ignores
   `objdump`'s return code. ⚠⚠ **So two missing binaries compare EQUAL, on the
   one function in the file whose entire job is to decide *byte-identical*.**
2. ⭐ **`disasm`'s needle is a bare substring**, so any symbol whose mangled name
   merely *contains* `kernel` is folded into the digest — measured: a crate
   named `nokernel` has a `main` mangling to `…_8nokernel4main`, and the loose
   reading fingerprints it. `harness/measure.py::_sum_rows` does **not** have
   this hole; it matches on the function field.

✅ Both guarded in `ph29`'s copy. ⚠⚠ **`patterns-php/ph16-fdset-index/controls/spellings.py`
IS NOT EDITED AND BOTH ARE LATENT THERE** → **open item 57**.

⚠ **And one of the suite's own must-fire cases fired for the WRONG REASON on its
first run** — the "false postcondition" Verus negative returned the right
verdict off `error: expected curly braces`, because `ensures` was written before
`requires` and Verus would not parse it. Fixed, plus a case asserting the output
really carries a `verification results::` line. ⭐ ***A must-fire case that fires
for the wrong reason is worth nothing*** — F52 inside the file that exists to
hunt F52.

### F74 — ⭐⭐⭐ ITEM 52 IS SETTLED **BY A NULL CONTROL THE PROJECT ALREADY SHIPS**, AND THE ANSWER IS FAMILY A

Manager, `.temp/mgr170/NOTES.md` §1a–§1k. Three probes, each `--selftest` PASS:
`.tasks-php/probes/spread_stat.py` · `.tasks-php/probes/callee_share.py` · `.tasks-php/probes/null_control.py`. ⚠ **UNREVIEWED**
(rule 9).

**There are not two statistics, there are SIX in TWO FAMILIES**, and **three are
in use across five published headlines**:

| family | source | counts |
|---|---|---|
| **A** kernel-exclusive | `results-php/<row>.json` → `cells[].ir[inp].kernel_exclusive_ir` | instructions **inside the kernel symbol only** — callees land in **no column** |
| **B** whole-program marginal | `results-php/gate/<row>.json` → `marginal_ir_per_call` | a **slope**, symbol-independent, **charges every callee** |

`ph03`/`ph16`/`ph29` publish **A1**; **`ph64` publishes B1**; **`ph07` publishes
A3** (per window byte) — a figure matching **none** of the 16 computable
(family × band × input) values for its own row, chased to
`controls/spellings.json .variants[0].pct_vs_r4ship`. ⚠ **The START HERE box
mixed A1 and B1 and was FAITHFUL in doing so — the rows themselves disagree.**

⭐⭐⭐ **THE DECIDER WAS ALREADY IN THE TREE.** `identity: unsafe == verus, O3
exact` pins R4 and R5 **byte-identical**, so **`verus − unsafe` has a known true
value of exactly 0** — a null control on every row, which nobody had read as one:

> ⚠⚠⚠ **CORRECTED IN PLACE TWICE — BY F82 (the premise) AND BY F83 (the
> mechanism). READ BOTH BEFORE QUOTING ANYTHING BELOW.** ⭐⭐ **F83 is the one
> that matters: the nonzero readings below are REAL WORK, not noise** — family C
> (`kernel` inclusive `Ir`, an independent method) reproduces B's `+266.000` as
> `+265.924` on `ph03/small` and matches it **exactly** on `large`. **B's defect
> is ATTRIBUTION, not noise**, and the advice below survives on a better reason.
>
> ⚠⚠⚠ **AND THE SENTENCE ABOVE IS THE PREMISE, WHICH WAS NEVER CHECKED PER
> ROW.** `identity` is `exact` at O3 on only **4 of 7 PHP** and
> **28 of 33 PAT** rows. ✅ **Every number in this section survives** — the right
> predicate is `Δnopad == 0`, not the level, and under it **all 33 PAT rows are
> true nulls**; `ph03` really is `exact`. ⚠ But **`ph45` and `ph64` are NOT nulls
> at all** and were counted as such below. ⭐⭐ **And a null control is ONE-SIDED:
> a statistic hard-wired to 0 would ace every null here. F82 supplies the
> sensitivity half this section argued without.** Read F82 before quoting the
> block below.

```
verus - unsafe        family A (kx)        family B (marginal)
6 PHP rows          0.000 % everywhere    up to +3.652 % (ph03/small)
33 PAT rows         0.000 % everywhere    up to +5.010 % (p25-realloc-growth/large)
```

⚠⚠ **ON `ph03`/`small.bin` FAMILY B's NULL (3.65 pp) EXCEEDS THE EFFECT B IS
BEING USED TO MEASURE** — B reports *"unsafe is 3.12 % faster than gcc C"* on
that exact cell. **A statistic cannot be the headline for a comparison it cannot
resolve.**

⭐ **Cross-checked against the frozen harness, to the digit**: `check.py`
documents this null as *"p25 … +269.52"* in **absolute `Ir`**; measured here
independently, `p25` O3/iso/large is `5379.39 → 5648.91`, **+269.52**, = **+5.010 %**.
⭐⭐ **And that reframing is the contribution, not the number**: the harness
records the null in a unit where it reads as negligible, while **every published
claim in both programmes is a percentage**, where the same quantity is larger
than most published effects.

⚠⚠⚠ **THE RULE AS FIRST PUBLISHED IS REFUTED. `TASK_PHP_036` BROKE IT ON THE
VERY NEXT ROW, AND I HAD ALREADY PUT IT INTO TWO TASK FILES.** Read the
correction below before quoting anything in this finding.

**What I published:** *"A is the headline only where the two compared cells have
comparable callee share"* — `inside_share = (kx/n_iters) / marginal`; a 310-
comparison sweep found **31 sign flips, every one with `|Δinside_share| > 0.02`
and NOT ONE below it** (medians: flips 0.146 / 20.68 pp, non-flips 0.009 /
1.03 pp).

⚠⚠ **What `ph45` does to it.** Re-run over **366** comparisons, the same probe
now prints its own refutation — ***"flips with Δshare ≤ 0.02: 6 ⚠⚠ THESE REFUTE
THE MECHANISM"*** — and **all six are `ph45`**:

```
ph45 small  safe_tuned vs unsafe    A +0.37 %   B -3.01 %   Δshare 0.003   ⚠⚠
ph45 small  safe_tuned vs verus     A +0.40 %   B -3.19 %   Δshare 0.004
ph45 small  safe_naive vs safe_tuned A +0.00 %  B +23.37 %  Δshare 0.019
      … and the same three on large.bin
```

▶ **THE CONDITION PASSES AND A1 IS STILL WRONG.** `_036` found this and said so
in exactly those terms.

⭐⭐ **WHY, and the repair is one word: ABSOLUTE, not only RELATIVE.**
`ph45`'s `inside_share` is **0.055 – 0.094** — the most extreme in the corpus by
a factor of seven. When family A sees **9 %** of a cell, the **91 %** it cannot
see carries the whole effect **even when both cells miss the same proportion**.
Asymmetry is what matters when the shares are high; when both are low, A is
measuring a small and unrepresentative slice and may disagree arbitrarily.

▶ ⭐ **THE CORRECTED RULE — TWO CONDITIONS, AND THE CONJUNCTION IS MEASURED
CLEAN:**

> **(i) `min(inside_share)` over the two cells must be HIGH — A must actually
> SEE both — AND (ii) `|Δinside_share| ≤ 0.02`.**
> Under both: **151 of 366 comparisons, ZERO sign flips.** Dropping (ii) is my
> original error; dropping (i) admits the six `ph45` cases.

⚠ **The threshold in (i) is NOT tuned and the corpus cannot pin it**: `> 0.3`,
`> 0.5` and `> 0.6` all give **0 flips** at 145–151 comparisons. Read it as
*"A sees most of both cells"*; **six rows cannot say more.** ⭐ Medians tell the
same story from the other side: `min(inside_share)` is **0.678** on flips and
**0.923** on non-flips.

⭐⭐⭐ **AND THE LESSON IS ABOUT ME, NOT ABOUT THE STATISTIC.** I published a
mechanism from **six rows**, wrote a *"refutation test PASSES"* line into the
probe, and **put the rule into `TASK_PHP_035.md` §3 and `TASK_PHP_036.md` §3
before any row had tried to break it.** The seventh row broke it. ⚠ **The probe
is what saved this** — it recomputes from the tree on every run and printed
`⚠⚠ THESE REFUTE THE MECHANISM` itself, unprompted. *A rule whose checker is a
committed script that re-derives it gets corrected; a rule written only into
prose does not.*

**With the corrected rule in hand, the original observations still hold:**

* **R3 vs R4** (`fixed-R4 bound`): Δshare ~0.003–0.014 → **never flips**. ⭐ That
  is **why** the spread table is robust — a mechanism, not luck.
* **C vs Rust on `ph29`/`ph64`**: Δshare 0.21–0.27 → **29 of the 31 flips**, and
  magnitudes moving **2.4×** and **5.2×**.
* ⚠⚠ **`ph64` R2 vs R3 flips too**: A says `safe_naive` is **2.81 % cheaper**
  than `safe_tuned`; B says **32.68 % dearer**. ▶ **F71's starred `R3 − R2 =
  −24.63 %` is family B and it STANDS** — `safe_naive`'s `inside_share` is
  **0.721** against `safe_tuned`'s **0.929**, so the naive rung really does
  allocate more and **A is simply blind to it** — **but it must be LABELLED
  family B**, beside a `fixed-R4 bound` that is family A.

⚠⚠⚠ **THE RULE HAS A LIMIT `TASK_PHP_035` FOUND ONE ROUND LATER — DO NOT QUOTE
IT PAST THAT LIMIT.** `ph29`'s `r3_copy_loop` is **`+5.08 %` on A1 and
`−0.99 %` on the slope: the two DISAGREE ON SIGN**, on an in-contract R3
variant. ⚠ **That is a disagreement WITHIN family A** — per call (`A1`) against
per window byte (`A3`) — **not the A-vs-B disagreement measured above** — and
its driver is the **FIXED PER-CALL COST**: `r3_copy_loop`'s is **105.35**
against `R4ship`'s **45.19**. **Callee share does not enter it.** ▶ So
**`|Δinside_share| ≤ 0.02` predicts A-vs-B agreement and says NOTHING about
A1-vs-A3.** ⭐ A1 stays the headline — nothing measured contradicts that — but
*"the statistics agree unless callee share differs"* is **false as a general
sentence**, and the **sub-statistic axis is now the sharper open half of item
52**.

⚠ **`ph64`'s box figure is `+17.47` under A1**, not `+17.08`. ⚠ **Nothing here
needs a re-gate, a re-measure or a `harness/` edit** — it is entirely which
committed number a document quotes. ⚠⚠ **The PAT programme has it too, on 33
rows, and it is NOT acted on**: PAT is frozen, `.web/` is a concurrent session,
`results/SYNTHESIS.md` is the authority there, **and PAT publishes in A, whose
null is zero** — so no PAT figure is in question.

### F75 — ⭐⭐⭐ `ph45`'s HUNT: `crashes_pristine_5_0_0` IS **BOOKKEEPING**, AND THE ROW NEEDS ITS FORCING MECHANISM FOR THE **BENIGN** CASE

`TASK_PHP_034`, investigation only. ✅ **Manager-verified on four counts.**

**(a) The `False` is a build artefact, not a fact about the defect.** The
*"pristine"* binary was configured **`--disable-all`**, so
`mb_convert_encoding()` does not exist in it and `CRASH-123.php` dies with
*"Fatal error: Call to undefined function"* **before any C in
`mbfilter_htmlent.c` runs.** ✅ Verified three ways: the field equals
`stock-run.json`'s `hard_crash` on **142/142** rows; **all 15 `build: fullext`
rows are `False`** (15/15, counted in `index.csv`); and the two logs say it
outright — ⚠ **and they are named counter-intuitively**: `CRASH-123.asan.log`
carries the *fatal error*, `CRASH-123.fullext.log` carries the real
**`SEGV on WRITE` at `mbfilter_htmlent.c:183`**, the exact cited line, 3/3.
⚠ `PROTOCOL_PHP.md` §B1.1's **conclusion survives but its MECHANISM does not** —
the size-class cache explains none of the 15 `fullext` rows.

**(b) ⭐⭐ The design problem is the OPPOSITE of the one predicted.** With the
faithful `emalloc_shim.h` the R1 rung **SEGVs 60/60 — including on a benign
input containing no `&`** — because the wild free at `:169` is **unconditional**;
R1h is **0/60**. ▶ **So there is no benign corpus at the default allocator
placement, stage 2's checksum agreement is unreachable, and the forcing
mechanism is needed to make the BENIGN case work, not the adversarial one.**

**(c) R1h is clean despite its subject.** `e8901dc17087` reads *"Fix bug #30573
(compiler warning due to invalid type cast)"* — F45's shape — but ✅
**manager-verified from the patch itself: it ADDS `void *opaque;` to the struct**
and moves all six `filter->cache` uses onto it, **both cast-backs included**.
`patch -p1` on the pristine tarball: **rc=0, no fuzz, no offset.**
⭐ **The two-file footprint was the right signal and the subject was the wrong
one** — a warning-silencing change casts at the *use* site; changing the
*declaration* is what removes the defect.

**(d) ⚠⚠ THREE OF MY PREMISES WERE WRONG**, the same error rate `_031` found:

* *"five lines … the whole mechanism"* → **15 tarball lines.** ✅ It misses
  **`:249`**, a **SECOND cast-back** in `mbfl_filt_conv_html_dec_flush` —
  manager-verified against the pinned tarball — and nine of ten dereferences.
* *"the trigger depends on where the allocator happens to put the block"* →
  **wrong twice**: 40/40 samples truncate, and it is **not a trigger condition
  at all**.
* *"sidesteps `zval.h` entirely"* → true of the defect file, **incomplete for the
  row**; the conclusion survives because the two spans needed are zval-free.

✅ Confirmed: the catalogue's off-by-one over `ADJUDICATION_001.md`; and *"the
only row in 166 with its own invariant"* is **TRUE and now ATTRIBUTED** —
`paper/invariants-166.json`, 20 distinct ids over 166 cases, **three obligations
mapping one-to-one onto the row's three cited lines.**

⚠ **The catalogue's oracle measures NOTHING** — R1 ≡ R1h bit-identically in the
lossless regime, **`ph64`'s lesson repeating on a second row**. A non-fatal,
deterministic, `u64`-visible replacement **is** measured: two filters 2³² apart
alias under truncation, and R1 decodes `&amp;` to **674** where R1h gives **38**.
⚠ **Tier `narrowed`, not the catalogue's `verbatim`** — flagged by the engineer
as a judgement call it wants attacked, counter-argument written out.
⚠ Adjacent and **not** pursued: `mbfilter_htmlent.c:123` carries a **separate,
uncatalogued** stack OOB write (`tmp + sizeof(tmp)` on an `int tmp[64]`), which
is why the row must not lift the encode half.

### F66 — ⭐⭐⭐ `ph64`'s R1h: THE CLEANEST BACKPORT YET, THE REPAIR IS AT A **THIRD** SITE, AND THE CATALOGUE'S ORACLE **MEASURES NOTHING**

`TASK_PHP_031`, a hunt-and-prep task dispatched **because** the box's *"8-line,
ONE id"* recommendation had an unhunted R1h — and `ph07` lost a whole task to
that shape.

**R1h = `562f886ecb14`**, Antony Dovgal, 2007-04-10, with **three artefacts
inside the commit**: bug #41037 in the subject, the **NEWS** line it adds, and
**`bug41037.phpt`** (23 lines). The bracket is a **DERIVATION, not a tag
selection** — the `5.2.1 → 5.2.2` diff of the function **is** the commit's hunk,
line for line — which is §C's *"scan tags until one suits"* trap avoided rather
than merely declared. ✅ **Manager-verified independently**: 5.0.0's
`user_tick_function_compare` at `basic_functions.c:2146` is **byte-identical to
the patch's pre-image**, and the disclosed `fuzz 1` is **one trailing context
line in the ADJACENT declaration** (`php_call_shutdown_functions(void)` vs
`(TSRMLS_D)`), outside the patched function. **A precise disclosure that checks
out.**

⭐⭐ **The repair is at a THIRD function** — neither the loop (`zend_llist.c:190`,
a read-after-free of a link pointer) nor the callee (`basic_functions.c:2135`, a
write-after-free) — and it works by making the **free unreachable**:

```c
+	if (ret && tick_fe1->calling) {
+		php_error_docref(NULL TSRMLS_CC, E_WARNING, "Unable to delete tick function executed at the moment");
 		return 0;
```

✅ **And that settles ONE ROW vs TWO — against the manager's stated lean, on the
stronger grounds.** The predicate `tick_fe1->calling` **is the callee's own state
variable**, so an L-only row has **no predicate, hence no R1h, hence breaks §C**.
⚠ `_031` records plainly that **§G's letter would say "two rows"** and why it is
not deciding there; **that tension stays on the record.** ⭐ Also proven: the
8-line `zend_llist_apply` is **byte-identical 5.0.0 → master, 21 years** — so
*"is the defect's own function ever repaired?"* is **NO**, measured.

⚠⚠⚠ **AND `CATALOGUE.md`'s PROPOSED `u64` ORACLE FOR THIS ROW MEASURES
NOTHING.** Request 39 → `REAL_SIZE` 40 → `cache_index 5 < 11` → cached, **payload
untouched**, so on the corpus's own trigger with no reuse **the visit fold is
BIT-IDENTICAL R1 vs R1h.** **This is F46's class** (*the mechanism sentences
hold; the `▸ trigger` lines do not*) **on the first temporal row, in exactly the
half a build task runs.** Two working oracles supplied instead
(`php_shim_tally()` + `l->count`; and one same-class `emalloc` in the callback,
where **R1 SIGSEGVs at all three `DEL_LLIST_ELEMENT` arms and R1h is clean**),
over 8 scenarios × 2 rungs on gcc/clang × `-O0`/`-O3`, forked so SEGV is an
outcome, with 3 must-NOT-fire. ⭐ **R1h changes nothing on the benign domain**, so
**stage 7h should pass first try** — a falsifiable prediction, and the thing that
cost `ph07` its rebuild.

⚠ **Fidelity is itself a finding**: faithful shim + ASan → `SEGV`; plain malloc +
ASan → `heap-use-after-free`, **WRITE of size 4, frame #0 at the callee**. **So
the corpus's `asan_kind` cannot have come from a pristine cached allocator.**

⚠ **An incompleteness candidate, INFERENCE and NOT MEASURED**: R1h's own refusal
path runs `php_error_docref(E_WARNING)` → … → `zend_error`'s **user-handler**
arm, i.e. **arbitrary userland from inside `zend_llist_del_element`'s walk**,
which holds `current`/`next`. Visible in the hunk above, and **master later
upgraded it to `zend_throw_error`, which cannot run userland.** If measured and
confirmed, `ph64` is the **fifth of five** built rows whose upstream fix is
incomplete or wrong. **Mechanism OPEN.**

⚠ **Three manager premises corrected**: the *"drift"* explanation (wrong
mechanism — the commit patches a different **function**), the chain length
(**five** frames, call at `:2143` not `:2139`), and *"8 lines, no PHP
machinery"* — **the faithful chain is ~140 lines**, which its own least-sure
section predicted. ⭐ **It also disclosed two probe bugs of its own and an F35
instance in its own tool**, each caught only by an expectation **declared before
the run**.

### F65 — ⭐⭐ ROW 4 (`ph29`): THE SHIM IS FAITHFUL, AND **NEITHER STAGE OF THE UPSTREAM FIX REMOVES THE DEFECT**

`TASK_PHP_027`, gate green and re-run by the manager (`check.py: PASS`, contract
`28a92facffb3`). Bracket `66/0` and **`10/0`** — ⚠ **a row adds TWO measurement
records**; the engineer predicted 9 and said so.

✅ **The reason this row preceded the temporal axis is discharged.** It is one of
two rows where the `_emalloc` truncation is load-bearing, so it **cannot pass**
unless the allocator shim is faithful. **§6.1's stopping condition was NOT
reached**: the behaviour the row needs is **one store** (`zend_alloc.c:129`/`:135`),
transcribed verbatim, and `controls/allocator.py --audit` re-derives those lines
**from the tarball, not from the shim** — 18 cells, both directions, PASS.
**F6's warning did not fire, and 31 temporal rows may now lean on it.**

⚠⚠ **§2 ANSWERED, AND THE ANSWER IS THE FINDING. STAGE 1 AND STAGE 2 ARE NOT THE
SAME RUNG.** R1h ships stage 1 (`445daac3ab1a`). Stage 2 (`6ac8ffdfea10`, found
by grepping **all 82 commits** on that file 2004–2009) buys **exactly two values
of `to_read`** over stage 1 and removes **ZERO** truncation faults. ⭐⭐ **Neither
removes the row's defect**, and the guard is **over-broad** — it refuses
`to_read == 0`, which was never a fault. **That is `PROTOCOL_PHP.md` §C's *"an
upstream fix is not automatically correct"* measured rather than asserted, and it
is the second row to show it after `ph07`.**

⭐ **MY OWN §3 WAS HALF WRONG AND THE ROW SAYS SO.** I wrote that under plain
`malloc` the defect vanishes because `malloc(2^63)` fails. **There are two
behaviours**: at the row's own UB-free trigger `4294967295`, plain `malloc`
**succeeds** with 4 GiB and the write is **in bounds**. Only the negative values
reach `exit(1)`.

⭐⭐ **PHP 5.0.0's SIZE-CLASS CACHE DEFEATS `-D_FORTIFY_SOURCE=3`** — zero `_chk`
symbols in **all 8 configs**, with a **must-fire** control: delete the cache arm
and `__memcpy_chk` appears. **No `#undef` needed, unlike `ph16`** (F56). ⚠ This
is **shim-wide** and affects **every future allocating row**.

⚠ **`R3 − R4` is −6.1 %/−6.4 %, so no figure here is a `fixed-R4 bound`** — the
same position as `ph16`. **THREE OF FOUR ROWS now owe `controls/spellings.py`**;
`TASK_PHP_028`'s scope grows again.
⚠ Nine declarations were wrong and the gate caught four. **Worst:
`idiom.forbidden[0]` backticked the expression it protects — while its own last
sentence warned against exactly that.**

### F64 — ⭐⭐ THE **PRE-IMAGE SCREEN**: A PROOF OF EXCLUSION FOR R1h, AND TWO ROWS SETTLED BY IT

`TASK_PHP_030`, tool promoted to `.tasks-php/preimage_screen.py`. Born from
`TASK_PHP_029` refuting `ph21`'s `fix_commit` **from the commit's own bytes** —
its 2015 pre-image already reads `safe_emalloc(input_len, mult, 1)` where 5.0.0
reads `emalloc(result_len + 1)`, so **it cannot be repairing the 5.0.0 line.**
Generalised:

> **If a `fix_commit`'s patch touches the defect's file but its PRE-IMAGE for
> that file does not contain the 5.0.0 text, that commit is not the repair.**

⭐ **This EXCLUDES; the date and id-spread selectors only RANK.** Network-free.

```
170 records:  43 NOT-THE-REPAIR (⚠ only 26 with positive evidence -- see below)
             106 CANDIDATE  ·  18 INAPPLICABLE  ·  2 NO-SPAN  ·  1 NO-SHA
```

⚠⚠⚠ **THIS SAID `33/43` AND THE TOOL SAYS `26/43`. CORRECTED 2026-09-10 BY TWO
INDEPENDENT MEASUREMENTS, AND THE CAUSE OF THE 33 IS UNKNOWN.** The predicate is
**provably the same one** — `decisive == (bracketed or same_function)` holds on
**43 of 43 records, zero mismatches** — so this is not two definitions
disagreeing. The manager recomputed it from the promoted tool's own `decisive`
field (**26**, with `bracketed` 2 / `same_function` 25); `TASK_PHP_031`
**independently reached 17 non-decisive, i.e. 26**, by reading all 17 git hunk
contexts with no knowledge of the field. ⚠ **The manager's first hypothesis —
that the `:0`-sentinel repair moved it — is MEASURED FALSE**: 0 of the 43
exclusions have a chosen `file:line` that moves between the naive and
sentinel-aware readings, and corpus-wide only **2** ids move at all
(`CRASH-112`, `V5C-112`), neither among the 43. **Cite 26. Re-derive before
citing anything else, and do not restore the 33 without an artefact.**
⚠ **Third time this file has carried a figure its own evidence no longer
produces**, which the size box at the top warns about twice.

⚠⚠⚠ **AND `NOT-THE-REPAIR` IS NOT A PROOF OF EXCLUSION FOR 17 OF THE 43 —
`ph64` IS A CONFIRMED FALSE EXCLUSION.** `TASK_PHP_031` §7.1: `562f886ecb14`
**removes no line at either of `ph64`'s cited sites, ever**, because it repairs a
**third function** in the same file — so **no line-level pre-image screen can
find a fix of this shape.** ✅ Confirmed mechanically by the manager:
`defect_file ∈ patch_files` for **17 of 17** non-decisive records, zero
exceptions, so the whole non-decisive population is **same-file /
different-function** — `INAPPLICABLE`'s mechanism one granularity down.
▶ ✅✅ **LANDED AT `TASK_PHP_040` §4 (F95)** — six negatives, `25 + 18 = 43`, 0
partition violations, docstring qualified in the same edit, and the 17 movers
reproduce this census exactly. ⛔ **Plus a soundness defect it exposed in
`same_function`, repaired by the manager.** ▶ **F95.** **The original ask:**
❌ **A manager-proposed extra signal is REFUTED and must not be added**: scoring
a bug-numbered `.phpt` in `patch_files` as evidence of a repair gives
**53 % / 46 % / 45 %** across non-decisive exclusions, decisive exclusions and
candidates — **no discriminating power**, because nearly every commit in that
column *is* a repair. F61's shape.

⚠⚠ **MY TASK'S §1 RULE WAS STRONGER THAN THE EVIDENCE AND
THE AGENT CORRECTED IT.** *"Absent from the pre-image"* has **two** readings: the
tree no longer has the text (**exclusion**), or the **~3-line hunk window never
reached it** (**proves nothing**) — median pre-image behind an exclusion is **14
lines**. It added two line-number-free locators (git's `@@ … @@ <function>` vs
the 5.0.0 enclosing function; 5.0.0-unique anchors bracketing the cited line) and
reports the other **10 as *"does not touch the cited lines"*, not as exclusions.**

✅ **9 for 9 on ground truth.** The four specified cases span **all three
outcomes**, so no constant implementation passes; **N9 adds five the programme
had established BY HAND and which were not used to build it** — `ph03`, `ph29`,
`ph16` **must-NOT-exclude** (the dangerous direction), `ph12`/`ph22` must
exclude. ⭐ `ph03`'s is strongest: `TASK_PHP_013` **applied** that patch and
measured it over 12 600 documents. ✅ Diff parser verified externally: it never
reads `@@ -a,b`'s declared length — **1892 hunks / 476 file sections, 0
mismatches.** ⭐ **It also shipped a false exclusion, found it, and guarded it**
(`ph73`/CRASH-100 — the cell reads `:728 (and 735, 742)` and bare numbers carry
no colon); the repair moved **exactly 2 of 170** verdicts.

⭐⭐ **Two R1h answers landed, each with an upstream artefact:**

```
ph95  db420cb6a141876b2f7d101051fb01934a28071a   bug #78833 -- regression test AND
      NEWS inside the commit, and the guard it adds is `if (currentarg > INT_MAX
      - arg)` immediately before :212, ph95's EXACT mechanism. The corpus column
      865739e5b196 (2025) is EXCLUDED; 6d98fc38b53 repairs :262 only, so the
      catalogue's "neither repairs the other" is now byte-evidenced.
ph22  6d98fc38b53c0ce803bf5cc8de05e2083eb6cd41   INC_OUTPUTPOS's arrival, 5.0.0's
      :247 byte-identical in its pre-image. FIXSURVEY_001 had only a tag bracket.
```

⚠ `ph95`'s **completeness** is flagged INFERENCE, not measured — do not upgrade it.
⚠⚠ **`CANDIDATE` means only *"could not exclude"*, and 100 of the 106 have never
been looked at by anyone. It is not a verdict.**

⚠ **I checked one limb and it was wrong.** `_030` reported `ph04`'s `url.c:132`
as *"a comment terminator, probably an off-by-one in the corpus"*. **131 is the
terminator; 132 is `if (*(e + 5) == ':')`** — the read five bytes past `e` that
the row's own `fix_commit` is titled after (*"bug #70480, `php_url_parse_ex()`
buffer overflow read"*). ⭐ **The corpus cell is CORRECT.** Landing it unchecked
would have put a false accusation against the corpus into the document whose job
is to be trusted about the corpus.

### F63 — ⚠⚠⚠ ITEM 45's PREMISE WAS WRONG, AND THE CAUSE WAS A `break` IN THE MANAGER'S OWN TOOL

`TASK_PHP_029`. Item 45 says *"`ph73`'s `fix_commit` does not touch `ph73`'s
function"*. **THE COLUMN IS RIGHT.** `ph73` carries **five** corpus ids, **each
with its own `fix_commit`**, and `fixsurvey.py` stopped at the first with a bare
`break` — *"one id per row is enough"*. `3d7b0bab28e7` is the **exact** fix for
**CRASH-052**; the catalogue's cited span is **CRASH-051's**, fixed by
`235e6c0afe1d`. **`CATALOGUE.md:868` lists all five sites and they map 1:1 onto
the five ids. The catalogue was right the whole time and the tool's output was
what looked wrong** — a tool defect that spent a manager's open item.

**Scale: 31 rows carry >1 resolvable id, 99 ids between them, so 68 were never
examined.** Removing the `break` took resolved records **101 → 169** and
**OTHER-FILE 8 → 19** — *eleven more instances of the `ph07` shape*, the very
shape this survey exists to find.

**`ph73`'s five answers, each with an artefact** (do not re-derive):

```
CRASH-051  235e6c0afe1d  5.0.3 -> 5.0.4   bug #30562
CRASH-052  3d7b0bab28e7  5.0.4 -> 5.0.5   regression test in-commit
CRASH-027  d2018ef2c035  5.0.4 -> 5.0.5   bug33116.phpt + NEWS
CRASH-032  30f4d3f9593d  5.1.0 -> 5.2.0   bug38220.phpt + NEWS
CRASH-100  5d804d163ae9  5.2.6 -> 5.2.7   NEWS -- vulnerable FOUR YEARS
```

⚠⚠ **CONSEQUENCE THE MANAGER OWES: `PROTOCOL_PHP.md` §F5's *"`kernel_hardened.c`
= the real `fix_commit`, sha-pinned"* HAS NO SPELLING FOR FIVE** — owed **before**
`ph73`'s build task, and it now applies to **30 rows**, not one.
⭐ **`ph21` settled too**: R1h `a4d2f0430723` (2006-08-10), decided by
`php-5.2.0/NEWS:161` **and** by the 5.1.0→5.2.0 diff of the function being that
hunk **and nothing else** — one commit in the window, so a **derivation, not a
selection**, which is exactly what §C's trap demands.
⚠ **Against my own commit earlier the same day**: *"covers 102/102 rows"* was
true **per ROW** and hid all of this. **Fixing the total-miss case is not fixing
the partial-miss case.**

### F62 — ⚠⚠ THE FIX SURVEY WAS BLIND TO THE CORPUS'S **THIRD ID NAMESPACE**, AND PRINTED A CLEAN BILL THROUGHOUT

Item 47. `fixsurvey.py` indexed `root_cause_id`, `v5c_id`, `input_id`. **22
corpus ids — every one a `V5C` — exist ONLY inside `merged_members`**,
semicolon-separated, in 19 of 166 corpus rows. `ph94` and `ph95` cite such an id
**and nothing else**, hit a bare `continue`, and **never entered the result set**.

⚠⚠ **The failure mode is the finding.** `len(res)` reported **the survivors as
the population**, while the one number that looks like a coverage check —
`unmapped: 0` — **stayed 0**, because `unmapped` counts something else entirely
(rows with *no id on the catalogue line*). **A row nobody could look up and a row
with no id were tracked by two different counters, and only the reassuring one
printed.**

⭐ **Third instance of this blindness**: the manager's own V5C check (caught only
by an absurd printed range), then `coverage.py` when it was promoted out of
scratch, now this. ⚠ **`ph03` — a BUILT row — also cites a merged-only id
(`V5C-116`) and survived only because it carries `CRASH-115` too.** No published
number moves; the margin was accidental.

✅ Fixed, and **§H's must-fire REBUILDS THE BLIND INDEX** rather than re-running
the fixed path — a test of the fixed path alone passes against a no-op patch.
✅ Survey now covers **102/102** rows; `ph36`'s `NO-SHA` is legitimate (its
`fix_commit` is the annotation *"(bison-regeneration; no single commit)"*).
✅ **A second parse defect, found by `_030`**: CRASH-112 (`ph72`) is
`ext/standard/uuencode.c:0|ext/standard/user_filters.c:140` — two files,
`|`-separated, the first carrying the sentinel `:0`, and `split(":")[0]` returned
the sentinel file. **OTHER-FILE 19 → 18**, which now agrees exactly with the
screen's INAPPLICABLE 18.

### F61 — ⚠ THE FIX-COMMIT **DATE** AND **ID-SPREAD** SELECTORS, MEASURED — AND **NEITHER IS PROMOTED**

The manager proposed the fix **date** as *"a cheap, high-signal selector for
F38's later-fix risk"* and **tested it before landing it**. Against **both** rows
whose column is known bad:

```
ph07   cb3cca21b345   2005-12-15   OTHER-FILE, and R1h is a strict SUBSET of it
ph73   3d7b0bab28e7   2005-06-03   right FILE, zero occurrences of the function
```

**Both sit in the most ordinary part of the distribution. Recall ZERO on the only
ground truth there was.** ⭐ **Had it shipped it would have been F58's mistake
repeated exactly** — a selector that *looks* principled, promoted on a shape
argument, carrying no signal for the thing it was named after.

⭐ **What survives is that there are TWO failure modes the programme was
conflating**: (a) **the column is WRONG** — wrong function, wrong file, or a fix
that is **too big** (`ph07`, `ph73`; dates ordinary); (b) **the column is RIGHT
and very LATE** — the defect genuinely survived for years (`ph95`, `ph22`,
`ph21`). ⚠⚠ **(b) is a LADDER problem, not a provenance one**: §C says R1h is
*"the `fix_commit` patch backported"*, and **for a 2025 commit against a 2004
tree that instruction may not have a referent.**

`_029` offers a second, network-free ranking — **id-spread**, 30 of 102 rows.
⚠ **Cross-tab: date 31, id-spread 30, overlap only 10** — nearly orthogonal.
⭐⭐ **Its own recommendation, which the manager accepts, is NEITHER AS A SWEEP**:
hunt R1h at the head of each build task. **F64's screen is why** — a decisive
test makes both rankings largely redundant, and it **finds 12 exclusion rows the
UNION of the two rankings misses.**
✅ One consistency check passed: **zero** rows have a `fix_commit` dated *before*
5.0.0's release, which a corrupt column could easily have produced.

### F60 — ⭐ `ph16` GUARD (c)'s PREMISE, MEASURED — AND THE PROBE WAS WRONG **TWICE**, BOTH TIMES CLEANLY

`ph16`'s R1h carries **three** guards, and (c) — `PHP_SAFE_MAX_FD` — stops
`php_select(max_fd + 1, …)` receiving an `nfds` past `FD_SETSIZE`, which **(b)
alone leaves possible** because `*max_fd = this_fd` sits inside the guarded arm
but is not itself bounded. `controls/fix_scope.py` prices (c) at the **model**
level and **never measures the syscall boundary**. Rule 14 says run the premise.

✅ **Measured** (`.tasks-php/probes/maxfd_probe.c`): the kernel **writes** past a
128-byte `fd_set` for every `nfds > FD_SETSIZE`, first dirty byte at `+0`,
**boundary exactly at `nfds = 1025`** — the first value needing 129 bytes.
**Guard (c) is load-bearing and its premise is now measured rather than argued.**
⚠ Precondition: the process must hold **more than `FD_SETSIZE` descriptors**,
since `core_sys_select()` caps `n` at the fdtable size — **the same precondition
`ph16`'s own defect needs.**

⚠⚠⚠ **AND IT WAS WRONG TWICE, IN F52's SHAPE, AND BOTH VERSIONS RAN CLEAN AND
PRINTED A CONFIDENT FALSE ANSWER.**

- **v1** opened **four** fds and swept `nfds` to 1048576 → **INTACT everywhere**.
  That is the kernel's **fdtable cap** firing long before the buffer. **The setup
  encoded the answer.** I nearly wrote *"the kernel is safe"*.
- **v2** grew the fdtable with `dup()`s of `/dev/zero`, which are **all
  readable**, so the `0xA4` canary was read as *"requested"*, the fds were ready,
  and the kernel **wrote the same bits back**. Bytes it had definitely written
  compared **equal** and printed INTACT. **A second answer-encoding setup, inside
  the probe written to avoid the first.**
- **v3** uses **pipe read-ends** (never ready) and canary `0xFF`, so every byte
  touched must be **cleared**.

⭐ **The lesson is not "be careful": it is that the MUST-FIRE case is the only
thing separating v3 from v1, and v1 would have shipped.**

⚠ **Item 46 adjudicated, and my first answer was wrong about a shipped row.** I
drafted a table claiming `99e290f882c9` has four repairs and `ph16` prices one.
**`ph16` prices TWO** — guards (b) and (c) — **and its `spec.md` had already done
the census I thought I was doing**, recording that the commit patches **four**
fd-set sites of which the catalogue has one, and explicitly declining to
adjudicate. **What is genuinely unpriced is `PHP_SAFE_FD_ISSET` (the READ, at
`streamsfuncs.c:577` and `sockets.c:563`) and the ~20 `poll(2)` conversions.**
§G verdict: **the burden of showing SAME is not discharged** — they share a
**commit**, not a **fix**, and §G1 says a distinct fix is evidence for DIFFERENT.
⭐ **The `FD_ISSET` read is the stronger candidate**, and `ext/sockets/` has
**zero** catalogue rows (F59). ⚠ A fifth cluster is untouched by the commit
entirely: **15 sites in bundled FastCGI** (`.tasks-php/probes/fdset_census.sh`;
47 sites in 11 files total).

### F59 — ⚠⚠ `ext/sockets/` WAS BUILT AND FUZZED AND HAS **ZERO** CORPUS ROWS. MY INNOCENT EXPLANATION IS REFUTED.

`TASK_PHP_026` §5, and I asked for exactly this check: *"if `ext/sockets` was
not in the built configuration, its zero rows are explained innocently."*
✅ **It was.** Verified independently: `--enable-sockets` is in the build's own
`config.nice`, and `sockets.o` is present in the ASan build trees.

| | `sockets.c` | `streamsfuncs.c` |
|---|---:|---:|
| corpus rows (`index.csv`, `c_file_line`) | **0** | **6** |
| catalogue rows | **0** | 6 |

> ⭐ **So this is a finding about the CORPUS's coverage, not the catalogue's.**
> The catalogue faithfully inherited a blind spot it did not create — and
> `99e290f882c9` proves the C in there carries the same defect as a row we built.

⚠⚠ **ONE LIMB OF THE ARGUMENT IS WEAKER THAN IT READS, AND I CHECKED IT.**
`_026` also cites *"0 of 2534 ASan logs name it"*. True — **but 0 of 2534 name
`streamsfuncs.c` either**, and that file has six rows. **The ASan census and the
corpus rows are largely disjoint** (F9 said so first: *not one spatial ASan
report is in the code the spatial axis mines*), so **the log count is not
evidence about `sockets.c` specifically.** ✅ **The corpus-row count is, and it
is the limb that carries the finding.**

### F58 — ⭐⭐ THE CENSUS CHANNEL IS REAL: **12 UNCATALOGUED SIBLING SITES FROM 6 OF 12 FIX COMMITS** — AND THE SELECTOR THAT FOUND THEM CARRIES NO SIGNAL

`TASK_PHP_026`, testing F50. **My 5–15 band is hit and the channel is not a
one-instance curiosity.** `ph16` **3** (my n = 1 confirmed byte-exact) · `ph73`
**3+1** · `ph23` **2** · `ph76` **2** · `ph39` **1** · `ph26` **1**.

⚠⚠⚠ **BUT THE ≥ 5-FILE SELECTOR THAT PRODUCED THE LIST IS WORTHLESS.**
Measured: files ≥ 8 → **1.00** siblings/row; files == 5 → **1.00**. **The two
biggest commits (17 files, 16 files) yielded nothing.** ⭐ **What actually
predicts a census is a NAMED WRAPPER in the repair** — `PHP_SAFE_FD_SET`,
`MAKE_REAL_ZVAL_PTR`, `zend_reset_all_cv`. **All three top rows had one, and it
is one grep per patch.** So `FIXSURVEY_001.md`'s *"12 fixes touch ≥ 5 files"*
heading was a **liability read** of a number that is **also not a lead** — my F50
promoted the wrong half of it.

⚠ **The message triage is a good POSITIVE predictor and a bad NEGATIVE one.**
`SWEEP` → yielded **3/3, no false positives**; but **3 of 12 were false
negatives, worth 5 of the 12 sites (42 %).** **Drop it as a filter** — it was
worth running once, as a control, and that is all.
⭐ **`ph26` kills my *"REWRITE yields nothing"*.** `main/snprintf.c:296`'s
`ap_php_cvt` is a line-for-line clone of `ph26`'s defect — same `NDIG 80`, same
negative-`mvl` `memmove` — deleted by the same commit, and **`snprintf.c` has
zero catalogue mentions.** ⚠ The variation is a **stack** buffer rather than
static BSS, **which is the oracle `ph26`'s own risk note says it lacks.**

⚠⚠ **AND THE ANCHORING CONTROL FAILED — MY FAULT, NOT THE AGENT'S.** The task
said *"do not read §4 until your triage is written"*; **my launch prompt said
*"read it in full"*.** The agent disclosed the contradiction up front and
**correctly reports its triage as anchored.** ⭐ **The fix is structural: a
prediction cannot be fenced inside a file the bootstrap says to read whole — put
it in a separate file.** ✅ It also disclosed that its extractor leaked the
diffstat on 4 of 12 rows, ⚠ **and noted that the row which REFUTES its triage is
one of the 8 clean ones**, so the leak did not manufacture the headline.

✅ **It did not adjudicate**, as instructed — §G1 is quoted at the head of its
findings. ⭐ **Its best clean negative is the one it expected to get wrong**:
three of `ph73`'s five `zval tmp_member` sites use the **byte-identical idiom**
and **never publish to userland** — *the idiom is not the defect, the
publication is*, and an idiom grep would have produced three false candidates.

### F57 — ⭐⭐⭐ ROW 3, THE FIRST OUTSIDE `S1`: THE SANITIZER IS BLIND, MIRI IS NOT, AND THE ROW'S ORACLE WAS ALREADY IN UPSTREAM'S OWN FRAME

`TASK_PHP_025`. `ph16-fdset-index`, gate **PASS**, `provenance --all` 4 rows
0 FAILED, brackets **66/0** (PAT untouched) and **8/0**. **Six controls, each
with a must-fire AND a must-not-fire case** — §H, landed the same morning.

⭐⭐ **THE CANARY I DESIGNED WAS NEVER NEEDED, AND THE REASON IS BETTER THAN THE
CANARY.** I measured that a `volatile` canary catches what ASan misses and told
the task to build on it. **`stream_select`'s own `wfds` and `efds` ARE the
witnesses**: `PHP_FUNCTION(stream_select)` declares `fd_set rfds, wfds, efds;`
at `:658` and reads **all three** back at `:706`, so an over-index into `rfds`
lands in a live object *the function's own result depends on*. ⚠ **`spec.md`'s
`forbidden[2]` now BANS a canary**, and `controls/oracle.py` **predicts R1's
corrupted checksum bit-for-bit under both compilers** from the measured frame
layout. ⭐ **It never differences the rungs** — otherwise `max_fd` would be
mistaken for the memory error, which is F52's trap avoided by construction.
⚠⚠ **And the three `fd_set`s being SEPARATE LOCALS is now a pinned obligation**:
packing them into an array or shipping one instead of three **deletes the row.**

⭐⭐⭐ **THE HEADLINE ASYMMETRY, MEASURED: ASan is silent at index 2048 on R1;
MIRI FIRES on an R4 mutant at the same index.** The mechanism is read off Miri's
own diagnostic — `core::slice::get_unchecked`'s precondition — **not** from
provenance. **A real memory-safety defect that C's standard detector misses and
Rust's does not.** ⚠ The redzone geometry is exact: index **1024–1279** is
`REPORTED`, index **1280–3071** is **SILENT** because the write has landed in
`wfds`. `adversarial-redzone.bin` and `adversarial-silent.bin` **differ in that
one number and nothing else.**

**The ladder** (whole-program `Ir`, vs `c-gcc`): R2 **+28.4 %** · R3 **−3.5 %** ·
R4/R5 **−2.3 %** · R1h **+10.8 %**. ✅ **`unsafe` and `verus` are byte-identical**
(`md5_fn 659d7b4b`, `identity: exact`) — the first php row to achieve that on
the shipped cell. ⚠⚠ **Only the R1-vs-R1h figure is confound-free**: both gcc
cells vectorise nothing while every other rung uses `xmm`.

⭐ **`ph16`'s upstream fix is COMPLETE and MINIMAL — the counter-example
`.memory-php/02` needed.** That entry generalised from two rows that *"neither
was minimal nor sufficient"*. **n = 3, and the third breaks it.**

⚠ **`controls/spellings.py` was NOT built.** I asked to be told if carrying it
made this two tasks; **it did.** Debt declared in three places, and ⚠⚠ **no
figure in this row is a `fixed-R4 bound`** — `R3ship − R4ship` is *negative*.
**So all three built rows now owe an R4-side search** (item 26).

### F56 — ⚠⚠⚠ THE COMPILER WAS ALREADY ENFORCING THE BOUND THE ROW IS ABOUT, AND CHARGING 60 % FOR IT

`TASK_PHP_025`, and it is the finding that reaches past its own row.

**Ubuntu's gcc injects `-D_FORTIFY_SOURCE=3` whenever it optimises**, and glibc's
fortified `FD_SET` is **`__fdelt_chk`** — a bounds check on **exactly the
quantity this row's defect is about**. Measured: `c-gcc-O3` **aborted** on the
adversarial input with *"bit out of range 0 - FD_SETSIZE on fd_set"*, and on the
**benign** input charged **14.87 `Ir` per `FD_SET`** — 92 605 764 → 148 709 085
`Ir` over 3 773 157 calls, **+60.6 % whole-program, counted rather than
estimated.**

> ⚠⚠⚠ **WITHOUT THE `#undef` BOTH C KERNELS NOW CARRY, R1 WAS NOT R1 IN HALF THE
> GCC CELLS — AND THE TAX WOULD HAVE READ AS C-VERSUS-RUST.**

✅ **Verified independently by the manager, with both halves.** ⚠ **A constant
index elides the check and would have hidden it** — F52's trap — so the probe
uses an `atoi`'d index: `-O0` clean, **`-O2` and `-O3` emit `__fdelt_chk`**,
`-D_FORTIFY_SOURCE=0` clean. Then the must-fire control: **defeat `ph16`'s
`#undef` and `__fdelt_chk` returns.**

✅✅ **IT DOES NOT REACH `ph03` OR `ph07`.** Both call `memcpy` and `memset` and
**neither carries an `#undef`**, so I compiled both kernels at `-O3`: **no `_chk`
symbols in either.** ⚠ This was worth checking rather than assuming — level **3**
uses `__builtin_dynamic_object_size` and tracks allocation sizes that level 2
cannot. **Their published C numbers stand.**

⚠⚠ **AND R1h IS THREE GUARDS, NOT TWO — I had it wrong in the task file.**
`99e290f882c9` also adds **`PHP_SAFE_MAX_FD`, in the caller's frame**, and it is
**not about the write**: `*max_fd = this_fd` sits *inside* the arm
`PHP_SAFE_FD_SET` protects but **is not bounded by it**. ⚠ Guard (a),
`&& this_fd >= 0`, is **DEAD here** — `this_fd` is a 14-bit field — **and the row
says so and measures it rather than banking it.**

⚠⚠ **MY OWN ERROR, IN THREE FILES: the caller's `fd_set` is at `:658`.** I wrote
`:657` and called `TASK_PHP_020`'s `:658` *"off by one and harmless"*. **`_020`
was right; I mis-read my own `sed -n '655,660p'`, whose fourth line is 658.**
⭐ **An inverted correction is worse than the drift it claims to fix** — it
converts a correct citation into a wrong one *and* spends the reviewer's credit
doing it. **Corrected in `RECAP_PHP.md`, `TASK_PHP_025.md` and
`.temp/mgr166/NOTES.md`.**

⭐ **The tier is `narrowed`, decided from `PLAN_PHP.md` §4's DEFINITION.** The M4
enclosing-frame test says `verbatim`; **this row is the case that separates the
test from the definition**, exactly as I suspected when I withdrew my *"already
tier-checked"*. ✅ Corrected in both catalogue parts. ⚠ Overlap **20 %** against
`narrowed`'s 25 % is **accounted for line by line, not repaired by moving the
tier** — which is the honest direction.

### F55 (MANAGER, UNREVIEWED) — ⚠ THE PREFLIGHT RECORD IS KEYED BY THE NAME YOU TYPED, NOT THE ROW IT RESOLVED TO — AND ONE WRONGLY-KEYED DUPLICATE IS COMMITTED

Found verifying `TASK_PHP_024`, which left an untracked
`results-php/preflight/ph07.preflight.json` beside the real
`ph07-strcut-cursor.preflight.json` and correctly called it the manager's call.
**It is not a stray file; it is a defect with a committed instance.** Measured:

| file | `row` field | runs | tools |
|---|---|---:|---|
| `ph00.preflight.json` ⚠ **committed** | `ph00` | **12** | check, measure, report |
| `ph00-smoke.preflight.json` | `ph00-smoke` | **1** | check |
| `ph07.preflight.json` ⚠ untracked, stale | `ph07` | **4** | build, check, measure, report |
| `ph07-strcut-cursor.preflight.json` | `ph07-strcut-cursor` | **16** | build, check, measure, report |

⚠⚠ **`harness-php/` resolves an abbreviated row through `glob(<row>*)` for the
WORK and then keys the record on the STRING YOU TYPED**, so `provenance.py ph07`
operates on `ph07-strcut-cursor` and writes its history to a different file.
**The two then diverge**, and `ph00.preflight.json` — a wrongly-keyed record with
**twelve** runs against the real row's one — has been in the repository since
`TASK_PHP_010`.

✅ **Nothing published rests on it**: the gate reads `results-php/gate/`, and
`--check-stale` is 6/0 either way. ⚠ **What it costs is the audit trail** — a
row's preflight history is silently split by how someone typed its name.
⚠⚠ **I am NOT fixing it here.** `_024` §5.3's rule, which I asked for and am
landing, says a validator change lands **with its must-fire negatives or not at
all**; this needs a control that types both spellings and asserts one file.
**Queued as item 42.**

### F54 — ⭐⭐ A DECLARATION CAN BE WRONG IN EVERY NUMBER AND RIGHT IN EVERY VERDICT, AND THAT IS THE CONFIGURATION NO CHECK HERE CAN SEE

`TASK_PHP_024`. `TASK_PHP_022` M1 checked the hashed `why`'s **first sentence**
and found four stale figures (item 36). Re-deriving **every cell the entry
names** found **nine**, and ⚠⚠ **all eleven numerals reproduce exactly against
`git show 8214b5f:`** — **it is not typos, it is a whole pre-rebuild snapshot**
that was never re-read after the rebuild.

⚠⚠⚠ **WHY NOTHING CAUGHT IT, PRECISELY: every *qualitative* claim survived.** At
O3/isolated the two cells still have equal `n_fn` and equal `fn_bytes`,
`md5_fn_norel` is still identical and `md5_fn` still differs — **so `norel` was
the right level before and after, and no gate verdict ever moved.** The hash
still matched because the text was never edited. ⭐ **A row can publish six wrong
numbers and be right about everything they were cited to support.**

⭐ **AND THE WRONG-COMMIT DEFECT HAD A SECOND COPY THE REVIEW MISSED.**
`c/kernel.h` named `d9dda48f8a7e` as R1h while shipping `cb3cca21b345` hunk (a)
— and so did **`safe_naive.rs`**, ⚠ **also a `measurement_sources` file**, ⚠⚠
**contradicting the ladder table four lines below it.** `TASK_PHP_022` looked at
`c/` and **nobody grepped the rungs**; `_024` found it with a 3-line hash sweep
run *after* its first re-measure, which cost a second full pass.

⭐ **The `extra_spans` disclosure was worse than I reported.** I said *"adding a
span cannot make the number go up for free"* was false in one measured case.
Swept over all seven subsets: **5 of 9 single-span additions RAISE it.** The
union overlap is a **weighted mean and is non-monotone** — so the claim was not
imprecise, it was **false in the common case**.

⭐⭐ **THE PROCESS RULE, AND IT IS NARROWER AND BETTER THAN THE ONE I OFFERED.**
I asked whether I should have committed a `harness-php/` change before review.
The answer: *no, but that is not the mechanism.* **All four defects were in the
harness half; the row half survived intact.** The row shipped with `.temp/php18/`
full of controls; **the validator change shipped with none** — its only artefact
is a 16-line derivation log with no mutation, no expectation and no control in
it, and the eleven must-fire negatives were written **by the reviewer, after the
commit.** ⚠ **A gate run EXERCISES a validator on three rows; it does not ATTACK
it**, and I let the row's green gate stand as evidence about the validator.

> ⭐ **`PROTOCOL_PHP.md` §H, landed: A CHANGE TO A VALIDATOR LANDS WITH ITS
> MUST-FIRE NEGATIVES IN THE SAME CHANGE, OR IT DOES NOT LAND.** All four
> defects were minutes of probe work — ~250 lines caught every one.

⚠ **The `why`-staleness check is priced and deliberately NOT landed**: ~28 lines,
fires on exactly this defect with **zero false alarms across all three rows**,
goes silent after the repair. `_024` refused to land its own new gate stage in
the task that argues the manager should not have — *"landing mine in the same
task would refute the argument by example."* ✅ **Correct, and it is `PROTOCOL.md`
rule 3 applied to itself.** ⭐ **The tree then proved its own point**: the gate
caught two citations `_024` introduced, and then caught its *disclosure* of the
first — which is why the check must be **reported, never enforced**.

### F53 — ⚠⚠⚠ A SHARED UPSTREAM FIX IS NOT EVIDENCE OF A SHARED MECHANISM, AND THE RULE THAT SAID OTHERWISE HAD ALREADY PUT A FALSE SENTENCE IN THE CATALOGUE

`TASK_PHP_023` §2.6 and §4.3. **The landed `ph32` block said all three short
entity tables *"are repaired by ONE commit … which is why they are one row"*.**
✅ **Measured at each commit** (`.tasks-php/probes/entcount.py` run at nine PHP-5.0 commits
touching `html.c` between 5.0.3 and 5.0.4): at **`b9ff04703f16` (2005-01-11)**,
two months earlier, `ent_uni_spacing` and `ent_uni_8592_9002` are **already
`ok`** while `ent_uni_338_402` is still **63/65**. **`56adfe1f3cf1` repairs one
of the three.** ⚠ **So `ph32`'s stated R1h is wrong for two of the three tables
it claims** — and `_019` §10.3's quoted *"spacing"* diff is `b9ff04703f16`'s,
misattributed. ✅ **No `phNN` moves**; neither table is a corpus row, and `ph102`
is unaffected and now rests on stronger evidence.

⭐⭐ **THE RULE FIRED CORRECTLY FOR `ph102` AND INCORRECTLY FOR `ph32` IN THE
SAME PARAGRAPH.** The culprit is `TASK_PHP_019`'s second disjunct — *"different
upstream fixes, each leaving the other standing"* — and `_023`'s attack on it
holds:

> ✅ **A DISTINCT fix is evidence for DIFFERENT.**
> ⚠⚠⚠ **A SHARED fix is NOT evidence for SAME.** One commit routinely repairs
> unrelated errors in one file — `56adfe1f3cf1` fixes `ent_uni_338_402`'s
> **count** and, in the same patch, two pure **name** typos in a correctly-sized
> table. **Absence of a distinguishing fix is not presence of a shared
> mechanism.**

⚠ It is also **not a C-side test**, **contingent** on what a maintainer noticed,
**often counterfactual**, and **silent on a large part of the corpus** (`ph36`
has no sha, 17 rows are `fixed-by-rewrite`, 31 % of fixes are 2010+).
⚠⚠ **And `.memory-php/02-ladder.md` ALREADY WARNED** that the `fix_commit`
column *"names **a** fix … NOT necessarily the one that removes the 5.0.0
defect"* — **§2.6 is that warning firing on a hand-bisected chain.**

⭐ **Landed as `PROTOCOL_PHP.md` §G/§G1** — *one test, one burden: can I show
these are the SAME?* — ⚠⚠ **and the rule it replaces was never in a standing
document at all.** `_019` wrote it in a report, **I adopted it without review
and then used it myself to overturn a verdict**, and it has been operating as
folklore ever since. ⚠ **§G is marked UNREVIEWED and owes a second pair of
eyes.** ⚠⚠⚠ **It is a CHECKLIST, NOT A DECISION PROCEDURE**: (a)(b)(c) have no
stated level of abstraction, so **the verdict is a function of the description,
not of the C** — `_019` §7 concedes it returns *both* answers on `CRASH-090` and
breaks the tie from outside itself. ✅ **The half that was always right is the
BURDEN** — kill only on a proof of *same*, the correct inversion of the corpus's
own `merged_members` predicate.

⭐ **This lands on F50 immediately, and helpfully**: the census channel is **good
for FINDING sibling sites and useless for deciding whether they are
duplicates.** Finding is what it is for.

### F52 — ⚠⚠⚠ THE PROBE MADE THE STATE IT WAS MEASURING, AND SO DID MINE, TWICE, THE SAME WEEK

`TASK_PHP_023` §2.2, answering the starred question I put to it — *"`_021`
measured that gcc zeroes the padding `ph94` is about; is the row still
admissible?"* ⭐ **The answer is that the measurement was wrong.**

`TASK_PHP_021`'s probe opened each trial with

```c
zval arg;
memset(&arg, 0, sizeof arg);            /* labelled "zend_API.c:692" */
```

⚠⚠ **There is no such `memset` in PHP, and `zend_API.c:692` is the function's
signature line, not a statement.** The zval reaches `_object_and_properties_init`
from `zend_execute.c:3245 ALLOC_ZVAL` — `emalloc`, contents unspecified — and
`zend_API.c:708` writes only `arg->type`. **Nothing zeroes `value`. The probe
was reading its own zeroes**, and could not distinguish *"the store wrote a
zeroed high half"* from *"the store never touched the padding."*

✅ **Re-run with a `0xAA` poison and the zval from the allocator, nothing else
changed: WILD READ at `-O0`, `-O1`, `-O2` and `-O3`.** ⭐ **The `-O0`
disassembly is the mechanism and it is toolchain-independent**: the store at
`zend_API.c:710` is `mov %ecx,(%rbx)` (4-byte handle) + `mov %rax,0x8(%rbx)`
(handlers) — **bytes 4–7 are never written by anything.** `_021`'s
`mov %esi,%eax` is in the *callee's* return and is irrelevant, because the
caller never stores RAX's high half into the zval at all.

**So `ph94`'s ORIGINAL claim is restored** — *the index is uninitialised memory,
not a program value* — and the corpus's own valgrind *"Use of uninitialised
value of size 8"* at `:4033` is **corroborated, not contradicted.** ⭐ The blob
advice survives for a different reason: not *"a faithful producer gives zeros"*
(false) but *"a faithful producer gives whatever `emalloc` left, which is
neither reproducible nor measurable"* — **a `projection`, and it must be
declared in the divergence ledger with that `kind`.**

⚠⚠⚠ **THE PATTERN IS THE FINDING, AND IT IS MINE TOO.** Three probes, one week,
all of them **constructing the state they were measuring** and rendering it as a
confident result:

| probe | the construction | what it claimed |
|---|---|---|
| `_021`'s `ph94_probe2.c` | a `memset` PHP does not do | *"no OOB read at any `-O`"* — ⚠ **published as a ⭐ headline** |
| my `asan_reach.c` | `CANARY_BYTE 0xA5`, bit 0 already set, so `|= 1` was a **no-op** | *"canary INTACT — nothing saw it"* (F50) |
| my `V5C` check | `re.sub(r'\D','',…)`, turning `V5C-001` into `5001` | *"absent from `v5c_id`"* (F51) |

⚠⚠ **`count_ent.py` last session was the fourth.** ⭐ **The common shape is not
"a bug in a probe" — it is a probe whose SETUP encodes the answer, so both the
true and the false world render identically.** ⚠ **`.memory-php/00`'s rule
(*"a probe that cannot evaluate must say so"*) does not catch this class**: these
probes *could* evaluate, and did, on a world they built. **The check that works
is the one `_023` used — change the setup's arbitrary constant and see whether
the verdict moves.**

### F51 (MANAGER, UNREVIEWED) — ⚠⚠ THE COMMITTED CLAIM LAYER RESTS ON GITIGNORED SCRATCH IN TEN PLACES, AND **TWO ARE ALREADY GONE**

`CLAUDE.md` rule 1 makes everything under `.temp/` re-derivable and **mandates
deleting it once the gates are green.** So a committed document that cites
`.temp/` is a claim with a scheduled expiry, and `citecheck.py` could not see it
— the path *resolves today*, which is all `os.path.exists` asks.

⚠⚠ **The sharpest instance: `CATALOGUE.md` C.7's coverage claim** — *"Nothing is
NOT killed and NOT catalogued. ✅ Measured with `python3
.temp/php11/coverage.py`"* — **rested entirely on a script the repo does not
carry, which existed in four divergent scratch copies (85 / 75 / 39 / 19
lines), none authoritative.** ✅ **Promoted to `.tasks-php/coverage.py` and the
`166/166` re-derived and CONFIRMED**, so the claim is now reproducible.

⚠ **And the pasted output block is stale**: it says **91 rows / 161 ids**; the
file has **93 / 163**. A number pasted into a document does not track the
document — the same shape as F14 (`0 STALE` ≠ pinned) and the `why`-block hole
at item 36. **Queued as item 39; `CATALOGUE.md` belongs to `TASK_PHP_023` today.**

⭐ **Two repairs to `coverage.py` came with the promotion, both from F49:** the
row regexes were `ph\d\d` (blind to `ph100`+), and **`gaps:` was computed from
`range(1, len(rows)+1)` — its own hit count — so a row it could not see shrank
the expected set by exactly one and the gap list stayed empty. The check could
not report its own blindness.** ✅ **F49's claim that the `166/166` was
unaffected is CORRECT**, verified by keeping both computations side by side.

⭐ **A third defect the promotion found, and it was MINE.** The tool reported
*"3 ids the catalogue names that the corpus does not have"* — `V5C-015`,
`V5C-116`, `V5C-173` — and `CATALOGUE.md` had pasted that line in unexplained.
They are **legitimate**: the corpus's own `merged_members` column, ids merged
away into a surviving row (`V5C-116` → `CRASH-115`, cited by `ph03`). **The
corpus has a THIRD namespace and the checker knew two of them.** ⚠⚠ **My first
probe "confirmed" they were absent from `v5c_id` too — using
`re.sub(r'\D','',...)`, which turns `V5C-001` into `5001`.** A wrong comparison
rendered as a confident negative, **the exact failure `count_ent.py` produced
last session**, caught only because the *"numeric range 5001–5191"* it printed
beside the verdict was visibly absurd. **The verdict happened to be right; the
evidence for it was nonsense.**

⚠ **The general form: a checker that lives in scratch cannot outlive the claim
it certifies.** `boxcheck.py` and `citecheck.py` were in `.temp/mgr165/` too and
are now `.tasks-php/` alongside `quota.py`, `coverage.py`, `fixsurvey.py` and
the landing scripts.

### F50 (MANAGER, UNREVIEWED, n = 1) — ⭐⭐ A FIX COMMIT IS A **CENSUS** OF ITS DEFECT'S SIBLINGS, AND WE HAVE ONLY EVER READ IT AS A SOURCE OF R1h

Found while prepping `ph16`'s build task — evidence and a `.tasks-php/probes/refetch_f50_census.sh` that
regenerates all of it in `.temp/mgr166/`. ⚠ **`PROTOCOL.md` rule 3: this is my
own observation and I have not cleared it. `TASK_PHP_026` is written to attack
it, and my prediction is written down there so it can be refuted.**

`ph16`'s `fix_commit` `99e290f882c9` was already on file, and
`FIXSURVEY_001.md:67-81` already recorded that it touches **10 files** — under a
heading that reads that number as a **cost**: *"⚠ 12 fixes touch ≥ 5 files
(F34's 'inside a rewrite' shape)"*, and `UPSTREAM_001.md:64`'s *"⚠ right fix,
big commit; cite the hunk, not the commit."*

⭐ **For `ph16` the extra files are not rewrite collateral. They are the same
defect at three other sites.** The commit adds one macro *pair* —
`PHP_SAFE_FD_SET` **and `PHP_SAFE_FD_ISSET`** — and applies it at four places:

| # | site in pristine 5.0.0 | primitive | catalogued? |
|---|---|---|---|
| 1 | `ext/standard/streamsfuncs.c:541` | OOB **write** | ✅ **`ph16`** |
| 2 | `ext/standard/streamsfuncs.c:577` | OOB **read** | ❌ |
| 3 | `ext/sockets/sockets.c:536` | OOB **write** | ❌ |
| 4 | `ext/sockets/sockets.c:563` | OOB **read** | ❌ |

⚠⚠ **`ext/sockets/sockets.c` has ZERO rows in the entire catalogue.**

> **The number we recorded as a liability is a lead.** Every one of the ~91
> resolved rows has a `fix_commit` on file, so the channel costs a patch fetch
> and a read — **and the discriminator is the commit MESSAGE**: `ph16`'s is a
> deliberate sweep (*"we avoid… by using poll(2)"*), `ph24`'s is *"Reimplemented
> date and gmdate with new timelib code"* and will yield nothing.

⚠⚠⚠ **n = 1, AND I EXPECT IT TO BE A MINORITY.** ✅ **"`ph16` is the only one
and the channel is dead" is a good result and `_026` is told to say it plainly**
— a one-instance channel dressed up as a programme is worse than a measured
negative (F7, F13), and this manager's projections have been wrong before (F32,
F36, and the `ph29` doubt that was wrong in all three limbs).

⚠ **This does NOT reopen the admission bar.** Every candidate it yields still
faces `PLAN_PHP.md` §3 on the C alone.

⭐⭐ **AND `TASK_PHP_023` HAS SINCE SETTLED HOW TO READ IT, IN THE DIRECTION THAT
MAKES THE CHANNEL MORE USEFUL.** I had flagged #1 vs #2 as a sharp test of
`_019`'s rule, because they **share one upstream fix** while differing in fault
primitive. `_023` measured that disjunct and it failed: **a *distinct* fix is
evidence for DIFFERENT; a *shared* fix is NOT evidence for SAME** — one commit
routinely repairs unrelated errors in one file, and that exact inference put a
false sentence into `ph32` (F53). **So the fix commit is good for FINDING
sibling sites and useless for deciding whether they are duplicates.** A clean
division of labour, and finding is what the channel is for. ⚠ **`_026` is told
not to report *"these four share a fix, therefore one mechanism"*** — the
refuted inference, in this task's own subject matter. **The finding is the
CHANNEL, not a row count.**

⭐ Also re-confirmed at source, and the catalogue is **exact**: `:541`, the
caller's `fd_set` at `:658` (⚠⚠ **this said `:657` and called `_020`'s `:658` an off-by-one; `_020` WAS RIGHT and the error was mine** — `TASK_PHP_025` caught it, F56),
`FD_SETSIZE 1024`, `sizeof(fd_set) 128`, index 4096 → **byte offset 512, past
the object**. ⚠ And `PHP_SAFE_FD_SET`'s safety is `#ifdef`-conditional — **Win32
gets the unguarded spelling and the comment saying so is CORRECT**, because
Win32's `fd_set` is a counted array of `SOCKET`s. **R1h must state which branch
it compiles.**

⭐⭐ **AND THE ROW'S ORACLE PROBLEM IS SOLVED, BY MEASUREMENT** (rule 14 —
`.tasks-php/probes/asan_reach.c`, one write per process past a 128-byte on-stack
`fd_set`, **identical at `-O0`, `-O1`, `-O3`**):

| bytes past the object | ASan | canary |
|---|---|---|
| 8, 16 | ✅ **REPORTED** `stack-buffer-overflow` | — |
| **32 … 512** | ⚠ **SILENT** | ⭐ **CAUGHT IT** |
| 4096 | ⚠ SILENT | INTACT — past the canary's own 512 B |

✅ **The catalogue's premise holds. But the cliff is at 32 bytes, not near 384**
— the redzone is 32 B wide, and the block's two data points leave the boundary
unspecified across a 47× range. ⭐⭐ **The canary oracle works across the whole
range where ASan fails, and for exactly the reason ASan fails**: past the
redzone the write lands in a **live neighbouring object**, so the address is
legitimate and there is nothing for a sanitizer to report — but it is an object
we control. **`TASK_PHP_025` §3 now carries this as a measurement rather than a
recommendation**, with the two caveats it earns: reach is bounded by the canary
and not by the defect, and `volatile` is load-bearing.

⚠⚠ **MY FIRST VERSION OF THAT PROBE PRINTED A CONFIDENT WRONG NEGATIVE.**
`CANARY_BYTE` was `0xA5`, bit 0 already set, so the kernel's `|= 1` was a
**no-op** and every distance reported *"canary INTACT — nothing in this frame
saw it"*. It said the opposite of the truth and looked clean. **Same class as
`count_ent.py`, and as the `re.sub(r'\D','',…)` V5C check in F51 the same
afternoon — three in two sessions, every one a broken computation rendering as
a positive claim.** ⚠ **`.memory-php/00`'s rule already covers it and I keep
writing probes that violate it; the rule is not the gap, the habit is.**

### F49 — ⭐⭐⭐ THE STOP CONDITION FIRED, AND THE AUDIT'S OWN FINDING PREDICTED WHICH HALF WOULD FAIL

`TASK_PHP_021` was told to land `_019`+`_020` into `CATALOGUE.md` **and then
trigger-test the nine rows the same batch creates**, with the rule *"more than
two need a correction → STOP the landing."* ⚠⚠ **THREE OF NINE FAILED —
`ph94`, `ph98`, `ph101` — SO THE CATALOGUE IS BYTE-UNCHANGED AT 93 ROWS.**

⭐ **F46 predicted exactly this half.** It measured *"the defect site was wrong
in 0 of 19 rows; the `▸ trigger` line would have cost an engineer time in 3"* and
recommended auditing triggers only. **Applied to the very next batch, the
trigger test fails on a third of it** — while the tiers were re-derived and **all
nine confirmed**. The rate is not a property of an adjudicator; **it is a
property of which half of a row anybody checks.**

| row | what the trigger claimed | what the C does |
|---|---|---|
| **`ph94`** | a wild read | ⚠ **reaches the line and produces nothing.** gcc returns the 16-byte `zend_object_value` in `RAX:RDX` and narrows through **`mov %esi,%eax`**, *zeroing the very padding the row is about*, at **`-O0` through `-O3`** — so `lval == handle` and the read lands **inside** the string. ⭐ **The layout claim is exactly right** (4 bytes into an 8-byte slot, confirmed in the disassembly); **the wild read is a codegen accident.** The kernel must take the un-written half from the blob |
| **`ph98`** | *"a handler that cannot be called"* | ⚠ **`ph21`'s shape** — `set_exception_handler` validates at **registration** (`zend_is_callable`), so such a handler cannot be installed. It must be broken *after* registration, via `zval_copy_ctor` sharing element zvals by refcount |
| **`ph101`** | a PHP snippet | ⚠ **not runnable as written** — `A::$x` is `protected` (E_ERROR from global scope) and the second clause's `class C` is never declared |

⭐⭐ **AND THE ENGINEER DISCLOSED THAT ITS OWN VERDICT WAS DECISIVE**, which is
the thing I most want from a stop condition: *"`ph101` is the marginal one;
scoring it 'additive' would give 2/9 and let the landing proceed — the decision
turns on this row alone."* ✅ **Verdict UPHELD**: a trigger that raises `E_ERROR`
and names an undeclared class is a *failed* trigger, not an incomplete one.

**Delivered and ready**: `.tasks-php/land_019_020.py` — **45 anchors, each
resolving exactly once**, 93 → 102, refuses on re-application, verified against a
scratch copy, **with the three corrected triggers already in its text.** It is
one command *after* the nine rows get a review cycle.

⚠⚠ **A MANAGER DECISION THE ROW FORCED, AND IT REACHES MOST OF FAMILY `S3`.**
`ph95` **passes** — the `pack.c:214` guard is defeated identically at `-O0`,
`-O3` **and `-O3 -fwrapv`**, with `arg = INT_MAX-1` refused as the control —
⚠ **but there is no UB-free trigger, because the signed wrap IS the mechanism**,
and `harness/build.py` is frozen and passes no `-fwrapv`.

> ✅ **DECISION: do NOT add `-fwrapv`** (a `harness/` edit = a 33-pattern
> re-gate, the same call as F31's `-lm`). **A row whose mechanism is signed
> overflow measures what the compiler actually did, and must ship a
> flag-differential control saying so.** ⭐ **`ph95` already supplies the evidence
> that makes this safe**: the mechanism is *stable across `-fwrapv`*, so the
> measurement is not an artefact of the flag's absence. **A row where it is not
> stable is a different row and must say so.**

⚠⚠ **AND A FOURTH *"CHECKER THAT CANNOT SEE ITS OWN BLINDNESS"*.**
`coverage.py`'s row-count regex is **`ph\d\d`** — blind to `ph100`–`ph102` — and
its `gaps:` set is built **from its own hit count**, so on a 102-row file it
prints **`99 … gaps: none`** and *structurally cannot report the blindness*.
✅ Its `166/166` is unaffected. **That is `TASK_PHP_012` M1's shape
(*a checker that accepts the artefact it is checking*) and F17's
(*a reassurance that tells the reader not to look*), for the fourth time.**

✅ **Two small things settled.** Part A's headings summed to 91 because
**`ph92`/`ph93` are `spatial` rows sitting under the `Temporal` heading** — the
landing moves them so heading = section = axis. And the two blank `tier` cells
are **`ph15` and `ph91`, the two `unresolved` rows** — **deliberate, not a
defect**, and the landing leaves them alone.

### F48 — ⚠⚠⚠ I ACCEPTED A REFUSAL AND THEN LANDED THE SAME RULE WITH THE VERBS CHANGED

> ⚠⚠⚠ **AND I ACTED ON THIS REVIEW WHILE IT WAS STILL WRITING.** `TASK_PHP_022`
> notified at **1087** lines; the report finished at **1225**. I committed it
> inside `8e2d834` and then landed findings, acted on §5.1 and opened item 36
> from the partial text — **four commits against a file whose author had not
> finished.** ⚠ **That is `PROTOCOL.md` rule 11's own shape with the roles
> reversed**: the rule forbids editing a file a running agent *reads*, and the
> live hazard turned out to be *acting on* a file a running agent is *writing*.
> ✅ Nothing landed was unfaithful and nothing was lost — **but four findings
> arrived after my commit and are carried below rather than in anything I
> landed**, and the reviewer had to **withdraw its own `m5`** (*"the finding is
> committed and the row is not"*) because I fixed it out from under the review.
> ⭐ **A completion notice is not a completion**, and the cheap guard is the one
> I did not use: **re-read the file's line count before acting on it.**

`TASK_PHP_022`, the review of the rebuild. **It confirmed F47's headline by
construction, refuted the sentence I built on it, and answered the question I
was least sure of with *"you were half right, and the half you got wrong is the
one you asked about."***

⚠⚠⚠ **§5.1 — THE DEFERRAL.** `TASK_PHP_018` refused my protocol extension
(4.1-B) and proposed landing 4.1-A as *"an observation, not a general
permission"*. **I accepted within minutes and said so.** ✅ **Holding 4.1-B was
right. Landing 4.1-A is not, because 4.1-A IS A NORM:**

1. **Its head clause is a deontic permission, in capitals, first** — *"**AND A
   ROW MAY SHIP A SUBSET OF ITS `fix_commit`, IF IT SAYS SO AND SAYS WHY.**"*
   Everything after it *qualifies a permission the preceding sentence has
   already granted.*
2. **It carries a requirement schedule for future rows** — *"a row that wants to
   do the same **owes** … all four of (i)–(iv)"*. **An observation does not tell
   future rows what they owe. That sentence is the definition of a norm.**
3. **It goes into `PROTOCOL_PHP.md` §C**, immediately under the sentence that
   *defines* R1h, in a document every later builder reads as rules.
4. ⚠ **The difference between 4.1-A and 4.1-B is PLACEMENT, NOT SUBSTANCE.**
   Both grant it, both attach the same four disclosures, both make (iii)
   mandatory.

⚠⚠ **And the engineer's own argument for holding refutes landing**: *"holding
costs `ph07` nothing, because the row does not need the protocol to change in
order to ship."* **By exactly that argument, landing 4.1-A buys nothing** — the
only thing it does is tell *future* rows what they may do, which is the thing
the programme had just decided it lacked the evidence for. ⚠ **And (iii) does
not close (a)'s objection**: *any* later upstream change to the function
satisfies it, and `UPSTREAM_002` §1 is itself a demonstration that this
function's guard set moves across many tags.

> ✅ **ACCEPTED. The reviewer's replacement lands instead: the same facts, past
> tense, descriptive, no deontic verbs, no owed-list — plus one sentence saying
> the generalisation is OPEN at n = 1 and that a second row brings it to the
> manager as a proposal.** ⚠ **The asymmetry is the argument**: an under-stated
> observation costs one task when a second row needs it; **an over-stated norm
> is, on this project's own record, what has to be un-landed.**

⭐⭐ **THE PATTERN IS THE FINDING, AND IT IS ABOUT ME.** `TASK_PHP_017` refused
a rule invented to make one row gateable. `TASK_PHP_018` refused mine. **I agreed
with both — and then re-published the second one with softer wording.**
**Agreeing with a refusal and re-wording the refused thing is not accepting it**,
and I could not see it from where I was standing, which is exactly why §5.1 was
in the task file.

**✅ WHAT SURVIVED A HARD ATTACK** — the review re-derived rather than re-read:

- **§2 — the R1h decision holds, on an independent transcription.** Hunk (b)
  **alone removes 0 of 396** over-reads; hunk (a) **alone removes 396 of 396**,
  and it is *structural* — the start walk never reads `length`. The corpus is
  genuinely unrestricted (**read from the `.bin` files**, not from `gen.py`).
  ⭐ **`bug49354.py` is a faithful replay, authenticated against the patch's own
  git blob sha1** and checked against the real C on 18/18 cells.
- **§3 — every published ladder figure reproduces exactly**, and ⭐⭐ **the
  DEGENERATE R4 claim survived a real attack**: three further spellings
  (`copy_from_slice`, fold-from-source, raw-pointer walk) at **+0.001 %,
  −0.003 %, +1.965 %** — none cheaper — **and the metric objection was tested
  too** (whole-program `Ir` beside kernel-exclusive) **and failed.** It now
  stands on **seven spellings from two agents.** `r4_index0`'s byte-identical
  claim checked independently and **true**.
- **§4 — `extra_spans` validates an extra span as strictly as the primary**
  (negatives built), and `ph03`/`ph00` really are byte-identical.

⚠⚠ **MY OWN PREMISE ABOUT THE BOUNDARY IS WRONG, and it is one I put in a task
file.** I wrote that `from == string->len` is safe *"because
`mblen_table_utf8[0] == 1` at the terminator"*. **It is not.** ⭐ **Any step ≥ 1
is in bounds; a step of 0 gives NON-TERMINATION, not an over-read.** The
operative premise is **`mbtab[b] >= 1`** — which is what the proof actually uses.
✅ All **11** `mblen_table`s in 5.0.0 are 256 entries with minimum 1.

⚠⚠ **TWO MAJORS NOBODY ASKED FOR, both on the row as committed:**

1. **`spec.md`'s HASHED `identity[0].why` cites FOUR figures the rebuild
   refuted** — 255 instructions and three hashes, all pre-rebuild. **The hash
   still matches**, so no gate can see it, ⚠ **and `NOTES.md` claims the
   addendum pass covered it, which is a false disclosure.** `PROTOCOL.md` rule
   6's documented hole, reproduced live.
2. **`c/kernel.h:20-25` names `d9dda48f8a7e` as R1h** while the file ships
   `cb3cca21b345` hunk (a) — ⚠ **and `spec.md`'s own `forbidden[2]` calls
   `d9dda48f8a7e` a *different function*.** It is inside `source_sha256` and
   predates the rebuild.

⚠ **Minors worth carrying**: `bug49354.py`'s docstring says it *"shares no code
with `fix_scope.py`"* and **the table and clamps are byte-identical copies** — a
**false disclosure**, though the conclusion is safe because three independent
checks agree; `spellings.py` **re-implements** `measure.py`'s statistic rather
than importing it; and ⚠ **the gate hashes `controls/*.py` and never runs them.**

### F47 — ⭐⭐⭐ ROW 2 REBUILT: THE ROW WAS SHIPPING A RUNG PHP ITSELF CALLS A BUG, AND **NO STRENGTH OF MEMORY-SAFETY-ONLY PROOF WOULD HAVE MOVED**

> ⚠⚠⚠ **THIS HEADING SAID *"AND ONLY A VALUE POSTCONDITION COULD HAVE NOTICED"*.
> THAT IS FALSE AND IT WAS MY AMPLIFICATION** (`TASK_PHP_022` §1). **The gate's
> own stage 2 separates the two configurations** on the rebuilt corpus — **4/32
> windows move on `small.bin`, 297/2050 on `large.bin`**, and the final `u64`
> differs on both. ⚠ **`NOTES.md:70` said only the true half — that the *proof*
> does not move — and I turned it into a claim about every observer.**
> ✅ The corrected claim is narrower, was **confirmed by construction**, and is
> quantified below.

`TASK_PHP_018`. Gate **PASS**, contract `be5f5818ffa6…` → **`1f1508531bd4…`**,
both brackets **66/0** and **6/0** first and last. ⚠ **UNREVIEWED** — nothing
here is in `.memory-php/` (rule 9), and the review is the next task.

**§1a — the question that could have killed the plan: YES, ALL OF THEM DID.**
All four Rust rungs carried hunk (b)'s clamp, **and so did `verus.rs`'s spec
function `strcut_fold`** and all three `model.py` implementations. Removing it
did **not** break the proof — **it made it cheaper**: the `rlimit` requirement
went from ~10–12 plain / **15** twin to **9 on both**.

> ⭐⭐⭐ **AND THAT IS THE ROW'S STRONGEST RESULT, ARRIVING FROM A DIRECTION
> NOBODY DESIGNED: a memory-safety-only `ensures` WOULD HAVE STAYED GREEN
> THROUGH THE ENTIRE REBUILD.** The clamp was never a memory-safety bug — it is
> a *wrong answer*. **That is the concrete case for proving what a function
> computes rather than merely that it does not fault**, and it was produced by
> an accident of the rebuild rather than by an argument.

✅✅ **CONFIRMED BY CONSTRUCTION AT `TASK_PHP_022` §1 — the proof nobody had
written was written, and the result is STRONGER than the assertion.** A
mechanical weakening of the row's own `verus.rs`, audited for value tokens:
**`ms_hunkab` (the pre-rebuild exec, both hunks) and `ms_hunka` (hunk (a) alone)
BOTH verify 17/0 plain and 20/0 twin**, and the `diff` between them is *comments
plus hunk (b)'s six exec lines* — **not one invariant, assert, ghost binding or
`decreases` differs.** Must-fire control holds: delete hunk (a) and both regimes
fail at `frm <= slen`.

⭐⭐ **AND THE ANSWER TO *"what did memory-safety-only cost to define?"* IS THE
BETTER HALF: NOTHING, BECAUSE THERE IS NOTHING TO DEFINE.** The kernel returns a
`u64` and writes no caller-visible memory, **so the honest memory-safety-only
spec is the EMPTY postcondition** — safety lives in the trusted items'
`requires`, the `decreases`, and Verus's built-in checks. ✅ **Vacuity measured
rather than argued: the same kernel with its body replaced by `0u64` verifies
13/0.** ⚠ The reviewer also built the *stronger* reading — an explicit ghost
*"no read past `slen`"* postcondition — **and it too verifies in both
configurations, and even with all four instrumentation points deleted.** *Even
that postcondition is bookkeeping nothing forces.*

> ⭐⭐⭐ **THE NUMBER THAT SAYS IT BEST: the memory-safety-only proof verifies at
> `rlimit` 1, against the row's 9. Essentially the ENTIRE proof budget is the
> value postcondition.**

⚠⚠ **What this does NOT license, and I claimed it did: *"only a value
postcondition could have noticed."*** **The GATE would have** — stage 2's
identity check moves on 4/32 and 297/2050 windows. **The correct statement is
about PROOFS, not about observers**: no strength of memory-safety-only
postcondition distinguishes the two rungs, and the row's `NOTES.md` said exactly
that and no more.

⭐⭐ **I OFFERED A STOPPING POINT AND IT WAS DECLINED ON EVIDENCE BETTER THAN MY
ARGUMENT.** `UPSTREAM_002` reasoned from archaeology. `controls/bug49354.py`
**replays upstream's own regression test** against all three configurations:

```
R1h_ab (the shipped two-hunk fix)   FAILS case 3   <- that IS bug #49354
R1     (5.0.0)                      FAILS case 6   <- that is CRASH-124
R1h    (hunk (a) alone)             agrees on all six
```

**The row was shipping, as "the real upstream fix", a rung PHP itself files as a
bug** — demonstrated behaviourally, not inferred from a tag sweep.

**THE NEW LADDER** (`Ir`/window byte vs R4; `-O3 isolated`; within-row only):
**R2 +59.77 %** (was +57.67) · **R3 +11.98 %** (was +13.50) · **R4 ≡ R5**
**byte-identical up to relocations**. F41's claims **(a)** and **(b)** survive
**unchanged**. ⚠ **This said *"byte-identical"* flat, and `TASK_PHP_022` is
right that the record does not support it: `md5_fn` DIFFERS between R4 and R5
and only `md5_fn_norel` matches, at `O3 / isolated` only.** `spec.md`'s
`identity` entry had it right and `.memory-php/` is clean — **the handoff was
the only place that overstated it.**

⚠⚠ **(c) SURVIVES, HALVED — AND GOT SMALLER WITHOUT GETTING CLEANER, WHICH IS
THE OPPOSITE OF WHAT MY TASK FILE PREDICTED.** One guard instead of two:
**+2.78 `Ir`/call gcc, +6.20 clang** (was +7.30 / +9.27). But the marginal
residual got **2.1× worse on gcc** and 1.5× better on clang.
⚠⚠⚠ **And the cross-check `TASK_PHP_017` §5c rested on has EVAPORATED**: the two
compilers' residuals were `−3.504e−05` and `−3.518e−05`, *identical to three
significant figures*, and §5c read that agreement as proof the residual is a
decomposition artefact. **They are now `+7.3e−05` and `−2.3e−05` — different
magnitudes, opposite signs. That agreement was a coincidence of one corpus.**
✅ The conclusion survives on a replacement argument that does not sit on a
rounding boundary (the marginal moves < 0.002 % on both compilers while the
delta holds across a **7.4×** range of window size); **the four-decimal-place
wording is retired.** ⭐ **A cross-check that only worked on one corpus is worth
more retired loudly than quietly.**

**§2 — `controls/spellings.py`, THE FIRST IN `patterns-php/`, and `ph07` is the
first php row to discharge F39's obligation.** ⚠ B1's `+2.62 %` is **not**
carried over — it was measured against the corpus §1c deleted.

```
fixed-R4 bound              R3ship - R4ship          +11.98 %
cheapest-found in-contract  inf(R3 found) - R4ship    +1.96 %   (r3_reslice)
```

⭐⭐ **AND THE R4 SIDE WAS SEARCHED AND IS DEGENERATE — a clean negative, which
is exactly the half F39's withdrawal said was missing.** Four R4 spellings, none
cheaper than a tie. **`ph07` makes it 12 of 20 rows where an R4-side search
found nothing**, which is `SYNTHESIS.md`'s *"degenerate more often than not"*
confirmed from inside this programme. ⭐ **So this `fixed-R4 bound` is a bound
over a SEARCHED endpoint** — materially stronger than the same number was a task
ago. ⚠ **Not exhausted**: four R4 and five R3 spellings over about one session.

⭐ **`r4_index0` is FREE and STRICTLY BETTER ON THE TRUSTED SIDE** — `s[0]`
instead of `*s.get_unchecked(0)` compiles to **the same bytes at the same
addresses**, verifies 21/0, and **removes one of `get_unchecked`'s four call
sites**. ⚠ Not shipped (the bench rule forbids re-shipping) — **and it is not
even cheaper; it is a smaller trusted surface at the same price**, which is a
different axis from the one the rule is about.

⚠ **A first draft measured the WRONG STATISTIC and said so** — `check.py`'s
100-vs-200 marginal, landing **1 %** off the shipped record. Not a discrepancy:
the driver picks its window from a checksum, so 200 iterations sample different
windows than 25 000. **A control quoted beside the row's headline must compute
the row's headline**; switched, and it now reproduces at **0.000 %** on all four
cells. ⭐ **Reported because it is exactly the size of error that gets absorbed
as noise.**

**§3 — `extra_spans` landed in `harness-php/provenance.py`** (additive, ~60
lines, **no PAT re-gate**, `ph03`/`ph00` byte-identical). ⚠⚠ **It exposed
something worse than it fixed.** The row's overlap headline falls **75 % → 61 %**
and the interesting number is `span2` at **15 %** — **the caller frame, which is
where R1h lives.** It is `modelled` text inside a row whose single `tier` word
says `narrowed`; the three lines that match are the two clamps and the call.
⭐ **The finding: a single `tier` word is the wrong shape for a multi-span row.**
`ph07` cites three spans at three fidelities — **100 % / 75 % / 15 %**. The
schema now lets a row say it lifts three; **it does not let it say at what
fidelity each.** ✅ Deliberately **not** extended — that is a second schema
change on n = 1.

⚠⚠ **§4.1 — I PROPOSED A PROTOCOL EXTENSION AND THE ENGINEER REFUSED IT, AND IT
IS RIGHT.** It ran `TASK_PHP_017`'s own three tests against `UPSTREAM_002` §4's
claim. **(b) and (c) pass** — and (b) is the strongest part of my case: *if
stage 7h learned tomorrow to express "this R1h legitimately differs on benign
inputs", `ph07`'s R1h would still be hunk (a) alone*, so unlike the §A2a clause
it does not retire with the gate check. ⚠⚠ **(a) FAILS.** A permission to cite
*"a tagged upstream configuration"* lets the next engineer **scan tags until one
is convenient** — *"instead of choosing the corpus to fit the fix, choose the fix
to fit the corpus."* **My distinction is true of this row and not true of the
rule unqualified.** ⭐ **And by the criterion `TASK_PHP_017` §3.2 landed — an
observation is settled by one command, a norm needs n ≥ 2 — a permission about
what a row MAY ship is a NORM, and it is on n = 1.**

> ✅ **ACCEPTED, as recommended: land 4.1-A (the worked example, with four
> MANDATORY disclosures) and HOLD the general permission until a second row
> needs it.** Disclosure **(iii) — *an upstream artefact decides it, not the
> row's convenience*** — is the load-bearing one. **Holding costs `ph07`
> nothing**: `spec.md` already discloses that R1h is a subset of `fix_commit`,
> why, and what it was chosen against. ⚠ **This is the second time in three
> tasks that a rule invented to make one row work has been refused, and this
> time the rule was mine.**

⚠ **F31 is PARTLY RETRACTED** (§4.3): stage 7h and `check_sanitizers_hardened`
are **not** the same defect on the same axis. One asks whether R1h changes
benign output — *a property of the fix*; the other whether it still faults — *a
property of the fix's completeness*. **Stage 7h was right; the analogy
`TASK_PHP_017` §4b drew was wrong**, and I had adopted it.

⚠ **THE WALL CLOCK NOW CONTRADICTS A FACT YOU CAN COUNT.** R4 and R5 are
byte-identical and their wall marginals differ by **2.73 %**; on this corpus the
wall clock says safe Rust is **5–6 % FASTER** than unsafe while the instruction
count says it executes **12 % more**. **A measurement that reverses a fact you
can count is measuring the box.**

⚠ **The gate cost 11 rounds, not the budgeted 6 — and every extra one caught a
real defect**, including `spellings.json` pinning **five sources that were
ABSENT** because it used row-relative keys where stage 9b wants repo-relative.
⭐ **That is open item 33's rebound-namespace hazard biting a second time, on a
new file, within a day of being written down.**

⚠ **`r202895` stays unresolved** — no `git-svn-id` trailers, `svn.php.net` dead —
**and it is not in the row.** ⭐ One thing did come out of the hunt: the removal
was committed **three times in the same second**, once per live branch.

### F46 — ⭐⭐ THE CATALOGUE'S MECHANISM SENTENCES HOLD. ITS `▸ trigger` LINES DO NOT, AND THAT IS THE HALF A BUILD TASK RUNS

`TASK_PHP_020`, on a seeded sample **drawn and printed before any C was
opened**. ⚠ **Two rates, never pooled** — the batch four are *chosen*, not drawn.

| stratum | needs correction | |
|---|---|---|
| **block 1**, n = 15, seed 20 | **1** (`ph93`) | 14 `SUPPORTED`, median **6 min/row** |
| **batch four** (`ph12 ph16 ph21 ph29`) | **1** (`ph21`) | the next rows to be built |

**No `NOT SUPPORTED`. No `UNDECIDABLE`.** ✅ **The catalogue's mechanism claims
are overwhelmingly right, and several are exact to a level a sampler does not
expect.** That is the answer I said would be the useful one, and it licenses
writing build tasks against a Part B block.

⭐⭐ **BUT THE RATE IS NOT THE FINDING. THE DEFECT SITE WAS WRONG IN 0 OF 19
ROWS; THE `▸ trigger` LINE WOULD HAVE COST AN ENGINEER TIME IN 3.**

> **The mechanism sentence is a POINTER — a build task re-reads the C anyway, so
> an error there is cheap. The `▸ trigger` line is LOAD-BEARING**: reachability
> is a build task's deliverable #1 (`PLAN_PHP.md` §4.2) and a row engineer
> starts by running the stated trigger. **`ph21`'s does not fire · `ph93`'s
> reaches the cited line and produces nothing · `ph29`'s fires only through UB.**

**→ Any follow-up audit should test `▸ trigger` lines ONLY** — 2–4 min/row once
the file is open, and it is where the entire yield was. ⚠ **This refutes half of
my own §6.3 hypothesis and confirms the other half**, which is the shape of a
question worth having asked.

⚠⚠ **AND THE RATE IS A LOWER BOUND, for two reasons the report states against
its own headline.** *"A cheaper audit than mine would have returned 15/15"* —
the one failure was the row it spent longest on (15 min), and three
`SUPPORTED` rows took 7–9. ⚠ **And the batch four are the rows with the most
eyes already on them** — an adjudication, `FIXSURVEY_001`, `UPSTREAM_001`, a
tier recheck — **and one still failed. Prior scrutiny is not protective.**

**`ph21` — the row that was going to be built FIRST — has a trigger that cannot
fire.** `str_repeat($s, 2^32/strlen($s))` makes `result_len` exactly 0, which
the guard's **surviving** first disjunct `result_len < 1` refuses. ⭐ **And the
block never says where the harm lands**: the general emit path bounds itself
with the *narrowed* `result_len` (`:4160`) and overflows nothing — **the
overflow is the `Z_STRLEN == 1` fast path at `:4153`, whose `memset` takes the
UN-NARROWED 64-bit `Z_LVAL_PP(mult)`.** Working trigger:
`str_repeat("A", 4294967297)`.

⭐ **`ph29` IS SETTLED, THE CATALOGUE WAS RIGHT, AND THE DOUBT WAS MINE.** F36
said *"`to_read` is a `long` and `emalloc` takes a `size_t`, which on this
64-bit box truncates nothing — either the mechanism is 32-bit-only, or it is
elsewhere, or the row is mis-catalogued."* ✅ **Measured on this box** with a
probe replicating `zend_alloc.c:129/132/135/182/201` verbatim: `to_read =
LONG_MAX` → `size = 2^63` → **`real_size = 0`** → a header-sized `malloc`
succeeds. ⚠⚠ **My doubt mis-located the truncation** — it was never at
`emalloc`'s signature; it is `REAL_SIZE` (F5's family). **And the row is
64-bit-ONLY, the exact opposite of the hypothesis I offered**, and satisfied in
our environment. Three strengthenings came with it: a **UB-free** trigger
(`to_read = 4294967295`, avoiding a `LONG_MAX + 1` gcc may fold), it **zeroes
`CHECK_MEMORY_LIMIT`'s accumulator**, and it **reaches the second truncation**
(`zend_alloc.h:53`'s `size:31`).

**→ BUILD ORDER CHANGED, on C-side grounds: `ph16 → ph29 → ph12 → ph21`.**
⚠ **`ph21` goes last precisely because its reachability claim is the one that
failed** — the standing order had it first.

⚠ **Two methodological corrections I am adopting.** (1) **`IMPRECISE` vs `NOT
SUPPORTED` did not separate** — the useful line is *does the error change what a
build task would do?* **Collapse to `SUPPORTED` / `NEEDS CORRECTION`, and count
*additive* corrections separately** (7 of 19 here). (2) ⚠ **Block 2 (n = 10,
seed 21) was NOT run as a mechanism audit** — per-row cost was not lower than
assumed, so it got the **weaker citation test only: 10/10 resolve**, plus two
cost nits. **It is a different test and must never be quoted as a mechanism
rate.** ✅ **The report labels it as such itself**, which is the discipline the
sampling design existed to protect.

### F44 — ⚠⚠⚠ THE MECHANISM TEST: 2 OF 13 KILLS ARE CORRECT AS WRITTEN, AND THE EVIDENCE THAT LOOKED STRONGEST WAS THE WEAKEST

`TASK_PHP_019` ran the test `ADJUDICATION_002` never ran — *does the C support
the mechanism claim?* — on all 13 `C.1` kills and `C.4`'s set, at the pinned
tarball. ⚠ **NOT LANDED**: `TASK_PHP_020` is drawing a sample from Part A and
eight new rows would corrupt its draw. Catalogue **93 → 101** when it does.

**Only 2 of 13 are correct as written** (`CRASH-090 → ph32`, `CRASH-037 →
ph39`). **Two more are right verdicts merged into the WRONG ROW** — `CRASH-101`
is `ph41`'s mechanism, *and `ph41`'s own block says "Do not fold into ph39"*;
`LOGIC-014` is `ph48`'s, *and `ph48` is the row `C.1`'s own sentence says was
**kept** for that reason.* **Nine fail**, eight becoming `ph94`–`ph101`.
⭐ The ninth, `V5C-116`, reverses and gets **no row**: `ph03` is built over both
defects and **has already measured them apart** — 144 of 12 600 documents still
read past the source with the other's complete fix applied.

⭐⭐ **THE ANSWER TO THE QUESTION I MOST WANTED: *"merged by the corpus itself"*
IS THE WEAKEST EVIDENCE IN `C.1`, NOT THE STRONGEST.** Three kills rested on it.

1. **The predicate is different.** The corpus merges on *root cause*
   (`validation/REPORT.md` §2a); `PLAN_PHP.md` §3.1 kills only on *exact C
   mechanism* and **explicitly admits a slight variation**. A corpus merge is
   evidence of relatedness, never of exactness.
2. ⚠⚠ **The burden is INVERTED.** *"Dedup burden of proof was set on 'distinct',
   not 'same'."* Ours splits unless *exact* is proven. **Citing the cell to
   support a kill cites a `not-proven-distinct` as a `proven-same`.**
3. ⚠⚠⚠ **And the corpus's own per-case validators flagged all three, in
   writing, in `verdicts.json`, BEFORE the merge** — *"distinct missing guards,
   verified by arithmetic … a dedup pass should keep them separate"* ·
   *"genuinely distinct (different fix commit) … keep `:212` as the
   distinguishing member"* · *"genuinely two distinct source-level mistakes on
   one line"*. **Three for three.**

⭐ **The three kills that looked strongest because they cited an external
authority were the three where that authority had written down the
counter-evidence.** ⚠ And the `index-other.csv` note that reads *"the SAME
defective construct as V5C-0NN"* is **boilerplate emitted by
`rebuild_corpus.py`**, identical on all three — a template, not a judgement.

**THE BASE RATE, AND ITS LESSON IS NOT THE NUMBER.** Of the **46** distinct ids
ever written down as killed in this programme, **6 survive** — **40 / 46 ≈ 87 %
reversed**, enumerated id-by-id so it can be checked. ⚠⚠ **But the informative
row is the outlier**: every deliberate pass reversed a majority *except*
`TASK_PHP_017`'s, which got **17 %** — and it was testing for a **cost word**.
The mechanism test on that same population returns **8**.

> ⚠⚠⚠ **THE RATE TRACKS THE TEST, NOT THE ROWS. It is not a property of the
> kill lists; it is a property of whether anyone opened the C.**

**And the test's own limit, found by running it.** `C.2` is **one** row and its
kill note already names the missing step — *"a 20-minute measurement, not an
adjudication"*, standing since `TASK_PHP_011`. `C.3` is one row and
`TASK_PHP_012` m3 already showed it does **not** fail criterion 3 — the honest
statement is **zero criterion-3 kills; one kill on a design decision**, owed a
landing, not a re-run. ⚠⚠ **What NOBODY has audited is the 93 catalogued rows'
`corpus rows` cells** — this task found **two** mis-merges there, **and
`coverage.py` cannot see them by construction**: it proves every id is
*somewhere*, never that it is in the *right* somewhere.

⭐ **`C.4`'s set: 6 members, and the enumeration finds no hidden seventh — a
clean negative.** But 3 were never individually adjudicated, because **`C.4`
reversed a set kill straight into another set kill.** → **F22 gains a rider:
*reversing a set into a set is not a reversal.*** ⚠ And `TASK_PHP_012` M2 was
**attacked rather than applied**: its count (3 of 4) is right and was reached
independently, but **two of its four cells are wrong.**

**⚠⚠ MY OWN TWO CORRECTIONS TO THE REPORT, both unreviewed and sent back to it:**

1. **§7 called `CRASH-090` undecidable and asked me to settle a bar question —
   *is a data object part of a C mechanism?* — but the report's OWN §1 rule
   decides it.** Its second disjunct is *"different upstream fixes each of which
   leaves the other standing"*, and ✅ I verified the disjointness at source:
   `46bc2c5ae2ae` (2004-07-19) touches **only** `ent_uni_punct`;
   `bd2e99ee50ed` (2005-05-11) **only** `ent_uni_338_402`. **10 of 13, and the
   bar question does not block the row.** ⚠ **The caution that cuts against my
   own argument**: `bd2e99ee50ed`'s pre-image does **not** match 5.0.0 — the
   comment bug it repairs is a **later** regression (*"merge error from 4.3"*) —
   so it is *a* fix, not demonstrably *the* fix. **F38 half 2 landing on the
   evidence I used to make the point.**
2. ⭐ **It is FOUR tables, not two.** `.tasks-php/probes/count_ent.py`, comment-aware,
   at 5.0.0: `ent_uni_338_402` **63/65**, `ent_uni_spacing` **22/23**,
   `ent_uni_punct` **66/67**, `ent_uni_8592_9002` **410/411**; **the other
   thirteen are exact**, and all four are repaired by 5.0.5. ✅ **This
   reproduces the report's `nm -S` figures exactly by a different method**, and
   confirms `ph32`'s own `⚠ risk` line. **→ Settled at F45.**

> ⚠⚠⚠ **AND THE SENTENCE THAT USED TO END THAT PARAGRAPH — *"the other six
> mapped tables are exact; 7 more are not in entity_map at all"* — WAS FALSE,
> AND IT WAS MY SCRIPT SAYING IT.** `declared()` matched bounds with `(\d+)`, so
> it could not read the **15** `entity_map[]` rows whose bounds are hex
> (`0x80`, `0xff`, …), returned `None` for the **8** tables those rows name —
> **and then printed *"(not in entity_map — unused?)"*.** ✅ Measured after the
> fact: **all 17 tables are in `entity_map[]`; 24 rows, 0 unevaluated, 4 short.**
> ⚠ I pasted that output into `RECAP_PHP.md` **and** into a message to the agent.
>
> ⭐⭐ **The defect is not the arithmetic — it is that BOTH failure paths
> rendered as a POSITIVE CLAIM ABOUT THE C instead of *"I could not evaluate
> this"*** (the other one printed `ok`). **That is F17's shape — a reassurance
> that tells the reader not to look — produced by F10/F11's mechanism: I parsed
> C with a regex to decide a C fact.** `TASK_PHP_019` §10 caught it by
> **re-deriving every number with the compiler**, which is F11's rule verbatim:
> *ask the tool that actually decides.* ⚠ **The staircase now has a fourth
> step, and the fourth is the manager's own probe.** The script is fixed to
> print `CANNOT EVALUATE` and exit non-zero; ✅ **all four of my figures were
> right**, which is exactly why the false sentence beside them survived.

⚠ **The bar question still stands and is mine to settle**: `PLAN_PHP.md` §3.1
and `CLAUDE.md` rule 6 both say *"its C mechanism"* and **neither says whether a
data object is part of one.** The catalogue answers it one way everywhere
already (`ph60` is four sites in one row, `ph61` five, `ph43` two limbs), so the
cheap fix is to **write down the reading we already use** — but it multiplies
`ph32`, `ph39` and `ph41` if decided the other way, so it is not free either.

### F45 — ⭐⭐⭐ A DEFECT MADE INVISIBLE BY THE COMMIT THAT FIXED ITS WARNING

`TASK_PHP_019` §10, on the split F44 sent back. **The answer is TWO rows, not
one and not four** — and the archaeology on the way is worth more than the split.

| row | tables | the commit that removes the **5.0.0** shortfall |
|---|---|---|
| **`ph32`** (keeps `CRASH-089`) | `ent_uni_338_402` **+ `ent_uni_spacing` + `ent_uni_8592_9002`** | **one** commit — `56adfe1f3cf1`, 2005-03-09, bug #28067 |
| **`ph102`** (takes `CRASH-090`) | `ent_uni_punct` | `46bc2c5ae2ae`, 2004-07-19, bug #29199 |

**Both disjuncts of the rule fire, in opposite directions**: the three share a
fix, so they **merge** on the first; `punct`'s fix touches none of them and
theirs touches not `punct`, so it **splits** on the second. ⭐ **So `CRASH-090`
reverses after all** — and *not* on the bar question `TASK_PHP_019` §7 raised,
which now scopes only to three tables that are in **no corpus row** and blocks
nothing.

⚠⚠⚠ **THE FINDING, AND IT IS A THIRD INSTANCE OF THIS PROGRAMME'S SHARPEST
SHAPE.** The repair is a **four-commit chain**, and step 3 is
`bd07142b9128`, 2005-03-10 — *"fix `/*`-within-comment warning"*. It closes the
comment **after** the swallowed block. **The compiler goes quiet; the 24
initialisers stay inside the comment; and php-5.0.4 ships `ent_uni_338_402` at
41 for a declared 65** — ⚠ **twelve times worse than 5.0.0's 63** — **with
`gcc -Wall` silent** (measured by the agent; ✅ **the 41/65 independently
reproduced here by the fixed counter**, 5.0.0 **63** → 5.0.4 **41** → 5.0.5
**65**).

> **A warning was the only thing pointing at the defect, and the fix for the
> warning is what hid it.**

⭐ **So `ph32`'s R1h is TWO commits, and stopping at the first passes every
syntactic check and is still wrong** — `ph03`'s two-hunk finding arriving at an
unrelated site, by an unrelated mechanism. **Three rows now say the same thing
from three directions**: `ph03` (a fix half dead, half incomplete), `ph07`
(a fix half *wrong*, deleted by upstream — F43), `ph32` (a fix whose second half
is invisible because the first half silenced the diagnostic).
⚠ **And it is the same family as `ph07`'s own headline** — *the clamp that
arrives too late to prevent the over-read is exactly the clamp that hides it*
(F41). **The mechanism that suppresses the symptom keeps turning up adjacent to
the defect**, and that is now a claim with four instances rather than a
flourish.

⭐ **Three kinds of shortfall, not one, and the kind explains the history.**
`338_402` and `spacing` are **miscounted NULL runs under explicit range
comments**; `punct` is the only `cs_utf_8` table with **no run markers at all**,
missing one placeholder; `8592_9002` is **compensating errors netting to −1**.
**The 2005 audit commit catches the three *labelled* tables in one pass, while
the unlabelled one had to be found by a user bug report nine months earlier —
and its fix adds the missing run markers.** ⚠ **My guess that the kinds differ
was a guess; it is now measured, and it was the right thing to send back.**

✅ **Three independent methods agree on every localisation** — the corpus's
`nm -S` control binaries, the agent's compiler-evaluated
`sizeof/sizeof[0]` walk, and my regex counter — **and each localisation was
predicted before the patch was read** (*"the omission is immediately before
`dagger`"* → `46bc2c5ae2ae` inserts a `NULL` there; *"`crarr` is one early"* →
`56adfe1f3cf1` moves it).

**Restated: 10 of 13 fail, and only `CRASH-037 → ph39` is correct exactly as
written. Nine new rows `ph94`–`ph102`. Catalogue 93 → 102. 41 of 46 ≈ 89 % of
everything ever killed in this programme is reversed.**

### F43 — ⭐⭐⭐ PHP DELETED HALF ITS OWN SECURITY FIX, AND OUR GATE HAD ALREADY SAID WHY

**Manager work, `.tasks-php/UPSTREAM_002.md`. ⚠ UNREVIEWED — `TASK_PHP_018`
builds on it and the review after it must attack it (rule 3).**

`TASK_PHP_017` §4 refused to land `ph07`'s proposed §A2a clause, noting that
hunk (b) of `cb3cca21b345` is **absent from php-5.2.17 and every later tag it
checked**. It verified the fact and stopped. **I went looking for the commit
that removed it.**

`PHP_FUNCTION(mb_strcut)`, brace-matched and hashed at **nineteen tags** (⚠ **not
grepped** — a grep for the hunk's own source line reports it **absent from
php-5.3.0**, where it is present and respelled `(unsigned int)from`; F35's trap
fired on me *inside* the document that restates it):

| tag | body sha256/16 | hunk (a) | hunk (b) |
|---|---|:---:|:---:|
| `php-5.1.2` … `php-5.2.11` | `a971fe…` / `ec8b60…` | ✅ | ✅ |
| **`php-5.2.12`** … `php-5.2.17` | **`26e2099e33433c74`** | ✅ | ❌ |
| `php-5.3.0`, `php-5.3.1` | `08719ef4…` | ✅ | ✅ *(respelled)* |
| **`php-5.3.2`** … `php-5.3.29` | **`49ad3ab2…`** | ✅ | ❌ |

**The removal is `c2471b495009`** — Moriyoshi Koizumi, 2009-09-23, the only
non-cosmetic commit on that file in the window. Its `mbstring.c` diff is
**exactly hunk (b) and nothing else**, its subject is *"Fixed bug #49354
(`mb_strcut()` cuts wrong length when offset is within a multibyte character)"*,
and it adds **a regression test** pinning six answers hunk (b) got wrong.

⚠⚠⚠ **SO `check.py` STAGE 7h WAS NOT A HARNESS LIMITATION. It detected the same
defect PHP's own maintainers detected — four years later, from a bug report —
and it detected it in the first hour row 2 existed.** The row read a true
refusal as an obstacle and proposed protocol to route around it (open item 24);
`TASK_PHP_017` declined the protocol on other grounds and was **right for a
stronger reason than it gave**. ⭐ **Open item 24 now closes by DELETION rather
than by a rule** — the best available outcome for a rule invented on n = 1.

⭐⭐ **And it is `ph03`'s finding from the opposite direction.** There a stated
obligation caught in 2026 what a patch missed for ten years: the fix was
**incomplete**. Here the fix was **too big**, and the excess was not merely dead
— it was **wrong**, and upstream removed it. Set beside `ph03`'s dead hunk:
**two rows, two shipped security fixes, NEITHER minimal NOR sufficient as
shipped.** That is a result about security patches rather than about PHP, and it
is now n = 2.

⚠ **The blame id is UNRESOLVABLE, and the finding does not need it.** The
removal commit says *"(This bug was introduced by the commit by r202895. Please
double-check the specification of the function you are going to \*fix\*.)"*.
✅ Measured: **php-src's git mirror carries no `git-svn-id` in any commit
message** (sampled across the SVN era), so `r202895` cannot be resolved from the
mirror at all, and I am **not** asserting it is `cb3cca21b345`. ⭐ **What
replaces it is stronger than the blame line, and is measured**: on `PHP-5.2` —
**the branch the removal is on** — `PHP_FUNCTION(mb_strcut)`'s body is
**byte-identical from php-5.1.2 to php-5.2.6** and changes by one unrelated
token to php-5.2.11, so **the three lines deleted in 2009 were added by
`cb3cca21b345` and by no other commit.** The *identity* of the removed code is
established; only the maintainer's *reference* to it is not. ⚠ **The same commit
message appears verbatim on the 5.3 branch as `0c974164e248`**, and 5.3's clamp
is respelled, so the two branches acquired it separately — one more reason the
single revision id cannot carry the claim. ⚠ **And the decision this licenses is a rebuild of row 2**, with its
own risk stated at `UPSTREAM_002.md` §4 — a subset of a commit is not a commit,
and calling a tagged upstream *configuration* an R1h is a protocol extension
invented to make one row work, **which is the exact shape `TASK_PHP_017`
refused.** The claimed difference — §A2a narrowed the *evidence* to fit the
artefact, this widens the *artefact* to fit the evidence — **is the thing to
attack.**

### F42 — ⚠⚠⚠ ROW 2's HEADLINE IS REFUTED BY CONSTRUCTION, AND SO IS F39's DIRECTION

`TASK_PHP_017` did what a review is for. **Three of my own claims and the row's
headline are wrong.** Every number below was re-derived by the reviewer, who
**first reproduced the shipped R3 exactly** (`2029.42` against the record's
`2029.4`) — which is what licenses the comparison.

**B1 — *"the row's cost sits exactly where safe Rust cannot reach it"* is FALSE.**
A hoisted re-slice reaches 80.6 % of it:

```rust
let w0: &[u8] = &s[..=frm];      // ONE check, hoisted OUT of the loop
while n <= frm { start = n; let m = mbtab(w0[n]) as usize; n = n + m; }
```

| | `Ir`/window byte | vs R4 |
|---|--:|--:|
| shipped `safe_tuned` (R3) | 3.4451 | **+13.50 %** |
| **`v1`, safe, in contract** | **3.1151** | **+2.62 %** |
| `unsafe` (R4) | 3.0354 | — |

**Zero `unsafe`. Identical checksums on all seven inputs, adversarial cells
included. In contract by `harness/check.py::spelling_matches` itself** — every
backticked Rust spelling the shipped R3 satisfies, no `forbidden` match. In the
disassembly the `cmp`/`jae` panic pair vanishes from **both** walks and **`v1`'s
start walk is instruction-for-instruction R4's**, seven opcodes, different
register allocation.

⚠ **The right action is NOT to re-ship R3** — `.memory/02-bench-rules.md`
forbids re-shipping for a cheaper spelling. **`v1` ships beside it as the
cheapest-found in-contract R3**, which makes `ph07` **the first php row that can
discharge F39's own obligation.**

**F39's direction claim is WITHDRAWN — it was a theorem, not an observation.**
The reviewer confirmed every one of my figures (`p22`'s **510.5×** exact, all
four directions correct, the PAT set exactly `p13 p34 p42 p49`) **and then
showed the inference does not follow:**

1. ⚠⚠⚠ **The statistic is `R3ship − min(R4 found)` with R3 held fixed, and a
   minimum can only fall. A row in that column that moved *toward* safe Rust
   CANNOT EXIST.** *"Every one against safe Rust"* is arithmetic.
2. ⚠⚠ **The base rate was hidden.** *"Four rows of 22"* implied four searches;
   `results/synthesis.md:369-401` records an R4-side search on **19 of 33 rows,
   and eleven found nothing.** The R4 endpoint is degenerate more often than not.
3. ⚠⚠ **Three of the four counterparts are OUT OF CONTRACT** by their own
   patterns' records (`p13`, `p12`, `p10` — `.memory/01-ladder.md` calls `p10`'s
   *"the **rejected** R4 candidate"*). **Only `p22`'s is admissible.**
4. ⚠⚠ **`SYNTHESIS.md:271-277` ALREADY SAYS IT IS A SEARCH-EFFORT ARTEFACT** —
   *"the R3-side levers … are easy to find; the R4-side levers have to clear the
   prover"*. **I converted a statement about which side got searched into a prior
   about the true value.** On the R3 side the PAT record moves **≥ 9 rows toward
   safe Rust**, often bigger (`p16 +27/+77 → −199/−2545`).
5. ⭐⭐ **And B1 is the direct confirmation from inside this programme**: an
   R3-side search on `ph07` moved **+13.50 % → +2.62 %**, *for* safe Rust, and
   **larger than three of the four R4-side moves the withdrawn claim rested on.**

**What survives, and it is the part that mattered**: both rows' ladders are
`fixed-R4 bound`s with **no search on either side**, `ph03`'s own hashed `why`
already demands *"an in-contract spread beside its headline"*, and **a row that
has searched neither side is unbounded in BOTH directions.**

⚠ **Two smaller corrections of mine, same review:** F38/F40's *"3 of 5 commits
name a later fix"* is **2 of 5** — `ph12`'s `896a5216d73d` **is** the fix; and
F39's *"byte-identical across six PAT patterns"* repeats the paragraph's **own
stale self-description** — it is in all **33**, in four variants.

⭐ **What survived a hard attack**, listed because clean negatives are the
review's other half: the proof killed **22 of 22** mutants, **ten of them
spec-side**, so R5's postcondition pins the function and not merely memory
safety; `lemma_mbtab_matches` verified with no `assume` and no sixth trusted
item; the `broadcast use` scoping did **not** weaken a spec; R1h's positional
fidelity holds — the reviewer brace-matched `PHP_FUNCTION(mb_strcut)` across
**nine** tags and the guard lands where upstream put it; and the `memcpy`
(~2 %) and wall-clock (5.4 %) caveats re-derive to the digit. **Eighteen clean
negatives in all.**

### F41 — ⭐⭐ ROW 2 IS BUILT, AND THE TWO ROWS DISAGREE ABOUT WHAT SAFETY COSTS

> ⚠⚠⚠ **EVERY NUMBER BELOW WAS MEASURED ON A CORPUS THAT NO LONGER EXISTS.
> `TASK_PHP_018` REBUILT THIS ROW (F43/F47) — read F47 for the live ladder.**
> The shipped R1h is now hunk (a) alone, `inputs/gen.py`'s restriction is gone,
> and the benign domain grew by the 13.5 % the withdrawn hunk changed.
> **R2 +57.67 → +59.77 · R3 +13.50 → +11.98 · R4 ≡ R5 still byte-identical
> UP TO RELOCATIONS** (`md5_fn_norel`; ⚠ `md5_fn` itself differs — F47).
> ✅ **Claims (a) and (b) below survive unchanged; (c) halved and its
> cross-check evaporated.** ⚠ **And B1's `+2.62 %` is superseded by `+1.96 %`,
> re-derived — do not quote the old figure.**

`ph07-strcut-cursor` — `mbfl_strcut`'s `mblen_table` arm, `mbfilter.c:1179-1259`,
CRASH-124, tier `narrowed`. **Gate `PASS`**, contract `be5f5818ffa625c7`, R5
**21/0**, 2 justified `loud`. ⚠ **UNREVIEWED** — nothing here is in
`.memory-php/` yet (rule 9). `-O3 isolated`, `Ir`/window byte, **within-row
only**:

| `c-gcc` | `c-gcc-h` | `c-clang` | `safe_naive` | `safe_tuned` | `unsafe` | `verus` |
|---:|---:|---:|---:|---:|---:|---:|
| +27.31 % | **+27.31 %** | +4.81 % | **+57.68 %** | **+13.50 %** | — | **0.00 %** |

⚠⚠⚠ **THE HEADLINE PUBLISHED HERE IS RETRACTED — SEE F42.** It read: *"`R3`'s
two walks are BYTE-FOR-BYTE `R2`'s … no safe spelling removes that check … the
row's cost sits exactly where safe Rust cannot reach it."* **`TASK_PHP_017`
refuted it by construction**: a hoisted `&s[..=frm]` re-slice reaches **80.6 %**
of the R3→R4 gap in safe, in-contract Rust (**+13.50 % → +2.62 %**), and its
start walk is instruction-for-instruction R4's.

**What survives is the measurement and the mechanism, not the impossibility
claim**: the *shipped* R3's two walks are byte-for-byte the shipped R2's — start
walk **9 insns + 1 bounds branch** in both, **7 + 0** in R4/R5 — so **the shipped
R3's entire gain over R2 is the copy and the fold**, and the mechanism predicts
the measurement to **2 %** with no fitting. ⚠ **The error was quantifying over
all safe spellings after searching one.** *"Nobody found one"* and *"none
exists"* are different claims and only the first was ours.

⚠⚠ **SO THE TWO BUILT ROWS ANSWER THE SAME QUESTION WITH OPPOSITE SHAPES, AND
THAT IS THE PROGRAMME'S FIRST REAL COMPARATIVE RESULT:**

| | `ph03` | `ph07` |
|---|---|---|
| what tuning recovers | **86.4 %** of the naive gap | **76.6 %** shipped — ⚠ **and the *"none of it from the pattern's own loop"* leg is GONE**: `v1` recovers the walks too (F42) |
| the upstream fix costs | a **RATE**: ∓3.0 `Ir`/line, **sign depends on the compiler** | a **CONSTANT**: +7.3 `Ir`/call gcc, +9.2 clang — both guards sit **outside both loops** |
| the fix is | **dead in one hunk, incomplete in the other** | ✅ **complete** — 15 333 over-reads → **0**, no residue |
| `R2`–`R5` vs `R1h` | must diverge (a rung built to the fix would panic) | **are ports of it** — because the fix is complete |

⭐ **`.memory-php/02`'s rule *"R2–R5 are NOT ports of R1h"* held by its
conditional, not its conclusion** — here they *are* ports, and the reason is a
measurement rather than a preference.

**Three more results, each measured rather than argued:**

1. ⭐⭐ **THE OVER-READ DOES NOT CHANGE THE ANSWER, AND THE CLAMP THAT ARRIVES
   TOO LATE TO PREVENT IT IS EXACTLY THE CLAMP THAT HIDES IT.** 15 333
   over-reading calls re-run under **seven** different out-of-bounds fillers:
   **0 answers move.** Must-fire control (delete `mbfilter.c:1227`'s
   `start > len`): **13 293 of 15 333 move.** ⚠ **That is why this shipped
   byte-identical in six releases and why no test suite could have seen it** —
   and it is a sharper statement of the same shape as `ph03`'s dead hunk.
2. ⭐ **THE 2010 WALK REWRITE IS NOT THE FIX.** `d9dda48f8a7e` made the walk test
   before it reads; **that rewrite alone still over-reads on 13 293 of the same
   calls.** **The loop shape is not the fix; the bound on `from` is.**
3. ⭐⭐ **ONE FUNCTION, ONE GUARDED WALK AND ONE UNGUARDED ONE** — and the
   asymmetry is **three asymmetries at three scales**, with **the correct code
   ADJACENT to the incorrect code at every scale**: the end walk is bounded three
   lines below an unbounded start walk; the sibling entry point `mb_strimwidth`
   **already clamped `from` from above in the pinned 5.0.0 tarball**; and the fix
   arrived in the caller. ⚠ **It is not "the author forgot"** — the start search
   *is* compared against `from`, and **a comparison against an attacker-controlled
   scalar reads as a bounds check.**

**Two convergences with manager findings, reached independently:**

- ⭐ **F35's family, at row scale.** The engineer's history table was **wrong in
  both directions** — one spelling reported absence where the guard had been
  *renamed*, one unanchored pattern reported presence where the hit was in a
  *different function* — **and neither error is visible from its own output. The
  first version passed a green gate.** ✅ Caught, corrected, re-gated, and kept
  in `NOTES.md`. **Ask about a FUNCTION, not about text.**
- ⚠ **F39, confirmed from the other side**: `ph07` also ships **no
  `controls/spellings.py`**, so *"no ratio is the cost of safety"* — **the debt
  is now on both built rows**, and the engineer flagged it unprompted.

⚠ **Three caveats the row states rather than hides:** `memcpy` is outside
`kernel_exclusive_ir` and **three rungs call it and three do not** — measured, the
hidden term is **~2 %** (R2-vs-R4 is +55.4 % total `Ir` against +57.7 %
kernel-exclusive); **the wall clock can decide nothing here** — R4 and R5 are the
same 255 instructions and their medians differ **5.4 %**, more than any
difference in the table; and `provenance.c_lines` **pins one span while this row
lifts two**, a schema gap now wanted by a second row.

### F40 — the fix hunt is now done for the WHOLE catalogue, once — `.tasks-php/FIXSURVEY_001.md`

`ph07` cost a task to *"where is the upstream fix?"*. **That question is now
answered mechanically for every catalogued row** (`python3
.tasks-php/fixsurvey.py`): **91 of 91, zero unmapped, zero fetch failures.**
Only what changes a decision:

- ⚠ **8 rows have the `ph07` shape — the fix is in ANOTHER FILE**: `ph07 ph27
  ph54 ph82 ph83 ph88 ph89 ph90`.
- ⭐⭐ **THREE of those are one sub-pattern: an EXECUTOR defect fixed in the
  COMPILER.** `ph54`, `ph82`, `ph83` all cite `Zend/zend_execute.c` and are all
  fixed in `Zend/zend_compile.c` (+ the parser). **For VM-level defects the
  repair is often in the code that EMITS the opcodes, not the code that runs
  them.** ⚠ **`R1h` for these is not a line you can add to the kernel**, and each
  must say so. ⭐ `ph27`'s file was **also moved** (`ext/standard/reg.c` →
  `ext/ereg/ereg.c`), so a path search fails on it too.
- ⚠ **12 fixes touch ≥ 5 files** — `ph48` **17**, `ph24` 16, `ph16` 10, `ph26` 9,
  `ph23`/`ph83` 8, then `ph39 ph54 ph65 ph73 ph76 ph84`. ✅ `ph24` and `ph26` are
  **independently** `history_status: fixed-by-rewrite`; the two fields agree.
- ⚠⚠ **`ph36` has no sha at all** — `(bison-regeneration; no single commit)`,
  **the only such row in the corpus**, so §F5 needs one escape hatch (F38).
- ⭐⭐ **28 of 90 rows (31 %) were fixed in 2010 or later**, against a 5.0.0
  release of 2004-07-13. **Each is either *the defect survived 6–21 years* or
  *the named commit is a later hardening*, and the survey cannot tell them
  apart — only the tag check can.** ⚠⚠ ⚠ **This finding said *"every case tested has come out the second
  way — `ph12`, `ph21`, `ph22`"*; `TASK_PHP_017` refuted `ph12`: `896a5216d73d`
  **is** the fix. It is **2 of 5**, not 3 of 5** — still enough to make the tag
  check mandatory, and the correction is exactly why it is. That is what makes the
  per-row tag check mandatory rather than cautious.
- ⭐ **`ph22` was the standout — fix dated 2025 — and settling it produced the
  third instance rather than a headline.** Traced across eight tags: the
  memory-safety hole closed in **5.1.0**, when `INC_OUTPUTPOS` arrived with an
  explicit `INT_MAX` guard; the expression then sat unchanged ~15 years. **`ph22`'s
  R1h is the 5.1.0 macro, not the 2025 commit**, and *"PHP shipped it for 21
  years"* — which this finding published — **is withdrawn.**
  ⭐ **What the 2025 commit really fixes is better**: signed-overflow UB **in the
  macro's ARGUMENT**, `(arg + (arg % 2))` wrapping at `INT_MAX` *before*
  `INC_OUTPUTPOS`'s guard runs — **an overflow-checking macro handed an
  already-wrapped value.** ⚠⚠ **That is `ph20`'s catalogued shape in a second
  function**, surviving nineteen years **inside the guard meant to prevent it**.
- ✅ **A clean negative worth recording.** The 7 rows an earlier version called
  *"unmapped"* are the `LOGIC-`-prefixed ones — the corpus uses **three** id
  prefixes and the parse knew two. ⚠ **Checked deliberately, because `LOGIC-`
  ids also appear under `rust-eval/`, which would have put seven rows'
  provenance on the Rust port** — against `SOURCES.md` and against the standing
  instruction that the port is a reference, never ground truth. **It does not:
  all 24 `LOGIC-` rows are in `index.csv` with ordinary `c_file_line` and
  `fix_commit` cells, and `ph48` cites the `c_file_line` `V5C-166` carries.**
- ⚠ `ph49` and `ph50` resolve to **one** corpus id and commit (CRASH-153). Two
  rows from one report is legitimate — the catalogue splits by mechanism — **but
  nobody has checked these two are distinct.** Flagged, not judged.

### F39 — ⚠⚠⚠ `ph03`'s LADDER IS A PAIR OF SPELLINGS, ITS OWN CONTRACT SAYS SO, AND THE PAT RECORD SAYS THE MISSING NUMBER MOVES **AGAINST SAFE RUST**

**This is not a new caveat. It is an obligation `ph03` already carries, in its
own hashed block, undischarged.** `spec.md`'s `why` — the NAMED-SPELLING
STANDARD paragraph, byte-identical across six PAT patterns — ends:

> *"**Every pattern owes an in-contract spread beside its headline**; on the R3
> side p16 and p17 have one from TASK_018, p02 from TASK_019 and p05 from
> TASK_021 …, on the R4 side ONLY p05 and p16, and p01 and p08 neither."*

`ph03` ships a headline (F33's ladder) and **no spread**. Its `controls/` holds
`negatives.py`, `fix_incomplete.c` and two patches — **no `spellings.py`**,
though the control is a solved, shipped thing on **four PAT rows** (`p13 p34 p42
p49`).

> ⚠⚠⚠ **THE DIRECTION CLAIM BELOW IS WITHDRAWN AT F42.** Every figure in it is
> exact and was re-verified; **the inference is not.** The statistic is
> `R3ship − min(R4 found)` with R3 held fixed, so a minimum can only fall and
> *"every one against safe Rust"* is a theorem. `SYNTHESIS.md:271-277` already
> says the asymmetry is a **search-effort artefact**, and on the R3 side the
> record moves **≥ 9 rows toward safe Rust**. **Read F42 before quoting any of
> this.** ⚠ The **obligation** half of this finding stands untouched.

⚠⚠ **And PAT's own headline result is that this is the biggest term.**
`results/SYNTHESIS.md` **Result 1: *"the safety tax is a property of a pair of
spellings, and the check is rarely the biggest term."*** Where anyone searched
the R4 side — **four rows of 22** — applying the result moved **three out of
their buckets, every one against safe Rust**:

| row | shipped | cheapest admissible R4 found |
|---|---|---|
| **p22** | `+2.00 / +2.00` | **`+125.00 / +1021.00`** — **510× on the large band** |
| **p13** | `−177 / −1054` | `+44.00 / +77.00` — **sign flip** |
| **p12** | `+3.00 / −26.00` | `+20.00 / +66.00` — **sign flip on `large`** |
| **p10** | `−323 / −603` | `−129.00 / −241.00` — **60 % of the margin was R4 spelling** |

**So the prior is not neutral.** `ph03`'s `safe_tuned +3.7 %` and *"tuning
recovers 86.4 % of the naive-safe gap"* are exactly the shape of claim that a
searched counterpart has moved before — and `.memory-php/02-ladder.md` publishes
them **in the authoritative layer**, where rule 9 makes them supersede.

⚠ **What is NOT claimed**: no figure is retracted. PAT's rule is *never re-ship a
rung because a cheaper spelling was found* — the shipped cell stays and is
published as a **`fixed-R4 bound`**, with the cheapest-found beside it, **and
neither is "the true one"**. **`ph03`'s numbers are fixed-R4 bounds that are not
labelled as such**, which is the one thing `SYNTHESIS.md` §2 says loses
information.

⚠ **Nor is `ph03` uniquely at fault** — the same paragraph records `p01` and
`p08` owing both sides. **But `ph03` is the template 90 php rows will clone**, so
an unlabelled headline here propagates in a way it does not on a finished corpus.

**→ Two actions, neither urgent enough to interrupt a build, both before any
number reaches the crash course:** (1) **label `ph03`'s ladder `fixed-R4
bound`** wherever it is published — `.memory-php/02-ladder.md`, F33, the START
HERE box; (2) **a task that ports `controls/spellings.py` to `ph03`** and
publishes the spread. ⚠ **(1) is cheap and (2) is not, so do (1) first** and do
not let (2)'s cost delay it — an unlabelled number is the defect, not a missing
control.

### F38 — ⚠⚠⚠ THE `fix_commit` WAS IN A COLUMN OF THE CORPUS INDEX ALL ALONG — AND IT IS NOT ALWAYS *THE* FIX

**Both halves of this finding matter and the second is the one that saves a row.**

**Half 1 — the lookup nobody did.**
`paper/evaluation/security/vuln-corpus-5.0/index.csv` has a **`fix_commit`
column**. Measured: **all 166 corpus rows carry one**, and **142 of the 145 ids
`CATALOGUE.md` cites resolve to one** (the 3 that do not are `V5C-015`,
`V5C-116`, `V5C-173` — ⭐ **exactly the three C.1 kills that say "merged by the
corpus itself", so the CSV's `merged_members` column independently confirms all
three**). `CRASH-124`'s cell is `cb3cca21b345`; `CRASH-115`'s is
`f95c1df58349`, the commit `ph03` ships as its R1h.

⚠ **That is NOT two independent sources agreeing, and this line said it was.**
`TASK_PHP_013` took `ph03`'s sha from **the corpus's own history layer**
(`TASK_PHP_012` §7.3 *"predicted this from the corpus's history layer"*), so
CSV and row share a source. **What calibrates the column is weaker and more
useful than agreement: the identifier survived BEHAVIOURAL verification.**
`TASK_PHP_013` applied the patch and measured its effect over 12 600 documents,
and `TASK_PHP_014` attacked the result. **The column has been confirmed correct
exactly once, by measurement, on one row** — which is precisely why half 2 below
is not paranoia.

⚠ **Nobody joined the two halves that were both already found.**
`TASK_PHP_012` **M7 counted this very column** (*"166 distinct fix_commit
values… and no repository to resolve them against"*) and correctly called the
blocker *resolution*; `TASK_PHP_013` **solved resolution** (F26, the `.patch`
URL). **From task 13 the answer was one lookup away, and at task 15 an engineer
searched the GitHub commit API and five tag snapshots instead, and the manager
then bisected five tags on top of that.**

⭐ **Why the search HAD to fail, and it is not carelessness.** Everyone reasoned
about the row as *`mbfl_strcut`*, so everyone searched **by function name**. The
fix's subject says **`mb_strcut()`** and its diff touches **`mbstring.c`**.
`TASK_PHP_015`'s search was correct and its corpus was wrong — and it bounded its
own claim explicitly (*"'no fix_commit exists' is **not** proved"*), which is why
this cost a task and not a row. **The key you hold is not the key the answer is
filed under** — `F1`'s three-frames problem, arriving in the *tooling*.

**Half 2 — ⚠⚠ THE COLUMN NAMES *A* FIX, NOT NECESSARILY *THE* MEMORY-SAFETY FIX.**
All five commits fetched and read. **Two of four batch rows would have shipped a
wrong R1h if the column had been taken on faith:**

| row | CSV `fix_commit` | what it actually is |
|---|---|---|
| `ph29` | `445daac3ab1a` (2004-07-28, Ilia) | ✅ **exact and minimal** — adds `if (to_read <= 0) … RETURN_FALSE;` and nothing else |
| `ph16` | `99e290f882c9` (2004-09-17, Wez) | ✅ **the right fix, inside a 10-file 27 KB change** — *"Bug #24189: possibly unsafe select(2) usage. We avoid the problem by using poll(2)"*; it **introduces** `PHP_SAFE_FD_SET` and applies it at the row's line |
| `ph12` | `896a5216d73d` (2006-04-25, Tony) | ❌ **a LATER fix.** Its own pre-image is already `if ((offset + len) >= s1_len)` — **the `len &&` short-circuit, which is the 5.0.0 defect, was gone before this commit.** This one fixes bug #33605, a negative offset with `len == 0` |
| `ph21` | `c591f022f8ab` (2015-05-10, Stas) | ❌ **a later fix, nine years on.** *"Fix bug #69403 and other int overflows"* adds `if (result_len > INT_MAX)` to a function that by then is **already** `size_t` + `safe_emalloc` — the 5.2.0 change that removed the defect |

⭐⭐ **So the column and the tag bisect are COMPLEMENTARY, and neither alone is
sufficient.** The column hands you a real sha with a security-sounding subject
that touches the right function; **only the bisect tells you whether it removes
*your* defect.** The `UPSTREAM_001` survey is not made redundant by this finding
— **it is what caught it.**

**Half 3 — the same CSV has a `history_status`, and ⚠ IT IS NOT THE SHORTCUT IT
LOOKS LIKE.** Two values: **`historical-known` 149**, **`fixed-by-rewrite` 17**.

- ✅ **Useful**: **10 catalogued rows are `fixed-by-rewrite`** — `ph24 ph26 ph36
  ph46 ph63 ph67 ph71 ph76 ph78 ph80`. **Expect F34's shape on every one of
  them**, and budget the archaeology before picking one.
- ✅ **Bounded**: **exactly ONE corpus row has a non-sha `fix_commit`** —
  `bison-yycheck-table-oob` (**`ph36`**), whose cell literally reads
  `(bison-regeneration; no single commit)`. **So `PROTOCOL_PHP.md` §F5's
  "sha-pinned real fix" needs ONE documented escape hatch, not a redesign** —
  and the corpus tells you in advance which row needs it.
- ⚠⚠ **The negative result, and it is the one that matters: neither field
  discriminates half 2.** All four batch rows are `historical-known` **with
  `confidence: high`** — **including `ph12` and `ph21`, whose commits I proved
  are later fixes.** **`historical-known` + `high` does NOT mean "this commit
  removes the 5.0.0 defect".** Nobody may use these fields to skip the check.

⚠ *Coverage note*: 81 of the 91 Part A rows expose a corpus id to a simple
parse; the other 10 (`ph48 ph52 ph66 ph75 ph77 ph79 ph82 ph83 ph84 ph85`) are a
**limit of the parse, not of the corpus** — resolve them by hand when reached.

**→ The pre-build checklist gains the item `TASK_PHP_015` asked for**, in the
form its own evidence now demands: *"read `index.csv`'s `fix_commit` for this
id, fetch the patch, **and confirm against the tags that it is the commit which
removes the 5.0.0 defect** — if it is not, cite both. Check `history_status`
too, but **never as a substitute for that confirmation**."*

### F37 — the two kills that survived the audit are the two that were written down as settled

`ADJUDICATION_001` closed with *"**four** instances in one audit (CRASH-136,
CRASH-157, CRASH-033, CRASH-053) — enough that it is the audit's main result"*:
each a kill whose stated reason the C-side bar forbids. ⚠⚠ **It is six.**
`CATALOGUE.md`'s `C.1` — headed *"Kills — **exact** C-side duplication"* — still
holds **`CRASH-106`** and **`CRASH-109`**, and **neither note claims exactness**:

| | the note's own words | what that is |
|---|---|---|
| CRASH-106 `nl2br` | *"distinct only in needing a ~358 MB input, **which is a worse kernel**"* | **cost** |
| CRASH-109 `wordwrap` | *"the second `alloced` growth path at `:692` **muddies the extraction**"* | **cost** |

**Both name the distinguishing feature and then discount it for cost** — and
`PLAN_PHP.md` §3.1 admits a *slight variation* as its own row here, on an
explicit user decision. ✅ **Both admitted, verified at source**
(`ADJUDICATION_002.md` §2): `ph92` `nl2br` `string.c:3593` — the corpus's **only**
sizing wrap where the multiplier is a constant, so the attacker has **one** free
value and the ~614 MB input is *a consequence of the mechanism*; `ph93`
`wordwrap` `string.c:679` + **`:692-694`** — the corpus's **only** buffer
**regrown mid-emit**, by arithmetic that is itself unchecked `int` and divides by
an attacker-controlled `linelength`.

⚠⚠ **AND BOTH OF THOSE TWO LINES USED TO CARRY A WRONG FACT, which is the
finding's own point landing on the finding.** This entry said **307 MB** (it is
`2^32/7 = 613 566 757`; at `2^31/7` the store goes negative and the allocation
simply fails) and cited `ph93`'s **`:682`** (the else-arm, in which `:692` —
the row's whole distinctness — is **unreachable**). ✅ Corrected in
`CATALOGUE.md` at `TASK_PHP_017` §2.2, and the evidence document's own §2 is
now marked in place rather than silently rewritten. ⚠ **`ph92`'s mechanism also
changed class**: `sizeof` yields `size_t`, so the RHS is 64-bit and is
**truncated by the store** into `int new_length` — **`ph21`'s class, not
`ph19`'s**, which *strengthens* the admission.

⭐⭐ **The reusable result is where the survivors were.** The audit found what it
went looking for; **the two it missed were sitting in the kill list under a
heading that asserts the criterion they fail.** `.memory-php/01-extraction.md`
already says *"an audit that re-examines only what it doubts measures its own
priors"* — **this is that finding's second confirmation, from the opposite
direction.** ⚠ **The remaining `C.1` rows are NOT re-examined**; four say
*"merged by the corpus itself"*, a stronger claim than a reviewer's judgement,
**and nobody has checked that either.**

## Open items — carried, not closed

⚠ **THE NUMBERS HAVE GAPS AND THAT IS CORRECT — DO NOT "REPAIR" THEM.**
**143 rows present, numbered 1 → 147, with 45–47 and 106 ABSENT** and a
growing set retired IN PLACE as `~~N~~`; no number is ever reused.
⛔⛔ **THIS LINE READ *"130 rows, 1 → 134"* UNTIL 2026-09-16 while the check
below printed `133 rows, max 137`** — items **135, 136 and 137 were appended in
the previous session and this header was not.** ▶ **The same defect the
`which statistic` cell has had five times and `task_cost.py`'s `060` entry had
once: APPEND TO A LIST WITHOUT CHECKING THE LIST'S OWN HEADER.** ⚠ **And it
survived a pre-compact audit that was hunting exactly this class** — the audit
checked the cells it had edited, not the ones it had appended to.
⚠ **Re-derived 2026-09-16 by the check below**, not by trusting this line — the
count, the maximum and the gap set are all re-derived, and this sentence exists
only so a reader knows what output to expect.

> ⛔⛔ **AND UNTIL 2026-09-15 THE CHECK BELOW DID NOT PRODUCE THESE NUMBERS.** It
> matched only the plain `| N |` spelling, so it read the **34 rows retired in
> place as `| ~~N~~ |` as ABSENT** and printed *"92 rows … retired: [38
> numbers]"* while this paragraph said **126 and four**. The paragraph's figures
> were the correct ones; ⭐ **the sentence that was false is the one claiming they
> came from the check.** ▶ Repaired by making the check match the claim — both
> spellings — rather than by editing the claim to match the check. ⚠⚠ **This is
> `F128`'s shape one level up: a claim and the derivation cited as its evidence
> disagreeing, in a block whose entire purpose is to be the derivation.** ⓘ And
> the gap set survived only because *"45, 46, 47, 106"* was ALSO written out in
> prose, three paragraphs down — **two stale-prone statements happened to
> disagree in a way that made one of them checkable.**
⛔⛔ **THIS PARAGRAPH SAID *"80 rows present, numbered 1 → 83"* UNTIL 2026-09-15 —
THIRTY-SEVEN ROWS AND THIRTY-EIGHT NUMBERS STALE, IN THE ONE BLOCK WHOSE ENTIRE
PURPOSE IS TO TELL A READER WHICH GAPS ARE CORRECT.** A reader checking the table
against it would have found four gaps where it names three, and 37 rows it does
not admit exist. ▶ **Do not re-hardcode these counts — run the check below.**
⚠ **`106` IS AN UNDOCUMENTED GAP**: the number is referenced **nowhere** in this
file, so it was allocated and never written rather than retired. **Recorded as a
gap so the next audit does not hunt for it**, and **not reused**. ⚠ **Two conventions coexist on purpose** — a retirement whose
*reasoning* is worth keeping stays as a struck row, and one whose successor
supersedes it is deleted. **The check below counts only what is present**, so it
reports `45, 46, 47, 106` as absent and that is the correct output, not a gap to fix. The table is **sorted**, has **no
duplicates**, and every citation elsewhere resolves to a stable number.
⭐ **45, 46 and 47 were all closed on 2026-09-10, and two of the three were
closed by being CORRECTED rather than answered**: **45**'s premise was wrong
(the column was right; `fixsurvey.py`'s `break` hid four of `ph73`'s five ids —
F63), **46** undercounted (`ph16` prices two of that commit's four repairs, not
one — F60), and only **47** was a plain discharge (F62). **Their successors are
48–50.**
⭐⭐ **AND 48 CLOSED THE SAME DAY IT WAS OPENED'S SUCCESSOR ROUND** — *"the
largest unmade decision on the PHP side"* turned out to be **two questions
wearing one number**, so it retires as a DECISION and its residue goes to
**item 35** rather than to a new number. **42 and 43 are now DECIDED but stay
in the table**, because each carries an action nobody has performed.
⚠ **51, 52 and 53 are new on 2026-09-10** and all three come from `_028`/`_031`
refuting a manager premise: **51** `ph29`'s spellings audit would be vacuous
(and my warning was on `ph03`, the wrong row), **52** the two published rows
quote their bound from **different statistics**, **53** `ph16`'s `.rs` comments
state a mechanism its own `NOTES.md` has now retracted.
✅ Check it rather than eyeballing it:

```sh
python3 - <<'EOF'
import re; s=open('RECAP_PHP.md').read(); sec=s[s.index('## Open items'):]
# ⛔ BOTH SPELLINGS OR THE OUTPUT DOES NOT MATCH THE PARAGRAPH ABOVE. A row
#    retired IN PLACE is written `| ~~N~~ |` and IS present; only a number that
#    matches NEITHER pattern is absent. Reading the plain spelling alone made
#    this check report 92 rows and 38 "retired" while the prose said 125 and 4.
n = [int(m) for m in re.findall(r'^\| ~?~?(\d+)~?~? \|', sec, re.M)]
print(len(n), 'rows, max', max(n), '|',
      'sorted' if n == sorted(n) else '⚠ UNSORTED',
      '| dups:', [x for x in set(n) if n.count(x) > 1] or 'none',
      '| ABSENT:', sorted(set(range(1, max(n) + 1)) - set(n)))
EOF
```

⚠ **The manager spent real effort re-deriving this once**, because a summary had
described the table as *"1..37, a permutation"* when it had **23 rows** — the
count and the highest number are different facts and the shorter sentence was
the wrong one.

| # | item | note |
|---|---|---|
| 1 | The pristine tarball lives under **another project's gitignored `.temp/`** and is deletable at any time | Phase 0 must land `patterns-php/SOURCES.md` with the sha256 + a per-file manifest before anything cites it |
| 2 | *"Where does the existing Rust port land on these scales?"* | **deferred, not deleted** (`DP-05`). Well-posed once the corpus exists |
| 3 | `.web/` does not know `results-php/` exists | deliberate. Do not teach it until there is something worth publishing |
| ~~4~~ | ✅ **CLOSED — and it had been closed for four tasks without the table knowing.** `ADJUDICATION_001.md` item 4 admitted CRASH-136; it is `ph13` (`CATALOGUE.md:91`, `:288`) | ⭐ **And it recovered CRASH-134 too, which no open item ever named.** ⚠ **The lesson is the table, not the row**: `PROTOCOL.md` rule 13 one level up — **when you close a finding, re-read the open-items table.** The successor item (m8) was real and is settled at `ADJUDICATION_002.md` |
| 5 | `EG(garbage)` is `zval *garbage[2]` with an unchecked `EG(garbage)[EG(garbage_ptr)++]` | a faithful temporal extraction **inherits a SPATIAL overflow**. Flagged, not bounded away — bounding it silently would be §4.2's invented non-defect. Manager decides |
| 6 | Four temporal merges flagged as probably wrong | ranks 21, 8, 12, 23. Split decisions owed at catalogue adjudication |
| ~~7~~ | ✅ **CLOSED at F9 — and the check turned out to be impossible.** All spatial `hotness` fields stay **reasoned** | The census holds **zero** spatial reports from `Zend/` or `ext/standard/`: 2156 of 2520 fault inside `libmysqlclient.so.14`, the rest in the regex matcher. **The census is struck as a source of spatial frequency evidence** rather than left as an open promise |
| 8 | Rank 15 (CRASH-158) may be spatial, not temporal | cross-check the two miners' lists at adjudication |
| 9 | ⚠⚠ **No php marginal `Ir` is comparable to any PAT one — and no two php runs are comparable to each other either** | `repo_path_bytes` is **15** bytes longer through the shim (⚠ this said **20**; corrected at `TASK_PHP_003`), and `gate.py`'s own `PYTHONDONTWRITEBYTECODE=1` adds `nvars` **+1** and `envp_stack_bytes` **+34** — measured directly at `TASK_PHP_004` (`25 + NUL + one 8-byte envp slot`). ⚠ **`TASK_PHP_003` gave that as +33 and that was a record-to-record difference between two SHELLS, not the variable's cost**: `ph00`'s own `envp_stack_bytes` moved **3686 → 3695** across two runs of the same gate with no source change, so the p01 delta was +33 and is now +42. **Never quote a php figure against a `pNN` one, and re-check the env block before quoting one php figure against another** |
| ~~10~~ | ✅ **CLOSED at `TASK_PHP_006` — `common-php/*.h` is in NO gate digest, and the `<row>/c/` symlink that was supposed to close the measurement half is BYPASSABLE** | `check.py`'s three `common/` globs are non-recursive and none matches `emalloc_shim.h`. The bridge half **fires** (F7). The symlink half was enforced by nothing (B1), was checked in `gate.py`'s preflight at `TASK_PHP_004` — and `TASK_PHP_005` **F-1** got round it twice, with rows that build, link and run a live allocator into neither digest. **`TASK_PHP_006` closes it** |
| 11 | A new php row costs **six commands (~28 min)**, not three | `gate → report → gate` is irreducible and `measure.py` builds nothing. Budget it. ✅ The three places that said three/five now say six (`TASK_PHP_004`) |
| ~~12~~ | ✅ **CLOSED — `.memory-php/` EXISTS**: `00-corpus` `01-extraction` `02-ladder` `03-numbers` `04-process` | Open from the programme's first task to its sixteenth. It carries **only php-specific** findings that survived a full engineer→reviewer cycle; the PAT `.memory/` 00–06 applies unchanged and is **not** restated. ⚠ **It supersedes any task report it contradicts** (rule 9) |
| 13 | ⚠ **`harness-php/*.py` is in NO digest, and putting it in one costs a 33-pattern re-gate** | `check.py`'s `srcs` would have to reach `harness-php/`, i.e. a `harness/` edit (`PLAN_PHP.md` §2.1). `TASK_PHP_004` landed the **cheap half**: `gate.py` writes `results-php/preflight/<row>.preflight.json` with the `harness-php/*.py` hashes, the manifest hash and whether `--no-provenance` was used. ⚠ **That record is evidence, not a pin — nothing hashes it** — ⚠⚠ **and `TASK_PHP_005` F-2 found it is worse than that: it is written one file per ROW, not per run, so a later preflight ERASES `provenance_skipped: true`; nothing anywhere detects a missing record; and the manager had made it uncommitted.** Being fixed at `TASK_PHP_006` (item 18) |
| 14 | ⚠⚠ **`provenance.py`'s overlap floor is SATISFIED BY DEAD CODE — the risk is a false PASS, not a false refusal** | Added at `TASK_PHP_004` for `TASK_PHP_003` M5. ⚠ **This row used to say the danger was a good row tripping a floor. `TASK_PHP_005` F-4 shows the opposite**: a kernel that implements *division*, cites *multiplication*, and hides the citation behind `#if 0` scores **100 % and is ACCEPTED** (`_normalise` drops lines starting with `#`, so `#if 0`/`#endif` vanish and everything between them counts); the same kernel without the dead block is refused at 11 %. ✅ **The floor is not too high** — a realistic `verbatim` `mul_function` lift scores 68 %. ⚠ **The check never reads `main.c`, the driver loop or the build, so it measures presence of TEXT IN A FILE, not presence of code in the benchmark**: a pass is not even evidence that the cited lines are compiled |
| 15 | ⚠ **The php staleness check is `gate.py --tool measure --check-stale`** and the mandated PAT `66/0` one does **not** examine `results-php/` at all | Both are now in `PROTOCOL_PHP.md` §E1 (`TASK_PHP_004`); today the php side is **2 records** |
| 16 | ⚠ **`TASK_PHP_004` edited `RECAP_PHP.md` — the manager's own handoff file** | `PROTOCOL.md` rule 4 reserves the state layer to the manager, and `TASK_PHP_004.md` did not forbid it explicitly. ✅ **The content is ACCEPTED — it is more accurate than what the manager was about to write** (the `+34` vs `+33` shell artefact, the `3686 → 3695` instability, items 13–15). ⚠ **But the boundary is real**: an engineer correcting the manager's numbers *in the manager's file* is how an unreviewed claim reaches the state layer without passing rule 9. **Future php task files must say explicitly that `RECAP_PHP.md` is manager-only** — the fix is one sentence in the task template, not a rollback of good work |
| 17 | ⚠ **PAT-SIDE, LATENT, DELIBERATELY NOT FIXED — and the php side now REFUSES the layout: `check.py:10314` and `measure.py:226` glob `<row>/c/*` NON-RECURSIVELY and drop the directory entry with `isfile()`** | so **every source file a row puts in a `c/` subdirectory is in no digest at all**, and `check.py`'s `--no-build` staleness scan misses it too, so editing one does not even mark a binary stale. ✅ **No row is affected today** — `find patterns patterns-php -mindepth 3 -maxdepth 3 -type d -path '*/c/*'` is empty. ⚠ **Fixing it is a `harness/` edit = a 33-pattern re-gate for zero present benefit.** Decision: **do not fix; FORBID the layout on the php side** (`TASK_PHP_006`), and carry this row so the next person to reach for `c/sub/` finds out first. ⚠ It matters more here than on PAT: php rows are *extracted* C and `c/zend/` is an ordinary thing to want |
| ~~18~~ | ✅ **CLOSED at `TASK_PHP_006`. The record is COMMITTED (minus `when`), the per-row overwrite is fixed by appending, and an absence is now a preflight NOTE** | `.gitignore:24-26` justified it as *"carries a `when` timestamp and the literal `gate_argv`, so it churns"*. ⚠ **`TASK_PHP_005` F-2c measured it: only `when` moves.** `sha256(rest)` is identical across two runs (`d91ce008ad273b36`) and `gate_argv` is a function of the command, **which is exactly the evidence M6 wanted**. The split the manager asked the reviewer to price **exists and costs one field**. → `TASK_PHP_006` commits the record without `when` and fixes the per-row overwrite |
| ~~19~~ | ✅ **CLOSED: THERE IS NO SIZE RULE. The 200-word rule is withdrawn — it was calibrated on n = 1 and is broken by 30 of 33 PAT rows** | `TASK_PHP_005` F-5: up to **2 533** words, and **`p01` — the template every row clones, and the row `PROTOCOL_PHP.md` cites as complying — is 201.** The 200 was simply the measurement of the one row that had been measured. ⚠⚠ **This is the THIRD version of this rule and the second that could not be met**; `RECAP_PHP.md` itself warns that *"a size rule that cannot be met is worse than none"*. **The manager must not invent a fourth number** — `TASK_PHP_006` measures the corpus distribution and proposes a limit, or proposes a structural rule instead, **and whatever lands must be enforced by a check or dropped** |
| ~~20~~ | ✅ **CLOSED at `TASK_PHP_006`** (was: `gate.py <row> --preflight` silently forwarded the flag and ran the tool) | `argparse.REMAINDER` collects from the first positional (`TASK_PHP_005` F-7). ⚠⚠ **The manager's own 06:55 `ph00.preflight.json` — cited as manager-verified evidence for the gitignore decision — is an instance: a FAILED `check.py` launch (`tool_returncode 2`) recorded as a preflight.** Part of the evidence for a manager decision was an artefact of a CLI bug |
| ~~21~~ | ✅ **LANDED** — `TASK_PHP_012` M4 — 12 rows declare `verbatim` whose defect site is inside a `PHP_FUNCTION` / VM-handler / arg-parsing frame, i.e. **`narrowed`** — and NONE has been corrected in `CATALOGUE.md`** | ✅ **Re-run and reproduced by the manager** (`.temp/mgr/batch/tier_recheck.log`): `ph05 ph11 ph12 ph21 ph22 ph24 ph35 ph50 ph55 ph59 ph76 ph80`. ⚠ **A cost statement, never a filter — no row's admission moves.** But `provenance.py` reports overlap **against the declared tier's expectation** (50 % / 25 %) and `TASK_PHP_008` made that a report rather than a floor, so **a mis-declared `verbatim` row hands its reviewer a scary number that is indistinguishable from a bad extraction.** `TASK_PHP_012` said *fix before the first row*; `ph03` was unaffected, **but `ph12` and `ph21` are in the NEXT BATCH.** ✅ **Landing is staged and mechanical**: `python3 .tasks-php/land_m4.py --check\|--apply` edits Part A + Part B for all 12 and **refuses unless every row has exactly two occurrences** (dry-run: 24 edits, 2 each). **Blocked only by `PROTOCOL.md` rule 11** — `TASK_PHP_016` is reading `CATALOGUE.md`. **Land it the moment that task reports** |
| ~~22~~ | ✅ **m8 LANDED (`ph92`/`ph93`, kills withdrawn IN PLACE, `ph28` narrowed). ⚠ M1/M2/M3/M5 and m1 STILL OWED** — was: the rest of `TASK_PHP_012`'s catalogue corrections — M1 (6 of 12 "merges" are silent drops), M2 (the four-`LOGIC` set kill), M3 (CRASH-021 reverses → a `ph60` merge, not a kill), M5 (CRASH-061/126 in the wrong family), and the minors m1/m5/m8 | Batch them with item 21's landing (`PROTOCOL.md` rule 6) — they are all `CATALOGUE.md` edits and share its rule-11 block. ✅ **m8 is ADJUDICATED** (`ADJUDICATION_002.md` §2, F37): `CRASH-106` → **`ph92`**, `CRASH-109` → **`ph93`**, both admitted, mechanisms and citations verified at source, §4 gives the exact Part A / Part B / Part C edits. **What is owed is the LANDING, not the judgement** — and the catalogue goes **91 → 93** |
| ~~23~~ | ✅ **ALL SIX LANDED** the moment `TASK_PHP_016` reported — was: blocked by `PROTOCOL.md` rule 11 — `TASK_PHP_016` is reading `CATALOGUE.md`, `.memory-php/` and `PROTOCOL_PHP.md`. **Land all five in ONE pass the moment it reports** (rule 6) | **(a)** `python3 .tasks-php/land_m4.py --apply` — the 12 mis-tiered rows (item 21). **(b)** `ADJUDICATION_002.md` §4 — add `ph92`/`ph93`, delete their `C.1` kills **and record the re-adjudication in place** (a kill that vanishes is worse than a kill that was wrong — M1), narrow `ph28`'s uniqueness claim to *resident*. Catalogue **91 → 93**. **(c)** `.memory-php/02-ladder.md` — F34's *"the guard moved to the PROLOGUE"* is **superseded**: it moved to the **CALLER, in another file** (F38), and the entry names `ph07`'s R1h, which is now `cb3cca21b345`. **(d)** `.memory-php/00-corpus.md` — its header says findings run *"F1–F34"* (rule 13: headers rot), and it should carry the **`fix_commit` column** and the **`grep -a`** hazard. **(e)** `PROTOCOL_PHP.md` — the `grep -a` rule (F35) and the pre-build item `TASK_PHP_015` asked for, in F38's stronger form: *read the CSV's `fix_commit`, fetch the patch, **and confirm against the tags that it removes the 5.0.0 defect**; if not, cite both*. **(f)** `.memory-php/02-ladder.md` again — **label row 1's table `fixed-R4 bound`** and carry F39's direction prior; the caveat there is the engineer's and is weaker than the situation |
| ~~24~~ | ✅✅ **CLOSING BY DELETION, NOT BY A RULE — `TASK_PHP_018` §1.** `TASK_PHP_017` §4 found hunk (a) alone is memory-safety-complete and is what PHP shipped from 5.2.17, so the clause rescued an avoidable R1h choice; **F43 then found WHY — upstream deleted hunk (b) in `c2471b495009` as bug #49354, with a regression test. Stage 7h was right.** With R1h re-pinned to the converged configuration the corpus restriction goes away and **no clause is needed at all.** ⚠ **The reviewer's guard clause is kept in `TASK_PHP_017_REPORT.md` §4 unlanded**, as the fallback if `TASK_PHP_018` §5.1 declines the rebuild. Was: **`ph07` is built and unreviewed, and its report proposes a `PROTOCOL_PHP.md` §A2a addition that was LOAD-BEARING for the row** | The row gates green only because `inputs/gen.py` keeps the upstream fix's guards **dead** on the measured corpus: `cb3cca21b345` hunk (b) **changes benign output on 15 870 of 117 612 non-crashing calls**, and `check.py` stage 7h requires R1h ≡ R1 on every non-adversarial input. **Proposed clause**: *where the upstream fix changes benign behaviour, the measured corpus must leave its guards dead, `gen.py` must assert it, and the behaviour change is measured in `controls/` where it cannot contaminate the ladder.* ⚠ **NOT LANDED — rule 9.** The manager landed only its own verified items (§F 5–6). **`TASK_PHP_017` must attack this clause specifically**: it is a rule invented to make one row gateable, which is exactly the shape that needs a second row before it becomes protocol |
| ~~25~~ | ✅ **CLOSED at `TASK_PHP_018` §3 — `extra_spans` landed in `harness-php/provenance.py`, additive, ~60 lines, NO PAT re-gate, `ph03`/`ph00` byte-identical.** ⚠⚠ **And it exposed something worse than it fixed**: the row's overlap headline falls **75 % → 61 %** and the caller frame — **the span R1h lives in** — scores **15 %**. It is `modelled` text inside a row whose single `tier` word says `narrowed`. ⭐ **A single `tier` word is the wrong shape for a multi-span row** (100 % / 75 % / 15 % here); the schema now lets a row say it lifts three spans and **not at what fidelity each**. ✅ Deliberately not extended — a second schema change on n = 1. Was:; `ph07` lifts THREE — and the UNPINNED one is where R1h lives** (⚠ this said TWO; `TASK_PHP_017` M1 counted three) | `TASK_PHP_015` §2.5 deferred the schema change; a second row now wants it. ⚠ **It is a `harness-php/` edit, so it costs no PAT re-gate** — but it moves the php preflight record. Decide at the review |
| 26 | ⚠⚠ **THE SPELLINGS DEBT IS NOW ON BOTH BUILT ROWS** (F39) | `controls/spellings.py` exists and works on **four PAT rows** (`p13 p34 p42 p49`); neither php row has one. **Two actions, and the first is cheap**: (a) ✅ **DONE** — both ladders are now labelled `fixed-R4 bound` in `.memory-php/02` and F33/F41; (b) ▶ **`TASK_PHP_018` §2 ports it to `ph07`; `ph03`'s half stays OWED.** ⚠ **Do (b) before any number reaches the crash course.** ⚠⚠ **The reason given here was WITHDRAWN at F42** — it said *"the PAT record is that the missing number moves against safe Rust, three times out of four"*, which is a theorem about taking a minimum, not evidence. **The real reason is stronger and has no direction in it: a row that has searched NEITHER side is unbounded in BOTH**, and `ph07`'s own R3-side search then moved **+13.50 % → +2.62 %**, *toward* safe Rust |
| ~~27~~ | ✅✅ **DONE at `TASK_PHP_018` §2 — and BOTH SIDES were searched.** `controls/spellings.py` is the **first in `patterns-php/`**. **`fixed-R4 bound +11.98 %` · `cheapest-found in-contract +1.96 %` (`r3_reslice`)**, both labelled, `safe_tuned.rs` **not** re-shipped. ⚠ B1's `+2.62 %` is **superseded, not carried** — it was measured on the corpus the rebuild deleted. ⭐⭐ **The R4 side is DEGENERATE** (four spellings, none better than a tie), making `ph07` **12 of 20** rows where an R4 search found nothing — so this bound is over a **searched** endpoint. Was: | +13.50 % → **+2.62 %**, safe, in contract by the gate's own matcher, checksums identical on all seven inputs. ⚠ **Do NOT re-ship R3** (`.memory/02-bench-rules.md`); publish **both, labelled**, which is what `ph03`'s own `why` has demanded all along. ⭐ **This makes `ph07` the first php row that can discharge F39's obligation** — and it should be done before `ph03`'s, because the code already exists |
| 28 | ▶ **`TASK_PHP_019`.** ⚠⚠ **Two MORE `C.1` kills reverse — `CRASH-126` and `CRASH-163`** (`ADJUDICATION_002.md` §5) | Killed **twice** for reasons the bar forbids: once in `C.4`'s set-shaped *"ordinary null-deref"* kill, then again under `C.1` as *"same fallible call's failure not tested"* — **and in both the failure IS tested.** `TASK_PHP_012` M5 is the same finding independently. ⚠ **`CRASH-101` and `CRASH-061` are *slight variations*, which §3.1 admits, so they are candidates too and nobody has looked.** Catalogue **93 → 95+** |
| 29 | ✅ **DISCHARGED at `TASK_PHP_019` → F44 — and the answer is that the rate tracked the TEST.** The mechanism test on the same population the cost-word test scored 17 % on returns **8 reversals**; across the programme **40 of 46 kills ever written down are now reversed**. ⚠ **Landing is BLOCKED on `TASK_PHP_020`** (it is sampling Part A; +8 rows would corrupt its draw). Was: | *"ZERO of the remaining `C.1` notes contains a cost word, so `ADJUDICATION_002`'s predicted re-read finds nothing. The two that DO reverse need a DIFFERENT test — **does the C support the mechanism claim?** — which that document never runs on anything, **including on its own two admissions**."* ⚠ **I audited for a WORD and called it an audit for a REASON.** The cost-word test found the two kills it was shaped to find and is now exhausted; **the mechanism test is unrun on all 12** |
| 30 | ⚠⚠ **A SECOND ADMISSIBLE FORM OF R1h — a TAGGED UPSTREAM CONFIGURATION, pinned by `(tag range, function, body sha256)`** | `PROTOCOL_PHP.md` §C says R1h is *the real upstream `fix_commit`*. F43 makes `ph07`'s R1h a **subset** of one — hunk (a) of `cb3cca21b345`, which is byte-for-byte what four tags shipped and kept. **My argument is that what upstream KEPT is a stronger citation than what it once committed.** ⚠⚠ **It is still a protocol extension invented to make one row work — the exact shape `TASK_PHP_017` refused for the §A2a clause**, and the claimed difference (§A2a narrowed the evidence to fit the artefact; this widens the artefact to fit the evidence) is **unreviewed and is the thing to attack.** `TASK_PHP_018` §4.1 proposes the wording; **nobody lands it before a reviewer has hit it** (rule 9) |
| ~~31~~ | ✅ **DISCHARGED at `TASK_PHP_020` → F46. The mechanism sentences hold (1 of 15 on a seeded block, 1 of 4 on the chosen batch); the `▸ trigger` lines do not (3 of 19 would have cost an engineer time, against 0 wrong defect sites).** ⚠ **The rate is a LOWER bound** — *"a cheaper audit than mine would have returned 15/15"* — and the batch four, the most-scrutinised rows in the corpus, still yielded one. **Any follow-up audits `▸ trigger` lines only.** Was: | Every build so far has found the claim wrong or incomplete, and **three of the four instances were found by accident while doing something else** (`ph07`'s frame, `ph92`'s class, `ph93`'s unreachable arm; `ph29`'s is open — F36). **93 rows are catalogued and 2 are built**, so the rate decides how much a build task may lean on a Part B block. ⚠ **A sample that comes back clean is the useful outcome**, not a disappointing one — F21/F37's lesson applies to this audit as much as to the kills it was derived from |
| 32 | ⚠ **TWO CITATION ROTS, both found by a mechanical sweep of every rooted path in the manager docs — batch them** (rule 6; `.memory-php/` and `PROTOCOL_PHP.md` are open in running agents) | ✅ **First, the clean negative that is the point of running it: of ~500 backticked paths, the ONLY unresolved ones are row-relative (`c/kernel.c`), deliberately hypothetical (`patterns-php/shared/` — the thing F24 says nobody needs) or reports not yet written. No dangling pointer.** ⚠ **(a) `.temp/san_tests/` does not exist in this repo.** It is `/home/apt/repos_common/php-in-safe-rust/.temp/san_tests/` — **484 MB in ANOTHER project's gitignored scratch**, i.e. open item 1's hazard applied to F9's ASan census, which no document says. `.memory-php/00-corpus.md` carries the unrooted path, so an agent following it finds nothing — **and F35's whole lesson is that "found nothing" is indistinguishable from "isn't there".** ✅ `patterns-php/SOURCES.md` is the exception and does it right, both for the census trees and for the tarball (**re-checked today: 5595997 B, sha256 `5783e0c0…d6919`, matches the pin**). ⭐ **And F9's census re-derives EXACTLY, two months on: 2534 logs, 3199 reports, 2450 / 490 / 189 / 70.** ⚠ **(b) `.ph93` is used as the name of a DEMONSTRATION dotted row** in F16 and `PROTOCOL_PHP.md:431`, and `ph93` is now a real catalogued row (`wordwrap`). Rename the demo |
| 33 | ⚠⚠ **A php GATE RECORD IS WRITTEN IN THE REBOUND NAMESPACE AND IS READ IN THE REAL ONE — and it names the one directory `CLAUDE.md` most loudly forbids touching** | ✅ Measured on all **3** php gate records: every one keys its sources as **`common/digest_bridge.py`**, `common/driver.c`, `common/driver.h`, `common/driver.rs`. **Those files do not exist.** They are `common-php/`, and the key is correct *inside* `harness-php/root.py`'s rebinding — which is exactly how the php side reuses the frozen harness without editing it (`PLAN_PHP.md` §2). ⚠ **The hazard is a reader outside that namespace**: someone chasing a STALE key goes looking in `common/`, the **frozen PAT** tree, for a file that is not there — and this project's own F35 finding is that *"not there"* and *"I looked in the wrong place"* are indistinguishable from the output. ⭐ **`TASK_PHP_002_REPORT.md` §3 spotted it and said a reader *"has to come here to expand it"*; it then reached NEITHER `.memory-php/` NOR `PROTOCOL_PHP.md`** — grep confirms neither carries the words *rebind*, *rebound* or *namespace*. **A hazard that lives only in a task report is a hazard nobody will find.** ⚠ **Do NOT fix it**: the keys come from `check.py`'s root-relative derivation, so changing them is a `harness/` edit and a 33-pattern re-gate (items 13/17's decision shape). **Document it, in the batch** |
| 34 | ⚠⚠⚠ **BOTH BUILT ROWS ARE IN THE SAME FAMILY, THIS FILE HAS SAID *"rows built: 2"* FOR FOUR TASKS, AND NO DOCUMENT ANYWHERE SAYS IT** | `CATALOGUE.md` Part B is **93 rows in 20 mechanism families**; `ph03` and `ph07` are **both `S1` — unbounded cursor walk**, a family of 9. **So F41's *"the two rows disagree about what safety costs"* is a WITHIN-family result**, and every use of it as *"two rows"* overstates the spread it covers. ⭐⭐ **Read the other way it is the most useful thing the programme has produced**: two rows from ONE family disagreed on **four properties** — which map onto `PLAN_PHP.md` §9 items **2, 3 and 4** only; ⚠ **items 1, 5 and 6 have never been compared across the two rows, and item 5 cannot be until a spellings search exists on either** (F42) — so **the within-family variance is large on the half we measured, and the between-family variance has never been measured at all.** ⚠⚠ **One row per family — the obvious plan — would have published S1's answer as whichever of the two we happened to pick.** → `.tasks-php/QUOTA_001.md` turns that accident into the method: **an adaptive quota, minimum 2 per family, a family stays OPEN until a new row moves none of the six answers, cap 4.** Floor **40 rows ≈ 140 tasks**, and that price should be visible here rather than discovered at row 30. ⚠ **S1 is NOT settled and owes a third row — record the debt, do not pay it next.** ⚠⚠ **UNREVIEWED, and `TASK_PHP_019`/`_020` are attacking the family boundaries right now — re-derive it after they report, do not defend it** |
| 35 | ⚠⚠ **NOBODY HAS AUDITED THE ROWS' `corpus rows` CELLS, AND `coverage.py` CANNOT SEE THE DEFECT.** ⭐⭐ **ITEM 48's RESIDUE LANDS HERE AND HANDS THE AUDIT ITS INPUT (2026-09-10): 24 of the 30 id-spread rows put EVERY id in a DIFFERENT FUNCTION of 5.0.0, each with its own distinct upstream fix** — `ph73` is 5 ids in 5 functions in 5 files fixed across four years, `ph82` is 9 in 9. §G1 makes a distinct fix **evidence for DIFFERENT**, so these rows assert one mechanism across N functions AND N fixes. ⚠⚠ **NOT a kill and NOT automatically a split** — admission is C-side only, and N functions can genuinely share one C mechanism: `ph61`'s five (`is_a_impl`, `php_array_walk`, `multisort_compare`, `_php_error_log`, `php_var_serialize`) all look like *an argument-stack-resident pointer surviving a userland re-entry*, which is precisely what a family should be. **What it is, is this audit, unpaid.** ⭐ The function census (`.temp/mgr168/enclosing_fn.py`, selftested, calibrated on the `_safe_emalloc`/`_ecalloc` pair F7 caught the manager confusing) **is the input** — it hands the auditor the list instead of asking them to build it. ⚠ **And the spread is a TEMPORAL-axis property — 21 of 31 rows (68 %) vs 6 of 29 type (21 %) and 3 of 42 spatial (7 %)** — so this audit is largest on the axis with zero built rows. ✅ Already-known instance, correctly recorded and NOT a new finding: `coverage.py` flags `CRASH-153` as claimed by both `ph49` and `ph50` with the right §G1 reasoning | `TASK_PHP_019` found **two** ids merged into the wrong surviving row (`CRASH-101` into `ph39` when `ph41`'s own block says *"Do not fold into ph39"*; `LOGIC-014` into `ph47` when `C.1`'s own sentence says `ph48` was **kept** for that mechanism). ⚠⚠ **The coverage checker proves every corpus id is SOMEWHERE; nothing checks it is in the RIGHT somewhere** — and that is by construction, not a bug. ⭐ This is the same shape as `TASK_PHP_012` M1 (*a checker that accepts the artefact it is checking*) on a different field. **It is the next audit after `_019`/`_020`, and it is mechanical: for each id, does the surviving row's mechanism match?** |
| 36 | ⚠⚠ **`ph07` CARRIES FOUR REFUTED FIGURES INSIDE ITS HASHED `why`, AND NO GATE CAN SEE THEM** — ▶ **`TASK_PHP_024`, written** | `TASK_PHP_022` M1/M2. **(a)** `spec.md`'s `identity[0].why` cites **255 instructions** and three hashes, **all pre-rebuild values the rebuild refuted** — ⚠ **the hash still matches**, because the text was never edited, **and `NOTES.md` claims the addendum pass covered it, which is a false disclosure.** `PROTOCOL.md` rule 6's documented hole, reproduced live on a row we are quoting. **(b)** `c/kernel.h:20-25` names **`d9dda48f8a7e`** as R1h while the file ships `cb3cca21b345` hunk (a) — ⚠ **and `spec.md`'s own `forbidden[2]` calls `d9dda48f8a7e` a *different function*.** It is inside `source_sha256` and predates the rebuild. **Both fixes cost a `ph07` re-gate**, plus the minors: `bug49354.py`'s *"shares no code with `fix_scope.py`"* is **false** (byte-identical table and clamps — conclusion still safe, three independent checks agree), `NOTES.md`'s rule-6 fence names 4 against 27 moved, §10d quotes a pre-rebuild log, and `spellings.py` **re-implements** `measure.py`'s statistic rather than importing it |
| 37 | ⚠⚠ **FOUR DEFECTS IN `harness-php/provenance.py`'s NEW `extra_spans`, all found AFTER I committed it** — ▶ **`TASK_PHP_024`, written** | `TASK_PHP_022`'s post-notification half. **(a)** ⚠⚠ **`provenance.py:836-837`'s disclosure *"adding a span cannot make the number go up for free"* is measurably FALSE.** Union overlap is `|hit|/|want|` over deduplicated sets, so **a span above the current fraction RAISES it** — measured on `ph07`'s own excerpts: primary alone **75 % (39/52)** → primary + the 100 % table span **77 % (44/57)**. `ph07` only lands at 61 % because span 2 happens to be 15 %. ✅ The set semantics *do* defend against citing the same span twice (measured: unchanged at 61 %) — **it is the general claim that fails.** **(b)** ⚠ **A `php_provenance: false` row short-circuits before any `extra_spans` validation**, so a wholly bogus extra span passes. **(c)** `gate.py:300` cites `provenance.py:841-843` for the dotted-row glob; the +60 lines moved it to **`:924`** — **citation rot introduced BY the change and not repaired.** **(d)** *"byte-identical"* holds for the **default invocation only**: under `--no-tarball`, `ph03` gains `for any of 1 span(s)` |
| 38 | ⚠ **`ext/sockets/sockets.c` HAS ZERO CATALOGUE ROWS, AND THE FIX COMMIT THAT NAMES IT WAS ALREADY ON FILE** — ▶ **`TASK_PHP_026`, written; dispatch AFTER `_023` lands** | F50, **manager, unreviewed, n = 1**. `ph16`'s `fix_commit` `99e290f882c9` patches **four** unchecked fd-set sites and the catalogue has **one**; the other three are `streamsfuncs.c:577` (`FD_ISSET`, a read) and `sockets.c:536,563`. ⚠⚠ **`FIXSURVEY_001.md:67-81` had already recorded the *10 files* — as a COST** (*"F34's inside-a-rewrite shape"*, *"right fix, big commit"*). **The channel: for each of the ~91 resolved rows, does its fix name siblings we never catalogued?** ⚠ **Expected to be a MINORITY** — the discriminator is the commit *message*, sweep vs rewrite — and *"the channel is dead"* is an outcome `_026` is told to report plainly. ⚠ **Does not reopen the bar**: every candidate still faces `PLAN_PHP.md` §3 on the C alone, and `sockets.c:536` looks `EXACT` against `ph16` under `_019`'s rule. ⚠⚠ **`:541` vs `:577` is a sharp test of that rule — one upstream fix, two fault primitives — so `_026` reads `_023`'s verdict first.** ⚠ First check whether `ext/sockets/` was in the **built configuration the ASan census ran**; if not, its zero rows are explained innocently and the finding is about the census's coverage |
| 39 | ⚠⚠ **`CATALOGUE.md` C.7's COVERAGE CLAIM RESTED ON GITIGNORED SCRATCH, AND ITS PASTED OUTPUT IS STALE** — ▶ **fix when `_023` releases the file** | F51. **(a)** ✅ **Done**: `.temp/php11/coverage.py` promoted to `.tasks-php/coverage.py`, `166/166` re-derived and confirmed, F49's two regex/gap defects repaired, and the corpus's **third namespace** (`merged_members` — `V5C-116` → `CRASH-115`) taught to the checker, which resolves the three *"ids the corpus does not have"* the catalogue had pasted in unexplained. **(b)** ⚠ **Still owed, in `CATALOGUE.md` itself**: C.7 cites `.temp/php11/coverage.py` and quotes **91 rows / 161 ids** against the file's **93 / 163**. Repoint at `.tasks-php/coverage.py` and refresh the block — ⚠ **after the landing, so it is refreshed once at 102.** **(c)** ⚠ **Nine more committed-claim citations into `.temp/`, two ALREADY GONE** (`patterns-php/SOURCES.md` ×4, `PLAN_PHP.md` ×3, `CATALOGUE.md` ×3, `.memory-php/00-corpus.md` ×1). `citecheck.py` now reports them as a **warning, not a failure** — they are evidence with a scheduled expiry, not broken pointers, and the fix is a committed generator per `CLAUDE.md` rule 1, not a whitelist. **(d)** ⚠ **`ph03` and `ph22`'s `corpus rows` cells cite merged-away ids** — legitimate, but F44 rates `merged_members` the WEAKEST evidence in C.1 and **these are the three merges C.1's kills rest on**; `TASK_PHP_019` reports the corpus's own validators flagged all three. **Not reopened here** |
| 40 | ⚠ **`ph98`'s TRIGGER HAS AN UNSTATED RESIDUE DEPENDENCE — F52's CLASS AT A THIRD SITE** | `TASK_PHP_023` §2.5.1. `zend_builtin_functions.c:1054` tests `Z_STRLEN_PP(exception_handler)==0` and for the trigger's `array($o,'m')` that reads `value.str.len` at offset 8 of a zval whose `_array_init` (`zend_API.c:644-651`) writes **only** `value.ht` (offset 0–7) and `type`. ⚠ **If the residue is 0 the handler is silently never stored and the trigger no-ops** — so the row's witness is allocator-dependent in exactly the way `ph94`'s was (F52), at a third site. ✅ **Not a kill and not a block**: the C-side mechanism is unaffected. **A build task on `ph98` must know this before it spends an hour on a trigger that sometimes does nothing.** ⚠ Additive, and `ph100` is *understated* the same way — `zend_execute_API.c:450 INIT_PZVAL(p)` clears `is_ref` and `:451` restores only `refcount`, so the binding breaks even where `SEPARATE_ZVAL` no-ops |
| 41 | ⚠ **`PROTOCOL_PHP.md` §G IS ONE REVIEWER'S RESTATEMENT AND THE MANAGER LANDED IT** | F53. `TASK_PHP_023` §4.3 attacked `TASK_PHP_019`'s duplication rule, measured its second disjunct false, and proposed a replacement; I landed it as `PROTOCOL_PHP.md` §G/§G1 **marked UNREVIEWED**. ⚠⚠ **This is the shape F48 warns about** — I have twice now taken one agent's construction into a standing document without a second pair of eyes, and the rule it replaces got there the same way. ✅ **The difference I am claiming**: the old rule was folklore in a report and is now in a document where it can be attacked, and it had a **measured** defect. ⚠ **If that reasoning is wrong, §G should come back out** — it is one paragraph. **Give it to the next reviewer whose task touches admission** |
| 42 | ⚠ **THE PREFLIGHT RECORD IS KEYED BY THE TYPED NAME, NOT THE RESOLVED ROW** | F55, **manager, unreviewed**. `harness-php/` resolves an abbreviated row through `glob(<row>*)` for the WORK and keys the record on **the string you typed**, so `provenance.py ph07` operates on `ph07-strcut-cursor` and writes its history elsewhere. **Measured**: `ph00.preflight.json` (`row: ph00`, **12 runs**) beside `ph00-smoke.preflight.json` (**1 run**), and `ph07.preflight.json` (**4**) beside `ph07-strcut-cursor.preflight.json` (**16**). ⚠⚠ **The `ph00` one is COMMITTED**, since `TASK_PHP_010`. ✅ **Nothing published rests on it** — the gate reads `results-php/gate/` and `--check-stale` is 6/0 either way; **what it costs is the audit trail**, silently split by how someone typed the name. ⚠ **The fix needs a control that types both spellings and asserts one file** — §H, so not a one-liner. ✅✅ **DECIDED 2026-09-10: KEEP ALL FOUR STRAYS, AND COMMIT THE TWO UNTRACKED ONES.** Current population, with run counts: `_norow` **16** ⭐ *not a stray at all — the record of ROW-LESS invocations, i.e. the `--check-stale` bracket every task file mandates twice, and it must be DOCUMENTED rather than deleted because `row: None, 16 runs` reads like a bug and is not one*; `ph00` **12** vs `ph00-smoke` **1** (⚠ the stray has 12× the real row's history); `ph07` **4** vs `ph07-strcut-cursor` **16**; `ph29` **1** vs `ph29-recvfrom-alloc` **7** (⚠ mine, and the engineer caught it, not me). **Three reasons.** (i) The §H control has to *type both spellings*, and **these four are the only extant instances of the defect** — deleting the evidence before the control exists is how a defect returns. (ii) They are **not rule-1 artefacts**: a run history is re-derivable by no script, so it is evidence and evidence stays. (iii) The tree is currently **inconsistent** — two strays committed, two not — **and that is worse than either policy**, because it makes the population read as two committed accidents rather than four instances of one defect |
| 43 | ⚠ **`ph00-smoke` IS NOW RETIRABLE AND NOBODY HAS RETIRED IT** | Its own `README.md` and `NOTES.md` say to delete it **once a real php row has gated green**; `ph03` and `ph07` both have. ⚠ It is a relocated PAT calibration kernel with **no PHP provenance** (`php_provenance: false`), it prices nothing, and it is **one of the 3 rows every `provenance.py --all` and every `--check-stale` bracket counts** — so the *6 records* and *3 rows checked* figures both include a fixture. ⚠⚠ **It is also the ONLY row the `php_provenance: false` path is exercised on** (item 42's sibling defect lives on that path), so retiring it removes the only live test of that branch. **Decide deliberately; do not just delete it.** ✅✅ **DECIDED 2026-09-10: DO NOT RETIRE IT — RE-LABEL IT.** Its stated condition **is** met (four real rows have gated green), and retiring it is still wrong: it is the **only row exercising the `php_provenance: false` path**, and item 42's sibling defect lives on that path, so retiring it deletes the only live test of the branch. The cost of keeping it — that `--check-stale` and `provenance.py --all` counts include a fixture — is a **documentation problem, not a correctness one**, and one sentence fixes it. ▶ **Rewrite its `README.md`/`NOTES.md` retirement clause** from *"delete me once a real row is green"* to *"retained as the only exercise of the `php_provenance: false` path; its records are fixtures — subtract it from any count."* ⚠⚠ **A retirement condition that has been met and is deliberately not acted on MUST STOP SAYING IT IS ONE**, or the next agent retires it correctly-by-the-document and wrongly-by-the-programme |
| 44 | ⚠⚠ **`vparse` TRUNCATES A VERUS CLAUSE AT THE FIRST `{`, AND THE GATE COMPARES THE PREFIX AND PASSES** | `TASK_PHP_025` §15.5. An `ensures` written with an `if … { … } else { … }` block expression derives as a **prefix** — the reporter's came out as `"r == if not_an_array"`. ⚠⚠ **Verus is unaffected** (it reads the source), **but the `spec.md` item pin under-describes the contract and the gate passes it** — a **false-PASS** shape, not a false-fail. ✅ Worked around in `ph16` by routing the conditional through two spec helpers, so no shipped clause contains a brace; **`harness/` untouched**. ⚠⚠⚠ **The fix is in `harness/vparse.py`, which is hashed into all 33 PAT gate records — a 33-pattern re-gate for a defect no built row currently trips.** Record it, price it, do not pay it on impulse. ⚠ Sibling, same report §15.6: **a `forbidden` entry bans every backticked span in its own PROSE** — documented in `check.py`, and `ph16` is the first row to *fire* on it (**14 refusals**), with the same mistake recurring inside the text that fixed it. **Write `forbidden` prose without backticks.** ⚠ And §15.7: **foreground `sleep` is blocked here, so an `until … sleep` poll loop returns INSTANTLY and reads exactly like a completed wait** — the third distinct shape of the poller hazard, after the `pgrep` self-match (four leaked loops killed 2026-09-09) and a waiter dying while its gate succeeded |
| ~~48~~ | ✅✅ **DECIDED 2026-09-10 — AND IT WAS TWO QUESTIONS WEARING ONE NUMBER. §F5's SINGULAR SPELLING IS CORRECT.** Was: *"§F5 has no spelling for a row with FIVE `fix_commit`s — 30 rows — and it is the largest unmade decision on the PHP side"* | **The spelling: R1h is the `fix_commit` of the id whose `c_file_line` the row's kernel EXTRACTS.** A kernel extracts **one** site (`PLAN_PHP.md` §3 criterion 3); that site is one id; that id has one fix. ✅ **Option (a) has a spelling on every one of the 30**, because the hypothesis that would have broken it — *one site upstream patched N times* — **is dead**: at `file:line` **29 of 30** rows have every id at a distinct line (`ph71` alone collides), and by **enclosing function against the pinned tarball, 24 of 30**. ❌ **Option (b), the union, is REFUSED** — it ships a configuration upstream never shipped as one change, and §C/F43 both rest on R1h being real upstream code, F43's whole lesson being that what upstream **kept** is the stronger citation. ➡ **Option (c), split, is NOT this item's business** — whether N ids belong in one row is a **catalogue** decision under §G1, answerable without reference to R1h, and it is **open item 35**. ⚠⚠ **Conflating the rung question with the catalogue question is what made this look unanswerable.** ⭐ **`_029` had already answered it from the other side** — *"a single `ph73` row cannot ship a single sha-pinned `kernel_hardened.c`"*, with a per-id R1h and tag pin for all five: a row pricing five sites cannot have one R1h, a row extracting one always can. ⚠ **Successor: the §F5 sentence itself, landed UNREVIEWED**; and §1b's residue goes to item 35, **not to a new number.** Evidence: `.temp/mgr168/{item48_decide,enclosing_fn,spread_axis,sha_norm}.py` + `.log`, all with `--selftest` |
| 49 | ⭐ **THE `elsewhere` CHANNEL — 8 RECORDS WHERE THE CITED 5.0.0 TEXT IS IN A *DIFFERENT FILE OF THE SAME PATCH*** | `TASK_PHP_030` §6. `reg.c → ereg.c`, `zend_execute.c → zend_vm_def.h` (×4), `.re → .c`. ⚠ **This converts several bare `INAPPLICABLE`s into *"the code moved file, and the commit may well be the repair"*** — i.e. some of the 18 INAPPLICABLE records are not the `ph07` shape at all but a **rename/generation** boundary. ⚠ **`ph46`/CRASH-053 is flagged for the manager specifically.** Cheap to chase (`python3 .tasks-php/preimage_screen.py --row <row>`), and it strictly *reduces* the number of rows whose R1h looks unanswerable |
| 50 | ⚠ **ITEM 46's RESIDUE: `PHP_SAFE_FD_ISSET` (THE **READ**) AND THE ~20 `poll(2)` CONVERSIONS ARE STILL UNPRICED** | ⚠⚠ **Item 46 is RETIRED because its premise undercounted**: F60. `99e290f882c9` carries **four** repair kinds and **`ph16` prices two** — guard (b) `PHP_SAFE_FD_SET` and guard (c) `PHP_SAFE_MAX_FD` — and `ph16`'s own `spec.md` had already censused the four **sites** and declined to adjudicate. **What is left is (2) the bounds-check on the READ (`streamsfuncs.c:577`, `sockets.c:563`) and (4) the poll conversion.** §G: the burden of showing SAME is **not discharged** — they share a **commit**, not a **fix**, and §G1 makes a distinct fix evidence for DIFFERENT. ⭐ **The `FD_ISSET` read is the stronger candidate** (different fault primitive, different oracle) **and `ext/sockets/` has ZERO rows** (F59). ⚠ A fifth cluster is untouched by the commit entirely: **15 sites in bundled FastCGI** — a provenance question before it is a row (`.tasks-php/probes/fdset_census.sh`; 47 sites / 11 files) |
| ~~51~~ | ✅✅✅ **CLOSED — EXECUTED AND GATE-VERIFIED, `TASK_PHP_033`.** `verdict PASS`, contract `a5dfc7d473a2`, brackets `66/0` + `12/0`, and **all eight predicted audit numbers came out FIRST TRY** (`spellings` 4→**12**, `pairs` 12→**36**, `present` 0→**22**, `required_pins_nothing` **0**, `required_absent` **2**, `forbidden_hits` **0**), with both absences exactly `required[1].rust` on the two safe rungs. ✅ Manager-verified from `results-php/gate/`, not from the report. ⚠ **`ph29` is now SEARCHABLE — not discharged and not enforced**; the spellings debt is `TASK_PHP_035`. ⚠⚠ **`.memory-php/02-ladder.md` is STALE on this row** (`4 / 4 / 0`; the record says **12 / 4 / 8**) — manager-owed. ⚠ F72's stated CAUSE was wrong and is corrected there. **The original framing, kept for the record:** | The call: `ph29`'s `required` entries are **spellings with the ticks dropped**, not a `p05`-style prose-only declaration — **7 of 8 spans already pin a rung**. ⚠ **But the repair is not "add backticks"**: `required[0]`/`required[1]` carry **no English at all**, so two of the eight must be respelled (`.wrapping_add(1)`, not a binding name; `read_buf[recvd] =`, not a char literal) and one owes a scoping sentence. ⚠ **The original framing below is half wrong and is kept for the record**: `required` **cannot fail the gate BY DESIGN** (its scope lives in English — `idiom_audit`'s docstring argues it at length), while `forbidden_hits` **does** fail, so *"a validator that cannot fail"* named a deliberate asymmetry rather than a defect. What was really wrong is that ph29 pins **nothing positive at all**, which makes its admissible class **undecidable by grep** — ▶ so the edit buys the **spread search**, and `ph29` becomes *searchable*, not *enforced* | `_028`, ✅ manager-verified from `.idiom_audit` in the gate records: `p05` **0**, `ph00-smoke` **0**, `ph03` **11** (6 forbidden), `ph16` **23** (10), **`ph29` 4 — and all four are `forbidden`, with ZERO `required`.** So every candidate passes and nothing is pinned: **a validator that cannot fail**, which is `PROTOCOL_PHP.md` §H's exact target and F52's family. ⚠⚠ **This corrects `TASK_PHP_028.md` §4.3, which named `ph03`** — `ph03` searches fine and needs **no** `spec.md` edit. ⭐ **The lesson is rule 14 in its hardest direction: I copied a TRUE sentence onto the WRONG SUBJECT.** The sentence is `p05`'s, it really is in the tree (inside `ph16`'s hashed `why`, printed by `check.py` on every `ph16` run, which is where I picked it up), and `spellings: 0` really did happen — **so nothing about the claim read as invented.** ⚠ Pinning `required` spellings on `ph29` is a `spec.md` edit **inside a hashed block** and costs a `ph29` re-gate |
| ~~52~~ | ✅✅ **DECIDED — F74, and by a NULL CONTROL the project already ships.** ▶ **Quote `A1` (kernel-exclusive, per call) and NAME it**, because `identity` makes `verus − unsafe` a null whose true value is 0: **family A is `0.000 %` across all 39 rows of both programmes, family B reaches `+3.65 %` (PHP) / `+5.01 %` (PAT)**, and on `ph03`/`small.bin` **B's null exceeds the effect B is measuring**. ⚠ **With its condition**: A is the headline only where the two compared cells have comparable callee share — **31 sign flips in 310 comparisons, every one above `Δinside_share` 0.02 and none below.** ⚠⚠ **The item UNDERSTATED the problem**: not two statistics over two rows but **SIX over two families, THREE in use across five published headlines** — `ph07` publishes `A3`, which matches none of its own row's 16 computable figures. ▶ Owed: `ph64`'s box figure → **`+17.47`**; `ph07`'s `A3` labelled; F71's `−24.63 %` labelled **family B** (it STANDS — A is blind to `safe_naive`'s allocations). ⚠ **No re-gate, no re-measure, no `harness/` edit** — it is which committed number a document quotes. **The original framing:** | `_028` §3. `ph07`'s bound is published from the **marginal** statistic and `ph16`'s from the **per-call** one, and on `ph16` they differ by **0.72 pp — 59 % of the figure** (`−1.22 %` per-call vs `−1.94 %` per window byte). ⚠ **So the two rows' bounds are not comparable as published**, which is exactly what `fixed-R4 bound` exists to prevent. ⚠ **Not a defect in either row** — both are internally consistent and `_028` shipped **all three** statistics precisely because they disagree. **What is owed is one sentence in `.memory/02-bench-rules.md` or `PROTOCOL_PHP.md` naming THE statistic a `fixed-R4 bound` is quoted in**, and a note on `ph07` if it is the one that moves. ⭐ **Cheap, and it gets more expensive with every row published** |
| 53 | ⚠ **`ph16`'s `safe_naive.rs` AND `safe_tuned.rs` STATE THE WRONG MECHANISM IN COMMENTS, AND FIXING A COMMENT COSTS A 28-CELL RE-MEASURE** | `_028` §2, which **retracted `ph16`'s own `NOTES.md` §8b** and landed that retraction: the R2→R3 **guard** respelling emits **byte-identical machine code in both directions** (`r3_guard_r2`, `r2x_guard_r3`), so the gap is the **subslice + `chunks_exact`**, not the guard. ✅ **The engineer correctly did NOT touch the `.rs` files** — they are measure-pinned. ⚠ **Manager's call, and F15's shape exactly**: a prose fix costing a corpus-wide re-measure, whose stated mitigation is already protocol — **batch it, never land it alone** (`PROTOCOL.md` rule 6). ⭐ **Do it the next time `ph16` is re-measured for a substantive reason**, and not before |
| ~~54~~ | ✅✅ **DISCHARGED 2026-09-12 — `PROTOCOL_PHP.md` §B1a, AND ITS COST OBJECTION WAS MEASURABLY FALSE.** ⭐ **`PROTOCOL_PHP.md` is in NO DIGEST** — not `contract_sha256` (which is `sha256` of the ```` slb-contract ```` block **and nothing else**, `check.py::read_contract`) and not `source_sha256`'s path set — ⚠ **which is NOT “40 paths”; that figure was MEASURED ON ONE ROW AND PUBLISHED AS THE FIGURE.** It is **per-row: ph00 29 · ph03 33 · ph07 38 · ph16 38 · ph29 39 · ph45 42 · ph53 41 · ph64 40** — and `ph64` is the 40, which is how it happened (F12's shape, in miniature). ✅ **The CONCLUSION is unaffected and independently confirmed: no digest key in ANY record names `PROTOCOL_PHP.md`, `CATALOGUE.md`, `SOURCES.md` or a manifest**; `66/0` and `14/0` immediately after the edit confirm it. **The item stood three rounds on a six-row-re-gate cost that does not exist.** ▶ **The decision: NOT a refusal** (admission is C-side only), **the row declares the allocation order**, **cross-language figures are labelled** — ⭐ **plus the positive half the item never stated: R2-vs-R3 and R4-vs-R5 allocate IDENTICALLY, so the allocator term CANCELS and the `fixed-R4 bound` is UNAFFECTED.** ⭐⭐ **That is the same boundary F89 and F91 reached independently** — two threads, three methods, one axis. ⚠ It **gets worse on the temporal axis**: intrusive containers allocate per element, so expect the precondition to fail on most `E*` rows. **The original text:** | ⚠⚠ **§B2's ORIGINAL WORDING** | F71, `TASK_PHP_032` §5, **UNREVIEWED — and the engineer flagged the alternative for a reviewer to push back on, which is the right shape.** §B forbids a Rust rung from linking the shim, so on `ph64` the **C rung allocates `2n+2` blocks per call and the Rust rungs count**: **60 % of the C's instructions are in libc `malloc`/`free`.** ⚠⚠ **So the C-vs-Rust column on this row is not a safety comparison** — it is largely a comparison of an allocator against arithmetic. ✅ **Not a defect in the row**: the engineer took the *"say so loudly"* option and every figure is published in `marginal_ir_per_call`. ⚠ **What is owed is a §B2 condition naming the O(1) precondition**, and a decision on what a row does when it does not hold. ⭐ **It gets worse, not better, with the temporal axis** — intrusive containers allocate per element, and `.memory-php/01-extraction.md`'s F1 says the temporal defects live in exactly those containers |
| ~~55~~ | ✅✅ **DISCHARGED 2026-09-12 — `PROTOCOL_PHP.md` §H1.** ⛔ **Its headline was FALSE**: *"the rule is real and cheap to state and there is **nowhere cheap to state it**"* — there is, and it is the file the item's own candidate list names. **See item 54 for the measurement.** ⭐ **And §H was not merely *a* candidate home — it is the home whose stated purpose this rule instantiates**: in `forbidden` a backticked character literal is **a ban that CANNOT FIRE**, which is §H's exact target. ⚠ **The php-only SCOPE objection stands and is ACCEPTED rather than solved**, with the condition that would move it: reach is **0 of 33 PAT**, so nothing is owed a PAT author today, and `charlit_reach.py` is the check that would say otherwise. **The original text:** | ⚠⚠ **F73'S WRITING RULE — ORIGINAL FRAMING** | F73. The natural place is the **named-spelling standard**, but that paragraph lives **inside every pattern's `why`, i.e. inside `contract_sha256`**, and it is byte-identical across six patterns — so writing one sentence into it costs a **six-row re-gate on the PHP side and 33 on PAT**. ⚠ The rule is real and cheap to state and there is **nowhere cheap to state it**. Candidate homes, none chosen: `PROTOCOL_PHP.md` §H (php-only, so PAT authors never see it); `.memory-php/` (authoritative but php-only, and needs review first); a `harness/` docstring (**forbidden — hashed**). ⭐ **The general shape is worth more than this instance**: a convention that binds BOTH programmes has no unhashed shared surface, which is why `CLAUDE.md`'s top table exists and why it keeps growing |
| 56 | ⚠ **A BARE-IDENTIFIER PIN IS A WEAK PIN, AND NOTHING MEASURES PIN QUALITY** | F72. `ph29`'s `required[3].rust` is `real_size`, which occurs **3–7 times per rung** — it pins *"this name occurs"*, not a construction. Compare `.wrapping_add(1)` and `emalloc(to_read + 1)`, which pin **exactly one line per rung**. ⚠ `idiom_audit` reports `pins_nothing` and `absent` but has **no notion of how tightly a present pin binds**, so a one-line pin and a seven-hit identifier are indistinguishable in the record. ✅ **Not a defect in `ph29`** — the entry's English carries the §B1.3 argument and the pin is honest; `TASK_PHP_033` is told explicitly not to strengthen it. ▶ Open: is hit-count-per-rung worth reporting beside each present pin, and **would it be a number nobody acts on** — the exact trap `idiom_audit`'s own docstring records about the printed `2` that moved nothing for three tasks |
| 57 | ⚠⚠ **`ph16`'s `controls/spellings.py` CARRIES TWO REAL DEFECTS, BOTH LATENT, AND FIXING THEM COSTS A `ph16` RE-GATE** | F79, `_035`, found by its own §H negatives and **guarded in `ph29`'s copy only**. (a) ⭐ **`kernel_fingerprint` returns `(0, 'd41d8cd98f00')` — the md5 of the EMPTY STRING — for a binary that does not exist**, because `disasm` ignores `objdump`'s return code, **so two missing binaries compare EQUAL on the one function whose job is to decide byte-identity.** (b) `disasm`'s needle is a **bare substring**, so a crate named `nokernel` fingerprints its own `main`. ✅ **Latent, not live, on `ph16`** — every call site there is downstream of a build whose success is checked — which is why `_035` correctly left it alone rather than widening its scope. ⚠ `controls/*.py` is in `source_sha256`, so the fix **costs a `ph16` re-gate**; batch it with any other `ph16` work. ⭐ **The general shape: a control cloned between rows carries its defects with it, and only the row that writes NEW negatives finds them** — `ph16`'s suite was 54 cases and did not catch these; `ph29`'s 75 did |
| 58 | ⚠⚠ **THREE OF SIX BUILT ROWS HAVE AN UNSEARCHED R4 ENDPOINT, AND F77 JUST PROVED THAT MATTERS** | `ph03`, `ph64` and now `ph45` (F80). ⚠ Until `TASK_PHP_035` this debt looked cosmetic, because `ph07` and `ph16` both searched their R4 side and found it **degenerate**. ⭐⭐ **F77 killed that reading**: `ph29`'s `r4_fold_iter` verifies byte-identically and is **5.63 pp cheaper**, so a `fixed-R4 bound` over an *unsearched* endpoint is a bound over a number nobody has tried to move. ▶ **`ph45` is the cheapest of the three to search** (its `spellings.py` was never built, so there is no declaration repair to do first) and `ph03` is the oldest. ✅ **`ph45` WAS SEARCHED at `_037` (F87) and BOTH its endpoints moved.** ⚠⚠ **But the debt did not shrink: `ph53` shipped without a `spellings.py` too.** ▶ ✅ **`ph53` WAS SEARCHED at `_042` and BOTH its endpoints move (F100), so the residue is now `ph03` and `ph64` — and 3 of 3 rows properly searched had a moving endpoint.** Item 80 carries the detail. ⚠ Each costs a re-gate; **batch each row's owed prose fixes into the same run** — the lesson `TASK_PHP_033.md` learned by failing to |
| 59 | ⚠ **A SIGNED OVERFLOW AT `mbfilter_htmlent.c:193`, IN `ph45`'s OWN FUNCTION, UNTRACED TO ANY FIX** | F80, `_036`'s own find, **reported and not pursued** — the right call, since chasing it was outside a build task's scope. ⚠ It is **inside the function `ph45` extracts**, so it is not merely adjacent: the row's benign corpus must be shown not to evaluate it (F46's UB-free-trigger rule), and `_036` does not say whether that was checked. ▶ ✅✅ **ASKED AND ANSWERED — AT `TASK_PHP_037` §4, AND THE ITEM NEVER RECORDED THAT IT WAS CLOSED.** ⛔ **`inputs/gen.py` neither edited nor run** (`sys.dont_write_bytecode` set before import; all eight blobs re-hashed before and after, none moved). **TWO independent decoders sharing no constant**, agreeing on values, entity tables and `html_entity_chars`. ⭐⭐ **And decoder B tracks the accumulator in unbounded integers AND wrapped 32-bit SIMULTANEOUSLY — identical on both inputs**, which is the **direct** statement that `:193` never overflowed, **not an inference from a margin.** ⭐⭐⭐ **THE SENTENCE THAT MUST BE LANDED, because the margin alone reads as *"it cannot happen"*: the guard is NOT VACUOUS A PRIORI — the `buffull` arm permits a 13-DIGIT numeric body, `~7.4e12`, THREE ORDERS OF MAGNITUDE ABOVE `INT_MAX`. ▶ So `:193` CAN overflow; what keeps this corpus safe is the TOKEN GRAMMAR, not the arm bound.** ⓘ Manager re-read `:193` in the pristine tarball independently (`ent = ent*10 + (buffer[pos] - '0')`, no cap inside the loop) — a third confirmation. ▶ **OWED: PROSE ONLY.** `NOTES.md` is in the gate digest and **not** the measurement digest, so landing it costs **one `ph45` re-gate and no re-measure** — **batch with items 63 and 65.** **The original ask:** ⓘ Distinct from the **stack OOB write at `:123`** in the *encode* half (F75), which is also uncatalogued and which the row deliberately does not lift |
| 60 | ⚠ **`harness/check.py`'s NULL-CONTROL TABLE JUSTIFIES ITS WORST CELL WITH BYTE-IDENTITY THAT THE ROW'S OWN PIN DENIES — PAT-SIDE, FOR ROUTING** | F82. The docstring is **more careful than my probe was** — it corrects the table for **mode**, **opt level** and **input**, and warns *⚠⚠⚠ A NULL IS A PROPERTY OF A CELL. DO NOT MAX IT OVER MODE, OVER LEVEL, OR OVER INPUT.* ⚠ It does not correct for the **identity level**: its worst quoted cell, **`p25 large +269.52`**, is on the row pinned `` `O0: norel`, `O3: norel` ``, while the table is justified by *"`identity` forces R4's and R5's kernels to agree byte for byte."* ✅ **The number is RIGHT and the justification is WRONG** — p25 rescues it by a different route its own identity note records (189 non-pad instructions and identical byte count in both cells). ⚠⚠ **`harness/` is FROZEN**: one sentence costs a 33-pattern re-gate, and `results/SYNTHESIS.md` is the PAT-side authority, not this file. ▶ **Reported, NOT fixed.** ⭐ The general shape is the same as F82's own: **a correct number whose stated reason is false survives every check, because checks test numbers** ⭐⭐ **AND F84 SUPPLIES THE MISSING MECHANISM FOR THE TABLE'S LARGEST CLASS.** That docstring records *"1.00 ≤ |null| < 2 in 35 cells, **34 of them exactly −1.00**"* without explaining the `−1.00`. ⛔ **I answered it wrongly and `TASK_PHP_038` §4.2 supplied the real one: it is exactly ONE INSTRUCTION PER KERNEL CALL IN `main`** — `main_exclusive_ir` Δ/n = **−1.0000** on `ph00` and `p11`, **already in every committed measurement record and needing no callgrind at all.** ⭐ **So the mechanism for `check.py`'s largest documented class IS now on file, just not the one I proposed** — and the routing item stands unchanged, since `harness/` is frozen either way |
| 61 | ⚠⚠⚠ **THE SHARED `why` BLOCK ARGUES R4 ADMISSIBILITY FROM AN ANTECEDENT THAT IS FALSE ON THREE OF SIX PHP ROWS** | F82. The block — **byte-identical across all six PHP rows and all 33 PAT rows** — says *"All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not merely a program that MAY use `unsafe`: it is a program that must have a byte-identical R5 twin that Verus verifies."* ⚠ **`ph07` pins `norel`, `ph45` and `ph64` pin `differ`.** It is **PAT-side boilerplate carried into a programme where it does not hold**, and it is the step by which `.memory/01-ladder.md` disqualifies unverifiable R4 candidates — so on those three rows **that disqualification has no stated basis**. ⚠⚠⚠ **AND `TASK_PHP_037` MEASURED THE STRONGER FORM: the wider bar is NECESSARY here, not merely permitted. NO twin on `ph45` compiles byte-identically — INCLUDING THE SHIPPED RUNG'S OWN (318 instructions against 320) — so under the shared block's own admissibility argument THIS ROW HAS NO ADMISSIBLE R4, NOT EVEN THE ONE IT SHIPS.** My task file said *"need NOT"* (permission) and that understated it. ▶ An R4 candidate on `ph45`/`ph64`/`ph07` need only **verify**; their searches are **wider than `ph29`'s** and F77's method is not the binding constraint — **F87 result 1 is a direct consequence.** ⚠ Fixing the sentence is a **six-row PHP re-gate** (it is inside `contract_sha256`) — ✅ **and THAT HALF IS CONFIRMED: `idiom.why` really is in the contract, measured at 15 028 B on `ph64`.** ⛔ **But item 55's *"no unhashed shared home"* is WITHDRAWN — `PROTOCOL_PHP.md` is in no digest at all** (item 54), so **one** of the two surfaces is free and one is not, and `STATISTICS_001 §6` collapsed them into one false sentence. ⭐⭐ **AND F91 GIVES THESE ROWS A SECOND, INDEPENDENT CONSEQUENCE: they also have NO NULL CONTROL.** `ph45` and `ph64` fail F82's `Δnopad == 0 and Δbytes == 0` predicate at **every** cell, so the frozen harness's *"compare against that pattern's OWN R5 − R4 null before quoting it in a band"* **cannot be satisfied on them** — and **`ph64` is the one row whose headline is family B.** ⚠⚠⚠ **AND THE COUNT PREDATES `ph53`: IT IS 4 OF 8, NOT 3 OF 6** (`TASK_PHP_042` §7.3, measured over all eight php `spec.md`s) — `O3` is `exact` on `ph00`/`ph03`/`ph16`/`ph29`, `norel` on `ph07`, **`differ` on `ph45`, `ph53` AND `ph64`.** ▶ **So the shared block's antecedent is now false on HALF the corpus**, and ⭐ **`ph53`'s search was WIDER for exactly that reason** — an R4 candidate there need only **verify**, which is what let nine twins in. ⚠⚠ **THE COUNT DIFFERS BY PREDICATE AND BOTH ARE RIGHT: THIS ITEM'S ADMISSIBILITY ARGUMENT TURNS ON BYTE-IDENTITY, SO IT IS THREE ROWS (`ph07` `norel`); THE MEASUREMENT QUESTION TURNS ON THE COUNTS, SO IT IS TWO (`ph07` IS RESCUED).** ⛔ **Do not "reconcile" them** |
| 62 | ⭐⭐ **FAMILY C — `kernel` INCLUSIVE `Ir` — STRICTLY DOMINATES FAMILY B AND IS NOT BUILT** | F83, `.temp/mgr172/inclusive_ir.py`. `callgrind_annotate --inclusive=yes` is in the **pinned** valgrind 3.27.1, so the kernel's whole **call tree** is computable **from ONE run** and **without touching frozen code** — `measure.py::callgrind_ir` records exclusive only, for two needles. ✅ **Same coverage as B with one fewer error source**: on `p25/large` B carries **+101.65 `Ir`/call** that C does not, and on `ph03` the two agree to **0.03 %** and **exactly**. ⚠⚠ **It solves NOTHING about attribution** — the allocator work *is* in the call tree, so C includes it and reads B's number; **I drafted the opposite claim and had to retract it inside the same finding.** ▶ Buildable as a **php-side control**: six PAT patterns' `controls/` already call `objdump` directly, so one calling `callgrind_annotate` is the same shape, and `controls/*.py` costs **one gate re-run and no re-measure**. ⚠ **Its own null must be measured before it is believed** — C is *attributable*, not *clean*. ⚠ Not started; `TASK_PHP_037` has since landed, so the one-agent slot is FREE. ⭐⭐⭐ **RE-SCOPED AGAIN, 2026-09-12, AND THIS TIME BACK TO THE REVIEWER'S RULING: `TASK_PHP_039` (F92) ANSWERS ITEM 68 **NO**, so F90's re-scoping is WITHDRAWN and `_038` §6's decision STANDS — C IS THE PRECONDITION.** ⭐ **And `_039` §12.4 adds POSITIVE evidence for C that nothing had**: F85's family C reads **+14.554** on `ph29/small` `c-gcc` vs `safe_naive` against `_039`'s 6400-iteration **grand B of +14.319 ± 0.15** — **agreement to 0.235 pp, from ONE run**, against the 22× cost of a pin that would match it. ⚠⚠ **BUT TEST TWO THINGS FIRST, AND THE SECOND IS NEW (F91).** (i) **its own NULL**, as this item already demanded; (ii) ⛔⛔ **its own SENSITIVITY** — F91 measured family B's on the cells where the R4/R5 kernels differ by a **known** static count and found `|B/A|` **49.6–393.9×** in the small-Δ regime. **C's is UNMEASURED, and the prediction is that it FAILS THE SAME REGIME**: on `ph03/small`, a **byte-identical** pair, C reads `+265.924` against B's `+266.000`. ▶ **If C also loses a 2-instruction difference, then C is the right SECOND column cross-language and NOT a substitute for A same-language — which is F91's axis, and it would make this item's deliverable narrower and cheaper.** ⓘ **The null alone is one-sided (F82); measure both in one go.** ⭐⭐ **AND F85 ALREADY USED C FOR REAL**: it re-derived `ph29`'s cross-language flips against C on the strength of `inclusive_ir.py` alone, which is the argument for building it properly rather than re-running a probe per question ⚠⚠⚠ **AND `TASK_PHP_038` §6 RULES IT A PRECONDITION, NOT A NICE-TO-HAVE**: its decision is *publish both, and the second column MUST BE C* — **drop W1 as corroboration**, because §1.3 measured that C and W1 are **nested scopes of ONE run** separated by a language-dependent fixed term of **≈176 k `Ir`**, so quoting them as independent was wrong. ▶ **And family B is now disqualified TWICE OVER** — F84 (it misses real work) and F88 (it is one unstable draw). **So C is the only admissible second column, and it is the one thing not built.** ⚠⚠⚠ **RE-SCOPED BY F90, WHICH DISAGREES WITH THAT RULING: of the four families B is the ONLY one with no DEFINITIONAL gap** — A is blind to callees, C is blind to `main` (the `−1.00` class proves it), W1 carries a ≈176 k `Ir` language-dependent fixed term, and **B's flaw is `probe_iters`, a parameter.** ▶ **C is still worth building — it is the only *attributable* column that sees callees, and it is what adjudicated F85 — but it is NO LONGER the answer to B's instability. Try item 68 FIRST.** ⚠ Also owed by that decision: **name `probe_iters` in the label** of any B figure that survives, since F88 makes the draw part of the number's identity. ⛔⛔ **NEW REQUIREMENT, `TASK_PHP_049` §3.3 (2026-09-13): FAMILY C MUST BE BUILT FOR **BOTH** C CELLS PER ROW — `c-gcc` AND `c-clang` — NOT ONE.** Splitting F85's 29 cross-language flips by baseline gives **21 `c-clang` to 8 `c-gcc`**, so a gcc-only family C **re-adjudicates 8 flips and leaves 20 untouched**, which is the wrong 8. ⭐ **AND `ph29` SHOWS C IS WORTH IT AND ALREADY DECIDED SOMETHING**: the gcc→clang gap there is `−28.09 %` (A1) / `−27.01 %` (C) / `−26.74 %` (W1), and **W1's immunity to symbol boundaries is what refuted the inlining-attribution confound** — without building anything. ⚠ **The other seven rows have no C-cell profiles.** ⓘ `_049` §5's most promising unchased lead: **`O3/whole`'s `main_exclusive_ir` already contains the inlined kernel on every cell and may be a cheap family-C proxy** — ⛔⛔ **CHASED 2026-09-14 AND IT DOES NOT WORK.** Tested on `ph29`, the one row where family C is measured: the proxy gives **`−32.34 %`** where family C gives **`−27.01 %`** (A1 `−28.09 %`, W1 `−26.74 %`) — **a 5.3 pp error, ~20 % of the effect.** ⭐⭐ **AND THE REASON IS STRUCTURAL, SO NO CALIBRATION FIXES IT: `main_exclusive_ir` at `O3/whole` IS A W1-LIKE QUANTITY, NOT A C-LIKE ONE** — it includes `main`'s own driver work and everything inlined and **excludes nothing**, whereas family C is *the kernel symbol inclusive of its callees*. **Their relationship is governed entirely by `inside_share`**: high-share rows nearly coincide (`ph52` `−1.2 … −4.3 %`, `ph53` `−0.1 … +4.4 %`) while **`ph45`'s Rust cells read `+847 %` to `+1168 %`**, its levers living in the callee `dec` at `inside_share` ≈ 9.5 %. ▶ **So the proxy is accurate exactly where family C is LEAST needed and useless exactly where it is MOST needed. Item 62 still needs the real thing.** ⚠ **And a hypothesis of mine died in the same probe**: from `ph29` alone I read *“clang exploits cross-TU visibility at `whole` and gcc does not”*; across 8 rows the means are `c-clang` **−1.05 %** against `c-gcc` **+0.74 %** with spread `−5.97 … +8.98` on both — **the spread swamps the means and `ph29` is an outlier.** ⭐ **Second time in two days a `ph29`-shaped n = 1 reading of mine has not survived n = 8** |
| 63 | ⚠⚠ **A THIRD DEFECT IN THE SHARED `spellings.py` MACHINERY, LATENT IN `ph29`, AND F79's TWO FIXES DO NOT COVER IT** | F87, `TASK_PHP_037` §6.2, found by its **128-case** §H suite (`ph29`'s bar was 75). ⚠ **`twin_identical` still compares two `(0, md5(""))` rows EQUAL** — F79 guarded `kernel_fingerprint` and `disasm`'s needle but **not this**, so the same *"two missing binaries are byte-identical"* hole survives at a second call site, in the one function whose whole job is to decide byte-identity. ✅ **Latent on `ph29`** (its call sites are downstream of a checked build), and **`_037` correctly declined to widen its scope into another row's control.** ⚠ Costs a `ph29` re-gate → **batch with open item 56** (`ph29`'s weak bare-identifier pin), the only other `ph29` prose debt. ⭐ **The shape is item 57's exactly, one generation on: a control cloned between rows carries its defects, and only the row that writes NEW negatives finds them** — 54 cases missed two, 75 missed one, **128 found it** |
| 64 | ⚠⚠ **`ph07`'s AND `ph03`'s CROSS-LANGUAGE FLIPS ARE NOT RE-DERIVED AGAINST FAMILY C** | F85. ✅ `ph29`'s five flips **survive** C and W1 — three statistics agreeing to ~2 pp against A — and its two non-flipping controls agree across **all four** families, **so the `ph29` half is settled.** ⚠ `ph07` (6 flips) and `ph03` (6) are still measured **against family B only**, and F84 showed B confounded in both directions by up to ~266 `Ir`/call. **The mechanism is the same and `ph29` makes it likely, which is exactly why it must be measured rather than assumed** (F78's lesson). ▶ **Cheap**: their binaries are on disk and md5-verified, and `.temp/mgr172/sweep_cg.sh` is the single regeneration entry point — add four C cells per row. ✅✅ **DISCHARGED at `TASK_PHP_038` §1.1, AND IT WENT FURTHER THAN THE ITEM ASKED: all 29 cross-language flips are now adjudicated against family C, not the 12 the manager had. `ph03` 6/6, `ph07` 6/6, `ph29` 16/16 SURVIVE; `ph00` 0/1 is REFUTED by C — so 28 of 29 survive.** ⭐ **The reviewer's OWN prediction that `ph03`'s would fail was refuted — C tracks B there to 0.006 pp.** ⚠ And it corrected the count: **29, not 28**, which the draft's own *"remaining 9"* already implied. ▶ **Quote F85 as *"29 of 38 flips are cross-language and 28 of 29 survive family C"*.** ⓘ `ph45` was excluded from both sweeps because it was being rebuilt; that is the only cell of the 38 still unadjudicated |
| 65 | ⚠ **`safe_tuned.rs`'s HEADER CITES A 68-BYTE LOG FOR FIVE NUMBERS IT DOES NOT CONTAIN, AND THE FIX COSTS A 32-CELL RE-MEASURE** | F87, `TASK_PHP_037` §9.5. `.temp/php36/logs-06-r3search.log` is **two lines** carrying two whole-program totals; **none** of the header's five candidate figures is in it, or anywhere under `.temp/php36/`. ✅ **A dangling citation, not a wrong number** — the `.rs` candidate sources survive so the figures are re-derivable, and two re-measured independently agree to **0.014 %**. ⓘ ⭐ **And `.temp/` is gitignored, so the citation was never reachable from a fresh clone at all** — which is the more general defect and applies to every `.temp/` citation in a committed file. ⚠ It is a `.rs` comment, i.e. **inside the measurement digest: 32 cells.** ▶ **Batch with F87 result 4's mechanism correction**, owed in the same file and the substantive one; **never alone** (`PROTOCOL.md` rule 6, item 53's shape). ⭐ **PARTLY DISCHARGED IN KIND, 2026-09-12**: this item's *general* defect — *"`.temp/` is gitignored, so the citation was never reachable from a fresh clone at all"* — was **acted on rather than argued about** for three artefacts. `STATISTICS_001.md` was committed last session; **`php_null.py` and `task_cost.py` are now committed in `.tasks-php/`** beside `quota.py`/`citecheck.py`, and **`.memory-php/02-ladder.md`'s citation of a gitignored DRAFT was re-pointed at its committed successor.** ⚠⚠ **For `task_cost.py` that was not optional: THE CLASSIFICATION *IS* THE ARGUMENT**, so a reader cannot audit *"3.0 tasks per row"* without it. ⓘ **Two `.temp/` citations remain in the authoritative layer** (`mgr170/null_control.py`, `mgr172/NOTES.md`) — `citecheck.py` reports both as *resolves TODAY*, which is the warning, not the fix. **The `.rs` half of THIS item is untouched and still costs a 32-cell re-measure** |
| 66 | ⭐⭐⭐ **IS `ph64`'s PUBLISHED B1 HEADLINE ONE UNSTABLE DRAW? — THE CHEAPEST NEXT MEASUREMENT IN THE PROGRAMME, AND UNTESTED** | F88, flagged by the reviewer rather than guessed. `probe_iters` is **`[100, 200]` in all seven PHP `spec.md`s and in `p11`** (manager-verified), so **every** family-B figure in both programmes is that one draw. On `ph29` the draw moves the level **32 %** and the published draw is the **largest of seven**. ⚠⚠ **`ph64` is the ONE ROW WHOSE HEADLINE IS B1** (F74), and it allocates **`2n+2` blocks per call** (F71, item 54) — so its per-window work must vary strongly, which is exactly the condition F88 identifies. ▶ **If `ph64`'s B moves like `ph29`'s, the draft §2 ban on family B is not a style rule, it is a correctness fix, and `ph64`'s headline needs restating.** ⭐ Cheap: `probe_iters` is a `spec.md` pin, the binaries are on disk, and `.temp/php38/draws.py` already does the sweep. ⚠ **`ph64`'s `NOTES.md` is in the gate digest but NOT the measurement digest**, so restating costs one re-gate. ✅✅ **ANSWERED — NO (F89).** Nine 100-wide draws: the headline moves **0.07 pp on a +17.08 % effect** and the published draw is **inside** the range; the level moves 6.75–7.04 %, so the heterogeneity is real but **4.6× less than `ph29`'s**. ⭐ **The conditional does not trigger and the ban on B rests on F84's observation alone.** ⚠ **Both my declared expectations were wrong** (I predicted >10 %, and named an `ph03`-like falsifier; the truth is between the two rows). ▶ **What replaces the item: the draw cancels same-language (0.07 pp) and does NOT cross-language (8.63 pp), same row, same draws** ✅✅ **INDEPENDENTLY CONFIRMED AT 64× THE SAMPLE, `TASK_PHP_039` §8.4 (F93): `ph64`'s B1 headline sits `0.0087 pp` from the 6400-iteration population mean on a `+17.08 %` effect — 0.05 % relative, sharper than F89's own `0.07 pp`.** ⚠ **And F93 NARROWS the mechanism on the OTHER row**: `ph29`'s pin is a `+6.9σ` **start-of-run transient**, not a draw, so its cross-language B is off by **3.53 pp = 24.7 % of its own effect** against the population mean — **a bias, which is a stronger statement than F88's 32 % spread.** ⓘ `ph64`'s pin is `+1.76σ` with **no** transient, which is why the two rows' answers differ |
| 67 | ⚠ **THE `BLIND` CLASS HAS NO WORKING TEST, AND THE TAXONOMY INVERTS THE EVIDENCE ON 5 OF ITS 14 CELLS** | F86 as narrowed, `TASK_PHP_038` §2.4. `BLIND` was defined as *A reads exactly `0` while the whole-program figure does not*, which lumps **two opposite situations**: *A genuinely sees nothing* (`ph45`'s `+0.000 %` against a `+23.37 %` effect — the real thing) and *A correctly reads a true zero* (5 of 14). ⚠ The exact straddle predicate cannot cover it — `a_ratio == 1` fails a strict inequality — and F80's threshold calls **13 of the 14 "safe"**. ⭐ **The reviewer proposed a test, ran it, reported that its own must-fire negative FAILED, and shipped the failure instead of the test** — which is the right call and F79's rule (*a must-fire case that fires for the wrong reason is worth nothing*) applied to itself. ▶ Open: a test that separates the two, or an argument that the distinction is decided by `min(inside_share)` and needs none |
| ~~68~~ | ⛔⛔⛔ **ANSWERED **NO** — `TASK_PHP_039` (F92, F93). THE EXPONENT IS ≈ −0.5 ON BOTH ROWS.** Six fits on `ph64`/`ph29`, all in `[−0.649, −0.405]`, every one inside the estimator's calibrated −0.5 band and above the −1 band's upper edge. **So 1 % of `ph29`'s `+14.3 %` effect needs `W ≈ 6 474–17 321` = a 22–58× gate stage**, and F93 adds a **bias the lever cannot reach at all** (`lo` stays at 100, so widening keeps the transient inside the span). ▶ ⛔ **DO NOT SPEND THE RE-GATE — the adoption step was conditional on this answer and the condition is NOT met.** ▶ ✅ **`TASK_PHP_038` §6's ruling STANDS; item 62 is the answer; my F90 is REFUTED on its operative half.** ⭐⭐ **AND THE EXPERIMENT VINDICATED ITS OWN DESIGN CHANGE**: this item's `8.124 → 2.092 → 1.243` fall was **faster than 1/W**, which no sampling mechanism permits — and it was **the ESTIMATOR** (9, 4 and 3 disjoint spans, and the expected RANGE of `K` samples grows with `K`). **Holding `K = 8` and the `n`-range fixed, and reporting `SD` not `max − min`, is what made it readable.** **The original text:** | ⭐⭐⭐ **RAISE `probe_iters` ON ONE ROW — ORIGINAL FRAMING** | F90. `probe_iters` is pinned at **`[100, 200]` in all seven PHP `spec.md`s and in `p11`** (manager-verified), and family B's only documented flaw is the **sampling error that pin causes**: on `ph64`'s worst cross-language pair, **8.124 pp at width 100 against 1.243 pp at width 300** (disjoint spans). ⚠⚠ **I could not pin the rate** — sliding spans share draws and disjoint spans leave fewer samples, and **both biases point the same way**, so only the direction and the width-100 figure are trustworthy. ▶ **The experiment: widen the pin on ONE row, re-gate it, and measure what moves.** ⭐ **If the cross-language spread collapses, B needs no replacement and item 62 stops being a precondition** — which is the opposite of `TASK_PHP_038` §6's ruling and is why this is worth an hour. ⚠ **Costs**: `probe_iters` is inside `contract_sha256`, so **one re-gate per row** (7 PHP, 33 PAT) and it moves every `marginal_ir_per_call`; and B takes **two** runs, so width 500 is ~5× the callgrind time of width 100. ⓘ **PAT publishes in A and may not need it — that is a PAT-side call and `results/SYNTHESIS.md` is its authority, not this file** |
| 69 | ⚠ **`ph29`'s TRANSIENT HAS A SHAPE AND NO MEASURED MECHANISM** | F93, `TASK_PHP_039` §8.2, **flagged by its own author before anyone asked.** The measurement is *"the excess is confined to the first few hundred iterations and decays"* — `17.852 → 14.813 → 15.101 → 14.148`, `+6.9σ` against the other seven spans. ⚠ **The stated cause — allocator free-list warm-up against the C rung's `2n+2` per-call allocation — is a HYPOTHESIS and nothing profiled it.** It is *consistent* with the shape and with F71/item 54. ▶ **Worth measuring because it decides whether the transient is a property of `ph29` or of every row whose C rung allocates per element** — and item 54's own note says **most `E*` rows will be.** ⓘ Cheap: the profiles exist, and `main`/`kernel` exclusive `Ir` against `n` would separate allocator warm-up from anything in the kernel. ⭐ **Same discipline as F72 and F87 result 3: the conclusion lands, the mechanism is marked OPEN.** ⭐⭐ **AND `ph53` IS A THIRD DATA POINT WITH A MECHANISM ATTACHED** (`TASK_PHP_041` §7): its `[100,200]` span does **NOT** sit on a transient (`0.39–0.93 %`), and the three points *track per-window work heterogeneity* — **`ph29` heterogeneous and transient, `ph03` uniform and flat, `ph53` in between and flat.** ▶ **That is a candidate mechanism F93 did not have.** ⚠ **And it is consistent with the allocator story rather than a refutation of it**: `ph53`'s allocations are O(1) per call (§B1a) and it shows no transient, while `ph29` is the `2n+2` row. **What it adds is that heterogeneity predicts the transient at least as well as allocation count does** |
| 70 | ⚠ **FOUR OF SEVEN ROWS HAVE NO WIDTH→SPREAD MEASUREMENT, AND TWO SMALLER THINGS `_039` COULD NOT TELL** | `TASK_PHP_039` §13. (a) **`ph45`, `ph07`, `ph16`, `ph00` UNTESTED.** ✅ `ph07` publishes **A3** and `ph45` publishes **A1+W1**, so neither headline is family B — **but `ph16`'s and `ph00`'s B behaviour is simply unknown**, and `ph16` publishes **A1**. (b) ⚠ **whether `ph29`'s SD has a FLOOR above `W=400` — COULD NOT TELL**: measured `0.536 → 0.552` is flat, a −0.5 law predicts a 29 % fall, and the `K=8` SD's own noise is **27 %** — *"the two hypotheses are the same size as the error bar"*. ⓘ **It points the same way as the verdict either way**, which is why it is an item and not a blocker. (c) ⚠ **why `_039`'s LEVEL spreads are 1.25–2.2× the published ones while its RATIO spreads AGREE — UNTESTED**; needs contiguous `W=100` spans at low `n`, which its endpoint set does not carry. ⓘ Related: **F89's spreads were RANGES, not SDs**, which nothing said until `_039` §4.4 |
| 71 | ⓘ **ADJACENT: THE MEASUREMENT RUN MAY ALREADY CONTAIN THE POPULATION SLOPE, FOR FREE** | `TASK_PHP_039` §13.8, **reported and explicitly not proposed.** `measure.py` already runs every cell at the row's full `n_iters` (**25 000** on `ph29`/`ph03`, **1 500** on `ph64`), so a whole-program slope between a cheap small `n` and *that* run would be the population mean at almost no extra callgrind cost — **which is exactly what F93 had to spend 396 profiles to get.** ⛔⛔ **WHOLLY UNTESTED, AND IT TOUCHES FROZEN CODE**: `measure.py::callgrind_ir` records **exclusive** `Ir` for two needles and **may record no whole-program total at all**; adding one is a `harness/` edit = **33 PAT + 7 PHP re-gate** and a full re-measure. ▶ **Check whether the total is already there before considering anything else** — if it is, this is free; if not, it is the most expensive idea on this list |
| 72 | ⚠⚠ **`STATISTICS_001 §4`'s RULE IS OVER-BROAD, AND NARROWING A PUBLISHED RULE NEEDS REVIEW** | F91. §4 says **publish both, labelled, ALWAYS**. ▶ **F91's regime measurement says A ALONE SUFFICES where the comparison does not cross languages** — `|B/A|` is **49.6–393.9×** at every small-Δ cell, so no callee-inclusive statistic can resolve a 1–2-instruction difference, and `check.py`'s own operative rule says the same with a 66-cell census behind it. ⚠ **Narrowing is not a free edit**: rule 9 (F91 is unreviewed), and it changes what **every** row publishes. ⛔ **And it must NOT be narrowed into *"A always"*** — cross-language the callee work **is** the effect (`_038` §1.5), which is F85. ▶ **Two regimes, named, with the `Δnopad` calibration and its stated limit** (that count exists only for the `unsafe vs verus` pair). ⓘ **`STATISTICS_001.md` is in `.tasks-php/` and in no digest, so the edit itself is free** — the cost is the review |
| 73 | ⚠⚠⚠ **A CORRECTION CAN LAND IN `RECAP_PHP.md` AND NOT IN `.memory-php/` — AND `.memory-php/` OUTRANKS IT. NO CHECK CATCHES THIS** | Manager, 2026-09-12, found doing F91's rule-9 check. **Two live instances, both now fixed**: `02-ladder.md` said *"28 of the 38 sign flips"* while **`:446` of the same file** already recorded *"29, not 28"*; and it carried F82's family-A percentages **unlabelled per input** where `RECAP_PHP.md:2120` labels them and flags the defect. ⭐⭐ **THE SHAPE: a correction was landed as a NEW PARAGRAPH instead of APPLIED TO THE SENTENCE IT CORRECTS**, so the authoritative layer stated both numbers at once and a reader who stops at the first gets the superseded one **from the layer that supersedes everything.** ⚠ **It is the INVERSE of ordinary staleness** — the correction exists, it is just not where the authority is — and it is the second half of the size box's own *"THE LESSON IS THE PROPAGATION, NOT THE ARITHMETIC"*, which tracked a **wrong** number forward; this is a **right** number that did not propagate. ⓘ ⛔ **A checker was prototyped and NOT shipped, on a measurement**: the corpus's correction idiom is `X, not Y`, and over the whole authoritative layer that gives **1 idiom hit · 2 survivals · 1 real defect · 1 false positive** — it catches **1 of the 2** instances, because F82's unlabelled percentages are not written in that form at all. **A validator finding half of a two-member class at 50 % precision does not earn §H's landing cost today**; the measured reach is recorded so a later task decides with a number. ▶ **What is owed is a HABIT, not a tool: apply a correction to the sentence, in every layer that carries it** |
| 74 | ⛔ **`CATALOGUE.md`'s `u64` FOR `ph53` IS ADDRESS-DEPENDENT AND CANNOT BE THE `u64`** | F94, `TASK_PHP_040` §5. The entry says *`u64` = fold of the interface pointers read*. ⛔ **Pointers are addresses**, so that fold differs between rungs — and between runs — **for reasons no rung chose**, which is exactly what the cross-rung checksum exists to rule out. ✅ **Caught by the build brief before a line was written**, and replaced with an index/id/count fold. ⚠ **The row-7 build will ship the correct one, so nothing is blocked** — what is owed is the **catalogue** correction, because the next reader of that entry gets the wrong instruction. ⭐ **And ask the general question once**: `grep -a` the other 101 rows' `u64` lines for *pointer*, *address* and *ptr* — **if `ph53` is not the only one, this is a catalogue-wide defect and not a row's footnote** |
| 75 | ⚠⚠ **BOTH ROW-7 CANDIDATES' DECLARED TIERS ARE OPTIMISTIC, AND THE ENGINEER SAID SO UNPROMPTED** | F94, `TASK_PHP_040` §5.1. `CATALOGUE.md` declares `ph53` **`verbatim`**; the engineer would declare **`narrowed`**, because the mechanism needs **three frames in two files** (`zend_compile.c:2571` + `:2591` + `zend_operators.c:1534-1535`) and a `verbatim` claim is about a span that lifts byte-identically. ⚠ It judged **`ph52`'s optimistic too.** ▶ **The question is whether `tier` is SYSTEMATICALLY optimistic across the catalogue**, because `tier` is *"a COST STATEMENT, NEVER A FILTER"* (§0.2) and an optimistic cost statement mis-prices every future row's build. ⭐ **Two of two examined are wrong in the same direction**, which is the shape of a rule, not a coincidence — and it is `F81`'s shape exactly (*"measured NOTHING on 2 rows of 2 tested"*). ⓘ Cheap to test: `tier` is declared in each row's `spec.md` **inside the hashed block**, so re-declaring one costs a re-gate — **but MEASURING the mismatch costs nothing** |
| 76 | ⭐ **`ph52`'s R1h COLUMN IS PREDICTED `0.00 %`, AND THAT IS A RESULT, NOT A DISQUALIFICATION** | F94. Its R1h deletes one `zval_dtor` from an **error arm the benign corpus never runs**, so R1h should price **identically to R1** on every benign input — where `ph53`'s R1h costs an **O(n) `memset` on the benign path.** ⚠⚠ **The temptation is to read a `0.00 %` R1h column as *"the row measures nothing"* and drop the row. ⛔ THAT IS THE ADMISSION-BAR BIAS** (`CLAUDE.md` rule 6, finding 53): *"no column moves"* is a **FINDING, NEVER A KILL.** ▶ ⭐ **What it actually says is worth publishing: the upstream fix for a whole CLASS of defect — the unreached error path — is FREE, and the ladder can say so with a number.** ⓘ **UNTESTED**, and it is a *prediction* by the engineer, labelled as one. It becomes measurable the moment either row is built, so **batch the check with whichever is built second** |
| 77 | ⚠⚠ **A ROW WHOSE UPSTREAM FIX DOES NOT REMOVE THE FAULT CANNOT SHIP THE INPUT THAT DEMONSTRATES IT — AND THIS WILL RECUR** | F97(A), `TASK_PHP_041` §4. Stage **7h** requires **R1h clean on every input in `inputs/`**, and `ph53`'s R1h converts a wild dereference into a **NULL** one rather than removing it. ▶ **So there can be no `adversarial-deref.bin`, and there is not one.** ⭐ **`.memory-php/02-ladder.md`'s F31 binding on a real row for the FIRST time**, and the resolution F31 prescribes — put the demonstration in `controls/` — is the one taken (`controls/r1h_consumers.py`, corroborated by the gate's own `sanitizer_hardened.fired = False ×7`). ▶ **Open: is `controls/` the RIGHT home, or does stage 7h want a declared exemption?** ⚠ A `controls/` demonstration is **not in the published table and not in the gate's verdict**, so a reader of `results-php/tables/` cannot see the row's own fault. ⓘ **Any future row with a `d09cdd9f71f3`-shaped R1h hits this**, and F94 says that shape is not rare — an optimisation or a rewrite that closes a window without guarding the consumer |
| ~~78~~ | ✅✅ **ANSWERED AT `TASK_PHP_043` §3 — AT ZERO MEASUREMENT COST, AND ⛔ BOTH CANDIDATE AXES LOSE.** ⭐ **The free route existed**: the missing same-language cell is **9 cells, not 10** — ⚠ **my arithmetic used the superseded 28; the corrected split is 29 cross-language** — and it is **non-empty**, from `ph45` (7) and `ph64` (2). ⛔ **THE RIVAL IS REFUTED THREE TIMES OVER**: a flip *entails* callee divergence (`a·b < 0` on all 38), **so the rival's variable does not vary**; and on 3 cells with `Δnopad` ground truth the callee-inclusive column is wrong by **50–400×**. ⛔ **AND F91's AXIS FALLS TOO, ON ITS OWN TABLE**: all nine of its Result-5 cells are **same-language** and separate by **`|Δ|` magnitude**, not language. ⭐⭐ **THE WINNER IS A PREDICATE ALREADY IN THE AUTHORITATIVE LAYER**: the two-condition **`inside_share`** conjunction catches **all 9** cells, is **language-agnostic**, and is **already computed for every cell in every record** — so the condition is **measurable per comparison with no new machinery.** ▶ ⭐ **Item 62 (family C) gets narrower and cheaper as hoped, but by a different route**, and **F91's own open demand is now the only thing it must do first: measure C's SENSITIVITY, not just its null.** ⚠⚠ **SCOPE: two rows, both with known statistic pathologies** (`ph45` is the `inside_share` outlier; `ph64` broke §B1a). ⓘ **`ph00`/`ph03`/`ph07`/`ph16`/`ph29` contribute ZERO same-language flips — the phenomenon is concentrated on two rows** | F96 result 2, `TASK_PHP_041` `NOTES.md` §8h. **A and B agree in sign and closely in magnitude on EVERY cross-language cell of `ph53`** — the opposite of F85's regime — **and the stated reason is that §B1a's O(1)-allocation precondition HOLDS on this row, so there is no allocator term for B to include and A to miss.** ▶ ⭐ **If that is the mechanism, then F91's *same-language vs cross-language* axis is a PROXY for *callee work diverges vs does not*, and language is merely correlated with it** — which would make the rule **testable per row** instead of assumed per comparison. ⚠⚠ **This is evidence about ONE row and the engineer says so in those words**; F85's 29 flips are on rows where the C rung allocates and the Rust rungs do not. ▶ **The test: a row where the callee work diverges WITHIN a language.** ⓘ **If it holds, item 72's narrowing gets sharper and cheaper**: the condition becomes measurable rather than declared |
| ~~79~~ | ✅✅ **MEASURED AT `TASK_PHP_042` (F100), AND THREE OF ITS FOUR SUPPORTS FELL.** `+1.79 %` A1, **shipped checksum on all seven inputs**, and it drops the compare-only consumer **on the Verus side only**. ⛔ `ptr::eq` **does** express it on the exec side; the comparison **is** specified (`vstd/raw_ptr.rs:221`, probe verifying against its `ensures`) and what Verus refuses is the **`&T → *const T` coercion in BOTH spellings**; and *"zero trusted items"* is **reachable only in a control**. ✅ Shipped as three arms — `mu_ref_exec.rs` (cost), `mu_ref.rs` (`8/0`, the `p < MAXP` obligation gone), `mu_ref_cmp.rs` (a **must-FIRE** refusal that fires). ⭐⭐ **So F97's *two sound rules are jointly unsatisfiable* is now a MEASURED FLOOR: ONE trusted accessor is reachable on either representation, ZERO only in a control.** **The original text:** | ⚠ **A `MaybeUninit<&Iface>` REPRESENTATION — ORIGINAL FRAMING** | F98, `TASK_PHP_041` §8. The shipped R4/R5 carry **four** trusted accessors; this alternative carries **none** — *5 verified / 0 errors with zero trusted items* — and was rejected because **the compare-only consumer needs `ptr::eq`**, ⚠ **without measuring it.** ✅ **The rejection is honest and probably right** (the row ships both consumers on purpose, F96 result 1). ▶ **But a representation with NO TRUSTED BASE AT ALL is worth a number even if it can only serve one consumer** — the ladder's whole point is that the trusted surface is a measured axis, and **this is the first row where a zero-trusted-item R5 was in reach.** ⓘ Cheap: the file verifies already; what is missing is its cost and a statement of which consumer it drops |
| ~~80~~ | ✅✅ **DISCHARGED AT `TASK_PHP_042` (F100) — AND BOTH ENDPOINTS MOVE.** `r3_chunks_mask` **−32.08 %**, `r4_bitmask` **−11.40 %**, and ⭐ **`r4_bitmask_min` is CHEAPER *AND* SMALLER-SURFACE** (3 trusted call sites against 10, 2 accessors against 4, twin `32/0`). **Second row in either programme where both endpoints move.** ⚠⚠ **BUT THE R4 HALF IS UNDECIDED ON A PIN QUESTION — see item 83**: under `required[4]`'s backticked spelling the R4 endpoint is degenerate, under its English it moves, and the two disagree. ⭐ **The call to search this row BEFORE building row 8 was made on the signal that R3 measured dearest against a prediction of cheapest, and that signal was RIGHT.** ⓘ **Residue: `ph03` and `ph64`.** **The original text:** | ⚠ **BOTH ENDPOINTS UNSEARCHED ON `ph53` — ORIGINAL FRAMING** | `TASK_PHP_041` §8: **no `controls/spellings.py` was built.** ⭐⭐ **This is item 58's residue GROWING, and F77/F87 are why it matters**: `ph29`'s R4 endpoint moved **5.63 pp** byte-identically, and `ph45`'s R4 **AND** R3 both moved with the bound's **sign reversing** — so a `fixed-R4 bound` over an unsearched endpoint is a bound over a number nobody has tried to move. ▶ **Unsearched now: `ph03`, `ph64`, `ph53`**; `ph07`/`ph16` searched theirs and found them degenerate; `ph29`/`ph45` moved. ⚠ **`ph53` is the cheapest of the three** (fresh, and its `controls/` machinery is the newest and already carries items 57/63's fixes) **and it is the one whose predictions were most wrong** — **R3 came out dearest-but-one against a prediction of cheapest**, which is exactly the signal that a search would move something. ⓘ Costs a `ph53` re-gate — ⭐ **batch with item 79's measurement and F99's citation repair, all three being `ph53` debt** |
| 81 | ⚠⚠ **A FOURTH DEFECT IN THE SHARED `spellings.py` MACHINERY, AND THE PATTERN NOW HAS A LAW** | F101, `TASK_PHP_042` §8. **`kernel_fingerprint`'s digest is PATH-SENSITIVE** — `r3_oprec_slice` built in two directories whose paths differ by **38 characters** fingerprints differently, so a comparison that should read *byte-identical* reads *different*. ⚠⚠ **LATENT on `ph53`, LIVE on `ph29`**, where byte-identity **is a bar**: F77's headline is *"`r4_fold_iter` verifies BYTE-IDENTICALLY and is 5.63 pp cheaper"*, so a path-sensitive digest there is a **false negative on the one property that sentence rests on.** ⛔ **`ph29` was NOT edited** — reported for routing, the third time that call has been made correctly. ⭐⭐ **THE LAW, and it is monotone in suite size: 54 cases missed two (item 57) → 75 missed one (item 63) → 128 found one (`_037`) → 161 found this.** ▶ ***A control cloned between rows carries its defects, and only the row that writes NEW negatives finds them*** — **so expect the next row's suite to find a fifth.** ⓘ Costs a `ph29` re-gate → **batch with items 56 and 63**, which are the only other `ph29` prose debt |
| ~~82~~ | ✅✅ **CLOSED AT `TASK_PHP_043` §2 — CLOSEABLE WITH **NO ROW EDIT**, AND THIS ITEM'S OPENING SENTENCE SHOULD BE STRUCK RATHER THAN DISCHARGED.** ⛔ **F87 never made the claim** — its body contains **zero** A1-spread claims; ⭐ **the confusable twin that explains the misattribution is F87's OTHER `0.000000`, which is `max|A|` over 8 true-null cells.** ✅ **The authoritative layer is CLEAN**: `.memory-php/02-ladder.md:531` carries **both** scope qualifiers (*"ON THIS ROW"* **and** *"all NINE searched variants"*). ✅ **And both rows' `controls/spellings.json` ALREADY carry the reconciliation, in `statistic`, each naming the other row** — `ph45` *"A1 SEES 9.5 % OF THIS ROW"*, `ph53` *"`kernel` carries 89.5 %"* — **so a re-gate would buy nothing.** ⛔ **ONE edit owed, and it is free: `.tasks-php/STATISTICS_001.md:50`, which is LIVE** — its *number* is scoped but its **inferential role** is not, sitting under a column headed *"the measurement that shows it"* beneath a claim about A's **definitional** gap, which is the role `RECAP_PHP.md:2465` already withdrew. ⚠⚠ **Item 73's shape for the THIRD time: the correction landed in `RECAP_PHP.md` and not in the document `RECAP_PHP.md:82` calls *"the whole argument"*.** ✅ **Question 2 YES** — it is F86's **BLIND** class, named **15 lines from `ph45`'s own instance**, though over a different population. ✅ **Question 3 NO** — F91's `|B/A|` does **not** depend on it, verified from the table's population. ⭐ **Question 4: the pre-search predicate ALREADY EXISTS and is ALREADY PUBLISHED** — `.memory-php/`'s two-condition `inside_share` conjunction, and **both rows already obeyed it** (9.5 % → W1, 89.5 % → A1) | F100. `ph53`'s `a1_spread_pp` is **R3 `39.899657`, R4 `45.313019`** over 20 searched variants. ⛔ **F87's `ph45` headline was `0.000000` pp over nine variants against `66.7` pp whole-program** — published as *"A1 does not move"*. ▶ **Two rows, two opposite answers, same statistic.** ⭐ **And the reconciliation matters for F91**: F91's regime argument is that A resolves small code differences **because it is symbol-scoped**, and here that same property resolves respellings to **40 pp** — **the property working, where F87 read it as A being blind.** ⚠ **So what `ph45` actually showed is that ITS nine variants did not change the KERNEL SYMBOL's instruction count**, which is a fact about those variants, not about A. ▶ **Owed: restate F87's sentence so it says which**, and check whether F91's `|B/A|` regime claim depends on the wrong reading (**it should not — that claim is measured on the R4/R5 pair's `Δnopad`, not on respellings** — but say so rather than assume it) |
| ~~83~~ | ✅✅ **CLOSED AT `TASK_PHP_043` §1 — RULED (a), AND ITEM 83's OWN SUMMARY SENTENCE WAS WRONG.** ⛔ **The pin and its English do NOT disagree.** The entry's **leading appositive** — the clause defining what the backticked span IS — reads *"THE ONE-BYTE-PER-SLOT WITNESS"*, a **representation** (`unsafe.rs:230`, `[bool; MAXD]`, one byte per slot); the challenger is declared *"a u32 bitmask **instead of `[bool; MAXD]`**"*, one BIT per slot; and *"indexed SAFELY on purpose"* fails on a bitmask too, which performs no indexed access. ▶ **English 2-to-1 against the bitmask, AGREEING with the backticks.** ⭐ **So `idiom.required[4]` pins the REPRESENTATION, `r4_bitmask{,_pool,_min}` are OUT OF CONTRACT, `r4_endpoint_degenerate → true`, and every remaining in-contract R4 variant is DEARER (+0.50…+33.92 %).** ⛔⛔ **AND THE MANAGER'S ROUTE WAS AN OVER-READ**: I argued from the `why`'s *"WHAT NO GREP SETTLES"* sentence that English decides scope and backticks decide spelling — but that sentence's own final clause says *"which spelling … is a reading"*, and `harness/check.py::idiom_audit` (`:2198-2212`) measures the naive reading at **41 misses of 158 obligations, all 41 non-defects, 17 ANTI-signal**. ▶ **My route would have licensed (a) on every backticked `required` span.** ✅ Degeneracy **simulated through the row's own verdict functions** (`.temp/php43/item83_sim.py`, selftest PASS, 4 negatives), not inherited. ✅✅ **LANDED AT `TASK_PHP_044`: `contract_sha256` **`c41ffad2b795…` → `6924e66fde49…`**, `verdict PASS-WITH-BLOCKED-ROWS`, `failures []`, `complete_run true`, identity `O0 differ / O3 differ`, `problems []`, and **`r4_endpoint_degenerate true` / `r3_endpoint_degenerate false` / `cheapest_r3_in_contract r3_chunks_mask`** — all re-read by me from the regenerated records.** ⛔⛔ **AND `_043` §1.8's DRAFT WOULD HAVE ADDED THREE FALSE PINS** — see item **100**. ⓘ Reading (c) refuted as stated → item **91** | F100. The entry's backticked spelling is `` `wrote[i]` `` (an indexed **byte array**); its English says *"THE ONE-BYTE-PER-SLOT WITNESS … what makes R4's unsafe read DISCHARGEABLE"* (a **purpose**). **A `u32` bitmask satisfies the purpose — twins `31/0` and `32/0` — and does not carry the spelling.** ▶ **Under the English both endpoints move; under F72's rule that these entries are *spellings with the ticks dropped*, the R4 endpoint is DEGENERATE.** ⛔ **`idiom.required` is presence-only and CANNOT FAIL THE GATE**, so nothing mechanical was ever going to decide it, and `required_absent` correctly *reported* the absence on both winners. ⭐⭐ **This is F72 recurring at a new site and item 56's prediction coming true** (*"a bare-identifier pin is a weak pin, and nothing measures pin quality"*) — ⚠ **and it is the FIRST time the ambiguity decides a published RESULT rather than a pin's tidiness.** ▶ **The repair: restate `required[4]` so its spelling and its English bind the same thing** — one sentence inside the hashed block, so **one `ph53` re-gate** and no re-measure. **Batch with item 82's F87 restatement if that turns out to need a row edit.** ⚠ **Do NOT resolve it by weakening the pin to match whichever variant won** — `.memory/02-bench-rules.md`'s rule that a rung is never cost-selected applies to its pins too |
| 84 | ⚠ **A FIGURE F100 CITES IS NOT IN THE FILE F100 IMPLIES — F99's OWN RULE, BROKEN BY F99's AUTHOR** | `_043` §1.9. F100 quotes the twin verdicts **`31/0`** and **`32/0`** in a paragraph whose other fields come from `controls/spellings.json` — **and `spellings.json`'s `verus_checked` is a bare `true`, not a count.** The figures are in **`ph53`'s `NOTES.md:550` and `:741`.** ▶ **Repaired in F100 in place.** ⭐ **The item is the GENERAL one: F99's lesson is *name the file every field came from*, and the very next finding written after F99 did not.** ▶ **Owed: one sweep of the F88–F101 block for any other field quoted without its file.** ⓘ Free — `RECAP_PHP.md` only |
| ~~85~~ | ✅ **CLOSED AT `TASK_PHP_044` §6 — AND THE CENSUS WAS WRONG IN **BOTH** DIRECTIONS.** ⛔ **The *"twice independently"* claim was at **FOUR** sites, not the two I named** — `spec.md:23`, `:68`, ⭐ **`:570` (`provenance.fix_commit_note`, which my table omitted)** and `NOTES.md:146+:150` — **all four repaired**, found with a **wrap-tolerant** census because a line-based grep cannot match a phrase that wraps (F35's second half, and I had warned about it in the same task file). ⛔⛔ **AND A FIFTH IS UNREPAIRABLE → item 98.** ⛔⛔ **AND THE `:1945` → `:1944` HALF WAS MY OWN ERROR BILLED TO THE ROW**: the row never made it — `spec.md:514` says `zend_compile.c:1941-1945`, a **correct RANGE**, and `:1942`/`:1944` elsewhere. ▶ **`:1945` came from MY prose, `_043` corrected MY slip, and I wrote that correction into this file as a debt owed by the ROW.** ⭐ **F12's propagation shape with the roles inverted: a manager number travelled into a task file as a premise and came back as a phantom defect.** ✅ **R1h unchanged** — `d09cdd9f71f3`, still zero fuzz | `_043` §4.1. **`patterns-php/ph53-iface-tail-uninit/spec.md:23` AND `:68`** (`idiom.required[5]`) both assert the two-route exclusion of `be8daf1f47fa` and both name the screen route — **which F95's own repair demoted to `INAPPLICABLE-SAME-FILE`**, a label the screen prints as *"NOT exclusions … says nothing about these"*. ✅ **The exclusion STANDS on the tag walk alone**, so nothing about the row's R1h changes. ⚠ **Also `:1945` → `:1944`** for the inheritance-merge survivor. ▶ **BATCH WITH ITEMS 83 / 89 / 90 — ONE `ph53` re-gate, NO re-measure** (`idiom` is in `source_sha256`, not in any measurement digest; verified) |
| ~~86~~ | ✅✅ **DISCHARGED 2026-09-13 AND LEFT UNSTRUCK FOR FOUR DAYS, WHICH IS ITS OWN FINDING.** `width.py` is committed at `.tasks-php/width.py`, both `X3b` defects repaired, `--selftest` rc = 0; ⭐ **and the sweep this row asked for was finally run on 2026-09-17** — `mgr170`/`mgr172`'s five probes plus `sweep_cg.sh` promoted under `F147`, with `NULLCTL_001.md` as their evidence record. ⛔⛔ **THE REMEDY WAS RECORDED IN THE PROMOTED FILE AND NOWHERE ELSE**, so this row, `RECAP_PHP.md`'s F92 block, its own next line and `.memory-php/`'s law 11 all kept describing the pre-promotion state — two of them contradicting each other seven lines apart (`F131`, `F147`(e)). ⛔ **AND ITS SUCCESSOR IS OPEN: `width.py`'s header claims `X3` *"does not fail"* and it DOES (item 149).** ⚠ **The sweep is NOT finished — `probes/scratchdeps.py` prints 48 LIVE citations still; adjudicating them is item 148.** Was: | `_043` §4.3. `.temp/php39/width.py --selftest` dies with a **`ZeroDivisionError` at `X3b`** — ⭐ **and it crashes because its check now passes MORE cleanly than the guard expected**, which is a guard written for a noisier world, not a refutation. ⛔⛔ **The structural half is worse than the crash: F92 is PUBLISHED (`STATISTICS_001.md` §5 answers item 68 `NO`) and its only evidence is a gitignored probe.** ▶ **That is F99's defect applied to F99's sibling, and the fix is the one F99 prescribes: COMMIT the probe to `.tasks-php/`** beside the other eight checkers, **with the X3b guard repaired and its must-fire negative** (§H). ⓘ **Free — `.tasks-php/` is in no digest.** ⚠ **And sweep for the same shape: `_043`'s four probes, and `mgr17{0,2,3,4,5}`/`php3{8,9}`/`php4{0,1,2}`, are all gitignored** |
| 87 | ⚠⚠ **THE MANAGER'S `same_function` SOUNDNESS GUARD IS *NECESSARY, NOT SUFFICIENT* — AND IT IS F95's OWN DEFECT CLASS** | `_043` §4.2. My guard — *the matched hunk must contain no function-definition header before its first changed line* — **was made to accept a ZERO-LEADING-CONTEXT hunk as proof** (`.temp/php43/samefunc_hole.py`): with no leading context there is no header to find, so the check passes vacuously. ✅ **Live reach on the real corpus is `0`** — **latent, not live.** ⛔ **But the shape is exactly what F95 exists to name: a soundness test promoting an exclusion to a proof**, which is F95's headline defect recurring **inside F95's own repair**. ▶ **Repair: require a minimum leading context, or fail closed when there is none** — **with its must-fire negative** (§H binds the manager equally). ⓘ Free — `.tasks-php/preimage_screen.py` is in no digest. ⚠ **`N10e`'s `43` is still a hardcode and WILL move at row 9** |
| 88 | ⛔⛔ **`citecheck.py` SILENTLY CHECKS NOTHING AT ONE ROW — AND THE DIRECTION I ASKED ABOUT WAS THE SAFE ONE** | `_043` §5.3. I asked whether `inherited = set.intersection(*per_spec.values())` breaks when a row is **ADDED**; ✅ **that direction fails LOUD and is acceptable.** ⛔ **The real hole is the single-row case: the intersection over one set IS that set, so EVERY citation classifies as *inherited* and all of them are suppressed — and `N2` still passes.** ⭐ **A checker that cannot fail, which is `F10`'s shape and §H's whole reason.** ▶ **Repair: `len(specs) >= 2`, with its must-fire negative.** ⓘ Free. ⚠⚠ **And the general lesson is about MY question: I asked after the direction I could imagine and the defect was in the one I could not — so a guard audit should enumerate the DEGENERATE inputs (0 rows, 1 row, all-identical), not the interesting ones** |
| ~~89~~ | ✅ **CLOSED FOR `ph53` AT `TASK_PHP_044` §5**; the `invariant` clause now says `in_contract` means **`forbidden_hits` empty**, with `required_absent` reported beside it and judged against each entry's English. ⚠ **STILL OWED BY `ph07` · `ph16` · `ph29` · `ph45`** — one re-gate each, batch with each row's next task | `_043` §1.5. **`controls/spellings.json`'s `invariant` field opens *"Every variant is in contract by `harness/check.py::spelling_matches` over EVERY backticked idiom entry"* — and that clause is FALSE AS WRITTEN in 5 of 5 php rows**, because `required_absent` is non-empty on variants the row ships, **including on R3's `v0_shipped`**. ⓘ **PAT's two copies do not carry the clause.** ⭐⭐ **Item 81 predicted *"expect the next row's suite to find a fifth"* and it did — so the law *a control cloned between rows carries its defects, and only the row that writes NEW negatives finds them* now has FIVE instances and ONE successful forward prediction.** ▶ **Repair drafted (`_043` §1.8 item 3): state that `in_contract` means `forbidden_hits` empty, and that `required_absent` is reported beside it and judged against each entry's English, because `required` is presence-only and cannot fail the gate.** ⓘ **Cost: one re-gate PER ROW — `ph53` batches with item 83; `ph07` / `ph16` / `ph29` / `ph45` batch with each row's next** |
| ~~90~~ | ✅ **CLOSED AT `TASK_PHP_044` §4 — NO EDIT WAS NEEDED, AND THE ENGINEER DID NOT MANUFACTURE ONE.** ✅ **`_043`'s SCOPE READ IS CORRECT** (`required[0]`'s English does scope to R3) and the engineer argued it both ways — ⓘ the `p19`/`p46` precedents disclaim discrimination while `required[0]` declares it. ⛔ **But `r3_no_capacity` was ALREADY excluded, on a different entry**: it already carried an `english_verdict` on **`required[8]`**, so it was already outside `_admissible`. ⭐⭐ **`_043` READ `in_contract: true` AS THE VERDICT WHEN ADMISSION NEEDS BOTH FIELDS** — which is the same class as its own ruling that `required_absent` is not self-interpreting, committed while establishing it. ▶ **So the ruling WAS applied as a rule and not as a patch, and it already had been** | `_043` §1.4. A **second** in-contract violation on `ph53`, independent of the witness dispute: `r3_no_capacity` records `required_absent` on **`required[0]` `Vec::with_capacity(num_interfaces)`**, whose English scopes it to the R3/R4 rungs. ⭐ **Why it matters more than its size: if item 83's ruling is applied ONLY to the three bitmask variants, the repair is a patch on the variants that embarrassed the headline; applied to `r3_no_capacity` too, it is a rule.** ▶ **Land it in the same `ph53` re-gate** (items 83 / 85 / 89). ⚠⚠ **UNCERTAIN BY THE REVIEWER'S OWN ACCOUNT**: the English-scope transcription is **theirs, by hand**, and `check.py`'s docstring says no gate stage reproduces it — **so verify `required[0]`'s scope before landing.** ✅ **Item 83's primary result does NOT depend on it** |
| 91 | ⚠ **READING (c) REFUTED AS STATED, BUT ITS NARROWED FORM IS A REAL DEFECT CLASS — `idiom.required` ENTRIES THAT PIN RUST-SIDE CHOICES** | `_043` §1.7. My third reading — *an entry saying "IT IS NOT IN THE C AND IT IS NOT UPSTREAM" does not belong in `idiom.required` at all* — is **refuted as stated**: the block legitimately carries per-language keys and a Rust key is not an error. ⚠ **But the narrowed form survives and is worth a corpus sweep**: an entry whose **only** key is `rust` and whose subject is a rung's own invented artefact pins an implementation choice inside a contract whose name says *idiom*. ▶ **Owed: count them across both programmes**, and decide whether they want a distinct field (`rung_required`?) rather than living in `idiom`. ⓘ Cheap to COUNT, and counting costs nothing. ✅✅ **CLOSED 2026-09-13 — COUNTED, AND THE COUNT OVERTURNS THE ITEM'S FRAMING** (`.tasks-php/contract_audit.py`, 8 §H negatives inside the validator). **648 idiom entries scanned; 27 have `rust` as their only language key — but 24 of those are in `forbidden`, where rust-only is the ONLY sensible shape**, because there is nothing in the C to forbid when the construct does not exist in C (`HashMap`, `transmute`, `ManuallyDrop`, `Box::leak`). ⭐ **The narrowed concern is `required`, and there are THREE: `p19[2]` and `p46[4]`, both of which OPEN with the words *"THE RUNG BOUNDARY INSIDE THE SAFE CLASS"* and are therefore declared rather than smuggled, and `ph53 required[4]`, the entry item 83 already ruled on.** ▶ **No new field for three entries, two of which say what they are. The count IS the answer.** ⭐⭐ **INCIDENTAL AND IT MATTERS TO ITEM 107: 343 of the 648 entries are PLAIN STRINGS with no language key at all** (267 `c,rust` · 27 `rust` · 11 `c`), **so the `idiom` schema is HETEROGENEOUS and a validator that assumes per-language dicts silently skips more than half the corpus** |
| 92 | ⚠ **TWO NORMALISATIONS FOR F88's `32 %`, AND NEITHER DOCUMENT NAMES ITS DENOMINATOR** | `_043` §5.6. `ph29`'s family-B draw spread re-derives as **`range/mean = 31.42 %`** on an independent 8-span sweep — ✅ **F88 UPHELD** — but **`31.4 %` and `38.6 %` are both in play and neither document says which normalisation it is using.** ▶ **Owed: name the denominator wherever the figure appears.** ⭐ **Same class as item 84 and as F98's four missing qualifiers — which makes three instances this round of *a number published without the thing that makes it a number*.** ⓘ Free |
| 93 | ⛔⛔ **A STALE HARDCODED FIGURE IN `task_cost.py` — THE FOURTH IN THIS SESSION — AND IT INFLATED THE PUBLISHED PROJECTION** | Manager, this round. `.tasks-php/task_cost.py:201` reads `owed = 34  # QUOTA_001 floor 40 - built 6`, and **built is 7**. `quota.py` says **33**; the tasks cell said **33** in its own prose **and quoted `~97`, which is `34 × 2.86`.** ⭐ **Fourth stale hardcode in a validator this session**, after `preimage_screen.py`'s `N10e` (*"26/17"*), `task_cost.py`'s own `N7` (*"total/rows ≈ 6.5"*, stale **three times within the hour**) and `citecheck.py`'s `N1`. ▶ **Repair is the one those three got: COMPUTED, not re-pinned** — `owed = FLOOR - len(ROWS)` with `FLOOR = 20 * 2` named — **plus a must-fire negative that catches a pinned `owed` again** (§H). ✅ **The projection is already re-derived in the tasks cell as `~94–127`.** ⓘ Free — `.tasks-php/*.py` is in no digest |
| 94 | ⭐⭐ **ROW 9 = `ph55` (T5), AND MY FIRST PICK WAS WRONG FOR EXACTLY THE REASON I TOLD `_043` TO HUNT FOR** | Manager, 2026-09-13, `.temp/mgr176/NOTES.md` §§5–7. I surveyed the **14 empty families** and first recommended **`ph32`** — on **one line of `ph53`'s own `why`** calling it *"same C shape … cross-reference, do not merge"* — **then read `ph32`'s own catalogue entry, which says the opposite about cost: THREE short tables (not the one the corpus records), and an R1h of FOUR COMMITS, one of which is *invisibly incomplete*** (`56adfe1f3cf1` rewrites the table to 65 **and leaves `/* 376 (0x0178)` unterminated in the same hunk, so it compiles to 41**; `bd07142b9128` then *"fixes the `/*`-within-comment warning"* by closing it **after** the swallowed block — **silencing GCC while keeping the defect**, which is how php-5.0.4 shipped at 41 with no diagnostic). ⛔ **Rule 14's failure mode, committed by me within the hour of dispatching a task about it. Fifth self-correction of the day.** ✅ **REVISED: `ph55`**, and the screen is run — R1h **`4f68f3774c34`, 2004, 1 file, same file** (the best shape in the catalogue, against `ph32`'s worst), and **all four mechanism facts verified on the pristine C**: `increment_opline = 0` at `:1728`, set at `:1749`, the **error** exit at `:1765-1770` calls `NEXT_OPCODE()` without consulting it, the **normal** exit at `:1792-1795` does; `NEXT_OPCODE()` = `EX(opline)++`, `INC_OPCODE()` = one more; and **`:4427` is `zend_opcode_handlers[ZEND_OP_DATA] = NULL;`**. ⭐⭐ **THREE USES OF ONE LOCAL FLAG AND ONE OF TWO EXITS FORGETS TO CONSULT IT — the smallest self-contained mechanism in the catalogue and the best crash-course specimen in it.** ⭐ **It needs NONE of `ph52`'s trouble**: no zvals, no allocator, **no garbage determinism** (the fault is a NULL indirect call), no stack-layout dependence — and the **Rust ladder is clean rather than blocked**, because a dispatch table of `Option<fn>` **cannot be called without unwrapping**. ⭐ **T5's SECOND row is nearly free** (`ph56`, 2004, 1 file; ⛔ **not `ph57` — 2013, 4 files**), so entering T5 discharges **2** of the 33. ⚠⚠ **THE SCREEN IS NOT COMPLETE: `preimage_screen.py` must confirm the cited lines are in the pre-image** (F38's lesson) — **deferred because that script was `_043`'s own subject.** ⚠ **AND THE §5.2 RANKING OF THE OTHER 12 FAMILIES IS UNRELIABLE** — it came from one line of prose each, which is what just failed; **read each candidate's OWN entry and OWN R1h before dispatching it** |
| 95 | ⚠ **ONE THING IN `ph55` I FOUND AND COULD NOT SETTLE — IT MAY BE A *SECOND* INSTANCE OF THE SAME DEFECT** | Manager, 2026-09-13, from the pristine C. **`INC_OPCODE()` is itself guarded: `if (!EG(exception)) { EX(opline)++; }`** — so **when an exception is pending the NORMAL exit also advances by only ONE word**, the same single stride the error exit takes unconditionally. ⚠⚠ **I do not know whether that is a second instance of the defect or a deliberate hand-off to exception dispatch, because I have not traced what reads `EX(opline)` once `EG(exception)` is set.** ▶ **It is the FIRST question row 9 must answer, and the answer changes the row: if the exception path is also defective the kernel needs TWO error exits, not one.** ⓘ **UNTESTED** |
| ~~96~~ | ✅ **CLOSED AT `TASK_PHP_044` §7 — THE CLAUSE LANDED AND THE CONCLUSION IS STRONGER THAN I WROTE IT.** ⛔⛔ **BUT MY STATED REASON WAS WRONG ON BOTH HALVES, AND I HAD READ THE FILE.** I wrote *"the shim ZEROES fresh blocks and poisons `0x5a` ON FREE"*. **Verified by me after the report: the `memset(p, 0, …)` at `emalloc_shim.h:573` is inside `php_shim_ecalloc`, where zeroing is the CONTRACT — `emalloc` does NOT zero — and `0x5a` appears in the header's own *"WHAT IS DELIBERATELY NOT MODELLED"* list**, as a ZEND_DEBUG behaviour the shim omits on purpose (*"modelling it would ADD a poison-on-free that pristine PHP does not do"*). ▶ **I read one function's body as the general allocation path, and a list of what a file does NOT do as what it does.** ⭐ **Same class as `check.py::spelling_matches`'s *a comment is not code*, and the SECOND time I made it in one session** — the first was a textual guard in `width.py` that fired on the comment documenting the very defect it was written to catch. ⭐⭐ **AND THE CORRECTED REASON IS SHARPER: the shim uses plain `malloc`, so `0xbe` is not even a compile-time property — `ASAN_OPTIONS=malloc_fill_byte=0` gives zeros, making it a RUNTIME OPTION DEFAULT.** Re-measured on four arms by the engineer | F102. `ph53`'s R1 reports `member access within misaligned address **0xbebebebebebebebe**`, and **`0xbe` is ASan's malloc fill byte** — measured on this box (`.temp/mgr176/asanfill.c`): fresh `malloc` under ASan reads `be be be …`, **without ASan it reads zero**. ⛔ **The `emalloc_shim` does NOT produce it**: it zeroes fresh blocks and poisons `0x5a` **on free** only. ▶ **So the specific wild value the row cites is the DETECTOR's pattern, not the row's or the shim's**, and a reader of `cwe_note` would reasonably take it for a property of the program. ✅ **Nothing about the row's verdict changes** — the slot genuinely is indeterminate and ASan genuinely reports it. ⚠ **What is owed is one clause saying WHOSE pattern it is.** ⓘ `cwe_note` is inside the hashed block → **batch with items 83/85/89/90's `ph53` re-gate** |
| 97 | ⛔⛔⛔ **§H HAS BEEN SATISFIED BY GITIGNORED EVIDENCE ON FOUR OF FIVE ROWS — A COMMITTED VALIDATOR SHIPS AND THE PROOF THAT IT CAN FAIL DOES NOT** | `TASK_PHP_044` §3.2 found ONE instance (`ph53/controls/spellings.py:1349` citing `.temp/php42/negatives_spellings.py`); **I extended `citecheck.py` to the layer it could not see and the answer is SYSTEMIC: 13 §H-at-risk citations across 4 rows** — `ph16`, `ph29`, `ph45`, `ph53` — **out of 30 `.temp/` citations in 11 committed `controls/*` files.** ⛔⛔ **`PROTOCOL_PHP.md` §H says *a validator change lands with its must-fire negatives, or it does not land*. If those negatives are gitignored, §H is satisfied in a way that DOES NOT SURVIVE A CHECKOUT.** ⭐ **`citecheck.py` scanned `spec.md` + `NOTES.md` only, so the checker that exists to find exactly this was blind to the layer where the worst instance lives** — F99/item 65 extended one layer out, and **F10's *a checker that silently checks nothing* for the third time.** ✅ **REPAIRED 2026-09-13**: `CONTROL_CLAIMS` added, the §H subclass flagged separately (matched on the **citing line**, not the path, because the role is what matters) and reported as a WARNING so the 17 historical hits do not drown it, **with negatives N5 / N5b / N5c / N5d**. ⭐ **And the right repair per row is the one `_044` chose for `ph53`: move the arms INSIDE the validator so they run on every invocation and feed `problems`** — then emptying the constant is a **red gate** (stage 9b `FRESH+VERDICT-FAILED`), not a better-looking number. ⚠ **Cost: one re-gate per row; batch with items 89 and 63** |
| 98 | ⛔⛔ **THE FIRST CASE WHERE A *PROSE CORRECTION* IS BLOCKED BY THE **MEASUREMENT** DIGEST — AND IT IS A STRUCTURAL HOLE, NOT A `ph53` PROBLEM** | `TASK_PHP_044` §6.1. The fifth *"twice independently"* site is **`patterns-php/ph53-iface-tail-uninit/c/kernel_hardened.c:8-9`** — a **comment** asserting *"and `preimage_screen.py` labels it `NOT-THE-REPAIR` independently"*, a route F95's own repair **withdrew**. ⛔ **`c/*` is in the MEASUREMENT digest, so repairing a COMMENT costs a 32-cell RE-MEASURE**, and trap 1 forbade it. ✅ **The engineer did the right next thing: `spec.md`'s `provenance.fix_commit_note` and `NOTES.md` §3 now both record that the comment is still there, that it is in the measurement digest, and that this file carries it** — so a later reader finds it **known** rather than undetected. ⚠⚠ **THE GENERAL PROBLEM: a C kernel's comments are hashed at MEASUREMENT price, so any provenance prose that ages inside one is effectively frozen.** ▶ **Owed: a policy. Either (a) C-kernel comments carry NO provenance claim that can age — point at `spec.md` instead — or (b) accept a re-measure when they do.** ⭐ **(a) is nearly free and is the convention the rest of the corpus already follows.** ⚠ **Audit the other 7 rows' `c/*` comments for aging provenance claims before this recurs** — cheap to COUNT, and counting costs nothing. ✅✅ **CLOSED 2026-09-13 — AUDITED, AND THE CORPUS ALREADY DOES (a)** (`.tasks-php/contract_audit.py`). ⭐ **The split that settles it is POINTER vs VERDICT**: *"`NOTES.md` §7 says so in terms"* **asserts nothing and therefore cannot age into falsehood**; *"`preimage_screen.py` labels it `NOT-THE-REPAIR` independently"* **asserts another artefact's conclusion, and that is what aged.** **27 POINTERs · 6 raw VERDICT hits, of which exactly 2 are REAL — and they are the two lines of F98's own known sentence in `ph53`.** ▶ **So policy (a) RATIFIES existing practice rather than changing it, and NO ROW OWES A REPAIR.** ⭐⭐ **AND THE METHOD FINDING: 4 of the 6 hits are classifier false positives** (`independent` inside *"order-independent"*, `labels` as a plural noun, *"`diff` proves it"* where `diff` ranges over files already in the digest). ⛔ **The tempting repair was to tune the regex until the count looked right — F10's shape.** ▶ **Instead every hit is adjudicated BY HAND with its reason and `N8` fails on any UNFILED *or* STALE entry — and it caught the manager on its first run, on a line filed from memory as `:484` when the real hit was `:640`** |
| 99 | ⚠⚠ **W1 MOVES BY ±14–28 Ir ACROSS REGENERATIONS WHILE **EVERY** A1 FIGURE IS BIT-IDENTICAL — UNEXPLAINED, AND IT IS EVIDENCE *FOR* THE `inside_share` RULE** | `TASK_PHP_044` §8.2. Across **four** regenerations of `ph53`'s sidecar the engineer measured **every A1 figure bit-identical** while the whole-program column moved by a **constant ±14–28 Ir**; I confirmed the residue myself — `wp_spread_pp` now reads `{R3: 67.930588, R4: 39.543994}` against `_042`'s `{67.930558, 39.543977}`, while `a1_spread_pp` is **unchanged to the digit**. ⓘ **14–28 Ir is exactly the per-call stack-alignment bistability `check.py::check_marginal_ir` names, and exactly the band `width.py`'s X3 found between sessions** — so the likely cause is the argv/env block, i.e. **the path length of whatever invoked the gate.** ⚠ **NOT ISOLATED** — the engineer de-quoted `wp_spread_pp` to 2 dp to break the fixpoint and said so rather than chasing it. ⭐⭐ **AND IT IS A THIRD, INDEPENDENT LEG UNDER `.memory-php/03-numbers.md`'s RULE: A IS SYMBOL-SCOPED AND THEREFORE REPRODUCIBLE, THE WHOLE-PROGRAM COLUMN IS NOT.** ▶ **So *"quote both, labelled"* now has a REPRODUCIBILITY reason beside its resolution reason** — and a row that publishes only W1 (`ph45`) publishes the unstable one. ⚠ ~~**UNEXPLAINED**~~ ✅✅ **EXPLAINED AND CONTROLLED 2026-09-14 BY `TASK_PHP_048` §4c — IT IS THE LENGTH OF `argv[1]`, AND THE STEP IS `7 Ir/call`.** `ph55`'s §8b-2 table was first computed with a **relative** input path and gave `c-clang → c-clang-h = −0.0007 Ir/call`; recomputed with an **absolute** path the SAME TWO BINARIES gave **`−7.004 Ir/call` = `−0.398 %`** — nothing rebuilt, `md5sum` identical across both runs. ⛔⛔ **A `−0.398 %` *“the fix is profitable under clang”* WAS ONE PASTE AWAY FROM BEING PUBLISHED.** ⭐ **Mechanism (inferred from the step's size and shape, NOT proven): a longer `argv[1]` shifts the stack pointer and with it the alignment of the 1 024-byte `[Op; 64]` and the 42-slot zval store the kernel zeroes on EVERY call; 7 Ir/call × 20 000 calls = 140 000 Ir = 0.4 % of the program.** ⛔ **NARROWED 2026-09-14 (`TASK_PHP_050` §4.2): THE MECHANISM IS UPHELD AND *UNDER-STATED* — PAT proved it at `TASK_098`, so it is MEASURED and not inferred — BUT THE TWO-ARRAY CLAUSE OVER-COUNTS BY TWO. The measured step is `7.00` with **two levels**, not `14.00` with three, so **AT MOST ONE ARRAY CONTRIBUTES.** ▶ **If this enters `.memory-php/`, it enters with the count removed.** ✅ **`ph55/controls/argv_align.py` sweeps eight `argv[1]` lengths over the same binaries and the same input bytes and reports TWO verdicts per pair — *magnitude resolvable?* and *sign stable?*** ⭐ **The split is a correction the control forced**: one pair is `+216 k` or `+76 k` Ir depending which side of the step it lands on, **both positive**, so the magnitude is not quotable and the sign is — **a single verdict would have thrown away a real result to avoid quoting an unreal one.** ⚠⚠ **AND IT BIT THE SAME ROW'S PROSE A SECOND TIME AFTER THE CONTROL EXISTED** (§8h published a flat `−7.42 %` from one run; the re-measure of byte-identical binaries gave `−7.79 %`, so §8h now publishes a **RANGE**). ⭐ **The sign and the band survive; the third digit does not exist.** ▶ **STILL: do not quote a W1 figure to more than 2 dp — now for a MEASURED reason** |
| 100 | ⛔⛔⛔ **A BACKTICK IN AN `idiom.required` ENTRY *IS* A PIN — AND `_043`'s DRAFTED REPAIR WOULD HAVE ADDED **THREE FALSE PINS** TO THE ENTRY IT WAS FIXING** | `TASK_PHP_044` §2. `_043` §1.8's draft backticked `` `u32` ``, `` `controls/spellings.json` `` and `` `required_absent` ``. Under `harness/check.py::spelling_matches` each becomes a declared spelling matched against every Rust rung: ⛔ **`u32` matches EVERY rung** (a pin that cannot discriminate, i.e. the **ANTI-signal** class `idiom_audit` measures at **17 of 41**), and the other two **match NO rung** (`pins nothing`, on all 20 variants and all 6 shipped rungs). ⭐⭐ **THE REVIEWER THAT ESTABLISHED *"a backticked span pins the representation"* THEN WROTE THREE SPANS IT DID NOT MEAN TO PIN, IN THE SENTENCE ESTABLISHING IT** — and `_043` §1.1 had already recorded the convention that forbids it (`p42`'s *"quoting a file name or a retracted span would pin it too"*). ⭐ **The engineer caught one of its OWN the same way**: a meta-sentence reading *"ONLY `wrote[i]` AND `[bool; MAXD]` ARE BACKTICKED HERE"* **re-backticked both spans and duplicated them** — caught **by running `spellings.py --audit-only` and reading the output, not by reasoning.** ▶▶ **THE LAW: ANY DRAFT OF `idiom.required` / `forbidden` PROSE GOES THROUGH `idiom_audit` BEFORE IT LANDS — including a reviewer's, including a manager's.** ✅ Landed in `.memory-php/02-ladder.md`. ⓘ `_043` §1.8's uncertainty 13 flagged exactly this gap, which is why flagging it was right |
| 101 | ⚠ **TWO THINGS `TASK_PHP_044` CHANGED OR DID NOT RUN, BOTH DECLARED** | `TASK_PHP_044` §8.2–8.3. **(a)** its generator change **alters `spellings.py --audit-only`'s exit code** — a deliberate consequence of moving two §H arms inside the validator so `problems` feeds stage 9b, **but any script that shells out to `--audit-only` and reads `$?` is affected.** ▶ **Grep for callers before the next row clones this control.** **(b)** **`controls/negatives.py` was NOT re-run — `UNTESTED`, and the engineer said so rather than implying coverage.** ⓘ It is a different control from `spellings.py` and the gate records `controls_json {"spellings.json": "FRESH"}` only. ▶ **Cheap: run it and record the result.** ⭐ **Both are the shape the programme wants — a declared gap costs one line; an implied one costs a reviewer** |
| ~~102~~ | ✅✅ **CLOSED AT `TASK_PHP_046`** — `controls/spellings.py` built (2896 lines, **15 variants, 24 §H arms INSIDE the validator**), `controls_json {} → {"spellings.json": "FRESH"}`, and the row's in-contract spread published **filtered AND unfiltered** (`a1_spread_pp {R3: 7.923098, R4: 7.769824}`, identical either way on this row — which settles `_044` §3.4's open question here by measuring both). ⚠ **STILL OWED: `ph03` and `ph64`'s endpoint searches**, and `task_cost.py`'s `N12` keeps firing until they land | `TASK_PHP_045` §23 names it the row's clearest omission: **the headline ships with no in-contract spread beside it**, and `controls_json` is `{}`. ⭐⭐ **AND CHECKING IT EXPOSED A DEFECT IN MY OWN COST TOOL, WITH A BIGGER ANSWER THAN THE ROW.** Every other row's figure includes an endpoint search (`ph45` = `_036`+`_037`; `ph53` = `_041`+`_042`); `ph52` landed at **1.00**, the cheapest entry ever, **with no search** — so the per-row series mixed two different amounts of work, which is `N5`'s own defect one level down where `N5` could not see it. ⛔ **`task_cost.py` now derives the flag FROM THE FILESYSTEM and the answer is THREE rows, not one: `ph03`, `ph64`, `ph52`.** ▶ **The comparable marginal is `3.23`, not `2.75` — the all-rows figure is optimistic by `+0.48` tasks/row** — and ⭐⭐ **the 40-row floor counts ROWS and not WORK OWED BY ROWS ALREADY BUILT, so three endpoint searches appear in NO floor estimate published so far.** ✅ **Range corrected to `~106 … ~119`, middle `~117`** (uncorrected it read `~88 … ~116`), with negatives **N12** (must-fire while any row is unsearched, and it stops on its own when the file appears) and **N13**. ▶ **Owed: three endpoint searches. `ph52`'s is the one that also buys its in-contract spread** |
| 103 | ⛔⛔ **`results-php/preflight/_norow.preflight.json` IS A DE-DUPLICATING LEDGER, NOT A PER-INVOCATION LOG — AND CLOSING THE BRACKET IS ITSELF A WRITE** | `TASK_PHP_045` §22.1. The engineer ran the no-row bracket **four** times; `runs` went **21 → 23 and stopped**, the two new entries differing in a single field (`tool_returncode`, `1` then `0`). ▶ **So a reviewer counting `runs` to count gate invocations UNDERCOUNTS**, and the ledger de-duplicates on content rather than appending. ⚠⚠ **AND THE STRUCTURAL HALF: taking the required bracket reading WRITES to a tracked file, so there is no way to satisfy the bracket obligation without dirtying the tree** — which is why `git status` shows that file modified after every task that obeys its own instructions. ▶ **Owed: either (a) say in `PROTOCOL_PHP.md` that this file is expected to move and is not part of any digest, or (b) give the check a read-only mode.** ⓘ **(a) is free**; confirm first that the file is in no digest. ✅✅ **CLOSED 2026-09-13 — CONFIRMED AND WRITTEN.** `.tasks-php/contract_audit.py`: **18 gate + measurement records scanned · 0 mention `preflight` at all · 0 digest entries name a preflight path.** ▶ **So taking the required bracket reading cannot stale anything**, option (a) is correct, and **the sentence is now in `PROTOCOL_PHP.md` §F6.** ⭐ **`N7` fails if a preflight path is ever hashed**, so the ruling cannot go stale silently |
| ~~104~~ | ⛔⛔ **WITHDRAWN AT `TASK_PHP_046` — THE PREMISE WAS FALSE AND I PROPAGATED IT WITHOUT CHECKING.** **All four `harness/build.py` citations RESOLVE CORRECTLY TODAY.** ▶ **The field `doc_citations.other` means only *"a line citation of a module other than `check.py`"* — it was NEVER a rot claim**, and I read `_045` §23's phrase *"deliberately left rotting"* as a measurement. ⭐ **Rule 14 with the roles reversed for the second time this session: an ENGINEER's summary phrase the manager had no reason to doubt — and one `grep` would have settled it.** ⓘ **And the real fact is the opposite of a row debt: THREE of the four live in the SHARED `common-php/emalloc_shim.h`, so repairing them is a NINE-ROW RE-MEASURE** — which makes them **item 98's** class and not this row's. ▶ **Reclassified into 98** | `TASK_PHP_045` §23. Four citations of `harness/build.py` line numbers have drifted, and **repairing a POINTER costs a 32-cell re-measure** because the citing files are in the measurement digest. ✅ **Left rotting deliberately and declared, which is the right call** — and it is **item 98's exact class on a second row within one day**, so the policy item 98 asks for is now load-bearing twice. ▶ **Free to fix the moment item 102's endpoint search forces a re-measure on this row** — batch them. ⭐ **AND THE GENERAL REPAIR IS THE SAME AS 98's: a file in the measurement digest carries NO pointer that can age** — cite a symbol name, not a line number |
| ~~105~~ | ✅✅ **DECIDED BY THE USER, 2026-09-17: OPTION (c) — LEAVE IT, DOCUMENT IT.** ▶ **The note is landed in `.memory-php/02-ladder.md`'s `tcb_items` entry** (the `F106` paragraph, in place — one home), and the worked case stays where (c) prescribes: `ph52` `NOTES.md` §11's six-variant table, the refusing stage for each, and the pressure analysis. ⛔ **`harness/` was NOT edited.** ⛔⛔ **THE DEFECT IS ACCEPTED, NOT FIXED, AND THE STANDING CONSEQUENCE IS RECORDED IN THE LAYER**: every future row whose best R4 has a smaller trusted base pays a `twin_justifications` hatch plus a blocked variant, and its reduction is **demonstrable but not publishable on the corpus's own axis**. ▶ **Record each instance against that entry**; re-opening needs a NEW measurement — a row where (c) loses something (c) cannot demonstrate — **not a fresh argument**, since the arguments are all on file. ⭐ **AND CHECKING THE PRICE BEFORE ASKING WAS WORTH IT**: option (a) was published as *“a 33-pattern re-gate”* and is **47 records — all 33 PAT and all 14 php**, `law 17` firing on the one item that asked the user to spend something; ⛔⛔ **AND MY FIRST EXPLANATION FOR WHY THE php HALF WENT UNPRICED WAS FALSE AND IS WITHDRAWN.** I wrote that `harness-php/gate.py` has no `--tool check --check-stale`, *therefore* the exposure is *“RECORDED and never REPORTED.”* **Measured by running it: `--tool measure --check-stale` examines all 14 php GATE records** (`FRESH results/gate/ph…` ×14) **and their `source_sha256` carries `harness/check.py`, so the bracket reports it perfectly.** ▶ **I inferred an absence from a CLI's SHAPE instead of running the command** — `--tool` selects which MODULE runs, while `check_stale()` globs `p*.json` and covers BOTH record families regardless, and `ph*` matches `p*`. `F148`'s class in a third direction and `F138`'s in its own (*reading argparse is not running the tool*). ✅ **The `47` STANDS** — that was measured from the records. **Only the excuse was invented**, and the real reason is the plain one: the item's author wrote *“33-pattern”* from the PAT side and never counted php. **The original framing, kept for the record:** | ⛔⛔⛔ **NOW MEASURED, NOT LATENT: F104 PINS A VERIFIED, BYTE-IDENTICAL, ZERO-COST TCB REDUCTION *OUT* OF THE CORPUS — A DECISION IS OWED** | F104 **+ F106**. `check.py::check_trusted_twins`'s `n_twins == 0` hard-fails the row with the **smallest** trusted base, and `TASK_PHP_046` §4 measured the consequence on real rung candidates: **all three smaller-TCB R4 variants are refused** — two by `n_twins == 0`, one by F97's `_scan_unsafe_sites` — and ⭐⭐ **`r4_no_wrapper` is `external_body` 4 → 3 at a BYTE-IDENTICAL `kernel` with 34 verified / 0 errors. One fewer axiom, zero cost, unshippable.** ⛔ **So the gate refuses a strict improvement on a PUBLISHED axis for a reason that has nothing to do with the row.** ⛔⛔⛔ **UPDATED 2026-09-13 BY `TASK_PHP_047` §1.7 — THERE ARE **TWO** OPTIONS, NOT THREE, AND THE MANAGER'S RECOMMENDATION IS WITHDRAWN.** ▶ **(a) edit `harness/check.py`** — ⛔⛔⛔ **PRICED AT *“a 33-pattern re-gate, PAT side re-verified”* AND THAT IS THE PAT POPULATION ASSERTED OF THE DECISION'S SCOPE. MEASURED 2026-09-17: `harness/check.py`'s sha256 `eeb7ffa7b034…` is in `source_sha256` of **ALL 33 PAT AND ALL 14 PHP** gate records, byte-identical in both — so the edit invalidates the recorded provenance of **47 rows, not 33**, a 42 % under-statement.** ⚠ **What I have NOT established, and it is the difference between 47 and 33**: whether the php records must be RE-GATED or may carry a stale `check.py` hash — `harness-php/gate.py` has no `--tool check --check-stale` combination, so **the php side's exposure is recorded but NOT REPORTED by any bracket**, which is why it went unpriced. ▶ **Settle that before choosing (a); it is one question and it moves the cost by 14 rows.** ⭐ `law 17`, landed hours earlier, fired on the open item that asks the user to spend money; **⛔ ~~(b) add the condition in `harness-php/`~~ DOES NOT EXIST**; **(c) leave it** — the row keeps its demonstration in `controls/` and the report says which. ⛔⛔ **WHY (b) IS GONE, ON THREE INDEPENDENT GROUNDS ALREADY WRITTEN IN THE TREE: (1)** `harness-php/gate.py`'s own header, under *"WHAT THIS FILE IS, AND WHAT IT IS FORBIDDEN TO BE"*, says it *"REIMPLEMENTS NO GATE STAGE and must never grow one … a php-only stage here would be **a second, unvalidated gate wearing the first one's name**"*; **(2)** it **cannot make itself mandatory** — `grep -c preflight harness/{check,measure,report}.py` is `0 0 0` (re-run by the reviewer), and no gate record says whether the wrapper ran, so **an exemption no artefact can witness is not a gate rule**; **(3)** `root.py` rebinds **PATHS** — it is a symlink shim so that `os.path.abspath` carries REPO-relative paths — **and it cannot change a stage's verdict.** ⛔ **I read `CLAUDE.md`'s "rebinds at run time" banner as verdict override; it is about path roots.** ⭐ **AND (c) IS NOT MERELY *"honest"* — IT IS THE ROUTE `gate.py`'s OWN HEADER PRESCRIBES**: *"if a php row needs a check the PAT gate does not have, it goes in that row's `controls/` or in a separate tool, and the report says which."* ⚠ **THE DECISION IS STILL THE USER'S**: (a) buys the ability to **publish** the smaller TCB inside the corpus, which (c) cannot — that trade is a judgement, not a measurement. ✅ **`TASK_PHP_047` §1.8 drafted the condition text for (a), so one decision routes one edit.** ⛔⛔ **DO NOT EDIT `harness/` TO TEST THIS** | F104. `check.py::check_trusted_twins`'s `n_twins == 0` rule hard-fails a row whose trusted base is **smallest**, and the repair is inside `harness/check.py` — **hashed into all 33 PAT gate records** (`CLAUDE.md`'s top banner). ⛔ **So the cost is a 33-pattern re-gate for a rule that currently pressures a php row to ENLARGE its TCB.** ⭐⭐ **THIS IS THE DECISION THE SPLIT-PROGRAMME DESIGN WAS ALWAYS GOING TO FORCE, and it has now arrived**: the php programme imports `harness/` and never edits it, which works until a php row finds a DEFECT there. ▶ **Three options, and the manager should pick one rather than let it recur: (a) accept the re-gate once, with the PAT side re-verified; ⛔ ~~(b) add the condition in `harness-php/` where php can override the stage~~ — **REFUTED `TASK_PHP_047` §1.7, `harness-php/` may not host a gate stage, cannot make itself mandatory, and rebinds paths not verdicts**; (c) leave it, and every future small-TCB row pays a `twin_justifications` hatch plus a blocked row.** ⚠ **(c) is what `ph52` did and it is honest, but it means the gate's strongest statement about a trusted item is unavailable exactly where the TCB is smallest.** ⓘ **Latent, not live** — `ph52` found a legitimate way out worth `−7.12 %`. ⚠⚠ **DO NOT EDIT `harness/` TO TEST THIS** — price it first |
| 107 | ⛔⛔ **A VALIDATOR THAT READS `idiom` PROSE INHERITS EVERY *INCIDENTAL* BACKTICK IN IT — ITEM 100's CLASS, THIRD INSTANCE, AND THIS ONE FIRED ON THE SHIPPED RUNG** | `TASK_PHP_046` §(own-defects). The engineer's new `english_verdict` rule **keyed on the `required` ENTRY** rather than on the span, and therefore **fired on five of six R4 variants INCLUDING THE SHIPPED RUNG'S OWN SPELLING** — because `required[0].rust` happens to quote `` `Option` `` **incidentally**. ✅ **The gate record's own `idiom_audit.absent` corroborated it**, and the repair is to key on the **span**; arm `E8` pins it. ⭐⭐ **THE COROLLARY IS THE FINDING AND IT GENERALISES BEYOND THIS ROW: a validator that consumes `idiom` prose inherits every backtick the prose contains, including the ones that are there to REFER and not to PIN.** ▶ **So item 100's audit step is owed not only by whoever WRITES the prose but by whoever writes a tool that READS it.** ⚠ **Third instance in three tasks — `_043` (a reviewer), `_045` (an engineer), `_046` (a validator) — so the law needs to be in the template, not only in `.memory-php/`** |
| 108 | ⚠⚠ **`ph52`'s **C** RUNGS ARE UNSEARCHED, AND THAT IS TRUE OF EVERY ROW IN THE CORPUS** | `TASK_PHP_046` §15, the engineer's own uncertainty list. The search covered the **15 Rust cells**; the **C** rungs were not respelled. ⚠ **This is not a defect in the task — it is scoped that way corpus-wide** — but it means the `fixed-R4 bound` and the R3-side span are **Rust-side spans against a C rung nobody has tried to move**, and the C rung is the baseline every cross-language figure divides by. ⓘ **`inside_share` is 22.24 % on `ph52`'s C cells, so A1 would resolve a C respelling POORLY and W1 would be the column** — i.e. the cheap method does not transfer. ▶ **Owed: a ruling on whether a C-side search is in scope for this programme at all.** ⭐ **If it is NOT, say so once and say why, rather than leaving eight rows each silently unsearched on one side** |
| 109 | ⛔⛔⛔ **F101 FIRED *LIVE* ON A THIRD ROW AND IN A DIRECTION `_043` RULED IMPOSSIBLE — IT *CAN* FABRICATE A BYTE-IDENTITY CLAIM** | F105, `TASK_PHP_046`. In a **fresh clone** the path-sensitive `kernel_fingerprint` gave **one false POSITIVE — two DIFFERENT sources reported byte-identical — plus two false negatives, 3 of 6 compared pairs.** ⛔⛔ **`_043` §5.1 ruled that a false negative *"cannot undermine a claim OF identity"* and therefore that F77 was structurally safe. The POSITIVE direction breaks that argument**: the defect **can** manufacture identity. ✅ **F77 itself is STILL safe — for the OTHER reason `_043` gave, that `r4_fold_iter`'s digests were checked EQUAL directly (`d71669d3c0e6`, 209/209) — so the conclusion survives on the leg that was a measurement rather than the leg that was an argument.** ▶ ⓘ **That is F83's shape exactly: a conclusion standing on two legs, one of which turns out to be worthless.** ✅ Repaired in `ph52`'s control (fixed-width `vNN` slug + an **asserted equal-path-length invariant**; exec-vs-twin via `asm.py::identity_level` at `norel`). ⚠⚠ **STILL UNREPAIRED IN `ph16`, `ph29`, `ph45`, `ph53`** — item 81's four rows, and the repair is now **written and proven** in `ph52`, so cloning it is cheap. ▶ **Batch with items 89 / 97 / 63 per row** |
| 110 | ⛔⛔ **A COMMITTED CHECKER HAS BEEN RED SINCE 2026-09-10 ON SOMETHING IT ADJUDICATES AS CORRECT, AND IT MADE MY *"all checkers pass"* FALSE** | Manager, 2026-09-13. **`.tasks-php/coverage.py` exits 1 in its INTENDED steady state.** Its substantive claims are all green — **`166/166` accounted for, `MISSING 0`, 102 Part A rows, 102 Part B blocks, no gaps** — but `bad` includes `dup`, and the two duplicates are `LOGIC-011` and `LOGIC-022`, both `['ph77','ph83']`, which **the script's own output declares ADJUDICATED in `CATALOGUE.md`** with a corroborating reason (the ids are *sites* in `ph77` and the *mechanism* in `ph83`; they resolve to **different fix commits**, and `PROTOCOL_PHP.md` §G1 says a distinct fix is evidence for DIFFERENT). ⛔ **So the script prints its own adjudication and then fails on it.** Introduced deliberately at `c10dbb9` (*"carry the verdict on a double-claimed id, instead of just the warning"*) — **the intent was right and the consequence is that the exit code now carries no signal**: a reader cannot tell *"coverage is fine"* from *"coverage broke"*. ⚠⚠ **AND IT BEARS ON A SENTENCE I PUBLISHED.** Measured 2026-09-13, **two of ten checkers exit non-zero**: `citecheck` ✅ **legitimately** (the 13 §H-at-risk citations, item 97, genuinely owed) and `coverage` ⛔ **not**. ▶ **The accurate statement is *"every checker's substantive claim is green, and two exit 1, one of them for a real reason"* — NOT *"all checkers pass"*.** ✅ **REPAIRED 2026-09-13**: `coverage.py` now carries the ratchet `contract_audit.py` introduced — an **adjudicated** duplicate is reported and excluded from `bad`, an **UNFILED** one fails, and a **STALE** adjudication fails too. ⓘ Free — `.tasks-php/*.py` is in no digest |
| 111 | ⛔ ~~**THE BIGGEST OPEN THREAD MAY BE A `gcc` PROPERTY**~~ → ✅ **CLOSED 2026-09-13: UPHELD-NARROWED, HEADLINE REFUTED, AND IT FOUND SOMETHING BIGGER** | ⛔⛔⛔ **THE TITLE IS REFUTED, BY THE ATTACK THE TASK WAS TOLD WAS MOST LIKELY TO KILL IT** (`TASK_PHP_049` §1.3): **YES, the *"three other statistics"* WERE THEMSELVES COMPUTED AGAINST `c-gcc`** (`.temp/mgr172/STATISTIC-DECISION-DRAFT.md` §5: `large \| c-gcc vs safe_naive \| A +33.01 \| B −0.80 \| C −1.06 \| W1 −1.19`). **So I compared A1(`c-clang`) to three `c-gcc` numbers.** ⛔ **Like-for-like, against `c-clang`, C and W1 are `−27.78 %` / `−27.61 %` — nowhere near ~1 %**, and the swap does not rescue A1: it shrinks the large gap 34.07 → 23.42 pp and **ADDS a sign flip on `small.bin` that gcc did not have.** ⛔⛔ **AND THE DIRECTION IS BACKWARDS**: splitting F85's **29 cross-language flips** by baseline gives **21 `c-clang` to 8 `c-gcc`**, and above a 1-pp floor on both columns **17 clang to 0 gcc**; **20 of the 28 family-C survivors are clang-baseline.** ▶ **If the thread is anyone's property it is CLANG's.** ✅✅ **WHAT SURVIVES, AND IT IS WORTH MORE THAN THE HEADLINE: all four `ph29` figures and all 24 cells reproduce to the digit; the swap flips `10 of 128` A1 cross-language pairs — `15.6 %` at `O3/isolated` and ⭐ `0 %` at `O0` — across FOUR of eight rows, so no cherry-picking.** ⭐⭐⭐ **AND A SECOND PUBLISHED CLAIM CHANGES SIGN, WHICH I HAD NOT FOUND: `.memory-php/02-ladder.md`'s `ph03` ROW-1 HEADLINE TABLE — *"unsafe and verus are 7.6 % FASTER than C"* becomes `+9.17 %` SLOWER against `c-clang`, on both inputs.** ⛔ **`ph03`'s OWN `NOTES.md:692-697` ALREADY SAID SO and the AUTHORITATIVE LAYER DROPPED THE COLUMN** — the `SYNTHESIS`-beats-`RECAP` pattern one level deeper, the ROW beating `.memory-php/`. ⭐⭐ **AND I LOOKED IN THE WRONG PLACE**: I blamed the RECAP summary cell, but the unlabelled central claim is in **`.memory-php/02-ladder.md`'s 182-line unit 453–634 — which says of itself *"THIS is the layer that outranks `RECAP_PHP.md`"* and contains neither `c-gcc` nor `c-clang`.** ⭐⭐⭐ **AND THE SUFFICIENT RULE ALREADY EXISTED IN `.memory/` SINCE `TASK_001` — *"never report a C-vs-Rust number without saying which C compiler"*, *"always report a clang column"*, *"never report a perf number from an `O0` row"* — and `.memory-php/` NEVER INHERITED IT. So this was a REDISCOVERY** (the PAT pilot measured the same effect at **+42.9 %**), **and the real defect was an un-inherited rule.** ✅ **Landed in `03-numbers.md` as the FIFTH thing every percentage owes, with *"quote a rung against a rung"* RETIRED in favour of the PAT wording.** ⛔ **THREE CORRECTIONS TO MY OWN ITEM-111 NUMBERS: *"six of eight"* is FIVE of eight; the premise was BACKWARDS (at `O0`, six cells move between `isolated` and `whole` and ALL SIX ARE `c-clang`, so `ph45`'s 8.41 pp disagreement is a clang `O0`-inlining artefact); and the summary triple *"\|min\| 1.86 / median 15.51 / \|max\| 42.17"* MIXES TWO POPULATIONS — true \|min\| is `0.45 %`, true median of the 8-cell column `15.39 %`.** ⚠⚠ **AND TWO OF THE THREE COLUMNS IN MY TABLE WERE `O0`, which `.memory/02-bench-rules.md` forbids reporting a perf number from — I quoted the rule's violation in the item that rediscovered the rule.** ✅ **THE ATTRIBUTION CONFOUND IS SETTLED ON `ph29` IN MY FAVOUR AND WITHOUT FAMILY C: the gcc→clang gap is `−28.09 %` (A1) / `−27.01 %` (C) / `−26.74 %` (W1), and W1 is IMMUNE to symbol boundaries — which also REFUTES the cold-helper alternative.** ⚠ **The other SEVEN rows have no C-cell profiles: UNTESTED.** ▶ **NEW REQUIREMENT ON ITEM 62** (below). ✅ Check landed: `.tasks-php/cbaseline_check.py`, **9 negatives inside the file**, `RATCHET` hand-adjudicated. ⓘ **ORIGINAL FRAMING, KEPT:** ⚠⚠⚠ **MANAGER, UNREVIEWED, ONE ROW, FROM ONE PROBE — `04-process.md` law 12 applies and this round just showed law 12 holding five times out of five. THIS IS A QUESTION TO ROUTE, NOT A FINDING TO PUBLISH, AND NOTHING FROM IT GOES INTO `.memory-php/`.** The *which statistic* cell calls it *"THE BIGGEST OPEN THREAD IN THE PROGRAMME"*: *"on `ph29/large` **A says C is +33 % dearer** than naive safe Rust while **three other statistics say ~1 % cheaper**"*. **Re-measured from `results-php/ph29-recvfrom-alloc.json`, A1 (`kernel_exclusive_ir`), `O3/isolated` — the published figure reproduces to the digit against `c-gcc` (`+33.01 %`) — and against `c-clang` the SAME CELL gives `−4.36 %`.** On `small.bin`: `c-gcc` `+39.92 %`, **`c-clang` `+0.95 %`**. ⭐⭐ **AGAINST `c-clang`, A1 LANDS IN THE SAME REGIME AS THE THREE OTHER STATISTICS ON BOTH INPUTS; AGAINST `c-gcc` IT IS 30× OUT AND, ON `large`, THE OPPOSITE SIGN.** ⛔⛔ **AND THE RULE ALREADY EXISTS — WRITTEN AT ROW 1**, in `ph03`'s own table, note 4: *"`c-clang` beats `c-gcc` by 15.4 %, **which is larger than every safety effect on this row**. A compiler difference, not a safety difference — **quote a rung against a rung, never against "C"**."* **The biggest-open-thread sentence says "C".** ✅ **`STATISTICS_001.md:92` gets it right** (*"`ph29/large`, `c-gcc` vs `safe_naive`"*) — ⭐ **so the ARGUMENT DOCUMENT is more careful than the SUMMARY CELL, which is exactly the pattern `CLAUDE.md` records for the PAT side, now load-bearing on the php side.** **The gap is corpus-wide**: A1, `small.bin`, clang vs gcc on identical extracted C — `ph03` −15.27 / `ph07` −16.27 / `ph16` −1.86 / `ph29` −27.85 / `ph45` −9.91 / `ph52` −15.51 / `ph53` −29.96 / `ph64` −2.30 at `O3/isolated`, **and the SIGN REVERSES at `O0` on three of eight** (`ph16` +32.91, `ph45` +7.96, `ph64` +17.39); **8 rows, \|min\| 1.86 %, median 15.51 %, \|max\| 42.17 %.** ⛔ **THE CONFOUND IS NOT RULED OUT, ONLY ITS SIMPLEST FORM:** A1 is symbol-scoped so differing inlining moves work across the boundary (`inside_share` is **22.24 %** on `ph52`'s C cells). **Against that: (1) at `O0`, `isolated` and `whole` agree to ≤ 0.1 pp on six of eight rows while the gap is 8–42 %, and an `O0` gap is not a symbol-boundary artefact; (2) ⭐ the static size goes the WRONG WAY for the attribution story** — `ph29` `O3/isolated` symbol `kernel`, from the measurement record's own `static` block, **`c-gcc` `n_nopad` 338 / 1388 B against `c-clang` 476 / 2176 B: clang holds 41 % MORE static code while executing 27.85 % FEWER dynamic instructions**, which is a loop transformation's signature, and `ph03`'s note 5 names the candidate (*both C compilers vectorise (`xmm`); no Rust rung does*). ⚠ **WHAT THIS DOES NOT DO: it does NOT refute family C or item 62** — F85's **29 of 38 flips in A, 28 of 29 surviving family C** is a corpus-wide count untouched by any of this, and if those flips survive C then C ≈ A on them and the compiler story would have to explain that too, which it does not yet. ✅ **What it DOES do is give item 62 a SECOND, INDEPENDENT motivation that does not depend on F91's sensitivity test at all.** ▶▶ **THE TASK, AND IT IS CHEAP — every number above came from committed records with no build and no callgrind run: (1) re-derive it independently and check the manager did not pick the one row and two inputs where it works; (2) sweep every cross-language pair in `results-php/` and COUNT how many publishable claims CHANGE SIGN under `c-gcc` → `c-clang`; (3) settle the attribution confound — *"needs family C"* is a VALUED answer because it re-scopes item 62 from *"is A the wrong column"* to *"is the C BASELINE a free parameter"*; (4) rule on what a cross-language figure must be LABELLED with.** ⭐ **Row 1's rule is already correct; what is missing is that NOTHING ENFORCES IT** — a `boxcheck`-style grep for a bare *"C"* in a cross-language claim would |
| 112 | ⛔⛔⛔ **`marginal_ir_per_call` IS BIMODAL, EVERY ROW'S FAMILY-B FIGURES ARE DIFFERENCES OF TWO CELLS FROM ONE RECORD, AND NOBODY HAS SWEPT IT** | `TASK_PHP_048` §12 item 6 — **the engineer's own uncertainty, flagged and explicitly NOT swept.** ⭐ `ph55` caught it only because it happened to own a control measuring the step (`controls/argv_align.py`); **no other row has one.** ⛔ **The step is `7.0029 Ir/call` on `ph55`'s clang cells, and item 99 measured the same phenomenon at `±14–28 Ir` on `ph53`** — so a family-B difference **of that order is not distinguishable from alignment.** ⚠⚠ **THE ROW THAT WORRIES ME, AND I CHECKED IT RATHER THAN ASSERTING IT: `patterns-php/ph64-callback-frees-cursor/NOTES.md:414-415` publishes `R1h − R1` at `+15.98` / `+16.95` Ir/call (gcc) and `+18.34` / `+18.33` (clang) — the SAME ORDER AS THE ARTEFACT.** ⭐ **BUT IT HAS INTERNAL CORROBORATION THAT AN ALIGNMENT ARTEFACT WOULD NOT PRODUCE: four cells across TWO COMPILERS and TWO INPUTS agreeing within `2.4 Ir`, all the same sign.** ▶ **So it is a REAL RISK AND NOT A REFUTATION, and the sweep is what decides it.** ⓘ ✅ `ph64`'s **B1 headline** (`safe_tuned` vs `unsafe`) is a **different quantity** and is separately checked: F89's table records it reproducing to **`0.0087 pp`**, 64× the sample. ▶▶ **THE TASK, AND IT IS CHEAP AND READ-ONLY: (1) sweep every `ph*` gate record's `marginal_ir_per_call` and flag every published family-B difference whose magnitude is within ~3× the alignment step; (2) clone `argv_align.py`'s TWO-VERDICT design — *magnitude resolvable?* and *sign stable?* — because `ph55` showed a single verdict throws away a real result to avoid quoting an unreal one; (3) rule on whether a family-B figure may be published at all without such a control.** ✅✅ **SWEPT AND CLOSED 2026-09-14 BY `TASK_PHP_050` — UPHELD, AND ITS `ph64` SUB-WORRY REFUTED BY MEASUREMENT.** `.tasks-php/php50_align_sweep.py`: **all ten rows, both inputs, 32 pads = a FULL 32-byte period, `-O3 isolated` — 5 120 callgrind runs, 180 family-B differences, NO BUILD NEEDED** (every binary already existed). The pipeline **reproduces the committed `marginal_ir_per_call` exactly**. ⛔ **`ph64`: step `0.00` on EVERY cell, all four published figures reproduced to the hundredth — it has no alignment-sensitive cell at all. THE FIGURES ARE REAL.** ✅ **The instrument is live**: `ph55`'s clang cells step **exactly `7.00 Ir/call`**, **period 32, window 16, phase differing per binary** — the PAT bistability model reproducing in family B on a row nobody had measured. ⭐⭐ **AND THREE EXPOSED ROWS NOBODY SUSPECTED: `ph45` (four **Rust** cells at `7.00`, with UNEQUAL PHASES, so two of its differences carry a `14.00` range), `ph07` (**`34.49 Ir/call`, the largest step in the corpus and NOT A MULTIPLE OF 7**) and `ph29` (`0.02`, PAT's heap class).** ✅✅ **`4` of `180` differences flagged, all on `ph55` and `ph07`, NONE on `ph64` — AND NO PUBLISHED FAMILY-B NUMBER IN THE CORPUS IS WRONG**, because the only row that both publishes family B and owns an exposed cell is `ph55`, which already refuses to quote it. ▶ **THE RULING IS NOW IN `.memory-php/03-numbers.md`**: publishable iff the two cells have a measured step of `0.00` over a full 32-residue sweep, or the difference clears it by the stable ratio. ⛔ **A MAGNITUDE FLOOR — the cheaper alternative — IS REFUTED BY MEASUREMENT: it would have to be ≥ `7` to protect `ph55`, but `ph53/small` publishes `+2.80 Ir/call` at range `0.00` soundly, and the step takes FOUR values corpus-wide (`0.00`, `0.02`, `7.00`, `34.49`). Too strict and too loose at once.** ⛔⛔ **AND I MUST RETRACT HALF OF MY OWN ARGUMENT FOR `ph64`: I wrote *“four cells across two compilers AND TWO INPUTS agreeing … which an alignment artefact would not produce”*. The two-compiler half is good evidence; THE TWO-INPUT HALF IS NOT EVIDENCE AT ALL** — `probe.small.bin.100.bin` and `probe.large.bin.100.bin` are **the same length (23)**, so both inputs run at the **same** stack alignment, and `ph55` is the counter-example that proves it (its artefact agrees across both inputs perfectly). ⭐⭐ **THE CONCLUSION WAS RIGHT AND THE SUPPORT FOR IT WAS WORTHLESS — which is a defect, because THE REASON IS WHAT GETS REUSED.** ⓘ Same shape as `_049`: the effect upheld, the story about it refuted |
| 113 | ⚠⚠ **A `pgrep … \| head` HID A LIVE PROCESS AND RACED A GATE AGAINST ITSELF — `CLAUDE.md`'s *"a truncated `ls`/`head` is not evidence of absence"*, NOW IN THE PROCESS-CONTROL LAYER** | `TASK_PHP_048` §4f. The engineer ran `pgrep -af '…' \| head`, **the list truncated and hid a still-running `final2.sh`**, and on that evidence launched a "resume". **Two `check.py` runs then shared `.temp/clausemut/ph55/` and both reported FAIL — with DIFFERENT failures.** ⭐⭐ **The raced numbers are their own fingerprint: the clean run records `oset ensures[0] load-bearing (49 verified, 4 errors)` and the two raced runs SWAPPED exactly that reading with the `53/0` baseline between them.** ✅ **Re-run from `build` with a preflight that is `pgrep` with NO `head` → `PASS, 307 ok, 0 FAIL`, stage 5c identical to the clean run.** ▶ **THE LAW: a liveness check may never be truncated. `pgrep` output feeding a decision gets no `head`, no `\| head -N`, no `tail`.** ⭐ **This is the same defect class as the manager reading `ls … \| head -30` as a deletion** (`_043`), **and as F35's `grep -a`: a tool that silently reports less than it found.** ⚠ **Third instance; the first two were READ operations and this one CORRUPTED A GATE RUN.** ⭐⭐ **AND `TASK_PHP_050` HIT THE MIRROR IMAGE THE SAME WEEK: a `pgrep` guard that MATCHED ITS OWN LAUNCHER'S COMMAND TEXT and span forever.** ▶ **SO THE LAW HAS TWO HALVES: a liveness check may not be TRUNCATED, and it may not MATCH ITSELF.** ✅ The repair for both is the one `CLAUDE.md` already mandates — **confirm `/proc/<pid>/cmdline` for an EXACT PID and act on that PID only** — and the cleanest version needs no `pgrep` at all |
| 114 | ⛔⛔ **`quota.py` COUNTED A *DIRECTORY* AS A BUILT ROW, AND AGREED WITH THE TRUTH FOR NINE ROWS ONLY BECAUSE NO ROW HAD EVER BEEN HALF-BUILT** | Manager, 2026-09-14, found while landing `_051`. `quota.py:84-85` derived `built` from `glob.glob('patterns-php/ph*/')` — **directory presence**. ⭐ **The right definition was already written down in this file's own STATE cell** — *"count it: `ls results-php/gate/ \| grep -av ph00 \| wc -l`"* — **so the repo knew it and the tool used a different one.** ⛔ **It was latent for nine rows because every previous row went from nothing to fully gated inside ONE task; `_051` is the first to stop mid-row, and `quota.py` immediately reported `built 10` for a row with no `spec.md`, no `verus.rs` and no gate record.** ⚠⚠ **AND I QUOTED IT** — the corpus count in the START HERE box and in a report to the user both came from this tool. ✅ **REPAIRED: `built` is now derived from `results-php/gate/ph*.json`, a directory with no record is reported as `⏳ IN PROGRESS` and NOT counted, and a record with no directory is reported as `⛔ ORPHAN RECORD`.** ⭐ **Four §H negatives added INSIDE the tool** — N1 in-progress excluded (⭐ **and it prints `VACUOUS TODAY` rather than passing silently when no row is half-built**, F10's lesson), N2 every built row has a record, N3 `ph00` never counted, N4 no orphan records. ✅ **Now reads `built 9 · IN PROGRESS 1 · remaining 31 · T5 OWES 1`.** ⓘ Free — `.tasks-php/*.py` is in no digest. ⭐⭐ **THE CLASS: a checker can agree with the truth for a long time because the STATE THAT WOULD SEPARATE THEM HAS NEVER OCCURRED.** F49's shape (*a check that could not report its own blindness*), and the third measurement tool in this programme to be wrong in a way only a new kind of input could reveal |
| 115 | ⚠⚠ **A CONTROL THAT CANNOT RUN ON ITS OWN SHIPPED FILE — AND THE GUARD MATCHES A *COMMENT*. *"A COMMENT IS NOT CODE"*, FOURTH INSTANCE** | `TASK_PHP_053` §2.5, **reproduced by the manager**. `patterns-php/ph56-fetchmode-arith/controls/rlimit_bisect.sh` refuses its own row: *"insertion matched 2x, want 1 -- verus.rs has been respelled and this script is measuring the wrong file"*. ⛔ **Its guard greps `verifier::rlimit`, and `verus.rs`'s own COMMENT about the rlimit matches**, so the count is 2 where the guard wants 1. ⚠⚠ **`ph55`'s copy is WORSE — two comments.** ⭐⭐ **FOURTH INSTANCE OF *A CHECK THAT READS PROSE AND CALLS IT CODE***: `spelling_matches`'s original lesson, `width.py`'s guard firing on the comment documenting its own defect, `contract_audit.py`'s `labels`-as-a-noun, and now this. ▶ **REPAIR: the guard must count occurrences in CODE — strip comments before matching, or match on the attribute's syntactic position.** ⓘ **`controls/*` is in `source_sha256`, so it is a RE-GATE per row and no re-measure** — batch with each row's next task. ⛔ **AND IT PRODUCED A WRONG PUBLISHED NUMBER**: F112's *"the floor bisects to 2"* came from this script; the floor is **3** |
| 116 | ⛔ **`check.py::req-mut` DELETES PRECONDITIONS ONE AT A TIME, SO IT CANNOT SEE A JOINTLY-NECESSARY PAIR** | `TASK_PHP_053` §2.4, at `harness/check.py:6718`. **Two preconditions can each be individually removable and jointly necessary**, and a one-at-a-time stage reports both as *"NOT load-bearing"* and invites deleting both. ✅ **It does NOT bite `ph56`** — that row's **shipped** file verifies without both, which the reviewer checked rather than assumed. ⚠⚠ **A `harness/` finding: REPORTED, NOT EDITED** — `harness/check.py` is hashed into all 33 PAT gate records, so a repair is a 33-pattern re-gate (the same price as item 105's option (a)). ▶ **If item 105 is ever answered (a), BATCH THIS WITH IT** — one re-gate, two repairs. ⓘ Until then it is a caveat on any *"not load-bearing"* verdict: **it means *not individually* load-bearing** |
| ~~117~~ | ✅✅ **CLOSED AT `TASK_PHP_055` (F119) — AND THE MEASUREMENT THAT CLOSES IT WAS TAKEN BY `_050`, THE TASK THAT OPENED THE ITEM.** ⛔ Its premise *"no tool here"* is **false**: `.temp/php50/sw_ph53.json`, written 2026-09-14, records `(verus − unsafe)` at a single value **`−14.0` across all 32 argv pad residues on BOTH inputs**, with **all eight cell steps `0.00`** — and an alignment artefact is **pad-dependent by definition**. ✅✅ **The durable support is COMMITTED and was unread**: `ph53`'s gate record at its three re-gates carries `envp_stack_bytes` **3686 / 3697 / 3698** with a **bit-identical** `marginal_ir_per_call` block (md5 `79716501c531`). ⛔ **DO NOT build the sweep extension** — `.memory/03-measurement.md` gives the mechanism: **100 % of the ±7 swing is inside a libc `memset` callee**, which `kernel_exclusive_ir` excludes structurally. ⚠ **And the manager's `M4R` is defeated by the same artefact**: the sweep varies the pad across 32 residues, so it is **32 draws per input**, not the one draw I said it was. **The original text:** | `TASK_PHP_050` §10 #2, triaged as load-bearing by `TASK_PHP_053` §1.6 and **still open**. ⛔ **F96's headline `−1.253 %` rests on it.** ⚠ **The sweep tool measures the whole-program slope, NOT `kernel_exclusive_ir`, so it cannot test an A1 figure** — no tool here does. ⭐ **Counter-evidence that stands**: `_050`'s PAT census found **0 of 288**, and `_053` §1.4 makes an alignment explanation *less* likely for an A1 figure rather than more, since the axes demonstrably differ. ⛔⛔ **AND ON 2026-09-15 THE MANAGER MADE AND THEN REFUTED A CLAIM THAT WOULD HAVE CLOSED THIS ITEM FREE.** `M4`: the step is `−14.000 Ir/call` on BOTH inputs at different `n_iters`, so a whole-program offset `κ` must be 0. ⛔ **Wrong twice: (a) `php50_align_sweep.py`'s own docstring says every family-B figure is a SLOPE over `probe_iters` and *"the slope cancels"* the one-shot term, so the measured steps are PER-CALL and never divide by `n_iters`; (b) `small.bin` and `large.bin` are BOTH 9 BYTES, so both runs sit at the SAME alignment state — one draw reported twice, the `ph64` defect exactly.** ⚠⚠ **And the counter-evidence was already in the layer**: `03-numbers.md:234` records `ph45`'s `unsafe → verus` carrying a measured **`14.00` RANGE — the same rung pair** — and `ph55`'s clang cells needing `14` to protect their difference. **Three `14`s in alignment contexts.** ✅ **What survives is `M4S`, much weaker**: the two inputs do 2.5× different per-call work, so any contaminant is **per-call-constant, not per-window** — a constraint on the artefact's SHAPE, not evidence there is none. ▶ ⭐ **A cheaper route than a new tool may exist and `_055` must price it**: `php50_align_sweep.py` already runs the binaries under callgrind and parses the output, so reporting `kernel_exclusive_ir` per pad looks like an EXTENSION. ⛔ If it is, it lands with its must-fire negatives INSIDE it (§H). ▶ **Route: a dedicated task that sweeps `kernel_exclusive_ir`, OR an explicit decision to accept the PAT census and say so once.** ⓘ **Of `_050`'s seven uncertainties this is the only one still owed**; #1 closed (the wrong way, F113), #3/#4/#7 are neither cheap-and-important nor load-bearing, #5 is handled by scoping, and #6 is *"one `verus_run.py` invocation — a paragraph, not a task"* |
| 118 | ⛔⛔ **A `task-notification` MEANS *STOPPED*, NOT *FINISHED* — AND I COMMITTED A DRAFT REPORT BECAUSE OF IT** | Manager, this round. `TASK_PHP_053` notified `status=completed`; I verified the artefacts, landed the findings and committed `e0d4975`. **The agent then resumed and added 38 insertions** — the completed `ph45` `envp` sweep and, more importantly, **a scope caveat that the round's headline refutation rests on ONE ROW against THREE that agree.** ⛔⛔ **So I published F113's *"`argv` and `envp` are NOT the same knob"* as a flat general claim while the evidence was `1` disagreeing against `3` agreeing** — ⭐⭐ **which is the exact defect this programme has corrected four rounds running, committed by me IN THE COMMIT THAT LANDED THE ROUND ABOUT IT.** ✅ **Repaired in RECAP and in `.memory-php/03-numbers.md`; the refutation still stands, because one counterexample breaks an `iff` and §B5 is an `iff` — but the SCOPE now travels with the claim.** ▶▶ **THE RULE: `status=completed` is the harness saying the agent STOPPED. It may resume. ⭐ Before committing a subagent's report, DIFF IT AGAINST WHAT YOU READ** — `git diff --stat` on the report file costs one command and would have caught this. ⚠ **And rule 11's widened form already forbade it**: *do not COMMIT a file the subagent WRITES.* **I read `completed` as "the subagent is gone" when the notification's own text says it fires each time the agent stops and may fire again.** ⓘ **No research consequence beyond the scope clause** — every number in the draft survived into the final report unchanged |
| 119 | ⚠ **RE-FRAMED 2026-09-15 — `ADJUDICATION_004`: FIVE OF THE SIX NEED A *SEARCH*, NOT A RULING, AND ONE IS ALREADY ANSWERED.** ✅ **`ph90` is SOLVED** — `_054` agent B found `0542a6f2c2a5` and applied it to the pinned tarball, bytes verified; **adopt it.** ⏳ **`ph54`, `ph67`, `ph72`, `ph101` have simply never been searched** for their real repair — **ONE bounded task, scheduled WITH the row that needs it**, not now (a survey against rows nobody is building is how `_015` stalled). ⏳ **`ph74` is ROUTED** — its defect may have gone by DRIFT rather than by a fix, and R1h turns out to be OPTIONAL at the gate (`check.py` 7h: *presence of the file is the whole switch*); ⛔ **the permission was NOT written, because §C's own history records two manager drafts of that subsection refused for being permissions, and *"no repair exists"* is the most abusable one available — a failed search and a non-existent fix look identical from the inside.** ▶ **The distinction any such finding must make: `NO REPAIR EXISTS` is a result, `NOT SEARCHED` is not.** ⛔ **THE ONE REAL DEFECT WAS IN `PROTOCOL_PHP.md` §C** and is repaired: its §F5 spelling made R1h a LOOKUP on the `fix_commit` column, which F38 measured wrong 3 of 5 by hand and F118 wrong on six rows. **The column is EVIDENCE for which commit repairs the cited site, not a definition of it.** ⭐ It also makes the screen's silence readable — three of these six return `CANDIDATE`, which under the corrected spelling is exactly what it is: **nothing**. ⓘ **`CATALOGUE.md` UNTOUCHED** — editing the column would destroy F38's and F118's evidence. **The original text:** | `TASK_PHP_054` agents A, B and C, each on its own rows; `ph54` **re-verified by the manager**. **`ph67`** — the 2014 commit is a **pure refactor**; the destructor still runs on a linked bucket. **`ph72`** — six hunks, all about `userdata`, **none touches the cited `key`**. **`ph74`** — `NOT-THE-REPAIR`, and by 2006 the defect was already gone (`MAKE_STD_ZVAL` + `dup=1` + `zval_ptr_dtor` were in the tree). **`ph54`** — ✅ measured here: `fc96c7f7fa18` contains **0** occurrences of `get_current_data` and **does not touch `zend_execute.c` at all**; it is a performance refactor and the row's faulting deref and depth-1 guard both survive it. **`ph90`** — ⭐ agent B found the **real** repair, `0542a6f2c2a5` (2005-02-10, 1 file, 3+/1−, at `array.c:1045-1046`), and **applied it to the pinned tarball with `git apply` strict**. **`ph101`** — ⭐ the only genuine `NOT-THE-REPAIR` exclusion in C's nineteen. ⚠⚠ **THE CLASS IS F38's, MEASURED WIDER: *the `fix_commit` was a column in the corpus index, and it is not always THE fix.*** ⛔⛔ **AND IT IS A LESSON ABOUT THE SCREEN, NOT JUST THE ROWS: `preimage_screen.py` returns `CANDIDATE` for three of these six.** `NOT-THE-REPAIR` is the only one of its four outcomes that is a proof — **`CANDIDATE` and the two `INAPPLICABLE` labels say NOTHING**, and this is the first measurement of what that costs. ▶ **A row whose R1h is on this list is BLOCKED-ON-A-DECISION, not killed. None of the six fails the C-side bar** |
| ~~120~~ | ✅✅ **CLOSED 2026-09-15 (F120) — §A3a LANDED, AND THE FIRST ROW TO SATISFY IT MEASURED ITS CRASH BEFORE THE TASK FILE WAS WRITTEN.** `PROTOCOL_PHP.md` §A3 now reads *"in writing AND, where a reproducer exists, EXECUTED"*, with four numbered obligations, the binary named, both cautions attached, and the instrument COMMITTED at `.tasks-php/probes/segaddr.c` (§F6: a row cites the probe, never the `.so`). ⭐ `ph97`: `mb_get_info()` → `SIG11 si_code=1 si_addr=(nil)`, exit `139`; `mb_get_info("internal_encoding")` → `ISO-8859-1`, exit `0`, same binary, same run. ⛔ **RESIDUE, AND IT IS REAL: the ten rows built before this had criterion 2 ARGUED, and re-running their triggers is a separate cheap task nobody has scheduled.** ⚠ **And most TEMPORAL rows have no CLI reproducer at all**, so §A3a must not become an implicit down-rank — `CLAUDE.md` rule 6 is unchanged and *"the reproducer did not fault"* is NOT a kill. **The original text:** | F116. A working **PHP 5.0.0 CLI** sits at `…/php-in-safe-rust/.app-tests/.temp/oracle/bin/php-5.0.0-mysql-webext` and the corpus ships a **reproducer per id**, and **no manager-owned document points at either** (measured: zero mentions across `CLAUDE.md`, `PLAN_PHP.md`, `RECAP_PHP.md`, `PROTOCOL_PHP.md`, `CATALOGUE.md`, `SOURCES.md`, `.memory-php/`). ▶ **THE ACTION: `PROTOCOL_PHP.md` §A3 says *"reachability is deliverable #1, in writing, before any rung exists"* — it should say *in writing AND, where a reproducer exists, EXECUTED*, with the binary named and `LD_PRELOAD`'d `si_addr` as the cheap instrument** (no gdb on this box; memcheck refuses to start). ⚠⚠ **Two cautions that must travel with it**: the binary is **`php-in-safe-rust`'s oracle build, not a museum-default one**, so a row must say which build it measured on; and **`crashes_pristine_5_0_0 = False` is still not evidence of absence** (F3) — ⭐ **but `= True`, executed, is now evidence of PRESENCE, which the programme has never had.** ⓘ **Cost: a `PROTOCOL_PHP.md` edit, which is in no digest.** ⛔ **It does NOT retroactively validate the ten built rows** — their criterion 2 was argued, and re-running them is a separate, cheap, and probably worthwhile task |
| ~~121~~ | ✅✅ **CLOSED 2026-09-15 — `ADJUDICATION_003`. ROUTE (a): the floor is `Σ min(2, |family|)` = **37**, DERIVED in both `quota.py` and `task_cost.py` from the same parse, with `N5`/`N5b` (and `N5b` declares itself VACUOUS rather than passing silently if the singletons ever disappear).** ⛔⛔ **THE NUMBER IS THE LEAST OF IT: route (a) CONCEDES that `S5`, `S6` and `T4` can never produce a family-level finding**, which is the thing `QUOTA_001` gives min-2 a REASON for (*"n = 1 cannot detect the S1 effect"*) and which `ph55`/`ph56` measured — one family, one fix shape, two completely different harms. **Recorded as a known limit of the corpus, not an accounting detail.** ⛔ **Route (b), MERGING the singletons, is REJECTED**: it fixes at most one of three, `S6` is a singleton *because* it was routed away once already, and it is set-level reasoning replacing row-level reasoning — the mechanism that made `C.1` wrong 17 times. ⏳ **Route (c) stays OPEN as a MEASURABLE question** — *does any of the 64 non-row corpus ids belong in `S5`/`S6`/`T4`?* **A clean negative closes it.** ⭐ (a) and (c) are not exclusive: the derived floor grows on its own if the catalogue does. ⭐⭐ **AND THE ADJUDICATION FOUND SOMETHING BIGGER THAN THE DECISION** — `T6`'s family name is FALSE of three of its five members and `CATALOGUE.md` says so itself; `ph54` (`T4`) and `ph97` (`T6`) are the same sentence. **ROUTED, NOT ACTED ON** (`ADJUDICATION_003` §4); renaming `T6` costs nothing and is not a merge. ⚠ **It affects ROW 12**, whose point is a family-level finding. **The original text:** | `TASK_PHP_054` agent C, §1.2, from `quota.py`'s own output. `S5` (`ph37`), `S6` (`ph38`) and `T4` (`ph54`) each contain **exactly one** row, while `QUOTA_001`'s rule is *"min 2 per family, cap 4"* and the published floor is **20 families × 2 = 40**. ⛔ **So the floor counts six rows that cannot exist unless the catalogue grows.** ⚠⚠ **STATED AS PROGRAMME ARITHMETIC AND EXPLICITLY NOT AS A DOWN-RANK** — all three rows pass the C-side bar and agent C says so in terms (`CLAUDE.md` rule 6). ▶ **THREE ROUTES, and the manager owes a choice**: (a) the floor becomes `min(2, |family|)` summed, which lowers it by **3** to 37; (b) those families are merged into their nearest neighbour, which is a catalogue change and needs its own adjudication; (c) the catalogue gains rows there from the 8 withdrawn `C.1` kills, which is where the original members went. ⓘ **`task_cost.py`'s projection is unaffected** — it counts rows owed, not families — but **`quota.py`'s `floor = 40` is quoted in the START HERE box's *"30 owed"*, so the choice changes a published number** |
| 122 | ⭐⭐ **THE TEN ROWS BUILT BEFORE §A3a HAD CRITERION 2 *ARGUED*, AND RE-RUNNING THEIR TRIGGERS IS CHEAP** | The residue of closed item 120 / **F120**, recorded separately so it does not die inside a struck row. `PROTOCOL_PHP.md` §A3a now requires a row to EXECUTE its `▸ trigger` where a reproducer exists; **`ph03`, `ph07`, `ph16`, `ph29`, `ph45`, `ph52`, `ph53`, `ph55`, `ph56`, `ph64` predate it** and each states its C-side reachability in prose only. ⓘ **Cost: one task, no build, no gate** — the binary and the `LD_PRELOAD` instrument both exist, and `TASK_PHP_054` agent B already ran 36 corpus reproducers this way in a single sitting. ▶ **What it buys:** the first ten rows' criterion 2 moves from ARGUED to MEASURED, and any disagreement is itself a finding (`PROTOCOL_PHP.md` §A4: *reproducing a DIFFERENT signal is a finding to state, not a failure to hide*). ⛔⛔ **WHAT IT CANNOT BUY, AND THE TASK MUST SAY SO IN ITS OWN BRIEF: a row whose trigger does NOT fault is NOT down-ranked** — F3, and `CLAUDE.md` rule 6. **A clean run is not evidence of absence and is not a kill.** ⚠ Several of these rows have no single-line PHP reproducer (the temporal ones especially); for those the honest answer is `NO CLI REPRODUCER`, recorded, not a blank |
| 123 | ⚠ **A CAUTION WRITTEN IN A README DOES NOT TRAVEL INTO THE TOOL THAT REPLACES THE README'S PROCEDURE, AND NOTHING CHECKS THAT IT DID** | **F122**, and the rate rather than the instance. Three un-inherited cautions are now on file — F108's C-compiler rule, `_env_block`'s three-equal-fields caution, and `citecheck.py` never inheriting `.tasks-php/README.md`'s *"ignore a MISSING report for a task that is still open"* — **and all three were found by accident, one per round.** ▶ **THE QUESTION, AND IT IS NOT YET A PROPOSAL: is there a cheap mechanical form?** A candidate: when a tool replaces a documented manual procedure, its docstring must name the document it supersedes, and a checker asserts every ⚠/⛔ paragraph in that document is either implemented or explicitly declined. ⛔ **I have not costed it and it smells like a heuristic over prose — the class that has already produced five false-positive rot entries this programme** (`a check that reads prose and calls it code`). ⚠ **Recorded as a PATTERN WITH NO REPAIR, deliberately.** Three instances is a rate; it is not yet a design |
| 124 | ⭐⭐ **THE SWEEP CANNOT TELL *A TASK IS IN FLIGHT* FROM *SOMETHING ROTTED*, AND IT IS NOW MEASURED IN TWO DIFFERENT CHECKERS** | **F122** and a live instance. `citecheck.py`'s rot rose while `_054`'s three **split-named** reports were unwritten (**repaired**); and on 2026-09-15 `contract_audit.py` went RED mid-build, its `N8` ratchet reporting three UNFILED `VERDICT` hits in `ph97`'s `c/*` **because `_056` was still writing them**. ⭐ **The ratchet was working perfectly** — the first hit was REAL and the sentence moved to `NOTES.md`; the other two were filed with reasons. ⛔ **What is missing is CONTEXT: `checkers.py` files `contract_audit.py` as `expect=0` and a reader meets a failure with no way to tell which kind it is.** ▶ **The repair's shape already exists**: `quota.py`'s `N1` prints `⏳ IN PROGRESS` for a row with a directory and no gate record, and declares itself `VACUOUS TODAY` rather than passing silently (item 114, F10). ⛔⛔ **DO NOT SUPPRESS THE RED** — an unfiled adjudication SHOULD block. **LABEL it.** ⓘ Not done on the day because `_056` might have been reading the file (`PROTOCOL.md` rule 11) |
| ~~125~~ | ⭐⭐ **HOW MANY *"CHEAPEST REMAINING CHECK"* ITEMS SIT IN A `WHAT I AM UNSURE OF` SECTION, DEMOTED ONCE AND NEVER REVISITED?** | **F123**, and it is the question the manager cannot answer about the manager. `_051` §8.1 called the PHP-rebuild check *"the cheapest remaining"*; `_052` §1.5 demoted it to *"nice to have, skip it"*; two rounds later a different agent said *"I cannot"*; today it was absent from a protocol section. ⛔ **No step was a lie, and nothing in this repo would have caught it.** ▶ **A COUNT OVER THE `§ WHAT I AM UNSURE OF` SECTIONS OF THE LANDED REPORTS WOULD ANSWER IT** — every build and review report has one, by DoD. ⚠⚠ **THE MANAGER DELIBERATELY IS NOT THE ONE WHO SCOPES IT**, because the finding is about the manager's own demotions. ▶ ~~**Give it to a reviewer~~ ✅ **RULED `_063` §6.3 — THE CENSUS RAN.** ⭐ **The layer-shaped claim it would test**: *an engineer's own uncertainty may be DEFERRED but not DOWNGRADED; the next task inherits its STATED priority, not the manager's.* ⛔ **Not in `.memory-php/` and not going there unreviewed** ✅✅ **CENSUS RUN AT `_063` §6.3: 66 reports → 80 sections → 631 items → **27 MEMBERS**, of which **2 CONFIRMED** and 25 await one read each.** ⛔ **AS SPECIFIED THE ITEM IS REFUTED — a LINE-level grep misses `F123`'s own founding instance**, so the question had to be re-specified to be answerable. ⭐⭐⭐ **AND THE RESULT IS BIGGER THAN THE COUNT: `F123`'s repair was a PROSE BOX; three rounds carried it in capitals and NONE DID THE WORK; `F140`'s printing ARM scoped it on its FIRST RUN.** ▶ **That is `F139`'s corrected axis — text vs an invoked arm — demonstrated on `F123` itself.** ⛔⛔ **STILL OPEN AND IT IS THE REVIEWER'S #1 RESUME PRIORITY, WHICH BINDS ME (`F123`): hand-adjudicate the 25 remaining members. COST ~15 MINUTES, the extractor is written.** ⛔ **DO NOT RE-ESTIMATE IT AT AN HOUR — that estimate is why it sat for six rounds** ✅✅✅ **DONE 2026-09-16, THE SAME DAY `_063` ORDERED IT FIRST — AND THE ARM IS THE DELIVERABLE, NOT THE NUMBER.** `.tasks-php/probes/item125_extract.py` derives the population (66 reports → 80 uncertainty sections → 631 items → **27 candidates**) and `.tasks-php/probes/item125_demoted.py` carries the hand adjudication with 5 must-fire arms. ▶ **THE SET: 7 MEMBERS · 16 TRACKED · 4 NOT-AN-ITEM.** ⭐⭐ **THE MEMBERS** — `_032` the index-scan R3 `forbidden[2]` pins absent · `_035` a fifth R4 spelling for that row · `_055` the period-16 finding is ONE unreproduced series · `_058` do the two `inside_share` definitions ever disagree in **SIGN** · `_058` *“byte-identical in all four rows”* is enforced by nothing · `_059` was the sweep's `59` ever right · `_062` is the two-level `inside_share` sweep too slow to re-run. ⭐⭐⭐ **FOUR OF THE SEVEN COME FROM `_058` OR LATER, SO THE CLASS IS STILL FORMING — it is not a backlog left over from the mining wave.** ⭐⭐⭐ **AND ONE MEMBER IS LOAD-BEARING FOR `_063`'s OWN RULINGS**: `F146` and item 137 both push toward REQUIRING a row-level two-level matrix, and `_062` asked whether a row can AFFORD one — **nobody has measured it.** ▶ ***A cost nobody has measured is exactly how `F123` happened.*** ⛔⛔ **N4 REFUSED ITS OWN AUTHOR'S HAND VERDICT WITHIN MINUTES**: I marked `_035` TRACKED on the token *“four spellings”*, which recurs in three earlier reports about unrelated things — **a generic token manufacturing tracking that did not exist.** ▶ **That is `_063` §6.3(c) demonstrated a second time inside its own repair: an invoked arm beats a prose box.** ⚠ **The tracking test is a PROXY and both files say so** — token recurrence is weaker than an answer, so it can only move a row OUT, and **the printed member set is a LOWER BOUND.** ⛔ **STRUCK, because the question is answered and the seven members are now PRINTED rather than remembered; each is its own work item and none is hidden** |
| 126 | ⚠ **`PROTOCOL_PHP.md` §A3a IS INCOMPLETE BY ONE OBLIGATION, AND WHETHER TO ADD IT IS A REAL TRADE** | **F123**. The fifth obligation — *re-run the trigger against the R1h POST-IMAGE build* — would make the upstream fix's efficacy measurable on real PHP, and the reason it was omitted was false. ⛔ **But it is NOT simply owed.** ▶ ~~**The trade, stated so a reviewer can rule~~ ⛔⛔ **RULED `_063` §4.3 — THE TRADE DOES NOT EXIST on it: REQUIRING it makes every row pay for a full PHP compile, and §A3a's entire merit is being cheap enough that nobody skips it; PERMITTING it may mean nobody ever does it.** ~~⚠ **And a third question nobody has answered: what does it buy over verifying the applied post-image BYTES, which `_056` did without building anything?**~~ ✅✅ **ANSWERED 2026-09-16, BY MEASUREMENT, ON `ph66`**: verifying bytes tells you the patch **applied**; it cannot tell you the program's **answer changed**. On `ph66` the byte check passes and says nothing, because **`rc=0` on both sides and the whole difference is in stdout**. ▶ **On a row whose target error is a VALUE, only RUNNING the post-image says the repair works.** ⚠⚠ **AND `F141` ADDS A LEG THIS ITEM DID NOT ANTICIPATE**: it framed the trade as *REQUIRING* vs *PERMITTING*, and what landed was a third thing — **REQUIRED-BUT-GATED**, exempting precisely the rows where the check is most informative. ✅ **Re-worded 2026-09-16 on `_062` §8.1's proposal.** ▶ **Scope this into `_063` beside `F141`; they are one question** ⓘ **Routed to `TASK_PHP_057` §1.2 with the manager's own answer registered as a prediction (`P1b`) and predicted to be wrong.** ⚠ **Until it rules, §A3a must not read as complete** ⛔⛔⛔ **CLOSED AT `_063` §4.3: THERE IS NO TRADE, BECAUSE THE COST PREMISE IS FALSE BY ~100× — AND THE MEASUREMENT IS IN THE SAME FILE AS THE RULE, FOUR LINES BELOW IT.** A row does not pay for *a full PHP compile*; it pays **30 s cold + ~600 ms incremental**, measured twice. ▶ **With the cost at ~0 there is nothing to trade**, and the item's framing is **`F123` recurring inside the item `F123` opened.** **PERMITTING ⛔ REFUTED** (a permitted 30-second check is still not done, because nothing makes anyone look) · **REQUIRING ✅ CORRECT, its only objection void** · **REQUIRED-BUT-GATED ⛔⛔ THE WORST OF THE THREE** — it exempts precisely the rows where the check is most informative **and it reads as required, so nobody re-opens it.** ✅ **The obligation-5 wording is re-written accordingly and the one-day-old *“REQUIRED WHENEVER…”* text is OVERTURNED — applied to `PROTOCOL_PHP.md` §A3a, not appended beside it** |
| 127 | ⭐⭐⭐ **FIVE BUILT ROWS NEVER MEASURED `inside_share`, AND THREE OF THEM PUBLISH AN `A1` HEADLINE — MEASURE `ph03`, `ph16`, `ph29`** | **F127**, and **`TASK_PHP_057`'s BINDING resume priority**: *"more important than any finding in this round, including the one it came out of."* ✅ **Manager-verified across all eleven rows**: only `ph97` has a dedicated control; `ph29`/`ph45`/`ph52`/`ph55`/`ph56` carry a value somewhere; **`ph03`, `ph07`, `ph16`, `ph53`, `ph64` have NONE.** ⛔⛔ **`ph29` is worse than missing**: its only figures live in a **docstring in `controls/spellings.py`** which says in terms that **A1 is not right for this row's C-vs-Rust column and *"that comparison is not made here"*** — while this file's *which statistic* cell publishes exactly that comparison (*"A says C is +33 % dearer"*) from this row, **the row at the centre of the programme's largest open thread.** ⚠ **CORRECTED by `F129`: *"exactly that comparison"* is ONE RUNG OFF** — the docstring disclaims C vs `safe_tuned`, the cell publishes C vs `safe_naive`. **Both fail the written bar by >11×, so the point stands and gets stronger.** ✅✅ **LANDED AS `TASK_PHP_058` — AND IT DID NOT CLOSE THIS ITEM.** ⭐ Three of the five rows now have a measured matrix (`ph03`, `ph16`, `ph29`), plus `ph97`'s template rewritten byte-identical across all four and re-gated. ⛔ **`ph07`, `ph53` and `ph64` STILL HAVE NONE** — the scoping was correct (the reviewer named the three rows that publish an `A1` headline) but **the item must not be ticked at 3 of 5**, which is `PROTOCOL.md` rule 13's trap. ▶ **RESIDUE: `ph07`, `ph53`, `ph64`, cost measured by `_058` and carried in its §8.** ⭐⭐ **What it bought is bigger than the gap it closed: `F129` — two quantities wear the name `inside_share`, and the `+33 %` flips sign between the two C compilers.** <br><br>⛔⛔ **AND THIS CELL SAID *"ENGINEER TASK, ~20 min + 3 re-gates"* BEFORE ANY OF IT WAS MEASURED — which is `F123`'s own defect, committed in the item that exists because of `F123`.** ✅ **Measured at `6bff271` before dispatch**: one re-gate **2 m 29 s** (`ph03`, `check.py: PASS`); one callgrind run **6.6 s** on the heaviest cell (`ph03/safe_naive-O3-isolated`, `large.bin`, 1.44 G Ir), so the 16-run matrix is **~2 min**; the `kernel` symbol **survives** at `O3/isolated` (95.03 % on that cell). ⛔ **And it is FOUR re-gates, not three** — `ph97`'s template hardcodes `n_iters` where `slb.read` derives it, and fixing the template in the same edit is what stops the *"fixed one limb"* class recurring. ⭐ **The estimate was roughly right. Being right by luck is not being right, and that is exactly what `F123` says.** ⚠ **`.memory-php/03-numbers.md` treats `inside_share` as a live per-cell discipline; on 5 of 11 rows it was aspirational when this item opened — **3 of 11 now** (`ph07`, `ph53`, `ph64`), and the layer gained the two-definition caution `F129` forced.** ⛔ **The manager's own task file asserted *"`inside_share` is in every row's `controls/` already"* — a rule-14 premise, false, and the reviewer checked it instead of believing it** |
| 128 | ⚠ **`F119` MUST BE RE-STATED ON ITS REAL EVIDENCE, AND THE REAL ONE IS STRONGER** | **F127** / `_057` §3.3. `F119`'s conclusion is UPHELD and UNDER-STATED — **96 cells (48 `isolated` + 48 `whole`), three `envp_stack_bytes` draws, bit-identical, md5 reproduced by an independently chosen recipe.** ⛔ **Its REASON is a category error**: *"100 % of the ±7 swing is inside a libc `memset` callee, which `kernel_exclusive_ir` excludes structurally"* is a claim about **A1**, yet **half the evidence is the `whole` column, which that immunity cannot protect** — the finding explains the stability of column Y with the immunity of column X. ⛔⛔ **And the `memset` fact is another pattern's**: `ph53`'s own `NOTES.md` §8b says its `memset` (`8·n_decl ≤ 128` B) is **inlined to `xmm` stores, inside `kernel`, not a libc callee**; `__memset_avx2_unaligned_erms` is a **`p03`/PAT-side** measurement. ⚠ **The record's own `domain` field forbids the comparison F119 makes** (*"comparable ONLY against a record with the same `envp_stack_bytes`"*). ▶ ⭐ **THE STRONGER STATEMENT: the ±7 term did not fire on this row at all, on three draws, INCLUDING in the vulnerable column — so the `domain` guard is more conservative than this row needs.** ⓘ Item 117 stays CLOSED either way. <br><br>⭐⭐ **NEW, AND IT IS A SECOND ROW ON AN *ACCIDENTAL* DRAW.** Quoted as an EVENT: I re-ran `python3 harness-php/gate.py ph03-uudecode-bound` at `6bff271` with **no source change**, purely to time it, and diffed the record against the committed one. **`envp_stack_bytes` moved `3695 → 3698`** (`bytes` `3303 → 3306`, `nvars` 49 both times) — so the record's own `domain` field declares the two runs **incomparable** — and **all 96 `marginal_ir_per_call` cells came back byte-identical, including the `whole` column that `A1`'s structural immunity cannot protect.** The only lines that moved were **4 ASan PIDs/ASLR addresses and 2 wall-clock timings**; `check.py: PASS`. ⛔ **This does NOT show the ±7 term is absent** — `TASK_114` measured it firing — and a **+3-byte** draw may land in the same stack-alignment bucket, **which nobody has tested.** ▶ **Two rows now, one deliberate and one accidental, both saying the guard is more conservative than the row needs.** ⓘ The run was reverted: its measured content was identical, so committing it would have added PID churn and no evidence |
| 129 | ⭐⭐ **THE `WHAT I AM UNSURE OF` CENSUS — AND THE REVIEWER SAYS TO SCOPE IT ANYWAY** | **F123**/**F127**, item 125's successor with a ruling. The manager wrote that he *"deliberately is not the one who scopes it"* because the finding is about his own demotions. ⛔ **`TASK_PHP_057` §9 item 4 overrules that: *"Scope it anyway — F123 is one instance and the whole finding is that the RATE matters, not the instance."*** ⭐ **That reviewer priority BINDS** (the task file said so, and F123 is the record of what happens when a stated priority is re-ranked). ▶ **THE TASK: every landed `_REPORT.md` has a `WHAT I AM UNSURE OF` section by DoD; count the items, and for each ask whether the NEXT task inherited it, demoted it, or dropped it silently.** ⭐ **The law it would test, in `_057`'s strengthened wording**: *an engineer's own estimate of a check's COST is evidence, and demoting a check on cost grounds without measuring the cost is `PROTOCOL.md` rule 14.* <br><br>⛔⛔ **SCOPED 2026-09-15, AND THIS ITEM'S OWN PREMISE IS FALSE.** *"Every landed `_REPORT.md` has one by DoD"* — **measured: 27 of 61 do; 34 do NOT.** The first is `_020`, the last without is `_040`, and it is **universal only from `_041`**. ⭐ **The 13 reports that skipped it AFTER the convention started (`_021`–`_028`, `_032`, `_036`, `_038`, `_039`, `_040`) are the census's FIRST RESULT, not an exclusion**: a report stating no uncertainty cannot have one demoted — **it skipped the step, and nothing noticed for twenty tasks.** ⛔ **Two of the 27 are false positives of the keyword search, in different ways**: `_057` merely DISCUSSES such sections (⚠ **any census keyed on the phrase matches every document about the census**), and `_048`'s match is a DoD row pointing at the section in the ROW's `NOTES.md`. ▶ **So the denominator is ≈ 289 items over 27 sections — 261 in 25 reports plus 28 in two rows' `NOTES.md` (`ph55` 21, `ph52` 7)**; median 10, largest `_044` at 19. ✅ **The counter is validated**: it reads `ph55` as 21 and `_048`'s independently-written DoD row also says 21. ⛔⛔ **~289 judgements, each needing a search of every later document, IS NOT A ONE-TASK JOB, and this item reads as if it were.** ▶ **The task file must pick a shape and SAY WHY** — full census · ⭐ mechanical pass + hand adjudication of the residue (the house ratchet, **but *mentioned later* must NOT be scored as *inherited*: the mechanical pass finds the DROPPED, only reading finds the DEMOTED, and demotion is the finding**) · or a stated sample. ⚠⚠ **Choosing a cheaper shape is fine; choosing it without saying so is the exact defect under audit.** ⚠ **`_057` overruled the manager on SCOPING it, not on EXECUTING it — a REVIEWER runs the census.** ⛔ **Not in `.memory-php/` and not going there unreviewed** <br><br>⭐⭐⭐ **A DATED INSTANCE ARRIVED 2026-09-15, AND IT IS THE FIRST WHERE THE UNANSWERED ITEM WOULD HAVE PREVENTED A PUBLISHED ERROR — WHICH IS THE STAKES THIS ITEM HAS LACKED.** `ph03`'s `NOTES.md` routed the manager a question — *"whether `F74`'s rule should exempt an `identity`-pinned pair is the manager's to rule on"* — attached to a measured counterexample: **(ii) rejects the one pair whose true A1 difference is KNOWN to be exactly zero.** ⛔⛔ **He did not rule, and then published `F129`'s *"INADMISSIBLE on the row's own written bar"*, which that paragraph refutes.** `TASK_PHP_059` spent a round re-deriving the same conclusion from a different row. ▶ ⭐ **THE LAW IT SHARPENS, and the census should be scoped to TEST THIS rather than merely to count: a question ROUTED TO THE MANAGER AND NEVER ANSWERED IS NOT NEUTRAL — it becomes a claim he is free to contradict without noticing.** An open question reads as open; an **unanswered** one reads as nothing at all. ⚠⚠ **So the census's unit may be wrong**: it was scoped over `WHAT I AM UNSURE OF` sections, and **this item was not in one** — it was a routed ruling request in a row's `NOTES.md`. ▶ **A census that only reads report sections will miss the class with the highest stakes** |
| 130 | ⭐⭐ **DO ANY OF THE OTHER ARMS ASSERT AN EFFECT'S *DIRECTION*? THE SWEEP `F128` OWES AND DID NOT RUN** | **F128**. Two arms are now known to have asserted a sign and so reported the DATA as the failure: **`N11`** (the first-in-family premium, `F126`, refuted at n = 8 after standing on n = 1) and **`N13`** (*"an unsearched row can only make the all-rows figure LOOK cheaper"* — refuted the day it was written, by a task charged to an unsearched row). ⛔⛔ **`F126`'s repair fixed `N11` and never asked the question about any other arm** — the *"fixed one limb"* class (`F122`, `F127`) for the **third** time, this time inside the repair of a finding about incomplete repairs. ▶ **THE SWEEP: read every arm's predicate in `.tasks-php/*.py` — count them with the tools, never from this sentence for a comparison whose direction is an EMPIRICAL claim rather than a definition, and for the cheaper tell — ⭐ *a predicate asserting more conditions than its own comment justifies*, which is how `N13` was found without any refuting datum.** ⚠ **The tell is a hypothesis from n = 1; the sweep is what would make it n > 1 or kill it.** <br><br>✅✅ **SWEPT 2026-09-15 — manager, read-only, 59 arms across 4 files, AND THE SWEEP NARROWED ITS OWN RULE.** ⓘ Its full write-up is folded into this cell rather than cited from scratch: a committed doc pointing at deletable `.temp/` is `CLAUDE.md` rule 1's own trap, and the first draft of this cell did it. ⛔ **`F128` as worded (*"an arm must not assert a sign"*) IS WITHDRAWN: applied literally it damages FIVE CORRECT ARMS.** ⭐⭐ **The arms split in two and only one kind is defective: (A) a REPRODUCTION arm re-asserts a PUBLISHED finding so the tool speaks when it stops reproducing — `width.py` `N4`/`N3b`, `php_null.py` `N8`/`N9`/`N7b`; firing is the POINT. ⭐ Two of them are the model to copy because they assert a FLOOR and PRINT THE MEASURED MARGIN BESIDE IT, so the margin is visible shrinking. (B) a PROJECTION arm asserts the direction of something still being ESTIMATED, where the opposite outcome is a legitimate RESULT — `N11`, `N13`, and ⛔⛔ `task_cost.py` `N5`, THE THIRD INSTANCE** — ⛔⛔ **and this cell said *"STILL UNREPAIRED"*, which was a LIVE FALSE CLAIM caught by `TASK_PHP_059` §4. The repair landed at `d9652b4`, ONE COMMIT after this cell was written, and survived two later commits INCLUDING A PRE-COMPACT AUDIT that was looking for exactly this.** ⭐⭐ **The mechanism is the cell's own subject: I wrote the item, did the repair in the next commit, and never came back to the sentence that said it was owed — *two homes for one fact* (`F131`), in the item about arms that report a changed conclusion as a failure.** ✅ `N5`'s `not rising` **IS** demoted to an `ⓘ` report; its variation-floor conjunct stays. ⚠ **`N6` (`dear == "ph07"`) is NOT a defect today and NOW HAS A RETIREMENT CONDITION and a printed margin** (also `d9652b4`) — a registered prediction with no expiry becomes a pin. ✅ **Cleared on inspection**: `N3`/`N4`/`N7` only LOOK directional — `marg <= pub` holds **by construction** (`spread` excludes ONCE/METH/PENDING; `PESSIMISM` only moves tasks INTO rows), so their empirical content is the constant alone. ⛔ **SIX CHECKERS UNSWEPT** — ✅ **`cbaseline_check.py` SWEPT AT `_059` §4; FIVE REMAIN**: `quota.py`, `citecheck.py`, `contract_audit.py`, `preimage_screen.py`, `fixsurvey.py` use a different arm spelling and were not read. ▶ **The reviewer's standing instruction, which BINDS: *fold a half-hour into another task; do NOT dispatch one for it* — and *put the margin clause into the rule BEFORE sweeping anything else*, because that is what makes a sweep's output actionable.** ✅✅ **THE RULE IS LANDED, NARROWED, IN `.memory-php/04-process.md` AS LAW 16** — with **both** sentences the reviewer said it was missing: the split is a property of the arm's RELATION to a finding's **current status** (`N11` changed kind with no edit to it), so **an arm asserting a published direction without printing its margin is an offending arm that has not been caught yet**; and **every such arm needs a written retirement condition.** ⓘ **The sweep's own census miscounted first** (60/17 from a `grep` that read a `check("N15b"…` quoted INSIDE a comment; recounted 59/16 and cross-checked against what the tools PRINT — **item 115's class, inside the sweep hunting item 115's class**). ⛔ **Not in `.memory-php/` and not going there unreviewed** |
| 131 | ⚠ **`N12` CANNOT READ THE ARM DIALECT A GROWING SET OF TOOLS SPEAK, SO IT COULD NOT TELL IF THEY WENT SILENT** | **F129**/`_058`. `N12` derives every *"&lt;n&gt; arms"* claim from what a checker PRINTS, matching `PASS`/`FAIL`/`OK` beside an `N&lt;digits&gt;` name. ⛔ **`controls/inside_share.py`, `php58_mutate_arms.py` and `php58_record_share.py` all print `ok &lt;n&gt; &lt;name&gt;` — lowercase, numeric, no `N`** — so `N12` scores them **0 arms** while they run 7, 6 and 7. ⓘ **It fired correctly in form**: it refused a registry entry of mine claiming 7. ▶ **The count was REMOVED from the `why` rather than the regex widened** (the registry's own rule, and *"the fix is no number, not a better one"*). ⛔ **The residual is real: `N12`'s silent-checker guard does not cover these three.** ▶ **Normalising the dialect would cost FOUR RE-GATES** (`inside_share.py` is hashed into four rows' `source_sha256`), which is why it is an item and not a same-day fix. <br><br>⛔⛔ **AND THE TITLE SAID *"THREE NEW TOOLS"* UNTIL 2026-09-15: `_059`'s `php59_share.py` SPEAKS THE SAME DIALECT, SO IT IS FOUR.** ⭐ **A count in the title of the item about an un-countable set** — `F121`'s class, in the item about a checker that cannot count. ▶ **No number lives here now; derive the set by running the tools and looking for `ok` without an `N<digits>` name.** ⚠ **The residue GREW while the item sat open, which is the argument for closing it rather than the argument for its cost estimate** |
| 132 | ⭐⭐ **`F74`'s CONDITION (i) HAS NO THRESHOLD, AND AT ELEVEN ROWS IT IS NOW CHEAP TO PIN** | **F129**/`_058` §9.4. `.memory-php/02-ladder.md`: the bar is **(i)** `min(inside_share)` HIGH **and (ii)** `|Δinside_share| ≤ 0.02`, and *"the threshold in (i) is **not tuned and six rows cannot pin it**"* — `>0.3`, `>0.5`, `>0.6` all give 0 flips. ⭐ **There are ELEVEN rows now and 360 evaluable cells.** ▶ **The sweep reads committed records and builds nothing** — `.tasks-php/php58_record_share.py --pairs`. ⚠⚠ **Do it in `F74`'s spelling, not the control's — they are different quantities (F129), and pinning the threshold of the wrong one would be worse than leaving it open** <br><br>✅✅ **CLOSED 2026-09-15 BY `TASK_PHP_059` §1.3a, AND THE ANSWER IS *DO NOT FIT IT*.** Swept in `F74`'s spelling as instructed, eleven rows, `O3`/`isolated`, both inputs, with `.tasks-php/php59_share.py sweep`. **(i) is VACUOUS on the cross-language column at every `t` in `[0.00, 0.90]`** — 0 of the 17 (ii)-survivors are killed. ⛔ **And the manager's `P3` REASON is refuted**: it is *not* that (ii) already failed on the rest. **All 17 survivors sit at min-share ≥ 0.9019**, because (ii) forces the two shares together and the close-shared cross-language pairs in this corpus are all high-share pairs. ⛔⛔ **SIX OF THE SEVENTEEN ARE ADMITTED ON A MIN-SHARE ABOVE `1.0`** — the item-133 pathology **inside the bar's own verdict**. ⭐ **Same-language (i) IS load-bearing** (10 kills at `t = 0.10`, 18 at `0.50`, 37 at `0.90`) — **but the population that would pin it, same-language flips passing (ii), is `ph45` ALONE, `n = 1` row.** ▶ ***A threshold fitted on one row's pathology is not a threshold.*** **So eleven rows still cannot pin (i), and the reason is now SPECIFIC rather than *"not enough rows"*.** ✅ **Landed in `.memory-php/02-ladder.md` beside `F74`'s rule** — it is reviewer work, so rule 9 permits it. ⓘ **The sweep also settled something the item did not ask: the bar is not a gate at all** (`F129` §3, withdrawn) |
| 133 | ⛔⛔ **`F74`'s SHARE EXCEEDS `1.0` ON 15 OF 360 CELLS, AND A SHARE OF THE WHOLE CANNOT** | **F129**/`_058`. ✅ **Manager-reproduced independently: exactly 15**, largest `ph07` `c-gcc`/`large` at **`1.0353`**, concentrated in `ph07` and `ph16` at `O3/isolated`. ⚠ **The proposed mechanism — numerator over `n_iters` calls, denominator a SLOPE at `collapse.probe_iters` — is consistent with the arithmetic and was NOT isolated**; it could equally be a start-of-run transient (`F93`'s shape). ⛔ **Do not quote the mechanism as measured; the engineer said so unprompted.** ▶ **The cheap discriminator: recompute the marginal at `n_iters` on one offending cell.** ⭐⭐ **THE STAKES: this quantity DECIDES WHICH STATISTIC MAY PUBLISH (`F74`'s two-condition bar), and it is out of range on 4 % of the corpus.** <br><br>⭐⭐ **THE SHARPEST SINGLE DATUM, manager-verified**: `ph16` `c-gcc`/`isolated`/`small.bin` — **the same row, cell and input** — reads **`0.0418` at `O0`** and **`1.0241` at `O3`**. `A1` is `476.48` vs a marginal of `11401.39` at `O0`, and `3683.26` vs `3596.61` at `O3`. ▶ **A 24× swing, from *A1 sees almost nothing* to *A1 sees more than the whole*, moved by the optimisation level alone.** ⛔ **I am deliberately NOT proposing a mechanism** — that is this item's whole point, and the engineer declined to as well |
| 134 | ⚠⚠ **`cbaseline_check.py` ENFORCES FOUR-FIFTHS OF THE RULE IT EXISTS FOR: ONE C COLUMN PASSES IT** | **F129**/item 130's sweep. `.memory-php/03-numbers.md` states the fifth thing as *"WHICH COMPILER — **with both columns, or an explicit statement that only one was measured.** ⛔ One column is not a number with error bars on it; it is a DIFFERENT SIGN."* ⛔ **But `scores()` is `MAG and XLANG and not BASE`, where `BASE` matches `c-gcc` OR `c-clang`** — so a sentence naming EITHER is deemed labelled. ⭐⭐ **And its `N2` arm, the exemplar it holds up as *"a correctly labelled claim"*, is `` `ph29/large`, `c-gcc` vs `safe_naive`: A says C is +33.01 % DEARER `` — ONE column, of the very pair whose columns have OPPOSITE SIGNS.** ⓘ **The enforcer's model of compliance is itself one item short of the rule.** <br><br>✅ **SCOPE MEASURED BEFORE OPENING THIS, and it is small: of the scanned corpus, 5 lines name BOTH C columns and 2 name exactly one** — and ⭐ **on inspection BOTH of those two are FINE**: `.memory-php/02-ladder.md` gives the `c-clang` swap in full two lines later, and the `RECAP_PHP.md` hit sits inside `F108`'s own discussion. ⛔ **So there is NO live violation — the finding is that nothing would have caught one**, plus the artefact that a **line-based** scan cannot see a claim whose two columns are one sentence apart. ▶ **The repair is cheap and is NOT a corpus job**: make `BASE` demand both spellings (or an explicit *"only one measured"*), re-adjudicate the handful of hits BY HAND, and fix the `N2` exemplar. ⚠ **It WILL move the `RATCHET` count — that is the point of a ratchet, and every new hit is adjudicated, never regex-tuned** <br><br>✅✅ **RULED AND CLOSED 2026-09-15 BY `TASK_PHP_059` §2.2 — AND THE RULING IS *REFUSE THE WIDENING AS FRAMED*, AN EIGHTH REFUSAL.** ⛔ **My *"the eighth instance cuts the other way"* is true of the EVIDENCE and FALSE of the REPAIR**: the two hits pull in **opposite directions** and are not one repair. `ph29` 1157 wants `BASE` to recognise **more** spellings; the `N2` exemplar wants it to demand **both** columns — and demanding both does nothing for `ph29` 1157 except make it a hit for a **second, independent** reason. ⛔⛔ **And the rule is a DISJUNCTION whose second branch is not regex-decidable**: *"both columns, **or an explicit statement that only one was measured**"*. A `BASE` that demands both would flag every legitimately single-column unit — of which there are at least four. **Spelling *"only one was measured"* for a regex is `F10` one level up.** ⛔ **My scope figure was also ~4× low and measured the wrong population**: *"5 both / 2 one"* was counted on LINES; **the checker scans UNITS, where it is 22 both / 10 one.** ⛔⛔ **And *"there is NO live violation"* was FALSE** — two, and they are the same sentence: `RECAP_PHP.md` and `.tasks-php/STATISTICS_001.md`, both publishing the `+33 %` with only `c-gcc` named. ✅ **DONE, all four parts:** **(a)** `BASE` LOOSENED to accept `gcc-C`/`clang-C` — a pure false-positive removal, verified **as a set** to retire exactly `ph29` 1157, ratchet 78 → 77; **(b)** `N2`'s exemplar is now a **both-columns** sentence, plus `N2b`/`N2c` (`N2c` asserts the loosened `BASE` still flags a claim naming **no** compiler, so the teeth are checked rather than assumed); **(c)** an **`ⓘ` ONE-COLUMN REPORT that carries no verdict** — it prints the population and leaves the disjunction's second branch to a reader, which is `quota.py`'s discipline and `F128`'s Kind-A/Kind-B rule at once; **(d)** both live sentences now carry `c-clang`'s `−4.36 %`, and the report fell 14 → 12. ⭐⭐ **What (d) revealed is bigger than the labelling defect: the disagreement this programme is about runs BETWEEN THE TWO C COMPILERS as well as between the statistics, and the one-column form hid the larger half** |
| 135 | ⚠ **THE `_INDEP` RATCHET'S LARGEST ENTRY CLASS IS FOUR FALSE POSITIVES AND EVERY ONE OF THEM IS AN ADJECTIVE** | `TASK_PHP_060` §15, routed by the engineer and registered here so it has a home — ⭐ **a question routed to nobody in particular is one nobody answers** (`F123`; and `_059` found a routed ruling buried in a row's `NOTES.md` that the manager then contradicted in print). **The four:** `ph29:23` *(`independently cached`)*, `emalloc_shim.h:640` *(`order-independent`)*, `ph97` `kernel.c:323` / `kernel_hardened.c:356` *(`TWO INDEPENDENT BYTES`)* and now `ph96` `kernel.h:112` *(`a third independent byte`)*. ⭐⭐ **`_INDEP` exists to catch a CORROBORATION BETWEEN TWO ARTEFACTS; all four hits are the word used as an ADJECTIVE DESCRIBING DATA, checkable from the file that says it.** `_056` called the class RECURRING at three; at four it is the single largest entry class in that ratchet. ▶ ~~**THE QUESTION, AND IT IS A REVIEWER~~ ✅ **RULED `_063` §1 — STEADY STATE, ON THE OPPOSITE GROUND'S: is a ratchet whose biggest class is a known, structural false-positive shape in its intended steady state, or is the class evidence the predicate is aimed one concept off?** ⛔⛔ **NO REGEX CHANGE IS PROPOSED AND NONE SHOULD BE MADE ON THIS ITEM ALONE** — §F6a and the ratchet rule both forbid tuning a regex to its hits, and the false-positive direction is the safe one. ⚠ **Nor should the PROSE be reworded to dodge the grep**: the engineer declined that deliberately, and on `ph96` it would also cost a 32-cell re-measure. ⓘ **Cheap and not yet done: ask whether any TRUE positive has ever been filed in this class.** If none has, that is the answer and it cost one grep ✅ **CLOSED AT `_063` §1 — *STEADY STATE*, BUT ON THE OPPOSITE GROUND FROM THE ONE THIS ITEM ARGUED.** ⚠ **UPHELD ONLY AS ARITHMETIC** (the adjective class is the largest). ⛔⛔ **THE REASON IS REFUTED AND INVERTED: the `_INDEP` arm has SEVEN hits, not four, and TWO ARE REAL** — making it the **more productive of the two arms** (2/7 vs 1/6). ⭐⭐⭐ **And on `ph97` an *“adjective false positive”* surfaced a TRUE defect NO ARM OF THE CLASSIFIER CAN SEE, repaired before the 32-cell measure froze it.** ▶ ***A false-positive class that keeps making a human read a real sentence is the arm working, not the arm mis-aimed.*** ✅ **No regex change, as the item required; the answer did cost about one grep, and the item's own count was the thing that was wrong** |
| 136 | ⛔⛔ **`quota.py`'s `CLOSED` LABEL WAS UNREACHABLE FROM THE DAY IT WAS WRITTEN, AND FOUR FAMILIES HAVE BEEN PRINTING THE OPPOSITE OF WHAT THEY MEAN** | Manager, 2026-09-15, found while landing row 12. The line read `if need == 0: st = 'open' if nb >= target else 'CLOSED'` — and `need` is `max(0, target - nb)`, so **`need == 0` IS `nb >= target`**: the guard and the ternary tested the same condition, the ternary was a constant, and **`CLOSED` could never print.** ⭐⭐ **HOW IT WAS CAUGHT, AND IT IS THE ONLY REASON IT WAS**: the manager wrote *“T6 ✅CLOSED”* into the START HERE box and checked it against the tool, which said `open`. ▶ ***A tool and a document disagreeing is the cheapest defect detector this programme has, and it only works if the document is checked against the tool rather than written from memory*** — ⛔ **the THIRD time in this one session that a tool's output and the manager's prose disagreed** (`F134`'s hunk label, `F135`'s expected exit code, this). ✅ **REPAIRED, with the intent stated as INFERRED**: once quota is met, `open` = the family can take more catalogued rows, `CLOSED` = all of them are built. **That is the only reading under which `CLOSED` is reachable.** ⓘ **It changes no label today** — no family is exhausted, so the defect was **vacuous now and would have mislabelled the FIRST exhausted family**. ⭐ §H honoured: `family_status` extracted PURE so the new `N6` drives the real code and not a copy (5 cases, both labels, both singleton shapes), plus `N6b` which tests reachability **from the live catalogue** and **declares itself vacuous** rather than passing silently. ⚠⚠ **THE CLASS, AND IT IS THE POINT: a dead branch and a correct branch are indistinguishable from outside.** Every quota-met family printed `open`, which is what a reader expected for most of them, so the wrong label never showed. ⓘ Same shape as `F135` — a check that could not do its job, passing quietly — and the second instance today |
| 137 | ⭐⭐ **THE RULE IS *“PUBLISH BOTH, LABELLED, ALWAYS”* AND SEVEN OF TWELVE ROWS DO NOT — INCLUDING ONE THAT DECLINED DELIBERATELY AND JUSTIFIED IT. IS THE RULE NARROWER THAN ITS OWN WORDING?** | Manager, 2026-09-16, exposed by the pre-compact audit that corrected the `which statistic` cell. **Measured across all 12 rows**: `W1` appears in `NOTES.md` for `ph45`, `ph52`, `ph53`, `ph55`, `ph56` — **five**. It appears **zero** times for `ph03`, `ph07`, `ph16`, `ph64`, `ph96`, `ph97` and once for `ph29`. ⭐⭐ **`ph96` IS THE INTERESTING ONE BECAUSE IT DECLINED ON PURPOSE AND SHOWED ITS WORKING**: `_060` §8 computed the 16-cell share matrix FIRST, found the two differences the row leans on hardest are **exactly zero** (which `A1` resolves trivially) and the rest between cells at 91–97 % `W`, and concluded *“`A1` is the resolving statistic for this row and every figure here is published in it.”* ▶ **That is either (a) a violation of a rule that says ALWAYS, or (b) evidence the rule's real content is *measure both, publish the one that RESOLVES, and show the matrix that proves which*.** ⚠⚠ **THE MANAGER DOES NOT RULE THIS AND SHOULD NOT** — deciding by fiat would settle a measurement question with a preference. ~~▶ It is a REVIEWER's, and it belongs in the round the backlog already owes.~~ ✅ **RULED `_063` §3.5 — AND THE MANAGER'S ANSWER IS OVERTURNED.** ⛔⛔⛔ **THAT ROUTE FAILED AND IS `F140`: `_061` IS THAT ROUND, I WROTE ITS BRIEF ONE COMMIT LATER, AND THIS ITEM IS NOT IN IT** (`grep` over brief and report: **0** and **0**). **A question routed to a PROCESS has no inbox** — this item's own closing sentence, fired on itself. ✅✅ **AND IT WAS ANSWERED ANYWAY, BY ACCIDENT, AND THE ANSWER IS (a) — THE OPPOSITE OF WHAT THIS ITEM LEANS TOWARD.** `_061` §2.2 refuted `F136`'s headline **precisely because `ph96` published `A1` only**: at `O0/isolated` `A1` reads `+0.0000` while `W1` moves `−2.24 … −19.58 Ir/call` across four cells, and upstream's repair is the **dearer** one. ▶ ⭐⭐⭐ **THE ROW THIS ITEM HELD UP AS THE BEST CASE FOR (b) IS THE COUNTEREXAMPLE TO (b): showing the matrix at ONE optimisation level is not showing the matrix.** ⚠ **What survives of (b), and it is worth a reviewer still**: *publish the one that resolves* may be right **per cell** — but the cell a row resolves in is not the only cell it will be quoted in, and nothing makes a row check the others. ⓘ **If (b) wins, the residue framing changes too**: the thing a row owes is the MATRIX, not the second column — and `ph07`, `ph53`, `ph64` ship neither, which is why they stay the residue under either reading. ⓘ **Registered rather than fixed, because a question routed to nobody is one nobody answers** (`F123`; `_059` found one buried in a row's `NOTES.md` that the manager then contradicted in print) ⛔⛔⛔ **CLOSED AT `_063` §3.5, AND THE MANAGER'S ANSWER (a) IS OVERTURNED: BOTH OPTIONS ARE ON THE WRONG AXIS.** ⭐⭐⭐ **`_061`'s own table shows `W1` at `O3` ALSO reads `+0.0000` — so publishing BOTH STATISTICS would NOT have caught `ph96`. Only the `-O` AXIS catches it.** ▶ ***The matrix is 4-D (statistic × input × opt × mode), and “publish both, labelled” names ONE of the four.*** ⛔ **So the rule as worded is neither (a) nor (b): it is under-specified, and `ph96` obeyed the specified part.** ▶ **The live successor question — *should a row-level TWO-LEVEL matrix be REQUIRED?* — is where `F146` and item 146 land too** |
| 138 | ⛔⛔ **`task_cost.py`'s `060` ENTRY CARRIED TWO GENERATIONS OF ITS OWN COMMENT — THE LANDED TEXT, AND THE PENDING-ERA DRAFT IN THE FUTURE TENSE BELOW IT** | Manager, 2026-09-16, found while registering `_061` in the same ledger. The stale half read *“▶ WHEN THE ROW GATES, do BOTH in one edit”* and *“It WILL then carry two extras”* — **written before `ph96` gated, and left in place under the landed text when it did.** ⭐⭐ **IT SAT BELOW THE LIVE VERSION, WHICH IS THE WORST PLACE FOR IT**: a reader scrolling to the nearest copy gets the oldest, which is the reason the *“backlog trend”* prefix in the RULE-9 block was struck for the same shape. ▶ **Item 73 — a correction APPENDED instead of APPLIED — made by the manager IN THE EDIT THAT LANDED THE ROW**, i.e. `F131`'s class inside the cost ledger. ✅ **REPAIRED BY REPLACEMENT, not striking**: the surviving text keeps the one clause the stale draft said better (`_058`'s rule *a control a row should have shipped with is that row's debt*, named rather than alluded to) and drops the rest. ⓘ **The draft's closing question is ANSWERED, which is why it could not stay** — *“ph97 came in at 1.00; that is the comparison to watch”* — both `T6` rows cost 1.00. ⚠⚠ **NOT A NUMBERS DEFECT: every figure `task_cost.py` prints was and is correct** (`--selftest` PASS across the edit, `N14` gated rows = `ROWS` = 12). **The defect is entirely in the prose a future reader would have consumed as the rationale**, which is why no re-run caught it and why it needed an item |
| 139 | ✅✅ **DONE — AND `F133`(i) TURNS OUT TO BE A WELL-FORMED QUESTION FOR ONLY ONE KIND OF REPAIR** | `TASK_PHP_061` §3.4, the reviewer's own priority 4, run **as a grep, not as ten censuses** (binding) and committed as `.tasks-php/probes/item139_sibling_census.py` (**10 arms, 9 must-fire**). ⭐⭐⭐ **The result is not a tally.** Sorting all 13 rows by WHAT KIND OF CHANGE the R1h is: **GUARD** (adds/copies a test — `F133`(i) is answerable) on **8 of 13**; ⛔⛔⛔ **and its positive evidence is `4 CLEAR + 1 BORDERLINE`, NOT the `7 of 8` this row published until 2026-09-17** — CHOSE `ph03` `ph07` `ph56` `ph96` · BORDERLINE `ph55` · SAME-CONSTRUCT-BUT-DIDN'T `ph97` · NOT-EVIDENCE-ABOUT-CHOICE `ph64` `ph66`; **API-SWAP** (ph29, ph53) answerable only at tree scope; **STRUCT** (ph45 — the repair ADDS the field it then uses); **DELETION** (ph52 — the whole patch is one removed line); **BUILD** (ph16 — 10 files + `configure.in`). ▶ **For five rows the question has NO ANSWER rather than a NO.** ⭐⭐ **Every positive is a SIBLING**: `ph64` is the purest — the `calling` flag the 2007 fix reads was **declared, set and cleared by the same file since 5.0.0** (`:157`, `:2108-2109`, `:2135`) and the delete's comparator never consulted it; `ph55`'s repair text is **already in the file verbatim**; `ph03` and `ph07` are sibling-function cases 60 and 163 lines apart. ⛔ **The one failure, `ph97`, fails informatively: 0 of the 5 optional-string parses in `mbstring.c` test the pointer — the construct's NORM is the defect.** ⛔⛔ **AND SCOPE DOES REAL WORK**: on `ph29` the answer is **NO in-file** (`safe_emalloc` 0×) and **YES tree-wide** (250 sites / 78 `.c` files — it was the established idiom and the defective file was the holdout). ***“The same construct” is not defined and the answer flips with the definition.*** ⛔⛔⛔ **AND `_062`'s ENGINEER WEAKENED THE HEADLINE FROM INSIDE THE ROW**: a `held` count may be **counting sites that had no choice**. `ph66`'s nine siblings are *structurally unable* to face `:464`'s choice — `_zend_hash_add_or_update` takes `arKey`/`nKeyLength` and nothing else — so the split is **a type-level fact about one signature**, and the nine are **NOT evidence of intent**. ▶ **`ph66` is a WEAK instance of `F133`(i), not the strong one the 9-of-10 suggests**, and **no column anywhere in this programme distinguishes *a sibling that chose the correct spelling* from *one that could not have spelled it otherwise* — which is what `F133`(i) actually needs.** ▶ ~~**That is the live residue and it goes to `_063`~~ ⚠ **RULED `_063` §7.1 beside `F133`** ⚠ **RULED AT `_063` §7.1: THE WEAKENING IS UPHELD-NARROWED — the brief's two-row test returns **1–1** (`ph03` COULD have been written the defective way; `ph64` could not).** ⛔ **But its REMEDY is the wrong column: *“did the site FACE the choice?”* is UNDECIDABLE, while **`same_construct?`** is CHECKABLE.** ▶ **`held` conflates CHOSEN and DISCOVERED — a distinction `F133`'s own re-worded rule already draws and its instrument does not implement.** ⛔⛔ **SO THE PUBLISHED *“7 of 8”* IS OVER-STATED TODAY.** ✅✅ **DONE 2026-09-17 — the reviewer's #3 resume priority, discharged.** `held` is SPLIT into **`same_construct?`** and **`chose_correctly?`**, `held` = BOTH, and the two prescribed §H negatives landed as **`N7`** (`ph66` reports `same_construct=NO` and therefore `held=--`, ⛔ **not** `✅ YES` — the row that PRODUCED the weakening, and its single ✅ was 1 of the old 7) and **`N8`** (`ph03` reports `YES`/`YES`, the positive control, so `N7` is not passing because the column says NO to everything). ⭐ **Two arms MORE than prescribed, both earning their place**: **`N9`** fails if the split ever stops MOVING the number — ⛔ *a new column that rubber-stamps is a relabelling, not a repair* — and **`N10`** asserts `held` is still the CONJUNCTION it always claimed to be rather than a third independent column. ⛔ **The column `_062`'s engineer proposed — *did this site FACE the choice?* — was REFUSED and the refusal is written into the file**: it asks about a counterfactual authorial state and cannot be filled from a repository. ⚠⚠ **The two new columns are HAND-ADJUDICATED and the adjudication is `_063`'s REVIEWER'S** — carried WITH its attribution, because the reviewer wrote *“it is a reading, not a measured column, and I say so”* and laundering that into a measured column would be the defect the whole row is about. ⭐⭐ **THIS DOES NOT WEAKEN `F133` — it makes its headline survivable**: *the repair was already in the file* is true on more rows than *a sibling chose it*, and only the second supports the rule that was landed. |
| 140 | ⚠⚠ **`st_expect: None` CONFLATES *HAS NO SELF-TEST* WITH *HAS ONE, UNFILED* — A THIRD SILENCING MECHANISM, WEAKER THAN `F135`'s BUT IN THE SAME FAMILY** | `TASK_PHP_061` §4.2, found live. **`width.py` and `php_null.py` — the TWO FILES `.memory-php/04-process.md` LAW 16 NAMES AS THE MODEL — shipped passing `--selftest`s the registry never ran.** ✅ **BOTH DECLARED `st_expect=0` 2026-09-16** after measuring them (`rc=0 SELFTEST PASS`, **33.3 s** and **0.08 s**); ⚠ **the sweep roughly DOUBLED, 35 s → 66 s, and that cost is accepted deliberately** — it is a task-boundary check, and a passing self-test nobody runs is `F135`'s class exactly: it will go red and nothing will say so. ⛔ **THE DESIGN RESIDUE IS NOT FIXED**: the field is two-valued over three states, so the registry still cannot tell *has none* from *has one, unfiled* at a glance, and nothing would catch the next instance. ▶ **A three-valued field separates them at ZERO runtime cost** — the reviewer's suggestion, not costed by me. ⓘ **`F135` found the first mechanism by sweep; this one was found by a reviewer asking the harder version of `F135`'s own question**, which is an argument for asking it of every `expect`-like column |
| 141 | ⭐⭐⭐ **§A3a OBLIGATION 5'S GATE IS *“the pre-image run FAULTED”* AND CRITERION 2 IS *“exhibits the target ERROR”* — REPAIR IT WITH AN ARM, NOT WITH WORDING** | `F141`, manager 2026-09-16, found by measuring row 13's candidate. **The gate excuses the obligation the section's own rationale box calls the most valuable in it**, on rows whose target error is a wrong ANSWER rather than a signal — which `_057` §3.2's rates put at roughly **61.3 %** of the temporal axis, where **15 of the 25 owed rows** live. ✅ **The generator half is already repaired**: `rebuild_hardened_php.sh` now takes `--patch/--trigger/--label/--workdir`, prints rc **and** stdout for both images, and adjudicates nothing. ✅✅ **THE PROTOCOL HALF LANDED 2026-09-16** — `_062`'s engineer routed the choice to the manager **by name** (§8.1, options (a)/(b)/(c)) and (b) was taken: obligation 5 now reads *"REQUIRED WHENEVER THE ROW CAN NAME AN OBSERVABLE THE REPAIR IS EXPECTED TO MOVE, WHICH IS EVERY ROW — because a row that cannot name one has no R1h claim to make"*, and it requires recording **exit status AND output** on both images. ⚠ **`F141` is still UNREVIEWED and the wording is overturnable**; what the review settles is the SCOPE, not whether the gate named the wrong predicate. ⛔ **The ARM is still owed and is still the item.** `F139` measured `PROTOCOL_PHP.md` losing a correction race to its own author by 9h25m, and `_061` §5.0 ruled that **location is not the variable — the durable home for a trap is an arm that prints**. ▶ **So the deliverable is an arm that, for each built row, reads whether §A3a obligation 5 was discharged and prints the rows where it was skipped** — wording alone would reproduce `F139` knowingly. ⚠ **Blocked on `F141`'s review**: if the reviewer's scope attack lands (the 38.7 % is over CATALOGUED ids while rows are SELECTED for buildability), this shrinks to a one-line wording fix and the arm is not worth building |
| 142 | ⭐⭐ **`R3 → R4` IS DEARER ON `ph66` AND THE MECHANISM IS NEW: WHAT `unsafe` REMOVED WAS AN *ANALYSIS*, NOT A BRANCH** | `TASK_PHP_062` §6.2. Same-language `A1`, `O3/isolated`: **`R3 → R4` is `+1.37 %` / `+0.86 %`** — removing every bounds check from the bucket arena **cost**, it did not save. ⓘ **The RESULT is not new** — *every in-contract `R4` variant is dearer* is already published (`r4_endpoint_degenerate`, `+0.50 … +33.92 %`). ⭐⭐ **The MECHANISM is**: `R3` binds `let n = &self.a[p as usize];` once, so LLVM hoists the single check out of the inner comparison and keeps `n` in registers; `R4`'s `nref` returns a reference through an opaque `get_unchecked` **the same alias analysis cannot see through**. Static counts agree — **`R3` 750 instructions against `R4` 791**. ▶ ***The bound was already free; what `unsafe` removed was an analysis.*** ⚠ **Registered rather than filed as a finding** because the conclusion is a confirmation; **the mechanism is what would enter `.memory-php/02-ladder.md`, and it needs a second row before it is a claim about the ladder rather than about `ph66`** |
| 143 | ⛔⛔ **THE LADDER'S *“DOES THE DEFECT SURVIVE?”* COLUMN DEPENDS ON A PORTING CHOICE THE PROTOCOL DOES NOT CONSTRAIN** | `F143`'s own reviewer-attack, and `_060` `P2` said the same thing a row earlier without either of us noticing it was a rule gap. **On `ph96`**: *“an `R2` mirroring the C's control flow with `.unwrap()` **panics** (a detected fault); one that handles `None` has **deleted the bug**. Both are legitimate and they are different rows of the ladder's column.”* **On `ph66`**: an `R2` built on a real `HashMap` deletes the bug; one that ports the bucket logic reproduces it **byte-identically**, which is what `F143` reports. ▶ ⭐⭐⭐ **So the column's value is set by the porting choice, and nothing in `PROTOCOL_PHP.md` says which to make.** ⛔ **Until it does, *“the safety stack is blind”* and *“the safety stack caught it”* are BOTH available on the same row, and the corpus's answers are not comparable across rows.** ⚠⚠ **THE MANAGER MUST NOT RULE THIS** — it decides what a published column means, and `_061` §2 is the precedent for refusing that move. ▶ **`_063`, beside `F143`** |
| 144 | ⛔⛔ **A SECOND QUESTION WAS ROUTED TO ME BY NAME IN `_062` §8.2 AND I ANSWERED ONLY §8.1 — `F140`'s CLASS, ONE SECTION LOWER** | Manager, 2026-09-16, found by the pre-compact audit. The engineer wrote: *“UNTESTED: whether flipping `task_cost.py`'s `CLASS["062"]` to `1.00` is the classification YOU want … **‘this row cost one task’ is a judgement, not an arithmetic fact, and I am the interested party.** The published projection moved `~63..~79/~64` to `~57..~72/~58` on the strength of it.”* ⭐ **It even cited the rule it was invoking** — *a cost ledger is not a build artefact; the party whose work it prices must not price it.* ⛔ **I read §8.1, answered it in `PROTOCOL_PHP.md`, and never read §8.2's first bullet** — so a question about a PUBLISHED figure sat unanswered in a report I had already acted on. ✅✅ **ANSWERED NOW: KEEP `1.00`.** Every other entry in the table measures the BUILD task(s) and row 13 took one, so changing the weight would make the series incomparable to fix a level. ⛔⛔ **BUT THE ENGINEER'S UNEASE IS CORRECT AND POINTS AT A REAL NON-UNIFORMITY I AM NOT RULING ON**: `ph53`'s R1h hunt and build brief WERE a task file (`_040`, now charged `0.5/0.5`), while row 13's equivalent work — `ROW13_001.md`, two probes, the `rebuild_hardened_php.sh` generalisation — was done by the MANAGER inside `_061`'s session and is charged **nowhere**. ▶ ***So scoping is charged for some rows and invisible for others, and which depends only on whether a task file happened to be written for it.*** ⚠⚠ **That is a defect in the LEDGER, not in this entry**, and it biases the series in an unknown direction. ✅ **RULED `_063` §5.2**** ✅ **RULED AT `_063` §5.2: KEEP `1.00` STANDS, and the engineer's unease is correct AND BIGGER THAN ROW 13.** ⛔⛔ **BUT *“it biases the series in an UNKNOWN direction”* IS REFUTED — the direction is STRICTLY DOWNWARD, by the ledger's own construction**: invisible scoping work can only be missing from the numerator, never added to it, so **every published marginal figure is a LOWER BOUND.** ⭐ **And the census costs ONE COMMAND, which the reviewer ran: THREE invisible row-attributable documents naming FOUR built rows.** ⚠ **The magnitude (~1 task-equivalent per document) is an ASSUMPTION and is labelled as one; the count and the direction are measured.** ▶ **Resume item 7: a NAMED SENSITIVITY ROW in `task_cost.py` plus its `N`-arm, ~20 min — so the bound is printed rather than remembered** |
| 145 | ⚠⚠ **A COMMITTED DOCUMENT MAY CITE `.temp/`, AND THE RULE THAT FORBIDS IT COVERS ONLY `spec.md`/`NOTES.md` — SO THE QUESTION IS NOT *DOES IT CITE SCRATCH* BUT *DOES A GENERATOR LIVE THERE WITH NO OTHER HOME*** | Manager, 2026-09-16, pre-compact audit, starting from `_062` §8.3 and **measured before being believed**. §F6 forbids `spec.md`/`NOTES.md` from citing `.temp/`, and `citecheck.py` enforces exactly that (3 inherited PAT-era hits, `ph66` adds none). ⛔ **But REPORTS cite `.temp/` universally** — counted across all landed PHP reports, every one does, and **`_062` at 3 is among the LOWEST**. ▶ **So this is not a `ph66` defect and not a new drift**; a report is a dated narrative and naming the directory you worked in is accurate history. ⛔⛔⛔ **AND MY FIRST DRAFT OF THIS ITEM PROPOSED AN ARM THAT MOSTLY ALREADY EXISTS — CHECKED BEFORE FILING, WHICH IS THE ONLY REASON IT IS NOT A SECOND HOME** (`F131`). `citecheck.py` **already scans `.tasks-php/*.md`**, reports itself **rc=1 at `HEAD`** on the long-standing `spec.md` debt (items 55/61, each repair a re-gate), and **already carries a `§H AT RISK` arm** for *a COMMITTED VALIDATOR citing its NEGATIVES in gitignored `.temp/`* — 8 live hits across `ph16`/`ph29`. ▶ **So the report-citation half is DELIBERATELY benign and the validator half is ALREADY ARMED.** ⭐⭐ **WHAT IS GENUINELY UNCOVERED IS NARROWER THAN I WROTE**: a `.temp/` path holding a **GENERATOR** — a `.py`/`.sh` that rebuilds evidence — **with no committed twin and no validator role**, so neither arm sees it. For `_062` that is `.temp/php66/clausetest.py` (the clause-mutation pre-check, §7.6, and it looks **REUSABLE across R5 rows**) and `REGEN.sh`. ⛔⛔ **AND THE TENSION IS IN THE RULES THEMSELVES, NOT IN ANYONE'S CONDUCT**: `CLAUDE.md` rule 1 says the `.py` probe and the logs **ARE the evidence and stay** — in `.temp/`, which is gitignored — while `F51`/`F99` say a committed document may not point at deletable scratch. **Both are followed here and they disagree.** ⚠ **NOT BUILT and the two files NOT promoted by fiat** — it decides what `CLAUDE.md` rule 1 means, which is above the manager, and the right shape may be a WIDENING of `citecheck.py`'s existing arm rather than a new one. ⛔⛔ **RULED `_063` §7.2 — AND THE SCOPE WAS WRONG BY ~100×**** ⛔⛔⛔ **RULED AT `_063` §7.2, AND BOTH HALVES WENT AGAINST ME.** **(1) THE TENSION IS A FALSE DICHOTOMY**: `CLAUDE.md` rule 1 and `F51`/`F99` govern **two different document lifetimes**, and **the tree already implements the resolution three times over.** **(2) ⛔⛔ THE SCOPE IS REFUTED BY ~100×** — I scoped it to ONE file; measured, there are **114 `.temp/` citations across the four permanent document families**, **10 of them in `.memory-php/`**, of which ⛔⛔⛔ **THREE ARE LIVE DEPENDENCIES IN `02-ladder.md` ON THE MANAGER'S OWN SCRATCH** (`:447`, `:451`, `:612` → `.temp/mgr172/NOTES.md`, `.temp/mgr170/null_control.py`). ▶ ***The AUTHORITATIVE LAYER depends on auto-`rm`-able scratch, and this directory family has already lost state once*** (`RECAP_PHP.md:115`). ⛔ **OPEN, and the reviewer's #2 resume priority: promote the two files, or re-write the three citations as HISTORY** |
| ~~146~~ | ⛔⛔⛔ **ANSWERED 2026-09-17, AND THE ANSWER IS THAT ONE OF THE FOUR SIGNS IS NOT THERE.** `--opt` landed (reviewer resume priority 5; `_063` §3.4 ruled the item names the wrong instrument — *measuring* was alive, **SWEEPING** was dead). The first `O0` sweep this programme has run reproduces all four published numbers **to the digit**, and then certifies at 32 pads: `small`/gcc ✅ RESOLVABLE + SIGN-STABLE · `small`/clang and `large`/clang ⛔ NOT RESOLVABLE but SIGN-STABLE · ⛔⛔⛔ **`large`/gcc NOT RESOLVABLE AND **SIGN-UNSTABLE** — step `8.89` against an effect of `6.12`, so `|d|/step = 0.69` and at some pads `R1h` is CHEAPER.** ▶ **So this item's own premise — *the `O0` sign is the opposite of the `O3` sign* — holds on THREE cells and is NOT ESTABLISHED on the fourth**, and the row was right to publish nothing. ⭐⭐ `F149`(b): a **4-pad** screen called that same cell `RESOLVABLE`/`SIGN-STABLE` — **the opposite verdict on both axes.** ▶ **`F149`; the residue is item 151** (correct `ph66`'s summary sentence, a RE-GATE; and sweep the other twelve rows, which nobody has ever done at `O0`). **The original framing, kept:** | `_062` §8.2, the engineer's own flagged uncertainty. At `O0` the R1h **COSTS** (`+4.00`/`+6.12` gcc, `+5.00`/`+9.69` clang Ir/call); at `O3` it **SAVES** (`−3.20`/`−19.83` gcc, `−2.03`/`−12.00` clang), **sign-stable over a 32-residue pad sweep**. ⛔ `php50_align_sweep.py` hard-codes `OPT = "O3"`, and `.memory-php/03-numbers.md` forbids quoting an `O0` figure as a performance figure — **so the engineer treated the `O0` numbers as lowering readings and published none.** ⭐ **That is the conservative reading and the engineer says it may be the wrong one**: *“a row that could publish both would be saying something the corpus currently cannot.”* ▶ **The question is whether *‘never quote an `O0` figure as a performance result’* has quietly become *‘never MEASURE at `O0`’*** — `F136`'s headline was refuted AT `O0` and `F144` was caught by looking at two levels, so the corpus's two most recent statistic findings both came from the level nothing sweeps. ⚠ **This is NOT a proposal to publish `O0` magnitudes.** It is a question about what a sweep is for. ⛔ **RULED `_063` §3.4 — THE ITEM NAMES THE WRONG INSTRUMENT**** ⛔ **RULED AT `_063` §3.4: THE ANSWER IS *NO* — MEASURING AT `O0` IS ALIVE AND WELL, AND THE ITEM NAMES THE WRONG INSTRUMENT.** ⭐ **What is dead is SWEEPING**: `php50_align_sweep.py:86` hard-codes `OPT, MODE = "O3", "isolated"`, so **no `O0` SIGN can clear §B5 and therefore none can be published** — which is exactly why `ph66`'s engineer published neither sign and was right not to. ▶ **So the question *“has ‘never quote’ become ‘never measure’?”* is answered NO, and replaced by a sharper one: *nothing can establish an `O0` sign because nothing sweeps there.*** ⚠ **OPEN — reviewer's #5 resume priority: `php50_align_sweep.py --opt`, ~30 min, with its two §H negatives.** ⛔ **Still NOT a proposal to publish `O0` magnitudes** |
| 147 | ⚠ **`ph66`'s `inside_share` MATRIX HAS AN UNEXPLAINED `n/a` IN EVERY `O0/large` CELL, IN A MATRIX THE ROW CALLED COMPLETE** | `_062` §8.2, raised by the engineer against itself: *“a `n/a` I have not explained is a hole in a matrix I called complete.”* `controls/inside_share.py`'s `F74` column reads `n/a` on every `O0/large` cell; `marginal_ir_per_call` has the key, so the likely cause is a `large.bin` `A1` the record does not carry at `O0` — ~~**but that was not confirmed.** ⭐ **Cheap**: it is one read of the record's keys, not a re-measure.~~ ✅✅ **CONFIRMED 2026-09-16 BY RUNNING IT, AND THE SCOPE IS THE ANSWER — `F146`.** The engineer's conjecture is **exactly right**, and the cause is **not `ph66`'s**: `kernel_exclusive_ir` is absent from the `O0/large.bin` cell of **every isolated cell of every row in BOTH programmes** — `0 of 263` PAT, `0 of 111` php — because `harness/measure.py`'s `CG_PLAN` adds `large` **only at `O3`**, in one deliberate line whose comment says *“where the perf claims live.”* ⛔ **So the `n/a` is INHERITED, not incurred, and `ph66`'s control reports it faithfully.** ⭐⭐ **What the run ALSO showed and the item did not anticipate**: the printed matrix mixes **two provenances in adjacent columns** — `A1`/`W`/`share_W` from a **live** callgrind over the build root, `share_F74` from the **committed** record — so the blank falls on exactly the 8 cells `CG_PLAN` never wrote, and a reader cannot tell which column was measured today. ⚠ **It matters more than it looks because of item 146**: if the `O0` half of the matrix is structurally incomplete, then *‘show the matrix at more than one optimisation level’* — the `_061` rule that caught `F144` — **is asking for something the instrument cannot fully supply**, and nobody has said so. ⛔ **THAT HALF IS STILL OPEN AND IS NOW `F146`'s LOAD-BEARING CLAUSE**: `_061` obeyed the rule by running its OWN callgrind, so *“cannot supply”* may be only *“does not supply for free.”* ✅ **RULED `_063` §3.3**** ✅✅ **RULED AT `_063` §3.3: THE ENGINEER'S CONJECTURE IS CONFIRMED, `F146` §3.2 IS ITS SCOPE, AND THE PROVENANCE QUESTION IS ANSWERED *YES — IT IS WORTH A RULE*.** ⭐ **But the rule is PER-COLUMN, not per-file**: a matrix may legitimately mix a live measurement and a committed one, and what it may not do is fail to say **which column is which**. ▶ **`F108` one level down — five things every percentage owes, and *which build* is one of them.** ⓘ **One of only TWO objects in `_063`'s seventeen that carry no refutation, and both were engineer-raised against themselves.** ⚠ **Open at LOW: the per-column label, plus `controls/inside_share.py`'s dead loop at `:113-116`** |
| ~~148~~ | ✅✅ **ADJUDICATED 2026-09-17 — `F150`. THE RULING IS IN THE TOOL, NOT IN THIS ROW**: `scratchdeps.py`'s `ADJUDICATION` table, keyed on `(finding, cited file)`, each row carrying its reason in the citing sentence's own terms. **`RESTS` 17 citations / 14 files / 13 findings · `HISTORY` 6 · `NOTDEP` 4.** ⚠⚠ **THIS ROW PREDICTED A MINORITY AND IT IS A MAJORITY (63 %)** — `F21`/`F37`'s duty runs both ways and the channel is live. ⛔ **And the severity is worse than the count: 11 of the 13 findings have never been reviewed**, so for them the gitignored probe is the only evidence anywhere; only `F89` and `F95` have a second method, and `F89`'s reviewer reproduced the CONTRAST while its two published figures still rest on the probe alone. ⭐⭐ **THE MECHANISM IS THE RULE BEING OBEYED**: `F102` cites *"generator kept, binaries deleted"* — `CLAUDE.md` Don't #1 done exactly right — and **the rule never says WHERE**, so a careful author still lands a law-11 defect. ⭐ **Three of the 27 were FALSE POSITIVES OF MY OWN CENSUS**, ruled `NOTDEP` rather than dropped: at `F59`/`F69` `streamsfuncs.c` is a PHP 5.0.0 source file in a table, not the scratch copy. ⭐ **The arm is COVERAGE, not cardinality** (`N19`–`N25`) — `17 RESTS` would go red the day the work is done — and **it caught its own author on the first try**, going red on the four fresh citations `F150`/`F151` introduced. ▶ **The promotions are item 153; the `verus.rs` half is item 152.** ⭐⭐ **AND THE ADJUDICATION FOUND SOMETHING BIGGER THAN THE VERDICTS** — `F151`, `citecheck.py` scanning 3 of 15 hashed role-classes. **The original row:** | ⛔⛔ **ADJUDICATE THE SCRATCH-CITED FILES BEHIND PUBLISHED FINDINGS — BY UNIT TEXT, NEVER BY COUNT** | `F147`. ▶ **Run it, do not quote this row**: `python3 .tasks-php/probes/scratchdeps.py` prints the SET — at the commit that filed `F147`, **54 LIVE citations over 29 distinct files**, and its `law 11` block: **34 citations inside a `### F<N>` section, over 22 published findings, 23 distinct files** (F44, F50–F53, F59, F69, F70, F72–F74, F82–F86, F89, F90, F95, F99, F100, F102). ✅ **6 files discharged by the `F82`–`F86` promotion** — `probes/{identity_null,inclusive_ir,bc_sweep,flip_exact,null_control}.py` + `sweep_cg.sh`, with `NULLCTL_001.md` as their evidence record. ⚠⚠⚠ **THIS IS A CANDIDATE SET, NOT A DEFECT COUNT** (`F132`), and the tool says so in its own docstring: it cannot tell a probe I wrote from upstream source I extracted, and **at least one member is the rule being FOLLOWED** — `.temp/php27/streamsfuncs.c` is PHP 5.0.0 source, re-derivable from `patterns-php/php-5.0.0.manifest`, where **committing it would be the error**. ▶ **The method is item 125's, which worked**: the extractor exists, so each member needs ONE read against its citing sentence, and the verdicts go into a must-fire arm rather than into prose. **Cost: ~25 min** — ⛔ **and an hour-shaped estimate is exactly why item 125 sat for six rounds.** ⓘ **Three classes are already someone else's home and must NOT be re-adjudicated here**: the §H subclass (`negatives_spellings.py`, 13 citations) is `citecheck.py`'s standing report and open item 97; the `controls/*` citations cost a per-row RE-GATE and batch with that row's next task; and the `.temp/` citations in the **OPEN-ITEMS TABLE** are provenance for work in flight and are **correct as written** — that is the half of `citecheck.py`'s exclusion that `F147`(d) upholds. ⭐ **Expect a MINORITY, and say so plainly if the channel is dead** (`F21`/`F37`) | ✅ **EVENT, 2026-09-17: ALL 29 TARGETS STILL EXIST — 0 GONE. Nothing has been lost; the exposure is real and the loss is hypothetical.** ⚠⚠ **A READING WITH A DATE, NOT A PROPERTY** — `citecheck.py` already reports **4** `controls/*` citations whose targets **are** gone, and `CLAUDE.md` constraint 6 *mandates* deleting `.temp/` blobs once gates are green. ⛔ **Do NOT "fix" this by committing artefacts**: a callgrind profile, a `.bin` or a build tree under `.temp/` is `CLAUDE.md` Don't #1 being **obeyed**. The defect is a SCRIPT or an EVIDENCE DOCUMENT in scratch — **never a re-derivable blob, and never its generator's output** |
| ~~149~~ | ✅✅ **DECIDED AND LANDED 2026-09-17 — AN UNRUNNABLE *CROSS-SESSION* CHECK REPORTS AND RETURNS 0, AND IT SAYS `NOT A PASS` IN CAPITALS WHILE DOING IT.** `reuse_check` returned `False` with `.temp/mgr173/cg/` absent, so `width.py` — filed `st_expect=0` — went **red for following `CLAUDE.md` Don't #1**. ✅ **Repaired where the reasoning lives**, with the §H negative **`X3d`**, which **plants its own input** (`reuse_check({})` reaches the same branch without deleting a directory the rest of the sweep reads) and is **demonstrated must-firing**: against the pre-repair behaviour `X3d(a)` FAILS and against the repair it PASSES. ⭐⭐ **THE TWO HALVES SEPARATE CLEANLY AND THAT IS THE RESULT**: `X3d(b)` — *does the message say `NOT RUN` / `NOT A PASS`?* — **passes in BOTH worlds**, because the message was always loud and only the return value was wrong. ▶ **So the defect was never dishonesty; returning 0 is only right BECAUSE the message already refused to claim a pass, and a silent 0 would be the worse of the two defects.** ⚠⚠ **AND THE HEADER WAS BELIEVED TWICE** (`F147`(e), the record of the remedy being wrong about the remedy): I told `PROMOTE_001`'s engineer to copy this file — ⭐ **it refused, checked behaviour against claim, and made its own guards return 0** — and `probes/inclusive_ir.py:269` cites *"the rule `.tasks-php/width.py`'s X3 already follows"* as precedent for a rule X3 **did not follow**. ⓘ **That citation is now true**, repaired by moving the code to the claim rather than the claim to the code. ⚠ **No new finding**: `F147`(e)/(g) already own this fact (`F131`). **The original row:** | ⚠⚠ **DECIDE WHAT AN *UNRUNNABLE* CHECK RETURNS — AND `width.py` IS RED IN A STATE `CLAUDE.md` INVITES** | `F147`(g), found by `PROMOTE_001`'s engineer when I told it to copy `width.py` as the precedent. **`.tasks-php/width.py`'s committed header says its cross-session check *"reports … **and does not fail**. ✅ So the selftest degrades honestly rather than lying."* ⛔ It fails.** With `.temp/mgr173/cg` absent it prints `FAIL X3`, ends `SELFTEST FAIL ['X3']`, **rc=1** — `reuse_check` returns `("X3", False, …)` at `width.py:1323` and `selftest`'s `check()` appends every falsy `cond` to `fails` (`:893-896`). ✅ **Verified statically by the manager, independently of the engineer's run.** ⚠ **Live, not cosmetic**: `width.py` is filed `st_expect=0`, and the state that reddens it — an emptied `.temp/mgr173/cg` — is the one `CLAUDE.md` Don't #1 *tells you to create*. **The routine sweep goes red for following the rules and no `why` says so.** ▶ **MY DECISION, ALREADY WRITTEN: an unrunnable CROSS-SESSION check REPORTS AND RETURNS 0.** The tree argues this one directory over — `probes/ph66_djbx33a_collide.py`'s entry says *"a checker that reddens when a sibling repo is cleaned is reporting on that repo"* — and `X3` is the same shape one level in. ⭐ **The engineer REFUSED my instruction and made its two new guards return 0 while saying in capitals that nothing was checked. That was the right call and it is why the promoted probes do not inherit the defect** | ⛔ **NOT a one-liner.** `width.py` carries `F92`, and `PROTOCOL_PHP.md` §H says a validator change lands **with its must-fire negatives or it does not land** — so this owes an arm that plants an absent cache and asserts *reports-and-returns-0*. ⚠ **And fix the HEADER in the same edit**: today it describes a behaviour the file does not have, which is `F147`(e)'s defect on the same file — **the record of the remedy being wrong about the remedy.** ⓘ `probes/inclusive_ir.py` and `probes/bc_sweep.py` already carry the shape to copy |
| 150 | ⚠ **I DISPATCHED A TASK'S WORTH OF WORK WITHOUT A TASK NUMBER, AND THE COST LEDGER CANNOT SEE IT — `n = 1`, STATED AS `n = 1`** | Manager, 2026-09-17. `task_cost.py` is keyed on `TASK_PHP_NNN`, so `PROMOTE_001` — a dispatched subagent with a brief, a 406-line engineer report, ~20 minutes and 110 tool calls — **is priced at ZERO**, and every figure the ledger publishes (`marginal 2.38`, `PUBLISH ~57..~72`) is computed without it. ⛔ **This is `F142`'s defect in a NEW SPELLING**: there, real row work sat misclassified `PENDING` *inside* the namespace and understated the projection; here it sits *outside* the namespace entirely, where no classification can be wrong because none exists. ✅ **MEASURED, and the population is exactly one**: `PROMOTE_001_REPORT.md` is the ONLY `*_REPORT.md` in `.tasks-php/` without a task number. ⚠⚠ **The other 12 unnumbered documents are NOT evidence for this** — `ADJUDICATION_00N`, `QUOTA_001`, `ROW13/14_001`, `STATISTICS_001`, `UPSTREAM_00N`, `FIXSURVEY_001`, `NULLCTL_001` are MANAGER write-ups produced inside numbered sessions, so their effort is plausibly already charged. **I have not verified that, and I am not claiming it** — ⛔ **`n = 1` is not a rate** (item 123). | ▶ **The question for a reviewer, and I should not settle it myself because it prices my own work** (`_057`'s engineer refused exactly this, and was right): should a dispatched chore be NUMBERED, or should the ledger learn a second namespace? ⚠ **Numbering is the cheaper answer and the one that needs no tool change** — but it makes every promotion a task file, which is the ceremony `_063` §7.2 ruled a false dichotomy about. ⓘ **Do NOT retro-number `PROMOTE_001`**: the ledger's own figures are quoted with commits, and moving a denominator under a published range is `F126`'s defect |
| 151 | ⛔⛔ **CORRECT `ph66`'s `O0` SUMMARY (a RE-GATE), AND SWEEP THE OTHER TWELVE ROWS AT `O0` — NOBODY HAS LOOKED BECAUSE UNTIL TODAY NOBODY COULD** | `F149`. **(a)** `patterns-php/ph66-hashdel-uncompared/NOTES.md:345-346` summarises four `O0` family-B figures as *“the extra conjunct costs at `O0`”*; the certified 32-pad sweep says that holds on **three** cells and is **NOT ESTABLISHED** on `large`/gcc, where the alignment step (`8.89`) EXCEEDS the effect (`6.12`) and the pair reads **SIGN-UNSTABLE**. ⛔ `NOTES.md` is in the gate record's `source_sha256` (`19b8d3fa72be0dba…`), so the fix **costs a `ph66` RE-GATE** — ▶ **batch it with that row's next task**, the practice items 36 and 39(c) already set. ⓘ **Not an accusation of over-claiming**: the row labels its `O0` rows *“LOWERING READINGS AND NOT PERFORMANCE CLAIMS”* in capitals and was correct under the rule as it stood; the defect is in the SUMMARY and the row was structurally unable to detect it. **(b)** ⭐⭐ **THE BIGGER HALF: twelve other built rows have never been swept at `O0` at all**, and the one row that has just produced a sign-unstable cell on its first look. **Cost: ~20 min per row per input at 32 pads** (measured: `ph66` both inputs ≈ 25 min), so this is a sweep task, not a by-hand one. ⚠⚠ **DO NOT let this become a licence to publish `O0` MAGNITUDES** — `.memory-php/03-numbers.md` stands and `--opt` buys a SIGN only, labelled a lowering reading, and only if swept | ⚠ **AND THE METHOD WARNING THAT COMES WITH IT, which is `F149`(b) and is bigger than either half above**: a **4-pad** screen reported that same cell `RESOLVABLE`/`SIGN-STABLE` with range `0.00` — ⛔ **the opposite verdict on BOTH axes** — because at the four sampled residues the two cells move together and diverge only where the screen never looks. ▶ **Sweep DIFFERENCES at 32 pads or do not claim a verdict about them**; a sparse screen is complete for a CELL and not for a DIFFERENCE, which `php50_align_sweep.py`'s docstring has argued since it was written and which is now MEASURED |
| 152 | ⛔⛔ **34 ROW-SPECIFIC `.temp/` CITATIONS SIT INSIDE HASHED SOURCES — BATCH EACH WITH ITS ROW'S NEXT TASK** | `F151`. ▶ **Run it, do not quote this row**: `python3 .tasks-php/citecheck.py`, the section headed *ROW-SPECIFIC `.temp/` citations inside OTHER HASHED sources*. **118 citations across 35 files** the checker could not see before today — **34 row-specific, 84 inherited through shared files, 1 already gone.** ⛔ **Each sits in `source_sha256`, so repairing one costs that row a RE-GATE and not a re-measure** — which is `citecheck.py`'s own standing rule for `controls/*`, and the reason this is a batching item and not a wave. ⭐ **THE ONE TO DO FIRST IS `ph53/verus.rs:24` and `:350`** → `.temp/php41/probe_wrap.rs`: it is the leftover the `F99` repair was written to catch, it is named in `citecheck.py`'s own comment, and `ph53` is the row most likely to be re-gated next. ⚠⚠ **THIS IS A CANDIDATE SET, NOT A DEFECT COUNT** (`F132`): most of the 118 are provenance notes in comments (*"measured at `.temp/php13/02-reach.log`"*), the same benign class as the 32 historical `controls/*` ones, and **`.temp/php4/*` under `c/emalloc_shim.h` is inherited by all 14 rows** — a corpus-wide debt with items 55/61, not a row's. ⓘ **The six inherited ones are listed separately by the tool for exactly that reason.** ▶ **The rule that decides each: a re-derivable log or blob cited as PROVENANCE is `CLAUDE.md` Don't #1 being followed; a SCRIPT or EVIDENCE DOCUMENT the row's claim depends on is the defect** — the same test item 148 used, applied one layer down | ⚠ **DO NOT "fix" these by committing artefacts.** A `.log` under `.temp/` is deletable by constraint 6; the repair is to drop the pointer or re-ground it, never to freeze the blob |
| ~~153~~ | ✅✅ **DISCHARGED 2026-09-17 — `TASK_PHP_064`. `RESTS` IS NOW `0`, MEASURED, NOT ASSERTED** (`python3 .tasks-php/probes/scratchdeps.py`). **15 files promoted, 13 new registry entries, every probe RUN rather than copied**; `F102` needed a REPOINT, not a promotion. ⭐⭐ **THE ENGINEER FILED FIVE FINDINGS AGAINST MY BRIEF AND FOUR CHANGED SOMETHING PUBLISHED** — item 11 was already done; *"only `F89` and `F95` reviewed"* was wrong (it is **4 of 13**, `F150` corrected in place); `item83_sim.py --selftest` exited **1** where I quoted it as live output; `F69` rests on `enclosing_fn.py` too, which my brief did not name while quoting its number. ⭐ **The §1.1 sibling rule earned itself twice**: `enclosing_fn.py` and `fn_body.py`, **neither findable by the census** — the one place the siblings are named uses a **BRACE EXPANSION** that `PATH_RE` reads as a bare directory, so **four citations register as zero**. ▶ **A third spelling the census cannot see**, after bare filenames (`F147`) and renames (`F150`). ⛔ **TWO PROBES ARRIVED BROKEN WITH NO CACHE PROBLEM — item 149 does not cover this**: `ph29_predict.py` crashed **because its prediction came true** (the simulated edit landed, so its own staleness assert fired) and `item83_sim.py` reddened because `ph53` was **re-searched** under it. ▶ **A probe can rot because the WORLD MOVED THE WAY IT PREDICTED.** ⭐⭐ **TWO PUBLISHED FIGURES MOVED, BOTH RE-VERIFIED BY THE MANAGER INDEPENDENTLY**: `F73` `0 of 6 PHP` → **1 of 14** (and the hit is a **Verus keyword**, so `PROTOCOL_PHP.md` §H1's title does not reach its own subject); `F85` `29 of 38` → **111 of 141**, counted off `--flips` by hand — ▶ **the RATIO survives a 2.3× corpus (76.3 % → 78.7 %) and the COUNT does not.** ⚠ **Quote `29 of 38` only as *that corpus's* number** (law 17). ⚠ **STILL OWED, stated by the engineer**: `F53`'s nine-commit corpus has **no committed generator**; three promoted probes carry **no must-fire negatives at all**, including `count_ent.py`, which this programme cites three times as a cautionary tale. → folded into item **155**. **The original row:** | ⛔⛔⛔ **PROMOTE THE 14 FILES 13 PUBLISHED FINDINGS REST ON — `PROMOTE_001`'s METHOD, AND `F85` FIRST** | `F150`, the discharge of item 148's ruling. ▶ **Run it for the list, do not quote this row**: `python3 .tasks-php/probes/scratchdeps.py`, the `RESTS` block. ⭐ **`PROMOTE_001` discharged 6 files in ONE task**, so 14 is about two — and it is the only task shape in this programme with a measured rate. ⛔ **`F85` FIRST AND IT IS NOT CLOSE**: the finding is *"the programme's central claim"* (29 of 38 sign flips are cross-language), it is **UNREVIEWED**, and **both** its named probes — `.temp/mgr170/callee_share.py` and `.temp/mgr172/STATISTIC-DECISION-DRAFT.md` §5 — are in scratch. ⚠ **`F74` shares `callee_share.py`, so those two discharge together**; `spread_stat.py` comes with them and `null_control.py` is already promoted, which is exactly how this gap survived — **a sibling promotion that took three of four.** ▶ **Order after `F85`/`F74`: `F89`+`F90` (`ph64_draws.py`, one file, two findings) · `F73` (`charlit_reach.py`, 6 negatives lost with it) · `F70`/`F69` (`item48_decide.py`, the measurement that DECIDED item 48) · `F50` (`asan_reach.c` + `REFETCH.sh`) · `F100` · `F95` · `F53` · `F44` · `F102`.** ⭐ **`F95`'s file is the REVIEWER's own counterexample** — `law 12` says the reviewer's independence is the product, and this is the only copy of it. ⚠⚠ **PROMOTION IS NOT COPYING**: `PROMOTE_001`'s engineer refused to copy a header that claimed a guard *"does not fail"* when it does (item 149), and its report filed five findings against my brief. **Each file needs a header stating what it measured, when, and what is still owed** — `NULLCTL_001.md` is the model. ⓘ **Free** — `.tasks-php/` is in no digest | ⚠ **Nothing is lost yet**: all 17 targets resolve today, so this buys durability, not recovery. ⛔ **But `CLAUDE.md` constraint 6 MANDATES deleting `.temp/` once gates are green**, so the expiry is scheduled and not hypothetical |
| 154 | ⛔⛔ **REVIEW STATUS FOR PRE-`F107` FINDINGS IS NOT DERIVABLE, AND TWO HOMES FOR IT DISAGREE** | `F150`. ▶ **Run it**: `python3 -c "import sys;sys.path.insert(0,'.tasks-php');import boxcheck;print(len(boxcheck.rule9_rows(open('RECAP_PHP.md').read())[0]))"` → **44 rows, and NONE of `F44 F50 F53 F70 F72 F73 F74 F85 F89 F90 F95 F100 F102`.** ⛔ **The RULE-9 block has TWO FORMATS**: one finding per row from `F107` on, which the parser reads, and a **grouped verdict cell** for the `_047` era (`⚠ UPHELD-NARROWED | F97 · F102 · F104`), which it cannot. ▶ **So the programme's own home for *has this been reviewed?* is silent on every finding before `F107`** — and `F140`'s round-scoping derives from that same table, so the silence is not cosmetic. ⛔⛔ **AND THE TWO HOMES CONTRADICT EACH OTHER TODAY**: `F102`'s section says `⚠ **UNREVIEWED** (rule 9)` while the `_047` block files it under `UPHELD-NARROWED` with *"narrowings APPLIED not appended"*. **`F131`'s class, on the process state that governs what may enter the authoritative layer.** ⚠⚠ **THIS IS WHY `F150` PUBLISHED A WRONG COUNT**: with no derivable answer I reached for a regex over prose, and `F100`'s `— **UPHELD-NARROWED.` (markdown bold inside the verdict) fell outside the character class — **`F148` in the session that filed `F148`.** ▶ **THE ROUTES, and I have not chosen**: (a) reformat the `_047` block to one row per finding, which is a RECAP edit and makes the parser total; (b) teach `rule9_rows` the grouped cell, which keeps the document as written; (c) accept that pre-`F107` status lives only in each finding's own section and **make `boxcheck` SAY SO** rather than reporting a count that silently excludes 13 findings. ⭐ **(c) is the cheapest and the most honest, and it is `F10`'s rule — a checker that cannot answer must say it cannot**, but it leaves the `F102` contradiction standing, so (c) does not dismiss (a) | ⚠ **A reviewer's, not mine, on one limb**: I am the author of the count that was wrong, so *how much this matters* is not mine to size (`_057`'s engineer refused exactly this shape). ▶ **The MEASUREMENT above is mine and is reproducible; the ROUTE is a decision** |
| 155 | ⚠⚠ **THREE PROMOTED PROBES CARRY NO MUST-FIRE NEGATIVES, AND ONE OF THEM IS THIS PROGRAMME'S OWN CAUTIONARY TALE** | `TASK_PHP_064` §6, the engineer's own statement of what it left undone — ⭐ **volunteered, not extracted.** `PROTOCOL_PHP.md` §H says a validator change lands **with its must-fire negatives or it does not land**; these arrived as *promotions* of pre-existing scratch, so §H never gated them. ⛔ **`count_ent.py` is the sharp one**: `F44` rests on its four-table result, and **`F50`, `F51` and `F52` each cite it as an example of a probe whose SETUP ENCODED ITS ANSWER.** ▶ ***A probe the corpus quotes three times as a cautionary tale, now committed, asserting nothing.*** ⚠ **`F53`'s nine-commit corpus has NO committed generator at all** — only two of the nine commits are named anywhere, so the measurement behind *"`ph32`'s stated R1h is wrong for two of three tables"* cannot be re-run even now that `entcount.py` is promoted. ▶ **That is a law-11 defect the promotion did not close, and it is the ONE the ruling's `RESTS → 0` does not cover** — ⛔ **so do not read `0` as *"nothing is owed"*.** ⭐ **The check that works on this class is already written down** (`F52`): **change the setup's arbitrary constant and see whether the verdict moves.** ⓘ Free — `.tasks-php/` is in no digest | ⚠ **Sizing, honestly: three probes × (one negative that must fire + one that must not) is not a task, it is an hour** — but `F53`'s generator is a re-derivation of a nine-commit sweep and **is** a task. **Do not batch them under one estimate** (item 125 sat six rounds behind an hour-shaped number) |
| 156 | ⚠⚠ **DECIDE WHICH CENSUS OWNS THE STANDING CLAIM DOCUMENTS IN `.tasks-php/` — AND IT IS A CHOICE BETWEEN TWO HOMES, NOT A WIDENING** | `F152`. **8 documents, 35 `.temp/` citations, 9 already gone**, in neither `citecheck.py`'s `CLAIMS` nor `scratchdeps.scan_set()`. ▶ **THE TWO ROUTES ARE NOT SYMMETRIC.** (a) **`citecheck.py`** already owns *"does a cited path resolve?"* across the corpus and **already scans these files for ROT** (they are in `DOCS`); it is only `CLAIMS`, the `.temp/`-dependency hunt, that skips them. ▶ **Adding `.tasks-php/*.md` minus `TASK_PHP_*` to `CLAIMS` is a two-line change to the tool that already reads them.** (b) **`scratchdeps.py`** owns *"which PUBLISHED FINDING rests on scratch?"* and keys everything on `(finding, file)` — but these documents have **no `### F<N>` sections**, so its whole law-11 machinery would be inert on them. ⭐ **(a) is right and (b) is a category error**, which is worth writing down because *"widen the newest tool"* was my instinct and it is the one that does not fit. ⛔⛔ **BUT DO NOT LAND (a) BLIND**: `PROTOCOL_PHP.md` alone adds **18** rows to a report that is already 118 lines long, and `F151`'s repair just taught that **burying the row-specific hits under inherited noise is the failure mode** — so it needs the same INHERITED/ROW-SPECIFIC split, or a `kind=` column. ⚠ **And `citecheck.py` is filed `expect=1`**: a new warning class must not touch `rot`, which is what `N5d`/`N7f` exist to assert. ▶ **Copy `N7f`.** ⓘ Free — `.tasks-php/` is in no digest | ⚠ **The 9 dead pointers are the only part that is urgent**, and they are urgent only in the sense that nobody would ever find out. ⛔ **Do NOT "fix" them by committing artefacts** — most are `.log` files that constraint 6 says to delete. **The repair is to drop the pointer or re-ground it** |
