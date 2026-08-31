/* p35 rung R1h -- the same idiomatic C99 tagged-union dispatcher WITH the
 * safety line. Identical to c/kernel.c apart from the ORDER of two statements
 * at the two sites marked below.
 *
 * **The safety line: publish the tag only once the payload it describes is in
 * place.** `cells[idx].tag = P35_T_*;` moves from *before* the
 * `if (navail > 0)` to *inside* it, after the payload store. Nothing is added,
 * nothing is deleted, no test is introduced: `../controls/safety_line.py`
 * preprocesses both shipped files and measures `+2 / -2` lines, a PURE REORDER
 * at both sites.
 *
 * ⚠ **This is the third SHAPE of safety line in the tree** -- p27's is a
 * CONJUNCT, p13's is a STORE, p35's is a SEQUENCING CONSTRAINT. There is no
 * extra test, no extra load and no extra branch.
 *
 * ⚠⚠ **THE SENTENCE THAT USED TO FOLLOW IS RETRACTED, AND THE ORIGINAL IS
 * STRUCK RATHER THAN QUIETLY DELETED** (PROTOCOL rule 6's added step; this
 * file is the copy the TASK_148 sweep MISSED, found by TASK_152 M4 and struck
 * at TASK_153). It read: ~~so the R1-vs-R1h cost of this pattern's safety is a
 * scheduling difference and nothing more~~. MEASURED, it is not a scheduling
 * difference and it is not nothing: R1h is CHEAPER than R1 on **16 of 16**
 * cells (2 compilers x 2 opt levels x 2 modes x 2 inputs), and at `-O0` the
 * whole of the difference is THIS FILE NOT EXECUTING A STORE -- exactly
 * 5.0000 Ir per failed tag store on all eight `-O0` cells, on both compilers,
 * because a `-O0` tag store is a five-instruction block (`harness/asm.py diff`
 * on the two `-O0` kernels moves precisely those five). ../NOTES.md 4 has the
 * table, the denominator and the instruction-level mechanism.
 *
 * **What it buys.** With the tag published only on the path that stores, the
 * tag and the union's live member cannot disagree, so `GET` always reads the
 * union at the member last written. The dereference of an attacker-derived
 * integer and the comparison of a garbage double both become unreachable, on
 * every input this pattern ships. Stage 7h runs this file under ASan+UBSan on
 * every input, adversarial included, and requires it CLEAN.
 *
 * Unsigned overflow wraps by definition (C99 6.2.5p9). */
#include <string.h>

#include "kernel.h"

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len)
{
    struct p35_cell cells[P35_CELLS];
    uint8_t arena[P35_BUDGET];
    size_t nops, i, p, navail, idx;
    uint8_t c, a;
    uint64_t acc = 0;

    (void)buf_len; /* p35's bound is not this one -- it is the cell's TYPE. */

    if (len < 4)
        return 0;
    nops = (size_t)buf[off] + 256 * (size_t)buf[off + 1]
        + 65536 * (size_t)buf[off + 2] + 16777216 * (size_t)buf[off + 3];
    if (nops == 0)
        return 0;

    memset(cells, 0, sizeof cells);
    for (i = 0; i < P35_BUDGET; i++)
        arena[i] = (uint8_t)(i * 11u + 5u);
    navail = P35_BUDGET;
    p = 4;

    for (i = 0; i < nops; i++) {
        if (len - p < 2)
            break;
        c = buf[off + p];
        a = buf[off + p + 1];
        p += 2;
        idx = (size_t)(a % P35_CELLS);

        if (c % 4 == 0) {
            /* SET_INT -- cannot fail, so both rungs agree here. */
            cells[idx].tag = P35_T_INT;
            cells[idx].u.i = (uint64_t)a * 2654435761u;
            acc = acc * 31 + (uint64_t)a;
        } else if (c % 4 == 1) {
            /* SET_PTR -- takes a byte out of the budget.
             * ===================== THE SAFETY LINE (1 of 2) =================
             * Publish the tag only once the payload it describes is in place.
             * c/kernel.c writes these two statements in the other order. */
            if (navail > 0) {
                cells[idx].u.p = &arena[P35_BUDGET - navail];
                cells[idx].tag = P35_T_PTR;
                navail--;
                acc = acc * 31 + 1;
            } else {
                acc = acc * 31 + P35_SENT;
            }
            /* =============================================================== */
        } else if (c % 4 == 2) {
            /* SET_DBL -- same budget, same ordering question.
             * ===================== THE SAFETY LINE (2 of 2) ================= */
            if (navail > 0) {
                cells[idx].u.d = (a % 2 == 0) ? 0.25 : 2.5;
                cells[idx].tag = P35_T_DBL;
                navail--;
                acc = acc * 31 + 2;
            } else {
                acc = acc * 31 + P35_SENT;
            }
            /* =============================================================== */
        } else {
            /* GET -- dispatch on the tag. Character-identical in both rungs. */
            if (cells[idx].tag == P35_T_INT) {
                acc = acc * 31 + (cells[idx].u.i & 0xFFu);
            } else if (cells[idx].tag == P35_T_PTR) {
                acc = acc * 31 + (uint64_t)*cells[idx].u.p;
            } else if (cells[idx].tag == P35_T_DBL) {
                acc = acc * 31 + (uint64_t)(cells[idx].u.d > 1.0 ? 1u : 0u);
            } else {
                acc = acc * 31 + P35_SENT;
            }
        }
    }
    return acc * 31 + (uint64_t)navail;
}
