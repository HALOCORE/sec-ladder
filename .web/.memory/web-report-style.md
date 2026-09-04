---
name: web-report-style
description: "User rejects template_apps' dark CSS for research dashboards; style is ours to choose, light-first"
metadata:
  type: feedback
---

When copying `Agentic/_lproc/experiments/template_apps` as a web-app starter, take
the framework (`common.js`, `common.css`, `vendor/`, the JSONML + Incremental DOM
patterns, `index.stdio.py`) but **not its visual style** — the user said its dark
palette "is too dark and not suitable for an interactive research blog/dashboard"
and left the styling to my judgement.

**Why:** these pages are shown to an advisor and to people learning the research;
they read as documents, not as terminal tools.

**How to apply:** write a fresh `index.css`, light-first with a selected dark mode,
and override `common.css`'s `:root` variables so the shared dialog/toast components
inherit the new palette instead of the template's. Used in [[web-report-app]].
