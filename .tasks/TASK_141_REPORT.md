# TASK_141 — the three repairs, and one of them is REPORTED rather than LANDED

**Role: research engineer.** Only agent running. Scratch is `.temp/t141/`.
No `git add` / `git commit`. `.memory/`, `RECAP.md` and `results/SYNTHESIS.md`
untouched — every correction they need is listed in §6 for the manager.
`.temp/t136/`, `t137/`, `t139/`, `t140/` were read and never written.

> ## ⚠⚠ READ THIS FIRST — REPAIR 3 IS NOT LANDED, AND THE REASON IS A MEASUREMENT
>
> `RECAP` records **21 unpinned sidecars** as owed. The task told me to
> re-derive the count. **The count is still 21 — and the WORD IS WRONG.**
>
> ```
> committed patterns/*/controls/*.json               6
>   carrying `derived_from_sha256`                   6      <- 6 of 6
>   carrying no pin                                  0      <- ZERO OUTSTANDING
>
> controls/*.py that call `json.dump(`                26
>   already emitting a pin                            5     (p23 x1, p29 x4)
>   not emitting a pin                                21    across 12 patterns
>   ... of those 21, how many write into the TREE?     0    <- ALL 21 -> .temp/
> ```
>
> **All 21 write their JSON into gitignored `.temp/`.** Stage 9b's glob is
> `patterns/*/controls/*.json`, so a `derived_from_sha256` written by any of
> the 21 is read **by nothing, ever**. Landing them would be adding 21 keys no
> check can fail on — this project's own most-named defect — and doing it
> without being able to run 21 callgrind sweeps to prove any of them right.
>
> ✅ **AND THE GENERATORS ARE ALREADY PINNED, BY A DIFFERENT MECHANISM.**
> `check.py::main`'s `source_sha` globs `patterns/*/controls/*.py`: **96
> entries across 27 gate records, and the set matches the disk exactly, 0
> mismatches.** So an edit to any of the 21 already stales its pattern's gate
> record. What is unpinned is only the *deletable* output, which
> `CLAUDE.md` constraint 1 says is the thing you delete and the generator is
> the thing you keep. `p06/controls/clayout.py`'s own docstring makes that
> argument in those words.
>
> ✅ **The cost claim the task asked me to VERIFY rather than assume is
> verified, and by measurement not by reading**: `controls/*` appears in **0**
> of 27 measurement records' `source_sha256` and in **27 of 27** gate records'.
> A `controls/*.py` edit is a gate re-run and never a re-measure.
>
> ⚠ **The residue that IS real and is NOT this class** — reported, not fixed:
> **8 committed control files are in NO digest at all**, because the gate globs
> `controls/*.py` and these are not `.py`:
> `p06`/`p14`/`p18`/`p27`'s `build_controls.sh`, `p06`/`p14`/`p18`'s
> `verify_controls.sh`, and `p42`'s `affine_leak.rs`, `leak.sh`,
> `miri_seeds.sh`. `p42`'s `NOTES.md` publishes numbers from `leak.sh` and
> `miri_seeds.sh`. `p23`'s `guard_variants.c` and `run.sh` are the only two
> non-`.py` control sources anything hashes, and it is `controls_pin.json` that
> does it. Full census in §3.

---

## VERDICT IN ONE SCREEN

| repair | state |
|---|---|
| **1 — `p29`'s false headline** | ✅ **LANDED** in 7 files (`spec.md` via its generator, `c/kernel.h`, `c/kernel.c`, `c/kernel_hardened.c`, `README.md`, `NOTES.md`, `controls/mkspec.py`), plus the hashed `obligations_note`'s attribution. `contract_sha256` `f77972d2d5da → a7249f0d60f3`. Two control sidecars regenerated (`arms.json`, `repro.json`) and `controls/arms.py` given a `pin.not_covered` for a DRAW it was publishing as a figure (§2d); `p29` re-measured and re-gated `PASS`. ⚠ **The `.rs` rung sources are NOT edited and one of them still carries the claim** — §2c, with the measured cost of doing it. |
| **2 — stage 9c's one-run lag** | ✅ **LANDED, with a must-fire arm built from the real `d41ba6c` state.** Old 9c `FRESH` / new 9c `STALE-CONTENT, 4 lines` / new 9c on the repaired state `FRESH`. Plus two more must-fire arms on the drift guard and on the "cannot" clause. §1. |
| **3 — the unpinned sidecars** | ⚠ **REPORTED, NOT LANDED.** Box above. 0 outstanding in the class the gate can read; the 21 are generators whose output is gitignored and already covered by the gate digest. |
| **the final sweep** | see §4 |
| **Running count** | base **687**, branch delta, sum: §7 |

---

## 1 — REPAIR 2: STAGE 9c NOW COMPARES AGAINST THE RECORD THIS RUN WRITES

### 1a. What was wrong, in one line

`check_table_render` called `reportmod.build(doc, name)`, and `report.py` read
`results/gate/<pattern>.json` off disk — which, at stage-9c time, is the
**previous** run's record. Worse, `check_control_json_pins` (stage 9b) ran
**after** 9c, so `controls_json` did not even exist yet when 9c needed it.

### 1b. The fix, and why NOT the obvious spelling

Three changes, all inside the gate digest and therefore paid for by this sweep:

1. **`harness/report.py`: `gate_record(pattern, gate=None)`** — one new
   function. `read_gate_audit` and `read_gate_loud` go through it, and
   `build`/`idiom_section`/`audit_section`/`shout_section` thread an optional
   `gate` dict. With `gate=None` — every standalone `harness/report.py pNN` —
   the behaviour is byte-for-byte what it was.
2. **`harness/check.py::main`: stage 9b MOVED ABOVE 9c**, and a snapshot
   `gate_now = {contract_sha256, controls_json, idiom_audit, loud}` taken
   between them and handed to 9c. The order is now load-bearing and says so in
   a comment.
3. **`harness/check.py::_check_render_inputs_final`** — after the record dict
   is built and **before** the verdict is computed, re-compare those four keys
   against what is actually being written; `rep.fail` on drift.

⚠ **Not "move 9c after the record write".** The failure would then have to
change a record already on disk, so either the record's `verdict` lies about
its own run or the stage rewrites it — which is the `verdict` self-reference
`TASK_127` fixed. Passing the values forward has neither problem.

⚠ **9c may still never `rep.shout`**, and the guard may not either: `loud` is
rendered, so a shout would falsify the comparison it is part of. Both are
`rep.fail`-only and the docstrings say why.

### 1c. THE FOUR KEYS ARE THE RIGHT FOUR, AND IT IS MEASURED

`python3 harness/tools/table_render_inputs.py --reads` mutates each key of each
record and re-renders:

```
  contract_sha256          27/27 pattern(s)
  controls_json            27/27 pattern(s)
  idiom_audit              27/27 pattern(s)  [raised on 27]
  loud                     27/27 pattern(s)
not read: 30 other keys, incl. verdict, blocked, failures, table_render
```

`--selfref` after the change: **`0` run-scoped keys reaching the render, over
27 patterns x 9 keys, `SELFREF: PASS`.**

**And the `gate=None` path is byte-identical**: re-rendering all 27 published
tables through the new `report.py` gives `27 checked, 0 differ`.

### 1d. ⚠⚠ THE MUST-FIRE ARM — REBUILT FROM `d41ba6c`, NOT MOCKED

`.temp/t141/probe_9c/` (`build_sandbox.py`, `arm.py`, `guard.py`). Two
repo-shaped sandboxes are built from `git show`, each with its own
`harness/check.py` + `harness/report.py` and every other harness module
symlinked, so the two arms differ **only** in the two files under test.

**The state reconstructed** (read out of `git`, not from memory):

```
git show d41ba6c:results/gate/p29-bst-delete.json
   controls_json  arms/miri_arms/proof_mutants/repro : all FRESH
   table_render   FRESH, render_sha256 == published_sha256 == b1398ea3ae68...
git show d41ba6c:results/tables/p29-bst-delete.md
   FOUR lines saying those same four sidecars are STALE ... UNDATED
```

The sandbox's **on-disk** record is `gate2`'s — `d41ba6c`'s record with
`controls_json` rolled back to all-`STALE`, which is what the published table
was rendered from — and "this run" computes all-`FRESH`, which is what the
committed record proves `gate3` computed.

```
== arm old: check_table_render(pdir, rep, tables)
   ok  results/tables/p29-bst-delete.md is byte-identical to a fresh render (b1398ea3ae68)
   {"arm":"old","verdict":"FRESH","failures":0,
    "render_sha256":"b1398ea3ae68df9a","published_sha256":"b1398ea3ae68df9a"}

== arm new: check_table_render(pdir, rep, tables, gate_now)
   FAIL [tables] results/tables/p29-bst-delete.md is STALE IN ITS CONTENT: 4 line(s) differ
   {"arm":"new","verdict":"STALE-CONTENT","lines_moved":4,"failures":1,
    "render_sha256":"b0d5af3b533f5826","published_sha256":"b1398ea3ae68df9a"}

== arm ctl: the TASK_140 repair applied (table re-rendered from the FRESH record)
   ok  byte-identical to a fresh render (b0d5af3b533f)
   {"arm":"ctl","verdict":"FRESH","failures":0}
```

⚠⚠ **The old arm's `render_sha256` is `b1398ea3ae68df9a…`, which is the value
`d41ba6c`'s committed record carries.** So this is a reproduction of the
committed state, not a model of it — the sandbox and the real `gate3` compute
the same hash.

**Two further must-fire arms** (`guard.py`, `rc=0`):

```
G1  _check_render_inputs_final
      control  (nothing moved)      failures=0
      loud grew by one shout        failures=1  FIRED   <- the reachable case
      controls_json moved           failures=1  FIRED
      idiom_audit moved             failures=1  FIRED
      contract_sha256 moved         failures=1  FIRED
G2  "or fail loudly when it cannot" -- driven against the REAL p29
      gate_now=None          -> RENDER-ERROR, 1 failure
      gate_now={}            -> RENDER-ERROR, 1 failure
      gate_now=3 of 4 keys   -> RENDER-ERROR, 1 failure
```

G2 matters because the cheap bug here is a `gate=None` default silently
restoring the lag. 9c asserts the shape instead of defaulting.

### 1e. What the new 9c does that the old one did not, on a NEW pattern

With no gate record at all, the old 9c said `FRESH` while stage 9 said
`UNPINNED` (finding 46 (i)). The new one renders with the audit section this
run computed and reports `STALE-CONTENT` — which is correct, and stage 9
already fails that case, so no workflow changes. The documented loop for a new
pattern is unchanged: `measure.py` → `report.py` → gate.

---

## 2 — REPAIR 1: THE COUNTING HEADLINE IS OUT OF THE TREE

`.temp/t141/repair1/apply.py` — 23 exact-match substitutions, each asserted
unique, `--check` first. `spec.md` is **generated**, so every `spec.md` change
was made in `controls/mkspec.py` and the artefact rebuilt (`mkspec.py --check`
was `OK` before and after).

⚠ **The script was NOT idempotent when I first wrote it and I caught it by
running it twice, not by reading it.** Two of the 23 substitutions *append* to
their anchor, so `old` is a prefix of `new` and still matched after they had
been applied — a second run would have duplicated both added paragraphs. Fixed
by testing `new in t` **before** `old`, and the ordering now carries a comment
saying why. Verified: a second real run reports `21 ALREADY APPLIED + 2 ALREADY
APPLIED` for all 23 and `0 applied`, and `git status` shows no new
modification.

### 2a. What replaced it

**Out**, everywhere it was a claim rather than a description:

> ~~`p27`'s read-path safety line needs ONE conjunct; `p29`'s needs TWO.~~

**In** — the task file's replacement, in the hashed `why`, `c/kernel.h`,
`README.md` and `NOTES.md` 0a:

> **One source line carries TWO BUG CLASSES SELECTED BY THE INPUT** — a
> use-after-**free** on 0/1-child victims and an in-bounds
> use-after-**recycle** on two-child ones, because the in-order-successor
> splice overwrites its victim in place and frees the successor. ⚠ **And the
> half every detector sees is the half that CANNOT BE GATED.**

⚠ **I did NOT write the task file's `19-of-20`.** The committed
`controls/repro.json` says **20 of 20** distinct on the use-after-free inputs,
and `repro.py`'s own docstring says the count is itself nondeterministic and
must never be quoted as a figure. The tree now states the **invariant** — *not
reproducible on the free windows, reproducible at 1 on the recycle one* — and
no count.

Also narrowed, per the task: `NOTES.md` §6c's *"the `&&` ordering is FORCED at
R5"* is now *"given the two-conjunct spelling, the order is forced"*, with the
`M2b` measurement kept and its scope stated; and §6c now carries **the one
argument that does prefer the shipped spelling** (`base`'s exec/ghost tie is
free under a bit and costs a new conjunct under an occupant tag), flagged
*argued, not measured*.

### 2b. The `obligations_note` attribution

Inside the hashed fence. **The NUMBER 25 does not move**; the stated cause
does. `25 = … + **struct Rec 1** + …` becomes `… + **the #[derive(Clone, Copy)]
on struct Rec 1** + …`, and the note now says a bare `struct` carries ZERO,
`#[derive(Clone)]` carries one, `#[derive(Debug)]`/`#[derive(PartialEq)]` carry
zero, that `TASK_139`'s probe added its `Rec2` **with** the derive while calling
it *bare*, and that `p36`'s bare `OpTag` counts zero and sums exactly to 12.
The prose pin table above the fence says the same thing.

### 2c. ⚠ WHAT I DID **NOT** EDIT, AND THE COST OF DOING IT

Three rung sources still carry a form of the claim, and the sharpest is
`unsafe.rs:61`: *"**This is the obligation p29 is about and it takes TWO
conjuncts**"*. `verus.rs:216`, `safe_naive.rs:200` and `safe_tuned.rs:198` say
*"the safety line below needs a second conjunct"*, which reads as a statement
about the spelling they are in, but reads the other way too.

They are absent from this task file's Sites list **and** from `TASK_140` §1's
ten-file list, and the cost of adding them is not in either:

| edit | stales | to clear |
|---|---|---|
| `unsafe.rs` | `controls/miri_arms.json` (pins `unsafe.rs`) + the measurement record | `miri_arms.py` (Miri over 4 arms) **+ a second `p29` re-measure** |
| `verus.rs` | `controls/proof_mutants.json` (pins `verus.rs`) + the measurement record | `proof_mutants.py` — **10 Verus runs over a 1486-line file**; `TASK_140` measured 7 such runs at ~15 min |
| `safe_naive.rs` / `safe_tuned.rs` | the measurement record | a re-measure |

The `p29` re-measure this task paid for took **6m18s** and its gate run
**6m51s** (§2e), so the re-measure half is cheap. **The mutant battery is not**:
`proof_mutants.py` runs ten Verus verifications of a 1486-line file, and
`TASK_140` measured seven such runs at ~15 min, so ten is ~20–25 min, on top of
a second measure + gate (~13 min) and a `miri_arms.py` regeneration. That is
~40 min of re-runs for a comment fix the task file does not list, on top of a
57-minute sweep — so under its own *"stop and report rather than half-land"*
rule I stopped. **Owed, and it is cheap to bundle with the next `p29`
re-measure, whatever causes it.**

### 2d. ⚠⚠ REGENERATING `arms.json` FOUND A DRAW PUBLISHED AS A FIGURE

`c/kernel.h` is pinned by `arms.json` and `c/kernel_hardened.c` by
`repro.json`, so a comment-only edit staled both and both were regenerated by
their own `pin.regenerate` command. `repro.json` came back identical except its
hashes and timestamp. **`arms.json` did not**, and the reason is worth more than
the repair:

```
                  wrong_total / wrong_on_uaf, keyonly and deref
HEAD (TASK_139)        7 / 7
TASK_141 draw 1        8 / 8      <- moved
TASK_141 draw 2        7 / 7
TASK_141 draw 3        7 / 7
TASK_141 draw 4        7 / 7      <- what is committed
EVERY OTHER CELL of all six arms: CONSTANT 4 of 4, including all six
`asan_lines`, every recycle column and every `nulltab` column.
```

**Structural, not environmental**: `keyonly` and `deref` are the two arms that
delete the **liveness** conjunct, so their identity test reads freed memory *by
construction*, and whether the stale bytes still spell the old key is a draw.
This is `p23`'s `k_selfpivot` class inside `p29`. Landed:
`arms.json`'s `pin.not_covered` now names those cells (and the unhashed
`SLB_GCC`), and `NOTES.md` §2b carries the draw history plus the invariant that
survives it — `keyonly`/`deref` pay ~208 ASan lines and a handful of wrong
answers, `liveonly` pays zero ASan lines and **every** recycle window. The
committed numbers are unchanged, so the published table is still correct.

### 2e. The re-measure, and what moved

`harness/measure.py p29`, log `.temp/t141/logs/measure-p29.log`.
**`real 6m18.157s`** — the re-measure is cheap, exactly as `PROTOCOL.md` rule 6
records for `p19` and `p46`, and this is a third instance.

**What moved, by leaf, against `git show HEAD:results/p29-bst-delete.json`:**

```
leaves: 1345   moved: 102
    96  wall-clock
     3  timestamp / git metadata
     3  source hash          (c/kernel.c, c/kernel.h, c/kernel_hardened.c)
     0  Ir      0  md5/static      0  checksum      0  identity
```

**Wall-clock cells discarded for >10% min-to-median spread: `0` before and `0`
after**, so nothing I ran alongside it contaminated the block — I kept the box
quiet for the whole run and checked afterwards rather than assuming.

`harness/check.py p29` then returned exactly the two failures the repair
predicts and nothing else — `[tables]` STALE (contract moved) and `[tables]`
STALE-CONTENT, 40 lines — with `blocked: []`, `verus 25 verified / 0 errors`,
`tcb_items 7`, `identity O0 differ / O3 norel`, `controls_json` all four
`FRESH`. `harness/report.py p29` re-rendered it; `measure.py p29 --check-stale`
is `2 record(s) examined, 0 STALE`, and all four sidecar pins re-hash clean.


---

## 3 — REPAIR 3: THE CENSUS, IN FULL

Re-derived, not trusted. `grep -l 'json\.dump'` over `patterns/*/controls/*.py`
also matches `json.dumps` — the same trap `TASK_127` recorded — so the census
separates them.

```
36 files match `json.dump(` or `json.dumps(`
26 files call `json.dump(`                     <- the class
 5 of those already emit `derived_from_sha256`  p23/sweep_fit.py,
                                                p29/{arms,miri_arms,proof_mutants,repro}.py
21 outstanding, across 12 patterns:
   p04 sweepfit.py                        p18 clayout.py  sweep_ir.py
   p06 clayout.py  sweep_ir.py            p22 clayout.py
   p10 clayout.py  fit.py  sweep_ir.py    p27 clayout.py  sweep_ir.py
   p12 sweep_ir.py                        p36 clayout.py
   p13 library_axis.py  spellings.py      p46 sweep_ir.py
       sweep_fit.py                       p47 clayout.py  sweep_ir.py
   p14 clayout.py  sweep_ir.py
```

⚠ **The figure has not moved and the reason is a coincidence worth writing
down**: `TASK_127` measured *22 files, 1 pinned ⇒ 21*. `p29` added **four**
files and **four** pins, so it is now *26 files, 5 pinned ⇒ 21*. Anyone
checking the arithmetic by re-running the grep gets the same 21 for a different
reason.

**And every one of the 21 writes into `.temp/`**, verified per file:
`.temp/p06/clay`, `.temp/p12/sweep_ir.json`, `.temp/t89/sweepfit.json`,
`.temp/p27/sweep.json`, `SCRATCH` under `.temp/…`, and so on. **None writes
into `patterns/*/controls/`**, which is the only place stage 9b looks.

**The two verifications the task asked for, both measured:**

```
controls/*.py in gate records' source_sha256   : 96 entries / 27 records,
                                                 set == disk, 0 mismatches
controls/*   in measurement records            : 0 occurrences, 27 records
```

So a `controls/*.py` edit costs a gate re-run and never a re-measure — and, more
to the point, **the generators are already covered**; it is only their
deletable output that is not, and `CLAUDE.md` constraint 1 is that the
generator is the artefact.

**Committed sidecars, all 19 non-`.py` files under `controls/`:**

| file | pinned by |
|---|---|
| `p23/sweep_fit.json` | its own `derived_from_sha256` |
| `p23/controls_pin.json` | itself; it pins `controls.log` |
| `p23/controls.log` | `controls_pin.json` |
| `p23/guard_variants.c`, `p23/run.sh` | `controls_pin.json` |
| `p29/{arms,miri_arms,proof_mutants,repro}.json` | their own `derived_from_sha256` |
| ⚠ `p06`,`p14`,`p18`,`p27` `build_controls.sh` | **nothing** |
| ⚠ `p06`,`p14`,`p18` `verify_controls.sh` | **nothing** |
| ⚠ `p42` `affine_leak.rs`, `leak.sh`, `miri_seeds.sh` | **nothing** |

**Zero unpinned committed sidecars carrying measured numbers.** The eight
⚠ rows are control **sources**, not caches, and are outside every digest
because the gate's glob is `controls/*.py`. `p42`'s `NOTES.md` publishes numbers
from `leak.sh` and `miri_seeds.sh`, so that one is worth a task; it is a
one-line glob change (`controls/*.py` → `controls/*`) plus one sweep, and I did
not make it because it is not this task's repair and it would have moved every
`source_sha256` for a reason the manager has not weighed.

---

## 4 — THE FINAL SWEEP

**Result: exactly what the task file predicts.** Read out of
`results/gate/*.json`, key by key, **never grepped** — `grep -c BLOCKED`
matches the verdict string `PASS-WITH-BLOCKED-ROWS` and decodes as `2N+1`.

```
verdicts        PASS 25   PASS-WITH-BLOCKED-ROWS 2      records 27
failures        0 on every pattern
blocked rows    p01 = 1   p42 = 1   every other pattern = 0   (total 2)
stage 9         FRESH 27/27
stage 9c        FRESH 27/27          <- the repaired stage, on its own sweep
```

⚠ **`p42` came back at 1, not 2.** The task file says 2 is legitimate because
the Miri slowdown is environment-selected; on this run it was 1, which is the
committed state and not a change.

**And the sweep is its own must-not-fire arm for repair 2.** Every one of the
27 patterns ran the new stage 9c against the record *that run* wrote, and 27 of
27 came back `FRESH` — including `p29`, whose whole `contract_sha256`,
measurement record and published table had moved earlier in the same task. The
old stage would have said `FRESH` there too, but for the wrong reason.

**Timings**, `.temp/t141/sweep/rc.txt`, one line per pattern, `rc=0` on all 27:

```
p01 340  p02 112  p03  94  p04  94  p05  87  p06 128  p07  89
p08 133  p09  95  p10  81  p11  84  p12 104  p13 107  p14 123
p16  88  p17 101  p18  77  p19  89  p22 302  p23 107  p27 206
p29 415  p36  95  p38  97  p42 455  p46 106  p47  79
                                                 total 3888 s = 64.8 min
```

⚠ **DISCLOSED: the sweep ran in three pieces, not one, and none of it is my
choice.** The harness stopped the background wrapper the loop was running under
after `p38` (24 of 27 complete), and a second invocation hit the tool's own
10-minute ceiling after `p46`. **Nothing was killed by me** — `CLAUDE.md`
constraint 2 — and nothing is lost or double-counted: `check.py` is
per-pattern, writes its record only at the end, and the three interrupted
wrappers had each finished the pattern they were on or left the previous
record intact (verified for `p42` before re-running it). `p42`, `p46` and `p47`
were then run individually to completion, `rc=0` each, and every one of the 27
records was written by a full non-`--skip` run.

### The finishing checks

```
harness/measure.py --check-stale        54 record(s) examined, 0 STALE
harness/tools/composition.py --check    OK: ... 27 patterns, 10 classes
harness/tools/temp_citations.py         OK (new=0 unclassified=0 resolved=0)
synthesis/licence.py --emit synthesis/licence.json
                                        27 patterns, 108 pair verdicts, 54 s
python3 synthesis/synthesize.py         wrote results/synthesis.md
                                        79381 bytes, 578 lines
                                        741eeb64e9d1 -> 801a160a8c62
```

⚠ **`licence.py --emit synthesis/licence.json` is not optional and the PATH is
not optional**: `licence.json` pins the gate `source_sha256` per pattern, this
task moved all 27, and bare `--emit` exits `rc=2` writing nothing — the
`TASK_127` mistake `RECAP` 46 records. Run in that order, `results/synthesis.md`
has **one** occurrence of `LICENCE STALE` and it is the *paragraph explaining
the mechanism*, not a verdict.

✅ **`results/SYNTHESIS.md` (CAPITALS) was never opened for writing**:
`git diff --stat results/SYNTHESIS.md` is empty.

✅ **Published tables**: all 27 re-rendered through `report.py` and diffed
against the committed files — **0 differ**.

✅ **`results/synthesis.md` now reads `Patterns: 27`, 14 occurrences of `p29`**,
and its Claim 1 identity census self-corrected to *"`exact` for the `unsafe vs
verus` pair on 25 patterns and `norel` for 2 (p29, p36)"* — the stale `25 / 1
(p36)` `TASK_140` §10 item 11 flagged.

---

## 5 — CLEAN NEGATIVES: things I checked that were NOT wrong

Named attacks that did **not** land, so nobody re-runs them.

1. **"The `gate=` parameter changes what `report.py pNN` renders."** No.
   All 27 published tables re-rendered through the new `report.py` with
   `gate=None`: **27 checked, 0 differ**, before any other change.
2. **"The four keys are the wrong four — `report.py` reads more than that."**
   No. `table_render_inputs.py --reads` re-measures the read set by mutation on
   the new code: exactly `{contract_sha256, controls_json, idiom_audit, loud}`,
   **27/27**, with 30 other keys not read.
3. **"Moving stage 9b above 9c changes 9b's verdicts."** No. 9b reads
   `source_sha` and the committed sidecars, neither of which any stage between
   them touches; `controls_json` is identical in every record before and after.
4. **"`arms.json`'s move to 8 was caused by my comment edit."** No — it is a
   draw: **7, 8, 7, 7** over four runs, three of them on one unchanged tree
   (§2d). A comment cannot change `-O1` codegen and the arms that do not read
   freed memory did not move.
5. **"`p23/controls/sweep_fit.json` goes stale because I edited `harness/`."**
   No. Its pin is `measure.py::measurement_sources(p23)` + `sweep_fit.py` + the
   sweep blobs; `check.py` and `report.py` are in neither list. Verified: it
   re-hashes clean and is `FRESH` in the sweep.
6. **"`RENDER-ERROR` cannot be reached, so the `gate_now` assertion is dead
   code."** No — arm G2 reaches it three ways and each `rep.fail`s.
7. **"`repro.json` will move because it is nondeterministic by design."** It
   did not: regenerated identically except the two moved hashes and
   `measured_utc`. Its `R1` distinct counts are `20/20/1/20/1/1`, the same
   invariant, on a different draw.


---

## 6 — FOR THE MANAGER: the files I may not edit that still carry the retracted claim

Everything below is in a file this task may not touch. Each is the
retracted conjunct-count sentence or a consequence of it.

| file | what is still there |
|---|---|
| `RECAP.md` ~4097 (finding **51**) | *"`p27`'s read-path line needs ONE conjunct (LIVENESS); `p29`'s needs TWO … The row clears the bar on a STRONGER claim"* — **un-struck**, while finding 52 twelve hundred lines below strikes it. Two findings disagreeing is PROTOCOL rule 13's shape across items rather than within one. |
| `.memory/06-catalogue.md` line 381, `p29` cell | the cell **both** strikes the sentence (clause 9) **and** re-asserts it (clause 44: *"THE ROW NOW CLEARS THE BAR ON LIMB 1 … ON A STRONGER SENTENCE: `p27`'s read-path line needs ONE conjunct; `p29`'s needs TWO"*). Rule 13 **inside one cell**. |
| `.memory/06-catalogue.md` line 381, clause 5 | *"TCB 7 — THE SECOND CONJUNCT COSTS NONE OF THEM"* reads as a claim about a necessary second conjunct; it is true and should say *the occupant-identity test costs none of them*. |
| `.memory/06-catalogue.md` `p29` row, cols 2–3 | still *"binary search tree insert/lookup"* / *"recursive ownership"*. The shipped row is delete-with-a-cached-lookup over a slot table of raw pointers (`TASK_140` §10 item 10, still owed). |
| `.memory/03-measurement.md` entry **15** | *"a green stage 9c is not evidence…"* is now **closed in code**; the entry should say so and name the arm, or the next reader re-derives the lag. |
| `.memory/04-verus.md` | the corrected obligation rule (bare `struct` 0, `#[derive(Clone)]` 1) is in `.memory/03-measurement.md` entry 17 as a *probe-design* lesson; `04-verus.md` is where a reader looks for the rule itself. `p29`'s hashed `obligations_note` now carries it. |
| ✅ already correct | `results/SYNTHESIS.md` 1314 (struck at `2cef643`), `.memory/02-bench-rules.md` 1930. |

⚠ **And one substantive item for `.memory/03-measurement.md`, from §2d:** a
`derived_from_sha256` that re-hashes clean does **not** make the sidecar's
numbers reproducible. `p29`'s `arms.json` is the second instance after `p23`'s
`controls.log`, and in both cases the irreproducible cells are the ones that
read memory the program does not own. **The rule that generalises: any control
arm built by DELETING a safety check produces draws, not figures, in exactly
the columns the deletion makes undefined.**


---

## 7 — PROTOCOL rule 2 running count

Base **687** (as given by the task file). Branch delta **+8**:

0. **The stage-9c one-run lag is CLOSED IN CODE, and the fix is proved on a
   reconstruction of the real committed state rather than on a mock.** Two
   repo-shaped sandboxes built from `git show`, differing only in
   `check.py`/`report.py`: the OLD stage 9c returns `FRESH` with
   `render_sha256 = b1398ea3ae68df9a…`, **which is the value `d41ba6c`'s own
   committed record carries**; the NEW one returns `STALE-CONTENT, 4 lines`;
   and the NEW one on the `TASK_140`-repaired state returns `FRESH`. A
   forward-only fix would have had none of those three.
1. ⚠⚠ **"21 unpinned sidecars" is wrong in KIND, not in count, and the count is
   unchanged for a coincidental reason.** **6 of 6 committed
   `patterns/*/controls/*.json` carry `derived_from_sha256`; ZERO are
   outstanding.** The 21 are *generators*, and **all 21 write into gitignored
   `.temp/`** — outside stage 9b's only glob — so a pin written by any of them
   would be read by nothing. ✅ **And they are already covered**:
   `controls/*.py` is in every gate record's `source_sha256`, **96 entries over
   27 records, set equal to the disk, 0 mismatches**. The figure is 21 both
   before and after `p29` only because `p29` added four files *and* four pins.
2. ⚠ **The task file's own figure does not match the committed evidence.**
   *"R1's checksum is 19-of-20 distinct on the UAF half"* — `repro.json` says
   **20 of 20**, and `repro.py`'s docstring says the distinct count is itself
   nondeterministic and must never be published. The tree now carries the
   INVARIANT and no count.
3. ⚠⚠ **`p29`'s `arms.json` publishes a DRAW as a figure, found by regenerating
   it.** `keyonly`/`deref` `wrong_total` and `wrong_on_uaf` measured
   **7, 8, 7, 7** over four draws — three on one unchanged tree — while **every
   other cell of all six arms was constant 4 of 4**. The two that move are
   exactly the two arms that DELETE THE LIVENESS CONJUNCT and therefore read
   freed memory by construction. **The rule: a control arm built by deleting a
   safety check yields draws, not figures, in exactly the columns the deletion
   makes undefined.** Landed in `pin.not_covered` and `NOTES.md` 2b.
4. ⚠ **Eight committed control files are in NO digest at all** — the gate globs
   `controls/*.py` and they are `.sh`/`.c`/`.rs`. `p42`'s `NOTES.md` publishes
   numbers from two of them (`leak.sh`, `miri_seeds.sh`). Different class from
   the one the task named, and not fixed here.
5. ⚠ **`.memory/06-catalogue.md`'s `p29` cell BOTH strikes the counting
   sentence AND re-asserts it**, 35 clauses apart, and `RECAP` finding **51**
   asserts it un-struck while finding **52** strikes it. PROTOCOL rule 13's
   shape *inside one cell* and *across two findings* — the manager's to fix,
   listed in §6.
6. ⚠ **Three `.rs` rung sources still carry the claim and I did not edit
   them**, because clearing the sidecars they are pinned by costs ~40 min of
   Verus and Miri re-runs on top of a second re-measure — more than the task
   file budgets. Reported with the cost rather than half-landed (§2c).
7. ✅ **A third instance of PROTOCOL rule 6's "the re-measure is cheap":**
   `p29` re-measured in **6m18s**, moving **102 of 1345 leaves — 96 wall-clock,
   3 timestamps, 3 source hashes, and ZERO `Ir`, md5, static, identity or
   checksum**, with 0 discarded wall-clock cells before and after.

**687 + 8 = 695.**

---

## 8 — SCRATCH

`.temp/t141/` — generators and evidence kept, binaries deleted by the
generators themselves.

```
probe_9c/build_sandbox.py   builds old/ new/ ctl/ from git + the working tree
probe_9c/arm.py             drives ONE sandbox's stage 9c        (repair 2)
probe_9c/guard.py           arms G1 and G2                       (repair 2)
repair1/apply.py            the 23 substitutions, --check first  (repair 1)
sweep.sh                    the 27-pattern sweep, one log per pattern
logs/arms.log logs/arms-run{2,3,4}.log  logs/arms-draw{1,2,3,4}.json
                            the four draws behind §2d
logs/repro.log  logs/measure-p29.log  logs/gate-p29-1.log
sweep/<pattern>.log  sweep/rc.txt      the sweep
```

Everything regenerates:

```sh
python3 .temp/t141/probe_9c/build_sandbox.py
python3 .temp/t141/probe_9c/arm.py old      # FRESH   -- the defect
python3 .temp/t141/probe_9c/arm.py new      # STALE-CONTENT, 4 lines
python3 .temp/t141/probe_9c/arm.py ctl      # FRESH   -- must-not-fire
python3 .temp/t141/probe_9c/guard.py        # G1 PASS  G2 PASS
python3 .temp/t141/repair1/apply.py --check # idempotent; all 23 accounted for
python3 patterns/p29-bst-delete/controls/mkspec.py --check
python3 harness/tools/table_render_inputs.py --selfref
python3 harness/tools/table_render_inputs.py --reads
sh .temp/t141/sweep.sh                      # ~1 h
```

⚠ `.temp/probe_9c/{old,new,ctl}/` contain symlinks into the real tree and a
copy of two harness files; they are rebuilt by `build_sandbox.py` and hold no
unique evidence. `.temp/t136/`, `t137/`, `t139/`, `t140/` were read and never
written.

