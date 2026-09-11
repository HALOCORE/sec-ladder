#ifndef PH64_KERNEL_H
#define PH64_KERNEL_H

#include <stddef.h>
#include <stdint.h>

#include "driver.h" /* SLB_NOINLINE */

/* ph64: dispatch one round of PHP tick functions over `zend_llist_apply`, with
 * one of them calling `unregister_tick_function()` from inside its own
 * callback, and fold what the walk saw into a u64.
 *
 *   window = [u32 nent][u32 trig][u32 mode][u32 post][ NMAX x 8 name bytes ]
 *   NMAX   = (len - 16) / 8          N = 1 + nent % NMAX
 *   register_tick_function(i) for i = 1..N              <- basic_functions.c:2799-2835
 *   zend_llist_apply(&list, user_tick_function_call)    <- zend_llist.c:186-193
 *   unregister_tick_function(post) at top level         <- basic_functions.c:2840-2862
 *   fold (the names visited, l->count, dtors, visits, refusals), xor the
 *   allocator tally, destroy the list.
 *
 * Contract in ../spec.md. Two C rungs share this declaration:
 *
 *   c/kernel.c            R1  -- PHP 5.0.0, narrowed. THE BUG (CRASH-086).
 *   c/kernel_hardened.c   R1h -- the same file plus `562f886ecb14`'s ONE hunk,
 *                                in `user_tick_function_compare`:
 *                                `if (ret && tick_fe1->calling) return 0;`
 *                                (Antony Dovgal, 2007-04-10, "MFH: fix #41037
 *                                (unregister_tick_function() inside the tick
 *                                function crash PHP)"). First shipped in
 *                                php-5.2.2; still in master, strengthened to
 *                                `zend_throw_error`.
 *
 * ⚠⚠ R1h IS IN A THIRD FUNCTION. It patches neither the loop that faults
 * (`zend_llist_apply`, `Zend/zend_llist.c:186-193`, the row's primary span) nor
 * the statement the corpus cites (`basic_functions.c:2135`). It patches the
 * COMPARATOR, so that the free never happens; the two dereferences are left
 * exactly as they were and are made unreachable instead. `zend_llist_apply`'s
 * body is byte-identical from php-5.0.0 to master, 21 years, with only
 * `TSRMLS_DC` removed -- so a row built at the loop alone would have NO R1h at
 * all. ../spec.md `provenance.fix_commit_note`; NOTES.md §4.
 *
 * ⚠⚠ THE THREE DANGLING REFERENCES, AND THE CITED LINE IS THE FIRST FAULT.
 * `zend_llist_del_element` expands `DEL_LLIST_ELEMENT`, whose last two
 * statements are `l->dtor(current->data)` -- which `efree`s the entry's
 * `arguments` block -- and `pefree(current)`. So one self-unregistration
 * produces:
 *
 *   1. `tick_fe`             (= element->data)  -- SITE C writes `calling = 0`
 *                                                  into it at :2135. FIRST fault
 *                                                  (ASan: `WRITE of size 4`).
 *   2. `element`             -- SITE L reads `element->next` at :190 and then
 *                              FOLLOWS it. `next` is at OFFSET 0 of the freed
 *                              block, so this is the freed block's first word.
 *   3. `tick_fe->arguments`  -- the comparator reads it on any later walk.
 *
 * ⚠⚠ AND ON THE PRISTINE 5.0.0 ALLOCATOR NONE OF THEM FAULTS BY ITSELF.
 * `sizeof(zend_llist_element) + sizeof(user_tick_function_entry) - 1` is 39,
 * `REAL_SIZE(39)` is 40 and `40 >> 3 = 5 < MAX_CACHED_MEMORY`, so the freed
 * element goes into `AG(cache)[5]` and is NOT returned to `malloc`: its payload
 * is untouched, `element->next` still reads the true successor, and the walk
 * completes normally. That is what the corpus's `crashes_pristine_5_0_0 = False`
 * is, and it is `PROTOCOL_PHP.md` §B1 rule 1 firing on this row. The defect
 * becomes observable in two ways and this row ships both:
 *
 *   * ALWAYS, in the allocator tally and `l->count` -- R1 really did free an
 *     element R1h refuses to free, so `n_free`, `n_cache_hit`,
 *     `bytes_mallocked`, `l->count` and the dtor count all move. That is the
 *     oracle in the measured u64 (§B1 rule 2);
 *   * ON REUSE, as a fault -- one same-size-class `emalloc` inside the same
 *     callback LIFO-pops the just-freed element back out, and whatever the tick
 *     function writes into it becomes `element->next`. `inputs/adversarial-*`
 *     carry that case and R1 SIGSEGVs on all four `DEL_LLIST_ELEMENT` arms.
 *
 * The kernel does NOT take `buf_len`: PHP's `zend_llist_apply(zend_llist *l,
 * llist_apply_func_t func)` carries its bound inside the list, and the defect
 * is that the loop's `element = element->next` is evaluated after `func` has
 * been allowed to free `element`. Handing the walk a separate length would be
 * modelling a different bug.
 *
 * The caller must guarantee `off + len <= buf_len` and `len >= 24`; that is the
 * structural precondition every rung shares and no rung checks (R5 proves it at
 * the call site instead). `nent`, `trig`, `mode`, `post` and every name byte are
 * attacker data and are the kernel's problem. */
SLB_NOINLINE uint64_t kernel(const uint8_t *buf, size_t off, size_t len);

#endif /* PH64_KERNEL_H */
