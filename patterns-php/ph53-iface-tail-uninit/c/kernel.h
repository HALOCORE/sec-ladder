#ifndef PH53_KERNEL_H
#define PH53_KERNEL_H

#include <stddef.h>
#include <stdint.h>

#include "driver.h" /* SLB_NOINLINE */

/* ph53: PHP 5.0.0's class-declaration interface array -- storage grown to the
 * COUNT, with the tail never written -- driven over a window of opcode-stream
 * bytes, folded into a u64.
 *
 *   window = [u32 n_decl_w][u32 n_pool_w][u32 n_ops_w]
 *            [ MAXP x u64 pool id ]
 *            [ n_ops x { u8 op; u32 a; u32 b } ]
 *
 *   n_decl = n_decl_w % (MAXD + 1)          0 .. 16   `implements` clauses
 *   n_pool = 1 + n_pool_w % MAXP            1 .. 8    interfaces in scope
 *   n_ops  = n_ops_w % (cap + 1),  cap = (len - PH53_OPS_OFF) / 9
 *
 *   phase 1  zend_do_implements_interface  :2584-2592, n_decl times
 *   phase 2  zend_do_end_class_declaration :2569-2572  <- THE DEFECT
 *   phase 3  the op stream: FILL writes one slot, QUERY reads them all
 *   teardown destroy_zend_class            zend_opcode.c:161-162
 *
 * Contract in ../spec.md.  Two C rungs share this declaration:
 *
 *   c/kernel.c            R1  -- PHP 5.0.0, narrowed.  THE BUG (CRASH-158).
 *   c/kernel_hardened.c   R1h -- the same file plus `d09cdd9f71f3` WHOLE:
 *                                `erealloc` -> `emalloc` + `memset(.., 0, ..)`
 *                                (Dmitry Stogov, 2005-06-08, "Fixed valgrind
 *                                errors").  First shipped in php-5.0.5.
 *
 * ============================================================================
 * ⚠⚠⚠ THE READ IS IN BOUNDS.  CWE-824, NOT CWE-125.
 * ============================================================================
 * `Zend/zend_compile.c:2569-2572`:
 *
 *     if (ce->num_interfaces > 0) {                                    :2570
 *         ce->interfaces = (zend_class_entry **) erealloc(ce->interfaces,
 *                          sizeof(zend_class_entry *)*ce->num_interfaces);
 *     }                                                                :2571
 *
 * `ce->num_interfaces` was advanced once per `implements` clause at COMPILE
 * time -- `zend_compile.c:2591`,
 * `opline->extended_value = CG(active_class_entry)->num_interfaces++;` -- and
 * NO slot was written by that advance.  `ce->interfaces` is NULL and
 * `ce->num_interfaces` is 0 at `:3747-3748`, so the `erealloc` is a plain
 * `malloc` and EVERY slot of the new array is indeterminate.  The slot the
 * consumer reads is INSIDE the block and nothing has been freed: this is an
 * uninitialised read of an in-bounds slot, not an over-read past the end.
 * ⚠ `ph32` is the cross-reference and NOT the duplicate -- same C shape, sized
 * to the LITERAL instead of the count, so its excess is PAST the end (CWE-125).
 *
 * ============================================================================
 * ⚠⚠ AND THE 2005 FIX DOES NOT REMOVE THE FAULT -- IT MAKES IT DETERMINISTIC
 * ============================================================================
 * The consumers are UNCHANGED at php-5.0.5, so with the array zeroed:
 *
 *   QUERY_DEREF  zend_operators.c:1534-1535  `interfaces[i]->id`  NULL -> SEGV
 *   QUERY_CMP    zend_compile.c:1951         `interfaces[i]==e`   NULL -> correct
 *
 * ⭐ ONE HUNK, TWO SEVERITIES, and that is why this kernel ships BOTH
 * consumers.  `../NOTES.md` §5 has the measurement.
 *
 * The kernel does NOT take `buf_len`.  The caller guarantees
 * `off + len <= buf_len` and `PH53_OPS_OFF <= len`; that is the structural
 * precondition every rung shares and no rung checks (R5 proves it at the call
 * site instead).  Every byte of the window is attacker data. */
SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t off, size_t len);

/* ---- the window's shape.  Identical in all six rungs and in model.py. ---- */

/* Maximum `implements` clauses per declaration, i.e. the largest
 * `ce->num_interfaces` this row admits.  ⚠ It bounds the fixed-size `idx[]`
 * that stands in for `opline->extended_value` and, in the Rust rungs, the
 * `wrote[]` witness -- so it is a shared constant and not a C detail. */
#define PH53_MAXD 16

/* Interfaces in scope, i.e. the pool of `zend_class_entry *` a declaration can
 * name.  The pool is NOT allocated: upstream's interfaces already exist. */
#define PH53_MAXP 8

#define PH53_HDR_BYTES  12                         /* three u32 head words */
#define PH53_POOL_OFF   PH53_HDR_BYTES
#define PH53_POOL_BYTES (8 * PH53_MAXP)
#define PH53_OPS_OFF    (PH53_POOL_OFF + PH53_POOL_BYTES)   /* 76 */
#define PH53_OP_BYTES   9                          /* u8 op, u32 a, u32 b */

#define PH53_OP_FILL        0
#define PH53_OP_QUERY_DEREF 1
#define PH53_OP_QUERY_CMP   2

/* `zend_class_entry`'s two interface members, and nothing else -- `zend.h:334`
 * and `:335`, in upstream's order and with upstream's types
 * (`zend_uint` is `unsigned int`, `zend_types.h:39`). */
typedef struct ph53_iface {
    uint64_t id;              /* stands for the interface's own identity */
} ph53_iface;

typedef struct ph53_ce {
    ph53_iface  **interfaces;      /* zend.h:334 */
    unsigned int  num_interfaces;  /* zend.h:335 */
} ph53_ce;

#endif /* PH53_KERNEL_H */
