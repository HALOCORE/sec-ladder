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

⚠⚠ **SIX COMMANDS, ~28 MINUTES.** This section said *"Three commands, not
two"* and listed three; **the very task that landed it had measured six**, and
a reader following it on the first real php row would get the sequence that
task proved wrong (`TASK_PHP_003` M4, corrected at `TASK_PHP_004`).

```sh
python3 harness-php/gate.py --tool build   ph00 --all   # 1. the 28 binaries
python3 harness-php/gate.py --tool measure ph00         # 2. the full matrix
python3 harness-php/gate.py --tool report  ph00         # 3. the table exists
python3 harness-php/gate.py                ph00         # 4. FAILS on tables
python3 harness-php/gate.py --tool report  ph00         # 5. re-render
python3 harness-php/gate.py                ph00         # 6. green
```

- **Step 1 is not optional.** `measure.py` **builds nothing** — it measures
  whatever binaries are in the build root. `TASK_PHP_002`'s first `measure`
  run reported `static: 1 cells` and wrote a one-cell record without
  complaining.
- **Steps 4→6 are the irreducible `gate → report → gate` chain.** `report.py`
  renders its audit section from `results-php/gate/ph00-smoke.json`, which
  does not exist until a gate has run, and the gate's stage 9c compares the
  published table against a fresh render of **this run's** record — so the
  first gate on a new row *must* fail with `[tables] … cites no
  contract_sha256 at all`.
- `check.py::check_published_tables`'s own *"three commands, not two"* message
  is about a **different** case: a row with no measurement record at all.
  Both are true; six is the figure to plan against.

## What it does and does not certify

| ✅ certifies | ❌ does not certify |
|---|---|
| the shim resolves and the real harness runs out of it | anything about PHP |
| the gate writes to `results-php/`, never `results/` | anything about a defect |
| `common-php/` re-exports resolve through `common -> common-php` | that a php row's extraction is faithful |
| `results-php/tables/` renders and stage 9c is satisfiable | any number worth publishing |

⚠ **Its `Ir` is not comparable to `p01`'s, and TWO domain terms move, not
one.** `check.py`'s `domain` string requires the same `repo_path_bytes`, the
same `envp_stack_bytes` **and** the same `tuning_vars`. This line said **20**
and was wrong (`TASK_PHP_003` M1); the corrected figures:

| term | `p01` | `ph00` | comes from |
|---|--:|--:|---|
| `repo_path_bytes` | 33 | 48 | **+15**, `/.temp/php-root` — a property of the tree, and the only stable one |
| `nvars` | 48 | 49 | **+1**, `harness-php/gate.py`'s `PYTHONDONTWRITEBYTECODE=1` |
| `envp_stack_bytes` | 3653 | 3686 → **3695** | **+34** from that variable (measured), **plus whatever the two invoking shells differ by** |

⚠⚠ **`envp_stack_bytes` is not stable across sessions**: `ph00`'s own value
moved **3686 → 3695** between two runs of the same gate with no source change,
so the p01→ph00 delta was `+33` at `TASK_PHP_003` and is `+42` now. **The
variable itself costs exactly +34** — `len("PYTHONDONTWRITEBYTECODE=1") + NUL
+ one 8-byte envp slot` — measured at `TASK_PHP_004`. So the mitigation for the
`__pycache__` escape is itself a second domain violation, shortening the shim
path would *not* make the records comparable, and **two php runs are not
comparable to each other either unless the shell is byte-identical.** See
`NOTES.md`.

The kernel contract, the rungs and every pin are the original's. Read
`patterns/p01-array-sum/` for what they mean; **do not edit that directory.**
