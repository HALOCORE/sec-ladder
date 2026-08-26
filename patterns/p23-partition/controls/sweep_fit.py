#!/usr/bin/env python3
"""p23 control -- RE-FIT the safety-tax law against the shipped sweep bands.

    python3 patterns/p23-partition/inputs/gen.py --sweep
    python3 patterns/p23-partition/controls/sweep_fit.py        # writes sweep_fit.json

`../NOTES.md 9` publishes `R3 - R4` as a two-term law in RECORDS and COPIED
BYTES. Two matrix inputs give two equations and two unknowns, so that fit is
EXACTLY DETERMINED and has no residual to look at -- which is not evidence, it
is arithmetic. `.memory/03-measurement.md` and TASK_101 §4 both say to re-fit
from a committed band before publishing, and p19 is the pattern that shipped a
band and never did.

This script measures per-function exclusive `Ir` for the `kernel` symbol on the
`sweep-m*` (live extent) and `sweep-k*` (PIVOT RANK) bands, at `-O3 isolated`,
and reports:

  * the least-squares fit of `R3 - R4` on (records, copied bytes) over band M,
    with residuals, against the two-point matrix fit;
  * whether the tax depends on the PIVOT RANK at fixed extent -- band K holds
    `m = 32` and `nrec = 8` and sweeps `nlow` 1..31, so a rank-free law predicts
    a flat line and the probe for this row predicted it would not be flat.

⚠ It reads `n_iters` out of each blob rather than assuming it, and divides the
kernel-exclusive count by the call count, so nothing here depends on the loader
or the environment block (`.memory/03-measurement.md` C7).
"""
import glob
import json
import os
import re
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
INPUTS = os.path.join(PDIR, "inputs")
BUILD = os.path.join(REPO, ".temp", "build", "p23")
OUT = os.path.join(REPO, ".temp", "t101", "cgsweep")
VALGRIND = os.path.expanduser("~/tools/valgrind/bin/valgrind")
CG_ANNOTATE = os.path.expanduser("~/tools/valgrind/bin/callgrind_annotate")
CELLS = ("safe_naive", "safe_tuned", "unsafe", "verus", "c-gcc-h", "c-gcc")


def n_iters(path):
    with open(path, "rb") as f:
        return struct.unpack("<Q", f.read(8))[0]


def kernel_ir(binary, blob, tag):
    os.makedirs(OUT, exist_ok=True)
    out = os.path.join(OUT, f"cg.{tag}.out")
    r = subprocess.run([VALGRIND, "--tool=callgrind",
                        f"--callgrind-out-file={out}", binary, blob],
                       capture_output=True, text=True, timeout=3600)
    if r.returncode != 0:
        return None
    ann = subprocess.run([CG_ANNOTATE, "--threshold=100", out],
                         capture_output=True, text=True, timeout=3600).stdout
    tot = 0
    seen = False
    for line in ann.splitlines():
        if ":kernel" not in line and not line.rstrip().endswith("kernel"):
            continue
        m = re.match(r"\s*([\d,]+)\s", line)
        if m:
            tot += int(m.group(1).replace(",", ""))
            seen = True
    os.remove(out)
    return tot if seen else None


def lsq(rows, key):
    """least squares of `tax = a*records + b*bytes` over `rows`."""
    sxx = sum(r["nrec"] ** 2 for r in rows)
    syy = sum(r["mbytes"] ** 2 for r in rows)
    sxy = sum(r["nrec"] * r["mbytes"] for r in rows)
    sxz = sum(r["nrec"] * r[key] for r in rows)
    syz = sum(r["mbytes"] * r[key] for r in rows)
    det = sxx * syy - sxy * sxy
    if det == 0:
        return None, None
    return (sxz * syy - syz * sxy) / det, (syz * sxx - sxz * sxy) / det


def main():
    want_m = [2, 4, 8, 16, 24, 32, 40, 48]
    want_k = [1, 4, 8, 16, 24, 28, 31]
    files = []
    for m in want_m:
        p = os.path.join(INPUTS, f"sweep-m{m:02d}n08.bin")
        if os.path.exists(p):
            files.append(("M", p, 8, m, m // 2))
    for lo in want_k:
        p = os.path.join(INPUTS, f"sweep-k{lo:02d}m32.bin")
        if os.path.exists(p):
            files.append(("K", p, 8, 32, lo))
    if not files:
        print("no sweep blobs; run inputs/gen.py --sweep first", file=sys.stderr)
        return 1
    recs = []
    for band, path, nrec, m, nlow in files:
        it = n_iters(path)
        row = {"band": band, "input": os.path.basename(path), "nrec": nrec,
               "m": m, "nlow": nlow, "rank": nlow / m, "mbytes": nrec * m,
               "n_iters": it}
        for cell in CELLS:
            b = os.path.join(BUILD, f"{cell}-O3-isolated")
            if not os.path.exists(b):
                continue
            ir = kernel_ir(b, path, f"{cell}.{os.path.basename(path)}")
            row[cell] = None if ir is None else ir / it
        if row.get("safe_tuned") and row.get("unsafe"):
            row["r3_r4"] = row["safe_tuned"] - row["unsafe"]
            row["r2_r4"] = row["safe_naive"] - row["unsafe"]
        recs.append(row)
        print("  %-22s nrec=%d m=%-2d rank=%.2f  R2=%9.2f R3=%9.2f R4=%9.2f  "
              "R3-R4=%8.2f" % (row["input"], nrec, m, row["rank"],
                               row.get("safe_naive") or 0,
                               row.get("safe_tuned") or 0,
                               row.get("unsafe") or 0, row.get("r3_r4") or 0))
    band_m = [r for r in recs if r["band"] == "M" and "r3_r4" in r]
    band_k = [r for r in recs if r["band"] == "K" and "r3_r4" in r]
    res = {"rows": recs}
    if band_m:
        a, b = lsq(band_m, "r3_r4")
        a2, b2 = lsq(band_m, "r2_r4")
        res["fit_band_M"] = {"r3_r4": {"per_record": a, "per_byte": b},
                             "r2_r4": {"per_record": a2, "per_byte": b2}}
        print(f"\nBAND M least squares  R3-R4 = {a:.3f}/record + {b:.4f}/byte")
        print(f"                      R2-R4 = {a2:.3f}/record + {b2:.4f}/byte")
        print("  residuals (R3-R4):")
        for r in band_m:
            pred = a * r["nrec"] + b * r["mbytes"]
            print("    m=%-3d obs=%8.2f pred=%8.2f resid=%+8.2f"
                  % (r["m"], r["r3_r4"], pred, r["r3_r4"] - pred))
    if band_k:
        vals = [r["r3_r4"] for r in band_k]
        res["band_K_r3_r4"] = {r["nlow"]: r["r3_r4"] for r in band_k}
        print(f"\nBAND K (m=32, nrec=8, rank swept): R3-R4 "
              f"min={min(vals):.2f} max={max(vals):.2f} spread={max(vals)-min(vals):.2f}")
        for r in band_k:
            print("    nlow=%-3d rank=%.2f  R2=%8.2f R3=%8.2f R4=%8.2f  R3-R4=%7.2f  R2-R4=%7.2f"
                  % (r["nlow"], r["rank"], r["safe_naive"], r["safe_tuned"],
                     r["unsafe"], r["r3_r4"], r["r2_r4"]))
    with open(os.path.join(HERE, "sweep_fit.json"), "w") as f:
        json.dump(res, f, indent=1)
    print("\nwrote", os.path.join(HERE, "sweep_fit.json"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
