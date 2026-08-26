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

Five edits. ⚠ **The headline this paragraph carried until TASK_106 was FALSE and
its own table refuted it** (TASK_105 m1): it read *"all of them disclosures
rather than weakenings, and no `required`, `forbidden`, `obligations`, `identity`
or `miri` entry changed meaning"*, while **row 1 below says `required[7]` lost
its backticks** and that removing them *"makes the declaration weaker in exactly
one direction: fewer pins"*. Under the declaration's own named-spelling standard
**backticks are the trigger** — `harness/check.py::spelling_matches`'s selftest
case reads *"an entry with no backticks pins nothing and reports nothing"* — so
un-backticking a spelling **is** a `required` entry changing meaning, and it
**is** a weakening. The edit itself stands (the gate reported the pin as matching
0 of 2 C rungs); the summary sentence did not. **PROTOCOL rule 6 is explicit that
a false disclosure is worse than the thing it describes**, because a disclosure
is what a reviewer trusts *instead of* re-checking, and this is also rule 13's
shape: the header asserting what the body underneath refutes.

**The corrected disclosure: ONE of the five edits is a weakening (edit 1, one
pin removed from `required[7]`); the other four are relabellings of prose inside
`why` keys and change no entry's meaning. No `forbidden`, `obligations`,
`identity` or `miri` entry moved at all.**

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
  pattern's headline: **LLVM elides ONE of two scans of the same array and not
  the other**, an asymmetry no earlier pattern here shows. ⚠ **The CAUSE is
  OPEN.** This limb used to read *"the direction of the induction variable
  decides"*; §9d now records the two isolations that refute it (TASK_105 M4).
  A limb that claims a new *reason* owes an isolation and not just a
  measurement — the phenomenon is what ships, and it is enough.

### What p23's obligation is, and the honest version of the novelty claim

TASK_101 §0 asked whether *"no built pattern has a multiset / permutation
obligation"*. Measured over all 24 built patterns' **pinned** `verus.items[*]`
`requires`/`ensures` (not just `verus.rs`), `grep -niE 'multiset|permut'`
returns **0 hits**, so the claim survives.

⚠⚠ **THE SENTENCE THAT USED TO STAND HERE IS RETRACTED, AND ITS EXPERIMENT WAS
MEASURING A VACUOUS POSTCONDITION** (TASK_105 A.2). Until TASK_106 this paragraph
read *"the nested-scan partition verifies with the multiset postcondition
(`.temp/t101/pA_hoare_nested.rs`, **6 verified, 0 errors**) and with every
multiset clause deleted (`pA2_no_multiset.rs`, **6 verified, 0 errors — same
count**). The multiset is **separable**."* Both `6/0` figures are real and
re-run at TASK_106, **but a matched pair of `6/0`s is not evidence of
separability, because `pA2`'s remaining postcondition admits a degenerate
body.** Spliced one in — zero `v[0..m)`, never compare against `pv`, return `m`
— and measured:

```
.temp/r105/pB2_no_multiset_DEGENERATE.rs  ->  4 verified, 0 errors   <- pA2's, multiset DELETED
.temp/r105/pB1_multiset_DEGENERATE.rs     ->  3 verified, 1 errors   <- pA's,  multiset KEPT
                                              error: postcondition not satisfied
```

**The must-fire arm is `pB1` and it fires.** With `p == m`, `forall k in [p, m)`
is vacuous, `forall k < m: v[k] == 0 <= pv` holds for every `u8` pivot and the
tail is untouched, so a body that never looks at the pivot satisfies the whole
of `pA2`. **`pA2` measures nothing about the multiset.**

✅ **The CONCLUSION stands, on better evidence, and the better evidence is about
the SHIPPED rung rather than about a probe.** p23 ships an exact functional
postcondition, `r == partition_fold(buf@, off, len)`, and the reason is not that
the multiset is separable — it is that `partition_fold` **implies** the multiset
and more: it is an order-sensitive Horner chain over the exact final scratch plus
the returned index, and a multiset is invariant under permutation where
`fold_scr` is not. **Measured against the shipped `verus.rs`: nine mutants, nine
failures, three controls verifying** (`.temp/r105/mk_mutants.py`,
`mk_mutants2.py`) — four degenerate bodies (zero the prefix and report `i = m`;
zero it and report `i = 0`; write the pivot everywhere; swap nothing and return
immediately), a correct partition folding the index as `0`, an upward-scan-only
body, and three deleted proof clauses. **9 of 9, against p24's 7 of 8 and p29's
3 of 4 — the strongest mutation result in the tree.**

⚠ **Two soft spots were closed rather than counted as passes, and that is what
makes the 9/9 worth quoting.** Four mutants first failed on the *hand-written*
tie `assert`, which a degenerate author would simply delete; re-run with it
deleted they still fail, now on **`invariant not satisfied at end of loop body`**
— the invariant that carries the postcondition. Three first failed on
**`Resource limit (rlimit) exceeded`**, which is a timeout and **not** a
refutation; re-run at `--rlimit 200` and `2000` they fail on the invariant too.
The final tally of *reasons*: **7 × `invariant not satisfied`, 1 × `precondition
not satisfied` (the trusted accessor's `requires` stops discharging), 1 ×
`assertion failed`. No timeouts, no `postcondition` fig leaves.**

**The controls**: a byte-identical splice through the same find-and-replace path
verifies `16/0` (`c01_identity.rs`, `diff` against the shipped `verus.rs` empty
— re-checked at TASK_106), a cosmetic ghost reorder verifies `16/0`, and the
shipped body **with the tie `assert` deleted** verifies `16/0`. So a mutant that
fails did not fail because the splice broke the file, and the noassert arm is a
real strengthening rather than a different experiment.

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

⚠⚠ **ON THESE TWO INPUTS THE SAFETY LINE HAS A NEGATIVE PRICE ON gcc.** Adding
two `i < j` conjuncts to the innermost loops makes the gcc kernel *smaller* (157
vs 160 static instructions) and *cheaper*: **the guard's price, `R1h − R1`, is
−39.10 / −60.34 `Ir` per call**, i.e. `R1 − R1h = +39.10 / +60.34`. p06 found the
same sign on **clang** and for a different reason (narrowing `r` let LLVM merge a
four-byte decode); p23 finds it on **gcc**.

⚠ **THE TWO SPELLINGS OF THAT ARE NOT INTERCHANGEABLE AND THE ROW SHIPPED WITH
THEM SWAPPED** (TASK_105 M2). The table above differences `R1 − R1h`, which is
**positive** when the guard is cheap; the prose used to say *"cheaper (−39.10 /
−60.34)"* in the same breath, which is the **guard's price** and the opposite
convention. Both readings are true of the same measurement and one of them was
copied into `.memory/` as a claim about `R1 − R1h`, where it inverted the sign of
**the one quantity whose entire point is its sign**. Write the quantity's name
next to every figure here.

⚠ **And the clang column changes sign between the two inputs** (−3.12 on
`small`, +23.14 on `large`), which is why this table has four cells and not one
number. **Any p23 claim about "the price of the guard" that quotes a single
compiler or a single input is wrong at the sign level.**

### ⚠⚠ 3a. …AND THE gcc SIGN IS A PROPERTY OF THE PIVOT'S RANK, NOT OF THE KERNEL

**p23's own rule — §9c's *"any p23 number quoted without its rank is quoted
without its domain"* — was never applied to p23's own C row, and it is exactly
where it bites** (TASK_105 M3). Measured over all **31** shipped band-K points
(`m = 32`, `nrec = 8`, 256 copied bytes per call, only the pivot's rank moving),
same `-O3 isolated` binaries and the same `controls/sweep_fit.py::kernel_ir`
pipeline as §9c, re-derived at TASK_106 (`.temp/t106/band_all.py`):

```
GUARD PRICE on gcc = c-gcc-h minus c-gcc, kernel-exclusive Ir/call
  nlow rank      up      dn      sw  rounds      c-gcc   c-gcc-h   guard price
     1 0.03    8.00  248.00    7.63   15.63    4218.67   4387.15     +168.48
     4 0.12   32.00  224.00   27.23   34.37    4384.68   4457.73      +73.04
     6 0.19   48.00  208.00   39.26   46.12    4488.43   4499.98      +11.54
     7 0.22   56.00  200.00   42.78   50.16    4524.52   4511.65      -12.87
    16 0.50  128.00  128.00   64.61   71.24    4686.41   4541.82     -144.59
    24 0.75  192.00   64.00   48.73   54.84    4462.70   4393.14      -69.56
    27 0.84  216.00   40.00   33.51   40.52    4291.40   4292.84       +1.45
    31 0.97  248.00    8.00    7.75   15.50    3991.88   4131.75     +139.87
```

⚠⚠ **`+168.48` at rank 0.03, `−144.59` at rank 0.50, `+139.87` at rank 0.97 —
TWO ZERO CROSSINGS**, located between `nlow` 6 and 7 and between 26 and 27.
`small` and `large` sit at mean ranks **0.44 and 0.28**, both inside the negative
window, and **`inputs/gen.py::_check_residues` REFUSES to write them unless they
straddle 0.35** — i.e. the generator enforces that both stay in the middle. And
on p23's own **mixed** band the price is positive at every point:
`sweep-x04 +46.91 · x06 +61.84 · x08a +61.23 · x08b +60.20 · x11 +19.57`.
**So *"the safety line has a negative price on gcc"* is a statement about the two
shipped inputs' pivot ranks and not about the kernel.**

⚠ **AND THE MECHANISM THIS SECTION USED TO GIVE IS REFUTED.** It read *"the
mechanism here is the trip bound: with `i < j` in the condition gcc can prove the
scan is bounded by `j - i` and rotates the loop"*, which predicts a saving
proportional to **scan steps**. Fitted over the same 31 points
(`.temp/t106/fit.py`):

```
regressor            coefficients                      R^2   max|res|
dn (scan steps)      -58.3744 +0.1992                0.0227     196.65
sw (exchanges)      +194.4765 -5.1970                0.9730      27.19
rounds              +237.6494 -5.3508                0.9739      22.90
dn + sw             +169.0928 +0.1981 -5.1963        0.9955      17.67
```

⚠ **Scan steps explain 2% of the variance; exchanges explain 97%.** The gcc
guard's price is ≈ **`+195` flat per call `− 5.2 Ir` per exchange** — it is paid
in the **round/exchange** path and not in the scans at all.

**A CANDIDATE for the replacement mechanism, offered as consistent with the
regression and NOT as proved** (TASK_105 M3, `harness/asm.py`, `-O3 isolated`,
whole `kernel` extent): the `cmp` count is **identical** (14 vs 14) and the
guarded kernel has **four fewer `mov`s**; per *scan iteration* the guarded loops
are **bigger** (up 5 vs 4 instructions, down 6 vs 5), so the saving cannot be in
the scans. R1's downward loop carries the cursor as
`mov %rcx,%rax ; lea -0x1(%rcx),%rcx` with the load at `-0x1(%r9,%rax,1)`, so the
exchange must reconstruct `j` and `j−1`; R1h decrements `%r13` in place and loads
at `(%rax,%r13,1)`. **What is MEASURED is that the published mechanism predicts
the wrong regressor. Which instruction sequence replaces it is OPEN.**

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
| `adversarial-single` (`m == 1`) | **exit 0, SILENT, and NON-DETERMINISTIC ACROSS BUILDS**: **eight C cells, SEVEN OR EIGHT distinct checksums** (gcc 3 or 4, clang 4 — it varies between runs of the same sources), none of them the model's `2705683097473408`. ⚠ **The values themselves move on every gate run and are NOT transcribed here — see below.** UBSan: `index 64 out of bounds` | exit 0, model checksum (all 8 checked cells agree) |
| `adversarial-inarray` | **exit 0, wrong answer, ASan+UBSan CLEAN.** `4207869107238960256` against the model's `4207864700635266816` | exit 0, model checksum |

⚠ **The one-element row is the sharpest and it was not in the plan.** Nothing
about `adversarial-single` is malformed — one element, a pivot, a partition
that is already done — and the record cannot be made benign, because one byte
cannot be both strictly above and strictly below the pivot. **Every C cell
prints a wrong number and none of them crashes**; the value is whatever byte
happened to sit past the frame, so it is a function of the build and not of the
input.

⚠⚠ **THIS SECTION USED TO TRANSCRIBE EIGHT SPECIFIC CHECKSUMS AND CALL THEM
EIGHT DISTINCT VALUES. IT WAS WRONG TWICE OVER, AND THE SECOND WAY IS THE
INTERESTING ONE.**

**First (TASK_105 M1): it was quoting a SUPERSEDED gate run, and it described the
two runs in REVERSE ORDER.** Three runs of these sources were kept at TASK_101,
plus two of TASK_106's:

| run | what | gcc distinct | clang distinct | total |
|---|---|---|---|---|
| 1 | `.temp/t101/gate1.log`, 15:44 | 3 | 4 | 7 |
| 2 | `.temp/t101/gate2.log`, 16:01 | **4** | 4 | **8** ← the eight numbers this file used to publish |
| 3 | `.temp/t101/gate_final.log`, **16:07** | 3 | 4 | 7 ← wrote the record TASK_101 committed |
| 4 | a TASK_106 `check.py p23` | 3 | 4 | 7 |
| 5 | the next TASK_106 `check.py p23`, minutes later | **4** | 4 | **8** |

Run 3's mtime matched `results/gate/p23-partition.json`'s to the second, so **it
was the LATER run and the committed one** — and this section used to call it
*"an earlier gate run … gave gcc only 3 distinct values instead of 4"*, exactly
backwards. Of run 2's eight published values, **one** survived into run 3 and
**none** into run 4 (`.temp/t106/m1_record.py`, `m1_run4.txt`).

⚠⚠ **Runs 4 and 5 are the same command, on the same sources, minutes apart, in
the same task — and they disagree on the DISTINCT COUNT as well as on every
value.** *"Seven distinct"* is the right correction to *"eight distinct"* and is
**still not a stable fact**.

⚠⚠ **Second, and this is why no numbers are transcribed here any more: quoting
them CANNOT be made to stay true.** `NOTES.md` is hashed into the gate record's
`source_sha256`, so **every edit to this file forces a gate re-run — and every
gate re-run rebuilds the C cells and moves these eight values.** The last gate
run therefore always postdates the last edit to the sentence describing it.
**A transcription of them is stale the moment it is written.** TASK_106
demonstrated this on itself **twice**: it corrected the eight numbers to run 3's,
re-ran the gate as its definition of done, and run 4 moved seven of the eight; it
then deleted the transcription, and run 5 — the same command minutes later —
moved all eight again *and* changed the distinct count from 7 to 8.

**So what this row publishes is the INVARIANT, and the record is where the
values live:**

```
  8 buggy C cells on adversarial-single.bin, all four (opt x mode) each compiler
    exit 0, no signal, no sanitizer output in the plain build      -- every run
    all 8 diverge from the model's 2705683097473408                -- every run
    both hardened C rungs print the model's value in all 8 cells   -- every run
    the number of DISTINCT values                                  -- RUN-DEPENDENT
    the per-cell values                                            -- MOVE EVERY RUN
```

**The two run-dependent lines are deliberately not given numbers.** The table
above records the runs that were logged; later runs are free to produce something
else, and TASK_106's did — it ran the gate repeatedly while landing this section
and got **both 7 and 8, with a different set of values every single time.**
**This file is written so that the next run cannot make it wrong.**

Across every run measured, **each of the eight cells has taken at least two
different values**, and no run has produced the same set as any other. That is
p12's magnitude ladder without the magnitude — the overrun is one byte and the
observable is a seven- or eight-way split — and it is the cleanest instance in this tree of
a bug whose *output* is a property of the binary's layout rather than of the
program. ⚠ **Nothing is pinned on these values**: `model.expected_exit` is 0, the
stdout is *recorded* under `adversarial/…` with `diverges: true` and never
*required*, and none of the numbers appears in `spec.md`, `model.py`,
`inputs/gen.py` or `results/p23-partition.json`. **The gate is indifferent to
them; only this file was not.**

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
band): **2991.00 … 3719.00, twelve spellings** — see 9b′, which corrects **both**
endpoints. **The R4-side span**: 2876.00 … 3050.00,
four spellings. The shipped R4 sits at 2882.00, i.e. **6.00 above the
cheapest R4 found**; the lever not taken is resliced-window addressing, held out
because R4 must be byte-identical to R5 and `split_at` on the window has not been
shown to verify at the pinned vstd. **The R4 endpoint is fixed BY FIAT and this
paragraph is the disclosure `.memory/01-ladder.md` asks for. No pair interval is
published.**

### ⚠⚠ 9b′. BOTH ENDPOINTS OF THE PUBLISHED R3-SIDE SPAN WERE WRONG, AND THE TWO SPANS OVERLAP

Until TASK_106 the line above read *"3141.00 … 4208.00, six spellings"*.

**First, the TOP endpoint, which nobody had flagged: `4208.00` is `r3b`, the
`.position(`/`.rposition(` spelling, and `r3b` is `forbidden`.** The very next
paragraph of this section says so — *"the EXCLUDED `.position(`/`.rposition(`
spelling is the DEAREST R3"* — so the span quoted, as its in-contract maximum,
the price of a spelling the declaration bans. Audited at TASK_106 with
`harness/check.py::spelling_matches` against every `k_*` in `.temp/t101/cost23.rs`
(`.temp/t106/audit_cost23.log`): **`r3b` hits both `forbidden` entries and is out;
the other six R3-side probe kernels are in.** The dearest of *those* at the median
band is `r3a` at **3535.00**, and the dearest in-contract spelling found since is
`u4` at **3719.00**. ⚠ **The top endpoint moves with search effort exactly as the
bottom one does, which is the whole reason `.memory/01-ladder.md` asks for a span
rather than a point.**

**Second, the FLOOR. TASK_105 M5 found a spelling at 2991.00** — `k_u1`, which
gives the **upward** scan the **downward** one's descending-index shape
(`g = m - i`, index `scr[m - g]`) — and left its admissibility open, because
`k_u1` writes
`m - g < j &&` on the upward scan where `required[0]` names `i < j &&`.
**`harness/check.py::spelling_matches` passes it** (the token occurs on the outer
loop, the exchange and the downward scan) **and `required[0]`'s ENGLISH does
not**, and `spec.md`'s own `why` says no gate stage reproduces that reading.

⚠ **TASK_106 settled it by measurement rather than by reading, and it settles
AGAINST this file's published floor.** Four further respellings were built
(`.temp/t106/mk_u2scan.py` → `u2scan.rs`, same driver and same `cost23.py`
convention), each carrying `i < j &&` **literally on both inner scan
conditions** so that it is in contract on the gate's test *and* on the English.
Audited with `spelling_matches` itself (`.temp/t106/audit_spellings.py`): all
four match every `required` entry and hit no `forbidden` one.

```
marginal Ir/call, NREC=4 NELEM=48 SEED=12345, rustc -O -C codegen-units=1, isolated
spelling                                            in contract?   rank 0    rank 50   rank 100
base  = k_r3c, the shipped R3 shape                  gate+English  3140.30   3187.00   2563.70
u1    descending mirror, guard `m - g < j &&`         gate ONLY    2756.30   2991.00   2563.70
u5    u1 + a REDUNDANT LEADING `i < j &&`            gate+English  2756.30   2991.00   2563.70
u2    two cursors, guard `i < j &&`, index `m - g`   gate+English  3152.30   3432.00   2951.70
u3    identity subtraction `scr[m - (m - i)]`        gate+English  3140.30   3187.00   2563.70
u4    u2 with the downward scan mirrored too         gate+English  3161.30   3719.00   2944.70
r4b   both scans unchecked (R4 side)                 gate+English  2768.30   3050.00   2575.70
```

⚠⚠ **`u5` IS `u1`.** The extra conjunct is a tautology — the outer `while i < j`
has just tested it and neither `i` nor `j` moves inside the scan — and it
compiles away completely: `harness/asm.py` gives `k_u1` and `k_u5`
**the same relocation-masked disassembly, `md5_norm da08af26d9b1`, 249
instructions each** (`.temp/t106/asm_u5.txt`, `-C opt-level=3`). Its shape is
`d5`'s, the redundant `j <= SCR` range hint TASK_105 audited as in contract.
Every checksum agrees at ranks 0/3/50/97/100 and the `wrong` arm differs.

**So the answer is not the one that keeps the headline:**

* **the cheapest in-contract R3 found is 2991.00, not 3141.00 — the published
  floor was 150.00 `Ir`/call too high**, and the corrected span over twelve
  in-contract spellings is **2991.00 … 3719.00**;
* **it is 59.00 below the in-contract R4 spellings `r4b`/`r4d` (3050.00) and
  lands inside the published R4 span**, so **p23's R3-side and R4-side spans
  OVERLAP**: 2991.00 … 3719.00 against 2876.00 … 3050.00. It is still above the
  shipped R4 (2882.00) and above `r4c` (2876.00);
* `spec.md`'s **one real bound** — *"`R3ship − R4ship` bounds
  `inf(in-contract R3) − R4ship`"* — **is not falsified**, because it is an upper
  bound and `inf ≤ R3ship`; it is **loosened**. On this band `R3ship − R4ship`
  = 3141.00 − 2882.00 = **259.00** while `inf(found) − R4ship` ≤ 2991.00 −
  2882.00 = **109.00**, so at least **150.00 of the published safe-side figure is
  attributable to the spelling and not to safety.**

⚠ **And the size of the correction is itself a function of the pivot's rank**,
which is §9c's rule applying to §9b: against the shipped spelling `r3d`
(3094.30 / 3141.00 / 2517.70 at ranks 0 / 50 / 100) the in-contract `u5` is
**338.00 below at rank 0, 150.00 below at rank 50 and 46.00 ABOVE at rank 100.**
**There is no single number for "how wrong the floor was".**

**And the reading question is settled by being made moot.** `k_u1` itself is
**NOT** admissible: `required[0]`'s English asks for the conjunct `i < j &&` *on
both inner scan conditions* and `k_u1`'s upward one is spelled `m - g < j &&`.
That reading stands, and the gate's disagreement with it is the declared gap
`spec.md` already names. **But it decides nothing, because `k_u5` satisfies the
English, satisfies `spelling_matches`, and is the same object code.** ⚠ **A
declaration that a semantically-null respelling can walk around is not enforcing
the number it was thought to be enforcing** — and that, rather than either
reading of `required[0]`, is what this row now shows.

⚠ **What is NOT claimed:** that 2991.00 is the infimum. It is the cheapest of
twelve in-contract spellings now searched, and the search is a reviewer's hour
plus an engineer's. **A floor is an upper bound on the infimum and this pattern
has published a wrong one; quote it as "cheapest found", never as "the
cheapest".**

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
an exact law; the curvature is not modelled here. ⚠ **That two-term fit is
superseded: 9c′ gives an EXACT law and 9c″ gives its domain.**

### 9c′. ⚠⚠ THE EXACT LAW, ON ALL 109 SHIPPED POINTS

The ±30 disclaimer above exists because the fit was on the wrong regressors, and
because seven of band K's thirty-one points were being read. Counting, from the
**bytes** of every shipped blob and by replaying the shipped driver loop, what
the kernel actually does per call —

```
recs    records partitioned            rounds  outer partition-loop iterations
up      upward-scan cursor moves       sw      exchanges performed
dn      downward-scan cursor moves     m       the live extent of each record
```

— and measuring all **31** band-K, **47** band-M, **24** band-N and **5** band-X
points plus the two shipped matrix inputs through the same
`controls/sweep_fit.py::kernel_ir` pipeline (`.temp/t106/band_all.py`,
`fit.py`, `fit3.py`, `holdout.py`), the tax closes exactly:

> ### `R3 − R4 = 2 + 30·recs + 2·dn + 2·sw − 3·rounds + Σ_records τ(m mod 4)`
> ### `Ir` per call, with `τ = {0 → 0, 1 → 2, 2 → 3, 3 → 4}`
>
> **max |residual| = 0.0000 over ALL 109 shipped points**, against a response
> spanning **41.75 … 956.40** `Ir`/call.

Read it as: **2 per call, 30 per record, 2 per downward-scan step, 2 per
exchange, −3 per outer round, and 0/2/3/4 per record according to `m mod 4`.**
Every coefficient is an integer.

**Must-fire and holdout arms, because eight parameters against 109 points is a
claim and not yet a prediction:**

* the byte-level replay's checksum is compared to `model.py`'s on one blob per
  band and agrees; a reversed window index is the negative arm and differs;
* the **seven published band-K rows re-measure to `+0.00`**, and so do the eight
  published band-M rows — 15 of 15, max |delta| 0.00;
* **fit the eight coefficients on bands M and N ONLY (71 points), then predict
  the 38 nobody fitted — band K's 31, band X's 5 and `small`/`large`. The fit
  returns `+2.0000, +30.0000, +2.0000, +2.0000, −3.0000, +2.0000, +3.0000,
  +4.0000` and the held-out max |error| is `0.0000` `Ir`/call.** With the
  training response shuffled, held-out max |error| is **6050.96**.

⚠ **`up + dn == mbytes` EXACTLY at every one of the 109 points**: total cursor
work equals the live byte count, and only its *split* between the two scans
moves. That is what makes the rank a clean axis — band K's `up + dn = 256.00` is
this identity at `nrec·m = 256`.

⚠ **The swap-count confound is REFUTED, not merely absent.** At `nlow = 1` and
`nlow = 31` the swap counts are **7.63 and 7.75 — within 1.6% — while the tax
differs by 3.11×**. Single-regressor fits over the 31 band-K points:
`dn` alone R²=0.9869, `rank` alone R²=0.9869, **`sw` alone R²=0.0132**,
`rounds` alone R²=0.0126. Swaps are a separately identified **+2.00 `Ir` per
exchange** term with the same sign, not a confound; the 3.11× swing is carried
by `dn`.

### 9c″. ⚠⚠ …AND THE BAND-K FORM OF IT DOES **NOT** GENERALISE. THE DOMAIN IS THE FINDING.

Band K fixes `nrec = 8` and `m = 32`, so **on band K the law collapses to
`242 + 2·dn + 2·sw − 3·rounds`** — `2 + 30·8 = 242`, and `32 ≡ 0 mod 4` kills the
`τ` term. That four-term collapse fits band K's 31 points to max |residual|
**0.00** with a `0.0000` odd/even holdout, which is exactly as convincing as it
looks and exactly as local. Evaluated **unchanged** off band K:

```
                                            max |error|, Ir/call
form                                    K       M       N       X    small/large
242 + 2dn + 2sw - 3rounds  (band K)   0.00   32.00  480.00  121.00   152.00
30.25recs + 2dn + 2sw - 3rounds       0.00   32.00    4.00   30.25    31.00
2 + 30recs + 2dn + 2sw - 3rounds + t  0.00    0.00    0.00    0.00     0.00
```

⚠⚠ **The band-K spelling mispredicts band N by up to 480 `Ir`/call and the two
SHIPPED matrix inputs by up to 152.** Band N re-fits to a *different* exact law
of the same shape — `2.00 + 5.75·dn + 2·sw − 3·rounds`, R²=1.0000 — because band
N holds `m = 16`, which makes `dn ≡ 8·recs` and lets the per-record term hide
inside the `dn` coefficient. **Two exact laws that disagree is what a
collinearity looks like from inside one band.**

**And the `τ` term was invisible to both.** Band M's residual under the
per-record form is not noise: over 47 consecutive points it is exactly
**0 / 16 / 24 / 32** as `m mod 4` is **0 / 1 / 2 / 3**, at `recs = 8` — i.e.
0 / 2 / 3 / 4 per record. Band K sits at `m = 32` and band N at `m = 16`, both
`≡ 0 mod 4`, so **neither band could see it**, and band M was read at 8 of its
47 points — `m = 2, 4, 8, 16, 24, 32, 40, 48`, **seven of them multiples of
four**, so the one point that could have shown it (`m = 2`) looked like a single
+19.26 residual in a two-parameter fit and was written off as curvature.

⚠ **The lesson is the one this section already teaches, one level up: a law owes
its domain, and a band that holds a regressor FIXED cannot tell you the
coefficient of anything collinear with it.** p23's rank axis is a genuine
finding; the *arithmetic* fitted on it was three times wrong before it was
right, and each wrong version fitted its own band perfectly.

### 9d. THE PHENOMENON: one of the two scans is elided and the other is not. ⚠ THE CAUSE IS **OPEN**.

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
three.** ✅ **Independently reproduced twice since** — TASK_105 from a probe
written from scratch, and TASK_106 from its own build of that probe
(`.temp/t106/u2scan_O3.log`) — **all nine cells to the instruction.** ⚠ **And
upgraded: `k_r4dn` and `k_r4b` are not merely equal in `Ir`, they have the same
relocation-masked disassembly** — `harness/asm.py`, `md5_norm 5b245ea73c9a`, 251
instructions each (`.temp/t106/asm_u5.txt`). Unchecking the downward read alone
does not approach the fully-unchecked floor, it *is* it. So:

> **LLVM already elides the UPWARD scan's bounds check, and does not elide the
> DOWNWARD one's. The whole of p23's scan-side safety tax is `scr[j - 1]`.**

⚠⚠ **THAT IS THE PHENOMENON AND IT SHIPS. THE EXPLANATION THIS SECTION USED TO
GIVE FOR IT IS WITHDRAWN** (TASK_105 M4). It read *"the reason is the direction
of the induction variable, and it is the finding"*, and named two causes: that
`i`'s ascending recurrence is what buys the elision, and that `j - 1`'s unsigned
**subtraction** is what costs it. **Both were isolated and neither survived**
(all at `-C opt-level=3`, NREC=8 NELEM=32, same probe, all checksums equal;
re-measured at TASK_106 from its own build):

| kernel | what it changes | rank 3% | 50% | 97% |
|---|---|---|---|---|
| `base` | the shipped R3 shape | 4460 | 4492 | 3764 |
| `d2` | **cursor made ASCENDING** (`t` counts up, index `m - 1 - t`) | **5276** | **6106** | **5077** |
| `d6` | **subtraction removed from the index** (`d == j - 1` carried), still descending | 4444 | 4480 | 3744 |
| `u5` | the **UPWARD** scan given the descending, subtracting shape (§9b′) | **3948** | **4230** | **3749** |
| `r4b` | the unchecked floor | 3972 | 4308 | 3778 |

* Making the induction variable **ascend** does not recover the elision — it
  costs **+816 / +1614 / +1313** *more* than `base`.
* Removing the **unsigned subtraction** recovers **16 / 12 / 20** `Ir` of a
  **488 / 184 / −14** gap. Essentially nothing.
* ⚠ **And a third measurement points the other way entirely.** Giving the
  **upward** scan exactly the shape 9d blames — a descending cursor and a
  subtraction at the index — makes it **CHEAPER by 512 / 262 / 15 `Ir`/call**
  on this same band, and takes it **BELOW the unchecked floor at two of the
  three ranks** (3948 against `r4b`'s 3972; 4230 against 4308). A story in which
  descent and unsigned subtraction are what *cost* the elision has to explain
  that.

**So what ships is the phenomenon plus an OPEN mechanism.** That is still a new
entry in this project's list of reasons a bounds check does or does not survive —
the earlier ones are all about where the bound *comes from* (p19's state-range
`cmp $0x8`, p05's per-row hoist, p46's header-derived range facts), and this one
is an **asymmetry between two scans of the same array under the same bound**,
which no earlier row shows. ⚠ **A limb that claims a new REASON owes an
isolation, not just a measurement** (PROTOCOL rules 9 and 12), and this row is
the case that shows the two combine.

⚠ **What this does NOT say:** it does not say the downward check is
unnecessary. R5 proves both, and `c/kernel.c` proves neither — §7 is what
happens then.

---

## 10 — what is not measured here

* **No `-C debug-assertions=on` column in the shipped matrix.** §3 of TASK_101
  warns that debug-assertions enable `assert_unsafe_precondition!` inside
  `get_unchecked` and that on 3 of 3 patterns R4 becomes dearer than R3 at `-O3`
  with it on. Every shipped figure in this file is **debug-assertions OFF**,
  which is the gate's own setting.
  ⚠⚠ **THE ABSENT COLUMN DOES HIDE A SIGN FLIP, AND ITS LOCATION IS NOW KNOWN**
  (TASK_105 m5, re-measured at TASK_106 from its own build,
  `.temp/t106/u2scan_O3da.log`). Probe, `-C opt-level=3 -C debug-assertions=on`,
  NREC=8 NELEM=32, the same three ranks:

  ```
  RANK    base (R3, checked)   r4b (unchecked)    R3 - R4
    3%          5192.00            4618.00        +574.00
   50%          6226.00            4892.00       +1334.00
   97%          4157.00            4403.00        -246.00   <- R4 is DEARER
  ```

  ⚠ **At rank 0.97 unsafe Rust costs MORE than safe Rust.** And, measured beside
  it: with debug-assertions on, **`r4dn` — the downward read unchecked — is
  EXACTLY EQUAL to `base` at all three ranks (5192 / 6226 / 4157)**, because
  `assert_unsafe_precondition!` reinstates precisely the check `get_unchecked`
  was bought to remove. **This is a PROBE**, so the intercepts are the probe's;
  what transfers is the sign flip and where it is. **The two shipped inputs sit
  at mean ranks 0.44 and 0.28, outside the flipping region, so the headline
  survives — but it survives BECAUSE of where the inputs sit, which is §3a's
  lesson again, and the disclosure has to say where it would not.**
* **No wall-clock claim.** The wall numbers are in
  `results/p23-partition.json`; the R4/R5 pair alone spans 519…554 ns for a
  byte-identical kernel, which is the floor on what a p23 timing claim could
  mean.
* ~~**Band X and band N are shipped and were not fitted.**~~ ✅ **They are now**
  (TASK_106, §9c′/9c″): all four bands and both matrix inputs were measured at
  every shipped point — 109 in total — and that is what turned the band-K fit
  from an exact law into a local one. `controls/sweep_fit.py` still reads bands M
  and K at 8 and 7 points; **the full sweep lives in `.temp/t106/band_all.py` and
  is one command**, and nothing in `controls/` was changed.
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
