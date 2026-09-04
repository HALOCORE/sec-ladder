---
name: division-of-labour
description: "I own .web/ as the presentation & reporting agent; the research tree above it is read-only and changes under me"
metadata:
  type: project
---

The user set this explicitly: **I am the presentation & reporting agent inside
`.web/`. The tree above it is the researcher agents' live work and is READ-ONLY
to me** — I read it as the data source and never edit it.

**Why:** other agents are extending that tree while I work. `.web/` is now part
of the research repository rather than a separate one, so a clean `git status`
in the parent is NO LONGER the check — my own commits show up there too. The
check is `git status --porcelain -- . ':!.web'`: anything it prints is a file I
should not have touched. It is not theoretical — during one session
`p46-bignum-mac` landed and every gate record grew a `verus_exit_anomalies` key,
both mid-work.

**How to apply:** everything I write goes under `.web/`, including this memory
(`../CLAUDE.md` rule 9). After any run, `git -C .. status --porcelain -- . ':!.web'`
must be empty. Evidence is read from `../results/`, `../results/gate/`
and `../patterns/`; the parent's `.memory/` 00–06 is the researchers'
authoritative findings layer and is not a place for my notes.

Corollary the user has acted on twice: the report must **degrade gracefully when
upstream moves** rather than break — a new pattern appears with a "no write-up
yet" fallback, and an unrecognised gate key becomes one aggregated warning on the
Method tab instead of a crash or silence. See [[script-guarded-notes]].
