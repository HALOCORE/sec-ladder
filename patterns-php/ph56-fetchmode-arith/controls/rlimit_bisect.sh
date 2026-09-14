#!/bin/sh
# ph56 control -- WHAT RLIMIT DOES THIS PROOF ACTUALLY NEED? Bisected, not guessed.
#
#     sh patterns-php/ph56-fetchmode-arith/controls/rlimit_bisect.sh
#
# `verus.rs` ships with NO `#[verifier::rlimit]` attribute, which is a claim
# ("the default of 10 is enough") and not an omission. This script is the
# measurement behind it. It NEVER edits the shipped file: it writes a copy into
# .temp/php56rl/ with the attribute inserted, runs Verus on the copy plain and
# under `--cfg slb_twin`, and prints one line per value.
#
# ⚠ The two columns are not the same question. The twin build verifies TEN extra
# items (one safe twin per trusted accessor), so it is the harder of the two and
# it is the one that decides the floor -- `ph16` in the PAT programme ships
# `#[verifier::rlimit(30)]` because its TWIN build failed at 8 while its plain
# build was fine.
#
# MEASURED ON THIS BOX (Verus 0.2026.08.09.92f466f, z3 bundled), 2026-09-14:
#
#     rlimit   1    65 verified /  1 error   plain     75 /  1 error   twin
#     rlimit   2    66 verified /  0 errors  plain     76 /  0 errors  twin
#     rlimit   3    66 / 0                             76 / 0
#     rlimit   5    66 / 0                             76 / 0
#     rlimit   8    66 / 0                             76 / 0
#     rlimit  10    66 / 0                             76 / 0     <- Verus default
#     rlimit  20    66 / 0                             76 / 0
#     rlimit  30    66 / 0                             76 / 0
#     rlimit  40    66 / 0                             76 / 0
#     rlimit  60    66 / 0                             76 / 0
#     rlimit 100    66 / 0                             76 / 0
#     rlimit 200    66 / 0                             76 / 0
#     (no attribute)                        66 / 0     76 / 0
#
# ⭐ THE FLOOR IS 2 AND THE DEFAULT IS 5x THAT. `ph55` bisected to the same 2 on
# a proof of the same shape -- a whole interpreter with a value postcondition
# over the entire machine state -- which makes this an n = 2 result about the
# SHAPE rather than a fact about one row: every obligation in both files is one
# unfolding of a recursive definition whose shape the exec code mirrors, so Z3
# never searches.
#
# ⚠⚠ AND THE FIRST DRAFT OF `verus.rs` DID EXCEED THE DEFAULT. The cause was a
# WRONG LOOP INVARIANT and not proof size: two clauses that cannot hold at a
# `break` were declared `invariant` rather than `invariant_except_break`, Z3
# spent the budget failing to prove them, and the diagnostic was
# `Resource limit (rlimit) exceeded`. An rlimit error is a SYMPTOM, not a size,
# and the obvious repair -- raise the number -- would have shipped a proof with
# a wrong invariant and a 20x budget.
set -e
ROOT=$(cd "$(dirname "$0")/../../.." && pwd)
SRC="$ROOT/patterns-php/ph56-fetchmode-arith/verus.rs"
OUT="$ROOT/.temp/php56rl"
mkdir -p "$OUT"
TMP="$OUT/rl.rs"

run() {  # $1 = label, extra args in $2
    P=$(timeout 3000 "$ROOT/verus_run.py" "$TMP" 2>&1 | grep -a 'verification results' || echo 'FAILED/TIMEOUT')
    T=$(timeout 3000 "$ROOT/verus_run.py" "$TMP" --cfg slb_twin 2>&1 | grep -a 'verification results' || echo 'FAILED/TIMEOUT')
    printf '%-22s plain: %-42s twin: %s\n' "$1" "$P" "$T"
}

for R in 1 2 3 5 8 10 20 30 40 60 100 200; do
    # The shipped file has no attribute, so INSERT one above the kernel item.
    sed 's|^#\[cfg_attr(slb_isolated, inline(never))\]$|#[verifier::rlimit('"$R"')]\n#[cfg_attr(slb_isolated, inline(never))]|' \
        "$SRC" > "$TMP"
    # ⚠ ASSERT THE INSERTION BIT. A sed that matched nothing would measure the
    # shipped file twelve times and print a flat table that looks like a result.
    n=$(grep -c 'verifier::rlimit' "$TMP" || true)
    if [ "$n" != "1" ]; then
        echo "rlimit_bisect: insertion matched ${n}x, want 1 -- verus.rs has been" \
             "respelled and this script is measuring the wrong file" >&2
        exit 2
    fi
    run "rlimit $R"
done
cp "$SRC" "$TMP"
run "(no attribute)"
rm -f "$TMP"
