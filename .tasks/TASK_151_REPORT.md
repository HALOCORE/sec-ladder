# TASK_151 — the three owed GATE repairs, done together. Report

**Role: research engineer.** All three repairs landed. One full sweep, run once.
⚠ **Repair 3's cost premise in the task file was wrong in the direction that
mattered and I did not take the fallback — see §3.**

Files changed (`git diff --stat`, and these three are the whole of it):

```
 harness/check.py                     | 459 ++++++++++++++++++++++++++++++---
 harness/report.py                    |  13 +-
 harness/tools/table_render_inputs.py | 231 +++++++++++++++---
 3 files changed, 634 insertions(+), 69 deletions(-)
```

## 0. The premise the task file asked me to verify BEFORE starting — CONFIRMED

⚠ **`harness/measure.py` IS in `measurement_sources` and I did not touch it.**
The task file's intro says *"you own `check.py`, `report.py`, `measure.py`"*, and
that third file is the one whose edit would have cost a re-measure. Read out of
`measure.py:224-235` and cross-checked against a shipped record rather than the
source:

```
results/p01-array-sum.json  source_sha256 harness/* keys:
    harness/asm.py   harness/build.py   harness/measure.py          <- 3, and no more
results/gate/p01-array-sum.json  source_sha256 harness/* keys:
    asm build check dloop fixture limbs measure report vparse       <- 9
```

So `check.py` and `report.py` are in the **gate** digest and in **no**
measurement record: **one re-gate, zero re-measure.** `git status --porcelain`
before the sweep showed exactly the three files above and nothing else, so
`build.py`, `asm.py` and `measure.py` are untouched and the six committed
`controls/*.json` sidecars (whose `derived_from_sha256` reuses
`measurement_sources`) cannot have gone stale.

✅ **`harness/tools/` is imported by nothing in `check.py`/`measure.py`/
`build.py`** — grepped, empty result. `table_render_inputs.py` stays outside the
gate digest, which is why repair 1 is free.

---

## 1. Repair 1 — the self-reference detector is now a CENSUS over an ALLOW-LIST

`harness/tools/table_render_inputs.py`.

**What was wrong** (`RECAP` 46 (iii), `.memory/03-measurement.md` entry 11): the
`--selfref` verdict rested on `RUN_SCOPED`, a hand-written 9-tuple, while the
gate record carries **34** keys — so 25 were unclassified, and a `report.py`
rendering `table_render` (stage 9c's own verdict about that very table) measured
`26/26 READ` while the detector printed `0` and exited `PASS`.

**What shipped:**

- `READ_OK = ("contract_sha256", "controls_json", "idiom_audit", "loud")` — the
  four keys `TASK_127` established **by mutation**. Everything else is
  forbidden, **including a key added tomorrow.**
- `measure_reads()` takes its key set **from each record**, not from a list in
  the file. `--selfref` is now `violations(measure_reads(all patterns))`.
- `_LEGACY_RUN_SCOPED` is retained, decides nothing, and exists only so the arm
  can show the old detector passing.
- `--selftest`, the must-fire arm.

**Measured on today's tree, 29 patterns:**

```
$ python3 harness/tools/table_render_inputs.py --reads
  contract_sha256          29/29 pattern(s)
  controls_json            29/29 pattern(s)
  idiom_audit              29/29 pattern(s)  [raised on 29]
  loud                     29/29 pattern(s)
not read on p01-array-sum: adversarial, blocked, clause_deletion, complete_run,
derived_contract, driver_loops, expected_hang, failures, identity, idiom,
inputs_checked, invocation, marginal_ir_env, marginal_ir_per_call, miri, notes,
pattern, proof_domain, published_table, requires_strength, run_timeout_s,
sanitizer, skipped_inputs, source_sha256, table_render, verdict,
verified_call_site, verified_twins, verus, verus_exit_anomalies
```

**The measured read set is exactly the allow-list, 29/29 — so the inversion
costs zero false alarms.**

### ⚠ The must-fire arm — `--selftest`, 4 cells, 2 per detector

The plant is `TASK_132`'s reproduction, not an approximation: `report.build` is
wrapped so the render appends the gate record's `table_render`, read through
`report.gate_record` — **the same function the real renderer uses**, out of the
same scratch tree `render()` substitutes into.

```
$ python3 harness/tools/table_render_inputs.py --selftest
must-fire arm for `--selfref`, over 3 pattern(s): p01-array-sum, p02-buffer-copy, p03-bounded-stack

PLANT: a `report.py` whose render appends the gate record's `table_render`
       -- stage 9c's OWN VERDICT about this very table (RECAP finding 46 (iii)).

  ok   PLANTED   census  (the TASK_151 repair)              want FAIL got FAIL
  ok   PLANTED   legacy deny-list (the DEFECT)              want PASS got PASS
  ok   UNPLANTED census  (must-not-fire control)            want PASS got PASS
  ok   UNPLANTED legacy deny-list                           want PASS got PASS

4/4 cell(s) as designed
SELFTEST: PASS -- the census fires on a plant the hand-written
deny-list passes, and neither fires on the shipped report.py.
```

⚠ **Row 2 is the finding, reproduced under the repaired file**: the hand-written
deny-list is blind to the defect the census catches. Log:
`.temp/t151/selfref_selftest.log`.

⚠ **A cell that raises is reported as a failed cell with its exception line, not
allowed to crash** — `.memory/03-measurement.md` entry 19's correction to `p32`'s
own `detector_selftest`, where three of four planted mutations failed by
crashing and the diagnostic was lost.

✅ **A free consequence worth naming: repair 3 adds `sanitizer_hardened` to the
gate record, and the census covers it with nobody listing it.** Under the
deny-list it would have joined the 25 unclassified keys.

⚠ **I did NOT re-run finding 46's clean negatives** (`RENDER-ERROR` is a failing
verdict; the old arm reproduces the `19 of 26`; grepped `verdict` agrees
`130/130`; three fresh `p03` draws move exactly four keys), as instructed.

---

## 2. Repair 2 — `assume(`/`admit(` now FAIL unless the contract declares them

`harness/check.py`. **I took option 2 — the manager's guess — and the deciding
number is a cost, not a preference.**

### The decision, with the cost of each option measured

| option | code | cost of the ESCAPE HATCH when someone legitimately needs an `assume` |
|---|---|---|
| **A** flat FAIL on `assume(` | ~6 lines | edit `harness/check.py` → moves `source_sha256["harness/check.py"]` in **all 29** gate records → **a full 29-pattern re-gate** |
| **B** FAIL unless declared ✅ | +385 lines incl. docs and the arm | one JSON key in that pattern's `slb-contract` block → moves **one** `contract_sha256` → **one pattern's gate run** |
| **C** leave it a shout | 0 | the defect stands, and **three rows remain to be built** |

**A costs 29 pattern re-gates to exercise; B costs 1.** That is the whole
argument, and it is the same argument `_check_axiom_decls` and
`_check_included_tcb` — the two functions immediately adjacent in the same file
— already made in as many words: **"Visibility, not prohibition."** An author who
has met `verus.axioms` will guess `verus.assumptions` correctly.

### ⚠ The accident test, which `.memory/02-bench-rules.md` requires and which C fails

*"Could this defect happen by accident?"* — **yes, and by the most ordinary
route there is.** `assume` is the standard Verus debugging move: assume the
lemma you have not proved yet so the file compiles, keep going, forget to take
it out. That is an honest mistake, which is the threat model.

And `.memory/02-bench-rules.md` settles the shout-vs-fail question with its own
measurement, on `p27`'s `forbidden_hits`: a real defect was **printed in the
verdict, written into the gate JSON and transcribed into `NOTES.md` across three
tasks and two adversarial reviews, and nobody acted on it.**

> **A number that is printed is not a check.**

⚠ **The `assume` shout is in exactly that position, twice over: two independent
reviewers (`TASK_145` X4 on `p32`, `TASK_149` B1 on `p28`) planted
`assume(false);`, both saw `[tcb-axiom]`, and both recorded it as a hole rather
than as a catch.** The shout is what a reviewer *reports*, not what the gate
*decides*.

### What shipped

- `_ASSUME_KEYWORDS` — ⚠ **word-anchored regexes**, `\bassume\s*\(`, replacing
  `re.escape("assume(")`. Promoting a check to a FAIL means a false positive now
  stops the gate: `re.escape` matched `reassume(`, and missed `assume (false)`.
- `_assume_keyword_hits(txt)` — a **pure function of the text**, `{keyword:
  [line, ...]}`, over `vparse.blank_noncode` output so comments and string
  literals are not hits. Pure so the stage-0 arm can drive it with no pattern, no
  contract and no Verus run.
- `_axiom_keyword_scan(rep, src, txt, vcfg)` (renamed from
  `_axiom_keyword_shout`; the old name is cited in `TASK_145_REPORT` §3 and
  `TASK_149_REPORT` §6 and the rename is stated in the docstring). It still
  shouts every hit **with line numbers**, and now `rep.fail("proof-vacuity", …)`
  when the `assume(`+`admit(` count differs from `spec.md`'s
  `verus.assumptions[<src>]` (default 0).
- ⚠ **`assume_specification` is deliberately NOT promoted**: it is a body-less
  trusted *declaration*, `vparse.axiom_decls` sees it, and `_check_axiom_decls`
  already fails unless `verus.axioms` declares it. Promoting it here would
  double-report one item under two contract keys.
- Runs over the `#[path]`-included files too, which is `TASK_084_REVIEW` major 1
  route C's file list.

### Exposure — re-measured, not quoted

```
$ vparse.blank_noncode over 118 committed .rs files (patterns/*/*.rs + common/driver.rs)
   \bassume\s*\(              0
   \badmit\s*\(               0
   \bassume_specification\b   0     (3 files name it, all inside comments)
hits: {}
```

⚠ **So this is prospective and there is no shipped row it breaks — which is
exactly why a green sweep is not its evidence.**

### ⚠ The must-fire arm — `_ASSUME_CASES`, run by stage 0 on EVERY invocation

Placed with `_IDIOM_CASES` / `_MATCH_CASES` / `_AUDIT_CASES` etc., checked in
`check_selftests`, so it is inside `source_sha256` and runs on every gate
invocation — the shape `TASK_147`'s `detector_selftest()` established. **Nine
cells, both guards.**

```
ok   an undeclared `assume(` in code FAILS                          got [1, 1] want [1, 1]
ok   an undeclared `admit(` in code FAILS                           got [1, 1] want [1, 1]
ok   `assume(` in a COMMENT is not a hit                            got [0, 0] want [0, 0]
ok   `assume(` in a STRING literal is not a hit                     got [0, 0] want [0, 0]
ok   a keyword that merely ENDS in `assume(` is not a hit           got [0, 0] want [0, 0]
ok   a DECLARED `assume(` passes and shouts twice                   got [0, 2] want [0, 2]
ok   declaring MORE than the file spells also FAILS                 got [1, 0] want [1, 0]
ok   `assume_specification` shouts but does NOT fail here (`verus.axioms` owns it) got [0, 1] want [0, 1]
ok   a clean file is silent                                         got [0, 0] want [0, 0]

cells: 9 passing: 9
```

⚠ **A raising detector REPORTS rather than crashes**: `_ak()` returns a
**three**-element list on an exception, which can never equal a two-element
expectation, so a broken scan fails stage 0 with its exception text instead of
killing `check.py` at import — `.memory/03-measurement.md` entry 19's correction
to `p32`'s arm, applied here rather than only noted.

---

## 3. Repair 3 — stage `7h`, the hardened arm under ASan+UBSan

⚠⚠ **THE TASK FILE'S COST PREMISE WAS RIGHT IN RATIO AND WRONG IN CONSEQUENCE,
AND I DID NOT TAKE THE FALLBACK.** It predicted this would *"roughly double stage
7"* and be *"the one most likely to blow the budget"*. **It does roughly double
stage 7 — and stage 7 is noise.** Measured before writing a line of it
(`.temp/t151/stage7_cost.py`, `.temp/t151/stage7_cost.json`):

```
second (hardened) sanitizer build      ~0.31 s per pattern
extra runs, ALL inputs incl. sweep-*   ~3.9 s per pattern
added cost over 28 hardened patterns   117.3 s total  (4.2 s each)
```

⚠ **117 s is an UPPER BOUND**: the probe ran every `sweep-*` blob and the gate
does not. Against a sweep in which `check.py p28` alone takes 33 minutes, the
narrowing was not worth taking, so **stage 7h runs on every input, adversarial
included** — which is what the task file says R1h *means*.

### What the sweep-before-the-sweep found: ZERO, over 2027 cells

```
28 hardened patterns x every shipped input
  hardened-arm rows measured : 2027
  hardened-arm SANITIZER FIRINGS : 0
```

✅ **`p28`'s clean result (`TASK_149`, 88 cells) generalises to all 28 rows.**
There is no live defect in any pattern's R1h; this was a gate gap and it is now
closed. **Nothing needed fixing in any pattern, so nothing was.**

### The expectation, and every part of it is a measurement

`.temp/t151/hardened_stdout.py`, both arms on every non-`sweep-` input of all 28:

| what | rule | why it is safe |
|---|---|---|
| any diagnostic, **any** input | **FAIL** | 0 of 2027 fire today |
| NON-adversarial exit + stdout | **FAIL** on mismatch | **72 of 72** non-adversarial rows are identical between the two arms, and the plain arm's are already checked against `model.py` — so this is inherited, not assumed |
| adversarial exit + stdout | **recorded, never required** | **74 of 139** adversarial rows DIFFER between the arms, **and that difference IS the result.** Requiring agreement would false-fail 74 rows |
| a declared hang | **recorded either way** | ⚠ `expected_hang` is a claim about the BUGGY rung. `p22`'s R1 runs past the 120 s budget on `adversarial-full` and **its R1h finishes in a second** |

Also factored out: `_san_build()` and `_san_fired()`, so **the two arms are
built by one compiler line and judged by one predicate** and cannot drift. (Two
copies of a compiler invocation is how `-fstrict-aliasing` came to be missing
from one of them — `TASK_077`.)

The new record key is `sanitizer_hardened`, its **own** key rather than a field
of `sanitizer`, because the two arms are held to different expectations —
`sanitizer` is per-input from `model.sanitizer_expect`, `7h` is `clean` on every
input — and merging them would make a reader think one verdict covered both.
`{}` for `p01`, the only pattern with no R1h.

### ⚠ The must-fire arm — `.temp/t151/hardened_arm.py`, 5 cells, 5/5

It drives **the real `check.check_sanitizers_hardened`**, with the real
`read_contract` / `load_model` / `build_models` / `run_budgets`, against a
sandbox copy of `p28` whose `c/kernel_hardened.c` — **and only that file** — has
a planted heap overflow. `inputs/` is not copied; the real
`patterns/p28-intrusive-lists/inputs/` is passed as `indir`.

```
  ok   C0 control: unmodified R1h (MUST NOT FIRE)               want (0, 8)   got (0, 8)
  ok   C1 benign plant: 7h FIRES, incl. a benign input          want (True, ['sanitizer-hardened'], True)
                                                                got (True, ['sanitizer-hardened'], True)
  ok   C3 same tree, stage 7 (PLAIN arm) stays GREEN            want 0        got 0
  ok   C2 adversarial-only plant: 7h FIRES there too            want (3, True) got (3, True)
  ok   C3b same tree, stage 7 (PLAIN arm) stays GREEN           want 0        got 0

5/5 cell(s) as designed
HARDENED-ARM SELFTEST: PASS -- stage 7h fires on a broken R1h that
no other gate stage sees, on a benign input AND on an adversarial one,
and is silent on the shipped kernel.
```

⚠⚠ **C1 + C3 together are the finding restated as an experiment: the plant makes
stage 7h fail on 7 of 8 inputs including all three BENIGN ones — the `p28d`
shape, `TASK_146` §1 — while stage 7 prints eight `ok` lines.** No pre-existing
stage sees it.

⚠⚠ **C2 is the cell that decided against the fallback.** The plant is keyed on
`len == 12`, a window length measured to occur **only** in
`adversarial-uaf-{head,read,write}.bin`; stage 7h fails on exactly those three
and stage 7 stays green. **Under the offered narrowing — hardened arm on
non-adversarial inputs only — stage 7h would never have run those three inputs
and C2 would have been invisible.** The full version costs ~4 s a pattern.

Log: `.temp/t151/hardened_arm.log`.

---

## 4. The sweep — 29 patterns, ONE pass, exactly the expected verdict

⚠ **Read out of `results/gate/*.json` by `.temp/t151/verdicts.py`, which opens no
log.** (`.temp/t151/verdicts.log`; timings in `sweep1.log` / `sweep2.log`.)

```
verdicts: {'PASS': 27, 'PASS-WITH-BLOCKED-ROWS': 2, 'FAIL': 0, 'other': 0}
total blocked rows : 2          p01 = 1, p42 = 1   <- exactly as predicted
total failures     : 0
total shouts       : 37
stage 7h: 211 row(s) measured, 0 fired, 0 record(s) with NO sanitizer_hardened key
```

**`27 PASS + 2 PASS-WITH-BLOCKED-ROWS`, `p01 = 1`, `p42 = 1`, every other pattern
`0`.** `p42` drew the fast Miri phase and blocked 1, not the legitimate 2.
`rc=0` on all 29 invocations. **Wall clock 6213 s ≈ 104 min**; `p28` alone
**2183 s (36 min)**, consistent with the task file's 33-minute warning.

⚠ **Disclosure: the sweep ran in two halves and the split was not mine.** The
harness killed the background command after `p27` (21 patterns, all `rc=0`);
`p28` was mid-run and its record was therefore still `HEAD`'s. I restarted the
remaining **eight** — `p28 p29 p32 p36 p38 p42 p46 p47` — as one command, and
`p28` was re-run **from scratch**, so no pattern's record is a partial. All 29
records carry `sanitizer_hardened`, which is the mechanical proof that all 29
ran under the new code.

### Closing checks, all run

| check | result |
|---|---|
| `harness/measure.py --check-stale` | ✅ **58 records examined, 0 STALE** — nothing here touched a measurement source |
| `harness/tools/composition.py --check` | ✅ `OK: published composition table matches the tree (29 patterns, 10 classes)` |
| `harness/tools/temp_citations.py` | ✅ `OK (new=0 unclassified=0 resolved=1)` — the `resolved=1` is `.temp/build/p28-repro`, pre-existing; **I did not run `--update`**, which rewrites a committed baseline |
| `table_render_inputs.py --selfref` | ✅ **0 forbidden keys over a 1015-cell census**, all four allow-listed keys READ 29/29, **5 s** |
| `table_render_inputs.py --selftest` | ✅ 4/4 |
| `check._ASSUME_CASES` | ✅ 9/9 |
| `synthesis/licence.py --emit` | re-emitted — see below |
| `synthesis/synthesize.py` | ✅ `wrote results/synthesis.md (81213 bytes, 600 lines)` |
| `results/SYNTHESIS.md` (CAPITALS) | ✅ **byte-identical, `md5sum -c` OK** — never regenerated |
| `results/tables/*.md` | ✅ **unchanged** — stage 9c FRESH 29/29; the repairs move nothing in the render |

`git status` is **34 modified + 1 new**: the 3 harness files, the 29 gate
records, `results/synthesis.md`, `synthesis/licence.json`, and this report.
**No `patterns/` file, no `.memory/`, no `RECAP.md`, no `results/SYNTHESIS.md`.**

### ⚠ `synthesis/licence.json` had to be re-emitted first, and the task file's sequence omits it

`.memory/05-layout.md`: *"`results/synthesis.md` cannot simply be regenerated
after a gate sweep. `synthesis/licence.json` pins each gate record's
`source_sha256` … Re-emit the sidecar first, then the artefact."* Any
`harness/*.py` edit moves all 29 gate digests, so a naive `synthesize.py` would
have published 28 false `LICENCE STALE` lines.

⚠ **And the re-emit crashed the first time, on my own leftovers:
`KeyError: 'p90'`.** `synthesis/licence.py` derives its population from
`.temp/build/`, and repair 3's must-fire arm had left `.temp/build/p90/` there
(the sandbox's pattern id). **Nothing was written** — `licence.json` was
byte-identical after the crash, verified. Removed the directory, re-ran, and
**added the cleanup to `hardened_arm.py`'s `finally` block** so the generator
cannot leave it again. Worth knowing generally: **a scratch pattern id under
`.temp/build/` is visible to `synthesis/licence.py`.**

Result of the good run: **29 patterns, 116 pair verdicts**, and

```
entries before/after: 28 -> 29        new entries: ['p28']
IDENTICAL ignoring gate_source_sha256: False
gate_source_sha256 moved on: 28 entries
pair verdicts changed: 0
```

**Zero licence verdicts moved** — only the staleness pin — **and `p28` gained an
entry it never had**, because `licence.json` had not been re-emitted since `p28`
landed. `results/synthesis.md` accordingly changes `p28 … no licence recorded` to
`p28 … NOT-LIC — ASYMMETRIC INDIRECT dispatch (safe_naive: 6, unsafe: 3)`.

### ⚠⚠ A RE-GATE IS NOT VALUE-FREE, and `--check-stale` structurally cannot see it

This is the one thing in the sweep I did not expect and it is worth the
manager's attention. `results/synthesis.md`'s calibration block moved:

```
- 208 rows, 192 hit, 4 miss, 12 false alarm; residual median 0.18, p95 5.59, max 15.79
+ 208 rows, 188 hit, 4 miss, 16 false alarm; residual median 0.30, p95 7.00, max 15.79
```

**Mechanism, measured rather than guessed:** `marginal_ir_per_call` is a
**callgrind measurement taken inside the gate** (stage 3b) and lives in the gate
record, so **re-running the gate re-draws it**. Diffed against `git show HEAD:`:

```
patterns whose gate marginal_ir_per_call MOVED : 18 of 29
cells moved                                    : 673 of 2772
|delta| min / median / p95 / max                : 5.6e-06 / 0.77 / 7.00 / 7.00
|delta| > 16.00 (the published "every one is real" band) : 0
dominant deltas                                : ±0.77 (324 cells), ±7.00 (32 cells)
```

✅ **Nothing published moved.** The `≥ 16.00` band is **41 rows / 41 real / 0
spurious** before and after; every moved cell sits in the two bands
`results/synthesis.md` already labels *"not safe — this is one environment
phase"* and *"a coin flip — do not quote alone"*. The `±7.00` is **exactly** the
sawtooth amplitude that file's own `‡` note names for `p03`/`p04` R3-R4 (*"`0.00`
at 16 of 32 environment phases and `±7.00` at the other 16"*).

> ⚠⚠ **But the scope is wider than the `‡` note says: 18 patterns and 673 cells,
> not two patterns and four rows.** And **`--check-stale` reported `0 STALE`
> throughout**, correctly — it compares **hashes of sources**, and no source
> moved. **A green `--check-stale` is not a claim that the numbers in the record
> are the same numbers.** I think that belongs in `.memory/03-measurement.md`;
> it is the manager's file, so it is a recommendation, not an edit.

---

## 5. What I did NOT do, and what I am unsure about

**Not touched:** `.memory/`, `RECAP.md`, `results/SYNTHESIS.md`, `harness/measure.py`,
`harness/build.py`, `harness/asm.py`, any earlier `.temp/t*/` or `.temp/mgr*/`.
No `git add`, no `git commit`, no history-mutating git.

### The two items the task file recorded as NOT in scope

1. **Masking the ASan pid and the Miri `seconds`. I agree with leaving it, and I
   can add one datum in its favour.** Stage 7h writes an **empty** `diagnostic`
   on every one of its cells, because it fires on none — so it adds **zero** new
   pid nondeterminism to the gate record. `TASK_149`'s *"5 of 1296 leaves"* is
   not made worse by this task; the denominator grows and the numerator does
   not. It is a fourth repair with its own arm, it changes recorded evidence
   rather than a check, and the standing note it would correct is the manager's.
2. **`p32`'s `detector_selftest()` failing by CRASHING rather than reporting** —
   not done, agreed as a different bundle (`model.py` is measurement-hashed, so
   it is a re-measure). ⚠ **But I applied its lesson to both of my own arms
   rather than only noting it**: `_ak()` returns a three-element list on an
   exception and `_cell()` prints the exception line, so a broken detector
   reports instead of crashing.

### ⚠ What I am least sure of, in order

**(a) `READ_OK` makes `loud` a PERMANENTLY TRUSTED key, and the census
structurally cannot check that.** The allow-list asserts *"these four are
functions of the committed sources"*; the census only asks *"did a key outside
the four reach the render"*. So if any future `rep.shout(` call site embeds
something run-scoped — a duration, a pid, a pointer, a `.temp/` path — **`loud`
silently becomes run-scoped and TASK_127's oscillation returns through an
ALLOW-LISTED key**, which is the same failure one level down. `check.py`'s stage
9c docstring already carries the rule (*"this stage may never `rep.shout`"*) for
**one** stage; `.memory/03-measurement.md` entry 11 bounds the population at
**26 `rep.shout(` sites**. Bounded today by `.temp/t151/loud_stability.py`, not
closed. **Recommend the manager record it as a residual with that mechanism.**

**(b) Stage 7h's exit/stdout comparison on non-adversarial inputs is EXTRA to the
repair.** The load-bearing new thing is *a detector on the hardened arm*. The
comparison is justified by 72/72 and by `p28d` itself — which was an **exit-code
failure on a benign input, not a sanitizer finding**, so a detector-only 7h would
still have missed it. But it does give a future pattern two ways to fail 7h that
are not sanitizer findings. Deleting the two `elif` branches is a two-line change
if a reviewer disagrees; I think it would be the wrong call, and I am naming it
because it is the part of repair 3 that is a judgement rather than a measurement.

**(c) `verus.assumptions` takes an INT, not a per-keyword dict.** `verus.axioms`
accepts int-or-list-of-names; `assume(`/`admit(` have no names, so a list is not
available and I took the simplest reviewable thing. A file with 1 `assume` and 2
`admit` declares `3`. The gate's failure message prints the per-keyword
breakdown **with line numbers**, so no information is lost from the diagnostic —
but the DECLARATION does not distinguish them.

### ⚠ A second instance of "a number grepped out of a log is not a number read out of a record" — mine, disclosed

Mid-sweep I ran a quick status grep,
`grep -E "^check\.py: (PASS|FAIL|PARTIAL|PASS-WITH-BLOCKED-ROWS)"`, and it
printed **`p01 PASS`**. p01 is `PASS-WITH-BLOCKED-ROWS`. **The alternation
matched `PASS` first and truncated the verdict.** Same class as the
`grep -c BLOCKED == 2N+1` defect, **different mechanism** — not a substring
count but **alternation order in the reader** — so the standing note does not
cover it. Every verdict and every `blocked` count in §4 is read out of
`results/gate/*.json` by `.temp/t151/verdicts.py`, which touches no log.

### Adjacent, reported and NOT fixed (scope rule)

- ⚠ **`.memory/05-layout.md` says *"6 of 6 committed `controls/*.json` ALREADY
  carry a pin; ZERO outstanding"*. It is now 16 of 16** — `p28` (5), `p29` (4)
  and `p32` (5) landed since. **All 16 use `derived_from_sha256`, none uses
  `gate_source_sha256`**, so the unreachable-fixpoint hazard is still designed
  out and this task's `check.py` edit could not stale any of them. ✅ **The count
  is stale; the conclusion is not.** Manager's file.
- ⚠ **`.memory/05-layout.md`'s regeneration note is what made me re-emit
  `synthesis/licence.json` before `synthesize.py`** — the task file's closing
  sequence does not mention it. Its figure (*"22 `LICENCE STALE` verdicts"*) is a
  pre-`p23` count; the rule is right and the number is stale.

## 6. Memory updates

**None written — subagents may not edit `.memory/`.** What the manager should
land, from the measured text above:

1. `.memory/03-measurement.md` **entry 11**: the *"invert to an ALLOW-LIST"*
   recommendation is **BUILT** (`--selfref` is a census; `--selftest` is its
   must-fire arm, 4 cells, and it reproduces the `table_render` blindness). ⚠
   Add residual **(a)**: the allow-list moves the trust onto `loud`, and the
   census cannot re-derive it.
2. `.memory/04-verus.md` / **entry for the vacuity hole**: `assume(`/`admit(`
   now FAIL unless `verus.assumptions` declares them. Exposure at landing ZERO
   over 118 `.rs` files. The deciding argument is the **cost of the escape
   hatch**: 29 re-gates (edit `check.py`) against 1 (edit `spec.md`).
3. `.memory/02-bench-rules.md` / `03`: **stage 7h exists**, and the headline is
   **0 firings over 2027 hardened-arm cells across all 28 hardened rows** — a
   gate gap, not a live defect, `p28`'s `TASK_149` result generalised.
4. ⚠ `.memory/05-layout.md`: the `controls/*.json` count is **16, not 6**.
5. ⚠ `.memory/03-measurement.md`'s log-vs-record note: **a second mechanism**,
   regex alternation order in the reader, disclosed in §5.
6. ⚠⚠ `.memory/03-measurement.md`: **a re-gate re-draws `marginal_ir_per_call`,
   and `--check-stale` cannot see it** — 673 of 2772 cells over 18 patterns moved
   on an unchanged tree, all `|Δ| ≤ 7.00`, none in the published `≥16.00` band.
   The `‡` note in `results/synthesis.md` describes this for `p03`/`p04` only;
   the real scope is 18 patterns. §4.
7. ⚠ `.memory/05-layout.md`: **re-emitting `synthesis/licence.json` is a
   REQUIRED step after any `harness/*.py` edit**, and it reads its population
   from `.temp/build/` — a stray scratch pattern id there kills it.

---

**PROTOCOL rule 2 running count: launched from 785
(`TASK_150_REPORT.md`'s closing paragraph), carried to 795** — branch delta
**+10**. ⚠ Reconciliation across any concurrent branch is the manager's job, not
mine.

1. ⚠⚠ **The task file's repair-3 cost premise was REFUTED, in the safe
   direction, and it nearly bought a narrowing that would have been blind.**
   Predicted *"roughly doubles stage 7 … most likely to blow the budget"*;
   measured **0.31 s + 3.9 s per pattern, 117 s over 28**. It does double stage
   7. Stage 7 is noise.
2. ⚠⚠ **Cell C2 shows the offered fallback was blind to three real cells** — a
   plant reachable only on `adversarial-uaf-{head,read,write}` fails stage 7h
   and passes stage 7; the narrowing would never have run those inputs.
3. ✅ **0 hardened-arm firings over 2027 (pattern × input) cells across all 28
   hardened rows**, and 211 rows in the committed records. `p28`'s `TASK_149`
   result generalises: **a gate gap, not a live defect.**
4. **`assume(false)` verifies at the shipped file's own obligation count** on
   both rows that were tried; the obligation count, the clause pin and the
   `identity` pin are all blind to it. The shout was the whole textual trace.
5. **Exposure re-measured at ZERO** across 118 committed `.rs` files, with a
   word-anchored regex the old `re.escape` spelling did not have.
6. **The deny-list detector passes the plant the census fails** — reproduced
   under the repaired file, not quoted.
7. ⚠ **A re-gate moved 673 of 2772 `marginal_ir_per_call` cells on an unchanged
   tree** while `--check-stale` correctly said `0 STALE`.
8. ⚠ **My own log grep decoded `PASS-WITH-BLOCKED-ROWS` as `PASS`** through
   regex alternation order — a second mechanism for a named failure class,
   self-disclosed.
9. **`synthesis/licence.json` had never been re-emitted since `p28` landed**;
   it gained a 29th entry and zero verdicts moved.

⚠ **A rigour signal, not a ledger.**
