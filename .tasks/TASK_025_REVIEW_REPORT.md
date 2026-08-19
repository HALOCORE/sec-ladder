# TASK_025_REVIEW — report

Reviewer's return message, recorded verbatim by the manager (the reviewer cannot
commit). Scratch: `.temp/r25/`. Severity ranked; the manager's landing decisions
are in `RECAP.md` and `.memory/`, and the pattern-file corrections are TASK_027.

## Did

Attacked TASK_024's §10a.2 on all eight fronts the task named, plus two the task
did not. Everything under `.temp/r25/`: `NOTES.md` (running notes),
`gen_r5_c32.py` (Verus R5 twins), `foldcmp.py` / `shipbody.py` / `mechcmp.py`
(disassembly), `gen_sweep.py` + `meas.py` + `sweepfit.py` / `sweepall.py` (the
sweep), `digits.py` (the `println` control), `gen_mech.py` (the `try_into`
control), `contract.py` (idiom entries), `marg.json` (all marginals),
`verus_v{1..4}.log`, `gate_p16.log`, `miri.log`. Rebuilt the twelve `.temp/p24/v`
probes from the surviving generator. Binaries and generated blobs deleted;
scripts, `.rs`, `.json`, `.log`, notes kept (`.temp/r25` = 316K, `.temp/p24` =
1.1M). No `git add`/`commit`; nothing under `patterns/`, `pilot/` or `.memory/`
edited; the incidental `results/gate/p16-tlv-walk.json` ASan-PID churn from the
gate run was reverted with `git checkout --`, tree clean.

## Evidence

### blocker 1 — `u_c32` cannot be a p16 R4 rung. §10a.1's own disqualification applies to it, and nobody ran it.

`patterns/p16-tlv-walk/spec.md:378` pins `identity: unsafe ≡ verus, O3 exact`, so
every R4 needs a verifying, byte-identical R5. Built that R5 (`verus.rs` with its
exec fold replaced by `u_c32`'s, verbatim):

```
=== v1 (fold transplanted verbatim) ===
error: The verifier does not yet support the following Rust feature: ref patterns
   --> verus_c32_v1.rs:275:17  |  for &x in a.iter() {

=== v4 (raw unsafe range read + indexed inner loop) ===
error: `core::slice::impl&%0::get_unchecked` is not supported
error: `core::slice::iter::ChunksExact` is not supported
error: `core::slice::impl&%0::chunks_exact` is not supported
error: `core::slice::iter::impl&%90%default%by_ref` is not supported
error: `core::array::TryFromSliceError` is not supported
error: aborting due to 5 previous errors

=== v3 (the 4th trusted item PAID: external_body get_unchecked_range) ===
error: ChunksExact / chunks_exact / by_ref / TryFromSliceError  — 4 errors
```

Shipping `u_c32` needs **five** new trusted items (a range accessor,
`assume_specification` × 2, `external_type_specification` × 2) on the pattern
whose entire memory-safety claim is *one* trusted `requires` (TCB 6 lines / 3
items). `r4_hdr` was disqualified for needing **one**. `NOTES.md:1367-1370`
audits the TCB of the *R3*-side chunked folds ("safe Rust, zero TCB") and never
audits the `u_*` side at all.

### major 2 — `−0.5625` is arithmetically wrong for the rung it names. Measured: `−0.65625`.

`NOTES.md:1607` states `5.09375 − 5.7500 = −0.5625`. That subtraction is
`−0.65625`. `−0.5625` is the **K=16** figure (`5.1875 − 5.75`), which is what
`TASK_023_REVIEW_REPORT.md:201` actually measured before TASK_024 re-pointed the
sentence at the K=32 rung. Measured directly, period-averaged at **every** residue
offset over 127 consecutive lengths:

```
cross-spelling gap vs the SHIPPED unsafe rung, period-averaged:
  u_ship - s_c16   : +0.56250 .. +0.56250 Ir/byte (n=64)
  u_ship - s_c32   : +0.65625 .. +0.65625 Ir/byte (n=96)
  u_ship - s_c64   : +0.70312 .. +0.70312 Ir/byte (n=16)
```

Independent check: `u_ship − s_c32` = 31 at `sweep-v56` and 115 at `sweep-v88`;
`(115−31)/(4·32) = 0.65625`. Sites: `NOTES.md:1605,1607`; hashed `spec.md:297`;
`.memory/01-ladder.md:393,417`; `RECAP.md:78,479`;
`results/tables/p16-tlv-walk.md:37`. *Failure scenario:* a reader reproduces the
two rates in the same table three lines above and gets a different number from
the headline in the hashed block.

### major 3 — `−199 / −2365` is not the in-contract minimum. `chunks_exact(64)` gives `−2545` at `large`, and it is in §10a.2's own rate table.

```
small.bin   s_c32=2825.30  s_c64=2897.30  u_ship=3024.30   ->  199.00 / 127.00
large.bin   s_c32=21447.30 s_c64=21267.30 u_ship=23812.30  -> 2365.00 / 2545.00
```

`s_c64` is the same one-substitution safe rung, 95/95 equivalent,
`req1=req2=True`, `forb1=forb2=False`. §10a.2 lists `chunks_exact(64)` at 5.04688
Ir/byte — cheaper per byte than the c32 row it publishes as the minimum — and
nobody differenced it at `large`. Sites: `NOTES.md:203-204,1390,1559`;
`README.md:58-59`; hashed `spec.md:297`; `.memory/01-ladder.md:392`. **Fifth
published p16/p05 "minimum" overturned by the next search**, and §10a.1's own
third bullet says it would be.

### major 4 — the "`chunks_exact(4)` is dearer" argument, one of the two legs of "why the unroll factor is NOT pinned", is an artefact of `try_into`.

`NOTES.md:1636-1638`. Built the control §10a.2 never built — the same
`chunks_exact(K)` fold with the `try_into` step removed:

```
probe      body     movzbl   rate       source
s_c4       26       3        6.50000    with try_into
s_n4       43       8        5.37500    NO try_into      (43 insns / 8 bytes)
s_c8       53       6        6.62500    with try_into
s_n8       43       8        5.37500    NO try_into
s_c16      83      16        5.18750    with try_into
s_n16      83      16        5.18750    NO try_into   <- identical
measured slope s_n4: (1749.00-1405.00)/(32*2) = 5.37500 exactly
u_ship - s_n4 = +1509 (large) / +167 (small)      <- CHEAPER, not dearer
```

The mechanism attribution to `try_into` is **confirmed** (first control run for
it); the rhetorical use of it is refuted. Chunking at K=4 is 1509 Ir/call
*cheaper* than shipped R4 at `large` once the `try_into` spelling is dropped.
"The free parameter is not a dial that only ever flatters the safe rung" rests on
the one spelling that happened to go the other way.

### major 5 — the direction test is applied with the sign inverted relative to its own recorded precedent.

`.memory/01-ladder.md:144-150` states it as a *sufficient* condition for
innocence — "an edit that **shrinks** the class and **lowers or does not raise**
the published figure is not self-certification" — and then cites as a **passing**
example "p16's exclusion makes its published tax **4.5× larger**", i.e. an
exclusion that *raised* the figure. `NOTES.md:1624-1629` reads the same test as
*forbidding* an exclusion **because** it raises the figure (−199 → +19). Both
cannot be right; the file's two cited passing examples move the figure in
opposite directions, so the rule as recorded does not decide this case at all.

And the counterfactual is wrong on its own terms: excluding the chunked fold does
not restore `+19`, because **manual unrolling is licensed by name** and §10a.2's
own table has the manual 32× unroll at **5.18750**, still below the shipped
5.75. *Failure scenario:* "we are not allowed to pin it, by our own rule" is the
load-bearing sentence of claim F and it is an argument from a rule that says
nothing about this edit.

### minor 6 — the published per-byte rates are not five-decimal measurements; only the difference is.

Period-averaged rates at every offset over the sweep:

```
fold  K   safe-unsafe/call  slope Ir/B   period rate (min..max, mean)      published
ship  4   [17.0, 21.0]      0.0005493    5.73891..5.75938 (mean 5.74970)   —
c4    4   [10.0]            0.0000000    6.48891..6.50938 (mean 6.50081)   6.50000
c8    8   [11.0]            0.0000000    6.58063..6.66250 (mean 6.62507)   6.62500
c16   16  [12.0]            0.0000000    5.16531..5.20625 (mean 5.18778)   5.18750
c32   32  [12.0]            0.0000000    5.08266..5.10313 (mean 5.09345)   5.09375
c64   64  [12.0]            0.0000000    5.04133..5.05156 (mean 5.04715)   5.04688
```

A legitimate residue-matched pair at a different offset gives 5.08266 or 5.10313
where §10a.2 reports 5.09375. The spread is exactly the `println` term, it does
**not** cancel within one binary, and it is ±0.01 Ir/byte — 20× the difference
between two published rates in that table. The 5-dp figures are exact as
*disassembly* quantities (`body/K`), not as measured slopes.

### minor 7 — the artefact cited as evidence for the mnemonic-identity claim prints the opposite verdict.

`NOTES.md:1665` names `.temp/p24/foldbody.py`; `.temp/p24/NOTES.md:75-77` reports
`identical=True` from it. Re-run as committed:

```
K=4    s_c4 n=None ... identical=False       K=16 ... txt=de5aebfde5b5 | txt=6da507ea369a identical=False
K=8    s_c8 n=None ... identical=False       K=32 ... identical=False
```

It compares full instruction *text* (registers included) and finds no body at
K=4/8. The claim itself is **true** — see the clean negative — but the
reproduction path for it is broken.

### minor 8 — "the chunk body is the same machine code on both sides" is exact for the five chunked spellings and only multiset-equal for the shipped row.

`s_ship`/`u_ship` bodies are 23 instructions each, same instructions, different
order (`movzbl` scheduled before the `×31` chain on the safe side, after it on the
unsafe side) — `.temp/r25/shipbody.py`.

## Clean negatives — do not re-run these

- **Attack 2, the null half — survives a genuine sweep, more strongly than
  published.** 127 consecutive `vlen` (120…246), `nrec` 2: safe−unsafe per call is
  a **single integer at every point** — 10 (c4), 11 (c8), 12 (c16/c32/c64) — slope
  of the difference `0.0000000` Ir/byte, max residual `0.00`. Shipped pair: 17 at
  `vlen ≡ 0 (mod 4)`, 21 otherwise, i.e. `7+5·nrec` / `7+7·nrec` at `nrec` 2. The
  residue-collapse claim also holds. Worth recording that §10a.2's "three
  residue-matched bands" are three pairs at **one** offset (56, 88, 2040, 2072,
  2168, 2296 are all ≡ 24 mod 32) — the sweep is what makes the null a result.
- **Attack 3 — all twelve probes honour all four `required` entries**, not just
  the two the matcher checks. `.temp/r25/contract.py`: `req1=req2=True`,
  `forb1=forb2=False`, tag folded **before** the fit test, `nrec` folded — 12/12
  `IN CONTRACT`, 0 failures. The phrase "in contract by the gate's own matcher" is
  weaker than "in contract" (`check.spelling_matches` is a definition, stage 0b is
  presence-only, `idiom_audit` is reporting-only) but the probes are in contract
  on the full reading.
- **Attack 4 — mnemonic identity holds, and at K=4 and K=8 too.** With
  innermost-loop selection: bodies 26 / 53 / 83 / 163 / 323, `movzbl` 3 / 6 / 16 /
  32 / 64, **mnemonics identical safe-vs-unsafe at K = 4, 8, 16, 32 and 64**.
  §10a.2 under-claims by hedging to 16/32/64.
- **Attack 5 — the offset is the `println` term, now controlled rather than
  asserted.** Holding fold and blob fixed and sweeping `n_iters` 100…123:
  `Ir = 354710 + 1459.91·n + 22.63·digits`, max residual 14.8 Ir. Band A's
  Δ(Δdigits) = +2 predicts `+0.00354` Ir/byte against a measured `+0.00469` (gap =
  15 Ir total, inside the fit residual); band B predicts and measures `+0.00000`.
  It cancels exactly in every safe-minus-unsafe difference because both rungs
  print the same checksum.
- **Attack 6 — claim E is right; the `51·nrec−5` / `48·nrec−5` domain really is
  wrong.** `u_ship − s_c32`: n1v124 46, n4v124 199, n9v124 454, n16v124 811;
  n1v126 43, n4v126 187, n9v126 427, n16v126 763; `small` 199, `large` **2365**
  against the law's `48·10−5 = 475`; `sweep-v56` **31** and `sweep-v88` **115**
  with both ≡ 0 (mod 4) at `nrec` 4. Every number in §10a.2's ⚠ reproduces.
- **Claim D's other halves reproduce.** `equiv.py`: 95/95 × 12 variants, 0
  mismatches over 1140 comparisons. `miri.py`: `u_ship`, `u_c4…u_c64` on `small`,
  `large` and all three `adversarial-*`, exit 0, no UB, all outputs agree.
- **The committed tree is green.** `harness/check.py p16` → `check.py: PASS` in
  1m27s; the only working-tree churn was the ASan PID string in
  `results/gate/p16-tlv-walk.json`, reverted.

## Problems

- **A concurrency bug in my own harness, caught by the data.** Two `meas.py` runs
  briefly shared `.temp/r25/probe/{lo,hi}.bin`, and one point came back with a
  non-12 value in the `s_c32 − u_c32` column — which is how it was found.
  `meas.py` now uses a per-PID scratch dir; all eight chunk-binary cache entries
  were purged and re-measured single-process, and `small`/`large` reproduced to
  the instruction. Every number above is from the clean pass. **Background
  `nohup` jobs on this box get reported "completed" while still running** — that
  is what created the overlap; run measurements in the foreground.
- **Attack 8 (reproduction gap), reported not fixed.** For §10a.2 to be
  re-derivable from the committed tree: (a) `controls/gen_controls.py` needs a
  third dict of the ten fold variants — `.temp/p24/gen_matched.py`'s
  `chunks(k, slice_expr)` is already the exact `sub()` shape, so it drops in, but
  its hardcoded `REPO = "/home/apt/repos_common/sec-ladder"` must become the
  `__file__`-derived path `gen_controls.py` already uses, and its `PATH_FIX` is
  byte-identical to the one there; (b) the K=64 row and the "323 insns" figure
  need either a fourth band in `inputs/gen.py` (appended **last**, per TASK_020's
  argument, so the 95 existing blobs stay byte-identical) or an explicit
  "scratch-only, not reproducible from the tree" marker — a consecutive band
  works, the 128-blob sweep needed no mod-64 triple; (c) `foldbody.py` must not
  ship as-is (minor 7). `measure.py`/`equiv.py`/`miri.py` all carry the same
  absolute-path constant. Landing (a) re-runs the p16 gate; (b) re-runs every p16
  measurement.

## Unsure / not done

- Did **not** test whether *some* admissible R4 can reach 5.09375 — a hand-unrolled
  32× fold with explicit indices is Verus-expressible in principle and §10a.2's
  table has manual 32× at 5.18750. So blocker 1 shows the six `u_c*` spellings are
  inadmissible; it does not prove `inf(admissible R4) > inf(admissible R3)`. What
  it does prove is that the sentence at `NOTES.md:1586-1588` — "the admissible
  unsafe class dips below the admissible safe class … exactly as `inf(R4) ≤
  inf(R3)` predicts by construction" — has no rung behind it, and that **the
  by-construction argument itself is unsound for p16**: R4 is chained by the
  `identity` pin to a verifiable R5, so it is **more** constrained than R3, not
  less. That is the mechanism behind "safe beats unsafe here" and it is stronger
  than the shipped-cell framing.
- Did not re-run the p05 or p02 gates (untouched), and did not re-measure
  §10a/§10a.1's four `nrec` laws (out of scope; TASK_023 swept them).
- The `s_n*` controls are mine and unswept beyond three points; their 5.375 slope
  is exact at both of the two period-64 steps measured and matches the
  disassembly (43/8), but it is not a 128-point sweep.

## The question behind all of it

The measurements support a **split** answer, and neither of the manager's two
readings as stated. A **bare per-byte rate is not a property of the kernel** — in
contract, on one pattern, one exact-string substitution apart, it ranges
5.04688 … 6.62500 (a 31% spread), and a seventh spelling lands at 5.375; worse,
it is not even measurable past ±0.01 because the driver's `println` term does not
cancel within a binary. So p16's 5.7500, p17's 10.0000/5.7500, p05's 1.375000 and
finding 11's 4.25 are all quoting a free parameter, and a **cross-spelling
difference of two such rates is worse still** — that is exactly what
−0.5625/−0.65625 is, and it is the number that reached four files as a headline.

But the **difference of rates at matched spelling is a property of the kernel**:
exactly 0.0000000 Ir/byte, over 80 consecutive lengths × 6 spellings, with the
mechanism visible (the reslice and the `get_unchecked` are hoisted out of the
fold, so the chunk body is mnemonic-identical).

So the publishable statement is **`p16's per-byte safety tax is 0.00000, swept`**
— and the rule that follows is stronger than the one §10a.2 adopted: not "name
the fold when you quote a rate", but **never publish a bare rate or a
cross-spelling difference of rates as a pattern's number; publish only
matched-spelling differences**. Under that rule §10a.2's own headline figure is
the thing that must be withdrawn, which is why the reporting rule as written did
not catch it. If a mechanical backstop is wanted it is cheap and it is not a
prose grep: the gate already disassembles, `spec.md` could pin the shipped fold's
chunk-body instruction count, and `check.py` could assert `body_len / K` equals
the published rate — `.temp/r25/foldcmp.py` is 90 lines and does exactly that.

## Memory updates

None — the reviewer does not write `.memory/`. What should land, once the manager
has read it: (1) the `⚠ CONTESTED — PROVISIONAL` block's second bullet is
confirmed on the null and refuted on "at matched spelling the unsafe rung is
cheaper … as `inf(R4) ≤ inf(R3)` requires" (blocker 1); (2) `−0.5625` →
`−0.65625` at `.memory/01-ladder.md:393,417` and every other site (major 2); (3)
`−2365` → at least `−2545` at `large` (major 3); (4) the direction test's
statement at `.memory/01-ladder.md:144-150` is self-contradictory in sign and
needs re-wording before it is cited again (major 5); (5) `inf(R4) ≤ inf(R3)` "by
construction" is **false for any pattern with an `identity: unsafe ≡ verus,
exact` pin** — the R4 class is bounded by what vstd can verify, and p16 is the
measured instance.
