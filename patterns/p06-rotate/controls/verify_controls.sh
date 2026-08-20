#!/bin/bash
# Put every Verus control through `./verus_run.py`, in both configurations, and
# print the verdict line. `.memory/05-layout.md` rule 11: these cannot live in
# the pattern dir, so this script plus `gen_controls.py` IS their reproduction
# path.
#
#   bash patterns/p06-rotate/controls/verify_controls.sh
#
# WHAT EACH MUTANT ACTUALLY DOES, measured (TASK_048) rather than predicted.
# The header here used to promise two controls this file does not generate
# (`a_nored_verus`, `b_msonly`) and to state expectations the pattern REFUTES;
# `.memory/05-layout.md` rule 11 makes this script the mutants' reproduction
# path, so its docstring is evidence and it is now the measured table.
#
#   b_nored          MUST FAIL. The reduction is deleted, so nothing establishes
#                    `r <= m`, `rot_left`'s domain is violated and the store at
#                    `scr[b - 1]` has no bound. Positive control for the proof.
#                    shipped 17/1 -- and its shipped-configuration failure is
#                    ** `while loop: Resource limit (rlimit) exceeded` **, NOT an
#                    obligation. Under --cfg slb_twin 22/1 `invariant not
#                    satisfied before loop`, which is the obligation. Raising
#                    --rlimit to 30 or 60 does not change it: the query diverges.
#                    ../NOTES.md 10 measures what moved the exhaustion here.
#   b_nored_msonly   MUST FAIL, 17/1 + 22/1 `invariant not satisfied before
#                    loop`. ** This REFUTES what TASK_047 predicted **: a
#                    memory-safety-only spec does NOT accept the unreduced
#                    kernel, because a proof quantifies over all inputs and the
#                    unreduced kernel is genuinely unsafe in regime 2. Separating
#                    "functionally wrong" from "memory-unsafe" needs a PROGRAM
#                    change, which is b_scrmod_msonly.
#   b_scrmod         MUST FAIL, 17/1 + 22/1 `precondition not satisfied`.
#   b_scrmod_msonly  MUST VERIFY, 18/0 and twin 23/0 -- ** this is p06's result
#                    **: `r %= SCR` is memory-safe on every input and
#                    functionally wrong on exactly regime 1, so the two specs
#                    disagree on one shipped-shaped program. It is caught by
#                    `spec.md`'s contract pin (1 clause diff) AND by the
#                    `identity` pin (174/166 against R4's 216/208).
#   b_weakreq        MUST VERIFY in the shipped configuration (18/0) and MUST
#                    FAIL under --cfg slb_twin (22/1, `precondition not met:
#                    index in bounds for this access`), because the twin's
#                    `v[i] = x` no longer verifies. It is ALSO caught by
#                    `spec.md`'s contract pin, with 2 clause diffs -- so the twin
#                    is the sole VERUS-LEVEL catcher and not the sole catcher
#                    (../NOTES.md 10b).
#   b_tautology      MUST FAIL, 17/1 + 22/1 `assertion failed`. ** This REFUTES
#                    the p02 M7 shape on p06 **: the driver's consuming
#                    `assert(r == rotate_fold(...))` still names the real spec,
#                    so weakening the kernel's postcondition breaks the CALL
#                    SITE and Verus catches it without any pin.
#
# The counts moved 16/21 -> 17/22 and 17/22 -> 18/23 at TASK_048, when
# `scr_load` stopped being `external_body` and its body became an obligation in
# the mutants too. No verdict moved.
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
