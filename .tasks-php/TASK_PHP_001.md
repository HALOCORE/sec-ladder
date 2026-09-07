# TASK_PHP_001 — Phase 1 mining wave: candidate patterns from PHP 5.0.0 C

**Role:** research engineer ×3, read-only, in parallel.
**Launched:** 2026-09-07. **Reports:** `TASK_PHP_001_REPORT_{TEMPORAL,SPATIAL,TYPE}.md`.

> ⚠⚠ **DISCLOSURE, AND IT MATTERS FOR AUDITABILITY: THIS SPEC WAS WRITTEN AFTER
> THE THREE AGENTS WERE LAUNCHED, NOT BEFORE.** The `.tasks-php/` convention was
> adopted mid-session, on the user's instruction, while the wave was already
> running. **This file is a faithful transcription of the prompts actually sent,
> not a reconstruction of what they should have said** — the prompts are the
> authority and this is the record of them. Every later task file in this
> programme is written **before** its agent starts, per `PROTOCOL.md`.

## Why three agents in parallel

Mining is **read-only code reading** over another repository. The user's standing
concurrency rule: **up to 3 agents in parallel for investigation/mining/reading;
exactly 1 at a time for construction and review** (`PLAN_PHP.md` `DP-09`). This
wave is the read-only case. Adjudicating its output into
`patterns-php/CATALOGUE.md` is the construction case and is serial.

## Scope — one axis each

| agent | axis | CWEs | corpus rows |
|---|---|---|--:|
| A | **temporal** | 416 · 401 · 562 · 590 · 415 · 911 · 824 | ~85 |
| B | **spatial** | 125 · 787 · 190 | ~47 |
| C | **type / init** | 843 · 476 · 664 · 908 · 822 · 457 | ~34 |

## The bar, given to all three verbatim

Admission is **C-SIDE ONLY**: (1) correct on benign inputs, (2) exhibits the
error on ≥1 adversarial input, (3) fits *flat blob in, `u64` out* — noting that a
structure **may** live inside the kernel driven by an opcode stream (`p27` holds
32 raw pointers that way).

⚠⚠⚠ **Nothing about Rust, Verus, Miri, cost gradients or what the ladder can
"price" may EVER remove a candidate.** All such observations are **findings**.
Each agent was told the PAT programme lost six admissible rows to exactly that
bias, and that the bias survived because it lived in the bar rather than in any
row, where row-level review could not see it.

⚠ **Duplication is not a filter** — neither against `patterns/` nor within
`patterns-php/`; slight variations are separate candidates (`DP-03`).

## Sources, and the pin

Citation base **PHP 5.0.0 only** (`DP-06`), against the pristine museum tarball:

```
sha256 5783e0c0ba94f165633a565fe73a83e59cf17b6880ef95fa8f936dc6301d6919
size   5595997 bytes    entries 3815
path   php-in-safe-rust/.app-tests/.temp/oracle/build-5.0.0/php-5.0.0.tar.gz
read   tar -xzOf <tarball> php-5.0.0/<path> | sed -n '<a>,<b>p'
```

All three were warned that **every extracted tree on this box is patched**
(modern-gcc, and in two cases the allocator), that a `c_file_line` that does not
resolve in the pristine tarball is a **finding to record, not to silently fix**,
and that a previous effort published citations from a patched tree and retracted.

Also supplied: `index.csv` (166 root causes with `fix_commit` and reproducer),
`invariants-166.json` + `invariants-list.md` (blind-labelled, T1/T2/T3), and
`.temp/san_tests/` (123 ASan reports from real page renders — frequency evidence).

**`php-rust/` was placed explicitly out of bounds** (`DP-05`). So were
`RECAP*.md`, `PLAN*.md` and `.memory/`, because the manager was editing them
concurrently — `PROTOCOL.md` rule 11.

## Deliverables

Per agent, into `.temp/php-mine/<axis>/`: `candidates.json` (schema in the
prompt — provenance, mechanism read from the source, benign behaviour,
adversarial trigger, self-containment tier, blob-drivability, hotness,
distinctness, risks), `NOTES.md` (mechanism **families**, rejected rows with the
**C-side** reason, corrected citations), `VERIFY.md` (top 5, with the actual
`tar … | sed` command and its output pasted).

Target **8–15 candidates each**, ranked, **breadth of mechanism over depth**.

Axis-specific asks: B flags `ptr_cursor: true` where the mechanism is a pointer
walk rather than an index compare (`DP-07`, census finding 45 — 2nd/3rd most
frequent bound operator in all 22 census programs, **zero** in all 33 PAT
kernels) and must answer `emalloc_dependent` for every sizing candidate
(`PLAN_PHP.md` §4.3). C must paste the `zval` / accessor-macro substrate verbatim
and label each candidate's harm limb `silent-wrong-value` / `wild-pointer-deref`
/ `both`.

## The calls the manager named for refutation

`PROTOCOL.md` rule 2 — each agent was given one manager belief **by name** and
asked to measure it:

| agent | the claim it was asked to refute |
|---|---|
| A | *"the CWE-416 mass in `zend_execute.c` collapses to only 3–5 distinct C mechanisms, most requiring the whole executor and rating `modelled`"* |
| B | *"`formatted_print.c` is the densest site (four root causes in one function) and therefore the best spatial candidate"* |
| C | *"the 11 CWE-843 rows are ONE mechanism at eleven sites, and the CoW / reference-separation rows are a genuinely different second mechanism"* |

---

**Running count for this programme: launched from 0.** It is a rigour signal,
not a ledger, and must never be added to the PAT programme's ≈965 —
they measure different things. Reconciliation is the **manager's** job at the
commit that lands these three reports, not any agent's.
