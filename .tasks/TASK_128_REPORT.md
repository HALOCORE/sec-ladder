# TASK_128 — §A INVERTS THE PREMISE, AND IT INVERTS IT WITH A MEASUREMENT

**Role: research engineer. Deliverable: a measurement and a verdict on the bar's
text.** Scratch, generators and every log: `.temp/t128/` — `BUILD.sh`
regenerates every source, binary and log and deletes the binaries at the end.
Nothing outside `.temp/t128/` and this file was written. `harness/check.py`,
`harness/build.py` and `harness/measure.py` were **not run**. No `git add`, no
`git commit`.

Every committed number below is read with **`git show df14f4f:<path>`**
(`df14f4f` = the commit `TASK_128.md` landed in; `git diff --stat df14f4f HEAD --
results/` was **empty** when I started, so it is also HEAD's `results/`).
⚠ **This mattered:** `git status` right now shows `TASK_127` holding
`results/tables/p23-partition.md`, `results/p03-bounded-stack.json` and 24 other
tracked files dirty. Reading the working tree would have produced numbers nobody
could reproduce.

---

## HEADLINE

⚠⚠ **THE MANAGER'S LEAST-SURE CALL #1 IS RIGHT, AND THE ANSWER IS SHAPE 1 WITH
ONE REFINEMENT. `TASK_124`'s provenance contrast measured TWO of the project's
six published columns — ASSEMBLY and `Ir`. It did not measure timing, proof
burden, trusted base or the harm matrix, and its own report says so of the third
in as many words: "B2 — Verus. NOT SPENT, deliberately."**

⚠⚠⚠ **AND I DID NOT STOP AT THE READING. I BUILT THE SAME CONTROL AND POINTED
THE MISSING INSTRUMENT AT IT. THE COLUMN MOVES.**

Holding the kernel **byte-identical by construction** and changing only the
bound's provenance (input extent → prior-pass count):

```
kernel symbol            243 B  sha256 a379bee990da90af   BOTH ARMS  -> IDENTICAL
kernel-exclusive Ir/call        176.00 vs 176.00                     -> +0.00
Verus `verified`  (= the published `obligations` column)  3  ->  5   -> +2  (+67%)
ghost clauses (requires/ensures/invariant/decreases)      9  -> 13   -> +4  (+44%)
TCB items / lines                                       1/1 -> 1/1   -> 0
```

with the must-fire arm firing: delete the sizing pass's `ensures` and Verus
reports **`precondition not satisfied … n <= src@.len()`** at the call site,
`4 verified, 1 errors`. The obligation is load-bearing, not decoration.

> ✅ **So *"a new source of the bound is a distinction THIS LADDER CANNOT PRICE"*
> is FALSE AS WRITTEN. It cannot be priced on ASSEMBLY or `Ir`. It prices on the
> published `obligations` column, which `results/synthesis.md` §3 titles
> *"Proof burden and trusted base"* and where the built tree's own range is
> `7 … 21`. A `+2` there is the gap between `p01` and `p03`.**

⚠ **`TASK_124` did not overclaim — its §B1 heading sits under `ir_extent.log`
and its §B2 says the Verus probe was not spent. The overclaim is in `RECAP.md`,
in exactly two places, and `.memory/` is clean (rule 9 held).**

---

## §A — WHAT `TASK_124`'s CONTRAST ACTUALLY MEASURED

Read from `.tasks/TASK_124_REPORT.md` **and from `.temp/t124/A/`'s scripts and
logs**, not from the summary sentence. `A/BUILD.sh` names every instrument that
touched the provenance arms (`s_rs` = prior-pass bound, `s_ext` = input extent):

| script / log | instrument | column |
|---|---|---|
| `extent_gen.py` | generates `split_extent.rs` from `split.rs` | (the control) |
| `probe2_provenance.log` | symbol extent + md5, from `readelf -sW` | assembly |
| `provenance_asm.py` / `.log` | mnemonic diff, operands stripped | assembly |
| `provenance_bytes.py` / `.log` | byte level, filename + line held equal | assembly |
| `provenance_reloc.py` / `.log` | relocation-normalised diff | assembly |
| `mutarm.py` / `.log` | plants `0xC0 → 0xE0`; the normaliser must SEE it | (must-fire) |
| `ir_extent.py` / `.log` | `valgrind --tool=callgrind`, parses `refs:` only | instruction count |

`ir_extent.py` is fifteen lines of callgrind and one regex for `refs:`. **That is
the whole of "every published difference moves by exactly `+0.00`": it is `Ir`.**
`matrix.sh` and `miri.sh` — the behaviour and sanitiser arms — drive
`s_rs`/`s_gcc`/`s_clang`/`s_asan` and the **`+8` perturbation**, which is a
different control; neither is ever pointed at `s_ext`.

### ✅ The deliverable table: six published columns × three questions

| # | published column | where it is published | did the contrast move it? | was it measured at all? | could it have moved? |
|---|---|---|---|---|---|
| 1 | **assembly** | `results/tables/*.md` static block; gate `identity` | **no** — 0 mnemonic diffs on all six kernels, R4 byte-identical, relocation-normalised 0 | ✅ yes, four ways, with a planted-difference arm | ⚠ **no** — reproduced independently here: same kernel string ⇒ same 243 B, same sha256 |
| 2 | **instruction count** | `Ir(kernel)`, gate `marginal_ir_per_call` | **no** — every rung difference `+0.00`; only the common sizing-pass term moved (`−63.00`) and it cancels | ✅ yes | ⚠ **no** — reproduced here: `176.00` vs `176.00`, work-matched, with a must-fire arm at `322.00` |
| 3 | **timing** | `results/tables/*.md` "Wall clock (secondary)" | — | ❌ **NO** | ⚠ **not distinguishably.** The kernel bytes are identical, so any move is layout, and the settled layout floor is `±4.6%`. **I did not measure it either, deliberately — see "not done"** |
| 4 | **proof burden** | `results/synthesis.md` §3, `obligations` (tree range `7…21`); gate `verus.<f>.verified` | — | ❌ **NO — `TASK_124` §B2: "NOT SPENT, deliberately"** | ⚠⚠ **YES, AND IT DOES. MEASURED HERE: `3 → 5` obligations, `9 → 13` ghost clauses, must-fire fired** |
| 5 | **trusted base** | `results/synthesis.md` §3, `TCB items` / `TCB lines` / `axioms` | — | ❌ **NO** (no `verus.rs` arm existed) | ✅ **no — measured here: `1 item / 1 line` on both arms.** A clean negative worth having: a prior-pass bound needs **no new trusted item** |
| 6 | **harm matrix** | gate `adversarial`, `sanitizer`, `miri` | — | ❌ **NO under the PROVENANCE control** (measured under the `+8` perturbation, a different control) | ⚠ **OPEN. I did not settle it and will not guess** |

⚠ **One more limitation of the contrast, for the record: it had NO C arm.** Even
the assembly column was measured over six Rust decode kernels only.

⚠ **`p42` is the standing counter-example the task file names and it holds:** a
BUILT row whose entire result is proof burden and harm, `obligations 18`,
`TCB 5/16`, two `Ir` points and no rate. **A mechanism can be worth a row while
moving `Ir` by nothing** — so "the ladder cannot price it" must always name a
column.

---

## §A-MEASURED — THE CONTROL, WITH THE MISSING INSTRUMENT ON IT

`.temp/t128/limb2/gen.py`. ⚠ **The kernel is ONE PYTHON STRING emitted verbatim
into every arm**, so "the kernel is held fixed" is true by construction and not
by inspection. Only the caller differs, and only in where `n` comes from.

- **arm E** — `n` is an INPUT EXTENT clamped at run time (`p02`/`p42`'s class).
- **arm P** — `n` is a PRIOR-PASS COUNT over the same input
  (`CVE-2021-23017`'s class).

```
$ ./verus_run.py .temp/t128/limb2/armE.rs --crate-type=lib
verification results:: 3 verified, 0 errors
$ ./verus_run.py .temp/t128/limb2/armP.rs --crate-type=lib
verification results:: 5 verified, 0 errors

$ python3 .temp/t128/count_burden.py limb2/armE.rs limb2/armP.rs
file       items exec_fn spec_fn proof_fn requires ensures loop_inv loop_dec ghost tcb tcb_lines
armE.rs    3     3       0       0        2        2       4        1        9     1   1
armP.rs    4     4       0       0        2        3       6        2        13    1   1

$ python3 .temp/t128/symcmp.py k_emit limb2/armE_c limb2/armP_c
limb2/armE_c  ..6armE_c6k_emit  size=243  sha256=a379bee990da90af
limb2/armP_c  ..6armP_c6k_emit  size=243  sha256=a379bee990da90af

$ python3 .temp/t128/kir.py 2000 k_emit limb2/armX_c 64 31     # work-matched
armE_c  whole=1,325,520  k_emit_excl=352,000  calls=2000  per-call=176.00  OK
armP_c  whole=1,981,500  k_emit_excl=352,000  calls=2000  per-call=176.00  OK
```

**Must-fire arms — all four fired:**

| arm | what it must do | result |
|---|---|---|
| **M1** `armP_noens.rs` | delete `k_size`'s `ensures`; Verus must FAIL | ✅ `precondition not satisfied … n <= src@.len()`, `4 verified, 1 errors` |
| **M2** `armE_plant.rs` | one planted `invariant`; the counter must SEE it | ✅ ghost clauses `9 → 10` |
| **M3** `armE_c` at `ext=64` | work not matched; the `Ir` probe must move | ✅ `322.00` vs `176.00` |
| **M4** calibration | what does Verus's `verified` tally count? | ✅ arm E + a trivial fn = `4`; arm E + a fn **with a loop** = `5`. So arm P's `+2` is `1 function + 1 loop`, not an artefact |

⚠⚠ **AND THE REASON THE CANCELLATION ARGUMENT HAS NO PURCHASE HERE, STATED
PRECISELY.** `TASK_124`'s kill is that the sizing pass is *"a term COMMON TO BOTH
ARMS of every published DIFFERENCE"*, so it cancels. **`obligations`, `TCB items`
and `TCB lines` are NOT rung differences.** `results/synthesis.md` §3 publishes
them **per pattern, one row per pattern**, not as `R_x − R_y`. There is nothing
for them to cancel against. **That is the whole of why one column survived a
control that killed the other two, and it is structural rather than lucky.**

- **CONCLUSION (measured, stands on the numbers above):** a pure change of the
  bound's provenance moves the published `obligations` column and moves nothing
  the machine emits.
- ⚠ **MECHANISM (argued, NOT measured — marked OPEN per PROTOCOL rule 9):** *a
  prior-pass bound is a relation between two traversals and therefore a proof
  obligation, while an extent is a value and therefore a run-time check.* One
  probe is not a proof of that; a second construction could put the burden on the
  other arm.

---

## §B — LIMB 3, AND IT DOES NOT FALL THE WAY THE TASK FILE EXPECTED

### B1 — the machine columns: the manager's guess is RIGHT, and `p13` confirms it rather than refuting it

⚠⚠ **The task file's least-sure call #2 asked me to check `p13` first because it
"reads like a REASON that priced". It is the opposite, and `p13`'s own `NOTES.md`
says so** (`patterns/p13-strncpy-trunc/NOTES.md` §4c, reviewed at
`TASK_045_REVIEW`, published as finding 25):

```
                                              slope, band L    Ir/call, small
R3ship   position(...).unwrap_or(DST_CAP)      +65.962          3762.70
S_walk   R2's UNBOUNDED but CHECKED walk       +65.962          3762.70
U_pos    R4bulk + position()                   +65.962          3718.70
u5       R4bulk + `while d < DST_CAP && ...`   (= U_pos)        3718.70
R4ship   unbounded UNCHECKED walk              +81.962          3939.70
```

> *"the check is one way of handing LLVM the bound and not the only one, and it
> is the bound that is worth the 2.00 Ir/byte."*

**Three different REASONS the consumer's bound reaches LLVM — an iterator, a
bounds CHECK, and an explicit unchecked BOUND — agree to five decimals on the
slope and to the instruction inside their family, while the OUTCOME
(bounded vs unbounded) prices at `+16.000 Ir`/call per unit `L`.** `p13` is the
tree's strongest evidence FOR "the ladder prices the outcome, not the reason".

**Reproduced independently** (`.temp/t128/limb3/reasons.rs`, plain `rustc`
`-C opt-level=3`; all seven arms return `acc=696`):

```
k_guard      dominating guard   `if n > src.len()`      489.00 Ir/call
k_unchecked  check DELETED      `get_unchecked`         489.00
k_reslice    reslice            `&src[..n]`             490.00
k_iter       iterator           `src[..n].iter()`       491.00
k_clamp      clamp              `min(n, src.len())`     491.00
k_noelide    NOTHING supplies the bound                 491.00
k_dyncheck   check FORCED to survive (`black_box(i)`)  1809.00   <- MUST-FIRE
```

**Five reasons plus outright deletion span `2.00 Ir`/call on a 200-byte fold =
`0.41%`** — an order of magnitude under the `±4.6%` layout floor. The must-fire
arm separates elided from surviving at **3.70×**, so `0.41%` is a measurement.

- ⚠ **A designed arm did NOT fire and I am recording it rather than dropping
  it**: `k_noelide` — *no source of the bound at all* — still reads `491.00`,
  because **LLVM unswitched the bound out of the loop unaided**. *No source of
  the bound* is not the same as *no elision*. `k_dyncheck` replaced it.
- ⚠ **Not attributed:** `black_box` also blocks unrolling and vectorisation, so
  the `1318.00` gap is **not** the price of the check.
- Symbol bytes DO differ across the reasons (160/169/176/177/185 B) — the
  prologue differs, the loop cost does not.

### B2 — the proof-burden column: limb 3 prices there too, exactly as limb 2 does

Two reasons the unchecked read is in bounds, same work, same trusted accessor
(`.temp/t128/limb3/gen_proof.py`) — `p04`'s own distinction, **bits vs range**:

| | arm RANGE (linear) | arm MASK (bits) | moved |
|---|---|---|---|
| Verus `verified` (= `obligations`) | **2** | **4** | **+2** |
| ghost clauses | 6 | 8 | +2 |
| TCB items / lines | 1 / 1 | 1 / 1 | 0 |
| `k_fold` symbol | 160 B `eae74840cc627510` | 131 B `5e43fe8df79e6287` | differs |
| `k_fold` Ir/call | 621.00 | 845.00 | +224.00 |

- **must-fire:** remove `by (bit_vector)` from arm MASK →
  `precondition not satisfied` at `get_unchecked(src, i & 255)`,
  `1 verified, 1 errors`. ✅
- **calibration:** arm RANGE **plus one** `by (bit_vector)` assert also reads
  `4 verified`, so arm MASK's `+2` is exactly the bit-vector query.
- ⚠⚠ **HONEST WEAKENING, AND IT IS THE MOST IMPORTANT CAVEAT IN THIS REPORT:
  this pair does NOT hold the exec code fixed** — `i & 255` is real code, which
  is why the machine columns move by `+224.00`. **You cannot in general change
  the reason a check is elided without changing the operator.** Where you *can*
  (B1's five arms), the machine columns move by `0.41%`.

---

## §C — LIMB 1, ON THE BUILT TREE, AGAINST THE `±4.6%` FLOOR

The task file is right that limb 1's control cannot be posed — the operator *is*
the kernel — so I answered the answerable question, and **the tree already runs
that control 100 times.** Every pattern ships a hardened C twin which is the
plain C rung with the safety-line operator **added** and, by the pattern's own
hashed declaration, nothing else changed. `p23`'s `why` says it in those words:
*"so `c-gcc-h` minus `c-gcc` is the price of the scan guard and of nothing
else."*

`.temp/t128/limb1/hardened_census.py`, over `git show df14f4f:results/*.json`,
`O3 / isolated`, `small` + `large`, both backends:

```
rows: 100   |dIr| > 4.6% floor: 35   at or below the floor: 65
wall rows: 100   |dwall| > 4.6% floor: 26   at or below: 74
patterns: 25   with ANY row above the Ir floor: 12
   -> p02 p03 p04 p06 p09 p11 p14 p18 p19 p22 p36 p47
MUST-FIRE ARM: at least one row above the floor -> OK
```

**25 patterns and not 26, checked rather than assumed:** `p01-array-sum` ships no
hardened C twin at all (`cells` are `c-gcc, c-clang, safe_naive,
safe_naive_verus, safe_tuned, unsafe, verus`), so it cannot enter this control.
`25 × 2 backends × 2 inputs = 100`.

Range: `p42` and `p10` at `0.00%`, `p47` at `+237.01%`, `p19` at `+361.78%`,
`p23` at `−1.39%`. **So limb 1 is the only limb that prices on the machine
columns at all — and it clears the layout floor on about a THIRD of rows, and on
13 of 25 patterns it never clears it on any row.** That is a much weaker "pass"
than the bar's text implies, and it is what the task file predicted when it
warned that limb 1 "will look like a PASS".

---

## THE CLEAN NEGATIVE — `p23`, the only row ever admitted under this bar

`patterns/p23-partition/NOTES.md:68-86` claims **all three limbs**. Against
`p23`'s own published numbers:

- **limb 1** — *"the guard is a comparison of two loop variables"*. The tree's
  own operator control gives `p23` **`−1.39 / −3.66 / +0.13 / −1.60 %`**: every
  row **below** the `±4.6%` floor, and the sign flips between backends.
- **limb 2** — *"each cursor's bound is the other cursor"*. `p23`'s published
  `obligations` is **16**, mid-tree (`7…21`); `proof_fn` **0**; TCB `5 / 10`.
  No proof-burden signature. ⚠ The one possible trace is `loop_decreases = 6`
  (joint 3rd of 26), from `decreases j - i` at three loops — **I did not isolate
  it and do not claim it.**
- **limb 3** — *"a new reason the check is or is not elided"*. ⚠⚠ **`p23`'s own
  `NOTES.md` says: "⚠ The CAUSE is OPEN … A limb that claims a new *reason* owes
  an isolation and not just a measurement — the phenomenon is what ships, and it
  is enough."** The two isolations that were tried (`TASK_105` M4) refuted the
  reason it was admitted for.

> ⚠⚠ **So the only row ever admitted under this bar claims three limbs and
> demonstrably exhibits at most one — and the limb it demonstrates best is a
> PHENOMENON whose REASON its own file records as open. The bar's problem is not
> only its text; it is that nothing checks a limb claim against the row's own
> numbers afterwards.**

---

## §D — THE VERDICT

⚠ **SHAPE 1, with one refinement, and the refinement is the finding.**

1. **The premise inverts.** `TASK_124` measured **two** columns of six, not one
   of six and not all six. **Limb 2 is NOT known-unpriceable**, and this is not a
   reading — the missing column was measured here and it moves by `+2`
   obligations with a firing must-fire arm.
2. **The bar's three limbs are intact. What is wrong is that the bar does not
   say WHICH COLUMN each limb prices on, and every reader so far has silently
   supplied "the machine ones".** The measured assignment:

   | limb | machine columns (assembly, `Ir`, timing, identity) | proof burden / TCB |
   |---|---|---|
   | **1** a new operator on the safety line | ⚠ **prices, on 35 of 100 rows** of the tree's own control; below the floor on the other 65 | not measured here |
   | **2** a new source of the bound | ❌ **`+0.00`** — twice measured, `TASK_124` and here | ✅ **`+2` obligations, `+4` ghost clauses** |
   | **3** a new reason the check is/is not elided | ❌ **`0.41%`**, under the layout floor; `p13` says the same to five decimals | ✅ **`+2` obligations** |

3. ⚠ **I am NOT reaching for shape 3.** *"The project has been writing its
   admission bar in terms of what the PROGRAMMER MEANS while its instrument sees
   only what the MACHINE DOES"* is **half right and the half that is wrong
   matters**: the project has a sixth column that sees exactly what the
   programmer means, it publishes it in `results/synthesis.md` §3, and **nobody
   pointed it at the question.** The honest sentence is:

   > **Five of this ladder's six published columns see only outcomes; the sixth —
   > proof burden and trusted base — is the only one that sees provenance and
   > reasons, and it is the one no limb-2 or limb-3 argument has ever been
   > measured against.**

4. **Shape 2 is refused with a reason.** Limb 2 does not need striking or
   restating; restating it as *"a new source of the bound THAT CHANGES THE
   CHECK'S COST"* would be **wrong**, because it changes no check cost and is
   still worth something. The bar keeps **three** limbs.

### The correction owed, and its blast radius is TWO LINES

`grep -rn "cannot price\|every published difference"` over `.memory/`, `RECAP.md`
and `results/*.md`:

- **`RECAP.md:2599`** (finding 42) — *"⚠⚠ **EVERY PUBLISHED DIFFERENCE MOVES BY
  EXACTLY `+0.00`** … ✅ **So *a new SOURCE of the bound* is a distinction THIS
  LADDER CANNOT PRICE**"*. Both sentences need the column named: **every
  published `Ir` difference**, and **cannot price on assembly or `Ir`**.
- **`RECAP.md:14`** (the START HERE box row) — same sentence, same fix.
- ✅ **`.memory/` is CLEAN** — the claim never reached the authoritative layer.
  **Rule 9 held**, and this is the first time I can find that it visibly paid.

⚠ **An observation, not a measurement, offered because it is the same class:**
`results/SYNTHESIS.md` §5 is titled *"what this instrument can and cannot price"*
and its (already-DISPUTED) claim is stated entirely in machine-code terms —
*"no machine-code footprint at all"* — in a document whose own §3 publishes
obligations and TCB. **The conflation of "the instrument" with "the machine
columns" is systemic in this project's prose, not a one-off in finding 42.**

---

## PROBLEMS / NOT DONE / UNSURE

- ⚠ **Timing (column 3) not measured, deliberately.**
  `.memory/03-measurement.md`: *"Concurrent load corrupts a wall-clock block —
  now MEASURED, not just warned."* `TASK_127` is running in this tree. Every
  wall-clock figure I quote is read out of `git show df14f4f:results/*.json`,
  i.e. from records taken when the box was quiet.
- ⚠ **Harm matrix (column 6) under the provenance control: OPEN.** Not measured
  by `TASK_124`, not measured by me. My probe kernels are Verus-proved
  memory-safe, so there is nothing for a sanitiser to see; a real answer needs a
  buggy pair and I did not build one.
- ⚠ **Limb 1's proof-burden column not measured.** The `35 / 100` figure is
  machine columns only.
- ⚠ **The limb-2 MECHANISM is OPEN** (see §A-measured). One probe.
- ⚠ **My limb-3 proof pair does not hold the exec code fixed** (§B2). Stated in
  the section rather than buried here.
- ⚠ **`p23`'s `loop_decreases = 6` may be a limb-2 proof-burden trace and I did
  not isolate it.** Anyone attacking my clean negative should start there.
- **Three instrument defects in my OWN probes, all caught by a must-fire arm,
  all fixed and all transferable:**
  1. ⚠⚠ **callgrind `fn=` and `cfn=` share ONE name-compression space.** A
     parser that learns names only from `fn=` lines returns a **silent zero**.
     Measured: `armE_c` read `k_emit_excl=0` while `armP_c` read `176.00` from
     the same parser on the same symbol.
  2. ⚠⚠ **LLVM hoisted the whole kernel call out of my driver loop** and
     callgrind recorded `calls=1`, so the probe printed `0.42 Ir/call` for a
     256-byte fold. `kir.py` now asserts the call count on **every** run.
     Reviewer-checklist item 1, caught by the instrument and not by eye.
  3. ⚠ **`git ls-tree <commit> results/` resolves its pathspec against the
     CURRENT DIRECTORY.** Run from `.temp/t128` the census matched nothing and
     printed `rows: 0` — *a detector that is not running looks exactly like one
     that found nothing*, which is this task file's own warning, landing on me.
     Its must-fire arm printed `*** ARM FAILED ***`. Pinned with `git -C REPO`.
- **Probe-2 defect 6 avoided as instructed**: `symcmp.py` takes every symbol
  extent from `readelf -sW`, never from disassembly text.

## OUT OF SCOPE and UNPROBED — one paragraph, per §E

⚠ **Not a proposal for a 27th pattern.** The measurement above says the project
owns an instrument — `obligations` + `TCB items`/`lines` — that separates rows
the machine columns cannot separate, and that it has never been used as an
*admission* instrument, only as a reported one. **If anyone ever re-opens the
bar, the cheap thing to run first is `.temp/t128/limb2/gen.py`'s shape**: hold
the kernel byte-identical, change the property the limb claims, and read
`obligations` rather than `Ir`. It cost about forty minutes here and it inverted
a finding. ⚠ **Offered as a suggestion, not wired up (`CLAUDE.md` rule 3), and
explicitly NOT an argument for building or for stopping — finding 41 forbids
both.**

## TREE STATE

- `git status` at finish: 26 modified tracked files + 2 untracked. **None are
  mine** — all are `TASK_127`'s. I wrote only `.temp/t128/**` and this file.
- `.temp/t128/` is **1.1 M**; `BUILD.sh` regenerates every source, binary and log
  and deletes the binaries. No binary, `.o`, `.pyc` or `.bin` remains.
- `harness/vparse.py` was **copied** out of `df14f4f` into `.temp/t128/` and the
  copy was run; the tree's file was never executed or read live.

## RUNNING COUNT

`583 → 594`. ⚠ **Reconciliation is the manager's job, not mine; `TASK_127` is
carrying its own. I am carrying, not re-adding.** The eleven:

1. `TASK_124`'s provenance contrast measured **2 of 6** published columns (§A);
2. the proof-burden column **moves** under a pure provenance change — `3 → 5`
   obligations, must-fire fired (§A-measured);
3. the reason it survives is structural: `obligations`/`TCB` are **per-pattern
   absolutes, not rung differences**, so nothing cancels (§A-measured);
4. the TCB column does **not** move under a provenance change — clean negative;
5. `p13` **confirms** the limb-3 hypothesis rather than refuting it, and the
   manager's least-sure call #2 was right (§B1);
6. five different elision reasons span **0.41%**, an order under the layout
   floor, reproduced independently (§B1);
7. *"no source of the bound"* ≠ *"no elision"* — LLVM unswitches it unaided, and
   a designed must-fire arm failed on exactly that (§B1);
8. limb 3 also prices on `obligations` (`2 → 4`), with the exec-code confound
   disclosed (§B2);
9. limb 1 clears the `±4.6%` floor on **35 of 100** rows of the tree's own
   operator control, and on 13 of 25 patterns never (§C);
10. `p23` claims three limbs and demonstrably exhibits at most one, and its own
    file records the limb-3 cause as OPEN (clean negative);
11. three instrument defects in my own probes, each caught by a must-fire arm —
    a callgrind name-compression silent zero, an LLVM-hoisted `calls=1`, and a
    `git ls-tree` pathspec resolved against the wrong directory.
