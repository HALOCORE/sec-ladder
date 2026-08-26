#!/bin/sh
# p23 controls. Rebuilds every artefact; binaries are not committed.
#
#   patterns/p23-partition/controls/run.sh        -> controls.log beside this file
#
# ⚠ `env -u LD_PRELOAD` on every sanitiser run, and the log is `grep`ed, never
# `head`ed. The POSITIVE CONTROL is `bug` on the all-below record: it MUST fire
# under ASan and UBSan, in this same binary and on this same command line. If it
# does not, nothing else in this file means anything.
set -u
cd "$(dirname "$0")"
LOG=controls.log
: > "$LOG"

CC=${CC:-gcc}
echo "--- build ($CC) ---" >> "$LOG"
$CC -O2 -g -fno-omit-frame-pointer -o gv_plain guard_variants.c 2>>"$LOG" || exit 1
$CC -O2 -g -fsanitize=address -fno-omit-frame-pointer -o gv_asan guard_variants.c 2>>"$LOG" || exit 1
$CC -O2 -g -fsanitize=undefined -fno-sanitize-recover=all -o gv_ubsan guard_variants.c 2>>"$LOG" || exit 1

run() {  # run <binary> <cell> <nelem> <pv> <nlow> <neq> <mode>
  echo "=== $* ===" >> "$LOG"
  env -u LD_PRELOAD timeout 60 ./"$@" >> "$LOG" 2>&1
  echo "exit=$?" >> "$LOG"
}

echo "--- A: which guard? three spellings, one benign record ---" >> "$LOG"
for cell in ij mz bug; do
  run gv_plain "$cell" 32 128 12 3 0        # benign: 12 below, 3 equal, 17 above
done

echo "--- A: the same three on an ALL-BELOW record (pv=255) ---" >> "$LOG"
for cell in ij mz bug; do
  run gv_plain "$cell" 32 255 32 0 0
  run gv_asan  "$cell" 32 255 32 0 0
  run gv_ubsan "$cell" 32 255 32 0 0
done

echo "--- A: the same three on an ALL-ABOVE record (pv=0) ---" >> "$LOG"
for cell in ij mz bug; do
  run gv_plain "$cell" 32 0 0 0 0
  run gv_asan  "$cell" 32 0 0 0 0
  run gv_ubsan "$cell" 32 0 0 0 0
done

echo "--- B: the TEXTBOOK pivot on an ALL-EQUAL record (mode=1) ---" >> "$LOG"
run gv_plain selfpivot 32 128 0 0 1
run gv_asan  selfpivot 32 128 0 0 1
run gv_ubsan selfpivot 32 128 0 0 1
echo "--- B control: the same kernel on a MIXED record (mode=0) must be clean ---" >> "$LOG"
run gv_plain selfpivot 32 128 12 3 0
run gv_asan  selfpivot 32 128 12 3 0
run gv_ubsan selfpivot 32 128 12 3 0

echo "--- static size of each cell, linked binary, padding stripped ---" >> "$LOG"
nm --print-size --radix=d gv_plain \
  | grep -E ' [tT] k_(ij|mz|bug|selfpivot)' \
  | awk '{printf "%-24s size=%s\n", $4, $2}' >> "$LOG"
echo "(gcc -O2 may suffix a name with .constprop/.isra; that is the same cell)" >> "$LOG"

rm -f gv_plain gv_asan gv_ubsan
echo "wrote $LOG (binaries deleted; re-run this script to rebuild them)"
