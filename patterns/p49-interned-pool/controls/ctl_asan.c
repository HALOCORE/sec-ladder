/* p49 POSITIVE CONTROL 1 of 3: the **ASan heap** column.
 *
 * ⚠⚠ **THIS FILE DOES NOT MODEL p49's HARM, AND IT CANNOT.** p49's harm is a
 * wrong VALUE: nothing is allocated, nothing is freed, no pointer dangles and
 * every index is inside `mem[0 .. P49_MEM)`, so there is no undefined behaviour
 * for ASan to report on any input. **Every detector column on this row is
 * SILENT, which makes a control that FIRES the only thing separating *silent*
 * from *not linked in*.** That is why this row ships three of them where most
 * rows ship two.
 *
 * This one commits a plain heap use-after-free, made to escape through a
 * `volatile` sink and sized from `argc` so that neither compiler can eliminate
 * the `malloc`/`free` pair -- `p31`'s malloc-elision artefact disarmed the first
 * spelling of `p32`'s control in this family, and `TASK_160` hit the same thing
 * in gcc at `-O1`, where `objdump` showed `main()` compiled to a single `puts`.
 *
 * ⚠ **It licenses the ASan column ONLY.** `-fsanitize=undefined` has no
 * use-after-free check, so on a UBSan-only build this program runs to completion
 * with zero diagnostics -- indistinguishable from a UBSan that is not linked in.
 * `ctl_ubsan.c` is the second half and `ctl_asan_stack.c` the third.
 *
 * Expected: ASan reports `heap-use-after-free`; the plain and UBSan-only builds
 * print a byte and exit 0.
 */
#include <stdio.h>
#include <stdlib.h>

/* `volatile` so the pointer escapes and the allocation cannot be proved dead. */
static volatile unsigned char *slb_sink49;

int main(int argc, char **argv)
{
    unsigned char *p;
    (void)argv;
    p = (unsigned char *)malloc(32u * (unsigned)argc);
    if (p == NULL)
        return 2;
    slb_sink49 = p;
    p[0] = (unsigned char)(argc + 40);
    free(p);
    /* THE HARM. MUST be reported by ASan. */
    printf("%u\n", (unsigned)slb_sink49[0]);
    return 0;
}
