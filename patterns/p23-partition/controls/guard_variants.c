/* p23 controls -- NOT rungs. Two questions the shipped tree cannot answer.
 *
 *   ../NOTES.md 7 (control B) and ../NOTES.md 8 (control A).
 *
 * A. WHICH GUARD? `spec.md` pins `i < j` on both inner scans. Two other
 *    spellings are memory-safe and one of them is what a careless hardener
 *    reaches for. This file builds all three and shows what each costs and what
 *    each COMPUTES:
 *
 *      k_ij     while (i < j && scr[i]   <= pv) i++;   <- SHIPPED
 *               while (i < j && scr[j-1] >= pv) j--;
 *      k_mz     while (i < m && scr[i]   <= pv) i++;   <- the ALTERNATIVE 
 *               while (j > 0 && scr[j-1] >= pv) j--;
 *      k_bug    while (          scr[i]  <= pv) i++;   <- R1
 *               while (          scr[j-1]>= pv) j--;
 *
 *    THE ANSWER IS NOT THE ONE THIS FILE WAS WRITTEN TO SHOW. `k_mz` was
 *    expected to be *"safe, and WRONG"* -- to let the upward cursor pass the
 *    downward one and return a non-partition-point. It does not: `k_ij` and
 *    `k_mz` print the same checksum on every record tried here, and
 *    `guard_equiv.py` extends that to 800 000 randomised records over two
 *    alphabets with ZERO differences. After an exchange `scr[j] > pv` and
 *    `scr[i-1] < pv`, so each scan stops at the other cursor whatever its guard
 *    says. **`../spec.md` therefore pins a SPELLING here, not a semantics**, and
 *    the corrected claim is in `../c/kernel_hardened.c`. `k_bug` is the
 *    contrast: no guard at all, and it leaves the array in both directions.
 *
 * B. THE TEXTBOOK PIVOT DOES NOT RESCUE `<=`/`>=`. Real Hoare partition takes
 *    `pv = scr[0]`, which is what makes the bare scans self-terminating -- with
 *    STRICT comparisons. `k_selfpivot` takes the pivot from the array and keeps
 *    the non-strict comparisons this pattern pins, on an ALL-EQUAL record: the
 *    upward scan still leaves the array, because `<=` refuses to stop on the
 *    sentinel. That is the second, better-known form of this bug and it is why
 *    ../spec.md pins the operator in every rung.
 *
 * Build and run: ./run.sh  (writes controls.log beside this file)
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define SCR 64
#define NOINL __attribute__((noinline))

static uint8_t blob[4096];
static size_t blob_len;

static void put32(size_t p, uint32_t v)
{
    blob[p] = (uint8_t)(v & 0xff);
    blob[p + 1] = (uint8_t)((v >> 8) & 0xff);
    blob[p + 2] = (uint8_t)((v >> 16) & 0xff);
    blob[p + 3] = (uint8_t)((v >> 24) & 0xff);
}

/* one window, one record: nelem bytes, `nlow` of them below `pv`, `neq` equal,
 * the rest above; `mode` 1 makes every byte equal to `pv` (control B). */
static void build(unsigned n, unsigned pv, unsigned nlow, unsigned neq, int mode)
{
    unsigned k;
    size_t p = 12;
    unsigned seed = 12345u;
    put32(0, 1);
    put32(4, n);
    put32(8, pv);
    for (k = 0; k < n; k++) {
        unsigned b;
        seed = seed * 1103515245u + 12345u;
        if (mode == 1)
            b = pv;
        else if (k < nlow)
            b = (pv == 0) ? 0 : (seed >> 16) % pv;
        else if (k < nlow + neq)
            b = pv;
        else
            b = pv + 1 + ((seed >> 16) % (255 - pv));
        blob[p + k] = (uint8_t)b;
    }
    blob_len = p + n;
}

#define PRELUDE                                                             \
    uint8_t scr[SCR];                                                       \
    size_t nrec, rec, p, q, i, j, nelem, m;                                 \
    uint64_t acc = 0;                                                       \
    uint8_t pv, t;                                                          \
    if (len < 4) return 0;                                                  \
    nrec = (size_t)buf[0] + 256 * (size_t)buf[1] + 65536 * (size_t)buf[2]   \
        + 16777216 * (size_t)buf[3];                                        \
    if (nrec == 0) return 0;                                                \
    memset(scr, 0, sizeof scr);                                             \
    p = 4;                                                                  \
    for (rec = 0; rec < nrec; rec++) {                                      \
        if (len - p < 8) break;                                             \
        nelem = (size_t)buf[p] + 256 * (size_t)buf[p + 1]                   \
            + 65536 * (size_t)buf[p + 2] + 16777216 * (size_t)buf[p + 3];   \
        pv = buf[p + 4];                                                    \
        p += 8;                                                             \
        m = nelem < SCR ? nelem : SCR;                                      \
        if (len - p < nelem) break;                                         \
        memcpy(scr, buf + p, m);                                            \
        p += nelem;                                                         \
        i = 0;                                                              \
        j = m;

#define EPILOGUE                                                            \
        for (q = 0; q < m; q++)                                             \
            acc = acc * 31 + (uint64_t)scr[q];                              \
        acc = acc * 31 + (uint64_t)i;                                       \
    }                                                                       \
    return acc * 31 + (uint64_t)nrec;

#define EXCHANGE                                                            \
            if (i < j) {                                                    \
                t = scr[i];                                                 \
                scr[i] = scr[j - 1];                                        \
                scr[j - 1] = t;                                             \
                i++;                                                        \
                j--;                                                        \
            }

NOINL static uint64_t k_ij(const uint8_t *buf, size_t len)      /* SHIPPED */
{
    PRELUDE
        while (i < j) {
            while (i < j && scr[i] <= pv) i++;
            while (i < j && scr[j - 1] >= pv) j--;
            EXCHANGE
        }
    EPILOGUE
}

NOINL static uint64_t k_mz(const uint8_t *buf, size_t len) /* EQUIVALENT */
{
    PRELUDE
        while (i < j) {
            while (i < m && scr[i] <= pv) i++;
            while (j > 0 && scr[j - 1] >= pv) j--;
            EXCHANGE
        }
    EPILOGUE
}

NOINL static uint64_t k_bug(const uint8_t *buf, size_t len)          /* R1 */
{
    PRELUDE
        while (i < j) {
            while (scr[i] <= pv) i++;
            while (scr[j - 1] >= pv) j--;
            EXCHANGE
        }
    EPILOGUE
}

/* CONTROL B: the TEXTBOOK pivot, taken from the array, with the non-strict
 * comparisons this pattern pins. Unguarded scans, exactly as a sort author
 * writes them when the sentinel argument is believed to apply. */
NOINL static uint64_t k_selfpivot(const uint8_t *buf, size_t len)
{
    uint8_t scr[SCR];
    size_t nrec, rec, p, q, i, j, nelem, m;
    uint64_t acc = 0;
    uint8_t sp, t;

    if (len < 4)
        return 0;
    nrec = (size_t)buf[0] + 256 * (size_t)buf[1] + 65536 * (size_t)buf[2]
        + 16777216 * (size_t)buf[3];
    if (nrec == 0)
        return 0;
    memset(scr, 0, sizeof scr);
    p = 4;
    for (rec = 0; rec < nrec; rec++) {
        if (len - p < 8)
            break;
        nelem = (size_t)buf[p] + 256 * (size_t)buf[p + 1]
            + 65536 * (size_t)buf[p + 2] + 16777216 * (size_t)buf[p + 3];
        p += 8;
        m = nelem < SCR ? nelem : SCR;
        if (len - p < nelem)
            break;
        memcpy(scr, buf + p, m);
        p += nelem;
        i = 0;
        j = m;
        if (m != 0) {
            sp = scr[0];                /* THE TEXTBOOK CHOICE */
            while (i < j) {
                while (scr[i] <= sp)
                    i++;
                while (scr[j - 1] >= sp)
                    j--;
                if (i < j) {
                    t = scr[i];
                    scr[i] = scr[j - 1];
                    scr[j - 1] = t;
                    i++;
                    j--;
                }
            }
        }
        for (q = 0; q < m; q++)
            acc = acc * 31 + (uint64_t)scr[q];
        acc = acc * 31 + (uint64_t)i;
    }
    return acc * 31 + (uint64_t)nrec;
}

int main(int argc, char **argv)
{
    unsigned n, pv, nlow, neq;
    int mode;
    uint64_t r;
    if (argc < 7) {
        fprintf(stderr,
                "usage: %s ij|mz|bug|selfpivot <nelem> <pv> <nlow> <neq> <mode>\n",
                argv[0]);
        return 2;
    }
    n = (unsigned)strtoul(argv[2], NULL, 10);
    pv = (unsigned)strtoul(argv[3], NULL, 10);
    nlow = (unsigned)strtoul(argv[4], NULL, 10);
    neq = (unsigned)strtoul(argv[5], NULL, 10);
    mode = (int)strtol(argv[6], NULL, 10);
    build(n, pv, nlow, neq, mode);
    if (!strcmp(argv[1], "ij")) r = k_ij(blob, blob_len);
    else if (!strcmp(argv[1], "mz")) r = k_mz(blob, blob_len);
    else if (!strcmp(argv[1], "bug")) r = k_bug(blob, blob_len);
    else r = k_selfpivot(blob, blob_len);
    printf("%s n=%u pv=%u nlow=%u neq=%u mode=%d -> %llu\n",
           argv[1], n, pv, nlow, neq, mode, (unsigned long long)r);
    return 0;
}
