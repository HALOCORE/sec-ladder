# TASK_164 — the owed gate bundle: A, B, C, D, E all landed, one sweep, and the
# budget derivation had a hole in it

**Role: research engineer.** All four `check.py`/`vparse.py` items are in the
tree, both must-fire arms exist and **have been seen to fail** (nine planted
mutations, nine fired), item E is confirmed already done, and the 33-pattern
sweep is **green at the expected baseline**: `30 PASS + 3
PASS-WITH-BLOCKED-ROWS`, **0 failures**, `blocked` = `p01` 1 / `p35` 3 /
`p42` 1, all 33 `rc=0`, `0 STALE`, and the four tail scripts each exit 0.
⚠ **The sweep completed ONCE but was STARTED twice** — the first attempt reached
p27 and I then found an error in my own item-C text, which is a `check.py` edit
and invalidates every record already written. **Problems §1.**

⚠⚠ **THE ONE THING TO READ FIRST — the budget derivation missed a cost, and I
absorbed it only after measuring that it was small.** `TASK_164.md` derived
*"no item touches a `slb-contract` fence -> `contract_sha256` does not move ->
one sweep"*. That is **true and I verified it** (§7). But
**`patterns/p35-tagged-union/controls/{proof_mutants,union_oracle}.json` pin
`harness/check.py` and `harness/vparse.py` inside their own
`derived_from_sha256`** — 3 of 46 sidecars pin something under `harness/` — so
**editing `check.py` at all makes two of p35's sidecars STALE and stage 9b
`rep.fail`s p35 twice.** Measured cost: **76 s**, both generators `rc=0`, `9/9`
and `9/9` arms as designed, and a leaf diff showing **ZERO substantive numbers
moved** — only the two pin hashes and `measured_utc`. §6. **Any future
`check.py` edit owes those two re-runs; nothing in `RECAP` or the task file says
so.**

---

## Did

| item | file | what landed |
|---|---|---|
| **A** | `harness/check.py` | `control_json_verdict()` — a **pure function** — stage 9b reading it, and `_CONTROL_VERDICT_CASES`, a **17-cell must-fire arm** run by `check_selftests` on every invocation |
| **B** | `harness/vparse.py` | `axiom_decls` matches the `global` directive (`GLOBAL_KINDS`; kinds `global layout` / `global size_of` / `global`), **11 new `_selftest` cells**. `harness/check.py` partitions them out of the `verus.axioms` comparison and out of `_axiom_items`, and records them under a new gate-record key `global_decls` |
| **C** | `harness/check.py` | `check_marginal_ir`'s docstring: the **second mechanism**, its per-`(level, mode, input)` cell table re-derived from `results/gate/*.json`, the `whole`-is-not-a-null note, the widened rule, and the stale census block **re-dated and re-denominated** |
| **D** | `harness/check.py` | the `copy_from_slice` false claim struck at its third and last site in `harness/`, with the pinned vstd's actual spec, a **bulk-copy twin built and verified**, and the real reason p02 keeps the indexed one |
| **E** | — | **confirmed already fixed**, both halves. Nothing changed |
| (owed, unforeseen) | `patterns/p35-tagged-union/controls/{proof_mutants,union_oracle}.json` | regenerated, because they pin `check.py`/`vparse.py` |

Scratch and every generator: `.temp/t164/`. Nothing under `.memory/`,
`RECAP.md`, `results/SYNTHESIS.md` or `harness/tools/composition.py` was
touched. No `git add`, no `git commit`. No earlier `.temp/t*/` or `.temp/mgr*/`
was read from or written to.

---

## Evidence

### 1. Item A — stage 9b hashed a sidecar and never read its verdict

**The census first, because the disposition depends on it**
(`.temp/t164/census_sidecars.py`, `.temp/t164/keys_sidecars.py`):

```
tracked patterns/*/controls/*.json  46
  ...carrying `problems`      30   non-empty: 0
  ...carrying `summary`       5
  ...carrying `invariant`     41
  ...carrying `measured_utc`  41
  ...pinning THEMSELVES in derived_from_sha256  0
  ...pinning a .py generator                    45
  ...with NEITHER problems NOR summary          11

summary values:
  p28/proof_mutants.json: {"n": 7, "as_expected": 7}
  p29/proof_mutants.json: {"n": 10, "as_expected": 10}
  p32/proof_mutants.json: {"n": 8, "as_expected": 8}
  p34/proof_mutants.json: {"n": 6, "as_expected": 6}
  p49/proof_mutants.json: {"n": 9, "as_expected": 9}
```

**Every figure in the task file's table reproduces exactly.** One wording
correction: the task says `p25` and `p35` *"carry `summary: null`"* — they carry
**no `summary` key at all**. `doc.get("summary")` cannot tell those apart, so it
changes nothing, but the sentence is not what the files say.

**What landed.** `harness/check.py::control_json_verdict(doc)` — a pure function
of the document, no filesystem, no `rep` — returning `(verdict, [detail, ...])`
with `verdict` in `{"FAILED", "CLEAN", "NO-VERDICT"}`. Stage 9b calls it on the
**raw** parsed document (before the existing `doc if isinstance(doc, dict) else
{}` coercion, so a sidecar that is not a JSON object is reported rather than
silently emptied), inside a `try/except` that turns any exception into a
`rep.fail` rather than a crash.

**The dispositions, each decided and each justified:**

* **non-empty `problems` → `rep.fail`.** Not a judgement call: `problems` is a
  verdict because **30 of 30 generators that write it exit 1 when it is
  non-empty**.
* **`summary` with `as_expected != n` → `rep.fail`.** I fail in **both**
  directions. `as_expected < n` is the regressed battery the task names;
  `as_expected > n` is incoherent and can only be a generator bug, and calling
  it clean would be the same silence pointing the other way.
* **`problems` that is not a list → `rep.fail`**, naming the type. `[]` is the
  one spelling of *"no problems"* the tree uses, 30 of 30. A string, a number,
  `null` or a dict is a typo or a hand edit, and the failure it creates is the
  bad one: a reader sees a `problems` key and reads "reported and clean" while
  `if doc["problems"]:` in the generator would read a non-empty string as a
  **failure**.
* ⚠⚠ **a sidecar with NO verdict field → SILENT (printed, not shouted, not
  failed).** The task asked me to decide and justify, and suggested a `SHOUT`.
  **I did not take the shout, and the reason is a measurement:**

  `RENDER_INPUT_KEYS = ("contract_sha256", "controls_json", "idiom_audit",
  "loud")` (`check.py`), and `report.py::shout_section` prints a line for every
  `loud` entry **and for every `controls_json` entry whose value is not
  `"FRESH"`**:

  ```
  harness/report.py:410   unpinned = {k: v for k, v in ctl.items() if v != "FRESH"}
  harness/report.py:433   for f, verdict in sorted(unpinned.items()):
  ```

  So a `rep.shout`, **or a new verdict string for those 11 sidecars**, makes
  `results/tables/{p23,p28,p29,p32,p35}.md` stale, stage 9c FAILs on all five,
  and the bundle costs five `report.py` runs plus a **second full sweep** — for
  a stage that has found nothing. The substance agrees with the price: a
  pin-only document (`p23/controls_pin.json`) or a table of rows
  (`p29/miri_arms.json`) has no verdict to give, and the stage's own docstring
  already argues that *"a red gate nobody can clear is how gates get switched
  off"*. **Promoting it to a shout is a one-line change and the manager's call;
  it is priced above.**
* **A FAILED verdict APPENDS to the pin verdict** (`FRESH+VERDICT-FAILED`)
  rather than replacing it. Losing *"the numbers are current"* to say *"the
  numbers are bad"* trades one fact for another.

**The must-fire arm, 17 cells, in `check_selftests` on every invocation:**

```
$ python3 -c "... for label, got, want in check._CONTROL_VERDICT_CASES ..."
ok   ['FAILED', 1]      a NON-EMPTY `problems` FAILS
ok   ['FAILED', 1]      `summary` {n: 9, as_expected: 7} FAILS (the regressed battery)
ok   ['CLEAN', 0]       `summary` {n: 9, as_expected: 9} is silent
ok   ['CLEAN', 0]       `problems: []` is silent -- and it is 30 of 46 sidecars today
ok   ['FAILED', 1]      `problems` as a STRING FAILS rather than passing
ok   ['FAILED', 1]      ...an EMPTY string too -- falsy is not the same as `[]`
ok   ['FAILED', 1]      `problems` as a NUMBER FAILS
ok   ['FAILED', 1]      `problems: null` FAILS -- 'not computed' is not 'none found'
ok   ['FAILED', 1]      `summary` with non-integer counts FAILS
ok   ['FAILED', 1]      `summary` with as_expected > n FAILS (incoherent, not clean)
ok   ['FAILED', 1]      half a `summary` FAILS
ok   ['FAILED', 2]      a doc that fails BOTH ways reports BOTH
ok   ['NO-VERDICT', 0]  a sidecar with NEITHER field is NO-VERDICT, not FAILED
ok   ['NO-VERDICT', 0]  `summary: null` alone is NO-VERDICT, not a malformed summary
ok   ['NO-VERDICT', 0]  a `summary` of some OTHER shape does not silently pass
ok   ['FAILED', 1]      a sidecar that is a LIST, not an object, FAILS rather than raising
ok   ['FAILED', 1]      ...and a `None` document too
n cases: 17   mismatches: 0
```

**And the shipped tree reads clean** — 35 `CLEAN`, 11 `NO-VERDICT`, **0
`FAILED`** across all 46, so `controls_json` does not move:

```
NO-VERDICT   p23/controls_pin.json   p23/sweep_fit.json   p28/repro.json
             p29/arms.json  p29/miri_arms.json  p29/repro.json
             p32/forgeable.json  p32/repro.json  p32/storage_arms.json
             p35/proof_mutants.json  p35/union_oracle.json
{'NO-VERDICT': 11, 'CLEAN': 35}   total 46
```

⚠ **FINDING — THE TREE USES FOUR VERDICT SHAPES, NOT TWO, and four sidecars
still carry a verdict this stage cannot read.** The task said *"the two above
are what the tree uses"* and told me not to invent a third; I did not, and I am
reporting what the census actually found:

| shape | files | read by 9b now? |
|---|---|---|
| `problems: [...]` | 30 | ✅ |
| `summary: {n, as_expected}` | 5 (all `proof_mutants.json`) | ✅ |
| `arms_as_designed` / `arms_total` | `p35/proof_mutants.json` | ❌ |
| `cells_ok` / `cells_total` | `p35/union_oracle.json` | ❌ |
| `hardened_kernel_broke` (+ `exit_code`) | `p32/forgeable.json` | ❌ |
| `unstable_cells` | `p28/repro.json`, `p32/repro.json` | ❌ |

**`p35`'s two proof-mutant/oracle sidecars are the sharp case**: they are
exactly the *"regenerated at 7 of 9"* hazard the item was written for, and they
use neither convention. Their generators still exit non-zero on a failed arm
(measured, §6), so the hole is only *"a stale sidecar recording a regression"*
— but that is the hole. **Reported, not fixed: a fifth and sixth key would be a
third and fourth convention.** The cheap repair if anyone wants one is to have
those two generators also emit `summary: {n, as_expected}` beside what they
already write — that is a `controls/*.py` edit, which is in `source_sha256`, so
it costs a gate re-run and no re-measure.

⚠ **`measured_utc` (41 of 46) and `invariant` (41 of 46) are NOT wired in, as
instructed.** Re-checked after my edits:
`grep -rn 'measured_utc\|invariant' harness/*.py synthesis/*.py` has **zero
`measured_utc` hits outside the docstring I wrote**, and every `invariant` hit
is the **Verus clause keyword** in `dloop`/`vparse`/`check`'s ghost-blanking
regexes, not the sidecar key. **Both fields are still read by nothing.** An
unread timestamp is untidy, not unsound, and `derived_from_sha256` answers the
stronger question the timestamp does not (*against WHAT?*).

---

### 2. Item B — the `global` directive, and the call I was told to attack

#### 2a. The census, re-derived with the SHIPPED code

`.temp/t164/census_global_shipped.py` drives `vparse.axiom_decls` itself:

```
  global layout  p28 p29 p34   3 patterns
  global size_of p10 p19 p22 p36 p38 p46 p47   7 patterns
  union          p10 p19 p22 p28 p29 p34 p36 p38 p46 p47   10 of 33

  p10  patterns/p10-fir-stencil/verus.rs:87       kind=global size_of name=usize
  p19  patterns/p19-state-machine/verus.rs:63     kind=global size_of name=usize
  p22  patterns/p22-hash-probe/verus.rs:133       kind=global size_of name=usize
  p28  patterns/p28-intrusive-lists/verus.rs:162  kind=global layout  name=Obj
  p29  patterns/p29-bst-delete/verus.rs:135       kind=global layout  name=Rec
  p34  patterns/p34-refcount-stack/verus.rs:147   kind=global layout  name=Obj
  p36  patterns/p36-vtable-dispatch/verus.rs:90   kind=global size_of name=usize
  p38  patterns/p38-alias-pun/verus.rs:80         kind=global size_of name=usize
  p46  patterns/p46-bignum-mac/verus.rs:79        kind=global size_of name=usize
  p47  patterns/p47-ct-compare/verus.rs:98        kind=global size_of name=usize

  NEGATIVE CONTROL p32/verus.rs: raw 'global layout' substring hits 1, axiom_decls global-kind 0
  NEGATIVE CONTROL p49/verus.rs: raw 'global layout' substring hits 1, axiom_decls global-kind 0
```

**My census agrees with the manager's exactly: 3 + 7 = 10 of 33, and `p32` has
none.** The raw-`grep` census (`.temp/t164/census_global.py`) reproduces the
error for the record: it returns `p28 p29 p32 p34 p49` for `global layout` —
**five**, because p32's and p49's hits are comments *saying the pattern has
none*. (TASK_156 reported *four* because `p49` did not exist yet.)

#### 2b. ⚠⚠ THE CALL I WAS ASKED TO ATTACK — `size_of` vs `layout`

**Measured, four probes, `.temp/t164/globalprobe/`, single-file mode, no
`--cargo`, verus `0.2026.08.09.92f466f`:**

```
layout_false.rs   6-byte struct declared `size == 24`   rc=1
    verification results:: 2 verified, 0 errors
    error[E0080]: evaluation panicked: does not have the expected size
layout_true.rs    the same struct declared `size == 6`  rc=0
    verification results:: 2 verified, 0 errors
sizeof_false.rs   `global size_of usize == 4`           rc=1
    verification results:: 2 verified, 0 errors
    error[E0080]: evaluation panicked: does not have the expected size
sizeof_true.rs    `global size_of usize == 8`           rc=0
    verification results:: 2 verified, 0 errors
layout_false_unused.rs   the lie on a NEVER-CONSTRUCTED, never-mentioned type
    verification results:: 1 verified, 0 errors  THEN the same E0080, rc=1
layout_false_lib.rs      the lie with `--crate-type=lib`, no `main`
    verification results:: 1 verified, 0 errors  THEN the same E0080, rc=1
```

**Answers, in order:**

1. **Can a `global` directive prove something FALSE about the program's
   behaviour? YES.** Both probes carry `fn measured() -> (r: usize) ensures r ==
   24usize { core::mem::size_of::<S>() }` — a claim about the value the program
   computes **at run time**, not a ghost claim — and vstd specifies
   `core::mem::size_of` as `ensures u as nat == size_of::<V>()`
   (`vstd/layout.rs:78`). Verus discharges it. The claim is false: `S` is 6
   bytes.
2. **Is it only rejected at codegen? NO — it is rejected earlier than the Verus
   guide says.** `_VERUS_DOC_/guide/src/reference-global.md` states the static
   check *"only happens when codegen is run; an 'ordinary' verification pass
   will not perform this check"*. **On the pinned Verus that is too weak**:
   `E0080` is a const-eval error and it fires in a plain `./verus_run.py
   <file>` with **no `--compile`**, and in `--crate-type=lib`, and on a type
   nothing constructs. This is the half TASK_156's reviewer measured, and it
   re-derives — *stronger* than they put it.
3. **Are `layout` and `size_of` the same exposure? YES, and the manager's
   *"possibly no for risk"* does not survive contact with the run.** The two
   produce **the identical diagnostic, at the identical stage, with the
   identical exit code**. The residual difference is real but is about
   *likelihood*, not *exposure*: `global layout Obj is size == 24` is a fact
   about a project-local type that moves when the struct moves, while
   `global size_of usize == 8` is a target fact that is false only on a 32-bit
   port. **Neither can reach a running binary.**
4. ⚠⚠ **AND THE GATE ALREADY CATCHES IT — which refutes `TASK_156` minor 2's
   *"Verus itself reports `1 verified, 0 errors` on a lie, so no verify-only
   stage is protected"*.** `check.py::_verus` treats `summary parsed and errors
   == 0 and returncode != 0` as an anomaly, and stage `5e`
   (`check_verus_exit_codes`) turns it into a stage failure. Driven in-process
   over the probes (`.temp/t164/globalprobe/drive_verus.py`):

   ```
   layout_false           _verus -> verified=None errors=None  summary_suppressed=True
   layout_true            _verus -> verified=2    errors=0     summary_suppressed=False
   sizeof_false           _verus -> verified=None errors=None  summary_suppressed=True
   sizeof_true            _verus -> verified=2    errors=0     summary_suppressed=False
   layout_false_unused    _verus -> verified=None errors=None  summary_suppressed=True

   _VERUS_RC_ANOMALIES: 3
   stage 5e rep.fail count: 3
   ```

   **The net holds, and it holds inside the gate, not only in a hypothetical
   build.** `build.py::build_verus` compiling the R5 rung is a second net.
   **This is a finding, not a reason to skip the visibility fix**, and the
   visibility fix landed anyway — `axiom_decls`' own docstring says the design
   is visibility, not prohibition.

#### 2c. What landed, and the ONE deviation from the task's letter

`vparse.axiom_decls` now emits `{"kind": "global layout"|"global size_of"|
"global", "name": ..., "line": ..., "in_verus": ...}`, keyword-keyed over
`blank_noncode`'d text. `vparse.parse()` was **not** widened (the docstring's
p36 measurement still governs). `vparse.GLOBAL_KINDS` names the partition.

⚠⚠ **THE DEVIATION, AND IT IS THE DIFFERENCE BETWEEN ONE SWEEP AND TWO:**
`check.py::_check_axiom_decls` **partitions the `global` kinds OUT** of the
`verus.axioms` declared-count comparison, out of the `tcb-axiom` shout, and out
of `_axiom_items`. Two reasons, and the first decides it:

* **A `global` is not an unchecked axiom.** The other five forms are trusted
  because *nothing* checks them. This one is const-evaluated by rustc, measured
  above, and stage 5e already fails on a lie. `_axiom_items` is the set that
  **mandates Miri**, on the argument *"the axiom is ghost but the call it
  licenses is executed"* — and Miri is not the backstop for a `global`; rustc
  is. Putting them in a list captioned *"axioms that NOTHING checks"* would be
  false.
* **The cost, stated rather than hidden.** `verus.axioms` lives **inside the
  `slb-contract` fence**. Counting `global` there demands a declaration on 10
  patterns → **10 `contract_sha256` moves, 10 stale published tables, 10
  `report.py` runs and a SECOND full sweep**. That is the task's own
  stop-and-report condition. **It is a legitimate future repair and it is the
  manager's call**; what it would add over what landed is a *declared* integer
  rather than a *recorded* one.

Instead the gate **prints** them on their own line and **records** them under a
new key `verus.<src>.global_decls`. `results/synthesis.md`'s section-3 "axioms"
column is `len(axiom_decls)` and its prose says a `0` means *"this pattern's
author wrote none of their own"* — folding `global` into that key would have
moved a published column and changed what it says.

#### 2d. B's must-fire arm — 11 new cells in `vparse._selftest()`

```
ok   axiom_decls: a `global` directive is counted, with its own kind [('global layout', 'Obj'), ('global size_of', 'usize')]
ok   axiom_decls: `global layout` in a COMMENT is NOT counted (the p32/p49 error) []
ok   axiom_decls: `global` in a STRING LITERAL is not counted []
ok   axiom_decls: a `global` directive is inside verus!   [True]
ok   axiom_decls: `global` is not a `parse()` item either []
ok   axiom_decls: a truncated `global layout` is counted as `?` [('global layout', '?')]
ok   axiom_decls: a truncated `global size_of` is counted as `?` [('global size_of', '?')]
ok   axiom_decls: an UNKNOWN `global` form at item position is counted [('global', '?')]
ok   axiom_decls: a LOCAL named `global` is not a directive []
ok   GLOBAL_KINDS covers every kind this can emit for a `global` []
vparse selftest: PASS
RC=0
```

The false-positive direction is pinned as well as the false-negative one, and
the unclassified-`global` fallback is line-anchored because `global` is an item
keyword: **measured, there are ZERO code-level `global` tokens outside the two
forms across all 161 tracked `.rs`**, so the fallback is prospective.

---

### 3. ⚠ BOTH ARMS BROKEN ON PURPOSE — nine mutations, nine fired

`.temp/t164/mutate_arms.py` copies `harness/` to a scratch `mut/` dir **which it
creates and deletes itself** (so no artefact is left; re-run the script to
reproduce), plants ONE
mutation per run **with an asserted substitution count**, and re-drives the arm.
Nothing under `harness/` is modified.

```
ITEM A ARM -- `_CONTROL_VERDICT_CASES`, driven on the MUTATED module
  BASELINE (unmutated copy): 17 cells, 0 mismatching, 0 RAISED -> ARM SILENT (correct)
  A1  non-empty `problems` no longer fails            -> 2 of 17 FAIL   ARM FIRES
  A2  the `summary` count comparison is deleted       -> 3 of 17 FAIL   ARM FIRES
  A3  a non-list `problems` reads as CLEAN            -> 4 of 17 FAIL   ARM FIRES
  A4  the verdict function RAISES                     -> 17 of 17 FAIL, 17 RAISED   ARM FIRES
  A5  the non-dict guard is removed                   -> 2 of 17 FAIL,  2 RAISED   ARM FIRES

ITEM B ARM -- `vparse._selftest()`, run on the MUTATED copy
  BASELINE (unmutated copy): rc=0  ['vparse selftest: PASS']
  B1  the `global` matcher is deleted entirely        -> rc=1, 5 cells FAIL   ARM FIRES
  B2  the matcher scans TEXT, not blanked CODE        -> rc=1, 3 cells FAIL   ARM FIRES
  B3  a truncated `global layout` becomes INVISIBLE   -> rc=1, 1 cell  FAIL   ARM FIRES
  B4  the `kind` stops distinguishing layout/size_of  -> rc=1, 2 cells FAIL   ARM FIRES
```

Two of these are worth naming:

* **A4/A5 are the `RAISED` arms** (`.memory/03-measurement.md` entry 19). A
  planted `raise` and a deleted type guard both come back as
  `['RAISED', 'RuntimeError', ...]` / `['RAISED', 'AttributeError', "'list'
  object has no attribute 'get'"]` — **a three-element list that can never equal
  a two-element expectation**, so the gate REPORTS the crash at stage 0 instead
  of dying at import. That is the exact defect entry 19 records p32's mutants
  hitting, where three of four *"failed by CRASHING rather than returning the
  designed message, so the failure is loud and the DIAGNOSTIC is lost"*.
* **B2 is the `p32` error itself**, planted: make the matcher read `text`
  instead of the comment-blanked `code` and the arm fails with
  `[('global layout', 'Fake'), ...]` on a directive that lives in a comment and
  a string literal. **That mutation is precisely what produced the published
  *"four patterns"*, and the arm now catches it.**

---

### 4. Item C — the docstring knew one mechanism and there are two

`check_marginal_ir`'s docstring now carries the second mechanism, the
consequence, and a per-cell table. **Every number in it was re-derived from
`results/gate/p*.json` by `.temp/t164/r45_null.py`, not copied from entry 23.**

```
verus - unsafe, `marginal_ir_per_call`, per (level, mode, input) cell
            O0/iso            O3/iso           O0/whole          O3/whole
         small    large    small    large    small    large    small    large
p25       0.00  +269.52    0.00  +269.52    0.00  +269.52    0.00  +269.52
p28    +281.28 +1732.73    0.00    +1.01 +281.28 +1732.73  +46.02  +211.87
p29    +113.76  +425.80    0.00    -0.02 +113.76  +425.80 +101.77  +465.55
p42       0.00   -31.00    0.00   -31.00    0.00   -31.00   -2.00   -33.00
p11       0.00     0.00   -1.00    -1.00    0.00     0.00 -494.00  -166.00

-O3 ISOLATED, whole tree, 66 (pattern, input) cells over 33 patterns:
  |null| >= 2.00 in  8: p25 large +269.52 . p42 large -31.00 . p03 +6.00 (both)
                        p04 +6.00 (both) . p02 -2.00 (both)
  1.00 <= |null| < 2  35   (34 exactly -1.00; p28 large 1.01)
  |null| < 1.00       23
-O0 ISOLATED, |null| >= 2.00 in 10 of 66:
  p28 large +1732.73 . p29 large +425.80 . p28 small +281.28 . p25 large +269.52
  p29 small +113.76  . p42 large  -31.00 . p19 -6.00 (both)  . p46 -3.00 (both)
-O3 WHOLE: 37 of 66 clear 2.00 and 15 clear 20.00 -- and NONE of it is a defect,
  because `check_identity` compares `isolated` digests only and nothing pins
  them equal.
```

**Entry 23's headline figures all reproduce**: `p25 269.52` in all four cells,
`p28` `1732.73 / 1.01 / 1732.73 / 211.87`, `p29 425.80` at `-O0 iso`,
`p42 31.00`, `p11 −494.00` at `O3/whole`, and *"only p25 and p42 reach 16.00,
and FIVE patterns clear 2.00: p25 269.52 . p42 31.00 . p04 6.00 . p03 6.00 .
p02 2.00"* at `-O3 isolated` — **exact**.

⚠⚠ **FINDING — ENTRY 23's TABLE MAXES OVER *INPUT*, WHICH IS THE FOURTH
DIMENSION ITS OWN RULE FORBIDS.** The rule reads *"a null is a property of a
CELL. Do not max it over mode, over level, or over input — print the cell."* The
table under it has three axes and prints one number per `(pattern, level,
mode)`:

| entry 23 prints | the cell it is | the OTHER input |
|---|---|---|
| `p25` `269.52` in all four | `large.bin` | `small.bin` is **`0.00`** in all four |
| `p28` `1732.73` at `O0/iso` | `large.bin` | `small.bin` is **`+281.28`** |
| `p29` `425.80` at `O0/iso` | `large.bin` | `small.bin` is **`+113.76`** |
| `p42` `31.00` | `large.bin` | `small.bin` is **`0.00`** in all four |
| `p11` `−494.00` at `O3/whole` | **`small.bin`** | `large.bin` is `−166.00` |

**The conclusions are untouched** — every quoted number is right, and it is the
right (worst) input for the argument being made. **But the table has one axis
too few, and this is the same shape as the two corrections entry 23 already
records.** ⚠ `.memory/` is the manager's; I have not edited it. The
`check.py` docstring I wrote carries the four-axis table.

⚠ **Second, smaller finding: entry 23 cites `check.py:3303` for
`check_identity`'s isolated-only comparison; it is now `:3313`.** Ordinary
citation rot. **My docstring names the function and the code line's text, and
gives no line number** — `.memory/02-bench-rules.md`'s own rule.

**The stale scope line is corrected as instructed, and NOT re-taken.** The
census block now opens with its own denominator: dated `2026-08-22`, **24
patterns against a tree of 33**. Re-taking it costs ~90 minutes and nothing
here needed it. `ls -d patterns/p*/ | wc -l` → **33**.

⚠⚠ **AND I GOT THE "WHICH NINE" LIST WRONG ON THE FIRST TRY, CAUGHT IT MYSELF,
AND THE MECHANISM IS THIS TASK'S OWN LESSON.** I first wrote *"nine patterns
(p25, p27, p28, p29, p32, p34, p35, p47, p49) have never been probed"* — an
**asserted** list, reconstructed from memory of which rows are recent. It is
wrong in **both directions**, exactly like the `global layout` census this task
exists to fix: `p27` and `p47` **are** in the census, and `p23` and `p42` are
**not**. **The census artefact is still on this box and names its own
subjects**, so the list is derivable in one command:

```
$ python3 -c "... json.load(open('.temp/r98/treescan_large.json')) ..."
census patterns (24): p01 p02 p03 p04 p05 p06 p07 p08 p09 p10 p11 p12 p13 p14
                      p16 p17 p18 p19 p22 p27 p36 p38 p46 p47
tree (33):            ...
NOT in the census (9): p23 p25 p28 p29 p32 p34 p35 p42 p49
in census but not tree: []
```

**The docstring now carries the derived list, both halves of it, and says the
first version guessed.** ⚠ And the gap is not a random nine — **seven of them
are the temporal, type and aliasing rows** (`composition.py --check`: temporal
`p25 p28 p29 p32 p34`, type `p35`, aliasing `p49`), which is the half of the
tree the SECOND mechanism has its largest nulls on. That is worth more than the
count was.

⚠ **This correction is why the sweep ran twice; see §8.**

---

### 5. Item D — the `copy_from_slice` claim, and a bulk twin actually built

**The sentence is gone.** The only remaining occurrence of the string in
`harness/` or `synthesis/` is inside the retraction that replaced it:

```
$ grep -rn 'no vstd spec for `copy_from_slice`\|there is no vstd spec' harness/ synthesis/
harness/check.py:6340:    WAS THE THIRD AND WORST SITE OF IT.** It read *"there is no vstd spec for
```

(Deliberately: `RECAP`'s own lesson is *"grep for what the FIXED text would say,
not for what the broken text said"* — the correction here **replaces** the
claim and quotes it only as struck text.)

**The pinned vstd, quoted into the docstring:**

```
~/tools/verus/vstd/std_specs/slice.rs:205
pub assume_specification<T: Copy>[ <[T]>::copy_from_slice ](dst: &mut [T], src: &[T])
    requires old(dst)@.len() == src@.len(),
    ensures  final(dst)@ == src@;
```

**I checked the surrounding argument, and it did not hold — so I measured the
replacement rather than asserting one** (`.temp/t164/twinprobe/`, generators
kept, substitution counts asserted):

```
$ ./verus_run.py patterns/p02-buffer-copy/verus.rs --cfg slb_twin
rc=0   verification results:: 12 verified, 0 errors          <- shipped indexed loop

$ python3 .temp/t164/twinprobe/mk.py        # rewrites ONLY the twin's body
substitutions asserted: 1
$ ./verus_run.py .temp/t164/verus_bulk_twin.rs --cfg slb_twin
rc=0   verification results:: 11 verified, 0 errors          <- BULK-COPY TWIN

$ python3 .temp/t164/twinprobe/weaken.py    # the documented weakening attack
substitutions asserted: 2 (trusted `copy_bytes` and `slb_twin_copy_bytes`)
$ ./verus_run.py .temp/t164/verus_bulk_twin_weak.rs --cfg slb_twin
rc=1   verification results:: 10 verified, 1 errors
       error: precondition not satisfied  --> ... a.copy_from_slice(&src[from..from + n]);
       error: possible arithmetic underflow/overflow
```

**So a bulk-copy twin is not merely available, it is a working STRENGTH
ORACLE**: weaken `from + n <= src@.len()` to `... + 1` — TASK_008_REVIEW's
blocker, the attack this stage exists for — and it fires at the range slice. It
is one obligation cheaper because the `while` loop is gone. It needs the shipped
twin's own `assert(src@.len() == vstd::slice::spec_slice_len(src));` to fire
`axiom_spec_len`, or `from + n` cannot be shown not to overflow.

**Should p02 have one? Reported, not built, and the cost is a number:**
`patterns/p02-buffer-copy/spec.md:245` pins `"twin_obligations": {"verus.rs":
12}` **inside the `slb-contract` fence**, so swapping the twin moves
`contract_sha256`, stales the table and costs a `report.py` plus a second gate.
On the merits it is close to a wash, and I lean to keeping the indexed loop: it
re-derives the copy element by element rather than leaning on one more vstd
`assume_specification`, which is more independent, which is the twin's whole
job. ⚠ **What does NOT apply is the `identity` argument** — p02 keeps its
`external_body` wrapper on the SHIPPED `copy_bytes` because the verified
spelling is +9 instructions and `+5.00 Ir`/call and breaks `identity: exact`,
but a twin is `#[cfg(slb_twin)]` and no build compiles it, so it costs zero
instructions either way. **The old parenthesis blurred those two questions and
the new text separates them.**

**The `harness/` sweep the task asked for:** `check.py:6187` was the only live
site. ⚠ **And its `.memory/04-verus.md` citation was dangling**: that file now
carries only the **correction**, at `:691` (*"This paragraph used to attribute
the wrinkle to `copy_from_slice` having no vstd spec; it has one"*) and `:1149`
(*"that is false and was corrected at TASK_048"*). **`.memory/` is clean —
nothing for the manager to fix there.**

⚠ **REPORTED, NOT FIXED — five pattern-doc citations to `.memory/04-verus.md:133`
and `:813` are now stale**, because `.memory/04-verus.md` was corrected in
place and those line numbers moved:

```
patterns/p02-buffer-copy/NOTES.md:691   "...and `.memory/04-verus.md:133` and `:813` STILL SAY"
patterns/p06-rotate/README.md:108       "`.memory/04-verus.md:133` and `:813` are false in both halves"
patterns/p06-rotate/NOTES.md:904        "...is the sentence `:133` and `:813` should carry"
patterns/p06-rotate/verus.rs:436        "...against what `.memory/04-verus.md:133` and"
patterns/p06-rotate/spec.md:446         INSIDE the `slb-contract` fence
```

`:133` now reads *"An `external_body` item need not contain `unsafe`"* and
`:813` is about the per-conjunct fix; neither says what the five citations say
they say, and **p02's "still say" is simply false today.** ⚠ Four are cheap
(`NOTES.md`/`README.md` = gate re-run; `verus.rs` = **re-measure**), but the
fifth is inside p06's contract fence and costs a `contract_sha256` move. **Not
in this task's scope; bundle with the next thing that re-gates p02 and p06.**

---

### 5b. Item E — CONFIRMED already done, both halves

**Half 1 — the sentence is fixed.** `patterns/p01-array-sum/spec.md:82` reads:

```
| `identity` | recorded as a **result** *and* enforced. A level at or above the
one pinned here is a result; a *drop below it* calls `rep.fail` and the run's
verdict is **FAIL** ... ⚠ This row read *"recorded as a **result**, not a gate
condition"* until TASK_084. That was retracted in `check.py` at TASK_028 and
this was the last copy of it in any `patterns/*/spec.md` (TASK_083_REVIEW A3). |
```

**Half 2 — it is outside the fence, so it never cost a `contract_sha256`
move.** Derived by brace-matching the fence rather than eyeballed:

```
$ python3 -c "... re.search(r'\`\`\`slb-contract\s*\n(.*?)\`\`\`', t, re.S) ..."
p01 fence spans lines 85 .. 196
identity row at line 82 -> inside fence: False
```

⚠⚠ **AND THE QUEUE ITEM IS ITSELF AN INSTANCE OF THE TRAP RECORDED DIRECTLY
ABOVE IT.** `RECAP`'s retired item says *"a naive `grep` for the substring
`recorded as a result` STILL HITS the corrected line, because the correction
APPENDED rather than replaced"*, and then the very next paragraph — the
*"Adjacent and NOT fixed"* note — was written from exactly such a grep: the
struck phrase survives **only inside the row's own retraction sentence**
(*"⚠ This row read `recorded as a result, not a gate condition` until
TASK_084"*). **The item that records the trap was scheduled by the trap.**
✅ **Retire it.** Nothing changed in `patterns/p01-array-sum/`.

---

### 6. ⚠⚠ THE UNFORESEEN COST — p35's sidecars pin `harness/check.py`

Driving stage 9b over every pattern immediately after the edits:

```
== 9b. controls/*.json staleness pins AND verdicts ===
FAIL [tables] patterns/p35-tagged-union/controls/proof_mutants.json is STALE:
              1 of 4 pinned source(s) moved under it (['harness/check.py'])
FAIL [tables] patterns/p35-tagged-union/controls/union_oracle.json is STALE:
              2 of 5 pinned source(s) moved under it (['harness/check.py',
              'harness/vparse.py'])
TOTAL fails=2 shouts=0
```

**Which sidecars pin anything under `harness/` — 3 of 46:**

```
p23/controls/sweep_fit.json:    ['harness/asm.py', 'harness/build.py', 'harness/measure.py']
p35/controls/proof_mutants.json:['harness/check.py']
p35/controls/union_oracle.json: ['harness/check.py', 'harness/vparse.py']
```

p23's pins none of what I touched, so it stayed FRESH. **p35's two had to be
regenerated, and I did it twice** — once after freezing the first round of
edits, and again after the item-C list correction (§4), because that was
another `check.py` edit. Both generators check their own arms and exit non-zero
on a regression, and both passed on every run:

```
$ python3 patterns/p35-tagged-union/controls/union_oracle.py
9/9 cell(s) as designed     UNION_ORACLE_RC=0        (~4 s)
$ python3 patterns/p35-tagged-union/controls/proof_mutants.py
9/9 arm(s) as designed      PROOF_MUTANTS_RC=0       (~72 s)
```

**And stage 9b over p35, after the final regeneration:**

```
{'detectors.json': 'FRESH', 'proof_mutants.json': 'FRESH', 'rust_bug.json': 'FRESH',
 'safety_line.json': 'FRESH', 'union_oracle.json': 'FRESH'}
fails: 0
```

**And a leaf diff against the pre-run snapshot (`.temp/t164/p35sidecar/`,
`.temp/t164/sidecar_diff.py`) — this is the negative control that says my
`check.py` edits changed nothing those batteries measure:**

```
proof_mutants.json: leaves before=53 after=53 added=[] removed=[] MOVED=2
    .derived_from_sha256.harness/check.py   703f0aa2… -> 60aba3e5…
    .measured_utc                            2026-08-31T09:30:56Z -> 2026-09-02T02:45:58Z
union_oracle.json:  leaves before=38 after=38 added=[] removed=[] MOVED=3
    .derived_from_sha256.harness/check.py   703f0aa2… -> 60aba3e5…
    .derived_from_sha256.harness/vparse.py  de1f4db8… -> 0922b5ad…
    .measured_utc                            2026-08-31T09:31:05Z -> 2026-09-02T02:45:36Z
```

**`60aba3e5…` and `0922b5ad…` are the FINAL `check.py` and `vparse.py`** — the
same hashes `synthesis/licence.json` records for all 33 patterns, so the pins
and the gate agree.

**ZERO substantive leaves moved.** The two sidecars are `.json`, which the gate
digest deliberately excludes, so there is no fixpoint and `controls_json` is
back to all-`FRESH`.

---

### 7. The budget premise, checked rather than trusted

```
$ grep -n 'contract_sha256' <every file I edited>
harness/check.py, harness/vparse.py         -- no `slb-contract` fence touched
patterns/*/spec.md                          -- UNMODIFIED (git status, §9)
```

`git status --short` shows **no `patterns/*/spec.md` modified**, so no
`contract_sha256` moved, `results/tables/*.md` did not go stale, and no
`report.py` run was needed. ✅ **The task's derivation was correct on
`contract_sha256`; it was incomplete on `controls/*.json`.**

`harness/measure.py::measurement_sources` does not include `check.py` or
`vparse.py`, so **zero re-measures** — confirmed by `--check-stale` in §8.

---

### 8. The runs

**The 33-pattern sweep, once, fully detached** (`.temp/t164/sweep.sh`, one log
per pattern under `.temp/t164/sweep/`, `02:46:08Z → 04:42:51Z`, **1 h 57 m**).
⚠ `p28` alone took **36 minutes** (`03:32:55 → 04:09:12`), which is the
`TASK_149` figure and not a hang.

**Every pattern's own exit status, recorded per pattern, not a pipeline's:**

```
$ awk '$2!=0 {print "NONZERO:", $0} END {print "patterns run:", NR}' .temp/t164/sweep/rc.txt
patterns run: 33            <- and NO "NONZERO:" line
```

**Verdicts read out of the RECORDS** (`.temp/t164/read_records.py`; never
grepped — `grep -c BLOCKED` matches `PASS-WITH-BLOCKED-ROWS` and decodes as
`2N+1`, and `grep -oE 'PASS|FAIL'` reports it as `PASS`):

```
records: 33   verdicts: {'PASS-WITH-BLOCKED-ROWS': 3, 'PASS': 30}
failures: 0   blocked: 5
blocked per pattern: {'p01': 1, 'p35': 3, 'p42': 1}
global_decls per pattern (non-zero only):
  {'p10': 1, 'p19': 1, 'p22': 1, 'p28': 1, 'p29': 1,
   'p34': 1, 'p36': 1, 'p38': 1, 'p46': 1, 'p47': 1}
```

✅ **Exactly the expected baseline**: `30 PASS + 3 PASS-WITH-BLOCKED-ROWS`, 0
failures, `p01` 1 / `p35` 3 / `p42` 1. (`p42`'s stayed at 1; the task allowed 2.)
✅ **And the `global` census now reproduces FROM THE GATE RECORDS** — 10
patterns, one directive each, exactly the set §2a derived: `p10 p19 p22 p28 p29
p34 p36 p38 p46 p47`. **`p32` records zero, which is the whole point.**

**The tail, each script's OWN exit status, no `&&` chains, no `echo`, no pipes:**

```
MEASURE_CHECK_STALE_RC=0     66 record(s) examined, 0 STALE
COMPOSITION_RC=0             OK: published composition table matches the tree
                             (33 patterns, 10 classes)
TEMP_CITATIONS_RC=0          temp_citations.py: OK (new=0 unclassified=0 resolved=4)
LICENCE_RC=0                 wrote synthesis/licence.json: 33 patterns,
                             132 pair verdicts (LICENSED, NOT-LIC, UNDEC)
SYNTHESIZE_RC=0              wrote results/synthesis.md (92856 bytes, 705 lines)
```

⚠ **`--check-stale` prints `66 record(s) examined` — GATE PLUS MEASUREMENT (33
+ 33), not 66 measurement records.** A commit message has already misread that.
**Zero re-measures were needed and none was run.**

**What the two regenerated publications moved — both are negative controls:**

* **`results/synthesis.md`: 4 lines, all `p08`, all in hundredths.**

  ```
  - | p08 | ... **small +10956.00** (-120.00) / **large +91057.02** (-883.98) |
  + | p08 | ... **small +10956.02** (-119.98) / **large +91057.00** (-884.00) |
  - | p08 | ... **small -2427.74** (-4152.74) / ...
  + | p08 | ... **small -2427.82** (-4152.82) / ...
  ```

  ⚠⚠ **That is the FIRST mechanism in item C's own docstring, arriving
  unprompted**: *"p08's work is a heap `memmove`, which is why p08 moves in
  hundredths"*, and *"if p08's 12 cells move by a few hundredths between gate
  runs, that is this effect and not a code change"*. **The docstring predicted
  the only thing that moved.**
  ✅ **And section 3's `axioms` column did NOT move on any of the 33 rows** —
  which is exactly what the `global_decls` partition (§2c) was for.
* **`synthesis/licence.json`: 2886 leaves, 66 moved, ALL of them
  `gate_source_sha256.harness/{check,vparse}.py`** (33 patterns × 2 files).
  **ZERO licence verdicts moved.**

**Final `git status --short`** — 2 harness files, p35's 2 sidecars, the 33 gate
records the sweep rewrote, the 2 regenerated publications, and this report.
**No `patterns/*/spec.md`. No `results/tables/*.md`. No `results/p*.json`.**

---

### 9. Clean negatives — named attacks that did NOT land, so nobody re-runs them

1. **`p32` really does not have a `global layout`.** Re-derived independently
   with `blank_noncode`: the raw substring hits at `p32/verus.rs:17` and
   `p49/verus.rs:29` are `//!` doc comments listing what the pattern has **no**
   of. The manager's self-refutation stands; **my census agrees with the
   manager's exactly (3 + 7 = 10 of 33).**
2. **`global size_of` is NOT a different exposure from `global layout`.** I
   tried to make it one and could not: same diagnostic, same stage, same exit
   code, on four probes. The manager's *"possibly no for risk"* does not
   survive.
3. **I could not make a false `global` reach a running binary.** Never
   constructed, `--crate-type=lib`, verify-only — the `E0080` fires in all
   three. **The net holds.**
4. **`.memory/04-verus.md` does NOT still carry the `copy_from_slice` false
   claim.** The task asked me to check and report if it did. It does not: both
   surviving mentions are the correction. **Nothing for the manager there.**
5. **Entry 23's numbers all reproduce on the 33-pattern tree.** I went looking
   for a fourth error in that table (it has had three) and the only thing I
   found is the missing INPUT axis; every printed figure is right.
6. **My `check.py`/`vparse.py` edits changed nothing p35's control batteries
   measure** — 9/9 and 9/9 on every re-run, zero substantive leaves moved.
7. **No new `.temp/` citation needs classifying.** `temp_citations.py` rc=0,
   `new=0 unclassified=0`, despite ~12 new `.temp/t164/` citations in the two
   edited files — they all exist on this box.
8. **I did NOT attempt to widen `vparse.parse()`.** The docstring's TASK_082
   measurement (p36 goes to six FAILs) governs and I took it as read rather
   than re-deriving it; keyword-keyed detection was the instruction and it is
   what landed.
9. **Exposure for item A really is zero.** I ran the new verdict read over all
   46 shipped sidecars looking for a live firing and there is none — 35 CLEAN,
   11 NO-VERDICT, 0 FAILED. **That is why the arm, not the sweep, is the
   evidence.**

---

## Problems

1. ⚠⚠ **THE SWEEP RAN TWICE, AND THE BUDGET SAID ONCE. I am reporting it as an
   overrun rather than hiding it.** The first sweep reached **p27 (22 of 33,
   all `rc=0`)** and was then killed by the agent harness, not by me — and in
   the same window I found the item-C list error (§4). Fixing it is a
   `check.py` edit, which stales every record already written (`RECAP` queue
   item 26 says so in terms), so the 22 records were invalid regardless. **I
   chose to correct the docstring and re-sweep from scratch rather than ship a
   list I knew was wrong.** The second sweep is the one reported in §8. ⚠ **The
   cost is wall clock only**: no `contract_sha256` moved, no published table
   went stale, no `report.py` ran and no re-measure was needed, so this does
   **not** hit the task's stop-and-report condition. ✅ **The process lesson is
   the useful part: the "one sweep" budget is only safe if EVERY `check.py`
   edit is frozen first, and a docstring whose numbers you have not yet
   re-derived is not frozen.**
2. ⚠ **The budget derivation in `TASK_164.md` was incomplete** — it accounted
   for gate records and measurement records and not for `controls/*.json` pins.
   §6. Small, bounded, measured, absorbed.
3. **`.temp/t164/p01.log` from the pre-sweep single-pattern run is not usable
   evidence**: two `check.py p01` runs overlapped on it (a detached
   `( … ) &` job I believed dead was still alive), so the file interleaves two
   runs. **Nothing in this report is read from it** — p01's verdict comes from
   the sweep record. The gate itself was unharmed (both runs were the same
   code and the sweep re-gated p01 afterwards), and no other pattern was
   affected.
4. **`temp_citations.py` reports 4 baseline entries "NO LONGER DANGLING"**
   (`.temp/p49ctl/{detectors,rust_bug,safe_arms,spellings}`). It says *"Not a
   failure"* and exits 0. **This is pre-existing, not mine** — those
   directories exist on the box from `TASK_163` and I ran none of p49's
   generators. **I did not run `--update`**, because the baseline is a
   committed artefact the manager owns.

## Unsure / not done

1. **I did not promote the no-verdict sidecar to a `SHOUT`.** It is one line
   and I priced it (§1): five patterns' tables go stale, five `report.py`
   runs, a second sweep. **If the manager wants it, it should be bundled with
   the next thing that re-gates — not taken now.**
2. **I did not read the four bespoke verdict shapes** (`arms_as_designed`,
   `cells_ok`, `hardened_kernel_broke`, `unstable_cells`). The task forbade a
   third convention and I obeyed. **The better repair is on the generator side
   — have `p35`'s two emit `summary: {n, as_expected}` beside what they already
   write — which is a `controls/*.py` edit, so a gate re-run and no
   re-measure.** I did not do it because it edits two patterns' controls, which
   is outside a `check.py` bundle.
3. **`global` directives are recorded but not DECLARED.** The stronger repair —
   counting them in `verus.axioms` so an author must declare one — is priced in
   §2c at 10 `contract_sha256` moves and a second sweep. **I believe the
   partition is also substantively right** (rustc checks them, and stage 5e
   already fails on a lie), **but the manager may disagree and it is a
   one-line change to reverse.** This is the call in this report I am least
   sure of.
4. **I did not re-take the ±7 environment census** (~90 min, explicitly out of
   scope). The docstring now says honestly what it covers and what it does not.
5. **I did not fix the five stale `.memory/04-verus.md:133 / :813` citations**
   in p02's and p06's docs (§5); one is inside p06's contract fence.
6. **`p02`'s bulk-copy twin is measured and not built** (§5). I lean to keeping
   the indexed loop, but that is a judgement, not a measurement — the
   measurement says both work and both are strength oracles.
7. **I did not verify the TASK_082 `parse()`-widening measurement** (p36 → six
   FAILs); I took the docstring's word for it, as instructed.
8. **`RECAP` rule-2 running count: launched from 925.** With this report,
   **926** — one manager claim refuted here (*"`global size_of` is possibly a
   different RISK from `global layout`"* — measured identical), plus the
   `TASK_156` minor-2 refutation (*"no verify-only stage is protected"*) and
   the entry-23 INPUT-axis finding, which are refutations of published text
   rather than of this task file. ⚠ **Reconciliation across branches is the
   manager's job; I have carried it forward by one and named what it counts.**

## Memory updates

**I wrote nothing into `.memory/`** (forbidden). Every durable fact learned went
into the code that owns it — `vparse.axiom_decls`' docstring, `check.py`'s
`control_json_verdict`, `check_control_json_pins`, `check_marginal_ir` and
`check_trusted_twins` docstrings — all of which are hashed into
`source_sha256`. **What the manager should consider landing in `.memory/`:**

| file | what |
|---|---|
| `.memory/03-measurement.md` **entry 23** | ⚠ **its table maxes over INPUT**, the fourth dimension its own rule forbids. §4 has the five affected rows and the per-input values. The conclusions all stand. |
| `.memory/03-measurement.md` **entry 23** | its `check.py:3303` citation for `check_identity` is now `:3313`. Ordinary rot. |
| `.memory/05-layout.md` (digest section) **or** `03` | ⚠⚠ **NEW, and nothing records it: a `harness/check.py` edit stales `patterns/p35-tagged-union/controls/{proof_mutants,union_oracle}.json`, because 3 of 46 sidecars pin files under `harness/` in their own `derived_from_sha256`.** The "a `check.py` edit costs a re-gate and no re-measure" rule is true and **not the whole cost**. §6. |
| `.memory/04-verus.md` | ⚠ **the `global` directive measurement**: Verus reports `N verified, 0 errors` on a FALSE `global layout` **and** a FALSE `global size_of`; rustc's `error[E0080]` fires in a **verify-only** run, on a **never-constructed** type, and in `--crate-type=lib`; the Verus guide's *"only happens when codegen is run"* is too weak on the pinned build; and `check.py`'s stage `5e` already fails the gate on it. §2b. |
| `.memory/02-bench-rules.md` **or** `05` | the `controls/*.json` verdict conventions: `problems` (30), `summary {n, as_expected}` (5), and **four bespoke shapes on five files that nothing reads**. §1. |
| `RECAP.md` **Immediate queue** | **retire item 26** (the `copy_from_slice` third site — fixed, §5) and **item 30** (the `check_marginal_ir` docstring — fixed, §4), and **retire item 30's "Adjacent and NOT fixed" p01 note** (already done before this task, §*Item E*). |
| `RECAP.md` findings | the `global` census as a **10 of 33** figure with the `p32` correction, and the `TASK_156` minor-2 refutation. |
| `../LearnVeri/PITFALLS.md` | the `global`-directive pitfall belongs there, but **`../LearnVeri/` is another project's repository and read-only**, so it is reported here and not written. |
