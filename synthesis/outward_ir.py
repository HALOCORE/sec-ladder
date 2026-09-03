#!/usr/bin/env python3
"""Price the work the kernel DISPATCHES OUTWARD -- a callgrind caller->callee sweep.

⚠ **THIS IS NO LONGER A COLUMN IN THE ARTEFACT.**  `results/synthesis.md`
publishes the callee correction **derived from committed records**
(`results/gate/pNN.json::marginal_ir_per_call`; see
`synthesis/synthesize.py::CALLEE_NOTE`), because that route is recomputed on
every run and needs no build, no callgrind and no sidecar.  What this file
still does, and what nothing else can:

  * it is the **oracle that calibrates** the derived column.  `synthesize.py`
    scores against it live and prints the three measured bands -- below
    2.00 `Ir` nothing real hides, 2.00..16.00 is a coin flip, at or above
    16.00 every row is real.  Those numbers are this file's whole remaining
    job in the artefact.
  * it **names the callee and now counts the calls**, which the derived route
    cannot do at all.

Its soundness as an oracle was established with two purpose-built probes
(TASK_075_REVIEW A0): a tail-`jmp` into a helper is still recorded as a
`calls=` edge, so the tail-call blind spot does not exist; and a callee reached
from two call sites plus transitively sums to exactly
`callgrind_annotate --inclusive=yes`, counted once.

## THE STALENESS PIN, AND ⚠⚠ THIS PARAGRAPH USED TO SAY THERE WAS NONE

It said *"⚠ **It carries no staleness pin**, unlike `synthesis/licence.json`"*,
and that has been **false since TASK_107 §F** added one -- `PROTOCOL` rule 13's
header rot, in the file's own opening. Corrected at TASK_170.

Re-emitting costs 352 callgrind runs against a fully built `.temp/build/`, which
is the reason it calibrates rather than publishes -- and the reason the pin has
to be RIGHT, because a sidecar nobody will re-emit is a sidecar whose false
STALE just gets ignored.

⚠⚠⚠ **AND THE PIN TASK_107 ADDED WAS THE WRONG KEY, MEASURED.** It carried the
**gate** `source_sha256`, which covers `harness/check.py`, `harness/vparse.py`,
every `patterns/*/*.md`, `model.py`, `inputs/gen.py` and `common/layout/*` --
none of which this file reads and none of which can move a callgrind number of an
already-built binary. One `check.py` docstring edit therefore staled **all 33
entries, falsely** (`TASK_168` P3). Stage 9b's own docstring argues against the
key in terms: *"a pin whose STALE does not mean 'the numbers are wrong' is a pin
that gets switched off."*

⚠⚠ **RECAP queue item 37's proposed replacement -- `measure.py::
measurement_sources` -- IS NOT THE REPAIR EITHER, and it was measured twice**
(`TASK_169` §5e, re-derived at `TASK_170` item D, `.temp/t170/pin_probe.py`):
it still reports **4 of 33 STALE** (`p12 p13 p16 p38`), because it globs
`model.py` and `inputs/gen.py` and those four had comment-only edits at
TASK_168. A pin that turns 33 false STALEs into 4 false STALEs is an improvement
and not a fix.

✅ **WHAT THIS FILE PINS NOW (`--repin`, TASK_170): the BUILD DETERMINANTS, and
nothing else.** Measured over the same evidence: **0 of 33 stale.**

    patterns/<pat>/*.rs        the four rung sources
    patterns/<pat>/c/*         kernel.c / kernel.h / kernel_hardened.c / main.c
    common/driver.{c,h,rs}     linked into every cell
    harness/build.py           the flags
    verus_run.py               builds the R5 cell
    + patterns/<pat>/inputs/{small,large}.bin   the blob, hashed directly
    + n_iters, which is the per-call DIVISOR

⚠ `common/slb.py` is deliberately **excluded** although `measurement_sources`
globs it: it is a Python reader/writer that is compiled into nothing. It reaches
this sidecar only through the blob's CONTENT, and the blob is pinned directly --
so including it would reintroduce exactly the false-STALE class the whole repair
is about. Same for `harness/asm.py` and `harness/measure.py`: this file imports
neither (only `harness/build.py`), and the one thing `measure.py` supplies is
`n_iters`, which is pinned as a VALUE.

⚠ **The pin is over SOURCES as a proxy for the BINARY.** What callgrind actually
saw is `.temp/build/<pat>/<cell>-O3-isolated`, which is gitignored; the source
set above is what `build.py` rebuilds it from. That is the same proxy every
measurement record uses and it has the same limit: a binary rebuilt with a
different toolchain from identical sources is not detected here.

⚠⚠ **HOW `--repin` AVOIDS A RE-EMIT, AND WHY THE VALUES ARE STILL HONEST.**
The old `gate_source_sha256` is not one hash -- it is the whole
`path -> sha256` MAP the gate recorded, so **the emit-time hash of every build
determinant is already committed inside this file.** `--repin` therefore
*filters that map*; it does not read the working tree for the values at all. So
the new `derived_from_sha256` is provably the emit-time content, `TASK_166`'s,
with no callgrind run and no `git` archaeology. The old map is kept, renamed
`gate_source_sha256_at_emit`, as provenance that is no longer COMPARED -- a key
that looks like a pin and is not checked is a trap.

⚠ **The one thing `--repin` cannot verify retroactively is the BLOB**, because
the gate map does not cover gitignored files. It pins today's hashes and
cross-checks them against each measurement record's own `input_sha256`, which
predates this sidecar. **MEASURED at TASK_170: 56 of 66 blobs retro-verified,
0 mismatched.** The other 10 are the two blobs each of **`p02 p05 p07 p11
p17`, whose measurement records carry no `input_sha256` at all** -- they were
emitted before TASK_035's provenance block, and `measure.py --check-stale`
cannot date them either while still printing `0 STALE`. **So for those five the
blob pin starts at TASK_170 and is not retro-verified.** That is a KNOWN
residual, named here rather than papered over.

It is NOT in `harness/`: `check.py` hashes `harness/*.py` into all 22 gate
records and `measure.py` is hashed into all 22 MEASUREMENT records, so putting
it there would force a full re-measure, which re-takes the wall-clock block.

HOW.  It runs callgrind once per cell and parses the raw `callgrind.out`
instead of `callgrind_annotate`, because the raw file carries the caller->callee
edges that the annotation throws away:

    fn=(id) <kernel>
    cfn=(id) <callee>
    calls=<n> <target>
    <line> <cost>            <- INCLUSIVE cost of those calls

    kernel_inclusive = kernel_exclusive + sum(edges out of kernel)

VALIDATION -- it re-derives three separately reviewed published numbers it was
never told:

    p13  R2 outward - R4 outward   = -190.00 small / -264.00 large
         == `.memory/03-measurement.md`: "overstated by 190 / 264 Ir/call,
            entirely because R2 makes no `memcpy` call and R4 does"
    p36  dispatch-target Ir/call   = gcc 512.00, clang/rustc 384.00
         == `.memory/03-measurement.md` (TASK_073), to the instruction
    p36  gcc-vs-clang, kernel col  = -120.00 / -1016.00  ->  +8.00 / +8.00
         == "the gcc-vs-clang C gap vanishes: 10*nrw vs 11*nrw becomes 14 vs 14"

⚠ TWO CAVEATS ON THE COLUMN ITSELF, both measured here and both meaning that
adding callees is not uniformly an improvement:

  * **p03/p04**: glibc `memset`'s path length moves with the stack array's
    alignment, so cells with identical call sets differ by +-7.00 Ir/call.
    On this column p03's `R5 - R4` reads **-7.00** -- "the proof costs -7
    instructions" -- and p04's `R3 - R4` flips sign.  There the
    kernel-EXCLUSIVE column is the correct one.  ⚠ **The figure itself does
    not reproduce**: two sweeps of the same binaries differing only in one
    ADDED ENVIRONMENT VARIABLE (`SLB_ALIGN_PAD=z*64`, i.e. **+87 bytes** of
    environment block -- ⚠ NOT +64, once the `envp` slot, the name and the NUL
    are counted; TASK_098 read it as 64, computed `64 mod 32 == 0` and called
    the control vacuous, and TASK_099 measured the block growing by exactly 87
    with the `memset` moving `50.00 -> 43.00` per kernel call) moved the
    outward figure on
    **11 of 348** (pattern, input, cell) triples -- p03/p04 `safe_tuned` and
    seven p08 cells -- while the kernel-EXCLUSIVE figure moved on **0 of 348**.
    ⚠ The effect is BISTABLE with a 32-byte period and a 16-wide window whose
    phase differs per binary, so `43.00` and `50.00` are not properties of the
    two cells: each takes both.  (A first version of this note blamed the
    `--callgrind-out-file=` path length.  That knob is INERT: valgrind strips
    its own options before building the client stack, and two paths of
    different length give identical figures.)
  * **gcc's PLT thunk**: gcc routes each libc call through `endbr64 ; jmp *GOT`,
    which callgrind attributes as its own function; clang's thunk is a bare
    `jmp` and is folded into the callee.  **+2.00 Ir per libc call, gcc only**,
    and one of the two instructions is the `endbr64` of gcc's default
    `-fcf-protection=full`.  This column therefore carries an IBT term the
    kernel-exclusive column never had.
  * **a one-off lazy-binding / IFUNC resolver**, 725-794 Ir per PROCESS, in
    clang's and rustc's binaries and not gcc's.  It is a per-process constant
    inside a per-call column, scaling as `1/n_iters` -- 0.0065 .. 0.5293
    Ir/call here -- and it is why p11 reads 299.8727 where 150 x 2.00 = 300.00.

Usage:
    synthesis/outward_ir.py p13 --input small.bin
    synthesis/outward_ir.py --emit synthesis/outward_ir.json     # whole tree

⚠ The emitted JSON gained `outward_calls_per_kernel_call` and
`outward_ir_per_callee_call` at TASK_076 (m5); a file emitted before that has
neither, and `synthesize.py` does not read them.  Re-emit to populate.
"""
import argparse
import glob
import hashlib
import json
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "harness"))
import build as bld  # noqa: E402

VALGRIND = os.path.expanduser("~/tools/valgrind/bin/valgrind")
BUILD = os.path.join(REPO, ".temp", "build")
SCRATCH = os.path.join(REPO, ".temp", "synth-cg")
KERNEL_RE = re.compile(r"(?:^|::)kernel(?:$|[^A-Za-z0-9_])")
PAIRS = [("safe_naive", "unsafe", "R2-R4"),
         ("safe_tuned", "unsafe", "R3-R4"),
         ("verus", "unsafe", "R5-R4"),
         ("c-gcc", "c-clang", "gcc-clang")]


def parse_cg(path):
    """-> (names{id: str}, exclusive{id: Ir}, edges{(caller,callee): Ir},
           calls{(caller,callee): n}).

    ⚠ The `calls=<n>` COUNT is kept, not discarded.  Without it the record
    cannot check its own per-call attribution -- TASK_075_REVIEW had to re-run
    callgrind to verify *"150 `strlen` calls x 2.00"*, because the earlier
    version of this parser read `calls=` only as an "the next cost line is an
    edge" flag and threw the number away (m5).  With it, `outward_by_callee`
    divides into `Ir per call of the callee`, which is what a thunk claim or a
    libc-path-length claim is actually about."""
    names, excl, edges, calls = {}, {}, {}, {}
    cur, pend, armed, ncalls = None, None, False, 0
    for line in open(path, errors="replace"):
        line = line.rstrip("\n")
        m = re.match(r"^(c?fn)=\((\d+)\)(?:\s+(.*))?$", line)
        if m:
            kind, fid, nm = m.group(1), int(m.group(2)), m.group(3)
            if nm:
                names[fid] = nm
            if kind == "fn":
                cur, pend, armed = fid, None, False
            else:
                pend = fid
            continue
        if re.match(r"^(c?ob|c?fl|c?fi|c?fe)=", line):
            continue
        m = re.match(r"^calls=(\d+)", line)
        if m:
            armed, ncalls = True, int(m.group(1))
            continue
        m = re.match(r"^([+\-*]?\d+|\*)\s+(\d+)", line)
        if m:
            ir = int(m.group(2))
            if armed and pend is not None and cur is not None:
                edges[(cur, pend)] = edges.get((cur, pend), 0) + ir
                calls[(cur, pend)] = calls.get((cur, pend), 0) + ncalls
                armed, pend, ncalls = False, None, 0
            elif cur is not None:
                excl[cur] = excl.get(cur, 0) + ir
    return names, excl, edges, calls


def measure(binary, arg, tag, timeout=3600):
    os.makedirs(SCRATCH, exist_ok=True)
    out = os.path.join(SCRATCH, f"cg.{tag}.out")
    r = subprocess.run([VALGRIND, "--tool=callgrind",
                        f"--callgrind-out-file={out}", binary, arg],
                       capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        raise RuntimeError(f"callgrind exit {r.returncode}: {r.stderr[-300:]}")
    names, excl, edges, calls = parse_cg(out)
    kids = [i for i, n in names.items() if KERNEL_RE.search(n)]
    kex = sum(excl.get(i, 0) for i in kids)
    by, ncalls = {}, {}
    for (x, y), ir in edges.items():
        if x in kids:
            n = names.get(y, f"?{y}")
            by[n] = by.get(n, 0) + ir
            ncalls[n] = ncalls.get(n, 0) + calls.get((x, y), 0)
    return {"kernel_symbols": [names[i] for i in kids],
            "kernel_exclusive_ir": kex,
            "outward_ir": sum(by.values()),
            "outward_by_callee": dict(sorted(by.items(), key=lambda kv: -kv[1])),
            "outward_calls_by_callee": {k: ncalls.get(k, 0)
                                        for k in sorted(by, key=lambda k: -by[k])},
            "kernel_inclusive_ir": kex + sum(by.values())}


def record_for(pat):
    """The measurement record with `cells` -- a pattern can own a SIDE record
    too (`results/p02-residue-sweep.json`, whose `inputs` is a string) and
    picking it by prefix alone crashes."""
    for f in sorted(glob.glob(os.path.join(REPO, "results", pat + "-*.json"))):
        d = json.load(open(f))
        if "cells" in d and isinstance(d.get("inputs"), dict):
            return d
    return None


def pattern_dir(pat):
    for d in sorted(os.listdir(os.path.join(REPO, "patterns"))):
        if d.startswith(pat + "-"):
            return os.path.join(REPO, "patterns", d)
    raise KeyError(pat)


def _gate_source_sha256(pat):
    """The gate record's `source_sha256` for `pat`, or `None` if there is no
    record.

    Copied from `synthesis/licence.py`, deliberately, key name included: the
    consumer (`synthesize.py::calibrate`) then needs ONE comparison for both
    sidecars instead of two conventions."""
    for d in sorted(os.listdir(os.path.join(REPO, "results", "gate"))):
        # `.partial.json` excluded, exactly as `licence.py` excludes it: a
        # PARTIAL run certifies strictly less and must not supply the pin. Since
        # TASK_056 those are written under `.temp/` instead, so this is belt and
        # braces -- and it is here because the file it copies has it.
        if (d.startswith(pat + "-") and d.endswith(".json")
                and not d.endswith(".partial.json")):
            try:
                return json.load(open(os.path.join(
                    REPO, "results", "gate", d))).get("source_sha256")
            except (OSError, ValueError):
                return None
    return None


# ==========================================================================
# THE PIN (TASK_170 item D).  See the module docstring for WHY these files and
# not `measure.py::measurement_sources`.
# ==========================================================================

#: Shared build inputs, by exact relative path.  ⚠ `common/slb.py`,
#: `harness/asm.py` and `harness/measure.py` are deliberately ABSENT although
#: `measurement_sources` globs all three -- see the docstring.
SHARED_DETERMINANTS = frozenset({
    "common/driver.c", "common/driver.h", "common/driver.rs",
    "harness/build.py", "verus_run.py",
})


def is_build_determinant(rel, pat_dirname):
    """Can this committed path change a number `outward_ir.py` records?

    Pure function of the path, so the must-fire arm can exercise the DECISION
    (`--selftest`) and not just its callers."""
    prefix = f"patterns/{pat_dirname}/"
    if rel.startswith(prefix):
        tail = rel[len(prefix):]
        # a rung source at the top level, or anything under `c/`
        return (tail.endswith(".rs") and "/" not in tail) or tail.startswith("c/")
    return rel in SHARED_DETERMINANTS


_PIN_CASES = [
    ("a rung source IS a determinant",
     is_build_determinant("patterns/p12-x/unsafe.rs", "p12-x"), True),
    ("the C kernel IS",
     is_build_determinant("patterns/p12-x/c/kernel.c", "p12-x"), True),
    ("a hardened C kernel IS (it is a measured cell)",
     is_build_determinant("patterns/p12-x/c/kernel_hardened.c", "p12-x"), True),
    ("the shared driver IS",
     is_build_determinant("common/driver.rs", "p12-x"), True),
    ("build.py IS -- it decides the flags",
     is_build_determinant("harness/build.py", "p12-x"), True),
    ("verus_run.py IS -- it builds the R5 cell",
     is_build_determinant("verus_run.py", "p12-x"), True),
    ("⚠ model.py is NOT -- this is the 4-of-33 case item 37 got wrong",
     is_build_determinant("patterns/p12-x/model.py", "p12-x"), False),
    ("⚠ inputs/gen.py is NOT -- the BLOB is pinned instead",
     is_build_determinant("patterns/p12-x/inputs/gen.py", "p12-x"), False),
    ("⚠ check.py is NOT -- this is the 33-of-33 case",
     is_build_determinant("harness/check.py", "p12-x"), False),
    ("⚠ vparse.py is NOT",
     is_build_determinant("harness/vparse.py", "p12-x"), False),
    ("⚠ a pattern doc is NOT",
     is_build_determinant("patterns/p12-x/NOTES.md", "p12-x"), False),
    ("⚠ a controls/ probe is NOT",
     is_build_determinant("patterns/p12-x/controls/pads.py", "p12-x"), False),
    ("⚠ common/slb.py is NOT -- it is compiled into nothing",
     is_build_determinant("common/slb.py", "p12-x"), False),
    ("⚠ asm.py is NOT -- this file never imports it",
     is_build_determinant("harness/asm.py", "p12-x"), False),
    ("⚠ ANOTHER pattern's rung source is NOT",
     is_build_determinant("patterns/p13-y/unsafe.rs", "p12-x"), False),
    ("a `.rs` in a SUBDIRECTORY is not a rung source",
     is_build_determinant("patterns/p12-x/controls/v.rs", "p12-x"), False),
]


def pin_selftest():
    bad = 0
    for label, got, want in _PIN_CASES:
        ok = got == want
        bad += not ok
        print(f"  {'ok  ' if ok else 'FAIL'}  {label}")
        if not ok:
            print(f"          got {got!r} want {want!r}")
    print(f"\noutward_ir.py --selftest: {'FAIL' if bad else 'OK'}  "
          f"({len(_PIN_CASES)} arms, {bad} failing)")
    return 1 if bad else 0


def blob_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def repin(path):
    """Rewrite ONLY the pin keys of an existing sidecar. No callgrind, no build.

    ⚠⚠ IT MUST NOT TOUCH A SINGLE MEASURED VALUE, and it asserts that: the
    per-input subtrees are compared before and after and the run aborts if any
    moved. `PROTOCOL` rule 6's artefact-vs-generator lesson cuts both ways --
    a re-pinner that quietly re-rounded a number would be undetectable."""
    with open(path) as fh:
        doc = json.load(fh)
    before = {p: {k: v for k, v in d.items() if k.endswith(".bin")}
              for p, d in doc.items() if isinstance(d, dict)}

    pats = sorted(p for p in doc if isinstance(doc[p], dict))
    n_pinned = n_blob = 0
    verified, unverified, mismatched = [], [], []
    for pat in pats:
        d = doc[pat]
        gate = d.pop("gate_source_sha256", None) or \
            d.get("gate_source_sha256_at_emit") or {}
        # keep the old map as PROVENANCE under a name nothing compares
        d["gate_source_sha256_at_emit"] = gate
        try:
            pdirname = os.path.basename(pattern_dir(pat))
        except KeyError:
            continue
        # ⚠ the values come from the sidecar's OWN committed map, never from
        # the working tree -- that is what makes them emit-time values.
        d["derived_from_sha256"] = {
            rel: h for rel, h in sorted(gate.items())
            if is_build_determinant(rel, pdirname)}
        n_pinned += len(d["derived_from_sha256"])

        # the blob: today's hash, cross-checked against the measurement
        # record's own `input_sha256`, which predates this sidecar.
        rec = record_for(pat) or {}
        recin = rec.get("input_sha256") or {}
        blobs = {}
        for inp in ("small.bin", "large.bin"):
            rel = os.path.join("patterns", pdirname, "inputs", inp)
            ap = os.path.join(REPO, rel)
            if not os.path.exists(ap):
                continue
            h = blob_sha256(ap)
            blobs[rel] = h
            n_blob += 1
            if rel in recin:
                (verified if recin[rel] == h else mismatched).append(rel)
            else:
                unverified.append(rel)
        d["input_sha256"] = blobs
        d["pin_note"] = (
            "TASK_170 item D. `derived_from_sha256` is FILTERED FROM THIS "
            "FILE'S OWN committed `gate_source_sha256` map, so the hashes are "
            "the EMIT-TIME ones (TASK_166, commit 6f5674f) and no callgrind "
            "run was needed. The MEASURED VALUES BELOW ARE UNCHANGED AND ARE "
            "TASK_166'S. `input_sha256` is TASK_170's reading of the blob, "
            "cross-checked against the measurement record's own "
            "`input_sha256` where that key exists.")

    after = {p: {k: v for k, v in d.items() if k.endswith(".bin")}
             for p, d in doc.items() if isinstance(d, dict)}
    assert before == after, "REPIN MOVED A MEASURED VALUE -- refusing to write"

    with open(path, "w") as fh:
        json.dump(doc, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(f"{os.path.relpath(path, REPO)}: re-pinned {len(pats)} patterns")
    print(f"  derived_from_sha256 : {n_pinned} entries "
          f"({n_pinned // max(len(pats), 1)} per pattern)")
    print(f"  input_sha256        : {n_blob} blobs  "
          f"({len(verified)} retro-verified against a measurement record, "
          f"{len(unverified)} not (record predates TASK_035), "
          f"{len(mismatched)} MISMATCHED)")
    if unverified:
        print("  ⚠ blob pin NOT retro-verified for: "
              + " ".join(sorted({r.split('/')[1] for r in unverified})))
    if mismatched:
        print("  ⚠⚠ MISMATCHED (a blob moved since its own measurement "
              "record): " + " ".join(mismatched))
    print("  measured values compared before/after: IDENTICAL "
          "(asserted, not inspected)")
    return 1 if mismatched else 0


def run_pattern(pat, inp, opt="O3", mode="isolated", cells=None, echo=True):
    rec = record_for(pat)
    if rec is None:
        return None
    n = rec["inputs"].get(inp, {}).get("n_iters")
    if not n:
        return None
    pdir = pattern_dir(pat)
    cells = cells or bld.measured_cells(pdir)
    blob = os.path.join(pdir, "inputs", inp)
    out = {"pattern": pat, "input": inp, "opt": opt, "mode": mode,
           "n_iters": n, "cells": {}}
    if echo:
        print(f"# {pat} {opt}/{mode} {inp}  n_iters={n}")
        print(f"{'cell':12s} {'kern.excl/call':>15s} {'outward/call':>13s} "
              f"{'kern.incl/call':>15s}")
    for c in cells:
        p = os.path.join(BUILD, pat, f"{c}-{opt}-{mode}")
        if not os.path.exists(p):
            continue
        r = measure(p, blob, f"{pat}-{c}-{opt}-{mode}-{inp}")
        out["cells"][c] = r
        if echo:
            print(f"{c:12s} {r['kernel_exclusive_ir']/n:15.2f} "
                  f"{r['outward_ir']/n:13.2f} {r['kernel_inclusive_ir']/n:15.2f}"
                  + ("   " + ", ".join(f"{k.split('::')[-1][:26]}={v/n:.2f}"
                                       for k, v in r["outward_by_callee"].items())
                     if r["outward_by_callee"] else ""))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pattern", nargs="?")
    ap.add_argument("--input", default="small.bin")
    ap.add_argument("--opt", default="O3")
    ap.add_argument("--mode", default="isolated")
    ap.add_argument("--emit", metavar="PATH")
    ap.add_argument("--repin", metavar="PATH",
                    help="rewrite ONLY the pin keys of an existing sidecar "
                         "(no callgrind, no build); see the module docstring")
    ap.add_argument("--selftest", action="store_true",
                    help="the must-fire arms for `is_build_determinant`")
    a = ap.parse_args()

    if a.selftest:
        return pin_selftest()
    if a.repin:
        return repin(a.repin)
    if not a.emit:
        run_pattern(a.pattern, a.input, a.opt, a.mode)
        return

    pats = sorted(d for d in os.listdir(BUILD) if re.fullmatch(r"p\d\d", d))
    doc = {}
    for pat in pats:
        doc[pat] = {}
        # ⚠ TASK_107 §F: THE STALENESS PIN THIS FILE'S OWN DOCSTRING SAID IT DID
        # NOT HAVE. `synthesis/licence.json` is the shape being copied -- carry
        # the gate `source_sha256` you were taken against, and let the consumer
        # print STALE on a mismatch (`synthesize.py::calibrate`). Without it the
        # sidecar was found THREE PATTERNS STALE (22 entries against 25) and
        # nothing could have said so; `results/synthesis.md` printed the absence
        # as a caveat in its own text, which is a warning, not a detector.
        #
        # Per pattern rather than one top-level key, because the sweep is per
        # pattern: a re-emit that skips a pattern (no build, no record) leaves
        # that pattern's OLD entry beside fresh ones, and one global hash cannot
        # express that. `.get(inp)` is how every consumer reads this level, so
        # the extra key is inert to all of them.
        doc[pat]["gate_source_sha256"] = _gate_source_sha256(pat)
        for inp in ("small.bin", "large.bin"):
            r = run_pattern(pat, inp, a.opt, a.mode)
            if r is None:
                continue
            n = r["n_iters"]
            cells = {c: {"kernel_exclusive_ir_per_call": v["kernel_exclusive_ir"] / n,
                         "outward_ir_per_call": v["outward_ir"] / n,
                         "kernel_inclusive_ir_per_call": v["kernel_inclusive_ir"] / n,
                         "outward_by_callee_per_call":
                             {k: x / n for k, x in v["outward_by_callee"].items()},
                         # m5: without these the record cannot check its own
                         # per-call attribution.
                         "outward_calls_per_kernel_call":
                             {k: x / n for k, x
                              in v["outward_calls_by_callee"].items()},
                         "outward_ir_per_callee_call":
                             {k: (v["outward_by_callee"][k]
                                  / v["outward_calls_by_callee"][k])
                              for k in v["outward_by_callee"]
                              if v["outward_calls_by_callee"].get(k)}}
                     for c, v in r["cells"].items()}
            pairs = {}
            for x, y, lab in PAIRS:
                if x in cells and y in cells:
                    de = (cells[x]["kernel_exclusive_ir_per_call"]
                          - cells[y]["kernel_exclusive_ir_per_call"])
                    di = (cells[x]["kernel_inclusive_ir_per_call"]
                          - cells[y]["kernel_inclusive_ir_per_call"])
                    pairs[lab] = {"kernel_exclusive": de,
                                  "kernel_plus_callees": di,
                                  "moves_by": di - de}
            doc[pat][inp] = {"n_iters": n, "cells": cells, "pairs": pairs}
    json.dump(doc, open(a.emit, "w"), indent=1, sort_keys=True)
    print(f"wrote {a.emit}: {len(doc)} patterns")
    # ⚠⚠ ARTEFACT-vs-GENERATOR SKEW, and this is the file `PROTOCOL` rule 6's
    # warning is about: TASK_170 re-pinned the committed sidecar with `--repin`,
    # and an `--emit` that wrote only `gate_source_sha256` would SILENTLY REVERT
    # that on the next re-emit. So the emit path calls the SAME re-pinner --
    # one code path decides what the pin is, and there is no second copy of the
    # determinant list to rot.
    rc = repin(a.emit)
    print("(pin written by the same `repin()` the `--repin` flag calls)")
    return rc


if __name__ == "__main__":
    # ⚠ `sys.exit(...)`, not a bare call: `--repin` and `--selftest` return a
    # STATUS, and a script whose exit code is always 0 cannot be checked.
    sys.exit(main() or 0)
