#ifndef PH52_KERNEL_H
#define PH52_KERNEL_H

#include <stddef.h>
#include <stdint.h>

#include "driver.h" /* SLB_NOINLINE */

/* ph52: PHP 5.0.0's `concat_function` hands `zend_make_printable_zval` a BARE
 * STACK LOCAL, and one early-exit arm DESTRUCTS it before anything has
 * constructed it -- driven over a window of concat operations, folded into a
 * u64.
 *
 *   window = [u32 n_ops_w][u32 fold_w]
 *            [ n_ops x { u8 t1; u8 a1; u8 t2; u8 a2 } ]
 *
 *   cap    = (len - PH52_OPS_OFF) / 4
 *   n_ops  = n_ops_w % (cap + 1)
 *   acc    = fold_w                      (both head words reach the u64)
 *
 *   per op   ph52_concat_function(&result, &op1, &op2)   zend_operators.c:1146
 *              -> ph52_make_printable_zval(op1, &op1_copy, &use_copy1)  :1152
 *              -> ph52_make_printable_zval(op2, &op2_copy, &use_copy2)  :1153
 *              -> the result concat                                :1180-1185
 *              -> zval_dtor(op1) / zval_dtor(op2)                  :1187-1192
 *
 * Contract in ../spec.md.  Two C rungs share this declaration:
 *
 *   c/kernel.c            R1  -- PHP 5.0.0, narrowed.  THE BUG (LOGIC-007).
 *   c/kernel_hardened.c   R1h -- the same file with `7412202c43e7`'s ONE DELETED
 *                                LINE applied: `zval_dtor(expr_copy);` at
 *                                `Zend/zend.c:243` is gone (Antony Dovgal,
 *                                2006-05-11, "no need to destroy the zval
 *                                here").  ⚠ A HAND RECONSTRUCTION, not a
 *                                `patch -p1`: ../spec.md's
 *                                `provenance.fix_commit_note` accounts for
 *                                every token that differs.
 *
 * ============================================================================
 * ⚠⚠⚠ THE DEFECT IS AN UNINITIALISED **TAG**, AND THE TAG IS WRITTEN **LAST**
 * ============================================================================
 * `Zend/zend_operators.c:1148`:
 *
 *     zval op1_copy, op2_copy;            <- no `= {0}`, no INIT_ZVAL, no memset
 *
 * `Zend/zend.c:188-265` writes `expr_copy->value.str.*` on every arm and
 * `expr_copy->type` EXACTLY ONCE, at `:263`, AFTER the switch -- and the arm at
 * `:242-247` tears the slot down first:
 *
 *     if (EG(exception)) {                                              :242
 *         zval_dtor(expr_copy);                                         :243
 *         expr_copy->value.str.len = 0;                                 :244
 *         expr_copy->value.str.val = empty_string;                      :245
 *         break;                                                        :246
 *     }                                                                 :247
 *
 * `_zval_dtor` (`Zend/zend_variables.c:36-80`) switches on
 * `zvalue->type & ~IS_CONSTANT_INDEX` and FREES A POINTER READ OUT OF THE SAME
 * UNINITIALISED SLOT.  ⚠ On the COMMON path (`:190-193`, `expr` already a
 * string) `expr_copy` is never written at all, so the function's own convention
 * is *constructed only if `*use_copy`* -- and this arm destructs it anyway.
 *
 * ⚠⚠ THE WRITE ORDER IS LOAD-BEARING AND IS PINNED.  A kernel that writes the
 * tag early -- the tidy ordering -- deletes the defect while keeping every line
 * that looks load-bearing.  `value` first, `type` last.  ../spec.md
 * `idiom.required[0]`.
 *
 * ============================================================================
 * ⚠⚠⚠ AND THE SLOT IS ON THE **STACK**, SO THE TRIGGER IS A CALL HISTORY
 * ============================================================================
 * A clean stack slot is usually 0 = `IS_NULL`, and `_zval_dtor` has
 * `case IS_NULL: default: return;` (`zend_variables.c:75-77`), so the defect is
 * SILENT -- which is why the corpus records `uninit-read-silent` and no crash.
 * It fires when a PRIOR call at the same depth left a freeing tag there:
 *
 *   op k    a converting arm (`:202`, `:214`, `:249`) puts a real `emalloc`
 *           pointer in `value.str.val` and `:263` writes `type = IS_STRING`;
 *           `:1188 zval_dtor(op1)` then FREES that pointer.
 *   op k+1  the `:242` arm reads `IS_STRING` + the dangling pointer and
 *           `:243` frees it again  ->  DOUBLE FREE.
 *
 * The arms that leave the slot SAFE are the ones whose `value.str.val` is
 * `empty_string`, because `zend.h:469 STR_FREE(ptr)` is
 * `if (ptr && ptr != empty_string) { efree(ptr); }`:  `:195-197` (IS_NULL),
 * `:204-205` (IS_BOOL false) and `:244-245` (the faulting arm itself, which is
 * therefore SELF-DEFUSING on repetition).
 *
 * ⚠ THE MEASURED CORPUS IS CONSTRAINED ACCORDINGLY and `inputs/gen.py` asserts
 * it from the bytes it wrote: no op may present a CONVERTING arm immediately
 * before a FAULTING arm on the same side, and no window's op 0 may be a
 * faulting arm on either side (its predecessor is the previous window's last
 * op, or -- on the program's first call -- the C runtime's own leftovers).
 * `inputs/adversarial-dblfree.bin` is the blob that breaks the first rule.
 *
 * The kernel does NOT take `buf_len`.  The caller guarantees
 * `off + len <= buf_len` and `PH52_OPS_OFF <= len`; that is the structural
 * precondition every rung shares and no rung checks (R5 proves it at the call
 * site instead).  Every byte of the window is attacker data. */
SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t off, size_t len);

/* ⚠⚠ UNCONDITIONAL `noinline`, and it is NOT `common/driver.h`'s
 * `SLB_NOINLINE`, which is empty unless `SLB_ISOLATED` is defined.  Upstream
 * `concat_function` (`zend_operators.c`), `zend_make_printable_zval` (`zend.c`)
 * and `_zval_dtor` (`zend_variables.c`) are THREE separate translation units and
 * PHP 5.0.0 links without LTO; `harness/build.py` compiles exactly three TUs and
 * is frozen, so the boundary is spelled here.  ⚠ MEASURED: without it, 2 of the
 * 16 {gcc,clang} x {O0,O3} x {isolated,whole} x {noinline,inlinable} cells
 * answer DIFFERENTLY, because at `-O3` a compiler that can see the unwritten tag
 * may treat it as `undef` and fold the teardown away.  ../NOTES.md §4. */
#define PH52_NOINLINE __attribute__((noinline))

/* ---- the window's shape.  Identical in all six rungs and in model.py. ---- */

#define PH52_HDR_BYTES 8                     /* two u32 head words */
#define PH52_OPS_OFF   PH52_HDR_BYTES        /* 8 */
#define PH52_OP_BYTES  4                     /* u8 t1, u8 a1, u8 t2, u8 a2 */

/* The five lifted arms of `zend_make_printable_zval`'s switch, selected by
 * `t % PH52_NARM`.  ⚠ These are SELECTORS and not `zend.h`'s IS_* codes: three
 * of upstream's eight arms are not lifted (`:207-212` IS_RESOURCE needs
 * `zend_list`, `:253-256` IS_DOUBLE needs `zend_locale_sprintf_double`,
 * `:258-261` the IS_LONG default needs `convert_to_string`'s `smart_str`), and
 * ../spec.md's `provenance.divergences` itemises all three. */
#define PH52_ARM_STRING 0   /* :190-193  EARLY RETURN -- expr_copy UNTOUCHED */
#define PH52_ARM_NULL   1   /* :194-197  len = 0, val = empty_string         */
#define PH52_ARM_BOOL   2   /* :198-206  "1" (allocates) or empty_string     */
#define PH52_ARM_ARRAY  3   /* :213-216  estrndup("Array", 5)   ALLOCATES    */
#define PH52_ARM_OBJECT 4   /* :217-252  the faulting arm, or "Object id #N" */
#define PH52_NARM       5

/* `sizeof("Object id #")-1 + MAX_LENGTH_OF_LONG` -- `zend.c:249` with
 * `zend_operators.h:37 MAX_LENGTH_OF_LONG 20`.  The REQUEST is this fixed size;
 * the recorded `len` is `sprintf`'s return value, which is shorter. */
#define PH52_OBJ_PREFIX_LEN 11               /* sizeof("Object id #") - 1 */
#define PH52_MAX_LENGTH_OF_LONG 20           /* zend_operators.h:37 */
#define PH52_OBJ_REQ (PH52_OBJ_PREFIX_LEN + PH52_MAX_LENGTH_OF_LONG)

/* ⚠⚠ THE CONTENT DIGEST, AND IT IS INSTRUMENTATION -- not a field of `zval`.
 *
 * `zend.c`'s converting arms write bytes into `expr_copy->value.str.val` and
 * `zend_operators.c:1182-1183` then `memcpy`s both into the result.  THOSE FIVE
 * STORE LINES ARE NOT LIFTED (`:250`, `:1182`, `:1183`, `:1184`, and `:214`'s
 * `estrndup` payload): the bytes they move are a pure function of the two
 * operand descriptors, so the kernel allocates exactly the blocks upstream
 * allocates and folds the SAME CONTENT as a 131-digest instead of materialising
 * it.  ⭐ THE REASON IS `ph64`'s LESSON ONE LEVEL OVER: keeping the stores would
 * put a `Seq<u8>` concatenation in R5's postcondition and would make the
 * cross-language column a comparison of `rep movsb` against a Rust `while` loop
 * -- a memcpy comparison, not a safety comparison.  ../spec.md's divergence
 * ledger carries the argument and `controls/digest.py` checks the constants
 * against the literals they stand for.
 *
 * Each is `fold131(s) = sum over bytes of (h = h*131 + byte)`, h0 = 0, in
 * `uint64_t`, i.e. mod 2^64.  The object handle's decimal digits are folded by a
 * loop, in LEAST-SIGNIFICANT-FIRST order, which is the order `sprintf`'s own
 * `do { } while (d)` produces them in. */
#define PH52_DIG_PREFIX 18136473400329561039ull   /* fold131("Object id #") */
#define PH52_DIG_ARRAY  19400746421ull            /* fold131("Array")       */
#define PH52_DIG_ONE    49ull                     /* fold131("1")           */

/* `Zend/zend.h:387-399`, verbatim. */
#define PH52_IS_NULL           0
#define PH52_IS_LONG           1
#define PH52_IS_DOUBLE         2
#define PH52_IS_STRING         3
#define PH52_IS_ARRAY          4
#define PH52_IS_OBJECT         5
#define PH52_IS_BOOL           6
#define PH52_IS_RESOURCE       7
#define PH52_IS_CONSTANT       8
#define PH52_IS_CONSTANT_ARRAY 9
#define PH52_IS_CONSTANT_INDEX 0x80

/* `Zend/zend.h:275-284 union _zvalue_value`, minus `obj` (which needs
 * `zend_object_value` and `zend_object_handlers`) -- one deletion-ledger line.
 * `ht` IS kept, and deliberately: the `IS_ARRAY` teardown arm reads the SAME
 * EIGHT BYTES as a `HashTable *` where the `IS_STRING` arm reads them as a
 * `char *`, and that type confusion through an unwritten tag is half of what
 * the row is about. */
typedef union ph52_value {
    long                 lval;         /* zend.h:276 */
    double               dval;         /* zend.h:277 */
    struct {
        char *val;
        int   len;
    }                    str;          /* zend.h:278-281 */
    struct ph52_hash    *ht;           /* zend.h:282 */
} ph52_value;

/* `HashTable` narrowed to the one field a teardown reads (`zend_hash.h:61`,
 * `nNumOfElements`).  `ALLOC_HASHTABLE`/`FREE_HASHTABLE` are
 * `emalloc(sizeof(HashTable))` / `efree(ht)` (`zend_hash.h:340-344`). */
typedef struct ph52_hash {
    uint64_t nNumOfElements;
} ph52_hash;

/* `Zend/zend.h:287-293 struct _zval_struct`, in upstream's field order and with
 * upstream's types (`zend_uint` is `unsigned int`, `zend_uchar` is
 * `unsigned char`, `zend_types.h:26-27`).  ⚠ THE FIELD ORDER IS NOT COSMETIC:
 * `type` sits AFTER `value` and `refcount`, so the byte the defect reads is at
 * offset 20 of a 24-byte object and an extraction that reordered the struct
 * would move which of the caller's leftovers it lands on. */
typedef struct ph52_zval {
    ph52_value    value;       /* zend.h:289 */
    unsigned int  refcount;    /* zend.h:290 */
    unsigned char type;        /* zend.h:291   <-- THE UNCONSTRUCTED BYTE */
    unsigned char is_ref;      /* zend.h:292 */
} ph52_zval;

#endif /* PH52_KERNEL_H */
