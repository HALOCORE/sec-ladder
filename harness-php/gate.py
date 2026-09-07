#!/usr/bin/env python3
"""Run the UNMODIFIED PAT harness against a php row, through the symlink shim.

    python3 harness-php/gate.py ph00                    # harness/check.py ph00
    python3 harness-php/gate.py --tool measure ph00     # harness/measure.py
    python3 harness-php/gate.py --tool report  ph00     # harness/report.py
    python3 harness-php/gate.py --tool build   ph00     # harness/build.py
    python3 harness-php/gate.py --tool measure --check-stale
    python3 harness-php/gate.py --preflight              # preflight only
    python3 harness-php/gate.py --audit                  # which php records
                                                         # have no preflight
                                                         # record; exit 1 if any
    python3 harness-php/provenance.py --selftest         # the overlap cases

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

The preflight is SEVEN things. ⚠ SIX of them can FAIL the run; the seventh is
a loud NOTE and says so. ⚠⚠ THIS LINE SAID "FIVE THINGS, ALL OF WHICH CAN
FAIL" AND THE "ALL" WAS FALSE OF STAGE 1 (TASK_PHP_005 F-6): stage 1 ran
`root.py`'s `build()` BEFORE its `check()`, so a mis-aimed shim link -- one
planted at the FROZEN PAT `results/` tree -- was silently repaired and recorded
`shim_ok: true`. Fixed at TASK_PHP_006: check, then repair, then check, and a
repair is printed and recorded in `shim_repaired`.

  1. `harness-php/root.py` -- the shim exists and every link points where it
     should, and nothing that is not a link lives in it.
  2. `common-php/digest_bridge.py --verify` -- every `common-php/` file is in
     some digest. ⚠ `check.py`'s `common/` globs are `driver.*`, `*.py` and
     `layout/*.py`, ALL NON-RECURSIVE, so `emalloc_shim.h` is in none of them
     and the bridge is what covers it. Ten committed control sources sat in no
     digest at all on the PAT side for many tasks; this is that check.
  3. ⚠⚠ `c_subdir_audit()` -- NO `patterns-php/<row>/c/<subdir>/`. Added at
     TASK_PHP_006. `check.py` and `measure.py` glob `<row>/c/*` NON-RECURSIVELY,
     so a source in a `c/` subdirectory is COMPILED and in NO digest at all.
     Fixing that is a `harness/` edit; the php side forbids the layout instead
     (`RECAP_PHP.md` open item 17). ⚠ The refusal message prices three ways out,
     one of them measured -- read it before working around it.
  4. ⚠⚠ `shim_link_audit()` -- THE ALLOCATOR SYMLINK. Added at TASK_PHP_004;
     see the block below, because for one task this was "mandatory" in two
     documents and enforced by nothing. ⚠ Its detector was a STRING SEARCH and
     TASK_PHP_005 F-1 got past it twice; since TASK_PHP_006 it is the
     PREPROCESSOR (`_tu_closure`).
  5. `overlap_selftest()` -- `provenance.py`'s kernel-overlap normaliser still
     refuses the dead-code cases TASK_PHP_005 F-4 built. Runs here because a
     self-test nobody runs is the silent-skip class this project keeps finding.
  6. `manifest_audit()` -- `patterns-php/php-5.0.0.manifest` still hashes to
     what `MANIFEST.sha256` says. `provenance.py` consults that manifest to
     decide whether a `c_file` is in the corpus, so a tampered manifest changes
     verdicts, and until TASK_PHP_004 it moved no hash anywhere
     (TASK_PHP_003 M6).
  7. `harness-php/provenance.py` -- the row's `provenance.extract_sha256`
     really is the sha256 of the lines it names, out of the pinned tarball.
     Skipped with `--no-provenance`, which prints a loud line AND is recorded
     in `results-php/preflight/<row>.preflight.json`, because a box without the
     tarball must still be able to re-gate but a record taken that way must
     not be indistinguishable from one taken with the check (TASK_PHP_003 M6:
     the gate record's `invocation` field is `check.py`'s argv, not this
     script's, so the skip left NO trace at all).

  + `preflight_coverage_audit()` -- a NOTE, never a failure: which php records
    have no preflight record beside them. ⚠ It is a DETECTOR, not a pin, and it
    cannot be made into one from here -- see its docstring, and TASK_PHP_006
    §1.3. `gate.py --audit` is the same check with an exit code.

⚠⚠ WHAT THIS SCRIPT DOES **NOT** ENFORCE, STATED HERE BECAUSE A HALF-TRUE
CLAIM IS WORSE THAN NONE: **it cannot make itself mandatory.**
`grep -c preflight harness/{check,measure,report}.py` is `0 0 0`, and
`PLAN_PHP.md` §2.1a documents running `check.py` straight out of the shim.
Nothing in a gate record says whether this wrapper ran -- the `invocation`
field is `check.py`'s own argv and is byte-identical either way. Closing that
needs a `harness/` edit and a 33-pattern re-gate. `PROTOCOL_PHP.md` §E says
"never run `harness/check.py` directly on a php row" and that sentence is a
convention, not a mechanism.

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
import re
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
#: ⚠⚠ AND ITS SECOND SPELLING. `emalloc_shim.c` is two lines --
#: `#define PHP_SHIM_IMPL` / `#include "emalloc_shim.h"` -- and it sits on
#: `-I common-php`, so `#include "emalloc_shim.c"` from `c/kernel.c` pulls the
#: WHOLE allocator in while no `c/` file contains the string `emalloc_shim.h`.
#: TASK_PHP_005 F-1 built that row: it compiles, links and allocates
#: (`alloc tally = 7688571`) with the allocator in NEITHER digest and the
#: preflight green. ⚠ `emalloc_shim.c`'s own header comment said it *"IS NOT ON
#: THE PATTERN BUILD PATH AND CANNOT BE"*, which is true of `build.py`'s TU list
#: and FALSE of the preprocessor -- corrected there at TASK_PHP_006.
SHIM_IMPL_TU = "emalloc_shim.c"
ALLOC_FILES = (SHIM_HEADER, SHIM_IMPL_TU)
#: The spelling `PROTOCOL_PHP.md` §B2 prescribes, from `<row>/c/`.
CANONICAL_LINK = os.path.join("..", "..", "..", "common-php", SHIM_HEADER)

#: The FALLBACK detector, used only when the preprocessor cannot answer.
#: ⚠ IT HAS A SPELLING and that is stated out loud wherever it fires:
#: it requires the name inside an `#include` ON THE SAME LINE, which is what
#: closes TASK_PHP_005 F-8 (a row whose only mention is the comment
#: `PLAN_PHP.md` §4.3 tells a NON-allocating row to write), and it still cannot
#: see a computed include, a macro-built path or a name reached through a
#: `-include` flag. The preprocessor closure below has no spelling; this does.
_INCLUDE_RX = re.compile(
    rb'^[ \t]*#[ \t]*include[ \t]*[<"][^">]*emalloc_shim\.[hc][">]', re.M)

#: `harness/build.py::c_flags` -- the two preprocessor states every measured C
#: cell is built in. `-O0`/`-O3` do not change the include closure; `-flto` does
#: not either; `-DSLB_ISOLATED` CAN, so both states are swept and unioned.
#: A row that hides `#include "emalloc_shim.h"` behind `#ifdef SLB_ISOLATED`
#: is a shim user in half its cells and this is what sees it.
_MM_CONFIGS = ([], ["-DSLB_ISOLATED"])


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def _tu_closure(cdir, common_dir):
    """The row's REAL translation-unit closure, from the preprocessor.

    Returns `(by_tu, errors)` where `by_tu` maps a TU's basename to the set of
    `realpath`s its `#include` graph reaches, under both `_MM_CONFIGS`.

    ⚠⚠ THIS IS THE DETECTOR, AND THE POINT IS THAT IT HAS NO SPELLING.
    TASK_PHP_005 F-1 got round the previous textual one twice -- once with
    `#include "emalloc_shim.c"` (the audit knew only the `.h`) and once with
    `c/sub/row_alloc.h` (`glob(cdir + "/*")` is not recursive) -- and
    TASK_PHP_005 F-8 showed the same detector FALSE-POSITIVING on a row whose
    only mention of the name is the comment `PLAN_PHP.md` §4.3 tells a
    non-allocating row to write. `gcc -MM` closes all three at once: it answers
    the question the digests care about, which is *"does the allocator's source
    reach a compiled TU"*, and it answers it the way `harness/build.py` would.

    ⚠ MEASURED PRICE (TASK_PHP_006, `.temp/php6/03-mm-price-batched.log`):
    **2 `gcc -MM` calls and ~115 ms per row**, batched over every TU, against a
    gate that takes ~24 minutes. Nine rows cost 1.03 s.

    ⚠ TUs are `build.py::build_c`'s: `common/driver.c` plus every `.c` in the
    row's `c/`. `driver.c` is included even though it is frozen PAT code,
    because `build_c` compiles it with `-I <row>/c` and a row could therefore
    shadow a driver header with one of its own.

    ⚠ IT CAN FAIL, AND FAILING IS NOT AN ANSWER. A row mid-construction whose
    `#include` does not resolve makes `gcc -MM` exit non-zero; the caller falls
    back to `_INCLUDE_RX` and SAYS SO. Do not read a failure as "no allocator".
    """
    by_tu, errors = {}, []
    tus = sorted(glob.glob(os.path.join(cdir, "*.c")))
    drv = os.path.join(common_dir, "driver.c")
    if os.path.exists(drv):
        tus.append(drv)
    if not tus:
        return by_tu, errors
    for defs in _MM_CONFIGS:
        cmd = (["gcc", "-std=c99", "-MM"] + defs
               + ["-I", common_dir, "-I", cdir] + tus)
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO)
        except OSError as e:
            errors.append(f"cannot run gcc -MM: {e}")
            return by_tu, errors
        if r.returncode != 0:
            errors.append(f"gcc -MM {' '.join(defs) or '(no -D)'} exited "
                          f"{r.returncode}: "
                          f"{(r.stderr.strip().splitlines() or ['?'])[0]}")
            continue
        for rule in r.stdout.replace("\\\n", " ").splitlines():
            if ":" not in rule:
                continue
            deps = [os.path.realpath(os.path.join(REPO, t))
                    for t in rule.split(":", 1)[1].split()]
            if not deps:
                continue
            # `gcc -MM a.o: a.c hdr.h` -- the first dependency is the TU.
            by_tu.setdefault(os.path.basename(deps[0]), set()).update(deps)
    return by_tu, errors


def _text_mentions(path):
    """Fallback detector: the allocator's name inside an `#include`."""
    try:
        with open(path, "rb") as fh:
            return bool(_INCLUDE_RX.search(fh.read()))
    except OSError:
        return False


def c_subdir_audit(patterns_dir=None):
    """⚠⚠ REFUSE any `patterns-php/<row>/c/<subdir>/`. Returns `(problems, [])`.

    ============================================================================
    WHY A LEGITIMATE DIRECTORY LAYOUT IS FORBIDDEN HERE
    ============================================================================
    `harness/check.py:10314` and `harness/measure.py:226` build a row's digest
    from `glob(<row>/c/*)` and then drop the directory entry with
    `os.path.isfile(s)`. Both globs are NON-RECURSIVE. So a file at
    `<row>/c/zend/foo.h` is:

      * in NO gate digest and in NO measurement digest -- the record shows no
        trace of it either way, so nothing goes STALE when it changes;
      * invisible to `check.py`'s `--no-build` staleness scan
        (`check.py:10187-10189`, the same glob), so editing it does not even
        mark the compiled binaries out of date;
      * still fully COMPILED, because `build_c` passes `-I <row>/c` and the
        preprocessor is recursive even though the glob is not.

    That is TASK_PHP_005 F-1's second mechanism, and it is bigger than the
    allocator: ANY source in a `c/` subdirectory is unpinned.

    ⚠ THIS IS A DELIBERATE TRADE, NOT AN OVERSIGHT, AND THE REFUSAL IS THE
    CHEAPER HALF OF IT. Fixing the glob is a `harness/` edit; `harness/*.py` is
    hashed into all 33 PAT gate records and `harness/measure.py` into all 33
    measurement records, so the repair costs a 33-pattern re-gate for zero
    present benefit -- `find patterns patterns-php -mindepth 3 -maxdepth 3
    -type d -path '*/c/*'` is empty. The manager decided against it:
    `RECAP_PHP.md` open item 17.

    ⚠⚠ IF YOU ARE READING THIS BECAUSE THE PREFLIGHT REFUSED YOUR ROW, THE
    TRADE MAY NOW BE WRONG AND THE PROJECT WANTS TO KNOW. php rows are
    EXTRACTED C and `c/zend/` is an ordinary thing to want. Three ways out, in
    order of cost:

      1. FLATTEN. Name the file for its origin -- `c/zend__zend_hash.h` for
         `Zend/zend_hash.h` -- and rewrite the `#include` to match. Costs one
         line in the deletion ledger (`PROTOCOL_PHP.md` §A2) and nothing else.
         This is the expected answer and no row has yet needed more.
      2. FLAT SYMLINK. Keep `c/zend/foo.h` and add `c/zend__foo.h -> zend/foo.h`
         beside it. ✅ MEASURED at TASK_PHP_006 (`.temp/php6/b1_rerun.py` §C,
         log `05-b1-rerun.log`): `glob` returns the flat symlink,
         `os.path.isfile` and `sha256_file` follow it, so the real bytes DO land
         in both digests under the flat key `c/zend__zend_hash.h` while the
         subdirectory file itself stays keyed nowhere.
         ⚠ It is NOT enabled here, and deliberately: nothing would force
         the NEXT file added to that subdirectory to get a link, so the
         guarantee would hold only for as long as somebody remembered it.
         If a row needs this, ask for it and it comes with a check.
      3. PAY THE RE-GATE. Fix the two globs in `harness/`, re-gate 33 PAT rows.
         Open item 17 is carried, not closed, precisely so this stays available.
    """
    patterns_dir = patterns_dir or os.path.join(REPO, "patterns-php")
    problems = []
    if not os.path.isdir(patterns_dir):
        return problems, []
    for pdir in sorted(glob.glob(os.path.join(patterns_dir, "*"))):
        cdir = os.path.join(pdir, "c")
        if not os.path.isdir(cdir):
            continue
        row = os.path.basename(pdir)
        for entry in sorted(os.listdir(cdir)):
            p = os.path.join(cdir, entry)
            if not os.path.isdir(p) or os.path.islink(p):
                continue
            inside = sorted(os.path.relpath(os.path.join(r, f), cdir)
                            for r, _d, fs in os.walk(p) for f in fs)
            problems.append(
                f"allocator/digest: {row}: c/{entry}/ IS A DIRECTORY, and no "
                f"file under it is in ANY digest.\n"
                f"       {len(inside)} file(s): {inside[:6]}"
                f"{'...' if len(inside) > 6 else ''}\n"
                f"       check.py:10314 and measure.py:226 glob `<row>/c/*` "
                f"NON-RECURSIVELY and drop the directory with isfile(), so "
                f"these files are compiled (build_c passes -I <row>/c) and "
                f"pinned by nothing: no gate digest, no measurement digest, "
                f"and not even check.py's --no-build staleness scan. Editing "
                f"one would not mark a single binary stale.\n"
                f"       ⚠ Fixing the glob is a harness/ edit = a 33-pattern "
                f"re-gate; the manager decided against it (RECAP_PHP.md open "
                f"item 17), so the php side forbids the layout instead.\n"
                f"       Fix: FLATTEN -- move it to c/{entry}__<name> and "
                f"rewrite the #include (one deletion-ledger line, "
                f"PROTOCOL_PHP.md §A2).\n"
                f"       ⚠⚠ IF FLATTENING IS WRONG FOR YOUR ROW, SAY SO -- "
                f"TASK_PHP_006 §5 call 1 asks to be told, with the row that "
                f"needs it. Two sanctioned alternatives are priced in "
                f"`c_subdir_audit`'s docstring, one of them measured.")
    return problems, []


def shim_link_audit(patterns_dir=None, common_dir=None):
    """`PROTOCOL_PHP.md` §B2's 'mandatory' symlink, as a check.

    Returns `(problems, notes)`. A row whose TUs REACH `emalloc_shim.h` (or
    `emalloc_shim.c`) MUST carry `<row>/c/emalloc_shim.h` as a SYMLINK resolving
    to `common-php/emalloc_shim.h`; anything else is a problem. A row that
    carries the link without using it gets a note, not a problem -- it is odd
    but it pins the right bytes.

    ⚠⚠ "REACH" IS DECIDED BY THE PREPROCESSOR, NOT BY A STRING SEARCH, SINCE
    TASK_PHP_006. The previous detector searched each `c/*` file for the literal
    `emalloc_shim.h`; TASK_PHP_005 F-1 got past it twice and F-8 made it fire on
    a comment. See `_tu_closure`. The text detector survives as a FALLBACK for
    the one case the preprocessor cannot answer -- a row that does not
    preprocess -- and every use of it says so in the notes.

    ⚠ Parameterised on purpose so a negative test can point it at a fixture
    tree under `.temp/` instead of at `patterns-php/`
    (`.temp/php4/b1_symlink_test.py`, `.temp/php5/b1_bypass.py`,
    `.temp/php6/b1_rerun.py`). A guard nobody has constructed a failing case for
    is a guard nobody has tested.
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
    alloc_real = {os.path.realpath(os.path.join(common_dir, f))
                  for f in ALLOC_FILES
                  if os.path.exists(os.path.join(common_dir, f))}

    for pdir in sorted(glob.glob(os.path.join(patterns_dir, "*"))):
        if not os.path.isdir(pdir):
            continue
        cdir = os.path.join(pdir, "c")
        if not os.path.isdir(cdir):
            continue
        row = os.path.basename(pdir)
        link = os.path.join(cdir, SHIM_HEADER)

        by_tu, mm_errors = _tu_closure(cdir, common_dir)
        # Every `c/` source, RECURSIVELY -- the text detector must not repeat
        # the non-recursive mistake even though `c_subdir_audit` forbids the
        # layout that exploits it.
        texty = sorted(
            os.path.relpath(os.path.join(r, f), cdir)
            for r, _d, fs in os.walk(cdir) for f in fs
            if f != SHIM_HEADER and _text_mentions(os.path.join(r, f)))

        if mm_errors:
            for e in mm_errors:
                notes.append(f"{row}: ⚠ PREPROCESSOR COULD NOT DECIDE -- {e}. "
                             f"Falling back to the TEXT detector, which only "
                             f"sees the name inside an #include and can miss a "
                             f"computed or conditional one. Make the row "
                             f"preprocess and re-run.")
            users = texty
            how = "text fallback"
        else:
            users = sorted(tu for tu, deps in by_tu.items()
                           if deps & alloc_real)
            how = "preprocessor"
            # Text says yes, the preprocessor says no: dead or conditional
            # code. Not a refusal -- the preprocessor is the authority -- but
            # worth saying, because it is the shape F-4 found on the overlap
            # floor.
            only_text = [t for t in texty
                         if not (by_tu.get(os.path.basename(t), set())
                                 & alloc_real)]
            reached = bool(users)
            for t in only_text:
                if not reached:
                    notes.append(
                        f"{row}: c/{t} #include(s) an emalloc_shim file but no "
                        f"translation unit REACHES it under -DSLB_ISOLATED or "
                        f"without it -- dead code, or a header nothing "
                        f"includes. Not treated as a shim user.")

        present = os.path.islink(link) or os.path.exists(link)

        if not users:
            if present:
                notes.append(f"{row}: carries c/{SHIM_HEADER} but no "
                             f"translation unit reaches it ({how}) -- "
                             f"harmless, but the record pins an "
                             f"allocator the row does not use")
            continue

        who = ", ".join(users)
        if not present:
            problems.append(
                f"allocator: {row}: the TU(s) {who} REACH an emalloc_shim "
                f"source ({how}) and {row}/c/{SHIM_HEADER} IS ABSENT.\n"
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
                     f"reached by {who} ({how})")
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


#: `check.py:1872-1873`'s own markers for the shared paragraph every `idiom.why`
#: must carry byte-identically. Duplicated here rather than imported because
#: importing `check.py` from the real `harness/` would run its module body.
_NS_BEGIN, _NS_END = "NAMED-SPELLING STANDARD", "p01 and p08 neither"
_FENCE_RX = re.compile(r"```slb-contract\s*\n(.*?)```", re.S)


def why_sizes(patterns_dir=None):
    """⚠ REPORTED, NEVER ENFORCED. The row-specific size of each `idiom.why`.

    ============================================================================
    THERE IS NO SIZE RULE ON `why`, AND THAT IS A MEASURED CONCLUSION
    ============================================================================
    `RECAP_PHP.md` open item 19: the manager wrote this rule twice and both
    versions failed, and asked TASK_PHP_006 to measure the distribution and
    propose (a) a limit the corpus supports, (b) a structural rule, or (c) no
    rule -- with the check that enforces it, or explicitly unenforced.
    Measured over all 33 built PAT rows plus `ph00-smoke`
    (`.temp/php6/15-f5-why-sizes.log`, `16-f5-structure.log`, `17-f5-tail.log`):

      (a) A WORD LIMIT. Over the 33 built PAT rows: min 197, median 989,
          p90 1817, MAX 3140, quartiles 527 / 989 / 1544. Any limit at or
          below the upper quartile (1544) refuses a quarter of the built corpus;
          any limit the corpus meets permits ~3x the median and would not have
          prevented the thing the rule exists for. And enforcing one on PAT
          means editing text INSIDE the hashed block on 33 rows -- 33
          `contract_sha256` moves and 33 re-gates. REJECTED.
      (b) A STRUCTURAL RULE. ⚠ *"the first paragraph is a self-contained
          summary"* is unsatisfiable as stated: **0 of 34 `why` strings contain
          a single newline**, so none of them HAS a second paragraph, and giving
          them one is the same 33 re-gates. The first-SENTENCE variant is
          satisfiable (median 26 words, max 80, 0 rows over 80) and is
          **vacuous**: only 14 distinct openers across 34 rows, and 22 rows open
          with one of exactly two boilerplate sentences (*"each deletes
          something this pattern IS…"* x11, *"POLICY ADOPTED AFTER MEASURING…"*
          x11). A check that 22 rows pass by sharing a sentence that says
          nothing about any of them measures nothing. REJECTED.
      (c) NO RULE, and this is the recommendation. `RECAP_PHP.md` already has
          none and says so; that is a stable state. What replaces it is THIS --
          the number, printed on every preflight and written into the committed
          preflight record, in front of whoever is about to write the next one.

    ⚠ IT IS NOT A BAR. It cannot fail a run and must not grow the ability to.
    An unenforced size rule is what produced both previous failures; a reported
    size is not a rule at all, which is the point.

    ⚠⚠ AND THE PREFIX IS NOT THE ROW-SPECIFIC HALF. `TASK_PHP_005` F-5 and
    `RECAP_PHP.md` open item 19 measured `why[:why.find(BEGIN)]` and reported
    `p49-interned-pool` at 2533 as the corpus maximum. **Two rows carry prose
    AFTER the shared block** -- `check.py:1866` says so in passing -- and
    `p16-tlv-walk`'s tail is **3031 words**, so p16's true row-specific half is
    **3140, the LARGEST in the corpus**, while the F-5 table lists it as the
    smallest at 109. This function counts prefix + tail.
    """
    # ⚠ `str.split()`, i.e. `wc -w`, DELIBERATELY -- the same cut the 200 and
    # the 201 in `RECAP_PHP.md` were taken with. `RECAP_PHP.md`'s size box warns
    # that this quantity already HAS three answers and that arbitrating it again
    # is the wrong move; an alnum-token count would be a fourth and would report
    # `ph00-smoke` as 197. `prefix_words` and `tail_words` are reported
    # SEPARATELY instead, because for 32 of the 34 rows the "tail" is the single
    # `.` that closes the sentence -- the whole of the 11003-vs-11004
    # discrepancy TASK_PHP_005 §4 settled -- and `wc -w` counts it as a word.
    # The two rows where the tail is real prose are `p16-tlv-walk` (3031 words)
    # and `p17-http-range` (346).
    def words(s):
        return len(s.split())

    patterns_dir = patterns_dir or os.path.join(REPO, "patterns-php")
    out = {}
    for spec in sorted(glob.glob(os.path.join(patterns_dir, "*", "spec.md"))):
        row = os.path.basename(os.path.dirname(spec))
        try:
            m = _FENCE_RX.search(open(spec, encoding="utf-8").read())
            why = (json.loads(m.group(1)).get("idiom") or {}).get("why")
        except (AttributeError, ValueError, OSError):
            continue
        if not isinstance(why, str):
            continue
        i, j = why.find(_NS_BEGIN), why.find(_NS_END)
        if i < 0 or j < 0:
            out[row] = {"row_specific_words": words(why),
                        "shared_block": False}
            continue
        head, tail = why[:i], why[j + len(_NS_END):]
        out[row] = {"row_specific_words": words(head) + words(tail),
                    "prefix_words": words(head),
                    "tail_words": words(tail),
                    "shared_block": True}
    return out


def overlap_selftest():
    """Run `provenance.py`'s dead-code regression cases. Returns `(problems, note)`.

    ⚠ IT IS RUN HERE BECAUSE A SELF-TEST NOBODY RUNS IS THE SILENT-SKIP CLASS
    THIS PROJECT HAS NOW FOUND ELEVEN TIMES. TASK_PHP_005 F-4 built the case it
    protects: a kernel that implements DIVISION, cites MULTIPLICATION, and hides
    the citation behind `#if 0` scored 100 % and was ACCEPTED, because
    `_normalise` dropped lines starting with `#` and so deleted the `#if 0` and
    the `#endif` while keeping everything between them. Cost measured at
    TASK_PHP_006: pure string work, no compiler, ~1 ms.
    """
    try:
        sys.path.insert(0, HERE)
        import provenance as provmod
        bad = provmod.selftest_overlap()
    except Exception as e:  # noqa: BLE001 -- a broken self-test is a problem
        return ([f"overlap self-test: could not run: {e!r}"], "ERROR")
    if bad:
        return ([f"overlap self-test: {b}" for b in bad],
                f"{len(bad)} FAILED")
    return ([], f"{len(provmod.OVERLAP_CASES)} cases")


def preflight_coverage_audit():
    """⚠ Which php records were produced by a run NOTHING certified?

    Returns `(problems, notes)`.

    TASK_PHP_005 §1's second half: `grep -c preflight harness/{check,measure,
    report}.py` is `0 0 0`, the gate record's 37 top-level keys carry no
    preflight field, and its `invocation` is byte-identical whether the run went
    through `gate.py` or was launched straight out of the shim -- which
    `PLAN_PHP.md` §2.1a documents as a supported spelling. ⚠⚠ **THAT CANNOT BE
    CLOSED FROM HERE.** Making `check.py` record the wrapper is a `harness/`
    edit, i.e. a 33-pattern re-gate, and TASK_PHP_006 §1.3 says not to try.

    **So this is the cheapest honest substitute, and it is a DETECTOR rather
    than a PIN:** every `results-php/gate/<row>.json` and
    `results-php/<row>.json` must have a `results-php/preflight/<row>.preflight.json`
    beside it. It cannot prove a preflight ran; it can prove one did NOT, for
    every record whose row never had one -- which is exactly the fresh-clone
    and run-it-directly cases. It is worth having only because the record is
    COMMITTED as of TASK_PHP_006 (`RECAP_PHP.md` open item 18); while it was
    gitignored, a clean checkout made every row look uncertified.

    ⚠ A NOTE, NOT A PROBLEM, AND THE REASON IS A DEADLOCK. If a missing record
    failed the preflight, the repair (`gate.py --preflight <row>`) would itself
    be a preflight and would fail on every OTHER uncovered row before writing
    anything. Loud beats unrunnable. `gate.py --audit` exits non-zero on the
    same condition, for anyone who wants it as a gate.
    """
    notes, uncovered = [], []
    rdir = os.path.join(REPO, "results-php")
    if not os.path.isdir(rdir):
        return [], notes
    recs = (sorted(glob.glob(os.path.join(rdir, "*.json")))
            + sorted(glob.glob(os.path.join(rdir, "gate", "*.json"))))
    for rec in recs:
        if rec.endswith(".partial.json"):
            continue
        stem = os.path.basename(rec)[:-len(".json")]
        rid = stem.split("-")[0]
        hits = glob.glob(os.path.join(PREFLIGHT_DIR, f"{rid}*.preflight.json"))
        if not hits:
            uncovered.append(os.path.relpath(rec, REPO))
    if uncovered:
        notes.append(
            f"⚠ {len(uncovered)} php record(s) have NO preflight record: "
            f"{uncovered}. Either the run did not go through gate.py "
            f"(PLAN_PHP.md §2.1a documents that spelling and nothing "
            f"downstream records it -- TASK_PHP_005 §1), or the record was "
            f"deleted. Re-run `python3 harness-php/gate.py --preflight <row>` "
            f"to certify the CURRENT tree, and say in the report that the "
            f"original run was not certified.")
    return [], notes


def preflight(row, do_provenance=True):
    """Returns `(problems, record)`. Empty `problems` means go."""
    problems = []
    record = {"row": row, "provenance_checked": bool(row and do_provenance),
              "provenance_skipped": bool(row and not do_provenance)}
    print("preflight")
    # ⚠⚠ `check()` BEFORE `build()`, AND THE ORDER IS THE WHOLE CHECK.
    # TASK_PHP_005 F-6: this ran `build()` first, so stage 1 verified the state
    # it had just created. A shim link aimed at the FROZEN PAT `results/` tree
    # was silently repaired and recorded `shim_ok: true`; `root.py --check`
    # caught it and the preflight could not, which made this stage strictly
    # weaker than the tool it wraps. Now: look, record what was found, then
    # repair, then look again. A repair is a NOTE, not a failure -- it errs
    # safe and the target is derived -- but it is no longer invisible.
    pre_bad = (rootmod.check() if os.path.isdir(rootmod.SHIM)
               else [f"{rootmod.SHIM} did not exist -- built from scratch by "
                     f"this run, which is normal on a fresh checkout"])
    rootmod.build(verbose=False)
    bad = rootmod.check()
    for b in bad:
        problems.append(f"shim: {b}")
    record["shim_ok"] = not bad
    record["shim_repaired"] = [b for b in pre_bad if b not in bad]
    print(f"  {'ok  ' if not bad else 'FAIL'} shim {rootmod.SHIM}")
    for b in record["shim_repaired"]:
        print(f"       | ⚠ REPAIRED BY THIS PREFLIGHT (was: {b}) -- "
              f"`shim_ok` below is a statement about the state AFTER the "
              f"repair (TASK_PHP_005 F-6)")

    r = subprocess.run([sys.executable,
                        os.path.join(REPO, "common-php", "digest_bridge.py"),
                        "--verify"], capture_output=True, text=True)
    if r.returncode != 0:
        problems.append("digest bridge:\n" + r.stdout + r.stderr)
    record["digest_bridge_ok"] = r.returncode == 0
    print(f"  {'ok  ' if r.returncode == 0 else 'FAIL'} common-php/ digest bridge")

    sub_bad, _ = c_subdir_audit()
    problems.extend(sub_bad)
    record["c_subdir_ok"] = not sub_bad
    print(f"  {'ok  ' if not sub_bad else 'FAIL'} no patterns-php/*/c/ "
          f"subdirectory (RECAP_PHP.md open item 17)")

    alloc_bad, alloc_notes = shim_link_audit()
    problems.extend(alloc_bad)
    record["allocator_symlink_ok"] = not alloc_bad
    record["allocator_symlink_notes"] = alloc_notes
    print(f"  {'ok  ' if not alloc_bad else 'FAIL'} "
          f"<row>/c/{SHIM_HEADER} symlink (PROTOCOL_PHP.md §B2)")
    for n in alloc_notes:
        print(f"       | {n}")

    ov_bad, ov_note = overlap_selftest()
    problems.extend(ov_bad)
    record["overlap_selftest_ok"] = not ov_bad
    print(f"  {'ok  ' if not ov_bad else 'FAIL'} provenance.py overlap "
          f"self-test ({ov_note})")

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

    sizes = why_sizes()
    record["why_sizes"] = sizes
    print(f"  --   `idiom.why` row-specific size (REPORTED, NO LIMIT -- "
          f"RECAP_PHP.md open item 19, `why_sizes`)")
    for r, s in sorted(sizes.items()):
        print(f"       | {r}: {s['row_specific_words']} words "
              f"({s.get('prefix_words')} before the shared block + "
              f"{s.get('tail_words')} after). PAT corpus n=33: "
              f"median 989, p90 1817, max 3140. NO LIMIT.")

    _cov_bad, cov_notes = preflight_coverage_audit()
    record["uncertified_records"] = cov_notes
    print(f"  {'ok  ' if not cov_notes else '!!  '} every php record has a "
          f"preflight record beside it")
    for n in cov_notes:
        print(f"       | {n}")

    record["harness_php_sha256"] = harness_php_hashes()
    record["problems"] = problems
    return problems, record


#: ⚠ NOT `results-php/gate/`. `measure.py --check-stale` globs
#: `results/gate/p*.json` and `results/p*.json`, and `ph00-smoke.preflight.json`
#: matches `p*.json` -- dropping it beside the gate records would make the
#: staleness check try to read it as one. Its own directory costs nothing.
PREFLIGHT_DIR = os.path.join(REPO, "results-php", "preflight")


#: The one field that moves for no reason. TASK_PHP_005 F-2c MEASURED it: two
#: consecutive identical-source runs differ in `when` and in NOTHING else --
#: `sha256(rest)` was `d91ce008ad273b36` both times. It lives in a gitignored
#: sidecar so the record itself is committable.
WHEN_FIELD = "when"

#: In-process slot bookkeeping: `main()` writes the same run's record up to
#: three times (`tool RUNNING` -> `tool exited`), and those are ONE run.
_RUN_SLOT = {}


def _record_paths(stem):
    return (os.path.join(PREFLIGHT_DIR, f"{stem}.preflight.json"),
            os.path.join(PREFLIGHT_DIR, f"{stem}.when.json"))


def write_preflight_record(record):
    """APPEND this run to `results-php/preflight/<row>.preflight.json`.

    ⚠⚠ THIS USED TO BE ONE FILE PER *ROW*, WHICH MEANT LAST-WRITE-WINS.
    TASK_PHP_005 F-2a measured the consequence: a run taken with
    `--no-provenance` recorded `provenance_skipped: true`, and **the next
    ordinary preflight ERASED it**. The record existed to prove that a run
    certified nothing, and any later run destroyed exactly that evidence. The
    file now holds `{"row": ..., "runs": [...]}` and a run is appended, never
    overwritten.

    ⚠ CONSECUTIVE IDENTICAL RUNS COLLAPSE, and that is what makes the file
    COMMITTABLE. `RECAP_PHP.md` open item 18: the manager gitignored this
    directory as churn, and TASK_PHP_005 F-2c showed the churn was ONE field --
    `when` -- while `gate_argv` is a function of the command and everything else
    is byte-identical across runs. So `when` goes to a gitignored
    `<row>.when.json` sidecar and the committed record is dropped in if it
    repeats the previous entry. Two identical `--check-stale` runs therefore
    leave the committed file BYTE-IDENTICAL, and a `--no-provenance` run leaves
    a permanent entry in git.

    ⚠ It is still EVIDENCE AND NOT A PIN: nothing hashes it, so it can prove
    `--no-provenance` WAS used and cannot prove it was not. Putting
    `harness-php/*.py` into `source_sha256` needs `check.py`'s `srcs` glob to
    reach `harness-php/`, i.e. a `harness/` edit and a 33-pattern re-gate
    (`PLAN_PHP.md` §2.1, `RECAP_PHP.md` open item 13). `preflight_coverage_audit`
    is the cheapest honest substitute for the absence half.
    """
    os.makedirs(PREFLIGHT_DIR, exist_ok=True)
    stem = record.get("row") or "_norow"
    out, when_out = _record_paths(stem)
    body = {k: v for k, v in record.items() if k != WHEN_FIELD}

    doc = {"row": record.get("row"), "runs": []}
    if os.path.exists(out):
        try:
            old = json.load(open(out, encoding="utf-8"))
        except (ValueError, OSError):
            old = None
        if isinstance(old, dict) and isinstance(old.get("runs"), list):
            doc = old
        elif isinstance(old, dict):
            # A pre-TASK_PHP_006 single-record file. Keep it: it is the only
            # evidence about the runs that produced the records already on
            # disk, and dropping it would be exactly the erasure F-2a is about.
            legacy = {k: v for k, v in old.items() if k != WHEN_FIELD}
            legacy["_schema"] = "pre-TASK_PHP_006 single-record file, migrated"
            doc = {"row": old.get("row"), "runs": [legacy]}

    slot = _RUN_SLOT.get(stem)
    if slot is None:
        doc["runs"].append(body)
        slot = len(doc["runs"]) - 1
        _RUN_SLOT[stem] = slot
    else:
        slot = min(slot, len(doc["runs"]) - 1)
        doc["runs"][slot] = body
    # Collapse a run that says exactly what the previous one said.
    if slot >= 1 and doc["runs"][slot] == doc["runs"][slot - 1]:
        doc["runs"].pop(slot)
        _RUN_SLOT[stem] = slot = len(doc["runs"]) - 1

    with open(out, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2, sort_keys=False)
        fh.write("\n")
    with open(when_out, "w", encoding="utf-8") as fh:
        json.dump({"row": record.get("row"), "last_run_slot": slot,
                   WHEN_FIELD: record.get(WHEN_FIELD)}, fh, indent=2)
        fh.write("\n")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tool", default="check", choices=sorted(TOOLS))
    ap.add_argument("--no-provenance", action="store_true")
    ap.add_argument("--preflight", action="store_true",
                    help="run the preflight and stop")
    ap.add_argument("--audit", action="store_true",
                    help="report php records with no preflight record and "
                         "exit 1 if there are any (nothing else run)")
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

    # ⚠⚠ RECLAIM THIS SCRIPT'S OWN FLAGS FROM THE REMAINDER. TASK_PHP_005 F-7:
    # `argparse.REMAINDER` starts collecting at the first POSITIONAL, so
    # `gate.py ph00 --preflight` left `a.preflight` False and forwarded
    # `--preflight` to `check.py`, which died with `unrecognized arguments`.
    # ⚠ The manager's own 06:55 `ph00.preflight.json` -- cited as
    # manager-verified evidence for the gitignore decision -- is an instance: a
    # FAILED check.py launch (`tool_returncode 2`) recorded as a preflight. Part
    # of the evidence for a manager decision was an artefact of this bug.
    # These three flags mean the same thing wherever they appear, so take them.
    reclaimed = []
    for flag, attr in (("--preflight", "preflight"),
                       ("--no-provenance", "no_provenance"),
                       ("--audit", "audit")):
        while flag in argv:
            argv.remove(flag)
            setattr(a, attr, True)
            reclaimed.append(flag)
    if reclaimed:
        print(f"note: {' '.join(sorted(set(reclaimed)))} appeared after the row "
              f"and is gate.py's own flag, not the tool's -- taken here rather "
              f"than forwarded (TASK_PHP_005 F-7).")

    row = next((x for x in argv if not x.startswith("-")), None)

    if a.audit:
        _bad, notes = preflight_coverage_audit()
        for n in notes:
            print(f"  {n}")
        print("preflight coverage: "
              + ("complete" if not notes else f"{len(notes)} problem(s)"))
        return 1 if notes else 0

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
