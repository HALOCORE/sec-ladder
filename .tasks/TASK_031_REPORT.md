# TASK_031 — report

Engineer's return message, recorded by the manager. Scratch `.temp/p31/` (92 K,
all text): `order.py`, `posbias.py`, `derive.py`, `NOTES.md`, 9 `.log`.

**Items 1, 3, 4, 5 landed as specified. Item 2 landed with a corrected diagnosis —
TASK_030_REVIEW's blocker 2 is a harness artefact, reproduced with zero layout
variation.** Item 6 is report-only, at the end.

## Did

| path | what |
|---|---|
| `p01/NOTES.md` | new **§3b** — `small` R2/R3 `ns` withdrawn; mechanism as `win32` on the 30-byte SSE loop; mode-matched and out-of-sample numbers; the failure scenario; a new identical-copy noise-floor control |
| `p01/README.md` | new "The `small` wall-clock column is withdrawn" section |
| `p05/NOTES.md` | new **§4b** — `small` row withdrawn, **not** for a shipped-layout reason |
| `p05/README.md` | ⚠ only `large` is quotable |
| `p02/NOTES.md` | new "these wall-clock cells… **SURVIVE**" subsection in §3 |
| `p08/NOTES.md` | new **§4b** — survives; plus the 11-point `large` magnitude caveat |
| `p16/NOTES.md` | "the null was bracketed at 30 code layouts, and it SURVIVES" |
| `p17/NOTES.md` | same, in §2b |
| `p07/NOTES.md` | §11e: bit 4 demoted to a proxy; mechanism replaced with `win32`/`jcc32` + SKX102; the wrong-loop negative corrected with the reason it was picked; simulator zeros corrected to "≤6 events in 10⁸"; out-of-sample block added; dominance bullet retracted; **new §11f** for the R4 band; §3's "bit 4" sentence replaced |
| `p07/README.md` | headline paragraph rewritten; R4 band flagged |

`spec.md` **not touched**: all seven `slb-contract` blocks were parsed and none
pins a wall-clock or `ns` value, so a wall-clock withdrawal has no hashed home.
`harness/`, rung sources and cells untouched; nothing relinked.

## Evidence

### The contradiction — blocker 2 is a round-robin ORDERING artefact

`.temp/r30/layout_gen.py:203` times with `for k, b in bins.items()` over a dict
filled rung-by-rung, so each rung occupies a contiguous third of every rep and the
*shipped* build is slot 0 of its own block. `harness/measure.py:wall()`,
`repeat.py` and `interleave.py` all alternate. **`interleave.py` ruled out
*width*, not *order*.** On 31 **byte-identical copies** per rung, one layout:

```
--- pass 0  order alt  ALTERNATING (measure.py/interleave.py) ---
  R2 vs R4 (medians)  +28.08%     R3 vs R4 (medians)   +1.21%
--- pass 0  order blk  BLOCKED (layout_gen.py) ---
  safe_naive   median   6.287 ms  copy#0   6.850 ms  rank 30/30
  safe_tuned   median   5.684 ms  copy#0   5.156 ms  rank  2/30
  unsafe       median   5.931 ms  copy#0   5.839 ms  rank  5/30
  R2 vs R4 (medians)   +6.00%     R3 vs R4 (medians)   -4.16%
  R2 vs R4 (copy#0)   +17.31%     R3 vs R4 (copy#0)   -11.70%
```

Against `layout_shipped.log` (shipped R2 rank 30/30, shipped R3 rank 0/30,
R3-vs-R4 **−9.91 / −11.57%**, "population" R2-vs-R4 **+7.17 / +6.96%**). Four
blocked blocks: R3-vs-R4 slot-0 **−11.70 / −10.77 / −3.68 / −3.92%**; four
alternating: **+0.63 … +6.64%**. **Every reading blocker 2 attributes to layout is
reproduced with no layout.**

### The real reason p05's row goes — its band is inside its own noise floor

`.temp/p31/spreads.log`, all `small`, 31 identical copies, 4 blocks each:

```
p01  0.82 … 3.17%   vs 30-layout band 10.42 / 10.15 /  7.74%
p07  0.83 … 2.24%   vs                31.76 / 17.12 /  8.08%
p05  5.09 … 45.04%  vs                14.09 /  8.30 /  9.34%
```

Under the alternating protocol p05's numbers are stable and positive: R2−R4 ≈+30%
across 17 measurements, R3−R4 +1.2…+6.9%.

**Minor 7's "lever bias" is the same artefact** (`posbias.log`) — slots 10–30
(`order` builds) vs 1–9 (`align` builds) on identical copies: blocked
**+3.90 / +5.30%**, alternating **−0.98 … +0.36%**, against `lever_bias.log`'s
+5.05 / +5.27 / +9.85% for that exact rung.

### p01's and p07's withdrawals are NOT the artefact — three ways

(a) The pre-registered out-of-sample run used 20 `order`-only builds and its
labels are uncorrelated with slot: `mean slot: slow 9.0 fast 10.0 (uniform 9.5)`,
all three rungs perfectly separated on both passes. (b) Both patterns are
protocol-*insensitive* on identical copies: p07 R2−R4 `+27.46 / +27.67 / +27.67 /
+27.77%`, R3−R4 `+12.42 / +12.65 / +12.42 / +12.60%` — alternating and blocked
agree; p01 `+4.55 … +4.80%`. (c) p01's mode has a disassembly mechanism (30-byte
SSE loop, `win32[1,2]`).

**Item 5 gets a clean control from the same probe**: p07 R4's 7.68–8.09% band is
~5–6× its 1.10–1.54% identical-copy floor and is order-insensitive — real layout
variance.

**Rows the task did not quote and that landed**: `p08 large safe_naive` published
+50.91% against +61.93% over the population (11 points; the layout population is
only 3% wide, so this is session/CPU, not layout), and `p05b small safe_tuned`
+4.12% → −0.99% "sign flips", which is the blocked-order artefact.

### Gates — every pattern touched

```
check.py p01: PASS-WITH-BLOCKED-ROWS      (Miri policy, not a regression)
check.py p02: PASS      check.py p05: PASS      check.py p07: PASS
check.py p08: PASS      check.py p16: PASS      check.py p17: PASS
source_sha256: 186 pinned files across 7 patterns, 0 stale
```

`md5_fn` unchanged everywhere. Moved gate-JSON keys: 10 `source_sha256` entries
for edited `.md` files, 18 ASan PID/ASLR strings, and p05's two documented
`adversarial-dims` stdout leaves. A structural diff over both JSON trees reports
**0** changed `md5*`, `n_fn`, `Ir` or `marginal` keys. `harness/report.py`
regenerates all seven tables **byte-identically**.

## Problems

- **`.temp/r30/layout_gen.py:203` is the bug** (`for k, b in bins.items()`), and
  its docstring and log both say "interleaved". Every cross-rung percentage in
  `layout_*.json` inherits it: `survives.log`'s `published/pooled/mode0/mode16`
  columns, `lever_bias.log` entirely, `analyze_*.log`'s `pooled median` rows. It
  does **not** invalidate within-rung mode ratios where the mode label is
  uncorrelated with build slot — guaranteed for the 20-layout out-of-sample runs,
  **not** guaranteed for the 30-layout populations (p01 R2: `%32=0` has 8 align +
  8 order, `%32=16` has 1 align + 13 order). p01's `+5.24 / −4.10` is quoted with
  that caveat rather than as primary evidence. One-line fix: build a flat
  interleaved list instead of iterating the dict.
- `.temp/build` (532 M) and `.temp/check` (302 M) are pre-existing shared caches
  refreshed by the mandated gate runs; 105 files predate today. Manager's sweep
  call.

## Unsure / not done

- **Item 3's framing — neither manager option was right.** p02/p08/p16/p17 are
  **not** untested-and-lucky: 30 layouts each, and their entire populations are
  0.84–3.66% wide on `small`, so nothing in them could move an 18% or 105% gap.
  But "survive essentially unchanged" is too strong: p08's `large` R2 is +50.91%
  published against +61.93% over the population. The honest summary is three-part
  — **the signs survive on four patterns; no magnitude survives to two decimals
  anywhere it was checked; and the C and R5 rungs of all seven remain
  unbracketed** — written that way in each file.
- No layout population was re-measured; everything is re-analysis of `.temp/r30/`
  stored JSON plus a new identical-copy probe.
- **The order effect's own mechanism is not identified** — established *that*
  blocked ordering moves p05's cross-rung gap by 5–25 points, not *why*.
  Candidates not separated: intra-rep thermal/frequency ramp, first-of-block
  transition cost. p01 and p07 are immune, so it needs an unstable cell to show.
- Fixed p07 `NOTES.md`'s retracted dominance sentence (TASK_030_REVIEW major 3
  named it; no task item covered it) — one edit beyond items 1–5, flagged.
- Not checked whether `predict_then_time.py` / `q3_convergence.py` carry residual
  slot bias (order-only populations, so the align/order split cannot apply).

## Item 6 — the reproduction path, report only

**Minimum shippable set, ~640 lines**: `loopfit.py` (132 — the mechanism),
`layout_gen.py` (239 — **must not ship until the ordering bug is fixed**),
`predict_then_time.py` (172 — the pre-registration harness, what makes the finding
falsifiable), `.temp/p31/order.py` (130 — the protocol control). Reporting extras:
`analyze.py` (178), `survives.py` (86), `q3_convergence.py` (72), `modesim2.py`
(90) → ~1,070 total. **`jcc.py` must not ship as-is** — its "tightest backward
branch" heuristic is the defect that produced §11e's wrong-loop negative; keep its
address/`md5_fn_norel` half and fold it into `loopfit.py`. All `sys.path`-insert
`harness/` and `import asm`.

**Cost by home** (`check.py:4777-4786`; globs are non-recursive). Measured gate
cost warm: 87 s (p16), 84 s (p05), 109 s (p02) → all seven ≈10–15 min.

| home | copies | gates re-run per edit | hashed? |
|---|---|---|---|
| `p07/controls/*.py` | 1, under a pattern it is not about | 1 | yes |
| one copy per citing pattern | **3, and they will diverge** | 1 each | yes |
| `common/*.py` | 1 | **all 7** | yes |
| `common/layout/*.py` (subdir) | 1 | **0** | **no** — matches neither glob |
| new top-level `layout/` | 1 | 0 | no |

**Recommendation**: `common/layout/*.py`, one copy, **with that glob added to
`check.py`'s `srcs`** so it is hashed — 7 gate runs per edit, for a tool that
should be stable, buying one authoritative copy for p01, p05, p07 and every future
pattern. Whichever home is picked, **fix the round-robin ordering first**;
shipping it as-is ships the artefact.

## Memory updates

None written (forbidden). Landed by the manager: p05's withdrawal reason, the
`--symbol-ordering-file` caveat's evidence withdrawn, the duplicated heading
removed, RECAP finding 16 refined to the three-part summary, and the new
**"Interleave by CELL, never by block"** section with the identical-copy
noise-floor table.
