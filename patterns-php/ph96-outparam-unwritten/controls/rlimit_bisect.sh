#!/usr/bin/env bash
# ph96 -- how big is the proof's SMT budget, and is the requirement MONOTONE?
#
#   bash patterns-php/ph96-outparam-unwritten/controls/rlimit_bisect.sh [max]
#
# `verus.rs` ships with NO `#[verifier::rlimit]`, and that is a MEASUREMENT
# rather than an omission. Verus's default is 10. This sweeps 1..max on both the
# plain and the `--cfg slb_twin` configuration and prints the pair.
#
# ⚠⚠ WHAT TO LOOK FOR IS NOT THE SMALLEST VALUE THAT PASSES -- IT IS WHETHER THE
# SEQUENCE IS MONOTONE. On `ph97`, before three `#[verifier::opaque]` attributes
# went on, `rlimit 10` passed, `30` FAILED and `60` passed: that is not *this
# proof is too big*, it is *this proof is a coin flip*, and raising the number
# would have hidden it behind a green line. ⭐ An rlimit error is a SHAPE, not a
# size.
#
# ph96 carries `#[verifier::opaque]` on `s_step` and `s_fold_zval` for the same
# reason: without them `kernel`'s loop unfolds `s_run` -> `s_step` ->
# `s_fold_zval` -> ten `s_fold_bytes` recursions on every iteration.
#
# ⚠ It rewrites a SCRATCH copy of verus.rs, never the shipped file.
set -euo pipefail
MAX="${1:-30}"
SEC=/home/apt/repos_common/sec-ladder
ROW=$SEC/patterns-php/ph96-outparam-unwritten
W=$SEC/.temp/php96/rlimit
mkdir -p "$W"

printf '%-8s %-26s %s\n' rlimit plain twin
for n in $(seq 1 "$MAX"); do
	sed "s|^#\[cfg_attr(slb_isolated, inline(never))\]$|#[verifier::rlimit($n)]\n#[cfg_attr(slb_isolated, inline(never))]|" \
		"$ROW/verus.rs" > "$W/k.rs"
	grep -qa "verifier::rlimit($n)" "$W/k.rs" || { echo "REFUSING: the rlimit attribute was not inserted"; exit 2; }
	p=$(cd "$SEC" && timeout 1800 ./verus_run.py "$W/k.rs" 2>&1 | grep -ao '[0-9]* verified, [0-9]* errors' | tail -1)
	t=$(cd "$SEC" && timeout 1800 ./verus_run.py "$W/k.rs" --cfg slb_twin 2>&1 | grep -ao '[0-9]* verified, [0-9]* errors' | tail -1)
	printf '%-8s %-26s %s\n' "$n" "${p:-<no verdict>}" "${t:-<no verdict>}"
done
echo
echo 'ⓘ the shipped file carries NO rlimit attribute at all; the table above is'
echo '  what licenses that. Read it for MONOTONICITY, not for a minimum.'
