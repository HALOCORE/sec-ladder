#!/bin/sh
# ph64 control -- §A4 FIDELITY, and the answer is a FINDING rather than a match.
#
#     sh patterns-php/ph64-callback-frees-cursor/controls/asan_fidelity.sh
#
# ⚠⚠ `harness-php/gate.py` HASHES THIS FILE AND NEVER RUNS IT.
#
# It builds `controls/dump.c` against the row's own `c/kernel.c` FOUR ways --
# {faithful shim, plain malloc} x {no sanitizer, ASan+UBSan} -- and drives each
# with two windows: the corpus's own trigger (self-unregistration, NO reuse) and
# the same trigger with the callback's one same-size-class allocation.
#
# THE EXPECTATIONS, DECLARED BEFORE THE RUN (PROTOCOL_PHP.md §H):
#
#   E1 must-NOT-fire  faithful shim, no reuse: SILENT under ASan, and the u64 is
#                     returned. The 40-byte block goes into AG(cache)[5], never
#                     reaches free(), and nothing scribbles the payload. THIS IS
#                     THE CORPUS'S OWN TRIGGER and it is why
#                     `crashes_pristine_5_0_0` is False.
#   E2 must-fire      faithful shim, WITH reuse: the sanitizers report. ⚠
#                     WHAT THEY REPORT IS NOT `heap-use-after-free`, and my
#                     declared guess at the exact string was WRONG: I predicted
#                     `SEGV on unknown address` and the measurement gives UBSan's
#                     `member access within misaligned address 0x1000000000004
#                     for type 'struct zend_llist_element'` and then
#                     `UndefinedBehaviorSanitizer: DEADLYSIGNAL`. The miss is
#                     recorded rather than rewritten. The CATEGORY claim -- not
#                     `heap-use-after-free`, because the block never reached
#                     free() -- is what E2 was for and it holds.
#                     `0x1000000000004` is inputs/gen.py's WILD_SLOT read back
#                     out of the recycled block.
#   E3 must-fire      PLAIN MALLOC, no reuse: ASan reports
#                     `heap-use-after-free`, and frame #0 is SITE C -- the
#                     `WRITE of size 4` at basic_functions.c:2135, which is the
#                     line index.csv cites. ⭐ THIS is the artefact that the
#                     recorded category is real.
#   E4 must-NOT-fire  either allocator, a window where nothing is freed under the
#                     cursor: silent, both builds. Without it E1-E3 could be
#                     about the harness rather than about the free.
#
# ⚠ E1 vs E3 is the row's §A4 statement in two lines: A C KERNEL ON PLAIN
# malloc/free REPRODUCES MORE OF THIS THAN PRISTINE PHP DOES (PROTOCOL_PHP.md
# §B1 rule 1), and the row measures under the faithful one.
set -e
cd "$(dirname "$0")/../../.."
R=patterns-php/ph64-callback-frees-cursor
O=.temp/php32/asan
mkdir -p "$O"
COMMON="-std=c99 -Wall -Wextra -O1 -g -I common-php -I $R/c"
SAN="-fsanitize=address,undefined -fno-omit-frame-pointer -fstrict-aliasing -static-libasan -static-libubsan"

gcc $COMMON                                   "$R/controls/dump.c" "$R/c/kernel.c" -o "$O/shim_plain.bin"
gcc $COMMON $SAN                              "$R/controls/dump.c" "$R/c/kernel.c" -o "$O/shim_asan.bin"
gcc $COMMON      -include "$R/controls/plain_alloc.h" "$R/controls/dump.c" "$R/c/kernel.c" -o "$O/malloc_plain.bin"
gcc $COMMON $SAN -include "$R/controls/plain_alloc.h" "$R/controls/dump.c" "$R/c/kernel.c" -o "$O/malloc_asan.bin"

# The three windows, built by controls/asan_fidelity.py so the layout is
# derived from ../inputs/gen.py's rules and not retyped here.
python3 "$R/controls/asan_fidelity.py" > "$O/windows.txt"

for b in shim_plain shim_asan malloc_plain malloc_asan; do
  echo "=============================== $b"
  while read -r label line; do
    printf '%-28s ' "$label"
    printf '%s\n' "$line" | "$O/$b.bin" 2>&1 | head -8 | tr '\n' ' '
    echo
  done < "$O/windows.txt"
done
