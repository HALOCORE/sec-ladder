/* p03 rung R1 -- idiomatic C99 bounded stack over an attacker-chosen opcode
 * stream. THE BUG.
 *
 * CWE-124/CWE-125 via a missing emptiness check. The window declares a count of
 * 5-byte operations; each one either pushes a value or pops one. This rung
 * bounds the PUSH (`sp < STACK_CAP`, because overflowing a fixed array is the
 * mistake everybody knows about) and does not bound the POP.
 *
 * That asymmetry is not a strawman, it is the shape the mistake actually takes:
 * the programmer thinks about the array's *capacity* because the array's size
 * is written down beside it, and does not think about its *emptiness* because
 * nothing in the type says a stack can be empty. `sp` is `size_t`, so
 * `sp - 1` at `sp == 0` is `SIZE_MAX`, `stack + SIZE_MAX` wraps to `stack - 1`,
 * and the read lands 8 bytes below the array -- inside this function's own
 * frame. It does not fault (../NOTES.md 7 measures what it does), which is
 * exactly why this class survives testing.
 *
 * `(void)buf_len` is half the finding, as it is in p11: the size is right there
 * in the signature and this rung does not need it. **Every buffer index in this
 * file is correct and in range.** The length check `5*nops > avail` is here,
 * the push guard is here, the cursor `4 + 5*k` never leaves the window. What is
 * wrong is a fact about the kernel's own local state, and no amount of care
 * about the *buffer* would have caught it. That is the difference between p03
 * and every earlier pattern here.
 *
 * R1h (kernel_hardened.c) is this file with `if (sp > 0) { ... }` around the
 * pop body and nothing else -- same signature, same calling convention, same
 * `len < 4` test, same `nops == 0` test, same length check, same push guard,
 * same cursor, same return -- so R1-vs-R1h is the cost of the emptiness check
 * and nothing else. ../NOTES.md 3 measures it per POP.
 *
 * Unsigned overflow wraps by definition (C99 6.2.5p9), so `acc*31 + stack[sp]`
 * and `(acc*31 + sp)*31 + nops` are the wrapping operations ../spec.md asks
 * for. The only undefined behaviour this rung can execute is the out-of-bounds
 * read itself.
 *
 * `stack` is deliberately NOT initialised, exactly as a C programmer writes it.
 * ../NOTES.md 3c prices what the four Rust rungs pay for `[0u64; STACK_CAP]`,
 * which is a language difference and not a bounds check, and separates it from
 * the safety terms rather than letting it hide inside them. */
#include "kernel.h"

#define STACK_CAP 64

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len)
{
    uint64_t stack[STACK_CAP];
    uint64_t acc = 0;
    size_t nops, sp = 0, k;

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
            /* THE PUSH GUARD. Present in every rung, R1 included. */
            if (sp < STACK_CAP) {
                stack[sp] = val;
                sp = sp + 1;
            }
        } else {
            /* THE POP GUARD is missing here, and that is the whole diff
             * against kernel_hardened.c. */
            sp = sp - 1;
            acc = acc * 31 + stack[sp];
        }
    }
    return (acc * 31 + (uint64_t)sp) * 31 + (uint64_t)nops;
}
