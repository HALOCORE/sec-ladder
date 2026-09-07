#!/usr/bin/env python3
"""Run the UNMODIFIED PAT harness against a php row, through the symlink shim.

    python3 harness-php/gate.py ph00                    # harness/check.py ph00
    python3 harness-php/gate.py --tool measure ph00     # harness/measure.py
    python3 harness-php/gate.py --tool report  ph00     # harness/report.py
    python3 harness-php/gate.py --tool build   ph00     # harness/build.py
    python3 harness-php/gate.py --tool measure --check-stale
    python3 harness-php/gate.py --preflight              # preflight only

⚠ THE THREE-COMMAND LOOP for a row that has never been measured, and it is
three and not two -- `harness/check.py::check_published_tables` says so at length, because
`report.py::load` needs `results/<row>-*.json` (MEASURE's record) and exits
without it, while stage 9 fails if `results/tables/<row>.md` is absent:

    harness-php/gate.py --tool measure ph00
    harness-php/gate.py --tool report  ph00
    harness-php/gate.py                ph00

============================================================================
WHAT THIS FILE IS, AND WHAT IT IS FORBIDDEN TO BE
============================================================================
It is a PREFLIGHT plus an `exec`. It REIMPLEMENTS NO GATE STAGE and must
never grow one: the whole value of `PLAN_PHP.md` §2.1a is that the php rows
are judged by the SAME code as the 33 PAT rows, so a php-only stage here
would be a second, unvalidated gate wearing the first one's name. If a php
row needs a check the PAT gate does not have, it goes in that row's
`controls/` or in a separate tool, and the report says which.

The preflight is three things, all of which can fail:

  1. `harness-php/root.py` -- the shim exists and every link points where it
     should, and nothing that is not a link lives in it.
  2. `common-php/digest_bridge.py --verify` -- every `common-php/` file is in
     some digest. ⚠ `check.py`'s `common/` globs are `driver.*`, `*.py` and
     `layout/*.py`, ALL NON-RECURSIVE, so `emalloc_shim.h` is in none of them
     and the bridge is what covers it. Ten committed control sources sat in no
     digest at all on the PAT side for many tasks; this is that check.
  3. `harness-php/provenance.py` -- the row's `provenance.extract_sha256`
     really is the sha256 of the lines it names, out of the pinned tarball.
     Skipped with `--no-provenance`, which prints a loud line, because a box
     without the tarball must still be able to re-gate.

============================================================================
PYTHONDONTWRITEBYTECODE, and why it is not superstition
============================================================================
Importing `check.py` through `.temp/php-root/harness/` writes the `.pyc` into
the REAL `harness/__pycache__/` (the OS resolves the link) with the SHIM path
recorded as `co_filename`, so a later PAT traceback would name a path under
`.temp/`. Measured at `TASK_PHP_002` (`.temp/php0/pycdemo`). It moves no hash,
but it is a write into a directory this programme has promised not to touch,
and one environment variable removes it.
"""

import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import root as rootmod  # noqa: E402

TOOLS = {
    "check": "check.py",
    "measure": "measure.py",
    "report": "report.py",
    "build": "build.py",
}


def preflight(row, do_provenance=True):
    """Returns a list of problems. Empty means go."""
    problems = []
    print("preflight")
    rootmod.build(verbose=False)
    bad = rootmod.check()
    for b in bad:
        problems.append(f"shim: {b}")
    print(f"  {'ok  ' if not bad else 'FAIL'} shim {rootmod.SHIM}")

    r = subprocess.run([sys.executable,
                        os.path.join(REPO, "common-php", "digest_bridge.py"),
                        "--verify"], capture_output=True, text=True)
    if r.returncode != 0:
        problems.append("digest bridge:\n" + r.stdout + r.stderr)
    print(f"  {'ok  ' if r.returncode == 0 else 'FAIL'} common-php/ digest bridge")

    if row and do_provenance:
        r = subprocess.run([sys.executable,
                            os.path.join(HERE, "provenance.py"), row],
                           capture_output=True, text=True)
        if r.returncode != 0:
            problems.append("provenance:\n" + r.stdout + r.stderr)
        print(f"  {'ok  ' if r.returncode == 0 else 'FAIL'} provenance {row}")
        for ln in r.stdout.splitlines():
            if ln.strip():
                print(f"       | {ln}")
    elif row:
        print(f"  !!   provenance SKIPPED for {row} (--no-provenance). This "
              f"run certifies nothing about where the kernel came from.")
    return problems


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tool", default="check", choices=sorted(TOOLS))
    ap.add_argument("--no-provenance", action="store_true")
    ap.add_argument("--preflight", action="store_true",
                    help="run the preflight and stop")
    ap.add_argument("args", nargs=argparse.REMAINDER,
                    help="passed to the tool verbatim")
    # ⚠ `parse_known_args`, not `parse_args`, and it is not cosmetic:
    # `argparse.REMAINDER` only starts collecting at the first POSITIONAL, so
    # a tool flag with no positional after it -- `--tool measure
    # --check-stale`, which this module's own docstring advertises -- was
    # rejected by the top-level parser as an unrecognised argument.
    # Found by running the docstring (TASK_PHP_002).
    a, unknown = ap.parse_known_args()

    argv = [x for x in (unknown + a.args) if x != "--"]
    row = next((x for x in argv if not x.startswith("-")), None)

    problems = preflight(row, not a.no_provenance)
    if problems:
        print("\nPREFLIGHT FAILED -- the tool was NOT run:")
        for p in problems:
            print(f"  {p}")
        return 2
    if a.preflight:
        print("\npreflight OK (nothing else run)")
        return 0

    tool = os.path.join(rootmod.SHIM, "harness", TOOLS[a.tool])
    cmd = [sys.executable, tool] + argv
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    print(f"\n$ {' '.join(cmd)}\n  (REPO for that process = {rootmod.SHIM})\n")
    sys.stdout.flush()
    return subprocess.run(cmd, cwd=rootmod.SHIM, env=env).returncode


if __name__ == "__main__":
    sys.exit(main())
