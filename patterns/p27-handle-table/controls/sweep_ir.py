#!/usr/bin/env python3
"""p27's sweep: measure marginal Ir/call over the `sweep-*` bands and fit the
four-regressor law, with the DOMAIN printed beside it.

    python3 patterns/p27-handle-table/inputs/gen.py --sweep
    python3 patterns/p27-handle-table/controls/sweep_ir.py --measure --cells unsafe,safe_tuned
    python3 patterns/p27-handle-table/controls/sweep_ir.py --fit .temp/p27/sweep.json

MARGINAL, NOT LEVEL. `.memory/03-measurement.md`: `measure.py`'s callgrind
columns are whole-run LEVELS and carry a per-process constant. Every number this
script produces is `(Ir(2N) - Ir(N)) / N` over the same binary and the same
input, which differences that constant away exactly.

INTERLEAVED BY CELL, NEVER BY BLOCK, and in the FOREGROUND. A probe that gives
each cell a contiguous block of every rep flipped a sign on its own
(`.memory/03-measurement.md`, finding 16's methodological result). Scratch is
per-PID.

THE REGRESSORS, and why three bands and not one:

  nopen    OPEN operations accepted (one malloc + one store each)
  nclose   CLOSE operations accepted (one free each)
  nread    READ operations accepted (one table index, one liveness test, one
           record load each)
  nrej     operations rejected on any path (the SENTINEL fold)

  band O   the mix held, the op count swept 8..128. Every regressor scales
           together, so this band alone cannot separate them -- it says whether
           the law is linear in the stream length at all.
  band R   the op count held at 96, the read fraction swept 0..0.80. The
           allocator traffic falls exactly as the number of reads rises, which
           is what breaks band O's collinearity.
  band S   the op count and the mix held, the table capacity the generator uses
           swept 1..32, so the number of LIVE records moves with everything else
           held. It is the band that can falsify "a READ costs the same however
           many records are alive".

⚠ A LAW OWES ITS DOMAIN, and p27's domain is a list of MISSING COLUMNS, not a
caveat (`.memory/03-measurement.md`; p10 went 3 -> 4 -> 6 parameters). Four are
known missing and unswept, and `--fit` prints them every run: RECSZ (fixed at 1,
so the whole sweep sits in one glibc size class and inside the tcache), TABCAP
(fixed at 32), the allocator itself (glibc 2.39's tcache IS the recycling
mechanism), and the op ORDER (an OPEN straight after a CLOSE is the case the
tcache serves fastest). The list is not closed.
"""
import argparse
import json
import os
import re
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PD = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PD))
sys.path.insert(0, os.path.join(REPO, "harness"))
sys.path.insert(0, os.path.join(REPO, "common"))
import measure as M  # noqa: E402
import slb  # noqa: E402

INDIR = os.path.join(PD, "inputs")
BUILD = os.path.join(REPO, ".temp", "build", "p27")
TABCAP, SENT, HDR, OPSZ = 32, 251, 4, 2


def regressors(path):
    """(nopen, nclose, nread, nrej) per kernel call, from the file alone.

    Every window of a sweep blob has the same op count by construction, and the
    driver's Lemire index visits windows pseudo-randomly, so the per-call figure
    is the MEAN over the blob's windows -- computed exactly here rather than
    sampled."""
    f = slb.read(path)
    stride, buf = slb.head1_u64_bytes(f.payload[: f.declared_len])
    nwin = len(buf) // stride
    tot = [0, 0, 0, 0]
    for w in range(nwin):
        win = buf[w * stride:(w + 1) * stride]
        nops = int.from_bytes(win[0:4], "little")
        tab, p = [], HDR
        for _ in range(nops):
            if len(win) - p < OPSZ:
                break
            c, a = win[p], win[p + 1]
            p += OPSZ
            op, h = c % 4, a
            if op == 0:
                if len(tab) < TABCAP:
                    tab.append(a)
                    tot[0] += 1
                else:
                    tot[3] += 1
            elif op == 1:
                if h < len(tab) and tab[h] is not None:
                    tab[h] = None
                    tot[1] += 1
                else:
                    tot[3] += 1
            else:
                if h < len(tab) and tab[h] is not None:
                    tot[2] += 1
                else:
                    tot[3] += 1
    return [t / nwin for t in tot], stride, nwin


def rewrite_iters(src, dst, n_iters):
    b = bytearray(open(src, "rb").read())
    b[0:8] = struct.pack("<Q", n_iters)
    open(dst, "wb").write(bytes(b))


VG = os.path.expanduser("~/tools/valgrind/bin/valgrind")


def total_ir(binary, arg, scr, tag):
    """WHOLE-PROGRAM Ir, from callgrind's own `totals:` line.

    NOT kernel-exclusive. p27's kernel calls `malloc` and `free` once per record
    and those bodies live in glibc, outside every symbol `_sum_rows` matches --
    measured, ~58-62% of the work. A law fitted on kernel-exclusive Ir would be
    a law about the part of an OPEN that is not the allocation."""
    o = os.path.join(scr, f"cg.{tag}")
    r = subprocess.run([VG, "--tool=callgrind", f"--callgrind-out-file={o}",
                        binary, arg], capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"sweep_ir.py: callgrind exit {r.returncode}")
    for line in open(o):
        if line.startswith("totals:"):
            return int(line.split()[1])
    raise SystemExit("sweep_ir.py: no `totals:` line in the callgrind output")


def marginal(binary, inp, scr, n1, n2):
    """(Ir(n2) - Ir(n1)) / (n2 - n1), WHOLE PROGRAM.

    The marginal differences out `measure.py`'s per-process constant exactly
    (`.memory/03-measurement.md` finding 20a: the `ns` and `Ir` columns are
    LEVELS, never differences)."""
    out = {}
    for n in (n1, n2):
        p = os.path.join(scr, f"in.{n}.bin")
        rewrite_iters(inp, p, n)
        out[n] = total_ir(binary, p, scr, f"{os.path.basename(binary)}.{n}")
    return (out[n2] - out[n1]) / float(n2 - n1)


def cmd_measure(a):
    scr = os.path.join(REPO, ".temp", "p27", f"sweep{os.getpid()}")
    os.makedirs(scr, exist_ok=True)
    blobs = sorted(f for f in os.listdir(INDIR)
                   if f.startswith("sweep-") and f.endswith(".bin"))
    if not blobs:
        raise SystemExit("sweep_ir.py: no sweep-* blobs; run inputs/gen.py --sweep")
    cells = a.cells.split(",")
    rows = []
    for b in blobs:                      # blob outer, CELL inner: interleaved
        reg, stride, nwin = regressors(os.path.join(INDIR, b))
        rec = {"blob": b, "stride": stride, "nwin": nwin,
               "nopen": reg[0], "nclose": reg[1], "nread": reg[2], "nrej": reg[3]}
        for c in cells:
            binary = os.path.join(BUILD, f"{c}-{a.opt}-{a.mode}")
            rec[c] = marginal(binary, os.path.join(INDIR, b), scr, a.n1, a.n2)
        rows.append(rec)
        print(f"  {b:22s} open={reg[0]:6.2f} close={reg[1]:6.2f} "
              f"read={reg[2]:6.2f} rej={reg[3]:6.2f}  "
              + "  ".join(f"{c}={rec[c]:10.4f}" for c in cells), flush=True)
    json.dump({"opt": a.opt, "mode": a.mode, "n1": a.n1, "n2": a.n2,
               "cells": cells, "rows": rows}, open(a.out, "w"), indent=1)
    subprocess.run(["rm", "-rf", scr])
    print(f"sweep_ir.py: {len(rows)} blobs -> {a.out}")
    return 0


def lstsq(X, y):
    """Ordinary least squares by Gaussian elimination on the normal equations --
    no numpy on this box (`.memory/00-environment.md`)."""
    k = len(X[0])
    A = [[sum(X[r][i] * X[r][j] for r in range(len(X))) for j in range(k)]
         + [sum(X[r][i] * y[r] for r in range(len(X)))] for i in range(k)]
    for i in range(k):
        piv = max(range(i, k), key=lambda r: abs(A[r][i]))
        A[i], A[piv] = A[piv], A[i]
        if abs(A[i][i]) < 1e-12:
            return None
        for r in range(k):
            if r == i:
                continue
            f = A[r][i] / A[i][i]
            for c in range(i, k + 1):
                A[r][c] -= f * A[i][c]
    return [A[i][k] / A[i][i] for i in range(k)]


def cmd_fit(a):
    d = json.load(open(a.path))
    names = ["nopen", "nclose", "nread", "nrej", "const"]
    for c in d["cells"]:
        rows = d["rows"]
        X = [[r["nopen"], r["nclose"], r["nread"], r["nrej"], 1.0] for r in rows]
        y = [r[c] for r in rows]
        b = lstsq(X, y)
        if b is None:
            print(f"{c}: singular design -- the bands are collinear")
            continue
        res = [y[i] - sum(b[j] * X[i][j] for j in range(5)) for i in range(len(y))]
        mx = max(abs(v) for v in res)
        print(f"{c:14s} " + "  ".join(f"{n}={v:9.4f}" for n, v in zip(names, b))
              + f"   max|resid| {mx:8.4f}  n={len(y)}")
    # --- the DIFFERENCES, which is what may actually be published ---------
    # `.memory/01-ladder.md` finding 14 / TASK_026 §0 item 1: publish
    # matched-spelling DIFFERENCES, never a level and never a difference of
    # rates across unmatched spellings. On p27 the reason is mechanical as well
    # as methodological -- the allocator is 58-62% of every level and cancels
    # exactly in a difference, which is why the residuals below are two orders
    # of magnitude smaller than the levels' are.
    pairs = [("c-gcc-h", "c-gcc", "R1h - R1  (gcc)"),
             ("c-clang-h", "c-clang", "R1h - R1  (clang)"),
             ("safe_tuned", "unsafe", "R3 - R4"),
             ("safe_naive", "unsafe", "R2 - R4"),
             ("safe_tuned", "c-gcc-h", "R3 - R1h (gcc)"),
             ("unsafe", "c-gcc-h", "R4 - R1h (gcc)")]
    have = set(d["cells"])
    print()
    print("DIFFERENCES -- the allocator cancels, and these are what may be quoted:")
    for a_, b_, name in pairs:
        if a_ not in have or b_ not in have:
            continue
        X = [[r["nopen"], r["nclose"], r["nread"], r["nrej"], 1.0] for r in d["rows"]]
        y = [r[a_] - r[b_] for r in d["rows"]]
        b = lstsq(X, y)
        res = [y[i] - sum(b[j] * X[i][j] for j in range(5)) for i in range(len(y))]
        print(f"  {name:20s} " + "  ".join(f"{n}={v:9.4f}" for n, v in zip(names, b))
              + f"   max|resid| {max(abs(v) for v in res):8.4f}")
    print()
    print("DOMAIN -- what this law is NOT swept over, and the list is not closed:")
    print("  RECSZ  = 1 byte per record. One glibc size class, inside the tcache.")
    print("  TABCAP = 32 slots, in every rung and every blob.")
    print("  the allocator: glibc 2.39. Its tcache IS the recycling mechanism.")
    print("  the op ORDER: the mix and the count are swept, the interleaving is not.")
    print("    -- and this one is MEASURED to matter. Splitting `nopen` into")
    print("       tcache HITS and MISSES (an OPEN straight after a CLOSE reuses")
    print("       the chunk) prices a hit at ~194 Ir and a miss at ~240 on the")
    print("       Rust rungs and ~178/~222 on the C ones, and cuts the LEVEL")
    print("       fit's max residual from ~154 to ~127 -- an improvement, and")
    print("       nowhere near closure. The level fit is NOT a law; the")
    print("       DIFFERENCES above are the publishable quantities.")
    return 0


def hitmiss_regressors(path):
    """`nopen` split into tcache HITS and MISSES, from the file alone.

    An OPEN reuses a chunk iff a CLOSE has put one in the bin since the last
    OPEN took it out. glibc's tcache is a 7-deep LIFO per size class and every
    record here is `malloc(1)`, so one bin and one stack is the whole
    simulation -- zero fitted parameters, exactly like `regressors` above.
    ../NOTES.md 9b is what this prints."""
    f = slb.read(path)
    stride, buf = slb.head1_u64_bytes(f.payload[: f.declared_len])
    nwin = len(buf) // stride
    tot = [0, 0, 0, 0, 0]                      # hit, miss, nclose, nread, nrej
    for w in range(nwin):
        win = buf[w * stride:(w + 1) * stride]
        nops = int.from_bytes(win[0:4], "little")
        tab, p, tcache = [], HDR, 0
        for _ in range(nops):
            if len(win) - p < OPSZ:
                break
            c, a = win[p], win[p + 1]
            p += OPSZ
            op, h = c % 4, a
            if op == 0:
                if len(tab) < TABCAP:
                    tab.append(a)
                    if tcache > 0:
                        tcache -= 1
                        tot[0] += 1
                    else:
                        tot[1] += 1
                else:
                    tot[4] += 1
            elif op == 1:
                if h < len(tab) and tab[h] is not None:
                    tab[h] = None
                    tcache = min(tcache + 1, 7)
                    tot[2] += 1
                else:
                    tot[4] += 1
            else:
                if h < len(tab) and tab[h] is not None:
                    tot[3] += 1
                else:
                    tot[4] += 1
    return [t / nwin for t in tot]


def cmd_hitmiss(a):
    """Refit every swept cell with `nopen` SPLIT, and print both residuals.

    ../NOTES.md 9b's table. It exists as a command rather than as prose because
    the numbers move whenever a rung does: TASK_061 deleted a store from R4 and
    the `unsafe` row moved with it."""
    d = json.load(open(a.path))
    print(f"{'cell':14s} {'nopen (one)':>12s}   {'hit':>9s} {'miss':>9s}   "
          f"{'resid 4-col':>12s} {'resid 5-col':>12s}")
    for c in d["cells"]:
        X1 = [[r["nopen"], r["nclose"], r["nread"], r["nrej"], 1.0] for r in d["rows"]]
        hm = [hitmiss_regressors(os.path.join(INDIR, r["blob"])) for r in d["rows"]]
        X2 = [[g[0], g[1], r["nclose"], r["nread"], r["nrej"], 1.0]
              for g, r in zip(hm, d["rows"])]
        y = [r[c] for r in d["rows"]]
        b1, b2 = lstsq(X1, y), lstsq(X2, y)
        r1 = max(abs(y[i] - sum(b1[j] * X1[i][j] for j in range(5)))
                 for i in range(len(y)))
        r2 = max(abs(y[i] - sum(b2[j] * X2[i][j] for j in range(6)))
                 for i in range(len(y)))
        print(f"{c:14s} {b1[0]:12.4f}   {b2[0]:9.4f} {b2[1]:9.4f}   "
              f"{r1:12.4f} {r2:12.4f}")
    print("\nThe split is an IMPROVEMENT and nowhere near closure: the op ORDER")
    print("is a real missing column, it is now measured, and it is not the only")
    print("one left (../NOTES.md 9a, 9d).")
    return 0


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("measure")
    m.add_argument("--cells", default="c-gcc,c-gcc-h,safe_naive,safe_tuned,unsafe,verus")
    m.add_argument("--opt", default="O3")
    m.add_argument("--mode", default="isolated")
    m.add_argument("--n1", type=int, default=2000)
    m.add_argument("--n2", type=int, default=4000)
    m.add_argument("--out", default=os.path.join(REPO, ".temp", "p27", "sweep.json"))
    m.set_defaults(fn=cmd_measure)
    f = sub.add_parser("fit")
    f.add_argument("path")
    f.set_defaults(fn=cmd_fit)
    hm = sub.add_parser("hitmiss")
    hm.add_argument("path")
    hm.set_defaults(fn=cmd_hitmiss)
    a = ap.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
