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

The preflight is NINE things. ⚠ EIGHT of them can FAIL the run; stage 8 is a
REPORTED number and cannot. ⚠⚠ THIS LINE SAID "FIVE THINGS, ALL OF WHICH CAN
FAIL" AND THE "ALL" WAS FALSE OF STAGE 1 (TASK_PHP_005 F-6): stage 1 ran
`root.py`'s `build()` BEFORE its `check()`, so a mis-aimed shim link -- one
planted at the FROZEN PAT `results/` tree -- was silently repaired and recorded
`shim_ok: true`. Fixed at TASK_PHP_006: check, then repair, then check, and a
repair is printed and recorded in `shim_repaired`. ⚠ It then said SEVEN over a
body of seven-plus-two; corrected at TASK_PHP_008, where stage 9 became a
failure. **Count the `problems.extend` / `problems.append` calls in
`preflight()` before believing this number** -- `.tasks/PROTOCOL.md` rule 13.

  1. `harness-php/root.py` -- the shim exists and every link points where it
     should, and nothing that is not a link lives in it.
  2. `common-php/digest_bridge.py --verify` -- every `common-php/` file is in
     some digest. ⚠ `check.py`'s `common/` globs are `driver.*`, `*.py` and
     `layout/*.py`, ALL NON-RECURSIVE, so `emalloc_shim.h` is in none of them
     and the bridge is what covers it. Ten committed control sources sat in no
     digest at all on the PAT side for many tasks; this is that check.
  3. ⚠⚠ `c_digest_audit()` -- EVERY file under `<row>/c/` has a digest key.
     `check.py` and `measure.py` build both digests from `glob(<row>/c/*)`,
     which is NON-RECURSIVE and never matches a leading dot, so a file in a
     `c/` subdirectory or a `c/.dotfile` is COMPILED and in NO digest at all.
     ⚠ It was a blanket BAN on the subdirectory layout (`c_subdir_audit`,
     TASK_PHP_006) until TASK_PHP_008 §1: TASK_PHP_007 M1/m1 showed the ban was
     UNSOUND (it skipped a symlinked directory by name, and never saw a
     dotfile) and OVER-STRICT (the flat-symlink layout is safe under exactly
     this audit). The layout is now AVAILABLE AND PRICED.
  4. ⚠⚠ `shim_link_audit()` -- THE ALLOCATOR SYMLINK, **UNCONDITIONAL** since
     TASK_PHP_008 §0. Every row carries `c/emalloc_shim.h` whether or not it
     allocates. ⚠ It used to DETECT allocator use -- a string search
     (TASK_PHP_004, bypassed twice at TASK_PHP_005 F-1) and then `gcc -MM`
     (TASK_PHP_006, bypassed twice at TASK_PHP_007 B1/B2). Both answered
     *"does this row use the allocator?"*, a question with an unbounded answer
     space. See the function's docstring for why the answer was to stop asking.
  5. `overlap_selftest()` -- `provenance.py`'s kernel-overlap normaliser still
     scores the dead-code cases TASK_PHP_005 F-4 built the way it did when they
     were measured. Runs here because a self-test nobody runs is the
     silent-skip class this project keeps finding. ⚠ Since TASK_PHP_008 §2 the
     overlap is REPORTED and no longer refuses, so this guards a NUMBER rather
     than a verdict -- which is still worth guarding: a wrong number is worse
     than an unenforced one.
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
  8. `why_sizes()` + `why_band()` -- ⚠ THE ONE STAGE THAT CANNOT FAIL. Each php
     row's row-specific `idiom.why` size beside the PAT band, which is COMPUTED
     from `patterns/*/spec.md` and no longer a hard-coded constant in a printed
     string (TASK_PHP_007 m6). `RECAP_PHP.md` open item 19: no size rule.
  9. ⚠⚠ `preflight_coverage_audit()` -- A FAILURE SINCE TASK_PHP_008 §3 M4:
     which php records have no preflight record beside them, and which have one
     in which NOT ONE RUN certified the tree. It was a note, on the strength of
     a deadlock that TASK_PHP_007 M4 demonstrated does not exist -- `main()`
     writes the record on the FAILURE path. ⚠ It is a DETECTOR, not a pin, and
     it cannot be made into one from here; see TASK_PHP_006 §1.3.
     `gate.py --audit` is the same check with an exit code and nothing else run.

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
⚠⚠⚠ THE `<row>/c/emalloc_shim.h` SYMLINK -- UNCONDITIONAL SINCE TASK_PHP_008
============================================================================
⚠⚠ EVERY row carries it, whether or not it allocates. That is the design
change, and it exists because the alternative -- deciding WHICH rows need it --
was closed twice and reopened twice (TASK_PHP_005 F-1, TASK_PHP_007 B1/B2).
Full argument in `shim_link_audit`'s docstring; the short form is that
*"does this row use the allocator?"* has an unbounded answer space and a guard
that enumerates idioms is reopened by the next idiom. There is now nothing to
detect: `os.path.islink` + `os.path.realpath`, no subprocess, no compiler, no
flag space, no fallback, no regex.

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

⚠⚠ AND THAT ASYMMETRY IS THE WHOLE PRICE OF THE UNCONDITIONAL RULE, WHICH IS
SMALLER THAN IT LOOKS. The GATE half was ALREADY unconditional and has been
since TASK_PHP_002: `common-php/digest_bridge.py` carries `emalloc_shim.h`'s
sha256 in its `BRIDGED` table, and `check.py`'s `common/*.py` glob puts
digest_bridge.py's OWN hash into EVERY php gate record -- so a shim edit has
always staled every php gate record, linked or not. Measured at TASK_PHP_008,
`.temp/php8/02-digest-reality.log`. What the link adds is the MEASUREMENT half,
so the marginal cost of "every row" over "every allocating row" is a re-measure
plus a `report.py` render, on top of a re-gate that was owed anyway.

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

#: The one allocator. `PROTOCOL_PHP.md` §B. EVERY row links it -- see
#: `shim_link_audit`, and TASK_PHP_008 §0 for why "every" and not "every row
#: that uses it".
SHIM_HEADER = "emalloc_shim.h"
#: The spelling `PROTOCOL_PHP.md` §B2 prescribes, from `<row>/c/`.
CANONICAL_LINK = os.path.join("..", "..", "..", "common-php", SHIM_HEADER)

#: ⚠⚠⚠ THERE IS NO DETECTOR HERE ANY MORE, AND THAT IS THE WHOLE POINT.
#: TASK_PHP_008 §0. `_INCLUDE_RX`, `_MM_CONFIGS`, `_tu_closure`, `_text_mentions`
#: and the text fallback were DELETED. Every one of them answered the question
#: *"does this row use the allocator?"*, and that question has an UNBOUNDED
#: answer space -- every preprocessor spelling, every flag combination, every
#: compiler -- so each round enumerated a few more of it and the next idiom
#: reopened the hole:
#:
#:   TASK_PHP_004  a mandatory symlink, checked by a STRING SEARCH of `c/*`
#:                 -> bypassed by `#include "emalloc_shim.c"` and by `c/<sub>/*`
#:   TASK_PHP_006  the string search replaced by `gcc -MM`
#:                 -> bypassed by `__OPTIMIZE__`, `__clang__` and
#:                    `__has_include` (2 of build.py's 8 preprocessor states
#:                    were simulated), and by a fallback that FAILS OPEN and
#:                    that the row can CHOOSE (TASK_PHP_007 B1/B2)
#:
#: ⚠ A guard whose correctness depends on enumerating idioms will be reopened
#: by the next idiom. Two rounds was enough evidence. The rule is now
#: UNCONDITIONAL -- see `shim_link_audit` -- so there is nothing to detect.


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def _walk_files(top, _seen=None):
    """Every file under `top`, FOLLOWING directory symlinks, cycle-safe.

    ⚠ `os.walk` does not follow a directory symlink, and `glob("c/*")` never
    matches a leading dot. TASK_PHP_007 M1 and m1 both walked round
    `c_subdir_audit` on exactly those two properties: `ln -s ../../extract/Zend
    c/zend` and `c/.payload.h` each COMPILED, landed in NO digest, and were not
    refused. This walker sees both. `followlinks=True` on `os.walk` would loop
    for ever on a cyclic link; the `_seen` set of realpaths is what makes
    following safe.

    Yields absolute paths, dotfiles included.
    """
    _seen = _seen if _seen is not None else set()
    real = os.path.realpath(top)
    if real in _seen:
        return
    _seen.add(real)
    try:
        entries = sorted(os.listdir(top))
    except OSError:
        return
    for e in entries:
        p = os.path.join(top, e)
        if os.path.isdir(p):
            yield from _walk_files(p, _seen)
        else:
            yield p


def c_digest_audit(patterns_dir=None):
    """⚠⚠ EVERY file under a row's `c/` is in BOTH digests, or the row is
    refused. Returns `(problems, [])`.

    ⚠⚠⚠ THIS REPLACES `c_subdir_audit`, WHICH BANNED THE SUBDIRECTORY LAYOUT
    OUTRIGHT. TASK_PHP_007 M1/m1 PROVED THE BAN WAS BOTH UNSOUND AND
    OVER-STRICT, AND THE MANAGER LIFTED IT AT TASK_PHP_008 §1.

      * UNSOUND: `c_subdir_audit` skipped a SYMLINKED directory by name
        (`if not os.path.isdir(p) or os.path.islink(p): continue`), so
        `ln -s ../../../extract/Zend c/zend` compiled every header behind it
        into NEITHER digest, unrefused. And `glob("c/*")` never matches a
        leading dot, so `c/.payload.h` walked round it too.
      * OVER-STRICT: the flat-symlink hatch the ban's own docstring priced and
        declined *"because nothing would force the NEXT file added to that
        subdirectory to get a link"* is forced by twelve lines. The reviewer
        BUILT them and fired them in both directions
        (`.temp/php7/a7_manager_calls.py`, log `07-manager-calls.log`).

    ⚠⚠ AND THE REASON THIS IS SOUND WHERE THE ALLOCATOR DETECTOR WAS NOT:
    **IT ENUMERATES FILES -- A FINITE, OBSERVABLE SET -- NOT IDIOMS.** There is
    no preprocessor state, no compiler, no flag space and no spelling. A file
    either has a key in `glob("c/*")` or it does not, and `_walk_files` sees
    every file including the two classes `glob` cannot.

    ============================================================================
    WHY A FILE WITH NO FLAT KEY IS A REAL DEFECT
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
    allocator: ANY source in a `c/` subdirectory is unpinned -- and so is any
    DOTFILE at the top level of `c/`, for the same reason one directory over.

    ⚠ Fixing the two globs is a `harness/` edit; `harness/*.py` is hashed into
    all 33 PAT gate records and `harness/measure.py` into all 33 measurement
    records, so the repair costs a 33-pattern re-gate (`RECAP_PHP.md` open item
    17, carried not closed). The php side pays for it with a flat symlink
    instead, which costs nothing.

    ============================================================================
    WHAT THIS AUDIT DEMANDS, AND THE TWO WAYS TO SATISFY IT
    ============================================================================
    Every file `_walk_files` finds under `<row>/c/` must have the same
    `realpath` as some entry of `glob("<row>/c/*")` that `os.path.isfile`
    accepts -- because that glob, and only that glob, is what both digests are
    built from.

      1. FLATTEN. Name the file for its origin -- `c/zend__zend_hash.h` for
         `Zend/zend_hash.h` -- and rewrite the `#include`. One deletion-ledger
         line (`PROTOCOL_PHP.md` §A2), and still the cheapest answer.
      2. FLAT SYMLINK BESIDE IT. Keep `c/zend/zend_hash.h` and add
         `c/zend__zend_hash.h -> zend/zend_hash.h`. ✅ MEASURED at TASK_PHP_006
         (`.temp/php6/05-b1-rerun.log` §C) and re-derived independently at
         TASK_PHP_007 (`.temp/php7/03-subdir.log`, row `ph83-flatlink`): `glob`
         returns the flat symlink, `os.path.isfile` and `sha256_file` follow it,
         so the real bytes land in BOTH digests under the flat key. ⚠ The
         layout is AVAILABLE AND PRICED, not forbidden -- and this audit is
         what forces the next file added to the directory to get a link, which
         is the exact objection TASK_PHP_006 declined it on.

    ⚠ A DOTFILE HAS NO SANCTIONED FORM. `glob` cannot match it, so there is no
    flat key to give it; rename it.
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
        # EXACTLY what `check.py:10314` and `measure.py:226` glob, and the
        # `os.path.isfile` filter they apply. A symlink is kept: `isfile`
        # follows it and `sha256_file` hashes the TARGET's bytes.
        keyed = {os.path.realpath(p): os.path.basename(p)
                 for p in sorted(glob.glob(os.path.join(cdir, "*")))
                 if os.path.isfile(p)}
        for p in _walk_files(cdir):
            real = os.path.realpath(p)
            if real in keyed:
                continue
            rel = os.path.relpath(p, cdir)
            dotted = any(part.startswith(".") for part in rel.split(os.sep))
            flat = rel.replace(os.sep, "__")
            fix = (f"       Fix: RENAME it -- `glob` never matches a leading "
                   f"dot, so there is no flat key a dotfile can have.\n"
                   if dotted else
                   f"       Fix: EITHER flatten it to c/{flat} and rewrite the "
                   f"#include, OR add the flat symlink beside it:\n"
                   f"             ln -s {rel} patterns-php/{row}/c/{flat}\n")
            problems.append(
                f"digest: {row}: c/{rel} is COMPILED and in NO DIGEST.\n"
                f"       check.py:10314 and measure.py:226 build both digests "
                f"from `glob(<row>/c/*)` + isfile(): that glob is "
                f"NON-RECURSIVE and never matches a leading dot, while "
                f"`build_c` passes `-I <row>/c` and the preprocessor is "
                f"recursive. So this file is in no gate digest, no measurement "
                f"digest, and not even check.py's --no-build staleness scan "
                f"(check.py:10187-10189, same glob) -- editing it would not "
                f"mark a single binary stale.\n"
                + fix
                + f"       (TASK_PHP_007 M1/m1; TASK_PHP_008 §1 lifted the "
                  f"blanket subdirectory ban in favour of this audit.)")
    return problems, []


def shim_link_audit(patterns_dir=None, common_dir=None):
    """⚠⚠⚠ EVERY `patterns-php/` ROW CARRIES `c/emalloc_shim.h` AS A SYMLINK TO
    `common-php/emalloc_shim.h` -- UNCONDITIONALLY. Returns `(problems, notes)`.

    ============================================================================
    WHY UNCONDITIONALLY, AND WHY THIS IS THE THIRD ATTEMPT
    ============================================================================
    B1 was closed twice and reopened twice, and both fixes answered the same
    question -- *"does this row use the allocator?"*:

      TASK_PHP_004  a STRING SEARCH over `c/*`.
                    Bypassed by `#include "emalloc_shim.c"` (the audit knew only
                    the `.h`, and `emalloc_shim.c`'s own header comment claimed
                    it *"CANNOT BE"* on the build path -- true of `build.py`'s
                    TU list, false of the preprocessor) and by `c/<subdir>/*`
                    (`glob` is not recursive). TASK_PHP_005 F-1.
      TASK_PHP_006  `gcc -MM`, "the preprocessor, which has no spelling".
                    ⚠ It simulated **2 of build.py's 8** preprocessor states:
                    `_MM_CONFIGS` swept `-DSLB_ISOLATED` and hard-coded `gcc`
                    with no `-O`, so `__OPTIMIZE__`, `__clang__` and
                    `__has_include` each gave a LIVE allocator in a real
                    measured cell with the audit silent -- and emitting a NOTE
                    saying *"dead code … Not treated as a shim user"* about a
                    row that allocates 1000 times in half its cells. Its text
                    FALLBACK failed OPEN and the row could CHOOSE it (a `c/*.c`
                    that `build.py` never compiles makes `gcc -MM` fail for the
                    whole row). TASK_PHP_007 B1/B2.

    ⚠⚠ THAT QUESTION HAS AN UNBOUNDED ANSWER SPACE, so each round enumerated a
    few more of it. **A guard whose correctness depends on enumerating idioms
    will be reopened by the next idiom.** TASK_PHP_008 §0 stopped asking it:
    every row carries the link whether or not it allocates, so there is nothing
    to detect. No subprocess, no flag space, no compiler, no fallback, no regex.

    ============================================================================
    WHAT IT COSTS, STATED HONESTLY -- AND IT IS SMALLER THAN THE DECISION SAID
    ============================================================================
    An `emalloc_shim.h` edit now stales EVERY php row, not only the allocating
    ones. ⚠ But the GATE half of that was ALREADY unconditional and has been
    since TASK_PHP_002: `common-php/digest_bridge.py` carries the shim's sha256
    in `BRIDGED`, and `check.py`'s `common/*.py` glob puts *digest_bridge.py's
    own hash* into every php gate record -- measured at TASK_PHP_008,
    `.temp/php8/02-digest-reality.log`. So the MARGINAL price of the
    unconditional link is the MEASUREMENT half only: a re-measure plus a
    `report.py` render per row, on top of a re-gate that was owed anyway.

    It errs SAFE: it can over-re-gate, and it can never leave a stale record
    FRESH.

    ⚠ `uses_allocator` in the row's `provenance` block is the DECLARED answer to
    the question this audit stopped asking. It is documentation for a reviewer;
    nothing depends on it being right, and nothing here reads it.

    ⚠ Parameterised on purpose so a negative test can point it at a fixture
    tree under `.temp/` instead of at `patterns-php/`
    (`.temp/php5/b1_bypass.py`, `.temp/php7/a1_flagmatrix.py`). A guard nobody
    has constructed a failing case for is a guard nobody has tested.
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
        why = (f"       Every php row carries it, whether or not it allocates: "
               f"the alternative is a detector, and two of those have been "
               f"bypassed (TASK_PHP_005 F-1, TASK_PHP_007 B1/B2). With the "
               f"link, the allocator's bytes are in the GATE digest and the "
               f"MEASUREMENT digest under `c/{SHIM_HEADER}`, so a later shim "
               f"fix can never leave this row's Ir numbers FRESH under an "
               f"allocator that no longer exists.\n"
               f"       Fix:  ln -s {CANONICAL_LINK} "
               f"patterns-php/{row}/c/{SHIM_HEADER}\n"
               f"       (PROTOCOL_PHP.md §B2; TASK_PHP_008 §0.)")

        if not os.path.islink(link):
            if os.path.exists(link):
                problems.append(
                    f"allocator: {row}: {row}/c/{SHIM_HEADER} is a REGULAR "
                    f"FILE, not a symlink. A copy is hashed under the same key "
                    f"and looks identical in the record while holding a "
                    f"DIFFERENT allocator.\n" + why)
            else:
                problems.append(
                    f"allocator: {row}: {row}/c/{SHIM_HEADER} IS ABSENT.\n"
                    + why)
            continue
        got = os.path.realpath(link)
        if got != want:
            problems.append(
                f"allocator: {row}: {row}/c/{SHIM_HEADER} -> "
                f"{os.readlink(link)!r} resolves to {got}, not "
                f"{want}. Every row links the ONE allocator.\n" + why)
            continue
        target = os.readlink(link)
        if target != CANONICAL_LINK:
            notes.append(f"{row}: c/{SHIM_HEADER} -> {target!r} resolves "
                         f"correctly but is not the canonical "
                         f"{CANONICAL_LINK!r} (PROTOCOL_PHP.md §B2)")
        notes.append(f"{row}: c/{SHIM_HEADER} OK -- symlink, in BOTH digests")
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


def why_band(patterns_dir=None):
    """The PAT corpus's row-specific `why` distribution, COMPUTED not quoted.

    ⚠ TASK_PHP_007 m6: `preflight` printed the band `median 989, p90 1817,
    max 3140` as a HARD-CODED CONSTANT inside an f-string, and `why_sizes`
    reads `patterns-php/` only -- so the moment PAT gains or edits a row the
    printed comparison is silently wrong. That is the citation-rot class this
    project keeps paying for, and the engineer disclosed it rather than fixing
    it. This derives it from `patterns/*/spec.md` on every run instead.

    ⚠ READ-ONLY. `patterns/` is frozen PAT infrastructure; this opens files
    there and writes nothing.
    """
    sizes = why_sizes(patterns_dir or os.path.join(REPO, "patterns"))
    vals = sorted(s["row_specific_words"] for s in sizes.values())
    if not vals:
        return None

    # ⚠⚠ THE PERCENTILE CONVENTION IS PINNED TO THE ONE ALREADY PUBLISHED, AND
    # THAT MATTERS MORE THAN WHICH ONE IS "RIGHT". `RECAP_PHP.md`'s size box
    # warns that this quantity already HAS three answers and that arbitrating
    # it again is the wrong move. `floor(f*(n-1))` -- numpy's `lower` -- is what
    # reproduces TASK_PHP_006's published `p90 1817`; `round` gives 2062 and
    # linear interpolation 2013, both defensible and both a FOURTH answer.
    # Measured at TASK_PHP_008, `.temp/php8/07-why-band.log`.
    # (The `527 / 989 / 1544` quartiles quoted in `why_sizes` and
    # `PROTOCOL_PHP.md` §E are Tukey's hinges over the same 33 values and are
    # CORRECT under that convention -- checked, not assumed.)
    def q(f):
        return vals[int(f * (len(vals) - 1))]

    return {"n": len(vals), "min": vals[0], "median": q(0.5),
            "p90": q(0.9), "max": vals[-1]}


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


#: ⚠⚠⚠ THE PREFIX THAT MAKES M4 AND M5 COMPOSE, AND WITHOUT IT THEY DEADLOCK.
#: This module's OWN coverage problems are tagged with it, and
#: `_run_is_certifying` discounts them. Read that function before touching it.
_COVERAGE_TAG = "preflight coverage:"


def _run_is_certifying(run):
    """Did this stored run actually certify the tree? Returns `(bool, why)`.

    ⚠⚠ TASK_PHP_007 M5: `--audit` only asked whether a preflight FILE existed,
    so a row whose ONLY recorded run was `PREFLIGHT FAILED` /
    `provenance_skipped` / `shim_ok: false` reported "coverage: complete".
    This is what reads the verdict instead.

    ⚠⚠⚠ AND THE OBVIOUS SPELLING OF IT DEADLOCKS. FOUND AT TASK_PHP_008,
    BEFORE SHIPPING, BY RUNNING IT (`.temp/php8/g4_selfdeadlock.py`,
    log `21-selfdeadlock-BEFORE.log`). The obvious rule is *"a run whose
    verdict is PREFLIGHT FAILED never certifies"*, and combined with M4 --
    which makes a MISSING record fail the preflight -- it is self-referential:

        run 1  no record          -> coverage problem -> PREFLIGHT FAILED
                                  -> writes a record whose only run FAILED
        run 2  record exists, its only run FAILED (M5)
                                  -> coverage problem -> PREFLIGHT FAILED
        run N  ... for ever, and NOTHING the operator can do fixes it.

    Measured: 6 runs, `coverage problems = 1` every time.
    ⚠ **THAT IS A REAL DEADLOCK, AND IT IS THE MIRROR OF THE ONE TASK_PHP_007
    M4 DISPROVED** -- the engineer asserted a deadlock that did not exist, and
    the fix for that assertion created one that does. Both were settled by
    running the loop rather than reading the code.

    ✅ THE REPAIR, AND IT IS ALSO THE HONEST READING: a run that failed ONLY on
    a coverage problem still verified the shim, the digest bridge, the `c/`
    digest keys, the allocator symlink, the overlap self-test, the manifest and
    provenance. It certified THIS tree; what it complained about was some OTHER
    row's paperwork. So only a SUBSTANTIVE problem -- one not tagged
    `_COVERAGE_TAG` -- makes a run non-certifying.

    ⚠ Do not "simplify" this back to `verdict == "PREFLIGHT FAILED"`. The
    must-fire control in `g4_selfdeadlock.py` exists to catch exactly that
    edit, and `verdict` is redundant anyway: it is `PREFLIGHT FAILED` iff
    `problems` is non-empty.
    """
    if not isinstance(run, dict):
        return False, "unparseable entry"
    substantive = [p for p in (run.get("problems") or [])
                   if not str(p).startswith(_COVERAGE_TAG)]
    if substantive:
        return False, (f"{len(substantive)} recorded problem(s), first: "
                       f"{str(substantive[0]).splitlines()[0][:60]}")
    if run.get("provenance_skipped"):
        return False, "provenance_skipped=true (--no-provenance)"
    if run.get("shim_ok") is False:
        return False, "shim_ok=false"
    return True, ""


def preflight_coverage_audit():
    """⚠ Which php records were produced by a run NOTHING certified?

    Returns `(problems, notes)`.

    ⚠⚠ IT RETURNS **PROBLEMS** SINCE TASK_PHP_008 §3 M4. It used to return
    notes only, justified by a DEADLOCK -- *"if a missing record failed the
    preflight, the repair (`gate.py --preflight <row>`) is itself a preflight
    and would fail on every OTHER uncovered row BEFORE WRITING ANYTHING"*.
    ⚠ **THAT DEADLOCK DOES NOT EXIST**: `main()` writes the record on the
    FAILURE path before returning 2, so N uncovered rows are repaired by the
    same N `--preflight <row>` invocations the note design needed anyway.
    Demonstrated by the reviewer (`.temp/php7/08-deadlock.log`) and re-run
    end-to-end at TASK_PHP_008 (`.temp/php8/23-coverage-cap-AFTER.log`, the
    three-uncovered-row repair loop).

    ⚠⚠ BUT MAKING IT A FAILURE CREATES A DIFFERENT DEADLOCK THAT IS REAL, AND
    `_run_is_certifying` IS WHAT AVOIDS IT. Read that function before changing
    either of them: this stage's own problems are tagged `_COVERAGE_TAG` and
    discounted there precisely so the pair composes.

    ⚠⚠ AND IT READS THE VERDICT, NOT JUST THE FILENAME (TASK_PHP_007 M5). A
    row whose only recorded run was `PREFLIGHT FAILED` / `provenance_skipped` /
    `shim_ok: false` used to count as covered, so the one question the
    committed record exists to answer was answered wrongly by the only tool
    that asked it.

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

    ⚠ `gate.py --audit` is the same check with an exit code and nothing else
    run, for anyone who wants it standalone.
    """
    problems, uncovered, hollow = [], [], []
    rdir = os.path.join(REPO, "results-php")
    if not os.path.isdir(rdir):
        return problems, []
    recs = (sorted(glob.glob(os.path.join(rdir, "*.json")))
            + sorted(glob.glob(os.path.join(rdir, "gate", "*.json"))))
    for rec in recs:
        if rec.endswith(".partial.json"):
            continue
        stem = os.path.basename(rec)[:-len(".json")]
        rid = stem.split("-")[0]
        hits = sorted(glob.glob(os.path.join(PREFLIGHT_DIR,
                                            f"{rid}*.preflight.json")))
        if not hits:
            uncovered.append(os.path.relpath(rec, REPO))
            continue
        # ⚠ THE FILE EXISTING IS NOT THE QUESTION (TASK_PHP_007 M5).
        why, certified = [], False
        for h in hits:
            try:
                doc = json.load(open(h, encoding="utf-8"))
            except (ValueError, OSError) as e:
                why.append(f"{os.path.basename(h)}: unreadable ({e})")
                continue
            runs = doc.get("runs") if isinstance(doc, dict) else None
            if not isinstance(runs, list) or not runs:
                why.append(f"{os.path.basename(h)}: no runs[]")
                continue
            for run in runs:
                ok, reason = _run_is_certifying(run)
                if ok:
                    certified = True
                    break
                why.append(f"{os.path.basename(h)}: {reason}")
            if certified:
                break
        if not certified:
            hollow.append((os.path.relpath(rec, REPO), sorted(set(why))[:4]))
    if uncovered:
        problems.append(
            f"{_COVERAGE_TAG} {len(uncovered)} php record(s) have NO "
            f"preflight record: {uncovered}. Either the run did not go through "
            f"gate.py (PLAN_PHP.md §2.1a documents that spelling and nothing "
            f"downstream records it -- TASK_PHP_005 §1), or the record was "
            f"deleted.\n"
            f"       Fix: `python3 harness-php/gate.py --preflight <row>` per "
            f"uncovered row, and say in the report that the ORIGINAL run was "
            f"not certified -- this certifies the CURRENT tree, not that one.\n"
            f"       ⚠ THERE IS NO DEADLOCK: `main()` writes the record on the "
            f"FAILURE path, so each repair invocation covers its own row even "
            f"while this stage is still failing on the others "
            f"(TASK_PHP_007 M4).")
    for rec, why in hollow:
        problems.append(
            f"{_COVERAGE_TAG} {rec} HAS a preflight record and NOT ONE RUN "
            f"IN IT CERTIFIED THE TREE: {why}.\n"
            f"       A record that only says the preflight FAILED, or that "
            f"provenance was SKIPPED, is evidence AGAINST the row and not for "
            f"it -- and `--audit` used to call that `complete` because it "
            f"never opened the file (TASK_PHP_007 M5).\n"
            f"       Fix: `python3 harness-php/gate.py --preflight <row>` with "
            f"the tarball present, and read the output.")
    return problems, []


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

    sub_bad, _ = c_digest_audit()
    problems.extend(sub_bad)
    record["c_digest_ok"] = not sub_bad
    print(f"  {'ok  ' if not sub_bad else 'FAIL'} every patterns-php/*/c/ file "
          f"has a digest key (RECAP_PHP.md open item 17)")
    for b in sub_bad:
        print(f"       | {b.splitlines()[0]}")

    alloc_bad, alloc_notes = shim_link_audit()
    problems.extend(alloc_bad)
    record["allocator_symlink_ok"] = not alloc_bad
    record["allocator_symlink_notes"] = alloc_notes
    print(f"  {'ok  ' if not alloc_bad else 'FAIL'} "
          f"<row>/c/{SHIM_HEADER} symlink, UNCONDITIONAL "
          f"(PROTOCOL_PHP.md §B2, TASK_PHP_008 §0)")
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
    band = why_band()
    record["why_band_pat"] = band
    band_txt = (f"PAT corpus n={band['n']}: median {band['median']}, "
                f"p90 {band['p90']}, max {band['max']}."
                if band else "PAT corpus: not readable from here.")
    print(f"  --   `idiom.why` row-specific size (REPORTED, NO LIMIT -- "
          f"RECAP_PHP.md open item 19, `why_sizes`)")
    for r, s in sorted(sizes.items()):
        print(f"       | {r}: {s['row_specific_words']} words "
              f"({s.get('prefix_words')} before the shared block + "
              f"{s.get('tail_words')} after). {band_txt} NO LIMIT.")

    # ⚠⚠ A FAILURE SINCE TASK_PHP_008 §3 M4, AND THE RETURN VALUE IS BOUND.
    # It used to read `_cov_bad, cov_notes = ...` and DISCARD the problems, so
    # the stage could not have failed the run even if it had returned any
    # (TASK_PHP_007 M4, parenthetical). Two lines, not one.
    cov_bad, _cov_notes = preflight_coverage_audit()
    problems.extend(cov_bad)
    record["uncertified_records"] = cov_bad
    print(f"  {'ok  ' if not cov_bad else 'FAIL'} every php record has a "
          f"CERTIFYING preflight record beside it")
    for n in cov_bad:
        print(f"       | {n.splitlines()[0]}")

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


#: ⚠ "COLLAPSE" IS NOT "BOUNDED". Content collapse removes repeats; a tree that
#: genuinely differs between runs still adds one entry each time. TASK_PHP_007
#: M3 measured the committed file quintupling in six cycles of ordinary use and
#: found nothing that prunes -- `gate.py contains 'prune'/'MAX_RUNS'/'truncat'/
#: 'rotate': False/False/False/False`. This is the missing one.
MAX_RUNS = 40


def _carries_evidence(run):
    """Never dropped by the cap. These are the entries the record EXISTS for:
    TASK_PHP_005 F-2a is about a `--no-provenance` run being erased."""
    return bool(isinstance(run, dict)
                and (run.get("provenance_skipped")
                     or run.get("problems")
                     or run.get("shim_repaired")
                     or run.get("verdict") == "PREFLIGHT FAILED"
                     or run.get("_schema")))


def _collapse_and_cap(runs, slot):
    """Drop content-duplicates (keeping the FIRST), then cap. TASK_PHP_008 M3.

    Returns `(runs, slot_or_None, n_dropped_by_the_cap)`. `slot` comes back
    `None` if the entry at `slot` was collapsed away onto an earlier identical
    one -- see `write_preflight_record` for why the caller must not reuse it.
    """
    seen, kept, newslot = {}, [], None
    for i, r in enumerate(runs):
        k = json.dumps(r, sort_keys=True)
        if k in seen:
            continue                      # byte-identical to an earlier entry
        seen[k] = len(kept)
        if i == slot:
            newslot = len(kept)
        kept.append(r)
    dropped = 0
    if len(kept) > MAX_RUNS:
        keep_idx = {0, len(kept) - 1}
        keep_idx |= {i for i, r in enumerate(kept) if _carries_evidence(r)}
        # then the most recent, until the cap is met
        for i in range(len(kept) - 1, -1, -1):
            if len(keep_idx) >= MAX_RUNS:
                break
            keep_idx.add(i)
        dropped = len(kept) - len(keep_idx)
        remap = {}
        pruned = []
        for i, r in enumerate(kept):
            if i in keep_idx:
                remap[i] = len(pruned)
                pruned.append(r)
        newslot = remap.get(newslot)
        kept = pruned
    return kept, newslot, dropped


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

    ⚠⚠ IDENTICAL RUNS COLLAPSE **ON CONTENT, NOT ON ADJACENCY** -- TASK_PHP_008
    §3 M3. Until then a run was dropped only if it equalled the IMMEDIATELY
    PRECEDING one, so two command lines used ALTERNATELY never collapsed at
    all, and one of them is the bracket every task file mandates twice. The
    reviewer measured it: `--preflight` alternated with
    `--tool measure --check-stale` grew the COMMITTED file by **+2 runs and
    +2385 bytes per cycle**, x5 in six cycles, ~19 kB/cycle at 80 rows, with
    nothing pruning (`.temp/php7/05-record-growth.log`). Now a run equal to ANY
    stored run is dropped, so both of those cycles are byte-neutral.

    ⚠ Collapsing on FULL CONTENT can never lose a fact: two entries only
    collapse when every field agrees, `provenance_skipped` included. That is
    why the key is the whole body and not a chosen subset.

    ⚠ AND IT IS CAPPED (`MAX_RUNS`), because "collapse" is not "bounded": a
    tree that really does change between every run produces a distinct entry
    every time. The cap keeps the first, everything that carries evidence
    (a failed verdict, a recorded problem, a skipped provenance, a repaired
    shim) and the most recent, and records how many it dropped.

    `RECAP_PHP.md` open item 18: the manager gitignored this directory as
    churn, and TASK_PHP_005 F-2c showed the churn was ONE field -- `when` --
    while `gate_argv` is a function of the command and everything else is
    byte-identical across runs. So `when` goes to a gitignored
    `<row>.when.json` sidecar and the committed record is stable.

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
    if slot is None or not doc["runs"]:
        doc["runs"].append(body)
        slot = len(doc["runs"]) - 1
    else:
        slot = min(slot, len(doc["runs"]) - 1)
        doc["runs"][slot] = body

    doc["runs"], slot, dropped = _collapse_and_cap(doc["runs"], slot)
    if dropped:
        doc["_dropped_runs"] = doc.get("_dropped_runs", 0) + dropped
    # ⚠ `slot is None` means THIS run collapsed onto an older identical entry.
    # Forget the slot rather than pointing at that older entry: the next
    # in-process write (`tool RUNNING` -> `tool exited`) would otherwise
    # OVERWRITE somebody else's record. It appends instead, and the collapse
    # runs again on the new content.
    _RUN_SLOT[stem] = slot

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
        bad, _notes = preflight_coverage_audit()
        for n in bad:
            print(f"  {n}")
        print("preflight coverage: "
              + ("complete" if not bad else f"{len(bad)} problem(s)"))
        return 1 if bad else 0

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
