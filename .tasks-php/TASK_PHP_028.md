# TASK_PHP_028 — discharge the spellings debt on `ph03`, `ph16` and `ph29`

> ✅✅ **REPORTED 2026-09-10. `ph16` IS DISCHARGED; `ph03` AND `ph29` ARE NOT.**
> `TASK_PHP_028_REPORT.md`. One row took the whole task, which §4.2 authorised
> and which was the right call. **`fixed-R4 bound −1.22 %` · `cheapest-found
> in-contract −1.42 %` (`r3_split_at`)**, per-call statistic, both labelled, no
> pair interval, no rung re-shipped.
>
> ⭐⭐ **§4.1 IS ANSWERED AND THE HYPOTHESIS IS REFUTED: on `ph16` the negative
> spread is a RESULT, not a spelling artefact.** The R4 side is **degenerate** —
> four respellings all dearer or byte-identical, **including `r4x_subslice`,
> which is R3's own spelling (+1.80 %)** — and the mirror control settles it:
> `r3_absindex` (R3 given R4's signature) is **byte-identical to
> `safe_naive.rs`** at **+33.07 %**. **The subslice is worth −24.9 % in safe
> Rust and +1.8 % in unsafe Rust, so the two rungs are cheapest under DIFFERENT
> spellings and R3's minimum sits under R4's.** ⚠ **n = 1. Not an effect.**
>
> ⚠ **The remaining two rows need their own task**, and it must carry §3.3's
> correction below: **`ph03` is searchable and `ph29`'s audit would be VACUOUS.**

⚠⚠ **SCOPE GREW ON 2026-09-10 AND THE TITLE USED TO SAY TWO ROWS.** `TASK_PHP_027`
built `ph29`. **THREE of the four built rows now owe this** — ⚠ **but NOT for the
same reason, and an earlier draft of this line said they did.** Re-derived from
the published tables (`Ir`, O3/isolated):

```
ph03   safe_tuned 191,208,596   unsafe 170,434,489   R3-R4 = +12.19 %  POSITIVE
ph16   safe_tuned  88,874,724   unsafe  89,974,452   R3-R4 =  -1.22 %  NEGATIVE
ph29   safe_tuned  23,441,029   unsafe  24,951,895   R3-R4 =  -6.06 %  NEGATIVE
```

- **`ph03`** owes it because it has searched **neither side** and is unbounded in
  **both** directions. Its spread is an ordinary positive one.
- **`ph16` and `ph29`** owe it because their spread is **negative**, so no figure
  in either row is a `fixed-R4 bound` **at all**.

⚠ **Read every "two rows" below as THREE**; those sections were written when it
was two and their argument is unchanged.
⭐ **`ph07` remains the ONLY discharged row and the only template.**

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
`harness-php/gate.py --tool measure --check-stale` → **`10/0`**, first and last.
⚠ **This line said `8/0` until 2026-09-10 and it was STALE** — `TASK_PHP_027`
built `ph29`, and **a row adds TWO measure records**, not one. Both figures were
re-run by the manager at dispatch. **If yours disagrees at the START, stop and
say so**; a bracket that has already moved before you touch anything means
someone else has been in the tree.
⚠ `.temp/php18/` (57 files) and `.temp/php25/` (64 files) were confirmed
**present** at dispatch. `.temp/php28/` does not exist yet — make it.

---

## §1 Why this is its own task

**THREE of the four built rows publish ratios that are not bounded cost
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

Two numbers, **labelled**, for `ph03`, `ph16` and `ph29`:

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

1. ⭐⭐ **THAT THE NEGATIVE `R3ship − R4ship` IS A DEBT RATHER THAN A RESULT — AND
   THIS GOT MUCH MORE INTERESTING ON 2026-09-10.** It is no longer one row:

   ```
   ph16   R3 -3.5 %   R4/R5 -2.3 %   vs c-gcc     safe-tuned CHEAPER than unsafe
   ph29   R3 - R4 = -6.1 % / -6.4 %                same direction, bigger
   ```

   **Two independently built rows, different families, same sign.** ⚠ That is
   weak evidence for a *systematic* effect (the `unsafe` rung has a
   bounds-check-free path the optimiser was already producing anyway) and
   correspondingly weaker evidence for a per-row spelling artefact. ⚠⚠ **But n = 2
   and both were built by the same machinery, so do NOT report it as an effect** —
   **this task is how we find out.** ⭐ **If the answer is "the ladder is
   genuinely non-monotone here", that is a headline result, not a defect** — and
   with two rows it would be the strongest cost finding the programme has.
2. ⚠ **That one task covers THREE rows.** If the first row's search is honest and
   expensive, **stop, ship it, and say the rest need their own task** — that is
   what `TASK_PHP_025` did and it was the right call. ⭐ **Prefer `ph16` or `ph29`
   first**, because they carry §4.1's question; `ph03` is the one that may not be
   searchable at all (§4.3).
3. ⚠⚠⚠ **THIS ITEM NAMED THE WRONG ROW. CORRECTED 2026-09-10 BY `_028`, AND
   VERIFIED BY THE MANAGER FROM THE GATE RECORDS.** It used to read *"`ph03`'s
   declaration backticks nothing, so `spellings` is 0 … if `ph03` cannot be
   searched without first pinning spellings in its contract, say so and STOP."*

   **That sentence is about PAT's `p05`, not `ph03`** — `ph16`'s own hashed
   `why` quotes it verbatim about `p05`, and `check.py` prints it on every
   `ph16` run, which is where I picked it up and mis-transcribed the subject.
   Measured, `.idiom_audit` in `results-php/gate/` and `results/gate/`:

   ```
   p05-index-flatten      spellings  0   forbidden  0   <- the row the sentence is about
   ph00-smoke             spellings  0   forbidden  0
   ph03-uudecode-bound    spellings 11   forbidden  6   <- SEARCHABLE, no spec.md edit
   ph16-fdset-index       spellings 23   forbidden 10
   ph29-recvfrom-alloc    spellings  4   forbidden  4   <- ⚠⚠ ALL FORBIDDEN, ZERO REQUIRED
   ```

   ⚠⚠ **The real hazard is `ph29`, and it is WORSE than the one described.**
   `ph03` searches fine. On `ph29` every spelling is `forbidden` and none is
   required, so **a `spellings.py` cloned from `ph07` would pass every candidate
   while checking nothing** — a **vacuous validator that reports success**,
   which is `PROTOCOL_PHP.md` §H's exact target and F52's family. **`ph29` is
   the row that needs the manager's `spec.md` call, and it must be made before
   a follow-up task touches that row.**

   ⭐ **The lesson is rule 14 again, in the direction that is hardest to catch:
   I copied a TRUE sentence onto the WRONG SUBJECT.** Both halves looked
   verified — the sentence really is in the tree, and `spellings: 0` really did
   happen — so nothing about the claim reads as invented.
