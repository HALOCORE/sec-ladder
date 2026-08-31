# TASK_158 review report — `p25`, and the tree-wide `Ir` finding

**Role: research reviewer.** Nothing under `patterns/`, `.memory/`, `RECAP.md`,
`results/` or `harness/` was edited. One tracked file was rewritten by running a
control (`controls/no_reloc.json`, timestamp only) and was **restored and
verified by bytes against HEAD** — §11. All instruments are under `.temp/t158/`.

**Verdict: `p25` STANDS as a row. Its C-mechanism distinction is real, its
detectors are real, its R5 is sound, and its gate certifies the tree it claims
to.** No blockers. **Six majors and eight minors**, of which **four majors are
the manager's**, and **the row's own headline 2 is wrong on the half of its
domain nobody measured**. `p25` is **NOT FINISHED** (§9).

---

## 0. Item-by-item verdict

| item | verdict |
|---|---|
| 1 tree-wide `marginal_ir_per_call` | **SURVIVES, NARROWED** — arithmetic exact, derivation wrong in three ways, and it IS a correction, not a methodology note (M1, M2) |
| 1b R2/R3 `-O0` sign inversion | **SURVIVES**, mechanism re-derived and closed over every function (CN-3) |
| 2 C-mechanism distinctness | **SURVIVES** — the distinction is in the C code, not the vocabulary (CN-1); census re-derived exactly |
| 3 the row rests on the detector | **SURVIVES** — the unbiased evidence exists and I reproduced it independently (CN-2) |
| 4 the cost result | **SURVIVES DIRECTIONALLY, FALLS AS A MAGNITUDE AND AS A CLASS CLAIM** (M3, M4) |
| 5 DR 400 | **SURVIVES, NARROWED** — no published number rests on it; the reading is narrower than the row's own conclusion; the citation is loose (m5, m6) |
| 6 `model.py` / determinism | **SURVIVES** — `sanitizer_expect` is DERIVED, the derivation fires, the row says so |
| 7 R5, mutants, `E0502` | **SURVIVES** — `assume(false)` does not land (CN-4) |
| 8 controls, Miri, gate hygiene | **SURVIVES** — all three first-run failures independently confirmed closed (CN-5…CN-8) |

---

## 1. ITEM 1 — settled

### 1a. The manager's arithmetic reproduces EXACTLY. Clean negative.

`.temp/t158/marg.py`, over the 32 committed gate records, max `|marg[verus] −
marg[unsafe]|` per pattern:

```
p28 1732.73 · p11 494.00 · p29 465.55 · p25 269.52 · p35 36.47 · p14 34.00
p42 33.00 · p17 30.00 · p18 25.00 · p13 22.00 · then p38 16.00 and below
```

Identical to `TASK_158.md`'s list, entry for entry. The commit message's *"ten
patterns are at >= 20 `Ir`/call"* is **correct**.

### 1b. But the RANKING is an artefact of mixing modes — **MAJOR 1**

`.temp/t158/marg2.out` splits the same quantity by `(opt, mode, input)`:

* **8 of the top 10 have their maximum at `O3/whole`.** In **`-O3 isolated`** —
  the only column `synthesis/synthesize.py` publishes (`marginal()` and
  `ir_per_call()` both default to it) — those same eight patterns read
  **`−1.00`**, the driver term `CALLEE_NOTE` already names.
* `-O0 isolated` and `-O0 whole` are **identical for every one of the 32
  patterns** (nothing inlines at `-O0`), so "it mixes `isolated` with `whole`" is
  vacuous at `-O0` and total at `-O3`.
* The real `-O3 isolated` exposure is **four patterns, not ten**:

```
p25 large  +269.52     p42 large  −31.00
p03/p04    +6.00  (already WITHDRAWN in results/synthesis.md §2)
p02 both   −2.00  (already explained: gcc's PLT thunk, CALLEE_NOTE)
```

### 1c. ⚠⚠ `whole` does NOT belong in the statistic, and the manager's own spot-check misses the cell its headline came from — **MAJOR 2**

`TASK_158.md` §1 states *"`p11` and `p25` are kernel-identical at EVERY cell (so
the whole gap is outside the kernel)"*. For `p11` that inference is **false at
the cell the `−494.00` comes from**, and it is false in the dangerous direction.

`.temp/t158/symdiff.py --pattern p11 --mode whole --opt O3` (decomposition closed
over every function; the sum of per-symbol deltas equals the whole-program delta,
asserted in the script):

```
p11 O3 whole small.bin
  whole-program marginal  unsafe 22527.00   verus 22033.00   Δ = −494.00
  per-symbol delta:  unsafe::main −22527.00   verus::main +22033.00
  (there is no `kernel` symbol at all — it is inlined)
```

**100 % of `p11`'s `−494.00` is inside the rungs' OWN code**, not a callee. The
static trace is there too (`harness/asm.py`):

```
p11 unsafe O3/whole   main 751 non-pad insns, 3407 bytes
p11 verus  O3/whole   main 747 non-pad insns, 3311 bytes
p11 unsafe O3/isolated main 625, 2751     p11 verus O3/isolated main 627, 2751
```

The reason the `identity: exact` pin does not catch it: **`check_identity`
compares `isolated` digests only** — `harness/check.py:3303`,
`digests.get((a, o, "isolated"))`. So:

> **Per mode, the number means different things.** In `isolated` it is
> `(kernel diff, pinned) + (callee diff) + (driver diff)` and the
> kernel-exclusive column is available and immune. In `whole` the kernel symbol
> is usually gone (`results/synthesis.md` §5 claim 3: 474 of 494 `whole` pairs
> have `kernel_exclusive_ir = None`), so the number contains the rungs' own
> inlined code and **the pair is not a null control there at all.**
> **`whole` must be excluded from any R4/R5-as-null statistic.**

⚠ This also scopes finding 1 (*"a proof costs zero instructions"*): it is an
**`isolated`** result. `p11`'s `whole` build executes 494 fewer instructions per
call in the R5 binary than in the R4 one.

### 1d. Is it NEW? **No as a fact; yes as a magnitude — and the RECAP quote is a DIFFERENT claim**

*Not new.* That `marginal_ir_per_call` is whole-program is **documented, load-
bearing and deliberate**:

* `harness/check.py:2805` — *"Measured as a slope … which is symbol-independent
  (so it works in `whole` mode, and at `O0` where a rung's work lives in
  `core::iter` symbols rather than in `kernel`)"*;
* `synthesis/synthesize.py:27–33` — *"`marginal_ir_per_call` is whole-program and
  therefore symbol-independent, so `(marg[A]−marg[B]) − (kex[A]−kex[B])` is the
  callee correction"*. **The entire published callee column is built on it.**
* `results/synthesis.md` §5 claim 1 **already publishes** *"the zero does NOT
  survive the callee correction … i.e. 'the proof costs instructions' between two
  byte-identical kernels"*, and already resolves it: **the kernel-exclusive zero
  is the correct reading.**

*Not the settled `ns` finding either.* The `RECAP` quote `TASK_158.md` offers —
*"a biased draw of size one … the floor is the layout population"* — is
`.memory/03-measurement.md:922`, and it is about **`ns`**, with the mechanism
*source-path length moves the kernel's ADDRESS*. Callgrind is layout-blind. **The
two claims must not be merged**, and the task file was right to warn.

*New:* the **magnitude** (`p25` +269.52; `p28` +1732.73 at `-O0`), and 1e.

### 1e. ⚠⚠⚠ DOES ANY PUBLISHED NUMBER FALL BELOW ITS OWN PATTERN'S R4/R5 GAP? **YES — THREE.** This is a CORRECTION, not a methodology note — **MAJOR 3**

`.temp/t158/nullctl.py` puts each pattern's `|R5−R4|` beside every **other**
pair's derived callee correction — the quantity `results/synthesis.md` §2
publishes — all at `-O3 isolated`:

| pattern / blob / pair | published correction | band | its own R5−R4 null | ratio |
|---|---:|---|---:|---:|
| **p25 large `gcc-clang`** | **+19.42** | **≥16.00 → "ALL real", printed BOLD** | **+269.52** | **13.9×** |
| p42 large `gcc-clang` | +5.00 | 2–16 → "coin flip", `?` | −31.00 | 6.2× |
| p02 both `gcc-clang` | +2.00 | exactly on the 2.00 floor | −2.00 | 1.0× |

* `p42`'s and `p02`'s are **published today**. `p02`'s is already argued
  (`CALLEE_NOTE`: the PLT thunk, *"the smallest real correction sits exactly on
  it"*) and `p42`'s carries the `?` "look further" marker.
* **`p25`'s is not published yet and will be the moment `synthesize.py` is
  re-run** — in the band the file's own legend calls *"ALL real, smallest
  17.00"*, at **1/14 of the same pattern's, same column's, same blob's null.**

**Recommended wording (I do not fix):** `synthesis/synthesize.py` should compute
`null = derived_correction(..., "verus", "unsafe", inp)` per (pattern, blob) and
**refuse to promote any other pair's correction to the `CONFIDENT` band when
`|correction| <= |null|`**, printing the null instead. That is a `synthesis/`
change, not a `harness/` one, so it costs **no re-gate**.

### 1f. ⚠ `results/synthesis.md` §5 claim 1 is ALREADY false, and `p25` makes it worse — **MAJOR 4**

`synthesis/synthesize.py:1485–1505` emits a **generated list** and then
**hardcoded prose**. The published file (`results/synthesis.md:611–615`) reads:

> *"… clears the ±2.00 floor on **7 rows** — p02 small, p02 large, p03 ×2
> `‡`, p04 ×2 `‡`, **p42 large −31.00** …"*
> *"**Every one of those rows is in the uncertain 2.00–16.00 band** …"*
> *"**The kernel-exclusive zero is the correct reading on all six** …"*

* **`p42 large −31.00` is NOT in the 2.00–16.00 band** — it is ≥16.00, and §2's
  own table prints it in **bold**, which the legend defines as the confident
  band. The universal is false.
* **Seven rows are listed and six are resolved.** `p42` is silently dropped, so
  the artefact leaves *"the proof costs −31 instructions"* standing.
* Re-running with `p25` gives **8 rows, two of them outside the band**, the new
  one at **+269.52 = 17× the `CONFIDENT` threshold**.

This is PROTOCOL rule 13's class in a generator: the list is computed, the
paragraph above it is not.

### 1g. Mechanism, CLOSED over every function — and the engineer's is 95.7 % of it

`.memory/03-measurement.md`'s *"Close a decomposition over EVERY function"* rule.
`.temp/t158/symdiff.py`, p25 `-O3 isolated large.bin`, environment pads **0 and
16** (`check_marginal_ir`'s own 16-wide-window argument makes a two-pad screen a
**complete** detector), results **identical to the hundredth**:

```
verus::kernel − unsafe::kernel  =  0.00   (4152.71 each; 9104.17 each at -O0)
verus::main   − unsafe::main    =  0.00   (  14.00 each;   25.00 each at -O0)
SIX glibc malloc-internal symbols            SUM = +268.88 = 100.0 % of the delta
  0xab570 +133.54  (called by malloc and by 0xacf50 -> _int_malloc)
  0xab170 +111.44  (called by free  and by 0xacf50 -> _int_free)
  0xa9ad0  +46.50 · 0xa9bb0 −31.62 · 0xacf50 +12.30 (called by realloc) · 0xa91f0 −3.28
```

* **The engineer's conclusion is confirmed exactly**: the two kernels cost
  identical `Ir` at both levels and the delta is entirely outside them.
* **Their three named routines are exactly right and exactly incomplete**:
  `133.54 + 111.44 + 12.30 = 257.28 = 718.28 − 461.00`, to the hundredth. The
  remaining **+11.60** is three further libc symbols the report does not
  mention, and the report's phrasing (*"what differs is three unnamed libc
  routines"*) reads as closed when it is 95.7 % closed — **minor 1**.
* **It is NOT the environment-phase effect.** Identical at pad 0 and pad 16.
* Symbol names are unavailable (`libc6-dbg` absent, PROTOCOL rule 14); the
  caller edges identify them.

### 1h. `p42`'s published `−31.00` decomposed, same instrument

```
p42 O3 isolated large.bin, pads 0 and 16, identical
  verus::kernel − unsafe::kernel = 0.00 (50734.00 each)
  verus::main   − unsafe::main   = 0.00 (   13.00 each)
  0xab170 (_int_free)  −31.00     = 100.0 % of the delta
```

### 1i. ⚠ The number does not reproduce to the hundredth — **minor 2**

`check_marginal_ir`: *"Quote marginals **to the instruction, never to the
hundredth**, across sessions."* The record says `verus … 5648.91`; two
independent runs here both give **5648.27** (`unsafe` reproduces **exactly** at
5379.39). Drift **0.64** — 32× the scratch-directory term
(`.memory/03-measurement.md`, ±0.02). `p25/NOTES.md` §8a and `TASK_157_REPORT`
§9 quote `+269.52` and `5648.91` to the hundredth.

### 1j. The sign-inversion half — **SURVIVES**, mechanism named

Re-derived from the committed gate record: `safe_naive/O0/isolated/small`
`2741.37` vs `safe_tuned` `4807.90` = **1.7538×**; `large` `12678.50` vs
`22220.61` = **1.7526×**; kernel-exclusive `1710.46` vs `1700.99` = R3 **0.55 %
cheaper**. And `.temp/t158/symdiff.py --opt O0 --cells safe_naive,safe_tuned`
closes it over every function:

```
safe_tuned::kernel − safe_naive::kernel                                −309.89
ChunksExact<u8>::next                                                 +4920.00
<[u8]>::split_at_unchecked                                            +3025.00
Take<ChunksExact<u8>>::next                                           +1810.00
<[u8]>::chunks_exact +38 · ::take +14 · into_iter +9 · 0x188a80 +36
main (cancels, 25.00 each)                                                0.00
                                                        SUM = +9542.11 = exact
```

The row's stated mechanism is right and now has four named symbols behind it.
⚠ Worth noting for the record: the single largest term in the **safe tuned**
rung's out-of-line cost is `<[u8]>::split_at_unchecked`.

---

## 2. ITEM 2 — the C-mechanism distinction. **SURVIVES.**

Census re-derived by running `controls/no_reloc.py`, identical to the committed
sidecar (only `measured_utc` moved; restored, §11):

```
32 patterns with a c/ directory
  call `realloc`                   :  1   [p25]
  call malloc/calloc/aligned_alloc :  5   [p27, p28, p29, p34, p42]
  call `free`                      : 32   [every pattern]
```

**The distinction is in the C code, not the vocabulary** — read side by side:

| | `p25/c/kernel.c` | `p34/c/kernel.c` |
|---|---|---|
| retirement | `realloc(toks, nc)` as a side effect of GROWTH; no `free` on that block, ever | `free(o)` explicitly, when `o->rc` hits 0 |
| omitted text | a **conjunct on the READ** (`curbase == toks`) | an **assignment on the ACQUIRE** (`t->rc = t->rc + 1`) |
| repair site | the READ | the ACQUIRE (and, per `TASK_155`, the DESTROY) |
| what is stale | an **interior** pointer into a container | a pointer to a **whole object** |
| CWE | 416 via 825 | 416 via 911 |
| read path in R1 | **wrong** | **correct** |

`p08` and `p32` call no allocator at all; `p27` mallocs whole records and frees
them explicitly. No built row's C can produce "the container moved under a live
interior pointer". ⚠ The census settles the **token** question only, and both
`NOTES.md` §1 and `spec.md` say so.

---

## 3. ITEM 3 — the thesis and the detector. **SURVIVES.**

The row is **not** ASan-only, and I reproduced the unbiased half independently
rather than reading it. `.temp/t158/search.py` section A, **plain** gcc `-O1`, no
sanitizer, real glibc, all 8 shipped inputs against `model.py`:

```
R1     model mismatch [adversarial-lateread, adversarial-many, adversarial-move]
R1h    model mismatch []      RD  []      TERN []      FIXUP []      PTR []   FIXUP2 []
```

R1 diverges on **exactly** the three relocating inputs and nowhere else. That is
the unbiased evidence, and it is enough: it does not depend on ASan's allocator.

`sanitizer_expect` is **DERIVED**, not declared (`model.py:564`, and the module
docstring says so): `_sim_window(harden=False)` routes every read through
`Heap.touch`, whose guard is `blk.retired` — **a property of the block reached**,
never a length or index test, which is exactly what
`.memory/03-measurement.md:3092` (entry 19) asks. `detector_selftest()` runs a
must-fire arm plus **two** silent controls that separate the two halves of the
harm condition, and `selfcheck()` runs it once per input on every gate
invocation.

⚠ **One honest circularity, and the row discloses it**: `controls/no_stale.py`
calls `model.window_stale`, which is the *same* `_sim_window` flag as
`sanitizer_expect` (*"so the two can never drift apart"*). It is therefore a
**re-report, not a second measurement**, and the independent oracles are the ASan
build (biased) and the plain-build divergence above (unbiased). Not a tautology
of the representation; is a tautology of the *simulation*, said out loud.

---

## 4. ITEM 4 — the cost result. **The direction survives; the magnitude and the class claim do not.**

I did what `TASK_157` explicitly did not: **searched both endpoints**.
`.temp/t158/search.py` builds six arms from the shipped C by substitutions whose
counts are asserted, and `.temp/t158/clangmarg.py` adds clang. **Every arm agrees
with `model.py` on 8/8 inputs and is ASan- and UBSan-clean.** Two independent
runs of the gcc half agreed to the hundredth.

**Kernel-exclusive marginal `Ir`/call, isolated, relative to R1:**

| arm | what | gcc s/O0 | gcc s/O3 | gcc l/O0 | gcc l/O3 | clang s/O0 | clang s/O3 | clang l/O0 | clang l/O3 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **R1h** | shipped conjunct | +14.76 | +24.69 | +131.08 | +164.39 | +18.45 | +18.72 | +163.85 | +93.65 |
| TERN | conjunct as a `?:` | +14.76 | +24.69 | +131.08 | +164.39 | — | — | — | — |
| **RD** | shipped re-derive | +7.38 | +10.87 | +65.54 | +65.67 | +3.69 | +3.72 | +32.77 | +17.09 |
| PTR | `*(toks+curi)` | +7.38 | +10.87 | +65.54 | +65.67 | — | — | — | — |
| FIXUP | repair at the GROWTH | +2.18 | +14.14 | **+2.68** | +69.69 | +3.27 | +17.25 | **+4.02** | +60.47 |
| FIXUP2 | ditto, DR-400-clean | +5.90 | +21.67 | +19.77 | +104.21 | +6.99 | +26.43 | +21.11 | +128.85 |

### 4a. ⚠⚠ *"on both compilers"* is a GCC-ONLY figure, and clang contradicts the magnitude by 2.5× — **MAJOR 5**

`patterns/p25-realloc-growth/README.md:25` (Headline 2):

> *"`controls/rederive.py` prices it at **roughly half** the shipped conjunct's
> cost, **on both compilers at both optimisation levels**."*

and `NOTES.md:252–255`:

> *"costs about HALF what the idiomatic one costs, **on both compilers** at both
> optimisation levels and on both inputs."*

**`controls/rederive.py`'s section C builds with `GCC` only** — `build(GCC, kern,
opt, …)` at `controls/rederive.py:251`. There is no clang marginal in
`rederive.json`. Measured here:

```
R1h / RD ratio    gcc   2.00  2.27  2.00  2.50
                  clang 5.00  5.03  5.00  5.48
```

*"Roughly half"* is true of **exactly one** of the four columns the sentence
claims (gcc dynamic). The static columns are 3.7×–5× (gcc) and 6×–9× (clang).
The error is in the row's own favour: on clang the standard-clean repair is
**5×** cheaper, not 2×. **The conclusion is safe; the number and its scope are
not.**

### 4b. ⚠⚠ *"the safer repair dominates"* is false of the CLASS — **MAJOR 6**

Both **published** endpoints are robust to respelling — a clean negative worth
having: `TERN` equals `R1h` and `PTR` equals `RD` **to the hundredth at every
cell**, and `TERN` costs `+11` static where `R1h` costs `+11`. So the two shipped
numbers are not spelling artefacts on that lever.

But **the repair SITE was never searched**, and there is a third one: repair the
interior pointer where it breaks, at the growth. Among the **two standard-clean
repairs**, the ordering **reverses**:

```
gcc   large -O0   RD +65.54   FIXUP2 +19.77   <- FIXUP2 3.3x cheaper
gcc   small -O0   RD  +7.38   FIXUP2  +5.90   <- FIXUP2
clang large -O0   RD +32.77   FIXUP2 +21.11   <- FIXUP2
clang small -O0   RD  +3.69   FIXUP2  +6.99   <- RD
every  -O3 cell   RD wins, by 1.6x (gcc large) to 7.1x (clang small)
```

So *"On the C side this row has no trade-off: the safer repair dominates on both
axes"* (README Headline 2, `NOTES.md` §3c, the commit message) is a statement
about **one spelling of one repair site**. The row's own disclaimer two
paragraphs below (*"the cost of THESE TWO SPELLINGS, never of the repair"*)
is correct and is doing more work than the headline admits — **the headline
should be brought down to the disclaimer, not the other way round.**

⚠ `FIXUP` (the natural spelling, `if (cur != NULL) cur = toks + curi;`) is
**not** DR-400-clean — it evaluates `cur != NULL` on a pointer `realloc` has made
indeterminate. `FIXUP2` carries the "has a SAVE happened" bit in an `int` and
touches no indeterminate value; both are in `.temp/t158/search.py` and both agree
with the model on 8/8.

### 4c. ✅ Clean negative that closes item 1's biggest risk to this row

For **every** C arm, at **every** cell, `whole-program marginal − kernel-exclusive
marginal` is **exactly constant**:

```
small -O0 521.27   small -O3 500.27   large -O0 1143.70   large -O3 1122.70
```

so the two `Ir` conventions give **identical differences** for the C arms, and
`NOTES.md` §3c's numbers are unaffected by the whole-program artefact whichever
convention a reader assumes.

⚠ **But the row never says which convention §3c is in — minor 3.** Its header
reads *"Marginal `Ir` per kernel call, gcc, isolated, `(Ir@200 − Ir@100)/100`"*,
which is `check.py::_callgrind_total`'s construction and is the literal name of
the **whole-program** gate field; the numbers are in fact **kernel-exclusive**
(`controls/rederive.py::kernel_ir` sums `callgrind_annotate` rows matching
`kernel`). `rederive.json`'s own field is likewise named `marginal_ir_per_call`,
colliding with the gate's whole-program key. `.memory/03-measurement.md:517`
(*"NAME THE ONE YOU USED"*, *"say which convention a number is in, every time"*)
is directly on point, and §8a two sections later is the very place that warns the
two differ on this pattern.

---

## 5. ITEM 5 — DR 400. **SURVIVES, NARROWED.**

* ✅ **The separation is real.** No published number rests on the standards
  argument: §3c's table is a measurement, and §4c shows it is convention-clean.
  `NOTES.md` §10 states *"Not that the shipped R1h is a correct C program under
  the abstract machine"*, and `TASK_157_REPORT` §11 names it as the least-certain
  call. That is the right handling.
* ⚠ **minor 4 — the reading is narrower than the row's own conclusion.**
  `NOTES.md` §3b says *"the surviving `*cur` in R1h's true branch is a use of an
  indeterminate value"*. But `curbase == toks` is itself a read of an
  indeterminate pointer value, **on every path, including the false one**. The
  broader statement is what actually licenses the row's conclusion (*"the only C
  rung DR 400 cannot reach is the UNCONDITIONAL re-derive"*), and it is also why
  my `FIXUP` arm is unclean and `FIXUP2` is not.
* ⚠ **minor 5 — the citation is loose.** WG14 **DR 400 is titled *"realloc with
  size zero problems"***. The load-bearing text for *"indeterminate whether or
  not it moved"* is **C11 6.2.4p2** (a pointer's value becomes indeterminate when
  the object's lifetime ends) plus **7.22.3.5p4** (*"deallocates the old
  object"*), with DR 260 for "an indeterminate value may change". The claim is
  right; the number attached to it is not the authority for it. It is quoted in
  `spec.md`'s hashed `why`, `c/kernel.c`, `NOTES.md`, `README.md` and
  `controls/rederive.py`.

---

## 6. ITEM 6 — `model.py`, determinism. **SURVIVES.**

* `sanitizer_expect` is **DERIVED and the derivation fires** — §3 above.
* `adversarial-nogrow` is an `adversarial-*` file that derives `clean`, which is
  what makes *"the adversarial rows fire"* a measurement about the detector
  rather than about the filename. Genuinely load-bearing.
* **Nothing gates on an R1/R1h divergence.** The gate's `sanitizer` block pins
  `fires`/`clean` and R1h's value; `controls/detectors.json` records R1's ubsan
  stdout (`3528946245511863296` on `adversarial-lateread`) as data, not as a pin.
  The 1-in-256 disclosure is in `NOTES.md` §2c, `spec.md` and the caveat.
* ⚠ **minor 6**: the caveat's formula (§8.3 below) is over-general.

---

## 7. ITEM 7 — the R5. **SURVIVES.**

* `grep` on `verus.rs`: **4 `#[verifier::external_body]`, zero `assume`, zero
  `admit`, zero `assume_specification`.** TCB tally of 4 recounted and correct;
  the gate governs 2 (`_is_trusted` = `external_body` **with** an `ensures`, or
  `unsafe` in the body), and `NOTES.md` §9 states the two denominators
  explicitly — the `TASK_145` p32 confusion is closed here, not repeated.
* Obligation census has an artefact: `.temp/t157/verus/obligations.{sh,log}`,
  one `--verify-function` run per item, `0+0+1+0+0+0+0+0+2+5 = 8` plus 2 consts
  = the pinned 10. Twin 12.
* The four mutants' diagnostics are recorded with asserted substitution counts
  and are the *right* diagnostics: ATTACK fails at the READ
  (`precondition not satisfied` on `vec_get_unchecked`), X1 at the SAVE
  (`invariant not satisfied at end of loop body`), VACUITY on the postcondition,
  SPEC-WEAKEN at `main`'s consuming assert.
* ✅ **`assume(false)` does not land.** Verified without touching the tree, by
  driving `harness/check.py` directly on a planted copy of `verus.rs`:

```
shipped verus.rs                       hits {}                    -> no failure
+ proof { assume(false); } in kernel   hits {'assume(': [391]}    -> FAIL proof-vacuity
+ // assume(false);        (comment)   hits {}                    -> no failure
spec.md verus.assumptions = None (i.e. 0)
```

* ✅ `arm_safe_negctl.rs` is a **genuine** negative control: `let r = &s.v;
  bump(&mut s); println!("{}", *r);` — a local struct, no heap, no growth, no
  container — and it prints `E0502` with the same wording as arm A. It cannot
  have p25's bug. No claim in the row rests on the error text: `NOTES.md` §10 and
  `README.md` both say `E0502` carries no information, and the published claim is
  the narrower *"the port that DOES compile has no bug"*.
* ⚠ **minor 7** — `p25`'s `identity` is **`norel` at BOTH levels** with
  `md5_raw_equal: false`. `spec.md:169` and `:427` disclose this in full, with
  the mechanism measured (`lea -0xde51(%rip)` vs `-0xde31(%rip)`, both resolving
  to `0x7910`; same 189 non-pad instructions and 751 bytes). But `NOTES.md` §8b
  — the file a reader goes to for numbers — asserts *"R4 == R5, **exactly**, in
  every kernel-only cell … the proof licenses the unsafe code at zero instruction
  cost"* and never mentions `norel`, while `.memory/03-measurement.md:611` says
  *"**quote the `md5` when saying a proof costs zero**"*. One cross-reference
  fixes it.

---

## 8. ITEM 8 + DELIVERABLE 3 — gate hygiene, and what the manager overstated

### 8.1 All three first-run failures independently confirmed closed

1. **shared named-spelling paragraph** — extracted `idiom.why` from p25's and
   p34's contracts and compared the tails from `NAMED-SPELLING STANDARD`:
   **11 003 bytes each, `sha256 59748cce2db5…` each, byte-identical, ending
   `p01 and p08 neither`.** Exactly what `NOTES.md` §0 claims.
2. **`SLB-TRUSTED-ARGUMENT` sections** — two present, matching the two items
   `_is_trusted` governs; the gate log prints both and the record is `PASS`.
3. **stale `controls/*.json`** — re-verified independently of the gate: all nine
   sidecars' `derived_from_sha256` entries (1–9 pinned sources each, 47 total)
   re-hash to the files on disk, **0 stale, 0 missing**, and every `problems`
   field is empty.

### 8.2 Detectors execute, and clang has not eliminated either

`controls/detectors.json` records both positive controls firing only in their own
detector at gcc `-O1`. I extended it to **clang at `-O1` and `-O3`**
(generator `.temp/t158/detectors_clang.sh`, log `.temp/t158/detectors_clang.log`,
`env -u LD_PRELOAD`, output never truncated with `head`):

```
ctl_asan  under asan  -O1 exit 1 ASan heap-use-after-free   -O3 exit 1 same
ctl_asan  under ubsan -O1 exit 0 "ctl_asan 85"/"ctl_asan 86"   -O3 exit 0 "ctl_asan 98"/"ctl_asan 99"
ctl_ubsan under asan  -O1 exit 0 "ctl_ubsan -2147483631"    -O3 exit 0 same
ctl_ubsan under ubsan -O1 exit 1 runtime error: signed integer overflow  -O3 exit 1 same
```

Neither is eliminated at any level; each licenses only its own column.

⚠ **minor 11, noticed by running the probe twice.** `ctl_asan`'s *non-ASan*
stdout **does not reproduce**: two runs of the same binary gave `85` then `86`
at `-O1` and `98` then `99` at `-O3` (it is a use-after-free reading recycled
heap). `controls/detectors.json` commits it as `"stdout": "ctl_asan 85"`. ✅ It
is inert — `detectors.py` asserts only `fired` for the controls, and asserts a
checksum only for **R1h**, whose semantics are deterministic — but it is a draw
recorded as a figure in a committed record, which is the class `RECAP` finding 4
names and which `.memory/06-catalogue.md`'s **own p25 row** warns about for this
very pattern. One `"stdout": "<non-reproducible, use-after-free>"` fixes it.

### 8.3 Miri is a real run, not the `TASK_148` non-run

The gate's `miri` block has `ran: true`, `available: true`, `probe_iters: 4`,
`miriflags: null`, and **all 8 rows carry a `stdout` that equals `model_stdout`**
— a non-run cannot produce that. `ub: false` on all 8. `controls/rust_bug.json`
is the matching must-fire half: `arm_unsafe_ptr.rs` gets
`memory access failed: allocNNNN has been freed` on exactly the three
growth-after-SAVE inputs and is **clean** on `adversarial-nogrow` and `small`,
so it is not an arm that fires on everything.

### 8.4 ⚠ `CAVEATS['p25']` — three manager overstatements

`harness/tools/composition.py:184–204`:

1. ⚠⚠ ***"manager-measured, `realloc` appears in 1 of 32 C rungs"*** — **the
   attribution is inverted.** The 1-of-32 is `controls/no_reloc.py`'s, the
   **engineer's**, comment-blanked. The *manager's* census
   (`.temp/mgr155/NOTES.md` §6) was refuted twice in the same commit that wrote
   this caveat, and the commit message says so in a section headed *"MY OWN
   `malloc` CENSUS WAS WRONG TWICE"*. Crediting the corrected figure to the party
   whose measurement was wrong is the worst possible provenance to attach to it.
2. ⚠ ***"exactly ONE of SIX doubling growths relocates"*** — **"six" is in no
   artefact.** `reloc_probe.json` records **one row per `realloc` call**:
   `adversarial-move` **5 calls** (2 initial + 3 growths), 1 moved;
   `adversarial-many` **7 calls** (2 initial + 5 growths), 1 moved;
   `adversarial-nogrow` 3 calls, 0 moved. The true statements are **1 of 3
   growths** and **1 of 5 growths**; there is no reading on which it is six.
   The row's own `README.md` prints the correct event lists.
3. ⚠ ***"every R1 answer is `min + 31*b` for the single stale byte `b`"*** —
   true only when the stale read is the **last** operation in the window. The
   Horner coefficient is `31^(k+1)` in general, and `adversarial-many` has four
   SAVE/grow/READ rounds. `NOTES.md` §2c states it correctly and generically
   (*"one byte in a Horner chain"*); the caveat sharpened it into something
   false. **The ≈1-in-256 conclusion survives either way.**

### 8.5 The `9b06f96` commit message

* ✅ *"ten patterns are at >= 20 `Ir`/call and p28 is at 1732.73"* — **correct**,
  reproduced exactly.
* ✅ *"5 of 32 (p27 p28 p29 p34 p42)"*, *"realloc in 1 of 32"* — **correct**.
* ⚠ *"~2x CHEAPER … **at every cell**"* — gcc only; clang is 5.0–5.5× (M5).
* ⚠ *"32 gate records … **64 measurement records** 0 STALE"* — there are **32**
  measurement records (33 `results/p*.json` files, one of which is the
  `p02-residue-sweep` side record). 64 is presumably 32+32; as written it is
  wrong — **minor 8**.

### 8.6 The `TEMPORAL 5 → 6` edit to `.memory/02-bench-rules.md`

Checked and **correct**: `15 of 31 → 15 of 32`, `1 → 6` with `p25 at TASK_157`
appended, and `harness/tools/composition.py --check` returns **`rc=0`, `OK:
published composition table matches the tree (32 patterns, 10 classes)`**. The
`temporal` class list and the published table agree.

---

## 9. DELIVERABLE 2 — is `p25` FINISHED? **NO.**

**The anchored PROTOCOL rule-1 check** (finding *headers* only, not mentions):

```
awk '/^## The findings so far/,/^## Retracted/' RECAP.md | grep -E '^[0-9]+\. ' > h
for d in patterns/p*/; do id=$(basename "$d" | cut -d- -f1)
  grep -q "\b$id\b" h || echo "MISSING: $id"; done
->  MISSING: p01        (the known benign exception — calibration row)
    MISSING: p25
```

**`p25` has no finding header in `RECAP.md`.** `p34`, missing one task ago, is
now present, so the check is working and the one new absence is real.

Other completeness facts, all measured:

| check | result |
|---|---|
| `results/synthesis.md` carries `p25` | **NO — zero occurrences.** It needs regenerating; I did not do it. See M3/M4 first: regeneration will *add* the false rows. |
| `results/tables/p25-realloc-growth.md` | exists; a fresh `harness/report.py p25 --stdout` is **byte-identical modulo one trailing newline** (42 097 vs 42 096 bytes; `rstrip("\n")` equal). Gate's `table_render: FRESH` is honest. |
| gate `source_sha256` | **53 entries, 0 stale, 0 missing** |
| measurement `source_sha256` | **18 entries, 0 stale, 0 missing** |
| `input_sha256` | **8 entries, 0 stale** (blobs are gitignored; `inputs/gen.py` is the generator) |
| `contract_sha256` | recomputed from `spec.md` = `c41099be4dfdc646…` = the record |
| `.memory/06-catalogue.md` p25 row | ⚠ still reads only *"ADMITTED AT `TASK_143`"* — **no BUILT/REVIEWED marker**. `p35`'s row has one; `p28`'s and `p34`'s do not either, so this is a class, not p25's alone — **minor 9** |

---

## 10. PROTOCOL rule 6 — fully verified, and ONE SENTENCE of the disclosure is false

✅ **The best rule-6 disclosure in the tree so far, and it is reconstructible.**
All four contract texts saved under `.temp/t157/` re-hash **exactly** to the four
claimed digests, and the shipped `slb-contract` block is byte-identical to the
last of them:

```
contract_first_written.json      54088d20a749069b…  OK   (= NOTES.md §0's pin)
contract_after_no_reloc.json     a4b9e5750361a1d9…  OK
contract_after_escapes.json      8cef5a43b154bd5f…  OK
contract_after_shared_para.json  c41099be4dfdc646…  OK   == the shipped block
```

⚠ **minor 10.** `NOTES.md` §0 closes with:

> *"**No `required`, `forbidden`, `identity`, `obligations`, `driver`,
> `collapse` or `miri` entry moved at any of the three steps** — checked by
> parsing each pair and diffing the objects."*

Parsing each pair and diffing the objects gives, per step:

```
step 1  /idiom/why
step 2  /idiom/why  /collapse/note  /identity[0]/why  /miri/reason
        /verus/obligations_note  /verus/twin_obligations_note      (-85-10-10-10-5-5 chars = 25 escapes)
step 3  /idiom/why
```

`identity`, `collapse` and `miri` **did** move, at step 2 — by exactly the 25
`⚠` → `⚠` normalisations the table above it describes and calls cosmetic,
and the six lengths sum to precisely 25 escapes. **No pin VALUE moved** — the
substance of the disclosure is sound. But the sentence a reviewer is invited to
trust *instead of re-checking* is literally false, which is the failure mode
rule 6 exists to prevent. The repair is one word: *"no pinned VALUE moved"*.

---

## 11. Hygiene

* **Restored by bytes.** Running `controls/no_reloc.py` rewrote its committed
  sidecar (`measured_utc` only). Restored with `git checkout --` and verified:
  `sha256 a68e7b17f1ea…` on disk == `git show HEAD:` == the same digest.
  `git status --porcelain` is clean apart from my report file. The census
  content is therefore **exactly reproducible**.
* No `.memory/`, `RECAP.md`, `results/`, `harness/`, `patterns/` or `pilot/`
  edit. No `git add`/`git commit`. No earlier `.temp/t*/` or `.temp/mgr*/`
  directory touched (read only).
* Instruments, all under `.temp/t158/`: `marg.py`, `marg2.py` (+ `.out`),
  `nullctl.py` (+ `.out`), `symdiff.py` (+ 4 `.json` and 4 `.log`), `search.py`
  (+ `search.json`, `search.log`, `search2.log`), `clangmarg.py` (+ `.log`),
  `detectors_clang.sh` (+ `.log`), `NOTES.md`, `composition.log`,
  `p25_render.md`. **CLAUDE.md rule 1 applied**: every binary, `.o`, `.bin` and
  callgrind blob has been deleted and every one is re-derivable by the script
  beside it (180 KB left, all `.py`/`.sh`/`.json`/`.log`/`.md`).

---

## 12. Clean negatives — named attacks that did NOT land

1. **The `p34`-distinctness argument was genuinely checked** by the engineer
   (`TASK_157_REPORT` §12), and it holds on the C code, not the vocabulary (§2).
2. **The one-growth-wide harm window was genuinely checked** — `reloc_probe.json`
   is the artefact, it shows `16 → 32` and nothing else on both compilers, and it
   *refuted the engineer's own prediction* about `32 → 64`. I did not re-run it.
3. **Are §3c's numbers contaminated by the whole-program artefact?** No — the
   `whole − kernel` offset is exactly constant across all six C arms at every
   cell (§4c). This was the biggest risk item 1 posed to this row.
4. **Do the shipped repairs' figures move under respelling?** No — `TERN` ≡ `R1h`
   and `PTR` ≡ `RD` to the hundredth at all four gcc cells.
5. **Is the `+269.52` an environment phase?** No — identical at pads 0 and 16,
   which `check_marginal_ir`'s own 16-wide-window argument makes a *complete*
   detector.
6. **`assume(false)`** — the gate FAILS on it (§7), the comment form is correctly
   not a hit, and no tree edit was needed to show it.
7. **Is `arm_safe_negctl.rs` a real negative control?** Yes — a local struct, no
   heap, no container; it cannot have p25's bug and it prints the same `E0502`.
8. **Is the ASan positive control eliminated by clang, or at `-O3`?** No — both
   controls execute and fire at clang `-O1` and `-O3`, each only in its own
   detector.
9. **Is Miri a non-run scored as "no UB"?** No — all 8 rows' `stdout` equals
   `model_stdout`.
10. **Are the control sidecars stale?** No — 47 pinned sources across nine
    files, 0 stale, verified independently of the gate.
11. **Do the gate and measurement records certify the tree on disk?** Yes —
    53 + 18 + 8 hashes, 0 stale, 0 missing; `contract_sha256` recomputes.
12. **Is `sanitizer_expect` a tautology of the model's representation?** No —
    `Heap.touch` keys on `blk.retired`, never on a length or an index.
13. **Is the row ASan-only?** No — a plain gcc `-O1` build diverges from
    `model.py` on exactly the three relocating inputs (§3).
14. **Does anything gate on `R1 ≠ R1h`?** No.
15. **Is `p25`'s TCB tally wrong?** No — 4 `external_body`, 2 governed, both
    twinned, `blocked: []`, and `NOTES.md` §9 states both denominators.
16. **Is the `TEMPORAL 5 → 6` edit or the composition table wrong?** No —
    `composition.py --check` returns `rc=0` on 32 patterns / 10 classes.
17. **Was the manager's tree-wide arithmetic wrong?** No — it reproduces entry
    for entry. Only its *reading* is wrong.

---

## 13. Recommended wording, for the manager to land (I did not fix any of it)

1. **`synthesis/synthesize.py`** — (a) replace the hardcoded *"Every one of those
   rows is in the uncertain 2.00–16.00 band … on all six"* with text derived from
   the same list that produced `broke`; (b) add a per-(pattern, blob) **null
   column** = the `R5−R4` derived correction, and refuse to print any other
   pair's correction as `CONFIDENT` when `|correction| <= |null|`. **No re-gate**
   — `synthesis/` is in neither hash glob.
2. **`harness/check.py::check_marginal_ir` docstring** (report only, do not
   edit): add one paragraph — *"⚠ This figure is WHOLE-PROGRAM and is therefore
   not a per-rung cost. Read cross-RUNG differences off `kernel_exclusive_ir`.
   The `R5 − R4` pair is the tree's own null on this column in `isolated` mode
   and reaches **+269.52** (p25) and **−31.00** (p42), both 100 % glibc malloc
   internals with byte-equal kernels and byte-equal `main`s. In `whole` mode the
   pair is NOT a null: the kernel is inlined and p11's `−494.00` is entirely the
   rungs' own code (`check_identity` compares `isolated` digests only)."*
3. **`CAVEATS['p25']`** — strike *"manager-measured"*, replace *"ONE of six
   doubling growths"* with *"one of the three (`adversarial-move`) / five
   (`adversarial-many`) growths `controls/reloc_probe.py` records"*, and replace
   `min + 31*b` with *"a one-byte divergence in a Horner chain"*.
4. **`p25/README.md` Headline 2 and `NOTES.md` §3c** — strike *"on both
   compilers"* from the dynamic claim, or take the clang column (it is 5.0–5.5×,
   `.temp/t158/clangmarg.py`); and demote *"the safer repair dominates"* to
   *"the cheapest standard-clean spelling found dominates at `-O3`; at `-O0` a
   growth-site repair is 3.3× cheaper again and the ordering reverses"*.
5. **`NOTES.md` §3c** — say the convention: *"kernel-exclusive"*.
6. **`NOTES.md` §0** — *"no pinned VALUE moved"* rather than *"no entry moved"*.
7. **`NOTES.md` §8a** — name six libc routines, not three, and quote the
   marginal to the instruction (`+269`), not the hundredth.
8. **`NOTES.md` §8b** — cross-reference `spec.md`'s `norel` disclosure beside
   *"R4 == R5, exactly"*.
9. **`.memory/06-catalogue.md`** — mark `p25` BUILT/REVIEWED (and, separately,
   `p28` and `p34`).
10. **`RECAP.md`** — `p25` owes a finding header; the anchored check names it.

---

**PROTOCOL rule 2 running count.** Launched from **898**. This review refuted
**four manager claims** (the tree-wide derivation's mode-mixing, the *"p11
kernel-identical at every cell"* inference, `CAVEATS['p25']`'s *"manager-
measured"* attribution and its *"one of six growths"*), **three engineer/row
claims** (*"on both compilers"*, *"the safer repair dominates"*, and `NOTES.md`
§0's *"no entry moved"*), and found **one pre-existing published falsehood** in
`results/synthesis.md` §5. **898 + 8 = 906.** ⚠ Reconciliation across branches is
the manager's job, not mine.
