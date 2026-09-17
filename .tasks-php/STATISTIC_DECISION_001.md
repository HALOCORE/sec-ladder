# STATISTIC_DECISION_001 — which statistic each comparison uses, and why

> ⛔⛔⛔ **WHY THIS FILE IS COMMITTED, AND IT IS NOT TIDINESS.** It was written as
> `.temp/mgr172/STATISTIC-DECISION-DRAFT.md`, which is **gitignored and
> auto-`rm`-able**, and **`F85` cites it BY SECTION** (`RECAP_PHP.md:6986`,
> *"`.temp/mgr172/STATISTIC-DECISION-DRAFT.md` §5"*, landed 2026-09-12, commits
> `fb49a3e`/`66d8412`). `F85` is **the programme's central claim** — that the
> cross-language column carries **29 of 38** family-A/B sign flips — and it is
> **UNREVIEWED**. `.memory-php/04-process.md` **law 11**: *a published finding
> whose only evidence is a gitignored probe will not survive a clean checkout.*
> Promoted by **`TASK_PHP_064`, 2026-09-17**, repo at commit `f4bda71`.
> ⓘ **Only the filename changed**; the body below is the draft as written, with
> the probe citations repointed (see the last bullet).
>
> ⛔⛔ **READ THIS BEFORE QUOTING §5's COUNT: THE DOCUMENT IS SUPERSEDED ON IT
> AND CONTRADICTS ITSELF.** §5's heading says **28 of 38 (76 %)** and its first
> sentence says ***"Of the 37 sign flips"***, while §4's by-column table sums to
> 37. **The published figure is `29 of 38`**, and `RECAP_PHP.md`'s F85 says so
> explicitly — *"the count is **29, not 28** — `38 − 9 = 29`, and the draft's own
> *'the remaining 9 are Rust-vs-Rust'* implies it … **76 % was right and '28' was
> not**; the headline mixed two scripts' populations"*, corrected by
> `TASK_PHP_038`. ▶ **Where this file and `RECAP_PHP.md` F85 disagree, F85
> wins.** The wrong numbers are left in the body ON PURPOSE — a draft edited to
> agree with its own correction stops being evidence of what was drafted — but
> nobody may quote §5's `28`/`37` as a result.
>
> ⚠⚠ **AND THE POPULATION IS A 2026-09-12 POPULATION.** Every count in §4 and §5
> is over **366 comparisons on SIX gated php rows**. Re-run 2026-09-17 over the
> **14** rows gated today, `probes/callee_share.py --flips` gives **758
> comparisons, 141 sign flips, 111 of them cross-language**. ⭐ **The RATIO
> survives** — 76.3 % then, **78.7 %** now — **the COUNT does not.** Quote
> `29 of 38` with its date and its row set, never off a fresh run.
>
> ✅ **EVERY PROBE THIS DOCUMENT NAMES IS NOW COMMITTED.** Six were cited in the
> `Evidence:` line and two more in the body; `PROMOTE_001` (2026-09-17) promoted
> `null_control.py`, `identity_null.py`, `inclusive_ir.py`, `bc_sweep.py`,
> `flip_exact.py` and `sweep_cg.sh`, and `TASK_PHP_064` promoted
> `callee_share.py` and `spread_stat.py`. ▶ **All eight citations below were
> repointed at `.tasks-php/probes/`.** No other `.temp/` reference in this file
> was touched: the rest are HISTORICAL — they say where work happened — and are
> correct as written.
>
> ⚠ **WHAT IT STILL DEPENDS ON THAT IS NOT COMMITTED:** the cached callgrind
> profiles under `.temp/mgr172/cg/` that §5's family-C re-derivation was taken
> from. Those are **re-derivable artefacts with a committed generator**
> (`probes/sweep_cg.sh`), which is `CLAUDE.md` Don't #1 being **followed**.
> ▶ **Do not commit them.**
>
> ⛔ **WHAT IS STILL OWED.** (1) **`F85` has never been reviewed**, and §5 of this
> file is what a reviewer must attack first — that is the debt, and this
> promotion does not touch it. (2) §5's own caveat stands: the `ph07` and `ph03`
> flips were **never** re-derived against family C and remain B-only. (3) §6's
> *"`ph64`'s B1 is forbidden by §2 and needs a single-run replacement"* is an
> action item that has not been discharged here and is not claimed to be.
> (4) ⚠⚠⚠ **UNREVIEWED** (`PROTOCOL.md` rule 9), exactly as it was when it was
> scratch. **Promotion changes where this lives, not what it has earned** — and
> in particular it does not turn a DRAFT into a decision.

⚠⚠⚠ **THIS IS A PROPOSAL AND IT IS UNREVIEWED. `PROTOCOL.md` rule 9 forbids it
entering `.memory-php/` before review, and it is too central to land on the
manager's word.** It needs a **reviewer task**, and the reviewer's first job is
§5 — the one clause I know rests on a statistic F84 just showed is confounded.

Evidence: `RECAP_PHP.md` F74 · F80 · F82 · F83 · F84(staged) · F71 · item 54 ·
`TASK_PHP_037_REPORT.md` §5.4 · probes
`.tasks-php/probes/{callee_share,spread_stat,null_control}.py` and
`.tasks-php/probes/{identity_null,inclusive_ir,bc_sweep}.py`,
all `--selftest` PASS.

---

## §1 There are FOUR families in use, not two, and three are published

| | definition | scope | runs |
|---|---|---|---|
| **A** | `results-php/<row>.json` → `cells[].ir[inp].kernel_exclusive_ir / n_iters` | the `kernel` symbol | 1 |
| **C** | `callgrind_annotate --inclusive=yes`, `kernel` row | the kernel's **call tree** | 1 |
| **W1** | `callgrind_annotate`'s `PROGRAM TOTALS / n_iters` | whole program | 1 |
| **B** | `results-php/gate/<row>.json` → `marginal_ir_per_call` | whole program, a **slope** | **2** |

**Published today:** `ph03`/`ph16`/`ph29` in **A1**; `ph07` in **A3**; `ph64` in
**B1**; `ph45` in **A1 + W1**, both labelled. ⚠ **Six rows, four statistics, and
the START HERE box mixed them while being faithful — the rows disagree.**

**C is not built** (item 62). W1 exists only inside `ph45`'s `spellings.py`.

## §2 ⛔ NEVER B WHERE A SINGLE-RUN FIGURE EXISTS

F84: B's two-point slope carries artefacts that are **up to 99.31 %** of the
reading (`ph29/small`, R4/R5) and that run in **both directions** — `ph29/large`
has **C `+2.383`/call against B `+0.000`**, B reporting a clean null over real
work. `ph00` shows **B `−1.000` against C `0.000`** on both inputs, which
identifies `check.py`'s documented **34-cell `−1.00` class** as the slope.

⭐ **`TASK_PHP_037` reached this independently and without seeing F84**, choosing
W1 *"so a variant is never priced on two runs"*, and characterised W1's own
fixed per-program term (**~0.9 %**, of which **~0.075 %** fails to cancel between
variants) instead of leaving it to be noticed. **Two routes, one conclusion.**

▶ **B keeps exactly one job — anti-collapse, which is what it was built for**
(`harness/check.py`'s own operative rule). It is **not** a cost column.

## §3 A IS EXACT AND IT IS BLIND, AND BOTH HALVES ARE MEASURED

**Exact** (F82): where the kernels differ by a known static count, A resolves it
**to the instruction** — `ph45` Δnopad `−2` gives `−3000` over 1500 calls and
`−400` over 200, `exec_rate` **1.0000** twice; `ph64`'s conditional path reads
**0.5093/0.5100**, two inputs agreeing on a quantity nobody designed to agree.
And A reads **`0.000000`** on all 8 true-null cells, re-derived in F84 off a
different code path than F82 used.

**Blind** (`_037` §5.4): on `ph45`, **A1's spread over all nine searched variants
is `0.000000` pp** against **66.7 pp (R3)** and **44.5 pp (R4)** whole-program.
⚠⚠⚠ **A control pricing that row in A1 alone writes
`r4_endpoint_degenerate: true` AND `r3_endpoint_degenerate: true`. Both are
false.** ⭐ And it is sharper than *"the symbol is identical"*: the symbol's
**code** changes (3 and 4 distinct digests) while its **executed count does not
move at all.**

## §4 ▶ THE DECISION: DECIDE BY WHERE THE LEVER IS, NOT BY WHICH COMPARISON IT IS

Let `s = inside_share = (kernel_exclusive_ir / n_iters) / marginal_ir_per_call`.

1. ⛔⛔ **THERE IS NO SHORTCUT — AND THIS REFUTES WHAT RULE 1 SAID IN MY FIRST
   DRAFT** (*"`min(s)` HIGH and `|Δs| ≤ 0.02` → A is sufficient"*).
   `.tasks-php/probes/flip_exact.py`, `--selftest` PASS, 6 negatives.

   Since `s ≡ A/B`, `a_ratio = (s_a/s_b) · b_ratio` **identically** — so *"the
   share ratio explains A's disagreement"* is **true by definition and explains
   nothing** (F78's shape; I had it written as a mechanism before noticing).
   The **exact** flip condition is geometric: **a flip occurs iff `1` lies
   strictly between `a_ratio` and `b_ratio`** — **0 mispredictions over all 366
   comparisons.**

   ⚠⚠ **I then tried to reduce that to a scalar `|effect| < |share mismatch|`
   and it is REFUTED, 30 of 346** — the scalar form drops the *side* condition
   and fires where `b` sits on the far side of 1.

   ⭐⭐⭐ **THE CONSEQUENCE IS DEFLATIONARY AND IT IS THE POINT: the exact test
   needs BOTH ratios, so deciding whether A is safe to publish requires
   computing B or C — THE VERY STATISTIC THE RULE WOULD LET YOU SKIP.** No
   function of the shares alone can certify A, **at any threshold**, because the
   flip condition depends on the **effect size** and the shares do not know it.
   ▶ **F80's rule is not a licence to publish A alone. It is a way to EXPLAIN a
   disagreement after seeing both.**
2. ▶ **SO THE OPERATIVE RULE IS THE ONE `ph45` ALREADY FOLLOWS: PUBLISH BOTH,
   LABELLED, ALWAYS** — and `|Δs|` is reported beside them as the *explanation*,
   never as a gate. ⚠ Never publish the whole-program figure instead of A: A is
   the attributable half and the reader needs both.
   ⭐ **This makes the corpus's disagreements cheap to describe and impossible to
   hide**, which is the outcome F74's four corrections were groping toward.
3. ⛔ **Two labelled quantities, never three, and NO PAIR INTERVAL.**
   `min(R3 found) − min(R4 found)` is not the repair.
4. ⚠ **Where the two cells' callee USAGE differs for reasons unrelated to the
   rung's safety strategy, NO statistic separates it — say so, do not pick a
   column.** F83: on `ph03` the R4/R5 kernels are **byte-identical** and C still
   reads **`+265.924`/call**, in libc, caused by binary layout. **Attribution is
   a property of the COMPARISON, not of the column.**

### Where A and the whole-program figure actually disagree — measured

⚠ **Not "where A is certified"** — §4.1 says nothing certifies it. This is where
the two **do** disagree, which is what a reader needs told.

**366 comparisons. Three classes, and the third was a taxonomy error of mine:**

| class | n | meaning |
|---|---|---|
| agree | 314 | same nonzero sign |
| **FLIP** | **38** | opposite **nonzero** signs — A points the wrong way |
| ⭐ **BLIND** | **14** | **A is exactly `0` while B is not — A says NOTHING** |

⚠⚠ **`flip_exact.py`'s first version scored BLIND as FLIP**, inflating the count
to 52 and producing 14 "mispredictions" of a predicate that was right — caught by
its own negative **N5**, which is phrased *"a number is being read wrong"* rather
than *"the rule is wrong"* and so pointed at the real cause. ⭐ **BLIND is the
worse failure and it needed its own name**: on `ph45` it is **A `+0.000 %`
against a `+23.37 %` effect** (`safe_naive` vs `safe_tuned`), which is `_037`
§5.4's result arriving from a different direction.

⚠ **F80's `|Δs| ≤ 0.02` scored per class**: it calls **7 real FLIPS** safe and
**13 of the 14 BLIND cells** safe, and flags **153 comparisons that agree**.
▶ **20 failures, not the 6 F80 published** — and 3 of the 7 flips are between
numbers both under **0.2 %** (`ph00` −0.111 vs +0.046; `ph45` R4/R5 twice), which
are two ways of measuring approximately nothing rather than real disagreements.

**By column, where the 38 FLIPS live:**

| comparison | flips |
|---|---|
| **the `fixed-R4 bound`  R3 vs R4** — the programme's headline | ✅ **`ph45` only** (2, and it publishes both) |
| the R4/R5 null | ⚠ 3, all **under 0.2 %** |
| the safe span  R2 vs R3 | ⚠ `ph45` 2 · `ph64` 2 |
| ⚠⚠⚠ **CROSS-LANGUAGE  C vs Rust** | ⛔ **28 of 38 — 76 %** |

✅ **The headline bound is safe.** ⚠⚠⚠ **The cross-language column is not.**

## §5 ⚠⚠⚠ THE CROSS-LANGUAGE COLUMN IS THE PROBLEM, AND THE FLIPS ARE REALLY THERE

Not merely uncertified — **measured**. Of the **37 sign flips** between A and the
whole-program figure across 366 comparisons, **28 (76 %) are cross-language**,
and they carry the largest magnitudes in the corpus:

| row | input | comparison | **A** | **whole-program** | `Δs` |
|---|---|---|---|---|---|
| `ph29` | large | `c-clang` vs `safe_tuned` | **+8.87 %** | **−21.81 %** | 0.257 |
| `ph29` | large | `c-clang` vs `unsafe` | +1.85 % | **−25.30 %** | 0.243 |
| `ph29` | large | `c-gcc` vs `safe_naive` | **+33.01 %** | **−0.80 %** | 0.235 |
| `ph29` | small | `c-clang` vs `safe_tuned` | +20.88 % | −2.82 % | 0.153 |
| `ph07` | small | `c-clang` vs `safe_tuned` | +0.83 % | **−11.94 %** | 0.117 |
| `ph03` | small | `c-gcc` vs `verus` | +8.10 % | −0.41 % | 0.077 |

⚠⚠ **The remaining 9 flips are Rust-vs-Rust and ALL are `ph45` (6) and `ph64`
(3)** — the two callee-heavy rows. **All 6 sub-threshold flips (`Δs ≤ 0.02`) are
`ph45`**, which is F80 exactly.

**`ph29/large c-gcc vs safe_naive` is the sentence this matters for:** A says C
is **33 % dearer** than naive safe Rust; whole-program says **0.8 % cheaper**.
That is the difference between *"safe Rust is a third cheaper than C here"* and
*"they are the same"* — and it is **this project's central claim.**

⭐ **This generalises open item 54 rather than repeating it.** Item 54 says
`ph64`'s C rung allocates `2n+2` per call with **60 %** of its instructions in
libc, so *"the C-vs-Rust column on this row is not a safety comparison"*.
▶ **Measured: it is not one row. A1 is uncertified for that column on FIVE of
six, and 28 flips sit there.**

### ✅✅ RESOLVED — THE FLIPS SURVIVE FAMILY C. I RE-DERIVED THEM RATHER THAN PUBLISH AND HOPE

**This section was staged with a blocker on itself**, because every flip above is
A against family **B**, and F84 had just shown B confounded by up to **~266
`Ir`/call — 17 % of `ph29`'s own 1 566.56 marginal**, which is not negligible
against a 21–25 pp effect. ▶ **So I profiled `ph29`'s cross-language cells and
recomputed against C and W1.** `.tasks-php/probes/sweep_cg.sh`.

| input | comparison | **A** | **B** | **C** | **W1** | |
|---|---|---|---|---|---|---|
| small | `c-clang` vs `safe_tuned` | **+20.88** | −2.82 | **−4.85** | −5.27 | **FLIP confirmed** |
| small | `c-clang` vs `unsafe` | **+13.56** | −7.20 | **−8.90** | −9.22 | **FLIP confirmed** |
| large | `c-gcc` vs `safe_naive` | **+33.01** | −0.80 | **−1.06** | −1.19 | **FLIP confirmed** |
| large | `c-clang` vs `safe_tuned` | **+8.87** | −21.81 | **−22.01** | −21.90 | **FLIP confirmed** |
| large | `c-clang` vs `unsafe` | **+1.85** | −25.30 | **−25.48** | −25.33 | **FLIP confirmed** |
| small | `c-gcc` vs `safe_naive` | +39.92 | +17.85 | +14.55 | +13.83 | agree (control) |
| large | `c-gcc` vs `safe_tuned` | +51.40 | +7.04 | +6.85 | +6.61 | agree (control) |

⭐⭐⭐ **EVERY FLIP SURVIVES, AND THE DISAGREEMENT IS NOT "A VERSUS A CONFOUNDED
STATISTIC" — IT IS A VERSUS THREE INDEPENDENT STATISTICS THAT AGREE WITH EACH
OTHER TO ~2 pp.** ✅ **And the two non-flipping comparisons agree across all four
families, which is the control**: if the pipeline were producing the flips, they
would flip too.

⚠ B and C do differ by **2–3 pp** on the `small.bin` cells (`−2.82` vs `−4.85`;
`+17.85` vs `+14.55`) — **the confound is real and present** — but it is an order
of magnitude short of flipping anything. ⓘ `ph45` was excluded from the sweep
because `TASK_PHP_037` was rebuilding it.

▶ **So §5 stands.** ⚠ The `ph07` and `ph03` flips are **not** re-derived against
C and remain B-only; the mechanism is the same and the `ph29` result makes it
very likely, but **that is an inference and the rows are named here rather than
folded in.**

### ⓘ WHAT THE ORIGINAL BLOCKER SAID, KEPT FOR THE RECORD

**Every flip above is A against family B, and F84 just showed B is confounded.**
`ph29`'s per-call marginal is **1 566.56** `Ir` and F83 measures the attribution
confound at up to **~266** `Ir`/call — **17 % of that row's marginal**, which is
**not** negligible against a 21–25 pp effect.

⚠⚠⚠ **SO THE FLIP LIST MUST BE RE-DERIVED AGAINST FAMILY C BEFORE ANY OF §5 IS
PUBLISHED.** I am **not** claiming the flips survive; I am claiming they are
measured against a statistic now known to be wrong in both directions by a
material fraction. ▶ **That is item 62's first job, and it is the reason this
file is a draft.** ⭐ If the flips survive against C, §5 is the programme's most
important finding. If they do not, **§5 is F74's fourth correction happening a
fifth time, to me, on the same afternoon** — and I would rather find that out
from a reviewer than from a reader.

## §6 What this costs to adopt

* **Nothing** for the headline bound — certified 5 of 6 already.
* `ph45` already complies (both families labelled).
* `ph07` publishes **A3**, `ph64` **B1** → ⛔ **`ph64`'s B1 is forbidden by §2**
  and needs a single-run replacement. ⚠ Its `NOTES.md` is in the gate digest but
  **not** the measurement digest, so restating it costs **one re-gate per row**.
* The cross-language column needs a decision **after** §5's re-derivation.
* ⚠ `PROTOCOL_PHP.md` §B2 and the shared `why` block are **hashed** — writing
  this into either is a **six-row PHP re-gate** (item 55's shape, and item 61's).
