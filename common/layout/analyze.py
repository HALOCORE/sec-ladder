#!/usr/bin/env python3
"""Read a `layout_<tag>.json` population and ask the four layout questions.

  1. Is the timing population bimodal at all (largest-gap clustering, and the
     ratio of the two cluster medians)?
  2. Does any address bit separate it?  Every bit from 4 to 12 is tried and the
     best is reported with its separation quality, so the answer can be "none".
     ⚠ An address bit is a PROXY -- see `loopfit.py` for the mechanism.  Bit 4
     only looks like a law because every kernel here is 16-byte aligned, so a
     32-byte-granular property can take exactly two values.
  3. Does the 32-byte loop geometry separate it (`loopfit.fit`)?
  4. Mode-matched rung comparison, and how much of the gap survives.
  5. Cross-pass reproducibility -- is a layout's time a PROPERTY of the binary
     or is it noise?  A real layout effect survives an independent pass.

    python3 common/layout/analyze.py .temp/layout/layout_p01.json
"""
import argparse
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import loopfit  # noqa: E402

CELLORDER = ["safe_naive", "safe_tuned", "unsafe"]


def spearman(x, y):
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        for pos, i in enumerate(order):
            r[i] = pos
        return r
    rx, ry = rank(x), rank(y)
    n = len(x)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** .5
    return num / den if den else float("nan")


def cluster(vals):
    v = sorted(vals)
    gaps = [(v[i + 1] - v[i], v[i], v[i + 1]) for i in range(len(v) - 1)]
    g, a, b = max(gaps)
    return g, [x for x in v if x <= a], [x for x in v if x >= b]


def sep_quality(groups):
    if len(groups) != 2 or any(len(g) == 0 for g in groups):
        return None
    a, b = groups
    if statistics.median(a) > statistics.median(b):
        a, b = b, a
    return max(a) < min(b)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("json")
    ap.add_argument("--ref", default="unsafe")
    a = ap.parse_args()
    rows = loopfit.load(a.json)
    cells = [c for c in CELLORDER if c in rows] + \
            [c for c in rows if c not in CELLORDER]
    print(f"### {os.path.basename(a.json)}")
    for stem in loopfit.stems(rows):
        print(f"\n================ {stem}.bin ================")
        print("-- band and clustering --")
        for c in cells:
            v = [r[stem] for r in rows[c]]
            g, lo, hi = cluster(v)
            print(f"  {c:12s} n={len(v)} {min(v):7.3f}..{max(v):7.3f} ms "
                  f"spread {100*(max(v)-min(v))/min(v):6.2f}%  "
                  f"largest gap {g:.3f} -> {len(lo)}@{statistics.median(lo):.3f}"
                  f" / {len(hi)}@{statistics.median(hi):.3f}  "
                  f"ratio {statistics.median(hi)/statistics.median(lo):.4f}x")

        print("-- does an address bit separate it? (PROXY; see loopfit.py) --")
        for c in cells:
            best = []
            for bit in range(4, 13):
                gr = {}
                for r in rows[c]:
                    gr.setdefault((r["addr"] >> bit) & 1, []).append(r[stem])
                if len(gr) != 2 or min(len(x) for x in gr.values()) < 3:
                    continue
                ratio = statistics.median(gr[1]) / statistics.median(gr[0])
                best.append((abs(ratio - 1), bit, ratio,
                             sep_quality([gr[0], gr[1]]),
                             len(gr[0]), len(gr[1])))
            best.sort(reverse=True)
            print(f"  {c:12s} " + "   ".join(
                f"bit{b}: x{r:.4f} {'PERFECT' if p else 'overlap '} "
                f"(n={n0}/{n1})" for _, b, r, p, n0, n1 in best[:3]))

    print("\n-- does the 32-byte loop geometry separate it? (the MECHANISM) --")
    for c in cells:
        hits = 0
        for li, L, prop, ks, stem, ratio, ok in loopfit.fit(rows, c):
            hits += 1
            print(f"  {c:12s} loop{li} [+{L['lo']:#x},+{L['hi']:#x}) "
                  f"{L['bytes']:3d}B  {prop:5s}{ks} {stem:12s} x{ratio:.4f}"
                  f"{'  *PERFECT*' if ok else ''}")
        if not hits:
            print(f"  {c:12s} no (loop, property) pair moves the time by >1% "
                  f"or separates it")

    if a.ref in rows:
        for stem in loopfit.stems(rows):
            print(f"\n-- {stem}: rung vs {a.ref}: pooled, mode-matched "
                  f"(addr%32), pairwise P(A>B) --")
            ref = rows[a.ref]
            refv = [r[stem] for r in ref]
            for c in cells:
                if c == a.ref:
                    continue
                cv = [r[stem] for r in rows[c]]
                pooled = 100 * (statistics.median(cv) - statistics.median(refv)) \
                    / statistics.median(refv)
                line = f"  {c:12s} pooled median {pooled:+6.2f}%   " \
                       f"best-vs-best {100*(min(cv)-min(refv))/min(refv):+6.2f}%   "
                for res in (0, 16):
                    cvr = [r[stem] for r in rows[c] if r["addr"] % 32 == res]
                    rvr = [r[stem] for r in ref if r["addr"] % 32 == res]
                    if cvr and rvr:
                        line += (f"mode{res}: {100*(statistics.median(cvr)-statistics.median(rvr))/statistics.median(rvr):+6.2f}%"
                                 f" (n={len(cvr)}/{len(rvr)})  ")
                pw = 100.0 * sum(1 for x in cv for y in refv if x > y) \
                    / (len(cv) * len(refv))
                line += f"| P(A>B) {pw:5.1f}%"
                print(line)

    all_stems = loopfit.stems(rows)
    for base in sorted({s.split("#")[0] for s in all_stems}):
        reps = [s for s in all_stems if s.split("#")[0] == base]
        if len(reps) < 2:
            continue
        print(f"\n-- cross-pass reproducibility, {base}.bin "
              f"({len(reps)} passes: {reps}) --")
        for c in cells:
            for i in range(len(reps)):
                for j in range(i + 1, len(reps)):
                    x = [r[reps[i]] for r in rows[c]]
                    y = [r[reps[j]] for r in rows[c]]
                    rel = [abs(b - a_) / a_ for a_, b in zip(x, y)]
                    print(f"  {c:12s} {reps[i]} vs {reps[j]}: "
                          f"spearman rho {spearman(x, y):+.3f}   "
                          f"median |d| {100*statistics.median(rel):.2f}%   "
                          f"max |d| {100*max(rel):.2f}%")
    return 0


if __name__ == "__main__":
    sys.exit(main())
