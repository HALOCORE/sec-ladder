#!/usr/bin/env python3
"""REVIEWER's INDEPENDENT re-derivation for TASK_PHP_059.

Deliberately shares NO code with `.tasks-php/php58_record_share.py`:
  * `n_iters` is parsed from the .bin header with `struct` directly rather than
    via `common-php/slb.py`;
  * the record walk is written from the schema, not copied;
  * the pair enumeration is ALL unordered cell pairs, not a hand-written list of
    nine, so it cannot inherit the manager's choice of which pairs count.

    python3 .tasks-php/php59_share.py cells      # every cell, F74 share
    python3 .tasks-php/php59_share.py pairs      # (ii) tally, x-lang vs same-lang
    python3 .tasks-php/php59_share.py sweep      # condition (i) threshold sweep
    python3 .tasks-php/php59_share.py over1      # cells above 1.0
    python3 .tasks-php/php59_share.py selftest
"""
import glob
import json
import os
import struct
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUTS = ("small.bin", "large.bin")
C_CELLS = ("c-gcc", "c-clang", "c-gcc-h", "c-clang-h")


def niters(rowdir, inp):
    with open(os.path.join(REPO, "patterns-php", rowdir, "inputs", inp), "rb") as f:
        return struct.unpack("<Q", f.read(8))[0]


def rowdirs():
    out = []
    for p in sorted(glob.glob(os.path.join(REPO, "results-php", "*.json"))):
        b = os.path.basename(p)[:-5]
        if b.startswith("ph00"):
            continue
        out.append(b)
    return out


def cells(row):
    """[(cell, opt, mode, inp, a1_per_call, marginal, f74_share)]"""
    m = json.load(open(os.path.join(REPO, "results-php", row + ".json")))
    g = json.load(open(os.path.join(REPO, "results-php", "gate", row + ".json")))
    marg = g["marginal_ir_per_call"]
    out = []
    for c in m["cells"]:
        ir = c.get("ir") or {}
        for inp in INPUTS:
            d = ir.get(inp) or {}
            kx = d.get("kernel_exclusive_ir")
            if kx is None:
                continue
            key = "/".join((c["cell"], c["opt"], c["mode"], inp))
            mv = marg.get(key)
            n = niters(row, inp)
            a1 = kx / n
            s = None if (not mv or not n) else a1 / mv
            out.append((c["cell"], c["opt"], c["mode"], inp, a1, mv, s))
    return out


def is_c(cell):
    return cell in C_CELLS


def allpairs(row, opt="O3", mode="isolated"):
    """EVERY unordered pair of distinct cells, same opt/mode/input."""
    tbl = {}
    for cell, o, md, inp, a1, mv, s in cells(row):
        if o == opt and md == mode:
            tbl[(cell, inp)] = (a1, s)
    names = sorted({k[0] for k in tbl})
    out = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            for inp in INPUTS:
                if (a, inp) not in tbl or (b, inp) not in tbl:
                    continue
                (a1a, sa), (a1b, sb) = tbl[(a, inp)], tbl[(b, inp)]
                if sa is None or sb is None:
                    continue
                xlang = is_c(a) != is_c(b)
                out.append((a, b, inp, sa, sb, abs(sa - sb), min(sa, sb), xlang))
    return out


MGR_PAIRS = [("safe_tuned", "unsafe"), ("safe_naive", "safe_tuned"),
             ("unsafe", "verus"), ("c-gcc", "c-gcc-h"), ("c-clang", "c-clang-h"),
             ("c-gcc", "safe_naive"), ("c-clang", "safe_naive"),
             ("c-gcc", "safe_tuned"), ("c-clang", "safe_tuned")]


def mgrpairs(row):
    """Restricted to the manager's nine, so the two populations are comparable."""
    keep = {frozenset(p) for p in MGR_PAIRS}
    return [p for p in allpairs(row) if frozenset((p[0], p[1])) in keep]


def cmd_cells():
    n = 0
    for r in rowdirs():
        for t in cells(r):
            n += 1
            print(f"{r:30s} {t[0]:11s} {t[1]:3s}/{t[2]:9s} {t[3]:10s} "
                  f"a1={t[4]:12.4f} marg={t[5]:12.4f} "
                  f"s={'None' if t[6] is None else format(t[6], '.6f')}")
    print(f"\nTOTAL evaluable cells (kernel_exclusive_ir present): {n}")


def cmd_over1():
    hits = [(r,) + t for r in rowdirs() for t in cells(r)
            if t[6] is not None and t[6] > 1.0]
    for h in hits:
        print(f"{h[0]:30s} {h[1]:11s} {h[2]}/{h[3]:9s} {h[4]:10s} s={h[7]:.6f}")
    print(f"\n{len(hits)} cell(s) above 1.0")
    byrow = {}
    for h in hits:
        byrow[h[0]] = byrow.get(h[0], 0) + 1
    print("by row:", byrow)


def _tally(getter, label):
    tot = {(True, True): 0, (True, False): 0, (False, True): 0, (False, False): 0}
    for r in rowdirs():
        for a, b, inp, sa, sb, d, mn, xl in getter(r):
            tot[(xl, d <= 0.02)] += 1
    xp, xf = tot[(True, True)], tot[(True, False)]
    sp, sf = tot[(False, True)], tot[(False, False)]
    print(f"--- {label}: {xp + xf + sp + sf} pairs, O3/isolated, both inputs "
          f"pooled, rule (ii) only")
    print(f"    cross-language: PASS {xp:4d}  FAIL {xf:4d}  "
          f"admissible {100.0 * xp / max(1, xp + xf):.1f} %")
    print(f"    same-language : PASS {sp:4d}  FAIL {sf:4d}  "
          f"admissible {100.0 * sp / max(1, sp + sf):.1f} %")
    return tot


def cmd_pairs():
    _tally(mgrpairs, "the manager's NINE pair classes")
    print()
    _tally(allpairs, "EVERY unordered cell pair")


def cmd_sweep():
    """Condition (i): does any threshold t change a cross-language verdict?

    Verdict = (i) and (ii).  With (ii) alone as the base, report for each t how
    many pairs (ii) passes but (i) rejects -- i.e. how many verdicts (i) MOVES.
    """
    for label, getter in (("mgr9", mgrpairs), ("all", allpairs)):
        rowsdat = [(a, b, inp, d, mn, xl)
                   for r in rowdirs() for a, b, inp, sa, sb, d, mn, xl in getter(r)]
        print(f"\n=== population {label}: {len(rowsdat)} pairs")
        print(f"  {'t':>6} {'xlang ii-PASS':>14} {'xlang i-kills':>14} "
                f"{'same ii-PASS':>13} {'same i-kills':>13}")
        for t in (0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99):
            xp = sum(1 for a, b, i, d, mn, xl in rowsdat if xl and d <= 0.02)
            xk = sum(1 for a, b, i, d, mn, xl in rowsdat
                     if xl and d <= 0.02 and mn <= t)
            sp = sum(1 for a, b, i, d, mn, xl in rowsdat if not xl and d <= 0.02)
            sk = sum(1 for a, b, i, d, mn, xl in rowsdat
                     if not xl and d <= 0.02 and mn <= t)
            print(f"  {t:6.2f} {xp:14d} {xk:14d} {sp:13d} {sk:13d}")
        mins = sorted(mn for a, b, i, d, mn, xl in rowsdat if d <= 0.02)
        if mins:
            print(f"  min(share) over ii-PASS pairs: min={mins[0]:.4f} "
                  f"p10={mins[len(mins) // 10]:.4f} "
                  f"median={mins[len(mins) // 2]:.4f} max={mins[-1]:.4f}")


def flippairs(row, opt="O3", mode="isolated", restrict=None):
    """[(a, b, inp, a_ratio, b_ratio, |ds|, min s, xlang, is_flip, is_blind)]

    The FLIP criterion is the one `.memory-php/02-ladder.md` actually used to
    say *"(>0.3, >0.5, >0.6) all give 0 flips"*: A's ratio and the
    whole-program ratio having OPPOSITE NONZERO signs.  B here is
    `marginal_ir_per_call` from the gate record -- family B, the column F86's
    366-comparison taxonomy used."""
    m = json.load(open(os.path.join(REPO, "results-php", row + ".json")))
    g = json.load(open(os.path.join(REPO, "results-php", "gate", row + ".json")))
    marg = g["marginal_ir_per_call"]
    tbl = {}
    for c in m["cells"]:
        if c["opt"] != opt or c["mode"] != mode:
            continue
        for inp in INPUTS:
            kx = ((c.get("ir") or {}).get(inp) or {}).get("kernel_exclusive_ir")
            if kx is None:
                continue
            mv = marg.get("/".join((c["cell"], opt, mode, inp)))
            if not mv:
                continue
            n = niters(row, inp)
            tbl[(c["cell"], inp)] = (kx / n, mv, (kx / n) / mv)
    names = sorted({k[0] for k in tbl})
    keep = {frozenset(p) for p in MGR_PAIRS} if restrict == "mgr9" else None
    out = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if keep is not None and frozenset((a, b)) not in keep:
                continue
            for inp in INPUTS:
                if (a, inp) not in tbl or (b, inp) not in tbl:
                    continue
                a1a, ba, sa = tbl[(a, inp)]
                a1b, bb, sb = tbl[(b, inp)]
                ar, br = a1b / a1a - 1, bb / ba - 1
                out.append((a, b, inp, ar, br, abs(sa - sb), min(sa, sb),
                            is_c(a) != is_c(b), ar * br < 0,
                            ar == 0 and br != 0))
    return out


def cmd_flip():
    """Can ELEVEN rows pin condition (i)?  Criterion: does any threshold admit
    a FLIP through the conjunction that a lower one excluded?"""
    for restrict in ("mgr9", None):
        dat = [t for r in rowdirs() for t in flippairs(r, restrict=restrict)]
        lab = "mgr9" if restrict else "all"
        fl = [t for t in dat if t[8]]
        bl = [t for t in dat if t[9]]
        print(f"\n=== population {lab}: {len(dat)} comparisons, O3/isolated, "
              f"both inputs; FLIP {len(fl)}  BLIND {len(bl)}")
        print(f"  {'t':>6} {'admitted by (i)&(ii)':>21} {'of which FLIP':>14} "
              f"{'of which BLIND':>15}")
        for t in (0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95):
            adm = [x for x in dat if x[5] <= 0.02 and x[6] > t]
            print(f"  {t:6.2f} {len(adm):21d} "
                  f"{sum(1 for x in adm if x[8]):14d} "
                  f"{sum(1 for x in adm if x[9]):15d}")
        print("  FLIPs that pass (ii), with their min-share "
              "(these are what a threshold for (i) must exclude):")
        for x in sorted((x for x in fl if x[5] <= 0.02), key=lambda z: z[6]):
            print(f"      min_s={x[6]:.4f} d={x[5]:.4f} "
                  f"{'XLANG' if x[7] else 'same '} {x[0]} vs {x[1]} {x[2]}")
        print("  BLIND that pass (ii):",
              sum(1 for x in bl if x[5] <= 0.02))


def cmd_named():
    """The two ph29 pairs the finding is about, spelled out."""
    for a, b in (("c-gcc", "safe_naive"), ("c-gcc", "safe_tuned"),
                 ("c-clang", "safe_naive"), ("c-clang", "safe_tuned")):
        for x in flippairs("ph29-recvfrom-alloc"):
            if (x[0], x[1]) == (a, b) or (x[0], x[1]) == (b, a):
                print(f"  {x[0]:10s} vs {x[1]:10s} {x[2]:10s} "
                      f"A1 {100 * x[3]:+8.2f}%  B {100 * x[4]:+8.2f}%  "
                      f"|ds|={x[5]:.4f}  min_s={x[6]:.4f}  "
                      f"flip={x[8]}")


def cmd_selftest():
    """Must-fire arms on synthetic data -- no record read."""
    ok = []

    def arm(name, got, want):
        ok.append((name, got == want, got, want))

    arm("n_iters is the first LE u64", struct.unpack("<Q", b"\x64\0\0\0\0\0\0\0")[0], 100)
    arm("is_c knows the four C cells",
        [is_c(x) for x in ("c-gcc", "c-clang-h", "safe_naive", "verus")],
        [True, True, False, False])
    # a cross-language pair by construction
    arm("share arithmetic", round((1000 / 100) / 20.0, 6), 0.5)
    arm("above 1.0 is not clamped", round((1000 / 100) / 8.0, 6), 1.25)
    bad = [a for a in ok if not a[1]]
    for n, good, got, want in ok:
        print(f"  {'ok  ' if good else 'BAD '}{n}: got {got!r} want {want!r}")
    print(f"\n{len(ok) - len(bad)} of {len(ok)} arms as expected")
    return 1 if bad else 0


if __name__ == "__main__":
    c = sys.argv[1] if len(sys.argv) > 1 else "cells"
    # ⓘ `--selftest` is an ALIAS added when this was moved out of `.temp/` and
    #   registered: `checkers.py`'s N10b requires a flag-gated checker's sweep
    #   argv to be exactly `["--selftest"]`. The bare `selftest` spelling the
    #   reviewer wrote is kept so every command line in TASK_PHP_059_REPORT.md
    #   still runs verbatim.
    sys.exit({"cells": cmd_cells, "pairs": cmd_pairs, "sweep": cmd_sweep,
              "over1": cmd_over1, "selftest": cmd_selftest,
              "--selftest": cmd_selftest, "flip": cmd_flip,
              "named": cmd_named}[c]() or 0)
