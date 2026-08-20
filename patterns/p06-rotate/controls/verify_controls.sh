#!/bin/bash
# Put every Verus control through `./verus_run.py`, in both configurations, and
# print the verdict line. `.memory/05-layout.md` rule 11: these cannot live in
# the pattern dir, so this script plus `gen_controls.py` IS their reproduction
# path.
#
#   bash patterns/p06-rotate/controls/verify_controls.sh
#
# Expected, and each is a different KIND of failure:
#
#   a_nored_verus  MUST FAIL to verify. The reduction is gone, so nothing
#                  establishes `r <= m`, `rot_left`'s domain is violated and the
#                  store at `scr[b - 1]` has no bound. This is the positive
#                  control for the whole proof.
#   b_msonly       MUST VERIFY. Same buggy exec code, postcondition weakened to
#                  memory safety only. **This is p06's result**: a
#                  memory-safety-only proof of this kernel accepts a bug that
#                  stays inside the scratch, i.e. the whole of regime 1.
#   b_weakreq      MUST FAIL under --cfg slb_twin (the twin's `v[i] = x` no
#                  longer verifies) and is separately caught by spec.md's
#                  `verus.items` pin. The shipped configuration may still pass:
#                  that is the point of the twin stage.
#   b_tautology    MUST VERIFY in both configurations, and be caught ONLY by
#                  spec.md's contract pin -- p02's M7 shape, on p06's functional
#                  postcondition.
set -u
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
CTL="$REPO/.temp/p06/controls"
cd "$REPO" || exit 1
for n in b_nored b_nored_msonly b_scrmod b_scrmod_msonly b_weakreq b_tautology; do
    for cfg in "" "--cfg slb_twin"; do
        printf "%-16s %-14s " "$n" "${cfg:-<shipped>}"
        # shellcheck disable=SC2086
        out=$(timeout 1800 ./verus_run.py "$CTL/$n.rs" $cfg 2>&1)
        v=$(echo "$out" | grep -E "^verification results::" | head -1)
        e=$(echo "$out" | grep -E "^error: " | head -1)
        echo "${v:-<no verdict>}   ${e:-}"
    done
done
