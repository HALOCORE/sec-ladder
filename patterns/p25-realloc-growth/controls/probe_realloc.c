/* p25 CONTROLS -- the `realloc` interposer `reloc_probe.py` links against.
 *
 * ⚠ **The point of this file is that the kernel under it is the SHIPPED one.**
 * `TASK_134` refused p25 on `moved = 0/12` measured with a hand-rolled driver,
 * and that number was a fact about THAT driver's heap topology rather than about
 * C. So this probe changes nothing about the program: `reloc_probe.py` compiles
 * `../c/kernel.c`, `../c/main.c` and `common/driver.c` unmodified, with
 * `-Drealloc=slb_p25_probe_realloc` on the command line, and links this
 * translation unit -- compiled WITHOUT that define -- to supply the name.
 *
 * The macro also renames `<stdlib.h>`'s declaration in the kernel's translation
 * unit, which is exactly what is wanted: the prototype the kernel sees is
 * `void *slb_p25_probe_realloc(void *, size_t)` and it matches this definition.
 *
 * What is recorded per call: the old pointer, the new pointer, the requested
 * size, and whether the block MOVED. The events are printed at exit as one line
 * each, so the parser in `reloc_probe.py` reads a fact per growth rather than a
 * summary this file computed.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#define SLB_P25_MAXEV 4096

struct slb_p25_ev {
    void *old_p;
    void *new_p;
    size_t size;
};

static struct slb_p25_ev slb_p25_ev[SLB_P25_MAXEV];
static size_t slb_p25_nev;
static int slb_p25_registered;

static void slb_p25_dump(void)
{
    size_t i;
    for (i = 0; i < slb_p25_nev; i++) {
        fprintf(stderr, "P25REALLOC %zu old=%p new=%p size=%zu moved=%d\n",
                i, slb_p25_ev[i].old_p, slb_p25_ev[i].new_p,
                slb_p25_ev[i].size,
                (slb_p25_ev[i].old_p != NULL
                 && slb_p25_ev[i].old_p != slb_p25_ev[i].new_p) ? 1 : 0);
    }
    fprintf(stderr, "P25REALLOC-TOTAL %zu\n", slb_p25_nev);
}

void *slb_p25_probe_realloc(void *p, size_t n);

void *slb_p25_probe_realloc(void *p, size_t n)
{
    void *q;
    if (!slb_p25_registered) {
        slb_p25_registered = 1;
        atexit(slb_p25_dump);
    }
    q = realloc(p, n);
    if (slb_p25_nev < SLB_P25_MAXEV) {
        slb_p25_ev[slb_p25_nev].old_p = p;
        slb_p25_ev[slb_p25_nev].new_p = q;
        slb_p25_ev[slb_p25_nev].size = n;
        slb_p25_nev++;
    }
    return q;
}
