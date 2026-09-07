# TYPE axis — candidate mining from PHP 5.0.0

Citation base: `php-5.0.0.tar.gz`, sha256 `5783e0c0ba94f165633a565fe73a83e59cf17b6880ef95fa8f936dc6301d6919`,
5595997 bytes (verified by `sha256sum` at the start of this session). **Every line number below was read
out of that tarball**, never out of a build tree. Reproduce any of them with

```
TB=/home/apt/repos_common/php-in-safe-rust/.app-tests/.temp/oracle/build-5.0.0/php-5.0.0.tar.gz
tar -xzOf $TB php-5.0.0/<file> | grep -n "" | sed -n 'A,Bp'
```

(`grep -n "" | sed -n` rather than plain `sed -n` so the printed numbers are the file's own.)

---

## 1. The substrate — paste this into the pattern spec

Everything on this axis is one design decision: **PHP's value type is a hand-rolled tagged union whose
tag and payload are read by two entirely separate macro families, and only one of them is ever called.**

### The tagged union — `Zend/zend.h:275-293`

```c
typedef union _zvalue_value {
	long lval;					/* long value */
	double dval;				/* double value */
	struct {
		char *val;
		int len;
	} str;
	HashTable *ht;				/* hash table value */
	zend_object_value obj;
} zvalue_value;


struct _zval_struct {
	/* Variable information */
	zvalue_value value;		/* value */
	zend_uint refcount;
	zend_uchar type;	/* active type */
	zend_uchar is_ref;
};
```

with `zend_object_value` — the member that array_unique reinterprets as a `HashTable *` — at
`Zend/zend.h:270-273`:

```c
struct _zend_object_value {
	zend_object_handle handle;      /* typedef unsigned int, zend.h:265 */
	zend_object_handlers *handlers;
};
```

### The type tags — `Zend/zend.h:386-399`

```c
/* data types */
#define IS_NULL		0
#define IS_LONG		1
#define IS_DOUBLE	2
#define IS_STRING	3
#define IS_ARRAY	4
#define IS_OBJECT	5
#define IS_BOOL		6
#define IS_RESOURCE	7
#define IS_CONSTANT	8
#define IS_CONSTANT_ARRAY	9

/* Ugly hack to support constants as static array indices */
#define IS_CONSTANT_INDEX	0x80
```

### The accessors — `Zend/zend_operators.h:234-275`

**This is the whole axis in one screen.** Note that `Z_TYPE` is a *separate* macro from every payload
accessor, and that **no payload accessor consults it**:

```c
#define Z_LVAL(zval)			(zval).value.lval
#define Z_BVAL(zval)			((zend_bool)(zval).value.lval)
#define Z_DVAL(zval)			(zval).value.dval
#define Z_STRVAL(zval)			(zval).value.str.val
#define Z_STRLEN(zval)			(zval).value.str.len
#define Z_ARRVAL(zval)			(zval).value.ht
#define Z_OBJ_HANDLE(zval)		(zval).value.obj.handle
#define Z_OBJCE(zval)			zend_get_class_entry(&(zval) TSRMLS_CC)
#define Z_OBJPROP(zval)			Z_OBJ_HT((zval))->get_properties(&(zval) TSRMLS_CC)
#define Z_OBJ_HANDLER(zval, hf) Z_OBJ_HT((zval))->hf
#define Z_RESVAL(zval)			(zval).value.lval

#define Z_LVAL_P(zval_p)		Z_LVAL(*zval_p)
...
#define Z_LVAL_PP(zval_pp)		Z_LVAL(**zval_pp)
#define Z_STRVAL_PP(zval_pp)	Z_STRVAL(**zval_pp)
#define Z_STRLEN_PP(zval_pp)	Z_STRLEN(**zval_pp)
#define Z_ARRVAL_PP(zval_pp)	Z_ARRVAL(**zval_pp)
...
#define Z_TYPE(zval)		(zval).type
#define Z_TYPE_P(zval_p)	Z_TYPE(*zval_p)
#define Z_TYPE_PP(zval_pp)	Z_TYPE(**zval_pp)
```

`Z_STRVAL_PP(x)` is textually `(**x).value.str.val`. There is no check anywhere in that expansion.
Writing `Z_STRVAL_PP` on an `IS_LONG` zval is not a mistake the compiler can see — it is the *documented
way to read a string*, applied to the wrong value.

### Two helper macros that do most of the damage

**`HASH_OF` — `Zend/zend_API.h:519`.** A two-arm accessor whose postcondition is *weaker* than what its
callers assume. It succeeds for arrays **and objects**:

```c
#define HASH_OF(p) ((p)->type==IS_ARRAY ? (p)->value.ht : (((p)->type==IS_OBJECT ? Z_OBJ_HT_P(p)->get_properties((p) TSRMLS_CC) : NULL)))
```

**`convert_to_*_ex` — `Zend/zend_operators.h:210-223`, over `SEPARATE_ZVAL_IF_NOT_REF` at `Zend/zend.h:554-571`.**
A copy-on-write conversion that **silently becomes an in-place retype when `is_ref == 1`**:

```c
#define convert_to_ex_master(ppzv, lower_type, upper_type)	\
	if ((*ppzv)->type!=IS_##upper_type) {					\
		SEPARATE_ZVAL_IF_NOT_REF(ppzv);						\
		convert_to_##lower_type(*ppzv);						\
	}

#define convert_to_long_ex(ppzv)	convert_to_ex_master(ppzv, long, LONG)
#define convert_to_string_ex(ppzv)	convert_to_ex_master(ppzv, string, STRING)
```

```c
#define SEPARATE_ZVAL(ppzv)									\
	{														\
		zval *orig_ptr = *(ppzv);							\
		if (orig_ptr->refcount>1) {							\
			orig_ptr->refcount--;							\
			ALLOC_ZVAL(*(ppzv));							\
			**(ppzv) = *orig_ptr;							\
			zval_copy_ctor(*(ppzv));						\
			(*(ppzv))->refcount=1;							\
			(*(ppzv))->is_ref = 0;							\
		}													\
	}

#define SEPARATE_ZVAL_IF_NOT_REF(ppzv)		\
	if (!PZVAL_IS_REF(*ppzv)) {				\
		SEPARATE_ZVAL(ppzv);				\
	}
```

`SEPARATE_ZVAL_IF_NOT_REF` is a **no-op exactly when the value is shared as a reference** — which is
exactly when separating matters most. That single line is the root cause of both CoW rows on this axis.

### ⚠ The collision — two `IS_*` namespaces, overlapping values

This is not in the brief and I think it is the single most valuable thing I found. There are **two
unrelated `IS_*` enumerations** in headers that are both included everywhere, and **their values collide**:

| value | `Zend/zend.h:387-396` (zval `.type`) | `Zend/zend_compile.h:285-288` (znode `.op_type`) |
|--:|---|---|
| 0 | `IS_NULL` | — |
| **1** | **`IS_LONG`** | **`IS_CONST` = (1<<0)** |
| **2** | **`IS_DOUBLE`** | **`IS_TMP_VAR` = (1<<1)** |
| 3 | `IS_STRING` | — |
| **4** | **`IS_ARRAY`** | **`IS_VAR` = (1<<2)** |
| 5 | `IS_OBJECT` | — |
| **8** | **`IS_CONSTANT`** | **`IS_UNUSED` = (1<<3)** |

`zend_compile.h:285-288` verbatim:

```c
#define IS_CONST	(1<<0)
#define IS_TMP_VAR	(1<<1)
#define IS_VAR		(1<<2)
#define IS_UNUSED	(1<<3)	/* Unused variable */
```

So `last_op->op2.op_type == IS_CONST` and `last_op->op2.u.constant.type == IS_LONG` are **the same
comparison against the same integer 1**, on two different fields, meaning two unrelated things. Candidate
#2 (`CRASH-144`) is what happens when a programmer checks the first and then reads as though they had
checked the second. A benchmark row that preserves this collision is carrying a real, named, citable
C-language hazard, not a toy.

---

## 2. Mechanism families — grouping the 34 rows

The brief's ~34 rows (CWE-843 ×11, CWE-476 ×14, CWE-664 ×5, CWE-908 ×2, CWE-822 ×1, CWE-457 ×1) resolve
into **twelve** mechanisms, not one or two. Families are named by *what the C code does wrong*, and I
tag each with the brief's requested READ / WRITE / ORDERING distinction.

| # | family | READ / WRITE / ORDERING | rows | candidate |
|---|---|---|---|---|
| A | **Missing tag guard on a union read.** No check of any kind at the site. | READ | CRASH-036, 037, 101 | #1 |
| A2 | **Presence checked, type not** — a hash lookup succeeds and that is taken as licence to read the value at a fixed C type. Compounded by a null-check that passes on garbage. | READ | CRASH-093 (+ zend_exceptions.c:310) | #8 |
| A3 | **Container checked, elements not** — a per-element callback assumes every element has the container's element type. | READ | CRASH-039 | #9 |
| B | **Guard present, wrong tag namespace** — checks `znode.op_type` and reads the `zval.type` union. | READ | CRASH-144 | #2 |
| C | **Type laundering by a two-arm helper** (`HASH_OF`). C1: result null-checked, then over-concluded to be an array. C2: result not checked at all. | READ | CRASH-079 (C1), CRASH-111 (C2) | #4, #13 |
| D | **Type inferred from a creation path** — 'entries here are always arrays because *this* path calls array_init', while another path inserts a scalar. | READ | CRASH-085 | #12 |
| E | **Type-changing write through an unseparated shared value** — `SEPARATE_ZVAL_IF_NOT_REF` no-ops on `is_ref`, so a CoW conversion retypes in place and invalidates a check that did hold. | **WRITE** | CRASH-104 (callee), CRASH-058 (caller), LOGIC-003, LOGIC-008, LOGIC-014, LOGIC-017, LOGIC-018 | #7 |
| F | **Statement ordering** — a count field and its container are transiently inconsistent across a re-entrancy window. | **ORDERING** | CRASH-153 (link 1) | #5 |
| G | **Discarded status code leaves an out-parameter unwritten**, and the uninitialised local is then dereferenced. | READ (of an uninit local) | CRASH-153 (link 2) | #11 |
| H | **Uninitialised struct consumed as function pointers** because an attacker-controlled flag, forwarded through an all-ones mask, enables a callee path that reads fields the caller never wrote. | READ (in the callee) | CRASH-087 | #10 |
| I | **Guard at the wrong pointer depth** — `if (!value)` where `if (!*value)` was meant. | READ | CRASH-143 | #6 |
| J | **Wrong PC stride on an early-exit path** — a two-word instruction's trailing data word is decoded as an instruction. | control flow | CRASH-023 | #3 |
| K | **Tag arithmetic with the guard replicated on some switch arms and forgotten on one.** | control flow | CRASH-041 | #14 |
| L | **Unconstructed caller-supplied slot destructed on an early-exit path**; a switch dispatches on an uninitialised tag byte. | READ (of an uninit tag) | LOGIC-007 | #15 |

Fifteen candidates cover twelve of these families. The remaining CWE-476 rows are ordinary
missing-NULL-check bugs (see §4).

---

## 3. ⚠ The call I was asked to check — the manager's hypothesis is **half right, and wrong in an
important way on the first half**

> *"I believe the 11 CWE-843 rows are essentially ONE mechanism (a missing tag guard before a union read)
> repeated at eleven sites, and that the CoW / reference-separation rows (`string.c:1945`,
> `zend_execute_API.c:730`) are a genuinely DIFFERENT second mechanism."*

**On the second half: correct, and I can strengthen it.** The CoW rows are not merely different — they
share one *named, citable* root cause that the read-side rows do not touch: `SEPARATE_ZVAL_IF_NOT_REF`
(`Zend/zend.h:568-571`) is a no-op when `is_ref == 1`, so `convert_to_*_ex` (`zend_operators.h:210-214`)
silently degrades from copy-on-write to in-place retype. `CRASH-104` is that defect seen from the callee
and `CRASH-058` is the same defect seen from the caller one frame up. They are a matched pair, and the
missing guard is on a **WRITE**.

**On the first half: no.** The eleven CWE-843 rows are **five** mechanisms, not one:

| mechanism | rows | count |
|---|---|--:|
| A — missing tag guard on a read (incl. A2/A3 variants) | CRASH-036, 037, 039, 093, 101 | **5** |
| C — `HASH_OF` type laundering | CRASH-079, 111 | 2 |
| E — unseparated in-place retype (**the CoW family**) | CRASH-058, 104 | 2 |
| B — guard on the wrong tag namespace | CRASH-144 | 1 |
| D — type inferred from creation path | CRASH-085 | 1 |

**So only 5 of the 11 are the mechanism the hypothesis attributes to all 11** — and, critically, **the
"genuinely different second mechanism" is not outside the eleven; it *is* two of them.** `string.c:1945`
(CRASH-104) and `zend_execute_API.c:730` (CRASH-058) are both labelled `cwe = CWE-843` in `index.csv`.
The CWE label is therefore not tracking the mechanism at all, and grouping by it would have merged
family E into family A and lost the read/write distinction the benchmark most wants to price.

Two of the five splits are not judgement calls, they are structural:

- **B is not "a missing if".** A guard is present at `zend_compile.c:1196` and it **passes**. It
  interrogates a different field in a different enum whose values collide with the intended one. Calling
  that the same mechanism as `zend_exceptions.c:551` (which has no guard at all) would erase the finding.
- **C is not "a missing if" either.** `array_unique` performs a type check and acts on its result; the
  check is simply weaker than the conclusion drawn from it, because `HASH_OF` accepts objects. The
  defect is a postcondition mismatch between two functions, not an omission at one site.

**Independent corroboration.** The blind invariant labelling — produced by analysts forbidden to read the
Rust port — reaches the same split without being asked to. It assigns `I4` to all 11 CWE-843 rows but
distinguishes the *obligations*: `I4/O1` ("must not read `value.str.val`/`.ht`/`.obj` from a zval whose
tag does not select that member", n=8) for the read family, and **`I4/O2`** ("a type established by an
earlier check or conversion must still hold at the point of use", n=3) for the CoW family. O1 and O2 are
described in `invariants-list.md` as *"separately-checkable halves"* of one invariant that *"fail in
opposite directions"*. That is the read/write split, arrived at independently.

**Recommendation.** Do not build one row per CWE-843 site. Build **one row per family**, and treat the
read/write/ordering trichotomy as the axis's primary structure. Family A can legitimately be a single row
with its A2/A3 variants folded in.

---

## 4. Rejected rows, and the C-side reason for each

No row was rejected for any Rust-side, Verus-side, Miri-side or cost-gradient reason. The only
disqualifier I applied is the one the brief permits: **C-side mechanism duplication**. Everything else
below is "belongs to another agent's axis", which is a routing decision, not a kill.

| row | c_file_line | C-side reason |
|---|---|---|
| CRASH-021 | `ext/standard/datetime.c:1033` | **Not this axis.** strftime with an out-of-range `tm` — the defect is in libc, the kernel would have to model glibc's strftime. `self_containment` would be `modelled` with almost nothing of the original left. Also a plain value-range bug. |
| CRASH-028 | `Zend/zend_compile.c:3274` | **Duplicate of K/#14** — another compile-time emission of an opcode/operand combination the executor does not implement (by-ref foreach over a string offset). Same mechanism, different arm. Report as near-duplicate of #14. |
| CRASH-029 | `ext/standard/array.c:1046` | Unconditional `zval_ptr_dtor` on a retval that is NULL when the callback threw. Ordinary missing-NULL-check; the interesting half (re-entrancy with a pending exception) is the **temporal** agent's territory. |
| CRASH-034 | `Zend/zend_execute_API.c:738-739` | CWE-822, but the mechanism is *errcontext aliases a symbol table freed via a by-ref param* — a use-after-free. **Temporal axis.** Note it cites the same lines as CRASH-058; the type-side reading of those lines is candidate #7. |
| CRASH-053 | `Zend/zend_execute.c:1632` | Verified: `make_real_object(object_ptr)` at :1632 **is** followed by `object->type != IS_OBJECT` at :1635, so the naive "unchecked" reading is wrong. The real defect is in the string-offset container path inside the helper. Container-kind confusion, but too entangled with the compound-assign machinery to extract cleanly; the same idea appears cleanly in #14. |
| CRASH-061 | `Zend/zend_object_handlers.c:513` | Missing NULL check after `offsetUnset` bails. Ordinary null-deref, no tag involved. |
| CRASH-071 | `Zend/zend.c:955` | Backtrace copies args of a torn-down executor frame during shutdown. **Temporal (UAF).** |
| CRASH-082 | `ext/standard/array.c:4085` | Operator-precedence bug in an exception check, continues with a NULL result. A precedence typo, not a type mechanism. |
| CRASH-088 | `ext/standard/ftp_fopen_wrapper.c:649` | Missing NULL check on a pathless URL. Ordinary null-deref. |
| CRASH-096 | `ext/standard/streamsfuncs.c:1047` | Verified exactly as claimed: the guard is `if (max_length < 0)`, so **zero passes** and a zero-size read buffer becomes NULL. A genuine defect, but it is a **range-guard boundary** (`< 0` where `<= 0` was needed) — a value/spatial mechanism. **Route to the spatial agent.** |
| CRASH-126 | `ext/mbstring/mbstring.c:3219` | Optional arg defaults to NULL, passed unchecked to `strcasecmp`. Ordinary null-deref. `crashes_pristine_5_0_0 = False`. |
| CRASH-163 | `Zend/zend.c:1083` | User exception handler failure leaves `EG(exception)` NULL, then deref. Ordinary null-deref. `crashes_pristine_5_0_0 = False`. |
| LOGIC-003, 008, 014, 017, 018 | various | **All family E**, i.e. duplicates of candidate #7's mechanism (`is_ref` stamped on, or not separated from, a live shared slot). LOGIC-014 (`zend_builtin_functions.c:1420`) and LOGIC-017 (`zend_execute_API.c:608-610`) are the most distinct — they *force* `is_ref` on a caller's by-value slot rather than failing to separate — so if the manager wants a second write-side row, take LOGIC-017. Otherwise merge. |

**Note on the three `crashes_pristine_5_0_0 = False` rows on my axis** (CRASH-037, CRASH-126, CRASH-163):
this does not affect admission, because the bar asks whether the *extracted C kernel* exhibits the target
error, not whether PHP 5.0.0 happens to fault. CRASH-037 is carried inside candidate #1 as a
near-duplicate for exactly this reason — the mechanism is identical to CRASH-036, which does crash.

---

## 5. Citation audit — every claim checked against the pristine tarball

**Result: zero corrections needed. All 19 citations I checked resolved exactly as `index.csv` claims.**
This is worth recording given the brief's warning about a previous effort publishing patched-tree line
numbers.

| row | claimed | verified in pristine? |
|---|---|---|
| CRASH-036 | `zend_exceptions.c:551` | ✅ `zend_error_va(E_ERROR, Z_STRVAL_P(file), Z_LVAL_P(line), …)` |
| CRASH-037 | `zend_exceptions.c:339` | ✅ `zend_hash_apply_with_arguments(Z_ARRVAL_P(trace), …)` |
| CRASH-039 | `:293`, deref `:304` → `zend_hash.c:850` | ✅ all three; :850 is `nIndex = h & ht->nTableMask;` |
| CRASH-058 | `zend_execute_API.c:730-753` | ✅ the param loop, else-branch at :751-753 |
| CRASH-144 | `zend_compile.c:1196/1197` | ✅ exact |
| CRASH-079 | `array.c:2695`, deref `:2728`, fault `zend_hash.c:460` | ✅ all three; :2695 is `*return_value = **array;` |
| CRASH-085 | `basic_functions.c:2996`, `hash = *find_hash` at `:2977` | ✅ both |
| CRASH-093 | `info.c:640-651`, wild deref `:828` | ✅ both |
| CRASH-101 | `streamsfuncs.c:817` | ✅ exact |
| CRASH-104 | `string.c:1945-1949`, convert `:2077`, fault `:2124` | ✅ all three |
| CRASH-111 | `url.c:612` | ✅ exact |
| CRASH-153 | `zend_hash.c:489-497` (dtor :490, decrement :497), consumer `array.c:1893-1894` | ✅ all |
| CRASH-087 | `dir.c:395`, `globbuf` at `:369`, `GLOB_FLAGMASK` at `:164` | ✅ all three; :164 is `#define GLOB_FLAGMASK (~0)` |
| CRASH-143 | `zend_execute.c:3832` guard / `:3853` fault | ✅ both |
| CRASH-023 | `zend_execute.c:1769` | ✅ `NEXT_OPCODE();` on the error-zval path |
| CRASH-096 | `streamsfuncs.c:1047-1054` | ✅ `if (max_length < 0)` — zero passes, as the corpus says |
| CRASH-053 | `zend_execute.c:1632` | ✅ line is `make_real_object(object_ptr TSRMLS_CC);` — **but see §4**, the following line :1635 *does* check `object->type != IS_OBJECT`, so the root_cause_id string "unchecked" is misleading about *what* is unchecked |
| LOGIC-003 | `zend_object_handlers.c:296-300` | ✅ exact |
| LOGIC-007 | `zend.c:243` | ✅ `zval_dtor(expr_copy);` inside `if (EG(exception))` |

**Two rows carry corrections the corpus authors had already made themselves**, inside the `c_file_line`
field — I confirmed both notes are right rather than silently trusting them:

- **CRASH-093** — the field says *"Claimed '866-878' are the 2014 fix commit's line numbers, not
  php-5.0.0's."* Correct: in pristine 5.0.0 the unguarded `Z_STRVAL_PP` block is at **640-651**.
- **CRASH-061** — the field says *"claimed :479 is the post-fix-tree line number, at 5.0.0 the function
  starts at :506"*. I did not verify this one (row rejected in §4), so it is untested here.

**One phrasing I would flag rather than correct.** CRASH-053's `root_cause_id` is
`string-offset-compound-assign-obj-wild-object-ptr-deref` and the `c_file_line` note says
"unchecked `make_real_object(object_ptr)`". The call at :1632 is followed at :1635 by an explicit
`if (object->type != IS_OBJECT)`. The type check is present; what is unchecked is whether
`make_real_object` succeeded in *producing* a real object from a string-offset container. Not a line-number
error, but a reader following the `root_cause_id` alone would look for a missing type check and not find one.

---

## 6. Hotness — a null result, with the reason, because it is easy to misread

I could get **no frequency evidence for this axis from the 123-render ASan census**, and the manager
should not read that as "these paths are cold". Two independent reasons:

**(a) ASan does not detect this bug class at all.** Across all 2534 reports in
`.temp/san_tests/asan-logs/` the error kinds are:

```
   2450 heap-buffer-overflow
    490 heap-use-after-free
    189 use-after-poison
     70 global-buffer-overflow
```

Every one is spatial or temporal. There is **no type-confusion class and no uninitialised-read class** —
those need MSan, which was not run. So the census is structurally blind to my axis. That is itself the
most useful thing it says: **the type axis is under-represented in the corpus partly because the
instrumentation everyone runs cannot see it.** It is a good argument for the axis existing at all.

**(b) The census build is max-LTO, so the relevant functions are inlined out of the traces.** Grepping
for the functions my candidates live in returns zero across all 2534 logs:

```
0	zend_hash_del_key_or_index      0	zend_hash_find
0	zend_hash_get_current_data      0	convert_to_string
0	convert_to_long                 0	_zval_copy_ctor
```

That is not absence — `zend_hash_find` is among the hottest functions in PHP. The traces contain **no
`zend_hash_*` symbol whatsoever**, while the outer dispatch frames dominate:

```
  11445 in zend_do_fcall_common_helper
   5586 in zend_include_or_eval_handler
   4529 in zend_do_fcall_handler
   3199 in zend_execute_scripts
```

The build path is `.../build-5.0.0-mysql-webext-maxlto-asan/`. Small helpers are inlined into their
callers, so only large outlined functions survive symbolisation.

**What I can say about hotness, from the traces that do exist:** the executor dispatch loop is on every
request (11445 + 3199 frames), which supports candidate **#3** (`opdata-stride-early-exit`) directly, since
it lives in that loop. Candidate **#2** and **#14** sit on the compile path, reached by every `include` /
`eval` — `zend_include_or_eval_handler` appears 5586 times, which is independent evidence that path is
exercised constantly by ordinary WordPress/phpBB traffic.

---

## 7. Two-limb structure — which candidates produce which harm

The brief asked me to label the limb and flag anything producing both. Tally over the 15:

- **`wild-pointer-deref` only — 9:** #1(dominant), #4, #6, #9, #12, #13, #14, plus #3 and #10 whose
  consumer is an indirect *call* rather than a load.
- **`both` — 5:** #1 (attacker picks the limb by choosing the tag), **#2**, #5, #7, #11.
- **`silent-wrong-value` headline — 1:** #15 (`LOGIC-007`, corpus `vuln_class = uninit-read-silent`).

**#2 (`CRASH-144`) is the one to build first if only one gets built.** It produces both limbs *in a single
expression*: `.str.val` overlays `lval` and yields an attacker-chosen `char *` (wild deref), while
`.str.len` reads union bytes that writing `lval` never wrote (uninitialised read). The blind labelling
independently marks it **`I4` and `I3`** — the only row on my axis carrying both invariants — and the
uninitialised length is not incidental: it is what makes the guard *pass*, because the leftover parser-stack
value happened to be 7 == `sizeof("__clone")-1`. One row, both limbs, both invariants, a one-line
reproducer, and a crash before any output is emitted.

Also worth the manager's attention: **#12 (`CRASH-085`) is the only candidate whose confused pointer lands
on valid mapped memory** (a real heap `char *` reinterpreted as a `HashTable *`), so it corrupts rather
than faults. A crash-based oracle will score it clean; only the checksum-vs-`model.py` comparison catches
it. That is a useful row precisely because it breaks the "memory safety bug ⇒ crash" assumption.

---

## 8. Near-duplicate clusters, for the manager to arbitrate

Flagged rather than filtered, per the brief:

1. **#1 / #8 / #9** — all family A, all in the accessor. Distinctness rests on *where* the guard is
   missing (nowhere / after a presence check / on elements rather than the container). If breadth is
   short, build **#1** and fold the other two in as variants of one row.
2. **#4 / #13** — the same `HASH_OF` macro misused in opposite directions. **Recommend building as one
   row with two limbs**; the pairing is a better finding than either alone.
3. **#5 / #11** — the corpus merges both into `CRASH-153`. I split them because they are independently
   extractable and the blind labelling separates the obligations (I3/O3 vs I3/O1+O2). **Recommend keeping
   split**: #5 needs a re-entrancy window, #11 does not.
4. **#3 / #14** — both about the instruction stream being the confused value, but at different times
   (run-time PC stride vs compile-time emission). Keep both; together they cover both halves.
5. **CRASH-028 is a near-duplicate of #14** (see §4) and is not proposed separately.

---

## 9. Reproducibility

`tar` extraction of the 27 files I navigated with went to `.temp/php-mine/type/src/`, and the two
single-file scratch copies to `.temp/php-mine/type/.ze.c`. All are re-derivable from the tarball; per
`CLAUDE.md` Don't-rule 1 they are deleted, and this is the command that rebuilds them:

```
TB=/home/apt/repos_common/php-in-safe-rust/.app-tests/.temp/oracle/build-5.0.0/php-5.0.0.tar.gz
mkdir -p src && tar -xzf $TB -C src \
  php-5.0.0/Zend/{zend.h,zend_operators.h,zend_operators.c,zend_exceptions.c,zend_execute_API.c,\
zend_compile.c,zend_hash.c,zend_hash.h,zend_execute.c,zend.c,zend_object_handlers.c,\
zend_builtin_functions.c,zend_API.h,zend_types.h,zend_variables.c,zend_objects_API.h} \
  php-5.0.0/ext/standard/{array.c,basic_functions.c,info.c,streamsfuncs.c,string.c,url.c,dir.c,\
datetime.c,ftp_fopen_wrapper.c} \
  php-5.0.0/ext/mbstring/mbstring.c php-5.0.0/main/streams/streams.c
```

Nothing outside `.temp/php-mine/type/` was written, and no git command was run.
