---
name: script-guarded-notes
description: "The user's mechanism for prose that cannot go stale: notes attached to assertions, withheld and reported when the evidence moves"
metadata:
  type: feedback
---

The user proposed this and named it: **script-guarded insights/notes**. Prose
that makes a claim about live research does not get to be a bare string. It
lives in a script (`.web/insights/insight_*.py`) **attached to assertions**, and
is emitted only while every assertion still holds. A failing guard withholds the
note and exits non-zero; the build turns that into a warning the page renders.

**Why:** a hard-coded sentence stays confidently wrong forever. A guarded one
stops being displayed the moment its evidence moves and tells you which sentence
to rewrite. The research tree it describes changes under the report.

**How to apply:** put the *generator* in a committed directory and its *output*
in the derived one — the user's first sketch put the script under `data/`, which
is gitignored and rebuilt, so it would have been deleted. Guard against the
primary evidence (`results/`, source files), never against the derived data the
note itself came from, or the check is circular.

It earned itself immediately: a note broadcast to all patterns **declined to
apply to p36**, whose kernels are not byte-identical, with nobody having encoded
that exception.

The same instinct generalises — the user also asked for **graded confidence over
all-or-nothing refusal** on the assembly line map (certain / likely /
approximate). Refusing whole pairs was discarding 97–99% good data. But grading
is only honest if the weak tier is *labelled*: a positional-pairing signal that
could not survive being labelled was correctly dropped as noise. See
[[web-report-app]].
