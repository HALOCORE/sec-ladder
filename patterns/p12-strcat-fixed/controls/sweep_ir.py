#!/usr/bin/env python3
"""p12's sweep: whole-program marginal Ir per call over both bands.

    python3 patterns/p12-strcat-fixed/controls/sweep_ir.py            # both bands
    python3 patterns/p12-strcat-fixed/controls/sweep_ir.py --band n   # one band
    python3 patterns/p12-strcat-fixed/controls/sweep_ir.py --fit      # fit only

`.memory/03-measurement.md`: the whole-program `summary:` line is a LEVEL that
moves with the environment block and does not reproduce across shells, but its
DIFFERENCE between two runs of the same binary in the same shell is exact,
because every loader and environment term cancels. So this measures

    marginal Ir per call = (Ir at n_iters=hi - Ir at n_iters=lo) / (hi - lo)

exactly as `harness/check.py`'s stage 3b does, with `n_iters` rewritten in place
at offset 0 of the input file (a format-level operation -- see
`.memory/02-bench-rules.md`).

**Why the whole-program column and not `kernel_exclusive_ir`**: six of p12's
seven cells make a bulk-memory call (`memcpy`, `memchr`), and kernel-exclusive Ir
silently drops the work that leaves the symbol. `.memory/03-measurement.md`:
*"Quote the marginal column for any pattern whose kernel contains a bulk-memory
call, and say which column you are quoting either way."*

**Band N is the string-count axis and every string is accepted**, so its
regressors are `(1, K, 5K, 4K)` and it is **rank 2 on its own**. **Band A is the
acceptance-ratio axis**: 24 strings of length `L`, of which `min(24, 128/L)` fit,
so scanned bytes rise linearly while copied bytes saturate -- which is what
breaks the collinearity. R1 (`c-gcc`, `c-clang`) is **not measurable on band A**
for `L >= 6`: it would copy `24*L` bytes into a 128-byte destination and either
abort on the canary or segfault. Those cells are recorded as `crash` rather than
skipped silently.
"""
import argparse
import json
import os
import re
import struct
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(REPO, "harness"))
sys.path.insert(0, os.path.join(REPO, "common"))
import build as buildmod  # noqa: E402

PDIR = os.path.join(REPO, "patterns", "p12-strcat-fixed")
INPUTS = os.path.join(PDIR, "inputs")
SCRATCH = os.path.join(REPO, ".temp", "p12", f"sweep.{os.getpid()}")
VALGRIND = os.path.expanduser("~/tools/valgrind/bin/valgrind")
OUT = os.path.join(REPO, ".temp", "p12", "sweep_ir.json")

CELLS = ["c-gcc", "c-gcc-h", "c-clang", "c-clang-h", "safe_naive", "safe_tuned",
         "unsafe", "verus"]
LO, HI = 100, 200
DST_CAP = 128


def probe(src, n_iters, out):
    blob = open(src, "rb").read()
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "wb") as f:
        f.write(struct.pack("<Q", n_iters) + blob[8:])
    return out


def total_ir(binary, arg, outfile):
    r = subprocess.run([VALGRIND, "--tool=callgrind",
                        f"--callgrind-out-file={outfile}", binary, arg],
                       capture_output=True, text=True, timeout=900)
    if r.returncode != 0:
        return None
    for line in open(outfile):
        if line.startswith(("summary:", "totals:")):
            return int(line.split()[1])
    return None


def regressors(band, k, ln):
    """(K, xscan, xdst, xrej, nacc) for one sweep blob, from the shape alone.

    K       strings walked (all are terminated and the count is honest)
    xscan   bytes the scan examines: `slen + 1` per string (the terminator is
            examined and is not copied)
    xdst    bytes copied, which is also bytes folded -- the two are equal BY
            CONSTRUCTION and no input can separate them (see `fit`)
    xrej    bytes scanned but not copied, i.e. the reject path's width. It is
            `xscan - K - xdst`, i.e. LINEARLY DEPENDENT on the others, and is
            recorded for reading rather than for fitting.
    nacc    strings ACCEPTED. On band N it equals K; on band A it saturates.
            This is the regressor `small`/`large` cannot separate from K,
            because they accept everything -- see ../NOTES.md 1.
    """
    acc = min(k, DST_CAP // ln) if ln else k
    xdst = ln * acc
    return k, k * (ln + 1), xdst, k * ln - xdst, acc


def blobs(band):
    out = []
    for f in sorted(os.listdir(INPUTS)):
        m = re.match(rf"sweep-{band}(\d+)L(\d+)\.bin$", f)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            k, ln = (a, b) if band == "n" else (a, b)
            out.append((f, k, ln))
    return out


def measure(bands, cells):
    rows = []
    for band in bands:
        for f, k, ln in blobs(band):
            src = os.path.join(INPUTS, f)
            lo = probe(src, LO, os.path.join(SCRATCH, f"{f}.{LO}.bin"))
            hi = probe(src, HI, os.path.join(SCRATCH, f"{f}.{HI}.bin"))
            K, xscan, xdst, xrej, nacc = regressors(band, k, ln)
            row = {"band": band, "blob": f, "k": k, "len": ln, "K": K,
                   "xscan": xscan, "xdst": xdst, "xrej": xrej, "nacc": nacc,
                   "ir": {}}
            for c in cells:
                b = os.path.join(REPO, ".temp", "build", "p12",
                                 f"{c}-O3-isolated")
                if not os.path.exists(b):
                    continue
                a = total_ir(b, lo, os.path.join(SCRATCH, "cg.lo"))
                z = total_ir(b, hi, os.path.join(SCRATCH, "cg.hi"))
                row["ir"][c] = ("crash" if (a is None or z is None)
                                else (z - a) / (HI - LO))
            rows.append(row)
            print(f"  {f:20s} K={K:3d} xscan={xscan:5d} xdst={xdst:4d} "
                  f"xrej={xrej:5d}  " +
                  " ".join(f"{c.split('-')[-1][:5]}={row['ir'].get(c)}"
                           for c in cells if c in row["ir"]), flush=True)
    return rows


def lstsq(A, y):
    """Least squares by normal equations, plus the rank of A (Gaussian
    elimination with partial pivoting). No numpy on this box."""
    n, m = len(A), len(A[0])
    ata = [[sum(A[i][a] * A[i][b] for i in range(n)) for b in range(m)]
           for a in range(m)]
    aty = [sum(A[i][a] * y[i] for i in range(n)) for a in range(m)]
    # rank of A
    M = [row[:] for row in A]
    rank, r = 0, 0
    for c in range(m):
        piv = max(range(r, n), key=lambda i: abs(M[i][c]), default=None)
        if piv is None or abs(M[piv][c]) < 1e-9:
            continue
        M[r], M[piv] = M[piv], M[r]
        for i in range(r + 1, n):
            f = M[i][c] / M[r][c]
            for j in range(c, m):
                M[i][j] -= f * M[r][j]
        r += 1
        rank += 1
        if r == n:
            break
    # solve
    aug = [ata[i][:] + [aty[i]] for i in range(m)]
    for c in range(m):
        piv = max(range(c, m), key=lambda i: abs(aug[i][c]))
        if abs(aug[piv][c]) < 1e-12:
            return None, rank
        aug[c], aug[piv] = aug[piv], aug[c]
        for i in range(m):
            if i == c:
                continue
            f = aug[i][c] / aug[c][c]
            for j in range(c, m + 1):
                aug[i][j] -= f * aug[c][j]
    return [aug[i][m] / aug[i][i] for i in range(m)], rank


def fit(rows, cells):
    """Fit `a + b*K + c*xscan + d*xdst` per cell and per difference, and report
    the RANK of the design so a rank-deficient band cannot masquerade as a law."""
    print("\n-- design rank (regressors: 1, K, nacc, xscan, xdst) --")
    for tag, sel in (("band n only", lambda r: r["band"] == "n"),
                     ("band a only", lambda r: r["band"] == "a"),
                     ("pooled", lambda r: True)):
        R = [r for r in rows if sel(r)]
        _, rank = lstsq(design(R), [0.0] * len(R))
        print(f"   {tag:12s} n={len(R):3d}  rank {rank}/{NREG}")
    print("\n-- fits (a + b*K + c*nacc + d*xscan + e*xdst), max |residual| --")
    series = [(c, lambda r, c=c: r["ir"].get(c) if usable(r["ir"].get(c)) else None)
              for c in cells]
    series += [("R1h-R1 gcc", lambda r: _d(r, "c-gcc-h", "c-gcc")),
               ("R1h-R1 clang", lambda r: _d(r, "c-clang-h", "c-clang")),
               ("R2-R4", lambda r: _d(r, "safe_naive", "unsafe")),
               ("R3-R4", lambda r: _d(r, "safe_tuned", "unsafe")),
               ("R5-R4", lambda r: _d(r, "verus", "unsafe"))]
    for name, get in series:
        R = [r for r in rows if isinstance(get(r), (int, float))]
        if len(R) < 6:
            print(f"   {name:14s} only {len(R)} usable point(s) -- skipped")
            continue
        A = design(R)
        y = [get(r) for r in R]
        beta, rank = lstsq(A, y)
        if beta is None:
            print(f"   {name:14s} n={len(R):3d} rank={rank} SINGULAR "
                  f"(rank-deficient design -- no fit is reportable)")
            continue
        res = max(abs(y[i] - sum(A[i][j] * beta[j] for j in range(NREG)))
                  for i in range(len(R)))
        print(f"   {name:14s} n={len(R):3d} rank={rank} "
              f"a={beta[0]:9.4f} K={beta[1]:8.5f} nacc={beta[2]:8.5f} "
              f"xscan={beta[3]:8.5f} xdst={beta[4]:8.5f}  maxres={res:8.4f}")


NREG = 5


def design(R):
    return [[1.0, r["K"], nacc_of(r), r["xscan"], r["xdst"]] for r in R]


def nacc_of(r):
    """Recomputed rather than read, so an older saved record still fits."""
    return r.get("nacc", min(r["K"], DST_CAP // r["len"]) if r["len"] else r["K"])


def usable(v):
    """A marginal of exactly 0 is NOT a datum. On `sweep-a24L06/L07` the R1
    cells built by clang overflow +16..+48 bytes, which lands in the DRIVER's
    frame: the same binary prints the identical checksum for n_iters 1, 2, 4, 8,
    100, 200 and 1000, so the loop no longer depends on `n_iters` at all and the
    two-point marginal is 0 by construction. ../NOTES.md 7."""
    return isinstance(v, (int, float)) and v > 0.5


def _d(r, a, b):
    """A DIFFERENCE may legitimately be negative or zero -- `R5 - R4` is exactly
    -1 and `R1h - R1` under gcc is negative -- so `usable` is applied to the two
    LEVELS and never to the difference."""
    x, y = r["ir"].get(a), r["ir"].get(b)
    if usable(x) and usable(y):
        return x - y
    return None


def fit_bandn(rows, cells):
    """Band N alone, regressors `(1, K)`.

    Band N holds the string length at 4, so every `memcpy` call the copy lowers
    to is a 4-byte call and the routine's SIZE DISPATCH is held fixed. That is
    what makes an exact law possible here and not on band A, where the string
    length walks 1..24 and glibc's `memcpy` changes code path with it -- a
    per-copied-byte rate on band A is a step function wearing a constant's
    clothes (`.memory/03-measurement.md`: name the routine beside every rate)."""
    print("\n-- band N only (L = 4 held fixed), a + b*K, max |residual| --")
    series = [(c, lambda r, c=c: r["ir"].get(c) if usable(r["ir"].get(c)) else None)
              for c in cells]
    series += [("R1h-R1 gcc", lambda r: _d(r, "c-gcc-h", "c-gcc")),
               ("R1h-R1 clang", lambda r: _d(r, "c-clang-h", "c-clang")),
               ("R2-R4", lambda r: _d(r, "safe_naive", "unsafe")),
               ("R3-R4", lambda r: _d(r, "safe_tuned", "unsafe")),
               ("R2-R3", lambda r: _d(r, "safe_naive", "safe_tuned")),
               ("R5-R4", lambda r: _d(r, "verus", "unsafe"))]
    for name, get in series:
        R = [r for r in rows
             if r["band"] == "n" and isinstance(get(r), (int, float))]
        if len(R) < 4:
            print(f"   {name:14s} only {len(R)} usable point(s) -- skipped")
            continue
        A = [[1.0, r["K"]] for r in R]
        y = [get(r) for r in R]
        beta, rank = lstsq(A, y)
        res = max(abs(y[i] - beta[0] - beta[1] * A[i][1]) for i in range(len(R)))
        print(f"   {name:14s} n={len(R):3d} rank={rank}/2 "
              f"a={beta[0]:10.4f} K={beta[1]:10.5f}  maxres={res:8.4f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--band", action="append", choices=["n", "a"])
    ap.add_argument("--fit", action="store_true", help="re-fit the saved rows")
    a = ap.parse_args()
    if a.fit:
        rows = json.load(open(OUT))
        fit(rows, CELLS)
        fit_bandn(rows, CELLS)
        return 0
    bands = a.band or ["n", "a"]
    print(f"p12 sweep -> {OUT}   bands={bands}")
    rows = measure(bands, CELLS)
    if os.path.exists(OUT) and a.band:
        old = [r for r in json.load(open(OUT)) if r["band"] not in bands]
        rows = old + rows
    json.dump(rows, open(OUT, "w"), indent=1)
    fit(rows, CELLS)
    fit_bandn(rows, CELLS)
    return 0


if __name__ == "__main__":
    sys.exit(main())
