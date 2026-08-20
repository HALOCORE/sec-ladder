#!/usr/bin/env python3
"""p14's fitter: turn `sweep_ir.py --json` output into a per-call cost law, and
test it OUT OF SAMPLE by LEAVE-ONE-LENGTH-OUT.

`.memory/03-measurement.md` ("Hold out a LENGTH, not a MIXTURE"): an
out-of-sample test whose held-out points are a random subset of a
length-homogeneous band can be provably unable to fail, because the held-out
regressor vector is a copy of one that stayed in. p14's fit set is
length-heterogeneous by construction -- band M sweeps `llen` 4..60, band X
carries several `llen` inside ONE window -- so the honest hold-out is **every
blob containing a given `llen`**, which removes a whole column of the design.

    python3 patterns/p14-field-split/controls/fit.py sweep.json --cell unsafe
    python3 patterns/p14-field-split/controls/fit.py sweep.json --cell unsafe --diff safe_naive
    python3 patterns/p14-field-split/controls/fit.py sweep.json --cell unsafe --lolo

Regressors, all per CALL (i.e. per window), read back out of the blobs by
`sweep_ir.py::shape`:

    1        the per-call constant (driver dispatch + the two early exits)
    nline    lines walked
    bytes    sum over lines of m = min(llen, SCR)     -- the COPY and the SCAN
    fields   sum over lines of min(ndelim+1, MAXTOK)  -- the FIELD term
    res4     sum over fields of (len % 4)             -- the FOLD's unroll residue
    nz4      fields with (len % 4) != 0               -- its indicator
    res2     sum over fields of (len % 2)
    content  bytes the fold reads                     -- SINGULAR, see below
    scan     the scan loop's trip count               -- SINGULAR, see below
    empties  recorded fields of length zero

⚠ **Two columns are EXACT linear combinations of the others and the design is
singular if they are named.** `scan == bytes + nline` always; and
`content == bytes - fields + nline` whenever no line is truncated at MAXTOK,
which is every blob in p14's sweep. `solve()` detects it and `main()` says so
rather than reporting a large condition number and a meaningless coefficient.

The residue columns exist because the FOLD's inner loop is unrolled, so a field
of length `tj` does not cost `a*tj + b`: p06's `fold(m mod 4)` term, on a second
pattern. **The unroll factor is DERIVED from the residuals and from the listing,
never pinned** -- TASK_024's rule.
"""

import argparse
import json
import os
import sys

REGS = ["const", "nline", "bytes", "fields"]

# `sweep_ir.shape` is re-run over the BLOBS here rather than trusting the
# regressor columns stored in the JSON, so a regressor added after a measurement
# needs no re-measure -- the Ir values are the expensive half and they do not
# move.


def refresh(rows):
    """Recompute every regressor from the blob, so `--regs` can name a column
    the JSON was written before."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import sweep_ir
    for r in rows:
        r.update(sweep_ir.shape(os.path.join(sweep_ir.INPUTS, r["blob"])))
    return rows


def design(rows, cell, regs):
    X, y, tag = [], [], []
    for r in rows:
        v = r["ir"].get(cell)
        if v is None:
            continue
        X.append([1.0 if g == "const" else float(r[g]) for g in regs])
        y.append(float(v))
        tag.append(r["blob"])
    return X, y, tag


def solve(X, y):
    """Least squares by normal equations + Gaussian elimination with partial
    pivoting. Returns (beta, singular)."""
    n, k = len(X), len(X[0])
    A = [[sum(X[i][a] * X[i][b] for i in range(n)) for b in range(k)]
         + [sum(X[i][a] * y[i] for i in range(n))] for a in range(k)]
    for c in range(k):
        p = max(range(c, k), key=lambda r: abs(A[r][c]))
        if abs(A[p][c]) < 1e-9:
            return None, True
        A[c], A[p] = A[p], A[c]
        for r in range(k):
            if r != c:
                f = A[r][c] / A[c][c]
                for q in range(c, k + 1):
                    A[r][q] -= f * A[c][q]
    return [A[i][k] / A[i][i] for i in range(k)], False


def report(name, beta, regs, X, y, tag):
    res = [y[i] - sum(X[i][a] * beta[a] for a in range(len(regs)))
           for i in range(len(y))]
    worst = max(range(len(res)), key=lambda i: abs(res[i])) if res else None
    print(f"  {name}: " + " + ".join(
        f"{beta[a]:.5f}*{regs[a]}" for a in range(len(regs))))
    if worst is not None:
        print(f"    max |residual| {abs(res[worst]):.4f} at {tag[worst]} "
              f"over {len(y)} point(s); rms "
              f"{(sum(r * r for r in res) / len(res)) ** 0.5:.4f}")
    return res


def lengths_of(blob):
    """The `llen` values a blob's name encodes, for the hold-out. Band X blobs
    are heterogeneous and are never held out -- they are what keeps the design
    non-singular when a whole length column is removed."""
    import re
    m = re.match(r"sweep-m(\d+)t\d+\.bin", blob)
    if m:
        return {int(m.group(1))}
    m = re.match(r"sweep-t\d+m(\d+)\.bin", blob)
    if m:
        return {int(m.group(1))}
    m = re.match(r"sweep-l\d+m(\d+)\.bin", blob)
    if m:
        return {int(m.group(1))}
    return set()


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("json")
    ap.add_argument("--cell", default="unsafe")
    ap.add_argument("--diff", help="fit (cell - diff) instead of cell")
    ap.add_argument("--regs", default=",".join(REGS))
    ap.add_argument("--lolo", action="store_true",
                    help="leave-one-LENGTH-out out-of-sample test")
    a = ap.parse_args()
    d = json.load(open(a.json))
    rows = refresh(d["rows"])
    regs = a.regs.split(",")

    if a.diff:
        for r in rows:
            x, z = r["ir"].get(a.cell), r["ir"].get(a.diff)
            r["ir"]["__diff"] = None if (x is None or z is None) else x - z
        cell, label = "__diff", f"{a.cell} - {a.diff}"
    else:
        cell, label = a.cell, a.cell

    X, y, tag = design(rows, cell, regs)
    if len(X) <= len(regs):
        raise SystemExit(f"only {len(X)} usable point(s) for {len(regs)} regressors")
    beta, sing = solve(X, y)
    if sing:
        raise SystemExit("design is singular -- drop a collinear regressor "
                         "(scan == bytes + nline exactly)")
    print(f"IN SAMPLE ({len(X)} points)")
    report(label, beta, regs, X, y, tag)

    if a.lolo:
        allL = sorted({L for r in rows for L in lengths_of(r["blob"])})
        print(f"\nLEAVE-ONE-LENGTH-OUT over llen in {allL}")
        worst = 0.0
        for L in allL:
            keep = [i for i, t in enumerate(tag) if L not in lengths_of(t)]
            held = [i for i, t in enumerate(tag) if L in lengths_of(t)]
            if len(keep) <= len(regs) or not held:
                print(f"  llen={L:3d}: skipped ({len(keep)} kept, {len(held)} held)")
                continue
            b, s = solve([X[i] for i in keep], [y[i] for i in keep])
            if s:
                print(f"  llen={L:3d}: design singular without this length -- "
                      f"THE HOLD-OUT REMOVED A COLUMN, which is the point")
                continue
            errs = [abs(y[i] - sum(X[i][q] * b[q] for q in range(len(regs))))
                    for i in held]
            worst = max(worst, max(errs))
            print(f"  llen={L:3d}: {len(held):2d} held out, max |error| "
                  f"{max(errs):9.4f}")
        print(f"  WORST out-of-sample error over all hold-outs: {worst:.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
