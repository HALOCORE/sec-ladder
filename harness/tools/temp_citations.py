#!/usr/bin/env python3
"""Do the `.temp/` paths that COMMITTED files cite still resolve on this box?

    python3 harness/tools/temp_citations.py             # the check; exit 1 on a NEW one
    python3 harness/tools/temp_citations.py --list      # the baseline, by kind, with notes
    python3 harness/tools/temp_citations.py --census    # the size-bound figures
    python3 harness/tools/temp_citations.py --update    # re-skeleton the baseline
    python3 harness/tools/temp_citations.py --include-tasks

`CLAUDE.md` rule 1 puts every agent's evidence under gitignored `.temp/`, and
`.memory/00-environment.md` constraint 6 then says to DELETE the re-derivable
half of it. Both are deliberate. The gap they leave is that a committed file may
name a `.temp/` path, and **nothing notices when that path goes away** -- the
loss needs an `rm`, not a clone. TASK_121 §B measured the exposure and
recommended *promote, don't publish*; this is the instrument that makes the
convention checkable instead of discovered.

⚠⚠ **THIS IS A STATEMENT ABOUT THIS BOX, NOT ABOUT A CLONE.** `.temp/` is
gitignored, so in a fresh clone every one of the ~1450 citations dangles and this
tool's output is meaningless. It answers *"has the evidence behind the committed
prose been deleted HERE, since it was written?"* -- which is the question the
project actually lost work to.

⚠ **AND IT IS BLIND TO THE FAILURE THAT MOTIVATED IT** (TASK_125, measured).
TASK_122 could not raise an 18.9 M `Ir` drift from sufficiency to actuality
because `.temp/t86/cost.rs` is **unversioned**, not because it is absent -- the
file is still on disk today and this checker resolves it and says nothing. An
existence check catches the cheap failure. The expensive one (present, mutated,
no record of what it used to be) needs a CONTENT pin, which is what promotion
into the tree buys for free.

## Why `harness/tools/` and not `harness/`

`check.py`'s gate digest globs `harness/*.py` into every pattern's
`source_sha256` (see its `srcs` list). That glob is **non-recursive**, exactly as
`common/*.py` is non-recursive and does not reach `common/layout/`. So a file
here is next to the gate and is not IN it, and that is the point:

  * this tool decides no pattern's verdict, so putting it in the digest would
    assert something false;
  * a comment fix in a file under `harness/*.py` costs a **26-pattern gate
    sweep** (~1 hour). A documentation-hygiene tool whose own upkeep costs an
    hour is a tool nobody will keep up. The project already has this pathology
    named for rung sources ("THERE IS NO CHEAP DOC FIX IN ANY RUNG SOURCE",
    `PROTOCOL.md` definition-of-done rule 6); there is no reason to build a
    second one on purpose.

⚠ **Nothing in `harness/tools/` may ever be imported by `check.py`,
`measure.py` or `build.py`** -- if it were, the digest would silently stop
covering a file that decides a verdict. That is the cost of this placement and
it is the only one.

## What counts as a citation, and the three things that are NOT one

Measured over the tree at TASK_125 (`.temp/t125/dangling_context.txt`): a naive
"path in a committed file that does not exist" check is ~85 hits and **most of
them are not defects**. Three classes, all handled here or in the baseline:

  1. **Glob stems** -- `\\.temp/[\\w./+-]*` truncates `.temp/p03/kir-band-*.json`
     at the `*` to a stem that can never exist. Handled HERE: `resolve()`
     consumes the metacharacters, rewrites `{a,b}` / `<pid>` / `$VAR` / `?` to
     `*`, and globs. ⚠ This deliberately WEAKENS the check -- one surviving file
     satisfies a whole glob -- and it is still right, because the alternative
     reports a stem that was never a path.
  2. **Output destinations** -- `mkdir -p .temp/pNN/…`, `BIN="$REPO/.temp/pNN/ctlbin"`,
     `--out .temp/pNN/sweep.json` (`TOOLCHAIN.md`, and every pattern's
     `controls/build_controls.sh` and `controls/sweep_ir.py`). The citing script
     CREATES the path when it runs; it is not a reference to evidence. Not
     auto-detectable without a heuristic that would silence real citations, so
     it goes in the baseline with `kind: destination`.
  3. **Negative citations** -- `patterns/p07-binary-search/NOTES.md` cites a
     twin-source path and says in the same sentence that it *"never existed"*;
     the four `patterns/*/controls/clayout.py` comments each cite p14's scratch
     directory to warn *"⚠ This said … -- p14's OWN scratch directory"*. The
     sentence asserts the path is WRONG. "Fixing" it deletes the warning.
     Baseline, `kind: negative`.

And the largest single class, `kind: regenerable`, is **constraint 6 working**:
`.temp/p05/cvar/kernel_intcheck.c` is still there while the four binaries
`p05/NOTES.md` runs in its transcript are not, which is precisely *keep the
generator, delete the artefact*. A dangling binary whose source survives is
compliance, not rot.

⚠ This docstring deliberately cites **no path that does not resolve**, because a
checker that has to baseline its own prose is a checker nobody will believe. The
generic `pNN` spellings above are skipped by `PLACEHOLDER`; the concrete cases
are named by their CITING FILE, which is the thing that will still be there.

## The baseline is a FILE, and that is a decision, not an accident

`temp_citations_baseline.json`, beside this file. A **count** would have been
smaller, and this project has watched a cached count rot three times
(`PROTOCOL.md` rule 13). A file is diffable, carries a `kind` and a `note` per
entry -- so the *"say what it showed"* half of the policy lives somewhere -- and
lets the check key on `(citing file, path)` pairs, so a NEW file citing an
ALREADY-dead path is still a new defect. `--update` writes the skeleton but
leaves `kind` empty and the check FAILS on an empty `kind`: you cannot bless a
new entry without saying what it is.

## The SECOND check in this file: `<harness module>.py:NNNN` line citations

`python3 harness/tools/temp_citations.py --lines` (and it runs by default).

`.memory/02-bench-rules.md`, *"Line citations into `check.py` decay. Cite the
FUNCTION"*: **name the FUNCTION and give NO LINE NUMBER AT ALL**, because a
function name cannot rot silently -- rename it and `grep` returns nothing, which
is a loud failure.

⚠⚠ **`check.py`'s stage `0c` enforces that over `check.py` ∩ `patterns/` -- ONE
of THIRTEEN harness modules and ONE of SIX committed directories that carry the
citation.** TASK_169 measured the rest and TASK_170 landed this: outside that
intersection the tree carried **7 in `RECAP.md`** (the file `CLAUDE.md` says to
read first, ≥4 rotten), **6 in `.memory/`**, **1 in a PUBLISHED
`results/synthesis.md`** emitted by `synthesis/synthesize.py`, and 13
non-`check.py` citations under `patterns/`. **The published one is the argument
for this check**: `.memory/03-measurement.md` recorded that exact coordinate as
rotted and repaired it *in its own copy of the sentence*, while the GENERATOR
kept re-emitting the other copy into a published artefact on every run --
`PROTOCOL` rule 6's artefact-vs-generator skew, on the citation-rot class itself.

**Why here and not in `0c`.** Two reasons, and the second is the deciding one:

  1. A **per-pattern** stage is the wrong instrument for a **repo-wide**
     convention. `0c` runs 33 times; scanning `RECAP.md` from it would report the
     same failures 33 times and couple every pattern's verdict to manager-owned
     files nobody edits during a build.
  2. ⚠⚠ **`0c`'s `line_citations` has, deliberately, NO ESCAPE HATCH -- and a
     tree-wide scan needs one.** Its documented workaround (*"spell it without
     the colon"*) DESTROYS the evidence in the cases that matter, because the
     sentence's whole subject IS the coordinate.

## ⚠ SO: WHAT AN ESCAPE HATCH LOOKS LIKE, AND WHY IT IS A BASELINE FILE

**It is the same baseline file, a second array, and four kinds** -- not an inline
`# noqa`-style marker. An inline marker would sit in `.memory/` and `RECAP.md`
prose as noise, and worse, it would be invisible to a reader deciding whether a
citation is still true. A classified baseline entry is diffable, carries the
reason, and `--list-lines` prints **the text the cited line holds today** beside
it, which is `.memory/02-bench-rules.md`'s own eyeball aid made mechanical.

  * `quotation` -- the sentence's SUBJECT is the coordinate: it quotes a rotted
    citation as evidence (`.memory/06-catalogue.md`'s *"`check.py:1249` is not
    the checksum rule"*). Spelling it without the colon deletes the finding.
  * `fixture` -- a literal inside a checker's own must-fire arm
    (`check.py`'s `_CITE_VERDICT_CASES`). The string is test DATA.
  * `generated-record` -- the citation sits inside a GENERATED artefact
    (`results/gate/*.json` re-emitting stage `0c`'s own report). **Fix the
    generator or the file it read, never the artefact** -- that is exactly the
    skew this check exists to catch, so the `note` must name the fix site.
  * `owed` -- a real citation that should be re-cited by function, whose repair
    is PRICED ELSEWHERE (the 13 under `patterns/` sit in `model.py` /
    `inputs/gen.py`, which are MEASUREMENT-hashed, so fixing them costs a
    re-measure). The `note` must name the target function and the cost.

**A kind is mandatory: `--update` writes the skeleton with an empty `kind` and
the check FAILS on an empty one.** So the hatch cannot be used silently, and a
NEW citation from a NEW file fails even if the same coordinate is already blessed
somewhere else.

⚠ **What this check does NOT do: decide whether a citation is still TRUE.**
Nothing can know what a citation meant. It prints the current line for a human --
same limit `.memory/02-bench-rules.md` states for its own aid.
"""
import argparse
import collections
import glob as globmod
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
BASELINE = os.path.join(HERE, "temp_citations_baseline.json")

#: Consumes shell metacharacters so a glob citation stays whole; see `resolve`.
#: `{a,b}` and `<pid>` are matched AS UNITS so that the comma inside a brace does
#: not end the path while a bare comma between two paths still does -- p10's
#: README cites `--json a.json,b.json,c.json` on one line.
PAT = re.compile(r"\.temp/[A-Za-z0-9_](?:\{[^}\s]*\}|<[^>\s]*>"
                 r"|[A-Za-z0-9_./+*?$\[\]-])*")
META = re.compile(r"[*?{}<>$\[\]]")

#: ⚠⚠ DEFECT 1, FIXED AT TASK_132. `PAT` above matches `.temp/` ANYWHERE in a
#: line, and `resolve` then joins the hit to THIS repo -- so an absolute path
#: into ANOTHER project's `.temp/` (the C corpora live in two of them) was
#: reported as a dangling citation of a path this repo never had. This
#: expression eats the path characters to the LEFT of the hit so the caller can
#: see whether the citation is absolute and, if it is, whose it is.
LEFT = re.compile(r"[A-Za-z0-9_./+-]*$")


def owner(line, start):
    """`"self"`, or the foreign root the `.temp/` at `line[start]` belongs to.

    A hit is FOREIGN when the path characters to its left form an ABSOLUTE path
    that is not under this repo. Anything else -- a bare backticked
    `.temp/<dir>`, a relative `sec-ladder/.temp/<dir>`, a hit after a backtick
    or a space -- is this repo's, which is the conservative direction: a false
    "self" is a citation that gets checked, a false "foreign" is a citation that
    stops being. Must-fire arm: `--selftest`."""
    pre = LEFT.search(line[:start]).group(0)
    if not pre.startswith("/"):
        return "self"
    if (pre + ".temp").startswith(REPO + "/"):
        return "self"
    return pre.rstrip("/") or "/"


#: ⚠⚠ DEFECT 2, FIXED AT TASK_132. A committed *Python* file that ASSEMBLES a
#: path with `os.path.join(REPO, ".temp", ...)` carries no literal `.temp/`, so
#: `PAT` could not see it and the checker silently covered less than it claimed.
#: `TASK_127` found it by ordinary use and reported it unfixed (the example is
#: `harness/tools/table_render_inputs.py`'s own `SCRATCH`). This matches a
#: `join` whose argument list contains a `".temp"` literal and reconstructs the
#: path from the string literals that follow it, stopping at the first
#: non-literal (a variable makes the rest unknowable, and half a path is not a
#: citation).
JOINED = re.compile(r"""(?:os\.path\.)?join\(([^()]*)\)""")
_STRLIT = re.compile(r"""['"]([^'"]*)['"]""")


def joined_paths(line):
    """`.temp/...` paths a Python source line BUILDS rather than spells."""
    out = []
    for m in JOINED.finditer(line):
        parts = [a.strip() for a in m.group(1).split(",")]
        try:
            i = next(k for k, a in enumerate(parts)
                     if _STRLIT.fullmatch(a) and _STRLIT.fullmatch(a).group(1) == ".temp")
        except StopIteration:
            continue
        comps = [".temp"]
        for a in parts[i + 1:]:
            lit = _STRLIT.fullmatch(a)
            if not lit:
                break
            comps.append(lit.group(1))
        if len(comps) > 1:
            out.append("/".join(comps))
    return out

#: Narrow and explicit, because the manager's first count called two of these
#: "missing" and they are template text. A component that IS or ENDS IN a run of
#: capital `N`s is a stand-in, not a path: `.temp/pNN/`, `.temp/build/pNN/`,
#: `.temp/tNN/foo.c`, `.temp/TASK_NNN/`. Nothing else is skipped -- in
#: particular a real directory whose name merely CONTAINS "NN" in the middle
#: (there are none today) would still be checked.
PLACEHOLDER = re.compile(r"(^|/)[A-Za-z_]*N{2,}(/|$)")

#: The same rule for the OTHER template spelling, and it is just as narrow: a
#: path component that is ENTIRELY `<...>` is documentation syntax
#: (`harness/build.py`'s `.temp/build/<pNN>/<cell>-<opt>-<mode>`). A component
#: that merely CONTAINS one is not -- p27's per-PID `irt<pid>` spelling and
#: `.temp/check/p22/miri/miri.<name>.bin` are both still checked, and the second
#: of those resolves.
TEMPLATE = re.compile(r"(^|/)<[^/>]*>(/|$)")

KINDS = {
    # the citing file CREATES this path when it runs; not a reference
    "destination",
    # gone, but a surviving generator or an inline recipe rebuilds it
    # (constraint 6: keep the generator, delete the artefact)
    "regenerable",
    # the sentence asserts the path is WRONG or never existed
    "negative",
    # per-PID / per-run scratch that never persists by design
    "transient",
    # the artefact now lives IN THE TREE; the citation should be repointed.
    # `note` must name the tree path and, if the fix costs a sweep, say so.
    "promoted",
    # a quoted tool diagnostic, reproduced as evidence of what a run printed
    "quote",
    # an illustrative path in a usage line, never a real one
    "example",
    # the string is inside a GENERATED artefact and is not a citation at all
    "generated-record",
    # gone, not regenerable. `note` must say what it showed.
    "lost",
}

# --------------------------------------------------------------------------
# CHECK 2: `<harness module>.py:NNNN` line citations, tree-wide.
# --------------------------------------------------------------------------

#: ⚠ DELIBERATELY THE SAME EXPRESSION AS `check.py::_CITE_RE`, character for
#: character, so the two checks cannot disagree about what a citation IS. It
#: matches the LEADING number of a range, which is what makes
#: `check.py:1249-1278` -- the tree's own worst case, and four of the eight
#: citations TASK_168 fixed were ranges -- a hit. `\b` stops `12check.py:5`.
_LINE_CITE_RE = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*\.py):(\d+)")

#: The range/span TAIL, reported so a reader sees the citation as written.
_LINE_CITE_TAIL = re.compile(r"\A[-–—](\d+)")

#: Not text. (Nothing tracked has these today; the guard is so that a future
#: committed blob cannot make this scan emit mojibake hits.)
_LINE_SKIP_EXT = (".bin", ".log", ".pyc", ".png", ".pdf", ".gz", ".o", ".so")

LINE_KINDS = {
    # the sentence's SUBJECT is the coordinate -- it quotes a rotted citation
    # as evidence. Removing the colon deletes the finding.
    "quotation",
    # a literal inside a checker's own must-fire arm; the string is test DATA.
    "fixture",
    # the citation is inside a GENERATED artefact. `note` must name the real
    # fix site -- the generator, or the file the generator read.
    "generated-record",
    # a real citation owed a re-cite by FUNCTION, whose repair is priced
    # elsewhere. `note` must name the target function and the cost.
    "owed",
}


def harness_module_names():
    """Basenames of every `harness/` module a committed file could cite by line.

    ⚠ DERIVED from the tree, never enumerated -- the same rule and the same two
    globs as `check.py::harness_module_names`, so a new harness module is
    covered the day it lands. `harness/tools/` is included: this file is in it.
    A pattern's own `model.py:50` / `gen.py:30` is NOT a harness citation and is
    not matched, because a pattern may cite its own lines."""
    return frozenset(
        os.path.basename(p)
        for p in globmod.glob(os.path.join(REPO, "harness", "*.py"))
        + globmod.glob(os.path.join(REPO, "harness", "tools", "*.py")))


def line_citations(text, names):
    """`[(line_in_text, module, cited_line, as_written)]` for one blob of text.

    `as_written` keeps the range tail (`check.py:1249-1278`) so the report shows
    the citation the way the file spells it, while the KEY stays the leading
    coordinate -- a range whose head is re-cited is fixed, and one whose head
    still stands is not."""
    out = []
    for i, line in enumerate(text.split("\n"), 1):
        for m in _LINE_CITE_RE.finditer(line):
            if m.group(1) not in names:
                continue
            written = m.group(0)
            tail = _LINE_CITE_TAIL.match(line[m.end():])
            if tail:
                written += tail.group(0)
            out.append((i, m.group(1), int(m.group(2)), written))
    return out


def scan_lines(include_tasks, names=None):
    """-> `[(file, line, "<module>.py:<N>", as_written, text)]`, sorted.

    Scope is every COMMITTED file `tracked()` yields -- which is every committed
    directory, minus `.tasks/` (dated instructions) and `*_REPORT.md` (dated
    records), for the reason `tracked()` states: repointing a dated record
    falsifies it."""
    names = harness_module_names() if names is None else names
    hits = []
    for rel in tracked(include_tasks):
        if rel.endswith(_LINE_SKIP_EXT):
            continue
        try:
            with open(os.path.join(REPO, rel), encoding="utf-8") as fh:
                txt = fh.read()
        except (UnicodeDecodeError, OSError):
            continue
        for n, mod, cited, written in line_citations(txt, names):
            src = txt.split("\n")[n - 1].strip()[:150]
            hits.append((rel, n, f"{mod}:{cited}", written, src))
    return sorted(hits)


def _line_text(cite):
    """The text the cited coordinate holds TODAY -- the eyeball aid.

    ⚠ This is `.memory/02-bench-rules.md`'s aid, mechanised and no stronger:
    *"nothing can know what a citation MEANT, so it prints each target for a
    human to judge."* It never decides."""
    mod, _, n = cite.partition(":")
    for sub in ("harness", os.path.join("harness", "tools")):
        p = os.path.join(REPO, sub, mod)
        if os.path.exists(p):
            with open(p, encoding="utf-8", errors="replace") as fh:
                lines = fh.read().split("\n")
            i = int(n)
            return lines[i - 1].strip()[:78] if 1 <= i <= len(lines) else \
                f"(past EOF: {mod} has {len(lines)} lines)"
    return "(module not found)"


def check_lines(a):
    """The line-citation half. Same contract as `check`: NEW or UNCLASSIFIED
    fails, everything else is reported."""
    names = harness_module_names()
    hits = scan_lines(a.include_tasks, names)
    base = load_baseline()
    known = {(e["file"], e["citation"]): e
             for e in base.get("line_citations", [])}
    seen = {(f, c) for f, _, c, _, _ in hits}

    new = sorted({(f, n, c, w, t) for f, n, c, w, t in hits
                  if (f, c) not in known})
    unclassified = sorted(k for k, e in known.items()
                          if e.get("kind") not in LINE_KINDS)
    resolved = sorted(k for k in known if k not in seen)

    by_dir = collections.Counter(
        (f.split("/")[0] if "/" in f else "(root)") for f, _, _, _, _ in hits)
    print(f"\n=== line citations: `<harness module>.py:NNNN` in committed files")
    print(f"harness modules  : {len(names)} derived from harness/*.py + "
          f"harness/tools/*.py")
    print(f"citations        : {len(hits)} over "
          f"{len({c for _, _, c, _, _ in hits})} distinct coordinates in "
          f"{len({f for f, _, _, _, _ in hits})} files")
    print("   by directory  : " + "  ".join(
        f"{d} {n}" for d, n in sorted(by_dir.items(), key=lambda kv: -kv[1])))
    print(f"baseline         : {len(known)} entries")
    hist = collections.Counter(e.get("kind") or "(none)"
                               for e in base.get("line_citations", []))
    print("   by kind       : " + "  ".join(
        f"{k} {n}" for k, n in sorted(hist.items(), key=lambda kv: -kv[1])))

    if resolved:
        print(f"\n-- {len(resolved)} baseline line-citation entr"
              f"{'y' if len(resolved) == 1 else 'ies'} NO LONGER PRESENT "
              f"(re-cited by function, or the file stopped citing it).")
        print("   Not a failure. Run --update to prune.")
        for f, c in resolved:
            print(f"   RESOLVED  {c}   <- {f}")

    if unclassified:
        print(f"\n-- {len(unclassified)} baseline line-citation entries have no "
              f"`kind`. An unexplained entry is not a baseline, it is a mute.")
        for f, c in unclassified:
            print(f"   UNCLASSIFIED  {c}   <- {f}")

    if new:
        print(f"\n-- {len(new)} NEW line citation(s) into a harness module:")
        for f, n, c, w, t in new:
            print(f"   {f}:{n}  cites `{w}`\n      | {t}\n"
                  f"      that line today: {_line_text(c)}")
        print("\nFix: NAME THE FUNCTION AND GIVE NO LINE NUMBER --\n"
              "  `check.py::check_identity`. A function name cannot rot "
              "silently; rename it and\n"
              "  `grep` returns nothing, which is a loud failure. "
              "(`.memory/02-bench-rules.md`.)\n"
              "  ⚠ If the file is GENERATED, fix the GENERATOR -- editing the "
              "artefact is reverted\n"
              "     on the next run (PROTOCOL rule 6). If the coordinate IS "
              "the sentence's subject,\n"
              "     `--update` and classify it `quotation`.")

    bad = bool(new) or bool(unclassified)
    print(f"\ntemp_citations.py --lines: {'FAIL' if bad else 'OK'}"
          f"  (new={len(new)} unclassified={len(unclassified)} "
          f"resolved={len(resolved)})")
    return 1 if bad else 0


def show_lines(a):
    """The classified line-citation baseline, with today's text at each target.

    This is the half that would have caught item 40: a `generated-record` entry
    whose target line has drifted onto an unrelated function is visible here
    without anyone grepping."""
    base = load_baseline()
    by = collections.defaultdict(list)
    for e in base.get("line_citations", []):
        by[e.get("kind") or "(none)"].append(e)
    for kind in sorted(by):
        if a.kind and a.kind != kind:
            continue
        print(f"\n=== {kind}  ({len(by[kind])})")
        for e in sorted(by[kind], key=lambda x: (x["file"], x["citation"])):
            lines = ",".join(str(n) for n in e.get("lines", []))
            print(f"  {e['citation']}   <- {e['file']}:{lines}")
            print(f"      that line today: {_line_text(e['citation'])}")
            print(f"      {e['note']}")
    return 0


# --------------------------------------------------------------------------
# MUST-FIRE ARMS.
#
# ⚠ `owner()`'s docstring has cited *"Must-fire arm: `--selftest`"* since
# TASK_132 and THERE WAS NO `--selftest` -- a dangling citation inside the
# citation checker. TASK_170 added the flag and the arms, `owner`'s included.
#
# Every arm states the REGRESSION it is armed against, and every one of them was
# SEEN TO FAIL under that regression before it was written down (TASK_170,
# `.temp/t170/arm_break.py`).
# --------------------------------------------------------------------------

_N = frozenset({"check.py", "measure.py", "build.py"})


def _guard(fn, *args):
    """Call `fn`, or return `("RAISED", repr)`.

    ⚠ EVERY arm below goes through this. `.memory/03-measurement.md` entry 19:
    *reported, not crashed*. These tables are built at MODULE SCOPE, so a bare
    call that throws is an import-time traceback and the tool has no output at
    all -- which is the same defect TASK_170 item G fixed in `check.py`'s `0c`
    and `0d` arm tables. Do not un-wrap these."""
    try:
        return fn(*args)
    except Exception as e:                                   # noqa: BLE001
        return ("RAISED", repr(e))


def _lc(text):
    """`line_citations` with a fixed name set, guarded."""
    return _guard(line_citations, text, _N)


def _ow(line, start):
    """`owner`, guarded."""
    return _guard(owner, line, start)


_SELFTEST_CASES = [
    # (label, got, want) -- regression each arm is armed against, in the label.
    ("a plain `check.py:1249` is a citation "
     "[armed against: the module filter dropping check.py]",
     _lc("see `check.py:1249` for the rule"),
     [(1, "check.py", 1249, "check.py:1249")]),
    ("a RANGE `check.py:1249-1278` is caught, keyed on its HEAD "
     "[armed against: a `(?!-)` guard that would skip ranges]",
     _lc("`harness/check.py:1249-1278` requires"),
     [(1, "check.py", 1249, "check.py:1249-1278")]),
    ("an EN-DASH range keeps its tail too "
     "[armed against: an ASCII-only tail matcher]",
     _lc("`check.py:1249–1278`"),
     [(1, "check.py", 1249, "check.py:1249–1278")]),
    ("a path prefix does not hide it "
     "[armed against: anchoring the module at a word start only]",
     _lc("see harness/measure.py:64"),
     [(1, "measure.py", 64, "measure.py:64")]),
    ("the FUNCTION spelling passes -- this is the convention "
     "[armed against: matching `::` as if it were `:`]",
     _lc("see `check.py::check_identity` for the rule"), []),
    ("a pattern's OWN model.py/gen.py is not a harness citation "
     "[armed against: dropping the name filter and failing every pattern]",
     _lc("`model.py:50` and `gen.py:30`"), []),
    ("a digit-glued lookalike is not a citation "
     "[armed against: dropping `_LINE_CITE_RE`'s leading \\b]",
     _lc("see `12check.py:5`"), []),
    ("EVERY harness module counts here, not just check.py "
     "[armed against: re-narrowing this check to CITE_FATAL_MODULE]",
     _lc("`build.py:66` and `measure.py:238`"),
     [(1, "build.py", 66, "build.py:66"),
      (1, "measure.py", 238, "measure.py:238")]),
    ("line numbers are the CITING file's, so a second line is reported as 2 "
     "[armed against: enumerate() starting at 0]",
     _lc("nothing here\n`check.py:1`"), [(2, "check.py", 1, "check.py:1")]),
    # `owner()` -- the arm its docstring has cited since TASK_132.
    ("owner(): a bare `.temp/` hit is THIS repo's "
     "[armed against: treating every hit as foreign and checking nothing]",
     _ow("see `.temp/tNN/x`", 5), "self"),
    ("owner(): an absolute path INTO this repo is this repo's "
     "[armed against: a naive startswith('/') foreign test]",
     _ow(f"{REPO}/.temp/tNN/x", len(REPO) + 1), "self"),
    ("owner(): another project's absolute `.temp/` is FOREIGN "
     "[armed against: joining a foreign path to REPO and reporting it dangling]",
     _ow("/home/apt/other/.temp/x", len("/home/apt/other/")), "/home/apt/other"),
]


def selftest(_a=None):
    bad = 0
    for label, got, want in _SELFTEST_CASES:
        ok = got == want
        bad += not ok
        print(f"  {'ok  ' if ok else 'FAIL'}  {label}")
        if not ok:
            print(f"          got  {got!r}\n          want {want!r}")
    # the derivation itself, not a fixture: this is what makes a new harness
    # module covered the day it lands.
    names = harness_module_names()
    for must in ("check.py", "measure.py", "build.py", "vparse.py",
                 "temp_citations.py"):
        if must not in names:
            bad += 1
            print(f"  FAIL  harness_module_names() is missing {must}")
    print(f"\ntemp_citations.py --selftest: "
          f"{'FAIL' if bad else 'OK'}  ({len(_SELFTEST_CASES)} arms, "
          f"{bad} failing, {len(names)} harness modules derived)")
    return 1 if bad else 0


def tracked(include_tasks):
    """The COMMITTED file list.

    ⚠ `git ls-files`, never a walk of the working tree: an untracked scratch
    file must not be able to satisfy -- or to create -- a citation. Contents are
    read from the working tree, because that is where an edit under review is."""
    out = subprocess.run(["git", "ls-files"], cwd=REPO, capture_output=True,
                         text=True, check=True).stdout.split("\n")
    for rel in out:
        if not rel or not os.path.isfile(os.path.join(REPO, rel)):
            continue
        # EXEMPT, and the reason has to be in the code or somebody "fixes" it:
        # a task report is a DATED RECORD of what was true when it was written.
        # Repointing its citations would falsify the record; the report is the
        # evidence, and it is committed.
        if rel.endswith("_REPORT.md"):
            continue
        # Same argument, one step weaker, so it is a flag: a `.tasks/TASK_NNN.md`
        # is a dated instruction. TASK_029.md's citation is literally to a path
        # its own sentence says "never existed".
        if not include_tasks and rel.startswith(".tasks/"):
            continue
        # The baseline is a LIST OF DEAD PATHS BY CONSTRUCTION. Scanning it would
        # make every entry re-report itself from a new citing file, forever.
        if os.path.abspath(os.path.join(REPO, rel)) == BASELINE:
            continue
        yield rel


def resolve(p):
    """Does this citation still point at something on this box?"""
    if not META.search(p):
        return os.path.exists(os.path.join(REPO, p))
    g = re.sub(r"\{[^}]*\}|<[^>]*>|\$+\{?\w*\}?|\?", "*", p)
    g = re.sub(r"\*+", "*", g)
    return bool(globmod.glob(os.path.join(REPO, g)))


def scan(include_tasks):
    """-> (all citations {path: {file}}, dangling [(file, line, path, text)])"""
    cites = collections.defaultdict(set)
    dangling = []
    foreign = 0
    for rel in tracked(include_tasks):
        with open(os.path.join(REPO, rel), errors="replace") as fh:
            for n, line in enumerate(fh, 1):
                # DEFECT 2 (TASK_132): paths a committed .py ASSEMBLES.
                if rel.endswith(".py"):
                    for p in joined_paths(line):
                        cites[p].add(rel)
                        if not resolve(p):
                            dangling.append((rel, n, p, line.strip()[:160]))
                for m in PAT.finditer(line):
                    hit = m.group(0)
                    # DEFECT 1 (TASK_132): another project's `.temp/`.
                    if owner(line, m.start()) != "self":
                        foreign += 1
                        continue
                    # Trailing prose punctuation is not part of the path.
                    # ⚠ `*` IS NOT STRIPPED, and stripping it was a real bug in
                    # the first draft: `` `.temp/review021/v05/z3_*` `` became
                    # the stem `.../z3_`, which cannot exist, and the tool
                    # reported two live directories as dangling. Markdown bold
                    # does not reach a path in backticks, which is how every
                    # citation in this tree is written.
                    p = hit.rstrip(".,;:)`'\"-")
                    if not p or PLACEHOLDER.search(p) or TEMPLATE.search(p):
                        continue
                    cites[p].add(rel)
                    if not resolve(p):
                        dangling.append((rel, n, p, line.strip()[:160]))
    if foreign:
        print(f"note             : {foreign} `.temp/` hit(s) skipped as "
              f"ANOTHER PROJECT's absolute path (TASK_132 defect 1)")
    return cites, dangling


def load_baseline():
    if not os.path.exists(BASELINE):
        return {"entries": []}
    with open(BASELINE) as fh:
        return json.load(fh)


def check(a):
    cites, dangling = scan(a.include_tasks)
    base = load_baseline()
    known = {(e["file"], e["path"]): e for e in base["entries"]}
    seen = {(f, p) for f, _, p, _ in dangling}

    new = sorted({(f, n, p, t) for f, n, p, t in dangling if (f, p) not in known})
    unclassified = sorted(k for k, e in known.items()
                          if e.get("kind") not in KINDS)
    resolved = sorted(k for k in known if k not in seen)

    print(f"scanned          : {len(list(tracked(a.include_tasks)))} committed files"
          f"{'' if a.include_tasks else ' (.tasks/ exempt; --include-tasks to scan)'}")
    print(f"citations        : {sum(len(v) for v in cites.values())} "
          f"over {len(cites)} distinct .temp/ paths")
    print(f"dangling         : {len(dangling)} citations, "
          f"{len({p for _, _, p, _ in dangling})} distinct paths, "
          f"{len({f for f, _, _, _ in dangling})} files")
    print(f"baseline         : {len(known)} entries  ({BASELINE[len(REPO) + 1:]})")
    hist = collections.Counter(e.get("kind") or "(none)"
                               for e in base["entries"])
    print("   by kind       : " + "  ".join(
        f"{k} {n}" for k, n in sorted(hist.items(), key=lambda kv: -kv[1])))
    print("⚠ this is a THIS-BOX check; in a fresh clone every citation dangles.")

    if resolved:
        print(f"\n-- {len(resolved)} baseline entr{'y' if len(resolved) == 1 else 'ies'} "
              f"NO LONGER DANGLING (fixed, or the file stopped citing it).")
        print("   Not a failure. Run --update to prune, so the baseline cannot rot.")
        for f, p in resolved:
            print(f"   RESOLVED  {p}   <- {f}")

    if unclassified:
        print(f"\n-- {len(unclassified)} baseline entries have no `kind`. "
              f"An unexplained entry is not a baseline, it is a mute.")
        for f, p in unclassified:
            print(f"   UNCLASSIFIED  {p}   <- {f}")

    if new:
        print(f"\n-- {len(new)} NEW dangling citation(s):")
        for f, n, p, t in new:
            print(f"   {f}:{n}\n      {p}\n      | {t}")
        print("\nFix, in this order (TASK_125 §B, and the first two are usually "
              "the right one):\n"
              "  (a) the generator survives  -> cite the generator and say what "
              "it rebuilds;\n"
              "  (b) it is re-derivable      -> cite the rebuild command;\n"
              "  (c) it is EVIDENCE a reader must be able to check -> PROMOTE it "
              "into the tree\n"
              "      (patterns/pNN/controls/ for a pattern probe, common/ for "
              "cross-pattern data);\n"
              "  (d) none of those           -> `--update`, then write a `kind` "
              "and a `note` saying\n"
              "      what it showed. A path that silently resolves to nothing is "
              "the only wrong answer.")

    bad = bool(new) or bool(unclassified)
    print(f"\ntemp_citations.py: {'FAIL' if bad else 'OK'}"
          f"  (new={len(new)} unclassified={len(unclassified)} "
          f"resolved={len(resolved)})")
    return 1 if bad else 0


def update(a):
    """Re-skeleton the baseline: keep every `kind`/`note` already written, add
    today's unknown dangling citations with an EMPTY `kind`, drop the resolved.

    ⚠ Deliberately not a blessing button -- `check` fails on an empty `kind`."""
    _, dangling = scan(a.include_tasks)
    base = load_baseline()
    known = {(e["file"], e["path"]): e for e in base["entries"]}
    # ⚠ ONE entry per (file, path), with the line numbers as a LIST. Keying on
    # the line number would make the baseline go stale on any edit above the
    # citation -- the `check.py:NNNN` rot this project already has a rule
    # against -- and three of these files cite one path from three lines.
    lines = collections.defaultdict(set)
    for f, n, p, _ in dangling:
        lines[(f, p)].add(n)
    entries, added = [], 0
    for f, p in sorted(lines):
        old = known.get((f, p))
        if old:
            old["lines"] = sorted(lines[(f, p)])
            old.pop("line", None)
            entries.append(old)
        else:
            entries.append({"file": f, "lines": sorted(lines[(f, p)]),
                            "path": p, "kind": "", "note": ""})
            added += 1
    seen = {(e["file"], e["path"]) for e in entries}
    dropped = [k for k in known if k not in seen]
    base["entries"] = entries
    base["count"] = len(entries)
    with open(BASELINE, "w") as fh:
        json.dump(base, fh, indent=1)
        fh.write("\n")
    print(f"{BASELINE[len(REPO) + 1:]}: {len(entries)} entries "
          f"(+{added} new, -{len(dropped)} resolved)")
    if added:
        print(f"⚠ {added} entr{'y' if added == 1 else 'ies'} need a `kind` "
              f"(one of {sorted(KINDS)}) and a `note`.")
    return update_lines(a, base)


def update_lines(a, base=None):
    """The same re-skeleton for the line-citation array. Keyed on
    `(citing file, "<module>.py:<N>")` -- NOT on the citing line number, for the
    reason `update` states above: keying on a line number makes the baseline go
    stale on any edit above the citation, which is the very rot this check is
    about."""
    base = load_baseline() if base is None else base
    hits = scan_lines(a.include_tasks)
    known = {(e["file"], e["citation"]): e
             for e in base.get("line_citations", [])}
    lines, written = collections.defaultdict(set), {}
    for f, n, c, w, _ in hits:
        lines[(f, c)].add(n)
        written[(f, c)] = w
    entries, added = [], 0
    for f, c in sorted(lines):
        old = known.get((f, c))
        if old:
            old["lines"] = sorted(lines[(f, c)])
            old["as_written"] = written[(f, c)]
            entries.append(old)
        else:
            entries.append({"file": f, "lines": sorted(lines[(f, c)]),
                            "citation": c, "as_written": written[(f, c)],
                            "kind": "", "note": ""})
            added += 1
    dropped = [k for k in known if k not in lines]
    base["line_citations"] = entries
    base["line_citation_count"] = len(entries)
    base["line_citation_kinds"] = {
        "quotation": "the sentence's SUBJECT is the coordinate -- it quotes a "
                     "rotted citation as evidence; removing the colon deletes "
                     "the finding",
        "fixture": "a literal inside a checker's own must-fire arm; the string "
                   "is test DATA",
        "generated-record": "the citation is inside a GENERATED artefact; the "
                            "`note` names the real fix site (the generator, or "
                            "the file the generator read)",
        "owed": "a real citation owed a re-cite BY FUNCTION whose repair is "
                "priced elsewhere; the `note` names the target function and "
                "the cost",
    }
    with open(BASELINE, "w") as fh:
        json.dump(base, fh, indent=1)
        fh.write("\n")
    print(f"{BASELINE[len(REPO) + 1:]}: {len(entries)} line-citation entries "
          f"(+{added} new, -{len(dropped)} resolved)")
    if added:
        print(f"⚠ {added} line-citation entr{'y' if added == 1 else 'ies'} "
              f"need a `kind` (one of {sorted(LINE_KINDS)}) and a `note`.")
    return 0


def census(a):
    """The forward policy's SIZE BOUND, re-derivable from the tree.

    TASK_125 measured this because *promote, don't publish* was adopted without
    one. A STRICT reading -- every cited `.temp/` path gets promoted -- is
    unbounded; the two bounds that make it finite are printed here."""
    keep = {".json", ".log", ".md", ".py", ".rs", ".c", ".h", ".txt", ".sh",
            ".toml"}
    rebuilt = (".temp/build", ".temp/check", ".temp/clausemut")
    cites, _ = scan(a.include_tasks)
    files, dirs, gone, closure = [], [], [], {}
    for p in sorted(cites):
        ap = os.path.join(REPO, p)
        if os.path.isfile(ap):
            files.append(p)
            closure[os.path.realpath(ap)] = os.path.getsize(ap)
        elif os.path.isdir(ap):
            dirs.append(p)
            for root, _, fs in os.walk(ap):
                for x in fs:
                    f = os.path.join(root, x)
                    if os.path.isfile(f) and not os.path.islink(f):
                        closure[os.path.realpath(f)] = os.path.getsize(f)
        else:
            gone.append(p)

    def mb(v):
        return sum(v) / 1e6

    print(f"cited .temp/ paths : {len(cites)}   plain file {len(files)} / "
          f"dir {len(dirs)} / neither {len(gone)}")
    print("   ('neither' is globs and missing paths together -- a glob has no "
          "size, so it is\n    excluded from the closures below; the DANGLING "
          "figure is the default mode's.)")
    print(f"STRICT closure (cited files + everything under cited dirs): "
          f"{len(closure)} files, {mb(closure.values()):.1f} MB")
    fsz = {p: os.path.getsize(os.path.join(REPO, p)) for p in files}
    print(f"WEAK   closure (paths cited AS FILES)                     : "
          f"{len(fsz)} files, {mb(fsz.values()):.2f} MB")
    for label, sel in (
        ("  under .temp/{build,check,clausemut} (a committed script rebuilds these)",
         {p: s for p, s in fsz.items() if p.startswith(rebuilt)}),
        ("  KEEP extensions (constraint 6's own list)",
         {p: s for p, s in fsz.items()
          if os.path.splitext(p)[1].lower() in keep}),
        ("  KEEP + not rebuilt + <= 256 KB",
         {p: s for p, s in fsz.items()
          if os.path.splitext(p)[1].lower() in keep
          and not p.startswith(rebuilt) and s <= 256 * 1024}),
        ("  source only (.py/.rs/.c/.h/.sh), not rebuilt",
         {p: s for p, s in fsz.items()
          if os.path.splitext(p)[1].lower() in {".py", ".rs", ".c", ".h", ".sh"}
          and not p.startswith(rebuilt)}),
    ):
        print(f"{label:70s} {len(sel):5d} files {mb(sel.values()):9.2f} MB")
    print(f"\ncommitted files SCANNED, for scale: "
          f"{len(list(tracked(a.include_tasks)))}  "
          f"(`git ls-files | wc -l` is larger; this excludes the exemptions)")
    print("⚠ So the binding constraint on a strict `promote everything` rule is "
          "not bytes --\n  it is FILE COUNT: the tightest sensible bound still "
          "roughly doubles the tracked tree.")
    return 0


def show(a):
    """Print the classified baseline -- the `say what it showed` half of the
    policy. This is the answer to *"the annotation is in a JSON, not next to the
    sentence"*: one command puts it in front of the reader, grouped."""
    base = load_baseline()
    by = collections.defaultdict(list)
    for e in base["entries"]:
        by[e.get("kind") or "(none)"].append(e)
    for kind in sorted(by):
        if a.kind and a.kind != kind:
            continue
        print(f"\n=== {kind}  ({len(by[kind])})")
        for e in sorted(by[kind], key=lambda x: (x["file"], x["path"])):
            lines = ",".join(str(n) for n in e.get("lines", []))
            print(f"  {e['path']}\n      cited by {e['file']}:{lines}\n"
                  f"      {e['note']}")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--list", dest="show", action="store_true",
                    help="print the classified baseline, grouped by kind")
    ap.add_argument("--kind", help="with --list, only this kind")
    ap.add_argument("--update", action="store_true",
                    help="re-skeleton the baseline (does not classify)")
    ap.add_argument("--census", action="store_true",
                    help="the promotion size-bound figures")
    ap.add_argument("--include-tasks", action="store_true",
                    help="also scan .tasks/ (dated instructions; exempt by default)")
    ap.add_argument("--lines", action="store_true",
                    help="ONLY the `<harness module>.py:NNNN` line-citation "
                         "check (it also runs by default)")
    ap.add_argument("--list-lines", action="store_true",
                    help="the classified line-citation baseline, with the text "
                         "each cited line holds TODAY")
    ap.add_argument("--selftest", action="store_true",
                    help="the must-fire arms")
    a = ap.parse_args()
    if a.selftest:
        return selftest(a)
    if a.list_lines:
        return show_lines(a)
    if a.show:
        return show(a)
    if a.update:
        return update(a)
    if a.census:
        return census(a)
    if a.lines:
        return check_lines(a)
    # ⚠ BOTH checks, and the exit status is the OR. A tool whose second half can
    # fail while it prints `OK` is worse than no second half -- `PROTOCOL` rule
    # 7's *"check each script's own exit status, not a pipeline's"* applies
    # inside a script too.
    rc = check(a)
    rc |= check_lines(a)
    return rc


if __name__ == "__main__":
    sys.exit(main())
