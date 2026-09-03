#!/usr/bin/env python3
"""The two published bound-site numbers, re-derived — WITH THEIR CONTROLS.

    python3 common/census/bound_sites.py            # both checks; exit 1 on a move
    python3 common/census/bound_sites.py --ladder   # just the site census
    python3 common/census/bound_sites.py --pvalue   # just the size-matched p
    python3 common/census/bound_sites.py --build-corpus   # the slow half, once

`results/SYNTHESIS.md` §7 publishes two figures that until TASK_170 rested on
instruments living **only in gitignored `.temp/`**:

  * *"`0 of 255` bound sites"* — `TASK_129`'s classifier, now
    `common/census/census_c.py`; at 33 kernels it is **0 of 464**;
  * *"`p ≈ 0.06`"* — `TASK_131`'s size-matched null probability, this file's
    second half; at 33 kernels it is **0.0123**.

⚠⚠ **A PROMOTION THAT DOES NOT CHECK ANYTHING IS A COPY.** `census_filelists.py`
is the precedent and the standard: it rebuilds `TASK_129`'s corpus population
from the committed manifests, reproduces `299 / 94 / 2162` and **exits 1 if any
of them moves**. So each half here carries its own 26-pattern CONTROL, and the
33-pattern figure is only reported if the 26-pattern one still reproduces:

  | population        | sites | `ptr_offset` | site-carrying fns | files |
  |-------------------|------:|-------------:|------------------:|------:|
  | 26 (the published caveat's) |  255 |  0 |  30 | 26 |
  | 33 (today)                  |  464 |  0 |  40 | 33 |

  | population | expected walkers (cgnu, size-matched) | `P(zero)` |
  |------------|--------------------------------------:|----------:|
  | 26         | 2.66 | 0.0612  <- the published "p ≈ 0.06" |
  | 33         | 4.12 | 0.0123 |

**The 26-row is the control and it is a REAL one**, not a stored number: the
26-kernel population is today's tree minus the seven patterns added after the
caveat was computed (`p25 p28 p29 p32 p34 p35 p49`), re-lexed and re-classified
by the same code on the same run. If the classifier drifts, or a 26-era
`c/kernel.c` moves, the control fails and the 33-figure is not printed as
comparable.

## What is committed and what is not — constraint 6, on purpose

Committed: the classifier, this driver, the three corpus **manifests**, and
`census_filelists.py`, which rebuilds the corpus file lists from them.
NOT committed: the census JSONs. `cgnu.json` alone is **11.9 MB** against a
506 K manifest set, and it is exactly re-derivable from what is committed —
*keep the generator, delete the artefact*.

✅ **And the rebuild path is verified rather than asserted** (TASK_170):
`census_filelists.py`'s rebuilt lists select the **identical 2555 files** —
php 299, coreutils 94, cgnu 2162, symmetric difference 0 — as `TASK_131`'s
scratch lists that produced the published `p`. So the corpus half of the
derivation is re-derivable from the tree even though its intermediate is not in
it.

⚠ **The p-value half needs the three C corpora, which live under two OTHER
projects' trees** (`README.md` §1 names the roots). If they are gone, the
manifests still say *what was measured*, and this half reports that it cannot
run rather than printing a number. **`--ladder` needs nothing but this repo.**

⚠ **Nothing here may be imported by `harness/check.py`, `harness/measure.py` or
`harness/build.py`** — `common/census/` is outside both digests only for as long
as that holds (`README.md`, *Digest note*).
"""
import argparse
import collections
import json
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SCRATCH = os.path.join(REPO, ".temp", "census")

#: The seven patterns added AFTER the `0 of 255` caveat was computed. Removing
#: them from today's tree reconstructs the population it was computed on.
#: ⚠ Derived once, at TASK_166, by listing `.temp/t166/t129rerun/ladder26.files`
#: against the 33-pattern tree; pinned here because the 26-row is a CONTROL and
#: a control whose population drifts is not one.
AFTER_26 = ("p25", "p28", "p29", "p32", "p34", "p35", "p49")

#: The published figures. A move in ANY of them exits 1.
WANT_SITES = {26: {"sites": 255, "ptr_offset": 0, "fns": 30, "files": 26},
              33: {"sites": 464, "ptr_offset": 0, "fns": 40, "files": 33}}

#: `TASK_131` §A / `README.md` §3, cgnu size-matched, FUNCTION unit.
#: ⚠ The FUNCTION unit is the honest one -- the SITE unit over-counts, because
#: the sites sit in a handful of functions in files cloned from one template
#: and are not independent draws (`TASK_131`, and the review that rejected it).
WANT_P = {26: 0.0612, 33: 0.0123}
P_TOL = 5e-4

BUCK = [(0, 60), (60, 120), (120, 250), (250, 500), (500, 1000), (1000, 10 ** 9)]
CORPORA = ("cgnu", "php", "coreutils")

sys.path.insert(0, HERE)
import census_c as census                                      # noqa: E402


# --------------------------------------------------------------- the ladder
def extract_ladder(dest):
    """Every `patterns/*/c/*.{c,h}` AT `git HEAD`, flattened.

    ⚠ `git show HEAD:`, not the working tree: the published figure is a
    property of the COMMITTED kernels, and an uncommitted edit must not be able
    to move it silently. (`.temp/t129/ladder_extract.sh` did the same.)"""
    os.makedirs(dest, exist_ok=True)
    for old in os.listdir(dest):
        os.remove(os.path.join(dest, old))
    dirs = subprocess.run(["git", "ls-tree", "--name-only", "HEAD", "patterns/"],
                          cwd=REPO, capture_output=True, text=True,
                          check=True).stdout.split()
    n = 0
    for d in dirs:
        d = d.rstrip("/")
        pat = os.path.basename(d)
        files = subprocess.run(
            ["git", "ls-tree", "-r", "--name-only", "HEAD", d + "/c/"],
            cwd=REPO, capture_output=True, text=True, check=True).stdout.split()
        for f in files:
            if not f.endswith((".c", ".h")):
                continue
            blob = subprocess.run(["git", "show", "HEAD:" + f], cwd=REPO,
                                  capture_output=True, check=True).stdout
            with open(os.path.join(dest, f"{pat}__{os.path.basename(f)}"),
                      "wb") as fh:
                fh.write(blob)
            n += 1
    return n


def census_ladder(dest, kernels, label):
    """Run the classifier over a list of kernel paths; return the JSON path."""
    lst = os.path.join(dest, f"{label}.files")
    with open(lst, "w") as fh:
        for p in kernels:
            fh.write("x\t" + p + "\n")
    hdr = os.path.join(dest, "ladder.headers")
    with open(hdr, "w") as fh:
        for p in sorted(os.listdir(os.path.join(dest, "ladder"))):
            if p.endswith(".h"):
                fh.write(os.path.join(dest, "ladder", p) + "\n")
    out = os.path.join(dest, f"{label}.json")
    # the classifier's own CLI, so this driver cannot drift from it
    rc = subprocess.run([sys.executable, os.path.join(HERE, "census_c.py"),
                         "run", lst, out, "--label", label, "--headers", hdr],
                        cwd=dest, capture_output=True, text=True)
    if rc.returncode != 0:
        print(rc.stdout[-2000:], rc.stderr[-2000:])
        raise SystemExit(f"census_c.py run failed for {label}")
    return out


def summarise(path):
    with open(path) as fh:
        rows = [r for r in json.load(fh)["rows"] if not r.get("gen")]
    return {"sites": len(rows),
            "ptr_offset": sum(1 for r in rows if r["op"] == "ptr_offset"),
            "fns": len({(r["file"], r["fn"]) for r in rows}),
            "files": len({r["file"] for r in rows})}


def ladder_check(dest):
    n = extract_ladder(os.path.join(dest, "ladder"))
    ldir = os.path.join(dest, "ladder")
    all_k = sorted(os.path.join(ldir, f) for f in os.listdir(ldir)
                   if f.endswith("__kernel.c"))
    k26 = [p for p in all_k
           if os.path.basename(p).split("-")[0] not in AFTER_26]
    print(f"extracted {n} `c/*.{{c,h}}` files at git HEAD; "
          f"{len(all_k)} kernels, {len(k26)} in the 26-pattern control")
    rc = 0
    got = {}
    for pop, kern in ((26, k26), (33, all_k)):
        got[pop] = summarise(census_ladder(dest, kern, f"ladder{pop}"))
        want = WANT_SITES[pop]
        ok = got[pop] == want
        rc |= 0 if ok else 1
        tag = "ok" if ok else "DIFFERS"
        role = "CONTROL, published" if pop == 26 else "today"
        print(f"  {pop} kernels ({role:18s}): "
              + "  ".join(f"{k} {got[pop][k]}" for k in
                          ("sites", "ptr_offset", "fns", "files"))
              + f"   (want {want}) {tag}")
    if rc == 0:
        print("  -> `0 of 255` reproduces from today's tree, so `0 of "
              f"{got[33]['sites']}` is the SAME instrument on a bigger "
              "population and not a new one.")
    return rc, got


# ------------------------------------------------- the size-matched p-value
def _bucket(n):
    for b in BUCK:
        if b[0] <= n < b[1]:
            return b
    return BUCK[-1]


def _sizes(files_path):
    """`{(file, fn): body_tokens}` for every function the classifier finds."""
    size = {}
    with open(files_path, errors="surrogateescape") as fh:
        paths = [ln.rstrip("\n").split("\t")[-1] for ln in fh if ln.strip()]
    for p in paths:
        try:
            with open(p, "rb") as fh:
                raw = fh.read()
            if census.is_generated(raw):
                continue
            code, _, _ = census.preprocess(raw.decode("latin-1"))
            for f in census.find_functions(census.lex(code)):
                size[(p, f.name)] = f.b - f.a
        except Exception:                                     # noqa: BLE001
            pass
    return size


def _rows(json_path):
    with open(json_path) as fh:
        return [r for r in json.load(fh)["rows"] if not r.get("gen")]


def _rates(files_path, json_path):
    size, rows = _sizes(files_path), _rows(json_path)
    fn_all = collections.defaultdict(set)
    fn_walk = collections.defaultdict(set)
    for r in rows:
        k = (r["file"], r["fn"])
        if k not in size:
            continue
        b = _bucket(size[k])
        fn_all[b].add(k)
        if r["op"] == "ptr_offset":
            fn_walk[b].add(k)
    return {b: (len(fn_walk[b]) / len(fn_all[b]) if fn_all[b] else 0.0)
            for b in BUCK}


def _ladder_profile(files_path, json_path):
    size, rows = _sizes(files_path), _rows(json_path)
    fn = collections.Counter()
    seen = set()
    for r in rows:
        k = (r["file"], r["fn"])
        if k in size and k not in seen:
            seen.add(k)
            fn[_bucket(size[k])] += 1
    return fn


def pvalue_check(dest, corpus_dir):
    """`P(zero ptr_offset walkers)` under the FUNCTION unit, size-matched.

    Both populations are computed on this run: the 26 is the CONTROL."""
    missing = [c for c in CORPORA
               if not os.path.exists(os.path.join(corpus_dir, c + ".json"))]
    if missing:
        print(f"  corpus census missing for {', '.join(missing)} in "
              f"{os.path.relpath(corpus_dir, REPO)}")
        print("  -> `python3 common/census/bound_sites.py --build-corpus` "
              "(needs the three C corpora; `README.md` §1 names the roots).")
        print("  ⚠ NOT a pass: the p-value half did not run.")
        return 2, {}
    rates = {c: _rates(os.path.join(corpus_dir, c + ".files"),
                       os.path.join(corpus_dir, c + ".json")) for c in CORPORA}
    rc, got = 0, {}
    for pop in (26, 33):
        prof = _ladder_profile(os.path.join(dest, f"ladder{pop}.files"),
                               os.path.join(dest, f"ladder{pop}.json"))
        line = []
        for c in CORPORA:
            fr = rates[c]
            exp = sum(prof[b] * fr[b] for b in BUCK)
            lp = sum(prof[b] * -math.log(1 - fr[b]) for b in BUCK if fr[b] < 1)
            p = math.exp(-lp)
            if c == "cgnu":
                got[pop] = p
                ok = abs(p - WANT_P[pop]) <= P_TOL
                rc |= 0 if ok else 1
            line.append(f"{c} exp {exp:5.2f} P(zero) {p:.4f}")
        role = "CONTROL, published" if pop == 26 else "today"
        tag = "ok" if abs(got[pop] - WANT_P[pop]) <= P_TOL else "DIFFERS"
        print(f"  {pop} kernels ({role:18s}, {sum(prof.values())} "
              f"site-carrying fns): " + " | ".join(line)
              + f"   (want cgnu {WANT_P[pop]}) {tag}")
    if rc == 0:
        print(f"  -> `p ≈ 0.06` reproduces ({got[26]:.4f}); at 33 it is "
              f"{got[33]:.4f}, about {got[26] / got[33]:.1f}x stronger. "
              "⚠ Still SUGGESTIVE, not decisive, and the SITE unit is not "
              "quoted: those sites are not independent draws.")
    return rc, got


def build_corpus(corpus_dir):
    """Rebuild the three corpus censuses from the COMMITTED manifests. Slow."""
    os.makedirs(corpus_dir, exist_ok=True)
    rc = subprocess.run([sys.executable,
                         os.path.join(HERE, "census_filelists.py"), corpus_dir])
    if rc.returncode != 0:
        print("census_filelists.py FAILED -- the corpora have moved; stop.")
        return rc.returncode
    for c in CORPORA:
        print(f"# census {c} ...", flush=True)
        r = subprocess.run(
            [sys.executable, os.path.join(HERE, "census_c.py"), "run",
             os.path.join(corpus_dir, c + ".files"),
             os.path.join(corpus_dir, c + ".json"), "--label", c],
            cwd=corpus_dir)
        if r.returncode != 0:
            return r.returncode
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--ladder", action="store_true",
                    help="only the bound-site census + its 26-pattern control")
    ap.add_argument("--pvalue", action="store_true",
                    help="only the size-matched p-value + its control")
    ap.add_argument("--build-corpus", action="store_true",
                    help="rebuild the three corpus censuses (slow, needs the "
                         "corpora); the JSONs are NOT committed by design")
    ap.add_argument("--scratch", default=SCRATCH,
                    help="gitignored working directory (default .temp/census)")
    ap.add_argument("--corpus-dir", default=None,
                    help="where the corpus `.files`/`.json` live "
                         "(default <scratch>/corpus)")
    a = ap.parse_args()
    corpus_dir = a.corpus_dir or os.path.join(a.scratch, "corpus")
    os.makedirs(a.scratch, exist_ok=True)
    if a.build_corpus:
        return build_corpus(corpus_dir)

    rc = 0
    do_l = a.ladder or not a.pvalue
    do_p = a.pvalue or not a.ladder
    if do_l or do_p:
        print("== bound sites in the ladder's C kernels "
              "(`results/SYNTHESIS.md` §7's `0 of 255`)")
        r, _ = ladder_check(a.scratch)
        rc |= r
    if do_p:
        print("\n== the size-matched null probability "
              "(`results/SYNTHESIS.md` §7's `p ≈ 0.06`), FUNCTION unit")
        r, _ = pvalue_check(a.scratch, corpus_dir)
        rc |= r
    print(f"\nbound_sites.py: {'FAIL' if rc else 'OK'}  (rc={rc}; "
          "2 means the p-value half could not run)")
    return rc


if __name__ == "__main__":
    sys.exit(main())
