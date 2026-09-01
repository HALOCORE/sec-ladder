# TASK_159 report — E1's null rule landed, and E1's own null table was wrong

**Role: research engineer.** All five items landed. **One re-gate, no re-measure**
— `spec.md` was not touched at all, inside or outside its fence, so
`contract_sha256` did not move; the measurement record is untouched.

⚠⚠ **THE HEADLINE IS A REFUTATION OF THE THING E1 RESTS ON.** The task file asked
me to attack the null table — *"check the mode split, check the four-pattern
figure, and check that the three affected numbers are the only three"*. **The
mode split is right and the LEVEL is wrong: the table published as `-O3 ISOLATED
(the published column)` has its two largest entries at `-O0`.** The three
affected numbers survive unchanged.

---

## 1. ⚠⚠⚠ E1's NULL TABLE IS MISLABELLED — `p28 1732.73` AND `p29 425.80` ARE `-O0` CELLS

`.tasks/TASK_159.md` §E1, `RECAP.md` finding 60 and `.memory/03-measurement.md`
entry 23 all print, verbatim:

> ```
> R4/R5 null, -O3 ISOLATED (the published column)
>   p28 1732.73 · p29 425.80 · p25 269.52 · p42 31.00 · everything else <= 6.00
> ```

Read straight out of the 32 committed gate records
(`.temp/t159/nullscan.py`, `.temp/t159/nullscan.out`):

```
p28  O0 small +281.28   O0 large +1732.73   O3 small +0.00   O3 large  +1.01
p29  O0 small +113.76   O0 large  +425.80   O3 small +0.00   O3 large  -0.02
```

**Both of the table's largest entries are `-O0 isolated`.** At `-O3 isolated` —
the level `synthesis/synthesize.py` publishes, and the only level any of the
corrections it scores are taken at (`marginal()` and `ir_per_call()` both default
to `opt="O3", mode="isolated"`) — **p28 reads `+1.01` and p29 reads `−0.02`.**
The quoted list is the max over **isolated at both levels**, which is a different
statistic from the one it is labelled with. Reproduced two ways: by
`synthesize.py`'s own `derived_correction`, and by reading
`marginal_ir_per_call` out of the gate JSONs directly. The two agree on all 64
`(pattern, blob)` cells to `1e-9`, because R4's and R5's `kernel_exclusive_ir`
are equal on every one of them.

**The true `-O3 isolated` null, complete:**

```
p25 large +269.52 · p42 large -31.00 · p03 small/large +6.00 · p04 small/large +6.00
p02 small/large -2.00 · p28 large +1.01 · everything else <= 1.00
```

⚠ **This is the THIRD correction to the same derivation.** `TASK_158` M1 removed
`whole` from the max and was right to; **the level was never removed with it.**
The failure is the same shape both times: *maxing a null over cells that are not
the published cell.*

### 1b. *"Real exposure is FOUR patterns"* is `-O0 isolated`'s count

`{p28, p29, p25, p42}` are exactly the four patterns at `|null| ≥ 20` **in `-O0
isolated`**. At `-O3 isolated`, **8 rows across 5 patterns** clear the `2.00`
floor and **2 patterns** (`p25`, `p42`) reach `16.00`. Also: `TASK_158` §1b's own
`-O3 isolated` code block lists **five** patterns (p25, p42, p03, p04, p02) under
the words *"four patterns"*, so the figure disagreed with its own list at the
moment it was written.

### 1c. *"Eight of that top ten read `−1.00`"* is wrong in the VALUE

Of the ten patterns whose all-cells max is `≥ 20`, at `-O3 isolated`:

```
p28 +1.01   p11 -1.00   p29 -0.02   p25 +269.52   p35 -1.00
p14  0.00   p42 -31.00   p17 -1.00   p18  -1.00   p13   -1.00
```

**Eight of the ten are negligible (`|v| ≤ 1.01`) — the substance holds — but
exactly FIVE read `−1.00`.** Three read `{+1.01, −0.02, 0.00}`.

### 1d. ✅ CLEAN NEGATIVE — the three affected numbers ARE the only three

Scored over **all four `PAIRS` × 32 patterns × 2 blobs** (128 rows), the rows
with `|correction| ≥ FLOOR` and `|correction| ≤ |own null|` are exactly:

```
p02 small gcc-clang  +2.00  vs  -2.00    (1.00x, mid band)
p02 large gcc-clang  +2.00  vs  -2.00    (1.00x, mid band)
p25 large gcc-clang +19.42  vs +269.52  (13.88x, CONFIDENT band)
p42 large gcc-clang  +5.00  vs -31.00    (6.20x, mid band)
```

**4 rows, 3 patterns, ALL in `gcc-clang`. ZERO in `R2-R4`, ZERO in `R3-R4`.**
Only **one** (`p25 large`) was in the `CONFIDENT` band. ✅ **And none of them is
touched by the level correction above** — they are `-O3 isolated` rows scored
against `-O3 isolated` nulls, so p28's and p29's `-O0` figures never reached
them.

### 1e. ⚠ NEW, and not in the review: the rule MUST exclude the self pair

Scored against itself, the `R5-R4` column **refuses every one of the 8 rows it
prints, at a ratio of exactly `1.00x`.** A control cannot be its own control.
`null_for()` returns `None` on `("verus", "unsafe")` and the published text says
why.

### 1f. What landed, in `synthesis/synthesize.py` only (no re-gate, no re-measure)

| thing | what it is |
|---|---|
| `NULL_PAIR`, `r5_null()`, `null_for()` | the per-`(pattern, blob)` null, and the self-pair exclusion |
| `classify(c, null)` | **PURE** — `(correction, null)` in, `low`/`mid`/`high`/`refused` out, so it can be driven on PLANTED values |
| `null_rule_selftest()` | **9 planted arms (3 must-fire, 6 silent) + 1 live must-fire arm**; raises `SystemExit` rather than publishing if any arm disagrees |
| `R5_ROW_WHY` | per-row resolution registry; **a row with no entry prints `UNRESOLVED`, loudly** |
| `†` in `derived()` | the marker, with the null printed beside the figure |
| §2 | the null table, the refusal table, the selftest table, and the `-O0`/`-O3` correction above — all derived on every run |
| §5 claim 1 | the false paragraph replaced by text derived from the same list that produces `broke` |

**The rule fires:** `p25-realloc-growth | ... | large -71.74 (+19.42) **†** (own
null +269.52)` where the old code printed `**large -71.74** (+19.42)` in the band
its own legend calls *"every one is real"*.

✅ **The must-fire arm caught a defect in itself on the first run.** I wrote
`classify(19.43, -19.42)` with `want="mid"`; the answer is `high` (19.43 ≥
CONFIDENT), and `synthesize.py` **refused to write the artefact**:

```
null_rule_selftest FAILED: silent one Ir over its null promotes normally: got 'high' want 'mid'
```

### 1g. ⚠ §5 claim 1's false sentence, and how it is prevented from returning

The published `results/synthesis.md:613–615` listed **7** rows, asserted *"every
one of those rows is in the uncertain 2.00–16.00 band"* while `p42 large −31.00`
is `≥ 16.00` and prints **bold** in §2, then resolved *"all six"*. The list was
computed and the paragraph was typed. It is now **8 rows (p25 added), 6 mid and 2
`≥ CONFIDENT`**, each with its own resolution bullet, and the counts, the
band split and the bullets all come off `broke_rows`.

---

## 2. E3 — the cost headline. `controls/rederive.py` REBUILT: 5 arms, BOTH compilers

`.temp/t159/rederive.log`, `rc=0`, `problems: []`. **24 checksums (3 generated
arms × 8 inputs) all agree with `model.py`, and every one is ASan- and
UBSan-clean.** Three repair *sites* are now built, not two:

```
R1h       the READ, guarded    (shipped)
rederive  the READ, unconditional            -- standard-clean
fixup     the GROWTH, `if (cur != NULL)`     -- ⚠ NOT standard-clean
fixup2    the GROWTH, an `int have` bit      -- standard-clean
```

**Kernel-exclusive marginal `Ir`/call over R1, `isolated`:**

| cc | input | opt | R1h | `rederive` | `fixup` | `fixup2` |
|---|---|---|---:|---:|---:|---:|
| gcc | small | `-O0` | +14.76 | +7.38 | +2.18 | +5.90 |
| gcc | small | `-O3` | +24.69 | +10.87 | +14.14 | +21.67 |
| gcc | large | `-O0` | +131.08 | +65.54 | +2.68 | +19.77 |
| gcc | large | `-O3` | +164.39 | +65.67 | +69.69 | +104.21 |
| clang | small | `-O0` | +18.45 | +3.69 | +3.27 | +6.99 |
| clang | small | `-O3` | +18.72 | +3.72 | +17.25 | +26.43 |
| clang | large | `-O0` | +163.85 | +32.77 | +4.02 | +21.11 |
| clang | large | `-O3` | +93.65 | +17.09 | +60.47 | +128.85 |

**M5 — *"about half, on both compilers"*.** R1h ÷ `rederive`: gcc `2.00 / 2.27 /
2.00 / 2.50`, clang `5.00 / 5.03 / 5.00 / 5.48`. The row now publishes
**`2.0–2.5×` (gcc) and `5.0–5.5×` (clang)** and says which is which.

**M6 — *"the safer repair dominates"*.** Between the two **standard-clean**
repairs the ordering reverses: `fixup2` wins 3 of the 4 `-O0` cells (`3.32×` on
gcc `large`) and `rederive` wins **all four** `-O3` cells.

⚠ **A correction to the REVIEW.** `TASK_158` §4b gives the `-O3` range as
*"1.6x (gcc large) to 7.1x (clang small)"*. `clang large -O3` is
`128.85 / 17.09 = 7.54×`, which is the maximum. **The published range is
`1.59× … 7.54×`.**

✅ **Every figure in `TASK_158`'s `.temp/t158/search.py` + `clangmarg.py` table
reproduces EXACTLY here, in a different session, from a different script, inside
the pattern's own committed control.** That is 32 dynamic cells and 20 static
cells agreeing to the hundredth.

⚠ **The convention is now named** (`TASK_158` minor 3): every `Ir` figure in
`rederive.json` and `NOTES.md` §3c is **kernel-exclusive**, and
`rederive.json`'s field `marginal_ir_per_call` **collides with the gate record's
key of the same name, which is whole-program.** Both files say so.

---

## 3. E4 — `NOTES.md` §0's disclosure, repaired with the diff rather than a claim

`harness/tools/contract_diff.py p25` → **`UNCHANGED`** (block sha256
`c41099be4dfdc646…` in `HEAD` and in the tree). The per-step key diff, from
`.temp/t159/contract_steps.py` over the four texts `TASK_157` saved (all four
re-hash **exactly** to their claimed digests):

```
step 1  /idiom/why                                                   +521 chars
step 2  /collapse/note -10 · /identity[0]/why -10 · /idiom/why -85
        /miri/reason -10 · /verus/obligations_note -5
        /verus/twin_obligations_note -5              == exactly 25 escapes
step 3  /idiom/why                                                  +9568 chars
        after_shared_para -> SHIPPED   parsed objects IDENTICAL
```

*"No entry moved"* was false — `identity`, `collapse` and `miri` **did** move at
step 2. **No pin VALUE moved**, and §0 now prints the diff so a reader does not
have to trust the conclusion.

---

## 4. E5 — the rest of `TASK_158` §13, plus two minors it did not list

| §13 | landed |
|---|---|
| 1 `synthesize.py` null rule + derived §5 prose | ✅ §1 above |
| 2 `check.py::check_marginal_ir` docstring | **REPORT ONLY** — §6 |
| 3 `CAVEATS['p25']` ×3 | manager's, **already fixed** — re-read and confirmed, all three corrections present, and `composition.py` carries **no** *"half"* / *"both compilers"* / *"dominates"* claim |
| 4 README Headline 2, `NOTES.md` §3c | ✅ both rewritten |
| 5 `NOTES.md` §3c convention | ✅ *"kernel-exclusive"*, with the key collision named |
| 6 `NOTES.md` §0 | ✅ §3 above |
| 7 `NOTES.md` §8a — six routines, quote to the instruction | ✅ the closed six-symbol decomposition, and *"about +269"* replaces *"+269.52"* with the `5648.91` vs `5648.27` drift disclosed |
| 8 `NOTES.md` §8b — `norel` cross-reference | ✅ with `md5_raw_equal: false` and the counts `[189,189,751]` / `[313,313,1791]` |
| 9 `.memory/06-catalogue.md`, 10 `RECAP.md` | manager's |

**Two more, from §5 and §8.2, both row-level:**

* **minor 4** — `NOTES.md` §3b said the DR-400 problem is *"the surviving `*cur`"*.
  Widened: **`curbase == toks` is itself a read of an indeterminate pointer
  value, on every path including the false one.** That broader reading is what
  licenses the row's conclusion and is exactly why the `fixup` arm is unclean
  and `fixup2` is.
* **minor 5** — the citation. `NOTES.md` §3b now records that **WG14 DR 400 is
  titled *"realloc with size zero problems"*** and the load-bearing text is
  **C11 6.2.4p2 + 7.22.3.5p4**, with **DR 260**. ⚠ **The shorthand *DR 400* was
  deliberately left in `spec.md`'s hashed `why`, `c/kernel.c`,
  `README.md` and `controls/rederive.py`** — the first costs a `contract_sha256`
  move and the second costs a **re-measure**, and a citation shorthand is not
  worth either. Disclosed rather than half-landed.
* **minor 11** — `controls/detectors.json` committed `"stdout": "ctl_asan 85"`
  for a use-after-free that reads recycled heap. **Fixed, and re-confirmed by a
  third distinct draw**: the record said `85`, the reviewer measured `85` then
  `86` at `-O1` and `98` then `99` at `-O3`, and **this run printed `ctl_asan
  87`**. The record now carries
  `<non-reproducible: with ASan absent this control reads recycled heap …>`.
  `detectors.py` re-run: `rc=0`, `problems: []`, both controls still fire only
  in their own detector.

---

## 5. A SECOND typed-under-a-computed-number falsehood, in the SAME file

⚠⚠ **Found while regenerating, not looked for, and no review has caught it.**
`results/synthesis.md` §2 has published, at `HEAD` and for many tasks:

> *"**179 hit, 17 false `LICENSED`, **2 false alarm**, 10 abstain**. The
> smallest movement under a `NOT-LIC` verdict is **0.00 `Ir`/call**, so ***0
> false alarms*** is robust to any tolerance below that …"*
> *"… **the false-alarm zero survived**; the hit count did not … ***`0 false
> alarms` is the part that holds across both of them.***"*

**The generated figure says `2` and the typed sentence beside it says `0`, three
times, in the paragraph immediately below the number that contradicts it.** And
the *reason* given is self-refuting: `smallest_NOT-LIC_move` is **`0.00`**, which
is not a margin — **it IS the false alarms**. This is exactly §5 claim 1's defect
(`TASK_158` M4), in the same generator, **400 lines earlier**.

✅ **Repaired the same way**: both paragraphs are derived, `calibrate_licence`
now returns the offending rows by name, and the file prints them —
**`p42 small R3-R4`, `p42 large R3-R4`**. ⚠ **Nothing published is wrong because
of it**: a `NOT-LIC` on a row the sweep says does not move is the *safe*
direction — the rule refused to license a difference that would have been fine.
What was wrong is the file saying there were none. The three historical triples
(`156/10/0/10`, `154/12/0/10`, `152/14/0/10`) are now labelled as history.

---

## 6. Gate, records and the closing checks — ALL GREEN

**`harness/check.py p25`**, read out of `results/gate/p25-realloc-growth.json`,
never grepped from the log:

```
verdict          PASS
failures         []      blocked  []      loud  []
contract_sha256  c41099be4dfdc6464941b3e60ea6b3e0067b8156735c4748b1ecdf5b6d00fddd
                 == HEAD's.  spec.md was NOT touched, inside or outside the fence.
published_table  FRESH   table_render  FRESH
```

**One gate run, no re-measure.** `git status --porcelain`:

```
 M patterns/p25-realloc-growth/NOTES.md
 M patterns/p25-realloc-growth/README.md
 M patterns/p25-realloc-growth/controls/detectors.json
 M patterns/p25-realloc-growth/controls/detectors.py
 M patterns/p25-realloc-growth/controls/rederive.json
 M patterns/p25-realloc-growth/controls/rederive.py
 M results/gate/p25-realloc-growth.json
 M results/synthesis.md
 M synthesis/licence.json
 M synthesis/synthesize.py
?? .tasks/TASK_159_REPORT.md
```

⚠ **No `spec.md`, no `c/*`, no `*.rs`, no `model.py`, no `inputs/gen.py`, and
`results/p25-realloc-growth.json` is byte-identical to `HEAD`.** Everything I
touched is in the gate glob only.

| check | result |
|---|---|
| gate `source_sha256` | **53 entries, 0 stale, 0 missing** |
| measurement `source_sha256` | **18 entries, 0 stale, 0 missing** |
| nine `controls/*.json` `derived_from_sha256` | **0 stale, 0 missing**, every `problems` empty |
| `harness/measure.py --check-stale` | `rc=0` — **`64 record(s) examined, 0 STALE`** (32 gate + 32 measurement, as the task file says) |
| `harness/tools/composition.py --check` | `rc=0` — `OK: published composition table matches the tree (32 patterns, 10 classes)` |
| `harness/tools/temp_citations.py` | `rc=0` — `OK (new=0 unclassified=0 resolved=0)`; 109 citations, 78 distinct paths |
| `synthesis/licence.py --emit synthesis/licence.json` | `rc=0` — **`32 patterns, 128 pair verdicts`**; p25 goes from *"no licence recorded"* to a real verdict |
| `synthesis/synthesize.py` | `rc=0` — `results/synthesis.md`, 92 041 bytes |
| **E2 — `results/synthesis.md` carries `p25`** | ✅ **21 occurrences** (was **0**) |
| **E2 — PROTOCOL rule 1, ANCHORED (headers, not mentions)** | ✅ prints **`MISSING: p01` only** — the known benign exception. **`p25` is no longer missing**: `RECAP.md` finding 60's header names it. |
| PROTOCOL rule 10 (report files cited exist) | only the three `TASK_NNN*` placeholders, which the rule says to ignore |

⚠ `rc` was read from the process every time, never after a pipe.

---

## 7. NOT DONE — reported, not fixed

1. **`check.py::check_marginal_ir`'s docstring owes a paragraph** (§13 item 2).
   ⚠ **Use the corrected numbers**: the `R5 − R4` null on `-O3 isolated` reaches
   **`+269.52` (p25)** and **`−31.00` (p42)**; **`p28`'s `+1732.73` and `p29`'s
   `+425.80` are `-O0 isolated` and must not be quoted into an `-O3` sentence.**
   In `whole` mode the pair is not a null at all (`check_identity` compares
   `isolated` digests, `check.py:3303`). A `harness/` edit is a 32-pattern
   re-gate.
2. **`global layout` is a sixth body-less form `vparse.axiom_decls` cannot see**,
   live on four patterns. `check.py`. Carried forward unchanged.
3. **Stage 9b hashes a control sidecar and never reads its own verdict**, and its
   sidecar deadline is distinct from `measure.py`'s. Same bundle.
4. **`results/SYNTHESIS.md` (CAPITALS) does not mention `p25`.** Hand-written,
   manager's file — reported, not touched.
5. **The DR 400 shorthand survives in four places** (§4 above) for budget
   reasons, all disclosed in `NOTES.md` §3b.
6. **`synthesis/outward_ir.json` is STALE against 26 patterns**, so §2's
   calibration is scored partly on rows taken against moved sources. Pre-existing,
   the file says so on every run, and re-emitting is 352 callgrind runs.
7. **The `‡` phase sweep was not re-taken.** `p03`/`p04`'s `±6.00` nulls are one
   draw of a bistable term; the null rule uses the drawn value, which is the
   conservative direction (a larger null refuses more).

---

## 8. Clean negatives — named attacks that did NOT land

1. **Is `TASK_158`'s repair-cost table reproducible?** Yes — all 32 dynamic and
   20 static cells reproduce **to the hundredth** from a different script, in a
   different session, inside the pattern's own committed control.
2. **Do the three affected published numbers change under the `-O0`/`-O3`
   correction?** No. They are `-O3 isolated` rows scored against `-O3 isolated`
   nulls; p28's and p29's `-O0` figures never touched them.
3. **Are there affected rows outside `gcc-clang`?** No — **zero** in `R2-R4`,
   **zero** in `R3-R4`, over all 128 (pair, pattern, blob) rows.
4. **Does the null rule fire on rows it should not?** No. `p42 small gcc-clang
   +5.00` survives untouched because p42's null is blob-specific and `small`'s
   is under the floor; the same pattern's `large` row is refused. The rule
   discriminates within a pattern.
5. **Does `spec.md` carry the falsified cost claim?** No — grepped the whole
   pattern: the hashed `why` never states a ratio, so `contract_sha256` did not
   have to move. `harness/tools/composition.py`'s `CAVEATS['p25']` does not
   either.
6. **Were the three manager corrections in `CAVEATS['p25']` really landed?**
   Yes — re-read all three (inverted attribution, *"one of six growths"*,
   `min + 31*b`); all present, none re-landed by me.
7. **Is the `+269.52` an environment phase?** Not re-run — `TASK_158` settled it
   at pads 0 and 16 and the two-pad screen is a complete detector for a
   16-wide window. Cited, not repeated.
8. **Do the `TERN`/`PTR` respelling negatives need re-running?** No — the task
   file said so and I did not.
9. **Did any control sidecar go stale under me?** No — checked before the gate
   and again after; `rederive.json` and `detectors.json` were regenerated
   **after** their generators' last edit, which is stage 9b's separate deadline.

---

**PROTOCOL rule 2 running count.** Launched from **906**. This task refuted
**three manager/artefact claims** (the null table's `-O3` label with two `-O0`
rows in it; *"real exposure is four patterns"*; *"eight of that top ten read
−1.00"*), **one reviewer claim** (the `-O3` range is `1.59×…7.54×`, not
*"1.6× to 7.1×"* — `clang large` is the maximum, not `clang small`), and found
**one further published falsehood nobody had looked for** (`results/synthesis.md`
§2's *"0 false alarms"* printed beside its own computed `2`). My own must-fire
arm additionally refuted **one of my own** written arms before it could publish.
**906 + 5 = 911.** ⚠ Reconciliation across branches is the manager's job, not
mine.
