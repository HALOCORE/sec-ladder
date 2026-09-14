# TASK_PHP_049 REPORT — **IS THE C BASELINE A FREE PARAMETER?**
## Attacking `RECAP_PHP.md` open item 111

**Role:** research reviewer / analyst, alone. **Subject:** the manager's own
item 111, from one probe.
⛔ **No build, no callgrind run, no edit under any hashed path.** Every number
below comes from committed records or from callgrind profiles that already
existed under `.temp/mgr172/cg/`.

---

## ⛔⛔ VERDICT ON ITEM 111 — **UPHELD-NARROWED, AND ITS HEADLINE IS REFUTED**

> **Item 111's TITLE — *"THE BIGGEST OPEN THREAD MAY BE A `gcc` PROPERTY"* — is
> REFUTED. Its OPERATIVE INFERENCE — *"against `c-clang`, A1 lands in the same
> regime as the three other statistics"* — is REFUTED, by a like-for-like
> measurement the manager did not take. What SURVIVES, and survives strongly,
> is everything item 111 says about LABELLING: the C baseline moves published
> signs, nothing enforces naming it, and the defect reaches deeper than item
> 111 found — into `.memory-php/`, the authoritative layer.**

Four sub-verdicts:

| item 111's claim | verdict |
|---|---|
| the four `ph29` figures | ✅ **UPHELD** — all four reproduce to the digit (§1.1) |
| the 24-cell corpus-wide clang-vs-gcc table | ✅ **UPHELD** — all 24 reproduce to the digit; its **summary triple is wrong** (§2.2) |
| *"against `c-clang`, A1 lands in the same regime as the three other statistics"* | ⛔⛔ **REFUTED** — the three others were computed against **`c-gcc`**; like-for-like they are **−27.78 % / −27.61 %**, not ≈1 % (§1.3) |
| *"the biggest open thread MAY BE a `gcc` property"* | ⛔⛔⛔ **REFUTED** — **21 of F85's 29 cross-language flips are `c-clang`-baseline; at a 1-pp floor it is 17 of 17** (§2.1) |
| *"an `O0` gap is not a symbol-boundary artefact"* | ⛔ **REFUTED as stated** — and **`c-clang` is the only cell in the corpus that moves** (§3.1) |
| *"`isolated` and `whole` agree to ≤ 0.1 pp on six of eight rows"* | ⛔ **WRONG — five of eight** (§3.1) |
| the static-size / cold-helper leg | ✅ **UPHELD, and by better evidence than the manager's** — the gap survives family C and W1 (§3.2) |
| *"Row 1's rule is correct and nothing enforces it"* | ✅ **UPHELD — and UNDERSTATED**: a **stronger** rule already exists in `.memory/`, and the unlabelled figure is in `.memory-php/` (§4) |

⭐ **It is NOT undecidable without family C.** Family C already existed for
`ph29`'s six cells in `.temp/mgr172/cg/` and settled the attribution question
for that row. **It IS undecidable without family C on the other seven rows**
(§3.3).

---

## §0 BRACKETS

| | opening | closing |
|---|---|---|
| `python3 harness/measure.py --check-stale` | **`66 record(s) examined, 0 STALE`** | **`66 record(s) examined, 0 STALE`** |
| `python3 harness-php/gate.py --tool measure --check-stale` | **`18 record(s) examined, 0 STALE`** | **`18 record(s) examined, 0 STALE`** |

**Unmoved.** `git status --porcelain` at close shows exactly one entry:
`?? .tasks-php/cbaseline_check.py` — the deliverable-4 checker, in **no digest**.
Nothing under `harness/`, `common/`, `common-php/`, `patterns/`, `patterns-php/`,
`results/`, `results-php/`, `pilot/`, `.web/`, `RECAP_PHP.md` or `.memory-php/`
was written.

**Probes** (all `--selftest PASS`, all under `.temp/php49/`, generators kept):
`sweep.py` (5 negatives) · `likeforlike.py` (6) · `baseline_split.py` (5) ·
`o0_leg.py` (5). **Checker**: `.tasks-php/cbaseline_check.py` (9 negatives
inside the file, per `PROTOCOL_PHP.md` §H).

⚠ **A structural fact that scopes everything below, and item 111 does not state
it:** in `results-php/`, **`large.bin` is measured at `O3` only**, and at
`O3`/`whole` **`kernel_exclusive_ir` is `null` on every cell of every row** (the
kernel is inlined into `main`). So **family A exists in exactly four
`(input, opt, mode)` combinations**, not eight:

```
small.bin O0/isolated   small.bin O0/whole   small.bin O3/isolated   large.bin O3/isolated
```

The full A1 cross-product is therefore **8 rows × 4 combos × 4 Rust rungs = 128
pairs**, and **§2's "extend it to `large.bin`" yields one column, not three.**
(`.temp/php49/sweep.py` negatives N4b/N4c/N6 pin this.)

---

## §1 DELIVERABLE 1 — RE-DERIVATION, THE SELECTION QUESTION, AND THE BASELINE OF THE "THREE OTHER STATISTICS"

### 1.1 ✅ All four figures reproduce to the digit

Source: `results-php/ph29-recvfrom-alloc.json`, `cells[].ir[<input>].kernel_exclusive_ir`,
÷ `inputs[<input>].n_iters`; statistic **A1**; `O3`/`isolated`; rung
**`safe_naive`**; effect = *"C dearer than the rung by"* = `(C − R)/R × 100`.

| input | baseline | item 111 | re-derived | file |
|---|---|---:|---:|---|
| `large.bin` | `c-gcc` | +33.01 % | **+33.0086 %** | `results-php/ph29-recvfrom-alloc.json` |
| `large.bin` | `c-clang` | −4.36 % | **−4.3566 %** | same |
| `small.bin` | `c-gcc` | +39.92 % | **+39.9212 %** | same |
| `small.bin` | `c-clang` | +0.95 % | **+0.9530 %** | same |

⭐ Arithmetic is not where item 111 is wrong.

### 1.2 ⛔ THE SELECTION QUESTION — the full 128-pair sweep

`.temp/php49/sweep.py`. Every row × every Rust rung × every input × `O0`/`O3` ×
`isolated`/`whole` **that A1 exists for**.

| magnitude floor on BOTH sides | AGREE | **SIGN FLIP** | one side sub-floor |
|---|---:|---:|---:|
| 0.0 pp | 118 | **10** | — |
| 1.0 pp | 113 | **10** | 5 |
| 2.0 pp | 110 | **10** | 8 |

▶ **`c-gcc` → `c-clang` changes the sign of `10 of 128` A1 cross-language pairs
= 7.8 %**, and the count is **stable up to a 2-pp floor on both sides**, so no
flip here is a near-zero artefact.

⭐⭐ **AND THE SHARPEST STRUCTURE IN THE SWEEP, WHICH ITEM 111 DOES NOT HAVE:
ALL TEN FLIPS ARE AT `O3`/`isolated`. ZERO OF THE 64 `O0` PAIRS FLIP.** The rate
at `O3`/`isolated` is **10/64 = 15.6 %**; at `O0` it is **0/64 = 0 %**.

The ten, with their `c-gcc` and `c-clang` values (A1, `O3`/`isolated`):

| row | input | rung | `c-gcc` | `c-clang` |
|---|---|---|---:|---:|
| `ph03` | small | `unsafe` | +8.10 % | −8.40 % |
| `ph03` | small | `verus` | +8.10 % | −8.40 % |
| `ph03` | large | `unsafe` | +6.04 % | −9.71 % |
| `ph03` | large | `verus` | +6.04 % | −9.71 % |
| `ph07` | large | `safe_tuned` | +15.72 % | −5.77 % |
| **`ph29`** | **large** | **`safe_naive`** | **+33.01 %** | **−4.36 %** ← the published one |
| `ph53` | small | `unsafe` | +23.24 % | −13.68 % |
| `ph53` | small | `verus` | +24.81 % | −12.58 % |
| `ph53` | large | `unsafe` | +2.24 % | −17.97 % |
| `ph53` | large | `verus` | +2.75 % | −17.57 % |

▶ **ANSWER TO THE SELECTION QUESTION: the manager did NOT cherry-pick a lone
working row.** Flips occur on **four of eight rows** (`ph03`, `ph07`, `ph29`,
`ph53`), on **both inputs**, and across **three of four Rust rungs**. `ph29` is
not an outlier.
⚠ **But the manager DID pick the single most favourable CELL.** `ph29/large/safe_naive`
has the largest `c-gcc`-side magnitude of the ten (+33.01 %) and its
`c-clang` partner is the smallest of the ten (−4.36 %), which maximises the
rhetorical distance. `ph29`'s own `small.bin` cell is **not** a flip
(+39.92 → +0.95, both positive), and item 111 states that correctly.

### 1.3 ⛔⛔⛔ **YES — THE "THREE OTHER STATISTICS" WERE THEMSELVES COMPUTED AGAINST `c-gcc`. THIS IS WHERE ITEM 111 DIES.**

**The three are B, C and W1.** Their source is
`.tasks-php/STATISTICS_001.md:92-95` —

> *"`ph29/large`, `c-gcc` vs `safe_naive`: **A says C is `+33.01 %` DEARER than
> naive safe Rust; B, C and W1 all say ≈ `1 %` CHEAPER.**"*

— whose underlying table is `.temp/mgr172/STATISTIC-DECISION-DRAFT.md` §5:

```
| large | `c-gcc` vs `safe_naive` | A +33.01 | B −0.80 | C −1.06 | W1 −1.19 |
```

**All three carry `c-gcc` in the row label.** So item 111's sentence —

> *"AGAINST `c-clang`, A1 LANDS IN THE SAME REGIME AS THE THREE OTHER
> STATISTICS ON BOTH INPUTS"*

— compares **A1 computed against `c-clang`** with **B, C and W1 computed against
`c-gcc`**. It is not like-for-like, and the "agreement" is a coincidence between
two unrelated numbers.

#### The like-for-like measurement, taken

`.temp/php49/likeforlike.py`, from the **already-existing** callgrind profiles
`.temp/mgr172/cg/ph29.{c-gcc,c-clang,safe_naive,safe_tuned,unsafe,verus}.{small,large}.out`
(regenerator: `.temp/mgr172/sweep_cg.sh`). **C** = `callgrind_annotate
--inclusive=yes`, rows matching the `kernel` needle. **W1** = `PROGRAM TOTALS`.
The probe's negative **N4 reproduces four of the draft's own C-column figures to
≤ 0.25 pp**, and **N5 reproduces A1's +33.01 / −4.36 to ≤ 0.02 pp**, so the A
and C columns are known to be about the same cells.

**`ph29`, `O3`/`isolated`, *"C dearer than `safe_naive` by"*:**

| input | baseline | **A1** | **C** | **W1** |
|---|---|---:|---:|---:|
| `large.bin` | `c-gcc` | **+33.01 %** | −1.06 % | −1.19 % |
| `large.bin` | **`c-clang`** | **−4.36 %** | ⛔ **−27.78 %** | ⛔ **−27.61 %** |
| `small.bin` | `c-gcc` | +39.92 % | +14.55 % | +13.83 % |
| `small.bin` | **`c-clang`** | **+0.95 %** | ⛔ **−14.66 %** | ⛔ **−14.85 %** |

▶ **Against `c-clang`, the "three other statistics" say `−27.78 %` / `−27.61 %`
on `large` and `−14.66 %` / `−14.85 %` on `small`. They are NOWHERE NEAR ≈1 %.**

▶ **A1 does not agree with them under either baseline:**

| cell | A1-vs-C gap | sign flip? |
|---|---:|---|
| `large`, `c-gcc` | 34.07 pp | **YES** |
| `large`, `c-clang` | 23.42 pp | no (but **6.4× out** in magnitude) |
| `small`, `c-gcc` | 25.37 pp | no |
| `small`, **`c-clang`** | 15.61 pp | ⭐ **YES — an EXTRA flip that `c-gcc` does not have** |

⛔⛔ **So swapping the baseline to `c-clang` does not rescue A1. It shrinks the
`large` gap from 34.07 to 23.42 pp and ADDS a sign flip on `small` that `c-gcc`
did not have.** The A-versus-whole-program disagreement is a property of the
**statistic**, not of the **compiler** — which is what item 62 has always said.

---

## §2 DELIVERABLE 2 — THE CORPUS-WIDE COUNT

### 2.1 ⭐⭐⭐ **§5's STARRED BONUS, ANSWERED: THE FAMILY-C SURVIVORS ARE NOT A `gcc` PROPERTY — THEY ARE PREDOMINANTLY A `clang` PROPERTY**

`.temp/php49/baseline_split.py` re-derives F85's population independently
(negative **N1** pins it at exactly **366 comparisons / 38 flips / 29
cross-language** or refuses to report) and then takes the split item 111 never
took: **which C cell is the baseline of each cross-language flip?**

⚠ `.temp/php38/flip_columns.py` survives and its report is correct, **but its
own `N5` negative hardcodes F85's superseded `28` and therefore FAILS on correct
data** (the corrected figure is 29, `STATISTICS_001.md:88`). That is why this is
re-derived rather than imported, and it is a **fifth** stale hardcode in a
validator — same class as item 93. *(It is gitignored scratch, so it is not a
committed defect; but "flip_columns selftest PASS" cannot be quoted.)*

**A vs B, `O3`/`isolated`, F85's exact 7 rows:**

| magnitude floor on BOTH columns | cross-language flips | **`c-gcc` / `c-gcc-h` baseline** | **`c-clang` / `c-clang-h` baseline** |
|---|---:|---:|---:|
| 0.00 pp | 29 | **8** | ⭐ **21** |
| 1.00 pp | 17 | ⛔⛔ **0** | ⛔⛔ **17** |

▶ **21 of 29 — and, above a 1-pp magnitude floor on both columns, 17 of 17 —
of the flips that motivate item 62 have `c-clang` as their C baseline.**
The eight `c-gcc` flips all die at a 1-pp floor because their **B-column**
magnitudes are sub-1 pp (`ph03` −0.18…−0.82; `ph29` −0.78/−0.80). The
`c-clang` flips carry B-column magnitudes of **2.8–25.3 pp**.

Applying `_038` §1.1's family-C adjudication (`ph00` 0/1 refuted, the rest
survive): **of the 28 family-C survivors, 20 are `c-clang`-baseline and 8 are
`c-gcc`-baseline.**

⛔⛔⛔ **THIS REFUTES ITEM 111's TITLE DIRECTLY AND QUANTITATIVELY.** The
biggest open thread is not a `gcc` property. If anything it is a `clang`
property, by 21 to 8 — and by 17 to 0 above a floor.

**Extension to the two rows built since F85** (`ph52`, `ph53`; `.temp/php49/baseline_split.py`
population `P9`, negative N5 pins that it is strictly larger):

| population | comparisons | flips | cross-language | gcc | clang |
|---|---:|---:|---:|---:|---:|
| F85's 7 rows | 366 | 38 | 29 | 8 | 21 |
| **+ `ph52` + `ph53`** | **478** | **71** | **62** | **25** | **37** |

⚠ **F85's "38 flips / 29 cross-language" is now a figure about a 7-row corpus
that has 9 rows.** `ph52` alone contributes **32 cross-language flips** (16 gcc,
16 clang) with `|A|` 33–55 % against `|B|` 115–195 % — by a wide margin the
largest-magnitude flips in the corpus, consistent with its `inside_share` of
**22.29 % on `c-gcc`/`small.bin`**. On the enlarged population the split is
**near-symmetric (25 gcc / 37 clang)**, which refutes gcc-specificity a second
way.

ⓘ **`inside_share` footnote.** Item 111 quotes **22.24 %** for `ph52`'s C cells.
That figure has a named source — `patterns-php/ph52-concat-copy-uninit/NOTES.md`
§8a, a callgrind ratio. Computed instead as `A/B` from
`results-php/ph52-concat-copy-uninit.json` ÷ `results-php/gate/ph52-concat-copy-uninit.json`
the four C cells span **20.23 %–22.69 %** (`c-gcc`/`small` 22.29 %,
`c-clang`/`small` 20.23 %, `c-gcc`/`large` 22.63 %, `c-clang`/`large` 20.88 %).
**So `inside_share` is itself compiler-dependent**, and a single row-level
"22.24 %" is a fifth thing that needs its baseline named. The ruling it supports
survives either value.

### 2.2 ⛔ THE 24-CELL TABLE REPRODUCES; ITS SUMMARY TRIPLE MIXES TWO POPULATIONS

All **24** cells of item 111's clang-vs-gcc table reproduce **to the digit**
(`.temp/php49/sweep.py`; A1, `kernel_exclusive_ir`, `(c_clang − c_gcc)/c_gcc`).
Extended to `large.bin` — which exists only at `O3`/`isolated`:

| row | `O3`/iso small | `O0`/iso small | `O0`/whole small | ⭐ **`O3`/iso large (NEW)** |
|---|---:|---:|---:|---:|
| `ph03` | −15.2656 | −23.5320 | −23.5466 | **−14.8600** |
| `ph07` | −16.2707 | −18.9161 | −18.9161 | **−18.5675** |
| `ph16` | −1.8631 | +32.9076 | +31.5547 | ⭐ **+0.7360** |
| `ph29` | −27.8501 | −24.0756 | −24.1112 | **−28.0923** |
| `ph45` | −9.9141 | +7.9616 | −0.4495 | **−9.2066** |
| `ph52` | −15.5141 | −42.1053 | −42.1672 | **−14.0664** |
| `ph53` | −29.9572 | −20.3175 | −22.2678 | **−19.7720** |
| `ph64` | −2.3014 | +17.3877 | +17.3877 | **−2.3515** |

⭐ On `ph16` the `O3`/isolated figure **changes sign between inputs**
(−1.86 % small, +0.74 % large) — but **both are below a 1-pp floor**, so the
honest reading is *"no measurable compiler difference on `ph16` at `O3`"*, and
item 111's `−1.86` is being quoted as if it were a direction.

⛔ **Item 111's summary — *"8 rows · |min| 1.86 % · median 15.51 % · |max| 42.17 %"* — is
wrong on all three terms:**

| | item 111 | truth, 8-cell `O3`/iso column | truth, the tabulated 24 cells |
|---|---:|---:|---:|
| `\|min\|` | 1.86 % | 1.8631 % | ⛔ **0.4495 %** (`ph45`, `O0`/whole) |
| median `\|·\|` | 15.51 % | ⛔ **15.3898 %** | 19.6168 % |
| `\|max\|` | 42.17 % | ⛔ **29.9572 %** | 42.1672 % |

▶ **The triple mixes populations**: `|min|` and *median* are from the 8-cell
`O3`/isolated column, `|max|` from the full 24. **Neither population yields all
three.** And "median 15.51" is not a median of anything — it is the **5th of 8**
order statistics (`ph52`'s cell); the median of 8 is 15.3898.
⚠ **The consequence is not cosmetic**: the true `|min|` over the tabulated cells
is **0.45 %**, which is *below* any sensible floor. Publishing `|min| 1.86 %`
makes the smallest compiler gap look **4× larger** than it is and deletes the
one cell that shows **no compiler effect at all**.

### 2.3 THE THREE POPULATIONS

| | finding |
|---|---|
| **published** | ⛔ **TWO published claims change sign, and BOTH are in `.memory-php/`, the authoritative layer.** See below. |
| **publishable** | **10 of 128** A1 cross-language cell-pairs flip (§1.2) — 7.8 % overall, **15.6 % at `O3`/isolated**, **0 % at `O0`**. |
| **already labelled** | ✅ `.tasks-php/STATISTICS_001.md:92` (*"`ph29/large`, `c-gcc` vs `safe_naive`"*). ✅ `patterns-php/ph03-uudecode-bound/NOTES.md:692-697` (*"R4 − `c-gcc` = −2.88 `Ir`/group, R4 − `c-clang` = +5.00"*). ✅ `patterns-php/ph53-iface-tail-uninit/NOTES.md:684` (*"No bare C-vs-Rust number is published"*). |

**PUBLISHED CLAIM 1 — `ph29/large` +33.01 %.** Appears in `RECAP_PHP.md:82`
(the *which statistic* cell, **unlabelled**), `.memory-php/02-ladder.md` unit
453–634 (**unlabelled**) and `STATISTICS_001.md:92` (**labelled**).
**Flips: +33.01 % (`c-gcc`) → −4.36 % (`c-clang`).**

**PUBLISHED CLAIM 2 — ⭐⭐ `ph03`'s ROW-1 HEADLINE TABLE, AND THIS ONE IS NEW.**
`.memory-php/02-ladder.md:145-152` publishes

```
| safe_naive | safe_tuned | unsafe | verus | c-gcc-h |
|   +26.8 %  |   +3.7 %   | −7.6 % | −7.6 %|  −0.4 % |
```

with **no C baseline named anywhere in the table or its caption**. Re-derived in
A1, `O3`/`isolated`, *"rung dearer than the C baseline by"*
(`results-php/ph03-uudecode-bound.json`):

| input | baseline | `safe_naive` | `safe_tuned` | `unsafe` | `verus` |
|---|---|---:|---:|---:|---:|
| `small.bin` | `c-gcc` | +27.06 % | +3.78 % | ⛔ **−7.49 %** | ⛔ **−7.49 %** |
| `small.bin` | **`c-clang`** | +49.95 % | +22.48 % | ⛔ **+9.17 %** | ⛔ **+9.17 %** |
| `large.bin` | `c-gcc` | +29.71 % | +5.78 % | ⛔ **−5.70 %** | ⛔ **−5.70 %** |
| `large.bin` | **`c-clang`** | +52.35 % | +24.25 % | ⛔ **+10.76 %** | ⛔ **+10.76 %** |

▶ ⛔⛔ **TWO OF THE FOUR RUST CELLS IN `ph03`'S PUBLISHED ROW-1 TABLE CHANGE
SIGN UNDER `c-gcc` → `c-clang`, ON BOTH INPUTS, AT 5.7–10.8 pp.** The published
reading *"unsafe and verus Rust are ~7.6 % **cheaper** than C"* becomes
*"~9.2 % **dearer** than C"*.

⭐⭐⭐ **AND `ph03`'s OWN `NOTES.md` ALREADY SAID SO**, at `:692-697`:

> *"**Unsafe Rust beats gcc C on this kernel and loses to clang C**, and the
> clang column is why that must be stated as two numbers."*

▶ **The row got it right and the memory layer dropped the clang column.** This
is the PAT-side `SYNTHESIS.md`-beats-`RECAP_PAT.md` pattern one level deeper —
here the **row** beats the **authoritative layer**.

⚠ **UNTESTED**: `ph07`'s published **A3** figure, `ph45`'s published **A1 + W1**
pair, and `ph64`'s published **B1** headline were not re-derived under both
baselines. `ph64`'s B1 is `fixed-R4 bound` (R3-vs-R4) and is **same-language**,
so it cannot be affected; the other two are cross-language and **could be**.
This is where §2's published census ran out.

---

## §3 DELIVERABLE 3 — THE ATTRIBUTION CONFOUND

### 3.1 ⛔ LEG 1 IS WRONG TWICE, AND ITS PREMISE IS BACKWARDS

`.temp/php49/o0_leg.py`. ⚠ **`large.bin` has no `O0` `Ir` anywhere in
`results-php/`** (negative N1 asserts it), so this leg is **`small.bin`-only by
construction** and "both inputs" is not askable.

**(a) *"six of eight"* is FIVE of eight.** `|iso − whole|` on the clang-vs-gcc
ratio at `O0`/`small.bin`:

| row | `O0`/iso | `O0`/whole | Δ pp | ≤ 0.1 pp? |
|---|---:|---:|---:|---|
| `ph03` | −23.5320 | −23.5466 | 0.0146 | ✅ |
| `ph07` | −18.9161 | −18.9161 | 0.0000 | ✅ |
| `ph16` | +32.9076 | +31.5547 | **1.3529** | ⛔ |
| `ph29` | −24.0756 | −24.1112 | 0.0355 | ✅ |
| `ph45` | +7.9616 | −0.4495 | **8.4111** | ⛔ |
| `ph52` | −42.1053 | −42.1672 | 0.0619 | ✅ |
| `ph53` | −20.3175 | −22.2678 | **1.9503** | ⛔ |
| `ph64` | +17.3877 | +17.3877 | 0.0000 | ✅ |

▶ **5 of 8, not 6.**

**(b) ⭐⭐⭐ THE PREMISE — *"an `O0` gap is not a symbol-boundary artefact"* — IS
FALSE, AND IT IS FALSE ONLY FOR `c-clang`.** Item 111 asks whether the *ratio*
moves; the question that tests the premise is whether **each cell's own
`kernel_exclusive_ir`** moves between `isolated` and `whole` at `O0`. It does:

| row | cell | `O0`/iso | `O0`/whole | whole−iso |
|---|---|---:|---:|---:|
| `ph03` | `c-clang` | 131,188,820 | 131,163,820 | −0.0191 % |
| `ph16` | `c-clang` | 15,832,107 | 15,670,949 | **−1.0179 %** |
| `ph29` | `c-clang` | 53,428,151 | 53,403,151 | −0.0468 % |
| `ph45` | `c-clang` | 21,255,780 | 19,599,780 | ⛔ **−7.7908 %** |
| `ph52` | `c-clang` | 23,375,000 | 23,350,000 | −0.1070 % |
| `ph53` | `c-clang` | 30,788,815 | 30,035,221 | **−2.4476 %** |

⛔⛔ **SIX CELLS MOVE. ALL SIX ARE `c-clang`. NOT ONE `c-gcc`, `safe_naive`,
`safe_tuned`, `unsafe` OR `verus` CELL MOVES BY A SINGLE INSTRUCTION.**
clang inlines at `-O0`; gcc does not. **So the exact mechanism item 111 says
cannot be present at `O0` is present at `O0`, on six of eight rows, in the one
compiler item 111 proposes switching to.** Above a 1-pp floor it is
**3 of 8 rows** (`ph16`, `ph45`, `ph53`).

**(c) `ph45`'s sign disagreement, explained.** `ph45`, `O0`, `small.bin`,
`n_iters = 1500`: `c-gcc` is **19,688,280 in both modes — identical to the
instruction**, while `c-clang` moves **−1,656,000 `Ir` = −1104 `Ir`/call**.
That single artefact produces the whole disagreement: iso
`(21,255,780−19,688,280)/19,688,280 = +7.96 %`, whole
`(19,599,780−19,688,280)/19,688,280 = −0.45 %`. ▶ **`ph45`'s `O0` "compiler gap"
is a compilation-mode artefact, not a compiler gap** — and at −0.45 % the whole
figure is below a 1-pp floor, i.e. **no measurable difference.**

⚠ **What this does NOT explain**: `ph16`'s and `ph64`'s `O0`-vs-`O3` sign
reversals (+32.91 → −1.86 and +17.39 → −2.30). Those are **opt-level** effects,
not mode effects — `ph64`'s cells do not move between modes at all.

⛔ **And a rule from the PAT authoritative layer that item 111's leg 1 violates
outright** — `.memory/02-bench-rules.md`, "Honesty rules": ***"Never report a
perf number from an `O0` row."*** **Two of the three columns in item 111's
corpus-wide table are `O0`.**

### 3.2 ✅ LEG 2 IS UPHELD, AND THE COLD-HELPER ALTERNATIVE IS REFUTED — BY BETTER EVIDENCE THAN THE MANAGER'S

The task asks whether clang could be inlining a **cold** helper (adding static
code that rarely runs) while keeping a **hot** one as a call (removing dynamic
work from the symbol). That would restore the confound.

**It is refuted for `ph29` without any new run, and the static-size argument is
not needed at all.** From `.temp/php49/likeforlike.py`, the **same** gcc→clang
gap measured at three nested scopes:

| `ph29`, `O3`/iso | `c-gcc` | `c-clang` | **clang vs gcc** |
|---|---:|---:|---:|
| **A1** (kernel exclusive), large | 120,800,132 | 86,864,573 | **−28.09 %** |
| **C** (kernel call tree), large | 125,896,779 | 91,895,259 | **−27.01 %** |
| **W1** (PROGRAM TOTALS), large | 127,161,820 | 93,156,627 | **−26.74 %** |
| **A1**, small | 39,273,585 | 28,335,859 | **−27.85 %** |
| **C**, small | 43,420,533 | 32,346,232 | **−25.50 %** |
| **W1**, small | 43,965,633 | 32,887,659 | **−25.20 %** |

▶ ⭐⭐ **THE COMPILER GAP SURVIVES BOTH WIDENINGS OF SCOPE, LOSING ONLY
1.1–2.7 pp.** If clang had merely **relocated** hot work out of the `kernel`
symbol, **C** would not see the gap — C is the whole call tree. If it had
relocated work out of the call tree entirely, **W1** would not see it — W1 is
the whole program and is immune to every symbol-boundary effect by construction.
**Both see it.** ⛔ **The cold-helper alternative is refuted on `ph29`: clang
really does execute ~27 % less total work than gcc on this kernel.**

ⓘ Supporting, and consistent: `results-php/ph29-recvfrom-alloc.json`'s own
`static` block at `O3`/`isolated`, symbol `kernel` — `c-gcc` `n_nopad` **338** /
1388 B with **25** backward branches; `c-clang` **476** / 2176 B with **35**.
**Both** carry `bulk_calls ['memcpy@plt']` and **both** carry `vector_regs
['xmm']`, so the difference is not "one vectorises and the other does not"; the
+10 backward branches on 41 % more static code is an unrolling/peeling
signature. ⚠ **This is corroboration, not proof** — the static block cannot
distinguish hot from cold code. The C/W1 measurement above is the proof.

⚠ **W1 figures quoted to 2 dp** per item 99 (W1 moves ±14–28 `Ir` across
regenerations — on 127 M that is ≤ 2.2 × 10⁻⁵ %, immaterial here).

### 3.3 ⭐ WHERE IT NEEDS FAMILY C — AND THE RE-SCOPING ITEM 111 ASKS FOR

**Settled without family C:** `ph29`. Family C already existed for its six
cells.

⛔ **NOT settled, and it needs family C:** the other **seven** rows.
`.temp/mgr172/cg/` holds only `unsafe` and `verus` profiles for `ph00`, `ph03`,
`ph07`, `ph16`, `ph64` — **no C-cell profiles at all** — and **nothing** for
`ph45`, `ph52`, `ph53`. So the corpus-wide clang-vs-gcc gap in §2.2 is **A1-only
on 7 of 8 rows**, and whether it survives family C there is **UNTESTED**.
⛔ **I did not build them, per the task's prohibition.**

▶ **THE RE-SCOPING, WHICH IS THE VALUABLE PART:** item 62's question is no
longer only *"is A the wrong column?"*. §2.1 shows the flips it exists to
adjudicate are **21-to-8 a `c-clang` phenomenon**, and §3.2 shows the compiler
gap itself is **real work, not attribution**, on the one row where it can be
checked. ▶ **Family C, when built, must be built for BOTH C cells on every row,
not just for whichever C cell a row happens to publish** — otherwise it will
re-adjudicate 8 flips and leave the other 20 untouched. That is a **new
requirement on item 62** and it is the concrete output of this deliverable.

⛔ **NOTHING HERE LICENSES DROPPING FAMILY C OR ITEM 62.** §1.3 strengthens
item 62: A1 disagrees with C by 15.6–34.1 pp under **both** baselines.

---

## §4 DELIVERABLE 4 — LABELLING: CENSUS, RULING, CHECK

### 4.1 ⭐⭐⭐ (a) THE CENSUS — AND ITEM 111 LOOKED IN THE WRONG PLACE

Item 111 says *"the ARGUMENT DOCUMENT is more careful than the SUMMARY CELL"*,
contrasting `STATISTICS_001.md:92` (labelled) with `RECAP_PHP.md:82` (not).
**That diagnosis is incomplete, and the omission is the consequential one:**

⛔⛔ **`.memory-php/02-ladder.md` — THE AUTHORITATIVE LAYER, WHICH OUTRANKS BOTH
— CARRIES THE UNLABELLED CENTRAL CLAIM.** One blockquote unit spans lines
**453–634** (182 lines) and contains:

> *"A says C is **+33 %** dearer than naive safe Rust; **B, C and W1 all say
> ~1 % CHEAPER**, agreeing to ~2 pp. That is the difference between *"safe Rust
> is a third cheaper than C here"* and *"they are the same"* — **this
> programme's central claim.**"*

**The strings `c-gcc` and `c-clang` appear nowhere in those 182 lines.**
That same unit says, of itself, *"THIS is the layer that outranks
`RECAP_PHP.md`"*.

▶ And by §1.3 the sentence is doubly wrong: the "~1 % CHEAPER" is `c-gcc`-only,
and the like-for-like `c-clang` figures are **−27.78 % / −27.61 %**.

**Plus PUBLISHED CLAIM 2** (§2.3): `.memory-php/02-ladder.md:145-152`, `ph03`'s
row-1 headline table — **five percentages, no baseline named, two of four Rust
cells change sign** — with the very next bullet warning that *"`c-clang` beats
`c-gcc` by 15.4 % (larger than every safety effect on the row)"*.
⭐ **The file warns about the effect and then publishes the table the effect
reverses.**

**Machine census** (`.tasks-php/cbaseline_check.py`): **59 hits across 25 files**
— magnitude + cross-language token + no `c-gcc`/`c-clang` in the same unit.

| file | hits |
|---|---:|
| `RECAP_PHP.md` | 30 |
| `patterns-php/ph52-concat-copy-uninit/NOTES.md` | 7 |
| `.memory-php/02-ladder.md` | **5** |
| `.tasks-php/STATISTICS_001.md` | 3 |
| `.memory-php/03-numbers.md` | **2** |
| `ph03`, `ph16`, `ph53` `NOTES.md` | 2 each |
| `ph29` `NOTES.md`/`README.md`, `ph45` ×2, `ph52` `README.md`, `ph64` `NOTES.md` | 1 each |

⛔⛔ **59 IS A TRIPWIRE, NOT A DEFECT COUNT. HAND-ADJUDICATED SAMPLE OF 10 →
5 TRUE / 5 FALSE**, recorded inside the checker beside the `RATCHET`. The
dominant false-positive class is **structural and cannot be regexed away: in
this corpus `C` names BOTH the language AND family C, the call-tree statistic.**
The second class is **unit size** — `.memory-php/02-ladder.md`'s blockquotes run
180 lines, so one stray `C` marries every magnitude in the block.
⭐ Following `contract_audit.py`: **adjudicated by hand, regex not tuned.**

### 4.2 (b) RULING — *"QUOTE A RUNG AGAINST A RUNG"* IS **NOT** SUFFICIENT, AND THE SUFFICIENT RULE ALREADY EXISTS

⛔ **Insufficient as written.** *"Quote a rung against a rung, never against
'C'"* constrains the **Rust** side — which was never the ambiguous one. It is
satisfied by *"`c-gcc` vs `safe_naive`"* **and** by *"C vs `safe_naive`"*, since
"C" reads as a rung name. It does not require naming the compiler.

⭐⭐⭐ **AND THE SUFFICIENT RULE ALREADY EXISTS, IN THE PAT AUTHORITATIVE
LAYER, SINCE `TASK_001`.** It is not in `.memory-php/`:

> `.memory/02-bench-rules.md`, **"Honesty rules"**:
> - *"Never report a perf number from an `O0` row."*
> - *"**Never report a C-vs-Rust number without saying which C compiler, and
>   whether a same-backend (clang) column exists.**"*

> `.memory/01-ladder.md:2572`:
> *"**Always report a clang column.** A gcc-only C baseline overstates C's
> dynamic cost here by **43 %** — gcc emits *fewer* instructions and executes
> **42.9 % more**."*

> `.memory/01-ladder.md:2534`: clang *"is the same-backend baseline and is
> **mandatory for any C-vs-Rust claim**; gcc is the 'what a distro ships'
> baseline."*

⭐ **The PAT pilot measured +42.9 % — the same direction and the same order of
magnitude as this corpus's −14 % to −42 %.** So item 111's *"the gap is
corpus-wide"* is a **rediscovery**, not a discovery, and `ph03`'s NOTES cites
the PAT rule by name at `:697`. **The gap is that `.memory-php/` never inherited
it** — `grep -a clang .memory-php/*.md` returns **one line**, and it is a
`ph03` observation, not a rule.

▶ **RULING — a cross-language figure must carry FOUR things** (three already
required by `.memory-php/03-numbers.md`, the fourth is what this task adds):
**the statistic** · **the input** · **the opt/mode level** · **the base it is
against, and if that base is a C cell, WHICH COMPILER.**
▶ **And, from `.memory/01-ladder.md`: BOTH C columns, or an explicit statement
that only one was measured.** §2.3 is why: one column is not a number with error
bars on it, it is **a different sign**.
⚠ ***"Quote a rung against a rung"* should be RETIRED in favour of the PAT
wording**, not kept beside it — two rules of different strength on one question
is how the weaker one gets cited.

### 4.3 (c) THE CHECK — `.tasks-php/cbaseline_check.py`

Lands in `.tasks-php/`, **in no digest, free** (`STATISTICS_001.md` §6's
measured table). **Nine must-fire negatives INSIDE the file** per
`PROTOCOL_PHP.md` §H:

| | asserts |
|---|---|
| **N1** | the real defect sentence from `.memory-php/02-ladder.md` **scores as a hit** |
| **N2** | the real labelled sentence from `STATISTICS_001.md:92` **does not** |
| **N3** | a magnitude is required (C prose with no number does not fire) |
| **N4** | a cross-language token is required (a Rust-vs-Rust figure does not fire) |
| **N5** | the `C` token does **not** match `CWE-125`, `uuencode.c:66`, `CVE`, `C99` |
| **N6** | `BASE` recognises all four spellings `c-gcc` `c-clang` `c-gcc-h` `c-clang-h` |
| **N7** | the ratchet comparison is live, not inert |
| **N8** | the scan list is non-empty and every entry exists (a mistyped glob cannot report "0 hits" as clean) |
| **N9** | ⭐ the count is **non-zero** on a corpus known to carry the defect |

`--selftest` **PASS (0 failures)**. `RATCHET = 59`, set at the measured count,
with the 10-item hand adjudication written beside it. `--ratchet` exits 1 if the
count grows.

---

## §5 ⭐ WHAT I AM UNSURE OF

1. **`ph07`'s published A3 and `ph45`'s published A1+W1 cross-language figures
   were NOT re-derived under both baselines.** The published census in §2.3 has
   **two verified entries and three untested ones**. This is where §2's depth
   ran out.
2. **The `c-*-h` (hardened) cells were excluded from the 128-pair sweep.**
   Including them roughly doubles the population and could move the 7.8 % rate.
   §2.1's split **does** include them (F85's population does).
3. **Family C exists on `ph29` only.** §3.2's verdict is **one row**. `ph52`,
   with `inside_share` 20–23 % on its C cells, is the row most likely to behave
   differently and has **no** C profile.
4. **`_038` §1.1's "28 of 29 survive family C" was not re-verified by me.** I
   inherited it to map §2.1's split onto the survivors. If that adjudication is
   itself gcc/clang-confounded, my 20-of-28 figure inherits the confound.
5. **The 59-hit census has a measured 5/10 false-positive rate on a 10-item
   sample.** The other 49 hits are **UNADJUDICATED**. The true defect count is
   somewhere between 5 and 59 and I did not narrow it further.
6. ⚠ **`ph03`'s `.memory-php/` table figures (+26.8/+3.7/−7.6/−7.6) do not
   match my A1 re-derivation exactly** (+27.06/+3.78/−7.49/−7.49). They are
   probably the `Ir`/group statistic `ph03` NOTES §8 uses, with ~150 `Ir` of
   fixed `php_shim_reset` cost subtracted. **The sign conclusion is robust to
   this** (the flip is 7.5 → 9.2 pp) but the exact figures are not mine.
7. **Whether `c-clang`'s `O0` inlining (§3.1b) affects the `O3` numbers is
   untested.** I measured mode-dependence at `O0` only, because `O3`/`whole` has
   no A1 at all.
8. **The `ph16` `O3` input-dependent sign change (−1.86 small / +0.74 large)** is
   below a 1-pp floor on both sides and I treated it as a null. If a smaller
   floor is defensible on this corpus, it is an 11th sign flip.
9. **`.temp/mgr172/cg/`'s profiles are gitignored.** My §1.3 and §3.2 results
   depend on blobs that a fresh clone does not have. The regenerator
   (`sweep_cg.sh`) exists but does **not** cover `ph29`'s four non-`unsafe`/`verus`
   cells — **so those six profiles have no committed regeneration path**, which is
   open item 65's shape again. I did not repair it (it is a `.temp/mgr172/` file,
   not mine).
10. **`.temp/php38/flip_columns.py`'s `N5` failure** — I diagnosed it as a stale
    hardcode of F85's superseded 28. I did **not** verify that no other negative
    in that file is also stale.
11. **I did not check `.web/`** (a concurrent session owns it). If it renders
    any of these unlabelled figures, the census is incomplete by that much.
12. **Whether `ph52`'s 32 new cross-language flips are genuine or an artefact of
    its three-TU `PH52_NOINLINE` boundary** is untested; their `|B|` of 115–195 %
    is far outside anything else in the corpus and deserves its own look.
13. **The claim that clang inlines at `-O0` and gcc does not** is my inference
    from the `Ir` movement pattern, not from reading assembly. I did not run
    `harness/asm.py` — §3.2's C/W1 measurement made it unnecessary for the
    verdict, but the *mechanism* statement in §3.1b is one step short of proven.
14. **I did not test whether the `O3`/`whole` `main_exclusive_ir` column** (which
    exists on every cell and contains the inlined kernel) would serve as a cheap
    proxy for family C. ⭐ **If it would, item 62 may be much cheaper than
    priced.** That is the single most promising unexplored lead I found.

---

## §6 SCOPE COMPLIANCE

✅ No edits under `harness/` `common/` `common-php/` `patterns/` `patterns-php/`
`results/` `results-php/` `pilot/`. ✅ `RECAP_PHP.md` and `.memory-php/` read
only. ✅ No family C built, no callgrind run, no build. ✅ No `git add`/`commit`.
✅ `.web/` untouched. ✅ New checker in `.tasks-php/` with negatives inside.
✅ Scratch in `.temp/php49/` only; generators kept, `__pycache__` deleted.
✅ `grep -a` throughout. ✅ `timeout` on every long command.
✅ Brackets **66/0** and **18/0**, first and last, unmoved.
