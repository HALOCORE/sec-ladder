#!/usr/bin/env python3
"""p25 CONTROLS: **census every blob in `inputs/` for the stale-read property.**

    python3 patterns/p25-realloc-growth/controls/no_stale.py

`../model.py::stale_free_problems` checks the input the GATE was handed, once per
gate invocation. This checks **the whole directory**, including the `sweep-*`
bands that `harness/check.py::inputs_of` drops and that no gate stage ever sees
-- and the sweep bands are exactly where a generator change would put a stale
window without anything noticing, because `NOTES.md`'s swept laws are measured on
them.

The property, from `../c/kernel.h`:

> **No NON-adversarial window may read through an interior pointer whose token
> vector has been reallocated since the SAVE.**

ASan's allocator moves on every `realloc`, so such a window makes R1 report
`heap-use-after-free` on a row whose `sanitizer_expect` is `clean`; and
`harness/check.py` stage 2 requires every non-adversarial cell to agree with
`../model.py` and with every other cell, which a rung reading retired storage
cannot do reproducibly.

⚠ **THE SPLIT IS PART OF THE MEASUREMENT, NOT AN EXEMPTION.** An `adversarial-*`
blob is allowed to go stale and is *expected* to -- except `adversarial-nogrow`,
which is the negative control among them and must be clean. This control prints
the per-file verdict for all three classes, so *"the adversarial rows fire"* is
readable as a measurement rather than as a property of the filename.

⚠ It imports `../model.py` deliberately rather than re-implementing the walk: the
question here is coverage (which FILES), not semantics (what STALE means), and a
second implementation of the semantics would be a second thing to keep in step.
`../inputs/gen.py` already carries the independent implementation that the
generator validates against, so the property has two implementations in the tree
and this file is not the place for a third.
"""

import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
INDIR = os.path.join(PDIR, "inputs")

sys.path.insert(0, PDIR)
sys.path.insert(0, os.path.join(REPO, "common"))
import model as m25  # noqa: E402
import slb  # noqa: E402

# The one `adversarial-*` file that must NOT go stale. It is the control that
# stops this census from being satisfied by the filename convention alone.
ADV_CLEAN = ("adversarial-nogrow.bin", "adversarial-stride3.bin")


def derived_from():
    out = {}
    for rel in ("patterns/p25-realloc-growth/model.py",
                "patterns/p25-realloc-growth/inputs/gen.py",
                "patterns/p25-realloc-growth/controls/no_stale.py"):
        p = os.path.join(REPO, rel)
        out[rel] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return out


def census(path):
    """`(nwin, stale_windows)` for one blob, from the SHIPPED bytes."""
    f = slb.read(path)
    payload = f.payload[: f.declared_len]
    stride, buf = slb.head1_u64_bytes(payload)
    n_blob = len(buf)
    if not (m25.HDR <= stride <= n_blob):
        return 0, []
    nwin = n_blob // stride
    stale = [w for w in range(nwin)
             if m25.window_stale(buf, w * stride, stride)]
    return nwin, stale


def main():
    files = sorted(f for f in os.listdir(INDIR) if f.endswith(".bin"))
    if not files:
        print("no_stale.py: inputs/ has no .bin files -- run inputs/gen.py",
              file=sys.stderr)
        return 1
    rows, problems = [], []
    n_matrix = n_sweep = 0
    for f in files:
        adv = f.startswith("adversarial-")
        sweep = f.startswith("sweep-")
        nwin, stale = census(os.path.join(INDIR, f))
        must_be_clean = (not adv) or f in ADV_CLEAN
        rows.append({"file": f, "windows": nwin, "stale_windows": stale,
                     "class": "adversarial" if adv else
                              ("sweep" if sweep else "matrix"),
                     "must_be_clean": must_be_clean})
        if sweep:
            n_sweep += 1
        else:
            n_matrix += 1
        if must_be_clean and stale:
            problems.append(
                f"{f}: window(s) {stale} read through an interior pointer whose "
                f"token vector was reallocated after the SAVE, and this file "
                f"must be clean"
                + (" (it is the negative control among the adversarial rows)"
                   if adv else ""))
        if adv and f not in ADV_CLEAN and not stale:
            problems.append(
                f"{f}: an adversarial file with NO stale window. The row it is "
                f"supposed to exercise is not exercised, and its "
                f"`sanitizer_expect` would derive `clean` -- which is silence "
                f"where the bug should be")
        print(f"  {f:32s} {'ADV' if adv else ('SWP' if sweep else 'MTX')} "
              f"windows={nwin:<5d} stale={stale if stale else '[]'}")

    print(f"\n  {n_matrix} matrix/adversarial file(s), {n_sweep} sweep band(s), "
          f"{len(problems)} problem(s)")
    if n_sweep == 0:
        print("  NOTE: no sweep bands present. Run "
              "`python3 patterns/p25-realloc-growth/inputs/gen.py --sweep` to "
              "census them too -- this run certifies the matrix only.")

    doc = {"pin": {"regenerate": "python3 patterns/p25-realloc-growth/controls/"
                                 "no_stale.py"},
           "derived_from_sha256": derived_from(),
           "measured_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "files": rows,
           "n_matrix_files": n_matrix,
           "n_sweep_files": n_sweep,
           "problems": problems,
           "invariant": "No non-adversarial window, and no window of "
                        "adversarial-nogrow or adversarial-stride3, reads "
                        "through an interior pointer whose token vector was "
                        "reallocated after the SAVE; and every OTHER "
                        "adversarial file has at least one window that does. "
                        "The blobs are gitignored, so the hashes pinned above "
                        "are the GENERATOR and the model, not the .bin files."}
    out = os.path.join(HERE, "no_stale.json")
    json.dump(doc, open(out, "w"), indent=2)
    print(f"wrote {out}")
    for p in problems:
        print(f"  *** {p}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
