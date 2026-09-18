# `.memory-php/03-numbers.md` — what may and may not be compared

> ⚠ **`.memory-php/` is the AUTHORITATIVE layer for the PHP programme, and it
> SUPERSEDES any task report it contradicts** (`.tasks/PROTOCOL.md` rule 9).
> Only findings that have survived a full engineer→reviewer cycle are here.
>
> ⚠⚠ **SCOPE: this carries ONLY what is php-specific.** The PAT `.memory/`
> 00–06 applies unchanged — same harness, same bench rules, same measurement
> discipline, same Verus notes. **Do not restate any of it here; two copies of
> one rule is how both go stale.**
>
> The narrative, the open items and findings **F1–F153** live in `RECAP_PHP.md`
> (⚠ this said *F1–F41* for **forty-nine** findings, then *F1–F90* for **eleven** more — `PROTOCOL.md` rule 13, **and it has now rotted THREE TIMES.** ✅ **`.tasks-php/boxcheck.py` CHECKS THIS LINE against the actual highest finding as of 2026-09-13, so it is the last time.**
> **Count it yourself: `grep -c '^### F' RECAP_PHP.md`.**)
> ⭐ **And the statistic decision — which column every row publishes in — is
> `.tasks-php/STATISTICS_001.md`, committed. It was in gitignored `.temp/`.**

---


- ⚠⚠ **NEVER quote a `phNN` figure against a `pNN` one**, anywhere, including
  in prose. `repo_path_bytes` is **15 B** longer through the shim and
  `gate.py`'s `PYTHONDONTWRITEBYTECODE=1` adds **+34** and one env var.
- ⚠⚠ **And no two php runs are comparable to each other** unless the invoking
  shell matches: `ph00`'s own `envp_stack_bytes` moved **3 686 → 3 695** between
  two runs of the same gate with no source change. **Measure a mechanism; never
  difference two records taken in two shells and call the result its cost.**
- ⚠⚠ **`0 STALE` does NOT mean "everything is pinned".** `measure.py::_compare`
  iterates the **recorded** keys, so an **added** file is invisible — it has no
  key, so it cannot be stale. It means *every source that was pinned still
  matches*. What closes the gap is the **preflight**, not the digest. ⚠ This is
  a `harness/` property and affects all 33 PAT rows identically. (F14.)
- **The allocator is pinned by an UNCONDITIONAL symlink** — every php row
  carries `c/emalloc_shim.h` whether or not it allocates. ⚠ **Do not reintroduce
  a detector**: *"does this row use the allocator?"* was answered twice (a string
  search, then `gcc -MM`) and bypassed twice. **The question is not meant to be
  load-bearing.** (F10, F16.)

---

## Landed 2026-09-13 from `TASK_PHP_043` — which column, and what a figure owes

- ⛔⛔⛔ **READ THIS BEFORE ANY `inside_share` FIGURE BELOW: TWO DIFFERENT
  QUANTITIES WEAR THAT NAME IN THIS PROGRAMME, AND *THIS FILE USES BOTH*.**

  > ⛔⛔⛔ **THIS LINE SAID *"AND EVERY FIGURE IN THIS FILE IS THE FIRST ONE"*.
  > `TASK_PHP_059` MEASURED THAT AND IT IS FALSE — IN THIS FILE.** The `ph52`
  > entry below reads *"**22.24 %** on its **C** rungs … **≈98.6 %** on its
  > **Rust** rungs (`unsafe` A1 48,846,257 against W1 49,549,469)"*, and that
  > parenthesis **spells out the `W` arithmetic**. Under `F74`'s definition the
  > same row reads `0.9892`–`0.9970` and `0.2023`–`0.2269`; neither `0.2224` nor
  > `0.986` appears anywhere in the corpus at ±0.0005.
  >
  > ⭐⭐⭐ **SO THE HAZARD IS WORSE THAN THIS BOX FIRST STATED, NOT SMALLER: the
  > two quantities are not separated between documents — they are INTERLEAVED
  > INSIDE SINGLE SENTENCES, here and in `RECAP_PHP.md`.** ⛔ **A caution box that
  > is wrong about the file it heads is worse than none**, because it tells a
  > reader they may stop checking. ▶ **Check the arithmetic of any figure you are
  > about to quote; the name does not tell you which one it is.**
  >
  > ⭐ **`cbaseline_check.py`'s hand ledger had already written down half of
  > this** — it files the `ph52` line with the note *"the four C cells actually
  > span 20.23–22.69 %"*, which **is** the `F74` span. **The discrepancy was
  > recorded and nobody read it as a definition mismatch.**

  | | definition | needs |
  |---|---|---|
  | ⭐ **`F74`'s — THIS FILE'S** | `(kernel_exclusive_ir / n_iters) / marginal_ir_per_call` | nothing; it is arithmetic over two committed records |
  | **the `W` one** | `kernel exclusive Ir / callgrind whole-run total Ir` | a callgrind run |

  On `ph29`'s `c-gcc`/`small.bin` cell they read **0.8045** and **0.8933**. ⛔ **The
  only control the corpus ships — `patterns-php/ph97-optarg-unwritten/controls/inside_share.py`,
  now byte-identical in four rows — computes the `W` one.** ⚠ **So does every copy
  of it.** ▶ **Say which you mean.**

  ⚠⚠ **THE NEXT SENTENCE IS THE TELL, AND IT IS WHY THIS CAUTION IS HERE**:
  *"already computed for every cell in every record"* is **true of `F74`'s and
  false of the `W` one**, and the file never said which — **`F88`'s own rule,
  *name the denominator*, broken by the quantity `F88`'s neighbours are measured
  in, in the document that states `F88`.**

  > ✅✅ **STATUS: REVIEWED AT `TASK_PHP_059`. The two definitions are UPHELD
  > and UNDER-STATED; the *"every figure here is `F74`'s"* clause is REFUTED
  > (struck above).** ⭐ **The gap between them is a MEASUREMENT, never a
  > constant: 8.9 pp on `ph29`, 0.01 pp on `ph45`** — so a reader shown only
  > `ph29` over-rates the risk on some rows and under-rates it on others.
  >
  > ⭐⭐ **THE STATUS NOTE THAT USED TO SIT HERE EARNED ITS KEEP AND IS KEPT AS A
  > RECORD.** It admitted this box while `F129` was UNREVIEWED, on the ground
  > that it *"changes no figure and asserts no new result — it labels figures
  > already here, all of which stay correct once labelled."* ⛔⛔ **THAT GROUND
  > WAS ITSELF THE REFUTED CLAIM**: the box did not merely label, it asserted a
  > corpus fact about this file, and that assertion was false. ▶ **The lesson is
  > not *"do not admit unreviewed material"* — admitting it was right, and rule 9
  > worked exactly as designed because the marking is what made the reviewer
  > attack it. The lesson is that *"it asserts no new result"* is itself a
  > claim, and nobody checked it.**
  >
  > ⛔ **`F74`'s form exceeds `1.0` on 15 of 360 corpus cells** — ⚠ **13 at `O3`
  > and 2 at `O0`**, all on `ph07` (5) and `ph16` (10). ⭐ **`_059` ran the
  > discriminator: re-basing the denominator on an `n_iters`-scale window removes
  > it on `ph07` (`1.0353` → `0.9569`) and MOST of it on `ph16` (`1.0241` →
  > `1.0021`, still above 1).** ⛔⛔ **The five-window slope series on `ph16` is
  > NON-MONOTONE with the published `[100, 200]` pin the LOWEST of five**, so it
  > is a **draw** effect (`F88` + `F93`), not a scale effect — **the two
  > candidates are the same phenomenon and the named discriminator cannot
  > separate them.** ▶ **Do not quote a bare `F74` share above 1.0** — open item
  > 133, now with a measured answer on one row and a measured *non*-answer on the
  > other.

- ⭐⭐⭐ **WHICH STATISTIC RESOLVES A CODE DIFFERENCE IS DECIDED BY
  `inside_share`, AND IT IS ALREADY COMPUTED FOR EVERY CELL IN EVERY RECORD.**
  **Family A resolves a difference exactly to the extent the difference lands
  INSIDE THE KERNEL SYMBOL.** ▶ **So compute `inside_share` BEFORE choosing the
  column, not after the search disagrees**: `ph45` at **9.5 %** published in
  **W1**, `ph53` at **89.5 %** published in **A1**, and both were right.
  ⛔ **Two earlier candidate axes are REFUTED**: *same-language vs
  cross-language* (all nine of its own cells are same-language and separate by
  `|Δ|`) and *does the callee work diverge* (**a sign flip ENTAILS callee
  divergence, so the variable does not vary**). **Details and scope —
  two rows, nine cells — in `02-ladder.md`.** (F91 narrowed, item 78 answered.)
  ⭐⭐ **AND THE SHARPEST EVIDENCE FOR *"the DIFFERENCE, not the share"* ARRIVED
  ON ROW 9: `ph55`'s C cells sit at `inside_share` 74–83 % — the corpus's FIRST
  HIGH-SHARE CELLS WHERE A1 STILL READS `0.000 %`.** Both C kernels compile to a
  **byte-identical `kernel` symbol** under both compilers (`asm.py` `exact`) and
  **one of the two binaries SEGVs**, because the defect lives in an uninlinable
  callee. ⛔ **So a high `inside_share` is NOT a certificate.** ⓘ **This is an
  INSTANCE of the rule above, not a new rule** — `TASK_PHP_050` §4.1 refuted
  landing it as one, on the ground that the layer already said it and a second
  statement of one rule is how the weaker gets cited. (F109, narrowed.)

- ⚠⚠⚠ **A ROW'S SPREAD OVER RESPELLINGS IS A FACT ABOUT THAT ROW'S VARIANTS, NOT
  ABOUT THE STATISTIC.** `ph45`'s A1 spread over nine searched variants is
  **`0.000000` pp** against 66.7/44.5 pp whole-program; **`ph53`'s is `39.9`/`45.3`
  pp over 20.** ▶ **Same statistic, opposite answers, and the difference is
  `inside_share`** — every lever `ph45`'s search found lives in the callee `dec`.
  ⓘ **`ph45`'s `0.000000` is an instance of F86's `BLIND` class** (*A is exactly
  `0` while the whole-program figure is not*, 14 of 366), **which the programme
  already had a name for.** ⛔ **Do not quote either row's spread as evidence
  about family A.** (F100, item 82.)

- ⛔⛔ **EVERY PERCENTAGE OWES FOUR THINGS AND A PUBLISHED FINDING SHIPPED
  WITHOUT ANY OF THEM: THE STATISTIC, THE INPUT, THE OPT/MODE LEVEL, AND THE
  BASE IT IS AGAINST.** F98's *"the shipped R4/R5 carry a coverage witness the C
  rung does not have, and it costs `+21.8 %`"* is **W1**, on **`small.bin`**, at
  **`O3/isolated`**, **against `controls/r4_nowitness.rs` — a RUST control, NOT
  against the C** — and **only ~44 % of it is the witness** (`+101.59` of
  `+228.87` `Ir`/call; the rest is the array being in memory at all).
  ⭐ **The headline invited an R1-vs-R4 reading it could not support, and the
  attribution of a whole difference to one named cause is F83's shape.**
  (F98 narrowed.)

- ⚠ **NAME THE DENOMINATOR.** `ph29`'s family-B draw spread is **`range / mean`**
  — `31.42 %` on an independent 8-span sweep. **A second normalisation, `38.6 %`,
  is also in circulation and neither document said which it used.** (F88 upheld,
  item 92.)

- ⚠⚠ **`probe_iters` CANNOT BE WIDENED OUT OF THE PROBLEM, AND *"HOPELESS"* IS
  TARGET-DEPENDENT.** The width→spread exponent is **≈ −0.5** on both rows, so a
  *relative* target needs an unreachable width — ⚠ **but for an ABSOLUTE 1-pp
  target the probe's own TABLE 7 gives `W ≤ 574` on every pair.** ▶ **The `NO`
  on open item 68 stands anyway, and for a better reason: the lever cannot fix a
  BIAS at any width** — F93's start-of-run transient and F91's bias. ⭐ **And the
  F52 control is what makes the exponent believable: it recovers `−0.5047` from
  i.i.d. noise and `−0.9799` from endpoint noise, so the experiment does
  distinguish *a weak lever* from *measuring its own null*.** (F92 narrowed.)


> ✅✅ **CYCLE CLOSED 2026-09-13 BY `TASK_PHP_047`. THE MATERIAL BELOW IS NOW
> REVIEWED** — F97/F102/F104 **UPHELD-NARROWED**, F106 **UPHELD and under-stated**,
> F105 **REFUTED in its `97.6 %` clause** (repaired in `02-ladder.md`, not here),
> F103's decomposition **REFUTED** (it was never in this layer), F96 **still
> UNREVIEWED**. ⭐⭐ **Law 12 held: not one of the five survived unchanged.**
> ⚠ **The banner below is kept because the defect it records was the manager's.**
>
> ⛔⛔⛔ **EVERYTHING FROM HERE TO THE END OF THIS FILE WAS `UNREVIEWED`, MANAGER, 2026-09-13.**
> It comes from `TASK_PHP_044`, `_045` and `_046`, which are **ENGINEER** tasks:
> `PROTOCOL.md` **rule 9** requires an engineer→reviewer cycle and **these have had
> only the engineer half.** ⭐ It is kept here rather than held back, under the same
> convention `02-ladder.md`'s family-B sensitivity paragraph used — **marked, not
> hidden** — because a later session needs the rule and the mark tells it what the
> rule is worth.
>
> ⚠⚠ **AND THE MARK IS HERE BECAUSE I LANDED THIS MATERIAL UNMARKED FIRST.** I
> wrote the RULE-9 STATE block one day earlier, landed `04-process.md` law 12
> (*a manager finding from one probe or two rows should be assumed narrowable until
> a reviewer has had it*) — **and then put seven unreviewed entries into the layer
> that supersedes everything.** ▶ **Caught by auditing before a handoff, which is
> the only reason it is marked at all.** → the RULE-9 STATE block in `RECAP_PHP.md`
> names which findings these are and what a review round owes.

- ⚠⚠ **A IS REPRODUCIBLE AND THE WHOLE-PROGRAM COLUMN IS NOT — SO *"QUOTE BOTH,
  LABELLED"* HAS A REPRODUCIBILITY REASON BESIDE ITS RESOLUTION REASON.** Over
  **four** regenerations of one row's sidecar, **every A1 figure was
  bit-identical** while the whole-program column moved by a constant
  **±14–28 Ir** — the per-call stack-alignment bistability
  `check.py::check_marginal_ir` names, almost certainly the argv/env block, i.e.
  **the path length of whatever invoked the gate.** ▶ **Do not quote a
  whole-program figure to more than 2 dp**, and note that a row publishing **only**
  the whole-program column publishes the unstable one. ⚠ **UNEXPLAINED — the
  cause was not isolated.** (Item 99, `TASK_PHP_044` §8.2.)

- ⭐⭐⭐ **`inside_share` IS PER-**CELL**, NOT PER-**ROW**, AND ONE ROW CAN NEED
  DIFFERENT COLUMNS FOR DIFFERENT COMPARISONS.** `ph52` measures **22.24 %** on its
  **C** rungs — `PH52_NOINLINE` puts three callees in their own symbols, 62.35 % of
  the program — and **≈98.6 %** on its **Rust** rungs, which inline everything
  (`unsafe` A1 `48,846,257` against W1 `49,549,469`). ▶ **So the row publishes its
  **R1-vs-R1h** column in **W1**, correctly, while a **respelling search of its Rust
  rungs** lands in the 98.6 % region where **A1** is the resolving statistic.**
  ⚠⚠ **The rule above is right as written — *to the extent the difference lands
  inside the kernel symbol* — but `ph45` (9.5 %), `ph53` (89.5 %) and `ph52` were all
  first discussed as ONE number per row, and that is the reading to drop.**
  ▶ **Compute `inside_share` for the CELLS the comparison actually spans, then
  choose.** ⓘ And note *why* `ph52`'s C figure is low: the same three-TU boundary
  that makes the defect reproducible at all — **`inside_share` is not independent of
  the extraction's fidelity choices**, so it is a measurement and never a constant.
  (`TASK_PHP_045` §4 + §6.2, manager-verified from `results-php/ph52-…json`.)

---

## Landed 2026-09-13 from `TASK_PHP_049` — **the fourth thing a cross-language figure owes**

- ⛔⛔⛔ **A CROSS-LANGUAGE FIGURE MUST NAME **WHICH C COMPILER**, AND SHOULD CARRY
  **BOTH** C COLUMNS — AND THIS RULE ALREADY EXISTED IN THE PAT LAYER SINCE
  `TASK_001`. `.memory-php/` NEVER INHERITED IT, AND THAT OMISSION PUT TWO
  SIGN-CHANGING CLAIMS INTO THE AUTHORITATIVE LAYER.**

  > `.memory/02-bench-rules.md`, **"Honesty rules"**:
  > *"Never report a C-vs-Rust number **without saying which C compiler**, and
  > whether a same-backend (clang) column exists."* · *"**Never report a perf
  > number from an `O0` row.**"*
  >
  > `.memory/01-ladder.md:2534, :2572`: clang *"is the same-backend baseline and
  > is **mandatory for any C-vs-Rust claim**; gcc is the *'what a distro ships'*
  > baseline."* · *"**Always report a clang column.** A gcc-only C baseline
  > overstates C's dynamic cost here by **43 %**."*

  ▶ ⭐ **SO THE FOUR THINGS EVERY PERCENTAGE OWES BECOME FIVE: the STATISTIC ·
  the INPUT · the OPT/MODE level · the BASE it is against · and IF THAT BASE IS A
  C CELL, WHICH COMPILER — with both columns, or an explicit statement that only
  one was measured.** ⛔ **One column is not a number with error bars on it; it
  is a DIFFERENT SIGN.**

  ⚠⚠ **AND *"quote a rung against a rung, never against 'C'"* — `ph03`'s own
  row-1 note 4 — IS INSUFFICIENT AND SHOULD BE RETIRED IN FAVOUR OF THE PAT
  WORDING, NOT KEPT BESIDE IT.** It constrains the **Rust** side, which was never
  the ambiguous one, and is satisfied by *"C vs `safe_naive`"* because *"C"* reads
  as a rung name. **Two rules of different strength on one question is how the
  weaker one gets cited.**

  ⭐⭐ **THE MEASURED SCALE, so nobody treats this as pedantry:** across 8 php
  rows, A1, `small.bin`, `O3/isolated`, clang against gcc on **identical
  extracted C**, the gap runs **−1.86 % to −29.96 %**. **10 of 128 A1
  cross-language cell-pairs change SIGN under the swap** — **15.6 % at
  `O3/isolated`, 0 % at `O0`** — across four of eight rows. ⓘ The PAT pilot
  measured the same effect at **+42.9 %** in the other direction, so this is a
  **rediscovery**, not a discovery.

  ⛔⛔ **AND IT CUTS THE OTHER WAY TOO, WHICH IS WHY IT IS A LABELLING RULE AND
  NOT A PREFERENCE FOR CLANG:** splitting F85's **29 cross-language sign flips**
  by baseline gives **21 `c-clang` against 8 `c-gcc`** — and above a 1-pp floor on
  both columns, **17 clang to 0 gcc**; **20 of the 28 family-C survivors are
  clang-baseline.** ▶ **So the A-vs-whole-program disagreement is, if anything, a
  `clang` property.** (F108; item 111 **UPHELD-NARROWED, headline REFUTED**.)

- ⚠⚠ **AND `TASK_PHP_049` SETTLED THE ATTRIBUTION CONFOUND ON THE ONE ROW THAT
  HAD THE EVIDENCE, WITHOUT BUILDING FAMILY C.** The objection was that A1 is
  symbol-scoped, so differing inlining could move work across the `kernel`
  boundary without changing the work done. ⛔ **Refuted on `ph29`: the gcc→clang
  gap is `−28.09 %` (A1), `−27.01 %` (family C), `−26.74 %` (W1)** — **W1 is
  immune to symbol boundaries and still sees it**, which also **refutes the
  cold-helper alternative** (a compiler inlining a cold helper while keeping a hot
  one as a call). ⚠⚠ **The other SEVEN rows have no C-cell profiles and are
  UNTESTED.** ▶ **New requirement on item 62: family C must be built for BOTH C
  cells per row**, or it re-adjudicates 8 flips and leaves 20 untouched.

---

## Landed 2026-09-14 from `TASK_PHP_050` — **when a family-B figure may be published**

- ⛔⛔⛔ **A FAMILY-B DIFFERENCE MAY BE PUBLISHED IFF THE TWO CELLS IT SPANS HAVE
  A MEASURED STEP OF `0.00 Ir/call` OVER A FULL 32-RESIDUE `argv` PAD SWEEP, OR
  THE DIFFERENCE EXCEEDS THAT STEP BY THE SWEEP'S STABLE RATIO.** The lever is
  the **stack alignment of the probe argv**, it is **bistable with period 32 and
  window 16**, and it **survives into family B by construction** because every
  family-B figure is a difference of two cells from one record.
  ⓘ Sweep: `.tasks-php/php50_align_sweep.py`, **no build, no gate, no
  re-measure** — minutes per row on already-built binaries.

  ⛔ **A MAGNITUDE FLOOR WAS CONSIDERED AND IS REFUTED BY MEASUREMENT, NOT
  DECLINED ON TASTE.** A floor would have to be ≥ `7 Ir/call` to protect `ph55`'s
  clang cells (`14` to protect their *difference*) — **but `ph53/small.bin`
  publishes `c-gcc → c-gcc-h` at `+2.80 Ir/call` with a measured range of `0.00`
  and it is perfectly sound**, so the floor would refuse a good figure.
  ⭐⭐ **AND THE STEP IS NOT A CONSTANT: measured corpus-wide ON THE `argv[1]`
  AXIS it takes FOUR distinct values — `0.00`, `0.02`, `7.00` and `34.49` — and
  the largest is NOT a multiple of the `7 Ir` constant.** ⚠⚠ **NAME THE AXIS:
  `34.49` is an `argv[1]` value and the SAME CELL reads `20.08` on `argv[0]` and
  `0.00` on `envp`** (`TASK_PHP_053` §1.4). **The sentence is true only with the
  axis in it.** ▶ **A constant floor is too strict and too
  loose at once, which is why the rule is a sweep and not a number.**
  ⭐ **And a floor sees MAGNITUDE where only a sweep sees PHASE**: `ph45`'s
  `unsafe → verus` is `+106.25` — above any floor anyone would set — yet carries
  a `14.00` range because its two cells have **different phases**.

  ✅ **STATE OF THE CORPUS WHEN THE RULE LANDED: `4` of `180` family-B
  differences flagged, on `ph55` and `ph07` only, and NO PUBLISHED FAMILY-B
  NUMBER IS WRONG** — the one row that both publishes family B and owns an
  exposed cell is `ph55`, which already refuses to quote it.
  ⓘ **Scope: all ten rows, both inputs, `-O3 isolated`, `probe_iters [100, 200]`,
  5 120 callgrind runs. Says nothing about `-O0` or `whole`.**

  ⛔⛔ **MEASURED `TASK_PHP_053` §1, AND THE VERDICTS STAND WHILE THE GROUND
  THEY WERE GIVEN IS REFUTED — SO READ THE GROUND, NOT THE OLD STORY.**
  The rule was defended here as *"`argv` and `envp` are the same knob"*.
  **They are not.** `ph07`'s `verus` cell steps **`34.49` under `argv[1]`,
  `20.08` under `argv[0]` and `0.00` under `envp`** (flat over **96** consecutive
  bytes), with a dead instrument, the added variable, a longer period and the
  *"the program reads `argv[1]`"* reading all ruled out. ▶ ⭐⭐ **THE STEP IS A
  PROPERTY OF THE `(cell, axis)` PAIR, NOT OF A CELL.** The mechanism is
  **unexplained and the reviewer said so.**
  ⚠⚠⚠ **SCOPE, AND QUOTE IT WITH THE CLAIM: ONE ROW DISAGREES AND THREE AGREE.**
  `ph55`'s clang cells agree; **`ph45`'s four Rust cells agree TO THE DIGIT on
  every median, range and verdict string**; the 12 clean cells read `0.00` on
  every axis. ⭐ **The refutation stands because ONE counterexample breaks an
  `iff` and this rule is an `iff`** — **not because the axes generally differ.**

  ✅ **WHAT SURVIVES, AND IT SURVIVES BY MEASUREMENT RATHER THAN BY ARGUMENT:
  12 `0.00`-`argv` cells were swept on `envp` AND on `argv[0]` — 24 cell-sweeps,
  NO COUNTEREXAMPLE — so `ph64`'s clearance is CONFIRMED ON THREE AXES**, and the
  magnitude-floor refutation gets *stronger*, because the `34.49` outlier that
  broke the floor is **axis-specific** as well as non-constant.

  ⚠⚠ **SO AN `argv[1]` SWEEP READING `0.00` IS A *NECESSARY* CONDITION,
  CORROBORATED ON 12 CELLS AND 2 FURTHER AXES, AND NOT A PROVED *SUFFICIENT*
  ONE.** ⭐⭐ **And the right way to say that is one this project has already
  written, about this exact quantity**: `harness/check.py::_env_block`'s caution
  that **three equal fields mean *this record cannot tell the two draws apart*,
  not *the two draws are the same*.** ▶ **§B5 did not inherit it. It does now.**

- ⚠⚠ **REPORT TWO VERDICTS PER PAIR, NEVER ONE — *magnitude resolvable?* and
  *sign stable?*** A single verdict throws away a usable result to avoid quoting
  an unusable one: one `ph55` pair is `+216 k` or `+76 k` Ir depending which side
  of the step it lands on, **both positive**, so the magnitude is unquotable and
  the sign is sound. (`ph55/controls/argv_align.py`, cloned in the sweep.)

- ⛔ **NEVER PUBLISH A FAMILY-B FIGURE FOR AN `unsafe → verus` (R4/R5) PAIR ON A
  ROW WHOSE KERNEL ALLOCATES.** `ph64`'s B1 for that pair is **`+193.36` on
  `small` and `−28.77` on `large`** while A1 is **`−0.510` on both** — **B
  disagrees with A in SIGN and FLIPS between inputs.** `check.py`'s own operative
  rule already says it (*"for a cross-RUNG comparison use `kernel_exclusive_ir`"*).
  ✅ Nothing shipped violates this; it is a guard-rail for the next row.

- ⚠⚠ **A FAMILY-B COMPARISON *ACROSS ROWS* IS OUT OF THE RECORDS' OWN STATED
  DOMAIN.** `marginal_ir_env.domain` says *"comparable ONLY against a record with
  the same `envp_stack_bytes`"* — and that field takes **four distinct values
  across the ten records (`3685`, `3695`, `3697`, `3698`), spanning 13 bytes
  inside a 16-wide window.** ✅ **No published figure is affected** (every one is
  a difference of two cells from ONE record, exactly the case the domain permits)
  — **this is a constraint on a comparison nobody has made yet, recorded before
  someone makes it.** ⭐ `ph55`, the one alignment-exposed C row, is the outlier.
