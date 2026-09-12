# TASK_PHP_037 — SEARCH `ph45`'s R4 ENDPOINT, and batch the row's owed prose

**Role:** research **engineer**. **One agent, alone** — this is careful
construction, not mining.
**Report:** `.tasks-php/TASK_PHP_037_REPORT.md` — **write the FILE** (rule 10).

**Read**, in this order:
1. `RECAP_PHP.md` — the START HERE box, then **F77** (the precedent: the first
   R4 endpoint in either programme that moved), **F82** (which *widens* this
   search — §2 below), **F80/F81** (this row), and **open items 58, 59, 61**.
2. `.tasks/PROTOCOL.md` — rules 6, 9, 10, 11, 13, **14**.
3. `.tasks-php/PROTOCOL_PHP.md` — **§B1/§B1.1/§B1.2/§B1.3, §B2, §H** all bind.
   **§H is the one that decides whether your work lands**: a validator ships
   with its must-fire negatives or it does not ship.
4. `.memory-php/` 00–04 **in full** — authoritative, and it supersedes any task
   report it contradicts. ⭐ **`02-ladder.md`'s FIFTH FLAG is F82** and it is
   about this task.
5. ⭐⭐ **`patterns-php/ph29-recvfrom-alloc/controls/spellings.py`** — **1 062
   lines, the best copy in the tree, and your template.** It is the one whose
   **75 §H cases** (44 must-fire, 31 must-not-fire) found two real defects in
   machinery it had inherited (F79). ⚠ **`patterns-php/ph16-fdset-index/controls/spellings.py`
   is 1 505 lines and CARRIES BOTH OF THOSE DEFECTS UNFIXED** (open item 57) —
   **clone `ph29`'s, not `ph16`'s**, and say which you cloned.
6. `patterns-php/ph45-htmlent-cache-int/` — **all of it**, and in particular
   **`safe_tuned.rs`'s header**, which is where this row's R3-side search lives.
7. `TASK_PHP_035_REPORT.md` — how the `ph29` search was actually run.

⚠⚠ **`RECAP_PHP.md` and `.memory-php/` ARE MANAGER-ONLY FOR WRITING.**
⚠⚠⚠ **NO EDITS under `harness/`, `common/`, `patterns/`, `results/`, `pilot/`,
`common-php/`.**
⚠ **No `git add` / `git commit`.** Never touch `.web/` — a **concurrent
session** edits it.
⚠ Scratch under `.temp/php37/`. **`.temp/php36/` holds this row's build logs
including `logs-06-r3search.log` — REUSE it, do not re-derive what it has.**
⚠ **`grep -a` ALWAYS** (F35). **No `until … sleep` poller loops** — foreground
`sleep` is blocked; one tracked background job, wait for its notification.

**Bracket**: `harness/measure.py --check-stale` → **`66/0`** and
`harness-php/gate.py --tool measure --check-stale` → **`14/0`**, **first and
last**. ✅ **Both verified by the manager immediately before writing this file**,
so a first reading that is not `66/0` and `14/0` is **damage, and you should
stop and report rather than work around it.**

---

## §1 What this task is for

`ph45` publishes a **`fixed-R4 bound`** — `R3ship − R4ship`, R4 held fixed **by
fiat** — over an R4 endpoint **nobody has tried to move**. Until
`TASK_PHP_035` that debt looked cosmetic, because `ph07` and `ph16` both
searched their R4 side and found it **degenerate**. ⭐⭐ **F77 killed that
reading**: `ph29`'s `r4_fold_iter` verifies, is admissible, and is **5.63 pp
cheaper** than the shipped R4. **A bound over an unsearched endpoint is a bound
over a number nobody has tried to move.**

⚠⚠⚠ **AND ON THIS ROW THE PRIOR IS UNUSUALLY STRONG, WHICH IS WHY `ph45` GOES
FIRST.** `safe_tuned.rs`'s header records, measured, whole-program `Ir`:

    R2  safe_naive, no hoist                  98.07 M /  98.28 M
    c2  `&[u8; REQ]` around the scan  SHIPPED  79.51 M /  79.68 M
    R4  unsafe, `get_unchecked`                82.02 M /  82.30 M

⭐ **The shipped R3 is already CHEAPER than the shipped R4**, and the reason the
row gives is that *"the bound LLVM gets free from the TYPE is worth more than
the check it removes."* ▶ **That lever — resolve the work buffer to a
`&[u8; REQ]` whose length is a compile-time constant — was applied to R3 and
NEVER TO R4**, which still indexes the **512-byte arena** through
`get_unchecked`. **The most obvious candidate in this row is one nobody has
compiled.** ⚠ *That is a motivated hypothesis, not a result.* It may be a
pessimisation — three of R3's four candidates were, **and the obvious one was
the worst**. **Measure it; do not assume it.**

---

## §2 ⭐⭐⭐ F82 WIDENS THIS SEARCH, AND THIS IS THE PREMISE TO RE-DERIVE FIRST

The shared `why` block — **byte-identical in all six PHP rows and all 33 PAT
rows** — argues R4 admissibility from the identity pin:

> *"All six patterns pin `identity: unsafe == verus, O3 exact`, so an R4 is not
> merely a program that MAY use `unsafe`: it is a program that must have a
> byte-identical R5 twin that Verus verifies."*

⚠⚠⚠ **THAT ANTECEDENT IS FALSE ON THIS ROW.** `ph45` pins
`{"a": "unsafe", "b": "verus", "O0": "differ", "O3": "differ"}`, and the gate
**measures** `differ` at both levels. It is PAT-side boilerplate carried into a
programme where it does not hold (open item **61**).

▶ **So an R4 candidate on `ph45` need NOT compile byte-identically to its R5
twin. The binding constraint is only that the twin VERIFIES.** `ph45`'s R4
search is therefore **wider than `ph29`'s was**, and **F77's method — hunt for a
spelling whose Verus twin happens to compile byte-identically — is not the
constraint here.**

⚠⚠ **RE-DERIVE THIS BEFORE YOU RELY ON IT.** Read `ph45`'s `identity` pin out of
`spec.md` **and** the measured level out of `results-php/gate/ph45-htmlent-cache-int.json`,
and say what you found. ⚠ **If they disagree with this section, this section is
wrong and you should say so** — it is the manager's unreviewed work.

⚠ **This widens the ADMISSIBLE CLASS; it does not lower any other bar.** A
candidate still needs: `unsafe` genuinely used, a **verifying** R5 twin, **no
new trusted item**, **no `assume`**, **no `is not supported`**, and it must
satisfy the row's own `idiom` declaration. **Read the ERROR TEXT, not the exit
code** — `is not supported` disqualifies, `postcondition not satisfied` does
not.

---

## §3 Scope — four things, one gate run

⭐⭐ **THE COST STRUCTURE IS WHY THESE ARE BATCHED, AND I MEASURED IT RATHER THAN
ASSUMING IT.** `results-php/ph45-htmlent-cache-int.json`'s `source_sha256` has
**21 entries** and **`NOTES.md`, `spec.md` and `controls/*` are NOT among
them**, while `controls/*.py` **is** in the *gate* record's digest. So:

| edit | costs |
|---|---|
| add `controls/spellings.py` | **one gate re-run** |
| fix `NOTES.md` prose | **one gate re-run** |
| `controls/*.json` | **nothing** — `.json`/`.log` are excluded by design |
| ⛔ **edit `inputs/gen.py`** | **A FULL 32-CELL RE-MEASURE** |
| ⛔ edit any `.rs` or `c/*` | **A FULL 32-CELL RE-MEASURE** |

▶ **So items 58 and 59 and the owed prose all ride on ONE gate run** — which is
the lesson `TASK_PHP_033.md` learned by failing to: I told that task not to
touch `NOTES.md`, then found the owed entry would have been **free** inside the
re-gate it was already paying for.

### 3.1 ▶ THE SEARCH — `controls/spellings.py` + `spellings.json` (item 58)

To `ph29`'s conventions. **Search BOTH sides, and report the R4 side whatever it
says** — `ph07` and `ph16` found theirs **degenerate** and that was a result.

Required in `spellings.json`, because `check_control_json_pins` now reads the
**verdict** and not only the pin (TASK_164 item A):

* **`derived_from_sha256`** — the `{repo-relative path: sha256}` key. ⭐ **Prefer
  it over `gate_source_sha256`**, which reports `STALE` on a *prose fix* and so
  is the wrong key for anything deriving from a narrower set.
* `verus_checked`, `problems`, **`r4_endpoint_degenerate`** (`ph29`'s is
  `false` — the first in either programme), `identity_checked`,
  `headline_statistic`.
* Per variant: the spelling, `in_contract`, the fingerprint, instruction count,
  and its cost **against the shipped rung**.

⚠⚠ **`kernel_fingerprint` and `disasm` CARRY TWO REAL DEFECTS in `ph16`'s copy
and are GUARDED IN `ph29`'s** (F79, item 57): `disasm` ignored `objdump`'s
return code, so a **missing binary fingerprinted as the md5 of the empty
string** and *two missing binaries compared EQUAL on the one function whose job
is to decide byte-identity*; and the symbol needle was a **bare substring**, so
a crate named `nokernel` fingerprinted its own `main`. **Take `ph29`'s guarded
versions and write a negative for each.**

### 3.2 ▶ ITEM 59 — the `:193` overflow margin. ⛔ **READ-ONLY.**

`NOTES.md` §12b reports a signed overflow at `mbfilter_htmlent.c:193` —
`ent = ent*10 + (buffer[pos] - '0')` in `int` arithmetic, with `:225`'s
`strchr(html_entity_chars, c)` admitting **letters** — **inside the function
this row extracts**, untraced to any fix. F46 requires the row's benign corpus
be shown not to evaluate it.

✅ **The guard EXISTS and I verified it**: `inputs/gen.py::_check_span` refuses a
corpus whose `max_ent` exceeds `ENT_CEILING = INT_MAX // 100`, and it runs on
**`small.bin` and `large.bin`** — the measured inputs.
⚠⚠ **But the OBSERVED margin is in no committed record.** `_check_span` prints
`max |ent|` to stdout and nothing keeps it.

▶ **Compute `max |ent|` over the two SHIPPED benign inputs and put the number in
`NOTES.md` §12b.**
⛔⛔ **DO NOT EDIT `inputs/gen.py` AND DO NOT RUN IT.** It is in the
**measurement** digest (verified above) *and* it **rewrites `inputs/*.bin`** — so
either would cost a 32-cell re-measure, and a byte change would invalidate every
number the row publishes. ▶ **Write a separate read-only probe** under
`.temp/php37/` that imports or re-implements the decode and reads the shipped
`.bin` files. ⚠ **If your probe disagrees with `gen.py`'s logic, say so** — a
re-implementation that quietly differs is F52's shape.

### 3.3 ▶ THE OWED PROSE FIX — `NOTES.md` §8b understates its own result

§8b closes: *"⚠ That is offered as an observation on one row, not as a
correction to F74 — F74 is a 310-comparison result and this is one row with a
mechanism."*

⭐ **That caution was right at the time and the row was right to write it — and
the observation then BECAME the correction.** The manager took it up, measured
it across **366** comparisons, and **F74's rule is withdrawn in its published
one-condition form.** The corrected rule, **0 flips in 151 comparisons**:

> **(i) `min(inside_share)` over the two compared cells must be HIGH — family A
> must actually SEE both cells — AND (ii) `|Δinside_share| ≤ 0.02`.**

⚠ The threshold in (i) is **not tuned and six rows cannot pin it** (`>0.3`,
`>0.5`, `>0.6` all give 0 flips).

▶ **Update §8b to say that this row's observation is what refuted the rule, and
cite the corrected two-condition form.** ⚠ **Do not overstate it either**: the
row supplied the counterexample, the 366-comparison sweep is the manager's and
is **unreviewed**.

### 3.4 ▶ WHAT F82 ADDS TO THIS ROW, AND IT IS A CREDIT

⭐⭐ **`ph45` is the tree's SENSITIVITY CALIBRATION for family A, and it did not
know it.** A null control is **one-sided** — a statistic hard-wired to `0` would
ace every null in this tree — and F74 argued from nothing else. Because `ph45`
pins `differ`, its two kernels differ by a **known** static count, so family A
has a **predicted nonzero** value:

| row | input | Δnopad | Δ(A) | `n_iters` | `exec_rate` |
|---|---|---|---|---|---|
| **`ph45`** | `large.bin` | −2 | **−400** | 200 | **1.0000** |
| **`ph45`** | `small.bin` | −2 | **−3000** | 1500 | **1.0000** |
| `ph64` | `large.bin` | −1 | −102 | 200 | 0.5100 |
| `ph64` | `small.bin` | −1 | −764 | 1500 | 0.5093 |

▶ **Add this to `NOTES.md`**, re-derived: **family A resolves a 2-instruction
static difference to the instruction, on two inputs 7.5× apart in call count** —
and ⭐ **the shipped R5's kernel is 2 instructions SMALLER than the shipped
R4's**, i.e. **the proved rung is cheaper than the hand-written unsafe one, with
no search at all.** ⚠ Nothing is violated; the row pins `differ`.
⚠ **`exec_rate` of exactly `1.0000` is "too clean" and too-clean is the only
warning F52 gives** — `ph64`'s conditional path is the control, and **say so**.
⚠ **Re-derive from `results-php/`, do not transcribe this table.**

---

## §4 The statistic — and BOTH families, labelled

▶ **This row must publish BOTH families, labelled**, for **every** comparison.
`ph45`'s `inside_share` is **0.055–0.094** — *seven times more extreme than
anything else in the corpus* — so family A sees under 10 % of the cell and
**condition (i) of the corrected rule FAILS on every comparison on this row.**

⚠ Already in `NOTES.md` §8: A1 **+0.37 %** against whole-program **−3.06 %** —
**opposite signs.** ⚠ And §8c: the upstream fix is **68 613 `Ir` cheaper** than
the defect, which A1 reports as **`0.00 %`**, because the saving is in a
**callee**.

⚠⚠ **Two labelled quantities, never three. NO PAIR INTERVAL.**
`min(R3 found) − min(R4 found)` is **not** the repair — two upper bounds
differenced bound nothing in either direction.

---

## §5 Traps

1. ⚠⚠⚠ **`inputs/gen.py` IS IN THE MEASUREMENT DIGEST AND REWRITES THE
   INPUTS.** §3.2. This is the single most expensive mistake available in this
   task.
2. ⚠⚠ **Your headline and your gate are two separate claims, and only the gate
   record settles the second.** A task reported "built" while its gate was still
   running and that gate then failed **twice**. **Do not write a verdict you
   have not read out of `results-php/gate/`.**
3. ⚠⚠ **`ph45`'s gate verdict is `PASS-WITH-BLOCKED-ROWS`, not bare `PASS`**, and
   that is **correct** — one trusted item (`ent_table`) has no possible twin,
   the same verdict `p01` and `p35` carry. **Do not "fix" it.** ▶ Expect the
   same verdict after your run, with `failures []`.
4. ⚠⚠ **THE BACKTICK TRAP HAS NOW COST THIS PROGRAMME THREE ROWS** (F72, F76,
   and `_036`'s own `idiom.forbidden` over-pinning). **A backticked span in an
   explanatory sentence IS A PIN.** When you write prose that quotes a spelling
   in order to *discuss* it, **do not backtick it**. ⚠ And **F73**: a declared
   spelling containing a **character literal can never match**, because
   `exec_code` blanks char literals — so never backtick a span containing one.
5. ⚠ **`clang` is not on `PATH`**; use `harness/build.py:53`'s
   `~/tools/llvm/bin/clang`. `rustc` is `~/.cargo/bin/rustc`.
6. ⚠ **Declare your expectations before running each probe.** `_034` did and
   **the expectations caught two of its own errors** that *"would not have been
   visible from the output alone"*. This is F52's countermeasure and the single
   most valuable habit in the reports.
7. ⚠ **A must-fire case that fires for the WRONG REASON is worth nothing** —
   `_035`'s "false postcondition" negative returned the right verdict off
   `error: expected curly braces`, because `ensures` preceded `requires` and
   Verus would not parse it. **Assert the output carries a
   `verification results::` line.**
8. ⚠ **`~/tools/verus/vstd/std_specs/` is where specs for std types live**, and
   a `vstd/<mod>.rs` **trait declaration is not the specification**. That exact
   confusion has produced a false *"no spec exists"* claim **twice**. Grep the
   **inherent** spelling as well as the free one.
9. ⚠ **Do not bump the Verus/vstd pin** (`TOOLCHAIN.md`).
10. ⚠ **R4 searched is not R4 exhausted.** `ph29`'s honest claim is *"an
    admissible cheaper R4 exists"*, never *"this is the cheapest"*. ⚠ And the
    unroll factor is an **LLVM heuristic** — every number is about
    `rustc 1.97.1 / LLVM 22.1.6`. **Say so.**

---

## §6 Definition of done

1. `controls/spellings.py` **and** `controls/spellings.json`, to `ph29`'s
   conventions, with **§H negatives that must fire** — and say how many
   must-fire / must-not-fire cases, and whether any found a real defect.
2. **BOTH sides searched.** `r4_endpoint_degenerate` recorded either way,
   **with the evidence**.
3. `NOTES.md`: §3.2's margin, §3.3's correction, §3.4's calibration.
4. **`harness-php/gate.py ph45-htmlent-cache-int` GREEN**, verdict read **out of
   `results-php/gate/`**. Expect `PASS-WITH-BLOCKED-ROWS`, `failures []`.
5. Both brackets, **first and last**. ⚠ **Expect `66/0` and `14/0` UNCHANGED** —
   nothing in this task's scope is in a measurement digest. **If the php figure
   moves, you have staled a measurement and must say so.**
6. ⚠ **`controls_json` currently reads `{}` for this row.** ▶ After your run it
   should carry `spellings.json`. **Read it out of the record and quote it.**
7. ⭐ **Anything contradicting this file — say so.** §2's premise and §3's cost
   table are the manager's own work; §2 is the part carrying the most weight and
   §3.2 is the part where being wrong is most expensive. ⚠ **§2, §3.4 and the
   corrected F74 rule are all UNREVIEWED (rule 9).**
