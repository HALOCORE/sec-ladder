# TASK_PHP_028 — discharge the spellings debt on `ph03` and `ph16`

**Role:** research **engineer**. **One agent, alone.**
**Report:** `.tasks-php/TASK_PHP_028_REPORT.md` — **write the FILE** (rule 10).

Read `.tasks/PROTOCOL.md`, **`.memory-php/02-ladder.md` in full — it is the
authority here and it states the debt in terms**, `.tasks-php/PROTOCOL_PHP.md`
(**§H is the one that binds this task**), `.memory/02-bench-rules.md`'s
`fixed-R4 bound` rule, and **`patterns-php/ph07-strcut-cursor/controls/spellings.py`
+ `spellings.json` — the only discharged instance, and your template.**

⚠⚠ **`RECAP_PHP.md` and `.memory-php/` ARE MANAGER-ONLY FOR WRITING.**
⚠⚠⚠ **NO EDITS under `harness/`, `common/`, `patterns/`, `results/`, `pilot/`.**
⚠ **Do not edit `patterns-php/ph07-strcut-cursor/`** — it is discharged and was
re-gated two days ago. **Read it, do not touch it.**
⚠ **No `git add` / `git commit`.** Never touch `.web/`.
⚠ Scratch under `.temp/php28/`. **Never `/tmp`.** `.temp/php18/` holds `ph07`'s
spellings work and `.temp/php25/` row 3's — **reuse them.**

**Bracket**: `harness/measure.py --check-stale` → **`66/0`** and
`harness-php/gate.py --tool measure --check-stale` → **`8/0`**, first and last.

---

## §1 Why this is its own task

**Two of the three built rows publish ratios that are not bounded cost
statements**, and that undermines the one thing this programme exists to
measure. `.memory-php/02-ladder.md`:

> *"NO RATIO HERE IS **THE** COST OF SAFETY, AND THESE ARE `fixed-R4 bound`s —
> PAT's term, and PAT's rule is that a bound ships LABELLED, beside a
> cheapest-found counterpart."*

⚠ **`ph03`'s own hashed `why` has demanded it since the row was built** —
*"Every pattern owes an in-contract spread beside its headline."* **Undischarged,
not unforeseen.** `ph16` acquired the same debt yesterday, deliberately:
`TASK_PHP_025` was told to say if carrying it made the build two tasks, **and it
did**. ⚠⚠ **So `ph16` ships with `R3ship − R4ship` NEGATIVE and no figure in the
row is a `fixed-R4 bound` at all.**

## §2 What ships, per row

Two numbers, **labelled**, for `ph03` and for `ph16`:

```
fixed-R4 bound              R3ship - R4ship          both held by fiat
cheapest-found in-contract  inf(R3 found) - R4ship   name the spelling AND the input
```

⚠⚠⚠ **AND NO PAIR INTERVAL.** `min(R3 found) − min(R4 found)` differences two
upper bounds and **bounds nothing in either direction**. `ph03`'s hashed `why`
retracts that construction in terms — **do not resurrect it.**
⚠⚠ **DO NOT RE-SHIP A RUNG.** `.memory/02-bench-rules.md`: the shipped rung is
chosen by **idiom**, before measurement, and it **stays**. A cheaper in-contract
spelling moves the **published bound**, not the row.

**Search BOTH sides.** ⚠ `ph07`'s R4 side came back **degenerate** — seven
spellings from two agents, none cheaper than a tie — making it the **12th of 20**
rows where an R4-side search found nothing. ⭐ **A degenerate result is a real
result and is worth reporting plainly**; a bound over a *searched* endpoint is a
materially stronger object than one over an unsearched endpoint, which is the
whole point of the exercise.

## §3 ⚠ The traps this specific task walks into

1. ⚠⚠⚠ **IMPORT `measure.py`'s STATISTIC. DO NOT RE-IMPLEMENT IT.** `ph07`'s
   first draft re-implemented it, **measured a different statistic and landed
   1 % off the record** (`TASK_PHP_024` §1.6 imported it; copy that).
2. ⚠⚠ **A `spec.md` edit stales `controls/spellings.json`.** Measured at
   `TASK_PHP_024` §4.2: **`ph07`'s sidecar is the only one in the tree that pins
   `spec.md`** (47 PAT sidecars checked). **If your work requires a `spec.md`
   edit, the sidecar must be regenerated** — and say whether pinning `spec.md`
   was the right design or whether it should pin the contract block only.
3. ⚠ **The gate hashes `controls/*.py`.** Adding one **moves the row's identity
   and costs a re-gate on that row.** Budget two re-gates; `TASK_PHP_018` needed
   **eleven** rounds and every extra one caught a real defect.
4. ⚠⚠ **`PROTOCOL_PHP.md` §H: `spellings.py` IS A VALIDATOR.** It ships with a
   must-fire and a must-NOT-fire case, run, output pasted. ⚠ **The gate hashes
   `controls/*.py` and never RUNS them** (`_022` m6), so the negatives are the
   only thing standing between this file and a silent wrong number.
5. ⚠ **A probe whose SETUP encodes the answer evaluates fine and is wrong** —
   five shapes now (F52/F54). **A spellings search is unusually exposed to
   this**: the candidate set is chosen by the same person who reports that
   nothing cheaper exists. **Say how you chose the candidates, and how you would
   know if the set were too narrow.**

## §4 What I am least sure of

1. ⚠⚠ **That `ph16`'s negative `R3ship − R4ship` is a debt rather than a
   result.** Row 3 measured R3 at **−3.5 %** and R4/R5 at **−2.3 %** against
   `c-gcc`, so **safe-tuned is CHEAPER than unsafe on that row** — which may be
   real (the `unsafe` rung has a bounds-check-free path the optimiser was
   already producing) or may be a spelling artefact. **This task is how we find
   out, and if the answer is "the ladder is genuinely non-monotone here", that
   is a headline result and not a defect.**
2. ⚠ **That one task covers two rows.** If the first row's search is honest and
   expensive, **stop, ship it, and say the second needs its own task** — that is
   what `TASK_PHP_025` did and it was the right call.
3. ⚠⚠ **That searching is even well-defined on `ph03`.** ⚠ **`ph03`'s
   declaration backticks nothing**, so `spellings` is 0 and admission is decided
   by prose plus one grep — the exact condition that made PAT's `p05` audit
   **unable to settle its own row**. **If `ph03` cannot be searched without first
   pinning spellings in its contract, say so and STOP** — that is a `spec.md`
   change inside a hashed block and it is the manager's call, not yours.
