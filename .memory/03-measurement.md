# Measurement protocol

Hardware counters are unavailable on this box (`perf` absent, `perf_event_paranoid=3`,
no root). Everything below is designed around that.

## Metrics recorded per cell

| Metric | How | Noise |
|---|---|---|
| **kernel instruction count** | `objdump -d`, extract kernel symbol, normalise, count | zero — deterministic |
| **kernel `.text` bytes** | `nm --print-size` / section headers | zero |
| **executed instructions (Ir)** | `~/tools/valgrind/bin/callgrind_annotate` on a `--tool=callgrind` run, **per-function exclusive Ir** | zero — deterministic |
| **wall clock** | `taskset -c <cpu>` pinned, ≥30 reps, report **min and median** | high |
| **binary size** | stripped `.text` of whole binary | zero |
| **exec LOC / spec+proof LOC / TCB lines** | counted per `.memory/04-verus.md` rules | zero |
| **verification time** | `verus --time` | low |
| **asm qualitative flags** | bounds check present? panic landing pad? vectorised (xmm/ymm)? unroll factor? | zero |

**Primary metrics are the deterministic ones.** Wall clock is a sanity check on
the instruction counts, never the headline number.

## Assembly extraction (the canonical normalisation)

```bash
objdump -d --no-show-raw-insn <bin> | awk '/kernel[^ ]*>:$/,/^$/' | grep -v '>:$' \
  | sed -E 's/^\s+[0-9a-f]+:\s+//; s/\s+#.*$//; s/<[^>]*>//g;
            s/0x[0-9a-f]+//g; s/\b[0-9a-f]{4,}\b//g; s/\s+$//' | grep -v '^$'
```

Strips addresses and symbol hashes so two builds diff cleanly. Rust symbols are
mangled (`_RNvCs..._6kernel`, v0); match on the `kernel` substring, not an exact
name. `harness/asm.py` will own this — **not yet written** as of TASK_001; until
it exists, use exactly the pipeline above.

### This normalisation is for READING diffs. It cannot prove identity.

**Never use the normalised text (or its md5) as the oracle for "R5 ≡ R4".** The sed
erases every immediate, every memory displacement and every branch target — so two
kernels with *different semantics* can normalise to the same text. Demonstrated at
TASK_001_REVIEW with a constructed collision:

```
c.c: acc ^= v[i]; acc = acc*3 + 0x1234;    d.c: ... + 0x5678;
normalised md5:  a4bb69cc38fbf4d7…  ==  a4bb69cc38fbf4d7…   <-- collide
raw asm md5:     69f30690…          !=  e38b6982…           <-- actually differ
./kc 7 7 7 -> 60799                     ./kd 7 7 7 -> 287915
```

The failure this invites: a pattern's R5 drifts from R4 by one immediate (different
unroll factor, mask, stride) and the tooling reports "identical" — making the
project's headline structural finding unfalsifiable by its own instruments.

**The identity oracle is the raw machine-code bytes of the kernel symbol** (locate
via `nm --print-size` mapped through the program headers, or `objdump -d` *with*
raw insn bytes and only the address column stripped). `harness/asm.py` must expose
both, and every "identical" claim must cite the raw-byte digest.

Under the raw-byte oracle the pilot's finding does hold, independently reproduced:
R2 ≡ R2v (`e5310297…`) and R4 ≡ R5 (`a23e076c…`) are byte-identical.

### Known hazards in the sed (fix when writing `harness/asm.py`)

- `s/\b[0-9a-f]{4,}\b//g` **eats the `fadd` mnemonic** (`fadd %st(1),%st` →
  `%st(1),%st`) — all four chars are hex digits. Latent until a float pattern
  lowers to x87. `faddp`/`fadds` are safe (trailing non-hex blocks the `\b`).
- Bare-hex branch targets are only stripped at ≥4 hex digits; `je 8f2` survives.
  Inert today (PIE `.text` ≥ 0x1000). The fix is **positional** — strip the operand
  of a branch instruction — not width-based.

### Three ways the earlier version of this pipeline lied (fixed above)

Corrected at TASK_001 by re-running the pilot.

**Root cause: the repo carried two divergent pipelines.** `.memory/03-measurement.md`
had `awk '/<kernel.*>:/,/^$/'`, which emits **zero lines** for the Rust rungs
(`<_RNvCs…_6kernel>:` does not contain `<kernel`) and so cannot have produced the
published numbers. `TOOLCHAIN.md` had `awk '/kernel>:/,/^$/'`, which does reproduce
33/58/38. Defects 1–3 below are the *latter's*. One pipeline, one owner
(`harness/asm.py`), is the actual lesson.

1. **Off by one, always.** It kept the `<addr> <sym>:` header line, which survives
   as a non-blank line after the sed. Every count published from it is exactly
   **one too high**. `pilot/README.md` and `PLAN.md` say 33 / 58 / 38; the real
   kernel instruction counts are **32 / 57 / 37**. Deltas are unaffected;
   absolutes are wrong.
2. **Bare-hex addresses survive.** objdump prints branch targets and rip-relative
   annotations without a `0x` prefix (`je 14456 <kernel+0x26>`, `# 52f18 <...>`),
   so the old `s/0x[0-9a-f]+//g` missed them. Two builds whose kernels differ only
   in link placement then diff **non-empty**, downgrading that pair's
   "byte-identical" claim to a mere count comparison. (Scope: it bit the *safe*
   pair, linked at 0x14430 vs 0x14450; the unsafe pair both linked at 0x14400 and
   diffed clean, so half the old claim was already a real text comparison.) Note
   this fix makes the text diff *usable*; it still does not make it an identity
   oracle — see the collision above.
3. **Trap/nop padding is counted as instructions.** The symbol size from
   `nm --print-size` includes LLVM's `int3` tail padding (9 of them in the pilot's
   safe-Rust kernel, 3 in the unsafe one) and gcc's alignment `nop`s. Report both
   a raw count and a **padding-excluded** count; the raw one overstates the
   safe-vs-unsafe gap (57 vs 37 raw → 46 vs 33 real).

### Static count is not a cost model

Reported at TASK_001: gcc's 32-instruction pilot kernel **executes 125,019** Ir at
n=50 000 while LLVM's 37-instruction kernel executes **87,520** — the ranking
inverts, because LLVM unrolls the SSE2 loop 2× (4 elems/iter, 7 instrs) and gcc
does not (2 elems/iter, 5 instrs). Never present a static count as a proxy for
work done. Pair it with `Ir` or say nothing.

## Callgrind protocol

```bash
~/tools/valgrind/bin/valgrind --tool=callgrind --callgrind-out-file=<out> ./bin <args>
~/tools/valgrind/bin/callgrind_annotate --threshold=100 <out> | grep kernel
```

**Report per-function exclusive `Ir` for the kernel symbol. Never the
whole-program `summary:` line.** Measured at TASK_001 on `pilot/k.c` (gcc, n=999):

| variation | whole-program Ir | kernel Ir |
|---|---|---|
| baseline | 325,593 | 2,516 |
| one extra env var (`FOO=barbar…`) | 326,144 | 2,516 |
| `env -i` (empty environment) | 277,198 | 2,516 |
| stdout to a pipe instead of `/dev/null` | 325,533 | 2,516 |

The whole-program column is **illustrative, not reference data** — an independent
re-run got 325,579 / 326,158 / 277,212 / 325,519, i.e. it does not reproduce even
on this box, which is precisely the claim. The kernel column reproduces exactly.

Whole-program `Ir` moves with the size of the environment block, the argv block
and what stdout is connected to — the dynamic loader and libc do proportional
work. It is *repeatable* (3/3 identical for all six pilot cells at n=50 000) but
not *portable across shells*, so it is worthless as a cross-cell number. Kernel-
exclusive `Ir` is invariant under all of it. The kernel needs `#[inline(never)]` /
`__attribute__((noinline))` for the symbol to survive, which the ladder mandates
for the `isolated` mode anyway.

Also: the Rust rungs' whole-program Ir (~31.8 M) is ~4× the C rungs' (~8.2 M) at
the same n, almost entirely Rust std startup plus `str::parse::<u64>` vs
`strtoul`. That is a driver artefact, not a kernel property — another reason the
summary line must never appear in a results table.

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
