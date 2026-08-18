/* p08 rung R1h -- c/kernel.c with `memcpy` replaced by `memmove` in the move,
 * and nothing else changed.
 *
 * `.memory/01-ladder.md`: R1-vs-R1h is what safety costs *inside one language*,
 * with the signature, the calling convention, the argument count and the
 * register allocation all held fixed. On p02 that difference was a bounds
 * comparison (+5 gcc / +12 clang per call); on p05 it was a size test (+7 / +2).
 * Here it is not a check at all -- **both cells call a bulk-memory routine of
 * the same size, and the difference is which one**. That makes p08's R1-vs-R1h
 * the cleanest instance of the axis this project has: the two builds differ by
 * one token and by no control flow the compiler can see.
 *
 * `diff c/kernel.c c/kernel_hardened.c` is exactly the `memcpy`/`memmove` line
 * and the comments around it, and `controls/gen_controls.py` asserts that.
 *
 * On glibc 2.39 / x86-64 the two are the SAME FUNCTION -- `dlsym("memcpy")` and
 * `dlsym("memmove")` return one address -- so this cell is expected to cost the
 * same as R1 and to agree with it on every input including the overlapping one.
 * That is measured in NOTES.md 2 and 3 rather than assumed, and it is p08's
 * central negative result: the bug is real, the UB is real, and *executing it
 * changes nothing on this platform*. */
#include <string.h>

#include "kernel.h"

#define P08_SCR 4096u

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len)
{
    uint8_t scr[P08_SCR];
    size_t d, nrep_w, nrep, avail, m, r, j;
    uint64_t acc = 0;

    (void)buf_len; /* the kernel reads nothing outside buf[off .. off+len). */

    if (len < 4)
        return 0;
    d = (size_t)buf[off] + 256 * (size_t)buf[off + 1];
    nrep_w = (size_t)buf[off + 2] + 256 * (size_t)buf[off + 3];
    avail = len - 4;
    m = avail < P08_SCR ? avail : P08_SCR;
    nrep = 1 + nrep_w % 4;
    if (m < 2 || d == 0 || d + nrep > m)
        return 0;

    memset(scr, 0, P08_SCR);
    memcpy(scr, buf + off + 4, m);

    for (r = 0; r < nrep; r++) {
        size_t dr = d + r;
        /* >>> THE OPERATION, spelled correctly. `memmove` is defined for
         * overlapping ranges; `memcpy` (c/kernel.c) is not. <<< */
        memmove(scr + dr, scr, m - dr);
    }

    for (j = 0; j < m; j++)
        acc = acc * 31 + scr[j];
    return acc * 31 + (uint64_t)m;
}
