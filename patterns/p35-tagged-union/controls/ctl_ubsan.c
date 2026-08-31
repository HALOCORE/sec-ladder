/* p35 POSITIVE CONTROL for the **UBSan** column.
 *
 * ⚠⚠ **THIS FILE EXISTS BECAUSE `ctl_asan.c` CANNOT LICENSE THE UBSan COLUMN.**
 * p35's loud harm is a wild pointer dereference; `-fsanitize=undefined` has no
 * wild-pointer check, so a UBSan-only build of that control SIGSEGVs at
 * `rc=139` with ZERO diagnostics -- which is exactly what a UBSan that was
 * never linked in looks like. `.temp/mgr147/NOTES.md` found `TASK_143`'s
 * demonstration in that state and closed it with a control of this shape.
 *
 * **THE RULE: A POSITIVE CONTROL LICENSES ONLY THE DETECTOR IT FIRES IN.** A
 * table with a per-detector column owes a per-detector control
 * (`.memory/03-measurement.md` entry 14, one level down; RECAP trap 5).
 *
 * So this file commits undefined behaviour that UBSan DOES check -- signed
 * integer overflow -- and nothing else. It is deliberately NOT p35's bug: its
 * only job is to prove that on the same build line, in the same run, UBSan is
 * linked and speaking. Once it does, the shipped kernel's silence on
 * `adversarial-dbl-confusion` is REAL silence rather than an absent detector.
 *
 * Expected: `runtime error: signed integer overflow` on the UBSan build,
 * `rc=0`; nothing at all on the plain build, `rc=0`.
 */
#include <stdio.h>

/* `volatile` so the overflow happens at run time and is not folded (or
 * rejected) at compile time. */
static volatile int slb_a35 = 32;
static volatile int slb_b35 = 2147483632; /* INT_MAX - 15 */

int main(void)
{
    int r = slb_a35 + slb_b35; /* MUST be reported by UBSan */
    printf("%d\n", r);
    return 0;
}
