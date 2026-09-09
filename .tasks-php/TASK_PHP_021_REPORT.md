# TASK_PHP_021 — REPORT · trigger-test the nine new rows, and land `_019` + `_020`

**Role:** research engineer, alone. **Scope obeyed:** the only file written
outside this report and `.temp/php21/` is the new `.tasks-php/land_019_020.py`.
**`patterns-php/CATALOGUE.md` was NOT written** (`git status` at the end: one
untracked script, nothing else). No `.memory-php/`, no `RECAP_PHP.md`, no
`harness/`, `common/`, `patterns/`, `results/`, `pilot/`, no `.web/`,
no `patterns-php/ph07-strcut-cursor/`. No `git add`, no `git commit`. `grep -a`
/ `/usr/bin/grep` throughout.

---

## §0 THE ANSWER, IN SIX LINES

1. ⚠⚠⚠ **THE STOP CONDITION FIRED. THE LANDING WAS NOT APPLIED.**
   **3 of the 9 new rows needed a `▸ trigger` correction** — `ph94`, `ph98`,
   `ph101` — and task §4.1 says *"if §2's trigger test fails on more than two of
   the nine, STOP the landing and report; that is the signal the batch needs a
   review cycle, not a landing."*
2. **The landing is nonetheless BUILT and `--check`-clean**:
   `.tasks-php/land_019_020.py`, 45 anchors, every one resolving **exactly
   once**, 93 → **102** rows, Part A and Part B both 102 with no mismatch,
   verified by applying to a scratch copy. **One command once the batch is
   reviewed.** The three corrected triggers are already folded into its text.
3. ⭐ **The most consequential finding is a MEASUREMENT, and it narrows a row.**
   `ph94`'s trigger reaches `zend_execute.c:4033` and **produces no
   out-of-bounds read on this box at `-O0`, `-O1`, `-O2` or `-O3`**: gcc 13.3.0
   returns the 16-byte `zend_object_value` in `RAX:RDX` and narrows through
   `mov %esi,%eax`, **zeroing the very padding the row is about**, so the index
   is the object handle and the read lands inside the string.
4. ⚠ **The answer to §2's starred question is the opposite of the hopeful one.**
   A clean nine-for-nine would have said the adjudicator's triggers beat the
   catalogue's. **They did not**: 3/9 here against `TASK_PHP_020`'s 3/19 — and
   §2.10 explains why the two rates are *not* cleanly comparable and why the
   gap is probably still real.
5. ✅ **§4.3 answered: the two blank `tier` cells are DELIBERATE.** They are
   `ph15` and `ph91`, the two `unresolved` rows. **Do not fill them** — §5.2.
6. ⭐ **`coverage.py` cannot count a three-digit row id and cannot report that
   it cannot** — measured, §6.1. Its `166/166` is unaffected; its row-count
   line would print `99 … gaps: none` on the 102-row file.

**Bracket, first and last, recorded rather than expected:**

| | open | close |
|---|---|---|
| `harness/measure.py --check-stale` | **66 / 0 STALE** | **66 / 0 STALE** |
| `harness-php/gate.py --tool measure --check-stale` | **6 / 0 STALE** | **6 / 0 STALE** |

⚠ The php bracket is **6**, not 3: `TASK_PHP_018` has landed, so `ph07` now
carries a gate record *and* a measurement record alongside `ph00` and `ph03`.
All six are FRESH.

---

## §1 The two coverage numbers §1.4 asks for

```
BEFORE  (patterns-php/CATALOGUE.md, 93 rows)   accounted for : 166 / 166   MISSING: 0
AFTER   (the landing applied to a scratch copy) accounted for : 166 / 166   MISSING: 0
```

Logs: `.temp/php21/coverage_before.log`, `.temp/php21/coverage_after.log`.
The "after" run used `.temp/php21/coverage_on.py`, which loads
`.temp/php11/coverage.py` and rebinds its hard-coded `CAT` — **it reimplements
none of the checker**, so the two numbers come from the same code.

`Part A distinct corpus ids` moves **163 → 167**, and every one of the four is
accounted for: `LOGIC-003`, `LOGIC-008` and `LOGIC-018` were Part C ids only and
become Part A ids (`ph99`/`ph100`/`ph101`); `LOGIC-014` moves into `ph48`'s cell.
`CRASH-090` moves ph32 → ph102 and `CRASH-101` moves ph39 → ph41 without
changing the total, which is the point of moving rather than duplicating.

⚠⚠ **I am NOT reporting this as certifying the moves, and task §4.2 is right to
warn about it.** `coverage.py` counts a mention in the **kill table** as
coverage, and **an id merged into the wrong row is invisible to it by
construction** — it reported `166/166` green throughout the whole period in
which `CRASH-101` sat under `ph39` and `LOGIC-014` under `ph47`, both of which
`TASK_PHP_019` then found to be wrong. **`166/166` is necessary and not
sufficient. The mechanism test is what checks the moves; this checks only that
nothing fell on the floor.** That sentence is folded into the landing's C.7
rewrite so the next reader meets it there.

---

## §2 ⭐ THE TRIGGER TEST — all nine, and the rate

**The bar, stated before the rows so it can be attacked.** `TASK_PHP_020` §6.3
says a build task's deliverable #1 is reachability and *"a row engineer starts by
running the row's stated trigger"*. So:

> **PASS** ⇔ an engineer could run the `▸ trigger` **exactly as written** and see
> the **stated** harm.
> **NEEDS CORRECTION** ⇔ it cannot be run as written, or it runs and the stated
> harm does not appear.
> An *additive* finding (something true the row does not say) is **not** a
> correction and is scored separately, exactly as `TASK_PHP_020` §6.2 asked.

Every `file:line` below was opened in the pinned tarball (sha256
`5783e0c0…d6919`, verified at extraction; `.temp/php21/extract.sh`). Where
arithmetic or codegen decided it, I wrote the probe.

| row | corpus id | trigger reaches the cited line? | produces the stated harm? | **verdict** |
|---|---|---|---|---|
| `ph94` | V5C-173 | ✅ `zend_execute.c:4033` | ❌ **measured: no OOB read at any `-O`** | **NEEDS CORRECTION** |
| `ph95` | V5C-015 | ✅ `pack.c:212`, `:214`, `:262` | ✅ **measured**, `emalloc(1)` + 2·INT_MAX-byte emit | PASS ⭐ +1 |
| `ph96` | CRASH-061 | ✅ `zend_object_handlers.c:513` | ✅ NULL deref at `zend_execute_API.c:389` | PASS |
| `ph97` | CRASH-126 | ✅ `mbstring.c:3219` | ✅ `strcasecmp("all", NULL)` | PASS |
| `ph98` | CRASH-163 | ❌ **the trigger cannot be SET UP** | — | **NEEDS CORRECTION** |
| `ph99` | LOGIC-003 | ✅ `zend_execute.c:1279` | ✅ `$o->q` becomes 4 | PASS ⭐ +1 |
| `ph100` | LOGIC-008 | ✅ `zend_object_handlers.c:797` → `zend_execute_API.c:430` | ✅ `A::$p` still 5 | PASS |
| `ph101` | LOGIC-018 | ✅ `zend_compile.c:1899-1900` | ⚠ **not observable as written; half does not compile** | **NEEDS CORRECTION** |
| `ph102` | CRASH-090 | ✅ `html.c:900` at `k = 8260` | ✅ `table[66]` of a 66-element literal | PASS |

> ### **3 of 9 needed a trigger correction. 6 of 9 were clean. 2 gained an additive strengthening.**

### 2.1 ⚠⚠ `ph94` — reaches the line and produces nothing. **Measured.**

The row's claim is that for an `IS_OBJECT` offset, `offset->value.lval` is
`[4 defined handle bytes | 4 bytes of padding `zend_objects_new` never writes]`,
so *"the index is uninitialised memory, not a program value"*.

**Everything structural about that is right, and I confirmed it three ways.**
`sizeof(zend_object_value) == 16` with `handlers` at offset 8, so `lval` overlays
`[handle:4][padding:4]`. `zend_objects.c:95` really is a bare stack local and
`:99`/`:100` really do write only the two members — visible in the `-O0`
disassembly as `mov %eax,-0x20(%rbp)`, **four bytes into an eight-byte slot**.
`zend_API.c:710` really does `arg->value.obj = zend_objects_new(…)`, a
whole-struct copy. And the trigger reaches `:4033`: `empty($s[$o])` compiles to
`ZEND_ISSET_ISEMPTY_DIM_OBJ` (`zend_compile.c:3229-3230`), the `IS_STRING`
container arm at `:4025` has **no type test and no `convert_to_long` anywhere**,
and the offset zval is passed through unconverted.

**What does not survive is the harm.** `.temp/php21/ph94_probe2.c` replicates
`zend_objects.c:93-104` statement for statement — the `emalloc`, both writes on
`*object`, the handle arriving from a `noinline` callee — and `zend_API.c:708-710`
around it, with the stack dirtied before each trial:

```
gcc 13.3.0, identical at -O0 / -O1 / -O2 / -O3:
t0 handle=1 padding=0x00000000 lval=1  :4033 guard PASSED -> reads s[lval] IN BOUNDS
t1 handle=2 padding=0x00000000 lval=2  :4033 guard PASSED -> reads s[lval] IN BOUNDS
...
verdict: wild read observed = NO
```

**Why**, from the `-O0` disassembly: the return sequence loads all eight bytes
(`mov -0x20(%rbp),%rax`) and then narrows through **`mov %esi,%eax`**, which
zeroes RAX's upper half. So `lval == handle` — 1, 2, 3 … — a small positive
*program value*, and `:4033`'s read lands inside `"abcdefgh"`. Push the handle
past `strlen` and the guard simply refuses. **On this toolchain there is no
input for which the trigger produces a wild read.**

⚠ **This is a property of the toolchain, not of the C, and I am not claiming
otherwise.** The uninitialised *read* is real at the C level — an 8-byte read of
a member of which only 4 are ever written — and the corpus's own valgrind run
reports exactly that: *"Use of uninitialised value of size 8"* at `:4033`, with
a SEGV on their build. A different gcc did not narrow.

**Consequence for the row, and it is bigger than the trigger line.** The block's
`⚠ risk` already says *"a memset'd model deletes the mechanism"*. That is too
weak: **even a producer that genuinely never writes those four bytes does not
deliver garbage here.** So the kernel must take the un-written half from the
**blob** — which the row's own `▸ blob` line already specifies — and criterion 2
must be discharged against the blob-driven kernel, with the faithful producer's
behaviour reported. The corrected trigger and this rider are in the landing.

⭐ **This is `ph29`'s lesson one level up.** `TASK_PHP_020` found `ph29` firing
only through *undefined* behaviour, which a compiler may fold. `ph94` fires only
through *unspecified* padding, which this compiler makes deterministic and
harmless. **Both are "the trigger depends on something that is not the pattern",
and only a probe finds either.**

### 2.2 ⚠⚠ `ph98` — the trigger cannot be set up. `ph21`'s shape.

Stated: *"a `set_exception_handler` handler that cannot be called, with an
exception pending."*

**`set_exception_handler` validates its argument at registration.**
`zend_builtin_functions.c:1038` is
`if (!zend_is_callable(*exception_handler, 0, &exception_handler_name))` →
`E_WARNING` and **return without storing**. An engineer's first three attempts —
a missing function, a non-callable string, an array naming no method — are all
refused before anything is stored, and none of them ever reaches `zend.c:1078`.

The handler must be **broken after registration**, and the route is a second
defect the row does not mention: `:1060-1061` does
`*EG(user_exception_handler) = **exception_handler; zval_copy_ctor(…)`, and
`zval_copy_ctor` on an array copies the `HashTable` but **shares its element
zvals by refcount**. So:

```php
class C { function m($e){} }
$o = new C; $arr = array($o, 'm');
$r = &$arr[1];               // element 1 becomes is_ref BEFORE registration
set_exception_handler($arr); // the stored copy shares that very zval
$r = 12345;                  // in-place write -> stored method name is IS_LONG
throw new Exception("boom");
```

`zend_call_function` then takes its `IS_ARRAY` path at `:598`, pulls element 1
into `fci->function_name`, and returns FAILURE at
**`zend_execute_API.c:678-680`** (`if (fci->function_name->type!=IS_STRING)`).
`zend.c:1083 zend_exception_error(EG(exception))` runs with the global that
`:1075` cleared, and `zend_exceptions.c:519`'s first statement `Z_OBJCE_P(NULL)`
→ `zend_API.c:204 Z_OBJ_HT_P(NULL)` faults at offset 8 — which is the corpus's
recorded `SEGV on unknown address 0x000000000008`.

**The defect site, the mechanism and the invariant are all exactly right.** Only
the trigger was a one-line paraphrase of a thing the engine refuses.

### 2.3 ⚠ `ph101` — fires, but cannot be observed as written, and half does not compile

Stated: `class A { protected static $x = "PARENT"; } class B extends A { public
static $x; } B::$x = "W";` → `A::$x` is `"W"`; and `class D extends C { public
static $y = "CHILDVAL"; }` prints NULL.

The first fragment **does** reach `:1899-1900` and **does** alias B's slot onto
A's zval — I traced `zend_do_inheritance`'s `:1990 zend_hash_merge(…,
inherit_static_prop, …)`, the `refcount++; is_ref = 1;` at `:1967-1971`, the
`:1899 (*prop)->refcount++`, and the `:1900 zend_hash_update` whose destructor
destroys the child's own zval. Two things stop an engineer:

- **`A::$x` is `protected`**, so `var_dump(A::$x)` from global scope is not a
  wrong answer, it is `E_ERROR "Cannot access protected property"`
  (`zend_object_handlers.c:783-784`). The row needs an accessor in `A`.
- **`class C` is never declared**, so the second clause is not a program.

And there is a live trap the row does not name: `:1891-1897` raises
`E_COMPILE_ERROR` when **both** the parent's and the child's defaults are
non-NULL, so the child's slot must be left uninitialised for `:1899` to be
reached at all. The corrected trigger (the corpus's own reproducer, verified
line by line) is in the landing.

⚠ **This is the marginal one of the three and I say so.** It fires and it
produces the harm; the defect is in the stated *witness*. I counted it because
the operational question is *"can an engineer run this and see it?"* and the
answer is no on both clauses. **A reviewer who prefers to score it `additive`
would put the rate at 2/9 and the landing would proceed** — the manager should
know the decision turns on this row and nothing else.

### 2.4 ✅ `ph95` — PASS, measured, with a UB rider that cannot be discharged

`pack("s2147483647", 1)`: `atoi` gives `arg = INT_MAX`; `:212 currentarg += arg`
wraps `1` to `INT_MIN`; **`:214`'s guard runs and is false**; `:262
outputpos += arg*2` wraps to `-2`, `outputsize` stays 0, `:304 emalloc(1)`; the
emit arm `:388-391` then writes 2 bytes per iteration for `arg` iterations and
walks `argv` past its `argc` entries on the second.

`.temp/php21/ph95_probe.c` lifts the declarations verbatim:

```
                                    argc arg          currentarg      guard
TRIGGER  pack("s2147483647", 1)      2  2147483647   -2147483648     PASSED  emalloc(1)
neighbour arg = INT_MAX-1            2  2147483646    2147483647     REFUSED
neighbour arg = 2147483645           2  2147483645    2147483646     REFUSED
```

Bit-identical at `-O0`, `-O3` **and** `-O3 -fwrapv`. The two neighbours are the
must-fire control in the opposite direction: they show the guard is defeated
**by the wrap** and by nothing else.

⚠⚠ **But the wrap at `:212` is signed-integer overflow, and unlike `ph29` there
is NO UB-free trigger.** `arg` cannot be negative (`:208-210` rewrites any
negative `arg`; the digit scanner at `:152-158` admits no sign), so the only way
past `:214` is the wrap — and upstream's own fix, `db420cb6a14`, is a
*pre-overflow test*. **The task's rule *"a trigger that needs UB must be
replaced with one that does not"* cannot be satisfied for this row**; what is
owed is the risk note, which the landing adds. §6.2 says why this is bigger than
one row.

### 2.5 ✅ `ph96`, `ph97`, `ph100`, `ph102` — PASS, traced end to end

- **`ph96`** — `:511` requires the class to implement `ArrayAccess` (the trigger
  should say so and the landing makes it explicit). `zend_call_function` writes
  `*fci->retval_ptr_ptr = NULL` at `:595` under the quoted comment, executes the
  throwing method, and **returns SUCCESS unconditionally at `:873`** even with
  `EG(exception)` set (`:870-872`). `:513 zval_ptr_dtor(&retval)` reaches
  `_zval_ptr_dtor`'s `:389 (*zval_ptr)->refcount--` with `*zval_ptr == NULL`.
- **`ph97`** — the cheapest and most reliable of the nine.
  `zend_parse_va_args` sets `min_num_args = 0` from the `|` (`zend_API.c:485-487`),
  passes the count test at `:511`, and its write loop `:537 while (num_args-- > 0)`
  runs **zero** times before `return SUCCESS`. `typ` keeps the caller's `NULL`.
- **`ph100`** — two premises I did not take on trust. `public static $p = K;`
  really compiles to an `IS_CONSTANT` zval (`zend_do_fetch_constant`,
  `zend_compile.c:2835-2843`, `ZEND_CT` arm); and the **write** path reaches
  `:797` too — `zend_fetch_var_address_helper` calls
  `zend_std_get_static_property` at `zend_execute.c:753` for **every**
  `BP_VAR_*`, not only reads. `SEPARATE_ZVAL` (`zend.h:554-566`) then separates
  on `refcount>1` **regardless of `is_ref`** and clears the flag at `:564`.
- **`ph102`** — `PHP_FUNCTION(html_entity_decode)` passes `all = 1`
  **unconditionally** (`:1219`), so `:890 if (all)` is always taken and the walk
  covers every `cs_utf_8` row. `ent_uni_punct` measured at **66 for 67** by two
  independent tools that agree — `.temp/php19/entcount.py` (the C compiler) and
  the manager's `.temp/mgr165/count_ent.py` re-run here (17 tables · 4 short ·
  **0 unevaluated**). At `k = 8260`, `:900` indexes `table[66]`.

### 2.6 ⭐ `ph99` — PASS, and the harm is larger than the row says

`$o->virt++` → `zend_std_get_property_ptr_ptr` returns NULL because a `__get`
exists (`:470-473`) → `have_get_ptr == 0` → `:1266 read_property(…, BP_VAR_RW)`
→ the `__get` arm returns `rv` unseparated (`:296-300`, `:311`) → `:1279
incdec_op(z)` **with no separator**, where the sibling `zend_pre_incdec_property`
separates at **`:1220`** (⚠ the report and the block both cite `:1219`, which is
`z->refcount++`; the landing corrects it). And `ZEND_RETURN`'s by-value arm hands
back the **live** zval rather than a copy — `zend_execute.c:2883-2886`,
`*EG(return_value_ptr_ptr) = retval_ptr; retval_ptr->refcount++`.

⭐ **Additive:** `zend_API.c:716` populates an object's properties with
`zend_hash_copy(…, zval_add_ref, …)`, so `$o->q`'s zval **is**
`ce->default_properties["q"]`. The in-place increment therefore moves the
**class default**, and a later `new O` starts at 4. The row says `$o->q`
becomes 4; the blast radius is every future instance.

### 2.7 What the corpus's own reproducers contributed

For seven of the nine the corpus ships a reproducer (`input/crash/*.php`,
`input/logic/*.php`, `crashes/roundE/V5C-173-*.php`). ⭐ **Where the row's
trigger and the corpus's reproducer agree, the row was right in every case
(6/6); all three corrections are rows where they DIVERGE** — `ph98` and `ph101`
because the row compressed a multi-step setup into one clause, `ph94` because
the reproducer's claim (*"frequently negative"*) is one this box's compiler
falsifies. **That is a cheap pre-filter for the next adjudication: diff the
proposed trigger against the corpus reproducer before writing it down.**

### 2.8 What the trigger test does NOT establish

1. **I did not run PHP.** Every verdict is source-tracing against the pinned
   tarball plus three compiled arithmetic/ABI probes. Where I say "reaches", I
   mean the control flow and the types permit it, traced line by line.
2. **`ph94`'s measurement is gcc 13.3.0 / x86-64 / SysV.** It is decisive for
   *this box* — which is the box a kernel is built on — and it is **not** a
   claim about php-5.0.0 as the corpus built it.
3. **Criterion 2 is demonstrated for none of the nine**, and none was expected;
   it is discharged at build.
4. **The six PASSes are graded on the harm the row STATES.** I did not go
   looking for stronger harms except where one fell out (`ph99`, `ph95`).

---

## §3 The tiers, re-derived — §2's third bullet

`TASK_PHP_019` §9.4 flags its own tiers as placeholders: *"every one of the
eight is `narrowed`, which is a suspiciously uniform answer and probably means I
did not think hard about any of them."*

**Re-derived from the source, all nine, against `PROTOCOL_PHP.md` §A1 and the
`land_m4.py` precedent (a defect site inside a PHP_FUNCTION / VM-handler /
arg-parsing frame is `narrowed`): every one is confirmed.** The uniformity is
real and it has a reason §9.4 did not state:

| row | the frame the defect sits in | tier |
|---|---|---|
| `ph94` | VM opcode handler `zend_isset_isempty_dim_prop_obj_handler` | `narrowed` |
| `ph95` | `PHP_FUNCTION(pack)` — arg-parsing frame (same function as `ph22`, already `narrowed` via `land_m4`) | `narrowed` |
| `ph96` | object handler + the executor's call contract, stubbed from the blob | `narrowed` |
| `ph97` | `PHP_FUNCTION(mb_get_info)` — arg-parsing frame, and the `\|` optionality must be modelled | `narrowed` |
| `ph98` | `zend_execute_scripts`, with the callee's FAILURE supplied by the blob | `narrowed` |
| `ph99` | VM helper + object handler; only the userland getter is modelled | `narrowed` |
| `ph100` | object handler + `zval_update_constant`; the constants table is one bit | `narrowed` |
| `ph101` | `do_inherit_property_access_check` + a dictionary with a value destructor | `narrowed` |
| `ph102` | `php_unescape_html_entities` — a **PHPAPI helper with a plain C signature**, no zval, no arg parsing | **`verbatim`** |

⭐ **Eight of the nine are `narrowed` because eight of the nine sit inside a
PHP_FUNCTION, a VM handler, an object handler or the executor** — precisely the
frames §A1 defines as `narrowed`. The ninth is the only one whose defect lives
in an ordinary C function over ordinary C data, and it is the only `verbatim`.
**The uniform answer was the right answer; what was missing was the reason.**

⚠ Restated because it decides nothing: **a tier is a cost statement and never a
filter** (`CATALOGUE.md` §0.2, `PLAN_PHP.md` §4). No row here gains or loses
admission.

⚠ Two are arguable and I say which way: `ph96` and `ph98` replace a *callee* —
the executor — with a blob-driven stub. I graded them `narrowed` because the
defect site's own statements lift unchanged and only the callee's contract is
supplied; a reviewer who reads §A1's `modelled` as covering that would move both,
and nothing follows from it either way.

---

## §4 The landing — built, `--check`-clean, **NOT APPLIED**

`.tasks-php/land_019_020.py`, following `land_m4.py`'s precedent exactly:
`--check` / `--apply`, and it **refuses unless every anchor it expects is
present exactly once**.

```
$ python3 .tasks-php/land_019_020.py --check
rows in Part A before: 93
  ok  header-counts …  ok  C7-output …  ok  B-T6-new       (45 anchors, all: 1)
rows in Part A after : 102   Part B blocks after: 102
--check only, nothing written. All anchors resolve exactly once.
```

It also refuses on **re-application** (verified: a second `--apply` to the same
file reports 25 anchors at 0 and writes nothing), and it cross-checks Part A
against Part B and asserts the final row count is 102 before writing a byte.

**What it lands.** `TASK_PHP_019` §5 (the eight rows), §10.6 (`ph32` rewritten
for three tables + `ph102`, with **R1h stated as TWO commits**), §4 (the `C.1`
rewrite and the `ph03` sentence); `TASK_PHP_020` §7.1 (`ph21`), §7.2 (`ph93`),
§7.3 (ten additive one-liners) and §4 (`ph29`'s three strengthenings); the four
`corpus rows` moves; the recounted headings; the `C.7` refresh; and §9's
derived-label caveat.

**Four things it does that were not spelled out, each because the file forced
them:**

1. **Every withdrawn kill stays in `C.1` with its original note quoted in
   full**, struck through and marked with its new row — `TASK_PHP_012` M1, *a
   kill that vanishes is worse than a kill that was wrong*. **No row is deleted
   from Part C.** That includes `CRASH-090`, which `TASK_PHP_019` §10.6 proposed
   to *delete* and replace with a paragraph; keeping it in the table is the same
   information in the shape M1 asks for.
2. **A `†` marker and its legend.** `inv/obl` and `echoes` on `ph94`–`ph102` are
   **derived, not carried** (task §3.3). Rather than a footnote nobody reads, the
   nine cells carry `†` and the column legend says what it means. §9 gains the
   matching caveat.
3. **`ph92` and `ph93` move into the Spatial section.** They are `spatial` rows
   that sat under the `Temporal` heading, which is why the headings summed to 91
   — §5.1.
4. **`ph99`'s citation of the separating sibling is corrected** `:1219` → `:1220`.

**Why it was not applied:** §0.1. The script is the deliverable that makes the
landing one command after the review cycle §4.1 asks for.

---

## §5 The small things §1 asked for — both settled

### 5.1 The section headings: recounted from the table itself

```
                          heading   rows in section   axis cells
Spatial                      38            38            spatial   40
Type / initialisation        22            22            type      22
Temporal                     31            33            temporal  31
                                                         --------- ---
                                          93                       93
```

**The headings do not sum to the total because two rows sit under the wrong
one.** `ph92` and `ph93` are both `spatial` in their axis cell and both are
appended at the end of the **Temporal** table. So the `Spatial` and `Type`
headings are correct *for their sections* and wrong *for their axis*, and
`Temporal (31)` is correct for its axis and wrong for its section.

**The fix that makes all three readings agree** — and the one the landing
applies — is to move the two rows into the Spatial section. Afterwards, with the
nine new rows filed by axis:

```
Spatial (42)   heading 42  rows 42  axis 42
Type … (29)    heading 29  rows 29  axis 29
Temporal (31)  heading 31  rows 31  axis 31          sum = 102 ✅
```

Verified on the applied scratch copy: **no row sits under a heading its axis
cell contradicts.** The file header's `91 rows … 38 · 22 · 31` is corrected to
`102 rows … 42 · 29 · 31`, and its *"one of them (`ph91`) unresolved"* to
*"two of them (`ph15`, `ph91`)"* — `ph15` has been `**unresolved**` in its status
cell since it was written.

### 5.2 ✅ The two empty `tier` cells are DELIBERATE. **Do not fill them.**

They are **`ph15` (line 93)** and **`ph91` (line 179)** — and they are *exactly*
the two rows whose status cell reads `**unresolved**`. Both hold `—`, not
whitespace. Both Part B blocks explain it:

- `ph15`: *"⚠⚠⚠ **THE MECHANISM BELOW IS REFUTED. DO NOT BUILD THIS ROW.**"* — and
  the block writes `**UNRESOLVED**` in the slot where every other block writes
  its tier, which is the convention made visible.
- `ph91`: *"the corpus label and its citation disagree … I could not decide which
  is the row."*

**A tier prices the extraction of a known mechanism.** Where the mechanism is
refuted or undecided there is nothing to price, and a tier written there would
be a cost claim about a row that has no defect yet — the *"reassurance that tells
the reader not to look"* shape that `.temp/mgr165/count_ent.py`'s own docstring
was rewritten to avoid. **They are correct as they stand and the landing does not
touch them.**

---

## §6 Three things nobody asked for, found on the way

### 6.1 ⭐ `coverage.py` cannot count a three-digit row id, and cannot report that it cannot

```
$ python3 .temp/php21/coverage_on.py <the 102-row file>
catalogue rows in Part A : 99  (ids ph01..ph91, gaps: none)
Part B blocks            : 99  (in Part A but not Part B: none)
```

Two independent defects, both producing a **positive claim about a population
the script cannot enumerate**:

1. Its last two checks use `^\| (ph\d\d) \|` and `^\*\*(ph\d\d) ` —
   **exactly two digits**. Measured: 99 seen, 102 present, invisible =
   `['ph100', 'ph101', 'ph102']`.
2. The `gaps:` set is `ph01..ph<the number it just found>`, i.e. built **from
   its own hit count**. Having found 99 it expects 99, finds 99, and prints
   **`gaps: none`** — so the blindness is undetectable from its own output.

⚠ **The `166 / 166` accounting is NOT affected** — that path scans
`line.startswith("| ph")` and does see them, which is why §1's numbers stand.
**But `CATALOGUE.md` §C.7 pastes this script's output as evidence**, so the
row-count line must be fixed before it is pasted again. I did **not** edit
`.temp/php11/coverage.py`: it is another task's cited artefact and the landing
records the defect in `C.7` instead, with the true numbers beside it.

⚠ This is `.memory-php/00`'s F35/F17 shape at a third site — *a check whose
failure path renders as a positive claim about the C* — and it is the same
defect class the manager already fixed in `count_ent.py`. **Two of this
programme's small checkers have now had it.**

### 6.2 ⚠ The *"replace a UB trigger"* rule cannot be satisfied by an `int`-wrap row

`TASK_PHP_020` §4 derived a good rule from `ph29`: prefer a trigger that does not
rely on undefined behaviour, because gcc may fold it and *"a kernel built to it
may behave differently at `-O3` than at `-O0` for a reason that is not the
pattern"*. `ph29` had such a trigger available. **`ph95` does not** (§2.4) —
and neither, structurally, does any row whose mechanism *is* a signed `int` wrap,
which is most of family `S3`: `ph18`–`ph30`, `ph92`, `ph93`.

✅ Checked, because it decides whether this is a problem: **`harness/build.py`
passes neither `-fwrapv` nor `-fno-strict-overflow`** — `c_flags()` is
`["-std=c99", "-Wall", "-Wextra"]` plus `-O0`/`-O3` plus the mode flag — and
`build.py` is frozen (editing it costs a full re-measure of all 33 PAT rows).

**So the rule needs a second clause, and I state it rather than apply it:**
*where the wrap is the mechanism, the trigger cannot avoid UB; what the row owes
instead is a measurement that the built kernel wraps the same way at both
optimisation levels.* `.temp/php21/ph95_probe.c` is that measurement for `ph95`
and it is green today. **This is a manager decision, not an engineer's** — it
touches a dozen rows and a frozen file.

### 6.3 `.memory-php/00-corpus.md` will be stale the moment this lands

It reads *"`patterns-php/CATALOGUE.md` catalogues **93**"*. After the landing it
is 102. **I did not touch it** (manager-only, rule 4/9) — flagging it so the
manager updates it in the same pass, along with `RECAP_PHP.md`'s row count if it
carries one.

---

## §7 Where I disagree, and what this report does not establish

**Task §3.1: land it anyway and say so.** I found **nothing** in either report's
verdicts I would overturn. Every one of the nine reversals survives the C: I
re-opened `ph96`'s, `ph97`'s and `ph98`'s *"the failure IS tested"* claims, and
all three are exactly right; `ph99`/`ph100`/`ph101`'s three-way split of the
LOGIC family turns on `SEPARATE_ZVAL` being a no-op at `refcount == 1`, which is
`zend.h:558` verbatim; `ph102`'s separation from `ph32` rests on two fix commits
neither of which touches the other's tables. **The corrections in §2 are to
`▸ trigger` lines and to one `⚠ risk` line. No verdict moved.**

⚠ **One place where I would go further than `TASK_PHP_019`, and did not:**
its §9.3 names `p48` on `ph94` and `p05` on `ph95` as the `echoes` it is least
sure of. Having now read `ph94`'s C closely, I think `p35` alone is the honest
answer and `p48` is a stretch — but `echoes` is a cross-reference and never a
filter, no `pNN` was opened, and re-adjudicating it is not this task. **Landed
as written, marked `†` derived.**

**What this report does not establish:**

1. **The six PASS verdicts are not a claim that those rows are buildable** — only
   that their `▸ trigger` reaches the cited line and shows the stated harm.
2. **`166/166` does not certify the four `corpus rows` moves** (§1). Nothing
   mechanical does.
3. **Nine unreviewed rows are still nine unreviewed rows.** Task §4.1's worry
   stands and this report does not answer it; it only supplies the number the
   stop condition needed.
4. **The comparison of rates in §0.4 is soft.** 3/9 here against
   `TASK_PHP_020`'s 3/19 is not a like-for-like measurement: `_020` spent a
   median of 6 min/row and says itself that *"a cheaper audit than mine would
   have returned 15/15"*, while **`ph94`'s failure was findable only with a
   compiled probe** and a 2–4 min read would have passed it. **The direction is
   probably right and the magnitude is not measured.** ⚠ Nor is 9 a sample from
   which to compute anything; it is the population.
5. **`ph94`'s measurement is one toolchain.** A second compiler would sharpen it
   and there is no clang on this box.

---

## §8 Scratch — kept and deleted (`.temp/php21/`)

**Kept (generators and evidence):** `extract.sh`, `ph94_probe.c`/`.log`,
`ph94_probe2.c`/`.log`, `ph95_probe.c`/`.log`, `coverage_on.py`,
`coverage_before.log`, `coverage_after.log`, `NOTES.md`.
**Deleted (re-derivable, with the rebuild command in `NOTES.md`):** `src/`
(`sh extract.sh`), the three probe binaries and their `.o` (`gcc -O0 -o …`), and
`CATALOGUE.after.md` (`cp` + `land_019_020.py --apply --to`).

**Files written by this task, in total:** `.tasks-php/land_019_020.py`,
`.tasks-php/TASK_PHP_021_REPORT.md`, and `.temp/php21/*`. Nothing else.

⚠ **`git status` at close also shows `M .tasks-php/TASK_PHP_022_REPORT.md`. That
is NOT this task** — a concurrent session was writing it (mtime 07:48, +94/−11);
I never opened it. Recorded so the manager does not attribute it here.
