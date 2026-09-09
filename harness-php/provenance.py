#!/usr/bin/env python3
"""Validate a php row's `provenance` block against the pinned PHP 5.0.0 tarball.

    python3 harness-php/provenance.py ph00            # one row
    python3 harness-php/provenance.py --all           # every row
    python3 harness-php/provenance.py ph07 --show     # print the excerpt
    python3 harness-php/provenance.py ph07 --no-tarball
                                                      # manifest-only, for a
                                                      # box without the tarball

Exit 0 if every checked row verifies, 1 otherwise.

============================================================================
WHAT IT IS FOR -- AND, PRECISELY, WHAT IT CHECKS
============================================================================
`PLAN_PHP.md` §6 used to say `extract_sha256` turns *"THIS KERNEL came from
those lines of that tarball"* into a one-command check. ⚠ IT DID NOT, AND THE
GAP WAS EXACTLY THE FIRST HALF: until TASK_PHP_004 this module never opened
`c/kernel.c` at all -- the word `kernel` appeared in it only inside that
sentence (TASK_PHP_003 M5). What it checked was *"those lines hash to that"*,
which is worth having and is a different claim.

So, itemised, because a half-true validator is worse than an honest one:

  ✅ CHECKED  the tarball is the pinned one, by sha256 of the whole file
  ✅ CHECKED  `c_file` is in `patterns-php/php-5.0.0.manifest`
  ✅ CHECKED  `sed -n 'a,bp'` over `c_file` really hashes to `extract_sha256`
  ✅ CHECKED  `extract_cmd` is the canonical spelling of `c_file`/`c_lines`
  ✅ CHECKED  the span is NON-EMPTY and IN RANGE (added TASK_PHP_004; an
              out-of-range span used to return `b""` and the caller accepted
              `sha256(b"")` -- so a transposed line number verified GREEN and
              printed `0 bytes`, on the module's own "a wrong span lands here
              often" comment)
  ⚠ REPORTED, NOT CHECKED (since TASK_PHP_008 §2)  a HEURISTIC kernel overlap:
              what fraction of the excerpt's non-trivial lines survive,
              normalised, into the row's `c/kernel*.{c,h}`. It used to REFUSE a
              row below a per-tier floor. It no longer does, and the reason is
              the same one that made the allocator symlink unconditional: the
              floor's correctness depended on recognising every spelling of
              "this block is dead", TASK_PHP_007 M2 measured **nine more** past
              the `#if 0` that TASK_PHP_006 fixed, and a check that must
              enumerate idioms is reopened by the next idiom.
              ⚠ The number, the tier's expectation and the count of
              preprocessor conditions this module CANNOT evaluate
              (`unevaluable_conditionals`) are all printed on every run.
  ✗ NOT CHECKED  ⚠⚠ THAT THE CITED LINES ARE COMPILED. The overlap reads
              `c/kernel*.{c,h}` and nothing else -- not `main.c`, not the
              driver loop, not `build.py`. TASK_PHP_005 F-4: a kernel that
              implements DIVISION, cites MULTIPLICATION and hides the citation
              behind `#if 0` scored 100 % and was ACCEPTED. `#if 0`, `#elif 0`
              and block comments are elided (`selftest_overlap`), but an unused
              `static` function beside the one the driver calls still scores
              full marks, and `-Wall -Wextra` without `-Werror` does not stop
              it. **IT MEASURES TEXT IN A FILE, NOT CODE IN THE BENCHMARK** --
              `RECAP_PHP.md` open item 14 said so before the floor was demoted.
  ✗ NOT CHECKED  `tier` (`verbatim`/`narrowed`/`modelled`) is a free-text
              declaration. The overlap number is evidence about it and no
              more.
  ✗ NOT CHECKED  ⚠⚠ `uses_allocator` -- DECLARED BY THE AUTHOR, NEVER
              DETECTED, and NOTHING MAY DEPEND ON IT BEING RIGHT
              (TASK_PHP_008 §0.4). Two detectors of exactly this fact were
              built and bypassed; the third answer was to stop asking and make
              the `c/emalloc_shim.h` symlink UNCONDITIONAL. This field is for a
              reviewer, and its absence is reported loudly rather than refused.
  ✗ NOT CHECKED  `divergences` (the lift ledger -- `deletions` until
              TASK_PHP_015, when TASK_PHP_014 measured that 3 of ph03's 4
              entries are substitutions or projections rather than
              deletions), `root_cause_ids`, `cwe`, `fix_commit`,
              `invariant`, `obligation`, `echoes` -- all unvalidated
              declarations.

`PLAN_PHP.md` §1 records that six reproducer comments in the source corpus
describe PHP 4.0.2 code that no longer exists at 5.0.0, one of which SAYS SO
IN ITS OWN TEXT and was still believed. That is what the checked half is for.

============================================================================
IT DOES NOT `exec` `extract_cmd`, AND THAT IS DELIBERATE
============================================================================
Running a shell string out of a `spec.md` would be arbitrary code execution
driven by a document, and it would also be a WEAKER check: a command that
extracts the right bytes by some other route would pass while the recorded
coordinates were wrong. So this module

  1. derives the excerpt from the STRUCTURED fields (`c_file`, `c_lines`)
     using Python's own tar reader, and hashes that;
  2. INDEPENDENTLY reconstructs the canonical `extract_cmd` string from those
     same fields and requires the recorded one to match it byte for byte.

(2) is what keeps the human-runnable command honest; (1) is what settles the
bytes. A row can fail either way, and the two failures mean different things:
(1) says the line span is wrong, (2) says the documented command does not
describe the line span.

⚠ `sed -n 'a,bp'` is 1-BASED AND INCLUSIVE, and the slice below is written to
match that exactly, including the case of a file with no final newline.
Verified against real `sed` in `TASK_PHP_002` T5.
"""

import argparse
import glob
import hashlib
import io
import json
import os
import re
import sys
import tarfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATTERNS = os.path.join(REPO, "patterns-php")
MANIFEST = os.path.join(PATTERNS, "php-5.0.0.manifest")

TARBALL_SHA256 = "5783e0c0ba94f165633a565fe73a83e59cf17b6880ef95fa8f936dc6301d6919"
TARBALL_ROOT = "php-5.0.0"
DEFAULT_TARBALL = os.environ.get(
    "PHP500_TARBALL",
    "/home/apt/repos_common/php-in-safe-rust/.app-tests/.temp/oracle/"
    "build-5.0.0/php-5.0.0.tar.gz")

#: ⚠ `check.py::read_contract`'s EXACT spelling, and it must stay exact.
#: The naive `\n``` form failed at TASK_PHP_002 on a `spec.md` whose
#: closing fence had no preceding newline: it ran on to the NEXT fence in
#: the file and reported `Extra data`, while the gate parsed it fine. A
#: validator that disagrees with the gate about where the contract ENDS
#: cannot be trusted about what is IN it.
_FENCE = re.compile(r"```slb-contract\s*\n(.*?)```", re.S)

#: A row that carries no PHP provenance at all -- `ph00-smoke` is the only one
#: this is meant for -- must say so IN TERMS rather than by omitting the block,
#: so that a missing block is always a defect and never a shrug.
NON_PHP_KEY = "php_provenance"

#: ⚠⚠⚠ DECLARED, NEVER DETECTED. TASK_PHP_008 §0.4. The row's author states
#: whether the kernel's numbers were taken under `common-php/emalloc_shim.h`;
#: a reviewer checks it against the kernel. It is DOCUMENTATION -- no digest,
#: no verdict and no audit reads it, and the `c/emalloc_shim.h` symlink is
#: unconditional whatever it says. ⚠ It is deliberately NOT in `REQUIRED`:
#: making it a hard requirement would be one step from making it load-bearing,
#: and two detectors of this exact fact have already been bypassed. A missing
#: one is reported loudly on every run instead.
ALLOC_KEY = "uses_allocator"

REQUIRED = ["php_version", "tarball_sha256", "c_file", "c_lines",
            "extract_cmd", "extract_sha256", "tier"]
TIERS = ("verbatim", "narrowed", "modelled")

#: ⚠⚠⚠ A ROW MAY LIFT MORE THAN ONE SPAN, AND UNTIL `TASK_PHP_018` IT COULD
#: ONLY CITE ONE. `ph07` lifts THREE -- `mbfilter.c:1179-1259` (the walk),
#: `mbfilter_utf8.c:39-56` (the table) and `mbstring.c:1774-1812` (the caller
#: frame, which is where R1h lives) -- and pinned the first. So its overlap
#: report was computed against a span containing **neither the fix nor the
#: frame the fix goes in** (`TASK_PHP_017` M1, `RECAP_PHP.md` open item 25).
#:
#: OPTIONAL, and a list of objects with the SAME four fields as the primary
#: span plus a `why`:
#:
#:     "extra_spans": [
#:       {"c_file": "ext/mbstring/mbstring.c", "c_lines": [1774, 1812],
#:        "extract_cmd": "...", "extract_sha256": "...",
#:        "why": "PHP_FUNCTION(mb_strcut), the caller frame; R1h lands here"}
#:     ]
#:
#: ⚠ **THE PRIMARY FOUR FIELDS DO NOT MOVE.** That is the whole design: a
#: single-span row is byte-identical, so `ph03` and `ph00-smoke` keep their
#: `contract_sha256` and no other row owes a re-gate for this schema change.
#: The alternative -- making `c_lines` a list of lists -- would have forced
#: `extract_cmd` and `extract_sha256` into lists too, moved every row, and
#: still not expressed `ph07`'s real shape, which is three spans in THREE
#: DIFFERENT FILES.
#:
#: Each entry is checked exactly as the primary is: in the manifest, in range,
#: `extract_cmd` canonical for its own `c_file`/`c_lines`, and
#: `extract_sha256` the hash of the bytes `sed` would print. ⚠ The kernel
#: overlap is then computed over the UNION of every cited span, which is the
#: point: it is the only check that asks whether the row's C resembles what it
#: cites, and it was asking about a third of it.
EXTRA_SPANS_KEY = "extra_spans"
_SPAN_FIELDS = ("c_file", "c_lines", "extract_cmd", "extract_sha256")


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def contract(spec_path):
    txt = open(spec_path, encoding="utf-8").read()
    m = _FENCE.search(txt)
    if not m:
        raise ValueError(f"{spec_path}: no ```slb-contract fence")
    return json.loads(m.group(1))


def canonical_cmd(c_file, a, b):
    """The one spelling of the read recipe. `PLAN_PHP.md` §1 and §6."""
    return (f"tar -xzOf <tarball> {TARBALL_ROOT}/{c_file} "
            f"| sed -n '{a},{b}p'")


def excerpt(tarball, c_file, a, b):
    """The bytes `sed -n 'a,bp'` would print. 1-based, inclusive."""
    member = f"{TARBALL_ROOT}/{c_file}"
    with tarfile.open(tarball, "r:gz") as tf:
        try:
            fh = tf.extractfile(member)
        except KeyError:
            raise ValueError(f"{member} is not in the tarball")
        if fh is None:
            raise ValueError(f"{member} is not a regular file")
        data = fh.read()
    # `splitlines(keepends=True)` keeps `\n` and does not invent one for a
    # final line that has none -- which is exactly what sed does.
    lines = io.BytesIO(data).readlines()
    if a < 1 or b < a:
        raise ValueError(f"bad span {a},{b}")
    # ⚠⚠ THIS USED TO `return b""` FOR `a > len(lines)`, WITH THE COMMENT
    # "sed prints nothing; the hash of b'' is a real value and a wrong span
    # lands here often" -- and then did nothing about it. The caller compared
    # `sha256(b"")` against the recorded hash, so a row that transposed a
    # digit or copied a line number out of the wrong file verified GREEN and
    # printed `0 bytes`. A validator whose MOST LIKELY wrong-span case passes
    # is not a must-fire. TASK_PHP_003 M5; negative in
    # `.temp/php4/m5_prov_test.py`.
    if a > len(lines):
        raise ValueError(
            f"span {a},{b} starts past the end of {c_file} ({len(lines)} "
            f"lines). `sed` would print nothing and sha256(b'') is a real "
            f"value -- this is a WRONG SPAN, not an empty file.")
    if b > len(lines):
        raise ValueError(
            f"span {a},{b} runs past the end of {c_file} ({len(lines)} "
            f"lines). `sed` silently stops at EOF; the citation does not.")
    out = b"".join(lines[a - 1:b])
    if not out.strip():
        raise ValueError(f"span {a},{b} of {c_file} is {len(out)} bytes of "
                         f"whitespace -- a citation must name real code")
    return out


# ---------------------------------------------------------------------------
# The kernel half. TASK_PHP_003 M5.2: `PLAN_PHP.md` §6 claimed this module made
# *"this KERNEL came from those lines"* a one-command check, and the module
# never opened the kernel.

#: Row `c/` files that are the extraction. `main.c` is the shared driver's
#: entry point and `emalloc_shim.h` is the allocator symlink -- neither is
#: extracted PHP, and including them would inflate the overlap with code the
#: citation never claimed.
_KERNEL_GLOBS = ("kernel.c", "kernel.h", "kernel_hardened.c", "kernel_*.c")

#: ⚠⚠⚠ REPORTED, NOT ENFORCED, SINCE TASK_PHP_008 §2. These are the fractions
#: a tier is EXPECTED to clear, printed beside the measured number so a reader
#: (and a reviewer) can see the gap. **The validator no longer refuses a row
#: for missing one.**
#:
#: The reason is TASK_PHP_008 §0's reason, one level down. The floor's
#: correctness depends on `_strip_dead_conditionals` recognising every way to
#: write "this block is dead", and TASK_PHP_007 M2 measured **nine more
#: spellings** past the `#if 0` that TASK_PHP_006 fixed -- `#if 0L`, `#if (0)`,
#: `#if 00`, `#if !1`, `#ifdef NEVER_DEFINED`, `#ifndef __STDC__`,
#: `#if defined(NOPE) && defined(NOPE2)`, the undisclosed `#if 1 … #else` and
#: the actively mishandled `#elif 0` -- each scoring **100 %** on a kernel that
#: divides while citing multiplication. A check whose correctness depends on
#: parsing every preprocessor conditional will be reopened by the next one.
#:
#: ⚠ AND `RECAP_PHP.md` OPEN ITEM 14 ALREADY RECORDED WHAT THE CHECK REALLY IS:
#: *it measures presence of TEXT IN A FILE, not presence of CODE IN THE
#: BENCHMARK.* It never reads `main.c`, the driver loop or `build.py`. That is
#: an honest thing to report and a dishonest thing to gate on.
#:
#: ⚠⚠ WHAT IS STILL ENFORCED IS THE EXACT HALF: `c_file` must be in the
#: manifest, the span must be in range, and `extract_sha256` must be the
#: sha256 of those lines of that tarball. Those are not heuristics.
#: ⚠ `#elif 0` IS FIXED ANYWAY (`_strip_dead_conditionals`), because a WRONG
#: number is worse than an unenforced one -- the same reason the false
#: "dead code" note was deleted from `gate.py`.
_OVERLAP_FLOOR = {"verbatim": 0.50, "narrowed": 0.25, "modelled": None}


def _strip_comments(text):
    """Translation phase 3: replace every comment with nothing, keeping lines.

    ⚠⚠ THIS IS HALF OF TASK_PHP_005 F-4's REPAIR, AND IT IS THE HALF F-4 DID
    NOT NAME. `_normalise` used to drop lines that *start with* `/*`, `*` or
    `//`, which is not the same thing as dropping comments: a citation pasted
    inside a block comment whose continuation lines do not begin with `*`

        /*
        result->value.lval = op1->value.lval * op2->value.lval;
        */

    counted in full, exactly as the `#if 0` block did. Measured at
    TASK_PHP_006; it is `selftest_overlap`'s case B2.

    String and character literals are tracked so that `"/*"` in a `printf`
    does not open a comment. Line structure is preserved because the overlap is
    a line-set comparison.
    """
    out = []
    i, n = 0, len(text)
    state = None  # None | 'str' | 'chr' | 'block' | 'line'
    while i < n:
        c = text[i]
        nxt = text[i + 1] if i + 1 < n else ""
        if state is None:
            if c == "/" and nxt == "*":
                state, i = "block", i + 2
                continue
            if c == "/" and nxt == "/":
                state, i = "line", i + 2
                continue
            if c == '"':
                state = "str"
            elif c == "'":
                state = "chr"
            out.append(c)
        elif state in ("str", "chr"):
            out.append(c)
            if c == "\\":
                if nxt:
                    out.append(nxt)
                i += 2
                continue
            if (state == "str" and c == '"') or (state == "chr" and c == "'"):
                state = None
            elif c == "\n":          # unterminated literal; do not swallow the file
                state = None
        elif state == "block":
            if c == "\n":
                out.append("\n")
            elif c == "*" and nxt == "/":
                state, i = None, i + 2
                continue
        elif state == "line":
            if c == "\n":
                out.append("\n")
                state = None
        i += 1
    return "".join(out)


#: A preprocessor conditional whose condition is the literal `0`. ⚠ THAT IS THE
#: ONLY DEAD ARM THIS MODULE CAN SEE, AND THE LIMIT IS STATED RATHER THAN
#: PRETENDED AWAY: `#ifdef NEVER_DEFINED`, `#if SOMETHING_FALSE` and a block
#: excluded by a `-D` on the command line are all still counted. Resolving them
#: needs a real preprocessor, and `gcc -E` cannot be used here because it
#: EXPANDS MACROS and would destroy the line-for-line comparison against the raw
#: tarball excerpt that the whole overlap number is.
_CPP_RX = re.compile(r"^\s*#\s*(if|ifdef|ifndef|elif|else|endif)\b(.*)$")
_LITERAL_FALSE = re.compile(r"^\s*0\s*$")


def _strip_dead_conditionals(text):
    """Delete `#if 0` / `#elif 0` … (`#else` | `#elif` | `#endif`) regions.
    Comments are already gone.

    ⚠⚠ TASK_PHP_005 F-4, THE BLOCKER-SHAPED MAJOR: a kernel that implements
    DIVISION, cites MULTIPLICATION, and pastes the cited lines behind `#if 0`
    scored **100 %** and was ACCEPTED, while the same kernel without the dead
    block was refused at 11 %. `_normalise` dropped lines *starting with* `#`,
    so `#if 0` and `#endif` vanished and everything between them counted.

    ⚠ `#else` is handled rather than ignored: the other arm of a `#if 0` IS
    compiled, so skipping it too would make the check refuse honest rows.

    ⚠⚠ `#elif` WAS A BUG AND NOT A LIMITATION, AND IT IS FIXED HERE
    (TASK_PHP_007 M2, landed TASK_PHP_008 §2). The old code read

        elif kw in ("else", "elif"):
            if skip_at == depth: skip_at = None

    so a `#elif 0` arm -- which is DEAD, unconditionally, whatever the `#if`
    said -- turned skipping OFF and everything under it counted. The function
    believed it handled `elif`; it handled it backwards, and
    `#if 0 … #elif 0 <payload> #endif` scored **100 %**.

    ⚠⚠⚠ AND THE RESIDUAL IS NAMED RATHER THAN ENUMERATED. `#if 0L`, `#if (0)`,
    `#if 00`, `#if !1`, `#ifdef NEVER_DEFINED`, `#ifndef __STDC__`,
    `#if defined(NOPE) && defined(NOPE2)` and `#if 1 … #else <payload> #endif`
    are all still counted, and chasing them is `TASK_PHP_008` §0's mistake one
    level down: a check whose correctness depends on parsing every conditional
    will be reopened by the next one. **So the overlap no longer REFUSES a row
    (TASK_PHP_008 §2) -- it is reported.** What is reported alongside it is
    `unevaluable_conditionals()`, which counts the conditions this function
    could not evaluate, so the reader sees the size of the residual instead of
    being told there is none.
    """
    out, depth, skip_at = [], 0, None
    for line in text.splitlines():
        m = _CPP_RX.match(line)
        if m:
            kw, rest = m.group(1), m.group(2)
            if kw in ("if", "ifdef", "ifndef"):
                depth += 1
                if skip_at is None and kw == "if" and _LITERAL_FALSE.match(rest):
                    skip_at = depth
            elif kw == "elif":
                # A `#elif 0` arm is dead whatever the preceding conditions
                # were; any other `#elif` ENDS a `#if 0` skip at this depth.
                if _LITERAL_FALSE.match(rest):
                    if skip_at is None or skip_at == depth:
                        skip_at = depth
                elif skip_at == depth:
                    skip_at = None
            elif kw == "else":
                if skip_at == depth:
                    skip_at = None
            elif kw == "endif":
                if skip_at == depth:
                    skip_at = None
                depth = max(0, depth - 1)
            out.append("")
            continue
        out.append("" if skip_at is not None else line)
    return "\n".join(out)


def unevaluable_conditionals(text):
    """How many `#if`/`#elif` conditions `_strip_dead_conditionals` could not
    decide, plus every `#ifdef`/`#ifndef`. Returns `(n, [spellings])`.

    ⚠ THIS EXISTS BECAUSE THE ALTERNATIVE IS THE ENUMERATION TREADMILL.
    TASK_PHP_007 M2 listed nine more spellings of "this block is dead" that the
    normaliser counts in full, and TASK_PHP_008 §0's whole lesson is that
    enumerating idioms loses. Rather than add nine predicates and wait for the
    tenth, the tool REPORTS how much of the file it could not evaluate. A
    number the reader can see is worth more than a guarantee that is false.

    ⚠ It is not a check and must never become one: a legitimate `verbatim` lift
    of PHP source is full of `#ifdef`s.
    """
    seen = []
    for line in _strip_comments(text).splitlines():
        m = _CPP_RX.match(line)
        if not m:
            continue
        kw, rest = m.group(1), m.group(2)
        if kw in ("ifdef", "ifndef"):
            seen.append(f"#{kw}{rest[:40]}")
        elif kw in ("if", "elif") and not _LITERAL_FALSE.match(rest):
            seen.append(f"#{kw}{rest[:40]}")
    return len(seen), seen


def _normalise(text):
    """Non-trivial code lines, whitespace-collapsed, for a set comparison.

    Drops comments, `#if 0` regions, blanks, brace-only lines and preprocessor
    lines -- `TSRMLS_*` plumbing and `#include`s are exactly what a `verbatim`
    lift is allowed to remove, so counting them would penalise a correct
    extraction.

    ⚠ THE RESIDUAL, STATED: this measures TEXT IN A FILE. It cannot see
    `#ifdef NEVER`, an unused `static` function sitting beside the one the
    driver calls, or a second kernel source the build never compiles. See
    `kernel_overlap`'s docstring for what a PASS does and does not mean.
    """
    out = set()
    for raw in _strip_dead_conditionals(_strip_comments(text)).splitlines():
        s = " ".join(raw.split())
        if not s or s in ("{", "}", "};", "*/", "/*"):
            continue
        if s.startswith(("/*", "*", "//", "#")):
            continue
        if len(s) < 4:
            continue
        out.add(s)
    return out


def overlap_of(kernel_text, ex_text):
    """(fraction, n_excerpt, n_matched) over already-read text, or (None, 0, 0).

    Split out of `kernel_overlap` so `selftest_overlap` can exercise the
    normaliser with no tarball, no filesystem and no row.
    """
    want = _normalise(ex_text)
    if not want:
        return None, 0, 0
    kern = _normalise(kernel_text)
    hit = len(want & kern)
    return hit / len(want), len(want), hit


def kernel_overlap(pdir, ex_text):
    """(fraction, n_excerpt, n_matched, [files]) or (None, 0, 0, []) if the
    row ships no kernel source.

    ⚠⚠ WHAT A PASS MEANS, AND IT IS LESS THAN IT LOOKS. This function reads the
    row's `c/kernel*.{c,h}` and NOTHING ELSE. It never opens `main.c`, never
    looks at the driver loop, and never consults `harness/build.py`, so
    **a pass is not evidence that the cited lines are COMPILED**, let alone
    that they are what the benchmark measures. A row that keeps the extracted
    function as an unused `static` beside the simplified one the driver
    actually calls scores the same as an honest lift -- `build.py` passes
    `-Wall -Wextra` and not `-Werror`, so `-Wunused-function` does not stop it
    either. TASK_PHP_005 F-4; `RECAP_PHP.md` open item 14.

    ⚠ What it IS evidence for: that the row's kernel source is not a
    re-expression wearing a `verbatim` tier. That is worth having, and it is
    the only claim the number supports.
    """
    cdir = os.path.join(pdir, "c")
    files = []
    for pat in _KERNEL_GLOBS:
        for p in sorted(glob.glob(os.path.join(cdir, pat))):
            if p not in files:
                files.append(p)
    if not files:
        return None, 0, 0, []
    kern_text = "\n".join(
        open(p, encoding="utf-8", errors="replace").read() for p in files)
    frac, nwant, nhit = overlap_of(kern_text, ex_text)
    if frac is None:
        return None, 0, 0, [os.path.basename(f) for f in files]
    return frac, nwant, nhit, [os.path.basename(f) for f in files]


# ---------------------------------------------------------------------------
# The regression test for the two dead-code bypasses. TASK_PHP_005 F-4 built
# cases A/B/C against the live tarball; these are the same cases with the
# excerpt EMBEDDED, so the self-test runs on a box with no tarball -- which is
# the box `--no-tarball` exists for, and the box a re-gate has to work on.
#
# ⚠⚠ D AND E ARE THE MUST-NOT-FIRE HALF AND THEY ARE THE POINT. Without them a
# `_normalise` that returned the EMPTY SET would satisfy every "must score
# under the floor" case and the self-test would go green on a normaliser that
# had stopped measuring anything. `.tasks/PROTOCOL.md` rule 1: before believing
# a check, ask what would make it FAIL.

#: `php-5.0.0/Zend/zend_operators.c:821-850` -- `mul_function`, the TYPE axis's
#: own leading candidate and the call site of the macro `PROTOCOL_PHP.md` §B is
#: about. Embedded verbatim (tabs included).
_SELFTEST_EXCERPT = (
    'ZEND_API int mul_function(zval *result, zval *op1, zval *op2 TSRMLS_DC)\n'
    '{\n'
    '\tzval op1_copy, op2_copy;\n'
    '\t\n'
    '\tzendi_convert_scalar_to_number(op1, op1_copy, result);\n'
    '\tzendi_convert_scalar_to_number(op2, op2_copy, result);\n'
    '\n'
    '\tif (op1->type == IS_LONG && op2->type == IS_LONG) {\n'
    '\t\tlong overflow;\n'
    '\n'
    '\t\tZEND_SIGNED_MULTIPLY_LONG(op1->value.lval,op2->value.lval, '
    'result->value.lval,result->value.dval,overflow);\n'
    '\t\tresult->type = overflow ? IS_DOUBLE : IS_LONG;\t\n'
    '\t\treturn SUCCESS;\n'
    '\t}\n'
    '\tif ((op1->type == IS_DOUBLE && op2->type == IS_LONG)\n'
    '\t\t|| (op1->type == IS_LONG && op2->type == IS_DOUBLE)) {\n'
    '\t\tresult->value.dval = (op1->type == IS_LONG ?\n'
    '\t\t\t\t\t\t (((double) op1->value.lval) * op2->value.dval) :\n'
    '\t\t\t\t\t\t (op1->value.dval * ((double) op2->value.lval)));\n'
    '\t\tresult->type = IS_DOUBLE;\n'
    '\t\treturn SUCCESS;\n'
    '\t}\n'
    '\tif (op1->type == IS_DOUBLE && op2->type == IS_DOUBLE) {\n'
    '\t\tresult->type = IS_DOUBLE;\n'
    '\t\tresult->value.dval = op1->value.dval * op2->value.dval;\n'
    '\t\treturn SUCCESS;\n'
    '\t}\n'
    '\tzend_error(E_ERROR, "Unsupported operand types");\n'
    '\treturn FAILURE;\t\t\t\t/* unknown datatype */\n'
    '}\n')

#: What a row that extracts `mul_function` HAS to change, and every one is
#: forced rather than stylistic: `ZEND_API`/`TSRMLS_DC` are Zend build plumbing,
#: `zendi_convert_scalar_to_number` drags in the whole zval conversion tree, and
#: `zend_error(E_ERROR, …)` is the engine's error path. TASK_PHP_005's clean
#: negative 7 -- the floor is not too HIGH -- lives or dies on this case.
_SELFTEST_KERNEL_A = (
    '#include "kernel.h"\n'
    '/* Extracted from php-5.0.0 Zend/zend_operators.c:821-850, tier verbatim. */\n'
    'int mul_function(zval *result, zval *op1, zval *op2)\n'
    '{\n'
    '\tif (op1->type == IS_LONG && op2->type == IS_LONG) {\n'
    '\t\tlong overflow;\n'
    '\n'
    '\t\tPHP_SHIM_SIGNED_MULTIPLY_LONG(op1->value.lval,op2->value.lval, '
    'result->value.lval,result->value.dval,overflow);\n'
    '\t\tresult->type = overflow ? IS_DOUBLE : IS_LONG;\n'
    '\t\treturn SUCCESS;\n'
    '\t}\n'
    '\tif ((op1->type == IS_DOUBLE && op2->type == IS_LONG)\n'
    '\t\t|| (op1->type == IS_LONG && op2->type == IS_DOUBLE)) {\n'
    '\t\tresult->value.dval = (op1->type == IS_LONG ?\n'
    '\t\t\t\t\t\t (((double) op1->value.lval) * op2->value.dval) :\n'
    '\t\t\t\t\t\t (op1->value.dval * ((double) op2->value.lval)));\n'
    '\t\tresult->type = IS_DOUBLE;\n'
    '\t\treturn SUCCESS;\n'
    '\t}\n'
    '\tif (op1->type == IS_DOUBLE && op2->type == IS_DOUBLE) {\n'
    '\t\tresult->type = IS_DOUBLE;\n'
    '\t\tresult->value.dval = op1->value.dval * op2->value.dval;\n'
    '\t\treturn SUCCESS;\n'
    '\t}\n'
    '\treturn FAILURE;\t\t\t\t/* unknown datatype */\n'
    '}\n')

#: The WRONG kernel: it divides. Everything after it is the payload.
_SELFTEST_WRONG = (
    '#include "kernel.h"\n'
    '/* This kernel implements DIVISION. It cites multiplication. */\n'
    'int div_kernel(zval *result, zval *op1, zval *op2)\n'
    '{\n'
    '\tresult->value.dval = op1->value.dval / op2->value.dval;\n'
    '\tresult->type = IS_DOUBLE;\n'
    '\treturn SUCCESS;\n'
    '}\n')

_FLOOR = 0.50   # `_OVERLAP_FLOOR["verbatim"]`, spelled out so a floor change
                # cannot silently retune the regression test.

OVERLAP_CASES = [
    ("A verbatim lift, plausible", _SELFTEST_KERNEL_A, _FLOOR, 1.01,
     "TASK_PHP_005 clean negative 7: the floor must NOT be too high. If this "
     "drops under the floor, a correct `verbatim` row is being refused."),
    ("B wrong kernel + `#if 0`", _SELFTEST_WRONG
     + "\n#if 0   /* never compiled */\n" + _SELFTEST_EXCERPT + "\n#endif\n",
     0.0, _FLOOR,
     "TASK_PHP_005 F-4: this scored 100% and was ACCEPTED."),
    ("B2 wrong kernel + block comment", _SELFTEST_WRONG
     + "\n/*\n" + _SELFTEST_EXCERPT + "\n*/\n", 0.0, _FLOOR,
     "TASK_PHP_006: the same bypass spelled with a comment whose continuation "
     "lines do not start with `*`."),
    ("B3 wrong kernel + nested `#if 0`", _SELFTEST_WRONG
     + "\n#if 0\n#if 1\n" + _SELFTEST_EXCERPT + "\n#endif\n#endif\n",
     0.0, _FLOOR,
     "a nested LIVE conditional inside a dead one is still dead."),
    ("B4 wrong kernel + `#elif 0`", _SELFTEST_WRONG
     + "\n#if 0\nint dead(void){return 0;}\n#elif 0\n" + _SELFTEST_EXCERPT
     + "\n#endif\n", 0.0, _FLOOR,
     "TASK_PHP_007 M2: `#elif` was handled BACKWARDS -- a `#elif 0` arm is "
     "DEAD and the code turned skipping OFF for it, so this scored 100%. "
     "Fixed at TASK_PHP_008 §2."),
    ("C control: wrong kernel, no dead code", _SELFTEST_WRONG, 0.0, _FLOOR,
     "the must-fire control. If this passes the floor, the floor measures "
     "nothing and B/B2/B3/B4 prove nothing."),
    ("D the excerpt itself", _SELFTEST_EXCERPT, 0.99, 1.01,
     "⚠ THE MUST-NOT-FIRE. A `_normalise` that returned the empty set would "
     "satisfy B, B2, B3 and C vacuously. This is what stops the self-test "
     "going green on a normaliser that stopped measuring."),
    ("E `#if 0` / `#else` -- the LIVE arm", _SELFTEST_WRONG
     + "\n#if 0\nint dead(void){return 0;}\n#else\n" + _SELFTEST_EXCERPT
     + "\n#endif\n", 0.99, 1.01,
     "⚠ the second must-not-fire: the other arm of a `#if 0` IS compiled, so "
     "stripping it too would refuse honest rows."),
    ("E2 `#if 0` / `#elif COND` -- the possibly-live arm", _SELFTEST_WRONG
     + "\n#if 0\nint dead(void){return 0;}\n#elif defined(PH_X)\n"
     + _SELFTEST_EXCERPT + "\n#endif\n", 0.99, 1.01,
     "⚠ THE THIRD MUST-NOT-FIRE, AND IT IS B4's GUARD. A non-literal `#elif` "
     "arm CAN be compiled, so the `#elif 0` fix must not start skipping every "
     "`#elif`. Without this case, `elif -> always skip` would satisfy B4."),
]


def selftest_overlap():
    """Run `OVERLAP_CASES`. Returns a list of failure strings; empty is pass.

    ⚠ No tarball, no filesystem, no compiler -- pure string work, ~1 ms, which
    is why `harness-php/gate.py`'s preflight runs it on every invocation.
    """
    bad = []
    for name, kernel, lo, hi, why in OVERLAP_CASES:
        frac, nwant, nhit = overlap_of(kernel, _SELFTEST_EXCERPT)
        if frac is None:
            bad.append(f"{name}: the excerpt normalised to NOTHING -- "
                       f"`_normalise` is broken, not the case. {why}")
            continue
        if not (lo <= frac < hi):
            bad.append(f"{name}: overlap {frac:.0%} ({nhit}/{nwant}), wanted "
                       f"{lo:.0%} <= x < {hi:.0%}. {why}")
    return bad


def manifest_map():
    if not os.path.exists(MANIFEST):
        return {}
    out = {}
    for line in open(MANIFEST, encoding="utf-8"):
        if line.startswith("#"):
            continue
        sha, _, path = line.rstrip("\n").partition("  ")
        if path:
            out[path] = sha
    return out


def check_row(pdir, tarball, use_tarball=True, show=False):
    """Returns (ok, [messages])."""
    msgs = []
    spec = os.path.join(pdir, "spec.md")
    row = os.path.basename(pdir)
    if not os.path.exists(spec):
        return False, [f"{row}: no spec.md"]
    try:
        c = contract(spec)
    except (ValueError, json.JSONDecodeError) as e:
        return False, [f"{row}: {e}"]
    prov = c.get("provenance")
    if prov is None:
        return False, [f"{row}: the slb-contract block has NO `provenance` "
                       f"object. Every php row carries one (PLAN_PHP.md §6); "
                       f"a row with no PHP source says so with "
                       f'"{NON_PHP_KEY}": false and a `why`.']

    # ⚠⚠ `uses_allocator` IS DECLARED, NEVER DETECTED (TASK_PHP_008 §0.4).
    # Two detectors of the same fact were bypassed (TASK_PHP_005 F-1,
    # TASK_PHP_007 B1/B2), so the audit stopped asking and the SYMLINK became
    # unconditional. This field is what a reviewer reads to know whether the
    # row's numbers were taken under the shim. ⚠⚠⚠ NOTHING DEPENDS ON IT BEING
    # RIGHT -- not the digests, not the preflight, not a single verdict. If it
    # ever acquires a consumer, it has become a third detector and this comment
    # is the warning.
    uses_alloc = prov.get(ALLOC_KEY)
    if uses_alloc is not None:
        msgs.append(f"{row}: uses_allocator={uses_alloc!r} -- ⚠ DECLARED BY "
                    f"THE AUTHOR, NEVER DETECTED, and nothing depends on it "
                    f"being right. A reviewer checks it against the kernel; "
                    f"the `c/emalloc_shim.h` symlink is unconditional either "
                    f"way (TASK_PHP_008 §0).")

    if prov.get(NON_PHP_KEY) is False:
        if not prov.get("why"):
            return False, [f"{row}: declares {NON_PHP_KEY}=false with no "
                           f"`why`. Say what it is instead, so nobody ever "
                           f"mistakes it for a php row."]
        msgs.append(f"{row}: NOT A PHP ROW -- {NON_PHP_KEY}=false. "
                    f"why: {prov['why'][:90]}")
        if uses_alloc is None:
            msgs.append(f"{row}: ⚠ no `uses_allocator` declared. Add it "
                        f"(PLAN_PHP.md §6, TASK_PHP_008 §0.4) -- a row with no "
                        f"PHP source still either allocates or does not.")
        return True, msgs

    missing = [k for k in REQUIRED if k not in prov]
    if missing:
        return False, [f"{row}: provenance is missing {missing}"]
    if prov["tarball_sha256"] != TARBALL_SHA256:
        return False, [f"{row}: tarball_sha256 {prov['tarball_sha256'][:12]} "
                       f"is not the pinned corpus {TARBALL_SHA256[:12]} "
                       f"(patterns-php/SOURCES.md)"]
    if prov["tier"] not in TIERS:
        return False, [f"{row}: tier {prov['tier']!r} not in {TIERS}"]
    # (1) EVERY cited span -- the primary one, then any `extra_spans`. The
    # primary is `spans[0]` and its four keys are read from the top level, so a
    # single-span row is byte-identical to what it was before TASK_PHP_018.
    spans = [{k: prov[k] for k in _SPAN_FIELDS}]
    spans[0]["why"] = "the primary span"
    extra = prov.get(EXTRA_SPANS_KEY, [])
    if not isinstance(extra, list):
        return False, [f"{row}: {EXTRA_SPANS_KEY} must be a list of span "
                       f"objects, got {type(extra).__name__}"]
    for i, sp in enumerate(extra):
        if not isinstance(sp, dict):
            return False, [f"{row}: {EXTRA_SPANS_KEY}[{i}] is not an object"]
        miss = [k for k in _SPAN_FIELDS if k not in sp]
        if miss:
            return False, [f"{row}: {EXTRA_SPANS_KEY}[{i}] is missing {miss}"]
        if not sp.get("why"):
            return False, [f"{row}: {EXTRA_SPANS_KEY}[{i}] has no `why`. A "
                           f"second span is a second claim; say what it is."]
        spans.append(sp)

    for i, sp in enumerate(spans):
        lines = sp["c_lines"]
        if not (isinstance(lines, list) and len(lines) == 2
                and all(isinstance(x, int) for x in lines)):
            return False, [f"{row}: span {i} c_lines must be [a, b] integers, "
                           f"got {lines!r}"]
        # (2) the recorded command must be the canonical spelling of the fields
        want = canonical_cmd(sp["c_file"], lines[0], lines[1])
        if sp["extract_cmd"] != want:
            return False, [f"{row}: span {i} extract_cmd does not describe "
                           f"c_file/c_lines\n"
                           f"       recorded: {sp['extract_cmd']}\n"
                           f"       canonical: {want}"]
    a, b = spans[0]["c_lines"]
    want_cmd = spans[0]["extract_cmd"]

    # the manifest half -- works with no tarball at all
    mm = manifest_map()
    if mm:
        for i, sp in enumerate(spans):
            if sp["c_file"] not in mm:
                return False, [f"{row}: span {i}: {sp['c_file']} is not in "
                               f"patterns-php/php-5.0.0.manifest"]
        msgs.append(f"{row}: {', '.join(sp['c_file'] for sp in spans)} "
                    f"{'is' if len(spans) == 1 else 'are'} in the manifest "
                    f"({', '.join(mm[sp['c_file']][:12] for sp in spans)})")
    else:
        msgs.append(f"{row}: ⚠ no manifest at {MANIFEST}; file-level check skipped")

    if not use_tarball:
        msgs.append(f"{row}: ⚠ --no-tarball: extract_sha256 was NOT verified "
                    f"for any of {len(spans)} span(s). This is a PARTIAL check.")
        return True, msgs

    if not os.path.exists(tarball):
        return False, [f"{row}: tarball not found at {tarball}. Set "
                       f"PHP500_TARBALL, or use --no-tarball and say in the "
                       f"report that the excerpt hash went unchecked."]
    got_tar = hashlib.sha256(open(tarball, "rb").read()).hexdigest()
    if got_tar != TARBALL_SHA256:
        return False, [f"{row}: the tarball at {tarball} hashes "
                       f"{got_tar[:12]}, not {TARBALL_SHA256[:12]}"]
    texts = []
    for i, sp in enumerate(spans):
        sa, sb = sp["c_lines"]
        try:
            ex = excerpt(tarball, sp["c_file"], sa, sb)
        except ValueError as e:
            return False, [f"{row}: span {i}: {e}"]
        got = sha256_bytes(ex)
        if show:
            sys.stdout.write(ex.decode("utf-8", "replace"))
        if got != sp["extract_sha256"]:
            return False, [f"{row}: EXTRACT MISMATCH for span {i}, "
                           f"{sp['c_file']}:{sa}-{sb}\n"
                           f"       recorded  {sp['extract_sha256']}\n"
                           f"       actual    {got}   ({len(ex)} bytes, "
                           f"{ex.count(chr(10).encode())} newlines)\n"
                           f"       run: {sp['extract_cmd']} | sha256sum"]
        texts.append(ex.decode("utf-8", "replace"))
        tag = "OK " if i == 0 else f"OK+{i}"
        msgs.append(f"{row}: {tag} {sp['c_file']}:{sa}-{sb}  {len(ex)} bytes  "
                    f"sha256 {got[:16]}"
                    + (f"  tier={prov['tier']}" if i == 0
                       else f"  -- {sp['why'][:70]}"))
    ex = texts[0]

    # the kernel half -- does the row's C actually look like what it cites?
    # ⚠⚠ OVER THE UNION OF EVERY CITED SPAN SINCE TASK_PHP_018. `ph07` lifted
    # three and pinned one, so this number was computed against a span
    # containing neither its fix nor the frame the fix goes in. A row that
    # cites more now has MORE to resemble, which is the direction this check
    # should err in: adding a span cannot make the number go up for free.
    if len(spans) > 1:
        per = []
        for i, t in enumerate(texts):
            f_i, w_i, h_i, _ = kernel_overlap(pdir, t)
            per.append(f"span{i} {f_i:.0%} ({h_i}/{w_i})"
                       if f_i is not None else f"span{i} n/a")
        msgs.append(f"{row}: per-span overlap: " + ", ".join(per)
                    + f"  -- the UNION is what is reported below, and it is "
                      f"what {len(spans)} cited spans oblige the row to")
    frac, nwant, nhit, kfiles = kernel_overlap(pdir, "\n".join(texts))
    if frac is None:
        if not kfiles:
            return False, msgs + [
                f"{row}: declares PHP provenance and ships NO kernel source "
                f"({', '.join(_KERNEL_GLOBS)} under c/). The citation names "
                f"lines that produced nothing."]
        msgs.append(f"{row}: ⚠ excerpt has no non-trivial code lines; kernel "
                    f"overlap not computed")
        return True, msgs
    expect = _OVERLAP_FLOOR.get(prov["tier"])
    nuc, spellings = unevaluable_conditionals(
        "\n".join(open(os.path.join(pdir, "c", f), encoding="utf-8",
                       errors="replace").read() for f in kfiles))
    msgs.append(f"{row}: kernel overlap {frac:.0%} ({nhit}/{nwant} excerpt "
                f"lines in {', '.join(kfiles)})"
                + (f"  tier={prov['tier']} is expected to clear {expect:.0%} "
                   f"-- REPORTED, NOT ENFORCED (TASK_PHP_008 §2)"
                   if expect is not None
                   else f"  (tier={prov['tier']}: reported, no expectation)"))
    if expect is not None and frac < expect:
        msgs.append(
            f"{row}: ⚠⚠ THE OVERLAP IS BELOW WHAT tier={prov['tier']} LEADS A "
            f"READER TO EXPECT ({frac:.0%} < {expect:.0%}). This is REPORTED "
            f"and does not refuse the row. Either the citation is wrong, or "
            f"the tier is (`modelled` is the honest answer for a re-expressed "
            f"mechanism), or the heuristic is wrong about this row -- say "
            f"which in NOTES.md, because a reviewer will ask.")
    msgs.append(f"{row}: ⚠ the overlap measures TEXT IN {', '.join(kfiles)}, "
                f"not code in the benchmark -- it never reads main.c, the "
                f"driver loop or the build, so a HIGH NUMBER is not evidence "
                f"that the cited lines are COMPILED (TASK_PHP_005 F-4), and a "
                f"LOW one is not a refusal (TASK_PHP_008 §2).")
    msgs.append(f"{row}: ⚠ {nuc} preprocessor condition(s) in the kernel this "
                f"heuristic CANNOT evaluate"
                + (f": {spellings[:4]}" if spellings else "")
                + f". Anything inside a dead one of those is counted as live "
                  f"(TASK_PHP_007 M2 measured nine such spellings). This is "
                  f"the size of the residual, not a defect.")
    if uses_alloc is None:
        msgs.append(f"{row}: ⚠ no `uses_allocator` declared. Add it (true or "
                    f"false, with a reason if false) -- PLAN_PHP.md §6, "
                    f"TASK_PHP_008 §0.4. DECLARED, NEVER DETECTED.")
    return True, msgs


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("row", nargs="?", help="row id or dir name, e.g. ph07")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--show", action="store_true", help="print the excerpt")
    ap.add_argument("--no-tarball", action="store_true",
                    help="manifest-only; does NOT verify extract_sha256")
    ap.add_argument("--selftest", action="store_true",
                    help="run the kernel-overlap regression cases and stop "
                         "(no tarball, no row needed)")
    ap.add_argument("--tarball", default=DEFAULT_TARBALL)
    a = ap.parse_args()

    if a.selftest:
        bad = selftest_overlap()
        for name, kernel, lo, hi, _why in OVERLAP_CASES:
            frac, nwant, nhit = overlap_of(kernel, _SELFTEST_EXCERPT)
            mark = "FAIL" if any(b.startswith(name) for b in bad) else "ok  "
            got = "n/a" if frac is None else f"{frac:.0%}"
            print(f"  {mark}  {name:38s} overlap {got:>4s} "
                  f"({nhit}/{nwant})  want {lo:.0%} <= x < {hi:.0%}")
        for b in bad:
            print(f"  BAD  {b}")
        print(f"\n{len(OVERLAP_CASES)} overlap case(s), {len(bad)} FAILED")
        return 1 if bad else 0

    if a.all:
        dirs = sorted(d for d in glob.glob(os.path.join(PATTERNS, "ph*"))
                      if os.path.isdir(d))
    elif a.row:
        hits = sorted(d for d in glob.glob(os.path.join(PATTERNS, a.row + "*"))
                      if os.path.isdir(d))
        if len(hits) != 1:
            print(f"provenance.py: {a.row!r} matches {hits or 'nothing'}")
            return 1
        dirs = hits
    else:
        ap.error("give a row id or --all")

    if not dirs:
        print("provenance.py: no rows under patterns-php/")
        return 1
    bad = 0
    for d in dirs:
        ok, msgs = check_row(d, a.tarball, not a.no_tarball, a.show)
        for m in msgs:
            print(("  " if ok else "  BAD  ") + m)
        if not ok:
            bad += 1
    print(f"\n{len(dirs)} row(s) checked, {bad} FAILED")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
