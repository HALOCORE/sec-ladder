#ifndef P03_KERNEL_H
#define P03_KERNEL_H

#include <stddef.h>
#include <stdint.h>

#include "driver.h" /* SLB_NOINLINE */

/* p03: a bounded stack driven by an attacker-chosen opcode stream. CWE-124
 * (buffer underwrite/underread) via a MISSING EMPTINESS CHECK -- the first
 * pattern in this project whose *operation sequence* is in the file rather than
 * in the code. See ../README.md and ../NOTES.md 0.
 *
 *   window = buf[off .. off+len)
 *   nops        = u32 LE at window byte 0        DECLARED. ATTACKER DATA.
 *   data_start  = 4
 *   avail       = len - 4                        what actually ARRIVED
 *   operations follow, 5 bytes each: op u8 (0 = PUSH, else POP), val u32 LE
 *   STACK_CAP   = 64                             a compile-time constant
 *
 *   uint64_t stack[STACK_CAP] ; sp = 0 ; acc = 0
 *   for k in 0 .. nops:
 *       op  = buf[off + 4 + 5*k]
 *       val = load_u32(off + 5 + 5*k)
 *       if op == 0:
 *           if sp < STACK_CAP: stack[sp] = val ; sp += 1   <<< THE PUSH GUARD,
 *                                                              in EVERY rung
 *       else:
 *           if sp > 0:                          <<< THE POP GUARD. R1 omits
 *               sp -= 1                             exactly this line.
 *               acc = acc*31 + stack[sp]
 *   return (acc*31 + sp)*31 + nops              u64, wrapping
 *
 * **The attacker chooses the control flow, not just the data.** Every earlier
 * kernel in this project has a fixed operation sequence with only the values
 * varying: p01/p02/p05/p16/p17 fold, p07 searches, p11 scans. Here the *file*
 * decides, per step, whether the kernel pushes or pops, which is what a
 * protocol state machine or a bytecode interpreter actually looks like, and it
 * is why the safety obligation is a loop invariant on `sp` that has to survive
 * a branch the attacker picks.
 *
 * **The index goes NEGATIVE, and on `size_t` that is `SIZE_MAX`.** p16 walks one
 * step past a length whose subtraction wrapped; p17 computes a
 * wrong-but-in-bounds index; p07 underflows an inclusive bound; p11's loop does
 * not stop. Here `sp - 1` at `sp == 0` is `SIZE_MAX`, and `stack + SIZE_MAX`
 * wraps to `stack - 1`: the read lands **8 bytes below the array, inside this
 * function's own stack frame**. ../NOTES.md 0 records that this is arithmetic
 * and not a guess, and ../NOTES.md 7 what each sanitiser does with it. Once
 * `sp == SIZE_MAX` the push guard `sp < STACK_CAP` is false for ever, so a
 * single stray POP disables the stack for the rest of the call and every later
 * POP walks one more slot DOWN the stack.
 *
 * **The PUSH guard is in every rung and the POP guard is not.** Overflow is not
 * the bug being modelled, and letting R1 overflow as well would confound the
 * two; `adversarial-overflow.bin` is the row where every rung including R1
 * agrees, and it is what makes that statement a measurement.
 *
 * Two C rungs share this declaration:
 *
 *   c/kernel.c           R1  -- no `if (sp > 0)`. THE BUG.
 *   c/kernel_hardened.c  R1h -- the same file with that one line.
 *
 * Both take `buf_len`, and that is the point: this API *has* the size, and the
 * bug is not about the size at all -- every buffer index in R1 is correct and
 * in range. What R1 gets wrong is a fact about its own local state.
 * R1-vs-R1h is therefore what the emptiness check costs inside one language
 * with the calling convention, the argument count and the register allocation
 * all held fixed (`.memory/02-bench-rules.md`, "The precondition must be
 * structural").
 *
 * Unsigned overflow wraps by definition in C (6.2.5p9), so `acc*31 + stack[sp]`
 * and `(acc*31 + sp)*31 + nops` are the wrapping operations ../spec.md asks for
 * with no special spelling. The only undefined behaviour this rung can execute
 * is the out-of-bounds read itself.
 *
 * `stack` is a fixed-size LOCAL array, not a `Vec` and not a heap allocation:
 * a growable stack moves the pattern to allocator behaviour, which is p02's
 * axis and not this one.
 *
 * The caller must guarantee `off + len <= buf_len`; that is the structural
 * precondition every rung shares and no rung checks (rung 5 proves it at the
 * call site instead). `nops` -- all 2^32 values of it -- and every byte of the
 * window are attacker data and are the kernel's problem. */
SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len);

#endif /* P03_KERNEL_H */
