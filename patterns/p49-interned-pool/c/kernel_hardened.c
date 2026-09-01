/* p49 rung R1h -- c/kernel.c with THE SAFETY LINE, and nothing else changed.
 *
 * The safety line is COPY-ON-WRITE at the MUTATION site: before the
 * cycle-breaker writes, it asks whether the buffer is the record's to write, and
 * if it is not it takes a private copy and writes to that instead. The
 * marked block below is the entire difference between this file and
 * c/kernel.c; ../controls/safety_line.py preprocesses both and diffs them.
 *
 * ⚠ **THIS IS NOT UPSTREAM'S PATCH.** `CVE-2022-40304`'s fix (commit `644a89e`)
 * changes the PROVENANCE -- never borrow, always own -- which deletes the
 * deduplication and, `TASK_160` measured, CHANGES A BENIGN OBSERVABLE. This
 * spelling changes no benign observable at all: the copy-on-write path runs only
 * when a BREAK names a SHARED record, which no non-adversarial window does
 * (../model.py::no_share_break_problems re-derives that from the shipped blob on
 * every gate invocation, and ../inputs/gen.py refuses to write one).
 * ../controls/spellings.py builds the provenance arm and prices it beside this
 * one.
 *
 * ⚠ **THE REPAIR CAN REFUSE, AND THAT IS THE HONEST PRICE OF COPY-ON-WRITE.**
 * Un-sharing needs storage the bug does not need. With the private region
 * exhausted this rung folds SENT and does not write at all -- still memory-safe,
 * still value-safe, and one behaviour the buggy rung does not have.
 * ../NOTES.md 3c measures how often that branch fires.
 *
 * ⚠ **The copy is a BYTE LOOP over ranges that cannot overlap.** The
 * destination is `pbump`, which is at or above `P49_ARENA`; the source is a
 * SHARED record's content, which lies wholly inside `mem[0 .. P49_ARENA)`. So
 * `src + w <= P49_ARENA <= dst` always, this is not a `memmove` site, and p49 is
 * not p08 (c/kernel.h; ../controls/no_overlap.py re-derives it).
 *
 * Everything else in this file is c/kernel.c character for character. */
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
    uint8_t c, a, key, w, j;
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
                /* >>> THE SAFETY LINE. Is this buffer mine to write? A
                 * deduplicated record BORROWS storage another record owns, so
                 * un-share first: take a private copy, point the record at it,
                 * and write there. c/kernel.c omits this whole block and writes
                 * through the alias. <<< */
                if (rshd[t]) {
                    if (pbump + rlen[t] > P49_MEM) {
                        v = P49_SENT;
                    } else {
                        for (j = 0; j < rlen[t]; j++)
                            mem[pbump + j] = mem[roff[t] + j];
                        roff[t] = (uint8_t)pbump;
                        rshd[t] = 0;
                        pbump = pbump + rlen[t];
                        mem[roff[t]] = 0;
                        v = 2;
                    }
                } else {
                    mem[roff[t]] = 0;
                    v = 2;
                }
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
     * reduction of the port's `"interned":true/false` field
     * (c/kernel.h, ../controls/spellings.py).
     *
     * ⚠ WHAT THIS FOLD IS AND IS NOT. It is SUFFICIENT to make the PROVENANCE
     * repair benign-observable. It is NOT NECESSARY, and the sentence that said
     * it was is WITHDRAWN (TASK_162 item 7, measured). Delete this one line from
     * all three arms and `provenance` STILL moves 2 of the 3 benign checksums --
     * because it also deletes the deduplication, so every record consumes
     * private bytes, the 44-byte private region fills (`sent_priv_full` 4 -> 398
     * on large.bin) and `nrec` changes (768 -> 762); the epilogue folds both of
     * those independently of the flag. Only `degenerate.bin`, where the two arms
     * agree on record count and refusals, needs the flag to separate them.
     * ../NOTES.md 3b has the table.
     *
     * ⚠ In THIS rung the flag also carries the copy-on-write's own trace: the
     * safety line above clears it, so the epilogue prices the repair's
     * bookkeeping as well as the corruption it prevents. */
    for (t = 0; t < nrec; t++) {
        acc = p49_fold(mem, roff[t], rlen[t], acc);
        acc = acc * 31 + (uint64_t)rshd[t];
    }
    return acc * 31 + (uint64_t)nrec;
}
