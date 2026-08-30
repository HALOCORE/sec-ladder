/* p32 CONTROLS -- **the NEGATIVE CONTROL for `repro.py`, and it is the arm that
 * makes p32's reproducibility claim evidence at all.**
 *
 * `repro.py` runs each cell twenty times and reports how many DISTINCT values it
 * saw. p32's answer is *"1, everywhere"*. ⚠ **That reading is VACUOUS if the box
 * cannot produce more than one** -- if ASLR is off, if the runner collapses the
 * outputs, if the twenty runs are not really twenty processes. A reproducibility
 * test is evidence only once it has been shown capable of FAILING, and until
 * `TASK_147` `repro.py` shipped with nothing that could
 * (`TASK_145_REPORT` §6a; the manager demanded exactly this arm for `p28` in
 * `.memory/06-catalogue.md`).
 *
 * So: the same twenty-run instrument, pointed at a kernel that MUST give more
 * than one value.
 *
 *   cc -std=c99 -O1 arm_aslr.c && ./a.out
 *
 * The mechanism is `.temp/mgr146/aslr/k.c`'s, and it is deliberately p32's own
 * `c-malloc` failure mode rather than an unrelated source of entropy: free a
 * chunk and READ USER OFFSET 0 of it. glibc's tcache overwrites that word with
 * a safe-linked `next` pointer, `(chunk >> 12) ^ next`, which is derived from
 * the heap base and therefore MOVES WITH ASLR. That is exactly why
 * `controls/storage_arms.py`'s `adv-stale-read` cell on the `malloc` arm is
 * `NOT REPRO` while the arena arm is `32521` in all five of its builds -- so
 * this control also demonstrates, in eight lines, the contrast p32 publishes.
 *
 * ⚠ It reads freed heap on purpose. It is a CONTROL, never a rung, it is built
 * plain (no sanitiser -- ASan would abort it, which is the point of the shipped
 * `storage_arms.py` arm and not of this one), and nothing in the ladder matrix
 * links against it.
 *
 * It prints one unsigned decimal and nothing else, so `repro.py` can count
 * distinct stdout lines exactly as it does for a rung.
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

struct alr {
    uint64_t w0, w1;
    uint8_t key;
};

int main(void)
{
    struct alr *a, *b;
    uint64_t acc = 0;

    a = (struct alr *)malloc(sizeof *a);
    b = (struct alr *)malloc(sizeof *b);
    if (a == NULL || b == NULL)
        abort();
    a->w0 = 1;
    a->w1 = 2;
    a->key = 3;
    b->w0 = 4;
    b->w1 = 5;
    b->key = 6;
    free(b);
    free(a);                 /* a->w0 now holds the safe-linked next pointer */
    acc = acc * 31 + a->w0;  /* <- ASLR-dependent BY CONSTRUCTION */
    printf("%llu\n", (unsigned long long)acc);
    return 0;
}
