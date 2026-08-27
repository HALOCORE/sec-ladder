/* p42 rung R1h -- the same C kernel with the error path joined to the cleanup
 * chain. One statement differs from `kernel.c`:
 *
 *     -        return 0;      // leaves without releasing `dig`
 *     +        goto cleanup;  // joins the chain, which releases `dig`
 *
 * and the two return the same value on that path, because `acc` is still 0 when
 * the chain is entered. So R1h is not a different algorithm and not a different
 * answer: it is the same program with the leak removed, which is what lets
 * R1-vs-R1h price the leak inside one language rather than across two
 * (`.memory/02-bench-rules.md`, "The precondition must be structural").
 *
 * ../spec.md's `forbidden` list keeps this file honest in the other direction
 * too: it may not "fix" anything else -- no reordering of the allocation, no
 * early tag test, no stack buffer. */
#include <stdlib.h>

#include "kernel.h"

SLB_NOINLINE uint64_t kernel(const uint64_t *v, size_t off, size_t len)
{
    uint64_t acc = 0;
    uint8_t *dig = NULL;
    uint64_t run;
    size_t i;

    dig = (uint8_t *)malloc(len);
    if (dig == NULL)
        goto cleanup;
    if ((v[off] & 0xffu) != P42_TAG)
        goto cleanup; /* HARDENED: the chain releases `dig` */
    run = 0;
    for (i = 0; i < len; i++) {
        run += v[off + i] ^ P42_MIX;
        dig[i] = (uint8_t)(run >> 24);
    }
    for (i = 0; i < len; i++)
        acc = acc * 31 + dig[len - 1 - i];

cleanup:
    free(dig);
    return acc;
}
