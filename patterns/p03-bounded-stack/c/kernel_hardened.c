/* p03 rung R1h -- kernel.c with the emptiness check.
 *
 * `.memory/02-bench-rules.md`, "The precondition must be structural. The attack
 * must be data.": R1 pops an empty stack because that is the bug being
 * modelled, and this cell does not, so that "C is faster" and "C is unsafe"
 * stop being confounded. R1-vs-R1h is what the check costs *within one
 * language*, with the signature, the calling convention, the header tests, the
 * length check, the push guard, the cursor and the return all held fixed.
 *
 * The diff against kernel.c is one `if` and its braces:
 *
 *     -            sp = sp - 1;
 *     -            acc = acc * 31 + stack[sp];
 *     +            if (sp > 0) {
 *     +                sp = sp - 1;
 *     +                acc = acc * 31 + stack[sp];
 *     +            }
 *
 * **What this cell does NOT add is a check on `nops`, or on the buffer.** The
 * declared count is still trusted and is still bounded only by
 * `5*nops > avail`, which R1 has too; every buffer index in both cells is
 * correct. `adversarial-count.bin` is the row that shows the length check works
 * in every rung, and `adversarial-overflow.bin` the row that shows the push
 * guard does -- the two controls that make "the *emptiness* check is the only
 * variable" a measurement rather than a claim.
 *
 * There is no subtraction-first subtlety of the kind p02 and p16 needed:
 * `len - 4` cannot underflow because `len >= 4` is tested above it, and
 * `sp - 1` cannot underflow because `sp > 0` is tested beside it -- which is
 * the entire point of this file.
 *
 * `stack` is uninitialised here too, exactly as in kernel.c, so R1-vs-R1h is
 * not contaminated by the initialisation term ../NOTES.md 3c prices on the Rust
 * side. */
#include "kernel.h"

#define STACK_CAP 64

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len)
{
    uint64_t stack[STACK_CAP];
    uint64_t acc = 0;
    size_t nops, sp = 0, k;

    (void)buf_len;

    if (len < 4)
        return 0;
    nops = (size_t)buf[off] + 256 * (size_t)buf[off + 1]
        + 65536 * (size_t)buf[off + 2] + 16777216 * (size_t)buf[off + 3];
    if (nops == 0)
        return 0;
    if (5 * (uint64_t)nops > (uint64_t)(len - 4))
        return 0;

    for (k = 0; k < nops; k++) {
        uint8_t op = buf[off + 4 + 5 * k];
        uint64_t val = (uint64_t)buf[off + 5 + 5 * k]
            + 256 * (uint64_t)buf[off + 6 + 5 * k]
            + 65536 * (uint64_t)buf[off + 7 + 5 * k]
            + 16777216 * (uint64_t)buf[off + 8 + 5 * k];
        if (op == 0) {
            if (sp < STACK_CAP) {
                stack[sp] = val;
                sp = sp + 1;
            }
        } else {
            /* THE POP GUARD. `sp > 0`, not a bound on an index. */
            if (sp > 0) {
                sp = sp - 1;
                acc = acc * 31 + stack[sp];
            }
        }
    }
    return (acc * 31 + (uint64_t)sp) * 31 + (uint64_t)nops;
}
