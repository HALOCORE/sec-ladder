#ifndef P36_KERNEL_H
#define P36_KERNEL_H

#include <stddef.h>
#include <stdint.h>

#include "driver.h" /* SLB_NOINLINE */

/* p36: function-pointer table dispatch. **The first INDIRECT CALL in this
 * tree** -- 0 of 534 built kernel symbols across the other 21 patterns contains
 * a computed-target `call`, measured rather than asserted (../NOTES.md 0d).
 *
 * A one-byte bytecode. The window carries a declared record count and then a
 * stream of (opcode, operand) byte pairs; the interpreter dispatches each
 * opcode through a static table of function pointers and folds the result:
 *
 *     acc = TABLE[op](acc ^ arg);        <<< THE DISPATCH
 *
 * `c/kernel.c` omits `op < SLB_P36_NOPS` and therefore loads a code pointer
 * from past the end of `TABLE` and **calls it**. That is CWE-125 reaching
 * CWE-691: the harm is not a wrong value, it is a control transfer to an
 * address the input chose.
 *
 * ⚠ **SAY THE UNFLATTERING THING FIRST: the BUG CLASS is this tree's twelfth
 * `index >= len`.** p01, p02, p03, p05, p07, p11, p12, p13, p14, p16 and p17
 * are all *"an index or a length is not checked against a buffer"*, and so is
 * this. What is new is not the bug, it is four measured things about it
 * (../NOTES.md 0):
 *
 *   1. **the HARM is a control transfer**, and it is the only one here that is;
 *   2. **no checker on this box can see that.** UBSan reports
 *      `index 8 out of bounds for type '<unknown> *[8]'` and ASan reports
 *      `global-buffer-overflow ... 0 bytes after global variable 'TABLE'` --
 *      both name the ARRAY READ. The one checker that names a control transfer,
 *      clang's `-fsanitize=function`, is not in gcc 13.3.0 at all and is
 *      defeated here anyway (the loaded garbage is not a function, so its
 *      prologue-signature read faults first);
 *   3. **the indirect call is a cost mechanism nothing here has had**;
 *   4. **the pinned Verus cannot type this file's central declaration.**
 *      `const TABLE: [fn(u64) -> u64; 8]` is
 *      `error: The verifier does not yet support the following Rust feature:
 *      function pointer types`, so R2..R5 dispatch through
 *      `[&'static dyn Op; 8]` instead and C is the only rung that uses a bare
 *      function pointer. ../spec.md's `idiom.why` prices the difference.
 *
 * Window layout (../spec.md):
 *
 *     byte 0..4   nrec  u32 LE   DECLARED record count     ATTACKER DATA
 *     data_start = 4
 *     record t:   opcode byte at 4 + 2t, operand byte at 5 + 2t
 *
 *     NOPS = 8      the table's extent, a compile-time constant
 *     SENT = 251    what a rejected opcode folds
 *
 *     if len < 4:                       return 0
 *     nrec from the header
 *     if nrec == 0:                     return 0
 *     acc = 0 ; p = 4 ; t = 0
 *     while t < nrec:
 *         if len - p < 2:  break                  <<< subtraction-first
 *         op = buf[off+p] ; arg = buf[off+p+1] ; p += 2
 *         if op < NOPS:   acc = TABLE[op](acc ^ arg)     <<< THE SAFETY LINE
 *         else:           acc = acc*31 + SENT
 *         t += 1
 *     return acc*31 + t
 *
 * **THE EIGHT OPS ARE ONE ARITHMETIC OPERATION EACH, ON PURPOSE.** The finding
 * is the *call*, not the callee: an expensive callee would drown the dispatch
 * cost the pattern exists to measure. They are also uniform in shape -- one
 * 64-bit constant and one of `^`, `+`, `-` -- so that the `sweep-mix*` band can
 * hold the OPCODE MULTISET fixed and vary only its ORDER, which makes the
 * executed instruction count identical by construction while the indirect
 * branch goes from perfectly predicted to unpredictable.
 *
 * No shift, no mask and no `%` anywhere in the fold, so the specification stays
 * inside linear arithmetic plus constant-operand `^` (.memory/04-verus.md) and
 * ../verus.rs carries no `by (bit_vector)`.
 *
 * Both C rungs take `buf_len` and both ignore it: p36's bound is the window's
 * and the table's, not the blob's. p47's, p38's, p22's, p12's, p06's, p14's,
 * p10's and p27's shape.
 *
 * Unsigned overflow wraps by definition in C (6.2.5p9), so `acc*31 + x` is the
 * wrapping operation ../spec.md asks for with no special spelling.
 *
 * The caller must guarantee `off + len <= buf_len`; that is the structural
 * precondition every rung shares and no rung checks (rung 5 proves it at the
 * call site instead). `nrec`, every opcode and every operand are attacker data
 * and are the kernel's problem. */

/* The table's extent. A compile-time constant in every rung and in model.py:
 * a bytecode interpreter has a fixed number of opcodes. */
#define SLB_P36_NOPS 8

/* What a rejected opcode folds. A compile-time constant in every rung. */
#define SLB_P36_SENT 251

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len);

#endif /* P36_KERNEL_H */
