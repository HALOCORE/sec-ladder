/* ph64 control -- the FIDELITY probe's allocator, and it is NOT PHP's.
 *
 * ⚠⚠ NO ROW MAY USE THIS. `PROTOCOL_PHP.md` §B is the allocator rule:
 * a php row links `common-php/emalloc_shim.h` or says in `spec.md` why not, and
 * an earlier effort that dropped plain `malloc` in reported a real defect as
 * unreachable and then invented an explanation for the upstream fix
 * (`PLAN_PHP.md` §4.3). This header exists to MEASURE that hazard on this row
 * rather than quote it.
 *
 * It defines `PHP_EMALLOC_SHIM_H` -- the real shim's include guard -- so that
 * `-include controls/plain_alloc.h` makes `c/kernel.c`'s
 * `#include "emalloc_shim.h"` a no-op and the four entry points resolve here.
 * The size-class cache is GONE, so a freed element really does reach `free()`
 * and ASan's quarantine really does hold it.
 *
 * ⭐ THE QUESTION IT ANSWERS. `index.csv` records `heap-use-after-free` for
 * CRASH-086. On the pristine 5.0.0 allocator that string is NOT REPRODUCIBLE
 * and cannot be -- `REAL_SIZE(39) >> 3 = 5 < MAX_CACHED_MEMORY`, so the block is
 * handed straight back out and never reaches `free()`. This build is what says
 * the recorded category is real rather than a mis-label: same kernel, same
 * chain, one allocator swapped.
 *
 * built only by `controls/asan_fidelity.sh`; it is on no build path.
 */
#ifndef PHP_EMALLOC_SHIM_H
#define PHP_EMALLOC_SHIM_H

#include <stdlib.h>
#include <stdint.h>

static inline void php_shim_reset(void) { }
static inline void *php_shim_emalloc(size_t size) { return malloc(size); }
static inline void php_shim_efree(void *ptr) { free(ptr); }
static inline uint64_t php_shim_tally(void) { return 0; }

#endif /* PHP_EMALLOC_SHIM_H */
