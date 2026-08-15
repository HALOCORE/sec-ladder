#!/usr/bin/env python3
"""Run Verus (or cargo-verus) with the right toolchain, from a throwaway scratch
dir so build artefacts don't pollute the repo.

Adapted from LearnVeri's `verus_check.py`, with three additions this repo needs:
  * locates the Verus install itself (no PATH setup required in your shell),
  * puts rustup's bin dir on PATH so Verus can find its pinned rustc,
  * a `--cargo` mode for whole-crate `cargo verus build/verify` runs.

Usage:
    ./verus_run.py <file.rs> [verus flags...]      # single-file verify
    ./verus_run.py --compile <file.rs> -o out      # verify + compile a binary
    ./verus_run.py --cargo build [cargo flags...]  # whole crate, from cwd
    ./verus_run.py --info                          # show resolved toolchain

Options handled here (everything else is forwarded verbatim):
    --cargo    run `cargo verus <args>` in the current directory instead of a
               scratch dir (cargo manages its own target/, so no temp dance)
    --keep     don't delete the scratch dir; print its path (to inspect .vir,
               logs, or emitted assembly)
    --info     print the resolved verus/rustup paths and versions, then exit

Verus is found by trying, in order: $VERUS_BIN (path to the binary),
$VERUS_HOME/verus, ~/tools/verus/verus, then `verus` on PATH.

Examples:
    ./verus_run.py patterns/p01-array-sum/rust-verus/src/lib.rs --crate-type=lib
    ./verus_run.py --compile bench.rs -o bench   # -o stays relative to YOUR cwd
    ./verus_run.py --keep --compile bench.rs --emit=asm
"""
import os
import shutil
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.abspath(__file__))
CANDIDATES = [
    os.environ.get("VERUS_BIN"),
    os.path.join(os.environ.get("VERUS_HOME", ""), "verus") if os.environ.get("VERUS_HOME") else None,
    os.path.expanduser("~/tools/verus/verus"),
]


def find_verus():
    for c in CANDIDATES:
        if c and os.path.isfile(c) and os.access(c, os.X_OK):
            return os.path.abspath(c)
    onpath = shutil.which("verus")
    if onpath:
        return os.path.abspath(onpath)
    sys.exit(
        "verus_run.py: no Verus install found.\n"
        "  Tried $VERUS_BIN, $VERUS_HOME/verus, ~/tools/verus/verus, and PATH.\n"
        "  See TOOLCHAIN.md for the install steps."
    )


def build_env(verus_bin):
    """Verus shells out to rustup to select its pinned rustc, and cargo-verus
    lives next to the verus binary — so both dirs must be on PATH."""
    env = dict(os.environ)
    cargo_bin = os.path.expanduser("~/.cargo/bin")
    parts = [os.path.dirname(verus_bin)]
    if os.path.isdir(cargo_bin):
        parts.append(cargo_bin)
    env["PATH"] = os.pathsep.join(parts + [env.get("PATH", "")])
    return env


def resolve(arg, prev):
    # The verifier runs with cwd inside a scratch dir, so any path arg must be
    # made absolute first or it won't be found.
    if arg.endswith(".rs") or (not arg.startswith("-") and os.path.exists(arg)):
        return os.path.abspath(arg)
    if prev in ("-o", "--export", "--import", "--log-dir"):
        return os.path.abspath(arg)
    return arg


def info(verus_bin, env):
    print(f"verus binary : {verus_bin}")
    print(f"verus dir    : {os.path.dirname(verus_bin)}")
    for cmd in (["verus", "--version"], ["rustup", "show", "active-toolchain"]):
        try:
            out = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=120)
            print(f"--- {' '.join(cmd)} ---\n{(out.stdout + out.stderr).strip()}")
        except (OSError, subprocess.TimeoutExpired) as e:
            print(f"--- {' '.join(cmd)} --- FAILED: {e}")
    return 0


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__.strip())
        return 2

    keep = "--keep" in args
    args = [a for a in args if a != "--keep"]
    verus_bin = find_verus()
    env = build_env(verus_bin)

    if args == ["--info"]:
        return info(verus_bin, env)

    if args and args[0] == "--cargo":
        # Whole-crate mode: cargo needs the real crate dir as cwd.
        return subprocess.run(["cargo", "verus", *args[1:]], env=env).returncode

    resolved, prev = [], None
    for a in args:
        resolved.append(resolve(a, prev))
        prev = a

    temp_root = os.path.join(REPO, ".temp", "verus")
    os.makedirs(temp_root, exist_ok=True)
    td = tempfile.mkdtemp(prefix="run.", dir=temp_root)
    try:
        rc = subprocess.run([verus_bin, *resolved], cwd=td, env=env).returncode
    finally:
        if keep:
            print(f"[verus_run] scratch dir kept: {td}", file=sys.stderr)
        else:
            shutil.rmtree(td, ignore_errors=True)
    return rc


if __name__ == "__main__":
    sys.exit(main())
