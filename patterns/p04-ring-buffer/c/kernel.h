#ifndef P04_KERNEL_H
#define P04_KERNEL_H

#include <stddef.h>
#include <stdint.h>

#include "driver.h" /* SLB_NOINLINE */

/* p04: a bounded FIFO ring buffer driven by an attacker-chosen opcode stream.
 * CWE-787-shaped in intent and NOT in effect -- a MISSING FULLNESS CHECK whose
 * every index stays inside the array. See ../README.md and ../NOTES.md 0.
 *
 *   window = buf[off .. off+len)
 *   nops        = u32 LE at window byte 0        DECLARED. ATTACKER DATA.
 *   data_start  = 4
 *   avail       = len - 4                        what actually ARRIVED
 *   operations follow, 5 bytes each: op u8 (0 = PUSH, else POP), val u32 LE
 *   RING_CAP    = 64                             a compile-time constant,
 *                                                A POWER OF TWO
 *
 *   uint64_t ring[RING_CAP] ; head = 0 ; tail = 0 ; acc = 0
 *   for k in 0 .. nops:
 *       op  = buf[off + 4 + 5*k]
 *       val = load_u32(off + 5 + 5*k)
 *       if op == 0:
 *           if (tail + 1) % RING_CAP != head:   <<< THE FULLNESS CHECK. R1
 *               ring[tail] = val                    omits exactly this line.
 *               tail = (tail + 1) % RING_CAP
 *       else:
 *           if head != tail:                    <<< THE EMPTINESS CHECK, in
 *               acc = acc*31 + ring[head]           EVERY rung.
 *               head = (head + 1) % RING_CAP
 *   return ((acc*31 + head)*31 + tail)*31 + nops        u64, wrapping
 *
 * **THE INDEX IS MODULAR, and that is the pattern.** p05 asked whether the
 * optimiser carries a bound through a *multiply*; p09 through a *shift*; p04
 * asks through `%`. `RING_CAP` is a power of two, so the compiler sees a mask.
 * ../NOTES.md 1 measures where the bound falls, and ../controls/gen_controls.py
 * ships the `RING_CAP = 60` build that answers the same question when it is
 * not.
 *
 * **THE BUG STAYS IN BOUNDS, and that is the point.** Drop the fullness check
 * and a push onto a full ring stores into the one slot the checked kernel keeps
 * reserved and then advances `tail` onto `head` -- so the ring reads EMPTY and
 * all 63 live elements become unreachable. **Every index in this file is in
 * [0, RING_CAP) on every input**, in R1 as much as in R1h: `head` and `tail`
 * start at 0 and every update is `(x + 1) % RING_CAP`. There is no
 * out-of-bounds access to find, so ASan, UBSan, Miri, safe Rust's bounds check
 * and the memory-safety half of the R5 proof are all silent
 * (../NOTES.md 6, 7). What catches it is the checksum.
 *
 * That is what makes the bug realistic rather than a strawman: the programmer
 * writes the emptiness test because "pop an empty queue" is the case the type
 * makes them think about, and omits the fullness test because a ring buffer
 * "cannot overflow" -- its indices really cannot. The state can.
 *
 * Two C rungs share this declaration:
 *
 *   c/kernel.c           R1  -- no `(tail + 1) % RING_CAP != head`. THE BUG.
 *   c/kernel_hardened.c  R1h -- the same file with that one line.
 *
 * Both take `buf_len`, and that is the point: this API *has* the size, and the
 * bug is not about the size at all -- every buffer index in R1 is correct and
 * in range, and so is every ring index. What R1 gets wrong is a RELATION
 * between two of its own local variables. R1-vs-R1h is therefore what the
 * fullness check costs inside one language with the calling convention, the
 * argument count and the register allocation all held fixed
 * (`.memory/02-bench-rules.md`, "The precondition must be structural").
 *
 * Unsigned overflow wraps by definition in C (6.2.5p9), so `acc*31 + ring[head]`
 * and `((acc*31 + head)*31 + tail)*31 + nops` are the wrapping operations
 * ../spec.md asks for with no special spelling. **This rung executes no
 * undefined behaviour at all**, on any input, which is a first for a bug
 * pattern in this project.
 *
 * `ring` is a fixed-size LOCAL array, not a `VecDeque` and not a heap
 * allocation: a growable queue moves the pattern to allocator behaviour, which
 * is p02's axis and not this one, and it deletes the two explicit cursors that
 * the result folds and that the proof's invariant is about.
 *
 * The caller must guarantee `off + len <= buf_len`; that is the structural
 * precondition every rung shares and no rung checks (rung 5 proves it at the
 * call site instead). `nops` -- all 2^32 values of it -- and every byte of the
 * window are attacker data and are the kernel's problem. */
SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len);

#endif /* P04_KERNEL_H */
