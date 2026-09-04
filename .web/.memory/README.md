# `.web/.memory/` — this agent's memory, in the repo

**Agent memory for `.web/` work lives here, not in `~/.claude/…/memory/`.**
See `../CLAUDE.md` rule 9 for why.

One fact per file, same shape the harness memory uses so nothing is lost in the
move:

```markdown
---
name: <short-kebab-case-slug>
description: <one line, used to decide relevance when scanning>
metadata:
  type: user | feedback | project | reference
---

<the fact.  For feedback/project, follow with **Why:** and **How to apply:**.
Link related notes with [[their-name]].>
```

## What belongs here, and what does not

| | |
|---|---|
| **here** | how the *user* wants this work done: preferences, corrections, standing decisions, pointers to things outside the repo |
| **`../RECAP.md`** | the state of the app — what is built, what is owed, the traps. The handover. |
| **`../CLAUDE.md`** | the rules for editing `.web/` |
| **`../../.memory/` 00–06** | ⚠ **NOT OURS.** That is the research project's authoritative findings layer, written by the researcher agents under `PROTOCOL.md` rule 9, and `.web/` never writes outside itself. |

If a note is about the app rather than about the user, it belongs in `RECAP.md`.

## The index

- [Report style](web-report-style.md) — take template_apps' framework, not its dark CSS.
- [Script-guarded notes](script-guarded-notes.md) — prose attached to assertions, withheld when the evidence moves.
- [Division of labour](division-of-labour.md) — I own `.web/`; the tree above is read-only and moves under me.
- [Paper writing process](paper-writing-process.md) — the sub-agent roles behind ver_A and ver_B, and the nine things that decided their quality: ground on primary artefacts, run reviewers blind so their contradictions surface, and check the supervisor's own rulings too.
