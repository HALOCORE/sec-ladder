/* ph52 control -- DELIVERABLE #0: IS THE STACK SLOT REUSED, AND IS THE DEFECT
 * DETERMINISTIC ACROSS THE BUILD MATRIX?
 *
 *   python3 controls/d0_stack.py            # builds and runs all 16 cells
 *
 * ⚠⚠⚠ **WHY A SEPARATE PROBE AND NOT THE KERNEL.** ph52's uninitialised datum is
 * a STACK slot, and every mechanism this tree has for uninitialised memory is an
 * ALLOCATOR shim. So before any rung existed the row had to settle whether
 * `Zend/zend.c:243` reads anything REPRODUCIBLE at all -- on `{gcc, clang}` x
 * `{-O0, -O3}` x `{isolated, whole}` and, because `harness/build.py` compiles
 * exactly three TUs where upstream has three SEPARATE ONES, x `{callee noinline,
 * callee inlinable}`.
 *
 * This is a faithful miniature of the shape, NOT the kernel: one `concat_function`
 * with one bare `zval op1_copy;`, `zend_make_printable_zval` with the IS_ARRAY and
 * IS_OBJECT arms, and `_zval_dtor` with the real `type == IS_LONG` early return,
 * the real `switch (type & ~IS_CONSTANT_INDEX)` and the real
 * `STR_FREE(ptr != empty_string)` test. It links `common-php/emalloc_shim.h`,
 * which is what the measured binaries do.
 *
 * ⚠ IT CARRIES NO INSTRUMENTATION COUNTER, DELIBERATELY. The first draft printed a
 * per-site call count, and that counter is itself an observable side effect -- it
 * stopped `clang -O3` from folding the teardown away and made two cells look
 * identical to the other fourteen. `controls/d0_stack.py` §N3 is that negative.
 *
 * What the 16 cells measure, and ../NOTES.md §4 reports:
 *   * the slot ADDRESS is the same on every call in every cell (the offset is
 *     exact, at both opt levels, in both modes, on both compilers);
 *   * with `NOINL` the u64 is IDENTICAL in all 16;
 *   * WITHOUT it, 2 of 16 differ -- `gcc -O3 isolated` and `clang -O3 whole` --
 *     because a compiler that can see the unwritten tag may treat it as `undef`
 *     and fold `:243` away.  ▶ THAT is why `c/kernel.h` defines PH52_NOINLINE.
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#define PHP_SHIM_IMPL
#include "emalloc_shim.h"

#include "d0_noinl.h"

#define IS_LONG 1
#define IS_STRING 3
#define IS_ARRAY 4
#define IS_OBJECT 5
#define IS_RESOURCE 7
#define IS_CONSTANT 8
#define IS_CONSTANT_ARRAY 9
#define IS_CONSTANT_INDEX 0x80

typedef union ph_value { long lval; double dval; struct { char *val; int len; } str; } ph_value;
typedef struct ph_zval { ph_value value; unsigned int refcount;
                         unsigned char type; unsigned char is_ref; } ph_zval;

static char ph_empty_string[1] = "";
unsigned long n243 = 0, n1188 = 0, nfree = 0;
unsigned long s243_tag[32]; void *s243_ptr[32]; void *s243_addr[32];
int site = 0;

NOINL static void ph_zval_dtor(ph_zval *zvalue)
{
    if (zvalue->type == IS_LONG) return;
    switch (zvalue->type & ~IS_CONSTANT_INDEX) {
        case IS_STRING: case IS_CONSTANT:
            if (zvalue->value.str.val && zvalue->value.str.val != ph_empty_string) {
                php_shim_efree(zvalue->value.str.val);
            }
            break;
        case IS_ARRAY: case IS_CONSTANT_ARRAY:
        case IS_OBJECT: case IS_RESOURCE:
            php_shim_efree(zvalue->value.str.val);
            break;
        default: return;
    }
}

NOINL static void ph_make_printable_zval(ph_zval *expr, ph_zval *expr_copy, int *use_copy)
{
    if (expr->type == IS_STRING) { *use_copy = 0; return; }
    *use_copy = 1;
    switch (expr->type) {
        case IS_ARRAY:
            expr_copy->value.str.len = 5;
            expr_copy->value.str.val = php_shim_estrndup("Array", 5);
            break;
        case IS_OBJECT:
            if (expr->value.lval) {
                ph_zval_dtor(expr_copy);   /* :243 */
                expr_copy->value.str.len = 0;
                expr_copy->value.str.val = ph_empty_string;
                break;
            }
            expr_copy->value.str.val = (char *)php_shim_emalloc(32);
            expr_copy->value.str.len = sprintf(expr_copy->value.str.val,
                                               "Object id #%ld", expr->value.lval);
            break;
        default:
            expr_copy->value.str.len = 1;
            expr_copy->value.str.val = php_shim_estrndup("x", 1);
            break;
    }
    expr_copy->type = IS_STRING;
    *use_copy = 1;
}

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t off, size_t len)
{
    ph_zval op1_copy; int use_copy1; ph_zval expr; uint64_t acc = 0;
    expr.type = buf[off];
    expr.value.lval = buf[off + 1];
    (void)len;
    ph_make_printable_zval(&expr, &op1_copy, &use_copy1);
    if (use_copy1) {
        acc += (uint64_t)(unsigned)op1_copy.value.str.len;
        acc = acc * 31 + op1_copy.type;
        ph_zval_dtor(&op1_copy);   /* :1188 */
    }
    return acc;
}

int main(int argc, char **argv)
{
    uint8_t blob[4];
    uint64_t acc = 0;
    unsigned long i, n = 6, k;
    if (argc > 1) n = strtoul(argv[1], NULL, 10);
    blob[0] = IS_ARRAY;  blob[1] = 0;
    blob[2] = IS_OBJECT; blob[3] = 1;
    for (i = 0; i < n; i++) { k = i & 1u; acc = acc * 31 + kernel(blob, k * 2, 2); }
    printf("u64=%llu\n", (unsigned long long)(acc * 31 + php_shim_tally()));
    return 0;
}
