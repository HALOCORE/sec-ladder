# TASK_PHP_053 REPORT — **THE `envp` SWEEP CLOSES ITEM 112's OPEN LINK, AND IT CLOSES IT THE OTHER WAY: `argv` AND `envp` ARE NOT THE SAME KNOB**

**Role:** research **reviewer**, one agent. **Scope:** `F110` (§1) · `F112` (§2) ·
`F111` (§3) · `F96` (§4). **All four reached.**

---

## §0 BRACKETS — first

Taken before anything else, both quoted verbatim from the last line of each run:

```
python3 harness/measure.py --check-stale              ->  66 record(s) examined, 0 STALE
python3 harness-php/gate.py --tool measure --check-stale -> 22 record(s) examined, 0 STALE
```

✅ `66/0` and `22/0`, exactly as the task states. **Nothing was measured, gated or
re-gated by this round.** Both re-read at §12.

---

## §1 ⛔⛔⛔ THE PRIORITY — **§B5's VERDICTS SURVIVE; §B5's STATED GROUND IS REFUTED**

### 1.0 THE ONE-LINE ANSWER

> **Does `ph64`'s `0.00`-`argv` cell step under `envp`? ⛔ NO.** `ph64`'s **eight**
> cells are `0.00` over a full 32-residue `envp` sweep **and** `0.00` over a full
> 32-residue `argv[0]` sweep. **Item 112's verdict is not merely un-refuted; it is
> now confirmed on three independent axes.**
>
> ⛔⛔ **BUT `argv` AND `envp` ARE MEASURABLY *NOT* THE SAME KNOB, AND THE LAYER
> SAYS THEY ARE.** `ph07`'s `verus` cell steps **`34.49 Ir/call`** under `argv[1]`,
> **`20.08`** under `argv[0]`, and **`0.00`** under `envp` — one binary, one input,
> one box, one session, one code path. **So *"the measured step"* of a cell is not
> a property of the cell. It is a property of the (cell, axis) pair.**

### 1.1 THE INSTRUMENT, AND WHY IT IS NOT A SECOND IMPLEMENTATION

`.tasks-php/php53_envp_sweep.py` (new, in `.tasks-php/`, no digest, §H negatives
inside it) **imports `.tasks-php/php50_align_sweep.py` and does not modify it**.
`_probe`, `_total`, `dcalls_of`, `build_dir`, `sweep_row`, `step_of`,
`sweep_completeness`, `verdicts` and `problems_of` are `_050`'s, verbatim. Only
the knob changes:

| axis | what grows | what is held fixed |
|---|---|---|
| `argv1` | the probe **filename** — `_050`'s own sweep, reached through the imported module | environment, `argv[0]` |
| `envp` | one variable `PH53PAD`, value `"x"*pad`, **`nvars` constant** | `argv[0]`, `argv[1]` |
| `argv0` | the **symlink name** the binary is invoked through (`argv[0]` + `AT_EXECFN`) | environment, `argv[1]` |

⭐ **A disagreement between axes therefore cannot be an artefact of two
implementations of the same measurement.**

`nvars` is held constant deliberately: `harness/check.py::_env_block` records that
a sweep in the **variable count** has period **4**, because a variable costs an
8-byte envp pointer slot as well as its text, and mixing the axes would alias a
32-byte period against an 8-byte one. Measured in a real child (never from
`os.environ` — that is `_env_block` note 1 and control entry 7 of
`.memory/03-measurement.md`), `envp_stack_bytes` runs **3679 → 3710**, one byte
per pad, `nvars` unmoved: **32 consecutive residues, a full period.**

### 1.2 ⭐ THE POSITIVE CONTROL — **`envp` REPRODUCES `argv`'s CONSTANTS EXACTLY ON `ph55`**

`ph55-opdata-stride` / `small.bin` / `O3 isolated`, slope in `Ir/call`
(`.temp/php53/envp_ph55.json`, log `.temp/php53/ph55.log`; `argv` series from
`_050`'s `.temp/php50/sw_ph55.json`):

| cell | axis | low state | high state | **step** | window | flip edges |
|---|---|---:|---:|---:|---|---|
| `c-clang` | `argv[1]` | 1742.79 | 1749.79 | **7.00** | 16 wide | low over pads **1..16** |
| `c-clang` | **`envp`** | 1742.79 | 1749.79 | **7.00** | 16 wide | low over pads **7..22** |
| `c-clang-h` | `argv[1]` | 1742.79 | 1749.79 | **7.00** | 16 wide | low over pads **29..12** |
| `c-clang-h` | **`envp`** | 1742.79 | 1749.79 | **7.00** | 16 wide | low over pads **3..18** |

⭐⭐ **THE PHASE SHIFT BETWEEN AXES IS `+6` FOR *BOTH* CELLS** (1→7 and 29→3, both
mod 32). A common baseline offset shifts every cell's phase by the same amount,
and a common offset is exactly what adding `PH53PAD` to the environment is. **On
`ph55` the two axes are one lever, and that is measured rather than assumed.**

The pair verdict is identical on both axes: `c-clang → c-clang-h`, median `0.00`,
range `14.00`, **NOT RESOLVABLE / SIGN-UNSTABLE**.

⭐⭐ **`ph45-htmlent-cache-int` / `large.bin` IS A SECOND POSITIVE CONTROL, AND IT
IS NOT MERELY "CONSISTENT" — THE TWO AXES ARE INDISTINGUISHABLE ON IT.**
32 `envp` residues, four Rust cells, `O3 isolated`
(`.temp/php53/envp_ph45.json`) against `_050`'s 32-residue `argv` sweep of the
same row (`.temp/php50/sw_ph45.json`):

| | `argv[1]` (`_050`) | **`envp`** (here) |
|---|---|---|
| step per cell | `safe_naive` `safe_tuned` `unsafe` `verus` all **`7.00`** | **identical** |
| `safe_naive → safe_tuned` | median `−93062.50`, range `0.00`, RESOLVABLE / SIGN-STABLE | **identical** |
| `safe_tuned → unsafe` | median `+13130.86`, range **`14.00`**, RESOLVABLE / SIGN-STABLE | **identical** |
| `unsafe → verus` | median `+794.86`, range **`14.00`**, RESOLVABLE / SIGN-STABLE | **identical** |

▶ **Every median, every range and every verdict string agrees to the digit**,
including `_050`'s own headline for this row — *"`7.00` on four **Rust** cells,
**UNEQUAL PHASES**, so two of its differences carry a `14.00` range"*: **exactly
two do, and they are the same two.** The windows are 16 wide and the period is 32
on this axis as well (`unsafe` `[5,20]`, `verus` `[7,22]`).

⭐ **So on `ph55` and on `ph45` the two axes are the same lever, measured rather
than argued. The refutation in §1.4 rests on ONE row against these two — and
that is stated as a scope limit in §7.**

### 1.3 ⛔⛔⛔ THE DECISIVE TEST — **`ph64` DOES NOT STEP UNDER `envp`**

`ph64-callback-frees-cursor` / `small.bin` / `O3 isolated`, 32 `envp` residues,
all 8 cells (`.temp/php53/envp_ph64_small.json`, log `.temp/php53/ph64_small.log`):

```
ENVP STEP PER CELL (Ir/call): c-gcc=0.0 c-gcc-h=0.0 c-clang=0.0 c-clang-h=0.0
                              safe_naive=0.0 safe_tuned=0.0 unsafe=0.0 verus=0.0
```

Every cell is **constant to the digit** across pads 0..31 (e.g. `c-gcc` is
`42585.22` at pad 0, pad 16 and pad 31). And the pipeline reproduces the committed
family-B difference exactly: `unsafe → verus` median **`+193.36`**, range `0.00` —
the same `+193.36` `.memory-php/03-numbers.md` quotes for that pair on `small`.

⭐ **A third axis says the same thing.** `ph64`, same row/input/opt, 32 `argv[0]`
residues (`.temp/php53/argv0_ph64_small.json`):
`ARGV0 STEP PER CELL: all eight = 0.0`.

▶ **`ph64` IS CLEAN ON `argv[1]` (`_050`), ON `envp` (here) AND ON `argv[0]`
(here). ITEM 112's VERDICT IS ESTABLISHED, AND MORE STRONGLY THAN IT WAS.**

`ph55`'s four **Rust** cells are the second `0.00`-`argv` group and behave the
same way **on both further axes**: step `0.00` on all four under `envp`
(`.temp/php53/envp_ph55_rust.json`) **and** under `argv[0]`
(`.temp/php53/argv0_ph55_rust.json`). Its `unsafe → verus` family-B pair reads
**`+1.14 Ir/call`, range `0.00`, RESOLVABLE / SIGN-STABLE** on **both** — the
same median on each axis.

▶ **Tally: 12 cells with a `0.00` `argv[1]` step, swept on `envp` (12 of 12
clean) and on `argv[0]` (12 of 12 clean). 24 cell-sweeps, no counterexample.**

⭐ **`knob_verdict` — the file's own pure verdict arm — returns `SAME-KNOB` for
(`ph55 c-clang` control, `ph64` subject) and for (`ph55 c-clang` control, `ph55`
Rust subject). Twelve cells with a `0.00` `argv` step were swept on `envp`; NONE
moved. The §B5 failure mode was looked for and NOT FOUND.**

### 1.4 ⛔⛔ AND YET — **`ph07` BREAKS THE "SAME KNOB" CLAIM OUTRIGHT**

`ph07-strcut-cursor` / `small.bin` / `O3 isolated`, cell `verus`:

| axis | pads swept | series | **step** |
|---|---|---|---:|
| `argv[1]` (`_050`, `.temp/php50/sw_ph07.json`) | 32 | `2402.62` low, `2437.11` over pads **11..26** | **34.49** |
| `argv[1]` **re-run with `PH53PAD` present** (`.temp/php53/argv_ctrl_ph07.json`) | 32 | same shape | **34.49** |
| **`argv[0]`** (`.temp/php53/argv0.json`) | 32 | `2402.62` low, `2422.70` over pads **2..17** | **20.08** |
| **`envp`** (`.temp/php53/envp_ph07.json`) | 32 | `2402.62` flat | **0.00** |
| **`envp`, extended** (`.temp/php53/envp_ph07_p96.json`) | **96 consecutive** | `2402.62` flat | **0.00** |

Four things this rules out, each by a measurement rather than an argument:

1. ⛔ **It is not a dead instrument.** `ph55`'s clang cells stepped `7.00` under
   `envp` in the same session, same code, same box.
2. ⛔ **It is not the extra variable.** Re-running the **`argv[1]`** sweep *with
   `PH53PAD` set to 17 bytes* still gives **`34.49`** (`.temp/php53/argv_ctrl.py`,
   written for exactly this confound).
3. ⛔ **It is not a period longer than 32.** The cell is flat over **96
   consecutive** values of `envp_stack_bytes`. A bistable lever of period ≤ 96
   with a window narrower than its period must show an edge in 96 consecutive
   samples.
4. ⛔ **It is not "`argv[1]`'s length is special because the program reads it".**
   The cell **does** move under `argv[0]` — a string the driver never looks at —
   with the same bistable period-32 / window-16 shape. So the lever really is the
   **initial stack offset**… and `envp` bytes, which move that same offset by one
   per step for `ph55`, move it not at all for `ph07`.

⚠⚠ **I CANNOT EXPLAIN (4) AND I AM NOT GOING TO PRETEND TO.** The *low* state is
`2402.62` on all three axes and the *high* state differs per axis (`+34.49`,
`+20.08`, none), which suggests more than one binary lever with axis-dependent
excitation. **That is a hypothesis, not a result. The measurement is the result.**

A first attempt to separate these padded **`argv[2]`**; the driver **refuses a
second argument** (`exited 2`, usage line), so `.temp/php53/argv2_probe.py`
printed a flat line of zeros **and its own guard fired**: *"NO MEASUREMENT AT ALL
— the driver refused a second argument, so this probe DECIDES NOTHING and must
not be read as a flat line."* ⭐ That probe is kept because the refusal is the
evidence that the `argv[0]` route was necessary.

### 1.5 ⛔⛔ THE RULING ON §B5

`PROTOCOL_PHP.md` §B5 and `.memory-php/03-numbers.md` say a family-B difference is
publishable **iff** the two cells have a measured step of `0.00 Ir/call` over a
full 32-residue **`argv`** pad sweep. The layer entry defends that with:

> *"The evidence they are the same knob is strong but **indirect** — both shift
> the same stack block, the step size and the 32/16 period match…"*

**VERDICT: ⚠ UPHELD-NARROWED, with one clause REFUTED.**

| | |
|---|---|
| ✅ **the rule's verdicts** | **not refuted.** 12 `0.00`-`argv` cells swept on `envp`; none moved. `ph64`'s clearance is **confirmed on two further axes.** |
| ✅ **the magnitude-floor refutation** | untouched and still right — `ph07` now makes it *stronger*, because the `34.49` outlier that broke the floor is **axis-specific** as well as non-constant. |
| ⛔ **"they are the same knob"** | **REFUTED as a general claim.** ✅ **Exactly** true on `ph55` (both cells, same `7.00`, constant `+6` phase) and on `ph45` (**every median, range and verdict identical**); ⛔ **false on `ph07`**, where one axis reads `34.49` and another reads `0.00`. ⚠ **2 rows agree, 1 disagrees — and one counterexample is enough to break an "iff", which is what §B5 is.** |
| ⛔ **"the measured step" as a property of a CELL** | **REFUTED.** It is a property of the **(cell, axis)** pair: `ph07/verus` = `{argv1: 34.49, argv0: 20.08, envp: 0.00}`. |
| ⚠ **sufficiency** | **STILL OPEN, and now for a REASON rather than for want of a measurement.** Since the axes demonstrably differ, an `argv[1]` sweep reading `0.00` is a **necessary** condition, corroborated on 12 cells and 2 further axes, and **not a proved sufficient one.** |

▶ **§B5 does not need a second sweep axis to be SOUND on anything it has judged.
It needs its GROUND corrected**, and the corrected ground is the same shape
`harness/check.py::_env_block` already uses for `envp_stack_bytes`: *three equal
fields mean "this record cannot tell the two draws apart"; they do not prove the
two draws are the same.* ⭐ **The project has written this exact caution once
already, about this exact quantity, and §B5 did not inherit it.**

⭐ **AND ONE CORPUS FIGURE IN THE LAYER NOW NEEDS AN AXIS LABEL.**
`.memory-php/03-numbers.md` says *"measured corpus-wide it takes FOUR distinct
values — `0.00`, `0.02`, `7.00` and `34.49`"*. **`34.49` is an `argv[1]`-axis
value; the same cell is `20.08` on `argv[0]` and `0.00` on `envp`.** The sentence
is true only if it says which axis.

### 1.6 `_050` §10's SEVEN UNCERTAINTIES, TRIAGED

| # | uncertainty | cheap? | load-bearing? | **state after this round** |
|---|---|---|---|---|
| **1** | the sweep perturbs `argv`, the gate's bimodality is across `envp` | ✅ **was cheap** (≈1 h, no build) | ⛔⛔ **yes — a rule in the layer rested on it** | ⛔ **CLOSED, and it went the other way.** §1.4. **Route: correct the layer entry.** |
| **2** | `ph53`'s A1 `unsafe→verus` is exactly `−14.000` and `14 = 2×7`; sweep measures the whole-program slope, not `kernel_exclusive_ir` | ⚠ medium — needs a `kernel_exclusive_ir` sweep, which no tool here does | ⭐ **yes — F96's headline `−1.253 %` rests on it** | ⛔ **STILL OPEN. I did not test it.** ⓘ `_050`'s own counter-evidence (PAT: `0 of 288`) stands, and my §1.4 result makes an alignment explanation *less* likely for an A1 figure, not more. **Route: a dedicated task, or accept the PAT census.** |
| **3** | only `-O3 isolated` swept; `whole` and `O0` unswept | ✅ cheap (same tool, `OPT`/`MODE` are two constants) | ⚠ **low** — `O0` may not be quoted as a performance result at all, and no row publishes a `whole` family-B figure | ⭐ **NEITHER. Deprioritise and say so in the layer's scope line, which already does.** |
| **4** | `STABLE_RATIO = 4.0` is inherited, not derived | ✅ trivial | ⚠ **low** — no shipped verdict in the corpus sits near the boundary (the one NOT-RESOLVABLE pair is at `1.25`, the rest are `≫ 4`) | **NEITHER. Leave as a declared convention.** |
| **5** | the UB reproduction is `n = 2`, one toolchain, one box | ⛔ not cheap | ⚠ medium — bounds what may be said, and `_050` already said it | **Already handled by scoping. No action.** |
| **6** | F109's *"Verus refuses fn pointer types"* rests on a committed artefact, not a Verus run | ✅ **cheap — I made 12 `verus_run.py` invocations this round for §2** | ⚠ medium | ⛔ **NOT TESTED by me either** (different file). **Route: one `verus_run.py` invocation; genuinely a paragraph, not a task.** |
| **7** | §6.2's `8 of 9` counter-instance count is self-scored | ✅ trivial | ⛔ **no — `_050` already withdrew it to "illustrative"** | **NEITHER. Closed by its own author.** |

⭐ **Only #1 and #2 are load-bearing. #1 is now closed. #2 is the one thing the
manager should route.**

---

## §2 **F112** — ONE CLAIM UPHELD-AND-NARROWED, ONE **REFUTED**, ONE CONTROL **BROKEN**

### 2.1 ⭐⭐ *"`R4 → R5` COSTS EXACTLY NOTHING"* — ✅ **TRUE, AND IT IS THE IDENTITY PIN RESTATED**

**Re-derived, and naming every field's file.** `results-php/ph56-fetchmode-arith.json`,
cell `unsafe`/`verus`, `opt O3`, `mode isolated`, `ir[<input>].kernel_exclusive_ir`,
`n_calls = 20000` (from the same record's `inputs` block):

| input | `unsafe` A1 | `verus` A1 | delta |
|---|---:|---:|---:|
| `small.bin` | `67 925 256` | `67 925 256` | **`0` Ir, `0.000000 %`** |
| `large.bin` | `198 372 201` | `198 372 201` | **`0` Ir, `0.000000 %`** |

Per call that is `3396.263` and `9918.610` for **both** rungs — the two figures
`spec.md` quotes, to the digit. ✅ **The number is exactly right.**

⭐⭐ **WHAT IS ZERO, AND THE NARROWING: THE `0.000` IS *ENTAILED* BY THE `norel`
PIN THE SAME RECORD CARRIES — IT IS NOT A SECOND, AGREEING FACT.**
From the same record's `static` block, `O3 isolated`:

```
unsafe  n_fn 632  md5_fn 0fbd6019  md5_fn_norel 4f508d25  md5_norm 70be6b27
verus   n_fn 632  md5_fn dfd7ff81  md5_fn_norel 4f508d25  md5_norm 70be6b27
```

`md5_fn_norel` **identical** ⇒ the two `kernel` symbols are the **same
instruction sequence**, differing only in relocation operands. Executing the same
instruction sequence on the same input **must** give the same instruction count,
and `kernel_exclusive_ir` excludes callees. ▶ **So `A1 = 0.000` is a
*consequence* of `identity: norel`, not independent evidence for it.** The row
presents them as two things (*"`identity` pins `norel`, **and** family B reads
`0.00`"*). **They are one thing, counted twice.**

⛔ **And `identity norel` is NOT byte-identity, exactly as the task warns.** The
gate record `results-php/gate/ph56-fetchmode-arith.json`, field `identity`, says
`md5_raw_equal: false` at **both** `O0` and `O3`. The row declares this correctly
in `spec.md` (*"the pin is `norel` and not `exact` because the raw bytes really do
differ… different drivers… different addresses"*). **No misstatement found.**

▶ **VERDICT on the `0.000`: ✅ UPHELD, ⚠ NARROWED — the figure is right and the
row's own framing over-counts its evidence by one.**

### 2.2 ⭐⭐ THE CAUSAL HALF — **THE TASK'S SUGGESTED ATTACK MISFIRES, AND I SAY SO**

The task asks whether `ph55`'s `+0.071 %` *"even clears `ph55`'s own alignment
step (`7.00 Ir/call` on its clang cells — §B5!)"*. **It does, and the question
misfires for two independent reasons. I report this as a non-refutation.**

1. ⛔ **`+0.071 %` IS AN `A1` FIGURE, AND §B5 GOVERNS FAMILY B ONLY.**
   Re-derived from `results-php/ph55-opdata-stride.json`, `kernel_exclusive_ir`,
   `O3 isolated`: `small.bin` `31 534 053 → 31 556 597` = **`+22 544` Ir =
   `+0.071491 %`**; `large.bin` `94 674 507 → 94 764 968` = **`+0.095549 %`**.
   `kernel_exclusive_ir` is the statistic `harness/check.py` calls *structurally
   immune* (`0 of 288` triples moved). §B5 does not reach it.
2. ⛔ **EVEN IN FAMILY B THE PAIR IS CLEAN, ON *BOTH* AXES.** `ph55`'s `unsafe`
   and `verus` cells have an `argv` step of `0.00` (`_050`) **and** an `envp` step
   of `0.00` (this round, `.temp/php53/envp_ph55_rust.json`). The family-B
   difference reads **`+1.14 Ir/call`, range `0.00`, RESOLVABLE / SIGN-STABLE.**
3. ⭐ **AND THE TWO FAMILIES AGREE.** A1 gives `22 544 / 20 000 = +1.127 Ir/call`;
   family B gives `+1.14`. **Agreement to `0.013 Ir/call` across two statistics
   and two sweep axes.** The number is as solid as anything in this corpus.

**So `+0.071 %` is resolvable and the comparison against `ph56`'s `0.000` is
between two real numbers.** ⭐ *That is a result, and I did not manufacture a
refutation out of it.*

⚠⚠ **THE COUNTERFACTUAL IS STILL A COUNTERFACTUAL, AND HERE IS WHAT I *CAN*
SETTLE.** The claim is that `ph55` paid `+0.071 %` **because** it shipped two
modulus spellings. Neither row measured a one-spelling `ph55`.

* ✅ **The divergence exists and is where the row says.** `ph55/unsafe.rs:397`
  writes `((vget(val, b) as usize) % NVAR)`; `ph55/verus.rs:825` writes
  `let x: usize = (vget(val, b) % (NVAR as u64)) as usize;`. **Cast-first against
  modulus-first, one site.**
* ⚠ **It is ONE site, and `verus.rs:825-826` also splits one expression into two
  typed `let` bindings.** So even at that site the divergence is *spelling plus
  structure*, not spelling alone.
* ⚠ **`ph55`'s R5 is the SHORTER file and the DEARER one.** From
  `results-php/ph55-opdata-stride.json`, `O3 isolated`: `unsafe n_fn 876`,
  `verus n_fn 872` — **four FEWER instructions, `+1.127 Ir/call` MORE work.**
  ⛔ **So the cost is an instruction-SELECTION effect, and a static count cannot
  attribute it to one source line.**
* ⛔ **VERDICT: the "bought it" story is UNPROVEN, and it is unproven in the
  direction F83 names** — a difference attributed to one named cause, where the
  counterfactual was never run. **It is a plausible reading of a real
  divergence, and it is not a measurement.** ⭐ The cheap test exists and nobody
  has run it: respell `ph55/verus.rs:825` (or `unsafe.rs:397`) to match, rebuild
  that one cell, re-read `kernel_exclusive_ir`. **That is one cell, not a row.**

### 2.3 ✅ *"NINE EXPRESSIONS, THREE FILES"* — **NINE IS NINE**

`ph56`'s normalised spelling is modulus-before-cast on a `u64`. Counted by hand
over the four Rust rungs:

| file | sites |
|---|---|
| `safe_naive.rs` | `:245`, `:443`, `:450` |
| `safe_tuned.rs` | `:265`, `:467`, `:474` |
| `unsafe.rs` | `:366`, `:577`, `:585` |
| `verus.rs` (**exec** side) | `:1139`, `:1590`, `:1598` — the same three |
| `verus.rs` (**ghost** side, `as int` not `as usize`) | `:467`, `:543`, `:546` — not exec, not counted |

**3 × 3 = 9 expressions changed, across the three non-R5 files**, with `verus.rs`
carrying the same three already. ✅ **The claim is exact, and *"three files"* is
the three rungs that were changed.**

⭐ **The residual cast-first sites are not counterexamples**: `var_of(o: u16)`
and `tmp_of(o: u16)` take a **`u16`**, so `(o as usize) % NVAR` is lossless and
Verus accepts it. **Only the `u64` `.lval` sites needed normalising, and all nine
of them were.**

✅ **BEHAVIOUR-PRESERVING, CONFIRMED FROM THE RECORD.** In
`results-php/ph56-fetchmode-arith.json`, the `checksum` field over all **32**
(cell × opt × mode) entries yields **exactly ONE distinct value per input** on
`small.bin` and on `large.bin` — so all four Rust rungs agree with each other and
with the four C rungs, at both optimisation levels and both modes. The six
adversarial inputs are covered by the gate's own `inputs_checked` (8 inputs,
`verdict PASS`, `failures []`).

### 2.4 ⛔ THE PRECONDITION DELETION — **`req-mut` DELETES ONE AT A TIME, AND THE HOLE IS REAL**

**THE EXPLICIT ANSWER THE TASK ASKS FOR: ONE AT A TIME.**
`harness/check.py:6718-6719`, inside `check_requires_strength`:

```python
open(mpath, "w").write(
    vparse.delete_conjunct(txt, it, "requires", idx, jdx))
```

Each mutant is written **from the pristine `txt`**, deleting exactly one
`(idx, jdx)` conjunct; the loop restores `txt` at `:6738`. **There is no
combination stage anywhere in the function.**

⛔ **AND THE HOLE IS NOT HYPOTHETICAL.** For a *verified* item the `requires` are
hypotheses the body proves under. If the body needs `Q`, and `P1 ⊢ Q` and
`P2 ⊢ Q` independently, then deleting `P1` verifies, deleting `P2` verifies, and
deleting **both** does not. **Two preconditions can each be individually
removable and jointly necessary, and a one-at-a-time stage reports both as "NOT
load-bearing" and cannot see it.**

✅ **IT DOES NOT BITE `ph56`, AND THE REASON IS SPECIFIC.** `ph56` did not merely
*report* the two deletions — it **shipped** them. The shipped `verus.rs` carries
`requires[0]` alone and **verifies at `66 verified / 0 errors`** (re-run by me,
§2.5). **The shipped artefact IS the joint test.** ⭐ The hole bites a row that
reports a non-load-bearing precondition and **keeps** it, or keeps one of two —
and no built row does that today.

▶ **This is a `harness/` finding, reported and not edited, as the task directs.**
The cheap repair is a final "delete all conjuncts this stage called
not-load-bearing, together" arm.

### 2.5 ⛔⛔⛔ THE `rlimit` CLAIM — **THE NUMBER IS WRONG, THE `n = 2` COINCIDENCE IS REFUTED, AND THE CONTROL CANNOT RUN**

**(a) THE CONTROL ABORTS ON ITS OWN SHIPPED FILE. Reproduced live:**

```
$ sh patterns-php/ph56-fetchmode-arith/controls/rlimit_bisect.sh
rlimit_bisect: insertion matched 2x, want 1 -- verus.rs has been respelled and this script is measuring the wrong file
EXIT=2
```

**Why.** The script inserts one `#[verifier::rlimit(R)]` and then guards with
`n=$(grep -c 'verifier::rlimit' "$TMP"); [ "$n" != "1" ] && exit 2`. But
`patterns-php/ph56-fetchmode-arith/verus.rs:1193` **is a comment** reading
*"⭐⭐⭐ **NO `#[verifier::rlimit]`, AND THAT IS A MEASUREMENT.**"* — so the count
is **2** and the guard fires before Verus runs once. ⛔ **`ph55`'s file has TWO
such comments (`:838`, `:849`), so its copy of the script would count 3.**

⭐⭐ **THE IRONY IS THE PROJECT'S OWN LESSON.** `harness/check.py::spelling_matches`
blanks comments before matching *precisely because* **a comment is not code**
(`.tasks-php/PROTOCOL_PHP.md`'s NAMED-SPELLING STANDARD, part (b), forced by two
shipped `kernel_hardened.c` files). **This guard does not, and its own file's
comment disarms it.**

**(b) I RE-DERIVED THE TABLE MYSELF, AND IT DOES NOT REPRODUCE.**
Same box, same `./verus_run.py`, same pinned Verus, same `sed` insertion the
script uses (anchor `#[cfg_attr(slb_isolated, inline(never))]`, verified to occur
**exactly once** in each file). Mutants in `.temp/php53/rl/`, log
`.temp/php53/rl.log` / `rl2.log` / `rl3.log`:

| file | rlimit | **plain** | **twin (`--cfg slb_twin`)** | shipped table says |
|---|---|---|---|---|
| `ph56` | *(no attribute — the CONTROL)* | ✅ **66 verified, 0 errors** | *(gate record: 76/0)* | 66/0 · 76/0 ✅ |
| `ph56` | 1 | 65 verified, **1 error** | — | 65/1 · 75/1 ✅ |
| `ph56` | **2** | ⛔ **65 verified, 1 error** | — | ⛔ **66/0 · 76/0** |
| `ph56` | **2 (repeat)** | ⛔ **65 verified, 1 error** | — | ⛔ same |
| `ph56` | **3** | ✅ **66 verified, 0 errors** | ✅ **76 verified, 0 errors** | 66/0 · 76/0 ✅ |
| `ph56` | 5 / 10 | ✅ 66/0 | — | ✅ |
| `ph55` | *(no attribute)* | ✅ 53 verified, 0 errors | — | — |
| `ph55` | **2** | ✅ **53 verified, 0 errors** | ✅ **61 verified, 0 errors** | ✅ floor ≤ 2 |
| `ph55` | 3 | ✅ 53/0 | — | ✅ |

The failing obligation at `rlimit 1` **and** at `rlimit 2` is the same:
`error: while loop: Resource limit (rlimit) exceeded`.

▶ ⛔⛔ **`ph56`'s FLOOR IS `3`, NOT `2`.** The control (shipped file, no attribute)
gives exactly the `66/0` the gate record carries, so this is **not** a broken
toolchain — it is the same file, verifying, beside a mutant that does not.
Measured twice.

⭐ **THE CONTROL IS TIGHT, AND HERE IS WHY IT COUNTS.**
`results-php/gate/ph56-fetchmode-arith.json`, field `verus["verus.rs"]`, reads
`{"verified": 66, "errors": 0, "pinned": 66}` — **the exact pair my pristine run
produced**; and my `rl3 --cfg slb_twin` produced **76/0**, the twin figure the
same record's `verified_twins` block backs. `harness/check.py::_verus` drives
`verus_run.py`, which is what `rlimit_bisect.sh` and I both called. ▶ **Same
entry point, same file, same numbers — so the `rlimit 2` failure is a property of
the mutant, not of my setup.**

▶ ⛔⛔⛔ **AND THE HEADLINE GOES WITH IT: *"the floor bisects to 2 — the same as
`ph55`, so `n = 2` about the proof SHAPE"* IS REFUTED.** `ph55` verifies at
`rlimit 2` on **both** columns; `ph56` does not on either. **The two rows do not
share a floor, and there is no `n = 2`.**

✅ **WHAT SURVIVES, AND IT IS THE PART WORTH KEEPING.** *"An `rlimit` error is a
SYMPTOM, not a size"* — the first draft's overrun was a wrong loop invariant
(`invariant` where `invariant_except_break` was needed), and raising the limit
would have shipped it. **That claim is about a debugging episode, is internally
coherent, is unaffected by the floor being 3 rather than 2, and I found nothing
against it.** ⚠ It is also **not independently checkable from anything in the
tree** — no artefact records the first draft — so it is upheld *as a lesson*, not
as a measurement.

⚠ **BAR (i) FAILS FOR THIS CLAIM IN A WAY WORTH RECORDING SEPARATELY:** the
rlimit table exists **only as a comment block inside `rlimit_bisect.sh`**. Every
other control on this row emits a machine-readable artefact (`negatives.json`,
`statistic.json`, `spellings.json`, `census.json`, `r1h_backport.json`);
`rlimit_bisect.sh` emits stdout, and its result lives in its own docstring.
**A number in a hashed file that the script in the same file cannot regenerate is
the `F6a` shape, one directory over.**

---

## §3 **F111** — THE CENSUS **RE-RUNS AND HOLDS** OFFLINE; THE UPSTREAM-HISTORY HALF IS **UNTESTED**

I ran the row's own control: `python3 patterns-php/ph56-fetchmode-arith/controls/census.py`
(log `.temp/php53/census.log`). It found the pinned tarball
(sha256 `5783e0c0…`) and a pristine 5.0.0 CLI, and reported **`problems: none`**.

**A — the pinned tarball's switch** (offline, decisive):

```
BP_VAR_R  guard=True   BP_VAR_W  guard=False  BP_VAR_RW guard=False
BP_VAR_IS guard=False  BP_VAR_FUNC_ARG guard=False  BP_VAR_UNSET guard=True
```

✅ **Four arms lack the guard; two have it.** `BP_VAR_FUNC_ARG` is unguarded at
5.0.0. **UPHELD.**

**C — a pristine PHP 5.0.0 CLI** (the declaration-order claim, *measured*):

```
BP_VAR_FUNC_ARG                     rc=0     4          <- silent mutation, array grew
BP_VAR_R (via a DECLARED callee)    rc=255   Fatal error: Cannot use [] for reading
BP_VAR_IS                           rc=-11              <- SIGSEGV
BP_VAR_RW / BP_VAR_W                rc=0     4
BP_VAR_UNSET                        rc=255   Fatal error: Cannot use [] for unsetting
```

⭐⭐ **THE DECLARATION-ORDER CLAIM IS UPHELD BY DIRECT MEASUREMENT, NOT BY
READING**: the same `f($a[])` is a **fatal error** when the callee is already
declared and a **silent array mutation** when it is not. **UPHELD.**

**B — the row's own ladder** confirms `BP_VAR_IS` is the only arm R1h moves
(`moves=True null_operand=True`), and the chained input moves without a null
operand (`moves=True null_operand=False`) — F111's *second harm*. **UPHELD.**

### 3.1 ✅ `0x14 = offsetof(zval, type)` — **CONFIRMED BY AN INDEPENDENT PROBE**

`.temp/php53/zval_offset.c`, struct transcribed from the pinned tarball's
`php-5.0.0/Zend/zend.h:255-293` (`HashTable *` and `zend_object_handlers *`
declared `void *`, sound for a layout question):

```
sizeof(zvalue_value)   = 16
offsetof(zval, refcount) = 16
offsetof(zval, type)     = 20  (0x14)      CLAIM offsetof(zval,type)==0x14 : HOLDS
```

⭐ The probe also prints its own scope: **on a 32-bit ABI the union is 8 bytes and
the answer would be `0xc`**, so this is evidence for the 64-bit ABI and says so.
✅ **UPHELD.**

### 3.2 ⛔ WHAT I DID **NOT** TEST — AND I DO NOT REPORT IT AS CONFIRMED

| claim | state |
|---|---|
| *"upstream **never** guarded `RW`/`FUNC_ARG` at compile time in **any** PHP 5"* | ⛔ **UNTESTED.** The row corroborates it by counting *"Cannot use [] for reading"* in 5.0.0 / 5.0.4 / 5.0.5 and over 18 release tags. **Only the 5.0.0 tarball is on this box**; I found no 5.0.4/5.0.5 or tag matrix locally, and `census.py` parses **5.0.0 only**. |
| *"the asymmetry survives into `master`"* (`zend_compile.c:3154-3161`) | ⛔ **UNTESTED — needs network.** |
| *"closed 11½ months later, at runtime, different file, different author, bug #34064, `9183f91b506a`, 2005-08-10"* | ⛔ **UNTESTED — needs network.** |
| *"that patch WIDENED the opcode specs, so RW-append is a FEATURE"* | ⛔ **UNTESTED — needs network.** The **conclusion** is independently supported by part C above (`BP_VAR_RW` → `rc=0`, array grows, on a pristine 5.0.0), but that is 5.0.0 behaviour, **not** evidence about the 2005 patch's intent. |

⛔ **I am recording these as `UNTESTED`, not as confirmations of absence.**

### 3.3 ⚠ ONE DURABILITY DEFECT IN THE CENSUS ITSELF

`census.py` part C located its pristine CLI at

```
/home/apt/repos_common/php-in-safe-rust/.trash/temp-20260805-0920/build-5.0.0/php-5.0.0/sapi/cli/php
```

⚠ **A `.trash/` directory in another repository.** The census's strongest arm —
the one that turns *"declaration order decides"* from a reading into a
measurement — depends on a binary sitting in someone's trash. **It will
evaporate, silently, and the control will report a weaker census with
`problems: none`.** ⓘ Reported, not edited.

---

## §4 **F96** — ⛔ **UNREVIEWED FOR THE FOURTH TIME**, BUT `ph56` SUPPLIES A SECOND METHOD `_050` SAID WAS MISSING — AND IT **REFUTES** A MECHANISM

### 4.1 THE LEDGER: `ph56` DOES NOT HELP, AND NOW THERE IS A **CRITERION** FOR WHY

F96's core is `ph53`'s build record plus the four-prediction ledger (R2 ≈ R1h, R3
cheapest, R4 elides, R5 no ghost state). **`ph56` is a `T5` row whose kernel is a
compiler mis-emit; `ph53` is a `T3` row whose kernel is an interface-table tail
read. Different family, different kernel, different tier.** ⛔ **UNREVIEWED, for
the fourth time, and I am not manufacturing a bar it can clear.**

⭐ **AND FOR F96's RESULT 3 THERE IS NOW A STATED CRITERION, WHICH IS THE USEFUL
PART.** `_050` §7.2 established that only rows with `unsafe vs verus` pinned
**`differ`** at `-O3` are evidence (the `exact`/`norel` rows' `0.000 %` is true by
construction). **`ph56` is pinned `norel`** (gate record `identity`, both opt
levels). ▶ **So `ph56` adds nothing to result 3, the denominator stays at 4
(`ph45`, `ph53`, `ph55`, `ph64`), and the next row will help only if it is pinned
`differ`.** That is a routing fact the manager can use.

### 4.2 ⭐⭐⭐ BUT `ph56` **IS** THE CROSS-LANGUAGE ROW `_050` §7.3 SAID IT LACKED — AND A AND B **DISAGREE IN SIGN**

`_050` §7.3 confirmed F96 result 2's *mechanism* on `unsafe → verus` and then
scoped itself honestly: *"F96 result 2 is about **cross-language** cells;
`unsafe → verus` is **same-language**… `n = 0` new rows for result 2 as written."*

**`ph56` is a cross-language row, and its kernel does not allocate**
(`spec.md`: `"uses_allocator": false`), so F96 result 2's stated precondition
**holds**. Computed by me from the two records — A1 from
`results-php/ph56-fetchmode-arith.json` (`kernel_exclusive_ir / 20000`), B1 from
`results-php/gate/ph56-fetchmode-arith.json` (`marginal_ir_per_call`), **`O3
isolated`**, base named per row:

| pair | input | **A1** | **B1** | |
|---|---|---:|---:|---|
| `c-gcc-h` → `safe_tuned` | `small.bin` | **`+293.93` (`+8.994 %`)** | **`−31.99`** | ⛔ **SIGN DISAGREE** |
| `c-gcc-h` → `safe_tuned` | `large.bin` | **`+1391.51` (`+14.854 %`)** | **`−74.96`** | ⛔ **SIGN DISAGREE** |
| `c-gcc-h` → `unsafe` | `small.bin` | **`+128.18` (`+3.922 %`)** | **`−197.87`** | ⛔ **SIGN DISAGREE** |
| `c-gcc-h` → `unsafe` | `large.bin` | **`+550.76` (`+5.879 %`)** | **`−917.45`** | ⛔ **SIGN DISAGREE** |
| `c-gcc-h` → `verus` | both | same as `unsafe` (`norel`) | same | ⛔ **SIGN DISAGREE ×2** |
| `c-clang-h` → `safe_tuned` | `small` / `large` | `+583.86` / `+1305.71` | `+486.00` / `+1209.31` | ✅ agree |
| `c-clang-h` → `unsafe`/`verus` | `small` / `large` | `+418.11` / `+464.96` | `+320.12` / `+366.82` | ✅ agree |

⛔⛔ **SIX OF TWELVE CROSS-LANGUAGE PAIRS DISAGREE IN SIGN, ON A ROW WHOSE KERNEL
DOES NOT ALLOCATE.** ▶ **F96 result 2's REASON — *"§B1a's O(1)-allocation
precondition HOLDS here, so there is no allocator term for B to include and A to
miss"* — IS NOT SUFFICIENT. Allocation is one source of A/B divergence; it is not
the only one.**

⭐ **AND THE SECOND SOURCE IS EXACT TO THE DIGIT.** The per-call work *outside*
the `kernel` symbol is `B1 − A1`: `c-gcc-h` `small` = `3677.75 − 3268.084 =
409.67` (**12.5 %** of B1); `unsafe` `small` = `3479.88 − 3396.263 = 83.62`
(**2.4 %**). Then

```
B1(c-gcc-h -> unsafe, small) = A1(pair) - [outside(gcc) - outside(rust)]
                             = +128.179 - (409.666 - 83.617)
                             = -197.87        <- exactly the recorded B1
```

▶ **The sign flip is `inside_share`, not the allocator**, and `ph56`'s own
`controls/statistic.py` already measures `inside_share` per cell. **This is a
second, allocation-independent mechanism for A/B divergence that F96 result 2
does not name, and `ph56` is the row that exhibits it.**

⚠ **SCOPE, STATED:** F96 result 2 as literally written is a claim about **`ph53`'s
own cells** and remains true of `ph53`. What `ph56` refutes is the **reason**
offered for it, i.e. the part that generalises and therefore the part that would
enter the layer. ⭐ **That is the same shape as `_049` and `_050`: the effect
survives and the story does not.**

---

## §5 ⛔⛔ COVERAGE TABLE

| finding | verdict | one line |
|---|---|---|
| **F110** | ⚠ **UPHELD-NARROWED** | Every sweep verdict re-derived or corroborated; `ph64` clean on **three** axes. ⛔ Its declared-open link is **closed against it**: `argv` and `envp` are **not** the same knob (`ph07`: `34.49` / `20.08` / `0.00`). The rule's verdicts stand; its **ground** must change and its `34.49` needs an axis label. |
| **F112** | ⚠ **UPHELD-NARROWED**, with **one clause REFUTED** | `0.000 Ir/call` ✅ exact, but **entailed by the `norel` pin** rather than independent of it. *"Nine expressions, three files"* ✅ exact. Behaviour-preservation ✅ confirmed. ⛔ **`rlimit` floor is `3`, not `2`, measured twice against a clean control — so the `n = 2` proof-SHAPE coincidence with `ph55` is REFUTED**, and `controls/rlimit_bisect.sh` **cannot run on its own shipped file**. The *"bought it"* causal story is **UNPROVEN** (no counterfactual), though the attack the task suggested misfires and the `+0.071 %` is solid. |
| **F111** | ⚠ **UPHELD-NARROWED** | Offline half **re-run and upheld** by the row's own control (`problems: none`): the four unguarded arms, the declaration-order asymmetry **measured on a pristine 5.0.0 CLI**, the second harm, and `0x14 = offsetof(zval, type)` by independent probe. ⛔ **The four upstream-history claims (any-PHP-5, `master`, the 2005 commit, "RW-append is a feature") are `UNTESTED` — network.** ⚠ The census's strongest arm depends on a binary in a `.trash/` directory. |
| **F96** | ⛔ **UNREVIEWED** (fourth round) | The ledger still has **no** cheap second method, and `ph56` is not one (`T5`, different kernel; and pinned `norel`, so no evidence for result 3 either). ⭐ **But `ph56` IS the cross-language row `_050` said was missing for result 2, and it REFUTES that result's stated REASON** (6 of 12 pairs disagree in sign on a non-allocating kernel). ⭐ **Four honest rounds is the finding: F96 needs a dedicated task or a permanent mark.** |

---

## §6 ⛔ WHAT MUST **COME OUT** OF `.memory-php/`, AND WHAT MUST **NOT GO IN**

### 6.1 ⛔⛔ MUST COME OUT / BE CORRECTED (this round is the first to owe a removal)

1. ⛔⛔ **`.memory-php/03-numbers.md:242-249` — the "one unproven link" paragraph.**
   It says the evidence the two axes are the same knob is *"strong but
   indirect"*. **It is now MEASURED, and it is FALSE as a general claim.**
   Replace with: *the two axes agree on `ph55` (both clang cells, same `7.00`
   step, same 32/16, constant `+6` phase) and on `ph45`, and **disagree
   completely on `ph07`'s `verus` cell** (`argv[1] 34.49` / `argv[0] 20.08` /
   `envp 0.00`, the last over **96** consecutive bytes). **The step is a property
   of the (cell, axis) pair.** The rule's `argv` test is therefore NECESSARY and
   not proved SUFFICIENT — corroborated on 12 `0.00`-`argv` cells swept on `envp`
   and 12 on `argv[0]`, none of which moved.*
   ⭐ **Apply the narrowing, do not append it** (item 73).
2. ⛔ **`.memory-php/03-numbers.md:227-230` — the four-value step list.**
   *"`0.00`, `0.02`, `7.00` and `34.49`"* must say **which axis**. `34.49` is
   `argv[1]`; the same cell is `20.08` on `argv[0]` and `0.00` on `envp`.
3. ⛔ **`PROTOCOL_PHP.md` §B5's rule sentence** carries the same `argv`-only
   phrasing and needs the same correction. ⓘ **The RULE ITSELF need not change**
   — no counterexample to its verdicts was found — **only what it claims to be
   testing.**

### 6.2 ⛔ MUST **NOT** ENTER

1. ⛔⛔ **NOT: *"`ph56`'s rlimit floor is 2, the same as `ph55`, so `n = 2` about
   the proof shape."*** **REFUTED.** `ph56` needs **3**; `ph55` verifies at **2**.
   Nothing about a shared floor may enter.
2. ⛔ **NOT: *"`R4 → R5` costs exactly nothing" as an independent measurement.***
   It may enter only as *"`ph56` pins `identity: norel` at both opt levels, and
   `kernel_exclusive_ir` is consequently equal to the digit."* **One fact, stated
   once.**
3. ⛔ **NOT: *"`ph55` paid `+0.071 %` BECAUSE it shipped two spellings."***
   The divergence is real and at one site; **the counterfactual was never run.**
   What may enter is the **advice** (*normalise the exec spelling across all four
   Rust rungs so the R2→R3 / R3→R4 gradients carry no representation change*),
   which is sound regardless of whether it explains `ph55`'s number.
4. ⛔ **NOT: any of F111's four upstream-history claims.** `UNTESTED` here.
   ⚠ Especially not *"RW-append is a FEATURE"*, which is an inference about a
   2005 author's intent.
5. ⛔ **NOT: *"`req-mut` establishes that `ph56`'s two deleted preconditions were
   not load-bearing."*** It establishes it **one at a time**; what establishes it
   **jointly** is that the shipped file verifies at `66/0` without either.
6. ⛔ **NOT: F96 result 2's reason as a rule.** Allocation is **not** the only
   source of A/B divergence — `inside_share` is another, measured on `ph56` to
   the digit. If anything enters, it is the **two**-mechanism version.
7. ⛔ **NOT: my `ph45` figures as a completed sweep** — 15 of 32 pads (§11).
8. ⛔ **NOT: any claim that `ph07`'s axis asymmetry is EXPLAINED.** I measured it
   and I could not explain it.

### 6.3 ✅ WHAT **MAY** ENTER

* ✅ **`ph64` is alignment-clean on three independent axes** (`argv[1]`, `envp`,
  `argv[0]`), 8 cells each, `small.bin`, `O3 isolated`. Item 112's verdict is
  established.
* ✅ **`ph55`'s `+0.071 %` / `+0.096 %` (A1, `O3 isolated`, base = its own
  `unsafe` cell) is resolvable** and agrees with family B (`+1.14` vs `+1.127`
  Ir/call) across two axes.
* ✅ **`harness/check.py`'s `req-mut` deletes preconditions one at a time** — a
  `harness/` limitation, reported not edited.
* ✅ **A control whose guard counts a spelling must blank comments first**
  (`rlimit_bisect.sh`, both rows). Generalises the NAMED-SPELLING STANDARD's
  part (b) from contracts to controls.
* ✅ **`inside_share` is a second, allocation-independent source of A/B sign
  divergence**, with `ph56`'s exact decomposition as the evidence.

---

## §7 ⭐ WHAT I AM UNSURE OF

0. ⚠⚠⚠ **THE "NOT THE SAME KNOB" REFUTATION RESTS ON ONE ROW.** Of the four
   cell-groups I swept on two or more axes, **three agree** — `ph55`'s clang
   cells (same `7.00`, constant `+6` phase), `ph45`'s four Rust cells (**every
   median, range and verdict identical to the digit**) and the 12 clean cells
   (`0.00` everywhere) — **and one, `ph07`'s `verus`, disagrees completely.**
   ⭐ One counterexample is enough to break an `iff`, and §B5 is an `iff`, so the
   refutation stands as stated. ⛔ **But if `ph07` turned out to be an artefact I
   failed to find, §B5's ground would be fine and this round's headline would
   collapse to "confirmed on three axes".** I attacked `ph07` four ways (§1.4)
   and it survived all four. **It is one row.**
1. ⚠⚠ **I CANNOT EXPLAIN `ph07`'s AXIS ASYMMETRY.** `argv[0]` moves it, `argv[1]`
   moves it more, `envp` does not move it at all over 96 consecutive bytes. I
   ruled out a dead instrument, the extra variable, a longer period and the
   "program handles `argv[1]`" reading. **The measurement is solid; the mechanism
   is open.** It may be a valgrind stack-synthesis detail, and I did not read
   valgrind's source.
2. ⚠⚠ **MY `envp` SWEEP ADDS A VARIABLE THAT THE GATE DOES NOT HAVE**
   (`PH53PAD`, baseline block `3679`). Every *step* I report is measured over 32
   or 96 consecutive values from that baseline, so a step is sound; **an absolute
   slope of mine is not directly comparable to a gate figure.** The `ph64`
   `unsafe → verus` median `+193.36` matching the record exactly is reassurance,
   not proof.
3. ⚠ **I swept `-O3 isolated` only, and mostly `small.bin` only.** `ph45` is
   `large.bin`. `O0`, `whole`, and the second input on most rows are **unswept**
   by me, exactly as `_050` §10.3 flagged for itself.
4. ⚠⚠ **THE `rlimit` REFUTATION IS ONE BOX, ONE DAY, ONE TOOLCHAIN.** Z3's
   `rlimit` is meant to be deterministic and my `rlimit 2` result reproduced on a
   repeat run with a clean `66/0` control beside it — **but I cannot exclude a
   Verus/Z3 detail that differed from the row author's run hours earlier**, and I
   did not check whether anything in the toolchain moved. ⭐ **If the floor really
   was 2 earlier today and is 3 now, that is a MORE alarming finding, not a less
   one, and it is the first thing to check.**
5. ⚠ **I did not re-run `req-mut` itself** (it would mean running the gate stage,
   which re-verifies). I read the code and confirmed the shipped file verifies
   without both preconditions. **The one-at-a-time answer is from the source, not
   from an execution.**
6. ⚠ **`ph56`'s nine expressions were counted by hand from a `grep`**, adjudicated
   line by line, not by a tool. I believe it is nine; I did not write a checker.
7. ⚠ **F96 §4.2's refutation rests on my reading of what F96 result 2 CLAIMS.**
   If result 2 is read as strictly row-local, `ph56` refutes nothing and merely
   adds a data point. **I read it as offering a mechanism, because the mechanism
   is what a layer entry would carry.**
8. ⚠ **`ph45`'s sweep was still running when I wrote this** (§11).

---

## §8 THE CHECKERS — all in `.tasks-php/`, no digest, free

**`.tasks-php/php53_envp_sweep.py`** — the §1 instrument. Imports
`php50_align_sweep.py` unmodified; adds the `envp` and `argv0` axes and two pure
verdict arms. **§H: 10 `knob_verdict` arms + 5 `axis_report` arms + `N7`–`N17`,
plus `php50_align_sweep`'s own 19, all re-run on EVERY invocation** — a broken
verdict arm refuses to measure rather than measuring anyway.

⚠⚠ **TWO ARMS FIRED AGAINST MY OWN FIRST DRAFT, AND THE CODE CHANGED:**

* **`N8`** — my first `knob_verdict` checked `INSTRUMENT-DEAD` **before**
  `B5-UNSOUND`, so a control that happened not to move would have **suppressed a
  live refutation of the rule**. The arm fired, the precedence was inverted, and
  the reason is now a comment at the branch.
* **`N17`** — the axis table must cover every `--axis` choice, so a run cannot
  name an axis that silently falls back to another.

**Scratch discipline** (`CLAUDE.md` Don't #1): `.temp/php53/` went **1012 K → 240 K**.
Every `.rs` mutant, the compiled `zval_offset`, and every stray `cg.*.out` were
deleted; **`.temp/php53/rl/regen.sh` was written first and verified to reproduce
them** (it asserts the `sed` ANCHOR rather than the string, which is the repair
for §2.5(a)'s defect). The four re-derivable probe blobs left under
`.temp/php50/sweep/dc/` were removed too — `php50_align_sweep.dcalls_of`
regenerates them. **All `.py`, `.c`, `.sh`, `.json` and `.log` evidence stays.**

Scratch probes (generators kept under `.temp/php53/`, artefacts deleted):
`argv_ctrl.py` (the `PH53PAD` confound — **ruled it out**), `argv2_probe.py`
(**refused to decide** when the driver rejected a second argument — the refusal is
its own §H arm working), `argv0_probe.py` (the symlink axis, later folded into the
`.tasks-php/` checker), `zval_offset.c` (§3.1, with a 32-bit-ABI scope line).

---

## §9 ⓘ WHAT I RAN THAT IS NOT MINE

`patterns-php/ph56-fetchmode-arith/controls/census.py` (read-only, `problems:
none`) · `patterns-php/ph56-fetchmode-arith/controls/rlimit_bisect.sh` (**aborted,
exit 2**) · `./verus_run.py` **12 times** over **9** copies under `.temp/php53/rl/`
(6 `ph56` variants, 3 `ph55`, two of them also under `--cfg slb_twin`, one repeat).
**No gate, no measure, no re-gate, no `git add`, no `git commit`, nothing written
under `harness*/`, `common*/`, `patterns*/`, `results*/`, `pilot/`, `.web/`,
`RECAP_PHP.md` or `.memory-php/`.**

---

## §10 ⛔ THE ONE FAMILY-B FIGURE I QUOTE, AND WHICH §B5 I APPLY

The only family-B figures in this report are **`ph55`'s `unsafe → verus`
`+1.14 Ir/call`** and **`ph64`'s `unsafe → verus` `+193.36`**, both `small.bin`,
`O3 isolated`. **I apply §B5 as written (`argv` sweep) *and* the corrected form
(both axes):** both pairs have step `0.00` on `argv[1]`, `envp` **and**
`argv[0]`, and both read RESOLVABLE with range `0.00`. ⛔ **`ph64`'s `+193.36` is
quoted ONLY as a pipeline cross-check against the committed record — never as a
performance result**, because `.memory-php/03-numbers.md` forbids publishing a
family-B `unsafe → verus` figure on an allocating row, and `ph64` is that row.
**No `O0` figure is quoted anywhere in this report.**

---

## §11 WHERE I STOPPED

⭐ **All four subjects were reached.** What is incomplete, named:

* ✅ **`ph45`'s `envp` sweep COMPLETED** after the first draft of this report, all
  32 pads, and `envp_ph45.json` is written. It turned out **stronger** than the
  draft claimed: the `envp` axis reproduces `_050`'s `argv` axis **to the digit
  on every median, every range and every verdict string** (§1.2). Nothing in this
  report now rests on a partial sweep.
* ✅ **`ph55`'s Rust cells on the `argv[0]` axis COMPLETED** after the first draft
  of this report: all four cells step `0.00` over 32 residues, `unsafe → verus`
  median `+1.14`, range `0.00`. §1.3's tally includes it.
* ⛔ **No `envp` or `argv[0]` sweep of the other six rows.** I swept to
  discriminate, not to tabulate, as the task directed.
* ⛔ **F111's four upstream-history claims** — network, `UNTESTED`.
* ⛔ **F96's four-prediction ledger** — `UNREVIEWED`, fourth round, by decision.
* ⛔ **`_050` §10.2** (`ph53`'s `−14.000` and `kernel_exclusive_ir`) — **not
  tested**, and it is the one load-bearing uncertainty still open.
* ⛔ **I did not run `ph56`'s `rlimit` bisect under every value the table lists**
  — 1, 2, 2-repeat, 3, 5, 10 plain and 3 twin; and `ph55` at pristine, 2, 3
  plain and 2 twin. **That is enough to refute a floor of 2 and not enough to
  rebuild the whole table.**

---

## §12 BRACKETS — last

```
python3 harness/measure.py --check-stale              ->  66 record(s) examined, 0 STALE
python3 harness-php/gate.py --tool measure --check-stale -> 22 record(s) examined, 0 STALE
```

✅ **`66/0` and `22/0`, unmoved.**
