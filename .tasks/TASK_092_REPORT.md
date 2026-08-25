# TASK_092 — `p46`'s corrections + the queue's exposure: report

**Role: research engineer.** **UNREVIEWED.**
⚠ **This file was written by the MANAGER after the fact — PROTOCOL rule 10 says
write the report BEFORE citing it, and the manager landed `.memory/` entries
attributing findings to `TASK_092` while this file did not exist.** The content
is the engineer's; the lateness is the manager's defect.

**PROTOCOL rule 2 running count: 259 → 261.**

---

## ⚠⚠ A0 — THE QUESTION p46's HEADLINE RESTED ON: `r4_mutreslice`'s FULL R5 CLOSES

```
$ controls/mkvariants.py --write DIR && ./verus_run.py DIR/v46_mutreslice.rs --multiple-errors 12
verification results:: 21 verified, 0 errors        <- same count as shipped verus.rs
```

Same postcondition `r == bn_fold(buf@, off, len)`; **no `assume`, no `admit`, no
`assume_specification`.** What closes it: a **ghost mirror** `gout: Seq<u64>`
taken *before* the borrow, the invariant `row@ == gout.subrange(i, i+m+1)` plus a
frame clause, and **`vstd::seq::lemma_seq_subrange_index`** — once per use and
once after the borrow ends. Mutation-tested, both `20 verified, 1 errors`.
⚠ **The path is `vstd::seq::`; `vstd::seq_lib::` is private.**

**So the stated reason for excluding it was FALSE. The conclusion survives on TWO
DIFFERENT measured grounds:**

**(a) two new trusted items.** `grep -rn get_unchecked ~/tools/verus/vstd/` →
**0 hits, anywhere**. R5 must add `slice_get_unchecked` / `slice_set_unchecked`:
**TCB 5/3 → 7/5.** That is the disqualifier `spec.md`'s own shared paragraph
already records for p16's `r4_hdr`.

**(b) ⚠⚠ THE R4/R5 PAIR IS `differ` AT `-O3`**, against p46's pinned
`identity: unsafe == verus, O3 exact`:

| blob | `r4_mutreslice` | `v46_mutreslice` | R5 − R4 | `15n+1` |
|---|---|---|---|---|
| n024m024 | 5923.00 | 6284.00 | +361.00 | 361 |
| n048m024 | 11317.00 | 12038.00 | +721.00 | 721 |
| n024m048 | 11052.70 | 11413.70 | +361.00 | 361 |
| n044m044 | 18092.70 | 18753.70 | +661.00 | 661 |
| n010m010 | 1450.00 | 1601.00 | +151.00 | 151 |

Exec source **textually identical** (ghost-stripped diff = brace placement only).
Per instruction: R5 keeps one extra `ja` — the per-row reslice bound, **+3/row** —
and **fails to fold `load_u64`'s eight byte reads into one `mov`** (13 insns
against 1, **+12/row**). `movzbl` 7 against 3; shipped `unsafe`/`verus` both 3.
**3 + 12 = 15.**

⚠⚠ **THE HONEST CONSEQUENCE, now in `NOTES.md` 0c, `spec.md`'s `why`,
`README.md` and both rung sources: *"both spans degenerate" SURVIVES and "safe
beats unsafe" does NOT invert — but the headline is contingent on the IDENTITY
PIN and the TCB, not on a specification gap. If either were relaxed it
inverts*** — `r4_mutreslice` at 5923 and **even its R5 at 6284** sit below
`safe_naive` 6453 / `safe_tuned` 6499 at (24,24), and below both on 4 of 5
shapes.

## ⚠ A blocker-class defect NO REVIEW CAUGHT: a one-sided flag mismatch

`controls/mkvariants.py`'s documented build command **omitted `-C
codegen-units=1`**, which `harness/build.py::rust_flags` passes to **every
measured cell**. So **every number in `NOTES.md` 8b and 0c was a one-sided flag
mismatch**, 1–2 `Ir`/call off.

⚠ **One-sided mismatches do NOT cancel; two-sided ones do** — §8a's
rolled-vs-rolled control applied the flag to both sides and was unaffected.

**Corrected: R4-side span 2 `Ir`/call (published 3), R3-side span 0 (published
2) — both still degenerate, so the conclusion got STRONGER.** Law re-fitted over
48 blobs, zero residual: `r4_mutreslice − R4ship = 1 + 7n − 1.5nm − 2.5n[m odd]`
— **only the constant moved.**

## M1–M3, m1 — the review's findings

- **M1** — the phantom **`111`** traced to `.temp/t89/NOTES.md:82`, the
  **pre-build probe** (*"R2 is 186 insns, R4 111"*); shipped is 179/150. Same
  source for `9490`/`2750`. ⚠ **A fourth M1-class defect the review did not
  list:** `unsafe.rs` said `r4_runidx` is `+25 Ir/call flat` — the probe's row —
  against the pattern's own NOTES 8b (`−3.00`; shipped-flag figure `−2.00`).
- **M2 re-derived from both sides.** `safe_naive` and `safe_tuned` have the
  **identical** conditional-branch multiset `ja:2 jae:2 jb:1 jbe:1 je:6 jne:5`.
  `safe_tuned` hoists `lea (%rsp,%r13,8),%r8 ; add $0x8,%r8` into the row header
  (+2/row); `safe_naive` computes the same base **inside its odd-`m` remainder
  block** — **which is why the law branches on parity.** ✅ Confirmed on odd
  blobs (`−2.00`) and even (`+46/+94/+46/+86/+18`), residual 0.
  ⚠ **So there are THREE hardening strategies, not four.**
- **M3** — `verus.rs:39` `14` → **`20 verified, 1 errors`**.
- **m1** — conventions now named at §8's summary and at §8d.

## ⚠ m2 — SOLVED, and it is a documented effect two reviews called unexplained

Two consecutive `check.py p46` runs on an identical tree move **2 of 963 values,
both ASan address strings, ZERO `Ir`.** The cause is in
`harness/check.py::check_marginal_ir`'s own docstring: the term is **bistable**,
the discriminator is *"the presence of a single environment variable, not its
size"*, and the mechanism is the environment block shifting the stack pointer → a
per-call stack array's alignment → a different tail in
`__memset_avx2_unaligned_erms`. **p46 `memset`s TWO stack arrays per call, which
is why `unsafe`/`verus` `O3 whole` move by `−14 = 2 × 7`.**

⚠ **p46 is the FOURTH pattern at ±7** (the docstring names three). ⚠ **And one
clause of that docstring is too strong:** it says the term is `whole`-mode only
and *"`isolated` is exactly invariant"*; **p46's movers include five `-O0
isolated` cells.** **Corrected rule: `-O3 isolated` is invariant; `-O0` moves in
BOTH modes.** → **RECAP "Owed" 30** (it is a `check.py` edit, so it costs a
24-pattern sweep and must be batched).

## ⚠⚠ The re-measure cost model in the task file AND PROTOCOL rule 6 was WRONG

`measure.py p46`: **111 of 1371 leaf values moved — 102 wall-clock, 6 source
hashes, a timestamp, git metadata. ZERO `Ir`, zero md5, zero identity, zero
checksum.**

⚠ **`harness/measure.py::measurement_sources` globs `pdir/*.rs`**, and
`results/p46-bignum-mac.json`'s `source_sha256` lists `safe_naive.rs`,
`safe_tuned.rs`, `unsafe.rs` and `verus.rs` beside `c/kernel.c`. ✅
**Manager-verified. So a doc-comment fix in ANY rung `.rs` costs the same
re-measure — there is no cheap doc fix in a rung source** — and fixing
`c/kernel.c` alongside them was **free at the margin**. ✅ **PROTOCOL rule 6's
budget note is corrected.**

## Rule 6 disclosure

`spec.md` has been touched by exactly one commit (`591fcec`, its landing
commit), **so the `git show HEAD:` diff is real, not vacuous.**

```
contract_sha256  bddd7e032a72592a…  ->  43925b2955e0af2e…
```

Of the **119** leaf values in the hashed block, **exactly one moved: `idiom.why`**
(14634 → 17357 chars). **No `required`, `forbidden`, `identity`,
`requires`/`ensures`, `verus`, `miri`, `collapse` or `driver` moved**, and the
shared named-spelling paragraph is **byte-identical** (`59748cce2db5…`, 11003
bytes). **Two spans changed, both because measurement falsified them.**

## Gates

`check.py p46` **PASS** ×4; `measure.py --check-stale` → **48 records, 0
STALE**; `licence.py --emit` → 24 patterns, 96 verdicts, **only p46's six source
hashes moved, no verdict changed**; `synthesize.py` → `results/synthesis.md`
**byte-identical to HEAD**. Full 49-blob sweep: **every law reproduces, max
|residual| 0.00000**. `census.py --mutsub` → 10 verdicts, exit 0.

---

## PART B — `p24` and `p26` at shipped shape

Four cells per pattern in **one harness** — same driver loop, input, decode and
checksum, so **shape is the only variable**. Shipped flags. Checksums agree
across all four cells on every input.

**⚠⚠ `p24` — the sign does not flip. IT COLLAPSES TO EXACTLY ZERO.**

```
input          ship_safe  ship_unsafe    S-U    probe_safe probe_unsafe      S-U
p24-n016.bin      701.29       701.29  +0.00        852.17       749.52  +102.65
p24-n128.bin     4635.63      4635.63  +0.00       5906.15      4924.85  +981.30
p24-n255.bin     8968.51      8968.51  +0.00      11455.80      9513.25 +1942.55
```

**`ship_safe` and `ship_unsafe` are BYTE-IDENTICAL** — *"identical by raw
machine-code bytes: True"*, `md5_fn 3d37ca7b…` both, `n_nopad 133` both, **no
panic edge in either**. The **probe** shape reproduces the published number
(+6.42…+7.62/element). Mechanism: the probe's sift is 54 insns with **`jae:6`**
safe against 36 with `jae:1` — **five surviving bounds branches per sift**,
because `i` is an opaque parameter and `n = v.len()` an ABI value. ✅ **Robust:
with a `u16` count the two kernels are STILL byte-identical.**

⚠ **`TASK_090`'s `≈7.9 ± 0.1 Ir`/element is therefore a PROBE-SHAPE number** —
measured with `TASK_086`'s own binary and convention. **Retracted from the
catalogue.**

**⚠⚠ `p26` — the sign holds on four inputs, roughly halves, AND INVERTS ON THE
FIFTH.**

```
input                ship_safe ship_unsafe        S-U   probe_safe probe_unsafe       S-U
p26-np016r016.bin      7570.30     6837.30    +733.00      7659.30      6161.30  +1498.00
p26-np016r200.bin     24450.30    32837.30   -8387.00     24555.30     23329.30  +1226.00
p26-np200r020.bin     55794.00    44381.00  +11413.00     56619.00     33025.00 +23594.00
```

At **run length 200 safe is CHEAPER by 8387 = −2.62 `Ir` per output byte**.
Mechanism: the two shipped spellings reach **different fill strategies** —
`ship_safe` 166 insns, one `memset@GLIBC` and `xmm` regs; `ship_unsafe` 116
insns, **two** `memset@GLIBC`, no vector regs (loop-idiom-recognize turned the
unchecked writes into a `memset` call). **Neither has a panic edge.**
⚠ **And p26's probe pair is NOT THE SAME FUNCTION** — `k26_checked` early-returns
on capacity, `k26_unchecked` has **no capacity test at all** — which is why it
read 495454 vs 92942.

⚠⚠ **RE-RANK: `p26` IS THE MORE EXPOSED ROW, NOT `p24`.** p24's answer is a
clean, robust **`0.00`**; **p26's sign is a property of the RUN LENGTH, not of
the row**, so **p26 cannot be costed until its input band is designed.** **The
manager's ranking was wrong in direction AND in order.**

## Unsure / not done

- ⚠ **WHY LLVM diverges between `r4_mutreslice` and `v46_mutreslice` from a
  textually identical exec source is NOT ESTABLISHED.** The instruction
  accounting is complete (`3 + 12 = 15`/row); the pass-level cause is not, and no
  `-C` flag was bisected. **Cite it, do not explain it.**
- **Part B's kernels are the engineer's reading of "shipped shape"**, following
  p46's template. **A real p24/p26 might differ**; the p24 `u16` control is the
  only sensitivity test run.
- **p26's inversion threshold is not located** — run lengths 16/20 (+) and 200
  (−), nothing between.
- **p35 and p23 were not built** — scoped to the two HIGH rows.
- `r4_mutreslice` was **not** put through Miri, `check.py` or the twin regime; it
  is a control.
- No wall-clock work; no full sweep; no `.memory/` edits; no `git add`/`commit`.
