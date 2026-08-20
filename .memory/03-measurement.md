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

### Attribute a surviving panic pad by DECODING its `core::panic::Location`

**Built at TASK_040_REVIEW (`.temp/r40/pads.py`), and it overturned a published
mechanism the same day.** Counting panic landing pads tells you *how many* checks
survived; it does not tell you **which**. The `Location` struct
(`file*, len, line, col`) is reachable from each pad, so the attribution is
mechanical:

```
safe_naive (R2)  pads=7   ... 70:29 `buf[off+i]`   71:17 `dst[dlen]`
safe_tuned (R3)  pads=2   50:24 `&buf[off..off+len]`   71:54 `&w[p..q]`
   ... and IDENTICAL for two other fold spellings
unsafe/verus     pads=0
```

**Why it matters**: p12 read "the count stays at 2 across three fold spellings" as
*the fold's check survives*. Decoded, **neither survivor is a destination check** —
`dst[..dlen]` contributes **zero** pads in all three, so the constant 2 is evidence
the fold **never** contributed a pad. The opposite conclusion had already reached a
rung's source comment and a published mechanism.

⚠ **Two traps in the decoder itself** (TASK_041, which found a pad the first
version missed — R2 has **seven** distinct pads, not six): **the `Location`
pointer's register is not fixed** — it depends on the panic entry's arity (`%rdx`
for `panic_bounds_check`, `%rax` for slice-range entries) — so a `%rcx`-only `lea`
match *under-counts*; and **in a PIE the `file` pointer is 0 in the image**, with
the real address in the `R_X86_64_RELATIVE` addend (`readelf -rW`). The shipped
decoder is `patterns/p12-strcat-fixed/controls/pads.py`; it matches any register,
validates the decoded struct, and has a `--source` mode.

**Always decode before attributing.** And note the sharper discriminator it
produced: `dlen ≤ DST_CAP` is bounded by a **constant** LLVM can see from the
guarded increments and is elided; `q ≤ len` is bounded by a **runtime value** and
is not. That is not p03's locality story and does not transplant it.

### `md5_fn` moves with the SOURCE FILE'S NAME when a panic survives

**Measured at TASK_037.** A kernel that retains a `panic!`/`assert!` landing pad
holds a pc-relative reference to a `core::panic::Location` carrying **the source
file's path**. So the *same* control built from two directories gives two
`md5_fn` values — p03's `r3_assert_pop`: `26e8bbe931c3` from
`.temp/p03/controls/`, `18e28795e5fc` from a copy — at identical `n_fn` (82),
identical `Ir`, and **identical `md5_fn_norel` (`e33533f83a4d`)**.

Three consequences:

- **Quote `md5_fn_norel` when comparing kernels built from different paths.**
  `md5_fn` is only comparable within one build location.
- **It is a free signal.** A control whose `md5_fn` is *stable* across paths has
  no surviving panic — which is exactly the "was the check deleted?" question. On
  p03 three of four assert-controls were byte-stable and the fourth was not, which
  independently confirmed which assertions LLVM removed.
- It does **not** affect the gate: `check.py` builds every cell into one tree, so
  the identity pin compares like with like.

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

   ⚠ **This entry was STATIC-ONLY until TASK_048, and the dynamic case is worse:
   alignment padding inside a hot loop is EXECUTED, so it lands in `Ir` and
   therefore inside a published law.** On p06, gcc's `R1h − R1 = +8.00·nrec`
   decomposes as `divq +1.000` + **`nopl`/`nop` +1.833** + `movzbl +4.000` +
   `movb +2.000` + `xorl +0.917` + `movq +0.167` − `cmpq 1.000` − `jae 1.000`:
   **23% of the law is executed padding, and only 1.000 of it is the safety line
   the law is named after.** `-fno-align-loops` moves it `+95.00 → +73.00`.
   It happened **twice on the same pattern** — p06's `R3 − R4` per-record term
   carries a `[k > 0]` indicator that is a single executed `.p2align` nop sitting
   immediately before the fold epilogue's back-edge target.

   **So: before naming a per-iteration `Ir` law after a mechanism, disassemble
   and attribute it mnemonic by mnemonic.** A padding-excluded *static* count
   does not protect a *dynamic* law, and the coefficient will look like a clean
   small integer either way.

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

### Callgrind counts a `rep`-string instruction **once per repetition**

Established at TASK_014, verified independently at TASK_014_REVIEW with a
minimal probe rather than by inference: `rep stosb` over 4096 bytes = **4110.00
Ir** (1.0034 Ir/byte) against `rep stosq`'s 527.00 and an empty call's 5.00. So
one x86 instruction can contribute thousands of `Ir`.

Consequence, measured on p08: gcc inlines `rep stos %rax` (0.126 Ir/byte) where
glibc's `memset` uses `rep stosb` (1.006), and `Ir` therefore says c-gcc is
**33% cheaper** than c-clang while wall clock says it is **dearer** — *`Ir` and
ns disagreeing in direction, with a named mechanism*. This is finding 5/6's
family with a cause attached, and it is a property of the **counter**, not of
the code.

**Blast radius checked and empty.** glibc picks the byte-wise `rep` paths only
above a size threshold — `memcpy`/`memmove` stay on the vector path at 0.104
Ir/byte up to somewhere between 8 KiB and 16 KiB, `memset` flips at 3 KiB — and
p02's copies (61 B = 26 Ir, 4092 B = 425 Ir) are well inside the vector regime.
p01, p05, p16 and p17 call no bulk routine at all. **Only p08's gcc kernels
contain a `rep` instruction**, so no previously published `Ir` comparison is
contaminated. Re-check this before denominating any future pattern in bytes
moved rather than bytes folded.

### Callgrind prices a hardware `div` at 1 `Ir`

Third named mechanism for `Ir`/ns disagreement, after `rep`-strings above and
p16's latency-bound Horner chain. `chunks_exact(n)` with a **runtime** chunk
size computes `len − len % chunk_size`, which lowers to a hardware `div` in the
prologue — one instruction to callgrind, tens of variable cycles to the machine.
Confirmed in the listing (`div %r11d`) at TASK_015 and again at review.

**The rule is sound; the ns evidence originally offered for it is not.**
TASK_015 reported +0.47% ns against −0.87% `Ir` on p05 `small`. Two independent
31-rep interleaved sessions at review **disagree on cell ordering** and on which
cell has the worst spread (one run's worst was a cell with no `div` at all), and
between-run drift of ~4% exceeds every inter-cell `Ir` difference. So the `div`
is a real hazard and this box cannot demonstrate its cost. Also:
`split_at_checked` consumes the slice with **no `div` and is 4 Ir cheaper
still**, so the defect belongs to one spelling, not to the consuming idiom.

**The two terms, settled at TASK_020.**

1. **Environment length, within one build: ≈ 0.10 Ir/call.** Three independent
   probes agree (21 pad lengths at TASK_020: min 7292.12, max 7292.22, and
   identical to TASK_019 at all six shared pads). It is **scatter, not trend** —
   pads 4…64 are byte-identical and the steps do not order with length.
2. **The build itself moves the level.** Same source, two build paths,
   **byte-identical kernel** (`md5_fn e207ec6c…`, `kernel` self-cost 9783.00 in
   both) → p02 `large` marginal 10210.82 vs 10210.84. The whole delta is inside
   libc's AVX `memmove`: 64 bytes of path length change the heap alignment.

Union over five probes: **7292.10 … 7292.30, i.e. 0.20** on p08 `small`.

**Two retractions, both landed by tasks that were correcting each other.**
TASK_017 said ≤0.08. TASK_019 then read TASK_018_REVIEW as saying *both*
endpoints of `7292.14 … 7292.30` were unreproduced, concluded "~0.1", and put it
in p01's **hashed** `collapse.note`. Both endpoints were in fact reproduced —
they are TASK_017_REVIEW's five measured points, committed at
`patterns/p08-overlap-move/NOTES.md:192`. **`check.py`'s original "about 0.2" was
right the whole time.** The lesson is the file's own: a marginal `Ir`/call is
exact only **within one build and one session**, and a number re-derived from a
prior task's prose rather than from a measurement inherits its errors.

Rule: **a spelling whose win is one instruction wide cannot be quoted on `Ir`
alone, and this box cannot supply the wall-clock column to rescue it** — say the
win is instruction-count-only and stop. A constant chunk size is a different
measurement from a runtime one.

### Two `Ir` conventions are in shipped patterns — always say which

p16's `NOTES.md` §2 quotes **callgrind kernel-exclusive `Ir` ÷ calls**; p05's and
p17's quote **whole-program marginal** `Ir` (the `n_iters` difference `check.py`
stage 3b uses). Nothing in the tree said so until TASK_016 measured it while
reconciling an audit that had quoted both.

**The offset is NOT uniform, and three published p16 deltas do move.** TASK_016
reported "+14.30 on every rung, so no difference is affected"; TASK_016_REVIEW
measured the per-rung offsets from the committed gate record and refuted it:

| rung | offset | rung | offset |
|---|---:|---|---:|
| c-gcc, c-gcc-h | **+15.72** | R2 / R3 / R4 | +14.30 |
| c-clang, c-clang-h | **+14.72** | R5 verus | **+13.30** |

and **five of p16's eight rows** have deltas that move — written consistently as
`row − R4`, small/large:

| delta | kernel-exclusive | whole-program marginal | moves by |
|---|---:|---:|---:|
| `c-gcc − R4` | +1052 / +8896 | +1053.42 / +8897.42 | +1.42 |
| `c-gcc-h − R4` | +1069 / +8937 | +1070.42 / +8938.42 | +1.42 |
| `c-clang − R4` | −17 / −37 | −16.58 / −36.58 | +0.42 |
| `c-clang-h − R4` | +7 / +17 | +7.42 / +17.42 | +0.42 |
| `R5 − R4` | 0 / 0 | −1.00 / −1.00 | −1.00 |

**No sign flips**, and this file previously said there were two — a correction
made at TASK_016_REVIEW, landed by the manager, and refuted at TASK_017. The
"flip" came from labelling a value `R4 − c-clang` while quoting `c-clang − R4`:
**switching sign convention mid-sentence, in the section whose own rule is "say
which convention".** The canonical table is `patterns/p16-tlv-walk/NOTES.md` §10.

`R5 − R4` going 0 → −1.00 is worth its own line: R4 and R5 are byte-identical
binaries (`md5_raw` equal), so their kernel-exclusive counts *cannot* differ.
The −1.00 is the driver's. **Finding 1 rests on the raw-byte identity oracle,
not on this number** — quote the `md5` when saying a proof costs zero.

Same shape as the two static-count conventions (`n_fn` vs `n_raw`), which
TASK_014_REVIEW's own write-up mixed. Rule, in both cases and now with teeth:
**say which convention a number is in, every time — a cross-rung delta is only
meaningful inside one convention.**

### Separate the safety cost from the LIBRARY cost by naming the routine

**p11 is the worked example (TASK_033, reviewed).** Its rungs call *different*
library routines, so a rung-to-rung ratio silently mixes three unrelated things.
Decomposed:

| factor | what it compares | size |
|---|---|---:|
| **library** | glibc `strlen` (IFUNC → AVX2) vs `core::slice::memchr` (SWAR, no xmm/ymm) | **12.0×** |
| **spelling** | `CStr::from_bytes_until_nul` vs `iter().position()`, both safe Rust | **5.3×** |
| **safety** | checked vs unchecked **at matched spelling** | **3.00000 Ir/byte** |

Only the third is a safety number. Reported as a single ratio, p11's R1-vs-R3 gap
would have read as a 60× "cost of safe Rust" and none of it would have been safety.

**The rule: whenever two rungs call different library routines, name the routine
beside every rate and difference rates only within a routine.** This is the
library-level analogue of the matched-spelling rule and it has the same failure
mode. Two calibration figures on this box, both AVX2: glibc `strlen` **0.0788
Ir/byte**, glibc `memchr` **0.1023** — 31% dearer, because `memchr` must also test
its count.

⚠ **And the kernel-exclusive `Ir` column cannot see any of it.** A routine called
*out* of the kernel symbol is not in that column. Measured across all eight
patterns (TASK_034, ratio-disagreement between the kernel-exclusive column and
`marginal_ir_per_call`, and the count of rung pairs whose **order inverts**):

| pattern | worst disagreement | inverted rung pairs |
|---|---:|---:|
| **p08** | **2.2315** | **10** |
| p11 | 0.7839 | 3 |
| p02 | 0.1895 | 0 |
| p01 / p05 / p07 / p16 / p17 | ≤0.0052 | 0 |

**p08 is the sharpest instance, not p11** — on that column `c-gcc` reads **58%
dearer** than `c-clang` where the marginal says **33% cheaper**, i.e. a C-vs-C
comparison reversed. p11 distorts by 43% of a cell and inverts three pairs; p02
distorts and inverts nothing.

**The author-checkable test, which needs no disassembly** (and is now the
generated boilerplate in `results/tables/*.md`): every rung runs the same input
the same number of times, so **rung-to-rung ratios of the kernel-exclusive column
must agree with the same ratios of `marginal_ir_per_call`**, which is
symbol-independent. Where they disagree, the marginal is the one to publish.
Note what does *not* work: the table prints no call column, and `bulk_calls` in
the gate record names only *recognised bulk* routines — p11's
`<CStr>::from_bytes_until_nul` never appears there.

### Staleness: `harness/measure.py --check-stale`, and why a COMMIT test is not the test

**TASK_034 found that `results/*.json` had no staleness detector; TASK_035 built
one and showed the manager's way of sizing the damage was wrong three times.**

**The mechanism now exists.** `measure.py` writes **`source_sha256`** (18 files
per pattern: the rung sources, `c/*`, `model.py`, `inputs/gen.py`,
`common/driver.*`, `common/slb.py`, `harness/{build,asm,measure}.py`,
`verus_run.py`) **and `input_sha256`** (the matrix blobs the run actually opened).
The rule in its comment block is *"a file belongs iff editing it can change a
number this record prints"*, and the exclusions each carry a checkable reason —
`report.py` renders *from* the record; `check.py`/`vparse.py`/`dloop.py`/
`fixture.py` certify rather than build or measure; `controls/*.py` are not in
`build.all_cells()`.

```
harness/measure.py --check-stale        # exit 1 on STALE; covers BOTH record families
  STALE | GEN-ONLY | NO BASELINE | MISSING | FRESH | SKIP
```

`GEN-ONLY` is the verdict that keeps two true facts from colliding: `gen.py`
moved but every matrix blob it produces is byte-identical, so
`.memory/05-layout.md`'s *"a sweep band costs one gate re-run, not a re-measure"*
stays literally true while "the inputs changed under this record" is still caught
— and caught better than a generator hash alone, which cannot tell a comment edit
from a data change.

⚠ **A commit test is NOT the test. Hashes are.** The manager sized the damage by
comparing each record's `git_state.commit` against the last commit touching
`common/driver.c`. That method was wrong in both directions:

- **p16 was never at risk.** Its rungs call `driver::head1_u64_bytes`, which that
  commit *added* — a p16 binary **cannot be built** against the older driver. Its
  record was taken from a dirty tree that already had it (`dirty: true`). Measured:
  **0 deterministic leaves moved**, 96 wall leaves and nothing else.
- **p11 WAS at risk, and the commit test could not see it** — the file that moved
  was `harness/asm.py` (`_BULK_STR_WORDS`), landed *after* p11's record. So
  `results/p11-nul-scan.json` records the C rungs calling **no bulk routine**,
  where p11's own headline is that glibc `strlen` is a 12.0× library factor.
- **p01 was at risk and did drift**, as reported: `md5_fn 2fe6ada7…` →
  `4104f391…` with `md5_fn_norel` equal and `n_fn`/`fn_bytes` unchanged, i.e.
  displacements only, plus 5 `binary_text_bytes` on C cells (none published
  anywhere).

**And the damage was small where it mattered: `Ir` is bit-identical on both
re-measured patterns.** p16's null re-derives exactly — R3−R4 = **27 / 77**
(`7+5·nrec` / `7+7·nrec`), R5−R4 = **0.00**. **Proved rather than argued**: p01
built against both drivers gives the *same* kernel `Ir`, the *same* whole-program
`Ir`, and identical rung-to-rung differences on both columns for all five rungs.
gcc/clang link the unused TU (+160 / +144 B of `.text`); rustc drops it before
codegen — the asymmetry this file already records, reproduced.

**Status: 0 STALE. But "0 stale everywhere" would overstate it** — p01 and p16 are
`FRESH`, the other six are **`NO BASELINE`** (their records predate the key) and
each clears on its next run. The deterministic half was closed by rebuild instead:
252 cells, 5544 static leaves, **6 moved**, all of them p11's `bulk_calls`.

**Do not make this a `check.py` stage.** Only `measure.py` can refresh a
measurement record, and `measure.py` is inside the gate's own hash — a gate stage
would hard-fail every pattern until each is re-measured, coupling gate greenness
to a full matrix re-measure. Run it before quoting a number.

⚠ **`check.py`'s own `harness/*.py` glob is over-broad, and the cost is now
measured.** `check.py` imports `asm`, `build`, `vparse`, `dloop`, `fixture` — **not
`measure`, not `report`** — yet hashes all of `harness/*.py`. TASK_035's
`measure.py` edit therefore cost **eight full gate re-runs, 13 minutes**, for a
file the gate never executes; p01's gate diff was one line. Narrowing it to the
five imported modules plus `check.py` is a judgement call (belt-and-braces cannot
under-cover, and the tax is per edit event) — but it is the same false positive
this project warns about one level up.

### `results/*.json` is kernel-exclusive for EVERY pattern — there is no p03-vs-p11 rule conflict

**Checked at TASK_036_REVIEW.** `results/p03-bounded-stack.json`,
`results/p11-nul-scan.json` and `results/p16-tlv-walk.json` all carry the
*identical* protocol string — *"callgrind per-function exclusive Ir, kernel symbol
only; whole-program summary deliberately not recorded"* — because it is
`harness/measure.py`'s hardcoded protocol for every pattern. p11's and p03's
`NOTES.md` prose about **which column to quote** is a compatible refinement of
that, not a contradiction:

- **p11**: the *rungs call different library routines*, so the kernel-exclusive
  column omits different amounts per rung and the **whole-program marginal** is
  what its rung comparisons must use.
- **p03**: its `[0u64; 64]` lowers to a `memset` whose path length depends on the
  array's alignment — which moves with **the probe file's path length** (±7
  Ir/call on byte-identical kernels) — so the **kernel-exclusive** column is the
  stable one.

**The discriminator is not "does the kernel call out". It is: does the callee have
a data-dependent path length, and is that dependence shared by every rung?**
p03 is also the second pattern whose whole-program marginal does not cancel the
environment, and the first where the mechanism is a **stack** buffer's alignment.

### `measure.py`'s `ns` column is a whole-process LEVEL, never a difference

⚠ **Project-wide, measured at TASK_038_REVIEW, and it changes every published
wall-clock ratio.** `measure.py` times whole process invocations, so **the
per-process constant — argv, file I/O, payload decode, process setup — is inside
every number.** On p09 that constant is **55% of the `small` figure and 73% of
`large`**; on `large`, 7.15 ms of R4's 9.75 ms is just the 8.2 MB payload read.

**Subtract it.** Run the same blob with `n_iters` rewritten to **1** and difference
— the marginal construction this file already endorses for `Ir`:

| pair | `Ir` | `ns` as published | `ns` kernel-only |
|---|---|---|---|
| p09 R3−R4 `small` | +205.6% | +99.1% | **+215.4%** |
| p09 R3−R4 `large` | +199.4% | +50.2% | **+183.1%** |
| p09 R2−R4 `small` | +148.5% | +58.0% | **+125.6%** |
| p09 R2−R4 `large` | +148.5% | +26.5% | **+100.0%** |

**A whole mechanism died on this.** p09 published "the extra instructions retire
far cheaper than the average instruction" (ILP) from a 2–4× `Ir`-vs-`ns` gap.
Corrected, **the largest surviving factor across four runs is 1.5×, not 2–4×** —
so the ILP reading dies either way. ⚠ **But name the blob** (TASK_039): R3's `ns`
penalty exceeds its `Ir` penalty **on `small` only** (+215…+220% against `Ir`'s
+205.6%, a dead heat to +7%); on `large` it stays *below* at +179…+183% against
+199.4%.

**Rules:**

1. **Never quote a wall-clock ratio off the raw column.** Quote the level if you
   must, and label it *"includes the per-process constant"*.
2. **The ±9-point bar lives in the CORRECTION, not in the level** (TASK_041):
   p12's raw `min_s` reproduced within **1.0 point on all eight cells** across
   sessions, while the corrected `R5 − R4` spanned **+0.21 … +5.94%**. The
   `n_iters = 1` pass is the noisy half — its own `min` wanders by >1 ms between
   cells within a single pass. So quote the raw level when you can, and treat the
   corrected ratio as the derived, wider quantity.
   The correction subtracts two noisy minima, so it is **noisier than the raw
   column**, and the residual is a **session property**: `R5 − R4` — which must be
   0, the kernels being byte-identical — read **−0.9%, +2.6%, +2.7%, +8.7%** over
   four runs (TASK_039). **Quote ±9 points as the error bar**, and only quote a
   corrected ratio when the effect clears it by a wide margin: p09's R2/R3 rows
   clear it by **11–25×**, not the 25–80× first written.
3. This is orthogonal to the layout modes below. Do **both**.

### This box's `ns` noise floor is a SESSION property, not a constant

**Measured at TASK_035, and it is why a wall-clock row can stop being quotable
without anything in the tree changing.** The *same* p16 binaries, three days
apart:

| | between-cell band, `small`, 16 `-O3` cells | within-cell min→median |
|---|---|---|
| original session | **12.69…12.85 ms (1.3%)** | 0.96…2.31% |
| TASK_035 session | **12.28…13.28 ms (8.2%)** | 3.64…12.04% |

Four cells tripped the 10% discard rule and
`results/tables/p16-tlv-walk.md` now carries a **DISCARD banner**. It is the box,
not the tree: an independent re-time of the same binaries with the shipped
`measure.wall()` read 12.19…13.04 ms (7.0%). **So a quiet-session figure cannot be
refuted by a noisy session — only left unresolved**, which is the state
`p16/README.md`'s "all 16 `-O3` cells within 1.3%" is now in.

### The byte-identical R4/R5 pair is a SMOKE ALARM, not a null control

**Proposed at TASK_049 as a free null the project already had; refuted at
TASK_049_REVIEW and restated at TASK_050, on two patterns.** It is an appealing
idea — R4 and R5 have byte-identical kernels and *exactly* equal `Ir`, so any
`ns` difference between them looks like pure measurement noise, and it costs
nothing because every pattern already ships the pair.

**It is a biased sample of size one.** On p06 and p14 the `verus` build's kernel
lands **0x20 below** the `unsafe` build's — the same two addresses on both — so
the pair samples one fixed `addr % 64` alignment contrast **every time you run
it**. ⚠ **The 0x20 is not universal and must not be quoted as a law**: p18's
R4/R5 pair lands at **offset 0** (PROVISIONAL — p18 is not yet reviewed), which
biases that pair toward reading ≈0. **What generalises is that the offset is
FIXED per pattern, not that it is 0x20** — either way the pair is one draw, not
a sample. p14's kernel is bimodal there (`%64==16` costs 264–277 ns, `%64==48` costs
244–248), its shipped `unsafe` sits in the fast class and its shipped `verus` in
the slow one, and the pair reads **+8.95%**. That is not noise and it is not a
floor: over a 24-layout population the pair's **median is ≈0** on both patterns
(p14 −0.07% paired, +0.27% across 576 cross-pairs, `P(R5>R4) = 0.559`), and the
+9.2% figure **under-states** the 13.22% within-cell layout spread it claimed to
bound.

> **The floor is the LAYOUT POPULATION.** Use the R4/R5 pair to notice that
> something is alignment-sensitive — it agreed to 0.06 pp across two passes
> precisely because it re-sampled the same draw — and never as the number a
> published `ns` figure has to clear.

**Consequence already landed:** p06's `NOTES.md` floor moved **±3% → ±4.6%**
(its own measured spread is 4.02% `unsafe` / 5.10% `verus`, cross-pair range
−4.31%…+4.61%). **p06's headline is intact** — its clang column clears ±4.6% at
~2.1× and its 30-layout C population defends it independently.

⚠ **And the fetch-grid spacing is a PARAMETER, which nobody had varied.**
PROVISIONAL — measured at TASK_050, not yet reviewed. `loopfit.kernel_report(…,
boundary=N)` has always taken it and every prior use was 32. On p14 the 32-byte
predicates are **coarser than the effect**: they merge the fastest class
(`%64==48`) with the slowest (`%64==16`). The sharp predicate is **`jcc32`
computed at boundary 64** (10 of 48 binaries, +7.2%, `perfect=True` on the
`verus` sub-population). The layout section below says *partition by
`win32`/`jcc32`, not by an address bit* — still right, **but 32 is not always the
grid to compute them on.**

### `common/layout/order.py` appends `.bin` — and a nonexistent file reports a clean null

**TASK_042.** `--input small.bin` silently times `small.bin.bin`. Every rung then
measures ~4.5 ms of process startup and nothing else, and `R2 − R4` reads
**+0.15%** — a tidy, publishable-looking null produced by a file that does not
exist. It exits 3, which is easy to miss in a loop.

**Pass the stem (`--input small`), and cross-check any `ns` null against the `Ir`
column before believing it.** That cross-check is what caught this one: +141% `Ir`
against a +0.15% `ns` null is not a conversion factor, it is a broken measurement.

### Interleave by CELL, never by block — it alone flipped a sign

### Interleave by CELL, never by block — it alone flipped a sign

**Measured at TASK_031, on 31 byte-identical copies of one binary.** A timing
probe that iterates a dict filled cell-by-cell gives each cell a *contiguous
block* of every rep instead of alternating. `harness/measure.py:wall()` and
`.memory/03-measurement.md`'s timing protocol both alternate; a hand-rolled probe
easily does not, and the docstring will still say "interleaved".

Same 31 identical copies, same machine, one layout, only the loop order changed:

```
ALTERNATING   R2 vs R4  +28.08%      R3 vs R4   +1.21%
BLOCKED       R2 vs R4   +6.00%      R3 vs R4   -4.16%      <- sign flips
BLOCKED, slot-0 only     +17.31%                -11.70%
```

**Every reading TASK_030_REVIEW attributed to p05's shipped layout is reproduced
here with no layout variation at all**: the "shipped R2 is rank 30/30, shipped R3
rank 0/30" ranking, the `−9.91/−11.57%` R3 figure, and the `+7.17%` "population"
value. So was the `--symbol-ordering-file` "lever bias".

Two rules follow:

1. **Alternate by cell.** Build a flat interleaved list; do not iterate a
   per-cell container. This costs nothing and it is the difference between a sign
   and its opposite on an unstable cell.
2. **Measure the noise floor with byte-identical copies before believing any
   layout or spelling effect.** Build the *same* source N times, time them as a
   population, and compare the spread to the effect:

   | pattern (`small`) | identical-copy floor | 30-layout band |
   |---|---|---|
   | p01 | 0.82…3.17% | 10.42 / 10.15 / 7.74% |
   | p07 | 0.83…2.24% | 31.76 / 17.12 / 8.08% |
   | **p05** | **4.19…14.83%** | 14.09 / 8.30 / 9.34% |

   p05's band is *inside its own noise floor*, which is why its `small` row is
   withdrawn and p01's and p07's are withdrawn for a real reason.
   (⚠ An earlier version of this row said 5.09…45.04% — that was the max over
   blocked *and* alternating blocks together, i.e. it included the artefact. The
   alternating figure is the honest one and the conclusion is unchanged.)

3. **Run the protocol control on every pattern before trusting any of its layout
   verdicts.** Done for all seven at TASK_032, ~8 minutes; **p05 is the only
   protocol-sensitive pattern**, and its row was already withdrawn — so the bug
   reached no surviving published verdict:

   | pattern | alternating | blocked | identical-copy floor | sensitive? |
   |---|---|---|---|---|
   | p02 R2 | +17.35 / +16.69% | +17.12 / +16.43% | 1.0–3.4% | no |
   | **p05 R2** | **+30.31 / +30.07%** | **+7.56 / +7.93%** | 4.2–21.0% | **YES** |
   | p08 R2 | +104.72 / +105.44% | +104.64 / +104.82% | 0.58–1.30% | no |
   | p16 R2 | −0.15 / −0.25% | −0.13 / −0.20% | 0.61–1.50% | no |
   | p17 R2 | −0.18 / +0.05% | −0.03 / +0.04% | 0.55–1.00% | no |

   p16's and p17's "gap < 1% either way" are therefore **clean negatives under
   both protocols**, which had not been established before. p01 and p07 are
   protocol-insensitive too (p07 R2−R4 reads +27.46…+27.77% blocked *and*
   alternating), which is how their modes were separated from the artefact.

**The tool ships: `common/layout/`.** `order.py` is this control, `layout_gen.py`
the population builder (its `round_robin()` is the scheduler, and `order.py` and
`predict_then_time.py` **import** it so the probe tests the shipped code rather
than a copy), `loopfit.py` the mechanism, `predict_then_time.py` the
pre-registration harness. `common/layout/README.md` has the recipes.

### Code layout: the 32-byte fetch grid, and why two patterns' `ns` columns are withdrawn

**TASK_026 → TASK_029 → TASK_030_REVIEW.** The final reading is TASK_030_REVIEW's,
measured on **all seven patterns**; it corrected four things the two earlier
tasks (and this file) had wrong. Read this section as the current one and ignore
any "band" or "bit 4" phrasing elsewhere.

#### What it is

Two binaries built from identical source, differing only in where the linker put
the kernel — same `n_fn`, same `md5_fn_norel`, same executed instruction stream —
can differ by **up to 27% of wall clock**, and the difference can **flip the sign
of a rung-to-rung comparison**.

**The mechanism is the 32-byte instruction-fetch / DSB window grid**, in two forms,
both computable statically from the disassembly with **zero fitted parameters**:

- **`win32`** — the loop body occupies one more 32-byte fetch window in one
  layout than the other. p01's `unsafe` SSE loop is 30 bytes: entirely inside one
  window at one residue, straddling two at the other (`movdqu` spanning bytes
  27..1). That is the whole mode.
- **`jcc32`** — a loop branch crosses or ends on a 32-byte boundary, so the chunk
  is not cached in the DSB. This box is **Cascade Lake (family 6 model 85 stepping
  7, µcode `0x5000024`)**, which carries the mitigated microcode for the **Jump
  Conditional Code erratum, Intel SKX102**.

⚠ **"Bit 4 of the kernel's entry address" is a PROXY, not the law.** It works only
because every kernel here is 16-byte aligned, so a 32-byte-granular property takes
exactly two values. A toolchain with 32-byte function alignment would erase the
proxy and leave the effect. Partition by `win32`/`jcc32` computed from the
listing, not by an address bit.

**The geometry flip is universal; being front-end-bound is not.** p02, p05, p16
and p17 all have loops whose `win32`/`jcc32` flips with layout exactly as p01's
and p07's do — and their time does not move. p07 is not special in layout; it is
special in having a serial 73-byte loop where one extra fetch window is 33% more
front-end work.

#### Where it bites — measured, all seven patterns, 30 layouts each

| pattern | verdict |
|---|---|
| **p07**, **p01** | **real mode, perfectly separated**; comparisons flip sign |
| p08 | marginal (R2, ~3%) — the +105% gap survives it easily |
| p02, p05, p16, p17 | **absent** (best bit ratio ≤ ×1.003, never perfect) |

```
pattern in    rung        published   pooled    mode0    mode16   verdict
p01    small safe_naive     +5.40%   +1.16%   +5.24%   -4.10%   SIGN FLIPS
p01    small safe_tuned     +4.72%   +1.44%   +7.01%   -5.67%   SIGN FLIPS
p02    small safe_naive    +18.04%  +16.75%  +16.68%  +17.03%   survives
p08    small safe_naive   +105.16% +104.77% +104.43% +110.05%   survives
p16    small safe_naive     -0.41%   -0.03%   +0.08%   -0.13%   gap <1% either way
p17    small safe_naive     -0.22%   -0.09%   -0.12%   -0.18%   gap <1% either way
```

⚠ **The `published` column is each pattern's record AS OF TASK_030_REVIEW, and
p01's has since moved.** Its TASK_035 re-measure reads **+5.71% / +4.30%** against
the +5.40% / +4.72% above — same sign, same class, **column still withdrawn**.
That a single-layout reading of a bimodal cell is not reproducible to 0.3 points
is this table's own point, so no verdict moves; only the label is stale.
**Re-derive that column from `results/*.json` rather than quoting it from here**,
and run `harness/measure.py --check-stale` first.

**Confirmed out of sample, pre-registered**: predictions written and SHA-256'd
*before* any timing, on 20 fresh symbol orderings — p01 all three rungs held with
perfect separation on both passes; p07 `safe_naive` held.

⚠ **`large` is smaller, NOT safe.** p07 R2's mode is perfectly separated on
`large` too (×0.970, three passes) and mode-matched R2-vs-R4 there is **+3.28% vs
+0.38%** — an 8× swing on the same partition. An earlier version of this section
said memory-bound inputs are "far safer"; that invites the single-layout reading
that failed.

#### The statistic to publish

1. **Mode-matched comparison** — partition by `win32`/`jcc32`, compare within a
   mode, report per mode. **A sign that flips between modes is not a sign.**
   Converges: medians flat in `N`, spread ~1/√N.
2. **Pairwise `P(A > B)`** over all `N²` layout pairs. A genuine proportion, flat
   at every `N` (58.1 → 58.4 across N = 4…30).

⚠ **Two statistics this section previously recommended are RETRACTED, both because
they are extrema and neither converges:**

- **worst-vs-best range / "disjoint bands"** — widened 28.91% → 30.78% on the same
  binaries by adding samples, and flipped a verdict;
- **dominance** ("slower than the *worst* layout of B") — p01 R2 drifts 28.7% at
  `N = 4` → 13.3% at `N = 30`, sd ±26 points at `N = 4`. It was introduced *as the
  fix for the range* and has the same defect. The claim that both replacements
  "are proportions rather than extremes" was wrong about this one.

#### Building a layout population

- **`-C llvm-args=-align-all-functions=N`** — moves the kernel inside `0x300`.
  Cheap; enough to *detect* a mode.
- **`-C link-arg=-Wl,--symbol-ordering-file=<f>`** (rust-lld) — moves it
  arbitrarily far, at unchanged `n_fn` and unchanged instruction stream.
  ⚠ It permutes all 582 text symbols, so it moves the driver, libstd and startup
  too. **The measured evidence that this biases results is WITHDRAWN** — the
  +5–10% `order`-vs-`align` gap was the blocked-ordering artefact below, and
  TASK_031 reproduced it on byte-identical copies (blocked +3.90/+5.30%,
  alternating −0.98…+0.36%). The lever may still be impure; nothing measured shows
  it. Use both levers to detect a mode, and do not quote a pooled band across the
  mixture as "the layout band" — that caution stands on its own.
- Two levers that do **not** work: a padding object via `-C link-arg` (rustc
  appends it after the crate's `.text` and passes `--gc-sections`), and
  `-align-all-nofallthru-blocks` (nops *inside* the kernel — not byte-identical).
- **Enumerate every loop.** A "tightest backward branch" heuristic picks the wrong
  one on any vectorised kernel (on p01 it finds the 12-byte scalar tail instead of
  the 30-byte SSE loop). `.temp/r30/loopfit.py` does it properly.

#### Verify invariance with `md5_fn_norel`, NOT `md5_fn`

⚠ A kernel that can `call` a panic path produces a **different `md5_fn` at every
layout**, because the `call rel32` displacement moves — 28–29 distinct digests
over 30 layouts, on *every* pattern. `md5_fn_norel` and `n_fn` are the invariants.
Following the `md5_fn` recipe, you conclude the code changed and abandon the
control.

#### Two published rows are withdrawn

- **p01's `small` R2/R3 `ns` cells** — sign flips with the mode.
- **p05's `small` R2/R3 `ns` cells** — a *different* defect, and the reason
  published at TASK_030_REVIEW was itself wrong. ~~"The shipped binary is the
  slowest R2 layout of 31 and the shipped R3 the fastest, so +36.01% is
  worst-against-best where the population says +7.17%."~~ **That ranking is a
  measurement artefact, reproduced at TASK_031 with ZERO layout variation** — see
  the interleaving rule below. The real reason is simpler and worse: **p05's
  `small` cell's noise floor on byte-identical binaries is 5–45%, wider than any
  gap anyone has read off it.** Under the project's own alternating protocol,
  R2−R4 is ≈+30% across 17 measurements and R3−R4 is +1.2…+6.9%, always positive.
  The cell is not quotable; p05's `large` row is.

### A per-byte rate from a marginal pair is good to ±0.09, not to five decimals

**Measured on p16 at TASK_027, and it lands on this project's most-quoted
number.** The driver's `println!` costs **0.2263 Ir per call per decimal digit**
of the checksum it prints. In a residue-matched marginal pair that residual is
divided by only `nrec·K` folded bytes, so a rate read off two runs carries

```
error  =  0.2263 · Δ(Δdigits) / (nrec · K)
```

Over a 130-length sweep that is, as a *measured slope*:

| fold | measured range | exact (`body/K`) |
|---|---|---|
| shipped, `K = 4` | **5.64750 … 5.82500** | 5.75000 |
| `chunks_exact(32)` | 5.08266 … 5.10313 | 5.09375 |
| `chunks_exact(64)` | 5.04219 … 5.05156 | 5.04688 |

**So p16's shipped 5.7500 — published since its §3 — is the least reproducible
rate in its own table, ±0.09 Ir/byte**, precisely because the shipped fold has the
smallest `K`. Subtracting the predicted digit term drops the residual to 0.0266 /
0.0045 / 0.0017, which confirms the term is the whole error.

**The rule: a five-decimal per-byte rate must come from the disassembly
(`body_len / K`), never from a two-point or few-point marginal.** A *difference*
of two rates at matched spelling is exempt and is exact — both rungs print the
same checksum, so the term cancels identically — which is why p16's 0.0000000
null survives at five decimals while the rates it is a null between do not.

### `marginal_ir_per_call` does not always cancel the environment block

This file already says whole-program totals move with the environment block
(argv, envp, the `PAD`-style padding a different shell hands you). What TASK_017
measured is that **differencing two runs does not always cancel it**:

```
p08  padlen=  0   marginal/iter = 7292.26
p08  padlen=200   marginal/iter = 7292.24
p08  padlen=400   marginal/iter = 7292.14
p16  padlen=0/200/400            = 3009.30 / 3009.30 / 3009.30   (control: invariant)
```

Byte-identical binary, byte-identical probe inputs, only the env block's length
changed. It is **p08-specific and mechanistic**: p08's per-iteration work runs
through glibc `memcpy`/`memmove`, whose path length depends on buffer alignment,
and the env block shifts the stack. p16, which calls no bulk routine, is exactly
invariant.

**Demonstrated at symbol granularity, not inferred** (TASK_017_REVIEW): at
PAD 36→40, `unsafe::main` and the `memset` are bit-identical, and **100% of the
drift is inside the `memmove`** at `libc+0x188a80` (196.96 → 197.00 Ir/iter).
It threatens **no published p08 number** — `R1h − R1 = 0.00` measured exactly
0.00 across 12 argv/env configurations.

Consequence for gate hygiene: **"every `marginal_ir_per_call` cell unchanged" is
a valid *within-session* invariant (96/96 across three p08 runs) and NOT a valid
cross-session one**. **There are TWO non-cancelling terms, and separating them
took four tasks and two wrong numbers** — see the box below. Do not read
such a drift as a code change, and do not quote p08's marginals to more
precision than that.

### Gate records carry per-run noise — subtract it before claiming a leaf moved

Measured at TASK_022 on unchanged trees, two consecutive runs:

- **p05: 4 leaves.** The `adversarial-dims` heap-OOB stdout for c-gcc and
  c-clang (genuinely nondeterministic — it reads past the allocation), plus two
  ASan PID/ASLR diagnostic strings.
- **p08: 23 leaves** — `marginal_ir_per_call`, across **all four** opt/mode
  combinations (not just `O0`/`whole`), to **±0.08**. TASK_022 recorded 8 and
  `O0`/`whole` only; TASK_023_REVIEW reproduced the **identical 23 keys on an
  unchanged tree**, which is what makes them noise rather than an effect.
  ⚠ **The count is not a constant and not even monotone.** Recorded values across
  four runs: **8 → 23 → 75 → 0** (TASK_022 / TASK_023_REVIEW / TASK_028 /
  TASK_032). Same magnitude every time (`10452.64 → 10452.72`, ±0.08), same key.
  It is **intermittent, not a growing per-run cost**, and each of the first three
  was written down as if it were *the* number. **Quote the magnitude and the key;
  budget "0…75"; re-measure the count.**
- **p02: 3, p16: 1, p17: 1** — previously unrecorded.
- **Total churn on an unchanged tree: 32 leaves at TASK_022/023, ~114 at
  TASK_028** (the p08 growth plus 5 ASan PID strings and p05's 2 nondeterministic
  `adversarial-dims` stdouts). Budget by *class*, never by count.

**TASK_021_REVIEW's clean negative 6 attributed exactly those 8 p08 leaves to an
edit.** They move on an unrelated edit too, so they are run noise, not an effect.
Any "N leaves moved" demonstration must subtract these first — the technique is
otherwise sound and is how the `source_sha256` gap was proved closed.

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

## The kernel-exclusive column is comparable only when the rungs call the SAME libc routines

(TASK_045_REVIEW, on p13 — the first pattern whose rungs differ in **which**
library calls they make. Two published figures moved.)

`kernel_exclusive_ir` counts the kernel symbol and **not** what it calls. That is
the right column when every rung dispatches the same work outward — p03's and
p04's `memset` for a stack array, where the callee's path length moves with
alignment and the noise is the only thing excluded. **It is the wrong column when
the rungs dispatch DIFFERENT work outward**, because then the column silently
credits a rung for the work it moved into libc.

p13's rungs: `c-gcc` calls `strlen`; `c-clang` calls `strlen` + `memcpy` +
`memset`; `safe_naive` calls `memset` only; R3/R4/R5 call `memcpy` + `memset`.
Measured consequences:

```
gcc-vs-clang gap     kernel column  494 Ir/call   ->  totals  188
R2 - R4              +1119 (+70.3%) / +2817 (+43.2%)
                 ->  +929  (+47.9%) / +2553 (+35.8%)   on totals
```

The matched-spelling safety tax was overstated by **190 / 264 Ir/call**, entirely
because R2 makes no `memcpy` call and R4 does.

**The rule**: before quoting the kernel column for a cross-rung difference,
**list the `@plt`/`@GLIBC` calls of every cell and check the lists are equal.**
If they are not, quote totals, or quote the kernel column **plus the libc
marginals per rung**, and say which. Equal lists is the licence; it is one
`objdump` per cell.

## Hold out a LENGTH, not a MIXTURE — an out-of-sample test can be provably unable to fail

(TASK_045_REVIEW, on p13. This **sharpens the section below**, which was written
after p04 and asked for "one blob that turns on every regressor at once". That is
necessary and it is **not sufficient**.)

⚠ **SECOND INSTANCE, and the general test is one line of linear algebra**
(TASK_049_REVIEW, on p14). p14's leave-one-length-out reported
`max|residual| = 0.0` over 29 hold-outs — because **an exact fit plus a design
that keeps full rank after the drop makes leave-one-out arithmetically incapable
of failing**: each hold-out re-derives the same exact solution. p14's design
stays **rank 4 after dropping any whole band** (`-l*` n=50, `-t*` n=50, `-m*`
n=37, `-x*` n=61 — all rank 4).

> **Report the post-drop RANK beside any hold-out claim.** A residual of exactly
> zero is not a strong pass; it is the signature of a test that could not fail.
> If the rank survives the drop, say so and rest the law on something else — an
> exact fit plus genuine out-of-sample *predictions* is honest evidence; the
> hold-out is not.

**p06 is the counter-example that shows the test has teeth**: its LOLO *can*
fail, and does — it misses by **−48.000 at `m=3`**, which is how its domain got
established.

If the fit set is **rank `n` in an `n`-column design**, its rows span all of
ℝⁿ — so **every** possible blob's regressor vector is a linear combination of
blobs already fitted, and *no* blob is out of sample in regressor space. A
"held-out" band built by mixing the fit set's own extremes is then a test that
**cannot fail, provably**, and its residuals will read *smaller* than in-sample.

p13's band T is exactly that: every row `= (t/8)·row(L=40) + ((16−t)/8)·row(L=8)
− (1,0,0,0,0)`, verified for all 17 values of `t`, with `(1,0,0,0,0)` itself a
difference of two band-N rows. Its residuals (**4.80 / 14.40** on the corrected tree) were **smaller** than
in-sample, which the delivery flagged against itself without diagnosing. All
**17 of 17** band-T rows are inside the fit set's row space.

**What does work: hold out a value of a structural parameter the model is
linear in, not a mixture of ones you fitted.** Leave-one-*length*-out on p13's
band L (fit `N + L \ {L₀}`, predict `L₀`) gives worst residuals **37.63 … 454.83**
across the five fitted cells — **3× to 95×** what band T reported.

So the out-of-sample protocol is two-part:

1. **A blob that turns on every regressor at once** — catches a law fitted in the
   wrong count vector (p04, below).
2. **A held-out level of a structural parameter** — catches a model that is the
   wrong *shape*. Check the held-out point is **outside the row space of the fit
   set**, or say plainly that it is an interpolation check.

⚠ **And say which estimator produced a residual.** p13's "no law" verdict rested
on residuals from **exact interpolation on 5 chosen rows** (111.57 … 873.21);
ordinary least squares on the same data gives **35.36 … 443.24** — **up to
4.2×**. A "the model does not fit" claim that moves by 4× with the estimator is a
claim about the estimator.

⚠ **And a step basis needs a length-HETEROGENEOUS fit set to be identifiable at
all.** Every p13 fit blob is length-homogeneous, which makes `ceil(f/32)` equal
to `K − T` and `ceil(c/32)` equal to `K` — so the natural step basis is
**singular**, as is every indicator basis. Nothing about the design could have
fitted the step, and the honest report is *"not identifiable here"*, not *"no law
exists"*.

## A fitted law is a law in SOMEBODY's counts — say whose

(TASK_042_REVIEW, on p04. Two of seven "exact integer cost models, max residual
0.0000 over 99 blobs" were wrong out of sample, and **no in-sample blob could
have shown it**.)

A swept law regresses a cell's `Ir` on regressors taken from **`model.py`'s**
execution counts. That is correct **only for cells that execute the model's
program.** An R1 cell with a guard omitted does not: what the model counts as a
*rejected* push, R1 *accepts*. So R1's law is stated in R1's own counts, and it
coincides with the model's only where the two count vectors agree.

**The trap is that a band can zero a regressor by construction and hide the
disagreement.** p04's band F is the only band where the fullness check fires, and
it has `epop == 0` *by construction* — so the licence *"R1's own counts equal the
model's"* was checked exactly where two of its three conditions could not fail.
On a fresh blob with `dpush` **and** `epop` both non-zero — a combination **no
shipped blob had** — the published rows missed by −385 and −330 while the file
said "max residual 0.0000".

Three rules, and the third is the one that costs nothing:

1. **State the regressor set per row**, not per table. If one row is in a
   different count vector, say so on that row.
2. **A self-consistency check that a rank-deficient or degenerate design cannot
   fail is not a check.** p04's was *"R1's `xpush` and `dpush` coefficients come
   out equal"* — real (the design is rank 5, so the coefficient vector is unique,
   and R1h comes out unequal on the same design) but it tests only the first of
   three conditions.
3. **Build one out-of-sample blob that turns on EVERY regressor simultaneously**,
   and predict it before measuring. Ninety-nine in-sample blobs did not catch
   this; one adversarial blob did. Sweep bands are built to *isolate* regressors,
   which is exactly why the pooled design needs a point where none is isolated.

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

**A side record in `results/` can make a table un-regenerable.** `report.py p02`
was a hard error from the moment `p02-residue-sweep.json` was committed — the
prefix matched two files — so `results/tables/p02-buffer-copy.md` could not be
regenerated at all, silently, for two tasks. Fixed at TASK_008 by discriminating
on the presence of a `cells` list. Any new side record in `results/` needs the
same thought.

**A marginal-`Ir` figure carries a per-input `println!` term.** The driver prints
the final checksum, and the number of *digits* differs per input, so the
whole-program `Ir` difference between two inputs includes a few instructions of
formatting that have nothing to do with the kernel. Measured at TASK_011_REVIEW:
it moved p17's swept rates from a true **10.0000 / 5.7500** to a reported
9.9991 / 5.7491. Re-measured independently at TASK_012 on the zero-residue pair
`sw228→sw232`: **10.0000 / 5.7500 / 5.7500 / 5.7500** for R2 / R3 / R4 / R5, plus
**14.0000** for the `i128` variant and **10.0000** for the all-unsigned one. A
non-zero-residue pair drifts visibly (`sw200→sw204` gives 10.1775 / 5.9275), so
**quote a rate only from a zero-residue lag pair**, and say which pair.

Done properly this is *exact*, not approximate: p05's zero-residue pairs give
**1.375000** (= 11/8, an 11-instruction body over 8 elements) and **1.062500**
(= 17/16) — six decimals, both bands, and the fractions fall straight out of the
disassembly. A per-element rate that does not land on a simple ratio of
instructions to lane width is a sign the pair was not residue-matched.

Also measured at TASK_013: **`measure.py` run twice on different cores reproduced
all 42 `kernel_exclusive_ir` figures identically**, while three wall-clock cells
changed discard status. Exactly the split this file predicts — deterministic
columns are portable across runs, the timing column is not. Small, but it is the difference between "reproduces p16's
constant" and "reproduces it *exactly*", and a four-decimal claim cannot afford
it. **Difference two inputs whose checksums have the same digit count** — a
residue-matched lag pair does this for free — or subtract the term explicitly.

**Re-run `measure.py` when the tree moves, and check what actually went stale.**
p01's JSON was four commits behind with `dirty_files: 15`. On re-running:
**all 42 `kernel_exclusive_ir` figures were identical** — including c-clang,
unsafe and verus at exactly 143,740,000 on `large` — but `binary_text_bytes`
had moved in 5 C cells (`common/driver.c` grew when p02 added
`head2_u64_bytes`), and one `md5_raw` had moved with `md5_raw_norel` unchanged,
i.e. link layout only. So "the kernels are byte-identical, therefore the numbers
stand" is right about the kernel columns and wrong about the whole-binary ones.
Say which columns a staleness argument covers.

**Reproduced exactly on p02 at TASK_011**, when `common/driver.c` grew again for
p16's `head1_u64_bytes`: `binary_text_bytes` moved in **10 of 32 cells and all 10
are C**. Static counts, kernel `Ir` and every Rust `md5_fn` were unchanged. The
asymmetry is the useful part and it is not noise: **rustc drops the unused
`driver::head1_u64_bytes` before codegen, while gcc and clang link the whole
translation unit.** So a shared-`common/` addition is invisible to the Rust rungs
and visible to every C one — which means a C-vs-Rust *whole-binary* size
comparison silently charges C for code no pattern calls. Never compare
`binary_text_bytes` across languages without saying this.
