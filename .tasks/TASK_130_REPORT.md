# TASK_130 — REVIEW of `TASK_128` and of finding 44. THE ENGINEER IS WRONG, THE MANAGER IS RIGHT, AND THE MANAGER'S REASON IS THE WEAKEST OF THE THREE AVAILABLE

**Role: research reviewer.** Scratch, generators and every log: `.temp/t130/` —
`RUN.sh` regenerates every source, binary and log and deletes the binaries.
Nothing outside `.temp/t130/` and this file was written. `harness/check.py`,
`build.py`, `measure.py`, `report.py` were **not run**. No `git add`, no
`git commit`. Every committed number is read with `git show HEAD:` — and
`git diff --stat df14f4f HEAD -- results/` touches **only**
`results/SYNTHESIS.md`, so `HEAD`'s `results/pNN-*.json` **are** `df14f4f`'s and
my numbers are comparable with `TASK_128`'s line for line.

---

## §A VERDICT — DECIDED, WITH EVIDENCE, AS RULE 3 REQUIRES

> ⚠⚠⚠ **The manager's reading is CORRECT. The engineer's headline is not merely
> unsupported — IT IS INVERTED. The columns that separate the limb-2 mechanism
> are ASSEMBLY and `Ir`; `obligations` is the one column that CANNOT, and at the
> project's own kernel convention it RANKS THE DEAD-CODE ARM ABOVE THE
> MECHANISM ARM.**

> ⚠⚠ **AND THE MANAGER'S STATED REASON — `_calib2` — IS THE WEAKEST OF THE
> THREE ARGUMENTS AVAILABLE, AND THE §A DEFENCE GENUINELY BLUNTS IT.** The
> defence is answered not by argument but by three measurements the manager did
> not have. **If the manager had had only `_calib2`, the engineer would have had
> the better of it.**

### A1 — the deciding arms: the SAME contrast at the PROJECT'S kernel convention

`TASK_124` and `TASK_128` both put the sizing pass **outside the measured
symbol**. The tree's kernel symbol is the whole of what the driver calls once
per record, and ⚠ **`TASK_124_REPORT.md` §B4 established that itself**: *"A
two-pass structure does not need two calls"* — `p42` mallocs inside `kernel()`,
and p09/p36/p38/p46 define helpers in the kernel TU. So I rebuilt the identical
contrast with `#[inline(never)]` on the whole two-pass function, which is what a
real pattern would ship (`.temp/t130/limb2/gen_kernel.py`):

```
arm  mechanism            kernel symbol   kernel sha256      kernel-excl Ir/call  obligations
kE   input extent         199 B           ffd9c4e2186777aa        121.00              3
kC   extent + DEAD loop   199 B           ffd9c4e2186777aa        121.00              5   <-- dead code
kP   PRIOR-PASS COUNT     407 B           f6040ef542cf2f58        450.00              4   <-- the mechanism
```

⚠⚠ **`kE` and `kC` are BYTE-IDENTICAL — same 199 B, same sha256 — while
`obligations` differs by `+2`. And `obligations` ranks the dead-code arm (5)
ABOVE the mechanism arm (4).** The published assembly column and the published
`Ir` column both separate the mechanism cleanly, agree with each other, and
place `kC` exactly where it belongs.

> ✅ **So *"the ladder can price a mechanism it cannot price in instructions;
> the column is `obligations`"* is not just unproven. The instrument the
> engineer named is the ONE that fails, and the instruments it wrote off are the
> ones that work.**

### A2 — `obligations` is neither NECESSARY nor SUFFICIENT for limb 2

Seven arms, kernel string emitted verbatim into every one (`gen.py`; `k_emit`
243 B `a379bee990da90af` in all four compiled arms, reproducing `TASK_128`
exactly). Must-fire: `armPinline_bad` deletes the `cnt <= i` invariant and
Verus reports `2 verified, 2 errors` at the call site.

| arm | limb-2 mechanism? | how it is SPELLED | `obligations` | ghost | TCB |
|---|---|---|---|---|---|
| `armE` | **NO** | run-time clamp of an input extent | 3 | 9 | 1/1 |
| `calib2` | **NO** | armE + an UNCALLED proved counting fn | **5** | **13** | 1/1 |
| `armEhard` | **NO** | armE, `k_emit`'s proof made strictly HARDER (value-level `ensures`, same exec code, no new fn, no new loop) | **3** | **13** | 1/1 |
| `armP` | **YES** | sizing pass in its own function | 5 | 13 | 1/1 |
| `armPinline` | **YES** | the same pass, **not factored out** | **4** | 12 | 1/1 |
| `armPext` | **YES** | the same pass, spelled `external_body` (how 26 patterns spell a pass they do not verify) | **3** | 10 | **2/6** |
| `armPspec` | **YES** | the same pass, count specified exactly | **7** | 18 | 1/1 |

```
mechanism PRESENT  ->  obligations in {3, 4, 5, 7}
mechanism ABSENT   ->  obligations in {3, 5}
                       THE TWO SETS OVERLAP AT 3 AND AT 5.
```

⚠ **`armEhard` is the arm `_calib2` is missing**: it makes the proof strictly
harder with **no new function and no new loop**, and the column does not move at
all (3), while `ghost_clauses_total` moves to 13 — the same value `armP` and
`calib2` both carry. **Every proof-burden column the engineer computed reads
IDENTICALLY on `armP` and `calib2`**: items 4/4, exec_fn 4/4, spec_fn 0/0,
proof_fn 0/0, requires 2/2, ensures 3/3, loop_invariant 6/6, loop_decreases 2/2,
ghost 13/13, TCB 1/1, TCB lines 1/1.

### A3 — THE RATIO, AND IT DISSOLVES THE CRUX RATHER THAN ANSWERING IT

The crux as posed — *does pricing require distinguishing the mechanism from ANY
change of the same size, or only from ITS OWN ABSENCE?* — is a false dilemma,
and the arms settle it without appealing to either horn. The operative question
is measurable: **how large is a column's variation across SPELLINGS of the
mechanism, against its variation between PRESENCE and ABSENCE?**

```
Ir            spelling spread      77 total   (armP 1,981,500 vs armPinline 1,981,423
                                               = 0.039 Ir/call, 0.004%)
              presence gap    655,982 total   (armP vs calib2, +327.99 Ir/call,
                                               kernel work MATCHED: k_emit_excl
                                               = 352,000 in all four arms)
                                               ------------------  ratio  8519 : 1

obligations   spelling spread        2        (armP 5 / armPinline 4 / armPext 3
                                               — one mechanism, three spellings)
              presence gap       <= 2         (armE 3 vs calib2 5), and NEGATIVE
                                               at the kernel convention (kC 5 > kP 4)
                                               ------------------  ratio     1 : 1
```

⚠⚠ **`Ir` is invariant under re-spelling of the mechanism and moves under its
presence. `obligations` is the exact reverse: it moves under re-spelling and is
invariant under presence.** That is why `Ir` prices a bounds check and
`obligations` does not price limb 2, and it needs no philosophy about what
counts as a control. Reproduced twice **to the instruction**; `calib2 − armE` is
`+1` on a whole-program total of 1.3 M, i.e. zero; doubling the input doubles
the gap (`638.998 Ir/call` at `n=128`).

### A4 — THE ENGINEER'S DEFENCE IS FALSE ABOUT THIS PROJECT'S PRACTICE, AND BOTH PRECEDENTS THE TASK FILE NAMED SAY SO

> *"`Ir` is accepted as PRICING a bounds check even though an unrelated `add`
> costs instructions too; by that same standard, `obligations` prices limb 2."*

⚠⚠ **This project has TWICE required an `Ir` figure to be distinguished from
*the same work spelled a different way*, and BOTH TIMES it struck a published
number when the distinction failed.**

- **`p23` / `TASK_106`, `k_u5`** (`patterns/p23-partition/NOTES.md`, HEAD): a
  tautological conjunct, **the same relocation-masked disassembly `md5_norm
  da08af26d9b1`, 249 instructions each**. The conclusion drawn was NOT *"so the
  conjunct prices at 0"*; it was **"the published floor was 150.00 `Ir`/call too
  high"** and *"at least **150.00** of the published safe-side figure is
  attributable to the spelling and not to safety"* — plus *"a declaration that a
  semantically-null respelling can walk around is not enforcing the number it
  was thought to be enforcing."*
- **`p46` §8a, rolled-vs-rolled** (`patterns/p46-bignum-mac/NOTES.md`): the
  published `R2 − R4` turned out to be an unroll decision plus a
  carry-materialisation spelling, derived instruction by instruction, and the
  sentence the pattern now publishes is **"p46's per-MAC safety tax is 0.00000
  and that is the sentence to quote."**

⚠ **The task file guessed these were precedents in opposite directions. They are
not — they point the same way, and it is against the engineer.** The project's
actual standard for `Ir` is *attribute a difference to a mechanism only after
same-work respellings have been searched and found not to produce it.* That is
the standard the manager applied to `obligations`, and it is the standard
`obligations` fails by a factor of 8519 relative to `Ir`.

### A5 — the engineer's STRUCTURAL argument proves too much, and this half of finding 44 must go

Finding 44 keeps one paragraph of the engineer's reasoning as *"structural and
survives"*: `obligations`/`TCB` are published **per pattern**, so *"there is no
second arm for the common sizing-pass term to cancel against."*

⚠⚠ **That argument, applied evenly, gives `Ir` the same property — and
`TASK_124` measured it.** Its §B1 table is a **level** move of **`−63.00`
`Ir`/call in every one of seven cells**. `Ir` is published per cell as a level
in `results/tables/*.md`, exactly as `obligations` is published per pattern.
**So the asymmetry the paragraph asserts does not exist**: comparing like with
like, both level columns move and both difference columns cancel — except that
`obligations` has no difference form at all, so it cannot even be compared
there. The paragraph reads as an explanation of why one column survived; what it
actually describes is the choice of comparison.

---

## §B — THE OPEN QUESTION, ANSWERED: **YES**, AND IT ANSWERS AGAINST THE ENGINEER

> *"Does ANY published column distinguish `armP` from `_calib2`?"*

| published column | at `TASK_128`'s factoring (kernel = `k_emit`) | at the PROJECT's kernel convention |
|---|---|---|
| **assembly** | kernel identical (243 B `a379bee9`) — but the crate's own `main` extent is **2925 vs 2575**, and armE/calib2 are **both 2575** | ✅ **YES: 407 B vs 199 B, and `kE`/`kC` are BYTE-IDENTICAL** |
| **instruction count** | ✅ **YES: +327.99 `Ir`/call at matched kernel work** (`calib2 − armE` = +0.0005/call) | ✅ **YES: 450.00 vs 121.00, 3.72×** |
| **timing** | not measured (`TASK_127`/`TASK_129` are live; concurrent load corrupts a wall-clock block) | same |
| **proof burden** | ❌ **NO — identical on all eleven counters** | ❌ **WORSE THAN NO: `kC` 5 > `kP` 4** |
| **trusted base** | ❌ NO (1/1 both). ⚠ and the "clean negative" is spelling-dependent — `armPext` reads **2 items / 6 lines** for the same mechanism | same |
| **harm matrix** | not measured; all arms are Verus-proved memory-safe, so there is nothing for a sanitiser to see | same |

⚠ **`ghost_clauses_total` and `proof_fn` were the two the task file asked about
specifically. Neither separates them** — and `ghost_clauses_total` additionally
gives `armEhard` (no mechanism, harder proof) the same 13 as `armP`.
✅ **Verification wall time was checked and separates nothing**: 0.93–0.97 s for
all seven arms, startup-dominated (indicative only, two tasks live).

---

## §C — LIMB 1's CENSUS: the FLAG premise HOLDS, the SOURCE premise FAILS, and the FLOOR is the wrong floor

### C1 ✅ CLEAN NEGATIVE — the confound the task file named is NOT there

`harness/build.py` (read, not run): `c_flags(opt, mode, panic)` **never sees the
kernel name**; `build_c` swaps `c/kernel.c` for `c/kernel_hardened.c` and
changes nothing else — same compiler, same `-std=c99 -Wall -Wextra -O3
-DSLB_ISOLATED`, same `common/driver.c`, same `main.c`, same include dirs. ⚠
**So "a different flag set, a different libc entry point, a stack-protector's
prologue" does NOT land, and I say so as a named attack that failed.** Verified
across all 25 twins: identical `#include`/`#define`/`#pragma` sets and an
identical `kernel` signature in every one (`.temp/t130/limb1/twin_diff.py`).

### C2 ⚠⚠ BUT THE SOURCE PREMISE FAILS, AND IT FAILS ON THE CENSUS'S TWO EXTREMES

*"the hardened-C twin IS the plain rung plus the safety-line operator and
nothing else"* is true of `p23` — its `why` says so verbatim and I verified the
quote — but the census **pools 25 patterns under that one label**, and the thing
added is not one kind of thing:

```
p11   strlen  ->  memchr                      A LIBC ROUTINE SWAP        max |dIr|  12.18%
p19   + a whole O(TBL) validation LOOP        A NEW PASS                 max |dIr| 361.78%   <-- census max
p47   memcmp/bcmp early-exit -> full-length
      or-accumulate over every byte           AN ALGORITHM SWAP          max |dIr| 237.01%   <-- 2nd
(also below the floor: p08 memcpy->memmove, p38 punned u32 load -> two u16 loads,
 p42 return -> goto cleanup, which is a LEAK fix and not a check at all)
```

⚠ **Each pattern's own file is honest** — p19's `why` says *"THE VALIDATION
PASS"*, p47's says the difference *"IS the pattern"*. **The overreach is the
census's aggregation, not any pattern's declaration.**

**Blast radius, measured:** 10 of the 35 above-floor rows belong to p11/p19/p47.
Restricted to twins that really are *plain + a compare/branch/arithmetic guard*:
**25 of 90 rows, 9 of 22 patterns.** ✅ *"About a third"* survives as a
qualitative statement; **`35 / 100` and `12 of 25` do not survive as the
limb-1 numbers.**

### C3 ⚠⚠ THE `±4.6%` FLOOR IS AN `ns` FLOOR, AND IT WAS APPLIED TO A CALLGRIND COLUMN

`patterns/p06-rotate/NOTES.md:351`, verbatim: **"Take ±4.6% as the honest
inter-binary floor for every `ns` figure in this file."** It is a layout
population over `ns`, and `.memory/03-measurement.md` says of exactly that
instrument: *"a LAYOUT POPULATION IS THE WRONG TOOL … it varies the program,
measures `ns`, and **callgrind is layout-blind**, so it would return ≈0 and read
as 'no effect.'"* The same file measures the `Ir` side of that axis at
**`kernel_exclusive` `3002.00` in ALL NINE runs** of the 32-pad sweep — a
**measured zero**.

⚠ **So the census applied a wall-clock layout floor to a deterministic
instruction-count column, and it fails in the direction of UNDER-reporting.**
The smallest `Ir` in the census is `310,504`, against which the documented ±7 Ir
artefact is **0.002%** — three orders below 4.6%. The honest `Ir` statement:

```
94 of 100 rows move at all      56 of 100 above 1%      median |dIr| = 1.77%
35 above 4.6%   27 above 10%   8 above 25%   6 above 100%
```

✅ **The `wall` half of the census (26 of 100) is sound** — there the `±4.6%`
floor is the right floor, and it is the floor's own home instrument.
⚠ **19 rows clear the floor on both columns and 4 of the 35 `Ir`-movers have a
wall column that moves the OTHER WAY.**

---

## §D — THE CLEAN NEGATIVE: two of its three cells are scored against a criterion the bar does not state

### D1 — all three cells verified from the committed record ✅

- **limb 1** — `results/pNN-*.json` at HEAD: `−1.39 / −3.66 / +0.13 / −1.60 %`
  (c-gcc small/large, c-clang small/large). Every one below `±4.6%`; the sign
  flips. ✅ reproduced exactly.
- **limb 2** — `results/gate/p23-partition.json`:
  `verus["verus.rs"].verified = 16`, `errors 0`, `tcb_items 5`; `proof_fn 0`
  from the gate's own parser. ✅ ⚠ **but "mid-tree" understates it**: the tree
  runs `7 … 21` with **median 12**, and 16 is **19th of 26**.
- **limb 3** — `patterns/p23-partition/NOTES.md` at HEAD: *"⚠ **The CAUSE is
  OPEN.** … A limb that claims a new *reason* owes an isolation and not just a
  measurement — the phenomenon is what ships, and it is enough."* ✅ verbatim.

### D2 ⚠⚠ AND THE QUESTION THE ENGINEER DID NOT ASK: *"EXHIBITS A LIMB"* HAS NO OPERATIONAL DEFINITION, AND THE BAR IS A **NOVELTY** TEST

The bar reads: *"A row is admissible whenever it **brings a new MECHANISM** —
(1) a new **operator on the safety line**, (2) a new **source of the bound**, or
(3) a new **reason the check is or is not elided**."* ⚠ **It says *brings*, not
*prices*. Nothing in it mentions a column, a floor or a delta.** *"Exhibits"* is
the engineer's word, not the bar's, and it is never defined.

⚠⚠ **p23 states each limb as a NOVELTY claim against the built set, with the
enumeration written out**: *"Every earlier bound here comes from outside the
loop: a header field (p05, p07, p16, p17, p19, p36), a compile-time capacity
(p03, p06, p12), a live length (p04, p14)."* And its limb-1 claim — *"the guard
is a comparison of two **loop variables**, not of an index against a length"* —
is checkable and, on my own twin census, **true**: p23 is the only one of 25
twins whose added guard compares two moving cursors.

> ✅ **So the clean negative is two-thirds rhetoric and one-third real.** Limbs 1
> and 2 are scored against a detectability test neither p23 nor the bar states,
> and p23 satisfies both on the bar's actual text. **Limb 3 genuinely fails, on
> the bar's own words** — it demands a new *reason*, and p23's own file records
> the cause as OPEN. ⚠ **The transferable finding is better than the one
> reported: the bar is a NOVELTY criterion and the project has been reading it
> as a DETECTABILITY criterion — which is the same conflation the engineer
> itself flagged as systemic ("the instrument" vs "the machine columns"),
> landing on the engineer's own clean negative.**

---

## §E — THE INSTRUMENTS: the self-caught defects, re-checked

✅ **The `git ls-tree` defect is genuinely fixed and the detector IS running.**
`.temp/t130/limb1/census2.py` is written from scratch and differs deliberately
(enumerates `patterns/` and asks for each record, `git cat-file blob` instead of
`git show`, an explicit `(cell,opt,mode)` index, a floor sweep, a must-fire on
the `>100%` bucket). It reproduces **exactly**:

```
patterns in tree: 26   with a hardened twin: 25   without: ['p01']
rows: 100   |dIr| > 4.6%: 35   at/below: 65
wall rows: 100   |dwall| > 4.6%: 26   at/below: 74
patterns with ANY row above the Ir floor: 12 -> p02 p03 p04 p06 p09 p11 p14 p18 p19 p22 p36 p47
MUST-FIRE ARM: at least one row above the floor -> OK
MUST-FIRE ARM 2: the >100% bucket must be non-empty (p19/p47) -> OK
```

✅ The callgrind name-compression fix and the `calls=` assertion both fired on
every one of my 14 `kir.py` runs (`OK` on all). Symbol extents came from
`readelf -sW` throughout (probe-2 defect 6 avoided).

⚠ **`.memory/03-measurement.md`'s failure-class entry 8 is this task's shape and
it now has a second instance.** `TASK_128`'s limb-3 arm `_calibRANGE_bv` is
`_calib2` again: arm RANGE **plus one unrelated `by (bit_vector)` assert** reads
`4 verified`, identical to arm MASK — reported as *"calibration: so arm MASK's
`+2` is exactly the bit-vector query"*. **Both of the engineer's `_calib` arms
are non-specificity refutations filed as calibrations, and finding 44 names only
one of them.** ⚠ Finding 44 calls limb 3's `obligations` claim unsupported *"for
limb 2's reason"*; it is unsupported for a **stronger** reason — its own control
arm demonstrates it directly.

---

## THE COLUMN ITSELF — `obligations` IS A CODE-SIZE PROXY, AND THE PROJECT ALREADY SAYS SO

`synthesis/synthesize.py:1217-1250` defines the column as
`gate.verus["verus.rs"]["verified"]`, and **the same paragraph already
documents its insensitivity**: an axiom *"adds no verified function, so
`obligations` does not move"*, and *"One column would let a 7-line reviewed
wrapper be traded for a zero-line unconditional axiom **at par**, and nothing in
the table would move."* ⚠ **The property `_calib2` demonstrates was already
published, one screen above the table it applies to.**

On the built tree (26 patterns, `.temp/t130/oblig_model.py`, gate parser):

```
corr(verified, exec_fn - tcb_items + proof_fn + loops) = 0.894
corr(verified, ghost clauses)                          = 0.820
corr(verified, verus.rs SOURCE LINES)                  = 0.795
```

And the decomposition is exact in the probes: `armE` = `k_emit` + its loop +
`run` = 3; `armP` = that + `k_size` + its loop = 5; `calib2` = that +
`probe_loop` + its loop = 5. **`verified` counts SMT query units — one per
function body, one per loop, two per `assert … by (bit_vector)` — and nothing
else.**

---

## FINDINGS, RANKED

**B1 · blocker · `RECAP.md:2805-2869` (finding 44) and `.tasks/TASK_128_REPORT.md`
HEADLINE.** The engineer's headline is **inverted**, not merely unsupported. At
the project's own kernel convention the assembly and `Ir` columns separate the
limb-2 mechanism (407 B vs 199 B; 450.00 vs 121.00 `Ir`/call) while
`obligations` ranks the **dead-code** arm above the mechanism arm (5 > 4).
Failure scenario: anyone acting on *"read `obligations` rather than `Ir`"* —
the engineer's own closing suggestion — selects the one column that is blind to
the property and discards the two that see it.

**B2 · blocker · `RECAP.md:2605-2607` (finding 42's REPLACEMENT sentence) and
`RECAP.md:12` (START HERE).** *"The true statement: a new source of the bound
cannot be priced **ON ASSEMBLY OR `Ir`**"* is **FALSE**. It cannot be priced on
any published **rung-to-rung DIFFERENCE**, because the sizing pass is a term
common to both arms. At the **level** it moves both columns: `TASK_124`'s own
§B1 measured **`−63.00 Ir`/call in all seven cells**, and my kernel-convention
arms give **`+329.00 Ir`/call and `+208` kernel bytes**. ⚠⚠ **This is the
second time in this thread that a strikethrough replaced one overstatement with
a *stronger* one — the exact shape `PROTOCOL` rule 9 records from `TASK_099`.**

**M3 · major · finding 44's *"structural and survives"* paragraph
(`RECAP.md:2835-2842`).** The level-vs-difference argument proves too much:
applied evenly it makes `Ir` price limb 2 as well, and `TASK_124` measured that
level move. Delete the paragraph or restate it as *a choice of comparison, not a
property of the columns*.

**M4 · major · finding 44's presentation of the crux.** The defence quoted at
full strength asserts something false about this project's practice.
`p23`/`k_u5` and `p46` §8a are both cases where the project **struck a published
number** (`150.00 Ir`/call; *"per-MAC safety tax is 0.00000"*) precisely because
the same work spelled differently produced the movement. Both should be cited in
the finding as the deciding precedent.

**M5 · major · `RECAP.md:2908-2914` and `TASK_128_REPORT.md` §C.** The census's
`±4.6%` floor is p06's **`ns`** floor (*"for every `ns` figure in this file"*),
applied to a callgrind column that the same `.memory/` file calls
**layout-blind** and measures at **exactly zero** noise on that axis. `35 / 100`
is not a property of limb 1; it is an artefact of an imported floor.

**M6 · major · same lines.** *"The hardened-C twin IS plain rung + the
safety-line operator and nothing else"* is a **build** truth (verified: no flag,
libc-entry or stack-protector confound) and a **source** falsehood for
p11/p19/p47 — which contribute **10 of the 35** above-floor rows and are the
census's two extremes. Restricted to clean-operator twins: **25 of 90 rows, 9 of
22 patterns**.

**M7 · major · `RECAP.md:2931-2937` (the clean negative).** *"Exhibits a limb"*
has no operational definition, and the bar's text is a **novelty** test, not a
**detectability** test. p23 states all three limbs as novelty claims with the
built set enumerated, and its limb-1 claim is checkably true (the only twin
whose guard compares two moving cursors). **The clean negative survives on limb
3 only.**

**m8 · minor.** *"the TCB column does not move under a provenance change — clean
negative"* is spelling-dependent: `armPext` carries the same mechanism at
**2 TCB items / 6 lines**.

**m9 · minor.** `p23`'s `obligations 16` is **19th of 26** against a median of
12, not *"mid-tree"*.

**m10 · minor.** Finding 44 does not record that limb 3's `_calibRANGE_bv` is
the same non-specificity refutation as `_calib2`.

---

## WHAT SHOULD CHANGE IN `RECAP.md` (manager applies; I edited nothing)

1. **Finding 42 + the START HERE row** — replace *"cannot be priced ON ASSEMBLY
   OR `Ir`"* with: **"moves no published rung-to-rung DIFFERENCE, because the
   sizing pass is a term common to both arms. It moves both LEVEL columns:
   `−63.00 Ir`/call in all seven of `TASK_124`'s own cells, and `+329.00
   Ir`/call with `+208` kernel bytes when the two passes sit inside the kernel
   symbol as a real pattern's would."**
2. **Finding 44** — keep it (manager's least-sure #2: **do not collapse it**;
   the §A premise inversion is real and the corrected verdict is now a
   measurement rather than an absence), but:
   - record §A as **DECIDED against the engineer, by the reviewer, with the
     kernel-convention arms, the spelling-vs-presence ratio and the
     p23/p46 precedents** — and record that `_calib2` alone would not have
     carried it;
   - delete or restate the *"structural and survives"* paragraph (M3);
   - **replace *"LIMBS 2 AND 3 PRICE ON NOTHING ANYONE HAS SHOWN TO BE SPECIFIC
     TO THEM"*** — limb 2 now has a measurement: **assembly and `Ir`, at the
     level, 8519:1 spelling-to-presence**;
   - qualify limb 1 per M5/M6;
   - correct the clean negative per M7.
3. **`.memory/03-measurement.md`** — add to the failure-class list, as a second
   instance of entry 8's shape: *`TASK_128`'s two `_calib` arms both FIRED and
   both refuted the sentence they were filed under.* And add, wherever the
   `±4.6%` floor is quoted: **it is an `ns` floor and callgrind is layout-blind;
   the measured `Ir` floor on that axis is ZERO.**
4. **`results/SYNTHESIS.md` §5** — the engineer's observation stands and is now
   measured: the conflation of *"the instrument"* with *"the machine columns"*
   is systemic, and here it ran in **both** directions in one task.

---

## PROBLEMS / NOT DONE / UNSURE

- ⚠ **Timing not measured**, deliberately: `TASK_127` and `TASK_129` are live and
  concurrent load corrupts a wall-clock block. Every wall figure I quote is read
  out of `git show HEAD:results/*.json`. The verification-time numbers are
  labelled INDICATIVE and are startup-dominated.
- ⚠ **Harm matrix under the provenance control: still OPEN.** Same reason as
  `TASK_128` — my arms are Verus-proved memory-safe.
- ⚠ **My kernel-convention arms are a construction, not a built pattern.** They
  show what the published columns *would* read if a two-pass kernel were shipped
  under `--cfg slb_isolated`. They rest on `TASK_124` §B4's own finding that a
  two-pass structure needs no second call; I did not build a 27th pattern and
  am not proposing one.
- ⚠ **`armPext` is contestable and I say so**: spelling the sizing pass
  `external_body` moves the burden to the TCB column instead of zeroing it. That
  is a partial defence of the engineer — *some* proof column moves — and it is
  why A2 does not rest on `armPext` alone. But the TCB move is `+1 item`, which
  is again a **count**, and would move identically for any unrelated trusted
  item.
- ⚠ **The twin classification in `census2.py::KIND` is mine and is a judgement**,
  read off the diffs in `.temp/t130/limb1/twin_diff_verbose.log`. A reader who
  calls p19's validation pass "an operator" gets `12` patterns back, not `9`.
  The diffs are printed so the judgement is checkable.
- ⚠ **I did not re-open `CVE-2021-23017`, propose a 27th pattern, or conclude
  "build more"/"stop"** (§F).
- ⚠ **I did not attack `TASK_128`'s §A premise-inversion result** (that
  `TASK_124` measured 2 of 6 columns). I checked it and it holds — `TASK_124`
  §B2 is headed *"Verus. ⚠ NOT SPENT, deliberately."* **That half of finding 44
  is correct and is the reason to keep the finding.**

## TREE STATE

- Wrote only `.temp/t130/**` and this file. `git status` shows `TASK_127`'s
  26 modified tracked files + `TASK_129`'s untracked; **none are mine**.
- `.temp/t130/` is **316 K**; `RUN.sh` regenerates every source, binary and log
  and deletes the binaries. No binary, `.o`, `.pyc` or `.bin` remains.
- `harness/vparse.py` was **copied** out of `HEAD` and the copy was run;
  `count_burden.py` / `kir.py` / `symcmp.py` were **copied** out of
  `.temp/t128/` unedited. Nothing under `harness/` or `.temp/t128/` was written.

## RUNNING COUNT

`594 → 617`. ⚠ **Reconciliation is the manager's job, not mine; `TASK_127` and
`TASK_129` carry their own. I am carrying, not re-adding.** The twenty-three:

1. `obligations` is neither necessary nor sufficient for limb 2 — presence
   `{3,4,5,7}`, absence `{3,5}`, overlapping at both (§A2);
2. at the project's kernel convention `obligations` ranks the DEAD-CODE arm
   ABOVE the mechanism arm, `5 > 4` (§A1);
3. `kE`/`kC` kernels are BYTE-IDENTICAL (199 B `ffd9c4e2186777aa`) while
   `obligations` differs by `+2` (§A1);
4. the engineer's headline is INVERTED: assembly and `Ir` see the mechanism,
   `obligations` does not (§A1, §B);
5. the spelling-spread : presence-gap ratio is **8519 : 1** for `Ir` and
   **1 : 1** for `obligations` — which dissolves the crux (§A3);
6. finding 42's REPLACEMENT sentence is false; the true scope is *no published
   rung-to-rung DIFFERENCE moves* (B2);
7. the engineer's level-vs-difference "structural" argument proves too much —
   `TASK_124`'s own `−63.00 Ir`/call is a level move (§A5);
8. `p23`/`k_u5` is a precedent AGAINST the engineer's defence: `150.00 Ir`/call
   struck from a published figure for exactly this reason (§A4);
9. `p46` §8a is the second: *"per-MAC safety tax is 0.00000"* (§A4);
10. `verified` is a code-size proxy on the built tree — corr `0.894` with
    syntactic units, `0.795` with source lines (§final);
11. `synthesize.py` already documents the column's insensitivity, one screen
    above the table (§final);
12. `TASK_128`'s limb-3 `_calibRANGE_bv` is the SAME non-specificity refutation
    as `_calib2`, filed the same way (§E);
13. ✅ **clean negative** — the census's FLAG premise holds: no flag, libc-entry
    or stack-protector confound, verified in `build.py` and across 25 twins (§C1);
14. the census's SOURCE premise fails for p11/p19/p47 — a libc swap, a whole
    validation pass, an algorithm swap (§C2);
15. those three carry **10 of the 35** above-floor rows and both extremes;
    clean-operator twins only: **25 of 90 rows, 9 of 22 patterns** (§C2);
16. the `±4.6%` floor is p06's **`ns`** floor, quoted verbatim *"for every `ns`
    figure in this file"*, applied to a layout-blind callgrind column (§C3);
17. the measured `Ir` floor on that same axis is **zero** (`kernel_exclusive`
    `3002.00` in all nine runs) (§C3);
18. the honest `Ir` statement is **94 of 100 rows move, 56 above 1%, median
    1.77%** (§C3);
19. *"exhibits a limb"* has no operational definition and the bar's text is a
    NOVELTY test, not a detectability test (§D2);
20. p23 states all three limbs as novelty claims with the built set enumerated,
    and its limb-1 claim is checkably true — the only twin whose guard compares
    two moving cursors — so the clean negative survives on **limb 3 only** (§D2);
21. the TCB clean negative is spelling-dependent — `armPext`, `2 items / 6
    lines` (m8);
22. `p23`'s `obligations 16` is 19th of 26 against a median of 12 (m9);
23. ✅ **clean negative** — an independently written census reproduces
    `100 / 35 / 26 / 25 / 12` exactly, and verification wall time separates
    nothing (§E).

Carry **617** forward, incremented by what the next agent finds.
