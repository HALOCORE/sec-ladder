/* p04 rung R1h -- kernel.c with the fullness check.
 *
 * `.memory/02-bench-rules.md`, "The precondition must be structural. The attack
 * must be data.": R1 pushes onto a full ring because that is the bug being
 * modelled, and this cell does not, so that "C is faster" and "C is unsafe"
 * stop being confounded. R1-vs-R1h is what the check costs *within one
 * language*, with the signature, the calling convention, the header tests, the
 * length check, the emptiness guard, the cursor and the return all held fixed.
 *
 * The diff against kernel.c is one `if` and its braces:
 *
 *     -            ring[tail] = val;
 *     -            tail = (tail + 1) % RING_CAP;
 *     +            if ((tail + 1) % RING_CAP != head) {
 *     +                ring[tail] = val;
 *     +                tail = (tail + 1) % RING_CAP;
 *     +            }
 *
 * **What this cell does NOT add is a bounds check**, because there is nothing
 * to bound: both cells index the ring only at `head` and `tail`, both of which
 * are in `[0, RING_CAP)` by construction in both. That is exactly what
 * separates p04 from p03 and p12, and `.memory/02-bench-rules.md`'s write rule
 * does not reach it -- p04's guard threshold is a **live length below the
 * allocation's extent**, so firing the guard and committing UB are independent
 * events, and the second never happens.
 *
 * The declared count is still trusted and still bounded only by
 * `5*nops > avail`, which R1 has too; `adversarial-count.bin` is the row that
 * shows the length check works in every rung, and `adversarial-wrap.bin` the
 * row that shows the modular arithmetic does -- the two controls that make "the
 * *fullness* check is the only variable" a measurement rather than a claim.
 *
 * There is no subtraction-first subtlety of the kind p02 and p16 needed:
 * `len - 4` cannot underflow because `len >= 4` is tested above it, and neither
 * cursor is ever decremented at all.
 *
 * `ring` is uninitialised here too, exactly as in kernel.c, so R1-vs-R1h is not
 * contaminated by the initialisation term ../NOTES.md 3c prices on the Rust
 * side. */
#include "kernel.h"

#define RING_CAP 64

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len)
{
    uint64_t ring[RING_CAP];
    uint64_t acc = 0;
    size_t nops, head = 0, tail = 0, k;

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
            /* THE FULLNESS CHECK. A relation between two cursors, not a bound
             * on an index. */
            if ((tail + 1) % RING_CAP != head) {
                ring[tail] = val;
                tail = (tail + 1) % RING_CAP;
            }
        } else {
            if (head != tail) {
                acc = acc * 31 + ring[head];
                head = (head + 1) % RING_CAP;
            }
        }
    }
    return ((acc * 31 + (uint64_t)head) * 31 + (uint64_t)tail) * 31
        + (uint64_t)nops;
}
