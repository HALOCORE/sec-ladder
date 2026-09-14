/* ph56 rung R1h -- PHP 5.0.0's compiler and executor plus THE REAL UPSTREAM FIX.
 *
 * ⭐⭐ THIS FILE IS `c/kernel.c` PLUS THE THREE INSERTED LINES OF
 * `1e708a5aeb30711f8b7b2a811377a13f2b23a8c9` (Marcus Boerger, 2004-08-29,
 * *"Bugfix #29882 isset crashes on arrays"*) AND NOTHING ELSE. One file, three
 * insertions, zero deletions. `controls/r1h_backport.py` re-derives the
 * difference between the two kernels on every run and checks it against the
 * upstream patch bytes at `controls/1e708a5aeb30.patch`.
 *
 * ⭐ AND `git apply` PLACES IT, which is the opposite of ph55. The commit is six
 * weeks after 5.0.0 shipped and the function had not drifted, so the hunk lands
 * -- `Hunk #1 succeeded at 761 (offset -2 lines)`. ⚠ THE OFFSET IS THE POINT:
 * the hunk header says `@@ -763,6` and 5.0.0's own `case BP_VAR_IS:` is ALSO at
 * 763, but those are two different lines and the agreement is a coincidence --
 * the hunk's first context line is `opline->opcode += 3;`, which 5.0.0 puts at
 * 761. It applies DESPITE a two-line offset, not because of an exact match.
 * `controls/r1h_backport.py` measures it; ../NOTES.md §5 says so.
 *
 * ⚠⚠ AND THE FIX IS COMPLETE FOR THE *BUG*, NOT FOR THE *SWITCH*. Four arms
 * lacked the guard and upstream added it to ONE. ../NOTES.md §2 is the census:
 * `BP_VAR_W` is legal by design, `BP_VAR_RW` runs clean, and
 * `BP_VAR_FUNC_ARG` is a LIVE UNCAUGHT SIBLING this patch does not touch. That
 * is a RESULT the row reports, not a defect the row repairs
 * (`PROTOCOL_PHP.md` §C: report it; do not repair it).
 *
 * The rest of this comment is `c/kernel.c`'s, unchanged, because the program is.
 *
 * ph56 rung R1 -- PHP 5.0.0's compiler and executor, NARROWED. THE BUG.
 *
 * ============================================================================
 * PROVENANCE
 * ============================================================================
 *   php-5.0.0.tar.gz  sha256 5783e0c0ba94f165633a565fe73a83e59cf17b6880ef95fa
 *                            8f936dc6301d6919
 *   tar -xzOf <tarball> php-5.0.0/Zend/zend_compile.c | sed -n '736,780p'
 *   plus five more spans, all pinned in ../spec.md `provenance.extra_spans`:
 *     zend_compile.h:636-656    the six groups of three, and the comment
 *     zend_compile.c:3215,3240  zend_do_isset_or_isempty -- THE SECOND REWRITE
 *     zend_compile.c:1398,1430  zend_do_pass_param -- FUNC_ARG's reachability
 *     zend_execute.c:88,125     get_zval_ptr -- the IS_UNUSED arm RETURNS NULL
 *     zend_execute.c:3958,4000  the handler that dereferences it
 *     zend_execute.c:890,975    zend_fetch_dimension_address -- the append arm
 *   Corpus row CRASH-041, root cause `isset-dim-unused-no-compile-guard`,
 *   CWE-476. Tier: declared in ../spec.md and MEASURED, not assumed.
 *
 * ============================================================================
 * THE DEFECT, IN ONE LINE
 * ============================================================================
 * :763-765 applied the mode delta without the test its two siblings apply,
 * and the three lines below put that test back:
 *
 *     case BP_VAR_R:
 *         if (opline->opcode == ZEND_FETCH_DIM_W
 *             && opline->op2.op_type == IS_UNUSED) {
 *             zend_error(E_COMPILE_ERROR, "Cannot use [] for reading");
 *         }
 *         opline->opcode -= 3;   break;          <- :752-757  ✅ GUARDED
 *     ...
 *     case BP_VAR_IS:
 *         opline->opcode += 6;   break;          <- :763-765  ⛔ NOT GUARDED
 *     ...
 *     case BP_VAR_UNSET:
 *         if (opline->opcode == ZEND_FETCH_DIM_W
 *             && opline->op2.op_type == IS_UNUSED) {
 *             zend_error(E_COMPILE_ERROR, "Cannot use [] for unsetting");
 *         }
 *         opline->opcode += 12;  break;          <- :770-775  ✅ GUARDED
 *
 * ⚠⚠ THE ARITHMETIC IS NOT A TRICK, IT IS THE DOCUMENTED LAYOUT. The eighteen
 * fetch opcodes are six groups of three at stride 3 and upstream says so in a
 * comment at zend_compile.h:636-638, exclamation mark and all. `+= 6` walks two
 * groups: ZEND_FETCH_DIM_W (84) -> ZEND_FETCH_DIM_IS (90). What the arithmetic
 * cannot carry is WHICH ARMS HAVE BEEN THOUGHT ABOUT.
 *
 * ============================================================================
 * ⛔⛔ AND THE HARM IS NOT WHERE READING `:763` ALONE WOULD PUT IT
 * ============================================================================
 * `ZEND_FETCH_DIM_IS` is NOT what reaches the executor on this trigger.
 * `zend_do_isset_or_isempty` calls `zend_do_end_variable_parse(BP_VAR_IS, 0)`
 * and then, four lines later, REWRITES the last opline again
 * (zend_compile.c:3223-3231):
 *
 *     case ZEND_FETCH_DIM_IS:
 *         last_op->opcode = ZEND_ISSET_ISEMPTY_DIM_OBJ;   <- :3229
 *
 * So the emitted opcode is ZEND_ISSET_ISEMPTY_DIM_OBJ (115) carrying an op2 of
 * IS_UNUSED, and THAT handler reads op2 with no test at all:
 *
 *     zval *offset = get_zval_ptr(&opline->op2, EX(Ts), &EG(free_op2),
 *                                 BP_VAR_R);          <- :3961, returns NULL
 *     ...
 *     switch (offset->type) {                          <- :3973, DEREFERENCES IT
 *
 * `get_zval_ptr`'s `case IS_UNUSED:` is an explicit `return NULL;` (:118-121).
 * ⭐ `offsetof(zval, type)` is 20, and a pristine 5.0.0 CLI faults at exactly
 * `SEGV on unknown address 0x000000000014`. ../NOTES.md §1 has the run.
 *
 * ⭐⭐ THE SECOND HARM IS A DIFFERENT ONE AND IT NEEDS A CHAIN.
 * `zend_do_isset_or_isempty` rewrites only the LAST opline, so in
 * `isset($a[][0])` the `[]` opline SURVIVES as ZEND_FETCH_DIM_IS and
 * `zend_fetch_dim_is_handler` really does run. Its
 * `zend_fetch_dimension_address` then takes the `op2->op_type == IS_UNUSED`
 * arm at :935-943 -- `new_zval = &EG(uninitialized_zval); new_zval->refcount++;
 * zend_hash_next_index_insert(...)` -- so `isset` APPENDS AN ELEMENT and
 * returns false, with exit 0 and no diagnostic from anything. Measured on the
 * pristine CLI: `count($a)` goes 3 -> 4. ../NOTES.md §1.
 *
 * ⚠⚠⚠ AND THAT APPEND IS NOT ITSELF A DEFECT -- IT IS THE IMPLEMENTATION OF
 * `$a[] = 1`. The same :935-943 arm is what BP_VAR_W and BP_VAR_RW reach on
 * every legal append, measured, so the `refcount++` on the process-global is
 * ordinary bookkeeping and the FAILURE arm at :941-942 decrements it again.
 * This kernel keeps `zval.refcount` where PHP keeps it and folds every slot's
 * refcount into the answer, so the balance is a NUMBER rather than an argument.
 * ../NOTES.md §1.4.
 *
 * ============================================================================
 * WHAT NARROWING REMOVED, AND WHY NONE OF IT IS A SEMANTIC CHANGE
 * ============================================================================
 * 1. `TSRMLS_DC` / `TSRMLS_CC` everywhere. Thread plumbing.
 *
 * 2. The fetch LIST is one or two records rather than a `zend_llist`. The
 *    switch runs once per list element in upstream (`while (le)`, :748-779) and
 *    once per record here; what the row needs is that it runs per opline and
 *    that only the LAST is rewritten by :3223-3231, and both hold.
 *
 * 3. `zvalue_value` keeps its `lval` member and the other fifteen bytes of the
 *    union become one opaque `value_hi` word, so the STRUCT OFFSETS are
 *    upstream's -- `refcount` at 16, `type` at 20. The branch that faults is
 *    `switch (offset->type)` and it is one for one, at the same offset.
 *
 * 4. `zend_hash` becomes a fixed DIM-element vector per array plus a next-free
 *    index. `zend_hash_next_index_insert` returning FAILURE (:939) is modelled
 *    by that vector being full, which is the one outcome the defect's arm
 *    distinguishes.
 *
 * 5. Dispatch is a `switch` on the opcode rather than
 *    `zend_opcode_handlers[opline->opcode]`. ⚠ THAT IS SOUND HERE AND IT WAS
 *    NOT ON ph55: every opcode this row emits HAS a handler, and the harm is a
 *    NULL OPERAND inside one of them rather than a NULL HANDLER. ph55's row is
 *    the one where the table entry is the mechanism. ../NOTES.md §7.
 *
 * ============================================================================
 * WHAT IS *NOT* CHANGED, AND MUST NOT BE
 * ============================================================================
 *   * the switch keeps SIX arms in upstream's order with upstream's deltas and
 *     upstream's two guards, and the opcode numbers are the REAL ones (80-97),
 *     so `+= 6` really does land on ZEND_FETCH_DIM_IS.
 *   * `zend_do_isset_or_isempty`'s second rewrite stays, and stays AFTER.
 *   * `get_zval_ptr` keeps its `case IS_UNUSED: return NULL;`, and the handler
 *     keeps dereferencing the result with nothing in between.
 *   * the append arm keeps its `refcount++`, its FAILURE branch and that
 *     branch's `refcount--`.
 */

#include <stdint.h>
#include <stddef.h>
#include <string.h>

#include "kernel.h"

#define PHP_SHIM_IMPL /* exactly one TU defines the allocator state */
#include "emalloc_shim.h"

/* ---------------------------------------------------------------- shape -- */
/* Records per window. `main.c` refuses a larger window, which is a DRIVER bound
 * and not a compiler check: `get_next_op` heap-grows the op_array and has no
 * such limit. ../spec.md `provenance.divergences`. */
#define PH56_MAX_STMT 64
#define PH56_MAX_OPS (2 * PH56_MAX_STMT) /* a chain emits two oplines */

#define PH56_NVAR 8 /* CV slots           -- the symbol table   */
#define PH56_DIM 4  /* elements per array -- a zend_hash, fixed */

/* The flat zval store. Two reserved slots come first, exactly as PHP keeps
 * `EG(uninitialized_zval)` and `EG(error_zval)` as process-global singletons. */
#define PH56_UNINIT 0u /* EG(uninitialized_zval) -- THE GLOBAL THE APPEND TAKES */
#define PH56_ERR 1u    /* EG(error_zval)                                        */
#define PH56_VAR_BASE 2u
#define PH56_ARR_BASE (PH56_VAR_BASE + PH56_NVAR)
#define PH56_NSLOT (PH56_ARR_BASE + PH56_NVAR * PH56_DIM)

/* zval.type, narrowed to the four this row's control flow distinguishes. */
#define PH56_IS_NULL 0u
#define PH56_IS_LONG 1u
#define PH56_IS_ARRAY 2u
#define PH56_IS_STRING 3u

/* ============ NARROWED: zend_compile.h:285-288 ============================ */
/* `znode.op_type`. Upstream's own bit values, because `IS_UNUSED` is tested by
 * the guard this row is about and a renumbering would make that test read
 * differently from the tarball. */
#define PH56_IS_CONST 1u  /* (1<<0) */
#define PH56_IS_VAR 4u    /* (1<<2) */
#define PH56_IS_UNUSED 8u /* (1<<3) -- `Unused variable`, and the whole row */
/* ========== end narrowed: zend_compile.h:285-288 ========================== */

/* ============ NARROWED: zend_compile.h:756-762 ============================ */
/* The six access modes. Upstream's own values. */
#define PH56_BP_VAR_R 0u
#define PH56_BP_VAR_W 1u
#define PH56_BP_VAR_RW 2u
#define PH56_BP_VAR_IS 3u
#define PH56_BP_VAR_FUNC_ARG 5u
#define PH56_BP_VAR_UNSET 6u
#define PH56_N_MODES 6u /* the six the compiler can be asked for */
/* ========== end narrowed: zend_compile.h:756-762 ========================== */

/* ============ NARROWED: zend_compile.h:636-656 ============================ */
/* ⭐⭐ THE REAL OPCODE NUMBERS, AND THEY ARE LOAD-BEARING. Upstream's comment
 * at :636-638 -- quoted without its delimiters, which a C comment cannot nest:
 *
 *     the following 18 opcodes are 6 groups of 3 opcodes each, and must
 *     remain in that order!
 *
 * `zend_do_end_variable_parse` relies on exactly that: `+= 6` on 84 is 90
 * because ZEND_FETCH_DIM_W and ZEND_FETCH_DIM_IS are two groups apart. Keeping
 * the literal values means the row's arithmetic is upstream's arithmetic. */
#define PH56_FETCH_R 80u
#define PH56_FETCH_DIM_R 81u
#define PH56_FETCH_OBJ_R 82u
#define PH56_FETCH_W 83u
#define PH56_FETCH_DIM_W 84u
#define PH56_FETCH_OBJ_W 85u
#define PH56_FETCH_RW 86u
#define PH56_FETCH_DIM_RW 87u
#define PH56_FETCH_OBJ_RW 88u
#define PH56_FETCH_IS 89u
#define PH56_FETCH_DIM_IS 90u
#define PH56_FETCH_OBJ_IS 91u
#define PH56_FETCH_FUNC_ARG 92u
#define PH56_FETCH_DIM_FUNC_ARG 93u
#define PH56_FETCH_OBJ_FUNC_ARG 94u
#define PH56_FETCH_UNSET 95u
#define PH56_FETCH_DIM_UNSET 96u
#define PH56_FETCH_OBJ_UNSET 97u
/* zend_compile.h:683-684, :713 -- the three `zend_do_isset_or_isempty` writes. */
#define PH56_ISSET_ISEMPTY_VAR 114u
#define PH56_ISSET_ISEMPTY_DIM_OBJ 115u
#define PH56_ISSET_ISEMPTY_PROP_OBJ 148u
/* ========== end narrowed: zend_compile.h:636-656, :683-684, :713 ========== */

/* `zend_op`, narrowed: an opcode, the two operands' kinds and values, and the
 * result temp. `extended_value` carries ZEND_ISSET, as :3239 writes it. */
typedef struct ph56_op {
    uint8_t opcode;
    uint8_t op1_type;
    uint8_t op2_type;
    uint8_t ext;
    uint16_t op1;
    uint16_t op2;
    uint16_t result;
} ph56_op;

/* ============ NARROWED: Zend/zend.h `struct _zval_struct` ================= */
/* `zval`. ⚠ IT IS A STRUCT AND THE ROW NEEDS IT TO BE: the fault is
 * `offset->type` through a NULL `zval *`, so the pointer has to be a pointer.
 *
 * ⭐⭐⭐ AND THE FIELD ORDER IS UPSTREAM'S, DELIBERATELY, SO THAT THE FAULTING
 * OFFSET IS UPSTREAM'S. PHP's zval is
 *
 *     zvalue_value value;      16 bytes on this ABI (the largest member is
 *                              `struct { char *val; int len; }`)
 *     zend_uint    refcount;   at 16
 *     zend_uchar   type;       at 20 == 0x14
 *     zend_uchar   is_ref;     at 21
 *
 * and a pristine 5.0.0 CLI built from the pinned tarball faults at exactly
 * `SEGV on unknown address 0x000000000014`. This kernel keeps the offsets so
 * that its own fault address is the SAME NUMBER rather than a different one
 * that would have to be explained away. `PH56_LAYOUT_ASSERT` below turns that
 * into a compile-time CHECK -- ../NOTES.md §1.3 has both runs side by side. */
typedef struct ph56_zval {
    uint64_t lval;      /* value.lval                                      :0  */
    uint64_t value_hi;  /* the rest of the union -- str.val / str.len / ht :8  */
    uint32_t refcount;  /*                                                 :16 */
    uint8_t type;       /* ⛔ :20 == 0x14 -- THE BYTE THE NULL READ TOUCHES    */
    uint8_t is_ref;     /*                                                 :21 */
} ph56_zval;

/* A C99 compile-time assertion (`_Static_assert` is C11 and `build.py` passes
 * `-std=c99`): a negative array bound if the offset ever moves. */
typedef char PH56_LAYOUT_ASSERT[
    (offsetof(ph56_zval, type) == 20 && offsetof(ph56_zval, refcount) == 16)
        ? 1 : -1];
/* ========== end narrowed: Zend/zend.h `struct _zval_struct` =============== */

/* `zend_executor_globals` + `zend_execute_data`, narrowed to what this row
 * touches. */
typedef struct ph56_ex {
    ph56_zval slots[PH56_NSLOT];
    uint16_t anext[PH56_NVAR];    /* HashTable.nNextFreeElement                  */
    uint16_t ts[PH56_MAX_STMT];   /* EX(Ts)[].var.ptr_ptr, as a slot index       */
    uint64_t acc;
    /* ⚠ `zend_bailout()`'s reach, as a value rather than a longjmp: 0 = none,
     * 1 = E_COMPILE_ERROR (the two guards; nothing runs at all), 2 = E_ERROR
     * (the string container's own guard at :963-964; execution stops there).
     * A `setjmp`/`longjmp` pair would be modelling PHP's SYNTAX rather than its
     * behaviour, and `provenance.divergences` itemises the substitution. */
    uint8_t bailout;
} ph56_ex;

/* ---------------------------------------------------- the zval helpers --- */
#define PH56_VAR_OF(o) (PH56_VAR_BASE + (unsigned)((o) % PH56_NVAR))
#define PH56_TMP_OF(o) ((unsigned)((o) % PH56_MAX_STMT))

/* ============ NARROWED: zend_execute.c:88-125 ============================= */
/* `_get_zval_ptr`. ⭐⭐ THE `IS_UNUSED` ARM IS THE ROW'S OTHER HALF AND IT IS
 * AN EXPLICIT CASE, NOT A FALL-THROUGH:
 *
 *     case IS_UNUSED:
 *         *should_free = 0;
 *         return NULL;                              <- :118-121
 *
 * It is correct: an operand that is not there has no zval. Every caller that
 * can be handed an IS_UNUSED operand is supposed to know it cannot be. */
static ph56_zval *ph56_get_zval_ptr(ph56_ex *ex, uint8_t op_type, uint16_t op)
{
    switch (op_type) {
        case PH56_IS_CONST:
            return &ex->slots[PH56_VAR_OF(op)];
        case PH56_IS_VAR:
            return &ex->slots[ex->ts[PH56_TMP_OF(op)] % PH56_NSLOT];
        case PH56_IS_UNUSED:
            return NULL; /* :120 */
        default:
            return NULL;
    }
}
/* ========== end narrowed: zend_execute.c:88-125 =========================== */

/* `get_obj_zval_ptr_ptr`, narrowed: the container is always a CV slot here. */
static ph56_zval *ph56_get_obj_zval_ptr_ptr(ph56_ex *ex, uint16_t op)
{
    return &ex->slots[PH56_VAR_OF(op)];
}

/* ============ NARROWED: zend_execute.c:896-975 ============================ */
/* `zend_fetch_dimension_address`. The IS_ARRAY arm's `op2->op_type ==
 * IS_UNUSED` branch is :935-943 and it is the APPEND -- which is what `$a[] =
 * 1` is implemented by, and is therefore NOT a defect on its own.
 *
 * ⭐ THE STRING CONTAINER *IS* GUARDED, at :963-964:
 *     if (op2->op_type==IS_UNUSED) {
 *         zend_error(E_ERROR, "[] operator not supported for strings");
 *     }
 * Arrays are the unguarded container type, which is exactly what the bug title
 * says. Both arms are here so the contrast is in the measured program. */
static uint16_t ph56_fetch_dimension_address(ph56_ex *ex, uint16_t op1,
                                             uint8_t op2_type, uint16_t op2,
                                             unsigned type)
{
    unsigned b = PH56_VAR_OF(op1);
    ph56_zval *container = &ex->slots[b];

    if (container->type == PH56_IS_NULL) { /* :914-927 */
        if (type == PH56_BP_VAR_W || type == PH56_BP_VAR_RW) {
            container->type = PH56_IS_ARRAY; /* array_init(container), :924 */
            container->lval = (uint64_t)(b - PH56_VAR_BASE);
            ex->anext[b - PH56_VAR_BASE] = 0;
        }
    }

    switch (container->type) {
        case PH56_IS_ARRAY: { /* :930 */
            unsigned a = (unsigned)(container->lval % PH56_NVAR);
            if (op2_type == PH56_IS_UNUSED) { /* :935 -- THE APPEND */
                uint16_t n = ex->anext[a];
                ex->slots[PH56_UNINIT].refcount++; /* :938 new_zval->refcount++ */
                if (n >= PH56_DIM) {     /* :939 ... == FAILURE */
                    /* :940 "Cannot add element to the array as the next
                     * element is already occupied" */
                    ex->slots[PH56_UNINIT].refcount--; /* :942 new_zval->refcount-- */
                    return (uint16_t)PH56_UNINIT; /* :941 */
                }
                ex->anext[a] = (uint16_t)(n + 1u);
                {
                    unsigned s = PH56_ARR_BASE + a * PH56_DIM + n;
                    ex->slots[s].type = PH56_IS_NULL; /* the uninitialized zval */
                    ex->slots[s].lval = 0u;
                    return (uint16_t)s;
                }
            }
            /* :944 zend_fetch_dimension_address_inner */
            return (uint16_t)(PH56_ARR_BASE + a * PH56_DIM
                              + (unsigned)(op2 % PH56_DIM));
        }
        case PH56_IS_STRING: /* :959 */
            if (op2_type == PH56_IS_UNUSED) {
                /* :963-964 E_ERROR "[] operator not supported for strings" --
                 * ⭐ THE CONTAINER TYPE THAT *IS* GUARDED. */
                ex->bailout = 2u;
                return (uint16_t)PH56_ERR;
            }
            return (uint16_t)PH56_UNINIT;
        case PH56_IS_NULL: /* :949-957 -- read mode */
            return (uint16_t)PH56_UNINIT;
        default: /* a scalar: "Cannot use a scalar value as an array" */
            return (uint16_t)PH56_ERR;
    }
}
/* ========== end narrowed: zend_execute.c:896-975 ========================== */

/* ============ NARROWED: zend_compile.c:736-780 ============================ */
/* `zend_do_end_variable_parse`. ⛔⛔ THE DEFECT SITE, AND THE SWITCH IS
 * UPSTREAM'S: six arms, upstream's order, upstream's deltas, and upstream's two
 * guards -- with the third one MISSING exactly where 5.0.0 leaves it missing.
 *
 * Returns 0 on E_COMPILE_ERROR (which in PHP is a `zend_bailout()` longjmp out
 * of the whole compile, so nothing runs at all -- ../spec.md
 * `provenance.divergences`). */
static int ph56_do_end_variable_parse(ph56_ex *ex, ph56_op *opline, unsigned type)
{
    switch (type) {                                            /* :751 */
        case PH56_BP_VAR_R:                                    /* :752 */
            if (opline->opcode == PH56_FETCH_DIM_W
                && opline->op2_type == PH56_IS_UNUSED) {       /* :753 */
                /* :754 zend_error(E_COMPILE_ERROR, "Cannot use [] for reading") */
                ex->bailout = 1u;
                return 0;
            }
            opline->opcode -= 3;                               /* :756 */
            break;                                             /* :757 */
        case PH56_BP_VAR_W:                                    /* :758 */
            break;                                             /* :759 */
        case PH56_BP_VAR_RW:                                   /* :760 */
            opline->opcode += 3;                               /* :761 */
            break;                                             /* :762 */
        case PH56_BP_VAR_IS:                                   /* :763 */
            /* ✅✅ 1e708a5aeb30's THREE INSERTED LINES, and they are
             * `BP_VAR_R`'s OWN GUARD COPIED ACROSS -- same test, same error
             * message string, "Cannot use [] for reading". Nothing is invented,
             * exactly as ph55's fix was the normal exit's own three lines. */
            if (opline->opcode == PH56_FETCH_DIM_W
                && opline->op2_type == PH56_IS_UNUSED) {
                ex->bailout = 1u;
                return 0;
            }
            opline->opcode += 6; /* 3+3 */                     /* :764 */
            break;                                             /* :765 */
        case PH56_BP_VAR_FUNC_ARG:                             /* :766 */
            opline->opcode += 9; /* 3+3+3 */                   /* :767 */
            opline->ext = 0u;    /* = arg_offset, :768 */
            break;                                             /* :769 */
        case PH56_BP_VAR_UNSET:                                /* :770 */
            if (opline->opcode == PH56_FETCH_DIM_W
                && opline->op2_type == PH56_IS_UNUSED) {       /* :771 */
                /* :772 zend_error(E_COMPILE_ERROR, "Cannot use [] for unsetting") */
                ex->bailout = 1u;
                return 0;
            }
            opline->opcode += 12; /* 3+3+3+3 */                /* :774 */
            break;                                             /* :775 */
        default:
            break;
    }                                                          /* :776 */
    return 1;
}
/* ========== end narrowed: zend_compile.c:736-780 ========================== */

/* ============ NARROWED: zend_compile.c:3215-3240 ========================== */
/* `zend_do_isset_or_isempty`. ⭐⭐ THE SECOND REWRITE, AND IT IS WHY READING
 * `:763` ALONE NAMES THE WRONG HARM. It runs AFTER
 * `zend_do_end_variable_parse(BP_VAR_IS, 0)` and rewrites the LAST opline only,
 * so the opcode that reaches the executor on `isset($a[])` is
 * ZEND_ISSET_ISEMPTY_DIM_OBJ and not ZEND_FETCH_DIM_IS. */
static void ph56_do_isset_or_isempty(ph56_op *last_op)
{
    switch (last_op->opcode) {                 /* :3225 */
        case PH56_FETCH_IS:
            last_op->opcode = PH56_ISSET_ISEMPTY_VAR;       /* :3227 */
            break;
        case PH56_FETCH_DIM_IS:
            last_op->opcode = PH56_ISSET_ISEMPTY_DIM_OBJ;   /* :3229 */
            break;
        case PH56_FETCH_OBJ_IS:
            last_op->opcode = PH56_ISSET_ISEMPTY_PROP_OBJ;  /* :3231 */
            break;
        default:
            break;
    }
    last_op->ext = 1u; /* = type, i.e. ZEND_ISSET -- :3239 */
}
/* ========== end narrowed: zend_compile.c:3215-3240 ======================== */

/* ============ NARROWED: zend_execute.c:3958-4000 ========================== */
/* `zend_isset_isempty_dim_prop_obj_handler`. ⛔⛔ THE FAULTING FRAME.
 *
 *     zval **container = get_obj_zval_ptr_ptr(&opline->op1, ...);   :3960
 *     zval *offset     = get_zval_ptr(&opline->op2, ...);           :3961
 *     ...
 *     switch (offset->type) {                                       :3973
 *
 * There is NOTHING between :3961 and :3973 that tests `offset`. There does not
 * need to be: every opcode the compiler emits for this handler is supposed to
 * carry an op2. `isset($a[])` is the one that does not. */
static void ph56_isset_isempty_dim_obj_handler(ph56_ex *ex, const ph56_op *opline)
{
    ph56_zval *container = ph56_get_obj_zval_ptr_ptr(ex, opline->op1); /* :3960 */
    ph56_zval *offset = ph56_get_zval_ptr(ex, opline->op2_type, opline->op2);
    int isset = 0;                                                     /* :3969 */
    unsigned result = 0;

    if (container->type == PH56_IS_ARRAY) {                            /* :3967 */
        unsigned a = (unsigned)(container->lval % PH56_NVAR);
        /* ⛔⛔⛔ :3973 -- `switch (offset->type)`. `offset` IS NULL whenever
         * op2 is IS_UNUSED, and the compiler emitted exactly that. On a
         * pristine 5.0.0 CLI this reads address 0x14, which is
         * `offsetof(zval, type)`. */
        switch (offset->type) {
            case PH56_IS_LONG: { /* :3977-3986 */
                unsigned idx = (unsigned)(offset->lval % PH56_DIM);
                unsigned s = PH56_ARR_BASE + a * PH56_DIM + idx;
                if (idx < ex->anext[a]) {
                    isset = 1;
                    if (ex->slots[s].type != PH56_IS_NULL) {
                        result = 1; /* :4002 ZEND_ISSET */
                    }
                }
                break;
            }
            case PH56_IS_NULL: /* :3992-3996 */
            default:
                break;
        }
    }
    ex->acc = ex->acc * 31u + (uint64_t)isset;
    ex->acc = ex->acc * 31u + (uint64_t)result;
}
/* ========== end narrowed: zend_execute.c:3958-4000 ======================== */

/* ---------------------------------------------------- the fetch handlers -- */
/* `zend_fetch_dim_{r,w,rw,is,func_arg,unset}_handler` -- zend_execute.c:2040-2100.
 * Six one-line handlers that differ only in the BP_VAR_* they pass down, which
 * is the whole reason the opcodes are laid out at a stride in the first place. */
static void ph56_fetch_dim_handler(ph56_ex *ex, const ph56_op *opline, unsigned type)
{
    uint16_t r = ph56_fetch_dimension_address(ex, opline->op1, opline->op2_type,
                                              opline->op2, type);
    ex->ts[PH56_TMP_OF(opline->result)] = r;
}

/* `zend_fetch_{r,w,...}_handler` -- the non-dim members of each group. */
static void ph56_fetch_handler(ph56_ex *ex, const ph56_op *opline)
{
    ex->ts[PH56_TMP_OF(opline->result)] = (uint16_t)PH56_VAR_OF(opline->op1);
}

/* `zend_isset_isempty_var_handler` -- zend_execute.c:4048. */
static void ph56_isset_isempty_var_handler(ph56_ex *ex, const ph56_op *opline)
{
    ph56_zval *v = ph56_get_obj_zval_ptr_ptr(ex, opline->op1);
    ex->acc = ex->acc * 31u + (uint64_t)(v->type != PH56_IS_NULL);
}

/* ============ NARROWED: zend_execute.c:1383-1396 ========================== */
/* `execute()`'s dispatch loop. Upstream reaches each handler through
 * `zend_opcode_handlers[opline->opcode]`; this row switches on the opcode
 * instead, and that is SOUND HERE in a way it was not on ph55: every opcode
 * this compiler can emit HAS a handler, and the harm is a NULL OPERAND inside
 * one of them rather than a NULL HANDLER reached through the table.
 * ../spec.md `provenance.divergences` itemises it. */
static void ph56_execute(ph56_ex *ex, const ph56_op *ops, size_t nops)
{
    size_t pc;
    for (pc = 0; pc < nops; pc++) {
        const ph56_op *opline = &ops[pc];
        if (ex->bailout != 0u) {
            break; /* zend_bailout() -- E_ERROR leaves the executor */
        }
        ex->acc = ex->acc * 31u + (uint64_t)opline->opcode;
        switch (opline->opcode) {
            case PH56_FETCH_DIM_R:
                ph56_fetch_dim_handler(ex, opline, PH56_BP_VAR_R); break;
            case PH56_FETCH_DIM_W:
                ph56_fetch_dim_handler(ex, opline, PH56_BP_VAR_W); break;
            case PH56_FETCH_DIM_RW:
                ph56_fetch_dim_handler(ex, opline, PH56_BP_VAR_RW); break;
            case PH56_FETCH_DIM_IS:
                /* ⭐ REACHABLE, and only through a CHAIN: :3223-3231 rewrites
                 * the LAST opline only, so `isset($a[][0])` leaves this one
                 * standing. It is the SILENT harm -- the array grows and isset
                 * returns false. Measured on the pristine CLI, 3 -> 4. */
                ph56_fetch_dim_handler(ex, opline, PH56_BP_VAR_IS); break;
            case PH56_FETCH_DIM_FUNC_ARG:
                /* :2084 -- ARG_SHOULD_BE_SENT_BY_REF picks W or R; by value is
                 * the common case and is what `f($a[])` takes. */
                ph56_fetch_dim_handler(ex, opline, PH56_BP_VAR_R); break;
            case PH56_FETCH_DIM_UNSET:
                ph56_fetch_dim_handler(ex, opline, PH56_BP_VAR_UNSET); break;
            case PH56_ISSET_ISEMPTY_DIM_OBJ:
                ph56_isset_isempty_dim_obj_handler(ex, opline); break;
            case PH56_ISSET_ISEMPTY_VAR:
                ph56_isset_isempty_var_handler(ex, opline); break;
            default:
                ph56_fetch_handler(ex, opline); break;
        }
    }
}
/* ========== end narrowed: zend_execute.c:1383-1396 ======================== */

/* ---------------------------------------------------------- the decoder -- */
/* The blob IS the record stream the parser hands the compiler. One statement
 * per little-endian u64:
 *
 *     byte 0   mode      BP_VAR_*, as an index into the six
 *     byte 1   base      which member of the W group the parser built,
 *                        plus bit 7 = CHAIN (two oplines, `$a[][d]`)
 *     byte 2   op2_type  IS_UNUSED / IS_CONST / IS_VAR
 *     byte 3   op2       the dimension
 *     bytes 4-5 op1      the container CV slot
 *     bytes 6-7 result   the result temp
 *
 * ⚠ THE PARSER ALWAYS BUILDS THE *W* MEMBER, and that is not an invention: the
 * guard's own text is `opline->opcode == ZEND_FETCH_DIM_W`, which is only ever
 * true if the pre-delta opcode is the W one. */
static const uint8_t PH56_MODES[PH56_N_MODES] = {
    PH56_BP_VAR_R, PH56_BP_VAR_W, PH56_BP_VAR_RW,
    PH56_BP_VAR_IS, PH56_BP_VAR_FUNC_ARG, PH56_BP_VAR_UNSET
};
static const uint8_t PH56_BASES[3] = {
    PH56_FETCH_W, PH56_FETCH_DIM_W, PH56_FETCH_OBJ_W
};
static const uint8_t PH56_OP2T[3] = {
    PH56_IS_UNUSED, PH56_IS_CONST, PH56_IS_VAR
};

/* ============ THE COMPILER'S ONE PASS ===================================== */
/* Decode one statement, build its oplines, run the mode switch over each, and
 * -- when the mode is BP_VAR_IS -- run `zend_do_isset_or_isempty`'s second
 * rewrite over the LAST one.
 *
 * Returns the number of oplines emitted, or 0 if the compile bailed out. */
static size_t ph56_compile(ph56_ex *ex, const uint8_t *win, size_t nstmt,
                           ph56_op *ops)
{
    size_t i;
    size_t n = 0;

    for (i = 0; i < nstmt; i++) {
        const uint8_t *p = win + 8u * i;
        unsigned mode = PH56_MODES[(unsigned)p[0] % PH56_N_MODES];
        unsigned chain = (p[1] & 0x80u) ? 1u : 0u;
        uint8_t base = PH56_BASES[(unsigned)(p[1] & 0x7Fu) % 3u];
        uint8_t o2t = PH56_OP2T[(unsigned)p[2] % 3u];
        uint16_t op2 = (uint16_t)p[3];
        uint16_t op1 = (uint16_t)((unsigned)p[4] | ((unsigned)p[5] << 8));
        uint16_t res = (uint16_t)((unsigned)p[6] | ((unsigned)p[7] << 8));
        size_t k;
        size_t first = n;

        if (n + 1u + chain > PH56_MAX_OPS) {
            break;
        }

        /* `while (le)` :748-779 -- the switch runs once per fetch-list element.
         * A chain's leading element is always a DIM fetch with an IS_UNUSED
         * op2, which is what `$a[][d]` parses to. */
        if (chain) {
            ops[n].opcode = PH56_FETCH_DIM_W;
            ops[n].op1_type = PH56_IS_CONST;
            ops[n].op2_type = PH56_IS_UNUSED;
            ops[n].ext = 0u;
            ops[n].op1 = op1;
            ops[n].op2 = 0u;
            ops[n].result = (uint16_t)(res + 1u);
            n++;
        }
        ops[n].opcode = base;
        ops[n].op1_type = PH56_IS_CONST;
        ops[n].op2_type = (base == PH56_FETCH_W) ? PH56_IS_UNUSED : o2t;
        ops[n].ext = 0u;
        ops[n].op1 = chain ? (uint16_t)(res + 1u) : op1;
        ops[n].op2 = op2;
        ops[n].result = res;
        n++;

        for (k = first; k < n; k++) {
            if (!ph56_do_end_variable_parse(ex, &ops[k], mode)) {
                return 0; /* zend_bailout() -- nothing runs */
            }
            ex->acc = ex->acc * 31u + (uint64_t)ops[k].opcode;
        }
        if (mode == PH56_BP_VAR_IS) {
            /* :3223 -- the LAST opline of the fetch list, and only that one. */
            ph56_do_isset_or_isempty(&ops[n - 1u]);
            ex->acc = ex->acc * 31u + (uint64_t)ops[n - 1u].opcode;
        }
    }
    return n;
}
/* ========== end the compiler's one pass =================================== */

/* The benchmark wrapper: build the globals, compile, execute, fold the store.
 *
 * ⚠ No `php_shim_reset()` and no `php_shim_tally()`: this path allocates
 * nothing. PHP's op_array is heap-grown by `get_next_op` and its hash tables by
 * `zend_hash_init`; this kernel uses frame arrays of a size the row fixes --
 * `provenance.divergences`. `provenance.uses_allocator` is `false` and says so.
 * The `c/emalloc_shim.h` symlink is carried anyway, because that rule is
 * UNCONDITIONAL. */
SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t off, size_t len)
{
    const uint8_t *win = buf + off;
    ph56_op ops[PH56_MAX_OPS];
    ph56_ex ex;
    size_t nstmt = len / 8u;
    size_t nops;
    unsigned i;

    memset(&ops, 0, sizeof ops);
    memset(&ex, 0, sizeof ex);

    /* The two process-global singletons, and the refcount PHP starts them at. */
    ex.slots[PH56_UNINIT].type = PH56_IS_NULL;
    ex.slots[PH56_UNINIT].refcount = 1u;
    ex.slots[PH56_ERR].type = PH56_IS_NULL;
    ex.slots[PH56_ERR].refcount = 1u;
    for (i = 0; i < PH56_NVAR; i++) {
        /* Half the CV slots start as arrays and half as scalars, so that both
         * container arms of `zend_fetch_dimension_address` are live. */
        unsigned s = PH56_VAR_BASE + i;
        ex.slots[s].refcount = 1u;
        if ((i & 1u) == 0u) {
            ex.slots[s].type = PH56_IS_ARRAY;
            ex.slots[s].lval = (uint64_t)i;
        } else if (i == 1u) {
            ex.slots[s].type = PH56_IS_STRING;
        } else {
            ex.slots[s].type = PH56_IS_LONG;
            ex.slots[s].lval = (uint64_t)(i * 7u);
        }
    }
    for (i = 0; i < PH56_NVAR * PH56_DIM; i++) {
        ex.slots[PH56_ARR_BASE + i].refcount = 1u;
        ex.slots[PH56_ARR_BASE + i].type = PH56_IS_NULL;
    }

    if (nstmt > PH56_MAX_STMT) {
        nstmt = PH56_MAX_STMT;
    }

    nops = ph56_compile(&ex, win, nstmt, ops);
    if (ex.bailout == 0u) {
        ph56_execute(&ex, ops, nops);
    }

    /* What `php_execute_script` observes: the store the program left behind,
     * the refcounts, and the arrays' next-free indices. ⭐ The refcount of slot
     * 0 -- `EG(uninitialized_zval)` -- is in here on purpose: it is how the row
     * answers "does the append leave the global's refcount unbalanced?" with a
     * number instead of an argument. */
    ex.acc = ex.acc * 31u + (uint64_t)ex.bailout;
    for (i = 0; i < PH56_NSLOT; i++) {
        ex.acc = ex.acc * 31u + (uint64_t)ex.slots[i].type;
        ex.acc = ex.acc * 31u + ex.slots[i].lval;
        ex.acc = ex.acc * 31u + (uint64_t)ex.slots[i].refcount;
    }
    for (i = 0; i < PH56_NVAR; i++) {
        ex.acc = ex.acc * 31u + (uint64_t)ex.anext[i];
    }
    return ex.acc;
}
