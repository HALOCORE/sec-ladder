# Measurement protocol

Hardware counters are unavailable on this box (`perf` absent, `perf_event_paranoid=3`,
no root). Everything below is designed around that.

## Metrics recorded per cell

| Metric | How | Noise |
|---|---|---|
| **kernel instruction count** | `objdump -d`, extract kernel symbol, normalise, count | zero — deterministic |
| **kernel `.text` bytes** | `nm --print-size` / section headers | zero |
| **executed instructions (Ir)** | `valgrind --tool=callgrind` (once TASK_001 lands) | zero — deterministic |
| **wall clock** | `taskset -c <cpu>` pinned, ≥30 reps, report **min and median** | high |
| **binary size** | stripped `.text` of whole binary | zero |
| **exec LOC / spec+proof LOC / TCB lines** | counted per `.memory/04-verus.md` rules | zero |
| **verification time** | `verus --time` | low |
| **asm qualitative flags** | bounds check present? panic landing pad? vectorised (xmm/ymm)? unroll factor? | zero |

**Primary metrics are the deterministic ones.** Wall clock is a sanity check on
the instruction counts, never the headline number.

## Assembly extraction (the canonical normalisation)

```bash
objdump -d --no-show-raw-insn <bin> | awk '/<kernel.*>:/,/^$/' \
  | sed -E 's/^\s+[0-9a-f]+:\s+//; s/0x[0-9a-f]+//g; s/<[^>]*>//g' | grep -v '^$'
```

Strips addresses and symbol hashes so two builds diff cleanly. Rust symbols are
mangled (`_RNvCs..._6kernel`); match on the `kernel` substring, not an exact name.
`harness/asm.py` owns this — do not reimplement it ad hoc.

## Timing protocol

1. Pin to a single core with `taskset -c N`. Use the same core for a whole
   comparison set; record which.
2. **Interleave cells** (round-robin across rungs, repeat) rather than running all
   reps of one cell then the next — this spreads thermal/neighbour drift across
   all cells instead of concentrating it in one.
3. ≥30 reps. Report min (the least-perturbed sample) and median. Never mean.
4. Discard a run whose min-to-median spread exceeds 10% and say so.
5. Frequency scaling is on and cannot be disabled without root. State this next to
   every wall-clock table.

## What we cannot measure, and must not fake

- IPC, branch mispredictions, cache misses. These would need
  `perf_event_paranoid ≤ 1`. **Do not estimate them from wall clock.** If a claim
  needs them (e.g. "the bounds check costs a branch miss"), mark it as a
  hypothesis and say what would test it.
- Callgrind `Ir` counts instructions, not cycles. A vectorised loop with fewer
  instructions is not automatically faster. Report both Ir and wall clock and let
  them disagree openly.

## Results format

One JSON per pattern in `results/pNN-<name>.json`, schema owned by
`harness/measure.py`. Generated tables go in `results/tables/`. Raw is committed;
tables are regenerable. Every JSON records the toolchain versions and the git
commit it was produced from.
