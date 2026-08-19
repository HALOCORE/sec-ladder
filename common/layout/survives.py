#!/usr/bin/env python3
"""How much of a pattern's PUBLISHED `ns` gap survives a layout population?

Compares `results/<pattern>.json`'s single-layout O3/isolated wall-clock minima
with the same rung-to-rung comparison recomputed over the population, four
ways:

  pooled          median over all layouts
  mode0 / mode16  mode-matched by kernel-entry residue `addr % 32`
  P(A>B)          pairwise, over all N*N layout pairs -- a genuine proportion,
                  and flat in N (`.memory/03-measurement.md`)

⚠ `addr % 32` is the PROXY.  It coincides with the mechanism only because every
kernel here is 16-byte aligned; `analyze.py` / `loopfit.py` report the
`win32`/`jcc32` partition that actually explains the modes, and a mode-matched
number should be quoted only when the two agree.

⚠ DOMINANCE ("slower than the worst layout of B") is deliberately NOT reported.
It is defined against an extremum of B, does not converge, and its spread is
+-26 points at N=4 (TASK_030_REVIEW major 3).

    python3 common/layout/survives.py --dir .temp/layout p01 p07
"""
import argparse
import json
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import loopfit  # noqa: E402

MAP = {"p01": "p01-array-sum", "p02": "p02-buffer-copy",
       "p05": "p05-index-flatten", "p05b": "p05-index-flatten",
       "p07": "p07-binary-search", "p08": "p08-overlap-move",
       "p16": "p16-tlv-walk", "p17": "p17-http-range"}


def published(pattern, cell, stem):
    d = json.load(open(os.path.join(REPO, "results", pattern + ".json")))
    for c in d["cells"]:
        if (c["cell"], c["opt"], c["mode"]) == (cell, "O3", "isolated"):
            return 1e3 * c["wall"][stem + ".bin"]["min_s"]
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tags", nargs="*",
                    default=["p01", "p02", "p05", "p07", "p08", "p16", "p17"])
    ap.add_argument("--dir", default=os.path.join(REPO, ".temp", "layout"))
    ap.add_argument("--ref", default="unsafe")
    ap.add_argument("--floor", type=float, default=1.0,
                    help="run-to-run floor in %%; a sign flip below it is not "
                         "a sign flip")
    a = ap.parse_args()
    print(f"{'pattern':6s} {'in':5s} {'rung':11s} {'published':>10s} "
          f"{'pooled':>8s} {'mode0':>8s} {'mode16':>8s} {'P(A>B)':>7s}  verdict")
    for tag in a.tags:
        path = os.path.join(a.dir, f"layout_{tag}.json")
        if not os.path.exists(path):
            continue
        rows = loopfit.load(path)
        pat = MAP[tag]
        for stem in loopfit.stems(rows):
            if "#" in stem:          # extra passes: the first pass is primary
                continue
            ref = rows[a.ref]
            refv = [r[stem] for r in ref]
            for cell in [c for c in rows if c != a.ref]:
                cv = [r[stem] for r in rows[cell]]
                pub_c, pub_r = published(pat, cell, stem), \
                    published(pat, a.ref, stem)
                pub = 100 * (pub_c - pub_r) / pub_r
                pooled = 100 * (statistics.median(cv) - statistics.median(refv)) \
                    / statistics.median(refv)
                mm = []
                for res in (0, 16):
                    x = [r[stem] for r in rows[cell] if r["addr"] % 32 == res]
                    y = [r[stem] for r in ref if r["addr"] % 32 == res]
                    mm.append(100 * (statistics.median(x) - statistics.median(y))
                              / statistics.median(y) if x and y else float("nan"))
                pw = 100.0 * sum(1 for x in cv for y in refv if x > y) \
                    / (len(cv) * len(refv))
                big = max(abs(mm[0]), abs(mm[1]))
                if mm[0] * mm[1] < 0 and big > a.floor:
                    flip = "SIGN FLIPS"
                elif big <= a.floor:
                    flip = f"gap < {a.floor:g}% either way"
                elif pw >= 95 or pw <= 5:
                    flip = "survives"
                else:
                    flip = f"no clean sign (P(A>B) {pw:.0f}%)"
                print(f"{tag:6s} {stem:5s} {cell:11s} {pub:+9.2f}% "
                      f"{pooled:+7.2f}% {mm[0]:+7.2f}% {mm[1]:+7.2f}% "
                      f"{pw:6.1f}%  {flip}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
