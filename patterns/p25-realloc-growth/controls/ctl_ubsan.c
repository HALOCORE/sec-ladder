/* p25 POSITIVE CONTROL for the **UBSan** column.
 *
 * ⚠⚠ **THIS FILE EXISTS BECAUSE `ctl_asan.c` CANNOT LICENSE THE UBSan COLUMN.**
 * p25's harm is a read through a pointer into storage `realloc` retired;
 * `-fsanitize=undefined` has no use-after-free check, so a UBSan-only build of
 * that control runs to completion with ZERO diagnostics -- which is exactly what
 * a UBSan that was never linked in looks like. `.temp/mgr155/NOTES.md` §3 found
 * `TASK_143`'s p25 demonstration in that state (`ubsan rc=0 ctl 94`, no
 * diagnostic) and asked this row to close it, as `p35` did.
 *
 * **THE RULE: A POSITIVE CONTROL LICENSES ONLY THE DETECTOR IT FIRES IN.** A
 * table with a per-detector column owes a per-detector control
 * (`.memory/03-measurement.md` entry 14; RECAP trap 5).
 *
 * p25 needs it, because **UBSan's silence is one of this pattern's published
 * results**: R1's undefined behaviour is entirely TEMPORAL -- `toks[ntok]` is
 * written only after the block has been grown to hold it, `&toks[a % ntok]` is
 * formed only under `ntok > 0`, and the cursor guard is subtraction-first -- so
 * UBSan reports nothing on any input at either optimisation level on either
 * compiler. Without this file that row would be unsupported.
 *
 * So this file commits undefined behaviour that UBSan DOES check -- signed
 * integer overflow -- and nothing else. It is deliberately NOT p25's bug: its
 * only job is to prove that on the same build line, in the same run, UBSan is
 * linked and speaking.
 *
 * Expected: `runtime error: signed integer overflow` on the UBSan build;
 * nothing at all on the plain build and nothing on the ASan build, `rc=0`.
 */
#include <stdio.h>

/* `volatile` so the overflow happens at run time and is not folded (or
 * rejected) at compile time. */
static volatile int slb_a25 = 25;
static volatile int slb_b25 = 2147483640; /* INT_MAX - 7 */

int main(void)
{
    int r = slb_a25 + slb_b25; /* MUST be reported by UBSan */
    printf("ctl_ubsan %d\n", r);
    return 0;
}
