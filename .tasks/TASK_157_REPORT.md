# TASK_157 report — `p25` built

**Role: research engineer.** `patterns/p25-realloc-growth/`, seven rungs, gate
green. This file is the durable copy of the return message; every number in it is
in the pattern's own `NOTES.md` and in a `controls/*.json` sidecar that
regenerates it.

## 1. What was built

```
patterns/p25-realloc-growth/
  c/kernel.h  c/kernel.c  c/kernel_hardened.c  c/main.c
  safe_naive.rs  safe_tuned.rs  unsafe.rs  verus.rs
  model.py  spec.md  NOTES.md  README.md
  inputs/gen.py
  controls/  safety_line.py + arm_body.inc          no_stale.py
             no_reloc.py                            reloc_probe.py + probe_realloc.c
             detectors.py + ctl_asan.c + ctl_ubsan.c
             safe_arms.py + arm_safe_ptr.rs + arm_safe_ptr_nopush.rs
                          + arm_safe_negctl.rs + arm_safe_index.rs
             rederive.py                            rust_bug.py + arm_unsafe_ptr.rs
             proof_mutants.py
             (nine `.json` sidecars, each with `derived_from_sha256`)
```

## 2. ⚠⚠ THE DESIGN CALL THAT CONTRADICTS THE TASK FILE, AND IT IS THE ROW'S SPINE

`TASK_157` and `.temp/mgr155/NOTES.md` §5 pin the hardened cell as

```c
if (curbase == toks) v = *cur; else v = P25_SENT;
```

**That cell cannot be shipped, and the reason is structural rather than
stylistic: it makes the kernel's ANSWER a function of the ALLOCATOR.**

* whether `realloc` relocates is a heap-topology fact, so `model.py` could not
  derive the checksum without simulating glibc — and encoding *"the `16 → 32`
  growth moves"* into the model is a tautology of **this box's allocator**, which
  is worse than the tautology `.memory/03-measurement.md` entry 19 forbids;
* the four Rust rungs grow a `Vec`, whose capacity sequence is `8, 16, 32, 64`
  where C's is `4, 8, 16, 32, 64` (measured, `NOTES.md` 5a), so their relocation
  points are not C's and they could not agree with the C rungs on the adversarial
  input;
* so `harness/check.py` stage 2's *"every checked rung agrees with the model"*
  would have been **unsatisfiable in principle**.

**What shipped re-derives instead:**

```c
} else if (curbase == toks) {
    v = (uint64_t)*cur;
} else {
    v = (uint64_t)toks[curi];
}
```

The conjunct survives — so the old kill's *"there is no safety conjunct to omit"*
stays refuted, and the shipped diff is it — and the answer is
allocator-independent, because **`realloc` copies**. ⚠ **The consequence is the
row's thesis: the conjunct buys MEMORY SAFETY and buys nothing else**, since both
branches compute the same value in every terminating execution.

### 2a. That also DISSOLVES the named "thing that will bite you"

`TASK_157` named the **sentinel decision** as its least-certain call and asked
for a choice between `P25_SENT = 251` (collision ≈ 1/130) and a `1<<40` sentinel
(`+4` / `+5` static instructions). **Neither is needed.** The collision
`.temp/mgr155/` measured — `R1h == min + 31·251` sitting inside R1's range — is a
property of the SENT-folding cell, and the shipped cell folds no sentinel at the
safety line at all. No sentinel value changes anything and the `+4`/`+5` static
cost is not paid.

⚠ **A residual collision remains and is disclosed rather than engineered away:**
R1 and R1h agree on an adversarial input about **1 run in 256**, because the
divergence is one byte in a Horner chain. `p29`'s precedent is followed exactly —
gate on the invariant, pin R1h's value and the detector, **never** pin
`R1 ≠ R1h`.

## 3. ⚠⚠ A MANAGER FIGURE REFUTED BY MEASUREMENT

`.temp/mgr155/NOTES.md` §6 published, as its novelty census:

> *"C rungs that call `malloc` at all → `p10 p27 p28 p29 p32 p42` (6 of 30)"*

`controls/no_reloc.py` blanks comments and string literals first — the rule
`check.py::exec_code` already applies to rung sources — and measures **5 of 32:
`p27 p28 p29 p34 p42`**. Two errors in one line, in opposite directions:

* **`p10` and `p32` are false positives.** Both mention `malloc` only in prose,
  and `p32/c/kernel.h:29` literally reads *"neither `malloc`'d nor `free`d per
  use"* — the grep counted a sentence that denies the thing it counted.
* **`p34` is missing**, and it really does allocate (`malloc(sizeof *o)` in both
  C rungs). It was committed before `mgr155` ran.

✅ **The load-bearing half survives, now comment-blanked: `realloc` is called by
exactly ONE pattern's `c/`, and it is p25 — 1 of 32.** ⚠ And the useful negative:
`free` is called by **32 of 32**, because every `c/main.c` frees the driver
payload, so *"calls `free`"* is not a distinguishing token and the distinction
has to be stated about the KERNEL.

The refuted sentence had been quoted verbatim into the hashed `why`; it was
struck, and that is contract move 1 (§8).

## 4. ⚠⚠ THE COST AXIS, AND THE SAFER REPAIR IS THE CHEAPER ONE

`controls/rederive.py` builds a THIRD C arm — the **unconditional re-derive**,
generated from the shipped `c/kernel.c` by one asserted substitution. It is the
only C rung **DR 400** cannot reach: C11 7.22.3.5p4 makes `cur` indeterminate the
moment `realloc` returns, *whether or not the block moved*, so the surviving
`*cur` in R1h's true branch is a use of an indeterminate value under the abstract
machine. It agrees with `model.py` on 8/8 inputs and is sanitizer-clean on all.

**Static `kernel` instructions (non-pad, isolated):**

| | gcc `-O0` | gcc `-O3` | clang `-O0` | clang `-O3` |
|---|---|---|---|---|
| R1 | 218 | 165 | 209 | 150 |
| R1h (the shipped conjunct) | 228 (+10) | 176 (+11) | 218 (+9) | 162 (+12) |
| unconditional re-derive | 220 (**+2**) | 168 (**+3**) | 210 (**+1**) | 152 (**+2**) |

**Marginal `Ir`/call, gcc, isolated, `(Ir@200 − Ir@100)/100`:**

| input | opt | R1 | R1h | re-derive |
|---|---|---|---|---|
| `small` | `-O0` | 1375.16 | 1389.92 (+14.76, +1.07 %) | 1382.54 (**+7.38, +0.54 %**) |
| `small` | `-O3` | 703.85 | 728.54 (+24.69, +3.51 %) | 714.72 (**+10.87, +1.54 %**) |
| `large` | `-O0` | 6540.98 | 6672.06 (+131.08, +2.00 %) | 6606.52 (**+65.54, +1.00 %**) |
| `large` | `-O3` | 3173.74 | 3338.13 (+164.39, +5.18 %) | 3239.41 (**+65.67, +2.07 %**) |

> **The repair that is correct under the C standard costs about HALF what the
> idiomatic one costs, on both compilers at both optimisation levels and both
> inputs. On the C side this row has no trade-off: the safer repair dominates on
> both axes.**

So **both halves of `TASK_134`'s kill are answered and they go opposite ways**:
the conjunct EXISTS (first half refuted) and it is INSUFFICIENT (second half
vindicated, for a reason nobody had stated — not *"a check is impossible"* but
*"the check is not enough"*).

⚠ **Weaker-searched endpoint, named as deliverable 4 requires:** *neither* repair
had its spelling searched. Each is ONE spelling; the levers were counted on
neither side. The figures are the cost of THESE TWO SPELLINGS, never of "the
repair". Both optimisation levels are given because the relative cost of R1h
grows from +1.07 % to +5.18 % — quoting one level would understate it 5×. The
inline mode is `isolated` in every row.

⚠ Unlike p34, **p25's safety line EXECUTES on every benign input** (every READ
evaluates the conjunct; no benign input takes the `else`), so p25 has a real,
non-zero benign gradient where p34's is `0.00`.

## 5. Deliverable 4's negative control — and `E0502` is not distinguishing

`controls/safe_arms.py`, four arms:

| arm | what | result |
|---|---|---|
| A `arm_safe_ptr.rs` | `&toks[curi]` held across `toks.push(a)` | **fails**, `E0502` |
| B `arm_safe_ptr_nopush.rs` | A with the ONE push replaced by the SENT fold | **compiles** — the diagnostic is attributable |
| C `arm_safe_negctl.rs` | **NEGATIVE CONTROL**: 12 lines, a struct and a `&mut`, no container, no growth, no saved reference | **fails, same `E0502`** |
| D `arm_safe_index.rs` | the index port | **compiles**, agrees with `model.py::parse_fold` on all four adversarial windows |

**Arm C is the finding.** `E0502` carries no information about interior pointers
— **the fourth time this project has read a rustc code as distinguishing when it
was not** (p25's own, p28's `E0382`/`E0499`, p34's `E0507`). So the claim this
row makes is the narrower, truer one: **the port that DOES compile has no bug**,
because `realloc` copies — safe Rust's answer here IS `c/kernel_hardened.c`'s, at
zero cost. The catalogue's *"the INDEX port has NO BUG AT ALL"* is confirmed and
recorded so nobody rediscovers it.

## 6. The R5 result: the ladder DELETES the bug above R1

`10 verified, 0 errors`; twin config `12 / 0`; **TCB 4 items**, two inside the
twin regime and both twinned, `blocked: []`.

⚠⚠ **The temporal obligation has no analogue at R5, and that is the result
rather than an omission.** Writing `c/kernel.c`'s READ in Rust needs
`unsafe { *cur }` under `curbase == toks.as_ptr()`, and Verus cannot license it:
the read needs a `PointsTo` no vstd API yields for a `Vec`'s buffer, and the
guard is an **address** comparison while Verus's pointers carry **provenance** —
the guard is exactly the fact the proof would need and exactly the fact address
equality does not give. What survives is the spatial residue
`have ==> curi < toks@.len()`.

⚠ **That is a claim about the PROOF rung, not about Rust**, and
`controls/rust_bug.py` keeps the two apart: `controls/arm_unsafe_ptr.rs` is
`unsafe.rs` with the index replaced by `toks.as_ptr().add(curi)` and nothing
else, and **Miri reports `memory access failed: allocNNNN has been freed`** on
exactly the three growth-after-SAVE inputs, while the shipped rung is clean on
all five probed and the arm itself is clean on `adversarial-nogrow` and `small`.

**A smaller obligation gets MORE scrutiny, not less** —
`controls/proof_mutants.py`, baseline `10/0`, every substitution count asserted:

| arm | Verus |
|---|---|
| ATTACK — delete `have ==> curi < toks@.len()` | `9/1` **precondition not satisfied** (at the READ) |
| X1 — strike the statement that re-establishes it | `9/1` **invariant not satisfied at end of loop body** (at the SAVE) |
| VACUITY — constant kernel body | `9/1`→`8/1` **postcondition not satisfied** |
| SPEC-WEAKEN — `ensures r == r`, `main` untouched | `9/1` **assertion failed** at the call site |

⚠ **p25's R5 is the first in this tree to call `Vec::push` in exec code** —
measured, not assumed: the five other `verus.rs` files containing `.push(` all
push a `Seq` in ghost code. vstd's `assume_specification[Vec::push]` carries
`final(vec)@ == old(vec)@.push(value)` and **no `requires` at all**, so the growth
costs no trusted item; `group_vec_axioms` is what ties `vec.len()` to
`vec@.len()`, and **no other pattern in the tree uses that group**.

## 7. Deliverable 5 — the `harness/tools/composition.py` bug class

⚠ **I did not edit that file.** `--check` currently fails on the population
(p25 has no gate record yet) and will fail with `built but unclassified: p25`
once it does. **That is the check working.**

**Proposed class: `temporal`**, joining `p27 p28 p29 p32 p34` → 6 rows. It fits
the declared axis exactly — *the ACCESS OUTLIVES THE OBJECT'S LIFETIME* — and
the declaration's own hedge (*"not necessarily its STORAGE"*) is not even needed
here: the storage really is returned.

**Proposed `CAVEATS['p25']` wording:**

> the retirement is not a `free` THE PROGRAM CALLS — `realloc` retires the old
> block as a side effect of GROWTH — and what is stale is an INTERIOR pointer
> into the middle of a container rather than a pointer to a whole object. ⚠ p25
> is the only row whose C rungs call `realloc` at all (1 of 32,
> `controls/no_reloc.py`). ⚠⚠ Its safety line is the only one in the temporal
> family that REPAIRS NOTHING ABOUT THE ANSWER: both branches of the hardened
> READ compute the same value, because `realloc` copies, so the conjunct buys
> memory safety and nothing else — and the standard-clean form of the repair
> (the unconditional re-derive, the only one DR 400 cannot reach) is measured at
> HALF its cost. ⚠⚠ It is also the only temporal row whose bug the LADDER
> DELETES rather than proves: safe Rust cannot hold the interior pointer, the
> index port it forces has no bug at all, and the R5 obligation is the spatial
> residue `curi < toks.len()`.

⚠ **On the catalogue's column, which the task asked about:** it calls this row
*"growth overflow, stale pointer"*. **The growth-overflow half is SPATIAL and was
refused on sight; what shipped is the stale-pointer half alone.** Proposed
replacement column: **"stale INTERIOR pointer across a `realloc` growth"**, axis
**temporal**.

## 8. PROTOCOL rule 6 — the contract hash and its three disclosed moves

As first written, before any measurement of its own pins:
`54088d20a749069b0111e674b01f80ba050fa11b70030219e97e7725b3fa4dba`.

⚠ **On a new pattern `git show HEAD:… | diff -` is VACUOUS** — the pattern lands
in one commit, so it always prints nothing and always looks like it passed. The
recorded hash is the only evidence, so the **verbatim block text** was saved
beside it (`.temp/t157/contract_first_written.json`, 26 255 bytes), which is the
standard `TASK_156` fixed after p34's first move proved unreconstructible.

| to | what moved |
|---|---|
| `a4b9e575…` | **one sentence of `why`** — the `mgr155` `malloc` census §3 refuted. Rule 6's second half exactly: a frozen declaration is evidence about *when* it was written, not about whether it is still true. |
| `8cef5a43…` | **25 unicode escapes**, `\\u26a0` → the single escape JSON decodes to `⚠`, which is p27's/p32's/p34's convention. Verified cosmetic: parsing both and normalising the escape gives identical objects. |
| `c41099be…` | **the tail of `why`.** The gate's `idiom-named-spelling` stage failed run 1: the SHARED named-spelling paragraph must be **byte-identical** and mine was a paraphrase. p34's is spliced in verbatim. The block was re-serialised in the same edit; verified that the parsed objects differ in `idiom.why` and nothing else, that `why`'s p25-specific prefix is unchanged, and that the tail equals p34's exactly. |

No `required`, `forbidden`, `identity`, `obligations`, `driver`, `collapse` or
`miri` entry moved at any of the three steps — checked by parsing each pair and
diffing the objects rather than by reading the text. The intermediate texts are
on disk (`.temp/t157/contract_*.json`). **Final: `c41099be4dfdc646…`.**

## 9. ⚠⚠ A MEASUREMENT DEFECT IN HOW THIS PROJECT READS `marginal_ir_per_call`

Found while building §10's table, and it is not about p25.

`harness/check.py::_cg_ir` reads callgrind's `summary:`/`totals:` line — **the
WHOLE PROGRAM** — and writes it into the gate record as
`marginal_ir_per_call`. `results/pNN-*.json`'s `kernel_exclusive_ir` is the
`kernel` symbol alone. On most rows the two move together. **On p25 they do not,
because p25's kernel calls out of itself** — into `realloc`, into
`RawVec::grow_one`, and at `-O0` into the `chunks_exact` iterator — and the two
columns then answer different questions and, twice, give opposite answers:

* **the gate record shows an R4 → R5 "proof tax" of `+269.52` Ir/call on `large`
  `-O3` (5379.39 → 5648.91), and there is no such thing.** Measured directly
  (`.temp/t157/irprobe/`): the two kernels cost **exactly 9104.17** (`-O0`) and
  **exactly 4152.71** (`-O3`), and `realloc` (205.36), `finish_grow` (159.48),
  `grow_one` (127.00) and `malloc` (84.00) are identical to the instruction in
  both binaries. What differs is three **unnamed libc routines**: 461.00 Ir/call
  in the R4 binary against 718.28 in the R5 one.
  **Conclusion (stands alone): the R4 and R5 kernels cost identical Ir at both
  levels; the whole-program delta is not a proof cost.**
  ⚠ **Mechanism: OPEN, and deliberately not asserted** — consistent with glibc
  copying different amounts inside `realloc` under two different heap layouts,
  which is the same class of fact this row studies, but not separately measured.
* **the two columns invert R2 against R3 at `-O0`.** Kernel-only they are within
  0.6 % (`small` 1710.46 vs 1700.99); whole-program R3 is **1.75× DEARER**
  (2741.37 vs 4807.90), and 1.75× again on `large`. At `-O3` the two columns
  agree **to the instruction** (both give R3 − R2 = −191.13 and −982.75),
  because everything is inlined into `kernel` there.

**I did not change `check.py`.** The gate's use of the whole-program number is
correct *for what stage 3b is* — an anti-collapse floor on the whole program.
What is wrong is reading it as a per-rung cost, and `p25/NOTES.md` 8a publishes
both columns side by side with the caveat rather than picking one.
⚠ **The record's own comment already recommends `kernel_exclusive_ir` for
cross-run comparison** ("structurally immune: 0 of 288 triples moved") — the gap
is that it says nothing about cross-RUNG comparison, which is the use that
misfires here. **Candidate `.memory/03-measurement.md` entry; not written by me
(subagents do not edit `.memory/`).**

## 10. Gate

```
results/gate/p25-realloc-growth.json
  verdict          PASS
  failures         []
  blocked          []
  loud             []
  contract_sha256  c41099be4dfdc6464941b3e60ea6b3e0067b8156735c4748b1ecdf5b6d00fddd
  published_table  FRESH   table_render  FRESH
  verus.rs         10 verified, 0 errors; 4 TCB items; twin config 12 / 0
  miri             8 rows, ub=False on all
```

✅ **The record certifies the exact tree**: every one of its `source_sha256`
entries re-hashes to the file on disk (0 stale, 0 missing), checked after the
last documentation edit rather than assumed. The last run was made *after* every
doc change precisely so that this would be true.

Three earlier runs failed, all on first-run bookkeeping, and each is worth
recording because each is a trap a new pattern walks into:

1. **`idiom.why` must carry the SHARED named-spelling paragraph BYTE-IDENTICAL.**
   I had written a faithful paraphrase; the gate wants the 11 003-byte block
   (`sha256 59748cce2db5…`, *"NAMED-SPELLING STANDARD"* → *"p01 and p08
   neither"*) copied verbatim from another pattern. Also: **NOTES.md needs one
   `SLB-TRUSTED-ARGUMENT <src> <item>` section per item `_is_trusted` governs**
   — two here, not four, because `load_input` and `emit` carry no `ensures`.
2. **Three `controls/*.json` sidecars went STALE under me**, because I re-ran
   them before making the last edits to `inputs/gen.py`, `c/kernel.h` and
   `controls/safety_line.py`. Stage 9b caught all three by name. ⚠ The task
   file's *"generate control JSONs AFTER the sources are final"* is about
   `measure.py`; **stage 9b makes the same demand of `controls/` and is a
   separate deadline.**
3. **Stage 9c's one-run lag**, exactly as the task file warned: on a brand-new
   pattern the loop is `measure` → `report` → gate → `report` → gate.

`python3 harness/tools/composition.py --check` → `rc=1`,
`built but unclassified: ['p25']`. **That is the check working**; §7 proposes
the class and the caveat. ⚠ `rc` was read from the process, not from a pipe.

## 11. Problems, and what I did NOT do

**Not done, deliberately:**

* **No `.memory/`, `RECAP.md`, `results/SYNTHESIS.md` or
  `harness/tools/composition.py` edit** — forbidden to this role. §7 and §9 are
  proposals for the manager.
* **Neither repair's spelling was searched** (§4), and no in-contract R3 spread
  is published: R2 and R3 differ in **two** levers at once (the walk and the
  opcode dispatch), so their gap is not a spread for either.
* **No sweep-band law.** `inputs/gen.py --sweep` writes 57 bands (O, R and T
  axes) and `controls/no_stale.py` censuses them, but nothing was fitted on
  them.
* **No wall-clock claim.** The timing block is in the measurement record and
  nothing here rests on it.
* **The `arm_unsafe_ptr.rs` R4 that holds the pointer is a CONTROL, not a
  rung** — it is not in `build.py`'s cell tables and is never measured.

**What I am least sure of, named so a reviewer can attack it:**

* ⚠⚠ **The DR 400 reading in §4 is a STANDARDS ARGUMENT, not a measurement.**
  *"`cur` is indeterminate after `realloc` returns whether or not the block
  moved"* is my reading of C11 7.22.3.5p4 plus DR 400, and no tool on this box
  can confirm or refute it — ASan cannot, because its allocator always moves, so
  under ASan R1h's true branch is only ever taken when no `realloc` happened.
  **The COST half is measured and stands independently**: the unconditional
  re-derive is ~2× cheaper than the conjunct at every cell, which is a reason to
  prefer it whatever the standard says.
* ⚠ **The mechanism behind the R4/R5 whole-program delta (§9) is OPEN.** The
  conclusion — kernels identical, delta outside the kernel — is measured; the
  heap-layout explanation is not.
* ⚠ **`sanitizer_expect` models ASan and not glibc**, on purpose (`NOTES.md` 2b).
  It is the checkable choice and the conservative one, but it means the gate's
  `fires` column is not a claim about what glibc does — `controls/reloc_probe.py`
  is, and it says exactly one growth in each shipped adversarial window
  relocates.
* ⚠ **`adversarial-many` was written expecting the `32 → 64` growth to relocate
  in later rounds. It does not** — `reloc_probe.py` refuted the prediction and
  `inputs/gen.py`'s docstring now says so. The input is still useful (four
  SAVE/grow/READ rounds, all four `fires` under ASan) but only one of the four
  reads retired storage under plain glibc.

**Worked around, disclosed:**

* `controls/rederive.py`'s first anchor, the bare statement text
  `v = (uint64_t)*cur;`, matched **twice** in `c/kernel.c` — once as code and
  once inside the comment that spells out what the hardened rung writes — and
  the control **refused to build**. That is the assert-your-substitution-count
  rule doing its job; the anchor is now newline-and-indent anchored.
* `controls/safety_line.py`'s first version asserted a **pure addition** and
  failed: the diff is `+3 / −1` because the read **moves** into the guarded
  branch. It now checks the exact line multiset, which says more.
* **`inputs/gen.py` shipped a FALSE prediction of my own and `reloc_probe.py`
  refuted it**: `adversarial-many`'s later rounds were expected to relocate at
  `32 → 64` and they do not — the token block is at the top of the heap by then.
  The docstring now says so. Under ASan all four rounds still `fire`; under plain
  glibc exactly one of the four reads retired storage.

## 12. For the manager's reconciliation (PROTOCOL rule 2)

⚠ **Reconciliation is the manager's job, not mine**, so this is the raw count and
not a total. **Four manager/task-file claims were contradicted by a
measurement in this task**, plus **two of my own predictions were self-refuted**
before shipping:

| # | claim | source | outcome |
|---|---|---|---|
| 1 | the hardened cell folds `SENT` on relocation | `TASK_157`, `.temp/mgr155/` §5 | **refuted** — it makes the answer allocator-dependent and stage 2 unsatisfiable in principle (§2) |
| 2 | the sentinel choice is the row's least-certain call and must be decided and disclosed | `TASK_157` "the thing that will bite you" | **dissolved** — the shipped cell folds no sentinel at the safety line; the `+4`/`+5` static cost is not paid (§2a) |
| 3 | *"C rungs that call `malloc` at all → p10 p27 p28 p29 p32 p42 (6 of 30)"* | `.temp/mgr155/` §6 | **refuted** — 5 of 32; two prose false positives, one real allocator missing (§3) |
| 4 | the gate's `marginal_ir_per_call` is a per-rung cost | implicit in how the record is read | **refuted** — it is whole-program, and it shows an R4→R5 proof tax of +269.52 Ir/call that does not exist (§9) |
| 5 | *(mine)* the safety-line diff is a pure addition | `controls/safety_line.py` v1 | **self-refuted** — `+3 / −1`, the read moves |
| 6 | *(mine)* `adversarial-many`'s later rounds relocate at `32 → 64` | `inputs/gen.py` v1 | **self-refuted** by `controls/reloc_probe.py` |

⚠ **Two things the manager got RIGHT and I checked rather than assumed**, so the
next agent does not re-run them: the `p34`-distinctness argument (§7's caveat is
it, in the row's own words, and `controls/no_reloc.py` is the census behind it),
and *"the harm window is one growth wide, tune the adversarial input to it"* —
`reloc_probe.py` confirms `16 → 32` and nothing else, under the shipped driver.
