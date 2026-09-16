# TASK_PHP_063_REPORT — the tenth review round

**Role:** research reviewer / analyst. One agent, alone.
**Brief:** `.tasks-php/TASK_PHP_063.md`. Binding order `§1 → §2 → §3 → §4 → §5 → §6 → §7`.
**Tree state at start:** `bcee07c` (`git log --oneline -1`), working tree clean.
**All readings below are dated EVENTS at `bcee07c`, 2026-09-16, unless a
different commit is named. They are HISTORICAL, not live.**

> ⚠ Written incrementally. `§ ORDER TO RESUME IN` at the end is the binding part
> for anything I did not reach.

---

## §0 SCOPE, DERIVED BY ME, NOT READ OFF THE BRIEF

`PROTOCOL.md` rule 14 / the brief's own `⛔ Count the manager findings yourself`.

**EVENT, `bcee07c`** — `python3 .tasks-php/boxcheck.py`:

```
RULE-9 rows          41  41 distinct, 8 open cycle(s): F146 F143 F144 F145 F142 F141 F140 F139
items -> a reviewer   9  LIVE, unscheduled: 125 126 135 137 139 144 145 146 147
```

Both sets reproduce the brief's scope exactly, **member for member**, not just by
count (`F138`: a cardinality is not a membership). 17 objects.

### 0.1 ⚠ ONE PREMISE OF THE BRIEF DOES NOT REPRODUCE — and it is `F121`'s own law, fired on the brief's closing note

The brief's closing paragraph (and my dispatch message) says *"**Eight** of the
seventeen objects are the manager's own findings."* Taking *"the manager's own"*
to mean **who opened it**, read off the RULE-9 table's `⛔ UNREVIEWED` cells and
the items table's provenance clauses:

| object | opened by |
|---|---|
| `F146` · `F142` · `F141` · `F140` | **manager** (4) |
| `F143` · `F144` · `F145` | engineer, `_062` |
| `F139` | **reviewer** (`_061` §3.3), manager-*verified* |
| item 125 · 126 | manager (both are `F123`, *"the question the manager cannot answer about the manager"*) |
| item 137 · 144 · 145 | manager, 2026-09-16 pre-compact audit |
| item 135 | engineer, `TASK_PHP_060` §15 |
| item 139 | reviewer, `TASK_PHP_061` §3.4 |
| item 146 · 147 | engineer, `_062` §8.2 |

**Manager-opened: 9 of 17, not 8.** Of the eight *findings*, only **4** are the
manager's. **Command:** the RULE-9 cells are `RECAP_PHP.md:2192-2199`; the nine
item rows and their provenance clauses are printed by
**`python3 .temp/php63/s0_scope_and_axes.py`** (part 1). No count in this report
is asserted without one.

⭐ **No research consequence** — it does not change what is owed on any object.
I record it only because the brief warns in terms that *"a count in prose about a
structure rots exactly like one inside it"* and then carries one. **It is the
tenth round and the law held on the brief that cites it.**

---

## §1 — ITEM 135, THE `_INDEP` RATCHET

> **VERDICT — CONCLUSION: ⚠ UPHELD-AS-ARITHMETIC. REASON / IMPLIED INFERENCE:
> ⛔⛔ REFUTED, AND INVERTED. The routed question answers *"steady state, leave
> it"* — but ON NEW GROUND, and the ground is the opposite of the item's.**

### 1.1 What the item asserts, and what reproduces

The item's arithmetic half: *"the adjective class is the single largest entry
class in that ratchet, and every one of them is an adjective."*

**EVENT, `bcee07c`** — `python3 .tasks-php/contract_audit.py` (rc 0, `✅ no
problems`, `N8 RATCHET VERDICT hits 13; unfiled 0; stale adjudications 0; ⭐ REAL 3`).
Classifying the 13 `ADJUDICATED` rows by the *reason text* the adjudicator wrote:

| class | rows | verdict |
|---|---|---|
| adjective/adverb describing **data**, checkable from the file | **5** (`ph29:23`, `(SHARED)/emalloc_shim.h:640`, `ph97 kernel.c:323`, `ph97 kernel_hardened.c:356`, `ph96 kernel.h:112`) | FALSE-POSITIVE |
| POINTER-verb (`proves`/`shows` pointing at where an argument lives) | 3 (`ph55` `:473`, `:496`, `:326`) | FALSE-POSITIVE |
| plural noun `labels` | 1 (`ph03:38`) | FALSE-POSITIVE |
| `diff proves it` (deterministic op over digested files) | 1 (`ph07:134`) | FALSE-POSITIVE |
| states another artefact's VERDICT | **3** (`ph53:8`, `ph53:9`, `ph55:9`) | REAL |

✅ **The adjective class IS the largest single class (5 rows / 4 distinct
sentences).** The item's count holds. ⓘ The brief renders it as *"its four
hits"*, which collapses `ph97`'s two rows; the item's own wording (*"entry
class"*) is the accurate one.

### 1.2 ⛔⛔ THE ITEM'S DISCRIMINATOR IS EITHER CIRCULAR OR ALREADY ANSWERED AGAINST IT — AND *"ONE GREP"* CANNOT RUN EITHER READING

The item names its own cheap test: *"ask whether any TRUE positive has ever been
filed in this class."* **That sentence has two readings and they give opposite
answers.**

**Reading (A) — *"this class"* = the adjective class.** **VACUOUS.** The class is
*defined by its adjudication reason*: a row is in it precisely because the
adjudicator wrote *"`independent` describes a byte of this record … checkable
FROM THIS FILE … not a corroboration between two artefacts."* Asking whether a
FALSE-POSITIVE-by-definition class contains a true positive is asking whether a
set defined by a predicate violates it. **It can only ever return "no", and its
"no" carries no information about the regex.**

**Reading (B) — *"this class"* = the hits the `_INDEP` **arm** produces.**
**ANSWERABLE, AND THE ANSWER IS *YES, TWICE*.**

⛔ **`_INDEP` IS NOT CO-EXTENSIVE WITH THE ADJECTIVE CLASS, AND THE ITEM, THE
`ph96` ADJUDICATION COMMENT AND THE BRIEF ALL READ AS THOUGH IT WERE.**
`contract_audit.py:229-238` — a line is `VERDICT` if `_INDEP.search(line)` **OR**
(`_TOOL` **and** `_VERDICT_VERB`). The two arms are independent, and **no column
of the `ADJUDICATED` table records which one fired.** So no grep over the table
can answer reading (B); you have to re-evaluate the predicate against the source.

**EVENT, `bcee07c`** — `python3 .temp/php63/s1_indep_class.py`, which imports the
live `contract_audit.py` and re-runs `_INDEP` / `_TOOL` / `_VERDICT_VERB` against
the actual source line named by every `ADJUDICATED` key:

```
entries in ADJUDICATED         : 13
caught by the _INDEP arm       : 7
  ...of which REAL             : 2
REAL entries overall           : 3
```

| arm | hits | REAL | true-positive rate |
|---|---|---|---|
| **`_INDEP`** | **7** | **2** (`ph53 kernel_hardened.c:9`, `ph55 kernel_hardened.c:9`) | **2/7 = 29 %** |
| `_TOOL` + `_VERDICT_VERB` | 6 | 1 (`ph53 kernel_hardened.c:8`) | 1/6 = 17 % |

⭐⭐⭐ **THE ARM THE ITEM SUSPECTS OF BEING *"AIMED ONE CONCEPT OFF"* IS THE MORE
PRODUCTIVE OF THE TWO ARMS, AND IT CAUGHT `F98`'S OWN FOUNDING INSTANCE.** The
two REAL `_INDEP` hits, read from the files:

- `ph53-iface-tail-uninit/c/kernel_hardened.c:9` — *"…`preimage_screen.py` labels it
  `NOT-THE-REPAIR` **independently**."* This is `independently` as an **adverb of
  corroboration between two artefacts** — the exact target concept — and it is
  `F98`'s own instance, frozen at re-measure price.
- `ph55-opdata-stride/c/kernel_hardened.c:9` — *"…the three **independent** legs that
  identify WHICH exit the hunk belongs to — `preimage_screen.py`'s own verdict is
  `CANDIDATE` and is NOT one of them."* ⚠ Note the mechanism: the adjudicated
  *reason* is about the **next line** (`:10`, the stated verdict), but `:10`
  matches **no arm** — `is` is not in `_VERDICT_VERB`. **The hit exists only
  because `_INDEP` fired on `independent legs` one line up.**

### 1.3 ⭐⭐⭐ AND THE ADJECTIVE CLASS HAS ALREADY PRODUCED A TRUE POSITIVE THE TABLE CANNOT SHOW — `ph97`

`contract_audit.py:173-179`, the adjudicator's own prose above the `ph97` entry:

> *"⚠ THE ROW'S FIRST HIT WAS REAL AND WAS REPAIRED BEFORE MEASURING … The
> comment as first written ended "A kernel that derived one from the other would
> have deleted the mechanism" — a VERDICT on a design argument … It was moved to
> `NOTES.md` §14 (gate-only) and the `c/*` comment now POINTS at it."*

**Verified as landed, not just claimed** (`bcee07c`):
`patterns-php/ph97-optarg-unwritten/NOTES.md:840` is `## §14 ⭐⭐ WHY THE TWO BYTES
MUST BE INDEPENDENT`, `:850` carries the moved sentence, and
`c/kernel.c:328-329` now reads *"…is argued in ../spec.md … and ../NOTES.md §14 —
this comment points at the argument and does not state its verdict."*

⛔⛔ **NOW THE PART THAT DECIDES THE ITEM.** I re-ran `_classify` on the moved
sentence:

```
python3 -c "... ca._classify(' * A kernel that derived one from the other would have deleted the mechanism')"
  -> None
```

**NO ARM OF THE CLASSIFIER SEES THE REAL DEFECT.** No tool name, no `_INDEP`
word. The only reason a human ever read that comment is that `_INDEP` fired,
**on the adjective, two lines up**.

> ▶ **So the largest "false-positive" class is the arm's single most valuable
> behaviour to date: on `ph97` an adjective hit surfaced a true `F98`-shaped
> defect that the predicate was structurally blind to, and it was repaired
> BEFORE the 32-cell measurement froze it.** On `ph55` the same thing happened
> one line apart and the REAL verdict *was* filed.

### 1.4 ⚠ WHAT MY MEASUREMENT COULD NOT SEE — say it rather than report a number (`§9` trap 2)

1. **Hits repaired before the row was committed are invisible to every method
   available to me.** `ph97`'s is known **only because the adjudicator wrote it
   down in prose**. I looked for others in history —
   **EVENT, `bcee07c`**: `git log -p --unified=0 -- 'patterns-php/*/c/*.c'
   'patterns-php/*/c/*.h' | grep -aE '^-' | grep -aiE 'independent|confirmed
   by|corroborat|both routes'` → **zero removed lines.** That is consistent with
   *"pre-commit repairs leave no trace in history"* and equally consistent with
   *"there were none"*; **the two are not distinguishable from this tree.** So
   the true-positive count for `_INDEP` is `2` **filed** and `≥ 3` **actual**,
   with no upper bound derivable.
2. **My method is exact for the `ADJUDICATED` population and says nothing about
   comments that never fired at all** (`F98`-shaped claims spelled with neither a
   tool name nor an `_INDEP` word). `ph97`'s moved sentence is a *worked example*
   that this population is non-empty. **I did not size it** — that would be a
   read of every comment in `patterns-php/*/c/*`, not a grep, and I judged it out
   of scope for this round. It is in `§ ORDER TO RESUME IN`.
3. `(SHARED)/emalloc_shim.h:640` is one physical line counted once across all
   rows by design (`item98`'s dedup). **It is one sentence, not thirteen**, and
   any future rate over rows must not re-multiply it.

### 1.5 ▶ THE RULING, AND WHAT WOULD CHANGE MY MIND

**RULING: steady state — leave the regex alone.** ✅ Both of the item's binding
constraints are respected: **no regex change is proposed**, and **no prose is
reworded to dodge the grep.**

⛔ **But NOT for the item's reason.** The item offers *"the false-positive
direction is the safe one"* — a tolerance argument. The measured ground is
stronger and different: **the `_INDEP` arm has the higher true-positive rate of
the two arms (2/7 vs 1/6), and its worst-looking class is the one that has
already bought a pre-measurement repair the classifier could not have found.**
**A predicate is not *"aimed one concept off"* when its off-concept hits are
what put a human in front of the on-concept defect.**

**What would change my mind, stated so the next round can just run it:**

- **the discriminating number is the `_INDEP` arm's REAL count, not the adjective
  class's size.** If the next **five** adjudications add **≥ 3** adjective
  FALSE-POSITIVEs and **0** REALs to the `_INDEP` arm — taking it to ≤ 2/10 = 20 %,
  below the `_TOOL` arm's current 17 %±, and with no further "repaired before
  measuring" note in the table — then the tolerance argument has run out and the
  predicate is worth re-opening. **Until then the arm is paying for itself.**
- ⚠ **`n` is small and I am saying so.** 7 hits, 2 REAL, from 13 rows over ~13
  rows of corpus and largely one author. This is a ratio over single digits and
  I am not dressing it as a rate.

### 1.6 ▶ ONE PROPOSAL, AND IT IS NOT A REGEX CHANGE (manager's call, NOT APPLIED)

**The item could not be answered from the table because the table does not record
which arm fired.** That is a *reporting* gap, not a predicate gap — precisely the
distinction `F138` landed (*"I called the tool's function" is not "I ran the
tool"*) and `F132` landed (*a count is a valid tripwire and an invalid
adjudication*).

▶ **Proposal:** `contract_audit.py`'s `item98` reporter prints the firing arm
(`INDEP` / `TOOL+VERB`) beside each hit, and `N8` additionally prints
`REAL by arm`. **This tunes nothing** — it changes no predicate and can change no
verdict; it makes reading (B) of the item's own discriminator a one-command
question instead of a bespoke probe.
⛔ **NOT APPLIED.** §H: a validator change lands with its must-fire negatives, and
the brief forbids me touching this file on this item. The must-fire negatives it
would need, if the manager takes it: **(i)** `ph53:9` reports `INDEP` and
`ph53:8` reports `TOOL+VERB` (**the two arms on adjacent lines of one sentence** —
a single-arm bug cannot pass both); **(ii)** `REAL by arm` prints `INDEP=2,
TOOL+VERB=1` and the two sum to `N8`'s `REAL 3` (**cardinality tied to
membership**, `F142`).

⭐ **Generator kept** (`CLAUDE.md` rule 1): `.temp/php63/s1_indep_class.py`,
~40 lines, imports the live module, reads only committed files, writes nothing.
⚠ **It is itself an instance of item 145 / §7.2 and I say so there rather than
pretend otherwise.**

---

## §2 — `F145` AND `F143`, THE TWO ROW-13 FINDINGS THAT WOULD ENTER `.memory-php/02-ladder.md`

### 2.1 `F145` — *"`R5` cannot BOTH compute `R1`–`R4`'s function AND refuse the defect"*

> **VERDICT — CONCLUSION: ⚠ UPHELD FOR ONE WORD AND ⛔⛔ REFUTED FOR THE OTHER,
> AND THE FINDING CHANGES THE WORD BETWEEN ITS TITLE AND ITS CONSEQUENCE.
> REASON: ⛔⛔ REFUTED — the block is SOUNDNESS, not the cross-rung checksum,
> and the checksum does no work in the argument at all.**
> ▶ **The finding shrinks from *a constraint of the ladder* to *a property of
> `ensures`*, which is exactly the outcome the brief named.**

#### 2.1.1 The question the brief asked, answered with Verus rather than with an opinion

> ⭐⭐⭐ *Could a spec function carry the defect for the CHECKSUM while a
> SEPARATE `ensures` clause refuses it?*

**EVENT, `bcee07c`, 2026-09-16 — `python3 .temp/php63/s2_witness.py`** (two Verus
runs, ~1 min, the cost `controls/key_identity.py`'s own `pin` quotes):

```
  PASS  W1  predicate=shipped   -> VERIFIES   [4 verified, 0 errors]   [want VERIFIES]
  PASS  W2  predicate=hardened  -> FAILS (postcondition)   [3 verified, 1 errors]   [want FAILS]
SELFTEST PASS
```

`W1` is the shipped `zend_hash.c:463-465` predicate — **the defect, unmodified,
byte-for-byte the `PRED_SHIPPED` string from `controls/key_identity.py:71-72`** —
carrying this **verified theorem** in the same file:

```rust
pub open spec fn w() -> Seq<Node> { seq![Node { h: 7, nkl: 0, k: 0, nxt: NIL }] }

pub proof fn defect_witness()
    ensures
        find(w(), 0, 7, 4, 99, 1) != NIL,                       // a bucket IS selected
        w()[find(w(), 0, 7, 4, 99, 1) as int].nkl != 4,         // …and its key KIND is not the one asked for
{ ... }
```

That is `NEW:container-key-identity` **refuted, as a theorem**, against the
defective predicate — and it **verifies**. `W2` is the must-fire negative: the
same theorem against `b73349dbe4e9`'s hardened predicate **fails on the
postcondition** (the hardened walk returns `NIL` for this witness), so `W1` is
attributable to the **predicate** and not to the shape of the file — the same
three-arm discipline `key_identity.py` uses, and for the same reason.

⭐ **Note the run caught its own instrument**: `W2`'s first attempt failed with
`unexpected closing delimiter` and my arm refused to score it, because it
requires a **postcondition** failure. That is `key_identity.py`'s `N2` design
working in a second file — *"a syntax or type error would pass a naive 'did it
fail?' test while measuring nothing."*

#### 2.1.2 ⛔ SO THE ANSWER IS *BOTH*, AND THE FINDING RIDES THE AMBIGUITY

| what "refuse" means | possible? | why |
|---|---|---|
| **REFUSE** = an `ensures` **on `kernel`** that the defect violates, so the artefact fails to build | ⛔ **NO** | **SOUNDNESS.** `kernel`'s exec code *is* the defective program. An `ensures` is a true statement about that code. *"The defect is absent"* is false of it. Verus is sound. **This holds whether or not a cross-rung checksum exists.** |
| **CATCH** = a verified statement, in the same file, that the defect **is** a defect | ✅ **YES, MEASURED** (`W1`) | The witness theorem quantifies over a `Seq<Node>` of its own; it touches nothing `kernel` computes and nothing `hash_fold` returns. `kernel` still returns the identical `u64`. |

⛔⛔ **F145's TITLE SAYS *"REFUSE"* AND ITS CONSEQUENCE CLAUSE SAYS *"CATCHING"*:**
*"the ladder's own cross-rung identity requirement is what stops the proof rung
from **catching** a logic bug."* **The tension holds for REFUSE and is FALSE for
CATCH, and the load-bearing word changes between the headline and the claim that
would enter the layer.** The clause that would enter `.memory-php/02-ladder.md`
is the **false** one.

#### 2.1.3 ⛔ AND THE STATED REASON — the cross-rung checksum — DOES NO WORK

The finding's mechanism: *"making `verus.rs` refuse would mean stating its
`ensures` against a correct delete … so `R5` would no longer compute the same
function as `R1`–`R4`, so the cross-rung checksum would be comparing two
different programs."*

⛔ **The checksum is downstream, not upstream.** The chain is:
**(1)** the ladder requires R5 to be a rung of *this* row, i.e. to implement R1's
function; **(2)** therefore R5's exec code carries the defect; **(3)** therefore
no true `ensures` of it denies the defect. **Step (3) follows from (2) by
soundness alone.** Delete the checksum from the project entirely and (3) is
unchanged. ▶ **The finding names the checksum because the checksum is where the
constraint is *visible*, not where it *lives*.**

⚠ **And the engineer's own cost note cuts against the finding**: *"nothing
resists at the Verus level — eleven tokens, one recursive proof, no lemmas."*
Measured here: the refutation is **~12 lines and 4 verified obligations.** ▶ **So
if the constraint were a design constraint it would be statable as such — and it
is not a design constraint. It is `ensures` doing what `ensures` does.**

#### 2.1.4 ⭐⭐ A SECOND, INDEPENDENT RESULT THE ROW SHOULD WANT: `N2` PROVES NON-PROVABILITY, `W1` PROVES FALSITY

`controls/key_identity.py`'s `N2` arm reports *"shipped predicate + the
obligation FAILS, postcondition"*. **That establishes that Verus could not
discharge the obligation. It does not establish that the obligation is FALSE.**
The two differ by SMT incompleteness, and `N3` (the vacuous control) rules out
*"Verus refuses this shape of file"* but not *"Verus could not find this proof"*.

▶ **`W1` closes that gap at ~12 lines**: it exhibits a concrete witness and
proves the property false. ⭐ **This is a strengthening of `ph66`'s R5 result, not
a criticism of it** — the row's `obligation_note` and `NOTES.md` §§6–7 rest on
`N2`, and `N2` is the weaker of the two available statements. ⛔ **NOT APPLIED**
(`patterns-php/` is out of my write scope and it would be a re-gate). It is a
proposal with a measured price: 2 Verus runs, ~1 minute, `.temp/php63/s2_witness.py`
is the generator.

#### 2.1.5 What survives, precisely

✅ **SURVIVES:** the shipped `verus.rs` verifies **with** the defect (49/0,
`results-php/gate/ph66-hashdel-uncompared.json`); an `ensures` on `kernel`
cannot be made to refuse it; and that fact **is** `_062`'s `P3` falsifier, which
is settled and needed no review.
⛔ **DOES NOT SURVIVE:** the generalisation to *the ladder*. The obstacle is a
property of postconditions, not of the ladder's identity requirement, and the
proof rung **can** carry a machine-checked refutation of the very defect it
computes. ▶ **The finding should be re-stated as a `ph66` row result plus one
general clause about `ensures`, not as a constraint of the ladder.**

⚠ **What I did NOT test:** whether the 1 647-line shipped `verus.rs` accepts the
witness theorem *in situ* (`rlimit`, the real `Node`/`G` types, `s_find_del`'s
extra `fuel` plumbing). I tested the **predicate**, in the same minimal harness
the row's own control uses. A drop-in is very likely and is not measured.

---

### 2.2 `F143` — *"the first row the whole safety stack is blind to"*

> **VERDICT — CONCLUSION: ✅ UPHELD, AND CORRECTLY SCOPED — it is about `ph66`,
> NOT about how `ph66` was ported. REASON: ⚠ UPHELD-BUT-INCOMPLETE — the leg
> that makes the scope correct is missing from the finding, and it is ALREADY IN
> THE TREE, gated, on 9 of 13 rows.**
> ⛔⛔ **AND `_060`'s `P2` — the precedent the brief asked me to weigh — IS
> REFUTED BY `ph96`'s OWN SHIPPED `model.py`.**

#### 2.2.1 ⛔ THE PREMISE OF THE WHOLE SUB-SECTION IS WRONG: THE COLUMN IS NOT UNCONSTRAINED

The brief: *"If the ladder's 'does the defect survive?' column takes its value
from a choice the protocol does not constrain, then the column needs a RULE
before this finding may enter the layer. Does it? Write the rule, or say why none
is possible."*

⭐⭐⭐ **IT IS CONSTRAINED, IN THREE PLACES, AND TWO OF THEM ARE GATED.**

**(a) `model.py` is the single declared point where the choice is made, and gate
stage 2 enforces every rung against it.** `harness/check.py:54-56`: *"every cell
prints the checksum the pattern's own `model.py` predicts"*, driven in an audit
-hook sandbox. `:79-86`, stage 4: *"`adversarial-*` behaviour is recorded per
rung and compared to the model's expected exit/stdout."* ▶ **A rung that
"deletes the bug" does not produce a different ladder cell — it FAILS THE GATE**,
unless `model.py` deletes it too, in which case R1 fails instead.

**(b) Both rows in question already DECLARE which algorithm they implement, in
`model.py`'s header.** Quoted verbatim:

| row | `model.py` declaration |
|---|---|
| `ph66` | *"`R2-R5` **`R1`'s function, not `R1h`'s.** The defect is a wrong boolean, not a memory error: safe Rust, `unsafe` Rust and Verus all express it exactly, and none of them has any reason to refuse it."* → *"THIS MODEL IMPLEMENTS `R1` = `R2` = `R3` = `R4` = `R5`, i.e. FIVE of the six rungs."* |
| `ph96` | *"`R2-R5` `R1h` **plus the `:385` guard at `:427`**, because `Option<&Zval>` cannot be released without being opened and the `None` arm has to go somewhere. **That is a FINDING about what the type forces and it is declared in `../spec.md`'s divergence ledger.**"* → *"THIS MODEL IMPLEMENTS `R2-R5`"* |

**(c) `.memory-php/02-ladder.md`'s FIRST bullet is already the rule's first
clause, and it is marked *"✅ Reviewed and upheld."*** —
*"⚠⚠⚠ **R2–R5 ARE NOT PORTS OF R1h.** … **a rung that panics is not a
translation of the C.** So the hardened C rung carries the historical fix, the
Rust rungs carry whatever is actually memory-safe, and only R1 diverges."*

#### 2.2.2 ⛔⛔ THEREFORE `_060`'s `P2` IS REFUTED, AND `ph96` IS THE THING THAT REFUTES IT

`_060` `TASK_PHP_060.md:307-313`: *"an R2 mirroring the C's control flow with
`.unwrap()` **panics**; one that handles `None` has **deleted the bug** — **both
are legitimate and they are different rows of the ladder's column**."*

⛔ **`ph96` did not treat it as a free choice and did not ship it as one.** Its
`model.py` says the divergence is **forced** — *"because `Option<&Zval>` cannot
be released without being opened and the `None` arm has to go somewhere"* — and
files it in `spec.md`'s **divergence ledger** as *"a FINDING about what the type
forces."* ⛔ **And the `.unwrap()` alternative is excluded by the layer's own
reviewed clause (c): a rung that panics is not a translation of the C.**

> ▶ **So the degree of freedom `P2` asserts is EMPTY on both rows.** On `ph96`
> safe Rust **cannot** express the defect and the row says so; on `ph66` safe
> Rust **can** and does, and the row says that too. **Neither row chose; each
> measured what its type system left it and declared the result.**

#### 2.2.3 ▶ THE RULE — AND IT IS A PROMOTION OF PRACTICE, NOT AN INVENTION

**⭐ RULE (proposed for `.memory-php/02-ladder.md`; NOT APPLIED — manager-only).**

> **THE LADDER'S *"does the defect survive?"* COLUMN IS READ OFF `model.py`, NOT
> OFF THE RUNGS.**
>
> 1. **`model.py` declares WHICH ALGORITHM it implements, naming the rungs it
>    covers** — `R1 = R2 = … = R5`, or a proper subset. *(Already practice: 9 of
>    13 rows do it; `ph96`'s header says it is doing something *"no earlier row
>    has had to say"*.)*
> 2. **Gate stage 2 then decides the column mechanically.** Every rung is checked
>    against `model.py`'s checksum; stage 4 checks adversarial behaviour. **A
>    rung that deletes the defect fails the gate; it does not quietly become a
>    different ladder cell.** *(Already enforced; costs nothing new.)*
> 3. ⭐⭐ **THE CLAUSE THAT IS NEW, AND IT IS THE ONLY LOAD-BEARING ONE:** where
>    `model.py` covers fewer than all five, **the row must state whether the
>    divergence is FORCED (the language cannot express R1's function) or CHOSEN**,
>    and a CHOSEN divergence is inadmissible — if a faithful safe rung exists,
>    it is the rung, and the idiomatic one ships beside it as a **mirror
>    control** (`02-ladder.md:284, 366, 647` — PAT's existing shape).
> 4. The FORCED case is not a defect of the row: **it is the ladder result.**
>    `ph96` is the worked instance and `ph66` is its negative.

**Why clause 3 is the whole rule:** without it, *"my `model.py` implements
`R2-R5` only"* is self-certifying and `P2`'s freedom comes straight back in
through the model file. With it, the freedom needs a **type-level reason**, and
a type-level reason is checkable by argument in the divergence ledger.

**⚠ HONEST PRICE, because a rule with an unpriced cost is how §A3a's obligation 5
got gated (`F141`):**
- clause 1 costs **nothing on 9 of 13 rows** and a header paragraph on the
  residue — **`ph45`, `ph52`, `ph53`, `ph56`** (**EVENT, `bcee07c`**:
  `grep -aln 'WHICH ALGORITHM\|IMPLEMENTS R' patterns-php/*/model.py` → 9 files;
  those four are the complement of the 13 built rows). ⛔ **Editing a `model.py`
  is a re-gate**, so this is *"required of new rows, back-filled never"*, not a
  repair order.
- clause 2 costs **nothing** — it is a statement of what the gate already does.
- clauses 3–4 cost **a sentence per row** and are **NOT machine-checkable**:
  `harness-php/provenance.py:65` lists `divergences` under
  **`✗ NOT CHECKED … all unvalidated declarations`**. ▶ **Say so in the rule.**
  A rule whose enforcement is *a reviewer reads the ledger* is still a rule; one
  that reads as gated when it is not is `F130`'s shape.

#### 2.2.4 What this does to `F143`

✅ **CONCLUSION UPHELD AND THE SCOPE SURVIVES.** `ph66`'s R2 is **not a porting
choice**: `controls/ladder.json` records `defective_rungs_agree_on: 8`,
`adversarial_separating: 4`, six rungs identical on every one of 8 inputs, only
`c-*-h` moving — and a HashMap-based R2 would have failed gate stage 2 against
`model.py`. ▶ ***"The safety stack is blind to this row" is about the row.***

⚠ **REASON UPHELD-BUT-INCOMPLETE.** `F143` states the measurement and leaves the
faithfulness worry standing; the engineer raised it honestly and then did not
close it. **It closes in the row's own `model.py` header and in gate stage 2.**
▶ **`F143` may enter `.memory-php/02-ladder.md` ONLY with the rule of §2.2.3 in
the same sentence**, because without clause 3 the headline is hostage to `P2`.

⚠ **`CLAUDE.md` rule 6 is respected and was never in tension here**: nothing in
this section refuses or shrinks the row. *"Safe Rust reproduces the bug
bit-identically"* is the finding, and clause 2 is what makes it a **measurement**
rather than an embarrassment.

---

## §3 — THE INSTRUMENT CLUSTER: `F144`, `F146`, ITEMS 137, 146, 147

⭐ **Verdicted as ONE question, per the brief and per `F131`.** The question —
*what is `A1` blind to, at what optimisation level, and what has the corpus
published on the strength of not knowing?* — turns out to have a single,
measurable answer, and I give it once here rather than five times below.

### 3.0 ⭐⭐⭐ THE ONE MEASUREMENT THAT SETTLES FOUR OF THE FIVE

**EVENT, `bcee07c`, 2026-09-16 — `python3 .temp/php63/s3_a1_deltas.py`,
`results-php/ph66-hashdel-uncompared.json` (committed measurement record) plus
`patterns-php/ph66-hashdel-uncompared/controls/inside_share.json` (committed
control).** `A1` = `kernel_exclusive_ir`; `n_iters` read from the record's own
`inputs` block (`small.bin` 20 000, `large.bin` 2 500). Statistic `A1`; base
`R1` per compiler; both C columns; mode `isolated`.

| compiler | opt | input | `A1(R1)` | `A1(R1h)` | **Δ `A1`/call** | provenance |
|---|---|---|---:|---:|---:|---|
| gcc | O0 | small | 33 968 756 | 33 968 756 | **+0.0000** | committed record |
| gcc | O0 | large | 32 428 063 | 32 428 063 | **+0.0000** | `inside_share.json` (live callgrind) |
| gcc | **O3** | **small** | 63 889 858 | 63 825 037 | ⭐ **−3.2410** | committed record |
| gcc | **O3** | **large** | 57 761 576 | 57 715 540 | ⭐ **−18.4144** | committed record |
| clang | O0 | small | 29 972 607 | 29 972 607 | **+0.0000** | committed record |
| clang | O0 | large | 29 004 865 | 29 004 865 | **+0.0000** | `inside_share.json` (live callgrind) |
| clang | O3 | small | 57 549 819 | 57 549 819 | **+0.0000** | committed record |
| clang | O3 | large | 53 826 260 | 53 826 260 | **+0.0000** | committed record |

> ⭐⭐⭐ **`A1` RESOLVES THIS ROW'S REPAIR IN 2 OF THE 8 C (compiler × opt ×
> input) CELLS. SIX READ EXACTLY `+0.0000`.**

✅ **THE TWO PROVENANCES CROSS-CHECK WHERE THEY OVERLAP**, which is why I am
willing to use the live half: on the six cells both carry, the committed record
and the live callgrind agree to the fourth decimal (`−3.2410` vs `−3.2411`;
`−18.4144` vs `−18.4144`; four exact zeros). ⚠ **The two `O0/large` rows are
live-only and I label them as such** (item 147, and §10.7).

⛔ **`F144` NAMES TWO OF THE SIX AND FRAMES THE CAUSE AS *"a choice the COMPILER
makes."* At `O0` NEITHER compiler inlines, so BOTH columns go blind** — which
makes the primary lever the **optimisation level**, not the backend. ✅ **`_062`'s
own report has this** (`TASK_PHP_062_REPORT.md:173-176`: *"at `-O0` neither
compiler inlines … `c-gcc`/`c-gcc-h` report the same `33,968,756` Ir"*).
⛔⛔ **It did not survive into `F144`'s `RECAP_PHP.md` cell.** The finding as
filed is the `O3` slice of its own report.

---

### 3.1 `F144` — the `+0.0000` a 65 % share did not predict

> **VERDICT — CONCLUSION: ✅ UPHELD AND UNDER-STATED (2 of 8, not 2 of 4).
> ⛔⛔ NOVELTY CLAIM REFUTED — the mechanism was named, in the same words, in a
> committed row's `NOTES.md`, before `ph66` existed. REASON (*"`F125`'s cause is
> a person's choice, this one a compiler's"*): ⚠ SURVIVES BUT RE-GROUNDED —
> and the right comparator is not `F125`.**

#### (a) Is it new, or `F125` restated? — ⛔ **NEITHER. It is `ph55` §8b restated.**

`F144`'s cell asserts: *"⛔⛔ **THIS IS THE THIRD TIME A SHARE HAS BEEN ASKED TO
CERTIFY `A1` AND THE FIRST TIME THE MECHANISM HAS BEEN NAMED.**"*

⛔⛔⛔ **FALSE, AND THE COUNTER-INSTANCE IS COMMITTED, TITLED, AND IN THE SAME
WORDS.** `patterns-php/ph55-opdata-stride/NOTES.md:407` —

> **§8b. ⛔⛔ A1 IS BLIND TO THIS ROW'S OWN R1-vs-R1h COLUMN — and `inside_share`
> does not warn you** … *"an `inside_share` of **74–83 %** is high, and A1 is
> **still** blind here, because what matters is not how much of the cell A sees
> but whether **the DIFFERENCE** lands inside it. … **Do not read a high
> `inside_share` as a certificate.**"*

and `:371` §8a opens by quoting `.memory-php/03-numbers.md`: *"family A resolves a
code difference exactly to the extent the difference lands INSIDE the kernel
symbol."* ▶ **`ph55` §8b attributes the naming to `STATISTICS_001.md` §4, so
`F144`'s headline sentence has at least TWO prior homes and this is the THIRD.**
That is `F131`'s defect, filed inside the round that is policing it.

⚠ **`ph55`'s instance is also the PURER one**: byte-identical `kernel` symbols
under *both* compilers, A1 at **`0.000 %` on every cell and every input**,
because the defect site is reached through a function-pointer table and
**cannot** be inlined.

#### (b) So what IS new? — ⭐⭐ **THE TWO C COLUMNS DISAGREE ON IDENTICAL SOURCE**

| | `ph55` §8b | `F125` (`ph97` libc control) | ⭐ `ph66` / `F144` |
|---|---|---|---|
| where the difference lives | a callee reached by function pointer | another translation unit (libc) | a callee in the **same** TU |
| can the boundary be dissolved? | ⛔ **no** — indirect call | ⛔ **no** — separate TU | ✅ **yes, by inlining** |
| do the two C columns agree? | ✅ yes (both blind) | ✅ yes | ⛔⛔ **NO — gcc sighted, clang blind** |
| do the two opt levels agree? | (not measured) | (not measured) | ⛔⛔ **NO — `O3` sighted on gcc, `O0` blind on both** |

▶ **THE NEW CLAIM, AND IT IS STRONGER THAN THE ONE FILED:** where the boundary is
**dissolvable**, *"`A1` is blind to this row"* **is not a well-formed sentence.**
`A1`'s visibility is a property of the (**row × backend × `-O` level**) triple, and
on `ph66` it takes both values inside one row. ⭐ **That converts `F108`'s fifth
thing — *which compiler* — from a caveat about MAGNITUDE into a caveat about
VISIBILITY**, which is a different and larger claim.

⛔ **The finding's own stated distinction (*person's choice / compiler's choice*)
does not carry that**, and its corollary — *"a row cannot avoid it by writing its
kernel carefully"* — is ⚠ **true here for a reason the finding does not give**:
the row could in principle dissolve the boundary (`static inline`, or no helper
at all), but `patterns-php/` rows are tier `verbatim` **extractions of upstream
C**, so their function boundaries are inherited and not authored. ⭐⭐ **That makes
this failure mode structural to the PHP programme in a way it is not to PAT** —
and *that* is the layer-shaped clause, not *"the compiler chose."*

▶ **DISPOSITION:** ⛔ it does **not** belong inside `F125` (different boundary
class). ⛔ it does **not** belong beside `ph55` §8b as a first naming. ✅ **It
belongs as `ph55` §8b's THIRD instance, re-titled on the per-compiler /
per-level split, with `ph55` §8b cited in the same sentence.**

#### (c) ▶ DOES ANYTHING STILL REST ON THE SHARE? — **MEASURED: essentially NO, and the reason is direction**

**EVENT, `bcee07c`** —
`grep -rlan inside_share patterns-php/*/NOTES.md` → **10 of 13 rows** (residue
`ph07`, `ph53`, `ph64`), reproducing §0.1's population. Reading each use:

| direction | rows | does `F144` weaken it? |
|---|---|---|
| **REFUSAL** — a low or divergent share is a reason **NOT** to quote `A1` | `ph52` §8a (22.24 % → *"this row publishes in W1"*), `ph55` §8a (C 74–83 % vs Rust 96–99 % → cross-language in W1), `ph56` §12d (*"the difference does not land inside the symbol on the gcc cells, so the gcc column may NOT be quoted in A1"*), `ph45` §§3/624 (the condition **fails** and the row says so) | ✅ **NO.** `F144` says a HIGH share is not a certificate; it says nothing against a LOW share being a warning. **These are all sound.** |
| **CERTIFICATION** — a high or Δ-small share offered as reassurance that `A1` is safe | `ph29` §15e's three `PASS` rows (`c-gcc` vs `c-gcc-h` Δ `0.0003`/`0.0000` → PASS) | ⚠ **YES — and it is already inoculated twice over**: the same section carries `_059`'s ruling that *"the two conditions are **NOT A GATE**"*, and §15f *"withdraws this section's own strongest sentence."* |

> ⭐⭐ **SO THE CORPUS IS NOT CARRYING A CASUALTY.** Rows use the share to
> **refuse** `A1`, essentially never to **certify** it, and the one place it is
> used as reassurance already ships its own refutation. ▶ ***"Every use of the
> share as reassurance in the corpus is weaker than it reads"* is TRUE and
> VACUOUS — there is one such use and it is already withdrawn.**
> ⚠ **What I could NOT see:** `.memory-php/`, `RECAP_PHP.md` and the task reports
> were **not** swept for the certification direction; I scoped to the rows.

---

### 3.2 `F146` — ⛔⛔ THE CENSUS REPRODUCES AND THE CONSEQUENCE CLAUSE IS REFUTED BY `ph66` ITSELF

> **VERDICT — CONCLUSION (the census): ✅ UPHELD, reproduces to the digit.
> CONSEQUENCE CLAUSE (*"`_061`'s rule cannot be discharged from committed
> records"*): ⛔⛔ REFUTED. ▶ In the brief's own words: THE ⭐⭐⭐ IS UNEARNED.**

**EVENT, `bcee07c`** — I re-ran the census verbatim (law 12: the evidence is the
premise, so I am entitled not to believe it):

```
--- PAT 34 rows ---        --- PHP 14 rows ---
 ('O0','large.bin',False) 263   ('O0','large.bin',False) 111
 ('O0','small.bin',True ) 263   ('O0','small.bin',True ) 111
 ('O3','large.bin',True ) 263   ('O3','large.bin',True ) 111
 ('O3','small.bin',True ) 263   ('O3','small.bin',True ) 111
```

✅ **Exact.** `263 + 111 = 374`, absent on `O0/large` in **every** isolated cell
of **both** corpora; `O0/small`, `O3/small`, `O3/large` complete. The cause is
`harness/measure.py`'s `CG_PLAN`, one deliberate line, comment *"`large` is added
only at O3, where the perf claims live."* ⛔ **NO EDIT IS PROPOSED** (33
measurement records; `CLAUDE.md`).

#### ⛔⛔ BUT THE CENSUS IS OVER ONE RECORD FAMILY AND THE CLAIM IS ABOUT *"COMMITTED RECORDS"*

**EVENT, `bcee07c` — `python3 .temp/php63/s3_o0large_committed.py`**, which widens
the census from `results*/` to **every committed `controls/*.json` in both
corpora**:

```
A: the MEASUREMENT records (F146's population)
   O0/large isolated cells: present 0, absent 374
B: every committed controls/*.json with an O0 + large.bin A1
   patterns-php/ph66-hashdel-uncompared/controls/inside_share.json   8 O0/large cells with A1
   TOTAL committed control files carrying O0/large A1: 1
     c-gcc/O0     large.bin  A1=32428063   share_W=16.42 %   share_F74=None
     c-clang/O0   large.bin  A1=29004865   share_W=17.26 %   share_F74=None
     … 8 of 8 cells present
```

> ⭐⭐⭐ **`A1` AT `O0/large` IS IN A COMMITTED RECORD, AND THE RECORD IS
> `ph66`'s — THE ROW WHOSE `n/a` PRODUCED THIS FINDING.** The one row in either
> corpus whose committed artefacts carry the missing cell is the row the finding
> was written about.

⛔ **So the consequence clause is not merely over-stated; it is false of the very
tree it was measured on.** And the brief's own fallback — *"the instrument does
not supply it **for free**"* — is **also too strong**: `controls/inside_share.py`
is a committed, pinned, `--selftest`ed generator that supplies it, it ran as part
of `ph66`'s ordinary build, and its output is committed beside the row.

▶ **THE CORRECTED STATEMENT, WHICH IS ALL THAT SURVIVES:**
> *`harness/measure.py`'s `CG_PLAN` omits `O0/large`, so a row that wants the
> matrix at two optimisation levels gets it from a **row-level control**, not from
> the measurement record. `ph66`'s `controls/inside_share.py` is the model and is
> the only one so far.*

⭐⭐ **THAT IS A NOTE ON HOW TO OBEY THE RULE**, which is exactly the outcome the
brief said would unearn the ⭐⭐⭐. ⛔⛔ **And it is `F142`'s own moral fired on
`F146`**: a census that bounds ONE population, read as a property of ANOTHER.
`F142` says *"`N8` bounds the pile's SIZE and the property is its MEMBERSHIP"*;
here, *the census bounds `results*/` and the property is about `committed`.*
▶ **Two manager findings, filed the same day, and the second commits the first's
error. That is worth more than either finding.**

#### Second clause — is *"where the perf claims live"* obsolete? — ⚠ **NOT YET, AND THE QUESTION DISSOLVES**

Instances where an `O0` reading overturned an `O3` one: **(i)** `_061` §2.2,
`F136`'s headline, on `ph96`; **(ii)** `_062` §P4, `F144`, on `ph66`. **n = 2,
from 2 rows, both produced by the same instruction `_061` added.** ⚠ **Item 123's
rule binds: *three instances is a rate and one is not yet a design.*** I decline
to call it obsolescence. ⭐ **But the question dissolves anyway**: nothing about
`CG_PLAN` needs to change, because the row-level control already supplies the
cell. ▶ **The live question is not *"is `CG_PLAN` wrong?"* but *"should a
row-level two-level matrix be REQUIRED?"*** — and that is item 137, below, where
I rule on it.

---

### 3.3 Item 147 — the `n/a`, and the two provenances

> **VERDICT — the engineer's conjecture: ✅ CONFIRMED (and §3.2 is the scope).
> The provenance question: ✅ YES, IT IS A DEFECT WORTH A RULE — and the rule is
> one line, because the file already carries half of it.**

**Measured**: in `inside_share.json`, the `O0/large` cells carry
`A1` and `inside_share_W_pct` (**live callgrind over `build_root`**) and
`inside_share_F74: null` (**committed records**, and `CG_PLAN` never wrote the
input it needs). ▶ **So the blank falls on exactly the 8 cells `CG_PLAN` never
wrote, and it falls in ONE column of a row whose neighbouring column is
populated.**

⭐ **The file already names the provenance — `"build_root":
"/…/.temp/php-scratch/build/ph66"` — but as a SINGLE TOP-LEVEL KEY describing the
whole file, while only SOME columns come from it.** A reader sees
`A1 = 32 428 063` beside `share_F74 = n/a` and cannot tell that one was measured
today over a gitignored build and the other is arithmetic over a frozen record.

▶ **RULE (proposed, NOT APPLIED):** *a matrix whose columns have different
provenances labels the provenance **per column**, not per file.* ⭐ **This is
`F108` one level down** — `F108`'s five things include *which build*; this asks
which build **each column** came from. **Cost: one header line in the printer of
`controls/inside_share.py`.** ⚠ Editing that file is a control change, not a
re-gate of the C, but it is under `patterns-php/` and therefore not mine.

ⓘ **Dead code, confirmed and reported, not fixed** (§H):
`patterns-php/ph66-hashdel-uncompared/controls/inside_share.py:111-116` —

```python
for c in d.get("cells", []):
    if c.get("mode") != "isolated":
        continue
    pass                      # <- loop body is `pass`; the real loop follows
```

Harmless (no effect on any output). ⛔ **NOT FIXED under this round** — a
validator change lands with its must-fire negatives and this round is not where
that belongs.

---

### 3.4 Item 146 — is *"never QUOTE an `O0` figure"* becoming *"never MEASURE at `O0`"*?

> **VERDICT: ⛔ NO — AND THE ITEM ASKS ABOUT THE WRONG INSTRUMENT. Measuring is
> alive and did the work (`_062` measured both levels). What is dead is
> **SWEEPING**, and that is the gap.**
> ⚠⚠ **NOTHING BELOW IS A PROPOSAL TO PUBLISH `O0` MAGNITUDES.**

The chain, measured:
1. `.memory-php/03-numbers.md` forbids quoting an `O0` figure as a performance
   figure. ✅ Correct and untouched.
2. **EVENT, `bcee07c`** — `grep -an '^OPT' .tasks-php/php50_align_sweep.py` →
   `:86  OPT, MODE = "O3", "isolated"`. **Hard-coded. Nothing is ever swept at
   `O0`.**
3. `PROTOCOL_PHP.md` §B5 requires a figure to clear a sweep before publication.
4. ▶ **Therefore an `O0` reading can never clear §B5, therefore its SIGN can
   never be certified stable, therefore it cannot be published even as a sign.**

⭐⭐ **THAT IS THE REAL MECHANISM AND IT IS NOT THE ONE THE ITEM NAMES.** The
engineer did measure at `O0`, on both statistics, both compilers, both inputs —
`_062` §P4 and `NOTES.md` §9.4/§9.5. He then published **no sign**, and his
stated reason was the `03-numbers.md` prohibition. ⛔ **The prohibition is about
FIGURES. A sign is not a figure.** What actually stopped him is (2)+(3): there was
no swept `O0` number to publish a sign *of*.

▶ **WHAT A SWEEP IS FOR, which is the question the item asks:** a sweep
distinguishes *a difference between two programs* from *an artefact of code
placement*. That question is **as meaningful at `O0` as at `O3`** — arguably more,
since at `O0` the compiler is doing less to hide placement. **A sweep is not a
performance claim; it is a stability test.**

▶ **THE MINIMAL CHANGE (proposed, NOT APPLIED — a `.tasks-php/` script, so not
frozen):** give `php50_align_sweep.py` an `--opt` argument defaulting to `O3`,
and let a row publish an `O0` **SIGN**, explicitly labelled *a lowering reading,
not a performance figure*, **iff it has been swept.** ⛔ **Magnitudes stay
forbidden.** §H must-fire negatives it would need: **(i)** `--opt O3` reproduces
the current output byte-for-byte (the change is additive or it is a regression);
**(ii)** an `--opt O0` run on `ph66` returns the `+4.00`/`+6.12`/`+5.00`/`+9.69`
family-B figures `_062` §P4 measured, i.e. **the arm is tied to a number that
already exists** rather than to whatever it prints.

⚠ **I am NOT ruling that `ph66` should have published its `O0` sign.** Under the
rules as they stood, the engineer's conservatism was correct and I would not
overturn it. The finding is that **the rules leave no path to publishing a sign
at all**, and nobody had noticed because nobody had tried.

---

### 3.5 Item 137 — ⛔⛔ THE MANAGER'S ALREADY-GIVEN ANSWER IS OVERTURNED

> **VERDICT: ⛔⛔ THE ANSWER IS NOT (a), AND IT IS NOT (b). BOTH OPTIONS ARE ON
> THE WRONG AXIS. `ph96` did not fail the *publish-both-STATISTICS* rule in any
> way that would have caught its error — publishing both statistics at `O3`
> reads `+0.0000` in BOTH. It failed on the *LEVEL* axis, and only the level
> axis.**

The item, and the brief §3.5, rule **(a)**: *"a violation of a rule that says
ALWAYS … `_061` §2.2 refuted `F136`'s headline **precisely because `ph96`
published `A1` only**."*

⛔⛔ **THAT IS REFUTED BY `_061`'s OWN TABLE.**
**EVENT, `bcee07c` — `TASK_PHP_061_REPORT.md:292-295`**, `ph96`, `c-gcc` vs
`c-gcc-h` and `c-clang` vs `c-clang-h`, `small.bin`/`large.bin`, `isolated`:

| statistic | opt | gcc pair | clang pair |
|---|---|---|---|
| **A1** | `O3` | `+0.0000` / `+0.0000` | `+0.0000` / `+0.0000` |
| **A1** | `O0` | `+0.0000` / `+0.0000` | `+0.0000` / `+0.0000` |
| **W1** | `O3` | **`+0.0000` / `+0.0000`** | **`+0.0000` / `+0.0000`** |
| ⛔ **W1** | **`O0`** | **`−2.2419` / `−19.5768`** | **`−0.7397` / `−6.5296`** |

> ⭐⭐⭐ **THREE OF THE FOUR ROWS READ `+0.0000`. `ph96` COULD HAVE PUBLISHED
> BOTH STATISTICS, LABELLED, AT `O3`, IN FULL COMPLIANCE WITH THE RULE THE ITEM
> IS ABOUT — AND `F136`'s HEADLINE WOULD STILL HAVE BEEN WRONG.**

▶ **So the diligence question the brief poses — *"if diligence was not
sufficient, the rule cannot be 'be diligent'"* — has a sharper answer than
expected: `ph96`'s diligence was not insufficient, it was aimed at the wrong
axis.** Confirmed structurally: **EVENT, `bcee07c`** — `ph96`'s
`controls/inside_share.json` `cells` keys are `['c-clang','c-clang-h','c-gcc',
'c-gcc-h','safe_naive','safe_tuned','unsafe','verus']` — **no `/O0` or `/O3`
suffix, i.e. ONE optimisation level**, and its `NOTES.md` §9.5 says
`O3/isolated`. `ph66`'s are keyed `c-gcc/O3`, `c-gcc/O0`, … — **two levels, 32
triples.**

#### ▶ THE RULE THAT WOULD HAVE CAUGHT IT

> ⭐⭐⭐ **THE MATRIX IS FOUR-DIMENSIONAL — (statistic × compiler × input ×
> OPT) — AND A ROW OWES ALL FOUR AXES. Publish the one that RESOLVES; show the
> matrix that proves which; and the matrix is not shown until the `-O` axis is in
> it.**

- It is **exactly `_061`'s existing rule**, and I am not inventing one: `_061`
  added *"show the matrix at more than one optimisation level"* after `F136`
  fell. **My contribution is only that item 137's (a)/(b) framing cannot see it,
  because both options live on the statistic axis.**
- ✅ **It has already earned its cost on the first row built after it**: `ph66`
  obeyed it and it caught `F144` **immediately** (`_062` §6: *"More than one
  optimisation level, measured — and it is what caught my own error"*).
- ✅ **Checked against §3.2 as the brief requires**: a rule demanding an
  `O0/large` `A1` demands a cell no measurement record holds — **and `ph66`
  shipped it anyway**, in `controls/inside_share.json`, from the row-level
  control. ⛔ **So the cost objection is void**, and that is the whole reason
  §3.2 had to be verdicted before this one.
- ⚠ **The honest price**: one extra callgrind pass per cell in a row-level
  control. **Not a re-measure, not a re-gate, not a `harness/` edit.**

#### What survives of (b)

⚠ The item's own residue — *"publish the one that resolves may be right **per
cell**, but the cell a row resolves in is not the only cell it will be quoted
in"* — ✅ **SURVIVES AND IS THE CORRECT STATEMENT**, and the four-axis rule is
what operationalises it. ⓘ The residue framing is unchanged: `ph07`, `ph53`,
`ph64` ship **no matrix on any axis**, so they stay the residue under every
reading.

---

## §4 — `F141` AND ITEM 126: §A3a's FIFTH OBLIGATION

> **VERDICT — `F141` CONCLUSION (*the gate names the wrong predicate*): ✅
> UPHELD, and the protocol itself already concedes it is measured.
> `F141` SCOPE CLAIM (*"vacuous on 61.3 % of the temporal axis"*): ⛔⛔ REFUTED,
> on a ground the brief did not name — it is a POPULATION SUBSTITUTION, not a
> selection-bias question, and the selection question is untestable at `n = 2`.**
> **ITEM 126's TRADE: ⛔⛔ DISSOLVED — its cost premise is false by a factor of
> ~100, measured twice, and both measurements are already in the protocol file.**

### 4.1 What I am not re-litigating

`rebuild_hardened_php.sh --label ph66` giving `rc=0` on both images while the
adversarial observable flips `count=1 → count=2` and the benign one stays
identical is **measured**, and `PROTOCOL_PHP.md` §A3a obligation 5 now says so in
its own struck block: *"What the review settles is the SCOPE … **not whether the
gate named the wrong predicate** — that part is measured."* ✅ **Agreed and not
attacked.** The gate was stated on the **instrument** (a fault) where §A3's
criterion 2 is stated on the **question** (does the C exhibit the target error).

### 4.2 ⛔⛔ THE SCOPE CLAIM — IT IS NOT THE ATTACK THE BRIEF EXPECTED

The brief proposes: *"the 38.7 % is over CATALOGUED temporal ids, and rows are
SELECTED for buildability — so the built population may fault far more often."*
▶ **I tested that and it cannot be tested. A different and fatal objection came
out instead.**

#### (a) ⛔⛔ POPULATION SUBSTITUTION — the 38.7 % measures a DIFFERENT ARTEFACT

**EVENT, `bcee07c` — `TASK_PHP_057_REPORT.md:612-620`**, the derivation `F141`
cites, quoted exactly:

> *"Route 1 — **I executed them** (**one reproducer per catalogue row**, `-n`,
> oracle CLI)"* → temporal `31` rows run, `12` faulted, **38.7 %**.

⛔ **That is the rate at which THE CORPUS'S OWN REPRODUCER faults.** Obligation
5's gate is over **the row's own `▸ trigger`** — §A3a step 1, *"Run the trigger"*,
where §A3's `▸ trigger` is **a PHP snippet the row author writes.** Two different
artefacts:

| | the corpus reproducer | the row's `▸ trigger` |
|---|---|---|
| who made it | the corpus authors, years before this programme | **the row author, while building the row** |
| what it targets | the cited CVE/crash id | **the row's extracted idiom** |
| can it be chosen to fault? | ⛔ no — it is a given file | ✅ **yes — it is authored** |

⭐⭐⭐ **`ph66` IS THE PROOF THAT THEY COME APART.** Its corpus row is
`LOGIC-001`, whose `crashes_pristine_5_0_0` column reads **`n/a (non-crash
class)`** (`spec.md`'s `cwe_note`), and its `▸ trigger` is **hand-constructed** —
`unset($a["abc"])` against a live `$a[6385036779]`, generated by
`.tasks-php/probes/ph66_djbx33a_collide.py`, which the row's own `why` describes
as *"running DJBX33A FORWARDS … one line, no search."* ▶ **The row did not use
the reproducer, so the reproducer's fault rate says nothing about the row's
trigger.**

> ⛔ **So *"vacuous on 61.3 % of the temporal axis"* reads one population's rate
> onto another population's predicate.** ⭐⭐ **That is `F142`'s moral AND
> `F146`'s error, a third time in one round** (see §3.2) — and all three are the
> manager's, filed within one day.

#### (b) ⚠ THE SELECTION QUESTION IS UNTESTABLE — `n = 2`

**EVENT, `bcee07c` — `python3 .temp/php63/s0_scope_and_axes.py`** (part 2), which
parses the axis and status of every row out of `patterns-php/CATALOGUE.md`'s own
table and diffs it against the rows on disk: **102 rows parsed, axes
`spatial 42 · type 29 · temporal 31`**, reproducing the file's own header line;
**14 directories carry a `spec.md`**, of which `ph00-smoke` is the smoke row, so
**13 built rows**:

| built row | axis |
|---|---|
| `ph03` `ph07` `ph16` `ph29` | spatial (4) |
| `ph45` `ph52` `ph53` `ph55` `ph56` `ph96` `ph97` | type (7) |
| ⭐ **`ph64` `ph66`** | **temporal (2)** |

> ⛔⛔ **ONLY TWO TEMPORAL ROWS HAVE EVER BEEN BUILT, AND THEY SPLIT 1–1:**
> `ph64` records a fault (`F141`'s own list), `ph66` records none. ▶ **The
> built-vs-catalogued comparison the brief proposes has `n = 2` on one side. I
> decline to report a rate from it, and saying so is the answer** (§9 trap 2).

⭐ **INCIDENTAL DEFECT FOUND WHILE DOING THIS, CHEAP AND REAL — and the same
command prints it:**

```
  rows ON DISK (spec.md): 14  ph00 ph03 ph07 ph16 ph29 ph45 ph52 ph53 ph55 ph56 ph64 ph66 ph96 ph97
  catalogue says BUILT  :  6  ph03 ph07 ph16 ph29 ph45 ph64
  ⛔ STALE status rows   :  7  ph52 ph53 ph55 ph56 ph66 ph96 ph97
```

**`patterns-php/CATALOGUE.md`'s `status` column is STALE BY SEVEN ROWS** — `ph52`
`ph53` `ph55` `ph56` `ph66` `ph96` `ph97` all still read `catalogued` while every
one has a PASS gate record. ▶ **A `boxcheck.py` arm derives it in three lines** —
⛔ **not built by me**; §H, and it is not this round's object. **New open item
proposed.**

#### (c) ▶ *Is "it would have excused this row" a finding, or a prediction wearing a finding's clothes?*

> ✅ **IT IS A FINDING.** It is a **predicate evaluated on an actual row**: the
> old gate read *"if the row's trigger did not fault, this is vacuous and you
> skip it"*; `ph66`'s trigger returns `rc=0`; the predicate returns *skip*.
> **That is arithmetic over the text, not a forecast.** `n = 1` and `n = 1` is
> enough for an existence claim.

⛔⛔ **BUT `F141`'s HEADLINE IS BUILT ON THE PREDICTION, NOT ON THE FINDING.** The
title's load-bearing number is `61.3 %`, which §4.2(a) refutes; the durable
content is the `n = 1` existence proof plus the predicate argument. ▶ **Re-title
it on the `ph66` instance and the predicate, and delete the axis rate.** ⓘ The
finding already concedes the neighbouring version of this — it struck its own
*"all twelve built rows' triggers fault"* sentence — **and then kept a second,
larger uncomputed rate in the title.**

⚠ **A denominator note**: `F141`'s census reads **6 of 12**; with `ph66` the
population is **13** and the count is **6 of 13**. The classification is *"records
a fault marker in `NOTES.md`"*, which is **prose-based and not independently
reproducible** without the marker's spelling — I did not re-derive it and I am
not relying on it.

### 4.3 ITEM 126 — ⛔⛔ THE TRADE DOES NOT EXIST

The item states the trade: *"**REQUIRING** it makes every row pay for a **full
PHP compile**, and §A3a's entire merit is being cheap enough that nobody skips
it; **PERMITTING** it may mean nobody ever does it."*

⛔⛔ **THE COST PREMISE IS FALSE AND THE MEASUREMENT IS IN THE SAME FILE AS THE
RULE.** **EVENT, `bcee07c` — `PROTOCOL_PHP.md` §A3a obligation 5's own footnote:**
*"ⓘ Cost, measured **twice**: **30 s cold build + ~600 ms incremental, per
row.**"* And `.tasks-php/probes/rebuild_hardened_php.sh`'s header: *"`--dry-run`
… exists so the claim … is CHECKABLE IN A SECOND instead of by a **30-second
build** nobody will re-run."*

> ⭐⭐⭐ **A ROW DOES NOT PAY FOR A FULL PHP COMPILE. IT PAYS 30 SECONDS ONCE AND
> ~600 ms PER RE-RUN.** `F123` is exactly this defect one level up — *"the
> cheapest remaining check"* demoted to *"nice to have, skip it"* and then to
> *"I cannot"*, when it cost **30 seconds**. ▶ **With the cost at ~0 there is
> nothing to trade, and the item's framing is `F123` recurring inside the item
> `F123` opened.**

**Ruling on all three options, as the brief requires:**

| option | ruling |
|---|---|
| **PERMITTING** | ⛔ **REFUTED.** The item's own closing law — *a question routed to nobody in particular is one nobody answers* — is the same law, and `F123` is the worked instance. A permitted check with a 30-second cost is still not done, because nothing makes anyone look. |
| **REQUIRING** | ✅ **CORRECT, and its only objection is void.** The merit clause (*"cheap enough that nobody skips it"*) **argues FOR requiring**, once the cost is 30 s. |
| ⛔ **REQUIRED-BUT-GATED** | ⛔⛔ **THE WORST OF THE THREE, AND `F141` MEASURED WHY.** It exempts precisely the rows where the check is most informative — the ones whose target error is a **value** — because it keys on the instrument. **And it is worse than PERMITTING in one respect nobody has said**: a gated obligation *reads as required*, so nobody re-opens it. `F123`'s mechanism, with a rule in place of a memory. |

### 4.4 ▶ ON THE NEW WORDING — I AM OVERTURNING IT, AND THE PROTOCOL INVITES IT

The landed text: *"**REQUIRED WHENEVER THE ROW CAN NAME AN OBSERVABLE THE REPAIR
IS EXPECTED TO MOVE, WHICH IS EVERY ROW** — because a row that cannot name one
has no R1h claim to make."*

⚠⚠ **IT IS STILL A GATED OBLIGATION.** *"WHENEVER …"* is a condition; *"WHICH IS
EVERY ROW"* is a parenthetical assertion that the condition is always true.
⛔ **A reader who acts on the first clause and not the second re-derives exactly
the defect `F141` found** — and this programme has measured that failure mode
twice (`F134`/`F139`: a person-facing caution lost by 9h25m **to its own
author**).

▶ **PROPOSED WORDING (manager's to apply, NOT APPLIED by me):**

> ⭐⭐⭐ **RE-RUN THE TRIGGER AGAINST THE R1h POST-IMAGE BUILD. REQUIRED, WITH NO
> CONDITION.** Record the observable on BOTH images: **exit status AND output**.
> A row that cannot name an observable the repair should move has no R1h claim,
> and that is a finding to report, not a reason to skip step 5.

**Two words shorter, no conditional to mis-read, and it says the same thing.**
⛔ The reason-why stays in the rationale box where it cannot be read as a gate.

⭐⭐ **AND I AGREE WITH `F141` THAT THE WORDING IS NOT THE DELIVERABLE.** `_061`
§5.0's ruling — *the durable home for a trap is an arm that prints* — applies:
**the arm should print which built rows have discharged obligation 5 and which
have not**, and it should PRINT rather than gate (item 141). ⚠ **Check `F131`
first**: `boxcheck.py` already prints per-row state and is the natural host; a
new tool would be a second home. ⛔ **I did not build it** — it is a validator,
§H applies, and it is item 141's not mine.

---

## §5 — `F142` AND ITEM 144: THE COST LEDGER

⭐ **All cost figures below are a DATED EVENT and are HISTORICAL, not live:**
`python3 .tasks-php/task_cost.py` **at `bcee07c`, 2026-09-16** →
marginal **2.38**, searched-only **2.35**, first-in-family **2.22** (n=9),
follow-on **2.75** (n=4), **`PUBLISH THE RANGE: ~57 .. ~72, middle ~58`**.
⚠ The word *"live"* would undo the date; `RECAP_PHP.md`'s cell carrying these
same figures went stale **inside one session** (`F142`'s own history).

### 5.1 `F142`

> **VERDICT — THE ADMISSION (*"I charged `0.5/0.5` and did not measure it"*): ✅
> UPHELD, and it is honest. THE IMPLIED CONSEQUENCE (*"the per-row series is
> what moves"*): ⚠ UPHELD-BUT-IMMATERIAL — MEASURED, THE PUBLISHED MIDDLE DOES
> NOT MOVE AT ALL. THE GENERAL MORAL (*"`F132`'s class one level up"*): ⛔
> REFUTED — it is a SIBLING, not a super-case, and I can prove it.**

#### (a) ⭐ THE DEFENSIBLE SPLIT IS READABLE OFF THE TASK FILE'S OWN TITLE, AND NOBODY LOOKED

**EVENT, `bcee07c`** — `head -1 .tasks-php/TASK_PHP_040.md`:

> *"# TASK_PHP_040 — the R1h hunt for **`ph52` AND `ph53`**, and the build brief
> for **ROW 7**"*

`ROWS[6]` in `task_cost.py` is `ph53`. ▶ **THREE named deliverables; TWO of them
are `ph53`'s.** The defensible split is **`ph52` 1/3, `ph53` 2/3**, not
`0.5/0.5` — and it takes one `head -1`, not a judgement call.

#### (b) ⛔ BUT IT CHANGES NOTHING PUBLISHED — MEASURED ACROSS THE FULL EXTREME RANGE

**EVENT, `bcee07c` — `python3 .temp/php63/s5_split_sensitivity.py`**, which
re-imports `task_cost.py`, varies `CLASS["040"]` and re-runs the module's **own**
`report()` (not a reimplementation — `F138`'s lesson: *run the checker*):

| split | searched-marginal | first-in-family | follow-on | `ph52` | `ph53` | PUBLISH |
|---|---:|---:|---:|---:|---:|---|
| **0.50 / 0.50** (as classified) | 2.35 | 2.22 | 2.75 | 2.50 | 3.50 | `~57 .. ~72, middle ~58` |
| ⭐ **0.33 / 0.67** (the title's split) | 2.35 | 2.24 | 2.71 | 2.33 | 3.67 | **`~57 .. ~72, middle ~58`** |
| 0.67 / 0.33 | 2.35 | 2.20 | 2.79 | 2.67 | 3.33 | `~57 .. ~72, middle ~58` |
| 0.00 / 1.00 (impossible extreme) | 2.35 | 2.28 | 2.62 | 2.00 | 4.00 | `~58 .. ~72, middle ~58` |
| 1.00 / 0.00 (impossible extreme) | 2.35 | 2.17 | 2.88 | 3.00 | 3.00 | `~56 .. ~72, middle ~58` |

```
  marginal_searched    INVARIANT   2.35
  first_in_family      MOVES       2.17 .. 2.28
  follow_on            MOVES       2.62 .. 2.88
  PUBLISH              MOVES       low endpoint ~56 .. ~58;  MIDDLE ~58 INVARIANT
```

> ⭐⭐⭐ **THE MARGINAL IS INVARIANT BY ARITHMETIC — the split conserves the
> sum — AND THE PUBLISHED MIDDLE IS INVARIANT ACROSS AN ASSUMPTION RANGE THAT
> INCLUDES TWO PHYSICALLY IMPOSSIBLE ENDPOINTS.** At the *defensible* split
> (1/3 : 2/3) **every published figure is bit-identical.**

✅ **`F142`'s statement that the per-row series moves is TRUE** (`ph52` 2.50 →
2.33; `ph53` 3.50 → 3.67) **and the finding is right to flag the assumption.**
⛔ **What it does not say, and a reader will assume, is that anything published
depends on it. Nothing does.** ▶ **The finding should carry the sensitivity in
the same sentence as the admission**, or the admission reads as a live risk.

⚠ **`first_in_family` / `follow_on` DO move**, because `ph53` is `T3`'s opener
and `ph52` is its follow-on — **the one pair in the ledger where a split crosses
a group boundary.** Range over the full extremes: `2.22 ± 0.06`, i.e. **±2.5 %**.
✅ Worth one line in the finding; not worth a re-classification.

#### (c) ⛔ *"`N8` bounds the pile's SIZE and the property is its MEMBERSHIP" is `F132`'s class one level up"* — REFUTED

⭐⭐⭐ **THE DECISIVE TEST, AND IT IS ONE SENTENCE: `F132`'s OWN REMEDY WOULD NOT
HAVE CAUGHT `"040"`.** `F132`'s remedy is **diff the set**
(`cbaseline_diff.py`). Diff the `PENDING` set at any two commits across the ~20
tasks `"040"` sat stale and you get **no difference** — `{"040", …}` is identical
at both ends. **The set was stable; what had changed was a member's
CLASSIFICATION, in the world, not in the file.** ▶ **A defect invisible to the
proposed super-class's remedy is not an instance of it.**

**The three are SIBLINGS, and `F138` already drew the line `F142` crosses:**

| finding | the arm's assertion | the property trusted for | remedy |
|---|---|---|---|
| `F132` | a **count** | the **set**'s contents | **diff the set** |
| `F138` | (a bespoke caller's output) | what **the checker** reports | **run the checker** |
| ⭐ `F142` | a **cardinality bound** | a **member's classification staying true** | **bind the member to the fact** (`PENDING:ph66` + `N8b`) |

▶ **The family statement, which is what may enter `.memory-php/04-process.md`:**

> ⭐ *An arm asserts about one object and is trusted about another. Name both,
> and the remedy is decided by which pair you have: count/set → **diff the
> set**; caller/tool → **run the tool**; cardinality/member → **make the member
> carry the fact that can go stale**.*

⛔ **NOT *"`F132` one level up"*.** *"One level up"* asserts containment, the
containment is false, and the false half is the half that would enter the layer.
⭐ **The repair itself (`N8b`/`N8c`/`N8d`, re-deriving from the gated corpus every
run) is right and is not in question.**

---

### 5.2 Item 144 — ⭐⭐⭐ THE CENSUS COSTS ONE COMMAND, AND THE DIRECTION IS SIGNABLE

> **VERDICT: the manager's ruling (**KEEP `1.00`**) ✅ STANDS, for the reason
> given. The engineer's unease ✅ IS CORRECT AND IS BIGGER THAN ROW 13. ⛔ The
> item's *"biases the series in an UNKNOWN direction"* is REFUTED: the
> direction is STRICTLY DOWNWARD, provable without a census — and the census it
> asks for costs ONE COMMAND, which I ran.**

#### (a) The direction, and why it needs no census

**EVENT, `bcee07c` — `task_cost.py:391-401`:** `task_ids()` globs **only**
`TASK_PHP_<digits>.md`. Every ledger entry is therefore a real, written task
file. ▶ **There is no mechanism in the ledger that charges a row for work
nobody did.** The error is one-sided: **work performed and not counted.**

> **Therefore `charged ≤ performed`, therefore the marginal UNDERSTATES, therefore
> the published `~57 .. ~72` is a FLOOR and not an estimate.** ⭐ **The direction
> is an arithmetic property of the ledger's construction, not an empirical
> question.**

#### (b) The census, run — **12 documents, 3 of them row-attributable, naming 4 BUILT rows**

**EVENT, `bcee07c`** — `ls .tasks-php/*.md | grep -av TASK_PHP_` → **12
committed documents the ledger cannot see**, with their own title lines:

| document | ledger-invisible work is attributable to |
|---|---|
| `ADJUDICATION_001` · `002` · `003` · `004` · `FIXSURVEY_001` · `QUOTA_001` · `STATISTICS_001` · `PROTOCOL_PHP` · `README` | ONCE / METHOD — correctly not row-charged |
| ⭐ **`ROW13_001.md`** — *"scoping the thirteenth row, which must be TEMPORAL"* | **`ph66`** |
| ⭐ **`UPSTREAM_001.md`** — *"the upstream repair survey for the batch `ph21 · ph16 · ph12 · ph29`"* | **`ph16`, `ph29`** (+ 2 unbuilt) |
| ⭐ **`UPSTREAM_002.md`** — *"`ph07`'s R1h"* | **`ph07`** |

> ⛔⛔ **SO THE NON-UNIFORMITY IS NOT ROW 13's PECULIARITY — IT HAS AT LEAST FOUR
> INSTANCES AND THE ITEM NAMES ONE.** `ph07`'s R1h survey and `ph16`/`ph29`'s
> upstream batch are exactly `_040`'s shape (row-attributable scoping work) and
> exactly row 13's fate (charged nowhere), and the only difference is the
> filename prefix somebody chose.

⭐ **That is the item's own sentence, confirmed and widened**: *"which depends
only on whether a task file happened to be written for it"* → **corrected to
*"only on whether it was NAMED `TASK_PHP_*`."***

#### (c) The magnitude, bounded — and it is ALREADY INSIDE THE PUBLISHED BAND

⚠ **This paragraph contains an explicit ASSUMPTION and is not a measurement.**
Assume each of the three row-attributable documents is worth ~1 task-equivalent
(they are briefs of the same kind the ledger charges at 1.00). Distributing them
over the built rows they name adds roughly **+2.0 … +3.0** to a `ROW` sum of 31
over 13 rows: **marginal 2.38 → ~2.54 … ~2.61.**

⭐⭐ **`task_cost.py` ALREADY PUBLISHES A BAND THAT CONTAINS THAT**:

```
2.38  tasks/row   (as classified)
2.62  tasks/row   (+ the three corpus-wide METHOD tasks charged to rows)
2.92  tasks/row   (+ the catalogue construction charged to rows too)
```

▶ **So the defect is real, signed, bounded, and already covered by the
sensitivity block — it is simply not named as one of the band's causes.**
⛔ **The repair is therefore NOT a re-weighting** (which would break the series'
comparability, exactly as the manager ruled) **but a NAMED SENSITIVITY ROW**:

> *"+ the 3 row-attributable `ADJUDICATION`/`UPSTREAM`/`ROW13` documents the
> `TASK_PHP_*` glob cannot see — `ph07`, `ph16`, `ph29`, `ph66`."*

⭐ **And an `N`-arm is available and cheap**: assert that every `.tasks-php/*.md`
which is **not** `TASK_PHP_*` is either in an explicit `ONCE` allow-list or names
a row — so the next `ROW14_001.md` is visible the day it is written. ⛔ **NOT
BUILT** (§H: a validator lands with its must-fire negatives, and this is item
144's deliverable, not mine). **Its two must-fire negatives**: **(i)** removing
`ROW13_001` from the allow-list makes it FIRE; **(ii)** the arm lists the 3
current row-attributable documents **by name**, not by count (`F132`/`F142`).

⚠ **KEEP `1.00` FOR `ph66` — I am not overturning that.** The manager's reason
holds and my measurement strengthens it: **the defect is in the GLOB, not in the
weight**, and changing the weight would corrupt the series to compensate for a
missing input.

---

## §6 — `F139`, `F140` AND ITEM 125: WHERE A TRAP LIVES

### 6.1 `F139` — ⛔⛔ *"FOUR HOMES, FOUR FAILURES, THEREFORE LOCATION IS NOT THE VARIABLE"* IS REFUTED, AND THE POSITIVE CONTROL IS IN THE RULING'S OWN LAST PARAGRAPH

> **VERDICT — THE MEASUREMENT (the caution named the wrong build): ✅ SETTLED,
> not attacked. THE INFERENCE `_061` §5.0 HANGS ON IT: ⛔⛔ REFUTED. LOCATION
> **IS** THE VARIABLE — the axis is (**text a person must read**) vs (**an arm
> that runs and is invoked**), and all four instances are FOUR SAMPLES OF ONE
> CELL, not four different homes. ✅ THE RULING'S *ACTION* IS NEVERTHELESS RIGHT,
> and its own final paragraph is why.**

#### (a) The four "homes" are one home

`_061` §5.0's table:

| instance | "home" |
|---|---|
| `F132` | `RECAP_PHP.md`, a person-facing finding |
| `F133`/`F139` | `PROTOCOL_PHP.md` §A3a, **in capitals** |
| `F138` | `boxcheck.py`'s CLI output — *which nobody ran* |
| `F134` | `preimage_screen.py::same_function`'s docstring — *which nobody ran* |

⛔ **All four are TEXT THAT MUST BE READ.** Two are prose documents; the other
two are **outputs of tools that were not invoked**, which is text that must be
read with an extra step in front of it. ▶ ***Four observations at one point on
the axis do not establish that the axis is flat.***

#### (b) ⭐⭐⭐ THE POSITIVE CONTROL EXISTS, AND THE RULING CITES TWO OF ITS MEMBERS IN ITS OWN CLOSING PARAGRAPH

The brief: *"nobody has asked how many traps in these same four homes DID hold
… if that control is missing, the ruling is an argument from silence."*
▶ **It is not missing. It was never collected.** Instances where an arm **ran,
fired, and stopped a person** — every one from this programme's own record:

| # | instrument | what it caught | source |
|---|---|---|---|
| 1 | `cbaseline_check.py` bare run | *"failed loudly and **stopped the manager mid-edit**, which is the count working"* | `RECAP_PHP.md:190` (`F132`'s verdict) |
| 2 | `task_cost.py` `N1` | ⛔ **`F142` EXISTS BECAUSE THIS FIRED** — *"found because an unrelated arm (`N1`) fired"* | `RECAP_PHP.md:196` |
| 3 | `task_cost.py` `N1`, earlier | *"N1 CAUGHT THESE **SEVEN** UNCLASSIFIED, which is exactly what it is for"* | `task_cost.py:154` |
| 4 | `boxcheck.py` duplicate-key arm | *"printed `33 rows, 33 distinct, 0 duplicate keys`, so `_061` was **correctly scoped by the artefact this finding repaired**"* | `F131`'s RULE-9 verdict |
| 5 | `contract_audit.py` `_INDEP` | ⭐ **§1.3 of this report**: fired on `ph97`, a human read it, a REAL `F98`-shaped defect was found and moved **before the 32-cell measurement froze it** | `contract_audit.py:173-179` |
| 6 | item 100's backtick law | *"FIRED ON THIS ROW'S OWN DRAFT"*, and again *"THIS ONE FIRED ON THE SHIPPED RUNG"* | `RECAP_PHP.md:4911, 9127` |
| 7 | `width.py`'s textual guard | fired on the comment documenting the defect it was written to catch | `RECAP_PHP.md:9117` |
| 8 | `controls/key_identity.py`'s `N2` discipline | ⭐ **§2.1.1 of this report, TODAY**: my `W2` arm refused to score a run that failed on a **syntax error** instead of a postcondition | `key_identity.py:44-53` |

> ⭐⭐⭐ **EIGHT HOLDS IN THE "EXECUTED ARM" HOME AGAINST FOUR FAILURES IN THE
> "TEXT" HOME. THE COMPARISON IS NOT AN ARGUMENT FROM SILENCE; IT IS AN
> ARGUMENT THAT COUNTED ONE COLUMN.**

⛔⛔ **AND `_061` §5.0's OWN LAST PARAGRAPH IS THE REFUTATION**, which is why this
is a finding about the inference and not about the author:

> *"`F132` already has one (`cbaseline_diff.py`), `F131` already has one
> (`boxcheck.py`'s duplicate-key arm, **which I exercised in §0**), `F138`'s
> exists and **was not invoked**, and `F134`'s exists and **was bypassed**."*

▶ **Three of the four failures had an arm available and it was NOT RUN.** So the
outcome tracks **INVOCATION**, not location — and `F131`'s arm, the one that
*was* invoked, **held, live, in the same round.**

#### (c) The corrected ruling, and what it does to item 129

> ⭐ **CORRECTED:** *Location is the variable, on the axis (text a person must
> read) vs (an arm that runs and is invoked). The four failures are all text;
> the executed-arm column has at least eight holds and no measured failure.
> **A tool that is not invoked is text.***

✅ **The ruling's ACTION — *"the durable home for a trap is an arm in a tool that
prints"* — is CORRECT, and my corrected axis is its justification** rather than
*"location is not the variable"*, which would equally justify doing nothing.
⭐ **This is a CONCLUSION-UPHELD / REASON-REFUTED, and the reason was the load-
bearing half**: the ruling as stated implies no home is better, and then
recommends a specific home.

✅ **ITEM 129 STAYS CLOSED AS A BLOCKER, ON THE NEW GROUND.** The home question
is answered *more* decisively by the corrected axis than by the flat one, so a
~289-item frequency census is still not needed **for this purpose**. ⛔ **But
`_061`'s stated reason for closing it is gone, and the closure should be
re-recorded on the new ground** — otherwise the next round inherits *"location is
not the variable"*, which is false.

⚠ **`n` discipline, stated rather than assumed**: the eight holds are drawn from
this programme's own narrative and are therefore **selected for being written
down**. A hold that nobody recorded is invisible to me exactly as it was to
`_061`. ⛔ **The asymmetry cuts my way, not `_061`'s** — *failures* are what this
programme writes up; that the recorded set still contains eight holds is
evidence a fortiori.

---

### 6.2 `F140` — ⭐⭐⭐ I BACK-TESTED THE ARM AGAINST HISTORY, WHICH ITS AUTHOR DID NOT

> **VERDICT — THE MEASUREMENT: ✅ UPHELD AND UNDER-STATED (`_061` missed FOUR
> routed items, not one). THE CAUSAL CLAIM (*structural, not forgetfulness*):
> ✅ UPHELD, ON A NEW GROUND — and the brief's counter-evidence is REFUTED as a
> comparison of unlike populations. §0.0's ARM: ✅ **REPAIR, NOT THEATRE** —
> measured. ⛔ Its own account of the widening is FALSE in one word.**

#### (a) The back-test

**EVENT, `bcee07c` — `python3 .temp/php63/s6_router_backtest.py`.** It runs
`boxcheck.py`'s router regex — **both the current WIDE form and the EXACT
pre-widening form, recovered by `git show 3f8298e:.tasks-php/boxcheck.py`, not
reconstructed** — against `RECAP_PHP.md` as it stood at each round's dispatch
commit. Read-only git; no checkout.

| commit | round | WIDE arm would print | NARROW (the actual pre-widening arm) |
|---|---|---|---|
| `2c3b6e7` | `_057` dispatched | **2**: 125 126 | **2**: 125 126 |
| `c868e60` | `_059` dispatched | **2**: 125 126 | **2**: 125 126 |
| `46560f9` | `_060` dispatched | **2**: 125 126 | **2**: 125 126 |
| ⛔ `e9c5c4d` | **`_061` dispatched** | ⛔ **4**: 125 126 **135 137** | ⛔ **4**: 125 126 135 137 |
| `aec0b7f` | `_062` dispatched | **4**: 125 126 135 137 | **4**: 125 126 135 137 |
| `8c2a546` | the arm's own commit | **9**: 125 126 135 137 **139** **144** 145 146 147 | **7**: 125 126 135 137 145 146 147 |
| `bcee07c` | `_063` dispatched | **9** | **7** |

#### (b) ✅ THE MEASUREMENT HALF IS UNDER-STATED — `_061` MISSED FOUR, NOT ONE

`F140` is filed about **item 137**. ⛔ **At `_061`'s dispatch commit the arm
would have printed FOUR routed items — 125, 126, 135 and 137 — and `_061` scoped
one.** ▶ **The finding named the instance it happened to notice and understated
its own measurement by a factor of four.** ⭐ **And this round confirms it from
the other side**: 125, 126 and 135 are all in `_063`'s scope, two rounds later.

#### (c) ⛔ THE BRIEF'S COUNTER-EVIDENCE IS A POPULATION SUBSTITUTION

The attack offered: *"`_059` folded **four** items in and `_057` folded **two**,
so the manager demonstrably **can** remember."*

⛔ **Those numbers count *items folded into a round, of any routing*; the arm
counts *items routed to a reviewer*.** Measured: at `_059`'s dispatch **only two
routed items existed** (125, 126) — so *"`_059` folded four"* cannot be a recall
rate over this population at all. **The two series are over different sets.**
⚠ **Third population substitution in this round**, after `F146`'s (§3.2) and
`F141`'s (§4.2a).

▶ **THE RECALL RATE, OVER THE RIGHT POPULATION:**

| round | routed items LIVE at dispatch | scoped | recall |
|---|---:|---:|---|
| `_057` | **2** | **2** | ✅ **100 %** |
| `_061` | **4** | **1** | ⛔ **25 %** |
| `_063` | **9** | **9** (derived) | ✅ 100 %, **by the arm** |

⭐⭐⭐ **RECALL WAS PERFECT WHEN THE POPULATION WAS TWO AND FELL TO A QUARTER WHEN
IT DOUBLED.** ▶ **That is exactly what *"structural, not forgetfulness"* predicts,
and it is a better ground than the one `F140` gives**: the claim is not that a
derivation is metaphysically necessary, it is that **a memory-tracked list has a
recall rate that falls with its length, and this one has grown 2 → 9.**
✅ **CAUSAL CLAIM UPHELD, ON NEW GROUND.** ⛔ *"The manager demonstrably can
remember"* is true only of a two-item list.

#### (d) ▶ REPAIR OR THEATRE? — ⭐⭐ **REPAIR. MEASURED, AND BY A TEST ITS AUTHOR DID NOT RUN.**

**FOR (a) — the arm catches nine a human had not scoped:** ✅ confirmed, and
strengthened: **the arm in its ORIGINAL form would have printed 4 at `_061`.**
The instance `F140` is about **does not depend on the widening at all** — WIDE
and NARROW agree at every historical commit (2, 2, 2, 4, 4). ▶ **The arm is not
tuned to the instance that produced it; it reproduces the miss in the form it
had before the tuning.**

**AGAINST (b) — the author evaded it four times and it only caught them after
regex AND text changed:** ⛔ **THE ACCOUNT IS FALSE IN ITS LOAD-BEARING WORD.**
`boxcheck.py:142-147` says *"Items 144-147 were registered … and the arm matched
**NONE** of them."* **Measured: the pre-widening arm matches 145, 146 and 147 —
THREE of the four.** It misses **144** only (plus **139**, which the comment does
not mention). ▶ **The widening bought 2 items, not 4.**

⚠⚠ **THE ONE THING I CANNOT SEPARATE, AND I AM SAYING SO RATHER THAN REPORTING A
NUMBER** (§9 trap 2): the regex widening and the item re-wording **landed in a
single commit (`8c2a546`) with no intermediate state in git**, so
`NARROW × pre-rewording text` is **unmeasurable from this tree**. My `NARROW = 7`
is `NARROW × post-rewording text`. ⛔ **The brief's worry — *"fixing the text as
well as the regex may mean the arm still only catches what its author remembers
to spell"* — is therefore NOT fully answerable, and no amount of cleverness
makes it answerable.**

> ⭐⭐⭐ **AND THAT IS THE ROUND'S CHEAPEST LAYER-SHAPED CLAUSE, WHICH IS §H ONE
> STEP FURTHER:**
>
> *A validator change and the data change it is measured against MUST NOT land in
> one commit. §H requires must-fire negatives; a negative is only a negative if
> it can be evaluated against text the change did not touch. Land the arm, commit,
> then land the data.*
>
> ⛔ **Not in `.memory-php/` and I am proposing it, not applying it.** ⭐ Its cost
> is **one extra commit**, and its worked instance is this sub-section.

✅ **`rule9_mustfire.py`'s negatives are sound and I ran them** — **EVENT,
`bcee07c`**: `RULE-9 MUST-FIRE DEMONSTRATION: PASS`, 12 arms, including
*"counts a route that names a ROUND (904)"* and ⭐ *"an item with NO addressee is
invisible to the router (905) — **a KNOWN HOLE, asserted so it is not mistaken
for coverage**."* **That is `F128`'s Kind-A/Kind-B discipline done right**, and
it is the reason I call this a repair: the arm ships with its own hole stated.

---

### 6.3 Item 125 — ⭐⭐⭐ THE CENSUS IS DONE, AND ITS RESULT IS THAT `F123`'s REPAIR WAS A PROSE BOX AND THE PROSE BOX LOST

> **VERDICT — the census: ✅ RUN, at ITEM granularity, and the SET is below.
> The routed question (*"a count over the `§ WHAT I AM UNSURE OF` sections would
> answer it"*): ⛔ REFUTED AS SPECIFIED — a line-level grep misses `F123`'s own
> founding instance. The layer-shaped claim: ⚠ UPHELD IN SPIRIT AND REFUTED AS A
> REMEDY, and this round is the experiment.**

#### (a) ⛔ ADJUDICATING THE SET — three independent under-counts, each measured

**EVENT, `bcee07c` — `python3 .temp/php63/s6_unsure_census.py`:**

```
REPORT POPULATION: 67  (66 landed + this report)
  WIDE heading match HIT : 60
  WIDE heading match MISS:  7
```

✅ **66 landed reports reproduces §0.1.**

1. **HEADING.** Under a WIDE match (`UNSURE|UNCERTAIN|DID NOT DO|NOT DONE|WHAT I
   COULD|WHAT REMAINS|LEFT UNDONE|…`) there are **~56 distinct heading spellings**,
   not 12, and **7 reports match none at all**. ⛔ A fixed-heading grep
   under-counts; ⛔ a wide one over-matches (it catches `…incomplete about what
   REMAINS`). **Neither number is the set.**
2. **SECTION SCOPE.** Some reports carry the material under *"WHAT IS NOT IN THIS
   REPORT"* or *"WHAT I DID NOT REACH"* rather than *"UNSURE"*. Folded in.
3. ⭐⭐⭐ **LINE GRANULARITY — AND THIS IS THE ONE THAT DECIDES THE ITEM.** My
   first pass applied the two predicates *per line* and returned **14 members**
   — ⛔ **and `F123`'s OWN FOUNDING INSTANCE WAS NOT ONE OF THEM.**
   `TASK_PHP_051_REPORT.md` §8.1 reads
   `:440` *"…it is confirmed in the kernel, but **not on the real interpreter**.
   It is the cheapest remaining"* / `:441` *"check and it is not done."*
   **The claim straddles a line break, so no line-based grep can see both
   predicates.** ▶ ***A count over these sections, done the way the item
   specifies, returns a number that excludes the one member we know is a
   member.*** ⛔ **The 14 is neither a superset nor a subset of the truth.**

#### (b) ✅ THE CENSUS, RE-RUN AT ITEM GRANULARITY — AND IT FINDS ITS OWN FOUNDING INSTANCE

**EVENT, `bcee07c` — `python3 .temp/php63/s6_unsure_items.py`.** It parses each
report's uncertainty **sections** into **items** (numbered / bulleted) and
applies *cheap* ∧ *undone* to the whole item text:

```
reports scanned            : 66
uncertainty SECTIONS found : 80
ITEMS inside them          : 631
MEMBERS (cheap AND undone) : 27
```

✅ **`_051` §8.1 is member #16.** The method is validated against the one
ground-truth member that exists. **631 → 27 is a 23× reduction, and the members
are printed as a SET, never as a count** (`F132`).

⭐⭐ **THAT ALSO CORRECTS `_057` §7.1's COST ESTIMATE, WHICH IS WHY NOBODY RAN
IT.** That reviewer wrote: *"**Cost: ~1 h** — 57 task reports, a section-extractor
plus a hand read of each item, **because the judgement 'is this a cheap check
that was demoted?' is not greppable**."* ✅ **The judgement is not greppable and
that is right.** ⛔ **But the extractor is ~60 lines and the hand read is over
27 items, not 631** — so the true cost is the extractor (**done, ~10 min**) plus
a **~15 min** hand read. ▶ ***A cost estimate that priced the un-automatable half
against the un-reduced population is why "the single most valuable thing left"
sat for six rounds.*** ⓘ And the population has grown 57 → 66 while it sat.

#### (c) ⭐⭐⭐ THE TWO FULLY-TRACED CHAINS — AND THE SECOND ONE IS THIS ITEM

**CHAIN 1 — `F123`'s own, re-verified end to end from the tree:**

| step | text |
|---|---|
| `_051_REPORT.md` §8.1 | *"It is **the cheapest remaining check and it is not done**."* |
| `_052_REPORT.md` §7.3 | *"`_051` §8.1 asked for it and **I did not do it either — it was the optional extra** and §1–§4 took the depth."* |
| the protocol, two rounds later | treated as **impossible** |
| `F123` | **cost: 30 seconds** |

⭐ **DEMOTED, then re-discovered by accident.** ✅ `F123`'s conclusion reproduces.

**CHAIN 2 — ⛔⛔ ITEM 125's OWN CENSUS, AND IT IS A MEMBER OF THE CLASS IT
MEASURES:**

| step | text / measurement |
|---|---|
| `_057_REPORT.md` §7.1 | *"the count over landed reports' `WHAT I AM UNSURE OF` sections … **NOT DONE.** ⭐ **This is the single most valuable thing left** and the manager explicitly declined to scope it."* |
| `_058` · `_059` · `_061` task files | **EVENT, `bcee07c`**: `grep -aln 'cheapest remaining check' .tasks-php/TASK_PHP_*.md` → `_057`, `_058`, `_059`, `_061`, `_063`. In `_059` and `_061` it appears **only inside the standing warning box** (*"YOUR STATED PRIORITY BINDS THE MANAGER. `F123` IS WHY"*) — **the lesson was carried; the work was not scoped.** |
| `_063` | ✅ **scoped — because `boxcheck.py`'s router PRINTED item 125** |

> ⭐⭐⭐ **THE RESULT, AND IT IS THE ROUND'S CLEANEST SENTENCE:**
>
> ***`F123`'s repair was a warning box in every task file. THREE consecutive
> rounds carried the box, in capitals, and none of them did the work. `F140`'s
> PRINTING ARM scoped it on its first run. The text lost, the arm won, and the
> object they were fighting over was `F123`'s own item.***

⛔⛔ **THAT IS §6.1's CORRECTED AXIS, MEASURED ON `F123` ITSELF** — and it is the
ninth entry in §6.1(b)'s positive-control table, arriving while I wrote it.
✅ **It is also `F140`'s strongest evidence, and `F140` does not have it.**

#### (d) ▶ THE LAYER-SHAPED CLAIM — ⚠ UPHELD IN SPIRIT, ⛔ REFUTED AS A REMEDY

> *"An engineer's own uncertainty may be DEFERRED but not DOWNGRADED; the next
> task inherits its STATED priority, not the manager's."*

✅ **The PROHIBITION is right** — chain 1 is the harm, measured.
⛔ **But as a REMEDY it has been tried and it does not work.** It is a rule about
how a person should read text, it has been printed in capitals in the preamble of
`_059`, `_061` and `_063`, and **the item it was written about stayed undone
through all three.** ▶ **A rule that has been obeyed as a statement and ignored
as an instruction for three rounds should not enter the layer in that form.**

> ⭐ **WHAT I WOULD LAND INSTEAD** (manager's call; **NOT APPLIED**):
> *An engineer's stated uncertainty is DERIVED into a later round's scope by an
> arm that PRINTS it, or it is not carried at all. The prohibition on
> downgrading is the rule's content; **the arm is its enforcement**, and this
> programme has now measured, twice, that the prohibition without the arm does
> not survive three rounds.*

⭐ **The arm exists in draft**: `.temp/php63/s6_unsure_items.py`, 60 lines,
read-only, prints the SET. ▶ **Recommend promoting it to
`.tasks-php/probes/unsure_census.py` as an `ⓘ` PRINTING arm that cannot fail a
run**, exactly like `boxcheck.py`'s router. ⛔ **NOT PROMOTED BY ME** — §H: it
lands with its must-fire negatives. **The two it needs**: **(i)** `_051` §8.1 is
in the set (**the ground-truth positive — a line-granularity regression drops it
and the arm must catch that**); **(ii)** a synthetic item that is *cheap* but
*done* is NOT in the set. ⚠ **See §7.2 for why I left it in `.temp/` rather than
committing it, and why that is the honest answer rather than the convenient one.**

#### (e) ⚠ WHAT THIS CENSUS DID NOT DO

⛔ **I did not hand-adjudicate the other 25 members.** The census produces
*candidates*; deciding *"was this DEMOTED, or legitimately deferred?"* requires
reading the next task file for each — **~15 minutes, and it is the top of my
`§ ORDER TO RESUME IN`.** ▶ **So the item's headline question — *how many* — has
a measured **upper bound of 27** and **two confirmed members**, and I am not
reporting a number between those as if I had one.

---

## §7 — ITEMS 139 AND 145

### 7.1 Item 139 — ⭐⭐ THE WEAKENING IS REAL, IS NOT THE ONE STATED, AND THE CENSUS NEEDS A DIFFERENT FOURTH COLUMN

> **VERDICT — the engineer's weakening (*a `held` count may be counting sites
> that had no choice*): ⚠ UPHELD-NARROWED. It is TRUE, but it is not a general
> denominator problem; ⛔ its stated remedy (*a "did it FACE the choice?"
> column*) is the WRONG column, and the right one is already in `F133`'s own
> re-worded rule.**

#### (a) The brief's test, run on two of the seven

**EVENT, `bcee07c` — `python3 .tasks-php/probes/item139_sibling_census.py`**
(6 arms, 5 must-fire): `F133`(i) well-formed on **8 of 13**, holds on **7 of 8**.
▶ *"Pick two of the seven and ask whether either COULD have been written the
defective way."* I read the pristine source for two, from
`.temp/php11/_cache/php-5.0.0/` (the manifest-checked tree):

**`ph03` — ✅ YES, IT COULD.** `ext/standard/uuencode.c:78-85`:

```c
while ((s + 3) < e) {
    ee = s + len;
    if (ee > e) { ee = e; len = ee - s; if (len % 3) { ee = s + (int)(floor(len/3)*3); } }
```

**The clamp is an explicit optional conditional over the input end.** Deleting it
leaves a compiling, running function — **and `php_uudecode`, 46 lines below in
the same file, is that function.** ▶ ⭐⭐⭐ **FOR A GUARD-KIND REPAIR THE DEFECTIVE
SITE IS ITSELF THE EXISTENCE PROOF THAT THE CONSTRUCT CAN BE SPELLED WITHOUT THE
GUARD.** The sibling faced the choice.

**`ph64` — ⛔ NO, NO SIBLING FACED IT.** `ext/standard/basic_functions.c:157`
declares `int calling;` and `:2108-2109`/`:2135` maintain it:

```c
/* Prevent reentrant calls to the same user ticks function */
if (! tick_fe->calling) { tick_fe->calling = 1;  …  tick_fe->calling = 0; }
```

⛔ **The flag exists for REENTRANCY, in the call path.** The defect is in the
**delete's comparator**, and **no other site in the file is an instance of that
comparator.** The `held ✅ YES` here means *"the repair's ingredient was already
in the file"* — **not** *"a sibling chose the correct spelling."*

> ▶ **THE BRIEF'S DECISIVE TEST RETURNS 1–1.** *"If both could not, the finding's
> positive evidence is much thinner than it reads."* **One could and one could
> not**, so the evidence is **thinner than 7 of 8, and not empty.**

#### (b) ⭐⭐⭐ THE `held` COLUMN CONFLATES TWO RELATIONS, AND `F133`'s OWN RE-WORDED RULE ALREADY NAMES THEM

`_061` re-worded `F133` to *"**what was CHOSEN, not always what was
DISCOVERED**."* ⛔ **The census's `held` column counts both and the rule only
licenses one.**

| class | what it shows | rows (my classification, from the census's own `claim` column + the two source reads above) |
|---|---|---|
| **(A) CHOSEN** — a sibling site **instantiating the same construct** spelled it correctly | authorial choice — ✅ licences the rule | `ph03` · `ph07` · `ph56` (arms of one `switch`) · `ph96` (7 of 23 call sites) |
| **(B) DISCOVERED** — the repair's **ingredient** already existed, for another purpose | available material — ⛔ does **not** licence a rule about choice | ⛔ **`ph64`** (verified above) · ⚠ `ph55` borderline (*"the repair's own three lines are already in the file"* at another VM handler — a sibling exit path, so arguably (A)) |
| **(C) NEITHER** — the siblings are a **different construct** | not evidence at all | ⛔ **`ph66`** — *"`_zend_hash_add_or_update` takes `arKey`/`nKeyLength` and nothing else"* |

▶ **So `F133`(i)'s positive evidence is 4 clear + 1 borderline of 8 well-formed
rows, not 7 of 8.** ⚠ **This is MY classification, from the census's claim column
plus two source reads. It is a reading, not a measured column, and I say so.**

#### (c) ▶ THE FOURTH COLUMN — and it is CHECKABLE, unlike the one proposed

⛔ **The engineer's proposed column — *"did this site FACE the choice?"* — is not
decidable**: it asks about a counterfactual authorial state.
✅ **The decidable substitute is *"is the sibling an instance of the SAME
CONSTRUCT as the defective site?"***, and that is a **type/signature** question
the census can answer from the source — which is exactly how `ph66`'s own
weakening was established (*"takes `arKey`/`nKeyLength` and nothing else"*).

> ⭐ **PROPOSED (manager's call; NOT APPLIED — §H):** split
> `item139_sibling_census.py`'s `held` into **`same_construct?`** and
> **`chose_correctly?`**. **`held` = both.** ⛔ Do not add a *"faced the choice"*
> column — it cannot be filled from a repository.
> **§H negatives it would need**: **(i)** `ph66` reports `same_construct = NO`
> and therefore `held = --`, **not** `✅ YES` (the ground-truth negative, and it
> is the row that produced the weakening); **(ii)** `ph03` reports
> `same_construct = YES, chose_correctly = YES`.

⭐ **This does not weaken `F133`. It makes its headline survivable**: *"the
repair was already in the file"* is true on more rows than *"a sibling chose it"*,
and only the second supports the rule that was landed.

---

### 7.2 Item 145 — ⛔⛔ RULE ON THE TENSION: IT IS A FALSE DICHOTOMY, AND THE REAL EXPOSURE IS ~100× WHAT THE ITEM SCOPED

> **VERDICT — the tension: ⛔ DISSOLVED (the two rules govern different documents
> with different lifetimes, and the tree already implements the resolution
> twice). The item's SCOPE: ⛔⛔ REFUTED — it scoped one file in one round's
> scratch, and the measured exposure is 114 citations across the four permanent
> document families, INCLUDING THREE IN `.memory-php/` ITSELF.**

#### (a) The tension, ruled

`CLAUDE.md` rule 1: *the `.py` probe and the logs **ARE the evidence and
stay*** — in `.temp/`, gitignored. `F51`/`F99`: *a committed document may not
point at a deletable path.* The item: *"Both are followed here and they
disagree."*

⛔ **THEY DO NOT DISAGREE. THEY GOVERN DIFFERENT DOCUMENTS:**

| | **a WORKING generator** | **a LOAD-BEARING generator** |
|---|---|---|
| whose evidence is it? | **the round's** — a number that lives in a **dated report** | **a committed, UNDATED document's** — `spec.md`, `NOTES.md`, `PROTOCOL_PHP.md`, `.memory-php/`, `RECAP_PHP.md`, `CATALOGUE.md` |
| home | ✅ **`.temp/`. `CLAUDE.md` rule 1 governs.** A report is a dated narrative; naming the directory you worked in is accurate history | ✅ **promoted to `.tasks-php/` or `.tasks-php/probes/`. `F51`/`F99` governs** |
| why | the report is itself dated, so a dead path reads as history | the document claims to be true NOW, and a claim may not depend on a deletable file |

⭐⭐ **THE TREE ALREADY IMPLEMENTS THIS, TWICE, AND SAYS SO IN THE ARTEFACT:**
- `.tasks-php/probes/rebuild_hardened_php.sh`'s header: *"COMMITTED out of
  gitignored `.temp/` by the manager — **evidence for a protocol rule may not
  live in scratch** (F51/F99 …)."*
- `.tasks-php/width.py` — promoted out of `.temp/php39/width.py` for the same
  reason (`.memory-php/04-process.md:165` records the defect).
- `.tasks-php/STATISTICS_001.md` — *"committed. It was in gitignored `.temp/`"*,
  a banner in **all four** `.memory-php/` files.

▶ **So the rule is already practice; it has simply never been written down. The
discriminator is NOT *"is it reusable"* — it is *"does an undated committed
document depend on it?"***

#### (b) ⛔⛔ AND THE ITEM'S SCOPE IS WRONG BY TWO ORDERS OF MAGNITUDE

**EVENT, `bcee07c`** — `grep -ac '\.temp/'` over the four permanent families:

| document | `.temp/` citations |
|---|---|
| `RECAP_PHP.md` | **70** |
| `.tasks-php/PROTOCOL_PHP.md` | **21** |
| `patterns-php/CATALOGUE.md` | **13** |
| ⛔ **`.memory-php/` (all five files)** | **10** |
| | **114 total** |

▶ ***The item scoped `.temp/php66/clausetest.py` — ONE file, in ONE round's
scratch. The measured exposure is 114 citations in the documents that are
supposed to outlive every round.***

#### (c) ✅ HAND-ADJUDICATED — the layer's ten, one by one (`F132`: adjudicate the SET)

| citation | verdict |
|---|---|
| `00-corpus:16` · `01-extraction:16` · `03-numbers:16` · `04-process:16` — *"`.tasks-php/STATISTICS_001.md`, **committed**. It was in gitignored `.temp/`"* | ✅ **BENIGN — HISTORY.** This sentence *is* the promotion being recorded. **The rule working, four times.** |
| `04-process:210` · `:212` — the rule's own statement (*"30 `.temp/` citations in 11 committed `controls/*` files"*) | ✅ **BENIGN** — the rule quoting its own evidence base |
| `04-process:165` — *"`.temp/php39/width.py` — gitignored, and its `--selftest` no longer …"* | ✅ **BENIGN — HISTORY.** `width.py` **has been promoted**; `.tasks-php/width.py` exists |
| ⛔ **`02-ladder:447`** — `.temp/mgr172/NOTES.md` cited as the source of `F82`'s correction | ⛔ **LIVE DEPENDENCY** |
| ⛔ **`02-ladder:451`** — *"`.temp/mgr170/null_control.py` **asserted** …"* | ⛔ **LIVE DEPENDENCY** |
| ⛔ **`02-ladder:612`** — `.temp/mgr172/NOTES.md` again, for `F83–F87` | ⛔ **LIVE DEPENDENCY** |

> ⛔⛔ **THREE LIVE DEPENDENCIES IN THE AUTHORITATIVE LAYER, ALL IN
> `02-ladder.md`, ALL POINTING AT `.temp/mgr17*/` — the MANAGER's scratch.**
> ⚠ **`RECAP_PHP.md:115` records that this exact directory family has already
> lost state once** (*"THIS STATE WAS LIVING IN GITIGNORED `.temp/mgr175/NOTES.md`
> — which is **F99's own defect**, applied to the one piece of process state that
> governs what may enter the authoritative layer"*).

✅ **THE HARM IS LATENT, NOT REALISED — measured**: all five sampled paths
(`.temp/mgr172/NOTES.md`, `.temp/mgr170/null_control.py`, `.temp/php39/width.py`,
`.temp/mgr175/NOTES.md`, `.temp/mgr169/charlit_reach.py`) **still exist today.**
⛔ **They are one `rm` under `.temp/` away from not existing, and `CLAUDE.md`
rule 1 says `rm` there is auto-permitted.**

#### (d) ⛔ CHECK `F131` FIRST — is a tool already reporting this? **NO, and I checked before proposing**

`citecheck.py` covers **(i)** `spec.md`/`NOTES.md` citing `.temp/` (§F6, rc=1 at
HEAD on the long-standing debt) and **(ii)** its `§H AT RISK` arm, *a committed
VALIDATOR citing its NEGATIVES in `.temp/`* (8 live hits, `ph16`/`ph29`).
⛔ **Neither covers `RECAP_PHP.md`, `PROTOCOL_PHP.md`, `CATALOGUE.md` or
`.memory-php/`.** The item's own instinct — *"the right shape may be a WIDENING
of `citecheck.py`'s existing arm rather than a new one"* — ✅ **is correct**, and
the widening is **the file list**, not a new predicate.

> ⭐ **PROPOSED (NOT APPLIED — a validator, §H):** widen `citecheck.py`'s
> existing scan to the four permanent families and **report** (never gate) each
> `.temp/` citation, split **HISTORY** (the sentence says *was*, *gitignored*,
> *committed out of*) from **LIVE DEPENDENCY**. ⛔ **Do not gate**: 7 of the
> layer's 10 are benign history and gating would delete accurate history —
> `F130`'s and item 115's class, which this programme has now hit **eight** times.
> **§H negatives**: **(i)** `02-ladder:451` is reported LIVE; **(ii)**
> `04-process:16` is reported HISTORY — **the two classes on adjacent evidence,
> so a one-sided classifier cannot pass both.**

#### (e) ⚠ APPLYING MY OWN RULING TO MY OWN GENERATORS — because DoD 10 tells me not to create this round's next instance

Five generators, all in `.temp/php63/`, all **WORKING** generators under my own
rule — every number they produce is quoted **in this dated report and nowhere
else**, so `.temp/` is their correct home and no promotion is owed:

| generator | cited by |
|---|---|
| `s1_indep_class.py` | §1.2 only |
| `s2_witness.py` | §2.1 only |
| `s3_a1_deltas.py` · `s3_o0large_committed.py` | §3.0 / §3.2 only |
| `s5_split_sensitivity.py` | §5.1 only |
| `s6_router_backtest.py` · `s6_unsure_census.py` · `s6_cheapest_class.py` · `s6_unsure_items.py` | §6.2 / §6.3 only |
| `s0_scope_and_axes.py` | §0.1 / §4.2(b) only |

⭐⭐ **THE MOMENT ANY OF THEM IS CITED FROM `RECAP_PHP.md` OR `.memory-php/`, MY
OWN RULE PROMOTES IT.** ▶ **Three are candidates and I name them rather than
pre-empting the manager**: `s6_unsure_items.py` (§6.3's arm — the strongest case,
because item 125's answer depends on it), `s2_witness.py` (§2.1 — reusable across
every R5 row, the same property item 145 spotted in `.temp/php66/clausetest.py`),
and `s6_router_backtest.py` (the back-test `F140` needs). ⛔ **I promoted none: a
committed probe is a manager decision and `s6_unsure_items.py` would need §H
negatives.** ⚠ **Artefacts deleted, generators kept** (`CLAUDE.md` rule 1): the
only artefacts I produced are the two Verus source files under
`.temp/php63/verus/`, which `s2_witness.py` rewrites on every run.

---

## §8 THE VERDICT TABLE — CONCLUSION AND REASON SCORED SEPARATELY, IN THOSE WORDS

**All 17 objects reached.** `§` names where each is ruled — **one home per fact**
(`F131`), so nothing below is verdicted twice.

| object | whose | CONCLUSION | REASON | § |
|---|---|---|---|---|
| **item 135** — the `_INDEP` ratchet | engineer | ⚠ **UPHELD-AS-ARITHMETIC** (the adjective class is the largest, 5 rows / 4 sentences) | ⛔⛔ **REFUTED AND INVERTED.** The `_INDEP` **arm** has **7** hits, not 4, and **2 are REAL** — the higher TP rate of the two arms. The discriminator is circular on one reading and answered against the item on the other | §1 |
| **`F145`** — R5 cannot compute *and* refuse | engineer | ⚠ **UPHELD for *REFUSE*, ⛔⛔ REFUTED for *CATCH***, and the finding changes the word between its title and its layer-bound clause. **Measured in Verus: a defect-carrying spec + a verified refutation co-exist (4 verified, 0 errors)** | ⛔⛔ **REFUTED.** The block is **SOUNDNESS**, not the cross-rung checksum; delete the checksum and the block is unchanged | §2.1 |
| **`F143`** — the safety stack is blind | engineer | ✅ **UPHELD, and CORRECTLY SCOPED** — it is about `ph66`, not about the porting | ⚠ **UPHELD-BUT-INCOMPLETE.** The leg that makes the scope correct is `model.py`'s WHICH-ALGORITHM header + gate stage 2, already gated on 9 of 13 rows. ⛔ `_060`'s `P2` is **REFUTED by `ph96`'s own `model.py`** | §2.2 |
| **`F144`** — the `+0.0000` | engineer | ✅ **UPHELD AND UNDER-STATED** — `A1` is blind in **6 of 8** C cells, not 2 | ⛔⛔ **NOVELTY CLAIM REFUTED** — *"the FIRST time the mechanism has been named"* is false; `ph55` `NOTES.md` §8b names it verbatim. ⚠ Distinction from `F125` survives **re-grounded** (dissolvable vs undissolvable boundary) | §3.1 |
| **`F146`** — `A1` never at `O0/large` | **manager** | ✅ **CENSUS UPHELD** (0 / 374, reproduces exactly) | ⛔⛔ **CONSEQUENCE CLAUSE REFUTED** — `ph66`'s own committed `controls/inside_share.json` carries `A1` at `O0/large` on all 8 cells. ▶ **the ⭐⭐⭐ is unearned** | §3.2 |
| **item 147** — the `n/a` | engineer | ✅ **CONFIRMED** (and §3.2 is its scope) | ✅ **YES, the mixed provenance is worth a rule** — per-COLUMN, not per-file. `F108` one level down | §3.3 |
| **item 146** — `O0` sweep | engineer | ⛔ **NO** — measuring is alive; the item names the wrong instrument | ⭐ **SWEEPING is what is dead** (`php50_align_sweep.py:86` hard-codes `O3`), so no `O0` **SIGN** can clear §B5 and none can be published | §3.4 |
| **item 137** — publish both, always | **manager** | ⛔⛔ **THE MANAGER'S ANSWER (a) IS OVERTURNED.** Both options are on the wrong axis | ⛔ **Publishing both statistics at `O3` reads `+0.0000` in BOTH** (`_061` §292-295). Only the `-O` axis catches it. ▶ **the matrix is 4-D** | §3.5 |
| **`F141`** — obligation 5's gate | **manager** | ✅ **UPHELD** (the gate names the wrong predicate; `n = 1` existence proof) | ⛔⛔ **SCOPE REFUTED** — `61.3 %` is a **POPULATION SUBSTITUTION** (corpus reproducers vs the row's authored trigger), and the selection test is untestable at `n = 2` built temporal rows | §4.2 |
| **item 126** — the §A3a trade | **manager** | ⛔⛔ **THE TRADE DOES NOT EXIST** | ⛔ Its cost premise (*"a full PHP compile"*) is **false by ~100×** — 30 s cold, ~600 ms incremental, **measured twice, in the same file as the rule**. ▶ REQUIRED ✅ · PERMITTING ⛔ · REQUIRED-BUT-GATED ⛔⛔ · **the new wording is overturned** | §4.3–4.4 |
| **`F142`** — the cost ledger | **manager** | ✅ **THE ADMISSION UPHELD** · ⚠ **the consequence UPHELD-BUT-IMMATERIAL** — at the defensible split every published figure is **bit-identical** | ⛔ **THE MORAL REFUTED.** Not *"`F132` one level up"*: **`F132`'s remedy would not have caught `"040"`**. They are siblings, and the family statement is the part that may enter | §5.1 |
| **item 144** — ledger non-uniformity | **manager** | ✅ **KEEP `1.00` STANDS** · ✅ the unease is correct and **bigger than row 13** | ⛔ *"UNKNOWN direction"* **REFUTED** — the direction is **strictly DOWNWARD** by the ledger's construction. ⭐ The census costs **one command**: **3** invisible row-attributable documents naming **4 built rows** | §5.2 |
| **`F139`** — where a trap lives | reviewer | ✅ **MEASUREMENT SETTLED** (not attacked) | ⛔⛔ **THE INFERENCE REFUTED.** *"Location is not the variable"* is false: the axis is **text vs an invoked arm**, all four failures are ONE cell, and the other cell has **≥ 8 holds** — two of them cited in the ruling's own last paragraph. ✅ **The ruling's ACTION is right** | §6.1 |
| **`F140`** — scope is not derived | **manager** | ✅ **UPHELD AND UNDER-STATED** — `_061` missed **FOUR** routed items, not one | ✅ **CAUSAL CLAIM UPHELD ON NEW GROUND** (recall 2/2 at `_057` → 1/4 at `_061`; the list grew 2 → 9). ⛔ The brief's counter-evidence is a **third population substitution**. ⛔ *"the arm matched NONE of 144–147"* is **FALSE — it matched three.** ▶ **REPAIR, NOT THEATRE** | §6.2 |
| **item 125** — demoted-once items | **manager** | ✅ **CENSUS RUN** — 66 reports, 80 sections, 631 items, **27 members**, and it finds `F123`'s own founding instance | ⛔ **AS SPECIFIED IT IS REFUTED** — a line-level grep misses that instance. ⭐⭐⭐ **RESULT: `F123`'s repair was a prose box; three rounds carried it and none did the work; `F140`'s ARM scoped it on its first run** | §6.3 |
| **item 139** — `F133`(i)'s denominator | reviewer | ⚠ **THE WEAKENING UPHELD-NARROWED** — the brief's two-row test returns **1–1** (`ph03` could, `ph64` could not) | ⛔ **Its remedy is the wrong column.** *"Did it FACE the choice?"* is undecidable; **`same_construct?`** is checkable. ▶ `held` conflates **CHOSEN** and **DISCOVERED**, which `F133`'s own re-worded rule already distinguishes | §7.1 |
| **item 145** — generators in `.temp/` | **manager** | ⛔ **THE TENSION IS A FALSE DICHOTOMY** — two rules, two document lifetimes; the tree implements the resolution **three times** already | ⛔⛔ **SCOPE REFUTED BY ~100×.** **114** `.temp/` citations across the four permanent families, **10 in `.memory-php/`**, of which **3 are LIVE DEPENDENCIES** in `02-ladder.md` on **the manager's own scratch** | §7.2 |

### ⭐ THE ROUND'S SHAPE, COUNTED OVER THIS TABLE, NOT RECALLED

⛔ **Counted off the table above, row by row, not recalled** (DoD 13):

- **17 objects verdicted, all 17 reached.**
- ⛔ **15 of 17 carry an outright ⛔ REFUTATION** of the stated reason, scope,
  moral, novelty claim or answer. **The two that do not are `F143` and item 147 —
  both ENGINEER-opened, and both had already scored themselves against their own
  falsifier before I saw them.**
- ⚠ **3 are UPHELD-ON-NEW-GROUND**: `F143` (the gated `model.py` declaration),
  `F140`'s causal claim (the list grew 2 → 9), `F139`'s *action* (against its own
  stated reason).
- ⭐⭐ **Of the 9 manager-opened objects (§0.1): 9 of 9 carry a refutation.**
  Of the 6 engineer-opened: 4. Of the 2 reviewer-opened: 2.
- ⭐⭐⭐ **THE ROUND'S OWN HEADLINE, AND IT IS NOT ONE OF THE SEVENTEEN: THREE
  MANAGER FINDINGS FILED WITHIN ONE DAY (`F141`, `F142`, `F146`) EACH COMMIT
  **THE SAME ERROR** — a rate or a census measured over one population and
  asserted about another — AND `F142` IS THE FINDING THAT NAMES THAT ERROR.**
  §3.2, §4.2(a), §6.2(c). **That is a rate (n = 3), and item 123's rule says
  three instances is a rate.**

---

## §9 ⛔ `§ ORDER TO RESUME IN` — THIS BINDS THE MANAGER (`F123`)

**I reached every section of the brief.** What follows is work this round
*created* or *bounded but did not finish*, in the order I would do it. ⚠ **Each
carries the priority I would give it and my measured or estimated cost.**

1. ⭐⭐⭐ **HAND-ADJUDICATE THE 25 REMAINING ITEM-125 MEMBERS.** §6.3 produced
   **27 candidates** and confirmed **2**. The remaining 25 need one read each
   against the next task file. **Cost: ~15 minutes** (not `_057`'s ~1 h — the
   extractor is written and the population is 27, not 631).
   ▶ **HIGHEST, because it is the only object in this round whose HEADLINE NUMBER
   I could not produce, and because it is the item that has been deferred six
   rounds.** ⛔ **Do not re-estimate this at an hour; that estimate is why it sat.**
2. ⭐⭐⭐ **THE THREE LIVE `.temp/` DEPENDENCIES IN `.memory-php/02-ladder.md`**
   (`:447`, `:451`, `:612` → `.temp/mgr172/NOTES.md`, `.temp/mgr170/null_control.py`).
   **Cost: promote two files, or re-write three citations as HISTORY.** ▶ **HIGH,
   because it is the authoritative layer depending on auto-`rm`-able scratch, and
   the same directory family has already lost state once** (`RECAP_PHP.md:115`).
3. ⭐⭐ **THE `same_construct?` SPLIT IN `item139_sibling_census.py`** (§7.1c),
   with its two §H negatives. **Cost: ~20 min.** ▶ **HIGH** — `F133`'s landed rule
   says *CHOSEN not DISCOVERED* and its instrument does not implement it, so the
   published *"7 of 8"* is over-stated **today**.
4. ⭐⭐ **`F146` / `F144` / `F141`'s SHARED ERROR** (§8's headline). ▶ **HIGH as a
   LAYER candidate, not as a repair**: at `n = 3` it is a rate, and it is the
   first process finding in this programme with three independent instances **in
   one round**. **Cost: it is written; it needs a manager decision, not work.**
5. ⭐⭐ **THE `O0` SWEEP ARGUMENT** (§3.4): `php50_align_sweep.py --opt`, with the
   two §H negatives named there. **Cost: ~30 min.** ▶ **MEDIUM-HIGH** — it is the
   only thing standing between the corpus and publishing an `O0` **sign**, and
   two of the last three statistic findings came from `O0`.
6. ⭐ **PROMOTE `s6_unsure_items.py`** to `.tasks-php/probes/` as an `ⓘ` printing
   arm (§6.3d), with its two §H negatives. ▶ **MEDIUM** — it is item 125's
   durable repair, and §6.3(c) is the evidence that the prose repair failed.
7. ⭐ **THE NAMED SENSITIVITY ROW IN `task_cost.py`** (§5.2c) and its `N`-arm.
   **Cost: ~20 min.** ▶ **MEDIUM.**
8. ⚠ **`CATALOGUE.md`'s `status` COLUMN IS STALE BY SEVEN ROWS** (§4.2b). A
   `boxcheck.py` arm derives it from `ls -d patterns-php/ph*`. **Cost: ~15 min.**
   ▶ **MEDIUM — cheap, and it is the corpus's own index.** **NEW OPEN ITEM.**
9. ⚠ **RE-RECORD ITEM 129's CLOSURE ON THE NEW GROUND** (§6.1c). It stays closed;
   its stated reason is refuted. **Cost: one edit.** ▶ **MEDIUM.**
10. ⓘ **THE `inside_share.py` DEAD LOOP** (§3.3) and the per-column provenance
    label. ▶ **LOW** — harmless, but it is in a committed control.
11. ⓘ **`s2_witness.py` DROPPED INTO `ph66`'s REAL `verus.rs`** (§2.1.4) — the
    strengthening from *non-provability* to *falsity*. ▶ **LOW as a repair, HIGH
    as a RESULT if `F145` is re-stated**, because it is what makes the re-statement
    concrete. ⛔ Costs a re-gate.
12. ⓘ **SIZE THE `F98`-SHAPED COMMENTS NO ARM CAN SEE** (§1.4.2). A read of every
    comment in `patterns-php/*/c/*`, not a grep. ▶ **LOWEST** — real, but it is
    the only item here whose cost I cannot bound.

---

## §10 ⭐ `§ WHAT I AM UNSURE OF`

1. ⚠⚠ **§6.2's confound is unresolvable and it is the biggest hole in this
   report.** The router's regex widening and the item re-wording landed in **one
   commit** (`8c2a546`) with no intermediate state, so `NARROW × pre-rewording
   text` **cannot be computed from this tree**. My `NARROW = 7` is against
   post-rewording text. ⛔ **I therefore CANNOT fully answer the brief's (b).**
2. ⚠ **§7.1(b)'s CHOSEN/DISCOVERED classification is MINE, not a measured
   column.** I read source for **two** rows (`ph03`, `ph64`); the other five are
   classified from the census's own `claim` text. **`ph55` I call borderline and
   I did not resolve it.**
3. ⚠ **§2.1.4's *"N2 proves non-provability, not falsity"* is a logical point I
   am confident of and did not stress-test.** For this decidable fragment a Verus
   postcondition failure is almost certainly a genuine counterexample; **the gap
   is formal, and I have not shown it is ever practically wide.** `W1` closes it
   regardless, which is why I did not pursue it.
4. ⚠ **I did NOT drop the witness theorem into `ph66`'s real 1 647-line
   `verus.rs`** (§2.1.5). `rlimit`, the real `G`/`Node` types and `s_find_del`'s
   `fuel` plumbing are untested. **A drop-in is likely and is not measured.**
5. ⚠ **§3.1(c) swept the 13 rows' `NOTES.md` for uses of `inside_share`. I did
   NOT sweep `.memory-php/`, `RECAP_PHP.md` or the 66 task reports** for the
   certification direction. ⛔ **So *"nothing still rests on it"* is a claim about
   the ROWS.**
6. ⚠ **§5.2(c)'s magnitude is an ASSUMPTION** (~1 task-equivalent per invisible
   document) and I label it as one. The **count** (3 documents, 4 built rows) and
   the **direction** (down) are measured; the number is not.
7. ⚠ **§3.0's `O0/large` figures come from a LIVE callgrind over a gitignored
   build root**, not from the frozen measurement pipeline. That is item 147's own
   point turned on my own evidence. The `O3` and `O0/small` figures are from the
   committed record.
8. ⚠ **I did not re-derive `F141`'s *"6 of 12 built rows record a fault marker"*.**
   The classification is prose-based and I say where I rely on it and where I do
   not (§4.2c).
9. ⚠ **§1.5's threshold (*"≤ 2/10 after five more adjudications"*) is a judgement
   I invented to make the ruling falsifiable.** It is not derived from anything;
   its merit is only that it is checkable.
10. ⚠ **§6.1(b)'s eight holds are drawn from this programme's own narrative** and
    are therefore selected for having been written down. I argue in §6.1 that the
    bias cuts toward `_061`'s position and not mine, but it is a bias.
11. ⚠ **`ph00-smoke` and `php-5.0.0.manifest` are excluded from "13 built rows"
    throughout.** That matches every other count in the tree; I did not re-derive
    the convention.
12. ⛔ **I did not verdict anything outside the 17.** Several adjacent things
    surfaced (`CATALOGUE.md`'s stale column, `citecheck.py`'s HEAD rc=1) and are
    **reported, not ruled**.

---

## §11 HOUSEKEEPING

- ⛔ **No `git add`, no `git commit`, no history-mutating git.** Read-only `git
  show` / `git log` only. **`git status --porcelain` at the end: a single `??
  .tasks-php/TASK_PHP_063_REPORT.md`.**
- ⛔ **Nothing edited under `harness/`, `common/`, `patterns/`, `results/`,
  `pilot/`, `common-php/`, `patterns-php/`, `RECAP_PHP.md`, `.memory-php/`,
  `.web/`.** Every repair in this report is **PROPOSED**, with its §H negatives
  where it is a validator.
- ✅ **Both brackets re-run at the end, green**: `python3 .tasks-php/checkers.py`
  → `CHECKERS PASS`; `python3 .tasks-php/cbaseline_check.py` → `scanned 35
  file(s); 77 hit(s); ratchet 77`, **rc 0**. Also green: `contract_audit.py`
  (`✅ no problems`), `probes/rule9_mustfire.py` (`PASS`, 12 arms),
  `probes/item139_sibling_census.py`, `boxcheck.py`.
- ✅ **`grep -a` throughout** (F35).
- ✅ **Scratch: `.temp/php63/` only.** **10 generators (`.py`) + 2 Verus `.rs`
  sources** — **`CLAUDE.md` rule 1 keeps both classes**; no blobs, no
  `__pycache__`, no artefact to delete. **No `/tmp` file was created.**
  ⭐ **Every figure in this report is produced by one of the ten, by a checker in
  `.tasks-php/`, or by a `git show` / `grep -a` quoted inline** (law 6).
- ⚠ **Verus runs: 3** (2 scored + 1 failed on my own typo, which the arm caught).
  No re-gate, no rebuild, no PHP compile, no re-measure.
