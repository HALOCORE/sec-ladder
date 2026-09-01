#ifndef P49_KERNEL_H
#define P49_KERNEL_H

#include <stddef.h>
#include <stdint.h>

#include "driver.h" /* SLB_NOINLINE */

/* p49: an INTERNED / DEDUPLICATED STRING POOL WITH IN-PLACE MUTATION, driven by
 * an op stream from the file. The C mechanism is `CVE-2022-40304`'s, admitted at
 * `TASK_143` and re-adjudicated and upheld at `TASK_160` by running it.
 *
 *   window = buf[off .. off+len)
 *   nops        = u32 LE at window byte 0        DECLARED. ATTACKER DATA.
 *   data_start  = 4
 *   op          = 2 bytes: c = opcode byte, a = operand byte   ALL ATTACKER DATA
 *   MEM    = 64    the pool, ONE byte array      a compile-time constant
 *   ARENA  = 20    mem[0 .. 20)  the INTERNING arena, SHARED
 *                  mem[20 .. 64) the PRIVATE region, OWNED
 *   NENT   = 8     intern-table entries          a compile-time constant
 *   NREC   = 12    records per window            a compile-time constant
 *   NKEY   = 7     key    = a % NKEY             a compile-time constant
 *   MAXW   = 6     width  = 1 + a % MAXW         a compile-time constant
 *   THRESH = 4     the INLINE_THRESHOLD          a compile-time constant
 *   SENT   = 251   what a rejected op folds      a compile-time constant
 *
 * THE C MECHANISM, AND WHY IT IS A SHAPE NO BUILT ROW HAS
 * ------------------------------------------------------
 * A record's content is `w` bytes, `w` derived from the operand. Content
 * SHORTER than `THRESH` is **INTERNED**: the pool looks the string up in a
 * dedup table and, on a hit, the new record BORROWS the buffer the earlier
 * record already holds. Two records then legitimately name ONE buffer. That is
 * correct, it is intended, it is what an intern pool is for, and **it is not
 * undefined behaviour in any way**. Content at or above the threshold is copied
 * into the record's own private storage and is OWNED.
 *
 * The cycle-breaker, `BREAK`, then zeroes the first byte of a record's content:
 *
 *     mem[roff[t]] = 0;          <<< THE WRITE THROUGH THE ALIAS
 *
 * and in `c/kernel.c` it does that **whether or not the buffer is the record's
 * to write**. When it is not, the other record's value silently changes, and so
 * does the arena copy that the dedup table hands to every LATER record with the
 * same content -- the port's downstream hash-key corruption.
 *
 * ⚠⚠ **NOTHING IS EVER FREED, NOTHING IS EVER ALLOCATED, EVERY INDEX IS INSIDE
 * `mem[0 .. MEM)`, AND NO POINTER DANGLES.** `c/kernel.c` executes NO undefined
 * behaviour of any kind, so ASan, UBSan and Miri are silent on every input
 * including the adversarial ones, at both optimisation levels on both
 * compilers. **The checksum is the only instrument this row has**, which is why
 * `../model.py` carries the whole result and ships a must-fire detector arm.
 * ✅ That is the exact INVERSE of `p34`'s detector-only cell, where the two
 * rungs' checksums are bit-identical and ASan is the only discriminator. The
 * two rows bracket *which instrument sees the harm* from opposite ends.
 *
 *   uint8_t mem[MEM]
 *   uint8_t ekey[NENT], elen[NENT], eoff[NENT]      the dedup table
 *   uint8_t roff[NREC], rlen[NREC], rshd[NREC]      the records
 *   nent = 0 ; nrec = 0 ; abump = 0 ; pbump = ARENA ; acc = 0 ; p = 4
 *   for o in 0 .. nops:
 *       if len - p < 2: break
 *       c = buf[off+p] ; a = buf[off+p+1] ; p += 2
 *       w = 1 + a % MAXW ; key = a % NKEY
 *       switch c % 4:
 *         0,1 DEFINE: if nrec == NREC:            v = SENT
 *                     elif w < THRESH:                       <<< THE THRESHOLD
 *                         f = find(ekey, elen, nent, key, w)
 *                         if f == nent:                      a dedup MISS
 *                             if nent == NENT or abump + w > ARENA: v = SENT
 *                             else: fill(mem, abump, key, w)
 *                                   ekey[nent]=key ; elen[nent]=w ; eoff[nent]=abump
 *                                   roff[nrec]=abump ; rlen[nrec]=w ; rshd[nrec]=1
 *                                   nent += 1 ; abump += w ; nrec += 1 ; v = a
 *                         else:                              a dedup HIT
 *                             roff[nrec]=eoff[f] ; rlen[nrec]=w ; rshd[nrec]=1
 *                             nrec += 1 ; v = a       <<< THE ALIAS IS CREATED,
 *                                                         AND IT IS CORRECT
 *                     else:
 *                         if pbump + w > MEM: v = SENT
 *                         else: fill(mem, pbump, key, w)
 *                               roff[nrec]=pbump ; rlen[nrec]=w ; rshd[nrec]=0
 *                               pbump += w ; nrec += 1 ; v = a
 *         2   BREAK : if nrec == 0: v = SENT
 *                     else: t = a % nrec
 *                           <<< THE SAFETY LINE GOES HERE -- see below >>>
 *                           mem[roff[t]] = 0 ; v = 2
 *         3   READ  : if nrec == 0: v = SENT
 *                     else: t = a % nrec ; v = fold(mem, roff[t], rlen[t], 0)
 *       acc = acc*31 + v
 *   for t in 0 .. nrec:
 *       acc = fold(mem, roff[t], rlen[t], acc)
 *       acc = acc*31 + rshd[t]
 *   return acc*31 + nrec
 *
 * THE SAFETY LINE IS `cow`, AND IT IS NOT THE UPSTREAM PATCH
 * ---------------------------------------------------------
 * `c/kernel_hardened.c` un-shares before writing -- copy-on-write:
 *
 *     if (rshd[t]) {                                   the OWNERSHIP question
 *         if (pbump + rlen[t] > P49_MEM) {
 *             v = P49_SENT;                            cannot un-share: REFUSE
 *         } else {
 *             for (j = 0; j < rlen[t]; j++)            take a private copy
 *                 mem[pbump + j] = mem[roff[t] + j];
 *             roff[t] = pbump; rshd[t] = 0; pbump += rlen[t];
 *             mem[roff[t]] = 0; v = 2;
 *         }
 *     } else { mem[roff[t]] = 0; v = 2; }
 *
 * and that whole block, at that ONE site, is the entire difference between the
 * two cells. `../controls/safety_line.py` preprocesses both shipped files and
 * diffs them, so the claim is measured rather than asserted.
 *
 * ⚠ **UPSTREAM'S PATCH (commit `644a89e`) IS THE OTHER SPELLING AND IT IS NOT
 * THE SAFETY LINE HERE.** Upstream fixes the PROVENANCE -- never borrow, always
 * own -- which deletes the deduplication. `TASK_160` measured that it CHANGES A
 * BENIGN OBSERVABLE in the port (`9 passed, 1 failed`; `"interned":true` ->
 * `false`) while copy-on-write is byte-identical to the bug on benign input.
 * The same thing is true here and it is measured, not inherited:
 * `../controls/spellings.py` builds the provenance arm and prices it, and the
 * epilogue's `acc*31 + rshd[t]` is this kernel's reduction of the port's
 * `"interned"` field -- which is exactly the observable upstream moves.
 * ⚠ **An upstream patch is not automatically a safety line; check it against
 * the benign observable.**
 *
 * WHY THE COPY-ON-WRITE ARM CAN REFUSE, AND WHY THAT IS NOT A HOLE
 * ---------------------------------------------------------------
 * Un-sharing needs storage the bug does not need. When the private region is
 * exhausted, R1h folds SENT and does not write at all -- so the hardened rung is
 * memory-safe AND value-safe on every input, and the price of the repair
 * includes a REFUSAL path that the buggy rung does not have. That is a real
 * property of copy-on-write as a repair, and `../NOTES.md` 3c measures how often
 * it fires. **A repair that consumes a resource can run out of it.**
 *
 * WHY EVERY INDEX IS IN BOUNDS IN BOTH RUNGS
 * -----------------------------------------
 *   * `w` is `1 + a % MAXW`, so `1 <= w <= MAXW = 6`.
 *   * an interned buffer is only ever created under `abump + w <= ARENA`, so
 *     `roff[t] + rlen[t] <= ARENA` for every shared record;
 *   * a private buffer is only ever created under `pbump + w <= MEM`, so
 *     `roff[t] + rlen[t] <= MEM` for every owned record;
 *   * `t = a % nrec` runs only under `nrec > 0` and `nrec <= NREC`;
 *   * `f = find(...)` returns a value in `0 ..= nent` and is dereferenced only
 *     under `f != nent`, i.e. `f < nent <= NENT`.
 * So `mem[roff[t]] = 0` and every `mem[base + j]` is inside the array in every
 * run of BOTH rungs. **R1's harm is a wrong VALUE and nothing else.**
 *
 * WHY THE DEDUP TABLE IS INSIDE THE KERNEL
 * ---------------------------------------
 * `p27`'s stated precedent -- *a file cannot name a pointer, but it CAN name an
 * operation that saves one* -- and `p32`'s pool restated. The file names a
 * CONTENT (through `key` and `w`), never a buffer and never an offset, so the
 * sharing is something the KERNEL decides and the attacker only provokes.
 * `TASK_160` §4 established by reduction that a `kernel(buf, off, len) -> u64`
 * signature does not lose the deduplication, which was the signature question.
 *
 * WHY THIS IS NOT `p08`, THE ROW A READER WILL REACH FOR FIRST
 * -----------------------------------------------------------
 * `p08` is `memcpy` where `memmove` is required: ONE library call whose source
 * and destination ranges overlap. The overlap exists only for the duration of
 * that call, it is UNDEFINED BEHAVIOUR (C11 7.24.2.1p2), it is created by an
 * arithmetic accident (`2*dr < m`), there is no second referent and no ownership
 * structure anywhere in the program, and the repair is A DIFFERENT FUNCTION.
 * Here the sharing is created deliberately by a dedup table, is CORRECT and is
 * not undefined behaviour at all, persists across many operations, and the
 * repair is an OWNERSHIP TEST BEFORE A WRITE. ⚠ **And this kernel contains no
 * overlapping copy at all**: `../controls/no_overlap.py` re-derives, over every
 * shipped window, that every copy's source and destination ranges are DISJOINT
 * and that two records' content ranges either COINCIDE EXACTLY or are disjoint
 * -- never partial, which is the only kind `p08` has. That is a measurement, not
 * an argument.
 *
 * Two C rungs share this declaration:
 *
 *   c/kernel.c           R1  -- BREAK writes through the borrowed buffer.
 *                               THE BUG.
 *   c/kernel_hardened.c  R1h -- the same, plus the copy-on-write block above,
 *                               and that is the whole difference between the
 *                               two cells.
 *
 * Both take `buf_len` and both ignore it: p49's bound is not the source
 * buffer's length. p12's, p06's, p14's, p27's, p29's and p32's shape.
 *
 * **The kernel must not mutate `buf`.** The driver calls it `n_iters` times and
 * every call must return the same value; the pool is a local, so call *i+1*
 * starts from the same state call *i* did. **This kernel makes no allocator call
 * at all**, so all seven rungs agree trivially about allocator traffic: there is
 * none.
 *
 * The guard is written subtraction-first (`len - p < 2`) rather than additively
 * (`p + 2 > len`) in all seven rungs, for p07's, p14's, p13's, p27's, p29's and
 * p32's reason: `p <= len` is maintained by the guard itself so the subtraction
 * cannot wrap, while the additive form can overflow and Verus rejects it.
 *
 * Unsigned overflow wraps by definition in C (6.2.5p9), so `acc*31 + x` is the
 * wrapping operation ../spec.md asks for with no special spelling.
 *
 * The caller must guarantee `off + len <= buf_len`; that is the structural
 * precondition every rung shares and no rung checks (rung 5 proves it at the
 * call site instead). `nops`, every opcode byte and every operand byte are
 * attacker data and are the kernel's problem. */
SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len);

#endif /* P49_KERNEL_H */
