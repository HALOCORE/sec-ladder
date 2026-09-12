# TASK_PHP_038_REPORT — review of the statistic findings; F85 attacked

**Role:** research reviewer, alone. **Subject:** `.temp/mgr172/STATISTIC-DECISION-DRAFT.md`
and findings **F83 · F84 · F85 · F86**.
**Probes:** `.temp/php38/` — `settle_37_38.py` · `flip_columns.py` · `item64.py` ·
`fixedterm.py` · `alias.py` · `draws.py` · `blind_and_scalar.py` · `pat_side.py` ·
`minus_one_and_p25.py`. Every one carries `--selftest` must-fire negatives.
Expectations declared in writing before each probe: `.temp/php38/EXPECT.md`.

**Brackets.** `harness/measure.py --check-stale` → **66 record(s), 0 STALE** and
`harness-php/gate.py --tool measure --check-stale` → **14 record(s), 0 STALE**,
**first and last**. Nothing I did moved either. No `git add`/`git commit`; no edit
under `harness/`, `common/`, `patterns/`, `results/`, `pilot/`, `common-php/`,
`patterns-php/`; nothing touched in `.web/`; no `/tmp`.

**The seven `--selftest`s I was asked to run, I ran** (`.temp/php38/selftests.log`):
`identity_null` · `inclusive_ir` · `bc_sweep` · `flip_exact` · `callee_share` ·
`spread_stat` · `null_control` — **all seven PASS.** Two remarks on what a PASS
is worth are in §F86 and §Negatives.

---

## ▶ VERDICTS, one line each

| finding | verdict |
|---|---|
| **F85** — 28 of 38 flips are cross-language, and they survive family C | ⚠ **UPHELD-NARROWED.** The *measurement* is stronger than published: **all 29** cross-language flips are now adjudicated against C and **28 survive**. ⛔ But the **count is 29, not 28** (so 76 % is right and "28 of 38" is not), **one flip is REFUTED by C**, and two of §5's supporting claims are wrong — *"three independent statistics"* and *"the confound is real and present"*. |
| **F86** — three classes, and the exact flip test proves there is no shortcut | ⚠ **UPHELD-NARROWED.** (a) identity **UPHELD** (verified by hand). (b) **UPHELD as algebra**, but *"0 mispredictions over all 366"* is a **logical tautology** and is not evidence — F78's shape one level up. (c) **too strong as written**; the operative conclusion survives for a simpler, unconditional reason the draft under-uses. The **BLIND** taxonomy inverts the evidence on 5 of 14 cells. |
| **F84** result 1 — `check.py`'s `−1.00` class is the **slope** | ✅ observation **UPHELD** on a PAT row (`p11`). ⛔ **MECHANISM REFUTED.** It is **not** the slope: it is **exactly one instruction per kernel call in `main`**, and the number is already in every committed record as `main_exclusive_ir`. |
| **F84** result 2 — B can miss real work | **UPHELD-NARROWED.** The observation stands; the mechanism is not "a two-directional error" but **the draw** (see §NEW). |
| **F83** — the null was measuring real work; B's defect is attribution | ✅ **UPHELD** on its conclusion (B and C agree by two methods). ⛔ **The environment control is worthless** — it tests a mechanism that **cannot apply to `ph03`**, whose per-call buffer is on the **heap**. The mechanism F83 itself names is **UNTESTED**. |
| **F83**'s `p25` residual (§3.3) | ✅ **ANSWERED, and it is not a mystery: it is the draw.** Two other draws read **exactly 0.000**; the largest reads **+166.85** against C's **+167.872**. |
| ⭐ **NEW** — family B is **one draw of a sampling distribution** | **A previously unreported error source, larger than F84's**, with a named mechanism in the committed driver source. |
| §1.5 — is cross-language callee work rung-attributable? | **RULED: YES, on this corpus, and the draft is right to assert it — but its reason is not the one it gives.** See §1.5. |
| §4.2 — 37 or 38 | **SETTLED: both, and neither script misreads a number.** |

---

## §1 F85 — THE PRIMARY TARGET

### §1.1 ⭐ ITEM 64 IS MEASURED. ALL 29 CROSS-LANGUAGE FLIPS, NOT 12.

`.temp/php38/item64.py`, `--selftest` **PASS, 8 must-fire negatives**; profiles from
`.temp/php38/sweep64.sh` (mine, self-contained). Full table in
`.temp/php38/item64.log`.

**I did more than the item asked**, because once the pipeline was checked the extra
cells were cheap and F85's `ph29` half was itself *5 measured of 16*:

| row | cross-language flips | survive family C |
|---|---|---|
| `ph00` | 1 | ⛔ **0** |
| `ph03` | 6 | ✅ **6** |
| `ph07` | 6 | ✅ **6** |
| `ph29` | 16 | ✅ **16** |
| | **29** | **28** |

**`ph03`'s six** (C tracks B to **0.006 pp** on every one):

```
ph03 small  c-gcc   vs verus       A  +8.102  B  -0.413  C  -0.419  W1  -0.510  SURVIVES
ph03 small  c-gcc-h vs verus       A  +7.647  B  -0.824  C  -0.830  W1  -0.920  SURVIVES
ph03 large  c-gcc   vs unsafe      A  +6.044  B  -0.240  C  -0.242  W1  -0.258  SURVIVES
ph03 large  c-gcc   vs verus       A  +6.044  B  -0.182  C  -0.184  W1  -0.200  SURVIVES
ph03 large  c-gcc-h vs unsafe      A  +5.640  B  -0.618  C  -0.620  W1  -0.635  SURVIVES
ph03 large  c-gcc-h vs verus       A  +5.640  B  -0.560  C  -0.562  W1  -0.578  SURVIVES
```

**`ph07`'s six** (C moves B by up to **0.92 pp**, and in **both directions** — note
`vs verus` moves *toward* zero while `vs unsafe` moves *away*):

```
ph07 small  c-clang   vs safe_tuned  A  +0.831  B -11.936  C -12.853  W1 -12.988  SURVIVES
ph07 small  c-clang   vs unsafe      A +12.323  B  -4.535  C  -4.943  W1  -5.187  SURVIVES
ph07 small  c-clang   vs verus       A +12.323  B  -6.019  C  -5.658  W1  -5.892  SURVIVES
ph07 small  c-clang-h vs safe_tuned  A  +1.132  B -11.695  C -12.609  W1 -12.747  SURVIVES
ph07 small  c-clang-h vs unsafe      A +12.657  B  -4.273  C  -4.676  W1  -4.924  SURVIVES
ph07 small  c-clang-h vs verus       A +12.657  B  -5.761  C  -5.394  W1  -5.631  SURVIVES
```

⚠ **MY DECLARED EXPECTATION WAS WRONG AND I AM SAYING SO** (`EXPECT.md` §E2). I
predicted `ph03`'s flips were the ones at risk, because their B side is **0.18–0.82 %**
while F84 measured `ph03/small`'s *own* R4/R5 confound at **+3.66 %** — nine times
the effect. ▶ **They survive anyway, and by a wide margin**: C reproduces B to
**0.006 pp** on all six. The reason my argument failed is worth recording: the
R4/R5 confound is an **allocator-layout difference between two byte-identical
kernels**, which is *specific to that pair*; it is not a noise floor that applies
to every comparison on the row. **F84's `~266 Ir/call` is not a per-row error bar,
and quoting it as one — which is what my prediction did — is the "do not max a null
over a dimension" error in a new dimension: over the COMPARISON.**

### §1.2 ⛔ THE COUNT IS 29, NOT 28 — AND THE DRAFT CONTRADICTS ITSELF ON IT

`.temp/php38/flip_columns.py`, an independent re-tally from the committed records.
Its **N5 FAILED against F85's published figure** and that is the finding.

* **29** of the 38 flips are C-vs-Rust. **28 of 38 = 73.7 %**, not 76 %. The 76 %
  the draft prints is correct for **28/37** or **29/38** — i.e. the numerator comes
  from `callee_share.py`'s 37-flip definition and the denominator from
  `flip_exact.py`'s 38-flip one. **F85's headline mixes the two populations.**
* ⭐ **The draft refutes itself in the next paragraph**: §5 says *"The remaining
  **9** flips are Rust-vs-Rust and ALL are `ph45` (6) and `ph64` (3)."*
  **38 − 9 = 29.** Both numbers are in the same section.
* ⭐ **And the manager's own scratch file already had 29.** `.temp/mgr172/mine.txt`
  lists all 38; its first 29 lines are `ph00` 1 + `ph03` 6 + `ph07` 6 + `ph29` 16,
  and the last 9 are `ph45`/`ph64`. The tally was right in the file and wrong in
  the finding.
* **The missing 29th is `ph00/small c-clang vs verus`**, A **−0.111** / B **+0.046**
  — one of the three sub-0.2 % flips the draft names *in a different sentence*.
  It looks as though it was dropped as sub-threshold in the column tally and kept
  in the class table.

⚠ **And the by-column table in §4 has a second, independent error.** It sums to
**37**, and it mislabels a column:

| the draft says | measured |
|---|---|
| fixed-R4 bound R3 vs R4 — `ph45` 2 | ✅ 2, `ph45` |
| the R4/R5 null — 3 | ✅ 3, `ph45` 2 + `ph64` 1 |
| the safe span **R2 vs R3** — `ph45` 2 · `ph64` 2 | ⛔ **2, `ph64` only** |
| — *(no row)* | ⛔ **2, `ph45`, and they are `safe_tuned vs verus` = R3 vs R5** |
| cross-language — 28 | ⛔ **29** |

`ph45`'s 2 flips assigned to *"the safe span R2 vs R3"* are in fact **R3 vs R5**
(`safe_tuned` vs `verus`); the draft has **no column for R3 vs R5**, and the
`ph45` R2-vs-R3 pair it is thinking of is **BLIND**, not a flip. ✅ The
**headline bound (R3 vs R4) really is `ph45`-only with 2 flips** — that part
is exact.

▶ **The correct sentences.** *"**29 of 38** sign flips (**76 %**) are
cross-language"* and *"**28 of the 29 survive family C**; the one that does not is
`ph00/small c-clang vs verus`, where A and B are both under 0.15 %."*
⚠ **Note the coincidence, because it will mislead somebody**: the number **28** is
in both the published claim and the corrected one, attached to a different
denominator and a different proposition.

### §1.3 ⭐ THE FIXED TERM — MEASURED, AND IT DOES DIFFER BY LANGUAGE

`.temp/php38/fixedterm.py`. `n_iters` is at offset 0 of every input file, so one
binary can be run at several `n` and `Ir(n) = FIXED + n·SLOPE` fitted. **My
[100,200] slope reproduces every published `marginal_ir_per_call` to < 1 Ir (N4),
so this is family B and not a lookalike.**

| | FIXED, C rungs | FIXED, Rust rungs | mean Rust − mean C |
|---|---|---|---|
| `ph29/small` | 153,578 .. 162,907 | 332,169 .. 338,695 | **+176,951 Ir** |
| `ph03/small` | 192,462 .. 195,026 | 368,463 .. 370,428 | **+176,154 Ir** |

⭐⭐ **Two independent rows agree to 0.45 %.** The answer to §1.3 is **YES**: there
is a language-bound fixed per-program term of **≈ 176 k Ir** that every Rust rung
pays and no C rung does. ⚠ I have **not** decomposed it into std init / `lang_start` /
panic runtime, and I am not going to invent that; it is a measured constant, not a
named mechanism.

**And the consequence is exactly the one the task predicted, quantified:**

* **B is immune.** It is a slope of *one* binary at two `n`; `FIXED` cancels
  algebraically. (⚠ My N6 tried to *test* that and failed — for a different
  reason, see §NEW. The algebraic cancellation is not in doubt; my test for it
  was the wrong test, and I would not have noticed without the declared
  expectation.)
* **C is immune.** It is the kernel's call tree and excludes `main` and start-up
  by construction.
* ⚠⚠ **W1 is contaminated, by `FIXED/n`, and this fully accounts for the C-vs-W1
  gap in F85's own table:**

| cell | predicted `FIXED/n` as % | F85's measured C→W1 gap |
|---|---|---|
| `ph03/small` (n = 25,000) | 0.094 % | `c-gcc vs verus` −0.419 → −0.510 = **0.091 pp** |
| `ph29/large` (n = 12,000) | 0.14 % | `c-gcc vs safe_naive` −1.064 → −1.188 = **0.124 pp** |
| `ph29/small` (n = 25,000) | ~0.52 % | `c-clang vs safe_tuned` −4.853 → −5.275 = **0.422 pp** |

⛔ **SO F85's SENTENCE *"A VERSUS THREE INDEPENDENT STATISTICS THAT AGREE WITH EACH
OTHER TO ~2 pp"* IS WRONG, AND ITS OWN §1 TABLE HAS THE EVIDENCE.** C and W1 are
**nested scopes of a single callgrind run** (C ⊂ W1), taken from the *same* profile
as A. Their agreement is not corroboration — and their *disagreement* is now a
**known, signed, language-bound offset**, not independent measurement error.
▶ There are **two** methods here, not three: **B** (two runs, a slope) and the
**single profile** that yields A, C and W1 at three scopes.
⚠ Note the direction: the contamination always makes a C-vs-Rust comparison look
*more* negative in W1 than in C, i.e. **W1 flatters the claim F85 is making.**
✅ **None of this touches a flip verdict** — the offsets are 0.09–0.52 pp against
A-side effects of 0.8–33 pp.

### §1.4 ▶ THE CONTROL: IS IT STRONG ENOUGH? — **YES, and it is stronger than the draft claims for it.**

`ph29`'s two non-flipping comparisons (`c-gcc vs safe_naive` small, `c-gcc vs
safe_tuned` large) agree in sign across **all four** families — reproduced here
(`item64.py` N8: `+39.92/+17.85/+14.55/+13.83` and `+51.40/+7.04/+6.85/+6.61`).

**Why it is a real control.** A pipeline artefact in *family A* would have to be
sign-preserving on these two and sign-flipping on the other 27 — and the two
controls share `c-gcc`'s A value with flipping comparisons on the same row and
input. So a bug in how A is read is excluded.

⚠ **But it is narrower than "a pipeline artefact would have moved them too."** It
does **not** exclude:

1. a *magnitude* error in A — both controls have A **2.3×** and **7.3×** the
   whole-program figure, so A could be badly wrong and still same-signed;
2. anything in **B**, which is where the artefacts actually are (§NEW measures B
   moving 14 % on this very row);
3. anything **input-specific** — there are only two controls and they are on
   different inputs.

▶ **Much better controls are already in the table and unclaimed**: the
**`-h` (hardened-C) cells**. `c-clang` and `c-clang-h` differ by one branch, and
every one of the 8 `-h` flips lands within **0.04 pp of its non-`-h` twin on all
four families** (e.g. `ph29/large vs safe_tuned`: C **−22.011** / **−22.035**).
That is an 8-fold near-duplicate control across the whole pipeline and it is
strictly stronger than the two the draft names. **Use it.**

### §1.5 ▶ THE RULING: IS CROSS-LANGUAGE CALLEE WORK RUNG-ATTRIBUTABLE?

**RULED: YES on this corpus — so the draft's conclusion is right — but its stated
reason is not sufficient, and the sufficient reason is different.**

**The draft's reason** is F71/item 54: *the C rung really links the shim and really
allocates.* ⚠ **That is a claim about `ph64`, and `ph64` contributes ZERO
cross-language flips.** All 29 are on `ph00`/`ph03`/`ph07`/`ph29`. So the draft
argues the hinge from a row that is not in the population — which is
`PROTOCOL.md` rule 13's shape (the header maintained, the body not).

**The reason that does hold, and it is a *structural* argument rather than a
measured one:**

1. **`PROTOCOL_PHP.md` §B forbids a Rust rung from linking the shim**, so the C
   rung's allocator traffic is **a consequence of the rung's own design choice**,
   not of an accident of layout. The C rung calls `emalloc`/`efree` per call
   because that is what the extracted PHP code does; the Rust rung reproduces the
   tally arithmetically. **Two different programs doing the same job by different
   means is exactly what the ladder is for.** That work *belongs* to the rung.
2. **F83's confound is provably absent here, and the proof is a property of the
   comparison rather than a measurement.** F83's mechanism requires the two
   kernels to be *identical or nearly so*, so that neither rung's code can have
   caused the callee difference. On a C-vs-Rust pair the kernels are **different
   programs in different languages** — `ph03`'s `c-gcc` kernel is 1,161 bytes and
   its `verus` kernel is 708. There is no "neither of them did it" inference
   available.
3. ⚠ **And the measurement that actually settles it is the one nobody quoted**:
   `W1 − C`, the work outside the kernel's call tree, is **0.13 %–2.1 % of the
   cell on every cross-language cell I measured** (`item64.log` §1.3 table), and
   `main` is **14.00 Ir/call for a C rung and 14.01 for a Rust rung** — identical.
   ▶ So on a cross-language comparison, **essentially all the work is inside the
   kernel's call tree, and the call tree is the rung's own.** That is the direct
   evidence, it is cheap, and the draft does not use it.

▶ **Recommended wording.** *"On a cross-language comparison the callee work is
rung-attributable, because §B makes the C rung's allocator traffic a design
property of the rung and because ≥ 98 % of the cell is inside the kernel's call
tree (measured). ⚠ It is NOT attributable on an R4/R5 pair, where the kernels are
byte-identical and F83's layout confound is the whole reading."*
⚠ **The `ph64` argument should be dropped from this hinge, or relabelled as a
warning about a row that has no flips.**

### §1.6 Binary freshness — and the guard is **scope-mismatched to the statistic**

✅ **30 binaries checked, 0 stale.** Every cell I used matches its published
`md5_fn`, per row and per cell (`item64.py` N1, `pat_side.py` N1,
`minus_one_and_p25.py` N1).

⚠⚠ **BUT `md5_fn` HASHES THE KERNEL SYMBOL ONLY, AND FAMILIES C AND W1 COUNT
INSTRUCTIONS THE KERNEL SYMBOL DOES NOT CONTAIN.** `inclusive_ir.py::verify_binaries`
and `bc_sweep.py::fresh` — and the task file's own instruction — guard family A
correctly and guard C and W1 **not at all**: a binary whose kernel bytes match but
whose driver, `main` or link layout differs would pass and move every C and W1
number. There is **no whole-binary digest** in the measurement record.

✅ **A strictly stronger guard is available and free**, and I used it: require the
profile's own totals to reproduce the record's `kernel_exclusive_ir` **and**
`main_exclusive_ir`. That validates the binary *and* the input file end to end.
**It passed on all 29 cells to < 1e-6 and exactly, respectively** (`item64.py`
N2/N3) — so **the manager's numbers are in fact sound.** His guard could not have
told him that; this one can, and it is two lines.

⭐ **And it caught a real poisoning in my own work.** My `pat_side.py` first ran
`p11` with a wrong slug, producing four profiles of a program that had exited
early; `ensure()` then *skipped* them as present. **N2 refused to report numbers**
off them. Deleted and re-run. That is the `.temp/` staleness hazard firing inside
the review of it.

---

## §2 F86

### §2.1 (a) the identity — ✅ UPHELD, verified by hand

Three cells, from raw integers, not by re-running the script:

```
ph29 large  c-gcc vs safe_naive        120,800,132/12,000 = 10066.677667
                                        90,821,295/12,000 =  7568.441250
   a_ratio 1.330085989  b_ratio 0.992039359   1 between?  True   flip?  True
   a_ratio == (s_a/s_b)*b_ratio : 1.330085989194 == 1.330085989194
ph29 small  c-gcc vs safe_naive
   a_ratio 1.399212059  b_ratio 1.178520776   1 between?  False  flip?  False
ph45 small  safe_naive vs safe_tuned    7,851,998/1,500 both cells
   a_ratio 1.000000000  b_ratio 1.233725883   1 between?  False  flip?  False
```

✅ **`inside_share ≡ A/B` and `a_ratio = (s_a/s_b)·b_ratio` identically.** The
draft's call — that *"the share ratio explains the disagreement"* is true by
definition and explains nothing — is **right, and catching it was good work.**

### §2.2 (b) ⚠ IT IS A **TAUTOLOGY**, SO *"0 MISPREDICTIONS OVER 366"* IS NOT EVIDENCE

In `flip_exact.py::analyse`, both sides are computed from the same two reals:

```python
flipped   = sign(apct) != 0 and sign(bpct) != 0 and sign(apct) != sign(bpct)
predicted = min(a_ratio, b_ratio) < 1.0 < max(a_ratio, b_ratio)
```

`apct = 100·(a_ratio − 1)`, `bpct = 100·(b_ratio − 1)`. So `flipped` says *"the
two ratios are on opposite sides of 1"* and `predicted` says *"1 lies between the
two ratios"*. **Those are the same sentence.** They are logically equivalent for
any pair of reals — the only gap is the `eps = 1e-12` in `sign()` against a strict
inequality, a window of width `1e-14` in ratio space.

⚠ **So `N5`'s message is false in both halves.** It says *"any nonzero value means
a family is being read from the wrong cell, since the predicate is algebra."*
A wrong cell read changes `a_ratio` and `flipped` **together and consistently**, so
it can never produce a misprediction. **N5 cannot fire for the reason it gives.**
(It *did* fire once, on the BLIND-as-FLIP bug — i.e. on a **definitional**
inconsistency between the two expressions, which is the only thing it can detect.
The catch was real; the label on it is not.)

▶ **This is F78's shape, one level up**, and it is the second time this round:
an identity presented with an empirical-sounding validation count. ✅ **Mitigated**
— the docstring says *"This is ALGEBRA, so it cannot be confirmed by the data"* —
but **F86's text in `RECAP_PHP.md` does not**, and reads *"A flip occurs iff 1 lies
strictly between the two ratios — **0 mispredictions over all 366**"* under a
heading containing the word **PROVES**. ⚠ **Drop the 366.** It is the number that
makes a tautology look measured.

### §2.3 (c) ⚠ TOO STRONG AS WRITTEN — but the conclusion survives for a better reason

**I tried to build the counterexample the task asked for, and there are two.**

1. **A degenerate certifier exists.** `s_a == s_b` exactly ⇒ `r = 1` ⇒
   `a_ratio = b_ratio` ⇒ **never flips**, for any effect size. So *"no function of
   the shares alone can certify A **at any threshold**"* is **false at threshold
   zero**. Pedantic — but (c) is a *negative existence claim*, and that is exactly
   where the degenerate case has to be excluded in writing.
2. **A useful certifier exists once a minimum effect size is declared.** With
   `δ` a lower bound on `|b_ratio − 1|`:

   > flip ⟺ `b` lies strictly between `1` and `1/r`. If `|b−1| ≥ δ` and
   > `|1/r − 1| ≤ δ`, the interval is empty. ▶ **No flip.**

   That is a function of the shares plus one declared number. ⚠ **It is not
   available today**: the `Ir` floors rows declare (`collapse.min_marginal_ir_per_call`,
   and `check.py`'s derived `rate × work_per_call`) are floors on the **absolute
   level** of a cell, **not on the difference between two cells.** ▶ So (c) is
   **true of this corpus and false as a general claim**, and the honest form is
   *"no function of the shares alone, and this corpus declares nothing else that
   would help."*

⭐⭐ **AND THE DRAFT'S OPERATIVE CONCLUSION IS RIGHT FOR A REASON IT BARELY USES,
WHICH IS STRONGER AND UNCONDITIONAL.** `s ≡ A/B` **by definition**. So *any*
function of the shares already requires **B**. F80's rule was **never** a licence
to skip B — not because the flip condition depends on effect size, but because the
rule's own input is a ratio containing B. The draft's route (via effect size)
makes the conclusion look contingent on an argument that can be attacked; the
one-line route cannot be. ▶ **Lead with it.**

### §2.4 ⚠ THE BLIND CLASS — a test, and the taxonomy inverts the evidence on 5 of 14

`.temp/php38/blind_and_scalar.py`. The 14 BLIND cells, split by fields **already in
the committed records** (`n_fn_nopad`, `fn_bytes`, `md5_fn`) — no new measurement:

```
  5  Δnopad 0, Δbytes 0, md5_fn EQUAL   (byte-identical kernels)
  7  Δnopad 0, Δbytes 0, md5_fn DIFFERS (same executed count, different encoding)
  2  Δnopad != 0                        (ph00/large c-clang vs unsafe/verus)
```

⛔⛔ **THE 5 BYTE-IDENTICAL CELLS ARE NOT "A SAYS NOTHING". THEY ARE CELLS WHERE
A IS PROVABLY RIGHT AND THE WHOLE-PROGRAM FIGURE IS THE ARTEFACT.** They include
`ph03/small unsafe vs verus`, where B reads **−3.524 %** — **F83 and F84's own
headline cell.** Calling that *"A says NOTHING"* labels the one statistic that got
it right as the blind one. ▶ **BLIND is at most 9 of 14, and on 5 of 14 the name is
backwards.**

⚠⚠ **AND MY OWN PROPOSED TEST IS INSUFFICIENT — MY `N5` FAILED AND I AM REPORTING
IT AS A FAILURE.** I predicted that a static-only split would isolate the
archetypal case (`ph45 safe_naive vs safe_tuned`, A +0.000 % against +23.37 %).
It does **not**: that pair has **Δnopad 0 and Δbytes 0** and lands in the *middle*
class beside the innocuous `c-gcc vs c-gcc-h` pairs. **Static equality cannot tell
"correctly zero" from "zero and blind".**

▶ **THE TEST THAT DOES WORK, in two parts, and it needs family C:**

> **(i) WHO IS RIGHT** — from the record alone. `md5_fn` equal ⇒ A's `0` is
> correct and any nonzero whole-program reading is an artefact. `Δnopad ≠ 0` with
> A `= 0` ⇒ the differing instructions never execute (`exec_rate = 0`, F82's own
> machinery).
> **(ii) WHETHER THERE IS AN EFFECT AT ALL** — **family C, not B.** On a BLIND
> cell B is exactly the statistic that cannot be trusted, because 5 of the 14 are
> pairs where B is *known* to be wrong. C scopes to the kernel's call tree, so
> `C ≠ 0` with `A = 0` is a *positive* finding: the effect is real and it is in
> the callees.

⭐ That is a direct argument for **item 62** (build family C) that the draft does
not make: C is not merely "B with one fewer error source", it is **the only
column that can adjudicate the BLIND class.**

### §2.5 ✅ THE 30 COUNTEREXAMPLES ARE EXACTLY THE CASE CLAIMED

Checked the half `flip_exact.py` does *not* print — whether `b` and `1/r` are on
opposite sides of 1. **All 30 are; 0 on the same side.** The manager's diagnosis
is correct and complete. Keeping the refuted form running and labelled was the
right call.

---

## §3 NEW FINDING — FAMILY B IS **ONE DRAW OF A SAMPLING DISTRIBUTION**

⚠⚠ **This is not in F74, F80, F82, F83, F84, F85, F86, `check.py`'s docstring or
any `spec.md` note I read, and on `ph29` it is larger than everything that is.**

`.temp/php38/fixedterm.py` · `alias.py` · `draws.py`, all `--selftest` with
must-fire negatives; **the `[100,200]` slope reproduces every published
`marginal_ir_per_call` to 0.01 Ir, so this is family B.**

**The observation.** `Ir(n)` is **not linear in `n`** on `ph29`:

```
ph29/small  c-gcc   adjacent-span slopes over n = 100..960:  1576.8 .. 2084.2   spread 32.2 %
ph29/small  safe_naive                                       1365.9 .. 1794.2   spread 31.4 %
ph29/small  unsafe                                           1278.8 .. 1695.4   spread 32.6 %
ph03/small  c-gcc                                            7516.6 .. 7519.1   spread  0.03 %
```

▶ **The published `marginal_ir_per_call` for `ph29` is the `[100,200]` draw, and it
is the LARGEST of the seven I measured.** `check.py` fixes `probe_iters` at
`[100, 200]` for **every row in both programmes** (`collapse.probe_iters` in all
seven PHP `spec.md`s I checked).

**The mechanism, from committed source** —
`patterns-php/ph29-recvfrom-alloc/c/main.c`, inside the `SLB-DRIVER` markers:

```c
while (it < inp.n_iters) {
    size_t k = (size_t)(((unsigned __int128)acc * (unsigned __int128)nwin) >> 64);
    uint64_t r = kernel(buf, k * stride, stride);
    acc = acc * 31 + r;
    it = it + 1;
}
```

The window index `k` is a **pseudo-random function of the running accumulator**.
`ph29/small.bin` holds **32** windows (payload 17,616 / stride 550) and per-window
work **varies** (`navail = want % (n_pay+1)`, drawn per window). So `B` is the mean
cost of a **100-element pseudo-random sample** of those windows. Deterministic,
but a *sample*. `ph03/small` also has 32 windows and shows **0.03 %**, because its
per-window work is uniform — **that contrast is the control**.

⚠ **MY FIRST HYPOTHESIS WAS WRONG AND THE NEGATIVE CAUGHT IT.** I predicted plain
*aliasing*: spans that are exact multiples of the 32-window cycle would be stable.
`alias.py::N3` **FAILED** — `(320,640)` gives 1765.82 and `(640,960)` gives
1865.04, both exactly 10 cycles. Then the driver source said why: the sequence is
not indexed by iteration, so there is no cycle to align to. **I published the
refutation rather than the tidy story.**

### Does it matter to F85? — **partly, and precisely**

Every rung computes the same function, returns the same `r`, follows the same
`acc` orbit and visits the **same windows**, so the sampling error largely cancels
in a *ratio*. `draws.py` measures the residue:

```
ph29/small                    F85 B   F85 C   (100,200)  (200,400)  (300,600)  (320,640)  (400,800)  (600,900)  (640,960)
c-clang vs safe_tuned         -2.82   -4.85      -2.82      -4.18      -4.67      -4.68      -4.34      -3.94      -3.88
c-clang vs unsafe             -7.20   -8.90      -7.20      -8.31      -8.68      -8.73      -8.45      -8.12      -8.05
c-gcc   vs safe_naive        +17.85  +14.55     +17.85     +15.08     +14.78     +14.94     +15.12     +15.49     +15.50
```

⭐⭐ **On all three pairs the published `[100,200]` draw is an OUTLIER and every
other draw is within 0.17–0.22 pp of family C.** So:

> ⛔ **F85's closing claim — *"B and C do differ by 2–3 pp on the `small.bin`
> cells — THE CONFOUND IS REAL AND PRESENT"* — MIS-ATTRIBUTES ITS OWN RESIDUAL.
> 90–93 % of that gap is the DRAW, not the attribution confound F83/F84 describe.**

✅ **The sign is stable across all seven draws on every pair** (`draws.py` N5), so
**no flip verdict moves** and F85's conclusion is untouched. ⚠ But two consequences
are not cosmetic:

1. **`inside_share` is not a share on `ph29`.** `s = A/B` divides a mean over
   25,000 draws by a mean over a *different, biased* 100-draw sample. F80's
   `min(inside_share)` rule and F86's `r = s_a/s_b` are arithmetically fine and
   **interpretively void** on any row with heterogeneous per-window work.
2. ⚠ **F84's `ph29` figures inherit it.** *"`ph29/small` R4/R5 B `+8.830` against
   C `+0.061` — **99.31 % artefact**"* and *"`ph29/large` C `+2.383` against B
   `+0.000`"* are both readings of this unstable quantity. The *conclusions*
   (B errs in both directions; B can miss real work) **get stronger**, because a
   sampling error is two-directional by nature. The *mechanism* changes.

▶ **The cheapest next measurement in the programme**, and I am flagging it rather
than guessing: **`ph64`.** It allocates `2n+2` blocks per call (F71, item 54), so
its per-window work must vary strongly — and it is the one row that **publishes
B1**. If its B moves like `ph29`'s, the draft's §2 ban on B is not a style rule,
it is a correctness fix. **UNTESTED by me.**

---

## §4 F83 AND F84 — THE SECONDARY TARGETS

### §4.1 ⛔ F83's ENVIRONMENT CONTROL TESTS A MECHANISM THAT CANNOT APPLY

The task asks *"is three enough, and is env size the right lever? `check.py`
attributes its ±7 to a per-call **stack array**'s alignment — does `ph03`'s kernel
even have one?"*

**It does not.** `patterns-php/ph03-uudecode-bound/c/kernel.c`: the kernel declares
`char *dest = NULL; uint64_t acc = 0; int n, i;` and nothing else; the per-call
buffer is `p = *dest = emalloc(ceil(src_len * 0.75) + 1)` — **a heap allocation.**
The row's own `spec.md` says so: *"ph03's kernel does one `emalloc` + one `efree` +
one `php_shim_reset` per call on the C side and one Vec allocation per call on the
Rust side."*

`check.py`'s mechanism is *"the environment block shifts the **stack pointer** → a
per-call **stack array**'s alignment → a different tail in
`__memset_avx2_unaligned_erms`"*, and it names its four patterns: **p03, p04, p38,
p46**, all of which `memset` a **stack** scratch buffer. It adds that **p08's work
is a heap `memmove`, which is why p08 moves in hundredths.**

▶ **So the answer to *"is three enough"* is: the number of sizes is irrelevant.
Env padding moves the **stack**; `ph03`'s buffer is on the **heap**; the env block
does not relocate the heap. The control could not have fired, and `spread 0` is
what a mechanism that cannot apply looks like.** ⚠ `inclusive_ir.py`'s **N6 is a
negative that cannot fire**, and its PASS carries no information about the cause.

⚠⚠ **AND THE MECHANISM F83 ITSELF NAMES IS UNTESTED.** F83 says the `+265.924` is
*"caused by binary layout"*. `check.py` documents that mechanism too, and it is a
**different** one — p02's: *"the two binaries differ in size and the destination
buffer therefore lands at a different alignment."* `ph03`'s two binaries have
**byte-identical kernels** (`md5_fn 338505795e…`) and **different sizes**
(`binary_text_bytes` 259,411 vs 259,363; 4,369,960 vs 4,369,896 bytes on disk), so
the heap start genuinely differs. **That is the live hypothesis and nothing in F83
tests it.** A lever that *would* reach it is the heap start (e.g. `MALLOC_TOP_PAD_`)
rather than the environment length — ⚠ **UNTESTED by me**, and `check.py` warns
`MALLOC_*` re-tunes the allocator, so it needs its own control.

✅ **What survives untouched:** F83's *conclusion* — that the `+3.65 %` is real
work, not noise — rests on **B and C agreeing by two methods**, and on the kernels
being byte-identical. The env control is not load-bearing for it. **The finding
should keep the conclusion and drop the control**, or relabel it *"rules out an
environment-length effect, which no mechanism predicted here."*

### §4.2 ⛔ F84's `−1.00` MECHANISM IS REFUTED — AND THE REAL ONE IS IN EVERY RECORD

`.temp/php38/pat_side.py` · `minus_one_and_p25.py`, both `--selftest` with
must-fire negatives (p25's N5 noted in §Negatives).

**Step 1 — the observation reproduces on a PAT row.** `check.py`'s own table puts
**`p11`** at exactly `−1.00` at `-O3 isolated` on both inputs. Measured:

```
p11  small   A +0.000   C +0.000   B -1.000   W1 -0.992
p11  large   A +0.000   C +0.000   B -1.000   W1 -0.991
```

**Step 2 — and W1 refutes the mechanism.** W1 is a **one-run whole-program
average**. A *slope-method* artefact cannot appear in it. On `ph00` — F84's own row:

```
ph00 small (n = 200,000)   A +0.000   C +0.000   B -1.000   W1 -1.000
ph00 large (n =  20,000)   A +0.000   C +0.000   B -1.000   W1 -1.000
```

**W1 tracks B, not C, on both rows and all four cells.**

**Step 3 — the mechanism, named, from a field already in every committed record:**

```
ph00  small.bin  n=200,000   kernel_excl Δ=0   main_exclusive_ir Δ= -199,995   = -1.00/call
ph00  large.bin  n= 20,000   kernel_excl Δ=0   main_exclusive_ir Δ=  -19,995   = -1.00/call
p11   small.bin  n=  6,000   kernel_excl Δ=0   main_exclusive_ir Δ=   -6,001   = -1.00/call
p11   large.bin  n=  1,500   kernel_excl Δ=0   main_exclusive_ir Δ=   -1,501   = -1.00/call
```

⭐⭐⭐ **THE `−1.00` IS EXACTLY ONE INSTRUCTION PER KERNEL CALL IN `main`.** Four
cells, two rows, two programmes, and it is `measure.py`'s own `main_exclusive_ir` —
**a field the harness has been recording all along and nobody read.** The `verus`
build's `main` loop runs one instruction fewer per iteration than the `unsafe`
build's; the kernel symbol and its whole call tree are identical, which is why A
and C both read `0` and why **B and W1 are both right**.

▶ **So the corrected claim is *better* than the published one, and cheaper:**

> `check.py`'s undocumented *"34 of them exactly `−1.00`"* class is **one
> instruction per kernel call in `main`**, outside the kernel's call tree. It is
> **not** a slope artefact — a one-run whole-program average reads it too. ⭐ And
> it is **checkable from the committed records with no callgrind at all**:
> `main_exclusive_ir` is in every cell of every `results*/…json`.

⚠ **Scope, stated rather than assumed.** This is 2 rows of the 34 cells. It is a
*mechanism* that predicts the exact value on both, and it is falsifiable per cell
from committed data — but *"all 34 are this"* is **UNTESTED** and the whole-class
sweep is a ~20-line script over `results/*.json`. **Do that before writing 34.**
⚠ And note: F84 said *"a whole documented class of that table is the **measurement
method**, not the program."* **The opposite is true.** It is the program — just
not the *kernel*.

### §4.3 ✅ §3.3 ANSWERED — `p25`'s +101.65 RESIDUAL IS THE DRAW

**My first hypothesis was refuted by measurement.** I predicted the residual was
work outside the kernel's call tree (`main` and its callees). Measured on `p25/large`:

```
p25 large   A +0.000   C +167.872   B +269.520   W1 +167.870
            W1 - C = -0.002/call   main alone = -0.000/call
```

**`W1 − C` is −0.002.** There is essentially **no** out-of-tree work. Hypothesis
dead.

What is left is the only other difference between B and C: B is a two-point slope
at `probe_iters [100,200]`, C is a one-run average at `n_iters = 20,000`. Measured
at five draws:

```
span          B unsafe     B verus    B diff   vs C +167.872
(100, 200)    5379.390    5648.270   268.880       +101.008     <- the published draw
(200, 400)    5373.130    5373.130     0.000       -167.872
(400, 800)    5380.535    5380.535     0.000       -167.872
(800, 1600)   5605.667    5614.979     9.311       -158.561
(1600, 3200)  5576.450    5743.300   166.850         -1.022
```

⭐⭐ **Two draws read EXACTLY 0.000. The largest reads +166.85 against C's
+167.872 — 1.02 Ir apart.** ▶ **The residual is the draw**, and F83's
*"~62 % is real call-tree work and ~+101.65/call is a method artefact of the
slope"* is right in substance with the mechanism now named. It is the **same**
mechanism as §3, on a PAT row, and it converges to C as the span grows.

⚠ ***"Method artefact of the slope"* is the right phrase HERE and the wrong phrase
in F84 result 1** — §4.2. The two were published together as one idea and they are
two different things: `p25`'s residual **is** the two-point method; `ph00`'s
`−1.00` **is not**. A one-run W1 separates them in one line, and neither finding
computed it.

---

## §5 TRAPS AND HOUSEKEEPING

### §5.1 ✅ §4.2 SETTLED — 37 *and* 38, and neither script misreads a number

`.temp/php38/settle_37_38.py`, `--selftest` **PASS, 6 negatives**, reproducing
**both** counts from **one** enumeration of 366. Two definitional differences that
run in **opposite** directions:

```
in flip_exact ONLY  (below callee_share's FLIP_MIN = 0.2 pp floor)   3
    ph00 small    c-clang vs verus       A -0.1110%  B +0.0460%
    ph45 small     unsafe vs verus       A +0.0384%  B -0.1829%
    ph45 large     unsafe vs verus       A +0.0054%  B -0.1940%
in callee_share ONLY (BLIND with B > 0)                              2
    ph45 small safe_naive vs safe_tuned  A +0.0000%  B +23.3726%
    ph45 large safe_naive vs safe_tuned  A +0.0000%  B +23.7238%

38 - 3 + 2 = 37
```

1. **`callee_share.py` applies a magnitude floor** (`FLIP_MIN = 0.2` pp) and
   `flip_exact.py` does not.
2. ⚠ **`callee_share.py` writes the sign test as `(a > 0) != (b > 0)`, which puts
   `a == 0` in the same bucket as `a < 0`.** That is a **real defect**: the same
   BLIND cell is scored a flip or not **depending on which way B happens to
   point**. `a == 0, b > 0` counts; `a == 0, b < 0` does not.

▶ **Which matters:** the second one, because it is asymmetric and undeclared. And
it matters *now* — §1.2 shows **F85's column tally was taken from the 37-list while
its headline denominator came from the 38-list.** ⭐ `.temp/mgr172/theirs.txt` is
**0 bytes**: the diff the manager abandoned is what would have caught it.

### §5.2 ⚠ §4.1 — WHAT COULD **NOT** BE REPRODUCED FROM A FRESH CLONE

| | reproducible from a fresh clone? |
|---|---|
| **F82**'s figures (`identity_null.py`) | ✅ **Yes.** Reads committed `results*/…json` only. Script must be rewritten; the data is all committed. |
| **F86**'s 366 / 38 / 14, F80's per-class scoring, the 30 counterexamples | ✅ **Yes** — and I re-derived all of them from committed records with independently written code (`settle_37_38.py`, `flip_columns.py`, `blind_and_scalar.py`). |
| **F84** result 1's mechanism (as corrected in §4.2) | ✅ **Yes**, and with **no callgrind** — `main_exclusive_ir` is in every record. |
| **F83 / F84 / F85**'s family **C** and **W1** columns | ⛔ **NO.** They need (i) a `callgrind_annotate --inclusive=yes` pipeline that exists only in `.temp/` — `measure.py::callgrind_ir` records **exclusive** only, for two needles; and (ii) a `.temp/build/` binary set that a fresh clone does not have and must rebuild. **This is open item 62's whole point and open item 65's defect.** |
| **F83**'s `+205.94` / `+56.98` libc localisation and its `181,733,873` env control | ⛔ **NO.** Per-function differencing over gitignored profiles. |
| ⚠ Even **with** the binaries | the record has **no whole-binary digest** — only `md5_fn`/`md5_fn_norel`, which cover the kernel symbol. See §1.6. |

▶ **The general rule this supports:** any figure that is not computable from
`results*/…json` plus committed sources is, today, unreproducible. **Family C is
the whole of that set** — which is the strongest argument for item 62 in the file.

### §5.3 ✅ CLEAN NEGATIVES — attacks I ran that did **not** land (rule 6)

Worth as much as the findings, and they stop the next agent re-running them:

1. **F85's `ph29` table is exactly right.** My independently written code
   reproduces **all 7** of its C and W1 cells to **0.02 pp** (`item64.py` N6).
   Not one digit moved.
2. **The flips do not depend on the `-h` cells being ignored.** All 8 `-h`
   cross-language flips survive C, within 0.04 pp of their non-`-h` twins.
3. **`ph03`'s flips survive, against my own prediction** (§1.1).
4. **Callgrind is deterministic here.** My profiles reproduce the manager's
   kernel-inclusive `Ir` **exactly** on all 5 overlapping cells (`item64.py` N5).
5. **No binary is stale.** 30 of 30 match `md5_fn`; 29 of 29 additionally
   reproduce `kernel_exclusive_ir` and `main_exclusive_ir` from the profile.
6. **Pair orientation is not a confound** in the 37/38 gap (`settle_37_38.py` N3:
   0 of 366 verdicts change under reversal).
7. **`kernel_exclusive_ir` is never 0** in the population, so `flip_exact`'s
   truthiness filter and `callee_share`'s `is None` filter see the **same** 366
   comparisons (`settle_37_38.py` N4). The gap is definitional, not population.
8. **`ph03` is NOT affected by the draw** — 0.03 % over ten spans (`alias.py` N6).
   The new finding is **not** a blanket indictment of family B.
9. **`p25/small` still reads 0 on A, C and B** — F83's stated control, intact.
10. **The scalar restatement's counterexample list is exactly what it claims**
    (§2.5), 30 of 30.

### §5.4 ⚠ MY OWN ERRORS, AND WHICH NEGATIVE CAUGHT EACH

Declaring expectations first caught three things I would otherwise have published:

| my claim | what happened |
|---|---|
| *"`ph03`'s flips may not survive C"* (E2) | **Refuted by measurement.** I had quoted F84's `~266 Ir/call` as a row-level error bar; it is a property of one *comparison*. §1.1. |
| *"the drift is window aliasing"* | **`alias.py::N3` FAILED.** Multiple-of-32 spans are not stable. The driver source gave the real mechanism. §3. |
| *"the fixed term cancels in B — test it by adjacent-pair slopes"* (`fixedterm.py` N6) | **The test was wrong, not the claim.** N6 failed on nonlinearity, which is a *different* fact. Algebraic cancellation is not in doubt; I would not have separated the two without the written expectation. |
| *"a static-only split isolates the genuine BLIND case"* (`blind_and_scalar.py` N5) | **FAILED.** `ph45`'s archetypal case has Δnopad 0 and Δbytes 0. The test needs family C. §2.4. |
| `pat_side.py` ran `p11` under a wrong slug | Four profiles of a program that exited early; `ensure()` skipped them as present. **N2 refused to report.** §1.6. |
| `minus_one_and_p25.py::N5` | My `[100,200]` `p25/verus` slope is **5648.27** against the published **5648.91** — 0.64 Ir. `unsafe` reproduces exactly. This is `check.py`'s own *"different environment ⇒ different draw, marginals NOT comparable"* rule; 0.64 Ir against the ±269 → 0 effect being measured. **Reported, not waved away.** |

### §5.5 Miscellaneous, small but real

* ⚠ **`bc_sweep.py`'s docstring contradicts the finding it supports.** It says
  *"TRUE ON 7 AND FALSE ON 5"*; its own run prints **6 agree / 6 disagree**, and
  `RECAP_PHP.md` F84 and `NOTES.md` §9 both say **6**. The docstring is stale.
* ⚠ **`bc_sweep.py::N6`'s *"all 8 true-null cells"* undercounts by F82's own
  corrected predicate.** `NULL_LEVELS = ("exact", "multiset")` excludes `ph07`
  (`norel`), which **F82 rescues via `Δnopad == 0`**. `ph07` reads A = 0 in the
  table, so including it would make the claim *stronger* — 10 cells, not 8. The
  probe uses the predicate F82 refuted.
* ⚠ **The draft's §5 heading says *"the 37 sign flips"* while its own class table
  says **38***. With §1.2's 29, three different flip counts appear in one section.
* ✅ **`PROTOCOL.md` rule 10:** this report file was written before I cited it.
* ⚠ **Rule 11 note for the manager**: nothing I read moved under me. The only
  concurrent writer flagged to me was `.web/`, which I never opened.

### §5.6 Verus / `grep` / process discipline

* **No Verus run was needed** — nothing in scope touches a proof. So there is no
  error text to read, and the rule is noted rather than exercised.
* **`grep -a` throughout.** ⚠ And I took §10's lesson seriously: every prose claim
  I checked in `RECAP_PHP.md`, `check.py` and the draft I checked by **reading the
  section**, not by matching a phrase. The one place it mattered was `check.py`'s
  stack-array sentence (§4.1), which wraps across three lines and no line-based
  pattern would have found.
* **One tracked background job at a time; no `sleep` pollers; no `pkill`.** Every
  long run used `timeout`.
* **`~266 Ir/call` is quoted with its row throughout** — `ph03/small`, R4/R5 —
  and §1.1 records that treating it as a row-level bound was *my* error.

---

## §6 ⭐ WHAT I THINK THE DECISION SHOULD BE (draft §4)

**Adopt §4.2 — publish both, labelled, always — and make three changes.**

The core decision is **right and I would land it**. It is reached independently by
two routes (F86's algebra and `TASK_PHP_037`'s *"never price a variant on two
runs"*), it is what `ph45` already does, and my work strengthens rather than
weakens it. But:

**1. ⛔ THE SECOND COLUMN MUST BE **C**, NOT B — AND THAT IS NOW A CORRECTNESS
REQUIREMENT, NOT A PREFERENCE.** The draft says *"publish both"* and leaves the
whole-program half to whatever the row has. Three separate results say it has to
be C:

* B's *level* moves **32 %** across draws on `ph29` and its *ratio* by up to
  **3.1 pp**, and the published draw is an outlier (§3);
* **90–93 %** of the B-vs-C gap F85 calls *"the confound"* is that draw (§3);
* on **5 of 14** BLIND cells B is *known* to be wrong while A is provably right
  (§2.4) — so B cannot adjudicate the class the draft says needs adjudicating.

▶ **So open item 62 is not a nice-to-have; it is the precondition for §4.2.**
Publishing "A and B, labelled" publishes one good number beside one whose value
depends on `probe_iters`. ⭐ **Raise item 62 to the top of the queue and make it
the next task.** ⚠ And §2's *"B keeps exactly one job — anti-collapse"* is
**exactly right and should be stated more strongly**: for a *floor* test a draw is
fine, because any draw clearing the floor proves the loop ran.

**2. ⚠ W1 IS NOT THE THIRD OPINION.** Report it if you like, but not as
corroboration: it is `C + FIXED/n`, and `FIXED` is language-bound at **≈ 176 k Ir**
(§1.3). Either publish `C` and cite W1 as *"C plus a measured start-up offset"*, or
drop it. ✅ The draft's §4.3 *"two labelled quantities, never three"* already says
this — **it just does not know that W1 is the third one it is warning about.**

**3. ⚠ ADD ONE SENTENCE THE DRAFT IS MISSING: NAME `probe_iters`.** Every figure in
family B is *"the mean over draws 100–199 of the driver's pseudo-random window
sequence"*. That is a scope, not a caveat, and by the draft's own principle —
name the statistic beside the figure — **it belongs in the label.** A reader who
knows `B = marginal_ir_per_call` still does not know it is a 100-sample draw.

**And what I would *not* change.** §4.4 — *"where the two cells' callee usage
differs for reasons unrelated to the rung's safety strategy, no statistic separates
it; say so, do not pick a column"* — is the best paragraph in the draft and it is
the one my §1.5 ruling turns on. **Keep it verbatim.** ⭐ Likewise §3's *"A is
exact AND it is blind, and both halves are measured"*: the exactness half is
`ph45`'s `exec_rate 1.0000` twice with `ph64`'s `0.5093/0.5100` as the too-clean
control, and it is the most carefully built claim in the round.

⚠ **One process point, since the decision governs how every row publishes.** The
draft's §4 is correct in structure and wrong in three of its numbers (29 not 28;
76 % against the wrong denominator; the R2-vs-R3 column). **All three are in the
by-column table, all three are re-derivable from committed JSON in about twenty
lines, and none of them needed a measurement.** ▶ Whatever lands in
`.memory-php/` should be generated by a committed script that re-derives its own
table, the way F74's rule was saved by `callee_share.py` printing
`⚠⚠ THESE REFUTE THE MECHANISM` unprompted. **A hand-tallied table in the
authoritative layer is the one thing this round has shown does not survive.**

---

## §7 Artefacts (CLAUDE.md constraint 6)

`.temp/php38/` keeps **9 `--selftest`ed `.py` probes**, `EXPECT.md` (expectations
declared before the measurements), `sweep64.sh` (the regeneration entry point) and
**every run's `.log`** — the evidence.

**Deleted as re-derivable:** all `.bin` probe inputs under `.temp/php38/probe/`
and all `.out` callgrind profiles under `.temp/php38/{cg,fixedcg,aliascg,patcg,p25cg}/`.
Each is rebuilt by a named script — `sweep64.sh` (item 64 and `ph29`),
`fixedterm.py`, `alias.py`, `draws.py`, `pat_side.py`, `minus_one_and_p25.py` —
and every one skips existing files, so re-running is cheap and idempotent.
⚠ **`.temp/mgr172/cg/` is the manager's and I left it alone.**
⚠ **`pat_side.py`'s `ensure()` and `sweep64.sh`'s `run()` both SKIP existing
profiles, which is how my own `p11` runs got poisoned (§1.6). If you re-run after
changing a path, delete the directory first.**

**Brackets, last:** `harness/measure.py --check-stale` → **66/0**;
`harness-php/gate.py --tool measure --check-stale` → **14/0**.
