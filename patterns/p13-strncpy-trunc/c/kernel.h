#ifndef P13_KERNEL_H
#define P13_KERNEL_H

#include <stddef.h>
#include <stdint.h>

#include "driver.h" /* SLB_NOINLINE */

/* p13: `strncpy` truncation. One window holds a declared count of packed,
 * NUL-terminated strings; the kernel copies each of them into a fixed-size
 * local `dst[DST_CAP]` with **exact `strncpy(dst, src, sizeof dst)`
 * semantics**, then CONSUMES `dst` as a C string. CWE-170 / CWE-125.
 *
 *   window = buf[off .. off+len)
 *   nstr        = u32 LE at window byte 0        DECLARED. ATTACKER DATA.
 *   data_start  = 4
 *   strings follow, packed, each terminated by one 0 byte
 *
 *   dst[DST_CAP] ; acc = 0 ; p = 4
 *   for s in 0 .. nstr:
 *       q = first 0 byte at or after p, capped at len   <<< bounded in EVERY rung
 *       slen = q - p
 *       n = min(slen, DST_CAP)                          <<< strncpy's n
 *       for i in 0 .. n:        dst[i] = buf[off+p+i]   <<< strncpy copies
 *       for i in n .. DST_CAP:  dst[i] = 0              <<< strncpy ZERO-FILLS
 *       dst[DST_CAP - 1] = 0            <<< THE TERMINATION. R1 omits THIS LINE.
 *       d = 0 ; while dst[d] != 0: d++  <<< THE CONSUMER. Unbounded in C.
 *       acc = acc*31 + d                u64, wrapping
 *       acc = acc*31 + dst[0]
 *       if q >= len: break              <<< no terminator: the last string
 *       p = q + 1
 *       if p >= len: break
 *   return acc*31 + nstr
 *
 * **This is the first bug in this project that is a CORRECTLY-CALLED library
 * function.** `strncpy(dst, src, sizeof dst)` is textbook C, correct by the
 * letter of its man page, and still wrong: `strncpy` does not NUL-terminate
 * when the source is at least as long as `n`. Every other R1 here omits a line
 * a careful programmer would have written; this one omits a line the *library*
 * should have written and did not.
 *
 * **And the harm lands at a DIFFERENT SITE from the bug.** The truncating copy
 * is memory-safe -- it writes exactly `DST_CAP` bytes into a `DST_CAP`-byte
 * array, every time. The out-of-bounds access is a READ, it happens later, in
 * the consumer, and it is an overrun of the *destination* rather than of the
 * source. Every earlier pattern's bug fires where it is written.
 *
 * **The two harms, and they are at different expressiveness levels:**
 *
 *   TRUNCATION   -- a memory-safe WRONG ANSWER. `n = min(slen, DST_CAP)`
 *                   discards everything past `DST_CAP`, and the fold then sees
 *                   `d == DST_CAP - 1` for every string of `DST_CAP` bytes or
 *                   more. EVERY rung has it, R5 included. p17's shape.
 *   MISSING NUL  -- an OUT-OF-BOUNDS READ. Only R1 has it; the checked rungs
 *                   cannot express it. p12's shape.
 *
 * One omitted line produces both. Measured on this box at the gate's own flags
 * (`.temp/p13/phase0/`, one string of 40 bytes, 200 runs each):
 *
 *   gcc   -O0   d = 33 x200                 STABLE, 2 bytes past dst[31]
 *   gcc   -O3   d = 38 x186, 34 x3, 35 x2, 32 x9   NOT stable across runs
 *   clang -O0   d = 32 x200                 STABLE, 1 byte past
 *   clang -O3   d = 32 x200                 STABLE, 1 byte past
 *
 * so THREE OF THE FOUR C CELLS ARE SILENTLY AND REPEATABLY WRONG and one is
 * run-to-run variable. ASan reports `stack-buffer-overflow READ` on both
 * compilers; valgrind memcheck is BLIND to it, because the bytes past `dst[31]`
 * are initialised stack bytes of the same frame and V-bit tracking has nothing
 * to flag. ../NOTES.md 0.
 *
 * **The zero-fill is load-bearing and must not be "optimised" away.** It is
 * real `strncpy` semantics, it is why `dst` is written in FULL on every
 * iteration -- so no rung ever reads a byte the current iteration did not write
 * -- and it is why `strncpy`'s cost is O(DST_CAP) per string regardless of how
 * short the source is. ../NOTES.md 3 measures exactly that.
 *
 * **The scan is bounded by the window in every rung, R1 included**, exactly as
 * in p12: p11 already measured the unbounded *source* scan, and importing it
 * here would put two bugs in one kernel. `adversarial-nonul-src` is p11's
 * malformed record arriving through p13's bug -- the source scan stops
 * correctly at the window end and it is the DESTINATION scan that overruns.
 *
 * Two C rungs share this declaration:
 *
 *   c/kernel.c           R1  -- no termination store. THE BUG.
 *   c/kernel_hardened.c  R1h -- `dst[DST_CAP - 1] = 0;`, and that one line is
 *                               the whole difference.
 *
 * Both take `buf_len`, and both ignore it: p13's bound is not the source
 * buffer's length. The number the programmer needed was `sizeof dst - 1`.
 *
 * Unsigned overflow wraps by definition in C (6.2.5p9), so `acc*31 + d`,
 * `acc*31 + dst[0]` and the return expression are the wrapping operations
 * ../spec.md asks for with no special spelling.
 *
 * The caller must guarantee `off + len <= buf_len`; that is the structural
 * precondition every rung shares and no rung checks (rung 5 proves it at the
 * call site instead). `nstr` -- all 2^32 values of it -- and every byte of the
 * window are attacker data and are the kernel's problem. */
SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len);

#endif /* P13_KERNEL_H */
