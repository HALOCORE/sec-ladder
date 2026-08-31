/* p34 POSITIVE CONTROL for the **ASan** column.
 *
 * p34's harm is a touch of a heap object whose reference count was driven to
 * zero while a live alias still named it. This file commits exactly that, in
 * isolation, with no loop and no input, and made to escape through a `volatile`
 * sink so that clang cannot eliminate the `malloc`/`free` pair -- `p31`'s
 * malloc-elision artefact silently disarmed the first spelling of `p32`'s
 * control in this same family.
 *
 * ⚠⚠ **AND IT LICENSES THE ASan COLUMN ONLY.** `-fsanitize=undefined` has no
 * use-after-free check at all, so on a UBSan-only build this program runs to
 * completion with ZERO diagnostics -- which is indistinguishable from a UBSan
 * that is not linked in. That is the gap `.temp/mgr147/NOTES.md` found in
 * `TASK_143`'s demonstration, and `ctl_ubsan.c` is the other half.
 *
 * **A POSITIVE CONTROL LICENSES ONLY THE DETECTOR IT FIRES IN.**
 * `controls/detectors.py` runs both and asserts that each fires where it should
 * and is silent where it should be. This matters more on p34 than on most rows,
 * because **UBSan's silence on this pattern is a published result**: p34's
 * undefined behaviour is entirely TEMPORAL and every index the kernel forms is
 * inside `stk[]` in both rungs, so there is nothing spatial for UBSan to see.
 *
 * Expected: ASan reports `heap-use-after-free`; the plain build prints a byte
 * and exits 0; the UBSan-only build prints a byte and exits 0.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define CTL_DLEN 8

struct ctl_obj {
    size_t rc;
    size_t len;
    uint8_t data[CTL_DLEN];
};

/* `volatile` so the pointer escapes and the allocation cannot be proved dead. */
static volatile void *slb_sink34;

int main(void)
{
    struct ctl_obj *o, *alias;
    o = (struct ctl_obj *)malloc(sizeof *o);
    if (o == NULL)
        abort();
    slb_sink34 = o;
    o->rc = 1;
    o->len = CTL_DLEN;
    memset(o->data, 0, CTL_DLEN);
    o->data[0] = 37;
    /* A SECOND REFERENCE, published and NOT retained -- p34's bug in one line. */
    alias = o;
    /* The release the first reference owes. The count reaches zero and the
     * object is freed while `alias` still names it. */
    o->rc = o->rc - 1;
    if (o->rc == 0)
        free(o);
    slb_sink34 = alias;
    /* THE HARM. MUST be reported by ASan. */
    printf("%u\n", (unsigned)alias->data[0]);
    return 0;
}
