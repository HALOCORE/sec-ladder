# TASK_163 report — `p49`'s corrections landed, and the sweep found two more sites the review had not

**Role: research engineer.** Scratch, probes, logs and generators under
`.temp/t163/`. No `git add`/`git commit`. `.memory/`, `RECAP.md`,
`results/SYNTHESIS.md`, `harness/check.py`, `harness/measure.py` and
`harness/tools/composition.py` were **not** edited.

---

## 0. THE HEADLINE, AND IT IS NOT E6.2

**E6.2 — the *"34 obligations, the largest in the tree"* claim — SURVIVES**,
derived across all 33 patterns rather than the two it was published on (§1).

**What did not survive is three of the manager's other published numbers, and
one of them is inside `contract_sha256` where two separate readings had already
declared the block clean:**

1. ⚠⚠ **`spec.md`'s `idiom.required[5].c` — INSIDE the hashed contract
   block — carried the item-7 counterfactual verbatim.** `TASK_162` checked
   the hashed `why`, reported it CLEAN, and was **right about the `why`**;
   `TASK_163.md` inherited that verdict and said in terms *"✅ `spec.md`'s
   hashed `why` is CLEAN on this — reviewer-verified. Do not disturb it for
   E1."* **Both statements were true and the BLOCK was still carrying the
   refuted sentence.** ⚠ **A key is not a block. Rule 6's second half is about
   every string inside the fence.** (§2)
2. ⚠⚠ **`verus.rs:365` and `safe_naive.rs:16` carried the same two refuted
   sentences, and both are MEASUREMENT-hashed.** Neither was named by the
   review or by the task file. This is precisely the *"`TASK_156` found three
   more on `p34` after its review"* case the task warned about. (§2)
3. ⚠⚠ **`RECAP.md` finding 62's per-evaluation table is wrong on one cell.**
   It prints *"the guard costs a constant `2.00` `Ir` per evaluation (gcc-O3
   2.00, clang-O3 2.00, **clang-O0 3.00**, gcc-O0 6.00)"*. Those are the guard
   LINE's *identified* `Ir`. At clang `-O0` the `<counts for unidentified
   lines>` bucket moves by **exactly 1.00 more per guard evaluation**, so the
   kernel SYMBOL — the convention `results/*.json` publishes — costs
   **4.00**; `4*G` reproduces the record's `+16.9273` exactly and `3*G` gives
   `12.70`. At clang `-O3` a fifth of the kernel is unidentified and the
   symbol-level per-guard figure is **not constant** (+3.29 / +7.70). ✅ **The
   constant-per-evaluation result is a GCC result.** (§3)

✅ **And the good half is better than the task asked for.** §4c's hedge is
replaced not by a mechanism but by a **zero-parameter law**, exact to
`0.0000 Ir/call` on four published cells (§3).

---

## 1. E6.2 — the obligation census, all 33 patterns. THE CLAIM SURVIVES.

`.temp/t163/obligation_census.py`, `obligation_census.json`. Read out of
`results/gate/p*.json` (`verified`/`pinned` — entry 21's *derived fact* kind,
not a draw) and cross-checked against every `spec.md`'s `verus.obligations`
pin: **the two agree on all 33 rows, 0 errors anywhere.**

```
pat     pin verified twin  lines clauses proof_fn spec_fn exec_fn invariant assert
p49      34      34    37   1126      33        3      17      15         5     22
p29      25      25    30   1494      34        0      16      19         2     58
p34      24      24    29   1183      39        5       8      19         2     41
p28      23      23    28   1709      34        0      18      20         2     75
p46      21      21    24    625      21        1      11      12         5     16
p22      20      20    23    743      28        5       8      10         2     17
p13/p14  19 . p06/p09/p42 18 . p23/p35 16 . p12/p27/p32 15 . p01 14 (TWO sources)
p38 13 . p05/p08/p11/p18/p19/p36/p47 12 . p07/p10/p16/p17/p25 10 . p02/p03/p04 9

RANK OF p49:  pin 1/33 . verified 1/33 . twin 1/33
              lines 4/33 . clauses 4/33 . spec_fn 2/33 . proof_fn 5/33
              exec_fn 7/33 . invariant 6/33 . assert 5/33
```

* **p49 34 is rank 1 of 33, margin 9 over `p29`'s 25**, and its 37 twin
  obligations are rank 1 too. `p01` is the only pattern with two obligation
  sources; its total 14 is still 20 below.
* ⚠ **The two comparisons the claim was published on were the right two by
  luck** — `p29` 25 really is the runner-up — but `p32` 15 is the
  **fourteenth** row, not the second.
* ⚠⚠ **The number does not mean what a reader will take it to mean, and the
  gate says so itself:** `check.py:4981`'s diagnostic calls the count *"one
  Verus query per function plus one per loop body … a checksum over the
  function/loop **skeleton**"* and *"not sensitive to any semantic weakening"*.
  **On every burden-shaped quantity p49 is 4th or 5th, and `p28` leads three of
  them.** The reviewer's counter-example (`p34`'s 1183 lines against p49's
  1126) is right about line count and does not touch the obligation count.
* **Mechanism, so it is not just a rank:** p49's obligations are the *smallest*
  of the top four — **33.1 lines each**, against `p29`'s 59.8, `p34`'s 49.3
  and `p28`'s 74.3. It leads because its proof is the most **decomposed**, not
  because it is the largest.

**Safe wording:** *"the largest OBLIGATION COUNT in the tree — 34 against
`p29`'s 25, over all 33 rows — which is a count of verified functions and
loop bodies and not a measure of proof burden; on lines, clauses and proof text
`p49` is fourth."*

---

## 2. E1 — the refuted mechanism, swept

**Named by the review, fixed:**

| site | hashed into | fix |
|---|---|---|
| `README.md:73-78` | gate | the guard mechanism replaced by the measured one — **guard TRUE 67 195 / FALSE 30 263, 31.1 % of 97 458 evaluations**; the real defect is *no record is ever born owned* |
| `c/kernel.c` epilogue | **measurement** | *"is what makes the PROVENANCE repair benign-observable"* → **SUFFICIENT, NOT NECESSARY**, with the 2-of-3 counterfactual and its mechanism |
| `c/kernel_hardened.c` epilogue | **measurement** | same, plus a sentence on what the flag prices in the hardened rung |

**NOT named by the review or the task file, found by the sweep:**

| site | hashed into | note |
|---|---|---|
| ⚠ **`verus.rs:365`** (`fold_recs` doc comment) | **measurement** | the same item-7 counterfactual |
| ⚠ **`safe_naive.rs:16`** (module header) | **measurement** | *"the two `Rc` arms differ in ONE type and nothing else"* |
| ⚠⚠ **`spec.md` `idiom.required[5].c`** | **CONTRACT + gate** | the same item-7 counterfactual, **inside `contract_sha256`** |
| `controls/arm_rc_makemut.rs:5`, `controls/arm_rc_refcell.rs:23` | gate | *"with one type changed"* |

**The contract move, disclosed.** Pre-image saved **verbatim**
(`.temp/t163/contract_step5_preedit.txt`, 46 012 chars, re-serialises to
`d339ef90…` = the shipped `contract_sha256`), which is `TASK_156`'s standard.
Generator `.temp/t163/fix_why.py` — asserted counts, `--check` mode,
idempotent.

```
contract_sha256  BEFORE  d339ef900e0b2c59c1f8b3a851fdebe3b46ae8f999294e593a5dc5d7a667e0be
contract_sha256  AFTER   3446cc4081a72c5400b449802402769b8144cfabbf73b57e00a23a563a31390d

harness/tools/contract_diff.py p49  ->  3 path(s) moved:
    ['idiom', 'idiom.required', 'idiom.why']
  collapse driver ensures identity kernel miri model note requires verus
  idiom.forbidden                                    ALL IDENTICAL
```

✅ **No pin moved.** All **43** backticked spellings in `idiom.required` are
byte-identical before and after, and `idiom.forbidden` is byte-identical
(`.temp/t163/` verification printed in §7).

---

## 3. E3 — the decomposition CLOSES, to a law with no fitted parameter

`.temp/t163/e3_decomp.py` (line-level callgrind), `.temp/t163/e3_law.py`.

**The `-g` builds are code-identical to the measured cells on all EIGHT C
cells**, by `n_fn_nopad` **and** `md5_raw` — gcc `-O0` 364/430, gcc `-O3`
274/410, clang `-O0` 306/354, clang `-O3` 350/481.

`G` = guard evaluations per call, `C` = intern-table creations per call, both
counted **directly** by an instrumented copy of `c/kernel_hardened.c` (two
counters spliced in by asserted substitution) linked against the **shipped**
driver and run on the **shipped** blobs:

```
small.bin  200 000 calls   G = 4.2318    C = 4.6256
large.bin   20 000 calls   G = 22.3508   C = 5.6449
```

```
input      cell     law              predicted     record   residual
small.bin  gcc/O3   2*G - 2*C - 2      -2.7877    -2.7877    -0.0000
large.bin  gcc/O3   2*G - 2*C - 2     +31.4117   +31.4117    -0.0000
small.bin  gcc/O0   6*G               +25.3909   +25.3909    -0.0000
small.bin  clang/O0 4*G               +16.9273   +16.9273    +0.0000
                  worst |residual| over 4 published cells: 0.0000 Ir/call
```

The gcc `-O3` line diff sums over **every** moving line, with **zero**
unidentified `Ir`:

```
small.bin  +8.43 if (rshd[t]) { .. -4.62 m[base+j]=p49_cbyte(..) .. -4.62 abump+=w
           -1.00 key .. -1.00 w   ->  -2.81 = the whole kernel delta
large.bin +44.75 .. -5.70 .. -5.70 .. -1.00 .. -1.00  ->  +31.35 = the whole delta
```

`abump` and the `p49_fill` store each lose exactly **9 237** `Ir` on the small
probe — precisely its 9 237 intern creations, i.e. **one instruction per
creation at each of two sites** — plus one per call in the operand decode.

⚠⚠⚠ **So the sign is set by the EVENT MIX, and the crossover has a closed
form: at gcc `-O3` the hardened kernel is CHEAPER exactly when `G < C + 1`.**
`small.bin` 4.23 < 5.63 → cheaper; `large.bin` 22.35 > 6.64 → dearer.
**gcc alone reverses between its own two inputs**, so *"a reversal between
COMPILERS"* is the wrong reading of §4b.

**The per-evaluation table, corrected:**

```
cell         guard LINE   KERNEL SYMBOL   unidentified   verdict
gcc   -O3        2.00         2.00           0.0 %       exact
gcc   -O0        6.00         6.00           0.0 %       exact
clang -O0        3.00      >> 4.00 <<        0.7 %       the LINE count is SHORT by 1.00
clang -O3        2.00      3.29 / 7.70    19.5-20.5 %    NOT a constant
```

⚠ **`clang-O0 3.00` in `RECAP.md` finding 62 and `TASK_162` MAJOR 6 is the
line figure, not the symbol figure.** The unidentified bucket moves by
`+1.00` per guard evaluation on top of it. **No clang decomposition is
published and none should be quoted**: the file TOTAL closes on clang, the
per-LINE attribution does not.

---

## 4. E2 — the `Rc` arms, decomposed rather than weakened

`.temp/t163/e2_arms.py`, `e2_arms.json`. Every variant derived from the shipped
arm by **asserted** substitution, built with
`harness/build.py::rust_flags("O3","isolated","unwind")`, scored on the **5 of
9** inputs on which the two C rungs print different numbers at all
(`adversarial-cascade`, `-cowfull`, `-many`, `-rehash`, `-share`).

```
arm                                              =R1h  =R1  NEITHER
C_ship    query + refusal + charge + flag clear     5    0      0
C_bare    the whole 20-line block deleted           0    0      5
C_flag    query + FLAG CLEAR only                   4    0      1
C_budget  query + refusal + charge, NO flag clear   1    0      4
C_getmut  the query via Rc::get_mut(..).is_none()   5    0      0
C_posthoc the query AFTER the write, via Rc::as_ptr 4    0      1
B_ship    the RefCell arm (the bug)                 0    5      0

C_bare vs B_ship:  EQUAL on the 4 non-discriminating inputs,
                   DIFFERENT on all 5 discriminating ones.
```

1. **The block is the BENCHMARK'S STORAGE ACCOUNTING, not the safety** — it
   clears the ownership flag the epilogue folds and charges the private copy to
   the same fixed 44-byte pool `c/kernel_hardened.c` charges it to.
2. **Both halves are load-bearing** — flag clear alone 4/5, budget alone 1/5,
   and the one the budget carries is `adversarial-cowfull.bin`.
3. **The ownership QUESTION is not tied to `strong_count`** — `Rc::get_mut`
   matches 5/5. ⚠ **The REFUSAL is the only part that must precede the write**:
   `C_posthoc` asks nothing beforehand and reads the answer off `Rc::as_ptr`
   across `make_mut`; it recovers the flag and the charge, cannot refuse, and
   fails on exactly `adversarial-cowfull.bin`.
4. ✅ **The residue of *"one type apart"* is TRUE and is the better claim:**
   with the block deleted from arm C the two arms are *literally* one type
   apart and still disagree on exactly the 5 discriminating inputs. **The TYPE
   carries the safety; the BLOCK carries the C kernel's accounting.** What
   `Rc::make_mut` replaces is exactly ONE of the four things
   `c/kernel_hardened.c`'s safety line does — the COPY and its aliasing
   correctness. The other three are hand-written in safe Rust either way.

---

## 5. E4 — one figure, and one range

`.temp/t163/e4_ratios.py`. **1 of the 16 shipped §4e cells disagreed with the
record**: `small.bin c-gcc` shipped `0.99`, record `1974.4131 / 1971.6254 =
1.001414 → 1.00`. The other 15 re-derive exactly, as do **all 32 cells of
§4a, all 8 deltas of §4b and every §4f wall figure** (and the `0.78–3.10 %`
spread range, which is over all `-O3 isolated` cells and is right).

⚠ **One more, not in the task file:** §4e's prose said clang's C is
*"15–17 %"* dearer than gcc's. Like-for-like it is 15.8 / 15.4 / 16.7 /
**18.0** %. Corrected to 15–18 %.

---

## 6. E5 — the census now has a must-fire arm, and the arena cap is NOT unreachable

`model.py::census_selftest()`, run from `selfcheck()` once per input on every
gate invocation. Three groups: the census answering three ways on four probes;
`no_share_break_problems` itself REPORTING (including the `adversarial-` early
return); and the arena-capacity refusal DECIDING an observable.

⚠ **The task file offered *"say plainly that it is unreachable"*. It is not
unreachable** — seven distinct `(key, w = 3)` entries need **21** bytes of a
**20**-byte arena, and `len(table) == 6 < NENT` there, so the ARENA conjunct is
what decides. `_PROBE_ARENA` is built so the refusal moves an answer: with the
cap the window ends with **7** records and `BREAK 13 % 7 == 6` selects the
OWNED record (detector silent); without it, **8** records, `13 % 8 == 5`
selects an interned one and `published` fires. **What is true is the
reachability census: it decides nothing on any shipped window**, which is why
the arm is a synthetic probe and not a tenth blob.

`.temp/t163/e5_mutate.py` — every mutation an asserted substitution, every
arm run inside a `try` so a crash is reported AS a crash
(`.memory/03-measurement.md` entry 19's refinement):

```
W1-census-neutered            REPORTED     W1-check-unwired              REPORTED
W1-census-always-true         REPORTED     W1-check-adversarial-always   REPORTED
W1-census-guard-inverted      REPORTED     S3-sim-arena-cap-dropped      REPORTED
S3-census-arena-cap-dropped   REPORTED     C0-control-inert              SILENT
                        7 of 7 REPORT with the designed message, 0 SILENT, 0 CRASH
```

---

## 7. Evidence — commands, and each one's OWN exit status

⚠ Every `rc` below was read from the thing that ran, never from a pipeline or an
`echo`, and every gate verdict was read out of `results/gate/p49-interned-pool.json`.

```
harness/check.py p49            GATE 1   rc=1  verdict FAIL  blocked []  complete_run true
    failures: exactly 2, BOTH [tables] -- the published table cites contract
    d339ef900e0b and spec.md now hashes to 3446cc4081a7. This is the outcome
    TASK_163.md predicted ("report.py p49 if the gate fails on [tables]").
    294 `ok` lines; loud = 1 (the known arr_set_unchecked parameter-coverage
    false positive, unchanged).

harness/measure.py p49                   rc=0   (.temp/t163/measure.log)

harness/report.py p49                    rc=0   22 insertions / 22 deletions

harness/check.py p49            GATE 2   rc=0  verdict PASS  blocked []  failures []
                                         complete_run true
                                         contract_sha256 3446cc4081a7...
                                         verus.rs 34 verified, 0 errors, pinned 34, TCB 5

harness/measure.py --check-stale         rc=0   66 record(s) examined, 0 STALE
                                                (66 = 33 gate + 33 measurement)
harness/tools/composition.py --check     rc=0   OK: 33 patterns, 10 classes
harness/tools/temp_citations.py          rc=0   new=0 unclassified=0 resolved=4
harness/tools/contract_diff.py p49       rc=1   (= "changed", the disclosure)
synthesis/licence.py --emit synthesis/licence.json
                                         rc=0   33 patterns, 132 pair verdicts
synthesis/synthesize.py                  rc=0   92 856 bytes, 705 lines
```

**The nine control regenerations, each status recorded separately**
(`.temp/t163/regen_controls.sh`, `.temp/t163/ctl/status.txt`) — run AFTER the
sources were final, which is the task file's rule and `TASK_139`'s cost when it
was not:

```
safety_line rc=0 1s . no_overlap rc=0 0s . no_share_break rc=0 0s
threshold rc=0 1s . spellings rc=0 14s . safe_arms rc=0 4s . rust_bug rc=0 5s
detectors rc=0 30s . proof_mutants rc=0 178s      -- 9 of 9, zero `problems`
```

`proof_mutants` re-ran because `verus.rs` moved: **9 of 9 behaved as expected**,
M0 control `34/0`, M1/M2/X1/X2/X3/M5 fail as designed, M3/M4 verify.
`detectors`: **216 kernel cells, 0 diagnostics; 36 control cells, 16 firings**.
`safe_arms`: **every checksum identical to before the edits**, and the JSON now
carries a `discriminating` flag per row and a `discriminating_inputs` list.

**Every control JSON's `derived_from_sha256` re-hashes clean against the tree**
(9 files, 46 pinned paths, 0 moved, 0 absent).

### The re-measure, PREDICTED BEFORE THE RUN and EXACT

The prediction is in `.temp/t163/NOTES.md`, written before `measure.py` started.

```
                      PREDICTED   MEASURED
wall/min_s                   32         32
wall/median_s                32         32
wall/spread_pct              32         32
source_sha256                 5          5   (kernel.c, kernel_hardened.c,
                                              model.py, safe_naive.rs, verus.rs)
generated_utc                 1          1
git/commit                    1          1
git/dirty_files               1          1
------------------------------------------
TOTAL                       104        104   of 1404 leaves
Ir                            0          0
static (md5_raw, md5_raw_norel, md5_fn, n_fn_nopad, bulk_calls, ...)
                              0          0
checksum                      0          0
input_sha256                  0          0
wall/reps                     0          0
```

**104 predicted, 104 moved, and the breakdown matches leaf for leaf.** The named
risk — a surviving panic pad's `core::panic::Location` line number shifting
under `safe_naive.rs`'s 26 added header lines and moving `md5_raw` — **did
not materialise**: the line number is a field inside a rodata struct that does
not move, so no `lea` displacement changed.

### The contract move, verified

```
$ python3 .temp/t163/verify_pins.py
idiom.required   backticked spellings: before 43, after 43 -- IDENTICAL
idiom.forbidden  backticked spellings: before 16, after 16 -- IDENTICAL
every top-level key except `idiom` is byte-identical: YES
rc=0
```

### `p49` IS NOW FINISHED — the anchored completeness check

```
$ awk '/^## The findings so far/,/^## Retracted/' RECAP.md     | grep -E '^[0-9]+\. ' > .temp/t163/h.txt      # 62 finding headers
$ for d in patterns/p*/; do id=$(basename "$d" | cut -d- -f1)
    grep -q "\b$id\b" .temp/t163/h.txt || echo "MISSING: $id"; done
MISSING: p01
```

**`p01` alone — the known benign exception.** `p49` was `MISSING` at
`TASK_162` and is not now: `RECAP.md` finding 62 exists (the manager's), and
`results/synthesis.md` now carries **10** mentions of `p49` where it carried 0.

PROTOCOL rule 10's report-file sweep prints only the three `TASK_NNN`
placeholders.

---

## 8. Problems

1. ⚠⚠ **`results/SYNTHESIS.md` (CAPITALS, hand-written) IS SEVEN ROWS BEHIND
   AND I DID NOT TOUCH IT**, as instructed. Its title still reads *"What **26**
   kernels say…"* and it was written at `TASK_108` against 26 built patterns;
   the tree has **33**. **`p49`: 0 mentions. `p25`: 1 mention, and it is
   stale** — line 857 calls `p25` a *deferral* (*"`p20`/`p21`/`p25` are the
   deferrals"*) when `p25` has been BUILT since `TASK_090`-ish and is one of the
   five rows entry 23's `-O3 isolated` null table names. ⚠ **So the one
   `p25` mention is not merely absent, it says the opposite of the tree.**
   Also absent by name: `p35`, `p46`, `p47` and `p49`. **Manager work.**
2. **Gate 1 failed, as designed.** `blocked []`, `complete_run true`, and the
   only two failures were `[tables]` staleness from the contract move. It cost
   nothing beyond the budgeted second gate.
3. ⚠ **`harness/tools/temp_citations.py --include-tasks` FAILS with 7 new
   dangling citations, and NONE of them is mine.** All seven are pre-existing
   `.tasks/` text: `PROTOCOL.md:52,54` (`.temp/h.$$`, the shell scratch in
   rule 1's own check), `TASK_001.md:25`, `TASK_029.md:72` (a file the text
   itself says *"never existed"*), `TASK_064_REVIEW.md:100` (a file the text
   says was deleted), `TASK_080.md:224` and `TASK_084.md:6`. **`.tasks/` is
   exempt by default and the default run is `rc=0`**, which is the check the
   task file names — so this is a clean negative and a note, not a finding.
4. **`harness/tools/temp_citations.py` reports 4 baseline entries NO LONGER
   DANGLING** (`.temp/p49ctl/{detectors,rust_bug,safe_arms,spellings}`), because
   my control regeneration recreated those scratch directories. It says
   *"Not a failure. Run `--update` to prune, so the baseline cannot rot."*
   **I did not run `--update`** — the baseline is a committed artefact and
   pruning it is a manager decision. `rc=0`.

## 9. Unsure / not done

* **The three-item `check.py` gate bundle** (stage 9b's unread sidecar verdict;
  `global layout` as a sixth body-less form; `check_marginal_ir`'s docstring)
  was **not** touched — the task says report only, and it needs a 33-pattern
  re-gate.
* **No clang-side line decomposition is published**, and §4c now says why in
  terms: 19.5–20.5 % of the kernel's `Ir` is unidentified at `-O3` and the
  symbol-level per-guard figure is not constant. ⚠ **What I did NOT do is find
  out WHERE clang's unidentified `Ir` goes.** At `-O0` it is exactly
  `1.00 × G`, which is suspiciously clean and might be one attributable
  instruction; I did not chase it.
* **The `Rc` arm variants are scored on ANSWERS, not priced.** `C_getmut` and
  `C_posthoc` are new arms I invented for this task; neither is shipped and
  neither carries an `Ir`.
* **`census_selftest()`'s probes are hand-written windows**, verified by
  `.temp/t163/e5_probe.py` against the shipped model and by
  `.temp/t163/e5_mutate.py` against seven planted defects. I did **not** fuzz
  them, and a reader should check the arithmetic in the `_PROBE_ARENA`
  docstring rather than take the constants on trust.
* **I did not re-run the whole tree's gate.** Only `p49` was gated, twice.
  `--check-stale` covers the other 32 records' SOURCES and, per entry 21,
  cannot see a re-drawn `marginal_ir_per_call`.
* **I did not price the `provenance` arm's benign-observable claim beyond
  re-stating `TASK_162`'s numbers.** §3b's new table (`0 of 3` / `2 of 3`) is
  the reviewer's measurement, cited as theirs; I did not re-run
  `.temp/t162/item7_epilogue.py`.
* ⚠ **One judgement call worth flagging:** the task said `spec.md`'s hashed
  `why` is clean on E1 and *"do not disturb it"*. I disturbed the **block** —
  not the `why` — because `idiom.required[5].c` carried the refuted sentence
  and the move was already being made for E2. If the manager disagrees, the
  pre-image is saved verbatim and `fix_why.py` is a three-line revert.

## 10. Memory updates

**None written by me** — `.memory/` and `RECAP.md` are the manager's, and the
task forbids them. Durable facts that belong there, in the order I would rank
them:

1. ⚠⚠ **`.memory/03-measurement.md` — RECAP finding 62's clang-`O0`
   `3.00` is the LINE figure; the SYMBOL figure is `4.00`.** With it,
   `delta = 4*G` reproduces the published `+16.9273` exactly. And the
   *"constant `2.00` per evaluation"* headline is a **gcc** result: at clang
   `-O3` a fifth of the kernel is unidentified and the symbol-level per-guard
   cost is `+3.29` / `+7.70`, not a constant. **New general lesson: a
   `callgrind_annotate --auto` per-line diff and a kernel-EXCLUSIVE record
   figure are different conventions, and the `<counts for unidentified lines>`
   bucket is the gap between them. Diff it too, or the decomposition is short
   by whatever it holds.**
2. ⚠⚠ **`.memory/04-verus.md` / `01-ladder.md` — the obligation count is a
   FUNCTION/LOOP SKELETON CHECKSUM and ranks differently from every burden
   quantity.** p49 is 1st of 33 on obligations and 4th on lines, clauses and
   proof text; `p28` leads three of those. Full census:
   `.temp/t163/obligation_census.py` and `.temp/t163/obligation_census.json`.
3. ⚠⚠ **`PROTOCOL.md` rule 6 / `.memory/01-ladder.md` — A KEY IS NOT A
   BLOCK.** `TASK_162` checked the hashed `why` for the item-7 counterfactual,
   reported it CLEAN, and **was right**; `TASK_163.md` inherited that and said
   *"do not disturb it"*. `idiom.required[5].c`, inside the same
   `contract_sha256`, carried the sentence verbatim. **Rule 6's second half
   means every string inside the fence, not the `why`.** ⚠ This is the second
   time on this row a false sentence has survived under a matching hash, and
   the fifth false sentence the hash has matched over.
4. ✅ **`.memory/01-ladder.md` — the safe-Rust result, restated correctly.**
   *"One type apart"* is false of the shipped pair and TRUE of the pair with
   the accounting removed. **What `Rc::make_mut` replaces is exactly ONE of the
   four things a C copy-on-write safety line does — the COPY.** The ownership
   query, the budget refusal and the flag clear are hand-written in safe Rust
   either way, and the REFUSAL is the only part that must precede the write.
5. ✅ **`.memory/03-measurement.md` — a zero-parameter law that closes on
   four published cells.** `delta/call = 2G − 2C − 2` at gcc `-O3`, `6G` at
   gcc `-O0`, `4G` at clang `-O0`; worst residual `0.0000 Ir/call`. **The sign
   condition is `G < C + 1`** — the safety line is free exactly when the
   window creates more intern entries than it evaluates the guard. **A reversal
   between INPUT MIXES, not between compilers.**
6. ✅ **`.memory/03-measurement.md` entry 19 — the p49 census arm is a second
   exemplar beside `p32`'s, and a better one:** 7 of 7 planted defects REPORT
   with the designed message and **0 crash**, because every arm runs inside a
   `try` that turns an exception into the designed problem string — which is
   the repair entry 19 asks for in its own last paragraph. ⚠ And **the arena
   cap is NOT unreachable**; it is unreached on the shipped corpus, which is a
   different claim and needs a synthetic probe rather than a tenth blob.
7. **`.memory/03-measurement.md` — the re-measure prediction was EXACT for the
   third task running** (`TASK_154` 110, `TASK_156` 103, `TASK_163` 104), and
   the leaf breakdown matched category by category. **A comment-only edit to a
   measurement-hashed rung source moves the wall column, the source hashes and
   the provenance block, and nothing else.**

---

**PROTOCOL rule 2 running count: launched from 920, +5 = 925.**
The five:
*(1)* `TASK_163.md` E1's *"✅ `spec.md`'s hashed `why` is CLEAN on this —
reviewer-verified. Do not disturb it for E1"* — **true of the `why` and false
of the BLOCK**: `idiom.required[5].c`, inside the same `contract_sha256`,
carried the refuted item-7 counterfactual verbatim;
*(2)* the sweep the task file asked for found **two more MEASUREMENT-hashed
sites nobody had named** — `verus.rs:365` and `safe_naive.rs:16`, each
carrying a sentence already withdrawn elsewhere in the same pattern;
*(3)* `RECAP.md` finding 62's per-evaluation table — ***"clang-O0 3.00"*
is the LINE figure; the published kernel-SYMBOL figure is 4.00**, and
*"clang-O3 2.00"* is a line-attribution artefact because a fifth of that
cell's `Ir` is unidentified and the symbol-level cost is not constant;
*(4)* `TASK_163.md` E5's offer to *"say plainly that it is unreachable"* —
**the arena cap is reachable** (7 distinct `(key, w=3)` entries need 21 bytes of
a 20-byte arena); what is true is that it is *unreached on the shipped corpus*,
which is a different claim and takes a synthetic probe rather than a tenth blob;
*(5)* `NOTES.md` §4e's *"clang's C is 15–17 % dearer than gcc's"* — the
hardened/hardened figure on `large.bin` is **18.0 %**.
⚠ **Three of the five are the MANAGER's or the task file's; two are the
ENGINEER's own earlier text.** ✅ **E6.2, the call the task file named as the
one to attack, SURVIVES** — derived across all 33 patterns rather than the
two it was published on, with the caveat that the quantity is a skeleton
checksum and `p49` is 4th on every burden-shaped measure.
⚠ **Reconciliation across branches is the manager's job, not mine.**
