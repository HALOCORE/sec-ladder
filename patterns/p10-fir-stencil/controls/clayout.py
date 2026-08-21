#!/usr/bin/env python3
"""LAYOUT POPULATIONS for p10, over the C cells AND over the Rust R4/R5 pair.

`.memory/03-measurement.md`: **no `ns` claim without a layout population**, and
**the byte-identical R4/R5 pair is a smoke alarm, not a floor** -- it is one
biased draw from a fixed `addr % 64` contrast and its median over a population
is ~0 on both patterns that have measured it. Two binaries built from identical
source, differing only in where the linker put the kernel, can differ by up to
27% of wall clock and can flip the sign of a rung comparison.

p10's `ns` question is C-vs-C -- **`c-*-h` minus `c-*`, the price of
`if (shift < VBITS)`** -- so the C population is the one that matters here, and
`common/layout/layout_gen.py` builds only with rustc. This file is p06's
`clayout.py` (which was built for exactly that reason) ported to p10, plus p14's
Rust half so that the R4/R5 null is measured over a population rather than as a
single draw.

    python3 patterns/p10-fir-stencil/controls/clayout.py --lang c    --build
    python3 patterns/p10-fir-stencil/controls/clayout.py --lang c    --time --input small
    python3 patterns/p10-fir-stencil/controls/clayout.py --lang c    --modes --pairs c-gcc:c-gcc-h,c-clang:c-clang-h
    python3 patterns/p10-fir-stencil/controls/clayout.py --lang rust --build --time --modes --pairs unsafe:verus

THE LEVER, for C, is NOT `-falign-functions` (which can change intra-function
padding and so the kernel's own bytes). It is a PAD OBJECT: a translation unit
whose whole content is `asm(".text; .space N")`, linked FIRST, which shifts
every later `.text` symbol by N without touching a byte of `kernel.o`. For Rust
it is `-C llvm-args=-align-all-functions=N` and
`-C link-arg=-Wl,--symbol-ordering-file`, the two `.memory/03-measurement.md`
says work.

CONTROL 1, asserted on every `--build`: `n_fn` and `md5_fn_norel` are
single-valued per cell over the whole population -- i.e. every binary here runs
the SAME instruction stream and differs only in where the linker put it.
`md5_fn` is deliberately NOT the control: it moves at every layout because
`call rel32` displacements move.

WHAT TO QUOTE from `--modes`. `.memory/03-measurement.md` RETRACTS worst-vs-best
range and dominance as layout statistics; neither converges in N. This script
prints the range because the eye wants it, and beside it the two statistics that
do converge: the MEDIAN of the paired distribution and `P(A > B)` over all N^2
cross pairs. Quote those.

⚠ Scratch is PER-PID. Two concurrent jobs sharing one scratch path is how
TASK_049 lost a whole sweep on p14, and TASK_051 repeats the instruction.
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
import slb            # noqa: E402
import loopfit        # noqa: E402

PDIR = os.path.join(REPO, "patterns", "p10-fir-stencil")
COMMON = os.path.join(REPO, "common")
GCC = "/usr/bin/gcc"
CLANG = os.path.expanduser("~/tools/llvm/bin/clang")
RUSTC = os.path.expanduser("~/.cargo/bin/rustc")
NM = os.path.expanduser("~/tools/llvm/bin/llvm-nm")
CFLAGS = ["-std=c99", "-Wall", "-Wextra", "-O3", "-DSLB_ISOLATED"]
RBASE = ["-C", "codegen-units=1", "-C", "opt-level=3",
         "-C", "debug-assertions=off", "--cfg", "slb_isolated"]

C_CELLS = {
    "c-gcc":     (GCC,   "kernel.c"),
    "c-gcc-h":   (GCC,   "kernel_hardened.c"),
    "c-clang":   (CLANG, "kernel.c"),
    "c-clang-h": (CLANG, "kernel_hardened.c"),
}
# p10's `ns` question is not p18's. p18 asked C-vs-C (the price of the hardening
# line); p10's hardening line costs 0.00 Ir on gcc and 1.00 on clang at
# `-O3 isolated` on the accepting domain (and -1.00 / 0.00 at `-O3 whole`;
# ../NOTES.md 4 has all four cells), so the C question is a null and the
# interesting pair is **safe_tuned vs unsafe** -- the rung pair whose `Ir` gap is
# negative, by 323.00 / 603.00 Ir per call at `-O3 isolated` against the SHIPPED
# R4 and 129.00 / 241.00 against the cheapest R4 shown admissible
# (../NOTES.md 8e). `.memory/03-measurement.md` forbids an `ns` claim without a
# layout population, so all four Rust cells are in the population and not just
# the R4/R5 pair.
# ⚠ ONE LANGUAGE PER INVOCATION, so the C and Rust runs are different timing
# sessions and `.memory/00-environment.md` forbids quoting a number across them.
# p10 makes no Rust-vs-C `ns` claim anywhere for exactly that reason.
RUST_CELLS = ("safe_naive", "safe_tuned", "unsafe", "verus")


def outdir(lang):
    return os.path.join(REPO, ".temp", "p10", f"clay-{lang}")


def sh(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, cwd=REPO)


# --------------------------------------------------------------------- C ---

def build_c(pads, out):
    os.makedirs(out, exist_ok=True)
    for cc_name, cc in (("gcc", GCC), ("clang", CLANG)):
        for n in pads:
            src = os.path.join(out, f"pad{n}.c")
            open(src, "w").write(
                f'__asm__(".text\\n.space {n}\\n");\n' if n else "typedef int _x;\n")
            o = os.path.join(out, f"pad{n}.{cc_name}.o")
            r = sh([cc] + CFLAGS + ["-c", src, "-o", o])
            if r.returncode:
                print("pad build failed", n, r.stderr[-300:])
                return 1
    objs = {}
    for cell, (cc, ksrc) in C_CELLS.items():
        tag = "gcc" if cc == GCC else "clang"
        ko = os.path.join(out, f"{cell}.kernel.o")
        do = os.path.join(out, f"{tag}.driver.o")
        mo = os.path.join(out, f"{cell}.main.o")
        for src, dst in ((os.path.join(PDIR, "c", ksrc), ko),
                         (os.path.join(COMMON, "driver.c"), do),
                         (os.path.join(PDIR, "c", "main.c"), mo)):
            r = sh([cc] + CFLAGS + ["-I", COMMON, "-I", os.path.join(PDIR, "c"),
                                    "-c", src, "-o", dst])
            if r.returncode:
                print("obj build failed", cell, src, r.stderr[-400:])
                return 1
        objs[cell] = (cc, tag, ko, do, mo)
    meta = {}
    for cell, (cc, tag, ko, do, mo) in objs.items():
        for n in pads:
            po = os.path.join(out, f"pad{n}.{tag}.o")
            b = os.path.join(out, f"{cell}.p{n}")
            r = sh([cc] + CFLAGS + [po, do, ko, mo, "-o", b])
            if r.returncode:
                print("link failed", cell, n, r.stderr[-300:])
                return 1
            rep = loopfit.kernel_report(b, "kernel")
            meta[f"{cell}|pad|{n}"] = {
                "cell": cell, "bin": b, "lever": "pad", "idx": n,
                "addr": rep["addr"], "n_fn": rep["n_fn"],
                "md5_fn": rep["md5_fn"], "md5_fn_norel": rep["md5_fn_norel"],
                "loops": rep["loops"],
            }
    return finish(meta, out, list(C_CELLS))


# ------------------------------------------------------------------ Rust ---

def build_rust_one(cell, dst, more):
    src = os.path.join(PDIR, cell + ".rs")
    if cell == "verus":
        cmd = [sys.executable, os.path.join(REPO, "verus_run.py"), "--compile",
               src, "-o", dst] + RBASE + list(more)
    else:
        cmd = [RUSTC, "--edition", "2021"] + RBASE + list(more) + [src, "-o", dst]
    r = sh(cmd)
    if r.returncode or not os.path.exists(dst):
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


def build_rust(aligns, orders, out):
    os.makedirs(out, exist_ok=True)
    meta = {}
    for cell in RUST_CELLS:
        made = []
        for k in range(aligns):
            b = os.path.join(out, f"{cell}.align{k}")
            if build_rust_one(cell, b, ["-C", f"llvm-args=-align-all-functions={k}"]):
                made.append(("align", k, b))
        b = os.path.join(out, f"{cell}.shipped0")
        if build_rust_one(cell, b, []):
            made.append(("shipped", 0, b))
        base = b
        if orders and os.path.exists(base):
            syms = text_symbols(base)
            for s in range(1, orders + 1):
                order = list(syms)
                random.Random(1000 * s + len(cell)).shuffle(order)
                f = os.path.abspath(os.path.join(out, f"{cell}.ord{s}.txt"))
                open(f, "w").write("\n".join(order) + "\n")
                bb = os.path.join(out, f"{cell}.order{s}")
                if build_rust_one(cell, bb,
                                  ["-C", f"link-arg=-Wl,--symbol-ordering-file={f}"]):
                    made.append(("order", s, bb))
        for lev, idx, bb in made:
            rep = loopfit.kernel_report(bb, "kernel")
            meta[f"{cell}|{lev}|{idx}"] = {
                "cell": cell, "bin": bb, "lever": lev, "idx": idx,
                "addr": rep["addr"], "n_fn": rep["n_fn"],
                "md5_fn": rep["md5_fn"], "md5_fn_norel": rep["md5_fn_norel"],
                "loops": rep["loops"],
            }
    return finish(meta, out, list(RUST_CELLS))


# --------------------------------------------------------------- shared ---

def finish(meta, out, cells):
    json.dump(meta, open(os.path.join(out, "meta.json"), "w"), indent=1)
    print(f"{'cell':12s} {'#builds':>7s} {'n_fn':>10s} {'md5_fn_norel':>22s} "
          f"{'#md5_fn':>8s}  addrs")
    ok = True
    norel = {}
    for cell in cells:
        ks = [k for k in meta if meta[k]["cell"] == cell]
        if not ks:
            continue
        nf = sorted({meta[k]["n_fn"] for k in ks})
        nr = sorted({meta[k]["md5_fn_norel"] for k in ks})
        fn = sorted({meta[k]["md5_fn"] for k in ks})
        ad = sorted({meta[k]["addr"] for k in ks})
        norel[cell] = nr
        print(f"{cell:12s} {len(ks):7d} {str(nf):>10s} {nr[0][:20]:>22s} "
              f"{len(fn):8d}  {len(ad)} distinct 0x{ad[0]:x}..0x{ad[-1]:x} "
              f"%32={sorted({x % 32 for x in ad})} %64={sorted({x % 64 for x in ad})}")
        ok &= len(nf) == 1 and len(nr) == 1
    print("CONTROL 1 -- kernel machine code invariant modulo pc-rel:", ok)
    if set(cells) == set(RUST_CELLS):
        same = norel.get("unsafe") == norel.get("verus")
        print("           -- verus's kernel bytes == unsafe's:", same)
        ok &= same
    return 0 if ok else 1


def time_pop(stem, reps, n_iters, cpu, out, scr):
    meta = json.load(open(os.path.join(out, "meta.json")))
    keys = sorted(meta)
    os.makedirs(scr, exist_ok=True)
    f = slb.read(os.path.join(PDIR, "inputs", stem + ".bin"))
    big = os.path.join(scr, f"{stem}.big.bin")
    one = os.path.join(scr, f"{stem}.one.bin")
    slb.write(big, n_iters, f.payload[: f.declared_len])
    slb.write(one, 1, f.payload[: f.declared_len])
    # ONE flat interleaved schedule: every cell launched once before any twice
    # (`.memory/03-measurement.md`: blocked ordering alone flipped a sign).
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
            b = meta[k]["bin"]
            a = time.perf_counter()
            subprocess.run(["/usr/bin/taskset", "-c", str(cpu), b, one],
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
          f"elapsed={time.time() - t0:.0f}s")
    print(f"# distinct stdouts over the population: {len(set(outs.values()))}")
    for tag, e in (("min", res), ("median", med)):
        pop = {k: dict(meta[k], **{stem: e[k]}) for k in keys}
        for k in pop:
            pop[k].pop("bin", None)
        json.dump(pop, open(os.path.join(out, f"layout_{stem}_{tag}.json"), "w"),
                  indent=1)
    json.dump({"stem": stem, "n_iters": n_iters, "reps": reps, "cpu": cpu,
               "min": res, "median": med, "raw": samples, "stdout": outs},
              open(os.path.join(out, f"times_{stem}.json"), "w"), indent=1)
    for c in per:
        v = [res[k] for k in per[c]]
        print(f"  {c:12s} n={len(v)}  min-of-reps ns/call {min(v):8.2f}..{max(v):8.2f}"
              f"  spread {100 * (max(v) - min(v)) / min(v):6.2f}%"
              f"  median {statistics.median(v):8.2f}")
    return 0


def floor_pop(stem, reps, n_iters, cpu, out, scr, n, cells):
    """THE IDENTICAL-COPY NOISE FLOOR (`.memory/03-measurement.md`): time N
    byte-identical copies of one binary as a population, under exactly the
    protocol `--time` uses, and compare the spread to the effect. p05's layout
    band turned out to be INSIDE its own noise floor, which is why its `small`
    row is withdrawn; nothing about a layout verdict is believable until this
    number is on the page."""
    meta = json.load(open(os.path.join(out, "meta.json")))
    os.makedirs(scr, exist_ok=True)
    fake = {}
    for cell in cells:
        src = next(meta[k]["bin"] for k in sorted(meta)
                   if meta[k]["cell"] == cell)
        for i in range(n):
            d = os.path.join(scr, f"{cell}.copy{i}")
            with open(src, "rb") as fh:
                data = fh.read()
            with open(d, "wb") as fh:
                fh.write(data)
            os.chmod(d, 0o755)
            fake[f"{cell}|copy|{i}"] = {"cell": cell, "bin": d,
                                        "lever": "copy", "idx": i,
                                        "addr": 0, "n_fn": 0, "md5_fn": "",
                                        "md5_fn_norel": "", "loops": []}
    sub = os.path.join(out, "floor")
    os.makedirs(sub, exist_ok=True)
    json.dump(fake, open(os.path.join(sub, "meta.json"), "w"), indent=1)
    return time_pop(stem, reps, n_iters, cpu, sub, scr)


def _pairs(u, v):
    return [(y / x - 1) * 100 for x in u for y in v]


def modes(stem, tag, boundary, pairs, out):
    path = os.path.join(out, f"layout_{stem}_{tag}.json")
    raw = json.load(open(path))
    meta = json.load(open(os.path.join(out, "meta.json")))
    print(f"# {path}  estimator={tag}-of-reps  stem={stem}  boundary={boundary}")
    if boundary != 32:
        for k in raw:
            raw[k]["loops"] = loopfit.kernel_report(
                meta[k]["bin"], "kernel", boundary=boundary)["loops"]
    cells = sorted({raw[k]["cell"] for k in raw})
    for cell in cells:
        v = [raw[k][stem] for k in raw if raw[k]["cell"] == cell]
        q = statistics.quantiles(v, n=4)
        print(f"  {cell:12s} n={len(v):3d}  ns/call {min(v):7.2f}..{max(v):7.2f}"
              f"  RANGE {100 * (max(v) - min(v)) / min(v):5.2f}%  "
              f"median {statistics.median(v):7.2f}  IQR {q[0]:7.2f}..{q[2]:7.2f}"
              f" ({100 * (q[2] - q[0]) / q[0]:4.2f}%)")
    for pr in pairs:
        a, b = pr.split(":")
        ka = [k for k in raw if raw[k]["cell"] == a]
        kb = [k for k in raw if raw[k]["cell"] == b]
        if not ka or not kb:
            print(f"  pair {pr}: one side is empty")
            continue
        u = [raw[k][stem] for k in ka]
        v = [raw[k][stem] for k in kb]
        paired = []
        for k in kb:
            twin = f"{a}|{raw[k]['lever']}|{raw[k]['idx']}"
            if twin in raw:
                paired.append((raw[k][stem] / raw[twin][stem] - 1) * 100)
        cross = sorted(_pairs(u, v))
        pab = sum(1 for x in u for y in v if y > x) / (len(u) * len(v))
        print(f"\n  {b} vs {a}")
        if paired:
            ps = sorted(paired)
            print(f"    paired by layout  n={len(ps):3d}  "
                  f"range {ps[0]:+6.2f}..{ps[-1]:+6.2f}   "
                  f"MEDIAN {statistics.median(ps):+6.2f}%")
        print(f"    all cross pairs   n={len(cross):4d}  "
              f"range {cross[0]:+6.2f}..{cross[-1]:+6.2f}   "
              f"MEDIAN {statistics.median(cross):+6.2f}%   "
              f"P({b}>{a}) = {pab:.4f}")
        # mode-matched, partitioned from the LISTING (never from an address bit)
        nloops = len(raw[ka[0]]["loops"])
        for li, prop in itertools.product(range(nloops), ("win32", "jcc32")):
            groups = {}
            for k in ka + kb:
                if li >= len(raw[k]["loops"]):
                    continue
                g = raw[k]["loops"][li][prop]
                groups.setdefault(g, {a: [], b: []})
                groups[g][raw[k]["cell"]].append(raw[k][stem])
            if len(groups) < 2 or any(not g[a] or not g[b]
                                      for g in groups.values()):
                continue
            print(f"    loop{li} {prop}:")
            for g in sorted(groups):
                uu, vv = groups[g][a], groups[g][b]
                c = sorted(_pairs(uu, vv))
                p = sum(1 for x in uu for y in vv if y > x) / (len(uu) * len(vv))
                print(f"       {prop}={g}: n={len(uu)}+{len(vv)}  "
                      f"{a} med {statistics.median(uu):.2f} | "
                      f"{b} med {statistics.median(vv):.2f} | "
                      f"med {statistics.median(c):+.2f}%  P={p:.3f}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", choices=("c", "rust"), default="c")
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--time", action="store_true")
    ap.add_argument("--modes", action="store_true")
    ap.add_argument("--input", default="small")
    ap.add_argument("--reps", type=int, default=7)
    ap.add_argument("--n-iters", type=int, default=200000)
    ap.add_argument("--cpu", type=int, default=5)
    ap.add_argument("--pads", default=",".join(str(16 * i) for i in range(30)))
    ap.add_argument("--aligns", type=int, default=9)
    ap.add_argument("--orders", type=int, default=14)
    ap.add_argument("--pairs", default="c-gcc:c-gcc-h,c-clang:c-clang-h")
    ap.add_argument("--estimator", default="min", choices=("min", "median"))
    ap.add_argument("--boundary", type=int, default=32)
    ap.add_argument("--floor", type=int, default=0,
                    help="time N byte-identical COPIES of one binary "
                         "per cell -- the noise floor any layout "
                         "verdict has to clear")
    ap.add_argument("--scr", default="")
    a = ap.parse_args()
    out = outdir(a.lang)
    scr = a.scr or os.path.join(REPO, ".temp", "p10", f"clay.in.{os.getpid()}")
    rc = 0
    if a.build:
        rc = (build_c([int(x) for x in a.pads.split(",")], out) if a.lang == "c"
              else build_rust(a.aligns, a.orders, out))
    if a.time and rc == 0:
        rc = time_pop(a.input, a.reps, a.n_iters, a.cpu, out, scr)
    if a.floor and rc == 0:
        rc = floor_pop(a.input, a.reps, a.n_iters, a.cpu, out, scr, a.floor,
                       (list(C_CELLS) if a.lang == "c" else list(RUST_CELLS)))
    if a.modes and rc == 0:
        rc = modes(a.input, a.estimator, a.boundary,
                   [p for p in a.pairs.split(",") if p], out)
    sys.exit(rc)
