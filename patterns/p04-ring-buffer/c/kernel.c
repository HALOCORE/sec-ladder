/* p04 rung R1 -- idiomatic C99 ring buffer over an attacker-chosen opcode
 * stream. THE BUG.
 *
 * A missing FULLNESS check. The window declares a count of 5-byte operations;
 * each one either enqueues a value or dequeues one. This rung bounds the POP
 * (`head != tail`, because "pop an empty queue" is the case the type makes you
 * think about) and does not bound the PUSH.
 *
 * That asymmetry is not a strawman, it is the shape the mistake actually takes:
 * a ring buffer is the data structure you reach for precisely because its
 * indices cannot run away, and they do not -- `head` and `tail` start at 0 and
 * every update is `(x + 1) % RING_CAP`, so **every index in this file is inside
 * [0, RING_CAP) on every input**. What overflows is not an index, it is the
 * QUEUE: pushing onto a full ring stores into the one slot the checked kernel
 * keeps reserved and moves `tail` onto `head`, and the ring then reads empty.
 * Sixty-three live elements vanish and nothing anywhere reports it.
 *
 * **This rung executes NO undefined behaviour on any input.** That is why it is
 * worth building: ASan, UBSan and Miri have nothing to say, and neither does
 * the memory-safety half of the R5 proof (../NOTES.md 6). The only thing that
 * catches it is the value -- which is why ../spec.md folds BOTH cursors into
 * the result, and why `adversarial-overwrite.bin` is a checksum row rather than
 * a sanitiser row.
 *
 * `(void)buf_len` is half the finding, as it is in p11 and p03: the size is
 * right there in the signature and this rung does not need it. Every buffer
 * index in this file is correct and in range; the length check
 * `5*nops > avail` is here, the cursor `4 + 5*k` never leaves the window. What
 * is wrong is a RELATION between two of the kernel's own local variables, and
 * no amount of care about the *buffer* would have caught it.
 *
 * R1h (kernel_hardened.c) is this file with `if ((tail + 1) % RING_CAP != head)`
 * around the push body and nothing else -- same signature, same calling
 * convention, same `len < 4` test, same `nops == 0` test, same length check,
 * same emptiness guard, same cursor, same return -- so R1-vs-R1h is the cost of
 * the fullness check and nothing else. ../NOTES.md 3 measures it per PUSH.
 *
 * Unsigned overflow wraps by definition (C99 6.2.5p9), so `acc*31 + ring[head]`
 * and `((acc*31 + head)*31 + tail)*31 + nops` are the wrapping operations
 * ../spec.md asks for.
 *
 * `ring` is deliberately NOT initialised, exactly as a C programmer writes it,
 * and no rung ever reads an unwritten slot: a POP happens only when
 * `head != tail`, and every slot between them was written by a PUSH -- in R1
 * too, because R1's collapse sets `head == tail` and the ring refills from
 * there. ../NOTES.md 3c prices what the four Rust rungs pay for
 * `[0u64; RING_CAP]`, which is a language difference and not a bounds check. */
#include "kernel.h"

#define RING_CAP 64

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len)
{
    uint64_t ring[RING_CAP];
    uint64_t acc = 0;
    size_t nops, head = 0, tail = 0, k;

    (void)buf_len; /* the size is right here ... and it is not the problem. */

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
            /* THE FULLNESS CHECK is missing here, and that is the whole diff
             * against kernel_hardened.c. The store below is IN BOUNDS. */
            ring[tail] = val;
            tail = (tail + 1) % RING_CAP;
        } else {
            /* THE EMPTINESS CHECK. Present in every rung, R1 included. */
            if (head != tail) {
                acc = acc * 31 + ring[head];
                head = (head + 1) % RING_CAP;
            }
        }
    }
    return ((acc * 31 + (uint64_t)head) * 31 + (uint64_t)tail) * 31
        + (uint64_t)nops;
}
