# TASK_033_REVIEW — report

Reviewer's return message, recorded by the manager. Scratch `.temp/r33/`:
`NOTES.md`, `marginal.py`, `ctrl_marginal.py`, `mcprobe.c`, and the three probe
sources `u_noqguard.rs`, `r2_noqguard.rs`, `r4_swar_twin.rs`.

**Verdict: the headline decomposition HOLDS. No blockers. Two majors and six
minors against the prose.** Everything below is the reviewer's own re-measurement,
not a re-read of `.temp/p11/`.

## The headline, confirmed

**A 12× C win that is a library difference, a 5.3× Rust-vs-Rust spread, and a
3.00000 Ir/byte safety cost.** Every term is exact and every term is what
`NOTES.md` says it is.

`3.00000` is at **matched spelling** — the two loop bodies differ by exactly three
instructions:

```
safe_naive SCAN  9 insns          unsafe SCAN  6 insns
  lea    (%rdx,%rbx,1),%r14   <-- materialise off+q
  cmp    %rsi,%r14            <-- vs buf.len()
  jae    <panic>
  cmpb   $0x0,(%r10,%rbx,1)     cmpb   $0x0,(%r8,%r11,1)
  sete   %bpl                   sete   %bpl
  je     <exit>                 je     <exit>
  inc    %rbx                   inc    %r11
  cmp    %rbx,%rcx              cmp    %r11,%rcx
  jne    <top>                  jne    <top>
```

**The mechanism is the induction variable, exactly as claimed** — not the loop
shape, not the `jae` target. `safe_naive`'s fold has `add %rdx,%rax` hoisted
*outside* the loop, so the fold's bound test is `cmp; jae` = 2; the scan's `%rbx`
is window-relative because its own exit test is `q < len`, so the check must `lea`
first = 3. Confirmed by a one-loop-at-a-time control the engineer built and never
reported:

```
sweep-len24k24.bin  R2-R4= 3921.00  scan= 1850.00 fold= 2110.00 sum= 3960.00 interaction= -39.00
sweep-len64k24.bin  R2-R4=10881.00  scan= 4730.00 fold= 6190.00 sum=10920.00 interaction= -39.00
```

`(4730−1850)/(24·40) = 3.00000` and `(6190−2110)/(24·40) = 4.25000`, both exact,
residual a **constant** −39/call.

`4.25 = 2.00 + 2.25`: fold bodies are R2 **10**, R4 rolled remainder **8**, R4
4×-unrolled **23/4 = 5.75**. Split reproduced.

`12.0×`: glibc's AVX2 loop at `libc+0x18b880` is the 10 instructions over 128
bytes `NOTES` quotes; independent callgrind gives **330,616 Ir / 4,194,304 B =
0.0788/byte**. `core::slice::memchr` inlined at `0x4f340` is 15 instructions over
16 bytes, SWAR on two `u64`, **no xmm/ymm**, gated by `cmp $0xf,%rsi; ja`.
`5.3×`: `r3_position`/`r3_takewhile` scan loops are 5 instructions.

## Clean negatives — do not re-run

- **The `Ir`-column trap does not land.** No sentence in `NOTES.md`, `README.md`
  or `spec.md` reads the wrong column. Every kernel-exclusive figure (12546,
  11375, 13747, 12761, 13302, 24558, 19070, 25657, 50160) occurs **exactly once**,
  inside §3's correction table. `README.md` contains no `Ir` number at all.
- **All 16 §3 marginals reproduce to the last digit**, and all 12 of §10a/§10b's
  control figures.
- **Verus**: `12 verified, 0 errors`; `1+1+1+4+5 = 12` per `--verify-function`.
  Twin 13. `r4_forfold_twin` 12/0 **and byte-identical** (`md5_fn 9145e57079d2`).
  `r4_ptr_twin` rejects on raw pointers; `r4_cstr_twin` rejects with **exactly 4**
  `is not supported`. `m1` 12/0 shipped and fails only under `--cfg slb_twin`;
  `m2` 10/2 on `decreases`; `m3` 11/1 on `get_unchecked`.
- **The SWAR-R4 question is now measured, not "likely"** — a new twin gives
  `error: core::num::impl&%9::from_le_bytes is not supported`. All three routes
  closed, and `from_le_bytes` is *separately* forbidden by p11's own
  `idiom.forbidden[1]`. §10b's "likely is not measured" can be retired.
- **Wall clock, reviewer's own `order.py`**: floors 1.03–1.88%; blocked and
  alternating agree to **0.04 and 0.06 points** — p11 is protocol-insensitive,
  confirmed independently. `analyze.py` reproduces §11b/§11c to the digit.
- **Gate `PASS`**; diffing 178 `ok` lines against the engineer's log yields **two**
  differences, both an ASan PID. Adversarial table and ASan reproduce exactly.

## major 1 — `if q >= len { break; }` is NOT free. It costs 1.00000 Ir per scanned byte, 8.5% of R4

`verus.rs:32-34` claims "zero cost in preconditions, in driver statements and
**(measured: NOTES.md 3)** in instructions"; `NOTES.md:364` and `unsafe.rs:38` say
the same. `c/main.c:29` is the only correct one (it claims zero cost in *driver
statements and preconditions* only).

Deleting the three lines (`.temp/r33/u_noqguard.rs`; checksums unchanged on every
input):

```
static   kernel 123 -> 114 insns (nopad 117 -> 109), md5_fn 9145e57079d2 -> 54f39868dbf4
scan     6 insns (cmpb sete je inc cmp jne)  ->  5 (cmpb je inc cmp jne)
marginal small  19084.00 -> 17481.00   (+1603.00 = +8.4% of R4)
marginal large  50174.00 -> 45909.00   (+4265.00 = +8.5% of R4)
   L    u_baseline   u_noqguard  guard cost  scanned B  per byte
   8       3329.00      3040.00      289.00        216    1.3380
  16       5585.00      5104.00      481.00        408    1.1789
  24       7841.00      7168.00      673.00        600    1.1217
  64      19121.00     17488.00     1633.00       1560    1.0468
```

**Exact law, zero residual, four points: `guard = 24·L + 97` at `k=24` =
1.00000 Ir per scanned byte + 3 per string + 1 per call.** Cross-check on `large`:
4100 + 41 scanned bytes + 3·41 + 1 = **4265**, measured **4265**.

**Mechanism**: with the guard the scan loop must carry its *exit reason* out in a
register — the `sete %bpl` exists only so the post-loop `test %bpl,%bpl; je` can
implement `if q >= len`. Without it the loop falls through and the `sete`
disappears. **The C rungs do not pay this per byte** (their scan is a libcall that
already returns the length), so of R4's 6.00000 Ir/byte scan, **1.00000 is
shared-idiom bookkeeping that `strlen`/`memchr` get for free**.

*Failure scenario*: the project publishes "p11 discharged the overflow obligation
for free where p17 had to buy a second `requires`", and p12–p15 copy the pattern.
**The real trade is 8.5% of the kernel instead of a precondition** — which is a
more interesting result than the one currently written.

**Clean negative attached**: this does **not** contaminate the 3.00000. Without
the guard the loops are 8 and 5; the difference is `lea;cmp;jae` either way.

## major 2 — the `adversarial-count` / `zerotail` pair differs in 33 bytes, not 20

`NOTES.md:556-558` and `inputs/gen.py:252` say "identical first three strings;
they differ in **20 tail bytes and nothing else**". Measured:

```
n differing bytes: 33
indices: [28,29,30,31, 33,34,35,36,37,38, 40,41,42, 44..63]
a payload: 00100000 8d6df4cd 00 1357338d5973 00 2b49f9 00 <20 non-zero>
b payload: 00100000 a8f6fe93 00 8775cbc8f598 00 c12408 00 <20 NUL>
```

The three strings share their **lengths** (4/6/3) and terminator positions but not
their bytes, because `gen.py:341` and `:347` each call `strings(rng, …)` on the
same sequentially-advancing RNG. **The conclusion survives** — string content
cannot change whether `strlen` runs off the end, and `count` overruns while
`zerotail` is clean in all 8 cells — but the sentence that upgrades this from a
remark to "a controlled comparison" is false about the shipped tree, and `cmp`
finds it in ten seconds. One-line fix: build `body` once and reuse it.

## minor 3 — the shipped table tells the reader to do exactly what §3 forbids

`results/tables/p11-nul-scan.md:100`, from `harness/report.py:483`: *"Use the
`isolated` kernel-exclusive figure, which needs no correction."* On p11 that
column is off by 9830 Ir/call and **inverts the R3-vs-R4 sign**. Pre-existing
boilerplate, **false on p02 too**. A reader who follows the table's own
instruction gets the sign backwards.

## minor 4 — glibc `memchr` is not 0.078125 Ir/byte

`NOTES.md:85` puts "R1, and **R1h's `memchr`**" on the 0.078125 row. Measured:
429,184 Ir at `libc+0x188080` over 4,194,304 B = **0.1023 Ir/byte**, 31% dearer
than `strlen`'s 0.0788 — the same fact §3(3) already states in prose ("`memchr`
must also test its count"). Both are AVX2, so the qualitative claim stands;
nothing in the decomposition rests on the rate.

## minor 5 — stale line citations, all +2, from a `verus.rs` edit after the logs were pasted

`NOTES.md:471` (252 → 254), `:500` (333 → 335), `:525` (346 → 348), `:382`
(`external_body` 202/251/263 → 204/253/265), and `NOTES.md:546` + `README.md:63`
(ASan frame `kernel.c:65` → `:68`). Verdicts and counts all correct.

## minor 6 — "four `(loop, property)` pairs" is seven

`NOTES.md:846-849`; `analyze.py` reports seven (it misses `loop0 jcc32[1,4]`,
`loop1 jcc32[0,1]`, `loop2 jcc32[0,1]`), in two opposite orientations (`×0.9399`
and `×1.0640` — the same partition read both ways). The conclusion ("the
population identifies the mode, not the loop") is **strengthened**.

## minor 7 — `−6.00000` and `−3.75000` are fitted, not read off a listing

`NOTES.md:291-292`, against the file's own opening rule. Per residue class the
slopes give −5.99563…−6.00219 and −3.74563…−3.75219. The claim is true and
corroborated to 0.04%; the five-decimal *presentation* of a fit is the defect.
Same section's c-gcc intercept range "−60 … −170" is really +39 … −170.

## minor 8 — "the token `slb_twin` occurs in this file exactly once" — it occurs twice

`NOTES.md:419-421`, a **hashed** `SLB-TRUSTED-ARGUMENT` clause. `grep -o` gives
line 233 (a comment) and 235 (the attribute). A comment cannot change codegen, so
argument (c) survives intact.

## Unsure / not done

- **No blockers.** Nothing invalidates a published p11 number. Major 1 does not
  distort any rung comparison, because `if q >= len` is in `idiom.required` for
  all six rungs and every cell pays it.
- Did not re-run the 31-layout population — re-analysed the stored
  `.temp/layout/layout_p11.json` and ran `order.py` fresh, per the task.
- Did not build the *exec* SWAR R4 to price it, only the twin — it is doubly
  inadmissible (unsupported **and** forbidden), so the number would describe
  nothing.
- **`check.py p11` rewrites the gate JSON with a fresh ASan PID, so a gate record
  can never reproduce byte-identically.** Affects 6 of 8 patterns
  (`grep -c '==[0-9]*==ERROR' results/gate/*.json`).

## Memory updates

None — reviewers do not write `.memory/`. Recommended:

1. `.memory/01-ladder.md` — **the 3.00000/2.00000 pair with its mechanism**: a
   bounds check costs 2 Ir/byte when the loop's induction variable already holds
   the address being checked and 3 when it does not; which one you get is decided
   by the *other* test in the loop.
2. `.memory/01-ladder.md` finding 4 — **4.25 = 2.00 + 2.25 confirmed on a third
   kernel including the split**, now by a one-loop-at-a-time control rather than a
   whole-kernel delta.
3. `.memory/01-ladder.md`, R4-by-permission — **p11 is the largest instance**:
   17,526 Ir/call, 35% of the kernel on `large`, and the SWAR alternative is now
   *measured* inadmissible.
4. `.memory/03-measurement.md` — **separate the safety cost from the library cost
   by naming the routine**, with p11's three-way split as the worked example, plus
   `memchr` = 0.1023 against `strlen`'s 0.0788.
5. `.memory/04-verus.md` — **a proof-enabling program change is not automatically
   free**: p11's guard removes an overflow obligation at zero preconditions and
   zero driver statements but costs **1.00000 Ir per scanned byte, 8.5% of R4**.
   p17 bought the same fact with a precondition at zero instructions. **That is
   the trade.**
