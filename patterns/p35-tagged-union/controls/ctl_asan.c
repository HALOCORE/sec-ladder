/* p35 POSITIVE CONTROL for the **ASan** column.
 *
 * p35's loud harm is the dereference of an attacker-derived integer read out of
 * a union at the wrong member. This file commits exactly that, in isolation and
 * made opaque so the compiler cannot fold it away, so that a run in which the
 * shipped kernel says nothing can be told from a run in which the detector was
 * never linked in.
 *
 * ⚠⚠ **AND IT LICENSES THE ASan COLUMN ONLY.** `-fsanitize=undefined` has NO
 * wild-pointer check, so on a UBSan-only build this program SIGSEGVs at
 * `rc=139` with ZERO diagnostics -- which is indistinguishable from a UBSan
 * that is not running. That is precisely the gap `.temp/mgr147/NOTES.md` found
 * in `TASK_143`'s demonstration, and `ctl_ubsan.c` is the other half.
 *
 * **A POSITIVE CONTROL LICENSES ONLY THE DETECTOR IT FIRES IN.**
 * `controls/detectors.py` runs both and asserts that each fires where it
 * should and is silent where it should be.
 *
 * Expected: ASan reports `SEGV on unknown address`; the plain build SIGSEGVs
 * with no diagnostic; the UBSan-only build SIGSEGVs with no diagnostic.
 */
#include <stdint.h>
#include <stdio.h>
#include <string.h>

struct ctl_cell {
    uint8_t tag;
    union {
        uint64_t i;
        double d;
        uint8_t *p;
    } u;
};

/* `volatile` so the value is not a compile-time constant and the load cannot
 * be folded away or proved unreachable. */
static volatile uint64_t slb_sink35 = 0x9E3779B97F4A7C15ull;

int main(void)
{
    struct ctl_cell cell;
    memset(&cell, 0, sizeof cell);
    /* The integer a previous SET_INT would have left in the union. */
    cell.u.i = slb_sink35 & 0xFFFFFFFFull;
    /* The tag the buggy rung publishes on a store that never landed. */
    cell.tag = 2;
    /* THE HARM. Read at the claimed type, then dereferenced. MUST be reported
     * by ASan. */
    printf("%llu\n", (unsigned long long)*cell.u.p);
    return 0;
}
