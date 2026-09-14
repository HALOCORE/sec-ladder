#ifndef PH55_KERNEL_H
#define PH55_KERNEL_H

#include <stddef.h>
#include <stdint.h>

#include "driver.h" /* SLB_NOINLINE */

/* ph55: run one op_array's worth of PHP 5.0.0's executor and fold what it
 * executed.
 *
 *   window = [u64 op][u64 op]...          one instruction WORD per u64
 *
 *   the blob                     IS the instruction stream (op_array->opcodes)
 *   pass_two                     opline->handler = zend_opcode_handlers[opcode]
 *   execute()'s loop             while (1) { if (EX(opline)->handler(...)) ... }
 *   the u64                      fold of the executed opcodes and the final
 *                                variable store
 *
 * Contract in ../spec.md. Two C rungs share this declaration:
 *
 *   c/kernel.c            R1  -- PHP 5.0.0 narrowed. THE BUG (CRASH-023).
 *   c/kernel_hardened.c   R1h -- the same file plus the THREE LINES of
 *                                4f68f3774c34 (Stanislav Malyshev,
 *                                2004-08-30, "fix crash #29893"), HAND
 *                                BACKPORTED: the commit is against 2004-08-30
 *                                HEAD and does not apply to 5.0.0.
 *                                See ../NOTES.md §5.
 *
 * ============================================================================
 * ⭐⭐⭐ THE WHOLE MECHANISM IS FIVE FACTS AND THEY ARE ALL IN THE TARBALL
 * ============================================================================
 *   1  a compound assignment to an array dimension is a TWO-WORD instruction
 *      -- `zend_op *op_data = opline+1;`            zend_execute.c:1742
 *   2  the handler records that in a LOCAL FLAG at run time
 *      -- `zend_bool increment_opline = 0;` :1728, `= 1;` only on the
 *         ZEND_ASSIGN_DIM arm at :1749
 *   3  ⛔ the ERROR exit does not consult the flag
 *      -- `if (*var_ptr == EG(error_zval_ptr)) { ...; NEXT_OPCODE(); }`
 *         :1765-1770, the NEXT_OPCODE() at :1769
 *   4  ✅ the NORMAL exit does
 *      -- `if (increment_opline) { INC_OPCODE(); } NEXT_OPCODE();`  :1792-1795
 *   5  `NEXT_OPCODE()` is stride 1 AND returns; `INC_OPCODE()` is a CONDITIONAL
 *      extra ++ with no return                     :1317-1320, :1326-1330
 *
 * and the harm is four more:
 *
 *   6  `ZEND_API opcode_handler_t zend_opcode_handlers[512];`      :1338
 *   7  ⭐ `zend_opcode_handlers[ZEND_OP_DATA] = NULL;`             :4427
 *   8  pass_two copies the table into EVERY instruction
 *      -- `opline->handler = zend_opcode_handlers[opline->opcode];`
 *                                                  zend_opcode.c:363
 *   9  ⛔ the executor dispatches through that field with NO NULL CHECK
 *      -- `if (EX(opline)->handler(...)) { return; }`  :1383-1394
 *
 * ▶ error arm -> PC strides 1 -> the PC lands on the trailing ZEND_OP_DATA
 *   word -> that word's `handler` field is NULL -> unconditional indirect call
 *   through NULL.
 *
 * ============================================================================
 * ⭐⭐ THE DETAIL THAT MAKES THIS THE SPECIMEN
 * ============================================================================
 * `INC_OPCODE()` has FOUR call sites in 5.0.0 -- :1719, :1793, :2193, :2224 --
 * and THREE of them are unconditional `INC_OPCODE(); NEXT_OPCODE();`, because
 * those handlers are STATICALLY two-word. Two of the three carry a shouting
 * comment in the original -- quoted here without its comment delimiters, which
 * a C comment cannot nest:
 *
 *     assign_obj has two opcodes!                 :2192
 *     assign_dim has two opcodes!                 :2223
 *
 * `zend_binary_assign_op_helper` is the ONLY one of the four whose instruction
 * width is DATA-DEPENDENT -- it dispatches on `opline->extended_value` and is
 * one-word for `default`, two-word for `ZEND_ASSIGN_DIM`. That is why it needs
 * a flag, and it is the one with the bug.
 *
 * ▶ THE SENTENCE THE CRASH COURSE WANTS: the codebase SHOUTS the invariant at
 *   the two sites that get it right, and is SILENT at the site where the
 *   invariant became conditional.
 *
 * This kernel carries ONE of the clean siblings -- `zend_assign_dim_handler`
 * (:2198-2226), opcode PH55_ASSIGN_DIM -- so the contrast is inside the
 * measured program and not only in this comment. Both siblings were read and
 * are CLEAN: each has exactly one exit. No sibling site is owed.
 *
 * ============================================================================
 * ⚠ WHAT THE KERNEL DOES *NOT* DO, AND WHY THAT IS THE ROW
 * ============================================================================
 * `execute()`'s loop is `while (1) { ... if (EX(opline)->handler(...)) }` and
 * there is NOTHING between `EX(opline)` and the call: no bound on the PC, no
 * test of the handler against NULL, no assertion that the PC is an instruction
 * start. Adding any of those would be modelling a different program. The PC is
 * kept inside the op_array by a STRUCTURAL invariant instead, and it is PHP's
 * own: every op_array ends with `ZEND_RETURN` followed by
 * `ZEND_HANDLE_EXCEPTION` (`zend_do_end_function_declaration`,
 * zend_compile.c:1088-1092), so a PC that reaches the tail stops. Two
 * terminator words and a maximum stride of two is what makes that airtight --
 * ../NOTES.md §4 has the argument.
 *
 * The caller must guarantee `off + len <= buf_len`, `len >= 16` and
 * `len <= 8 * PH55_MAX_OPS`; that is the structural precondition every rung
 * shares and no rung checks (R5 proves it at the call site instead).
 * Everything else -- every opcode byte, every operand, every extended_value --
 * is attacker data and is the kernel's problem. */
SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t off, size_t len);

#endif /* PH55_KERNEL_H */
