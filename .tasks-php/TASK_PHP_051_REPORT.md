# TASK_PHP_051 — REPORT · `ph56`, T5's second row

**Role:** research **engineer**, alone. **Subject:** build row 10, `ph56`, and
establish its harm end to end.

> # ⛔⛔⛔ HEADLINE, AND IT IS TWO THINGS AT ONCE
>
> ## 1. ⭐⭐⭐ DELIVERABLE #0 IS DONE, AND IT REFUTES THE CATALOGUE **AND** THE CORRECTION
> The catalogue's `⚠ risk` note is wrong in both halves, exactly as the task
> said. ⛔ **But `TASK_PHP_051` §2.2's correction is ALSO wrong** — it names the
> right code and the **wrong harm**. `zend_fetch_dim_is_handler` **never runs**
> on this row's trigger, and the `refcount++` on `EG(uninitialized_zval)` is
> **not a defect at all**: it is the implementation of `$a[] = 1`, it is
> balanced, and the FAILURE arm decrements it. **The real harm is a NULL
> POINTER READ AT OFFSET `0x14` IN A DIFFERENT HANDLER** — measured on a
> pristine PHP 5.0.0 CLI *and* reproduced at the same offset in the kernel.
>
> ## 2. ⛔ THE ROW IS **NOT** BUILT AT FIVE RUNGS AND **NOT** GATED — I ran out of depth
> **Five of six rungs exist, all differentially validated and all agreeing.**
> `verus.rs` and `spec.md` **do not exist**; nothing was built, measured,
> reported or gated. §9 is the exact stopping point. **No `Ir`, no percentage
> and no statistic is published by this task**, and deliverables #2 and #5 are
> **UNMET**.

---

## §0 BRACKETS — first and last

| | first (before any work) | last (after everything) |
|---|---|---|
| `python3 harness/measure.py --check-stale` | **`66 record(s) examined, 0 STALE`** | ✅ **`66 record(s) examined, 0 STALE`** |
| `python3 harness-php/gate.py --tool measure --check-stale` | **`20 record(s) examined, 0 STALE`** | ✅ **`20 record(s) examined, 0 STALE`** |

✅ **BOTH UNMOVED.**
⚠ **The task predicted `22/0` at close, "once this row's two records land". THEY
DID NOT LAND** — the row was never measured, so there are no new records and
`20/0` is the correct reading. That is the bracket reporting the stopping point
rather than contradicting it.

`git status --short` at close, in full:

```
 M results-php/preflight/_norow.preflight.json      <- expected, PROTOCOL_PHP.md §F6b
?? patterns-php/ph56-fetchmode-arith/               <- the new row, untracked
```

Nothing else moved. No edit under `harness/`, `common/`, `patterns/`,
`results/`, `pilot/`, `common-php/`, `.web/`, `RECAP_PHP.md` or `.memory-php/`.
No `git add`, no `git commit`.

**Checks run as required:**

| | result |
|---|---|
| `.tasks-php/cbaseline_check.py --ratchet` | **rc 0** — 68 hits, ratchet 69. ⭐ **`ph56` contributes 0** (grepped) |
| `.tasks-php/citecheck.py` | **rc 0** — ⭐ **`ph56` contributes 0** (grepped) |
| `harness-php/gate.py --preflight` with the new row present | **rc 0**, all stages ok |
| `spellings.py --audit-only` | **N/A — this row has no `spec.md`, so there is no contract prose to audit.** Stated rather than skipped silently |

ⓘ `cbaseline_check` prints *"68 hits < ratchet 69 — lower RATCHET to 68"*. **I
did not lower it**: `.tasks-php/cbaseline_check.py` is a manager tool, the drop
is not mine (my files are absent from the hit list), and tightening a corpus-wide
ratchet is a decision about the corpus.

---

## §1 ⭐⭐⭐ DELIVERABLE #0 — THE HARM, END TO END

### 1.1 What I ran

`patterns-php/SOURCES.md` §3 forbids **citing** a build tree. It does not forbid
**running** one, and every `file:line` below resolves against the pinned tarball
(`5783e0c0…`, verified). I found **twelve** extracted `php-5.0.0` trees on this
box and confirmed that **all twelve carry a `Zend/zend_compile.c` and a
`Zend/zend_execute.c` byte-identical to the tarball's** (`ac6ef970d6e2…`,
`04eb85da37e7…`) before running anything. `controls/census.py::find_cli`
re-derives that check on every invocation — and additionally **smoke-tests the
binary**, because several of the trees are `-mysql-webext` builds whose CLI exits
127 with `error while loading shared libraries`, which would have answered every
question with the same exit code.

### 1.2 ⛔ The catalogue is wrong, and so is the correction

`CATALOGUE.md`: *"the executor must have **no handler** for the illegal
combination — an extraction with a total dispatch table has removed the harm."*
⛔ Both halves false, as the task says.

`TASK_PHP_051` §2.2: *"THE HARM IS A REFCOUNT MUTATION OF A PROCESS-GLOBAL
ZVAL"*, via `zend_fetch_dim_is_handler` (`:4385`, `:2075-2080`) and
`zend_fetch_dimension_address`'s append arm (`:935-943`).
⛔⛔ **Also false for this row's trigger, and false in a more interesting way.**

**Why.** `zend_do_isset_or_isempty` (`zend_compile.c:3215-3240`) calls
`zend_do_end_variable_parse(BP_VAR_IS, 0)` at `:3219` — and then, **four lines
later**, rewrites the last opline *again*:

```c
case ZEND_FETCH_DIM_IS:  last_op->opcode = ZEND_ISSET_ISEMPTY_DIM_OBJ;  /* :3229 */
```

▶ **`ZEND_FETCH_DIM_IS` exists for four lines and is then overwritten.** The
opcode that reaches the executor is `ZEND_ISSET_ISEMPTY_DIM_OBJ` (115), so
`zend_fetch_dim_is_handler` is never entered and `:935-943` is never reached.

### 1.3 ⭐⭐⭐ The real harm, measured

`zend_isset_isempty_dim_prop_obj_handler` (`zend_execute.c:3958`):

```c
zval **container = get_obj_zval_ptr_ptr(&opline->op1, EX(Ts), BP_VAR_R);  /* :3960 */
zval *offset     = get_zval_ptr(&opline->op2, EX(Ts), &EG(free_op2), BP_VAR_R);
                                                                          /* :3961 */
...
switch (offset->type) {                                                   /* :3973 */
```

`_get_zval_ptr`'s `case IS_UNUSED:` is an explicit `*should_free = 0; return
NULL;` (`zend_execute.c:118-121`). **Nothing between `:3961` and `:3973` tests
`offset`.**

**Run, pristine 5.0.0 CLI, ASan:**

```
$a = array(1,2,3);  $r = isset($a[]);
==3098033==ERROR: AddressSanitizer: SEGV on unknown address 0x000000000014
    #0 in zend_isset_isempty_dim_prop_obj_handler
    #1 in execute
```

⭐ `0x14` = **20** = `offsetof(zval, type)` on this ABI (`value` 16 + `refcount`
4 — verified with a standalone `offsetof` probe). The fault is `offset->type`
through NULL.

> ### ▶ THE VERDICT DELIVERABLE #0 ASKS FOR: **MEMORY ERROR**, not a logic
> defect. A read through a NULL pointer at a fixed offset, in the executor,
> reached because the **compiler** emitted an opcode whose handler's operand
> contract it did not check. **CWE-476**, which is what the corpus records.

### 1.4 ⭐⭐ The kernel faults at the **same address**

`c/kernel.c` keeps `zval`'s field order on purpose (`lval`/`value_hi` 16,
`refcount` 4, `type` at 20) and carries a **C99 compile-time assertion**
(`PH56_LAYOUT_ASSERT`, a negative array bound since `_Static_assert` is C11 and
`build.py` passes `-std=c99`) that fails the build if the offset moves. Under
ASan:

```
==3110311==ERROR: AddressSanitizer: SEGV on unknown address 0x000000000014
    #0 in ph56_isset_isempty_dim_obj_handler
```

**Same crash category, same faulting offset, same enclosing function.**
`PROTOCOL_PHP.md` §A4 discharged by measurement, not by resemblance.

### 1.5 ⚠⚠⚠ AND THE REFCOUNT IS **BALANCED** — the manager's harm is the ordinary append path

The task asks whether the global's refcount goes unbalanced. **It does not, and
that is the finding.** `:935-943` is what **`$a[] = 1`** (`BP_VAR_W`) and
**`$a[] += 1`** (`BP_VAR_RW`) reach on every legal append — measured, §2 — so
`new_zval->refcount++` at `:938` is **the implementation of `[]`**, and the
insertion really does take the reference it counts. The FAILURE arm decrements
it again at `:942`. The kernel folds every slot's refcount into its `u64` so the
balance is a number rather than an argument.

▶ **Upstream is careful at `:935-943`. The carelessness is one file away, in the
compiler.**

### 1.6 ⭐⭐ THE SECOND HARM IS REAL — the manager's harm, reached by a different trigger

`:3223` rewrites only the **last** opline of the fetch list. So in
`isset($a[][0])` the `[]` opline **survives** as `ZEND_FETCH_DIM_IS`,
`zend_fetch_dim_is_handler` *does* run, and the append arm *is* reached.
Measured:

```
$a = array(1,2,3);
var_dump(isset($a[][0]));   ->  bool(false)
count($a)                   ->  4        ⛔ isset() GREW THE ARRAY
exit code                   ->  0        and no diagnostic from anything
```

⭐ **So §2.2's mechanism is correct about the CODE and wrong about the
TRIGGER.** The task anticipated exactly this outcome — *"if the harm turns out
to be 'the array silently grows and isset returns a value for an element it just
created' … THAT IS A FINDING AND THE ROW STILL STANDS"* — and it is the row's
**second** input rather than its headline. The row ships both, one byte-record
apart, and `inputs/gen.py` asserts the difference.

---

## §2 ⭐⭐⭐ THE §2.5 SIBLING CENSUS — **NON-EMPTY**, and the answer is not "an oversight"

`ph55`'s census came back empty. **This one does not.** Re-derived on every run
by `controls/census.py`, three independent ways (the parsed tarball switch, the
row's own ladder, and a pristine 5.0.0 CLI), with a **7-case selftest**.

| arm | delta | guard at 5.0.0 | the PHP | **measured on 5.0.0** |
|---|---:|---|---|---|
| `BP_VAR_R` | `-= 3` | ✅ `:753-755` | `$x = $a[];` | `rc=255` `Fatal error: Cannot use [] for reading` |
| `BP_VAR_W` | `0` | — | `$a[] = 1;` | `rc=0`, `count` 3→4 — ✅ **legal by design** |
| `BP_VAR_RW` | `+= 3` | — | `$a[] += 1;` | `rc=0`, `count` 3→4 — ✅ **legal by design** |
| `BP_VAR_IS` | `+= 6` | ⛔ **none** | `isset($a[]);` | **`rc=-11` — SEGV** |
| `BP_VAR_FUNC_ARG` | `+= 9` | ⚠ **none** | `f($a[]);` | `rc=0`, `count` 3→4 — **silent** |
| `BP_VAR_UNSET` | `+= 12` | ✅ `:771-773` | `unset($a[]);` | `rc=255` `Fatal error: Cannot use [] for unsetting` |

### 2.1 ⚠⚠ `BP_VAR_FUNC_ARG` is a live defect at 5.0.0 whose reachability is **DECLARATION ORDER**

`zend_do_pass_param` (`zend_compile.c:1411-1427`) asks for `BP_VAR_R` when
`function_ptr` is non-NULL — i.e. when the callee is **already declared at the
point of call** — and `BP_VAR_FUNC_ARG` when it is not. Measured, both ways:

```
function f($z){}  $a=array(1,2,3); f($a[]);   ->  Fatal error: Cannot use [] for reading
$a=array(1,2,3);  f($a[]);  function f($z){}  ->  rc=0,  count($a)=4      ⛔
$f="f";           $f($a[]);                    ->  rc=0,  count($a)=4      ⛔
```

⭐ **The same expression is a compile error or a silent array mutation depending
on whether `function f` is written above or below the call.** That is the
census's sharp edge, and `controls/census.py` runs both spellings side by side.

### 2.2 ⭐⭐⭐ WHY ONLY `BP_VAR_IS`? **BECAUSE THE GUARD MIGRATED LAYERS.**

I took this to the upstream history. Measured over **18 release tags** (first and
last of every 5.x minor line), by fetching `Zend/zend_compile.c` and splitting
the switch per arm:

> **`BP_VAR_FUNC_ARG` and `BP_VAR_RW` NEVER received the compile-time guard, in
> any PHP 5 release, ever** — `php-5.6.40` still reads
> `case BP_VAR_FUNC_ARG: opline->opcode += 9; ... break;` verbatim.

But `BP_VAR_FUNC_ARG` **was** closed — **11½ months later, at RUN TIME, in a
different file, by a different author**:

| sha | branch | date | author | subject |
|---|---|---|---|---|
| `9183f91b506a858f5f53c13b63c485e859eeac0f` | `PHP_5_0` | 2005-08-10 | Dmitry Stogov | *Fixed bug #34064 (arr[] as param to function is allowed only if function receives argument by reference)* |
| `779e6d203e4fa159120dfbc0644a3ed386bcf66e` | HEAD / `PHP_5_1` | 2005-08-10 | Dmitry Stogov | *Fixed bug #34064 …* |

Neither touched `zend_compile.c`. The `PHP_5_0` patch put three lines into
`zend_fetch_dim_func_arg_handler` in `Zend/zend_execute.c`; the HEAD patch also
**widened the opcode specs**, adding `UNUSED` to op2 for **`ZEND_FETCH_DIM_RW`
and `ZEND_FETCH_DIM_FUNC_ARG`** in `zend_vm_def.h`.

▶ **Upstream's settled position, reached in 2005 and unchanged since: the RW
append and the by-reference argument append are FEATURES; only the by-value read
is an error; and by-value-ness is not always knowable at compile time, so that
check belongs in the VM.**

Corroborated by counting: `"Cannot use [] for reading"` occurs **0 times** in
`php-5.0.0` and `php-5.0.4`'s `zend_execute.c`, and **once, at `:2135`**, in
`php-5.0.5`'s. So **this row's silent-append finding holds for 5.0.0 – 5.0.4 and
was closed in 5.0.5**.

### 2.3 ⚠ And the compile-time asymmetry is **permanent**

`zend_do_end_variable_parse` was deleted in PHP 7. Its descendant,
`zend_delayed_compile_dim`, reads at **master `zend_compile.c:3154-3161`**:

```c
if (dim_ast == NULL) {
    if (type == BP_VAR_R || type == BP_VAR_IS) {
        zend_error_noreturn(E_COMPILE_ERROR, "Cannot use [] for reading");
    }
    if (type == BP_VAR_UNSET) {
        zend_error_noreturn(E_COMPILE_ERROR, "Cannot use [] for unsetting");
    }
```

**Same three arms guarded, same three not** — identical at `php-7.0.0`,
`php-8.3.0` and master. Measured on real 8.2–8.5 binaries: `$a[] += 1` still
appends silently with no error, no warning and no deprecation, and is a
**tested, supported** case in `ext/opcache/tests/jit/assign_dim_op_001.phpt`.

> ### ⭐⭐ THE CENSUS'S CONCLUSION
> **`1e708a5aeb30` is NOT an incomplete fix later completed in the same place.**
> It is a compile-time fix to the one arm that was a defect, after which upstream
> decided two of the remaining three are **features** and moved the third's check
> into the **VM**. The asymmetry at `:751-776` is **deliberate**, and it survives
> into PHP 8. ▶ **This is a finding about the CATALOGUE, not about the row**, and
> §2.5 asked for exactly that.

### 2.4 ⭐ And the bug with no test outlived by its sibling's test

Bug **#29882** (*"isset crashes on arrays"*, 2004-08-29, assigned `helly`) is
closed and live on `bugs.php.net`. `1e708a5aeb30` shipped **+3/−0 and no test**;
`Zend/tests/bug29882.phpt` is **404** at `php-5.1.0`, `php-5.6.0` and master.
The **sibling's** fix did get one: `Zend/tests/bug34064.phpt` exists at
`php-5.1.0` and is **still in master**, substantively unchanged in twenty years.

⚠ **Sampling caveat, stated:** the tag matrix used first+last of each minor line,
so a guard added *and removed* inside one minor line would be invisible.

---

## §3 ⭐⭐⭐ THE `ph55` PAIRING — the family-level finding neither row has alone

| | `ph55` | `ph56` |
|---|---|---|
| defect site | `zend_execute.c:1765-1770` — the **executor** | `zend_compile.c:763-765` — the **compiler** |
| upstream fix | `4f68f3774c34`, 2004-08-30, **3 lines** | `1e708a5aeb30`, 2004-08-29, **3 lines** |
| **the fix's shape** | the **normal exit's** own guard, copied onto the error exit | **`BP_VAR_R`'s** own guard, copied onto `BP_VAR_IS` |
| `git apply` on 5.0.0 | ⛔ **FAILS** — hand backport | ✅ **SUCCEEDS** (offset −2) |
| **the harm** | **NULL indirect CALL** — the PC lands on a data word whose handler is `NULL` | **NULL operand READ** — `get_zval_ptr` returns `NULL` and the handler dereferences it at `0x14` |
| what breaks | the **program counter** | the **operand contract** |
| the invariant relied on untested | *no instruction start is a data word* | *an opcode that reads op2 is only emitted with op2 present* |
| the silent twin | `adversarial-opdatalive.bin` — 1 byte, wrong answer, exit 0 | `adversarial-chain.bin` — 1 record, array grows, exit 0 |
| Verus's obstacle | **function pointer types unsupported** → `Option<u8>` + `match` | **none** — dispatch is a `switch`, because every emitted opcode HAS a handler |

> ⭐⭐ **THE SENTENCE, and it is the crash course's paragraph:** *both defects are
> a guard that already exists elsewhere in the same function, not copied onto one
> more arm — and in both, what the unguarded arm breaks is an invariant the
> executor relies on WITHOUT TESTING.* **One family, one fix shape, one proof
> shape, two completely different harms.**

⚠ **And the two rows sit on opposite sides of the family's own name.** T5 is
*"the emitted program is not the one the executor implements"* — a statement
about a **gap**. `ph55` is an executor bug whose compiler is outside the row;
`ph56` is a compiler bug whose executor is inside it. The corpus now has one row
on each side. **T5 is closed at 2 of 2 in mechanism — but see §9: the row is not
gated, so `quota.py` will still read 9 built until it is.**

---

## §4 ⚠ THE SCREEN CONTRAST — same tool, same verdict string, completely different weight

`preimage_screen.py --id CRASH-041` → `CANDIDATE`, `hits [[763, "case
BP_VAR_IS:"]]`, `misses []`, `n_matchable 1`, `n_dropped 0`. §2.4's quote
reproduces **exactly**.

⭐ **`case BP_VAR_IS:` occurs EXACTLY ONCE in `Zend/zend_compile.c`** — I counted
it, at line **763**, the cited line; `controls/r1h_backport.py` re-counts it on
every run and fails if it ever stops being unique.

⚠⚠ Against `ph55`, which got the **same verdict string** on the strength of one
`NEXT_OPCODE();` line occurring **117 times**. ▶ **The screen's verdict is not a
scalar: its evidential weight is decided entirely by the uniqueness of the cited
line, and the tool does not report that.** A row quoting `CANDIDATE` owes the
occurrence count beside it.
✅ Recorded in `NOTES.md` §4, **not** in any `c/*` comment — `PROTOCOL_PHP.md`
§F6a, and the trap `ph55` fell into.

---

## §5 ⭐ R1h — PREDICTION 1 **SURVIVES**, ITS STATED REASON DOES NOT, AND `--check` LIED LIVE

Patch fetched, sha256 `9e86b04f294c4516…`, shipped at
`controls/1e708a5aeb30.patch`. Contents match §2.3 byte for byte.

**`git apply` SUCCEEDS:**

```
Checking patch Zend/zend_compile.c...
Hunk #1 succeeded at 761 (offset -2 lines).
Applied patch Zend/zend_compile.c cleanly.
```

⚠⚠ **THE REASON §2.3 GIVES IS REFUTED.** §2.3 argues it applies because *"THE
HUNK HEADER IS `@@ -763,6 +763,9 @@` — THE SAME LINE NUMBER AS 5.0.0's `:763`"*.
Those are **two different lines that happen to share a number**: the hunk's first
context line is `opline->opcode += 3;`, which 2004-08-30 HEAD puts at 763 and
5.0.0 puts at **761**. It applies **despite** a two-line offset, not because of
an exact match. The control measures both numbers and fails if they converge.

### 5.1 ⛔⛔ `_048` §4d's TRAP FIRED, LIVE, ON MY FIRST ATTEMPT

```
git apply --check -p1 <patch>   ->  rc=0
git apply       -p1 -v <patch>  ->  rc=0,  "Skipped patch 'Zend/zend_compile.c'."
bytes moved                     ->  NONE
```

Both exit codes reported success on a run in which **nothing was applied**,
because `.temp/` is gitignored in the enclosing repo. `git init`ing the scratch
directory fixed it. ⭐ `controls/r1h_backport.py::gitignore_trap` **reproduces
this on every invocation** and records `{path_is_gitignored: true, check_rc: 0,
bytes_moved: false}`, so a future `git` that fixes the behaviour surfaces as a
changed number rather than a stale paragraph. ▶ **`--check` is not the test; the
bytes are.**

### 5.2 ⭐ A detail worth keeping: the fix adds nothing new, it adds one more *copy*

My first spelling of the control computed the applied hunk's added lines as a
**set** difference and got `[]` — because **all three inserted lines already
occur in the file**, in `BP_VAR_R`'s arm. That is the fix in one sentence. The
control now uses a **multiset** difference and explains why in situ.

---

## §6 THE THREE §2.6 PREDICTIONS, SCORED

| # | prediction | verdict |
|---|---|---|
| **1** | **`git apply` SUCCEEDS**, where it failed on `ph55` | ✅ **UPHELD** — and its stated *reason* is **REFUTED** (§5). It applies at offset **−2** |
| **2** | stage 5c-twin passes cleanly, no hatch, no blocked row | ⛔ **UNTESTED.** `verus.rs` was never written, so nothing went through Verus. **Not refuted — unasked.** §9 |
| **3** | the R1h costs ~nothing at run time, because the guard is in the compiler | ⚠ **UPHELD ON THE MECHANISM, UNTESTED ON THE NUMBER.** The guard *is* in the compiler — verified from the source. ⛔ **AND THE TASK'S OWN CAVEAT FIRES: THIS KERNEL MODELS COMPILE-AND-RUN IN ONE LOOP.** `kernel()` compiles the whole record stream and then executes it, on **every** call, so the guard runs once per statement **per kernel call** where PHP runs it once per *compilation*. Any `c-gcc-h − c-gcc` this row ever measures is a loose **upper bound** on PHP's cost of `1e708a5aeb30` and may not be quoted as PHP's cost. `NOTES.md` §8 |

⭐ **Prediction 1 survives and I am not manufacturing a refutation of it** (§4
item 10 of the definition of done). What is refuted is the *argument*, which is
a separate claim.

**Additional statements of the task file that measurement moved:**

| statement | verdict |
|---|---|
| §2.2: *"THE HARM IS A REFCOUNT MUTATION OF A PROCESS-GLOBAL ZVAL"* | ⛔ **REFUTED for the trigger** — that handler never runs on `isset($a[])`; and the refcount is **balanced** (§1.5) |
| §2.2: *"`Zend/zend_execute.c:4385` … the handler at `:2075-2080` is three lines"* | ✅ **UPHELD as code** — both verified on the tarball. It is simply not on this path |
| §2.2: *"the STRING container IS guarded"* (`:963-964`) | ✅ **UPHELD**, verified; carried into the kernel so the contrast is in the measured program |
| §2.1's line numbers | ✅ all verified, **one nit**: `new_zval->refcount++` is at **`:938`**, not `:937` — there is a blank line at 937 |
| §2.4's screen quote | ✅ **UPHELD exactly**, and `case BP_VAR_IS:` really is unique (§4) |
| §2.5: *"a non-empty census would be a finding about the catalogue"* | ✅ **AND IT IS NON-EMPTY** (§2) |

---

## §7 ⛔ WHAT IS **NOT** IN THIS REPORT, AND WHY

**Definition-of-done #5 is UNMET and I am not partially satisfying it.** There is
**no `inside_share` matrix, no statistic, no cross-language figure, no C column,
no family-B figure and no `php50_align_sweep.py` verdict pair** — because the row
was never built into binaries, never measured and never gated. Publishing any
number here would be publishing a number with no measurement record behind it.

**Definition-of-done #2 is UNMET**: the row is not built at five rungs (four
Rust rungs are specified; three exist) and there is no gate record, so there is
no verdict to quote and none is quoted.

⚠ **No percentage appears anywhere in this report.** `cbaseline_check.py`
confirms `ph56` contributes zero hits.

---

## §8 ⭐ WHAT I AM UNSURE OF

1. ⚠⚠ **I did not verify the fixed compiler against real PHP.** I confirmed
   `git apply` places the patch and that the kernel's R1h removes both harms, but
   I **did not rebuild PHP 5.0.0 with the patch and re-run the six snippets**.
   That the fix also kills `isset($a[][0])` is an inference from the source —
   the `while (le)` loop at `:748-779` runs the switch over **every** fetch-list
   element, so the leading `[]` opline is tested too — and it is confirmed in the
   kernel, but **not on the real interpreter**. It is the cheapest remaining
   check and it is not done.
2. ⚠ **The tag matrix is a sample**, not a bisect (§2.4's caveat).
3. ⚠ **Part C of the census depends on a build tree under another project's
   `.temp`/`.trash`**, which that project's convention makes deletable at any
   time. `controls/census.py` degrades to `UNMEASURED` rather than to a wrong
   answer, and says which, but the census's strongest leg is not permanently
   reproducible on this box.
4. ⚠ **I could not tell whether `ph56`'s `switch`-based dispatch is a
   *substitution* or a *projection*** in `provenance.divergences` terms. PHP
   dispatches through `zend_opcode_handlers[]`; every opcode this row emits has a
   handler, so no behaviour changes — but "no behaviour changes on the extracted
   domain" is the `substitution` test and I have only argued it, not
   differentially demonstrated it against a table-driven variant. **§A1(c) would
   want the differential.** Not done.
5. ⚠ **The tier is undeclared.** The task asked me to declare what I measured
   rather than trust the catalogue's `narrowed`. **I cannot**: `provenance.py`'s
   kernel-overlap number is computed from `spec.md`'s `provenance` block, and
   there is no `spec.md`. My *expectation*, stated so it can be attacked, is that
   this row will measure **below** `narrowed`'s 25 % — the control flow is lifted
   one-for-one but the zval, the hash table and the fetch list are all
   re-expressed — i.e. the same direction `ph55` refuted its own label in. **That
   is a prediction, not a measurement.**
6. ⚠ **I do not know whether the Verus proof is tractable.** §9 states the
   obligation precisely, and it is structurally `ph55`'s `ok_from`. That is a
   reason for optimism and not evidence.

---

## §9 ⛔⛔⛔ THE STOPPING POINT — exactly where depth ran out

### DONE, and differentially validated

| | evidence |
|---|---|
| Deliverable #0 | §1 — on a pristine-sourced CLI **and** in the kernel, same offset, same frame |
| §2.5 census | §2 — `controls/census.py`, three ways, 7-case selftest, **rc 0** |
| R1h + prediction 1 | §5 — `controls/r1h_backport.py`, 10-case selftest, **rc 0** |
| screen contrast, `ph55` pairing | §4, §3, in `NOTES.md` §4 and §3 |
| `c/kernel.c`, `c/kernel_hardened.c`, `c/kernel.h`, `c/main.c` | build clean; all six arms behave as §2's table |
| `model.py` — **three** independent implementations | agree on **156 synthetic windows** spanning the whole (mode × base × op2-type × chain) cross product |
| **C ↔ model differential** | **156 windows × 2 configurations, 0 mismatches**; the 2 windows the model predicts NULL-deref are exactly the 2 the C SEGVs on |
| `inputs/gen.py` + corpus | every `_check_span` assertion green, **including an assertion of the census itself** |
| `safe_naive.rs` (R2), `safe_tuned.rs` (R3), `unsafe.rs` (R4) | compile; ⭐ **all five built rungs agree on every input** |
| preflight with the row present | `gate.py --preflight` → **rc 0** |

**The five-rung agreement table** (real corpus, real drivers):

| input | `c-gcc` (R1) | `c-gcc-h` (R1h) | R2 | R3 | R4 |
|---|---|---|---|---|---|
| `small.bin` | `11996482202912280498` | same | same | same | same |
| `large.bin` | `2176799369531671810` | same | same | same | same |
| `adversarial-funcarg.bin` | `7352021033067941120` | **same** ⭐ the uncaught sibling | same | same | same |
| `adversarial-nullderef.bin` | ⛔ **SEGV (139)** | `8698019932423182848` | same | same | same |
| `adversarial-chain.bin` | ⛔ `5859151209396187392` **— wrong answer, exit 0** | `8698019932423182848` | same | same | same |

Both benign checksums equal `model.py`'s independently predicted values.

### NOT DONE

1. ⛔ **`verus.rs` (R5) does not exist.** The obligation is written down:
   > for every `j < nops`, `ops[j].opcode == ISSET_ISEMPTY_DIM_OBJ` implies
   > `ops[j].op2_type != T_UNUSED`

   — established as a loop invariant of the compile pass (which **needs** the
   `BP_VAR_IS` guard, i.e. R1h) and consumed at `zunwrap`'s call site. ⭐ It is
   the direct analogue of `ph55`'s `ok_from`: a property the **emitter**
   establishes and the **executor** relies on without testing.
2. ⛔ **`spec.md` does not exist** — no contract, no `provenance` block, no
   `idiom`, no `identity`, no `collapse`, no tier, no `contract_sha256`.
3. ⛔ **Never built, measured, reported or gated.**
4. ⛔ No `spellings.py`, `negatives.py`, `statistic.py` or `argv_align.py`.

### The order to resume in

1. `verus.rs` from `unsafe.rs` (the exec text must stay **one** text —
   `identity` pins R4 == R5). Start with the compile-pass invariant.
   ⚠ `unsafe.rs` already isolates **ten** trusted accessors, and the tenth,
   `zunwrap`, **is CRASH-041 written as a precondition**.
2. `spec.md`, deriving `requires`/`ensures` from `verus.rs`. `ensures` should
   name `ph56_run`, which `model.py` already exports via `helpers`.
   ⚠ Run `spellings.py --audit-only` on the contract prose **before** quoting it.
3. The **six**-command sequence (`PROTOCOL_PHP.md` §E). Expect the first gate to
   FAIL on tables — that is the `gate → report → gate` chain.
4. Then the statistic, the `inside_share` matrix, and `php50_align_sweep.py`
   with **two** verdicts per pair.
5. Then §8.1 — rebuild PHP with the patch and re-run the six snippets.

### ⚠ Blast radius: none

The row is **untracked**, in **no digest**, and `gate.py --preflight` is green
with it present (measured). `harness/measure.py --check-stale` and
`harness-php/gate.py --tool measure --check-stale` are **unmoved** at 66/0 and
20/0. **Deleting the directory costs only the work.**

---

## §10 Housekeeping

* **Scratch**: `.temp/php51/` only, never `/tmp`. Artefacts deleted per
  `CLAUDE.md` constraint 6; `.temp/php51/NOTES.md` is the rebuild recipe for
  everything removed. 40 KB remains — two `.c` probes, one `.php` reproducer,
  the screen JSON and the control's output log.
* **Liveness**: no `pgrep` was used at any point, and no process was killed.
  Every long command ran under `timeout`.
* **`grep -a`** throughout.
* ⚠ **One `.tasks-php/` tool reported a suggestion I did not act on**:
  `cbaseline_check.py` prints *"68 hits < ratchet 69 — lower RATCHET to 68"*.
  The drop is not mine (`ph56` contributes 0). Lowering a corpus-wide ratchet is
  a manager decision, so I left it and record it here.
