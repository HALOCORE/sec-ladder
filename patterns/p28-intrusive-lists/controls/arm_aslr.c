/* p28 CONTROLS -- THE NEGATIVE CONTROL for `controls/repro.py`.
 *
 * p28's claim is that R1's checksum is REPRODUCIBLE on its adversarial inputs --
 * one distinct value in twenty runs -- **even though R1 reads freed heap**. That
 * claim is worth nothing unless the twenty-run instrument can report more than
 * one, and *"it reported one"* and *"it cannot report more than one"* look
 * identical from outside (`.memory/03-measurement.md` 19, and
 * `TASK_145_REPORT` 6a, where p32's version of this arm was found missing).
 *
 * So this kernel is built to be ASLR-dependent BY CONSTRUCTION and run through
 * the SAME twenty-run counter. It frees a chunk and reads USER OFFSET 0 -- the
 * word glibc's tcache overwrites with its safe-linked `next`, `(chunk >> 12) ^
 * next`, which is derived from the heap base. It MUST print more than one
 * distinct value; if it prints one, ASLR is off (or the runner is collapsing the
 * outputs) and every count `repro.py` reports is vacuous.
 *
 * ⚠ **It is deliberately p28's OWN failure mode and not an unrelated source of
 * entropy**: it reads a freed chunk, exactly as R1 does. What differs is WHICH
 * WORD it reads, and that is the whole of p28's layout note (`c/kernel.h`): p28
 * puts the four links FIRST, so tcache's two words land on `lp` and `ln` and the
 * `key`/`val`/`hn`/`hp` R1 actually reads SURVIVE. This arm reads the word that
 * does not survive. **The same run therefore exhibits the contrast the row
 * publishes rather than merely certifying the instrument.**
 *
 * ⚠ Built with `-Wno-use-after-free`: the read of the freed chunk is the
 * mechanism, not an accident, and gcc is right to warn. The warning is silenced
 * here and nowhere else in this pattern. */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

/* The same six-byte payload p28's object carries, with the links first -- but
 * read at offset 0, which is where p28's `lp` sits and where tcache writes. */
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
