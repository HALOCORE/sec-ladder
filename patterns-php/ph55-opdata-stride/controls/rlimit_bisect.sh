#!/bin/sh
# ph55 control -- WHAT PROOF BUDGET THIS ROW ACTUALLY NEEDS.
#
#     sh patterns-php/ph55-opdata-stride/controls/rlimit_bisect.sh
#
# Regenerates the table quoted in ../NOTES.md §10 and in ../spec.md's
# `verus.twin_obligations_note`. READ-ONLY on the row: it writes one scratch
# copy under `.temp/php55rl/` and never touches `verus.rs`.
#
# ⚠ THE SCRATCH DIRECTORY IS TWO LEVELS BELOW THE REPO ROOT ON PURPOSE.
# `verus.rs` reaches the shared driver with `#[path = "../../common/driver.rs"]`,
# which resolves relative to the SOURCE FILE, so a copy at any other depth does
# not compile and the bisect would report a failure that is the script's.
#
# ⭐ WHAT IT FOUND, AND IT IS THIS ROW'S VERUS RESULT: `verus.rs` ships with NO
# `#[verifier::rlimit]` at all, because the whole proof -- an interpreter, ten
# handlers, a value postcondition over the entire machine state, and eight
# verified twins -- needs **2** against Verus's default of 10. ph16's obligation
# is a single index bound with no loop in it and it had to ship
# `#[verifier::rlimit(30)]` because its twin build FAILED at 8.
set -e
cd "$(dirname "$0")/../../.."
SRC=patterns-php/ph55-opdata-stride/verus.rs
TMP=.temp/php55rl
mkdir -p "$TMP"

for r in 1 2 3 4 5 10 30; do
  # The shipped file has no rlimit attribute, so INSERT one; a `sed` that only
  # substituted would silently measure the default seven times.
  awk -v r="$r" '/^#\[cfg_attr\(slb_isolated, inline\(never\)\)\]$/ && !done \
                 { print "#[verifier::rlimit(" r ")]"; done = 1 } { print }' \
      "$SRC" > "$TMP/v.rs"
  grep -q "verifier::rlimit($r)" "$TMP/v.rs" || {
      echo "FATAL: the attribute was not inserted -- the anchor line moved"; exit 2; }
  for cfg in "" "--cfg slb_twin"; do
    out=$(timeout 900 ./verus_run.py "$TMP/v.rs" $cfg 2>&1 \
          | grep -E 'verification results' || echo "FAILED/timeout")
    echo "rlimit=$r cfg='${cfg:-plain}' -> $out"
  done
done
