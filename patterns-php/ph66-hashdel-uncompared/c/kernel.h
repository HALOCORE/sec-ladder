#ifndef PH66_KERNEL_H
#define PH66_KERNEL_H

#include <stddef.h>
#include <stdint.h>

#include "driver.h" /* SLB_NOINLINE */

/* ph66: run PHP 5.0.0's `Zend/zend_hash.c` container over an insert/delete key
 * stream and fold THE SURVIVING KEYS.
 *
 *   window = [4-byte record][4-byte record]...
 *
 *   the blob              IS the key stream -- an op, a key KIND, a key
 *                         selector and a payload, each from its own bit or byte
 *   the container         _zend_hash_init / _zend_hash_add_or_update /
 *                         _zend_hash_index_update_or_next_insert /
 *                         zend_hash_del_key_or_index / zend_hash_destroy
 *   the u64               fold of every SURVIVING bucket's (nKeyLength, h,
 *                         arKey bytes, payload), plus nNumOfElements, the
 *                         destructor count and fold, the delete outcomes, and
 *                         php_shim_tally()
 *
 * Contract in ../spec.md. Two C rungs share this declaration:
 *
 *   c/kernel.c            R1  -- PHP 5.0.0 verbatim. THE BUG (LOGIC-001).
 *   c/kernel_hardened.c   R1h -- the same file with b73349dbe4e9 (Zeev
 *                                Suraski, 2006-02-01, "Fix possibility of a
 *                                wrong element being deleted by
 *                                zend_hash_del()") applied VERBATIM, -p1, one
 *                                file, six lines, no backport.
 *
 * ============================================================================
 * THE DEFECT, IN TWO LINES, AND THEY ARE THE PRIMARY SPAN
 * ============================================================================
 *   Zend/zend_hash.c:464-465, inside `zend_hash_del_key_or_index`'s chain walk
 *
 *     if ((p->h == h) && ((p->nKeyLength == 0) ||
 *         ((p->nKeyLength == nKeyLength) && (!memcmp(p->arKey, arKey, n)))))
 *
 * A NUMERIC bucket is marked by `nKeyLength == 0` -- upstream says so itself at
 * `:387`, quoted in `_zend_hash_index_update_or_next_insert` below -- so for a
 * numeric bucket the LEFT DISJUNCT FIRES AND THE KEY IS NEVER COMPARED AT ALL.
 * Hash equality alone is treated as key identity.
 *
 * ============================================================================
 * THE TRIGGER NEEDS NO PREIMAGE, AND THAT IS WHY THIS ROW IS CHEAP
 * ============================================================================
 * `_zend_hash_index_update_or_next_insert` stores `p->h = h` with `h` the RAW
 * user-chosen index. So the collision is built by running the hash FORWARDS:
 * `zend_inline_hash_func("abc", 4) == 6385036779`, and inserting THAT as an
 * integer index gives a numeric bucket that `unset($a["abc"])` destroys.
 * `.tasks-php/probes/ph66_djbx33a_collide.py` is the generator; the record
 * decode below does the same thing per record, with `coll` as the switch.
 *
 * ⚠ `nKeyLength` INCLUDES THE NUL -- `Zend/zend_execute.c:3612` passes
 * `varname->value.str.len + 1` -- so the kernel hashes `kl + 1` bytes.
 *
 * ============================================================================
 * ⛔⛔ EVERY FREE IN THIS KERNEL IS A CORRECT FREE
 * ============================================================================
 * This row's target error is a WRONG ANSWER, not a signal. There is no
 * use-after-free here and there must not be one: a bucket is unlinked from the
 * bucket chain, from the global list AND from `ht->pInternalPointer` before
 * `pefree(p)`, exactly as `:466-489` does it, and nothing reads it afterwards.
 * ../NOTES.md section 3 states how that is checked. A kernel that freed the
 * bucket and then read it would have built a DIFFERENT ROW.
 *
 * ../NOTES.md carries the measurements; this comment POINTS at them and states
 * no verdict of theirs (PROTOCOL_PHP.md section F6a). */

/* ---- the record layout, identical in every rung and re-derived in model.py --
 *
 *   b[0]  ctl   -> op   = b[0] & 1          0 INSERT, 1 DELETE
 *                  kind = (b[0] >> 1) & 1   0 STRING KEY, 1 NUMERIC INDEX
 *                  coll = (b[0] >> 2) & 1   INDEX only: 1 -> the index IS
 *                                           hash(key(sel)), i.e. the collision
 *   b[1]  sel   -> sel  = b[1] & 63         which of the 64 string keys;
 *                  for a NON-colliding index record the index is b[1] itself
 *   b[2]  lo    -> payload low byte
 *   b[3]  hi    -> payload high byte
 *
 * key(sel): kl = 1 + (sel % 7) characters, key[i] = 'a' + ((sel/7)*5 + i*7)%26,
 * then a NUL, so nKeyLength = kl + 1 in 2..8. The 64 keys are pairwise
 * distinct and their 64 hashes are pairwise distinct and all far above 255 --
 * `inputs/gen.py::_check_keys` asserts all three rather than assuming them, so
 * the ONLY collision in this kernel's domain is the one `coll` builds.
 *
 * ⭐ `nKeyLength` spans 2..8, so `zend_inline_hash_func`'s `nKeyLength >= 8`
 * UNROLLED arm runs on the longest key and its `switch` tail runs on every
 * other: both are REACHED (PROTOCOL_PHP.md A2a rule 1, asserted in
 * inputs/gen.py). ⚠ And the whole key fits in EIGHT bytes, which is what lets
 * the four Rust rungs carry it as one `u64` -- ../spec.md's divergence ledger
 * states the equivalence and controls/differential.py measures it. */
#define PH66_REC 4
#define PH66_KMAX 7  /* max key CHARACTERS; nKeyLength = kl + 1 <= 8 */
#define PH66_NKEY 64 /* sel = b[1] & 63 */

/* Zend/zend_hash.h:32-37 -- the flag words, upstream's own spelling. */
#define HASH_UPDATE (1 << 0)
#define HASH_ADD (1 << 1)
#define HASH_DEL_KEY 0
#define HASH_DEL_INDEX 1

/* Zend/zend.h:240-241. */
#define SUCCESS 0
#define FAILURE -1

SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t off, size_t len);

#endif /* PH66_KERNEL_H */
