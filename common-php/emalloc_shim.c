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
 * hole.
 *
 * ⚠⚠ AND THE SENTENCE THAT REPLACED IT WAS WRONG WITHIN ONE TASK, WHICH IS THE
 * SAME DEFECT AGAIN AND IS WORTH LEAVING ON THE RECORD. It read: *"Closed at
 * TASK_PHP_006: `harness-php/gate.py::_tu_closure` asks `gcc -MM` for the real
 * translation-unit closure instead of grepping for a name, SO BOTH SPELLINGS
 * AND ANY FUTURE ONE ARE SEEN."*  `TASK_PHP_007` B1/B2 bypassed `_tu_closure`
 * twice: it simulated 2 of the 8 preprocessor states `build.py` compiles in
 * (no `-O`, `gcc` hard-coded), so `__OPTIMIZE__`, `__clang__` and
 * `__has_include` were each invisible, and its text fallback failed OPEN.
 * "ANY FUTURE ONE" was a prediction about an unbounded space, made by a guard
 * that had enumerated two points of it.
 *
 * ✅ CLOSED AT `TASK_PHP_008` §0 BY DELETING THE QUESTION. `_tu_closure` is
 * gone. Every `patterns-php/` row carries `c/emalloc_shim.h` as a symlink
 * UNCONDITIONALLY, allocating or not, so no spelling of `#include` -- of this
 * file or of the header -- can put the allocator outside the digests. There is
 * nothing left for a comment in this file to mislead.
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
