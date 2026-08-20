/* p18 rung R1h -- the same C kernel WITH the shift bound.
 *
 * `if (shift < VBITS)` is the one line c/kernel.c omits. Everything else in
 * this file -- the scan bound `p < len`, the outer cursor guard `p == len`, the
 * per-varint reset, the fold, the wrapping arithmetic -- is character for
 * character what R1 does, so `c-gcc-h` minus `c-gcc` is the price of that line
 * and of nothing else (`.memory/02-bench-rules.md`, "The precondition must be
 * structural").
 *
 * **The hardened answer is TRUNCATION, and ../spec.md pins it.** Once the shift
 * count reaches the accumulator's width this rung keeps consuming the varint's
 * bytes -- so `nb` and the cursor are unchanged -- and simply stops
 * accumulating. That is what the Linux kernel's `uleb128`, Go's
 * `binary.Uvarint` in its non-error path, and most hand-written protobuf
 * readers do, and it is p13's shape one level up: **the hardened cell is
 * memory-safe, well-defined, and LOSES DATA.**
 *
 * Pinning truncation rather than rejection is a deliberate choice with a
 * measured reason (../NOTES.md 0b): the rejecting spelling needs a second live
 * variable and a second test, so R1-vs-R1h would stop being a one-line
 * difference; and rejecting would delete `truncating.bin`, the row on which
 * every rung agrees, every sanitizer is silent, `debug-assertions` is silent,
 * Miri is silent, the proof discharges -- and the answer is still wrong.
 *
 * **This rung still executes the shift on clang.** `cmpl $0x40,%ecx ; cmovaeq`
 * performs `shlq %cl` and then discards the result, where gcc branches around
 * it. The C is well-defined either way -- the guard is in the SOURCE, and that
 * is what the standard and UBSan read -- but it is worth saying out loud that
 * "the hardened rung does not do the dangerous thing" is a statement about the
 * source and not about the instruction stream. ../NOTES.md 4.
 *
 * The declaration, the window layout and the full argument are in kernel.h;
 * this file carries only what is different. */
#include "kernel.h"

#define VBITS 64

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len)
{
    uint64_t acc = 0, val;
    size_t nv, v, p, nb;
    unsigned shift;
    uint8_t c;

    (void)buf_len; /* p18's bound is not this one -- it is VBITS. */

    if (len < 4)
        return 0;
    nv = (size_t)buf[off] + 256 * (size_t)buf[off + 1]
        + 65536 * (size_t)buf[off + 2] + 16777216 * (size_t)buf[off + 3];
    if (nv == 0)
        return 0;

    p = 4;
    for (v = 0; v < nv; v++) {
        if (p == len)
            break;
        val = 0;
        shift = 0;
        nb = 0;
        while (p < len) {
            c = buf[off + p];
            p = p + 1;
            nb = nb + 1;
            /* THE SAFETY LINE, and the only line c/kernel.c omits. */
            if (shift < VBITS)
                val |= (uint64_t)(c & 0x7f) << shift;
            shift += 7;
            if (!(c & 0x80))
                break;
        }
        acc = acc * 31 + val;
        acc = acc * 31 + (uint64_t)nb;
    }
    return acc * 31 + (uint64_t)nv;
}
