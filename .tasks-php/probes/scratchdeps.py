#!/usr/bin/env python3
"""WHICH PUBLISHED DOCUMENTS STILL DEPEND ON GITIGNORED SCRATCH -- the SET, not a count.

⛔⛔⛔ WHY THIS REPLACES AN ARM I BUILT FOUR DAYS AGO. `boxcheck.py` grew a
`.memory-php -> .temp` arm on 2026-09-17 as the remedy for `TASK_PHP_063` §7.2.
It printed **4**, and the START HERE box published that 4 as the work to do.
On first contact with the real set the 4 was wrong in BOTH directions:

  * it matched `.temp/<path>` ONLY, so **five citations that name a scratch
    probe by BARE FILENAME were invisible** -- `identity_null.py` (x2),
    `inclusive_ir.py`, `bc_sweep.py`, `flip_exact.py`, the evidence behind six
    published findings (F82-F87);
  * one of the 4 it did print, `04-process.md:165 -> .temp/php39/width.py`, is
    **NOT a live dependency at all**: that probe was promoted to
    `.tasks-php/width.py` on 2026-09-13 and the citation simply went stale;
  * it scanned `.memory-php/` ONLY, while `RECAP_PHP.md` -- the document whose
    own box published the 4 -- carries 91 `.temp/` citations of its own.

▶ **THE ARM'S CARDINALITY WAS TREATED AS THE MEMBERSHIP** (`F142`), by the
manager, in the box, one round after `F142` was written. And its recall was
measured at the only n it had ever seen -- `F140`'s shape exactly.

⚠⚠ THE DISTINCTION THIS TOOL EXISTS TO HOLD, AND IT IS EASY TO GET BACKWARDS:

  * a **SCRIPT** or an **EVIDENCE DOCUMENT** living only in gitignored scratch
    is the DEFECT (`.memory-php/04-process.md` law 11: a published finding whose
    only evidence is a gitignored probe will not survive a clean checkout);
  * a **re-derivable ARTEFACT** under `.temp/` -- a callgrind profile, a `.bin`,
    a build tree -- is **THE RULE**, not a defect (`CLAUDE.md` Don't #1, *keep
    the generator, delete the artefact*).

So this tool must never report an artefact as a dependency, and never report a
script as an artefact.

⚠⚠ WHAT `LIVE` IS AND IS NOT -- STATED, BECAUSE THE FIRST ARM'S WHOLE DEFECT WAS
LETTING A NUMBER STAND FOR A SET. `LIVE` is a **CANDIDATE SET REQUIRING
ADJUDICATION BY UNIT TEXT** (`F132`), not a defect count. This tool cannot tell
apart two things that look identical to a regex:

  * `.temp/mgr172/identity_null.py` -- a probe I WROTE, whose loss loses the
    evidence for F82. A law-11 defect.
  * `.temp/php27/streamsfuncs.c` -- PHP 5.0.0 source EXTRACTED into scratch,
    re-derivable from `patterns-php/php-5.0.0.manifest`. **Not a defect**; the
    rule being followed.

▶ So read the SET and rule on each row. A row here is a QUESTION, not a verdict.

⛔⛔ AND IT MUST NOT GUESS. 50 tracked files are called `NOTES.md`. A resolver
that answers "is there a tracked file with this basename" would report
`.temp/mgr172/NOTES.md` -- the evidence record behind F82-F87 -- as ALREADY
PROMOTED, because `patterns-php/ph03-uudecode-bound/NOTES.md` exists. ▶ There
are THREE outcomes, not two, and the third is printed rather than hidden:
**LIVE / PROMOTED (citation stale) / AMBIGUOUS (name too generic to resolve)**.

RUN IT:  python3 .tasks-php/probes/scratchdeps.py --selftest   # the negatives
         python3 .tasks-php/probes/scratchdeps.py              # the census

Read-only. Re-derives everything from the working tree and `git ls-files`.
"""
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# The documents whose scratch dependencies MATTER: the authoritative layer and
# the handoff. ⚠ `.tasks-php/` reports are a HISTORICAL record -- a task report
# citing the scratch it ran in is correct and must not be flagged.
def scan_set():
    out = [os.path.join(ROOT, "RECAP_PHP.md")]
    mem = os.path.join(ROOT, ".memory-php")
    if os.path.isdir(mem):
        out += [os.path.join(mem, f) for f in sorted(os.listdir(mem))
                if f.endswith(".md")]
    return [p for p in out if os.path.exists(p)]


# ⚠ A citation of the RULE about `.temp/` is not a dependency ON `.temp/`.
PATH_RE = re.compile(r'`?(\.temp/[A-Za-z0-9_./-]+)')
BARE_RE = re.compile(r'`([A-Za-z0-9_][A-Za-z0-9_.-]*\.(?:py|sh|rs|c))`')

# Suffixes that carry EVIDENCE. Everything else under `.temp/` is an artefact or
# a directory, and an artefact under `.temp/` is the rule being followed.
EVIDENCE_SUFFIX = (".py", ".sh", ".rs", ".c", ".md")

# ⛔ Basenames too generic to resolve by name. `NOTES.md` has 50 tracked
# instances; answering "promoted?" from the basename would be a guess.
GENERIC = {"NOTES.md", "README.md", "run.sh", "gen.py", "build.sh",
           "Makefile", "main.rs", "kernel.c", "spec.md", "model.py"}

LIVE, PROMOTED, AMBIG, ARTEFACT, RULE = (
    "LIVE", "PROMOTED", "AMBIGUOUS", "artefact", "rule-spelling")


def tracked_basenames(_cache={}):
    """Every basename git tracks, as a set. ⚠ `git ls-files` not the filesystem:
    the question is what survives a CLEAN CHECKOUT, which is what git holds."""
    if not _cache:
        r = subprocess.run(["git", "ls-files"], cwd=ROOT,
                           capture_output=True, text=True)
        _cache["v"] = {os.path.basename(l) for l in r.stdout.split("\n") if l}
    return _cache["v"]


def classify(path, tracked):
    """PURE, given `tracked`. Returns (verdict, why)."""
    if path in (".temp", ".temp/"):
        return RULE, "the bare directory is how the rule is spelled"
    base = os.path.basename(path.rstrip("/"))
    if not path.endswith(EVIDENCE_SUFFIX):
        return ARTEFACT, "no evidence suffix -- a directory or a re-derivable blob"
    if base in GENERIC:
        return AMBIG, f"`{base}` is too generic to resolve by name"
    if base in tracked:
        # ⚠⚠ `PROMOTED` MEANS *A TRACKED TWIN EXISTS*, NOT *THIS CITATION IS
        # WRONG*. A citation may point into `.temp/` on purpose, as HISTORY --
        # `.memory-php/04-process.md`'s law 11 says F92's probe "WAS in
        # `.temp/php39/width.py`" and then names the promotion. That is the
        # CORRECT form and it still matches here, because this tool resolves
        # PATHS and cannot read TENSE. ⛔ Teaching it to would be regex-tuning
        # over prose, which is the defect `F148` is about. ▶ A reader rules.
        return PROMOTED, f"a tracked `{base}` exists -- STALE, or deliberate HISTORY"
    return LIVE, "no tracked file of this name -- will not survive a clean checkout"


def census():
    """The SET. Returns a list of dicts; the caller counts if it wants a count."""
    tracked = tracked_basenames()
    rows = []
    for f in scan_set():
        rel = os.path.relpath(f, ROOT)
        with open(f, encoding="utf-8", errors="replace") as fh:
            for i, line in enumerate(fh, 1):
                seen = set()
                for m in PATH_RE.finditer(line):
                    p = m.group(1).rstrip(".,;:)`")
                    if p in seen:
                        continue
                    # ⛔ ADD THE BASENAME TOO. Without this, a line that cites
                    # BOTH `.temp/mgr172/inclusive_ir.py` and the bare
                    # `inclusive_ir.py` is counted TWICE -- measured at
                    # `RECAP_PHP.md:9112` on this tool's first live run.
                    seen.add(p)
                    seen.add(os.path.basename(p))
                    v, why = classify(p, tracked)
                    rows.append(dict(doc=rel, line=i, cite=p, spelling="path",
                                     verdict=v, why=why,
                                     exists=os.path.exists(os.path.join(ROOT, p))))
                # ⭐ THE SPELLING THE FIRST ARM COULD NOT SEE. A bare name is a
                # dependency only if it resolves to scratch and NOT to the tree.
                for m in BARE_RE.finditer(line):
                    b = m.group(1)
                    if b in seen or b in tracked or b in GENERIC:
                        continue
                    hits = scratch_hits(b)
                    if not hits:
                        continue
                    seen.add(b)
                    rows.append(dict(doc=rel, line=i, cite=hits[0],
                                     spelling="bare", verdict=LIVE,
                                     why=f"cited as `{b}`, resolves only to scratch",
                                     exists=True))
    return rows


def scratch_hits(base, _cache={}):
    """Where under `.temp/` does this basename live? ⚠ Depth-limited: `.temp/`
    holds build trees with thousands of files and the answer does not need them."""
    if not _cache:
        top = os.path.join(ROOT, ".temp")
        idx = {}
        if os.path.isdir(top):
            for d in sorted(os.listdir(top)):
                sub = os.path.join(top, d)
                if not os.path.isdir(sub):
                    continue
                try:
                    for f in os.listdir(sub):
                        if os.path.isfile(os.path.join(sub, f)):
                            idx.setdefault(f, []).append(f".temp/{d}/{f}")
                except OSError:
                    pass
        _cache["v"] = idx
    return _cache["v"].get(base, [])


_HEAD = re.compile(r'^#{1,4}\s')
_FHEAD = re.compile(r'^#{1,4}\s+\**(F\d+)\b')


def sections(doc_rel, _cache={}):
    """-> [(start_line, 'F<N>' or None)] for every heading in a document.

    ⭐⭐ THIS IS THE GRANULARITY `citecheck.py` GOT WRONG, AND ITS PREMISE WAS
    HALF RIGHT. It excludes `RECAP_PHP.md` wholesale, reasoning that the handoff
    *"cites the manager's current scratch on purpose as provenance for work in
    flight"*. Measured over its 48 LIVE citations: **14 are in the OPEN-ITEMS
    TABLE, where that is exactly right**, and **32 are inside `### F<N>` finding
    sections, where it is false** -- `F82`'s evidence line has been a published,
    cited finding for five days. ▶ A SECTION-LEVEL PROPERTY IMPLEMENTED AS A
    FILE-LEVEL EXCLUSION (`F147`(d)). The repair NARROWS the exclusion; it does
    not reverse it, because the half that is right bought something real.
    """
    if doc_rel not in _cache:
        out = []
        with open(os.path.join(ROOT, doc_rel), encoding="utf-8",
                  errors="replace") as fh:
            for i, l in enumerate(fh, 1):
                if _HEAD.match(l):
                    m = _FHEAD.match(l)
                    out.append((i, m.group(1) if m else None))
        _cache[doc_rel] = out
    return _cache[doc_rel]


def _section_of(secs, line):
    """PURE. Which section `line` falls in, given `[(start, key)]` in order.

    ⭐ SPLIT OUT SO THE NEGATIVES CAN PLANT THEIR OWN INPUT. An arm that pinned
    real line numbers would break the moment anyone edited `RECAP_PHP.md` --
    and the edits that DISCHARGE this work are exactly such edits. An arm must
    not go red because the tree got healthier (`F147`'s sibling lesson).
    """
    hit = None
    for start, key in secs:
        if start > line:
            break
        hit = key
    return hit


def finding_of(doc_rel, line):
    return _section_of(sections(doc_rel), line)


def published_finding_deps():
    """The rows a COMMITTED FINDING depends on -- the law-11 population.

    ⛔ Still a CANDIDATE SET (`F132`). A finding section may cite scratch as
    history; what it may not do is rest on it.
    """
    out = []
    for r in census():
        if r["verdict"] != LIVE:
            continue
        f = finding_of(r["doc"], r["line"])
        if f:
            out.append(dict(r, finding=f))
    return out


def report():
    rows = census()
    order = [LIVE, AMBIG, PROMOTED]
    bad = [r for r in rows if r["verdict"] in order]
    print(f"scanned {len(scan_set())} document(s); "
          f"{len(rows)} `.temp/` citation(s); "
          f"{len(bad)} needing a decision")
    for v in order:
        sel = [r for r in rows if r["verdict"] == v]
        print(f"\n  {v:10} {len(sel):3}")
        for r in sel:
            mark = "" if r["exists"] else "  ⛔ TARGET GONE"
            print(f"    {r['doc']}:{r['line']:<6} {r['cite']:<38} "
                  f"[{r['spelling']}] {r['why']}{mark}")
    quiet = [r for r in rows if r["verdict"] not in order]
    print(f"\n  {'(not a dependency)':10} {len(quiet):3}  "
          f"{ARTEFACT}/{RULE} -- `CLAUDE.md` Don't #1 being FOLLOWED")

    # ⛔ THE LAW-11 POPULATION: a citation inside a PUBLISHED finding's section.
    pfd = published_finding_deps()
    fs = sorted({r["finding"] for r in pfd}, key=lambda x: int(x[1:]))
    print(f"\n  {'law 11':10} {len(pfd):3}  citation(s) inside a `### F<N>` "
          f"section, over {len(fs)} published finding(s)")
    print(f"    {' '.join(fs)}")
    print(f"    ⚠ the REST of `RECAP_PHP.md`'s LIVE citations are in the "
          f"OPEN-ITEMS TABLE,\n      where citing current scratch as provenance "
          f"for work in flight is CORRECT.")
    return bad


# ---------------------------------------------------------------- negatives
def selftest():
    """⛔ EVERY ARM HERE MUST FAIL IF THE CODE IS WRONG. An arm pinned to the
    tree's current CONTENT would go green the day the work is done and stop
    testing anything -- so the arms plant their own inputs where they can."""
    fails = []

    def chk(name, got, want, note):
        if got != want:
            fails.append(f"{name}: got {got!r} want {want!r} -- {note}")
        print(f"  {'ok ' if got == want else 'FAIL'} {name:6} {note}")

    # A synthetic tracked-set, so these arms do not move when the tree does.
    T = {"width.py", "coverage.py", "NOTES.md", "check.py"}

    chk("N1", classify(".temp/zz/zzz_never_promoted.py", T)[0], LIVE,
        "a scratch script with no tracked twin is a LIVE dependency")
    chk("N2", classify(".temp/php39/width.py", T)[0], PROMOTED,
        "a scratch path whose basename IS tracked is a STALE CITATION, not a dep")
    chk("N3", classify(".temp/mgr172/NOTES.md", T)[0], AMBIG,
        "⛔ 50 tracked `NOTES.md` -- resolving this by name would be a GUESS")
    chk("N4", classify(".temp/mgr172/cg/p25.unsafe.small.out", T)[0], ARTEFACT,
        "a callgrind profile under `.temp/` is the RULE, never a defect")
    chk("N5", classify(".temp/", T)[0], RULE,
        "the bare directory is how the rule itself is spelled")
    chk("N6", classify(".temp/php39/", T)[0], ARTEFACT,
        "a directory citation is not an evidence citation")

    # ⭐ The spelling the first arm could not see, tested as TEXT so the arm
    # survives the promotion that is about to happen.
    planted = "evidence: probe `zzz_never_promoted.py`, `--selftest` PASS"
    chk("N7", bool(BARE_RE.search(planted)), True,
        "a BARE filename citation is matched at all -- the 2026-09-17 blind spot")
    chk("N8", BARE_RE.search(planted).group(1), "zzz_never_promoted.py",
        "and the name is captured without its backticks")
    chk("N9", bool(BARE_RE.search("see `.temp/mgr172/bc_sweep.py` for the sweep")),
        False, "a PATH citation must not also fire the BARE arm (double-count)")

    # The two resolvers must disagree with each other on a generic name, which
    # is the whole reason AMBIGUOUS exists.
    chk("N10", classify(".temp/x/NOTES.md", T)[0] == classify(".temp/x/n.md", T)[0],
        False, "generic and specific `.md` must NOT classify alike")

    # ⛔ An arm over the LIVE tree, pinned to a property that cannot go green by
    # accident: the scan set must include the handoff, which the first arm missed.
    docs = [os.path.relpath(p, ROOT) for p in scan_set()]
    chk("N11", "RECAP_PHP.md" in docs, True,
        "⛔ the first arm scanned `.memory-php/` ONLY and missed the handoff")
    chk("N12", any(d.startswith(".memory-php/") for d in docs), True,
        "and the authoritative layer is still scanned")

    # ---- the SECTION granularity, on PLANTED input so the tree may move ----
    # `### F82` at 10, an unnamed `## Open items` at 50, `### F99` at 80.
    S = [(10, "F82"), (50, None), (80, "F99")]
    chk("N13", _section_of(S, 20), "F82",
        "a citation inside a finding's section is attributed to that finding")
    chk("N14", _section_of(S, 60), None,
        "⛔ one inside the OPEN-ITEMS TABLE is attributed to NOTHING -- that is "
        "the half of citecheck's exclusion that was RIGHT")
    chk("N15", _section_of(S, 5), None,
        "and one before any heading is attributed to nothing")
    chk("N16", _section_of(S, 80), "F99",
        "the boundary line itself belongs to the section it opens")
    chk("N17", _section_of([], 42), None,
        "a document with no headings attributes nothing (no IndexError)")

    # ⛔ ONE LIVE ARM, AND IT IS STRUCTURAL ON PURPOSE. It asserts the heading
    #   regex still parses the handoff -- NOT that any particular finding is
    #   still dirty, which would go red the day the work is finished.
    live = sections("RECAP_PHP.md")
    chk("N18", bool(live) and any(k for _, k in live), True,
        "the `### F<N>` regex still finds finding headings in RECAP_PHP.md")

    print("\nSELFTEST " + ("PASS" if not fails else f"FAIL ({len(fails)})"))
    for f in fails:
        print("   " + f)
    return 1 if fails else 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    report()
    sys.exit(0)
