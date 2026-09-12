#!/usr/bin/env python3
"""ph45 control -- BUG #30573, MEASURED. The row can count its own bug report.

`e8901dc17087`'s subject line is *"- Fix bug #30573 (compiler warning due to
invalid type cast)"*, and the warning it names is one gcc still emits, at
`harness/build.py`'s own `-Wall -Wextra`, at exactly the four sites the patch
rewrites. ⭐ So there is no *"compiler-warning fix versus real fix"* distinction
to draw on this row at all: the warning and the memory-safety defect are the
SAME EVENT.

    python3 patterns-php/ph45-htmlent-cache-int/controls/warnings.py

⚠ `check.py` does not test warnings -- `check_build` fails only on a non-zero
compiler exit -- so this is a CONTROL and not a gate stage.

⚠⚠ AND THE THIRD COLUMN IS THE LADDER RESULT. The same idiom in Rust compiles
with ZERO diagnostics, even under `-D warnings`, and SIGSEGVs when run; Verus
refuses it and points at both cast sites (`controls/o1_roundtrip*.rs`). gcc says
four things, rustc says nothing, Verus says no. `../NOTES.md` section 10.
"""
import os
import re
import subprocess
import sys

ROW = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(os.path.dirname(ROW))
COMMON = os.path.join(REPO, "common")
GCC = os.environ.get("SLB_GCC", "/usr/bin/gcc")
CLANG = os.environ.get("SLB_CLANG", os.path.expanduser("~/tools/llvm/bin/clang"))
TMP = os.path.join(REPO, ".temp", "php45ctl")

# `harness/build.py::c_flags`, verbatim.
FLAGS = ["-std=c99", "-Wall", "-Wextra"]
WANT = {
    "kernel.c": {"-Wpointer-to-int-cast": 1, "-Wint-to-pointer-cast": 3},
    "kernel_hardened.c": {},
}
RX = re.compile(r"\[(-W[a-z0-9-]+)\]")
SITE = re.compile(r"kernel(?:_hardened)?\.c:(\d+):")


def compile_one(cc, ksrc, opt, mode):
    os.makedirs(TMP, exist_ok=True)
    out = os.path.join(TMP, "w.bin")
    cmd = ([cc] + FLAGS + [opt]
           + (["-DSLB_ISOLATED"] if mode == "isolated" else ["-flto"])
           + (["-fuse-ld=lld"] if (mode != "isolated" and "clang" in cc) else [])
           + ["-I", COMMON, "-I", os.path.join(ROW, "c"),
              os.path.join(COMMON, "driver.c"),
              os.path.join(ROW, "c", ksrc),
              os.path.join(ROW, "c", "main.c"), "-o", out])
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO)
    log = r.stdout + r.stderr
    hits = {}
    lines = {}
    for ln in log.splitlines():
        m = RX.search(ln)
        if m and "warning:" in ln:
            hits[m.group(1)] = hits.get(m.group(1), 0) + 1
            s = SITE.search(ln)
            if s:
                lines.setdefault(m.group(1), []).append(int(s.group(1)))
    return r.returncode, hits, lines


def main():
    print(__doc__.splitlines()[0])
    print(f"flags: {' '.join(FLAGS)} {{-O0|-O3}} {{-DSLB_ISOLATED|-flto}}")
    bad = 0
    for cc, name in ((GCC, "gcc"), (CLANG, "clang")):
        if not os.path.exists(cc):
            print(f"  SKIP {name}: not at {cc}")
            continue
        for ksrc in ("kernel.c", "kernel_hardened.c"):
            for opt in ("-O0", "-O3"):
                for mode in ("isolated", "whole"):
                    rc, hits, lines = compile_one(cc, ksrc, opt, mode)
                    tot = sum(hits.values())
                    tag = f"{name:5s} {ksrc:18s} {opt:4s} {mode:9s}"
                    detail = ", ".join(
                        f"{k} x{v} at {sorted(set(lines.get(k, [])))}"
                        for k, v in sorted(hits.items()))
                    print(f"  rc={rc} {tag} warnings={tot:2d}  {detail}")
                    if rc != 0:
                        print("       ⚠ NON-ZERO COMPILER EXIT")
                        bad += 1
                    if name == "gcc":
                        want = WANT[ksrc]
                        got = {k: v for k, v in hits.items() if k in
                               ("-Wpointer-to-int-cast", "-Wint-to-pointer-cast")}
                        if got != want:
                            print(f"       ⚠ EXPECTED {want}, GOT {got}")
                            bad += 1
    print()
    print("EXPECTED, and it is bug #30573: gcc emits -Wpointer-to-int-cast once")
    print("(mbfilter_htmlent.c:161, the STORE) and -Wint-to-pointer-cast three")
    print("times (:169 the FREE, :178 and :249 the two CASTS BACK) on R1, and")
    print("NOTHING on R1h -- four sites, and they are the four the patch rewrites.")
    print(f"-> {'PASS' if bad == 0 else 'FAIL'} ({bad} problem(s))")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
