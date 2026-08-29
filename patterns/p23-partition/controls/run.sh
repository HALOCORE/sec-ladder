#!/bin/sh
# p23 controls. Rebuilds every artefact; binaries are not committed.
#
#   patterns/p23-partition/controls/run.sh   -> controls.log        beside this file
#                                            -> controls_pin.json   its staleness pin
#
# ⚠ `env -u LD_PRELOAD` on every sanitiser run, and the log is `grep`ed, never
# `head`ed. The POSITIVE CONTROL is `bug` on the all-below record: it MUST fire
# under ASan and UBSan, in this same binary and on this same command line. If it
# does not, nothing else in this file means anything.
#
# ⚠⚠ THE PIN, TASK_127, and read what it does NOT claim. `controls.log` is NOT
# byte-reproducible and MUST NOT be self-hashed: it embeds ASLR addresses, PIDs,
# BuildIds and absolute repo paths, AND -- the reason the task file did not
# know -- ONE OF ITS DATA LINES IS A DRAW. `selfpivot` on the ALL-EQUAL record
# reads uninitialised stack by construction, and five runs of one binary in one
# directory printed 3910418957284214783 / ...752 / ...783 / ...783 / ...752,
# while the committed log carries a sixth value, ...814. So the pin is over the
# SOURCES the log derives from, and `pin.not_covered` says what a green pin
# still does not buy. `check.py::check_control_json_pins` (stage 9b) reads it
# with zero new gate code: it globs `patterns/*/controls/*.json`.
#
# The pin is emitted BY THIS SCRIPT, at the end of a run that has just rewritten
# the log. That is deliberate and it is TASK_121's `rebuild_cells` lesson: a pin
# that can be stamped without regenerating the artefact is a green pin over a
# stale number, which is the defect the pin exists to catch.
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

# --- the staleness pin -------------------------------------------------------
# No timestamp and no host field on purpose: re-running this script on an
# unchanged tree must produce a BYTE-IDENTICAL controls_pin.json, so that a
# regeneration shows up in `git status` only when something it pins moved.
PIN=controls_pin.json
h() { sha256sum "$1" | cut -d' ' -f1; }
cat > "$PIN" <<PINEOF
{
  "note": "Staleness pin for controls.log, which cannot pin itself. TASK_127.",
  "pins": "patterns/p23-partition/controls/controls.log",
  "derived_from_sha256": {
    "patterns/p23-partition/controls/guard_variants.c": "$(h guard_variants.c)",
    "patterns/p23-partition/controls/run.sh": "$(h run.sh)"
  },
  "pin": {
    "regenerate": "sh patterns/p23-partition/controls/run.sh",
    "read_by": "harness/check.py::check_control_json_pins (gate stage 9b)",
    "not_covered": [
      "the C toolchain: \$CC defaults to gcc and is not pinned, so a compiler bump moves the four static sizes and nothing here fires",
      "the log itself: it embeds ASLR addresses, PIDs, BuildIds and absolute repo paths, so it is not byte-reproducible and is deliberately NOT hashed",
      "ONE DATA LINE IS A DRAW, not just cosmetics: 'selfpivot ... mode=1' reads uninitialised stack by construction and printed ...783/...752/...783/...783/...752 over five runs of one binary (TASK_127). A green pin does NOT make that number reproducible, and NOTES.md must not quote it as a figure."
    ]
  }
}
PINEOF
echo "wrote $LOG and $PIN (binaries deleted; re-run this script to rebuild them)"
