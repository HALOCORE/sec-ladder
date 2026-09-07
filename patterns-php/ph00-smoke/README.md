# `ph00-smoke` — the pipeline's own smoke test

⚠⚠⚠ **NOT A PHP ROW. NOT A RESULT. DELETE ONCE A REAL PHP ROW IS GREEN.**

A byte-for-byte relocation of `patterns/p01-array-sum/` — window sum over a
`u64` array, wrapping addition — landed at `TASK_PHP_002` for exactly one
purpose: to prove that the **unmodified** PAT gate runs green out of the
symlink shim `.temp/php-root/` and writes its record into `results-php/gate/`.

It models no bug, prices nothing, carries no security claim and has **no PHP
provenance**. Its `provenance` block declares `php_provenance: false` with a
`why`, and `harness-php/provenance.py` accepts it only because of that.

## Running it

```sh
python3 harness-php/gate.py --tool measure ph00     # the full matrix
python3 harness-php/gate.py --tool report  ph00     # results-php/tables/ph00-smoke.md
python3 harness-php/gate.py               ph00     # the gate
```

Three commands, not two: `report.py` renders from **`measure.py`'s** record
(`results-php/ph00-*.json`) and exits without it, while the gate's stage 9
fails if `results-php/tables/ph00-smoke.md` is absent. `harness/check.py`'s
own stage-9 `MISSING` message spells this out at length.

## What it does and does not certify

| ✅ certifies | ❌ does not certify |
|---|---|
| the shim resolves and the real harness runs out of it | anything about PHP |
| the gate writes to `results-php/`, never `results/` | anything about a defect |
| `common-php/` re-exports resolve through `common -> common-php` | that a php row's extraction is faithful |
| `results-php/tables/` renders and stage 9c is satisfiable | any number worth publishing |

⚠ **Its `Ir` is not comparable to `p01`'s.** `check.py::_env_block` records
`repo_path_bytes = len(REPO)`, which is 20 bytes longer through the shim, and
the gate's own `domain` string makes an equal `repo_path_bytes` a necessary
condition for comparing two records. See `NOTES.md`.

The kernel contract, the rungs and every pin are the original's. Read
`patterns/p01-array-sum/` for what they mean; **do not edit that directory.**
