#!/bin/sh
# ph97: what proof budget does `kernel` actually need, in BOTH configurations?
#
# `verus.rs` carries `#[verifier::rlimit(N)]` on `kernel`, and a number in a
# source file is a claim like any other. This re-derives it: it rewrites the
# attribute to each value in turn, runs the verifier plain and under
# `--cfg slb_twin`, and prints the table. Nothing here is cached and nothing is
# asserted -- read the output.
#
#     sh patterns-php/ph97-optarg-unwritten/controls/rlimit_bisect.sh [values...]
#
# ⚠ It edits a COPY under `.temp/php97/rlimit/`; `verus.rs` itself is not
# touched. ⚠ It is slow -- about a minute per (value, configuration) pair.
#
# ⚠⚠ THE TWIN SIDE IS THE EXPENSIVE ONE and that is not an accident: under
# `--cfg slb_twin` seven verified twins join the module's SMT context and
# `kernel` pays for all of them. A budget that passes plain and fails twin is a
# proof that passes on one side of a coin flip. ../NOTES.md §11 has the numbers
# this script produced.
set -eu
ROW="$(cd "$(dirname "$0")/.." && pwd)"
REPO="$(cd "$ROW/../.." && pwd)"
OUT="$REPO/.temp/php97/rlimit"
mkdir -p "$OUT"
VALUES="${*:-1 2 5 10 20 30 60 90}"

printf '%-8s %-28s %s\n' rlimit plain 'twin (--cfg slb_twin)'
for v in $VALUES; do
    sed "s/#\[verifier::rlimit([0-9]*)\]/#[verifier::rlimit($v)]/" \
        "$ROW/verus.rs" > "$OUT/verus_$v.rs"
    p=$(cd "$REPO" && timeout 1800 ./verus_run.py "$OUT/verus_$v.rs" 2>&1 \
        | grep -a 'verification results' || echo 'TIMEOUT/ERROR')
    t=$(cd "$REPO" && timeout 1800 ./verus_run.py "$OUT/verus_$v.rs" --cfg slb_twin 2>&1 \
        | grep -a 'verification results' || echo 'TIMEOUT/ERROR')
    printf '%-8s %-28s %s\n' "$v" "$(echo "$p" | sed 's/.*:://')" "$(echo "$t" | sed 's/.*:://')"
done
