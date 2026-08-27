/* p42 rung R1 -- idiomatic C99, single-exit with a `goto cleanup` chain, and
 * ONE ERROR PATH THAT DOES NOT JOIN THE CHAIN. That missing jump is the bug.
 *
 * The shape is the one SEI CERT MEM12-C recommends -- "Consider using a goto
 * chain when leaving a function on error when using and releasing resources" --
 * and the bug is the failure mode the same rule warns about: an error branch
 * that returns directly, or jumps into the chain BELOW the link that releases
 * what it holds. This kernel does the first; the real defect the pattern is
 * modelled on did the second.
 *
 * PRECEDENT, fetched and quoted rather than remembered (../NOTES.md 1):
 * Linux commit 505d9dcb0f7ddf9d075e729523a33d38642ae680, "crypto: ccp - fix
 * resource leaks in ccp_run_aes_gcm_cmd()", drivers/crypto/ccp/ccp-ops.c,
 * CVE-2021-3764:
 *
 *              if (ret)
 *      -               goto e_ctx;
 *      +               goto e_aad;
 *
 * One label. `e_ctx` sits below `e_aad` in the chain, so the wrong jump skipped
 * the AAD work area's release and leaked it on every failed DMA mapping.
 *
 * WHAT IS DELIBERATE HERE AND MUST NOT BE "FIXED":
 *   * `malloc` comes BEFORE the tag test. That is the ordinary order -- take
 *     your working storage, then parse -- and it is what makes an error path
 *     capable of leaking at all. Moving the test above the allocation deletes
 *     the pattern.
 *   * the digest is `len` BYTES, sized from the caller's window length, so it
 *     cannot be a stack array without becoming p12's bug class. ../spec.md
 *     forbids a stack buffer for that reason.
 *   * `free(NULL)` is defined and is why the allocation-failure branch can jump
 *     straight into the chain.
 *
 * The hardened twin `kernel_hardened.c` differs in exactly one statement. */
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
        return 0; /* THE BUG: leaves without joining the cleanup chain */
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
