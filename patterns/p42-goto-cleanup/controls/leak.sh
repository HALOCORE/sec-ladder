#!/bin/sh
# p42 control 1 -- THE LEAK, and the control that must fire.
#
# The gate's stage 7 (`check.py::check_sanitizers`) already requires a
# diagnostic on the three inputs `model.py` computes `sanitizer_expect: "fires"`
# for.  It CANNOT tell WHICH sanitizer fired: its predicate is
#
#     fired = ("runtime error" in se or "AddressSanitizer" in se
#              or "UndefinedBehaviorSanitizer" in se or "ERROR:" in se)
#
# a four-way substring OR, so a heap-buffer-overflow would satisfy p42's
# `"fires"` obligation exactly as a leak does.  This script carries the finer
# check the gate cannot: it greps for `LeakSanitizer` SPECIFICALLY, it asserts
# the leaked byte count against the INVARIANT `n_err * win_len` that `model.py`
# derives from the file alone, and it runs the whole matrix at four optimisation
# levels because `.memory/00-environment.md` records a leak shape that is
# visible at `-O0` and invisible at `-O1`/`-O2`.
#
# THE POSITIVE CONTROL IS `c/kernel_hardened.c`.  One statement differs, it must
# be SILENT on every input at every level, and if it ever reports a leak the
# instrument is measuring something other than the missing `goto`.  Equally, if
# the BUGGY rung is ever silent on an input `model.py` says errors, the detector
# is not running -- and a detector that is not running looks exactly like a
# detector that found nothing (`.memory/00-environment.md`).
#
# The control has 352 points, not one: 2 kernels x 4 levels x 44 inputs.
#
# /!\ CORRECTED AT TASK_110, from TASK_109 C5.  This line used to say `88
#     points ... x 11 inputs` and the success message below used to say `ALL 88
#     POINTS`, and 88 was never right for ANY input set.  The glob below is
#     "$PDIR"/inputs/*.bin, which takes the 32 sweep-w*.bin as well as the 12
#     matrix inputs: 2 x 4 x 44 = 352.  Without the sweeps it would be 96.  The
#     review ran this script byte-identically, counted 352 rows, and watched it
#     print `ALL 88 POINTS`.  The count is now DERIVED from the loop rather than
#     written down, so it cannot go stale again.
#
#   sh patterns/p42-goto-cleanup/controls/leak.sh
#
# Artefacts land in .temp/t104/leakctl/ and are re-derivable from this script.
set -u
REPO=$(cd "$(dirname "$0")/../../.." && pwd)
PDIR="$REPO/patterns/p42-goto-cleanup"
OUT="$REPO/.temp/t104/leakctl"
mkdir -p "$OUT"

# What model.py says each input leaks, from the file alone: `n_err * win_len`.
python3 - "$PDIR" >"$OUT/want.txt" <<'PY'
import glob, importlib.util, os, sys
pdir = sys.argv[1]
spec = importlib.util.spec_from_file_location("m42", os.path.join(pdir, "model.py"))
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
for f in sorted(glob.glob(os.path.join(pdir, "inputs", "*.bin"))):
    print(os.path.basename(f), m.build(f).leak_bytes)
PY

# The gate's own stage-7 flag string, except for -O, which this script sweeps.
FLAGS="-std=c99 -Wall -Wextra -g -fsanitize=address,undefined -fstrict-aliasing
       -static-libasan -static-libubsan -DSLB_ISOLATED"

fail=0
points=0
for O in O0 O1 O2 O3; do
  for K in kernel kernel_hardened; do
    bin="$OUT/$K-$O"
    # shellcheck disable=SC2086
    gcc $FLAGS "-$O" -I "$REPO/common" -I "$PDIR/c" \
        "$REPO/common/driver.c" "$PDIR/c/$K.c" "$PDIR/c/main.c" -o "$bin" \
      || { echo "BUILD FAIL $K $O"; fail=1; continue; }
    for f in "$PDIR"/inputs/*.bin; do
      n=$(basename "$f")
      want=$(awk -v k="$n" '$1==k{print $2}' "$OUT/want.txt")
      [ "$K" = kernel_hardened ] && want=0
      # `env -u LD_PRELOAD`: the container ships one that breaks the sanitizer
      # runtime's init ordering.  `grep`, never `head`: gcc's UBSan report is
      # four lines and ASan's banner is on lines 5-6, which is how TASK_086 hid
      # four rows of a harm table.
      log="$OUT/$K-$O-$n.log"
      env -u LD_PRELOAD "$bin" "$f" >"$log.out" 2>"$log"
      rc=$?
      if grep -q 'LeakSanitizer' "$log"; then lsan=YES; else lsan=no; fi
      if grep -q 'AddressSanitizer: heap\|runtime error' "$log"; then other=YES; else other=no; fi
      bytes=$(grep -o 'SUMMARY: AddressSanitizer: [0-9]* byte' "$log" | grep -o '[0-9]*')
      [ "$want" -gt 0 ] && expect=YES || expect=no
      status=OK
      [ "$lsan" = "$expect" ] || { status="*** WRONG (want $expect) ***"; fail=1; }
      if [ "$lsan" = YES ] && [ "${bytes:-x}" != "$want" ]; then
        status="*** BYTES ${bytes:-none} != model's $want ***"; fail=1
      fi
      [ "$other" = no ] || { status="$status  *** a NON-leak sanitizer fired ***"; fail=1; }
      points=$((points + 1))
      printf '%-16s %-3s %-28s exit=%-3s LSan=%-3s bytes=%-8s model=%-8s %s\n' \
             "$K" "$O" "$n" "$rc" "$lsan" "${bytes:-.}" "$want" "$status"
    done
  done
done
echo
if [ "$fail" -eq 0 ]; then
  echo "ALL $points POINTS AS DECLARED: the buggy rung reports a LeakSanitizer leak of"
  echo "exactly n_err * win_len bytes on every input that reaches the error path"
  echo "and is silent on every input that does not; the hardened rung is silent on"
  echo "all of them, at every optimisation level.  No other sanitizer fired."
else
  echo "*** SOMETHING IS WRONG -- read the rows marked above ***"
fi
exit "$fail"
