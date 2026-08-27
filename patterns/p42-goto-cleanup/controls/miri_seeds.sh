#!/bin/sh
# p42 control 4 -- MIRI, ACROSS SEEDS, AND THE LEAK CHECK IT DOES DO.
#
# Two things this answers that the gate's own Miri stage does not.
#
# (1) SEEDS.  `harness/check.py` passes no `MIRIFLAGS` and no `-Zmiri-seed`, and
#     `.memory/00-environment.md` records that Miri's alignment check is
#     SEED-DEPENDENT -- the same source clean on seeds 0 and 2 and reporting UB
#     on 1 and 3.  So a green gate row means "no UB at whatever seed ran", and
#     writing "Miri: N of N, no UB" as though it were seed-independent is what
#     that entry warns against.  This sweeps seeds 0..7 explicitly and prints
#     which ran.
#
# (2) THE LEAK CHECK, WHICH IS THE ONE MECHANICAL CHECK p42 HAS ON R4.
#     What stands behind "R4 does not leak" is Miri's own report at process exit
#     -- and an unexercised checker is indistinguishable from a satisfied one.
#     The POSITIVE CONTROL is the shipped `unsafe.rs` with the ERROR PATH's
#     `dig_free` deleted, generated here by substitution so it cannot drift:
#     Miri MUST report a leak on it, and MUST NOT on the shipped rung.
#
#     /!\ AMENDED AT TASK_110.  This paragraph used to say "Verus cannot state
#         leak-freedom at the pinned version (controls/affine_leak.rs), so what
#         stands behind `R4 does not leak` is Miri".  The first clause is
#         RETRACTED: R5 states leak-freedom and Verus checks it on every exit
#         (controls/ledger_leak.py, ../NOTES.md 6).  This control is NOT
#         weakened by that, because the ledger is a fact about R5 and this is
#         the check on R4: the two are byte-identical machine code, the ledger
#         is erased before codegen, and a proof carried by one rung is not a
#         proof about the other.
#
#   sh patterns/p42-goto-cleanup/controls/miri_seeds.sh
#
# Artefacts land in .temp/t104/miri/ and are re-derivable from this script.
set -u
REPO=$(cd "$(dirname "$0")/../../.." && pwd)
PDIR="$REPO/patterns/p42-goto-cleanup"
OUT="$REPO/.temp/t104/miri"
NIGHTLY=nightly-x86_64-unknown-linux-gnu
MIRI="$HOME/.rustup/toolchains/$NIGHTLY/bin/miri"
mkdir -p "$OUT"

SYSROOT=$("$HOME/.cargo/bin/cargo" "+$NIGHTLY" miri setup --print-sysroot 2>/dev/null)
[ -n "$SYSROOT" ] || { echo "no miri sysroot"; exit 1; }

# The gate clamps n_iters to 4 (check.py's MIRI_PROBE_ITERS); do the same, since
# what is being checked is UB and leakage per call, not throughput.
python3 - "$PDIR" "$OUT" <<'PY'
import glob, os, struct, sys
pdir, out = sys.argv[1], sys.argv[2]
for f in sorted(glob.glob(os.path.join(pdir, "inputs", "*.bin"))):
    # `sweep-*` is diagnostic and not part of the matrix -- `check.py` and
    # `measure.py` both skip it, and so must this control: 32 extra files times
    # 8 seeds is 40 minutes of interpretation for nothing.
    if os.path.basename(f).startswith("sweep-"):
        continue
    b = open(f, "rb").read()
    open(os.path.join(out, os.path.basename(f)), "wb").write(struct.pack("<Q", 4) + b[8:])
# THE POSITIVE CONTROL: the shipped R4 with the ERROR PATH's release deleted.
src = open(os.path.join(pdir, "unsafe.rs")).read()
old = """        // The error path, and the hand-written release the C rung is missing.
        dig_free(p, len, 1);
        return 0;"""
new = """        // CONTROL: the release deleted -- this rung now has the C rung's bug.
        return 0;"""
assert old in src, "unsafe.rs no longer contains the error path this control deletes"
open(os.path.join(out, "u_leaky.rs"), "w").write(src.replace(old, new))
PY

fail=0
# 180 s is check.py's own MIRI_TIMEOUT. A row that exceeds it is BLOCKED, which
# is what the gate does too -- `large.bin` is 1 000 000 u64s the driver decodes
# one element at a time under interpretation.
run_miri () {   # $1 = source, $2 = input, $3 = seed
  timeout 180 env -u LD_PRELOAD "$MIRI" --sysroot "$SYSROOT" --edition 2021 \
      -Zmiri-disable-isolation "-Zmiri-seed=$3" "$1" -- "$2" \
      >"$OUT/miri.out" 2>"$OUT/miri.err"
  echo $?
}

# The two BIG inputs are measured ONCE, not swept: `large.bin` (1 000 000 words)
# and `adversarial-wincap.bin` (200 000) are decoded element by element under
# interpretation and each costs the full 180 s budget, so sweeping them eight
# times would cost 48 minutes to learn one fact. What a seed changes is Miri's
# alignment/ordering nondeterminism, which is a property of the ACCESSES, and
# every access shape p42 has appears in the small inputs too.
echo "== the two big inputs, once, at the default seed =="
for f in "$OUT/large.bin" "$OUT/adversarial-wincap.bin"; do
  rc=$(run_miri "$PDIR/unsafe.rs" "$f" 0)
  if [ "$rc" = 124 ]; then
    printf '  %-28s BLOCKED (>180 s under interpretation)\n' "$(basename "$f")"
  elif grep -qE 'Undefined Behavior|memory leaked|error: ' "$OUT/miri.err"; then
    fail=1
    printf '  %-28s rc=%s :: %s\n' "$(basename "$f")" "$rc" \
      "$(grep -m1 -E 'Undefined Behavior|memory leaked|error: ' "$OUT/miri.err")"
  else
    printf '  %-28s no UB, no leak\n' "$(basename "$f")"
  fi
done

echo
echo "== seed sweep, shipped unsafe.rs, seeds 0..7, the NINE small inputs =="
for s in 0 1 2 3 4 5 6 7; do
  bad=0
  for f in "$OUT"/*.bin; do
    case "$(basename "$f")" in large.bin|adversarial-wincap.bin) continue ;; esac
    rc=$(run_miri "$PDIR/unsafe.rs" "$f" "$s")
    if [ "$rc" = 124 ]; then
      printf '  seed=%s %-28s BLOCKED (>180 s under interpretation)\n' \
             "$s" "$(basename "$f")"
    elif grep -qE 'Undefined Behavior|memory leaked|error: ' "$OUT/miri.err"; then
      # /!\ NOT `rc != 0`: `adversarial-shortlen.bin` exits 5 BY DESIGN (the
      # declared payload_len exceeds the file, `driver::load` refuses it), and a
      # control that read a correct exit code as UB would have flagged every
      # seed. What Miri reports goes on stderr; read that.
      bad=$((bad + 1)); fail=1
      printf '  seed=%s %-28s rc=%s :: %s\n' "$s" "$(basename "$f")" "$rc" \
        "$(grep -m1 -E 'Undefined Behavior|memory leaked|error: ' "$OUT/miri.err")"
    fi
  done
  [ "$bad" -eq 0 ] && echo "  seed=$s  nine small inputs: no UB, no leak"
done

echo
echo "== POSITIVE CONTROL: the same rung with the error path's dig_free deleted =="
echo "== (must report a leak on the inputs that reach the error path)          =="
for f in "$OUT"/adversarial-notag.bin "$OUT"/adversarial-mixed.bin \
         "$OUT"/adversarial-win1.bin "$OUT"/small.bin; do
  rc=$(run_miri "$OUT/u_leaky.rs" "$f" 0)
  if grep -q 'memory leaked' "$OUT/miri.err"; then leak=YES; else leak=no; fi
  case "$(basename "$f")" in
    small.bin) want=no ;;      # never reaches the error path
    *)         want=YES ;;
  esac
  st=OK; [ "$leak" = "$want" ] || { st="*** WRONG (want $want) ***"; fail=1; }
  printf '  %-28s rc=%-3s miri-leak=%-3s want=%-3s %s :: %s\n' \
    "$(basename "$f")" "$rc" "$leak" "$want" "$st" \
    "$(grep -m1 'memory leaked' "$OUT/miri.err" | cut -c1-70)"
done

echo
[ "$fail" -eq 0 ] && echo "ALL AS DECLARED" || echo "*** SOMETHING IS WRONG ***"
exit "$fail"
