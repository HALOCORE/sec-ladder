#ifndef P22_KERNEL_H
#define P22_KERNEL_H

#include <stddef.h>
#include <stdint.h>

#include "driver.h" /* SLB_NOINLINE */

/* p22: open-addressing hash probe. **The first pattern in this tree whose bug
 * is not a memory-safety bug at all.**
 *
 * The kernel builds a fixed-capacity open-addressed table from the window's key
 * bytes and folds the slot each key lands in. Probing is linear:
 *
 *     while (tab[i] != EMPTY && tab[i] != k)     <<< THE PROBE LOOP
 *         i = (i + 1) % SLB_P22_TABCAP;
 *
 * Every access is `tab[i]` with `i` reduced modulo the capacity, so **every
 * access is in bounds, at every input, in every rung.** There is no bounds
 * check to omit, no lifetime to violate and no undefined behaviour anywhere in
 * this file. What the loop can do instead is **never return**: on a table with
 * no EMPTY slot left, a key that is not present makes the cursor walk the ring
 * for ever. That is a denial of service, it is a real shipped C bug, and it is
 * the whole of p22.
 *
 * **THE SAFETY LINE, and it is the ONE thing c/kernel.c omits:**
 *
 *     if (k != EMPTY && nfill < SLB_P22_TABCAP)      c/kernel_hardened.c
 *     if (k != EMPTY)                                c/kernel.c
 *
 * one conjunct, p27's shape. `nfill < TABCAP` is what guarantees an EMPTY slot
 * exists, and an EMPTY slot is what stops the probe.
 *
 *   window = buf[off .. off+len)
 *   nkey        = u32 LE at window byte 0        DECLARED. ATTACKER DATA.
 *   data_start  = 4
 *   every byte from data_start on is one key. Key 0 is the EMPTY sentinel and
 *   is not storable, so it folds SENT; every other byte value is a legal key
 *   and no input is malformed.
 *
 *   tab[TABCAP] = {EMPTY} ; nfill = 0 ; acc = 0 ; p = 4
 *   for t in 0 .. nkey:
 *       if len - p < 1:  break                   <<< SUBTRACTION-FIRST
 *       k = buf[off+p] ; p += 1
 *       if k != EMPTY && nfill < TABCAP:         <<< THE SAFETY LINE
 *           i = (k * 2654435761) / 16777216 % TABCAP
 *           while tab[i] != EMPTY && tab[i] != k:  i = (i + 1) % TABCAP
 *           if tab[i] == EMPTY:  tab[i] = k ; nfill += 1
 *           acc = acc*31 + i
 *       else:
 *           acc = acc*31 + SENT
 *   return acc*31 + nfill
 *
 * The hash is written `* 2654435761 / 16777216 % TABCAP` and never
 * `* 2654435761 >> 24 & 63`. The two are the same function on unsigned values
 * and lower to the same instructions, but only the first is linear arithmetic,
 * so ../verus.rs carries no `by (bit_vector)` anywhere (.memory/04-verus.md).
 *
 * `nkey` is DECLARED and bounds nothing: the `len - p < 1` guard is what stops
 * the walk, and it is written subtraction-first so it cannot wrap.
 *
 * Both C rungs take `buf_len` and both ignore it: p22's bound is the window's
 * and the table's, not the blob's. p47's, p12's, p06's, p14's, p10's, p27's and
 * p38's shape.
 *
 * Unsigned overflow wraps by definition in C (6.2.5p9), so `acc*31 + x` is the
 * wrapping operation ../spec.md asks for with no special spelling.
 *
 * The caller must guarantee `off + len <= buf_len`; that is the structural
 * precondition every rung shares and no rung checks (rung 5 proves it at the
 * call site instead). `nkey` and every key byte are attacker data and are the
 * kernel's problem. */

/* The table's extent. A property of the PROGRAM -- a fixed-capacity hash table
 * has a fixed number of slots -- and not of the input. In every rung and in
 * model.py. A power of two, so `% SLB_P22_TABCAP` lowers to a mask. */
#define SLB_P22_TABCAP 64

/* The EMPTY sentinel, and what a rejected key folds. In every rung. */
#define SLB_P22_EMPTY 0
#define SLB_P22_SENT 251

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len);

#endif /* P22_KERNEL_H */
