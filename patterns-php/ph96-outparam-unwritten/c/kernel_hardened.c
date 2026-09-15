/* ph96 rung R1h -- PHP 5.0.0's `zend_call_method` helper and the four
 * `ArrayAccess` handlers that call it, NARROWED, PLUS THE REAL UPSTREAM FIX.
 *
 * ============================================================================
 * R1h IS A BACKPORT OF cf020f133487, AND THE WORD BACKPORT IS LOAD-BEARING
 * ============================================================================
 * cf020f133487d36a8b1d9cfd16ec456f7f07952e -- Marcus Boerger, 2005-03-19,
 * "- Fix #31185". `controls/cf020f133487.patch` is the cached patch bytes.
 *
 * `git apply --check` REFUSES it on pristine 5.0.0 at every context width,
 * because the patch's pre-image carries two lines 5.0.0 does not have
 * (`SEPARATE_ARG_IF_REF(offset);` and `zval_ptr_dtor(&offset);`, an unrelated
 * later change). The three-line hand backport below reproduces upstream's own
 * diffstat EXACTLY -- `Zend/zend_object_handlers.c | 4 +---`, `1 file changed,
 * 1 insertion(+), 3 deletions(-)` -- so the SEMANTIC change is upstream's and
 * only the context is not. `controls/r1h_backport.py` re-runs both halves on
 * every invocation and takes its verdict FROM THE BYTES.
 *
 * The change, at the `offsetunset` site and nowhere else:
 *
 *   -   zval *retval;                                             :509
 *   -   zend_call_method_with_1_params(..., "offsetunset", &retval, offset);
 *   +   zend_call_method_with_1_params(..., "offsetunset", NULL, offset);
 *   -   zval_ptr_dtor(&retval);                                   :513
 *
 * It does not TEST the output -- it REMOVES it, switching the call site from
 * `zend_interfaces.c:94`'s contract to `:88-93`'s, which is the contract
 * `:413` had been using 99 lines up since before the bug was reported.
 *
 * `controls/repair_price.py` builds the OTHER attested strategy -- the guard at
 * `:385` -- as a third C binary and prices the two against each other.
 * ../NOTES.md section 7 has the numbers; this comment points at them and states
 * no verdict of theirs (PROTOCOL_PHP.md section F6a).
 *
 * ============================================================================
 * PROVENANCE
 * ============================================================================
 *   php-5.0.0.tar.gz  sha256 5783e0c0ba94f165633a565fe73a83e59cf17b6880ef95fa
 *                            8f936dc6301d6919
 *   tar -xzOf <tarball> php-5.0.0/Zend/zend_object_handlers.c | sed -n '378,434p'
 *   plus  Zend/zend_object_handlers.c | sed -n '506,517p'  -- unset_dimension
 *   plus  Zend/zend_interfaces.c      | sed -n '30,95p'    -- zend_call_method
 *   plus  Zend/zend_execute_API.c     | sed -n '384,396p'  -- _zval_ptr_dtor
 *   plus  Zend/zend_execute_API.c     | sed -n '592,595p'  -- the NULL sentinel
 *   plus  Zend/zend_execute_API.c     | sed -n '866,874p'  -- SUCCESS anyway
 *   plus  Zend/zend_execute.h         | sed -n '68,112p'   -- i_zend_is_true
 *   plus  Zend/zend.h                 | sed -n '270,293p'  -- the zval layout
 *   Corpus row CRASH-061. Tier: declared in ../spec.md and argued in
 *   ../NOTES.md section 11. The WRAPPER comes off (TSRM plumbing, the
 *   `zend_fcall_info` struct, the class-entry lookup, the VM); THE BODIES ARE
 *   UNCHANGED. Every divergence is itemised in ../spec.md's
 *   `provenance.divergences`, individually and with a citation.
 *
 * ============================================================================
 * THE DEFECT R1 HAS AND THIS RUNG DOES NOT, IN ONE LINE
 * ============================================================================
 * The STATUS is tested and the OUT-PARAMETER is not:
 *
 *     zval *retval;                                          <- :509
 *     zend_call_method_with_1_params(&object, ce, NULL,
 *                    "offsetunset", &retval, offset);        <- :512
 *     zval_ptr_dtor(&retval);                                <- :513
 *
 * `zend_call_method` DOES test its callee's status -- `if (result == FAILURE)`
 * at `zend_interfaces.c:81` raises `E_CORE_ERROR`, which does not return. What
 * nothing tests is the OUT-PARAMETER, which `zend_call_function` NULLed at
 * `:595` under its own comment and then left alone while returning SUCCESS at
 * `:873` with the exception pending.
 *
 * MEASURED, NOT REASONED. A PHP 5.0.0 CLI on this box, under
 * `.tasks-php/probes/segaddr.c`, driven by
 * `.tasks-php/probes/ph96_arrayaccess_matrix.sh`:
 *
 *     offsetUnset throws  -> SIG11 si_code=1 si_addr=0x10, rc 139
 *     offsetExists throws -> SIG11 si_code=1 si_addr=0x14, rc 139
 *     offsetGet throws    -> Fatal error: Uncaught exception, rc 255
 *     offsetSet throws    -> Fatal error: Uncaught exception, rc 255
 *     nothing throws      -> clean, rc 0
 *
 * ../NOTES.md section 2 has the run, the build it was taken on, and the two
 * cautions that travel with it.
 *
 * ============================================================================
 * THE STATUS TEST IS UPSTREAM'S AND IT IS NOT MISSING
 * ============================================================================
 * `zend_interfaces.c:81-87` tests `result == FAILURE` and calls
 * `zend_error(E_CORE_ERROR, ...)`, which terminates. So `I12/O1`'s *status
 * code* clause is DISCHARGED here, and its *NULL-able out-parameter* clause is
 * not. That distinction is the row, and this kernel keeps both halves. */
#include <stdint.h>
#include <stddef.h>

#include "kernel.h"

#define PHP_SHIM_IMPL /* exactly one TU defines the allocator state */
#include "emalloc_shim.h"

/* ==================================================================== zval ==
 * `struct _zval_struct` -- Zend/zend.h:287-293, with the union at :275-284.
 *
 * THE LAYOUT IS THE FAULT ADDRESS AND IT IS ASSERTED, NOT ASSUMED. On LP64 the
 * `zvalue_value` union is 16 bytes because `zend_object_value` is
 * `{zend_object_handle handle; zend_object_handlers *handlers;}` (zend.h:270-273),
 * so `refcount` lands at 16 = 0x10 and `type` at 20 = 0x14 -- the two addresses
 * the 5.0.0 CLI faults at. The three negative-array-size assertions below are
 * C99's `_Static_assert` (build.py compiles `-std=c99`) and fail the BUILD if
 * this extraction ever stops matching upstream's offsets. */
typedef union {
    int64_t lval;                                        /* zend.h:276 */
    double dval;                                         /* zend.h:277 */
    struct { const uint8_t *val; int32_t len; } str;     /* zend.h:278-281 */
    struct { uint32_t handle; const void *handlers; } obj; /* zend.h:283 */
} ph96_zvalue_value;

typedef struct {
    ph96_zvalue_value value;                             /* zend.h:289 */
    uint32_t refcount;                                   /* zend.h:290 -> 0x10 */
    uint8_t type;                                        /* zend.h:291 -> 0x14 */
    uint8_t is_ref;                                      /* zend.h:292 */
} ph96_zval;

typedef char ph96_assert_value_16[(sizeof(ph96_zvalue_value) == 16) ? 1 : -1];
typedef char ph96_assert_refcount_10[
    (offsetof(ph96_zval, refcount) == 0x10) ? 1 : -1];
typedef char ph96_assert_type_14[(offsetof(ph96_zval, type) == 0x14) ? 1 : -1];

/* Z_TYPE_P, upstream's own numbering. The four the record can carry. */
static const uint8_t ph96_tytab[4] = {
    PH96_IS_NULL, PH96_IS_LONG, PH96_IS_BOOL, PH96_IS_STRING
};

/* =========================================================== the fold tags ==
 * The four handlers answer in four different ways -- a zval, nothing, an int,
 * nothing -- and the guarded NULL arm at `:389` answers with a fifth. The row's
 * `u64` is *the fold of what each handler did with the outcome*, so each lands
 * in it distinguishably. */
#define PH96_TAG_READ 0x11u
#define PH96_TAG_UNDEF 0x12u /* :389 -- the GUARD firing */
#define PH96_TAG_WRITE 0x13u
#define PH96_TAG_EXISTS 0x14u
#define PH96_TAG_UNSET 0x15u
#define PH96_TAG_CORE 0x16u /* zend_interfaces.c:86 -- E_CORE_ERROR */

/* ======================================================= _zval_ptr_dtor =====
 * zend_execute_API.c:384-396. THE FIRST STATEMENT IS THE DEREFERENCE, and there
 * is nothing in front of it.
 *
 * `zval_dtor` + `safe_free_zval_ptr` are PROJECTED onto a release tally: the
 * row declares `uses_allocator: false` and models no allocator, so the zval a
 * user method returns is a frame object rather than an `ALLOC_ZVAL`. ../spec.md
 * itemises the projection. */
static void ph96_zval_ptr_dtor(ph96_zval **zval_ptr, uint64_t *n_rel)
{
    (*zval_ptr)->refcount--;                                  /* :389 */
    if ((*zval_ptr)->refcount == 0) {                         /* :390 */
        (*n_rel)++;                     /* zval_dtor + safe_free_zval_ptr_rel */
    } else if ((*zval_ptr)->refcount == 1) {                  /* :393 */
        /* upstream's second arm, kept with its reason: a method return in this
         * row always arrives at refcount 1, so this arm is unreachable here --
         * it is reachable upstream whenever the value is also held elsewhere.
         * ../NOTES.md section 6. */
        (*zval_ptr)->is_ref = 0;                              /* :394 */
    }
}

/* ========================================================= i_zend_is_true ===
 * Zend/zend_execute.h:68-112, narrowed to the four type tags this row carries.
 * THE FIRST STATEMENT IS `switch (op->type)` -- the read at offset 0x14. */
static int ph96_is_true(const ph96_zval *op)
{
    int result;

    switch (op->type) {                                       /* :72 */
    case PH96_IS_NULL:
        result = 0;                                           /* :74 */
        break;
    case PH96_IS_LONG:
    case PH96_IS_BOOL:
        result = (op->value.lval ? 1 : 0);                    /* :79 */
        break;
    case PH96_IS_STRING:
        if (op->value.str.len == 0
            || (op->value.str.len == 1 && op->value.str.val[0] == '0')) {
            result = 0;                                       /* :87 */
        } else {
            result = 1;                                       /* :89 */
        }
        break;
    default:
        result = 0;                                           /* :108 */
        break;
    }
    return result;
}

/* ============================================ the value reaching the caller ==
 * `zend_std_read_dimension` RETURNS the zval to the VM. A `u64` kernel cannot
 * return a zval, so the row folds what the VM would go on to read: the type
 * tag, and for a string its whole `Z_STRLEN` bytes. ../spec.md itemises the
 * substitution. */
static uint64_t ph96_fold_zval(uint64_t acc, const ph96_zval *z)
{
    uint64_t a = acc * 31u + (uint64_t) z->type;
    if (z->type == PH96_IS_STRING) {
        int32_t i;
        for (i = 0; i < z->value.str.len; i++) {
            a = a * 31u + (uint64_t) z->value.str.val[i];
        }
        return a * 31u + 1u; /* the terminator, so "a" and "a\0b" differ */
    }
    return a * 31u + (uint64_t) (uint8_t) z->value.lval;
}

/* ============================================ zend_call_function, narrowed ===
 * zend_execute_API.c:537-874, narrowed to the three facts the row rests on.
 *
 *   :595  `*fci->retval_ptr_ptr = NULL` runs UNCONDITIONALLY and BEFORE every
 *         FAILURE return in the function (:667, :674, :679, ...), so the
 *         sentinel is guaranteed on both outcomes;
 *   :870  a pending exception is re-thrown and the function does NOT report it
 *         in its return value;
 *   :873  `return SUCCESS`.
 *
 * `slot` is the zval the user method would have returned -- an `ALLOC_ZVAL` in
 * PHP, a frame object here (../spec.md, `uses_allocator: false`). */
static int ph96_call_function(const uint8_t *b, ph96_zval *slot,
                              ph96_zval **retval_ptr_ptr)
{
    *retval_ptr_ptr = (ph96_zval *) 0;                        /* :595 */

    if (b[1] % 5u == 0u) {
        /* the early FAILURE returns -- :667, :674, :679. Note that :595 has
         * already run, so the out-parameter is the sentinel here too. */
        return PH96_FAILURE;
    }

    if (b[2] % 3u != 0u) {
        /* the user method returned a value: ZVAL_* + PZVAL_LOCK. */
        slot->type = ph96_tytab[b[3] % 4u];
        slot->refcount = 1;                        /* the caller's own hold */
        slot->is_ref = 0;
        if (slot->type == PH96_IS_STRING) {
            slot->value.str.val = b + 6;
            slot->value.str.len = (int32_t) (b[5] % (PH96_STRMAX + 1u));
        } else {
            slot->value.lval = (int64_t) b[4];
        }
        *retval_ptr_ptr = slot;
    }
    /* ...and if it did NOT, `*retval_ptr_ptr` is still the :595 sentinel. That
     * is the state zend_execute_API.c:592-594's comment names, and it is what
     * :870-873 below then reports as SUCCESS. */

    /* :870-872 -- EG(exception) is re-thrown, and the status does not say so. */
    return PH96_SUCCESS;                                      /* :873 */
}

/* ================================================ zend_call_method ==========
 * zend_interfaces.c:30-96. TWO CONTRACTS IN ONE FUNCTION, and the row is about
 * which one a call site picks.
 *
 *   :48  `fci.retval_ptr_ptr = retval_ptr_ptr ? retval_ptr_ptr : &retval;`
 *   :81  the STATUS IS TESTED -- E_CORE_ERROR, which does not return
 *   :88  `if (!retval_ptr_ptr) { if (retval) { zval_ptr_dtor(&retval); } ... }`
 *   :94  `return *retval_ptr_ptr;`
 *
 * `:89`'s `if (retval)` is the NULL test the `offsetunset` site omits, written
 * by the same hand in the function being called. ../NOTES.md section 4.
 *
 * `E_CORE_ERROR` terminates the request in PHP; the row PROJECTS that onto
 * *this call contributes a CORE tag and the consumer does not run*, the same
 * shape `common-php/emalloc_shim.h` uses for PHP's `exit(1)`. ../spec.md
 * itemises the projection. `core` is set when that arm is taken. */
static ph96_zval *ph96_call_method(const uint8_t *b, ph96_zval *slot,
                                   ph96_zval **retval_ptr_ptr,
                                   uint64_t *n_rel, int *core)
{
    int result;
    ph96_zval *retval;
    ph96_zval **target = retval_ptr_ptr ? retval_ptr_ptr : &retval;   /* :48 */

    result = ph96_call_function(b, slot, target);          /* :58 and :79 */

    if (result == PH96_FAILURE) {                               /* :81 */
        *core = 1;                     /* :86 zend_error(E_CORE_ERROR) */
        return (ph96_zval *) 0;
    }
    if (!retval_ptr_ptr) {                                      /* :88 */
        if (retval) {                                           /* :89 */
            ph96_zval_ptr_dtor(&retval, n_rel);                 /* :90 */
        }
        return (ph96_zval *) 0;                                 /* :92 */
    }
    return *retval_ptr_ptr;                                     /* :94 */
}

/* ================================================ zend_std_read_dimension ===
 * zend_object_handlers.c:378-400. SHAPE 0 -- the OUTPUT contract, GUARDED.
 *
 * `:385 if (!retval)` is the test `:513` omits, TWO LINES AFTER an identical
 * call. It is one of the two correct spellings in this file. */
static uint64_t ph96_read_dimension(const uint8_t *b, ph96_zval *slot,
                                    uint64_t acc, uint64_t *n_rel,
                                    uint64_t *n_core)
{
    ph96_zval *retval;                                          /* :381 */
    int core = 0;

    ph96_call_method(b, slot, &retval, n_rel, &core);            /* :384 */
    if (core) {
        (*n_core)++;
        return acc * 31u + PH96_TAG_CORE;
    }
    if (!retval) {                                              /* :385 */
        /* :386-388 -- with EG(exception) set, which is exactly the state that
         * put the sentinel here, the E_ERROR is NOT raised and the handler
         * answers quietly. */
        return acc * 31u + PH96_TAG_UNDEF;                      /* :389 */
    }
    acc = ph96_fold_zval(acc, retval);       /* :395 the zval reaches the VM */
    retval->refcount--;                      /* :393 Undo PZVAL_LOCK() */
    return acc * 31u + PH96_TAG_READ;
}

/* =============================================== zend_std_write_dimension ===
 * zend_object_handlers.c:403-417. SHAPE 1 -- the NO-OUTPUT contract.
 *
 * `:413` passes NULL for `retval_ptr_ptr`, 99 lines before `:512` passes
 * `&retval`. The contract that CANNOT be misused was already in this file, and
 * cf020f133487 is `:512` being changed into `:413`. */
static uint64_t ph96_write_dimension(const uint8_t *b, ph96_zval *slot,
                                     uint64_t acc, uint64_t *n_rel,
                                     uint64_t *n_core)
{
    int core = 0;

    /* :413 -- zend_call_method_with_2_params, retval_ptr_ptr == NULL */
    ph96_call_method(b, slot, (ph96_zval **) 0, n_rel, &core);
    if (core) {
        (*n_core)++;
        return acc * 31u + PH96_TAG_CORE;
    }
    return acc * 31u + PH96_TAG_WRITE;
}

/* ================================================= zend_std_has_dimension ===
 * zend_object_handlers.c:420-434. SHAPE 2 -- the OUTPUT contract, UNGUARDED,
 * and it dereferences the sentinel TWICE: `:428` reads `op->type` at 0x14 and
 * `:429` writes `(*zval_ptr)->refcount` at 0x10.
 *
 * THIS LIMB IS UPSTREAM'S, CHARACTER FOR CHARACTER, AND cf020f133487 DOES NOT
 * TOUCH IT. ../NOTES.md section 5 records what that means and the scope of the
 * claim; this comment points at it and states no verdict of its own
 * (PROTOCOL_PHP.md section F6a). */
static uint64_t ph96_has_dimension(const uint8_t *b, ph96_zval *slot,
                                   uint64_t acc, uint64_t *n_rel,
                                   uint64_t *n_core)
{
    ph96_zval *retval;                                          /* :423 */
    int result;                                                 /* :424 */
    int core = 0;

    ph96_call_method(b, slot, &retval, n_rel, &core);            /* :427 */
    if (core) {
        (*n_core)++;
        return acc * 31u + PH96_TAG_CORE;
    }
    result = ph96_is_true(retval);           /* :428 <- read at 0x14 */
    ph96_zval_ptr_dtor(&retval, n_rel);      /* :429 <- write at 0x10 */
    return acc * 31u + PH96_TAG_EXISTS + (uint64_t) result;      /* :430 */
}

/* =============================================== zend_std_unset_dimension ===
 * zend_object_handlers.c:506-517. SHAPE 3 -- THE ROW'S OWN SITE. The OUTPUT
 * contract, UNGUARDED, and `:513` is the whole of what stands between the
 * `:595` sentinel and `_zval_ptr_dtor`'s first statement. */
static uint64_t ph96_unset_dimension(const uint8_t *b, ph96_zval *slot,
                                     uint64_t acc, uint64_t *n_rel,
                                     uint64_t *n_core)
{
    /* cf020f133487 deletes `zval *retval;` here. */
    int core = 0;

    /* :512, with `&retval` replaced by NULL -- the NO-OUTPUT contract, which
     * `zend_interfaces.c:88-93` then discharges behind its own `if (retval)`
     * NULL test at `:89`. */
    ph96_call_method(b, slot, (ph96_zval **) 0, n_rel, &core);
    if (core) {
        (*n_core)++;
        return acc * 31u + PH96_TAG_CORE;
    }
    /* cf020f133487 deletes `zval_ptr_dtor(&retval);` here. */
    return acc * 31u + PH96_TAG_UNSET;
}

/* ================================================================ kernel ====
 * One window = one run of 16-byte call records. Each record is one
 * `$obj[...]` operation with its own handler, its own call status and its own
 * out-parameter outcome.
 *
 * The kernel allocates NOTHING: `slot` is a frame object and `ph96_tytab` is
 * static, so allocations per kernel call are ZERO, which satisfies
 * `PROTOCOL_PHP.md` section B1a's O(1) precondition with room to spare.
 * `provenance.uses_allocator` is `false` and says so. The `c/emalloc_shim.h`
 * symlink is carried anyway, because that rule is UNCONDITIONAL. */
SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t off, size_t len)
{
    const uint8_t *win = buf + off;
    size_t nrec = len / PH96_REC;
    uint64_t acc = 0;
    uint64_t n_rel = 0;
    uint64_t n_core = 0;
    ph96_zval slot;
    size_t r;

    for (r = 0; r < nrec; r++) {
        const uint8_t *b = win + r * PH96_REC;
        switch (b[0] % 4u) {
        case PH96_SHAPE_READ:
            acc = ph96_read_dimension(b, &slot, acc, &n_rel, &n_core);
            break;
        case PH96_SHAPE_WRITE:
            acc = ph96_write_dimension(b, &slot, acc, &n_rel, &n_core);
            break;
        case PH96_SHAPE_EXISTS:
            acc = ph96_has_dimension(b, &slot, acc, &n_rel, &n_core);
            break;
        default:
            acc = ph96_unset_dimension(b, &slot, acc, &n_rel, &n_core);
            break;
        }
    }

    return (acc * 31u + n_rel) * 31u + n_core;
}
