#!/usr/bin/env bash
# Check p14's control cells against `model.py` and put the two prover probes
# through `./verus_run.py`.
#
#   python3 patterns/p14-field-split/controls/gen_controls.py
#   bash    patterns/p14-field-split/controls/build_controls.sh
#   bash    patterns/p14-field-split/controls/verify_controls.sh
#
# Two different questions, and they must not be run together in one's head:
#
#  1. **Does the control compute the pattern's function?** Every control except
#     the delete-the-check family and the fold mutants must print `model.py`'s
#     checksum on every matrix input; a control that does not is measuring a
#     different kernel and its Ir figure is not comparable to a rung's. The
#     delete-the-check family is EXPECTED to diverge, and how it diverges is the
#     finding (../NOTES.md 7).
#
#  2. **Would the PROVER admit it?** `.memory/01-ladder.md`: an R4 is not merely
#     a program that may use `unsafe`, it is a program that must have a
#     byte-identical R5 twin that Verus verifies -- so a spelling that is
#     `is not supported` at the pinned vstd is inadmissible as R4 whatever it
#     costs. **Read the ERROR TEXT and not the exit code**: `is not supported`
#     disqualifies; `postcondition not satisfied` disqualifies nothing.
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
PDIR="$REPO/patterns/p14-field-split"
BIN="$REPO/.temp/p14/ctlbin"
CTL="$REPO/.temp/p14/ctl"
IN="$PDIR/inputs"

echo "== 1. checksums against model.py =="
python3 - "$PDIR" "$BIN" "$IN" <<'PY'
import glob, os, subprocess, sys
pdir, binp, indir = sys.argv[1:4]
sys.path.insert(0, pdir)
import model as M
AGREE = ["c_hcond-gcc", "c_hcond-clang", "c_memchr-gcc", "c_memchr-clang",
         "t_1step", "t_idxfold", "t_pos", "t_split"]
DIVERGE = ["c_strtok-gcc", "c_strtok-clang", "n_nocap", "t_nocap", "u_nocap",
           "m_nolen", "m_nocount"]
inputs = sorted(glob.glob(os.path.join(indir, "*.bin")))
inputs = [p for p in inputs if not os.path.basename(p).startswith("sweep-")]
print(f"{'control':16s} " + " ".join(f"{os.path.basename(p)[:11]:>12s}" for p in inputs))
bad = 0
for c in AGREE + DIVERGE:
    b = os.path.join(binp, c)
    if not os.path.exists(b):
        print(f"{c:16s} NOT BUILT"); continue
    row = f"{c:16s} "
    for p in inputs:
        exp = M.build(p).checksum
        r = subprocess.run([b, p], capture_output=True, text=True)
        got = r.stdout.strip()
        if r.returncode != 0:
            mark = f"rc{r.returncode}"
        elif got == str(exp):
            mark = "="
        else:
            mark = "DIFF"
        if c in AGREE and mark != "=":
            bad += 1
            mark = "!" + mark
        row += f" {mark:>12s}"
    print(row)
print(f"\n{bad} unexpected divergence(s) among the controls that must agree")
PY

echo
echo '== 2. would the prover admit <[T]>::split ? =='
echo "-- reading the ERROR TEXT, not the exit code --"
timeout 900 "$REPO/verus_run.py" "$CTL/v_split_probe.rs" 2>&1 \
  | grep -E "is not supported|not supported|error:|verification results" | head -10
