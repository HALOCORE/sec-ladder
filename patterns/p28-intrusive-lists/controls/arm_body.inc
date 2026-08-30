/* p28 CONTROLS -- ONE kernel body, included TWICE, with `SLB_HARDEN` 0 (R1, the
 * bug) and 1 (R1h). `controls/arm_sites.c` is the only file that includes it and
 * `controls/harm_sites.py` is the only thing that builds that.
 *
 * ⚠ **This is NOT a rung and must never become one.** `controls/safety_line.py`
 * explains why: `harness/check.py`'s `forbidden` audit reads the rung sources as
 * TEXT, so a kernel body hidden in an `.inc` would be outside the audit. The
 * shipped rungs are `c/kernel.c` and `c/kernel_hardened.c`, written out in full,
 * and `safety_line.py` proves by preprocessing that they differ by the splice
 * and nothing else. The include-twice construction lives HERE, where the two
 * arms have to be in ONE binary and where nothing depends on it being the rung.
 *
 * It differs from `c/kernel.c` in exactly two ways, both marked below:
 *
 *   * `#if SLB_HARDEN` selects the safety line, so the two arms are the same
 *     text by construction;
 *   * `#if SLB_SITES` counts, in the HARDENED arm and BEFORE the free, which
 *     branch of the splice TRIM takes. That is the row's own claim about WHERE
 *     the dangling pointer would be, computed with no undefined behaviour at
 *     all:
 *
 *         victim->hp == NULL   the victim is the CHAIN HEAD, so the buggy rung
 *                              leaves the dangling pointer in `bucket[vb]`
 *         victim->hp != NULL   the victim is FURTHER DOWN the chain, so the
 *                              buggy rung leaves it inside ANOTHER HEAP
 *                              OBJECT -- `victim->hp->hn`
 *
 *     ⚠ It is computed in the HARDENED arm on purpose. Reading `bucket[vb]` or
 *     a predecessor's `hn` after the free in the buggy arm would answer the same
 *     question by committing the very use-after-free the control is measuring,
 *     and a control that has to execute the bug to observe it proves nothing
 *     about where the bug is. Both arms take the same branch, because the branch
 *     is decided by `victim->hp`, which both arms compute identically. */

SLB_NOINLINE uint64_t KNAME(const uint8_t *buf, size_t buf_len, size_t off,
                            size_t len)
{
    struct p28_obj *bucket[P28_NB];
    struct p28_obj *head, *tail, *n, *victim;
    size_t nops, o, p, nmade, b, steps;
    uint8_t c, a;
    int found;
    uint64_t acc = 0;

    (void)buf_len;

    if (len < 4)
        return 0;
    nops = (size_t)buf[off] + 256 * (size_t)buf[off + 1]
        + 65536 * (size_t)buf[off + 2] + 16777216 * (size_t)buf[off + 3];
    if (nops == 0)
        return 0;

    for (b = 0; b < P28_NB; b++)
        bucket[b] = NULL;
    head = NULL;
    tail = NULL;
    nmade = 0;
    p = 4;

    for (o = 0; o < nops; o++) {
        if (len - p < 2)
            break;
        c = buf[off + p];
        a = buf[off + p + 1];
        p += 2;
        b = (size_t)(a % P28_NB);

        if (c % 4 == 0) {
            n = bucket[b];
            steps = 0;
            found = 0;
            while (n != NULL && steps < P28_SLOTS) {
                steps++;
                if (n->key == a) {
                    found = 1;
                    break;
                }
                n = n->hn;
            }
            if (found) {
                n->val = (uint8_t)(a * 7u + 1u);
                acc = acc * 31 + (uint64_t)a;
            } else if (nmade < P28_SLOTS) {
                n = (struct p28_obj *)malloc(sizeof *n);
                if (n == NULL)
                    abort();
                n->key = a;
                n->val = (uint8_t)(a * 7u + 1u);
                n->lp = NULL;
                n->ln = head;
                if (head != NULL)
                    head->lp = n;
                else
                    tail = n;
                head = n;
                n->hp = NULL;
                n->hn = bucket[b];
                if (bucket[b] != NULL)
                    bucket[b]->hp = n;
                bucket[b] = n;
                nmade++;
                acc = acc * 31 + (uint64_t)a;
            } else {
                acc = acc * 31 + P28_SENT;
            }
        } else if (c % 4 == 1) {
            n = bucket[b];
            steps = 0;
            found = 0;
            while (n != NULL && steps < P28_SLOTS) {
                steps++;
                if (n->key == a) {
                    found = 1;
                    break;
                }
                n = n->hn;
            }
            if (found)
                acc = acc * 31 + (uint64_t)n->val;
            else
                acc = acc * 31 + P28_SENT;
        } else if (c % 4 == 2) {
            n = bucket[b];
            steps = 0;
            found = 0;
            while (n != NULL && steps < P28_SLOTS) {
                steps++;
                if (n->key == a) {
                    found = 1;
                    break;
                }
                n = n->hn;
            }
            if (found) {
                if (n->hp != NULL)
                    n->hp->hn = n->hn;
                else
                    bucket[b] = n->hn;
                if (n->hn != NULL)
                    n->hn->hp = n->hp;
                if (n->lp != NULL)
                    n->lp->ln = n->ln;
                else
                    head = n->ln;
                if (n->ln != NULL)
                    n->ln->lp = n->lp;
                else
                    tail = n->lp;
                free(n);
                acc = acc * 31 + 2;
            } else {
                acc = acc * 31 + P28_SENT;
            }
        } else {
            if (tail != NULL) {
                victim = tail;
                if (victim->lp != NULL)
                    victim->lp->ln = NULL;
                else
                    head = NULL;
                tail = victim->lp;
#if SLB_SITES
                /* Which site would hold the dangling pointer? Computed BEFORE
                 * the free, so this arm executes no undefined behaviour. */
                if (victim->hp != NULL)
                    p28_site_interior++;
                else
                    p28_site_head++;
#endif
#if SLB_HARDEN
                /* ===================== THE SAFETY LINE ===================== */
                {
                    size_t vb = (size_t)(victim->key % P28_NB);
                    if (victim->hp != NULL)
                        victim->hp->hn = victim->hn;
                    else
                        bucket[vb] = victim->hn;
                    if (victim->hn != NULL)
                        victim->hn->hp = victim->hp;
                }
                /* ========================================================== */
#endif
                free(victim);
                acc = acc * 31 + 3;
            } else {
                acc = acc * 31 + P28_SENT;
            }
        }
    }

    n = head;
    while (n != NULL) {
        struct p28_obj *nx = n->ln;
        free(n);
        n = nx;
    }
    return acc * 31 + (uint64_t)nmade;
}
