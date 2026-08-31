# TASK_153 — landing `p35`'s review corrections. Report

**Role: research engineer.** **All five majors and all three minors in scope are
LANDED**, in **one re-measure** and the documented **gate → `report.py` → gate**
loop. Final state, read out of `results/gate/p35-tagged-union.json` with
`json.load`, never grepped:

```
verdict PASS-WITH-BLOCKED-ROWS   failures 0   blocked 3   loud 6   complete_run True
contract_sha256 7f85ac5ea2bca031f60e8d7600d7326b0134cd5cfb450da9a2dee99bd9d90d56
verus 16 verified / 0 errors / pinned 16      twins 4      identity O3 exact, O0 norel
miri 8 runs / 0 UB      controls_json all five FRESH      published_table FRESH
```

`blocked = 3` is the row's R5 result, not a defect. Tree-wide, derived from the
records: **30 patterns, 27 `PASS` + 3 `PASS-WITH-BLOCKED-ROWS`, 0 failures
anywhere, blocked `p01=1 p42=1 p35=3`, 60 measurement records `0 STALE`,
catalogue 48 rows.**

⚠ **`p35` IS NOW FINDABLE IN THE SYNTHESIS**: `results/synthesis.md` regenerated
— `Patterns: **30**. Gate records: **30**`, and `p35` appears **14** times where
it appeared **zero**. `results/SYNTHESIS.md` (CAPITALS) **untouched** —
`git diff` on it is empty.

I touched **no** `.memory/`, **no** `RECAP.md`, **no** `results/SYNTHESIS.md`,
**no** `harness/` file, and ran no `git add`/`git commit`. Scratch is
`.temp/t153/` only; `.temp/t152/` was **copied from, never written to**.

---

## 0. The prediction, written BEFORE the run — and it is an exact hit

`.temp/t153/PREDICTION.md` was written before `harness/measure.py p35` started.
⚠ **Which do I expect to move first, `Ir` or `md5`? NEITHER** — every edit to a
measurement-hashed file was comment-only, so I predicted `source_sha256` as the
*only* derived-fact column that moves, and by exactly six entries.

| predicted | measured (`.temp/t153/measure_diff.txt`) |
|---|---|
| `source_sha256`: **exactly 6** movers, named | **6**, and they are exactly the six named |
| `input_sha256`: **0** | **0** |
| `Ir` (`kernel_exclusive_ir`/`main_exclusive_ir`): **0** | **0** of 32 cells |
| `static` (`md5_raw`, `md5_fn`, `md5_norm`, `n_raw`, `binary_text_bytes`): **0** | **0** |
| `checksum`: **0** | **0** |
| moving legitimately: `generated_utc`, `git`, wall clock | 3 provenance + 101 wall-clock |
| gate run 1: **`FAIL`, on `[tables]` ONLY** | `FAIL`, **2** failures, **both** `tables` |
| gate run 2: `PASS-WITH-BLOCKED-ROWS`, 0 failures, blocked 3, loud 6 | exactly that |
| `proof_mutants` **9/9** with `X1` **VERIFYING** at 16/0 | 9/9, `X1` `{'verified': 16, 'errors': 0}` |
| `rust_bug` 0 problems, new Miri row `ub=True` | 0 problems, `adversarial-exhaust ub=True` |
| `--check-stale` 0 STALE · `composition --check` OK · `temp_citations` OK | all three |

```
leaves before=1356 after=1361  MOVED=110
  provenance      3      source_sha256   6      wall-clock    101
source_sha256 movers: c/kernel_hardened.c, inputs/gen.py, model.py,
                      safe_tuned.rs, unsafe.rs, verus.rs
```

The 5 added leaves are `wall/large.bin/warning` (min-to-median spread > 10 %) on
5 cells — a wall-clock draw, and `NOTES.md` 8 publishes no wall-clock headline.

⚠ **The one way I said the prediction could be wrong** was `md5_fn` moving
because I added LINES to three `.rs` files: I argued a surviving panic pad passes
a *pointer* to a `core::panic::Location`, so the line number is rodata and not an
immediate, while the file NAME's length is what becomes one — and no file was
renamed. **Measured: 0 static movers.** The only line-number movement anywhere is
the gate record's `verus.tcb_items[*].line` (9 items, shifted by my comments) and
`M5b`'s reported `assume(` line, `513 → 551`, both disclosed in `NOTES.md` 11.

**Everything else the gate derives is byte-identical across the change**:
`identity`, `clause_deletion`, `requires_strength`, `verified_twins`,
`proof_domain`, `adversarial`, `derived_contract`, `driver_loops`,
`idiom_audit`.

---

## 1. ⚠⚠⚠ M1 — the decision, the justification, and which endpoint was unsearched

**I TOOK (b): keep the shipped `R4` and publish `373.61 Ir/call` as THE PRICE OF
THE `identity` PIN.** The manager's guess was right, and here is why **(a) is not
a live option at all**, which is stronger than "(b) is preferable":

* **Lever 2 (`chunks_exact(2).take(nops)`) cannot ship.** Re-measured a third
  time (`.temp/t153/verus/p_chunks.rs`) and it is **four** errors, not the one
  the build quoted: `core::iter::adapters::take::Take`,
  `core::slice::iter::ChunksExact`,
  `core::slice::iter::impl&%90%default%take` and
  `core::slice::impl&%0::chunks_exact` are **all** `is not supported`. ⚠ **`take`
  is unsupported as well as `chunks_exact`** — the build report never said that —
  and `identity: unsafe ≡ verus` chains R4 to R5.
* **Lever 1 (the reslice) IS available** — `2 verified, 0 errors`
  (`.temp/t153/verus/p_reslice2.rs`), confirming the reviewer — **but giving it
  to R4 makes R4 DEARER by `+8.00 Ir/call` at `-O3`.** So the only live form of
  (a) moves the published gap the *wrong* way and changes no conclusion.

**Which endpoint was the weaker-searched one: `R4`.** R3's side had **two**
levers named; R4's had **one named and zero counterfactuals measured**. Sixth
instance of the flattering-direction trap.

**My own four-arm rig, with the two shipped rungs as controls that must reproduce
the committed record** (`.temp/t153/rig/`, `harness/build.py::rust_flags` +
`check.py`'s `(Ir₂₀₀−Ir₁₀₀)/100` probe):

```
arm                        O3 large   O3 small   O0 large   O0 small
safe_tuned R3  CONTROL      3060.92     684.55   17783.37    4223.32   = record
unsafe     R4  CONTROL      3231.48     712.02   14591.09    3332.22   = record
R4 + lever 1 (reslice)      3239.48     720.02   14369.09    3302.22
R4 + levers 1 AND 2         2857.87     653.71   20626.55    4691.10
all four arms: 751388249273516652 / 3733036646187536480  (IDENTICAL)
```

**All eight control cells reproduce `results/gate/p35-tagged-union.json`
exactly**, so the rig is calibrated against the tree and not against itself.

**Two results, one of which the review did not have:**

1. Matched on the op-walk, **R4 wins by 203.05 `Ir`/call (6.63 %) on `large` and
   30.84 (4.51 %) on `small`** — the sign reverses on both inputs. The honest
   figure is **373.61 `Ir`/call (11.56 %)**, the price of the pin. `170.56` is
   46 % of it.
2. ⚠⚠ **NEW, AND IT MAKES THE RETRACTION INDEPENDENT OF THE COUNTERFACTUAL: the
   sign is not stable across optimisation level either.** At `-O0` the
   **shipped** pair already runs the other way — `R4 14591.09` against
   `R3 17783.37` on `large`, **17.95 % in R4's favour**, with **no matching at
   all**. Mechanism, controlled to one change on one rung: the same pair of
   levers is **−373.61 `Ir`/call at `-O3` and +6035.46 at `-O0`**. R3's win is an
   optimiser-dependent iterator lever, not a property of safe Rust.

**The sentence *"R3 beats R4"* survives in no file.** Landed struck-not-deleted
in `NOTES.md` 3 (iii), and the corrected framing is in `unsafe.rs`'s and
`safe_tuned.rs`'s headers, `NOTES.md` 8's *does-not-publish* list.

---

## 2. ⚠⚠⚠ M2 — the band claim, per figure; and the *"mechanism OPEN"* hedge is RETIRED

**Band membership, stated per figure rather than as a blanket** — every delta
read out of the gate record (`.temp/t153/bands_and_deltas.txt`), all **16** cells
(2 compilers × 2 opt × 2 inline modes × 2 inputs), **16 of 16 cheaper for R1h**:

| cells | Δ | band |
|---|---|---|
| gcc `O3` small (both modes) | **−13.71** | ⚠ `2.00…16.00` — *a coin flip, DO NOT QUOTE ALONE* |
| gcc `O3` large, clang `O3` small/large (both modes) | −85.91 / −40.40…−59.02 / −215.86…−298.34 | `≥16.00` — *every one is real* |
| **all eight `O0` cells** | **−18.35** (small) / **−164.50** (large), **numerically identical on gcc and clang and in both modes** | `≥16.00` |

So: **one** of the four published `-O3` figures is inside the coin-flip band —
the sentence said none were — and the conclusion survives on the `O0` cells the
build report never used. ⚠ I also recorded that **the band is a borrowed
yardstick**: it is calibrated on the *derived environment-block correction*
column, so what does not depend on it is the direction, 16 of 16.

### ✅✅ The hedge is gone, and the mechanism is closed from BOTH sides

The denominator: `marginal_ir_per_call` is `(Ir@200 − Ir@100)/100`, i.e. the mean
over calls **100…199**. My own simulator of `common/driver.c` + `c/kernel.c`
(`.temp/t153/failed_stores_t153.py`) **reproduces both published checksums
exactly** and gives

```
small.bin  all200 = 3.6700/call   calls100-199 = 3.6700/call
large.bin  all200 = 32.7550/call  calls100-199 = 32.9000/call   <- TASK_148 used 32.7550
```

**With `32.90`: exactly `5.0000` `Ir` per failed tag store on ALL EIGHT `-O0`
cells** — both compilers, both inline modes, both inputs. (`TASK_152` closed four;
the `whole` mode gives four more.) A check that does not use the constant at all:
`164.50/18.35 = 8.964578` and `32.9000/3.6700 = 8.964578`, to six decimals.

⚠⚠ **AND I CLOSED IT AT THE INSTRUCTION LEVEL, WHICH THE REVIEW DID NOT.**
`harness/asm.py diff` on the two `-O0` kernels moves a **five-instruction block
and nothing else**, on **both** compilers, with static counts identical either
side (gcc 293/293, clang 259/259):

```
gcc    mov -(%rbp),%rax · shl $,%rax · add %rbp,%rax · sub $,%rax · movb $,(%rax)
clang  mov -(%rbp),%rcx · lea -(%rbp),%rax · shl $,%rcx · add %rcx,%rax · movb $,(%rax)
```

**A `-O0` tag store is five instructions; R1h does not execute it on the failure
path; `5.0000 × failed stores` is the entire delta.** `-O3` remains OPEN and is
now marked as the *only* open half (the constant spans 2.61–11.01 there).

⚠ And the honest framing follows: **R1h executes strictly less work than R1** —
the bug wastes a store — rather than *safety is negative-cost*.

---

## 3. ⚠⚠ M3 — `X1` shipped as a control arm, verdict RE-DERIVED not quoted

`controls/proof_mutants.py` now runs **9 arms, 9 as designed**. I re-derived
`X1` twice, independently of `TASK_152`:

```
$ python3 .temp/t153/x1_probe.py                      # standalone, mutant to a .temp/ mirror
deleted conjuncts: 3 -> 0
X1-delete-variant-requires   verified=16 errors=0 rc=0
  shipped obligation count = 16; unmoved = True

$ python3 patterns/p35-tagged-union/controls/proof_mutants.py
  ok   X1-delete-variant-requires {'verified': 16, 'errors': 0}
9/9 arm(s) as designed
```

**And I executed the REAL gate predicate to find what catches it**, rather than
quoting the planted-gate run (`.temp/t153/x1_pin_probe.py` drives
`vparse.parse` + `check._clauses` against `spec.md`'s `verus.items`, the same
comparison `check.py` makes at `proof-pin`):

```
SHIPPED   verus.rs: 0 item(s) drift from the spec.md pin
X1 MUTANT verus.rs: 3 item(s) drift from the spec.md pin
   proof-pin  pay_d_gt1  requires: ['i < v@.len()'] != pinned [..., 'v@[i as int] is d']
   proof-pin  pay_i      requires: ['i < v@.len()'] != pinned [..., 'v@[i as int] is i']
   proof-pin  pay_o      requires: ['i < v@.len()'] != pinned [..., 'v@[i as int] is o']
every X1 drift is a `requires`: True
```

I did **not** re-plant `X1` into the tree — `TASK_152` did that with a
byte-verified restore, and re-planting risks leaving a mutated source in
`patterns/`. The pin half is now re-derived without planting anything.

**The headline as landed** (`NOTES.md` 6b, `spec.md` prose, `verus.rs`,
`proof_mutants.py`'s docstring, `union_oracle.py`, `README.md`):

> the correct-variant obligation **cannot be weakened by editing the abstract
> machine** — `M3`/`M6` measure that, and it is `p32`'s opposite — and it **can
> be deleted outright from the trusted readers' `requires`**, with the proof
> staying green at the pinned obligation count. **Configuration B RESISTS the
> same deletion and configuration A does not**, so the gate does not merely force
> the weaker of two available proofs: **it forces the one whose central
> obligation can be DELETED WITHOUT THE GATE NOTICING.** *"Imposed by the type
> system at the operation"* is true of **configuration B only**.

⚠ `union_oracle.py`'s arm `B2` **is that same mutation** in configuration B, and
it FAILS at the read — so the contrast is a shipped pair of arms, not an
argument.

**What the shipped configuration's obligation rests on, said plainly**
(`NOTES.md` 6a): **(a)** the member read matching the item's name, and **(b)**
`i < v@.len()` licensing `get_unchecked` — **neither tested for strength**,
because `5c-twin` is the stage that would and it is one of the three blocked
rows; the backstops are stage 3c identity and stage 8 Miri.

---

## 4. ⚠⚠ M4 — the retracted clause, swept over EVERY file

`c/kernel_hardened.c:12-16` struck, `p42` house style, with the corrected
mechanism in its place. ⚠ **I grepped the whole tree, not just the file the
reviewer named** — and the naive `grep` for it **fails**, because the clause
straddles a comment-continuation newline:

```
grep -rl "scheduling difference and nothing more"   ->  RECAP.md, .tasks/TASK_153.md   (MISSES the .c!)
python3 re.compile(r"scheduling\s+difference\s+and[\s*]*nothing\s+more")  -> the real set
```

Live occurrences outside `.temp/` and `.tasks/`: `c/kernel_hardened.c` (**the one
unstruck copy — now struck**), `spec.md` (already struck), `NOTES.md` (the
disclosure table), `RECAP.md` (the manager's), plus the two **generated**
artefacts `results/tables/p35-tagged-union.md` and
`results/gate/p35-tagged-union.json`, which carry the struck fence text and are
regenerated. **No unstruck copy survives anywhere.**

✅ **The rule-6 disclosure is now checkable by a tool, not by assertion.** The
pattern is committed, so `harness/tools/contract_diff.py p35` works where it
could not at `TASK_148`:

```
block sha256  HEAD: e8e7199af62d589d4e709cba9ffcd99f4aefd23c98bb56efd0e1902f337b73ba
block sha256  tree: 7f85ac5ea2bca031f60e8d7600d7326b0134cd5cfb450da9a2dee99bd9d90d56
10 path(s) moved: idiom, idiom.why, miri, miri.reason, verus,
                  verus.twin_justifications{,.verus.rs,.pay_i,.pay_o,.pay_d_gt1}
IDENTICAL: idiom.required, idiom.forbidden, identity, verus.obligations,
           verus.twin_obligations, verus.items, verus.unsafe_justifications,
           requires, ensures, driver, collapse, note, kernel, model
```

**Nothing the gate pins moved, and that is a tool's output.** `NOTES.md` 11
records the second move with the three-hash chain and the per-key table.
`.temp/t153/contract_diff_{before,after}.log`.

---

## 5. ⚠⚠ M5 — decision: KEEP the shipped configuration, CORRECT the justification

**I did not adopt configuration C.** Reasons, stated so the choice is reviewable:

* it does **not** reduce `blocked` — the field read still has no safe twin;
* it takes the TCB from **nine items to ten**, i.e. one more trusted item in
  exchange for a narrower axiom on three of them, which is a real trade and not
  obviously the right way round;
* the reviewer measured it as a **proof**, not as a **rung**: nobody has checked
  it survives the `identity` pin with a mirrored `unsafe.rs`, so adopting it
  risked a second re-measure and a failed identity pin — over the task's budget.

**What I did instead is the half that is not optional**: the justification now
names **both** unchecked operations, everywhere it appeared — `spec.md`'s
`twin_justifications` (all three, hashed), `spec.md`'s prose, `verus.rs`'s module
note, `verus.rs`'s trusted-items comment, `controls/union_oracle.py`'s docstring
and its `invariant`, `NOTES.md` 6a and 6d. `pay_d_gt1` is counted at **three**
axioms, not two. Configuration C is recorded as **available and not shipped**
with its measured evidence, so the next agent does not re-derive it.

⚠ `NOTES.md`'s `SLB-TRUSTED-ARGUMENT` sections **always said "two unchecked
operations"** — it was the *summary* sentence above them that said one. That is
`PROTOCOL` rule 13's shape exactly (the body is maintained, the header rots), and
it is recorded as such in 6a.

---

## 6. Minors

**minor 1 — `miri.reason`. ⚠⚠ THIS ONE GREW: the counter-example is REACHABLE ON
A SHIPPED INPUT, not merely constructible.**

I re-ran the reviewer's probe with its positive control (`.temp/t153/miri/`):
`Pay{i:..}` then `.d` is silent; `Pay{o:7}` then `.i` is
*"reading memory at `alloc…[0x0..0x8]`, but memory is uninitialized at
`[0x4..0x8]`"*. Then I asked the question the review did not: **which
`(tag, live member)` pairs does `p35` actually reach?**
(`.temp/t153/confusion_pairs.py`, over all 24 committed inputs.)

```
tag PTR(o:u32,4B)  over live INT(u64,8B)   n=  80  narrowing 8B -> 4B   all initialised
tag DBL(f64,8B)    over live INT(u64,8B)   n= 200  same width           all initialised
tag DBL(f64,8B)    over live PTR(o:u32,4B) n= 160  WIDENING 4B -> 8B    UNINITIALISED
```

The third row is **`adversarial-exhaust.bin`**, and Miri **reports it**:

```
$ miri ... arm_unsafe_bug.rs -- <reduced adversarial-exhaust.bin>
error: Undefined Behavior: reading memory at alloc1827[0x0..0x8], but memory is
       uninitialized at [0x4..0x8]   --> arm_unsafe_bug.rs:127  pays[idx].d
```

⚠ **The reviewer's reason for calling it unreachable was wrong** — it considered
only the `.i` direction (*"`T_INT` is only ever published in the same arm that
stores an `i` payload"*) and missed the `.d`-over-`o` direction, which is the
same widening.

**Nothing published moves, and two things sharpen.** Stage 8 runs the CORRECT
rung, which never confuses a cell, so `0 UB` on 8 inputs stands; the
DBL-confusion row's `UB=False` stands because that confusion is *narrowing*
(re-measured: `rc=0`, checksum `162643197298427456`, matching the record). What
changes is the SCOPE: **Miri is silent on this bug class only where the read is
no wider than the write** — and ⚠⚠ **the widening case exists ONLY in the Rust
rungs**, because `uint8_t *` is 8 bytes here so all three C members are 8 bytes.
**It is therefore another consequence of the disclosed offset-for-pointer
substitution, which turns out to change which instrument fires on the SILENT harm
too and not only on the loud one.** The NATIVE Rust arm still reproduces C bit
for bit on that input (`1705852038987163136`).

✅ **`controls/rust_bug.py` now runs Miri on `adversarial-exhaust` as the
must-fire arm for the initialisedness half**, with an assertion that fails the
control if it stops firing. Its docstring, table and `invariant` are corrected.
That closes a real coverage gap: the control ran Miri on the DBL and PTR inputs
only, so **the one input that could refute the generalisation was the one input
Miri never saw**.
Corrected in: `spec.md`'s `miri.reason` (hashed), `spec.md`'s `miri.required`
prose row, `NOTES.md` 7 (finding 1 and the table), `README.md`, `model.py`.

**minor 2 — the catalogue. ⚠ `.memory/` IS THE MANAGER'S; I LIST, I DO NOT
EDIT.** `.memory/06-catalogue.md:414`, `p35` cell. Independently re-verified at
`TASK_153`:

| # | stale claim, quoted | status |
|---|---|---|
| 1 | *"It is the TYPE axis, which still has **ONE** built row"* (twice — also in the `TASK_134` re-triage sentence) | **FALSE.** `composition.py --check`: 30 patterns, **type 2** |
| 2 | *"a twin must be justified away → `n_twins == 0` → **hard FAIL** … `p35` has **NO LEGAL CONFIGURATION**"* | **REFUTED.** The record shows `twins: 4`; `twin is None` **with** a justification is `rep.block` + `rep.shout`. Row is green |
| 3 | *"`p35` **IS DEAD** AND THE CATALOGUE CLOSES"* | **REFUTED by construction** |
| 4 | *"`p35` has **no configuration in which its safety obligation is CHECKED**"* | **REFUTED.** The wrapper's `requires` is checked at every call site — `proof_mutants.py` arm `M1` |
| 5 | *"`verus.twin_justifications` … is in **0 of 26** shipped contracts … its only occurrence under `patterns/` is `p17`'s NOTES REJECTING an axiom"* | **STALE.** `grep -c` over `patterns/*/spec.md`: exactly one file has it — `p35`'s — with **3 entries** |
| 6 | *"THE WEAK LINK … **none of this is GATE-CERTIFIED** … Execute that before treating the twin/`n_twins` interaction as settled"* | **DISCHARGED.** `union_oracle.py` `G-A`/`G-B` run the real `_scan_unsafe_sites` against a synthetic pdir; re-run here, 9/9 |
| 7 | citation `harness/check.py:**3941**` for `cand += _include_literals(txt)[0]` | **ROT.** Re-verified: the line is at **`harness/check.py:3972`** |

⚠ Item 5 is a *seventh* thing worth fixing and was not on the reviewer's list of
five; items 1–4 and 6 are the five, and 7 is the citation.

**minor 3 — `results/synthesis.md`.** Regenerated: **`Patterns: 30`**, `p35`
mentioned 14 times, no `LICENCE STALE` verdict anywhere. `synthesis/licence.py
--emit synthesis/licence.json` was run **first** (30 patterns, 120 pair
verdicts), then `synthesize.py`. ⚠ Note what the synthesis itself says about the
M1 row: `p35 | −26.50 | −170.56 | UNDEC` — the R3−R4 pair is **not licensed to be
differenced** there either, independently of M1.

---

## 7. NOT fixed, recorded so it is not silently absorbed

* **Stage 9b hashes a control sidecar and never reads its own verdict.**
  Re-confirmed at `TASK_153`: `grep -n "cells_ok\|arms_as_designed"
  harness/check.py` → **no hits**; `check_control_json_pins` compares
  `derived_from_sha256` and nothing else. **This task made it sharper, not
  softer**: `proof_mutants.json` now carries `arms_as_designed: 9` /
  `arms_total: 9` and `rust_bug.json` carries `problems: []`, and a run that
  regenerated them at `7/9` or with a non-empty `problems` list would still be
  `FRESH` and the gate would still say `PASS`. A `check.py` change is a
  30-pattern re-gate and a different bundle. **Reported, not fixed**, per the
  task file.
* **`results/SYNTHESIS.md` §7** still says *"every claim this document makes
  about the type axis rests on ONE pattern"*. It is hand-written and I may not
  edit it — **the manager owns this**, and it is the last thing between `p35` and
  *finished* now that the generated synthesis is current.
* **`idiom.why`'s DBL sentence was deliberately left**: *"tag DBL over an **int**
  payload … not Miri on the Rust reproduction"* is correctly **scoped to the
  narrowing case** and is true; the fence's `miri.reason` right below it now
  carries the full widening correction. Editing it would have cost a third gate
  run for no change in truth value.

---

## 8. What I did NOT do, and what I am unsure about

1. **I did not adopt configuration C** (§5). It is measured as a proof, not as a
   rung; whether it moves `Ir` or survives the `identity` pin is **unmeasured**,
   and that is recorded in `NOTES.md` 12.3c rather than assumed.
2. **I did not re-plant `X1` into the tree and re-run the whole gate** (§3), and
   I did not build the `TASK_003_REVIEW` shape where the mutation **and** the pin
   move in one commit — which is what the blocked twin exists to catch.
   `NOTES.md` 12.3b says so.
3. **`NOTES.md` 3 (iii) executes decision (b) in substance but does not name
   *"(a)"* and *"(b)"* as such.** It publishes `373.61` as the pin's price, says
   R4-with-levers wins by 6.63 %, and gives the two reasons that spelling cannot
   ship — which is the whole of (b). ⚠ I judged the explicit *"(a) was
   considered and rejected"* framing not worth a **third** gate run, because
   `NOTES.md` is in the gate's `source_sha256` and there is no cheap doc fix.
   **If the manager wants that sentence, it is free the next time `p35` is
   gated.**
4. **`-O3`'s mechanism is still OPEN**, and only `-O3`. I did not disassemble the
   `-O3` kernels to explain the 2.61–11.01 spread.
5. **The `-O0` cross-rung comparison in M1 result 2 is a record read, not a fair
   safe-vs-unsafe measurement.** At `-O0` no rung's spelling is optimised and the
   column is dominated by un-inlined iterator and wrapper machinery. Its job is
   to show the **sign is not stable**, and the controlled claim beside it — the
   same pair of levers on the *same* rung, `−373.61` at `-O3` against `+6035.46`
   at `-O0` — is the one that carries the mechanism.
6. **I did not gate any other pattern.** The other 29 verdicts were read out of
   their records only.
7. **I did not verify the reviewer's `.temp/t152/verus/c4_split.rs` numbers by
   re-running them.** Configuration C's `2/0`, `3/0` and `_scan_unsafe_sites` → 0
   are quoted from `TASK_152` and cited as such in `spec.md` and `NOTES.md`;
   everything else I published, I ran.
8. ⚠ **Five wall-clock cells now carry a `spread > 10%` warning** that the
   previous record did not. Nothing rests on the `ns` column
   (`NOTES.md` 8), but a reader diffing the record will see it.

---

## 9. Evidence index

`.temp/t153/NOTES.md` is the manifest and says how to rebuild every artefact.
`PREDICTION.md` · `measure.log` + `measure_diff.txt` · `gate1.log` (`FAIL`,
tables only) · `report.log` · `gate2.log` + `gate2_verdict.txt` ·
`bands_and_deltas.txt` · `mechanism_t153.txt` · `failed_stores_t153.py/.log` ·
`asm_O0_{gcc,clang}.diff` · `confusion_pairs.py/.log` ·
`miri/{uninit_probe.rs,uninit_probe.log,exhaust_probe.log}` ·
`verus/{p_chunks.rs,p_reslice2.rs}` + `verus_m1_probes.log` ·
`x1_probe.py/.log` · `x1_pin_probe.py/.log` ·
`rig/{measure_rig.py,pdir/*.rs,rig_t153.log,rig_vs_record.txt}` ·
`contract_diff_{before,after}.log` · `ctl_*.log` (five controls) ·
`check_stale.log` · `composition.log` · `temp_citations.log` · `licence.log` ·
`synthesize.log` · `tree_sweep.txt` · `{measure_record,gate_record}_BEFORE.json`
+ `table_BEFORE.md`.
**Deleted as re-derivable** (`CLAUDE.md` constraint 1, 37 M → 692 K): `rig/out/`
binaries and callgrind out-files, the `X1` mutant mirror, the reduced-`n_iters`
`.bin` copies — each with its generator kept and named in the manifest.

---

**PROTOCOL rule 2 running count: launched from 842
(`.tasks/TASK_152_REPORT.md`'s closing paragraph), carried to 882** — 40 distinct
measurements here, among them a four-arm `Ir` rig whose two controls reproduce
the committed record on all eight cells, an independent failed-store simulator
that reproduces both published checksums, a two-compiler `-O0` disassembly diff
that names the five-instruction mechanism, three fresh Verus probes, `X1`
re-derived twice plus the real `proof-pin` predicate executed on the mutant, a
Miri run with its own positive control that found a **reachable** counter-example
to a hashed sentence, an exhaustive `(tag, live member)` enumeration over all 24
committed inputs, one re-measure whose 110 moved leaves were predicted exactly,
two gate runs read out of the record, five control re-runs, and the five adjacent
tree checks. ⚠ Reconciliation across any concurrent branch is the manager's job,
not mine. **A rigour signal, not a ledger.**
