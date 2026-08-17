# TASK_007_REVIEW — report

**Verdict on `.memory/01-ladder.md` finding 4: it OVERCLAIMS — narrowly, and not
where I expected.** The 4.25 Ir/byte is real, the decomposition is sound, and the
2.00-check / 2.25-unroll split is now **confirmed by construction** (§1.1, the
rolled-vs-rolled control, landed at exactly 2.0000 in both bands). What
overclaims is the *headline*: R3's marginal rate is **5.7500, identical to R4's
to four decimals**, so idiomatic safe Rust has **zero** per-byte cost on p16.
The thing that is O(n) is one naive spelling, not safety — and
`.memory/01-ladder.md`'s own rule ("Never publish a safety-cost claim without
R3") makes R3 the safety-cost number. Two further sub-claims are checkably wrong
(the 32-cell `vector_regs` count; the cycle arithmetic).

No blockers. The result survives publication if four sentences are rewritten.

Everything below was re-measured by me; nothing is taken from the engineer's
report. Scratch, binaries and scripts: `.temp/review007/`. `results/gate/` was
not touched (I never ran `check.py`); `git status` at exit shows only this file
and `.tasks/TASK_007_REVIEW.md`.

---

## 1. Part 1 — is the +4.25 real, and is the cause right?

### 1.1 The rolled-vs-rolled control — **the attribution is confirmed**

`-C llvm-args=-unroll-count=1` forces R4's value fold to stay rolled. Two
properties make it a clean intervention rather than a confound:

* the flag is a **no-op on R2** — `r2-base` and `r2-uc1` are identical
  instruction-for-instruction (only branch addresses differ), and their measured
  `Ir` agrees to 0.1 at every sweep point. So the flag changes only R4.
* after rolling, `r4-uc1`'s kernel differs from `r2-uc1`'s **only** by
  `cmp %rax,%rsi ; je <panic>` inside the fold (plus the per-record header
  checks, which are not per-byte). Even the u16 length load converges on the
  same `movzwl`.

Marginal `Ir` per folded byte, lag-32 differencing (so both endpoints share a
residue mod 4, 8, 16), my own callgrind runs:

| | band A (vlen 56→88, 4 rec/win) | band B (vlen 2040→2072, 2 rec/win) |
|---|---:|---:|
| R2 (rolled, checked) | **10.0000** | **10.0000** |
| R2 with `-unroll-count=1` | 10.0000 | 10.0000 |
| R4 as shipped (4× unrolled, unchecked) | **5.7500** | **5.7500** |
| **R4 rolled (`-unroll-count=1`), unchecked** | **8.0000** | **8.0000** |
| **gap R2 − R4rolled** | **2.0000** | **2.0000** |

`4.2500 = 2.0000 + 2.2500` with **zero residual**, at two scales 18× apart.
The 2.25 is not a bucket; both legs are separately measured.

The static reading is in fact **stronger than `NOTES.md` states**, and the file
misses its own best evidence: **R4's own remainder loop is the rolled-unchecked
reference, sitting in the shipped binary** —
`mov, shl $0x5, sub, movzbl, add, inc, dec, jne` = 8 insns/byte, which is R2's
10-instruction body minus exactly `cmp`+`je`. Two more independent sightings of
the same 8.00 constant: gcc's `-O3` fold body (8 insns/byte, rolled) and, in
R4's dynamic sweep, the mod-4 sawtooth (+12, +8, +8, −5 per record per byte) —
the +8 steps *are* the remainder loop, and 12 = 8 + a 4-instruction remainder
setup. Four sightings, one number.

### 1.2 The one thing that does not survive: the counterfactual gloss

`NOTES.md:280` labels the 2.25 "loop overhead the 4× unroll **would have
amortised**". That reads as a counterfactual and the counterfactual is false.
LLVM *can* unroll the checked loop; it just does not by default because runtime
multi-exit unrolling is off. Forcing it:

```
-C llvm-args=-unroll-runtime -C llvm-args=-unroll-runtime-multi-exit
-C llvm-args=-unroll-count=4     →  9.5000 Ir/byte   (not 7.75)
```

Body = 38 insns / 4 bytes. The four exit tests cost `mov, or, cmp, je` = **15
instructions (3.75/byte)**, because LLVM cannot fold four multi-exit tests into
one induction comparison. So unrolling the *checked* loop recovers **0.50**, not
2.25 — the 2.25 is the unroll benefit an *unchecked* loop gets. The split is
therefore **path-dependent**: via (rolled-unchecked) it is 2.00 + 2.25; via
(unrolled-checked) it is 0.50 + 3.75. `NOTES.md`'s decomposition is the right one
to quote and its arithmetic is exact, but "would have amortised" must become
"that an unchecked loop gets and a checked one does not".

The headline sentence — *"more than half the cost of the bounds check is not the
check, it is the optimisation the check forecloses"* — **survives**, and this
measurement strengthens the word *forecloses*: the optimisation is not merely
un-applied, it is not worth applying once the check is in the loop.

### 1.3 `shl $0x5` site counting is **not** independent corroboration

7 = 1 (tag) + 4 (unrolled body) + 1 (remainder) + 1 (epilogue); 3 = 1 + 1 + 1.
The count is a re-reading of the unroll factor off the same disassembly that
produced 23/4 and 10/1. It is independent of the *timing*, but it carries
**zero** information about the 2.00 — it says nothing about the check at all.
Its real value is as a cheap classifier: it confirms the rolled/unrolled
partition across all 8 variants without re-reading eight disassemblies. Restate
it as that.

### 1.4 10.00 and 5.75 are measured, not fitted — verified

Re-derived from raw callgrind by me (`.temp/review007/ctl.py`, my own builds, the
engineer's probe inputs), reproducing his `sweep.json` to the instruction
(v56: R2 2375.0, R3 1473.0, R4 1446.0).

* **R2 is exactly linear**: least-squares over all 34 points/band gives slope
  **10.0000** with **residual identically 0.00** in both bands. Every lag-1
  marginal is 10.0 — no sawtooth at any residue.
* **R4 is 5.7613 with a mod-4 sawtooth** whose cycle sums to 23 per 4 bytes;
  lag-32 differencing removes it exactly, giving 5.7500. `NOTES.md` is right to
  quote the lag-32 figure and right about which modulus matters.
* Caveat worth recording: the lag-32 marginal has only **n = 2 pairs per band**
  (34 points, lag 32). It is exact, but "68 consecutive lengths" describes the
  linearity evidence, not the marginal-rate estimator. Both are fine; they are
  different claims.

### 1.5 The `Ir`-per-byte denominator is right, and does not manufacture 4.25

"Folded bytes" = `nrec · (1 + vlen)` — the tag plus the value, correctly
excluding the two length bytes and the `nrec` fold. Proof by reconstruction:
fitting R2 over the two bands gives

```
R2(Ir/call) = 10·folded + 21·nrec + 11
```

which reproduces **both shipped numbers exactly**:
`small` 10·500 + 21·4 + 11 = **5095** (measured 5095.0);
`large` 10·4070 + 21·10 + 11 = **40921** (measured 40921.0).
Using `stride` instead (508 / 4090) would move the *averages* 4.17→4.10 and
4.21→4.19 — a 2% wobble, not a manufactured 4.25. The 4.25 is marginal and
denominator-free by construction.

---

## 2. Part 2 — the wall-clock null

**It is measured well enough to state, and the shipped statement of it is worse
than the data deserves.**

* **Spread**: `(median−min)/min` per cell is **0.96 %…2.31 %** across all 16 O3
  cells (`results/p16-tlv-walk.json`), i.e. nowhere near
  `.memory/06-catalogue.md`'s 10 % discard threshold. The between-cell range
  (1.26 % on `small`, 0.90 % on `large`) is *smaller* than the within-cell noise.
  So the honest statement is "equal to within ~1.4 %, our resolution" — and the
  effect being denied is +70 %, i.e. **50× the resolution**. The null is solid.
* `NOTES.md:167` "R2 … is, **if anything, marginally faster**" reads 0.5 % of a
  1.4 % noise band as signal. Drop it.

**The cycle arithmetic does not reconcile as written (major).**
`NOTES.md:173-175`: "4070 bytes × 3 cycles × 20 000 calls ≈ 244 M cycles ≈ 74 ms
at this box's observed turbo" implies **3.30 GHz**. Two errors:

1. CPU 5 under load runs at **3.85 GHz**, not 3.3 (measured:
   `.temp/review007/calib.c`, a 1-cycle serial `add` chain, 2 × 10⁹ iterations →
   3.652 / 3.859 / 3.851 GHz over three runs; `cpuinfo_max_freq` 3.9 GHz).
2. **13 % of the quoted 74 ms is not the kernel.** With `n_iters` rewritten to 0,
   `large` still takes **9.4 ms** (process start + reading the 8.4 MB file);
   `small`'s fixed cost is **2.7 ms of 12.7 ms = 21 %**.

They cancel. Corrected: (74.07 − 9.41) ms × 3.85 GHz / 81.4 MB = **3.06
cycles/byte**. The conclusion is right; the arithmetic that reaches it is not,
and neither input to the fix is in the file.

**The right measurement, which also answers the bandwidth question.**
Differencing two `n_iters` (`.temp/review007/wall.py`, min of 15, `taskset -c 5`)
removes startup, file I/O and the turbo ramp:

| rung | `large` cyc/byte | `small` cyc/byte |
|---|---:|---:|
| c-gcc | 3.051 | 2.670* |
| c-clang | 3.029 | 3.080 |
| **safe_naive** | **3.035** | **3.055** |
| safe_tuned | 3.046 | 3.035 |
| **unsafe** | **3.027** | **3.056** |
| verus | 3.046 | 3.074 |

\* c-gcc's `small` point is unstable across the two `n_iters`; its `large` figure
is clean.

Marginal R2−R4: **+0.27 % on `large`, −0.03 % on `small`**, against +72 % / +69 %
in `Ir`. The Horner-latency explanation is **confirmed at 3.03–3.08 cycles/byte**,
which is the floor of the chain (`shl`→`sub`→`add`, 3 cycles), for every rung.

**The second explanation is ruled out, and the two inputs do discriminate.**
`small` is L1-resident (16 KB blob), `large` is 8.4 MB — L3-resident, not L2. A
bandwidth-bound `large` would show a *higher* cycles/byte than `small`; it shows
**3.03 vs 3.06**, i.e. the same. At 3.85 GHz, 3.03 cyc/byte is 1.27 GB/s, orders
below L3 bandwidth. The kernel is latency-bound on both, and the write-up's
single explanation is the right one.

---

## 3. Part 3 — pattern validity

**Semantic equivalence: holds, and I pushed it well past the shipped corpus.**
`.temp/review007/fuzz.py` — **210 random record chains** (seeds 20260817 / 424242)
containing zero-length values, over-declared lengths, 1–2-byte truncated tails,
one-record windows, strides 3…1024 — run through **12 binaries** (R1h-gcc,
R1h-clang, R2, R3, R4, R5 × O3 and O0, isolated) and compared to `model.py`
(whose own two-implementation `selfcheck` was asserted on every case):
**0 mismatches**. The three shipped adversarial inputs also agree across all
eight cells. No rung folds a different set of bytes.

**R2 is a fair naive port — not a strawman. This was my main attack and it
failed.** Four other spellings a working Rust programmer might write, walk held
identical to R2's, marginal Ir/byte (band A, lag 32):

| spelling | Ir/byte |
|---|---:|
| R2 as shipped (`for j in 0..vlen`, `buf[p+3+j]`) | 10.0000 |
| `while j < vlen` (the literal C transliteration) | 10.0000 |
| `for j in p+3..p+3+vlen`, `buf[j]` | 10.0000 |
| `buf.iter().skip(p+3).take(vlen)` | **11.0000** |
| `buf.get(p+3+j).unwrap_or(&0)` | **11.0000** |
| `let v = &buf[p+3..p+3+vlen]; v[j]` (one reslice) | **5.7500** |

R2 is tied-cheapest of the five naive spellings; two plausible ones are *worse*.
The cliff is the reslice and nothing else — which is exactly `NOTES.md` §3's
variant-3 point, now with four more data points.

**R3 does not restore unsafety and does not change the algorithm.** Zero `unsafe`
tokens; both `&buf[p..p+3]` and `&buf[p+3..p+3+vlen]` are checked slicing; it is
fuzz-equivalent to every other rung. Its cost is O(records) and **0 per byte**
(marginal 5.7500 = R4's), i.e. 0.90 % of the call on `small` and 0.32 % on
`large` — a fraction that *shrinks* with input size. That is the opposite of an
O(n) tax and it is why §0's framing is the problem (finding F1).

**The C rung is idiomatic C99** — `c/kernel.c` is 12 lines of the obvious walk.

**gcc-vs-clang: a real codegen difference, but a *default-flag* one (minor).**
Not a fortify or stack-protector artefact — `Ir/call` is **4062.0 unchanged**
under `-D_FORTIFY_SOURCE=0 -fno-stack-protector` (this kernel calls no fortified
function). gcc's fold body is genuinely rolled at 8 insns/byte. But adding
`-funroll-loops` gives gcc **2823.0**, i.e. **better than clang's 2993.0**. So
"gcc is 36 % dearer" is a statement about `gcc -O3`'s default unrolling policy,
not about gcc. Worth one clause, because `NOTES.md:146-149` uses the gap to argue
what a "same-backend comparison" is worth.

**The `7 + 7·nrec` fit is half a prediction (minor).** Per residue class the fit
has 2 free parameters and exactly 2 distinct `nrec` values (band A = 4, band B =
2): it is exact interpolation with zero degrees of freedom.
`small` has **nrec = 4 and vlen ≡ 0 (mod 4) — one of the two fitted
configurations**, so 27 is in-sample in `nrec` (it does test "nothing per byte",
since vlen moves 56→124). `large`'s nrec = 10 is a genuine 2.5× extrapolation and
77 is a real prediction. "predicts both shipped numbers without being fitted to
them" overstates by half.

---

## 4. Part 4 — the security half

**"Unbounded walk", not "reads past the end": CONFIRMED, and demonstrated rather
than argued.** `.temp/review007/unbounded.c` runs `c/kernel.c`'s loop verbatim
over the shipped `adversarial-overrun` blob placed at the head of a 256 MiB
mapping, with the loop condition instrumented:

```
blob_len=3072  end=3072
  p=7107 is PAST end=3072; end - p = 18446744073709547581 (0xfffffffffffff03d)
      -- loop test `end - p >= 3` is STILL TRUE
  p=32879  ... 0xffffffffffff8b91 ... STILL TRUE
  p=88132  ... 0xfffffffffffeb3bc ... STILL TRUE
REACHED CAP: walked 209716767 bytes (200.0 MiB) past the end of the window,
6459 records, and the kernel never terminated.
```

Only my 200 MiB cap stopped it. The analytic argument is airtight too: `p` is
monotone increasing (`p += 3 + vlen ≥ 3`), so once `p > end` the exit condition
`end − p ∈ {0,1,2}` is unreachable short of a 2⁶⁴ wrap. Shipped R1 SIGSEGVs
(exit 139) under both gcc and clang; R1h and all four Rust rungs print
`8267139675305953920`.

**Delete-the-check controls are honest.** Reproduced all four:

| rung minus `if vlen > end - (p+3)` | result |
|---|---|
| `c/kernel.c` (= R1, shipped) | exit 139, SIGSEGV, silent |
| `nocheck-unsafe.rs` | exit 139, SIGSEGV, silent |
| `nocheck-safe_naive.rs` | **exit 101**, `index out of bounds: the len is 3072 but the index is 3072`, panicking at **`.rs:35:53` — the value fold `buf[p + 3 + j]`**, i.e. the first byte past the blob, exactly where `NOTES.md` says |
| `verus.rs` (mutant M3) | `error: invariant not satisfied before loop --> :272:17  p + 3 + vlen <= end`; `9 verified, 1 errors` |

**M1 (the off-by-one axiom) reproduces exactly.** Mutant verifies alone —
`10 verified, 0 errors` — and fails under `--cfg slb_twin` with
`precondition not met ... verus.rs:181:5 | v[i]`, `10 verified, 1 errors`. The
shipped file under `--cfg slb_twin`: `11 verified, 0 errors`, matching the pinned
obligation counts 10 / 11.

**TCB tally is accurate.** Recounted: three `external_body` items —
`get_unchecked` (1 line), `load_input` (4), `emit` (1) = **6 lines / 3 items**,
exactly one `unsafe` token in the file (`verus.rs:148`). R4 ≡ R5:
`md5_fn 852405e0fa43` at O3 (both), `md5_fn_norel 90a946a4f260` at O0 (both).

---

## 5. Findings, by severity

**No blockers.**

**F1 (major) — the headline attributes to "safety" what belongs to one spelling.**
`.memory/01-ladder.md:198-199` ("delivers the project's first real O(n) safety
cost") and `patterns/p16-tlv-walk/NOTES.md:7-12`. R3's marginal rate is
**5.7500 = R4's exactly**; idiomatic safe Rust costs **nothing per byte** on p16.
`.memory/01-ladder.md:116` is explicit: *"Never publish a safety-cost claim
without R3. Reporting R2 alone overstates safe Rust's cost by ~3.7×."* Both
documents *contain* the R3 row, but both lead with R2's +69 %.
*Failure scenario:* a reader quotes "safe Rust pays +69 % on data-dependent
walks" — the bolded sentence — and is refuted by row 3 of the same table, which
is the exact shape of the p02 retraction. Suggested restatement, which loses
nothing: *"the naive index-per-byte spelling pays 4.25 Ir/byte on a walk LLVM
cannot hoist; the idiomatic reslice spelling pays zero per byte. Safe Rust's cost
here is O(records) and 0.3–0.9 % of the call. The transferable finding is that
of the 4.25, only 2.00 is the check — 2.25 is the unroll the check forecloses."*

**F2 (major) — the cycle arithmetic does not reconcile as written.**
`NOTES.md:173-175`. Implies 3.30 GHz; the box turbos to **3.85 GHz** and 13 % of
the quoted 74 ms is not the kernel. Two errors that cancel. Corrected figure
**3.06 cycles/byte**; my marginal measurement gives **3.027–3.055** across rungs.
*Failure scenario:* the next agent re-derives it, gets 63 ms against a measured
74 ms, and concludes the latency story is wrong when it is right. Fix: quote the
marginal, and cite the 3.85 GHz measurement.

**F3 (minor) — "`vector_regs` is `[]` for every one of the 32 cells" is false.**
`NOTES.md:298-300` and `.memory/01-ladder.md:242-244`. It is `[]` in **23 of 32**;
**9** are `['xmm']` — `c-clang`, `c-clang-h`, `safe_naive`, `safe_tuned`,
`unsafe`, `verus` in `whole` mode, where the matched symbol is `main` and the
`xmm` comes from the driver's inlined loader, not the fold. The conclusion (the
fold does not vectorise) is right and no claim rests on the miscount. Restate as
"`[]` in all 16 `isolated` cells, where `kernel` is its own symbol".

**F4 (minor) — "loop overhead the 4× unroll *would have amortised*" is a false
counterfactual.** `NOTES.md:280`. Forcing the unroll on the checked loop recovers
0.50, not 2.25 (§1.2). Arithmetic of the split is exact; replace the gloss with
"that an unchecked loop gets and a checked one does not", and note that forcing
it confirms *forecloses*.

**F5 (minor) — the `shl $0x5` count is not independent corroboration of the
split.** `NOTES.md:284-288`. It re-reads the unroll factor from the same
disassembly and says nothing about the 2.00 (§1.3).

**F6 (minor) — "predicts both shipped numbers without being fitted to them"
overstates by half.** `NOTES.md:353-362`. Zero-DOF interpolation; `small`'s
nrec = 4 is one of the fitted configurations. Only `large` (nrec = 10) is
out-of-sample.

**F7 (minor) — "inlining is the one situation in which LLVM *can* see the
caller's `off + len <= buf.len()`".** `NOTES.md:203-206`. It cannot: deriving it
needs `(n/s)·s + s <= n`, nonlinear over a `udiv` — which is precisely why R5
needs `lemma_div_non_zero`, `lemma_fundamental_div_mod`, `lemma_mul_inequality`
and a `by (nonlinear_arith)` (`NOTES.md:747-750`). R2 getting *worse* in `whole`
mode is evidence LLVM did **not** derive it. The conclusion drawn from the
sentence ("bound visibility is not a sufficient explanation") loses its support
and should be dropped or re-argued.

**F8 (minor) — "if anything, marginally faster".** `NOTES.md:167`. 0.5 % inside a
1.4 % noise band. Marginal figures: +0.27 % / −0.03 %. Say "equal within ~1 %".

**F9 (minor) — the wall-clock table quotes totals that are 13 % / 21 %
non-kernel.** `NOTES.md:156-163`. The `n_iters = 0` baseline (9.4 ms / 2.7 ms)
and the marginal are both ~2 minutes of measurement and make the null stronger,
not weaker. Consider adding a marginal column here and in the recipe.

**F10 (minor, adjacent) — gcc's 36 % deficit is a default-flag difference.**
`NOTES.md:146-149`. `-funroll-loops` puts gcc at 2823 vs clang's 2993. Add the
clause; the same-backend argument is unaffected but the sentence currently reads
as a compiler-capability claim.

---

## 6. Part 5 — clean negatives (attacks that did **not** land)

1. **"R2 is pessimised into losing."** Four alternative naive spellings: two tie
   at 10.0000, two are *worse* at 11.0000, only the reslice is free. R2 is the
   fairest available naive port. Do not re-run this.
2. **"10.00 / 5.75 / 4.25 are fitted or one residue mislabelled."** R2's sweep is
   exactly linear, residual **0.00** over 34 points in each of two bands; I
   reproduced the engineer's numbers from raw callgrind with my own builds.
3. **"The 4.25 is a denominator artefact."** `10·folded + 21·nrec + 11`
   reproduces both shipped totals **to the instruction**; the marginal rate is
   denominator-free anyway.
4. **"The 2.25 is a residual bucket."** Both legs are now separately measured
   (2.0000 and 2.2500) with zero residual, at two scales.
5. **"A rung folds a different set of bytes."** 210 random adversarial chains ×
   12 binaries × `model.py`: 0 mismatches.
6. **"The wall-clock null is really memory-bandwidth on `large`."** L1-resident
   `small` and L3-resident `large` give the same 3.03–3.06 cycles/byte.
7. **"The wall-clock cells should have been discarded like p01's."** p16's
   spreads are 0.96–2.31 %, versus a 10 % threshold.
8. **"gcc's 4062 is a fortify artefact."** Byte-identical `Ir` with fortify and
   the stack protector disabled.
9. **"R3 quietly restores unsafety or changes the algorithm."** No `unsafe`,
   checked slicing, fuzz-equivalent.
10. **"The TCB tally / identity / obligation pins are wrong."** Recounted: 6
    lines, 3 items, 1 `unsafe` token; `md5_fn` equal at O3 and `md5_fn_norel`
    equal at O0; 10 obligations shipped, 11 under `--cfg slb_twin`.
11. **"The unbounded-walk claim is rhetoric."** 200 MiB / 6459 records past the
    end, `end − p = 0xfffffffffffff03d`.
12. **"M1/M3 do not reproduce."** Both reproduce with the quoted diagnostics.

## 7. Not done / residual

* **No gate run.** `check.py p16` and the mirror-pattern stages were out of scope
  per the task ("not a gate-bypass hunt"); consequently `results/gate/` is
  untouched and I have **not** independently re-verified the gate's own green
  rows (stage 3c identity beyond the digests above, Miri, stage 7 ASan). The ASan
  `heap-buffer-overflow` line in `NOTES.md` §1 was **not** re-run by me; the
  plain SIGSEGV was.
* **Verus was re-run only on the shipped file, M1 and M3.** M0 (`p += vlen`,
  §8) and M2 (trivial `ensures`, §7) were not re-run.
* `-C llvm-args` is an off-label intervention. I justified it by showing the flag
  is a bit-for-bit no-op on R2, and I only ever compare **marginal** (per-byte)
  rates — `r4-uc1`'s per-*record* constant does differ from `r4-base`'s, since
  the unroll setup disappears. Anyone re-using these binaries should keep to the
  marginal.
* The `small` marginal wall-clock for `c-gcc` is unstable between the two
  `n_iters` points; I did not chase it, and no claim rests on it.
* I did not attack `spec.md`'s pin block, `model.py`'s `work_per_call` argument,
  or `harness/` — all explicitly out of scope.
