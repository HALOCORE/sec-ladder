# p35 — tagged union / discriminated dispatch. Findings.

Every number here was produced by a command in this repository and the command
is named beside it. `results/tables/p35-tagged-union.md` is the generated table;
this file is what a reader should take away from it.

**Built at `TASK_148`.** Admitted at `TASK_143` on the C-side bar and ranked
first of seven by distance from `p27`/`p29`; its C demonstration was re-run by
the manager at `.temp/mgr147/`, which also found and closed the one gap in it
(see 2b). ⚠ **The row was refused three times before that and every refusal was
Verus-side or gate-side.** Those refusals are findings in section 6 and none of
them shrinks the row (`CLAUDE.md` rule 6).

---

## 0. What this pattern is, in one paragraph

A cell is a **tag** plus a **union** — `uint8_t tag` beside
`union { uint64_t i; double d; uint8_t *p; }`. An op stream from the file writes
cells at three types and reads them back through the tag. Storing a pointer or a
double takes a byte out of a budget of four, so **the store has a failure path**
— and `c/kernel.c` publishes the tag *before* the payload lands. When the budget
is exhausted the cell claims to hold a pointer (or a double) while the union
still holds the integer a previous `SET_INT` put there, and `GET` reads it **at
the claimed type**. CWE-843.

⚠ **NOT A TEMPORAL ROW.** Nothing is allocated, freed, recycled or aliased
anywhere in this pattern; the cells and the arena are locals whose extent is a
compile-time constant. `p35` was carried in `TASK_143`'s temporal
re-adjudication list only because its old refusal was Verus-side. The axis is
**TYPE**, and this is the tree's **second** type row after `p38`.

---

## 1. The safety line is a STATEMENT ORDERING, and that is a third shape

`p27`'s safety line is a **conjunct**. `p13`'s is a **store**. `p35`'s is a
**sequencing constraint**: `cells[idx].tag = P35_T_PTR;` and
`cells[idx].tag = P35_T_DBL;` move from *before* the `if (navail > 0)` to
*inside* it, after the payload store.

Measured on the two SHIPPED files, `controls/safety_line.py`:

```
  preprocessed kernel.c          230 line(s)
  preprocessed kernel_hardened.c 230 line(s)
  diff  +2 / -2
    - cells[idx].tag = 2;
    - cells[idx].tag = 3;
    + cells[idx].tag = 2;
    + cells[idx].tag = 3;
```

The two preprocessed files have **the same multiset of lines** — nothing is
added and nothing is deleted — and the control also checks the half a line count
cannot see: in `kernel.c` each moved store is immediately followed by
`if (navail > 0)`, and in `kernel_hardened.c` each is immediately preceded by a
`cells[idx].u.*` payload store.

⚠ **That positional half has a must-fire arm**, because a check that cannot fail
is not a check (`.memory/03-measurement.md` entry 19):

```
$ python3 patterns/p35-tagged-union/controls/safety_line.py --selftest
  ok   shipped order (must NOT fire)                        []
  ok   SWAPPED order (must FIRE)                            [...4 problems...]
  ok   multiset check is BLIND to the swap (must be True)   []
3/3 cell(s) as designed
```

**The line-count half is blind to a swap and the positional half is not** — both
files have the same lines, so `+2 / −2` and `multiset_equal` hold in *either*
direction. That is why the control does not stop at the diff.

⚠ **The `#include`-twice construction from `TASK_143`'s demonstration
(`.temp/t143/p35/body.inc`) is NOT what ships**, and the reason is `p32`'s:
`harness/check.py`'s `forbidden` audit reads the rung sources as TEXT, so a
kernel body moved into an `.inc` would be in neither C rung's text and a
forbidden spelling could sit in it unseen. Measuring the shipped files is
strictly stronger than a construction that makes the property true by fiat.

---

## 2. Detector coverage: one ordering, two harms, and they are detected differently

`controls/detectors.py`, five build lines × two shipped kernels × every input.

| input | R1 (`c/kernel.c`) | plain | gcc ASan | gcc UBSan | clang | clang ASan |
|---|---|---|---|---|---|---|
| `small`, `large`, `degenerate`, `-stride3` | correct | — | — | — | — | — |
| `adversarial-dbl-confusion` | **silent wrong value** | — | — | — | — | — |
| `adversarial-exhaust` | **silent wrong value** | — | — | — | — | — |
| `adversarial-ptr-confusion` | **SIGSEGV** | `rc=-11` | **fires** | `rc=-11`, 0 diag | `rc=-11` | **fires** |
| `adversarial-ptr-deep` | **SIGSEGV** | `rc=-11` | **fires** | `rc=-11`, 0 diag | `rc=-11` | **fires** |

`—` is *no diagnostic and exit 0*. **R1h is clean on every input on every one of
the five build lines, and its stdout equals `model.py`'s on every one of them.**
The gate's stage 7h re-measures the gcc ASan+UBSan cell of that and requires it.

⚠ **Why the DBL row is silent, stated because it is easy to get wrong and `p38`
is the neighbouring row.** Reading a union member other than the one last stored
is **defined** in C99 (6.2.6.1p7, 6.5.2.3): the bytes are reinterpreted and the
only hazard is a trap representation, which IEEE-754 `double` and `uint64_t` do
not have on this target. So the DBL arm executes **no undefined behaviour at
all** and is simply WRONG. It is not `p38`'s effective-type violation, and both
kernels are compiled `-fstrict-aliasing` in every sanitizer build here without a
word from either compiler. The PTR arm's undefined behaviour is the
**dereference**, not the union read that produced the pointer.

### 2b. ⚠⚠ The control the demonstration lacked, and the rule behind it

`TASK_143`'s demonstration shipped **one** positive control — a wild pointer
dereference — and used it to license a table with a **per-detector column**.
`.temp/mgr147/NOTES.md` measured what that control does on the `ubsan` build
line: `rc=139`, **0 diagnostics**, because `-fsanitize=undefined` has no
wild-pointer check. A UBSan build that says nothing is indistinguishable from
one that is not linked in (RECAP trap 5; `.memory/03-measurement.md` entry 14,
one level down), so **the `ubsan` column's silence was uninterpretable as
shipped.**

> **A POSITIVE CONTROL LICENSES ONLY THE DETECTOR IT FIRES IN.** A table with a
> per-detector column owes a per-detector control.

`controls/detectors.py` ships two, and the failure of the first to fire in the
second's detector is recorded as a measured row rather than hidden — it is the
evidence for the rule:

```
  ctl_asan.c     plain       rc=-11   hits=0
  ctl_asan.c     asan        rc=1     hits=5   AddressSanitizer:DEADLYSIGNAL
  ctl_asan.c     ubsan       rc=-11   hits=0        <- DOES NOT FIRE
  ctl_asan.c     clang       rc=-11   hits=0
  ctl_asan.c     asan_clang  rc=1     hits=5   AddressSanitizer:DEADLYSIGNAL
  ctl_ubsan.c    plain       rc=0     hits=0
  ctl_ubsan.c    ubsan       rc=0     hits=1   runtime error: signed integer overflow
  ctl_ubsan.c    asan        rc=0     hits=0
```

With both alive, **the DBL row's silence is real silence.** The control also
asserts that `ctl_asan.c` does **not** fire under UBSan, so a future
`-fsanitize=undefined` that gained a wild-pointer check would show up here
rather than quietly making this argument redundant.

---

## 3. The cost table

`marginal_ir_per_call` (stage 3b, callgrind, `(Ir at 200 iters − Ir at 100) /
100`), `O3`, `isolated`, `large.bin`. One call is one window of **120
operations**; `d(Ir)/d(work)` is the slope against window BYTES across the two
probe inputs.

| rung | Ir/call | Ir/op | d(Ir)/d(byte) | static insns | md5(fn) |
|---|---|---|---|---|---|
| `c-gcc` **R1** | 3117.95 | 25.98 | 12.51 | 139 | `364a15767b` |
| `c-gcc-h` **R1h** | **3032.04** | **25.27** | 12.14 | 137 | `e18452bdbe` |
| `c-clang` R1 | 3583.93 | 29.87 | 14.64 | 142 | `ccae6ba0ad` |
| `c-clang-h` R1h | **3368.07** | **28.07** | 13.72 | 142 | `23504bb946` |
| `safe_naive` **R2** | 3946.16 | 32.89 | 16.04 | 180 | `d430a7f81d` |
| `safe_tuned` **R3** | 3060.92 | 25.51 | 12.38 | 141 | `be72f8924b` |
| `unsafe` **R4** | 3231.48 | 26.93 | 13.12 | 112 | `6beb2748d1` |
| `verus` **R5** | 3230.48 | 26.92 | 13.12 | 112 | `6beb2748d1` |

Three things in that table are worth reading twice.

**(i) R4 ≡ R5 at `-O3` by raw machine-code bytes** (`identity` pin, stage 3c:
`md5_raw equal=True`), and the 1.00 Ir/call between them is therefore **not in
the kernel** — it is in the driver loop, which Verus compiles through its own
`main`. The proof licenses the unsafe code at zero instruction cost, which is
this project's standing R4/R5 result.

**(ii) R4/R5 have the SMALLEST kernel of the eight — 112 instructions against
gcc's 139 — and are still 3.6% dearer per call than gcc R1.** Static size is not
dynamic cost, and this row is a clean instance of it.

**(iii) ⚠⚠ R3 (safe, tuned) IS CHEAPER THAN R4 (unsafe): 3060.92 against
3231.48, −5.3%.** ⚠ Before quoting that, the levers on each side were counted,
because five patterns have published a headline wrong in the flattering
direction. R3's levers are the window reslice (`&buf[off..off+len]`) and
`w[4..].chunks_exact(2).take(nops)`; R4's is `get_unchecked` on every array
access. **R4 cannot take R3's lever, and that is a fact about the prover rather
than about Rust** — re-measured here rather than quoted from `p16`:

```
$ ./verus_run.py .temp/t148/verus/probe5.rs
error: `core::slice::impl&%0::chunks_exact` is not supported (note: you may be
able to add a Verus specification to this function with `assume_specification`)
```

`.memory/01-ladder.md`'s finding: *a rung covered by an `identity` pin is
chained to the prover*, so the admissible-R4 class and the admissible-R3 class
are **incomparable, not nested**. p35 is another instance and it is on the cost
axis rather than only on the expressibility one.

---

## 4. ⚠⚠ THE SAFETY LINE IS FREE, AND ON THIS PATTERN IT IS BETTER THAN FREE

**R1h is CHEAPER than R1, on both compilers, and by a margin far outside the
noise band.**

| | R1 | R1h | Δ |
|---|---|---|---|
| gcc, `large.bin` | 3117.95 | 3032.04 | **−85.91 Ir/call (−2.8%)** |
| gcc, `small.bin` | 715.40 | 701.69 | **−13.71 Ir/call (−1.9%)** |
| clang, `large.bin` | 3583.93 | 3368.07 | **−215.86 Ir/call (−6.0%)** |
| clang, `small.bin` | 773.58 | 733.18 | **−40.40 Ir/call (−5.2%)** |

`results/synthesis.md`'s own calibration calls anything under `16.00 Ir/call` a
coin flip; every figure above is 13.7 to 215.9, so all four are real.

**The candidate mechanism, and it is NOT settled.** `c/kernel.c` writes the tag
on the failure path as well as the success path, so it performs a store the
hardened rung does not. `.temp/t148/failed_stores.py` counts them from the input
alone:

```
small.bin    calls=  200 ops/call=   24.00 FAILED stores/call=    3.67
large.bin    calls=  200 ops/call=  120.00 FAILED stores/call=   32.76
```

Dividing gives **2.62 Ir per failed store on gcc/large and 3.74 on gcc/small;
6.59 and 11.01 on clang.** ⚠ **The constant is not stable across window length,
so "one extra store" does not account for the whole of it** and the mechanism is
recorded as OPEN. What is not open is the direction and the size: the safety
line costs nothing, and the unhardened spelling is the slower one.

⚠ **What this does NOT mean.** It is not evidence that safety is free in
general; it is evidence that *this* safety line is a reordering rather than a
test, and a reordering has no instruction of its own to pay for. `p35`'s safety
line was chosen by the bug, not by the benchmark.

---

## 5. ⚠⚠ The one place the rungs are not isomorphic — disclosed, and measured

**The C union holds a POINTER; the four Rust rungs hold the ARENA OFFSET.**

`c/kernel.c` stores `&arena[BUDGET - navail]` into `union { ...; uint8_t *p; }`;
`unsafe.rs` and `verus.rs` store `(BUDGET - navail) as u32` into
`union Pay { ...; o: u32 }` and read `arena[o]`. `*p` and `arena[o]` name the
same byte, so **every checksum agrees on every input, adversarial ones
included** (stage 2 and stage 4 both).

**Why.** `.memory/01-ladder.md`: *a rung covered by an `identity` pin is chained
to the prover.* `spec.md` pins `identity: unsafe ≡ verus`, and R5 cannot hold a
`*const u8` and dereference it without `vstd::raw_ptr`'s `PointsTo` machinery —
which is `p27`'s and `p29`'s row and would put an allocation proof inside a
type-confusion pattern. R4 inherits the constraint; R2/R3 follow R4 so that all
four Rust rungs are one algorithm.

**What it changes, measured rather than argued** (`controls/rust_bug.py`):

| input | C R1 | unsafe arm (union, buggy order) | safe arm (`from_bits`, buggy order) |
|---|---|---|---|
| `small.bin` | `751388249273516652` | **same** | **same** |
| `adversarial-dbl-confusion` | `15737687950051384960` | **same** | **same** |
| `adversarial-exhaust` | `1705852038987163136` | **same** | **same** |
| `adversarial-ptr-confusion` | `rc=-11` SIGSEGV | `rc=-11` SIGSEGV | `rc=101` **panic** |
| `adversarial-ptr-deep` | `rc=-11` SIGSEGV | `rc=-11` SIGSEGV | `rc=101` **panic** |

So the substitution does **not** make the Rust side quieter on the silent harm —
it reproduces it bit for bit — and on the loud harm it changes **which
instrument fires**: what follows a confused read is an out-of-bounds index into
a four-byte arena rather than the dereference of an attacker-derived pointer.
Miri sees the first and not the second:

```
Miri on arm_unsafe_bug.rs (n_iters reduced to 4):
  adversarial-dbl-confusion.bin    rc=0     UB=False
  adversarial-ptr-confusion.bin    rc=1     UB=True   Undefined Behavior: `assume` called with `false`
```

⚠ **The `UB=True` row is the must-fire arm for the `UB=False` one.** Without it
the DBL row's silence would be a Miri that never started — and it nearly was:
the first version of this control invoked Miri without the `--` separator, so
Miri read the input path as a second source file and exited 1 with
`multiple input filenames provided`, which the script would have scored as *no
UB*. `controls/rust_bug.py` now asserts `ran` explicitly.

---

## 6. ⚠⚠⚠ R5: Verus checks unions natively, and the gate cannot use it

### 6a. The TCB

**Nine `#[verifier::external_body]` items**, of which the gate governs **seven**
(`_is_trusted` = `external_body` **and** (`ensures` or `unsafe` in body), so
`load_input` and `emit` are outside it):

| item | what it axiomatises | twin |
|---|---|---|
| `buf_get_unchecked` | the unchecked window read | ✅ `v[i]` |
| `arr_get_unchecked` | the unchecked array read (tags, arena) | ✅ `v[i]` |
| `arr_set_unchecked` | the unchecked array store | ✅ `v[i] = x` |
| `pay_set_unchecked` | the unchecked payload store | ✅ `v[i] = x` |
| `pay_i` | **the union read at `i`** | ❌ **cannot exist** |
| `pay_o` | **the union read at `o`** | ❌ **cannot exist** |
| `pay_d_gt1` | **the union read at `d`, and `d > 1.0`** | ❌ **cannot exist** |

`16 verified, 0 errors` shipped; `20 verified, 0 errors` under `--cfg slb_twin`
— **16 + 4**, one per item that HAS a twin. The obligation census is
`.temp/t148/verus/obligations.log`: 7 consts + `run` 1 + `kernel` 3 + `main` 5.

**So the gate BLOCKS three rows on every run, out loud.** The verdict is
`PASS-WITH-BLOCKED-ROWS` and `blocked == 3`. ⚠ **That is not a defect in this
pattern's spelling; it is the row's R5 result, and section 6d is the experiment
behind it.**

### 6b. What the proof forces — `controls/proof_mutants.py`, 8 arms, 8 as designed

| arm | what it does | result |
|---|---|---|
| `M0-unmutated` | the shipped file | `16 verified, 0 errors` |
| `M1-drop-tag-test` | `GET` reads `pay_i` without testing the tag | **FAILS**, `precondition not satisfied` |
| `M2-bug-order-exec` | R1's bug in R5's exec code | **FAILS**, `assertion failed` at `st_out =~= step(st_in, c, a).0` |
| `M3-bug-order-both` | M2 **plus the same reorder in the abstract machine** | **FAILS**, `invariant not satisfied at end of loop body`, naming **`wf_cells`** |
| `M6-weaken-invariant` | M3 **plus `wf_cell` weakened to `true`** | **FAILS**, `precondition not satisfied` |
| `M4-constant-body` | the kernel returns `0` | **FAILS**, `postcondition not satisfied` |
| `M5-assume-false` | `assume(false);` in the kernel | ⚠ **VERIFIES**, `16 verified, 0 errors` |
| `M5b-gate-sees-it` | `check._assume_keyword_hits` on the same text | `{'assume(': [513]}`; shipped file `{}`; `spec.md` declares `0` |

⚠⚠ **M3 IS THE ROW'S SHARPEST R5 RESULT AND IT IS THE OPPOSITE OF `p32`'s.**
`p32`'s spec-weaken arm — delete the safety conjunct from the exec code *and*
from the abstract machine — **VERIFIES `15/0`**, because nothing forces the
conjunct and the proof is purely functional. **p35's does not**, and `M6` says
why: with the invariant itself weakened to `true`, the proof still fails, now at
the union read's own `requires`. **The correct-variant obligation is imposed by
the type system at the operation and cannot be specified away.** That is the
first row in this tree where the safety line is forced by something other than
the postcondition.

⚠ **Two predictions in that battery were wrong about the diagnostic and right
about the outcome, and they are corrected rather than quietly refitted.** M2 and
M3 were written expecting `precondition not satisfied`; measured, M2 fails one
step earlier (the exec code stops agreeing with the abstract machine before
anything reaches a union read) and M3 fails on `wf_cells` itself — which is the
sharper statement. The correction is in the control's docstring beside the
prediction.

⚠ **M5 reproduces the vacuity hole `TASK_145` and `TASK_149` both planted**, and
M5b is the other half: `TASK_151`'s repair sees it with a line number, sees
nothing on the shipped file, and `spec.md` declares `verus.assumptions` nowhere
— so the shipped gate would now FAIL the file M5 verifies. **The shipped tree's
exposure is zero and this pattern does not change that.**

### 6c. ⚠ `f64` is opaque at the pinned vstd, and the proof says so

Four probes, `.temp/t148/verus/probe3.rs` and `probe4.rs`:

| construct | result |
|---|---|
| `ensures r == (a as f64) + 0.5f64` | **fails** — `+` on `f64` carries `add_req` (`vstd/std_specs/ops.rs:68`) and nothing discharges it |
| `ensures r == big(d)` for `d > 1.0f64` | **fails** — exec comparison and spec comparison are not connected |
| `ensures r == (a as f64)` | **fails** — `float_cast_spec` is *"(possibly) non-deterministic Rust cast"* (`vstd/float.rs`) |
| `Pay { d: 0.25f64 }` against a spec fn of literals | ✅ **verifies** |

So the DBL payload is built from **two literals**, `(a % 2 == 0) ? 0.25 : 2.5`,
in **every rung** — the C rungs spell the same conditional, so no rung is
disadvantaged — and the `d > 1.0` comparison is axiomatised inside `pay_d_gt1`
against the spec function `dbl_gt1`. ⚠ **The proof establishes that the kernel
folds `dbl_gt1(dbl_of(a))` consistently with the specification; it does NOT
establish what that boolean is.** That is a second axiom carried by `pay_d_gt1`
alone, independent of the union one — so that item is untwinnable twice over.

⚠ **This is a deviation from `TASK_143`'s demonstration, which used
`(double)a + 0.5`**, and it is recorded rather than absorbed. The admitted C
mechanism — the ordering, the failure path, the two harms — is untouched; what
changed is the payload expression, so that R5 can state what it computes.
### 6d. The two configurations of the union read — `controls/union_oracle.py`

⚠⚠⚠ **Verus supports the Rust `union` NATIVELY.** The correct-variant
obligation is first class in the type system, checked **at the operation**:

```
error: requirement not met: to access this field, the union must be in the
       correct variant
```

⚠ It is a **language builtin, not a vstd specification**, so a `std_specs/` grep
misses it entirely — which matters on this project, where *"no spec exists"* has
been the wrong reading twice.

But a union read is spelled `unsafe { p.i }` in Rust whether or not Verus checks
it, and `check.py::_scan_unsafe_sites` requires every `unsafe` **token** to sit
inside a `#[verifier::external_body]` body. **Wrapping the read is exactly what
moves it out of the region Verus checks and into an axiom** — and the wrapper,
being trusted, then owes a twin that cannot be written, because Rust has no safe
spelling of a union read at all.

`controls/union_oracle.py` runs both configurations, each with a must-fail arm,
plus the gate's own predicate and the language's own answer, **9 cells, 9 as
designed**:

```
  ok   A1  SHIPPED: read wrapped in external_body VERIFIES      2 verified, 0 errors
  ok   A2  ...delete the CALL SITE's tag test -> must FAIL      1 verified, 1 errors
             | error: precondition not satisfied
  ok   B1  REFUSED: read left in VERIFIED code VERIFIES         2 verified, 0 errors
  ok   B2  ...delete `requires *p is i` -> must FAIL at the READ 1 verified, 1 errors
             | error: requirement not met: to access this field, the union must
             |        be in the correct variant
  ok   G-A `check._scan_unsafe_sites` on A -> 0 failures        {'failures': 0}
  ok   G-B `check._scan_unsafe_sites` on B -> >= 1 failure      {'failures': 1}
  ok   E-index         safe union read -> must be E0133         E0133
  ok   E-get_unchecked safe union read -> must be E0133         E0133
  ok   E-deref         safe union read -> must be E0133         E0133
```

`G-A`/`G-B` execute **the real `_scan_unsafe_sites`** against a synthetic pattern
directory — `TASK_096`/`TASK_097`'s method, execute the predicate rather than
read it. `E-*` is plain `rustc` on three spellings of the twin, so the
impossibility is a fact about the **language** and not about one way of writing
it.

> ⚠⚠⚠ **THE CONFIGURATION THE GATE REFUSES IS THE STRONGER ONE.** In B the
> prover checks the variant at the read and there is no axiom at all. In A —
> what ships — the obligation survives as the wrapper's `requires`, which Verus
> checks **at every call site**, and what is axiomatised is that the body reads
> the member its name says.

**p35 ships A and makes the gap the finding.** `p42` is the standing precedent
and its sentence transfers with one word changed: *the pin protected the
pattern; the proof did not* becomes **the wrapper carried the obligation; the
prover was not allowed to discharge it.**

⚠ **This pattern does NOT propose a `check.py` change.** A `check.py` edit is a
29-pattern re-gate and is the manager's call; `.tasks/TASK_148_REPORT.md` states
the case and stops there.

⚠ **What is NOT true, and the temptation to write it is real**: it is *not*
the case that the shipped configuration checks nothing. `controls/proof_mutants.py`
arm `M1-drop-tag-test` deletes the tag test in front of a `pay_*` call and Verus
reports `precondition not satisfied`. The tag/variant agreement IS proved.


---

## 7. Can Rust reproduce the bug? Three cells, and only one of them is "no"

`controls/rust_bug.py` and the two arms beside it.

| arm | the DBL (silent) harm | the PTR (loud) harm |
|---|---|---|
| `c/kernel.c` | silent wrong value | SIGSEGV, ASan reports |
| `controls/arm_unsafe_bug.rs` — a real `union` | **reproduces it bit for bit**; Miri **silent** | out-of-bounds `get_unchecked`; **Miri reports it**; native SIGSEGV |
| `controls/arm_safe_bug.rs` — `#![forbid(unsafe_code)]`, `f64::from_bits` | **reproduces it bit for bit** | **panics**, index out of bounds |
| **the shipped R2/R3** — a `Cell` **enum** | **unrepresentable** | **unrepresentable** |

Three findings, in order of how much they move:

1. ⚠⚠ **A wrong-variant union read is NOT undefined behaviour in Rust** when the
   bytes are a valid value of the field's type — and every bit pattern is valid
   for `u32`, `u64` and `f64`. So `unsafe` Rust reproduces C's silent harm
   exactly and **Miri has nothing to say about it.** This is the type-axis
   mirror of `p38`'s result rather than a repeat of it: `p38` found that Rust
   has no type-based *aliasing* rule for `unsafe` to unlock; `p35` finds that
   Rust *does* have a correct-*variant* rule, that `unsafe` is required to break
   it, that **Verus checks it natively** — and that **Miri does not**.
2. ⚠ **SAFE Rust reproduces the silent harm too**, under
   `#![forbid(unsafe_code)]`, through `f64::from_bits` — safe Rust's **total**
   reinterpretation, defined for every bit pattern. That is why `from_bits` and
   `to_bits` are in `spec.md`'s `forbidden` list: a rung spelling them would
   delete the correct-variant obligation altogether, and the pattern with it,
   while looking like the same algorithm.
3. ✅ **The shipped safe rungs cannot express either harm.** `Cell::Ptr(o)` is
   one value: the discriminant and the payload are written by one assignment and
   cannot come apart. The boundary is **compile time** — `p08`'s shape — and it
   is why R2 and R3 have no safety line to write.

⚠ Read (1)+(2) together and the honest summary is: **safe Rust removes the
memory-safety half of this bug class and leaves the wrong-answer half exactly
where it was.**

---

## 8. What this pattern does NOT publish, said so the absence does not read as a zero

* **No wall-clock headline.** The measurement record carries the timing block;
  nothing in this file rests on it.
* **No claim that the safety line is free in general.** Section 4's result is
  about a reordering, and it is stated with its mechanism marked OPEN.
* **No `min_ir_per_work` of its own** — the harness default of `0.25 Ir/byte`
  applies, and stage 3b's tightest margin is **49.7×** over it.
* **No `run` budget**: nothing here is declared non-terminating.
* **⚠ No claim that R5 proves the DBL arm's VALUE.** See 6d.
* **⚠ No claim about how OFTEN this shape occurs in the field.** `p38`'s
  `TASK_066_REVIEW` M3 retracted exactly such a sentence; this row measures what
  the class costs and who catches it, not how common it is.

---

## 9. `model.py`: what it can represent, and what it cannot

**Decided before any cell was built, because it decides the shape of the file.**

**A Python model has no unions.** A `(tag, payload)` pair cannot reinterpret one
object's storage at a second type, because the payload object carries its own
type with it. So p35's HARM is **unrepresentable in the model by construction**,
and `model.py` does not pretend otherwise: `_sim_window` under the buggy
semantics returns `acc = None` from the confusion onward, because it does not
know and cannot know what the C program folded.

**What IS representable is the TRIGGER, and it is a measurement rather than a
restatement.** `TaggedCell` keeps `tag` and `kind` — what the cell claims, and
what its payload actually is — as two separate facts, so `tag != kind` is a
state the model can reach. It reaches it exactly when the safety line is absent
and the budget is exhausted, and it cannot reach it otherwise.

So `sanitizer_expect` is **split, and the split is written into its docstring**:

* **DERIVED** — does a type-confused read happen at all, and at which type;
* **DECLARED** — what each detector does when one does.

The declared half is licensed by `controls/detectors.py` (section 2b). The
derived half has a must-fire arm that the gate runs on every input on every run:

```
$ python3 -c "
import sys; sys.path.insert(0, 'patterns/p35-tagged-union')
import model as M
print('selftest        ', M.detector_selftest())
print('PTR probe, fixed', M._sim_window(M._PROBE_PTR, 0, len(M._PROBE_PTR), True))
print('PTR probe, buggy', M._sim_window(M._PROBE_PTR, 0, len(M._PROBE_PTR), False))
print('DBL probe, buggy', M._sim_window(M._PROBE_DBL, 0, len(M._PROBE_DBL), False))"
selftest         []
PTR probe, fixed (917327355, None)     # safety line PRESENT -> no confusion
PTR probe, buggy (None, 2)             # safety line ABSENT  -> tag-2 (PTR) confusion
DBL probe, buggy (None, 3)             # ...and tag-3 (DBL) on the other probe
```

`detector_selftest()` runs **both directions on both probes**, four cells, and
⚠ **a cell that raises is reported as a failed cell with its exception text
rather than allowed to crash** — `p32`'s arm failed by crashing and the
diagnostic was lost (`TASK_151_REPORT` §5); fixing it there costs a re-measure,
and here it was free.

⚠ **The two implementations are different in SHAPE, not merely in spelling**
(`TASK_136`'s defect): implementation 1 is mutable objects with identity and an
exception raised at the read site; implementation 2 is two parallel sequences
stepped by a pure function that mirrors `verus.rs`'s `run` and has no confusion
detection at all. `selfcheck()` runs them against each other on sampled calls on
every gate invocation.

---

## 10. SLB-TRUSTED-ARGUMENT sections

The gate requires one section per trusted item **as
`harness/check.py::_is_trusted` defines one** — `#[verifier::external_body]`
with a non-empty `ensures`, or `unsafe` in the body — and prints it in full on
every run. **It requires SEVEN for p35**, and there are seven below.
`load_input` and `emit` are the two `external_body` items the gate does not
govern: they carry no `ensures`, so they cannot axiomatise a falsehood, which is
the property `_is_trusted` is keyed on.

## SLB-TRUSTED-ARGUMENT verus.rs buf_get_unchecked

**(a) Is the twin's body the right checked stand-in?** The trusted body is
`unsafe { *v.get_unchecked(i) }` on a `&[u8]`; the twin's is `v[i]` on the same
`&[u8]`, with the same parameters and character-identical clause text. `v[i]` is
the checked form of the identical operation — rustc emits the bounds test
`i < v.len()` that `get_unchecked` requires of the caller — so a `requires` too
weak to license the unchecked read is too weak to license the indexed one, and
`--cfg slb_twin` would reject it. This is the item every unsafe rung in this
project ships and it is unchanged here.

**(b) Is the `ensures` complete?** The body performs exactly one operation, a
read of one element, and returns it; `r == v@[i as int]` names that element and
its value, and `v: &[u8]` is immutable so nothing can be modified. The
completeness question is `TASK_009_REVIEW`'s x4 — a body that also read `i + 1`
would satisfy this contract — and the answer is that the body is the one line
above and contains no second access. On p35 this item is used only for the
window read: `off + p + 1 < buf@.len()` follows from `off + len <= buf@.len()`
and `p + 2 <= len`, both loop invariants, so the caller discharges the
precondition with no arithmetic the reader cannot check.

**(c) Does each clause mean the same in both configurations?** `i < v@.len()`
and `r == v@[i as int]` mention only `i`, `v` and `r`; `v@` for a slice is
`vstd::slice`'s view in both configurations, `spec_slice_len` is the same
function, and nothing in the clause text is `cfg`-dependent. The
`#[cfg(slb_twin)]` twin differs from the trusted item in its body and in nothing
else — `_check_twin_cfg_hygiene` checks that mechanically.

## SLB-TRUSTED-ARGUMENT verus.rs arr_get_unchecked

**(a) Is the twin's body the right checked stand-in?** The trusted body is
`unsafe { *v.get_unchecked(i) }` on a `&[T; N]`; the twin's is `v[i]` on the same
`&[T; N]`, same parameters, same clause text. For a fixed-size array `v[i]` is
the checked form of the identical operation — rustc emits the bounds test
`i < N` — so a `requires` too weak to license the unchecked read is too weak to
license the indexed one. It is generic over `T: Copy` and `N` on purpose: p35
indexes **two** arrays with it, the tag array `[u8; 8]` and the arena `[u8; 4]`,
and one item is one axiom instead of two.

**(b) Is the `ensures` complete?** The body performs exactly one operation, a
read of one element, and returns it; `r == v@[i as int]` names that element and
its value, and `v` is `&[T; N]` so nothing can be modified. ⚠ **On p35 every `T`
is `u8`** — a plain integer — so there is no provenance, no pointer and no
interior mutability for the clause to be silent about. ⚠⚠ **And `T` is
deliberately NOT `Pay`**: the union has its own accessors below, precisely
because a `Seq<Pay>` equality would not be equality of "the value read" in the
sense this clause means. `Pay` is not `Copy` (Verus rejects the derive), so it
could not instantiate `T` even if that were wanted.

**(c) Does each clause mean the same in both configurations?** Both clauses
mention only `i`, `v` and `r`, and `v@` for `[T; N]` is `vstd::array`'s view in
both. `N` is a const generic instantiated identically at every call site in both
configurations. Nothing in the clause text is `cfg`-dependent, and the twin
differs only in its body.

## SLB-TRUSTED-ARGUMENT verus.rs arr_set_unchecked

**(a) Is the twin's body the right checked stand-in?** The trusted body is
`unsafe { *v.get_unchecked_mut(i) = x; }`; the twin's is `v[i] = x;`, same
signature, same clause text. `v[i] = x` is the checked form of the identical
store, so a `requires` too weak to license the unchecked one is too weak to
license the checked one. The vacuity probe confirms the twin NEEDS the
precondition: stage 5c-twin deletes `i < old(v)@.len()` and the twin stops
verifying.

**(b) Is the `ensures` complete?** The body performs exactly one operation, a
store of one element; `final(v)@ == old(v)@.update(i as int, x)` names the whole
of the array's new value — every index other than `i` is asserted UNCHANGED, so
a body that also wrote `i + 1` could not satisfy it. That is the completeness
question answered positively rather than argued: this `ensures` is total over
the object, unlike a read's, which only names one element. ⚠ `x` is a pure VALUE
parameter and no `requires` constrains it, which the gate shouts every run; the
justification is in `spec.md`'s `verus.unsafe_justifications`, and it is that `x`
is stored and never used as an address, an index or a length.

**(c) Does each clause mean the same in both configurations?** `old(v)`,
`final(v)` and `Seq::update` are the same in both; nothing is `cfg`-dependent;
the twin differs only in its body.

## SLB-TRUSTED-ARGUMENT verus.rs pay_set_unchecked

**(a) Is the twin's body the right checked stand-in?** The trusted body is
`unsafe { *v.get_unchecked_mut(i) = x; }` on a `&mut [Pay; N]`; the twin's is
`v[i] = x;`, same signature, same clause text. ⚠ **The `unsafe` here is the
unchecked INDEX and nothing else — WRITING a union member is safe Rust**, only
reading one is not — so the checked stand-in really is an ordinary indexed store
and the correspondence is exact. This item exists separately from
`arr_set_unchecked` only because `Pay` is not `Copy` and so cannot instantiate
its `T: Copy`.

**(b) Is the `ensures` complete?** One store, and
`final(v)@ == old(v)@.update(i as int, x)` names the whole array afterwards, so
every other index is asserted unchanged and a second write could not satisfy it.
⚠ **What the clause does NOT say, and does not need to:** it says nothing about
which union MEMBER `x` is in. It does not have to, because `Seq<Pay>` equality
carries the whole `Pay` value including its variant — `wf_cells` is stated over
exactly those values and is re-established from this `ensures` alone. `x` is a
pure value parameter with no `requires`, justified in `spec.md` as above.

**(c) Does each clause mean the same in both configurations?** Same clauses,
same views, same const generic `N`, nothing `cfg`-dependent; the twin differs
only in its body.

## SLB-TRUSTED-ARGUMENT verus.rs pay_i

**(a) Is the twin's body the right checked stand-in?** ⚠⚠ **THERE IS NO TWIN AND
THERE CANNOT BE ONE**, and that is this pattern's R5 result rather than an
omission. Rust has **no safe spelling of a union read at all**: `v[i].i`,
`v.get_unchecked(i).i` and `p.i` are each `error[E0133]: access to union field
is unsafe`, measured on all three by `controls/union_oracle.py`, and
`_TWIN_BANNED` forbids `unsafe` in a twin. The item is declared in
`verus.twin_justifications` and the gate BLOCKS the row, out loud, on every run.
**What stands in for the twin is a different oracle, and it is a stronger one:**
`controls/union_oracle.py` shows that the same read left in VERIFIED code is
checked by Verus **at the operation** (`requirement not met: to access this
field, the union must be in the correct variant`), with a must-fail arm — and
that `_scan_unsafe_sites` refuses that configuration. So the strength question
has an answer; the gate's mechanism for asking it is what is unavailable.

**(b) Is the `ensures` complete?** The body is one expression,
`unsafe { v.get_unchecked(i).i }`, and performs exactly two unchecked
operations: the index and the union read. Both are named by the `requires` —
`i < v@.len()` and `v@[i as int] is i` — and the `ensures`
`r == pay_int(v@[i as int])` names the value of the member read and nothing
else. `v` is `&[Pay; N]`, so nothing can be modified. ⚠ The residual is
`TASK_009_REVIEW`'s x4 in its purest form: **nothing checks that the body reads
the member the item's NAME says.** That is exactly what configuration B in
`union_oracle.py` would check and what wrapping the read gives up, and it is
recorded here rather than argued away. The backstops are stage 3c identity
(R4 ≡ R5 byte for byte) and stage 8 Miri, which runs `unsafe.rs` — the same
expression — on every input.

**(c) Does each clause mean the same in both configurations?** There is only one
configuration, since there is no twin. Within it: `v@` for `[Pay; N]` is
`vstd::array`'s view, `is i` is Verus's builtin variant test, and `pay_int` is a
`pub open spec fn` whose body is `get_union_field::<Pay, u64>(p, "i")` — a
`verus_builtin` spec function, not a vstd item. Nothing is `cfg`-dependent.
⚠ `pay_int` exists as a NAMED spec function rather than inline because
`harness/vparse.py` splits a clause on top-level commas without treating `<...>`
as nesting, so the literal spelling tore in half at the generic argument's
comma; see `.tasks/TASK_148_REPORT.md`.

## SLB-TRUSTED-ARGUMENT verus.rs pay_o

**(a) Is the twin's body the right checked stand-in?** Identical to `pay_i`'s
answer, for the `o: u32` member: no safe spelling exists, the item is justified
in `spec.md`, the gate blocks it out loud, and `controls/union_oracle.py` is the
stronger oracle that stands in its place.

**(b) Is the `ensures` complete?** One expression, two unchecked operations —
the index and the union read — and both are named by the `requires`
(`i < v@.len()`, `v@[i as int] is o`). The `ensures`
`r == pay_off(v@[i as int])` names the value of the member read. ⚠ **This item
carries the pattern's ONE SPATIAL obligation and it is NOT in this contract**:
the caller uses `r` as an index into `arena`, and what licenses that is
`wf_cell`'s second conjunct, `pay_off(p) < BUDGET`, maintained by the kernel's
loop invariant. So this item's `ensures` being silent about the value's RANGE is
correct — the range is a property of the cells, not of the read — and the
obligation is discharged where it belongs, at `arr_get_unchecked(&arena, ...)`.

**(c) Does each clause mean the same in both configurations?** As for `pay_i`;
`pay_off` is the `get_union_field::<Pay, u32>` spelling under the same
`vparse` constraint.

## SLB-TRUSTED-ARGUMENT verus.rs pay_d_gt1

**(a) Is the twin's body the right checked stand-in?** ⚠⚠ **No twin, for TWO
independent reasons, and either one alone would be enough.** First, as for
`pay_i`: there is no safe spelling of a union read. Second, and this item is the
only one it applies to: even if the read were safe, the twin would have to prove
that the exec comparison `d > 1.0f64` equals the spec function `dbl_gt1`, and at
the pinned vstd that link **cannot be proved** — `f64` comparison is specified
through `partial_cmp`'s existential and `f64` arithmetic through an
undischargeable `add_req` (`.temp/t148/verus/probe3.rs`). So this item is
untwinnable twice over and the two reasons do not overlap.

**(b) Is the `ensures` complete?** The body is one expression,
`unsafe { v.get_unchecked(i).d > 1.0 }`, and performs three things: the
unchecked index, the union read, and the comparison. The first two are named by
the `requires`; the third is the **second axiom** and it is stated as such —
`r == dbl_gt1(pay_dbl(v@[i as int]))` asserts that the exec comparison agrees
with the spec one and nothing more. ⚠ **So this item axiomatises strictly more
than the other six**, and the proof consequently does NOT establish what the
folded boolean IS, only that the kernel folds it consistently with the
specification. Section 6c is the measurement behind that and the reason the DBL
payload is two literals rather than arithmetic. The backstop is the same:
identity plus Miri on `unsafe.rs`, whose comparison is the same expression.

**(c) Does each clause mean the same in both configurations?** One
configuration; `is d` is the builtin variant test; `pay_dbl` and `dbl_gt1` are
`pub open spec fn`s in this file with no `cfg` gating. ⚠ `dbl_gt1`'s body is
`x > 1.0f64` — a SPEC-level comparison, which Verus treats as a different
function from the exec one; that is precisely the gap this item's `ensures`
bridges by fiat, and calling it an axiom rather than a proof is the honest
description.

---

## 11. PROTOCOL rule 6 — the contract declaration

The `slb-contract` block's sha256, **as first written, before any measurement
and before the first `harness/check.py p35` run**:

```
141fb37c7358beccd8bdfac962aeb3d5b78fc4ea074218cc325c4e5ffbaefa01
```

⚠ **The `git show HEAD:… | diff -` check is VACUOUS on a new pattern** and rule
6 says so itself: p35 lands in one commit, so the working tree and `HEAD` cannot
differ and the command always prints nothing. **The recorded hash above is the
only evidence**, which is why rule 6 opens by demanding it be written down
before any cell is built. It was recorded in `.temp/t148/NOTES.md` at that
moment and copied here.

**If it has moved by the time you read this, `python3
harness/tools/contract_diff.py p35` says what moved inside the hashed block,
key by key, from `git` alone.**

### ⚠⚠ THE HASH MOVED, AND IT MOVED BECAUSE RULE 6'S ADDED STEP FIRED

Rule 6's second half — *re-read the hashed `why` and every rung-source doc
comment AGAINST YOUR OWN MEASURED NUMBERS; a frozen declaration is evidence
about WHEN it was written, not about whether it is still true* — is `p46`'s
defect, and it **fired on p35**. Two clauses in the hashed `idiom.why` were
refuted by this pattern's own controls:

| clause, as first written | what refutes it |
|---|---|
| *"the R1-vs-R1h cost … is a SCHEDULING difference and nothing more, which is why NOTES.md 4 reports it … rather than as a headline"* | section 4: R1h is **cheaper**, by −13.71 to −215.86 Ir/call over four measurements, and the candidate mechanism is an extra **store** (32.76 per call on `large.bin`), not scheduling. §4 *is* a headline. |
| *"IT REMOVES THE LOUD HARM FROM THE RUST SIDE ENTIRELY"* | `controls/rust_bug.py`: the unsafe arm **SIGSEGVs**, `rc=-11`, exactly as C does. What the substitution changes is the harm's **class** — a wrong index rather than a wild pointer — and therefore **which instrument reports it**. |

**Both are corrected in the fence with the original left visible** (`p42`'s house
style: strike, do not delete), and the same over-claim was fixed in `spec.md`'s
prose and in `README.md`. The one-time script is
`.temp/t148/rule6_correction.py`.

```
contract_sha256 as FIRST WRITTEN   141fb37c7358beccd8bdfac962aeb3d5b78fc4ea074218cc325c4e5ffbaefa01
contract_sha256 as SHIPPED         e8e7199af62d589d4e709cba9ffcd99f4aefd23c98bb56efd0e1902f337b73ba
```

⚠ **Nothing that the gate PINS moved** — no `required`, no `forbidden`, no
`identity`, no obligation count, no clause. The whole of the diff is two
sentences of `idiom.why`, and rule 6's direction test
(`.memory/01-ladder.md`) is satisfied in the strict direction: the declaration
was made WEAKER and more specific by a measurement, not adjusted to fit one.
⚠ `python3 harness/tools/contract_diff.py p35` cannot show this, and says so —
*"not present at HEAD (a pattern added since?)"* — because the pattern lands in
one commit. The two hashes above are the evidence.

Two further corrections were made in the same re-read and are visible rather
than silent: the `M2`/`M3` diagnostics in 6b, and the `(double)a + 0.5` →
two-literals deviation in 6c.

---

## 12. What was NOT done, and what is open

1. **⚠ The gate verdict is `PASS-WITH-BLOCKED-ROWS` with `blocked == 3`**, one
   per union reader. That is a THIRD blocked pattern in the tree (`p01 = 1`,
   `p42 = 1`) and the manager should know it is a design outcome, not a defect:
   the alternative configurations were measured and are in 6b.
2. **No `check.py` change is proposed or made.** The `_scan_unsafe_sites`
   interaction is reported in `.tasks/TASK_148_REPORT.md`; a `check.py` edit is a
   29-pattern re-gate.
3. **The mechanism of section 4's R1h-is-cheaper result is OPEN.** The direction
   and the size are measured; "one extra tag store on the failure path" does not
   account for the whole of it, because the implied per-store cost is not stable
   across the two window lengths.
4. **`f64` in the proof is an axiom, not a theorem** (6c), and it is the one
   place where a reader should not read `16 verified, 0 errors` as covering the
   whole kernel.
5. **The `arena` is 4 bytes and never written after initialisation.** A larger
   arena would make the PTR arm's harm depend on the offset's range as well as
   its type; that was not explored.
6. **No sweep law is published.** `inputs/gen.py` ships `sweep-nops*.bin` and
   the gate drops them from the matrix; nothing in this file rests on them.
