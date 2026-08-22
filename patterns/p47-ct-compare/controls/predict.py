#!/usr/bin/env python3
"""p47's ADDITIVITY EXTRAPOLATION -- the only out-of-sample test on this project
that has ever been able to fail (`.memory/03-measurement.md`).

    python3 patterns/p47-ct-compare/controls/predict.py .temp/p47/sweep-iso.json

**The prediction is registered BEFORE the held-out rows are looked at**, in the
sense that it is built from two bands neither of which contains the held-out
configuration:

  band k   `nmatch = 0`, every comparison mismatching at the same `k`, and
           `ncmp = 4`. This band alone gives the per-comparison cost of a
           MISMATCHING comparison as a function of how many 32-byte blocks it
           reads, relative to the cheapest one (`k < 32`).
  band m   `k = 0`, `ncmp = 8`, the number of EQUAL comparisons swept 0..8.
           This band alone gives the cost of an EQUAL comparison.
  band x   `k > 0` AND `nmatch > 0`, `ncmp = 8`. **Neither band contains it.**

The model, and it is a STEP function rather than a line -- which is the whole
reason a linear OLS fit of these rows has a residual of 30-60 `Ir` and this one
has 0:

    Ir(k, nmatch)  =  Ir(band m at the same nmatch)
                      +  (ncmp - nmatch) * [ u(blocks(k)) - u(32) ]

`u(B) - u(32)` is read off band k as `(Ir_k(B) - Ir_k(32)) / 4`, i.e. per
comparison, and is then applied at `ncmp = 8` beside a mixture of equal
comparisons. **Four independent things could have broken it and none did**: a
dependence of the per-comparison cost on `ncmp`, an interaction between equal
and mismatching comparisons, a dependence on the *order* of the two kinds
within a window, and a dependence on `k` beyond the 32-byte block count.

⚠ **`u` is NOT linear in `B`.** Measured per comparison, relative to `u(32)`:
`+7, +14, +19, +40, +43, +46, +46` at `B = 64, 96, 128, 160, 192, 224, 256`.
The `+19 -> +40` step at 128 -> 160 bytes is glibc's own size-class dispatch,
and it is why an attacker learns MORE from some positions than others. A model
that assumed a slope would be wrong by up to 21 `Ir` per comparison.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PD = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PD))
sys.path.insert(0, os.path.join(HERE))


def blocks_of(row):
    """The 32-byte blocks ONE mismatching comparison of this blob reads."""
    nmis = row["ncmp"] - row["neq"]
    return row["kblk_mis"] / nmis if nmis else 0.0


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path")
    ap.add_argument("--cells", default="")
    a = ap.parse_args()
    d = json.load(open(a.path))
    cells = a.cells.split(",") if a.cells else d["cells"]
    rows = {r["blob"]: r for r in d["rows"]}
    kband = sorted((r for b, r in rows.items() if b.startswith("sweep-k")),
                   key=lambda r: r["kblk_mis"])
    mband = {int(b[len("sweep-m"):-4]): r for b, r in rows.items()
             if b.startswith("sweep-m")}
    xband = sorted(b for b in rows if b.startswith("sweep-x"))
    if not kband or not mband or not xband:
        raise SystemExit("predict.py: need bands k, m and x in that file")

    print(f"# p47 additivity extrapolation  [{d['opt']} {d['mode']}, "
          f"whole-program marginal {d['n1']}->{d['n2']}]")
    print(f"# fit bands: k ({len(kband)} blobs, nmatch=0, ncmp="
          f"{kband[0]['ncmp']:.0f}) and m ({len(mband)} blobs, k=0, ncmp="
          f"{list(mband.values())[0]['ncmp']:.0f})")
    print(f"# HELD OUT: band x ({len(xband)} blobs, k>0 AND nmatch>0) -- a "
          f"configuration NEITHER fit band contains")

    # u(B) - u(32), per comparison, straight off band k.
    base = kband[0]
    nmis_k = base["ncmp"] - base["neq"]
    print(f"\n# u(B) - u(32) per comparison, from band k "
          f"(ncmp={base['ncmp']:.0f}):")
    u = {}
    for c in cells:
        tab = {}
        for r in kband:
            B = blocks_of(r)
            tab[B] = (r[c] - base[c]) / nmis_k
        u[c] = tab
    Bs = sorted(u[cells[0]])
    print("  " + "B=".join([""] + [f"{int(B):<8d}" for B in Bs]))
    for c in cells:
        print(f"  {c:12s} " + " ".join(f"{u[c][B]:+8.3f}" for B in Bs))

    print(f"\n# prediction: Ir(k, nmatch) = Ir(band m @ nmatch) "
          f"+ (ncmp - nmatch) * [u(blocks(k)) - u(32)]")
    worst, nbad, ntot = {}, 0, 0
    for c in cells:
        worst[c] = 0.0
    for b in xband:
        r = rows[b]
        nm = int(r["neq"])
        nmis = r["ncmp"] - r["neq"]
        B = blocks_of(r)
        if nm not in mband:
            print(f"  {b}: no band-m row at nmatch={nm}, skipped")
            continue
        for c in cells:
            if B not in u[c]:
                print(f"  {b}: band k has no B={B}, skipped for {c}")
                continue
            pred = mband[nm][c] + nmis * u[c][B]
            resid = r[c] - pred
            ntot += 1
            if abs(resid) > 1e-6:
                nbad += 1
            worst[c] = max(worst[c], abs(resid))
            print(f"  {b:20s} {c:12s} nmis={nmis:.0f} B={int(B):4d} "
                  f"pred={pred:10.3f} meas={r[c]:10.3f} resid={resid:+9.4f}")
    print(f"\n# max|resid| per rung:")
    for c in cells:
        print(f"  {c:12s} {worst[c]:.6f}")
    print(f"# {ntot - nbad} of {ntot} predictions exact to 1e-6; "
          f"{nbad} inexact")
    return 1 if nbad else 0


if __name__ == "__main__":
    sys.exit(main())
