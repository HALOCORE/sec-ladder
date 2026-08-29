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
    for rel in tracked(include_tasks):
        with open(os.path.join(REPO, rel), errors="replace") as fh:
            for n, line in enumerate(fh, 1):
                for hit in PAT.findall(line):
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
    a = ap.parse_args()
    if a.show:
        return show(a)
    if a.update:
        return update(a)
    if a.census:
        return census(a)
    return check(a)


if __name__ == "__main__":
    sys.exit(main())
