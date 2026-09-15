#ifndef PH96_KERNEL_H
#define PH96_KERNEL_H

#include <stddef.h>
#include <stdint.h>

#include "driver.h" /* SLB_NOINLINE */

/* ph96: run PHP 5.0.0's `zend_call_method` helper and the FOUR `ArrayAccess`
 * handlers that call it, and fold what each of them does with the out-parameter
 * the helper wrote -- or did not write.
 *
 *   window = [16-byte call record][16-byte call record]...
 *
 *   the blob              IS the call-outcome stream -- a CONSUMER SHAPE, a
 *                         call STATUS and a WROTE-OUTPUT bit, each from its own
 *                         byte, plus the zval the method would have returned
 *   zend_call_function    writes `*fci->retval_ptr_ptr = NULL` at :595 and
 *                         returns SUCCESS at :873 whether or not anything
 *                         replaced it
 *   the four handlers     read_dimension / write_dimension / has_dimension /
 *                         unset_dimension -- zend_object_handlers.c
 *   the u64               fold of `(shape, status, wrote_out)` and of the value
 *                         each handler reads, plus the count of RELEASES and
 *                         the count of E_CORE_ERROR outcomes
 *
 * Contract in ../spec.md. Two C rungs share this declaration:
 *
 *   c/kernel.c            R1  -- PHP 5.0.0 narrowed. THE BUG (CRASH-061).
 *   c/kernel_hardened.c   R1h -- the same file plus the BACKPORT of
 *                                cf020f133487 (Marcus Boerger, 2005-03-19,
 *                                "- Fix #31185"): three lines at the
 *                                `offsetunset` site.
 *
 * ============================================================================
 * THE MECHANISM IS THREE FACTS AND THEY ARE ALL IN THE TARBALL
 * ============================================================================
 *   1  the callee NULLs the out-parameter ON PURPOSE, and says why. Upstream's
 *      own comment at zend_execute_API.c:592-594, quoted without its delimiters
 *      so that this file carries no nested comment opener:
 *
 *          we may return SUCCESS, and yet retval may be uninitialized,
 *          if there was an exception...                            :592-594
 *          *fci->retval_ptr_ptr = NULL;                            :595
 *
 *   2  and returns SUCCESS anyway, with the exception still pending
 *
 *          if (EG(exception)) {
 *              zend_throw_exception_internal(NULL TSRMLS_CC);
 *          }
 *          return SUCCESS;                      zend_execute_API.c:870-873
 *
 *   3  and the caller releases the out-parameter with no test of any kind
 *
 *          zval *retval;                        zend_object_handlers.c:509
 *          zend_call_method_with_1_params(&object, ce, NULL,
 *                       "offsetunset", &retval, offset);          :512
 *          zval_ptr_dtor(&retval);                                :513
 *
 *      and `_zval_ptr_dtor`'s first statement is
 *
 *          (*zval_ptr)->refcount--;             zend_execute_API.c:389
 *
 * ▶ A throwing `offsetUnset` -> SUCCESS -> `retval` is the `:595` sentinel ->
 *   the refcount decrement writes through address `offsetof(zval, refcount)`,
 *   which `Zend/zend.h:287-293` puts at 0x10 on LP64. The `_Static`-style
 *   assertions in `kernel.c` hold this file's own zval to those offsets, so the
 *   fault address is a BUILD-TIME property of the extraction rather than a
 *   coincidence of one run.
 *
 * ============================================================================
 * THE 2x2, AND BOTH CORRECT SPELLINGS ARE IN THE SAME FILE BY THE SAME AUTHOR
 * ============================================================================
 *   shape  handler                      site   contract          the test
 *   0      zend_std_read_dimension      :384   output, &retval   :385 if(!retval)
 *   1      zend_std_write_dimension     :413   NO-OUTPUT, NULL   vacuous
 *   2      zend_std_has_dimension       :427   output, &retval   NONE
 *   3      zend_std_unset_dimension     :512   output, &retval   NONE
 *
 * ../NOTES.md section 2 has the four-handler run against a PHP 5.0.0 CLI and
 * section 5 has the second limb's scope. This comment POINTS at those and
 * states no verdict of theirs: every file under c/ is in the measurement
 * digest and a verdict frozen there costs a re-measure to repair
 * (PROTOCOL_PHP.md section F6a).
 *
 * ============================================================================
 * WHAT THE KERNEL DOES *NOT* DO, AND WHY THAT IS THE ROW
 * ============================================================================
 * `ph96_unset_dimension` does not test `retval`, does not ask the helper what
 * it wrote, and does not look at the status the helper already consumed.
 * Adding any of those is cf020f133487 or the sibling spelling at `:385`, and
 * adding one to `c/kernel.c` would delete the row.
 *
 * The caller must guarantee `off + len <= buf_len`; that is the structural
 * precondition every rung shares and no rung checks (R5 proves it at the call
 * site instead). Everything else -- every shape, every status, every byte of
 * every returned value -- is attacker data and is the kernel's problem. */

/* ---- the record layout, identical in every rung and re-derived in model.py --
 *
 *   b[0]  shape_raw   -> shape  = b[0] % 4      which of the four handlers
 *   b[1]  stat_raw    -> failed = b[1] % 5 == 0 zend_call_function -> FAILURE
 *   b[2]  wrote_raw   -> wrote  = b[2] % 3 != 0 the user method returned a zval
 *   b[3]  ty_raw      -> Z_TYPE_P(retval) = PH96_TYTAB[b[3] % 4]
 *   b[4]  lval        -> Z_LVAL_P(retval)
 *   b[5]  len_raw     -> Z_STRLEN_P(retval) = b[5] % 11
 *   b[6..16]          -> 10 bytes of Z_STRVAL_P(retval)
 *
 * `stat_raw` AND `wrote_raw` ARE SEPARATE BYTES AND NEITHER IS DERIVED FROM
 * THE OTHER. *Did the call fail?* and *did it leave an output?* are two
 * propositions, and `zend_execute_API.c:592-594`'s comment is upstream saying
 * so in English. `shape_raw` is a third independent byte. ../spec.md
 * `idiom.required[0]` pins the independence, ../NOTES.md section 8 argues why it
 * is the row, and `inputs/gen.py` asserts the corpus reaches every combination
 * the benign domain admits. */
#define PH96_REC 16
#define PH96_STRMAX 10

/* Z_TYPE_P, upstream's own numbering -- Zend/zend.h:302-309. Four of the eight
 * are reachable here; ../spec.md `provenance.divergences` itemises the rest. */
#define PH96_IS_NULL 0
#define PH96_IS_LONG 1
#define PH96_IS_BOOL 3
#define PH96_IS_STRING 6

/* The four consumer shapes, in `zend_object_handlers.c`'s own file order. */
#define PH96_SHAPE_READ 0
#define PH96_SHAPE_WRITE 1
#define PH96_SHAPE_EXISTS 2
#define PH96_SHAPE_UNSET 3

#define PH96_SUCCESS 0
#define PH96_FAILURE (-1)

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t off, size_t len);

#endif /* PH96_KERNEL_H */
