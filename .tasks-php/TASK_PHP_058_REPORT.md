# `TASK_PHP_058_REPORT.md` — `inside_share` measured on `ph03`, `ph16`, `ph29`, and the template fixed in `ph97`

> **ENGINEER report.** Item 127, `TASK_PHP_057`'s BINDING resume priority. Four
> rows re-gated `check.py: PASS`. Every number below was produced by a command
> in this report and every command was run.

---

## §0 THE HEADLINE, BEFORE THE DETAIL

⭐⭐⭐ **THE DOCSTRING'S FOUR NUMBERS ARE NOT THE STATISTIC THE TEMPLATE
COMPUTES.** `ph29`'s `0.655 / 0.669 / 0.927 / 0.655` reproduce **exactly**, in
**exactly one cell set** — `large.bin` / `O3` / `isolated`, C = `c-gcc` — under
`F74`'s definition `(kernel_exclusive_ir / n_iters) / marginal_ir_per_call`.
⛔ **They reproduce in NO cell under the definition `ph97`'s template uses**
(`A1 / callgrind summary total`). **Two different quantities are called
`inside_share` in this programme and no document said so**; on `ph29`'s
`c-gcc`/`small.bin` cell they read `0.8045` and `0.8933`, and the F74 one
exceeds `1.0` on **15 cells** of the corpus, which no share can do.

⭐⭐⭐ **AND THE `+33 %` HAS A THIRD MOVER NOBODY NAMED: THE COMPILER FLIPS ITS
SIGN.** On `ph29`/`large.bin`/`O3/isolated`, A1 against `safe_naive` reads
**`+33.01 %` on `c-gcc`** and **`−4.36 %` on `c-clang`**. The statistic moves it
too (`W1`: `−0.80 %`), and so does the input (`small.bin`: `+39.92 %`).

---

## §1 WHAT I BUILT

| path | what |
|---|---|
| `patterns-php/ph03-uudecode-bound/controls/inside_share.py` | the control, **byte-identical in all four rows** |
| `patterns-php/ph16-fdset-index/controls/inside_share.py` | ditto |
| `patterns-php/ph29-recvfrom-alloc/controls/inside_share.py` | ditto |
| `patterns-php/ph97-optarg-unwritten/controls/inside_share.py` | ditto — the template, rewritten |
| the four matching `inside_share.json` sidecars | each `FRESH`, each `problems: []`, each with `summary` |
| `patterns-php/ph03-uudecode-bound/controls/_pin.py` | new, from `ph97`'s |
| `patterns-php/ph16-fdset-index/controls/_pin.py` | new |
| `patterns-php/ph29-recvfrom-alloc/controls/_pin.py` | new |
| `.tasks-php/php58_record_share.py` | `F74`'s share for every built row, from the committed records; `--pairs` applies `F74`'s rule; `--find` locates a value; `--selftest` 7/7 |
| `.tasks-php/php58_mutate_arms.py` | **the §H attack**: mutates the shipped control's decisions and checks the arms notice |
| `NOTES.md` sections | `ph03` §14, `ph16` §13, `ph29` §15, `ph97` §8.6 extended |
| `README.md` control listings | all four rows, which omitted the new control (and, on `ph97`, `optional_cost.py` as well) |

```
$ sha256sum <the four controls>   # one hash, four rows
14033d12416a59c4419df877422ec15ced07f9834227fd5eb739c2051e37aa8b  (x4)
```

**Nothing is hardcoded that can be derived.** `n_iters` comes from each input's
own header via `common-php/slb.py`; the build-root tag is derived the way
`harness/build.py::pattern_id` derives it; the row name is the directory. The
file names no row, so the four copies are one file and a reader can prove it
with `sha256sum` instead of a diff.

### 1.1 The must-fire negatives are INSIDE the control, and the gate reads their score

`PROTOCOL_PHP.md` §H. Seven arms run on **every** invocation (not only under
`--selftest`), four of them must-fire; the count lands in the sidecar's
`summary` block, which `harness/check.py::control_json_verdict` **FAILS** when
`as_expected != n`.

```
$ python3 patterns-php/ph29-recvfrom-alloc/controls/inside_share.py --selftest
  ok  1 must-NOT-fire: a C `kernel` row is counted: got 39273585
  ok  2 must-NOT-fire: a Rust `crate::kernel` row is counted: got 39273585
  ok  3 MUST-FIRE: `kernel_hardened` is NOT a `kernel` row: got None
  ok  4 MUST-FIRE: a listing with no `kernel` row reads None: got None
  ok  5 MUST-FIRE: an empty build root reports every cell missing: got [8 cells]
  ok  6 must-NOT-fire: this row's own pin is clean: got []
  ok  7 MUST-FIRE: a pin written in the non-shim view is caught: got 2
  7 of 7 arms as expected
```

⚠ **A self-reported `ok` is worth nothing until something breaks the decision it
reports on.** `.tasks-php/php58_mutate_arms.py` loads the **shipped** module,
mutates one decision at a time and re-runs the arms:

```
$ python3 .tasks-php/php58_mutate_arms.py
  CAUGHT         loose `kernel` regex -- `kernel_hardened` would be counted
  CAUGHT         kernel row parser always returns 0 instead of None
  CAUGHT         missing-binary check always says nothing is missing
  CAUGHT         pin check always says the pin is clean
  CAUGHT         pin asked for a path this row does not have
  not caught     NO MUTATION (must-NOT-fire)
  all 6 cases behaved as expected (5 must-fire, 1 must-NOT-fire)
```

⭐ **Arm 6 is the pin guard §2.2 asked for, and it fires on the exact failure
the task file warns about.** `_pin.py` carries a hand-copied `ROW` literal;
stage 9b only **SHOUTS** when a pin's paths are absent, so a mis-aimed pin is
*"the quietest possible way to have no pin at all"*. The control asks stage 9b's
question locally, where it is a **FAILURE**, and asks a second one the stage
cannot: `_pin.derived_from` silently **omits** a path that does not exist, so a
typo in the pinned list shrinks the pin instead of breaking it.

⚠ **The probe `.tasks-php/php58_record_share.py` caught a real defect in itself
on its first run** (arm 6 read the wrong tuple field). That is the argument for
§H in one line: the arms found the author's bug before the author did.

---

## §2 §2.3's FOUR QUESTIONS, WITH NUMBERS

### (a) Do the docstring's four numbers reproduce? **YES — but not in my matrix.**

They are **fractions**: `0.655 / 0.669 / 0.927 / 0.655` = **65.5 % / 66.9 % /
92.7 % / 65.5 %**. Multiply by 100 to meet the control's percent column.

⛔⛔ **AND THEY DO NOT REPRODUCE THERE.** Under the template's definition the
row's `large.bin` column reads `66.90 %` (`safe_tuned`), `68.35 %` (`unsafe`),
`95.00 %` (`c-gcc`) — and `65.5 %` and `92.7 %` appear **nowhere** in the
matrix, on either input. ⚠⚠ **`66.90 %` DOES appear — as `safe_tuned`, where
the docstring's `0.669` is `unsafe`.** A reader checking one number against the
wrong definition would have confirmed it and mislabelled the cell.

**They reproduce under `F74`'s definition, exactly:**

| docstring | rung | measured |
|---|---|---|
| `0.655` | `safe_tuned` (R3) | **0.655124** |
| `0.669` | `unsafe` (R4) — and `verus`, byte-identical | **0.668981** |
| `0.927` | `c-gcc` (R1) | **0.926592** |
| `0.655` | `safe_tuned` again | **0.655124** |

### (b) WHICH CELL? **`large.bin` / `O3` / `isolated`, uniquely.**

Searched over **every computable cell of every built row** — up to 32 per row
(`O0/isolated`, `O0/whole`, `O3/isolated` × two inputs × eight cells; `O3/whole`
is not computable, see below):

```
$ python3 .tasks-php/php58_record_share.py --find 0.655 0.669 0.927
  0.655: 1 hit   ph29 safe_tuned O3/isolated large.bin  0.655124
  0.669: 2 hits  ph29 unsafe / verus O3/isolated large.bin  0.668981
  0.927: 3 hits  ph29 c-gcc 0.926592 · ph29 c-gcc-h 0.926625 · ph97 safe_tuned 0.926942
```

`0.655` has **one** hit in the entire corpus and it is this row's
`safe_tuned`/`large`. On `small.bin` the same four rungs read `0.6268 / 0.6371 /
0.8045 / 0.6268` — nothing matches. ▶ **So the cell is recoverable, and only
because `0.655` happens to be unique.** The residual ambiguities inside the
cell: `0.669` is `unsafe` **or** `verus` (harmless — `identity` pins them
byte-identical) and `0.927` is `c-gcc` **or** `c-gcc-h` (**not** harmless — R1
and R1h are different programs; they agree here to 4 dp).

⚠ **So the disclaimer was missing FIVE things, not three**: the input, the
`-O` level, the mode, the compiler — **and the definition**, which no version of
F108's list contains because nobody had noticed there were two.

### (c) WHICH C? **`c-gcc`. `c-clang` is `0.9122` on the same cell.**

| `large.bin` `O3/isolated` | F74 share | template share |
|---|---:|---:|
| `c-gcc` | **0.9266** | 95.00 % |
| `c-clang` | **0.9122** | 93.25 % |
| `c-gcc-h` | 0.9266 | 95.00 % |
| `c-clang-h` | 0.9121 | 93.24 % |

The docstring's `0.927` is **`c-gcc`'s alone**: a one-compiler claim standing in
for both, exactly as F108 forbids. ✅ **Its CONCLUSION survives the swap** —
`Δshare` against `safe_tuned` is `0.2715` (gcc) and `0.2570` (clang), both more
than **12×** the written `0.02` bar — **but the number in it does not.**

### (d) THE VERDICT ON THE `+33 %`

**The comparison does NOT meet the bar the docstring sets, and the docstring is
right.** There IS a written bar (see P5) — `F74`'s corrected rule, in
`RECAP_PHP.md` F74 and in `.memory-php/02-ladder.md`: *(i) `min(inside_share)`
must be HIGH, threshold not tuned; (ii) `|Δinside_share| ≤ 0.02`.* On this row,
at `O3/isolated`:

| pair | `small.bin` | `large.bin` | rule (ii) |
|---|---:|---:|---|
| `safe_tuned` vs `unsafe` — the `fixed-R4 bound` | 0.0103 | 0.0139 | **PASS** |
| `c-gcc` vs `safe_tuned` — the docstring's C-vs-Rust pair | 0.1777 | **0.2715** | **FAIL** |
| `c-gcc` vs `safe_naive` — the PUBLISHED `+33 %` pair | 0.1269 | **0.2355** | **FAIL** |
| `c-clang` vs `safe_naive` | 0.1021 | 0.2211 | **FAIL** |

▶ **The docstring's disclaimer is UPHELD and must NOT be narrowed.** The pair it
defends passes (ii) with room; the pair it refuses fails by **more than an order
of magnitude**, on both C columns and both inputs.

⚠ **And the `+33 %` is NOT thereby FALSE.** A1 really does say it — `+33.01 %`,
reproduced to the digit. What the number may not be is a **claim about C against
Rust**. The four readings of that one comparison:

| `C` vs `safe_naive`, `large.bin`, `O3/isolated` | `c-gcc` | `c-clang` |
|---|---:|---:|
| **A1** (`kernel_exclusive_ir` per call) | **+33.01 %** | **−4.36 %** |
| **W1** (`marginal_ir_per_call`) | −0.80 % | −27.54 % |
| whole-program total `Ir`, one run | −1.19 % | −27.61 % |
| `Δ` F74-share | 0.2355 | 0.2211 |

⭐⭐ **In the role `RECAP_PHP.md`'s cell actually uses it — evidence that A1
disagrees with three other statistics — the figure is sound and now better
supported than before**, because the `Δshare` of `0.2355` is the measured reason
it disagrees. **Bare, it is a C-vs-Rust headline this row disclaims.** The label
it needs is six items: *A1 · `c-gcc` · `large.bin` · `O3/isolated` · against
`safe_naive` · `Δinside_share` 0.2355, which the programme's own rule says the
statistic cannot resolve* — **and a seventh: `c-clang` reads `−4.36 %`.**

⚠⚠ **ONE PRECISION THE THREAD HAS BEEN MISSING: THE DOCSTRING AND THE HEADLINE
ARE NOT ABOUT THE SAME PAIR.** The docstring's `0.927 vs 0.655` is C vs
**`safe_tuned`** (R3); the published `+33 %` is C vs **`safe_naive`** (R2). Both
fail (ii), so the disclaimer covers the headline in substance — but F127's
sentence *"the exact comparison the row's own control disclaims"* is **one rung
off**, and nobody had checked.

### §2.4's requirement, and §2.5's

The control prints F109's warning on every run and every `NOTES.md` section
carries it. ✅ **§2.5 is now MEASURED rather than asserted**: at `O3`/`whole`
all four rows' measurement records carry `kernel_exclusive_ir: null` for all
eight cells on both inputs — 16 null entries per row — so the ratio is
**undefined**, not 100 %.

---

## §3 P1–P5, WITH THE EVIDENCE

| | verdict | evidence |
|---|---|---|
| **P1** — the four reproduce in at least one cell, and it is `small.bin`/`O3`/`isolated` | ⚠ **SPLIT: conclusion UPHELD, cell REFUTED** | they reproduce in exactly one cell set and it is **`large.bin`**. On `small.bin` the four rungs read `0.6268 / 0.6371 / 0.8045 / 0.6268` — no match. The stated reason (*"A1 on this row is defined on `small.bin` by the same docstring"*) is true of A1 and false of the shares beside it |
| **P2** — no cell reproduces all four, because the C figure names no compiler and the two C columns differ | ⚠ **SPLIT: conclusion REFUTED, reason UPHELD** | one cell reproduces all four. And `c-gcc` `0.9266` vs `c-clang` `0.9122` **do** differ, and the docstring's figure **is** gcc's alone — the reason was right and did not entail the conclusion, because 0.927 is nearer 0.9266 than the gap between the columns |
| **P3** — `ph03` and `ph16` read high (> 90 %) on every cell | ✅ **UPHELD at `O3/isolated`; REFUTED if read over all cells** | `ph03` template-share `90.13 – 99.18 %`, F74-share `0.9031 – 0.9929`; `ph16` template-share `99.20 – 99.66 %`, F74-share `0.9501 – 1.0279`. ⛔ **At `O0` they collapse**: `ph16`'s `c-gcc`/`O0` F74-share is **0.0418**. Every published figure is `O3`, so the prediction is right where it matters and the `O0` half is worth knowing |
| **P4** — the `+33 %` is under-qualified rather than false; the fix is a label | ✅ **UPHELD-NARROWED** | A1 does say `+33.01 %`, so it is not false; item 127's ruling stands. ⚠ **The label is bigger than predicted**: it must carry the **other C column, whose sign is opposite**. *"A label, not a retraction"* is true only if the label includes `−4.36 %` |
| **P5** — the *"comparable callee share"* bar has no written definition anywhere in this repo | ⛔ **REFUTED, and half-narrowed** | It has one, in two places, and (ii) is a number: `RECAP_PHP.md` F74 and `.memory-php/02-ladder.md` — *(i) `min(inside_share)` HIGH **and** (ii) `|Δinside_share| ≤ 0.02`*, *"conjunction measured clean at 151 of 366 comparisons with ZERO flips"*. ⚠ **(i) HAS no threshold and says so** (*"`>0.3`, `>0.5` and `>0.6` all give 0 flips … six rows cannot pin it"*), so §2.3(d)'s third outcome is live for **half** the bar. ▶ **I did not invent one**: `.tasks-php/php58_record_share.py --pairs` prints (ii) only, and says in its docstring why it prints no verdict for (i) |

⭐ **Three of five predictions split, one is refuted, one is upheld-narrowed.
Zero survived as written.** That is the eighth consecutive round.

---

## §4 THE FOUR RE-GATES

```
$ python3 harness-php/gate.py ph03-uudecode-bound     # 2m28.9s
check.py: PASS
$ python3 harness-php/gate.py ph16-fdset-index        # 2m37.4s
check.py: PASS
$ python3 harness-php/gate.py ph29-recvfrom-alloc     # 2m40.5s
check.py: PASS
$ python3 harness-php/gate.py ph97-optarg-unwritten   # 2m58.4s
check.py: PASS
```

Full logs: `.temp/php58/gate/ph03.log`, `.temp/php58/gate/ph16.log`,
`.temp/php58/gate/ph29.log`, `.temp/php58/gate/ph97.log`. ⚠ **Those four are
gitignored scratch and will be deleted; the committed evidence is the four gate
records under `results-php/gate/`, which carry `verdict`, `failures` and
`controls_json` directly.** Named here so a reader knows the logs existed, not
so anything depends on them.

| row | `verdict` | `failures` | `controls_json` |
|---|---|---|---|
| `ph03` | `PASS` | 0 | `inside_share.json: FRESH` |
| `ph16` | `PASS` | 0 | `inside_share.json: FRESH`, `spellings.json: FRESH` |
| `ph29` | `PASS` | 0 | `inside_share.json: FRESH`, `spellings.json: FRESH` |
| `ph97` | `PASS` | 0 | nine sidecars, **all FRESH** |

Stage 9b on each: `ok patterns/<row>/controls/inside_share.json pins 10
source(s) by derived_from_sha256, all matching this tree`. ⭐ **No
`report.py` re-render was needed**: adding a `FRESH` sidecar does not move the
published table, so the `gate → report → gate` chain did not fire. Every gate
record's `source_sha256` was re-verified against the tree after the run —
**0 mismatches over 157 paths across the four rows.**

⚠ **The pin is 10 paths, not `ph97`'s 8**: I added `c/kernel.h` and `c/main.c`,
which are compiled into every C cell and which the template pinned neither.

### 4.1 The `ph97` port moved nothing — that is the control for the rewrite

```
matrix value diffs: []          # old sidecar vs new, every cell, every field
new-only keys: row, n_iters, summary, not_this_definition
pin: 8 paths -> 10
```

**Sixteen cells, identical to the digit**, with `n_iters` now derived instead of
hardcoded. The literals `{small: 20000, large: 3000}` were correct, and they
were still literals.

---

## §5 THE TASK FILE'S PREMISES, CHECKED (`PROTOCOL.md` rule 14)

| premise | verdict |
|---|---|
| the three rows have no `inside_share` anywhere; `ph29` has one docstring | ✅ **TRUE** |
| all four rows share `ph97`'s cell/input shape exactly, 96 `marginal_ir_per_call` entries | ✅ **TRUE** |
| the `kernel` symbol survives at `O3/isolated` | ✅ **TRUE** on all 64 cells measured |
| `n_iters`: `ph03` 25000/20000 · `ph16` 25000/12000 · `ph29` 25000/12000 · `ph97` 20000/3000 | ✅ **TRUE**, read back from the headers |
| `_pin.py` exists in three rows only | ✅ **TRUE** |
| one re-gate costs ~2 m 29 s | ✅ **TRUE for `ph03`**; the four ran 2:28.9 – 2:58.4, mean **2:41** |
| ⚠ one callgrind run costs ~6.6 s **even on the 8.4 MB input**, so the 16-run matrix is **~2 min** | ⛔ **TRUE OF THE CELL IT WAS MEASURED ON AND FALSE AS A PER-ROW COST.** Measured 16-run matrices: `ph03` **34.6 s**, `ph16` **17.2 s**, `ph29` **8.7 s**, `ph97` **5.4 s** — **65.9 s for all 64 runs.** The 6.6 s cell (`ph03`/`safe_naive`/`large`) is the heaviest measured; `ph29`'s `large.bin` is the same size to within 0.3 % (8 355 824 B against 8 384 524 B) and its 16 runs average **0.54 s**. ▶ **The cost is set by the `Ir` count, not the input size**, and *"even on the 8.4 MB input"* attributes it to the wrong variable. ⓘ **The premise's `Ir` figure reproduces**: the task file says `1,444,434,324` and my run of that cell recorded `1,444,434,562` — **238 `Ir` apart, 1.6 × 10⁻⁷**, with a different `--callgrind-out-file` path in `argv`, which is the axis `.memory-php/03-numbers.md` says moves this column |
| `ph97`'s `CALLS` literals are correct today | ✅ **TRUE** |

⭐ **So the task's own honest-cost paragraph was over-cautious by ~4× on the
measurement half and right on the gate half** — and the gate half is 91 % of the
bill, so the conclusion (*"the budget is dominated by the gate"*) is **more**
true than it was stated.

---

## §6 THE FREE MEASUREMENT FOR ITEM 128 — REPORTED AS AN EVENT, NOT CHASED

⚠ **Read this as noise unless you are item 128.** Four gate runs, each against
the committed record, diffed leaf by leaf:

| row | `envp_stack_bytes` | `marginal_ir_per_call` cells moved | other movement |
|---|---|---|---|
| `ph03` | **3695 → 3698** | **0 of 96** | 2 edited-doc hashes, 4 ASan diagnostics, 1 Miri wall clock |
| `ph16` | **3697 → 3698** | **0 of 96** | 2 doc hashes, 1 ASan, 2 Miri |
| `ph29` | **3697 → 3698** | **0 of 96** | 2 doc hashes, 2 ASan, 1 Miri |
| `ph97` | 3698 → 3698 | 0 of 96 | 3 hashes, 1 ASan, 1 Miri |

**Three rows on three accidental draws — one `+3`, two `+1` — and the record's
own `domain` field declares each pair incomparable while all 96 cells, including
the `whole` column A1's structural immunity cannot protect, came back
byte-identical.** Total movement: **5 to 9 leaves of 1100 – 1276**, and **zero
`Ir`, zero checksum, zero identity, zero `md5`.**

⛔ **This does NOT show the ±7 term is absent** (`TASK_114` measured it firing),
and `+1` and `+3` draws may land in the same alignment bucket — untested. ⚠ **My
four runs also appended a preflight record and moved the ASan PIDs and Miri
timings named above; a reviewer should not read those as a result.**

---

## §7 WHAT THIS COST, MEASURED

| | |
|---|---|
| 4 re-gates | **10 m 45 s** (2:28.9 + 2:37.4 + 2:40.5 + 2:58.4) |
| 64 callgrind runs | **65.9 s** |
| everything else (selftests, probes, record reads) | **< 5 s** |
| **total machine time** | **≈ 11 m 56 s** |
| re-measures | **0** — `controls/` is in no measurement digest |
| `report.py` renders | **0** — no published table moved |

---

## §8 ⚠⚠ WHAT I AM UNSURE OF

*(Item 129 is a census of exactly these sections. Written for a reader who will
audit it. Every cost below is either measured or labelled an estimate.)*

1. ⛔ **I did NOT repair `ph29`'s `controls/spellings.py` docstring, and that is
   the one artefact F127 named.** The four numbers still sit there unlabelled.
   **Reason, and it is a cost I checked rather than assumed**: that file is
   pinned by its own `controls/spellings.json`, whose `pin.regenerate` is
   `python3 patterns-php/ph29-recvfrom-alloc/controls/spellings.py --verus` — a
   Verus run over the row's variants. Editing one comment therefore stales the
   sidecar and forces that regeneration, which would also rewrite published
   measured numbers as a side effect of a comment fix.
   ⚠⚠ **I DID NOT MEASURE HOW LONG THAT RUN TAKES. That is an UNMEASURED COST
   and I am flagging it as one rather than calling it expensive.** The labels
   are in `NOTES.md` §15 instead, which is free. ▶ **Manager's call.**
2. **The `ph16` `F74`-shares above 1.0 are reported, not explained.** Ten cells,
   largest `1.0279`, all `small.bin`. The mechanism I give — numerator over
   `n_iters` calls, denominator a slope at `collapse.probe_iters` — is
   consistent with the arithmetic and I did **not** isolate it by, say,
   recomputing the marginal at `n_iters`. It could also be a start-of-run
   transient (F93's shape). **Unexplained; do not quote my mechanism as
   measured.**
3. **I did not test whether the two definitions ever disagree in SIGN on a
   difference.** I measured that they disagree in LEVEL (up to ~9 pp on `ph29`)
   and that their Δ columns agree in verdict on the pairs I printed. A sign
   disagreement between the two shares' Δ would be a stronger result and I did
   not look for it. **Estimated cost: minutes, no build** — it is a loop over
   `.tasks-php/php58_record_share.py --pairs`'s output against the sidecars.
   ⚠ **That is an ESTIMATE.**
4. **`F74`'s rule (ii) refuses a pair whose true A1 difference is known to be
   exactly zero**, on `ph03`/`small.bin`: `unsafe` vs `verus`, `Δshare` **0.0330**,
   because the `verus` binary's whole-run total is `+3.64 %` — F74's own
   documented family-B null maximum, arriving here by a different route. I state
   this as a fact about the **rule** and I do **not** propose an exemption for
   `identity`-pinned pairs. n = 1.
5. **Condition (i) is uncomputed and I did not invent a threshold.** `ph29`'s
   `safe_naive` sits at `0.6911` — above `>0.3`, `>0.5` and `>0.6`, and below
   every share on `ph03` and `ph16`. If (i) were ever set at `>0.7` the `+33 %`
   pair would fail **both** conditions instead of one. **I am not proposing that.**
6. **I did not re-read all five rows F127 names.** `ph07`, `ph53` and `ph64`
   still have no `inside_share` control. `.tasks-php/php58_record_share.py`
   computes the F74 share for them **today, from the committed records, at zero
   cost** — but the callgrind matrix does not exist for them. **Measured cost of
   extending: ~16 callgrind runs per row (5–35 s) plus one re-gate per row
   (2:29–2:58).**
7. **The `_pin.py` `ROW` literal is still hand-copied in five rows** (`ph55`,
   `ph56`, `ph97` and my three — six files). I considered deriving it and
   **declined**, because unlike `n_iters` a wrong `ROW` cannot silently corrupt
   a number: it makes every pinned path absent, which is loud. My control's arm
   6 now catches it locally anyway. ⚠ **Deriving it in all six would cost 6
   re-gates ≈ 16 min at my measured per-gate rate — an ESTIMATE by
   multiplication, not a measurement.**
8. **I asserted in three `NOTES.md` sections that the control is "byte-identical
   in all four rows".** True as of this report (`sha256sum`, one hash). Nothing
   enforces it: a future edit to one copy would falsify four documents at once.
   **A check would be one line in a manager tool and I did not write it.**
9. **I did not verify that the `+33 %` sentence is the only place the programme
   publishes a bare `ph29` C-vs-Rust A1 figure.** I checked `RECAP_PHP.md`'s
   *which statistic* cell and the row's own documents. `.web/` is a concurrent
   session and I did not touch or read it.
10. **Scope of the sign flip.** I measured that the C column choice flips the
    sign of the `ph29` C-vs-`safe_naive` A1 figure on `large.bin`, and that on
    `small.bin` it does not (`+39.92 %` vs `+0.95 %` — same sign, 42× apart).
    **I did not check the other rows for the same flip.** F108's corpus figure
    (*"10 of 128 A1 cross-language cell-pairs change SIGN under the swap"*)
    already covers this class; I did not re-derive it.

---

## §9 ROUTED TO THE MANAGER

1. ⭐⭐⭐ **NAME THE TWO SHARES, IN THE AUTHORITATIVE LAYER.**
   `.memory-php/03-numbers.md` says *"NAME THE DENOMINATOR"* (F88) and then
   carries `inside_share` figures in the F74 form without naming it, while the
   only shipped control computes the other one. **This is F88's own rule
   violated by the quantity F88's neighbours are measured in.** The fix is a
   table with two rows; every existing figure is F74's and stays correct once
   labelled.
2. **F127's sentence is one rung off** — the docstring disclaims C vs
   **`safe_tuned`**, the headline makes C vs **`safe_naive`**. Both fail the
   bar; the sentence should say so.
3. **The `+33 %` needs a seven-item label**, and the seventh is `c-clang`'s
   `−4.36 %`. Under F108 (*"one column … is a DIFFERENT SIGN"*) this is the
   programme's most-cited number carrying the defect F108 exists to stop.
4. **Condition (i) of the bar has no threshold.** Six rows could not pin it;
   there are eleven now, and 15 more cells per row than when it was written.
   **A row-by-row sweep would cost nothing** — `--pairs` reads committed records.
5. **`ph29`'s `controls/spellings.py` docstring repair** — §8 item 1, with the
   unmeasured cost named.
6. **`ph07`, `ph53`, `ph64`** still have no control (§8 item 6), with the cost
   measured.
