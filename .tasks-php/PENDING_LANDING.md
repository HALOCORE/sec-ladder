# PENDING — what lands the moment `TASK_PHP_056` returns

**Manager, 2026-09-15.** ⛔ **DELETE THIS FILE WHEN IT IS CONSUMED.** It is a
worklist, not a record; everything on it has its evidence elsewhere.

> ⭐⭐ **WHY IT EXISTS, AND IT IS THIS SESSION'S OWN LESSON.** `TASK_PHP_057`
> §1.2a records a check decaying from *"the cheapest remaining"* to *"impossible"*
> across four documents because **nobody wrote down that it was still owed**.
> Everything below is blocked by `PROTOCOL.md` **rule 11** — *do not edit, and do
> not commit, a file a running subagent reads* — and `RECAP_PHP.md`,
> `PROTOCOL_PHP.md`, `.memory-php/`, `quota.py` and `contract_audit.py` are all
> on that list while `_056` runs. ⛔ **A queue held in the manager's head across
> a compaction is exactly the failure this file is named after.**

---

## 1. ⭐⭐⭐ `F123` — IT EXISTS ONLY IN `TASK_PHP_057` §1.2a AND IN A COMMIT MESSAGE

**Write it into `RECAP_PHP.md`'s findings section and index.** The material is in
`.tasks-php/TASK_PHP_057.md` §1.2 and §1.2a, complete, with its four-row table.

**The headline:** *"PHP 5.0.0 cannot be rebuilt on this box" is false — there is
a tracked, idempotent build script — and the obligation it was used to exclude
from `PROTOCOL_PHP.md` §A3a had been proposed by an engineer as **"the cheapest
remaining check"**, demoted by the manager to **"nice to have, skip it"**,
skipped, and then re-derived as impossible from a different agent's sentence.*

⭐ **The structural half is the valuable half: the programme's characteristic
failure mode is a conclusion surviving while its reason dies; this is that
BACKWARDS** — the reason decayed (*"I didn't"* → *"not owed"* → *"I can't"* →
*"one can't"*) while the conclusion hardened into a protocol section.

⚠ **`F123` is UNREVIEWED and goes in the RULE-9 table as such**, and it is a
manager finding about the manager. **Review scope becomes `F114`–`F123`, ten.**

## 2. `PROTOCOL_PHP.md` §A3a — must not read as COMPLETE

§A3a lists four obligations. **A fifth is missing and the reason given for its
absence was false.** ⛔ **Do NOT write the fifth obligation yet** — `_057` §1.2
asks the reviewer whether it should be REQUIRED or merely PERMITTED, and
requiring it makes every row pay for a full PHP compile. ▶ **Add one line saying
the list is under review and pointing at `_057` §1.2.** Nothing more.

## 3. Item 121 → `ADJUDICATION_003.md`

- `quota.py`: `floor` becomes **`Σ min(2, |family|)` = 37**, derived from the
  parsed family table, **never a literal**. ⛔ **§H: lands with must-fire
  negatives INSIDE the tool** — one asserting the derived floor equals
  `2 × families` when no family is a singleton, one asserting it is strictly
  less when one is.
- `RECAP_PHP.md`: item 121 closed citing the adjudication; **START HERE's
  *"30 owed"* → 27**; §2's concession (*three families can never produce a
  family-level finding*) recorded where a reader meets it.
- ⏳ **The `T4`/`T6` question is ROUTED, not decided.** `CATALOGUE.md` untouched.

## 4. Item 119 → `ADJUDICATION_004.md`

- `PROTOCOL_PHP.md` §C: the `fix_commit` **column is EVIDENCE for R1h, not a
  definition of it**. ⚠ **Applied in place, not appended** (item 73, ×7).
- `RECAP_PHP.md` item 119 re-framed: **`ph90` solved (`0542a6f2c2a5`, adopt it);
  four rows need a SEARCH scheduled with the row that needs them; `ph74` routed.**
- ⛔ `CATALOGUE.md` untouched — editing the column destroys F38's and F118's
  evidence.

## 5. `task_cost.py` — and `N14` is *designed* to fail until both halves are done

On landing: **add `ph97` to `ROWS`** (build order, last) **AND** change
`"056"` from `"PENDING"` to `{"ph97": 1.0}`. ⚠ **N14 fails until the first half
is done and `N1` never sees the second** — that asymmetry is deliberate and is
written in the classification comment.

## 6. `RECAP_PHP.md` — the ordinary landing

Rows built **10 → 11**; the `T6` cell; the tasks cell (**`_056` reported**, and
⛔ **diff the report before believing it — a task-notification means STOPPED, not
FINISHED**, item 118); `which statistic`; START HERE's NEXT → **`ph96` closes
T6**, with ⚠ **row 13 SHOULD be temporal** carried forward.

## 7. ⭐ NEW ITEM TO OPEN — the sweep cannot tell *in flight* from *rotted*

**Measured twice now, in two different checkers:**

- `citecheck.py` — rot rose while `_054`'s three **split-named** reports were
  unwritten (**F122**, repaired).
- `contract_audit.py` — **red RIGHT NOW**, `N8` reporting three UNFILED
  `VERDICT` hits in `ph97`'s `c/*`, **because `_056` is mid-build**. ⭐ The
  ratchet is working perfectly; what is missing is that the sweep files it as
  `expect=0` and a reader sees a failure with no context.

▶ **The shape of the repair already exists**: `quota.py`'s `N1` prints
**`⏳ IN PROGRESS`** for a row with a directory and no gate record, and declares
itself **`VACUOUS TODAY`** rather than passing silently (item 114, F10).
⛔ **Do NOT suppress the red** — an unfiled adjudication SHOULD block. **Label
it.** ⚠ **`contract_audit.py` was not edited today because `_056` may read it.**

ⓘ **Relayed to `_056` mid-task rather than fixed**, with the cost stated (free
now; a 32-cell re-measure after the row gates, `c/*` being in the measurement
digest) and with three explicit non-instructions: I did not edit its row, I did
not call the comment wrong (`UNFILED` ≠ defect), and I did not ask it to tune
the regex.

---

## ⛔ WHAT IS **NOT** ON THIS LIST, DELIBERATELY

- **Item 105** — still the **USER's** decision: (a) edit `harness/check.py`, a
  33-row re-gate that buys publishing the verified byte-identical zero-cost TCB
  reduction, or (c) leave it, which is what `gate.py`'s own header prescribes.
  ⭐ **I proceed under (c) and will not take (a) unasked.**
- **Dispatching `TASK_PHP_057`** — written and held. **One agent at a time.**
- **Answering `_057`'s own questions** — ⛔ **pre-answering them would destroy
  the round.** `PROTOCOL.md` rule 14: a premise in a task file is one the agent
  has no reason to doubt, **and that is precisely how `F123` happened.**
