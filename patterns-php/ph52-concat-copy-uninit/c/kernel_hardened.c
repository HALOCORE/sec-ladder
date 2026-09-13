/* ph52 rung R1h -- c/kernel.c WITH `7412202c43e7` APPLIED.  THE FIX.
 *
 * ============================================================================
 * ⚠⚠⚠ THE WHOLE DIFF AGAINST c/kernel.c IS ONE DELETED STATEMENT
 * ============================================================================
 *     -                ph52_zval_dtor(expr_copy);                    :243
 *
 * `7412202c43e7` -- Antony Dovgal, 2006-05-11, "no need to destroy the zval
 * here", `Zend/zend.c`, 1 file, 1 hunk, 0 insertions, 1 deletion.
 *
 * ⚠⚠ IT IS A HAND RECONSTRUCTION AND NOT A `patch -p1`, AND ../spec.md's
 * `provenance.fix_commit_note` ACCOUNTS FOR EVERY TOKEN THAT DIFFERS.  The
 * DELETED STATEMENT is byte-identical to 5.0.0's `:243` up to one tab of
 * indentation; what does not match is the commit's CONTEXT, because by 2006 the
 * enclosing arm had been restructured and uses two tokens that do not exist in
 * 5.0.0 at all (`STR_EMPTY_ALLOC()` and `E_RECOVERABLE_ERROR`).
 *
 * ⭐ AND THE DELETION IS COMPLETE.  `zend.c:243` is the ONLY line in
 * `zend_make_printable_zval` that READS `expr_copy` with no write to it earlier
 * on the same path: every other read (`:210`, `:214`, `:250`, `:254`, `:259`,
 * `:260`) reads a field written one or two lines above, `:253`/`:258` are
 * whole-struct writes, `:222` is inside the `#if 0` at `:220-228`, and `:263`
 * -- `expr_copy->type = IS_STRING` -- sits AFTER the switch, so every path that
 * leaves the function has written the tag.  Deleting `:243` therefore leaves no
 * path that tears down an unconstructed slot.  ../spec.md and ../NOTES.md §3.
 *
 * ⚠ `controls/r1h_onelinedel.py` IS THIS CLAIM AS A CHECK, not as prose: it
 * regenerates this file from c/kernel.c and refuses any other difference.
 *
 * Everything below is c/kernel.c, unchanged.
 *
 * ---------------------------------------------------------------------------
 *
 ph52 rung R1 -- PHP 5.0.0's `concat_function` / `zend_make_printable_zval`,
 * NARROWED.  THE BUG (corpus row LOGIC-007, CWE-457 / CWE-824).
 *
 * ============================================================================
 * PROVENANCE
 * ============================================================================
 *   php-5.0.0.tar.gz  sha256 5783e0c0ba94f165633a565fe73a83e59cf17b6880ef95fa
 *                            8f936dc6301d6919
 *   tar -xzOf <tarball> php-5.0.0/Zend/zend.c | sed -n '242,247p'
 *   plus pinned extra spans -- the bare declaration
 *   (Zend/zend_operators.c:1146-1153), the tag write (Zend/zend.c:258-265), the
 *   teardown (Zend/zend_variables.c:36-80), the caller's own teardown
 *   (Zend/zend_operators.c:1179-1194), `empty_string`/`STR_FREE`
 *   (Zend/zend_variables.c:29-33, Zend/zend.h:467-470) and the zval itself
 *   (Zend/zend.h:275-293, :386-399).  Every one of them is in ../spec.md's
 *   `provenance.extra_spans` with its own `extract_sha256`.
 *   Corpus row LOGIC-007.  Tier `narrowed`.
 *
 * ⚠ NO PROVENANCE CLAIM IN THIS COMMENT CAN AGE: `.memory-php/04-process.md`
 * law 14 -- a C kernel is in the MEASUREMENT digest, so a comment that carries a
 * claim which later has to be corrected cannot be corrected at re-gate price.
 * Everything arguable lives in ../spec.md; this header states the mechanism.
 *
 * ============================================================================
 * THE DEFECT, IN ONE LINE
 * ============================================================================
 * `zend_operators.c:1148` declares the slot and nothing initialises it:
 *
 *     zval op1_copy, op2_copy;
 *
 * and `zend.c:243`, on the `EG(exception)` early exit, tears it down:
 *
 *     if (EG(exception)) {                                              :242
 *         zval_dtor(expr_copy);                                         :243
 *
 * while the tag that decides which teardown arm runs is written ONCE, at `:263`,
 * AFTER the switch.  ⚠⚠ `value` FIRST, `type` LAST -- see ../kernel.h and
 * ../spec.md `idiom.required[0]`.
 *
 * ============================================================================
 * WHAT NARROWING REMOVED, AND WHY NONE OF IT IS A SEMANTIC CHANGE
 * ============================================================================
 * 1. `TSRMLS_DC` / `TSRMLS_CC` / `TSRMLS_FETCH()` (`zend_operators.c:1146`,
 *    `zend.c:219`, `zend_variables.c:49`).  Thread plumbing.
 *
 * 2. `EG(exception)` and the `cast_object` / `get` handler dispatch
 *    (`zend.c:229-241`).  PROJECTION: on the faulting path those handlers'
 *    only role is to have SET the exception, and what this row prices is the
 *    teardown at `:243`.  One attacker byte stands for the flag.
 *
 * 3. Three of the switch's eight arms are NOT lifted -- `:207-212`
 *    (IS_RESOURCE, needs `zend_list_delete`), `:253-256` (IS_DOUBLE, needs
 *    `zend_locale_sprintf_double`) and `:258-261` (the IS_LONG default, needs
 *    `convert_to_string`'s `smart_str`).  `.memory-php/01-extraction.md` F8:
 *    extraction cost is priced at the DEFECT site.  The five that ARE lifted
 *    span every shape the defect needs: an arm that writes nothing, an arm that
 *    writes `empty_string`, an arm that allocates, an arm that allocates
 *    conditionally, and the faulting arm itself.
 *
 * 4. `_zval_dtor`'s `IS_OBJECT` arm (`zend_variables.c:57-63`,
 *    `Z_OBJ_HT_P(zvalue)->del_ref`) and `IS_RESOURCE` arm (`:64-71`,
 *    `zend_list_delete`).  Both need machinery outside the defect site.
 *    ⚠ THE NUMBER THEY AFFECT IS PUBLISHED ANYWAY: `controls/tag_sweep.c`
 *    carries all SIX arms over the whole byte and reports the count, and
 *    ../NOTES.md §6 quotes it.
 *
 * 5. `zend_operators.c:1155-1178` -- the `use_copy1` + `result == op1` in-place
 *    arm.  The kernel always passes a result distinct from both operands, so
 *    `result == op1` is false on every call; the `else` arm at `:1179-1186` is
 *    the one that runs.  Both arms are DOWNSTREAM of the defect.
 *
 * 6. `zend_error` (`zend.c:226`, inside the `#if 0` at `:220-228`) and
 *    `CHECK_ZVAL_STRING_REL` (`zend_variables.c:44`, `zend_API.h:338-346`,
 *    which is EMPTY in a non-`ZEND_DEBUG` build -- the shipped one).
 *
 * ============================================================================
 * WHAT IS *NOT* CHANGED, AND MUST NOT BE
 * ============================================================================
 *   * `op1_copy` / `op2_copy` are BARE LOCALS of `ph52_concat_function`.  No
 *     `= {0}`, no `memset`, no `INIT_ZVAL`.  That is the row.
 *   * `expr_copy->type = PH52_IS_STRING` is the LAST write, after the switch.
 *   * `ph52_make_printable_zval` and `ph52_zval_dtor` are `noinline`.  Upstream
 *     they live in THREE separate translation units (`zend_operators.c`,
 *     `zend.c`, `zend_variables.c`) and PHP 5.0.0 is not built with LTO;
 *     `harness/build.py` compiles exactly three TUs and is frozen, so the
 *     boundary is spelled here instead.  ⚠ MEASURED, NOT STYLISTIC: without it
 *     2 of 16 {compiler x opt x mode x inline} cells answer differently,
 *     because at `-O3` the compiler may treat the unwritten tag as `undef` and
 *     fold the teardown away.  ../NOTES.md §4 and
 *     `controls/tu_boundary.sh` have the 16-cell table.
 *   * `STR_FREE` keeps its `ptr != empty_string` test (`zend.h:469`).  It is
 *     what makes three of the five arms leave the slot SAFE, and deleting it
 *     would make every repetition of the faulting arm a double free.
 *   * `type` is `unsigned char` and sits AFTER `value` and `refcount`.
 */

#include <stdint.h>
#include <stddef.h>

#include "kernel.h"

#define PHP_SHIM_IMPL /* exactly one TU defines the allocator state */
#include "emalloc_shim.h"

/* ---- window decoding.  Byte at a time, so no rung depends on alignment. --- */

static uint32_t ph52_rd32(const uint8_t *w, size_t o)
{
    return (uint32_t)w[o]
         | ((uint32_t)w[o + 1] << 8)
         | ((uint32_t)w[o + 2] << 16)
         | ((uint32_t)w[o + 3] << 24);
}

/* ---- Zend/zend_variables.c:29-33 `empty_string`.  ⚠ It is the ADDRESS that
 * `STR_FREE` compares, so this must be one object with static storage. */
static char ph52_empty_string[1] = "";

/* ============ VERBATIM: Zend/zend_variables.c:36-80, `_zval_dtor` ==========
 * The two arms that are NOT lifted (`IS_OBJECT`'s `del_ref`, `IS_RESOURCE`'s
 * `zend_list_delete`) fall to `default: return` here and are measured in
 * `controls/tag_sweep.c` instead.
 *
 * ⚠⚠ THIS IS THE TAG-DISPATCHED TEARDOWN AND THE TAG MAY BE ANYTHING.  The
 * pointer it releases is read out of the SAME uninitialised slot as the tag, so
 * the harm is a FREE and not merely a branch.  */
PH52_NOINLINE static void ph52_zval_dtor(ph52_zval *zvalue)
{
    if (zvalue->type == PH52_IS_LONG) {                           /* :38 */
        return;                                                   /* :39 */
    }
    switch (zvalue->type & ~PH52_IS_CONSTANT_INDEX) {             /* :41 */
        case PH52_IS_STRING:                                      /* :42 */
        case PH52_IS_CONSTANT:                                    /* :43 */
            /* :44 CHECK_ZVAL_STRING_REL -- empty in a non-debug build.
             * :45 STR_FREE_REL(zvalue->value.str.val), zend.h:470 */
            if (zvalue->value.str.val
                && zvalue->value.str.val != ph52_empty_string) {
                php_shim_efree(zvalue->value.str.val);
            }
            break;                                                /* :46 */
        case PH52_IS_ARRAY:                                       /* :47 */
        case PH52_IS_CONSTANT_ARRAY:                              /* :48 */
            /* :51-54, narrowed: the `ht != &EG(symbol_table)` test and
             * `zend_hash_destroy` are not lifted; `FREE_HASHTABLE(ht)` is
             * `efree(ht)` (zend_hash.h:344).  ⚠ THE SAME EIGHT BYTES AS THE
             * ARM ABOVE, READ AS A DIFFERENT TYPE. */
            if (zvalue->value.ht) {
                php_shim_efree(zvalue->value.ht);
            }
            break;                                                /* :56 */
        case PH52_IS_LONG:                                        /* :72 */
        case PH52_IS_DOUBLE:                                      /* :73 */
        case PH52_IS_BOOL:                                        /* :74 */
        case PH52_IS_NULL:                                        /* :75 */
        default:                                                  /* :76 */
            return;                                               /* :77 */
    }
}
/* ========== end: zend_variables.c:36-80 ================================== */

/* ============ NARROWED: Zend/zend.c:188-265 ================================
 * `zend_make_printable_zval`.  ⚠⚠ `expr_copy` IS THE CALLER'S BARE LOCAL.
 *
 * `arm` is `t % PH52_NARM` -- see ../kernel.h.  `aux` carries `expr`'s payload:
 * the boolean for `:200`, the object handle for `:250`, and the
 * `EG(exception)` flag for `:242`.  */
PH52_NOINLINE static void ph52_make_printable_zval(unsigned arm, unsigned aux,
                                                    ph52_zval *expr_copy,
                                                    int *use_copy, uint64_t *dig)
{
    /* :190-193 -- THE COMMON PATH.  `expr_copy` IS NEVER WRITTEN, which is the
     * whole reason the function's convention is *constructed only if
     * `*use_copy`* -- and the `:242` arm destructs it regardless. */
    if (arm == PH52_ARM_STRING) {
        *use_copy = 0;                                            /* :191 */
        *dig = (uint64_t)(unsigned char)('a' + aux % 26u);
        return;                                                   /* :192 */
    }
    *dig = 0;
    switch (arm) {                                                /* :194 */
        case PH52_ARM_NULL:                                       /* :195 */
            expr_copy->value.str.len = 0;                         /* :196 */
            expr_copy->value.str.val = ph52_empty_string;         /* :197 */
            break;                                                /* :198 */
        case PH52_ARM_BOOL:                                       /* :199 */
            if (aux & 1u) {                                       /* :200 */
                expr_copy->value.str.len = 1;                     /* :201 */
                expr_copy->value.str.val =
                    php_shim_estrndup("1", 1);                    /* :202 */
                *dig = PH52_DIG_ONE;
            } else {                                              /* :203 */
                expr_copy->value.str.len = 0;                     /* :204 */
                expr_copy->value.str.val = ph52_empty_string;     /* :205 */
            }
            break;                                                /* :206 */
        case PH52_ARM_ARRAY:                                      /* :213 */
            expr_copy->value.str.len = 5;                         /* :214  sizeof("Array")-1 */
            expr_copy->value.str.val =
                php_shim_estrndup("Array", (unsigned)expr_copy->value.str.len);
            *dig = PH52_DIG_ARRAY;
            break;                                                /* :216 */
        default: {                                                /* :217 PH52_ARM_OBJECT */
            /* :229-241 -- the handler dispatch is a PROJECTION onto one byte. */
            if (aux & 1u) {                                       /* :242 EG(exception) */
                /* ⭐ `7412202c43e7` DELETED THE LINE THAT WAS HERE:
                 *
                 *     ph52_zval_dtor(expr_copy);                  :243
                 *
                 * There is nothing to destroy: no path that reaches this arm has
                 * written `expr_copy`. */
                expr_copy->value.str.len = 0;                     /* :244 */
                expr_copy->value.str.val = ph52_empty_string;     /* :245 */
                break;                                            /* :246 */
            }
            expr_copy->value.str.val =
                (char *) php_shim_emalloc(PH52_OBJ_REQ);          /* :249 */
            /* :250 `sprintf(val, "Object id #%ld", (long)handle)`, narrowed to
             * the prefix plus the handle's decimal digits.  The REQUEST is the
             * fixed `:249` size; `len` is `sprintf`'s return. */
            /* :250  `sprintf(val, "Object id #%ld", handle)`, NARROWED: the
             * prefix is a constant digest and the handle's decimal digits are
             * folded by the same `do { } while (d)` `sprintf` itself runs, in the
             * same least-significant-first order. */
            /* ⚠ `aux` is ONE WINDOW BYTE -- the kernel's projection of
             * `zend_object_handle`, which `zend.h:265` makes an `unsigned int` --
             * so the handle has AT MOST THREE decimal digits and `sprintf`'s own
             * `do { } while (d)` is narrowed to an exhaustive three-way case.
             * Declared in ../spec.md; `controls/digest.py` drives all 256. */
            {
                unsigned nd;
                *dig = PH52_DIG_PREFIX;
                *dig = *dig * 131u + (uint64_t)(unsigned)('0' + aux % 10u);
                if (aux < 10u) {
                    nd = 1u;
                } else {
                    *dig = *dig * 131u
                         + (uint64_t)(unsigned)('0' + (aux / 10u) % 10u);
                    if (aux < 100u) {
                        nd = 2u;
                    } else {
                        *dig = *dig * 131u
                             + (uint64_t)(unsigned)('0' + aux / 100u);
                        nd = 3u;
                    }
                }
                expr_copy->value.str.len = (int)(PH52_OBJ_PREFIX_LEN + nd);
            }
            break;                                                /* :251 */
        }
    }
    expr_copy->type = PH52_IS_STRING;                             /* :263  TAG LAST */
    *use_copy = 1;                                                /* :264 */
}
/* ========== end narrowed: zend.c:188-265 ================================= */

/* ============ NARROWED: Zend/zend_operators.c:1146-1194 ====================
 * `concat_function`.  ⚠⚠ `:1148`'s DECLARATION IS THE ROW.
 *
 * ⚠ `noinline` so that the two slots really are locals of THIS frame at a fixed
 * offset, reused by the next call -- upstream's `concat_function` is a
 * `ZEND_API` function the executor calls from a different TU.  */
PH52_NOINLINE static void ph52_concat_function(ph52_zval *result,
                                               unsigned a1, unsigned x1,
                                               unsigned a2, unsigned x2,
                                               uint64_t *d1, uint64_t *d2)
{
    ph52_zval op1_copy, op2_copy;     /* :1148  ⛔ BARE.  THE DEFECT'S HOME. */
    int use_copy1, use_copy2;         /* :1149 */
    int n1, n2;

    ph52_make_printable_zval(a1, x1, &op1_copy, &use_copy1, d1);  /* :1152 */
    ph52_make_printable_zval(a2, x2, &op2_copy, &use_copy2, d2);  /* :1153 */

    /* :1155-1166 -- `op1 = &op1_copy` / `op2 = &op2_copy` when a copy was
     * made.  `result == op1` is false on every call this kernel makes, so
     * `:1159-1161` is not lifted. */
    if (use_copy1) {                                              /* :1155 */
        n1 = op1_copy.value.str.len;                              /* :1162 */
    } else {
        n1 = 1;                     /* the operand is one attacker byte */
    }
    if (use_copy2) {                                              /* :1164 */
        n2 = op2_copy.value.str.len;                              /* :1165 */
    } else {
        n2 = 1;
    }

    /* :1179-1186 -- the `result != op1` arm.  ⚠ `:1182-1184`'s THREE memcpy/
     * store lines are NOT lifted: the bytes they move are a function of the two
     * operand descriptors and `*d1` / `*d2` carry them into the u64 instead.
     * ../spec.md's divergence ledger has the argument. */
    result->value.str.len = n1 + n2;                              /* :1180 */
    result->value.str.val = (char *) php_shim_emalloc(
                                (size_t)result->value.str.len + 1);  /* :1181 */
    result->type = PH52_IS_STRING;                                /* :1185 */

    if (use_copy1) {                                              /* :1187 */
        ph52_zval_dtor(&op1_copy);                                /* :1188 */
    }
    if (use_copy2) {                                              /* :1190 */
        ph52_zval_dtor(&op2_copy);                                /* :1191 */
    }
}
/* ========== end narrowed: zend_operators.c:1146-1194 ===================== */

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t off, size_t len)
{
    const uint8_t *win = buf + off;
    uint64_t acc;
    unsigned n_ops, cap, o;

    php_shim_reset();                          /* PROTOCOL_PHP.md B1.3 */

    cap   = (unsigned)((len - PH52_OPS_OFF) / PH52_OP_BYTES);
    n_ops = (unsigned)(ph52_rd32(win, 0) % (uint32_t)(cap + 1u));
    acc   = (uint64_t)ph52_rd32(win, 4);

    for (o = 0; o < n_ops; o++) {
        size_t p = PH52_OPS_OFF + (size_t)PH52_OP_BYTES * o;
        unsigned a1 = (unsigned)win[p]     % (unsigned)PH52_NARM;
        unsigned x1 = (unsigned)win[p + 1];
        unsigned a2 = (unsigned)win[p + 2] % (unsigned)PH52_NARM;
        unsigned x2 = (unsigned)win[p + 3];
        ph52_zval result;
        uint64_t d1 = 0, d2 = 0;

        ph52_concat_function(&result, a1, x1, a2, x2, &d1, &d2);

        acc = acc * 31u + (uint64_t)(unsigned)result.value.str.len;
        acc = acc * 31u + d1;
        acc = acc * 31u + d2;

        /* The executor releases the temporary. */
        php_shim_efree(result.value.str.val);
    }

    /* PROTOCOL_PHP.md B1.2 -- the allocator's own behaviour lands in the u64 and
     * not only in a sanitizer.  ⭐⭐ ON THIS ROW IT IS WHAT CARRIES THE DEFECT:
     * `:243`'s teardown is observable ONLY through the allocator, so a slot
     * whose garbage tag frees moves `n_free`, `n_cache_hit` and
     * `bytes_mallocked` -- and the published u64 changes.  ph53's benign corpus
     * could not do that. */
    acc ^= php_shim_tally();
    return acc;
}
