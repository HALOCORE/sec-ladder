# TASK_034 — report

Engineer's return message, recorded by the manager. Scratch `.temp/p34/`.
All ten items landed; all eight gates green.

## Did

**Item 1 — the guard is not free; the trade is published, the line is untouched.**
`p11/NOTES.md` §5a rewritten (law, mechanism, p17-vs-p11 currency table, "the line
stays"); `unsafe.rs` and `verus.rs` header comments corrected; and — beyond the
task — **two more places in `spec.md`** that said the same thing (its `required`
bullet and the "ONE clause" paragraph, both prose *outside* the hashed block:
`contract_sha256` unchanged at `277a725a25ab…`). `c/main.c` was already right.
§4c's "nothing left over" now carries the qualification that 1.00000 of R4's
6.00000 is guard bookkeeping.

**Item 2 — generator fixed, not the sentence.** `inputs/gen.py` draws
`shared = strings(rng, COUNT_LENS)` once for the `count`/`zerotail` pair.
Regenerated; the pair now differs in **20 bytes, all in the tail**.

**Items 3–8.** §2's `memchr` row split out at a re-measured **0.1023 Ir/byte**;
§5b `external_body` lines → 217/266/278; §6 mutant citations re-derived with a
warning that they track `verus.rs`; §11b "four pairs" → **seven, in two
orientations**; §4c presented as a **per-residue-class fit** with the c-gcc
intercept range corrected to **+39 … −170**; SLB-TRUSTED-ARGUMENT (c) now gives
all three `slb_twin` counts (3 substring / 2 token / **1 in blanked code, which is
what the gate scans**); §10b retires "*likely* is not measured". `README.md`: ASan
frame `:65 → :68`.

**Item 9 — `harness/report.py`.** The false sentence replaced by the condition
plus a check an author can actually run.
**Item 10 — `harness/asm.py`.** `_BULK_STR_WORDS` (search/copy/compare `str*`;
conversions `strtoul`/`strtol`/`strtod`/`strerror`/`strsignal` deliberately
excluded), plus **27 new selftest cases** (47 total). `harness/` touched for
nothing else.

`results/p11-nul-scan.json`'s **`inputs` block only** was refreshed via
`measure.py`'s own code path — one line, `zerotail`'s `expected=`. A full
re-measure would have redrawn every `Ir`/`ns` that §3 quotes.

## Evidence

```
unsafe (shipped)  n_fn=123 nopad=117 md5_fn=9145e57079d2
u_noqguard        n_fn=114 nopad=109 md5_fn=54f39868dbf4
small.bin  unsafe 19084.00  u_noqguard 17481.00  guard 1603.00 = 8.4% of R4
large.bin  unsafe 50174.00  u_noqguard 45909.00  guard 4265.00 = 8.5% of R4
```

Controlled pair, and only **three** blobs moved:

```
n differing bytes: 20   indices: [44 … 63]
zerotail (intended), stride3 (0 kernel calls), sweep-len01k24 (band-A lengths are
constant, so no law can move); count byte-identical.
```

Nothing past `sweep-len01k24` moved because `random.shuffle`'s rejection sampling
makes word consumption data-dependent and the streams re-converge (MT index 343 vs
339 before it, **entire state equal after it**).

ASan on the regenerated tree: `READ of size 13 / 66-byte region` and `READ of size
21 / 40-byte region`, both `#1 kernel …/c/kernel.c:68`; zerotail clean. `memchr`:
**429,184 Ir / 4,194,304 B = 0.1023** at `libc+0x188080`. Mutants 12/0, twin 12/1,
10/2, 11/1 — unchanged.

**All eight gates green**; every gate JSON's 34–36 `source_sha256` entries match
the tree; **252 cells compared, 1 changed** (p11's zerotail checksum, intended).
Churn is the documented class only — ASan diagnostics (PID *and* `pc`/BuildId, so
byte-identical reproduction is impossible), p05's two `adversarial-dims` stdouts,
and **p08's marginal jitter: 30 entries, largest move 0.08** (series
8 → 23 → 75 → 0 → **30**, inside the 0…75 budget). All eight tables regenerated.

**Item 9's numbers, and the manager's premise contradicted — p11 is not the worst
case:**

```
p01 0.0051  p05 0.0052  p07 0.0030  p16 0.0036  p17 0.0018   0 inverted pairs
p02 0.1895                                                   0 inverted pairs
p08 10 inverted rung pairs, worst 2.2315  (c-gcc 58% DEARER than c-clang here,
                                           33% CHEAPER on the marginal)
p11  3 inverted rung pairs, worst 0.7839
```

## Problems

- **`results/p01-array-sum.json` is stale and nothing detects it.**
  `c-gcc/O0/whole` records `md5_fn 2fe6ada73f90`; a rebuild gives `4104f39118e8`,
  twice, deterministically. **Not caused by this task**: HEAD's own `asm.py`
  extracts the same new value, `n_fn` (98) and `fn_bytes` (411) are unchanged so
  it is displacements only, and the record was measured at `5bbb5ac` after which
  `common/driver.c` gained 23 lines. **Root cause: `results/*.json` carries no
  `source_sha256` block**, unlike `results/gate/*.json`, so a measurement record
  can drift silently — it did, for ~7 tasks. Reported, not fixed.
- **`RECAP.md`'s queued-defect block is now false** — both harness defects landed
  here. Manager's file; not edited.
- Cosmetic, deliberately not changed to avoid re-hashing `check.py` mid-run: stage
  3a still says "bulk-memory call" where the family is now bulk-memory *or*
  bulk-string.

## Unsure / not done

- **Item 9's wording — the manager's least-certain call, answered with a
  measurement.** "Same routines in every rung" is **not** checkable from the
  table: it prints no call column, and `bulk_calls` in the gate record names only
  *recognised bulk* routines, so p11's `<CStr>::from_bytes_until_nul` would never
  appear there. But "point at `NOTES.md` and stop" would have been weaker than
  necessary, because a complete check exists that needs no disassembly: **every
  rung runs the same input the same number of times, so rung-to-rung ratios of the
  kernel-exclusive column are comparable with the same ratios of
  `marginal_ir_per_call`**, which is symbol-independent. That is what shipped,
  with the p08/p11 instances quantified.
- Landed the reviewer's four-length `guard = 24·L + 97` table as *theirs* —
  reproduced the static counts and both marginals, not the four sweep points.
- Did not build an *exec* SWAR R4 (doubly inadmissible); did not re-run the
  31-layout population; did not re-measure any wall clock.

## Memory updates

None written. Landed by the manager: the p08-is-sharpest correction and the
author-checkable ratio test (`.memory/03-measurement.md`), the `results/*.json`
staleness gap with its two-pattern scope, and the RNG re-convergence fact
(`.memory/05-layout.md`).
