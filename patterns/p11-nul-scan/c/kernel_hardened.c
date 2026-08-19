/* p11 rung R1h -- kernel.c with the scan bounded by the window.
 *
 * `.memory/02-bench-rules.md`, "The precondition must be structural. The attack
 * must be data.": R1 trusts the sentinel because that is the bug being
 * modelled, and this cell does not, so that "C is faster" and "C is unsafe"
 * stop being confounded. R1-vs-R1h is what the bound costs *within one
 * language*, with the signature, the calling convention, the header test, the
 * fold, the cursor and the return all held fixed. The diff against kernel.c is
 * one expression.
 *
 * **Why `memchr` and not `strnlen`, measured rather than preferred.** `strnlen`
 * is POSIX (`_POSIX_C_SOURCE >= 200809L`), not C99. `harness/build.py` compiles
 * with `-std=c99` and defines no feature-test macro, so `<string.h>` does not
 * declare it:
 *
 *     clang: error: call to undeclared function 'strnlen'; ISO C99 and later
 *            do not support implicit function declarations
 *     gcc:   warning: implicit declaration of function 'strnlen'
 *
 * `memchr` is C99 and needs nothing. It is also the closer mirror of what the
 * Rust rungs do -- find the terminator inside a span of *known length* -- so
 * R1h and R3 differ in which library they call and not in what they compute.
 * The `NULL` arm is what makes the bound real: a window with no terminator left
 * yields `q = len`, i.e. "the string ends where the window ends", which is
 * exactly what every checked Rust rung does.
 *
 * There is no subtraction-first subtlety of the kind p02 and p16 needed:
 * `len - p` cannot underflow because `p < len` on entry to every iteration --
 * `p` is 4 with `len >= 4` on the first, and the loop breaks at `p >= len`
 * afterwards. When `p == len` on the first iteration (a 4-byte window) the count
 * is 0 and `memchr` returns `NULL` immediately, which is the same answer the
 * Rust rungs' empty scan gives.
 *
 * Note what this cell does NOT add: a check on `nstr`. The declared count is
 * still trusted, and it still bounds nothing -- the *sentinel* and the *window
 * end* are what stop the walk. `adversarial-zerotail.bin` is the input that
 * demonstrates it, and it is the one row where an inflated `nstr` is harmless in
 * every rung including R1. ../NOTES.md 7. */
#include <string.h>

#include "kernel.h"

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len)
{
    size_t nstr, s, p, q, i, slen;
    uint64_t acc = 0;

    (void)buf_len;

    if (len < 4)
        return 0;
    nstr = (size_t)buf[off] + 256 * (size_t)buf[off + 1]
        + 65536 * (size_t)buf[off + 2] + 16777216 * (size_t)buf[off + 3];
    if (nstr == 0)
        return 0;

    p = 4;
    for (s = 0; s < nstr; s++) {
        uint64_t h = 0;
        const void *z = memchr(buf + off + p, 0, len - p);
        /* THE BOUND. `len - p` bytes, not "until a zero byte". */
        q = (z == NULL) ? len : (size_t)((const unsigned char *)z - (buf + off));
        slen = q - p;
        for (i = p; i < q; i++)
            h = h * 31 + (uint64_t)buf[off + i];
        acc = acc * 31 + (h ^ (uint64_t)slen);
        if (q >= len)
            break;
        p = q + 1;
        if (p >= len)
            break;
    }
    return acc * 31 + (uint64_t)nstr;
}
