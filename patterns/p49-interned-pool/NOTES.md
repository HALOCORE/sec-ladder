# p49 — measurements, and what they do not support

`README.md` is the one-screen version, `spec.md` the contract and the reasoning,
`c/kernel.h` the kernel in pseudocode. **This file is where the numbers live and
where what they do NOT support is written down.**

---

## 0. PROTOCOL rule 6 — the contract hash, and the FOUR moves it has made

`spec.md`'s `slb-contract` block, **as first written, before any measurement of
its own pins**:

```
a297e6cbe3c042b1bcde1375ed569e1d0894b79187760f1f1e4e6c729aed4b38
```

⚠ **On a NEW pattern `git show HEAD:patterns/p49-interned-pool/spec.md | diff -`
is VACUOUS** — the pattern lands in one commit, so on a clean tree the command
always prints nothing and always looks like it passed (`PROTOCOL.md` rule 6, the
p22 case). **The recorded hash above is the only evidence**, and the block's
verbatim text was saved beside it at
`.temp/t161/contract_first_written.json` (44 201 characters) so a reviewer can
reconstruct the hash rather than take it on trust — the standard `TASK_155` found
missing on p34 and `TASK_156` fixed.

⚠ **And "as first written" here means BEFORE `harness/measure.py`, BEFORE
`harness/report.py` and BEFORE any full `harness/check.py` run — but AFTER the
seven rungs were built and cross-checked**, because three of the block's own pins
(`verus.obligations`, `verus.twin_obligations` and `identity`) are MEASURED
values that cannot be written before the rung they measure exists. p25's and
p34's disclosures have the same shape; saying so is the point of the rule.

**FOUR moves, all disclosed. ⚠⚠ AND THE OBVIOUS SUMMARY — *"no entry moved"* —
WOULD BE FALSE, WHICH IS EXACTLY THE SENTENCE `p25`'s NOTES HAD TO WITHDRAW.**
So here is the diff, key by key, produced by parsing all five texts and diffing
the objects rather than by assertion (`.temp/t161/` holds all five and each
re-hashes to its digest):

```
1 first-written -> 2 pins        /idiom/required[0]/rust    -2 chars
                                 /idiom/required[1]/c       +5
                                 /idiom/required[5]/c       +2
                                 /idiom/why               +410
2 pins          -> 3 entry19     /idiom/why              +1045
3 entry19       -> 4 stale       /idiom/why               +192
4 stale         -> 5 breakqual   /idiom/why               +162
```

**So THREE `required` entries DID move at step 2**, and what moved in them is
FOUR backticked spellings, deleted:

```
required[0].rust   `unsafe`
required[1].c      `rshd[]`
required[5].c      `"interned":true/false`   `rshd[]`
```

⚠ **Three of the four are the ones the gate's own audit reported as
`pins nothing` — `0 of 2 rung(s)`** — and the fourth, `` `unsafe` ``, was
backticked inside the sentence *"with no `unsafe` anywhere"*, which the audit
then read as a spelling the safe rungs were required to contain. **All four
pinned nothing any rung writes, and removing them made the audit say what it
means.** ✅ **Nothing else moved at any step**: `requires`, `ensures`, every
other `required` entry, `forbidden`, `verus.obligations`,
`verus.twin_obligations`, `verus.items`, `driver`, `collapse`, `identity` and
`miri` are byte-identical from the first state to the shipped one.

| to | what moved | why |
|---|---|---|
| `f4bc4334c9fab9a506ec2f4a81456da22e3c4eb4d8faaf51fc68233e731dd180` | **three accidental backticks and one added sentence** | The gate's own idiom audit printed `3 pin nothing` — `` `rshd[]` `` twice and `` `"interned":true/false` `` once were backticked inside prose, so the audit read them as pinned spellings no rung contains. Unbackticked. In the same edit the `why` gained a sentence saying the `memcpy`/`memmove`/`memset` ban is about SOURCE spellings and not about the object, because `safe_tuned.rs`'s `copy_within` lowers to `memmove@GLIBC_2.2.5` and the gate's own stage-3a column prints it. Text: `.temp/t161/contract_step2_pins.json`. |
| `de0d40a5c9b85a22a8fe10da2f499d3c501f50926ce75e4663cb60377dcb4d5d` | **the entry-19 paragraph of `why`** | It repeated the task file's *"the guard CAN NEVER BE FALSE"*, and §8a **refutes that by measurement in the reduction's own C**. Rule 6's second half is exactly this case: a frozen declaration is evidence about *when* it was written, not about whether it is still true. Text: `.temp/t161/contract_step3_entry19.json`. |
| `3001e6edd05cb2cc5b0cd382088a06ec153f38f716ba588e4f680153bbd584ab` | **the `Rc` arm names in `why`** | It named the safe-Rust control arms `Rc<RefCell<[u8; MAXW]>>` and `Rc<[u8]>`; what was actually built is `Rc<RefCell<Buf>>` and `Rc<Buf>`, where `Buf` carries the width as a field — **so the two arms differ in ONE type, which is the finding the old spelling obscured**. Text: `.temp/t161/contract_step4_stale.json`. |
| `d339ef900e0b2c59c1f8b3a851fdebe3b46ae8f999294e593a5dc5d7a667e0be` | **one qualifier** | *"the safety line DOES EXECUTE ON EVERY BENIGN BREAK"* → **every benign BREAK THAT NAMES A RECORD**. `degenerate.bin` executes 3 BREAKs and evaluates the guard twice, because a BREAK with `nrec == 0` folds SENT before reaching it. Text: `.temp/t161/contract_step5_breakqual.json`. |

All five texts re-hash exactly to the five digests above
(`.temp/t161/mkcontract.py` is the generator; it asserts its own substitution
count and has a `--check` mode).

⚠ **The third and fourth moves are the SAME CLASS as the second and they were
found by the rule-6 second-half pass**, not by any gate stage: nothing in
`check.py` reads a `why` for truth. Three MEASUREMENT-hashed files were corrected
in the same pass and cost one re-measure between them — `inputs/gen.py` (the same
*can never be false* claim), `c/kernel.c` (*"the copy loop below"*, **and
`c/kernel.c` has no copy loop at all**) and `verus.rs` (`lemma_rec_in_pool` is a
solver hint, §8c). ⚠ **A false sentence in a shipped rung source is the thing
this rule exists to catch and the hash would never have caught it.**

⚠ **And rule 6 is necessary, not sufficient** (p46's lesson): the hashed `why`
was re-read against the measured numbers before this file was finished, which is
how the entry-19 sentence was caught.

---

## 1. Is this `p08`? — the question answered with a census, not an argument

`harness/tools/composition.py` declares `p08`'s class as *"two live references to
overlapping storage, one of them mutable"*, which describes `p49` word for word.
`spec.md` gives four separations; three are arguments and the fourth is this
number (`controls/no_overlap.py`, re-derived from the shipped blobs on every
run):

```
p49   copies performed .................................... 6
      of them with DISJOINT source and destination ........ 6
      record pairs whose content ranges COINCIDE EXACTLY .. 11 084
      record pairs whose content ranges are DISJOINT ...... 892 352
      record pairs PARTIALLY overlapping ..................       0

p08   partially-overlapping copies (the negative control) ..       9
      of which on its own adversarial-overlap.bin ..........       4
```

**`p49`'s sharing is EXACT — deduplication hands back *the same buffer* — and
`p08`'s is PARTIAL, which is the only kind it has.** The census runs both
semantics (R1 and R1h) on every window, and the `p08` arm is synthesised from
`p08`'s own documented decode so it runs from a fresh clone whether or not that
pattern's gitignored blobs are present.

⚠ **The `11 084` is load-bearing in the other direction too**: a census that only
ever answered *no overlap here* would pass on a program with no sharing at all,
so the control fails if no two records ever hold one buffer.

**The other three separations, for the record.** (i) `p08`'s overlap is
UNDEFINED BEHAVIOUR (C11 7.24.2.1p2); `p49`'s sharing breaks no rule of C.
(ii) `p08`'s alias is an arithmetic accident (`2*dr < m`); `p49`'s is the
contract, and deleting it deletes the deduplication — which is upstream's patch,
priced in §3b. (iii) `p08` repairs by changing the FUNCTION; `p49` repairs by
adding an OWNERSHIP TEST that costs storage and can refuse.

---

## 2. Every detector, on every arm, on every input — and all of them silent

`controls/detectors.py`: `c/kernel.c` and `c/kernel_hardened.c`, gcc and clang,
`-O0` and `-O3`, `plain` / `-fsanitize=address` / `-fsanitize=undefined`, over
all nine shipped inputs.

```
216 cell(s) run; 0 carried a diagnostic
```

Miri agrees, on the shipped R4 (gate stage 8) and on the rung with the safety
line DELETED (`controls/rust_bug.py`): **18 of 18 bug-arm cells report no
undefined behaviour.**

### 2a. The three positive controls, and why this row needs a third

⚠⚠ **On a row where every column is silent, a control that FIRES is the only
thing standing between *silent* and *not linked in*.**

```
ctl_asan.c        heap use-after-free ......... FIRED under ASan   (4/4 cells)
ctl_asan_stack.c  c/kernel.c's own store, one
                  byte outside a local [u8;64]  FIRED under ASan   (4/4)
                                                FIRED under UBSan  (4/4)
ctl_ubsan.c       signed integer overflow ..... FIRED under UBSan  (4/4)
                                            16 firings, 0 unexpected
```

`ctl_asan_stack.c` is the row-specific one and it is the one that matters:
`c/kernel.c`'s harm is a store into a **local array**, and without it *"ASan is
silent on p49"* would be compatible with *"ASan cannot see this class of
object"*. Read the pair together: **p49's store is in bounds and both sanitizers
say nothing; the SAME store one byte out is reported by both.**

⚠ **One expectation in this control was WRONG and is recorded rather than
quietly relaxed.** Its first `CONTROLS` table required `ctl_asan_stack` to be
SILENT under UBSan; the run said otherwise on **both compilers at both levels** —
UBSan's `-fsanitize=bounds` sees a constant-extent array indexed out of range.
That makes the control STRONGER (it licenses the stack-array class in both
columns), and the table now encodes the measurement.

### 2b. Miri's must-fire arm

`controls/rust_bug.py` builds an arm with real, Miri-visible undefined behaviour
(`get_unchecked` past the end) and requires Miri to report it:

```
arm_miri_ctl.rs     ub=True   error: Undefined Behavior: `assume` called with `false`
arm_safe_bug.rs     ub=False  on all 9 inputs
arm_unsafe_bug.rs   ub=False  on all 9 inputs
```

### 2c. What the silence is, stated exactly

`c/kernel.c` allocates nothing, frees nothing, holds no pointer, and forms no
index outside `mem[0 .. 64)` — `c/kernel.h` proves the last clause in four lines.
**There is no undefined behaviour for any of these instruments to report**, so
`model.py` DECLARES `sanitizer_expect = "clean"` on every input rather than
deriving it: `.memory/03-measurement.md` entry 19, *declaring is honest; a
derivation that cannot fire is not*. What `model.py` **does** derive is a
different question — *what did the write REACH* — and that derivation fires,
distinguishes three cases and is exercised on every gate invocation (§2e).

### 2d. Reproducibility

Every arm's answer is one distinct value across the 12 cells it is run in
(2 compilers × 2 levels × 3 detectors) on every input; the control fails if any
arm produces two. **p49's adversarial rows are excluded from the gate's agreement
set because they DISAGREE, not because they are unstable** — the pool is a local
array with no heap addresses in it. That is `p32`'s position, not `p27`'s.

### 2e. The divergence, which is the whole instrument

```
input                          R1 (c/kernel.c)          R1h (c/kernel_hardened.c)
adversarial-cascade      8653438269484025856     18333534148569259008   DIFFER
adversarial-cowfull      8897935692788144128      9887309797562598400   DIFFER
adversarial-many        10636248267475679232      4770081662406190080   DIFFER
adversarial-rehash      14042888476904305664      1773053308779294720   DIFFER
adversarial-share       17203576457335438336      9997648724353765376   DIFFER
adversarial-stride3                        0                        0   agree (no window)
degenerate              15194016535539881984     15194016535539881984   agree
large                   15925195548848871244     15925195548848871244   agree
small                    3739266750910054865      3739266750910054865   agree
```

`model.py::Detector` answers the finer question at each write the buggy rung
performs, and its three probes answer three different ways — including an
INTERNED record that no other record names, where `published` is true and
`aliased` is false. That middle probe is what makes the detector a derivation
rather than a restatement of the ownership flag, and `selfcheck()` runs all six
cells once per input on every gate invocation.

Across the shipped inputs: `adversarial-rehash` is the one where `aliased` is
**false** and `published` is **true** — the corruption crosses the ownership
boundary **forwards in time**, into a record that did not exist when the write
happened. No built row can produce that.

---

## 3. The safety line

### 3a. Measured on the shipped files

`controls/safety_line.py` preprocesses both C rungs with `gcc -E -P` and diffs:

```
kernel.c           229 preprocessed lines
kernel_hardened.c  243
diff               +17 / -3
```

⚠ **It is NOT a pure addition, and the three `-` lines are named rather than
counted**: two of them (`mem[roff[t]] = 0;` and `v = 2;`) are **re-indented into
the block's inner `else`**, and the third is the declaration line, which gains
the copy loop's index `j`. Nothing is deleted. The control asserts all of that,
plus:

```
`if (rshd[t]) {`   sites   kernel.c 0   kernel_hardened.c 1
`mem[roff[t]] = 0;` sites  kernel.c 1   kernel_hardened.c 2
outside the BREAK arm, statement text identical:  True
```

**The write appears in BOTH rungs.** The bug is not that R1 writes somewhere
else — both rungs write the same byte of the same array — it is that R1 does not
ask whether that byte is its to write.

⚠ p34 additionally ships an `arm_body.inc` include-twice construction and p49
does not, for a reason worth stating: p34's safety line is ONE STATEMENT, so one
body plus one `#if` models it faithfully. p49's changes the control flow of the
`else` arm around it, so an include-twice body would need the `#if` to straddle a
brace.

### 3b. Two repair spellings, and the benign observable decides

`controls/spellings.py` builds the upstream `provenance` repair by ONE asserted
substitution on `c/kernel.c` (the threshold test forced false, so content is
never interned) and runs all three arms on all nine inputs:

```
benign inputs on which `cow` moves the answer        : 0 of 3   []
benign inputs on which `provenance` moves the answer : 3 of 3   [degenerate, large, small]
```

⚠⚠ **That is `TASK_160`'s port-level finding reproduced INSIDE the row.** On the
port, upstream's patch turned `10 passed, 0 failed` into `9 passed, 1 failed` and
flipped `"interned":true` to `false`; here it moves every benign checksum,
because the epilogue folds each record's ownership flag — which is this kernel's
reduction of that API field. **`cow` is benign-invisible and upstream's patch is
not, so `cow` is the safety line.** *An upstream patch is not automatically a
safety line; check it against the benign observable.*

Both repairs fix every adversarial input except `adversarial-stride3.bin`, whose
windows the driver guard skips.

### 3c. The repair can REFUSE, and that is priced

Un-sharing needs storage the bug does not need. `adversarial-cowfull.bin` drives
the private region to exhaustion and then BREAKs a shared record: R1 writes
through, R1h has nowhere to put the copy and folds SENT. Over 20 000 random
windows the refusal fires **412 times** against **33 373** copy-on-write
executions — about **1.2%** (`controls/threshold.py`). **A repair that consumes a
resource can run out of it**, and nothing else in this tree says so.

### 3d. The guard is EVALUATED on every benign BREAK

```
input          BREAKs   guard TRUE   guard FALSE
large.bin        1437            0          1437
small.bin          34            0            34
degenerate.bin      3            0             2      (one BREAK with nrec == 0)
adversarial-*      ...            7             1
```

⚠ **Unlike p34, p49's safety line executes on every benign input** — what no
benign window does is take its TRUE branch. So p49 has a real, non-zero benign
cost gradient where p34's is `0.00`, and §4 prices it. `controls/no_share_break.py`
fails the row if a matrix blob ever evaluates the guard **zero** times, because a
matrix blob with no BREAK at all would silently turn p49 into p34.

---

## 4. The cost axis

⚠ **Every figure below is a CELL — (rung, compiler, optimisation level, inline
mode) — and none is maxed across one.** That is
`.memory/03-measurement.md` entry 23's rule, and this row obeys it because
**its own numbers change sign between compilers and between levels.** Source:
`results/p49-interned-pool.json`, kernel-EXCLUSIVE callgrind `Ir` divided by the
call count.

⚠ **Why the `O3/whole` column is empty**: in `whole` mode at `-O3` the kernel is
inlined into `main` and there is no `kernel` symbol to take an exclusive count
from. `.memory/03-measurement.md`'s standing rule — say which convention you
used — so: **kernel-exclusive, isolated unless stated.**

### 4a. Ir per kernel call, `small.bin` (200 000 calls)

```
cell          O0/iso    O0/whole    O3/iso
c-gcc        2939.89     2939.89   1974.41
c-gcc-h      2965.28     2965.28   1971.63
c-clang      2324.99     2235.91   2286.84
c-clang-h    2341.92     2252.83   2300.71
safe_naive   5978.66     5978.66   2548.46
safe_tuned   7595.92     7595.92   2400.42
unsafe       5898.56     5898.56   2261.93
verus        5898.56     5898.56   2261.93
```

`large.bin` is measured at `-O3` only (`measure.py`'s protocol), `isolated`:

```
c-gcc 5077.88 · c-gcc-h 5109.29 · c-clang 5857.90 · c-clang-h 6029.05
safe_naive 6670.87 · safe_tuned 6058.67 · unsafe 6047.49 · verus 6047.49
```

⚠ `c-clang`'s `O0/whole` (2235.91) differs from its `O0/isolated` (2324.99)
while gcc's two are identical: `whole` mode adds `-flto`, and clang's LTO does
cross-TU work at `-O0` that gcc's does not. Nothing else in this table depends
on it, but a reader comparing the two compilers' `whole` columns should know.

### 4b. ⚠⚠ THE SAFETY LINE's BENIGN PRICE — and its SIGN REVERSES

`R1h − R1`, per cell:

```
input        cc     level  mode        R1        R1h      delta      %
small.bin    gcc    O0     isolated  2939.89   2965.28   +25.39   +0.86
small.bin    gcc    O0     whole     2939.89   2965.28   +25.39   +0.86
small.bin    gcc    O3     isolated  1974.41   1971.63    -2.79   -0.14   <-- NEGATIVE
small.bin    clang  O0     isolated  2324.99   2341.92   +16.93   +0.73
small.bin    clang  O0     whole     2235.91   2252.83   +16.93   +0.76
small.bin    clang  O3     isolated  2286.84   2300.71   +13.87   +0.61
large.bin    gcc    O3     isolated  5077.88   5109.29   +31.41   +0.62
large.bin    clang  O3     isolated  5857.90   6029.05  +171.15   +2.92
```

⚠⚠ **At `-O3` on `small.bin` the hardened kernel is CHEAPER than the buggy one
under gcc (−2.79) and DEARER under clang (+13.87).** That is `p35`'s trap —
*the comparison can reverse* — live on this row, and it is why every figure here
carries its compiler and its level. **A single headline number for "the price of
p49's safety line" does not exist.**

### 4c. What the price is a price OF — and a decomposition that does NOT close

No benign window takes the guard's TRUE branch (§3d), so on every matrix input
the copy loop, the flag store and the bump **never execute**: the whole gradient
is the guard's own load, compare and branch. The driver's window-visit orbit
gives the guard evaluations per call exactly (`.temp/t161/guard_per_call.py`
replays the Lemire index rather than assuming a uniform visit):

```
small.bin        4.232 guard evaluations per call   (34 over 8 windows, 3..6 each)
large.bin       22.351                              (1437 over 64 windows, 13..33)
degenerate.bin   2.000                              (2 over 1 window)
```

Dividing gives an apparent per-guard price of

```
gcc   O0  small  +6.00      clang O0  small  +4.00
gcc   O3  small  -0.66      clang O3  small  +3.28
gcc   O3  large  +1.41      clang O3  large  +7.66
```

⚠⚠ **AND THAT DECOMPOSITION DOES NOT CLOSE, SO IT IS NOT PUBLISHED AS THE PRICE
OF THE GUARD.** Within one (compiler, level) cell the figure moves as much
across the two INPUTS (gcc `-O3`: −0.66 against +1.41; clang `-O3`: +3.28
against +7.66) as it does across compilers. A per-guard constant would be
input-independent, and this is not: the extra branch also changes register
pressure and scheduling in the rest of the loop, and this measurement cannot
separate the two. **What is published is the per-CALL delta per cell above.**
`.memory/03-measurement.md`'s rule — *close a decomposition over every function
or say "presumed"* — and this one is not closed.

### 4d. The R4/R5 pair: 0.00 in every measured cell

```
small.bin  O0 isolated   unsafe 5898.56   verus 5898.56   delta +0.00
small.bin  O0 whole      unsafe 5898.56   verus 5898.56   delta +0.00
small.bin  O3 isolated   unsafe 2261.93   verus 2261.93   delta +0.00
large.bin  O3 isolated   unsafe 6047.49   verus 6047.49   delta +0.00
```

**The proof licenses the unsafe code at zero instruction cost**, which is this
project's standing R4/R5 result, and here the kernel is byte-identical at `-O3`
(§6c) so the zero is forced rather than lucky.

⚠⚠ **THIS IS NOT `.memory/03-measurement.md` ENTRY 23's NULL AND MUST NOT BE
QUOTED AS ONE.** Entry 23 is about `marginal_ir_per_call`, a **whole-program
slope** taken inside the GATE, which includes everything the kernel calls; the
table above is the **kernel-exclusive** column from the MEASUREMENT record. They
are different quantities measured by different instruments, and p49's entry-23
figure is whatever `results/gate/p49-interned-pool.json` says — not this.

### 4e. The ladder, `-O3` isolated, against R1h (the CHECKED C rung)

```
small.bin   c-gcc 0.99  c-gcc-h 1.00  c-clang 1.16  c-clang-h 1.17
            safe_naive 1.29  safe_tuned 1.22  unsafe 1.15  verus 1.15
large.bin   c-gcc 0.99  c-gcc-h 1.00  c-clang 1.15  c-clang-h 1.18
            safe_naive 1.31  safe_tuned 1.19  unsafe 1.18  verus 1.18
```

**Safe Rust is 19–31% dearer than hardened gcc C here, and `unsafe`/`verus` are
15–18% dearer.** ⚠ The gap between safe and unsafe Rust — 0.14x on `small.bin`,
0.13x on `large.bin` — is what the bounds checks cost, and it is small because
the kernel's inner work (the dedup scan and the byte loops) dominates the index
arithmetic. ⚠ **And note that clang's C is 15–17% dearer than gcc's on this
kernel**, so *"C"* is not one column: a C-vs-Rust claim taken against clang
would be half the size of the same claim against gcc.

### 4f. Wall clock — SECONDARY, and it cannot resolve the safety line

```
small.bin -O3 isolated, min of 30 reps: c-gcc 44.272 ms (spread 2.03%)
                                        c-gcc-h 44.995 ms (0.78%)   +1.63%
                                        c-clang 37.586 (1.96%) / c-clang-h 37.694 (1.88%)  +0.29%
large.bin -O3 isolated:                 c-gcc 29.838 / c-gcc-h 29.268   -1.91%
                                        c-clang 29.101 / c-clang-h 28.708  -1.35%
```

⚠ **The wall-clock sign disagrees with the `Ir` sign on `large.bin` for both
compilers, and the run-to-run spread (0.78–3.10%) is larger than the effect
(0.6–2.9%).** So the wall column **cannot** resolve this row's safety-line price
and is reported only as a sanity check on `Ir`. Frequency scaling is on and
cannot be disabled without root (`.memory/00-environment.md`).

---

## 5. The R3 lever

`safe_tuned.rs` changes four spellings against `safe_naive.rs` — the op walk
(`chunks_exact(2).take(nops)`), the opcode (`match`), the dedup lookup
(`iter().zip().position()`) and the three byte loops (slice iterators and
`copy_within`). None touches the ownership discipline. What it moves,
kernel-exclusive `Ir` per call:

```
small.bin  O0 isolated   R2 5978.66   R3 7595.92   +1617.26   +27.05%
small.bin  O0 whole      R2 5978.66   R3 7595.92   +1617.26   +27.05%
small.bin  O3 isolated   R2 2548.46   R3 2400.42    -148.05    -5.81%
large.bin  O3 isolated   R2 6670.87   R3 6058.67    -612.20    -9.18%
```

⚠⚠ **THE SIGN REVERSES WITH THE OPTIMISATION LEVEL, AND BY A LOT.** At `-O0`
the tuned spelling is **27% DEARER** — every iterator adapter is an un-inlined
closure call — and at `-O3` it is 6–9% cheaper. Static instruction count tells
the same story from the other side: at `-O3` `safe_tuned` is **1216**
instructions against `safe_naive`'s **731**, i.e. **bigger and faster**, which
is what unrolled iterator code looks like.

⚠ **NO R3-SIDE SPREAD IS PUBLISHED.** `.memory/01-ladder.md` finding 14 asks for
*cheapest FOUND, on this input*, never *minimum* — and this row has only ONE
in-contract R3 spelling built, so there is not even a second point to bound a
spread with. A second spelling is the obvious next measurement and it was not
made; §10.

⚠ `copy_within` lowers to `memmove@GLIBC_2.2.5`, which the gate's own stage-3a
bulk-call column prints for both `safe_tuned` cells. The `forbidden` list bans
the SOURCE spellings `memcpy(`/`memmove(`/`memset(`, not the object-level call;
`spec.md`'s `why` says so.

---

## 6. The proof

### 6a. The counts, measured rather than predicted

```
./verus_run.py patterns/p49-interned-pool/verus.rs               34 verified, 0 errors   ~4 s
./verus_run.py patterns/p49-interned-pool/verus.rs --cfg slb_twin 37 verified, 0 errors   ~4 s
```

**34 is the largest obligation count in this tree**, and that is a census and
not an impression — every `spec.md`'s `verus.obligations` summed
(`.temp/t161/`, 33 patterns): **p49 34, p29 25, p34 24, p28 23, p46 21, p22 20,
… p32 15, p25 10, p04 9**. ⚠ It is the largest count and **NOT the largest
file**: `p28`'s `verus.rs` is 1709 lines and `p29`'s 1494 against p49's 1126.
The reason for the count is the content width: a variable-width string pool needs four verified
helper loops — `find`, `fill`, `copy_bytes`, `fold_bytes` — where every one of
`p32`'s operations is O(1) straight-line code, plus three recursive spec
functions (`filled`, `copied`, `folded`) and two induction lemmas to give those
loops postconditions. §8b counts what that cost.

**TCB: five items** — `buf_get_unchecked`, `arr_get_unchecked`,
`arr_set_unchecked`, `load_input`, `emit`. `p27` and `p29` ship SEVEN; the two
p49 does not need are `vstd::raw_ptr::allocate` and `deallocate`, because **p49
allocates nothing**. Three of the five carry verified twins (`load_input` and
`emit` are outside the regime: `external_body` with no `ensures` and no `unsafe`
body).

### 6b. What the R5 proves, and what it does not

⚠⚠ **NEW: `copy_bytes` carries `requires src + w <= dst` — a DISJOINTNESS /
PROVENANCE precondition — and `TASK_160` §8 predicted that nothing in this tree
states one.** It is discharged out of `wf_prov`, the loop invariant that a SHARED
buffer lies wholly inside the interning arena while the private bump is at or
above it: `roff[t] + rlen[t] <= ARENA <= pbump`.

⚠ **The `ensures` deliberately does NOT say "no record's content aliases
another's", because that is FALSE BY DESIGN.** Deduplication is the contract, and
the abstract machine `run` shares buffers exactly where the kernel does. The
disjointness that IS stated is narrower and is about the COPY.

⚠⚠ **And the safety line ITSELF is discharged as an ordinary FUNCTIONAL
postcondition** — `p32`'s finding in a different currency. Both arms of
`if rshd[t] == 1` type-check without the test, every index is in range either
way, and no permission is consumed anywhere in the kernel. What fails without it
is that the loop stops computing `run`. **Linearity has nothing to say about this
bug, because the bug does not touch an allocation.**

`controls/proof_mutants.py` measures all of that rather than asserting it:

`controls/proof_mutants.py` measures all of that rather than asserting it —
**nine arms, every verdict re-derived by the script at `--rlimit 200`**:

```
M0-control                 control      expect verify  got verify   34/0
M1-safety-line             attack       expect fail    got fail     33/1
M2-constant-body           vacuity      expect fail    got fail     31/1  postcondition not satisfied
M3-spec-weaken             must-verify  expect verify  got verify   34/0
X1-spec-only-weaken        attack       expect fail    got fail     33/1  assertion failed
X2-provenance-invariant    deletion     expect fail    got fail     33/1  postcondition not satisfied
X3-copy-disjointness       deletion     expect fail    got fail     33/1  invariant not satisfied before loop
M4-lemma-rec-in-pool       must-verify  expect verify  got verify   34/0
M5-both-hints              attack       expect fail    got fail     33/1  rlimit exceeded
```

**The three-cell experiment**: `M1` (exec only) FAILS, `X1` (spec only) FAILS,
`M3` (both) VERIFIES. So `step`'s branch is not inert and the two sides are tied
to each other and to nothing outside — *the safety line is load-bearing against
the specification and against nothing else.*

**This row's own pair**: `X3` deletes `copy_bytes`'s `src + w <= dst` and the
copy loop's own invariant stops holding before the loop; `X2` deletes the
`wf_prov` clause that discharges it and `lemma_rec_in_pool`'s two memory-safety
postconditions stop being derivable. **The disjointness obligation demands
something and something has to discharge it**, measured from both sides.

⚠⚠ **AND ONE ARM SURPRISED ITS AUTHOR, WHICH IS RECORDED RATHER THAN QUIETLY
RELAXED.** `M4` was written expecting `fail` and the run said `verify`: deleting
both `lemma_rec_in_pool` calls leaves a file that still verifies. §8c has the
bisection and the reason — `M5` is the arm that makes it a result.

⚠ **What `M1`'s diagnostic does NOT establish.** At `--rlimit 200` it is
`while loop: Resource limit (rlimit) exceeded`, and a probe at `--rlimit 4000`
was still running after about twenty-five minutes and was terminated without an
answer. **So the ATTACK arm's failure SITE is not established here** — only that
the file does not verify. An earlier draft of this file's own `why` claimed it
failed on the postcondition; that claim is withdrawn.

### 6c. `identity`: R4 == R5 by raw bytes at `-O3`

```
-O3 isolated   md5_raw       563ecf2f9431db3c9ec8963b5ccd5c62   IDENTICAL on both
               n_fn_nopad    439      fn_bytes 1822
-O0 isolated   md5_raw_norel bdab100e3517b0c56fc510117d7bac7a   IDENTICAL on both
               md5_norm      06e8fe436c25b756ace6c640a5fad7ac   IDENTICAL
               n_fn_nopad    665      fn_bytes 3739
```

`exact` at `-O3` and `norel` at `-O0` — p32's pin, and for p32's reason: p49 has
no pointer write, no allocation and no vstd call in the kernel, so there is
nothing for the two rungs to spell differently. The `-O0` residue is link layout.
⚠ **The four verified helpers are `#[inline(always)]` in BOTH files and carry
contracts in only one; the contracts erase, which is why adding them costs zero
instructions.**

---

## 7. Miri

Mandatory (five trusted items). ⚠ **And note what it finds, because it is this
row's headline and not a gap in the run: NOTHING, on any input, including all
five adversarial ones** — on the shipped R4 (gate stage 8) and on the rung with
the safety line deleted (`controls/rust_bug.py`, 18 of 18 cells). The pool is a
local array alive for the whole call; the buggy rung's every index is in range;
nothing is allocated, so nothing can be used after being freed. **Miri is an
instrument about ALLOCATIONS and p49 has none.**

What Miri still buys is what it buys on `p08` and `p32`: a trusted body that read
one element past an array would satisfy every `ensures` in `verus.rs` and be
invisible to Verus, to the twins, to the contract pin and to stages 5c/5c-req.

---

## 8. The reduction's defect, and what fixing it cost

### 8a. ⚠⚠ THE MANAGER'S CENTRAL CLAIM IS HALF FALSE, AND THAT IS MEASURED

`TASK_161.md` and `.temp/mgr161/NOTES.md` both assert, verbatim:

> ⚠⚠⚠ **`r_shared[nrec]` is therefore ALWAYS `1`, so `SLB_HARDEN == 1`'s guard
> `if (r_shared[i])` CAN NEVER BE FALSE.**

**The first clause is true; the second is not.** The reduction's own
copy-on-write arm writes `r_shared[i] = 0;` when it un-shares
(`.temp/t160/red/k40304.c:122`), so a *second* `BREAK` on a record the first one
copied takes the false branch. Measured **in the reduction's own C**, with two
counters spliced into a COPY of it and every substitution count asserted
(`.temp/t161/red_probe/probe.py`, 20 000 random op streams at `SLB_HARDEN=1`):

```
records BORN shared ............. 215 579
records BORN owned ..............       0      <-- the DEAD branch, and the defect
guard `if (r_shared[i])` TRUE ...  67 195
guard `if (r_shared[i])` FALSE ..  30 263      <-- 31.1% of 97 458 evaluations
```

⚠ **What IS true of the reduction as SHIPPED**: its two blobs evaluate the guard
**once between them** — benign 0, adversarial 1 — and it is TRUE that once, so
the demonstration never exercised the false branch even though the program can.

✅ **The precise defect is *no record is ever born owned*, not *the guard cannot
fire*, and the two would need different repairs.** The fix this build makes —
deriving the width from the input — repairs the first, which is the one that
matters: the `INLINE_THRESHOLD` is the CVE's own precondition and a compile-time
`if (3 < 5)` is not a test of it.

### 8b. The shipped configuration against the reduction's, on the same streams

`controls/threshold.py`, 20 000 random windows, both width rules on the same op
streams, cross-checked against `model.py` on all 78 shipped windows first:

```
                                shipped (w = 1 + a % 6)   reduction (w == 3)
intern branch taken                       90 476                180 834
own branch taken                          89 409                      0    DEAD
records BORN shared                       90 222                177 555
records BORN owned                        87 760                      0    DEAD
dedup hits                                 9 525                 81 624
guard TRUE                                33 373  (34.2%)        65 973  (67.7%)
guard FALSE                               64 127  (65.8%)        31 527  (32.3%)
   ...on a record BORN owned              48 033                      0    IMPOSSIBLE
   ...after an earlier copy-on-write      16 094                 31 527
copy-on-write REFUSED                        412                      0
```

### 8c. ⚠⚠ THE FIX WAS NOT SMALL, WHICH THE TASK FILE ASSERTED

`.temp/mgr161/NOTES.md`: *"✅ **THE FIX IS SMALL AND IT MAKES THE ROW BETTER:**
derive the content width from the input."* The second half is right. **The first
half is not**, and the count is the refutation. A constant width makes
materialising, copying and folding a buffer straight-line code; a variable width
makes all three LOOPS, and at R5 a loop needs a recursive spec function, a loop
invariant, and — for the copy — an induction lemma.

| what the variable width added to `verus.rs` | |
|---|---|
| recursive spec fns the width ADDED | 3 (`filled`, `copied`, `folded`) — a constant width needs none. (p49 declares 17 spec fns in all; the other 14 are the machine, and `p32` declares 9.) |
| verified exec helpers with loops | 4 (`find`, `fill`, `copy_bytes`, `fold_bytes`) — `p32`, whose ops are all O(1), has 0 |
| proof fns | **3** — `lemma_find` and `lemma_copied_below` are inductions, `lemma_rec_in_pool` is a case split. **`p32` has 0 proof fns at all.** |
| Verus obligations | **34**, against `p32`'s 15 and `p25`'s 10 — the largest in the tree (§6a has the census; runner-up `p29` at 25) |
| `verus.rs` lines | **1 126**, against `p32`'s 641. ⚠ Not a size record: `p28` is 1709 and `p29` 1494 |

⚠⚠ **AND IT PRODUCED ONE VERUS FAILURE THAT IS WORTH RECORDING ON ITS OWN.**
The first complete `verus.rs` reported

```
error: while loop: Resource limit (rlimit) exceeded
verification results:: 32 verified, 1 errors
```

on the kernel's own op loop at the **default** budget. At `--rlimit 400` the real
gap appeared — `fold_bytes`'s `base + w <= MEM` precondition, undischarged on the
READ path — and adding `lemma_rec_in_pool` (a lemma whose only body is
`assert(st.rshd[t] == 0u8 || st.rshd[t] == 1u8);`, forcing the case split the
`wf_prov` quantifiers are triggered on) fixed **both**: the shipped file now
verifies at the **default** rlimit in about four seconds.

✅ **So the rlimit exceedance was a MISSING CASE SPLIT, not genuine size** — and
p49 therefore ships **no `#[verifier::rlimit(..)]` attribute**, where `p28` needs
`400` on its kernel. ⚠ **The rlimit message is a diagnostic about the solver's
search, not about the proof's difficulty, and reading it as the latter would have
sent this build down a much longer road.**

---

## 9. The bug class — OPEN, and the engineer proposes `aliasing`

`harness/tools/composition.py --check` fails with `built but unclassified` until
the manager adds a row. **That is the check working**, and this file does not
edit that file. Both candidates are defensible and the case for each is stated:

**`aliasing`** — *"two live references to overlapping storage, one of them
mutable"*. Describes p49 literally: two records name one buffer and the
cycle-breaker's reference is the mutable one. And it is what
`composition.py`'s own stated test selects: *what does the SAFETY LINE ask?* —
`if (rshd[t])` asks an **ownership** question about a live alias.

**`logical`** — *"wrong answer, memory-safe throughout: no rung leaves its
object"*. Also literally satisfied, and by a wide margin: §2 is 216 silent
detector cells plus 18 silent Miri cells.

**Proposed: `aliasing`, with a caveat.** Two reasons and one cost:

  1. `logical`'s three members (`p04`, `p06`, `p19`) have **no aliasing
     structure at all**, while p49 **cannot exist without one** — delete the
     sharing and the pool stops deduplicating. Filing it under `logical` would
     erase the row's mechanism.
  2. `aliasing` is currently a singleton, and a class with one member is a
     description of that member rather than a class.
  3. ⚠ **The cost, stated because it is real**: `p08`'s aliasing IS undefined
     behaviour and p49's is not, so admitting p49 forces the class description
     to widen. That is a genuine argument for `logical` and the manager may take
     it.

Proposed wording, to apply or to reject:

```python
"aliasing": (
    "two live references to overlapping storage, one of them mutable. "
    "⚠ The two members differ on whether that is UNDEFINED BEHAVIOUR: p08's "
    "overlap is a `memcpy` whose ranges overlap (C11 7.24.2.1p2) and IS UB; "
    "p49's sharing is created deliberately by a dedup table, is correct C, and "
    "the bug is the WRITE THROUGH IT",
    ["p08", "p49"],
),
```

```python
CAVEATS["p49"] = (
    "the aliasing is the CONTRACT, not the bug -- deduplication is what an "
    "intern pool IS. controls/no_overlap.py measures that two records' content "
    "ranges are always EQUAL or DISJOINT and never PARTIAL (11 084 equal, "
    "892 352 disjoint, 0 partial), while p08's are PARTIAL (9 copies). Counted "
    "`aliasing` on what the SAFETY LINE ASKS -- is this buffer mine to write?, "
    "an OWNERSHIP question -- which is this table's own stated test. ⚠ "
    "`logical` is the defensible alternative and is literally satisfied: "
    "nothing is allocated, nothing is freed, every index is in bounds, and "
    "ASan, UBSan and Miri are silent on every input including the adversarial "
    "ones (216 + 18 cells, 0 diagnostics). It was not chosen because logical's "
    "three members have no aliasing structure at all while p49 cannot exist "
    "without one. ⚠⚠ p49 is the THIRD position on this axis: p28's aliasing "
    "is the SETUP that makes the omission possible, p32's IS the harm, and "
    "p49's is the CONTRACT and the WRITE is the harm."
)
```

---

## 10. What is NOT here, and what I am unsure about

**Not measured, and each would be a real next step**

  * **No `--sweep` bands.** `inputs/gen.py --sweep` writes an operation-count
    band and a DEDUP band (the DEFINE fraction swept, so the number of interning
    lookups rises while the number of operations does not). Neither was run, so
    **nothing here is a law with a domain** — every figure in §4 is two input
    shapes, not a fit.
  * **No second in-contract R3 spelling**, so no R3-side spread (§5).
  * **No `-O0d` (debug-assertions) column and no `--panic abort` column.**
  * **No `safe_naive_verus.rs`** (the R2v control cell).
  * **`large.bin` has no `-O0` `Ir` column** — `measure.py`'s protocol measures
    it at `-O3` only, so the `-O0` sign reversal in §5 rests on `small.bin`
    alone.
  * **The `Rc` arms are checked for their ANSWER, not priced.**
    `controls/safe_arms.py` establishes that `Rc<RefCell<Buf>>` reproduces
    `c/kernel.c` and `Rc<Buf>`+`make_mut` reproduces `c/kernel_hardened.c`, on
    all nine inputs. It does **not** measure what either costs. **So "safe Rust
    offers both the bug and the repair" is a claim about EXPRESSIVENESS and
    carries no number.**
  * **`M1`'s failure site** (§6b).
  * **The `provenance` arm is priced but never gated**: `controls/spellings.py`
    builds it and reports its `Ir`, and no gate stage runs a detector on it. It
    is a control, not a rung.

**Assumptions a reviewer should attack**

  1. ⚠ **The arena is byte-packed and the buffers are 1–6 bytes.** A real intern
     pool holds strings of any length. The width is load-bearing three ways
     (it decides intern-vs-own, it is half the dedup key, and it consumes arena),
     but nothing here tests a width that does not fit in a `u8` or an arena that
     does not fit in one either. **`MEM = 64` is what makes every offset a `u8`
     and every `Seq` short enough for the solver.**
  2. ⚠ **The dedup table compares `(key, w)` and not the bytes.** That is an
     EXACT content comparison *because* content is a function of `(key, w)` —
     `model.py::content` — so there is no hash collision to model. A pool whose
     key were a real hash would have a collision path this row does not have.
  3. ⚠ **The epilogue folds the ownership flag**, which is what makes the
     `provenance` repair benign-observable (§3b). That is a modelling choice
     standing in for the port's `"interned"` API field. **Without it,
     `provenance` and `cow` would be indistinguishable on benign input and this
     row would have no reason to prefer one.** It is disclosed in the `why`, in
     `c/kernel.h` and here, and a reviewer may reasonably call it the thing that
     decides §3b.
  4. ⚠ **`no_share_break` is a property of the SHIPPED blobs, not a theorem.**
     `inputs/gen.py` cannot emit a violating window and `model.py` re-derives the
     property every gate run, but a hand-written blob could violate it and the
     gate would then report a stage-2 disagreement rather than a clear message.
  5. ⚠ **§4c's per-guard figures do not close.** They are printed to be argued
     with, not quoted.

**Process**

  * `.memory/`, `RECAP.md`, `results/SYNTHESIS.md` and
    `harness/tools/composition.py` were **not** edited — the task forbids it and
    the class proposal in §9 is a proposal.
  * `harness/tools/composition.py --check` will FAIL with `built but
    unclassified` until the manager applies §9. **That is the check working.**

---

## 11. SLB-TRUSTED-ARGUMENT sections

The gate requires one section per trusted item **as
`harness/check.py::_is_trusted` defines one** — `#[verifier::external_body]`
**with a non-empty `ensures`**, or `unsafe` in the body — and prints it in full on
every run. **It requires THREE for p49**, and there are three below.

⚠ **THREE IS NOT THE SAME DENOMINATOR AS §6a's TCB TALLY**, and p32's NOTES
records that the two were once mixed up. Counted:

| | `#[verifier::external_body]` items | sections the gate requires |
|---|---|---|
| `p49` | **5** | **3** |
| `p32` | 5 | 3 |
| `p27` / `p29` | 7 | 5 / 7 |

The two p49 items the gate does **not** govern are `load_input` and `emit`: they
carry no `ensures`, so they cannot axiomatise a falsehood, which is the property
`_is_trusted` is keyed on. §6a's *"TCB: five items"* is the ITEM count and is
correct.

## SLB-TRUSTED-ARGUMENT verus.rs buf_get_unchecked

**(a) Is the twin's body the right checked stand-in?** The trusted body is
`unsafe { *v.get_unchecked(i) }` on a `&[u8]`; the twin's is `v[i]` on the same
`&[u8]`, with the same parameters and character-identical clause text. `v[i]` is
the checked form of the identical operation — rustc emits the bounds test
`i < v.len()` that `get_unchecked` requires of the caller — so a `requires` too
weak to license the unchecked read is too weak to license the indexed one, and
`--cfg slb_twin` would reject it. This is the same item every unsafe rung in this
project ships and it is unchanged here.

**(b) Is the `ensures` complete?** The body performs exactly one operation, a
read of one element, and returns it; `r == v@[i as int]` names that element and
its value, and `v: &[u8]` is immutable so nothing can be modified. The
completeness question is TASK_009_REVIEW's x4 — a body that also read `i + 1`
would satisfy this contract — and the answer is that the body is the one line
above and contains no second access. On p49 this item is used for the window
bytes ONLY, at four sites: the `u32` header (`off`, `off+1`, `off+2`, `off+3`)
and the op pair (`off + p`, `off + p + 1`). Each is discharged from
`off + len <= buf@.len()` together with `4 <= len` or `p + 2 <= len`, both loop
invariants, so the caller discharges the precondition with no arithmetic the
reader cannot check. ⚠ **The POOL is not read through this item** — it is
`[u8; MEM]`, an array, and goes through `arr_get_unchecked`.

**(c) Does each clause mean the same in both configurations?** `i < v@.len()` and
`r == v@[i as int]` mention only `i`, `v` and `r`; `v@` for a slice is
`vstd::slice`'s view in both configurations, `spec_slice_len` is the same
function, and nothing in the clause text is `cfg`-dependent. The `#[cfg(slb_twin)]`
twin differs from the trusted item in its body and in nothing else — the gate's
`_check_twin_cfg_hygiene` checks that mechanically.

## SLB-TRUSTED-ARGUMENT verus.rs arr_get_unchecked

**(a) Is the twin's body the right checked stand-in?** The trusted body is
`unsafe { *v.get_unchecked(i) }` on a `&[T; N]`; the twin's is `v[i]` on the same
`&[T; N]`, same parameters, same clause text. For a fixed-size array `v[i]` is the
checked form of the identical operation — rustc emits the bounds test `i < N` — so
a `requires` too weak to license the unchecked read is too weak to license the
indexed one. **It is generic over `T: Copy` and `N` on purpose**: p49 indexes
**seven** arrays with it — the pool `[u8; 64]`, the dedup table's `ekey`, `elen`
and `eoff` (`[u8; 8]` each) and the record table's `roff`, `rlen` and `rshd`
(`[u8; 12]` each) — and one item is one axiom instead of seven. Genericity does
not weaken the argument, because the body is `T`-independent and `vstd::array`'s
`array_len_matches_n` supplies `v@.len() == N` for every `N`.

**(b) Is the `ensures` complete?** The body performs exactly one operation, a
read of one element, and returns it; `r == v@[i as int]` names that element and
its value, and `v` is `&[T; N]` so nothing can be modified. ⚠ **On p49 every `T`
is `u8`** — there is no `u32` array here and no pointer anywhere in the kernel —
so there is no provenance and no interior mutability for the clause to be silent
about, which is the place where p29's version of this argument has to work harder
(its `T` includes `*mut Rec`). Here `Seq<u8>` equality is equality of the integer,
and that is the whole of what a read can produce. ⚠ **And the completeness
question has a p49-specific edge worth naming**: a body that read `i + 1` would be
invisible to this contract, and the array most exposed to that is the POOL, whose
neighbouring bytes belong to a DIFFERENT record — which is precisely this
pattern's harm. That is why `miri.required` is `true` here even though Miri finds
nothing: Miri is the only instrument that would see it.

**(c) Does each clause mean the same in both configurations?** Both clauses
mention only `i`, `v` and `r`, and `v@` for `[T; N]` is `vstd::array`'s view in
both. `N` is a const generic instantiated identically at every call site in both
configurations. Nothing in the clause text is `cfg`-dependent, and the twin
differs only in its body.

## SLB-TRUSTED-ARGUMENT verus.rs arr_set_unchecked

**(a) Is the twin's body the right checked stand-in?** The trusted body is
`unsafe { *v.get_unchecked_mut(i) = x; }` on a `&mut [T; N]`; the twin's is
`v[i] = x;` on the same `&mut [T; N]`, same parameters, same clause text.
`v[i] = x` is the checked form of the identical store and rustc emits the bounds
test `i < N` that `get_unchecked_mut` requires of the caller, so `--cfg slb_twin`
rejects a `requires` too weak for either.

**(b) Is the `ensures` complete?** `final(v)@ == old(v)@.update(i as int, x)` is
an equality over the WHOLE sequence, so it says both what changed and — element by
element — that nothing else did. A body that also wrote `i + 1` would violate it,
which is the direction TASK_009_REVIEW's x4 asks about, and the body is the one
line above. ⚠ **On this row that whole-sequence equality is doing more work than
usual**: the store `arr_set_unchecked(&mut mem, ro as usize, 0)` IS the pattern's
harm site, and *nothing else in the pool changed* is exactly the property the
abstract machine's `st.mem.update(...)` asserts. A contract that named only the
written element would let a trusted body scribble on a neighbouring record and
still satisfy every `ensures` in the file. The parameter `x` is unconstrained by
any `requires` and that is the parameter-coverage false positive
`.memory/04-verus.md` names: `x` is a pure VALUE, stored into the array and never
used as an address, an index or a length, so every `T` is a legal thing to store
in a `T` slot. `spec.md`'s `verus.unsafe_justifications` carries the same argument
in the hashed block.

**(c) Does each clause mean the same in both configurations?** `i < old(v)@.len()`
and the `update` equality mention only `i`, `v` and `x`; `old`/`final` and
`Seq::update` are Verus builtins with one meaning, and `v@` for `[T; N]` is
`vstd::array`'s view in both configurations. Nothing is `cfg`-dependent and the
twin differs only in its body.
