#ifndef P27_KERNEL_H
#define P27_KERNEL_H

#include <stddef.h>
#include <stdint.h>

#include "driver.h" /* SLB_NOINLINE */

/* p27: a handle table over individually allocated records, driven by an op
 * stream from the file. **The one TEMPORAL bug class in this project** -- every
 * other pattern's bug is spatial (an index outside an allocation) or logical (a
 * wrong answer inside one). Here the address is inside no live allocation at
 * all, because the record it named was freed.
 *
 *   window = buf[off .. off+len)
 *   nops        = u32 LE at window byte 0        DECLARED. ATTACKER DATA.
 *   data_start  = 4
 *   op          = 2 bytes: c = opcode byte, a = operand byte   ALL ATTACKER DATA
 *   TABCAP = 32    the handle table's extent     a compile-time constant
 *   RECSZ  = 1     one record, one allocation    a compile-time constant
 *   SENT   = 251   what a rejected op folds      a compile-time constant
 *
 *   uint8_t *tab[TABCAP] = {0} ; uint8_t live[TABCAP] = {0}
 *   ntab = 0 ; acc = 0 ; p = 4
 *   for o in 0 .. nops:
 *       if len - p < 2: break
 *       c = buf[off+p] ; a = buf[off+p+1] ; p += 2 ; h = a
 *       switch c % 4:
 *         0 OPEN : if ntab < TABCAP: q = malloc(RECSZ) ; *q = a
 *                                    tab[ntab] = q ; live[ntab] = 1 ; ntab++
 *                                    acc = acc*31 + a
 *                  else:              acc = acc*31 + SENT
 *         1 CLOSE: if h < ntab && live[h]: free(tab[h]) ; live[h] = 0
 *                                    acc = acc*31 + 1
 *                  else:              acc = acc*31 + SENT
 *         2,3 READ:
 *                  if h < ntab && live[h]:  <<< THE SAFETY LINE. R1 omits the
 *                                    acc = acc*31 + *tab[h]   second conjunct.
 *                  else:              acc = acc*31 + SENT
 *   for j in 0 .. ntab: if live[j]: free(tab[j]) ; live[j] = 0
 *   return acc*31 + ntab
 *
 * **THE HANDLE IS AN INTEGER, and that is what makes the bug unavoidable in C.**
 * The op stream comes out of a file, so the only thing an operation can name is
 * a slot number. "Set the pointer to NULL when you free it" is therefore not a
 * defence: the read does not have the pointer, it has an index, and something
 * must tell it whether the record behind that index is still there. `live[]` is
 * that something -- a generation counter degenerated to one bit, because slots
 * are never reused (`ntab` only grows). Every real handle table carries the same
 * field for the same reason.
 *
 * **THE FREE IS A REAL `free`.** Not a freelist push into a slab: `tab[h]` after
 * a CLOSE points into no live allocation, so the stale read in R1 is a genuine
 * use-after-free -- ASan and Miri both see it, and `PointsTo` cannot license it.
 * A slab-and-freelist spelling would put the stale read inside a live
 * allocation, which is p17's LOGICAL class and not this one. ../spec.md pins it.
 *
 * **THE HARM IS DISCLOSURE, and it needs the chunk to be RECYCLED.** glibc's
 * tcache is LIFO, so the OPEN that follows a CLOSE gets the same chunk back.
 * A READ of the closed slot then returns the *newer* record's byte -- one
 * record's contents delivered under another record's handle. `adversarial-uaf`
 * is exactly that shape. This is why the adversarial inputs recycle before they
 * read: a stale read of a chunk that is still in the tcache returns glibc's own
 * safe-linked `next` pointer, which is ASLR-dependent and therefore not a
 * measurement.
 *
 * **What this rung KEEPS is as important as what it drops.** It keeps the slot
 * bound `h < ntab`, so the table read is in bounds and the bug is not spatial;
 * it keeps `live[]` and maintains it, so CLOSE is idempotent and neither rung
 * can double-free; it keeps the capacity guard `ntab < TABCAP`, so the table
 * never overflows; it keeps the epilogue, so neither rung leaks. The only thing
 * missing is the one conjunct that asks whether the record is still alive.
 *
 * The guard is written subtraction-first (`len - p < 2`) rather than additively
 * (`p + 2 > len`) in all seven rungs, for p07's, p14's and p13's reason:
 * `p <= len` is maintained by the guard itself so the subtraction cannot wrap,
 * while the additive form can overflow and Verus rejects it.
 *
 * Two C rungs share this declaration:
 *
 *   c/kernel.c           R1  -- no liveness test on the READ path. THE BUG.
 *   c/kernel_hardened.c  R1h -- `&& live[h] == 1` on the READ path, and that one
 *                               conjunct is the whole difference.
 *
 * Both take `buf_len` and both ignore it: p27's bound is not the source
 * buffer's length. p12's, p06's and p14's shape.
 *
 * **The kernel must not mutate `buf`.** The driver calls it `n_iters` times and
 * every call must return the same value; every allocation this kernel makes is
 * also freed by it before it returns, so call *i+1* starts from the same
 * allocator state call *i* did. That is what makes a kernel that allocates legal
 * in this benchmark at all, and ../NOTES.md 0b measures that it holds.
 *
 * Unsigned overflow wraps by definition in C (6.2.5p9), so `acc*31 + x` is the
 * wrapping operation ../spec.md asks for with no special spelling. The only
 * undefined behaviour this rung can execute is the LOAD through a dangling
 * `tab[h]`.
 *
 * The caller must guarantee `off + len <= buf_len`; that is the structural
 * precondition every rung shares and no rung checks (rung 5 proves it at the
 * call site instead). `nops`, every opcode byte and every operand byte are
 * attacker data and are the kernel's problem. */
SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len);

#endif /* P27_KERNEL_H */
