#!/usr/bin/env python3
"""Build `.temp/php-root/` -- the SYMLINK SHIM the UNMODIFIED PAT gate is run
out of.

    python3 harness-php/root.py            # build/refresh it, print the map
    python3 harness-php/root.py --check    # verify only; exit 1 if wrong
    python3 harness-php/root.py --sweep    # re-derive the link list from the
                                           # harness sources and report gaps

⚠⚠⚠ THE WHOLE POINT: `PLAN_PHP.md` §2.1. `harness/*.py` and `common/*.py` are
hashed into all 33 PAT gate records, and `harness/{build,asm,measure}.py` into
all 33 measurement records. Adding one `.py` to `harness/` costs a 33-pattern
re-gate; editing `build.py` costs a full re-measure. So the PHP programme
never edits either -- it runs the real thing out of a directory of symlinks.

WHY IT WORKS, and it is one sentence: every harness module derives

    REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

and `os.path.abspath` **does not resolve symlinks**. Running
`.temp/php-root/harness/check.py` therefore makes `REPO` the shim, and every
REPO-relative path -- INCLUDING THE FIVE HARD-CODED ONES `PLAN_PHP.md` §2.1a
lists -- follows. Verified: `.tasks-php/TASK_PHP_002_REPORT.md` T2 recomputes
`p01`'s gate `source_sha256` through a shim and gets 35 keys and 35 hashes
identical to the COMMITTED `results/gate/p01-array-sum.json`.

============================================================================
THE LINK MAP, AND TWO OF THESE SEVEN WERE NOT IN THE ORIGINAL SPEC
============================================================================
`TASK_PHP_002` §2 listed five links and said the list was derived from four
modules' constants rather than from a sweep, and asked to be corrected. It
needed two more:

  pilot  -> ../../pilot     ⚠⚠ WITHOUT THIS THE GATE CANNOT START.
        `harness/check.py::check_selftests` calls `fixture.ensure()`, and
        `harness/fixture.py:31` reads `PILOT = REPO/pilot` to compile the six
        `.temp/build/docrepro/` binaries `asm.selftest()` re-derives every
        pinned pilot number from. Through the shim that is
        `.temp/php-root/pilot`; with no link all six builds fail and
        `check.py::check_selftests` calls `rep.fail("fixture", "... step 0 cannot
        run")` and returns -- so stage 0 fails and the gate's verdict is FAIL.
        Not a hash question and not cosmetic. ⚠ MEASURED, not reasoned:
        `.tasks-php/TASK_PHP_002_REPORT.md` §4 shows `fixture.ensure()`
        returning False with all six compiler errors, on a shim with no
        `pilot` link.
        ⚠ It is READ-ONLY on `pilot/`: `fixture.py:30` writes to
        `REPO/.temp/build/docrepro`, which the `.temp` link below sends into
        `.temp/php-scratch/`. So the php side builds its own six binaries and
        never touches the PAT tree. (`pilot/` is frozen evidence --
        `.tasks/PROTOCOL.md`, rules for every agent.)

  .temp  -> ../php-scratch  the manager knew this one was missing and asked
        which way to resolve it. **Decision: the shim gets its own `.temp`
        LINK, pointing at a php-only scratch root.** Three candidates, and the
        reason the middle one loses is the one that decided it:

          A. leave it nesting at `.temp/php-root/.temp/`
             REJECTED -- ⚠ BUT NOT FOR THE REASON THIS DOCSTRING GAVE UNTIL
             TASK_PHP_004. It said *"this script REBUILDS the shim by removing
             and recreating it ... so every rebuild would silently delete every
             build artefact underneath it"*, and TASK_PHP_003 m3 MEASURED that
             to be fiction: `build()` is `makedirs(exist_ok=True)` plus a
             per-link `unlink` only when the target differs, there is no
             `rmtree` anywhere in this file, and a scratch marker planted
             inside the shim SURVIVED a `build()`.
             ✅ Option C is still right, on the reasons that hold:
               - a `.temp` inside a `.temp` is invisible to `ls .temp/` and to
                 any "delete the artefact" sweep (`CLAUDE.md` constraint 1);
               - `check()` REFUSES any entry in the shim that is not a link
                 ("unexpected entries in the shim"), so a nested scratch tree
                 would make the preflight fail on every run -- that check, not
                 a rebuild, is what actually protects the shim;
               - the shim IS a derived artefact and a human deleting it by
                 hand (which is the documented repair) would take the scratch
                 tree with it.
          B. point it at the REAL `.temp/`
             REJECTED, and this is the dangerous one. `build.py:119` keys the
             build directory on `pattern_id(pdir)` = `basename.split("-")[0]`,
             so php `ph00` and PAT `p01` do not collide TODAY. A collision
             would be silent and would swap a binary underneath a
             measurement; the cost of avoiding it is one directory.
          C. `.temp/php-root/.temp -> ../php-scratch`   ✅ CHOSEN.
             php scratch is visible at `ls .temp/`, survives a shim rebuild,
             and cannot collide with PAT scratch.

        Six REPO-relative scratch paths land there, all four modules
        confirmed: `.temp/build` (`build.py:50`, `check.py::_san_build`,
        `fixture.py:30`, `asm.py:822`), `.temp/check`
        (`check.py::check_marginal_ir`, `::_dep_info_files`,
        `::_probe_selftest` and the Miri stage),
        `.temp/clausemut` (`check.py::_mutant_path`),
        `.temp/gate-partial` (`check.py::main`), `.temp/cg`
        (`measure.py:449`) and `.temp/dloop-selftest` (`dloop.py:744`).

============================================================================
WHAT IS DELIBERATELY *NOT* LINKED
============================================================================
`.memory/`, `.tasks/`, `RECAP_PAT.md`, `PLAN_PAT.md`, `TOOLCHAIN.md`,
`synthesis/`, `.web/`, `cg/`. Swept: `harness/{build,check,measure,report,
asm,dloop,fixture,vparse}.py` construct **no** path to any of them.
`harness/tools/composition.py:72-73` does read `.memory/06-catalogue.md`, but
`check.py` never imports or executes anything under `harness/tools/` -- it
only globs `tools/*.py` for BASENAMES, at `check.py::harness_module_names`, for the
citation-rot audit. Linking them would be scope the gate does not use.

============================================================================
KNOWN, ACCEPTED, AND MEASURED: `__pycache__`
============================================================================
Importing `check.py` through `.temp/php-root/harness/` writes the bytecode
cache into the REAL `harness/__pycache__/` (the OS resolves the link), and the
`.pyc` records the SHIM path as `co_filename`, so a later PAT traceback would
name `.temp/php-root/harness/check.py`. Measured, not assumed, at
`TASK_PHP_002` -- ⚠ its probe tree `.temp/php0/pycdemo` was deleted with that
task's other scratch artefacts, so the citation is the pasted output in
`.tasks-php/TASK_PHP_002_REPORT.md:290-295` and not the path
(TASK_PHP_009 m4).

It moves no hash (`__pycache__` is gitignored and outside every glob) and it
only happens when a php run is the FIRST to import a freshly-edited harness
module. `harness-php/gate.py` sets `PYTHONDONTWRITEBYTECODE=1` anyway, so the
php path never writes one at all. Cost: one re-parse of a 600 KB source per
run, against a gate that takes tens of minutes.
"""

import argparse
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHIM = os.path.join(REPO, ".temp", "php-root")
SCRATCH = os.path.join(REPO, ".temp", "php-scratch")

#: link name in the shim -> path relative to the shim directory.
#: ⚠ The targets are RELATIVE so the shim keeps working if the checkout moves.
LINKS = [
    ("harness",      "../../harness",     "the REAL, UNMODIFIED PAT harness"),
    ("common",       "../../common-php",  "php shared code + re-exports"),
    ("patterns",     "../../patterns-php", "the php rows"),
    ("results",      "../../results-php", "php gate/measurement records"),
    ("verus_run.py", "../../verus_run.py", "R5's compiler driver, read-only"),
    ("pilot",        "../../pilot",       "fixture.py:31, read-only -- NOT in the original spec"),
    (".temp",        "../php-scratch",    "php-only scratch; see the module docstring"),
]

#: Directories that must exist for the links to resolve to something usable.
#: `report.py:45` does `os.listdir(RESULTS)` BEFORE any `makedirs`, so
#: `results-php/` has to be there before the first render.
REQUIRED_DIRS = [
    os.path.join(REPO, "common-php"),
    os.path.join(REPO, "patterns-php"),
    os.path.join(REPO, "results-php"),
    os.path.join(REPO, "results-php", "gate"),
    os.path.join(REPO, "results-php", "tables"),
    SCRATCH,
]


def build(verbose=True):
    """Create or refresh the shim. Idempotent."""
    for d in REQUIRED_DIRS:
        os.makedirs(d, exist_ok=True)
    os.makedirs(SHIM, exist_ok=True)
    for name, target, _why in LINKS:
        link = os.path.join(SHIM, name)
        if os.path.islink(link):
            if os.readlink(link) == target:
                continue
            os.unlink(link)
        elif os.path.exists(link):
            raise SystemExit(
                f"root.py: {link} exists and is NOT a symlink. Refusing to "
                f"delete it -- a real file here means somebody wrote into the "
                f"shim, and the shim is a derived artefact meant to hold "
                f"nothing but links. Inspect it, then remove it by hand. "
                f"(⚠ This message used to say 'that this script rebuilds'; "
                f"`build()` never deletes anything but a mis-aimed link, "
                f"measured at TASK_PHP_003 m3.)")
        os.symlink(target, link)
    if verbose:
        print(f"shim -> {os.path.relpath(SHIM, REPO)}")
        for name, target, why in LINKS:
            real = os.path.realpath(os.path.join(SHIM, name))
            print(f"  {name:14s} -> {target:20s} = {os.path.relpath(real, REPO)}"
                  f"   ({why})")
    return SHIM


def check():
    """Verify the shim without changing it. Returns a list of problems."""
    bad = []
    if not os.path.isdir(SHIM):
        return [f"{SHIM} does not exist -- run `python3 harness-php/root.py`"]
    for name, target, _why in LINKS:
        link = os.path.join(SHIM, name)
        if not os.path.islink(link):
            bad.append(f"{name}: ABSENT" if not os.path.exists(link)
                       else f"{name}: exists and is NOT a symlink")
            continue
        got = os.readlink(link)
        if got != target:
            bad.append(f"{name}: points at {got!r}, want {target!r}")
        elif not os.path.exists(link):
            bad.append(f"{name}: DANGLING -- {target} does not resolve")
    # Nothing may live in the shim that is not one of the links: a real file
    # here is a write that escaped into a derived artefact.
    extra = sorted(set(os.listdir(SHIM)) - {n for n, _, _ in LINKS})
    if extra:
        bad.append(f"unexpected entries in the shim: {extra}")
    return bad


# --------------------------------------------------------------------------
# The sweep. `TASK_PHP_002` §4 claim 1: "the shim needs only the five links in
# §2, plus a decision about `.temp`" -- derived from four modules' constants,
# not from a sweep. This re-derives the list FROM THE SOURCES so the answer
# ages with the harness instead of with this docstring.

_MODULES = ["build.py", "check.py", "measure.py", "report.py",
            "asm.py", "dloop.py", "fixture.py", "vparse.py", "limbs.py"]

#: Only paths rooted at the REPO itself: those are the ones a shim link has to
#: cover. ⚠ `os.path.join(COMMON, "driver.c")` and `os.path.join(RESULTS,
#: "gate")` are SECOND-level and are already covered by the `common` and
#: `results` links -- an earlier spelling of this sweep matched them too and
#: printed four false gaps (`driver.c`, `gate`, `tables`, `p*.json`).
#:
#: ⚠⚠ THE QUOTE CLASS IS THE FIX FOR TASK_PHP_005 F-10, AND THERE IS A LIVE
#: INSTANCE. These patterns required DOUBLE quotes, so a single-quoted or
#: prefixed literal was invisible: `harness/limbs.py:66` is
#: `sys.path.insert(0, os.path.join(REPO, 'harness'))` -- benign only because
#: `harness` is already linked for other reasons. One `'` in a future harness
#: edit and the sweep went quiet on a genuinely missing link, which is exactly
#: the silent-skip class this project keeps paying for. `harness/` is frozen and
#: cannot be respelled, so the SWEEP learns both spellings instead.
_QUOTED = r"""(?:[rRfFbBuU]{0,2})(['"])([^'"]+)\1"""
_JOIN_REPO = re.compile(r'os\.path\.join\(\s*REPO\s*,\s*' + _QUOTED)
#: The same root, spelled inline off `__file__` instead of via `REPO` --
#: `asm.py:822` and `dloop.py:744` both do this and neither defines `REPO`.
_JOIN_FILE = re.compile(r'os\.path\.abspath\(__file__\)\)\)\s*,\s*\n?\s*' + _QUOTED)
#: ⚠ `os.path.join(REPO, <not a literal>)` -- a component the sweep CANNOT
#: derive, because it is computed at run time. TASK_PHP_005 F-10 counted five,
#: all of them `source_sha256` keys built from a variable and all covered today.
#: They are REPORTED rather than silently skipped: a reader of `--sweep` should
#: be able to see what the sweep could not answer, not just what it could.
#: The third spelling: an f-string that interpolates `REPO` directly rather
#: than calling `os.path.join`. No harness module uses it today; it is here
#: because TASK_PHP_005 F-10's planted `corpus_c` proved the sweep could not see
#: it, and a sweep whose job is to age with the harness must not be blind to a
#: spelling a future edit is free to use.
_FSTRING_REPO = re.compile(r'''f(['"])\{REPO\}/([^'"/{}]+)''')
#: ⚠ `(?=\S)` is load-bearing: without it `\s*` backtracks to zero width, the
#: negative lookahead is evaluated at a SPACE and succeeds, and every literal
#: site is reported as dynamic. Measured while writing this -- 54 false
#: "DYNAMIC" lines on the first spelling.
_JOIN_DYNAMIC = re.compile(
    r'os\.path\.join\(\s*REPO\s*,\s*(?=\S)(?![rRfFbBuU]{0,2}["\'])([^),]+)')


def sweep():
    """Print every first path component the harness builds off its repo root."""
    hits = {}
    dynamic = []
    for m in _MODULES:
        p = os.path.join(REPO, "harness", m)
        if not os.path.exists(p):
            continue
        txt = open(p, encoding="utf-8").read()
        for rx in (_JOIN_REPO, _JOIN_FILE, _FSTRING_REPO):
            for mo in rx.finditer(txt):
                comp = mo.group(2)
                ln = txt.count("\n", 0, mo.start()) + 1
                hits.setdefault(comp, []).append(f"{m}:{ln}")
        for mo in _JOIN_DYNAMIC.finditer(txt):
            ln = txt.count("\n", 0, mo.start()) + 1
            dynamic.append((f"{m}:{ln}", mo.group(1).strip()))
    # Also the module-level constants, which the regex above sees only at
    # their use sites.
    for m in _MODULES:
        p = os.path.join(REPO, "harness", m)
        if not os.path.exists(p):
            continue
        for i, line in enumerate(open(p, encoding="utf-8"), 1):
            mo = re.search(r'=\s*os\.path\.join\(REPO,\s*' + _QUOTED, line)
            if mo:
                hits.setdefault(mo.group(2), []).append(f"{m}:{i}")

    # ⚠⚠ THERE WAS A SECOND ARM HERE AND IT MADE THE SWEEP A TAUTOLOGY FOR
    # FOUR OF THE SEVEN LINKS. It read
    #
    #     elif comp in ("common", "harness", "patterns", "results"):
    #         print("LINKED ...")
    #
    # -- a hard-coded whitelist of four names that are ALSO in `LINKS`, so it
    # was unreachable while the map was intact and, the moment a link was
    # deleted to test the sweep, it silently caught it and printed LINKED.
    # `--sweep` exists to make the link list age with the harness; for the four
    # links that carry the gate it could not fail. TASK_PHP_003 M2 measured it
    # link by link: `harness`, `common`, `patterns`, `results` all returned
    # rc=0 with a deleted entry, and the engineer's own must-fire control had
    # been run on `pilot`, one of the three the whitelist does NOT cover, so
    # the whitelist was never exercised. This is the silent-skip class the
    # project has now found eleven times. Deleted at TASK_PHP_004; the
    # per-link negative is `.temp/php4/m2_sweep_test.py`.
    covered = {n for n, _, _ in LINKS}
    print("first path component off the harness's repo root, from a source sweep")
    print(f"({len(_MODULES)} modules; the link map has {len(LINKS)} entries)\n")
    rc = 0
    for comp in sorted(hits):
        where = ", ".join(sorted(set(hits[comp]))[:6])
        if comp in covered:
            print(f"  LINKED   {comp:16s} {where}")
        else:
            print(f"  ⚠ GAP    {comp:16s} {where}")
            rc = 1
    if dynamic:
        print(f"\n  ⚠ {len(dynamic)} `os.path.join(REPO, <computed>)` site(s) "
              f"this sweep CANNOT derive a component for:")
        for where, expr in sorted(set(dynamic)):
            print(f"    ? DYNAMIC  {expr[:44]:44s} {where}")
        print("    (the component is a run-time value -- typically a "
              "`source_sha256` key. All covered today; listed so the sweep's "
              "residual is visible instead of silent. TASK_PHP_005 F-10.)")
    print()
    if rc:
        print("A GAP means the harness builds a repo-root-relative path the "
              "shim does not cover. Decide it deliberately: add a link, or "
              "record here why nesting under the shim is correct.")
    else:
        print("no gaps: every repo-root-relative component the sweep finds is "
              "covered by the link map.")
    return rc


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="verify only")
    ap.add_argument("--sweep", action="store_true",
                    help="re-derive the link list from the harness sources")
    a = ap.parse_args()
    if a.sweep:
        return sweep()
    if a.check:
        bad = check()
        for b in bad:
            print(f"  BAD  {b}")
        print("shim OK" if not bad else f"{len(bad)} problem(s)")
        return 1 if bad else 0
    build()
    bad = check()
    for b in bad:
        print(f"  BAD  {b}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
