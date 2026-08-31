# TASK_148 — build `p35`, the TYPE axis's second row. Report

**Role: research engineer.** `patterns/p35-tagged-union/` is built, gated and
measured. ⚠ **The verdict is `PASS-WITH-BLOCKED-ROWS` with `blocked == 3`, and
that is a DESIGN OUTCOME rather than a defect** — it is the row's R5 result, it
is measured from both sides in `controls/union_oracle.py`, and §3 is the whole
of the argument. **The tree therefore goes to THREE blocked patterns** (`p01 =
1`, `p42 = 1`, `p35 = 3`), which the manager needs to know before reading the
next sweep's summary line.

Files added — this pattern and nothing else. **No `harness/` file, no
`.memory/`, no `RECAP.md`, no `results/SYNTHESIS.md`, no `git add`, no
`git commit`.**

```
patterns/p35-tagged-union/
  c/{kernel.h,kernel.c,kernel_hardened.c,main.c}
  safe_naive.rs  safe_tuned.rs  unsafe.rs  verus.rs
  model.py  spec.md  NOTES.md  README.md
  inputs/gen.py
  controls/{safety_line.py,detectors.py,union_oracle.py,proof_mutants.py,
            rust_bug.py, ctl_asan.c,ctl_ubsan.c,
            arm_unsafe_bug.rs,arm_safe_bug.rs}  + five .json sidecars
results/p35-tagged-union.json          (measure.py)
results/tables/p35-tagged-union.md     (report.py)
results/gate/p35-tagged-union.json     (check.py)
```

---

## 0. The two things `TASK_148.md` was written before, both handled

1. **Stage `7h`.** `c/kernel_hardened.c` is clean under ASan+UBSan on **every**
   input, adversarial included — the gate says so, and
   `controls/detectors.py` re-measures it across **five** build lines instead of
   the gate's one (`plain`, gcc ASan, gcc UBSan, clang, clang ASan): **0
   firings, and R1h's stdout equals `model.py`'s on 8 inputs × 5 build lines =
   40 cells.** No firing to report.
2. **`assume(` / `admit(`.** Neither appears in any shipped rung; `spec.md`
   declares no `verus.assumptions`. ⚠ `controls/proof_mutants.py` arm `M5`
   plants `assume(false);` and shows it verifying at the shipped obligation
   count (`16 verified, 0 errors`), and arm `M5b` drives **the real
   `check._assume_keyword_hits`** over the same text: `{'assume(': [513]}` on
   the mutant, `{}` on the shipped file, `verus.assumptions = 0` in `spec.md`.
   **So `TASK_151`'s repair is shown catching the file this row's own battery
   verifies.**

---

## 1. What was built, and the C-side result

`.temp/t143/p35/{k.c,body.inc}` and `.temp/mgr147/` were promoted, not
re-derived. The C mechanism is unchanged: a tag beside a
`union { uint64_t i; double d; uint8_t *p; }`, a store with a failure path, and
`c/kernel.c` publishing the tag before the payload lands.

**The safety line is a pure REORDER, re-measured on the SHIPPED files**
(`controls/safety_line.py`):

```
  preprocessed kernel.c          230 line(s)
  preprocessed kernel_hardened.c 230 line(s)
  diff  +2 / -2
    - cells[idx].tag = 2;      - cells[idx].tag = 3;
    + cells[idx].tag = 2;      + cells[idx].tag = 3;
```

⚠ **`+2 / −2` and `multiset_equal` are BLIND to a swap** — both files have the
same lines — so the control also checks positionally (in `kernel.c` each moved
store is immediately followed by `if (navail > 0)`; in `kernel_hardened.c` each
is immediately preceded by a payload store) **and has a must-fire arm for that
half**: `--selftest` feeds the two files the other way round, `3/3 cells as
designed`, with the line-count half shown to be blind to the same swap.

**Behaviour, all eight inputs, both C rungs, five build lines**
(`controls/detectors.py`): benign identical; `adversarial-dbl-confusion` and
`-exhaust` **silent wrong value** everywhere; `adversarial-ptr-confusion` and
`-ptr-deep` **SIGSEGV**, ASan reports (gcc and clang), **UBSan reports nothing**.

### ⚠ The control the demonstration lacked — repaired, and the repair is a pair

`ctl_asan.c` (a wild dereference) and `ctl_ubsan.c` (signed integer overflow).
The measured rows, with the ASan control's *failure* recorded rather than
hidden, because it is the evidence for the rule:

```
  ctl_asan.c   asan  rc=1   hits=5   AddressSanitizer:DEADLYSIGNAL
  ctl_asan.c   ubsan rc=-11 hits=0   <- DOES NOT FIRE
  ctl_ubsan.c  ubsan rc=0   hits=1   runtime error: signed integer overflow
  ctl_ubsan.c  plain rc=0   hits=0
```

**A positive control licenses only the detector it fires in.** The control also
ASSERTS that `ctl_asan.c` does not fire under UBSan, so a future
`-fsanitize=undefined` that gained a wild-pointer check would surface here
rather than quietly making the second control redundant.

---

## 2. `model.py` — the representability question, decided FIRST

**Written down before any cell was built** (`.temp/t148/NOTES.md`, and repeated
in `patterns/p35-tagged-union/NOTES.md` §9):

> **A Python model has no unions.** A `(tag, payload)` pair cannot reinterpret
> one object's storage at a second type, so p35's HARM is unrepresentable by
> construction. What IS representable — and is not a tautology — is the
> **TRIGGER**: `TaggedCell` keeps `tag` and `kind` as two separate facts, so
> `tag != kind` is a state the model can reach, and it reaches it exactly when
> the safety line is absent and the budget is exhausted.

So `sanitizer_expect` is **split and says so in its own docstring**: DERIVED
down to the trigger (which type was confused), DECLARED for the one step from
trigger to detector verdict — and the declared half is licensed by
`controls/detectors.py`'s two positive controls.

⚠ **The derivation has a must-fire arm in both directions, on both probes**, and
`selfcheck()` runs it on every input on every gate invocation:

```
_sim_window(_PROBE_PTR, harden=True)  -> (917327355, None)   safety line PRESENT
_sim_window(_PROBE_PTR, harden=False) -> (None, 2)           ABSENT -> PTR confusion
_sim_window(_PROBE_DBL, harden=False) -> (None, 3)           ABSENT -> DBL confusion
detector_selftest() -> []
```

⚠ **A cell that raises is reported as a failed cell with its exception text**,
never allowed to crash — `TASK_151_REPORT` §5's owed correction to `p32`, applied
here where it was free.

**Not transliterated:** implementation 1 is mutable objects with identity and an
exception at the read site; implementation 2 is two parallel sequences stepped
by a pure function mirroring `verus.rs`'s `run`, with no confusion detection at
all. `selfcheck()` runs them against each other.

---

## 3. ⚠⚠⚠ THE R5 RESULT, AND THE THREE BLOCKED ROWS

**Verus supports the Rust `union` natively.** The correct-variant obligation is
first class in the type system, checked **at the operation**:
`error: requirement not met: to access this field, the union must be in the
correct variant`. ⚠ It is a **language builtin, not a vstd spec** — a
`std_specs/` grep misses it, exactly as the task file warned.

But a union read is spelled `unsafe { p.i }` whether or not Verus checks it, and
`_scan_unsafe_sites` requires every `unsafe` token to sit inside an
`#[verifier::external_body]` body. **Wrapping the read is what moves it out of
the region Verus checks and into an axiom** — and the wrapper, being trusted,
owes a twin that cannot be written, because Rust has no safe spelling of a union
read at all.

`controls/union_oracle.py`, **9 cells, 9 as designed**, every claim with a
must-fail arm and the gate's own predicate executed rather than read:

```
  ok   A1  SHIPPED: read wrapped in external_body VERIFIES        2 verified, 0 errors
  ok   A2  ...delete the CALL SITE's tag test -> must FAIL        1 verified, 1 errors
             error: precondition not satisfied
  ok   B1  REFUSED: read left in VERIFIED code VERIFIES           2 verified, 0 errors
  ok   B2  ...delete `requires *p is i` -> must FAIL AT THE READ  1 verified, 1 errors
             error: requirement not met: to access this field, the union must
                    be in the correct variant
  ok   G-A `check._scan_unsafe_sites` on A -> 0 failures          {'failures': 0}
  ok   G-B `check._scan_unsafe_sites` on B -> >= 1 failure        {'failures': 1}
  ok   E-index / E-get_unchecked / E-deref  safe union read       error[E0133] x3
```

> **THE CONFIGURATION THE GATE REFUSES IS THE STRONGER ONE.** In B the prover
> checks the variant at the read and there is no axiom. In A — what ships — the
> obligation survives as the wrapper's `requires`, which Verus checks at every
> call site, and what is axiomatised is that the body reads the member its name
> says.

**I shipped A and made the gap the finding** (`p42`'s precedent). ⚠ **I did NOT
ship the `include!` configuration**, and I did not need to: `TASK_134`'s
correction 1 is confirmed — but **at `check.py:3972`, not the `3941` that cell
cites**: a line citation that has decayed by 31 lines, which is the rot class
this project already has a rule for. The line reads
`cand += _include_literals(txt)[0]`, so `_path_includes` resolves `include!` and
that route is closed at HEAD. **I did not verify it by execution** (it was not
needed for the build); the cell-level claim stands on reading, as `TASK_134` left
it.

**⚠ I did not change `check.py` and I am not proposing a specific change.** The
case, stated once for the manager to decide: `_scan_unsafe_sites` is keyed on the
`unsafe` TOKEN, and for `get_unchecked` that is exactly right because Verus
cannot see the operation. For a **union field read** Verus *can* see it, and the
rule therefore forces the weaker of two available proofs. Whether that is worth a
29-pattern re-gate is a judgement about the whole tree, not about this row.

### What the shipped proof DOES force — `controls/proof_mutants.py`, 8/8

| arm | result |
|---|---|
| `M0-unmutated` | `16 verified, 0 errors` |
| `M1-drop-tag-test` | **FAILS** `precondition not satisfied` |
| `M2-bug-order-exec` (R1's bug in R5) | **FAILS** `assertion failed` at `st_out =~= step(...)` |
| `M3-bug-order-both` (**the spec-weaken arm**) | **FAILS** `invariant not satisfied at end of loop body`, naming **`wf_cells`** |
| `M6-weaken-invariant` (`wf_cell` → `true`) | **FAILS** `precondition not satisfied` |
| `M4-constant-body` | **FAILS** `postcondition not satisfied` |
| `M5-assume-false` | ⚠ **VERIFIES** `16/0` |
| `M5b-gate-sees-it` | `check._assume_keyword_hits` = `{'assume(': [513]}`; shipped `{}`; declared `0` |

⚠⚠ **M3 IS THE OPPOSITE OF `p32`'s ANSWER AND IT IS THE ROW'S SHARPEST R5
RESULT.** `p32`'s spec-weaken arm VERIFIES `15/0` — nothing forces its safety
conjunct. **p35's does not**, and M6 says why: with the invariant itself weakened
to `true` the proof still fails, at the union read's own `requires`. **The
correct-variant obligation is imposed by the type system at the operation and
cannot be specified away.** First row in this tree where the safety line is
forced by something other than the postcondition.

⚠ **Two of my predictions in that battery were WRONG about the diagnostic and
right about the outcome, and they are corrected in the control's own docstring
rather than quietly refitted.** M2 and M3 were written expecting `precondition
not satisfied`.

---

## 4. Evidence — the gate, the measurement, the numbers

### `harness/check.py p35` — the final run, read out of the RECORD

```
$ python3 -c "import json; d=json.load(open('results/gate/p35-tagged-union.json')); ..."
verdict: PASS-WITH-BLOCKED-ROWS | failures: 0 | blocked: 3 | loud: 6
contract_sha256: e8e7199af62d589d4e709cba9ffcd99f4aefd23c98bb56efd0e1902f337b73ba
controls_json: all five FRESH        table_render: FRESH
7h rows: 8   fired: 0                miri runs: 8   ub: 0
verus obligations: 16                (twin configuration: 20)
```

⚠ **`verdict` and `blocked` are read out of `results/gate/p35-tagged-union.json`,
never grepped out of the log** (`.memory/03-measurement.md` entries 21–22).
⚠⚠ **`contract_sha256` MOVED, ONCE, AND THE MOVE IS THE POINT OF §6.** It was
`141fb37c…` as first written (recorded in `.temp/t148/NOTES.md` before any cell
was built) and ships as `e8e7199a…`, because PROTOCOL rule 6's ADDED STEP fired:
two clauses of the hashed `idiom.why` were refuted by this pattern's own
controls. Both are corrected with the original struck and visible, **nothing the
gate PINS moved**, and `NOTES.md` 11 is the disclosure. ⚠
`harness/tools/contract_diff.py p35` cannot help and says so — *"not present at
HEAD (a pattern added since?)"* — because the pattern lands in one commit; the
two hashes are the evidence.

Stage by stage, from the log:

```
 2  checksum      small/large/degenerate: all 32 of 32 cells that exited 0 agree
 3b marginal Ir   64 cell/probe pairs, all above the floor; tightest margin 49.7x
 3c identity      unsafe vs verus  O0: norel   O3: exact  (md5_raw equal=True)
 5c clause del.   8 `ensures` conjunct(s) deleted, n=8>0, all load-bearing
                  + 1 reachability probe: `assert(false)` at the call site unprovable
 5c-req           11 `requires` conjunct(s) probed, none a tautology
 5c-twin          4 twin(s) for 7 trusted item(s); 3 justified away and BLOCKED
 5d               760 kernel call(s) across 8 input(s), `requires` evaluated on
                  all of them, `ensures` re-derived independently on 544
 6  driver        5 driver loops all normalise to the pinned 12-statement sequence
 7  sanitizers    ptr-confusion + ptr-deep FIRE as declared; everything else clean
 7h R1h           clean on all 8 input(s), adversarial included
 8  miri          unsafe.rs: no UB on any of 8 inputs, exit and stdout match the model
 9/9b/9c          table FRESH; five controls/*.json FRESH; render FRESH
```

**Adjacent checks, all run after the gate:**

```
$ harness/measure.py --check-stale        60 record(s) examined, 0 STALE
$ harness/tools/temp_citations.py         OK  (new=0 unclassified=0 resolved=1)
$ harness/tools/composition.py --check    FAIL: built but unclassified: ['p35']   <- the check working, §7
$ git status --porcelain                  5 lines, all `??`: nothing modified anywhere
```

⚠ **`temp_citations.py` reads `git ls-files`, so it does NOT yet see p35's own
citations** — they arrive with the commit. I checked them by hand instead:
every `.temp/` path cited by a p35 file exists on this box, including the four
`controls/union_oracle.json` records by relative path. See §5's masking note for
why there are only four.

### It took SEVEN full gate runs (plus one `--no-build` diagnostic), and NONE of the six re-runs was a defect in the row

```
 1  FAIL [tables]   no results/tables/p35-*.md yet -- stage 9's known lag
 2  PASS-WITH-BLOCKED-ROWS
 3  PASS-WITH-BLOCKED-ROWS   after masking the controls' diagnostics
 4  PASS-WITH-BLOCKED-ROWS   after three batched doc fixes
 5  PASS-WITH-BLOCKED-ROWS   after renumbering NOTES.md section 6
 6  FAIL [tables]   the contract MOVED, so the table's citation went stale
 7  PASS-WITH-BLOCKED-ROWS   final
```

Two of the six are stage 9/9c's one-run lag, which is documented behaviour and
which `README.md` now spells out; the other four are my own edits, each below.

1. **`FAIL [tables]`** — `results/tables/p35-tagged-union.md` did not exist, then
   cited no `contract_sha256`. That is stage 9c's known one-run lag: `report.py`
   renders from the gate record, so on a brand-new pattern the loop is
   **`measure.py` → `report.py` → gate → `report.py` → gate**. Cleared; the
   pattern's `README.md` now spells that order out.
2. **`source_sha256` moved** when I patched the five controls to mask
   diagnostics (§5's masking note). Re-run, clean, `PASS-WITH-BLOCKED-ROWS`.
3. **`source_sha256` moved again** for a batch of THREE doc fixes, deliberately
   taken in ONE pass (PROTOCOL rule 6: batch doc fixes rather than avoid them).
   ⚠ **One of the three is a correction to this report**: §4's proof-domain line
   said *"920 kernel calls … 632 sampled"*, which I had ESTIMATED rather than
   read; the log says **760 across 8 inputs, 544 sampled**. The other two are
   that `NOTES.md` §9's illustrative `python3 -c` commands would have raised
   `ModuleNotFoundError` as printed, and that the reproduce block gave the
   commands in an order that cannot work on a new pattern. **None of them is
   inside the hashed fence: `contract_sha256` is unchanged at
   `141fb37c…`, verified after the edit.**
4. ⚠ **`source_sha256` moved a third time, for CITATION ROT I found in my own
   files.** Three comments frozen in MEASUREMENT-HASHED sources
   (`c/kernel.h:93`, `verus.rs:53`, `verus.rs:615`) and two occurrences inside
   `spec.md`'s hashed fence cite `NOTES.md` subsections **by letter** — and
   `NOTES.md`'s section 6 had drifted under them: `6c` pointed at the
   union-oracle experiment instead of the `f64` measurement, and `6b` at the
   wrong one too.
   ⚠ **Fixing the citations would have cost a RE-MEASURE (`c/kernel.h` and
   `verus.rs` are in `measurement_sources`) and a `contract_sha256` MOVE
   (`spec.md`'s fence). Renumbering `NOTES.md` cost a gate re-run and nothing
   else**, and the resulting order reads better anyway: `6a` TCB, `6b` what the
   proof forces, `6c` `f64`, `6d` the two configurations. `.temp/t148/
   renumber_notes.py` is the one-time script and it refuses to run unless the
   headings are in the pre-fix order. **`contract_sha256` is unchanged.**
5. ⚠⚠ **`source_sha256` and `contract_sha256` moved a fourth time, for
   PROTOCOL RULE 6's ADDED STEP.** The final re-read of the hashed `idiom.why`
   against my own measured numbers found **two clauses this pattern's controls
   refute**:

   | clause, as first written | what refutes it |
   |---|---|
   | *"the R1-vs-R1h cost … is a SCHEDULING difference and nothing more, which is why NOTES.md 4 reports it … rather than as a headline"* | R1h is **cheaper** by −13.71 to −215.86 Ir/call, the candidate mechanism is an extra **store** and not scheduling, and §4 *is* a headline |
   | *"IT REMOVES THE LOUD HARM FROM THE RUST SIDE ENTIRELY"* | `controls/rust_bug.py`: the unsafe arm **SIGSEGVs at `rc=-11`, exactly as C does**. What changes is the harm's CLASS and therefore which instrument reports it |

   **This is `p46`'s defect — a declaration measurement has FALSIFIED while the
   hash still matches — caught by the author before shipping rather than by a
   reviewer afterwards.** Both are corrected in the fence with the original
   struck and visible (`p42`'s style), and the same over-claim was fixed in
   `spec.md`'s prose and `README.md`. `contract_sha256`
   `141fb37c…` → `e8e7199a…`; **nothing the gate PINS moved** — no `required`,
   no `forbidden`, no `identity`, no obligation count, no clause. ⚠ A contract
   move re-opens stage 9's citation, so the loop is **gate → `report.py` →
   gate**: re-runs 6 and 7.


### The cost table (`O3`, `isolated`, `large.bin`; one call = 120 operations)

| rung | Ir/call | Ir/op | static insns | md5(fn) |
|---|---|---|---|---|
| `c-gcc` R1 | 3117.95 | 25.98 | 139 | `364a15767b` |
| `c-gcc-h` R1h | **3032.04** | 25.27 | 137 | `e18452bdbe` |
| `c-clang` R1 | 3583.93 | 29.87 | 142 | `ccae6ba0ad` |
| `c-clang-h` R1h | **3368.07** | 28.07 | 142 | `23504bb946` |
| `safe_naive` R2 | 3946.16 | 32.89 | 180 | `d430a7f81d` |
| `safe_tuned` R3 | 3060.92 | 25.51 | 141 | `be72f8924b` |
| `unsafe` R4 | 3231.48 | 26.93 | 112 | `6beb2748d1` |
| `verus` R5 | 3230.48 | 26.92 | 112 | `6beb2748d1` |

Three results, and **each rung-to-rung figure below had the levers counted on
BOTH sides before it was written** (the task file's deliverable 4):

1. ⚠⚠ **THE SAFETY LINE IS FREE AND ACTUALLY NEGATIVE.** R1h is CHEAPER than R1
   on both compilers and both inputs: gcc **−85.91** Ir/call on large
   (−2.8%) and −13.71 on small; clang **−215.86** (−6.0%) and −40.40. All four
   are far outside `results/synthesis.md`'s own `16.00 Ir/call` coin-flip band.
   ⚠ **The mechanism is OPEN and marked so**: R1 performs the tag store on the
   failure path too (32.76 such stores per call on large, 3.67 on small,
   `.temp/t148/failed_stores.py`), but the implied per-store cost is 2.62 Ir on
   gcc/large and 3.74 on gcc/small — **not stable**, so one extra store does not
   account for all of it.
2. ⚠⚠ **R3 (safe, tuned) IS CHEAPER THAN R4 (unsafe): −170.56 Ir/call, −5.3%.**
   R3's levers are the window reslice and `chunks_exact(2).take(nops)`; R4's is
   `get_unchecked`. **R4 cannot take R3's lever**, and that was re-measured here
   rather than quoted from `p16`: `chunks_exact` is `is not supported` at the
   pinned vstd (`.temp/t148/verus/probe5.rs`). Another instance of
   `.memory/01-ladder.md`'s *a rung covered by an `identity` pin is chained to
   the prover* — this time on the COST axis.
3. **R4 ≡ R5 byte for byte at `-O3`** (`md5_raw equal=True`), so the 1.00 Ir/call
   between them is in the DRIVER, not the kernel. And R4/R5 have the **smallest**
   kernel of the eight (112 insns vs gcc's 139) while being 3.6% dearer per call.

### Can Rust reproduce the bug? — `controls/rust_bug.py`, 0 problems

| arm | DBL (silent) harm | PTR (loud) harm |
|---|---|---|
| `c/kernel.c` | `15737687950051384960` | SIGSEGV |
| unsafe Rust, real `union` | **same, bit for bit**; Miri **silent** | OOB `get_unchecked`; **Miri REPORTS it**; native SIGSEGV |
| safe Rust, `f64::from_bits`, `#![forbid(unsafe_code)]` | **same, bit for bit** | **panic**, `rc=101` |
| the shipped R2/R3 `Cell` enum | **unrepresentable** | **unrepresentable** |

Three findings: a wrong-variant union read is **not UB in Rust** when the bytes
are a valid value of the field's type, so **Miri has nothing to say** about the
silent harm; **safe Rust reproduces the silent harm too** through `from_bits`,
which is why `from_bits`/`to_bits` are `forbidden` in a rung; and the shipped
safe rungs cannot express either harm because the `enum` makes the mismatch
unrepresentable (`p08`'s compile-time shape).

⚠ **The Miri `UB=True` row is the must-fire arm for the `UB=False` one — and it
nearly was not there.** My first invocation omitted the `--` separator, so Miri
read the input path as a second SOURCE file and exited 1 with `multiple input
filenames provided`, which the script would have scored as *no UB*. The control
now asserts `ran` explicitly and copies `check.py:8841`'s command line verbatim.

---

## 5. Problems, and the one deviation from the admitted demonstration

### ⚠ `(double)a + 0.5` became `(a % 2 == 0) ? 0.25 : 2.5`, in every rung

**Measured, not preferred.** At the pinned Verus/vstd, `f64` is opaque:

| construct | result |
|---|---|
| `ensures r == (a as f64) + 0.5f64` | **fails**; `+` on `f64` carries `add_req` (`vstd/std_specs/ops.rs:68`) and nothing discharges it |
| `ensures r == big(d)` for `d > 1.0f64` | **fails**; exec and spec comparison are unconnected |
| `ensures r == (a as f64)` | **fails**; `float_cast_spec` is *"(possibly) non-deterministic Rust cast"* |
| `Pay { d: 0.25f64 }` vs a spec fn of literals | ✅ **verifies** |

(`.temp/t148/verus/probe3.rs`, `probe4.rs`.) So the DBL payload is two literals
in **every** rung — the C rungs spell the same conditional, so no rung is
disadvantaged — and the `d > 1.0` comparison is axiomatised inside `pay_d_gt1`.
**The admitted C mechanism is untouched**: the ordering, the failure path, the
two harms and the detector asymmetry all survive; the confusion still flips the
folded bit (`2.5 > 1.0` is true, a subnormal is not). ⚠ **The consequence, said
plainly: R5 does NOT prove what the DBL arm's boolean IS, only that the kernel
folds it consistently with the spec.** `pay_d_gt1` therefore carries two
independent axioms and is untwinnable twice over.

### ⚠ The C union holds a POINTER; the four Rust rungs hold the ARENA OFFSET

Disclosed in `spec.md`'s `idiom.why`, `NOTES.md` §5 and every rung's header.
R5 cannot hold a `*const u8` without `vstd::raw_ptr`'s `PointsTo` machinery,
which is `p27`/`p29`'s row; `identity` chains R4 to R5; R2/R3 follow R4 so the
four Rust rungs are one algorithm. `*p` and `arena[o]` name the same byte, so
**every checksum agrees on every input**. What it changes is measured, not
argued (§4's table): the silent harm survives into Rust exactly, and the loud one
becomes an out-of-bounds index instead of a wild dereference — so it changes
**which instrument fires**, not merely how loud it is.

### ⚠ Hygiene fixed BEFORE it reached the manager: masked diagnostics

The four controls that record a compiler, Verus or Miri diagnostic were writing
it verbatim into a committed `controls/*.json` — which meant embedding
`/home/apt/repos_common/sec-ladder/.temp/…` paths, ASan pids and pointer values
in a tracked file. ⚠ **`harness/tools/temp_citations.py` reads `git ls-files`,
so that cost would only have appeared AFTER the commit**, as a batch of new
citations to files a fresh clone will not have — `.memory/05-layout.md`'s `p23`
precedent one level down (`controls.log` is declared deliberately un-hashable
because it embeds ASLR addresses, pids, BuildIds and absolute repo paths).

`.temp/t148/mask_patch.py` added one `mask()` per control: the repo prefix goes,
a `.temp/` path becomes `<scratch>`, `==NNNN==` becomes `==<pid>==`, and a long
hex literal becomes `0x<addr>`. **The diagnostic TEXT — which is what the
control is evidence for — is untouched.** Measured after:
`grep -c '\.temp/' controls/*.json` is **0, 0, 0, 0 and 4**, and the four are
`union_oracle.json`'s deliberate `file` keys naming the two configurations'
sources by RELATIVE path, which is worth keeping and is live on this box.

### ⚠ ADJACENT DEFECT FOUND, NOT FIXED: `vparse` splits a clause inside `<...>`

`harness/vparse.py` / `check._clauses` splits a `requires`/`ensures` clause on
top-level commas and **does not treat `<...>` as nesting**, so a clause naming a
generic with two or more parameters is torn in half. Minimised:

```
f ensures = ['r == get_union_field::<U', 'u64>(*p, "i")']     <- two fragments
g ensures = ['r == core::cmp::max::<u64>(a, b)']              <- one, correct
```

⚠ **Consequence, reasoned and NOT measured**: both `spec.md`'s pin and the
derivation use the same splitter, so they still agree and the pin merely records
garbage; but `check_clause_deletion` builds mutants from those spans, and
deleting `get_union_field::<U` would leave `u64>(*p,"i")` — a parse error, so
`_verus` returns `None` and stage 5c FAILS loudly. **So this is a fidelity
defect that becomes a loud failure, not a silent hole.** I did not run that
mutant; `verus.rs` avoids the spelling entirely by naming three spec functions
(`pay_int`, `pay_off`, `pay_dbl`), which reads better anyway.

**Exposure, MEASURED rather than asserted: ZERO.** A sweep of all **121**
committed `patterns/*/*.rs`, **597** parsed clauses, counting clause regions
whose source contains a generic argument list with a top-level comma
(`::<A, B>`): **0**, p35's own included. ⚠ **My first attempt at that
measurement was wrong and is disclosed rather than dropped**: I used
*"the fragment's `<` and `>` counts disagree"* as the tear signature, which
false-positives on **every** `i < v@.len()` and reported 229 hits over the
whole tree. The comparison operator and the generic bracket are the same
character; the signature has to be the generic-argument comma, not the bracket
balance.

### ⚠ Three blocked rows, and what the alternatives cost

Reducing `blocked` below 3 is possible and I judged it wrong. **One** trusted
item could read the union by dispatching on the tag inside its own body —
`blocked == 1` — but the tag→member mapping would then live in an
`external_body` body that nothing checks, which is strictly more trust for a
smaller number. **Three narrow readers keep the mapping in VERIFIED code** and
put the whole of the axiom on "this body reads the member its name says". The
one-item alternative is named here so the choice is reviewable rather than
implicit.

---

## 6. Unsure / not done

1. **The mechanism of the R1h-is-cheaper result is OPEN** (§4.1). Direction and
   size are measured; the per-store constant is not stable across window length.
2. **I did not execute the `include!` route.** `TASK_134`'s correction 1 says
   `check.py:3941` closed it — the line is now at **3972** — and I read it
   rather than building a synthetic pdir
   for it, because the shipped configuration does not use it. If the manager
   wants that re-confirmed by execution, `controls/union_oracle.py`'s
   `scan_unsafe()` is the rig — it already drives the real `_scan_unsafe_sites`
   against a synthetic pattern directory.
3. **I did not measure whether a `blocked == 3` verdict changes anything
   downstream** — `synthesis/`, `composition.py --check`, `results/synthesis.md`.
   `composition.py --check` will FAIL with *built but unclassified* until the
   manager classifies `p35`; that is the check working (see §7).
4. **`p42`'s Miri block count** and the tree-wide sweep were not re-run; I gated
   `p35` only.
5. **The 1.00 Ir/call between R4 and R5** is attributed to the driver loop
   because the kernels are byte-identical at `-O3`. I did not disassemble
   Verus's `main` to name the instruction.
6. **`f64` in the proof is an axiom, not a theorem**, and it is the one place a
   reader should not read `16 verified, 0 errors` as covering the whole kernel.
7. **`.memory/` was not touched.** §8 lists what I think belongs there; the
   manager applies it after review (PROTOCOL rule 9).

---

## 7. `harness/tools/composition.py` — the bug class, PROPOSED not applied

⚠ **I did not edit that file.** `--check` will FAIL with *built but
unclassified* until it is edited, which is the check working as designed. The
wording I propose, and `p35` is the `type` axis's **SECOND** row:

```python
    "type": (
        "the bytes are read at a type they were not written at",
        ["p35", "p38"],
    ),
```

and, because the classification is defensible but not the whole story, a
`CAVEATS` entry:

```python
    "p35": "the safety line is a STATEMENT ORDERING -- the tag store moves "
           "inside the budget test -- so the table's stated test (what does the "
           "safety line ASK?) applies only obliquely: it asks nothing, it "
           "SEQUENCES. Counted `type` on the HARM's cause: a GET dispatches on "
           "a tag that names a different type from the one the payload was "
           "written at, which is CWE-843 exactly. ⚠ The harm has TWO limbs and "
           "only one is memory-unsafe: the DBL limb is a SILENT WRONG VALUE "
           "with no undefined behaviour anywhere (reading a union member other "
           "than the one last stored is DEFINED in C99 6.2.6.1p7), which is "
           "`logical`'s class; the PTR limb dereferences an attacker-derived "
           "integer, which is CWE-822. Counted `type` because ONE ordering "
           "produces both and the type confusion is what produces them.",
```

---

## 8. Memory updates

**None written — subagents may not edit `.memory/`.** What the manager should
land, from the measured text above, after review:

1. `.memory/06-catalogue.md` `p35` cell: **BUILT at `TASK_148`.** ⚠ The cell's
   *"`p35` has no configuration in which its safety obligation is CHECKED"* and
   *"`p35` IS DEAD AND THE CATALOGUE CLOSES"* are both **refuted by
   construction** — the row is built, green, and its obligation IS checked at
   every call site (`controls/proof_mutants.py` `M1`). What survives is narrower
   and sharper: **the configuration in which VERUS checks the read is the one
   `_scan_unsafe_sites` refuses**, and the shipped one axiomatises only the
   wrapper's body.
2. `.memory/01-ladder.md`: another instance of *a rung covered by an `identity`
   pin is chained to the prover*, **on the COST axis** — R3 beats R4 by 5.3%
   because `chunks_exact` is `is not supported` at the pin (re-measured).
3. `.memory/04-verus.md`: **Verus supports `union` natively; it is a LANGUAGE
   BUILTIN and a `std_specs/` grep misses it.** And: **`f64` is opaque at the
   pin** — arithmetic carries an undischargeable `add_req`, `as f64` is a
   possibly-non-deterministic cast, literals verify.
4. `.memory/02-bench-rules.md` / `03`: **a positive control licenses only the
   detector it fires in**, now with a shipped instance in `controls/detectors.py`
   that records the ASan control's non-firing under UBSan as evidence.
5. ⚠ `.memory/03-measurement.md`: **a Miri invocation without `--` reads the
   program's argument as a second SOURCE file** and exits 1 with `multiple input
   filenames provided` — which is not a UB verdict and must never be scored as
   one. Nearly shipped here.
6. ⚠ `harness/vparse.py`'s clause splitter does not treat `<...>` as nesting
   (§5). Fidelity defect, loud downstream, zero exposure today.
7. **The tree now has THREE patterns with blocked rows.** Any summary line
   saying *"blocked exactly `p01 = 1` and `p42 = 1`"* is stale — `RECAP.md`'s
   START HERE box and `.tasks/TASK_148.md` both say it.
8. ⚠ `.memory/06-catalogue.md`'s `p35` cell cites **`check.py:3941`** for
   `_include_literals`; the line is at **3972**. Same citation-rot class the
   file already has a rule for.

---

**PROTOCOL rule 2 running count: launched from 795 (`TASK_151_REPORT.md`'s
closing paragraph), carried to 807.** ⚠ Reconciliation across any
concurrent branch is the manager's job, not mine.

1. ⚠⚠ **The catalogue cell's two strongest sentences about this row are
   REFUTED BY CONSTRUCTION.** *"`p35` has NO LEGAL CONFIGURATION"* and *"a twin
   must be justified away → `n_twins == 0` → hard FAIL"* are both wrong on the
   shipped `check.py`: `twin is None` **with** a `verus.twin_justifications`
   entry is `rep.block` + `rep.shout`, **not** `rep.fail`. The hard FAIL fires
   only when EVERY trusted item is justified away, and p35 has four that are
   twinnable. `n_twins == 4`.
2. ⚠⚠ **The gate forces the WEAKER of two available proofs on this row**, and
   both are measured with must-fail arms (`controls/union_oracle.py`, 9/9).
   Verus checks a union read natively; `_scan_unsafe_sites` requires the token
   to be inside a trusted body, which is exactly what turns the checked read
   into an axiom.
3. ⚠⚠ **`p32`'s spec-weaken result does NOT generalise.** `p32`'s arm verifies
   `15/0`; p35's fails at `wf_cells`, and with the invariant itself weakened to
   `true` it fails at the union read's own precondition. **The correct-variant
   obligation cannot be specified away.**
4. ⚠⚠ **THE SAFETY LINE IS CHEAPER THAN ITS ABSENCE** — four measurements,
   −13.71 to −215.86 Ir/call, all outside the coin-flip band — **with the
   mechanism explicitly marked OPEN** because the implied per-store cost is not
   stable across window length.
5. ⚠ **R3 beats R4 by 5.3%**, and `chunks_exact` being `is not supported` was
   **re-measured** rather than quoted from `p16`.
6. ⚠ **`f64` is opaque at the pinned vstd** (four probes), which changed the C
   program's payload expression — disclosed, with the admitted mechanism shown
   to survive.
7. ⚠ **The union-read TWIN cannot exist in three spellings**, measured with
   plain `rustc`, so the impossibility is about the LANGUAGE.
8. ⚠ **A Python model has no unions**, decided and written down before any cell
   was built, with `sanitizer_expect` split into a DERIVED half that has a
   must-fire arm and a DECLARED half that has two positive controls.
9. ⚠ **Two of my own predictions were refuted by my own battery** (M2/M3
   diagnostics) and are corrected in the control beside the prediction.
10. ⚠ **A Miri invocation missing `--` scored a non-run as "no UB"** and I
    caught it only because the must-fire arm did not fire. Self-disclosed, and
    the control now asserts `ran`.
11. ⚠⚠ **A SECOND self-disclosure, and it is the sharper one: I read a verdict
    out of a record a still-running gate was about to overwrite.** My wait loop
    was `until grep -q '^check.py: '`, which matches the log's **header** line
    (`check.py: p35-tagged-union`) as well as the verdict line — so it returned
    within a second of launch and I printed the PREVIOUS run's record believing
    it was the new one. Caught before it reached any claim, by noticing the log
    was still at stage 0b. **Same family as `TASK_151`'s
    `grep -oE 'PASS|FAIL'` decoding `PASS-WITH-BLOCKED-ROWS` as `PASS`, and a
    third mechanism for it: not substring counting, not alternation order, but
    a PREFIX shared between a log's header and its verdict.** Every number in
    §4 is from the completed run.
12. ⚠ **`vparse`'s clause splitter does not treat `<...>` as nesting** —
    minimised to two lines, exposure zero, loud downstream rather than silent.
13. ⚠⚠ **PROTOCOL RULE 6'S ADDED STEP FIRED, ON MY OWN DECLARATION, AND
    CAUGHT TWO CLAUSES A MEASUREMENT HAD FALSIFIED WHILE THE HASH STILL
    MATCHED.** That is `p46`'s defect exactly — found here by the author
    before shipping rather than by a reviewer afterwards — and both clauses
    are corrected with the original struck and visible.
14. ⚠ **`.memory/06-catalogue.md`'s `p35` cell cites `check.py:3941` for a
    line that is now at `3972`** — 31 lines of citation rot, found while
    confirming the cell's own correction 1.

⚠ **A rigour signal, not a ledger.**

