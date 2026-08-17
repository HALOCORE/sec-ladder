/* p05 rung R1h -- kernel.c plus the one line a careful C programmer writes.
 *
 * `.memory/02-bench-rules.md`, "The precondition must be structural. The attack
 * must be data.": R1 omits the check because that is the bug being modelled,
 * and this cell includes it, so that "C is faster" and "C is unsafe" stop being
 * confounded. R1-vs-R1h is what the check costs *within one language*, with the
 * signature, the calling convention, the header tests, the fold and the return
 * all held fixed. The diff against kernel.c is one `if`.
 *
 * **The width is the whole subtlety, and it is why this cell is worth reading
 * twice.** `nrow` and `ncol` are `size_t` here, so `nrow * ncol` is exact:
 * at most 65535 * 65535 = 4 294 836 225, which is nowhere near `SIZE_MAX`.
 * Write the same line with `int` dimensions and it becomes
 *
 *     if ((int)nrow * (int)ncol > (int)avail) return 0;
 *
 * whose product overflows `INT_MAX` by 2 147 352 577 on `adversarial-ovf.bin`
 * -- undefined behaviour, in practice -131 071 -- so the comparison is false
 * and the attack goes straight through a check that *looks* right. That is the
 * "hardened wrong" cell; NOTES.md 6 builds it and measures it.
 *
 * Note the boundary precisely, because it is not the boundary the obvious
 * phrasing suggests: with u16 dimension fields the product still **fits in
 * `uint32_t`** (4 294 836 225 < 4 294 967 295), so an *unsigned* 32-bit check
 * is sound against every input this format can express. Only the signed one
 * breaks. "Do the check in 64 bits" is the right advice; "do it in an unsigned
 * type" happens to be sufficient here and would not be if the header fields
 * were u32.
 *
 * There is also no subtraction-first subtlety of the kind p02 and p16 needed.
 * `avail = len - 4` cannot underflow because `len >= 4` was tested two lines
 * above, and the comparison is `product > avail` rather than
 * `product > len - 4 - something`, so nothing wraps. The danger in this pattern
 * is a *multiplication* that is too wide for the type it is done in, not a
 * subtraction that is too small. */
#include "kernel.h"

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len)
{
    size_t nrow, ncol, avail, i, j;
    uint64_t acc = 0;

    (void)buf_len;

    if (len < 4)
        return 0;
    nrow = (size_t)buf[off] + 256 * (size_t)buf[off + 1];
    ncol = (size_t)buf[off + 2] + 256 * (size_t)buf[off + 3];
    if (nrow == 0 || ncol == 0)
        return 0;
    avail = len - 4;
    if (nrow * ncol > avail)
        return 0;

    for (i = 0; i < nrow; i++) {
        uint32_t row = 0;
        for (j = 0; j < ncol; j++)
            row = row + buf[off + 4 + i * ncol + j];
        acc = acc * 31 + row;
    }
    return acc * 31 + (uint64_t)(nrow * ncol);
}
