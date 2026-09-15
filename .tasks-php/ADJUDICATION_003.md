# ADJUDICATION_003 — **open item 121: three families have one row each, so `QUOTA_001`'s min-2 floor is arithmetically unreachable for them**

**Manager, 2026-09-15.** ⚠ **UNREVIEWED.** Written while `TASK_PHP_056` was
running; it touches no file that task reads or writes.

**The item, in one line:** `S5` (`ph37`), `S6` (`ph38`) and `T4` (`ph54`) each
hold **exactly one** catalogued row, while `QUOTA_001`'s rule is *"min 2 per
family, cap 4"* and the published floor is **20 × 2 = 40**. `TASK_PHP_054` agent
C found it, stated it as programme arithmetic and **explicitly not** as a
down-rank — all three rows pass the C-side bar and agent C says so in terms
(`CLAUDE.md` rule 6). **Three routes were offered and the manager owes a choice.**

---

## §1 THE DECISION

> ### ✅ **ROUTE (a): the floor becomes `Σ min(2, |family|)` = 37.**
> ### ⛔ **ROUTE (b) — merging the singleton families — is REJECTED.**
> ### ⏳ **ROUTE (c) — growing the catalogue there — stays OPEN as a MEASURABLE question, and is recorded as a hope until someone measures it.**

**Floor 40 → 37. Owed 30 → 27.** ⓘ `task_cost.py`'s projection is unaffected —
it counts rows owed, not families — but the figure is quoted in `RECAP_PHP.md`'s
START HERE box, so this changes a published number.

⚠⚠ **AND (a) IS NOT JUST ARITHMETIC. IT IS A CONCESSION, AND IT MUST BE STATED
AS ONE** — see §2. Lowering the number quietly would hide the thing worth knowing.

---

## §2 ⭐⭐⭐ WHAT ROUTE (a) CONCEDES, IN `QUOTA_001`'s OWN WORDS

`QUOTA_001` §3 does not give *"min 2"* as a round number. It gives a **reason**:

> **Minimum 2 per family** — because **n = 1 cannot detect the S1 effect**, and
> **S1 proves n = 1 would have published a wrong answer.**

And the programme has since **measured the thing the rule buys**. `ph55` and
`ph56` are `T5`'s two rows, and `TASK_PHP_051` §1 required the pairing to be
written down because it is a result **neither row has alone**:

> *Both are "the emitted program is not the one the executor expects"; **both
> upstream fixes are THE SAME THREE-LINE SHAPE** — a guard that already exists
> elsewhere in the same function, copied onto the arm that lacks it — **and the
> two HARMS are completely different.***

▶ ⛔⛔ **SO ROUTE (a) CONCEDES, IN PLAIN TERMS: `S5`, `S6` AND `T4` CAN NEVER
PRODUCE A FAMILY-LEVEL FINDING, AND WHATEVER THEY PUBLISH WILL BE A ONE-ROW
CLAIM WITH NO WITHIN-FAMILY CONTROL.** That is a **known limitation of the
corpus**, not an accounting detail, and it belongs in the crash course beside
the S1 story rather than in a footnote.

⭐ **Recording it is most of the value of this adjudication.** The number falling
from 40 to 37 is worth nothing on its own; *"three of twenty families are
structurally incapable of the programme's own control"* is worth a paragraph.

---

## §3 WHY (b) IS REJECTED — and it is the route I was most tempted by

**Route (b):** merge the singleton families into their nearest neighbours.

**Three reasons, in increasing order of weight:**

1. ⚠ **It barely works.** The best merge candidate is `T4` → `T6` (§4). That
   leaves **19 families and TWO remaining singletons**, so the floor becomes 38
   and `S5`/`S6` are untouched. **It solves at most one third of the problem and
   costs a catalogue adjudication to do it.**
2. ⛔ **`S6` is a singleton BECAUSE OF HOW IT ARRIVED, and merging it would
   repeat the mistake that made it one.** Its own `⚠ risk` note says `ph38` was
   *"routed away by the spatial miner as 'a value-model property, not a spatial
   one' and **never picked up by anyone**"*. **A row that fell between axes was
   given its own family so it would stop falling.** Folding it back into a
   neighbour is the same move that lost it the first time.
3. ⛔⛔ **IT HAS THE SHAPE OF THE `C.1` SET-KILL, AND THAT SHAPE HAS ALREADY COST
   THIS PROGRAMME 17 REVERSALS.** `TASK_PHP_019` §6's finding is that ids killed
   **inside a set** never acquired a row-level entry to attack — *"three ids
   killed TWICE, once inside `C.4`'s six-member set, then again inside a
   one-sentence three-id row, so neither kill ever acquired a row-level entry"*.
   ⚠ **A merge is not a kill** — `ph37`, `ph38` and `ph54` would all survive,
   re-filed. **But the mechanism that made `C.1` wrong was set-level reasoning
   replacing row-level reasoning, and (b) is set-level reasoning.**

▶ **(b) may still be right. It is not rejected on the merits of the taxonomy —
it is rejected as a MANAGER decision taken from a desk.** If it is taken, it is
taken by an adjudication with a row-level entry per affected row, like
`ADJUDICATION_002`, and not by lowering a count.

---

## §4 ⭐⭐⭐ THE THING I FOUND WHILE DECIDING, WHICH IS WORTH MORE THAN THE DECISION

**`T6`'s family name is FALSE of three of its five members, and `CATALOGUE.md`
says so itself.** From `ph60`'s own `⚠ risk` note, verbatim:

> *In `ph96` the call returns **SUCCESS** and NULLs the out-parameter on purpose;
> in `ph97` the failure **is** tested and the call does **not** fail (`|` makes
> the argument optional); in `ph98` the failure is tested and it is the **error
> branch** that faults. **"Failure not tested" is false at all three.***

And `T4`'s single row, `ph54`, is *"`!p` where `!*p` was meant"* — **a guard that
is present, runs, and can never fire, because it tests the wrong depth.**

Put the two sentences side by side:

| row | family | the guard | what it answers | what the code needs |
|---|---|---|---|---|
| `ph54` | **T4** — *the guard is at the wrong depth* | present, runs, **never fires** | *"is the out-parameter pointer NULL?"* | *"is the pointed-to value NULL?"* |
| `ph97` | **T6** — *a fallible call whose failure is not tested* | present, runs, **passes** | *"were the supplied arguments well-typed?"* | *"was the optional argument supplied?"* |

⭐⭐ **These are the same sentence.** The unifying mechanism of `T4`, and of at
least three of `T6`'s five rows, is ***a guard exists and does not establish the
property the code relies on*** — which is also, read generously, `S2`'s
(*"a guard that runs and is wrong"*, n = 8).

### ⛔⛔ AND I AM NOT ACTING ON IT. HERE IS WHY, AND IT IS NOT TIMIDITY.

1. **It is one manager reading of Part B entries, from a desk, with no C read
   beyond the two rows above.** `.memory-php/04-process.md` law 12 and six
   consecutive review rounds say assume it narrowable.
2. **It is exactly the class of claim `TASK_PHP_019` had to reverse 17 times.**
   A taxonomy argument that groups rows by a *sentence* rather than by their C
   is how the mining wave produced set-kills.
3. ⚠⚠ **`TASK_PHP_056` IS BUILDING `ph97` RIGHT NOW as "`T6`'s first row".**
   ⭐ **This does not affect that task and I checked**: `TASK_PHP_056` describes
   `ph97`'s mechanism from the C, line by line, and **never leans on `T6`'s
   name**. The row is admissible on the C either way (`CLAUDE.md` rule 6).
4. ⛔ **But it DOES affect row 12.** The plan is *"`ph96` closes `T6`"*, and the
   family-level finding that closure is supposed to buy would then rest on a
   family name the catalogue itself contradicts.

▶ **ROUTED, NOT DECIDED.** ⭐ **The question for a reviewer or miner, stated so
it can be answered against the C rather than against the prose:**

> **Is there a C-side mechanism distinction between `ph54` and `ph96`/`ph97`/`ph98`
> — and between those and `S2` — or is *"a guard that does not establish the
> property relied on"* one family that the mining wave split three ways on the
> strength of where the guard sits rather than what it fails to establish?**

⚠ **Whoever answers it must answer from the C**, and must remember that **a
merge changes a published number while a re-naming does not** — ⭐ **and that
renaming `T6` to describe its actual members is available, costs nothing, and is
not a merge.** That may well be the whole repair.

---

## §5 WHY (c) STAYS OPEN, AND WHAT WOULD CLOSE IT

**Route (c):** the catalogue gains rows in `S5`/`S6`/`T4` from the **8 withdrawn
`C.1` kills**, *"which is where the original members went."*

⛔ **Measured: that has ALREADY HAPPENED, and it did not help.** The `C.1`
reversals landed as `ph96`, `ph97`, `ph98` and the four `LOGIC` family-E rows —
**in other families**. ▶ **So (c) as agent C stated it is spent.**

⚠ **But the general version is alive and I cannot answer it from here.** The
corpus has **166 ids** and the catalogue has **102 rows**; the difference is
merges and kills. ▶ **The question that would close (c) is bounded and
mechanical:**

> **Does any id not currently carrying a row belong in `S5`, `S6` or `T4`?**

⭐ **That is a mining question, cheap, and it has a clean negative** — *"no, and
here is the list I checked"* is a real answer and closes the item. ⛔ **It is
NOT a question the manager should answer by guessing**, which is the whole
reason (c) is recorded as a hope rather than taken as a route.

ⓘ **Until it is measured, (a) stands.** (a) and (c) are not exclusive: if the
catalogue grows, `Σ min(2, |family|)` grows with it **automatically**, because it
is a derivation and not a pin — which is the fourth reason to prefer it.

---

## §6 WHAT LANDS, AND WHAT DOES NOT

| | |
|---|---|
| ✅ **`quota.py`** | `floor` becomes `Σ min(2, \|family\|)`, **derived from the parsed family table**, never a literal. ⛔ **§H: it lands with must-fire negatives INSIDE the tool** — at minimum, an arm that the derived floor equals `2 × families` when no family is a singleton, and one that it is strictly less when one is. ⚠ **`.memory-php/04-process.md` law 6: a bound is not a derivation** — `40` was a pin and pins in this programme have gone stale **seven** times |
| ✅ **`RECAP_PHP.md`** | item 121 closed with this file as its adjudication; the START HERE box's *"30 owed"* becomes **27**; §2's concession recorded where a reader will meet it |
| ⏳ **the §4 question** | **ROUTED to the next review or mining round. NOT a catalogue change today** |
| ⛔ **`CATALOGUE.md`** | **UNTOUCHED.** No row is merged, re-filed, re-named or moved by this adjudication |
| ⛔ **`.memory-php/`** | **NOTHING.** This is unreviewed manager work; rule 9 |

⚠⚠ **TIMING: `quota.py` and `RECAP_PHP.md` are NOT edited while `TASK_PHP_056`
runs** — `PROTOCOL.md` rule 11, widened: *do not edit, and do not commit, a file
a running subagent reads.* **This document is written now and lands when the
row does.**
