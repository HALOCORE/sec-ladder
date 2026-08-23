#!/usr/bin/env python3
"""p22: the R2/R3/R4 marginal `Ir` per call over the `sweep-*` band, and the
additivity extrapolation the two structural parameters make available.

`sweep-*` blobs are diagnostic: `check.inputs_of` drops them from
`inputs_checked` and `measure.SKIP_INPUT_PREFIX` drops them from the measurement
matrix, so nothing in `results/p22-hash-probe.json` depends on any of them
(`.memory/05-layout.md`). Adding the band cost one gate re-run.

    python3 patterns/p22-hash-probe/controls/sweep_ir.py            # all bands
    python3 patterns/p22-hash-probe/controls/sweep_ir.py --band k d # fit only

⚠ **WHOLE-PROGRAM marginal, named here** (`.memory/03-measurement.md`: the two
`Ir` conventions can differ by 13x, so say which). Every figure this script
prints is a DIFFERENCE between two rungs on the same input, and the per-process
constant cancels exactly -- verified against the kernel-exclusive column, where
`R2 - R3` and `R3 - R4` on `small.bin`/`large.bin` come out identical to four
decimals.

⚠ **RESIDUE CLASSES.** Band k holds `nd = 24` and varies `nk`; band d holds
`nk = 256` and varies `nd`; both held-constant values are `= 0 (mod 8)`. Band x
draws `(nk, nd)` pairs neither band contains and DELIBERATELY spans `nk mod 8`
in {0, 4, 6} -- because p38's additivity miss was two-thirds a band sitting at
one residue while the third did not, which fits in sample and misses out of it
with no in-sample residual to warn you.
"""

import argparse
import os
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
OUT = os.path.join(REPO, ".temp", "p22", "controls")
assert OUT.endswith(os.path.join("p22", "controls")), OUT
BUILD = os.path.join(REPO, ".temp", "build", "p22")
INPUTS = os.path.join(PDIR, "inputs")
VALGRIND = os.path.expanduser("~/tools/valgrind/bin/valgrind")

CELLS = ["safe_naive", "safe_tuned", "unsafe"]


def probe_input(blob, n_iters):
    os.makedirs(OUT, exist_ok=True)
    out = os.path.join(OUT, f"sw-{n_iters}-{blob}")
    b = open(os.path.join(INPUTS, blob), "rb").read()
    open(out, "wb").write(struct.pack("<Q", n_iters) + b[8:])
    return out


def ir(exe, arg):
    o = os.path.join(OUT, "cgsw.out." + str(os.getpid()))
    r = subprocess.run([VALGRIND, "--tool=callgrind", f"--callgrind-out-file={o}",
                        exe, arg], capture_output=True, text=True, timeout=1800)
    if r.returncode != 0:
        return None
    for line in open(o):
        if line.startswith(("summary:", "totals:")):
            return int(line.split()[1])
    return None


def marginal(exe, blob, lo=100, hi=200):
    a, b = ir(exe, probe_input(blob, lo)), ir(exe, probe_input(blob, hi))
    return None if a is None or b is None else (b - a) / (hi - lo)


def stride_of(blob):
    b = open(os.path.join(INPUTS, blob), "rb").read()
    return struct.unpack("<Q", b[16:24])[0]


sys.path.insert(0, PDIR)
import model as modelmod   # noqa: E402


def keys_walked(blob, lo=100, hi=200):
    """The MEAN number of key bytes the kernel actually walks per call, over
    EXACTLY THE CALLS THE MARGINAL DIFFERENCES -- iterations [lo, hi).

    ⚠ **Not `stride - 4`.** The walk stops at `min(nkey, len - 4)`, `nkey` is a
    per-window header field, and the Lemire window index does not visit windows
    uniformly -- so on a length-heterogeneous blob the regressor is a weighted
    mean and not a maximum. The first version of this script used `stride - 4`
    and reported residuals up to 992 against a law whose residual is actually
    0.00 on 30 of 30 blobs.

    ⚠ **And the call WINDOW matters too.** `marginal()` differences the runs at
    `lo` and `hi` iterations, so the regressor must average over iterations
    [lo, hi) and not over all `n_iters` of them. Averaging over all of them left
    the three length-heterogeneous `sweep-h*` blobs with residuals of +4.22,
    -16.90 and +4.14 -- the only non-zero residuals in the table -- and they go
    to exactly 0.00 with the right window. The Lemire window index does not
    visit windows uniformly, so on a heterogeneous blob the two averages
    differ."""
    m = modelmod.build(os.path.join(INPUTS, blob))
    tot = n = 0
    for i, c in enumerate(m.iter_calls()):
        if not (lo <= i < hi):
            continue
        w = m.buf[c["off"]:c["off"] + c["len"]]
        nkey = int.from_bytes(w[:4], "little")
        tot += min(nkey, c["len"] - 4)
        n += 1
    return tot / n if n else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--band", nargs="*", default=["k", "d", "x", "h"])
    a = ap.parse_args()
    blobs = sorted(f for f in os.listdir(INPUTS)
                   if f.startswith("sweep-") and f.endswith(".bin")
                   and f[6] in a.band)
    exes = {c: os.path.join(BUILD, f"{c}-O3-isolated") for c in CELLS}
    for c, p in exes.items():
        if not os.path.exists(p):
            raise SystemExit(f"sweep_ir.py: {p} missing -- run harness/build.py p22")
    print(f"{'blob':22s} {'nkw':>8s} {'%8':>3s} "
          f"{'R2':>12s} {'R3':>12s} {'R4':>12s} "
          f"{'R2-R3':>10s} {'R3-R4':>8s} {'2*nkw+17':>10s} {'resid':>8s}")
    rows = []
    for b in blobs:
        nk = keys_walked(b)
        m = {c: marginal(exes[c], b) for c in CELLS}
        r2r3 = m["safe_naive"] - m["safe_tuned"]
        r3r4 = m["safe_tuned"] - m["unsafe"]
        pred = 2 * nk + 17
        rows.append((b, nk, r2r3, r3r4, pred))
        print(f"{b:22s} {nk:8.2f} {int(nk) % 8:3d} "
              f"{m['safe_naive']:12.2f} {m['safe_tuned']:12.2f} "
              f"{m['unsafe']:12.2f} {r2r3:10.2f} {r3r4:8.2f} "
              f"{pred:10.2f} {r2r3 - pred:8.2f}")
    flat = {r[3] for r in rows}
    print(f"\nR3 - R4 over {len(rows)} sweep blob(s): distinct values {sorted(flat)}")
    res = [abs(r[2] - r[4]) for r in rows]
    if res:
        print(f"R2 - R3 against `2*nkw + 17`: max |residual| = {max(res):.2f} "
              f"over {len(rows)} blob(s), nkw in "
              f"[{min(r[1] for r in rows):.2f}, {max(r[1] for r in rows):.2f}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
