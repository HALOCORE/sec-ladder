#!/usr/bin/env python3
"""Render a paper version to plain markdown, as a reader sees it.

Strips `%%` source comments, resolves `\\num{}` against data/index.json, and
turns the structural markers into headings.  `--level1` cuts each section at its
first `\\subsection`, which is the breadth-first cut the framing exists to have:
that output must read as a finished paper on its own.

Lives in tools/ because the artefact does not survive the task but the generator
must (.web/CLAUDE.md "Don't" rule 5): a draft handed to a cold reader has to be
reproducible, and the --level1 cut is the only mechanical check that ver_E's
breadth-first property actually holds rather than being asserted.

    python3 tools/render_paper.py ver_E            > .temp/verE/DRAFT.md
    python3 tools/render_paper.py ver_E --level1   > .temp/verE/LEVEL1.md
"""
import json
import re
import sys

ver = sys.argv[1] if len(sys.argv) > 1 else "ver_E"
level1 = "--level1" in sys.argv

data = json.load(open("data/index.json"))


def num(path):
    parts = path.split("|")[0].split(".")
    o = data
    for k in parts:
        o = o[k]
    return o


def fmt(m):
    path = m.group(1)
    v = num(path)
    return str(v) if "|" in path else f"{v:,}"


meta = json.load(open(f"paper_vers/{ver}/meta.json"))
print(f"# {meta['title']}\n\n*{meta.get('subtitle','')}*\n")

# Resolve \ref to the SECTION NUMBER the page shows.  This used to expand to
# "the section on x", which doubled every time the prose (rightly) wrote
# "section \ref{...}" -- the scratch draft read "section the section on checks"
# and a reviewer reported it as a defect in the paper.  It was a defect in this
# renderer.  One pre-pass numbers the sections, exactly as paper.js does.
_labels, _sec, _sub = {}, 0, 0
for _line in open(f"paper_vers/{ver}/paper.md"):
    _m = re.match(r"\\input\{(.+?)\}", _line.strip())
    if not _m:
        continue
    for _l in open(f"paper_vers/{ver}/{_m.group(1)}"):
        if _l.startswith("%%"):
            continue
        if _l.startswith("\\section{"):
            _sec += 1; _sub = 0; _cur = str(_sec)
        elif _l.startswith("\\subsection{"):
            _sub += 1; _cur = f"{_sec}.{_sub}"
        elif _l.startswith("\\label{"):
            _lm = re.match(r"\\label\{(.+?)\}", _l.strip())
            if _lm:
                _labels[_lm.group(1)] = _cur

for line in open(f"paper_vers/{ver}/paper.md"):
    m = re.match(r"\\input\{(.+?)\}", line.strip())
    if not m:
        continue
    t = open(f"paper_vers/{ver}/{m.group(1)}").read()
    t = "\n".join(l for l in t.split("\n") if not l.startswith("%%"))
    if level1:
        t = t.split("\\subsection")[0]
    t = re.sub(r"\\num\{(.+?)\}", fmt, t)
    t = re.sub(r"\\section\{(.+?)\}", lambda x: "\n## " + x.group(1), t)
    t = re.sub(r"\\subsection\{(.+?)\}", lambda x: "\n### " + x.group(1), t)
    t = re.sub(r"\\label\{.+?\}", "", t)
    t = re.sub(r"\\ref\{(.+?)\}", lambda m: _labels.get(m.group(1), "??"), t)
    t = re.sub(r"\\src\{(.+?)\}", r"[source: \1]", t)
    t = re.sub(r"\\cite\{(.+?)\}", r"[\1]", t)
    print(re.sub(r"\n{3,}", "\n\n", t).strip() + "\n")
