#!/usr/bin/env python3
"""p49 CONTROLS: **the census that makes the benign invariant a checked property
rather than an argument** -- which of this pattern's shipped blobs execute a
BREAK on a record whose buffer is SHARED?

    python3 patterns/p49-interned-pool/controls/no_share_break.py

WHY THIS EXISTS
---------------
`harness/check.py` stage 2 requires every non-adversarial cell to agree with
`../model.py` **and with every other cell**, and a BREAK on a shared record is
exactly where R1 and R1h part company. ⚠ **The divergence is not only the
corrupted byte**: R1h's copy-on-write also spends private storage and clears the
record's ownership flag, and the epilogue folds that flag, so a BREAK on a shared
record moves the checksum *even when no other record was naming the buffer*.
Both halves are excluded by one property, which is why it is stated about the
FLAG:

    no non-adversarial window may execute a BREAK on a record with `rshd == 1`.

⚠ A structural claim of that shape is exactly the kind this project has been
wrong about before, so it is checked in THREE independent places rather than
assumed once:

  1. `../inputs/gen.py` cannot EMIT one -- `benign_ops` looks for an operand
     naming an OWNED record and emits a READ when the window holds none -- **and
     re-checks the bytes it wrote anyway**, because a filter that cannot fire
     proves nothing;
  2. `../model.py::no_share_break_problems` re-derives the property from the
     SHIPPED blob, and `selfcheck()` runs it once per input on **every gate
     invocation**;
  3. this file, which censuses every `.bin` in `../inputs/` at once and prints
     the op histogram beside the guard's two answers, so a reader can see the
     answer for the whole directory instead of one input at a time.

⚠⚠ **AND UNTIL `TASK_163` NONE OF THE THREE HAD A MUST-FIRE ARM INSIDE THE
GATE**, which is `.memory/03-measurement.md` entry 19 one level up: neuter
`window_share_break` to `return False, 0, 0` and place 2 goes silent, place 1
stops filtering, and place 3 -- this file -- **is HASHED by the gate but never
RUN by it**, so nothing turns red (`TASK_162` MINOR 7, measured on all nine
inputs). ✅ **`../model.py::census_selftest()` is the repair**: four hand-built
probe windows on which the census must answer three different ways, an arm that
makes `no_share_break_problems` itself REPORT, and an arm for the arena-capacity
refusal that no shipped input reaches. `selfcheck()` runs it once per input on
every gate invocation, exactly as it runs `detector_selftest()`. **Seven planted
defects, seven designed messages, zero crashes** (`.temp/t163/e5_mutate.py`).

⚠ It walks the cursor the RUNGS walk -- `nops` operations, two bytes each,
stopping when `len - p < 2` -- so an op the header DECLARES but the window cannot
hold is not counted. A census over raw bytes would over-report and would
therefore be the wrong check.

WHAT IT ASSERTS: every non-`adversarial-` blob evaluates the guard **only with
the answer FALSE**, and every `adversarial-` blob except
`adversarial-stride3.bin` (whose windows the driver guard skips entirely)
evaluates it TRUE at least once. **Both directions**, because a census that only
ever says "no shared BREAK here" would pass on an empty directory.

⚠ **And a third direction, which p34's equivalent could not have**: the guard
must be EVALUATED on the matrix inputs, not merely be false there. p34's safety
line cannot execute on a benign input at all, so its benign cost gradient is
`0.00`; p49's is evaluated on every BREAK, which is why this row HAS a benign
gradient. A matrix blob with zero guard evaluations would silently turn p49 into
p34 and is reported as a problem.
"""

import glob
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
sys.path.insert(0, os.path.join(REPO, "common"))
sys.path.insert(0, PDIR)

import slb            # noqa: E402
import model as m49   # noqa: E402

NAMES = ("DEFINE", "DEFINE", "BREAK", "READ")

#: `adversarial-stride3.bin`'s window is 3 bytes, below the driver's
#: `stride_w >= 4` guard, so the loop is skipped and NO op of any kind executes.
#: It is an adversarial file that legitimately breaks nothing, and saying so here
#: is what stops the "every adversarial blob has one" arm from being a rule with
#: a silent exception.
NO_OPS = ("adversarial-stride3.bin",)


def window_ops(buf, off, ln):
    """The op codes the window at `off` actually EXECUTES, in order."""
    if ln < m49.HDR:
        return []
    nops = int.from_bytes(buf[off:off + 4], "little")
    out, p = [], m49.HDR
    for _ in range(nops):
        if ln - p < m49.OPSZ:
            break
        out.append(buf[off + p] % 4)
        p += m49.OPSZ
    return out


def census(path):
    f = slb.read(path)
    payload = f.payload[: f.declared_len]
    stride, buf = slb.head1_u64_bytes(payload)
    n_blob = len(buf)
    hist = [0, 0, 0, 0]
    gt = gf = nwin = 0
    if m49.HDR <= stride <= n_blob:
        nwin = n_blob // stride
        for w in range(nwin):
            for op in window_ops(buf, w * stride, stride):
                hist[op] += 1
            _, t, fa = m49.window_share_break(buf, w * stride, stride)
            gt += t
            gf += fa
    return stride, n_blob, nwin, hist, gt, gf


def derived_from():
    out = {}
    for rel in ("patterns/p49-interned-pool/inputs/gen.py",
                "patterns/p49-interned-pool/model.py",
                "patterns/p49-interned-pool/controls/no_share_break.py"):
        p = os.path.join(REPO, rel)
        out[rel] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return out


def main():
    paths = sorted(glob.glob(os.path.join(PDIR, "inputs", "*.bin")))
    if not paths:
        print("no_share_break.py: no .bin files -- run inputs/gen.py first",
              file=sys.stderr)
        return 1
    rows, problems = [], []
    print(f"{'input':32s} {'stride':>7s} {'nwin':>5s}  {'DEFINE':>7s} "
          f"{'BREAK':>6s} {'READ':>6s}   {'guard T':>8s} {'guard F':>8s}")
    for p in paths:
        name = os.path.basename(p)
        stride, n_blob, nwin, hist, gt, gf = census(p)
        adv = name.startswith("adversarial-")
        ndef = hist[0] + hist[1]
        rows.append({"input": name, "stride": stride, "n_blob": n_blob,
                     "nwin": nwin, "define": ndef, "break": hist[2],
                     "read": hist[3], "guard_true": gt, "guard_false": gf,
                     "adversarial": adv})
        print(f"{name:32s} {stride:7d} {nwin:5d}  {ndef:7d} {hist[2]:6d} "
              f"{hist[3]:6d}   {gt:8d} {gf:8d}"
              + ("   <-- adversarial" if adv else ""))
        if not adv and gt:
            problems.append(
                f"{name} is a MATRIX input and its copy-on-write guard is TRUE "
                f"{gt} time(s). R1 would write through a buffer another record "
                f"owns, so R1 and R1h cannot agree on it and the benign "
                f"invariant stops holding")
        if adv and name not in NO_OPS and not gt:
            problems.append(
                f"{name} is an ADVERSARIAL input and its guard is never TRUE, "
                f"so it exercises nothing this pattern is about -- either the "
                f"generator changed or this census is looking at the wrong "
                f"bytes")
        if not adv and nwin and not gf:
            problems.append(
                f"{name} is a MATRIX input and NEVER EVALUATES the guard. p49's "
                f"benign cost gradient exists because R1h evaluates `rshd[t]` "
                f"on every BREAK; a matrix blob with no BREAK at all makes this "
                f"row p34, whose gradient is 0.00 for a different reason")

    gt_matrix = sum(r["guard_true"] for r in rows if not r["adversarial"])
    gf_matrix = sum(r["guard_false"] for r in rows if not r["adversarial"])
    gt_adv = sum(r["guard_true"] for r in rows if r["adversarial"])
    print(f"\n  guard TRUE  on MATRIX inputs      : {gt_matrix}")
    print(f"  guard FALSE on MATRIX inputs      : {gf_matrix}")
    print(f"  guard TRUE  on ADVERSARIAL inputs : {gt_adv}")

    doc = {"pin": {"regenerate": "python3 patterns/p49-interned-pool/controls/"
                                 "no_share_break.py"},
           "derived_from_sha256": derived_from(),
           "measured_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "rows": rows,
           "guard_true_matrix": gt_matrix,
           "guard_false_matrix": gf_matrix,
           "guard_true_adversarial": gt_adv,
           "problems": problems,
           "invariant": "Every non-adversarial blob evaluates the copy-on-write "
                        "guard at least once and with the answer FALSE every "
                        "time; every adversarial blob except "
                        "adversarial-stride3.bin evaluates it TRUE at least "
                        "once. The first half is what makes R1 and R1h agree on "
                        "every matrix input; the second is what stops the first "
                        "from being vacuous; and the 'at least once' is what "
                        "distinguishes p49's non-zero benign gradient from "
                        "p34's 0.00."}
    out = os.path.join(HERE, "no_share_break.json")
    json.dump(doc, open(out, "w"), indent=2)
    print(f"wrote {out}")
    for p in problems:
        print(f"  *** {p}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
