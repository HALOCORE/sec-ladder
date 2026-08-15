#!/usr/bin/env python3
"""Measure a pattern's built matrix into results/pNN-<slug>.json.

Metrics, in the order `.memory/03-measurement.md` ranks them:

  deterministic, primary
    static instruction count -- raw AND padding-excluded, never one alone
    kernel .text bytes, whole-binary .text bytes
    executed instructions: callgrind **per-function exclusive Ir** for the
    kernel symbol. Never the whole-program `summary:` line -- that moves with
    the size of the environment block and does not reproduce across shells,
    while the kernel column is invariant under all of it.

  noisy, secondary
    wall clock: pinned with taskset, cells interleaved round-robin, >=30 reps,
    min and median (never mean). Frequency scaling is on and cannot be disabled
    without root, so this is a sanity check on Ir, not a headline.

Not measurable on this box and not faked: IPC, branch misses, cache misses
(`perf` absent, perf_event_paranoid=3, no root).

  harness/measure.py p01
  harness/measure.py p01 --reps 30 --cpu 3
  harness/measure.py p01 --no-callgrind        # static + wall only
"""

import argparse
import json
import os
import re
import statistics
import subprocess
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "common"))
sys.path.insert(0, os.path.join(REPO, "harness"))
import slb  # noqa: E402
import asm  # noqa: E402
import build as buildmod  # noqa: E402

VALGRIND = os.path.expanduser("~/tools/valgrind/bin/valgrind")
CG_ANNOTATE = os.path.expanduser("~/tools/valgrind/bin/callgrind_annotate")
RESULTS = os.path.join(REPO, "results")

# Callgrind is a ~50x slowdown, so its plan is explicit rather than exhaustive.
# The constraint that shapes it: `.memory/03-measurement.md` forbids reporting a
# static instruction count without a paired `Ir`, and every (opt, mode) pair has
# static counts -- so every (opt, mode) pair gets at least the `small` column.
# `large` is added only at O3, where the perf claims live.
CG_PLAN = [("O0", "isolated", "small.bin"),
           ("O0", "whole", "small.bin"),
           ("O3", "isolated", "small.bin"),
           ("O3", "whole", "small.bin"),
           ("O3", "isolated", "large.bin"),
           ("O3", "whole", "large.bin")]

# Diagnostic inputs, not part of the matrix. See patterns/*/inputs/gen.py.
SKIP_INPUT_PREFIX = "sweep-"


# --------------------------------------------------------------------------

def sh(cmd, timeout=600):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return (r.stdout + r.stderr).strip()
    except (OSError, subprocess.TimeoutExpired) as e:
        return f"<{e}>"


def toolchain():
    return {
        "gcc": sh([buildmod.GCC, "--version"]).splitlines()[0],
        "clang": sh([buildmod.CLANG, "--version"]).splitlines()[0],
        "rustc": sh([buildmod.RUSTC, "--version"]).strip(),
        "rustc_llvm": next((l.strip() for l in
                            sh([buildmod.RUSTC, "--version", "--verbose"]).splitlines()
                            if l.startswith("LLVM")), "?"),
        "verus": sh([sys.executable, os.path.join(REPO, "verus_run.py"), "--info"]),
        "valgrind": sh([VALGRIND, "--version"]),
        "objdump": sh([asm.OBJDUMP, "--version"]).splitlines()[0],
    }


def git_state():
    commit = sh(["git", "-C", REPO, "rev-parse", "HEAD"])
    dirty = sh(["git", "-C", REPO, "status", "--porcelain"])
    return {"commit": commit, "dirty": bool(dirty.strip()),
            "dirty_files": len(dirty.splitlines())}


def host():
    gov = "?"
    p = "/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor"
    if os.path.exists(p):
        gov = open(p).read().strip()
    model = next((l.split(":", 1)[1].strip()
                  for l in open("/proc/cpuinfo") if l.startswith("model name")), "?")
    return {"cpu_model": model, "governor": gov,
            "note": "frequency scaling active, shared container -- wall clock is noisy"}


# --------------------------------------------------------------------------

_CG_ROW = re.compile(r"^\s*([\d,]+)\s*(?:\([^)]*\))?\s+(\S.*)$")


def _sum_rows(ann, needle):
    """callgrind_annotate splits one function across several `file:function`
    rows, so the rows must be added up rather than the first one taken."""
    total, names = 0, []
    for line in ann.splitlines():
        m = _CG_ROW.match(line)
        if not m:
            continue
        rest = m.group(2)
        if ":" not in rest:
            continue
        func = rest.split(":", 1)[1].split(" [")[0].strip()
        if re.search(r"(?:^|::)" + re.escape(needle) + r"(?:$|[^A-Za-z0-9_])", func):
            total += int(m.group(1).replace(",", ""))
            names.append(func)
    return (total, sorted(set(names))) if names else (None, [])


def callgrind_ir(binary, arg, outdir, tag, timeout=3600):
    """Per-function exclusive Ir for `kernel` and for `main`, separately.

    Both are recorded for every cell because which one is meaningful depends on
    the build: in `isolated` the kernel is its own symbol and `kernel` is the
    number; in `whole` at O3 it has been inlined away and only `main` exists; in
    `whole` at O0 nothing inlines, so `main` *excludes* the kernel and quoting it
    alone would understate the cell by ~50x. Recording both makes that visible
    instead of hiding it behind one column."""
    os.makedirs(outdir, exist_ok=True)
    out = os.path.join(outdir, f"cg.{tag}.out")
    r = subprocess.run(
        [VALGRIND, "--tool=callgrind", f"--callgrind-out-file={out}", binary, arg],
        capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        return {"error": f"callgrind exit {r.returncode}: {r.stderr[-200:]}"}
    ann = sh([CG_ANNOTATE, "--threshold=100", out], timeout=timeout)
    rec = {}
    for needle in ("kernel", "main"):
        ir, names = _sum_rows(ann, needle)
        rec[needle + "_exclusive_ir"] = ir
        rec[needle + "_functions"] = names
    if rec["kernel_exclusive_ir"] is None and rec["main_exclusive_ir"] is None:
        return {"error": "neither `kernel` nor `main` found in callgrind output"}
    return rec


def wall(binaries, arg, cpu, reps):
    """Interleaved round-robin timing. `.memory/03-measurement.md`: spreading
    thermal/neighbour drift across all cells beats concentrating it in one."""
    samples = {k: [] for k in binaries}
    for _ in range(reps):
        for k, path in binaries.items():
            t0 = time.perf_counter()
            subprocess.run(["taskset", "-c", str(cpu), path, arg],
                           capture_output=True, timeout=1800)
            samples[k].append(time.perf_counter() - t0)
    out = {}
    for k, s in samples.items():
        mn, md = min(s), statistics.median(s)
        out[k] = {"min_s": mn, "median_s": md, "reps": len(s),
                  "spread_pct": 100.0 * (md - mn) / mn if mn else None}
    return out


# --------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pattern")
    ap.add_argument("--reps", type=int, default=30)
    ap.add_argument("--cpu", type=int, default=3, help="taskset core for timing")
    ap.add_argument("--no-callgrind", action="store_true")
    ap.add_argument("--no-wall", action="store_true")
    ap.add_argument("--cells", default="all", choices=["all", "measured"])
    a = ap.parse_args()

    pdir = buildmod.pattern_dir(a.pattern)
    pid = buildmod.pattern_id(pdir)
    slug = os.path.basename(pdir)
    cells = buildmod.ALL_CELLS if a.cells == "all" else buildmod.MEASURED_CELLS
    indir = os.path.join(pdir, "inputs")
    scratch = os.path.join(REPO, ".temp", "cg", pid)

    doc = {
        "pattern": slug,
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "git": git_state(),
        "toolchain": toolchain(),
        "host": host(),
        "timing_cpu": a.cpu,
        "protocol": {
            "static": "harness/asm.py; raw and padding-excluded both reported",
            "ir": "callgrind per-function exclusive Ir, kernel symbol only; "
                  "whole-program summary deliberately not recorded",
            "wall": f"taskset -c {a.cpu}, interleaved round-robin, {a.reps} reps, "
                    f"min and median; frequency scaling on, shared box",
        },
        "inputs": {},
        "cells": [],
    }

    for f in sorted(os.listdir(indir)):
        if not f.endswith(".bin") or f.startswith(SKIP_INPUT_PREFIX):
            continue
        sf = slb.read(os.path.join(indir, f))
        head, body = slb.head_u64_body(sf.payload[: sf.declared_len])
        doc["inputs"][f] = {"n_iters": sf.n_iters, "declared_len": sf.declared_len,
                            "present": len(sf.payload), "truncated": sf.truncated,
                            "win_len": head, "v_len": len(body)}

    rows = []
    for c in cells:
        for o in buildmod.OPTS:
            for m in buildmod.MODES:
                p = buildmod.out_path(pdir, c, o, m, "unwind")
                if os.path.exists(p):
                    rows.append((c, o, m, p))
                else:
                    doc["cells"].append({"cell": c, "opt": o, "mode": m,
                                         "status": "MISSING BINARY"})

    # ---- static ----------------------------------------------------------
    print(f"static: {len(rows)} cells")
    for c, o, m, p in rows:
        needle = "kernel" if m == "isolated" else "main"
        k = asm.try_kernel(p, needle)
        rec = {"cell": c, "opt": o, "mode": m, "binary": os.path.relpath(p, REPO),
               "asm_symbol_needle": needle,
               "binary_text_bytes": asm.text_size(p), "status": "ok"}
        if k is None:
            rec["status"] = f"no symbol containing {needle!r}"
        else:
            rec["static"] = k.summary()
        doc["cells"].append(rec)

    by_key = {(r["cell"], r["opt"], r["mode"]): r for r in doc["cells"]}

    # ---- checksums -------------------------------------------------------
    for c, o, m, p in rows:
        rec = by_key[(c, o, m)]
        rec["checksum"] = {}
        for name in ("small.bin", "large.bin"):
            f = os.path.join(indir, name)
            if os.path.exists(f):
                r = subprocess.run([p, f], capture_output=True, text=True, timeout=1800)
                rec["checksum"][name] = r.stdout.strip()

    # ---- callgrind -------------------------------------------------------
    if not a.no_callgrind:
        for opt, mode, inp in CG_PLAN:
            f = os.path.join(indir, inp)
            if not os.path.exists(f):
                continue
            for c, o, m, p in rows:
                if (o, m) != (opt, mode):
                    continue
                t0 = time.time()
                res = callgrind_ir(p, f, scratch, f"{c}-{o}-{m}-{inp}")
                rec = by_key[(c, o, m)].setdefault("ir", {})
                rec[inp] = res
                if "error" in res:
                    print(f"  cg {c:18s} {o} {m} {inp:12s} FAILED: {res['error']}")
                else:
                    k, mn = res["kernel_exclusive_ir"], res["main_exclusive_ir"]
                    print(f"  cg {c:18s} {o} {m} {inp:12s} "
                          f"kernel={k if k is None else format(k, ',')} "
                          f"main={mn if mn is None else format(mn, ',')} "
                          f"({time.time() - t0:.0f}s)")

    # ---- wall clock ------------------------------------------------------
    if not a.no_wall:
        for inp in ("small.bin", "large.bin"):
            f = os.path.join(indir, inp)
            if not os.path.exists(f):
                continue
            # O0 rows are never a perf claim (`.memory/02-bench-rules.md`), so
            # only O3 is timed.
            group = {(c, o, m): p for c, o, m, p in rows if o == "O3"}
            print(f"wall: {inp} -- {len(group)} O3 cells x {a.reps} reps, "
                  f"interleaved, pinned to cpu {a.cpu}")
            res = wall(group, f, a.cpu, a.reps)
            for k, v in res.items():
                rec = by_key[k].setdefault("wall", {})
                rec[inp] = v
                if v["spread_pct"] is not None and v["spread_pct"] > 10:
                    rec[inp]["warning"] = ("min-to-median spread > 10% -- "
                                           "`.memory/03-measurement.md` says discard")

    os.makedirs(RESULTS, exist_ok=True)
    out = os.path.join(RESULTS, f"{pid}-{slug.split('-', 1)[1]}.json")
    with open(out, "w") as fh:
        json.dump(doc, fh, indent=2, sort_keys=False)
    print(f"\nwrote {os.path.relpath(out, REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
