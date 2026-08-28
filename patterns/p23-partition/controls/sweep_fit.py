#!/usr/bin/env python3
"""p23 control -- RE-FIT the safety-tax law against the shipped sweep bands.

    python3 patterns/p23-partition/inputs/gen.py --sweep
    python3 patterns/p23-partition/controls/sweep_fit.py        # writes sweep_fit.json

`../NOTES.md 9` publishes `R3 - R4` as a two-term law in RECORDS and COPIED
BYTES. Two matrix inputs give two equations and two unknowns, so that fit is
EXACTLY DETERMINED and has no residual to look at -- which is not evidence, it
is arithmetic. `.memory/03-measurement.md` and TASK_101 §4 both say to re-fit
from a committed band before publishing, and p19 is the pattern that shipped a
band and never did.

This script measures per-function exclusive `Ir` for the `kernel` symbol on the
`sweep-m*` (live extent) and `sweep-k*` (PIVOT RANK) bands, at `-O3 isolated`,
and reports:

  * the least-squares fit of `R3 - R4` on (records, copied bytes) over band M,
    with residuals, against the two-point matrix fit;
  * whether the tax depends on the PIVOT RANK at fixed extent -- band K holds
    `m = 32` and `nrec = 8` and sweeps `nlow` 1..31, so a rank-free law predicts
    a flat line and the probe for this row predicted it would not be flat.

⚠ It reads `n_iters` out of each blob rather than assuming it, and divides the
kernel-exclusive count by the call count, so nothing here depends on the loader
or the environment block (`.memory/03-measurement.md` C7).

## The staleness pin (TASK_121) -- `derived_from_sha256`

`sweep_fit.json` is a tracked cache of measured numbers, and `NOTES.md` 9c
quotes it. `harness/measure.py --check-stale` cannot see it: it globs
`results/*.json` and `results/gate/p*.json` and nothing else. So this file
carries its own pin, and `harness/check.py::check_control_json_pins` verifies
it. See `derived_from` for what is in the digest and, more importantly, what is
deliberately NOT — and `rebuild_cells` for the one term a hash could not have
covered at all.
"""
import glob
import hashlib
import json
import os
import re
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
sys.path.insert(0, os.path.join(REPO, "harness"))
import build as buildmod  # noqa: E402  -- see `rebuild_cells`
import measure  # noqa: E402  -- for `measurement_sources`, see `derived_from`

INPUTS = os.path.join(PDIR, "inputs")
BUILD = os.path.join(REPO, ".temp", "build", "p23")
OUT = os.path.join(REPO, ".temp", "t101", "cgsweep")
VALGRIND = os.path.expanduser("~/tools/valgrind/bin/valgrind")
CG_ANNOTATE = os.path.expanduser("~/tools/valgrind/bin/callgrind_annotate")
CELLS = ("safe_naive", "safe_tuned", "unsafe", "verus", "c-gcc-h", "c-gcc")


def n_iters(path):
    with open(path, "rb") as f:
        return struct.unpack("<Q", f.read(8))[0]


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def rebuild_cells():
    """Rebuild the six `-O3 isolated` cells before measuring them.

    ⚠⚠ **Without this the pin would OVERCLAIM, in `.memory/03-measurement.md`'s
    entry-8 shape: *"would its FAILING mean what its PASSING means?"*** This
    script reads pre-built binaries out of gitignored `.temp/build/p23/` and
    never used to check where they came from. So a source edited without a
    rebuild produced rows measured on the OLD binary while `derived_from`
    recorded the NEW source hash -- a green pin over a stale number, which is
    the exact defect the pin exists to catch.

    Closed by RE-DERIVING rather than by hashing, the way
    `harness/asm.py::selftest` re-derives the pilot's counts instead of
    trusting a recorded one. Measured at TASK_121: all six cells rebuild in
    **~3 s** (`verus` 2.1 s -- `build_verus` compiles, it does not re-verify),
    and the result is **bit-reproducible** (four cells, sha256 unchanged across
    a rebuild). So this is nearly free and it makes the binaries' provenance a
    property of the run rather than an assumption about the box.

    ⚠ The built binaries are deliberately NOT added to `derived_from`: they are
    gitignored derived artefacts, hashing them would make a fresh clone report
    `MISSING-SOURCES` (a SHOUT) instead of a checkable verdict, and once the
    rebuild guarantees provenance they add no detection power."""
    made = []
    for cell in CELLS:
        try:
            ok, out, log = buildmod.build_cell(PDIR, cell, "O3", "isolated",
                                               quiet=True)
        except SystemExit as e:                     # unknown/absent cell
            print(f"  build {cell}: SKIPPED ({e})", file=sys.stderr)
            continue
        if not ok:
            print(f"  build {cell}: FAILED\n{log}", file=sys.stderr)
        else:
            made.append(cell)
    print("rebuilt %d/%d cells at -O3 isolated: %s"
          % (len(made), len(CELLS), " ".join(made)))
    return made


def derived_from(blobs):
    """`{repo-relative path: sha256}` for everything that can change a number
    in `sweep_fit.json`. Self-describing: the reader re-hashes exactly these
    paths, so it needs no knowledge of what this script does.

    Three terms, and the third is the one the obvious answers miss.

    * **`measure.py::measurement_sources(PDIR)`** -- REUSED, not re-listed. It
      is the project's one answer to "committed files whose contents can change
      a number in this record", and the six `-O3 isolated` binaries this script
      reads out of `.temp/build/p23/` are built from exactly that set
      (`p23 *.rs`, `c/*`, `common/driver.*`, `build.py`, `verus_run.py`). A
      second hand-rolled copy of that list is a list that rots; that is the
      defect this project keeps finding. It is mildly OVER-broad -- `asm.py`,
      `measure.py`, `model.py` and `common/slb.py` cannot move a number here --
      and over-broad is the safe direction for a staleness pin, at 47 s to
      clear.
    * **this script**, because `want_m`, `want_k`, `CELLS` and `kernel_ir`'s
      regex all decide what the rows are. Not self-referential: the sidecar is
      not hashed, only the generator is.
    * ⚠⚠ **the sweep blobs actually opened.** `measure.py`'s
      `SKIP_INPUT_PREFIX = "sweep-"` means `inputs/sweep-*.bin` is hashed by
      NEITHER `source_sha256` NOR `input_sha256`. That is CORRECT for
      `measure.py`, which never measures them -- and wrong for a sidecar whose
      every row is one of them. `measure.py::matrix_inputs`'s own comment
      rejects hashing `gen.py` INSTEAD of the blobs ("the generator hash cannot
      tell 'the inputs changed' from 'a comment changed'"), and that argument
      applies here unchanged, so the blobs are hashed as well as `gen.py`.
      Only the 15 blobs this run READ are pinned, not all 107 present: adding a
      band must not stale a fit that never looked at it.

    ⚠ **Deliberately NOT in the digest, with the reason:**

    * `spec.md` / the `slb-contract` block. The rows are measurements of
      BINARIES, and `spec.md` enters no binary -- `measurement_sources` omits it
      for the same reason. A contract move with the rung sources unchanged does
      not falsify a single number here.
    * `NOTES.md`, `README.md`. ⚠ The gate's `source_sha256` DOES cover
      `patterns/*/*.md`, which is why pinning against the gate digest is the
      wrong answer: it would report `STALE` on a prose fix, and a pin whose
      `STALE` does not mean "the numbers are wrong" is a pin that gets switched
      off. ⚠ Note the cost argument usually given for this ("~30 minutes of
      callgrind to clear it") is FALSE and was measured at TASK_121: a full
      regeneration is **47 s** and byte-identical. The reason is the SIGNAL,
      not the price.
    * valgrind / `callgrind_annotate` / the toolchain. Unpinned and unpinnable
      from here; `.memory/00-environment.md` carries the versions. Named as a
      gap rather than left implicit (TASK_114's env-pin lesson)."""
    files = [s for s in measure.measurement_sources(PDIR) if os.path.isfile(s)]
    files.append(os.path.join(HERE, "sweep_fit.py"))
    files.extend(blobs)
    return {os.path.relpath(p, REPO): sha256_file(p) for p in sorted(set(files))}


def kernel_ir(binary, blob, tag):
    os.makedirs(OUT, exist_ok=True)
    out = os.path.join(OUT, f"cg.{tag}.out")
    r = subprocess.run([VALGRIND, "--tool=callgrind",
                        f"--callgrind-out-file={out}", binary, blob],
                       capture_output=True, text=True, timeout=3600)
    if r.returncode != 0:
        return None
    ann = subprocess.run([CG_ANNOTATE, "--threshold=100", out],
                         capture_output=True, text=True, timeout=3600).stdout
    tot = 0
    seen = False
    for line in ann.splitlines():
        if ":kernel" not in line and not line.rstrip().endswith("kernel"):
            continue
        m = re.match(r"\s*([\d,]+)\s", line)
        if m:
            tot += int(m.group(1).replace(",", ""))
            seen = True
    os.remove(out)
    return tot if seen else None


def lsq(rows, key):
    """least squares of `tax = a*records + b*bytes` over `rows`."""
    sxx = sum(r["nrec"] ** 2 for r in rows)
    syy = sum(r["mbytes"] ** 2 for r in rows)
    sxy = sum(r["nrec"] * r["mbytes"] for r in rows)
    sxz = sum(r["nrec"] * r[key] for r in rows)
    syz = sum(r["mbytes"] * r[key] for r in rows)
    det = sxx * syy - sxy * sxy
    if det == 0:
        return None, None
    return (sxz * syy - syz * sxy) / det, (syz * sxx - sxz * sxy) / det


def main():
    want_m = [2, 4, 8, 16, 24, 32, 40, 48]
    want_k = [1, 4, 8, 16, 24, 28, 31]
    files = []
    for m in want_m:
        p = os.path.join(INPUTS, f"sweep-m{m:02d}n08.bin")
        if os.path.exists(p):
            files.append(("M", p, 8, m, m // 2))
    for lo in want_k:
        p = os.path.join(INPUTS, f"sweep-k{lo:02d}m32.bin")
        if os.path.exists(p):
            files.append(("K", p, 8, 32, lo))
    if not files:
        print("no sweep blobs; run inputs/gen.py --sweep first", file=sys.stderr)
        return 1
    # ⚠ ORDER MATTERS. Rebuild FIRST, so the binaries provably come from the
    # sources about to be pinned (`rebuild_cells`), and pin SECOND but still
    # BEFORE the measurement, so a source edited while the 90 callgrind runs
    # are in flight is recorded as it was when they started rather than as it
    # ended up -- a mid-run edit then shows up as STALE on the next gate, which
    # is the safe direction.
    rebuild_cells()
    pins = derived_from([p for _, p, _, _, _ in files])
    recs = []
    for band, path, nrec, m, nlow in files:
        it = n_iters(path)
        row = {"band": band, "input": os.path.basename(path), "nrec": nrec,
               "m": m, "nlow": nlow, "rank": nlow / m, "mbytes": nrec * m,
               "n_iters": it}
        for cell in CELLS:
            b = os.path.join(BUILD, f"{cell}-O3-isolated")
            if not os.path.exists(b):
                continue
            ir = kernel_ir(b, path, f"{cell}.{os.path.basename(path)}")
            row[cell] = None if ir is None else ir / it
        if row.get("safe_tuned") and row.get("unsafe"):
            row["r3_r4"] = row["safe_tuned"] - row["unsafe"]
            row["r2_r4"] = row["safe_naive"] - row["unsafe"]
        recs.append(row)
        print("  %-22s nrec=%d m=%-2d rank=%.2f  R2=%9.2f R3=%9.2f R4=%9.2f  "
              "R3-R4=%8.2f" % (row["input"], nrec, m, row["rank"],
                               row.get("safe_naive") or 0,
                               row.get("safe_tuned") or 0,
                               row.get("unsafe") or 0, row.get("r3_r4") or 0))
    band_m = [r for r in recs if r["band"] == "M" and "r3_r4" in r]
    band_k = [r for r in recs if r["band"] == "K" and "r3_r4" in r]
    # TASK_121. The pin goes FIRST so it is the first thing a reader of the
    # file sees, and `pin.*` gives `check.py::check_control_json_pins` the two
    # commands it needs to print when it fires -- a stale verdict nobody knows
    # how to clear is how gates get switched off.
    res = {"derived_from_sha256": pins,
           "pin": {
               "regenerate":
                   "python3 patterns/p23-partition/controls/sweep_fit.py",
               "restore_missing":
                   "python3 patterns/p23-partition/inputs/gen.py --sweep",
               "not_covered":
                   "spec.md, NOTES.md, README.md (no binary depends on them) "
                   "and the valgrind/compiler toolchain (unpinnable from here; "
                   "versions in .memory/00-environment.md). See "
                   "controls/sweep_fit.py::derived_from.",
           },
           "rows": recs}
    if band_m:
        a, b = lsq(band_m, "r3_r4")
        a2, b2 = lsq(band_m, "r2_r4")
        res["fit_band_M"] = {"r3_r4": {"per_record": a, "per_byte": b},
                             "r2_r4": {"per_record": a2, "per_byte": b2}}
        print(f"\nBAND M least squares  R3-R4 = {a:.3f}/record + {b:.4f}/byte")
        print(f"                      R2-R4 = {a2:.3f}/record + {b2:.4f}/byte")
        print("  residuals (R3-R4):")
        for r in band_m:
            pred = a * r["nrec"] + b * r["mbytes"]
            print("    m=%-3d obs=%8.2f pred=%8.2f resid=%+8.2f"
                  % (r["m"], r["r3_r4"], pred, r["r3_r4"] - pred))
    if band_k:
        vals = [r["r3_r4"] for r in band_k]
        res["band_K_r3_r4"] = {r["nlow"]: r["r3_r4"] for r in band_k}
        print(f"\nBAND K (m=32, nrec=8, rank swept): R3-R4 "
              f"min={min(vals):.2f} max={max(vals):.2f} spread={max(vals)-min(vals):.2f}")
        for r in band_k:
            print("    nlow=%-3d rank=%.2f  R2=%8.2f R3=%8.2f R4=%8.2f  R3-R4=%7.2f  R2-R4=%7.2f"
                  % (r["nlow"], r["rank"], r["safe_naive"], r["safe_tuned"],
                     r["unsafe"], r["r3_r4"], r["r2_r4"]))
    with open(os.path.join(HERE, "sweep_fit.json"), "w") as f:
        json.dump(res, f, indent=1)
    print("\nwrote", os.path.join(HERE, "sweep_fit.json"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
