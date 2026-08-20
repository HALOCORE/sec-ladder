#!/usr/bin/env bash
# Build p18's control cells from `.temp/p18/ctl/` at the gate's own flags.
#
#   python3 patterns/p18-varint-shift/controls/gen_controls.py
#   bash    patterns/p18-varint-shift/controls/build_controls.sh
#
# Binaries land in `.temp/p18/ctlbin/`, never in the pattern dir, and are
# re-derivable from the two scripts above -- `.memory/00-environment.md`
# constraint 6, so they are deleted once the gate is green and the GENERATORS
# stay.
#
# Flags are `harness/build.py`'s exactly: -std=c99 -Wall -Wextra -O3
# -DSLB_ISOLATED for C, and --edition 2021 -C codegen-units=1 -C opt-level=3
# -C debug-assertions=off --cfg slb_isolated for Rust. A control built at other
# flags is not on the same axis as the cells it is compared with.
#
# THE THREE RUST OPT AXES ARE ALL BUILT HERE, and p18 is the first pattern in
# this project to build `O0d` on anything:
#
#   O0   -C opt-level=0 -C debug-assertions=off   the semantics-matched O0 cell
#   O0d  -C opt-level=0 -C debug-assertions=on    NOT semantics-matched to C -O0
#   O3   -C opt-level=3 -C debug-assertions=off   where the perf claims live
#
# `harness/build.py`'s ALL_OPTS is ["O0", "O0d", "O3"] and has no `-O3` +
# debug-assertions cell at all, so the fourth combination is built HERE as
# `O3d` and is a CONTROL, not a matrix cell. ../NOTES.md 5 says what that is
# for and why no harness change was made for it.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
PDIR="$REPO/patterns/p18-varint-shift"
CTL="$REPO/.temp/p18/ctl"
BIN="$REPO/.temp/p18/ctlbin"
GCC=/usr/bin/gcc
CLANG="$HOME/tools/llvm/bin/clang"
RUSTC="$HOME/.cargo/bin/rustc"
CFLAGS=(-std=c99 -Wall -Wextra -O3 -DSLB_ISOLATED -I "$REPO/common" -I "$PDIR/c")
RBASE=(--edition 2021 -C codegen-units=1 --cfg slb_isolated)

mkdir -p "$BIN"

# --- C controls: same driver, same header, a different kernel TU ------------
for k in c_mask c_ncap c_reject; do
  for cc in gcc clang; do
    if [ "$cc" = gcc ]; then CC="$GCC"; else CC="$CLANG"; fi
    "$CC" "${CFLAGS[@]}" "$REPO/common/driver.c" "$CTL/${k}_kernel.c" \
        "$PDIR/c/main.c" -o "$BIN/${k}-${cc}"
    echo "  built ${k}-${cc}"
  done
done

# --- Rust controls, at O3 (the perf axis) -----------------------------------
for r in n_noguard t_noguard u_noguard t_1step t_chain t_iter t_pos \
         t_wshl t_cshl u_ushl; do
  "$RUSTC" "${RBASE[@]}" -C opt-level=3 -C debug-assertions=off \
      "$CTL/$r.rs" -o "$BIN/$r-O3" || echo "  FAILED $r-O3"
  echo "  built $r-O3"
done

# --- the four Rust (opt-level x debug-assertions) cells, on the rungs AND on
# --- the three delete-the-check controls. This is the O0d axis.
for r in n_noguard t_noguard u_noguard; do
  "$RUSTC" "${RBASE[@]}" -C opt-level=0 -C debug-assertions=off \
      "$CTL/$r.rs" -o "$BIN/$r-O0"
  "$RUSTC" "${RBASE[@]}" -C opt-level=0 -C debug-assertions=on \
      "$CTL/$r.rs" -o "$BIN/$r-O0d"
  "$RUSTC" "${RBASE[@]}" -C opt-level=3 -C debug-assertions=on \
      "$CTL/$r.rs" -o "$BIN/$r-O3d"
  echo "  built $r-O0 $r-O0d $r-O3d"
done
for r in safe_naive safe_tuned unsafe; do
  "$RUSTC" "${RBASE[@]}" -C opt-level=3 -C debug-assertions=on \
      "$PDIR/$r.rs" -o "$BIN/$r-O3d"
  echo "  built $r-O3d (the shipped rung at the fourth, non-matrix combination)"
done

echo "controls in $BIN"
