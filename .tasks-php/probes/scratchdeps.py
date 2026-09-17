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


# ------------------------------------------------- THE ADJUDICATION (item 148)
# ⛔⛔ A VERDICT PER (finding, cited file), reached on 2026-09-17 by READING THE
# CITING SENTENCE -- item 125's method, which is the only one that has ever
# worked here. `F132`: the census prints a CANDIDATE SET and a person rules on
# it. This table IS the ruling; the prose write-up is `F150`.
#
# THREE VERDICTS, and the two that are NOT defects carry the whole lesson:
#
#   RESTS    the finding's PUBLISHED NUMBER is this file's OUTPUT. Lose the
#            file and the number cannot be re-derived by anyone. ▶ LAW-11
#            DEFECT. Remedy: promote the probe, or re-ground the finding.
#   HISTORY  the file is the SUBJECT of the sentence, not its evidence -- a
#            retracted probe being named, a defect class being illustrated.
#            The claim is stated in full where it is made, so losing the file
#            loses no evidence. ⚠ NOT a licence: it applies only where the
#            finding makes no live quantitative claim the file alone supports.
#   NOTDEP   not a dependency on scratch AT ALL. Either upstream source
#            (`CLAUDE.md` Don't #1 being FOLLOWED), or -- and this is the one
#            that surprised me -- the census's BARE-NAME resolver matching a
#            token that is a FILENAME IN A TABLE and not a citation of scratch.
VERDICT_RESTS, VERDICT_HISTORY, VERDICT_NOTDEP = "RESTS", "HISTORY", "NOTDEP"

# ⛔⛔ A FOURTH VERDICT, ADDED THE DAY THE RULING WAS FIRST TESTED AGAINST
#   REALITY. `classify()` resolves `PROMOTED` by BASENAME, so a promotion that
#   RENAMES the file is invisible to it -- `.temp/mgr176/asanfill.c` became
#   `.tasks-php/asan_fill_byte.c` on 2026-09-13 and the census still called it
#   LIVE four days later, and I ruled it `RESTS` on that basis.
# ▶ The remedy for one of these is a REPOINT, which is free, and NOT a
#   promotion, which is work already done. Telling them apart matters because
#   the pile of "owed promotions" is what the next task is sized from.
# ⚠ It is also the reason `AMBIGUOUS` exists one level up: this tool must never
#   GUESS that two files with different names are the same file. A rename is
#   found by a PERSON reading the citing sentence, which is what item 148 was.
VERDICT_PROMOTED_STALE = "PROMOTED-RENAMED"

ADJUDICATION = {
    # (finding, cited path) -> (verdict, why -- in the citing sentence's terms)
    ("F44", ".temp/mgr165/count_ent.py"): (
        VERDICT_RESTS, "the four-table result 63/65 22/23 66/67 410/411 is its "
        "output; the `nm -S` figures corroborate but the INDEPENDENT method is "
        "the added value and only this file carries it"),
    ("F50", ".temp/mgr165/REFETCH.sh"): (
        VERDICT_RESTS, "named in the finding as the script that REGENERATES all "
        "of F50's evidence -- the generator `CLAUDE.md` Don't #1 asks for, kept "
        "where a clean checkout cannot see it"),
    ("F50", ".temp/mgr166/asan_reach.c"): (
        VERDICT_RESTS, "the instrument behind the published bytes x ASan x "
        "canary table and the `cliff is at 32 bytes, not near 384` claim"),
    ("F50", ".temp/mgr165/count_ent.py"): (
        VERDICT_HISTORY, "`same class as count_ent.py` -- a precedent for a "
        "defect SHAPE, and the shape is spelled out in the sentence"),
    ("F51", ".temp/mgr165/count_ent.py"): (
        VERDICT_HISTORY, "`the exact failure count_ent.py produced last "
        "session` -- a precedent; F51's own evidence is `coverage.py`, PROMOTED"),
    ("F52", ".temp/mgr165/count_ent.py"): (
        VERDICT_HISTORY, "a row in the three-probes table, whose cell states "
        "the construction error in full"),
    ("F52", ".temp/mgr166/asan_reach.c"): (
        VERDICT_HISTORY, "same table; the cell quotes the literal that caused "
        "it (`CANARY_BYTE 0xA5`, bit 0 already set)"),
    ("F52", ".temp/php21/ph94_probe2.c"): (
        VERDICT_HISTORY, "same table; `a memset PHP does not do` is the whole "
        "claim and it is retracted, not relied on"),
    ("F53", ".temp/php19/entcount.py"): (
        VERDICT_RESTS, "`entcount.py run at nine PHP-5.0 commits` IS the "
        "evidence for `ph32`'s stated R1h being wrong for two of three tables"),
    ("F59", ".temp/php27/streamsfuncs.c"): (
        VERDICT_NOTDEP, "⚠ FALSE POSITIVE of the bare-name resolver: here "
        "`streamsfuncs.c` is a COLUMN HEADING naming a PHP 5.0.0 source file, "
        "and the counts come from the committed `index.csv`"),
    ("F69", ".temp/php27/streamsfuncs.c"): (
        VERDICT_NOTDEP, "⚠ FALSE POSITIVE, same shape: one of the five files "
        "`ph73` spans, in a parenthesised list of upstream sources"),
    ("F147", ".temp/php27/streamsfuncs.c"): (
        VERDICT_NOTDEP, "cited AS the example of the rule being FOLLOWED -- "
        "PHP 5.0.0 source, re-derivable from `php-5.0.0.manifest`"),
    ("F70", ".temp/mgr168/item48_decide.py"): (
        VERDICT_RESTS, "F69's `29 of 30 at file:line` and `24 of 30 by "
        "enclosing function` -- the measurement that DECIDED item 48 -- are "
        "this probe's output, and its must-fires go with it"),
    ("F72", ".temp/mgr169/ph29_predict.py"): (
        VERDICT_RESTS, "the six published prediction numbers (spellings 4->12, "
        "pairs 12->36, present 0->22, ...) are its output, and the finding "
        "calls them `the falsifiable prediction`"),
    ("F73", ".temp/mgr169/charlit_reach.py"): (
        VERDICT_RESTS, "the headline `0 of 33 PAT AND 0 of 6 PHP` is its "
        "output; its 6 must-fire negatives and its DIFFERENTIAL design are the "
        "reason the headline is believable, and both are gitignored"),
    ("F74", ".temp/mgr170/spread_stat.py"): (
        VERDICT_RESTS, "one of the three probes the finding names as settling "
        "item 52; the six-statistics-in-two-families table is their output"),
    ("F74", ".temp/mgr170/callee_share.py"): (
        VERDICT_RESTS, "as above -- and its sibling `null_control.py` was "
        "PROMOTED while these two were not, which is how the gap survived"),
    ("F85", ".temp/mgr170/callee_share.py"): (
        VERDICT_RESTS, "⛔ THE SHARPEST: F85 is `the programme's central "
        "claim` (29 of 38 sign flips are cross-language) and this is one of "
        "its two named probes"),
    ("F85", ".temp/mgr172/STATISTIC-DECISION-DRAFT.md"): (
        VERDICT_RESTS, "the finding cites `§5` of it by section -- an EVIDENCE "
        "DOCUMENT, not an artefact, and the only home of the derivation"),
    ("F89", ".temp/mgr173/ph64_draws.py"): (
        VERDICT_RESTS, "the `0.07 pp` same-language spread and the N4 control "
        "(`0.034 %` against F88's `0.03 %`) are its output. ⭐ MITIGATED: "
        "`_043` §5.7 reproduced the CONTRAST at 55.6x by a different design, "
        "so the finding survives the loss and the two figures do not"),
    ("F90", ".temp/mgr173/ph64_draws.py"): (
        VERDICT_RESTS, "`ph64_draws.py`'s data RE-SLICED -- the re-slice is the "
        "whole of F90, and it refutes a published recommendation"),
    ("F95", ".temp/php43/samefunc_hole.py"): (
        VERDICT_RESTS, "⭐ THE REVIEWER'S OWN COUNTEREXAMPLE, the artefact that "
        "made my `same_function` guard accept a zero-leading-context hunk. "
        "`law 12`: the reviewer's INDEPENDENCE is the product, and this is the "
        "only copy of it"),
    ("F99", ".temp/php41/probe_wrap.rs"): (
        VERDICT_HISTORY, "in RECAP the finding is ABOUT the citation having "
        "been written into a hashed block -- the file is the subject. ⛔ BUT "
        "SEE F150(c): it is cited LIVE twice inside `ph53/verus.rs`, which is "
        "hashed and which NO checker was reading"),
    ("F100", ".temp/php43/item83_sim.py"): (
        VERDICT_RESTS, "`all six published A1 percentages re-derive to the "
        "digit` is its output, and it drives the row's OWN verdict functions"),
    ("F102", ".temp/mgr176/asanfill.c"): (
        VERDICT_PROMOTED_STALE,
        "⛔⛔ I RULED THIS `RESTS` ON 2026-09-17 AND IT WAS WRONG. The "
        "generator was promoted on 2026-09-13 as `.tasks-php/asan_fill_byte.c` "
        "-- 85 lines, fuller header, cited as COMMITTED at "
        "`TASK_PHP_045.md:90`. F102 needs a REPOINT, not a promotion. "
        "▶ Caught by `TASK_PHP_064`'s engineer, against my brief"),

    # ⭐⭐ AND THESE FOUR ARE THE ARM CATCHING ITS OWN AUTHOR, ON THE FIRST TRY.
    # Writing F150 and F151 -- the findings that REPORT this adjudication --
    # put four fresh `.temp/` citations inside published finding sections, and
    # `N20` went red before the commit. ▶ A finding ABOUT a citation quotes the
    # citation; that is unavoidable and it is why the verdict must be RECORDED
    # rather than assumed. `F131`: the ruling is keyed on the citation, so a
    # new one is a new question even when the file already has an answer
    # elsewhere.
    ("F150", ".temp/mgr176/asanfill.c"): (
        VERDICT_HISTORY, "F150 quotes F102's citation as the EXHIBIT for its "
        "central point (`generator kept` in a gitignored directory). The file "
        "is the subject; F102's own row above is where the debt is recorded"),
    ("F150", ".temp/php27/streamsfuncs.c"): (
        VERDICT_NOTDEP, "named as the false positive it is -- still upstream "
        "source, still re-derivable from the manifest"),
    ("F150", ".temp/mgr166/asan_reach.c"): (
        VERDICT_HISTORY, "quoted to show the same FILE ruling two ways under "
        "two findings; the debt is booked once, against F50"),
    ("F150", ".temp/mgr165/REFETCH.sh"): (
        VERDICT_HISTORY, "F150 names it as the EXHIBIT for `keep the generator "
        "and never say where` -- a regenerator named in a finding's own "
        "sentence that could not regenerate anything from a clean checkout. "
        "⭐ It replaced `asanfill.c`, which I had picked for how well it read "
        "and which turned out to be the one case that REFUTES the lesson. The "
        "debt itself is discharged: promoted as `probes/refetch_f50_census.sh`"),
    ("F151", ".temp/php41/probe_wrap.rs"): (
        VERDICT_HISTORY, "F151 is ABOUT this citation being unscanned inside "
        "`ph53/verus.rs`. ▶ The DEBT is open item 152 (a re-gate), not a "
        "promotion -- the file is a subject here and a hashed pointer there"),
}


def adjudicate(finding, cite):
    """PURE. The ruling for one law-11 row, or `None` if nobody has ruled.

    ⭐ SPLIT OUT SO THE ARM CAN PLANT ITS OWN INPUT -- the same reason
    `_section_of` is split out, and for the same failure it prevents.
    """
    return ADJUDICATION.get((finding, cite))


def unadjudicated(rows):
    """PURE. Law-11 rows with no ruling. ⛔ THIS, NOT A COUNT, IS THE ARM.

    An arm asserting `17 RESTS` would go RED the day the promotions land, i.e.
    the day the work is DONE -- `F147`'s sibling lesson, and the trap this file
    already dodged once in `_section_of`. What must never happen is a NEW
    citation appearing inside a published finding with nobody having read it.
    """
    return [r for r in rows if adjudicate(r["finding"], r["cite"]) is None]


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

    # ⛔ THE RULING (item 148). REPORTED, never asserted -- the tally moves as
    # the promotions land, and an arm pinned to it would go red on success.
    tally = {}
    for r in pfd:
        a = adjudicate(r["finding"], r["cite"])
        tally.setdefault(a[0] if a else "⛔ UNADJUDICATED", []).append(r)
    print(f"\n  {'ruling':10}     item 148, by unit text -- "
          f"{len(pfd)} citation(s) ruled on")
    for v in (VERDICT_RESTS, VERDICT_HISTORY, VERDICT_NOTDEP,
              VERDICT_PROMOTED_STALE, "⛔ UNADJUDICATED"):
        sel = tally.get(v, [])
        if not sel and v != VERDICT_RESTS:
            continue
        files = sorted({r["cite"] for r in sel})
        finds = sorted({r["finding"] for r in sel}, key=lambda x: int(x[1:]))
        print(f"    {v:16} {len(sel):3} citation(s)  "
              f"{len(files):2} file(s)  {len(finds):2} finding(s)")
        if v == VERDICT_RESTS:
            print(f"      ▶ LAW-11 DEFECTS -- promote or re-ground: "
                  f"{' '.join(finds)}")
        for r in sel:
            print(f"        {r['finding']:<5} {r['cite']}")
    print(f"    ⚠⚠ `RESTS` is a DEFECT and `HISTORY`/`NOTDEP` are NOT. "
          f"Read `ADJUDICATION` for the\n       reason on each row -- "
          f"the verdict is the sentence, not the bucket.")

    un = unadjudicated(pfd)
    if un:
        print(f"\n  ⛔⛔ {len(un)} law-11 citation(s) NOBODY HAS RULED ON:")
        for r in un:
            print(f"      {r['finding']:<5} {r['doc']}:{r['line']} {r['cite']}")
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

    # ---- the ADJUDICATION (item 148) -------------------------------------
    # ⛔ THE ARM IS COVERAGE, NOT CARDINALITY. `17 RESTS` would go RED the day
    #   the promotions land -- the day the work is DONE. What must never pass
    #   silently is a NEW citation inside a published finding that nobody read.
    synth = [
        {"finding": "F102", "cite": ".temp/mgr176/asanfill.c",
         "doc": "RECAP_PHP.md", "line": 1},
        {"finding": "F999", "cite": ".temp/zzz/brand_new_probe.py",
         "doc": "RECAP_PHP.md", "line": 2},
    ]
    chk("N19", [r["finding"] for r in unadjudicated(synth)], ["F999"],
        "⛔ an UNRULED law-11 citation is caught, and a ruled one is not -- "
        "asserted on PLANTED rows so the arm does not depend on the live "
        "backlog being empty or full")
    chk("N20", unadjudicated(pfd := published_finding_deps()) == [], True,
        "every law-11 citation in the LIVE tree has a ruling (item 148 done)")
    chk("N21", adjudicate("F59", ".temp/php27/streamsfuncs.c")[0], VERDICT_NOTDEP,
        "⭐ the bare-name resolver's FALSE POSITIVE is ruled NOTDEP, not "
        "quietly dropped -- a census row is a QUESTION and `no` is an answer")
    chk("N22", adjudicate("F50", ".temp/mgr166/asan_reach.c")[0] !=
        adjudicate("F52", ".temp/mgr166/asan_reach.c")[0], True,
        "⛔⛔ THE SAME FILE RULES DIFFERENTLY UNDER TWO FINDINGS -- if the key "
        "were the FILE the ruling would be wrong for one of them (`F131`)")
    chk("N23", sorted({v[0] for v in ADJUDICATION.values()}),
        sorted([VERDICT_HISTORY, VERDICT_NOTDEP, VERDICT_PROMOTED_STALE,
                VERDICT_RESTS]),
        "all four verdicts are USED -- a table that only ever says `defect` "
        "is an accusation, not an adjudication (`F21`/`F37`)")
    chk("N26", adjudicate("F102", ".temp/mgr176/asanfill.c")[0],
        VERDICT_PROMOTED_STALE,
        "⛔ THE ONE I GOT WRONG: a promotion that RENAMED the file is "
        "invisible to a basename resolver, so the census said LIVE and I "
        "ruled `RESTS`. A repoint, not a promotion -- and the arm pins the "
        "correction so it cannot quietly revert")
    chk("N24", all(len(w) > 40 for _, w in ADJUDICATION.values()), True,
        "every ruling carries a REASON in the citing sentence's own terms, "
        "because the verdict is the sentence and not the bucket")
    chk("N25", len({f for f, _ in ADJUDICATION}) >= 13, True,
        "the ruling spans the findings it claims to -- non-vacuous")

    print("\nSELFTEST " + ("PASS" if not fails else f"FAIL ({len(fails)})"))
    for f in fails:
        print("   " + f)
    return 1 if fails else 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    report()
    sys.exit(0)
