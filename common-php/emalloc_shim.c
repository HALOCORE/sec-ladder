/* emalloc_shim.c -- the state-defining translation unit for
 * `emalloc_shim.h`, FOR STANDALONE CONSUMERS ONLY.
 *
 * ⚠⚠ THIS FILE IS NOT ON THE PATTERN BUILD PATH AND CANNOT BE.
 * `harness/build.py:163-165` compiles exactly three translation units --
 * `common/driver.c`, `<row>/c/<kernel>.c`, `<row>/c/main.c` -- and adding a
 * fourth means editing `build.py`, which stales all 33 PAT measurement
 * records (`PLAN_PHP.md` §2.1). Measured and stated rather than assumed:
 * `.tasks-php/TASK_PHP_002_REPORT.md` §4, claim 3.
 *
 * A ROW therefore does this in `c/kernel.c` and nowhere else:
 *
 *     #define PHP_SHIM_IMPL
 *     #include "emalloc_shim.h"
 *
 * and `c/main.c` includes the header without the define. This file exists so
 * that a standalone probe or a future non-ladder consumer can link the state
 * without repeating the incantation -- `emalloc_probe.c` uses it.
 */

#define PHP_SHIM_IMPL
#include "emalloc_shim.h"
