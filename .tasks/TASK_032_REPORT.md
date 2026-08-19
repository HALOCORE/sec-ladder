# TASK_032 — report

Engineer's return message, recorded by the manager. Scratch `.temp/p32/` (1.4 M,
46 files, all text). **The methodology arc closes here.**

## Did

| path | what |
|---|---|
| `common/layout/` (**new**, 1327 lines + `README.md`) | `loopfit.py` (mechanism + `jcc.py`'s address/`md5_fn_norel` half; the "tightest backward branch" heuristic **not** ported), `layout_gen.py` (population builder, **ordering bug fixed**), `order.py`, `predict_then_time.py`, plus `analyze.py`, `survives.py`, `q3_convergence.py`, `modesim2.py`. `__file__`-derived paths, default `--out .temp/layout`, each deletes its own build scratch. |
| `common/layout/data/` | **one addition beyond the task's list, flagged**: p01's fixed-builder population + the pre-registration + its outcome (69 K). Matched by **no** `source_sha256` glob (verified), so zero gate cost. |
| `harness/check.py` | exactly two edits — `srcs` glob `+ common/layout/*.py`, and `head("3c. … (recorded as a result AND enforced)")`. 12 insertions / 1 deletion. |
| `p01/NOTES.md` §3b, `README.md` | hedge removed, replaced with the re-measurement (rule 9). |

**The fix** is `layout_gen.round_robin(keys)`; `order.py` and
`predict_then_time.py` **import** it rather than re-implement, so the probe tests
the shipped scheduler.

## Evidence

### Item 1 — the fix, on 31 byte-identical copies of p05 (`small`, one layout, 2 passes, 3 schedules)

```
  schedule alt first six cells ['safe_naive','safe_tuned','unsafe','safe_naive','safe_tuned','unsafe']
  schedule blk first six cells ['safe_naive','safe_naive','safe_naive','safe_naive','safe_naive','safe_naive']
  schedule gen first six cells ['safe_naive','safe_tuned','unsafe','safe_naive','safe_tuned','unsafe']

--- pass 0  order alt  ALTERNATING (harness/measure.py) ---
  R2 vs R4 (medians)  +30.31%     R3 vs R4 (medians)   +4.22%
--- pass 0  order blk  BLOCKED (the bug) ---
  safe_naive median 6.291 ms  NOISE FLOOR 21.03%  copy#0 7.426 ms  rank 30/30
  R2 vs R4 (medians)   +7.56%     R3 vs R4 (medians)   -0.09%
--- pass 0  order gen  layout_gen.round_robin (SHIPPED) ---
  safe_naive median 6.945 ms  NOISE FLOOR  6.15%  copy#0 6.900 ms  rank 9/30
  R2 vs R4 (medians)  +30.08%     R3 vs R4 (medians)   +3.92%
```

Pass 1 the same (alt +30.07/+4.15, gen +30.25/+3.46, blk +7.93/+0.36; blk slot-0
rank 29/30). **`gen ≡ alt`.** Blocked order costs **22 points on R2**, removes
R3's sign, and puts slot 0 — where a "shipped" build lands — at rank 30/30 and
29/30 of 31 *identical* copies. That is TASK_030_REVIEW blocker 2, manufactured.

### Item 2 — THE MODE SURVIVES

p01, 30 layouts + shipped, 31 reps, 2 passes, `small` + `large`, fixed builder:

```
pattern in    rung         published   pooled    mode0   mode16  P(A>B)  verdict
p01    small safe_naive      +5.40%   +0.60%   +5.80%   -3.61%   60.8%  SIGN FLIPS
p01    small safe_tuned      +4.72%   +1.58%   +7.10%   -5.45%   66.1%  SIGN FLIPS
p01    large safe_naive      +0.54%   +0.12%   +0.17%   +0.08%   66.8%  gap < 1% either way
p01    large safe_tuned      +0.06%   +0.02%   +0.07%   +0.06%   54.9%  gap < 1% either way
```

TASK_031 (blocked) had `+5.24 / −4.10` and `+7.01 / −5.67`. **Every number moves
by ≤0.6 points; no sign moves.** Pass 2 independently `+5.14 / −4.04`,
`+6.92 / −5.44`. Three further ways:

- **Inside one lever**, so composition cannot contribute: `order`-only R2
  `+5.14 / −3.61` (n = 8/6, 13/15), R3 `+7.22 / −5.55`; `align`-only
  `+6.12 / −5.92`, `+6.80 / −4.31`.
- **Mechanism**, `win32[1,2]` on the 30-byte SSE loop, PERFECT on all three rungs
  and both passes: `×1.0494/×1.0463` (R2), `×1.0831/×1.0798` (R3),
  `×1.0459/×1.0471` (R4). Cross-pass Spearman ρ **+0.944 / +0.902 / +0.883** on
  `small`; on `large` +0.29 / −0.13 / −0.02 (noise, as it should be).
- **Fresh out-of-sample pre-registration with the fixed timer**, hash printed
  before any timing (`5c5c2a8c…b155eb4a9`), 20 orderings, **one** directional rule
  `win32@0` with no per-rung tuning: `PREDICTION HELD (perfect separation)` on all
  three rungs, both passes — ×1.0628/×1.0633, ×1.0565/×1.0533, ×1.0411/×1.0432.
  Strictly stronger than TASK_031's, which used `bit4` with the direction fitted
  per rung. `data/predictions_p01oos.json`'s **own file sha256 is that hash**.

p07 not re-run, as instructed.

### Gates — all seven, sequential, foreground

```
p01b  PASS-WITH-BLOCKED-ROWS      p07  PASS      p02  PASS      p05  PASS
p08   PASS                        p16  PASS      p17  PASS
242 pinned entries, 0 stale        (was 186; +7×8 layout files)
load-bearing keys moved: 0        65 source_sha256 leaves, 11 text/diagnostic
all seven tables regenerate byte-identically
```

`results/*.json` — where the published `md5_fn`, `n_fn` and `Ir` live — is
**byte-unchanged** (`measure.py` not run). Full sweep cost **15m44s** (p01 5m37s
from Miri's two 180 s timeouts; the other six 1m23s–2m20s), i.e. the top of the
10–15 min estimate rather than inside it.

### Churn class, re-measured

**9** ASan PID/ASLR strings (TASK_031 recorded 18); p05's **2**
`adversarial-dims` stdouts; p08 `marginal_ir_per_call` **0 of 96 marginal keys
moved** — also 0 on p02 and p05. **The series 8 → 23 → 75 gains a fourth entry,
0.** Intermittent, not a growing per-run cost; budget "0…75".

## Problems

- **Second instance of the ordering bug**, not in the task file:
  `.temp/r30/predict_then_time.py:133` had the same `for k, b in bins.items()`.
  TASK_031 listed it under "not checked"; it *was* blocked. Fixed in the shipped
  copy.
- **The protocol control now covers all seven patterns** (~8 min), which nobody
  had asked for:

  | pattern | alternating | blocked | identical-copy floor | sensitive? |
  |---|---|---|---|---|
  | p02 R2 | +17.35 / +16.69% | +17.12 / +16.43% | 1.0–3.4% | no |
  | **p05 R2** | **+30.31 / +30.07%** | **+7.56 / +7.93%** | 4.2–21.0% | **YES** |
  | p08 R2 | +104.72 / +105.44% | +104.64 / +104.82% | 0.58–1.30% | no |
  | p16 R2 | −0.15 / −0.25% | −0.13 / −0.20% | 0.61–1.50% | no |
  | p17 R2 | −0.18 / +0.05% | −0.03 / +0.04% | 0.55–1.00% | no |

  **p05 is the only protocol-sensitive pattern and its row is already withdrawn**,
  so the bug reached no surviving published verdict. p16's and p17's
  "gap < 1% either way" are clean negatives under both protocols — not previously
  established.
- p05's *alternating* identical-copy floor is **4.19–14.83%**, not the
  5.09–45.04% `.memory/03-measurement.md` quoted — that figure was the max over
  blocked *and* alternating blocks together. p05's withdrawal stands (its band
  14.09/8.30/9.34% is inside 4.2–14.8%); the table row overstated by mixing
  protocols.

## Item 3 — the third option

**The manager's framing has a false premise, and it is measurable.**
`source_sha256` is written by `check.py:4805` and **nothing compares it to the
tree**; `.memory/02-bench-rules.md:762` says "at least *detectable*". An edit to a
hashed file fails no gate — it leaves seven records disagreeing with the tree
until the next sweep. The tax is also per **edit event**, not per file: shipping 8
files costs what shipping 4 costs, and batching N edits into one sweep costs one
sweep. And a change to `common/layout/*.py` cannot invalidate anything *in* a gate
record (the gate never imports it) — only a claim in a pattern's `NOTES.md`, which
`glob(pdir/*.md)` already hashes.

**So the real hole is not where the `.py` files live — it is that shipping the
tool without the data leaves finding 16 reproducible but not auditable.** `.temp/`
is gitignored and has been swept once; nobody could check that `+5.80 / −3.61%`
came from the numbers claimed without ten minutes of measurement.
`layout_p01.json` is 48 K. Committed under `common/layout/data/` — matched by no
glob, **zero** gate runs — and
`python3 common/layout/survives.py --dir common/layout/data p01` now reproduces
the published table with no measurement at all. Once the data is the reproduction
path, the hash on the tool stops being load-bearing.

**Keep the glob as specified (done).** Blocker on doing the same for the other
six: `.temp/r30/layout_p*.json` were all produced by the blocked builder and their
cross-rung columns inherit an error measured at up to 22 points. **They must not
be committed as evidence.**

## Unsure / not done

- **Dangling `.temp/` citations in committed prose** — adjacent, out of scope:
  `p07/NOTES.md:1274,1307,1310,1331,1443` and `p05/NOTES.md:554,565,568,569,578,
  579,600` cite `.temp/{r30,p31}/`. Repointing at `common/layout/` costs a p05 and
  a p07 gate run. p01's were repointed since its gate was already re-running.
- **`predict_then_time.py`'s rule syntax changed** (`win32@N` / `jcc32@N`, loop
  index required) because the old `n_hit_loop` field came from the banned
  heuristic. Old pre-registration hashes in `.temp/r30/` are historical and not
  reproducible by the shipped script.
- `q3_convergence.py`, `survives.py`, `analyze.py` still mode-match by the
  `addr % 32` **proxy** (labelled as such in each docstring); only `loopfit.py`
  and `analyze.py`'s geometry section use `win32`/`jcc32` directly. A
  `--partition win32@N` option is the obvious improvement, not added.
- No C or R5 layout sweep; six unbracketed `ns` cells per pattern remain.
- `.temp/build` and `.temp/check` left alone (shared caches, manager's call).

## Memory updates

None written (forbidden). Landed by the manager: item 2's resolution and the
hedge removal, the p05 noise-floor correction, the p08 jitter series gaining a
`0`, the seven-pattern protocol-sensitivity table, the measured 15m44s sweep cost,
and — in `.memory/02-bench-rules.md` — the fact that `source_sha256` staleness is
detectable only by hand, with the one-line checker (run at landing: **0 stale
across 242 entries**).
