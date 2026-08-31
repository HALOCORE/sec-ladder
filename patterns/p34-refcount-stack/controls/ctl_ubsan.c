/* p34 POSITIVE CONTROL for the **UBSan** column.
 *
 * ⚠⚠ **THIS FILE EXISTS BECAUSE `ctl_asan.c` CANNOT LICENSE THE UBSan COLUMN.**
 * p34's harm is a use-after-free; `-fsanitize=undefined` has no use-after-free
 * check, so a UBSan-only build of that control runs to completion with ZERO
 * diagnostics -- which is exactly what a UBSan that was never linked in looks
 * like. `.temp/mgr147/NOTES.md` found `TASK_143`'s demonstration in that state
 * and closed it with a control of this shape.
 *
 * **THE RULE: A POSITIVE CONTROL LICENSES ONLY THE DETECTOR IT FIRES IN.** A
 * table with a per-detector column owes a per-detector control
 * (`.memory/03-measurement.md` entry 14; RECAP trap 5).
 *
 * p34 needs it more than most rows, because **UBSan's silence is one of this
 * pattern's published results**: R1's undefined behaviour is entirely TEMPORAL,
 * every index the kernel forms is inside `stk[]` in both rungs, and UBSan
 * therefore reports nothing on any input at either optimisation level on either
 * compiler. Without this file that row would be unsupported.
 *
 * So this file commits undefined behaviour that UBSan DOES check -- signed
 * integer overflow -- and nothing else. It is deliberately NOT p34's bug: its
 * only job is to prove that on the same build line, in the same run, UBSan is
 * linked and speaking.
 *
 * Expected: `runtime error: signed integer overflow` on the UBSan build,
 * `rc=0`; nothing at all on the plain build, `rc=0`.
 */
#include <stdio.h>

/* `volatile` so the overflow happens at run time and is not folded (or
 * rejected) at compile time. */
static volatile int slb_a34 = 32;
static volatile int slb_b34 = 2147483632; /* INT_MAX - 15 */

int main(void)
{
    int r = slb_a34 + slb_b34; /* MUST be reported by UBSan */
    printf("%d\n", r);
    return 0;
}
