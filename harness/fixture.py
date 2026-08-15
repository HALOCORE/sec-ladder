#!/usr/bin/env python3
"""Build the pilot fixture `harness/asm.py selftest` measures.

`asm.selftest()` re-derives every pilot number recorded in `.memory/01-ladder.md`
and `.memory/03-measurement.md` from six binaries in `.temp/build/docrepro/`.
Before TASK_003 nothing in the repo built them, so on a fresh checkout the
selftest returned 77 ("fixture missing"), `harness/check.py` downgraded that to a
note, and step 0 of the gate silently measured nothing (TASK_002_REVIEW, M11).

The flags are the ladder's, from `TOOLCHAIN.md` "Pilot reproduction" -- the same
`-O3 -C codegen-units=1 -C debug-assertions=off` the numbers were taken at.
Changing them invalidates the pinned digests, which is the point of pinning them.

    harness/fixture.py            # build any missing binary
    harness/fixture.py --force    # rebuild all six
    harness/fixture.py --check    # build if needed, then run the selftest
"""

import argparse
import os
import subprocess
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "harness"))
import asm  # noqa: E402
import build as buildmod  # noqa: E402

OUT = os.path.join(REPO, ".temp", "build", "docrepro")
PILOT = os.path.join(REPO, "pilot")

# The opt flags every rung shares (`.memory/01-ladder.md` build matrix).
C_FLAGS = ["-std=c99", "-Wall", "-Wextra", "-O3"]
RUST_FLAGS = ["-C", "opt-level=3", "-C", "debug-assertions=off",
              "-C", "codegen-units=1"]

# out-name -> (kind, source)
TARGETS = [
    ("k_gcc", "c", "k.c", buildmod.GCC),
    ("k_clang", "c", "k.c", buildmod.CLANG),
    ("k_rust", "rust", "k_rust.rs", None),
    ("k_unsafe", "rust", "k_unsafe.rs", None),
    ("k_verus", "verus", "k_verus.rs", None),
    ("k_unsafe_verus", "verus", "k_unsafe_verus.rs", None),
]


def cmd_for(name, kind, src, cc):
    out = os.path.join(OUT, name)
    src = os.path.join(PILOT, src)
    if kind == "c":
        return [cc] + C_FLAGS + [src, "-o", out]
    if kind == "rust":
        return [buildmod.RUSTC] + RUST_FLAGS + [src, "-o", out]
    return [sys.executable, os.path.join(REPO, "verus_run.py"), "--compile", src,
            "-o", out] + RUST_FLAGS


def build(force=False):
    os.makedirs(OUT, exist_ok=True)
    bad = 0
    for name, kind, src, cc in TARGETS:
        out = os.path.join(OUT, name)
        if os.path.exists(out) and not force:
            print(f"  have {name}")
            continue
        cmd = cmd_for(name, kind, src, cc)
        t0 = time.time()
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO)
        ok = r.returncode == 0 and os.path.exists(out)
        print(f"  {'ok  ' if ok else 'FAIL'} {name:16s} {time.time() - t0:5.1f}s")
        if not ok:
            bad += 1
            for line in (r.stdout + r.stderr).splitlines()[:15]:
                print(f"       | {line}")
    return bad


def ensure():
    """Build anything missing. Returns True if all six exist afterwards.

    `harness/check.py` calls this so the gate's step 0 cannot no-op."""
    if all(os.path.exists(os.path.join(OUT, n)) for n, _, _, _ in TARGETS):
        return True
    return build() == 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--check", action="store_true", help="run asm.selftest after")
    a = ap.parse_args()
    print(f"fixture -> {os.path.relpath(OUT, REPO)}")
    bad = build(force=a.force)
    if bad:
        return 1
    if a.check:
        return asm.selftest()
    return 0


if __name__ == "__main__":
    sys.exit(main())
