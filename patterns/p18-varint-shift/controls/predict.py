#!/usr/bin/env python3
"""Pre-register p18's extrapolation predictions, then score them.

`.memory/03-measurement.md`: *"an exact fit plus genuine out-of-sample
predictions is honest evidence; the hold-out is not."* p18's pooled design is
three columns wide (`bytes`, `nv`, `1`), so any three independent rows determine
it and **no leave-one-band-out over b/v/x can fail** -- measured, `../NOTES.md`
8. Band Y exists to replace that with something falsifiable: its shapes sit
outside the convex hull of b/v/x in BOTH regressors.

    # 1. fit on b/v/x and WRITE THE PREDICTIONS DOWN, hashed
    python3 patterns/p18-varint-shift/controls/predict.py register \
        .temp/p18/sweep_all_O3.json -o .temp/p18/predict_y.json

    # 2. only then measure band Y
    python3 patterns/p18-varint-shift/controls/sweep_ir.py --band y --cells all \
        --json .temp/p18/sweep_y_O3.json

    # 3. score
    python3 patterns/p18-varint-shift/controls/predict.py score \
        .temp/p18/predict_y.json .temp/p18/sweep_y_O3.json

`register` prints the SHA-256 of the prediction file it wrote; `score` re-hashes
it and refuses to run if it has changed, which is the whole mechanism -- a
prediction that can be edited after the measurement is not a prediction.
"""

import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fit as fitmod  # noqa: E402


def load_rows(path, prefix="sweep-"):
    d = json.load(open(path))
    return [r for r in d["rows"] if r["blob"].startswith(prefix)], d["cells"]


def register(a):
    rows, cells = load_rows(a.json)
    rows = [r for r in rows if fitmod.band_of(r["blob"]) in ("b", "v", "x")]
    if not rows:
        raise SystemExit("no b/v/x rows in the fit json")
    X = [fitmod.row_vec(r) for r in rows]
    out = {"fit_json": os.path.basename(a.json), "n_fit_rows": len(rows),
           "fit_bands": sorted({fitmod.band_of(r["blob"]) for r in rows}),
           "fit_rank": fitmod.rank(X),
           "fit_bytes_range": [min(r["bytes"] for r in rows),
                               max(r["bytes"] for r in rows)],
           "fit_nv_range": [min(r["nv"] for r in rows),
                            max(r["nv"] for r in rows)],
           "coeffs": {}, "predictions": {}}
    for c in cells:
        ys = [F(r["ir"][c]).limit_denominator(10 ** 6) for r in rows]
        s = fitmod.solve_ls(X, ys)
        if s is None:
            continue
        out["coeffs"][c] = [float(x) for x in s]
        for tag, (b, n) in a.shapes.items():
            pred = float(s[0] * b + s[1] * n + s[2])
            out["predictions"].setdefault(tag, {})["bytes"] = b
            out["predictions"][tag]["nv"] = n
            out["predictions"][tag].setdefault("ir", {})[c] = pred
    txt = json.dumps(out, indent=1, sort_keys=True)
    open(a.out, "w").write(txt)
    h = hashlib.sha256(txt.encode()).hexdigest()
    print(f"  wrote {a.out}")
    print(f"  fit: {out['n_fit_rows']} rows, bands {out['fit_bands']}, "
          f"rank {out['fit_rank']}, bytes {out['fit_bytes_range']}, "
          f"nv {out['fit_nv_range']}")
    for tag, p in sorted(out["predictions"].items()):
        print(f"  predict {tag}: bytes={p['bytes']} nv={p['nv']}  " +
              "  ".join(f"{c}={v:.2f}" for c, v in sorted(p["ir"].items())))
    print(f"  sha256 {h}")
    return 0


def score(a):
    txt = open(a.pred).read()
    h = hashlib.sha256(txt.encode()).hexdigest()
    print(f"  prediction file sha256 {h}")
    pred = json.loads(txt)
    rows, cells = load_rows(a.measured)
    ok = bad = 0
    print(f"  {'blob':10s} {'cell':14s} {'predicted':>12s} {'measured':>12s} "
          f"{'error':>10s}")
    worst = {}
    for r in rows:
        tag = r["blob"].replace("sweep-", "").replace(".bin", "")
        if tag not in pred["predictions"]:
            continue
        p = pred["predictions"][tag]
        assert p["bytes"] == r["bytes"] and p["nv"] == r["nv"], \
            f"{tag}: registered shape {p['bytes']},{p['nv']} != " \
            f"measured {r['bytes']},{r['nv']}"
        for c, v in sorted(p["ir"].items()):
            m = r["ir"].get(c)
            if m is None:
                continue
            e = m - v
            worst[c] = max(worst.get(c, 0.0), abs(e))
            print(f"  {tag:10s} {c:14s} {v:12.2f} {m:12.2f} {e:10.4f}")
            ok += 1
    print()
    for c, e in sorted(worst.items()):
        print(f"  worst |error| {c:14s} {e:.4f}")
    print(f"  {ok} prediction(s) scored")
    return 0 if not bad else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("register")
    r.add_argument("json")
    r.add_argument("-o", "--out", required=True)
    s = sub.add_parser("score")
    s.add_argument("pred")
    s.add_argument("measured")
    a = ap.parse_args()
    # The shapes of band Y, transcribed from inputs/gen.py's SWEEP_Y_SHAPES so
    # that `register` never has to read a blob that does not exist yet.
    a.shapes = {"y16": (160, 16), "y40": (220, 40), "y64": (320, 64)}
    return register(a) if a.cmd == "register" else score(a)


if __name__ == "__main__":
    sys.exit(main())
