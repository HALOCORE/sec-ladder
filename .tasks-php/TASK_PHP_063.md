# TASK_PHP_063 — **THE TENTH REVIEW ROUND.** ⭐⭐⭐ Eight findings **and nine routed items**, and this is the first round in the programme's history whose scope was **DERIVED BY A TOOL** instead of remembered by the manager

**Role:** research **reviewer / analyst**. **One agent, alone.**
**Report:** `.tasks-php/TASK_PHP_063_REPORT.md` — **write the FILE** (`PROTOCOL.md`
rule 10). A report that exists only in your final message does not exist.

⚠⚠⚠ **YOUR JOB IS TO FALSIFY, NOT TO CONFIRM.** `.memory-php/04-process.md`
**law 12**: *a manager finding from one probe or two rows should be assumed
narrowable until a reviewer has had it.*

⛔ **Count the manager findings yourself** — read `RECAP_PHP.md`'s RULE-9 table
and take the rows whose verdict column opens `⛔ UNREVIEWED`, then read who
opened each. **Do not trust this sentence**: a count in prose about a structure
rots exactly like one inside it (`F121`), and **`F138` is the manager doing
precisely that with this table.**

⭐⭐⭐ **THE STANDING RECORD, SO YOU KNOW WHAT NORMAL LOOKS LIKE.** **Nine
consecutive review rounds have refuted manager or engineer claims.** At `_053`
**not one finding survived as written**. At `_055` **three of four conclusions
survived and ZERO of four REASONS did**. At `_058` **zero of five manager
predictions survived**. At `_061` **six of the eight findings it verdicted carry
a refutation IN THE VERDICT COLUMN ITSELF** — counted over the RULE-9 table, not
recalled; **only `F131` and `F132` do not.**

> ▶ **SO: SCORE THE CONCLUSION AND THE REASON SEPARATELY, EVERY TIME, IN THOSE
> WORDS.** A finding whose conclusion holds on a ground you had to invent for it
> is **UPHELD-ON-NEW-GROUND**, not UPHELD, and that distinction has been this
> programme's most valuable single output for seven rounds running.

---

## §0 ⛔ READ THIS BEFORE PLANNING YOUR TIME

**Eight findings and nine open items.** That is **the largest scope any round
has carried** — `_057`'s was 13 findings, `_061`'s was 8 findings and **one**
item. ⚠ **Rounds have folded items in before — `_057`: 2, `_059`: 4, `_061`: 1 —
and every one of those was the manager REMEMBERING. That is the variance `F140`
is about, and §0.0 is what replaced it.**

### 0.0 ⭐⭐⭐ WHY THE ITEMS ARE HERE, AND WHY THAT IS THE POINT

**`F140`** is the finding that a round's scope is *derived* from the RULE-9
table while **nothing** is derived from the items table — so an item saying
*"this is a reviewer's"* was **invisible to the process that scopes rounds**.
Item 137 proved it on itself: it routed itself to *"the round the backlog
already owes"*, `_061` was that round, and the item is absent from `_061`'s
brief and report (`grep`: **0** and **0**).

The repair is an `ⓘ` arm in `boxcheck.py` that **PRINTS** the routed items and
**cannot fail a run**. ▶ **This brief's item scope is that arm's output, pasted:**

```
items -> a reviewer    9  LIVE, unscheduled: 125 126 135 137 139 144 145 146 147
```

⛔⛔ **AND THE ARM'S AUTHOR EVADED IT FOUR TIMES IN THE TURN THAT WROTE IT.**
Items 144–147 were registered saying *"▶ A REVIEWER's, and it goes to `_063`"*
and the arm matched **none** of them, because it keyed on the spellings `F140`
happened to use. It has been widened, the items were given explicit addressees,
and two must-fire negatives were added (`rule9_mustfire.py` rows 904/905 — **905
asserts a KNOWN HOLE**, an item with no addressee at all, so that the hole is not
mistaken for coverage).

> ⭐⭐ **THE LESSON IS NOT THE REGEX. It is that an arm keyed to the phrasing of
> the instance that produced it catches that instance and nothing else.**
> ▶ **`§6` asks you to rule on whether that repair is sound or theatre.**

### 0.1 ⭐ MEASURED PREMISES — every one was RUN before this file was written

`PROTOCOL.md` **rule 14**: *run the premise before you write it into a task
file.* The two worst propagations in this programme's history (*"~7 000 words"*,
*"123 ASan reports"*) were both numbers nobody had measured, cited back by
engineers who had no reason to doubt them. Each row names its command, **run at
`8c2a546`**.

| premise | command | measured |
|---|---|---|
| the checker registry passes | `python3 .tasks-php/checkers.py` | `CHECKERS PASS`, **32 filed, 32 on disk** |
| the ratchet is green | `python3 .tasks-php/cbaseline_check.py` | `scanned 35 file(s); 77 hit(s); ratchet 77`, **rc 0** |
| both staleness brackets | `harness/measure.py --check-stale`; `harness-php/gate.py --tool measure --check-stale` | **`66 / 0 STALE`** and **`28 / 0 STALE`** |
| the backlog and the item scope are **derived**, not asserted | `python3 .tasks-php/boxcheck.py` | **8 open cycles**, **9 routed items** — the two lists this brief is sectioned from. ⚠ **Read the MEMBERS, not the count — that is `F138`** |
| row 13 gated | `results-php/gate/ph66-hashdel-uncompared.json` | `verdict: PASS`, `complete_run: true` |
| `ph66`'s `R5` verifies **with** the defect | the same record's `verus` block | **`verified: 49, errors: 0, pinned: 49`** |
| and its key-identity control is three-armed | `controls/key_identity.json` | `N1` hardened+obligation **verifies**; `N2` shipped+obligation **fails, postcondition**; `N3` shipped+vacuous **verifies** |
| ⭐⭐ `A1` is absent from **every** `O0/large` cell of **both** corpora | the `python3 -c` census in **§3.2** below | PAT **0 of 263** present; php **0 of 111**. `O0/small`, `O3/small`, `O3/large` are **all complete** |
| …and it is a documented plan, not a hole | `sed -n '50,64p' harness/measure.py` | `CG_PLAN`, with *"`large` is added only at O3, where the perf claims live"* |
| the `O0` sweep is hard-coded | `grep -an '^OPT' .tasks-php/php50_align_sweep.py` | `:86` → `OPT, MODE = "O3", "isolated"` |
| how many rows carry `inside_share` at all | `grep -rlan inside_share patterns-php/*/NOTES.md patterns-php/*/controls/*.py` | **10 of 13**; residue **`ph07`, `ph53`, `ph64`** |
| the live cost figures | `python3 .tasks-php/task_cost.py` | marginal **2.38**, searched-only **2.35**, first-in-family **2.22** (n=9), follow-on **2.75** (n=4), **PUBLISH `~57 .. ~72`, middle `~58`** |
| the report population, for `§6` | `ls .tasks-php/TASK_PHP_*.md \| grep -av REPORT \| wc -l`, and the same with `REPORT` | **62 task files, 66 reports** |
| ⚠⚠ …and the *"`WHAT I AM UNSURE OF`"* heading has **at least 12 distinct spellings** | `grep -ahoiE '^#+ *[^\n]{0,12}(WHAT I AM UNSURE\|UNSURE OF\|UNCERTAIN)[^\n]{0,30}' .tasks-php/TASK_PHP_*REPORT*.md \| sort \| uniq -c` | `## §7 ⭐ WHAT I AM UNSURE OF`, `## § WHAT I AM UNSURE OF`, `## §13 … AND WHAT I DID NOT DO`, `## §8 … — 14 items`, … **54 reports mention the word at all.** ▶ **A single fixed-heading grep WILL under-count. That is `F132`'s class waiting for you in §6.** |

> ⛔⛔ **WHAT §0.1 DELIBERATELY DOES NOT CONTAIN: any measurement of the evidence
> for a finding you are asked to attack.** **Law 12**: *the reviewer's
> INDEPENDENCE is the product.* Where a section needs a number, it gives you the
> **command**, not the answer. ⚠ **The one exception is `F146`, which is my own
> finding and whose census IS the premise — attack the census too if you like it
> not.**

### 0.2 ▶ THE ORDER IS BINDING: §1 → §2 → §3 → §4 → §5 → §6 → §7

⭐⭐⭐ **STOPPING CLEANLY IS A FIRST-CLASS OUTCOME.** If you run out of depth,
**STOP AND SAY WHERE.** A report that verdicts §1–§3 properly and says *"I did
not reach §6"* is worth more than one that touches seventeen things shallowly —
and the second kind is how a round produces confirmations instead of verdicts.

⛔⛔ **YOUR STATED PRIORITY BINDS THE MANAGER. `F123` IS WHY.** An engineer wrote
*"it is the cheapest remaining check and it is not done"*; the manager's next
task file demoted it to *"nice to have, skip it"*; two rounds later the protocol
treated it as **impossible** — and it turned out to cost **30 seconds**.
▶ **Write a `§ ORDER TO RESUME IN` naming what is left AND the priority you
would give it. It will be CARRIED, not re-ranked.**

⭐ **Nothing in this round needs a re-gate, a rebuild or a PHP compile.**
Everything is arithmetic over committed records, a grep, or a Verus run whose own
`pin` states its cost (`ph66`'s `controls/key_identity.py`: *"three Verus runs;
about a minute"*).

---

## §1 ⛔ ITEM 135 — ONE GREP, AND IT IS FIRST BECAUSE IT WAS LEFT FOR YOU ON PURPOSE

`RECAP_PHP.md` → open item **135**. `TASK_PHP_060` §15 raised it; the manager
**registered it and did not answer it**, because the item's own closing line is
*a question routed to nobody in particular is one nobody answers* and answering
it myself would have made me the fourth home for a fact.

**The state.** The `_INDEP` ratchet exists to catch **a corroboration claimed
between two artefacts**. Its four hits are `ph29:23` (*independently cached*),
`emalloc_shim.h:640` (*order-independent*), `ph97` `kernel.c:323` /
`kernel_hardened.c:356` (*TWO INDEPENDENT BYTES*) and `ph96` `kernel.h:112`
(*a third independent byte*). **All four are the word used as an ADJECTIVE
DESCRIBING DATA**, checkable from the file that says it. `_056` called the class
*recurring* at three; at four it is **the single largest entry class in that
ratchet**.

**THE QUESTION:** *is a ratchet whose biggest class is a known, structural
false-positive shape in its intended steady state — or is the class evidence the
predicate is aimed one concept off?*

⭐ **THE ITEM NAMES ITS OWN CHEAP DISCRIMINATOR AND NOBODY HAS RUN IT:**

> *"ask whether any TRUE positive has ever been filed in this class. If none has,
> that is the answer and it cost one grep."*

▶ **Run it.** ⚠ **And note the trap §0.1's last row plants**: *"one grep"* is the
item's estimate, not a measurement — **if the true positives would be spelled
several ways, a single-spelling grep answers a narrower question than the one
asked, and you should say so rather than report its number.**

⛔⛔ **CONSTRAINTS, BOTH BINDING AND BOTH FROM THE ITEM:**
1. **NO REGEX CHANGE IS PROPOSED AND NONE SHOULD BE MADE ON THIS ITEM ALONE** —
   §F6a and the ratchet rule both forbid tuning a regex to its hits, and the
   false-positive direction is the safe one.
2. **NOR SHOULD THE PROSE BE REWORDED TO DODGE THE GREP.** The engineer declined
   that deliberately; on `ph96` it would also cost a **32-cell re-measure**.

▶ **A verdict of *"steady state, leave it"* is a perfectly good outcome and is
the one the manager expects. Say which, and say what would change your mind.**

---

## §2 ⭐⭐⭐ `F145` AND `F143` — THE TWO ROW-13 FINDINGS THAT WOULD CHANGE `.memory-php/02-ladder.md`

These are **engineer** findings from `_062`, both scoring **registered manager
predictions**, and they are first among the findings because they are the only
two in this round that would enter the **ladder** file. Everything else in this
brief is process or instrument.

### 2.1 `F145` — *"`R5` cannot BOTH compute `R1`–`R4`'s function AND refuse the defect"*

Read: `RECAP_PHP.md` → `F145`; `TASK_PHP_062_REPORT.md` §P3;
`patterns-php/ph66-hashdel-uncompared/verus.rs` and `controls/key_identity.py`
with its `.json`.

**Settled, and not what you owe it**: the shipped `verus.rs` verifies **with the
defect** (49/0) — `_062`'s `P3` predicted *"R5 is the only rung that can refuse
it"* with falsifier *"an R5 that verifies with the defective predicate in
place"*, and **the shipped artefact is that falsifier**. The `N1`/`N2`/`N3`
table is three Verus runs and reproduces in a minute.

⚠⚠ **WHAT YOU OWE IT IS THE TENSION CLAIM**, in the finding's own words: *making
`verus.rs` refuse would mean stating its `ensures` against a correct delete
rather than against `hash_fold` — and then `R5` would no longer compute the same
function as `R1`–`R4`, so the cross-rung checksum would be comparing two
different programs.*

▶ **ATTACK IT. The specific question, and it is answerable with Verus rather
than with an opinion:**

> ⭐⭐⭐ **Could a spec function carry the defect for the CHECKSUM while a
> SEPARATE `ensures` clause refuses it?**

If **yes**, the tension dissolves into a row-level design choice and the finding
shrinks a long way — from *a constraint of the ladder* to *how `ph66` happened to
write `hash_fold`*. If **no**, say precisely what blocks it.

⭐ **The engineer removed the cost excuse in advance**: *nothing resists at the
Verus level — eleven tokens, one recursive proof, no lemmas.* **So if this is a
design constraint it is a logical one, not a budget one, and it should be
statable as such.**

### 2.2 `F143` — *"the first row the whole safety stack is blind to"*

Read: `RECAP_PHP.md` → `F143`; `_062` §0/§P1/§P2; the row's `controls/ladder.py`
+ `.json`, and its `safe_naive.rs`.

**Settled**: six rungs return the **same `u64` on all eight inputs**; ASan/UBSan
`fired: false`; Miri `ub: false`. It is in the gate record.

⚠⚠ **WHAT YOU OWE IT IS THE FAITHFULNESS QUESTION — AND THE ENGINEER RAISED IT
AGAINST ITSELF**, which is why it is worth taking seriously rather than
dismissing:

> a safe-Rust `R2` built on a real `HashMap` **would have deleted the bug**; one
> that ports the bucket logic reproduces it.

▶ **So *"the safety stack is blind"* is at least partly a statement about a
PORTING CHOICE.** **Is the finding about `ph66`, or about how `ph66` was ported?**

⭐⭐ **AND THE HARDER VERSION, WHICH IS WHY THIS IS NOT A ROW NOTE:** `_060`'s
`P2` made the **opposite** choice explicit for `ph96` —

> *"an R2 mirroring the C's control flow with `.unwrap()` panics; one that
> handles `None` has deleted the bug — both are legitimate and they are different
> rows of the ladder's column."*

▶ **If the ladder's *"does the defect survive?"* column takes its value from a
choice the protocol does not constrain, then the column needs a RULE before this
finding may enter the layer.** **Does it? Write the rule, or say why none is
possible.** ⛔ **That is the deliverable of this sub-section, not a verdict word.**

⚠ **`CLAUDE.md` rule 6 is live here and cuts in the finding's favour**: *"safe
Rust reproduces the bug bit-identically"* is a **FINDING, NEVER A KILL**. You are
being asked whether the finding is correctly *scoped*, not whether it is
embarrassing.

---

## §3 ⭐⭐⭐ THE INSTRUMENT CLUSTER — `F144`, `F146`, AND ITEMS 137, 146, 147

⭐⭐ **These five are ONE QUESTION SEEN FROM FIVE SIDES and they must be verdicted
together, or you will write `F131`'s defect** (*one home per fact*) **into the
round that is supposed to be policing it.** The question:

> **What is `A1` blind to, at what optimisation level, and what has the corpus
> published on the strength of not knowing?**

### 3.1 `F144` — the `+0.0000` that a 65 % share did not predict

`RECAP_PHP.md` → `F144`; `_062` §P4; `controls/inside_share.py` + `.json`.

**Settled**: `A1` reads **exactly `+0.0000`** for `c-clang` at `O3` against
family B's `−2.03` / `−12.00 Ir/call`, because **clang keeps
`zend_hash_del_key_or_index` out of line** (`0x3a5` vs `0x3a2`) where **gcc
inlines it** — one `nm` line.

⚠ **First thing owed: IS IT NEW, OR IS IT `F125` RESTATED?** The distinction the
finding claims: `F125`'s cause was *a choice a PERSON makes* (moving work into
libc); this one is *a choice the COMPILER makes*, so **a row cannot avoid it by
writing its kernel carefully**. ⛔ **If that distinction does not survive, this is
`F125` with a second example and belongs INSIDE `F125`, not beside it.**

⭐⭐ **Second thing, and it is the one with teeth**: the finding says a high
`inside_share` *could not* have predicted this — the share measures *how much of
the cell is inside the symbol*, and the question is *whether THE DIFFERENCE is*.
**If true, every use of the share as reassurance in the corpus is weaker than it
reads**, and `_059` already refuted the share as a **gate**.

▶ **DOES ANYTHING STILL REST ON IT?** §0.1 gives you the population: **10 of 13
rows** carry `inside_share` somewhere. **Go and look.** A row that computed the
share and then *concluded* something from its height is the casualty; a row that
printed it as context is not.

### 3.2 `F146` — ⚠ MY OWN FINDING, FILED WHILE WRITING THIS BRIEF, AND ATTACK THE CENSUS TOO

`RECAP_PHP.md` → `F146`. **This is the manager's, opened today, and §0.1's
law-12 exemption applies to it: the census below is the evidence, so you are
entitled to re-run it rather than believe it.**

```
python3 -c "
import json,glob,collections
def census(pat):
    agg=collections.Counter(); rows=0
    for p in sorted(glob.glob(pat)):
        d=json.load(open(p)); rows+=1
        for c in d.get('cells',[]):
            if c.get('mode')!='isolated': continue
            ir=c.get('ir') or {}
            for inp in ('small.bin','large.bin'):
                ok=bool((ir.get(inp) or {}).get('kernel_exclusive_ir'))
                agg[(c['opt'],inp,ok)]+=1
    return rows,agg
for label,pat in (('PAT','results/p*.json'),('PHP','results-php/ph*.json')):
    rows,agg=census(pat); print('---',label,rows,'rows ---')
    for k in sorted(agg): print(' ',k,agg[k])
"
```

**Measured**: `kernel_exclusive_ir` is present on `O0/small`, `O3/small` and
`O3/large` for **every** isolated cell of **both** corpora, and absent from
`O0/large` on **all 374** of them (**263** PAT + **111** php). The cause is
`harness/measure.py`'s **`CG_PLAN`**, one deliberate line, with the comment
*"`large` is added only at O3, where the perf claims live."*

⚠⚠ **WHAT YOU OWE IT IS THE CONSEQUENCE CLAUSE, WHICH IS THE ONLY PART THAT IS
MINE:** *`_061`'s rule — show the matrix at more than one optimisation level —
cannot be discharged from committed records.*

▶ **ATTACK IT.** `_061` **did** obtain `O0/large` `A1`, by running its own
callgrind (`.temp/php61/ph96_price_at_O0.py`). ⛔ **So *"the instrument cannot
supply it"* may be only *"the instrument does not supply it for free"* — and if
that is right, `F146` shrinks to a note on HOW to obey the rule and the ⭐⭐⭐ is
unearned. **Say which, in those words.**

⭐⭐ **Second, and independent**: the `CG_PLAN` comment's justification —
*"where the perf claims live"* — **is a PAT-era premise the php programme has
since falsified twice** (`F136`'s headline refuted **at `O0`**; `F144` caught
**because** `_062` looked at two levels). ▶ **Is that a real obsolescence, or two
instances read as a trend?** ⚠ **n = 2, and this programme has a rule about that**
(item 123: *three instances is a rate and one is not yet a design*).

⛔⛔ **NO EDIT TO `CG_PLAN` IS PROPOSED AND YOU MUST NOT PROPOSE ONE AS A FIX.**
`harness/measure.py` is hashed into **all 33 PAT measurement records**
(`CLAUDE.md`, top): changing it costs a **full re-measure**. If you think the
plan is wrong, that is a *finding about the plan*, and it goes to the user with
its price attached — the same shape as open item 105.

### 3.3 Item 147 — the `n/a`, now CONFIRMED, and what survives

The engineer's conjecture was **right** and §3.2 is why. ⛔ **What is left is not
the cause but a thing the item did not anticipate:** `ph66`'s printed matrix
carries **two provenances in adjacent columns** — `A1`/`W`/`share_W` from a
**live** callgrind over the build root, `share_F74` from the **committed**
record — and the blank falls on exactly the 8 cells `CG_PLAN` never wrote.
▶ **Is a table that mixes a live and a committed measurement, unlabelled, a
defect worth a rule?** ⚠ **Bear `F108` in mind: five things every percentage
owes, and *which build* is one of them.**

ⓘ **While you are in that file**: `controls/inside_share.py:113-116` is a loop
that iterates every cell, `continue`s the non-isolated ones and then does `pass`
— **dead code in a committed control.** Harmless; report it, do not fix it under
this round (§H: a validator change lands with its must-fire negatives).

### 3.4 Item 146 — is *"never QUOTE an `O0` figure"* quietly becoming *"never MEASURE at `O0`"*?

`_062` §8.2, the engineer's own flagged uncertainty. At `O0` `ph66`'s R1h
**COSTS** (`+4.00`/`+6.12` gcc, `+5.00`/`+9.69` clang `Ir`/call); at `O3` it
**SAVES** (`−3.20`/`−19.83`, `−2.03`/`−12.00`) — **sign-stable over a 32-residue
pad sweep.** `php50_align_sweep.py:86` hard-codes `OPT = "O3"`, and
`.memory-php/03-numbers.md` forbids quoting an `O0` figure as a performance
figure — **so the engineer treated the `O0` numbers as lowering readings and
published neither sign.**

▶ **THE QUESTION IS ABOUT WHAT A SWEEP IS FOR**, and §3.2 shows `O0` is
under-instrumented from a **second** direction. ⚠⚠ **THIS IS NOT A PROPOSAL TO
PUBLISH `O0` MAGNITUDES** and a verdict that reads as one has answered a
different question.

### 3.5 Item 137 — the rule says ALWAYS and 7 of 12 rows did not, one of them on purpose

**Measured across all 12 rows at the time**: `W1` appears in `NOTES.md` for
`ph45`, `ph52`, `ph53`, `ph55`, `ph56` — **five**; **zero** times for `ph03`,
`ph07`, `ph16`, `ph64`, `ph96`, `ph97`; **once** for `ph29`.

⭐⭐ **`ph96` is the interesting one because it declined ON PURPOSE and showed its
working**: `_060` §8 computed the 16-cell share matrix **first**, found the two
differences the row leans on hardest are **exactly zero**, and concluded *"`A1`
is the resolving statistic for this row."*

**(a)** a violation of a rule that says ALWAYS, or **(b)** evidence the rule's
real content is *measure both, publish the one that RESOLVES, and show the matrix
that proves which*?

⛔⛔ **THE ITEM IS ALREADY HALF-ANSWERED AND THE ANSWER WENT AGAINST WHAT IT LEANED
TOWARD.** `_061` §2.2 refuted `F136`'s headline **precisely because `ph96`
published `A1` only** — at `O0/isolated` `A1` reads `+0.0000` while `W1` moves
`−2.24 … −19.58 Ir/call`, and upstream's repair is the **dearer** one. **That is
(a).**

▶ **SO WHAT IS LEFT FOR YOU IS NARROWER AND SHARPER: `ph96` did the diligent
thing — matrix first, reasoned choice, working shown — AND STILL PUBLISHED A
CLAIM THAT DOES NOT HOLD ONE OPTIMISATION LEVEL DOWN.** ⭐⭐⭐ **If diligence was
not sufficient, the rule cannot be *"be diligent"*. State the rule that WOULD
have caught it** — and check it against §3.2, because a rule that requires an
`O0/large` `A1` requires a callgrind run no committed record holds.

⚠⚠ **THE MANAGER DOES NOT RULE THIS AND SHOULD NOT**: deciding by fiat would
settle a measurement question with a preference.

---

## §4 ⭐⭐ `F141` AND ITEM 126 — §A3a's FIFTH OBLIGATION. **ONE QUESTION, TWO NUMBERS.**

Item 126 says so itself: *"scope this into `_063` beside `F141`; they are one
question."*

### 4.1 What is settled

`rebuild_hardened_php.sh --label ph66` gives **`rc=0` on both images** while the
adversarial observable flips **`count=1 → count=2`** and the benign one stays
identical. ▶ **So obligation 5's old gate — *"REQUIRED, GATED ON the pre-image
run faulted"* — would have excused the cleanest obligation-5 result in the
corpus**, because this row's target error is a **silent wrong answer** and
nothing ever faults.

✅ **The wording has already been changed** to *"REQUIRED WHENEVER THE ROW CAN
NAME AN OBSERVABLE THE REPAIR IS EXPECTED TO MOVE, WHICH IS EVERY ROW"*, with the
old text struck and a note that **`F141` is UNREVIEWED and the wording is
overturnable**. ⛔ **You may overturn it. That is not a courtesy — the protocol
says so in the file.**

### 4.2 ⚠ What you owe `F141`: the SCOPE claim

*"Vacuous on **61.3 %** of the temporal axis"* is `_057` §3.2's rate **read as a
forecast over rows nobody has built.**

▶ **ATTACK IT.** The 38.7 % is over **CATALOGUED** temporal ids, and **rows are
SELECTED for buildability** — so the built population may fault far more often
than the catalogued one. ⛔ **If so, the finding shrinks to `ph66` alone, and item
141 is a one-line wording fix rather than an arm.**

⭐⭐ **And the harder half: the finding claims a defect with ZERO CASUALTIES.**
⛔ **The first version of that cell said *"all 12 built rows' triggers fault"* and
the manager never computed it.** Measured: **6 of 12 record a fault, 6 record
none** — **but the blanks are because §A3a's first ten rows ARGUED criterion 2
rather than running it**, so the gate has been **reachable on almost no row.**
▶ ***Is "it would have excused this row" a finding, or a prediction wearing a
finding's clothes?***

### 4.3 ⚠ What you owe item 126: the TRADE

> **REQUIRING it makes every row pay for a full PHP compile, and §A3a's entire
> merit is being cheap enough that nobody skips it; PERMITTING it may mean
> nobody ever does it.**

✅ **One leg is closed by measurement**: verifying the applied post-image
**bytes** (which `_056` did without building) tells you the patch **applied** —
**it cannot tell you the program's ANSWER changed.** On `ph66` the byte check
passes and says nothing, because `rc=0` on both sides and the whole difference is
in stdout. ▶ **On a row whose target error is a VALUE, only RUNNING the
post-image says the repair works.**

⚠⚠ **AND `F141` ADDED A LEG THE ITEM DID NOT ANTICIPATE.** The item framed the
trade as **REQUIRING vs PERMITTING**; what actually landed was a third thing —
**REQUIRED-BUT-GATED**, exempting precisely the rows where the check is most
informative. ▶ **Rule on all three, and note that `F123` measured the check's
cost at 30 SECONDS, not at a full compile — which may dissolve the trade
entirely. Check that number before you lean on it.**

---

## §5 ⭐⭐ `F142` AND ITEM 144 — THE COST LEDGER, AND A QUESTION ROUTED TO THE MANAGER BY NAME

### 5.1 `F142` — what is settled, and the two things that are not

**Arithmetic over the committed ledger, needs no review**: `"040"` was the R1h
hunt for `ph52` **and** `ph53` plus row 7's build brief, both rows gated since
`_041`/`_042`, and it sat classified `PENDING` throughout — marginal
`2.42 → 2.50`, **PUBLISH `~61..~77` → `~63..~79`**. ✅ Repaired at the data; a
`PENDING` entry now spells itself `"PENDING:ph66"` and `N8b`/`N8c`/`N8d`
re-derive the answer from the gated corpus every run.

⚠ **First thing owed: THE SPLIT.** The manager charged `"040"` **`0.5/0.5`**
across `ph52`/`ph53` and **did not measure that — he assumed it.**
▶ **ATTACK IT**: one task carrying two R1h hunts *and* one build brief may not be
half-and-half, and **the per-row series (`ph52` 2.50, `ph53` 3.50) is what moves
if it is not.**

⭐⭐ **Second, and it is the general claim**: *"`N8` bounds the pile's SIZE and the
property is its MEMBERSHIP"* is offered as **`F132`'s class one level up**.
▶ **Is that a real generalisation, or a post-hoc fit?** `F132` was about
adjudicating a ratchet's **SET** by unit text; this is a validator asking a
**cardinality** question. ⛔ **If they are only analogous, the finding is a good
repair with an over-reaching moral — and the moral is the part that would enter
`.memory-php/`.**

### 5.2 Item 144 — the non-uniformity the manager answered around

`_062` §8.2 routed a question to the manager **by name**, citing the rule it was
invoking: *"'this row cost one task' is a judgement, not an arithmetic fact, and
**I am the interested party**."* ⛔ **The manager read §8.1, answered it in the
protocol, and never read §8.2's first bullet** — `F140`'s class, one section
lower, about a **published** figure.

✅ **Answered since: KEEP `1.00`.** Every other entry measures the BUILD task(s)
and row 13 took one; changing the weight would make the series incomparable in
order to fix a level.

⛔⛔ **BUT THE ENGINEER'S UNEASE IS CORRECT AND THE MANAGER IS NOT RULING ON IT.**
`ph53`'s R1h hunt and build brief **were** a task file (`_040`, charged
`0.5/0.5`); **row 13's equivalent work — `ROW13_001.md`, two probes, the
`rebuild_hardened_php.sh` generalisation — was done by the manager inside
`_061`'s session and is charged NOWHERE.**

> ▶ ***So scoping is charged for some rows and invisible for others, and which
> depends only on whether a task file happened to be written for it.***

⚠⚠ **That is a defect in the LEDGER, and it biases the published projection in an
UNKNOWN DIRECTION.** ▶ **Say which direction, or say that it cannot be signed
without a census and what that census would cost.** ⭐ **§0.1 gives you the live
figures and the command; quote them as an EVENT with the commit, and make the
LABEL historical too — a date makes a number true as HISTORY while the word
*"live"* claims it is true NOW, which is how the RECAP cell carrying these very
figures went stale inside one session.**

---

## §6 ⭐⭐ `F139`, `F140` AND ITEM 125 — WHERE A TRAP LIVES, AND WHETHER ANYONE HAS CHECKED THE OTHER SIDE

⭐⭐⭐ **These three are the round's methodological core and they share one
missing control.** Read them together or you will verdict them three times.

### 6.1 `F139` — *"four homes, four failures, therefore location is not the variable"*

**The measurement is settled and is NOT what you owe it**: the wrong build is
checkable in three commands and the manager ran all three.

⚠ **What IS owed is the INFERENCE `_061` §5.0 hangs on it** — *four homes, four
failures, therefore location is not the variable* — **and that ruling is what
closed item 129 as a blocker.**

▶ **ATTACK THE `n`.** Four instances, all from one programme and largely one
author, is a small sample for a claim that general. ⛔⛔ **AND THE COMPARISON HAS
NO POSITIVE CONTROL: nobody has asked how many traps in these same four homes
DID hold.** ▶ ***If that control is missing, the ruling is an argument from
silence.***

⭐ **This is the cheapest high-value thing in the round**: the positive control is
a census, not a re-measure, and **§7 of this brief gives you a committed
instrument built for exactly this shape** (`probes/item139_sibling_census.py`,
6 arms — a table of `(row, kind, file, tripwire, held?, claim+generator, why)`).
**Reuse its shape; do not rebuild it.**

### 6.2 `F140` — *structural, not forgetfulness*

**The measurement half needs no review** — that item 137 is absent from `_061`'s
brief and report is two greps.

⚠ **What you owe it is the CAUSAL claim.** ▶ **ATTACK IT**: `_059` folded **four**
items in and `_057` folded **two**, so the manager demonstrably **can** remember.
***Is the variance really the absence of a derivation, or just this round's
author under load?*** ⛔ **If it is the latter, the arm is still harmless but the
FINDING is an over-reading** — and the manager says so in advance.

⭐⭐ **THE LIVE TEST IS THIS BRIEF.** §0.0 is the arm's output pasted into a round.
▶ **Rule on whether that is a repair or theatre**, and note the two facts that
cut opposite ways: **(a)** the arm caught nine items a human had not scoped;
**(b)** the arm's own author evaded it four times **in the turn that wrote it**,
and it only caught them after the regex was widened **and the items were
re-worded**. ⛔ **Fixing the text as well as the regex may mean the arm still only
catches what its author remembers to spell.**

### 6.3 Item 125 — *how many "cheapest remaining check" items were demoted once and never revisited?*

**`F123`, and it is the question the manager cannot answer about the manager.**
`_051` §8.1 called the PHP-rebuild check *"the cheapest remaining"*; `_052` §1.5
demoted it to *"nice to have, skip it"*; two rounds later a different agent said
*"I cannot"*; and it was absent from a protocol section. ⛔ **No step was a lie,
and nothing in this repo would have caught it.**

▶ **A COUNT OVER THE `§ WHAT I AM UNSURE OF` SECTIONS OF THE LANDED REPORTS WOULD
ANSWER IT** — every build and review report has one, by DoD.

⚠⚠ **THE MANAGER DELIBERATELY IS NOT THE ONE WHO SCOPES IT**, because the finding
is about the manager's own demotions. **§0.1 therefore gives you the POPULATION
and not the answer: 66 reports, 54 mentioning the word, and AT LEAST 12 DISTINCT
SPELLINGS OF THE HEADING.** ⛔⛔ **A single fixed-heading grep will silently
under-count, and an under-count here reads as *"the problem is small."*
Adjudicate the SET (`F132`).**

⭐ **The layer-shaped claim it would test**: *an engineer's own uncertainty may be
DEFERRED but not DOWNGRADED; the next task inherits its STATED priority, not the
manager's.* ⛔ **Not in `.memory-php/` and not going there unreviewed.**

---

## §7 ITEMS 139 AND 145 — TWO SMALL ONES, LAST BECAUSE THEY ARE CHEAPEST

### 7.1 Item 139 — `F133`(i) is well-formed for only one kind of repair, and the count may be counting sites that had no choice

**Done and committed** as `.tasks-php/probes/item139_sibling_census.py`. Sorting
all 13 rows by **what kind of change the R1h is**: **GUARD** (`F133`(i) is
answerable) on **8 of 13**, holding on **7**; **API-SWAP** (`ph29`, `ph53`)
answerable only at tree scope; **STRUCT** (`ph45`); **DELETION** (`ph52`);
**BUILD** (`ph16`). ▶ **For five rows the question has NO ANSWER rather than a
NO.**

⛔⛔ **AND `_062`'s ENGINEER WEAKENED THE HEADLINE FROM INSIDE THE ROW**: a `held`
count may be **counting sites that had no choice.** `ph66`'s nine siblings are
*structurally unable* to face `:464`'s choice — `_zend_hash_add_or_update` takes
`arKey`/`nKeyLength` and nothing else — **so the split is a type-level fact about
one signature.**

▶ **RULE ON THE WEAKENING.** If a `held` requires the site to have **faced** the
choice, **7 of 8 is the wrong denominator** and the census needs a fourth column.
⭐ **Cheap and decisive: pick two of the seven and ask whether either COULD have
been written the defective way.** ⛔ **If both could not, the finding's positive
evidence is much thinner than it reads.**

### 7.2 Item 145 — a generator in `.temp/` with no committed twin

⭐ **Measured before being believed, and most of the item died in the
measurement.** §F6 forbids `spec.md`/`NOTES.md` from citing `.temp/`, and
`citecheck.py` enforces exactly that (`ph66` adds none). **Reports cite `.temp/`
universally** — every landed PHP report does, and **`_062` at 3 is among the
LOWEST**. ▶ **So the report-citation half is DELIBERATELY benign** (a report is a
dated narrative and naming the directory you worked in is accurate history)
**and the validator half is ALREADY ARMED** (`citecheck.py`'s `§H AT RISK` arm, 8
live hits across `ph16`/`ph29`).

⭐⭐ **WHAT IS GENUINELY UNCOVERED IS NARROWER**: a `.temp/` path holding a
**GENERATOR** — a `.py`/`.sh` that rebuilds evidence — **with no committed twin
and no validator role**, so neither arm sees it. For `_062` that is
`.temp/php66/clausetest.py` (the clause-mutation pre-check, §7.6, and it looks
**REUSABLE across R5 rows**) and `REGEN.sh`.

⛔⛔ **THE TENSION IS IN THE RULES THEMSELVES, NOT IN ANYONE'S CONDUCT**:
`CLAUDE.md` rule 1 says the `.py` probe and the logs **ARE the evidence and
stay** — in `.temp/`, which is **gitignored** — while `F51`/`F99` say a committed
document may not point at a deletable path.

▶ **RULE ON THE TENSION, NOT ON `_062`.** ⚠ **And check the premise the manager's
FIRST DRAFT of this item got wrong**: it proposed an arm that mostly already
exists, and was corrected before filing **only because `citecheck.py` was read
first**. ⛔ **Before you propose any arm in this round, check whether a tool
already reports it** (`F131`: one home per fact).

---

## §8 DEFINITION OF DONE

1. ⛔ **`.tasks-php/TASK_PHP_063_REPORT.md` EXISTS AS A FILE.**
2. **Every one of the 8 findings and 9 items you reached carries a verdict word**,
   and **CONCLUSION and REASON are scored separately, in those words.**
3. **Anything you did not reach is named explicitly** — with `§ ORDER TO RESUME
   IN` and the priority you would give it. **It will be CARRIED, not re-ranked.**
4. **Every figure you assert names the command that produced it** (**law 6**), and
   every re-gateable reading is quoted as a **dated EVENT with its commit** —
   ⭐ **and with a HISTORICAL label, because the word *"live"* undoes the date.**
5. **Every percentage owes `F108`'s five things**: STATISTIC · INPUT · OPT/MODE ·
   BASE · and if the base is a C cell, **WHICH COMPILER, with both columns or an
   explicit statement that only one was measured.**
6. **A `§ WHAT I AM UNSURE OF`.** ⭐ It is read — item 125 is a census **of this
   section across 66 reports**, and `F123` is what happens when it is ignored.
7. ⛔ **No `git add` / `git commit`** (`CLAUDE.md` rule 4). The manager commits.
8. ⛔ **No edits under `harness/`, `common/`, `patterns/`, `results/`, `pilot/`,
   `common-php/`.** ⚠ **And none to `RECAP_PHP.md` or `.memory-php/`** — those are
   manager-only for writing. **Propose; do not apply.**
9. ⛔ **`.web/` IS EDITED BY A CONCURRENT SESSION. Do not touch it, and never
   `git add -A`.**
10. **No `/tmp` scratch** — `.temp/`, a subdir per category, **keep the generator
    and delete the artefact** (`CLAUDE.md` rule 1). ⚠ **§7.2 is a round about
    exactly this; do not create its next instance while ruling on it.**
11. **`grep -a` ALWAYS** (F35).
12. ⚠ **If you change a validator, it lands with its must-fire negatives or it
    does not land** (`PROTOCOL_PHP.md` §H). ⛔ **§1 and §3.2 forbid two specific
    changes outright — re-read them before touching anything.**
13. ⭐ **COUNT IT, DON'T ASSERT IT.** ⛔ **And a CARDINALITY IS NOT A MEMBERSHIP**
    (`F132`/`F142`): if a tool prints a SET, run it for its set.

---

## §9 ⚠ THE TRAPS THIS ROUND IS MOST LIKELY TO SPRING

1. ⛔⛔ **VERDICTING THE SAME FACT IN THREE SECTIONS.** §3 is five objects and one
   question; §6 is three objects and one missing control. **One home per fact**
   (`F131`) applies to your report too.
2. ⛔ **ANSWERING A NARROWER QUESTION THAN THE ONE ASKED, AND REPORTING THE
   NUMBER.** §1's *"one grep"* and §6.3's heading spellings are both planted
   instances. **Say what your grep could not see.**
3. ⛔ **TREATING A MANAGER'S ANSWER AS SETTLED.** §3.5, §4.1 and §5.2 each carry
   an answer the manager already gave. **All three are overturnable and two of
   them say so in the protocol file itself.**
4. ⛔ **THE OBSERVABLE IS NOT `rc` AND NOT `count` — IT IS THE SURVIVOR LIST**
   (`_062` §3.1). Row 13's entire evidence base is a row where **everything exits
   0**.
5. ⛔ **`_062` §8.2 HAD TWO BULLETS AND THE MANAGER READ ONE.** **Read every
   section of this brief to its end before planning your time.**

---

⭐⭐⭐ **A CLOSING NOTE ON WHAT THIS ROUND IS FOR.** Nine rounds have refuted
something every time, and the programme's single most valuable output has been
**the conclusion/reason split**. Eight of the seventeen objects here are the
**manager's own**, five of those are **the manager about the manager**, and one
(`F146`) was filed **while this brief was being written**. ▶ **The round is not
scoped to be survivable. It is scoped to be honest about what is owed.** **Stop
where you stop, and say so.**
