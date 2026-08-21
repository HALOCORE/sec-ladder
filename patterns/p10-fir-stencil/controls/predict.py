#!/usr/bin/env python3
"""p10's REGISTERED out-of-sample predictions for sweep band `e`.

`.memory/03-measurement.md`: *a re-derivable hash is TAMPER-EVIDENCE, not
pre-registration; to make it real, register the hash in a commit that PRECEDES
the measurement commit.* This file is the registration. Running it prints the
predictions and their sha256; the sha256 goes into ../NOTES.md 8a **before**
band `e` is measured, and re-running the script at any later time reproduces it
byte-identically from `inputs/gen.py`'s blobs plus the coefficients below.

    python3 patterns/p10-fir-stencil/controls/predict.py
    python3 patterns/p10-fir-stencil/controls/predict.py --json out.json

**Where the coefficients came from, and what is and is not out of sample.** They
are the exact-rational fit of bands `r` (16 blobs, `nout` fixed at 32) and `o`
(10 blobs, `taps` fixed at 9), computed by `controls/fit.py`, max |residual|
0.0000 in sample and 0.0000 on band `h` as a hold-out. Band `e` moves BOTH
structural parameters at once and to values neither band reaches: `nout` 160..256
against band `r`'s 32 and band `o`'s 8..192, and `taps` 25..49 against band `o`'s
9 and band `r`'s 3..33.

⚠ **STATED PRECISELY, BECAUSE THE PROJECT HAS PUBLISHED A HOLD-OUT THAT COULD
NOT FAIL:** the pooled `r`+`o` design is **rank 4 of 4** in the difference
model, so a band-`e` regressor vector IS a linear combination of rows already
fitted, and this test **cannot fail from linearity alone**. What it can and does
test is a **missing interaction, a missing regime column or a nonlinearity** --
and that failure mode is real on p10 and was observed: the first version of this
model used a per-CALL no-vector indicator (`novec`) instead of the per-OUTPUT one
(`novecout`), fitted bands `r` and `o` at max |resid| 0.0000, and **missed band
`h` by up to 15.6 Ir**. Band `h` is why the model has the column it has. A
prediction that survives band `e` therefore says the two-regime linear model
extrapolates; it does not say the design had a hold-out that was capable of
failing on rank grounds, and this paragraph is here so nobody reads it as
saying that.

⚠ **The leave-one-band-out rank IS non-vacuous here, which is the other half of
the same rule.** The pooled design is rank 4 of 4; dropping band `o` leaves
rank 3 and dropping band `r` leaves rank 2. So **neither band is redundant** --
p18's defect was that one band alone was already full rank, so dropping any
other changed nothing.
"""
import argparse
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import sweep_ir  # noqa: E402

INPUTS = os.path.join(PDIR, "inputs")
BAND_E = ["sweep-e160r20.bin", "sweep-e192r24.bin",
          "sweep-e224r18.bin", "sweep-e256r12.bin"]
N1, N2 = 2000, 6000

# Exact-rational coefficients from controls/fit.py over bands r + o.
# cols = [1, nout, scaltap, novecout] for the DIFFERENCES,
# cols = [1, nout, scaltap, vecit, novecout] for the LEVELS.
DIFFS = {
    "safe_naive-unsafe":     {"1": 65, "nout": 41, "scaltap": 3, "novecout": -7},
    "safe_tuned-unsafe":     {"1": -3, "nout": -5, "scaltap": 0, "novecout": -1},
    "safe_naive-safe_tuned": {"1": 68, "nout": 46, "scaltap": 3, "novecout": -6},
    "c-gcc-h-c-gcc":         {"1": 0, "nout": 0, "scaltap": 0, "novecout": 0},
    "c-clang-h-c-clang":     {"1": 1, "nout": 0, "scaltap": 0, "novecout": 0},
}
LEVELS = {
    "unsafe":     {"1": 71, "nout": 29, "scaltap": 9, "vecit": 17, "novecout": -8},
    "verus":      {"1": 71, "nout": 29, "scaltap": 9, "vecit": 17, "novecout": -8},
    "safe_tuned": {"1": 68, "nout": 24, "scaltap": 9, "vecit": 17, "novecout": -9},
    "safe_naive": {"1": 136, "nout": 70, "scaltap": 12, "vecit": 17, "novecout": -15},
    "c-clang":    {"1": 72, "nout": 30, "scaltap": 7, "vecit": 17, "novecout": -8},
}
# NO c-gcc LEVEL LAW IS REGISTERED, and that is a result rather than an omission:
# gcc vectorises this loop SIXTEEN samples wide and then emits an EIGHT-wide
# half-block before the scalar tail, so it has three regimes where LLVM has two.
# Five designs were tried (LLVM's five columns at vector width 4, 8 and 16, and
# gcc's own `v16/h8/t8` columns with and without a no-vector regime term) and the
# best max |resid| in sample was 45.3. ../NOTES.md 8b. gcc's DIFFERENCE law,
# `c-gcc-h - c-gcc = 0`, is exact on every blob and needs no level law.

TOL = 0.05   # the driver's println! digit-count term; see ../NOTES.md 8a.


def predict():
    out = []
    for b in BAND_E:
        sh = sweep_ir.shape(os.path.join(INPUTS, b), N1, N2)
        row = {"blob": b,
               "regressors": {k: sh[k] for k in
                              ("nout", "taps", "vecit", "scaltap", "novecout")},
               "diff": {}, "level": {}}
        for name, co in DIFFS.items():
            row["diff"][name] = round(
                co["1"] + sum(co[k] * sh[k] for k in co if k != "1"), 6)
        for name, co in LEVELS.items():
            row["level"][name] = round(
                co["1"] + sum(co[k] * sh[k] for k in co if k != "1"), 6)
        out.append(row)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json")
    a = ap.parse_args()
    rows = predict()
    body = json.dumps({"band": "e", "n1": N1, "n2": N2, "tol": TOL,
                       "diffs": DIFFS, "levels": LEVELS, "rows": rows},
                      indent=1, sort_keys=True)
    print(body)
    print("\npredictions sha256:", hashlib.sha256(body.encode()).hexdigest(),
          file=sys.stderr)
    print(f"{len(rows)} blob(s) x "
          f"{len(DIFFS) + len(LEVELS)} quantities = "
          f"{len(rows) * (len(DIFFS) + len(LEVELS))} predictions, "
          f"tolerance +/-{TOL} Ir", file=sys.stderr)
    if a.json:
        open(a.json, "w").write(body)
    return 0


if __name__ == "__main__":
    sys.exit(main())
