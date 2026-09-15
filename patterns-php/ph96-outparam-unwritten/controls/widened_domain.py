#!/usr/bin/env python3
"""ph96 -- does R1h CHANGE ANY BENIGN ANSWER, or only stop faulting?

    python3 patterns-php/ph96-outparam-unwritten/controls/widened_domain.py

`harness/check.py` stage 7h refuses an R1h that changes benign output, and
`RECAP_PHP.md` F43/F47 records that it was RIGHT to: on `ph07` the arm it refused
was a bug PHP itself later deleted with a regression test. So *the fix changes
nothing where the bug is not exercised* is a claim this row has to MEASURE.

▶ Eight cells (six rungs plus the two hardened C cells) x every shipped input.
The row's claim is that the R1-vs-R1h disagreement set is EXACTLY
`{adversarial-unset.bin}`, on both compilers, and that every other cell agrees
with the model bit for bit.

⛔⛔⛔ **AND IT MEASURED SOMETHING THE ROW DID NOT EXPECT, WHICH IS WHY THE
FAULTING SET IS A MEASUREMENT HERE AND NOT AN ASSERTION.** At `-O2` and above,
**clang does not fault on the row's own adversarial input -- it prints a WRONG
ANSWER.** The null dereference is UB, clang propagates *`retval` is non-NULL*
backwards from the dereference, and the sentinel path compiles into something
that computes a checksum nobody wrote. gcc faults at every level and clang faults
at `-O0` and `-O1`. ▶ **So this row's C failure mode is BUILD-DEPENDENT**, which
is `RECAP_PHP.md` F3 -- *a clean run is not evidence of absence* -- firing live on
a row that also has a faulting run to compare it against. The opt-level sweep
below is the measurement and `../NOTES.md` section 6 is the argument.

⚠ It also records the one thing spec.md's divergence ledger declares and no
gate input reaches: the four Rust rungs carry the `:385` guard at `:427` and R1h
does not, so they part on a state that is NOT in `inputs/`. That state is
`controls/second_limb.py`'s and is named here rather than left implicit.
"""
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
sys.path.insert(0, HERE)
sys.path.insert(0, PDIR)
import _pin  # noqa: E402
import model  # noqa: E402

SCRATCH = os.path.join(REPO, ".temp", "php96", "wdom")
RUSTC = os.path.expanduser("~/.cargo/bin/rustc")
VERUS = os.path.join(REPO, "verus_run.py")
CLANG = os.path.expanduser("~/tools/llvm/bin/clang")


def build_c(d, cc, ksrc):
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    out = os.path.join(d, "k")
    subprocess.run([cc, "-std=c99", "-O3", "-Wall", "-Wextra", "-DSLB_ISOLATED",
                    "-I", os.path.join(REPO, "common"),
                    "-I", os.path.join(PDIR, "c"),
                    os.path.join(REPO, "common", "driver.c"),
                    os.path.join(PDIR, "c", ksrc),
                    os.path.join(PDIR, "c", "main.c"), "-o", out],
                   check=True, capture_output=True)
    return out


def build_rs(d, rung):
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    out = os.path.join(d, "k")
    if rung == "verus":
        subprocess.run([sys.executable, VERUS, "--compile",
                        os.path.join(PDIR, "verus.rs"), "--cfg", "slb_isolated",
                        "-C", "opt-level=3", "-C", "codegen-units=1",
                        "-C", "debug-assertions=off", "-o", out],
                       check=True, capture_output=True, cwd=REPO)
    else:
        subprocess.run([RUSTC, "--edition", "2021", "-C", "codegen-units=1",
                        "-C", "opt-level=3", "-C", "debug-assertions=off",
                        "--cfg", "slb_isolated",
                        os.path.join(PDIR, rung + ".rs"), "-o", out],
                       check=True, capture_output=True)
    return out


def main():
    os.makedirs(SCRATCH, exist_ok=True)
    cdir = os.path.join(SCRATCH, "common")
    os.makedirs(cdir, exist_ok=True)
    shutil.copy(os.path.join(REPO, "common", "driver.rs"),
                os.path.join(cdir, "driver.rs"))
    problems = []
    cells = {}
    spec = [("c-gcc", "c", "gcc", "kernel.c"),
            ("c-gcc-h", "c", "gcc", "kernel_hardened.c"),
            ("c-clang", "c", CLANG, "kernel.c"),
            ("c-clang-h", "c", CLANG, "kernel_hardened.c"),
            ("safe_naive", "rs", None, "safe_naive"),
            ("safe_tuned", "rs", None, "safe_tuned"),
            ("unsafe", "rs", None, "unsafe"),
            ("verus", "rs", None, "verus")]
    for i, (name, kind, cc, src) in enumerate(spec):
        d = os.path.join(SCRATCH, f"v{i:02d}")
        cells[name] = build_c(d, cc, src) if kind == "c" else build_rs(d, src)
    assert len({len(os.path.dirname(p)) for p in cells.values()}) == 1, (
        "the eight build directories must have EQUAL PATH LENGTHS (F101)")

    inputs = sorted(f for f in os.listdir(os.path.join(PDIR, "inputs"))
                    if f.endswith(".bin"))
    rec = {"problems": problems, "cells": {}, "inputs": inputs,
           "model_stdout": {}}
    print(f"{'input':28s}" + "".join(f"{c:>13s}" for c in cells))
    faulting = []
    for inp in inputs:
        m = model.build(os.path.join(PDIR, "inputs", inp))
        want = m.expected_stdout.strip()
        rec["model_stdout"][inp] = want
        row = []
        for name, exe in cells.items():
            r = subprocess.run([exe, os.path.join(PDIR, "inputs", inp)],
                               capture_output=True, text=True, timeout=1800)
            got = r.stdout.strip()
            rec["cells"].setdefault(name, {})[inp] = {"exit": r.returncode,
                                                      "stdout": got}
            if r.returncode != 0:
                row.append("FAULT")
                faulting.append((inp, name))
            else:
                row.append("=model" if got == want else "DIFFER")
                # ⚠ ADVERSARIAL BEHAVIOUR IS RECORDED PER RUNG AND IS NOT
                # REQUIRED TO AGREE (`.memory/02-bench-rules.md`; the gate's own
                # stage 4 says the same). On this row that exemption is not
                # bookkeeping: `c-clang` at -O2 and above answers WRONGLY rather
                # than faulting, which is the opt sweep below and a finding.
                if got != want and not (inp.startswith("adversarial")
                                        and name in ("c-gcc", "c-clang")):
                    problems.append(f"{name} on {inp} printed {got!r}, model "
                                    f"says {want!r}")
        print(f"{inp:28s}" + "".join(f"{c:>13s}" for c in row))

    rec["faulting_set"] = sorted(f"{i}/{c}" for i, c in faulting)
    print(f"\nfaulting set (O3): {rec['faulting_set']}")
    # ⚠ NOT an assertion on WHICH cells fault -- see the module header. What IS
    # asserted is that no cell faults on an input the row calls benign, and that
    # every R1h cell answers.
    for i, c in faulting:
        if not i.startswith("adversarial"):
            problems.append(f"{c} faults on {i}, which the row calls benign")
        if c.endswith("-h") or c in ("safe_naive", "safe_tuned", "unsafe",
                                     "verus"):
            problems.append(f"{c} faults on {i}; only the two R1 cells may")

    # the R1-vs-R1h disagreement set, from the recorded stdout
    dis = []
    for inp in inputs:
        for a, b in (("c-gcc", "c-gcc-h"), ("c-clang", "c-clang-h")):
            ra, rb = rec["cells"][a][inp], rec["cells"][b][inp]
            if ra["exit"] != rb["exit"] or ra["stdout"] != rb["stdout"]:
                dis.append(f"{inp}/{a}-vs-{b}")
    rec["r1_vs_r1h_disagreements"] = dis
    print(f"R1-vs-R1h disagreements: {dis}")
    if len(dis) != 2 or any("adversarial-unset" not in d for d in dis):
        problems.append(f"R1 and R1h disagree on {dis}; the row's claim is that "
                        f"they agree on every input but the one R1 faults on, "
                        f"which is what makes stage 7h have nothing to refuse")

    # ---- the opt-level sweep: WHAT the C defect does, per build ----------
    print("\n\u26d4\u26d4 THE C FAILURE MODE IS BUILD-DEPENDENT. R1 on "
          "adversarial-unset.bin:")
    shim = os.path.join(SCRATCH, "segaddr.so")
    subprocess.run(["gcc", "-shared", "-fPIC", "-O0", "-o", shim,
                    os.path.join(REPO, ".tasks-php", "probes", "segaddr.c")],
                   check=True, capture_output=True)
    want = rec["model_stdout"]["adversarial-unset.bin"]
    rec["opt_sweep"] = {}
    print(f"   {'compiler':10s}{'opt':6s}{'rc':>5s}  {'si_addr':10s} outcome")
    for cc, cname in (("gcc", "gcc"), (CLANG, "clang")):
        for o in ("-O0", "-O1", "-O2", "-O3"):
            d = os.path.join(SCRATCH, "s0")
            shutil.rmtree(d, ignore_errors=True)
            os.makedirs(d)
            out = os.path.join(d, "k")
            subprocess.run([cc, "-std=c99", o, "-DSLB_ISOLATED",
                            "-I", os.path.join(REPO, "common"),
                            "-I", os.path.join(PDIR, "c"),
                            os.path.join(REPO, "common", "driver.c"),
                            os.path.join(PDIR, "c", "kernel.c"),
                            os.path.join(PDIR, "c", "main.c"), "-o", out],
                           check=True, capture_output=True)
            r = subprocess.run([out, os.path.join(PDIR, "inputs",
                                                  "adversarial-unset.bin")],
                               capture_output=True, text=True, timeout=600,
                               env=dict(os.environ, LD_PRELOAD=shim))
            import re as _re
            a = _re.search(r"si_addr=(\S+)", r.stderr or "")
            addr = a.group(1) if a else None
            got = r.stdout.strip()
            if r.returncode != 0:
                kind = "SIGSEGV -- the defect, detected"
            elif got == want:
                kind = "the R1h answer -- the defect did not happen"
            else:
                kind = "SILENT WRONG ANSWER -- UB exploited, not lowered"
            rec["opt_sweep"][f"{cname}{o}"] = {"exit": r.returncode,
                                               "si_addr": addr, "stdout": got,
                                               "outcome": kind}
            print(f"   {cname:10s}{o:6s}{r.returncode:>5d}  "
                  f"{str(addr):10s} {kind}")
    kinds = {v["outcome"] for v in rec["opt_sweep"].values()}
    rec["opt_sweep_distinct_outcomes"] = sorted(kinds)
    if len(kinds) < 2:
        problems.append("the opt sweep finds ONE outcome across eight builds, "
                        "so the build-dependence claim in the module header and "
                        "in NOTES.md section 6 is not reproduced")
    if any(v["outcome"].startswith("the R1h answer")
           for v in rec["opt_sweep"].values()):
        problems.append("some build of R1 produces the R1h answer on the "
                        "adversarial input, which would mean the defect is not "
                        "reachable in that build and the row owes an "
                        "explanation")

    rec["declared_but_unreached"] = (
        "the four Rust rungs carry the `:385` guard at `:427` and R1h does not "
        "(spec.md's divergence ledger, last entry). No input in `inputs/` "
        "reaches that state, by design -- an input that did would fault in R1h "
        "and stage 7h fails a row whose R1h fires a sanitizer on ANY input. "
        "controls/second_limb.py drives it.")
    print(f"\n⚠ {rec['declared_but_unreached']}")

    rec.update(_pin.pin(["c/kernel.c", "c/kernel_hardened.c", "safe_naive.rs",
                         "safe_tuned.rs", "unsafe.rs", "verus.rs", "model.py"],
                        "python3 controls/widened_domain.py",
                        "eight builds and 56 runs; minutes"))
    with open(os.path.join(HERE, "widened_domain.json"), "w") as f:
        json.dump(rec, f, indent=1)
        f.write("\n")
    print(f"\nwrote controls/widened_domain.json -- {len(problems)} problem(s)")
    for p in problems:
        print("  ⛔ " + p)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
