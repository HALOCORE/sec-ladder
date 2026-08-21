# TASK_058 — audit of the documentation layer against the records

**Reviewer, read-only. Nothing was executed**: no `check.py`, `measure.py`,
`build.py`, `verus_run.py`, no compiler, no valgrind, no Miri, no cargo, no
binary under `.temp/`. Every number below comes from `grep`/`sed`/`python3 -c`
over JSON and markdown, or from read-only `git show`.

Tree state while auditing: `.memory/06-catalogue.md` and `RECAP.md` were being
committed by another agent during the audit (`RECAP.md` grew 1533 → 1544 lines
mid-pass), and `patterns/p10-fir-stencil/` appeared untracked. **Line numbers
below were re-verified at `9dce856`; every finding also quotes the string, so
grep for the string if a line has moved.**

Severity: `blocker` = a published number is wrong · `major` = two authoritative
files disagree, or a citation lands somewhere false · `minor` = a stale constant
with no consumer.

---

## B1 — `blocker` — p13's shipped proof is published as **17/0 (twin 20/0)**; the records say **19/0 (twin 22/0)**

| side | says |
|---|---|
| `.memory/01-ladder.md:1795` | "Sound and unchanged: Verus **17/0 first attempt** (twin 20/0), `R4 ≡ R5 exact`, TCB 5 matching the gate's own count" |
| `RECAP.md:951` | "Sound: Verus **17/0 first attempt**, `R4 ≡ R5 exact`, TCB 5 = the gate's own count" |
| `results/gate/p13-strncpy-trunc.json` | `verus.verus.rs.verified = 19`, `pinned = 19`; `verified_twins.verus.rs` = **22 / 0** |
| `patterns/p13-strncpy-trunc/spec.md:347-348` | `` `verus.obligations` = 19 ``, `` `twin_obligations` = 22 `` |
| `patterns/p13-strncpy-trunc/NOTES.md:707-709` | "→ **`19 verified, 0 errors`**, first attempt (both before and after the fold repair). `--cfg slb_twin` → **`22 verified, 0 errors`**" |

**The records support 19/0 and twin 22/0.** Provenance, from read-only git:
`git show 752a9ca:results/gate/p13-strncpy-trunc.json` (TASK_043, delivery)
reads `{'verus.rs': (17, 0)}` / twin `(20, 0)`, and `752a9ca:.../spec.md:343-344`
pins `17` / `20`. TASK_046 (`0856e52`) took it to 19 / 22 (`fold_dst` added,
`kernel` 6 → 7). **Both stale sites sit inside the paragraph that describes
TASK_046** — `.memory/01-ladder.md`'s p13 finding and RECAP's finding 25 — so
the correction moved the pattern and not the write-up. The `TCB 5` half of both
sentences is correct.

`.memory/` is the authoritative layer, so this is the more severe of the two
copies.

## B2 — `blocker` — `.memory/01-ladder.md` gives p13's bulk-R4 control two different obligation counts, 16 lines apart

- `.memory/01-ladder.md:314-315`: "`copy_nonoverlapping` and `write_bytes`
  verify at the pinned vstd (**15/0, twin 22/0**, `identity: exact` holding)"
- `.memory/01-ladder.md:299` (same file, the scoped-entry table): "the bulk
  spelling verifies (**17/0, twin 24/0**); the prover never excluded it"
- `patterns/p13-strncpy-trunc/NOTES.md:1124`: `u1_bulk_copyfill` …
  "`copy_nonoverlapping` + `write_bytes`; **17 verified / 0 errors, twin 24/0**,
  `identity: exact` holds; **TCB 5 → 7**"
- `RECAP.md:913`: "**17/0, twin 24/0**"

**The records support 17/0, twin 24/0.** `15/0, twin 18/0` is p12's route-A R4
(`.memory/01-ladder.md:1572`), so `:315` looks like a cross-pattern carry.

## M3 — `major` — `RECAP.md:28` quotes the exact TCB figure `.memory/04-verus.md` says must not be quoted, and attributes it to the wrong denominator

- `RECAP.md:28-29` (**the START HERE box**): "**The TCB column is not gameable —
  retrospectively.** 3.4% exposure across the **16 patterns that exist**."
- `.memory/04-verus.md:216-217`: "Census at TASK_048, **14 patterns**: 57 items
  / 118 lines"
- `.memory/04-verus.md:237`: "Measured exposure was **2 of 58 items (3.4%)** —
  p06's `scr_load` (removed, TCB 6 → 5) and p08's `copy_in`."
- `.memory/04-verus.md:241-246`: "⚠ **BOTH named exposures are now CLOSED, so
  the measured exposure is `0`, and the denominator moved too.** … **Recount
  rather than quoting `58` or `3.4%`**"

`.memory/` is authoritative and supersedes RECAP: the figure is `0` of a
recounted denominator, the census was 14 patterns not 16, and `3.4%` is the
literal string the authoritative file forbids. Confirmed from the records that
both exposures are closed: `results/gate/p06-rotate.json` `tcb_items` = 5 (no
`scr_load`), `results/gate/p08-overlap-move.json` `tcb_items` = 3 (no `copy_in`).

## M4 — `major` — the rule that exists to settle the two `Ir` conventions names the wrong one for the tables (and TASK_058's own premise inherits it)

`.memory/03-measurement.md:498-500`:

> **`results/tables/*.md` and every published price read `marginal_ir_per_call`.**
> A number taken with `callgrind_ir` is a *different measurement* …

Every one of the 16 `results/tables/*.md` says the opposite about itself
(e.g. `results/tables/p04-ring-buffer.md:78`, `p08-overlap-move.md:61`,
`p13-strncpy-trunc.md:101`, `p16-tlv-walk.md:58`):

> `Ir` is **callgrind per-function exclusive** for the kernel symbol. The
> whole-program total is deliberately absent …

`marginal_ir_per_call` appears in each table exactly 3 times, and only as the
*cross-check* ("rung-to-rung ratios of this column are directly comparable
with … `marginal_ir_per_call` in `results/gate/<pattern>.json`").

And "every published price" is false too. Recomputed from
`results/p04-ring-buffer.json` (`kernel_exclusive_ir / calls`, calls 6000 /
1500):

```
safe_tuned  3368.0 / 11667.0     <- p04/README.md:151 and NOTES.md:506 publish exactly this
unsafe      3363.0 / 11662.0
gate marginal_ir_per_call: safe_tuned 3425.0 / 11724.0, unsafe 3420.0 / 11719.0
```

p04's published **levels** are kernel-exclusive (+57 away from the marginal);
p13's `NOTES`/`.memory/03-measurement.md` "1769 on the kernel column" is
kernel-exclusive too. **No published delta moves** — p04's `+5.00` is identical
in both conventions — which is why this is `major` and not `blocker`, but the
sentence is the one a future agent will use to decide which column to publish,
and it is wrong about the artefact it names.

The task file's own premise ("`marginal_ir_per_call`, which is what the
published tables read") comes from this sentence and is wrong for the same
reason. The two citations the task file gives — `.memory/03-measurement.md:479`
and `:508` — both land correctly.

## M5 — `major` — `.memory/04-verus.md`'s prescribed TCB recount undercounts by 3

`.memory/04-verus.md:248-264` gives a recount command and records "At the time
this correction was written that prints **62 items across 16 patterns**."

Run as written it does print **62**. The true totals are **65 `tcb_items`
across all verified files, 134 body lines** (63 items / 129 lines counting
`verus.rs` only). The command's `find()` returns the **first** `tcb_items` it
meets and stops; `results/gate/p01-array-sum.json`'s `verus` dict is
`['safe_naive_verus.rs', 'verus.rs']`, so p01 contributes its R2v count (2) and
its `verus.rs` items — `get_unchecked`, `load_input`, `emit` — are silently
dropped. p01 is the only pattern with two verified files, so the bug is
invisible on 15 of 16.

This is the "print the count rather than trust a constant" rule failing in the
authoritative file, three lines under the sentence that invokes it. Correct
one-liner (drop the short-circuit):

```bash
python3 -c "
import json,glob
n=sum(len(t) for f in glob.glob('results/gate/*.json')
      for v in json.load(open(f))['verus'].values() for t in [v['tcb_items']])
print(n,'items')"        # 65
```

## M6 — `major` — `RECAP.md` contradicts itself on the sole-catcher sweep

- `RECAP.md:1016-1018`: "⚠ **\"The twin is the sole catcher\" was false on SIX
  patterns**, not two — … p06's and p12's are fixed; **p03, p04, p05, p11 and
  p18 are not.**"
- `RECAP.md:1341`: "p12's, p03's, p04's, p05's, p11's and p18's sole-catcher
  prose **is corrected**"

The patterns settle it — all five allegedly-unfixed ones carry the correction,
each naming TASK_054/TASK_056:

```
patterns/p03-bounded-stack/NOTES.md:822   (TASK_054, TASK_056): the twin is the sole catcher only of a mutant that edits…
patterns/p04-ring-buffer/NOTES.md:1092    …the twin is the sole catcher only of a mutant that edits…
patterns/p05-index-flatten/NOTES.md:920   The rule (TASK_054, TASK_056, six patterns)…
patterns/p11-nul-scan/NOTES.md:588,635-647  "…the twin is the sole VERUS-LEVEL catcher, and the pin catches it too"; "CORRECTED AT TASK_056"
patterns/p18-varint-shift/NOTES.md:1615   "here the twin is the sole **Verus-level** catcher and not the sole catcher."
```

**`RECAP.md:1341` is the side the records support; `:1016-1018` is stale.**

## M7 — `major` — the authoritative layer says p12's sole-catcher prose is "not yet fixed"; it is fixed

- `.memory/01-ladder.md:1889-1890`: "p12's `NOTES.md:1046-1049` is wrong the
  same way and is **not yet fixed**"
- `patterns/p12-strcat-fixed/NOTES.md:1047`: "### 9b. `p2_weak_write_requires`
  -- one character, and the twin is the sole ***Verus-level*** catcher"

Same defect class as M6 but one layer up: `.memory/` is described as
authoritative and supersedes task reports, so a reader trusts it over the
pattern. `RECAP.md:1341` already records the fix.

## M8 — `major` — `RECAP.md:155` publishes p01's R3 tax as `+8…+10`; the record and p01's own NOTES say `+4…+5`

- `RECAP.md:154-156` (finding 3, the "safety is cheap" headline): "Tuned safe
  Rust is **+8…+10 instructions per call** versus unsafe on **p01/p02**"
- `patterns/p01-array-sum/NOTES.md:262`: "**R3 is the honest number for 'what
  safe Rust costs': +4 to +5 instructions**"
- `.memory/01-ladder.md:500` (finding 3's p01 table, by residue): R3 = **+5 /
  +4 / +4 / +4**
- `results/gate/p01-array-sum.json` `marginal_ir_per_call`, O3/isolated:
  `safe_tuned 918.3 / 7205.3` vs `unsafe 914.3 / 7200.3` → **+4.00 small,
  +5.00 large**

p02's half is right (`+10.00 / +10.00`, checked). The joint range over the two
patterns RECAP names is **+4…+10**. The `+5 (gcc) / +12 (clang)` hardened-C
figures in the very next sentence reproduce exactly from p02's gate marginals,
so only the Rust half is wrong. (Its "3.7× on p01" is `.memory/01-ladder.md:443`'s
*pilot* figure; on p01 the R2/R3 ratio runs 2.75×…5.8×. Flagging, not counting —
it is a ratio of a range.)

## M9 — `major` — C5: the "finding N" collision is live, and it lands wrong in the authoritative file

`.memory/01-ladder.md:364-368` states the rule for its own text:

> ⚠ **AND THE COLLISION IS LIVE … "finding 14" is p13 **here** and *"every rung
> is a spelling"* in `RECAP.md`.** … The same trap sits at "13" (here = p04,
> there = p08) and at "12" (here = p12, there = p05).

Citations that violate it, i.e. that resolve to the wrong finding:

| site | text | resolves in-file to | intended |
|---|---|---|---|
| `.memory/05-layout.md:252` | "the pin was at line 69 and the hashed block started at line 309. See **`.memory/01-ladder.md` finding 14**." | ladder 14 = **p13 `strncpy`** | RECAP 14 / ladder **finding 3** (`:486-492`), which carries p05's `spec.md:69-73` mechanism |
| `.memory/01-ladder.md:312` | "the R4-is-chained-to-the-prover mechanism (**finding 14**)" | p13 | RECAP 14 |
| `.memory/01-ladder.md:488` | "A published spread cannot carry a safety claim at all — see **finding 14**" | p13 | RECAP 14 |
| `.memory/01-ladder.md:964` | "emphatically **not** \"safe beats unsafe\" (**finding 14**)" | p13 | RECAP 14 |
| `.memory/01-ladder.md:1128` | "that is the step **finding 14** shows is not available" | p13 | RECAP 14 |
| `.memory/01-ladder.md:1836` | "**Finding 6** — `Ir` and wall clock disagreeing in direction — now has a designed instance" | ladder 6 = **p05** | RECAP 6; the ladder's own copy of that fact is in **finding 3** (`:568-572`) |
| `.memory/01-ladder.md:191` | "`min(R3) − min(R4)` differences two upper bounds and bounds nothing (**finding 12**)" | ladder 12 = **p12** | ladder **finding 6** (`:1155`) / RECAP 12 |
| `.memory/02-bench-rules.md:676` | "the R4 side is chained to the prover (**finding 14**)" | ambiguous, unqualified | RECAP 14 |
| `.memory/06-catalogue.md:29` | "produced **finding 14**" (T015 row) | ambiguous, unqualified | RECAP 14 |

`.memory/05-layout.md:252` is the worst of these: it **names the file**, so a
reader does not get to guess, and it lands on `strncpy` truncation when the
subject is p05's forbidden `chunks_exact`. The five inside `.memory/01-ladder.md`
are the file contradicting its own warning; note that the same file uses
"finding 6" *correctly* (= p05) at `:1305` and `:1406`, so the two schemes are in
use simultaneously ~500 lines apart.

**What is CLEAN here** (do not re-run these): RECAP's map table at `RECAP.md:117-133`
is correct **row by row** — ladder headings are at `:371/413/417` (p01+p02 → 1–3),
`574` p16=4, `867` p17=5, `996` p05=6, `1222` p08=7, `1271` p07=8, `1342` p11=9,
`1392` p03=10, `1466` p09=11, `1540` p12=12, `1590` p04=13, `1711` p13=14,
`1823` p06=15, `1906` p14=16, `1958` p18=17, and RECAP's own list runs 1–28 with
p16=9, p17=10, p05=12, p08=13, p07=15, p11=17, p03=18, p09=19, p12=21, p04=23,
p13=25, p06=26, p14=27, p18=28 and cross-cutting 14/16/20/22/24 exactly as
stated. Every **"finding 16"** citation in the tree names its file explicitly
(`common/layout/README.md:11,86`, `harness/check.py:4983` → RECAP 16;
`patterns/p18-varint-shift/{NOTES.md:457,README.md:123,inputs/gen.py:465}` →
`.memory/01-ladder.md` finding 16 = p14 ✓). RECAP's three
"Authoritative: `.memory/01-ladder.md` finding N" pointers (p06→15, p14→16,
p18→17) are all correct.

## M10 — `major` — C3: ten `file:line` citations no longer land where the citing sentence says

Verified one by one against the current sources.

| citation | what the sentence claims is there | what is actually at that line | real target |
|---|---|---|---|
| `.memory/02-bench-rules.md:595` → `check.py:3819` | "rewrites `n_iters` to `MIRI_PROBE_ITERS = 4`" | `spec.md`'s `contract.{kw}` vs `verus.rs` comparison | `check.py:311` (the constant), `:4769` (the use) |
| `.memory/05-layout.md:215` → `check.py:1446` | "requires *every* `.rs` … containing a `verus!` block to be pinned in `verus.obligations`" | the `--no-callgrind` collapse-ir bail-out | `check.py:2197`, `:2215` |
| `.memory/05-layout.md:215` → `check.py:1549` | "fails the gate for any pinned file reporting `n_err > 0`" | the `MIN_DECLARABLE_IR_PER_WORK` clamp message | `check.py:2323-2324` |
| `.memory/06-catalogue.md:201` → `check.py:566` | "admits only `clean`/`fires`" | the `spelling_matches` selftest | `check.py:1247-1249` |
| `.memory/03-measurement.md:788` → `check.py:1249` | "cell-agreement requirement rejects outright" | `f"'clean' or 'fires'")` — **the line the row above wanted** | elsewhere |
| `.memory/05-layout.md:311` → `check.py:459-460`, `measure.py:60` | "hardcoded in **two module-level literals**" | `run_bin`'s `subprocess.run` / a `CG_PLAN` row | `check.py` has **no** module-level literal — it is an inline `f.startswith("sweep-")` at `:474`; `measure.py`'s is `SKIP_INPUT_PREFIX` at `:64` |
| `.memory/02-bench-rules.md:109` → `check.py:469` | "drop `sweep-*` entirely" | `d = os.path.join(pdir, "inputs")` | `:474` (`measure.py:64` in the same sentence is **exact**) |
| `.memory/01-ladder.md:277` → p13 `spec.md:374`, `:394` | "pin the byte-loop copy and fill … exempting `safe_tuned.rs` by name" | the `strncpy`-`n` cap entry / the fixed-size-local entry | `:378` (fill) and `:398` (copy) — **and both now read "Until TASK_046 it pinned … It was relaxed symmetrically"**, so the present-tense "pin" is wrong as well as the line |
| `.memory/06-catalogue.md:159` → p16 `spec.md:269`, `:278` | required[0] "in every rung" / `split_first_chunk::<3>()` asserted admissible | prose about obligation arithmetic / the `miri.required` pin row | `:289` and `:60` |
| `RECAP.md:1474` → `harness/check.py:1753` | "display string still says 'recorded as a result'" | a comment block | `check.py:1766` (`head("3c. structural identity R4-vs-R5 (recorded as a result AND enforced)")`) |

**CLEAN citations, checked and correct** — do not re-run: `.memory/01-ladder.md:101`
(p16 `verus.rs:275` really is `p + 3 + vlen <= end`, its own `forbidden[0]` as a
ghost invariant), `.memory/01-ladder.md:2065` (p01 `NOTES.md:697` = "`panic=abort`
and `O0d` … built but not measured"), `.memory/03-measurement.md:469`
(p08 `NOTES.md:192` = the five re-measured 7292.1x points),
`.memory/02-bench-rules.md:35` (`measure.py:56-61` = `CG_PLAN`, exact),
`.memory/02-bench-rules.md:935` and `RECAP.md:713` (`check.py:929` really is
`_TICK.findall`), `.memory/06-catalogue.md:446,449` (`.memory/03-measurement.md:411`
`rep`-strings, `:434` `div` at 1 `Ir`, `:551` name-the-routine), and the task
file's own `.memory/03-measurement.md:479` / `:508`.

## M11 — `major` — p08's §6b mutant table is pre-TASK_056 and, unlike its neighbours, is not flagged

- `patterns/p08-overlap-move/NOTES.md:869`: `| control | — | `11 verified, 0 errors` | — |`
- `results/gate/p08-overlap-move.json` `clause_deletion.verus.rs.control_verified` = **12** (its mutants read 11/1)
- `patterns/p08-overlap-move/NOTES.md:768-770`, 100 lines above: "**`12 verified,
  0 errors`** … `--cfg slb_twin` → **`16 verified, 0 errors`**. ⚠ **Both counts
  were one lower (11 / 15) until TASK_056**"

§6c *does* flag its transcript ("the transcript quoted above says *\"4 TCB
items\"* and *\"11 verified\"* … they are 3 and 12 now"); §6b's table does not,
and its `control` row is directly contradicted by the gate record.

The same pre-TASK_056 base is republished, unflagged, in three more places:
`patterns/p08-overlap-move/README.md:37` ("**`11 verified, 0 errors`** shipped
and **`15 verified, 0 errors`** under `--cfg slb_twin`"), `RECAP.md:292`
("verifies 11/0 and 15/0 under the twin"), `.memory/01-ladder.md:1251`
("verifies `11/0` shipped and `15/0` under the twin").

⚠ **`needs-measurement` for the exact replacements** — those are mutant runs and
need `./verus_run.py`, which this task may not do. What *is* established from the
records is that the shipped base they are quoted against moved 11 → 12 and
15 → 16 at TASK_056, so as written they no longer describe the tree.

## m12 — `minor` — RECAP's own stage-enumeration command prints 19; there are 18 stages

`RECAP.md:1512-1513`: "`check.py` (**18** stages; this line said 17 and
`.memory/05-layout.md` said 16 — enumerate them with
`grep -on 'head(\"[0-9]' harness/check.py`, **do not copy a constant**)".

```
$ grep -on 'head("[0-9]' harness/check.py | wc -l
19
```

The constant **18 is right**; the command is wrong. `head("1. build the matrix`
appears twice — `check.py:1218` and `check.py:4903` — so the distinct stages are
0, 0b, 1, 2, 3a, 3b, 3c, 4, 5a, 5b, 5c, 5c-req, 5c-twin, 5d0, 5d, 6, 7, 8 = **18**.
The next agent who obeys the "print the count" instruction will "correct" a
correct constant. A command that does not over-count:

```bash
grep -o 'head("[0-9][^.]*\.' harness/check.py | sort -u | wc -l   # 18
```

## m13 — `minor` — `.memory/04-verus.md`'s vstd citations are right, but `CLAUDE.md` points readers at a *different* vstd where they are wrong

All of them land against the **pinned** vstd
(`/home/apt/tools/verus-0.2026.08.09.92f466f/vstd/`): `std_specs/slice.rs:205`
= `copy_from_slice` ✓, `:185` = `split_at_mut` ✓, `:235` = `copy_within` ✓,
`array.rs:175` = `ref_mut_array_unsizing_coercion` ✓, `std_specs/slice.rs:14`
= `SliceIndexSpecImpl for usize` ✓, `:31` = `for Range<usize>` ✓
(`.memory/04-verus.md:976` writes `:14,30`, one line off).

But `CLAUDE.md:37` sends readers to `../LearnVeri/_VERUS_DOC_/` for "full vstd
source", and that copy is a **different snapshot**: `std_specs/slice.rs` is 215
lines against the pinned 253, contains **no `copy_from_slice` and no
`copy_within` at all**, and its line 205 is `split_at_mut`. Anyone who checks
`.memory/04-verus.md:139-143` there will conclude the memory file is wrong.
(`array.rs:175` there is `spec_array_update`; the real coercion is at `:195`.)

## m14 — `minor` — "six patterns" with no `source_sha256` is five

`RECAP.md:1434` (Priority item 6): "`results/*.json` has no `source_sha256` for **six
patterns**". The files without it are `p02`, `p05`, `p07`, `p11`, `p17` — five
patterns — plus `p02-residue-sweep.json`, which is a side record and not a
pattern (`.memory/02-bench-rules.md` and `measure.py:316` both say so).

---

## Checked and CLEAN — do not re-run these

**Proof records (C1).** Every per-pattern `tcb_items` claim in every
`NOTES.md`/`README.md` equals `results/gate/*.json`, body lines included:
p01 3 (+ R2v 2, 6/5 lines), p02 4/10, p03 5/10, p04 5/10, p05 3/6, p06 5/10
(and its "6 → 5"), p07 3/6, p08 3/9 (and its "4 → 3"), p09 4/7, p11 3/6,
p12 5/10, p13 5, p14 6/11, p16 3/6, p17 3/6, p18 3/6.

Every `verus.obligations` / `twin_obligations` pin in every `spec.md` equals the
gate's `verified` / twin `verified`, and every gate record has `errors = 0` and
`verified == pinned`: p01 7 & 7 / 8, p02 9/12, p03 9/12, p04 9/12, p05 12/13,
p06 18/23, p07 10/11, p08 12/16, p09 18/21, p11 12/13, p12 15/18, p13 19/22,
p14 19/23, p16 10/11, p17 10/11, p18 12/13. (**B1 is the only place a shipped
obligation count is misquoted, and it is misquoted only in the prose layer.**)

All 16 patterns pin and meet `identity: unsafe ≡ verus, O3 exact`. p08's `-O0`
row reads `exact` against an `expected` of `norel` — that is *stronger* than the
pin and is already disclosed at `.memory/04-verus.md:243-245`.

**Headline deltas (C1), recomputed from `marginal_ir_per_call`, O3/isolated:**
p02 `R3−R4 = +10.00 / +10.00` and `R1h−R1 = +5 gcc / +12 clang`;
p05 `123 / 399`; p16 `+27 / +77`; p17 `+32 / +32`; p12 `+3.00 / −26.00`;
p13 `−177 / −1054`; p04 `+5.00 / +5.00`; p08 `R1h−R1 = 0.00 / 0.00`;
p06 `R1h−R1 clang = −45.00 / −108.00` (the sign-wrong headline);
p09 `safe_tuned large = 73404.3` (the out-of-sample prediction's target).
p03's two laws are **exact against the records**: `results/p03-bounded-stack.json`
gives `win0_xpops = 118 / 207`, and `R1h−R1 = 236 / 414 = 2·xpop`,
`R3−R4 = 359 / 626 = 3·xpop + 5`.

**The 13× two-convention trap (C1).** p13's `.memory/03-measurement.md` figures
both reproduce: kernel-exclusive per call gives `c-gcc 5048.0 − c-clang 3279.0 =
**1769**` and the marginal gives `5270.28 − 3807.28 = **1463.00**`; `R2 − R4` on
the marginal is `1008/3939.7 = **25.59%**` and `2697/10819.3 = **24.93%**`. p04's
`3368 / 11667` is kernel-exclusive and exact, and its `+5.00` is identical in
both conventions. **No figure I checked is wrong in the convention it claims** —
M4 is about the *rule*, not about a number.

**Counts (C4).** 47 catalogue rows ✓; `forbidden_hits` = **0 of 132** across the
16 gate records, matching `.memory/02-bench-rules.md:138` ✓; sanitizer rows
**114 / 114** carry `stdout`, matching `RECAP.md:1336` ✓; verdicts are p01
`PASS-WITH-BLOCKED-ROWS` and the other fifteen `PASS`, matching `RECAP.md:1503-1505` ✓;
`.memory/04-verus.md:199-200`'s vstd census reproduces exactly — **402**
`assume_specification` and **272** `external_body` in the pinned vstd ✓.

**The named-spelling invariant (C4).** RECAP's own command returns a set of size
**1**, value **`59748cce2db5`**, exactly as `RECAP.md:1507` states.

**PROTOCOL rule 10 (dangling reports).** Ran over `.memory/ .tasks/ RECAP.md
CLAUDE.md PLAN.md TOOLCHAIN.md patterns/ common/ harness/`. Only
`.tasks/TASK_055_REVIEW_REPORT.md` shows, and its sole "citation" is the
*instruction* inside `.tasks/TASK_055_REVIEW.md:149` for a task that has not run.
Not a defect. (The two `TASK_NNN` placeholders are the documented false
positives.)

**p06's floor correction (C2/C6)** is consistent everywhere it appears:
`RECAP.md:27`, `:1020`, `.memory/01-ladder.md:1899-1904`,
`.memory/03-measurement.md:841-843`, `.memory/06-catalogue.md:423`, and
`patterns/p06-rotate/NOTES.md:351-362`, which itself names the two surviving
"±3%" sentences and says why they still hold. This is the model the M6/M7 sites
failed to follow.

**p05's declaration arithmetic (C2)** is consistent: `spec.md:69-73` prose pin
vs the hashed block at line 309 = RECAP finding 14's "starts 240 lines later" =
`.memory/06-catalogue.md:82`'s "line 69 … 309".

**Toolchain (C2).** `RECAP.md:1525`'s pins agree with the generated tables and
the tree: Verus `0.2026.08.09.92f466f` (directory exists), rustc 1.97.1,
clang/LLVM 22.1.6, valgrind 3.27.1.

---

## Attacks that did NOT land (clean negatives, PROTOCOL rule 6)

- **"RECAP's numbering map is wrong."** It is not. Fifteen rows, all correct,
  verified against the ladder's actual heading line numbers. The map is the one
  guard in this area that has *not* drifted.
- **"The `Ir` figures are quoted in the wrong convention."** They are not. Every
  headline delta I could recompute reproduces in the convention its source
  claims, including the p13 pair (1769 kernel / 1463 total) that exists
  specifically to be got wrong, and p04's kernel-exclusive levels.
- **"`.memory/04-verus.md`'s vstd citations have rotted."** They have not, against
  the pinned vstd. (See m13 for the trap that makes them *look* rotten.)
- **"Some pattern's gate `verified`/`tcb_items` disagrees with its `spec.md`
  pin."** None does. 16/16 exact on both, and `errors = 0` everywhere.
- **"A `spec.md` obligation pin drifted after measurement."** Not detectable here
  and not claimed: every pin equals the gate, which is what the tree can show.

## Unsure / not done / `needs-measurement`

1. **M11's replacement numbers.** p08's mutant table (`11/0`, `14/1`, `10/1`
   rows), `README.md:37`'s `11/0` & `15/0`, `RECAP.md:292`,
   `.memory/01-ladder.md:1251` — the *new* values need `./verus_run.py` on
   mutants. I established only that the base moved +1 at TASK_056.
2. **`patterns/p08-overlap-move/spec.md:194`** quotes gate 5c as saying a
   deleted `ensures` "still gives 11 verified, 0 errors". The current
   `clause_deletion` control is 12 and its mutants read 11/1, so the quote may be
   accidentally right for the wrong reason. `needs-measurement`.
3. **I did not re-derive any wall-clock, layout-population, sweep-law or
   controls figure** — those live in `.temp/` or need a run. C1 was scoped to
   what `results/gate/*.json` and `results/*.json` can settle.
4. **`.memory/04-verus.md:200`'s "545 `broadcast` proof fns across 44 files"**
   reads 547 / 36 files under my grep predicate (`broadcast +proof +fn`), and
   "44" matches none of the three per-construct file counts (33 / 45 / 36). The
   counting predicate is unstated, so I am not calling it wrong; the two exact
   numbers beside it do reproduce.
5. **`RECAP.md:1311`'s "~5100 lines" for `check.py`** is 5262 today. It carries a
   "~" and is used only as a ratio argument, so I did not count it as a finding.
6. **`patterns/p10-fir-stencil/` is untracked and in flight** (TASK_057). RECAP's
   own prescribed count `ls -d patterns/p*/ | wc -l` (`RECAP.md:78`) now returns
   **17** against a 16-row table. That is the in-flight pattern, not drift — but
   the command does not distinguish, and RECAP offers it as the authority.
7. **`CLAUDE.md:27-30`'s `harness/` list omits `limbs.py`**, which
   `RECAP.md:1342` records as having moved into `harness/`. Cosmetic; listed for
   completeness only.

## Premise of the task file that is wrong

**"`marginal_ir_per_call`, which is what the published tables read"** — see M4.
The tables read callgrind kernel-exclusive and say so in their own header; the
premise is inherited from `.memory/03-measurement.md:498-500`, which is the
actual defect. The task file's two line citations (`:479`, `:508`) are correct.
