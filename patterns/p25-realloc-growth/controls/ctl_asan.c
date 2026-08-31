/* p25 CONTROLS -- THE ASan POSITIVE CONTROL.
 *
 * ⚠ **A positive control licenses only the detector it FIRES IN** (RECAP trap 5,
 * found on p35 and re-found by the manager on p25's own pre-build demonstration:
 * a UBSan build that says nothing looks exactly like one that is not linked in).
 * So this file is the ASan one and `ctl_ubsan.c` is a DIFFERENT program.
 *
 * The harm modelled here is p25's, in miniature and unmistakable: take an
 * interior pointer into a heap block, force a `realloc` that MUST move (the old
 * block is pinned by a second live allocation immediately behind it, and the new
 * size is far larger than any in-place extension could satisfy), then read
 * through the stale interior pointer.
 *
 * The volatile sink is there so that no optimiser can fold the
 * take-pointer / realloc / read triple away and leave a control that cannot
 * fire for a reason having nothing to do with the detector.
 *
 * Exit code is deliberately NOT the signal -- `detectors.py` reads the
 * DIAGNOSTIC, because a control that "fails" by exiting non-zero is
 * indistinguishable from one that failed to build.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

static volatile void *slb_p25_sink;

int main(void)
{
    uint8_t *v, *pin, *nv;
    const uint8_t *stale;
    unsigned long acc;

    v = (uint8_t *)malloc(16);
    pin = (uint8_t *)malloc(16);
    if (v == NULL || pin == NULL)
        return 3;
    slb_p25_sink = v;
    slb_p25_sink = pin;

    v[3] = 0x5A;
    stale = &v[3];              /* THE INTERIOR POINTER */

    nv = (uint8_t *)realloc(v, 1u << 20);   /* MUST move: pinned and far larger */
    if (nv == NULL)
        return 3;
    slb_p25_sink = nv;

    acc = (unsigned long)*stale;            /* <- ASan MUST report this */
    printf("ctl_asan %lu\n", acc);

    free(nv);
    free(pin);
    return 0;
}
