# TASK_142 — clear the last two residuals: `p29`'s three `.rs` sources, and the eight undigested control files

**Role: research engineer.** ⚠⚠ **You are the only agent running.** You own
`harness/check.py`, `harness/measure.py` and the records.

⚠ **The build programme is DONE and the tree is green** — 27 patterns,
`25 PASS + 2 PASS-WITH-BLOCKED-ROWS`, 0 failures, `54 records 0 STALE`
(`TASK_141`, manager-verified). **This task is stability, not research. Do not
start anything new.**

Read first: `.tasks/TASK_141_REPORT.md` §6 and its residual list; `RECAP.md`'s
START HERE box and finding **52**; `.memory/03-measurement.md` entries **15–18**;
`.tasks/PROTOCOL.md`.

## Residual 1 — the retracted sentence survives in three `.rs` rung sources

⚠⚠⚠ **`p29` ships a FALSE sentence in three Rust rung sources** —
`unsafe.rs:61` most sharply — the conjunct-count claim `TASK_140` measured
false and `TASK_141` cleared from `spec.md`, the three C files, `README.md` and
`NOTES.md`:

> ~~**`p27`'s read-path safety line needs ONE conjunct; `p29`'s needs TWO.**~~

✅ **ONE CONJUNCT IS ENOUGH.** Two single-conjunct arms score **0 wrong / 0 ASan
lines** with the positive control firing, and one **adds no state** (it widens
`live[]` from a bit to the occupant tag). ✅ **What replaces it, and the row must
NOT read as retracted:** *one source line carries **two bug classes selected by
the input** — a use-after-**free** on leaf victims and an in-bounds
use-after-**recycle** on two-child ones — and the half every detector sees is
the half that **cannot be gated**.*

⚠⚠ **COST, stated so it is not re-scoped: `*.rs` is MEASUREMENT-HASHED, and the
sidecars these files are pinned by must be regenerated — a Verus mutant battery
+ Miri + a second `p29` re-measure, ~40 min.** `TASK_141` left it deliberately
rather than half-land it. ⚠ **Expect `p29`'s measurement record to move on
wall-clock, timestamps and hashes and NOT on `Ir`/`md5`/identity/checksum —
`TASK_141` saw 102 of 1345 leaves move that way. If an `Ir` or identity leaf
moves, STOP: that is not a comment edit.**

## Residual 2 — eight committed control files are in NO digest at all

⚠⚠ **`TASK_141` found EIGHT committed control files (`*.sh`, `*.c`, `*.rs`)
covered by neither the gate digest nor `measurement_sources` — and `p42`'s
`NOTES.md` PUBLISHES NUMBERS FROM TWO OF THEM.**

**First deliverable: re-derive the list and the exposure.** Which files, which
patterns, and which published prose depends on them? ⚠ **The count is
`TASK_141`'s; check it.**

**Then decide and say why**, rather than reflexively widening a glob:

- **Widening a digest costs a sweep** and pulls those files into a hash that
  fires on comment edits.
- **`derived_from_sha256` in a sidecar** is the mechanism the pinned controls
  already use and costs gate re-runs only.
- **Or: the honest do-nothing** — record in `.memory/05-layout.md` that these
  files are outside every digest and that prose citing them is undated.

⚠⚠ **`TASK_141` measured that `controls/*.py` IS already in every gate record's
`source_sha256` (96 entries / 27 records, set == disk) while `controls/*` is in
ZERO measurement records. Re-verify that before choosing** — it decides whether
this is a gate cost or a measure cost.

## Then

Re-gate whatever you touched, `harness/measure.py --check-stale`,
`harness/tools/composition.py --check`, `harness/tools/temp_citations.py`, and
`python3 synthesis/synthesize.py`. ⚠⚠ **`results/SYNTHESIS.md` (CAPITALS) is
HAND-WRITTEN — NEVER regenerate over it.**
⚠ **Read `blocked` out of each RECORD, never `grep` the log.** Expect
`p01 = 1`, `p42 = 1`; **`p42` may legitimately be 2 (environment-selected Miri
slowdown) and that is not a regression.**

## Rules

- `.temp/t142/` for scratch. **You may not edit `.memory/`, `RECAP.md`, or
  `results/SYNTHESIS.md`** — the manager applies those. No `git add`/`git commit`.
- ⚠ **Do not touch `.temp/t136/`, `t137/`, `t139/`, `t140/`, `t141/`** — all are
  cited evidence, and `t141/probe_9c/` is the stage-9c must-fire arm.
- Verus via `./verus_run.py`, single-file mode, never `--cargo`.
- Hand-run sanitisers need `env -u LD_PRELOAD`; never truncate a sanitiser log
  with `head`; every harm probe owes a positive control that must fire.
- No blind process killing; prefer `timeout <N> <cmd>` with a generous timeout.
- ⚠ **If either residual costs more than this file says, STOP AND REPORT rather
  than half-landing it.** The tree is green; leaving it green and reporting a
  cost is strictly better than leaving it half-changed.
- Report to `.tasks/TASK_142_REPORT.md`. **PROTOCOL rule 2: you carry 695.**
