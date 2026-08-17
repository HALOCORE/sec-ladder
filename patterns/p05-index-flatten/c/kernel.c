/* p05 rung R1 -- idiomatic C99 2-D index flattening. THE BUG.
 *
 * CWE-129: the declared dimensions are trusted against the buffer that actually
 * arrived. A header says the matrix is `nrow x ncol`; this rung walks
 * `nrow*ncol` elements without checking that many are present. It is the
 * shortest bug in numerical C and it is still being written.
 *
 * The single `(void)` cast is half the finding: the size is *right there* in
 * the signature. R1 has it and does not look; R1h (kernel_hardened.c) is this
 * file plus one line. Everything else about the two cells -- signature, calling
 * convention, the `nrow == 0 || ncol == 0` test, the fold, the return -- is
 * identical, so R1-vs-R1h is the cost of the check and nothing else.
 *
 * Note what this rung *keeps*: `len < 4` and `nrow == 0 || ncol == 0`. The
 * first is what makes reading the header itself defined; the second is a
 * denial-of-service guard rather than a memory one (see ../spec.md, "The zero
 * guard is a DoS guard") and dropping it would confound the pattern with a
 * second variable. What it drops is the one line marked below.
 *
 * **Why the inner loop is a plain sum and the outer one is Horner.** The inner
 * loop is associative on purpose, so that it *can* vectorise: p05 is the first
 * pattern in this repo whose measured loop is not a serial dependence chain,
 * and the whole point is to find out what a bounds check costs when it can
 * block a vector form rather than a 4x unroll. The Horner step happens once per
 * **row**, so the result still depends on row order and the two loops cannot be
 * re-associated into one flat scan. `i*ncol + j` is written out rather than
 * strength-reduced to a moving pointer, in every rung, because the flattened
 * index *is* the pattern.
 *
 * **Why `row` is `uint32_t` and not `uint64_t`.** Measured, TASK_013: with a
 * `uint64_t` row accumulator, LLVM's cost model declines to vectorise this loop
 * at the flags this project builds with (`-O3`, no `-march`, baseline SSE2) --
 * *"the cost-model indicates that vectorization is not beneficial"* -- in C and
 * in all four Rust rungs alike, while gcc vectorises it anyway. Narrowing the
 * row accumulator to 32 bits makes every back end vectorise, because a
 * u8 -> u32 widening sum needs two unpack levels per lane instead of three.
 * A 32-bit per-row checksum is also what a real row-hash would use. NOTES.md 1
 * has the disassembly for both. `acc` stays 64-bit.
 *
 * Unsigned overflow wraps by definition in C (6.2.5p9), so `row + b` and
 * `acc * 31 + row` are the wrapping operations ../spec.md asks for with no
 * special spelling. Nothing here can overflow *signed*. The only undefined
 * behaviour this rung can execute is the out-of-bounds read itself. */
#include "kernel.h"

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len)
{
    size_t nrow, ncol, avail, i, j;
    uint64_t acc = 0;

    (void)buf_len; /* the size is right here ... and this rung never looks. */

    if (len < 4)
        return 0;
    nrow = (size_t)buf[off] + 256 * (size_t)buf[off + 1];
    ncol = (size_t)buf[off + 2] + 256 * (size_t)buf[off + 3];
    if (nrow == 0 || ncol == 0)
        return 0;
    avail = len - 4;
    /* R1h has `if (nrow * ncol > avail) return 0;` here, and this rung does
     * not. That one line, in 64-bit arithmetic, is the whole difference.
     * `avail` is computed in both cells and consumed in only one, which is the
     * sharper version of the finding: this rung worked out how many bytes it
     * had and then indexed as if the header were true. (The dead store is
     * eliminated by every -O3 build, so the codegen delta is exactly the
     * comparison; the `(void)` is only to keep -Wextra quiet.) */
    (void)avail;

    for (i = 0; i < nrow; i++) {
        uint32_t row = 0;
        for (j = 0; j < ncol; j++)
            row = row + buf[off + 4 + i * ncol + j];
        acc = acc * 31 + row;
    }
    return acc * 31 + (uint64_t)(nrow * ncol);
}
