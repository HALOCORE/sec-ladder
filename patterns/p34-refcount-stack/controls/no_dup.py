#!/usr/bin/env python3
"""p34 CONTROLS: **the census that makes `0.00` a checked property rather than an
argument** -- which of this pattern's shipped blobs contain an executed `DUP` op?

    python3 patterns/p34-refcount-stack/controls/no_dup.py

WHY THIS EXISTS
---------------
p34's headline is that its benign cost gradient across the safety line is `0.00`
BY CONSTRUCTION, and the proof is two lines (`../c/kernel.h`): the retain is the
only increment in the kernel, so in R1 every object's `rc` is permanently 1, and
any executed DUP therefore ends in a use-after-free. The corollary is that **no
input on which R1 and R1h agree can contain a DUP**, and `harness/check.py`
stage 2 requires every non-adversarial cell to agree.

⚠ A structural claim of that shape is exactly the kind this project has been
wrong about before, so it is checked in THREE independent places rather than
assumed once:

  1. `../inputs/gen.py` cannot EMIT a DUP on a matrix blob -- `benign_ops`'s
     alphabet is NEW/POP/READ -- **and re-checks the bytes it wrote anyway**,
     because a filter that cannot fire proves nothing;
  2. `../model.py::no_dup_problems` re-derives the property from the SHIPPED
     blob, and `selfcheck()` runs it once per input on **every gate
     invocation**;
  3. this file, which censuses every `.bin` in `../inputs/` at once and prints
     the op histogram, so a reader can see the answer for the whole directory
     instead of one input at a time.

⚠ It walks the cursor the RUNGS walk -- `nops` operations, two bytes each,
stopping when `len - p < 2` -- so an op the header DECLARES but the window cannot
hold is not counted. A census over raw bytes would over-report and would
therefore be the wrong check.

WHAT IT ASSERTS: every non-`adversarial-` blob has ZERO executed DUPs, and every
`adversarial-` blob except `adversarial-stride3.bin` (whose windows the driver
guard skips entirely) has at least one. **Both directions**, because a census
that only ever says "no DUP here" would pass on an empty directory.
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
import model as m34   # noqa: E402

NAMES = ("NEW", "DUP", "POP", "READ")

#: `adversarial-stride3.bin`'s window is 3 bytes, below the driver's
#: `stride_w >= 4` guard, so the loop is skipped and NO op of any kind executes.
#: It is an adversarial file that legitimately contains no DUP, and saying so
#: here is what stops the "every adversarial blob has one" arm from being a
#: rule with a silent exception.
NO_OPS = ("adversarial-stride3.bin",)


def census(path):
    f = slb.read(path)
    payload = f.payload[: f.declared_len]
    stride, buf = slb.head1_u64_bytes(payload)
    n_blob = len(buf)
    hist = [0, 0, 0, 0]
    nwin = 0
    if m34.HDR <= stride <= n_blob:
        nwin = n_blob // stride
        for w in range(nwin):
            for op in m34.window_ops(buf, w * stride, stride):
                hist[op] += 1
    return stride, n_blob, nwin, hist


def main():
    paths = sorted(glob.glob(os.path.join(PDIR, "inputs", "*.bin")))
    if not paths:
        print("no_dup.py: no .bin files -- run inputs/gen.py first",
              file=sys.stderr)
        return 1
    rows, problems = [], []
    print(f"{'input':32s} {'stride':>7s} {'nwin':>5s}  "
          + "  ".join(f"{n:>6s}" for n in NAMES))
    for p in paths:
        name = os.path.basename(p)
        stride, n_blob, nwin, hist = census(p)
        adv = name.startswith("adversarial-")
        rows.append({"input": name, "stride": stride, "n_blob": n_blob,
                     "nwin": nwin, "ops": dict(zip(NAMES, hist))})
        print(f"{name:32s} {stride:7d} {nwin:5d}  "
              + "  ".join(f"{h:6d}" for h in hist)
              + ("   <-- adversarial" if adv else ""))
        if not adv and hist[m34.DUP]:
            problems.append(
                f"{name} is a MATRIX input and executes {hist[m34.DUP]} DUP "
                f"op(s). R1 would free an object a live stack entry still "
                f"names, so R1 and R1h cannot agree on it and the `0.00` "
                f"benign gradient stops being true by construction")
        if adv and name not in NO_OPS and not hist[m34.DUP]:
            problems.append(
                f"{name} is an ADVERSARIAL input and executes NO DUP, so it "
                f"exercises nothing this pattern is about -- either the "
                f"generator changed or this census is looking at the wrong "
                f"bytes")

    ndup_matrix = sum(r["ops"]["DUP"] for r in rows
                      if not r["input"].startswith("adversarial-"))
    ndup_adv = sum(r["ops"]["DUP"] for r in rows
                   if r["input"].startswith("adversarial-"))
    print(f"\n  executed DUP ops on MATRIX inputs      : {ndup_matrix}")
    print(f"  executed DUP ops on ADVERSARIAL inputs : {ndup_adv}")

    doc = {"pin": {"regenerate": "python3 patterns/p34-refcount-stack/controls/"
                                 "no_dup.py"},
           "derived_from_sha256": {
               rel: hashlib.sha256(open(os.path.join(REPO, rel), "rb").read())
               .hexdigest()
               for rel in ("patterns/p34-refcount-stack/inputs/gen.py",
                           "patterns/p34-refcount-stack/model.py",
                           "patterns/p34-refcount-stack/controls/no_dup.py")},
           "measured_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "rows": rows,
           "dup_ops_matrix": ndup_matrix,
           "dup_ops_adversarial": ndup_adv,
           "problems": problems,
           "invariant": "Every non-adversarial blob executes ZERO DUP ops and "
                        "every adversarial blob except adversarial-stride3.bin "
                        "executes at least one. The first half is what makes "
                        "p34's benign cost gradient 0.00 by construction; the "
                        "second is what stops the first from being vacuous."}
    out = os.path.join(HERE, "no_dup.json")
    json.dump(doc, open(out, "w"), indent=2)
    print(f"wrote {out}")
    for p in problems:
        print(f"  *** {p}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
