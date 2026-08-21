#!/bin/sh
# Build p27's control rungs. Generators are committed; the binaries are not
# (`CLAUDE.md` constraint 6 -- keep the generator, delete the artefact).
#
#   sh patterns/p27-handle-table/controls/build_controls.sh [OUTDIR]
#
# Defaults to .temp/p27/controls. `r5_vstdpure.rs` goes through ./verus_run.py
# --compile, so it is verified as well as built: its whole point is that it
# VERIFIES with a smaller trusted base and still is not a rung, because the
# R4/R5 identity pin drops to `differ`.
set -e
REPO=$(cd "$(dirname "$0")/../../.." && pwd)
OUT=${1:-$REPO/.temp/p27/controls}
RUSTC=$HOME/.cargo/bin/rustc
RFLAGS="--edition 2021 -C codegen-units=1 -C opt-level=3 -C debug-assertions=off"

python3 "$REPO/patterns/p27-handle-table/controls/gen_controls.py" --out "$OUT"

for f in r4_tabchecked r3_issome r2_epilogue; do
    for mode in isolated whole; do
        cfg=""; [ "$mode" = isolated ] && cfg="--cfg slb_isolated"
        # shellcheck disable=SC2086
        timeout 600 $RUSTC $RFLAGS $cfg "$OUT/$f.rs" -o "$OUT/$f-O3-$mode"
        echo "  built $f-O3-$mode"
    done
done

# The proof control: verify AND compile, both inline modes.
for mode in isolated whole; do
    cfg=""; [ "$mode" = isolated ] && cfg="--cfg slb_isolated"
    # shellcheck disable=SC2086
    timeout 3600 python3 "$REPO/verus_run.py" --compile "$OUT/r5_vstdpure.rs" \
        -o "$OUT/r5_vstdpure-O3-$mode" -C opt-level=3 -C debug-assertions=off \
        -C codegen-units=1 $cfg
    echo "  built r5_vstdpure-O3-$mode"
done

echo "controls in $OUT"
