/* p47 rung R1 -- idiomatic C99 tag comparison. THE BUG.
 *
 * CWE-208 (observable timing discrepancy), reached through CWE-1254
 * (incorrect comparison logic granularity). The comparison is `memcmp`, which
 * stops at the first differing byte, so the time the call takes -- and, on
 * this project's primary metric, the number of instructions it executes -- is
 * a function of how many leading bytes of the secret the attacker guessed
 * right. An attacker who can time the call recovers the secret one block at a
 * time instead of guessing it whole.
 *
 * **The whole difference from c/kernel_hardened.c is the comparison
 * expression** -- `memcmp(a, b, tlen) == 0` here, an or-accumulate over every
 * byte there. Everything else in the two files is character-identical.
 *
 * **WHAT THIS RUNG DOES NOT DO, AND IT IS THE POINT.** It does not read out of
 * bounds -- the guard `len - p >= 2*tlen` is here and is the same guard the
 * hardened rung has. It does not write anything. It does not allocate. It
 * returns, on every input this benchmark will ever run, *the same value as
 * every other rung*, so `harness/check.py` stage 2 cannot see the difference,
 * `model.py` cannot see it, ASan and UBSan report nothing (stage 7 declares
 * every input `clean` and it is), Miri is clean, and the postcondition rung 5
 * proves is satisfied by this file too. **p47's bug is invisible to every
 * oracle this project owns except the instruction counter.**
 *
 * **AND IT IS NOT A COMPILER ARTEFACT.** ⚠ At `-O3` clang rewrites
 * `memcmp(a,b,n) == 0` into a call to **`bcmp`** -- `R_X86_64_JUMP_SLOT bcmp`
 * on the shipped binary -- which is the *identical* symbol rustc emits for
 * `a == b` on two slices. gcc emits `memcmp`. So the c-clang cell and the R2
 * cell are calling one routine and any difference between them is a LIBRARY
 * difference, not a language one (`.memory/03-measurement.md`, "name the
 * routine"). Measured, glibc's `bcmp` on this box exits at 32-byte
 * granularity, so `Ir` as a function of the first-mismatch position `k` is a
 * **staircase of +7 Ir per 32-byte block**, not a line. ../NOTES.md 4.
 *
 * `memcmp` is called with `tlen` from the file, but only after the guard has
 * established that `2*tlen` bytes are present from `p`, so both arguments name
 * a `tlen`-byte range inside the window. There is no overlap: the candidate
 * starts exactly `tlen` bytes after the secret.
 *
 * Unsigned overflow wraps by definition (C99 6.2.5p9). This rung executes no
 * undefined behaviour on any input. */
#include <string.h>

#include "kernel.h"

#define MATCH 7
#define MISS 251

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len)
{
    size_t ntag, tlen, o, p;
    uint64_t acc = 0;

    (void)buf_len; /* p47's bound is the window's, not the blob's. */

    if (len < 8)
        return 0;
    ntag = (size_t)buf[off] + 256 * (size_t)buf[off + 1]
        + 65536 * (size_t)buf[off + 2] + 16777216 * (size_t)buf[off + 3];
    tlen = (size_t)buf[off + 4] + 256 * (size_t)buf[off + 5]
        + 65536 * (size_t)buf[off + 6] + 16777216 * (size_t)buf[off + 7];
    if (ntag == 0 || tlen == 0)
        return 0;

    p = 8;
    o = 0;
    while (o < ntag && len - p >= 2 * tlen) {
        /* THE TIMING LINE. c/kernel_hardened.c writes an or-accumulate over
         * all `tlen` bytes here and that expression is the whole difference
         * between the two cells. This one stops at the first mismatch. */
        if (memcmp(buf + off + p, buf + off + p + tlen, tlen) == 0)
            acc = acc * 31 + MATCH;
        else
            acc = acc * 31 + MISS;
        p += 2 * tlen;
        o += 1;
    }
    return acc * 31 + (uint64_t)o;
}
