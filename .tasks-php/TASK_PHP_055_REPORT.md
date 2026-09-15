# TASK_PHP_055_REPORT — **REVIEW ROUND**: `F96` per group, `F113`, and five manager claims

**Role:** research **reviewer**, one agent, alone.
**Scratch:** `.temp/php55/` (`rederive24.py`, `shaquote.py`, both with `--selftest`).
**Brackets, FIRST:** `python3 harness/measure.py --check-stale` → **`66 record(s) examined, 0 STALE`**;
`python3 harness-php/gate.py --tool measure --check-stale` → **`22 record(s) examined, 0 STALE`**.
**Brackets, LAST:** at the end of this file. **Nothing measured, nothing re-gated, no `check.py` on a php row, no `git add`/`commit`, no edits outside `.tasks-php/TASK_PHP_055_REPORT.md` and `.temp/php55/`.**

---

## §0 ⭐⭐⭐ THE HEADLINE — **ITEM 117 CLOSES, AND THE EVIDENCE HAS BEEN COMMITTED SINCE 2026-09-14**

`ph53`'s `unsafe → verus` step is **`−14.00 Ir/call` in FAMILY B as well as in A1**, and
`_050`'s own sweep artefact records it as **identical at every one of 32 `argv` pad
residues, on both inputs**, with `_050`'s own verdict string `["-14.0", 0.0,
"RESOLVABLE", "SIGN-STABLE"]`.

```
.temp/php50/sw_ph53.json   ph53/small.bin   unsafe  min=max=1253.45 over 32 pads
                                            verus   min=max=1239.45 over 32 pads   Δ = -14.00
                           ph53/large.bin   unsafe  min=max=3062.75 over 32 pads
                                            verus   min=max=3048.75 over 32 pads   Δ = -14.00
```

Item 117 says *"the sweep measures the whole-program slope, NOT
`kernel_exclusive_ir`, so it cannot test an A1 figure — **no tool here does**"*.
⛔ **That premise is false in the way that matters.** The sweep cannot read A1 —
but it read **the same number, `−14.00`, in the other statistic, under the exact
perturbation item 117 is afraid of, and it did not move.** An alignment artefact
is *by definition* pad-dependent. This one is pad-invariant over a full period,
twice.

Four more independent supports, all already on file, **§3.3**. ▶ **Item 117
CLOSES. `F96`'s `−1.253 %` does not rest on an artefact, and the route the RECAP
proposes — extend the sweep to report `kernel_exclusive_ir` — is not needed and
is the wrong instrument** (`harness/check.py`'s own operative rule says A1 is the
column the artefact cannot reach).

⭐ **And the second headline: `F96`'s hardest clause — the NOVELTY claim — has a
cheap second method, it is in the row's own hashed `spec.md` and in the
catalogue's own `ph53` entry, and BOTH PRE-DATE THE BUILD.** `M5` is refuted;
so is the RULE-9 table's *"the ONE clause with no cheap second method"*; and so
is the claim that `_047` checked it. **`F96` needs no permanent mark. Every one
of its groups is verdictable, and this report verdicts them.**

---

## §1 ⛔ THE VERDICT TABLE — **CONCLUSION AND REASON, SEPARATELY**

| claim | CONCLUSION | REASON |
|---|---|---|
| **M1** — F96 is four claim-groups wearing one number | ✅ **UPHELD, and UNDER-STATED** — it is **at least seven**, not four | ⛔ **REFUTED IN PART.** The table is **not exhaustive** (§1.1), and **two of its four cells state a fact that is not true**: (d)'s *"the novelty claim is the ONE clause with no cheap second method"* is false (§1.4), and *"that is precisely what `_047`'s reviewer checked"* is false — `_047` checked the **prediction ledger**, group (b) (§1.1b) |
| **M1-residual** — is a verdict filed under another number a discharge? | ✅ **A DISCHARGE for the clause, a BOOKKEEPING FAILURE for the finding** — the manager's position is right | ⚠ **NARROWED: the bookkeeping failure is FORCED BY THE TABLE'S SHAPE, not by the reviewers.** The RULE-9 table has one cell per finding and the reviewers had one clause to file. Blaming the filing hides the cause (§1.5) |
| **M2** — one of the eight gate quotes is stale | ✅ **UPHELD EXACTLY.** `7013be6f7c1c` was `ph53`'s value at `4297b1d`, → `c41ffad2b795` at `bee710e` (`_042`), → `6924e66fde49` at `b754da4` (`_044`) | ✅ **UPHELD, and the other seven reproduce** (`forbidden_hits` **is** nested under `idiom_audit`; both `identity` rows are `differ`/`differ` as pinned). ⭐ **But the manager's hand-check found ONE stale quote and there are TWO** — `RECAP_PHP.md:2922` (F100) quotes `c41ffad2b795` unmarked (§1.2) |
| **M3** — the headline `−1.253 %` reproduces | ✅ **UPHELD EXACTLY** — `(1102.947 − 1116.947)/1116.947 = −1.2534 %`; and *"largest of the three"* and *"n = 3"* both **reproduce** (§1.3) | ⛔ **REFUTED as to the five things.** F96's sentence states **2 of 5** — statistic and base. **INPUT and OPT/MODE are absent**, and the same pair reads **`−16.870 %` at `O0`** (13×) and **`−0.494 %` on `large.bin`** (2.5×). ⭐ **And F96 stripped a caution the row's own `NOTES.md` carries in the same breath** |
| **M4** — the two-`n_iters` equality forces `κ = 0` | ⚠ **CONCLUSION SURVIVES, BY A DIFFERENT ROUTE** — item 117 does close at zero cost, on `_050`'s sweep, which M4 never invoked | ⚠ **UPHELD-NARROWED, NOT DEAD.** The arithmetic is **valid against a one-shot term inside the kernel symbol**, conditional on `s` being input-constant — which **is** independently arguable (§3.2). It is powerless against a per-call term. **M4R threw away the half that worked** |
| **M4R** — M4 rests on modelling the artefact as a whole-program additive constant, so it has **no power at all** | ✅ **UPHELD as a refutation of M4-as-stated** — M4 cannot exclude a per-call artefact, and M4R is right that the family-B step is per-call | ⛔⛔ **REFUTED AS STATED.** *"the observation has NO POWER AT ALL"* is false: it excludes the **one-shot** class exactly. ⭐ **And that class is the one actually measured on this row** — `_044` §8.2 recorded `ph53`'s W1 moving by *"a constant **±14 to ±28** whole-program `Ir`"* across three runs **while every A1 figure was bit-identical**. M4R names three `14`s and misses the fourth, which is on `ph53` itself and is **one-shot** |
| **M4R leg (b)** — both inputs 9 bytes, so one draw twice | ✅ **FACTUALLY CORRECT** (`len("small.bin") == len("large.bin") == 9`) | ⚠ **NARROWED — it attacks a premise M4's surviving half does not use.** For the one-shot class the discriminating variable is `n_iters` (25 000 vs 10 000), not the alignment state |
| **M4S** — any contaminant is per-call-constant, not per-window | ✅ **UPHELD** — `A1(unsafe)` is `1116.947` vs `2835.952`, **2.539×**, so a work-proportional term is excluded | ⭐ **UPHELD and UNDER-STATED.** It is one row of a four-class taxonomy which, completed, leaves **no contaminant class standing** (§3.1) |
| **M5** — only the novelty claim lacks a cheap second method | ⛔⛔ **REFUTED** | ⛔ **REFUTED.** The novelty claim has **three** cheap second methods, two of them written **before the row was built**: `CATALOGUE.md:752` and `patterns-php/ph53-…/spec.md:577`'s `cwe_note`, both deriving it from `index.csv`'s own CWE-824 for CRASH-158. ⭐ **And a group the decomposition does not list — the `index_mut` settlement — reproduces in two minutes** (§1.4) |

**Every one of M1/M2/M3/M5 lost or narrowed its REASON. M2 is the only one whose
reason survives intact, and even it under-counted. `P1` is CORRECT** (§4).

---

### 1.1 `M1`-conclusion — **the decomposition is faithful but NOT EXHAUSTIVE**

The four groups do map onto F96's text, and the mapping is accurate where it
reaches. But F96 (`RECAP_PHP.md:3194-3254`) contains **at least three more
claim-groups that the table does not name**:

| group | F96's text | second method? |
|---|---|---|
| **(e) the BRACKET EVENT** | *"Brackets `66/0` + `14/0` → `66/0` + `16/0`, re-run by me."* | ✅ **cheap, and it REPRODUCES as an event**: 8 php records × 2 = 16 at row 7; today 11 × 2 = **22**. ⭐ **This is the control in §1.2** |
| **(f) the `index_mut` SETTLEMENT** | *"✅ `_040`'s residual `index_mut` risk is SETTLED: yes, a full value-level `ensures`."* | ✅✅ **cheap — two minutes, and it REPRODUCES.** `~/tools/verus/vstd/std_specs/slice.rs:43-48` ships `assume_specification[ <Range<usize> as SliceIndex<[T]>>::index_mut ]` with `r@ == old(slice)@.subrange(…)`, **`final(r)@ == final(slice)@.subrange(…)`** and a frame condition. ⚠ **This is the exact class `CLAUDE.md` warns about twice**, and the check is a grep of the pinned vstd |
| **(g) the §8 POINTER** | *"15 things it is unsure of … both endpoints are unsearched and that is now 4 of 7 rows"* | ⚠ **SUPERSEDED, not unreviewed** — `_042`/F100 searched both endpoints and `_043` ruled on the R4 half. The clause is a **historical state quote**, same class as M2 |
| **(h) the META-CLAIM** | *"a prediction that names its own falsifier and is then refuted on the falsifier's own terms is worth more than a confirmation"* | ⛔ **not a measurable claim at all.** It is a methodological opinion and should never have been inside a finding that the RULE-9 table gates on evidence |

▶ ⭐⭐ **So the decomposition written to cure *"a claim written as a set hides its
members"* is itself a set that hides members — the FIFTH instance of
F22/F27/F69/F114's shape, and the first one inside its own repair.**
▶ **M1-conclusion: UPHELD and strengthened. The count is not four.**

### 1.1b ⛔ **THE FACTUAL ERROR INSIDE `M1`'s CELL (d)**

> *"⛔ the novelty claim is the ONE clause with no cheap second method — and that
> is precisely what `_047`'s reviewer checked when it asked whether `ph52`
> supplies one and found it does not"*

**Both halves are false.** `_047`'s own text
(`TASK_PHP_047_REPORT.md:636-652`) scopes its check explicitly:

> *"(ii) I checked the task's specific question — **has `ph52` since supplied a
> second method for any of the four predictions?** NO … a prediction about
> `ph53`'s R2/R3/R4/R5 cannot be re-tested on it."*

`_047` checked **group (b), the prediction ledger.** It never touched the novelty
claim. ▶ **The RULE-9 table has been carrying, for two rounds, a reason that
attributes to a reviewer a check the reviewer did not make** — and the check it
did make was of a different group. ⚠ **This is the same defect the whole task is
about, one level up: the CONCLUSION (*F96 is unreviewed*) survived while the
REASON given for it named the wrong artefact.**

### 1.2 `M2` — **UPHELD, UNDER-COUNTED, AND THE RULE IS INSIDE `F96` ITSELF**

**Verdict on the three-way question: (iii), a defect in how the RECAP presents
findings — and it is measurable rather than a matter of taste.** F96 was
**correct when written**: `git show 4297b1d:results-php/gate/ph53-iface-tail-uninit.json`
gives `contract_sha256 7013be6f7c1c…`. It is not (i) a defect in F96's
measurement and not (ii) an unavoidable consequence of being a record.

⭐⭐⭐ **THE CONTROL IS IN THE SAME SENTENCE.** F96 quotes two re-gateable
readings, six words apart:

```
contract_sha256 7013be6f7c1c                       a STATE   -> two re-gates stale
Brackets 66/0 + 14/0 -> 66/0 + 16/0, re-run by me  an EVENT  -> still exactly true
```

Same finding, same sentence, same author, same minute. **Only the state form
rotted.** ▶ **THE RULE, and it is not a preference:**

> ⛔ **A finding that quotes a re-gateable record field must quote it as an
> EVENT — the reading, the transition, or the commit/date at which it was taken
> — never as a bare STATE.** The event form ages into a true historical
> sentence; the state form ages into a false current one.

✅ **The layer already knows how to do this and does it twice**:
`.memory-php/03-numbers.md:238` (*"STATE OF THE CORPUS WHEN THE RULE LANDED"*)
and `PROTOCOL_PHP.md:1032` (*"State when this landed"*). **The rule ratifies
practice; F96 is the outlier.**

#### §H treatment — **the checker, built and run**

`.temp/php55/shaquote.py`, **11 must-fire arms, all passing**, pure classifier so
the arms can drive it without git. Run on `RECAP_PHP.md`:

```
11 live gate record(s); 18 distinct contract_sha256 prefix(es) in history
RECAP_PHP.md: 9 keyed sha quote(s), 2 problem(s)
  2922: STALE STATE QUOTE `c41ffad2b795` -- ph53's contract_sha256 at bee710e, superseded, not event-marked
  3200: STALE STATE QUOTE `7013be6f7c1c` -- ph53's contract_sha256 at 4297b1d, superseded, not event-marked
```

⭐⭐ **THE MANAGER'S HAND-CHECK FOUND ONE AND THERE ARE TWO.** Line **2922 is
`F100`** — `_042`'s finding, *"✅ Manager-verified from `results-php/gate/` …
`contract_sha256 c41ffad2b795`"* — stale since `_044` and unmarked. **That is
§H's argument in one line: a green hand-check is not an attack.**
✅ Correctly **exempt**: `:153` and `:1929` (both say *"STALE"*), `:6845` (the
transition form `c41ffad2b795… → 6924e66fde49…`), and the four CURRENT quotes at
`:2048` `:2258` `:2493` `:2615`.

⚠⚠ **THE CHECKER'S OWN HISTORY IS THE MOST USEFUL PART OF IT, AND IT IS IN THE
FILE.** Its first version was a **line grep** and reported **0 quotes** on
`RECAP_PHP.md` — because F96's quote is `` `contract_sha256\n7013be6f7c1c` ``,
**key and value on two lines, inside one backtick pair**. That is trap 1 (F35)
firing on the tool written to catch trap 2. `N7` is that arm. Its second version
accepted `→` as an event marker and **exempted F96 itself**, because the *next
clause* carries an arrow; `N8` is that arm, built from F96's verbatim text, and
`N9` is the arm that stops `N8`'s repair from rejecting `:6845`'s legitimate
transition form.

▶ **TO LAND IT** (the manager lands; I did not put it in `.tasks-php/` because
`checkers.py` fails a new `.py` there as **UNFILED** until its registry line
exists, and `§H`'s founding story `8e2d834` is about a validator and its filing
landing apart):

1. `git mv`-equivalent: copy `.temp/php55/shaquote.py` → `.tasks-php/php55_shaquote.py`.
2. File it in `.tasks-php/checkers.py`'s `REGISTRY` in the **same commit**, argv
   `["RECAP_PHP.md"]`, note: *"11 §H arms; N7 is F35 (a wrapped quote), N8/N9
   are the exemption predicate. Reports; changes no verdict."*
3. **Do not repair `:3200` or `:2922` by deleting the sha.** The repair is the
   event form: `` `contract_sha256 7013be6f7c1c` (as gated at `4297b1d`; now
   `6924e66fde49` after `_042` and `_044`) ``.

### 1.3 `M3` — **the number is exact; the sentence owes three things and drops a caution**

Re-derived from committed `results-php/ph53-iface-tail-uninit.json`,
`kernel_exclusive_ir / n_iters`:

| opt/mode | input | `n_iters` | unsafe | verus | Δ/call | % |
|---|---|---:|---:|---:|---:|---:|
| `O3/isolated` | `small.bin` | 25 000 | 1116.947 | 1102.947 | **−14.00000** | **−1.2534 %** |
| `O3/isolated` | `large.bin` | 10 000 | 2835.952 | 2821.952 | **−14.00000** | **−0.4937 %** |
| `O0/isolated` | `small.bin` | 25 000 | 6287.746 | 5226.986 | −1060.76 | −16.8703 % |

✅ **`−1.253 %` is exact.** ✅ **And two more of F96's clauses reproduce**, which
the manager did not claim: *"largest margin of the three"* and *"n = 3"* —

| row | A1 `unsafe→verus`, `O3/isolated` | small | large |
|---|---|---:|---:|
| `ph53` | **−14.0000 Ir/call, exactly, on both** | **−1.2534 %** | −0.4937 % |
| `ph45` | **−2.0000 Ir/call, exactly, on both** (`n_iters` 1500 / 200) | −0.0383 % | −0.0054 % |
| `ph64` | −0.5093 / −0.5100 | −0.0067 % | −0.0009 % |

**Three rows, all negative, `ph53` largest by 33×.** ✅ Both clauses upheld.

⛔ **THE FIVE THINGS.** F96's sentence is *"THE PROVED RUNG IS CHEAPER THAN THE
UNSAFE ONE — a THIRD row, and by the largest margin of the three (`A1 −1.253 %`)"*.

| owed | stated? |
|---|---|
| STATISTIC | ✅ `A1` |
| INPUT | ⛔ **absent** — it is `small.bin`, and `large.bin` reads **−0.494 %**, 2.5× smaller |
| OPT/MODE | ⛔ **absent** — it is `O3/isolated`, and `O0` reads **−16.870 %**, 13× larger |
| BASE | ✅ *"the unsafe one"* = the shipped R4 |
| **WHICH C COMPILER** | ⭐ **DOES NOT APPLY, AND I AM SAYING SO EXPLICITLY.** `unsafe → verus` is **Rust → Rust**; no C cell is on either side, so `.memory-php/03-numbers.md:170-174`'s fifth clause is vacuous here. **This is the sentence F108 wishes someone had written the first time, and it is now written.** ⚠ It applies the moment anyone quotes this row's R4 or R5 **against a C cell** |

⛔⛔ **AND A DEFECT NOT ON THE TASK'S LIST: `F96` STRIPPED A CAUTION THE ROW
CARRIES IN THE SAME BREATH.** `patterns-php/ph53-…/NOTES.md:1118-1123`:

> *"⚠⚠ **DO NOT READ IT AS A COST OF PROOF IN EITHER DIRECTION.** Nothing about
> the proof is in the binary: every `let ghost`, `assert` and `proof {}` erases
> before codegen, and **R5's exec code is R4's**. What differs is that rustc sees
> a larger module and allocates registers differently — `mov %rdx,%r15` where R4
> keeps the value in `%rcx`, from the very first basic block. **The row states
> the difference and does not attribute it.**"*

**F96 carries the number and not the caution.** ▶ **That is the THIRD
un-inherited caution in this programme** (F108 first, `_env_block` second) — and
the first one inherited **from a php row's own `NOTES.md` rather than from
`harness/`, which is worse, because there is no cross-programme excuse.**
⭐ **It is also, ironically, the single best piece of evidence for `M4`** (§3.2).

### 1.4 ⭐⭐⭐ THE NOVELTY CLAIM — **THE CATALOGUE IS A CHEAP SECOND METHOD, AND SO IS THE ROW'S OWN `spec.md`**

**Answer to §1.4's question: YES, and it answers in both directions.**

**`patterns-php/CATALOGUE.md:752`, `ph53`'s own Part-B entry, written BEFORE the
row was built:**

> *"⚠⚠ risk: **axis reassigned** (adjudication §2 item 8) — both miners reached
> for spatial/temporal, but **the read is *in bounds* (inside the reallocated
> block) and nothing is freed. CWE-824** and `I3` put it here. ⭐ **Same C shape
> as `ph32`**, differing only in which of two numbers the storage was sized from:
> `ph32` sizes to the literal (excess is past the end → CWE-125), `ph53` sizes to
> the count (excess is inside → CWE-824). **Cross-reference, do not merge.**"*

Set beside F96: *"an uninitialised read that is IN BOUNDS. CWE-824 — the slot is
inside the reallocated block and nothing is freed. … `ph32` (sized to the
literal, excess past the end) is its cross-reference, not its duplicate."*
▶ ⛔ **F96's "novelty" is a RESTATEMENT of the catalogue's adjudication note, not
a discovery of the build.** And the catalogue was landed and its nine admissions
reviewed at `TASK_PHP_023`.

**A second, independent support is inside the row's own hashed contract**,
`patterns-php/ph53-iface-tail-uninit/spec.md:577`:

> *"⚠⚠ **THE READ THAT CAUSES IT IS IN BOUNDS, WHICH IS WHY THE CWE IS 824 AND
> NOT 125**: the slot is inside the reallocated block and nothing has been freed,
> so there is nothing for ASan to say about the read ITSELF … ⭐ **Miri is the
> only detector in this tree that sees the read itself.**"*

and it derives the class from a source outside this programme — *"index.csv
records … **CWE-824** for CRASH-158"*. ⭐ **And the in-bounds property is
MEASURABLE, not asserted: an out-of-bounds uninitialised read is ASan's class and
an in-bounds one is MSan's/Miri's, and the row measured exactly that
asymmetry.** ▶ **Three routes, one of them upstream data and one of them a
measurement.**

#### ⛔⛔ AND THE SURVEY THE CATALOGUE MAKES CHEAP **REFUTES THE CORPUS HALF**

F96's two halves have **different verdicts**:

| clause | verdict |
|---|---|
| *"the **first** IN-BOUNDS uninitialised read"* | ✅ **UPHELD as a statement about build order** — `ph53` is row 7, `ph52` is row 8. ⛔ **REFUTED as a statement about the catalogue**: `CATALOGUE.md`'s **T3 family is literally called *"initialised before read"* and has FIVE rows**; `ph50`, `ph51` and `ph52` are all reads of storage that exists and was never written. **The claim is only true under the reading F96's next sentence supplies** |
| *"**No built row priced that**"* | ⛔⛔ **TRUE WHEN WRITTEN (6 prior rows), FALSE NOW.** `ph52` (row 8) prices an in-bounds uninitialised read — its `spec.md:13` says *"uninitialised slot: **CWE-457 with CWE-824 as the consequence**"* and its `cwe_note` files it under the same T3 family. Different mechanism (an unwritten **tag byte** in a caller's stack zval vs an unwritten **tail slot** in a reallocated heap block), same class |

⭐⭐⭐ **AND THAT IS `M2`'s DEFECT IN A SECOND CLAUSE OF THE SAME FINDING.**
*"No built row priced that"* is a **corpus-state quote presented as current**,
exactly like `contract_sha256 7013be6f7c1c`. ▶ **So `M2`'s rule is bigger than a
hash and must be written to cover both:**

> ⛔ **A finding that quotes a re-gateable RECORD or a CORPUS-STATE COUNT must
> quote it as an EVENT.** *"No built row priced that"* → *"no row built before
> this one priced that (6 rows, 2026-09-12)"*.

⓵ **`.memory-php/03-numbers.md:238` and `PROTOCOL_PHP.md:1032` already do this
for the family-B corpus count. `F96` does it for its brackets and not for its
sha or its corpus claim.**

### 1.5 `M1`-residual, and the question worth more than either

**Is *"`_050` confirmed result 2 while calling F96 unreviewed"* a discharge or a
bookkeeping failure? — BOTH, and the manager's split is right.** For the clause
it is a discharge: rule 9 asks whether a **reviewer** has attacked a claim with a
second method, and result 2 has had two reviewers and two opposite outcomes
(F110 #4 confirms it on its own stated falsifier; F113 refutes its stated
reason). Which number the verdict was filed under does not change what was done.

⚠⚠ **But the REASON the manager gives — that the reviewers mis-filed — is
narrowed, and the narrowing is the useful part. THE TABLE HAD NOWHERE ELSE TO
PUT IT.** The RULE-9 table is *"the index of what may enter `.memory-php/`"* and
it has **one cell per finding**. A reviewer who verdicts one clause of a
seven-clause finding cannot write *"F96: half-verdicted"* into a cell that holds
one verdict, so it opens a new finding number. ▶ **The filing behaviour is what
the table's shape rewards. Four reviewers did the same thing; that is a design
property, not four lapses.**

**Answer to *"should a bundling finding be admissible as one finding at all?"* —
YES as a narrative unit, NO as a review unit.** Forcing seven finding numbers per
built row would be worse: a row build *is* one event and the narrative is how the
next agent reads it. The rule belongs to the **table**, not to the findings:

> ⭐ **RULE (for `04-process.md`, law 13): a ROW-BUILD finding enters the RULE-9
> table DECOMPOSED INTO ITS CLAIM-GROUPS, on the day it is written, by its
> author.** The author knows what the claims are and it costs ten minutes; a
> manager reconstructing them four rounds later costs a session **and still
> misses three** (§1.1). ▶ **And a reviewer's verdict on a clause is written into
> THAT CLAUSE'S ROW, whatever finding number the reviewer files the evidence
> under.**

#### §H treatment for that rule — **specified, NOT built** (depth; see §7)

A checker `rule9_index.py`:

* parse the RULE-9 table's finding→verdict cells;
* parse every `.tasks-php/TASK_PHP_*_REPORT.md` header/`Scope:` line for finding
  ids and for the task's declared **role**;
* **FLAG** any finding whose cell reads `UNREVIEWED` while a task whose role is
  **reviewer** names it in scope.

Must-fire negatives: **(N1)** a finding in scope of a reviewer task and marked
`UNREVIEWED` **must fire** — this is the arm that would have fired after `_043`,
`_047`, `_050` **and** `_053`; **(N2)** a finding in scope of an **engineer**
task and marked `UNREVIEWED` must **not** fire (that is rule 9 working — `_042`);
**(N3)** a finding with no table cell at all must fire as `UNINDEXED`;
**(N4)** a decomposed finding whose every clause row has a verdict must **not**
fire even though the parent name still appears; **(N5)** a table cell naming a
finding that does not exist in `RECAP_PHP.md` must fire as `STALE`.

---

## §2 `F113` — **VERDICTED ON ALL FOUR POINTS**

### 2.1 Point 1 — the 24 cell-sweeps ⚠ **UPHELD, and the artefacts are in gitignored `.temp/`**

`.temp/php55/rederive24.py` (`--selftest`, 3 arms). **The 24 re-derive exactly,
and the 12 are identifiable**: `ph64`'s **8** cells (all `0.00` on `argv[1]` per
`.temp/php50/ph64_full.json`) + `ph55`'s **4 Rust** cells, each swept on **`envp`**
and on **`argv[0]`** = **24 cell-sweeps, 0 counterexamples.** ✅ `ph64` is flat on
all three axes on all eight cells. ✅ **F113 point 1 UPHELD, conclusion and
reason.**

⛔⛔ **AND THE ARTEFACTS ARE IN GITIGNORED `.temp/php53/` AND `.temp/php50/`**
(`git check-ignore -v` → `.gitignore:3:.temp/`). **That is F99/F51's defect
applied to the evidence for a rule in the authoritative layer.**
▶ **Does the generator alone rebuild them? — YES in principle, NO in practice
today, and the distinction matters.** `php50_align_sweep.py` and
`php53_envp_sweep.py` are **both committed** and both read already-built binaries
out of `.temp/php-scratch/build/<row>/`. **Those binaries are also gitignored**,
so a fresh clone must rebuild ten rows before either generator can run. ▶ **The
committed generator restores the rule's evidence at the price of a full rebuild,
not at the price of a script.** ⓘ `.tasks-php/` already commits 18 `.py`; the
~230 KB of sweep `.json` is the evidence and is not committed.

### 2.2 Point 2 — **IS `§B5` AN `iff`? — YES textually, and the `iff` ARGUMENT IS A NON-SEQUITUR**

`PROTOCOL_PHP.md:1009-1011` and `.memory-php/03-numbers.md:213-215` both say
**IFF**, in capitals. ✅ **So F113's premise *"§B5 is an `iff`"* is textually
true.** ⛔ **But the inference is not.**

> `03-numbers.md:257-258`: *"The refutation stands because **ONE counterexample
> breaks an `iff` and this rule is an `iff`** — not because the axes generally
> differ."*

**Three things are wrong with that reason, and the conclusion survives all
three:**

1. ⛔ **What `ph07` refutes is the GROUND, not the rule.** *"`argv` and `envp`
   are the same knob"* is a **universal generalisation over cells**, and one
   counterexample falsifies a universal whether or not any rule downstream is an
   `iff`. **The `iff` is doing no work in the inference.**
2. ⛔⛔ **`ph07` IS NOT A COUNTEREXAMPLE TO THE `iff`, and F113 says so in the
   same breath.** The rule's condition is *step `0.00` on the `argv` sweep*.
   `ph07`'s `verus` cell reads **`34.49`** there — the rule **refuses** it, and
   refusing an alignment-exposed cell is the correct verdict. A counterexample to
   the `iff` would be a cell reading `0.00` on `argv` and non-zero off it; the
   24 cell-sweeps found **none**. ▶ **The sentence as written asserts that the
   rule was broken by the same evidence the round used to confirm it.**
3. ✅ **What the `iff` really does is fix the COST of the refutation, not its
   validity.** Because §B5 licenses publication (a *sufficient* condition),
   *"same knob"* was its warrant for sufficiency; `ph07` removes the warrant by
   showing the step is axis-dependent **a priori**. ▶ **That is exactly the
   operative consequence F113 lands (*"NECESSARY … NOT PROVED SUFFICIENT"*) — so
   the right reason was already in the round, one paragraph down.**

▶ **VERDICT: F113 point 2 — CONCLUSION UPHELD (the ground is refuted, and the
one-row scope does not weaken it, because a universal needs only one
counterexample). REASON REFUTED and REPLACED.** Replacement text for
`03-numbers.md:257-258`, **as a replacement and not an addendum** (item 73):

> ⭐ **The refutation stands because *"`argv` and `envp` are the same knob"* is a
> UNIVERSAL claim about cells, and `ph07`'s `verus` cell falsifies it —
> **`34.49` / `20.08` / `0.00` on the three axes.** ⛔ **It is NOT a
> counterexample to the publication rule itself**, whose verdicts are confirmed
> on 24 cell-sweeps; `ph07`'s cell reads `34.49` on `argv[1]` and the rule
> correctly refuses it. **What the refutation costs is the rule's WARRANT for its
> sufficiency direction, which is why the caution below is necessary.**

### 2.3 ⭐⭐⭐ Point 3 — **THERE IS NO FIFTH; THE MANAGER'S CANDIDATE IS REFUTED ARITHMETICALLY, AT ZERO COST, ON `_053`'s OWN ARTEFACTS**

The candidate: *"a `(cell, axis)` step could be the cell's ALIGNMENT SENSITIVITY
**times** the axis's REACH, not a property of the pair."* **It is testable
cheaply — the table is already measured — and it is FALSE.**

| cell | `argv[1]` | `argv[0]` | `envp` |
|---|---:|---:|---:|
| `ph07` `verus` | **34.49** | 20.08 | **0.00** |
| `ph07` `unsafe` | 0.00 | — | 0.00 |
| `ph45` × 4 Rust cells | 7.00 | — | **7.00** |
| `ph55` `c-clang`, `c-clang-h` | 7.00 | 7.00 (`c-clang`) | **7.00** |
| `ph55` × 4 Rust cells | 0.00 | 0.00 | 0.00 |

Under `step = sens(cell) · reach(axis)`: from `ph45`/`ph55`,
`sens·reach(argv1) = sens·reach(envp) = 7` with `sens ≠ 0`, so
**`reach(envp) = reach(argv1)`**. From `ph07 verus`,
`sens'·reach(argv1) = 34.49` so `sens' ≠ 0`, hence `sens'·reach(envp)` must be
`34.49`. **It is `0.00`.** ⛔ **The separable model is refuted.**

⭐⭐ **AND A SHARPER FACT NOBODY HAS REPORTED, WHICH KILLS THE SOPHISTICATED
VERSION TOO: the PERIOD is also a property of the pair.** Reading the raw
series rather than the steps, **every non-flat series in the corpus is period 32
/ window 16 — with exactly one exception**:

```
.temp/php53/argv0.json   ph55-opdata-stride/c-clang, argv[0] axis
   1749.79 x7 | 1742.79 x8 | 1749.79 x8 | 1742.79 x8 | 1749.79 x1   (circular 8/8/8/8)
   -> PERIOD 16, WINDOW 8
.temp/php53/argv0.json   ph07-strcut-cursor/verus,  argv[0] axis
   -> PERIOD 32, WINDOW 16
```

**Same axis, same run, same 32 pads, two different periods.** A "reach" is a
property of the **axis** and cannot differ between two cells on one axis; a
"sensitivity modulus" is a property of the **cell** and cannot differ between two
axes for one cell — and `ph55 c-clang` reads period 32 on `argv[1]` and `envp`
and period 16 on `argv[0]`. ▶ ⛔ **No `(sens, reach)` factorisation fits. F113's
*"the step is a property of the `(cell, axis)` PAIR"* is now PROVED, not
asserted — and it holds for the period as well as the magnitude.**

⚠⚠ **AND A CONSEQUENCE FOR THE LANDED TEXT.** `PROTOCOL_PHP.md:1005` and
`.memory-php/03-numbers.md:216-217` both state, as a property of *"the lever"*,
that it is **bistable with period 32 and window 16**. **One measured cell is
period 16 / window 8.** ✅ **No published figure is at risk** — 32 is a multiple
of 16, so a 32-residue sweep still covers a period-16 cell, and §B5's rule is
**safe**. ⛔ **But the sentence is a universal with a counterexample in `_053`'s
own artefact**, and it is the sentence that justifies the sweep's width.
▶ **Replacement, both homes:** *"bistable, **period 32 and window 16 on 29 of 30
measured cell-axis series**; `ph55`'s `c-clang` cell reads **period 16, window
8** on the `argv[0]` axis (`_053`, `.temp/php53/argv0.json`). ⭐ **A 32-residue
sweep covers both, which is why the rule sweeps a full period rather than
screening two pads.**"*

✅ **VERDICT: F113 point 3 — CONCLUSION UPHELD and STRENGTHENED. The mechanism is
still unexplained; there is no fifth rival, because the whole separable FAMILY is
now excluded.** The remaining candidates are non-separable and none is cheap: the
most plausible is that **valgrind synthesises the client stack itself**
(`harness/check.py:3298-3303` says so in terms — *"valgrind … synthesises the
client's stack itself"*), so each axis's bytes reach `%rsp` through a different
part of valgrind's own layout. ▶ **Testing it needs a probe that prints the
client `%rsp` under callgrind for 32 pads × 3 axes — 96 valgrind runs and a
scratch binary. That is a task, not a section, and I did not run it.**

### 2.4 Point 4 — the inherited caution ⚠ **PRESENT BUT APPENDED, AND THE SCOPE LANDED IN ONLY ONE OF TWO HOMES**

⛔ **F113's *"§B5 did not inherit it. It does now"* is TRUE as to presence and
FALSE as to application.** In **both** homes the caution sits **below a rule
sentence that still reads `IFF`**:

| home | the rule | the caution | gap |
|---|---|---|---|
| `PROTOCOL_PHP.md` | **:1009-1011**, *"may be published **IFF** … `0.00`"* | **:1042-1046** | 33 lines |
| `.memory-php/03-numbers.md` | **:213-215**, *"**IFF** … `0.00`"* | **:266-271** | 53 lines |

A rule box exists to be read and stopped at. ▶ **This is item 73's shape — a
correction appended instead of applied — inside the repair for item 73's fifth
instance. Sixth instance.**

⛔⛔ **AND ITEM 118's SCOPE LANDED IN ONLY ONE HOME.** The RULE-9 table says
*"its SCOPE (1 row against 3) landed with it"*. It is in
`.memory-php/03-numbers.md:254-256`. **It is NOT in `PROTOCOL_PHP.md` §B5** — and
§B5 is what §0 of this very task file tells a reader to read. **An agent reading
§B5 gets the refutation without the scope.**

**REPLACEMENT TEXT for the `PROTOCOL_PHP.md` §B5 rule box** (not an addendum):

> ▶ **RULE: a family-B difference may be published IFF the two cells it spans
> have a measured step of `0.00 Ir/call` over a full 32-residue `argv[1]` pad
> sweep, or the difference exceeds that step by the sweep's stable ratio.**
> ⚠⚠ **THE `0.00` READING IS NECESSARY AND NOT PROVED SUFFICIENT**, and the
> `IFF` is the rule this project has chosen to act on, not a proved equivalence:
> the sweep perturbs `argv[1]`, the step is a property of the `(cell, axis)`
> PAIR, and sufficiency is corroborated on **24 cell-sweeps across `envp` and
> `argv[0]` with no counterexample** — not proved. **Say it the way
> `harness/check.py::_env_block` says it: three equal fields mean *this record
> cannot tell the two draws apart*, not *the two draws are the same*.**
> ⚠ **SCOPE OF THE GROUND-REFUTATION: ONE ROW DISAGREES AND THREE AGREE**
> (`ph07` against `ph45`, `ph55` and the 12 clean cells).
> ⓘ `.tasks-php/php50_align_sweep.py` — no build, no gate, no re-measure.

### 2.4b ⭐ **THE RATE QUESTION — SAMPLED, AND THE SAMPLE IS BAD NEWS**

**Sample, declared before looking: the three `harness/check.py` functions that
produce the family-B statistic §B5 governs** — `_env_block` (:3270),
`_callgrind_total` (:3405) and `check_marginal_ir` (:3440). **Five operative
cautions. One is fully inherited.**

| # | the caution, in `harness/check.py` | php layer |
|---|---|---|
| 1 | `_env_block`: *"three equal fields mean this record cannot tell the two draws apart"* | ✅ **INHERITED** (`_053`) — ⚠ appended, §2.4 |
| 2 | `_env_block` `domain`: *"When the three differ, compare **`kernel_exclusive_ir`** … **structurally immune, 0 of 288 triples moved**"* | ⛔ **NOT INHERITED as a rule**, and **item 117 was written as its opposite** (*"no tool here"* can test an A1 figure). ⚠ The string is in **every php gate record**, unread |
| 3 | `_callgrind_total`: *"a kernel that `memset`s a stack array pays an alignment-dependent cost **per call** … four patterns at 7 Ir/call (p03, p04, p38, and **p46 … which `memset`s TWO stack arrays per call and so moves by `−14 = 2 × 7`**)"* | ⛔⛔ **NOT INHERITED.** ⭐ **Item 117's *"`14 = 2 × 7`"* worry was invented from scratch when the mechanism, the constant AND a named PAT pattern were already written down in the harness** |
| 4 | `check_marginal_ir` **THE OPERATIVE RULE**: *"for a cross-RUNG comparison use `kernel_exclusive_ir`; use `marginal_ir_per_call` **for anti-collapse, which is what it was built for**"* | ⚠ **HALF-INHERITED.** `03-numbers.md:283` quotes the first clause **only in support of one prohibition**. The second clause is not inherited at all — and §B5 is a whole publication regime for a statistic the harness says is not for publication |
| 5 | `check_marginal_ir`: *"Quote marginals **to the instruction, never to the hundredth**, across sessions"* | ⚠ **REPLACED BY A WEAKER RULE POINTING THE OTHER WAY**: `03-numbers.md:130-132` says *"do not quote a whole-program figure to more than **2 dp**"*. The corpus quotes `34.49`, `20.08`, `+106.25`, `−14.00`, `+2.80`. ⓘ **Checked and it does not bite**: every one of those is a **within-session** sweep reading, where the slope is deterministic; the harness's caution is explicitly *"across sessions"*. ⚠ **But `03-numbers.md:180-181` itself says *"two rules of different strength on one question is how the weaker one gets cited"*, and this is that** |

▶ **RATE: 1 of 5 fully inherited, 3 of 5 load-bearing, and the two that bite
hardest (#2, #3) both bear on the one open item this task was asked to route.
Two in three rounds was not a coincidence; it is 4 in 5 on a targeted sample.**
▶ **RECOMMENDATION: a bounded ENGINEER task — *"read the docstrings of the seven
`harness/` functions whose output a php row publishes, and file every caution as
INHERITED / NOT / CONTRADICTED"*.** Bound it by **function list**, not by file.
⛔ **Not a sweep of `harness/`**: `check.py` alone is >10 000 lines.

---

## §3 ITEM 117 — ⭐⭐⭐ **CLOSED**

### 3.1 The contaminant taxonomy — **which argument reaches which class**

`Δ_A1(input) = s(input) + contaminant`, with `dTot = Δ·n` an exact integer.

| contaminant class | reached by | verdict on `ph53` |
|---|---|---|
| **one-shot OUTSIDE the `kernel` symbol** | structure: A1 is symbol-scoped and *"never charges a callee"* (`check.py`'s operative rule) | ⛔ **cannot enter A1 at all** |
| **one-shot INSIDE `kernel`** (`κ`) | ⭐ **M4, and ONLY M4.** `25000·s + κ = −350 000` and `10000·s + κ = −140 000` ⟹ `15000·s = −210 000` ⟹ **`s = −14`, `κ = 0`**, given `s` input-constant | ⛔ **EXCLUDED.** ⚠ **This is the class `_044` §8.2 actually measured on this row** (a *constant* ±14–28 whole-program `Ir`) |
| **per-call, work-proportional** | **M4S** — 2.539× different work, identical Δ | ⛔ **EXCLUDED** |
| **per-call, constant, PAD-DEPENDENT** (the alignment lever) | ⛔ M4 and M4S are powerless — **M4R is right about this** | ⛔ **EXCLUDED by `_050`'s sweep**: step `0.00` on all 8 cells over a full 32-residue period, both inputs, and `Δ = −14.00` at **every** residue |
| **per-call, constant, PAD-INDEPENDENT** | — | ✅ **this IS `s`. It is the code difference.** There is nothing left |

### 3.2 Is `s` independently arguable as input-constant? — ✅ **YES, and not from the equality**

1. **Source-level**, `ph53/NOTES.md:1118-1123`: *"every `let ghost`, `assert` and
   `proof {}` erases before codegen, and **R5's exec code is R4's**. What differs
   is that rustc … **allocates registers differently — `mov %rdx,%r15` where R4
   keeps the value in `%rcx`, from the very first basic block**."* A register
   allocation difference in per-call straight-line code is **constant per call by
   construction** and independent of how many bytes the call processes.
2. **Static counts**, from the committed record: `O3/isolated` `kernel` `n_fn`
   **764 (unsafe) vs 746 (verus)** — 18 static instructions, giving 14 dynamic
   per call.
3. **The exact integrality**: `dTot` is `25000 × (−14)` and `10000 × (−14)`
   **exactly** — the same 14 instructions on every one of 35 000 calls.

⚠ **Neither (1) nor (2) is inferred from the equality M4 uses them to license.
The circularity the task warns about is avoided.**

### 3.3 The five independent supports, all already committed

| # | evidence | where |
|---|---|---|
| 1 | **B1 `unsafe→verus` is `−14.00` at every one of 32 `argv` pad residues, both inputs**, step `0.00` on all 8 cells; `_050`'s own verdict `RESOLVABLE / SIGN-STABLE` | `.temp/php50/sw_ph53.json` (⚠ gitignored — §2.1) |
| 2 | ⭐ **THREE INDEPENDENT GATE RUNS, at `envp_stack_bytes` 3686 → 3697 → 3698 (residues 6, 17, 18 mod 32), give all 96 `marginal_ir_per_call` figures BIT-IDENTICAL** — `check_marginal_ir` re-runs `_callgrind_total` per cell per gate, so these are three fresh measurements, not a copy | `git show {4297b1d,bee710e,b754da4}:results-php/gate/ph53-…json` — **committed, and nobody had read it** |
| 3 | **Every A1 figure bit-identical across three runs** of `ph53`'s sidecar, while every W1 figure moved by a constant **±14 to ±28 whole-program `Ir`** | `TASK_PHP_044_REPORT.md:607-612` |
| 4 | **`kernel_exclusive_ir` is structurally immune**: `100 %` of the ±7 swing is inside `__memset_avx2_unaligned_erms`, a **libc callee**; **0 of 288** triples moved, re-confirmed at **0 of 58** and **0 of 72** on whole-tree regenerations | `.memory/03-measurement.md:2605-2625`; the same sentence is in every php record's `marginal_ir_env.domain` |
| 5 | **The code difference**, §3.2 | `NOTES.md` + the record |

⚠⚠ **THE HONEST LIMIT ON (2), APPLYING `_env_block`'s OWN CAUTION TO MY OWN
EVIDENCE:** the three draws span **12 bytes inside a 16-wide window**, so I
**cannot show they straddle the boundary**. *Three equal fields mean this record
cannot tell the draws apart.* ▶ **(2) is corroboration on a second axis, not
proof.** (1) is the one that does not need this caveat, because it sweeps a full
period.

⚠ **AND THE SCARIEST COUNTER-EVIDENCE, NAMED AND THEN KILLED.**
`harness/check.py:3405-3420` records a PAT pattern, **`p46`, that moves by
exactly `−14 = 2 × 7` per call because it `memset`s TWO stack arrays**. So
`−14 Ir/call` has a documented alignment mechanism in this tree, which item 117
never cited and which is worse than the three `14`s the RECAP lists. ⛔ **It does
not bite**: that mechanism is **pad-dependent by construction**, and `ph53`'s is
pad-invariant over a full period (support 1), in a column the same file calls
structurally immune (support 4). ⓘ ⚠ **A PAT-side inconsistency I noticed and
did not act on:** the docstring attributes `−14` to `p46` while
`.memory/03-measurement.md`'s enumerated seven-cell table shows `p46 c-clang`
moving `6216.00 → 6209.00` = **`−7`**, and lists no `p38` cell at all. **Reported,
not edited** — `harness/` is frozen and this is a PAT matter.

### 3.4 ⭐ Question 3 — **pricing item 117's proposed route: DON'T BUILD IT**

**Is reporting `kernel_exclusive_ir` per pad an extension of
`php50_align_sweep.py`? — YES, and it is cheap: ~1–2 hours.** The tool already
runs the binaries under callgrind and parses `summary:`/`totals:`; adding
`--dump-instr`-free per-symbol attribution means swapping `_callgrind_total` for
a `callgrind_annotate`-style parse and a second output column. Its §H arms would
be: a synthetic profile with a known symbol split; a cell whose kernel symbol is
absent (must FIRE, not return 0); a pad at which A1 and B disagree in sign.

⛔⛔ **BUT IT SHOULD NOT BE BUILT, AND NOT ON COST GROUNDS.** `harness/check.py`'s
own operative rule is that `kernel_exclusive_ir` is **the immune column** — the
one you fall back to *when* the marginal is contaminated. Building a sweep to ask
*"is the immune column contaminated by the lever it is immune to?"* re-opens a
question the PAT layer closed with a **mechanism** (the swing is inside a libc
callee) plus **288 + 58 + 72** negative observations. ▶ **The correct disposal is
the RECAP's own second option: an explicit decision to accept the mechanism and
the census, and say so once.** ⭐ **And this task supplies the row-specific half
the census did not have — supports 1, 2 and 3 are all `ph53`.**

### 3.5 ▶ **ITEM 117: CLOSED.** Replacement text

> | ~~117~~ | ✅✅ **CLOSED AT `TASK_PHP_055` — `ph53`'s A1 `unsafe→verus` `−14.000` IS THE ROW'S CODE DIFFERENCE, NOT AN ALIGNMENT ARTEFACT, AND THE EVIDENCE WAS COMMITTED ON 2026-09-14.** ⭐ **The decisive fact nobody had read: the SAME `−14.00` appears in FAMILY B, and `_050`'s sweep recorded it at EVERY ONE OF 32 `argv` PAD RESIDUES ON BOTH INPUTS, with step `0.00` on all eight cells** (`.temp/php50/sw_ph53.json`; `_050`'s own verdict `[-14.0, 0.0, RESOLVABLE, SIGN-STABLE]`). **An alignment artefact is pad-dependent by definition; this one is pad-invariant over a full period, twice.** ✅ Four more supports, all pre-existing: **three independent gate runs at `envp_stack_bytes` 3686/3697/3698 give all 96 family-B figures BIT-IDENTICAL** (⚠ 12 bytes inside a 16-wide window, so corroboration and not proof); `_044` §8.2's **A1 bit-identical across three runs while W1 moved a constant ±14–28 whole-program `Ir`**; `.memory/03-measurement.md:2605-2625`'s **mechanism** — 100 % of the ±7 swing is inside `__memset_avx2_unaligned_erms`, a **libc callee**, and `kernel_exclusive_ir` is symbol-scoped, **0 of 288 / 0 of 58 / 0 of 72**; and the **code**: `NOTES.md:1118-1123` says R5's exec code IS R4's modulo register allocation, and the static `kernel` is **764 vs 746**. ⛔ **`M4` must still not be cited AS STATED** — its arithmetic reaches only a one-shot term inside the kernel symbol, conditional on `s` input-constant. ⚠ **`M4R` is also narrowed: *"no power at all"* is wrong — M4 excludes the one-shot class exactly, and that is the class `_044` measured on this row.** ⛔ **DO NOT BUILD the `kernel_exclusive_ir` sweep**: it would test the immune column for the contaminant a mechanism says cannot reach it (`TASK_PHP_055` §3.4). ⚠⚠ **AND THE `14 = 2 × 7` WORRY HAD A PAT PRECEDENT THE ITEM NEVER CITED**: `harness/check.py:3405-3420` records `p46` moving by *"`−14 = 2 × 7`"* because it `memset`s TWO stack arrays per call. **It does not bite — that mechanism is pad-dependent and `ph53` is not** — but it is the third un-inherited `harness/` caution in three rounds (`TASK_PHP_055` §2.4b) |

---

## §4 THE PREDICTIONS, SCORED

| | prediction | score |
|---|---|---|
| **P1** | at least one of `M1`/`M2`/`M3`/`M5` refuted, and a **REASON** rather than a **CONCLUSION** | ✅✅ **CORRECT, AND UNDERSHOT.** **All four lost or narrowed their REASON; `M5` lost its conclusion too.** Only `M2`'s reason survived intact, and it under-counted the defect 1→2. **Three of four conclusions survived.** The predicted asymmetry is exactly what happened: **conclusions 3/4 survive, reasons 0/4 survive as written.** ▶ **Five rounds is now six** |
| **P2** | `M4R` survives but NOT AS STATED, narrowed by the level-vs-slope distinction | ✅ **CORRECT, and the manager identified the right fragility while writing the question.** M4R's conclusion stands; *"no power at all"* is refuted by exactly the level-vs-slope distinction §3's question 1 names. ⭐ **And the narrowing is bigger than predicted: the class M4 does reach is the class `_044` measured on this row** |
| **P3** | `M1`'s CONCLUSION survives and `M1`'s REASON is narrowed | ✅ **CORRECT, and the fragility was in the corrected draft too.** The conclusion survives and is **under-stated** (≥ 7 groups). The reason is narrowed twice: the table is not exhaustive, **and cell (d) contains a false statement about what `_047` checked** — a role/scope attribution error in the section that was itself corrected once before dispatch for a role/scope attribution error |

⛔ **The four-round run is not broken.** No manager claim survived with its reason
intact.

---

## §5 NOT ON THE LIST

1. ⛔⛔ **A SECOND STALE `contract_sha256` IN `RECAP_PHP.md`, IN `F100`** — line
   **2922**, `c41ffad2b795`, superseded by `_044`, not event-marked. Found by the
   checker, missed by the hand-check (§1.2).
2. ⛔⛔ **`ph56` IS A THIRD ALIGNMENT-EXPOSED ROW AND THE LANDED CORPUS-STATE
   SENTENCE DOES NOT KNOW IT.** `_052` §4.4 measured `ph56`'s `c-clang` and
   `c-clang-h` at **`7.00 Ir/call`** and found **one non-publishable pair**
   (`c-clang → c-clang-h`, `small.bin`, median `+17.53`, **range `14.00`**,
   `|d|/step = 1.25`). ⭐ **That is a FOURTH `14.00` in an alignment context and
   item 117 never listed it.** Both `.memory-php/03-numbers.md:238-243` and
   `PROTOCOL_PHP.md:1032-1034` say *"`4` of `180` … on `ph55` and `ph07` only"*
   with scope *"all ten rows"*. ✅ **Both are correctly marked *"when this
   landed"*, so neither is false** — ⚠ **but the ten rows were nine built rows
   plus `ph00`, and `ph56` (row 10) was not among them**; `.temp/php50/` has
   `sw_ph{00,03,07,16,29,45,52,53,55}.json` + `ph64_full.json` and **no `ph56`**.
   ▶ **Replacement for both: *"`4` of `180` when the rule landed (`_050`: nine
   built rows + `ph00`, `ph55` and `ph07` only). `_052` §4.4 then swept `ph56`
   and found a third exposed row — `c-clang` and `c-clang-h` at `7.00`, one
   difference NOT RESOLVABLE (range `14.00`). The row does not quote it.
   ⭐ Still no published family-B number is wrong."***
3. ⛔ **`F96` CONTAINS A SECOND TIME-STAMPED-AS-CURRENT CLAIM**: *"No built row
   priced that"*, true at 6 rows and false at 10 (§1.4). **`M2`'s rule must cover
   corpus-state counts, not just record fields.**
4. ⚠ **`.tasks-php/checkers.py` FAILS ANY NEW `.py` AS `UNFILED`** (:251-253), so
   a reviewer who lands a probe in `.tasks-php/` without the registry line turns
   a checker red. ⓘ **This is the ratchet working**, but it means §H's *"a
   validator lands with its negatives"* now also means *"and with its registry
   line, in the same commit"* — which is `8e2d834`'s lesson restated. **Worth one
   sentence in §H.**
5. ⚠ **`.memory-php/03-numbers.md:124-133` (item 99) IS THE EXCULPATORY HALF OF
   THE LAYER AND THE `M4R` DISCUSSION CITES ONLY THE INCRIMINATING HALF
   (`:222-236`).** They are ~100 lines apart in one file. The exculpatory
   paragraph says *"every A1 figure was bit-identical while the whole-program
   column moved by a constant ±14–28 Ir"* — **and one of its two numbers is 14**,
   on the row under test. ▶ **When a finding searches the layer for
   counter-evidence it must search for both signs**; `04-process.md` law 12's
   companion.
6. ⚠ **`ph45`'s A1 `unsafe→verus` is `−2.0000` EXACTLY on both inputs at
   `n_iters` 1500 and 200** — the same exact-integer, two-`n_iters` structure as
   `ph53`'s `−14.000`, **on the row whose family-B difference for the same rung
   pair carries the measured `14.00` alignment range.** ⭐ **That is the natural
   positive control for item 117 and it is free**: on the corpus's most
   alignment-exposed row, the same pair's A1 is a clean small integer while its B
   is `+106.25 ± 14`. **The two statistics do not share the artefact.**
7. ⚠ **`F96`'s bracket quote is the only one of its readings that aged
   correctly**, and it is also the only one written as a transition. **Noted as
   the control for §1.2's rule** rather than as a defect.

---

## §6 WHAT I AM UNSURE OF

1. ⚠⚠ **I did not re-run either sweep.** Supports 1 and the whole of §2.3 rest on
   **reading `_053`'s and `_050`'s committed-generator/gitignored-artefact JSON**,
   not on re-measurement. If those artefacts are stale relative to the current
   binaries, my §2.3 period result and §3.3 support 1 move. ⓘ Mitigating:
   support 1's `1253.45`/`1239.45` **match the committed gate record exactly**,
   which is a real cross-check.
2. ⚠⚠ **The period-16 finding is ONE SERIES.** `ph55 c-clang` on `argv[0]`,
   32 points, one run, `problems: []`. **I did not reproduce it.** It is the only
   exception in 30 series, which is either a real effect or a single bad run, and
   **I cannot tell those apart from one artefact.** ▶ **If a task re-runs one
   thing from this report, re-run that.**
3. ⚠ **Whether `_050`'s sweep and the gate's `check_marginal_ir` measure `ph53`
   in bit-identical conditions.** They agree to the digit on the two cells I
   checked, which is strong, but I did not audit the sweep's build/env against
   the gate's.
4. ⚠ **The `s` input-constancy argument is source-level and static-count-level,
   not disassembly-level.** I did not diff `unsafe` and `verus` objdump for
   `ph53`; I read `NOTES.md`'s claim about register allocation and corroborated
   it with `n_fn` 764 vs 746. **`_042` §3 did disassembly for R3, not for this
   pair.**
5. ⚠ **My `shaquote.py` exemption predicate is a heuristic** and I changed it
   twice while writing this report (both changes are `N8`/`N9` arms in the file).
   **It is right on all five real cases in `RECAP_PHP.md`, and I do not claim it
   generalises.** It also scans only `contract_sha256`; `source_sha256`,
   `input_sha256` and `derived_from_sha256` quotes are **not covered**.
6. ⚠ **I did not verify that `ph50`/`ph51` really are in-bounds uninitialised
   reads** beyond their catalogue prose. **`ph52` I did verify** from its
   `spec.md`. The T3 argument in §1.4 would survive on `ph52` alone.
7. ⚠ **`F113`'s point-2 verdict turns on a reading of what *"the ground"* names.**
   I read *"argv and envp are the same knob"* as a universal over cells. If it
   was meant as *"the same knob generally"*, the one-row scope bites and the
   headline weakens to *"one row disagrees"*. **I think the universal reading is
   right — it is what the sentence says — but a reviewer could differ.**
8. ⚠ **I did not review `F115`, `F116` or `F118`.** They were in the brief as
   optional depth and the depth went to §3 and §5. **`F117` I touched only
   incidentally** (§5 item 4, which corroborates its registry design).

---

## §7 DEPTH — WHERE IT RAN OUT, EXACTLY

**Done:** M1 · M2 · M3 · M4 · M4R · M4S · M5 verdicted both halves; `F96`
verdicted per group with the RULE-9 replacement text; `F113` on all four points
with the `iff` reading; **item 117 CLOSED** with replacement text; §4 scored; §5
with seven items; one §H checker **built and run** (11 arms).

**Stopped, deliberately, and named:**

* ⛔ **The `rule9_index.py` checker (§1.5) is SPECIFIED, NOT BUILT** — five
  must-fire arms written out. It needs a role parser over 55 task headers and I
  chose to spend the time on §3 instead.
* ⛔ **The valgrind client-stack probe (§2.3) is PRICED, NOT RUN** — 96 valgrind
  runs plus a scratch binary. It is the only route left to the unexplained
  mechanism.
* ⛔ **The period-16 series is NOT REPRODUCED** (§6.2).
* ⛔ **`F115` / `F116` / `F118` NOT REVIEWED** (§6.8).

---

### ▶ REPLACEMENT TEXT FOR THE RULE-9 `F96` BLOCK

Replacing `RECAP_PHP.md:147-156` **entirely** — not appended (item 73):

> | **F96** | ✅✅ **VERDICTED PER GROUP AT `TASK_PHP_055`. NOT `UNREVIEWED`, AND NOT PERMANENTLY MARKED — EVERY GROUP HAD A CHEAP SECOND METHOD AND THE LAST ONE WAS IN THE ROW'S OWN `spec.md` ALL ALONG** | ⛔ **The *"no cheap second method"* ground was wrong twice over** (F114 found the first half; `_055` the second) |
>
> #### ⭐⭐⭐ `F96`, PER GROUP — **seven groups, not four** (`TASK_PHP_055` §1.1)
>
> | group | verdict |
> |---|---|
> | **(a)** the eight gate quotes | ✅ **VERDICTED. Seven reproduce** (`forbidden_hits` **is** nested under `idiom_audit`; both `identity` rows `differ`/`differ` as pinned). ⛔ **`contract_sha256 7013be6f7c1c` is a STATE quote and is two re-gates stale** — correct at `4297b1d`, → `c41ffad2b795` at `bee710e`, → `6924e66fde49` at `b754da4`. ▶ **Repair is the EVENT form, not deletion** |
> | **(b)** the 4-prediction ledger | ⚠ **R3 VERDICTED by `_042` §3** (*"the prediction's MECHANISM was wrong"*, with the disassembly) and **that is the group `_047` checked** — not (d). ⛔ **R2 / R4 / R5 UNREVIEWED**, and they are the only clauses of F96 still owed |
> | **(c)** result 2 | ✅ **VERDICTED TWICE, SPLIT ALONG CONCLUSION/REASON.** `_050`/F110 #4 **CONFIRMS the conclusion on its own stated falsifier**; `_053`/F113 **REFUTES the stated REASON** (§B1a's O(1)-allocation precondition). ⓘ **A verdict filed under another finding's number is still a verdict; the table's one-cell-per-finding shape is what forced the mis-filing** (law 13) |
> | **(d)** results 1/3/4 | ✅ **VERDICTED. Result 3's `A1 −1.253 %` reproduces exactly**, and so do *"largest of the three"* (33×) and *"n = 3"*. ⛔ **The sentence owes INPUT and OPT/MODE** (`large.bin` reads `−0.494 %`, `O0` reads `−16.870 %`) and ⭐ **the C-compiler clause DOES NOT APPLY — this is a Rust→Rust pair, stated explicitly**. ⛔ **And it strips the row's own caution** (`NOTES.md:1118-1123`, *"do not read it as a cost of proof in either direction"*) |
> | **(d′) the NOVELTY claim** | ⛔⛔ **IT WAS NEVER THE CLAUSE WITHOUT A SECOND METHOD, AND `_047` NEVER CHECKED IT.** ✅ **The mechanism half — in bounds, CWE-824, `ph32` a cross-reference — is UPHELD by THREE routes that all pre-date the build**: `CATALOGUE.md:752`, `spec.md:577`'s `cwe_note`, and `index.csv`'s own CWE-824 for CRASH-158; **plus a measurement** (ASan sees only the dereference; Miri alone sees the read). ⛔ ***"the first in-bounds uninitialised read"* is true only of BUILD ORDER** — `CATALOGUE.md`'s **T3 family is *"initialised before read"* and has five rows**. ⛔⛔ ***"No built row priced that"* was true at 6 rows and is FALSE at 10**: `ph52` (`spec.md:13`, CWE-457 with CWE-824 as the consequence) prices one |
> | **(e)** the bracket event | ✅ **VERDICTED — reproduces, and it is the CONTROL for the state-vs-event rule**: 8 records × 2 = `16/0` then, 11 × 2 = `22/0` now |
> | **(f)** the `index_mut` settlement | ✅ **VERDICTED — reproduces in two minutes.** `~/tools/verus/vstd/std_specs/slice.rs:43-48` ships the full value-level `ensures`, `final(r)@ == final(slice)@.subrange(…)`, plus a frame condition |
> | **(g)** the §8 pointer (*"both endpoints unsearched, 4 of 7 rows"*) | ⚠ **SUPERSEDED, not unreviewed** — `_042`/F100 searched both, `_043` ruled on the R4 half. **A historical state quote** |
> | **(h)** the meta-claim about falsifiers | ⛔ **NOT A MEASURABLE CLAIM.** A methodological opinion inside an evidence-gated finding. **It should be moved to `04-process.md` or dropped, not verdicted** |
>
> ▶ **WHAT IS STILL OWED ON `F96`: R2, R4 and R5 of the prediction ledger. Nothing else.**
> ▶ **`F96` may enter `.memory-php/` for groups (a) [event form], (c) [with BOTH verdicts in the same sentence], (d) [with input + opt/mode + the row's caution], (d′) [mechanism half only, with the corpus half re-dated], (e) and (f). NOT (b)'s R2/R4/R5. NOT (h).**

---

**Brackets, LAST** — re-run at the end of this task:

```
python3 harness/measure.py --check-stale                  ->  66 record(s) examined, 0 STALE
python3 harness-php/gate.py --tool measure --check-stale  ->  22 record(s) examined, 0 STALE
```

**`66/0` and `22/0`, unmoved.** Nothing was measured, gated or re-gated;
`harness/check.py` was never run on a php row; no `git add`, no `git commit`; the
only files written are this report and `.temp/php55/{rederive24.py,shaquote.py}`,
both of which carry their must-fire negatives and run them on every invocation.
