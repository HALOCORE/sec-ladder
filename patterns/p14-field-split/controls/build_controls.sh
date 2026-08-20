#!/usr/bin/env bash
# Build p14's control cells from `.temp/p14/ctl/` at the gate's own flags.
#
#   python3 patterns/p14-field-split/controls/gen_controls.py
#   bash    patterns/p14-field-split/controls/build_controls.sh
#
# Binaries land in `.temp/p14/ctlbin/`, never in the pattern dir, and are
# re-derivable from the two scripts above -- `.memory/00-environment.md`
# constraint 6, so they are deleted once the gate is green and the GENERATORS
# stay.
#
# Flags are `harness/build.py`'s O3/isolated exactly: -std=c99 -Wall -Wextra
# -O3 -DSLB_ISOLATED for C, and --edition 2021 -C codegen-units=1
# -C opt-level=3 -C debug-assertions=off --cfg slb_isolated for Rust. A control
# built at other flags is not on the same axis as the cells it is compared with.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
PDIR="$REPO/patterns/p14-field-split"
CTL="$REPO/.temp/p14/ctl"
BIN="$REPO/.temp/p14/ctlbin"
GCC=/usr/bin/gcc
CLANG="$HOME/tools/llvm/bin/clang"
RUSTC="$HOME/.cargo/bin/rustc"
CFLAGS=(-std=c99 -Wall -Wextra -O3 -DSLB_ISOLATED -I "$REPO/common" -I "$PDIR/c")
RFLAGS=(--edition 2021 -C codegen-units=1 -C opt-level=3 -C debug-assertions=off --cfg slb_isolated)

mkdir -p "$BIN"

# --- C controls: same driver, same header, a different kernel TU ------------
for k in c_hcond c_memchr c_strtok; do
  for cc in gcc clang; do
    if [ "$cc" = gcc ]; then CC="$GCC"; else CC="$CLANG"; fi
    "$CC" "${CFLAGS[@]}" "$REPO/common/driver.c" "$CTL/${k}_kernel.c" \
        "$PDIR/c/main.c" -o "$BIN/${k}-${cc}"
    echo "  built ${k}-${cc}"
  done
done

# --- Rust controls ---------------------------------------------------------
for r in n_nocap t_nocap u_nocap t_1step t_idxfold t_pos t_split m_nolen m_nocount; do
  "$RUSTC" "${RFLAGS[@]}" "$CTL/$r.rs" -o "$BIN/$r"
  echo "  built $r"
done

echo "controls in $BIN"
