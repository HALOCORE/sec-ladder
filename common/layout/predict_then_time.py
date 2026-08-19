#!/usr/bin/env python3
"""Pre-registration: predict which layouts are slow, hash the prediction, THEN
time.  This is what makes the layout finding falsifiable.

The `win32`/`jcc32` partition was found *after* looking at a 30-layout
population.  A rule fitted on a population and then scored on the same
population is not evidence.  This script runs it the other way round:

  1. draw N FRESH symbol orderings the hypothesis has never seen,
  2. build them and read each kernel's 32-byte loop geometry statically,
  3. WRITE THE PREDICTION FILE AND PRINT ITS SHA-256 -- before a single timing,
  4. only then time, and score.

Rules, one per cell, named on the command line.  All are directional and have
no fitted parameter: more fetch windows / a DSB-evicting branch predicts
SLOWER, never the reverse.

    win32@N      slow <=> loop N occupies more 32-byte fetch windows
    jcc32@N      slow <=> a branch in loop N crosses/ends on a 32-byte boundary
    jcc32        the same, aggregated over every loop in the kernel
    bit4=0slow   slow <=> kernel entry address bit 4 == 0   (the PROXY -- keep
    bit4=1slow   slow <=> kernel entry address bit 4 == 1    it only to falsify
                                                             it against win32)
    none         no mode is predicted at all

Loop indices are the ones `loopfit.py --loops <binary>` prints; the kernel's
bytes are layout-invariant, so they are stable across the whole population.

    python3 common/layout/loopfit.py --loops <a build>      # pick the index
    python3 common/layout/predict_then_time.py --pattern p07-binary-search \\
        --rules safe_naive=jcc32@3,safe_tuned=jcc32@2,unsafe=none
"""
import argparse
import hashlib
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
sys.path.insert(0, HERE)
import layout_gen  # noqa: E402
import loopfit  # noqa: E402

RUSTC = os.path.expanduser("~/.cargo/bin/rustc")
NM = os.path.expanduser("~/tools/llvm/bin/llvm-nm")
BASE = ["--edition", "2021", "-C", "codegen-units=1", "-C", "opt-level=3",
        "-C", "debug-assertions=off", "--cfg", "slb_isolated"]


def sh(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, cwd=REPO)


def score(rule, m):
    """The rule's ORDINAL prediction for one build: higher = predicted slower.
    `None` means the rule predicts no ordering at all."""
    if rule == "none":
        return None
    if rule == "jcc32":
        return loopfit.any_loop_jcc32(m)
    if rule.startswith(("win32@", "jcc32@")):
        prop, li = rule.split("@")
        return m["loops"][int(li)][prop]
    if rule == "bit4=0slow":
        return 1 - ((m["addr"] >> 4) & 1)
    if rule == "bit4=1slow":
        return (m["addr"] >> 4) & 1
    raise SystemExit(f"unknown rule {rule}")


def label(rule, m, lo):
    s = score(rule, m)
    return "flat" if s is None else ("fast" if s == lo else "slow")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pattern", required=True)
    ap.add_argument("--rules", required=True)
    ap.add_argument("--seeds", type=int, default=20)
    ap.add_argument("--seed-base", type=int, default=777000)
    ap.add_argument("--reps", type=int, default=21)
    ap.add_argument("--passes", type=int, default=2)
    ap.add_argument("--cpu", type=int, default=3)
    ap.add_argument("--input", default="small")
    ap.add_argument("--symbol", default="kernel")
    ap.add_argument("--tag", default="")
    ap.add_argument("--out", default=os.path.join(REPO, ".temp", "layout"))
    a = ap.parse_args()

    # split ONCE: `safe_naive=bit4=0slow` must give ("safe_naive","bit4=0slow")
    rules = dict(x.split("=", 1) for x in a.rules.split(","))
    pdir = os.path.join(REPO, "patterns", a.pattern)
    inp = os.path.join(pdir, "inputs", a.input + ".bin")
    os.makedirs(a.out, exist_ok=True)
    scr = os.path.join(a.out, f"pt.{os.getpid()}")
    os.makedirs(scr, exist_ok=True)
    tag = a.tag or a.pattern.split("-")[0]

    bins, meta = {}, {}
    for cell in rules:
        src = os.path.join(pdir, cell + ".rs")
        r = sh([RUSTC] + BASE + [src, "-o", os.path.join(scr, cell + ".base")])
        if r.returncode:
            print((r.stdout + r.stderr)[-400:])
            return 1
        syms = [ln.split()[2]
                for ln in sh([NM, os.path.join(scr, cell + ".base")])
                .stdout.splitlines()
                if len(ln.split()) == 3 and ln.split()[1] in ("t", "T")]
        for s in range(1, a.seeds + 1):
            order = list(syms)
            random.Random(a.seed_base + 31 * s + len(cell)).shuffle(order)
            f = os.path.join(scr, f"{cell}.ord{s}.txt")
            open(f, "w").write("\n".join(order) + "\n")
            dst = os.path.join(scr, f"{cell}.o{s}")
            r = sh([RUSTC] + BASE +
                   ["-C", f"link-arg=-Wl,--symbol-ordering-file={f}",
                    src, "-o", dst])
            if r.returncode == 0:
                bins[(cell, "ord", s)] = dst
                meta[(cell, "ord", s)] = loopfit.kernel_report(dst, a.symbol)

    # ---- PRE-REGISTRATION: written and hashed before a single timing --------
    floor = {}
    for c in rules:
        ss = [score(rules[c], meta[k]) for k in bins if k[0] == c]
        floor[c] = None if ss[0] is None else min(ss)
    pred = {f"{c}|{s}": {"rule": rules[c],
                         "addr": meta[(c, o, s)]["addr"],
                         "bit4": (meta[(c, o, s)]["addr"] >> 4) & 1,
                         "score": score(rules[c], meta[(c, o, s)]),
                         "md5_fn_norel": meta[(c, o, s)]["md5_fn_norel"],
                         "predicted": label(rules[c], meta[(c, o, s)], floor[c])}
            for (c, o, s) in bins}
    pf = os.path.join(a.out, f"predictions_{tag}.json")
    blob = json.dumps(pred, indent=1, sort_keys=True)
    open(pf, "w").write(blob)
    print(f"PRE-REGISTERED {pf}")
    print(f"  sha256 {hashlib.sha256(blob.encode()).hexdigest()}")
    for c in rules:
        ps = [pred[f"{c}|{s}"]["predicted"] for (cc, o, s) in bins if cc == c]
        print(f"  {c:12s} rule={rules[c]:11s} predicted "
              f"slow={ps.count('slow')} fast={ps.count('fast')} "
              f"flat={ps.count('flat')}")
        nr = {meta[k]["md5_fn_norel"] for k in bins if k[0] == c}
        print(f"  {c:12s} control: md5_fn_norel {sorted(nr)} "
              f"({len(nr)} distinct -- must be 1)")

    # ---- now time, interleaved BY CELL (layout_gen.round_robin) -------------
    sched = layout_gen.round_robin(sorted(bins))
    print(f"\nschedule: {len(sched)} launches/rep, first six cells "
          f"{[k[0] for k in sched[:6]]} (must alternate)")
    res = {}
    for p in range(a.passes):
        samples = {k: [] for k in bins}
        t0 = time.time()
        for _ in range(a.reps):
            for k in sched:
                t = time.perf_counter()
                subprocess.run(["taskset", "-c", str(a.cpu), bins[k], inp],
                               capture_output=True, timeout=900)
                samples[k].append(time.perf_counter() - t)
        res[p] = {k: min(v) * 1e3 for k, v in samples.items()}
        print(f"\n== pass {p}, {a.reps} reps, cpu {a.cpu}, "
              f"{time.time()-t0:.0f}s ==")
        for c in rules:
            g = {}
            for (cc, o, s), v in res[p].items():
                if cc == c:
                    g.setdefault(pred[f"{c}|{s}"]["predicted"], []).append(v)
            desc = "  ".join(f"{kk}: n={len(v)} med {statistics.median(v):7.3f} "
                             f"[{min(v):7.3f}..{max(v):7.3f}]"
                             for kk, v in sorted(g.items()))
            verdict = ""
            if "slow" in g and "fast" in g:
                sep = max(g["fast"]) < min(g["slow"])
                ratio = statistics.median(g["slow"]) / statistics.median(g["fast"])
                verdict = (f"  -> x{ratio:.4f}  "
                           f"{'PREDICTION HELD (perfect separation)' if sep else 'OVERLAP'}")
            elif "flat" in g:
                v = g["flat"]
                verdict = (f"  -> spread "
                           f"{100*(max(v)-min(v))/min(v):.2f}% (no mode predicted)")
            print(f"  {c:12s} {desc}{verdict}")

    json.dump({f"{k[0]}|{k[2]}": {"pass%d" % p: res[p][k] for p in res}
               | pred[f"{k[0]}|{k[2]}"] for k in bins},
              open(os.path.join(a.out, f"predtimes_{tag}.json"), "w"),
              indent=1, sort_keys=True)
    shutil.rmtree(scr, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
