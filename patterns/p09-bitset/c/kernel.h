#ifndef P09_KERNEL_H
#define P09_KERNEL_H

#include <stddef.h>
#include <stdint.h>

#include "driver.h" /* SLB_NOINLINE */

/* p09: a bitset probed by an attacker-chosen list of bit indices. CWE-125 via a
 * MISSING RANGE CHECK -- and the first pattern in this project whose safety
 * check is **not a bounds check**. See ../README.md and ../NOTES.md 0.
 *
 *   window = buf[off .. off+len)
 *   nbits       = u32 LE at window byte 0        DECLARED. ATTACKER DATA.
 *   nq          = u32 LE at window byte 4        DECLARED. ATTACKER DATA.
 *   data_start  = 8
 *   avail       = len - 8                        what actually ARRIVED
 *   nwords      = (nbits + 63) >> 6
 *   words   : nwords * 8 bytes at window byte 8            (u64 LE)
 *   queries : nq * 4 bytes after them                      (u32 LE bit indices)
 *
 *   acc = 0 ; hits = 0
 *   for k in 0 .. nq:
 *       q = load_u32(queries + 4*k)
 *       if q < nbits:                       <<< THE GUARD. R1 omits exactly
 *           w = load_u64(words + 8*(q>>6))      this line and nothing else.
 *           if w & (1 << (q & 63)): hits += 1
 *           acc = acc*31 + w
 *   acc = acc*31 + hits
 *   for i in 0 .. nwords:                   <<< THE POPCOUNT PASS. Separate
 *       acc = acc*31 + popcount(words[i])       from the query loop on purpose.
 *   return (acc*31 + nbits)*31 + nq         u64, wrapping
 *
 * **THE GUARD IS NOT A BOUNDS CHECK, AND THAT IS THE POINT.** Every earlier
 * pattern here guards a range that the access mentions: p16 `end - p >= 3`,
 * p17 `start < end`, p05 `i*ncol + j < avail`, p07 `lo < hi`, p11 `q < len`,
 * p03 `sp > 0` / `sp < STACK_CAP`. p09 guards `q < nbits` -- a bound on the
 * **bit** index -- and then accesses `words[q >> 6]`, a **word** index. The
 * fact the access needs, `q >> 6 < nwords`, is derived from the guard *through
 * a shift*, and neither the guard nor the array length appears in it directly.
 * That is p05's question on a different operator; ../NOTES.md 4 measures what
 * each middle-end does with it.
 *
 * **TWO BUGS, AND ONLY ONE OF THEM IS A MEMORY ERROR.**
 *
 *   c/kernel.c           R1  -- no `if (q < nbits)`. A SPATIAL bug: `q >> 6`
 *                              walks off the word array. ASan fires.
 *   c/kernel_hardened.c  R1h -- the same file with that one line.
 *
 * The second bug is not a rung at all, it is a one-character edit built as a
 * control (../NOTES.md 6): spell the mask `q & 31` instead of `q & 63` and the
 * index stays in range, every rung returns the **same wrong answer**, and no
 * sanitiser, no bounds check and no memory-safety proof says anything. Only
 * `model.py` and the functional `ensures` catch it. ../NOTES.md 6 also measures
 * the OTHER one-character edit the task file proposed, `q >> 5`, and reports
 * that it is **not** in that class: `q >> 5 = q/32 >= q/64`, so it is a second
 * spatial bug and R5 rejects it on the accessor's precondition alone.
 *
 * Both C rungs take `buf_len` and both ignore it, exactly as in p03 and p11:
 * the API *has* the size, and in R1h every buffer index is correct without it.
 * R1-vs-R1h is therefore what the range check costs inside one language with
 * the calling convention, the argument count and the register allocation all
 * held fixed (`.memory/02-bench-rules.md`, "The precondition must be
 * structural").
 *
 * Unsigned overflow wraps by definition in C (6.2.5p9), so every `acc*31 + x`
 * here is the wrapping operation ../spec.md asks for with no special spelling.
 * The only undefined behaviour R1 can execute is the out-of-bounds read itself.
 *
 * The caller must guarantee `off + len <= buf_len`; that is the structural
 * precondition every rung shares and no rung checks (rung 5 proves it at the
 * call site instead). `nbits`, `nq` -- all 2^32 values of each -- and every
 * query word are attacker data and are the kernel's problem. */
SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len);

#endif /* P09_KERNEL_H */
