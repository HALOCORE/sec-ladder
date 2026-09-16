# `TASK_PHP_061_REPORT` — the ninth review round, all eight findings

**Role:** research reviewer / analyst. One agent, alone.
**Read at / run at:** `e9c5c4d` (working tree clean at start; I committed nothing
and added nothing to the index).
**Scope reached:** §1 → §2 → §3 → §4 → §5, **all five**, in the binding order.
⚠ **What that does NOT mean is full coverage** — `§ WHAT I DID NOT DO` is
explicit and long, and every section names the attack I did not run.

---

## §0 THE BACKLOG, DERIVED, NOT TRUSTED

`boxcheck.rule9_rows` over `RECAP_PHP.md` at `e9c5c4d`, **members printed**:

```
RULE-9 rows          33    33 distinct, 8 open cycle(s):
                     F131 F132 F133 F137 F136 F135 F138 F134
```

**33 keys, 33 distinct, ZERO duplicates.** So:

- the backlog is **8**, and it is exactly the eight the brief sections;
- ⭐ **`F131`'s repair HELD, and that is this round's own live check** — §5.1
  says *"if the repair failed, this round is mis-scoped"*. It did not fail, and
  the round is correctly scoped. **This is the cheapest verdict in the round and
  it had to be taken first.**

⭐ **I printed the members before I counted them.** That is `F132`/`F138`'s rule
applied to this report, and it is the reason §5.0a below can say what it says.

---

## §1 `F137` — ⚠ **CONCLUSION SPLIT THREE WAYS. CLAUSE 1 UPHELD · CLAUSE 2 REFUTED · CLAUSE 3 REFUTED-AS-WRITTEN, UPHELD-ON-NEW-GROUND**

### 1.0 The headline, in one line

> ⛔⛔⛔ **`F137`'s GENERALISATION IS REFUTED BY THE ROW IT NAMED AS ITS OWN
> FALSIFIER. ON `ph97` THE C RUNG FAULTS IN ALL EIGHT BUILDS — BOTH COMPILERS,
> `-O0` THROUGH `-O3` — SO *"C's DETECTION IS BUILD-DEPENDENT AND FAILS THE SAME
> WAY"* DOES NOT REPRODUCE ONE ROW OVER.**

### 1.1 CLAUSE 1 — the row measurement. ✅ **UPHELD. CONCLUSION AND REASON BOTH.**

**Second method, and it is not a re-run of the manager's tool:** the two 4-column
tables come from `patterns-php/ph96-outparam-unwritten/controls/widened_domain.py`
and `controls/rust_bug.py`. I did not re-run either. Instead I read
**`results-php/gate/ph96-outparam-unwritten.json`**, which is produced by
`harness/check.py`'s `adversarial` stage — a different producer, written before
either control existed. It carries:

```
adversarial-unset.bin/c-gcc    -> [ exit -11, cells [O0/isolated, O0/whole, O3/isolated, O3/whole], diverges true ]
adversarial-unset.bin/c-clang  -> [ exit -11, cells [O0/isolated, O0/whole],                        diverges true ],
                                  [ exit   0, cells [O3/isolated, O3/whole],
                                    stdout "18121308747923605504", model "15642763268152511488", diverges true ]
```

⭐⭐ **The gate record SPLITS `c-clang` INTO TWO ENTRIES, and it splits it for
exactly the reason `F137` gives.** The silent wrong answer, its value, and the
value it should have had were all in a committed gate record before `F137` was
written. **Clause 1 is not just reproducible — it was already double-sourced.**

### 1.2 CLAUSE 2 — *"a property of the C-vs-Rust ladder, not of `ph96`"*. ⛔⛔⛔ **REFUTED. MEASURED.**

⭐ **I ran the C half of the finding's own named falsifier**, which nobody had:
`.temp/php61/ph97_c_optsweep.py`, built to the **same construction** as `ph96`'s
(`-std=c99 <OPT> -DSLB_ISOLATED`, `common/driver.c` + `<row>/c/kernel.c` +
`<row>/c/main.c`, system `gcc` and `~/tools/llvm/bin/clang`, `si_addr` via
`.tasks-php/probes/segaddr.c` under `LD_PRELOAD`), on **both** candidate inputs.
Run at `e9c5c4d`; the generator is committed at that path and the JSON beside it.

**`ph97`, `adversarial-absent.bin` — the real null-sentinel input:**

| compiler | `-O0` | `-O1` | `-O2` | `-O3` |
|---|---|---|---|---|
| **gcc** | SIGSEGV `(nil)` | SIGSEGV `(nil)` | SIGSEGV `(nil)` | SIGSEGV `(nil)` |
| **clang** | SIGSEGV `(nil)` | SIGSEGV `(nil)` | SIGSEGV **`0x1`** | SIGSEGV **`0x1`** |

**`ph97`, `adversarial-nullvalue.bin` — the file `F137`'s falsifier names:**
**eight builds, eight clean runs, the R1h answer every time.** ⛔ A reviewer who
picked by name would have swept a clean input, found nothing at any `-O`, and
reported `F137` **refuted for the wrong reason**. §0.1's correction is confirmed
in full and was load-bearing; I say so because the brief asked me to rule on it.

**What this settles, item by item against the manager's three registered doubts:**

- **(a) "the built cell may not be `-O3`."** ⛔ **It is `-O3`, and not from a
  `pin` note.** `harness/build.py:129` is `f.append("-O0" if opt in ("O0","O0d")
  else "-O3")`, and `widened_domain.py:79/97` runs `{cell}-O3-isolated`.
  **Independently:** my own `-O3` builds reproduce the committed record's cell
  exactly — rc 139 both compilers, `si_addr=(nil)` under gcc and **`0x1`** under
  clang, which are the two values `widened_domain.json` records. Two methods agree.
- **(b) "the defect shape may differ."** ⚠ **It does not differ in the way that
  would make the comparison meaningless.** Both rows are `cwe: CWE-476`, both
  declare `invariant: I12` (`ph96` `obligation O1`, `ph97` `O3`), both are a NULL
  sentinel left by a callee/arg-parser and then dereferenced. Read from the two
  hashed `slb-contract` blocks. **The comparison is admissible.**
- **(c) "faults at `-O3` does not establish faults at every `-O`."** ✅ **Correct,
  and that is why I swept all four.** It faults at every one.

⭐⭐⭐ **AND THE STRUCTURAL DISCRIMINATOR, WHICH IS THE PART WORTH KEEPING.** The
optimiser *does* transform `ph97` at the same threshold: clang's `si_addr` moves
`(nil) → 0x1` at exactly `-O2`, the level at which `ph96` goes silent. So the
`-O2` clang boundary is real on both rows; **what differs is the consequence, and
the reason is where the faulting load sits in the dataflow**:

- **`ph96`** — the sentinel feeds `if (!retval)` / `retval->refcount--`
  (`c/kernel.c:283`, `:290`). The dereference licenses *"`retval` is non-NULL"*,
  which lets clang fold a **branch**, and a folded branch produces an answer.
- **`ph97`** — the sentinel is passed straight into `ph97_strcasecmp(ph97_sels[0],
  typ)` (`c/kernel.c:344`), a byte loop whose **result is the answer**. There is
  no branch to fold away; the load is load-bearing, so the optimiser can only
  reorder it — which is precisely what moving `si_addr` from `0` to `1` looks like.

▶ **THE NARROWED CLAIM I WOULD LET `F137` KEEP, and it is the brief's option (b):**

> *An optimiser can convert a **detected** fault into a **silent wrong answer**,
> and whether it does is compiler-, level- and **row**-dependent. It happens when
> the UB licenses folding a branch whose outcome is the answer; it does not happen
> when the faulting load's value IS the answer.*

⭐ That is **weaker as a headline and stronger as a rule**, exactly as §1.2
predicted — because it applies to every C row the programme will ever build and
it makes a falsifiable prediction about which ones.

**And the third outcome the finding's binary has no room for is real**, but it is
on the Rust side and it is in `ph97`'s committed `controls/rust_bug.json`:
`opt_sweep_unchecked` = `O0` rc **−6**, then **`TIMEOUT`** at `O1`, `O2`, `O3`.
Not detected, not silent — **hung**.

### 1.3 ⛔⛔ THE BRIEF'S OWN §1.1 IS WRONG ABOUT THE TWO SWEEPS, AND IT IS `F134`'s CLASS A THIRD TIME

§1.1 says: *"AND THE TWO SWEEPS ARE NOT THE SAME CONSTRUCTION … on `ph97` the
swept `unchecked` variant's own `why` says it is `unsafe.rs`, 'the one that
reproduces C'."*

⛔ **They ARE the same construction.** `ph97`'s `controls/rust_bug.py:115` is
`src = src.replace(GUARDED, UNGUARDED, 1)` over `unsafe.rs`, with
`GUARDED = "if typ.is_none() || strcasecmp(...) == 0 {"` and `UNGUARDED` the same
line minus the disjunct — i.e. **a guard-deleted mutant of the shipped rung**,
which is what `ph96`'s `rust_bug.py:67` (`src.replace(GUARD, NO_GUARD, 1)`) also
builds. The module header says so in terms: *"Both are built from the SHIPPED
rungs by deleting exactly `f7326d627962`'s disjunct."*

⭐⭐ **The `source: "unsafe.rs"` field in the JSON names the BASE, not the
program** — and the same JSON proves it, because
`shipped_unsafe_on_adversarial` answers `1265852909175663616` on the very input
the `unchecked` variant **times out** on. A field and a body, and the brief read
the field.

▶ **So the brief's §1.1, written to warn a reviewer against reading a LABEL
instead of a BODY, does it itself, in the same sentence.** That is the third
level of `F134`'s class inside one round: the finding, the brief's correction of
the finding, and the brief's correction of its own correction. I agree with §1.1
that this is *evidence about the programme, not about `ph97`* — and it is now
stronger evidence than §1.1 knew.

⚠ **What survives of §1.1's point, and it is a real narrowing of `F137`:** the
two *tables* in `F137` are still not parallel. The **C** table's build-dependent
rung is the **shipped R1**; the **Rust** table's build-dependent rung is a
**mutant that is no rung of the ladder** — the shipped `unsafe.rs` answers
correctly at all four levels on both rows. So *"unsafe Rust buys back C's
performance and C's failure mode with it"* is a claim about a **hypothetical**
R4 that spells the defect, not about either row's R4 as built. `F137` does not
say which is which, and it must.

### 1.4 CLAUSE 3 — *"a currency the ladder's cost columns cannot express at all"*. ⛔ **REFUTED AS WRITTEN. UPHELD ON NEW GROUND.**

The brief offered three readings and asked which. **None of the three is right,
and the fourth is better than all of them.**

| reading | verdict |
|---|---|
| *"the **COST** columns cannot express it"* | trivially true, uninteresting — as §1.3 of the brief says |
| *"the ladder has no column for it"* | ⛔ **FALSE.** `results-php/gate/*.json`'s `adversarial` block is keyed `(input, cell)` and carries `exit`, `stdout`, `signal`, `model_stdout`, `diverges` |
| *"…no column for it ACROSS OPTIMISATION LEVELS"* | ⛔ **FALSE, and this is the one I expected to hold.** Each `adversarial` entry carries a `cells` list, and `ph96`'s `c-clang` entry is **split into two entries** — `[O0/isolated, O0/whole]` and `[O3/isolated, O3/whole]` — *because the outcomes differ by optimisation level.* The datum exists at exactly the granularity `F137` says is missing |

▶ **THE FOURTH READING, WHICH IS WHAT I WOULD LET IT SAY:**

> *The gate **records** detection per `(input, cell, opt-group)` and **publishes
> nothing from it**, at **two** optimisation levels out of four, and **no stage
> acts on it**.*

Three measured limbs, each checkable:

1. **Recorded.** Above.
2. **Published nowhere.** `results-php/tables/ph96-outparam-unwritten.md` has
   `## Toolchain`, `## Inputs`, `## Declared idiom`, `### Spelling audit`,
   `## What the gate said out loud`, `## Static + executed instructions`,
   `## Structural identity`, `## Wall clock`, `## Cells and metrics not measured`.
   **There is no detection column.** The only categorical per-input field is
   `san=fires` / `sentinel=True`, which is a **declaration** copied from
   `spec.md`, not a measured per-cell outcome.
3. **Acted on by nothing.** `ph96` gated `PASS` with `failures: []` while its own
   `adversarial` block carries `diverges: true` on a C cell that exits 0 with a
   wrong checksum. That is **by design** — `harness/check.py:8478-8487` states it:
   *"On an adversarial input the C rung diverging from the model IS the result …
   `check_adversarial` exists to record rather than require it."*
4. **Only two of four levels.** `harness/build.py:67` is `OPTS = ["O0", "O3"]`.
   ⛔ **`ph96`'s silencing happens at `-O2`, and `-O2` is not a cell.** The gate
   caught the *edge* of this transition only because `-O3` is on the far side of it.

⭐ **That fourth reading is more useful than "cannot express" because it is
actionable**: it names a column that could be published from data already on
disk, and it names the two levels that are missing.

### 1.5 The two cheap clauses

**(a) The `F3` half** — *"a reviewer who tested only `c-clang -O3` would have
concluded the defect was not reachable."*
⚠ **UPHELD ABOUT A REVIEWER · REFUTED ABOUT THIS GATE · and the sharper claim is
a third thing.**

- **True of the cell in isolation:** the gate record shows `c-clang` at
  `O3/isolated` exiting 0 with `18121308747923605504` — a plausible checksum, no
  signal, no diagnostic.
- ⛔ **Rhetoric with respect to the gate.** The row could **not** have gated PASS
  on a clean clang run: `harness/check.py`'s `sanitizer` stage runs
  `adversarial-unset.bin` with `expect: "fires"`, `fired: true`, diagnostic
  *"runtime error: member access within null pointer of type 'struct ph96_zval'"*.
  Had it not fired, the `elif rc != m_exit` / declared-`fires` arm would have
  failed the row. A second stage also sees it: `c-gcc` SIGSEGVs.
- ⭐⭐ **BUT THE STAGE THAT CATCHES IT IS `gcc`-ONLY AND `-O1`-ONLY.**
  `harness/check.py:8303-8312`: `[buildmod.GCC, "-std=c99", …, "-O1", "-g",
  "-fsanitize=address,undefined", …]`, and its docstring says *"This stage is
  gcc-only, as it always was."* ▶ **So a defect silenced by `gcc` at `-O2`+ would
  be invisible to every stage of the gate.** That is the version of the clause
  that is worth publishing, it is checkable, and `F137` does not make it.

**(b) *"clang miscompiles"* — does the text slip?** ⚠ **YES, ONCE, and I can name
the sentence.** `RECAP_PHP.md:2002-2005`:

> *"…the sentinel path returns `18121308747923605504` **where the correct answer
> is** `15642763268152511488`. No crash, no diagnostic, **a wrong checksum**."*

On a program with UB there is no *correct answer* to be wrong about; the value
being called correct is the model's/R1h's. Quoted alone, that sentence reads as
*clang produced a wrong result*. ⭐ **The finding's own control has the right
wording and the finding did not copy it** — `widened_domain.py:202` labels the
cell `"SILENT WRONG ANSWER -- UB exploited, not lowered"`. ▶ **Re-state the
sentence in the control's words.** Everything else in `F137` is about detection.

### 1.6 What may enter `.memory-php/`, and what may not

| | |
|---|---|
| ✅ **MAY ENTER** | the **narrowed** rule in §1.2 (*an optimiser can convert a detected fault into a silent one; it happens when the UB licenses folding a branch whose outcome is the answer*) — **with `ph97` as the negative instance in the same sentence**, because a rule published from `ph96` alone is the rule this round refuted |
| ✅ **MAY ENTER** | §1.5(a)'s measured gap: **the gate's only UB detector is `gcc`-only at `-O1`, and `OPTS = ["O0","O3"]` skips the level where `ph96` flips** |
| ⛔ **MAY NOT ENTER** | *"detection-survives-the-optimiser is a NEW AXIS"* — one row, and the one row tested against it says no |
| ⛔ **MAY NOT ENTER** | *"the ladder's cost columns cannot express it"* at any of the three widths the brief offered. The fourth reading in §1.4 may, and it is a different claim |
| ⛔ **MAY NOT ENTER** | *"unsafe Rust buys back C's failure mode"* without the words **"a guard-deleted mutant of"** in front of `unsafe.rs` |

---

## §2 `F136` — ✅ **CONCLUSION UPHELD AS MEASURED · ⛔ HEADLINE REFUTED · ⭐⭐ MECHANISM UPHELD AND UNDER-STATED**

### 2.1 The cheapest attack, run first: did the control build two binaries? ✅ **YES. THREE WAYS.**

1. **Construction.** `controls/repair_price.py:148-155` builds four executables in
   four directories `v00..v03`, from **two different sources**:
   `guard=False` → `c/kernel_hardened.c` **verbatim**; `guard=True` → `c/kernel.c`
   with `VULN_SITE` replaced by `GUARD_SITE`, written to a fresh `kernel_guard.c`.
   The **same `exes` dict** feeds both the callgrind runs (`:160-170`) and the
   identity comparison (`:218-220`), so there is no path on which one binary is
   measured and two are compared.
2. **`md5_fn_equal: false` under `c-gcc`.** The two `kernel` symbols differ **in
   bytes** while agreeing in counts (207/198/705 both ways). ⭐ **A single-binary
   bug cannot produce a false md5 equality.** This is the decisive one.
3. **The two sources differ only at the site.** `diff c/kernel.c
   c/kernel_hardened.c` is a comment block plus three lines at `:509/:512/:513`.

▶ **`F136` exists.**

### 2.2 ⛔⛔⛔ BUT ITS HEADLINE IS REFUTED, AND BY ITS OWN STATED MECHANISM

`F136`'s mechanism sentence ends *"**and inlining erases even that**."* That is a
**forward prediction**: at `-O0`, where nothing is inlined, the two spellings
should not be the same program. **I ran it.**
`.temp/php61/ph96_price_at_O0.py` — the same construction as the committed
control (it **imports** `VULN_SITE`, `GUARD_SITE`, `CALLS` and `_cg` from it, so
a divergence cannot come from my retyping), with `-O3` changed to `-O0`.

⭐ **All five of `F108`'s things, both C columns, for every figure below:**
STATISTIC as named · INPUT `small.bin` and `large.bin` · OPT/MODE `O0/isolated`
and `O3/isolated` (`-DSLB_ISOLATED`) · BASE `noout` (upstream `cf020f133487`) ·
COMPILERS **both**. Checksums equal in all 24 runs, so every difference is a
price and not a semantics change. Run at `e9c5c4d`.

| statistic | cell | `guard − noout`, gcc `small`/`large` | clang `small`/`large` |
|---|---|---|---|
| **A1** (`Ir(kernel)`/call) | `O3/isolated` | `+0.0000` / `+0.0000` | `+0.0000` / `+0.0000` |
| **A1** | `O0/isolated` | `+0.0000` / `+0.0000` | `+0.0000` / `+0.0000` |
| **W1** (whole-program `Ir`/call) | `O3/isolated` | `+0.0000` / `+0.0000` | `+0.0000` / `+0.0000` |
| ⛔ **W1** | **`O0/isolated`** | **`−2.2419` / `−19.5768`** | **`−0.7397` / `−6.5296`** |

As a percentage of the same cell's whole-program total, base = `noout`:
**gcc `−0.1370 %` (`small`) and `−0.1417 %` (`large`); clang `−0.0565 %` and
`−0.0584 %`** — W1, `O0/isolated`, both C columns, both inputs.

⭐ **The difference is real work, not startup noise, and it scales with the right
denominator.** It is **not** proportional to driver calls (20 000 vs 2 500) — the
absolute deltas are 44 838 and 48 942 — it is proportional to **records
processed** (20 000×7 = 140 000 and 2 500×62 = 155 000, from the published
`Inputs` table): **0.3203 and 0.3157 Ir per record** under gcc, **0.1057 and
0.1053** under clang. Two inputs, one constant, per compiler. That is the shape
of per-record work and nothing else.

> ⛔⛔ **SO: *"THE UNMISUSABLE CONTRACT IS FREE"* IS AN `O3` FACT. Un-inlined it is
> not free, and it is not free in the direction the finding rules out: upstream's
> no-output repair is the DEARER of the two.**

⚠ **`F136`'s published figures are NOT wrong** — it names its cell (`A1`,
`O3/isolated`) and every one of the four cells reproduces to the digit. **The
title generalises past the cell it measured**, and the RECAP body's *"the price
is exactly zero"* is the sentence that will be quoted.

⚠⚠ **AND THIS IS THE `which statistic` CELL'S OWN DEFECT, ONE LEVEL DOWN.**
`RECAP_PHP.md` measured on 2026-09-16 that `ph96` publishes **`A1` only** and
`W1` **zero times**. `F136` is the row's headline result and it is published in
one statistic. ⛔ **At `O0/isolated` the two statistics disagree in the strongest
possible way: A1 reads `+0.0000` against a sign-stable, scaling W1 difference on
four cells.** That is the `ph55` counterexample already on file
(`c-gcc` vs `c-gcc-h`, A1 `+0.0000 %` against **66.14 `Ir`/call** whole-program)
**reproduced on `ph96`, on `F136`'s own quantity.**

### 2.3 ⭐⭐ THE MECHANISM — **UPHELD, AND UNDER-STATED, AND NOW MEASURED PER SYMBOL**

`.temp/php61/ph96_where_is_the_difference.py` runs `callgrind_annotate` per
function on the two `-O0` builds and diffs the table. **gcc, `small.bin`, 20 000
calls:**

| symbol | `noout` | `guard` | delta |
|---|---:|---:|---:|
| `ph96_call_method` — the callee, `zend_interfaces.c:88-93`'s home | 4 977 962 | 4 894 543 | **−83 419** |
| `ph96_unset_dimension` — the caller, `:512` | 873 429 | 912 010 | **+38 581** |
| `kernel` — **the A1 symbol** | — | — | **+0** |
| **whole program** | | | **−44 838** |

At `-O3`: **no symbol differs at all.**

▶ ⭐⭐⭐ **THAT IS `F136`'s MECHANISM, MEASURED DIRECTLY, WHICH IT NEVER WAS.**
*"Removing the output moves the call site from `:94`'s contract onto `:88-93`'s"*
is now a number: 83 419 `Ir` leaves the callee and 38 581 arrives in the caller.
The finding asserted a structural story; this is the story with instruments on it.

⭐ **And it under-states in one direction:** the two contracts are not the same
amount of work. The callee's `:88-93` disposal costs **more** than the caller's
guard, so upstream's spelling is the dearer one un-inlined.

**The narrowing `F136` should carry — and it is NOT the one the brief proposed.**

- ⛔ The brief's §2.2 third bullet (*"it would not be zero for an obligation whose
  callee carries no such test"*) is **near-vacuous**: if the callee carried no
  such test, the no-output strategy would not dispose of the value at all and
  `cf020f133487` would not be a repair. There is nothing to compare.
- ✅ **The measured narrowing is INLINING**: *the price is zero **because both
  spellings inline into one symbol**; un-inlined they differ, and the direction
  is that upstream's is dearer.* That is checkable, it predicts, and it is
  `F136`'s own parenthesis promoted to the mechanism.

### 2.4 The quantifier — *"already written once, in the callee, for all seven no-output call sites"*. ✅ **UPHELD, AND ITS GROUND IS STRONGER THAN STATED**

`controls/census.json`: `sites: 23`, `no_output: 7`, `output: 16` — reproducing
`F133`'s census. `census.py:45-48` and `:107` match
`zend_call_method(_with_\d_params)?`, i.e. **every one of the 23 sites funnels
into the single `zend_call_method` in `zend_interfaces.c`**, whose `:88` test is
`if (!retval_ptr_ptr)` — which is *by definition* true at exactly the no-output
sites. ▶ **So it is not seven-out-of-seven by arithmetic; it covers every
no-output site that exists and every one that will ever be added.** `F136` states
the weaker version.

### 2.5 *"Does `counts` hide a real difference that `exact` would not?"* ✅ **YES, AND `ph96` IS ITS OWN WORKED EXAMPLE**

`identity.c-gcc` is `level: "counts"`, `counts_noout == counts_guard ==
[207, 198, 705]`, and **`md5_fn_equal: false`**. So under gcc the two kernels are
**different machine code with identical instruction, relevant-instruction and
byte counts**. ▶ **`counts` licenses *"the same cost at instruction-count
granularity"* and licenses **nothing** about the programs being the same.**
`exact` (clang, `md5_fn_equal: true`) licenses both. `F136` is right to call the
clang evidence strong and the gcc evidence weaker, and it should say *what*
`counts` does not license, because the row's own record shows it not licensing it.

### 2.6 The method lesson. ✅ **RIGHT, AND THE OTHER READING IS ALSO RIGHT, AND THEY ARE NOT ALTERNATIVES**

*"Registering both poles of a disjunction does not make the disjunction
exhaustive"* — ✅ correct and worth keeping. *"`P1` should have had a null pole"* —
✅ also correct, and it is the **operational** form of the same lesson. ⭐ **This
round is the argument for keeping the second form**: `P1` was *cheaper* vs
*dearer*, the answer at `O3` was *neither*, and the answer at `O0` is
**`dearer`** — the pole the manager did register, in a cell nobody measured. ▶ **A
disjunction that omits *neither* also tends to omit *it depends on the cell*.**

### 2.7 What may enter `.memory-php/`

| | |
|---|---|
| ✅ **MAY ENTER** | *the price of an obligation's spelling is a property of the **cell**, and at `O0/isolated` on `ph96` the two attested repairs differ by `−0.32`/`−0.11` `Ir` **per record** (gcc/clang) while A1 reads `+0.0000`* |
| ✅ **MAY ENTER** | *`identity_level = counts` licenses equal cost at count granularity and **nothing** about program identity — `ph96`'s `c-gcc` cell is `counts` with `md5_fn_equal: false`* |
| ✅ **MAY ENTER** | the method lesson, in **both** forms (§2.6) |
| ⛔ **MAY NOT ENTER** | *"the unmisusable contract is FREE"* unqualified, or *"the price is exactly zero"* without `A1, O3/isolated` in the same sentence |
| ⛔ **MAY NOT ENTER** | the brief's *"contingent on the callee already carrying the test"* narrowing — replace it with **inlining** |

---

## §3 `F133` — ⚠ **CONCLUSION UPHELD-NARROWED · ⛔⛔ TITLE REFUTED · ⛔⛔ ITS BUILD CAUTION NAMES THE WRONG BUILD, FOR THE SECOND TIME**

### 3.1 The (i)/(ii)/(iii) split, which is the right way to read it

- **(i) the repair existed in the tree.** ✅ **UPHELD, MEASURED.**
  `census.json` 23/7/16; `zend_object_handlers.c:413` takes the no-output
  contract **99 lines before** `:512` does not; `:385` guards `:384`.
- **(ii) its author knew it existed.** ⛔⛔ **NOT ESTABLISHED — AND THE ONLY
  AUTHORSHIP EVIDENCE ON THIS BOX POINTS THE OTHER WAY.** See §3.2.
- **(iii) an R1h cannot be read as evidence of discovery.** ✅ **UPHELD — BUT ON
  (i), NOT ON (ii).** ⭐ **The finding slides from (i) to (iii) through (ii), and
  it does not need to.** A repair that is a verbatim copy of a sibling 99 lines
  up in the same file is **not novel whoever found it**; *discovery* is a property
  of the repair's availability, not of anyone's mental state. ▶ **So (iii) stands
  on (i) alone, and the layer should take it that way** — which is strictly
  better, because (ii) is unmeasurable from a tarball and (i) is one `grep`.

### 3.2 ⛔⛔⛔ *"BY ONE AUTHOR"* — REFUTED FROM THE CITATION BASE

The title is *"BOTH CORRECT SPELLINGS OF AN OBLIGATION AND BOTH WRONG ONES LIVED
**IN ONE FILE, BY ONE AUTHOR**"*, and the body says the contract's test was
*"written by the same hand"*.

**Measured, from the pinned tarball** (sha256 `5783e0c0…d6919`, extracted to
`.temp/php61/tar/`, second method = the citation base itself rather than any
probe):

| file | `Authors:` header | last RCS `$Id` committer |
|---|---|---|
| `Zend/zend_object_handlers.c` — the four call sites `:384 :413 :427 :512` | **Andi Gutmans**, **Zeev Suraski** | **`wez`**, 2004-05-26 |
| `Zend/zend_interfaces.c` — the contract `:48`, `:88-93` | **Marcus Boerger** | **`helly`**, 2004-04-27 |

- ✅ ***"IN ONE FILE" IS TRUE***, of the four call sites — all four are in
  `zend_object_handlers.c`, confirmed by grep against the tarball at `:384`,
  `:413`, `:427`, `:512`.
- ⛔⛔ ***"BY ONE AUTHOR" HAS NO SUPPORT IN THE RECORD, AND THE RECORD CUTS
  AGAINST IT.*** Two named authors on one file, one on the other, and a third
  name as the last committer of the first. There is no git history in a tarball.
- ⭐ **What IS establishable, and is a different and weaker claim:** the **fixer**
  is Marcus Boerger — `controls/cf020f133487.patch` reads `From: Marcus Boerger
  <helly@php.net>, Sat, 19 Mar 2005` — and Boerger is the author of the file the
  unmisusable contract lives in. ▶ **That is evidence that the person who APPLIED
  the repair knew the contract, not that the person who WROTE the defective call
  sites did.** As a finding it is much less interesting, and it is the one the
  bytes support.

▶ **Consequence: the title must lose *"BY ONE AUTHOR"*, and (iii) must be
re-grounded on (i).** `F133`'s conclusion survives; **its stated reason does not.**

### 3.3 ⛔⛔ AND ITS `§A3a` BUILD CAUTION NAMES THE WRONG BUILD — `F127`, REPEATED, NINE HOURS AFTER THE AUTHOR'S OWN CORRECTION LANDED

`RECAP_PHP.md:2249-2251`: *"the binary is php-in-safe-rust's **oracle** build
(**`-O3 -march=native -flto`**, mysql+webext)"*.

- The probe is `.tasks-php/probes/ph96_arrayaccess_matrix.sh:63`, which defaults
  `ORACLE` to `…/oracle/bin/php-5.0.0-mysql-webext` — **the plain binary**.
- `ls …/oracle/bin/`: **only `-O3lto` and `-maxlto` carry `.buildinfo` files.**
  The plain binary has none.
- `PROTOCOL_PHP.md` §A3a already says this in capitals: *"⛔⛔ **THIS CLAUSE SAID
  `-O3 -march=native -flto` FOR ONE DAY.** Those flags are the SIBLING variants'
  … the plain binary has none and its `config.status` says `-O0`. ⭐ **The caution
  whose whole point is *say which build* named the wrong build** — `F127`."*

⛔⛔⛔ **DATES.** The protocol correction landed at **`1cc2c0e`, 2026-09-15
07:47**. `F133` landed at **`46560f9`, 2026-09-15 17:12** — **nine and a half
hours later, same author, same day.**

⭐⭐⭐ **THIS IS THE MOST IMPORTANT SINGLE DATUM IN THE ROUND, AND IT IS NOT ABOUT
`ph96`.** It is `§5.0`'s question answered by experiment: the knowledge was in a
**person-facing prose document**, in **capitals**, in the section the finding
cites, **written that morning by the person who then broke it that afternoon.**
See §5.0.

### 3.4 The generalisation — ⭐ **`ph56` SUPPORTS (i), AND THE ANSWER WAS ALREADY WRITTEN IN ITS OWN CONTROL'S DOCSTRING**

The brief said to do `ph56` first because it is the one other row with a `census`
control. I confirmed the population — `patterns-php/*/controls/census.py` returns
**exactly two files**, `ph56` and `ph96` — and read `ph56`'s.

`patterns-php/ph56-fetchmode-arith/controls/census.json`, `evidence.guards`,
measured against the pinned tarball:

| arm | guard in pristine 5.0.0? |
|---|---|
| `BP_VAR_R` | **YES** |
| `BP_VAR_UNSET` | **YES** |
| `BP_VAR_W`, `BP_VAR_RW`, `BP_VAR_IS`, `BP_VAR_FUNC_ARG` | no |

`1e708a5aeb30` adds the guard to **`BP_VAR_IS` only**. ▶ **So on `ph56` too the
repair was already written, in the same `switch`, in the same file, before the
bug was filed — the fix copies a sibling arm.** **(i) generalises to a second
row.**

⭐⭐ **And `ph56` answers the authorship half in the opposite direction, which
strengthens §3.2:** its docstring records that the sibling defect
(`BP_VAR_FUNC_ARG`) was fixed *"11 ½ months later, at RUNTIME, in a different
file, **by a different author**"* — `9183f91b506a` / `779e6d203e4f`, Dmitry
Stogov. ▶ **Where the corpus can speak about authorship, it says the repairs of
one construct come from different hands.**

⭐⭐⭐ **AND THE COST OF THIS ANSWER WAS ZERO — it is in the committed control's
own header, and nobody was on that path.** `F134`'s class again, for the fourth
time in this round.

**What a THIRD row would cost, since the brief asked rather than assuming:** the
other ten rows ship no `census` control, so the instrument does not exist. Building
one is not free — `ph96`'s is 8 264 bytes and `ph56`'s runs the 5.0.0 CLI six
ways. ▶ **Estimate, explicitly labelled an estimate: one engineer task per row**,
because `ph56`'s census is not a clone of `ph96`'s (different question, different
evidence tiers A/B/C). ⛔ **I did not measure this and no committed script rebuilds
it.** ⚠ **But the cheap half is free**: the question *"was the R1h's strategy
already present elsewhere in the same construct?"* is a `grep` against the pinned
tarball for every row, and costs no control at all. **That is the sweep I would
dispatch, not ten censuses.**

### 3.5 The scope caveat — ✅ **PRESERVED IN BOTH PLACES · ⚠ ONE PHRASE WILL TRAVEL BADLY**

`F133` states it twice and correctly: *"that is the **screened corpus cache**, not
php-src's full history. ***'No repair in the cache' is a result (F10); 'upstream
never fixed it' is a claim this box cannot support***"*, and again in the `_060`
blockquote: *"it still says nothing about whether some other commit, outside the
cache, ever did."* ✅ **Both survive.**

⚠ **The one phrase that does not carry it:** the same blockquote ends *"Same
obligation, different site, **no known repair**."* Quoted alone — and it is the
quotable sentence, because it is the routing decision for the candidate row —
*"no known repair"* compresses *"no repair in the 163-patch cache"* into something
a reader will take as *upstream never fixed it*. ▶ **One word: *"no repair in the
cache"*.**

### 3.6 What may enter `.memory-php/`

| | |
|---|---|
| ✅ **MAY ENTER** | *(i)+(iii) on (i)'s ground*: **an R1h is not evidence that its strategy was DISCOVERED, because on both rows where a census exists the strategy was already present in the same construct — `ph96` 7 of 23 call sites, `ph56` 2 of 6 switch arms.** Two rows, two mechanisms, both measured |
| ⛔ **MAY NOT ENTER** | *"by one author"* / *"written by the same hand"* / anything resting on (ii). **Refuted from the citation base** |
| ⛔ **MAY NOT ENTER** | *"an R1h is evidence about what was CHOSEN, not about what was KNOWN"* **as worded** — *known* is (ii). ▶ Re-word to *"…not about what was DISCOVERED"* |
| ⓘ **UNCHANGED** | it commits the ladder to nothing (`CLAUDE.md` rule 6) |

---

## §4 `F135` — ✅ **CONCLUSION UPHELD · ⛔ THE LAYER CLAUSE'S *"EXACTLY AS SURELY"* IS REFUTED · ⛔⛔ AND I FOUND THE THIRD MECHANISM, LIVE, ON THE TWO FILES THE LAYER CALLS THE MODEL**

### 4.1 The `expect` column as a whole, verdicted — ✅ **§0.1's population reproduces exactly**

Derived by importing `checkers.REGISTRY` at `e9c5c4d` and printing every entry
(29 filed; kinds: **20 checker, 7 tool, 2 landing**):

- **three** non-zero `expect`: `citecheck.py = 1`, `land_019_020.py = 2`,
  `land_m4.py = 2`;
- `st_expect` is **`0` on all 12 that declare one**, **`None` on 17**
  (8 checker, 7 tool, 2 landing) — so *"eight of those twenty are `kind=checker`"*
  is right: **8 of the 20 checkers**.

**The discriminator I used, and it is NOT *"it says so in its `why`"*:**

> ***Does the value move when the TREE moves?*** An INTENT-derived expectation is
> fixed by a line in the script. An OBSERVATION-derived one is a count over the
> corpus and changes when the corpus does.

| entry | verdict | how I told |
|---|---|---|
| `land_019_020.py` `expect=2` | ✅ **INTENT** | `land_019_020.py:490` is a literal `return 2` on the already-landed branch. The value is in the script; no corpus change can move it |
| `land_m4.py` `expect=2` | ✅ **INTENT** | `land_m4.py:27`, same shape |
| ⛔ `citecheck.py` `expect=1` | ⛔ **OBSERVATION** | `1` is *the number of standing adjudicated rot hits*. Repair `TASK_PHP_048.md:337` and the correct value is `0`; add a second false positive and it is `2`. It is a **count over the tree pinned as a literal** — `.memory-php/04-process.md` **law 6**'s class exactly (*a bound is not a derivation*) |

▶ **`F135`'s reviewer question is ANSWERED: `citecheck.py`'s `expect=1` is the
ONLY observation-captured expectation left in the registry.** (This is the one
manager prediction of five that survives — see §6.)

### 4.2 ⛔⛔⛔ THE HARDER VERSION, AND IT IS A LIVE THIRD MECHANISM

The brief asked whether *"a checker with no declared self-test"* is a third
silencing family, and noted the registry cannot tell *"has none"* from *"has one
and it passes"*. **I measured it.** Of the 8 checkers with `st_expect=None`, I
ran `--selftest` on the two whose source mentions it most:

```
width.py    --selftest : rc=0, SELFTEST PASS, 31.64 s
php_null.py --selftest : rc=0, SELFTEST PASS,  0.08 s
```

⛔⛔⛔ **BOTH SELF-TESTS EXIST, BOTH RUN, BOTH PASS — AND `checkers.py` NEVER
INVOKES EITHER, BECAUSE THE REGISTRY DECLARES `st_expect: None`, WHICH MEANS
*"no `--selftest` is declared"*. `CHECKERS PASS` is printed with 2 of 20
checkers' arms never exercised.**

⭐⭐⭐ **AND THEY ARE NOT ARBITRARY FILES.** `.memory-php/04-process.md` **law 16**
names exactly these two as the model to copy:

> *"The model to copy is `width.py` `N4`/`N3b` and `php_null.py` `N8`/`N9`/`N7b`:
> they re-assert a **published** result so the tool speaks when it stops
> reproducing, **and firing is the point.**"*

▶ **The two arm-suites the authoritative layer holds up as exemplary are the two
the registry does not run. If they stopped reproducing, nothing would speak.**

⚠ **It is a THIRD mechanism, and it is not the same as `F135`'s.** `F135`'s was
an expectation edited to match a failure. This is **an arm that is never
invoked**. Nothing is mis-asserted; nothing is asserted at all.

### 4.3 The layer clause — ⚠ **CONCLUSION UPHELD · ⛔ *"EXACTLY AS SURELY"* REFUTED, BY THIS ROUND'S OWN NEW INSTANCE**

> *"A ratchet silenced by editing its EXPECTATION is silenced exactly as surely
> as one silenced by editing its INPUT, and only the second is forbidden in
> writing."*

- ✅ **The second half is plainly true** and is the useful half: the house rule
  (`.tasks-php/README.md`) forbids editing the input and says nothing about the
  expectation.
- ⛔ ***"Exactly as surely" is FALSE, and the brief's own test case decides it.***
  There is an **ordering of recoverability**, and `F135`'s instance is the *most*
  recoverable of the three:

| mechanism | what survives the silencing | how it was/would be found |
|---|---|---|
| edit the **INPUT** | nothing — the evidence is destroyed | not findable from the tool |
| edit the **EXPECTATION** (`F135`) | the failing arm, fully visible to anyone running the tool directly; **and a `why` in committed registry text naming the arms** | ⭐ **found exactly that way** — by a sweep reading the registry |
| ⛔ **never declare the self-test** (§4.2, new) | **nothing to sweep**: no red arm, no wrong expectation, no `why` to read. The field says `None` and `None` is indistinguishable from *"there is no self-test"* | **not found for the life of the registry**; found here only by running the scripts |

▶ **So the right sentence is the ordering, not the equation.** And `F135`'s own
history is the proof: it was recovered *from the registry text*, which is
precisely what the other two mechanisms do not leave behind.

- ✅ ***"A benign cause does not make a failing arm benign"*** — **agree, and it is
  a DIFFERENT claim**, not a restatement. The layer clause is about *the
  mechanism of silencing*; this one is about *the inference from cause to
  harmlessness*. ⭐ **It is the durable half**, it is one sentence, and it is the
  one I would land.

### 4.4 Where it goes — ⛔ **NEITHER OPTION THE BRIEF OFFERED, BECAUSE THE SECOND ONE DOES NOT EXIST**

§4.2 of the brief says: *"does it enter `04-process.md` as a NEW law or as a
clause on the **existing ratchet rule**? ⭐ Prefer the second unless you can say
why."*

⛔⛔ **There is no ratchet rule in the layer.** `grep -ain "ratchet"` over
`.memory-php/00`–`04` returns **rc 1, zero hits**; over `.memory/` (the PAT
layer, which applies unchanged) **zero files**. The ratchet rule lives in
`.tasks-php/README.md`. **The preferred option is unavailable as stated.**

✅ **The right home is a CLAUSE ON LAW 6**, and `F135`'s own body already routes
itself there — *"the EIGHTH pinned figure to go stale in a `.tasks-php/`
validator (`.memory-php/04-process.md` law 6, *a bound is not a derivation*)"*.
Law 6 reads *"A FIGURE A VALIDATOR ASSERTS IS COMPUTED FROM THE TREE, OR IT IS
NOT ASSERTED"*, and `rot == 0` and `st_expect = 1` are both exactly that. ▶ **One
appended clause, no new law.** Proposed wording is in `§ FOR THE MANAGER` item 6,
where it also absorbs `F138` and `F132`.

### 4.5 What may enter `.memory-php/`

| | |
|---|---|
| ✅ **MAY ENTER** | *a benign cause does not make a failing arm benign* — one sentence, as a clause on **law 6** |
| ✅ **MAY ENTER** | the **ordering** in §4.3 (input ≻ expectation ≻ undeclared, by recoverability), **not** the equation |
| ✅ **MAY ENTER** | *an expectation is INTENT-derived if a line in the script fixes it and OBSERVATION-derived if a count over the tree does* — the discriminator, which is checkable |
| ⛔ **MAY NOT ENTER** | *"exactly as surely"* |
| ⛔ **MAY NOT ENTER** | anything as a **new law**, or as a clause on a **ratchet rule the layer does not contain** |
| ⓘ **NOT A FINDING, A REPAIR** | §4.2's two undeclared self-tests. Route as work, not as layer material — `§ FOR THE MANAGER` item 4 |

---

## §5 THE FOUR DOCUMENT FINDINGS

### 5.0 ⭐⭐⭐ THE SHARED QUESTION — **WHERE DOES A TRAP LIVE? RULING: *NOT THE LAYER, AND NOT THE TRAPS LIST EITHER.* LOCATION IS NOT THE VARIABLE.**

**The question is decidable, it is decidable WITHOUT item 129, and this round
decided it by accident.**

The brief's framing assumes the failures differ by *where the knowledge lives* —
tool docstring (`F134`), committed tool (`F132`), nowhere (`F131`, `F138`) — and
asks which home works. **Run the comparison across this round's evidence and the
homes are not the variable:**

| instance | where the knowledge lived | who wrote it | gap |
|---|---|---|---|
| `F132` instances 2 and 3 | `RECAP_PHP.md`, a person-facing finding | **the person who tripped it** | **within the hour** |
| ⭐ **`F133`'s build caution (§3.3, NEW THIS ROUND)** | **`PROTOCOL_PHP.md` §A3a, in capitals, the section the finding cites** | **the person who tripped it** | **9 ½ hours** |
| `F138` | `boxcheck.py`, whose CLI **already printed the members** (§5.0a) | **the person who tripped it** | **1 day** |
| `F134` | `preimage_screen.py::same_function`'s docstring | the person who tripped it, 3 days earlier | 3 days |

▶ ⭐⭐⭐ **FOUR HOMES — a tool docstring, a committed tool's output, a handoff
finding, and a person-facing protocol section IN CAPITALS — AND ALL FOUR FAILED,
AGAINST THE PERSON WHO HAD AUTHORED THE TEXT.** `F134`'s proposed remedy is
*"move it to where a PERSON meets it"*; **`F133` is the experiment, and the
person-facing document lost.**

**THE RULING, for all four:**

> ⛔ **NOT THE LAYER**, and **not the traps list either**, and **not on the ground
> the brief's case-against gives.** The case-against says a law per hand-error
> fills the layer with things true of people in general. ⭐ **That is right, and
> the measurement above is *why* it is right: the general claim — *a document is
> not a control* — is exactly a fact about people in general, and moving it
> between documents is what the evidence shows does not work.**
>
> ✅ **What IS programme-specific, and what I would land, is the narrow
> operational half, as a clause on LAW 6** (§4.4): *a figure asserted about the
> tree must be printed by a tool at the moment it is quoted* — extended from
> *validators* to *documents*, and extended from *numbers* to *sets*.
>
> ⭐ **The reason that one is not "true of people in general" is that it names an
> artefact this programme has: a committed checker that prints the thing.**

**And the alternative, stated so the manager can act on it:** for each of the
four, the durable home is **an arm in a tool that prints** — `F132` already has
one (`cbaseline_diff.py`), `F131` already has one (`boxcheck.py`'s duplicate-key
arm, which I exercised in §0), `F138`'s exists and was not invoked (§5.0a), and
`F134`'s exists and was bypassed by reading a patch by hand instead of running
`preimage_screen.py`. ▶ **Three of four already have the tool. The residue is a
habit, not a document, and no document has ever fixed it.**

**Is item 129's census the sizing instrument?** ⛔ **No, and it is not a blocker.**
The home question is not a frequency question — it asks whether **location changes
outcome** — and four instances at four different locations, all failing, answer
it. A ~289-item census would tell us *how often*, which does not bear on *where*.
▶ **Item 129 is UNBLOCKED for this purpose.** (It may still be owed for `F123`'s
separate clause; that is not this question.)

### 5.0a `F138` — ⚠ **CONCLUSION UPHELD (it is DISTINCT from `F132`) · ⛔⛔ REASON REFUTED IN ITS LOAD-BEARING WORD**

**The arithmetic half** reproduces and I did not need to re-run it: `boxcheck.py`
today prints `33 rows, 33 distinct`, so the six duplicate keys are gone, and
`RECAP_PHP.md:1950-1954`'s raw-vs-deduplicated table is arithmetic over committed
commits.

⛔⛔ **But the sentence the whole finding rests on is wrong:**

> *"THE PART THAT MAKES THIS A FINDING AND NOT AN ERRATUM: **I DID RUN THE
> TOOL.** … **One `print` of the set** at `f98e716` would have shown `F120 … F125`
> sitting in it."*

**`.tasks-php/boxcheck.py`'s `main()` ALREADY PRINTS THE MEMBERS:**

```python
print(f'{"RULE-9 rows":18} {len(keys):4}  {len(set(keys))} distinct, '
      f'{len(open_cycles)} open cycle(s): {" ".join(open_cycles)}')
```

`git log -S 'open cycle(s):'` dates that line to **`c868e60`, 2026-09-15
14:43** — it is part of **`F131`'s own repair**, written by the manager **the day
before** the `F138` error. ▶ **So the tool was not run. A bespoke sweep imported
`rule9_rows` and reimplemented the reporting path badly.**

- ⭐⭐ **That makes `F138` MORE distinct from `F132`, not less — on a ground it
  does not state.** `F132` is *a count standing in for a set*. The corrected
  `F138` is ***a one-off caller of a checker's library function does not inherit
  the checker's reporting***. Different mechanism, different remedy (`F132`'s is
  "diff the set"; this one's is "**run the checker**"). ✅ **Keep it separate. Do
  not merge.**
- ⛔ **But *"I used the tool" is not the defence it sounds like* is the wrong
  lesson** as stated, because **the tool was not used**. ▶ The lesson is
  ***"I called the tool's function" is not "I ran the tool."***

**The de-duplication rule** — *"a key with two rows has been verdicted in one of
them, so it is not open"*. ⚠ **Right answer, wrong rule.** It is sound only
because every duplicated key happened to have one verdicted row. The correct rule
is structural and needs no heuristic: **the backlog is the count of distinct KEYS
no row of which carries a verdict.** Two rows both opening `⛔ UNREVIEWED` would
break the manager's rule and not the structural one.

**The residue** — *"a tool that returns a falsy value for 'cannot answer' invites
the `len()` mistake"*. ⛔ **Refuted in its mechanism.** `rule9_rows` returns
`(None, None)` on no-parse, and **`len(None)` raises `TypeError`** — it is loud,
not silent. `boxcheck.main()` handles it correctly (`if keys is None:
fail.append(…)`). ✅ **The recommendation still stands for the *series*** — twelve
no-parse commits are UNKNOWN and must not be rendered as 0 — **but not for the
reason given, and the tool needs no repair for it.**

⚠ **One repair the tool DOES arguably need, and I did not make it:**
`rule9_rows`'s `open_cycles` is appended **per row**, with no de-duplication, so
the exact `F120`–`F125` shape would over-count it again. One line
(`list(dict.fromkeys(open_cycles))`) fixes it. ⛔ **I deliberately did not apply
it** — see `§ FOR THE MANAGER` item 5 for why, and note `boxcheck.py`'s
duplicate-key arm already fails on the upstream cause, so the marginal value is
small.

### 5.1 `F134` — ✅ **ITS DISCLAIMER HOLDS · ⚠ ITS PROPOSED REMEDY IS REFUTED BY §5.0**

- ✅ **The body does say it**, at `RECAP_PHP.md:2156-2159`: *"NOT a claim that the
  tool's measured reach changed … whether `235e6c0afe1d` is even in that 170 **I
  did not measure**. ⛔ Do not quote this finding as moving that number."*
  I read the whole body and **nothing else implies otherwise** — every other
  sentence is about a hand reading outside the tool's path. ✅ **Clean.**
- ⛔ **Its remedy — *"both now sit in a task file's `§3 TRAPS` where a person meets
  them"* — is refuted by `F133` (§3.3):** a person-facing document, in capitals,
  authored by the same person that morning, lost by nine and a half hours.
- ⓘ **Its core sentence survives and is worth keeping as prose**: *a trap
  documented only where the code meets it is documented for the code.* ⚠ **The
  converse it implies — that documenting it where the person meets it works — is
  the part this round refutes.**

### 5.2 `F132` — ⚠ **CONCLUSION UPHELD-NARROWED · the repair is right and *"never the number"* is over-stated by its own evidence**

- ✅ **The mechanism reproduces**: `units()` splits on blank lines, so the unit is
  a paragraph and prose moves the count.
- ⛔ ***"ADJUDICATE THE SET, BY UNIT TEXT, NEVER THE NUMBER"* — the last three
  words are refuted by the finding's own closing paragraph**: *"What the bare run
  got right: it **failed**, loudly, and stopped the manager mid-edit."* ⭐ **The
  NUMBER is what fired.** I used it myself this round — `scanned 33 file(s); 77
  hit(s); ratchet 77`, rc 0 — and because it did not move I did not need the set.
  ▶ **The correct rule: *the count is a valid TRIPWIRE and an invalid
  ADJUDICATION.*** That keeps the ratchet, which is the thing that worked.
- ⛔ **Does the PARAGRAPH UNIT need changing? No.** Any unit is arbitrary, a
  line-keyed unit is worse (line numbers move), and `_059` refused widening
  `BASE`/`XLANG` for an eighth time so a better regex is off the table.
  ⭐ **`cbaseline_diff.py` makes the unit irrelevant by diffing text**, which is
  the right shape: it changes the QUESTION rather than sharpening the pattern —
  `PROTOCOL_PHP.md` §B2's durable lesson, applied correctly.
- ✅ **Its strongest clause is untouched and this round adds a third instance to
  it** (`F133`, §3.3): *"remember to check" is refuted as a control by the person
  who wrote the reminder.*

### 5.3 `F131` — ✅ **UPHELD, AND THE REPAIR IS VERIFIED LIVE BY THIS ROUND'S OWN SCOPE**

- ✅ **The repair held**: 33 rows, 33 distinct, 0 duplicate keys, 8 open cycles,
  derived in §0. **This round is correctly scoped.** That was the one §5 item
  with a live consequence and it was nearly free.
- ✅ **The structural half landed in a tool, not a document**: `boxcheck.py`'s
  `d9` arm fails on any key with two rows, and its comment says why. ⭐ **That is
  the only one of the four whose lesson is in an arm that runs on every
  invocation, and it is the only one of the four that has not recurred.**
- ✅ **Its layer-shaped clause is CORRECT**: *a verdict-shaped phrase in a verdict
  column is a verdict, whoever wrote it, so self-narrowing must not share a column
  with review outcomes, because that erases law 12's distinction.* ⚠ **But it
  should not enter the layer as a law** — it is a **schema rule for one table**,
  it is already enforced structurally for the duplicate half, and `rule9_rows`'s
  docstring carries it. ▶ **Where it should go, if anywhere, is a second
  `boxcheck.py` arm** — see `§ FOR THE MANAGER` item 5.

### 5.4 What may enter `.memory-php/` — all four

| finding | may enter | may NOT enter |
|---|---|---|
| **F138** | ⛔ **nothing as a law.** ✅ The corrected distinction (*calling a checker's function is not running the checker*) belongs in **law 6's new clause** | *"I ran the tool"*; the *"falsy value"* residue's mechanism |
| **F134** | ⛔ **nothing** | its remedy (*the traps list is the right home*) — **refuted** |
| **F132** | ✅ *the count is a TRIPWIRE, not an ADJUDICATION* — into **law 6's clause**, same sentence | *"never the number"* |
| **F131** | ⛔ **nothing** — a document repair, already enforced in an arm | its verdict-column clause as a **law**; it is a table schema rule |

---

## §6 THE MANAGER'S FIVE PREDICTIONS — **ONE OF FIVE SURVIVES**

| | prediction | score |
|---|---|---|
| **P1** | `F137` UPHELD-NARROWED; clause 2 refuted or heavily narrowed on `ph97`; needs a third outcome category (*hung*) | ⚠ **HALF.** ✅ Clause 2 **refuted outright** (not narrowed) and the *hung* category is real. ⛔ **But the overall verdict is not UPHELD-NARROWED** — clause 3 is refuted-as-written too, and the *hung* outcome is on the **Rust** side, where `F137`'s table already has it, not in the C binary the prediction implies. ⛔ And the reading `P1` rests on (§1.2's datum) **under-states**: the row faults at **every** `-O`, not merely at `-O3` |
| **P2** | `F136`'s conclusion survives untouched; mechanism survives with the *callee-already-carries-the-test* narrowing | ⛔ **REFUTED, BOTH HALVES.** The conclusion does **not** survive untouched — the headline is refuted at `O0/isolated` in W1 on four cells. The narrowing is **inlining**, not the callee's test, and the predicted narrowing is near-vacuous (§2.3) |
| **P3** | `F133` UPHELD-NARROWED on (i)/(ii)/(iii); (ii) not established | ⚠ **CORRECT ON (ii), UNDER-STATED OVERALL.** ✅ (ii) is not established. ⛔ **The prediction misses that the record cuts AGAINST the title** (§3.2: two authors on one file, one on the other, a third as last committer) and misses `F133`'s own `F127` build mislabel (§3.3), which is the bigger result |
| ✅ **P4** | `F135`'s layer clause UPHELD and enters as a **clause on the existing ratchet rule**, not a new law; `citecheck.py`'s `expect=1` is the **only** observation-captured expectation left | ⚠ **SPLIT — and the survivor.** ✅✅ **The `expect=1` half is EXACTLY RIGHT**, and it is the only prediction in five rounds' registers I have upheld without qualification. ⛔ *"Enters as a clause on the existing ratchet rule"* is **impossible**: there is no ratchet rule in the layer (§4.4). ⛔ And the clause is **not** upheld — *"exactly as surely"* is refuted |
| **P5** | §5.0 ruled *"not the layer"* for all four, at most one clause entering, and the home question decidable **without** item 129 | ⚠ **CONCLUSION RIGHT ON ALL THREE LIMBS, REASON DIFFERENT.** ✅ Not the layer; ✅ one clause; ✅ decidable without item 129. ⛔ **But the reason is not the one predicted** — it is not that a census would be too big, it is that **location is not the variable**, which §3.3 measured by accident. ▶ **UPHELD-ON-NEW-GROUND** |

▶ **Plainly: `P4`'s measurable half is the one clean survival, and it is the half
the manager could have checked in three minutes and did not.** A round that
refutes everything is as suspicious as one that confirms everything, so I state
it: **`P4`'s `expect=1` claim is correct, `P5`'s three limbs are all correct, and
`P1`'s direction was right even though its shape was not.**

---

## § WHAT I AM UNSURE OF

1. ⚠ **`si_addr` `(nil) → 0x1` at clang `-O2` on `ph97`: I assert this is a
   REORDERING, and that is an inference, not a measurement.** I did not
   disassemble. **Cost to settle: an `objdump` of the two clang builds, which I
   estimate at minutes** — ⛔ **explicitly an estimate; I did not run it.** The
   *measurement* (the address moves at `-O2`, deterministically, at both `-O2`
   and `-O3`, and not at `-O0`/`-O1`) stands on its own.
2. ⚠ **My `-O0` price difference on `ph96` is `W1`, and `W1` at `-O0` includes
   driver and libc work that the row's published statistic deliberately excludes.**
   I argue it is real per-record work because it scales with **records** and not
   with **calls** (0.3203 vs 0.3157 `Ir`/record, gcc), and the per-symbol
   breakdown puts all of it in `ph96_call_method` and `ph96_unset_dimension`.
   ⚠ **What I did NOT do is check whether `.tasks-php/STATISTICS_001.md` licenses
   a `W1` comparison at `-O0`**; if it does not, my refutation of `F136`'s
   headline needs a statistic that is licensed there, and the per-symbol table in
   §2.3 is the one I would fall back on, because it needs no statistic at all.
3. ⛔ **My first must-fire control for §2.2 FAILED TO FIRE and I report it rather
   than dropping it.** `.temp/php61/ph96_price_at_O0.py`'s `guard2` variant adds
   `if (!retval) { (void) 0; }` and reads `+0.0000` everywhere — because an empty
   branch costs nothing at any `-O`. ✅ **I replaced it with a direct measurement**
   (`ph96_where_is_the_difference.py`, the per-symbol breakdown), which is
   stronger. ⚠ **But it means the `-O0` A1 zeros in my table have no synthetic
   positive control**; what they have is the per-symbol table showing the delta
   living in two named non-`kernel` symbols, which I consider sufficient and
   someone may not.
4. ⚠ **`F133` (ii): I show the FILE HEADERS name different authors. I do not show
   that the four ArrayAccess handlers were written by Gutmans/Suraski** — a header
   names a file's authors, and a function added later can be anyone's. ▶ **My
   claim is precisely that (ii) is UNESTABLISHED and that the only evidence on
   this box cuts against the title, not that the title is false about the
   handlers.** Settling it needs php-src history, i.e. network, which this box
   does not have.
5. ⚠ **I did not verify that `width.py`/`php_null.py`'s self-tests were ALWAYS
   undeclared.** I measured the registry at `e9c5c4d`. It is possible they were
   declared and removed. ⛔ **Unmeasured; a `git log -S "st_expect"` would settle
   it and I did not run one.**
6. ⚠ **`width.py --selftest` at 31.64 s is MEASURED (a single run, `time.time()`
   around a `subprocess.run`).** It would roughly double the registry sweep's
   ~35 s. `php_null.py --selftest` at 0.08 s is free. ⭐ **Per `F123`: this is my
   own estimate of a check's cost and it is the section that gets demoted — so I
   say plainly that 0.08 s is free and the 31.64 s is the only argument against
   declaring both, and it is a weak one against a self-test that nothing runs.**
7. ⚠ **§1.4's claim that the published table has no detection column rests on one
   row's table** (`ph96`). I read its section headers only, and did not check the
   other eleven. `report.py` is shared, so I expect it to hold, but **I did not
   measure it.**

---

## § ORDER TO RESUME IN — **THIS BINDS THE MANAGER (`F123`)**

I reached all five sections, so this is the residue, not an interruption. **Priority
is mine and it is to be CARRIED, not re-ranked.**

1. ⭐⭐⭐ **HIGHEST — `F133`'s `F127` REPEAT (§3.3) IS THE ROUND'S BIGGEST RESULT
   AND IT IS NOT IN ANY OF THE EIGHT FINDINGS.** A caution whose entire content is
   *say which build* named the wrong build, nine and a half hours after its own
   author corrected that exact clause in `PROTOCOL_PHP.md`. ▶ **Open it as a
   finding in its own right**, because §5.0's ruling depends on it and a ruling
   whose evidence is buried in a review report will not survive the next round.
   **Cost: one `RECAP_PHP.md` edit.**
2. ⭐⭐⭐ **`F136`'s headline must be re-stated before it is quoted anywhere**
   (§2.2). *"The unmisusable contract is FREE"* is an `A1, O3/isolated` fact and
   it is false in `W1` at `O0/isolated` on four cells. ⛔ **This is live: `ph96` is
   the row that just closed `T6`, and the finding is its headline.**
   **Cost: one `RECAP_PHP.md` edit; the measurement is already in
   `.temp/php61/ph96_price_at_O0.json` and its generator.**
3. ⭐⭐ **The two undeclared self-tests (§4.2).** `width.py` and `php_null.py` —
   the two files **law 16 names as the model** — have passing `--selftest`s the
   registry never runs. **Cost: two registry lines + one sweep re-run; measured
   marginal runtime 31.72 s.** ▶ **And the design question behind it: `st_expect:
   None` conflates *"has none"* with *"has one, unfiled"*, and a three-valued
   field would separate them at zero runtime cost.**
4. ⭐⭐ **The cheap generalisation of `F133`(i) to the other ten rows (§3.4) — as a
   GREP, not as ten censuses.** *"Was the R1h's strategy already present elsewhere
   in the same construct?"* is one pass over the pinned tarball per row. ▶ **Do
   NOT dispatch ten census controls**; I estimate that at one task per row and I
   did not measure it.
5. ⚠ **`F137`'s re-statement** (§1.2, §1.4): narrow clause 2 to the branch-folding
   rule with `ph97` as the negative instance in the same sentence; replace clause
   3 with the fourth reading; fix the *"correct answer"* sentence to the control's
   own wording.
6. ⓘ **LOWEST — the optional `rule9_rows` de-duplication (§5.0a).** One line. The
   upstream cause is already caught by `boxcheck.py`'s duplicate-key arm, so the
   marginal value is small and it can wait.

⛔ **What I would NOT prioritise, and say so explicitly so it is not silently
demoted:** item 129's ~289-item census is **not** needed for §5.0's ruling and
should not be treated as blocking it. It may still be owed for `F123`'s separate
clause.

---

## § FOR THE MANAGER — numbered, actionable

1. ⛔⛔⛔ **`F137` clause 2 is REFUTED.** `ph97`'s C rung faults in **all eight**
   builds (`gcc` and `clang`, `-O0`…`-O3`), measured at `e9c5c4d` by
   `.temp/php61/ph97_c_optsweep.py` (committed generator, JSON beside it).
   **Update the `F137` body and its RULE-9 row.** The narrowed rule to keep is in
   §1.2 and it is *stronger as a rule and weaker as a headline*, exactly as the
   brief's option (b) anticipated.
2. ⛔⛔ **The brief's own §1.1 correction is wrong** (§1.3): `ph97`'s `unchecked`
   variant **is** a guard-deleted mutant, same construction as `ph96`'s
   (`rust_bug.py:115`). The `source: "unsafe.rs"` field names the base. ▶ **Do not
   carry *"the two sweeps are not the same construction"* into `RECAP_PHP.md`.**
   The *real* asymmetry — C table = shipped rung, Rust table = mutant — is in
   §1.3 and **should** be carried.
3. ⛔⛔⛔ **`F136`'s headline is refuted at `O0/isolated`** (§2.2) and its mechanism
   is **upheld and under-stated**, now measured per symbol (§2.3: `−83 419` from
   the callee, `+38 581` to the caller, `+0` in `kernel`). ▶ **Re-state, do not
   append** (item 73). ⚠ **This is `ph96` publishing `A1` only, which the
   `which statistic` cell flagged on 2026-09-16 — the defect it names has a live
   consequence and this is it.**
4. ⭐⭐ **Two checkers' self-tests are never run** (§4.2): `width.py` and
   `php_null.py`, the two the layer's **law 16** calls the model. Measured:
   both `rc=0 SELFTEST PASS`, 31.64 s and 0.08 s. ▶ **Declare `st_expect: 0` for
   both**, or decide the three-valued field. ⛔ **I did NOT make this edit** —
   adding entries to the ratchet during the round that reviews the ratchet is
   `F132`/`F138`'s own shape, and the runtime cost is a decision that is yours.
5. ⓘ **One optional one-line tool repair I did not apply**, with the reason:
   `boxcheck.rule9_rows` appends to `open_cycles` per row with no de-duplication,
   so the `F120`–`F125` shape would over-count again;
   `list(dict.fromkeys(open_cycles))` fixes it. ⛔ **Not applied** because (a) the
   duplicate-key arm already fails on the cause, and (b) editing the tool `F138`
   is about, mid-review of `F138`, is the thing this round exists to discourage.
6. ✅ **THE ONE CLAUSE I WOULD LAND IN `.memory-php/04-process.md`, as an APPEND
   TO LAW 6 — covering `F135`, `F138` and `F132` at once, and NOT as a new law:**

   > *…and the same applies to a figure a **DOCUMENT** asserts about the tree: if
   > a committed tool prints it, quote the tool's output **and the commit you ran
   > it at**, never a literal. ⚠ **And a tool that prints a SET must be RUN for
   > its set** — calling its function and taking `len()` is not running it, and
   > the count is a valid **tripwire** and an invalid **adjudication**.
   > ⭐ A benign cause does not make a failing arm benign.*

   ⛔ **Nothing else from the eight should enter**, and specifically **not** a law
   about where traps live: §5.0 measures four homes and four failures, all against
   the text's own author.
7. ⛔ **The brief's §4.2 preferred option does not exist.** `grep -ain "ratchet"`
   over `.memory-php/00`–`04` is **rc 1, zero hits**; the PAT `.memory/` has none
   either. **There is no ratchet rule in the layer to append to.** Law 6 is the
   home, and `F135`'s own body already routes itself there.
8. ⚠ **`F133`'s title must lose *"BY ONE AUTHOR"*** and its rule must be re-worded
   from *"what was KNOWN"* to *"what was DISCOVERED"* (§3.2). ✅ **And `ph56`
   supports (i) at zero cost** — `BP_VAR_R` and `BP_VAR_UNSET` already carried the
   guard — so the layer gets **two rows**, which it did not have.
9. ⚠ **Two phrases that will travel badly if quoted alone**, both one word from
   correct: `F133`'s *"no known repair"* → *"no repair in the cache"* (§3.5), and
   `F137`'s *"where the correct answer is … a wrong checksum"* → the control's own
   *"UB exploited, not lowered"* (§1.5b).
10. ⓘ **Registries re-run at the end of the round, as required** (§8.8): see below.

---

## § END-OF-ROUND CHECKS (DoD item 8)

| check | result |
|---|---|
| `python3 .tasks-php/checkers.py` | ✅ **`CHECKERS PASS`**, 29 filed, arm-count claims all `ok` |
| `python3 .tasks-php/cbaseline_check.py` | ✅ **`scanned 33 file(s); 77 hit(s); ratchet 77`, rc 0** — ⭐ **the count did NOT move**, so no set diff was needed (`F132`; and §5.2 is the verdict on using the number this way) |
| `python3 .tasks-php/boxcheck.py` | ✅ box 20/20 lines, 138 findings, highest `F138`, **RULE-9 33 rows / 33 distinct / 8 open cycles, members printed**, catalogue 102, `.memory-php/` range 0 stale |

⚠ **I repaired no tool, so no registry re-run was owed on that ground.**

---

## § WHAT I DID NOT DO

1. ⛔ **I did not re-run `.tasks-php/probes/ph96_arrayaccess_matrix.sh`.** `F133`'s
   2×2 (the four ArrayAccess handlers against the 5.0.0 oracle) is taken as
   reproducing, per the brief's instruction to attack the generalisation. **Its
   measurement half is UNVERIFIED BY ME.**
2. ⛔ **I did not re-run either row's `rust_bug.py`.** `ph97`'s `O0` SIGABRT /
   `O1-O3` TIMEOUT and `ph96`'s four-by-three table are read from committed JSON.
3. ⛔ **I did not sweep the other ten rows** for `F133`(i) or for `F137`'s axis. I
   did `ph56` as instructed and priced a third row as an **estimate**.
4. ⛔ **I did not disassemble anything.** §1.2's reordering inference and §2.5's
   `counts`-vs-`exact` discussion both rest on committed `md5_fn` / `counts`
   fields and on callgrind, not on `objdump`.
5. ⛔ **I did not check `.tasks-php/STATISTICS_001.md`** for whether `W1` at `-O0`
   is a licensed comparison (§ WHAT I AM UNSURE OF, 2).
6. ⛔ **I did not verify that eleven other published tables lack a detection
   column** — only `ph96`'s (§ WHAT I AM UNSURE OF, 7).
7. ⛔ **I did not measure whether `235e6c0afe1d` is in `same_function`'s 170.**
   `F134` says nobody did; I did not either, and I do not need it for the verdict.
8. ⛔ **I did not run the two staleness brackets** (`harness/measure.py
   --check-stale`, the php one through `harness-php/gate.py`). They are §0.1
   premises about the tree, not claims of mine, and nothing I did could move them
   — I built only under `.temp/`.
9. ⛔ **I did not verify `F138`'s forty-commit sweep myself.** I verified that its
   conclusion's *precondition* is gone (0 duplicate keys today) and refuted its
   **reason**; the historical raw-vs-deduplicated table is unchecked.
10. ⛔ **I edited nothing under `patterns-php/`, `harness/`, `common/`,
    `patterns/`, `results/`, `pilot/`, `common-php/`, `.web/`, `RECAP_PHP.md` or
    `.memory-php/`.** I ran `git log`, `git show` and `git status` only. **I ran
    no `git add` and no `git commit`.** My only writes are
    `.tasks-php/TASK_PHP_061_REPORT.md` and `.temp/php61/`.

---

## § ARTEFACTS — generators kept, blobs deletable

| path | role |
|---|---|
| `.temp/php61/ph97_c_optsweep.py` + `.json` | ⭐ **the C half of `F137`'s own falsifier, on `ph97`** — 16 builds, 16 runs, both candidate inputs, with a classifier control |
| `.temp/php61/ph96_price_at_O0.py` + `.json` | `F136`'s forward prediction tested at `-O0` and `-O3`, 24 callgrind runs, both compilers, both inputs. ⚠ **Its `guard2` control does not fire and the file says so** |
| `.temp/php61/ph96_where_is_the_difference.py` + `.json` | ⭐ **the per-symbol breakdown — `F136`'s mechanism, measured** |
| `.temp/php61/sweep/`, `o0price/`, `where/`, `tar/` | binaries, `.so`, callgrind outputs and the extracted tarball files. ⛔ **Re-derivable by the three scripts above; delete freely.** |

⚠ **Every number in this report has a committed-or-`.temp/`-generator except
three, and I name them: the `git log` dates in §3.3 and §5.0a
(`git log -S`, one command each, quoted inline), the file-header authorship in
§3.2 (`tar -xzf` + `head`, quoted inline), and the `width.py`/`php_null.py`
timings in §4.2 (a `time.time()` wrapper, quoted inline).**
