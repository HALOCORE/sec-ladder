/* p35 rung R1 -- idiomatic C99 tagged-union dispatcher. THE BUG.
 *
 * CWE-843 (access of resource using incompatible type). The store of a
 * pointer or a double takes a byte out of a budget that can run out, so it has
 * a FAILURE PATH -- and this rung PUBLISHES THE TAG BEFORE THE PAYLOAD LANDS.
 *
 * **The safety line is a STATEMENT ORDERING**, at the two sites marked below,
 * and it is the only difference between this file and c/kernel_hardened.c:
 * `cells[idx].tag = P35_T_*;` sits *before* the `if (navail > 0)` here and
 * *inside* it, after the payload store, there. `../controls/safety_line.py`
 * preprocesses both shipped files and measures the diff: `+2 / -2` lines, a
 * PURE REORDER at both sites, and nothing else.
 *
 * **ONE ORDERING, TWO BUG CLASSES, SELECTED BY THE INPUT.**
 *
 *   tag says PTR, payload is an int   GET DEREFERENCES an attacker-derived
 *                                     integer. SIGSEGV; ASan reports it.
 *   tag says DBL, payload is an int   GET compares a garbage double. A SILENT
 *                                     WRONG VALUE -- no ASan, no UBSan, no
 *                                     compiler warning, on either compiler.
 *
 * ⚠ **WHAT IS AND IS NOT UNDEFINED HERE, stated because it is easy to get
 * wrong and p38 is the neighbouring row.** Reading a union member other than
 * the one last stored is DEFINED in C99 (6.2.6.1p7 and 6.5.2.3's footnote:
 * the bytes are reinterpreted, and the only hazard is a trap representation,
 * which IEEE-754 `double` and `uint64_t` do not have on this target). So the
 * DBL arm executes NO undefined behaviour at all and is simply WRONG; this is
 * not p38's effective-type violation and `-fstrict-aliasing` has nothing to
 * say about it. The PTR arm's undefined behaviour is the DEREFERENCE of an
 * invalid pointer value, not the union read that produced it.
 *
 * **What this rung KEEPS.** The `else` arm that folds `P35_SENT` when the
 * budget is exhausted, so a failed store is still ACCOUNTED FOR and the bug is
 * not "the fold lost an operation". The `tag == 0` arm, so a cell that was
 * never written folds `P35_SENT` in both rungs and the bug is not "read
 * uninitialised". `navail`, decremented only on a store that actually
 * happened, so the two rungs return the same trailing term. **The whole of the
 * bug is that the tag is published on a path where the payload may not land.**
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
             * This rung publishes the tag HERE, before the payload it
             * describes is known to land. c/kernel_hardened.c moves this one
             * statement inside the `if` below, after the store. */
            cells[idx].tag = P35_T_PTR;
            if (navail > 0) {
                cells[idx].u.p = &arena[P35_BUDGET - navail];
                navail--;
                acc = acc * 31 + 1;
            } else {
                acc = acc * 31 + P35_SENT;
            }
            /* =============================================================== */
        } else if (c % 4 == 2) {
            /* SET_DBL -- same budget, same ordering question.
             * ===================== THE SAFETY LINE (2 of 2) ================= */
            cells[idx].tag = P35_T_DBL;
            if (navail > 0) {
                cells[idx].u.d = (a % 2 == 0) ? 0.25 : 2.5;
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
