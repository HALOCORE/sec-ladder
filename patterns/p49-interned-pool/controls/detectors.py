#!/usr/bin/env python3
"""p49 CONTROLS: **every detector, on every arm, on every input -- and the three
positive controls that make the silence mean something.**

    python3 patterns/p49-interned-pool/controls/detectors.py

WHY THIS ROW NEEDS IT MORE THAN ANY OTHER
-----------------------------------------
⚠⚠ **Every detector column on p49 is SILENT, including on the buggy rung and on
the adversarial inputs.** Nothing is allocated, nothing is freed, no pointer
dangles, and `../c/kernel.h` proves in four lines that every index is inside
`mem[0 .. MEM)`. **The checksum is the only instrument this row has.**

That makes a positive control load-bearing in a way it is not elsewhere: on a
row where every column is silent, *a control that fires is the only thing
standing between "silent" and "not linked in"*. So this ships THREE, and the
middle one is row-specific:

  1. `ctl_asan.c`        a heap use-after-free -- ASan is linked and speaking
                         about the HEAP.
  2. `ctl_asan_stack.c`  ⚠ **`c/kernel.c`'s own store, one byte outside a local
                         `[u8; 64]`** -- ASan is linked and speaking about the
                         STACK ARRAY p49's write actually lives in. Without it,
                         *ASan is silent on p49* would be compatible with *ASan
                         cannot see this class of object*.
  3. `ctl_ubsan.c`       a signed integer overflow -- UBSan is linked and
                         speaking. `ctl_asan.c` cannot license this column:
                         `-fsanitize=undefined` has no use-after-free check, so
                         a UBSan build of it is silent, which is what an absent
                         UBSan looks like.

⚠⚠ **AND ONE MEASURED CORRECTION, RECORDED RATHER THAN QUIETLY RELAXED.** This
file's first `CONTROLS` table expected `ctl_asan_stack` to be SILENT under
UBSan, and the run said otherwise on **both compilers at both levels**: UBSan's
`-fsanitize=bounds` reports `index 64 out of bounds for type 'unsigned char[64]'`,
because the array's extent is a compile-time constant. **That makes the control
STRONGER, not weaker** -- it licenses the stack-array class in BOTH detector
columns, so *both* instruments demonstrably can see a stray store to the pool
and *both* are silent on p49.

WHAT IT RUNS
------------
`c/kernel.c` (R1) and `c/kernel_hardened.c` (R1h), each with gcc and clang, at
`-O0` and `-O3`, under `plain`, `-fsanitize=address` and
`-fsanitize=undefined` -- 24 binaries -- over **every** `.bin` in `../inputs/`,
adversarial ones included. ⚠ `p28d`'s lesson is that the hardened arm is the one
no stage ran a detector on until `TASK_151`, so it is here on equal terms.

Each control is built with **the same compiler and the same flags** as the
binaries whose column it licenses, and every child runs with `LD_PRELOAD`
unset.

WHAT IT ASSERTS
---------------
  * every control FIRES in its own detector and is SILENT in the others;
  * no kernel cell produces any ASan or UBSan diagnostic, on any input;
  * R1 and R1h agree on every non-adversarial input and differ on every
    adversarial one except `adversarial-stride3.bin` -- the divergence is the
    only instrument, so it is asserted here too.
"""

import glob
import hashlib
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PDIR = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(PDIR))
COMMON = os.path.join(REPO, "common")
CDIR = os.path.join(PDIR, "c")
SCRATCH = os.path.join(REPO, ".temp", "p49ctl", "detectors")

GCC = os.environ.get("SLB_GCC", "/usr/bin/gcc")
CLANG = os.environ.get("SLB_CLANG", os.path.expanduser("~/tools/llvm/bin/clang"))

SAN = {"plain": [],
       "asan": ["-fsanitize=address", "-fno-omit-frame-pointer"],
       "ubsan": ["-fsanitize=undefined"]}

ASAN_RE = re.compile(r"ERROR: AddressSanitizer: ([a-z-]+)")
UBSAN_RE = re.compile(r"runtime error: ([^\n]+)")

#: The one adversarial input whose windows the driver guard skips entirely, so
#: R1 and R1h agree on it. Naming it here is what stops the divergence assertion
#: from being a rule with a silent exception.
NO_DIVERGE = ("adversarial-stride3.bin",)

#: What each control must produce under each build. `None` means "no diagnostic
#: at all". ⚠ `ctl_asan_stack` fires in BOTH sanitizers and that is a RESULT,
#: not an accident: UBSan's `-fsanitize=bounds` sees a constant-extent array
#: indexed out of range, so **both instruments can see a stray store to the
#: pool, and both are silent on p49**. The first spelling of this table expected
#: silence there and the run said otherwise on both compilers at both levels --
#: recorded rather than quietly relaxed.
CONTROLS = {
    "ctl_asan": {"plain": None, "asan": "heap-use-after-free", "ubsan": None},
    "ctl_asan_stack": {"plain": None, "asan": "stack-buffer-overflow",
                       "ubsan": "out of bounds for type"},
    "ctl_ubsan": {"plain": None, "asan": None,
                  "ubsan": "signed integer overflow"},
}


def env():
    e = dict(os.environ)
    e.pop("LD_PRELOAD", None)          # `.memory/00-environment.md`
    e["ASAN_OPTIONS"] = "detect_leaks=0"
    return e


def build_kernel(cc, opt, san, kernel, out):
    cmd = ([cc, "-std=c99", "-Wall", "-Wextra", "-g",
            "-O0" if opt == "O0" else "-O3", "-DSLB_ISOLATED"]
           + SAN[san]
           + ["-I", COMMON, "-I", CDIR,
              os.path.join(COMMON, "driver.c"),
              os.path.join(CDIR, kernel),
              os.path.join(CDIR, "main.c"), "-o", out])
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        raise SystemExit(f"detectors.py: build failed:\n{' '.join(cmd)}\n"
                         f"{r.stderr}")
    return out


def build_ctl(cc, opt, san, name, out):
    cmd = ([cc, "-std=c99", "-Wall", "-Wextra", "-g",
            "-O0" if opt == "O0" else "-O3"] + SAN[san]
           + [os.path.join(HERE, name + ".c"), "-o", out])
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        raise SystemExit(f"detectors.py: control build failed:\n"
                         f"{' '.join(cmd)}\n{r.stderr}")
    return out


def run(exe, *args):
    r = subprocess.run([exe, *args], capture_output=True, text=True,
                       timeout=900, env=env())
    blob = r.stdout + r.stderr
    a = ASAN_RE.search(blob)
    u = UBSAN_RE.search(blob)
    return {"rc": r.returncode,
            "stdout": r.stdout.strip().splitlines()[-1] if r.stdout.strip() else "",
            "asan": a.group(1) if a else None,
            "ubsan": u.group(1) if u else None}


def derived_from():
    out = {}
    for rel in ("patterns/p49-interned-pool/c/kernel.c",
                "patterns/p49-interned-pool/c/kernel_hardened.c",
                "patterns/p49-interned-pool/c/main.c",
                "patterns/p49-interned-pool/c/kernel.h",
                "patterns/p49-interned-pool/inputs/gen.py",
                "patterns/p49-interned-pool/controls/ctl_asan.c",
                "patterns/p49-interned-pool/controls/ctl_asan_stack.c",
                "patterns/p49-interned-pool/controls/ctl_ubsan.c",
                "patterns/p49-interned-pool/controls/detectors.py"):
        p = os.path.join(REPO, rel)
        out[rel] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return out


def main():
    os.makedirs(SCRATCH, exist_ok=True)
    problems = []
    ccs = [("gcc", GCC)]
    if os.path.exists(CLANG):
        ccs.append(("clang", CLANG))
    else:
        problems.append(f"clang not found at {CLANG}; the clang half of this "
                        f"census did not run")
    inputs = sorted(glob.glob(os.path.join(PDIR, "inputs", "*.bin")))
    if not inputs:
        print("detectors.py: no .bin files -- run inputs/gen.py first",
              file=sys.stderr)
        return 1

    # ---- 1. the three positive controls ----------------------------------
    print("1. POSITIVE CONTROLS -- each must FIRE in its own detector and be "
          "SILENT in the others")
    ctl_rows = []
    for tag, cc in ccs:
        for opt in ("O0", "O3"):
            for name, want in CONTROLS.items():
                for san in ("plain", "asan", "ubsan"):
                    want_txt = want[san]
                    exe = build_ctl(cc, opt, san,
                                    name, os.path.join(
                                        SCRATCH, f"{name}.{tag}.{opt}.{san}"))
                    res = run(exe)
                    fired = res["asan"] if san == "asan" else (
                        res["ubsan"] if san == "ubsan" else None)
                    ok = (fired is None) if want_txt is None \
                        else (want_txt in (fired or ""))
                    ctl_rows.append({"control": name, "cc": tag, "opt": opt,
                                     "san": san, "fired": fired, "ok": ok})
                    mark = "FIRED" if fired else "silent"
                    print(f"    {name:16s} {tag:5s} {opt:3s} {san:6s} "
                          f"{mark:6s} {fired or ''}"
                          + ("" if ok else "   <-- UNEXPECTED"))
                    if not ok:
                        problems.append(
                            f"{name} under {tag} {opt} {san}: expected "
                            + (f"`{want_txt}`" if want_txt else "silence")
                            + f", got {fired!r}. A control that cannot fire "
                              f"proves nothing, and on p49 the controls are the "
                              f"ONLY evidence that the silent columns below are "
                              f"a fact about the program")
                    os.unlink(exe)

    # ---- 2. the kernels ---------------------------------------------------
    print("\n2. THE KERNELS -- R1 and R1h, every compiler x level x detector x "
          "input")
    rows, answers = [], {}
    for tag, cc in ccs:
        for opt in ("O0", "O3"):
            for arm, kern in (("R1", "kernel.c"), ("R1h", "kernel_hardened.c")):
                for san in ("plain", "asan", "ubsan"):
                    exe = build_kernel(cc, opt, san, kern, os.path.join(
                        SCRATCH, f"{arm}.{tag}.{opt}.{san}"))
                    for path in inputs:
                        name = os.path.basename(path)
                        res = run(exe, path)
                        rows.append({"arm": arm, "cc": tag, "opt": opt,
                                     "san": san, "input": name, **res})
                        answers.setdefault((arm, name), set()).add(res["stdout"])
                        if res["asan"] or res["ubsan"]:
                            problems.append(
                                f"{arm} {tag} {opt} {san} on {name}: "
                                f"asan={res['asan']} ubsan={res['ubsan']}. p49's "
                                f"claim is that NO detector fires on ANY input "
                                f"in EITHER rung -- that is the row's headline, "
                                f"and a hit refutes it")
                        if res["rc"] != 0:
                            problems.append(
                                f"{arm} {tag} {opt} {san} on {name}: exit "
                                f"{res['rc']}")
                    os.unlink(exe)

    n_diag = sum(1 for r in rows if r["asan"] or r["ubsan"])
    print(f"    {len(rows)} cell(s) run; {n_diag} carried a diagnostic")
    print(f"\n{'input':32s} {'R1':>22s} {'R1h':>22s}  agree?")
    diverge = {}
    for path in inputs:
        name = os.path.basename(path)
        a = answers.get(("R1", name), set())
        b = answers.get(("R1h", name), set())
        if len(a) != 1 or len(b) != 1:
            problems.append(f"{name}: an arm produced more than one answer "
                            f"across the 12 cells ({a} / {b})")
            continue
        av, bv = a.pop(), b.pop()
        same = av == bv
        diverge[name] = not same
        adv = name.startswith("adversarial-")
        print(f"{name:32s} {av:>22s} {bv:>22s}  {'YES' if same else 'no '}"
              + ("   <-- adversarial" if adv else ""))
        if not adv and not same:
            problems.append(f"{name} is a MATRIX input and the two C rungs "
                            f"DISAGREE, which check.py stage 2 forbids")
        if adv and name not in NO_DIVERGE and same:
            problems.append(
                f"{name} is an ADVERSARIAL input and the two C rungs AGREE. On "
                f"a row where every detector is silent the divergence IS the "
                f"instrument, so an adversarial input that does not diverge "
                f"measures nothing")

    doc = {"pin": {"regenerate": "python3 patterns/p49-interned-pool/controls/"
                                 "detectors.py"},
           "derived_from_sha256": derived_from(),
           "measured_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "compilers": [t for t, _ in ccs],
           "controls": ctl_rows,
           "cells": rows,
           "diagnostics": n_diag,
           "diverges": diverge,
           "problems": problems,
           "invariant": "Three positive controls fire where the CONTROLS table "
                        "says and nowhere else, under both compilers at both "
                        "optimisation levels -- and ctl_asan_stack fires in BOTH "
                        "sanitizers, which licenses the stack-array class in "
                        "both columns. With them firing, NO kernel cell "
                        "-- buggy or hardened, any compiler, any level, any "
                        "input including the adversarial ones -- produces an "
                        "ASan or UBSan diagnostic. The two C rungs agree on "
                        "every matrix input and disagree on every adversarial "
                        "one except adversarial-stride3.bin, and on this row "
                        "that divergence is the only instrument there is."}
    out = os.path.join(HERE, "detectors.json")
    json.dump(doc, open(out, "w"), indent=2)
    print(f"wrote {out}")
    for p in problems:
        print(f"  *** {p}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
