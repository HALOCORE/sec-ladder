# TASK_PHP_019_REPORT — the MECHANISM test on every surviving duplication kill

**Role: investigator / adjudicator, one agent.** Population: `CATALOGUE.md` §C.1,
all 13 rows, plus §C.4's set enumeration. **Nothing outside this file and
`.temp/php19/` was written.** No `git add`, no `git commit`. `.web/` untouched.

Every `file:line` below was opened in the pinned tarball
(sha256 `5783e0c0…d6919`, verified this run) with `grep -a` / `/usr/bin/grep`
only. Re-derive the source with `.temp/php19/extract.sh`.

---

## §0 THE ANSWER, IN FIVE LINES

1. **Of 13 kills, 2 are correct exactly as written.** `CRASH-090 → ph32` and
   `CRASH-037 → ph39`.
2. **2 more are correct verdicts merged into the wrong row.** `CRASH-101` is
   `ph41`'s mechanism, not `ph39`'s — and `ph41`'s own block says *"Do not fold
   into ph39."* `LOGIC-014` is `ph48`'s mechanism, not `ph47`'s — and `ph48` is
   the row `C.1`'s own sentence says was **kept** for that reason.
3. **9 fail the mechanism test.** 8 become new rows `ph94`–`ph101`; the ninth
   (`V5C-116`) reverses but must **not** become a row, because `ph03` is already
   built over both defects and **has already measured them apart** — 144 of
   12 600 documents still read past the source with `V5C-115`'s complete upstream
   fix applied (`ph03/spec.md`, lines 91-95).
4. ⭐ **`"merged by the corpus itself"` does not mean what `C.1` used it to mean.**
   The corpus's merge predicate is *root cause* with the **burden of proof set on
   `distinct`, not on `same`** (`validation/REPORT.md`, "Method"). Ours is *exact
   C mechanism* with the burden on `same`. Worse: **all three of those merges
   were flagged by the corpus's own per-case validators as covering two
   separately-fixed defects**, in writing, in `verdicts.json`, before the merge.
   **The strongest-looking evidence in `C.1` was the weakest.**
5. ⚠ **One row cannot be decided from the bar as written** — `CRASH-090 → ph32`,
   where the corpus's own adversarial verifier broke the identical merge with
   binary and runtime evidence. §7 states the open question rather than forcing a
   verdict.

---

## §1 Verdict table

Rule applied, stated before the rows so it can be attacked (§7 discusses it):

> **EXACT** ⇔ the two sites agree on all three of (a) the **unchecked predicate**,
> (b) the **attacker-controlled quantity**, (c) the **fault primitive**. Then the
> extracted kernels differ only in identifiers and data.
> **SLIGHT VARIATION** ⇔ exactly one differs → `PLAN_PHP.md` §3.1 **admits** it.
> **DIFFERENT MECHANISM** ⇔ two or more differ, **or** the two defects have
> different upstream fixes each of which leaves the other standing.

⚠ **Mechanism *quality* was not used, in either direction.** No row was admitted
because it is "better" and none was killed because it is "worse". Duplication
with `patterns/` was not considered at all.

| # | kill | into | verdict | outcome |
|---|---|---|---|---|
| 1 | `CRASH-090` html.c:155/:401 | ph32 | **EXACT** | ✅ kill stands · note rewritten · ⚠ see §7 |
| 2 | `V5C-116` uuencode.c:145 | ph03 | **DIFFERENT MECHANISM** | ⚠ kill reverses — **no new row**; `ph03` already carries and measures both (§2.2) |
| 3 | `V5C-173` zend_execute.c:4033 | ph11 | **DIFFERENT MECHANISM** | → **`ph94`** |
| 4 | `V5C-015` pack.c:212/:262 | ph22 | **SLIGHT VARIATION** | → **`ph95`** |
| 5 | `CRASH-037` zend_exceptions.c:339 | ph39 | **EXACT** | ✅ kill stands · note rewritten |
| 6 | `CRASH-101` streamsfuncs.c:817 | ph39 | **EXACT — but against `ph41`** | ✅ kill stands · **merge target corrected** |
| 7 | `CRASH-061` zend_object_handlers.c:513 | ph60 | **SLIGHT VARIATION** | → **`ph96`** |
| 8 | `CRASH-126` mbstring.c:3219 | ph60 | **DIFFERENT MECHANISM** | → **`ph97`** (confirms `ADJUDICATION_002` §5) |
| 9 | `CRASH-163` zend.c:1083 | ph60 | **DIFFERENT MECHANISM** | → **`ph98`** (confirms `ADJUDICATION_002` §5) |
| 10 | `LOGIC-003` zend_object_handlers.c:296-300 | ph47 | **DIFFERENT MECHANISM** | → **`ph99`** |
| 11 | `LOGIC-008` zend_object_handlers.c:797 | ph47 | **DIFFERENT MECHANISM** | → **`ph100`** |
| 12 | `LOGIC-014` zend_builtin_functions.c:1420 | ph47 | **EXACT — but against `ph48`** | ✅ kill stands · **merge target corrected** |
| 13 | `LOGIC-018` zend_compile.c:1899-1900 | ph47 | **DIFFERENT MECHANISM** | → **`ph101`** |

**Citations: 13/13 resolve, in both directions.** Every kill line and every
surviving row's line was opened. No `F23` repeat. Two riders:
`ph32`'s block says the index is at `:900` and `:905`; there is a **third** at
`:906` (`strncpy`). `CRASH-061`'s `index.csv` cell already corrects the claimed
`:479` to `:513` — ✅ confirmed, `zend_std_unset_dimension` starts at `:506`.

---

## §2 The rows, with the C

### 2.1 `CRASH-090 → ph32` — **EXACT.** Kill stands.

```c
/* html.c:155 */  static entity_table_t ent_uni_punct[] = {   /* 66 initialisers */
/* html.c:401 */      { cs_utf_8,  8194, 8260, ent_uni_punct },   /* declares 67 */
/* html.c:398 */      { cs_utf_8,  338,  402,  ent_uni_338_402 },  /* declares 65, has 63 */
/* html.c:896 */  for (k = entity_map[j].basechar; k <= entity_map[j].endchar; k++) {
/* html.c:900 */      if (entity_map[j].table[k - entity_map[j].basechar] == NULL)
```
(a) unchecked: no relation between `endchar - basechar + 1` and the literal's
element count. (b) attacker: input text plus the charset selector, reaching the
top of a short table's range. (c) primitive: global-buffer-overflow **read** of a
`char *` at `:900`/`:905`/`:906`, index computed in `int` (`int j, k;` at
`html.c:877`). **All three identical. Only the data literal and the shortfall
(2 vs 1) differ** — the extracted kernel differs in no statement, expression,
type or guard. ⚠ **The corpus disagrees; §7.**

### 2.2 `V5C-116 → ph03` — **DIFFERENT MECHANISM.** Kill reverses; no new row.

The kill note is *"same loop, same bound"*. **The bound is what differs, and it
is the one thing the two triggers do not share.**

```c
/* uuencode.c:141 */  ee = s + (len == 45 ? 60 : (int) floor(len * 1.33));
/* uuencode.c:143 */  while (s < ee) {
/* uuencode.c:144 */      *p++ = PHP_UU_DEC(*s)       << 2 | PHP_UU_DEC(*(s + 1)) >> 4;
/* uuencode.c:145 */      *p++ = PHP_UU_DEC(*(s + 1)) << 4 | PHP_UU_DEC(*(s + 2)) >> 2;
/* uuencode.c:146 */      *p++ = PHP_UU_DEC(*(s + 2)) << 6 | PHP_UU_DEC(*(s + 3));
/* uuencode.c:147 */      s += 4;
```
- **ph03 / V5C-115** — unchecked: `ee <= e`. Trigger `"MAAA"`: `len = 45`,
  `ee = s+60`, `e = src+4`. **The bound is wrong.** Primitive: over-read **and**
  over-write through `p` past `emalloc(ceil(src_len*0.75)+1)`.
- **V5C-116** — unchecked: `s + 4 <= e`. Trigger (corpus reproducer, second line
  `"a."`): `PHP_UU_DEC('a') = 1`, `ee = s + floor(1*1.33) = s+1 == e` **exactly**,
  and `len(1) < src_len(64)`. **The bound is correct and the read still leaves the
  buffer**, because the loop *tests* at 1-byte granularity and the body *consumes*
  4. Primitive: ≤3-byte source over-read only; the destination write is in bounds.

All three of (a)(b)(c) differ. **Two different upstream fixes:**
`f95c1df58349` (2004, `len > src_len` + `ee > e`) does **not** repair V5C-116 —
the corpus verified that by arithmetic. And ⭐ **this project has already
measured it**, in the built row:

> `patterns-php/ph03-uudecode-bound/spec.md`: *"The 2004 fix is **incomplete**…
> with the 2004 fix applied, **0 write past `emalloc` and 144 still read past the
> source**"* — over 12 600 documents — which is why `R2–R5` carry
> `1e2818b14376` (2014, `s + 4 > e`) as a separate check and
> `verus.rs` cannot verify without it (`controls/negatives.py --emit no2014`).

**So the kill note is contradicted by the gate record of the very row it merges
into.** ⚠ **But the remedy is NOT a new `phNN`.** `ph03` extracts the whole of
`php_uudecode` and already ships both defects in `R1`, both fixes as separate
rung-level hunks, and a control for the residual. A second row would re-extract
the same function and **double-count a ladder cost paid once** — the argument
`ph04`'s and `ph43`'s own risk notes already make. `ph03`'s Part A cell already
names `V5C-116`. **What is owed is the corrected note (§4) and one sentence in
`ph03`'s Part B block (§4).**

### 2.3 `V5C-173 → ph11` — **DIFFERENT MECHANISM.** → `ph94`.

Same line. Not the same defect.

```c
/* zend_execute.c:4025 */  } else if ((*container)->type == IS_STRING) { /* string offsets */
/* zend_execute.c:4033 */      if (offset->value.lval <= Z_STRLEN_PP(container) && Z_STRVAL_PP(container)[offset->value.lval] != '0') {
/* zend.h:270-273 */  struct _zend_object_value { zend_object_handle handle; zend_object_handlers *handlers; };
/* zend.h:275-284 */  typedef union _zvalue_value { long lval; … zend_object_value obj; } zvalue_value;
```
- **ph11 / V5C-145** — unchecked: **the range**, `0 <= i` (and `<` vs `<=`).
  Attacker: a **negative `long`** subscript. Primitive: OOB read at a chosen
  displacement (`empty($s[-1000000])`). CWE-125.
- **V5C-173** — unchecked: **the type tag**. There is no type test and no
  `convert_to_long` anywhere in the arm (`:4025-4037`, read in full). For an
  `IS_OBJECT` offset, `value.lval` overlays `value.obj`, i.e. on LP64
  `[4-byte handle | 4 bytes of struct padding that `zend_objects_new`'s
  stack-returned `zend_object_value` never writes]`. Attacker: merely supplying
  an object. **The index is uninitialised memory, not a program value.** CWE-843.

(a) and (b) differ; (c) differs in kind — an uninitialised-value read that then
becomes a wild byte read. ⭐ **The corpus's own per-case validator says so**:
*"They are genuinely two distinct source-level mistakes on one line, but a
strict per-line/per-fix dedup would merge them"* (`verdicts.json`, V5C-173).
Corroborated (⚠ *corroborated only* — `F2`: the reproducer header is not
authoritative) by `crashes/roundE/V5C-173-1f4f33afcfd8.php`, whose header carries
a valgrind trace *"Uninitialised value was created by a stack allocation at
zend_objects_new (zend_objects.c:94)"* and the sentence **"NOT the same defect as
V5C-145 (same sink line)"**. The union layout I re-derived from `zend.h` myself.

### 2.4 `V5C-015 → ph22` — **SLIGHT VARIATION.** → `ph95`.

The kill note is *"same two-pass sizing mismatch"*. That half is true. It is not
the whole defect.

```c
/* pack.c:174-190  "Always uses one arg"  — ph22's 'H' arm */
    case 'h': case 'H':
        if (currentarg >= argc) { … RETURN_FALSE; }
        …
        currentarg++;
/* pack.c:194-221  "Use as many args as specified" — V5C-015's 's' arm */
    case 's': case 'S': case 'n': case 'v': …
        if (arg < 0) { arg = argc - currentarg; }
/* pack.c:212 */    currentarg += arg;
/* pack.c:214 */    if (currentarg > argc) { … RETURN_FALSE; }
/* pack.c:247 */  outputpos += (arg + 1) / 2;   /* ph22 */
/* pack.c:262 */  outputpos += arg * 2;         /* V5C-015 */
/* pack.c:304 */  output = emalloc(outputsize + 1);
```
✅ **`ph22`'s trigger cannot reach `:212`.** `H` is in the *"Always uses one
arg"* arm (`:174-191`), which does `currentarg++` and has **no** `currentarg +=
arg` and no wrapping guard. So `ph22` has exactly one mechanism: an unguarded
`int` sizing accumulator.

`V5C-015` has **two, chained**: with `arg = INT_MAX`, `:212` wraps `currentarg`
to `INT_MIN` so **the guard at `:214` — which exists, and runs — is false**;
only then does `:262` compute `INT_MAX*2 = -2`. **A guard defeated by the wrap of
its own operand** is not in `ph22` and is not anywhere else in the catalogue.
⭐ The corpus's own validator asked for exactly this split: *"The `currentarg +=
arg;` overflow at :212 is genuinely distinct (different fix commit, 2019) and is
unique to this case; if the two pack cases are merged, **keep :212 as the
distinguishing member**"* (`verdicts.json`, V5C-015). Two upstream commits:
`6d98fc38b53` (2004) repairs `:262`; `db420cb6a14` (2019, bug #78833) adds
`if (currentarg > INT_MAX - arg)` before `:212`. Neither repairs the other.

`ph95`'s claim is the `:212` guard-defeat, not the sizing.

### 2.5 `CRASH-037 → ph39` — **EXACT.** Kill stands.

```c
/* zend_exceptions.c:551 (ph39/CRASH-036) */
    zend_error_va(E_ERROR, Z_STRVAL_P(file), Z_LVAL_P(line), "Uncaught %s\n  thrown", Z_STRVAL_P(str));
/* zend_exceptions.c:339 (CRASH-037) */
    zend_hash_apply_with_arguments(Z_ARRVAL_P(trace), (apply_func_args_t)_build_trace_string, 3, str, len, &num);
/* :338 */  trace = zend_read_property(default_exception_ce, getThis(), "trace", sizeof("trace")-1, 1 TSRMLS_CC);
```
(a) unchecked: the `type` tag, before a `Z_*VAL_P` macro that consults no tag —
identical. (b) attacker: the type of a userland-settable property, set through
`unserialize` — identical. (c) primitive: **an attacker-chosen `long`
dereferenced as a pointer** — identical; only the static type imposed on it
differs (`char *` vs `HashTable *`). The kernel is the same `(tag, payload)`
record fold with a different member selected. ✅ **Kill stands.** The one real
difference (the confused type, hence the shape of the primitive) belongs in
`ph39`'s block as a rider, not as a row — §4.

### 2.6 `CRASH-101 → ph39` — **EXACT, but against `ph41`.** Merge target corrected.

```c
/* streamsfuncs.c:917 */  if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "ra", &zcontext, &params) == FAILURE) …
/* streamsfuncs.c:816 */  if (SUCCESS == zend_hash_find(Z_ARRVAL_P(params), "options", sizeof("options"), (void**)&tmp)) {
/* streamsfuncs.c:817 */      parse_context_options(context, *tmp);
/* streamsfuncs.c:775 */  zend_hash_internal_pointer_reset_ex(Z_ARRVAL_P(options), &pos);
/* streamsfuncs.c:778 */          && Z_TYPE_PP(wval) == IS_ARRAY) {     /* ← the check, one level down */
```
The container `params` **is** type-checked — `"a"` at `:917`. The **element**
`*tmp` is not, and `:775` reads it as a `HashTable *`. Reproducer:
`stream_context_set_params($ctx, array("options" => 1));`.

That is **`ph41` — *"container checked, elements not"*** (`zend_exceptions.c:293`,
`HashTable *ht = Z_ARRVAL_PP(frame);`), on all three of (a)(b)(c). It is **not**
`ph39`, whose block is headed *"no tag check **of any kind**"* — and ⚠ **`ph41`'s
own `⚠ risk` line says *"the container/element split is the mechanism. Do not
fold into ph39."*** `C.1` folded it into `ph39`.

**Kill stands; `CRASH-101` moves from `ph39`'s `corpus rows` to `ph41`'s.**
One residual C fact worth carrying as a rider on `ph41`, **not as a row**: the
identical tag test is *present at depth 2* (`:778`) and *absent at depth 1*.
I graded that as context rather than mechanism; it is the closest call in the
"stands" column and I say so rather than hiding it.

### 2.7 `CRASH-061 → ph60` — **SLIGHT VARIATION.** → `ph96`.

The note says *"same fallible call's failure not tested"*. **The call does not
fail.**

```c
/* zend_object_handlers.c:509 */  zval *retval;
/* zend_object_handlers.c:512 */  zend_call_method_with_1_params(&object, ce, NULL, "offsetunset", &retval, offset);
/* zend_object_handlers.c:513 */  zval_ptr_dtor(&retval);
/* zend_execute_API.c:592-595 */
    /* we may return SUCCESS, and yet retval may be uninitialized,
     * if there was an exception...  */
    *fci->retval_ptr_ptr = NULL;
```
- **ph60 / CRASH-088** — `stream = php_ftp_fopen_connect(…)` at `:649` **returns
  NULL**; `:652` uses it. One output; testing it is sufficient.
- **CRASH-061** — two outputs. `zend_call_function` returns **SUCCESS** when the
  userland `offsetUnset` throws, and NULLs the out-parameter **on purpose, with
  the comment above quoted verbatim from the tarball.** Testing the status —
  the obvious guard — does not help. Trigger: `unset($c[0])` where `offsetUnset`
  throws.

(a) differs: the unchecked predicate is *"is the out-parameter NULL **despite**
SUCCESS"*, not *"is the return NULL"*. (b) and (c) match. **One difference →
SLIGHT VARIATION → §3.1 admits it.** ⚠ This is the weakest of my three `ph60`
admissions and it is graded at the minimum the evidence carries. Checked against
`ph50` (*"a discarded status code leaves an out-parameter unwritten"*) and
`ph87`'s `I12` limb: in both of those the slot is **never written** (garbage); here
it is written, to NULL, by contract. Not the same.

### 2.8 `CRASH-126 → ph60` — **DIFFERENT MECHANISM.** → `ph97`. Confirms `ADJUDICATION_002` §5.

```c
/* mbstring.c:3211 */  char *typ = NULL;
/* mbstring.c:3215 */  if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "|s", &typ, &typ_len) == FAILURE) {
/* mbstring.c:3216 */      RETURN_FALSE;
/* mbstring.c:3219 */  if (!strcasecmp("all", typ)) {
```
**The failure IS tested, at `:3215`, and the call succeeds.** `|` makes `type`
optional; `mb_get_info()` with zero arguments returns SUCCESS and never writes
`typ`, which keeps the caller's own `= NULL`. (a) unchecked: *"was the optional
argument supplied?"* — a **different proposition** from the one the guard tests
(*"were the supplied arguments well-typed?"*). (b) attacker: **omitting** an
argument. (c) primitive: a NULL handed to **libc** (`strcasecmp`) — the
obligation `I12/O3` names verbatim. Three differ. **Reverses.**

### 2.9 `CRASH-163 → ph60` — **DIFFERENT MECHANISM.** → `ph98`. Confirms `ADJUDICATION_002` §5.

```c
/* zend.c:1074 */  old_exception = EG(exception);
/* zend.c:1075 */  EG(exception) = NULL;
/* zend.c:1078 */  if (call_user_function_ex(CG(function_table), NULL, orig_user_exception_handler, &retval2, 1, params, 1, NULL TSRMLS_CC) == SUCCESS) {
/* zend.c:1079 */      if (retval2 != NULL) { zval_ptr_dtor(&retval2); }
/* zend.c:1082 */  } else {
/* zend.c:1083 */      zend_exception_error(EG(exception) TSRMLS_CC);
```
**The failure is tested, at `:1078`, and the error branch is the one that
faults.** The NULL comes from `:1075`, where **this function itself** moved the
exception out into `old_exception`. (a) unchecked: *"is the global I cleared
still cleared on the path where the callee could not re-establish it?"*.
(b) attacker: a `set_exception_handler` handler that cannot be called.
(c) primitive: the **error reporter's own argument** is the thing the error path
cannot supply. Upstream `79ed194a64a9` adds
`if (!EG(exception)) EG(exception) = old_exception;` — a **restore**, which is
`I16/O4` word for word. Three differ. **Reverses.**

### 2.10–2.13 The four-`LOGIC` set kill

`C.1` disposes of four rows in one sentence: *"all family E — `is_ref` stamped
on, or not separated from, a live shared slot; LOGIC-017 was kept as ph48
because it forces the flag rather than failing to clear it."* Four different
files, four different upstream fixes, and **the surviving row it names is
neither of the two the sentence's own discriminator points at.** The macros:

```c
/* zend.h:554-566 */  #define SEPARATE_ZVAL(ppzv) { … if (orig_ptr->refcount>1) { … (*(ppzv))->is_ref = 0; } }
/* zend.h:568-571 */  #define SEPARATE_ZVAL_IF_NOT_REF(ppzv)     if (!PZVAL_IS_REF(*ppzv)) { SEPARATE_ZVAL(ppzv); }
/* zend.h:573-577 */  #define SEPARATE_ZVAL_TO_MAKE_IS_REF(ppzv) if (!PZVAL_IS_REF(*ppzv)) { SEPARATE_ZVAL(ppzv); (*(ppzv))->is_ref = 1; }
```
⭐ **`SEPARATE_ZVAL` is a no-op at `refcount == 1`.** That single fact decides
three of the four.

**`ph47`** is *the separator runs and does nothing* (`is_ref == 1` short-circuits
`SEPARATE_ZVAL_IF_NOT_REF`), producing an **in-place retype** that invalidates a
cached length → `memcpy` OOB at `string.c:2116-2126`.
**`ph48`** is *separate, then force the flag on*.

| row | the C, from the tarball | verdict |
|---|---|---|
| **LOGIC-003** `zend_object_handlers.c:296-300` + consumer `zend_execute.c:1277-1279` | `rv = zend_std_call_getter(object, member); if (rv) { retval = &rv; }` → `:311 return *retval;` — the `__get` result is returned **unseparated even for `BP_VAR_RW`**, and `:1266 read_property(…, BP_VAR_RW)` → `:1279 incdec_op(z)` mutates it in place → `:1281 write_property(…, z)`. **No separator is called at all.** Sibling `zend_pre_incdec_property` at `:1219` *does* separate. (a) differs (absent vs no-op), (b) differs (a shared `__get` return vs a reference), (c) differs (in-place *mutation* seen by another holder vs in-place *retype* → OOB). | **DIFFERENT** → `ph99` |
| **LOGIC-008** `zend_object_handlers.c:797` + `zend_execute_API.c:430`, `:458` | `:797 zval_update_constant(retval, (void *) 1)` on the static-property slot; inside, the `IS_CONSTANT` and `IS_CONSTANT_ARRAY` arms run an **unconditional** `SEPARATE_ZVAL(pp)`, which separates on `refcount>1` **regardless of `is_ref`** and then sets `is_ref = 0` (`zend.h:564`). The parent↔child static binding written by `inherit_static_prop` is **severed by a plain read**. **A separator that fires where it must not** — the exact opposite of `ph47`, and a third direction the killing sentence has no slot for. | **DIFFERENT** → `ph100` |
| **LOGIC-014** `zend_builtin_functions.c:1420` | `arg = (zval **) p++; SEPARATE_ZVAL_TO_MAKE_IS_REF(arg); (*arg)->refcount++;` over the live `EG(argument_stack)`. Expanded: `if (!is_ref) { if (refcount>1) {clone} ; is_ref = 1; }`. `ph48` is `SEPARATE_ZVAL_IF_NOT_REF(p); … (*p)->is_ref = 1;` — expanded, `if (!is_ref) { if (refcount>1) {clone} } ; is_ref = 1;`. **Identical in the defect case** (`is_ref==0, refcount==1`: no clone, flag stamped on the caller's live by-value slot). (a)(b)(c) all match. | **EXACT vs `ph48`** — kill **stands**, target corrected |
| **LOGIC-018** `zend_compile.c:1899-1900` (primary) | `(*prop)->refcount++; zend_hash_update(ce->static_members, child_info->name, …, (void**)prop, sizeof(zval*), NULL);` — the child's own freshly-compiled default zval is **destroyed by the update's destructor** and the slot is re-pointed at the **parent's** zval. **Two dictionary slots aliased by a hash update that also destroys what it replaces**, with no separation and no `is_ref` on this path. Neither `ph47` nor `ph48`. | **DIFFERENT** → `ph101` |

⚠⚠ **`TASK_PHP_012` M2, attacked rather than applied.** M2's count (3 of 4) is
right and I reached it independently. **Two of its four cells are not.**
1. M2 says LOGIC-014 *"FORCES the flag. This is `ph48`'s mechanism delivered by
   one macro instead of two lines"* — and then files it under *"none of these
   four is exact."* **Its own evidence makes it exact**, against `ph48`.
   §3.1 kills exact duplication with *another `patterns-php/` row*, and `ph48`
   is one. **M2's conclusion is refuted by M2's own sentence.**
2. M2 prices LOGIC-018 at `zend_compile.c:1967-1971` (`inherit_static_prop`).
   `index.csv` — authoritative — names `:1899-1900` **primary** and `:1967-1971`
   the *enabling helper*. **M2 priced the wrong frame**, which is the
   `ADJUDICATION_001` defect, committed inside the finding that reports the
   catalogue's set-kill defect. The verdict survives; the reason does not.

---

## §3 ⭐ What `merged_members` actually means — the question §5.1 most wanted answered

**It does not mean what `C.1` used it to mean, and it is the *weakest* evidence
in that table, not the strongest.**

**Where the field comes from.** `validation/finalize.py` writes
`merged_members` from `validation/data/merge-closure.json`'s `groups`
(19 groups, 22 cases absorbed, canonical = lowest V5C number). Our three:
`V5C-014←015`, `V5C-115←116`, `V5C-145←173`.

**The predicate, in the corpus's own words** (`validation/REPORT.md`):
> §2a — *"The 19 merge groups (**root-cause dedup, decided by reading the C
> defect**, never the fix commit or crash frame)."*
> "Method" — *"**Dedup burden of proof was set on 'distinct', not 'same'**,
> because an unjustified split is what inflates the headline."*

Two things follow, and they point the same way:

1. **The predicate is *root cause*, ours is *exact C mechanism*.** Those are not
   the same relation, and `PLAN_PHP.md` §3.1 is explicit that **a slight
   variation is admitted here**. A corpus merge is therefore evidence of
   *relatedness*, never of *exactness*.
2. ⚠⚠ **The burden is inverted.** The corpus merged unless a verifier could
   prove *distinct*; §3.1 splits unless an adjudicator can prove *exact*. A
   `merged_members` cell is the output of the **opposite decision procedure**.
   Citing it to support a kill is citing a `not-proven-distinct` as a
   `proven-same`.

**And the corpus's own per-case validators had already flagged all three.**
This is the part that makes `"merged by the corpus itself"` untenable:

| merge | what the corpus's own validator wrote, *before* the merge (`verdicts.json`) |
|---|---|
| `V5C-115←116` | *"**distinct missing guards, verified by arithmetic** … two separate defects in the same function, not one; **a dedup pass should keep them separate on that basis**"* — and the merge was nonetheless made, listed under `verifier_initiated` |
| `V5C-014←015` | *"The `currentarg += arg;` overflow at :212 is **genuinely distinct** (different fix commit, 2019) and is unique to this case; **if the two pack cases are merged, keep :212 as the distinguishing member**"* |
| `V5C-145←173` | *"They are **genuinely two distinct source-level mistakes on one line**, but a strict per-line/per-fix dedup would merge them. I have made the fingerprint's `mishandled_object` explicitly the offset zval's TYPE **so the dedup pass can decide**"* |

**Three for three.** Each merge absorbed a defect its own examiner had recorded
as separately real and separately fixed. Under the corpus's headline-count
purpose that is a defensible call; under **our** bar it is the reverse of what
`C.1` claimed. ⭐ **The three kills that looked strongest because they cited an
external authority were the three where the external authority had written down
the counter-evidence.**

⚠ **The `index-other.csv` note is boilerplate, not evidence.** All three rows
carry the identical string *"real defect, but the SAME defective construct as
V5C-0NN (root-cause dedup, adversarially verified)"*, emitted by
`rebuild_corpus.py`. It is a template, and **"real defect"** is the operative
half of it.

---

## §4 Deliverable 3 — the notes rewritten, for the kills that stand

⚠ **I do not edit `CATALOGUE.md`.** This is proposed text. `C.1`'s table after
this task has **four** rows, and every one now states a mechanism reason.

```markdown
### C.1 Kills — exact C-side duplication (criterion: `PLAN_PHP.md` §3.1)

| row | duplicate of | evidence |
|---|---|---|
| CRASH-090 `html.c:155/:401` | **ph32** | **Mechanism, not cost**: same unchecked predicate (no relation between `endchar-basechar+1` and the literal's element count), same attacker quantity (a code point inside the declared range), same primitive (global OOB read of a `char*` at `:900`/`:905`/`:906`, index in `int`). **Only the data literal and the shortfall differ — 63-for-65 vs 66-for-67** — so the extracted kernel differs in no statement, expression, type or guard. ⚠⚠ **The corpus's own round-2 verifier BROKE this merge** with `nm -S` sizes and a control-build runtime witness, on the ground that `:900` is *"the READ SITE, traversed identically by ALL 14 rows of `entity_map[]` — and 11 of them are correct"*. It is a **bar question, not a C question** — see `TASK_PHP_019_REPORT` §7 — and until §3.1 says whether a data object is part of a mechanism, the kill stands with that dissent recorded. ⚠ `ent_uni_spacing` (22 for 23) and `ent_uni_8592_9002` (410 for 411) are two further instances in no corpus row |
| CRASH-037 `zend_exceptions.c:339` | **ph39** | **Mechanism, not cost**: same unchecked predicate (the `type` tag, before a `Z_*VAL_P` macro that consults none), same attacker quantity (the type of a property set from userland via `unserialize`), same primitive (an attacker-chosen `long` dereferenced as a pointer). Only the static type imposed on that pointer differs — `Z_ARRVAL_P` → `HashTable*` at `:339` vs `Z_STRVAL_P` → `char*` at `:551`. Carried inside ph39's `corpus rows`; the type difference is a rider on ph39's block, not a row |
| CRASH-101 `streamsfuncs.c:817` | **ph41** ⚠ **(was ph39 — corrected)** | **Mechanism, not cost**, and the target was wrong. `params` **is** type-checked, by `zend_parse_parameters(…, "ra", …)` at `:917`; the **element** `*tmp` is not, and `:775 Z_ARRVAL_P(options)` reads it as a `HashTable*`. That is **ph41 — *container checked, elements not*** on all three tests, and ⚠ **ph39's heading is *"no tag check OF ANY KIND"*, which this site does not satisfy** — ph41's own `⚠ risk` line says *"the container/element split is the mechanism. Do not fold into ph39."* **Moved to ph41's `corpus rows`.** ⚠ Rider for ph41: here the identical tag test is **present at depth 2** (`:778 Z_TYPE_PP(wval) == IS_ARRAY`) and absent at depth 1 |
| LOGIC-014 `zend_builtin_functions.c:1420` | **ph48** ⚠ **(was ph47 — corrected)** | **Mechanism, not family**, and the target was wrong. `SEPARATE_ZVAL_TO_MAKE_IS_REF(arg)` (`zend.h:573-577`) expands to `if (!is_ref) { if (refcount>1) {clone}; is_ref = 1; }`; ph48's `zend_execute_API.c:608-610` expands to `if (!is_ref) { if (refcount>1) {clone} }; is_ref = 1;`. **In the defect case (`is_ref==0, refcount==1`) `SEPARATE_ZVAL` is a NO-OP and both stamp the flag on the caller's live by-value slot** — identical predicate, identical attacker quantity, identical primitive. ph48 is the row `C.1`'s own sentence said was **kept** for forcing the flag; this is that mechanism at a second site. **Moved to ph48's `corpus rows`.** ⚠ `TASK_PHP_012` M2 reached this C and still filed the row as non-exact; that half of M2 is retracted |

⚠ **`C.1` shrank from 12 merges to 4 at `TASK_PHP_019`, which ran the test
`ADJUDICATION_002` never ran: *does the C support the mechanism claim?*** Nine
rows failed it. `V5C-116`'s kill reverses **without** a new row (ph03 already
carries both defects and measures them apart); the other eight are `ph94`–`ph101`.
Every note above now states a **mechanism** reason, because the old notes stated
a family or a cost reason even where the verdict was right.
```

**And one sentence to add to `ph03`'s Part B block** (after the existing
mechanism prose), because that row's kill note was the false one:

```markdown
⚠⚠ **`V5C-116` is a SECOND defect in this loop, not a duplicate of the first,
and this row already carries both.** `:141`'s bound can be wrong (`ee > e`);
independently, `:143`'s test is at 1-byte granularity while `:144-147`'s body
consumes 4, so the group over-runs even a **correct** bound — V5C-116's trigger
has `ee == e` exactly. Two upstream fixes, `f95c1df58349` (2004) and
`1e2818b14376` (2014); **measured, the 2004 fix leaves 144 of 12 600 documents
still reading past the source** (`spec.md`, `.temp/php13/02-reach.log` Q3), which
is why `R2–R5` carry the 2014 check and `verus.rs` cannot verify without it.
No second row: one extraction, two defects — splitting would double-count a
ladder cost paid once (ph04's rule). `C.1`'s old note said *"same loop, same
bound"*; **the bound is the one thing they do not share.**
```

---

## §5 Deliverable 2 — the eight new rows, in `CATALOGUE.md`'s exact format

⚠ **Format note.** These follow the file's **live** schema (§0.4: a fixed
six-field micro-schema of ~80–110 words), not `TASK_PHP_011` §1's 150-word one,
because that is what the manager has to land beside 93 existing blocks.

⚠ **`inv/obl` is DERIVED here, not carried.** §9.5 says the existing labels are
the corpus's blind labelling; the corpus has none for these, so I read them off
the obligation texts in `php-in-safe-rust/paper/invariants-list.md` and each is
quoted in the block's prose. **Mark them as derived when landing.**

⚠ **`corpus rows` MOVE, they do not duplicate.** Each id below leaves the row it
is currently listed under, so `coverage.py`'s 166/166 is preserved:
`V5C-173` ph11→ph94 · `V5C-015` ph22→ph95 · `CRASH-061`/`126`/`163` ph60→ph96/97/98 ·
`LOGIC-003`/`008`/`018` are currently Part C ids only and become Part A ids.
`CRASH-101` ph39→ph41 and `LOGIC-014` C.1→ph48 (§4).

### Part A — eight rows after `ph93`

```
| ph94 | type | untyped offset: the union's `obj` member read as a byte index | narrowed | I4/O1, I3/O2 | V5C-173 | p35, p48 | catalogued |
| ph95 | spatial | an argument-count guard defeated by the wrap of its own operand | narrowed | I11/O1 | V5C-015 | p05 | catalogued |
| ph96 | type | SUCCESS does not mean the out-parameter was written | narrowed | I12/O1, I16/O2 | CRASH-061 | p42 | catalogued |
| ph97 | type | an optional argument never written; the guard tests a different question | narrowed | I12/O3 | CRASH-126 | — | catalogued |
| ph98 | type | a global cleared by the caller, read back on the error path | narrowed | I16/O4, I12/O2 | CRASH-163 | — | catalogued |
| ph99 | type | a read handler's result mutated in place on the read-WRITE path | narrowed | I9/O2 | LOGIC-003 | p49 | catalogued |
| ph100 | type | the separator fires where it must not, and clears the binding | narrowed | I8/O2, I9/O5 | LOGIC-008 | p49 | catalogued |
| ph101 | type | two dictionary slots aliased by an update that destroys one | narrowed | I9/O1, I8/O1 | LOGIC-018 | p49 | catalogued |
```

⚠ **Counts to fix in Part A's headings and the file header**: Spatial 40 → **41**,
Type/initialisation 22 → **29**, Temporal 31 unchanged; total 93 → **101**.

### Part B — the blocks

**In family `S3` (sizing arithmetic vs an unbounded emit cursor), beside `ph19`–`ph22`:**

```markdown
**ph95 · `pack`: the argument-count guard defeated by its own wrap** — `ext/standard/pack.c:212`, `:214`, `:262` · V5C-015 · `narrowed` · I11/O1 · echoes p05
The *"use as many args as specified"* arm does `:212 currentarg += arg;` and then `:214 if (currentarg > argc) RETURN_FALSE;` — **the guard exists, runs, and is false**, because with `arg = INT_MAX` its own operand has already wrapped `currentarg` to `INT_MIN`. Only then does `:262 outputpos += arg * 2;` wrap to `-2`, leaving `outputsize` at 0 and `:304 emalloc(1)`. ⚠ **`ph22` cannot reach `:212`**: `H` is in the *"always uses one arg"* arm (`:174-191`), which does a bare `currentarg++`. Two upstream fixes: `6d98fc38b53` (2004) repairs `:262`, `db420cb6a14` (2019, bug #78833) adds `if (currentarg > INT_MAX - arg)` before `:212`; neither repairs the other.
▸ trigger: `pack("s2147483647", 1)`.
▸ benign: ordinary count-based formats; `u64` = the packed bytes' checksum.
▸ blob: the format codes + the argument count + the arguments.
⚠ risk: **the row's claim is `:212`, not the sizing** — an extraction that lifts only `:262` has rebuilt ph22. ⚠ Re-adjudicated out of `C.1` at `TASK_PHP_019`; the corpus's own V5C-015 validator asked for exactly this split (*"keep :212 as the distinguishing member"*).
```

**In family `T1` (a union member read without an adequate tag check), beside `ph39`–`ph46`:**

```markdown
**ph94 · the offset's TYPE is never checked, so the index is struct padding** — `Zend/zend_execute.c:4033` with `Zend/zend.h:270-284` · V5C-173 · `narrowed` · I4/O1 + I3/O2 · echoes p35, p48
`:4025-4037` reads `offset->value.lval` as a byte index with **no type test and no `convert_to_long` anywhere in the arm**. For an `IS_OBJECT` offset the union's active member is `value.obj` = `{ zend_object_handle handle; zend_object_handlers *handlers; }` (`zend.h:270-273`), so on LP64 `lval` is **`[4 defined handle bytes | 4 bytes of struct padding `zend_objects_new`'s stack-returned value never writes]`**. ⭐ **The index is uninitialised memory, not a program value** — the only row in the catalogue where that is true. `I4/O1` ("must not read `value.obj` from a zval whose tag does not select that member") composed with `I3/O2` ("must not use a value read from such a slot as … a size, or length").
▸ trigger: `$s = "abcdefgh"; $o = new stdClass; empty($s[$o]);`
▸ benign: `IS_LONG` offsets answer correctly; `u64` = fold of the boolean answers.
▸ blob: a string + a `(tag, payload)` offset stream, one payload deliberately left unwritten.
⚠ risk: **do not fold into ph11** — ph11 is the *range* check on a well-typed signed index (CWE-125); this is the *tag* check (CWE-843), and the corpus's own V5C-173 validator calls them *"genuinely two distinct source-level mistakes on one line"*. ⚠ The uninitialised half needs a producer that really leaves padding unwritten; a memset'd model deletes the mechanism.
```

**In family `T6` (a fallible call whose failure is not tested), beside `ph59`/`ph60`:**

```markdown
**ph96 · SUCCESS does not mean the out-parameter was written** — `Zend/zend_object_handlers.c:509`, `:512-513` with `Zend/zend_execute_API.c:592-595` · CRASH-061 · `narrowed` · I12/O1 + I16/O2 · echoes p42
`zval *retval;` then `:512 zend_call_method_with_1_params(…, &retval, offset); :513 zval_ptr_dtor(&retval);` — **no test of any kind**, and testing the status would not help: `zend_call_function` writes `*fci->retval_ptr_ptr = NULL` at `:595` under its own comment *"we may return SUCCESS, and yet retval may be uninitialized, if there was an exception"*. Two outputs whose relationship is non-trivial, where ph60 has one. `I12/O1` names the case verbatim — *"a NULL return, sentinel, status code, **or NULL-able out-parameter** must be tested"* — and `I16/O2` is *"the outputs of an aborted call must not be … destroyed"*.
▸ trigger: `unset($c[0])` where `C::offsetUnset()` throws.
▸ benign: ordinary `offsetUnset` returns and its result is released once; `u64` = fold of `(status, out!=NULL)` per call.
▸ blob: a call-outcome stream carrying `(status, wrote_out)` **independently**.
⚠ risk: **the two flags must be independent in the blob** — a kernel that derives `wrote_out` from `status` has deleted the mechanism and rebuilt ph60. Re-adjudicated out of `C.1` at `TASK_PHP_019`; ph60's *"failure not tested"* is false here, the call succeeds.

**ph97 · the optional argument the parser never writes** — `ext/mbstring/mbstring.c:3211`, `:3215`, `:3219` · CRASH-126 · `narrowed` · I12/O3 · echoes —
`char *typ = NULL;` at `:3211`; `:3215 zend_parse_parameters(…, "|s", &typ, &typ_len)` — **the `|` makes it optional, so zero arguments returns SUCCESS and `typ` is never written**; `:3219 strcasecmp("all", typ)` hands the caller's own NULL to libc. ⚠ **The failure IS tested and the call does NOT fail.** The guard answers *"were the supplied arguments well-typed?"*; the code reads it as *"was the optional argument supplied?"* — a **different proposition**, whose real test is `ZEND_NUM_ARGS()` or `typ != NULL`. `I12/O3`: *"a possibly-NULL pointer must not be passed to a callee — including libc — that dereferences it without testing it."*
▸ trigger: `mb_get_info()` — zero arguments.
▸ benign: `mb_get_info("internal_encoding")` and friends answer; `u64` = the selected settings' checksum.
▸ blob: an argument-presence bitmap + the argument bytes.
⚠ risk: `zend_parse_parameters` must be **modelled with an optional spec**, not stubbed to always-write — the optionality is the defect. Re-adjudicated out of `C.1` at `TASK_PHP_019` (`ADJUDICATION_002` §5 found it first).

**ph98 · the global the caller cleared, read back on the error path** — `Zend/zend.c:1074-1075`, `:1078`, `:1083` · CRASH-163 · `narrowed` · I16/O4 + I12/O2 · echoes —
`:1074 old_exception = EG(exception); :1075 EG(exception) = NULL;` — **this function moves the exception out itself** — then `:1078 if (call_user_function_ex(…) == SUCCESS) {…} else { :1083 zend_exception_error(EG(exception)); }`. The status test is present and correct; **the fault is on the branch where it says FAILURE**, and the argument the error reporter needs is the thing the error path cannot supply. Upstream `79ed194a64a9` adds `if (!EG(exception)) EG(exception) = old_exception;` — a **restore**, i.e. `I16/O4` word for word: *"an exception moved out of `EG(exception)` into a local must be restored … on every exit path."*
▸ trigger: a `set_exception_handler` handler that cannot be called, with an exception pending.
▸ benign: the handler runs, the global is re-established, the error path is never taken; `u64` = fold of `(handled, reported)`.
▸ blob: a stream of `(raise, handler-callable?)` events.
⚠ risk: **the row is the save/clear/restore triple, not the null-deref** — a kernel that only omits a NULL check has rebuilt ph60. Re-adjudicated out of `C.1` at `TASK_PHP_019` (`ADJUDICATION_002` §5 found it first).
```

**In family `T2` (a type-changing write through a value that was not separated), beside `ph47`/`ph48`:**

```markdown
**ph99 · a read handler's result mutated in place on the read-WRITE path** — `Zend/zend_object_handlers.c:296-300`, `:311` with `Zend/zend_execute.c:1266`, `:1277-1281` · LOGIC-003 · `narrowed` · I9/O2 · echoes p49
`zend_std_read_property`'s `__get` arm does `rv = zend_std_call_getter(…); if (rv) { retval = &rv; }` and `:311 return *retval;` — **the getter's zval is returned unseparated even for `BP_VAR_RW`**. The consumer then does `:1266 read_property(object, property, BP_VAR_RW)`, `:1277 *retval = *z;`, **`:1279 incdec_op(z)` with no separator at all**, `:1281 write_property(…, z)`. ⚠ **Not ph47**: ph47's separator *runs and no-ops* because `is_ref == 1`; here none is called. The sibling `zend_pre_incdec_property` at `:1219` **does** separate. `I9/O2`: *"a value handed out for read-write access must be either exclusively owned by the writer or a reference the program itself wrote."*
▸ trigger: `class O { public $q = 3; function __get($n){ return $this->q; } } $o = new O; $o->virt++;` — `$o->q` becomes 4.
▸ benign: declared properties increment without touching anything else; `u64` = fold of every slot's value after each op.
▸ blob: a slot stream + an op stream, with a `via_handler` bit per op.
⚠ risk: **a boolean `shared` bit is enough** — importing refcounts adds ph69/ph70's mechanism to a row that is not about them (ph47's rule). Re-adjudicated out of `C.1`'s four-`LOGIC` set kill at `TASK_PHP_019`.

**ph100 · the separator fires where it must not, and clears the binding** — `Zend/zend_object_handlers.c:797` with `Zend/zend_execute_API.c:430`, `:458` and `Zend/zend.h:554-566` · LOGIC-008 · `narrowed` · I8/O2 + I9/O5 · echoes p49
`inherit_static_prop` binds a child's static slot to the parent's zval (`refcount++; is_ref = 1;`). Every access then runs `:797 zval_update_constant(retval, 1)`, whose `IS_CONSTANT` (`:430`) and `IS_CONSTANT_ARRAY` (`:458`) arms call **`SEPARATE_ZVAL(pp)` unconditionally** — and `zend.h:558-564` separates on `refcount>1` **regardless of `is_ref`**, then sets `is_ref = 0`. ⭐ **A deliberate reference set is torn apart by a plain READ.** ⚠ **The opposite of ph47** — a separator that acts where it must not, where ph47's no-ops where it must act. `I8/O2`: *"must not clear or lose a binding the program did write."*
▸ trigger: `define('K',5); class A { public static $p = K; } class B extends A {} B::$p = 7;` → `A::$p` is still 5.
▸ benign: a plain-literal static default keeps the binding; `u64` = fold of every slot's `(value, is_ref, refcount)`.
▸ blob: a slot stream with a per-slot `needs_resolution` bit and a bound-pairs list.
⚠ risk: **the constant-resolution step is the trigger, not the mechanism** — model it as one bit, not as a constant table. `crashes_pristine_5_0_0` is `n/a` (non-crash class), like every other refcount-logic row including ph48; criterion 2 is discharged at build. Re-adjudicated out of `C.1`'s four-`LOGIC` set kill at `TASK_PHP_019`.

**ph101 · two dictionary slots aliased by an update that destroys one** — `Zend/zend_compile.c:1899-1900` with `:1967-1971` · LOGIC-018 · `narrowed` · I9/O1 + I8/O1 · echoes p49
When a child redeclares a parent's `protected static` as `public static`, `do_inherit_property_access_check` does `:1899 (*prop)->refcount++;` — `prop` is the **parent's** zval — then `:1900 zend_hash_update(ce->static_members, child_info->name, …, (void**)prop, sizeof(zval*), NULL);`. **The child's own freshly-compiled default zval is destroyed by the table's destructor and the slot is re-pointed at the parent's**, with no separation. The enabling helper `:1967-1971 inherit_static_prop` has already stamped `is_ref = 1` on the general merge path. ⚠ **Neither ph47 (no separator no-ops here) nor ph48 (no `is_ref` on this path)**: the defect is the aliasing update itself.
▸ trigger: `class A { protected static $x = "PARENT"; } class B extends A { public static $x; } B::$x = "W";` → `A::$x` is `"W"`; and `class D extends C { public static $y = "CHILDVAL"; }` prints NULL.
▸ benign: an ordinary override gets its own storage; `u64` = fold of every slot's `(value, identity)` after inheritance.
▸ blob: a class/slot declaration stream + a write stream.
⚠ risk: ⚠ **cite `:1899-1900`, the primary site.** `TASK_PHP_012` M2 priced `:1967-1971` (the helper) and reached the right verdict from the wrong frame. `crashes_pristine_5_0_0` is `n/a` (non-crash class). Re-adjudicated out of `C.1`'s four-`LOGIC` set kill at `TASK_PHP_019`.
```

**And the `C.7` line that keeps the coverage check honest:**

```markdown
⚠ `V5C-015`, `V5C-116` and `V5C-173` appear in Part A but are **not** `input_id`s
— they are the corpus's own `merged_members`, carried across so the merge is
visible. ⚠⚠ **Since `TASK_PHP_019` two of them carry their OWN row** (`V5C-015`
→ ph95, `V5C-173` → ph94), because the corpus's merge predicate is *root cause
with the burden of proof on "distinct"* while `PLAN_PHP.md` §3.1's is *exact
mechanism with the burden on "same"* — the opposite decision procedure. `V5C-116`
stays inside `ph03`, which already carries and separately measures both defects.
```

---

## §6 Deliverable 4 — the `C.4` set kill, enumerated against `index.csv`

**The set as written** (`ADJUDICATION_001` §3b, restated in `C.4`):
*"the 'ordinary null-deref' set (CRASH-061, 082, 088, 126, 163, 021) —
mechanism-quality judgement on the C, which the bar permits."*

**Count: 6 named members.**

**Enumeration against `index.csv`, not against the prose** (F27). The corpus has
**14** rows with `category == null-deref` / `cwe == CWE-476`:

| id | in the set? | individually adjudicated? | where it is now |
|---|---|---|---|
| CRASH-021 datetime.c:1033 | ✅ | ✅ yes — `C.2`, its own row, with a stated pending measurement | `C.2` soft kill |
| CRASH-061 zend_object_handlers.c:513 | ✅ | ❌ **no — killed a second time inside `C.1`'s 3-id sentence** | → **`ph96`** (this task) |
| CRASH-082 array.c:4085 | ✅ | ✅ yes — `C.4` says *"not even in the family"* | `ph59` |
| CRASH-088 ftp_fopen_wrapper.c:649 | ✅ | ✅ yes — became the family row | `ph60` |
| CRASH-126 mbstring.c:3219 | ✅ | ❌ **no — same second sentence** | → **`ph97`** (this task) |
| CRASH-163 zend.c:1083 | ✅ | ❌ **no — same second sentence** | → **`ph98`** (this task) |
| CRASH-023 zend_execute.c:1769 | ✗ | — | `ph55` |
| CRASH-028 zend_compile.c:3274 | ✗ | — | `ph57` |
| CRASH-029 array.c:1046 | ✗ | — | `ph90` |
| CRASH-041 zend_compile.c:763 | ✗ | — | `ph56` |
| CRASH-053 zend_execute.c:1632 | ✗ | — | `ph46` |
| CRASH-071 zend.c:955 | ✗ | — | `ph91` (unresolved) |
| CRASH-096 streamsfuncs.c:1047-1054 | ✗ | — | `ph15` |
| CRASH-143 zend_execute.c:3832 | ✗ | — | `ph54` |

**Answers.**
1. **The set has 6 members, and the enumeration finds no hidden seventh.** ✅
   The other 8 `null-deref` rows were never inside it and are all catalogued.
   **That is a clean negative and it is worth recording as one** — F27's rule
   held here, and produced no recovery.
2. **3 of the 6 were never individually adjudicated** — `CRASH-061`, `-126`,
   `-163` — and they are exactly the three that were **killed twice**. ⭐ **The
   new shape, and it is what F22 did not predict: `C.4` REVERSED the set kill,
   and the reversal put the same three ids straight into a second set kill**
   (`C.1`'s one-sentence, three-id row). A member never acquired a row-level
   entry, so row-level review still could not reach it. **F22's rule needs the
   rider: when you reverse a set-shaped kill, its members must land as
   individual entries — reversing a set into a set is not a reversal.**
3. ⚠ **`C.1` itself contains three more set-shaped kills**, covering 9 ids:
   `CRASH-061/126/163 → ph60` (3), `LOGIC-003/008/014/018 → ph47` (4),
   `CRASH-037/101 → ph39` (2). **8 of those 9 turned out to be mis-stated** — 7
   reversed and 1 merged into the wrong row. `C.1` is `F22`'s densest site in
   the file, and it is the section headed *"exact"*.

---

## §7 ⚠ Deliverable §5.3 — the one row the lens cannot decide crisply, and why

**`CRASH-090 → ph32`.** *"Does the C support the mechanism claim?"* is decidable
for 12 of the 13. On this one it returns **both answers**, and the disagreement
is not about the C — both readings quote the same lines.

The corpus's round-2 pass proposed exactly this merge and **an adversarial
verifier broke it** (`validation/data/dedup2-verify.json`, group `M6-html-tables`,
`merge_holds: false`), with evidence I could not fault:

> *"THE MERGE RESTS ON A SHARED SINK. The pass's 'one single expression' is
> `entity_map[j].table[k - entity_map[j].basechar]` at `html.c:900`. That is the
> **READ SITE**, traversed identically by **ALL 14 rows** of `entity_map[]` — and
> **11 of them are correct**. … Defectiveness is a per-array property."*

plus `nm -S` sizes (`ent_uni_338_402` 0x1f8 = 63 ptrs for 65; `ent_uni_punct`
0x210 = 66 for 67), disjoint code-point blocks, disjoint upstream fixes
(`46bc2c5ae2ae` 2004 touches only `ent_uni_punct`; `bd2e99ee50ed` 2005 only
`ent_uni_338_402`), and a control-build runtime witness for each.

**Both sides are right about different things**, and the bar does not say which
one it means:

| reading of "its C mechanism" | verdict |
|---|---|
| **the operation** — the unchecked predicate, the attacker quantity, the primitive | **EXACT** → kill stands (what I applied, §1) |
| **the operation *and the object it operates on*** — the corpus's, and the one the corpus applies consistently to eight integer-overflow sites and five missing-tag sites | **DIFFERENT** → two rows |

⚠ **This is not a gap I can close from inside the task.** `PLAN_PHP.md` §3.1 and
`CLAUDE.md` rule 6 both say *"its C mechanism"* and neither says whether a data
object is part of one. The choice is consequential well beyond this row: under
the object reading, `ph32` is 4 rows (the catalogue's own `⚠ risk` line already
records that **four** `entity_map` literals are short, not two) and `ph39`/`ph41`
multiply the same way. **I applied the operation reading because it is the one
the catalogue already uses everywhere else** — `ph60` is four sites in one row,
`ph61` is five, `ph43` is two limbs — and consistency inside our own file beats
consistency with the corpus's different purpose. **But the manager should settle
it in §3.1, and until then `C.1`'s CRASH-090 note should carry the dissent.**
It is recorded in the proposed note (§4).

**Everywhere else the lens was decidable**, and it was decidable for a reason
worth keeping: **each of the twelve had a separate upstream `fix_commit`, and
asking *"does this fix repair that defect?"* is a question the tarball and
`git log` answer without judgement.** That test decided 9 of the 12 on its own.

---

## §8 ⭐ Deliverable 5 — the base rate

**This task: 9 of 13 fail the mechanism test (69 %).** ⚠ **Stated strictly, only
2 of 13 (15 %) are correct as written**: the other two that stand
(`CRASH-101`, `LOGIC-014`) name the wrong surviving row, and one of them is
folded into a row whose own text forbids the fold.

⚠ **I did not go looking.** The verdicts were reached by opening every row's C
before reading `TASK_PHP_012` M2 or re-reading `ADJUDICATION_002` §5, the rule in
§1 was fixed before the rows were graded and applied unchanged, and **the two
"stands" verdicts came out of the same procedure** — including `CRASH-090`,
where I had the corpus's own reversal in hand and still upheld the kill. Two of
my nine (`CRASH-126`, `-163`) are confirmations of a prior finding, not
discoveries; a third (`CRASH-061`) was already flagged as a candidate by
`ADJUDICATION_002` §5. **Four of the nine are new** (`V5C-116`, `V5C-173`,
`V5C-015`, and `LOGIC-018`'s frame), and three are the LOGIC set.

### The historical rate, as far as it can be counted

| pass | opened | reversed | rate |
|---|--:|--:|--:|
| `ADJUDICATION_001` §1 — the mining wave's kill list | ~28 | **17** | ~61 % |
| `TASK_PHP_011` — `ADJUDICATION_001`'s own **upheld** list (`C.4`) | 5 + a 6-member set + 3 hidden in the mbstring sentence | **9 + 5 of the 6** | ~90 % |
| `ADJUDICATION_002` §2 — rider m8 | 2 | **2** | 100 % |
| `TASK_PHP_017` §5 — a side review of `C.1` | 12 | **2** | 17 % |
| **`TASK_PHP_019` — `C.1`, deliberately, all 13** | **13** | **9** | **69 %** |

**The answer to *"what fraction of a kill list has this corpus's kill lists got
wrong?"*: of the **46** distinct ids ever written down as killed in this
programme, **6 survive** — `CRASH-017` (C.3), `CRASH-021` (C.2, soft) and four
merges (`CRASH-090`, `-037`, `-101`, `LOGIC-014`). **That is 40 / 46 ≈ 87 %
reversed, and every single deliberate re-examination has reversed a majority of
what it opened.**

*The 46, enumerated so it can be checked rather than trusted:* `C.5`'s 19
(CRASH-123, 136, 134, 157, 130, 107, 014, 120, 018, 019, 055, 056, LOGIC-017,
028, 033, 053, 005, 009, 008) + `C.4`'s first table 5 (135, 133, 097, 098, 147)
+ `C.4`'s mbstring sentence 3 (124, 127, 128) + `C.4`'s null-deref set 6 (061,
082, 088, 126, 163, 021) + `C.1`'s 12 further ids (106, 109, 090, V5C-116,
V5C-173, V5C-015, 037, 101, LOGIC-003, -008, -014, -018; 061/126/163 are already
counted in the set) + `C.3`'s 1 (017). `C.6`'s five *"fell between axes"* rows
are **excluded** — they were dropped, not killed.

⚠ **The one pass with a low rate is the informative one.** `TASK_PHP_017` got
17 % — and it was testing for a **cost word**, which is the wrong test for this
population (`ADJUDICATION_002`'s predicted re-read finds nothing because zero of
the remaining `C.1` notes contains one). **The rate tracks the TEST, not the
rows.** The mechanism test on the same 12 returns 8. **So the base rate is not a
property of the kill lists; it is a property of whether anyone opened the C.**

### Do `C.2` and `C.3` deserve the same pass?

**`C.2` — yes, and it is cheap.** One row, `CRASH-021`, and its own note already
names the missing step: *"the fault is inside glibc's `strftime`, and I did
**not** run it on this box's glibc … If someone runs it and it faults, it is
admissible and the kernel is ten lines."* **This is not an adjudication, it is a
20-minute measurement**, and the note has been standing since `TASK_PHP_011`.
⚠ And note the asymmetry the mechanism test exposes: modern glibc being clean
would make it a criterion-2 kill *on this box's libc*, which is a property of the
harness, not of the C — the same shape as `CRASH-098`'s *"requires
`RLIMIT_NOFILE`"*, already reversed. **Whoever runs it should say what a clean
run licenses, before running it.**

**`C.3` — no, and the reason is already written down.** One row, `CRASH-017`, and
`TASK_PHP_012` m3 has already run the mechanism test on it and found that
**it does not fail criterion 3 at all** — it is retired by `PLAN_PHP.md` §4.3's
standing decision, which is binding and correct. The honest statement is *zero
criterion-3 kills; one kill on a design decision*. That finding is owed a
landing, not a re-run.

**What does deserve a pass, and nobody has asked for it:** the mechanism test has
now been run on `C.1` (13 rows), `C.4` (the 6-member set), `C.2` and `C.3`.
⚠ **It has never been run on the 93 catalogued rows' `corpus rows` cells** — and
this task found **two** mis-merges there (`CRASH-101` in `ph39`, `LOGIC-014`
implicitly), plus `ph32`'s open question. `coverage.py` proves every id is
*somewhere*; **nothing checks that it is in the right somewhere**, and a wrong
`corpus rows` cell is invisible to the coverage check by construction.

---

## §9 What this report does NOT establish

1. **Criterion 2 is not demonstrated for any of the eight new rows** — no
   detector was run and no positive control was built. Neither was it for the 93
   already catalogued; it is discharged at build (`ADJUDICATION_002` §2's rule,
   applied unchanged).
2. **The `inv/obl` labels are mine, derived from `paper/invariants-list.md`**,
   not the corpus's blind labelling. Every one is justified in its block's prose;
   mark them as derived when landing.
3. **`echoes` is a reading.** No `pNN` was opened. `p48` on `ph94` and `p05` on
   `ph95` are the two I am least sure of.
4. **Tiers are estimates read off the source**, and every one of the eight is
   `narrowed` — which is a suspiciously uniform answer and probably means I did
   not think hard about any of them. Treat them as placeholders.
5. **I did not re-check the 91 pre-existing kills that are already reversed.**
   The population was `C.1` plus `C.4`'s set, as tasked.
6. **`ph03`'s spec.md figures (144 / 12 600) are quoted, not re-measured.**

⚠ **§1, §4 and §8 are superseded for `CRASH-090` by §10**, which ran the second
disjunct properly and reverses that row. The counts in §8 are restated at §10.6.

---

# §10 — the `html.c` split, settled

**Added after the manager's reply.** Task: settle `ent_uni_*` on the C, four
tables not two. ✅ **Every claim below is measured, by three independent methods,
and the upstream chain is tag-confirmed.** Tools (all in `.temp/php19/`,
all re-runnable): `entcount.py` · `entruns.py` · `entdrift.py` · `extract.sh`.

## §10.0 ⭐ THE ANSWER

**TWO rows, not four and not one.** Under my own §1 rule, applied to the fix
commits I bisected rather than to the ones the corpus cites:

| row | tables | the commit that removes the **5.0.0** shortfall |
|---|---|---|
| **`ph32`** (keeps `CRASH-089`) | `ent_uni_338_402` **+ `ent_uni_spacing` + `ent_uni_8592_9002`** | **one** commit — `56adfe1f3cf1` (PHP-5.0) / `16d67ab9f55a` (HEAD), 2005-03-09, Derick Rethans, **bug #28067** |
| **`ph102`** (takes `CRASH-090`) | `ent_uni_punct` | `35e43dabe16b` (PHP-5.0) / `46bc2c5ae2ae` (HEAD), 2004-07-19, Moriyoshi Koizumi, **bug #29199** |

**Neither commit touches the other's tables.** ✅ **So `CRASH-090 → ph32`
REVERSES — the manager's verdict, reached through the manager's own stricter
test, and it survives that test.** ⚠ The three that share a fix **merge under my
rule's second disjunct failing to fire**, so I am not delivering four rows.

## §10.1 ⚠ The counting script, attacked first

I did not build on `count_ent.py`. I re-derived every number **with the C
compiler** (`entcount.py`: emits the tables + `entity_map[]` into a program that
prints `sizeof(T)/sizeof(T[0])` per row, enumerates the map by walking to
`cs_terminator`, and joins table↔row by **pointer identity**). Independent of the
regex on comment handling, on literal radix, on enumeration and on the join.

✅ **Result: the manager's four figures are exactly right**, and so are the other
two numbers under a scope the prose does not state:

```
5  ent_uni_338_402    declares=65   has=63   SHORT      (all 24 map rows checked)
6  ent_uni_spacing    declares=23   has=22   SHORT
8  ent_uni_punct      declares=67   has=66   SHORT
11 ent_uni_8592_9002  declares=411  has=410  SHORT
   the other 20 rows: ok.   map rows: 24 ; named tables in file: 17
```
That is **three independent agreements** on 63-for-65 and 66-for-67: the
manager's regex, my compiler, and the corpus's `nm -S` on an ASan binary.

**Two defects in the script, one of which matters:**

1. ⚠⚠ **`declared()`'s `(\d+)` cannot read a hex bound, and the failure is
   SILENT.** `entity_map[]` declares **8 of its 24 rows** in hex
   (`{ cs_cp1252, 0x80, 0x9f, … }`, `0xa0..0xff`, `0xa3`, `0x0b`). For those,
   `declared()` returns `None`, and the script's own ternary prints **`ok`** —
   `('SHORT by %d' % …) if want and have < want else 'ok'`. **A table it could
   not evaluate is reported as correct.** ✅ I measured all 8 with the compiler
   and every one is genuinely exact, so no finding was lost — **but the script
   would have said `ok` either way**, which is the *"reports absence as
   not-present"* class the F35 note is about, one level up.
2. **`strip_comments`, the thing the docstring worries about, is fine.**
   `re.sub(r'/\*.*?\*/', '', s, flags=re.S)` is non-greedy across the whole file,
   so an **unterminated** `/*` swallows to the next `*/` anywhere later —
   **exactly what a C compiler does.** I checked it against GCC on the one input
   where it matters (`html-5.0.4.c`, §10.4) and they agree: 41. Its real gaps are
   `//` comments and `*/` inside a string literal; html.c has neither.

**The "6 exact / 7 not in the map" figures are right, under an unstated scope.**
Scoped to `cs_utf_8` rows: 10 rows, 4 short, **6 exact**, and **7** of the 17
tables are not in a `cs_utf_8` row. ⚠ Under the plain reading of the words —
*"not in `entity_map` at all"* — it is false: **all 17 `entity_table_t` tables
are in `entity_map[]`**, and 13 of the 17 are exact.

## §10.2 The kind of each shortfall — ✅ the manager's guess is confirmed, three kinds

Two more methods, both C-side and both needing no execution.
**`entruns.py`** walks each table's `/* codepoint */` markers and compares the
running index with what the marker claims. **`entdrift.py`** uses the table's own
named entries as the oracle — an HTML4 entity name has a fixed code point, so
`basechar + index` must equal it — with Python's stdlib `html.entities.html5` as
the reference. `ent_uni_greek` (70 for 70) is the negative control and passes.

| table | short | **kind** | localisation |
|---|--:|---|---|
| `ent_uni_338_402` | **2** | **two miscounted NULL runs** under explicit range comments | `/* 354 - 375 */` at `html.c:115-117` writes **21** for 22; `/* 377 - 401 */` at `:121-123` writes **24** for 25. Drift: `Yuml` → U+0177 (true U+0178, −1); `fnof` → U+0190 (true U+0192, −2) |
| `ent_uni_spacing` | **1** | **same kind** — one miscounted NULL run | `/* 711 - 731 */` at `:132-133` writes **20** for 21. Drift: `tilde` → U+02DB (true U+02DC, −1) |
| `ent_uni_punct` | **1** | ⚠ **DIFFERENT KIND — an omitted element in a flat, UNLABELLED dense list.** The table carries **one** marker (`/* 8194 */`) and no runs at all, so **nothing in the source states any entry's intended code point** | the run walk **cannot see it**. Content drift can: correct through `bdquo` (index 28 = U+201E), then **−1 from `dagger` onward** — a single missing `NULL` placeholder for U+201F immediately before `"dagger"` at `:161` |
| `ent_uni_8592_9002` | **1 net** | ⚠ **A THIRD KIND — compensating errors.** 25 run markers, several internally inconsistent (`/* 8870 - 8901 */` followed by its own `/* 8901 */`; `/* 8969 - 9000 */` where the running index is already 8972). At least one short run and at least one long one, so the drift moves in **both** directions and nets to −1 | first wrong entry `crarr`, index 36 → U+21B4 (true U+21B5): the `/* 8624 (0x21b0) */` run is one short. ⚠ **Not localisable to a single omission by content** — the table also carries independent *naming* errors (`rarrw`, `bepsi`, `ni`) my oracle cannot separate from index drift, and `lang`/`rang` are an oracle artefact (HTML5 remapped them U+2329→U+27E8) |

⭐ **And the kind explains the history.** `56adfe1f3cf1` adds
`http://www.w3.org/TR/2002/REC-xhtml1-20020801/dtds.html#h-A2` **to the file
header** — it re-derived the tables from the XHTML DTD — and in one pass caught
the two labelled-run miscounts, the compensating drift, *and* two pure name
typos in the correct-length `ent_uni_greek` (`ups1h`→`upsih`, `p1v`→`piv`;
1-for-i, not a shortfall, not a memory defect). **`ent_uni_punct`, the one table
with no run comments, is the one that had to be found by a user bug report nine
months earlier — and its fix commit ADDS the `/* 8216 */` and `/* 8242 */`
markers that were missing.** The absent scaffolding is why it was found last by
audit and first by a user.

## §10.3 ✅ Every localisation above was predicted before the patch was read

`entdrift.py` said *"the omission is BEFORE line 161 (`dagger`)"*. `46bc2c5ae2ae`:

```diff
-	"lsquo", "rsquo", "sbquo", NULL, "ldquo", "rdquo", "bdquo",
+	/* 8216 */
+	"lsquo", "rsquo", "sbquo", NULL, "ldquo", "rdquo", "bdquo", NULL,
 	"dagger", "Dagger",	"bull", NULL, NULL, NULL, "hellip",
```
`entdrift.py` said `crarr` at index 36 is one early. `56adfe1f3cf1`:
```diff
-	NULL, NULL, NULL, NULL, "crarr", NULL, NULL, NULL,
+	NULL, NULL, NULL, NULL, NULL, "crarr", NULL, NULL,
```
`entruns.py` said `/* 711 - 731 */` writes 20 for 21. `56adfe1f3cf1`:
```diff
-	/* 711 - 731 */   ...20 NULLs...   /* 732 */   "tilde",
+	/* 711 - 730 */   ...20 NULLs...   /* 731 - 732 */   NULL, "tilde"
```
And the corpus verifier's eight control-binary values for `ent_uni_punct`
(dagger→U+201F … frasl→U+2043) are reproduced **exactly**, from the source text,
with no binary and no execution.

## §10.4 ⚠⚠ The manager's caution (point 2) is CORRECT — and the chain is worse than that

**`bd2e99ee50ed`'s pre-image is not 5.0.0's text**, and it is not the fix for the
5.0.0 shortfall. **Bisected across the tags** (`entcount.py` on each; 5.0.1–5.0.4
fetched from `raw.githubusercontent.com/php/php-src/php-5.0.N`):

```
tag      338_402   spacing   punct   8592_9002
5.0.0    63/65     22/23     66/67   410/411
5.0.1    63/65     22/23     ok      410/411     <- punct fixed alone
5.0.2    63/65     22/23     ok      410/411
5.0.3    63/65     22/23     ok      410/411
5.0.4    41/65 (!) ok        ok      ok          <- spacing + 8592_9002 fixed; 338_402 GOT WORSE
5.0.5    ok        ok        ok      ok
```

**The four-commit chain, every sha tag-confirmed and every window closed by a
GitHub API listing of `ext/standard/html.c` on branch `PHP-5.0`:**

| # | PHP-5.0 sha | HEAD sha | date | what it does |
|---|---|---|---|---|
| 1 | `35e43dabe16b` | `46bc2c5ae2ae` | 2004-07-19 | bug #29199. **Fixes `ent_uni_punct` alone** — inserts the U+201F `NULL`, adds two run markers, ships `bug29199.phpt`. Touches no other table |
| 2 | `56adfe1f3cf1` | `16d67ab9f55a` | 2005-03-09 | bug #28067. **The DTD audit.** Fixes `spacing` and `8592_9002`; **rewrites `338_402` to the correct 65-element layout — and leaves `/* 376 (0x0178)` UNTERMINATED in the same hunk**, so the array compiles to **41** |
| 3 | `bd07142b9128` | `37967386818e` | 2005-03-10 | *"fix `/*`-within-comment warning"*. ⚠⚠ **It closes the comment at the WRONG line** — appends `*/` **after** the swallowed block — so the GCC warning goes away and **the 24 initialisers stay inside the comment.** 5.0.4 ships at 41 **with no diagnostic at all** (✅ measured: `gcc -Wall` on 5.0.4's tables is silent) |
| 4 | `85afcb802dc1` | `bd2e99ee50ed` | 2005-05-11 | bug #29119, *"merge error from 4.3"*. Moves the `*/` onto the `/* 376 */` line, un-swallowing all 24 → **65** |

⚠ **Two riders the corpus's citations need.** (a) **The corpus cites HEAD shas;
the branch the tags are cut from is `PHP-5.0`, and every fix here is an MFH pair
with a different sha.** Both resolve to the same change, but *"is it an ancestor
of tag php-5.0.0"* must be asked of the right one. (b) `bd2e99ee50ed` is
**a** fix for `ent_uni_338_402` and **not the** fix for its 5.0.0 shortfall —
it repairs damage that commit #2 introduced. **The manager's F38-half-2 caution
was right and I am not keeping the argument on that commit.**

⭐ **And #3 is the sharpest thing in this section.** *A defect was made invisible
by the commit that fixed its warning.* From 2005-03-10 the source **looks**
correct — the layout is the audited one, the comment is closed, GCC is silent —
and the array is still 24 short. **`ph32`'s R1h must be `56adfe1f3cf1` +
`85afcb802dc1`, and a build that stops at the first will pass every syntactic
check and still be wrong.** That is a `ph03`-shaped finding (*"of a two-hunk fix
one hunk is dead and the other is incomplete"*) at a second site, and it is the
best argument in this report for `PLAN_PHP.md` §4.4's *"R1h is the real upstream
fix"* being a **measurement**, not a lookup.

## §10.5 Applying the §1 rule, all four

**Second disjunct** — *different upstream fixes, each of which leaves the other
standing*, under the manager's stricter reading (*the fix that removes the
**5.0.0** shortfall*):

- **`ent_uni_punct` vs the other three: FIRES.** `35e43dabe16b` touches only
  `ent_uni_punct` — measured: 338_402, spacing and 8592_9002 are **still short at
  5.0.1, 5.0.2 and 5.0.3**. And `56adfe1f3cf1` does not touch `ent_uni_punct` at
  all (its hunks run `ent_uni_338_402` → `ent_uni_spacing` → `ent_uni_greek` →
  `ent_uni_8592_9002`, with `ent_uni_punct` appearing only as context). ⚠ **One
  direction is counterfactual** — punct was already fixed by 2005 — so the honest
  form is *"#2 would not have repaired punct had it still been short"*, which the
  patch settles by inspection. → **DIFFERENT MECHANISM.**
- **`ent_uni_338_402` vs `ent_uni_spacing` vs `ent_uni_8592_9002`: DOES NOT
  FIRE.** One commit, `56adfe1f3cf1`, repairs all three in one hunk-set. There
  is no "different upstream fix" to test.

**First disjunct**, for the three that share a fix: (a) unchecked predicate — no
relation between `endchar-basechar+1` and the literal's element count: identical.
(b) attacker quantity — a code point inside the declared range: identical.
(c) fault primitive — global-buffer-overflow read of a `char *` at `:900`/`:905`/
`:906`, index in `int`: identical. **All three match → EXACT → they merge.**
⚠ **The three *kinds* differ (miscounted run ×2, compensating drift), and that
does not move the verdict**: the kind is how the transcription error was made,
not what the C does at run time, and the extracted kernel is the same loop over a
differently-short literal.

⚠ **This is where the §7 bar question would have bitten, and it no longer does.**
Under the *object* reading `ent_uni_338_402`, `spacing` and `8592_9002` are three
rows; under the *operation* reading they are one. **The fix-commit disjunct
decides `CRASH-090` without needing an answer**, so §7's question is now a
question about the three **uncatalogued** tables only, and none of them is a
corpus row. **It still deserves settling in §3.1, but nothing is blocked on it.**

## §10.6 Deliverables — the new row, the `ph32` rewrite, and the restated counts

⚠ **Proposed text only. `CATALOGUE.md` is not edited** (`TASK_PHP_020` is drawing
from Part A). New id continues from `ph101` → **`ph102`**.

**Part A — one more row, and one existing row's `corpus rows` cell changes:**

```
| ph102 | spatial | one omitted element in the only entity table with no run comments | verbatim | I1/O2 | CRASH-090 | p27 | catalogued |
```
```diff
-| ph32 | spatial | a range declared in one place, a table literal sized in another | verbatim | I1/O2 | CRASH-089, CRASH-090 | p27 | catalogued |
+| ph32 | spatial | a range declared in one place, a table literal sized in another | verbatim | I1/O2 | CRASH-089 | p27 | catalogued |
```

**Part B — `ph32`, rewritten** (it is now the *three-table, one-fix* row):

```markdown
**ph32 · `entity_map`: a range declared here, a table sized there** — `ext/standard/html.c:398`, `:401`, `:896`, `:900` · CRASH-089 · `verbatim` · I1/O2 · echoes p27
Each `entity_map` row pairs a `char **` table with a `basechar`/`endchar` range declared **in a completely different place** from the table literal. `:896`'s loop walks `k` from `basechar` to `endchar` **inclusive** and indexes `table[k - basechar]` at `:900`, `:905` **and `:906`**, with no compiler or runtime relation between the count and the extent (`int j, k;` at `:877`).
▸ trigger: any input reaching the top of a short table's range.
▸ benign: ordinary entity decoding; `u64` = fold of the decoded entities.
▸ blob: the text + a charset selector.
⚠⚠ risk: **the corpus records ONE short table for this row; there are THREE with the same fix.** ✅ Measured with the C compiler (`.temp/php19/entcount.py`, `sizeof/sizeof[0]` over all 24 map rows): `ent_uni_338_402` **63 for 65**, `ent_uni_spacing` **22 for 23**, `ent_uni_8592_9002` **410 for 411**. All three are repaired by ONE commit — `56adfe1f3cf1` (PHP-5.0) / `16d67ab9f55a` (HEAD), 2005-03-09, bug #28067 — which is why they are one row. **A build fixing only CRASH-089 is still defective on two tables.** ⚠ The *kinds* differ and the mechanism does not: two miscounted NULL runs (`:115-117`, `:121-123`), one miscounted run (`:132-133`), and a compensating drift that nets to −1 (`crarr`, index 36).
⚠⚠ **R1h IS TWO COMMITS AND THE FIRST ONE IS INVISIBLY INCOMPLETE.** `56adfe1f3cf1` rewrites `ent_uni_338_402` to the correct 65-element layout **and leaves `/* 376 (0x0178)` unterminated in the same hunk**, so it compiles to **41**. `bd07142b9128` (2005-03-10) then *"fixes the `/*`-within-comment warning"* by closing the comment **after** the swallowed block — **silencing GCC while keeping the defect**, which is how php-5.0.4 shipped at 41 with no diagnostic. Only `85afcb802dc1` / `bd2e99ee50ed` (2005-05-11, bug #29119) un-swallows the 24. **R1h = `56adfe1f3cf1` + `85afcb802dc1`; stopping at the first passes every syntactic check and is wrong** (`ph03`'s two-hunk finding, second instance).
⚠ Cross-reference **ph53**: same C shape, storage sized from the other number, different vulnerability class. And **ph102**, the fourth short table, which is a separate row because it has a separate fix.
```

**Part B — the new row, beside `ph32` in family `S4`:**

```markdown
**ph102 · `ent_uni_punct`: the table with no run comments, and the element nobody counted** — `ext/standard/html.c:155`, `:401`, `:900` · CRASH-090 · `verbatim` · I1/O2 · echoes p27
`:401 { cs_utf_8, 8194, 8260, ent_uni_punct }` declares **67** slots; the literal at `:155-166` has **66**. Same read site as ph32, **different defect and different fix.** ⭐ **It is the only `cs_utf_8` table written as a flat dense list with no `/* codepoint */` run markers**, so nothing in the source states any entry's intended value — and the defect is a single omitted `NULL` placeholder for U+201F, immediately before `"dagger"` at `:161`. ✅ Localised from the source text alone (`.temp/php19/entdrift.py`, HTML4 entity names as the oracle): correct through `bdquo` (index 28 → U+201E), then uniformly **−1** — `dagger`→U+201F, `Dagger`→U+2020, `bull`→U+2021, `hellip`→U+2025, `permil`→U+202F, `prime`→U+2031, `oline`→U+203D, `frasl`→U+2043. Reproduces the corpus verifier's eight control-binary values exactly, with no binary.
▸ trigger: `html_entity_decode('&frasl;', ENT_QUOTES, 'UTF-8')` — anything reaching the top of 8194..8260.
▸ benign: punctuation entities decode; `u64` = fold of the decoded code points.
▸ blob: the text + a charset selector.
⚠ risk: **R1h is `35e43dabe16b` (PHP-5.0) / `46bc2c5ae2ae` (HEAD), 2004-07-19, bug #29199** — it inserts the missing `NULL` **and adds the `/* 8216 */` and `/* 8242 */` markers that were absent**, which is the row's whole point: the scaffolding that would have made the miscount visible was not there. ⚠ **Do not merge into ph32**: ph32's three tables are repaired by `56adfe1f3cf1` (2005-03-09), which does not touch this one, and this fix left all three of ph32's standing — **measured: they are still short at php-5.0.1, 5.0.2 and 5.0.3.** Two fixes, neither repairing the other → `PLAN_PHP.md` §3.1. ⚠ Before the OOB read at `k = 8260`, the whole tail from U+2020 up **decodes to the wrong code point** — a silent correctness defect the corpus's `global-buffer-overflow` label does not name.
```

**Counts restated** (these replace §1, §5 and §8 where they differ):

| | before | after |
|---|--:|--:|
| kills failing the mechanism test | 9 / 13 | **10 / 13** |
| correct **exactly as written** | 2 | **1** (`CRASH-037 → ph39`) |
| correct verdict, wrong merge target | 2 | 2 (`CRASH-101`→ph41, `LOGIC-014`→ph48) |
| new rows | ph94–ph101 (8) | **ph94–ph102 (9)** |
| catalogue rows | 93 | **102** — spatial 40 → **42**, type 22 → **29**, temporal 31 |
| survivors of every kill list ever written (of 46) | 6 | **5** → 41 / 46 ≈ **89 % reversed** |

`C.1`'s table drops to **three** rows: `CRASH-037 → ph39`, `CRASH-101 → ph41`,
`LOGIC-014 → ph48`. **The `CRASH-090` row is deleted from `C.1`** and replaced by
one line recording the re-adjudication, per `TASK_PHP_012` M1's *"do not silently
drop a kill"*:

```markdown
⚠ **`CRASH-090` was re-adjudicated at `TASK_PHP_019` §10 and ADMITTED as `ph102`.**
The kill said *"literally the same defect on a different table"*. The operation is
the same; **the fix is not.** `ent_uni_punct` is repaired by `35e43dabe16b` /
`46bc2c5ae2ae` (2004-07-19, bug #29199), which leaves ph32's three tables short
through php-5.0.3 — measured, tag by tag — and ph32's own fix `56adfe1f3cf1`
(2005-03-09, bug #28067) does not touch `ent_uni_punct`. Two upstream fixes,
neither repairing the other.
```

## §10.7 What §10 does NOT establish

1. **`ent_uni_spacing` and `ent_uni_8592_9002` are in NO corpus row.** They enter
   the catalogue only as `ph32`'s risk text. Their shortfalls are measured; their
   *exploitability* is inherited from `ph32`'s argument, not demonstrated.
2. **`ent_uni_8592_9002`'s single missing element is bounded, not pinpointed.**
   The table carries independent naming errors in both directions; I localised
   the first short run (`crarr`) and the fix commit confirms it, but I cannot
   rule out that the net −1 is the sum of more than two errors.
3. **`entdrift.py`'s oracle is HTML5, not HTML4.** `lang`/`rang` were remapped
   (U+2329→U+27E8), which shows up as a spurious −1216 and is flagged in-line;
   `nles`, `nges`, `cupre`, `sscue`, `epsis` have no single-char HTML5 entry and
   are skipped. **Neither affects the three tables the method decided.**
4. **The `crashes_pristine_5_0_0` flag is `False` for both `CRASH-089` and
   `CRASH-090`**, and the corpus records `CRASH-090`'s ASan log as a duplicate of
   `CRASH-089`'s. Criterion 2 is discharged at build for both, as for every other
   catalogued row — it is **not** a distinctness argument and was not used as one.
5. **No PHP was built or run.** Every figure is from the compiler over the table
   definitions, from the source text, or from a fetched upstream patch.
