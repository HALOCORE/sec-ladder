# TASK_PHP_048 — ROW 9: `ph55-opdata-stride` (T5), **THE SMALLEST SELF-CONTAINED MECHANISM IN THE CATALOGUE**

**Role:** research **engineer**. **One agent, alone.**
**Report:** `.tasks-php/TASK_PHP_048_REPORT.md` — **write the FILE** (rule 10).

> ⏳ **WRITTEN, NOT YET DISPATCHED.** `TASK_PHP_047` (the review round) is in
> flight and **one agent works at a time** (`.tasks/PROTOCOL.md`). The manager
> dispatches this only after `_047` reports. ⚠ **If `_047` refutes F106 or
> F104, re-read §2.6 before starting** — that is the only section of this task
> whose premises `_047` can move.

---

## §1 Why this row

**Row 9 opens `T5`, the seventh of 20 mechanism families**, and `quota.py`
records 32 rows still owed with **14 families unentered**. ⭐ **T5's second row
(`ph56`, 2004, 1 file) is nearly free once T5's scaffolding exists**, so entering
this family discharges **2** of the 32, which no other unentered family offers as
cheaply.

⭐⭐⭐ **AND IT IS THE BEST CRASH-COURSE SPECIMEN IN THE CORPUS.** The manager's
standing instruction is that this ladder will become a crash course for people
porting PHP to Rust. **This row's entire mechanism is five facts, all verified
below on the pristine C, and the fix is three lines.** Nothing else in the
catalogue is that small and that complete.

⭐ **It also needs NONE of `ph52`'s trouble**: no zvals, no allocator, **no
garbage determinism** (the fault is a NULL indirect call, not a read of
uninitialised memory), no stack-layout dependence, no `MaybeUninit`. ⛔ **So it
will NOT reproduce F97/F104's collision**, and that is worth saying out loud:
this row is the control that shows those findings are about `MaybeUninit` rows
and not about php rows generally.

---

## §2 The manager's decisions, and the facts behind them

### 2.1 ⭐⭐⭐ THE MECHANISM, **VERIFIED FACT BY FACT ON THE PRISTINE TARBALL** — you are not being asked to re-derive this, you are being asked to build it

⚠ **Rule 14: a premise in a task file is one an engineer has no reason to doubt,
so the manager measured every one of these.** Source is the pinned tarball
(`sha256 5783e0c0…`), read with
`tar -xzOf <tb> php-5.0.0/<path> | sed -n 'a,bp'`. **Re-read any you depend on.**

| # | fact | site |
|---|---|---|
| **1** | A compound assignment to an array dimension is a **two-word** instruction: `zend_op *op_data = opline+1;` | `Zend/zend_execute.c:1742` |
| **2** | The handler records that at run time in a **local flag**: `zend_bool increment_opline = 0;` at declaration, `increment_opline = 1;` **only** on the `ZEND_ASSIGN_DIM` arm | `:1728`, `:1749` |
| **3** | ⛔ **The error exit does NOT consult the flag** — `if (*var_ptr == EG(error_zval_ptr)) { …; NEXT_OPCODE(); }` | **`:1765-1770`**, the `NEXT_OPCODE()` at **`:1769`** |
| **4** | ✅ The normal exit **does**: `if (increment_opline) { INC_OPCODE(); } NEXT_OPCODE();` | `:1792-1795` |
| **5** | The two macros: `NEXT_OPCODE()` = `CHECK_SYMBOL_TABLES() EX(opline)++; return 0;` — **stride 1 AND returns**. `INC_OPCODE()` = `if (!EG(exception)) { CHECK_SYMBOL_TABLES() EX(opline)++; }` — **conditional, no return** | `:1317-1320`, `:1326-1330` |

**And the harm, also verified:**

| # | fact | site |
|---|---|---|
| **6** | `ZEND_API opcode_handler_t zend_opcode_handlers[512];` — a fixed 512-entry table | `:1338` |
| **7** | ⭐ `zend_opcode_handlers[ZEND_OP_DATA] = NULL;` — **explicitly, deliberately NULL** | `:4427` |
| **8** | `pass_two` copies the table into **every instruction**: `opline->handler = zend_opcode_handlers[opline->opcode];` | `Zend/zend_opcode.c:363` |
| **9** | ⛔ The executor dispatches through that field with **NO NULL CHECK**: `while (1) { zend_clean_garbage(…); if (EX(opline)->handler(…)) { return; } }` | `Zend/zend_execute.c:1383-1394` |

▶ **So: error arm → PC strides 1 → PC lands on the trailing `ZEND_OP_DATA` word
→ that word's `handler` field is `NULL` → unconditional indirect call through
NULL.**

> ### ⭐⭐⭐ THE DETAIL THAT MAKES THIS THE SPECIMEN, AND IT IS NOT IN THE CATALOGUE
>
> **`INC_OPCODE()` has FOUR call sites in 5.0.0** — `:1719`, `:1793`, `:2193`,
> `:2224` — and the manager read all four. **Three are unconditional**
> `INC_OPCODE(); NEXT_OPCODE();`, because those handlers are **statically**
> two-word. ⭐ **Two of the three carry a shouting comment**:
> `/* assign_obj has two opcodes! */` (`:2192`) and
> `/* assign_dim has two opcodes! */` (`:2223`), **exclamation marks in the
> original.**
>
> ⭐⭐ **`zend_binary_assign_op_helper` is the ONLY one of the four whose
> instruction width is DATA-DEPENDENT** — it dispatches on
> `opline->extended_value` and is one-word for `default`, two-word for
> `ZEND_ASSIGN_DIM`. **That is why it needs a flag, and it is the one with the
> bug.**
>
> ▶ ⭐ **THE SENTENCE THE CRASH COURSE WANTS: the codebase shouts the invariant
> at the two sites that get it right, and is silent at the site where the
> invariant became conditional.** ✅ **The manager checked the two siblings for
> the same defect and they are CLEAN** — `zend_assign_obj_handler` (`:2186-2195`)
> and `zend_assign_dim_handler` (`:2198-2226`) each have **exactly one exit**.
> **No sibling site is owed** (F50/F58's census channel, run and empty).

### 2.2 ⭐⭐ ITEM 95 IS **ANSWERED — DELIBERATE HAND-OFF, NOT A SECOND DEFECT.** THE ROW NEEDS **ONE** ERROR EXIT

Item 95 asked whether `INC_OPCODE()`'s own `if (!EG(exception))` guard is a
*second* instance of the defect, since with an exception pending the normal exit
also advances by only one word. ▶ **It is not, and the manager traced it.**

`Zend/zend_exceptions.c:36-59`, `zend_throw_exception_internal`:

```c
53   if ((EG(current_execute_data)->opline+1)->opcode == ZEND_HANDLE_EXCEPTION) {
54       /* no need to rethrow the exception */
55       return;
56   }
57   EG(opline_before_exception) = EG(current_execute_data)->opline;
58   EG(current_execute_data)->opline = &EG(active_op_array)->opcodes[EG(active_op_array)->last-1-1];
```

⭐⭐ **`last-1-1` is `last-2`, and `ZEND_HANDLE_EXCEPTION` is the LAST opcode** —
`zend_do_end_function_declaration` emits `zend_do_return(…)` then
`zend_do_handle_exception(…)` (`Zend/zend_compile.c:1088-1092`, emission at
`:1078-1085`). ▶ **So the throw parks the PC one slot SHORT of the handler, in
anticipation of the `EX(opline)++` that the handler's own trailing
`NEXT_OPCODE()` will perform.** ✅ **Line 53 reads the same invariant back:
*"`opline+1` is `ZEND_HANDLE_EXCEPTION`"* is exactly the state `:58` creates.

▶ **`INC_OPCODE()`'s guard therefore exists to stop the stride being spent
TWICE** — the exception redirect already budgeted the one `++`. **It is a
correction, not an omission.**

⛔ **CONSEQUENCE FOR THE KERNEL: build ONE faulting exit, not two.** The
exception path is correct and modelling it adds a whole exception machinery for
no mechanism. ⚠ **Say in `NOTES.md` that you considered it and why it is out** —
item 95 is closed by this task and its closure should be visible.

⭐ **AND IT STRENGTHENS THE ROW:** the same function guards its stride correctly
against **two** hazards on one exit (the `increment_opline` flag *and*
`EG(exception)`), and against **neither** on the other exit, 25 lines earlier.

### 2.3 ⭐⭐ THE R1h IS `4f68f3774c34` AND IT IS **THREE LINES** — BUT IT DOES **NOT** APPLY TO 5.0.0. HAND-BACKPORT IT.

The full patch, from the cache (`.temp/mgr/batch/patches/4f68f3774c34.patch`;
⚠ **gitignored — `refetch.sh` / `fixsurvey.py --online` is the generator**):

```
Stanislav Malyshev, Mon 30 Aug 2004, "fix crash #29893"
 Zend/zend_execute.c | 3 +++

@@ -1942,6 +1942,9 @@ static inline int zend_binary_assign_op_helper(…)
 			AI_USE_PTR(EX_T(opline->result.u.var).var);
 		}
 		FREE_OP_VAR_PTR(free_op1);
+		if (increment_opline) {
+			INC_OPCODE();
+		}
 		NEXT_OPCODE();
 	}
```

⭐⭐ **THE FIX IS THE NORMAL EXIT'S OWN THREE LINES, COPIED ONTO THE ERROR
EXIT.** Nothing is invented. **This is the cleanest R1h in the catalogue and it
is why this row was chosen.**

⚠⚠ **BUT THE CONTEXT DOES NOT MATCH 5.0.0 AND `git apply` WILL FAIL.** The fix
is 2004-08-30 against HEAD; 5.0.0 shipped 2004-07-13, and by fix time the
function had gained an inner block and a `FREE_OP_VAR_PTR(free_op1);` that 5.0.0
does not have at `:1765-1770`. ▶ **Backport the THREE LINES by hand, before
`:1769`'s `NEXT_OPCODE();`.**

⭐⭐ **THE IDENTIFICATION OF *WHICH EXIT* IS DECISIVE AND OFFLINE — THREE
INDEPENDENT LEGS, because `preimage_screen.py` alone is NOT enough here:**

1. **The hunk's own function-context line names the function**:
   `@@ … @@ static inline int zend_binary_assign_op_helper(…)`.
2. **`increment_opline` is a local of that function and of no other.**
3. ⭐ **The other exit already has the identical guard at 5.0.0 (`:1792-1794`)**,
   so a patch adding it *there* would be adding a duplicate. **Therefore the
   hunk is the error exit.**

⛔⛔ **AND THE SCREEN'S OWN VERDICT IS WEAK — YOU ARE BEING TOLD SO RATHER THAN
LEFT TO INHERIT IT.** `preimage_screen.py --id CRASH-023` returns **`CANDIDATE`**
with `hits [[1769, "\t\tNEXT_OPCODE();"]]`, `misses []`, `n_matchable 1`,
`n_dropped 0`, `patch_files ["Zend/zend_execute.c"]`. ⚠⚠ **`NEXT_OPCODE();`
occurs 115 times in that file**, so *"1/1 cited 5.0.0 lines are present in the
pre-image"* is **true and nearly information-free**. ▶ **The screen has done its
job — it is an EXCLUSION tool (F68/item D11) and it correctly declines to
exclude — but do not quote it as confirmation.** ⭐ **Quote the three legs
above instead.** ⓘ `preimage_screen.py --selftest` **PASSES** (manager-run),
including N12/N13.

### 2.4 TIER — **declare what you measure**, not the catalogue's label

The catalogue files `ph55` as **`narrowed`**. ⚠ **That is a mining-wave label.**
▶ **State the tier you actually built and the evidence for it**, as every row
since `_029` has.

### 2.5 ⭐⭐⭐ THE LADDER, AND THE QUESTION THIS ROW EXISTS TO PRICE

⭐ **This is the one candidate whose original C shape IS the pinned kernel
shape** (catalogue, Part B): an instruction array, a PC, a dispatch table with a
NULL entry, a two-word form. **No translation of the mechanism is required.**

**The kernel, as the manager sees it — argue with it if the build says
otherwise:** the blob **is** the instruction stream. Decode a fixed-size record
per word; walk a PC; dispatch through a table; fold executed opcodes into the
`u64` answer. One opcode has a two-word form whose second word is a DATA word
with no handler. One arm of that opcode's handler is a faulting arm that exits
without consulting the width.

> ### ⭐⭐ THE QUESTION, AND IT IS SHARPER THAN *"safe Rust catches it"*
>
> The defect is a **control-flow** error — a wrong PC. The NULL call is only how
> it **manifests**. ▶ **So the row prices: DOES THE DISPATCH REPRESENTATION
> CATCH THE WRONG PC, AND WHAT DOES THE CATCH COST?**
>
> * A table of `Option<fn>` **cannot be called without unwrapping**, so safe
>   Rust converts a NULL call into a **panic** — ⭐ **a real difference, and it
>   is a FINDING, not the row's purpose.**
> * ⛔⛔ **BUT IF THE DATA WORD'S OPCODE FIELD HAPPENS TO BE A VALID OPCODE,
>   SAFE RUST EXECUTES GARBAGE SILENTLY, EXACTLY LIKE C.** The `Option` catches
>   the NULL, not the wrong PC.
> * ▶ **BUILD BOTH CASES AS SEPARATE ADVERSARIAL INPUTS AND PRICE THEM
>   SEPARATELY.** *"Safe Rust reproduces the bug"* and *"safe Rust panics"* are
>   **both** results here, on the same row, distinguished by one byte of the
>   data word. ⭐ **That contrast is the single most teachable thing this row
>   can produce, and no other built row has it.**
>
> ⚠ **The R5 obligation is therefore about the PC, not about the table**:
> *the PC always lands on an instruction word, never on a data word.* **If that
> is what Verus ends up proving, say so — it is a better statement than
> `handler != NULL`.**

⛔⛔⛔ **AND THE STANDING RULE: NEVER REFUSE OR NARROW THIS ROW FOR A RUST-SIDE,
VERUS-SIDE OR LADDER-SIDE REASON** (`CLAUDE.md` rule 6). *"Safe Rust can't
express it"*, *"safe Rust reproduces it bit-identically"*, *"no column moves"*,
*"Miri doesn't see it"* are **ALL FINDINGS, NEVER KILLS.**

### 2.6 ⛔ F97 / F104 / F106 — **EXPECTED NOT TO RECUR, AND THAT IS A DELIVERABLE**

`ph53` and `ph52` both hit the `MaybeUninit` collision: `_scan_unsafe_sites`
refuses a stray `unsafe`, and `check_trusted_twins`'s `n_twins == 0` hard-fails a
row with one untwinnable trusted item. ⭐ **This row has no `MaybeUninit` and its
R4 unsafety is `unwrap_unchecked` on an `Option<fn>`, which is TWINNABLE — a safe
exec twin is just `t.unwrap()`.** ▶ **So the manager predicts stage 5c-twin
PASSES CLEANLY here.** ⚠⚠ **REGISTER THE PREDICTION AND REPORT THE OUTCOME
EITHER WAY.** ⛔ **If it fails, that is a much bigger finding than F104** — it
would mean the collision is not about `MaybeUninit` at all.

⚠ `_047` is reviewing F97/F104/F106 as this is written. **Re-read its coverage
table before relying on this section.**

### 2.7 ⭐⭐⭐ WHICH STATISTIC — **MEASURE `inside_share` FIRST AND LET IT DECIDE. DO NOT ASSUME A1.**

`.memory-php/03-numbers.md`'s rule, and `ph52` is the row that proved it must be
**per-cell**: `inside_share` was **22.24 %** on `ph52`'s C cells and **98.6 %**
on its Rust cells, so **the same row needed W1 for one column and A1 for the
other.** `ph45` is 9.5 % → W1; `ph53` is 89.5 % → A1.

▶ **Measure `inside_share` per cell BEFORE choosing, publish the matrix, and
publish BOTH statistics labelled.** ⛔ **Never publish a percentage without
saying WHICH INPUT and WHICH STATISTIC.** ⚠ **Do not quote a W1 figure to more
than 2 dp** — item 99: W1 moves ±14–28 Ir across regenerations while every A1
figure is bit-identical.

ⓘ **The manager's guess, offered as a guess:** the whole mechanism is inside the
dispatch loop, so `inside_share` should be **high on every cell** and A1 should
resolve this row well. **If it is not, that is the finding.**

### 2.8 ⭐ TWO PREDICTIONS, REGISTERED BEFORE ANY RUNG EXISTS

⚠ **Registered so they can be refuted.** `ph52` refuted five manager statements
and `ph53` refuted three of four predictions; **that is the expected yield, not a
failure.**

1. **The R3 endpoint is DEGENERATE and the R4 endpoint MOVES** — the opposite of
   `ph52`. Reason: there is no bounds-check term to respell away (the PC walk is
   the whole kernel), while `unwrap()` → `unwrap_unchecked()` is a single named
   lever. ⛔ **`ph45` and `ph52` both reversed their ordering under search, so
   `n = 2` says search first and predict second.**
2. **The upstream fix costs a measurable, non-zero amount** — it adds a branch on
   `increment_opline` to a hot dispatch loop. ⓘ **`ph52` refuted the analogous
   prediction in W1** (item 76: the fix was *profitable*, `−0.342 %`). **If this
   one is free or profitable too, that is `n = 2` toward a real law.**

### 2.9 SCREEN AND QUOTA — the bookkeeping, already done

* ✅ `preimage_screen.py --selftest` **PASS**; `--id CRASH-023` → **`CANDIDATE`**
  (see §2.3 for why that is weak and what replaces it).
* ✅ `quota.py`: **8 built, 32 owed, T5 unentered.** This row + `ph56` = 2.
* ⚠ **NAME COLLISION, DO NOT BE MISLED:** `.tasks-php/TASK_PHP_005/006/008_REPORT`
  mention `ph55-extern`, `ph56-mention`, `ph57-rust`. **Those are synthetic
  fixtures for the provenance checker and have NOTHING to do with catalogue rows
  `ph55`/`ph56`/`ph57`.**

---

## §3 Traps

1. ⚠⚠⚠ **`grep -a` ALWAYS** (F35) — 41 corpus files exit 1 silently under plain
   `grep`, and a probe script does not reproduce it. ⭐ **A line-based grep also
   cannot find a prose phrase that WRAPS.**
2. ⛔⛔ **A BACKTICK IN AN `idiom.required`/`forbidden` ENTRY *IS* A PIN** — item
   100, and **three instances in three consecutive tasks** (a reviewer, an
   engineer, a validator). ▶ **Run `spellings.py --audit-only` on any contract
   prose you draft, BEFORE it lands, and read the output.** `required` is
   presence-only and **cannot fail the gate**; `required_absent` is a raw
   presence report that fires on shipped rungs.
3. ⛔⛔ **§H: a validator change lands with its must-fire negatives, or it does
   not land — AND THE NEGATIVES MUST LIVE INSIDE THE VALIDATOR**, feeding
   `problems` so stage 9b sees `FRESH+VERDICT-FAILED`. ⚠ **NOT in gitignored
   `.temp/`** — item 97 measured 13 §H-at-risk citations across 4 rows.
   ⭐ **`ph52` is the model: 24 arms in 3 batteries inside `spellings.py`, and it
   contributes ZERO to that count.**
4. ⛔ **F101 / item 109 — `kernel_fingerprint` is PATH-SENSITIVE and it fired
   LIVE on `ph52` in BOTH directions**, including **one false POSITIVE** (two
   different sources reported byte-identical). ▶ **Clone `ph52`'s repair**: a
   fixed-width `vNN` scratch slug, an **asserted equal-path-length invariant**,
   and exec-vs-twin through `asm.py::identity_level` at `norel`.
5. ⚠ **A comment is not code.** Three separate defects in this programme came
   from a check that read prose, including one guard that fired on the comment
   documenting its own defect. ▶ **Test behaviour.**
6. ⚠ **`timeout <N> <cmd>`**; never `pkill`/`killall`/substring match; confirm a
   full command line for an exact PID before killing it.
7. ⚠ **`.temp/php48/` only — never `/tmp`.** Keep the generator, delete the
   artefact. **If a blob has no script that rebuilds it, write one first.**
8. ⚠⚠ **`.web/` is owned by a CONCURRENT session. NEVER `git add -A`.** And
   **no `git add` / `git commit` at all** — the manager commits at task
   boundaries.
9. ⚠⚠ **`RECAP_PHP.md` and `.memory-php/` are MANAGER-ONLY for writing.**
10. ⚠⚠⚠ **NO EDITS under `harness/`, `common/`, `patterns/`, `results/`,
    `pilot/`, `common-php/`.** ⛔ `harness/check.py` is hashed into all 33 PAT
    gate records.
11. ⓘ **`verus_checked` and `problems` are NOT gate-record fields.** They live in
    `controls/spellings.json`; `problems` is also a preflight field. **NAME THE
    FILE EVERY FIELD CAME FROM** (F99, item 84).
12. **Bracket**: `harness/measure.py --check-stale` → **`66/0`**;
    `harness-php/gate.py --tool measure --check-stale` → **`18/0` before you
    start**, and it will read **`20/0`** when this row's two records land.
    ⓘ **The php bracket covers GATE records too**, so `18/1` mid-task while a
    gate-only file moves is legitimate. ⛔ **`66/0` must never move.**

---

## §4 Definition of done

1. **The row built at all five rungs + R1h**, gated, with `harness-php/gate.py`
   green and the verdict quoted **from the gate record, named**.
2. ⭐⭐ **THE TWO ADVERSARIAL INPUTS OF §2.5 PRICED SEPARATELY** — the NULL-handler
   case and the valid-opcode-in-the-data-word case — **with an explicit statement
   of what safe Rust does in each.**
3. **`inside_share` measured PER CELL and published as a matrix, before the
   statistic is chosen**; both statistics published, labelled.
4. **Item 95 recorded as CLOSED** in `NOTES.md`, with §2.2's reasoning and the
   note that the exception path is deliberately out of the kernel.
5. **The two §2.8 predictions scored, either way.**
6. ⭐ **The stage-5c-twin prediction of §2.6 reported**, pass or fail.
7. **`NOTES.md` records that the R1h is a HAND BACKPORT**, that `git apply`
   fails, and the **three legs** of §2.3 that identify the exit — **not** the
   screen's `CANDIDATE`.
8. ⭐ **WHAT YOU ARE UNSURE OF, in its own section.** `_041` reported 15
   uncertainties and found its own citation defect; that is the standard.
   **`UNTESTED` and `I could not tell` are valued answers.**
9. **Brackets quoted first and last.**
10. ⛔ **If a prediction survives, say so plainly. Do not manufacture a
    refutation to have something to report.**
