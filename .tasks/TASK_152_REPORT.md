# TASK_152 — review of `p35-tagged-union`. Report

**Role: research reviewer.** **VERDICT: `p35` STANDS.** No ground for refusal
exists — its C mechanism is distinct from every built row's, and that is the
only ground `CLAUDE.md` rule 6 admits. **The row is NOT FINISHED**, for one
reason that has nothing to do with its gate (deliverable 2, finding **m5**).

**Two full `harness/check.py p35` runs of my own, plus one on a planted mutant.
Every number below was read out of `results/gate/p35-tagged-union.json`, never
grepped out of a log.** Tree left **clean** (`git status --porcelain` empty);
every file I planted into `patterns/p35-*/` was restored and **verified by
bytes against `git show HEAD:`**.

---

## 0. Headline

| # | claim under attack | verdict |
|---|---|---|
| 1 | the C mechanism is distinct (`p38`/`p16`/`p19`) | **SURVIVES** — and I found a harder C-side discriminator than the one shipped |
| 2 | *the gate forces the weaker of two available proofs* | **SURVIVES, AND IS STRONGER THAN CLAIMED.** No third configuration exists. The shipped axiom is **weaker** than the row says (M3, M5) |
| 3 | `blocked = 3` is the row's R5 result, not a defect | **SURVIVES, NARROWED** — `block` is the designed verdict; but the blocked check is exactly the one that would catch M3's mutant |
| 4a | *the safety line is cheaper than its absence* | **SURVIVES, NARROWED** — direction robust over 16 cells; **its stated support is false** (M2); **mechanism CLOSED at `O0`** (m1) |
| 4b | *`R3` beats `R4` by 5.3 %* | ⚠⚠ **FALLS as a safe-vs-unsafe result** (M1). Give `R4` `R3`'s own levers and the sign reverses |
| 5 | `model.py` / `sanitizer_expect` | **SURVIVES** — split, declared, must-fire arm reports rather than crashes (planted twice) |
| 6 | proof-mutant battery, `p32` non-generalisation | **SURVIVES, NARROWED** — 8/8 reproduce; the **conclusion drawn from them** is over-general (M3) |
| 7 | positive controls, per detector | **SURVIVES** — every control executes and fires only in its own detector |

**5 majors, 5 minors, 0 blockers.** Nothing invalidates a published measurement.
Two majors (M1, M2) are the flattering-direction class the task file warned
about; one (M3) makes the row's own headline sharper.

---

## 1. Reproduction, first

```
$ python3 harness/check.py p35                       (twice, on a clean tree)
   run A  verdict PASS-WITH-BLOCKED-ROWS  failures 0  blocked 3  loud 6
   run B  verdict PASS-WITH-BLOCKED-ROWS  failures 0  blocked 3  loud 6
   contract_sha256 e8e7199af62d589d4e709cba9ffcd99f4aefd23c98bb56efd0e1902f337b73ba (both)
   source_sha256 identical to HEAD's record
```

Read out of the RECORD with `json.load`, per `.memory/03-measurement.md`
entries 21–22. Leaf diff against the committed record: **5 and 6 movers, all
run-scoped** — `sanitizer/*/diagnostic` (ASan pid + address),
`miri/runs[]/seconds`, `marginal_ir_env/{bytes,envp_stack_bytes}`. Exactly the
four fields *"A GATE RECORD IS NOT BYTE-REPRODUCIBLE"* names. **Zero `Ir`, zero
md5, zero identity, zero verdict movement.** Tree survey, derived not trusted:
**30 patterns, 27 `PASS` + 3 `PASS-WITH-BLOCKED-ROWS`, blocked `p01=1 p42=1
p35=3`, catalogue 48 rows, 60 records 0 STALE, `temp_citations.py` OK,
`composition.py --check` OK (30 patterns, 10 classes), `contract_diff.py p35`
UNCHANGED.** The `RECAP.md` **Patterns** row is correct in every field.

All five controls re-run and restored byte-identically: `safety_line` 3/3 with
its `--selftest` firing, `union_oracle` **9/9**, `proof_mutants` **8/8**,
`rust_bug` 0 problems, `detectors` 0 firings on R1h × 40 cells.

⚠ `results/gate/p35-tagged-union.json` is **restored to HEAD**; my two re-runs
are kept at `.temp/t152/gate_record_t152_rerun2.json` and
`.temp/t152/gate_rerun.log` if the manager wants to land one (`a9cbba6`'s
precedent).

---

## 2. MAJORS

### ⚠⚠ M1 — *"`R3` beats `R4` by 5.3 %"* is an UNSEARCHED `R4` SIDE. The sign reverses.

`.tasks/TASK_148_REPORT.md` §4.2 and `RECAP.md` 58 both publish **`R3` (safe,
tuned) is cheaper than `R4` (unsafe) by −170.56 `Ir`/call, −5.3 %**, with the
explanation *"`R4` cannot take `R3`'s lever"*. The explanation is **correct
about why the shipped `R4` is dear** and **the counterfactual was never
measured**. This is `p10`'s and `p27`'s shape exactly, and the retraction list
already carries *"Safe Rust beat unsafe Rust"* once.

I built it. Rig at `.temp/t152/rig/`, using `harness/build.py::rust_flags` and
`check.py`'s own probe method (`n_iters` 100→200, `(Ir₂₀₀−Ir₁₀₀)/100`), with
**both shipped rungs as controls that must reproduce the record**:

```
                                   O3/isolated large.bin   small.bin
  safe_tuned  (R3, shipped)   CONTROL    3060.92 = record     684.55 = record
  unsafe      (R4, shipped)   CONTROL    3231.48 = record     712.02 = record
  unsafe + R3's lever 1 (reslice)        3239.48  (+8.00)     720.02
  unsafe + R3's levers 1 AND 2           2857.87              653.71
       (`&buf[off..off+len]` + `w[4..].chunks_exact(2).take(nops)`)
  all four rungs' checksums on small.bin and large.bin: IDENTICAL
```

* the shipped gap is **5.28 %** in `R3`'s favour — reproduced exactly;
* **give `R4` the same op-walk and it wins by 203.05 `Ir`/call (6.63 %) on
  `large` and 30.84 (4.51 %) on `small`.** The sign reverses on both inputs;
* so the missing number is **what the `identity` pin costs `R4`: 373.61
  `Ir`/call, 11.56 %.** `R3`'s published 170.56 is 46 % of it.

⚠ **And lever 1 was never measured either, in either direction.** The report
says *"`R4` cannot take `R3`'s lever"* (singular) and justifies it only with
`chunks_exact`. I re-measured both halves:

* `chunks_exact` — `error: core::slice::impl&%0::chunks_exact is not
  supported` at the pin (`.temp/t152/verus/p_chunks.rs`). **Engineer's claim
  CONFIRMED by my own run.**
* the **window reslice IS available to R5** — `&buf[off..end]` with
  `assert(w@ =~= buf@.subrange(..))` gives **`2 verified, 0 errors`**
  (`.temp/t152/verus/p_reslice2.rs`; it needs `off + len <= usize::MAX`, which
  is the only thing that was in the way). So the "chained to the prover"
  account covers one of the two levers, not both — **and the free one costs
  `R4` +8.00 `Ir`/call, which is why it is not the source of `R3`'s win.**

**What to publish instead:** `R3` beats the *shipped* `R4` by 5.3 %, and the
whole of that is the op-walk spelling the `identity` pin forbids. **As a
safe-vs-unsafe statement it is false: matched on the walk, unsafe wins by
6.6 %.** The `.memory/01-ladder.md` entry the report proposes (*"a rung covered
by an `identity` pin is chained to the prover, on the COST axis"*) is the right
entry — but its figure is **373.61**, not 170.56.

### ⚠⚠ M2 — *"all four are far outside the `16.00 Ir/call` coin-flip band"* is FALSE, and it is inside the HASHED fence.

`TASK_148_REPORT` §4.1, `RECAP.md` 58 (*"four figures, all outside the
coin-flip band"*) and — the part that costs — **`spec.md`'s `idiom.why`, inside
`slb-contract`**: *"four figures, every one of them outside the coin-flip band
`results/synthesis.md` publishes"*.

`results/synthesis.md`'s bands, read at source (lines 195–199):

```
  < 2.00          143 rows   4 real / 139 spurious   "not safe — one environment phase"
  2.00 … 16.00     24 rows   8 real /  16 spurious   "a coin flip — do not quote alone"
  >= 16.00         41 rows  41 real /   0 spurious   "every one is real"
```

The four quoted figures are `−13.71`, `−40.40`, `−85.91`, `−215.86`. **`−13.71`
is inside the `2.00 … 16.00` band**, the one the document labels *a coin flip —
do not quote alone*. Three of four are outside it; the sentence says four.
(Separately: the band is calibrated on the *derived environment-block
correction* column, so it is a borrowed yardstick — but even borrowed it does
not say what the fence says.)

✅ **The conclusion survives on better evidence, which the report did not use:
the `O0` cells.** `−18.35` (small) and `−164.50` (large), **identical on gcc
and clang**, both far outside the band. See m1 for why they are the right
evidence.

### ⚠⚠ M3 — *"the correct-variant obligation … CANNOT BE SPECIFIED AWAY"* is false of the SHIPPED configuration. New arm `X1`.

`patterns/p35-tagged-union/NOTES.md:329`, `controls/proof_mutants.py`'s
docstring (*"the correct-variant obligation is a PRECONDITION OF THE READ …
weakening the specification does not rescue the mutant"*) and
`TASK_148_REPORT` §3 all draw this from `M3` and `M6`. **`M3` and `M6`
reproduce exactly** — I re-ran the battery, 8/8. What they test is a weakening
of the **abstract machine** (`step`, `wf_cell`). They do not test a weakening
of the **trusted readers' own `requires`**, and that is where the obligation
actually lives in configuration A.

The task file asked for the arms the battery lacks. `.temp/t152/extra_mutants.py`,
mutant written to a `.temp/` mirror, never into `patterns/`:

| arm | mutation | result |
|---|---|---|
| **`X1`** | **delete `v@[i as int] is {i,o,d}` from ALL THREE trusted readers' `requires`** | ⚠⚠ **`16 verified, 0 errors` — the SHIPPED obligation count, unmoved** |
| `X2` | `X1` + `wf_cell` → `true` | FAILS (`precondition not satisfied` at the arena index, then `assertion failed`) |
| `X3` | unreachable trusted body: `pay_i` `requires false` | FAILS `precondition not satisfied` |
| `X4` | `requires false` on the VERIFIED kernel | FAILS at the call site in `main` |
| `X5` | postcondition true of the wrong program: `ensures r == r` | FAILS `assertion failed` at the call site |
| `X6` | `X1` + the battery's own `M1` (drop the call site's tag test) | FAILS, but at **`assertion failed`**, not `precondition not satisfied` |

`assume(false)` is arm `M5` and **is not declared**: `spec.md` carries no
`verus.assumptions`, and `check._assume_keyword_hits` returns `{}` on the
shipped file — verified by re-running `M5b`.

**I then planted `X1` into the tree and ran the REAL gate**
(`.temp/t152/plant_x1.py`, restore in a `finally:`, `sha256` verified equal to
`git show HEAD:` — `7e89d6e2…` before and after):

```
  gate verdict FAIL   failures 6   blocked 3
    proof-pin  verus.rs:444 `pay_i`     requires ['i < v@.len()'] != pinned [... , 'v@[i as int] is i']
    proof-pin  verus.rs:455 `pay_o`     (same)
    proof-pin  verus.rs:471 `pay_d_gt1` (same)
    tables     proof_mutants.json / union_oracle.json STALE, table content STALE
  and EVERY soundness stage stayed GREEN:
    verus 16 verified, 0 errors, pinned 16    identity O3 exact, O0 norel
    requires_strength: every clause "not a tautology"    miri 8 runs, 0 UB
```

So: **the only thing that stops `X1` is `spec.md`'s pin — a declaration the
author writes — and the one stage that judges STRENGTH rather than triviality
is `5c-twin`, which is BLOCKED for exactly these three items.** That is
`TASK_003_REVIEW`'s blocker shape, on the exact clause this row's headline is
about, and the gate says so itself in the run I made
(`check.py`, stage 5c-req: *"deleting a trusted item's precondition can never
fail a file (measured — it only removes obligations from callers)"*).

⚠⚠ **This makes the row's headline STRONGER, not weaker.** In configuration
**B** — the one `_scan_unsafe_sites` refuses — the same deletion **fails at the
read** (`requirement not met: to access this field, the union must be in the
correct variant`; `union_oracle` arm `B2`, which I re-ran). **So the two
configurations differ not only in axiom-versus-check but in resistance to a
`requires` deletion, and that is a sharper statement of *the gate forces the
weaker proof* than the one that shipped.**

**Correct wording:** *the correct-variant obligation cannot be weakened by
editing the ABSTRACT MACHINE — `M3`/`M6` measure that, and it is `p32`'s
opposite. It CAN be deleted outright from the trusted readers' `requires`, and
the proof stays green at the pinned obligation count; nothing but the
declaration catches it, and the strength check designed for it is one of this
row's three blocked rows.* **"Imposed by the type system at the operation" is
true of configuration B only** — in A, Verus never sees the read.

### ⚠⚠ M4 — `c/kernel_hardened.c:14-16` still carries the clause `PROTOCOL` rule 6 retracted. `p46`'s defect, in a MEASUREMENT-hashed source.

The rule-6 sweep struck *"the R1-vs-R1h cost of this pattern's safety is a
SCHEDULING difference and nothing more"* in `spec.md`'s fence, in `spec.md`'s
prose and in `README.md`. `.temp/t148/rule6_correction.py` shows exactly those
three edits — and **`c/kernel_hardened.c` is not among them**:

```
c/kernel_hardened.c:13  * ⚠ **This is the third SHAPE of safety line in the tree** ...  It is also the
c/kernel_hardened.c:14  * cheapest: there is no extra test, no extra load and no extra branch, so the
c/kernel_hardened.c:15  * R1-vs-R1h cost of this pattern's safety is a scheduling difference and
c/kernel_hardened.c:16  * nothing more. ../NOTES.md 4 measures it.
```

It is the only surviving copy — `grep -rn "scheduling"` over the pattern
returns this line, the fence's strikethrough, and `NOTES.md`'s correction table
and nothing else. Cost of the fix: `c/*.c` is in
`measure.py::measurement_sources`, so **a re-measure** (`p19`: 1 m 17 s; `p46`:
zero `Ir` moved). ⚠ **And the round that would have caught it re-measured
anyway** — `source_sha256` moved four times — so it was free at the margin and
was missed.

✅ **The rule-6 disclosure itself VERIFIES EXACTLY, by reconstruction.**
Reversing only the two disclosed substitutions (`A_OLD`/`A_NEW`,
`B_OLD`/`B_NEW`, taken from the engineer's own script) against the shipped
`spec.md` reproduces the fence hash

```
  reconstructed pre-correction : 141fb37c7358beccd8bdfac962aeb3d5b78fc4ea074218cc325c4e5ffbaefa01
  disclosed "as first written" : 141fb37c7358beccd8bdfac962aeb3d5b78fc4ea074218cc325c4e5ffbaefa01   MATCH
  shipped                      : e8e7199af62d589d4e709cba9ffcd99f4aefd23c98bb56efd0e1902f337b73ba
```

**so nothing else moved inside the hashed block, and this is the artefact
`p22`'s disclosure never had.** `p46`'s lesson holds anyway: the hash was
perfect and the sentence still shipped, one file over.

### ⚠⚠ M5 — the shipped axiom is WIDER than the twin justification says, and a gate-legal narrower configuration exists.

`spec.md`'s `verus.twin_justifications["pay_i"]` (hashed), the gate record's
blocked reason, `verus.rs:436` and `TASK_148_REPORT` §3 all end with:

> **What the axiom asserts is only that this body reads the member its name says.**

The body is `unsafe { v.get_unchecked(i).i }`. **Two unchecked operations, not
one.** The axiom also asserts that the trusted body's *unchecked index* is
licensed by `i < v@.len()` — and that clause's STRENGTH is untested for these
three items, which is precisely what their blocked rows say. `check.py`'s own
5c-twin `ok` text names this case (*"a body that also reads `i + 1` passes
every stage here"*) — ⚠ **and that line does not print on `p35`**, because it
is suppressed whenever anything is justified away.

**Configuration C exists, is gate-legal, and is strictly narrower**
(`.temp/t152/verus/c4_split.rs`): split the index out into a trusted item that
**does** have a safe twin, and axiomatise only the bare field read.

```
  fn pay_ref<const N>(v: &[Pay; N], i) -> (r: &Pay)      external_body, requires i < v@.len()
      #[cfg(slb_twin)] slb_twin_pay_ref  { &v[i] }        <- SAFE RUST, and it verifies
  fn pay_i(p: &Pay) -> (r: u64)                          external_body, requires *p is i

  ./verus_run.py c4_split.rs                    2 verified, 0 errors
  ./verus_run.py c4_split.rs --cfg slb_twin     3 verified, 0 errors     (the twin verifies)
  check._scan_unsafe_sites on it (REAL function, synthetic pdir)   failures: 0
  must-fail arm: the same predicate on configuration B              failures: 1
```

`Pay` is not `Copy`, which is why it is a `&Pay` and not a value — that is the
whole of the trick, and **the write side of this very pattern already does it**
(`pay_set_unchecked` splits the index from the write and *"unlike the three
readers, HAS a verified twin"*). The read side could have taken the same split
and did not.

It does **not** reduce `blocked` — the three readers still have no twin — but
it moves the unchecked *index* from an untested axiom into a twin-checked one
and makes the shipped sentence true. **Cost: `verus.rs` + `unsafe.rs` are
measurement-hashed, so a re-measure, and `contract_sha256` moves.** ⚠ **I am
reporting, not prescribing**: whether it is worth a re-measure is the manager's
call. The sentence is wrong either way and can be fixed in prose alone.

---

## 3. MINORS

**m1 — `32.76` is the wrong denominator, and with the right one the OPEN mechanism CLOSES at `O0`.**
`marginal_ir_per_call` is `(Ir@200 − Ir@100)/100` (`spec.md`'s `collapse.note`
says so), so its denominator is the mean over **calls 100–199**, not over all
200. I re-derived the failed-store count from the committed generator's output
with my own simulator (`.temp/t152/failed_stores_t152.py`), which **reproduces
both published checksums exactly** (`751388249273516652`,
`3733036646187536480`) and confirms the generator's claim that no benign stream
reaches a confused `GET`:

```
  small.bin   3.6700 /call over all 200   3.6700 /call over calls 100-199
  large.bin  32.7550 /call over all 200   32.9000 /call over calls 100-199   <- TASK_148 used 32.7550
```

With `32.90`:

```
  cell          input        R1        R1h     delta   Ir per failed tag store
  c-gcc/O0      small    1596.85    1578.50    -18.35            5.0000
  c-gcc/O0      large    6953.44    6788.94   -164.50            5.0000
  c-clang/O0    small    1738.43    1720.08    -18.35            5.0000
  c-clang/O0    large    7757.30    7592.80   -164.50            5.0000
  c-gcc/O3      small     715.40     701.69    -13.71            3.7357
  c-gcc/O3      large    3117.95    3032.04    -85.91            2.6112
  c-clang/O3    small     773.58     733.18    -40.40           11.0082
  c-clang/O3    large    3583.93    3368.07   -215.86            6.5611
```

⚠⚠ **At `O0` it is exactly `5.0000` on all four cells, on BOTH compilers.** The
`O0` delta is even numerically identical across compilers (`−18.35` /
`−164.50`). **So the mechanism is CLOSED at `O0`: the entire difference is
5 instructions × the number of tag stores `c/kernel.c` performs on the failure
path**, and the "not stable" reading came from the 0.44 % denominator error
(`5.0221` instead of `5.0000`). It remains **OPEN at `O3`**, where the constant
spans 2.61–11.01 because the optimiser restructures around the removed store.

⚠ **And the honest framing of 4a follows from that**: R1h is not "hardening for
free". **R1h executes strictly less work than R1** — the buggy rung performs a
tag store, 32.9 times per call on `large.bin`, whose result nothing ever reads.
*"The safety line is cheaper than its absence"* is true and reproducible on
**16 of 16** cells (2 compilers × 2 opt × 2 modes × 2 inputs); the mechanism is
*the bug wastes a store*, not *safety is negative-cost*.

**m2 — the hashed `miri.reason` over-generalises, and this union is its own counter-example.**
`spec.md`'s `miri.reason` (inside the fence) says a wrong-variant union read is
not UB in Rust *"when the bytes are a valid value of the field's type, and
**every bit pattern is valid for `u32`, `u64` and `f64`**"*. Validity is not
the whole condition — **initialisedness** is the other half, and `Pay` has a
4-byte member in an 8-byte union. Measured with the gate's own Miri command
shape (`.temp/t152/miri/uninit_probe.rs`):

```
  Pay { i: .. } then read .d   ->  no UB              (p35's DBL confusion; matches the row)
  Pay { o: 7  } then read .i   ->  error: Undefined Behavior: reading memory at
                                   alloc[0x0..0x8], but memory is uninitialized at [0x4..0x8]
```

**Not reachable in `p35`'s own program** — `T_INT` is only ever published in
the same arm that stores an `i` payload, and `SET_INT` cannot fail — so no
measurement moves and the Miri rows stand. But the sentence is a general claim
about this exact union and it is false; the `o` member exists only because of
the pointer→offset substitution.

**m3 — `.memory/06-catalogue.md`'s `p35` cell.** Every correction the engineer
listed in §8.1 is real and none is landed. Independently confirmed:
*"`p35` has NO LEGAL CONFIGURATION"*, *"`p35` IS DEAD AND THE CATALOGUE
CLOSES"* and *"a twin must be justified away → `n_twins == 0` → hard FAIL"* are
all refuted (`_check_twin`: `twin is None` **with** a justification is
`rep.block` + `rep.shout`; the hard FAIL fires only at `n_twins == 0` and `p35`
has **4**). Also still stale in that cell: *"It is the TYPE axis, which still
has ONE built row"*. ✅ The citation rot is real and I re-measured it:
`cand += _include_literals(txt)[0]` is at **`check.py:3972`**, the cell says
`3941`. ✅ And the cell's closing debt — *"none of this is GATE-CERTIFIED …
execute that before treating the twin/`n_twins` interaction as settled"* — **is
now discharged**: `union_oracle`'s `G-A`/`G-B` run the real
`_scan_unsafe_sites` against a synthetic pdir, and I re-ran them.

**m4 — adjacent, gate-side: stage 9b reads a control sidecar's HASH and never its own verdict.**
`check_controls_freshness` compares `derived_from_sha256` and nothing else.
`grep -n "cells_ok\|arms_as_designed" harness/check.py` → **no hits.** A
`controls/*.json` recording `0/9 cells as designed` would still be reported
`FRESH` and the gate would still say `PASS`. Concretely: on an `X1` tree the
`M1` arm's diagnostic changes from `precondition not satisfied` to `assertion
failed` (arm `X6` above), so `proof_mutants.py` would exit non-zero with
`7/8` — **and nothing in the gate would notice.** ⚠ Not a `p35` defect and not
in scope to fix; reported because every pattern from `p23` on now ships arm
outcomes in a sidecar the gate only hashes.

**m5 — ⚠ `p35` IS NOT FINISHED, and the gap is the exact one `PROTOCOL` rule 1 names.**

```
  grep -c p35 results/synthesis.md          0
  head -7  results/synthesis.md             "Patterns: **29**. Gate records: **29**."
  results/SYNTHESIS.md §7                   "every claim this document makes about
                                             the type axis rests on ONE pattern"
```

`results/synthesis.md` is the **generated** one and has not been regenerated
since `p28`; `results/SYNTHESIS.md` (capitals, hand-written) still asserts the
type axis has one row. So a reader who goes to the synthesis cannot find
`p35`'s result at all. ✅ The rest of deliverable 2 is clean: `RECAP.md` finding
**58** exists, the `PROTOCOL` rule-1 findings loop reports **no MISSING
pattern**, `composition.py --check` is OK with `p35` classified `type` and its
`CAVEATS` entry landed, and **`results/tables/p35-tagged-union.md` is
byte-identical to a fresh `harness/report.py p35`.**

---

## 4. CLEAN NEGATIVES — named attacks that did NOT land

**N1 — there is NO third configuration.** The task file's highest-value
question. `_is_trusted` requires `item.external == "verifier::external_body"`,
so the only gate-legal home for an `unsafe` token is a body Verus does not
check; the question is therefore whether the token can be avoided. It cannot:

```
  .temp/t152/verus/c3_nounsafe.rs   `p.i` with NO unsafe, inside verus!{}
     verification results:: 2 verified, 0 errors
     error[E0133]: access to union field is unsafe and requires unsafe function or block
```

⚠ **Verus's own verification does not need the token — rustc does.** So
configuration B is genuinely the only checked one and it is genuinely refused.
Three safe spellings were already measured (`E-index`, `E-get_unchecked`,
`E-deref`, all `E0133`); a `macro_rules!` route is `TASK_009_REVIEW`'s blocker
x1 and `_scan_unsafe_sites` scans the raw text; `_TWIN_BANNED` contains
`"unsafe"`, so a twin cannot host it either. (Aside: the *verifies-but-does-
not-compile* state that probe exhibits is **already closed** — stage 5e /
`_VERUS_RC_ANOMALIES` fails any run that reports `N verified, 0 errors` with a
non-zero exit.)

**N2 — `p38` duplication: the distinction is in the C CODE, not the vocabulary.**
The sharpest evidence is not in either pattern's prose; it is in the two gate
records' `adversarial` blocks:

```
  p38  adversarial-huge.bin / c-gcc     SIGSEGV at  O3/isolated, O3/whole
                                        CORRECT (= model) at O0/isolated, O0/whole
       adversarial-huge.bin / c-clang   CORRECT at ALL FOUR cells — never fires

  p35  adversarial-dbl-confusion / c-gcc AND c-clang   one group, cells
       [O0/isolated, O0/whole, O3/isolated, O3/whole], same wrong value
       15737687950051384960 in all four, `diverges: true`
       adversarial-ptr-confusion, -ptr-deep: SIGSEGV in all four cells, both compilers
```

**`p38`'s harm is a MISCOMPILE**: its C is undefined (C99 6.5p7 effective
type), the clamp is written and the optimiser is entitled to ignore it, and the
harm exists only under gcc at `-O3`. **`p35` executes no undefined behaviour on
its silent limb at all** (C99 6.2.6.1p7 / 6.5.2.3 fn 82; both kernels are built
`-fstrict-aliasing` in the sanitizer stage and neither compiler says a word),
and its harm is in the abstract machine — present at `-O0`, on both compilers,
to the bit. *One is "the compiler is allowed to disbelieve your check"; the
other is "your check was never asked".* Distinct C-side.

**N3 — `p16` / `p19`.** Both omit a bounds check on attacker data (`vlen`; a
transition-table entry used as a row index) and both harm spatially. `p35`
omits no bound: `idx = a % P35_CELLS` is unconditionally in range, and the
arena offset is `BUDGET − navail` with `navail >= 1`. Its error selects the
wrong *interpretation* of in-range bytes. Distinct.

**N4 — `block` is the designed verdict, not lenience about a `fail`.**
`_check_twin`: `twin is None` **without** a justification is `rep.fail`; **with**
one it is `rep.block` + `rep.shout`, and the comment says why (`TASK_009_REVIEW`
x3 shipped two weakenings past a `PASS` + 3 shouts). The hard FAIL is
`n_twins == 0`, and `p35` certifies **4**. The three rows are shouted on every
run with their full justification text.

**N5 — nothing `p35` publishes depends on a blocked row's outcome.** The blocked
rows are strength checks that were *not performed*; the cost table, the
identity pin, the obligation count, the Miri row and the detector matrix are all
independent of them. The TCB tally counts the three and says so.

**N6 — `model.py` and `sanitizer_expect` (item 5).** `sanitizer_expect` is
genuinely split and says so in its own docstring; the DERIVED half runs
`_sim_window` under buggy semantics on the windows the driver visits, and its
verdict matches the sanitizer stage on all 8 inputs. I planted **two** breakages
into `detector_selftest` and it **reported** both rather than crashing: make
`_sim_window` raise → *"the HARDENED arm of the probe RAISED RuntimeError …
this cell tested nothing"* ×4; make it lie (a confusion with the safety line
present) → *"the type-confusion detector FIRED on the probe WITH the safety
line present"* ×3. `TASK_151`'s owed `p32` correction is genuinely applied here.

**N7 — the positive controls (item 7).** Re-run; every one executes (none
folded away) and each licenses only its own detector:

```
  ctl_asan.c   asan       rc=1   hits=5  AddressSanitizer:DEADLYSIGNAL
  ctl_asan.c   asan_clang rc=1   hits=5  AddressSanitizer:DEADLYSIGNAL
  ctl_asan.c   ubsan      rc=-11 hits=0   <- asserted NOT to fire; it does not
  ctl_asan.c   plain      rc=-11 hits=0
  ctl_ubsan.c  ubsan      rc=0   hits=1  runtime error: signed integer overflow
  ctl_ubsan.c  plain/asan/clang/asan_clang  hits=0
```

Controls and kernels share a build line (`-O1 -g -fstrict-aliasing` + the
sanitizer), so the licence transfers. ⚠ The claim is correctly scoped: the
`NOTES.md` table's column is literally *"gcc UBSan"* and there is no clang-UBSan
build line to license.

**N8 — Miri, under a correctly-formed invocation (deliverable 4).** `check.py`'s
own call **does** carry `--` (`check.py:8842`), so the gate's 8 runs were never
at risk; the near-miss was in `controls/rust_bug.py` and is fixed. I re-ran the
shipped `unsafe.rs` by hand with the gate's exact command shape and
`MIRI_PROBE_ITERS = 4`:

```
  adversarial-ptr-confusion.bin  rc=0  no UB
  adversarial-dbl-confusion.bin  rc=0  no UB
  large.bin                      rc=0  no UB
```

and my rig's **positive control fired** on the same command shape (m2's uninit
probe reported UB), so the silence is real silence. **No number in
`TASK_148_REPORT` §4 traces to a stale read** — every one I checked
(`3117.95 / 3032.04 / 3583.93 / 3368.07 / 3946.16 / 3060.92 / 3231.48 /
3230.48`, `139/137/142/142/180/141/112/112`, `md5 6beb2748d1` twice, `760`
calls, `544` sampled, obligations `16`/`20`, `blocked 3`, `loud 6`) reads back
out of the record I regenerated.

**N9 — `M3`/`M6` and the `p32` non-generalisation reproduce.** `M3` fails
`invariant not satisfied at end of loop body` naming `wf_cells`; `M6` fails
`precondition not satisfied`; `p32`'s equivalent arm verifying `15/0` is the
contrast and it holds. The *measurement* is sound; only the sentence drawn from
it is over-general (M3).

**N10 — the safety line is a pure `+2/−2` REORDER, and its must-fire arm fires.**
`safety_line.py --selftest` **3/3**: fed the two files the other way round, the
positional half reports both sites, and the multiset half is demonstrated
**blind** to the same swap.

---

## 5. What I did NOT do

1. **I did not measure `X1` + a moved `spec.md` pin.** `X1` alone is caught by
   `proof-pin`; the full `TASK_003_REVIEW` shape (mutation and pin moved in one
   commit) is what the twin exists for. I established every soundness stage
   goes green under `X1` and reasoned the last step; I did not run it, because
   it needs `spec.md` and `results/tables/` planted at once.
2. **I did not re-derive the `O3` mechanism.** m1 closes `O0` exactly and
   leaves `O3` open, as the report does.
3. **I did not touch `harness/`, `.memory/`, `RECAP.md`, `results/SYNTHESIS.md`
   or `patterns/p35-*/`.** Everything planted was restored and byte-verified.
4. **I did not gate any other pattern.** `p42`'s Miri block count and the
   tree-wide sweep were not re-run; I read the other 29 verdicts out of their
   records only.
5. **M5's configuration C is measured as a proof, not as a rung.** I did not
   rebuild `p35`'s R5 on it, so I have not measured whether it moves `Ir`
   (it should not — `#[cfg(slb_twin)]` twins compile into nothing and
   `pay_ref` is `#[inline(always)]`), and I did not check that `unsafe.rs`
   could mirror it under the `identity` pin.
6. **M1's `unsafe_chunks` variant is not a proposal.** It cannot ship —
   `chunks_exact` is unsupported at the pin and `identity` chains R4 to R5. It
   exists only to supply the counterfactual the 5.3 % headline was missing.

## 6. What the manager should land

1. **M4** — strike the retracted clause in `c/kernel_hardened.c:13-16`
   (re-measure; batch M2's fence sentence with it).
2. **M2** — the `idiom.why` sentence (`contract_sha256` moves), plus `RECAP` 58
   and `TASK_148_REPORT` §4.1. Replace the band argument with the `O0` figures.
3. **M1** — restate `R3`-beats-`R4` as an `identity`-pin cost. The
   `.memory/01-ladder.md` entry is right; **the figure is 373.61 `Ir`/call.**
4. **M3** — restate `NOTES.md:329` and `proof_mutants.py`'s docstring. Record
   the sharper headline: **configuration B resists a `requires` deletion and
   configuration A does not.**
5. **M5** — at minimum, correct *"only that this body reads the member its name
   says"* wherever it appears (`spec.md` fence, `verus.rs:436`, the report).
   Configuration C is available if the narrowing is judged worth a re-measure.
6. **m1** — `32.90`, and *mechanism CLOSED at `O0` at exactly 5.0000 `Ir` per
   failed tag store*; **m2** — the `miri.reason` sentence; **m3** — the
   catalogue cell's five stale claims and the `3941 → 3972` citation;
   **m5** — regenerate `results/synthesis.md` and fix `SYNTHESIS.md` §7, which
   is the only thing standing between `p35` and *finished*.
7. **m4** is a gate question, not a `p35` question: decide separately whether
   stage 9b should read a control's own verdict field. `PROTOCOL` rule 5's
   *"could this happen by accident?"* test applies.

**Evidence:** `.temp/t152/` — `gate_rerun.log`, `gate_restore.log`,
`gate_x1.log`, `gate_record_t152_rerun2.json`, `failed_stores_t152.py`,
`extra_mutants.py` + `.json`, `extra_mutants2.py`, `plant_x1.py`,
`verus/{c3_nounsafe,c4_split,p_chunks,p_reslice2}.rs`,
`rig/{measure_rig.py,marginal.json,pdir/*.rs}`, `miri/uninit_probe.rs`,
`ctl/*.{log,json}`.

---

**PROTOCOL rule 2 running count: launched from 807
(`.tasks/TASK_148_REPORT.md`'s closing paragraph), carried to 842** — 35
distinct measurements in this review, among them two full gate runs read out of
the record, a third on a planted mutant with a byte-verified restore, six new
proof-mutant arms, four Verus configuration probes, a four-cell `Ir` rig whose
two controls reproduce the committed record exactly, an independent
failed-store simulator that reproduces both published checksums, a Miri run
with its own positive control, and a reconstruction of the rule-6 pre-build
contract hash. ⚠ Reconciliation across any concurrent branch is the manager's
job, not mine. **A rigour signal, not a ledger.**
