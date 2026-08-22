# p47 — constant-time tag comparison: notes

Working notes and measurements. `spec.md` is the contract; `README.md` is the
summary. Everything below was run on this box (`.memory/00-environment.md`):
gcc 13.3.0, clang 22.1.6, rustc 1.97.1, glibc 2.39, valgrind 3.27.1,
Cascade Lake, `perf_event_paranoid = 3`.

**`slb-contract` sha256, as shipped:**

```
04f034f09a679ed3ce090f62f4ca0496a8e3ec92045dab2f379ec5d30d22c091
```

**It moved once, at TASK_065**, from
`1f0b4ba6a9611fc94d11a2d30b3f175cfceea0b3f05b75a6ad250c2fce516e1a` (the value
this line carried at `e6e86fc`, the commit that landed p47). **Two pins moved
and both are corrections of text that was already false when it was written**,
so no cell was admitted or excluded by the edit: `collapse.note` still described
the *pre-repair* denominator (§12, major 3) and `obligations_note` had the
`main` comparison **backwards** (§12, major 2). `git diff` on the block is
confined to those two string values; `controls/mkcontract.py` carries both, so
`python3 patterns/p47-ct-compare/controls/mkcontract.py --check` reproduces the
shipped block byte for byte.

⚠ **That last sentence is checked, not asserted, and checking it caught a
defect of my own during this very task.** I edited `mkcontract.py`'s
`obligations_note` after the run that produced the block, so for a while
`spec.md` carried a hash (`b8ec990a6c5d…`) that the committed generator would
not reproduce — the same "artefact and generator disagree" shape as §6a and
§15, introduced while fixing them. `--check` is a diff and it is one command;
**run it after every edit to the generator, not after the last one**:

```
python3 patterns/p47-ct-compare/controls/mkcontract.py --check \
  | diff - <(python3 -c "import re;print(re.search(r'\`\`\`slb-contract\n(.*?)\n\`\`\`',
      open('patterns/p47-ct-compare/spec.md').read(),re.S).group(1))")
```

reproduce with

```
python3 -c "import re,hashlib;t=open('patterns/p47-ct-compare/spec.md').read();\
print(hashlib.sha256(re.search(r'```slb-contract\\s*\\n(.*?)```',t,re.S).group(1).encode()).hexdigest())"
```

⚠ **This is NOT "as first written before any measurement", and §12 says why and
lists every pin that moved, with its direction.** Read §12 before quoting this
line.

---

## 0. §0 — the three probes the task asked for, run BEFORE anything was built

`.temp/p47/probe/` — `pr_rust.rs`, `pr_c.c`, `sweep.c`, `sweep.rs`, `risky.c`,
`inl.rs`. Standalone, no harness, so nothing in the pattern could have been
built around a wrong premise.

### 0a. Does R2's `a == b` on slices lower to an early exit? **YES**

`llvm-objdump -R` on the probe binary:

```
0000000000055138 R_X86_64_GLOB_DAT        bcmp
```

and `r2_eq`'s entire body is

```
cmpq %rcx,%rsi ; jne <ret 0> ; callq *GOT[bcmp] ; sete %al
```

The length test is inline; the byte comparison is one libc call. **The
manager's load-bearing claim holds.**

### 0b. Does R3's `fold` with `|` survive `-O3`? **YES — the feared collapse does not happen**

`a.iter().zip(b.iter()).fold(0u8, |acc,(x,y)| acc | (x^y))` at
`-C opt-level=3` vectorises to SSE2 `movdqu/movdqu/pxor/por` with no
data-dependent branch, and its `Ir` is **constant to the instruction** across
thirteen values of the first-mismatch position `k`. So

> *"constant-time code is not expressible in safe Rust at `-O3` without
> `black_box` or a crate"* — the stronger alternative the task file offered —
> **is FALSE on this toolchain.** The weaker, true statement is what p47 ships.

⚠ **But the accumulator TYPE is load-bearing.** The same algorithm with a `u64`
accumulator (`fold(0u64, |acc,(x,y)| acc | ((x^y) as u64))`) lowers to a
`movzwl / punpcklbw / punpcklwd / punpckldq` widening loop consuming **4 bytes
per iteration** instead of 32, because LLVM vectorises the zero-extension rather
than the xor. `spec.md` pins `fold(0u8` for that reason.

### 0c. Do R1 and R2 lower to the same libc routine? **YES under clang**

| rung | relocation on the probe binary |
|---|---|
| C, clang `-O3`, `memcmp(a,b,n) == 0` | `R_X86_64_JUMP_SLOT bcmp` |
| C, gcc `-O3`, same source | `R_X86_64_JUMP_SLOT memcmp` |
| Rust, `a == b` on `&[u8]` | `R_X86_64_GLOB_DAT bcmp` |

clang rewrites `memcmp(...) == 0` into `bcmp`. **So `c-clang` and `safe_naive`
enter one glibc routine**, and any difference between them is what the *caller*
does around the call — a library result, not a language one
(`.memory/03-measurement.md`, "name the routine"). The manager's third worry
lands and §4 separates the three factors.

### 0d. The Ir(k) probe, and the two ways `Ir` could have lied

`.temp/p47/probe/sweep.c` and `sweep.rs`, n = 256, 1000 calls, whole-program
callgrind totals. `k` is zero-padded in argv, because `atol` costs **6 Ir per
digit** and that term alone moved the count.

Rust, `-C opt-level=3`:

| k | `a==b` (bcmp) | `zip().fold(0u8,..)` | indexed `a[i]^b[i]` | `get_unchecked` | naive early exit |
|---:|---:|---:|---:|---:|---:|
| 000 | 395905 | 489905 | 489905 | 511905 | 380899 |
| 031 | 395905 | 489905 | 489905 | 511905 | 566899 |
| 032 | 402905 | 489905 | 489905 | 511905 | 572899 |
| 064 | 409905 | 489905 | 489905 | 511905 | 764899 |
| 255 | 441905 | 489905 | 489905 | 511905 | 1910899 |

**Hazard 1 (`rep`-strings, `.memory/03-measurement.md:411`) is EMPTY here.** The
`bcmp` step is +7 Ir per **32 bytes**, which is AVX2 granularity; a `repe cmpsb`
lowering would step per byte. And **no p47 cell contains a `rep` instruction at
all** — checked on all eight shipped kernels, §1.

**Hazard 2 (`div` priced at 1, `:434`) is empty too**: no p47 cell contains
`div` or `idiv`.

⚠ **And the manager's table is wrong about the shape.** It says `Ir` is
*"linear in `k`"* for the leaking rung. It is **a 32-byte staircase**, and above
128 bytes it is not even that — see §4.

### 0e. "Did the optimiser put the branch back?" — **NO**, 5 spellings × 2 C compilers × 5 opt levels × rustc, inlined and not

`.temp/p47/probe/risky.c` (or-accumulate, boolean flag, and-accumulate, match
count, wide-word or) at `-O1 -O2 -O3 -Os -Oz` on gcc 13.3.0 and clang 22.1.6;
`.temp/p47/probe/inl.rs` with the fold `#[inline(always)]`-inlined into a caller
that **branches on the result**, plus fixed-size `[u8;16]` and `[u8;32]`.

**Not one grew a data-dependent exit.** gcc's boolean-flag variant becomes
`cmovne`; clang's vectorises; the fixed-size Rust folds become
`pcmpeqb ; pmovmskb ; xorl ; cmoveq`.

⚠ A `ret`-count heuristic is NOT a valid detector — the `n == 0` early return
gives a second `ret` in every variant. The detectors are `Ir(k)` constancy (§4)
and reading the loop body (§1).

⚠ **A NEGATIVE CLAIM IS ONLY AS STRONG AS THE WIDEST SEARCH BEHIND IT, AND THE
WIDEST ONE IS NOT THIS ONE.** TASK_064_REVIEW ran a strictly larger search
against the same claim and could not break it either, so what p47 publishes is
the union rather than the delivery's own grid:

| search | this file (0e) | TASK_064_REVIEW A3 |
|---|---|---|
| spellings | 5 C | **7 C + 4 Rust**, incl. `__builtin_expect` in **three** placements and a branching caller with the callee `static inline` |
| opt levels | `-O1 -O2 -O3 -Os -Oz`, gcc + clang + rustc | `-O3` |
| link | — | **LTO** (`-flto`, `-C lto=fat`) |
| profile | — | **PGO trained 100% on mismatch-at-byte-0** |
| ISA | baseline | **AVX2** and **AVX-512** |
| binaries | 5 × 2 × 5 + rustc | **16** |

`Ir(k=0) − Ir(k=n−1) = 0` **exactly**, per function, in every one of them —
whole-program *and* per-function self-cost, n = 256, 400 reps, with callgrind
name-compression and `calls=` inclusive-cost handling done properly. **The
detector is not blind**: the same instrument on the same runs reports the
leaking Rust `a == b` at **+18 448 Ir**. On the AVX-512 builds a scripted check
across all five binaries × seven spellings — *does any
`test`/`or`/`ptest`/`pmovmskb`/`kortest` feed a conditional jump?* — returns
**0 hits in 33 of 33 functions**, and that half is **static only** for the
reason in §16. Optimisers here move *away* from branching: `vpternlogq`,
`cmovne`, `sete`, `pcmpeqb/pmovmskb/cmove`.

### 0f. §0's decisions

**(a) THE BUG CLASS — `.memory/06-catalogue.md`'s row is OVERTURNED.** It says
*"timing side channel — **compiler may reintroduce a branch**"*. The second half
is false on this toolchain (0e). p47's bug is **source-level**: `memcmp` and
`==` early-exit by definition and need no optimiser help. **The adversary is the
IDIOM, not the optimiser.** Fourth catalogue row overturned, third upheld.

**Rejected candidates, and why:**

1. *"R1h is the accumulate and the finding is that `-O3` breaks it."* Measured
   (0e): it does not break, at any opt level, in either language, inlined or
   not, at fixed or runtime length.
2. *"Constant-time SELECT (`cmov`) instead of compare."* A select's leak is a
   **branch-prediction** leak. Both spellings are branchless at `-O3`, so `Ir`
   is identical *by construction* and this box has no branch-miss counter for
   the perf row. `Ir` cannot see it. **The compare leaks in `Ir`; the pattern
   has to be the compare.**
3. *"Add a spatial bounds bug as well."* Ten of the eighteen existing patterns
   are bounds bugs. An eleventh here would confound the axis p47 exists for.
   p47's window guard is in **every** rung, R1 included.
4. *"`volatile` accumulate as R1h."* Measured 6.35× on the probe and **6.75× on
   the shipped kernel** (§8c) for zero security gain. It ships as the control
   `h_vol` and `spec.md` forbids it in the measured cells.

**(b) THE SWEEP.** Four structural parameters, **and the list is not claimed
closed**: `k` (first-mismatch position), `nmatch` (equal comparisons per
window), `tlen`, `ntag`. `k` and `nmatch` vary independently, so **additivity
extrapolation is available** — §5.

**(c) WHAT AN ADVERSARIAL ROW MEANS HERE**, which the task file said it did not
know: not a crash and not a wrong checksum, because **every rung agrees with
`model.py` on every input, always**. It is a **PAIR** of files — same seed, same
shape, same verdict sequence, different `k` — that print an **identical
checksum on all eight cells** and differ in instruction count. §6.

---

## 1. The shipped objects, read statically

`.memory/06-catalogue.md` hazard 2: *a text pin binds the SOURCE and not the
OBJECT.* Everything in this section is off the shipped binaries.

`harness/asm.py show`, `-O3 isolated`, kernel symbol:

| cell | insns | calls | vector ops | `rep` | `div` |
|---|---:|---:|---:|---:|---:|
| `c-gcc` | 89 | **1** | 0 | 0 | 0 |
| `c-clang` | 69 | **1** | 0 | 0 | 0 |
| `c-gcc-h` | 215 | 0 | 27 | 0 | 0 |
| `c-clang-h` | 176 | 0 | 32 | 0 | 0 |
| `safe_naive` | 203 | 11 | 0 | 0 | 0 |
| `safe_tuned` | 282 | 10 | 32 | 0 | 0 |
| `unsafe` | 174 | 0 | 32 | 0 | 0 |
| `verus` | 174 | 0 | 32 | 0 | 0 |

⚠ **THE "vector ops" COLUMN WAS WITHDRAWN AND RE-DERIVED AT TASK_065.** As
shipped it read 18 / 22 / 22 / 22 / 22 and it was **the one column of this table
that reproduced under no counting rule** — TASK_064_REVIEW minor 6 could not
get it, and neither could I on re-attempt: the whole-symbol count under
`controls/loops.py`'s own mnemonic-prefix list is 47 / 56 / 84 / 54 / 54, and
under an "is it an SSE/AVX mnemonic" reading 45 / 44 / 44 / 44 / 44. Only the
18 is traceable, to `loops.py`'s per-**loop-body** `vec=` figure for `c-gcc-h`'s
109-instruction second body, which is not what the column claims to be; the 22
matches nothing. **The rule is now one line of code and is printed beside the
numbers** — *an instruction counts as vector when one operand names an
`%xmm`/`%ymm`/`%zmm` register*, over the whole kernel symbol:

```
$ python3 patterns/p47-ct-compare/controls/loops.py --vecops
cell          insns  vector   by mnemonic
c-gcc            89       0   -
c-clang          69       0   -
c-gcc-h         215      27   movd:1 movdqa:5 movdqu:2 movq:3 por:7 psrldq:5 pxor:4
c-clang-h       176      32   movd:4 movdqa:4 movdqu:4 por:10 pshufd:2 psrld:2 psrlw:2 pxor:4
safe_naive      203       0   -
safe_tuned      282      32   movd:4 movdqa:4 movdqu:4 por:10 pshufd:2 psrld:2 psrlw:2 pxor:4
unsafe          174      32   movd:4 movdqa:4 movdqu:4 por:10 pshufd:2 psrld:2 psrlw:2 pxor:4
verus           174      32   movd:4 movdqa:4 movdqu:4 por:10 pshufd:2 psrld:2 psrlw:2 pxor:4
```

which agrees with the review's independent `xmm|ymm|zmm` count exactly. **A
mnemonic list is what went wrong** and a register-operand test is what replaces
it: `pshufd`, `psrld`, `psrlw` and `movdqa` are all outside `loops.py`'s prefix
list, so any count built on it under-reports whatever the next LLVM emits.
⚠ Note also the stronger fact the corrected column exposes: **hardened clang C,
safe Rust, unsafe Rust and the proved rung have the byte-identical vector
histogram**, not merely the same total — 32 instructions over the same eight
mnemonics in the same multiplicities. That is §1a's eleven-instruction result
holding over the whole symbol rather than only over the tag loop.

**The call targets, resolved by GOT relocation and `nm`** — not guessed:

| cell | calls from the kernel symbol |
|---|---|
| `c-gcc` | 1 × `memcmp` |
| `c-clang` | 1 × `bcmp` |
| `safe_naive` | 1 × **`bcmp`** + 2 × `core::slice::index::slice_index_fail` + 8 × `core::panicking::panic_bounds_check` |
| `safe_tuned` | 2 × `slice_index_fail` + 8 × `panic_bounds_check` |
| `unsafe`, `verus` | **none** |
| `c-gcc-h`, `c-clang-h` | none |

⚠ **R2 and R3 carry the IDENTICAL panic-path structure — 2 + 8 call sites
each — and R2's only extra call is the `bcmp`.** That is why `R2 − R3` is the
one pair in this pattern that differences the comparison idiom with the safety
term cancelled exactly, and it is why `spec.md` pins the two rungs to the same
addressing.

### 1a. The tag loops, `controls/loops.py`

The innermost loop with a `$0x10`/`$0x20` induction bump is the tag loop. **A
conditional branch inside it would be the reintroduced early exit.**

| cell | body | interior conditional branches | bytes/iter | Ir per compared byte |
|---|---:|---:|---:|---:|
| `c-gcc-h` | 7 | **0** | 16 | **0.437500** = 7/16 |
| `c-clang-h` | 11 | **0** | 32 | **0.343750** = 11/32 |
| `safe_tuned` | 11 | **0** | 32 | **0.343750** = 11/32 |
| `unsafe` / `verus` | 12 | **0** | 32 | **0.375000** = 12/32 |

Every rate is `body_len / K` off the listing, never a marginal
(`.tasks/TASK_026.md` §0 item 2), and each is confirmed to five decimals by the
`sweep-t*` band: the band-t step per +128 compared bytes is 56 / 44 / 44 / 48 Ir
respectively, i.e. exactly `128 × rate`.

**`safe_tuned` and `c-clang-h` emit the SAME ELEVEN INSTRUCTIONS** in the same
order — safe Rust's constant-time comparison loop *is* hardened clang C's:

```
movdqu -0x10(%r13,%rsi),%xmm2 ; movdqu (%r13,%rsi),%xmm3
movdqu -0x10(%r12,%rsi),%xmm4 ; pxor %xmm2,%xmm4 ; por %xmm4,%xmm1
movdqu (%r12,%rsi),%xmm2      ; pxor %xmm3,%xmm2 ; por %xmm2,%xmm0
addq $0x20,%rsi ; cmpq %rsi,%r15 ; jne
```

**`unsafe`'s twelfth instruction is a second induction variable** —
`addq $0x20,%r14` *and* `addq $0x20,%r11`, where R3 advances one shared index.
That is `.memory/01-ladder.md` finding 18's (p10's) mechanism reproduced on a
completely different kernel: *the safe iterator gives LLVM a simpler
induction-variable structure than explicit index arithmetic does, and it is a
codegen result rather than a safety result.*

**The leaking cells have no tag loop at all** in the kernel symbol — the
comparison is inside glibc — which is why every `Ir` figure in this file is
**whole-program** and never kernel-exclusive.

---

## 2. Verus: 12 verified, 0 errors, first run

```
$ ./verus_run.py patterns/p47-ct-compare/verus.rs
verification results:: 12 verified, 0 errors
```

No lemma, no `by (nonlinear_arith)` in the kernel, no `assume`, no
`assume_specification`. The kernel's proof is two loop invariants and three
ghost `assert`s, all unfoldings of the spec functions.

`12 = MATCH 1 + MISS 1 + xacc 1 + twalk 1 + kernel 3 + main 5`, every term
**measured**:

```
u32_at            0 verified   xacc     1 verified   twalk   1 verified
tag_fold          0 verified   kernel   3 verified   main    5 verified
buf_get_unchecked 0 verified   load_input 0          emit    0
```

⚠ **THIS PARAGRAPH SAID THE OPPOSITE UNTIL TASK_065, AND THE OPPOSITE WAS
FALSE ABOUT NINE PATTERNS.** As shipped it read *"`main` reports 5, not the 4
that p03, p05, p06, p07, p10, p11, p12, p14, p17 and p27 record"*. Measured:

```
$ grep -o 'main [0-9]' patterns/*/spec.md | sort | uniq -c
     17 main 5          <- p03 p04 p05 p06 p07 p08 p09 p10 p11 p12 p13 p14
                           p16 p17 p18 p27 p47
      1 main 4          <- p27, BEFORE TASK_065 corrected it
```

**`main` is 5 and it is the rule**: every pattern in this tree that records the
term records 5 (p01 and p02 record no term). p47 is not anomalous. The single
`4` was **p27's, and p27 was wrong** — provably from its own arithmetic, since
`TABCAP 1 + RECSZ 1 + SENT 1 + run 1 + rec_open 1 + rec_close 1 + rec_read 1 +
kernel 3 + main 4` sums to **14** against p27's pinned and separately measured
total of **15**, and `main 5` makes it exactly 15. Re-measured directly:

```
$ ./verus_run.py patterns/p27-handle-table/verus.rs --verify-function main --verify-root
verification results:: 5 verified, 0 errors (partial verification with `--verify-*`)
```

⚠ **And the "shared off-by-one note" is not about the value 4 at all, so the
sentence *"it does not transfer"* was denying something no pattern claims.** The
note other patterns carry is about **prediction minus one** — p10's reads *"body
+ driver loop + one per by-block would predict 6 and Verus reports 5, the
identical off-by-one p03's, p05's, p06's, p07's, p11's, p12's, p14's, p17's and
p18's spec.md record"*. It is a claim about the **rule of thumb**
(`.memory/04-verus.md`'s one-query-per-function-plus-one-per-loop, which p10
records as giving 8 where Verus gives 5), not about any particular value. p27's
copy mis-transposed it into *"would predict 5 and Verus reports 4"*, which is
where the stray 4 entered the tree, and p47's ⚠ then read the 4 as the thing
being shared. **What is shared is the shape; what is not shared is a 4, because
there is no 4.**

TASK_065 corrected `patterns/p27-handle-table/spec.md` and its generator
`controls/mkspec.py`, which moved p27's `contract_sha256`; the disclosure and
the byte-provable undo are in p27's own `NOTES.md`, and §15 below records why
the fix landed out of p47's corrections task. Found by TASK_064_REVIEW major 2.

`--cfg slb_twin`: **13 verified, 0 errors** (12 + the one twin).

---

## 3. Anti-collapse, and the denominator that had to change

⚠ **THE FIRST GATE RUN FAILED `collapse-ir` ON TEN OF SIXTEEN `-O3` CELLS**, and
the fix is a denominator, not a `min_ir_per_work`.

p47's work unit is a **byte comparison**, which consumes **two window bytes**
(a secret byte and a candidate byte) and produces one xor. Denominated in
window bytes — every other pattern's unit — the vectorised rungs land at
0.189…0.245 Ir per window byte, *under* the harness default of 0.25, on kernels
that are demonstrably doing the whole job:

```
[collapse-ir] unsafe O3 isolated: d(Ir)/d(work) = 0.206 < rate 0.25
              (434 Ir at work 200 -> 606 at 1032)
```

`.memory/02-bench-rules.md`'s own warning applies — *a floor that forbids the
fastest correct implementation is not a floor, it is a bug that happens not to
have fired yet* — and the repair it points at is the denominator. `model.py`'s
`work_per_call` is now `min over windows of (ncmp × tlen)`, the byte
comparisons the checked kernel performs (**96 on `small.bin`, 512 on
`large.bin`**, from `python3 model.py inputs/small.bin inputs/large.bin`). The
same two points then give **0.413**, and every `-O3` cell clears 0.25. **No
`min_ir_per_work` is declared**, so the harness default applies unchanged.

### 3a. Why the window-byte floor *forbids* this kernel, off the disassembly

⚠ **The delivery argued this from two whole-program marginals, which is an
argument about two points on a line. The mechanism is in §1a's listings and is
stronger** (TASK_064_REVIEW A1, which extracted it independently and upheld the
change). The tag loop is:

| rung | insns per iteration | window bytes per iteration | Ir per **window byte** |
|---|---:|---:|---:|
| `safe_tuned` / `c-clang-h` | 11 | 32 of *each* tag = **64** | **0.172** |
| `unsafe` / `verus` | 12 | 32 of *each* tag = **64** | **0.188** |

Both are **asymptotic rates read off the loop body**, not fits: at large `tlen`
the whole call converges on them. **0.172 and 0.188 are below 0.25**, so a
0.25-per-window-byte floor does not merely embarrass the shipped kernel — *it
forbids it, and it forbids the fastest correct implementation of the pattern in
either language.* On a wider ISA it is worse. `clang -march=native` on
`c/kernel_hardened.c`, tag loop, read off the listing:

```
vmovdqu   -0x60(%r12,%rbx), %ymm4        ... x4
vpternlogq $0xf6, -0x60(%r13,%rbx), %ymm4, %ymm1   # ymm1 = ymm1 | (ymm4 ^ mem)
                                          ... x4   <- xor and or FUSED
sub  $-0x80, %rbx ; cmp %rbx,%r15 ; jne             <- latch on the INDEX
```

**11 instructions per iteration, `$-0x80` = 128 bytes of *each* tag = 256 window
bytes** → **0.043 Ir per window byte, 5.8× under the floor**, with **0 interior
conditional branches** (so the constant-time property survives the wider ISA
too). ⚠ That figure is **static only**: §16 records why no `-march=native` build
on this box can be measured dynamically at all.

**So the unit is forced, not chosen.** The alternative — declaring a
`min_ir_per_work` — would have had to sit at or below 0.189 to admit `c-clang`,
i.e. a rate *fitted to the measurement* when the achievable rate is 0.043, which
is the thing the direction test exists to catch. A denominator is a fact about
the algorithm and is the same fact on every input.

**And p47 is the THIRD pattern to make this move, two of them after the
identical gate stage failed:**

| pattern | unit | bytes per unit | why it moved |
|---|---|---:|---|
| p07 | `probe` | 4 | a byte floor *"would fail a perfectly healthy pattern"* |
| p10 | `tap` | **2** | a byte floor *"would understate the work by a factor of `taps`"* — it moved to make the check **stricter** |
| p13 | `DST_CAP*K + S` | — | `stride` was *"WRONG for p13, **and the gate caught it**"* |
| p47 | `byte comparison` | **2** | this pattern |

`harness/check.py:1755-1760`'s own failure message prescribes it verbatim: *"the
fix is to re-denominate `work_per_call` in the thing the kernel touches."*

### 3b. ⚠ The cost, stated rather than left to a gate record

**The redenomination left p47 with the TIGHTEST anti-collapse margin of all 19
patterns, by a factor of 2.4.** From the committed gate JSONs
(`collapse_tightest_margin`):

```
p47-ct-compare      2.93x   <- tolerates a 65.9% work loss before collapse-ir fires
p01-array-sum       7.02x
p03-bounded-stack   7.47x
…
p14-field-split    57.76x
p18-varint-shift   65.46x
p27-handle-table  134.45x   <- tolerates a 99.3% work loss
```

So the change did **not** neuter the check on this pattern; it left it the most
binding it is anywhere in the tree. What it does not do is close the residual
`.memory/02-bench-rules.md:215` has recorded since TASK_008_REVIEW — nothing
checks that `work_per_call` is denominated in the unit `work_unit_bits` names,
and `work_per_call` itself appears in **no** gate JSON (`grep -c work_per_call
results/gate/*.json` → 0), so a *halving of the denominator under an unchanged
unit name* would leave no trace. p47 neither creates nor widens that; the unit
**name** did change and is recorded (`"collapse_work_unit": "byte comparison"`
where p02 and p27 carry `"byte"`), so a reader diffing gate records sees this
edit.

**Which way the estimate errs: STRICT, in three ways** — the minimum over
windows rather than window 0's or the mean; the header, the guard arithmetic,
the verdict fold and the Horner chain all counted as zero; window padding
ignored. ⚠ **And one way it is NOT strict, which has to be said rather than
hidden: the LEAKING rungs do not perform this much work.** That is the bug. Both
`collapse.probe_inputs` are chosen so it cannot fire — `small` has `tlen = 24 <
32` so even `bcmp` reads the whole tag, and `large` has two of its eight
comparisons EQUAL, forcing a full scan of those two in every rung.

---

## 4. THE RESULT: `Ir(k)`, and it is the side channel

`controls/sweep_ir.py --leak`, 35 `sweep-k*` blobs, `tlen = 256`, `ncmp = 4`,
every comparison mismatching, `k` stepped 0…255. **`cbytes` and `ncmp` are
constant across the entire band** (the script asserts it and prints the sets),
so the only thing that moves is where the first differing byte is. Whole-program
marginal, `n_iters` 100 → 200.

### `-O3 isolated`

| rung | Ir @ k=0 | Ir @ k=255 | **spread** | verdict |
|---|---:|---:|---:|---|
| `c-gcc` | 221.000 | 405.000 | **184.000** | LEAKS |
| `c-clang` | 197.000 | 381.000 | **184.000** | LEAKS |
| `safe_naive` | 324.000 | 508.000 | **184.000** | LEAKS |
| `c-gcc-h` | 694.000 | 694.000 | **0.000** | constant in k |
| `c-clang-h` | 618.000 | 618.000 | **0.000** | constant in k |
| `safe_tuned` | 700.000 | 700.000 | **0.000** | constant in k |
| `unsafe` | 626.000 | 626.000 | **0.000** | constant in k |
| `verus` | 625.000 | 625.000 | **0.000** | constant in k |

### `-O3 whole`

| rung | Ir @ k=0 | Ir @ k=255 | **spread** |
|---|---:|---:|---:|
| `c-gcc` | 214.000 | 398.000 | **184.000** |
| `c-clang` | 182.000 | 366.000 | **184.000** |
| `safe_naive` | 290.000 | 474.000 | **184.000** |
| `c-gcc-h` | 674.000 | 674.000 | **0.000** |
| `c-clang-h` | 593.000 | 593.000 | **0.000** |
| `safe_tuned` | 671.000 | 671.000 | **0.000** |
| `unsafe` | 594.000 | 594.000 | **0.000** |
| `verus` | 598.000 | 598.000 | **0.000** |

**0.000 is exact, not "small".** The 35 blobs print the same checksum (all
verdicts are MISS), so the driver's `println!` digit term cancels identically
and the constant-time rungs read the *same integer* at every one of 35 values
of `k`, in both inline modes.

**184.000 is the same integer on all three leaking rungs, in both modes.** It is
not a language property; it is glibc's.

### 4a. The shape is a STAIRCASE, not a line, and above 128 bytes not even that

Per **comparison**, relative to the cheapest (`k < 32`), off band k:

| bytes read by one comparison | 32 | 64 | 96 | 128 | 160 | 192 | 224 | 256 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| extra Ir | 0 | **+7** | +14 | +19 | **+40** | +43 | +46 | +46 |

The step is 32 bytes wide — AVX2, no `rep` — but it is **not uniform**. The
`+19 → +40` jump at 128 → 160 bytes is glibc's own size-class dispatch, and the
`+46 → +46` at 224 → 256 is where the block count stops mattering. **An attacker
therefore learns MORE from some positions than from others**, and a model that
assumed a slope would be wrong by up to 21 Ir per comparison. The three leaking
rungs' tables are **identical, integer for integer** — the "name the routine"
payoff: `memcmp` (gcc) and `bcmp` (clang, rustc) are one implementation here.

### 4b. Separating the three factors (`.memory/03-measurement.md`, p11's rule)

`-O3 isolated`, `small.bin` (whole-program marginal Ir/call):

| factor | what it compares | size |
|---|---|---:|
| **library** | `bcmp`'s early exit vs a byte-granular one (`safe_naive` 356.16 vs `n_early` 346.00 at k=5, and their **leak spreads**: 160.00 vs 6096.00 on the adversarial pair) | **38×** in leak resolution |
| **spelling** | `safe_naive` 356.16 vs `safe_tuned` 524.00 — one rung leaks, the other does not, same addressing | **+47.1%** |
| **safety** | `safe_tuned` 524.00 vs `unsafe` 434.00, at matched constant-time spelling | **+20.7%** |

Only the third is a safety number, and only the second is a security one.
Reported as a single `c-clang` vs `safe_tuned` ratio p47 would read as a 2.29×
"cost of safe Rust" and **none of it would be safety**.

---

## 5. Additivity extrapolation — 40 of 40 exact, in BOTH inline modes

`controls/predict.py`. This is the only out-of-sample test on this project that
has ever been able to fail (`.memory/03-measurement.md`).

**The fit bands, neither of which contains the held-out configuration:**

- **band k** — `nmatch = 0`, `ncmp = 4`, `k` swept. Gives the per-comparison
  cost of a MISMATCHING comparison as a function of the blocks it reads.
- **band m** — `k = 0`, `ncmp = 8`, `nmatch` swept 0…8. Gives the cost of an
  EQUAL comparison.
- **band x** — `k > 0` **and** `nmatch > 0`, `ncmp = 8`. **Neither band has it.**

**The model, and it is a STEP function rather than a line:**

```
Ir(k, nmatch) = Ir(band m at the same nmatch)
                + (ncmp - nmatch) * [ u(blocks(k)) - u(32) ]
```

**Result: `max|resid| = 0.000000` on all eight rungs, 40 predictions per inline
mode, 80 in total.** Sample rows (`-O3 isolated`):

```
sweep-x128m5.bin  c-gcc       nmis=3 B=160 pred= 658.000 meas= 658.000 resid=+0.0000
sweep-x192m2.bin  safe_naive  nmis=6 B=224 pred= 865.700 meas= 865.700 resid=+0.0000
sweep-x064m3.bin  safe_tuned  nmis=5 B= 96 pred=1276.300 meas=1276.300 resid=+0.0000
```

**Four independent things could have broken it and none did**: a dependence of
the per-comparison cost on `ncmp` (fitted at 4, applied at 8); an interaction
between equal and mismatching comparisons; a dependence on their *order* within
a window; and a dependence on `k` beyond the block count.

⚠ **What this is NOT.** A plain 5-column OLS over the same rows
(`sweep_ir.py --fit`, regressors `ncmp, cbytes, neq, kblk_mis, const`) has
`max|resid|` of **61…155 Ir** and the held-out rows land 0.1…37.7 out. The
design is rank 5 of 5 and the held-out rows are **inside** its row space, so by
`.memory/03-measurement.md`'s own criterion that fit's residuals are an
interpolation check. The step model is what is exact, and it is exact because it
is the mechanism rather than a basis.

⚠ **A LAW OWES ITS DOMAIN.** Five parameters this sweep does **not** vary, and
the list is **not claimed closed** — `sweep_ir.py --fit` prints them on every
run: tag ALIGNMENT relative to a 32-byte boundary (every blob puts the first tag
at window byte 8); the WIDTH of the differing byte (`gen.py` always flips 4
bits); the DISTRIBUTION of `k` *within* one window (every comparison in a sweep
window has the same `k`); glibc's IFUNC choice (one machine, one libc); and the
number of distinct windows (4 or 2 throughout).

---

## 6. The adversarial rows — a checksum-identical pair

**A timing pattern has no crash and no wrong answer.** All eight cells agree
with `model.py` on every input at every opt level and inline mode, ASan and
UBSan report nothing on any input, and Miri is clean. So p47's adversarial rows
are a **pair**:

| input | shape | checksum, all 8 cells × 2 opts × 2 modes |
|---|---|---|
| `adversarial-k000` | 8 comparisons, `tlen` 128, all mismatching at byte **0** | `15618968502624590848` |
| `adversarial-klast` | same seed, same shape, all mismatching at byte **127** | `15618968502624590848` |
| `adversarial-equal` | same shape, every comparison **equal** | `15278858700986457088` |
| `adversarial-stride7` | 7-byte window; the driver guard skips the loop | `0` |

`controls/ir_table.py --mode isolated --leak-controls`, whole-program marginal.
**Re-derived in full at TASK_065 after the generator repair below; every figure
below is that run's output, and every one of the eleven rows the delivery
published reproduced to the milli-instruction.**

| binary | k=0 | k=127 | equal | **klast − k000** | verdict |
|---|---:|---:|---:|---:|---|
| `c-gcc` | 373.720 | 533.720 | 493.720 | **+160.000** | LEAKS |
| `c-clang` | 333.720 | 493.720 | 453.720 | **+160.000** | LEAKS |
| `safe_naive` | 524.300 | 684.300 | 644.300 | **+160.000** | LEAKS |
| `c-clang-h` | 798.720 | 798.720 | 798.720 | **+0.000** | constant |
| `c-gcc-h` | 870.720 | 870.720 | 870.720 | **+0.000** | constant |
| `safe_tuned` | 924.300 | 924.300 | 924.300 | **+0.000** | constant |
| `unsafe` | 798.300 | 798.300 | 798.300 | **+0.000** | constant |
| `verus` | 797.300 | 797.300 | 797.300 | **+0.000** | constant |
| **`m_leak` (the PROVED rung, §9)** | 276.300 | 7364.300 | 7364.300 | **+7088.000** | **LEAKS** |
| `n_early` (safe Rust, hand loop) | 354.300 | 6450.300 | 6482.300 | **+6096.000** | LEAKS |
| `h_vol-clang` | 5390.720 | 5390.720 | 5390.720 | +0.000 | constant |
| `h_vol-gcc` | 8426.720 | 8426.720 | 8426.720 | +0.000 | constant |

**Two byte-different files, one checksum, +160 instructions.** That is the harm
column, per rung, and it is the only column in this project that can hold it.

`n_early`'s +6096.000 over 8 comparisons × 127 bytes = **exactly 6.000 Ir per
leaked byte**, reproducing the standalone probe (0d) on the shipped kernel
shape. **The library's early exit leaks at 32-byte resolution; a hand-written
one leaks at 1-byte resolution and is 38× louder.**

### 6a. ⚠ The `+7088.000` rested on a blob with NO GENERATOR, and now does not

**As shipped, `controls/gen_controls.py:416-418` read**

```python
for name, p, kind, _src in made:
    if kind == "verus":
        continue
```

so `--build` wrote `m_leak`'s **source** and never built its **binary**;
`ir_table.py --leak-controls` printed `MISSING` for the row this pattern's
README quotes as its punchline. The `+7088.000` was correct — the review
rebuilt it by hand and got it exactly — but it came from a blob the committed
tree could not rebuild, which is `CLAUDE.md` "Don't" #1 (*if a blob has no
script that rebuilds it, write one before finishing*). **The number was
reproducible; the reproduction path was not, and only the second of those is
checkable by the next reader.** TASK_064_REVIEW major 1, and the reviewer
deliberately deleted their own hand-built `m_leak` binary rather than leave one
that would have hidden the defect.

**The repair, and it is in the generator rather than in a note.**
`gen_controls.py::build()` grew a `verus`-kind branch whose flags are
`harness/build.py::build_verus` verbatim, and a `VERUS_BUILD` set naming the
variants whose binary is wanted — `m_leak` alone, because `m_noguard` and
`m_hdr` **must fail** to verify (so no object can exist) and the `u_*_verus`
files are twins whose job is verification, their Ir coming from the
byte-identical `u_*` builds. Skips are **printed**, not silent:

```
$ python3 patterns/p47-ct-compare/controls/gen_controls.py --build
  --   m_noguard      verus-kind, no binary wanted (see VERUS_BUILD)
  --   m_hdr          verus-kind, no binary wanted (see VERUS_BUILD)
  ok  m_leak         isolated  .../ctlbin/m_leak-O3-isolated   [verification results:: 14 verified, 0 errors]
  ok  m_leak         whole     .../ctlbin/m_leak-O3-whole      [verification results:: 14 verified, 0 errors]
```

and the table above is that binary. Two adjacent reproduction defects in the
same tooling went with it: `--leak-controls` defaulted to the **8 shipped
cells**, so `README.md`'s documented line printed 8 rows against this 12-row
table (fixed — `LEAK_CELLS` is the default, which is why `c-gcc` now appears);
and `ir_table.py::binary()` fell back to `-O3-isolated` when a `whole` build was
absent, so `--mode whole` on a control built only isolated printed an
**isolated** figure under a `whole` heading. No published figure was affected —
every `h_vol` number in §8c is isolated — but it was a silent-wrong-answer path
in the tool that produced this pattern's tables. The fallback is gone and
`--build` now writes **both** inline modes for every kind, C controls included.

---

## 7. Sanitisers, Miri, and what they do NOT see

- **ASan + UBSan** (gate stage 7, gcc `-O1 -fsanitize=address,undefined`):
  `clean` on all seven inputs, and `model.py` declares `clean` unconditionally.
  There is nothing to tabulate: `c/kernel.c` reads only inside the window its
  own guard proved present.
- **Miri**: required (a trusted item exists) and **silent about p47's bug**. It
  checks the `get_unchecked` reads, which are the thing `c/kernel.c` gets right.
  It is listed in `spec.md` because a wrong `buf_get_unchecked` would still be
  invisible to Verus; it is **not evidence about the timing property**.
- **The gate's own checksum stage** cannot see the bug either, by construction.

**p47 is the first pattern here whose `c/kernel.c` is memory-safe.** Every other
`c/kernel.c` in the tree either reads outside an allocation or returns a wrong
answer on some input.

---

## 8. The rung comparison, both inline modes, both blobs

`controls/ir_table.py`, whole-program marginal Ir/call, `n_iters` 100 → 200.

⚠ **`results/p47-ct-compare.json` was re-measured from scratch at TASK_065**
(`model.py` moved, so the record went STALE). **Every deterministic field
reproduced exactly** — all 32 cells, all `n_raw` / `n_nopad` / `.text` bytes /
`md5_raw` / `md5_raw_norel` / kernel-exclusive `Ir` values byte-for-byte
identical to the record `e6e86fc` shipped, `0` non-wall field differences over
the whole file. Only wall clock moved, which is what it is for: a *different*
four of the 32 rows now exceed the 10% min-to-median spread threshold and are
discarded, and they are printed marked in `results/tables/p47-ct-compare.md`.
**No claim in this file rests on a discarded row**, and §11's wall-clock figures
come from `controls/clayout.py`'s 72-binary layout population rather than from
this record.

| cell | small, isolated | large, isolated | small, whole | large, whole |
|---|---:|---:|---:|---:|
| `c-gcc` | 253.270 | 426.280 | 246.270 | 423.280 |
| `c-clang` | 229.270 | 386.280 | 214.270 | 375.280 |
| `c-gcc-h` | 422.000 | 645.280 | 402.000 | 621.280 |
| `c-clang-h` | 442.000 | 621.280 | 401.000 | 592.280 |
| `safe_naive` | 356.160 | 577.700 | 322.160 | 539.700 |
| `safe_tuned` | 524.000 | 747.700 | 479.000 | 714.700 |
| `unsafe` | 434.000 | 605.700 | 402.000 | 601.700 |
| `verus` | 433.000 | 604.700 | 406.000 | 609.700 |

`verus − unsafe` is −1.00 / −1.00 isolated and +4.00 / +8.00 whole. **The
kernels are byte-identical at `-O3` (`md5_fn a3898fc70d69`, `md5_raw` equal), so
this is the driver's and not the kernel's** — quote the `md5` when saying a
proof costs zero (`.memory/03-measurement.md`).

### 8a. The exact difference laws, and the INLINE MODE changes one of them

`tlen ≡ 0 (mod 32)`, 61 rows per mode from bands k, m, t and g:

```
-O3 isolated   R3 - R4 = 54 + 13*ncmp - 0.031250*cbytes     max|resid| 0.00000
-O3 whole      R3 - R4 = 41 +  9*ncmp + 0.000000*cbytes     max|resid| 0.00000
```

⚠ **The `cbytes` coefficient DIES between the modes.** In `isolated`, safe Rust
is 1/32 Ir per compared byte *cheaper* than unsafe Rust — the twelfth
instruction of §1a — and in `whole` that advantage is **exactly zero**, because
once the kernel is inlined into `main` LLVM gives both rungs the same induction
structure. `.memory/03-measurement.md`'s p10 entry is the same phenomenon with
the regressors *swapping*; here one dies. **Both fits are exact and both are
full rank, so nothing but naming the mode distinguishes them.**

**The DOMAIN is `tlen ≡ 0 (mod 32)` and it is a missing column, not a caveat.**
Outside it the law fails and by how much is measured, `-O3 isolated`, `ncmp = 4`:

| `tlen` | 1 | 2 | 4 | 8 | 12 | 16 | 24 | 32 | 48 | 64 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| measured `R3 − R4` | 134 | 134 | 90 | 90 | 90 | 90 | 90 | 102 | 82 | 98 |
| law | 105.9 | 105.8 | 105.5 | 105 | 104.5 | 104 | 103 | **102** | 100.5 | **98** |
| residual | +28.1 | +28.3 | −15.5 | −15 | −14.5 | −14 | −13 | **0** | −18.5 | **0** |

The residual is **0 exactly at every multiple of 32 and never elsewhere.** The
missing column is the vectoriser's scalar tail, whose own structure is a
16/8/4/1-byte cascade; a linear `tlen mod 32` term does not fit it either
(measured: `t016` implies −0.25/byte, `t024` implies −0.17). **Not identifiable
from this design**, and that is the honest verdict rather than "no law exists".

### 8b. Safe Rust vs hardened C: **zero per compared byte**

Same 61 rows:

```
-O3 isolated   R3 - R1h(clang) = 37.90 + 10.99*ncmp + 0.000086*cbytes   max|resid| 0.449
-O3 whole      R3 - R1h(clang) = 33.90 + 10.99*ncmp + 0.000086*cbytes   max|resid| 0.449
```

The `cbytes` coefficient (0.000086, i.e. 0.176 Ir at the largest `cbytes` in the
band) is **below the residual**, which is itself the driver's `println!`
digit-count term across the C and Rust emit paths. So: **safe Rust's
constant-time comparison costs nothing per compared byte over hardened clang C
— the two tag loops are the same eleven instructions (§1a) — and its whole cost
is `38 + 11·ncmp` per call, flat in the data.** That is
`.memory/01-ladder.md` finding 3's shape on a ninth pattern.

Unsafe Rust against the same baseline is `−16 − 2·ncmp + 0.031336·cbytes`
isolated and `−7 + 2·ncmp + 0.000086·cbytes` whole: **cheaper than hardened C
per call and dearer per byte, and the sign of the `ncmp` term flips between
modes.** Do not quote it without the mode.

### 8c. The `volatile` control, and why `spec.md` forbids it

| cell | small, isolated | large, isolated | ratio to the plain accumulate |
|---|---:|---:|---:|
| `c-clang-h` | 442.000 | 621.280 | — |
| `h_vol-clang` | 646.000 | 2829.280 | 1.46× / **4.55×** |
| `c-gcc-h` | 422.000 | 645.280 | — |
| `h_vol-gcc` | 914.000 | 4329.280 | 2.17× / **6.71×** |

On the adversarial window (`tlen` 128, 8 comparisons) it is **6.75× (clang)** and
**9.68× (gcc)**. `volatile` defeats vectorisation entirely: the loop becomes
load / xor / or / store through a stack slot, one byte at a time, in both
compilers. **It buys nothing** — the plain accumulate is already exactly
constant in `k` (§4) at every optimisation level tested (0e). The received
advice is measurably wrong on this toolchain, and the ratio grows with `tlen`,
so quote it with the blob.

### 8d. The R3-side span, in contract, cheapest found with the input NAMED

`spec.md` pins the comparison expression and leaves the ADDRESSING free.
`-O3 isolated`, whole-program marginal:

| R3 spelling | small | large |
|---|---:|---:|
| `t_win` — window resliced once, tags are subslices of it | **520.000** | **735.700** |
| `safe_tuned` (shipped) | 524.000 | 747.700 |
| `t_split` — `split_at` twice instead of `&buf[a..b]` | 532.000 | 759.700 |
| `t_iter` — `.iter().skip().take()` instead of a subslice | 1328.000 | 5419.700 |

**R3-side span: 520.000 … 1328.000 (`small`) / 735.700 … 5419.700 (`large`).**
Cheapest found is `t_win` on **both** blobs — `−4.000 / −12.000` against the
shipped rung. The word is "cheapest found", never "minimum"
(`.memory/01-ladder.md` finding 14). `t_iter` is *in contract* — it keeps the
pinned `fold(0u8, |acc, (x, y)| acc | (x ^ y))` — and is 2.5×/7.3× the shipped
rung, because `skip`/`take` iterators defeat the vectoriser. **A pinned idiom
makes the class decidable, not singular**, and the span is the measurement of
that.

### 8e. The R4 side, SEARCHED — and it is not degenerate

`.memory/01-ladder.md` findings 18 and 19: *"degenerate as far as this task
searched" has been FALSE on two consecutive patterns, and both times it
flattered the safe rung.* Six R4 levers were built, each measured **and** put
through `./verus_run.py` before its number was quoted (`.tasks/TASK_026.md` §0
item 3), reading the **error text** and not the exit code:

| candidate | small | large | twin | `identity` at `-O3` | admissible? |
|---|---:|---:|---|---|---|
| `unsafe` (shipped) | 434.000 | 605.700 | 12/0 | `exact` | yes |
| `u_base` — the two bases hoisted | 434.000 | 605.700 | **12/0** | `exact` (byte-identical) | **yes**, and moves 0 |
| `u_winu` — window resliced with `get_unchecked(range)` | 434.000 | 605.700 | **12/0** | `exact` | **yes, at a FOURTH trusted item** |
| `u_end` — `while i < ea` with an end cursor | 475.000 | 674.700 | **12/0** | `exact` (byte-identical) | **yes**, `+41.000 / +69.000` |
| `u_win` — window resliced with safe `split_at` | **410.000** | **581.700** | **12/0** | **`norel`, NOT `exact`** | **no** |
| `u_ptr` — raw pointers | 424.000 | 587.700 | `error: dereferencing a raw pointer is not supported` | — | **no** |

**So the R4 side MOVES: `u_end` verifies 12/0, is byte-identical to its twin,
and measures +41.000 / +69.000 against the shipped rung.** The admissible-at-
`exact` R4 range found is **434.000 … 475.000 (`small`) / 605.700 … 674.700
(`large`)** — width 41 / 69, which is not zero, so p47 is the third pattern
(after p03 and p12) with a non-degenerate R4 endpoint.

⚠ **But nothing found moves it DOWN at `exact`.** `u_win` is 24.000 cheaper on
both blobs, verifies with no new trusted item and no lemma, and is excluded by
the **identity level alone** — `md5_raw` differs while `md5_raw_norel` matches,
which is p10's `u_win` situation exactly. `u_winu` reaches
`<[T]>::get_unchecked` on a *Range* to remove the panic pad, which needs a
**fourth `external_body` item** (`slice_unchecked`) — p16's `r4_hdr` shape: a
respelling that costs a new axiom is not free.

⚠ **And the prose above used to read *"`u_winu` removes that panic pad and is
`exact`"*, which reads as a near-miss and understates the result.** Measured:

```
$ python3 harness/asm.py stat .temp/build/p47/unsafe-O3-isolated
n_raw 174  n_nopad 156  md5_raw 4d99e76e0b10..  md5_raw_norel c52ba8187b22..
$ python3 harness/asm.py stat .temp/p47/ctlbin/u_winu-O3-isolated
n_raw 174  n_nopad 156  md5_raw 4d99e76e0b10..  md5_raw_norel c52ba8187b22..
```

**`u_winu` is BYTE-IDENTICAL to the shipped R4**, not a variant that removes
something from it — the table's own 434.000 / 605.700 says so. LLVM already
elides the panic pad on the shipped spelling, so the fourth axiom buys **zero
instructions**, and "nothing found moves it down at `exact`" is therefore
*stronger* than the prose suggested (TASK_064_REVIEW minor 4). The review pushed
this further and I record it because it strengthens the exclusion: `get_unchecked`
appears **nowhere** in `~/tools/verus/vstd/` for any index type, so no route to
it exists without a new axiom; and `slice_unchecked` is `external_body` +
`requires` + `ensures` + `unsafe` body, which puts it *inside* the verified-twin
regime (`.memory/04-verus.md:820`) while `u_winu_verus.rs` supplies no twin for
it — so shipping it would cost a fourth axiom **and** a fifth item **and** would
fail gate stage 5c-twin as written.

**What p47 therefore publishes is the FIXED-R4 bound** — `R3ship − R4ship`
bounding `inf(in-contract R3) − R4ship`, R4 held by fiat — **beside the R3-side
span and the measured R4-side width.** `R3ship − R4ship = +90.000 / +142.000`
(`-O3 isolated`) and `+77.000 / +113.000` (`-O3 whole`).

⚠ **The `u_win` mechanism, because "it vanished" is not one** (PROTOCOL rule
12). Its tag loop is **11 instructions** where the shipped R4's is 12: LLVM
turns the trip counter into a countdown (`addq $-0x20, %r12`, whose flags feed
the `jne` directly) instead of `addq $0x20,%r11 ; cmpq %r11,%r9`. The
**closed** decomposition (`controls/ir_table.py --closed`, parsing the whole
callgrind table rather than four named needles) puts **all** of it in the kernel:

```
u_win::kernel  568.0000   unsafe::kernel  592.0000   delta -24.0000
SUM OVER EVERY FUNCTION = -24.0000
whole-program delta     = -24.0000
closed? YES
```

⚠ **What is NOT attributed**: the −24.000 is *flat* across `small` (`ncmp` 4,
`tlen` 24 — no 32-byte vector iteration runs at all) and `large` (`ncmp` 8,
`tlen` 64 — sixteen do). A per-iteration saving cannot be flat across those two,
so the eleven-vs-twelve loop is **not** the whole of it and the residue is
unexplained. Said here rather than papered over.

### 8f. `R3 − R4` is 100% kernel

Same closed decomposition on `large.bin`, `-O3 isolated`:

```
safe_tuned::kernel 734.0000   unsafe::kernel 592.0000   delta +142.0000
SUM OVER EVERY FUNCTION = 142.0000
whole-program delta     = 142.0000
closed? YES
```

Nothing in the allocator, nothing in libc, nothing in `core::fmt` beyond the
±0.22 digit term. Unlike p27, where 52% of the gap was drop glue.

---

## 9. Verus, and THE POINT OF THE PATTERN

### 9a. What CAN be proved

`kernel` verifies `r == tag_fold(buf@, off as int, len as int)` from one
structural precondition, `off + len <= buf@.len()`. That covers:

- every unchecked read is in bounds — the `buf_get_unchecked` precondition
  discharges from the window guard plus the precondition;
- the walk stops for the right reason and performs the right *number* of
  comparisons (`o` is folded);
- each verdict is the right one — `xacc` is the whole-tag or-accumulate;
- no arithmetic in the kernel overflows (`2 * tlen`, `p + 2 * tlen`,
  `off + p + tlen + i`), given `global size_of usize == 8`, which is CHECKED
  against the target rather than assumed.

Both loops terminate (`decreases ntag - o` and `decreases tlen - i`).

### 9b. What CANNOT be proved, and it is not a matter of effort

**The two mutants that MUST fail, and do:**

```
$ ./verus_run.py .temp/p47/ctl/m_noguard.rs     # window guard `len - p >= 2*tlen` deleted
 1: error: invariant not satisfied before loop
 7: verification results:: 11 verified, 1 errors
 8: error: aborting due to 1 previous error

$ ./verus_run.py .temp/p47/ctl/m_hdr.rs         # second tag's read shifted by one byte
 7: error: invariant not satisfied at end of loop body
19: error: precondition not satisfied            <- buf_get_unchecked's `i < v@.len()`
32: verification results:: 11 verified, 1 errors
33: error: aborting due to 2 previous errors
```

⚠ **`m_hdr` was quoted here as "11 verified, 2 errors" and Verus says 1**
(TASK_064_REVIEW minor 2). The 2 is **rustc's** *previous-errors* count on the
last line, not Verus's; both error **texts** were right and the mutant fails as
required, but the count was transposed from the wrong line of a block presented
as pasted output. The full line numbering is reproduced above so the two counts
cannot be confused again.

**And the mutant that MUST PASS, which is p47's deliverable:**

```
$ ./verus_run.py .temp/p47/ctl/m_leak.rs
verification results:: 14 verified, 0 errors
```

`m_leak` is `verus.rs` with the constant-time tag loop replaced by an
**early-exiting** one — `while i < tlen && d == 0` — plus one ghost lemma,
`lemma_xacc_sticky`, saying that once the accumulator is non-zero it stays
non-zero. The count is `14 = 12 + 2`, measured: `kernel` still reports **3**,
exactly as the shipped file does, and the two extra obligations are the
lemma's own body and its `by (bit_vector)` query
(`--verify-function lemma_xacc_sticky --verify-root` → 2 verified). **The
kernel's proof burden does not change at all when the leak is put back in.** That lemma is the whole of why the leaking program satisfies the
constant-time specification: **the two programs are the same function.**

The compiled `m_leak` binary leaks **+7088.000 Ir/call** between
`adversarial-k000` and `adversarial-klast` — two files that print the *same
checksum* (§6). It is the loudest leaker in the table, and it carries a proof.

> **So the top rung of this project's ladder certifies a leaking kernel.**

### 9b′. ⚠ The precise sense in which the two proofs differ — and it is not in the contract

The obvious attack on §9b is *"the honest proof must establish something the
leaking one does not, or the sentence is rhetoric."* **It does. The point is
that the difference is invisible at the interface**, and stating it that way is
strictly stronger than what this section said as shipped (TASK_064_REVIEW A2,
which diffed the two files instruction by instruction and reproduced every
count).

- **Shipped `verus.rs:338-364`.** The loop invariant is
  `xacc(buf@, base, tlen, i, d) == xacc(buf@, base, tlen, 0, 0)` and the loop
  has a **single** exit, so at the base case `i == tlen` and the invariant
  yields `d == xacc(…, 0, 0)` — **the accumulator's exact value**.
- **`m_leak`.** The same invariant survives, but the loop can now exit with
  `i < tlen`, so the base case **splits** and `lemma_xacc_sticky` gives only
  `d == 0 <==> xacc(…, 0, 0) == 0` — **the accumulator's zero-ness**.

So the shipped file proves a strictly **stronger intermediate fact**. It buys
nothing at the interface, because `tag_fold` folds the **verdict** and never the
accumulator, so both files discharge the *identical* `ensures`. **The diff
touches no `requires` and no `ensures` — not one character of the kernel
signature or of either clause differs**, and the whole exec delta is one
conjunct, `while i < tlen` → `while i < tlen && d == 0`. Everything else added
is a `proof fn`, a `proof {}` block and two `assert`s, all erased before
codegen — visible on the object, and measured on the binary the repaired
generator now builds (§6a):

```
$ python3 harness/asm.py stat .temp/p47/ctlbin/m_leak-O3-isolated
n_raw 68   n_nopad 66    md5_raw 7c75757d95e1..
$ python3 harness/asm.py stat .temp/build/p47/verus-O3-isolated
n_raw 174  n_nopad 156   md5_raw 4d99e76e0b10..
```

**68 instructions against the shipped 174**, and the difference is the early
exit rather than the lemma — a ghost lemma that survived codegen would show up
as *more* instructions, not 106 fewer.

**Identical contract, strictly stronger intermediate.** *"The proof certifies a
leaking kernel"* is exactly right, and this is the precise reason: **the extra
strength the honest proof carries is invisible in the specification the ladder
certifies.**

### 9c. Why, stated precisely

1. `ensures r == tag_fold(...)` denotes the **value** returned. p47's defect
   does not change the value — no strengthening of a value postcondition can
   exclude it, because the leaking and the constant-time kernels are
   *extensionally equal* and `lemma_xacc_sticky` is the proof of that.
2. A timing property is about the **trace**. Verus's assertion language has no
   term denoting a trace, no cost model, and no way to quantify over the *two*
   executions a non-interference property compares. It is not hard here; it is
   **not expressible**.
3. It is not even a property of this program. It is a property of the machine
   code, which LLVM chooses after Verus has finished — `.memory/06-catalogue.md`
   hazard 2 (*a text pin binds the source, not the object*) with the prover in
   place of the pin. p47's answer to that hazard is the `identity: O3 exact`
   pin plus §1a's disassembly: R5's object **is** R4's object, and R4's object
   contains a branchless vectorised loop.

This mirrors `.memory/01-ladder.md` finding 5 (p17, *provably memory-safe and
still leaking*) one level up, and finding 11 (p09, *invisible to the proof*)
from the other side: p09's bug is invisible because the *specification* was
silent about it and could have been strengthened; p47's is invisible because
the **logic** is silent about it and cannot be.

---

## 10. The trusted base

**3 items**, one with a `requires`. Classification:
**1 U-license + 2 infra + 0 V-gap.**

| item | kind | why |
|---|---|---|
| `buf_get_unchecked` | **U-license** | vstd ships no spec for `<[T]>::get_unchecked`; identical character for character to the accessor sixteen other patterns ship |
| `load_input` | infra | argv, file I/O, LE decode, delegated to `common/driver.rs`; **no `ensures`**, deliberately |
| `emit` | infra | `println!` is not verifiable; no `ensures` |

**How the rung reaches unchecked memory**: `unsafe.rs` and `verus.rs` perform
exactly one kind of memory access — a byte read of the input window through
`<[u8]>::get_unchecked`. There is no scratch buffer, no output buffer, no
allocation and no write of any kind, so `buf_get_unchecked` is the *only* door
to unchecked memory and its `requires i < v@.len()` is the only obligation
standing in it. `harness/check.py` derives the TCB from `verus.rs` rather than
from `spec.md` and reports **3**, which is `tcb_items`.

⚠ **On p47 that obligation has nothing to do with the pattern's bug.**
`c/kernel.c` violates no bound. This is a difference from p10, where the trusted
item's `requires` *is* the C rung's defect.

SLB-TRUSTED-ARGUMENT verus.rs buf_get_unchecked

(a) Is the twin's body the right checked stand-in for the unchecked operation?
    The trusted body is `unsafe { *v.get_unchecked(i) }` and the twin
    `slb_twin_buf_get_unchecked` is `v[i]`, under the identical signature and
    the identical `requires i < v@.len()` / `ensures r == v@[i as int]`. Those
    are the same operation on the same operands, differing only in whether the
    bound is checked at run time: `get_unchecked`'s documented contract in the
    standard library is precisely "if the caller guarantees `i < v.len()`, this
    is `v[i]`". A `requires` too weak to license `*v.get_unchecked(i)` is too
    weak to license `v[i]`, and Verus can see the second one -- which is what
    makes the twin a real test rather than a restatement. It verifies at
    `--cfg slb_twin` (13 verified, 0 errors against the shipped 12) and it
    FAILS when the `requires` conjunct is deleted (12 verified, 1 errors),
    which gate stage 5c-twin checks by deleting it.

(b) Is the `ensures` COMPLETE with respect to every unchecked operation the
    body performs? The body performs exactly ONE unchecked operation -- a
    single byte load at `i` -- and the `ensures` states the whole of its
    result, `r == v@[i as int]`. There is no second access to leave
    unspecified, which is TASK_009_REVIEW's x4 hazard (a trusted body that also
    reads `i + 1` would pass the contract pin, the twin and the
    `--cfg slb_twin` run unchanged). The claim is checkable by reading the
    one-line body: it contains one `*`, one `get_unchecked` and no other
    expression. p47's kernel writes nothing anywhere and allocates nothing, so
    there is also no store and no allocator effect to be silent about.
    ⚠ And the completeness claim here is about MEMORY EFFECTS ONLY. This item's
    `ensures` says nothing about how long the load takes or how many
    instructions it costs, and neither does any other clause in `verus.rs`;
    that is p47's whole subject (see 9c) and it is a property of the assertion
    language, not an omission in this contract.

(c) Does each clause mean the same thing in the shipped configuration as in the
    twin's? Both clauses are over `v@` and `i` only -- no `old()`, no
    `final()`, no ghost state, no cfg-dependent name -- and `v@` is `Seq<u8>`
    in both configurations because the parameter type is the same `&[u8]`.
    `#[cfg(slb_twin)]` is a cfg no measured build ever sets, so the twin is
    stripped by rustc before codegen and cannot change the shipped instruction
    stream; gate stage 5c-twin additionally checks that the token `slb_twin`
    occurs nowhere in the file but on that one attribute, and the `-O3`
    identity pin (R4 == R5, `md5_raw` equal) is the independent evidence that
    the shipped object contains no twin.

---

## 11. Wall clock — bracketed by a 72-binary layout population

`controls/clayout.py`, ported from p27's (which was ported from p14's), with
the paths, the cell list and two machinery repairs noted in §13. `small.bin`,
`n_iters = 200 000`, 13 reps, alternating schedule, estimator
`(t(N) − t(1))/(N − 1)` — which differences the per-process level away
(`.memory/03-measurement.md` finding 20a).

**CONTROL 1**, asserted every build: `n_fn` and `md5_fn_norel` are single-valued
per cell over all 24 layouts — `safe_naive` [194] / `8d0de7dc2c8f`,
`safe_tuned` [270] / `0d22a2eaeb86`, `unsafe` [162] / `f35103acf9fc`, 21
distinct kernel addresses each. Every binary runs the same instruction stream
and differs only in where the linker put it.

| cell | ns/call | median | IQR |
|---|---|---:|---|
| `safe_naive` (R2, leaks) | 23.07…26.71 | **25.89** | 25.23…26.30 |
| `safe_tuned` (R3, constant) | 32.70…35.83 | **33.46** | 33.02…33.78 |
| `unsafe` (R4, constant) | 25.62…28.94 | **27.56** | 26.98…27.96 |

**What to quote — the two statistics that converge** (`.memory/03-measurement.md`
retracts worst-vs-best range and dominance):

```
safe_tuned vs unsafe   paired by layout n= 24  MEDIAN +21.95%
                       all cross pairs  n=576  MEDIAN +21.62%  P(R3>R4) = 1.000
safe_naive vs safe_tuned  paired n= 24  MEDIAN -22.65%
                       all cross pairs  n=576  MEDIAN -22.86%  P(R2>R3) = 0.000
safe_naive vs unsafe   all cross pairs  n=576  MEDIAN  -6.34%  P(R2>R4) = 0.043
```

⚠ **`P(R3>R4) = 1.000` IS SATURATED, AND A SATURATED PROPORTION IS NOT THE
SANCTIONED STATISTIC** (TASK_064_REVIEW minor 5). `.memory/03-measurement.md:1075`
licenses pairwise `P(A > B)` over all `N²` layout pairs on the strength of a
flatness measurement taken at ≈0.58 — mid-range, *"flat at every `N`
(58.1 → 58.4 across N = 4…30)"*. **That measurement does not cover the
ceiling.** At `P = 1.000` the statistic is `min(R3) > max(R4)`, i.e. **disjoint
bands** — which is exactly the *worst-vs-best range* statistic
`.memory/03-measurement.md` **retracts six lines above**, for widening
28.91% → 30.78% on the same binaries and flipping a verdict. It is the retracted
statistic wearing the sanctioned one's clothes. **Nothing here is withdrawn**:
the convergent medians below are published beside it and are what the headline
should quote. `P = 1.000` is reported as a *separation flag* and never as a
magnitude, and `README.md` now quotes the median.

**Two claims are sayable and one is not:**

1. **Safe Rust's constant-time rung is +21.6% wall clock over the unsafe one on
   `small`** — median of 576 layout cross pairs, +21.95% paired by layout
   (n = 24). The bands are also disjoint (`P(R3>R4) = 1.000`), including under
   mode-matching: partitioned by `win32`/`jcc32` on every loop the predicate
   applies to, all **four** partitions separate, medians +20.63%…+23.60%. Quote
   the median, and read the separation as *"no layout pair inverts it"* rather
   than as a probability estimate — see the ⚠ above. Compare `Ir`: +20.7%.
   **`Ir` and `ns` agree here, in direction and to within a point** — which is
   worth saying because `.memory/01-ladder.md` findings 5 and 6 are the two
   cases where they did not.
2. **Constant time costs +29.6% wall clock over the leaking safe rung**
   (`P = 0.000`, i.e. perfect separation the other way; the median ratio
   `-22.86%` inverted). `Ir` says +47.1%, so **`Ir` overstates the wall-clock
   price of the security property by 1.6×** and a paper quoting `Ir` alone
   would overstate what constant time costs.
3. **`safe_naive` vs `unsafe` is NOT sayable**: `P = 0.043` and the paired range
   crosses zero (−18.48…+1.70). No magnitude is published for that pair.

⚠ **All three figures are `small.bin` at `-O3 isolated` only.** `large.bin` at
n_iters = 3000 gives an estimator dominated by the 8.4 MB file load — measured,
and it produced *negative* ns/call — so no `large` wall-clock figure is
published.

---

## 12. The `slb-contract` hash, disclosed

**PROTOCOL definition-of-done item 6 asks for the sha256 as first written,
before any cell was built. p47 cannot supply an honest one**, and saying so is
better than supplying a value the tree cannot reproduce:

`spec.md`'s fenced block is **generated** by `controls/mkcontract.py`, which
reads the shared named-spelling paragraph out of a donor `spec.md`. The block
therefore did not exist as a file until after `verus.rs` did, because the
generator's `verus.items` table is a transcription of `verus.rs`'s clauses and
its `obligations` pin is a measured count. What is checkable instead, and is
stronger in the one way that matters:

- **`controls/mkcontract.py` is committed**, so the block is re-derivable from
  it by one command and any edit to a pin is an edit to a reviewed Python
  literal rather than to 27 KB of JSON;
- **the generator IMPORTS `harness/check.py::named_spelling_problem` and refuses
  to write** if the result does not satisfy it, so the p27 accident
  (`.memory/05-layout.md`: a generator with an embedded copy of the paragraph
  silently deleted it on re-run) **cannot happen here by construction**;
- **`items` is hand-transcribed and not derived** from `verus.rs`, because a pin
  generated out of the artefact it pins certifies nothing.

**Every pin that moved after a measurement, and why** — this is the disclosure
the recorded-hash rule exists to force:

**Before `e6e86fc` — pins that moved while p47 was being built:**

| pin | from | to | why | direction |
|---|---|---|---|---|
| `verus.obligations` | (never written wrong) | 12 | measured before the first gate run | — |
| `obligations_note` | `main 4` | `main 5` | the term was **predicted** from a misreading of p10's note rather than measured; measured per item afterwards, and p47's `main` is 5 | corrects a *wrong* claim; the pinned total 12 never moved |
| `forbidden` | ``memcmp``, ``bcmp`` universal | `{"rust": ...}` | `memcmp` is REQUIRED in `c/kernel.c`; a universal `forbidden` entry contradicted it and the gate's audit reported the hit | **narrows** nothing measured; it scopes an entry that was self-contradictory |
| `forbidden` | had ``any(``, ``all(``, ``ct_eq`` | removed | prose-only tokens that pinned nothing and would fire on unrelated code | no cell moved |
| ~~`collapse.note`~~ | ~~window bytes~~ | ~~byte comparisons~~ | ⚠ **THIS ROW WAS FALSE. The edit it describes was never made.** See below. | — |

**No `required` or `forbidden` entry was added, removed or reworded in order to
admit a cell that had been measured.** The two `forbidden` edits both *reduce*
what is excluded and neither was made after measuring a cell that violated it —
`memcmp` was in `c/kernel.c` from the first draft, which is what made the
universal entry wrong on the first gate run, before any `Ir` was taken.

### 12a. ⚠ The fifth row of that table was a FALSE DISCLOSURE, and that is worse than the stale pin it described

TASK_064_REVIEW major 3. As shipped at `e6e86fc`, the `collapse.note` pin inside
the hashed block **still carried the pre-repair text verbatim**, both numbers
included —

```
$ git show e6e86fc:patterns/p47-ct-compare/spec.md | grep -o 'work_per_call is [^-]*-- .\{0,60\}'
work_per_call is **bytes of the window** -- `stride`, 200 on small and 1032 on large -- which is
```

— against a measured `work_per_call` of **96 and 512 byte comparisons**
(`python3 model.py inputs/small.bin inputs/large.bin`). The denominator repair
of §3 landed in `model.py` and in this file and **not** in the contract. The
same staleness was in `model.py:10-11`'s own header, against `model.py:224-278`
which return `"byte comparison"` and `ncmp*tlen`.

**And the row above claimed it had been changed.** p47 lands in exactly one
commit, so this disclosure table *is* the snapshot a reviewer has instead of a
pre-edit tree — and one of its five rows described an edit the tree did not
contain. **A false disclosure is worse than the stale note it describes**,
because the disclosure is precisely what a reader trusts *instead of*
re-checking. The concrete failure it invites is the audit §3 exists to invite: a
reader checks the contract, reads "window bytes, 200 and 1032", recomputes
`(606−434)/(1032−200) = 0.207 < 0.25`, and concludes the gate is passing a floor
the kernel fails.

**Both are now fixed and the contract hash moved** (see the top of this file).
The rule I would write down from it: *a disclosure row is a claim about the
tree and must be checked against `git show`, not against intent.* One command
would have caught it —

```
git show HEAD:patterns/p47-ct-compare/spec.md | grep -c 'bytes of the window'
```

**Pins that moved at TASK_065, and why** — the second disclosure, made the way
the first should have been, each row verified against `git diff` on the block:

| pin | from | to | why | direction |
|---|---|---|---|---|
| `collapse.note` | ``stride``, 200 / 1032 window bytes | ``ncmp * tlen``, 96 / 512 byte comparisons | the edit the row above **claimed** had been made; §3's repair, now in the contract | **describes** the floor already in force; no published `Ir` figure moves, no cell is admitted or excluded, and the recorded `collapse_tightest_margin` 2.93× is unchanged |
| `obligations_note` | *"`main` 5, not the 4 that ten patterns record"* | *"`main` 5, which every pattern recording the term records"* | the comparison was **backwards**; measured (§2) | corrects a *wrong* claim about **other** patterns; p47's own pinned total 12 and its `main` term 5 both unchanged |

⚠ **The direction test on both rows passes trivially and it should still be
stated rather than assumed**: neither pin decides admission of any cell, neither
moves a published figure, and both replace text that was false when written with
text that is measured. The *first* row is nonetheless a declaration edit made
after a measurement, which is exactly what `.memory/01-ladder.md`'s direction
test governs — the reason it is safe is that the pin it corrects had **no** effect
on the gate run (`check.py` reads `collapse.probe_inputs` and
`collapse.probe_iters`, never `collapse.note`), so the shipped record and the
corrected record are the same record.

---

## 13. Two defects found in ported machinery, reported not fixed

1. ⚠ **`patterns/p27-handle-table/controls/clayout.py:67` writes its layout
   population into `.temp/p14/clay`** — p14's scratch directory — and
   `patterns/p14-field-split/controls/clayout.py` writes there too. Running the
   p47 port unchanged **overwrote `.temp/p14/clay/meta.json`** while the older
   `layout_small_*.json` survived beside it, which is exactly the
   stale-population hazard `.memory/03-measurement.md` records ("a
   whole-program marginal figure can be a function of the SCRATCH DIRECTORY")
   and which p27's own docstring warns about two paragraphs above the constant.
   Nothing committed was harmed (`.temp/` is gitignored and re-derivable).
   **p47's copy uses `.temp/p47/clay`; p27's and p14's are NOT edited** — a
   subagent does not touch another pattern.
2. ⚠ **p27's `clayout.py --modes` hard-codes the `unsafe`/`verus` pair** and
   raises `KeyError` / `ZeroDivisionError` on any population that is not that
   pair or that has an empty mode group. p47's copy parameterises it over
   `CELLS`; the two edits are marked in the source.

---

## 14. What is NOT established

- **No `large.bin` wall-clock figure**, for the reason in §11.
- **No branch-misprediction measurement.** `perf_event_paranoid = 3`. p07's
  `callgrind --branch-sim=yes` route was not used here because p47's rungs are
  branchless in the tag loop by construction, so a branch-miss column would be
  measuring the driver.
- **The `R3 − R4` law's scalar-tail column is NOT identifiable** from this
  design (§8a). "No law exists outside `tlen ≡ 0 mod 32`" is *not* claimed;
  "not identifiable here" is.
- **The `u_win` −24.000 is not fully attributed** (§8e).
- **The domain list of §5 is not claimed closed.** Five parameters are named as
  unswept; p10 went 3 → 4 → 6 and said the same thing one round too early.
- **`Ir` is not time**, and p47 leans on `Ir` harder than any other pattern
  here. What licenses that is not that `Ir` approximates time — it is that
  **`Ir` is a deterministic function of the input, and a leak is exactly a
  dependence of a resource on a secret**. A rung whose `Ir` is constant in `k`
  is not thereby constant-*time* on real hardware: cache and port pressure are
  unmeasured, and `.memory/03-measurement.md`'s `rep`-string and `div` entries
  are two named cases where `Ir` and cycles part company (neither applies here,
  §0d). **`Ir(k)` constant is a necessary condition that p47 measures exactly,
  not a sufficient one.** The five constant-time rungs are also branchless and
  data-independent in their *addresses* — every one reads all `2·tlen` bytes in
  order — which is the other half of the usual argument, and it is read off the
  disassembly in §1a rather than assumed.
- **No `Ir` figure exists for any `-march=native` build on this box at all** —
  §16, and it is a property of the instrument rather than of p47.

---

## 15. The p27 correction, and why it landed out of p47's task

§2 found `main 4` in `patterns/p27-handle-table/spec.md`, wrong by p27's own
arithmetic. TASK_065 fixed it there rather than reporting it, because the
alternative was leaving a pin the tree can prove false in the layer this project
calls authoritative. **Exactly two lines of p27's `spec.md` changed** — the
`obligations_note` pin and the prose pin-table row that restates it — and its
generator `controls/mkspec.py` carries the same correction, which matters here
for the same reason §6a does: p27's `spec.md` **is generated**, so a fix applied
to the artefact alone would be silently reverted by the documented regeneration
command. Verified before editing that `python3
patterns/p27-handle-table/controls/mkspec.py` reproduced p27's committed
`spec.md` **byte for byte**, so the generator and the artefact were in sync
before the edit and are in sync after it.

p27's `contract_sha256` moves
`01e2137f…` → `c84673e1…`. **The disclosure with its byte-provable undo is in
p27's own `NOTES.md`**, beside the four earlier moves of the same hash, because
that is where a p27 reader looks. Nothing else of p27's was touched — not its
sources, not its other controls, not its inputs, not its measured figures — and
its gate is re-run green below.

⚠ **What is NOT fixed, and is reported rather than chased**: §13's two ported-
machinery defects are still open in p27 and p14, and TASK_064_REVIEW added a
third observation about the first of them — **p27's own published layout
population was produced while its control wrote into p14's directory**, before
`915bb8a` repointed it. p27's CONTROL 1 (single-valued `n_fn`/`md5_fn_norel`
per cell) would have caught a foreign binary — p14's kernel is `n_fn 185` — so
p27's figures are protected by its own control rather than by luck, but nobody
has re-run that population.

---

## 16. A MEASURABILITY LIMIT, not a defect: `Ir` does not exist for `-march=native` on this box

**valgrind 3.27.1 cannot decode the EVEX encodings this box's compilers emit for
Cascade Lake, so `Ir(k)` — p47's entire instrument — is unobtainable for an
AVX-512 build.** `.memory/02-bench-rules.md:224-229` says *"Nothing on this box
builds with `-march`, so it is not live — but a pattern that adds one must
re-argue ALPHA."* **It should also say the figure cannot be taken at all**,
which is a harder constraint and a cheaper one to check than re-arguing a
constant.

Measured, on p47's own rungs (`.temp/p47c/native/mknative.sh` rebuilds all of
it; `native-probe.log` is the output):

| build | `small.bin` | `large.bin` | `adversarial-k000.bin` |
|---|---|---|---|
| gcc 13.3 `-march=native`, `c/kernel_hardened.c` | **SIGILL** | **SIGILL** | **SIGILL** |
| clang 22.1 `-march=native`, same source | 7 375 287 Ir | 2 472 414 Ir | **SIGILL** |
| rustc 1.97 `-C target-cpu=native`, `unsafe.rs` | 6 933 473 Ir | **SIGILL** | **SIGILL** |

```
vex amd64->IR: unhandled instruction bytes: 0x62 0xF1 0x7F 0x28 0x6F 0x1C 0x2 ...
valgrind: Unrecognised instruction at address 0x4001ac0.
Process terminating with default action of signal 4 (SIGILL)
```

`0x62` is the EVEX prefix; the failing opcodes are `vmovdqu8`/`vmovdqu64` under
gcc and `vpternlogd` under clang and rustc.

⚠ **And the shape is worse than "it does not run", which is why it is worth
recording precisely rather than as a slogan: 7 of the 9 cells die and 3 survive,
and WHICH ones is a function of the INPUT.** The EVEX instruction sits on the
widest vectorised path, which only some `tlen` reach — `small.bin` is `tlen` 24,
`large.bin` 64, `adversarial-k000` 128 — so a `-march=native` build can hand
back a plausible `Ir` on one blob and SIGILL on the next. **A partial table
would look complete.** Anything reported from such a build must name the blob
and say the rest could not be taken.

This also strengthens §3a independently of the argument there: at AVX-512 the
window-byte rate is 0.043, so a 0.25-per-window-byte floor would have had to
move regardless of which unit p47 chose.
