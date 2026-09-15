# TASK_PHP_059 — **THE EIGHTH REVIEW ROUND.** ⭐⭐⭐ `F129` redefines what every `inside_share` figure in this programme *means*, and one clause of it may delabel the entire cross-language column

**Role:** research **reviewer / analyst**. **One agent, alone.**
**Report:** `.tasks-php/TASK_PHP_059_REPORT.md` — **write the FILE** (`PROTOCOL.md`
rule 10). A report that exists only in your final message does not exist.

⚠⚠⚠ **YOUR JOB IS TO FALSIFY, NOT TO CONFIRM.** `.memory-php/04-process.md`
**law 12**: *a manager finding from one probe or two rows should be assumed
narrowable until a reviewer has had it.* ⛔ **Three of the four findings below
are MANAGER findings, and two of those are the manager about the manager.**
Count them yourself in `RECAP_PHP.md`'s RULE-9 table — read the rows whose
verdict column opens `⛔ UNREVIEWED`, and do not trust this sentence.

⭐⭐⭐ **THE STANDING RECORD, SO YOU KNOW WHAT NORMAL LOOKS LIKE.** **Seven
consecutive review rounds have refuted manager or engineer claims.** At `_053`
**not one finding survived as written**. At `_055` **three of four conclusions
survived and ZERO of four REASONS did**. At `_058` **zero of five manager
predictions survived as written** — and *three of the five split, with the
conclusion and the reason failing in OPPOSITE directions.*

> ▶ **SO: SCORE THE CONCLUSION AND THE REASON SEPARATELY, EVERY TIME, IN THOSE
> WORDS.** A finding whose conclusion holds on a ground you had to invent for it
> is **UPHELD-ON-NEW-GROUND**, not UPHELD, and that distinction has been this
> programme's most valuable single output for five rounds running.

---

## §0 ⛔ READ THIS BEFORE PLANNING YOUR TIME

Four findings. **That is a third of `_057`'s load and it is deliberate** — the
backlog was allowed to grow to thirteen once and the round that cleared it said
so in terms. ⭐ **This round is small enough to go deep, and going deep is the
instruction.**

▶ **THE ORDER IS BY STAKES AND IT IS BINDING: §1 → §2 → §3 → §4.**

⭐⭐⭐ **STOPPING CLEANLY IS A FIRST-CLASS OUTCOME.** If you run out of depth,
**STOP AND SAY WHERE.** A report that verdicts §1 properly and says *"I did not
reach §4"* is worth more than one that touches all four shallowly — and the
second kind is how a round produces confirmations instead of verdicts.

⛔⛔ **AND YOUR STATED PRIORITY BINDS THE MANAGER. `F123` IS WHY.** An engineer
wrote *"it is the cheapest remaining check and it is not done"*; the manager's
next task file demoted it to *"nice to have, skip it"*; two rounds later the
protocol treated it as **impossible**, and it turned out to cost **30 seconds**.
▶ **Write a `§ ORDER TO RESUME IN` naming what is left AND the priority you
would give it. It will be CARRIED, not re-ranked.**

### 0.1 ⭐ MEASURED PREMISES — every one of these was RUN before this file was written

`PROTOCOL.md` **rule 14**: *run the premise before you write it into a task
file.* ⛔ The last time the manager priced a task without measuring it, the
estimate was right **by luck** and the item existed because of `F123`. Each row
below names the command that produced it, **run at `f98e716`**.

| premise | command | measured |
|---|---|---|
| the ratchet is green **and now actually enforcing** | `python3 .tasks-php/cbaseline_check.py` | `scanned 31 file(s); 77 hit(s); ratchet 77`, **rc 0**, **0.13 s** |
| the whole checker registry passes | `python3 .tasks-php/checkers.py` | `CHECKERS PASS`, **24 filed / 24 on disk**, **35 s** |
| `F74`-share **per published pair** already exists as a tool | `python3 .tasks-php/php58_record_share.py --pairs` | 11 rows, **198 pairs**, `O3`/`isolated` **only**, rule **(ii) only**, **0.25 s** |
| the full `F74`-share matrix | the same script with no flag | every cell of every row that carries a `kernel_exclusive_ir` |
| both staleness brackets | `python3 harness/measure.py --check-stale`, then the php one via `harness-php/gate.py` with `--tool measure --check-stale` | **`66 / 0 STALE`** and **`24 / 0 STALE`** |
| `F130`'s history claim is checkable | `git show 1cc2c0e:.tasks-php/cbaseline_check.py` | `RATCHET = 69` at line 201; enforcement behind `if '--ratchet' in argv` at line 248 |

⭐ **Nothing in this round needs a re-gate, a rebuild or a measurement run.**
Every number you are asked to attack is arithmetic over **committed records**.
A `callgrind` run, if you want one for a second method, cost **6.6 s** on the
heaviest cell measured (`ph03`/`safe_naive`-`O3`-`isolated`, `large.bin`).

---

## §1 ⭐⭐⭐ `F129` — THE HIGHEST-STAKES UNREVIEWED FINDING IN THE PROGRAMME

`RECAP_PHP.md` → the `F129` section. Read it, then read `TASK_PHP_058.md` and
`TASK_PHP_058_REPORT.md`, then `.memory-php/03-numbers.md`'s `inside_share`
section and `.memory-php/02-ladder.md`'s statement of `F74`'s bar.

⚠⚠ **THE SITUATION LAW 12 IS SHARPEST ABOUT.** The manager **re-derived every
load-bearing number in `F129` from the committed records with independent code**
before landing it. ⛔ **That is VERIFICATION, NOT REVIEW. Nobody has yet asked
whether the CONCLUSIONS FOLLOW FROM the numbers.** ▶ **Attack the inferences.
Re-deriving the arithmetic a third time is the cheapest way to waste this round.**

`F129` makes **five separable claims**. Verdict them separately.

### 1.1 The name collision — *"two quantities wear the name `inside_share`"*

The claim: `F74`'s share is `(kernel_exclusive_ir / n_iters) / marginal_ir_per_call`;
the control's `W` share is `kernel exclusive Ir / callgrind whole-run total Ir`;
on `ph29` `c-gcc`/`small.bin` they read **0.8045** and **0.8933**.

- ⭐ **The attackable clause is the CORPUS one, not the arithmetic**: *"EVERY
  `inside_share` figure in `RECAP_PHP.md`, in `.memory-php/03-numbers.md` and in
  `ph29`'s `controls/spellings.py` is `F74`'s."* ▶ **Did anyone CHECK every
  figure, or a sample?** Enumerate them and say how many there are. **If one
  published figure is the `W` one, the finding's headline changes shape.**
- ⚠ Its supporting tell — that `03-numbers.md`'s *"IS ALREADY COMPUTED FOR EVERY
  CELL IN EVERY RECORD"* is true of `F74`'s and false of the control's — is an
  **inference about what a sentence meant when it was written.** ▶ Is there a
  reading on which it was always about the `W` one? Check the date and what
  existed then.
- ⓘ **Second method available and cheap**: compute both shares on one cell
  **without either shipped tool** — the record fields and one `callgrind` run.

### 1.2 The `+33 %` and its sign flip

| | A1 vs `safe_naive` | W1 |
|---|---|---|
| **`c-gcc`** | `+33.01 %` | `−0.80 %` |
| **`c-clang`** | `−4.36 %` | `−27.54 %` |

(`ph29`/`large.bin`/`O3`/`isolated`.)

- ⓘ The manager already **corrected his own over-claim here** before anyone saw
  it: `c-clang`'s `−4.36 %` is **not new** — `_049` filed it 2026-09-13 in
  `.memory-php/02-ladder.md` and in this file's item 111. ▶ **Check that
  correction is itself correct**, and that the residual claim — *a correction
  reached the authoritative layer and the headline cell never inherited it* — is
  what the git history actually shows.
- ⛔ **Is `+33.01 %` really the number `RECAP_PHP.md` publishes?** Same cell,
  same input, same opt/mode, same base, same pair? **A finding that delabels a
  sentence must be about THAT sentence.**

### 1.3 ⭐⭐⭐ THE ADMISSIBILITY VERDICT — **THE CLAUSE THIS ROUND EXISTS FOR**

`F129` §3 says the published comparison is **INADMISSIBLE on the row's own
written bar**, not merely under-qualified: `.memory-php/02-ladder.md` states
`F74`'s corrected **two-condition** bar — **(i)** `min(inside_share)` HIGH
**and (ii)** `|Δinside_share| ≤ 0.02` — and the published pair's Δ is **0.2355**,
more than **eleven times** the bar.

⚠⚠⚠ **IF THAT READING IS RIGHT IT DOES NOT STOP AT ONE SENTENCE.** Here is a
manager observation, registered so you can attack it rather than inherit it:

> ⭐⭐ **MANAGER OBSERVATION, 2026-09-15 — UNVERIFIED, ONE TOOL, ONE TALLY.**
> Tallying `php58_record_share.py --pairs` across all **11 rows / 198 pairs**
> (`F74`'s spelling · `O3`/`isolated` only · rule **(ii)** only · `small.bin` and
> `large.bin` pooled):
>
> | pair class | PASS (ii) | FAIL (ii) | admissible |
> |---|---|---|---|
> | **cross-language** (a `c-*` cell vs a Rust cell) | **17** | **71** | **19.3 %** |
> | **same-language** (everything else) | **99** | **11** | **90.0 %** |
>
> ⛔ **PRODUCED BY AN UNCOMMITTED SHELL ONE-LINER OVER THE TOOL'S STDOUT.** That
> is `CLAUDE.md` rule 1's own trap — evidence with no committed generator — and
> it is **said rather than smoothed over.** ▶ **RE-DERIVE IT. DO NOT CITE MINE.**

▶ **THE QUESTION, AND IT CUTS BOTH WAYS:**

- **(a)** If `F74`'s bar is a **publication gate**, then **roughly four fifths of
  this programme's cross-language comparisons are inadmissible on a rule the
  authoritative layer already carries** — including the headline. `F129` is then
  far bigger than it claims, and the programme owes a re-statement.
- **(b)** If the bar is **narrower than that** — a condition for treating `A1` as
  a *proxy for total cost*, or a condition for `A1` and `W1` to *agree*, rather
  than a gate on publishing a labelled `A1` figure — then **`F129`'s own key
  added clause over-applies it**, and the right verdict is UPHELD-NARROWED with
  the word *"inadmissible"* withdrawn.

⭐⭐⭐ **SETTLING (a) VS (b) IS THE MOST VALUABLE THING THIS ROUND CAN DO.** Read
`F74`'s body, `.memory-php/02-ladder.md`'s statement of the bar, and
`.tasks-php/STATISTICS_001.md` — **which is the whole argument for the
publish-both-labelled rule and is committed.** ⚠ Note that `STATISTICS_001.md`
says `inside_share` *"explains a disagreement and never gates one"*. ▶ **If that
sentence is right, reading (b) wins and `F129` §3 is narrowed by a document the
manager cited in the same session and did not apply.** ⛔ **Do not take my word
for that either — it is the hypothesis, not the verdict.**

#### 1.3a ⭐ ITEM 132 IS FOLDED IN, BECAUSE §1.3 IS **NOT DECIDABLE WITHOUT IT**

`F74`'s bar is a **conjunction**, and only conjunct (ii) has a number.
`.memory-php/02-ladder.md` says (i)'s threshold is *"not tuned and **six rows
cannot pin it**"* — `>0.3`, `>0.5`, `>0.6` all gave 0 flips. ⭐ **There are
ELEVEN rows now and 360 evaluable cells.**

▶ **You cannot verdict a conjunctive bar knowing one conjunct.** If (i) also
fails on the disclaimed pairs the verdict is over-determined; if (i) is strongly
met, (ii) alone carries it, and the size of the margin is the finding.

- The sweep **reads committed records and builds nothing** (0.25 s).
- ⚠⚠ **DO IT IN `F74`'s SPELLING, NOT THE CONTROL's.** They are different
  quantities — that is `F129` §1 — and **pinning the threshold of the wrong one
  would be worse than leaving it open.**
- ▶ If the honest answer is *"eleven rows still cannot pin it, and here is why"*,
  **that is a result**, and item 132 closes on it.

### 1.4 The over-`1.0` cells — a share of the whole that exceeds the whole (item 133)

**15 of 360 cells** exceed `1.0` under `F74`'s definition; largest is `ph07`
`c-gcc`/`large` at **`1.0353`**; they concentrate in `ph07` and `ph16` at
`O3`/`isolated`. ✅ Manager-reproduced independently as exactly 15.

⭐⭐ **THE SHARPEST SINGLE DATUM**: `ph16` `c-gcc`/`isolated`/`small.bin` — **same
row, same cell, same input** — reads **`0.0418` at `O0`** and **`1.0241` at
`O3`**. A **24× swing**, from *A1 sees almost nothing* to *A1 sees more than the
whole*, **moved by the optimisation level alone.**

- ⛔⛔ **NOBODY HAS PROPOSED A MECHANISM ON THE RECORD, DELIBERATELY.** The
  engineer declined; the manager declined. The candidate — numerator over
  `n_iters` calls against a denominator that is a **slope** at
  `collapse.probe_iters` — is *consistent with the arithmetic and NOT isolated*,
  and could equally be a start-of-run transient (`F93`'s shape).
- ▶ **THE CHEAP DISCRIMINATOR, already named: recompute the marginal at
  `n_iters` on one offending cell.** If the share drops under 1.0, the slope
  explanation survives; if it does not, it is something else.
- ⭐⭐ **THE STAKES: this quantity DECIDES WHICH STATISTIC MAY PUBLISH, and it is
  out of range on 4 % of the corpus.** A bar computed from a quantity that
  violates its own definition on 4 % of cells is not obviously a bar.

### 1.5 The two cheap clauses — verdict them, briefly

- **§5, *"the repair shipped the defect it repairs"***: the new control's
  docstring introduced both quantities and then wrote *"the two read 80.45 % and
  89.33 %"* — **two bare unlabelled numbers, in the one sentence whose purpose is
  to stop two quantities being confused**, in the order a reader would most
  likely map them **backwards**. ▶ Read the repaired docstring in the four rows
  that share it. **Is it now right, and is it right in all four?** (The file is
  byte-identical across them — one `sha256` — so a difference is itself a
  finding.)
- **§4/§4a, the prediction score**: *zero of five survived as written.* ▶ **Is
  the scoring honest, or generous to itself?** ⭐ Manager self-scoring is exactly
  where a reviewer earns the round, and `P2`'s *"right reason that does not
  entail its conclusion"* is the interesting one.

---

## §2 ⭐⭐⭐ `F130` — A RATCHET THAT NOTHING EVER INVOKED

The claim: `cbaseline_check.py` is `F108`'s enforcer and the house *"adjudicate
every hit BY HAND; never tune the regex"* ratchet — **and its enforcement sat
behind `if '--ratchet' in argv` with no caller passing it.** Measured against a
worktree at `1cc2c0e`: **70 hits against a ratchet of 69**, with no run anywhere
that would have said so.

- ✅ **The history is checkable in one command** (§0.1). Do that first.
- ▶ **Then ask what the finding does NOT say.** *How long had it been un-run?*
  The ratchet has been raised before, by hand, with adjudications. **Was
  enforcement ever wired, and did something unwire it — or was it never wired?**
  `git log` on that file answers it, and the answer changes whether this is a
  regression or a birth defect.
- ⛔ **ONE of the 70 hits at `1cc2c0e` was ALREADY unadjudicated and the manager
  did NOT chase it.** Said plainly in the finding rather than smoothed over.
  ▶ **Chase it.** *"The ratchet is honest again from 77, not retrospectively"* is
  a claim about a number nobody has decomposed.

### 2.1 The eight new hits — **are they really all benign?**

The finding adjudicates eight and calls them all benign, two informative. ▶ **Do
your own adjudication of all eight and say where you disagree.** The two the
manager flagged:

- `ph29` `NOTES` line 1145 **quotes the defective `RECAP` sentence in order to
  criticise it** — a quotation of a defect scoring as the defect. Item 115's
  class, *a check that reads prose and calls it code*, **seventh instance**.
- ⭐⭐ `ph29` `NOTES` line 1157 **names BOTH C columns and is flagged anyway**,
  because it writes them `gcc-C` / `clang-C` while `BASE` matches only `c-gcc` /
  `c-clang`. ⛔ **The checker flags the one line in the corpus that obeys its
  rule BEST, because of a spelling.**

### 2.2 ⚠⚠ ITEM 134 — `BASE` ENFORCES FOUR FIFTHS OF THE RULE IT EXISTS FOR

`.memory-php/03-numbers.md` states `F108`'s fifth thing as *"WHICH COMPILER —
**with both columns, or an explicit statement that only one was measured.**
⛔ One column is not a number with error bars on it; it is a DIFFERENT SIGN."*

⛔ **But `scores()` is `MAG and XLANG and not BASE`, and `BASE` matches `c-gcc`
OR `c-clang`** — so a sentence naming **either** is deemed labelled. ⭐⭐ **And
its `N2` arm, the exemplar it holds up as *"a correctly labelled claim"*, is the
`+33.01 %` sentence — ONE column, of the very pair whose columns have OPPOSITE
SIGNS.** The enforcer's model of compliance is one item short of the rule it
enforces.

✅ **Scope was measured before the item was opened, and it is small**: of the
scanned corpus **5 lines name BOTH C columns and 2 name exactly one**, and **both
of those two are fine on inspection**. ⛔ **So there is no live violation — the
finding is that nothing would have caught one**, plus the artefact that a
**line-based** scan cannot see a claim whose two columns are one sentence apart.

▶ **THE RULING OWED, AND IT IS A REAL TRADE:** the standing note has refused to
widen `BASE` **seven times**. ⭐ **The eighth instance cuts the other way** —
`F130` found `BASE` flagging a *compliant* line and passing a *non-compliant*
one, in the same run. ⚠⚠ **Widening it WILL move the `RATCHET` count. That is
what a ratchet is for** — every new hit is adjudicated BY HAND, **never
regex-tuned.** ▶ Rule on it: widen, or refuse an eighth time **with the reason
stated in terms of these two hits**.

---

## §3 `F127` — the reviewer finding `_058` was built to test

⚠ **LAW 12 CUTS THE OTHER WAY HERE.** `F127` is a **reviewer** finding, and an
**engineer** task tested it directly. ▶ So the question is not *"is the manager
over-claiming"* but **"did `_058` actually test what `F127` claimed, and did it
close it?"**

- ✅ `_058` measured `ph03`, `ph16`, `ph29` and rewrote `ph97`'s template
  byte-identical across four rows; four rows re-gated PASS.
- ⛔ **THE ITEM IS NOT CLOSED: `ph07`, `ph53` and `ph64` still have no measured
  share.** ▶ **Was the scoping right?** The reviewer named the three rows that
  publish an `A1` headline; the manager dispatched those three. **Is *"publishes
  an A1 headline"* the right selector, or does a row with no headline still owe a
  share because the bar in §1.3 needs one?** ⭐ **If §1.3 lands on reading (a),
  the residue stops being bookkeeping and becomes load-bearing.**
- ⚠ `F127`'s own text was corrected by `F129`: *"exactly that comparison"* is
  **one rung off** — the docstring disclaims C vs `safe_tuned`, the headline
  publishes C vs `safe_naive`. ▶ **Does the correction weaken `F127` or
  strengthen it?** The manager says stronger. **Check.**

---

## §4 `F128` — the arm that asserted an effect's sign, and the sweep that narrowed it

⚠ **A manager self-finding, narrowed by a manager sweep the same day. That is
not a review, and its RULE-9 row now says so.** Cheapest section; do it last.

- ✅ The `N13` defect is real and repaired; a **third** instance (`N5`) was found.
- ⛔⛔ **`F128`'s rule AS WORDED is WITHDRAWN — too broad: applied literally it
  damages FIVE CORRECT ARMS.** ▶ **Is the replacement right?** The **Kind
  A / Kind B** rule: an arm MAY assert a direction when the direction is a
  **published finding it exists to defend** — and then **must print the measured
  margin beside the floor** — but must NOT assert a direction still being
  **estimated**, where the opposite outcome is a legitimate RESULT.
  ⭐ **Attack the boundary.** *Published* and *being estimated* are not disjoint:
  `F126` refuted a published premium at n = 8. **What happens to a Kind A arm
  when the finding it defends is refuted?**
- ⛔ **SIX CHECKERS WERE NEVER SWEPT** — the sweep covered four files and skipped
  `cbaseline_check.py`, `quota.py`, `citecheck.py`, `contract_audit.py`,
  `preimage_screen.py` and `fixsurvey.py`, which use a different arm spelling.
  ⭐⭐ **`cbaseline_check.py` is in that list, and §2 is about it.** ▶ **Sweep at
  least that one**, and say whether the residue is worth a task.
- ⓘ The sweep's own census **miscounted first** (60/17, from a `grep` that read a
  `check("N15b"…` quoted INSIDE a comment; recounted 59/16). **Item 115's class,
  inside the sweep hunting item 115's class.** ▶ Spot-check the recount.

---

## §5 THE MANAGER'S PREDICTIONS, REGISTERED — **score every one**

⛔ **Last round these scored ZERO OF FIVE.** They are registered so the round has
something to refute, not because they are likely right.

| | prediction | confidence |
|---|---|---|
| **P1** | §1.1's name collision survives **as written**. It is a definitional fact, not an inference, and definitions do not narrow. | high |
| **P2** | ⭐⭐⭐ §1.3 lands on reading **(b)**: `F74`'s bar is a condition for trusting `A1` as a proxy, **not a publication gate**, so *"inadmissible"* is withdrawn and `F129` §3 is **UPHELD-NARROWED**. | **low — I am predicting against my own finding's strongest clause** |
| **P3** | Item 132 will find that **no threshold for (i) in `[0.3, 0.9]` changes any cross-language verdict**, because (ii) already fails on ~81 % of them — i.e. **(i) is not load-bearing for the cross-language column**, and that is why eleven rows still cannot pin it. | medium |
| **P4** | The over-`1.0` mechanism **will be isolated** by the cheap discriminator and **will be** the `n_iters`-vs-`probe_iters` slope, not a transient. ⚠ **Registered deliberately, and it does NOT violate item 133's *"do not quote the mechanism as measured"*** — a registered prediction is the opposite of a measurement: it exists to be refuted. | medium |
| **P5** | Item 134 will be judged **WORTH DOING** — the standing seven-time refusal to widen `BASE` flips on the eighth instance, because this one shows it failing in **both** directions at once. | medium |

▶ **If you refute one, say which clause and on what evidence. If one survives,
say so plainly — a round that refutes everything is as suspicious as one that
confirms everything.**

---

## §6 TRAPS

1. ⭐ **`grep -a` ALWAYS.** `F35`. Several files here trip binary detection and
   `grep` silently reports nothing rather than failing.
2. ⛔ **DESCRIBE A COMMAND OR PATH, DO NOT SPELL IT.** Brace expansion in a task
   document has produced `citecheck` rot **seven times**, and **three of those
   were created by a document warning about it.** Name the directory and the
   file in prose.
3. ⚠ **Quote a re-gateable reading as an EVENT, never a STATE** — *"read at
   `f98e716`"*, not *"the value is"*. Records change under you; a dated reading
   never goes stale, it just gets old.
4. ⛔⛔ **YOU NEVER RUN `git commit` OR `git add`** — `CLAUDE.md` rule 4. Read-only
   git is fine and you will need it. The manager commits at task boundaries.
5. ⛔⛔ **DO NOT EDIT ANYTHING UNDER `patterns-php/`. REPORT IT INSTEAD.** The
   shared `inside_share` control is hashed into **four** rows' `source_sha256`;
   touching it costs **four re-gates** at ~2 m 30 s each. You may repair tools
   under `.tasks-php/`. ⚠ **If you repair one, re-run the registry.**
6. ⛔ **No edits to `harness/`, `common/`, `patterns/`, `results/`, `pilot/` or
   `common-php/`** — the PAT side is frozen infrastructure hashed into 33 gate
   records.
7. ⛔ **No `/tmp` scratch.** Use `.temp/`, a subdir per category. **Keep the
   generator, delete the artefact** — if a number you report has no committed
   script that rebuilds it, **say so**, which is exactly what §1.3's manager
   observation does.
8. ⚠ **A count in prose ABOUT a tool rots exactly like one inside it** (`F121`).
   If you state *"N arms"* anywhere, derive it from what the tool PRINTS.
9. ⭐⭐ **WRITE A CORRECTION IN PLACE OF A STALE CLAIM, NEVER BESIDE IT.** Three
   instances in one day; the RULE-9 table had **six** at once. If you find a
   stale sentence in your own draft, **replace it**.
10. ⚠ **`.memory-php/` and `RECAP_PHP.md` are MANAGER-ONLY for writing.** Quote
    them, cite them, refute them — do not edit them.
11. ⚠ **`.web/` is edited by a concurrent session.** Do not touch it, and never
    `git add -A`.
12. ⛔⛔⛔ **NEVER REFUSE OR REMOVE A PATTERN FOR A RUST-SIDE, VERUS-SIDE OR
    LADDER-SIDE REASON.** Admission is decided **solely on the C program**.
    *"Safe Rust can't express it"*, *"no column moves"*, *"Miri doesn't see it"*,
    *"the R5 can't state the obligation"* are **ALL FINDINGS, NEVER KILLS.**

---

## §7 DEFINITION OF DONE

1. **Every claim scored CONCLUSION and REASON SEPARATELY, in those words.**
2. **Each verdict names its SECOND METHOD** — or says plainly there was none, and
   why. *"I re-ran the manager's tool"* is not a second method.
3. **Every percentage pays `F108`'s five things**: STATISTIC · INPUT · OPT/MODE ·
   BASE · and if the base is a C cell, **WHICH COMPILER — with both columns, or
   an explicit statement that only one was measured.**
4. **A `§ WHAT I AM UNSURE OF` section**, with every cost either **measured** or
   **explicitly labelled an estimate**. ⭐ `F123`: an engineer's own estimate of a
   check's cost is evidence, and this section is the one that gets demoted.
5. **A `§ ORDER TO RESUME IN`** if you stop short, naming what is left **and the
   priority you would give it**. It BINDS the manager.
6. **A numbered `§ FOR THE MANAGER`** routing anything that needs a decision, a
   dispatch, or a `RECAP_PHP.md` edit.
7. **Re-run the checker registry at the end** and report `CHECKERS PASS` or the
   exact failure.
8. **Say what you did NOT do.** A round that claims full coverage of four
   findings in one sitting will be read as shallow, because the last seven were
   not.
