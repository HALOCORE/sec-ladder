/* p32 CONTROLS -- the storage experiment's kernel body, included TWICE by
 * `arm_malloc.c` with `P32_HARDEN` 0 and 1, so that the control's own two arms
 * provably differ by the safety line alone.
 *
 * ⚠ **This file is a CONTROL and not a rung.** The rungs are
 * `../c/kernel.c` and `../c/kernel_hardened.c`, written out in full because the
 * gate's `forbidden` audit reads the rung sources as TEXT: a kernel body moved
 * into an `.inc` would leave that audit entirely, which is the honest-refactor
 * escape route `harness/check.py::forbidden_only_sources` names by name. The
 * include-twice construction lives here, where nothing depends on it, and
 * `../controls/safety_line.py` makes the same claim about the SHIPPED files by
 * PREPROCESSING them and diffing -- which is a measurement rather than a
 * construction that cannot fail.
 *
 * `-DP32_ARENA` gives the pool storage the pattern ships; the default is
 * per-block `malloc`/`free`. THE ALGORITHM, THE FREE LIST, THE GENERATIONS, THE
 * HANDLE REGISTERS, THE FOLD AND THE SAFETY LINE ARE BYTE-IDENTICAL BETWEEN THE
 * TWO. Only where the bytes live changes. That is the experiment. */

static uint64_t KNAME(const uint8_t *buf, size_t off, size_t len)
{
#ifdef P32_ARENA
    uint8_t pool[SLOTS * BLK];
#else
    uint8_t *blk[SLOTS];
#endif
    uint8_t nx[SLOTS];
    uint32_t gen[SLOTS];
    uint8_t regs[NREG];
    uint32_t regg[NREG];
    uint8_t freehead;
    size_t nops, o, p, j, r, nalloc;
    uint8_t c, a, h;
    uint32_t g;
    uint64_t acc = 0, v;

    if (len < 4)
        return 0;
    nops = (size_t)buf[off] + 256 * (size_t)buf[off + 1]
        + 65536 * (size_t)buf[off + 2] + 16777216 * (size_t)buf[off + 3];
    if (nops == 0)
        return 0;

    for (j = 0; j < SLOTS; j++) {
        nx[j] = (uint8_t)((j + 1 < SLOTS) ? (j + 1) : NIL);
        gen[j] = 0;
#ifdef P32_ARENA
        pool[j * BLK + 0] = 0;
        pool[j * BLK + 1] = 0;
        pool[j * BLK + 2] = 0;
        pool[j * BLK + 3] = 0;
#else
        blk[j] = NULL;
#endif
    }
    for (j = 0; j < NREG; j++) {
        regs[j] = NIL;
        regg[j] = 0;
    }
    freehead = 0;
    nalloc = 0;
    p = 4;
    (void)g;

    for (o = 0; o < nops; o++) {
        if (len - p < 2)
            break;
        c = buf[off + p];
        a = buf[off + p + 1];
        p += 2;
        r = (size_t)(a % NREG);
        if (c % 4 == 0) {
            if (freehead == NIL) {
                v = SENT;
            } else {
                uint8_t s = freehead;
                uint32_t gs;
                freehead = nx[s];
#ifndef P32_ARENA
                blk[s] = (uint8_t *)malloc(BLK);
                if (blk[s] == NULL)
                    abort();
#endif
                P32_PAY(s)[0] = a;
                P32_PAY(s)[1] = (uint8_t)(a * 7u + 1u);
                regs[r] = s;
                gs = gen[s];
                regg[r] = gs;
                nalloc++;
                v = (uint64_t)s + 8 * (uint64_t)gs;
            }
        } else {
            h = regs[r];
            g = regg[r];
            if (h == NIL) {
                v = SENT;
            }
#if P32_HARDEN
            /* ===================== THE SAFETY LINE ======================== */
            else if (gen[h] != g) {
                v = SENT;
            }
#endif
            else if (c % 4 == 1) {
#ifndef P32_ARENA
                /* `blk[h]` is deliberately NOT nulled -- p27's argument, and it
                 * is MEASURED here: nulling it turns the stale read into a NULL
                 * dereference (a SIGSEGV, a different bug class) and turns the
                 * double free into a no-op `free(NULL)`, which is how the first
                 * draft of this control reported "LeakSanitizer only" where the
                 * real answer is `attempting double-free`. */
                free(blk[h]);
#endif
                gen[h] = gen[h] + 1;
                nx[h] = freehead;
                freehead = h;
                v = 1;
            } else if (c % 4 == 2) {
                v = (uint64_t)P32_PAY(h)[1];
            } else {
                P32_PAY(h)[1] = (uint8_t)(a * 13u + 3u);
                v = 3;
            }
        }
        acc = acc * 31 + v;
    }

#ifndef P32_ARENA
    /* Teardown frees every block that is not on the free list. The walk is
     * bounded by SLOTS, so under the BUGGY arm's self-looping list it does not
     * see the slots the loop lost and frees them a SECOND time -- a consequence
     * of the bug, not an extra one. */
    {
        uint8_t onfree[SLOTS];
        uint8_t t;
        unsigned sd;
        for (j = 0; j < SLOTS; j++)
            onfree[j] = 0;
        t = freehead;
        sd = 0;
        while (t != NIL && sd < SLOTS) {
            onfree[t] = 1;
            t = nx[t];
            sd++;
        }
        for (j = 0; j < SLOTS; j++)
            if (!onfree[j] && blk[j] != NULL)
                free(blk[j]);
    }
#endif
    return acc * 31 + (uint64_t)nalloc;
}
