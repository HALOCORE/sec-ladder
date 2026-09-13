#!/bin/sh
# ph52 control: THE 16-CELL TRANSLATION-UNIT-BOUNDARY TABLE.
#
#     sh patterns-php/ph52-concat-copy-uninit/controls/tu_boundary.sh [--selftest]
#
# ⚠⚠ WHY THIS FILE EXISTS AND IS FOUR LINES LONG, STATED RATHER THAN LOOKING LIKE
# PADDING.  `c/kernel.c` and `c/kernel_hardened.c` both carry the comment
#
#     "../NOTES.md §4 and `controls/tu_boundary.sh` have the 16-cell table"
#
# and `c/*` IS IN THE MEASUREMENT DIGEST -- `.memory-php/04-process.md` law 14: a
# comment inside a C kernel cannot be corrected at re-gate price, only at a 32-cell
# re-measure.  The 16-cell table is implemented in `controls/d0_stack.py`, which is
# the file that has the build matrix, the selftest and the negatives.
#
# ▶ So the CHEAP and HONEST repair for a pointer that named a file which did not
# exist is to write the named file as the documented entry point: `controls/*` is
# gate-only, so this costs ONE re-gate where editing the kernel comment would cost a
# 32-cell re-measure.  `TASK_PHP_045_REPORT.md` §17 records it with the other three.
#
# ⚠ It is NOT a second implementation and it must never become one: two copies of a
# measurement is how they disagree (`harness/asm.py`'s own docstring is that lesson).
exec python3 "$(dirname "$0")/d0_stack.py" "$@"
