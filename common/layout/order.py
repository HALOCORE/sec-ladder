#!/usr/bin/env python3
"""The two controls without which no population number can be believed:
the round-robin's ORDER, and the identical-copy NOISE FLOOR.

Holds the CODE constant -- N byte-identical copies of each rung at one fixed
(shipped) layout, distinct inodes -- and varies only the schedule.  Anything
that moves is therefore not layout, not the binaries and not the source.

Three schedules are timed:

    alt   ALTERNATING, one launch per cell per round      (harness/measure.py)
    blk   BLOCKED, a contiguous run of every copy of a cell   (the BUG)
    gen   whatever `layout_gen.round_robin` actually produces -- imported, not
          re-implemented, so this is a test of the shipped scheduler

`gen` must agree with `alt`.  If it agrees with `blk` instead, the population
builder is blocking and every cross-cell percentage it produces is suspect:
measured at TASK_031 on p05, 31 identical copies, one layout, R3-vs-R4 read
**+1.21% alternating and -4.16% blocked**, and -11.70% at slot 0 of a block,
which is where a "shipped" build naturally lands.

The second output is the NOISE FLOOR: the spread over N byte-identical copies.
An effect smaller than that floor is not an effect.  p05's 30-layout "band"
(14.09 / 8.30 / 9.34%) is inside its own 5.09-45.04% identical-copy floor,
which is why its `small` wall-clock row is withdrawn; p01's and p07's floors
are 0.82-3.17% and 0.83-2.24% against 7.7-31.8% bands, which is why theirs are
withdrawn for a real reason.

    python3 common/layout/order.py --pattern p05-index-flatten --copies 31
    python3 common/layout/order.py --pattern p01-array-sum --orders alt,gen
"""
import argparse
import os
import shutil
import statistics
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import layout_gen  # noqa: E402

RUSTC = os.path.expanduser("~/.cargo/bin/rustc")
BASE = ["--edition", "2021", "-C", "codegen-units=1", "-C", "opt-level=3",
        "-C", "debug-assertions=off", "--cfg", "slb_isolated"]
CELLS = ["safe_naive", "safe_tuned", "unsafe"]


def sequence(order, cells, n):
    """`[(cell, 'copy', i), ...]` in the order the processes will be launched."""
    keys = [(c, "copy", i) for c in cells for i in range(n)]
    if order == "alt":
        return [(c, "copy", i) for i in range(n) for c in cells]
    if order == "blk":
        return keys
    if order == "gen":
        return layout_gen.round_robin(keys)
    raise SystemExit(f"unknown order {order}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pattern", default="p05-index-flatten")
    ap.add_argument("--input", default="small")
    ap.add_argument("--copies", type=int, default=31)
    ap.add_argument("--reps", type=int, default=31)
    ap.add_argument("--passes", type=int, default=2)
    ap.add_argument("--orders", default="alt,blk,gen")
    ap.add_argument("--cpu", type=int, default=3)
    ap.add_argument("--out", default=os.path.join(REPO, ".temp", "layout"))
    a = ap.parse_args()

    pdir = os.path.join(REPO, "patterns", a.pattern)
    inp = os.path.join(pdir, "inputs", a.input + ".bin")
    os.makedirs(a.out, exist_ok=True)
    scr = os.path.join(a.out, f"ord.{os.getpid()}")
    os.makedirs(scr, exist_ok=True)
    orders = a.orders.split(",")
    try:
        paths = {}
        for c in CELLS:
            dst = os.path.join(scr, f"{c}.0")
            r = subprocess.run([RUSTC] + BASE + [os.path.join(pdir, c + ".rs"),
                                                 "-o", dst],
                               capture_output=True, text=True, cwd=REPO)
            if r.returncode:
                print((r.stdout + r.stderr)[-400:])
                return 1
            paths[(c, "copy", 0)] = dst
            for i in range(1, a.copies):
                p = os.path.join(scr, f"{c}.{i}")
                shutil.copyfile(dst, p)
                os.chmod(p, 0o755)
                paths[(c, "copy", i)] = p

        print(f"{a.pattern}  {a.input}.bin  cpu {a.cpu}  reps {a.reps}  "
              f"{a.copies} identical copies/rung = {3*a.copies} files, "
              f"ONE fixed (shipped) layout")
        for o in orders:
            heads = [k[0] for k in sequence(o, CELLS, a.copies)[:6]]
            print(f"  schedule {o:3s} first six cells {heads}")
        for pi in range(a.passes):
            for order in orders:
                seq = sequence(order, CELLS, a.copies)
                s = {k: [] for k in paths}
                t0 = time.time()
                for _ in range(a.reps):
                    for k in seq:
                        t = time.perf_counter()
                        subprocess.run(["taskset", "-c", str(a.cpu),
                                        paths[k], inp],
                                       capture_output=True, timeout=900)
                        s[k].append(time.perf_counter() - t)
                m = {}
                for c in CELLS:
                    m[c] = [min(s[(c, "copy", i)]) * 1e3
                            for i in range(a.copies)]
                r2 = 100 * (statistics.median(m["safe_naive"])
                            - statistics.median(m["unsafe"])) \
                    / statistics.median(m["unsafe"])
                r3 = 100 * (statistics.median(m["safe_tuned"])
                            - statistics.median(m["unsafe"])) \
                    / statistics.median(m["unsafe"])
                lbl = {"alt": "ALTERNATING (harness/measure.py)",
                       "blk": "BLOCKED (the bug)",
                       "gen": "layout_gen.round_robin (SHIPPED)"}[order]
                print(f"\n--- pass {pi}  order {order}  {lbl}  "
                      f"{time.time()-t0:.0f}s ---")
                for c in CELLS:
                    v = m[c]
                    rank = sorted(v).index(v[0])
                    print(f"  {c:12s} median {statistics.median(v):7.3f} ms  "
                          f"range {min(v):7.3f}..{max(v):7.3f}  "
                          f"NOISE FLOOR {100*(max(v)-min(v))/min(v):6.2f}%  "
                          f"copy#0 {v[0]:7.3f} ms  rank {rank}/{len(v)-1}")
                    print("    by position: "
                          + " ".join(f"{x:.3f}" for x in v))
                print(f"  R2 vs R4 (medians) {r2:+7.2f}%     "
                      f"R3 vs R4 (medians) {r3:+7.2f}%")
                print(f"  R2 vs R4 (copy#0)  "
                      f"{100*(m['safe_naive'][0]-m['unsafe'][0])/m['unsafe'][0]:+7.2f}%"
                      f"     R3 vs R4 (copy#0)  "
                      f"{100*(m['safe_tuned'][0]-m['unsafe'][0])/m['unsafe'][0]:+7.2f}%")
    finally:
        shutil.rmtree(scr, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
