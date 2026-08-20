#!/usr/bin/env bash
# Re-run every behavioural claim ../NOTES.md makes about p18's controls, and
# print the evidence. Nothing here is a perf measurement -- the prices are in
# controls/sweep_ir.py and controls/fit.py.
#
#   python3 patterns/p18-varint-shift/controls/gen_controls.py
#   bash    patterns/p18-varint-shift/controls/build_controls.sh
#   bash    patterns/p18-varint-shift/controls/verify_controls.sh
#
# The three sections are ../NOTES.md 7 (the delete-the-check rows), 9 (the
# priced fiats and their prover disposition) and 10 (the Verus mutants).
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
PDIR="$REPO/patterns/p18-varint-shift"
CTL="$REPO/.temp/p18/ctl"
BIN="$REPO/.temp/p18/ctlbin"
I="$PDIR/inputs"
MIRI="$HOME/.rustup/toolchains/nightly-x86_64-unknown-linux-gnu/bin/miri"
SYSROOT="$(cd "$REPO" && "$HOME/.cargo/bin/cargo" +nightly-x86_64-unknown-linux-gnu miri setup --print-sysroot 2>/dev/null | tail -1)"

echo "=============================================================="
echo " 7. THE DELETE-THE-CHECK ROWS -- the same source at four Rust"
echo "    (opt-level x debug-assertions) combinations."
echo "    O0 and O3 are TWO OF THE 24 MEASURED CELLS' flags."
echo "=============================================================="
printf "%-12s %-5s %-24s %-6s %s\n" cell opt input rc stdout/stderr
for r in n_noguard t_noguard u_noguard; do
  for o in O0 O0d O3 O3d; do
    for f in small adversarial-shift11; do
      out=$("$BIN/$r-$o" "$I/$f.bin" 2>"$BIN/.err"); rc=$?
      err=$(grep -m1 'panicked\|attempt to' "$BIN/.err" | head -1)
      printf "%-12s %-5s %-24s %-6s %s%s\n" "$r" "$o" "$f" "$rc" "$out" "$err"
    done
  done
done
echo
echo "  model:  small = 14238010737147540887"
echo "          adversarial-shift11 (CHECKED rungs) = 9722957826816"
echo "          adversarial-shift11 (C rung R1)     = 1758263303383808"
echo
echo "  ...and under Miri (which runs with debug-assertions ON):"
for r in n_noguard u_noguard; do
  for f in small adversarial-shift11 adversarial-sat truncating; do
    p="$REPO/.temp/p18/miri/$f.bin"
    [ -f "$p" ] || continue
    out=$(timeout 400 "$MIRI" --sysroot "$SYSROOT" --edition 2021 \
            -Zmiri-disable-isolation "$CTL/$r.rs" -- "$p" 2>"$BIN/.err"); rc=$?
    printf "    miri %-12s %-22s rc=%-4s %s %s\n" "$r" "$f" "$rc" "$out" \
           "$(grep -m1 'attempt to\|Undefined Behavior' "$BIN/.err")"
  done
done

echo
echo "=============================================================="
echo " 9. THE PRICED FIATS -- values, and the sanitizer on c_mask"
echo "=============================================================="
printf "%-14s %-24s %s\n" binary input stdout
for b in c_mask-gcc c_mask-clang c_ncap-gcc c_reject-gcc t_wshl-O3 t_cshl-O3 u_ushl-O3; do
  for f in small adversarial-shift11 adversarial-sat; do
    printf "%-14s %-24s %s\n" "$b" "$f" "$("$BIN/$b" "$I/$f.bin" 2>&1 | tail -1)"
  done
done
echo
echo "  c_mask under the GATE'S OWN ASan+UBSan flags (check.py:4390):"
if [ ! -x "$BIN/c_mask-asan" ]; then
  /usr/bin/gcc -std=c99 -Wall -Wextra -O1 -g -fsanitize=address,undefined \
    -static-libasan -static-libubsan -DSLB_ISOLATED \
    -I "$REPO/common" -I "$PDIR/c" "$REPO/common/driver.c" \
    "$CTL/c_mask_kernel.c" "$PDIR/c/main.c" -o "$BIN/c_mask-asan"
fi
for f in adversarial-shift11 adversarial-sat; do
  echo "    -- $f"
  "$BIN/c_mask-asan" "$I/$f.bin"; echo "       rc=$?"
done

echo
echo "=============================================================="
echo " 10. THE VERUS MUTANTS -- read the ERROR TEXT, not the exit code"
echo "=============================================================="
for m in m_noguard m_noguard_ms m_wshl m_wshl_ms; do
  echo "--- $m"
  timeout 1200 "$REPO/verus_run.py" "$CTL/$m.rs" 2>&1 | grep -E '^error|verification results' | head -6
done
echo "--- m_weakreq (shipped config)"
timeout 1200 "$REPO/verus_run.py" "$CTL/m_weakreq.rs" 2>&1 | grep -E '^error|verification results' | head -4
echo "--- m_weakreq (--cfg slb_twin: the TWIN must fail)"
timeout 1200 "$REPO/verus_run.py" "$CTL/m_weakreq.rs" --cfg slb_twin 2>&1 | grep -E '^error|verification results' | head -4
echo "--- the shl family's availability to an R4, at the pinned vstd"
timeout 1200 "$REPO/verus_run.py" "$CTL/probe_shl_family.rs" 2>&1 | grep -E 'is not supported|verification results' | head -6
timeout 1200 "$REPO/verus_run.py" "$CTL/probe_shl_bare.rs" 2>&1 | grep -E 'is not supported|verification results' | head -3
timeout 1200 "$REPO/verus_run.py" "$CTL/probe_shl_unchecked.rs" 2>&1 | grep -E 'is not supported|verification results' | head -3
