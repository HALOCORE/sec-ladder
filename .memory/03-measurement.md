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
name.

**`harness/asm.py` now owns this (written at TASK_002). Do not run objdump
anywhere else.** The shell pipeline above is kept only as documentation of
intent; the implementation differs in two ways it had to:

- the branch-target strip is **positional** (operand of a branch/call), not
  width-based, so `fadd` survives and `je 8f2` does not;
- there is no `s/\b[0-9a-f]{4,}\b//g` at all.

API: `asm.kernel(binary, needle) -> Kernel` with

- objdump-grouping convention (function **+** inter-function padding):
  `.n_raw`, `.n_nopad`, `.n_bytes`, `.raw_bytes`, `.md5_raw`, `.md5_raw_norel`;
- `nm --print-size` convention (the function proper — **use this for identity**):
  `.n_fn`, `.n_fn_nopad`, `.fn_bytes`, `.md5_fn`, `.md5_fn_norel`, `.has_extent`;
- padding, reported separately and never folded in: `.pad_insns`, `.pad_bytes`;
- shape: `.normalised`, `.md5_norm`, `.has_loop`, `.backward_branches`,
  `.vector_regs`.

Also `asm.nm_extents(binary) -> {sym: (addr, size)}`;
`asm.diff(a, b) -> (same_fn, same_fn_norel, text)` (compared on the declared
extent); `asm.identity_level(ka, kb) -> (level, evidence)` where level is one of
`exact` / `norel` / `counts` / `differ`, ordered in `asm.IDENTITY_LEVELS`;
`asm.text_size(binary)`.

`asm.selftest()` re-derives every pilot number in this file and in
`.memory/01-ladder.md` from `.temp/build/docrepro/` — **both digest conventions
are pinned**, so neither can drift into the other silently.
**`harness/fixture.py` builds that fixture** (nothing in the repo did before
TASK_003, so on a fresh checkout the selftest returned 77 and the gate
downgraded it to a note — step 0 measured nothing). `harness/check.py` now
builds the fixture if it is missing and *fails* if it cannot, then runs the
selftest as its step 0, so a regression in the extractor fails the gate.

Reproduced from a clean rebuild at TASK_003 — all six binaries, both
conventions, bit-exact:

| binary | n_raw / n_nopad | `md5_raw` | `md5_fn` (nm extent) | padding |
|---|---|---|---|---|
| `k_gcc` | 32 / 30 | `42779803…` | `42779803…` | 0 insn / 0 B |
| `k_clang` | 33 / 31 | `92dc2bc6…` | `f5cc6e16…` | 1 insn / 3 B |
| `k_rust`, `k_verus` | 57 / 46 | `935221a8…` | `e5310297…` | 9 insn / 9 B |
| `k_unsafe`, `k_unsafe_verus` | 37 / 33 | `98e4a665…` | `a23e076c…` | 3 insn / 3 B |

Padding-excluded = every `int3`/`nop`*/`xchg %ax,%ax` dropped, wherever it sits
(not just the tail). `ud2` is deliberately **counted**: it is the tail of a real
panic path, not alignment.

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
R2 ≡ R2v and R4 ≡ R5 are byte-identical.

**Two digest conventions exist and they mean different things. Say which you used.**

| convention | extent | pilot digests |
|---|---|---|
| `nm --print-size` (the declared symbol size) | the function | `e5310297…` / `a23e076c…` |
| `harness/asm.py` `md5_raw` (objdump's symbol grouping) | function **+ inter-function `int3` padding** (9 / 3 bytes on the pilot) | `935221a8…` / `98e4a665…` |

TASK_002 recorded that the `nm` digests "came from an unrecorded convention and
cannot be reproduced". **Both halves of that were false** — the convention is the
one written two paragraphs above, and TASK_002_REVIEW reproduced both digests
first try. The real issue is that `asm.py` reads *past* the declared symbol size,
so `md5_raw` and `n_raw` are a digest and count of the function plus whatever
alignment padding follows it. Consequence: two genuinely identical kernels at
different alignments get different digests, and a gate that hard-fails on digest
mismatch turns a benign relink into a false "the proof cost something" finding.
Prefer the `nm`-extent digest for identity; keep the padded one only if the
padding is reported separately.

### The raw-byte oracle has one blind spot: link layout

A `call rel32` encodes the distance to its callee, so two binaries containing the
*same* kernel differ byte-for-byte if anything shifted the callee — and a
one-character difference in a crate name (`6unsafe` vs `5verus`) does exactly
that. This is invisible at `-O3`, where the kernels are leaf functions, and bites
at `-O0`, where the Rust kernel still calls `Iterator::next`. Measured at
TASK_002 on p01: `md5_raw` differs at O0 for R4-vs-R5, and the entire difference
is three `call`/`jmp` displacements and one `%rip` displacement.

`harness/asm.py` therefore also exposes **`md5_raw_norel`**: the same machine-code
bytes with pc-relative *displacement fields only* zeroed. It recovers each field's
value from objdump's own decoded target (`target - end_of_insn`) and locates it in
the encoding, so nothing else is touched — every immediate, every non-pc-relative
displacement, every opcode and register field still contributes. The constructed
`0x1234`-vs-`0x5678` collision above is still caught.

Rule: **quote `md5_raw` when it matches. When it does not, say so, and quote
`md5_raw_norel` explicitly as the weaker claim it is.** Never silently substitute.

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

`harness/measure.py` owns this. Two things the one-liner gets wrong:

- **`callgrind_annotate` splits one function across several `file:function`
  rows.** Take the *sum* of every matching row, not the first. `measure.py`
  matches on `(?:^|::)kernel(?:$|\W)` against the function half of `file:function`
  so `k::kernel` and `???:kernel` both hit and `main::{closure#0}` does not.
- In `whole` builds there is no kernel symbol — it was inlined on purpose — so
  `measure.py` records `main`-exclusive `Ir` there and labels it. **`isolated` and
  `whole` Ir are not comparable to each other**; `main` includes the loader.
- **`main`-exclusive `Ir` is not comparable between C and Rust either.** It counts
  whatever *else* was inlined into `main`, and that differs by language: the Rust
  rungs inline the payload decoder into `main`, the C rungs leave it in
  `common/driver.c`'s own symbols. Measured on p01 `large`: ~12.36 M instructions
  the Rust `main` carries and the C `main` does not. Taken raw, that column
  reports an 8.32% clang-over-rustc win **that does not exist**.

  **Do not try to rescue it by subtraction.** TASK_002 subtracted each cell's own
  `isolated` `main` figure and published "equal to within 1 instruction"; the
  arithmetic was wrong (c-clang is **+78**, not −1, and `safe_tuned` flips sign
  from −19,918 to **+80,001**). The residue also silently includes an 11-Ir C-ABI
  shim the Rust rungs have and C does not. A difference of two large numbers, each
  containing language-specific inlining, is not a measurement.

  **Use the `isolated` kernel-exclusive figure instead — it needs no correction
  and it makes the point cleanly.** On p01 `large`, c-clang and unsafe Rust both
  execute **143,740,000** kernel instructions: not "within 1", but exactly equal.
  That is the publishable form of this claim.

### The one honest use of whole-program `Ir`: a slope

Whole-program `Ir` is unquotable as a level (below). It is perfectly good as a
**difference**, because every term that makes it unquotable — loader work, the
size of the environment block, what stdout is connected to — is identical in two
runs of the same binary in the same shell and cancels exactly.

`harness/check.py` step 3b uses this as its anti-collapse assertion:

```
marginal Ir per call = (Ir at n_iters=200  -  Ir at n_iters=100) / 100
```

The probe files are the pattern's own `small.bin` with the `n_iters` field
rewritten — that field is at offset 0 of *every* input file
(`.memory/02-bench-rules.md`), so the harness builds them without the pattern's
help. Two properties make this better than a per-symbol `Ir` floor:

- **symbol-independent** — works in `whole` mode, where the kernel has been
  inlined away, and at `O0`, where `safe_tuned`'s work lives in `core::iter`
  symbols and its `kernel` symbol executes only 32 Ir/call;
- **cheap** — 56 callgrind runs over p01's 28 cells took 10 s wall.

A kernel that had been constant-folded, hoisted or CSE'd reads ~0.

**The floor is derived, not pinned** (TASK_005). `spec.md` used to declare an
absolute `min_marginal_ir_per_call`, and p01's was 400 against a measured
minimum of 915 — 0.80 Ir per element against 1.83 achieved. Worse, it was a
number the pattern author could lower in the same commit that broke the loop.
`model.py` now reports `work_per_call` and `harness/check.py` asserts
`marginal_Ir >= ALPHA_IR_PER_WORK * work_per_call`, plus `d(Ir)/d(work) >= ALPHA`
across two probe shapes; ALPHA is a harness constant (0.25 — one instruction per
four 64-bit SIMD lanes, doubled for headroom). Measured on p01 after the TASK_005
barrier swap: 908 … 274 496 Ir/call over 56 cell/probe pairs, `d(Ir)/d(work)`
1.75 … 67.00.

**Report per-function exclusive `Ir` for the kernel symbol. Never the
whole-program `summary:` line as a level.** Measured at TASK_001 on `pilot/k.c`
(gcc, n=999):

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

### …but kernel-exclusive `Ir` silently drops work that leaves the symbol

Found at TASK_004 on p02, whose kernel is a `memcpy` plus a fold. `memcpy` is in
libc, so callgrind attributes it to libc — and the `kernel` symbol's *exclusive*
count, which is what `harness/measure.py` reports, does not contain it. On
`large` (4092 bytes per call, `-O3 isolated`):

| | c-gcc | c-clang | unsafe |
|---|---:|---:|---:|
| marginal Ir per call (whole program, difference of two runs) | 9195.7 | 10192.7 | 10200.8 |
| `kernel` symbol, exclusive | 8765 | 9764 | 9772 |
| missing: driver loop + the `memcpy` | ~431 | ~429 | ~429 |

~4% here, and it would be ~100% for a kernel that is *only* a `memcpy`. The same
applies to a Rust rung whose work is in `core::iter` symbols at `-O0`.

**The direct measurement of that `memcpy`, since several rules now depend on it**
(TASK_004_REVIEW, re-derived at TASK_006). Difference of two rungs that are
identical except that one deletes the copy, `-O3 isolated`, 4092 bytes:

| rung | marginal Ir/call |
|---|---:|
| copy 4092 B, then fold 8 of them | 483.7 |
| the same with the copy deleted | 58.0 |
| **glibc `memcpy`, 4092 bytes** | **425.7 = 0.104 Ir per byte** |

Two things rest on it: the anti-collapse floor's per-unit rate cannot exceed
0.104 for a byte-denominated unit without forbidding the fastest correct
implementation (`.memory/02-bench-rules.md`), and "the copy is 4% of p02's
kernel" is a subtraction rather than an estimate. Note the second row is *not*
zero — 58.0 Ir is the surviving prologue, rejection test and 8-byte fold.

**So: kernel-exclusive `Ir` is the right level for a self-contained kernel, and
the wrong one for a kernel that calls out.** The gate's `marginal_ir_per_call`
(whole-program `Ir` at 2N calls minus at N, over N) has neither problem — it is a
difference of two runs of the same binary in the same shell, so every loader and
environment term cancels, and it is symbol-independent so nothing can leave it.
Quote the marginal column for any pattern whose kernel contains a bulk-memory
call, and say which column you are quoting either way.

And from the same pattern, the standing caveat about `Ir` as a proxy for time,
now with a counterexample: **gcc executed 10% fewer instructions than clang on
identical source and took 23% longer** (8765 vs 9764 Ir/call; 30.8 vs 25.0 ms
wall, min of 15, pinned). `Ir` and wall clock disagreed in *direction*. This box
cannot measure IPC to explain it (no `perf`, `perf_event_paranoid=3`, no root),
so it stands as an observation — and as the reason a wall-clock column must
accompany any cross-compiler claim.

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
