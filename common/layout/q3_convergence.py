#!/usr/bin/env python3
"""Which layout statistic actually CONVERGES as the population grows?

TASK_029 retired "publish an interval, require disjoint bands" because the
worst-vs-best range provably widens with more samples.  That is an argument
against the old rule, not evidence for a new one.  This subsamples a population
at several sizes, 400 draws each, and reports mean +- spread for all of them:

  band / range-interval  drifts monotonically (the retired rule)
  mode-matched median    FLAT in N, spread ~1/sqrt(N)  -> converges
  dominance vs worst     DRIFTS -- defined against an EXTREMUM of B, so it
                         inherits the range's defect (+-26 points at N=4)
  pairwise P(A>B)        a genuine proportion over all N*N pairs, flat in N

    python3 common/layout/q3_convergence.py .temp/layout/layout_p01.json \\
        small safe_naive unsafe
"""
import os
import random
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import loopfit  # noqa: E402


def main():
    path, stem = sys.argv[1], sys.argv[2]
    cell = sys.argv[3] if len(sys.argv) > 3 else "safe_naive"
    ref = sys.argv[4] if len(sys.argv) > 4 else "unsafe"
    rows = loopfit.load(path)
    A, B = rows[cell], rows[ref]
    rng = random.Random(11)
    print(f"### {os.path.basename(path)}  {stem}  {cell} vs {ref}")
    print(f"{'N':>3s} | {'band(A) %':>18s} | {'range-interval lo/hi':>22s} | "
          f"{'mode0 %':>16s} | {'mode16 %':>16s} | {'dom vs worst':>16s} | "
          f"{'pairwise P(A>B)':>16s}")
    for n in (4, 7, 10, 15, 20, 25, 30):
        if n > min(len(A), len(B)):
            continue
        band, ilo, ihi, m0, m16, dom, pw = [], [], [], [], [], [], []
        for _ in range(400):
            sa, sb = rng.sample(A, n), rng.sample(B, n)
            a = [r[stem] for r in sa]
            b = [r[stem] for r in sb]
            band.append(100 * (max(a) - min(a)) / min(a))
            ilo.append(100 * (min(a) - max(b)) / max(b))
            ihi.append(100 * (max(a) - min(b)) / min(b))
            for res, acc in ((0, m0), (16, m16)):
                x = [r[stem] for r in sa if r["addr"] % 32 == res]
                y = [r[stem] for r in sb if r["addr"] % 32 == res]
                if x and y:
                    acc.append(100 * (statistics.median(x)
                                      - statistics.median(y))
                               / statistics.median(y))
            dom.append(100.0 * sum(1 for x in a if x > max(b)) / n)
            pw.append(100.0 * sum(1 for x in a for y in b if x > y) / (n * n))

        def s(v):
            if not v:
                return "         n/a     "
            return f"{statistics.mean(v):+7.2f}±{statistics.pstdev(v):5.2f}"
        print(f"{n:3d} | {s(band):>18s} | {s(ilo):>10s} {s(ihi):>10s} | "
              f"{s(m0):>16s} | {s(m16):>16s} | {s(dom):>16s} | "
              f"{s(pw):>16s}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
