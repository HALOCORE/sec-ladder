#!/usr/bin/env python3
"""Build one pattern's Rust rungs at a POPULATION of code layouts, and time it.

A single-layout wall-clock number is a sample of size one from a distribution
the source does not determine.  This builds ~30 layouts per rung with two
levers --

    -C llvm-args=-align-all-functions=K            (weak; moves inside 0x300)
    -C link-arg=-Wl,--symbol-ordering-file=<perm>  (strong; arbitrary)

-- asserts the controls that make the population a *layout* population and not
a source population, records each build's 32-byte loop geometry
(`loopfit.kernel_report`), and times every binary in one interleaved,
CPU-pinned round-robin.

CONTROLS, all printed and all falsifiable:
  1. `md5_fn_norel` and `n_fn` single-valued per rung -- the kernel's machine
     code is byte-identical modulo pc-relative displacements at every layout.
     **`md5_fn` is NOT usable here**: a kernel that can `call` a panic path
     gets a different `md5_fn` at every layout because the `call rel32`
     displacement moves, and it gave 28-29 distinct digests over 30 layouts on
     every pattern this has been run on (`.memory/03-measurement.md`).
  2. stdout identical at every layout, per input.
  3. (`--ir`) callgrind whole-program totals invariant over layouts.

⚠ INTERLEAVE BY CELL, NEVER BY BLOCK.  See `round_robin` below.  The version of
this file that shipped as `.temp/r30/layout_gen.py` timed with
`for k, b in bins.items()` over a dict filled cell-by-cell, which gives each
cell a contiguous block of every rep while the docstring and the log both say
"interleaved".  That alone flipped the sign of a rung-to-rung comparison on
BYTE-IDENTICAL binaries and manufactured a reviewer's blocker (TASK_031).
`order.py` is the control that catches it; run it before believing a number.

    python3 common/layout/layout_gen.py --pattern p01-array-sum --tag p01
    python3 common/layout/layout_gen.py --pattern p07-binary-search \\
        --seeds 21 --aligns 9 --reps 31 --passes 2 --cpu 3
"""
import argparse
import json
import os
import random
import shutil
import statistics
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "harness"))
sys.path.insert(0, HERE)
import loopfit  # noqa: E402

RUSTC = os.path.expanduser("~/.cargo/bin/rustc")
NM = os.path.expanduser("~/tools/llvm/bin/llvm-nm")
VG = os.path.expanduser("~/tools/valgrind/bin/valgrind")
BASE = ["--edition", "2021", "-C", "codegen-units=1", "-C", "opt-level=3",
        "-C", "debug-assertions=off", "--cfg", "slb_isolated"]
CELLS = ["safe_naive", "safe_tuned", "unsafe"]


def round_robin(keys):
    """A FLAT interleaved schedule: every cell is visited once before any cell
    is visited twice.

    THE RULE (`.memory/03-measurement.md`, "Interleave by CELL, never by
    block").  `harness/measure.py:wall()` gets this right by accident -- its
    dict holds exactly one binary per cell, so iterating it *is* alternating.
    Here the dict holds ~31 binaries per cell, so the identical idiom
    (`for k, b in bins.items()`) blocks instead, and a per-cell block absorbs
    whatever drifts on the scale of a block: on p05, byte-identical copies read
    R3-vs-R4 as +1.21% alternating and -4.16% blocked, and slot 0 of a block
    (which is where a "shipped" build naturally lands) as -11.70%.

    `keys` are `(cell, lever, idx)`; grouping is by `key[0]`, in first-seen
    order, and cells with unequal build counts are simply exhausted late."""
    per = {}
    for k in keys:
        per.setdefault(k[0], []).append(k)
    out = []
    for i in range(max(len(v) for v in per.values())):
        for c in per:
            if i < len(per[c]):
                out.append(per[c][i])
    return out


def sh(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, cwd=REPO, **kw)


def text_symbols(binary):
    syms = []
    for line in sh([NM, binary]).stdout.splitlines():
        f = line.split()
        if len(f) == 3 and f[1] in ("t", "T"):
            syms.append(f[2])
    return syms


def total_ir(binary, inp, scr):
    o = os.path.join(scr, "cg.out")
    subprocess.run([VG, "--tool=callgrind", f"--callgrind-out-file={o}",
                    binary, inp], capture_output=True, cwd=REPO)
    v = None
    for line in open(o):
        if line.startswith(("summary:", "totals:")):
            v = int(line.split()[1])
    return v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pattern", required=True)
    ap.add_argument("--cells", default=",".join(CELLS))
    ap.add_argument("--seeds", type=int, default=21)
    ap.add_argument("--aligns", type=int, default=9)
    ap.add_argument("--reps", type=int, default=31)
    ap.add_argument("--passes", type=int, default=1,
                    help="independent timing passes; a real per-binary effect "
                         "must reproduce across them")
    ap.add_argument("--cpu", type=int, default=3)
    ap.add_argument("--cpu2", type=int, default=None,
                    help="second CPU; one extra pass is run there")
    ap.add_argument("--inputs", default="small,large")
    ap.add_argument("--extra", default="", help="extra rustc flags, ;-separated")
    ap.add_argument("--seed-base", type=int, default=1000)
    ap.add_argument("--ir", action="store_true", help="callgrind Ir per layout")
    ap.add_argument("--symbol", default="kernel")
    ap.add_argument("--tag", default="")
    ap.add_argument("--out", default=os.path.join(REPO, ".temp", "layout"),
                    help="where layout_<tag>.json is written")
    ap.add_argument("--keep", action="store_true")
    a = ap.parse_args()

    pdir = os.path.join(REPO, "patterns", a.pattern)
    inputs = os.path.join(pdir, "inputs")
    cells = a.cells.split(",")
    os.makedirs(a.out, exist_ok=True)
    scr = os.path.join(a.out, f"b.{os.getpid()}")
    os.makedirs(scr, exist_ok=True)
    extra = [x for x in a.extra.split(";") if x]
    print(f"scratch {scr}   pattern {a.pattern}   extra {extra}")

    bins, meta = {}, {}
    for cell in cells:
        src = os.path.join(pdir, cell + ".rs")

        def build(tag, more):
            dst = os.path.join(scr, f"{cell}.{tag}")
            r = sh([RUSTC] + BASE + extra + list(more) + [src, "-o", dst])
            if r.returncode:
                print(f"  FAIL {cell}.{tag}: {(r.stdout+r.stderr)[-400:]}")
                return None
            return dst

        base = build("base", [])
        if base is None:
            return 1
        # the SHIPPED layout: exactly harness/build.py's O3/isolated flags, no
        # layout lever at all.  Timed inside the same round-robin as the
        # population so "published vs population" is not a cross-harness
        # comparison.  With `round_robin` it is no longer slot 0 of a block.
        bins[(cell, "shipped", 0)] = base
        syms = text_symbols(base)
        for k in range(a.aligns):
            p = build(f"a{k}", ["-C", f"llvm-args=-align-all-functions={k}"])
            if p:
                bins[(cell, "align", k)] = p
        for s in range(1, a.seeds + 1):
            order = list(syms)
            random.Random(a.seed_base * s + len(cell)).shuffle(order)
            f = os.path.join(scr, f"{cell}.ord{s}.txt")
            open(f, "w").write("\n".join(order) + "\n")
            p = build(f"o{s}", ["-C", f"link-arg=-Wl,--symbol-ordering-file={f}"])
            if p:
                bins[(cell, "order", s)] = p
        print(f"  {cell}: {len(syms)} text symbols, "
              f"{sum(1 for k in bins if k[0] == cell)} builds")

    # ---- controls -----------------------------------------------------------
    print("\nCONTROL 1 -- kernel machine code identical modulo pc-rel "
          "(md5_fn_norel) at every layout:")
    ok = True
    for key, b in sorted(bins.items()):
        meta[key] = loopfit.kernel_report(b, a.symbol)
    for cell in cells:
        ks = [k for k in meta if k[0] == cell]
        nr = sorted({meta[k]["md5_fn_norel"] for k in ks})
        fn = sorted({meta[k]["md5_fn"] for k in ks})
        nn = sorted({meta[k]["n_fn"] for k in ks})
        ad = sorted({meta[k]["addr"] for k in ks})
        print(f"  {cell:12s} n_fn {nn}  md5_fn_norel {nr}  "
              f"(#distinct md5_fn {len(fn)})")
        print(f"  {cell:12s} {len(ad)} distinct addrs 0x{ad[0]:x}..0x{ad[-1]:x}"
              f"  addr%16 {sorted({x % 16 for x in ad})}"
              f"  addr%32 {sorted({x % 32 for x in ad})}")
        ok &= (len(nr) == 1 and len(nn) == 1)
    print(f"  => byte-identical modulo pc-rel: {ok}")

    print("\nCONTROL 2 -- program output identical at every layout:")
    for cell in cells:
        outs = set()
        for k in [k for k in bins if k[0] == cell]:
            for stem in a.inputs.split(","):
                r = sh([bins[k], os.path.join(inputs, stem + ".bin")])
                outs.add((stem, r.stdout.strip()[-80:]))
        print(f"  {cell:12s} {len(outs)} distinct (input, tail-of-stdout) pairs "
              f"[expect {len(a.inputs.split(','))}]")

    if a.ir:
        print("\nCONTROL 3 -- executed instruction count (callgrind totals) "
              "invariant over layouts, small.bin:")
        inp = os.path.join(inputs, "small.bin")
        for cell in cells:
            vs = {}
            for k in [k for k in bins if k[0] == cell]:
                vs[k] = total_ir(bins[k], inp, scr)
            u = sorted(set(vs.values()))
            print(f"  {cell:12s} {len(vs)} layouts -> {len(u)} distinct Ir: "
                  f"{u if len(u) <= 4 else [u[0], '...', u[-1]]}")

    print("\nSTATIC 32-BYTE GEOMETRY per loop (loopfit; every loop, no "
          "'inner loop' heuristic):")
    for cell in cells:
        loops = meta[(cell, "shipped", 0)]["loops"]
        for li, L in enumerate(loops):
            tab = {}
            for k in sorted(meta):
                if k[0] != cell:
                    continue
                g = meta[k]["loops"][li]
                key = (g["win32"], g["jcc32"])
                tab[key] = tab.get(key, 0) + 1
            print(f"  {cell:12s} loop{li} [+{L['lo']:#x},+{L['hi']:#x}) "
                  f"{L['bytes']:3d}B  (win32,jcc32)->count "
                  f"{ {f'{w}/{j}': c for (w, j), c in sorted(tab.items())} }")

    # ---- time ---------------------------------------------------------------
    # ONE flat interleaved schedule, built once and reused for every rep, so
    # consecutive process launches alternate cells.  See `round_robin`.
    sched = round_robin(sorted(bins))
    heads = [k[0] for k in sched[:6]]
    print(f"\nschedule: {len(sched)} launches/rep, first six cells {heads} "
          f"(must alternate)")
    passes = [(p, a.cpu) for p in range(a.passes)]
    if a.cpu2 is not None:
        passes.append((a.passes, a.cpu2))
    res = {}
    for stem in a.inputs.split(","):
        path = os.path.join(inputs, stem + ".bin")
        for pi, cpu in passes:
            samples = {k: [] for k in bins}
            t0 = time.time()
            for _ in range(a.reps):
                for k in sched:
                    t = time.perf_counter()
                    subprocess.run(["taskset", "-c", str(cpu), bins[k], path],
                                   capture_output=True, timeout=900)
                    samples[k].append(time.perf_counter() - t)
            name = stem if pi == 0 else f"{stem}#p{pi}c{cpu}"
            res[name] = {k: min(v) * 1e3 for k, v in samples.items()}
            print(f"\n===== {stem}.bin pass {pi} cpu {cpu}, {a.reps} reps "
                  f"interleaved by cell, {time.time()-t0:.0f}s =====")
            for cell in cells:
                v = [res[name][k] for k in bins if k[0] == cell]
                print(f"  {cell:12s} n={len(v)}  {min(v):8.3f}..{max(v):8.3f} ms"
                      f"  spread {100*(max(v)-min(v))/min(v):6.2f}%  "
                      f"median {statistics.median(v):8.3f}")

    tag = a.tag or a.pattern.split("-")[0]
    out = os.path.join(a.out, f"layout_{tag}.json")
    json.dump({f"{k[0]}|{k[1]}|{k[2]}": {
        **{s: res[s][k] for s in res},
        "addr": meta[k]["addr"], "n_fn": meta[k]["n_fn"],
        "md5_fn": meta[k]["md5_fn"], "md5_fn_norel": meta[k]["md5_fn_norel"],
        "n_branch_fn": meta[k]["n_branch_fn"], "n_hit_fn": meta[k]["n_hit_fn"],
        "loops": meta[k]["loops"]} for k in bins},
        open(out, "w"), indent=1, sort_keys=True)
    print(f"\nwrote {out}")
    if not a.keep:
        shutil.rmtree(scr, ignore_errors=True)
        print(f"removed {scr}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
