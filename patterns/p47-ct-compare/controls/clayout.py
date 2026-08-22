#!/usr/bin/env python3
"""A LAYOUT POPULATION for p47's R3/R4 pair, and the mode analysis of it.

PORTED FROM p27 (`patterns/p27-handle-table/controls/clayout.py`), which was
itself ported from p14, with the paths, the input names and the cell list
changed and nothing else. Diff it against p27's to see that the machinery is
unmodified.

WHY p47 NEEDS IT AT ALL, given that p47's whole result is in `Ir`:
`RECAP.md`'s rule is **no `ns` claim without a layout population**, and p47 is
tempted to make one -- *"constant time costs 1.4x-2.2x wall clock"* is the
sentence a reader wants. This file is what decides whether that sentence is
sayable. p47's population is over the two RUST cells that carry its
safe-vs-unsafe comparison (`safe_tuned` = R3 and `unsafe` = R4); the levers are
`-align-all-functions` and `--symbol-ordering-file`, the two
`.memory/03-measurement.md` says work.

    python3 patterns/p47-ct-compare/controls/clayout.py --build
    python3 patterns/p47-ct-compare/controls/clayout.py --time --input small --reps 13
    python3 patterns/p47-ct-compare/controls/clayout.py --modes

CONTROL 1, asserted every `--build`: `n_fn` and `md5_fn_norel` are single-valued
per cell over the whole population -- i.e. every binary here runs the SAME
instruction stream and differs only in where the linker put it. `md5_fn` is
deliberately not the control: it moves at every layout because `call rel32`
displacements move (`.memory/03-measurement.md`).

WHAT TO QUOTE FROM `--modes`: the MEDIAN of the paired distribution and
`P(A > B)` over all N^2 cross pairs. Worst-vs-best RANGE and dominance are
retracted as layout statistics (`.memory/03-measurement.md`); neither converges
in N.

Scratch is per-PID by default (`--scr`).
"""

import argparse
import itertools
import json
import os
import random
import statistics
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(REPO, "harness"))
sys.path.insert(0, os.path.join(REPO, "common"))
sys.path.insert(0, os.path.join(REPO, "common", "layout"))
import slb          # noqa: E402
import loopfit      # noqa: E402

PDIR = os.path.join(REPO, "patterns", "p47-ct-compare")
# ⚠ NOT `.temp/p14/clay`. `patterns/p27-handle-table/controls/clayout.py:67`
# and `patterns/p14-field-split/controls/clayout.py` BOTH write there, so
# every ported copy shares one scratch directory across patterns and the
# later `--build` silently overwrites the earlier population's `meta.json`
# while its `layout_*.json` survives. Found by running this port unchanged
# (TASK_064); reported, not fixed in p27 -- p47 does not edit another
# pattern. `.memory/03-measurement.md` already records that a scratch path
# can move a published figure.
OUT = os.path.join(REPO, ".temp", "p47", "clay")
RUSTC = os.path.expanduser("~/.cargo/bin/rustc")
NM = os.path.expanduser("~/tools/llvm/bin/llvm-nm")
BASE = ["-C", "codegen-units=1", "-C", "opt-level=3",
        "-C", "debug-assertions=off", "--cfg", "slb_isolated"]
CELLS = ("safe_naive", "safe_tuned", "unsafe")


def sh(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, cwd=REPO)


def build_one(cell, out, more):
    src = os.path.join(PDIR, cell + ".rs")
    if cell == "verus":
        cmd = [sys.executable, os.path.join(REPO, "verus_run.py"), "--compile",
               src, "-o", out] + BASE + list(more)
    else:
        cmd = [RUSTC, "--edition", "2021"] + BASE + list(more) + [src, "-o", out]
    r = sh(cmd)
    if r.returncode or not os.path.exists(out):
        print(f"  FAIL {cell} {more}: {(r.stdout + r.stderr)[-300:]}")
        return False
    return True


def text_symbols(binary):
    syms = []
    for line in sh([NM, binary]).stdout.splitlines():
        f = line.split()
        if len(f) == 3 and f[1] in ("t", "T"):
            syms.append(f[2])
    return syms


def build(aligns, orders):
    os.makedirs(OUT, exist_ok=True)
    bins = {}
    for cell in CELLS:
        for k in range(aligns):
            out = os.path.join(OUT, f"{cell}.align{k}")
            if build_one(cell, out, ["-C", f"llvm-args=-align-all-functions={k}"]):
                bins[(cell, "align", k)] = out
        out = os.path.join(OUT, f"{cell}.shipped0")
        if build_one(cell, out, []):
            bins[(cell, "shipped", 0)] = out
        base = bins.get((cell, "shipped", 0))
        if base and orders:
            syms = text_symbols(base)
            for s in range(1, orders + 1):
                order = list(syms)
                random.Random(1000 * s + len(cell)).shuffle(order)
                f = os.path.abspath(os.path.join(OUT, f"{cell}.ord{s}.txt"))
                open(f, "w").write("\n".join(order) + "\n")
                out = os.path.join(OUT, f"{cell}.order{s}")
                if build_one(cell, out,
                             ["-C", f"link-arg=-Wl,--symbol-ordering-file={f}"]):
                    bins[(cell, "order", s)] = out

    meta = {}
    for (cell, lev, k), b in bins.items():
        rep = loopfit.kernel_report(b, "kernel")
        meta[f"{cell}|{lev}|{k}"] = {
            "lever": lev, "idx": k, "bin": b, "addr": rep["addr"],
            "n_fn": rep["n_fn"], "md5_fn": rep["md5_fn"],
            "md5_fn_norel": rep["md5_fn_norel"], "loops": rep["loops"],
        }
    json.dump(meta, open(os.path.join(OUT, "meta.json"), "w"), indent=1)

    print("\nCONTROL 1 -- kernel machine code invariant over the population:")
    ok = True
    norel = {}
    for cell in CELLS:
        ks = [k for k in meta if k.split("|")[0] == cell]
        nf = sorted({meta[k]["n_fn"] for k in ks})
        nr = sorted({meta[k]["md5_fn_norel"] for k in ks})
        ad = sorted({meta[k]["addr"] for k in ks})
        norel[cell] = nr
        ok &= len(nf) == 1 and len(nr) == 1
        print(f"  {cell:7s} {len(ks):3d} builds  n_fn {nf}  md5_fn_norel {nr}  "
              f"{len(set(ad))} distinct addrs 0x{ad[0]:x}..0x{ad[-1]:x}  "
              f"addr%32 {sorted({x % 32 for x in ad})}  "
              f"addr%64 {sorted({x % 64 for x in ad})}")
    # p27's population is the R4/R5 pair, whose kernels must be IDENTICAL, so
    # its control also asserted `norel[unsafe] == norel[verus]`. p47's is the
    # R3/R4 pair, which are different programs by construction, so that half of
    # the control does not apply and is replaced by the per-cell one above --
    # the only edit to the ported machinery beyond paths and the cell list.
    print(f"  single-valued per cell: {ok}   "
          f"(cross-cell equality NOT asserted: this population is R3 vs R4, "
          f"which are different programs)")
    return 0 if ok else 1


def time_pop(stem, reps, n_iters, cpu, scr):
    meta = json.load(open(os.path.join(OUT, "meta.json")))
    keys = sorted(meta)
    os.makedirs(scr, exist_ok=True)
    f = slb.read(os.path.join(PDIR, "inputs", stem + ".bin"))
    big = os.path.join(scr, f"{stem}.big.bin")
    one = os.path.join(scr, f"{stem}.one.bin")
    slb.write(big, n_iters, f.payload[: f.declared_len])
    slb.write(one, 1, f.payload[: f.declared_len])
    # ONE flat interleaved schedule: every cell launched once before any twice.
    per = {}
    for k in keys:
        per.setdefault(k.split("|")[0], []).append(k)
    sched = []
    for i in range(max(len(v) for v in per.values())):
        for c in per:
            if i < len(per[c]):
                sched.append(per[c][i])
    samples = {k: [] for k in keys}
    outs = {}
    t0 = time.time()
    for _ in range(reps):
        for k in sched:
            b = meta[k]["bin"]
            x = time.perf_counter()
            subprocess.run(["/usr/bin/taskset", "-c", str(cpu), b, one],
                           capture_output=True, text=True)
            y = time.perf_counter()
            r2 = subprocess.run(["/usr/bin/taskset", "-c", str(cpu), b, big],
                                capture_output=True, text=True)
            z = time.perf_counter()
            outs.setdefault(k, r2.stdout.strip())
            samples[k].append(((z - y) - (y - x)) / (n_iters - 1) * 1e9)
    est = {k: min(v) for k, v in samples.items()}
    med = {k: statistics.median(v) for k, v in samples.items()}
    print(f"# stem={stem} n_iters={n_iters} reps={reps} cpu={cpu} "
          f"schedule=alternating estimator=(t(N)-t(1))/(N-1) "
          f"elapsed={time.time() - t0:.0f}s")
    print(f"# distinct stdouts over the whole population: {len(set(outs.values()))}")
    # loopfit-format population: one file per estimator convention
    for tag, e in (("min", est), ("median", med)):
        pop = {k: dict(meta[k], **{stem: e[k]}) for k in keys}
        for k in pop:
            pop[k].pop("bin", None)
        json.dump(pop, open(os.path.join(OUT, f"layout_{stem}_{tag}.json"), "w"),
                  indent=1)
    json.dump({"stem": stem, "n_iters": n_iters, "reps": reps, "cpu": cpu,
               "min": est, "median": med, "raw": samples, "stdout": outs},
              open(os.path.join(OUT, f"times_{stem}.json"), "w"), indent=1)
    return 0


def _pairs(u, v):
    return [(y / x - 1) * 100 for x in u for y in v]


def modes(stem, tag, boundary):
    path = os.path.join(OUT, f"layout_{stem}_{tag}.json")
    rows = loopfit.load(path)
    raw = json.load(open(path))
    print(f"# {path}  estimator={tag}-of-reps  stem={stem}  boundary={boundary}")
    if boundary != 32:
        # `win32`/`jcc32` are computed against a FETCH GRID whose spacing is a
        # parameter.  32 is the DSB window and the one `.memory/03-measurement.md`
        # names; p47 inherits p27's 64-byte case -- see ../NOTES.md 11.
        meta = json.load(open(os.path.join(OUT, "meta.json")))
        for k in raw:
            raw[k]["loops"] = loopfit.kernel_report(
                meta[k]["bin"], "kernel", boundary=boundary)["loops"]
            for r in rows[k.split("|")[0]]:
                if r["lever"] == k.split("|")[1] and r["idx"] == int(k.split("|")[2]):
                    r["loops"] = raw[k]["loops"]

    for cell in CELLS:
        v = [raw[k][stem] for k in raw if k.split("|")[0] == cell]
        q = statistics.quantiles(v, n=4)
        print(f"  {cell:7s} n={len(v):3d}  ns/call {min(v):7.2f}..{max(v):7.2f}"
              f"  RANGE {100 * (max(v) - min(v)) / min(v):5.2f}%  "
              f"median {statistics.median(v):7.2f}  IQR {q[0]:7.2f}..{q[2]:7.2f}"
              f" ({100 * (q[2] - q[0]) / q[0]:4.2f}%)")

    # the pair, three ways
    ship = {c: raw[f"{c}|shipped|0"][stem] for c in CELLS}
    # p27's copy hard-codes the R5-vs-R4 pair. p47's population is R3 vs R4
    # (and R2 when built), so the pair is parameterised and every ordered pair
    # of cells is reported. The two statistics printed are the ones
    # `.memory/03-measurement.md` says converge -- the MEDIAN of the paired
    # distribution and `P(A > B)` over all N^2 cross pairs. Worst-vs-best RANGE
    # is printed above only because the eye wants it; it is retracted as a
    # layout statistic and must not be quoted.
    for hi, lo in itertools.combinations([c for c in CELLS], 2):
        paired, keys = [], []
        for k in raw:
            cell, lev, idx = k.split("|")
            if cell != hi:
                continue
            uk = f"{lo}|{lev}|{idx}"
            if uk in raw:
                paired.append((raw[k][stem] / raw[uk][stem] - 1) * 100)
                keys.append((lev, idx))
        u = [raw[k][stem] for k in raw if k.startswith(lo + "|")]
        v = [raw[k][stem] for k in raw if k.startswith(hi + "|")]
        if not u or not v or not paired:
            print(f"\n  {hi}-{lo}: no paired layouts")
            continue
        cross = sorted(_pairs(u, v))
        pab = sum(1 for x in u for y in v if y > x) / float(len(u) * len(v))
        ps = sorted(paired)
        print(f"\n  {hi} vs {lo}  SHIPPED pair          "
              f"{(ship[hi] / ship[lo] - 1) * 100:+6.2f}%"
              f"   ({lo} {ship[lo]:.2f} ns, {hi} {ship[hi]:.2f} ns)")
        print(f"  {hi} vs {lo}  paired by layout n={len(ps):3d}  "
              f"range {ps[0]:+6.2f}..{ps[-1]:+6.2f}   "
              f"MEDIAN {statistics.median(ps):+6.2f}%")
        print(f"  {hi} vs {lo}  all cross pairs  n={len(cross):3d}  "
              f"range {cross[0]:+6.2f}..{cross[-1]:+6.2f}   "
              f"MEDIAN {statistics.median(cross):+6.2f}%   "
              f"P({hi}>{lo}) = {pab:.3f}")

    # which loop/property separates the population?  from the listing.
    print("\n  loopfit.fit -- (loop, property) vs time, from the disassembly:")
    for cell in CELLS:
        for li, L, prop, ks, st, ratio, perfect in loopfit.fit(rows, cell):
            print(f"    {cell:7s} loop{li} {prop:6s} lo=0x{L['lo']:x} "
                  f"bytes={L['bytes']:4d} groups={ks} ratio={ratio:.4f} "
                  f"perfect={perfect}")

    # mode-matched comparison, partitioned by the winning predicate.
    # PARAMETERISED over the pair, where p27's copy hard-coded `unsafe`/`verus`
    # and raised KeyError on any population with a third cell.
    hi_c, lo_c = CELLS[-2], CELLS[-1]
    print(f"\n  mode-matched {hi_c}-{lo_c} (partition from the listing):")
    for li, prop in itertools.product(range(len(raw[f"{lo_c}|shipped|0"]["loops"])),
                                      ("win32", "jcc32")):
        groups = {}
        for k in raw:
            cell = k.split("|")[0]
            if cell not in (hi_c, lo_c):
                continue
            g = raw[k]["loops"][li][prop]
            groups.setdefault(g, {"unsafe": [], "verus": [], "addr": []})
            groups[g]["unsafe" if cell == lo_c else "verus"].append(raw[k][stem])
            groups[g]["addr"].append(raw[k]["addr"])
        if len(groups) < 2 or any(not g["unsafe"] or not g["verus"]
                                  for g in groups.values()):
            continue
        parts = []
        for g in sorted(groups):
            uu, vv = groups[g]["unsafe"], groups[g]["verus"]
            c = sorted(_pairs(uu, vv))
            p = sum(1 for x in uu for y in vv if y > x) / (len(uu) * len(vv))
            parts.append(f"{prop}={g}: n={len(uu)}+{len(vv)} "
                         f"u {min(uu):.2f}..{max(uu):.2f} med {statistics.median(uu):.2f} | "
                         f"v {min(vv):.2f}..{max(vv):.2f} med {statistics.median(vv):.2f} | "
                         f"R5-R4 med {statistics.median(c):+.2f}% P(R5>R4)={p:.3f} | "
                         f"addr%32 {sorted({a % 32 for a in groups[g]['addr']})} "
                         f"addr%64 {sorted({a % 64 for a in groups[g]['addr']})}")
        print(f"    loop{li} {prop}")
        for p in parts:
            print(f"       {p}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--time", action="store_true")
    ap.add_argument("--modes", action="store_true")
    ap.add_argument("--input", default="small")
    ap.add_argument("--reps", type=int, default=13)
    ap.add_argument("--n-iters", type=int, default=200000)
    ap.add_argument("--cpu", type=int, default=5)
    ap.add_argument("--aligns", type=int, default=9)
    ap.add_argument("--orders", type=int, default=14)
    ap.add_argument("--estimator", default="min", choices=("min", "median"))
    ap.add_argument("--boundary", type=int, default=32,
                    help="fetch-grid spacing for win32/jcc32 (32 = the DSB "
                         "window; 64 is the one that separates p14)")
    ap.add_argument("--scr", default="")
    a = ap.parse_args()
    scr = a.scr or os.path.join(REPO, ".temp", "p47", f"clay.in.{os.getpid()}")
    rc = 0
    if a.build:
        rc = build(a.aligns, a.orders)
    if a.time and rc == 0:
        rc = time_pop(a.input, a.reps, a.n_iters, a.cpu, scr)
    if a.modes and rc == 0:
        rc = modes(a.input, a.estimator, a.boundary)
    sys.exit(rc)
