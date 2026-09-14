# ph56 — NOTES

Measurements and arguments for `ph56-fetchmode-arith`. `README.md` is the
reader's entry point; this file is the record.

⛔ **THE ROW IS INCOMPLETE — §10 IS THE STOPPING POINT.** Read it before
planning any work here.

---

## §1 ⭐⭐⭐ THE HARM, ESTABLISHED END TO END — and the catalogue is wrong in **both** halves, and so was the correction

`patterns-php/CATALOGUE.md` says of this row:

> ⚠ risk: the executor must have **no handler** for the illegal combination — an
> extraction with a total dispatch table has removed the harm.

⛔ **Both halves are false.** There *is* a handler, and the harm is not removed
by a total dispatch table because the harm is not about the dispatch table at
all.

⚠⚠ **AND `TASK_PHP_051` §2.2's CORRECTION IS ALSO WRONG — it names the right
code and the wrong harm.** It says the harm is a refcount mutation of
`EG(uninitialized_zval)` reached through `zend_fetch_dim_is_handler`
(`zend_execute.c:4385`, `:2075-2080`) and `zend_fetch_dimension_address`'s
append arm (`:935-943`). **`zend_fetch_dim_is_handler` never runs on this
row's trigger.** The task file said, correctly and in terms, that the manager
read the code and did not run it; this section is what running it produced.

### 1.1 What actually happens, measured on a pristine 5.0.0 CLI

`zend_do_isset_or_isempty` (`zend_compile.c:3215-3240`) calls
`zend_do_end_variable_parse(BP_VAR_IS, 0)` at `:3219` and then, at `:3225-3232`,
**rewrites the last opline a second time**:

```c
switch (last_op->opcode) {
    case ZEND_FETCH_IS:      last_op->opcode = ZEND_ISSET_ISEMPTY_VAR;      break;
    case ZEND_FETCH_DIM_IS:  last_op->opcode = ZEND_ISSET_ISEMPTY_DIM_OBJ;  break;  /* :3229 */
    case ZEND_FETCH_OBJ_IS:  last_op->opcode = ZEND_ISSET_ISEMPTY_PROP_OBJ; break;
}
```

So `ZEND_FETCH_DIM_IS` **exists for four lines and is then overwritten**. The
opcode that reaches the executor is `ZEND_ISSET_ISEMPTY_DIM_OBJ` (115), and its
handler is `zend_isset_isempty_dim_prop_obj_handler` (`zend_execute.c:3958`):

```c
zval **container = get_obj_zval_ptr_ptr(&opline->op1, EX(Ts), BP_VAR_R);  /* :3960 */
zval *offset     = get_zval_ptr(&opline->op2, EX(Ts), &EG(free_op2), BP_VAR_R);
                                                                          /* :3961 */
...
switch (offset->type) {                                                   /* :3973 */
```

`get_zval_ptr`'s `case IS_UNUSED:` is an explicit `*should_free = 0; return
NULL;` (`:118-121`). Nothing between `:3961` and `:3973` tests `offset`.

**MEASURED**, `php-5.0.0` CLI built from the pinned tarball
(`Zend/zend_compile.c` and `Zend/zend_execute.c` both byte-identical to
`5783e0c0…`), under ASan:

```
==3098033==ERROR: AddressSanitizer: SEGV on unknown address 0x000000000014
    #0 in zend_isset_isempty_dim_prop_obj_handler
    #1 in execute
```

⭐ `0x14` is **20**, and `offsetof(zval, type)` is 20 on this ABI
(`value` 16 + `refcount` 4). The fault is `offset->type` through a NULL
`zval *`. **CWE-476, and it is a memory error, not a pure logic defect.**

### 1.2 The verdict Deliverable #0 asks for

> **MEMORY ERROR.** A read through a NULL pointer, at a fixed offset, in the
> executor, reached because the *compiler* emitted an opcode whose handler's
> operand contract it did not check.

### 1.3 ⭐⭐ The kernel faults at the SAME ADDRESS

`c/kernel.c` keeps `zval`'s field order — `lval`/`value_hi` (16) then `refcount`
(4) then `type` — so `offsetof(ph56_zval, type)` is also 20, and
`PH56_LAYOUT_ASSERT` is a C99 negative-array-bound assertion that fails the
build if it ever moves. Under ASan the kernel reports:

```
==3110311==ERROR: AddressSanitizer: SEGV on unknown address 0x000000000014
    #0 in ph56_isset_isempty_dim_obj_handler
```

**Same crash category, same faulting offset, same enclosing function.** That is
`PROTOCOL_PHP.md` §A4 discharged by measurement rather than by resemblance.

### 1.4 ⚠⚠⚠ AND THE REFCOUNT IS **BALANCED** — the manager's harm is the ordinary append path

The task asks whether the refcount on the shared global goes unbalanced.
**It does not, and the reason is the finding.**

`:935-943` is reached by **`$a[] = 1`** (`BP_VAR_W`) and **`$a[] += 1`**
(`BP_VAR_RW`) on every legal append — measured, §2 — so
`new_zval->refcount++` at `:938` is **the implementation of `[]`**, not a
defect. The insertion takes a reference; the reference is real; the count is
correct. And the FAILURE arm decrements it again:

```c
if (zend_hash_next_index_insert(...) == FAILURE) {
    zend_error(E_WARNING, "Cannot add element to the array ...");   /* :940 */
    *retval = &EG(uninitialized_zval_ptr);                          /* :941 */
    new_zval->refcount--;                                           /* :942 */
}
```

This kernel keeps `zval.refcount` where PHP keeps it and folds **every** slot's
refcount into the answer, so the balance is a number in the checksum rather than
an argument. Upstream is careful here; the carelessness is one file away, in the
compiler.

### 1.5 ⭐⭐ The SECOND harm, and it is the one nothing sees

`:3223` rewrites the **last** opline of the fetch list. In `isset($a[][0])` the
fetch list has two elements, so the `[]` opline **survives as
`ZEND_FETCH_DIM_IS`**, `zend_fetch_dim_is_handler` really does run, and
`zend_fetch_dimension_address` takes the append arm. Measured on the pristine
CLI:

```
$a = array(1,2,3);
var_dump(isset($a[][0]));   ->  bool(false)
count($a);                  ->  4          ⛔ isset() GREW THE ARRAY
exit code                   ->  0
```

⭐ **So the manager's harm is real — it is just reached by a different trigger,
and it is the row's SECOND input rather than its headline.** The row ships both:
`inputs/adversarial-nullderef.bin` and `inputs/adversarial-chain.bin`, which
differ **in the first statement record only** (the chain bit and the operand-kind
index — `inputs/gen.py` asserts it), one of which SEGVs and one of which returns
a plausible answer with exit 0 and `sanitizer_expect: clean`.

---

## §2 ⭐⭐⭐ THE SIBLING CENSUS — six arms, two guards, and the answer is NOT "an oversight"

`TASK_PHP_051` §2.5 asks why only `BP_VAR_IS` was fixed when four arms lack the
guard. **`ph55`'s census came back empty. This one does not.** Re-derived on
every run by `controls/census.py`, three independent ways: the pinned tarball's
parsed switch, the row's own ladder, and a pristine 5.0.0 CLI.

| arm | guard | PHP 5.0.0, measured | fixed by `1e708a5aeb30`? |
|---|---|---|---|
| `BP_VAR_R` | ✅ | `Fatal error: Cannot use [] for reading` | already guarded |
| `BP_VAR_W` | — | `rc=0`, `count($a)` 3→4 | **no — legal by design** |
| `BP_VAR_RW` | — | `rc=0`, `count($a)` 3→4 | **no — legal by design** |
| `BP_VAR_IS` | — | **`rc=-11` (SEGV)** | ✅ **yes** |
| `BP_VAR_FUNC_ARG` | — | `rc=0`, `count($a)` 3→4, silent | **no** |
| `BP_VAR_UNSET` | ✅ | `Fatal error: Cannot use [] for unsetting` | already guarded |

### 2.1 Three of the four unguarded arms are not oversights

* **`BP_VAR_W`** is the entire point of `[]`. `$a[] = 1` *must* reach `:935`.
* **`BP_VAR_RW`** (`$a[] += 1`) appends and then applies the operator. It has
  **never** been guarded, at compile time or run time, in any PHP from 5.0.0 to
  master — and `Zend/tests` and `ext/opcache/tests/jit/assign_dim_op_001.phpt`
  carry it as an **expected-to-succeed** case. It is a supported feature.
* **`BP_VAR_FUNC_ARG`** is the real sibling, and §2.2 is its story.

### 2.2 ⚠⚠ `BP_VAR_FUNC_ARG` IS A LIVE DEFECT AT 5.0.0 WHOSE REACHABILITY IS **DECLARATION ORDER**

`zend_do_pass_param` (`zend_compile.c:1411-1427`):

```c
case ZEND_SEND_VAR:
    if (function_ptr) {
        zend_do_end_variable_parse(BP_VAR_R, 0 TSRMLS_CC);          /* GUARDED */
    } else {
        zend_do_end_variable_parse(BP_VAR_FUNC_ARG, offset TSRMLS_CC); /* NOT */
    }
```

`function_ptr` is non-NULL exactly when the callee is **already declared at the
point of the call**. So, measured:

```
function f($z){}  $a=array(1,2,3); f($a[]);   ->  Fatal error: Cannot use [] for reading
$a=array(1,2,3);  f($a[]);  function f($z){}  ->  rc=0,  count($a) = 4   ⛔
$f="f"; $f($a[]);                              ->  rc=0,  count($a) = 4   ⛔
```

⭐ **The same expression is a compile error or a silent array mutation depending
on whether `function f` is written above or below the call.** `controls/census.py`
runs both spellings side by side, as its own must-not-fire control.

### 2.3 ⭐⭐⭐ AND THE ANSWER TO "WHY ONLY ONE?" IS THAT **THE GUARD MIGRATED LAYERS**

`BP_VAR_FUNC_ARG` was closed **11½ months later, at run time, in a different
file, by a different author**:

| sha | branch | date | author | subject |
|---|---|---|---|---|
| `9183f91b506a858f5f53c13b63c485e859eeac0f` | `PHP_5_0` | 2005-08-10 | Dmitry Stogov | *Fixed bug #34064 (arr[] as param to function is allowed only if function receives argument by reference)* |
| `779e6d203e4fa159120dfbc0644a3ed386bcf66e` | HEAD / `PHP_5_1` | 2005-08-10 | Dmitry Stogov | *Fixed bug #34064 (arr[] as param to function in class gives invalid opcode)* |

Neither touched `Zend/zend_compile.c`. The `PHP_5_0` patch added three lines to
`zend_fetch_dim_func_arg_handler` in `Zend/zend_execute.c`; the HEAD patch also
**widened the opcode specs**, adding `UNUSED` to op2 for
`ZEND_FETCH_DIM_RW` *and* `ZEND_FETCH_DIM_FUNC_ARG` in `zend_vm_def.h`.

▶ **Upstream's settled position, arrived at in 2005 and unchanged since: the RW
append and the by-reference argument append are FEATURES; only the by-value read
is an error; and by-value-ness is not always knowable at compile time, so that
check belongs in the VM.**

Corroboration, measured: `"Cannot use [] for reading"` occurs **0 times** in
`php-5.0.0/Zend/zend_execute.c` and `php-5.0.4`'s, and **once, at `:2135`**, in
`php-5.0.5`'s. So this row's silent-append finding holds for **5.0.0 – 5.0.4**
and was closed in **5.0.5**.

### 2.4 ⚠ AND THE COMPILE-TIME ASYMMETRY IS PERMANENT

`zend_do_end_variable_parse` was deleted in PHP 7 (0 occurrences at
`php-7.0.0`), replaced by `zend_delayed_compile_dim`. Master
(`Zend/zend_compile.c:3154-3161`) reads:

```c
if (dim_ast == NULL) {
    if (type == BP_VAR_R || type == BP_VAR_IS) {
        zend_error_noreturn(E_COMPILE_ERROR, "Cannot use [] for reading");
    }
    if (type == BP_VAR_UNSET) {
        zend_error_noreturn(E_COMPILE_ERROR, "Cannot use [] for unsetting");
    }
```

**The same three arms guarded, the same three not** — identical at `php-7.0.0`,
`php-8.3.0` and master. The 2004 shape is still load-bearing twenty-two years
later.

> ⭐ **THE CENSUS'S CONCLUSION: `1e708a5aeb30` is NOT an incomplete fix that was
> later completed in the same place. It is a compile-time fix to the one arm
> that was a defect, after which upstream decided two of the remaining three are
> features and moved the third's check into the VM. The asymmetry at
> `:751-776` is deliberate, and it survives into PHP 8.**

⚠ **Sampling caveat, stated**: the tag matrix was taken at the first and last
release of each 5.x minor line, so a guard added *and removed* entirely inside
one minor line would be invisible. Nothing else suggests that happened.

### 2.5 There is no regression test for #29882

Bug **#29882** (*"isset crashes on arrays"*, `tomas_matousek at hotmail dot
com`, 2004-08-29, assigned `helly`) is closed and live on `bugs.php.net`.
`1e708a5aeb30` added **one file, +3/−0 and no test**; `Zend/tests/bug29882.phpt`
is 404 at `php-5.1.0`, `php-5.6.0` and master.
⭐ **The sibling's fix DID get one**: `Zend/tests/bug34064.phpt` exists at
`php-5.1.0` and is still in master, substantively unchanged in twenty years.
**The defect this row is about is the one with no test; its uncaught sibling is
the one with the test that outlived it.**

---

## §3 ⭐⭐⭐ THE `ph55` PAIRING — one family, one fix shape, two harms, and one proof shape

**This is the family-level finding, and neither row has it alone.**

| | `ph55` | `ph56` |
|---|---|---|
| corpus id | CRASH-023 | CRASH-041 |
| defect site | `zend_execute.c:1765-1770` — the **executor** | `zend_compile.c:763-765` — the **compiler** |
| the one-line defect | an early exit strides **1** over a two-word instruction | one `switch` arm applies its delta without the test its two siblings apply |
| upstream fix | `4f68f3774c34`, 2004-08-30, **3 lines** | `1e708a5aeb30`, 2004-08-29, **3 lines** |
| **the fix's shape** | **the normal exit's own guard, copied onto the error exit** | **`BP_VAR_R`'s own guard, copied onto `BP_VAR_IS`** |
| `git apply` on 5.0.0 | ⛔ **FAILS** — hand backport | ✅ **SUCCEEDS** (offset −2) |
| the harm | **NULL indirect CALL** — `zend_opcode_handlers[ZEND_OP_DATA]` is `NULL` and the PC lands on a data word | **NULL operand READ** — `get_zval_ptr` returns `NULL` for `IS_UNUSED` and the handler dereferences it at offset `0x14` |
| what breaks | the **program counter** | the **operand contract** |
| the silent twin | `adversarial-opdatalive.bin` — 1 byte away, wrong answer, exit 0 | `adversarial-chain.bin` — 1 record away, array silently grows, exit 0 |
| Verus's obstacle | **function pointer types unsupported** → `Option<u8>` + `match` | none — dispatch is a `switch`, because every emitted opcode HAS a handler |

⭐⭐ **THE SENTENCE:** *both defects are a guard that already exists elsewhere in
the same function, not copied onto one more arm — and in both, what the
un-guarded arm breaks is an invariant the executor relies on without testing.*
`ph55`'s is *"no instruction start is a data word"*; `ph56`'s is *"an opcode
that reads op2 is only ever emitted with op2 present"*. **Same family, same fix
shape, same proof shape — and completely different harms.**

⚠ **And the two rows disagree about where the mechanism lives.** `ph55` is an
executor bug whose compiler is outside the row; `ph56` is a compiler bug whose
executor is inside the row. T5's name — *the emitted program is not the one the
executor implements* — is a statement about the **gap**, and the corpus now has
one row on each side of it.

---

## §4 ⚠ THE PRE-IMAGE SCREEN: same tool, same verdict string, completely different weight

`python3 .tasks-php/preimage_screen.py --id CRASH-041` →

```
verdict       CANDIDATE
why           1/1 cited 5.0.0 lines are present in the pre-image of Zend/zend_compile.c
hits          [[763, "\t\t\tcase BP_VAR_IS:"]]
misses        []
n_matchable   1
n_dropped     0
```

⭐ **`case BP_VAR_IS:` occurs EXACTLY ONCE in `Zend/zend_compile.c`** — counted
on the pristine tarball, and re-counted by `controls/r1h_backport.py` on every
run (`case_bp_var_is_count`). So the `1/1` really does discriminate.

⚠⚠ **Contrast `ph55`, which got the SAME verdict string on the strength of one
`NEXT_OPCODE();` line that occurs 117 times in its file** — where the `1/1` was
true and nearly information-free. **The screen's verdict is not a scalar: its
evidential weight is decided entirely by the uniqueness of the cited line, and
the tool does not report that.** ▶ A row quoting `CANDIDATE` owes the
occurrence count beside it.

---

## §5 ⭐ R1h — `git apply` PLACES IT, and the manager's reason is refuted

`1e708a5aeb30711f8b7b2a811377a13f2b23a8c9` (Marcus Boerger, 2004-08-29,
*"Bugfix #29882 isset crashes on arrays"*) — one file, **+3 −0**. Patch bytes
at `controls/1e708a5aeb30.patch`, sha256 `9e86b04f294c4516…`.

**PREDICTION 1 (`TASK_PHP_051` §2.3) SURVIVES.** Measured by
`controls/r1h_backport.py` on every run:

```
Checking patch Zend/zend_compile.c...
Hunk #1 succeeded at 761 (offset -2 lines).
Applied patch Zend/zend_compile.c cleanly.
```

⚠⚠ **ITS STATED REASON DOES NOT.** §2.3 argues the patch applies because *"THE
HUNK HEADER IS `@@ -763,6 +763,9 @@` — THE SAME LINE NUMBER AS 5.0.0's `:763`"*.
Those are **two different lines that happen to share a number**: the hunk's first
context line is `opline->opcode += 3;`, which 2004-08-30 HEAD puts at 763 and
5.0.0 puts at **761**. The patch applies *despite* a two-line offset. The
control measures `hunk_header_old_start` (763) against
`first_context_line_at_5_0_0` (761) and fails if they ever become equal.

### 5.1 ⛔⛔ AND `git apply --check` LIED, LIVE, EXACTLY AS `_048` §4d SAID

First attempt, inside the enclosing (gitignored) `.temp/`:

```
git apply --check -p1 ...   ->  rc=0
git apply       -p1 -v ...  ->  rc=0, "Skipped patch 'Zend/zend_compile.c'."
bytes moved                 ->  NONE
```

Both exit codes said success on a run in which nothing was applied.
`gitignore_trap()` reproduces this on every invocation and records
`{path_is_gitignored: true, check_rc: 0, bytes_moved: false}`, so a future `git`
that fixed the behaviour shows up as a **changed number** rather than as a stale
paragraph. **`--check` is not the test; the bytes are.** The real apply is run
inside a `git init`ed scratch.

### 5.2 The R1 → R1h delta is upstream's, and the lines are a COPY

`controls/r1h_backport.py::kernel_delta` re-derives the difference between
`c/kernel.c` and `c/kernel_hardened.c` inside the `BP_VAR_IS` arm and checks
that the added text tests **both** the opcode and the op2 type, as upstream's
three lines do.

⭐ **A detail worth keeping:** the control's first spelling computed the applied
hunk's added lines as a *set* difference and got `[]` — because **all three
inserted lines already occur in the file**, in `BP_VAR_R`'s arm. That is the fix
in one sentence: it adds nothing new, it adds one more *copy*. The control now
uses a multiset difference and says why.

---

## §6 The two adversarial inputs, and the one that nothing sees

| input | R1 | R1h / R2 / R3 / R4 | `sanitizer_expect` |
|---|---|---|---|
| `adversarial-nullderef.bin` | **SEGV** (rc 139) | `8698019932423182848` | `fires` |
| `adversarial-chain.bin` | `5859151209396187392` — **a different, wrong answer, exit 0** | `8698019932423182848` | ⛔ `clean` |
| `adversarial-funcarg.bin` | `7352021033067941120` | `7352021033067941120` — **identical** | `clean` |
| `adversarial-guardfires.bin` | `8698019932423182848` | identical | `clean` |

▶ **`model.py::sanitizer_expect` derives `fires` from the NULL DEREFERENCE and
not from the mis-compile**, and says so in its own docstring. The chain input
mis-compiles by exactly as much as the null-deref one and is declared `clean`,
because there is nothing for a detector to say.

⭐⭐ **And `adversarial-funcarg.bin` is the census inside the ladder**: R1 and
R1h agree to the digit, because `1e708a5aeb30` does not touch that arm.

---

## §7 ⚠ The dispatch: a `switch`, and why that is sound here and was not on `ph55`

`c/kernel.c` dispatches with a `switch` on the opcode rather than through
`zend_opcode_handlers[opline->opcode]`. On `ph55` that substitution would have
**deleted the row** — the table's one `NULL` entry *is* the mechanism. Here
every opcode the compiler can emit **has** a handler; the harm is a NULL
*operand* inside one of them. ▶ So `ph56` never meets `ph55`'s Verus wall
(*"the verifier does not yet support function pointer types"*) and its four Rust
rungs need no `Option<u8>` handler-ID substitution at all.

⚠ **That is a finding about the two rows' costs, not a claim that one is
better**: `ph55` pays a substitution and prices it; `ph56` does not need one.

---

## §8 ⚠⚠ THE R1h COST PREDICTION IS ABOUT THIS HARNESS, NOT ABOUT PHP — stated, as §2.6 requires

`TASK_PHP_051` §2.6 prediction 3 says the R1h guard *"costs ~nothing at run
time — the guard is in the COMPILER, not the executor, so it runs once per
emitted opline and not per execution"*, and adds: ⛔ *"if the kernel models
compile-and-run in one loop, say so, because then the prediction is about your
harness and not about PHP."*

▶ **IT DOES. SAID PLAINLY: `kernel()` COMPILES AND EXECUTES ON EVERY CALL.**
Each driver iteration decodes the whole record stream, runs the mode switch over
every emitted opline, and then executes the op_array. So in this row the guard
runs **once per statement per kernel call**, where in PHP it runs once per
statement per *compilation* and is amortised over every execution of the
compiled script.

⚠ **The consequence for the number**: whatever `c-gcc-h − c-gcc` measures here
is an **upper bound** on PHP's own cost of the fix, and a loose one — PHP caches
nothing in this harness that it would cache in life. **No R1h cost figure from
this row may be quoted as PHP's cost of `1e708a5aeb30`.**

⛔ **AND NO SUCH FIGURE IS PUBLISHED BY THIS ROW AT ALL**, because the row was
not measured — see §10. The prediction is therefore recorded as **UNTESTED on
the number and UPHELD on the mechanism**: the guard is in the compiler, which is
verified from the source, and the harness does fold compile into the measured
loop, which is verified from `c/kernel.c`.

---

## §9 The ladder as built, and what the R3 → R4 step buys

All five built rungs agree on every input (§6). The rungs differ as follows:

* **R2 → R3** removes three bounds checks and nothing else: one subslice per
  record instead of eight indexings, the container zval read once, and the
  global refcount held in a local across the append arm's two writes.
* **R3 → R4** replaces checked access with **ten trusted accessors**. Nine are
  ordinary unchecked indexing. ⭐ **The tenth, `zunwrap`, is
  `Option::unwrap_unchecked` on the OPERAND — the exact operation
  `zend_isset_isempty_dim_prop_obj_handler` performs at `:3973`.** Its
  `requires t.is_some()` is discharged by the *compiler pass*, and that
  precondition **is CRASH-041 written as a proof obligation**.

⚠ **No instruction counts, no `Ir`, no percentages are published here**, because
no measurement record exists — §10.

---

## §10 ⛔⛔⛔ THE STOPPING POINT — what is done, what is not, and what to do next

`TASK_PHP_051` says: *"If your depth runs out, STOP and say exactly where."*
This is exactly where.

### DONE, and validated

| | evidence |
|---|---|
| Deliverable #0 — the harm end to end | §1. Run on a pristine-sourced CLI **and** in the kernel; same offset, same frame |
| the §2.5 sibling census | §2, and `controls/census.py` re-derives it three ways with a 7-case selftest |
| R1h + the `git apply` prediction | §5, and `controls/r1h_backport.py` with a 10-case selftest |
| the pre-image screen contrast | §4 |
| the `ph55` pairing | §3 |
| `c/kernel.c`, `c/kernel_hardened.c`, `c/kernel.h`, `c/main.c` | build clean; all six arms behave as §2's table |
| `model.py` | THREE implementations, agreeing on **156 synthetic windows** |
| C ↔ model differential | **156 windows × 2 configurations, 0 mismatches**; the 2 predicted NULL-deref windows are exactly the 2 that SEGV |
| `inputs/gen.py` + the corpus | every `_check_span` assertion green, including the census assertion |
| `safe_naive.rs` (R2), `safe_tuned.rs` (R3), `unsafe.rs` (R4) | compile; **all five built rungs agree on every input** |
| `controls/` | both controls green, both selftests green |
| the preflight with this row present | `gate.py --preflight` → **rc 0** |

### NOT DONE

1. ⛔ **`verus.rs` (R5) does not exist.** The proof obligation is written down —
   §9, and `unsafe.rs::zunwrap`'s doc comment — but no Verus source was
   attempted. **This is the long pole.** The property to prove is:

   > for every `j < nops`, `ops[j].opcode == ISSET_ISEMPTY_DIM_OBJ` implies
   > `ops[j].op2_type != T_UNUSED`

   established as a loop invariant of the compile pass (which needs the
   `BP_VAR_IS` guard, i.e. R1h) and consumed at `zunwrap`'s call site. It is the
   direct analogue of `ph55`'s `ok_from`, and like `ok_from` it is a property the
   **emitter** establishes and the **executor** relies on without testing.
2. ⛔ **`spec.md` does not exist**, so the row has no contract, no `provenance`
   block, no `idiom`, no `identity` and no `collapse`. `provenance.py` has
   nothing to validate and the gate cannot read a `contract_sha256`.
3. ⛔ **The row has never been built, measured, reported or gated.** No `Ir`, no
   `inside_share`, no statistic choice, no family-B figure, no alignment sweep.
4. ⛔ `controls/` has no `spellings.py`, no `negatives.py`, no `statistic.py`,
   no `argv_align.py`.

### ⚠ Consequently, these `TASK_PHP_051` deliverables are **UNMET**

* **#2** — the row is not built at five rungs and not gated; no verdict to quote.
* **#5** — no `inside_share` matrix, no statistic, no C columns, no §B5 sweep.
* **#6 prediction 2** (*stage 5c-twin passes cleanly*) — **UNTESTED**. Nothing
  was put through Verus, so nothing is known. It is not refuted; it is unasked.
* **#6 prediction 3** — upheld on the mechanism, **UNTESTED on the number**; §8.

### The order to resume in

1. Write `verus.rs` from `unsafe.rs` — the exec text must stay one text
   (`identity` pins R4 == R5). Start with the compile-pass invariant.
2. Write `spec.md`, deriving `requires`/`ensures` from `verus.rs`. `ensures`
   should name `ph56_run`, which `model.py` already exports as `helpers`.
3. The six-command sequence (`PROTOCOL_PHP.md` §E). ⚠ Expect the first gate to
   FAIL on tables; that is the `gate → report → gate` chain, not a defect.
4. Then, and only then, the statistic, the `inside_share` matrix and
   `.tasks-php/php50_align_sweep.py`.

⚠ **Nothing in this row is load-bearing for any other row.** It is untracked,
it is in no digest, and `gate.py --preflight` is green with it present
(measured). Deleting it costs only the work.
