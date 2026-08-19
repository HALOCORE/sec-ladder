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
  harness/measure.py --check-stale             # do any committed records
  harness/measure.py p01 --check-stale         # disagree with the tree?
"""

import argparse
import glob
import hashlib
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


def load_model(pdir):
    """The pattern's own `model.py`, or None. Used only to describe the inputs.

    `harness/check.py` imports the same file under an audit-hook sandbox
    because there it is a *correctness oracle*; here it only produces a log
    line, so a plain import is enough -- but nothing in this file may come to
    depend on it."""
    path = os.path.join(pdir, "model.py")
    if not os.path.exists(path):
        return None
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        f"slb_measure_model_{buildmod.pattern_id(pdir)}", path)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception:                                      # noqa: BLE001
        return None
    return mod if hasattr(mod, "build") else None


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
    """Provenance of the run, with a structural caveat (TASK_008_REVIEW minor 3).

    `commit` is HEAD **at the time of measurement**, which is necessarily the
    commit *before* the one this JSON is committed in. So a freshly re-run,
    entirely up-to-date results file always reads `commit: <HEAD~1>, dirty:
    true`, and "the recorded commit is behind the tree" is therefore not
    evidence of staleness by itself. There is no fix -- a file cannot name the
    commit that will contain it -- so do not chase it. What *is* evidence:
    this record's own `source_sha256`/`input_sha256` maps (TASK_035), compared
    against the tree by `harness/measure.py --check-stale`. Before TASK_035 the
    only such map was `results/gate/<pattern>.json`'s, which covers what the
    *gate* read and is not the same list.

    `dirty_files` counts every modified path in the working tree, not just the
    ones this measurement depended on, so it is a smoke signal and nothing
    more."""
    commit = sh(["git", "-C", REPO, "rev-parse", "HEAD"])
    dirty = sh(["git", "-C", REPO, "status", "--porcelain"])
    return {"commit": commit, "dirty": bool(dirty.strip()),
            "dirty_files": len(dirty.splitlines()),
            "note": "commit is HEAD when measured, i.e. the parent of the "
                    "commit this file lands in; a fresh run always names "
                    "HEAD~1 and reads dirty. For real staleness run "
                    "`harness/measure.py --check-stale`, which compares this "
                    "record's source_sha256/input_sha256 against the tree."}


def host():
    gov = "?"
    p = "/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor"
    if os.path.exists(p):
        gov = open(p).read().strip()
    model = next((l.split(":", 1)[1].strip()
                  for l in open("/proc/cpuinfo") if l.startswith("model name")), "?")
    return {"cpu_model": model, "governor": gov,
            "note": "frequency scaling active, shared container -- wall clock is noisy"}


# ---- provenance: what this record depends on -----------------------------
#
# TASK_035. `results/gate/*.json` has carried `source_sha256` since TASK_005;
# `results/*.json` -- where every published `Ir`, `ns`, digest and static count
# lives -- carried nothing, so a measurement record could disagree with the tree
# indefinitely with nothing to say so. It did, for ~7 tasks:
# `results/p01-array-sum.json`'s `c-gcc/O0/whole` recorded `md5_fn 2fe6ada73f90`
# where a rebuild deterministically gives `4104f39118e8` (`md5_fn_norel` equal,
# so: `common/driver.c` grew 23 lines at `c623b22` and moved the call
# displacements).
#
# The list below is deliberately NOT `check.py`'s. That one globs `harness/*.py`
# wholesale, which is right for a gate record -- the gate really does read every
# one of those files -- and wrong here: a `report.py` edit would invalidate every
# measurement record in the repo without a single measured number moving, and a
# detector that cries wolf is a detector people switch off. The rule for this
# list is narrower: **a file belongs iff editing it can change a number this
# record prints.**
#
#   * `<pattern>/*.rs`, `<pattern>/c/*` -- the rung sources, including
#     `c/kernel_hardened.c` (R1h) and `safe_naive_verus.rs` (R2v) where they
#     exist; `build.py` selects cells by file presence, so the glob is the cell
#     list.
#   * `common/driver.*` -- `driver.c`/`driver.h` are compiled into every C cell
#     and `driver.rs` is `#[path]`-included by every Rust one. This is the file
#     that actually drifted, and it is shared, so an edit for pattern X restates
#     every whole-binary column of patterns A..W.
#   * `<pattern>/model.py`, `common/slb.py` -- the `inputs` block is `slb.read`
#     plus `model.build(path).describe()`. Unlike `check.py`, `measure.py` uses
#     the model for a description and never as an oracle -- but the description
#     is IN the record, so it is a dependency.
#   * `harness/build.py` -- owns the compiler paths and every flag
#     (`-O0/-O3`, `-DSLB_ISOLATED`, `-flto`, `--cfg slb_isolated`,
#     `codegen-units=1`). It decides what the machine code is.
#   * `harness/asm.py` -- owns every static column and both digest conventions.
#     A change to the normalisation or to the `nm`-extent walk restates
#     `n_fn`/`md5_fn`/`binary_text_bytes` with no rebuild at all.
#   * `harness/measure.py` -- this file: `CG_PLAN` (which cells get an `Ir`
#     column), `_sum_rows`' symbol matcher, `SKIP_INPUT_PREFIX`, and the wall
#     protocol.
#   * `verus_run.py` -- R5's and R2v's compiler driver (`build.py:VERUS_RUN`).
#     It decides what the `verus` cells' machine code is, and `toolchain.verus`
#     is its `--info` output.
#
# Deliberately EXCLUDED, each for a reason a later reader can check:
#
#   * `harness/report.py` -- renders `results/tables/*.md` FROM this record. It
#     cannot change a number in it. This is the false positive the list exists to
#     avoid.
#   * `harness/check.py`, `vparse.py`, `dloop.py`, `fixture.py` -- the gate and
#     its analysers. They certify the tree; they do not build or measure it, and
#     nothing they compute appears here.
#   * `<pattern>/*.md` -- `spec.md`'s pins bind the *gate*; `measure.py` reads no
#     pin from any of them. Hashing them would invalidate every record on a
#     `NOTES.md` prose edit, which is the `report.py` false positive again.
#   * `<pattern>/controls/*.py` -- control generators. Control cells are not in
#     `build.all_cells()` and are never measured here.
#   * `common/layout/*.py` -- the code-layout probe. It is a separate experiment
#     with its own outputs; `measure.py` neither imports nor runs it.
#
# `inputs/gen.py` is in `source_sha256`, but the blobs get their OWN block --
# see `input_sha256` below for why, and `--check-stale` for what the difference
# buys.


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def measurement_sources(pdir):
    """Committed files whose contents can change a number in this record."""
    return sorted(glob.glob(os.path.join(pdir, "*.rs"))
                  + glob.glob(os.path.join(pdir, "c", "*"))
                  + glob.glob(os.path.join(pdir, "model.py"))
                  + glob.glob(os.path.join(pdir, "inputs", "gen.py"))
                  + glob.glob(os.path.join(REPO, "common", "driver.*"))
                  + glob.glob(os.path.join(REPO, "common", "slb.py"))
                  + glob.glob(os.path.join(REPO, "harness", "build.py"))
                  + glob.glob(os.path.join(REPO, "harness", "asm.py"))
                  + glob.glob(os.path.join(REPO, "harness", "measure.py"))
                  + glob.glob(os.path.join(REPO, "verus_run.py")))


def matrix_inputs(indir):
    """The blobs a measurement actually opens -- the same filter the `inputs`
    loop below uses, so the two cannot drift apart.

    These are gitignored (`.memory/05-layout.md`), so `gen.py` is what is
    committed and the generator is hashed above. The blobs are hashed *as well*,
    separately, because the two answer different questions and collapsing them
    into one boolean is what makes the generator look like a bad thing to hash:

      * a `gen.py` edit that moves a matrix blob -- the record is stale, and only
        the blob hash proves it (the generator hash cannot tell "the inputs
        changed" from "a comment changed");
      * appending a sweep band, which `.memory/05-layout.md` measured as costing
        one gate re-run and no re-measure -- the generator moves, every matrix
        blob is byte-identical, and `--check-stale` says so instead of demanding
        a re-measure that would change nothing.

    Blobs missing from a fresh clone are reported as such, not as staleness:
    running `gen.py` is the documented way to get them back."""
    return sorted(os.path.join(indir, f) for f in os.listdir(indir)
                  if f.endswith(".bin") and not f.startswith(SKIP_INPUT_PREFIX))


def provenance(pdir, indir):
    return ({os.path.relpath(s, REPO): sha256_file(s)
             for s in measurement_sources(pdir) if os.path.isfile(s)},
            {os.path.relpath(b, REPO): sha256_file(b)
             for b in matrix_inputs(indir)})


# ---- the checker ---------------------------------------------------------

def _compare(rec, key):
    """(stale, missing) for one hash block of one record."""
    stale, missing = [], []
    for rel, want in sorted((rec.get(key) or {}).items()):
        path = os.path.join(REPO, rel)
        if not os.path.exists(path):
            missing.append(rel)
        elif sha256_file(path) != want:
            stale.append(rel)
    return stale, missing


def check_stale(pattern=None):
    """Compare every committed record's hash blocks against the working tree.

    Covers both record families, because they have the same failure mode and
    `.memory/02-bench-rules.md`'s hand-run one-liner only ever covered one:

      results/gate/*.json  -- `source_sha256`, written by `check.py`
      results/*.json       -- `source_sha256` + `input_sha256`, written here

    Verdicts. STALE is the only one that sets the exit code, so this can be run
    before trusting any committed number without it failing on a fresh clone:

      STALE          a hashed source, or a matrix input blob, differs from the
                     tree -- the record does not describe this tree
      GEN-ONLY       `inputs/gen.py` moved and every matrix blob it produces is
                     byte-identical: a sweep band, not a re-measure
      NO BASELINE    the record predates its hash block; nothing to compare
      MISSING        hashed file absent (gitignored blobs on a fresh clone --
                     run `inputs/gen.py`)
      FRESH          every hash matches
    """
    files = sorted(glob.glob(os.path.join(RESULTS, "p*.json"))
                   + glob.glob(os.path.join(RESULTS, "gate", "p*.json")))
    bad = seen = 0
    for f in files:
        rel = os.path.relpath(f, REPO)
        if pattern and not os.path.basename(f).startswith(pattern):
            continue
        # A `--skip`/`--no-callgrind` gate run certifies strictly less and gets
        # its own file (`check.py`); it is not the record of record.
        if f.endswith(".partial.json"):
            print(f"SKIP        {rel:42s} partial run")
            continue
        rec = json.load(open(f))
        # `results/p02-residue-sweep.json` is a side record, not a matrix
        # measurement; `report.py` discriminates on the `cells` list and so does
        # this (`.memory/03-measurement.md`, "a side record can make a table
        # un-regenerable").
        gate = os.path.basename(os.path.dirname(f)) == "gate"
        if not gate and "cells" not in rec:
            print(f"SKIP        {rel:42s} side record (no `cells` list)")
            continue
        seen += 1
        if "source_sha256" not in rec:
            print(f"NO BASELINE {rel:42s} (record predates `source_sha256`; "
                  f"it will carry one after the next run)")
            continue
        stale, missing = _compare(rec, "source_sha256")
        bstale, bmissing = _compare(rec, "input_sha256")
        gen_only = (not bstale and not bmissing and "input_sha256" in rec
                    and all(s.endswith("inputs/gen.py") for s in stale) and stale)
        if gen_only:
            print(f"GEN-ONLY    {rel:42s} {stale[0]} moved; "
                  f"{len(rec['input_sha256'])} matrix blob(s) byte-identical "
                  f"-- no re-measure needed")
        elif stale or bstale:
            bad += 1
            for s in stale + bstale:
                print(f"STALE       {rel:42s} {s}")
        else:
            print(f"FRESH       {rel:42s} "
                  f"{len(rec['source_sha256'])} source(s)"
                  + (f" + {len(rec['input_sha256'])} input(s)"
                     if "input_sha256" in rec else ""))
        for m in missing + bmissing:
            print(f"MISSING     {rel:42s} {m}")
    print(f"\n{seen} record(s) examined, {bad} STALE")
    return 1 if bad else 0


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
    ap.add_argument("pattern", nargs="?")
    ap.add_argument("--check-stale", action="store_true",
                    help="compare every committed results record against the "
                         "tree and exit; measures nothing")
    ap.add_argument("--reps", type=int, default=30)
    ap.add_argument("--cpu", type=int, default=3, help="taskset core for timing")
    ap.add_argument("--no-callgrind", action="store_true")
    ap.add_argument("--no-wall", action="store_true")
    ap.add_argument("--cells", default="all", choices=["all", "measured"])
    a = ap.parse_args()

    if a.check_stale:
        return check_stale(a.pattern)
    if not a.pattern:
        ap.error("a pattern is required unless --check-stale is given")

    pdir = buildmod.pattern_dir(a.pattern)
    pid = buildmod.pattern_id(pdir)
    slug = os.path.basename(pdir)
    # Per-pattern: the R1h cells exist only where c/kernel_hardened.c does and
    # the R2v control only where safe_naive_verus.rs does.
    cells = (buildmod.all_cells(pdir) if a.cells == "all"
             else buildmod.measured_cells(pdir))
    indir = os.path.join(pdir, "inputs")
    scratch = os.path.join(REPO, ".temp", "cg", pid)
    src_sha, inp_sha = provenance(pdir, indir)

    doc = {
        "pattern": slug,
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "git": git_state(),
        # TASK_035: what this record depends on, so staleness is detectable --
        # `harness/measure.py --check-stale`. See `measurement_sources` for why
        # each line is in the list and `matrix_inputs` for why the blobs are a
        # separate block.
        "source_sha256": src_sha,
        "input_sha256": inp_sha,
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

    # The per-input row used to decode the payload with `slb.head_u64_body`,
    # i.e. it assumed p01's "one head word then u64s" layout and reported
    # `win_len`/`v_len` for every pattern. p02's payload is two head words and a
    # byte blob, so those two columns were nonsense there. What is actually
    # generic is the file *format* (n_iters / payload_len / present / truncated)
    # plus whatever the pattern's own `model.py` says about itself.
    modmod = load_model(pdir)
    for f in sorted(os.listdir(indir)):
        if not f.endswith(".bin") or f.startswith(SKIP_INPUT_PREFIX):
            continue
        path = os.path.join(indir, f)
        sf = slb.read(path)
        rec = {"n_iters": sf.n_iters, "declared_len": sf.declared_len,
               "present": len(sf.payload), "truncated": sf.truncated}
        if modmod is not None:
            try:
                rec["model"] = modmod.build(path).describe()
            except Exception as e:                        # noqa: BLE001
                rec["model"] = f"<model.py failed: {e}>"
        doc["inputs"][f] = rec

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
