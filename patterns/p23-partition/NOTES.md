# p23 — in-place Hoare partition: measurements and notes

## Rule 6 disclosure — the contract hash

`slb-contract` block, **as first written, before any measurement**:

```
30741 bytes   sha256 22240ee490dcea32b8da5900182f25a351e3d2881109a8f68cda6122e567dd9e
```

Recorded at TASK_101 before the first cell was built, which is the whole point
of `PROTOCOL.md` rule 6: a pattern lands in **one commit**, so *"no `required`
or `forbidden` entry moved after I measured"* is not otherwise checkable.

⚠ **The `git show HEAD:… | diff -` command PROTOCOL rule 6 quotes is VACUOUS on
a new pattern and was not run as evidence.** It compares the working tree to
`HEAD`; p23 does not exist in `HEAD`, so on a clean tree it prints nothing and
always looks like it passed. **The hash above is the only evidence**, exactly as
rule 6's own new-pattern clause says.

### The hash MOVED once, after the first gate run and before any measurement

```
31085 bytes   sha256 8251a6762b1043e4f5b1d7ebeee174a263c3f43467b6befae615e370868816af
```

Five edits, all of them disclosures rather than weakenings, and **no `required`,
`forbidden`, `obligations`, `identity` or `miri` entry changed meaning**:

| # | what moved | why |
|---|---|---|
| 1 | `required[7]`: backticks removed from *`p <= len`* | the gate's own audit reported it as *"pins nothing (0 of 2 C rungs)"* — no rung spells it, it is a property the guards maintain. The entry still pins `len - p < 8`, which every rung does spell. **A pin that matches nothing is noise, and removing it makes the declaration weaker in exactly one direction: fewer pins.** |
| 2 | `idiom.why`: the `k_r2`/`k_r3c` byte-identity figures relabelled as a PROBE's | `.memory/03-measurement.md`: a probe measures a slope and its intercept is a property of the probe. The transferable claim is the *equality*, not the 219 instructions. |
| 3 | `idiom.why`: the `.position(` price relabelled as a PROBE's, and the transferable claim narrowed to the ORDERING FLIP | same reason |
| 4 | `idiom.why`: the R4-side lever's `6.00 Ir/call` relabelled `6.00 probe-Ir/call` | same reason |
| 5 | `identity[0].why`: *"four loops"* → *"five loops"* | recount: record walk, outer partition, two scans, fold |

Nothing else in the block moved, and the first hash above is what a reviewer
should reconstruct edits 1–5 against.

---

## 0 — what this pattern is, and what it is not

p23 partitions a 64-byte scratch in place around a pivot the record supplies,
with Hoare's two-cursor **nested scan**: an outer loop, an upward scan, a
downward scan, an exchange. `c/kernel.c` omits the `i < j` conjunct from both
inner scan conditions and nothing else; `c/kernel_hardened.c` is that file plus
those two conjuncts.

**The reason to build the row is the SOURCE OF THE BOUND, not the bug class.**
The bug class is `index >= len` and it is the tree's **fifteenth** — RECAP's
replacement bar retired that as the admission test (*"another `cmp`/`jbe` in the
same place for the same reason"* is the question) and p23 clears the replacement
bar on all three limbs:

* **a new operator on the safety line** — the guard is a comparison of two
  *loop variables*, not of an index against a length;
* **a new source of the bound** — each cursor's bound is **the other cursor**,
  and both move. Every earlier bound here comes from outside the loop: a header
  field (p05, p07, p16, p17, p19, p36), a compile-time capacity (p03, p06, p12),
  a live length (p04, p14);
* **a new reason the check is or is not elided** — §9 measures it and it is the
  pattern's headline: **the direction of the induction variable decides**.

### What p23's obligation is, and the honest version of the novelty claim

TASK_101 §0 asked whether *"no built pattern has a multiset / permutation
obligation"*. Measured over all 24 built patterns' **pinned** `verus.items[*]`
`requires`/`ensures` (not just `verus.rs`), `grep -niE 'multiset|permut'`
returns **0 hits**, so the claim survives. ⚠ **And it is worth less than it
sounds, which was also measured:** the nested-scan partition verifies with the
multiset postcondition (`.temp/t101/pA_hoare_nested.rs`, **6 verified, 0
errors**) *and* with every multiset clause deleted (`pA2_no_multiset.rs`, **6
verified, 0 errors — same count**). The multiset is **separable**: it is not
load-bearing for the partition postcondition and not load-bearing for memory
safety, because the guarded form's bound `i < j <= m <= SCR` is positional. So
p23 ships the obligation it actually needs — an exact functional postcondition
(`part`) — and does **not** claim a permutation obligation it does not use.

What p23 *does* inherit from the permutation is the **fold rule**, in a stronger
form than p06's: a partition is a permutation of the loaded prefix on **every**
input, not merely in one regime, so a sum- or xor-fold could not observe the
partition at all. The fold is order-sensitive Horner over the full live extent,
plus the partition point.

---

## 1 — the disassembly: five loops, no vectorisation, in every rung

`-O3 isolated`, `nm --print-size` extent, padding excluded (from
`results/p23-partition.json`):

| cell | insns | bytes | backward branches | bulk call |
|---|---|---|---|---|
| `c-gcc` (R1) | 160 | 589 | 9 | — |
| `c-gcc-h` (R1h) | **157** | 587 | 10 | — |
| `c-clang` (R1) | 146 | 546 | 7 | `memcpy@plt` |
| `c-clang-h` (R1h) | 154 | 570 | 7 | `memcpy@plt` |
| `safe_naive` (R2) | 248 | 1068 | 6 | `memcpy@GLIBC_2.14` |
| `safe_tuned` (R3) | 223 | 936 | 6 | `memcpy@GLIBC_2.14` |
| `unsafe` (R4) | **157** | 647 | 7 | `memcpy@GLIBC_2.14` |
| `verus` (R5) | **157** | 647 | 7 | `memcpy@GLIBC_2.14` |

⚠ **The hardened gcc rung is SMALLER than the buggy one** — 157 against 160.
That is not a typo and §3 measures what it costs in executed instructions. gcc
inlines the copy at `-O3` and keeps no `memcpy` call at all; clang keeps one in
both C cells.

No vector registers in any cell (`vector_regs: []` for all 32). The fold is a
serial Horner chain and both scans are data-dependent `while` loops, so there is
nothing to vectorise; that is also the argument behind `model.py`'s
`work_per_call` floor.

`R4 ≡ R5` byte-for-byte at `-O3`: `md5_fn 43acbc727fc6`, 157 instructions, 647
bytes, both cells. At `-O0` they are `norel` (crate names differ in length, so
call displacements differ — link layout, not codegen). Both are what `spec.md`'s
`identity` pins and the gate enforces.

---

## 2 — why the fold has to be order-sensitive, and why it folds the index

A partition is a **permutation** of the loaded prefix. Unlike p06's rotate,
where the buggy and correct scratches coincide as multisets only in regime 1,
here they coincide on **every** input by construction — so a sum-fold or an
xor-fold would return the same value whether the kernel partitioned or did
nothing at all, and every rung would agree for the wrong reason. The fold is
therefore `acc = acc*31 + scr[q]` over `scr[0..m)`.

**And the partition point is folded on top of it**, `acc = acc*31 + i`. Without
that term a rung could return any index and no checksum would move; with it, the
`adversarial-inarray` row separates R1 from R1h **on the index alone** — the
scratch contents there are identical in both cells and only `i` differs
(4207869107238960256 against 4207864700635266816).

---

## 3 — the cost of the safety line in C: R1 against R1h

Kernel-exclusive `Ir` per call, `-O3 isolated` (`results/p23-partition.json`;
`small` = 5 records / 157 copied bytes per call, `large` = 12 records / 54):

| | `small` | `large` |
|---|---|---|
| `c-gcc` (R1, buggy) | 2816.81 | 1650.81 |
| `c-gcc-h` (R1h) | 2777.71 | 1590.47 |
| **R1 − R1h, gcc** | **+39.10** | **+60.34** |
| `c-clang` (R1, buggy) | 2350.03 | 1450.11 |
| `c-clang-h` (R1h) | 2353.15 | 1426.97 |
| **R1 − R1h, clang** | **−3.12** | **+23.14** |

⚠⚠ **THE SAFETY LINE HAS A NEGATIVE PRICE ON gcc, ON BOTH INPUTS.** Adding two
`i < j` conjuncts to the innermost loops makes the gcc kernel *smaller* (157 vs
160 static instructions) and *cheaper* (−39.10 / −60.34 `Ir` per call). p06
found the same sign on **clang** and for a different reason (narrowing `r` let
LLVM merge a four-byte decode); p23 finds it on **gcc**, and the mechanism here
is the trip bound: with `i < j` in the condition gcc can prove the scan is
bounded by `j - i` and rotates the loop; without it the scan is an unbounded
`do`-shaped walk that has to be laid out for an arbitrary trip count.

⚠ **And the clang column changes sign between the two inputs** (−3.12 on
`small`, +23.14 on `large`), which is why this table has four cells and not one
number. **Any p23 claim about "the price of the guard" that quotes a single
compiler or a single input is wrong at the sign level.**

---

## 5 — the Verus proof: one sentence, three loops, zero lemmas

`./verus_run.py patterns/p23-partition/verus.rs` → **`16 verified, 0 errors`,
first attempt**. With `--cfg slb_twin` → **`19 verified, 0 errors`**.

Per-item, each measured with `--verify-function <name> --verify-root`:

```
SCR 1 · part 1 · fold_scr 1 · walk 1 · scr_load 1 · kernel 6 · main 5   = 16
u32_at 0 · nrec_at 0 · zero_scr 0 · load_into 0 · swap2 0 · partition_fold 0
buf_get_unchecked 0 · scr_get_unchecked 0 · scr_set_unchecked 0
load_input 0 · emit 0
```

**The count is LOWER than p06's 18 and the pattern is harder.** p06 needs three
`proof fn`s because three reverses are not syntactically a rotation. p23 needs
**zero**, because the spec function `part` is written in the shape the loop nest
moves in: its three cases *are* the upward scan step, the downward scan step and
the exchange, so every loop invariant is the same sentence — *"the partition
from here is the whole partition"* — and Z3 discharges each step by unfolding
`part` once.

**The specification and the code are different algorithms**, deliberately.
`part` is the **single-loop three-way step**; the kernel is the **nested-scan**
form. `model.py` mirrors that split too: its simulation runs the nested scan and
its `partition_fold` helper runs the single-step rule.

⚠ **This is TASK_086's named kill risk for the row, and it is dead.** TASK_086
recorded *"p23's verified spelling is not the spelling its cost kernels
implement"* and TASK_101's task file sharpened it to *"the bug may live in the
form that does NOT verify easily."* Both spellings verify, both first attempt:
the single-loop form at `.temp/t86/v23_partition.rs` (`4 verified, 0 errors`)
and the nested-scan form at `.temp/t101/pA_hoare_nested.rs` (`6 verified,
0 errors`). The shipped R5 is the nested-scan form.

**One clause, `off + len <= buf@.len()`**, and it is structural — about the shape
of the buffer the driver built, not its contents. The proof assumes **nothing
about the pivot**: `pv == 0` and `pv == 255` are exactly the two values R1 dies
on and both are inside R5's verified domain. Checked call by call by the gate:
80 048 kernel calls across 9 inputs, `requires` evaluated on all of them,
`ensures` re-derived independently on 304.

`decreases j - i` is the measure at all three partition loops. The interesting
one is `part`'s third case, which shrinks it by **two**: that is only
non-negative because the case cannot fire at `j == i + 1`, where `s[j-1]` and
`s[i]` are the same slot and the case's own guards say it is both `> pv` and
`< pv`. Z3 gets that from congruence and nothing is asserted by hand.

---

## 6 — the trusted base: three items for one fact, and four bases for it

**TCB: 5 `external_body` items**, three of them contract-bearing:

| item | `requires` | what it licenses |
|---|---|---|
| `buf_get_unchecked` | `i < v@.len()` | the window header reads |
| `scr_get_unchecked` | `i < v@.len()` | both scans, the exchange's reads, the fold |
| `scr_set_unchecked` | `i < old(v)@.len()` | the exchange's two stores |
| `load_input` | — | argv, file I/O, LE decode |
| `emit` | — | `println!` |

`scr_load` is **verified, not trusted** — p06's TASK_048 route reused verbatim,
so the axiom relocates into vstd (`ref_mut_array_unsizing_coercion`,
`split_at_mut`, `copy_from_slice`) rather than vanishing.

**Four trusted bases for the one disjointness/bounds fact**, which is the
structural result and not a speed number:

| rung | who discharges `i < j <= m <= SCR` |
|---|---|
| R2 `safe_naive` | rustc, once per access, at run time |
| R3 `safe_tuned` | rustc for the scans; `core`'s own `unsafe` inside `<[T]>::swap` for the exchange |
| R4 `unsafe` | nobody — a comment |
| R5 `verus` | Z3, once, statically |

⚠ **`grep -rn get_unchecked ~/tools/verus/vstd/` → 0 hits, re-run at TASK_101.**
So the wrapper route is unavoidable, as it is for the eleven other patterns that
ship the same accessor.

### SLB-TRUSTED-ARGUMENT verus.rs buf_get_unchecked

(a) *Is the twin's body the right checked stand-in?* The trusted body is
`unsafe { *v.get_unchecked(i) }` and the twin's is `v[i]`. On a `&[u8]` Verus
gives the indexed read a `SliceIndexSpecImpl` precondition of `i < v@.len()`,
which is precisely what `get_unchecked` requires its caller to have discharged.
**Measured by the gate itself, not asserted:** stage 5c-twin deletes the
conjunct `i < v@.len()` from `buf_get_unchecked`'s `requires` and the twin then
reports `18 verified, 1 errors` — the checked implementation genuinely needs it.

(b) *Is the `ensures` complete?* The body performs exactly one unchecked read,
at index `i`, and returns it; it writes nothing, allocates nothing and reads no
second slot. `r == v@[i as int]` is a complete description of that. The failure
mode it cannot see is TASK_009_REVIEW's x4 — a body that *also* read `i + 1`
would satisfy this contract — and the backstops for that are the `-O3` identity
pin against R4 (`md5_fn 43acbc727fc6`, equal) and Miri on `unsafe.rs`, both
green on all nine inputs.

(c) *Does each clause mean the same thing in both configurations?* `v@.len()` is
the slice's view length in both; there is no `cfg`-dependent type here, and the
gate confirms the token `slb_twin` occurs nowhere in `verus.rs` but on the three
twin attributes, so the shipped and twin configurations differ in nothing but
the twin items.

### SLB-TRUSTED-ARGUMENT verus.rs scr_get_unchecked

(a) *Is the twin's body the right checked stand-in?* Trusted body
`unsafe { *v.get_unchecked(i) }`, twin body `v[i]`, on a `&[u8; 64]`. Verus
gives an indexed read on an array an obligation of `i < v@.len()`, and for a
`[u8; 64]` vstd's `array_len_matches_n` discharges `v@.len() == 64` from the
parameter type alone — which is why the `requires` is **one** conjunct and not
`i < v@.len(), v@.len() == 64`; p03's gate run refused exactly that second
draft. Gate stage 5c-twin deletes the conjunct and the twin reports
`18 verified, 1 errors`.

(b) *Is the `ensures` complete?* One unchecked read at `i`, returned; nothing
else. **This item is called from four places in the kernel** — the upward scan,
the downward scan, both halves of the exchange's read, and the fold — so its
`requires` is the single obligation that stands between R4 and both of R1's
overruns, upward at `scr[SCR]` and downward at `scr[-1]`. The `ensures` is a
value equality and it is what makes the loop invariants carry the *contents* of
the scratch, not merely its bounds; without it the gate's clause-deletion stage
reports `12 verified, 4 errors`, the largest such drop in this file.

(c) *Does each clause mean the same thing in both configurations?* Yes — same
type, same view, no `cfg` in the signature.

### SLB-TRUSTED-ARGUMENT verus.rs scr_set_unchecked

(a) *Is the twin's body the right checked stand-in?* Trusted body
`unsafe { *v.get_unchecked_mut(i) = x; }`, twin body `v[i] = x;`. Verus gives an
indexed store on a `[u8; 64]` an `IndexSetTrustedSpec` obligation of
`i < v@.len()`, the same fact `get_unchecked_mut` demands. Gate stage 5c-twin
deletes the conjunct: `18 verified, 1 errors`.

(b) *Is the `ensures` complete?* The body performs one unchecked write, of `x`
into slot `i`, and nothing else. The postcondition is a **whole-sequence**
equality, `final(v)@ == old(v)@.update(i as int, x)`, so it says both *"slot `i`
became `x`"* and *"nothing else moved"* — and the second half is load-bearing
here, because `swap2` is a composition of two `update`s and an `ensures` that
pinned only slot `i` would not compose with the partition invariant at all. It
also rules out p08's failure mode directly: a body that additionally wrote
`i + 1` disagrees with `old(v)@.update(i, x)` at slot `i + 1`.

⚠ **This item is where p23's WRITE half lives, and the write is downstream of a
missing READ guard.** R1 never writes out of bounds *directly* — its exchange is
still behind `if (i < j)`. What makes R1's exchange dangerous is that R1 can
reach it with `j` **wrapped**: the downward scan decrements past 0, `i < j` is
then true for a wild `j`, and the store goes to `scr[j - 1]` below the frame. So
this `requires` excludes a write that a missing *read* guard, one loop earlier,
made reachable — which is why `.memory/02-bench-rules.md`'s write rule reaches
p23 (the threshold the scan guard enforces **is** the scratch's live extent).

`x` has no precondition and the gate shouts about it every run; `spec.md`'s
`verus.unsafe_justifications` carries the argument. It is the parameter-coverage
false positive `.memory/04-verus.md` names (p03 first, p12 second, p06 third,
p23 fourth): `x` is stored and never used as an address, an index or a length.

(c) *Does each clause mean the same thing in both configurations?* Yes.

---

## 7 — the harm, per direction, at the gate's own flags

Both C rungs, all four (opt × mode) cells, from the gate's stage 4 and stage 7:

| input | what R1 does | R1h / R2–R5 |
|---|---|---|
| `adversarial-allbelow` (`pv = 255`) | **exit −11, SIGSEGV**, all 4 cells, both compilers. UBSan: `kernel.c:96 index 64 out of bounds for type 'uint8_t [64]'`; ASan: `stack-buffer-overflow` | exit 0, model checksum |
| `adversarial-allabove` (`pv = 0`) | **exit −11, SIGSEGV**, all 4 cells, both compilers. UBSan: `kernel.c:101 index 18446744073709551615 out of bounds` — the wrapped `j - 1` | exit 0, model checksum |
| `adversarial-both` | SIGSEGV; UBSan names the **upward** one first | exit 0, model checksum |
| `adversarial-single` (`m == 1`) | **exit 0, SILENT, and NON-DETERMINISTIC ACROSS BUILDS**: **eight C cells, eight distinct checksums**, none of them the model's — gcc `2771782152875008` / `2772663473613696` / `2773544794352384` / `2774426115091072`, clang `2762968945488128` / `2784120643216640` / `2798307064139327` / `2812321731838034`. UBSan: `index 64 out of bounds` | exit 0, model checksum (all 8 checked cells agree) |
| `adversarial-inarray` | **exit 0, wrong answer, ASan+UBSan CLEAN.** `4207869107238960256` against the model's `4207864700635266816` | exit 0, model checksum |

⚠ **The one-element row is the sharpest and it was not in the plan.** Nothing
about `adversarial-single` is malformed — one element, a pivot, a partition
that is already done — and the record cannot be made benign, because one byte
cannot be both strictly above and strictly below the pivot. **All eight C cells
print a DIFFERENT wrong number and none of them crashes**; the value is whatever
byte happened to sit past the frame, so it is a function of the build and not of
the input. It is unstable under a COMMENT-ONLY edit, measured: an earlier gate
run of the same sources with three comment lines changed in `c/kernel.c` gave
gcc only 3 distinct values instead of 4, and every one of the eight numbers
moved. That is p12's magnitude ladder without the magnitude — the overrun is one
byte and the observable is an eight-way split — and it is the cleanest instance
in this tree of a bug whose *output* is a property of the binary's layout rather
than of the program.

**The `inarray` row is the in-bounds middle regime**, p23's analogue of p06's
regime 1: record 2's upward scan has no sentinel in its own `scr[0..16)` but
finds one in record 1's leftovers at `scr[16..48)`, so it stops **inside** the
array. No sanitizer fires and no rung panics, and the only thing that differs is
the folded partition point. **That row is asserted at generation time**, not
hoped for — `inputs/gen.py` refuses to write it unless R1 both diverges and
stays inside the scratch.

### Control B — the textbook pivot does not rescue the non-strict comparisons

`controls/guard_variants.c` + `controls/run.sh` → `controls/controls.log`.
`k_selfpivot` takes `pv = scr[0]`, the choice that makes real Hoare partition
self-terminating, and keeps the `<=`/`>=` this pattern pins:

```
selfpivot, ALL-EQUAL record (mode=1):
  plain gcc -O2   exit 0, prints 3910418957284214752
  ASan            stack-buffer-overflow at guard_variants.c:186 in k_selfpivot
  UBSan           index 64 out of bounds for type 'uint8_t [64]'
selfpivot, MIXED record (mode=0)  -- the must-be-clean arm:
  plain/ASan/UBSan  all exit 0, all print 7500084040178903629
```

**Positive control, same binary and same command line:** `bug` on the all-below
record fires ASan (`stack-buffer-overflow`, exit 1) and UBSan (`index 64`, exit
1) and SIGSEGVs unsanitised (exit 139); `bug` on the all-above record fires
`stack-buffer-**underflow**` and `index 18446744073709551615`. The `ij` and `mz`
cells are clean on every one of those runs. So neither the fire nor the
all-clear could have been produced by a probe that does nothing.

---

## 8 — control A: `i < j` is a SPELLING pin, not a semantics pin

⚠⚠ **A CLAIM THIS PATTERN SHIPPED IN DRAFT AND ITS OWN CONTROL REFUTED, BEFORE
MEASUREMENT.** `c/kernel_hardened.c` originally said that the alternative guard

```c
while (i < m && scr[i]   <= pv) i++;
while (j > 0 && scr[j-1] >= pv) j--;
```

is *"safe, and WRONG"* — memory-safe but computing a different partition point,
because the upward cursor could pass the downward one. **That is false.**
`controls/guard_equiv.py`:

```
  full 0..255    trials=400000 differing=0
  narrow 0..4    trials=400000 differing=0
  must-fire arm: a partition of the same bytes at m=32 vs m=64 differs: True
  verdict: EQUIVALENT
```

and `controls/guard_variants.c`'s `k_ij` and `k_mz` print the same checksum on
every record `run.sh` tries, benign and adversarial alike. The invariant the
draft missed is one line: **after an exchange `scr[j] > pv`**, because that is
the element the exchange just put there, so the next upward scan stops at or
before `j` whatever its guard says; symmetrically `scr[i-1] < pv` stops the
downward scan at or above `i`. The cursors cannot cross.

So `spec.md` pins a **spelling** here, and says so. Static price of the choice,
`gcc -O2`, linked binary, from `controls/controls.log`:

```
k_ij         586 B      <- the shipped spelling
k_mz         608 B
k_bug        614 B      <- no guard at all
k_selfpivot  612 B
```

**What is NOT a spelling choice is having no guard at all**, which is R1.

---

## 9 — the safety tax, its mechanism, and the parameter that is NOT `n`

### 9a. the shipped cells

Kernel-exclusive `Ir` per call, `-O3 isolated`:

| difference | `small` (5 rec / 157 B) | `large` (12 rec / 54 B) |
|---|---|---|
| `safe_naive − unsafe` (R2 − R4) | +350.69 | +531.17 |
| `safe_tuned − unsafe` (R3 − R4) | **+305.74** | **+443.55** |
| `safe_naive − safe_tuned` (R2 − R3) | +44.95 | +87.62 |
| `unsafe − verus` (R4 − R5) | **0.00** | **0.00** |
| `c-gcc-h − unsafe` | +390.77 | +91.50 |
| `c-clang-h − unsafe` | **−33.79** | **−72.00** |

⚠ **The C-vs-Rust sign depends entirely on the compiler**: hardened clang C is
*cheaper* than unsafe Rust on both inputs, hardened gcc C is *dearer* on both.
A p23 claim about C against Rust that quotes one compiler is backwards half the
time. (Reviewer checklist: *"any C-vs-Rust claim without a clang column?"*)

⚠ **`R4 − R5 = 0.00` is a tautology here**, forced by the `identity` pin, and
the wall clock is not: `unsafe` reads 519.25 ns/call median on `small isolated`
against `verus`'s 554.29 for a **byte-identical kernel**. That is the
source-path-length artefact `.memory/03-measurement.md` records; the pair is a
**biased draw of size one** and no p23 wall-clock claim rests on it.

### 9b. the R2 → R3 levers, priced separately

Probe figures (`.temp/t101/cost23.rs`, marginal whole-program `Ir`/call, fixed
driver, `-O` isolated, debug-assertions **off**, median-pivot band). ⚠ A probe
measures a slope; what transfers is the ordering and the zero:

| lever | against R2 |
|---|---|
| `<[T]>::swap` for the exchange | **0.00** — and the two kernels have the same padding-stripped normalised disassembly |
| two-step window reslice | −38.00 |
| `iter().fold` for the checksum | −16.00 |
| both (the shipped R3) | −46.00, i.e. **+8.00 interaction, not additive** |

**So R3's whole advantage over R2 is the header reslice and the fold, and none
of it is the exchange** — the operation the pattern is named for. The shipped
cells agree in direction: R2 − R3 = +44.95 / +87.62.

**The R3-side span, cheapest to dearest found in contract** (probe, median
band): 3141.00 … 4208.00, six spellings. **The R4-side span**: 2876.00 … 3050.00,
four spellings. The shipped R4 sits at 2882.00, i.e. **6.00 above the cheapest
R4 found**; the lever not taken is resliced-window addressing, held out because
R4 must be byte-identical to R5 and `split_at` on the window has not been shown
to verify at the pinned vstd. **The R4 endpoint is fixed BY FIAT and this
paragraph is the disclosure `.memory/01-ladder.md` asks for. No pair interval is
published.**

⚠ **The excluded `.position(`/`.rposition(` spelling is the DEAREST R3 at the
median pivot (4208.00) and the CHEAPEST at the minimum-rank pivot (2812.30, 328
below R2).** A rung built on it would make p23's safe-side headline a function
of which band was measured.

### 9c. ⚠⚠ THE LAW, ITS DOMAIN, AND THE PARAMETER THE DOMAIN IS ABOUT

Re-fitted against the **committed sweep bands**, not against the two matrix
inputs (`controls/sweep_fit.py`, `controls/sweep_fit.json`; regenerate with
`inputs/gen.py --sweep`). Band M holds `nrec = 8` and the pivot rank at 0.50 and
sweeps the live extent `m` from 2 to 48:

```
BAND M least squares  R3-R4 = 29.430/record + 0.7066/byte
                      R2-R4 = 38.279/record + 0.7405/byte
  residuals (R3-R4):  m=2 +19.26 · m=4 -8.92 · m=8 -7.18 · m=16 -6.35
                      m=24 +0.53 · m=32 -1.16 · m=40 +0.37 · m=48 +3.46
```

(The two-point fit from `small` and `large` alone gives 32.9/record +
0.899/byte, and it is exactly determined, so it has no residual to look at —
which is arithmetic, not evidence. The band is what the law now rests on.)

**Band K holds EVERY size regressor fixed — `m = 32`, `nrec = 8`, 256 copied
bytes per call — and sweeps only the PIVOT'S RANK:**

```
 nlow  rank      R2        R3        R4      R3-R4     R2-R4
    1  0.03  4378.41   4296.41   3590.04    706.37    788.37
    4  0.12  4436.77   4355.62   3714.29    641.33    722.48
    8  0.25  4481.97   4401.22   3843.33    557.89    638.64
   16  0.50  4406.31   4325.67   3912.18    413.49    494.13
   24  0.75  4098.96   4018.86   3715.91    302.96    383.06
   28  0.88  3869.21   3787.46   3532.46    255.00    336.75
   31  0.97  3657.25   3575.50   3348.50    227.00    308.75
```

⚠⚠ **`R3 − R4` moves from 227.00 to 706.37 — a factor of 3.11 — with `n`, the
record count and the copied-byte count ALL HELD CONSTANT.** The band-M law
predicts **416.32** for every one of those seven rows. **p23 is the first
pattern in this tree whose safety tax is a function of the data's SHAPE rather
than its SIZE**, and any p23 number quoted without its rank is quoted without
its domain. `small` and `large` are deliberately built at different mean ranks
(0.44 and 0.28) and `inputs/gen.py::_check_residues` refuses to write them
otherwise.

Fitted on band K, `R3 − R4 = 187.3 + 16.01·(m − nlow)` per call — that is
**2.00 `Ir` per record per DOWNWARD scan step**, plus a rank-invariant 23.4 per
record. Residuals ±30 over a 227…706 range, so it is a good description and not
an exact law; the curvature is not modelled here.

### 9d. THE MECHANISM: the direction of the induction variable decides

`(m − nlow)` is the number of steps the **downward** scan takes. Isolating the
two scans one at a time (probe, `k_up` = upward unchecked only, `k_dn` =
downward unchecked only, against `k_r3c` = both checked and `k_r4b` = both
unchecked):

```
RANK    k_r3c     k_up      k_dn      k_r4b
  3%   4460.00   4460.00   3972.00   3972.00
 50%   4492.00   4492.00   4308.00   4308.00
 97%   3764.00   3764.00   3778.00   3778.00
```

**`k_up == k_r3c` exactly at all three ranks, and `k_dn == k_r4b` exactly at all
three.** So:

> **LLVM already elides the UPWARD scan's bounds check, and does not elide the
> DOWNWARD one's. The whole of p23's scan-side safety tax is `scr[j - 1]`.**

The reason is the direction of the induction variable, and it is the finding:

* `scr[i]` — `i` starts at 0, increases monotonically, and the loop condition
  gives `i < j <= m <= 64`. LLVM's range analysis proves `i < 64` from the
  induction variable's own recurrence. **Free.**
* `scr[j - 1]` — `j` starts at a *runtime* `m` and **decreases**. The check needs
  `j - 1 < 64`, which is implied by `j <= m <= 64`, but the index is also a
  *subtraction* on an unsigned, so the same expression additionally has to be
  shown not to wrap. LLVM keeps the check. **≈2.00 `Ir` per step.**

That is a new entry in this project's list of reasons a bounds check does or
does not survive — the earlier ones are all about where the bound *comes from*
(p19's state-range `cmp $0x8`, p05's per-row hoist, p46's header-derived range
facts). Here both bounds are provable and only one is *proved*, and the
difference is which way the cursor walks.

⚠ **What this does NOT say:** it does not say the downward check is
unnecessary. R5 proves both, and `c/kernel.c` proves neither — §7 is what
happens then.

---

## 10 — what is not measured here

* **No `-C debug-assertions=on` column.** §3 of TASK_101 warns that
  debug-assertions enable `assert_unsafe_precondition!` inside `get_unchecked`
  and that on 3 of 3 patterns R4 becomes dearer than R3 at `-O3` with it on.
  Every figure in this file is **debug-assertions OFF**, which is the gate's own
  setting, and the alternative column was not run for p23.
* **No wall-clock claim.** The wall numbers are in
  `results/p23-partition.json`; the R4/R5 pair alone spans 519…554 ns for a
  byte-identical kernel, which is the floor on what a p23 timing claim could
  mean.
* **Band X and band N are shipped and were not fitted.** `sweep_fit.py` reads
  bands M and K only. The other two are committed and re-derivable.
* **The `<`/`>` variant of the comparisons is not built as a rung.** It is a
  different program (its partition point differs by one on any record with a
  byte equal to its pivot) and it is excluded by contract, not measured.

### A clean negative, so nobody re-runs it

⚠ **`check.py` sets no `MIRIFLAGS`, and Miri's alignment check is
seed-dependent** — the same source can be clean on `-Zmiri-seed=0,2` and report
UB on `1,3`. **That defect does not bite p23**, checked rather than assumed:
`unsafe.rs` run under Miri at `-Zmiri-seed=` 0, 1, 2 and 3 against
`adversarial-both.bin`, `adversarial-single.bin` and `degenerate.bin` gives
**0 UB reports in all twelve runs**, and all twelve checksums equal `model.py`'s
exactly. The reason it cannot bite is structural: every unchecked access here is
a `u8` read or write into a `[u8; 64]` or a `&[u8]`, so there is no alignment
question for the seed to randomise.
