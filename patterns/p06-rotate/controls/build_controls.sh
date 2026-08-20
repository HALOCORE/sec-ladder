#!/bin/bash
# Build every control `gen_controls.py` emits, with the SAME flags
# `harness/build.py` uses for the shipped `-O3 isolated` cells.
#
#   bash patterns/p06-rotate/controls/build_controls.sh
#
# Rust:  rustc --edition 2021 -C opt-level=3 -C debug-assertions=off
#               -C codegen-units=1 --cfg slb_isolated
# C:     <cc> -std=c99 -O3 -DSLB_ISOLATED   kernel + c/main.c + common/driver.c
#
# The Verus controls are NOT built here -- they are verified, not run
# (`verify_controls.sh`).
set -u
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
CTL="$REPO/.temp/p06/controls"
OUT="$REPO/.temp/p06/ctlbin"
RUSTC="$HOME/.cargo/bin/rustc"
CLANG="$HOME/tools/llvm/bin/clang"
GCC=/usr/bin/gcc
mkdir -p "$OUT"

rc=0
for f in "$CTL"/a_nored_safe_naive.rs "$CTL"/a_nored_safe_tuned.rs \
         "$CTL"/a_nored_unsafe.rs "$CTL"/c_idx.rs "$CTL"/c_oneshot.rs \
         "$CTL"/c_r4inline.rs "$CTL"/c_reverse.rs "$CTL"/c_rotate.rs \
         "$CTL"/c_copywithin.rs "$CTL"/c_foldidx.rs \
         "$CTL"/c_swap.rs "$CTL"/e_revonly.rs "$CTL"/e_foldonly.rs "$CTL"/e_hdronly.rs; do
    n=$(basename "$f" .rs)
    if timeout 300 "$RUSTC" --edition 2021 -C opt-level=3 -C debug-assertions=off \
        -C codegen-units=1 --cfg slb_isolated -o "$OUT/$n" "$f" 2>"$OUT/$n.err"; then
        echo "  ok   $n"
    else
        echo "  FAIL $n"; head -5 "$OUT/$n.err"; rc=1
    fi
done

for f in "$CTL"/d_cmp.c "$CTL"/d_sub.c; do
    n=$(basename "$f" .c)
    for cc in gcc clang; do
        [ "$cc" = gcc ] && CC="$GCC" || CC="$CLANG"
        if timeout 300 "$CC" -std=c99 -O3 -DSLB_ISOLATED \
            -I"$REPO/patterns/p06-rotate/c" -I"$REPO/common" \
            -o "$OUT/$n-$cc" "$f" "$REPO/patterns/p06-rotate/c/main.c" \
            "$REPO/common/driver.c" 2>"$OUT/$n-$cc.err"; then
            echo "  ok   $n-$cc"
        else
            echo "  FAIL $n-$cc"; head -5 "$OUT/$n-$cc.err"; rc=1
        fi
    done
done
exit $rc
