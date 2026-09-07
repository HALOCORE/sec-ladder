#!/usr/bin/env python3
"""Run the UNMODIFIED PAT harness against a php row, through the symlink shim.

    python3 harness-php/gate.py ph00                    # harness/check.py ph00
    python3 harness-php/gate.py --tool measure ph00     # harness/measure.py
    python3 harness-php/gate.py --tool report  ph00     # harness/report.py
    python3 harness-php/gate.py --tool build   ph00     # harness/build.py
    python3 harness-php/gate.py --tool measure --check-stale
    python3 harness-php/gate.py --preflight              # preflight only

⚠⚠ A BRAND-NEW ROW COSTS **SIX** COMMANDS (~28 min), NOT THREE, AND THE ORDER
IS LOAD-BEARING. This docstring said "THE THREE-COMMAND LOOP ... and it is
three and not two" until TASK_PHP_004; the same task's own measurement had
already refuted it (TASK_PHP_003 M4), and `ph00-smoke` needed all six:

    harness-php/gate.py --tool build   <row> --all   # 1. the 28 binaries
    harness-php/gate.py --tool measure <row>         # 2. the matrix
    harness-php/gate.py --tool report  <row>         # 3. the table exists
    harness-php/gate.py                <row>         # 4. FAILS on tables
    harness-php/gate.py --tool report  <row>         # 5. re-render
    harness-php/gate.py                <row>         # 6. green

  * Step 1 is NOT optional: `measure.py` builds nothing, it measures whatever
    binaries happen to be in the build root. TASK_PHP_002's first `measure`
    run reported `static: 1 cells` and wrote a one-cell record silently.
  * Steps 4->6 are the irreducible `gate -> report -> gate` chain.
    `report.py`'s audit section renders from `results/gate/<row>.json`, which
    does not exist until a gate has run; and stage 9c compares the published
    table against a fresh render of THIS run's record. So the first gate on a
    new row MUST fail with `[tables] ... cites no contract_sha256 at all`.
  * `check.py::check_published_tables`'s own "three commands, not two" message
    is about a DIFFERENT case -- a row with no measurement record at all.
    Both are true; six is the figure to plan against.
  (`.tasks-php/PROTOCOL_PHP.md` §E, `RECAP_PHP.md` open item 11.)

============================================================================
WHAT THIS FILE IS, AND WHAT IT IS FORBIDDEN TO BE
============================================================================
It is a PREFLIGHT plus an `exec`. It REIMPLEMENTS NO GATE STAGE and must
never grow one: the whole value of `PLAN_PHP.md` §2.1a is that the php rows
are judged by the SAME code as the 33 PAT rows, so a php-only stage here
would be a second, unvalidated gate wearing the first one's name. If a php
row needs a check the PAT gate does not have, it goes in that row's
`controls/` or in a separate tool, and the report says which.

The preflight is FIVE things, all of which can fail:

  1. `harness-php/root.py` -- the shim exists and every link points where it
     should, and nothing that is not a link lives in it.
  2. `common-php/digest_bridge.py --verify` -- every `common-php/` file is in
     some digest. ⚠ `check.py`'s `common/` globs are `driver.*`, `*.py` and
     `layout/*.py`, ALL NON-RECURSIVE, so `emalloc_shim.h` is in none of them
     and the bridge is what covers it. Ten committed control sources sat in no
     digest at all on the PAT side for many tasks; this is that check.
  3. ⚠⚠ `shim_link_audit()` -- THE ALLOCATOR SYMLINK. Added at TASK_PHP_004;
     see the block below, because for one task this was "mandatory" in two
     documents and enforced by nothing.
  4. `manifest_audit()` -- `patterns-php/php-5.0.0.manifest` still hashes to
     what `MANIFEST.sha256` says. `provenance.py` consults that manifest to
     decide whether a `c_file` is in the corpus, so a tampered manifest changes
     verdicts, and until TASK_PHP_004 it moved no hash anywhere
     (TASK_PHP_003 M6).
  5. `harness-php/provenance.py` -- the row's `provenance.extract_sha256`
     really is the sha256 of the lines it names, out of the pinned tarball.
     Skipped with `--no-provenance`, which prints a loud line AND is now
     recorded in `results-php/preflight/<row>.json`, because a box without the
     tarball must still be able to re-gate but a record taken that way must
     not be indistinguishable from one taken with the check (TASK_PHP_003 M6:
     the gate record's `invocation` field is `check.py`'s argv, not this
     script's, so the skip left NO trace at all).

============================================================================
⚠⚠⚠ THE `<row>/c/emalloc_shim.h` SYMLINK, AND WHY IT IS CHECKED HERE
============================================================================
`.tasks-php/PROTOCOL_PHP.md` §B2 and `RECAP_PHP.md` open item 10 both call it
MANDATORY. TASK_PHP_003 built a row that links the allocator and omits the
symlink: it BUILDS (`#include "emalloc_shim.h"` resolves through `-I COMMON`,
`harness/build.py::build_c`) and the allocator lands in NEITHER digest.

The failure that enables is concrete and permanent. Fix the shim ->
`digest_bridge.py --regen` -> the row's GATE record goes STALE and a re-gate
refreshes it; but `measure.py::measurement_sources()` names neither
`common/*.py` nor anything under `common-php/`, so the MEASUREMENT record --
the one carrying every `Ir` -- stays FRESH for ever, carrying numbers taken
under an allocator that no longer exists.

The symlink is what closes it: `check.py` globs `<row>/c/*` (:10189, :10314)
and `measure.py::measurement_sources` globs `<row>/c/*` too, `glob` returns
symlinks and `sha256_file` follows them, so the real content lands under
`<row>/c/emalloc_shim.h` in BOTH digests.

⚠ A REGULAR-FILE COPY IS REFUSED, and that is not pedantry: a copy would be
hashed under the same key and look identical in the record, while silently
holding an allocator that no longer matches `common-php/`. Only a symlink
makes "the row's allocator" and "the programme's allocator" the same bytes by
construction. ⚠ NO HARNESS EDIT IS INVOLVED -- verified at TASK_PHP_004:
`harness/*.py` and `common/*.py` contain zero references to `common-php/`,
`patterns-php/` or `emalloc_shim`, so this preflight is the only lever there
is.

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
import datetime
import glob
import hashlib
import json
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

#: The one allocator. `PROTOCOL_PHP.md` §B.
SHIM_HEADER = "emalloc_shim.h"
#: The spelling `PROTOCOL_PHP.md` §B2 prescribes, from `<row>/c/`.
CANONICAL_LINK = os.path.join("..", "..", "..", "common-php", SHIM_HEADER)


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def shim_link_audit(patterns_dir=None, common_dir=None):
    """`PROTOCOL_PHP.md` §B2's 'mandatory' symlink, as a check.

    Returns `(problems, notes)`. A row whose `c/` sources mention
    `emalloc_shim.h` MUST carry `<row>/c/emalloc_shim.h` as a SYMLINK resolving
    to `common-php/emalloc_shim.h`; anything else is a problem. A row that
    carries the link without using it gets a note, not a problem -- it is odd
    but it pins the right bytes.

    ⚠ Parameterised on purpose so a negative test can point it at a fixture
    tree under `.temp/` instead of at `patterns-php/`
    (`.temp/php4/b1_symlink_test.py`). A guard nobody has constructed a failing
    case for is a guard nobody has tested.
    """
    patterns_dir = patterns_dir or os.path.join(REPO, "patterns-php")
    common_dir = common_dir or os.path.join(REPO, "common-php")
    real_shim = os.path.join(common_dir, SHIM_HEADER)
    problems, notes = [], []
    if not os.path.isdir(patterns_dir):
        return problems, notes
    if not os.path.exists(real_shim):
        problems.append(f"allocator: {os.path.relpath(real_shim, REPO)} does "
                        f"not exist -- every row's symlink dangles")
        return problems, notes
    want = os.path.realpath(real_shim)

    for pdir in sorted(glob.glob(os.path.join(patterns_dir, "*"))):
        if not os.path.isdir(pdir):
            continue
        cdir = os.path.join(pdir, "c")
        if not os.path.isdir(cdir):
            continue
        row = os.path.basename(pdir)
        link = os.path.join(cdir, SHIM_HEADER)
        users = []
        for src in sorted(glob.glob(os.path.join(cdir, "*"))):
            if os.path.basename(src) == SHIM_HEADER or not os.path.isfile(src):
                continue
            try:
                with open(src, "rb") as fh:
                    if SHIM_HEADER.encode() in fh.read():
                        users.append(os.path.basename(src))
            except OSError as e:
                problems.append(f"allocator: {row}: cannot read {src}: {e}")
        present = os.path.islink(link) or os.path.exists(link)

        if not users:
            if present:
                notes.append(f"{row}: carries c/{SHIM_HEADER} but no c/ source "
                             f"mentions it -- harmless, but the record pins an "
                             f"allocator the row does not use")
            continue

        who = ", ".join(users)
        if not present:
            problems.append(
                f"allocator: {row}: c/{who} include(s) {SHIM_HEADER} and "
                f"{row}/c/{SHIM_HEADER} IS ABSENT.\n"
                f"       It BUILDS anyway (-I common-php), and that is the "
                f"whole problem: the allocator then sits in NEITHER the gate "
                f"digest nor the MEASUREMENT digest, so a later shim fix "
                f"leaves this row's Ir numbers FRESH for ever under an "
                f"allocator that no longer exists.\n"
                f"       Fix:  ln -s {CANONICAL_LINK} "
                f"patterns-php/{row}/c/{SHIM_HEADER}\n"
                f"       (PROTOCOL_PHP.md §B2; TASK_PHP_003 B1.)")
            continue
        if not os.path.islink(link):
            problems.append(
                f"allocator: {row}: {row}/c/{SHIM_HEADER} is a REGULAR FILE, "
                f"not a symlink. A copy is hashed under the same key and looks "
                f"identical in the record while holding a DIFFERENT allocator. "
                f"Replace it with:  ln -s {CANONICAL_LINK} "
                f"patterns-php/{row}/c/{SHIM_HEADER}")
            continue
        got = os.path.realpath(link)
        if got != want:
            problems.append(
                f"allocator: {row}: {row}/c/{SHIM_HEADER} -> "
                f"{os.readlink(link)!r} resolves to {got}, not "
                f"{want}. Every row links the ONE allocator.")
            continue
        target = os.readlink(link)
        if target != CANONICAL_LINK:
            notes.append(f"{row}: c/{SHIM_HEADER} -> {target!r} resolves "
                         f"correctly but is not the canonical "
                         f"{CANONICAL_LINK!r} (PROTOCOL_PHP.md §B2)")
        notes.append(f"{row}: c/{SHIM_HEADER} OK -- symlink, in BOTH digests, "
                     f"used by {who}")
    return problems, notes


def manifest_audit():
    """`patterns-php/MANIFEST.sha256` vs the manifest it covers.

    `provenance.py` consults the manifest to decide whether a `c_file` is in
    the corpus, so a tampered manifest changes verdicts -- and it is in no
    digest anywhere (TASK_PHP_003 M6). `MANIFEST.sha256` existed and nothing
    ran it. Returns `(problems, info)`.
    """
    pdir = os.path.join(REPO, "patterns-php")
    man = os.path.join(pdir, "php-5.0.0.manifest")
    sums = os.path.join(pdir, "MANIFEST.sha256")
    if not os.path.exists(man) or not os.path.exists(sums):
        return ([], {"manifest": None,
                     "note": "no manifest / MANIFEST.sha256 on this box"})
    got = sha256_file(man)
    want = None
    for line in open(sums, encoding="utf-8"):
        sha, _, path = line.strip().partition("  ")
        if os.path.basename(path) == "php-5.0.0.manifest":
            want = sha
    if want is None:
        return ([f"manifest: MANIFEST.sha256 has no line for "
                 f"php-5.0.0.manifest"], {"manifest": got})
    if got != want:
        return ([f"manifest: php-5.0.0.manifest hashes {got[:12]}, "
                 f"MANIFEST.sha256 says {want[:12]}. Regenerate with "
                 f"`sh patterns-php/manifest.sh` and say so, or restore the "
                 f"manifest -- provenance.py's corpus check reads it."],
                {"manifest": got, "expected": want})
    return ([], {"manifest": got})


def harness_php_hashes():
    """Every `harness-php/*.py`, hashed. TASK_PHP_003 M6: the tool that
    certifies a php run is itself in no digest, so a run certified by a tool
    nobody can pin is not certified. This does not put them in `source_sha256`
    -- that needs a harness edit and a 33-pattern re-gate -- but it does put
    them in the preflight record beside the run they certified."""
    return {os.path.basename(p): sha256_file(p)
            for p in sorted(glob.glob(os.path.join(HERE, "*.py")))}


def preflight(row, do_provenance=True):
    """Returns `(problems, record)`. Empty `problems` means go."""
    problems = []
    record = {"row": row, "provenance_checked": bool(row and do_provenance),
              "provenance_skipped": bool(row and not do_provenance)}
    print("preflight")
    rootmod.build(verbose=False)
    bad = rootmod.check()
    for b in bad:
        problems.append(f"shim: {b}")
    record["shim_ok"] = not bad
    print(f"  {'ok  ' if not bad else 'FAIL'} shim {rootmod.SHIM}")

    r = subprocess.run([sys.executable,
                        os.path.join(REPO, "common-php", "digest_bridge.py"),
                        "--verify"], capture_output=True, text=True)
    if r.returncode != 0:
        problems.append("digest bridge:\n" + r.stdout + r.stderr)
    record["digest_bridge_ok"] = r.returncode == 0
    print(f"  {'ok  ' if r.returncode == 0 else 'FAIL'} common-php/ digest bridge")

    alloc_bad, alloc_notes = shim_link_audit()
    problems.extend(alloc_bad)
    record["allocator_symlink_ok"] = not alloc_bad
    record["allocator_symlink_notes"] = alloc_notes
    print(f"  {'ok  ' if not alloc_bad else 'FAIL'} "
          f"<row>/c/{SHIM_HEADER} symlink (PROTOCOL_PHP.md §B2)")
    for n in alloc_notes:
        print(f"       | {n}")

    man_bad, man_info = manifest_audit()
    problems.extend(man_bad)
    record["manifest"] = man_info
    record["manifest_ok"] = not man_bad
    print(f"  {'ok  ' if not man_bad else 'FAIL'} patterns-php/MANIFEST.sha256")

    if row and do_provenance:
        r = subprocess.run([sys.executable,
                            os.path.join(HERE, "provenance.py"), row],
                           capture_output=True, text=True)
        if r.returncode != 0:
            problems.append("provenance:\n" + r.stdout + r.stderr)
        record["provenance_ok"] = r.returncode == 0
        record["provenance_stdout"] = r.stdout.strip().splitlines()
        print(f"  {'ok  ' if r.returncode == 0 else 'FAIL'} provenance {row}")
        for ln in r.stdout.splitlines():
            if ln.strip():
                print(f"       | {ln}")
    elif row:
        print(f"  !!   provenance SKIPPED for {row} (--no-provenance). This "
              f"run certifies nothing about where the kernel came from.")
    record["harness_php_sha256"] = harness_php_hashes()
    record["problems"] = problems
    return problems, record


#: ⚠ NOT `results-php/gate/`. `measure.py --check-stale` globs
#: `results/gate/p*.json` and `results/p*.json`, and `ph00-smoke.preflight.json`
#: matches `p*.json` -- dropping it beside the gate records would make the
#: staleness check try to read it as one. Its own directory costs nothing.
PREFLIGHT_DIR = os.path.join(REPO, "results-php", "preflight")


def write_preflight_record(record):
    """One JSON per row per run, so a php gate record has SOMETHING beside it
    saying what certified it.

    ⚠ This is the CHEAP half of TASK_PHP_003 M6. It does NOT put
    `harness-php/*.py` into `source_sha256`; that needs `check.py`'s `srcs`
    glob to reach `harness-php/`, i.e. a `harness/` edit, i.e. 33 stale PAT
    gate records and a ~2 h re-gate sweep (`PLAN_PHP.md` §2.1). The manager
    owns that trade; this file records the hashes next to the run instead.

    ⚠ It is also NOT hashed by anything, so it is evidence and not a pin: it
    can prove `--no-provenance` WAS used and cannot prove it was not.
    """
    os.makedirs(PREFLIGHT_DIR, exist_ok=True)
    stem = record.get("row") or "_norow"
    out = os.path.join(PREFLIGHT_DIR, f"{stem}.preflight.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=2, sort_keys=False)
    return out


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

    problems, record = preflight(row, not a.no_provenance)
    record["tool"] = a.tool
    record["gate_argv"] = sys.argv[1:]
    record["tool_argv"] = argv
    record["when"] = datetime.datetime.now().isoformat(timespec="seconds")
    if problems:
        record["verdict"] = "PREFLIGHT FAILED"
        write_preflight_record(record)
        print("\nPREFLIGHT FAILED -- the tool was NOT run:")
        for p in problems:
            print(f"  {p}")
        return 2
    if a.preflight:
        record["verdict"] = "preflight only"
        write_preflight_record(record)
        print("\npreflight OK (nothing else run)")
        return 0

    tool = os.path.join(rootmod.SHIM, "harness", TOOLS[a.tool])
    cmd = [sys.executable, tool] + argv
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    record["verdict"] = "tool RUNNING"
    write_preflight_record(record)
    print(f"\n$ {' '.join(cmd)}\n  (REPO for that process = {rootmod.SHIM})\n")
    sys.stdout.flush()
    rc = subprocess.run(cmd, cwd=rootmod.SHIM, env=env).returncode
    record["verdict"] = "tool exited"
    record["tool_returncode"] = rc
    write_preflight_record(record)
    return rc


if __name__ == "__main__":
    sys.exit(main())
