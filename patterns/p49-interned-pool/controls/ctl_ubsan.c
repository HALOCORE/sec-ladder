/* p49 POSITIVE CONTROL 3 of 3: the **UBSan** column.
 *
 * ⚠⚠ **THIS FILE EXISTS BECAUSE NEITHER ASan CONTROL CAN LICENSE THE UBSan
 * COLUMN.** `-fsanitize=undefined` has no use-after-free check and no
 * stack-buffer-overflow check, so a UBSan-only build of either runs to
 * completion with ZERO diagnostics -- which is exactly what a UBSan that was
 * never linked in looks like. `.temp/mgr147/NOTES.md` found `TASK_143`'s
 * demonstration in that state and closed it with a control of this shape.
 *
 * **THE RULE: A POSITIVE CONTROL LICENSES ONLY THE DETECTOR IT FIRES IN.** A
 * table with a per-detector column owes a per-detector control
 * (`.memory/03-measurement.md` entry 14; RECAP trap 5).
 *
 * p49 needs it more than any other row in this tree, because **UBSan's silence
 * here is not a side note, it is half the headline**: `c/kernel.c` executes no
 * undefined behaviour at all -- `../c/kernel.h` proves in four lines that every
 * index is inside `mem[0 .. MEM)` -- so UBSan reports nothing on any input at
 * either optimisation level on either compiler. Without this file that row would
 * be unsupported.
 *
 * So this file commits undefined behaviour UBSan DOES check -- signed integer
 * overflow -- and nothing else. It is deliberately NOT p49's bug, because p49
 * has no undefined behaviour to model; its only job is to prove that on the same
 * build line, in the same run, UBSan is linked and speaking.
 *
 * Expected: `runtime error: signed integer overflow` on the UBSan build,
 * `rc=0`; nothing at all on the plain build, `rc=0`.
 */
#include <stdio.h>

/* `volatile` so the overflow happens at run time and is not folded (or
 * rejected) at compile time. */
static volatile int slb_a49 = 32;
static volatile int slb_b49 = 2147483632; /* INT_MAX - 15 */

int main(void)
{
    int r = slb_a49 + slb_b49; /* MUST be reported by UBSan */
    printf("%d\n", r);
    return 0;
}
