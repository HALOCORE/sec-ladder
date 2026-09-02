# TASK_164 — the owed gate bundle: FOUR `check.py` items, ONE 33-pattern re-gate

**Role: research engineer.** ⚠⚠ **You are the only agent running.** You own
`harness/check.py`. Nobody else touches it while you work.

Read first: `PROTOCOL.md` (**rules 6, 13, 14** especially);
`.memory/03-measurement.md` entries **19** and **23**; `RECAP.md`'s START HERE
box and its **Immediate queue items 26 and 30**; `.tasks/TASK_156_REPORT.md`
**§7 minors 2 and 3** (where items A and B were first reported);
`.tasks/TASK_151.md` (**the precedent for landing a gate bundle with must-fire
arms**).

---

## ⚠⚠⚠ THE BUDGET, AND IT IS DERIVED RATHER THAN GUESSED

**ONE 33-pattern re-gate. ZERO re-measures. ZERO `report.py` runs.**

Manager-verified before writing this file, because rule 14 says to run the
premise:

```
harness/check.py's gate `srcs` list (check.py:9198)  includes glob('harness/*.py')
  -> editing check.py stales EVERY gate record -> 33-pattern re-gate
harness/measure.py::measurement_sources (measure.py:224)  does NOT include check.py
  -> ZERO re-measures
no item below touches any patterns/*/spec.md `slb-contract` fence
  -> `contract_sha256` does not move -> no report.py, no second gate
```

⚠ **That last line is the one to check rather than trust.** If any item you land
moves a `contract_sha256`, the published tables go stale, `report.py` cannot run
before a gate, and the bundle costs **two** sweeps (`TASK_156` §8 measured
exactly that). **If that happens, STOP AND REPORT before running the second
sweep.**

⚠ **Do the sweep ONCE, at the end, with all four items landed.** A `check.py`
edit mid-sweep invalidates every record already written (queue item 26 says so
in terms).

---

## A. ⚠⚠⚠ STAGE 9b HASHES A SIDECAR AND NEVER READS ITS VERDICT

`check.py::check_control_json_pins` (stage `9b`, `check.py:8351`) reads
`derived_from_sha256` and `gate_source_sha256` **and nothing else**. It answers
*"were these numbers taken against this tree?"* and never *"what did the control
conclude?"*

**Manager-measured on the tree as it stands, not quoted from the report:**

```
tracked patterns/*/controls/*.json                    46
  ...carrying a `problems` key   (a verdict)          30    ALL EMPTY today
  ...carrying an `invariant` key (the prose claim)    41
  ...carrying `measured_utc`                          41    read by NOTHING
  ...that pin THEMSELVES in derived_from_sha256        0    <-- the hole
  ...that pin their own generator .py                 45 of 46
generators writing a `problems` key                   30
  ...of which exit NON-ZERO when it is non-empty      30 of 30   <-- unanimous
`grep -rn 'problems\|invariant\|measured_utc' harness/ synthesis/`
  -> zero reads of any sidecar verdict field
```

✅ **`problems` is unambiguously a VERDICT, not a note field: 30 of 30
generators exit 1 on it.** So `rep.fail` is the correct disposition and not a
judgement call. ⚠⚠ **And because 0 of 46 sidecars pin themselves, editing
`problems` from `[]` to `["the control failed"]` moves NOTHING stage 9b hashes
— the stage prints `FRESH` and the gate stays green.**

**There is a SECOND unread verdict field and the report did not name it:**
`controls/proof_mutants.json` carries `summary: {"n": 9, "as_expected": 9}` on
**5 of 7** proof-mutant sidecars (`p28` 7/7, `p29` 10/10, `p32` 8/8, `p34` 6/6,
`p49` 9/9; `p25` and `p35` carry `summary: null` and use other shapes). **A
battery that regressed to `as_expected: 7` of `n: 9` reads `FRESH` today.**
That is the *"regenerated at 7/9"* case `RECAP` names, and it is a different
field from `problems`.

✅ **Land:** stage 9b reads the verdict as well as the pin.

- **non-empty `problems`** → `rep.fail`, naming the sidecar and quoting the
  entries. **It fires on zero sidecars today**, so the sweep proves nothing on
  its own — hence the arm below.
- **`summary` with `as_expected < n`** → `rep.fail`, same shape.
- ⚠ **Decide and JUSTIFY the disposition for a sidecar with NO verdict field at
  all.** The stage's own docstring already argues the principle for the pin
  (*"a red gate nobody can clear is how gates get switched off"*), so a `SHOUT`
  is the shape that matches; but 16 of 46 sidecars carry no `problems` and some
  of those genuinely have nothing to report. **Say which you chose and why, and
  do not silently make it a fail.**
- ⚠ **Do NOT invent a third convention.** Read what the 46 files actually do
  first; the two above are what the tree uses.
- ⚠ **`measured_utc` and `invariant` are NOT part of this item** — an unread
  timestamp is untidy, not unsound. **Report on them; do not wire them in.**

### ⚠⚠ A's must-fire arm — and this is the whole point of the item

`_ASSUME_CASES` (`check.py`, checked in `check_selftests`) is the shape to copy:
a `(label, got, want)` table evaluated on **synthetic in-memory documents**,
run on **every** invocation, precisely because the repair is **prospective** —
no shipped sidecar has a non-empty `problems`, so a green 33-pattern sweep says
**nothing** about whether the check can fire.

**The arm must include, at minimum:**
1. a doc with non-empty `problems` → **must FAIL**;
2. a doc with `summary {n: 9, as_expected: 7}` → **must FAIL**;
3. a doc with `summary {n: 9, as_expected: 9}` → **must be silent**;
4. a doc with `problems: []` → **must be silent**;
5. ⚠ **a doc whose `problems` is a STRING or a number rather than a list** —
   decide what that means and pin it, because a generator typo must not read as
   "no problems";
6. ⚠ **`got[0] == "RAISED"` semantics**: a malformed doc must be **REPORTED,
   not CRASH** the gate (`.memory/03-measurement.md` entry 19).

⚠⚠ **Refactor the verdict logic into a pure function the arm can call
directly.** An arm that reaches it only through a full stage cannot be run
in-process on every invocation, and an arm that is not run is not an arm.

---

## B. ⚠⚠⚠ `global` DIRECTIVES ARE INVISIBLE TO `axiom_decls` — AND THE PUBLISHED COUNT IS WRONG TWICE

`harness/vparse.py::axiom_decls` matches five body-less trusted forms —
`axiom fn`, `uninterp spec fn`, `assume_specification`,
`external_trait_specification`, `external_type_specification`. **A `global`
directive is a sixth and nothing in `harness/` mentions it.**

### ⚠⚠ THE MANAGER PUBLISHED *"live on FOUR patterns (`p28` `p29` `p32` `p34`)"* AND IT IS WRONG IN BOTH DIRECTIONS

Re-derived by the manager with `vparse.blank_noncode` — i.e. **comments
blanked**, which is what the original `grep -l` did not do:

```
global layout   p28 p29 p34                                    3 patterns
global size_of  p10 p19 p22 p36 p38 p46 p47                    7 patterns
union                                                         10 of 33
axiom_decls sees: 0 of either, on every one of the 10
```

- ⚠⚠ **`p32` DOES NOT HAVE ONE.** `patterns/p32-free-list-pool/verus.rs:17` is a
  **comment saying the pattern has NO `global layout`**, and `p49`'s line 29
  says the same thing. A `grep -l` counted a **negation as an instance**. That
  is `TASK_156`'s reviewer's error and the manager copied it into `RECAP` and
  into this bundle's scope without re-running it. **It is the same failure this
  session has now made repeatedly: reading a value out of the wrong column.**
- ⚠⚠ **AND IT UNDERCOUNTS.** `global size_of usize == 8;` is the same
  construct — a `global` directive, body-less, trusted, invisible to
  `axiom_decls` — and it is live on **seven more patterns**. **The exposed
  surface is 10 of 33, not 4.**

### ⚠⚠⚠ THE CALL I AM LEAST SURE OF, AND THE ONE I WANT YOU TO ATTACK

**Are `global layout` and `global size_of` the same thing for this purpose?**

My belief, and I want it measured rather than accepted: **yes for visibility,
and possibly no for risk.** `global layout Obj is size == 24, align == 8;` is a
claim about a **project-local type** that the author writes by hand.
`global size_of usize == 8;` is a claim about a **target fact** that is true on
this box and would be false only on a 32-bit target. Those are different
exposures even though the construct is identical.

✅ **Settle it with a run, not an argument.** The single measurement that
decides it:

- write a minimal `verus!` file declaring a **FALSE** `global layout` (say a
  6-byte struct declared `size == 24`) and verify it with `./verus_run.py`,
  single-file mode. **Does Verus report `N verified, 0 errors`?**
- do the same with a **FALSE** `global size_of usize == 4;`.
- ⚠ **Then check what rustc does at CODEGEN in each case**, because
  `TASK_156` claims rustc is the net and that it *"fires even on a
  never-constructed type"* — **that half was measured by the reviewer and is
  worth re-deriving, since the whole defensibility argument rests on it.**
- ⚠ **Report whether a `global` directive can be made to prove something FALSE
  about the program's behaviour**, or only to be rejected at codegen. If it is
  the latter on both forms, say so plainly — ***"the net holds"* is a finding,
  not a reason to skip the visibility fix.**

✅ **Land the visibility fix regardless of how that measurement comes out.**
`axiom_decls`' own docstring states the design: **visibility, not
prohibition**, and over-counting is the safe direction *"for a mechanism whose
job is visibility"*. The gate should **see** all 10.

⚠ **Whichever way you settle `size_of` vs `layout`, the record must
distinguish them** — a `kind` that says which, so a later reader can count
either without re-deriving this.

⚠⚠ **DO NOT WIDEN `vparse.parse()` TO DO THIS.** `axiom_decls`' docstring
records the measurement: deleting `parse()`'s `if body_open is None: continue`
makes `by_name` raise on `p36`, whose trait method declarations are body-less
too, taking a green pattern to six FAILs. **Keyword-keyed detection in
`axiom_decls`, the way the other five forms are done.**

### B's must-fire arm

`vparse._selftest()` already runs inside stage 0 and already carries
`axiom_decls` cases (`check.py:867` fails the gate on a non-zero return).
**Add there**, and the arm must pin **both directions**:

1. a `global layout` inside `verus!` → **counted**, with its own `kind`;
2. a `global size_of` inside `verus!` → **counted**;
3. ⚠ **`global` in a COMMENT → NOT counted.** This is the arm that would have
   caught the `p32` error, so it is not optional, and `p32`/`p49`'s real
   sources are the live negative controls;
4. ⚠ a `global` inside a **string literal** → not counted;
5. an unreadable/truncated `global` line → **counted with `name='?'`**, never
   invisible (that is the existing convention for the other forms).

⚠ **Then re-derive the 10-pattern census with the SHIPPED code** and paste it.
If your census disagrees with mine, **yours wins and say so.**

---

## C. ⚠⚠ `check_marginal_ir`'s DOCSTRING KNOWS ONE MECHANISM AND THERE ARE TWO

`check.py:2799`. `RECAP`'s START HERE box says this docstring *"leads with
`±0.20` and warns of `±7` against a measured `269.52` at `-O3 isolated`"`.

⚠⚠ **THAT SENTENCE IS THE MANAGER'S AND IT CONFLATES TWO DIFFERENT
QUANTITIES. Do not repeat it.** Having read both, here is what is actually
true, and it is the thing to land:

| | mechanism | magnitude | cell |
|---|---|---|---|
| what the docstring documents | the **environment block** shifts the stack pointer → a per-call stack array's alignment → a different tail in `__memset_avx2_unaligned_erms` | `±0.20` (p08), `±7` per stack array (p03/p04/p38/p46) | drift **between runs of the same build** |
| what it does NOT document | `marginal_ir_per_call` is a **whole-program slope**, so it includes everything the kernel calls — glibc malloc internals above all | **`269.52`** on `p25`, `1732.73` on `p28` at `-O0` | the **R4/R5 gap within ONE run**, on a pair `identity` pins to `exact` |

**These are not the same effect and the docstring's uncertainty budget is drawn
entirely from the first.** `.memory/03-measurement.md` entry **23** is the
authority for the second, and it also records that `check.py:2805` is one of
three places already documenting the whole-program reading — so the docstring
half-knows this and never joins it to a number.

✅ **Land:** the second mechanism, its per-cell table, and the consequence.

- ⚠⚠⚠ **QUOTE ENTRY 23's PER-CELL TABLE AND NEVER A MAX.** *"A null is a
  property of a CELL. Do not max it over mode, over level, or over input."*
  The manager got that table wrong **three times, the same way each time**, by
  maxing across a dimension that matters. **`p28 1732.73` and `p29 425.80` are
  `-O0` cells and must never appear under an `-O3` heading.**
- ⚠⚠ **AND `whole` IS NOT A NULL AT ALL** — `check_identity` compares
  `isolated` digests only, so at `p11`'s `O3/whole` cell there is no `kernel`
  symbol and the difference is `unsafe::main` vs `verus::main`. Say that where
  a reader will hit it.
- ✅ **The consequence, which is the operative sentence:** *for a cross-RUNG
  comparison use `kernel_exclusive_ir`; use `marginal_ir_per_call` for
  anti-collapse, which is what it was built for.* The docstring currently says
  a narrower version of this **naming only `p03` and `p04`**, on the strength
  of the ±7 mechanism. **Widen it to the rule and name entry 23.**
- ⚠ **Correct the stale scope line while you are in there:** the docstring's
  own census block is dated `2026-08-22` over **24 patterns** and the tree has
  **33**. **Do NOT re-take the census — it costs ~90 minutes and nothing here
  needs it.** ✅ **Date it and state the denominator honestly**, the way the
  paragraph above it already demands (*"quoted as a measurement — with its
  instrument, its date and its denominator"*).

### ⚠ C OWES NO MUST-FIRE ARM, AND THAT IS A DECISION, NOT AN OVERSIGHT

C is documentation. There is no behaviour change, so there is nothing that can
fire. **What C owes instead: every number you write into it must be re-derived
from `results/*.json` and pasted, not copied from entry 23.** Entry 23 is the
manager's table and the manager has been wrong about it three times. ⚠ **If any
figure you re-derive disagrees with entry 23, that is a finding — report it and
do NOT edit `.memory/`.**

---

## D. ⚠⚠ THE `copy_from_slice` FALSE CLAIM IS STILL ALIVE IN `check.py` — THIRD SITE, AND THE WORST ONE

`RECAP` **Immediate queue item 26**, still live, manager-verified today:

```
check.py:6187  "(there is no vstd spec for `copy_from_slice`, so a bulk-copy
                twin is not available -- `.memory/04-verus.md`)"
~/tools/verus/vstd/std_specs/slice.rs:205
               pub assume_specification<T: Copy>[ <[T]>::copy_from_slice ]
                   (dst: &mut [T], src: &[T])
```

⚠⚠ **This is the site an engineer reads WHILE BEING TOLD TO WRITE A TWIN**, so
it is the site most likely to cause the error a third time. `CLAUDE.md` records
this exact claim as having stood from `TASK_004` to `TASK_048`;
`patterns/p02-buffer-copy/NOTES.md:692` already carries the correction and the
gate's own explanation of its rule does not.

✅ **Fix the sentence, and check the surrounding argument still holds** — the
twin mechanism's justification may or may not depend on the claim. ⚠ **If a
bulk-copy twin IS now available, say what that would cost and whether `p02`
should have one; report it, do not build it.**

⚠ **Also sweep `harness/` for the same claim elsewhere.** `.memory/04-verus.md`
is cited as the authority in that parenthesis — **check whether `.memory/`
still says it**, and if it does, **report it; the manager owns `.memory/`.**

---

## E. ⚠ ONE QUEUE ITEM IS ALREADY DONE — CONFIRM AND SAY SO

`RECAP` queue item 30 closes with *"Adjacent and NOT fixed:
`patterns/p01-array-sum/spec.md` still carries `| identity | recorded as a
**result**, not a gate condition` — bundle it with the next thing that
re-gates p01."*

**Manager-checked: it is already fixed.** `patterns/p01-array-sum/spec.md:82`
reads *"recorded as a **result** *and* enforced"*, and it sits at line 82
against a fence opening at line 84 — **outside `slb-contract`**, so it never
cost a `contract_sha256` move either. **Confirm both halves and report**; the
manager will retire the queue item.

---

## ⚠ NOT in this task

- **`.memory/`, `RECAP.md`, `results/SYNTHESIS.md`, `harness/tools/composition.py`**
  — the manager owns them. **Report what needs changing; change nothing.**
- **The Results gap** — `results/SYNTHESIS.md`'s four Results were drawn from 26
  kernels against a 33-pattern tree. **That is the NEXT task and it is
  substantive research, not cleanup. Do not touch it.**
- **`synthesis/outward_ir.json`** is stale against 26 patterns (352 callgrind
  runs to re-emit). **Not here.**
- **Re-taking the ±7 environment census.** ~90 minutes and nothing needs it.

## Then, in this order

1. **All four items landed**, arms in place.
2. **Run the arms alone first** — `harness/check.py p01` reaches stage 0, which
   is where A's and B's arms live. ⚠ **Confirm each arm FAILS when you break the
   thing it guards**, by breaking it on purpose and pasting the failure. **An
   arm nobody has seen fail is not an arm** (`TASK_151`'s standard, and the
   `axiom_decls`/`synthesis.md` tautology in `RECAP`'s trap 2 is why).
3. **THEN the 33-pattern sweep**, once, in the background, waiting on the exact
   PID. ⚠ **A single pattern can take 30+ minutes.** Log per pattern.
4. `harness/measure.py --check-stale` — ⚠ **it prints GATE PLUS MEASUREMENT: 66
   examined against 33 measurement records; a commit message has already
   misread that.**
5. `harness/tools/composition.py --check` · `harness/tools/temp_citations.py` ·
   `python3 synthesis/licence.py --emit synthesis/licence.json` (⚠ **`--emit`
   TAKES A PATH**; bare `--emit` exits 2) · `python3 synthesis/synthesize.py`.
6. ⚠⚠ **CHECK EACH SCRIPT'S OWN EXIT STATUS, NOT A PIPELINE'S OR AN `echo`'s.**
   The manager committed on a FAILING `temp_citations.py` this session by
   chaining `&&` from an `echo`, and separately misread `rc=$?` after a pipe.
   **Three instances, one cure: read the status of the thing you ran.**

## Rules

- `.temp/t164/` for scratch. ⚠ **Do not touch any earlier `.temp/t*/` or
  `.temp/mgr*/`** — cited evidence. **No `git add`/`git commit`.**
- ⚠ **Expected verdicts, so you can tell a regression from the baseline:**
  `30 PASS + 3 PASS-WITH-BLOCKED-ROWS`, 0 failures, `blocked` = `p01` 1,
  `p35` 3, `p42` 1. ⚠ **`p42`'s may legitimately be 2** — the Miri slowdown is
  selected by the ENVIRONMENT, not by the gate. **Do not read that as a
  regression.**
- ⚠⚠ **Read `blocked`/`verdict` out of the RECORD, never `grep` the log.**
  `grep -c BLOCKED` matches the verdict string `PASS-WITH-BLOCKED-ROWS` and
  decodes as `2N+1`; `grep -oE 'PASS|FAIL'` reports `PASS-WITH-BLOCKED-ROWS`
  as `PASS`.
- ⚠⚠ **DO NOT LEAVE A `pgrep -f` WAITER RUNNING** — a waiter's own command line
  contains the string it greps for, so its exit condition can never be true,
  and the enclosing tool `bash -c` matches too. **Use `wait <pid>` or a `.done`
  sentinel** (`.memory/00-environment.md`).
- Verus via `./verus_run.py`, **single-file mode, never `--cargo`**.
- Hand-run sanitisers need `env -u LD_PRELOAD`; never truncate a sanitiser log
  with `head`.
- ⚠⚠ **`../LearnVeri/` IS ANOTHER PROJECT'S REPOSITORY — READ ONLY.**
- **Keep the generator, delete the artefact.** A generator that edits source by
  string substitution **MUST ASSERT ITS SUBSTITUTION COUNT**.
- ⚠ **If any item costs more than this file says, STOP AND REPORT** rather than
  absorbing it.
- Report to `.tasks/TASK_164_REPORT.md`. **Write the file before citing it.**

**PROTOCOL rule 2 running count: launched from 925**
(`.tasks/TASK_163_REPORT.md`'s closing paragraph). Carry it forward.
⚠ **Reconciliation across branches is the manager's job, not yours.**

⚠⚠ **The manager has been refuted in every one of the last nine tasks, and
this file already contains one self-refutation (`p32` has no `global layout`;
the published *"four patterns"* was a `grep` that matched a comment).
The call to attack is B's — *is `global size_of` the same exposure as
`global layout`?* I have asserted they are the same for VISIBILITY and
different for RISK, on a source read with NOTHING RUN. That is exactly the
shape of the two axis proposals `RECAP` records as refused for the same
reason. Measure it.**
