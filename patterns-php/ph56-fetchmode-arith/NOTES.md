# ph56 — NOTES

Measurements and arguments for `ph56-fetchmode-arith`. `README.md` is the
reader's entry point; this file is the record.

⭐ **THE ROW IS COMPLETE AND GATED.** §11 is the proof, §12 is the statistic.
§10 is the HISTORY and not a warning: the row was built over **two** tasks, and
`TASK_PHP_051` stopped cleanly at five rungs with no `spec.md` rather than
guessing at the sixth.

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

* **R4 → R5** adds the proof and **changes not one character of the exec text**
  (§11). The numbers are in §12c.

⭐⭐ **AND THE R3 → R4 LEVER IS ONE SPELLING OF ONE EXPRESSION.** `safe_naive.rs`
and `safe_tuned.rs` write a **checked** `unwrap` on the operand; `unsafe.rs` and
`verus.rs` write the unchecked one through `zunwrap`. `spec.md`'s
`idiom.required[2]` declares that per rung and backticks nothing on the Rust
side, because a pin there would name a spelling half the Rust rungs cannot
carry.

---

## §10 ⓘ THE ROW'S HISTORY — it was built over two tasks, and the stop was the right call

`TASK_PHP_051` built five of six rungs, established the harm end to end, ran the
sibling census and the R1h backport, and then **stopped** — `verus.rs` and
`spec.md` did not exist and nothing had been built, measured or gated. It wrote
down the obligation, the resume order and the blast radius, and published **no**
`Ir`, **no** percentage and **no** statistic rather than half of one.
`TASK_PHP_052` resumed from that note and did §11 and §12.

⭐ **That cost the programme one task and cost it nothing else.** The five rungs
were differentially validated before the stop and none of them moved afterwards
except for one normalisation the proof forced, itemised in §11.3 and in
`spec.md`'s `provenance.divergences`.

### What was already true at the stop, and is still true

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

### What `TASK_PHP_052` added

| | evidence |
|---|---|
| `verus.rs` (R5) | §11. **66 verified / 0 errors**, **76 under `--cfg slb_twin`**, no `#[verifier::rlimit]` |
| `spec.md` | the contract, the seven pinned spans, the tier declaration and the 56 `verus.items` pins |
| the gate | the six-command sequence, `PROTOCOL_PHP.md` §E |
| the statistic | §12 — the `inside_share` matrix per cell, both C columns on every cross-language figure, and §B5's sweep |
| `controls/negatives.py` | the mutants that must FAIL to verify, including `r1` |
| `controls/spellings.py` | every backticked pin in `spec.md` against every rung |
| `controls/statistic.py`, `controls/rlimit_bisect.sh` | §12 and §11.4 |

---

## §11 ⭐⭐⭐ THE PROOF — `operand_present`, and it is `ph55`'s `ok_from` one file over

### 11.1 What is proved

```
requires  off + len <= buf@.len(),  16 <= len,  len <= 8 * MAX_STMT
ensures   r == ph56_fold(buf@, off as int, len as int)
```

A **value** postcondition over the whole machine, not a memory-safety-only
retreat. `ph56_fold` is PHP 5.0.0's compiler-plus-executor with `1e708a5aeb30`
applied, spelled as recursive spec functions — `c_stmt`, `parsed`, `compiled`,
`s_fetch`, `e_step`, `e_run`, `fold_slots`, `fold_anext` — and `model.py`'s
**second** implementation, `ph56_run`, re-derives the same `u64` from a
different decomposition. A kernel that returned `0` unconditionally would
satisfy every bounds obligation in the file; it is the `ensures` that stops the
proof being vacuous, and `main`'s
`assert(r == ph56_fold(buf@, (k * stride) as int, stride as int))` is what
*consumes* it.

### 11.2 ⭐⭐⭐ The obligation, and where it comes from

> `operand_present(ops, n)` — *for every `j < n`, an opline whose opcode is
> `ZEND_ISSET_ISEMPTY_DIM_OBJ` carries an op2 that is `IS_CONST` or `IS_VAR`,
> and never `IS_UNUSED`.*

It is the **loop invariant of the compile pass**, it is what discharges
`zunwrap`'s `requires t.is_some()`, and **it is exactly the invariant
`case BP_VAR_IS:` breaks at 5.0.0.** Three facts carry the per-statement step,
and the middle one is the upstream fix:

1. `ZEND_ISSET_ISEMPTY_DIM_OBJ` is reachable only through
   `zend_do_isset_or_isempty`'s `ZEND_FETCH_DIM_IS` arm (`:3229`), and
   `ZEND_FETCH_DIM_IS` is `ZEND_FETCH_DIM_W + 6` and nothing else — that is the
   six-groups-of-three layout doing the work;
2. `case BP_VAR_IS:` **refuses** `ZEND_FETCH_DIM_W` with an `IS_UNUSED` op2.
   At 5.0.0 it does not, and this is the assert that fails;
3. `zend_do_isset_or_isempty` rewrites the **last** opline only, so a chain's
   leading `[]` opline is judged by (2) as well.

⭐⭐ **It is ESTABLISHED BY THE EMITTER and CONSUMED BY THE EXECUTOR WITHOUT
TESTING**, which is `ph55`'s `ok_from` with the layers swapped. See §11.5.

⚠ **Note what it is NOT: it is not *every opcode has a handler*.** Every opcode
this compiler emits HAS one. What is missing is the **operand** — §7, and it is
why this row needs no `Option<u8>` substitution and never meets Verus's
function-pointer-type refusal.

### 11.3 ⚠ THE ONE THING THE PROOF CHANGED IN THE OTHER RUNGS, and it is declared

Verus models `usize` as 32 **or** 64 bits and will not assume a `u64` cast to
`usize` is lossless, so R5 must take the modulus **before** the cast. `ph55`
resolved that by shipping `(x as usize) % NVAR` in `unsafe.rs` and
`(x % (NVAR as u64)) as usize` in `verus.rs` — two texts, on a row whose
`identity` pin says one.

▶ **This row normalised ALL FOUR Rust rungs onto the second spelling** (three
expressions per file, nine in total), so:

* R4 and R5 are **one exec text**, character-identical apart from the `verus!`
  block, the spec and proof items and the ghost clauses;
* the R2→R3 and R3→R4 gradients are **not** polluted by a representation change
  that has nothing to do with either lever.

The two expressions denote the same value on any 64-bit target and compile to
the same mask. C keeps the cast-first form, because C has nothing to prove.
Itemised in `spec.md`'s `provenance.divergences`, and demonstrated
behaviour-preserving by the gate's own stage-3 cross-rung checksum on every
input.

### 11.4 ⭐⭐ THE RLIMIT IS **2**, AND THE DEFAULT IS 10

`controls/rlimit_bisect.sh`, bisected on this box rather than guessed:

| rlimit | plain | `--cfg slb_twin` |
|---:|---|---|
| 1 | 65 verified / **1 error** | 75 / **1 error** |
| 2 | **66 / 0** | **76 / 0** |
| 3, 5, 8, 10, 20, 30, 40, 60, 100, 200 | 66 / 0 | 76 / 0 |
| *(no attribute — what ships)* | 66 / 0 | 76 / 0 |

⭐ **`ph55` bisected to the same `2`** on a proof of the same shape. That makes
it an `n = 2` result about the SHAPE and not a fact about one row: every
obligation in both files is one unfolding of a recursive definition whose shape
the exec code mirrors, so Z3 never searches. ⚠ Compare `ph16`, whose obligation
is a single index bound with no loop in it and which ships
`#[verifier::rlimit(30)]` because its twin build FAILED at 8.

⚠⚠ **AND THE FIRST DRAFT OF `verus.rs` DID EXCEED THE DEFAULT.** The cause was a
**wrong loop invariant**, not proof size: two clauses that cannot hold at a
`break` were declared `invariant` instead of `invariant_except_break`, Z3 spent
the budget failing to prove them, and the diagnostic was
`Resource limit (rlimit) exceeded`. ▶ **An rlimit error is a symptom, not a
size** — and the obvious repair, raise the number, would have shipped a proof
with a wrong invariant and a 20× budget.

### 11.5 ⭐⭐⭐ THE `ph55` PAIRING'S R5 HALF — the family is now `n = 2` on the PROOF too

§3 pairs the two rows on the **defect** and the **fix**. This is the third axis
and neither row has it alone:

| | `ph55` | `ph56` |
|---|---|---|
| the obligation | `ok_from` — *starting at `p` and striding by each instruction's own width, every word the PC lands on is an INSTRUCTION word* | `operand_present` — *every opline that reads op2 was emitted with op2 present* |
| what it is about | the **program counter** | the **operand contract** |
| who establishes it | the **emitter** (`emit_from`) | the **emitter** (the compile pass's loop invariant) |
| who consumes it | the **executor**, untested, at `zend_execute.c:1391` | the **executor**, untested, at `zend_execute.c:3973` |
| what it discharges | `hunwrap`'s `requires t.is_some()` | `zunwrap`'s `requires t.is_some()` |
| trusted items | 8 (+8 twins) | 10 (+10 twins) |
| rlimit needed | **2** | **2** |
| Verus's obstacle | ⛔ **function pointer types unsupported** — a TYPE-LEVEL refusal no `external_body` wrapper fixes; forced `Option<u8>` + `match` on all four Rust rungs | **none** |
| the must-fire negative | `--emit nofixup` deletes the emitter pass | `--emit r1` deletes `1e708a5aeb30`'s three lines |

> ⭐⭐ **THE SENTENCE, and it completes §3's:** *in both rows the obligation is a
> property the EMITTER establishes and the EXECUTOR relies on WITHOUT TESTING,
> both are loop invariants of the emitting pass, both discharge exactly one
> `unwrap_unchecked` precondition, and both proofs need an rlimit of 2 against a
> default of 10.* **One family, one fix shape, one proof shape, two harms.**

### 11.6 ⭐ THE MUTANTS, AND `r1` FAILS ON THE ROW'S OWN ASSERT

`controls/negatives.py`. Four mutants, and the row declares in advance which
must fail:

| mutant | what it removes | must | measured |
|---|---|---|---|
| `r1` | ⭐⭐⭐ `1e708a5aeb30`'s three lines — from `s_parse_ok` and from the exec arm together | **FAIL** | **65 verified / 1 error**, and the error is the `assert forall` that re-establishes `operand_present` — the diagnostic names `ISSET_ISEMPTY_DIM_OBJ` |
| `noinv` | `operand_present` from the **executor** loop's invariant | **FAIL** | see `controls/negatives.json` |
| `nocap` | the `nops + 1 + chain > MAX_OPS` break | **FAIL** | 65 / 1 |
| `noclamp` | the `if nstmt > MAX_STMT { nstmt = MAX_STMT; }` clamp | **FAIL** | 65 / 1 |
| `nobuf` | `off + len <= buf@.len()` — the kernel's **only** precondition | **FAIL** | 65 / 1 |

⭐ **The `r1` mutant is the whole R5 argument in one command.** It is not enough
that the file verifies; what makes the proof *about CRASH-041* is that deleting
the 2004 patch makes it stop verifying, **at the obligation and not somewhere
else** — which `negative_problems` arm 3 checks by reading the diagnostic rather
than the exit code.

⚠ `pristine` re-verifies the **shipped** file plain and twin on every run and
fails if either moves off 66/0 or 76/0. Without it, a run in which Verus was
broken for every input would report five mutants failing and look like a pass.
Measured: `66 / 0` plain and `76 / 0` twin, with all five mutants at `65 / 1`.

### 11.7 ⭐⭐ THE PRECONDITION COUNT WENT 3 → 1, AND THE GATE DID IT

The first draft of `verus.rs` carried `ph55`'s three preconditions, copied
across:

```
requires  off + len <= buf@.len(),  16 <= len,  len <= 8 * MAX_STMT
```

⛔ **The gate's own `req-mut` stage deleted each one from the verified item and
re-ran Verus.** Two of the three came back `66 verified, 0 errors` — i.e. the
body never used the assumption and no call site ever had to discharge it:

```
[req-mut] verus.rs kernel requires[1] is NOT load-bearing   (16 <= len)
[req-mut] verus.rs kernel requires[2] is NOT load-bearing   (len <= 8 * MAX_STMT)
```

Both were **deleted**, and the shipped kernel has exactly one `requires`.

▶ **Why the two rows differ, and it is not about the proof.** `ph55`'s decoder
writes `nops - 2` and its op_array has no capacity test, so `16 <= len` and
`len <= 8 * MAX_OPS` are the only things keeping those expressions defined.
`ph56` **establishes** both facts in the code instead: `nstmt` is clamped to
`MAX_STMT` two lines after it is computed, and the statement loop breaks on
`nops + 1 + chain > MAX_OPS`. ⭐ Those are exactly the two things
`controls/negatives.py`'s `noclamp` and `nocap` delete, and **both mutants
fail** — so the row does not merely assert that the code establishes the
bounds, it measures that nothing else does.

⚠⚠ **AND THE LESSON IS ABOUT COPYING A SIBLING'S SIGNATURE.** A precondition
that is not load-bearing is not harmless: it is a claim about the caller that
the callee does not need, it narrows the admissible call sites for nothing, and
it is exactly the decoration `.memory/04-verus.md` warns a `requires` can become.
It was caught by a stage that exists for that purpose and would not have been
caught by reading.

⭐ **AND THE DELETION COST ZERO BYTES, MEASURED RATHER THAN ASSERTED.** A ghost
clause erases before codegen, so removing two of them should change no machine
code — but *should* is an argument. The four `verus` binaries were `md5sum`'d
before and after, and rebuilt from the edited source through
`harness-php/gate.py --tool build`:

```
verus-O3-isolated   ecf9521fdebbe03cc91fc034b076f83a   before and after
verus-O0-isolated   33d6eeb18628d24e5a36de9f60fc4eef   before and after
```

▶ **Byte-identical.** So every figure in §12 that was taken before the edit is a
figure about the shipped binary. ⚠ The MEASUREMENT RECORD still had to be
retaken, because it pins `verus.rs`'s **source** hash and not the binary's —
`harness-php/gate.py --tool measure --check-stale` reported `STALE
results/ph56-fetchmode-arith.json patterns/ph56-fetchmode-arith/verus.rs`, which
is the digest doing exactly its job on a change that moved no byte it measures.

### 11.8 SLB-TRUSTED-ARGUMENT — the per-item arguments the gate requires

Ten trusted items, ten arguments. Each answers the three things no stage of the
gate can judge: **(a)** is the twin's body the right checked stand-in for the
unchecked operation; **(b)** is the `ensures` COMPLETE with respect to every
unchecked operation the body performs; **(c)** does each clause mean the same
thing in the shipped configuration as in the twin's.

#### SLB-TRUSTED-ARGUMENT verus.rs bget

**(a)** The unchecked operation is `*v.get_unchecked(i)` on a `&[u8]`; the twin
is `v[i]`, the same read with the bounds check Rust would have emitted. There is
no third thing `get_unchecked` does. **(b)** The body performs exactly one
memory operation and it is a read at `i`; `r == v@[i as int]` names the value of
that read, and there is no post-state to constrain because `v` is a shared
reference and the function returns by value. A body that also read `i + 1` would
still satisfy this contract — `TASK_009_REVIEW`'s x4 — and the defence is Miri,
which this row requires, plus a body three tokens long quoted verbatim beside
the twin. **(c)** `i < v@.len()` and `r == v@[i as int]` mention only the
parameter, the slice view and the return value; `slb_twin` is on the twin's own
`#[cfg]` and nowhere else, so nothing in either clause can differ between the
two configurations.

#### SLB-TRUSTED-ARGUMENT verus.rs oget

**(a)** `*a.get_unchecked(i)` on a `&[Op; MAX_OPS]` against the twin's `a[i]`:
the same read, checked. `Op` is `Copy`, so both return by value and neither can
alias. **(b)** One read, at `i`, returned; `r == a@[i as int]` is the whole of
it, and there is no post-state — `a` is shared. **(c)** The clauses name `i`,
`MAX_OPS` and `a@`; `MAX_OPS` is a `pub const usize` outside any `#[cfg]`, so it
is the same 128 in both configurations. ⚠ **The `requires` is `i < MAX_OPS` and
NOT `i < a@.len()`**, deliberately: the length is in the TYPE, so
`a@.len() == MAX_OPS` holds of every `a` this signature admits and a
length-shaped `requires` would be saying nothing. That is the difference from
`bget`, whose slice length is a run-time fact.

#### SLB-TRUSTED-ARGUMENT verus.rs oset

**(a)** `*a.get_unchecked_mut(i) = x` against the twin's `a[i] = x`: the same
store, checked. **(b)** ⭐ This is the completeness case that matters. The body
performs exactly one store, and the `ensures` names the **whole post-state** —
`final(a)@ == old(a)@.update(i as int, x)` — so a body that also clobbered
`a[i + 1]`, or stored something other than `x`, or stored at some other index,
could not satisfy its own postcondition. A weaker `ensures` naming only
`final(a)@[i] == x` would have admitted all three, and this row does not write
one. **(c)** `i`, `MAX_OPS`, `x`, `old(a)@`, `final(a)@` — none is
`#[cfg]`-dependent. ⚠ `x: Op` is a **pure value** and correctly has no
precondition: every inhabitant of `Op` is a legal store into a slot that
`[ZERO_OP; MAX_OPS]` has already initialised.

#### SLB-TRUSTED-ARGUMENT verus.rs sget

**(a)** `*a.get_unchecked(i)` on a `&[Zv; NSLOT]` against `a[i]`: the same read,
checked; `Zv` is `Copy`. **(b)** One read, at `i`, returned by value;
`r == a@[i as int]` is the whole of it and there is no post-state. **(c)** `i`,
`NSLOT` (a `pub const usize` = 42, outside any `#[cfg]`) and `a@`. ⭐ `Zv` is
ONE record where `ph55` used two parallel arrays for the same zval store, so
this row has one get/set pair for the store where `ph55` has two — a trusted
surface two items narrower for the same job, and `spec.md`'s
`unsafe_justifications` records the trade rather than hiding it.

#### SLB-TRUSTED-ARGUMENT verus.rs sset

**(a)** `*a.get_unchecked_mut(i) = x` against `a[i] = x`. **(b)** One store, and
the `ensures` is the whole post-state `old(a)@.update(i as int, x)`, so a body
that clobbered a neighbour could not satisfy it. `x: Zv` is a pure value and
needs no precondition — every inhabitant of `Zv` is a legal store into an
already-initialised slot, and `[ZERO_ZV; NSLOT]` initialises all 42 before the
first call site. ⚠ The array is `[Zv; 42]` and not `[Op; 128]`: a reviewer
checking that the bound matches the array is checking a different pair here than
in `oset`. **(c)** `i`, `NSLOT`, `x`, `old(a)@`, `final(a)@`; none is
`#[cfg]`-dependent.

#### SLB-TRUSTED-ARGUMENT verus.rs tget

**(a)** `*a.get_unchecked(i)` on a `&[u16; MAX_STMT]` against `a[i]`. **(b)** One
read at `i`, returned; `r == a@[i as int]`, no post-state. **(c)** `i`,
`MAX_STMT` (= 64) and `a@`. ⚠ **The bound is `MAX_STMT`, not `NSLOT` and not
`MAX_OPS`** — `EX(Ts)` has one slot per STATEMENT — and this file has THREE
different array bounds in play, which is the thing a reviewer of this section
has to keep apart. `tmp_of`'s `% MAX_STMT` is what establishes it at every call
site.

#### SLB-TRUSTED-ARGUMENT verus.rs tset

**(a)** `*a.get_unchecked_mut(i) = x` against `a[i] = x`. **(b)** One store; the
`ensures` is the whole post-state. `x: u16` is a pure value. **(c)** `i`,
`MAX_STMT`, `x`, `old(a)@`, `final(a)@`; none is `#[cfg]`-dependent.

#### SLB-TRUSTED-ARGUMENT verus.rs nget

**(a)** `*a.get_unchecked(i)` on a `&[u16; NVAR]` against `a[i]`. **(b)** One
read at `i`, returned; `r == a@[i as int]`, no post-state. **(c)** `i`, `NVAR`
(= 8) and `a@`. ⚠ This is the NARROWEST of the four bounds and the one
established from a value the INPUT controls: `a` comes from
`cz.lval % (NVAR as u64)`, where `cz.lval` is whatever the decoded record put
in the container slot. The modulus is what makes it sound, and it is in the exec
text of all four Rust rungs identically.

#### SLB-TRUSTED-ARGUMENT verus.rs nset

**(a)** `*a.get_unchecked_mut(i) = x` against `a[i] = x`. **(b)** One store; the
`ensures` is the whole post-state `old(a)@.update(i as int, x)`. `x: u16` is a
pure value. **(c)** `i`, `NVAR`, `x`, `old(a)@`, `final(a)@`; none is
`#[cfg]`-dependent.

#### SLB-TRUSTED-ARGUMENT verus.rs zunwrap

⭐⭐⭐ **THE ROW'S OWN TRUSTED ITEM, AND THE ONLY ONE OF THE TEN THAT IS NOT AN
INDEX.**

**(a)** The unchecked operation is `t.unwrap_unchecked()` on an
`Option<usize>`; the twin is `t.unwrap()`, which is the same projection with the
`None` test Rust would have emitted. ⚠ **Neither TESTS the operand** — `unwrap`
panics, it does not take a different path — so the twin is the right stand-in
for what C does at `zend_execute.c:3973`, which is to assume and read.
**(b)** The body performs exactly one operation and it is the projection;
`r == t.unwrap()` names its result and there is no post-state, because `t` is
taken by value and `usize` is `Copy`. There is no second parameter to leave
unconstrained — the shape this stage exists to catch cannot arise here, because
the ONLY thing that can make `t.unwrap_unchecked()` undefined is `t` itself.
**(c)** `t.is_some()` and `r == t.unwrap()` name only the parameter and the
return value; `Option<usize>` is `core`'s and carries no `#[cfg]`.

⚠ **What makes this entry worth reading is where the precondition comes from.**
Not from arithmetic and not from the caller's convenience: from the COMPILER.
`operand_present` is the compile pass's loop invariant, it holds only because
`case BP_VAR_IS:` refuses an append dim, and that refusal is `1e708a5aeb30`.
`controls/negatives.py --emit r1` deletes the three lines and the mutant must
FAIL — measured, `65 verified / 1 error`, and the error is the `assert forall`
that re-establishes `operand_present`.

---

## §12 ⭐⭐⭐ THE STATISTIC — and on this row **the cross-language sign depends on which one you pick**

⛔ **Everything in this section is `O3`, and every percentage names five things:
STATISTIC · INPUT · OPT/MODE · BASE · and, where the base is a C cell, WHICH
COMPILER — with BOTH C columns.** No `O0` figure is quoted as a performance
result and none is measured into this section. Produced by
`controls/statistic.py` (`statistic.json`), with the family-B half from
`.tasks-php/php50_align_sweep.py` (§12d).

ⓘ **The two shapes**: `small.bin` is a 128-byte window = **16 statement
records**; `large.bin` is 512 bytes = **64**. Both at 20 000 driver iterations.

### 12a ⭐⭐ `inside_share` PER CELL, BEFORE ANY STATISTIC IS CHOSEN

`inside_share` = A1 / W1 = (the `kernel` symbol's exclusive Ir) / (the whole
program's Ir), per call, O3/isolated.

| cell | `small.bin` | `large.bin` |
|---|---:|---:|
| `c-gcc` (R1) | **0.8848** | **0.8547** |
| `c-gcc-h` (R1h) | **0.8856** | **0.8560** |
| `c-clang` (R1) | 0.9368 | 0.9791 |
| `c-clang-h` (R1h) | 0.9371 | 0.9792 |
| `safe_naive` (R2) | 0.9761 | 0.9922 |
| `safe_tuned` (R3) | 0.9720 | 0.9905 |
| `unsafe` (R4) | 0.9707 | 0.9897 |
| `verus` (R5) | 0.9707 | 0.9897 |

⚠⚠ **READ THE GCC ROW.** gcc keeps **11.4 % of the per-call work on `small.bin`
and 14.5 % on `large.bin` OUTSIDE the `kernel` symbol** — in callees it chose
not to inline — where the four Rust cells keep 0.8–2.9 % outside. The gap
between `c-gcc-h` and the Rust cells is **0.085 to 0.137**, far past
`STATISTICS_001.md` §1's `0.02` threshold.

⭐ **Exactly one pair set is NARROW**: the Rust cells against `c-clang-h` **on
`large.bin`**, where the gap is **0.0104 to 0.0130**. `controls/statistic.py`
pins that set in `DECLARED_NARROW` and checks the two halves in OPPOSITE
directions (arms 7 and 8), so neither the wide claim nor the narrow one can rot
silently.

⛔⛔ **AND A HIGH SHARE IS STILL NOT A CERTIFICATE.** `ph55`'s two C cells —
`c-gcc` and `c-clang` — sit at 74–83 % and A1 reads `0.000 %` on that row's own
defect site anyway (base there: the R1 cell of the same compiler), because
what matters is not how much of the cell A1 sees but whether **THE DIFFERENCE**
lands inside it. §12b is this row's answer to that question and it is the
opposite of `ph55`'s.

### 12b ⭐⭐⭐ A1 **SEES** THIS ROW'S FIX, WHERE IT WAS BLIND TO `ph55`'s

R1 → R1h, both families, **both compilers**. Base is the R1 cell of the SAME
compiler; statistic named per column; O3/isolated.

| input | pair | **A1** Ir/call | **A1 %** | **W1** Ir/call | **W1 %** |
|---|---|---:|---:|---:|---:|
| `small.bin` | `c-gcc` → `c-gcc-h` | **+24.422** | **+0.753 %** | +24.419 | +0.666 % |
| `small.bin` | `c-clang` → `c-clang-h` | **+17.377** | **+0.587 %** | +17.378 | +0.550 % |
| `large.bin` | `c-gcc` → `c-gcc-h` | **+99.425** | **+1.073 %** | +99.423 | +0.917 % |
| `large.bin` | `c-clang` → `c-clang-h` | **+68.044** | **+0.725 %** | +68.045 | +0.710 % |

⭐ **Non-zero on all four, in both families**, where `ph55` measures *exactly*
`0.000 %` in A1 on both of its C cells, `c-gcc` and `c-clang`, against the same
R1-cell base. ▶ **The difference between the two rows
is not the defect: it is whether the path from the kernel symbol to the fix goes
through a function pointer.** `ph55`'s three lines live in a handler reached
through `opline->handler`, which cannot be inlined; `ph56`'s live in
`ph56_do_end_variable_parse`, a `static` called from an ordinary loop, which
both compilers inline into `kernel` at O3.

### 12c ⭐⭐ PREDICTION 2, MEASURED: THE GUARD RUNS ONCE PER EMITTED OPLINE

The task predicts *"the R1h costs ~nothing at run time — the guard is in the
COMPILER, so it runs once per emitted opline, not per execution"*. Dividing
§12b's A1 deltas by the statement count:

| compiler | `small.bin` (16 stmts) | `large.bin` (64 stmts) |
|---|---:|---:|
| gcc | **1.526** Ir per emitted statement | **1.554** |
| clang | **1.086** | **1.063** |

⭐ **The per-statement cost is flat across a 4× change in statement count** —
1.53 vs 1.55 for gcc, 1.09 vs 1.06 for clang. That is the mechanism confirmed by
the number: the guard is paid **once per opline the compiler emits**, not once
per execution of anything.

⚠⚠ **AND THE PERCENTAGE IS NOT PHP's.** §8 states it and it is restated here
because this is where the number appears: `kernel()` **compiles and then
executes on every call**, where PHP compiles once per script and executes many
times. **`+0.753 %` / `+0.587 %` (A1, O3/isolated, base = the R1 cell of the
same compiler) is a LOOSE UPPER BOUND on PHP's cost of `1e708a5aeb30` and may
not be quoted as PHP's cost of it.** What may be quoted is the per-opline figure
above, because that quantity is the same in both harnesses.

### 12d ⛔⛔ THE CROSS-LANGUAGE COLUMN — and it changes SIGN between the families

Statistic named per column; input named per row; O3/isolated; bases
`c-gcc-h` and `c-clang-h` (the R1h cells, so the C side is the fixed program the
Rust rungs implement).

| rust cell | input | **A1** vs `c-gcc-h` | **A1** vs `c-clang-h` | **W1** vs `c-gcc-h` | **W1** vs `c-clang-h` |
|---|---|---:|---:|---:|---:|
| `safe_naive` (R2) | `small.bin` | +28.232 % | +40.716 % | +16.344 % | +35.103 % |
| `safe_tuned` (R3) | `small.bin` | +8.994 % | +19.605 % | **−0.694 %** | +15.318 % |
| `unsafe` (R4) | `small.bin` | +3.922 % | +14.039 % | **−5.185 %** | +10.103 % |
| `verus` (R5) | `small.bin` | +3.922 % | +14.039 % | **−5.185 %** | +10.103 % |
| `safe_naive` (R2) | `large.bin` | +41.172 % | +39.891 % | +21.787 % | +38.057 % |
| `safe_tuned` (R3) | `large.bin` | +14.854 % | +13.812 % | **−0.741 %** | +12.520 % |
| `unsafe` (R4) | `large.bin` | +5.879 % | +4.918 % | **−8.423 %** | +3.811 % |
| `verus` (R5) | `large.bin` | +5.879 % | +4.918 % | **−8.423 %** | +3.811 % |

> ### ⛔⛔⛔ THE SIGN FLIPS BETWEEN THE TWO FAMILIES, AGAINST GCC, ON SIX OF THE
> EIGHT ROWS. R4 against `c-gcc-h` on `large.bin` is **+5.879 % in A1** and
> **−8.423 % in W1** — *the same pair of binaries, the same input, the same
> optimisation level, dearer or cheaper depending on the statistic*. Against
> `c-clang-h` the sign is stable positive in both families.

⭐ **`inside_share` predicts it exactly**, which is the point of publishing §12a
first: `c-gcc` and `c-gcc-h` hide 11–15 % of their per-call work in callees A1
does not sum, so A1 compares 88 % of the `c-gcc-h` program against 97–99 % of
the Rust one. **The
difference does not land inside the symbol on the gcc cells**, so per
`STATISTICS_001.md` §1 the gcc column may NOT be quoted in A1 and **W1 is the
statistic for it**. The clang column on `large.bin` is the one pair set where
the shares are within `0.02` and A1 IS admissible.

▶ **What this row therefore publishes as its cross-language figure**, and it
names all five things: ⭐ **R4/R5 against the R1h C cells, W1, O3/isolated,
`large.bin`: −8.423 % against `c-gcc-h` and +3.811 % against `c-clang-h`.**
Two C columns, two signs, and the row says so rather than picking the flattering
one — **F108 in a single line.**

### 12e THE LADDER, AND R5 COSTS **EXACTLY** R4

A1, O3/isolated, base named per column.

| step | `small.bin` | `large.bin` |
|---|---:|---:|
| R2 → R3 (`safe_naive` → `safe_tuned`) | −628.731 Ir/call, **−15.003 %** | −2465.411 Ir/call, **−18.642 %** |
| R3 → R4 (`safe_tuned` → `unsafe`) | −165.749 Ir/call, **−4.653 %** | −840.748 Ir/call, **−7.814 %** |
| R4 → R5 (`unsafe` → `verus`) | **0.000 Ir/call, 0.000 %** | **0.000 Ir/call, 0.000 %** |

⭐⭐⭐ **R4 → R5 IS EXACTLY ZERO ON BOTH INPUTS AND IN BOTH FAMILIES** (§12f has
the family-B half). `ph55` paid **+0.071 %** on the same pair. The reason is
§11.3: this row's R4 and R5 are **one exec text**, so the compiler emits the same
instruction sequence and the binaries differ only in relocation bytes
(`md5_fn_norel` and `md5_norm` identical at both O0 and O3 isolated — measured,
and `spec.md`'s `identity` pins `norel` on the strength of it).

⭐ **The R3 → R4 step is this row's own `unsafe`.** Nine of the ten trusted
accessors are ordinary unchecked indexing; the tenth, `zunwrap`, is the check
whose absence is CRASH-041. **−4.653 % / −7.814 % (A1, O3/isolated, base = R3)
is what the whole trusted surface buys**, and the row does NOT attribute it to
`zunwrap` alone — nothing here decomposes it, and `ph55`'s
`controls/spellings.py` is the shape that would (that search is **NOT** done on
this row; §13).

### 12f ⛔ FAMILY B, THROUGH `PROTOCOL_PHP.md` §B5's SWEEP — two verdicts per pair

`.tasks-php/php50_align_sweep.py --row ph56-fetchmode-arith --pads 32`, a full
32-residue argv pad sweep, O3/isolated, `dcalls=100`.

**Measured step per cell**: `c-clang` **7.0** Ir/call, `c-clang-h` **7.0**, and
**0.0** for `c-gcc`, `c-gcc-h`, `safe_naive`, `safe_tuned`, `unsafe`, `verus`.
ⓘ Corpus-wide the step takes `0.00`, `0.02`, `7.00` and `34.49`; this row draws
two of those four, in the same record.

| input | pair | median Ir/call | range | \|d\|/step | magnitude | sign |
|---|---|---:|---:|---:|---|---|
| `small.bin` | `c-clang` → `c-clang-h` | +17.53 | 14.00 | 1.25 | ⛔ **NOT RESOLVABLE** | ✅ SIGN-STABLE |
| `small.bin` | `c-gcc` → `c-gcc-h` | +24.41 | 0.00 | n/a | ✅ RESOLVABLE | ✅ SIGN-STABLE |
| `small.bin` | `c-gcc-h` → `safe_tuned` | −31.99 | 0.00 | n/a | ✅ RESOLVABLE | ✅ SIGN-STABLE |
| `small.bin` | `c-gcc-h` → `unsafe` | −197.87 | 0.00 | n/a | ✅ RESOLVABLE | ✅ SIGN-STABLE |
| `small.bin` | `c-clang-h` → `safe_tuned` | +486.00 | 7.00 | 69.43 | ✅ RESOLVABLE | ✅ SIGN-STABLE |
| `small.bin` | `c-clang-h` → `unsafe` | +320.12 | 7.00 | 45.73 | ✅ RESOLVABLE | ✅ SIGN-STABLE |
| `small.bin` | `safe_naive` → `safe_tuned` | −628.60 | 0.00 | n/a | ✅ RESOLVABLE | ✅ SIGN-STABLE |
| `small.bin` | `safe_tuned` → `unsafe` | −165.88 | 0.00 | n/a | ✅ RESOLVABLE | ✅ SIGN-STABLE |
| `small.bin` | `unsafe` → `verus` | **0.00** | 0.00 | n/a | ✅ RESOLVABLE | ✅ SIGN-ZERO |
| `large.bin` | `c-clang` → `c-clang-h` | +70.76 | 14.00 | 5.05 | ✅ RESOLVABLE | ✅ SIGN-STABLE |
| `large.bin` | `c-gcc` → `c-gcc-h` | +101.61 | 0.00 | n/a | ✅ RESOLVABLE | ✅ SIGN-STABLE |
| `large.bin` | `c-gcc-h` → `safe_tuned` | −74.96 | 0.00 | n/a | ✅ RESOLVABLE | ✅ SIGN-STABLE |
| `large.bin` | `c-gcc-h` → `unsafe` | −917.45 | 0.00 | n/a | ✅ RESOLVABLE | ✅ SIGN-STABLE |
| `large.bin` | `c-clang-h` → `safe_tuned` | +1209.31 | 7.00 | 172.76 | ✅ RESOLVABLE | ✅ SIGN-STABLE |
| `large.bin` | `c-clang-h` → `unsafe` | +366.82 | 7.00 | 52.40 | ✅ RESOLVABLE | ✅ SIGN-STABLE |
| `large.bin` | `safe_naive` → `safe_tuned` | −2463.50 | 0.00 | n/a | ✅ RESOLVABLE | ✅ SIGN-STABLE |
| `large.bin` | `safe_tuned` → `unsafe` | −842.49 | 0.00 | n/a | ✅ RESOLVABLE | ✅ SIGN-STABLE |
| `large.bin` | `unsafe` → `verus` | **0.00** | 0.00 | n/a | ✅ RESOLVABLE | ✅ SIGN-ZERO |

⛔ **ONE PAIR IS NOT PUBLISHABLE AS A MAGNITUDE**: `c-clang` → `c-clang-h` on
`small.bin` is `+17.53` with a range of `14.00` over the pad sweep, i.e.
`|d|/step = 1.25`. **Its SIGN is sound and its SIZE is not**, and this row does
not quote `+17.53 Ir/call` as a family-B figure. The A1 figure for that pair
(`+17.377 Ir/call`, §12b) is a different statistic taken on the `kernel` symbol
and is not subject to it.

⭐ **Everything else clears.** In particular the three figures this row leans on
— `safe_tuned` → `unsafe` (−165.88 / −842.49), `unsafe` → `verus` (0.00 / 0.00)
and `c-gcc-h` → `unsafe` (−197.87 / −917.45) — all have **range 0.00 across all
32 residues**, so their magnitudes are resolvable and their signs stable.

⭐⭐ **AND THE TWO FAMILIES AGREE ON THE R3 → R4 STEP TO WITHIN 0.2 Ir**:
A1 gives −165.749 / −840.748 and family B gives −165.88 / −842.49. The price of
this row's own `unsafe` is the one figure that does not depend on which
statistic you pick.

### 12g ⚠ The family-B cross-language sign flips between the two COMPILERS too

Family B, O3/isolated, medians from §12f: against `c-gcc-h` the R3 and R4 cells
are **cheaper** (−31.99 / −197.87 on `small.bin`, −74.96 / −917.45 on
`large.bin`); against `c-clang-h` they are **dearer** (+486.00 / +320.12 and
+1209.31 / +366.82). ▶ **So on this row the cross-language sign depends on the
STATISTIC *and* on the C COMPILER, independently.** A single C column would have
been a different answer, not a noisier one.

---

## §13 ⭐ WHAT THIS ROW DOES **NOT** HAVE

Stated so nobody infers it from the presence of the other controls.

1. ⛔ **No in-contract RESPELLING SEARCH.** `ph55` ships
   `controls/spellings.py` as a search — it reverts each R3 lever one at a time
   and reduces the R4 trusted surface one class at a time, and prices each in
   Ir. **This row's file of the same name is the CONTRACT AUDIT only** (every
   backticked pin × every rung), and says so in its own docstring. ▶ **So the
   R2 → R3 and R3 → R4 numbers in §12e are the SHIPPED cells and nothing else:
   no in-contract spread on either side, and no decomposition of the R3 → R4
   step into `zunwrap` versus the nine index accessors.** That is the row's
   largest gap and it is a separate task's work.
2. ⛔ **No `controls/argv_align.py`.** The family-B alignment question is
   answered by the corpus-wide `.tasks-php/php50_align_sweep.py` (§12f) rather
   than by a per-row control.
3. ⛔ **No endpoint search.** `spec.md` pins R3 and R4 by IDIOM, chosen before
   measurement, which is what makes `R3ship − R4ship` a bound rather than a
   difference of two minima. `ph45` and `ph52` both reversed their ordering
   under search and `ph55` refuted its endpoint prediction in both halves with
   the signs exactly swapped — so **no prediction about this row's endpoints is
   made here**, and none should be read into §12e.
4. ⚠ **The R1h was not verified against a rebuilt PHP.** §8.1 of
   `TASK_PHP_051`'s report asked for it: rebuild 5.0.0 with `1e708a5aeb30`
   applied and re-run the six census snippets. That the fix also kills
   `isset($a[][0])` is an inference from the source plus a measurement in the
   kernel, and it is **not** confirmed on the real interpreter. It is still the
   cheapest remaining check on this row.
