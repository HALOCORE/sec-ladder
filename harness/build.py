#!/usr/bin/env python3
"""Build the ladder matrix for a pattern.

Matrix (`.memory/01-ladder.md`): 6 measured cells x 2 opt levels x 2 inline
modes = 24 builds.

  cells   c-gcc  c-clang  safe_naive  safe_tuned  unsafe  verus
  opt     O0     O3
  mode    isolated  whole

Plus three opt-in axes that are *not* in the default 24 and must be reported
separately if used:

  --cell safe_naive_verus   the R2v control (safe Rust + proof); holds up
                            `.memory/01-ladder.md` finding 2
  --opt O0d                 Rust with debug-assertions=ON. This is NOT
                            semantics-matched to C -O0: it inserts integer
                            overflow checks. Never compare it to a C column.
  --panic abort             deletes landing pads; a real safety-cost lever

Outputs land in `.temp/build/<pNN>/<cell>-<opt>-<mode>[-abort]`, never in the
pattern dir (`.memory/05-layout.md`).

  harness/build.py p01                       # the 24
  harness/build.py p01 --cell unsafe --opt O3 --mode isolated
  harness/build.py p01 --all                 # the 24 + the R2v control
  harness/build.py p01 --list
"""

import argparse
import os
import shutil
import subprocess
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMMON = os.path.join(REPO, "common")
PATTERNS = os.path.join(REPO, "patterns")
BUILD_ROOT = os.path.join(REPO, ".temp", "build")

GCC = os.environ.get("SLB_GCC", "/usr/bin/gcc")
CLANG = os.environ.get("SLB_CLANG", os.path.expanduser("~/tools/llvm/bin/clang"))
RUSTC = os.environ.get("SLB_RUSTC", os.path.expanduser("~/.cargo/bin/rustc"))
VERUS_RUN = os.path.join(REPO, "verus_run.py")

MEASURED_CELLS = ["c-gcc", "c-clang", "safe_naive", "safe_tuned", "unsafe", "verus"]
CONTROL_CELLS = ["safe_naive_verus"]
ALL_CELLS = MEASURED_CELLS + CONTROL_CELLS
OPTS = ["O0", "O3"]
ALL_OPTS = ["O0", "O0d", "O3"]
MODES = ["isolated", "whole"]

# Rung -> source stem. `c-gcc` and `c-clang` share c/.
RUST_SRC = {
    "safe_naive": "safe_naive.rs",
    "safe_tuned": "safe_tuned.rs",
    "unsafe": "unsafe.rs",
    "verus": "verus.rs",
    "safe_naive_verus": "safe_naive_verus.rs",
}


def pattern_dir(pat):
    """`p01` -> patterns/p01-array-sum."""
    if os.path.isdir(os.path.join(PATTERNS, pat)):
        return os.path.join(PATTERNS, pat)
    hits = sorted(d for d in os.listdir(PATTERNS)
                  if d.startswith(pat + "-") or d == pat)
    if len(hits) != 1:
        raise SystemExit(f"build.py: {pat!r} matches {hits or 'nothing'} in {PATTERNS}")
    return os.path.join(PATTERNS, hits[0])


def pattern_id(pdir):
    return os.path.basename(pdir).split("-")[0]


def out_path(pdir, cell, opt, mode, panic):
    d = os.path.join(BUILD_ROOT, pattern_id(pdir))
    os.makedirs(d, exist_ok=True)
    suffix = "" if panic == "unwind" else f"-{panic}"
    return os.path.join(d, f"{cell}-{opt}-{mode}{suffix}")


# --------------------------------------------------------------------------

def c_flags(opt, mode, panic):
    f = ["-std=c99", "-Wall", "-Wextra"]
    f.append("-O0" if opt in ("O0", "O0d") else "-O3")
    if mode == "isolated":
        # SLB_ISOLATED turns on __attribute__((noinline)) for the kernel; the
        # separate TUs and absence of LTO do the rest (.memory/02-bench-rules.md
        # rule 3).
        f.append("-DSLB_ISOLATED")
    else:
        f.append("-flto")
    del panic  # C rungs have no landing pads to delete
    return f


def rust_flags(opt, mode, panic):
    f = ["--edition", "2021", "-C", "codegen-units=1"]
    if opt == "O0":
        f += ["-C", "opt-level=0", "-C", "debug-assertions=off"]
    elif opt == "O0d":
        f += ["-C", "opt-level=0", "-C", "debug-assertions=on"]
    else:
        f += ["-C", "opt-level=3", "-C", "debug-assertions=off"]
    if mode == "isolated":
        f += ["--cfg", "slb_isolated"]
    # `whole` mode adds nothing: a single-crate Rust binary with
    # codegen-units=1 already has the kernel and the driver loop in one module,
    # which is exactly what -flto buys the three-TU C build. `-C lto=fat` is
    # NOT used, because Verus links a precompiled vstd rlib that carries no
    # bitcode ("failed to get bitcode from object file for LTO"), so R5 could
    # not have it and the rungs would stop being comparable. See NOTES.md.
    if panic == "abort":
        f += ["-C", "panic=abort"]
    return f


def build_c(pdir, cc, opt, mode, panic, out, dry):
    srcs = [os.path.join(COMMON, "driver.c"),
            os.path.join(pdir, "c", "kernel.c"),
            os.path.join(pdir, "c", "main.c")]
    cmd = [cc] + c_flags(opt, mode, panic) + \
        ["-I", COMMON, "-I", os.path.join(pdir, "c")] + srcs + ["-o", out]
    if mode == "whole" and "clang" in os.path.basename(cc):
        lld = os.path.expanduser("~/tools/llvm/bin/ld.lld")
        if os.path.exists(lld):
            cmd.insert(1, "-fuse-ld=lld")
    return run(cmd, dry)


def build_rust(pdir, cell, opt, mode, panic, out, dry):
    src = os.path.join(pdir, RUST_SRC[cell])
    cmd = [RUSTC] + rust_flags(opt, mode, panic) + [src, "-o", out]
    return run(cmd, dry)


def build_verus(pdir, cell, opt, mode, panic, out, dry):
    src = os.path.join(pdir, RUST_SRC[cell])
    # verus_run.py forwards unrecognised flags to rustc verbatim, --cfg included
    # (verified on this box). --edition is fixed by Verus, so it is not passed.
    flags = [f for f in rust_flags(opt, mode, panic) if f not in ("--edition", "2021")]
    cmd = [sys.executable, VERUS_RUN, "--compile", src, "-o", out] + flags
    return run(cmd, dry)


def run(cmd, dry):
    if dry:
        print("  " + " ".join(cmd))
        return 0, "", ""
    t0 = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO)
    return r.returncode, (r.stdout + r.stderr).strip(), f"{time.time() - t0:.1f}s"


def build_cell(pdir, cell, opt, mode, panic="unwind", dry=False, quiet=False):
    """Build one cell. Returns (ok, out_path, log)."""
    out = out_path(pdir, cell, opt, mode, panic)
    if cell == "c-gcc":
        rc, log, el = build_c(pdir, GCC, opt, mode, panic, out, dry)
    elif cell == "c-clang":
        rc, log, el = build_c(pdir, CLANG, opt, mode, panic, out, dry)
    elif cell in ("verus", "safe_naive_verus"):
        rc, log, el = build_verus(pdir, cell, opt, mode, panic, out, dry)
    elif cell in RUST_SRC:
        rc, log, el = build_rust(pdir, cell, opt, mode, panic, out, dry)
    else:
        raise SystemExit(f"build.py: unknown cell {cell!r}")
    ok = rc == 0 and (dry or os.path.exists(out))
    # Verus prints "N verified, 0 errors" on stdout even on success; warnings on
    # stderr are common and harmless, so only a non-zero rc is a failure.
    if not quiet:
        tag = "ok  " if ok else "FAIL"
        print(f"  {tag} {cell:18s} {opt:4s} {mode:9s} {el}")
        if log and (not ok or "warning" in log.lower()):
            for line in log.splitlines()[:20]:
                print(f"       | {line}")
    return ok, out, log


def check_toolchain():
    missing = [(n, p) for n, p in (("gcc", GCC), ("clang", CLANG), ("rustc", RUSTC))
               if not (os.path.exists(p) or shutil.which(p))]
    if missing:
        raise SystemExit("build.py: missing toolchain: " +
                         ", ".join(f"{n} at {p}" for n, p in missing))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pattern", help="pattern id or dir name, e.g. p01")
    ap.add_argument("--cell", action="append", choices=ALL_CELLS)
    ap.add_argument("--opt", action="append", choices=ALL_OPTS)
    ap.add_argument("--mode", action="append", choices=MODES)
    ap.add_argument("--panic", default="unwind", choices=["unwind", "abort"])
    ap.add_argument("--all", action="store_true",
                    help="include the R2v control cell")
    ap.add_argument("--list", action="store_true", help="print the matrix and exit")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    check_toolchain()
    pdir = pattern_dir(a.pattern)
    cells = a.cell or (ALL_CELLS if a.all else MEASURED_CELLS)
    opts = a.opt or OPTS
    modes = a.mode or MODES

    print(f"pattern {os.path.basename(pdir)}  ->  "
          f"{os.path.join(BUILD_ROOT, pattern_id(pdir))}")
    print(f"cells={cells} opts={opts} modes={modes} panic={a.panic} "
          f"({len(cells) * len(opts) * len(modes)} builds)")
    if a.list:
        for c in cells:
            for o in opts:
                for m in modes:
                    print("  " + os.path.basename(out_path(pdir, c, o, m, a.panic)))
        return 0

    failures = []
    for c in cells:
        for o in opts:
            for m in modes:
                ok, out, log = build_cell(pdir, c, o, m, a.panic, a.dry_run)
                if not ok:
                    failures.append((c, o, m, log))
    if failures:
        print(f"\n{len(failures)} build(s) FAILED:")
        for c, o, m, log in failures:
            print(f"  {c} {o} {m}")
            for line in (log or "").splitlines()[:15]:
                print(f"    | {line}")
        return 1
    print("all builds ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
