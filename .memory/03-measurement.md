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

⚠ **THE THRESHOLD IS 8192 BYTES EXACTLY, not a range** (TASK_090, PROVISIONAL).
Pinned with a cleaner instrument than a bisection:
`GLIBC_TUNABLES=glibc.cpu.x86_rep_movsb_threshold=1000000` **collapses the
effect** — at n=2048 a clone costs `16740 → 1951` `Ir` — and the per-element
clone cost steps `1.15 → 8.34` between **n = 1024 and n = 1025** on `u64`s, i.e.
8192 bytes. **`rep movsb` is one retired instruction that callgrind charges at
≈1 `Ir` per byte moved**, roughly **10× the vector path's 0.104**.

⚠⚠ **AND "BLAST RADIUS CHECKED AND EMPTY" IS A TASK_074 STATEMENT WITH SIX
PATTERNS BUILT SINCE — see RECAP "Owed" 28.** It has **not** been re-run over
p13, p14, p18, p10, p27, p47, p38, p22, p36 or p19. ⚠ **Do not read it as
current.** Note the distinction the re-check must respect: **what matters is the
size of an individual `memcpy`/`memmove`/`memset` CALL inside the measured
window, not the size of the input file.** p02 copies 61 B and 4092 B out of a
16 KB blob; conflating the two overstates the risk.

⚠ **PROVISIONAL — measured at TASK_074, NOT YET REVIEWED. The threshold does not
merely inflate the number; at the crossing it INVERTS THE DIRECTION, and that is
new.** Probing a zero-fill cost axis (`vec![0; n]` against `MaybeUninit`), rustc
1.97.1 `-C opt-level=3`, whole-program `Ir`:

| `n` | 512 | 1024 | **2048** | 4096 | 65536 |
|---|---:|---:|---:|---:|---:|
| (safe − unsafe) / call | 300.97 | 326.30 | **2106.94** | 4154.94 | 65595.01 |

**The delta jumps 6.46× for a 2× increase in `n`**, at glibc's
`__x86_rep_stosb_threshold` — `libc.so.6+0x18954a` is `f3 aa  rep stos
%al,%es:(%rdi)`, guarded at `+0x1894c0`. **`rep stosb` is what the hardware runs
BECAUSE it is fast, so `Ir` reports the cost rising 6.5× at exactly the size the
real cost falls.** The `memset` flip above is quoted at 3 KiB; this measured one
is at 2 KiB, so **do not trust either constant — probe it at the sizes you are
about to publish.**

⚠ **A law fitted across 2048 has no domain**, and the `Ir/byte` column makes it
look benign: 0.58783 → 0.31865 → **1.02878** → 1.01439 → 1.00090. **A fit banded
below the threshold extrapolates into a different regime with no in-sample
residual to warn you** — the RESIDUE-CLASS rule's shape, in a different variable.
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

### ⚠ The two conventions can differ by 13×, and p08 is where. NAME THE ONE YOU USED.

**TASK_056, measured; unreviewed — and this one propagated from a probe report
into a manager's task file before anyone noticed.** The section below says the
two conventions differ and to name which. **On p08 they do not merely differ,
they differ by an order of magnitude**, and quoting the wrong one understates a
published price by 13×:

```
respelling p08's R4/R5 load, -O0, per call
  kernel-exclusive `Ir` on `kernel`  (measure.py::callgrind_ir)      +2.00
  whole-program marginal            (check.py::_callgrind_total)    +27.00
  gate record `marginal_ir_per_call`                                +27.00
```

The mechanism is that the respelling moves work **into callees**: `index_mut`
10+25 becomes `split_at_mut` 35+25, so +25 of the +27 never appears in
`kernel`'s exclusive count and only +2 (an ABI shuffle) does.

> **A number taken with `callgrind_ir` is a *different measurement* from one
> taken with `_callgrind_total`, not a rounding of the same one. Say which tool
> produced it. When a change RELOCATES WORK ACROSS A CALL BOUNDARY, the
> kernel-exclusive column is blind to the part that moved, so publish the
> marginal too and say why.**

⚠ **THIS BOX USED TO ASSERT THAT `results/tables/*.md` READ
`marginal_ir_per_call`. IT IS THE OPPOSITE, AND THE TABLES SAY SO THEMSELVES**
(TASK_058, read-only audit). Every generated table's own header reads:

> *"`Ir` is **callgrind per-function exclusive** for the kernel symbol. The
> whole-program total is deliberately absent: it moves with the size of the
> environment block and does not reproduce across shells."*

and `:699` below says the same of `results/*.json`. The false sentence conflated
two different things: **`results/tables/*.md` are uniformly kernel-exclusive**,
while *"every published price"* varies **per pattern's `NOTES.md`** — which is
exactly what the next section is about (p16 kernel-exclusive; p05 and p17
marginal).

**What survives, and it is the substantive half:** pricing p08's respelling at
`+2.00` was still wrong, because +25 of the +27 **moved into `split_at_mut`**
rather than disappearing. The right correction was *"the exclusive column cannot
see relocated work"*; *"the tables read the marginal"* was a wrong reason
attached to a right conclusion, and the manager repeated it in a task file and a
handoff before the audit caught it. ⚠ **A right answer with a wrong justification
propagates exactly like a wrong answer** — this one survived three commits.

⚠ **p08 is one of exactly two patterns whose own table already warns that the
kernel-exclusive column REVERSES real comparisons** — which is precisely why it
was the wrong column to price a p08 change with, and the warning was sitting in
the file the whole time.

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

### ⚠ `harness/build.py` is hashed into the MEASUREMENT records, not just the gate records — so a `build.py` edit costs a full re-measure

**TASK_056, measured. This is why `O3d` is NOT a first-class build mode.**

The batching rule everyone has been using — *"a `harness/` edit makes all 16 gate
records stale, so batch the fixes and pay one ~30-minute gate re-run"* — is
**true of `check.py` and FALSE of `build.py`.** `build.py` is in
`source_sha256`, so editing it makes **`results/pNN-*.json` stale too**, and
clearing *those* means re-running callgrind over the whole matrix: **hours, not
30 minutes.**

**And the real cost is not the compute, it is the prose.** `measure.py` re-takes
the **wall-clock** block, and this box's `ns` floor is a *session* property (see
above): a p08 re-measure taken the same day read **~18% lower on every `large`
cell, including cells that had not changed by a byte**. Re-measuring ten patterns
to clear a hash would move ten patterns' published timing rows and stale every
sentence quoting them.

⚠ **THE ≈18% FIGURE IS RETRACTED AS A GENERAL ESTIMATE — it is a p08 one-off,
and it is now the OUTLIER of four observations** (TASK_077/078). Measured
across re-measures of unchanged cells: **p08 ~18%**, **p10 ~8%**, and **p38
median 0.50% / max 3.62%** — and on p38's `large` band the mean movement is
**−0.22%, sign-mixed (−1.52 … +0.89), with no level shift at all.** ⚠ **Do not
size a re-measure's prose cost at 18%.** The honest statement is that the shift
**varies by pattern across at least 0.2% … 18%**, so the cost is *"unknown until
measured, and it has been small three times out of four."*

✅ **And the decision it was used to justify still stands for a better reason**:
a re-measure moves *which cells are discarded* (see the 10%-cliff note in the
protocol section below), which is a **presentation** change that no amount of
timing stability prevents.

> **Decision recorded at TASK_056: the `O3d` mode was built, measured inert (all
> 24 `(opt, mode, panic)` tuples byte-identical), and then REVERTED** — because
> the choice was between a permanently red `--check-stale` (which destroys the
> signal the project's own "before quoting any number" rule depends on) and
> churning ten patterns' timing prose. The axis stays reachable exactly as p18
> reached it: **build it under `controls/` with a direct `rustc` invocation.**

**When to land it for real: bundled with a pattern that is being re-measured
anyway**, so the re-measure is already being paid for. A `build.py` change is
free *only* then.

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

⚠ **SAY IT THE OTHER WAY ROUND, BECAUSE THE MANAGER GOT IT BACKWARDS AT
TASK_073 AND ALMOST DEFERRED A FIX ON IT.** *"`gen.py` is measurement-hashed"*
is true and is **not** the same as *"editing `gen.py` forces a re-measure"*.
**`STALE` is the only verdict that sets the exit code.** So a **comment-only**
edit and an **appended sweep band** are both `GEN-ONLY`, exit 0, **no
re-measure** — measured twice now (`.memory/05-layout.md`'s band case, and
p36 at TASK_073, where a docstring correction *and* a new `sweep-mixrand6` blob
landed together with all 30 committed blobs byte-identical). **What forces a
re-measure is a `gen.py` edit that changes a MATRIX blob's bytes.** Run the
command and read the verdict; do not infer it from the hash list.

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

### A freed chunk's first 16 bytes are glibc's tcache metadata — fold past them

**TASK_055 probe 2, measured; unreviewed.** A kernel that reads through a
dangling pointer is **not reproducible**: a naked use-after-free printed **five
different answers in five runs**, which **`check_checksums`**'s cell-agreement
requirement (`check.py::check_checksums`; this read `:1249` until TASK_066 and
`:1440-1476` until TASK_071, both of which had drifted onto unrelated code) rejects outright — so "a lifetime bug cannot be benchmarked here"
looks true and **is not**.

The cause is not ASLR and not allocator growth (that first explanation was
measured and withdrawn): glibc writes **tcache metadata into the first 16 bytes
of the freed chunk**. **Fold from offset 16** and gcc, clang and rustc all print
the same value on every run at `-O3`.

> ⚠ **THAT LAST SENTENCE IS TRUE AND THE RULE BUILT ON IT IS INSUFFICIENT**
> (TASK_055_REVIEW, measured). Folding from offset 16 removes the *run-to-run*
> variation and leaves a **variation across `-O` LEVEL**, which is worse,
> because `build.py`'s `OPTS = ["O0","O3"]` puts both in **one matrix**:
>
> ```
> gcc  -O0/-O1/-O2/-Os : 2582767925679282152     gcc   -O3      : 6789584477807083544
> clang -O0            : 2582767925679282152     clang -O1/-O2/-O3: 6789584477807083544
> rust  -O0            : 2582767925679282152     rust  -O1/-O2/-O3: 6789584477807083544
> ```
>
> `check.py`'s cell-agreement stage rejects that outright. **The pattern would
> fail stage 2, having passed the offset-16 check.**
>
> **And the mechanism is the real finding, because it is not a measurement
> problem at all.** Disassembly of the `-O3` build shows three `movups` into the
> **first** slab and **no store loop into the recycled slab whatsoever** — the
> writes are **dead-store-eliminated**. So the `-O3` row reads the *original*
> bytes and **does not model "a stale handle reads a recycled record" in the
> first place.** A checksum that agreed would have been agreeing about the wrong
> program. (Not constant folding: the literal is absent from all three binaries.)
>
> **The repair is to put the UAF on ADVERSARIAL inputs only**, where
> `check.py` records behaviour per rung and does *not* require cells to agree —
> the engineer's own `.temp/p55/NOTES.md:389-393` said so and it was dropped when
> a different explanation was withdrawn. Precedent already in the tree:
> `results/gate/p06-rotate.json` records **four behaviours in four cells** for one
> adversarial input.
>
> **The general lesson is bigger than the allocator**: *when a "reproducibility
> fix" makes a UB row agree, check that the row still EXECUTES the UB.* Agreement
> is equally consistent with the optimiser having deleted the bug.

**Generalise it as: when a bug's harm lands in memory the allocator also uses,
find the allocator's own footprint before concluding the harm is
unobservable.** p13's runaway consumer and p06's canary read are the same
question asked of the *stack*.

### The byte-identical R4/R5 pair is a SMOKE ALARM, not a null control

**Proposed at TASK_049 as a free null the project already had; refuted at
TASK_049_REVIEW and restated at TASK_050, on two patterns.** It is an appealing
idea — R4 and R5 have byte-identical kernels and *exactly* equal `Ir`, so any
`ns` difference between them looks like pure measurement noise, and it costs
nothing because every pattern already ships the pair.

**It is a biased sample of size one.** On p06 and p14 the `verus` build's kernel
lands **0x20 below** the `unsafe` build's, so the pair samples one fixed
`addr % 64` alignment contrast every time you run it.

⚠ **Do NOT quote 0x20, and do NOT say "the offset is fixed per pattern" — both
were the manager's generalisations from two patterns and BOTH ARE WRONG**
(TASK_051_REVIEW M1, measured). **The offset is a SOURCE-PATH-LENGTH artefact.**
p06's R4 kernel moves `0x15690 → 0x156d0` as its source path grows from 29 to 98
characters, while R5 stays put — because `p06/unsafe.rs` embeds its path as a
panic `Location` and `p18/unsafe.rs` embeds none. p18's pair therefore lands at
**offset 0** and reads ≈0.

> **So the offset is not a property of the pattern, of Verus, or of the linker —
> it is a property of where the checkout happens to live and of whether a panic
> pad survives in R4.** Which is a *stronger* reason not to use the pair as a
> null: its bias moves if you clone the repo to a different path.

**What survives unchanged is the conclusion**: the pair is one draw, not a
sample, and **the floor is the layout population.** p14's kernel is bimodal there (`%64==16` costs 264–277 ns, `%64==48` costs
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

   ⚠⚠ **THE 10% THRESHOLD IS A CLIFF, AND ITS OUTPUT IS UNSTABLE ON AN
   UNCHANGED TREE** (TASK_077 + TASK_077_REVIEW M3 + TASK_078; the cleanest
   instrument measurement this project has). **p38's discard count, recoverable
   from `git`, reads `4 → 3 → 6 → 5`** across re-measures where **`Ir` is
   32/32, static 32/32 and checksums 32/32 BYTE-IDENTICAL**. One cell —
   `safe_naive/whole` — has read **8.98 / 12.48 / 11.09 / 10.86%**, crossing the
   line twice. Between the last two runs the only committed change was **a
   docstring**, and **7 of 32 cells crossed**.

   **Why it is a cliff and not a filter**: the *timings* move by a median of
   0.50% (max 3.62%) while **`spread_pct` itself moves 30× more** — median
   14.18%, max 48.77%. **The quantity the rule thresholds is far noisier than
   the quantity it is protecting.**

   **So: a discard COUNT is not a stable property of a pattern.** Quote it from
   the table you are looking at, never from prose, and ⚠ **never write "no claim
   rests on a marked row" without checking** — p38's own §4d quoted three
   discarded cells and annotated them *"what SHIPS"*.
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

⚠ **WIDENED AT TASK_073, on p36: the rule is about OUTWARD-DISPATCHED WORK, not
about libc.** Written as `@plt`/`@GLIBC` it reads as a rule about library calls,
and p36 walked straight past it — its callees are **its own project-local
functions**, reached through a dispatch table, so every `@plt` list in the
pattern is equal and the licence appeared to hold. **It did not.** Measured
dispatch-target `Ir`/call on `small.bin`: **gcc 512, clang/rustc 384, and 0 for
the `match` control**, which inlines all eight arms. Consequences, all published
and all wrong on the kernel column alone:

- the `match` control **reverses** — dearer on the kernel column, **cheaper by
  58.23 / 507.00 on kernel + targets** — and *"it is DEARER"* was quoted inside
  `spec.md`'s **hashed** `idiom.why` as the reason it was forbidden;
- the **gcc-vs-clang C gap vanishes**: `10·nrw` vs `11·nrw` becomes `14` vs `14`;
- a *"2.00000 `Ir` per dispatch cheaper"* claim is **3.00000**.

**Ask "does every cell execute the same work OUTSIDE the kernel symbol", not
"does every cell call the same libc routines".** An indirect call, a
devirtualised `match`, a `static` helper the optimiser did not inline, and a
library call are the same hazard.

⚠ **THE LICENCE IS DERIVABLE FROM COMMITTED RECORDS — NO DISASSEMBLY, NO NEW
MEASUREMENT** (TASK_075_REVIEW B1, and this file already prescribed it as *"the
author-checkable test"*). `results/gate/pNN.json` carries
**`marginal_ir_per_call`** per `(cell, opt, mode, input)` — whole-program and
therefore symbol-independent — so

```
(marg[A] − marg[B]) − (kex[A] − kex[B])   =   the callee correction
```

It reproduces every large correction independently: p11 `+9815.56/+7116.78`,
p08 `−4152.92/−4488.90`, p09 `+379/+2626`, p13 `−190/−264`, p27
`+120.33/+130.95`, p47 `+88.37/+166.00`, p36 `+129/+1025`. The residual is
**structured, not noise** — exactly `+1.00` on 26 of 44 `gcc-clang` rows and
`−1.00` on 28 of 44 `R5−R4` rows (the driver term).

⚠ **THIS BLOCK FIRST SAID *"zero misses at every threshold"* AND THAT WAS A
SCORING ARTEFACT** (TASK_076, correcting TASK_075_REVIEW and the manager who
copied it). **The review scored the ORACLE at the same threshold as the
ESTIMATE** — `truth = |cg| >= th` — which makes misses impossible by
construction. Against a **fixed** truth threshold, 176 rows:

| threshold | hit | **miss (false OK)** | false alarm |
|---|---:|---:|---:|
| **2.0 Ir** | 162 | **0** | 14 |
| 3.0 Ir | 164 | **2** | 10 |
| 5.0 Ir | 165 | **2** | 9 |

**Zero misses holds at 2.0 Ir and nowhere else**; both misses are `p02
gcc-clang` at exactly `+2.00` — the PLT thunk, i.e. the term the method cannot
resolve, sitting exactly on the boundary.

**The useful form is three bands, measured, not a single threshold:**

```
|corr| <  2.00    120 rows    0 real / 120 spurious   <- SUPERSEDED, see below
                                                     ⚠ AND IT READS `0 real` AGAIN TODAY.
                                                       THAT IS A COINCIDENCE, NOT A VINDICATION.
2.00 .. 16.00      22 rows    8 real /  14 spurious   <- print these with a "?"
|corr| >= 16.00    34 rows   34 real /   0 spurious   <- smallest is 17.00
```

⚠⚠ **THE FIRST ROW'S GLOSS — *"nothing real hides below the floor"* — NO LONGER
HOLDS, AND THIS FILE CONTRADICTED ITSELF FOR SEVERAL TASKS (found at
`TASK_114`).** After `TASK_107` re-emitted `synthesis/outward_ir.json`, the
generated `results/synthesis.md` prints the `< 2.00` band as **`4 real / 139
spurious`** where it printed `0 real`. ✅ **The four are fully attributed and the
attribution is CONFIRMED**: they are `p03`/`p04`'s `R3−R4` cells, each **one
callee** (`0x189480`, `__memset_avx2_unaligned_erms`), and an 8-pad sweep shows
each rung takes its term independently with boundaries offset by 8 bytes, so
**`R3−R4` takes `{−7, 0, +7}`**. ⚠ **So the published `4 real / 139 spurious` is
ONE DRAW of the ±7 environment term, not a discovery** — and equally, **`0 real`
was one draw too.** ⚠⚠ **Neither number is a property of the tree. The band's
honest statement is: below the floor, whether a correction reads "real" is
decided by the environment phase, so do not quote either count.**

⚠⚠⚠ **AND AT `TASK_119` IT SWUNG BACK: the generated `results/synthesis.md` now
prints `0 real / 143 spurious` again.** ⚠ **DO NOT READ THAT AS THE TABLE ROW
ABOVE BEING VINDICATED AND DO NOT DELETE ITS `SUPERSEDED` MARKER.** **It is the
THIRD draw of the same ±7 term, and `TASK_119` read the cause straight out of the
sidecar rather than asserting it: `outward_by_callee 0x189480`
(`__memset_avx2_unaligned_erms`) moved `43.0 → 50.0`, so `p03`'s `R3−R4 moves_by`
went `−7.0 → 0.0`.** ⚠⚠ **A superseded number that COMES BACK is more dangerous
than one that stays wrong, because it looks like confirmation. `0 real` has now
been printed by two different draws with a `4 real` draw between them.**

⚠ **And the floor is ±2 Ir with a measured max residual of 15.79** (p22) and
**10.11** (p07) — ~~"±16 on p07 and p22"~~ was this block's own guess and
**nothing reaches 16**. The method **cannot** resolve the ±7 `memset` or the
+2 PLT thunk below. Use it as the trigger; disassembly or a callee sweep is the
refinement.

### The callee column is an ADDITION, never a REPLACEMENT — it is less reproducible than the column it corrects

(TASK_075 + TASK_075_REVIEW M1. ⚠ **The delivery's own perturbation knob —
lengthening `--callgrind-out-file=` — is MEASURABLY INERT**, because valgrind
strips its own options before building the client stack; the review replicated
the two paths at exact length and got identical figures. **Re-run with the
ENVIRONMENT BLOCK as the knob, which demonstrably works.**)

Two independent sweeps, 348 `(pattern, input, cell)` triples:

```
kernel-EXCLUSIVE Ir/call moved in   0 of 348
OUTWARD          Ir/call moved in  11 of 348
   p03/p04 safe_tuned, both blobs   50.00 -> 43.00   (glibc memset, alignment)
   p08 x6 cells small +0.0627/+0.0676 ; p08 large unsafe +0.0065
```

**On the callee column `R5 − R4` reads −7.00 on p03 and p04** — *"the proof
costs −7 instructions"* — **between byte-identical kernels.** So the kernel
column is the *correct* one there. ⚠ **p08 is a third exposed pattern** and its
offset cancels within a language, so it changes no verdict today and would
change one the moment a cross-language row used it.

### gcc's PLT thunk: +2.00 `Ir` per libc call, gcc's column only

(TASK_075_REVIEW, verified with call counts on p02, p11, p12 and p47.) gcc
routes every libc call through a 2-instruction thunk that **callgrind attributes
as its own function**:

```
gcc    memcpy@plt:  endbr64 ; jmp *0x2e06(%rip)     <- 2 insns, 2.00 Ir/call
clang  memcpy@plt:  jmp *0x2f92(%rip)               <- 1 insn, folded away
```

⚠ **One of the two instructions is the `endbr64` of gcc's default
`-fcf-protection=full`** — so that mitigation is priced **twice** in gcc's
column, once per function entry and once per libc call. On p47 both compilers
call the *same address* (`0x188320`); the entire `memcmp`-vs-`bcmp` difference
is this thunk. **Two rows of a licence census survive only through a term the
disassembly-based rule cannot see.**

**And a per-process constant hiding inside a per-call column**: a one-off lazy
binding / IFUNC resolver (`725–794` Ir per process, **clang and rustc only**),
which scales as `1/n_iters` — 0.0065 … **0.5293** Ir/call. It is why p11 reads
`299.8727` where `150 × 2.00 = 300.00`.

### ⚠ gcc's DEFAULT `-fcf-protection=full` prices a CFI mitigation in gcc's column, invisibly, tree-wide

(TASK_073, on p36; **manager-verified independently** — `gcc -Q --help=common`
prints `-fcf-protection=full` as the default, and a one-line function compiles
to **1 `endbr64` on gcc and 0 on clang**.)

Every gcc-compiled function on this box opens with an `endbr64` **IBT landing
pad**; clang and rustc emit none. On p36 that is **49 `endbr64` in each gcc
binary against 5 in all six others**, and it is measurable exactly: building
with `-fcf-protection=none` moves the dispatch targets **512 → 384** `Ir`/call
and the total **1855.3740 → 1726.3331**, i.e. gcc's default IBT costs
**`1.00000·nrw + 1` `Ir` per call**.

⚠ **The consequence is bigger than one pattern.** p36's own write-up said the
real-world hardened answer for its bug class was *"a compiler mitigation this
matrix cannot price"* — **it has been pricing one all along**, in one compiler's
column only, and never said so. **Any gcc-vs-clang instruction-count comparison
in this tree carries an IBT term.** It is small where the kernel is one function
(one pad per call) and it is `O(dispatches)` wherever control leaves the kernel.
**Name it before attributing a gcc-vs-clang gap to codegen.**

### ⚠⚠ BOTH COMPILERS DELETE A NON-ESCAPING `malloc`/`free` PAIR AT `-O2` — an allocator in the kernel measures NOTHING by default

(TASK_079, on the refused p31. ✅ **Manager-verified on both compilers**:
`grep -cE 'call.*(malloc|free)'` over `-S` output is **0** for
`/usr/bin/gcc -O2` and **0** for `~/tools/llvm/bin/clang -O2`, and **2** for each
once `-fno-builtin-malloc -fno-builtin-free` is added.)

A loop doing `p = malloc(8); *p = i; acc += *p; free(p);` — where the pointer
never escapes — compiles to **no allocator call at all** on both compilers at
`-O2`. Measured whole-program marginals:

```
c-malloc-free  (builtin elision live)      2.00 Ir/object   <-- ARTEFACT
c-malloc-free  -fno-builtin-malloc/free  140.00 Ir/object   <-- the truth
c-bump-arena                              10.00 Ir/object
```

**The naive measurement reports the arena as 7× WORSE where it is in fact 14×
BETTER.** ⚠ **Any pattern that puts allocation in the kernel must defeat that
elision or its C rung is measuring an empty loop.** This is the p31 analogue of
p48's `rep stosb` mis-pricing and it is **cheaper to hit**, because it needs no
threshold to be crossed — it fires at `-O2` on the first non-escaping allocation.

⚠ **And the kernel-exclusive column REVERSES THE SIGN on the same pair** —
the sharpest instance of the outward-dispatch rule found so far. `main` is
**990,034 `Ir`** in the malloc rung against **1,100,035** in the bump rung, while
the *whole program* is **12.30× dearer** in the malloc rung, because **89.75%**
of its cost is inside libc. A `kernel_exclusive_ir` reading publishes *"the bump
allocator is 1.00 `Ir`/object WORSE"* against a true *"130.00 BETTER"*.
✅ **ATTACKED AND REPRODUCED EXACTLY at TASK_080** — both `main` figures, both
marginals, and `38.16 + 29.68 + 21.91 = 89.75%`.
⚠ **With ONE number corrected, and it was the MANAGER'S: `8.6×` is wrong and
`12.30×` is right** (15,565,615 / 1,265,467). The manager copied `8.6` out of
the engineer's report without deriving it, into the same entry that marked the
rest PROVISIONAL. ⚠ **Note there are THREE ratios here and only two are real** —
the whole-program *level* ratio is **12.30×**, the *marginal* ratio is **14.00×**
(140.00/10.00), and `8.6` is neither and reconstructs from nothing in the
committed log. **Quote 12.30× for levels, 14.00× for marginals.**
Fourth instance of the rule: p13 overstated, p48 would have reported zero, p36
**reversed a control**, and p31 would have reversed **its own headline**.

✅ **The open question about p27 is ANSWERED, and the answer is GENUINE — plus
the manager's framing of it was wrong.** p27's closed decomposition publishes
`230.07 = 109.65 kernel + 120.42 drop glue + **0.00 allocator**`, and this entry
asked whether that `0.00` was the elision above. **It is not.** ⚠ **The framing
conflated ABSENT with EQUAL**: the elision produces a **missing symbol**, whereas
p27's `0.00` is a **difference of two present, equal, large terms** —
`patterns/p27-handle-table/NOTES.md:793` records `malloc` at **421.1211 `Ir`/call
in BOTH rungs**, and `:465` says **58–63% of that kernel's work is inside
`malloc`/`free`**. An elided allocator cannot produce 421.1211. Confirmed
independently by rebuilding both cells: `objdump -d | grep` gives
`3 free@GLIBC 1 realloc@GLIBC 1 malloc@GLIBC` **identically** for
`safe_tuned-O3-whole` and `unsafe-O3-whole`. ✅ **Manager-verified from the
committed record**, no rebuild needed.

⚠ **THE RULE THIS ENTRY FIRST EXTRACTED — *"check whether the symbol is PRESENT,
not whether the difference is zero"* — DOES NOT GENERALISE, and was refuted at
TASK_081_REVIEW with a counterexample.** Put **one escaping allocation outside
the loop** and the symbols are all present — `1 malloc@GLIBC 2 malloc@plt
1 free@GLIBC 2 free@plt` — while **every allocation inside the loop is still
elided**, giving exactly the artefact rate (185,298 → 385,520 = **2.00222
`Ir`/object**, the committed BUILTIN-ELIDED figure). **Presence is NECESSARY,
NOT SUFFICIENT.**

**The test that actually settles it is a RATE, which is what p27 had all
along**: `malloc` at **421.1211 `Ir`/call in both rungs** is a per-call cost no
elision can produce. **Check the per-call rate of the allocator symbol, not its
presence in the symbol table** — and note that this is the same shape as the
outward-dispatch rule above: a symbol list answers a weaker question than a
column of numbers.

## ⚠ A LAW CAN SURVIVE OUT-OF-SAMPLE AND ITS MECHANISM STILL BE WRONG — p17's sawtooth

(TASK_082 fitted it, TASK_083_REVIEW kept the law and killed the explanation.
**This is the cleanest instance in the project of the two coming apart.**)

**The law held everything you could ask of it.** `R3ship − R4` over `nsuf = 1..8`
is `18, 23, 30, 37, 44, 49, 56, 63`; lag-4 differencing gives **26 four times,
zero residual**; extended **out of sample to `nsuf = 9..12`** on an independent
`n_iters` pair it gives `70, 75, 82, 89` and **26 four more times, 8/8**.

⚠⚠ **AND THE STATED MECHANISM WAS STILL WRONG.** TASK_082 attributed the period
to *"the 4×-unrolled walk over the suffix table"*. **The table walk is SCALAR in
both rungs** — one `movzx` pair, `inc`, `cmp`, `je`. The 4× unroll is the **inner
BYTE fold**, keyed on the *served length*, with an `and $0x3` epilogue.

**The experiment that settles it — perturb only the GENERATOR's suffix step:**

```
step=36 (0 mod 4): 18 25 32 39 46 53 60 67   +7 x7        NO SAWTOOTH
step=37 (1 mod 4): 18 23 30 37 44 49 56 63   +5,+7,+7,+7,+5,+7,+7
step=38 (2 mod 4): 18 25 32 39 46 53 60 67   +7 x7        NO SAWTOOTH
step=39 (3 mod 4): 18 25 32 37 44 51 58 63   +7,+7,+5,+7,+7,+7,+5
```

Request count is `1..8` in every row. ⚠ **The period is the GENERATOR'S, not a
loop's** — and `p17/inputs/gen.py`'s own hashed comment already said the suffix
index *"has no residue class"*.

**The replacement law, zero free parameters:**

```
R3ship − R4 = 11 + 7·nsuf − 2·#{ i : s_i ≡ 0 (mod 4) }
```

It predicts **all 49 measured points** and **both published inputs** — `small`
(suffixes 498/251/122 → residues 2,3,2 → **32**) and `large` (4085/2041/1019 →
1,1,3 → **32**), each matching to `0.00`.

✅ **It also closes the `30 ≠ 32` question**, which looked like a published
number being off by 2: `sweep-nsuf-03`'s suffixes are 497/460/423, **one of which
is ≡ 0 mod 4**, so 30 is what the law requires. **No published p17 number is
wrong.**

⚠⚠ **DO NOT QUOTE `6.50 Ir`/request. It is BAND-SPECIFIC and it makes p17's own
shipped inputs LESS accurate.** Both shipped inputs have **no** residue-0 suffix
and therefore pay **7.00**; over 20 ranges the truth is 151, `7n + 9` gives 149,
and `6.50` gives ~140.

> **The rule, and it is the reusable part: an out-of-sample test validates the
> LAW, not the STORY.** A sawtooth in the data is evidence of *a* period; it is
> not evidence of *which* loop. ⚠ **Any 8-point sequence can be lag-4 differenced
> — four equal differences are a fact about the numbers.** **Confirm a mechanism
> in the disassembly, or by perturbing the thing you claim causes it, before
> naming it.** Here, perturbing the generator moved the period and the
> disassembly named a different loop.

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

⚠ **THIRD instance on p18, and two corrections to the rule as stated above**
(TASK_051_REVIEW, TASK_052):

- **The criterion is POST-DROP RANK, not column count.** p18's proposed caveat
  — *"a 3-column design makes every leave-one-band-out unable to fail"* — is
  **wrong**. The cause was that **one band alone was already full rank**, so
  dropping any *other* band changed nothing. p06 is rank 5 of 5 and its hold-out
  fails. **Column count is not the test; the rank after the drop is.**
- **A re-derivable hash is TAMPER-EVIDENCE, not pre-registration.** p18 replaced
  its dead hold-out with 24 predictions committed under a `sha256` — and
  re-running the registration script reproduces that hash byte-identically at any
  later time. It proves the file was not altered; it proves **nothing** about
  whether the predictions predate the measurement. **To make it real, register
  the hash in a commit that PRECEDES the measurement commit** — git supplies the
  ordering, the manager already commits at task boundaries, so it costs one extra
  commit and nothing else. ⚠ And note a corollary p18 learned the hard way: a
  **file mtime is not evidence** either — re-running a generator destroys it.

### The out-of-sample test that finally worked: ADDITIVITY EXTRAPOLATION

**p18, TASK_052 — the first out-of-sample test on this project that could have
failed and did not.** Where a law has two structural parameters, **fit on rows
where they are never observed TOGETHER, then predict the rows where both fire.**
p18 fitted 38 rows in which `cut` and `brk` never co-occur and predicted the five
rows where they do: **40 predictions, worst |error| 0.0228.**

This has teeth where a hold-out does not, because the held-out cell is **outside
the row space of the fit set** by construction rather than by hope — a linear
combination of the fit rows cannot reach it. **Prefer it whenever the design has
two or more parameters that can be varied independently.**

## A per-call `Ir` law owes its DOMAIN, and the domain is usually MISSING COLUMNS

**p14 and p18, and on p18 the distinction was measured.** p14's exact hardening
law was fitted where its guard never fired; p18's exact level laws were fitted
where `cut = brk = 0` and **a committed matrix input (`degenerate.bin`) violated
both**, missing by up to **+8.00** against a quoted max residual of **0.029** —
and its `R3 − R4` prediction had the **wrong sign** (−5.00 predicted, +1.00
measured).

> **Do not write the domain as a caveat. Test whether it is a missing column.**
> On p18 the corrected design is rank 5 of 5, `max|resid|` stays 0.03, and the
> old coefficients are **unchanged** — the published law is exactly the new law's
> restriction to `cut = brk = 0`. Refitting the *old* two columns over all rows
> takes the residual to **1.81…7.27** and knocks every coefficient off its
> integer. A caveat would have hidden that.

⚠ **EIGHTH PATTERN, and this time the diagnostic is quantified** (p10,
TASK_059). p10's laws were fitted where every call is **accepted**; a blob whose
windows are rejected (`taps > n`) breaks **every** difference law, with residuals
**exactly linear in the rejected-call fraction** — `R2−R4` −14.00, `R3−R4`
+22.00, `R2−R3` −36.00, identical across three blobs at rejection fractions
0.52 / 0.50 / 0.17. Adding the columns: **rank 7 of 7, `max|resid| 0.0000` in and
out of sample, and every one of the four original coefficients survives to the
integer.** Refitting the OLD columns over all 33 rows instead gives residuals
**9.19, 14.12, 23.31** and **1606.73** on clang's hardening law. **A caveat would
have hidden all of that** — exactly p18's result, now on a second pattern.

⚠ **And p10 needed a SIXTH parameter behind the fifth, which is a distinction
worth stealing: it is WHICH GUARD rejects, not which comparison.** Rejecting at
`last >= len` costs +4/+5 more per rung than rejecting at `n < taps`, and the two
"far" regressors are identical in all six guarded cells. p10's parameter count
went **3 → 4 → 6**, and it says so rather than claiming the list is closed.

⚠ **And the parameter list is rarely complete on the first pass.** Both the
manager's task file and the review named p18's domain as **one** condition
(`term == nv`); the engineer measured **two** independent ones, and a band
varying only the first would have produced a law that still missed the
counterexample by +2 on six of eight cells. **Say explicitly which parameters you
established and that you cannot claim the list is closed.**

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

## ⚠ A law fitted in one INLINE MODE is not the law in the other — the regressors can SWAP

**p10, TASK_059, measured — and this is the sharpest instance of "say whose
counts" on the project, because both fits are exact and both designs are full
rank.** p10's `R3 − R4` was published from `-O3 isolated` (which is
`controls/sweep_ir.py`'s default and was named nowhere) as:

```
-O3 isolated   R3 − R4 = −3  − 5.00·nout + 0.00·scaltap − 1·novecout + …
-O3 whole      R3 − R4 = +1  + 0.00·nout − 2.00·scaltap + 1·novecout + …
```

**`nout` and `scaltap` swap roles.** Both fits are **rank 7 of 7** with
`max|resid| 0.0000` in and out of sample. The whole-mode figure reproduces to the
instruction as `1 − 2·64` and `1 − 2·120`, and the headline shrinks 2.5×
(−323/−603 → −127/−239).

> **The mechanism is real, not a fitting artefact.** Once the kernel is inlined
> into `main`, the outer-loop strength reduction goes away, so the per-tap cost
> absorbs the address arithmetic the per-output term carried in `isolated`. The
> epilogue bodies, counted off the shipped binary rather than fitted, are
> R4 = 9, R3 = 7, `c-clang` = 7 — and R4's two extra instructions are **two
> `lea`s re-forming its two four-term indices**, not checks.

**Consequences, and they are cheap to obey:**

1. **Name the mode at every figure**, in `NOTES.md`, `README.md` and any
   `.memory/` entry. A mode-free per-call `Ir` figure is under-specified in
   exactly the way a convention-free one is (`:479`).
2. **A sweep's default mode is a silent choice.** `sweep_ir.py --mode isolated`
   was the default on p10 and nothing in the published text said so.
3. **Fitting both modes is nearly free and can upgrade a correction into a
   result.** p10's C2 was specced as *"the number is smaller"*; fitting the
   second mode turned it into the swap above, and the whole-mode value landed
   **within 2 `Ir`** of the value an independent route (a cheaper admissible R4)
   produced. **Two routes to one number is worth more than either alone.**

## Close a decomposition over EVERY function, not over the four you suspect

**p27, TASK_060_REVIEW + TASK_061.** p27's safety tax was first decomposed by
naming four functions (`kernel`, `drop_glue`, `malloc`, `free`) and observing
that the allocator terms were equal between rungs. That is corroboration. The
review re-did it by **parsing the whole callgrind annotate table**, and the
result is categorically stronger:

```
230.0694  =  kernel 109.6476  +  drop_glue 120.4218  +  allocator 0.0000
SUM OVER EVERY FUNCTION = 230.0694 = the whole-program delta.   closed? YES
```

`_int_malloc`, `_int_free`, the unix shim and all three `__rust_*` are also
**equal to the last digit**. **Nothing else moved** — which four needles cannot
establish, because they cannot see the fifth.

> **A closed decomposition is the difference between "these terms explain it" and
> "these terms ARE it."** It costs one pass over a table you already generate
> (`controls/ir_table.py --closed`), and it is what let p27 say *nothing* in
> `R3 − R4` is temporal safety rather than *most of it isn't*.

## ⚠ A whole-program marginal figure can be a function of the SCRATCH DIRECTORY

**p27, TASK_061 — and the correction is to the reason, not the retraction.** p27
published `R5 − R4 = +0.0132` on `large`. It was retracted, and the first stated
reason (*"it does not reproduce"*) is **wrong**: it reproduces exactly, twice,
under the tool's own scratch path. It moves to **`+0.0104`** under a
per-PID path and to **`+0.0020`** under a third — **on identical binaries and
identical bytes**.

> **The finding is "it is a function of the scratch directory", not "it is
> noisy".** A whole-program count includes the process's own argv and
> environment handling, so a path-length change of a few characters moves it by
> **±0.02 `Ir`/call**. That is below anything this project publishes, and it is
> exactly the size at which a five-decimal figure looks meaningful and is not.
> ⚠ **Sanity-check the arithmetic too**: `0.0132 × 5000 calls = 66`, not 132 —
> the figure never had a consistent reading.
> **Kernel-exclusive counts do not have this problem.** Related but distinct
> from `:1099` (the environment block does not always cancel) and from the
> source-path-length artefact in the R4/R5 null.

## ⚠ An `identity: exact` pin excludes every candidate R4 that carries a PANIC PAD

**p10, TASK_057_REVIEW + TASK_059, measured on a pad count rather than inferred.**
p10's rejected R4 candidate `u_win` **verifies** (10/0, no new trusted item), and
its R4/R5 pair is `md5_fn_norel`-equal with `md5_fn` **different**: the sole real
difference is one pc-relative `lea`, the `split_at` **panic-`Location`
pointer**. `pads.py --source` gives `u_win` **1** surviving pad and the shipped
`unsafe` rung **0**.

> **So a pattern pinning `identity: exact` cannot admit any R4 whose spelling
> leaves a panic pad standing, whatever the pad costs.** That is a bound on the
> **R4 search space of every pattern**, not a p10 quirk, and it is the reason
> p10 publishes an R4-side span instead of a cheaper R4. It sharpens
> `:116`'s *"`md5_fn` moves with the SOURCE FILE'S NAME when a panic survives"*:
> the same mechanism that makes a digest path-sensitive also makes `exact`
> unreachable for the whole class.

**Do not relax a pattern's pin to admit one** — p10 did not; every other pattern
pins `exact` at `-O3` and the exception would be the finding. **Publish the
fixed-R4 bound and the span, and name the pin as the binding constraint.**

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

## "0 STALE" is not "every record is verified"

**Measured at TASK_066.** `measure.py --check-stale` prints `NO BASELINE` for a
record lacking `source_sha256` and **`continue`s without incrementing `bad`**
(`measure.py:325-328`), so the run reports `0 STALE` and **exits 0** while some
records are unverifiable by hash.

Today that is **five of nineteen measurement records** — `p02-buffer-copy`,
`p05-index-flatten`, `p07-binary-search`, `p11-nul-scan`, `p17-http-range` —
including **p02, the project's strongest security result**.
✅ **All 19 GATE records do carry it**, so the gap is the measurement layer only
and the provenance exists one file over. The fix is a re-measure of those five;
RECAP "Owed" item 6 carries it.

⚠ **The audit that first "closed" this used
`'source_sha256' not in open(f).read()`** — a raw substring search. Each of those
five files contains the string exactly once, inside `/git/note`, in a sentence
advising *"Use `results/gate/*.json`'s `source_sha256`"`*. **The pointer to the
hash was mistaken for the hash.** Parse the JSON and test the top-level key:

```bash
python3 -c "import json,glob;print([f for f in sorted(glob.glob('results/*.json')+glob.glob('results/gate/*.json')) if 'source_sha256' not in json.load(open(f))])"
```

## Additivity extrapolation failed once, and the failure was 100% attributable

**p38 — TASK_066, its review, and TASK_067.** The only out-of-sample test on this
project that has ever been *able* to fail did fail: `R2 − R4` missed by **86.66**.
Then it was repaired exactly. **The repair is the finding.**

⚠ **The published cause was wrong, and so was the manager's prescribed fix.**
p38 blamed a missing `nw` (window-bytes) column. **`R2 − R4` is exactly CONSTANT
in `nw`** — `115.00` at `nw` ∈ {128,160,200,240,248,256} for `(nrec,rlen)=(2,4)`.
And **adding `nw` makes out-of-sample WORSE**: 86.66 → 102.74. The manager
prescribed precisely that repair in `TASK_066_REVIEW.md`.

**The model was missing THREE columns and none of them was the one named:**

1. **A real `nrec × rlen` interaction, carried by the PARITY of `rlen`** — odd
   records cost **10.5 less each**. Invisible because band `r` fixes `rlen = 4`.
2. **A band-design defect whose column is `nw mod 8`** — bands `r` (240) and `x`
   (256) are **both `0 mod 8`** while band `w` sits entirely at 244 (`4 mod 8`),
   a flat −22.
3. **`rlen == 1` is a law TERM, not an anomaly** (TASK_067; the review's grid
   started at `rlen = 2`). Its residual is exactly `6·nrec`. ✅ **This retires
   `sweep-w01`, the pattern's one disclosed exception, and withdraws the
   "the reslice has nothing to amortise" explanation that stood for it.**

**The repaired laws, ZERO free parameters:**

```
R2 - R4 = A(nw mod 8) - 8*nrec + 6.5*nrec*rlen - 10.5*nrec*(rlen mod 2)
          + 6*nrec*[rlen==1]          A(0) = 79 ;  A(m) = 33 + 6m, m = 1..7
R3 - R4 = 17 + 1.00*nrec + 1.00*nrec*[rlen==1]      (exactly independent of nw)
```

**106 rows, max abs residual `0.00000` on both** — 22 in sample, **6 out of
sample**, a 49-cell `(nrec × rlen)` grid never measured before, two `nw` sweeps,
and both matrix blobs exactly (small 257, large 711).

> ⚠ **So "the additivity test finally failed" is TRUE AS AN EVENT AND FALSE AS
> WRITTEN.** Nothing was non-additive in the parameters named; the law was fitted
> over bands holding three further structures fixed. **This is the DOMAIN rule
> landing on a real case — the domain was a missing column, three times over —
> and it is a better result than the failure was.**
>
> ⚠ **The generalisable rule, and it is cheap: CHECK THE RESIDUE CLASS of any
> parameter your bands hold constant.** Two of p38's three bands shared
> `nw ≡ 0 (mod 8)` and the third did not. **That is exactly the configuration
> that fits in sample and misses out of it**, and no amount of in-sample residual
> would have shown it. Vary the parameter, or prove independence of it — holding
> it at one value in every band is the trap.

⚠ **Mechanism NOT established** for `A(nw mod 8)`, the parity term or the
`rlen == 1` term. The shapes are exact over 106 points; nobody has read the
vector epilogue. Owed in p38's §4c/§10d.

⚠ **Cross-pattern `Ir` comparison is `isolated`-mode ONLY.** Of 318 `-O3`
cell/input pairs tree-wide, `whole` has `kernel_exclusive_ir = None` in **302** —
the kernel is inlined and has no symbol. Since **p10 showed regressors swap
between modes**, any cross-pattern synthesis speaks for one mode only. *(Manager
measurement, TASK_066; probe at `.temp/synth/aggregate.py`.)*

## TySan, the project's third sanitizer — and it checks only what survives

**p38.** `~/tools/llvm/…/libclang_rt.tysan.a` exists, `-fsanitize=type` links, and
it reports `TypeSanitizer: type-aliasing-violation`. **It is the only tool here
that sees type-based aliasing**: UBSan has **no** strict-aliasing check and fires
only as `array-bounds`, where the index leaves a typed array.

⚠ **The manager's mechanism was wrong.** A probe showed a one-TU `static` build
silent at `-O1/-O2/-O3` where a two-TU build fired at all four levels, written up
as *"the blind spot is INLINING"*. **It is not.** One TU **plus `noinline`** fires
at every level; inlined builds whose object is **heap-allocated or
address-escaped** fire at every level; and a fourth control (one TU, inlined,
stack, no escape, **dynamic index ⇒ unpromotable**) also fires. Inlining matters
only because a cross-TU call **forces the object into memory**.

> **The accurate statement is broader than "promotion": TySan checks only
> accesses that SURVIVE TO THE END OF THE PIPELINE. Promotion is the case that
> removes all of them.** A dead `store i32` eliminated at `-O2` halves the report
> count *and changes its direction*, and p38's own kernel halves 160000 → 80000
> at `-O2` on an array that is never promoted.

✅ p38's scratch is a real array, so **TySan fires in BOTH inline modes**, 8/8 —
a prediction that could have failed. So p38 is **not** a pattern where the
catcher has an inline-mode domain, and the same measurement says why the toy
looked like one.

## A static diff cannot close a dynamic gap — derive per-instruction or say "presumed"

**p22 §4e, TASK_071.** The capacity conjunct costs **gcc 1.00/key, clang
5.00/key**, and the natural move — diff the disassembly — **gives the wrong
answer for gcc**: `asm.py stat` reports **87 → 89 (+2)** against a measured
**+1.00/key**. A review derived clang's side statically and was *right*, then
derived gcc's the same way and was **incomplete**.

**Per-instruction callgrind (`--dump-instr=yes`) closes it:**

```
gcc  : +128.00/call = 1.00/key    cmp +1  ja +1  lea -1
clang: +640.00/call = 5.00/key    setne +1 setb +1 and +1 cmp +2 jne +1 je -1
```

**gcc DOES short-circuit and recovers a `lea` by re-associating the Horner
shift.** That **−1 is invisible in a static count** and is the entire 2-vs-1
discrepancy. clang's +5 is `setne`/`setb`/`and` — it **refuses** to short-circuit
the `&&`.

> **The rule: a static instruction diff bounds the change, it does not measure
> it.** Static counts miss compensating reassociation. **Either derive it
> per-instruction, or label the mechanism a presumption** — p22 labelled it,
> which is why its wrong explanation was a *minor* and not a *major*.

## Concurrent load corrupts a wall-clock block — now MEASURED, not just warned

**p22, TASK_071, self-disclosed.** A `measure.py` run that overlapped the
engineer's own **log-polling shell loop** came back with **14 of 32 O3 cells over
the 10% spread threshold**. Re-run on a quiet box: **0 of 32**, with **every `Ir`
figure bit-identical**.

> This is the concurrency rule with a number attached. **Deterministic `Ir` under
> callgrind is immune to contention; the `ns` column is not, and the failure is
> SILENT** — the run completes and simply reports a degraded spread. ⚠ **Even a
> polling loop counts as load.** Run `measure.py` in the foreground on an
> otherwise idle box, and re-run rather than shipping a visibly degraded timing
> block even when no published number depends on it.

⚠ **A re-measure after a docs+generator change moved 101 leaves and ZERO measured
numbers** — 96 wall-clock, 3 provenance, 2 source hashes. Useful calibration for
what a "stale" record actually costs to refresh.

## ⚠⚠ AN INTERCEPT MEASURED ON A PROBE BINARY DOES NOT TRANSFER. ONLY THE SLOPE DOES.

**PROVISIONAL — measured at TASK_088, not yet reviewed.** ⚠ **This bears
directly on every row in `TASK_086`'s queue, because all of their numbers are
probe numbers.**

p19 shipped two laws taken from a 5-length probe (`.temp/t87/cost.rs`):
`R2 − R4 = 6.25·m − 8` and `R3 − R4 = 1.00·m − 2`. Re-fitted from the
**committed** blobs against the **shipped** binaries, with zero residual over all
19 lengths:

```
R2 - R4 = 6.25*m - 6 - 2.25*(m mod 4) - 4*[m mod 4 != 0]
R3 - R4 = 1.00*m + 4                  - 1*[m mod 4 != 0]
```

**Two independent things were wrong, and only one of them is the residue rule.**

1. **The residue term.** The probe never varied `m mod 4`, so it could not see a
   `2.25·r + 4·[r≠0]` epilogue term. That is the known rule — *check the residue
   class of any parameter your bands hold constant.*
2. ⚠⚠ **A FIXED PER-PROGRAM OFFSET, AND THIS ONE IS NEW.** The probe sampled
   **only `m ≡ 0 (mod 4)`**, where the correct law *is* `6.25m − 6` / `1.00m + 4`
   — and it still published `−8` / `−2`. **The delta is exactly `+2` and `+6` at
   all ten `m ≡ 0 (mod 4)` points.** The probe was a **different binary**: a
   different driver, different call overhead, different register pressure.

⚠ **The second failure mode is INVISIBLE TO A RESIDUE-COVERING BAND**, because
it is constant in `m`. Sweeping every residue class perfectly would not have
caught it. **What catches it is re-fitting against the SHIPPED cells** — and
p19's own `NOTES.md` printed the four shipped marginals **two sections above the
law that contradicted them**.

**The rule: a probe measures a SLOPE. Carry the slope forward as a prior and
RE-FIT THE INTERCEPT from the shipped binary, always.** A probe's intercept is a
property of the probe.

⚠⚠ **AND ONE PATTERN LATER THAT RULE WAS ITSELF TOO WEAK: A PROBE CAN LOSE THE
SLOPE, AND THE RUNG BOUNDARY WITH IT.** (TASK_089, on p46. PROVISIONAL.) The
probe measured **`+5.05 Ir` per MAC step, +49.6 %**, safe over unsafe. Shipped,
the ordering is **reversed** — `safe_naive` < `safe_tuned` < `unsafe` — and **the
per-MAC safety tax is `0.00000`.**

⚠⚠ **THE MECHANISM THE MANAGER FIRST LANDED HERE WAS WRONG, AND IT IS
RETRACTED (TASK_089_REVIEW B2, measured).** ~~*"the probe wrapped its dimensions
in `black_box`, which withheld the `u8` range … `black_box` is not a neutral
stop-the-optimiser tool, it is a fact-hiding tool"*~~ — **`black_box` changed
NOTHING.** Rebuilt with and without it, **every probe kernel is byte-identical**
on the linked binaries: p46's 296 B `a73eda77…` / 126 B `daca171e…`, and the same
for p23's, p24's, p26's and p35's. ⚠ **A `black_box` at a CALL SITE cannot reach
the codegen of an `#[inline(never)]` callee.**
⚠ **And the retraction has teeth for the next probe author: dropping
`black_box` "so as not to hide range facts" would re-enable the constant folding
it exists to prevent, while the real cause went unfixed.**

✅ **THE CORRECT MECHANISM, and it is stronger: A PROBE WHOSE KERNEL SIGNATURE
DIFFERS FROM THE SHIPPED KERNEL'S LOSES THE RANGE FACTS THE SHIPPED KERNEL
DERIVES FROM ITS INPUT HEADER.** Isolated by a control that puts p46's **shipped
body** inside the probe harness, **both called through `black_box`**: the shipped
body loses every bounds check while the probe kernel keeps ten conditional
branches. **The probe did not mis-measure a cost; it measured a DIFFERENT
PROGRAM** — one where the safety check is live, and dead in the shipped one.

⚠⚠ **BLAST RADIUS, now RANKED from the probe sources rather than asserted** —
and it governs four unbuilt rows:

| row | exposure | why |
|---|---|---|
| **p24** heapify | **HIGH** | `l = 2*i+1` guarded by `l < n`; with a fixed-capacity scratch and a header-derived `n <= CAP`, the accesses are provable by **the same linear reasoning as p46's `i+j < 96`. Expect the same sign flip.** |
| **p26** RLE | **HIGH** | `out[o]` already guarded one line above, and `k26_checked` 247 B vs `k26_unchecked` 221 B is nearly free already |
| **p35** union | MEDIUM | `tags[k]` needs `tags.len() >= vals.len()`; in a one-window shipped kernel both come from one header. (p35's headline is punning, not bounds cost.) |
| **p23** partition | ✅ **LOW — CONFIRMED by the build (TASK_101)** | ⚠⚠ **THE MECHANISM IS DISPUTED; THE CONCLUSION IS NOT.** Pre-registered as *"`while v[i] < pivot { i += 1 }` has **no upper guard**: the bounds check **IS** the termination bound and cannot be deleted"*. **TASK_101 reports that this does not describe a CORRECT rung** — an unguarded scan is the bug, not the baseline — and offers a different mechanism: **LLVM already elides the UPWARD cursor's check and not the DOWNWARD one**, because `i` is a monotone induction variable while `j` decreases and its index is an unsigned subtraction (`k_up == k_r3c` and `k_dn == k_r4b`, exactly, at three pivot ranks). ⚠ **NOT LANDED AS SETTLED — `TASK_101` is unreviewed, and this row is annotated rather than struck**, per `PROTOCOL.md` rule 9's refinement: **a conclusion and a mechanism carry different evidence, and the manager has already once struck a TRUE sentence on the strength of an unreviewed mechanism** (the ±7 launcher claim, reversed at TASK_103). **Both readings are recorded; the review decides.** |
| **p28** DLL | **not exposed — UPHELD, but read the note below** | it is **not in `cost.rs` at all**, and its probe validated `Ir` against static loop-body counts to three decimals |

**Treat every unbuilt row's probe cost as a DIRECTION-UNKNOWN prior until its
rungs exist** — but note p23 and p28 are the two that do not need the caveat.

⚠⚠ **A RUNG-PAIR CHANGE IS NOT A PROBE-SHAPE DEFECT, AND CONFLATING THEM WAS
ALMOST THIS FILE'S FOURTH WRONG ENTRY.** (TASK_093 claimed it; TASK_093_REVIEW
refuted it as a **category error**; manager-verified by reading the probe
source.) TASK_093 reported that `p28`'s probe *"reports the wrong SIGN"* —
`+12.50` against a true `−296.00` — and proposed it as a **third** probe-shape
mechanism beside p46's lost range facts and p26's length dependence.

**It is not one.** `.temp/t91/p28probe.rs`'s `k28_checked` and `k28_rawptr`
**both** run over a pre-built arena: there is **no `alloc`/`dealloc` in any
TASK_091 kernel**, so the allocator is absent from **both** sides. TASK_093's
`−296.00` put a per-node `malloc` on **one** side only. That is a **different
pair of rungs**, not the same rungs measured through a different harness.

> **Probe shape = SAME rungs, DIFFERENT harness. Different rungs = a design
> choice, and it is argued, not measured away.**

**Measured like-for-like** — free present in *both* rungs, TASK_093's own kernel
— the tax is **`+24.00`, R3 dearer: the SAME SIGN as the probe's `+12.50`.**
✅ **So the p28 entry above stands, and there is no third mechanism.** ⚠ **The
two that ARE established remain p46's (signature ⇒ lost range facts) and p26's
(input band ⇒ length dependence).**

### ⚠⚠ p24 and p26 MEASURED at shipped shape (TASK_092) — and the ranking above was wrong IN KIND

Four cells per pattern in **one harness** — same driver loop, input, decode and
checksum, so *shape* is the only variable. `ship` = fixed-capacity scratch,
count from a window-header byte, capacity tested. `probe` = identical everything
with the work behind a `#[no_mangle] #[inline(never)]` fn on a runtime-length
slice. **Shipped flags.**

**`p24` — the sign does not flip. IT COLLAPSES TO EXACTLY ZERO.**

```
input          ship_safe  ship_unsafe    S-U    probe_safe probe_unsafe      S-U
p24-n016.bin      701.29       701.29  +0.00        852.17       749.52  +102.65
p24-n128.bin     4635.63      4635.63  +0.00       5906.15      4924.85  +981.30
p24-n255.bin     8968.51      8968.51  +0.00      11455.80      9513.25 +1942.55
```

⚠ **`ship_safe` and `ship_unsafe` are BYTE-IDENTICAL** — *"identical by raw
machine-code bytes: True"*, `md5_fn 3d37ca7b…` both, `n_nopad 133` both, **no
panic edge in either**. The **probe** shape reproduces the published number
(+6.42 … +7.62 `Ir`/element against TASK_086's 7.85 and TASK_090's 7.9 ± 0.1).
Mechanism: the probe's sift is 54 insns with **`jae:6`** safe against 36 with
`jae:1` unsafe — **five surviving bounds branches per sift**, because `i` is an
opaque parameter and `n = v.len()` an ABI value, so `v[m]` cannot be discharged.
✅ **Robust: with the count read as a `u16` (only `n > CAP → REJ` bounds it) the
two kernels are STILL byte-identical.**

⚠ **So `TASK_090`'s `≈7.9 ± 0.1 Ir/element` is a PROBE-SHAPE number** — it was
measured with `TASK_086`'s own binary and convention, i.e. the same exposed
shape.

**⚠⚠ `p26` — the sign holds on four inputs, roughly halves, AND INVERTS ON THE
FIFTH.**

```
input                ship_safe ship_unsafe        S-U   probe_safe probe_unsafe       S-U
p26-np016r016.bin      7570.30     6837.30    +733.00      7659.30      6161.30  +1498.00
p26-np016r200.bin     24450.30    32837.30   -8387.00     24555.30     23329.30  +1226.00
p26-np200r020.bin     55794.00    44381.00  +11413.00     56619.00     33025.00 +23594.00
```

At **run length 200 safe is CHEAPER by 8387 = −2.62 `Ir` per output byte**, where
the probe shape shows `+1226` on the same input. Mechanism: the two shipped
spellings reach **different fill strategies** — `ship_safe` 166 insns, one
`memset@GLIBC` and `xmm` regs (run fill vectorised inline); `ship_unsafe` 116
insns, **two** `memset@GLIBC`, no vector regs (loop-idiom-recognize turned the
unchecked writes into a `memset` call). **Neither has a panic edge.**
⚠ **And p26's probe pair is worse than shape-mismatched — it is NOT THE SAME
FUNCTION**: `k26_checked` early-returns on capacity, `k26_unchecked` has **no
capacity test at all**, which is why it read 495454 vs 92942.

⚠⚠ **RE-RANK: `p26` IS THE MORE EXPOSED ROW, NOT `p24`.** p24's answer is a
clean, robust **`0.00`**; **p26's sign is not a property of the row at all — it
is a property of the RUN LENGTH**, so **p26 cannot be costed until its input band
is designed.** The manager ranked p24 HIGH and *"expect the same sign flip"*;
the flip direction was wrong (it is a collapse to byte-identity) and the ordering
was wrong.

### ⚠ A control differenced against a shipped cell must use `harness/build.py::rust_flags`

**TASK_092, and it was a blocker-class defect no review caught.**
`controls/mkvariants.py` omitted **`-C codegen-units=1`**, which `build.py`
passes to every measured cell — so every number in p46's `NOTES.md` 8b and 0c
was a **ONE-SIDED flag mismatch**, 1–2 `Ir`/call off. ⚠ **One-sided mismatches do
NOT cancel; two-sided ones do** — p46's §8a rolled-vs-rolled control applied the
flag to both sides and was unaffected. **Corrected spans: R4 2, R3 0 — both still
degenerate, so the conclusion got stronger.**

## ⚠ A two-parameter law fitted on axis-aligned bands can be UNDERDETERMINED

**PROVISIONAL — TASK_089, on p46, and it is sharper than p38's missing column.**
p46's `R2 − R4 = 3 + 5n − n·floor(m/2)` was fitted over `n` and `m`. **Fitting on
the two axis-aligned bands alone (vary `n` at fixed `m`, vary `m` at fixed `n`)
leaves a ONE-PARAMETER FAMILY that fits BOTH EXACTLY.** One off-axis point pins
it, and the other **nine are then out of sample at zero residual.**

⚠ **No in-sample residual could have shown this** — unlike p38, where three
missing columns left a fit that was merely wrong out of sample. **A band that
holds every other parameter at its axis value does not constrain a product
term.** **Ship at least one off-axis point per pair of parameters.**

## `GEN-ONLY` cannot fire on a GATE record

**PROVISIONAL — measured at TASK_088.** Editing only a docstring in
`patterns/pNN/inputs/gen.py` classifies **`GEN-ONLY` on the measurement record**
and **`STALE` on the gate record**. `check_stale`'s `gen_only` branch requires
`"input_sha256" in rec`, and **gate records carry none**; they also hash
`NOTES.md` / `README.md` / `spec.md`. **A `check.py pNN` re-run clears it.**
⚠ **So "a docstring edit is free" is true of the measurement record and false of
the gate record.** Budget one gate run.

⚠ **And any edit at all to `c/kernel.c` / `c/kernel.h` — a comment included —
stales the MEASUREMENT record.** There is no comment-only escape. Measured cost
for one pattern: `measure.py p19` = **1 m 17 s**, moving `min_s` / `median_s` /
`spread_pct` across 32 cells plus timestamps and source hashes — **zero `Ir`,
zero static/md5, zero checksum, zero identity.**

---

### ⚠⚠ `malloc_consolidate` fires at a 64 KiB freed chunk and taxes a WHOLE BAND

**TASK_093_REVIEW major 2, reviewed.** A probe's own *bookkeeping* container can
add a step to every `Ir`/element figure in a band, and it looks exactly like a
property of the rung.

`box_arena` read `408.078 Ir`/node on the 2048→4096 band and **`472.050`** on
4096→8192 — a clean `+64`/node that TASK_093 reported as unexplained and
suspected was p26's length dependence. **It is neither.** It is **not** `Vec`
growth doubling: the probe uses `with_capacity(n)` and never reallocates. The
kernel symbol itself is **exactly `99.0 Ir`/node at every `n`**.

`callgrind_annotate` finds a libc symbol carrying **262,010 `Ir` present only at
n=8192** and absent at 2048/4096; `262010/4096 = 63.97`, i.e. the entire step.
Its body is the `xchg %rbx,0(%r13)` / `add $0x8,%r13` fastbin-array sweep —
glibc **`malloc_consolidate`**. The decisive control is one node wide:

```
n=8188 vec_bytes=65504 Ir=3659465
n=8189 vec_bytes=65512 Ir=3659903
n=8190 vec_bytes=65520 Ir=3922410   <- +262,507 Ir for ONE more node
n=8191 vec_bytes=65528 Ir=3922880
n=8192 vec_bytes=65536 Ir=3923290
```

`free()` of the `Vec` backing store crosses **`FASTBIN_CONSOLIDATION_THRESHOLD`
(a 65536-byte chunk)** between 8189 and 8190. Below it the rung is flat:
`(3659903 − 1989775)/4093 = 408.045` against `408.078`.

⚠ **The rule: any `Ir` sweep whose band crosses a 64 KiB freed allocation picks
up a one-off ~262k `Ir` that a per-element figure smears across the whole band.**
Sibling traps already recorded here: **`rep movsb` at 8192 bytes** (callgrind
charges ≈1 `Ir` per byte moved) and **`__x86_rep_stosb_threshold` at 2048**
(`Ir` rises 6.5× exactly where the real cost falls).

✅ **The consequence for p28 was real:** *"`box_arena`'s +68.00 advantage over
`rc` collapses to +4.02 one band over"* is **false** — it is a stable `+68.00`,
and *"p28 could not be costed until its input band was designed"* does not
follow.

---

### ⚠⚠ A COST PAIR THAT OMITS THE ALLOC/FREE MEASURES THE **WALK**, NOT THE CLASS

**Third instance, and `p29` is the one where the same instrument gives both
answers on the SAME PROGRAM.** (TASK_095, PROVISIONAL — unreviewed; the two
earlier instances are reviewed.)

| pattern | pair as probed | pair with the alloc/free present |
|---|---|---|
| `p28` (TASK_091) | `+12.50 Ir`/victim | `+24.00 Ir`/victim (TASK_093_REVIEW) |
| `p29` (TASK_094) | **`−0.00024 Ir`/lookup** | **`+48.01 Ir`/key** (TASK_095) |

`p29`'s `−0.00024` is **real and it reproduces exactly** — a tree walk has no
index, so there is no bounds check to remove, and `Option<Box<T>>`'s niche **is**
the null pointer, so `while let Some(n)` and `while !cur.is_null()` lower to the
same `test/je`. ⚠ **It is a true zero about the part of the program the pattern
is not about.** Add the build and the free and the pair reads `+48.01`, of which
the `remove` term alone is `+18.95`.

> **Before declaring a cost zero, ask which OPERATIONS the pair contains — not
> just whether the two rungs are the same shape.** A pair can be honest, matched,
> reproducible **and still measure the wrong half of the program.**

⚠ **This is NOT the probe-shape defect** (`p46`'s lost range facts, `p26`'s
length dependence). It is the **rung-pair** question recorded above: *probe shape
= same rungs, different harness; different operations = a design choice, argued
not measured away.* **A task file that pins a declared zero before the pair is
designed pins the wrong number** — the `p29` task file did exactly that and the
engineer refused the instruction with a measurement.

---

## ⚠⚠⚠ `-O3 isolated` IS **NOT** INVARIANT. The published marginal moves ±7 with the ENVIRONMENT BLOCK.

**TASK_097 found it; ✅ the MANAGER PROVED THE MECHANISM with a one-variable
experiment the engineer said it had only inferred.** `.temp/mgr97/README.md`
rebuilds it.

`check.py::check_marginal_ir`'s docstring says the ±7 bistable term is
`whole`-mode only and that `-O3 isolated` is *"not merely small, it is **exactly
invariant**"* — *"the only cell class no probe has moved"*. **False.**

**Same binary, same input, same shell; only the length of one environment
variable varied.** p03, `-O3 isolated`, marginal `Ir`/call on `small.bin`:

```
 envpad   unsafe   verus    pair (verus - unsafe)
      0     3059    3065     +6
      1     3059    3065     +6
      7     3059    3065     +6
     15     3066    3058     -8    <-- BOTH FLIP, IN OPPOSITE DIRECTIONS
     63     3059    3065     +6
    255     3059    3065     +6
   1023     3059    3065     +6
   4095     3059    3065     +6
```

⚠⚠ **THE TWO RUNGS MOVE IN OPPOSITE DIRECTIONS, so the PAIR swings by 14** —
`unsafe +7`, `verus −7` — and p03's published `derived_correction`
`(ma−mb)−(ka−kb)` goes **`+6.00 → −8.00`: A SIGN FLIP IN A PUBLISHED NUMBER.**
**14 is 7× the `±2.00` floor the same table uses.**

⚠ **BISTABLE, NOT MONOTONE** — `pad=15` flips it and `pad=63/255/1023` flip it
back. It is a stack-alignment effect, exactly the mechanism the docstring
describes. **Only its SCOPE was wrong**, and the scope is what everything rests
on: **`synthesize.py::marginal` DEFAULTS to `O3/isolated` BECAUSE of that rule.**

**What this does and does not mean.**

- ✅ **It is NOT new in kind.** `RECAP.md`'s settled answer 1 already says the
  R4/R5 pair *"is not a null control … that offset is a **source-path-length
  artefact** (it moves if you clone elsewhere), so the pair is a **biased draw of
  size one**"*, and p06's own floor is **±4.6%**. **This is the KNOWN layout
  population reaching the one class that was declared immune to it.**
  ⚠⚠⚠ **AND `±4.6%` IS AN `ns` FLOOR. DO NOT APPLY IT TO AN `Ir` COLUMN — that
  is a category error and `TASK_130` caught the manager committing it across a
  100-row census.** `p06/NOTES.md` says verbatim *"Take `±4.6%` as the honest
  inter-binary floor for **every `ns` figure** in this file"*, and this file says
  of the same instrument *"a LAYOUT POPULATION IS THE WRONG TOOL … **callgrind is
  layout-blind**"* — which is why the `Ir` side of that very axis measures
  `kernel_exclusive 3002.00` **in all nine runs, a measured ZERO**.
  ✅ **So the honest `Ir` floor on a layout axis is ≈0 (documented ±7 `Ir`, i.e.
  0.002% of a 310 504-`Ir` row), and a `>4.6%` cut applied to `Ir` discards real
  movement: on the hardened-twin census 94 of 100 rows move, median 1.77%, and
  only 35 clear 4.6%.** ⚠ **The `±4.6%` cut IS correct for the wall-clock half —
  that is the floor's home instrument.**
- ⚠ **Binaries are byte-reproducible** (`unsafe e7ea55fa488df703`,
  `verus 75a48f319f14e689`, twice), so this is **not** a build nondeterminism.
  The *program* is fixed; the *process image* is not.
- ⚠⚠ **Any published `-O3 isolated` difference between two rungs carries ±7 PER
  RUNG, i.e. up to ±14 on a pair**, and a pair difference smaller than that is
  **not resolvable without a layout population.** ⚠ **Several published pair
  differences in this tree are smaller than 14.**
- ✅ **REINSTATED AND SHARPENED — REVIEWED at TASK_103.** ⚠⚠ **The manager
  struck the sentence below at TASK_099 and THE SENTENCE WAS TRUE.** It is
  restored, with the mechanism made exact:

  > **TASK_097 also observed it as a between-RUN difference — a `nohup`'d script
  > against an interactive shell, which differ in environment size — and that is
  > the same variable. It is not a property of the launching method; it is a
  > property of the environment block's LENGTH.**

  ✅ **The launcher matters EXACTLY AND ONLY through the bytes it puts in the
  environment block.** `bash -c "cd repo && …"` **exports `OLDPWD=repo`**;
  `subprocess.run(cwd=repo)` leaves `OLDPWD` at its inherited value. On this box
  that is an **11-byte** difference — enough to cross a 16-wide window in a
  32-byte period. **The launcher itself is inert.**

  ✅ **Settled by a CROSSED design, 8 whole `check.py p03` runs**, where `A2` =
  B's launcher with A's environment and `B2` = A's launcher with B's environment,
  each arm's environment read from `/proc/self/environ` before its run:

  ```
                                        env  safe_tuned  unsafe   verus
    A  bash+cd     file  env=short     3269     3418.00  3059.00  3065.00
    B  subprocess  pipe  env=long      3280     3425.00  3066.00  3058.00
    A2 subprocess  pipe  env=SHORT     3269     3418.00  3059.00  3065.00
    B2 bash+cd     file  env=LONG      3280     3425.00  3066.00  3058.00
  ```

  **`A == A2` and `B == B2` on all 8 keys, each arm run twice.** Not the
  launching program, not stdout-to-pipe vs stdout-to-file, not the parent.

  ⚠⚠ **AND IT CLOSES TASK_099's OWN LOOSE END:** its `d1_sweep.sh` opens with
  `cd <repo>` while its `b2_source_to_published.py` uses `subprocess.run(...,
  cwd=REPO)`. **That is exactly the A/B pair** — the `b2` control failed and the
  §D sweep did not **because of an 11-byte `OLDPWD`**, i.e. because of the
  mechanism the retraction had just declared dead.

  ⚠⚠ **THE CONSEQUENCE STANDS UNCHANGED, AND IT IS THE POINT: *"re-run the gate
  and compare"* IS NOT A REPRODUCTION TEST for an `-O3 isolated` marginal** —
  **because two equally natural ways of invoking the gate hand it different
  environments, and nothing in the artefact records which one you got.**
  ⚠ **Byte-identical output across two gate runs has been quoted as evidence at
  least twice in this project.**

  ### ✅ THE REPRODUCTION PROTOCOL, decided at TASK_103

  **Record the environment-block byte length in the gate record** — one integer,
  `len(open("/proc/self/environ","rb").read())`, beside `marginal_ir_per_call`.
  Then **same recorded length ⇒ the marginal must match EXACTLY, and a mismatch
  is a real change** (demonstrated: three arms across two launchers agree to
  `0.00`); **different length ⇒ compare `kernel_exclusive_ir`, or re-run at the
  recorded length.** ⚠ **This is NOT the forbidden pin** — it does not force an
  environment and so cannot make the number reproducible-and-wrong; **it records
  which draw you took, so a disagreement becomes diagnosable.**
  **Complement for the seven exposed cells: publish the pair at `L` and `L+16`**
  — the 32-period/16-window result makes a two-point screen complete, ≈2 min per
  pattern on the two patterns that need it.

  ⚠⚠ **`kernel_exclusive_ir` IS the column to QUOTE but is NOT a reproduction
  test, and the manager's advice to "reproduce against it" was too strong on two
  counts:** *(a)* **it is not in the gate record at all** — it lives in
  `results/pNN-*.json`, which only `measure.py` writes, so reproducing against it
  is not a `check.py` re-run; *(b)* it is **`None` in 302 of 318 `-O3 whole`
  pairs**. ✅ **Its immunity itself is upheld**: `0.00` on 4 of 4 p03 cells across
  both an 11-byte and a 16-byte perturbation, while the marginal moved `±7` in
  the same runs.

  ⚠ **Not established:** environment **length** alone versus length-plus-content.
  `A` and `A2` have byte-identical environments, so launcher-vs-environment is
  settled; length-vs-content still rests on `.temp/r98/p03_sweep.json`.
  **And everything here is `p03` only** — p04, p38 and p46 are unprobed on this
  axis.

  ### ✅ THE SEVEN EXPOSED CELLS, ENUMERATED AT LAST

  `7 of 144` = 24 × 6; the 288 below is ×2 blobs. **Must-fire arm (pad0 vs pad0)
  moved 0 of 288.**

  | # | pattern | cell | `small.bin` | `large.bin` |
  |---|---|---|---|---|
  | 1 | p03 | `safe_tuned` | 3418.00 → 3425.00 | 9067.30 → 9074.30 |
  | 2 | p03 | `unsafe` | 3059.00 → 3066.00 | 8441.30 → 8448.30 |
  | 3 | p03 | `verus` | 3065.00 → 3058.00 | 8447.30 → 8440.30 |
  | 4 | p04 | `safe_tuned` | 3425.00 → 3432.00 | 11724.00 → 11731.00 |
  | 5 | p04 | `unsafe` | 3420.00 → 3427.00 | 11719.00 → 11726.00 |
  | 6 | p04 | `verus` | 3426.00 → 3419.00 | 11725.00 → 11718.00 |
  | 7 | **p46** | **`c-clang`** | 6216.00 → 6209.00 | 23230.66 → 23223.66 |

  **`kernel_exclusive` moved on 0 of 288 in the same scan.**

  ✅ **INDEPENDENTLY CONFIRMED TWICE MORE, on a different axis, by whole-tree
  regenerations of `synthesis/outward_ir.json` months of tasks later:**
  **0 of 58 leaves at the p23 regeneration and 0 of 72 at the p42 one**, while
  `kernel_inclusive` moved 10 in the first — and the movers land exactly at
  `libc+0x189480` in the CALLEE column, which is the known memset term.
  ⚠ **So the immunity is not an artefact of the sweep that first measured it.**

**What is owed, and none of it is done:** the docstring's scope; a decision on
whether every `-O3 isolated` pair difference now needs the layout harness
(`common/layout/`) the way p06's did; and a re-read of every published pair
difference under `|Δ| < 14`. ⚠ **BLAST RADIUS UNREVIEWED — measured on `p03`
only; `p04`, `p38` and `p46` are unprobed.**

⚠ **AND ONE OF THE MANAGER'S OWN COMMIT MESSAGES IS NOW WRONG.** `9f8fa9d` says
of `results/synthesis.md`: *"unlike the last time I quoted a byte-identical
synthesis.md, that zero is MEANINGFUL."* **The acceptance test behind that claim
is sound, but the byte-identity itself is conditional on the launching shell's
environment size.** The zero is evidence about the *acceptance test*, not about
the tree.

### ✅ RESOLVED (TASK_098, reviewed) — the ±7 is ONE libc callee, and `kernel_exclusive_ir` is STRUCTURALLY IMMUNE

✅ **MANAGER-VERIFIED by per-symbol attribution**, `.temp/mgr98/`, p03 `unsafe`
`-O3 isolated`, marginal `Ir`/call, pad 0 against pad 15:

```
symbol                                   pad0     pad15    delta
unsafe::kernel  (the measured symbol)  3002.00   3002.00   +0.00
0x189480        libc.so.6                43.00     50.00   +7.00
unsafe::main                             14.00     14.00   +0.00
TOTAL (whole-program marginal)         3059.00   3066.00   +7.00
```

**`libc+0x189480` is `__memset_avx2_unaligned_erms`** (`vpbroadcastb` /
`vmovdqu %ymm0`; a stripped libc mis-names it `__nss_database_lookup+0x1440`).
**100% of the swing is inside it.** Decomposition of the pair:
`R5 − R4 = kernel 0 + memset{−7, 0, +7} + main(−1)`.

> ⚠⚠ **SO THE KERNEL-EXCLUSIVE COLUMN CANNOT CONTAIN THE ±7, AND DOES NOT —
> 0 of 288 triples moved while 14 marginal cells did.** The exposed surface is
> **exactly one column**: `synthesize.py::derived` prints `k − k2 + c` with
> `c = (ma−mb) − (ka−kb)`, so the kernel terms cancel and the printed figure is
> algebraically **`ma − mb`** — the whole-program marginal pair difference, 1:1.

✅ **THE HEADLINES SURVIVE, and they were checked rather than assumed** — over a
**32-pad sweep**: p01's `+4…+5`/call, p16's *"a single integer per call"* and
p46's `0.00000` per-MAC tax **all swing `0.00`**. ⚠ **And the SLOPE protection is
exact:** `d_ir_d_work` moves **`0.000000000000`** on all 8 exposed cells, because
the term is per-call and identical on both probe blobs. **A slope survives where
a level does not — that distinction is the general rule.**

⚠ **The exposed set is SMALL and this file's earlier fear was too wide: 7 of 144
cells, across THREE patterns.** ⚠⚠ **This said "2 patterns, 7 of 144 cells" and
that is ARITHMETICALLY IMPOSSIBLE — corrected at TASK_099 (PROVISIONAL,
unreviewed). The third is `p46`'s `c-clang` cell, which is the seventh.** The
manager wrote the pattern count and the cell count from two different passes and
never checked one against the other; **two numbers in one sentence that cannot
both be true is a defect any reader can catch, and it survived into
`.memory/`.** `check_marginal_ir`'s four-pattern list is still **wrong** — p38
and p46's *Rust* rungs swing `0.00` over 32 pads.

⚠⚠ **WITHDRAWN: 4 CELLS.** p03 and p04's `R5 − R4 = +6.00` takes **`{−8, −1,
+6}`** over 32 pads (support 14 / 4 / 14). ⚠ **The reproducible content is
`−1.00` — the `main` term — and it is the OPPOSITE SIGN to the published
`+6.00`.** The `+6` was one draw from a trimodal distribution.

⚠⚠ **RETRACTED AT TASK_099 — THE PARAGRAPH BELOW IS FALSE AND IT WAS THE
MANAGER'S.** ⚠ **PROVISIONAL: TASK_099 is unreviewed. The superseded text is
kept, per convention, because the refutation matters more than the tidiness.**

> ~~**AND THE CONTROL ALREADY IN `results/synthesis.md` IS VACUOUS: `64 mod 32
> == 0`.** Its second sweep used a *"64-byte-longer env"*, which is **the same
> alignment phase as pad 0**, so it could not have moved. **Fifth instance of a
> control that cannot fail.**~~

**Measured:** the sweep does not add 64 bytes. It sets `SLB_ALIGN_PAD=z*64`,
which lengthens the environment block by **87 bytes**, and **`87 mod 32 = 23`,
not 0. THE CONTROL FIRED.**

✅ **MANAGER-VERIFIED INDEPENDENTLY — the 87 decomposes exactly, and the
decomposition is the whole lesson:**

```
  envp pointer slot        8      <-- the part the manager forgot entirely
  name "SLB_ALIGN_PAD"    13
  "="                      1
  pad z*64                64      <-- the ONLY part the manager counted
  NUL                      1
  ----------------------  87      87 mod 32 = 23    (64 mod 32 = 0)
```

⚠⚠ **Four of the five terms were invisible to the original argument**, which
reasoned about *"a 64-byte-longer environment"* because that is what the prose
said. **A variable does not cost its value; it costs a pointer slot, its name,
an `=`, its value and a NUL.**
It is not the fifth vacuous control; **it is a working one**, and it produced the
published `50.00 → 43.00` to the instruction: p03 `safe_tuned`'s memset goes
`300129 → 258129`, i.e. `129 + 50.00×6000` against `129 + 43.00×6000`.

⚠⚠ **THE LESSON IS THE MANAGER'S, NOT THE CONTROL'S: the arithmetic was done on
the DOCUMENTED intent (*"a 64-byte-longer environment"*) instead of on the
BYTES THE PROCESS ACTUALLY RECEIVES.** A `mod` argument about alignment must be
computed from the measured block length, never from the prose describing it.
**And this was written into a task file as an established fact, which is the
precise failure `PROTOCOL.md` rule 14 was added to prevent — one task earlier.**

✅ **What survives unchanged:** the `< 2.00` band's claim that *"nothing real
hides below the floor"* **is still false** — p04's `R3 − R4` correction is blank
at one phase and `±7` at another. That half never depended on the vacuity claim.

**The instrument, decided:** ⚠⚠ **a LAYOUT POPULATION IS THE WRONG TOOL AND FAILS
IN THE DANGEROUS DIRECTION** — it varies the *program*, measures `ns`, and
**callgrind is layout-blind, so it would return ≈0 and read as "no effect."**
✅ **The right axis is `argv` length and `envp` length, and they are ONE axis**
(measured: same ±7, `kernel_exclusive` `3002.00` in all 9 runs). Same *family* as
`RECAP.md`'s settled answer 1, **a different variable**. **Cost: a 32-pad sweep
is ≈2 min/pattern against ~4.8 h for a layout population; only p03/p04 need it,
≈4 min.** ⚠ **Do NOT "fix" this by pinning the gate's environment** — cheap
(`check.py` is not measurement-hashed) but it makes the number
**reproducible-and-wrong.**

---

## ⚠⚠ A PANIC EDGE CAN BE INVISIBLE IN DISASSEMBLY TEXT — PIE + GOT-INDIRECT CALLS

**TASK_115, PROVISIONAL. It produced a published false claim, so it is not a
curiosity.** Under PIE the call to the panic handler goes through the GOT, and
`objdump` prints the target as something like **`_DYNAMIC+0x2c8`** rather than as
a panic symbol. ⚠⚠ **So *"grep the disassembly for a panic edge"* is a FALSE
NEGATIVE, and `TASK_092` used it to report that `p26`'s two rungs had NO panic
edge when BOTH HAVE ONE.** That single wrong reading is what made `p26` look like
a large safe-vs-unsafe difference with no compare-and-branch anywhere — the
apparent counterexample to finding 37 that motivated a whole task.

✅ **The fix: resolve through `.rela.dyn` instead of reading the mnemonic text**
(`.temp/t115/resolve_calls.py`). ⚠ **Anything in this repo that decides "is there
a check here?" from disassembly TEXT is suspect on a PIE binary.**

## ⚠ `memset` CROSSES TO `rep stosb` AND CALLGRIND THEN CHARGES ~1 `Ir`/BYTE

**TASK_115, PROVISIONAL — and it is the SECOND instance of one effect.** glibc's
`memset` switches implementation between **2000 and 4000 bytes**; below the
crossover a call costs `36…152 Ir`, above it callgrind charges **≈`1.011
Ir`/byte**. ⚠⚠ **So a "cost per element" that spans the crossover is measuring
the LIBC's dispatch decision, not the kernel** — and the denominator moves under
you. **`p24`'s row already records the same effect for `memcpy` at 8192 bytes**
(`rep movsb`, ≈1 `Ir`/byte), where it turned a `27.5% → 22.2%` "step" into an
artefact of the DENOMINATOR. ⚠ **Two libc routines, same trap: check whether any
swept band crosses a bulk-routine threshold before quoting a rate.**

## ⚠⚠ THE CONTROLS THAT COULD NOT HAVE FIRED — the running list, in one place

**Landed at TASK_100. PROVISIONAL where an entry cites an unreviewed task.**

⚠⚠ **THE COUNT IS SEVEN LIVE ENTRIES. Entry 5 is RETRACTED, so the list numbers 1–8 and contains seven.** ⚠⚠ **AND IT WENT STALE AGAIN THE MOMENT `TASK_118` ADDED ENTRY 8 — the manager updated this line in the same edit that added the entry, having ALREADY quoted the old figure into THREE queued task files. That is the third time this exact count has rotted. THE FIX IS NOT A BETTER NUMBER: task files now say *derive it*, and carry no ordinal at all.** ⚠ **And the manager then quoted *"seven"* into FIVE task files — after writing the sentence two paragraphs below that says *keep the list, not the ordinal*, and after the ordinal had ALREADY gone wrong once the same way.** Caught by `TASK_108`. **The failure is not arithmetic: a count is a cached derivation of a list, and it goes stale exactly like every other cached number in this repo. Cite the list; if you must give a number, derive it at the point of writing.**
This project keeps writing checks that pass because they *cannot* fail, and until
now the count lived as a bare ordinal (*"the fifth instance"*) scattered across
files — ⚠ **which is how the count itself went wrong: entry 5 below was
RETRACTED, so anyone quoting "five" was quoting a number one of whose members had
already been struck.** Keep the list, not the ordinal.

1. **The `axiom_decls` regeneration.** The manager added the field to 22 gate
   records, regenerated `results/synthesis.md`, got a **byte-identical** file and
   quoted that as *"the change moved no published number"*. It is byte-identical
   because **`synthesize.py` reads `tcb_items` and the word *"axiom"* appears
   ZERO times in `synthesis/`** — the published column cannot see the field.
2. **`TASK_084`'s limb 3, verified in two halves with the join never run.** One
   script proved *source → gate log*, a second proved *hand-edited JSON →
   `synthesis.md`*, and **nobody ran a real axiom through a real gate into the
   record it wrote and on into the published table.** The review did, on ten
   routes, and limb 3's own stated failure mode reproduced on three.
   ⚠ **A test split across two artefacts tests neither seam.**
3. **`harness/limbs.py::TWIN_BANNED` missing `"external_body"`** — `\bexternal\b`
   does not match it, so the re-derivation tool under-reported `5ct-cfg`.
4. **`TASK_086`'s harm table, truncated by `head -4`.** gcc's UBSan report is
   **exactly four lines** and ASan's banner lands on lines 5–6, so four rows
   (`p21`, `p24`, `p26`, `p41`) could only ever show their UBSan half.
   ✅ **Re-run with `grep` at TASK_100: four cells were corrupted and ZERO
   verdicts were.**
5. ~~**The `64-byte-longer environment` control, `64 mod 32 == 0`.**~~
   ⚠⚠ **RETRACTED AT TASK_099 — THIS ENTRY WAS ITSELF A CONTROL-SHAPED ERROR.**
   The sweep adds **87** bytes, not 64 (`8` envp pointer slot `+ 13` name `+ 1`
   `=` `+ 64` pad `+ 1` NUL), and `87 mod 32 = 23`. **The control fired.** The
   manager computed the alignment from **the prose describing the control**
   instead of from the bytes the process receives.
6. **`TASK_100`'s own first `p42` leak probe, `if (acc & 1)`** — `acc` is **even
   for both p01 inputs**, so the leak branch was unreachable and the arm could
   never fire. ⚠ **Caught by the reviewer itself, by printing `acc`**, before it
   reached a conclusion; changed to `acc != 0` and re-run.

7. ⚠⚠ **`TASK_099`'s `a3_launcher.py`, AND IT CARRIED A BLOCKER.** It existed to
   test whether the launching method changes the ±7, and **both of its arms were
   the same arm**: arm A ran `bash -c "timeout 60 <py> a3_launcher.py --child"`
   with **no `cd` and no `cwd=`**, so it was byte-identical to arm B. The one
   variable it existed to vary was **held constant by construction**, so it could
   only ever print *"identical"* — and C7, a blocker that struck a true sentence
   out of `.memory/`, was built on it. It also measured the block length from
   `os.environ` (a Python dict) rather than `/proc/self/environ`.
   ⚠⚠ **ITS LESSON IS DISTINCT FROM ENTRY 5's AND IS THE MOST TRANSFERABLE ONE
   HERE: A CONTROL MUST REPRODUCE THE COMMAND, NOT THE IDEA OF THE COMMAND.**
   The probe modelled *"bash versus python"*; the arms that actually differed
   were `bash -c "cd X && cmd"` versus `subprocess.run(cmd, cwd=X)`, **and the
   `cd` was the entire effect** — it exports `OLDPWD`, 11 bytes.

8. ⚠⚠ **`p42`'s `controls/ledger_leak.py` — AND IT IS A DIFFERENT SHAPE FROM
   EVERY ENTRY ABOVE. `TASK_118`.** ⚠ **Entries 1–7 are all *a control that
   COULD NOT HAVE FIRED*. This one FIRED, on both arms, and its firing did not
   support the sentence it printed.** Its two arms were **DELETIONS** — remove
   the exit-emptying statement, Verus rejects — so together they distinguish
   *no exit-emptying statement* from **SOME** *exit-emptying statement*.
   ⚠⚠ **The script concluded *"states leak-freedom"*, which is a claim about
   WHICH statement, and no deletion arm can reach it.** **A program that empties
   the ledger WITHOUT FREEING passes both arms and leaks** — that is exactly the
   `atk_decoy_err` leaker, `19 verified, 0 errors`.
   ⚠⚠⚠ **THE LESSON, AND IT SHARPENS THIS FILE'S OWN RULE RATHER THAN REPEATING
   IT: *"before believing a check, ask what would make it FAIL"* IS NECESSARY AND
   NOT SUFFICIENT. YOU MUST ALSO ASK: *"and would its FAILING mean what the
   script says its PASSING means?"*** ⚠ **A deletion arm proves NECESSITY. A
   claim about sufficiency needs an ATTACK arm** — `TASK_118` rewrote the control
   to five arms, with **two attacks pinned as ACCEPTANCE arms** (they must
   VERIFY, because they are the known hole) so that a future encoding which
   rejects them makes the script FAIL rather than silently pass.

9. ⚠⚠⚠ **`TASK_128`'s TWO `_calib` ARMS — AND THIS IS ENTRY 8's SHAPE WITH THE
   SIGN REVERSED, WHICH IS WORSE. `TASK_130`.** ⚠ **Entry 8 is *a control that
   fired and whose firing did not support its printed sentence.* These two
   fired, supported the OPPOSITE of the sentence they were printed under, and
   were FILED AS CALIBRATION.**

   - **Limb 2: `_calib2.rs` is arm E — bound still the INPUT EXTENT — plus a
     proved counting function OF THE SAME SHAPE AS THE MECHANISM'S, whose result
     is DISCARDED. It reads `5 verified`, exactly as the mechanism arm does.**
   - **Limb 3: `_calibRANGE_bv.rs` is the same trick** — arm RANGE plus one
     *unrelated* `assert … by (bit_vector)`, also `4 verified`.

   **Both were used to DECOMPOSE a `+2` (*"1 function + 1 loop"*), and read that
   way they support the finding. Read as SPECIFICITY controls — which is what
   they structurally are — they refute it.** ⚠⚠ **THE HEADLINE THEY WERE PRINTED
   UNDER (*"the ladder can price a mechanism on `obligations`"*) IS NOT MERELY
   UNSUPPORTED BUT INVERTED: at the project's own kernel convention the
   `obligations` column RANKS THE DEAD-CODE ARM (`5`) ABOVE THE MECHANISM ARM
   (`4`), while assembly and `Ir` separate them at `+208` bytes and
   `+329.00 Ir`/call.**

   ⚠⚠⚠ **THE LESSON, AND IT IS NEW: A CALIBRATION ARM AND A SPECIFICITY CONTROL
   CAN BE THE SAME PROGRAM. Whenever you build an arm to explain HOW MUCH a
   column moved, ASK WHETHER IT ALSO SHOWS THE COLUMN WOULD MOVE WITHOUT THE
   MECHANISM — because if it does, that is the stronger reading and it points
   the other way.** ⚠ **Neither the engineer nor the manager saw the second arm;
   the manager saw the first only by RE-RUNNING the artefacts instead of reading
   the report, and even then got the SCOPE wrong** (see `RECAP.md` finding 44).

   ✅ **The operational test that settles this class, and it is cheap: measure a
   column's SPELLING SPREAD against its PRESENCE GAP. `Ir` came out `8519 : 1`
   — invariant under re-spelling, moving under presence. `obligations` came out
   `1 : 1`, and NEGATIVE at the kernel convention. A column whose ratio is near
   1 is not measuring the mechanism.**

10. ⚠⚠ **A CONTROL WHOSE PUBLISHED NUMBERS ARE NOT THE ONES ITS OWN COMMITTED
    SCRIPT AND INPUTS PRODUCE. `TASK_131` on `TASK_129`'s `crosscheck.py`.**
    ⚠ **Distinct from entries 1–7 (*could not have fired*) and from entry 9
    (*fired, and pointed the other way*): this one fired, was read correctly, and
    its TABLE was captured from an EARLIER version of the instrument.**
    **Re-running the script against its own byte-identical inputs differs in
    **18 of 27 cells** (`strlen` 586→633, `sprintf` 646→561), and the sentence
    it licensed — *"coreutils is 0 on eight of nine, so the pipeline is not
    lossy by construction"* — is **five of nine, of which two are trivial
    `0`-vs-`0` rows, i.e. 3 of 7 non-trivial.** ✅ **Diagnosed from mtimes
    alone: the table predates the last instrument fix by three minutes.**
    ⚠⚠⚠ **THE QUESTION IT ADDS: *were these numbers produced by the code that is
    committed, or by an earlier one?*** ✅ **The cheap defence, and it worked in
    the same task: EVERY OTHER ARM THAT WAS WRITTEN TO A FILE REPRODUCED
    BYTE-EXACTLY. The one that lived only in a terminal did not.** ⚠ **So:
    a number quoted from a terminal is undated. Write arms to files and
    regenerate them from a `REBUILD.sh` at the end.**

11. ⚠⚠⚠ **A CHECK WHOSE OWN OUTPUT IS AN INPUT TO THE ARTEFACT IT CHECKS.
    `TASK_127`, reviewed and sharpened at `TASK_132`.** ⚠ **It PASSES the
    must-not-fire arm and still oscillates forever, because the oscillation
    begins THE FIRST TIME THE CHECK FIRES.**

    **`harness/report.py` rendered the gate record's `verdict` into
    `results/tables/*.md`, and `check.py` stage `9c` re-renders that table and
    fails on a difference — inside the run that WRITES `verdict`:**

    ```
    run N    9c fires -> rep.fail -> this run's verdict is FAIL
    report.py         -> the table now prints  verdict `FAIL`
    run N+1  render(FAIL record) == table -> FRESH -> verdict PASS
    run N+2  render(PASS record) != table -> FIRES AGAIN -> forever
    ```

    **Measured before the fix: 19 of 26 tables changed bytes when `verdict`
    changed.** ✅ **Fixed at the source — `verdict` is no longer rendered.**

    ⚠⚠⚠ **THE QUESTION IT ADDS, AND NO OTHER ENTRY ASKS IT: *DOES THIS CHECK
    WRITE ANYTHING THE THING IT CHECKS READS?*** **The list's standing question —
    *what would make it FAIL?* — is satisfied here and does not help.**

    ⚠ **THE RULE: a field a gate run WRITES must not be rendered into an artefact
    that same gate run CHECKS.** **`loud`, `controls_json`, `idiom_audit` and
    `contract_sha256` are deterministic functions of the committed sources and
    are safe; `verdict` and `blocked` are functions of the RUN.**

    ⚠⚠ **AND THE TWO THINGS THE REVIEW ADDED, BOTH OF WHICH GENERALISE:**

    - ⚠⚠ **THE DETECTOR BUILT FOR THIS IS A DENY-LIST, NOT A CENSUS**
      (`harness/tools/table_render_inputs.py --selfref`): its run-scoped key list
      is HAND-WRITTEN and 25 of the record's 34 keys are unclassified, so a
      `report.py` rendering `table_render` — **stage 9c's own verdict** —
      measures `26/26 READ` while the detector prints `0` and passes.
      ✅ **Invert to an ALLOW-LIST over the measured read set.** ⚠ **A detector
      for a self-reference that is itself enumerated by hand can only find the
      self-references you already thought of.**
    - ⚠⚠ **REMOVING THE SELF-REFERENCE LEAVES A ONE-RUN LAG, AND THE LAG IS NOT
      FREE.** **Stage 9c runs MID-GATE against the PREVIOUS run's record, so:
      add one unpinned `patterns/*/controls/*.json`, stage 9b shouts (and does
      not fail), and `run 3 = PASS / 9c FRESH` — where a user commits — then
      `run 4 = FAIL / 9c STALE-CONTENT` with nothing changed.** ⚠ **The trigger
      is in NEITHER digest, so `--check-stale` cannot see it.** ⚠⚠ **Do not
      accept *"the older check has the same shape"*: stage 9 compares LIVE
      `spec.md` against the table, so its DETECTION has no lag; 9c's lag is in
      the detection. Bound: 26 `rep.shout(` sites, 5 firing, 7 latent.**

12. ⚠⚠⚠ **EVERY NUMBER IN A RETRACTED SENTENCE CAN BE ARITHMETICALLY CORRECT,
    SO A READER WHO CHECKS THE ARITHMETIC FINDS NOTHING WRONG.** `TASK_135`,
    reviewer work, ✅ **manager-verified against `p17`'s own NOTES and fixed in
    place.**

    `RECAP.md` published ~~*"lag-4 differencing gives 26, 26, 26, 26 with ZERO
    residual = `6.50 Ir` per request — a mod-4 sawtooth from the 4×-unrolled
    table walk"*~~ for about **fifty tasks** after `TASK_083_REVIEW` majors 6
    and 7 retracted **both halves**. ⚠ **The staircase reproduces. The residual
    reproduces. The four 26s reproduce.** **What was retracted is the
    CONCLUSION**: `6.50` is the mean of a band that samples each residue once
    per four (both shipped inputs pay `7.00`, so a 20-range extrapolation is
    ELEVEN LOW), and **neither rung's suffix-table walk is unrolled at all**.

    > ⚠⚠ **A VERIFICATION PASS THAT RE-DERIVES THE FIGURES CANNOT SEE THIS
    > CLASS.** The figures are the part that survived. **Ask separately what the
    > figures were said to MEAN, and whether that reading was ever attacked.**

    ⚠⚠⚠ **SECOND INSTANCE, AND IT IS THE MANAGER'S OWN — RE-RUNNING SOMEONE'S
    SCRIPT CHECKS THE ARITHMETIC, NOT THE EXPERIMENT DESIGN.** `TASK_134`
    published *"in `p25`'s shipped heap topology `realloc` NEVER moves,
    `moved = 0/12` under both compilers"*. **The manager re-ran the probe, got
    `0/12` under both compilers, and stamped it ✅ manager-verified — into
    `RECAP` finding 48, the `p25` catalogue cell, and a kill that stood for nine
    tasks.**

    ✅ **`TASK_143` refuted it on a CORRECTED probe: the single-vector topology
    moves `11/48`, and a token vector plus a string table — what a PARSER does —
    moves `24/48`, identical under gcc and clang.** ⚠⚠ **`0/12` was a property of
    a GROWTH SCHEDULE THAT NEVER CROSSES `16 → 32`. The script was faithful; the
    INPUT it was driven with could not exhibit the phenomenon.**

    > ⚠⚠⚠ **BEFORE STAMPING A RE-RUN: ask what input would make this probe say
    > the OPPOSITE, and check the probe can reach it.** A probe that cannot
    > produce the negative result is not evidence for the positive one — this is
    > entry 14's *"a control that fires is not a control that tested what you
    > said it did"*, on the OTHER side of the same coin.

    ⚠ **The `TASK_143` engineer hit the identical trap (its first adversarial
    input grew only `4 → 8`), FOUND it with a dedicated `probe_when.c`, and
    disclosed it rather than quietly fixing it.**

    ⚠ **`.memory/03-measurement.md` already carries the governing rule — *"an
    out-of-sample test validates the LAW, not the STORY"* — and it was violated
    by a document that quotes it. **Any 8-point sequence can be lag-4
    differenced; four equal differences are a fact about the numbers, not
    evidence of which loop.**

13. ⚠⚠⚠ **A STALE `PROVISIONAL` MARKER IS NOT INERT — IT TELLS EVERY READER
    WHICH ITEM NOT TO TRUST, WHILE THE LIVE DEFECT SITS IN THE PARAGRAPH ABOVE
    IT.** `TASK_135`.

    `p17` §10b's marker said *"awaiting review"*. **§10b had been reviewed
    TWICE** — attacked at `TASK_083_REVIEW` (the attack WON), replacement landed
    at `TASK_084`, upheld at `TASK_084_REVIEW` item 12. ⚠⚠ **So the marker was
    stale AND it was guarding the wrong thing: the defect was the paragraph
    carrying it, which was still publishing the retracted claims.**

    > ⚠ **A marker spends a reader's scepticism. Point it at a live claim or
    > remove it** — and when triaging markers, **read what they GUARD, not only
    > whether their stated ground still holds.**

    ⚠⚠ **AND MARKERS HIDE INSIDE HASHED FENCES, WHERE NO TRIAGE HAS EVER LOOKED:**
    `p09-bitset/spec.md`, `p16-tlv-walk/spec.md` and `p42-goto-cleanup/spec.md`
    each carry one **inside the `slb-contract` block**. ⚠⚠⚠ **BUT ADJUDICATED AT
    `TASK_138` ONLY ONE WAS LIVE DEBT, AND THE FIRST TELLING OF THIS ENTRY
    OVERSTATED IT TWO WAYS.** ✅ **`p09`'s fence contains *"unattacked"* ZERO
    TIMES — its `PROVISIONAL` is an adjective inside a CITATION of another
    document, so it spends no scepticism about `p09` at all, and it STANDS.**
    ⚠ **`p42`'s is NARRATIVE about a past defect.** **Only `p16` was stale, so
    the bill was ONE `contract_sha256` move and ONE gate re-run, not two.**

    ⚠⚠⚠ **AND THE UNDERLYING CLAIM WAS WRONG IN THE WAY THIS WHOLE ENTRY IS
    ABOUT: *"a reviewer APPLIED the test and it FIRED"* IS NOT *"a reviewer
    ATTACKED the repair"*.** `TASK_045_REVIEW` says *"Apply the direction
    test"* and files the result under *Clean negatives*, **reporting a MAGNITUDE
    where the repair's criterion is DIRECTION OF FLATTERY.** ✅ **The true status
    is EXERCISED, NOT ATTACKED** — applied by name on nine patterns, fired once,
    **never itself the object of a review** — and `.memory/01-ladder.md` carried
    BOTH readings at once, forty lines apart. ⚠ **An instrument that WORKS is
    not an instrument that has been AUDITED.**

    ⚠⚠ **AND A MARKER SWEEP MISSED ONE BY A SINGLE LETTER: `p42`'s is
    `unreviewed`, lower case, and every token list used was CASE-SENSITIVE.**
    ✅ **Sweep case-insensitively, and read the tier out of the RECORDS rather
    than hard-coding it** (`.temp/t138/sweep_markers.py`).
    **Named-token totals: contract 3, gate 12, measure 0 — no marker anywhere
    costs a re-measure.** ⚠ **`grep PROVISIONAL RECAP.md` is not the census; the
    real figure is 13 lines in `RECAP.md`, 65 in `.memory/`, 3 in
    `SYNTHESIS.md`, and 2 inside hashed contracts.**

14. ⚠⚠⚠ **A CONTROL THAT FIRES IS NOT A CONTROL THAT TESTED WHAT YOU SAID IT
    DID.** ✅ **The manager's own, this session, caught on inspection rather than
    by an agent.**

    Five negative controls were run against `harness/tools/composition.py` and
    **all five "fired"**. ⚠ **Three fired for the wrong reason.** Two were run by
    copying the script to `.temp/` and editing the copy — **the copy computed
    the repo root from its own path, so it TRACEBACKED** and the non-zero exit
    was read as the control working. The third planted a 27th pattern directory
    to test the *"built but unclassified"* arm, but tripped the
    *"`patterns/` and `results/gate/` disagree"* arm first, **leaving the arm it
    was aimed at untested.**

    ✅ **Re-run in place with a byte-identical restore (`sha256` checked before
    and after), all five now fire on their OWN reason.**

    > ⚠⚠ **CHECK THE REASON, NOT THE EXIT CODE. `rc != 0` is what a broken
    > control and a working one have in common** — the same shape as this box's
    > ASan-behind-`LD_PRELOAD` trap, where both cases exit 1.

    ⚠ **And the control that matters most here compares MEMBERSHIP, not totals:**
    moving `p23` from spatial to logical still sums to 26, and only a set
    comparison catches it.

15. ⚠⚠⚠ **A GREEN STAGE `9c` IS NOT EVIDENCE THAT THE PUBLISHED TABLE MATCHES
    THE RECORD THAT RUN WROTE.** `TASK_140`, ✅ manager-reproduced and repaired.

    **Stage 9c compares `results/tables/pNN.md` against a render built from the
    PREVIOUS run's record.** So a run that changes `controls_json`, `loud` or
    `idiom_audit` **passes itself and poisons the next run.**

    ✅ **`p29` is the first row to exhibit it, and it was DECIDABLE FROM THE
    COMMITTED TREE WITH NOTHING RUN:** the gate record said
    `controls_json: all four FRESH` while the committed table carried **four
    lines saying those same sidecars were STALE**, under a heading reading
    *"these are not defects"*. **`check.py p29` then returned `FAIL [tables]`.**
    ⚠ **A 27-pattern sweep found 26 render byte-identically; only `p29` drifted.**

    > ⚠⚠ **THE MANAGER READ `verdict: PASS` OUT OF THE RECORD — WHICH IS THIS
    > FILE'S OWN RULE — AND WAS STILL WRONG.** *"Read the record, not the log"*
    > protects against grep artefacts. **It does not protect against a record
    > that is one run behind the artefact it certifies.**
    > **Ask WHICH RUN wrote the record you are reading, and whether anything it
    > changed feeds the table.**

    ⚠⚠⚠ **A SECOND INSTANCE, FROM THE READER'S SIDE, AND IT IS THE SAME MISTAKE
    IN A DIFFERENT COSTUME (`TASK_142`, self-disclosed): an agent waited for a
    gate run with `until grep -qE 'real\s' <gate.log>`, which matched the
    UNRELATED line `ok f: real call site found`, and so read the record
    MID-RUN — reporting `PASS` off the PREVIOUS record.** ✅ **Caught by
    checking the record's own `unsafe.rs` hash.**

    > ⚠⚠ **WAIT ON THE PROCESS, NEVER ON LOG TEXT.** A log line is not a
    > completion signal, and a `grep` pattern loose enough to match early is the
    > same defect as one loose enough to match the wrong thing.

    ✅ **Repair is two commands — `harness/report.py pNN` then `check.py pNN`.**
    ⚠ **This is finding 46's one-run lag, and the manager hit it on `p16` TWO
    TASKS EARLIER, fixed it there, and did not think to check `p29`.**

    ✅✅ **CLOSED IN CODE AT `TASK_141`, AND PROVED ON THE REAL HISTORICAL STATE
    RATHER THAN A MOCK.** **`check.py` now moves stage `9b` above `9c`, hands
    `9c` a `gate_now` snapshot of `{contract_sha256, controls_json, idiom_audit,
    loud}`, and re-compares that snapshot against the record actually written,
    failing loudly on drift.** ⚠ **The obvious fix — moving `9c` after the write
    — was REJECTED because it reintroduces the `verdict` self-reference
    `TASK_127` removed (entry 11).**

    ✅ **The must-fire arm rebuilds `d41ba6c`'s exact state in two repo-shaped
    sandboxes differing only in `check.py`/`report.py`
    (`.temp/t141/probe_9c/build_sandbox.py`, `arm.py`) — ✅ manager-re-run:**

    ```
    old code, d41ba6c state   render == published == b1398ea3ae68df9a   0 failures   <- the BUG
    new code, same state      render b0d5af3b != published b1398ea3    1 failure, 4 lines
    new code, repaired state  render == published == b0d5af3b533f5826   0 failures   <- silent
    ```

    ⚠⚠ **`b1398ea3ae68df9a` is the `render_sha256` `d41ba6c`'s COMMITTED RECORD
    ACTUALLY CARRIES**, so the sandbox reproduces the historical defect rather
    than approximating it. ✅ **`gate=None` renders 27/27 tables byte-identically,
    so the report change is inert where it is not wanted.**

16. ⚠⚠⚠ **THE GATE'S MIRI STAGE RUNS THE *CORRECT* RUNG, SO IT CAN NEVER
    SUBSTANTIATE A *"MIRI SEES / DOES NOT SEE"* CLAIM.** `TASK_139`, scope
    corrected by `TASK_140`.

    ✅ **Structural, not a sampling accident: `miri.sources == ["unsafe.rs"]` in
    27 of 27 records, and 202 of 202 rows read `ub: false`.** **`unsafe.rs` is
    the rung that does NOT have the bug**, so every row is a statement about a
    correct program.

    > ⚠ **Any pattern publishing a mechanism table with a Miri row owes a
    > DEDICATED arm that runs Miri over the BUGGY spelling.**

    ⚠ **`TASK_139` also claimed *"no other pattern has one"* and that is FALSE —
    `p18`, `p22` and `p42` ship dedicated Miri arms, and
    `p42/controls/miri_seeds.sh` states this same hole in writing.**
    ✅ **`p29` ships one too, and its result is the interesting one: Miri reports
    UB on both use-after-FREE inputs, and on the use-after-RECYCLE input it runs
    the buggy program to completion, says nothing, and prints a different
    number.**

17. ⚠⚠ **A PROBE THAT ADDS A FEATURE *PLUS* AN ATTRIBUTE CANNOT ATTRIBUTE THE
    RESULT TO THE FEATURE.** `TASK_140`.

    `TASK_139` proposed the rule *"a `struct` inside `verus!` is its own
    obligation, exactly as a `const` is"*, measured by adding *"one further BARE
    `#[repr(C)] struct Rec2 { a: u8 }"*. ⚠⚠ **The probe's struct carries
    `#[derive(Clone, Copy)]`, and the word *"bare"* appears in the report AND in
    `p29`'s HASHED `obligations_note`.**

    ✅ **The measured rule is the opposite: a bare `struct` carries ZERO** (adding
    one gives 25, not 26; adding three still gives 25). **`#[derive(Clone)]`
    carries the obligation.** ✅ **Cross-checked against the tree: `p36`'s bare
    `pub struct OpTag<const K: u8>` counts ZERO and sums exactly to its pinned
    12.**

    ⚠ **The published NUMBER was right and its stated CAUSE was wrong** — `p31`'s
    failure mode — **and it reached a hashed block, so correcting it costs a
    contract move.**


18. ⚠⚠⚠ **A `derived_from_sha256` THAT RE-HASHES CLEAN DOES NOT MAKE THE
    SIDECAR'S NUMBERS REPRODUCIBLE.** `TASK_141`; second instance after `p23`'s
    `controls.log`.

    `p29`'s `controls/arms.json` re-hashed clean and was **publishing a DRAW as a
    figure**: regenerating it gave `keyonly`/`deref` `wrong_total` = **7, 8, 7,
    7** across four draws, while every other cell was constant. ⚠ **The two cells
    that move are exactly the arms that DELETE THE LIVENESS CONJUNCT and so read
    freed memory by construction.**

    > ⚠⚠ **THE RULE THAT GENERALISES: any control arm built by DELETING a safety
    > check produces DRAWS, NOT FIGURES, in exactly the columns the deletion
    > makes undefined.** **Pin those columns as not-covered, or publish a range
    > and say it is one.**

    ✅ **The pin proves the sidecar was generated from THESE sources; it says
    nothing about whether re-running them yields the same numbers.** Those are
    different properties and this project has now conflated them twice.

19. ⚠⚠⚠ **A CHECK CAN BE A TAUTOLOGY OF THE REPRESENTATION IT IS WRITTEN
    OVER — AND THEN IT CANNOT FIRE, WHILE READING EXACTLY LIKE A DERIVATION.**
    `TASK_145` M1 on `p32`, repaired at `TASK_147`.

    `model.py` claimed — **in six places, two of them inside
    `contract_sha256`** — to *"compute every index the buggy rung would compute
    and report whether one escapes"*. Its guard was `0 <= s < SLOTS` over a slot
    drawn, by construction, **from a successor map over `0..SLOTS-1`**.

    ```
    firings in 20 000 fuzzed BUGGY windows, old detector:        0
    the one input that would have set it (`read(Block(255))`):   crashes the
                                                                 model first
    indexes the rungs form that it never touched:  gen[h], nx[h], regs[r]
    the R5 battery's own memory-safety failure (M3-nil-test):    unrepresentable
    ```

    ⚠⚠ **The CONCLUSION was true — the sanitisers really are silent — and the
    EVIDENCE CLAIM was false.** That combination is what makes this class hard to
    see: nothing downstream is wrong, so nothing downstream complains.

    > ⚠⚠⚠ **THE RULE: whatever a model DERIVES rather than DECLARES owes an arm
    > that SHOWS IT FIRING. A predicate written over the model's own
    > representation cannot see anything that representation cannot express, and
    > "it never fires" is indistinguishable from "it cannot fire" from outside.**
    > ✅ **DECLARING IS HONEST. A derivation that cannot fire is not.**

    ✅ **The tree contains the exemplar, and it is `p04`** — measured across all
    28 patterns (`.temp/mgr150/audit_derived_checks.py`): six declare `fires` on
    no input; **four (`p01`, `p08`, `p22`, `p47`) `return "clean"` outright,
    which is an honest declaration**; **two derive and never fire, `p04` and
    `p32`**; the other 22 derive and fire. **`p04` is not a defect**: it names
    its predicate, gives the **arithmetic** reason it is always false (*"that is
    arithmetic and not luck"* — every index is `head` or `tail`, every update is
    `(x + 1) % RING_CAP`), and says the `"clean"` derivation **is the headline
    rather than a gap**. ⚠ **`p04`'s predicate is false by a fact about the
    PROGRAM; `p32`'s was false by a fact about the MODEL. Only the second is a
    defect — and the two are indistinguishable from outside WITHOUT A MUST-FIRE
    ARM.**

    ✅ **What the repair looks like** (`p32`'s, and it is the shape to copy):
    `touch(name, i, limit)` became a check about a **VALUE** — the caller hands
    it the integer the rung would form and the extent of the array — so
    **nothing in it knows how the simulation stores a handle**; the sentinel
    `NIL = 255` became representable; and `detector_selftest()` runs **four
    cells, two per guard** — silent with the guard present, **fires** with it
    deleted — from `selfcheck()`, which the gate runs once per input on **every**
    invocation. The same 20 000-window sweep now fires **19 622** times with
    `h == NIL` deleted and **0** with both guards present.

    ⚠ **AND THE ARM OWES THE SAME TEST AS THE THING IT REPAIRS.**
    ✅ Manager-verified adversarially (`.temp/mgr151/`): four mutations planted
    into a copy — `touch` neutered, `touch` always raising, the upper bound
    dropped, the predicate made constant-`True` — and **all four make the gate
    FAIL**, because `check.py:2387` calls `sb(m.selfcheck)` and `sb` propagates.
    ⚠ **But three of the four fail by CRASHING inside the simulation rather than
    returning the designed message, so the failure is loud and the DIAGNOSTIC is
    lost.** **Next time, wrap the mutation run so an exception becomes the
    designed problem string** — a crash and a firing are different failure modes
    and only one of them says what happened.


20. ⚠⚠ **`measure.py` HASHES `measurement_sources` BEFORE THE MEASUREMENT LOOP,
    NOT AFTER — SO EDITING A MEASUREMENT-HASHED FILE MID-RUN COSTS THE WHOLE
    RUN.** `harness/measure.py:450` calls `provenance(pdir, indir)` and builds
    `source_sha256` **above** the cell loop.

    **The consequence, and it is not the obvious one:** the record that lands
    carries the hashes of the sources **as they were when the run STARTED**,
    while the cells were measured against whatever was on disk **as each one
    ran**. If the file changed in between, `--check-stale` compares the *new*
    disk against the *old* recorded hash and correctly says **STALE** — so
    nothing false ships. ⚠ **But the run is wasted, and a long one.**

    ✅ **`TASK_150` paid it: two full `p28` measure runs for one edit**, and
    reported it rather than absorbing it. ⚠ **The temptation is real** — the
    natural workflow is *measure, read the record, fix the comment the record
    made you notice, measure again* — **and the fix is free: make every
    measurement-hashed edit BEFORE the run, and treat the run as a barrier.**
    ⚠ **Same shape as `TASK_139`'s cost** (control JSONs generated before the
    sources were final) **and it is the mirror image**: there the artefact was
    generated too EARLY, here the source was edited too LATE.


21. ⚠⚠⚠ **A RE-GATE IS NOT VALUE-FREE, AND `--check-stale` STRUCTURALLY CANNOT
    SEE IT.** `TASK_151`, ✅ **manager-re-verified independently against `HEAD`.**

    `marginal_ir_per_call` is a **callgrind measurement taken INSIDE the gate**,
    so a gate run re-draws it. Re-gating all 29 patterns on an **otherwise
    unchanged tree**:

    ```
    marginal_ir_per_call cells compared   2772
    cells that MOVED                       673   across 18 patterns
    max |delta| 7.00   mean 0.916   cells >= the published 16.00 band: 0
    p01:16 p03:62 p04:14 p05:32 p06:32 p07:32 p08:85 p09:32 p10:32
    p12:48 p13:48 p14:32 p16:32 p17:32 p18:32 p19:32 p23:32 p27:48
    ```

    ✅ **`--check-stale` said `0 STALE` and was RIGHT** — it hashes **sources**,
    not **values**, and no source moved. **The two properties are different and
    only one of them is checked.**

    > ⚠⚠ **THE RULE: a gate record holds two KINDS of leaf — DERIVED FACTS about
    > committed bytes (hashes, `md5_fn`, identity, obligation counts, verdicts),
    > which are reproducible, and MEASUREMENTS taken during the run, which are
    > DRAWS. `--check-stale` covers the first kind only.** **Before quoting a
    > gate-record number, ask which kind it is.**

    ⚠ **SCOPE, AND DO NOT OVER-ATTRIBUTE IT** — this is the error the manager
    made one task earlier. `results/synthesis.md`'s `‡` note describes an
    environment-phase mechanism **for `p03` and `p04`**, bistable with a 32-byte
    period. **The movement measured here is WIDER — 18 patterns — but whether it
    is the SAME mechanism is NOT established by this measurement.** *"18 patterns
    move"* is the finding; *"18 patterns are `‡`"* is not.
    ✅ **What is safe either way: nothing reached the published `≥16.00` band**,
    so no headline figure is in question.

22. ⚠⚠ **A SECOND MECHANISM FOR *"a number grepped out of a log is not a number
    read out of a record"*, AND IT IS NOT A COUNTING BUG.** `TASK_151`,
    self-disclosed by the engineer.

    The known instance is `grep -c BLOCKED == 2N + 1` — a **substring** matching
    the verdict string `PASS-WITH-BLOCKED-ROWS`. The new one is **ALTERNATION
    ORDER IN THE READER**: a status grep spelled roughly
    `grep -oE 'PASS|FAIL|PASS-WITH-BLOCKED-ROWS'` reports `p01` as **`PASS`**,
    because the regex engine takes the **first alternative that matches at the
    leftmost position** and never tries the longer one.

    ⚠ **So the reader can be wrong even when it is not counting**, and the two
    mechanisms need different fixes: the first wants a record read, the second
    wants the longest alternative first — or an anchor. ✅ **Both are cured by
    the same discipline: READ THE VERDICT OUT OF `results/gate/*.json`.**

23. ⚠⚠⚠ **`marginal_ir_per_call` IS A WHOLE-PROGRAM SLOPE, SO THE R4/R5 PAIR HAS
    A NON-ZERO NULL — AND THREE PUBLISHED NUMBERS SIT BELOW THEIR OWN PATTERN'S.**
    Found by `TASK_157`'s engineer on `p25`, extended tree-wide by the manager,
    **and the extension was corrected twice by `TASK_158` before it was right.**

    The slope is `Ir@N − Ir@N/2` over the call difference — **deliberately
    symbol-independent**, so it works in `whole` mode and at `-O0` where a
    rung's work lives in `core::iter`. The consequence is that it includes
    everything the kernel calls. `identity` forces R4's and R5's kernels to
    agree, so **their difference is a measured null control**, and it is not
    zero:

    ⚠⚠⚠ **AND THE TABLE BELOW WAS WRONG A FOURTH TIME, IN THE SAME SHAPE AS THE
    FIRST THREE — IT MAXED OVER *INPUT*.** Found by `TASK_164`'s engineer,
    **manager-re-derived independently** from `results/gate/p*.json`. The rule
    three paragraphs down says *"do not max it over mode, over level, **or over
    input**"*, and the table under it had **three axes** and printed one number
    per `(pattern, level, mode)`. ✅ **Every figure it printed is RIGHT and is
    the worst input, which is the right one for the argument** — but the axis
    was missing, so the table is replaced with the four-axis form:

    ```
    verus - unsafe, `marginal_ir_per_call`, per (level, mode, INPUT) cell
                O0/iso            O3/iso           O0/whole          O3/whole
             small    large    small    large    small    large    small    large
    p25       0.00  +269.52    0.00  +269.52    0.00  +269.52    0.00  +269.52
    p28    +281.28 +1732.73    0.00    +1.01 +281.28 +1732.73  +46.02  +211.87
    p29    +113.76  +425.80    0.00    -0.02 +113.76  +425.80 +101.77  +465.55
    p42       0.00   -31.00    0.00   -31.00    0.00   -31.00   -2.00   -33.00
    p11       0.00     0.00   -1.00    -1.00    0.00     0.00 -494.00  -166.00
      p06/p14/p17/p18/p13/p35/p38/p34  <= 1.01 isolated, 14..36 at O3/whole

    At -O3 ISOLATED -- the cell the corrections are published in -- only p25 and
    p42 reach 16.00, and FIVE patterns clear 2.00:
      p25 269.52 . p42 31.00 . p04 6.00 . p03 6.00 . p02 2.00
    ```

    ⚠⚠ **THE INPUT AXIS IS NOT COSMETIC — ON THREE OF THE FIVE ROWS ONE INPUT IS
    EXACTLY `0.00`.** `p25`'s `small.bin` null is `0.00` in **all four** cells,
    so *"`p25`'s null is 269.52"* is a `large.bin` statement;
    `p28`'s `O0/iso` is `+281.28` on `small` against `+1732.73` on `large`; and
    ⚠ **`p11`'s `-494.00` is the `SMALL` cell, not the large one** (`large` is
    `-166.00`), which is the one place the old table's implied input was also
    the wrong one. **State the input with the cell, always.**

    ⚠⚠⚠ **AND THIS PARAGRAPH WAS ITSELF WRONG WHEN IT LANDED — THE FIFTH ERROR
    IN THIS ENTRY'S LINEAGE AND THE FIRST TO CONTRADICT ITS OWN TABLE.**
    (`TASK_165` MAJOR 2.) It read *"`p25`'s **and `p42`'s** `small.bin` nulls
    are `0.00` in all four cells"*. **`p42`'s `-O3/whole/small` is `-2.00`**
    (`unsafe` 1444 against `verus` 1442) — **and the four-axis table EIGHT LINES
    ABOVE ALREADY PRINTS `-2.00` IN THAT CELL.** ⚠⚠ **The manager wrote a
    summary sentence that contradicts the table directly above it, and marked it
    `✅ manager-re-derived` in `RECAP` finding 63(c).** ⚠ **The mechanism is
    `PROTOCOL` rule 13 operating INSIDE one entry: the table was derived and the
    prose beside it was generalised from three rows to four.** ✅ **A summary of
    a table you have just written is not evidence — re-read the table.**

    ✅ **Tree-wide at `-O3 isolated`, 66 `(pattern, input)` cells over 33
    patterns:** `|null| >= 2.00` in **8**, `1.00 <= |null| < 2.00` in **35** (34
    of them exactly `-1.00`), `|null| < 1.00` in **23**. At `-O0 isolated`,
    `|null| >= 2.00` in **10 of 66**. ⚠ At `-O3 whole`, 37 of 66 clear 2.00 and
    15 clear 20.00 — **and none of that is a defect**, because `check_identity`
    compares `isolated` digests only and nothing pins the `whole` cells equal.

    ⚠⚠⚠ **THIS TABLE WAS WRONG TWICE AND THE SHAPE OF BOTH ERRORS IS THE SAME:
    A MAX TAKEN ACROSS A DIMENSION THAT MATTERS.** The manager's first version
    maxed over `isolated` AND `whole` and reported *"ten patterns at >= 20"*;
    `TASK_158` removed `whole` and the manager published the result as
    *"-O3 isolated"* when it was still **maxed over BOTH LEVELS** -- so
    `p28 1732.73` and `p29 425.80`, which are `-O0` cells, were printed under an
    `-O3` heading, and *"four patterns"* was `-O0`'s count. `TASK_159` removed
    the level. ⚠ **Three passes, each removing one confound and leaving the
    next.** ✅ **THE RULE: a null is a property of a CELL. Do not max it over
    mode, over level, or over input -- print the cell.**

    ✅ **THE FINDING ITSELF IS UNTOUCHED BY BOTH CORRECTIONS, and that was
    checked rather than assumed**: at `-O3 isolated` `p25`'s null is still
    `269.52`, `p42`'s still `31.00`, `p02`'s still `2.00`.

    ✅ **The mechanism is CLOSED over every function** (pads 0 and 16 identical):
    kernels `0.00`, `main` `0.00`, and **six glibc malloc-internal symbols
    accounting for 100.0%**. On `p25` the two kernels cost *exactly* `9104.17`
    (`-O0`) and `4152.71` (`-O3`) while the slope differs by `+269.52`.

    ⚠⚠ **THE MODE MATTERS AND SO DOES THE LEVEL — see the table's own note.**
    Maxing over cells including `whole` gave *"ten patterns at ≥ 20"*; in
    `-O3 isolated` **eight of that top ten are negligible (`|Δ| ≤ 1.01`)**.
    ⚠⚠⚠ **AND `whole` IS NOT A NULL AT ALL: `check_identity`
    compares `isolated` digests only, and at `p11`'s
    `O3/whole` **`small.bin`** cell — the one the `−494.00` comes from — there
    is NO `kernel` symbol, the difference is `unsafe::main` vs `verus::main`,
    and the static traces are genuinely 751 against 747 non-pad
    instructions.** ⚠ **A null control is only a null in the MODE ITS IDENTITY
    PIN COVERS. Never max a null across modes.**
    ⚠ **This sentence carried `check.py:3303` until `TASK_164`, by which time
    the line was `:3313`** — ordinary citation rot, and
    `.memory/02-bench-rules.md`'s rule is *name the FUNCTION and give NO LINE
    NUMBER AT ALL*, because a function name cannot decay. **Fixed by deleting
    the number, not by updating it.**

    ⚠⚠⚠ **THREE PUBLISHED NUMBERS ARE BELOW THEIR OWN PATTERN'S NULL**:
    `p25 large gcc-clang` `+19.42`, which the published calibration places in
    the **`≥ 16.00` band labelled *"every one is real"***, against a null of
    `+269.52` — **13.9× larger**; `p42 large gcc-clang` `+5.00` against
    `−31.00`; `p02` `+2.00` against `−2.00`. ⚠ **And `results/synthesis.md`'s
    first calibration claim was ALREADY false independently of `p25`**: it lists
    seven rows including `p42 −31.00`, asserts *"every one is in the
    `2.00 … 16.00` band"* when `p42` is `≥ 16` and printed **bold**, then
    resolves *"all six"*.

    ✅ **THE RULE: for a cross-RUNG comparison use `kernel_exclusive_ir`; use
    `marginal_ir_per_call` for anti-collapse, which is what it was built for.
    And on any pattern whose kernel calls out of itself, compare a correction
    against that pattern's OWN `R5 − R4` null before quoting a band.**
    ⚠ **The repair is `synthesis/`-only and costs NO re-gate: refuse to promote
    a correction to the CONFIDENT band when it is below its own pattern's null.**

    ⚠ **NOT A NEW FACT, and the manager cited the wrong precedent for it.**
    `check.py:2805`, `synthesize.py:27–33` and `CALLEE_NOTE` all document the
    whole-program reading. `RECAP`'s *"the R4/R5 pair is not a null control …
    a source-path-length artefact"* is the **`ns`** finding — a different claim
    about wall clock. **What is new is the magnitude, the mode split, and the
    three affected numbers.**

## ⚠ A number GREPPED OUT OF A LOG is not a number READ OUT OF A RECORD

**`TASK_127`, swept at `TASK_132`.** **The gate writes structured JSON and also
prints a log. Two published numbers came from the log and were wrong.**

```
grep -c BLOCKED  matches the VERDICT STRING `PASS-WITH-BLOCKED-ROWS`
decoder:  grep -c BLOCKED == 2N + 1      (N = real blocked rows)
          ✅ validated 130/130 against the records over 130 sweep logs
```

✅ **The sweep is bounded and it came out well: 29 transcript-greps, and ONLY the
`blocked` family is defective. Grepped `verdict` and grepped FAIL-count agree
with the record `130/130`.** ⚠ **534 source-greps are a different class and were
NOT swept — stated, not silently capped.** ⚠ **So the rule is *READ THE RECORD*,
not *never grep*.** ⚠⚠ **The defect ORIGINATES AT `TASK_121`, four tasks before
the finding that names it; `TASK_125` was merely the first to PUBLISH from it.**

⚠⚠ **AND THE CORRECTION TO THIS RULE WAS ITSELF MADE BY OVER-GENERALISING, WHICH
IS THE PART WORTH REMEMBERING.** **The manager wrote *"EVERY `p42 saw 2` / `p42
saw 3` / `p22 shows one` is a grep artefact."* **`p42 saw 2` WAS A
MEASUREMENT** — `.temp/t107/gate-p42-rerun.log` carries two genuinely distinct
blocked rows (`adversarial-wincap.bin` and `large.bin`, both real 180 s Miri
timeouts) and that sweep used `tail -1`, not `grep -c`. ⚠ **Two true instances
were generalised to a universal, and the universal destroyed the support for the
sentence beside it.**

✅ **THE RULE: read `blocked` out of `results/gate/*.json`. If you must grep a
log, VALIDATE THE DECODER against the records first — it is one pass and it is
what turned this from a suspicion into a number.**

**The reflex, and it is one question:** ⚠⚠ **before believing a check, ask what
would make it FAIL — and then make that happen.** Every entry above passes that
question and none of them survived it. **A control with no demonstrated failing
arm is not evidence.** ⚠ **Entry 9 adds a second question for any arm you build
to EXPLAIN a movement: *would this same arm show the column moving WITHOUT the
mechanism?*** ⚠ **Entry 10 adds a third, and it is the cheapest of the three:
*were these numbers produced by the code that is committed?* — answered by
regenerating every arm from a `REBUILD.sh` before you write the report.**
⚠⚠ **Entry 11 adds a fourth that none of the others reaches: *does this check
WRITE anything the thing it checks READS?* — and its corollary, *is my detector
for that an allow-list or a hand-written deny-list?***

⚠ **Entries 5, 6 and 7 all landed within three tasks of each other**, which says
the reflex is not yet habitual. ✅ **The counter-example worth copying is
`TASK_103`, which gave EVERY probe an arm that must fire and reported each one
firing** — `+17` predicted and measured on an env-length probe, a `CONTROL-plain`
route that must be scanned, a `--selfdiff` over 24 179 leaves returning 0, and a
pad0-vs-pad0 scan over 288 triples returning 0 movers.

## ⚠ An allocation counter PERTURBS the measured cell; the LSan hook does not

**TASK_100, PROVISIONAL.** Measured in the real C config (`-O3 -DSLB_ISOLATED`,
`common/driver.c` + p01's `kernel.c`):

```
base                                     257362037 / 209367011
__lsan_default_options "use_stacks=0"    257362037 / 209367011   identical
-Wl,--wrap=malloc,free,calloc,realloc    257364247 / 209369261   +2210 / +2250
```

⚠ **So a `--wrap` allocation counter is HARM-PROBE-ONLY and must never ride in a
measured cell.** The `__lsan_default_options` hook is `Ir`-neutral **to the
instruction** (kernel disassembly identical modulo one trailing alignment
`nopl`), blinds no sanitizer (six cells byte-identical), and false-positives on
none of p01's eight inputs. ⚠ **Its one cost: a pattern legitimately holding an
allocation on the stack at exit would false-positive. Validated on one pattern.**

## ⚠ A `p13` gate re-run REORDERS its `c-clang` adversarial list

**TASK_103, reviewed.** Between two `check.py` runs on an identical tree, four of
`p13`'s `c-clang` adversarial entries change **list index without changing
value**. **A naive JSON leaf-diff therefore overstates the change by four
leaves**, which is exactly what happened once: a sweep reported *"95 adversarial
… p13 8"* where the truth is **91 moved + 2 added + 2 removed** (the arithmetic
stayed internally consistent, `95+40+24 = 159 = 155+4`, so nothing downstream was
wrong). ⚠ **When diffing gate records, compare adversarial entries as a SET keyed
by input name, not by position.**

## ⚠⚠ THREE MUTUALLY INCONSISTENT "EXACT" LAWS FROM ONE PATTERN — THE RESIDUE-CLASS TRAP, THIRD INSTANCE AND THE SHARPEST

**TASK_106, PROVISIONAL (unreviewed).** `p23` produced **three** closed forms,
each with **zero in-sample residual**, each wrong outside the band it was fitted
on:

```
                                            max |error|, Ir/call
form                                    K       M       N       X   small/large
242 + 2dn + 2sw - 3rounds  (band K)   0.00   32.00  480.00  121.00   152.00
30.25*recs + 2dn + 2sw - 3rounds      0.00   32.00    4.00   30.25    31.00
2 + 30*recs + 2dn + 2sw - 3rounds + t 0.00    0.00    0.00    0.00     0.00
```

⚠⚠ **THE BAND-K FORM MISPREDICTS THE TWO SHIPPED MATRIX INPUTS BY UP TO 152.00
`Ir`/CALL** — it was the headline law, and its holdout inside band K was
`0.0000`. **A within-band holdout cannot detect a term the band holds constant.**

**The law that survives all 109 shipped points:**

> **`R3 − R4 = 2 + 30·recs + 2·dn + 2·sw − 3·rounds + Σ_records τ(m mod 4)`**,
> with **`τ = {0→0, 1→2, 2→3, 3→4}`** — **max |residual| `0.0000` over all 109
> points**, response range `41.75 … 956.40`. `-O3 isolated`, kernel-exclusive
> `Ir`, debug-assertions **off**.
> **Holdout: fit all eight coefficients on bands M+N only (71 points) → predict
> the 38 nobody fitted → max |error| `0.0000`.** Shuffled training: `6050.96`.

⚠⚠ **WHY NEITHER BAND COULD SEE `τ`, AND THIS IS THE TRANSFERABLE PART.**
Band K sits at `m = 32` and band N at `m = 16` — **both `≡ 0 (mod 4)`, so `τ` is
identically zero across each.** Band M sweeps `m` but `controls/sweep_fit.py`
reads it at **`want_m = [2, 4, 8, 16, 24, 32, 40, 48]`** — **seven of those eight
are multiples of four**, leaving `τ` with **one** non-zero sample. Its residual
there is exactly `0 / 16 / 24 / 32` as `m mod 4` runs `0 / 1 / 2 / 3`.

⚠ **Band N re-fits to a DIFFERENT exact law** (`2.00 + 5.75·dn + 2·sw −
3·rounds`, R² `1.0000`) purely because `m = 16` makes `dn ≡ 8·recs` — **two
regressors collinear inside the band and separable only outside it.**

**The rule, stated generally, third time of asking** (p38's additivity failure
was the first, p46's underdetermined two-band fit the second):

> ⚠⚠ **A band that holds a regressor fixed cannot give the coefficient of
> anything collinear with it, AND A WITHIN-BAND HOLDOUT WILL NOT TELL YOU.**
> **Check the residue class of every parameter your bands hold constant, and fit
> on one band while predicting another.** ⚠ **`p46` showed a two-band fit can be
> UNDERDETERMINED with no in-sample residual; `p23` shows a one-band fit can be
> CONFIDENTLY WRONG with a perfect in-band holdout.** The only test that caught
> either is **out-of-band prediction.**

✅ **Also landed, and it is what makes the axis clean:** `up + dn == mbytes`
**exactly at all 109 points** (band K's `up + dn = 256.00` generalised) — total
cursor work is constant and only its **split** moves. ⚠⚠ ~~**The swap-count
confound is refuted and reproduced:** endpoints `sw = 7.63` vs `7.75` while the
tax differs `3.11×`; `dn` alone R² `0.9869`, **`sw` alone R² `0.0132`.**~~
**RETRACTED AT `TASK_117`, MANAGER-RE-MEASURED — AND IT IS A METHOD FINDING, NOT
A `p23` FINDING.** Those R² values are real **for the shipped spelling pair**.
**Against the cheapest IN-CONTRACT safe rung the two regressors SWAP: `dn` →
`0.0001`, `sw` → `0.9930`**, and the headline ratio falls `3.11× → 1.315×`.

⚠⚠ **THE TRANSFERABLE RULE, and it is new: A SPELLING DIFFERENCE CAN BE
COLLINEAR WITH THE AXIS YOU ARE MEASURING, AND THEN IT FORGES BOTH THE
MAGNITUDE AND THE MECHANISM.** `p23`'s spelling term is **exactly
`2·dn − 2·recs`** — it *is* a function of the swept variable — so it inflated
one endpoint, left the other untouched, and made `dn` look like the cause.
⚠ **A control that varies the axis while holding the spelling fixed cannot see
this; you have to vary the SPELLING at each point of the axis.** ⚠ **This is
strictly worse than the known "an endpoint is what someone thought to write"
trap, because here the spelling error is not a constant offset and does not
cancel in a ratio.** ✅ **Check for it the cheap way: regress the spelling term
itself on the swept variable. If R² is high, no number on that axis is
publishable until the spelling is held at its in-contract floor.**

⚠ **`τ`'s MECHANISM IS NOT ESTABLISHED** — per-record, periodic, values
`0/2/3/4`, not disassembled. **Cite it; do not explain it.**

## ⚠⚠ THE ENVIRONMENT-LENGTH PIN IS NECESSARY AND NOT SUFFICIENT — CONTENT MOVES `Ir` TOO

**TASK_107, PROVISIONAL.** `TASK_103` decided to record
`len(/proc/self/environ)` in the gate record and explicitly left
**length-versus-content** open. **It is now measured, and content matters more
than the term the pin was built for:**

```
child-measured env block = 3332 bytes in BOTH arms
  GLIBC_TUNABLES=...x86_rep_stosb_threshold=64   ->  3545.00 Ir/call
  same length of filler                          ->  3059.00 Ir/call
                                                     +486.00, at IDENTICAL length
```

⚠⚠ **That is 69× the `±7` the pin was designed to diagnose.** A length-only pin
would have read *"same draw"* across a 486-instruction difference.

✅ **The shipped field records BOTH**: `marginal_ir_env: {bytes, tuning_vars}`,
where `tuning_vars` captures the allocator/libc-tuning variables whose *content*
is known to change codegen paths. ~~⚠ **`tuning_vars`'s prefix set is derived from
ONE measurement and is not proved complete** — treat it as a growing list.~~

⚠⚠ **THE RULE THIS FIELD LICENSES IS FALSE, AND THE LOSSY TERM IS `bytes`, NOT
`tuning_vars` (`TASK_114`, and the manager's own suspicion pointed at the wrong
half).** The rule written beside the field is *same `bytes` and same
`tuning_vars` ⇒ the marginal must match exactly.* **Measured counterexample, at
byte-identical `bytes = 3520` and identical (empty) `tuning_vars`, varying only
the NUMBER of variables:**

```
3059.00, 3059.00, 3066.00, 3066.00      <- period 4 in the VARIABLE COUNT
```

⚠⚠ **MECHANISM, MEASURED NOT ARGUED: a 9-rung sweep at constant `bytes = 3680`
is period 4 in the variable count, which is the 32-byte stack-alignment period
divided by the 8 bytes of ONE `envp` POINTER SLOT.** **`_env_block` records
`len(/proc/self/environ)`, which is `NAME=VALUE\0` concatenated and contains NO
POINTER ARRAY AT ALL.**

⚠⚠⚠ **AND THIS FILE ALREADY CONTAINED THE ARITHMETIC. The 87-byte decomposition
above is `8 (envp pointer slot) + 13 + 1 + 64 + 1`, and this file calls that
leading `8` "the part the manager forgot entirely". THE PIN REPEATS THE EXACT
ERROR IT WAS WRITTEN TO PREVENT.** ✅ **Fix is one integer: record `nvars`, or
record `bytes + 8·nvars`.**

✅ **CLEAN NEGATIVES that redirect the search — `tuning_vars` is FINE.** A pure
**permutation** of the environment does not move it; neither does value content
outside the prefix set (`LANG`, `TZ`). ⚠ **So the growing-list worry was
misplaced and the manager sent a reviewer at the wrong term.** ⚠ **`argv` DOES
move it ±7, and the "valid within one clone location" domain that makes the pin
sound exists ONLY in `.tasks/TASK_107_REPORT.md` — 0 hits in `check.py`, in
`.memory/`, and in the record itself.** **A pin whose domain is not written down
where the pin is read is not a pin.**

✅ **The pin worked on its first live outing:** re-running the chain from an
interactive shell (`bytes: 3280`) instead of the sweep's (`3269`) — **an 11-byte
difference, exactly the `OLDPWD` term** — moved p03's published row, **and the
new field is what says so.** Before it existed, that move was indistinguishable
from a real change.

---

## ⚠⚠ A WHOLE-PROGRAM TOTAL IS NOT A MEASUREMENT BELOW ~100 `Ir`

⚠⚠ **PROVISIONAL AND UNREVIEWED — `TASK_120`'s own result, produced while
reviewing finding 40. `TASK_122` §A/§B is its review. Rule 9: this is landed as a
conclusion with its mechanism OPEN, and it must not be treated as settled.**

**Measured: whole-program `Ir` totals moved by `60` between `--cache-sim=yes` and
plain `callgrind` ON THE SAME BINARY AND THE SAME ARGV.** ✅ **Marginal
(differenced) numbers did not move AT ALL.**

> ⚠ **So any published figure below ~100 `Ir` taken from a WHOLE-PROGRAM TOTAL
> rather than from a DIFFERENCE is at the noise floor.**

**Known instances**: `p40`'s `21`, `p40`'s `193`, `p43`'s `+3.00`.
✅ **`p40`'s `21` SURVIVES ANYWAY**, because `TASK_120` re-derived it as a
difference against a **zero-iteration control** that makes the two kernels
byte-equal.

⚠⚠ **BUT THE ZERO-ITERATION CONTROL IS NOT UNIVERSAL, AND THIS BLOCK RECOMMENDED
IT AS IF IT WERE — CORRECTED AT `TASK_124`, ONE TASK AFTER IT WAS WRITTEN.**
**It is WRONG for a kernel that ALLOCATES**, because `n = 0` never pays glibc's
arena setup and prints a shorter line. **Measured error:**

```
C-gcc   +0.82   C-clang  +1.51   Rust  +0.42     Ir/call
```

✅ **`p40`'s `21` is unaffected — a different construction, and its two arms are
byte-equal at zero iterations.** ⚠ **The rule is therefore: subtract a
zero-iteration control ONLY when you have checked that the arms are byte-equal
there. If the kernel allocates or prints a variable-length line, USE A
PERTURBATION CONTRAST INSTEAD** — hold everything fixed, perturb the one term you
are pricing, and ask whose behaviour moves. ⚠⚠ **That is also the shape that
killed `CVE-2021-23017`: six of eight arms had to change and did, and the two
`Vec::push` arms did not** (RECAP finding 42).

⚠⚠ **THE `println!` TRAP, and it is the reason `p40`'s `+193` was 60% artefact:
formatting a kernel NAME six characters longer cost `115 Ir` with the kernels
NEVER CALLED.** ⚠ **A harness that prints which variant it is running has put the
variant's NAME LENGTH on the measured axis.** **Give every variant a name of the
same length, or measure against a zero-iteration control.**

⚠⚠ ~~**AND THE BOX IS NOT AS STABLE AS THIS FILE ASSUMES.**~~ **STRUCK AT
`TASK_122`, WHICH MEASURED IT OUT. IT IS NOT THE BOX.** `p40`'s absolute total
moved **`360,114,293` → `378,984,676`** (18.9 M, ~5.2%). ✅ **Not the BUILD**
(identical flags, binary bit-reproducible across paths); ✅ **not the BOX**
(`dpkg` untouched since Aug 15; `libc`/`valgrind`/`rustc` binaries all Aug 15,
**all predating `TASK_086`**); ✅ **not the ENVIRONMENT** (measured at
**61,877 `Ir`**, 300× too small — ⚠ **though four orders ABOVE the ±7 recorded
above, because that ±7 is a MARGINAL where the term cancels**).
✅ **MEASURED MECHANISM: deleting ONE SETUP ARRAY (`tagged`) drops the total by
`18,874,783` against a drift of `18,870,383` — `0.023%`.**
⚠ **SUFFICIENCY, NOT ACTUALITY** — and ⚠⚠ **it can never be raised to actuality,
which is itself the finding: `.temp/` IS GITIGNORED, SO THE `p40`-ERA `cost.rs`
IS GONE, and *"byte-identical pipeline"* was checked against TODAY'S copy.**

> ✅ **THE RULE THAT REPLACES IT: WHOLE-PROGRAM TOTALS FROM `.temp/` PROBES ARE
> UNREPRODUCIBLE IN PRINCIPLE.**

✅ **BLAST RADIUS IS ONE FIGURE.** **The drift sits in a term COMMON TO BOTH ARMS
of every published difference, so it hits DENOMINATORS and not DIFFERENCES** —
`5.8e-8` is the whole list and it is already corrected.
⚠ **Separately and NARROWLY, two checked rungs (`k20_checked`, `k21_checked`)
each re-measure exactly `−4 Ir` while their unchecked twins are EXACT, and
`k39`/`k41`/`k43` all reproduce exactly** — so the `−4` is **not** the 18.9 M
drift. ✅ **The `.rodata`-alignment hypothesis for the `−4` was RUN AND KILLED**
(`--remap-path-prefix` to the old build path gives identical numbers).
⚠ **Two open instrument questions, both narrow, neither guessed at. Do not
publish a mechanism for either without a measurement** — this axis is where
`MIRIFLAGS` produced two confident wrong mechanisms.

---

## ⚠⚠ A GATE RECORD IS NOT BYTE-REPRODUCIBLE — 17 OF 26 MOVE ON A RE-RUN

**`TASK_125`, as a by-product of running the sweep twice on the same tree.**
⚠ **Engineer work, not yet reviewed (rule 9). The CONCLUSION is cheap to
re-derive: run `check.py` twice and diff.**

**Everything that moves is RUN-SCOPED, and the `source_sha256` is IDENTICAL
throughout — so this is not staleness and `--check-stale` is right to say
nothing:**

| field | why it moves |
|---|---|
| sanitizer `diagnostic` strings | PID and ASLR addresses |
| `miri.runs[].seconds` | wall clock (⚠ landed deliberately at `TASK_119` to make the two-state Miri slowdown VISIBLE — see `00-environment.md`) |
| order of equal-behaviour cell groups in `adversarial` | grouping is unordered |
| ⚠⚠ `notes`: *"opt/mode variants of this rung disagree (**N** distinct behaviours)"* | **N MOVED `3→4` ON `p03` AND `3→2` ON `p23`** |

⚠⚠⚠ **THE LAST ROW IS THE ONE WITH PROSE CONSEQUENCES, AND ITS CAUSE IS THE
POINT: `N` MOVES BECAUSE THOSE CELLS READ UNINITIALISED MEMORY AND PRINT
GARBAGE.** ✅ **That is the pattern behaving as designed — it is what those
adversarial inputs EXIST to demonstrate** — **but it means the count is a draw,
not a property.**

> ⚠ **DIFF GATE RECORDS MODULO THOSE FOUR FIELDS.** **A reviewer who reads a
> moved `notes` line as a regression is chasing UB, not a defect** — and will
> "fix" a pattern whose whole subject is that the UB is there.

⚠ **Do not quote an `N distinct behaviours` figure as a stable number.** ⚠ **And
note the shape: this is a COUNT that is a CACHED DERIVATION of a nondeterministic
run, which is the same class as the failure-class list's own rotting ordinal —
`a count is a cached derivation` keeps being the lesson.**
