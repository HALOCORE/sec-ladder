#ifndef PH56_KERNEL_H
#define PH56_KERNEL_H

#include <stddef.h>
#include <stdint.h>

#include "driver.h" /* SLB_NOINLINE */

/* ph56: COMPILE one PHP 5.0.0 fetch-list into an op_array, then EXECUTE it, and
 * fold what was emitted and what was executed.
 *
 *   window = [u64 record][u64 record]...    one STATEMENT per u64
 *
 *   the blob                     IS the record stream the parser hands the
 *                                compiler -- an operand kind, a base opcode and
 *                                an ACCESS MODE per statement
 *   zend_do_end_variable_parse   opline->opcode +/- a per-mode DELTA
 *   zend_do_isset_or_isempty     rewrites the LAST opline one more time
 *   execute()                    dispatches the emitted opcodes
 *   the u64                      fold of the emitted opcodes, the executed
 *                                opcodes and the final variable store
 *
 * Contract in ../spec.md. Two C rungs share this declaration:
 *
 *   c/kernel.c            R1  -- PHP 5.0.0 narrowed. THE BUG (CRASH-041).
 *   c/kernel_hardened.c   R1h -- the same file plus the THREE LINES of
 *                                1e708a5aeb30 (Marcus Boerger, 2004-08-29,
 *                                "Bugfix #29882 isset crashes on arrays").
 *                                `git apply` PLACES this one -- see
 *                                ../NOTES.md §5, and contrast ph55.
 *
 * ============================================================================
 * ⭐⭐⭐ THE WHOLE MECHANISM IS FIVE FACTS AND THEY ARE ALL IN THE TARBALL
 * ============================================================================
 *   1  the six fetch modes are SIX GROUPS OF THREE OPCODES AT A FIXED STRIDE,
 *      and upstream SHOUTS it -- quoted here without its comment delimiters,
 *      which a C comment cannot nest:
 *
 *          the following 18 opcodes are 6 groups of 3 opcodes each, and must
 *          remain in that order!                     zend_compile.h:636-638
 *
 *      ZEND_FETCH_DIM_R 81, _W 84, _RW 87, _IS 90, _FUNC_ARG 93, _UNSET 96.
 *
 *   2  the compiler therefore selects the mode by ARITHMETIC ON THE OPCODE
 *      VALUE -- `-= 3` / `+= 3` / `+= 6` / `+= 9` / `+= 12`, one arm each
 *      -- `zend_do_end_variable_parse`, zend_compile.c:751-776
 *
 *   3  ✅ TWO arms first REFUSE the append-dimension combination
 *      -- `if (opline->opcode == ZEND_FETCH_DIM_W && opline->op2.op_type ==
 *         IS_UNUSED) { zend_error(E_COMPILE_ERROR, ...); }`
 *         at :753-755 (BP_VAR_R) and :771-773 (BP_VAR_UNSET)
 *
 *   4  ⛔ `case BP_VAR_IS:` does not -- :763-765, three lines, no guard
 *
 *   5  and the LAST opline is then rewritten a SECOND time
 *      -- `case ZEND_FETCH_DIM_IS: last_op->opcode = ZEND_ISSET_ISEMPTY_DIM_OBJ;`
 *         `zend_do_isset_or_isempty`, zend_compile.c:3223-3231
 *
 * and the harm is three more:
 *
 *   6  `ZEND_ISSET_ISEMPTY_DIM_OBJ`'s handler reads op2 UNCONDITIONALLY
 *      -- `zval *offset = get_zval_ptr(&opline->op2, ...);`   :3961
 *   7  ⭐ `get_zval_ptr` RETURNS NULL for `IS_UNUSED`, deliberately and with
 *      its own case -- `case IS_UNUSED: *should_free = 0; return NULL;`
 *                                                         :118-121
 *   8  ⛔ and the handler dereferences it with no test
 *      -- `switch (offset->type) {`                          :3973
 *
 * ▶ `isset($a[])` -> BP_VAR_IS on a `ZEND_FETCH_DIM_W` whose op2 is IS_UNUSED
 *   -> `+= 6` makes it ZEND_FETCH_DIM_IS -> `zend_do_isset_or_isempty` rewrites
 *   it to ZEND_ISSET_ISEMPTY_DIM_OBJ -> that handler reads op2 -> NULL ->
 *   `offset->type` -> READ OF ADDRESS 0x14.
 *
 * ⚠⚠⚠ 0x14 IS NOT A GUESS. `offsetof(zval, type)` is 20 on this ABI, and a
 * pristine 5.0.0 CLI built from the pinned tarball faults at exactly
 * `SEGV on unknown address 0x000000000014` in
 * `zend_isset_isempty_dim_prop_obj_handler`. ../NOTES.md §1 has the run.
 *
 * ============================================================================
 * ⭐⭐ THE DETAIL THAT MAKES THIS THE SPECIMEN
 * ============================================================================
 * SIX arms; TWO carry the guard; FOUR do not. Only ONE of the four is a defect,
 * and which one is not deducible from the shape -- it took running all six:
 *
 *     BP_VAR_R        guarded          `$x = $a[];`      compile error
 *     BP_VAR_W        unguarded  ✅ LEGAL. `$a[] = 1;` is what [] is FOR
 *     BP_VAR_RW       unguarded  ✅ works, exit 0        `$a[] += 1;`
 *     BP_VAR_IS       unguarded  ⛔ SEGV                 `isset($a[]);`
 *     BP_VAR_FUNC_ARG unguarded  ⚠ reachable, silent     `f($a[]);`
 *     BP_VAR_UNSET    guarded          `unset($a[]);`    compile error
 *
 * ▶ THE SENTENCE THE CRASH COURSE WANTS: the guard is replicated by HAND onto
 *   the arms whose author happened to think of them, and the arithmetic that
 *   picks the opcode carries no record of which arms were considered.
 *
 * ⚠⚠ AND `BP_VAR_FUNC_ARG` IS A LIVE UNCAUGHT SIBLING WHOSE REACHABILITY IS
 * DECIDED BY DECLARATION ORDER. `zend_do_pass_param` (zend_compile.c:1411-1427)
 * asks `BP_VAR_R` when the callee is already declared and `BP_VAR_FUNC_ARG`
 * when it is not, so `f($a[]);` is a COMPILE ERROR or a SILENT ARRAY APPEND
 * depending on whether `function f` appears above or below the call. Measured
 * on the pristine CLI, both ways. ../NOTES.md §2 is the census; 1e708a5aeb30
 * did not touch it.
 *
 * ============================================================================
 * ⚠ WHAT THE KERNEL DOES *NOT* DO, AND WHY THAT IS THE ROW
 * ============================================================================
 * `zend_isset_isempty_dim_prop_obj_handler` reads `opline->op2` and then
 * dereferences the result, with nothing in between: no `if (offset)`, no
 * assertion that the opcode's operands are the ones its handler expects.
 * Adding either would be modelling a different program. What keeps the
 * executor safe in ordinary code is a COMPILE-TIME invariant -- *an opcode that
 * reads op2 is only ever emitted with op2 present* -- and the whole defect is
 * that one arm of one switch does not maintain it.
 *
 * The caller must guarantee `off + len <= buf_len`, `len >= 16` and
 * `len <= 8 * PH56_MAX_STMT`; that is the structural precondition every rung
 * shares and no rung checks (R5 proves it at the call site instead).
 * Everything else -- every mode byte, every operand kind, every slot index --
 * is attacker data and is the kernel's problem. */
SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t off, size_t len);

#endif /* PH56_KERNEL_H */
