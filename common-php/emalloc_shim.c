/* emalloc_shim.c -- the state-defining translation unit for
 * `emalloc_shim.h`, FOR STANDALONE CONSUMERS ONLY.
 *
 * ⚠⚠ THIS FILE IS NOT A TRANSLATION UNIT `harness/build.py` COMPILES.
 * `harness/build.py:162-164` compiles exactly three -- `common/driver.c`,
 * `<row>/c/<kernel>.c`, `<row>/c/main.c` -- and adding a fourth means editing
 * `build.py`, which stales all 33 PAT measurement records (`PLAN_PHP.md` §2.1).
 * Measured and stated rather than assumed:
 * `.tasks-php/TASK_PHP_002_REPORT.md` §4, claim 3.
 *
 * ⚠⚠⚠ THIS SENTENCE USED TO READ *"IS NOT ON THE PATTERN BUILD PATH AND CANNOT
 * BE"*, AND THE SECOND HALF WAS FALSE AND EXPENSIVE. It is true of `build.py`'s
 * TU LIST and false of the PREPROCESSOR: this file sits on `-I common-php`, so
 * `#include "emalloc_shim.c"` from `c/kernel.c` pulls the whole allocator into
 * a row's real build. `TASK_PHP_005` F-1 constructed that row -- it compiles,
 * links and allocates (`alloc tally = 7688571`) -- and because the preflight's
 * allocator audit searched only for the string `emalloc_shim.h`, the allocator
 * landed in NEITHER the gate digest nor the measurement digest with the
 * preflight green. ⚠ **The audit did not cover this spelling BECAUSE OF THIS
 * COMMENT.** A "cannot" that is only a "does not" is how a guard acquires a
 * hole. Closed at `TASK_PHP_006`: `harness-php/gate.py::_tu_closure` asks
 * `gcc -MM` for the real translation-unit closure instead of grepping for a
 * name, so both spellings and any future one are seen.
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
