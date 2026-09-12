/* ph53 rung R1 -- PHP 5.0.0's class-declaration interface array, NARROWED.
 * THE BUG (CRASH-158, CWE-824).
 *
 * ============================================================================
 * PROVENANCE
 * ============================================================================
 *   php-5.0.0.tar.gz  sha256 5783e0c0ba94f165633a565fe73a83e59cf17b6880ef95fa
 *                            8f936dc6301d6919
 *   tar -xzOf <tarball> php-5.0.0/Zend/zend_compile.c | sed -n '2569,2572p'
 *   plus four pinned extra spans -- the count advance (:2584-2592), the
 *   compare-only consumer (:1947-1957), the faulting consumer
 *   (Zend/zend_operators.c:1530-1538), the init (:3740-3748) and the teardown
 *   (Zend/zend_opcode.c:152-168).  Every one of them is in ../spec.md's
 *   `provenance.extra_spans` with its own `extract_sha256`.
 *   Corpus row CRASH-158.  Tier `narrowed` -- ⚠ the catalogue says `verbatim`
 *   and it is WRONG; the DEFECT SPAN lifts byte-identically (which is why R1h
 *   patches onto it at zero fuzz) but the MECHANISM needs three frames in two
 *   files and two of them do not lift.  `TASK_PHP_040_REPORT.md` §5.1 itemises
 *   it and ../spec.md's `provenance.divergences` carries the ledger.
 *
 * ============================================================================
 * THE DEFECT, IN ONE LINE
 * ============================================================================
 * The count is advanced at COMPILE time and no slot is written:
 *
 *     opline->extended_value = CG(active_class_entry)->num_interfaces++;  :2591
 *
 * and then the storage is grown to that count and left indeterminate:
 *
 *     if (ce->num_interfaces > 0) {                                       :2570
 *         ce->interfaces = (zend_class_entry **) erealloc(ce->interfaces,
 *                          sizeof(zend_class_entry *)*ce->num_interfaces); :2571
 *     }
 *
 * `:3747-3748` set `num_interfaces = 0` and `interfaces = NULL`, so the
 * `erealloc` is a plain `malloc` and the WHOLE array is indeterminate.  A
 * consumer that runs before `ZEND_ADD_INTERFACE` has executed for every clause
 * reads a slot that is inside the block and was never written.
 *
 * ⚠⚠ THE READ IS IN BOUNDS.  Nothing is freed and nothing is past the end:
 * CWE-824 (uninitialised pointer), not CWE-125 (over-read).  `ph32` is the
 * cross-reference, sized to the LITERAL rather than the count.
 *
 * ============================================================================
 * WHAT NARROWING REMOVED, AND WHY NONE OF IT IS A SEMANTIC CHANGE
 * ============================================================================
 * 1. `TSRMLS_DC` / `TSRMLS_CC` (`:2542`, `:2584`, `zend_operators.c:1530`).
 *    Thread plumbing.
 *
 * 2. `zend_op` / `get_next_op(CG(active_op_array))` / `CG(implementing_class)`
 *    / `opline->extended_value` (`:2586-2590`).  PROJECTION: the opcode
 *    array's only role at these lines is to carry the compile-time index from
 *    phase 1 to phase 2, and the blob's op stream carries it instead.
 *    ⚠⚠ AND THE ROW DOES NOT REACH FOR THE EXECUTOR.  `ph49`'s warning applies
 *    verbatim: an extraction that reaches for the executor has built a
 *    different row.  THE BLOB IS THE OPCODE STREAM.
 *
 * 3. `instanceof_function`'s parent-chain walk (`zend_operators.c:1539-1546`).
 *    NARROWED: this row prices the SLOT READ, not the class-tree walk, so the
 *    recursive `instanceof_function(interfaces[i], ce)` becomes an identity
 *    test through the slot pointer.  The DEREFERENCE -- which is the fault --
 *    is kept, one per examined slot.
 *
 * 4. `zend_verify_abstract_class` / `do_verify_abstract_class` (`:2573-2579`).
 *    Inside the extracted span's following `if`; neither touches
 *    `ce->interfaces`.
 *
 * 5. `do_inherit_parent_constructor` and the ctor/dtor/clone `fn_flags` block
 *    (`:2546-2567`).  Same function, above the defect, does not touch
 *    `ce->interfaces`.
 *
 * ============================================================================
 * WHAT IS *NOT* CHANGED, AND MUST NOT BE
 * ============================================================================
 *   * `:2570`'s `if (ce->num_interfaces > 0)` guard stays.  It is the defect's
 *     own branch and both of its arms are in the measured corpus.
 *   * the allocator stays `erealloc` on a NULL pointer -- which is what
 *     `:3748` guarantees -- so the block really is fresh, uninitialised heap.
 *     `common-php/emalloc_shim.h` IS PHP 5.0.0's `_erealloc`/`_emalloc`.
 *   * both consumers ship.  `d09cdd9f71f3` lands at TWO severities and a
 *     kernel with one consumer could not show it.
 *   * `num_interfaces` stays `unsigned int` (`zend.h:335`, `zend_uint`).
 */

#include <stdint.h>
#include <stddef.h>
#include <string.h>

#include "kernel.h"

#define PHP_SHIM_IMPL /* exactly one TU defines the allocator state */
#include "emalloc_shim.h"

/* ---- window decoding.  Byte at a time, so no rung depends on alignment. --- */

static uint32_t ph53_rd32(const uint8_t *w, size_t o)
{
    return (uint32_t)w[o]
         | ((uint32_t)w[o + 1] << 8)
         | ((uint32_t)w[o + 2] << 16)
         | ((uint32_t)w[o + 3] << 24);
}

static uint64_t ph53_rd64(const uint8_t *w, size_t o)
{
    return (uint64_t)ph53_rd32(w, o) | ((uint64_t)ph53_rd32(w, o + 4) << 32);
}

/* ============ NARROWED: Zend/zend_operators.c:1530-1538 ==================
 * `instanceof_function_ex`'s interface loop -- THE FAULTING CONSUMER.
 *
 *     for (i=0; i<instance_ce->num_interfaces; i++) {                 :1534
 *         if (instanceof_function(instance_ce->interfaces[i], ce)) {   :1535
 *             return 1;
 *         }
 *     }
 *
 * `instanceof_function` is `instanceof_function_ex(instance_ce, ce, 0)`
 * (`:1552-1555`), whose own `while (instance_ce) { if (instance_ce == ce) ...`
 * DEREFERENCES the slot.  Narrowed to one dereference per examined slot: the
 * row prices the slot read and not the tree walk.
 *
 * ⚠ THE `||` DISJUNCT `interfaces[i] == target` IS DELIBERATELY ABSENT.  It is
 * redundant -- `p == q` implies `p->id == q->id` -- and its only effect would
 * be to SKIP the dereference on the matching slot.  A matching slot is written
 * by construction, so no behaviour moves; what it buys is that no rung's
 * control flow ever depends on an ADDRESS (`TASK_PHP_041.md` §2.3).
 *
 * Writes `*examined` (slots looked at) and `*matched_id` (0 if no match).  */
static int ph53_instanceof_ex(const ph53_ce *ce, const ph53_iface *target,
                              unsigned *examined, uint64_t *matched_id)
{
    unsigned i;
    for (i = 0; i < ce->num_interfaces; i++) {
        *examined = i + 1;
        /* :1535 -- THE DEREFERENCE.  On R1 `ce->interfaces[i]` may be a slot
         * this declaration never wrote; the value is whatever `malloc`
         * returned it holding, and this line follows it. */
        if (ce->interfaces[i]->id == target->id) {
            *matched_id = ce->interfaces[i]->id;
            return 1;
        }
    }
    return 0;
}
/* ========== end narrowed: zend_operators.c:1530-1538 ===================== */

/* ============ NARROWED: Zend/zend_compile.c:1947-1957 ====================
 * `zend_do_inherit_interfaces`'s dedup scan -- THE COMPARE-ONLY CONSUMER.
 *
 *     for (i = 0; i < ce_num; i++) {                                   :1950
 *         if (ce->interfaces[i] == entry) {                            :1951
 *             break;
 *         }
 *     }
 *
 * ⚠⚠ IT READS THE SLOT AND DOES NOT DEREFERENCE IT.  That is the whole reason
 * this kernel carries two consumers: `d09cdd9f71f3` turns the slot into NULL,
 * which makes the line above DEFINED AND CORRECT and the line at
 * `zend_operators.c:1535` a NULL dereference.  One hunk, two severities.
 *
 * Returns the index it stopped at -- `ce_num` when nothing matched, exactly as
 * upstream's `if (i == ce_num)` at `:1955` then tests.  */
static unsigned ph53_inherit_scan(const ph53_ce *ce, const ph53_iface *entry)
{
    unsigned i;
    for (i = 0; i < ce->num_interfaces; i++) {
        if (ce->interfaces[i] == entry) {      /* :1951 -- no dereference */
            break;
        }
    }
    return i;
}
/* ========== end narrowed: zend_compile.c:1947-1957 ======================= */

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t off, size_t len)
{
    const uint8_t *win = buf + off;
    ph53_iface pool[PH53_MAXP];
    unsigned idx[PH53_MAXD];
    ph53_ce ce_storage;
    /* ⚠ A POINTER, so that the extracted span is spelled exactly as upstream
     * spells it -- `ce->interfaces`, `ce->num_interfaces`.  In PHP `ce` really
     * is a `zend_class_entry *` (`CG(active_class_entry)`, `:2544`), so this is
     * fidelity rather than style: it makes `diff` against the tarball's
     * `:2569-2572` two identifiers wide. */
    ph53_ce *ce = &ce_storage;
    uint64_t acc = 0;
    unsigned n_decl, n_pool, n_ops, cap, k, o;

    php_shim_reset();                          /* PROTOCOL_PHP.md B1.3 */

    n_decl = (unsigned)(ph53_rd32(win, 0) % (uint32_t)(PH53_MAXD + 1));
    n_pool = (unsigned)(1u + ph53_rd32(win, 4) % (uint32_t)PH53_MAXP);
    cap    = (unsigned)((len - PH53_OPS_OFF) / PH53_OP_BYTES);
    n_ops  = (unsigned)(ph53_rd32(win, 8) % (uint32_t)(cap + 1u));

    /* The interfaces themselves.  NOT allocated: at `:2571` every interface
     * named by an `implements` clause is an existing `zend_class_entry`. */
    for (k = 0; k < n_pool; k++) {
        pool[k].id = ph53_rd64(win, PH53_POOL_OFF + 8 * (size_t)k);
    }

    /* ---- zend_compile.c:3747-3748, `zend_initialize_class_data`'s tail ---- */
    ce->num_interfaces = 0;
    ce->interfaces = NULL;

    /* ---- phase 1: zend_do_implements_interface, :2584-2592, n_decl times --
     * `opline->extended_value = CG(active_class_entry)->num_interfaces++;`
     * ⚠⚠ THE COUNT MOVES AND NO SLOT IS WRITTEN.  That is the defect's first
     * half and it is a whole statement away from the second. */
    for (k = 0; k < n_decl; k++) {
        idx[k] = ce->num_interfaces++;          /* :2591 */
    }

    /* ---- phase 2: zend_do_end_class_declaration, :2569-2572, VERBATIM ----- */
    /* Inherit interfaces */
    if (ce->num_interfaces > 0) {
        ce->interfaces = (ph53_iface **) php_shim_erealloc(ce->interfaces,
                        sizeof(ph53_iface *)*ce->num_interfaces);
    }
    /* ---- end verbatim: the whole of the defect span --------------------- */

    /* ---- phase 3: the op stream.  THE BLOB IS THE OPCODE STREAM. --------- */
    for (o = 0; o < n_ops; o++) {
        size_t p = PH53_OPS_OFF + (size_t)PH53_OP_BYTES * o;
        unsigned op = (unsigned)win[p] % 3u;
        uint32_t a = ph53_rd32(win, p + 1);
        uint32_t b = ph53_rd32(win, p + 5);

        if (op == PH53_OP_FILL) {
            /* ZEND_ADD_INTERFACE's runtime half: the slot the compile-time
             * index named finally gets its pointer.  `d` is folded whether or
             * not there is a slot to write, so the u64 has the same shape on
             * both arms of `:2570`. */
            unsigned d = (n_decl > 0u) ? (unsigned)(a % (uint32_t)n_decl) : 0u;
            unsigned pi = (unsigned)(b % (uint32_t)n_pool);
            if (n_decl > 0u) {
                ce->interfaces[idx[d]] = &pool[pi];
            }
            acc = acc * 31u + (uint64_t)d;
        } else if (op == PH53_OP_QUERY_DEREF) {
            unsigned t = (unsigned)(a % (uint32_t)n_pool);
            unsigned examined = 0;
            uint64_t matched = 0;
            int r = ph53_instanceof_ex(ce, &pool[t], &examined, &matched);
            acc = acc * 31u + (uint64_t)r;
            acc = acc * 31u + matched;
            acc = acc * 31u + (uint64_t)examined;
        } else {
            unsigned t = (unsigned)(a % (uint32_t)n_pool);
            unsigned i = ph53_inherit_scan(ce, &pool[t]);
            acc = acc * 31u + (uint64_t)(i != ce->num_interfaces);
            acc = acc * 31u + (uint64_t)i;
        }
    }

    /* ---- teardown: zend_opcode.c:161-162, `destroy_zend_class` ----------- */
    if (ce->num_interfaces > 0 && ce->interfaces) {
        php_shim_efree(ce->interfaces);
    }

    /* PROTOCOL_PHP.md B1.2 -- the allocator's own behaviour lands in the u64
     * and not only in a sanitizer.  ⭐ On this row it also makes BOTH ARMS OF
     * `:2570` visible: n_decl == 0 allocates nothing and the tally is 0. */
    acc ^= php_shim_tally();
    return acc;
}
