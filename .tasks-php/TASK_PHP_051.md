# TASK_PHP_051 — ROW 10: `ph56`, **T5's SECOND ROW, WHICH CLOSES THE FAMILY** — and the catalogue is WRONG about its harm

**Role:** research **engineer**. **One agent, alone.**
**Report:** `.tasks-php/TASK_PHP_051_REPORT.md` — **write the FILE** (rule 10).

---

## §1 Why this row

**It closes `T5` at 2 of 2** — `quota.py`'s floor is *min 2 per family* — so it
takes the corpus from **9 built / 31 owed** to **10 / 30** and turns the 7th
family from `OWES 1` to `CLOSED`. ⭐ **No other candidate is this cheap**: 2004,
**one file**, **three-line fix**, and the scaffolding `ph55` just built.

⭐⭐ **AND IT PAIRS WITH `ph55` INTO A RESULT NEITHER ROW HAS ALONE.** Both are
*"the emitted program is not the one the executor expects"*; **both upstream
fixes are THE SAME THREE-LINE SHAPE — a guard that already exists elsewhere in
the same function, copied onto the arm that lacks it** — ⛔ **and the two HARMS
are completely different.** ▶ **Say so explicitly in `NOTES.md`; it is the
family-level finding and it is the crash course's paragraph.**

---

## §2 The manager's decisions, and the facts behind them

### 2.1 ⭐⭐⭐ THE MECHANISM, VERIFIED ON THE PRISTINE TARBALL — you are building, not re-deriving

⚠ **Rule 14: a premise in a task file is one an engineer has no reason to doubt,
so the manager measured every one of these** from the pinned tarball
(`sha256 5783e0c0…`). **Re-read any you depend on.**

**`Zend/zend_compile.c`, `zend_do_end_variable_parse` (opens `:736`), `:751-776`:**

```c
751  switch (type) {
752    case BP_VAR_R:
753      if (opline->opcode == ZEND_FETCH_DIM_W && opline->op2.op_type == IS_UNUSED) {
754        zend_error(E_COMPILE_ERROR, "Cannot use [] for reading");      /* GUARD */
755      }
756      opline->opcode -= 3;   break;
758    case BP_VAR_W:            break;                     /* the base, no delta */
760    case BP_VAR_RW:  opline->opcode += 3;  break;
763    case BP_VAR_IS:  opline->opcode += 6;  break;        /* ⛔ NO GUARD — THE BUG */
766    case BP_VAR_FUNC_ARG: opline->opcode += 9; opline->extended_value = arg_offset; break;
770    case BP_VAR_UNSET:
771      if (opline->opcode == ZEND_FETCH_DIM_W && opline->op2.op_type == IS_UNUSED) {
772        zend_error(E_COMPILE_ERROR, "Cannot use [] for unsetting");     /* GUARD */
773      }
774      opline->opcode += 12;  break;
776  }
```

**The arithmetic is real and the strides land on real opcodes**
(`Zend/zend_compile.h:640-656`):

| | `DIM_R` | `DIM_W` | `DIM_RW` | `DIM_IS` | `DIM_FUNC_ARG` | `DIM_UNSET` |
|---|---:|---:|---:|---:|---:|---:|
| opcode | **81** | **84** | **87** | ⛔ **90** | **93** | **96** |
| delta from `W` | `−3` | `0` | `+3` | **`+6`** | `+9` | `+12` |

ⓘ **The stride is 3 because each access mode has three members** — `DIM`, `OBJ`
and a third (`82 FETCH_OBJ_R`, `85 FETCH_OBJ_W`, `88 FETCH_OBJ_RW`, `91
FETCH_OBJ_IS` …). **The `+= 3` arithmetic walks between MODES, not members.**

### 2.2 ⛔⛔⛔ THE CATALOGUE'S `⚠ risk` NOTE IS **WRONG**, AND THE REAL HARM IS BETTER

`patterns-php/CATALOGUE.md` says: *"the executor must have **no handler** for the
illegal combination — an extraction with a total dispatch table has removed the
harm."* ⛔ **Both halves are false, and the manager checked rather than assuming:**

1. **THERE IS A HANDLER.** `Zend/zend_execute.c:4385` —
   `zend_opcode_handlers[ZEND_FETCH_DIM_IS] = zend_fetch_dim_is_handler;` — and
   the handler at `:2075-2080` is three lines.
2. ⭐⭐⭐ **THE HARM IS A REFCOUNT MUTATION OF A PROCESS-GLOBAL ZVAL, REACHED
   FROM AN OPERATION THAT IS SUPPOSED TO BE SIDE-EFFECT-FREE.**
   `zend_fetch_dimension_address` (`:896`), the `IS_ARRAY` arm at **`:935-943`**:

```c
935  if (op2->op_type == IS_UNUSED) {
936      zval *new_zval = &EG(uninitialized_zval);      /* a GLOBAL SINGLETON */
937      new_zval->refcount++;                          /* ⛔ on the global */
938      if (zend_hash_next_index_insert(container->value.ht, &new_zval, …) == FAILURE) {
940          zend_error(E_WARNING, "Cannot add element to the array …");
```

▶ ⛔⛔ **So `isset($a[])` on an ARRAY container APPENDS AN ELEMENT and takes a
reference to `EG(uninitialized_zval)` — `isset` MUTATES the array and bumps the
refcount of a process-global.** That is why the bug is titled *"isset crashes on
arrays"*.
⭐ **And the STRING container IS guarded** — `:963-964` gives
`zend_error(E_ERROR, "[] operator not supported for strings")`. **Arrays are the
unguarded container type, which is exactly what the bug title says.**

⚠⚠ **WHAT THE MANAGER DID *NOT* VERIFY, STATED SO YOU DO NOT INHERIT IT:** I read
the code; **I did not run it.** ▶ **DELIVERABLE #0: establish the harm end to
end** — that the refcount on the shared global goes **unbalanced**, and what the
observable consequence is (premature free? a later `zval_ptr_dtor` on a global?).
⭐ **If the harm turns out to be *"the array silently grows and `isset` returns a
value for an element it just created"* — a pure logic defect with no memory
error — THAT IS A FINDING AND THE ROW STILL STANDS** (`CLAUDE.md` rule 6;
`ph55`'s second input is exactly that shape and it is the row's best result).

⭐⭐ **EITHER WAY THIS IS A DIFFERENT HARM FROM `ph55`'s**, which is a **NULL
indirect call** through a null dispatch slot. ▶ **Two rows, one family, one fix
shape, two harms. Name that in `NOTES.md`.**

### 2.3 ✅ THE R1h IS `1e708a5aeb30`, THREE LINES, AND **`git apply` SHOULD WORK** — the opposite of `ph55`

```
Marcus Boerger, Sun 29 Aug 2004, "Bugfix #29882 isset crashes on arrays"
 Zend/zend_compile.c | 3 +++

@@ -763,6 +763,9 @@ void zend_do_end_variable_parse(int type, int arg_offset TSRMLS_DC)
 				opline->opcode += 3;
 				break;
 			case BP_VAR_IS:
+				if (opline->opcode == ZEND_FETCH_DIM_W && opline->op2.op_type == IS_UNUSED) {
+					zend_error(E_COMPILE_ERROR, "Cannot use [] for reading");
+				}
 				opline->opcode += 6; /* 3+3 */
 				break;
 			case BP_VAR_FUNC_ARG:
```

⭐⭐ **THE FIX IS `BP_VAR_R`'s GUARD COPIED ONTO `BP_VAR_IS`, ERROR MESSAGE AND
ALL** — *"Cannot use [] for reading"*, the same string. **Nothing is invented**,
exactly as `ph55`'s fix was the normal exit's own three lines.

⭐ **AND THE HUNK HEADER IS `@@ -763,6 +763,9 @@` — THE SAME LINE NUMBER AS
5.0.0's `:763`**, with context matching the pristine file. The fix is
**2004-08-29**, six weeks after 5.0.0 shipped, and this function had not drifted.
▶ **PREDICTION, REGISTERED: `git apply` SUCCEEDS on this row, where it FAILED on
`ph55`.** ⛔ **Verify it; do not assume it.** ⚠ `_048` §4d found that
**`git apply --check` returns 0 on a gitignored path** — read that section before
trusting an apply check.

### 2.4 ⭐ THE PRE-IMAGE SCREEN IS **STRONG HERE**, UNLIKE ON `ph55`

`preimage_screen.py --id CRASH-041` → **`CANDIDATE`**, `hits [[763, "case
BP_VAR_IS:"]]`, `misses []`, `n_matchable 1`, `n_dropped 0`.
⭐⭐ **`case BP_VAR_IS:` occurs EXACTLY ONCE in `Zend/zend_compile.c`** (manager
counted). ▶ **So the `1/1` is genuinely discriminating**, where `ph55`'s matched
`NEXT_OPCODE();` — **117 occurrences** — and confirmed almost nothing.
⭐ **Quote the screen here. That contrast is worth one sentence in `NOTES.md`:
the same tool, the same verdict string, and completely different evidential
weight, decided by the uniqueness of the cited line.**

### 2.5 ⚠⚠ THE OPEN QUESTION THE MANAGER COULD NOT SETTLE — **FOUR ARMS LACK THE GUARD, ONE IS A DEFECT**

`BP_VAR_W`, `BP_VAR_RW`, `BP_VAR_IS` and `BP_VAR_FUNC_ARG` all lack it; only
`BP_VAR_IS` was fixed. ▶ **WHY?** Candidates: `$a[] = 1` (**`W`**) is *legal* and
is the whole point of `[]`; `$a[] += 1` (**`RW`**) and `f($a[])` (**`FUNC_ARG`**)
may be legal, guarded elsewhere, or **uncaught siblings.**
⛔⛔ **THIS IS F50/F58's CENSUS CHANNEL AND IT IS THE FIRST QUESTION THIS ROW
SHOULD ANSWER**, because `ph55`'s census came back **empty** and a non-empty one
here would be a finding about the catalogue, not about the row.
⭐ **`ph55` is the precedent for how to do it**: read each sibling arm's full
path, do not reason from the shape.

### 2.6 TIER, STATISTIC, AND THE PREDICTIONS

* **TIER** — the catalogue says `narrowed`. ⚠ **That is a mining-wave label and
  `ph55` REFUTED its own.** ▶ **Declare what you measured.**
* ⭐⭐⭐ **`inside_share` PER CELL FIRST, then choose.** ⛔ **A HIGH SHARE IS NOT
  A CERTIFICATE** — `ph55`'s C cells are **74–83 %** and A1 still reads
  `0.000 %` on its own defect site, because what matters is whether **the
  DIFFERENCE** lands inside the symbol. `.memory-php/03-numbers.md`.
* ⛔⛔ **EVERY PERCENTAGE OWES FIVE THINGS: STATISTIC · INPUT · OPT/MODE · BASE ·
  and if the base is a C cell, WHICH COMPILER — with BOTH C columns** (F108).
  **Never quote an `O0` figure as a performance result.** ▶ Run
  `.tasks-php/cbaseline_check.py --ratchet` before finishing; **adjudicate any
  new hit BY HAND, never widen the regex.**
* ⛔⛔⛔ **NEW, AND IT BINDS ANY FAMILY-B FIGURE YOU PUBLISH:
  `PROTOCOL_PHP.md` §B5.** A family-B difference is publishable **iff the two
  cells have a measured step of `0.00 Ir/call` over a full 32-residue `argv` pad
  sweep**, or clear it by the stable ratio. ▶ **`.tasks-php/php50_align_sweep.py`
  does this — no build, no gate, minutes.** ⚠ **Report TWO verdicts per pair:
  *magnitude resolvable?* and *sign stable?*** ⓘ The step is **not** a constant —
  corpus-wide it takes `0.00`, `0.02`, `7.00` and `34.49`.
* **PREDICTIONS, REGISTERED** — ⚠ `ph55` refuted **four of five** and `ph52` five
  of my statements; **that is the expected yield.**
  1. **`git apply` SUCCEEDS** (§2.3).
  2. **Stage 5c-twin passes cleanly, no hatch, no blocked row** — this row has no
     `MaybeUninit`, so F97's collision should not recur. ⭐ `ph55` upheld the same
     prediction at `n_twins = 8`.
  3. **The R1h costs ~nothing at run time** — the guard is in the **COMPILER**,
     not the executor, so it runs once per emitted opline and not per execution.
     ⛔ **If the kernel models compile-and-run in one loop, say so, because then
     the prediction is about your harness and not about PHP.**

---

## §3 Traps

1. ⛔⛔⛔ **A LIVENESS CHECK MAY NOT BE TRUNCATED, AND MAY NOT MATCH ITSELF**
   (item **113**, both halves earned the hard way). `pgrep` feeding a decision
   gets **no `head`, no `tail`** — a truncated one hid a live process and **raced
   `ph55`'s gate against itself**, two runs sharing a scratch dir and reporting
   *different* failures. And a `pgrep` guard that **matched its own launcher**
   span forever. ▶ **Confirm `/proc/<pid>/cmdline` for an exact PID; best of all,
   need no `pgrep`.** ⛔ Never `pkill`/`killall`/substring-match.
2. ⚠⚠⚠ **`grep -a` ALWAYS** (F35). A line-grep misses a phrase that wraps.
3. ⛔⛔ **A BACKTICK IN AN `idiom.required`/`forbidden` ENTRY IS A PIN** (item
   100, three instances in three tasks). **Run `spellings.py --audit-only` on any
   contract prose BEFORE quoting it, and read the output.**
4. ⛔⛔ **§H: a validator lands with its must-fire negatives INSIDE it**, feeding
   `problems` so stage 9b sees them. ⚠ **Never in gitignored `.temp/`.**
   ⭐ **If a checker is a grep, ADJUDICATE hits by hand and ratchet.**
5. ⛔ **F101 / item 109 — `kernel_fingerprint` is PATH-SENSITIVE and fired LIVE
   in BOTH directions on `ph52`.** ▶ Clone `ph52`/`ph55`'s repair: fixed-width
   `vNN` slug, asserted equal-path-length invariant, `asm.py::identity_level`.
6. ⚠ **A comment is not code.** Test behaviour, not text.
7. ⚠⚠ **A `c/*` COMMENT MAY POINT AT AN ARGUMENT; IT MAY NOT STATE THAT
   ARGUMENT'S VERDICT** (`PROTOCOL_PHP.md` §F6a). ⛔ **`ph55` shipped one anyway
   — *"`preimage_screen.py`'s own verdict is `CANDIDATE`"* — because the MANAGER's
   task file told it to record the screen's weakness and did not say where.
   That belongs in `NOTES.md`, which is gate-only. `c/*` is the MEASUREMENT
   digest and costs 32 cells to repair.** ▶ **Put §2.4's sentence in `NOTES.md`.**
8. ⚠ **`.temp/php51/` only — never `/tmp`.** Keep the generator, delete the
   artefact; if a blob has no script that rebuilds it, write one.
9. ⚠⚠ **`RECAP_PHP.md` and `.memory-php/` are MANAGER-ONLY.** ⚠⚠⚠ **NO EDITS
   under `harness/`, `common/`, `patterns/`, `results/`, `pilot/`, `common-php/`.**
   ⚠ **No `git add` / `git commit`.** Never touch `.web/`.
10. **Bracket**: `harness/measure.py --check-stale` → **`66/0`** (must NEVER
    move); `harness-php/gate.py --tool measure --check-stale` → **`20/0` before
    you start, `22/0`** once this row's two records land. **Quote first and last.**

---

## §4 Definition of done

1. ⭐⭐⭐ **DELIVERABLE #0 (§2.2): the harm established END TO END**, and an
   explicit statement of what it is — memory error, or pure logic defect.
   **Either is a result.**
2. **The row built at all five rungs + R1h**, gated, verdict quoted **from the
   gate record, named**.
3. ⭐⭐ **THE §2.5 SIBLING CENSUS ANSWERED** — why only `BP_VAR_IS`, when four
   arms lack the guard.
4. ⭐ **THE `ph55` PAIRING NAMED IN `NOTES.md`**: one family, one fix shape, two
   different harms.
5. **`inside_share` per cell as a matrix, before the statistic is chosen**; both
   statistics labelled; **both C columns on every cross-language figure**; any
   family-B figure cleared through §B5's sweep with **two verdicts**.
6. **The three §2.6 predictions scored, either way.**
7. **`NOTES.md` records the R1h apply result** and §2.4's screen contrast.
8. ⭐ **WHAT YOU ARE UNSURE OF, in its own section.** `UNTESTED` and *"I could
   not tell"* are valued answers.
9. **Brackets quoted first and last.**
10. ⛔ **If a prediction survives, say so plainly. Do not manufacture a
    refutation to have something to report.**
