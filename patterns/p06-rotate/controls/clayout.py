#!/usr/bin/env python3
"""A LAYOUT POPULATION for p06's C cells.

BUILT AT TASK_047_REVIEW (clean negative CN-1) and moved into the pattern at
TASK_048, because ../NOTES.md 3c now PUBLISHES numbers derived from it and a
published number whose generator lives only in gitignored scratch is the
self-certifying trap one level down.

`common/layout/layout_gen.py` and `order.py` build with rustc and hardcode
CELLS = ["safe_naive","safe_tuned","unsafe"], so neither can touch c-gcc /
c-gcc-h / c-clang / c-clang-h.  p06's headline (R1h - R1) is C-vs-C, so before
TASK_047_REVIEW it had never been checked against a layout population.

The lever here is NOT -falign-functions (which can change intra-function
padding and so the kernel's own bytes).  It is a PAD OBJECT: a translation unit
whose whole content is `asm(".text; .space N")`, linked FIRST, which shifts
every later .text symbol by N without touching a byte of kernel.o.  The control
that licenses it is the same one layout_gen asserts: n_fn and md5_fn_norel
single-valued per cell over the whole population.

    python3 patterns/p06-rotate/controls/clayout.py --build
    python3 patterns/p06-rotate/controls/clayout.py --time --input small --reps 7

`--time` reports BOTH estimators; ../NOTES.md quotes the median over layouts of
the per-layout MIN of `reps` (`times_*.json`'s `min` key), which is the
`.memory/03-measurement.md` convention.
"""
import argparse
import hashlib
import json
import os
import shutil
import statistics
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(REPO, "harness"))
sys.path.insert(0, os.path.join(REPO, "common"))
sys.path.insert(0, os.path.join(REPO, "common", "layout"))
import slb            # noqa: E402
import loopfit        # noqa: E402

PDIR = os.path.join(REPO, "patterns", "p06-rotate")
COMMON = os.path.join(REPO, "common")
OUT = os.path.join(REPO, ".temp", "p06", "clay")
GCC = "/usr/bin/gcc"
CLANG = os.path.expanduser("~/tools/llvm/bin/clang")
CFLAGS = ["-std=c99", "-Wall", "-Wextra", "-O3", "-DSLB_ISOLATED"]

CELLS = {
    "c-gcc":     (GCC,   "kernel.c"),
    "c-gcc-h":   (GCC,   "kernel_hardened.c"),
    "c-clang":   (CLANG, "kernel.c"),
    "c-clang-h": (CLANG, "kernel_hardened.c"),
}


def sh(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, cwd=REPO)


def build(pads, extra_kernels):
    os.makedirs(OUT, exist_ok=True)
    cells = dict(CELLS)
    for name, (cc, ksrc) in extra_kernels.items():
        cells[name] = (cc, ksrc)
    # pad objects
    for cc_name, cc in (("gcc", GCC), ("clang", CLANG)):
        for n in pads:
            src = os.path.join(OUT, f"pad{n}.c")
            open(src, "w").write(
                f'__asm__(".text\\n.space {n}\\n");\n' if n else "typedef int _x;\n")
            o = os.path.join(OUT, f"pad{n}.{cc_name}.o")
            r = sh([cc] + CFLAGS + ["-c", src, "-o", o])
            if r.returncode:
                print("pad build failed", n, r.stderr[-300:]);  return 1
    # per-cell object files
    objs = {}
    for cell, (cc, ksrc) in cells.items():
        tag = "gcc" if cc == GCC else "clang"
        ko = os.path.join(OUT, f"{cell}.kernel.o")
        do = os.path.join(OUT, f"{tag}.driver.o")
        mo = os.path.join(OUT, f"{cell}.main.o")
        kpath = ksrc if os.path.isabs(ksrc) else os.path.join(PDIR, "c", ksrc)
        for src, dst in ((kpath, ko),
                         (os.path.join(COMMON, "driver.c"), do),
                         (os.path.join(PDIR, "c", "main.c"), mo)):
            r = sh([cc] + CFLAGS + ["-I", COMMON, "-I", os.path.join(PDIR, "c"),
                                    "-c", src, "-o", dst])
            if r.returncode:
                print("obj build failed", cell, src, r.stderr[-400:]); return 1
        objs[cell] = (cc, tag, ko, do, mo)
    # link at every pad
    meta = {}
    for cell, (cc, tag, ko, do, mo) in objs.items():
        for n in pads:
            po = os.path.join(OUT, f"pad{n}.{tag}.o")
            b = os.path.join(OUT, f"{cell}.p{n}")
            r = sh([cc] + CFLAGS + [po, do, ko, mo, "-o", b])
            if r.returncode:
                print("link failed", cell, n, r.stderr[-300:]); return 1
            rep = loopfit.kernel_report(b, "kernel")
            meta[f"{cell}|{n}"] = {
                "cell": cell, "pad": n, "addr": rep["addr"], "n_fn": rep["n_fn"],
                "md5_fn": rep["md5_fn"], "md5_fn_norel": rep["md5_fn_norel"],
                "loops": rep["loops"],
            }
    json.dump(meta, open(os.path.join(OUT, "meta.json"), "w"), indent=1)
    # controls
    print(f"{'cell':12s} {'#builds':>7s} {'n_fn':>18s} {'md5_fn_norel':>22s} "
          f"{'#distinct md5_fn':>17s}  addrs")
    ok = True
    for cell in objs:
        ks = [k for k in meta if meta[k]["cell"] == cell]
        nf = sorted({meta[k]["n_fn"] for k in ks})
        nr = sorted({meta[k]["md5_fn_norel"] for k in ks})
        fn = sorted({meta[k]["md5_fn"] for k in ks})
        ad = sorted({meta[k]["addr"] for k in ks})
        print(f"{cell:12s} {len(ks):7d} {str(nf):>18s} {str(nr):>22s} "
              f"{len(fn):17d}  {len(ad)} distinct 0x{ad[0]:x}..0x{ad[-1]:x} "
              f"%32={sorted({x % 32 for x in ad})}")
        ok &= len(nf) == 1 and len(nr) == 1
    print("CONTROL 1 byte-identical modulo pc-rel:", ok)
    return 0


def time_pop(stem, reps, n_iters, cpu, cells):
    meta = json.load(open(os.path.join(OUT, "meta.json")))
    keys = [k for k in sorted(meta) if meta[k]["cell"] in cells]
    scratch = os.path.join(OUT, "in")
    os.makedirs(scratch, exist_ok=True)
    f = slb.read(os.path.join(PDIR, "inputs", stem + ".bin"))
    big = os.path.join(scratch, f"{stem}.big.bin")
    one = os.path.join(scratch, f"{stem}.one.bin")
    slb.write(big, n_iters, f.payload[: f.declared_len])
    slb.write(one, 1, f.payload[: f.declared_len])
    # ONE flat interleaved schedule: every cell launched once before any twice.
    per = {}
    for k in keys:
        per.setdefault(meta[k]["cell"], []).append(k)
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
            b = os.path.join(OUT, f"{meta[k]['cell']}.p{meta[k]['pad']}")
            a = time.perf_counter()
            r1 = subprocess.run(["/usr/bin/taskset", "-c", str(cpu), b, one],
                                capture_output=True, text=True)
            b1 = time.perf_counter()
            r2 = subprocess.run(["/usr/bin/taskset", "-c", str(cpu), b, big],
                                capture_output=True, text=True)
            c1 = time.perf_counter()
            outs.setdefault(k, r2.stdout.strip())
            samples[k].append(((c1 - b1) - (b1 - a)) / (n_iters - 1) * 1e9)
    res = {k: min(v) for k, v in samples.items()}
    med = {k: statistics.median(v) for k, v in samples.items()}
    print(f"# stem={stem} n_iters={n_iters} reps={reps} cpu={cpu} "
          f"schedule=alternating estimator=(t(N)-t(1))/(N-1) "
          f"elapsed={time.time()-t0:.0f}s")
    json.dump({"stem": stem, "n_iters": n_iters, "reps": reps,
               "min": res, "median": med,
               "raw": samples, "stdout": outs},
              open(os.path.join(OUT, f"times_{stem}.json"), "w"), indent=1)
    for c in per:
        v = [res[k] for k in per[c]]
        print(f"  {c:12s} n={len(v)}  min-of-reps ns/call "
              f"{min(v):8.2f}..{max(v):8.2f}  spread {100*(max(v)-min(v))/min(v):6.2f}%"
              f"  median {statistics.median(v):8.2f}")
    print("  distinct stdouts per cell:",
          {c: len({outs[k] for k in per[c]}) for c in per})
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--time", action="store_true")
    ap.add_argument("--input", default="small")
    ap.add_argument("--reps", type=int, default=7)
    ap.add_argument("--n-iters", type=int, default=200000)
    ap.add_argument("--cpu", type=int, default=5)
    ap.add_argument("--pads", default=",".join(str(16 * i) for i in range(30)))
    ap.add_argument("--cells", default=",".join(CELLS))
    ap.add_argument("--extra", default="",
                    help="name=cc:kernelpath,... extra cells")
    a = ap.parse_args()
    extra = {}
    for item in [x for x in a.extra.split(",") if x]:
        name, rest = item.split("=", 1)
        cc, path = rest.split(":", 1)
        extra[name] = (GCC if cc == "gcc" else CLANG, path)
    pads = [int(x) for x in a.pads.split(",")]
    rc = 0
    if a.build:
        rc = build(pads, extra)
    if a.time and rc == 0:
        rc = time_pop(a.input, a.reps, a.n_iters, a.cpu, a.cells.split(","))
    sys.exit(rc)
