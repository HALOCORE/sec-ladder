#ifndef P23_KERNEL_H
#define P23_KERNEL_H

#include <stddef.h>
#include <stdint.h>

#include "driver.h" /* SLB_NOINLINE */

/* p23: in-place Hoare partition of a fixed scratch buffer around a pivot the
 * record supplies. One window holds a declared count of records; each record
 * declares an element count and a PIVOT BYTE, and the kernel copies the
 * elements into a fixed-size local `scr[SCR]` and partitions the live prefix in
 * place with Hoare's two-cursor NESTED-SCAN, then folds the partitioned prefix
 * and the partition point. See ../README.md and ../NOTES.md 0.
 *
 *   window = buf[off .. off+len)
 *   nrec        = u32 LE at window byte 0        DECLARED. ATTACKER DATA.
 *   data_start  = 4
 *   record      = u32 LE nelem ; u8 pivot ; u8 pad[3] ; nelem bytes
 *                                                ALL ATTACKER DATA
 *   SCR = 64                                     a compile-time constant
 *
 *   scr[SCR] = {0} ; acc = 0 ; p = 4
 *   for rec in 0 .. nrec:
 *       if len - p < 8: break
 *       nelem = u32le(buf[off+p]) ; pv = buf[off+p+4] ; p += 8
 *       m = min(nelem, SCR)             <<< the CLAMP, present in EVERY rung
 *       if len - p < nelem: break
 *       memcpy(scr, buf + off + p, m)   <<< bulk, in EVERY rung
 *       p += nelem
 *       i = 0 ; j = m
 *       while i < j:
 *           while (i < j &&) scr[i] <= pv:     i++   <<< SAFETY LINE, half 1
 *           while (i < j &&) scr[j - 1] >= pv: j--   <<< SAFETY LINE, half 2
 *           if i < j: swap(scr[i], scr[j-1]) ; i++ ; j--
 *       for q in 0 .. m: acc = acc*31 + scr[q]     u64, wrapping
 *       acc = acc*31 + i                           the PARTITION POINT
 *   return acc*31 + nrec
 *
 * **THE BOUND ON ONE CURSOR IS THE OTHER CURSOR, and that is why this pattern
 * exists.** Every earlier bound in this project comes from somewhere outside
 * the loop: a header field (p05, p07, p16, p17, p19, p36), a compile-time
 * capacity (p03, p06, p12), a live length (p04, p14). Here `i` is bounded by
 * `j`, `j` is bounded by `i`, and BOTH move. Delete the two conjuncts and the
 * loop's only remaining stopping condition is a property of the DATA -- an
 * element strictly above the pivot for the upward scan, an element strictly
 * below it for the downward one. Textbook Hoare gets that property for free by
 * taking the pivot FROM the array; this kernel is handed one, so it does not.
 *
 * **THE TWO HALVES OVERRUN IN OPPOSITE DIRECTIONS.** `scr[i]` runs off the TOP
 * of the scratch and `scr[j-1]` runs off the BOTTOM, and `j - 1` at `j == 0`
 * wraps `size_t`, so the downward scan walks away from the frame rather than
 * one byte past it. One omitted pair of conjuncts, two out-of-bounds classes:
 *
 *   pv == 255, every element <= pv   the upward scan leaves `scr[SCR-1]`
 *                                    behind. `adversarial-allbelow`.
 *   pv == 0,   every element >= pv   the downward scan leaves `scr[0]` behind
 *                                    and `j` wraps. `adversarial-allabove`.
 *
 * Both are reachable at a SINGLE HEADER BYTE, because no `uint8_t` is greater
 * than 255 or less than 0: `pv == 255` and `pv == 0` are adversarial whatever
 * the elements are, and every other pivot is benign exactly when the record
 * holds an element on each side of it. ../NOTES.md 7 records what each does at
 * the gate's flags.
 *
 * **What this rung KEEPS is as important as what it drops.** It keeps the clamp
 * `m = min(nelem, SCR)`, so the *copy* is bounded and every read of the source
 * is in bounds; it keeps both cursor guards, so `p` never leaves the window; it
 * keeps the outer `while (i < j)` and the `if (i < j)` before the swap. The
 * only things missing are the two conjuncts marked above. That is what makes
 * R1-vs-R1h the cost of the scan guard and nothing else.
 *
 * **The comparisons are `<=` and `>=`, not `<` and `>`, in EVERY rung.** That
 * is the spelling that makes the two cursors meet: with `<=`/`>=` a run of
 * elements equal to the pivot is consumed by whichever scan reaches it first,
 * so `j - i == 1` always collapses to `i == j` and the cursors never cross.
 * With `<`/`>` an element exactly equal to the pivot stops both scans, the
 * swap is a no-op and `i` steps past `j`. Both spellings are in the wild;
 * this one is pinned in ../spec.md so that no rung comparison moves on it.
 *
 * The guards are written subtraction-first (`len - p < 8`) rather than
 * additively (`p + 8 > len`) in all seven rungs. `p <= len` is maintained by
 * the guards themselves, so the subtraction cannot wrap; the additive form can
 * overflow `size_t` for a window at the top of the address space and Verus
 * rejects it. p07's lesson, and p06's: the spelling that makes the proof
 * trivial is the one that makes the bug impossible.
 *
 * Two C rungs share this declaration:
 *
 *   c/kernel.c           R1  -- no `i < j &&`. THE BUG.
 *   c/kernel_hardened.c  R1h -- `i < j &&` on both scans, and those two
 *                               conjuncts are the whole difference.
 *
 * Both take `buf_len`, and both ignore it: p23's bound is not the source
 * buffer's length, it is the SCRATCH's live extent, which is carried by the
 * two cursors. That is the contrast with p02, p16 and p17, where the check the
 * C rung skips is against a length it was handed.
 *
 * **The kernel must not mutate `buf`.** The driver calls it `n_iters` times and
 * every call must return the same value; the scratch copy is what makes an
 * in-place pattern legal in this benchmark at all. `scr` is zero-initialised on
 * every call in every rung, which is what makes the tail past `m` -- which the
 * unguarded upward scan reads before it leaves the array at all -- deterministic
 * and identical across rungs.
 *
 * Unsigned overflow wraps by definition in C (6.2.5p9), so `acc*31 + scr[q]`,
 * `acc*31 + i` and the return expression are the wrapping operations ../spec.md
 * asks for with no special spelling. The undefined behaviour this rung can
 * execute is the out-of-bounds READ that either scan performs, and the
 * out-of-bounds WRITE that the swap performs afterwards when the downward scan
 * has wrapped `j` -- so the read escalates, which is why ../NOTES.md 7 reports
 * a behaviour per direction rather than one row.
 *
 * The caller must guarantee `off + len <= buf_len`; that is the structural
 * precondition every rung shares and no rung checks (rung 5 proves it at the
 * call site instead). `nrec`, `nelem`, `pv` and every byte of the window are
 * attacker data and are the kernel's problem. */
SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len);

#endif /* P23_KERNEL_H */
