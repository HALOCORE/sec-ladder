# VERIFY — pristine-tarball excerpts for the top 5 TYPE candidates

Every block below was produced by running the command shown, against the **pristine tarball only**:

```
TB=/home/apt/repos_common/php-in-safe-rust/.app-tests/.temp/oracle/build-5.0.0/php-5.0.0.tar.gz
sha256  5783e0c0ba94f165633a565fe73a83e59cf17b6880ef95fa8f936dc6301d6919   (verified this session)
bytes   5595997
```

`grep -n "" | sed -n 'A,Bp'` is used rather than plain `sed -n` so that the numbers printed on each line
are the file's own line numbers, making the citation self-checking. Every excerpt below was re-run
immediately before this file was written; the output is pasted unedited.

---

## Shared substrate — needed by candidates 1, 2 and 4

```
$ tar -xzOf $TB php-5.0.0/Zend/zend.h | grep -n "" | sed -n '275,293p'
275:typedef union _zvalue_value {
276:	long lval;					/* long value */
277:	double dval;				/* double value */
278:	struct {
279:		char *val;
280:		int len;
281:	} str;
282:	HashTable *ht;				/* hash table value */
283:	zend_object_value obj;
284:} zvalue_value;
285:
286:
287:struct _zval_struct {
288:	/* Variable information */
289:	zvalue_value value;		/* value */
290:	zend_uint refcount;
291:	zend_uchar type;	/* active type */
292:	zend_uchar is_ref;
293:};
```

```
$ tar -xzOf $TB php-5.0.0/Zend/zend_operators.h | grep -n "" | sed -n '237,239p;273,275p'
237:#define Z_STRVAL(zval)			(zval).value.str.val
238:#define Z_STRLEN(zval)			(zval).value.str.len
239:#define Z_ARRVAL(zval)			(zval).value.ht
273:#define Z_TYPE(zval)		(zval).type
274:#define Z_TYPE_P(zval_p)	Z_TYPE(*zval_p)
275:#define Z_TYPE_PP(zval_pp)	Z_TYPE(**zval_pp)
```

The payload accessors and the tag accessor are separate macros; **no payload accessor invokes `Z_TYPE`.**

---

## #1 `zval-union-read-no-tag-guard` — `Zend/zend_exceptions.c:551` (CRASH-036)

```
$ tar -xzOf $TB php-5.0.0/Zend/zend_exceptions.c | grep -n "" | sed -n '547,551p'
547:		str = zend_read_property(default_exception_ce, exception, "string", sizeof("string")-1, 1 TSRMLS_CC);
548:		file = zend_read_property(default_exception_ce, exception, "file", sizeof("file")-1, 1 TSRMLS_CC);
549:		line = zend_read_property(default_exception_ce, exception, "line", sizeof("line")-1, 1 TSRMLS_CC);
550:
551:		zend_error_va(E_ERROR, Z_STRVAL_P(file), Z_LVAL_P(line), "Uncaught %s\n  thrown", Z_STRVAL_P(str));
```

Three user-settable properties are read at :547-549 and consumed at :551 as `char *`, `long`, `char *`.
No `Z_TYPE_P(...) == IS_STRING` appears anywhere between the read and the use. Reproducer
(`input/crash/CRASH-036.php`) sets `$this->file = 0x41414141;` in an `Exception` subclass, so **the
attacker chooses the dereferenced address outright**.

---

## #2 `wrong-tag-namespace-const-guard` — `Zend/zend_compile.c:1196-1197` (CRASH-144)

```
$ tar -xzOf $TB php-5.0.0/Zend/zend_compile.c | grep -n "" | sed -n '1193,1199p'
1193:	last_op_number = get_next_op_number(CG(active_op_array))-1;
1194:	last_op = &CG(active_op_array)->opcodes[last_op_number];
1195:
1196:	if ((last_op->op2.op_type == IS_CONST) && (last_op->op2.u.constant.value.str.len == sizeof(ZEND_CLONE_FUNC_NAME)-1)
1197:		&& !zend_binary_strcasecmp(last_op->op2.u.constant.value.str.val, last_op->op2.u.constant.value.str.len, ZEND_CLONE_FUNC_NAME, sizeof(ZEND_CLONE_FUNC_NAME)-1)) {
1198:		zend_error(E_COMPILE_ERROR, "Cannot call __clone() method on objects - use 'clone $obj' instead");
1199:	}
```

The guard tests `op2.op_type` — the **znode operand-kind** tag — and then reads `op2.u.constant.value.str.*`,
the **zval** union. The two tags are unrelated *and their values collide*:

```
$ tar -xzOf $TB php-5.0.0/Zend/zend_compile.h | grep -n "" | sed -n '285,288p'
285:#define IS_CONST	(1<<0)
286:#define IS_TMP_VAR	(1<<1)
287:#define IS_VAR		(1<<2)
288:#define IS_UNUSED	(1<<3)	/* Unused variable */
```

```
$ tar -xzOf $TB php-5.0.0/Zend/zend.h | grep -n "" | sed -n '387,392p'
387:#define IS_NULL		0
388:#define IS_LONG		1
389:#define IS_DOUBLE	2
390:#define IS_STRING	3
391:#define IS_ARRAY	4
392:#define IS_OBJECT	5
```

`IS_CONST == 1 == IS_LONG`; `IS_VAR == 4 == IS_ARRAY`; `IS_UNUSED == 8 == IS_CONSTANT`.
Reproducer is one line: `$abcdefg->{1}();`. `.str.val` overlays `lval` and hands the literal `1` to
`zend_binary_strcasecmp` as a `char *`; `.str.len` reads union bytes the `lval` write never touched, and the
stale `7` is what lets the length test at :1196 pass. **Both harm limbs in one expression.**

---

## #3 `opdata-stride-early-exit` — `Zend/zend_execute.c:1769` (CRASH-023)

The two-word instruction form is set up here; `increment_opline = 1` records that the PC must advance by 2:

```
$ tar -xzOf $TB php-5.0.0/Zend/zend_execute.c | grep -n "" | sed -n '1742,1749p'
1742:					zend_op *op_data = opline+1;
1743:
1744:					zend_fetch_dimension_address(&op_data->op2, &opline->op1, &opline->op2, EX(Ts), BP_VAR_RW TSRMLS_CC);
1745:
1746:					value = get_zval_ptr(&op_data->op1, EX(Ts), &EG(free_op1), BP_VAR_R);
1747:					var_ptr = get_zval_ptr_ptr(&op_data->op2, EX(Ts), BP_VAR_RW);
1748:					EG(free_op2) = 0;
1749:					increment_opline = 1;
```

The **early exit ignores `increment_opline`** and advances by one:

```
$ tar -xzOf $TB php-5.0.0/Zend/zend_execute.c | grep -n "" | sed -n '1761,1770p'
1761:	if (!var_ptr) {
1762:		zend_error(E_ERROR, "Cannot use assign-op operators with overloaded objects nor string offsets");
1763:	}
1764:
1765:	if (*var_ptr == EG(error_zval_ptr)) {
1766:		EX_T(opline->result.u.var).var.ptr_ptr = &EG(uninitialized_zval_ptr);
1767:		SELECTIVE_PZVAL_LOCK(*EX_T(opline->result.u.var).var.ptr_ptr, &opline->result);
1768:		AI_USE_PTR(EX_T(opline->result.u.var).var);
1769:		NEXT_OPCODE();
1770:	}
```

The **normal exit honours it** — this contrast is the proof that :1769 is wrong, not merely different:

```
$ tar -xzOf $TB php-5.0.0/Zend/zend_execute.c | grep -n "" | sed -n '1792,1795p'
1792:	if (increment_opline) {
1793:		INC_OPCODE();
1794:	}
1795:	NEXT_OPCODE();
```

`NEXT_OPCODE` is a stride of exactly one, and the trailing data word's handler is **explicitly NULL**:

```
$ tar -xzOf $TB php-5.0.0/Zend/zend_execute.c | grep -n "" | sed -n '1317,1320p'
1317:#define NEXT_OPCODE()		\
1318:	CHECK_SYMBOL_TABLES()	\
1319:	EX(opline)++;			\
1320:	return 0; /* CHECK_ME */

$ tar -xzOf $TB php-5.0.0/Zend/zend_execute.c | grep -n "" | sed -n '4427p'
4427:	zend_opcode_handlers[ZEND_OP_DATA] = NULL;
```

So the executor fetches the operand-payload word as an instruction and makes an **indirect call through a
NULL function pointer**. This is the candidate whose original C shape is already the pinned kernel shape.

---

## #4 `hash-of-launders-object-as-array` — `ext/standard/array.c:2695` (CRASH-079)

The laundering helper accepts arrays **and objects**:

```
$ tar -xzOf $TB php-5.0.0/Zend/zend_API.h | grep -n "" | sed -n '519p'
519:#define HASH_OF(p) ((p)->type==IS_ARRAY ? (p)->value.ht : (((p)->type==IS_OBJECT ? Z_OBJ_HT_P(p)->get_properties((p) TSRMLS_CC) : NULL)))
```

`array_unique` uses it as its type check, then struct-copies the zval **whole — tag included**:

```
$ tar -xzOf $TB php-5.0.0/ext/standard/array.c | grep -n "" | sed -n '2688,2696p'
2688:	target_hash = HASH_OF(*array);
2689:	if (!target_hash) {
2690:		php_error_docref(NULL TSRMLS_CC, E_WARNING, "The argument should be an array");
2691:		RETURN_FALSE;
2692:	}
2693:
2694:	/* copy the argument array */
2695:	*return_value = **array;
2696:	zval_copy_ctor(return_value);
```

and later reads that still-`IS_OBJECT` zval through the **array** accessor:

```
$ tar -xzOf $TB php-5.0.0/ext/standard/array.c | grep -n "" | sed -n '2727,2731p'
2727:			if (p->nKeyLength) {
2728:				zend_hash_del(Z_ARRVAL_P(return_value), p->arKey, p->nKeyLength);
2729:			} else {
2730:				zend_hash_index_del(Z_ARRVAL_P(return_value), p->h);
2731:			}
```

`Z_ARRVAL_P` reads `.value.ht`, but the live union member is `.value.obj`
(`{zend_object_handle handle; zend_object_handlers *handlers;}`, `zend.h:270-273`), so the small integer
object handle becomes the `HashTable *`. Fault is at `zend_hash.c:460`, `nIndex = h & ht->nTableMask;`.
Reproducer: `array_unique(new C)`.

---

## #5 `stale-count-reentrant-window` — `Zend/zend_hash.c:489-497` (CRASH-153)

The bucket surgery is bracketed by interrupt blocking, but the count decrement is placed **outside** it,
*after* an arbitrary userland destructor has been allowed to run:

```
$ tar -xzOf $TB php-5.0.0/Zend/zend_hash.c | grep -n "" | sed -n '466p'
466:			HANDLE_BLOCK_INTERRUPTIONS();

$ tar -xzOf $TB php-5.0.0/Zend/zend_hash.c | grep -n "" | sed -n '486,498p'
486:			if (ht->pInternalPointer == p) {
487:				ht->pInternalPointer = p->pListNext;
488:			}
489:			if (ht->pDestructor) {
490:				ht->pDestructor(p->pData);
491:			}
492:			if (!p->pDataPtr) {
493:				pefree(p->pData, ht->persistent);
494:			}
495:			pefree(p, ht->persistent);
496:			HANDLE_UNBLOCK_INTERRUPTIONS();
497:			ht->nNumOfElements--;
498:			return SUCCESS;
```

Re-entrant code running inside `pDestructor` at :490 therefore sees `nNumOfElements` one too high over an
already-unlinked list. The consumer gates on exactly that count and then **discards the accessor's status**
(this is the separately-proposed candidate #11):

```
$ tar -xzOf $TB php-5.0.0/ext/standard/array.c | grep -n "" | sed -n '1884,1894p'
1884:	if (zend_hash_num_elements(Z_ARRVAL_PP(stack)) == 0) {
1885:		return;
1886:	}
1887:		
1888:	/* Get the first or last value and copy it into the return value */
1889:	if (off_the_end)
1890:		zend_hash_internal_pointer_end(Z_ARRVAL_PP(stack));
1891:	else
1892:		zend_hash_internal_pointer_reset(Z_ARRVAL_PP(stack));
1893:	zend_hash_get_current_data(Z_ARRVAL_PP(stack), (void **)&val);
1894:	*return_value = **val;
```

`val` is a bare automatic with no initialiser, so when the accessor at :1893 returns FAILURE without
writing its out-parameter, :1894 dereferences it twice:

```
$ tar -xzOf $TB php-5.0.0/ext/standard/array.c | grep -n "" | sed -n '1866,1870p'
1866:static void _phpi_pop(INTERNAL_FUNCTION_PARAMETERS, int off_the_end)
1867:{
1868:	zval **stack,			/* Input stack */
1869:	     **val;			/* Value to be popped */
1870:	char *key = NULL;
```

Reproducer: a class whose `__destruct` calls `array_pop($GLOBALS['a'])`, then `unset($a[0])`.

---

## One-command re-derivation of everything above

```
TB=/home/apt/repos_common/php-in-safe-rust/.app-tests/.temp/oracle/build-5.0.0/php-5.0.0.tar.gz
r(){ echo "--- $1 $2"; tar -xzOf $TB "php-5.0.0/$1" | grep -n "" | sed -n "$2"; }
r Zend/zend.h '275,293p;387,392p'; r Zend/zend_operators.h '237,239p;273,275p'
r Zend/zend_exceptions.c '547,551p'; r Zend/zend_compile.c '1193,1199p'; r Zend/zend_compile.h '285,288p'
r Zend/zend_execute.c '1742,1749p;1761,1770p;1792,1795p;1317,1320p;4427p'
r Zend/zend_API.h '519p'; r ext/standard/array.c '2688,2696p;2727,2731p;1866,1870p;1884,1894p'
r Zend/zend_hash.c '466p;486,498p'
```
