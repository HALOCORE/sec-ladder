# STATISTICS_001 — which statistic each comparison uses, and why

> ⚠⚠ **THIS FILE EXISTS BECAUSE ITS CONTENT WAS LIVING IN GITIGNORED SCRATCH.**
> The decision that governs how **every row publishes its numbers** was in
> `.temp/mgr172/STATISTIC-DECISION-DRAFT.md`, and `.gitignore` line 3 is
> `.temp/`. **A fresh clone had none of it.** That is open item 65's defect
> exactly (*"a committed claim resting on gitignored scratch"*) and
> `TASK_PHP_038` §5.2 flagged it by name. **Same convention as
> `QUOTA_001.md` / `ADJUDICATION_001.md`: a standalone, committed, numbered
> analysis.**
>
> ⚠⚠⚠ **STATUS: NOT AUTHORITATIVE.** `.memory-php/` is the authoritative layer
> and this is not in it. F83–F86 have had an engineer→reviewer cycle and are
> **UPHELD-NARROWED**; **F88, F89 and F90 have not been reviewed at all**, and
> F90 **disagrees with the reviewer**. ▶ **Read this for the argument and the
> numbers; do not cite it as settled.**
>
> Sources: `RECAP_PHP.md` **F71, F74, F80, F82–F90**, open items **52, 54, 60,
> 62, 63, 65, 67, 68**, `TASK_PHP_037_REPORT.md` §5.4, `TASK_PHP_038_REPORT.md`
> in full. Probes, all `--selftest` PASS and all under gitignored `.temp/` —
> **so the numbers below are the record and the probes are not**:
> `.temp/mgr170/{callee_share,spread_stat,null_control}.py` ·
> `.temp/mgr172/{identity_null,inclusive_ir,bc_sweep,flip_exact}.py` ·
> `.temp/mgr173/ph64_draws.py` · `.temp/php38/*.py`.

---

## §1 There are FOUR families in use, not two, and three are published

| | definition | scope | runs |
|---|---|---|---|
| **A** | `results-php/<row>.json` → `cells[].ir[inp].kernel_exclusive_ir / n_iters` | the `kernel` symbol | 1 |
| **C** | `callgrind_annotate --inclusive=yes`, the `kernel` row | the kernel's **call tree** | 1 |
| **W1** | `callgrind_annotate`'s `PROGRAM TOTALS / n_iters` | whole program | 1 |
| **B** | `results-php/gate/<row>.json` → `marginal_ir_per_call` | whole program, a **slope** | **2** |

**Published today:** `ph03` / `ph16` / `ph29` in **A1** · `ph07` in **A3** ·
`ph64` in **B1** · `ph45` in **A1 + W1**, both labelled.
⚠ **Six rows, four statistics.** The START HERE box once mixed A1 and B1 and was
**faithful** in doing so — the rows themselves disagree.

⚠ `harness/measure.py::callgrind_ir` records **exclusive** `Ir` only, for two
needles (`kernel`, `main`). **C is not built** (item 62). **W1 exists only inside
`patterns-php/ph45-htmlent-cache-int/controls/spellings.py`.**

## §2 Each family's DEFINITIONAL gap — measured, not argued

| | definitional gap | the measurement that shows it |
|---|---|---|
| **A** | ⛔ **blind to callees** | `ph45`'s `inside_share` is **0.055–0.094**, and A1's spread over **nine** searched R3/R4 variants is **`0.000000` pp** against 66.7/44.5 pp whole-program (F87, `_037` §5.4) |
| **C** | ⛔ **blind to `main`** | the `−1.00` class: **one instruction per kernel call in `main`**, `main_exclusive_ir` Δ/n = **−1.0000** on `ph00` and `p11`. **C cannot see it; B can** (F84 as corrected by `_038` §4.2) |
| **W1** | ⛔ **carries a language-dependent fixed term** | **≈176 k `Ir`**, two rows agreeing to **0.45 %** (`_038` §1.3). ▶ **So C and W1 are NESTED SCOPES OF ONE RUN, not independent** — my *"three independent statistics"* was wrong |
| **B** | ✅ **none found** | it cancels the fixed term and charges everything. Its flaw is **`probe_iters`**, a `spec.md` **parameter** — see §5 |

⚠⚠ **AND ONE THING NO COLUMN FIXES: ATTRIBUTION.** On `ph03` the R4/R5 kernels
are **byte-identical** (`md5_fn` `338505795ee18db952aafcdaec522df4`) and **C
still reads `+265.924`/call**, in libc, caused by **binary layout**. Neither
rung's code can have caused it. ▶ **Attribution is a property of the COMPARISON,
not of the statistic** (F83), and **it applies to C exactly as much as to B.**

## §3 Where A and the whole-program figure actually disagree

**366 comparisons. Three classes:**

| class | n | meaning |
|---|---|---|
| agree | 314 | same nonzero sign |
| **FLIP** | **38** | opposite **nonzero** signs — A points the wrong way |
| **BLIND** | **14** | **A is exactly `0` while the other is not** |

⚠ **The BLIND taxonomy inverts the evidence on 5 of its 14 cells** — it lumps
*A genuinely sees nothing* (`ph45`: **A `+0.000 %` against a `+23.37 %`
effect**) with *A correctly reads a true zero*. **It still has no working test**
(item **67**); the reviewer built one, its must-fire negative failed, and it
shipped the failure rather than the test.

**Of the 38 flips, 29 are CROSS-LANGUAGE** — and `TASK_PHP_038` §1.1 adjudicated
**all 29** against family C: `ph03` 6/6, `ph07` 6/6, `ph29` 16/16 **survive**,
`ph00` 0/1 **refuted**. ▶ **28 of 29 survive.**

⚠⚠⚠ **THE SENTENCE THIS IS ABOUT.** `ph29/large`, `c-gcc` vs `safe_naive`: **A
says C is `+33.01 %` DEARER than naive safe Rust; B, C and W1 all say ≈ `1 %`
CHEAPER.** That is the difference between *"safe Rust is a third cheaper than C
here"* and *"they are the same"* — **and it is this project's central claim.**
⭐ It **generalises** open item 54 rather than repeating it: not one row.

⚠ **RULED (`_038` §1.5): cross-language callee work IS rung-attributable**, so A
really is the wrong column there. ⚠ But **not** for the reason the draft gave
(`ph64`, a row with **zero** flips); the sufficient reasons are §B's design
constraint plus the measured fact that **≥ 98 %** of a cross-language cell is
inside the kernel's call tree.

## §4 ⛔ THERE IS NO SHORTCUT — the rule that was tried and does not exist

`inside_share ≡ A/B`, so `a_ratio = (s_a/s_b) · b_ratio` **identically**.
▶ *"The share ratio explains A's disagreement"* is **true by definition and
explains nothing** — F78's shape, in the finding that cites F78.

**The exact flip condition is geometric: a flip occurs iff `1` lies strictly
between the two ratios.** ⚠ *"0 mispredictions over all 366"* is a **logical
tautology** and **is not evidence** (`_038` §2.2). A scalar restatement
(`|effect| < |share mismatch|`) is **refuted 30 of 346** — it drops the *side*
condition.

⭐⭐⭐ **THE OPERATIVE CONSEQUENCE: the exact test needs BOTH ratios, so deciding
whether A is safe to publish requires computing the statistic the rule would let
you skip.** ⚠ *"No function of the shares can certify A at any threshold"* is
**too strong** — a certifier from shares **plus a declared minimum effect size**
is constructible; it fails here only because no such floor exists. ✅ **But the
conclusion survives unconditionally for a simpler reason: `s ≡ A/B`, so
computing the share requires B already.**

> ### ▶ THE RULE
>
> 1. **PUBLISH BOTH, LABELLED, ALWAYS** — the attributable column (A) and a
>    whole-program or call-tree column, and **name which statistic each is.**
> 2. **`|Δinside_share|` is reported beside them as the EXPLANATION, never as a
>    gate.** F80's `≤ 0.02` threshold, scored per class, calls **7 real FLIPS**
>    and **13 of the 14 BLIND cells** "safe" and flags **153** that agree —
>    **20 failures, not the 6 F80 published.**
> 3. ⛔ **Two labelled quantities, never three. NO PAIR INTERVAL** —
>    `min(R3 found) − min(R4 found)` is not the repair.
> 4. ⚠ **Where the two cells' callee usage differs for reasons unrelated to the
>    rung's safety strategy, say so — do not pick a column.**
> 5. ⚠ **Quote a magnitude floor with every sign claim.** Three of the
>    taxonomies written for this analysis needed one and **none had one on the
>    first pass** — the `ph00` flip (−0.111 vs +0.046), the BLIND class, and an
>    outlier test that fired on `ph03` at a spread of **0.00 pp**.

## §5 ⚠⚠ THE UNRESOLVED PART, AND IT IS A DISAGREEMENT WITH THE REVIEWER

`TASK_PHP_038` §6 rules: *publish both, and **the second column MUST be C***;
drop W1; name `probe_iters`. **Item 62 becomes a precondition.**

**F90 disagrees**, on the reviewer's own finding. F88 established that B is one
draw of a pseudo-random sample (`probe_iters` is **`[100, 200]` in all seven PHP
`spec.md`s and in `p11`**, manager-verified; `ph29`'s level moves **32 %** across
draws). ▶ **But that is SAMPLING ERROR, and the pin is a lever on it.**
`ph64/small`, worst cross-language pair, **disjoint** spans:

| span width | disjoint spans | `safe_tuned` vs `unsafe` | `c-gcc` vs `safe_naive` |
|---|---|---|---|
| **100** — the shipped pin | 9 | 0.067 pp | **8.124 pp** |
| 200 | 4 | 0.037 pp | **2.092 pp** |
| 300 | 3 | 0.021 pp | **1.243 pp** |

⚠⚠ **The RATE is not pinned and two attempts to pin it are both confounded in
the same direction** — sliding spans share draws (width-500 windows share 400 of
500), disjoint spans leave fewer samples. **A 1/width fit that looked clean was
two biases meeting.** ▶ **Only the direction and the width-100 figure are
trustworthy.**

⭐ **And F89: the draw CANCELS in a same-language ratio and does NOT
cross-language — `0.07 pp` against `8.63 pp`, same row, same nine draws.**
`ph64`'s published B1 headline moves **0.07 pp on a +17.08 % effect** and the
published draw is **inside** the range, so **item 66 answered NO** and B's
disqualification rests on **F84's observation alone**.

▶ **THE OPEN QUESTION, and it is cheap:** item **68** — widen `probe_iters` on
**one** row, re-gate, measure what moves. **If the cross-language spread
collapses, B needs no replacement and item 62 stops being a precondition.**
⚠ Costs: `probe_iters` is inside `contract_sha256`, so **one re-gate per row**
(7 PHP, 33 PAT), it moves every `marginal_ir_per_call`, and B needs **two** runs
so width 500 is ~5× the callgrind time. ⓘ **PAT publishes in A and may not need
it — a PAT-side call, and `results/SYNTHESIS.md` is its authority, not this
file.**

## §6 What adopting the §4 rule costs

* **Nothing** for the `fixed-R4 bound` — A1's flips there are **`ph45` only**,
  and `ph45` already publishes both labelled.
* ⛔ **`ph64` publishes B1 and `ph07` publishes A3**, so both need a second
  labelled column. ⚠ Their `NOTES.md` are in the **gate** digest and **not** the
  measurement digest, so restating costs **one re-gate per row and no
  re-measure**.
* ⚠⚠ **`PROTOCOL_PHP.md` §B2 and the shared `why` block are HASHED** — writing
  this rule into either is a **six-row PHP re-gate**. That is item **55**'s shape
  and item **61**'s, and it is why this file is in `.tasks-php/` and not in a
  pattern's contract.
