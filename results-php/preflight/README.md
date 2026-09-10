# `results-php/preflight/` — what is in here, and why four files look like bugs

**Read this before deleting anything in this directory.** Four of the files here
are artefacts of a known, open defect and are **kept deliberately as its only
evidence**. `RECAP_PHP.md` **open item 42** (finding **F55**) is the item.

## What the records are

`harness-php/gate.py` appends a run record per invocation:
`<key>.preflight.json` carries the `harness-php/*.py` hashes, the manifest hash,
whether `--no-provenance` was used, and the `gate_argv`. ⚠ **Nothing hashes these
files** — they are an **audit trail**, not a pin (open item 13). The gate itself
reads `results-php/gate/`.

⚠ The sibling `<key>.when.json` holds only the timestamp, split out so the record
proper does not churn (open item 18: measured — `sha256(rest)` is identical
across runs and **only `when` moves**).

## ⚠⚠ THE KEY IS THE STRING YOU TYPED, NOT THE ROW THAT RAN — F55 / item 42

`harness-php/` resolves an abbreviated row name through `glob(<row>*)` for **the
work** and then keys the record on **what you typed**. So `gate.py ph07` operates
on `ph07-strcut-cursor` and **writes its history to a different file**. The
result, with run counts:

| file | runs | what it is |
|---|---:|---|
| `_norow.preflight.json` | 16 | ⭐ **NOT a stray.** The record of **row-less** invocations. ✅ Verified: **all 16** `gate_argv` are `['--tool','measure','--check-stale']` — the staleness bracket **every php task file mandates twice**. `row: None` with the highest run count in the directory reads like a bug and **is not one** |
| `ph00-smoke.preflight.json` | 1 | the real row |
| `ph00.preflight.json` | 12 | ⚠ **stray — and it has 12× the real row's history.** Committed since `TASK_PHP_010` |
| `ph07-strcut-cursor.preflight.json` | 16 | the real row |
| `ph07.preflight.json` | 4 | ⚠ stray |
| `ph03-uudecode-bound.preflight.json` | 10 | the real row |
| `ph16-fdset-index.preflight.json` | 10 | the real row |
| `ph29-recvfrom-alloc.preflight.json` | 7 | the real row |
| `ph29.preflight.json` | 1 | ⚠ stray — **the manager's, and the engineer caught it, not the manager** |

*(Counts are as of 2026-09-10 and grow with use; the **structure** is the point,
not the numbers.)*

## ✅ DECIDED 2026-09-10: KEEP ALL FOUR STRAYS

Three reasons, and the third is the one that changed the answer:

1. **The fix needs a control that types both spellings and asserts one file** —
   `PROTOCOL_PHP.md` §H, so it is not a one-liner. **These four are the only
   extant instances of the defect.** Deleting the evidence before the control
   exists is how a defect comes back.
2. **They are not rule-1 artefacts.** `CLAUDE.md` rule 1 says keep the generator
   and delete the artefact — but **a run history is re-derivable by no script**,
   so it is evidence, and evidence stays.
3. **The directory was INCONSISTENT** — two strays committed, two untracked —
   **and that is worse than either policy**, because it made the population read
   as two committed accidents rather than four instances of one defect. All four
   are now committed.

## ✅ Nothing published rests on a stray

The gate reads `results-php/gate/`, and `--check-stale` returns the same figures
either way. ⚠ **What the defect costs is the audit trail**, silently split by how
someone happened to type a row name.

## ▶ How to avoid adding a fifth

**Always type the FULL row directory name**: `gate.py ph16-fdset-index`, never
`gate.py ph16`.
