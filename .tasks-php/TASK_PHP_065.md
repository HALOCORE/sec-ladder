# TASK_PHP_065 — **THE ELEVENTH REVIEW ROUND.** ⛔⛔⛔ Seven findings, and for the first time in the programme's history **every single one of them is the manager's**

**Role:** reviewer. **Programme:** PHP (`patterns-php/`). **Class:** `METH`.
**Manager:** the author of all seven findings under review, and of four of the
five items.

---

## §0 ⛔ READ THIS BEFORE PLANNING YOUR TIME

### 0.0 ⭐⭐⭐ WHY THIS ROUND IS DIFFERENT, AND IT IS NOT A COMPLIMENT TO ANYBODY

Ten rounds have run. **Nine of them refuted a manager claim.** `_064` was not
even a round — it was a promotion chore — and its engineer still filed **five
findings against my brief, four of which changed something published**, including
one where **I had ruled a discharged obligation a defect.**

⛔⛔ **This round's backlog is `F147 F148 F149 F150 F151 F152 F153`. I wrote all
seven.** Five of them were filed in a single session, about my own instruments,
using my own methods, and **two of the seven are findings about me getting a
count wrong** (`F148`, `F150`). ▶ **That is not a healthy configuration and I am
not pretending it is.** The output of this round that I value most is not a
verdict on any one of them — it is **an answer to whether a manager reviewing his
own instruments produces findings at all, or produces a genre.**

⚠⚠ **SO THE SINGLE MOST USEFUL THING YOU CAN DO IS REFUTE THE FAMILY CLAIMS.**
Four of the seven (`F147`, `F151`, `F152`, `F153`) end by asserting that several
separate scope bugs are *one mechanism*. ⛔ **`F53` is my own finding and it says
exactly this is how I go wrong**: *a shared upstream fix is not evidence of a
shared mechanism.* **I have flagged the family claim as the weak part in `F153`
myself. Do not let that flag buy it any credit — it is cheap to write.**

### 0.1 ⭐ MEASURED PREMISES — every figure below was RUN on 2026-09-18, before this file was written

⛔ **Do not trust one of them. Every line carries the command.** If a premise of
mine does not reproduce, **that is a finding and it outranks whatever section it
was in.**

| # | premise | command |
|---|---|---|
| P1 | `CHECKERS PASS`; brackets `66/0` and `28/0` | `python3 .tasks-php/checkers.py` |
| P2 | **48 rule-9 rows, 48 distinct, 7 open**: `F147 F148 F149 F150 F151 F152 F153` | `python3 .tasks-php/boxcheck.py` |
| P3 | **13 rows gated**, `9/20` families, **24 owed** to a floor of **37** | `python3 .tasks-php/quota.py` |
| P4 | law 11 today: **10 citations, 7 findings, RESTS `0` / HISTORY `5` / NOTDEP `5`** | `python3 .tasks-php/probes/scratchdeps.py` |
| P5 | `F151`'s residue: **118 citations across 35 files** — 34 row-specific, 84 inherited, 1 gone | `python3 .tasks-php/citecheck.py` |
| P6 | **13 §H-AT-RISK citations over 5 rows**: committed `controls/*.py` validators cite their must-fire negatives in gitignored `.temp/`. **All resolve TODAY** | `python3 .tasks-php/citecheck.py` |
| P7 | `F153`: **11** struck-item citations in real stdout over 12 tools; **3 defects, 8 benign** | §2 below gives the loop |
| P8 | the items header read *"143 rows, 1 → 147"*; its own check printed **`153 rows, max 157`**. ✅ **Repaired at `0454da4`** | the fenced block under `## Open items` |

⛔⛔ **P4 IS THE ONE THAT WILL CONFUSE YOU, AND I WANT IT CONFUSING YOU EARLY.**
`F150`'s title says **"17 OF 27 LAW-11 CITATIONS ARE DEFECTS OVER 14 FILES AND
13 FINDINGS"**, in the present tense, with no date. The tool it tells you to run
prints **`RESTS 0`, over 10 citations and 7 findings.** ▶ **Both are correct
about different moments** — `_064` promoted 15 files and discharged the 17 — **and
the title says which moment it means nowhere.** ⭐ `F150`'s first line does say
*"Run it, do not quote this row"*, which is a real guard. **Whether that guard is
enough for a title is §3.1's question and it is yours, not mine.**

### 0.2 ▶ THE ORDER IS BINDING: §1 → §2 → §3 → §4 → §5 → §6 → §7

**Why this order and not by severity:** §1 decides whether the *scope of this
round* is right, so it has to come before the round. §2 is the freshest finding
and therefore the softest. §3 is the big cluster. §5 is the only expensive
section and it is late on purpose — ⚠ **if you run out of time, run out of it in
§5 and SAY SO.** A section reported as NOT REACHED is worth more than a section
skimmed; `F10`'s rule, and `width.py`'s `X3` is the model.

⛔⛔ **A `VACUOUS TODAY` / `NOT REACHED` verdict is a RESULT. Returning "pass"
for a check you did not run is the one thing this programme will not forgive**
(`F135`: a known arm failure re-classified as an expected exit code).

---

## §1 ⛔⛔⛔ **START HERE: THE ARM THAT SCOPES THIS ROUND SAYS ONE ITEM, AND I CAN NAME TWO IT MISSES — ONE OF WHICH I CREATED YESTERDAY BY WRITING ENGLISH**

`F140` is `UPHELD AND UNDER-STATED`. Its deliverable was `boxcheck.ROUTE`: an arm
that reads the open-items table and prints every item routed **to a reviewer**,
so that a round's scope stops depending on the manager remembering.

**Run it:**

```sh
python3 .tasks-php/boxcheck.py      # look at the line `items -> a reviewer`
```

**It prints `1  LIVE, unscheduled: 150`.**

**Now run this** — a candidate set, which is all it is:

```sh
python3 - <<'EOF'
import sys, re; sys.path.insert(0, '.tasks-php')
import boxcheck as bc
s = open('RECAP_PHP.md', encoding='utf-8').read()
sec = s[s.index('## Open items'):]
items = re.findall(r'^\| (~~)?([0-9]+)(~~)? \|(.*)$', sec, re.M)
for st, n, _, t in items:
    if st: continue
    u = bc.unstruck(t)
    if re.search(r'reviewer', u, re.I):
        print(f'item {n:>4}  ROUTE={"YES" if bc.ROUTE.search(u) else "NO "}')
EOF
```

**24 live items mention a reviewer. The arm matches 1.**

⚠⚠ **THAT `24` IS NOT A DEFECT COUNT AND I AM NOT CLAIMING IT IS.** The arm
*correctly* declines narration — its own must-fire suite asserts that
(`probes/rule9_mustfire.py`, cases 903 and 910), and most of the 24 are sentences
like *"the reviewer measured…"*. ⛔ **An arm prints a candidate set; only a person
adjudicates one.**

**But I can name two from personal knowledge, because I wrote both:**

| item | the words in it | why the arm cannot see them |
|---|---|---|
| **154** | *"⚠ **A reviewer's, not mine, on one limb**"* | the possessive `a reviewer's` is in none of `ROUTE`'s alternatives |
| **158** | *"⚠ **(a) and (b) are a reviewer's**"* | same, **and I wrote it yesterday, in ordinary prose, with no thought of the regex** |

⭐⭐⭐ **ITEM 158 IS THE EXHIBIT AND IT IS WHY THIS SECTION IS FIRST.** `F140`'s
verdict established the arm is *not* tuned to the instance that produced it —
the reviewer back-tested WIDE and NARROW at six historical commits and they
agreed. ▶ **That settles overfitting. It does not settle RECALL**, and *"recall
measured at the only `n` an instrument has ever seen is not recall"* is that
verdict's own sentence.

### ▶ WHAT YOU OWE §1

1. **Adjudicate all 24 by unit text.** How many are genuine live routes the arm
   misses? ⛔ **Read the cell; do not pattern-match the word.** This is item 148's
   method and it cost ~25 minutes for 27 rows, so this is an hour at most.
2. **State the arm's recall as a fraction over that adjudicated population** —
   the first time it will have been measured against a population that did not
   produce it.
3. ⛔⛔ **DO NOT WIDEN THE REGEX AS YOUR ANSWER.** `F147` is *four instruments in
   eight days, each scoped to the instance that prompted it*, and widening a
   regex to catch the two spellings I happened to use this week **is that finding
   happening to you, in the round that is reviewing it.** ▶ If the honest answer
   is *"an arm cannot classify English mood and should report that it cannot"*,
   **say that** — `quota.py`'s `VACUOUS TODAY` is the model and `F10` is the rule.
4. ⭐ **And then answer the question that outranks all three: WAS THIS ROUND'S
   SCOPE WRONG?** I derived it by hand *and* by the arm and took the union. **If
   there is a routed item in the 24 that I have not put in a section below, that
   is a finding against this brief and I want it in your §1.**

---

## §2 ⭐⭐⭐ `F153` — THE FRESHEST, THEREFORE THE SOFTEST. **ATTACK IT FIRST.**

Filed **today**, hours before this brief, by me, about my own tools.

**The claim:** three committed tools print instructions to do work that is
already done; eight other struck-item citations in the same output are correct
history; **and the axis separating them is grammatical mood, not reference,
because all eleven pointers RESOLVE.**

**Reproduce it** — ⛔ **the exhibits are deliberately UNREPAIRED** (`F135`:
editing the input destroys the evidence), so you can see them live:

```sh
python3 .tasks-php/boxcheck.py  | grep -a 'item 153'
python3 .tasks-php/citecheck.py | grep -a 'item 148\|items 55/61'
```

### 2.1 The three I assert

| tool | what it prints | my verdict |
|---|---|---|
| `boxcheck.py` | `0 RESTS on scratch -> promote them: item 153` | item 153 **struck**, and the count is `0` |
| `citecheck.py` | `Adjudicate by unit text -- open item 148.` | item 148 **is** adjudicated |
| `citecheck.py` | `RECAP_PHP.md open items 55/61, not a row's debt` | **55 struck, 61 LIVE** — one pointer, two truth values |

### 2.2 ⛔ TWO OF MY EXHIBITS DIED BEFORE I FILED, AND THAT IS EVIDENCE ABOUT THE OTHER THREE

- `02-ladder.md:297` — *"open item 51 … **owed first**"*. I had it as the sharpest
  layer-level defect. **The very next line reads `✅ BOTH SENTENCES ARE NOW
  HISTORY: item 51 is closed`.** ▶ **Item 73 being obeyed, in my exhibit list.**
- `spread_stat.py:255` — *"item 52 is **still owed**"*. I called it the sharpest
  in the tree. **It is in an `else` branch and the `if` branch is the one that
  fires.** ▶ **I had inferred "live output" from the presence of `print(` on a
  line.**

⭐ **So the base rate of my exhibits in this finding is 3 of 5. Treat the three
as soft and read each citing sentence.**

### 2.3 ▶ WHAT YOU OWE §2

1. **Verify the three, by reading the citing sentence, not the grep.** Any that
   is really descriptive is a refutation.
2. ⭐⭐ **ATTACK THE MOOD AXIS — it is the load-bearing claim.** *"Every one of
   the eleven resolves, so no rot checker in this tree can see the difference."*
   ▶ **Is that true?** If any existing checker can already separate them, `F153`
   is a coverage gap and **its headline is wrong**.
3. ⛔ **Refute the family claim if you can.** `F153` argues it belongs with
   `F142` (size vs membership), `F138` (cardinality vs membership) and `F152`
   (directory vs document-kind) as *the check asks a neighbouring question and
   passes*. **I expect to lose this and said so; make me lose it.**
4. ⓘ **Item 158(a)'s three repairs are decisions, not edits.** Whether
   `open items 55/61` should drop the struck `55` or stay as history is an
   adjudication — **`F150` pre-empted exactly this kind of call on `F102` and was
   wrong.** Rule it; do not silently patch it.

---

## §3 ⭐⭐⭐ THE CENSUS CLUSTER — `F147` `F150` `F151` `F152`, PLUS ITEMS 156 AND 157

Four findings, one week, one subject: **which documents depend on gitignored
`.temp/`, and which instrument is supposed to notice.**

### 3.1 `F150` — the adjudication, and its title's tense

The ruling is **in the tool**, not the prose: `scratchdeps.ADJUDICATION`, keyed
`(finding, cited path)`.

- ▶ **The cheapest attack is the `HISTORY` bucket**: I ruled citations *not
  evidence*, and each is a judgement I made about my own prose. **Re-read the
  sentences, not the table.**
- ⛔ **One row was already wrong**: `F102` was ruled `RESTS` while its generator
  had been promoted four days earlier **under a new name**, which the basename
  resolver cannot see. Caught by `_064`'s engineer. ▶ **So ask of every ruling:
  is there a RENAMED twin?**
- ⭐⭐ **AND THE TITLE.** See §0.1's P4. **"17 OF 27 … ARE DEFECTS" is present
  tense over a population that no longer exists.** Is the *"run it, do not quote
  this row"* line enough? ⛔ **This is `F126`'s defect if it is one** — *a date
  makes a number true as history; the absence of one claims it is true now* — and
  `F126` is also mine.

### 3.2 `F151` and item 152 — the scan set that was a list where the gate has a derivation

`citecheck.py` certified **3 of 15 hashed role-classes**. The leftover it missed
is **the exact one named in the comment documenting its own previous repair**
(`ph53/verus.rs:24,350` → `.temp/php41/probe_wrap.rs`).

- ▶ **Check that identity FIRST.** If that citation is *not* the one the `F99`
  repair comment names, `F151` is an ordinary coverage gap and its headline goes.
- ⚠ **What I did NOT establish**: whether any of the 118 is a real dangling claim
  rather than a benign provenance note. **I say so in the finding — verify I say
  it loudly enough**, because `118` is the number a reader will carry away.
- ⭐ **P6 is a live, unexamined instance in this same class and it is NOT in any
  finding**: **13 committed `controls/*.py` validators cite their must-fire
  negatives in gitignored `.temp/`**, across 5 rows. `PROTOCOL_PHP.md` §H says a
  validator lands **with** its negatives. ▶ **Is §H already violated on five
  built rows, or is a resolving-today pointer good enough? Rule it.**

### 3.3 `F152` and item 156 — eight standing documents in neither census

`PROTOCOL_PHP.md` itself carries 18 `.temp/` citations, 3 already gone, and is in
neither `citecheck.CLAIMS` nor `scratchdeps.scan_set()`.

- ▶ **Attack the `n = 3` claim** — is `F147`(d) / `F151` / `F152` really one
  mechanism? **That is the only part that generalises.**
- ⓘ Item 156 rules route **(a) `citecheck.py`** right and **(b) `scratchdeps.py`**
  a category error. ⚠ **That ruling is mine and unreviewed.** If (a) is right,
  ⛔ **do not land it blind** — `PROTOCOL_PHP.md` alone adds 18 rows to a report
  already 118 lines long, which is the failure mode `F151`'s own repair just
  taught. **It needs the INHERITED/ROW-SPECIFIC split, and `citecheck.py` is
  filed `expect=1` so a new class must not touch `rot`. Copy `N7f`.**

### 3.4 `F147` and item 157 — the instrument-per-instance claim, and what `RESTS = 0` means

- ▶ **The falsifiable part is law 11's `F88–F101` capturing 5 of 22.** Re-derive
  it; do not read it out of the finding.
- ⛔ **Row 4 of that table is mine and is not exempt**: `scratchdeps.py` resolves
  by basename, cannot tell a probe I wrote from upstream source I extracted, and
  scans two document families. **The pattern predicts a row 5 and you should try
  to be it.**
- ⭐⭐ **Item 157 is the honest reading and it is the sentence I most want
  checked**: ***`RESTS = 0` means every citation the tool CAN SEE is discharged,
  and the tool's RECALL IS UNMEASURED.*** Three citation spellings, one repaired:
  **(a)** bare filename ✅ fixed; **(b)** rename ⛔ not fixed; **(c)** brace
  expansion ⛔ not fixed — `PATH_RE` reads
  `.temp/mgr168/{item48_decide,enclosing_fn,spread_axis,sha_norm}.py` as a bare
  directory and discards it, so **four citations register as zero**, and one of
  them is the probe `F69`'s published `24 of 30` rests on.
- ▶ **The measurable question, and it is an hour**: expand every brace citation by
  hand, re-run, **report how many NEW law-11 rows appear.** ⛔ **Do not widen the
  regex and declare victory.**

---

## §4 ⭐⭐ `F148` — *a `grep -c` over hard-wrapped prose fails in BOTH directions*

⚠ **`n = 4` and the finding says so**: two identifier probes right, two prose
probes wrong, verified by reading the matched line. **The other six probes that
session were never checked and are NOT evidence.**

- ▶ **The rule it proposes — *never grep prose to decide presence; grep an
  IDENTIFIER or read the section* — would forbid checks this programme runs
  constantly.** So **the scope clause is the load-bearing part**: *locating* text
  is fine, *asserting absence* is not. **Attack there.**
- ⚠ It claims to supersede `NULLCTL_001.md` §10's *"use a short unwrappable
  token"*, on the ground that my own `coin flip` homonym refutes it. ▶ **Check
  that the supersession is real and not a restatement.**
- ⭐⭐ **AND `F148` HAS A SECOND VICTIM I FOUND TODAY, IN §2.2**: I inferred
  *live output* from `print(` appearing on a source line, without asking which
  branch runs. ▶ **Is that the same finding or a different one?** It is not a
  `grep -c` and it is not prose — **it is inferring behaviour from syntax.** If it
  is different, `F148`'s scope clause is narrower than it reads and **you should
  say what the wider family is.**

---

## §5 ⚠ `F149` AND ITEM 151 — THE `O0` SWEEP. **THE ONLY EXPENSIVE SECTION, AND IT IS LAST ON PURPOSE.**

⛔ **Cost, measured: ~20–25 min per row per input at 32 pads.** Budget before you
start, and **if you cannot afford it, report `NOT REACHED` and stop** — do not
run a 4-pad screen and report a verdict, **because that is the exact error the
finding is about.**

### 5.1 ▶ CHECK THE CONTROL FIRST — if it is wrong, everything below it is

All four of `ph66`'s published `O0` family-B numbers are claimed to reproduce **to
the digit at BOTH pad resolutions**, so `OPT-5` is pinned to a committed figure
and not to its own output. **Verify that before anything else.**

### 5.2 The claim

```sh
python3 .tasks-php/php50_align_sweep.py --opt O0 \
        --row ph66-hashdel-uncompared --pads 32
```

⛔ **The `large`/gcc cell is the whole finding**: alignment step `8.89` against an
effect of `6.12`, so `|d|/step = 0.69` and **the sign is not established.**

### 5.3 ⭐⭐ ATTACK (b) HARDEST — IT IS MUCH BIGGER THAN THE ROW

I claim a **4-pad screen returned the OPPOSITE verdict on BOTH axes** for that
cell (`RESOLVABLE` / `SIGN-STABLE`, range `0.00`). ▶ **If that is true, every
sparse sweep in this tree is suspect for a DIFFERENCE** — and that is a far larger
claim than the row it is about. **A sparse screen is complete for a CELL and not
for a DIFFERENCE.**

### 5.4 ⓘ Item 151, and what it must NOT become

`ph66`'s `NOTES.md:345-346` summary needs correcting and **`NOTES.md` is in
`source_sha256`, so it costs that row a RE-GATE** — batch it, do not do it here.
⚠⚠ **AND DO NOT LET THIS BECOME A LICENCE TO PUBLISH `O0` MAGNITUDES.**
`.memory-php/03-numbers.md` stands: `--opt` buys a **SIGN** only, labelled a
lowering reading, and only if swept.

---

## §6 ⚠ ITEMS 150 AND 154 — THE TWO I AM BARRED FROM SETTLING

### 6.1 Item 150 — a task's worth of work with no task number

`PROMOTE_001` was a dispatched subagent with a brief, a 406-line report, ~20
minutes and 110 tool calls, and **`task_cost.py` prices it at ZERO** because the
ledger is keyed on `TASK_PHP_NNN`. Every published figure (`marginal 2.38`,
`PUBLISH ~57..~72`) is computed without it.

⛔ **I must not settle this: it prices my own work.** `_057`'s engineer refused
exactly this shape and was right.

▶ **The question: should a dispatched chore be NUMBERED, or should the ledger
learn a second namespace?** ⚠ Numbering needs no tool change but makes every
promotion a task file. ⓘ **Do NOT retro-number `PROMOTE_001`** — moving a
denominator under a published range is `F126`'s defect.
⚠⚠ **`n = 1`, and `n = 1` is not a rate.** The other 12 unnumbered documents are
**not** evidence for this and I do not claim them.

### 6.2 Item 154 — review status for pre-`F107` findings is not derivable

`boxcheck.rule9_rows` parses **48 rows and none of `F44 F50 F53 F70 F72 F73 F74
F85 F89 F90 F95 F100 F102`**, because the `_047`-era block uses a **grouped
verdict cell** the parser cannot read.

⛔⛔ **And the two homes contradict each other today**: `F102`'s section says
`⚠ UNREVIEWED (rule 9)` while the `_047` block files it `UPHELD-NARROWED`.

▶ **Three routes, and I have not chosen:** (a) reformat the `_047` block to one
row per finding; (b) teach `rule9_rows` the grouped cell; (c) make `boxcheck`
**say** it cannot answer rather than printing a count that silently excludes 13
findings. ⭐ **(c) is cheapest and most honest and it is `F10`'s rule — but it
leaves the `F102` contradiction standing, so (c) does not dismiss (a).**

⚠ **One limb is yours and one is not**: the measurement is mine and reproducible;
**the route is a decision, and I am the author of the count that was wrong.**

---

## §7 ⚠ ITEM 155 — THREE PROMOTED PROBES ASSERT NOTHING, AND ONE IS THIS PROGRAMME'S OWN CAUTIONARY TALE

`PROTOCOL_PHP.md` §H: a validator change lands **with its must-fire negatives or
it does not land**. These arrived as *promotions* of pre-existing scratch, so §H
never gated them.

⛔ **`count_ent.py` is the sharp one**: `F44` rests on its four-table result, and
**`F50`, `F51` and `F52` each cite it as an example of a probe whose SETUP
ENCODED ITS ANSWER.** ▶ ***A probe the corpus quotes three times as a cautionary
tale, now committed, asserting nothing.***

⭐ **The check that works on this class is already written down** (`F52`): **change
the setup's arbitrary constant and see whether the verdict moves.**

⚠⚠ **SIZING, AND DO NOT BATCH THESE:** three probes × (one negative that must
fire + one that must not) **is an hour**. ⛔ **`F53`'s nine-commit corpus has NO
committed generator at all** — only two of the nine commits are named anywhere —
**and re-deriving it IS a task.** Item 125 sat six rounds behind an hour-shaped
number; do not repeat that.

---

## §8 DEFINITION OF DONE

Write `.tasks-php/TASK_PHP_065_REPORT.md`. It is done when:

1. **Every one of the seven findings carries a verdict, scored CONCLUSION and
   REASON separately.** ⭐ This programme's rounds routinely uphold a conclusion
   and refute the reason that argued it; **that split is the product.**
2. **Each verdict states what may enter `.memory-php/` and what may not**, in the
   rule-9 table's own vocabulary (`UPHELD` / `UPHELD-NARROWED` / `REFUTED` /
   `UPHELD, REASON REFUTED`). ⛔ **You do not edit `.memory-php/` or
   `RECAP_PHP.md` — those are manager-write-only. You write the verdict; I apply
   it.**
3. **§1's recall fraction is stated over an adjudicated population**, or §1 says
   why it could not be.
4. **Every premise in §0.1 you relied on is re-derived**, and any that failed is
   reported as a finding against this brief.
5. **Anything NOT REACHED is named as NOT REACHED**, with what it would have cost.
6. **Your own findings are filed as findings**, numbered `R1, R2, …` in your
   report. `_064`'s engineer filed five against my brief and four changed
   something published — **that is the benchmark, not an anomaly.**
7. ⭐ **A closing section: DID THIS ROUND'S SCOPE COME FROM THE RIGHT PLACE?**
   Seven manager findings reviewed by one reviewer is a configuration, not a
   process. **Say what you think it is producing.**

---

## §9 ⚠ THE TRAPS THIS ROUND IS MOST LIKELY TO SPRING

1. ⛔⛔⛔ **NEVER INFER AN ABSENCE — OR A PRESENCE — FROM A CLI's SHAPE, A
   `grep -c`, OR A REGEX OVER PROSE. RUN IT.** Two of my exhibits died to this
   **today**, in the finding about it.
2. ⛔ **AN ARM PRINTS A CANDIDATE SET; ONLY A PERSON ADJUDICATES ONE** (`F132`).
   If a count appears in your report, say what its unit is and who read them.
3. ⛔ **`grep -a` ALWAYS** (`F35`) — this tree has files `grep` calls binary, and
   the most-cited one is among them.
4. ⛔ **A validator change lands with its must-fire negatives or it does not
   land** (§H). **And a validator change must not land in the same commit as the
   data it is measured against** (`_063`).
5. ⛔ **Do not "repair" a `.temp/` citation by committing the artefact.** A `.log`
   under `.temp/` is deletable by constraint 6; **the repair is to drop the
   pointer or re-ground it.**
6. ⛔ **No `/tmp` scratch — use `.temp/`**, a subdir per category. **Keep the
   generator, delete the artefact.**
7. ⛔ **You do not run `git commit` or `git add`**, or any history-mutating git
   command. Read-only git is expected and encouraged.
8. ⛔ **Do not edit `harness/`, `common/`, `patterns/`, `results/`, `pilot/` or
   `common-php/`** — the PAT side is hash-pinned infrastructure. **And do not
   touch `.web/`**: a concurrent session owns it.
9. ⚠ **`.memory-php/` supersedes any task report it contradicts** — including
   this brief. If I have written something here that the layer refutes, **the
   layer wins and that is a finding against me.**
10. ⭐ **Item 73**: a correction goes IN PLACE OF a stale claim, never BESIDE it.
    **Three of my findings this week exist because I appended instead of
    replacing.**
