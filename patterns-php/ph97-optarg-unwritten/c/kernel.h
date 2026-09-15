#ifndef PH97_KERNEL_H
#define PH97_KERNEL_H

#include <stddef.h>
#include <stdint.h>

#include "driver.h" /* SLB_NOINLINE */

/* ph97: PARSE a PHP 5.0.0 argument list against the type spec "|s", then run
 * `PHP_FUNCTION(mb_get_info)`'s selector chain over whatever the parser left in
 * `typ`, and fold the answers.
 *
 *   window = [24-byte call record][24-byte call record]...
 *
 *   the blob                     IS the call stream -- an ARGUMENT-PRESENCE
 *                                count, an argument TYPE TAG and the argument
 *                                bytes, per call
 *   zend_parse_parameters        "|s": the `|` makes the argument OPTIONAL
 *   mb_get_info's body           five `strcasecmp` arms plus an unmatched arm
 *   the u64                      fold of the selected settings' checksums and
 *                                the count of RETURN_FALSE outcomes
 *
 * Contract in ../spec.md. Two C rungs share this declaration:
 *
 *   c/kernel.c            R1  -- PHP 5.0.0 narrowed. THE BUG (CRASH-126).
 *   c/kernel_hardened.c   R1h -- the same file plus the ONE LINE of
 *                                f7326d627962 (Antony Dovgal, 2005-01-28,
 *                                "MFB: fix #31732").
 *
 * ============================================================================
 * ⭐⭐⭐ THE WHOLE MECHANISM IS FIVE FACTS AND THEY ARE ALL IN THE TARBALL
 * ============================================================================
 *   1  `mb_get_info` initialises its own out-parameter to NULL and leaves the
 *      length uninitialised beside it
 *
 *          char *typ = NULL;                        mbstring.c:3211
 *          int typ_len;                             mbstring.c:3212
 *
 *   2  it parses against a spec whose FIRST character is the optional marker
 *
 *          if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "|s",
 *                                    &typ, &typ_len) == FAILURE) {
 *              RETURN_FALSE;                        mbstring.c:3215-3217
 *
 *   3  `|` FIRST means `min_num_args` becomes the running `max_num_args`,
 *      which is still ZERO at that point
 *
 *          case '|':
 *              min_num_args = max_num_args;         zend_API.c:485-487
 *
 *   4  so a call with no arguments passes the count test
 *
 *          if (num_args < min_num_args || num_args > max_num_args) {
 *                                                   zend_API.c:511
 *
 *      and the loop that WRITES the out-parameters runs ZERO TIMES
 *
 *          while (num_args-- > 0) {                 zend_API.c:537
 *
 *      before `return SUCCESS` at :548.
 *
 *   5  ⛔ and the body reads `typ` with no test at all
 *
 *          if (!strcasecmp("all", typ)) {           mbstring.c:3219
 *
 * ▶ `mb_get_info()` with zero arguments -> SUCCESS -> `typ` keeps its :3211
 *   initialiser -> libc `strcasecmp` reads the second operand's first byte ->
 *   READ OF ADDRESS 0.
 *
 * ============================================================================
 * ⭐⭐ THE CLAIM, IN ONE SENTENCE
 * ============================================================================
 * THE GUARD IS PRESENT AND IT PASSES, AND IT ANSWERS A DIFFERENT QUESTION FROM
 * THE ONE THE CODE NEEDS ANSWERED. `:3215` tests *were the supplied arguments
 * well-typed?*; `:3219` needs *was the optional argument supplied?*. The real
 * test is `ZEND_NUM_ARGS()` or `typ != NULL`, and `f7326d627962` writes the
 * second of those.
 *
 * ⚠⚠ THE TWO QUESTIONS COME APART AT RUN TIME AND NOT ONLY ON PAPER. A
 * measured PHP 5.0.0 CLI answers `mb_get_info(null)` with `bool(false)` and
 * `mb_get_info()` with a SIGSEGV, because `zend_API.c:302-308`'s IS_NULL arm
 * writes `*p = NULL` only under the `!` modifier, which "|s" does not carry --
 * so the NULL VALUE becomes the empty string and only the ABSENT ARGUMENT
 * leaves `typ` at NULL. ../NOTES.md §1 has both runs.
 *
 * ⚠ `int typ_len;` at `:3212` is UNINITIALISED and is written only by the same
 * loop that never runs -- so the one call leaves TWO outputs unwritten. It is
 * NOT a second defect here, because nothing on the faulting path reads it, and
 * this kernel does not read it either. ../NOTES.md §3 records it as an
 * observation with that qualifier; it is `ph96`'s mechanism, one row over.
 *
 * ============================================================================
 * ⚠ WHAT THE KERNEL DOES *NOT* DO, AND WHY THAT IS THE ROW
 * ============================================================================
 * `ph97_get_info` does not test `typ`, does not consult the argument count a
 * second time, and does not ask the parser which out-parameters it wrote.
 * Adding any of those is `f7326d627962` or a variant of it, and adding one to
 * `c/kernel.c` would delete the row.
 *
 * The caller must guarantee `off + len <= buf_len` and `len >= PH97_REC`; that
 * is the structural precondition every rung shares and no rung checks (R5
 * proves it at the call site instead). Everything else -- every argument
 * count, every type tag, every byte of every argument -- is attacker data and
 * is the kernel's problem. */

/* ---- the record layout, identical in every rung and re-derived in model.py --
 *
 *   b[0]  argc_raw    -> num_args = b[0] % 3        ZEND_NUM_ARGS()
 *   b[1]  type_raw    -> type_tag = b[1] % 4        Z_TYPE_PP(arg)
 *   b[2]  len_raw     -> arg_len  = b[2] % 21       Z_STRLEN_PP(arg)
 *   b[3]  lval        -> the scalar the non-string conversions read
 *   b[4..24]          -> 20 bytes of Z_STRVAL_PP(arg)
 *
 * ⭐⭐ `argc_raw` AND `type_raw` ARE SEPARATE BYTES AND NEITHER IS DERIVED FROM
 * THE OTHER. *Was an argument supplied?* and *was it well-typed?* are two
 * propositions and the guard at `:3215` answers the second. ../spec.md
 * `idiom.required[0]` pins the independence, ../NOTES.md §14 argues why it is
 * the row, and `inputs/gen.py` asserts the corpus reaches every combination.
 * ⚠ This comment POINTS AT that argument and does not state its verdict --
 * every file under c/ is in the measurement digest, and a verdict frozen there
 * costs a 32-cell re-measure to repair (PROTOCOL_PHP.md §F6a). */
#define PH97_REC 24
#define PH97_STRMAX 20
/* one more than PH97_STRMAX: the NUL `convert_to_string_ex` materialises. */
#define PH97_BUFSZ 21

/* Z_TYPE_PP(arg), the four the "|s" arm of `zend_parse_arg` distinguishes --
 * zend_API.c:301-331. IS_LONG and IS_DOUBLE fall in with IS_STRING and are
 * deleted; IS_OBJECT and IS_RESOURCE fall in with IS_ARRAY and are deleted.
 * ../spec.md `provenance.divergences` itemises both. */
#define PH97_IS_NULL 0
#define PH97_IS_BOOL 1
#define PH97_IS_STRING 2
#define PH97_IS_ARRAY 3

#define PH97_SUCCESS 0
#define PH97_FAILURE (-1)

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t off, size_t len);

#endif /* PH97_KERNEL_H */
