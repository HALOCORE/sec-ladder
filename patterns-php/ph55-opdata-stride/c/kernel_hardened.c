/* ph55 rung R1h -- PHP 5.0.0's executor, NARROWED, PLUS THE REAL UPSTREAM FIX.
 *
 * ⚠⚠ THIS FILE IS `c/kernel.c` PLUS THREE LINES AND TWO COMMENT BLOCKS. Diff
 * them. The three lines are `4f68f3774c34`'s whole patch, HAND BACKPORTED:
 * the commit is dated 2004-08-30 against then-HEAD, php-5.0.0 shipped
 * 2004-07-13, and by fix time the function had gained an inner block and a
 * `FREE_OP_VAR_PTR(free_op1);` that 5.0.0's `:1765-1770` does not have, so
 * `git apply` cannot place it. ../NOTES.md §5 records the failure and the
 * three independent legs that identify WHICH exit the hunk belongs to --
 * `preimage_screen.py`'s own verdict is `CANDIDATE` and is NOT one of them.
 *
 * ⭐⭐ THE FIX IS THE NORMAL EXIT'S OWN THREE LINES, COPIED ONTO THE ERROR
 * EXIT. Nothing is invented.
 *
 * The rest of this header is `c/kernel.c`'s, unchanged.
 *
 * ph55 rung R1 -- PHP 5.0.0's executor, NARROWED. THE BUG.
 *
 * ============================================================================
 * PROVENANCE
 * ============================================================================
 *   php-5.0.0.tar.gz  sha256 5783e0c0ba94f165633a565fe73a83e59cf17b6880ef95fa
 *                            8f936dc6301d6919
 *   tar -xzOf <tarball> php-5.0.0/Zend/zend_execute.c | sed -n '1724,1796p'
 *   -> 2407 bytes, sha256 9bce864972fdf5d7086b5ded5f59aa46a20580c1f02a22784cd
 *                         4c7ae2a818fe6
 *   plus five more spans, all pinned in ../spec.md `provenance.extra_spans`:
 *     zend_execute.c:1313-1338  NEXT_OPCODE / INC_OPCODE / the 512-entry table
 *     zend_execute.c:1383-1396  execute()'s dispatch loop
 *     zend_execute.c:2198-2226  zend_assign_dim_handler -- the CLEAN sibling
 *     zend_execute.c:4426-4427  zend_opcode_handlers[ZEND_OP_DATA] = NULL
 *     zend_opcode.c:341-366     pass_two's handler copy
 *   Corpus row CRASH-023, root cause
 *   `assign-op-dim-error-zval-skips-op_data-increment`, CWE-476.
 *   Tier `modelled`, and the catalogue's `narrowed` is REFUTED BY MEASUREMENT:
 *   `harness-php/provenance.py` reports the kernel overlap at 14% (13/93) over
 *   the union of the six cited spans and 16% (7/45) over the defect site alone,
 *   where `narrowed` leads a reader to expect 25%. THE CONTROL FLOW IS LIFTED
 *   ONE FOR ONE -- the flag, the arm that sets it, the `op_data = opline+1`
 *   read, both exits in upstream's order, both stride macros with upstream's
 *   bodies, pass_two's handler copy, and a dispatch loop with nothing between
 *   the field and the call -- but the SCENERY is RE-EXPRESSED: zvals become
 *   (kind, val) pairs in a flat store, `zval **` becomes an index, the hash
 *   container is gone, and the opcode set is ten opcodes standing for PHP's
 *   ~150. A tier is a COST and never a filter, and a tier read as STRONGER than
 *   it is, is the dangerous direction. ../NOTES.md §2 has the adjudication.
 *   Every divergence is itemised in ../spec.md's `provenance.divergences`,
 *   individually and with a line citation.
 *
 * ============================================================================
 * THE DEFECT, IN ONE LINE
 * ============================================================================
 * :1765-1770 exits without consulting the width flag that :1792-1794 consults:
 *
 *     if (*var_ptr == EG(error_zval_ptr)) {
 *         EX_T(opline->result.u.var).var.ptr_ptr = &EG(uninitialized_zval_ptr);
 *         SELECTIVE_PZVAL_LOCK(...);
 *         AI_USE_PTR(EX_T(opline->result.u.var).var);
 *         NEXT_OPCODE();                 <- :1769.  STRIDE 1, unconditionally
 *     }
 *     ...
 *     if (increment_opline) {            <- :1792.  the SAME function, 23
 *         INC_OPCODE();                     lines later, gets it right
 *     }
 *     NEXT_OPCODE();
 *
 * The flag is set at :1749 on the ZEND_ASSIGN_DIM arm and nowhere else, and
 * that arm is the one whose instruction is TWO WORDS (`zend_op *op_data =
 * opline+1;`, :1742). So the error exit leaves the PC on the trailing data
 * word.
 *
 * ⭐⭐ AND THE DATA WORD HAS NO HANDLER, DELIBERATELY.
 * `zend_opcode_handlers[ZEND_OP_DATA] = NULL;` (:4427) is an explicit
 * assignment, not an omission; `pass_two` copies the table into every
 * instruction (zend_opcode.c:363) so the data word's own `handler` field is
 * NULL; and the executor calls through that field with no test (:1391). The
 * result is an indirect call through NULL.
 *
 * ⚠ THERE IS EXACTLY ONE LIMB AND IT IS A CONTROL-FLOW ERROR. Nothing in this
 * kernel reads or writes out of bounds -- the PC stays inside the op_array,
 * by the structural argument in ../NOTES.md §4. The harm is that the PC is on
 * the WRONG WORD, and the NULL call is only how that MANIFESTS. ../spec.md
 * `cwe_note` says so and the row is built to price the distinction.
 *
 * ============================================================================
 * WHAT NARROWING REMOVED, AND WHY NONE OF IT IS A SEMANTIC CHANGE
 * ============================================================================
 * 1. `TSRMLS_DC` / `TSRMLS_CC` everywhere. Thread plumbing.
 *
 * 2. zvals become `(kind, val)` pairs in one flat store and `zval **` becomes
 *    an INDEX into that store. `EG(error_zval_ptr)` and
 *    `EG(uninitialized_zval_ptr)` are two reserved indices, so
 *    `*var_ptr == EG(error_zval_ptr)` at :1765 is an index comparison and the
 *    branch structure is one for one. Refcounting, `SEPARATE_ZVAL_IF_NOT_REF`
 *    and `zval_ptr_dtor` are gone; none of them touches the PC.
 *
 * 3. `zend_fetch_dimension_address(..., BP_VAR_RW)` (:1744) keeps the ONE
 *    property this row needs: on a non-array base it yields
 *    `EG(error_zval_ptr)`. That is the `$x = 1; $x[0] += 1;` trigger the
 *    corpus records, and it is what makes the error arm reachable.
 *
 * 4. The `ZEND_ASSIGN_OBJ` arm of the switch (:1731-1733) is DELETED. It is a
 *    `return zend_binary_assign_op_obj_helper(...)` into one of the THREE
 *    unconditional `INC_OPCODE(); NEXT_OPCODE();` sites (:1719), so it strides
 *    2 on every path and carries no part of the defect. Its clean sibling
 *    `zend_assign_dim_handler` (:2198-2226) IS lifted, as PH55_ASSIGN_DIM, so
 *    the contrast between a statically-two-word handler and a
 *    data-dependently-two-word one is inside the measured program.
 *
 * 5. The compiler is outside this row. The blob IS the instruction stream --
 *    `PLAN_PHP.md` §3 wants a flat blob in and a u64 out, and this is the one
 *    candidate whose original C shape IS that shape. `pass_two` is kept,
 *    because fact 8 is half the harm chain.
 *
 * 6. The exception path is deliberately outside the kernel. `INC_OPCODE()`'s
 *    own `if (!EG(exception))` guard is NOT a second instance of the defect:
 *    `zend_throw_exception_internal` parks the PC at
 *    `opcodes[last-1-1]` (zend_exceptions.c:58), one slot SHORT of the
 *    ZEND_HANDLE_EXCEPTION word, in anticipation of the `EX(opline)++` the
 *    handler's own trailing NEXT_OPCODE() performs -- and :53 reads the same
 *    invariant back. The guard exists to stop the stride being spent TWICE.
 *    It is a CORRECTION, not an omission. ../NOTES.md §3 is the trace.
 *
 * ============================================================================
 * WHAT IS *NOT* CHANGED, AND MUST NOT BE
 * ============================================================================
 *   * `NEXT_OPCODE()` and `INC_OPCODE()` stay MACROS with upstream's bodies,
 *     including `NEXT_OPCODE()`'s `return 0;`. The fact that one of them
 *     returns and the other does not is why the error exit reads like a
 *     complete exit and is not one.
 *   * dispatch stays an INDIRECT CALL through a per-instruction `handler`
 *     field that `pass_two` filled from a table with a NULL entry. A switch on
 *     the opcode would delete facts 6-9 and the row with them.
 *   * `zend_bool increment_opline` stays a LOCAL initialised to 0 at the top
 *     and set to 1 on exactly one arm.
 *   * the two exits stay TWO exits, 23 lines apart, in one function.
 */

#include <stdint.h>
#include <stddef.h>
#include <string.h>

#include "kernel.h"

#define PHP_SHIM_IMPL /* exactly one TU defines the allocator state */
#include "emalloc_shim.h"

/* ---------------------------------------------------------------- shape -- */
/* The op_array's capacity. `main.c` refuses a window larger than this, which
 * is a DRIVER bound and not a kernel check: PHP's op_array is heap-grown by
 * `get_next_op` and has no such limit. ../spec.md `provenance.divergences`. */
#define PH55_MAX_OPS 64

#define PH55_NVAR 8  /* CV slots           -- EX(Ts) / the symbol table */
#define PH55_DIM  4  /* elements per array -- a zend_hash of fixed size */
#define PH55_NT   4  /* temp_variable slots -- EX(Ts)[].var.ptr_ptr       */

/* The flat zval store. Two reserved slots come first, exactly as PHP keeps
 * `EG(uninitialized_zval)` and `EG(error_zval)` as singletons. */
#define PH55_UNINIT   0u  /* EG(uninitialized_zval_ptr) */
#define PH55_ERR      1u  /* EG(error_zval_ptr)         */
#define PH55_VAR_BASE 2u
#define PH55_ARR_BASE (PH55_VAR_BASE + PH55_NVAR)
#define PH55_NSLOT    (PH55_ARR_BASE + PH55_NVAR * PH55_DIM)

/* zval.type, narrowed to the three this row's control flow distinguishes. */
#define PH55_IS_NULL  0u
#define PH55_IS_LONG  1u
#define PH55_IS_ARRAY 2u

/* ============ NARROWED: the opcode set ==================================== */
/* Names mirror upstream's. PH55_OP_DATA is ZEND_OP_DATA and is the one whose
 * table entry is NULL (:4427). */
#define PH55_NOP          0u
#define PH55_ASSIGN       1u  /* $x = <long>                                 */
#define PH55_INIT_ARRAY   2u  /* $x = array()                                */
#define PH55_ADD          3u  /* $r = $a + $b -- ONE WORD, a real handler    */
#define PH55_FETCH_DIM_RW 4u  /* ZEND_FETCH_DIM_RW -- may yield error_zval   */
#define PH55_ASSIGN_DIM   5u  /* zend_assign_dim_handler :2198-2226, TWO words */
#define PH55_ASSIGN_ADD   6u  /* zend_binary_assign_op_helper :1724-1796     */
#define PH55_OP_DATA      7u  /* ZEND_OP_DATA -- handler is NULL             */
#define PH55_ECHO         8u  /* fold a variable into the answer             */
#define PH55_RETURN       9u  /* ZEND_RETURN -- the handler returns 1        */
#define PH55_N_OPCODES   10u

/* `zend_binary_assign_op_helper`'s `opline->extended_value` selector. */
#define PH55_X_DEFAULT 0u
#define PH55_X_DIM     1u  /* ZEND_ASSIGN_DIM -- the TWO-WORD form */

/* One decoded instruction word. `zend_op`, narrowed: `opcode`,
 * `extended_value`, three operands and the `handler` field pass_two fills. */
typedef struct ph55_op ph55_op;
typedef struct ph55_ex ph55_ex;

/* `opcode_handler_t` -- zend_execute.h. Returns non-zero to leave the loop. */
typedef int (*ph55_handler_t)(ph55_ex *ex, ph55_op *opline);

struct ph55_op {
    uint8_t opcode;
    uint8_t extended_value;
    uint16_t op1;
    uint16_t op2;
    uint16_t result;
    ph55_handler_t handler; /* zend_opcode.c:363 writes this */
};

/* `zend_execute_data`, narrowed to what the two exits and the loop touch. */
struct ph55_ex {
    ph55_op *opline;              /* EX(opline) -- THE PC                     */
    ph55_op *opcodes;             /* op_array->opcodes                        */
    uint8_t kind[PH55_NSLOT];     /* zval.type                                */
    uint64_t val[PH55_NSLOT];     /* zval.value.lval                          */
    uint16_t ts[PH55_NT];         /* EX(Ts)[].var.ptr_ptr, as an index        */
    uint64_t acc;                 /* what the benchmark observes              */
};

/* ============ NARROWED: zend_execute.c:1317-1330 ========================== */
/* ⚠ VERBATIM, including NEXT_OPCODE()'s `return 0;` and INC_OPCODE()'s lack of
 * one. CHECK_SYMBOL_TABLES() is `#else`-empty in a non-ZEND_DEBUG build
 * (:1313-1315), which is the build PHP 5.0.0 ships. */
#define CHECK_SYMBOL_TABLES()

#define NEXT_OPCODE()   \
    CHECK_SYMBOL_TABLES() \
    ex->opline++;         \
    return 0; /* CHECK_ME */

#define INC_OPCODE()      \
    if (!PH55_EXCEPTION) {  \
        CHECK_SYMBOL_TABLES() \
        ex->opline++;         \
    }

/* `EG(exception)`. ⚠ PINNED TO 0 AND THAT IS A DECISION, NOT A SIMPLIFICATION:
 * the exception path is CORRECT (../NOTES.md §3) and modelling it would add a
 * whole exception machinery for no mechanism. Kept as a token so that
 * INC_OPCODE()'s body is upstream's body. */
#define PH55_EXCEPTION 0
/* ========== end narrowed: zend_execute.c:1317-1330 ======================== */

/* ---------------------------------------------------- the zval helpers --- */
/* `get_zval_ptr_ptr` / `get_zval_ptr`, narrowed. An operand names either a CV
 * slot or a temp slot; the top bit selects, exactly as `op_type` does. */
#define PH55_OP_IS_TMP(o) (((o) & 0x8000u) != 0u)
#define PH55_VAR_OF(o) (PH55_VAR_BASE + (unsigned)((o) & 0x7FFFu) % PH55_NVAR)
#define PH55_TMP_OF(o) ((unsigned)((o) & 0x7FFFu) % PH55_NT)

static unsigned ph55_get_zval_ptr_ptr(ph55_ex *ex, uint16_t op)
{
    if (PH55_OP_IS_TMP(op)) {
        return (unsigned)ex->ts[PH55_TMP_OF(op)]; /* an IS_VAR temp */
    }
    return PH55_VAR_OF(op); /* an IS_CV slot */
}

static uint64_t ph55_get_zval_ptr(ph55_ex *ex, uint16_t op)
{
    unsigned s = ph55_get_zval_ptr_ptr(ex, op);
    return ex->kind[s] == PH55_IS_LONG ? ex->val[s] : 0u;
}

/* `zend_fetch_dimension_address(..., BP_VAR_RW)` -- zend_execute.c:1744.
 *
 * ⭐ THE ONE PROPERTY THIS ROW NEEDS: on a base that is not an array,
 * `zend_fetch_dimension_address_inner` raises
 * "Cannot use a scalar value as an array" and yields `EG(error_zval_ptr)`.
 * That is `$x = 1; $x[0] += 1;` -- the corpus's own trigger for CRASH-023. */
static unsigned ph55_fetch_dimension_address(ph55_ex *ex, uint16_t base, uint16_t dim)
{
    unsigned b = PH55_VAR_OF(base);
    if (ex->kind[b] != PH55_IS_ARRAY) {
        return PH55_ERR; /* *retval = &EG(error_zval_ptr) */
    }
    return PH55_ARR_BASE + (unsigned)(ex->val[b] % PH55_NVAR) * PH55_DIM
           + (unsigned)(dim % PH55_DIM);
}

/* `add_function`, narrowed to the long/long arm. */
static void ph55_add_function(ph55_ex *ex, unsigned dst, uint64_t v)
{
    if (ex->kind[dst] != PH55_IS_LONG) {
        ex->kind[dst] = PH55_IS_LONG;
        ex->val[dst] = 0u;
    }
    ex->val[dst] += v;
}

/* ============ NARROWED: zend_execute.c:1724-1796 ========================== */
/* `zend_binary_assign_op_helper`. THE DEFECT.
 *
 * ⚠ The `case ZEND_ASSIGN_OBJ:` arm (:1731-1733) is deleted -- see the header
 * comment, item 4. Everything else is one for one: the local flag, the arm
 * that sets it, the `op_data = opline+1` read, the two exits and their order. */
static int ph55_binary_assign_op_helper(ph55_ex *ex, ph55_op *opline)
{
    unsigned var_ptr;
    uint64_t value;
    uint8_t increment_opline = 0; /* :1728 */

    switch (opline->extended_value) { /* :1730 */
        case PH55_X_DIM: {            /* case ZEND_ASSIGN_DIM: :1734 */
            ph55_op *op_data = opline + 1; /* :1742 */

            /* :1744 -- the address lands in the DATA word's op2 temp slot */
            ex->ts[PH55_TMP_OF(op_data->op2)] =
                (uint16_t)ph55_fetch_dimension_address(ex, opline->op1, opline->op2);

            value = ph55_get_zval_ptr(ex, op_data->op1);       /* :1746 */
            var_ptr = ph55_get_zval_ptr_ptr(ex, op_data->op2); /* :1747 */
            increment_opline = 1;                              /* :1749 */
        } break;
        default:                                              /* :1753 */
            value = ph55_get_zval_ptr(ex, opline->op2);       /* :1754 */
            var_ptr = ph55_get_zval_ptr_ptr(ex, opline->op1); /* :1755 */
            /* do nothing */                                  /* :1757 */
            break;
    }

    if (var_ptr == PH55_ERR) { /* :1765 -- `*var_ptr == EG(error_zval_ptr)` */
        ex->ts[PH55_TMP_OF(opline->result)] = PH55_UNINIT; /* :1766 */
        /* SELECTIVE_PZVAL_LOCK / AI_USE_PTR are refcount plumbing, :1767-1768 */
        /* ============ R1h: 4f68f3774c34, HAND BACKPORTED =================== *
         * Stanislav Malyshev, 2004-08-30, "fix crash #29893". THREE LINES,
         * and they are the NORMAL exit's own three lines copied onto the
         * error exit. Nothing is invented; ../controls/4f68f3774c34.patch is
         * the commit and ../NOTES.md §5 shows why `git apply` refuses it. */
        if (increment_opline) {
            INC_OPCODE();
        }
        /* ============ end R1h ============================================= */
        NEXT_OPCODE(); /* :1769 */
    }

    ph55_add_function(ex, var_ptr, value);              /* :1783 binary_op(...) */
    ex->ts[PH55_TMP_OF(opline->result)] = (uint16_t)var_ptr; /* :1786 */

    if (increment_opline) { /* :1792 -- ✅ the SAME function, 23 lines later */
        INC_OPCODE();       /* :1793 */
    }
    NEXT_OPCODE(); /* :1795 */
}
/* ========== end narrowed: zend_execute.c:1724-1796 ======================== */

/* ============ NARROWED: zend_execute.c:2198-2226 ========================== */
/* `zend_assign_dim_handler` -- THE CLEAN SIBLING, and it is here on purpose.
 * It is STATICALLY two-word, so it needs no flag and has exactly one exit; the
 * `assign_dim has two opcodes!` comment at :2223 is upstream's, exclamation
 * mark and all. ⚠ Its `if (object_ptr && ... IS_OBJECT)` arm (:2210) is the
 * deleted object path; what is kept is :2212-2222 and the exit. */
static int ph55_assign_dim_handler(ph55_ex *ex, ph55_op *opline)
{
    ph55_op *op_data = opline + 1; /* :2200 */
    unsigned dst;
    uint64_t value;

    /* :2218 -- BP_VAR_W, and it too yields error_zval on a scalar base. The
     * handler writes through it without testing, which is a DIFFERENT and
     * uncatalogued question; here the write lands harmlessly in the reserved
     * error slot, exactly as PHP's does, and ../NOTES.md §9 does not
     * adjudicate it. */
    dst = ph55_fetch_dimension_address(ex, opline->op1, opline->op2);
    ex->ts[PH55_TMP_OF(op_data->op2)] = (uint16_t)dst;

    value = ph55_get_zval_ptr(ex, op_data->op1); /* :2220 */
    if (dst != PH55_ERR) {                       /* :2221 assign_to_variable */
        ex->kind[dst] = PH55_IS_LONG;
        ex->val[dst] = value;
    }
    ex->ts[PH55_TMP_OF(opline->result)] = (uint16_t)dst;

    /* assign_dim has two opcodes! -- :2223, upstream's own comment */
    INC_OPCODE(); /* :2224 */
    NEXT_OPCODE(); /* :2225 */
}
/* ========== end narrowed: zend_execute.c:2198-2226 ======================== */

/* ---------------------------------------------------- the other handlers -- */
static int ph55_nop_handler(ph55_ex *ex, ph55_op *opline)
{
    (void)opline;
    NEXT_OPCODE();
}

static int ph55_assign_handler(ph55_ex *ex, ph55_op *opline)
{
    unsigned d = PH55_VAR_OF(opline->op1);
    ex->kind[d] = PH55_IS_LONG;
    ex->val[d] = (uint64_t)opline->op2;
    ex->ts[PH55_TMP_OF(opline->result)] = (uint16_t)d;
    NEXT_OPCODE();
}

static int ph55_init_array_handler(ph55_ex *ex, ph55_op *opline)
{
    unsigned d = PH55_VAR_OF(opline->op1);
    ex->kind[d] = PH55_IS_ARRAY;
    ex->val[d] = (uint64_t)(opline->op2 % PH55_NVAR);
    ex->ts[PH55_TMP_OF(opline->result)] = (uint16_t)d;
    NEXT_OPCODE();
}

/* ⭐ ONE WORD, AND A REAL HANDLER. This is what a mis-strided PC lands on in
 * the SECOND adversarial case -- see ../spec.md and ../NOTES.md §6. */
static int ph55_add_handler(ph55_ex *ex, ph55_op *opline)
{
    /* ⚠ BOTH OPERANDS ARE READ BEFORE THE DESTINATION IS TOUCHED. `result` may
     * name the same slot as `op1` or `op2`, and writing `kind[d]` first would
     * make the second read see a type the instruction had not yet produced.
     * model.py's synthetic sweep caught exactly that in the first draft --
     * PROTOCOL_PHP.md A2a rule 2, firing on this row. */
    uint64_t v = ph55_get_zval_ptr(ex, opline->op1)
                 + ph55_get_zval_ptr(ex, opline->op2);
    unsigned d = PH55_VAR_OF(opline->result);
    ex->kind[d] = PH55_IS_LONG;
    ex->val[d] = v;
    NEXT_OPCODE();
}

static int ph55_fetch_dim_rw_handler(ph55_ex *ex, ph55_op *opline)
{
    ex->ts[PH55_TMP_OF(opline->result)] =
        (uint16_t)ph55_fetch_dimension_address(ex, opline->op1, opline->op2);
    NEXT_OPCODE();
}

static int ph55_echo_handler(ph55_ex *ex, ph55_op *opline)
{
    unsigned s = ph55_get_zval_ptr_ptr(ex, opline->op1);
    ex->acc = ex->acc * 31u + (uint64_t)ex->kind[s];
    ex->acc = ex->acc * 31u + ex->val[s];
    NEXT_OPCODE();
}

/* `ZEND_RETURN` -- the only handler that leaves the loop. */
static int ph55_return_handler(ph55_ex *ex, ph55_op *opline)
{
    (void)ex;
    (void)opline;
    return 1;
}

/* ============ NARROWED: zend_execute.c:1338, :4426-4427 =================== */
/* `ZEND_API opcode_handler_t zend_opcode_handlers[512];` (:1338) -- a
 * FIXED-SIZE table with one entry per opcode, which
 * `zend_init_opcodes_handlers` fills once at startup. Written here as a C99
 * designated initialiser so the filling happens at link time rather than on
 * every kernel call; `provenance.divergences` itemises that, and the ONE entry
 * this row turns on is written out explicitly because upstream writes it out
 * explicitly.
 *
 * ⭐⭐ `zend_opcode_handlers[ZEND_OP_DATA] = NULL;` (:4427) IS NOT AN
 * OMISSION. It sits between two real assignments, in the middle of a 200-line
 * block of them, and it is the only `= NULL` in the block. The data word is a
 * carrier of operands and was never meant to be dispatched on. */
static ph55_handler_t ph55_opcode_handlers[PH55_N_OPCODES] = {
    [PH55_NOP] = ph55_nop_handler,
    [PH55_ASSIGN] = ph55_assign_handler,
    [PH55_INIT_ARRAY] = ph55_init_array_handler,
    [PH55_ADD] = ph55_add_handler,
    [PH55_FETCH_DIM_RW] = ph55_fetch_dim_rw_handler,
    [PH55_ASSIGN_DIM] = ph55_assign_dim_handler,
    [PH55_ASSIGN_ADD] = ph55_binary_assign_op_helper,
    [PH55_OP_DATA] = NULL, /* ⭐ :4427 -- DELIBERATELY NULL */
    [PH55_ECHO] = ph55_echo_handler,
    [PH55_RETURN] = ph55_return_handler,
};
/* ========== end narrowed: zend_execute.c:1338, :4426-4427 ================= */

/* ============ NARROWED: zend_opcode.c:341-366 ============================= */
/* `pass_two`'s walk. Everything but the last two lines is jump-address fixup
 * and constant refcounting, which this kernel has no analogue for; what is
 * lifted is the line that makes the NULL reachable from an instruction. */
static void ph55_pass_two(ph55_op *opcodes, size_t last)
{
    ph55_op *opline = opcodes;
    ph55_op *end = opline + last;

    while (opline < end) {
        opline->handler = ph55_opcode_handlers[opline->opcode]; /* :363 */
        opline++;
    }
}
/* ========== end narrowed: zend_opcode.c:341-366 =========================== */

/* ---------------------------------------------------------- the decoder -- */
/* The blob IS the instruction stream. One u64 per `zend_op`, little-endian:
 *
 *     byte 0    opcode          byte 1    extended_value
 *     bytes 2-3 op1             bytes 4-5 op2           bytes 6-7 result
 *
 * ⚠ TWO WORDS ARE FORCED, AND IT IS PHP'S OWN TAIL, NOT A BOUNDS CHECK.
 * `zend_do_end_function_declaration` emits `zend_do_return` then
 * `zend_do_handle_exception` (zend_compile.c:1091-1092), so every op_array
 * ends with ZEND_RETURN followed by ZEND_HANDLE_EXCEPTION. With a maximum
 * stride of two that is what keeps the PC inside the array without the
 * executor testing anything -- ../NOTES.md §4 proves it. Both tail words are
 * PH55_RETURN here, which is the exception path's `projection`: with no
 * exception pending, ZEND_HANDLE_EXCEPTION's handler ends execution too. */
static size_t ph55_decode(const uint8_t *win, size_t nops, ph55_op *ops)
{
    size_t i;
    for (i = 0; i < nops; i++) {
        const uint8_t *p = win + 8u * i;
        ops[i].opcode = (uint8_t)(p[0] % PH55_N_OPCODES);
        ops[i].extended_value = p[1];
        ops[i].op1 = (uint16_t)((unsigned)p[2] | ((unsigned)p[3] << 8));
        ops[i].op2 = (uint16_t)((unsigned)p[4] | ((unsigned)p[5] << 8));
        ops[i].result = (uint16_t)((unsigned)p[6] | ((unsigned)p[7] << 8));
        ops[i].handler = NULL;
    }
    /* ⚠⚠ THE KERNEL'S OWN PRECONDITION, STATED WHERE C CAN STATE IT -- AND THE
     * PLACE THE LADDER SHOWS THROUGH MOST CHEAPLY. `verus.rs` says
     * `requires 16 <= len` in ONE LINE and pays nothing; C has no signature to
     * say it in, so the same fact is a run-time compare. ⭐ It is not
     * defensive padding: without it gcc's `-Wstringop-overflow` fires on both
     * lines below in every inlined (`whole`) cell -- *writing 1 byte into a
     * region of size 0 ... at offset -32 into destination object `ops`* --
     * because after inlining it cannot re-derive `nops >= 2` from the driver's
     * `stride_w >= 16`. Measured: 2 warnings without, 0 with. Every rung
     * carries it, so the compare is in the cross-language comparison on both
     * sides. ../NOTES.md §8. */
    if (nops >= 2u) {
        ops[nops - 2].opcode = (uint8_t)PH55_RETURN; /* zend_do_return          */
        ops[nops - 1].opcode = (uint8_t)PH55_RETURN; /* zend_do_handle_exception */
    }
    return nops;
}

/* How wide an instruction is. ⚠ BOTH FORMS ARE HERE AND THEY ARE NOT THE SAME
 * KIND OF FACT: `ZEND_ASSIGN_DIM` is two words for EVERY instance, which is
 * why `zend_assign_dim_handler` needs no flag (:2224); `ZEND_ASSIGN_ADD` is
 * two words only when its `extended_value` says so (:1734, :1749), which is
 * why `zend_binary_assign_op_helper` does. */
static size_t ph55_width(const ph55_op *o)
{
    return (o->opcode == PH55_ASSIGN_DIM
            || (o->opcode == PH55_ASSIGN_ADD
                && o->extended_value == PH55_X_DIM)) ? 2u : 1u;
}

/* ============ THE EMITTER'S GUARANTEE, AND IT IS THE COMPILER'S =========== */
/* `zend_compile` emits `ZEND_OP_DATA` ONLY as the trailing word of a two-word
 * instruction -- `zend_do_assign_op` calls `get_next_op` twice and sets the
 * second word's opcode to ZEND_OP_DATA -- so NO INSTRUCTION START IS A DATA
 * WORD, and that is exactly why `execute()` can dispatch through
 * `opline->handler` without testing it (:1391). The executor is not careless;
 * it is relying on an invariant the compiler establishes.
 *
 * ⚠⚠ THE COMPILER IS OUTSIDE THIS ROW -- the blob IS the op_array -- so
 * SOMETHING here has to stand in for it, and this walk is it. It visits
 * exactly the words a CORRECT executor visits and refuses a data word at any
 * of them. ⭐ It touches nothing else: a word that is not an instruction start
 * is left exactly as the blob carries it, which is what lets
 * `adversarial-opdatalive.bin` exist at all. ../NOTES.md §4.
 *
 * ⚠ Every rung has this, C and Rust alike, and `provenance.divergences`
 * itemises it. It is the ONE thing the harness must supply, and it is supplied
 * identically everywhere, so no rung is advantaged. */
static void ph55_emit_fixup(ph55_op *ops, size_t nops)
{
    size_t p = 0;
    while (p + 2u < nops) {
        if (ops[p].opcode == PH55_OP_DATA) {
            ops[p].opcode = (uint8_t)PH55_NOP;
        }
        p += ph55_width(&ops[p]);
    }
}
/* ========== end the emitter's guarantee =================================== */

/* ============ NARROWED: zend_execute.c:1345-1396 ========================== */
/* `execute()`. What is kept is the frame initialisation, `SET_OPCODE`, and the
 * dispatch loop.
 *
 * ⛔⛔ THE LOOP IS THE ROW. There is NOTHING between `EX(opline)` and the
 * call: no PC bound, no NULL test, no assertion. `zend_clean_garbage()` at
 * :1390 is refcount sweeping with no analogue here; the opcode fold stands in
 * for it as the per-dispatch observation. */
static uint64_t ph55_execute(ph55_ex *ex, ph55_op *opcodes)
{
    ex->opcodes = opcodes;
    ex->opline = opcodes; /* SET_OPCODE(op_array->opcodes) -- :1362 */

    while (1) { /* :1383 */
        ex->acc = ex->acc * 31u + (uint64_t)ex->opline->opcode;
        if (ex->opline->handler(ex, ex->opline)) { /* :1391 -- NO NULL CHECK */
            return ex->acc;                       /* :1392 */
        }
    }
}
/* ========== end narrowed: zend_execute.c:1345-1396 ======================== */

/* The benchmark wrapper: build the frame, run pass_two, execute, fold the
 * final store.
 *
 * ⚠ No `php_shim_reset()` and no `php_shim_tally()`: this path allocates
 * nothing. PHP's op_array is heap-grown by `get_next_op` at COMPILE time and
 * the compiler is outside this row; `EX(Ts)` is a `safe_emalloc` in
 * `execute()` (:1352) whose size is `op_array->T`, a compile-time constant,
 * and this kernel keeps it as a fixed frame array instead --
 * `provenance.divergences`. `provenance.uses_allocator` is `false` and says
 * so. The `c/emalloc_shim.h` symlink is carried anyway, because that rule is
 * UNCONDITIONAL. */
SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t off, size_t len)
{
    const uint8_t *win = buf + off;
    /* ⚠ ZEROED, and that is PARITY rather than necessity: `ph55_decode` writes
     * every entry the executor can reach, so C needs none of it -- but safe
     * Rust cannot declare `[Op; MAX_OPS]` without initialising all of it, and
     * a fixed per-call term present in one language and absent in the other
     * would read as a C-versus-Rust result. ../NOTES.md §8 decomposes it. */
    ph55_op ops[PH55_MAX_OPS] = {{0, 0, 0, 0, 0, NULL}};
    ph55_ex ex;
    size_t nops = len / 8u;
    unsigned i;

    memset(&ex, 0, sizeof ex);
    ex.kind[PH55_UNINIT] = PH55_IS_NULL; /* EG(uninitialized_zval) */
    ex.kind[PH55_ERR] = PH55_IS_NULL;    /* EG(error_zval)         */
    for (i = 0; i < PH55_NVAR; i++) {
        ex.kind[PH55_VAR_BASE + i] = PH55_IS_LONG;
    }
    for (i = 0; i < PH55_NVAR * PH55_DIM; i++) {
        ex.kind[PH55_ARR_BASE + i] = PH55_IS_LONG;
    }

    nops = ph55_decode(win, nops, ops);
    ph55_emit_fixup(ops, nops);
    ph55_pass_two(ops, nops);
    ph55_execute(&ex, ops);

    /* What `php_execute_script` observes: the store the program left behind. */
    for (i = 0; i < PH55_NSLOT; i++) {
        ex.acc = ex.acc * 31u + (uint64_t)ex.kind[i];
        ex.acc = ex.acc * 31u + ex.val[i];
    }
    for (i = 0; i < PH55_NT; i++) {
        ex.acc = ex.acc * 31u + (uint64_t)ex.ts[i];
    }
    return ex.acc;
}
