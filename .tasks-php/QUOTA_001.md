# QUOTA_001 — how many rows this programme builds, and the rule for stopping

**Author: the manager.** ⚠⚠ **UNREVIEWED.** `PLAN_PHP.md` §8 says *"Do not fix a
row count before Phase 1 reports."* **Phase 1 has reported** — 93 rows — so the
decision is due, and it has been due since the catalogue landed without anyone
noticing. **Nothing here is landed in `PLAN_PHP.md`** (rule 9, and that file is
open in a running agent).

---

## §1 The fact that reframes the question

**Both built rows are in the SAME family.** Measured over `CATALOGUE.md` Part B:

```
93 rows in 20 mechanism families    S1-S6 (spatial 40) · T1-T6 (type 22) · E1-E8 (temporal 31)
S1  unbounded cursor walk   9 rows   <== ph03 AND ph07
```

⚠⚠ **THAT BLOCK IS THE STATE AT `TASK_PHP_020`. IT IS NOW STALE AND KEPT ONLY
BECAUSE §2 ONWARDS ARGUES FROM IT.** Re-derived 2026-09-10 (`quota.py`):

```
102 rows in 20 mechanism families   spatial 42 · type 29 · temporal 31
S1  unbounded cursor walk   9 rows   <== ph03, ph07     (open)
S2  a guard that runs and is wrong   8 rows  <== ph16   (owes 1)
                                     18 other families owe 2 each
built 3 · floor 40 · still owed 37
```

⚠ **SUPERSEDED 2026-09-10 — `TASK_PHP_027` built `ph29` (S3).** Current:

```
built rows  4   ph03, ph07 (S1)  ·  ph16 (S2)  ·  ph29 (S3)
S1  9 rows  n=2  OPEN     S2  8 rows  n=1 OWES 1     S3  17 rows  n=1 OWES 1
floor = 40 · built 4 · still owed 36
```

⚠⚠ **AND THE AXIS GAP DID NOT CLOSE — IT WIDENED IN IMPORTANCE.** All **four**
built rows are **SPATIAL**; **TYPE (29) and TEMPORAL (31) are still ZERO**.
✅ `ph29`'s reason for jumping the queue is now **discharged**, so the argument
that deferred the temporal axis has been spent: it was *"`ph29` is the only row
that cannot pass unless the allocator shim is faithful"*, and `TASK_PHP_027`
proved the shim (F65). **There is no longer a stated reason to build a fifth
spatial row before a temporal one.**

⭐⭐ **THE FACT §1 IS BUILT ON IS NOW HALF-REPAIRED, AND THE OTHER HALF IS
WORSE.** `ph16` (`TASK_PHP_025`) is the first row outside `S1`, so *"both built
rows are the same family"* no longer holds. ⚠⚠ **But all FOUR built rows are
SPATIAL, and the TYPE and TEMPORAL axes have ZERO** — 60 catalogued rows, no
measurement. **The between-family gap this file was written about is smaller
than the between-AXIS gap nobody had named.** `TASK_PHP_027` took `ph29`
(spatial) anyway, on a stated reason about the allocator shim that the temporal
axis depends on — ⚠ **that reason is now SPENT: the shim is proven (F65), so it
cannot be used again.** ⭐ **The next row should be TEMPORAL unless someone
states a new reason.** The manager's finalists are in `RECAP_PHP.md`'s box:
**`ph64`** (8-line `zend_llist_apply`, ONE corpus id, write-after-free) against
**`ph61`** (5 ids / 5 fix commits, so it also owes item 48's §F5-for-five call).
⚠⚠ **The manager's stated reason for `ph64` is that it is the smallest honest
specimen — which is the CHEAPEST-NEXT heuristic §3 exists to remove. It is
defended on the grounds that the maximal-difference clause governs the SECOND
row in a family and both `E1`/`E2` are at n = 0. ATTACK THAT, do not accept it.**

⚠⚠ **THOSE NUMBERS WERE COUNTED BY HAND, ONCE, AGAINST A CATALOGUE TWO RUNNING
TASKS WERE EDITING. RE-DERIVE THEM — DO NOT TRUST THIS BLOCK:**

```sh
python3 .tasks-php/quota.py        # from the repo root; writes nothing
```

It prints the family sizes, which families the built rows are in, the rows still
owed to reach the floor, and it **cross-checks Part A's section against Part B's
axis per row**. ✅ Its first run reproduced, from scratch and by a different
route, the two defects already on file — the section headers declaring **91**
against 93 rows, and **`ph92`/`ph93` filed under *Temporal* in Part A while
Part B has them in `S3` (spatial)**. ⚠ **It exits non-zero while either stands**,
so it will stay red until `land_019_020.py` moves them. ⚠ **If it cannot parse
the catalogue it prints `CANNOT EVALUATE` and exits 2** — it never prints a
number it could not derive.

⚠ **`RECAP_PHP.md` has said *"rows built: 2"* for four tasks and no document
anywhere says they are the same family.** The programme's first comparative
result (F41 — *the two rows disagree about what safety costs*) is therefore a
**within-family** comparison, and every use of it as *"two rows"* overstates the
spread it covers.

⭐⭐ **But read the other way it is the most useful thing the programme has
produced, and it decides the quota.** Two rows from **one** family disagreed on
almost everything §9 asks:

| | `ph03` | `ph07` |
|---|---|---|
| the upstream fix costs | a **rate** (sign depends on the compiler) | a **constant** |
| the upstream fix is | **dead in one hunk, incomplete in the other** | **complete — and TOO BIG; upstream deleted half of it** (F43) |
| R2–R5 vs R1h | must **diverge** | are **ports** of it |
| what tuning recovers | 86.4 % of the naive gap | 76.6 % shipped, and an R3-side search then found **+13.50 % → +2.62 %** |

⚠ **Count that honestly: those are FOUR PROPERTIES, not "four of §9's six
questions."** They map onto §9 items **2** (*what goes wrong, and the real
upstream fix*), **3** and **4** (*the naive and tuned translations, and what
they cost*). ⚠⚠ **Items 1, 5 and 6 — the citation, what `unsafe` buys against
what the proof costs, and which invariant moved — have NOT been compared across
the two rows at all**, and item 5 cannot be until a spellings search exists on
either (F42). **So the disagreement is measured on half the axes and unmeasured
on the other half; do not report it as six.**

⚠⚠⚠ **Even at three axes the conclusion holds: the WITHIN-family variance is
large, and the BETWEEN-family variance has never been measured at all.** Had the
programme built one row per family — the obvious plan — **S1's published answer
would have been whichever of these two we happened to pick.** ⭐ **We know this
only because we accidentally built two from one family.** That accident is the single most informative thing in the programme's
cost record, and it should become the method rather than stay an anomaly.

## §2 The rate, measured

| | |
|---|---|
| `ph03` | `TASK_PHP_013` build, `_014` review (+ a share of `_012`'s prep) |
| `ph07` | `TASK_PHP_015` prep (**stalled — "no fix exists", overturned**), `_016` build, `_017` review, `_018` rebuild |
| **per row** | **≈ 3.5 tasks**, against `PLAN_PHP.md` §8's PAT-measured **~3** |

⚠ **The overhead is NOT the tax it looks like.** `_015`'s stall produced F34/F38
and `FIXSURVEY_001`, which answered *"where is the upstream fix?"* **once, for
all 91 rows**; `_017`'s review produced `UPSTREAM_002` and F43. **Both were
one-time corpus-wide costs charged to a row.** The marginal rate for a row built
now, with the fix already surveyed and the R1h rule written, is **≈ 3 and
falling** — but that is a projection, not a measurement, and it is the first
thing the next two rows will test.

**At 3.5 tasks/row: all 93 ≈ 325 tasks · one per family ≈ 70 · two per family ≈ 140.**

## §3 The decision — an ADAPTIVE quota with a stated stopping rule

**Do not fix a number. Fix a rule, and let the corpus's own variance set the
count.**

> **THE RULE.** Build a family's rows one at a time, each chosen to be the **most
> different admissible row remaining in that family**. A family is **SETTLED**
> when a newly built row **fails to move any of `PLAN_PHP.md` §9's six
> answers** in a way an already-built row in that family does not. Until then it
> is **OPEN** and gets another row.
>
> **Minimum 2 per family** — because n = 1 cannot detect the S1 effect, and S1
> proves n = 1 would have published a wrong answer.
> **Cap 4 per family**, and a family still open at 4 is itself the finding:
> *this mechanism does not have a characteristic cost*, which is worth more to
> the crash course than a fifth row.

**What this gives, on today's catalogue:** a floor of **40 rows** (20 families ×
2), a ceiling of 80, and a *decidable* stopping point per family rather than a
budget nobody can defend. ⚠ **It is a floor of ~140 tasks. That is the real
price of the programme and it should be visible in the handoff**, not discovered
at row 30.

⭐ **And it makes the ordering matter more than the count.** Within a family,
pick the row **most unlike** the one already built — the opposite of the
cheapest-next heuristic that produced two S1 rows in a row. **`ph07` was picked
because `ph03` had made the machinery work on that shape.** That is exactly the
selection bias this rule exists to remove.

## §4 What follows immediately

1. ✅ **The standing batch is already right and should not change** — `ph21`
   (S3), `ph16` (S2), `ph12` (S2), `ph29` (S3) leave S1 and open two families.
   ⚠ **But `ph16` and `ph12` are BOTH S2 and `ph21`/`ph29` are BOTH S3**, which
   is the minimum-2 rule satisfied by luck rather than by design. **Say so in
   the task files, so the second row of each pair is chosen for maximal
   difference and not for convenience.**
2. ⚠ **S1 is NOT settled at 2** — `ph03` and `ph07` disagreed on four of six
   axes, so by the rule S1 is **OPEN** and owes a third row. **It does not get
   one next**: two open families with n = 0 beat a third row in a family with
   n = 2. **Record the debt, do not pay it yet.**
3. ⚠ **A rot to batch**: Part A's section headers read **`Spatial (38)`** ·
   `Type / initialisation (22)` · `Temporal (31)` = **91**, and the table holds
   **93** — `ph92`/`ph93` were added to the spatial section and the header was
   not moved. **Two rows also carry an empty `tier` cell.**

## §5 What I am least sure of

1. ⚠⚠ **That "fails to move any of the six answers" is decidable.** It is a
   judgement, and this programme's own record is that judgements written as
   criteria get applied inconsistently (F8, F21, F37). **The honest version may
   be *"a reviewer must state, per axis, whether the new row moved it"*** — a
   six-cell table per row, which is checkable, rather than a verdict, which is
   not. **If the first application of this rule is a coin-flip, that is the
   defect and it is mine.**
2. ⚠⚠ **That 20 families is the right granularity at all.** They came from one
   adjudication pass and `TASK_PHP_019`/`_020` are attacking the catalogue right
   now. **If either finds the family boundaries are wrong, the quota moves with
   them** — this document must be re-derived after they report, not defended.
3. ⚠ **That the marginal rate really is falling.** §2's *"≈ 3 and falling"* is a
   projection with n = 2, and **this programme has three separate findings about
   numbers that were projected and then cited as measured** (F4, F12, F32).
   **Treat it as unmeasured until `ph21` and `ph16` report.**
