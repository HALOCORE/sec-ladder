/* p49 rung R1 -- idiomatic C99 interned / deduplicated string pool. THE BUG:
 * a WRITE through a buffer the record does not own.
 *
 * CWE-1250-shaped in the port and CWE-471 (modification of assumed-immutable
 * data) in this reduction: the interned buffer is shared BY DESIGN and is
 * assumed immutable by every record that borrows it, and the cycle-breaker
 * mutates it in place.
 *
 * **The missing block is the copy-on-write test `if (rshd[t])`**, at the ONE
 * site marked below, and it is the only difference between this file and
 * c/kernel_hardened.c. `../controls/safety_line.py` preprocesses both and diffs
 * them, so that claim is measured rather than asserted.
 *
 * ⚠⚠ **THIS RUNG EXECUTES NO UNDEFINED BEHAVIOUR AT ALL.** Nothing is
 * allocated, nothing is freed, no pointer dangles, and every index is inside
 * `mem[0 .. P49_MEM)` -- c/kernel.h has the four-line proof. ASan and UBSan are
 * therefore SILENT on every input including the adversarial ones, at both
 * optimisation levels on both compilers (../NOTES.md 2), and **the checksum is
 * the only instrument this row has**.
 *
 * **What this rung KEEPS.** The `nrec < P49_NREC` guard, the `nrec > 0` guards
 * on BREAK and READ, both capacity tests (`abump + w > P49_ARENA` and
 * `pbump + w > P49_MEM`), the whole dedup table, and the `rshd[]` array itself
 * -- which this rung MAINTAINS and folds into the answer in the epilogue but
 * never CONSULTS before writing. **The whole of the bug is that a write through
 * a borrowed buffer does not ask whether the buffer is the writer's to change.**
 *
 * ⚠ `rshd[]` is live in this rung, not dead: the epilogue folds it, which is
 * this kernel's reduction of the port's `"interned":true/false` API field. Were
 * it dead, both compilers would delete the array here and the R1-vs-R1h
 * gradient would price the bookkeeping instead of the check.
 *
 * ⚠ **THIS RUNG PERFORMS NO COPY AT ALL** -- the only copy in the pattern is the
 * one c/kernel_hardened.c's safety line makes, and it is a BYTE LOOP over ranges
 * that cannot overlap rather than a `memcpy`. p49 is not p08: c/kernel.h says
 * why, and ../controls/no_overlap.py re-derives, from the shipped blobs on every
 * run, that every copy is disjoint and that two records' content ranges either
 * COINCIDE EXACTLY or are disjoint -- never partial, which is the only kind p08
 * has.
 *
 * Unsigned overflow wraps by definition (C99 6.2.5p9), so `acc*31 + v` needs no
 * special spelling. */
#include "kernel.h"

#define P49_MEM 64u
#define P49_ARENA 20u
#define P49_NENT 8u
#define P49_NREC 12u
#define P49_NKEY 7u
#define P49_MAXW 6u
#define P49_THRESH 4u
#define P49_SENT 251u

/* A content byte. The string a record holds is
 * `cbyte(key,0) .. cbyte(key,w-1)`, so the pair `(key, w)` names the string and
 * nothing else does -- which is what makes the dedup table's `(ekey, elen)`
 * comparison an exact content comparison rather than a hash. */
static uint8_t p49_cbyte(uint8_t key, uint8_t j)
{
    return (uint8_t)(key * 7u + j * 13u + 1u);
}

/* Materialise a string into the pool. */
static void p49_fill(uint8_t *m, size_t base, uint8_t key, uint8_t w)
{
    uint8_t j;
    for (j = 0; j < w; j++)
        m[base + j] = p49_cbyte(key, j);
}

/* Fold a string out of the pool. */
static uint64_t p49_fold(const uint8_t *m, size_t base, uint8_t w, uint64_t acc)
{
    uint8_t j;
    for (j = 0; j < w; j++)
        acc = acc * 31 + (uint64_t)m[base + j];
    return acc;
}

/* THE DEDUP LOOKUP. Returns `nent` when the string is absent. */
static size_t p49_find(const uint8_t *ekey, const uint8_t *elen, size_t nent,
                       uint8_t key, uint8_t w)
{
    size_t k;
    for (k = 0; k < nent; k++)
        if (ekey[k] == key && elen[k] == w)
            return k;
    return nent;
}

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t buf_len, size_t off,
                             size_t len)
{
    uint8_t mem[P49_MEM] = { 0 };
    uint8_t ekey[P49_NENT] = { 0 }, elen[P49_NENT] = { 0 }, eoff[P49_NENT] = { 0 };
    uint8_t roff[P49_NREC] = { 0 }, rlen[P49_NREC] = { 0 }, rshd[P49_NREC] = { 0 };
    size_t nops, o, p, nent, nrec, abump, pbump, f, t;
    uint8_t c, a, key, w;
    uint64_t acc = 0, v;

    (void)buf_len; /* p49's bound is not this one -- it is the pool's extent. */

    if (len < 4)
        return 0;
    nops = (size_t)buf[off] + 256 * (size_t)buf[off + 1]
        + 65536 * (size_t)buf[off + 2] + 16777216 * (size_t)buf[off + 3];
    if (nops == 0)
        return 0;

    nent = 0;
    nrec = 0;
    abump = 0;
    pbump = P49_ARENA;
    p = 4;

    for (o = 0; o < nops; o++) {
        if (len - p < 2)
            break;
        c = buf[off + p];
        a = buf[off + p + 1];
        p += 2;
        w = (uint8_t)(1u + a % P49_MAXW);
        key = (uint8_t)(a % P49_NKEY);
        if (c % 4 == 0 || c % 4 == 1) {
            /* DEFINE a record whose content is the `w`-byte string `key`. */
            if (nrec >= P49_NREC) {
                v = P49_SENT;
            } else if (w < P49_THRESH) {
                /* THE INLINE THRESHOLD, and it is a real test: `w` comes from
                 * the file, so this branch and the one below are BOTH live and
                 * `rshd[]` genuinely varies. */
                f = p49_find(ekey, elen, nent, key, w);
                if (f == nent) {
                    if (nent >= P49_NENT || abump + w > P49_ARENA) {
                        v = P49_SENT;
                    } else {
                        p49_fill(mem, abump, key, w);
                        ekey[nent] = key;
                        elen[nent] = w;
                        eoff[nent] = (uint8_t)abump;
                        roff[nrec] = (uint8_t)abump;
                        rlen[nrec] = w;
                        rshd[nrec] = 1;
                        nent = nent + 1;
                        abump = abump + w;
                        nrec = nrec + 1;
                        v = (uint64_t)a;
                    }
                } else {
                    /* A DEDUP HIT. The new record BORROWS the buffer an earlier
                     * record already holds. **This is correct, it is what the
                     * pool is for, and it is not undefined behaviour.** */
                    roff[nrec] = eoff[f];
                    rlen[nrec] = w;
                    rshd[nrec] = 1;
                    nrec = nrec + 1;
                    v = (uint64_t)a;
                }
            } else {
                if (pbump + w > P49_MEM) {
                    v = P49_SENT;
                } else {
                    p49_fill(mem, pbump, key, w);
                    roff[nrec] = (uint8_t)pbump;
                    rlen[nrec] = w;
                    rshd[nrec] = 0;
                    pbump = pbump + w;
                    nrec = nrec + 1;
                    v = (uint64_t)a;
                }
            }
        } else if (c % 4 == 2) {
            /* BREAK -- the cycle-breaker. It zeroes the first byte of a
             * record's content. */
            if (nrec == 0) {
                v = P49_SENT;
            } else {
                t = (size_t)a % nrec;
                /* >>> THE SAFETY LINE IS ABSENT HERE, AND ITS ABSENCE IS THE
                 * WHOLE BUG. c/kernel_hardened.c asks `if (rshd[t])` -- is this
                 * buffer mine to write? -- and takes a private copy first. This
                 * rung writes through whatever the record points at, which on a
                 * deduplicated record is storage another record owns. <<< */
                mem[roff[t]] = 0;
                v = 2;
            }
        } else {
            /* READ -- fold a record's content. */
            if (nrec == 0) {
                v = P49_SENT;
            } else {
                t = (size_t)a % nrec;
                v = p49_fold(mem, roff[t], rlen[t], 0);
            }
        }
        acc = acc * 31 + v;
    }

    /* Fold EVERY record, so a corrupted neighbour cannot hide, and fold each
     * record's ownership flag beside its content: `rshd[t]` is this kernel's
     * reduction of the port's `"interned":true/false` field, and it is what
     * makes the PROVENANCE repair benign-observable while copy-on-write is not
     * (c/kernel.h, ../controls/spellings.py). */
    for (t = 0; t < nrec; t++) {
        acc = p49_fold(mem, roff[t], rlen[t], acc);
        acc = acc * 31 + (uint64_t)rshd[t];
    }
    return acc * 31 + (uint64_t)nrec;
}
