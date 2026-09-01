# p25 — notes, and every number this row publishes

Built at `TASK_157`. Read `README.md` for the shape, `spec.md` for the contract
and the reasoning, `c/kernel.h` for the kernel in pseudocode. **This file is
where the numbers live and where what they do NOT support is written down.**

## 0. PROTOCOL rule 6 — the contract hash, and the three moves it has made

`spec.md`'s `slb-contract` block, **as first written, before any measurement of
its own pins**:

```
54088d20a749069b0111e674b01f80ba050fa11b70030219e97e7725b3fa4dba
```

⚠ **On a NEW pattern `git show HEAD:patterns/p25-realloc-growth/spec.md | diff -`
is VACUOUS** — the pattern lands in one commit, so on a clean tree the command
always prints nothing and always looks like it passed (`PROTOCOL.md` rule 6, the
p22 case). **The recorded hash above is the only evidence**, and the block's
verbatim text was saved beside it at `.temp/t157/contract_first_written.json`
(26 255 bytes) so a reviewer can reconstruct the hash rather than take it on
trust — the standard `TASK_155` found missing on p34 and `TASK_156` fixed.

**THREE moves, all disclosed, all verified to be what they say:**

| to | what moved | why |
|---|---|---|
| `a4b9e5750361a1d9c116fec58969557d16e2853efc6f3e521ce8fdaa94c0c3e7` | **one sentence of `why`** | It quoted `.temp/mgr155/NOTES.md` §6's `malloc` census verbatim, and `controls/no_reloc.py` — written after the block — **refuted it** (§1 below). Rule 6's second half is exactly this case: a frozen declaration is evidence about *when* it was written, not about whether it is still true. |
| `8cef5a43b154bd5fbf5ba433ca5d1773df5c3c9b6453d0802df1ffef1a4bbf3c` | **25 unicode escapes** | The block as first written carried `\\u26a0` where p27, p32 and p34 carry `⚠`, so JSON decoded a six-character literal instead of `⚠`. Verified purely cosmetic: parsing both texts and normalising the escape gives **identical** objects. |
| `c41099be4dfdc6464941b3e60ea6b3e0067b8156735c4748b1ecdf5b6d00fddd` | **the tail of `why`** | The gate's own `idiom-named-spelling` stage FAILED the first full run: `idiom.why` must end with the SHARED named-spelling paragraph **byte-identical** (11 003 bytes, `sha256 59748cce2db5…`, *"NAMED-SPELLING STANDARD"* → *"p01 and p08 neither"*), and what was there was a faithful paraphrase. p34's is spliced in verbatim. ⚠ The block was re-serialised in the same edit, so the whitespace moved too; verified that the parsed objects differ in `idiom.why` **and nothing else**, that the p25-specific prefix of `why` is byte-identical to before, and that the tail is byte-identical to p34's. |

⚠⚠ **NO PIN *VALUE* MOVED — AND THIS SENTENCE USED TO SAY *"no entry moved"*,
WHICH IS FALSE** (`TASK_158` minor 10). Three entries' **prose** moved at step 2,
by exactly the 25 `\\u26a0` → `⚠` normalisations the table above calls cosmetic.
Here is the diff, key by key, produced by parsing each pair and diffing the
objects — the instrument is `.temp/t159/contract_steps.py`, and
`harness/tools/contract_diff.py p25` says the shipped block is `UNCHANGED`
against `HEAD`:

```
step 1  first_written -> after_no_reloc     /idiom/why                    +521 chars
step 2  after_no_reloc -> after_escapes     /collapse/note                 -10
                                            /identity[0]/why               -10
                                            /idiom/why                     -85
                                            /miri/reason                   -10
                                            /verus/obligations_note         -5
                                            /verus/twin_obligations_note    -5
                                                              == exactly 25 escapes
step 3  after_escapes -> after_shared_para  /idiom/why                  +9568 chars
        after_shared_para -> SHIPPED        parsed objects IDENTICAL
```

**So: `identity`, `collapse` and `miri` DID move, and no `required`, `forbidden`,
`identity`, `obligations`, `driver`, `collapse` or `miri` PIN VALUE did** — every
step-2 change is `⚠`-escape normalisation inside a free-text `why` / `note` /
`reason` field, and the character counts sum to precisely the 25 escapes the
table describes. ⚠ **A disclosure is what a reviewer trusts INSTEAD of
re-checking, so a wrong one removes the check it was meant to enable**; that is
why this now prints the diff rather than asserting the conclusion.
`.temp/t157/contract_after_no_reloc.json`, `.temp/t157/contract_after_escapes.json`
and `.temp/t157/contract_after_shared_para.json` are the intermediate texts, and
all four re-hash exactly to the four digests above.

⚠ **And rule 6 is necessary, not sufficient** (p46's lesson): the hashed `why`
was re-read against the measured numbers before finishing, which is how the
`malloc` census sentence was caught.

## 1. ⚠⚠ The novelty census — and it REFUTES the manager's figure

`spec.md` and `c/kernel.h` both rest on *"no other built row has an allocation
that MOVES while logically live"*. `.temp/mgr155/NOTES.md` §6 published, as a
measurement:

> ~~`grep -rln 'realloc' patterns/*/c/` → 0 files, all 30 patterns; C rungs that
> call `malloc` at all → `p10 p27 p28 p29 p32 p42` (6 of 30)~~

`controls/no_reloc.py` blanks comments and string literals first — the same rule
`harness/check.py::exec_code` applies to the rung sources — and gets:

```
32 patterns with a c/ directory
  call `realloc`                   :  1   [p25]
  call malloc/calloc/aligned_alloc :  5   [p27, p28, p29, p34, p42]
  call `free`                      : 32   [every pattern]
```

**Two errors in one line, and they go opposite ways.** `p10` and `p32` are
**false positives** — both mention `malloc` only in prose, and `p32/c/kernel.h`
line 29 literally says *"neither `malloc`'d nor `free`d per use"*, i.e. the grep
counted a sentence that denies the thing it counted. And **`p34` is missing**,
though it really does allocate (`malloc(sizeof *o)` in both C rungs) and was
committed before `mgr155` ran.

✅ **The load-bearing half survives and is now comment-blanked: `realloc` is
called by exactly one pattern's `c/`, and it is p25.** ⚠ The `free` column is the
useful negative: **32 of 32**, because every `c/main.c` frees the driver payload,
so *"calls `free`"* is not a distinguishing token and this row's distinction has
to be stated about the **kernel**, which `c/kernel.h` does.

⚠ **What the census settles is the TOKEN question, not the semantic one.** *"No
other row has an allocation that moves while live"* is an argument, it is in
`spec.md`, and this is its load-bearing premise rather than its whole content.

## 2. The detectors, and which of them is biased

### 2a. The per-detector table (`controls/detectors.py`, gcc `-O1`)

Two positive controls, each firing only in its own detector — because **a UBSan
build that says nothing looks exactly like one that was never linked in**, and
`.temp/mgr155/NOTES.md` §3 caught this row's own pre-build demonstration in
precisely that state:

```
ctl_asan.c   under asan   exit=1   ASan fires      under ubsan  exit=0  silent
ctl_ubsan.c  under asan   exit=0   silent          under ubsan  exit=1  UBSan fires
```

Then both C arms, every input, both detectors:

| input | `model.py` says | R1 ASan | R1 UBSan | R1h ASan | R1h UBSan |
|---|---|---|---|---|---|
| `small` | clean | silent | silent | silent | silent |
| `large` | clean | silent | silent | silent | silent |
| `degenerate` | clean | silent | silent | silent | silent |
| `adversarial-nogrow` | **clean** | silent | silent | silent | silent |
| `adversarial-stride3` | clean | silent | silent | silent | silent |
| `adversarial-move` | **fires** | **fires** | silent | silent | silent |
| `adversarial-lateread` | **fires** | **fires** | silent | silent | silent |
| `adversarial-many` | **fires** | **fires** | silent | silent | silent |

⚠ **`adversarial-nogrow` is the row that makes this a measurement.** It is an
`adversarial-*` file that derives `clean`: it has the SAVE and the READ and no
growth between them, so nothing is retired and R1 is correct. Without it,
*"the adversarial rows fire"* would be true of the filename rather than of the
detector.

✅ **R1h is clean under BOTH detectors on EVERY input, adversarial included** —
gate stage `7h`'s standard, kept locally as well, because `p28d`'s hardened arm
SEGVed on a *benign* input and no gate stage had ever looked.

✅ **UBSan is silent on every input**, and that is **derived** rather than
observed-and-hoped: R1's undefined behaviour is entirely temporal — `toks[ntok]`
is written only after the block has been grown to hold it, `&toks[a % ntok]` is
formed only under `ntok > 0`, and the cursor guard is subtraction-first — so
there is no spatial violation for UBSan to see. The claim is licensed by
`ctl_ubsan.c` and by nothing else.

### 2b. ⚠ ASan is the BIASED half, and the row does not rest on it

**ASan's allocator moves on every `realloc`**, so the ASan column would fire even
under a heap topology in which glibc never relocated. Two consequences, both
stated rather than hidden:

* the **unbiased** evidence is the plain-build divergence in §2c;
* `model.py`'s derived `sanitizer_expect` models **ASan's** semantics — *the
  token vector was reallocated while a saved pointer was live* — not glibc's.
  That is the checkable choice (the gate compares against an ASan build) and the
  conservative one: every read it calls stale is a read C already calls
  undefined (C11 7.22.3.5p4, DR 400).

### 2c. The plain-build divergence, and the collision it owes

R1h's adversarial answers are **single-valued on every build measured** — gcc and
clang, `-O0`/`-O1`/`-O3`, plain/ASan/UBSan:

```
adversarial-move       11296769385036522496
adversarial-lateread   14062580838451436544
adversarial-many         418471180153818624
adversarial-nogrow     16907751744586910720   (== R1, no relocation)
```

R1's are **not**: on the three relocating inputs it differs between gcc `-O0`,
gcc `-O3`, clang `-O0` and clang `-O3`, and between runs, because it is folding
whatever the retired block now holds.

⚠⚠ **THE ROW DOES NOT PIN `R1 ≠ R1h`, AND THE REASON IS ARITHMETIC.** The
divergence is one byte in a Horner chain, so R1 equals R1h exactly when the
retired block's byte at `curi` happens to equal the byte `realloc` copied
forward — about **1 run in 256**. `p29` is the precedent and it already solved
this: **gate on the invariant, publish no pinned count.** What is pinned is
R1h's value and `sanitizer_expect`; the divergence is reported and never gated.

⚠⚠ **AND THAT SETTLES THE SENTINEL QUESTION `TASK_157` NAMED AS ITS LEAST
CERTAIN CALL — by removing it.** `.temp/mgr155/` measured the collision on a
hardened cell whose `else` folded `P25_SENT`, so `R1h == min + 31·251` sat inside
R1's range and the fix was to move the sentinel out of byte range at a cost of
`+4`/`+5` static instructions. **The shipped cell folds no sentinel at the safety
line at all** (§3), so *"R1h is the sentinel value"* has no analogue, no sentinel
choice changes anything, and the `+4`/`+5` static cost is not paid. The residual
1-in-256 R1-vs-R1h collision is intrinsic to a one-byte divergence and is
disclosed here rather than engineered away.

## 3. ⚠⚠ The hardened cell RE-DERIVES, and that is forced

The obvious hardened cell is

```c
if (curbase == toks) v = (uint64_t)*cur; else v = P25_SENT;
```

and it **cannot be shipped**. It makes the kernel's **answer a function of the
allocator**: whether `realloc` relocates is a heap-topology fact, so `model.py`
could not derive the checksum without simulating glibc, and the four Rust rungs
— whose `Vec` grows on a different schedule (§5) — could not agree with the C
ones on the adversarial input. `harness/check.py` stage 2's *"every checked rung
agrees with the model"* would be **unsatisfiable in principle**.

The shipped cell re-derives instead, and that is allocator-independent because
**`realloc` copies**: `toks[curi]` after the move is the byte `*cur` named before
it. ⚠ **So the conjunct buys MEMORY SAFETY and buys nothing else** — both
branches compute the same value in every terminating execution — which makes the
R1-vs-R1h gradient a clean price for memory safety alone.

### 3a. The safety line, measured (`controls/safety_line.py`)

```
kernel.c          328 preprocessed lines
kernel_hardened.c 330 preprocessed lines
diff  +3 / -1     net +2
  + } else if (curbase == toks) {
  + v = (uint64_t)*cur;
  + v = (uint64_t)toks[curi];
  - v = (uint64_t)*cur;
arm_body.inc @ SLB_HARDEN 0  ==  kernel.c           IDENTICAL
arm_body.inc @ SLB_HARDEN 1  ==  kernel_hardened.c  IDENTICAL
```

⚠ **It is NOT a pure addition and the first version of that control asserted it
was and failed.** The removal is not a deletion: the read `v = (uint64_t)*cur;`
**moves** out of an unguarded `else` into the branch the conjunct guards. The
control now checks the exact line multiset, which says more than a `+N / −0`
shape would.

⚠ **`.temp/mgr155/` measured `+4 / −1` for the SENT-folding cell.** That number
is about a different program and is not this row's.

### 3b. ⚠⚠ The conjunct is NOT the standard-clean repair

C99 7.20.3.4p4 / C11 7.22.3.5p4 with **DR 400** make the old pointer value
indeterminate the moment `realloc` returns, **whether or not the block moved**.
So the surviving `*cur` in R1h's true branch is a use of an indeterminate value
under the abstract machine, even though no relocating allocator can observe it —
under ASan the true branch is taken only when no `realloc` happened at all, which
is why R1h is ASan-clean everywhere.

⚠⚠ **AND THE READING IS BROADER THAN THE DEREFERENCE — THIS SENTENCE USED TO
STOP AT `*cur` AND THAT WAS TOO NARROW** (`TASK_158` minor 4). **`curbase == toks`
is itself a read of an indeterminate pointer value, on EVERY path including the
false one.** The dereference is the vivid case; the *comparison* is what makes
the whole guarded form unreachable-by-repair. That broader statement is what
actually licenses the conclusion below, and it is also why the growth-site arm
`fixup` (`if (cur != NULL) …`) is **not** standard-clean while `fixup2`, which
tests an `int`, is (§3c).

⚠ **The citation is loose and the claim is not** (`TASK_158` minor 5). **WG14
DR 400 is titled *"realloc with size zero problems"***; the load-bearing text for
*"indeterminate whether or not it moved"* is **C11 6.2.4p2** (a pointer's value
becomes indeterminate when the object's lifetime ends) together with **7.22.3.5p4**
(*"deallocates the old object"*), with **DR 260** for *"an indeterminate value may
change"*. The number *DR 400* is quoted as shorthand in `spec.md`'s hashed `why`,
`c/kernel.c`, `README.md` and `controls/rederive.py`; **it is not the authority
for the claim, and those four spellings were left alone deliberately** — `spec.md`
inside the fence costs a `contract_sha256` move and `c/kernel.c` costs a
re-measure, and neither is worth a citation shorthand.

**The only C rung DR 400 cannot reach is the UNCONDITIONAL re-derive**, which is
precisely the addressing-mode change `TASK_134`'s kill named. `controls/rederive.py`
generates it from the shipped `c/kernel.c` by one asserted substitution and
prices it (§3c) — alongside the two GROWTH-site arms, of which `fixup2` is the
second standard-clean repair.

> **So both halves of the old kill are answered and they go opposite ways: the
> conjunct EXISTS (the first half is refuted, and §3a is it) and it is
> INSUFFICIENT (the second half is vindicated, for a reason nobody had stated).**

### 3c. ⚠⚠ THREE REPAIR SITES — AND THE ORDERING BETWEEN THE TWO STANDARD-CLEAN ONES REVERSES BETWEEN OPTIMISATION LEVELS

`controls/rederive.py`, re-run at `TASK_159`. **Every arm agrees with `model.py`
on 8 of 8 inputs — benign and adversarial — and every one is ASan- and
UBSan-clean on all of them** (24 checksums, `problems: []`).

⚠⚠ **THIS SECTION USED TO PUBLISH A GCC-ONLY DYNAMIC TABLE UNDER THE WORDS *"on
both compilers"*, AND USED TO CLAIM *"the safer repair dominates"* OF THE CLASS
(`TASK_158` M5, M6). Both are corrected here, and the correction is in the row's
own disfavour on one axis and in its favour on the other.**

⚠ **THE CONVENTION, BECAUSE THIS ROW HAS TWO AND THEY DISAGREE (§8a):** every
`Ir` figure below is **KERNEL-EXCLUSIVE** — `controls/rederive.py::kernel_ir`
sums the `callgrind_annotate` rows matching `measure.py`'s own kernel needle.
`rederive.json`'s field is spelled `marginal_ir_per_call`, which **collides with
the gate record's key of the same name, and that one is WHOLE-PROGRAM.**

**The three sites.** `R1h` guards the READ; `rederive` replaces the READ; `fixup`
and `fixup2` refresh `cur` at the GROWTH and leave the READ as R1 writes it.
⚠ **`fixup` is NOT standard-clean** — `if (cur != NULL)` is itself an evaluation
of the pointer value `realloc` made indeterminate (§3b). **`fixup2` carries the
"a SAVE has happened" bit in an `int` and reads no indeterminate value.** So the
standard-clean set is `{rederive, fixup2}` and `fixup` is priced as the spelling
a C programmer reaches for first.

**Static `kernel` instructions (non-pad, `-DSLB_ISOLATED`), over R1:**

| | gcc `-O0` | gcc `-O3` | clang `-O0` | clang `-O3` |
|---|---|---|---|---|
| R1 | 218 | 165 | 209 | 150 |
| R1h (READ, guarded — **shipped**) | 228 (**+10**) | 176 (**+11**) | 218 (**+9**) | 162 (**+12**) |
| `rederive` (READ, unconditional) | 220 (**+2**) | 168 (**+3**) | 210 (**+1**) | 152 (**+2**) |
| `fixup` (GROWTH, ⚠ not clean) | 224 (**+6**) | 171 (**+6**) | 215 (**+6**) | 158 (**+8**) |
| `fixup2` (GROWTH, clean) | 226 (**+8**) | 175 (**+10**) | 217 (**+8**) | 161 (**+11**) |

**Marginal `Ir` per kernel call over R1, kernel-exclusive, `isolated`,
`(Ir@200 − Ir@100) / 100`, BOTH compilers and BOTH levels:**

| cc | input | opt | R1 | R1h | `rederive` | `fixup` ⚠ | `fixup2` |
|---|---|---|---:|---:|---:|---:|---:|
| gcc | `small` | `-O0` | 1375.16 | **+14.76** | **+7.38** | +2.18 | **+5.90** |
| gcc | `small` | `-O3` | 703.85 | **+24.69** | **+10.87** | +14.14 | **+21.67** |
| gcc | `large` | `-O0` | 6540.98 | **+131.08** | **+65.54** | +2.68 | **+19.77** |
| gcc | `large` | `-O3` | 3173.74 | **+164.39** | **+65.67** | +69.69 | **+104.21** |
| clang | `small` | `-O0` | 1418.11 | **+18.45** | **+3.69** | +3.27 | **+6.99** |
| clang | `small` | `-O3` | 738.80 | **+18.72** | **+3.72** | +17.25 | **+26.43** |
| clang | `large` | `-O0` | 6828.46 | **+163.85** | **+32.77** | +4.02 | **+21.11** |
| clang | `large` | `-O3` | 3263.16 | **+93.65** | **+17.09** | +60.47 | **+128.85** |

**1. The direction survives and the MAGNITUDE was a gcc-only figure.** The
unconditional re-derive is cheaper than the shipped conjunct at every one of the
eight cells, but *"about half"* is **gcc's** number and no other:

| R1h ÷ `rederive`, over R1 | `small -O0` | `small -O3` | `large -O0` | `large -O3` |
|---|---:|---:|---:|---:|
| **gcc** | 2.00× | 2.27× | 2.00× | 2.50× |
| **clang** | 5.00× | 5.03× | 5.00× | 5.48× |

> ⚠⚠ **The repair that is correct under the C standard costs `2.0–2.5×` less
> than the idiomatic conjunct on gcc and `5.0–5.5×` less on clang. Say which
> compiler.** The statically countable cost tells the same story with different
> numbers (`+10/+11` against `+2/+3` on gcc, `+9/+12` against `+1/+2` on clang).

**2. *"The safer repair dominates"* is FALSE OF THE CLASS**, though it is true of
the shipped pair. Between the two **standard-clean** repairs the ordering
reverses with the optimisation level:

```
gcc   large -O0   rederive +65.54   fixup2 +19.77   <- fixup2, 3.32x cheaper
gcc   small -O0   rederive  +7.38   fixup2  +5.90   <- fixup2, 1.25x
clang large -O0   rederive +32.77   fixup2 +21.11   <- fixup2, 1.55x
clang small -O0   rederive  +3.69   fixup2  +6.99   <- rederive, 1.89x
every       -O3   rederive wins, by 1.59x (gcc large) to 7.54x (clang large)
```

> ⚠⚠ **A comparison that reverses between optimisation levels is not a fact
> about the things compared** (`p35`'s lesson, here on a third axis: the repair
> SITE). What is true is narrower and is what this row publishes: **of the two
> spellings on the READ, the standard-clean one is cheaper at every cell; of the
> two standard-clean repairs, which one wins depends on the level.**

⚠ **NAME THE WEAKER-SEARCHED ENDPOINT** (`TASK_157` deliverable 4; the trap has
now fired seven times). The **site** is now searched — three of them — and one
respelling lever was tried at each READ site and moved nothing: `TASK_158` §4b
found a ternary spelling of R1h and a `*(toks + curi)` spelling of `rederive`
equal to their originals **to the hundredth at every cell**, so neither shipped
figure is a spelling artefact on that lever. ⚠ **What is still unsearched is the
spelling of the GROWTH-site repair**: `fixup2` is one way to carry the bit, and a
`curbase`-style sentinel or an index-only rewrite were not built. The inline mode
is **isolated** in every row of both tables.

## 4. The benign gradient, and how it differs from p34's

⚠ **Unlike p34, p25's safety line EXECUTES on every benign input.** Every `READ`
evaluates `curbase == toks`; what no benign input does is take the `else` branch.
So p25 has a real, non-zero benign gradient where p34's is `0.00`.

**R1h − R1, kernel-exclusive marginal `Ir`/call, `isolated`, BOTH compilers and
BOTH optimisation levels** (the full matrix is §8, and §3c prices the
standard-clean alternative beside it):

| | `small` `-O0` | `small` `-O3` | `large` `-O0` | `large` `-O3` |
|---|---|---|---|---|
| **gcc** | **+14.76** | **+24.69** | **+131.08** | **+164.39** |
| **clang** | **+18.45** | **+18.72** | **+163.85** | **+93.65** |

⚠ **Both compilers are given because they disagree about the SHAPE**: gcc's cost
grows from `-O0` to `-O3` on both inputs, clang's *falls* on `large`
(163.85 → 93.65). A one-compiler, one-level figure would have read as a law.

**The corollary is a hard constraint on the inputs** — *no non-adversarial window
may read through an interior pointer whose token vector has been reallocated
since the SAVE* — and it is enforced in three independent places rather than
assumed:

* `inputs/gen.py` constructs streams in which a `PUSHT` after a `SAVE` is emitted
  only while it cannot trigger a `realloc`, and re-simulates every blob it writes;
* `model.py::stale_free_problems` re-derives the property from the **shipped**
  blob on every gate invocation;
* `controls/no_stale.py` censuses the whole directory — **8 matrix/adversarial
  files and 57 sweep bands, 0 problems**, with the split printed per file so
  *"the adversarial rows fire"* is readable as a measurement.

The reason is `2b`: ASan's allocator moves on every `realloc`, so a benign window
that went stale would make R1 report `heap-use-after-free` on a row whose
`sanitizer_expect` is `clean`, and stage 7 would fail.

## 5. The rungs, and where they are NOT the same program

### 5a. The growth policy — the one real difference between C and `Vec`

The C rungs write the capacity discipline out (`tcap` doubling from `SEED = 4`,
capped at `MAXCAP = 64`); the four Rust rungs write `if v.len() < MAXCAP {
v.push(a) }` and no capacity variable at all. **The acceptance semantics are
identical** — `MAXCAP` is `SEED · 2^k`, so growth at `n == cap` from `cap = SEED`
makes the guard fire at exactly `n == MAXCAP`, which is what `spec.md`'s
`required` entry pins — but the **allocator-call counts are not**:

```
C rungs        capacity sequence to len 64:  4, 8, 16, 32, 64   -> 5 realloc calls
Vec<u8>::push  capacity sequence to len 64:  8, 16, 32, 64      -> 4 alloc  calls
               (measured: .temp/t157/vecgrow/cap.rs prints [8, 16, 32, 64, 128])
```

⚠ **So a fully-grown token vector costs C one more allocator call than Rust**,
and any C-vs-Rust `Ir` difference on this row contains that term. It is disclosed
here rather than folded into a headline.

### 5b. What is deliberately NOT pinned

How R3 walks the op stream — `chunks_exact(2).take(nops)` against R2's cursor,
and `match c % 4` against R2's `if` chain — exactly as p32 leaves its
handle-register spelling unpinned, p34 leaves its op walk and p14 leaves its fold
loop. That is the R3 lever and it costs zero TCB.

**What it moves** (R3 − R2, `isolated`; the full matrix and the two-column
caveat are §8):

| | `small` `-O0` | `small` `-O3` | `large` `-O0` | `large` `-O3` |
|---|---|---|---|---|
| kernel-exclusive | **−9.47** | **−191.13** | **−309.89** | **−982.75** |
| whole-program | **+2066.53** | −191.13 | **+9542.11** | −982.75 |

⚠⚠ **The two columns DISAGREE ABOUT THE SIGN at `-O0`, and §8a is why**: the
`chunks_exact` iterator is a separate, un-inlined symbol there, so it is outside
the `kernel` extent that the left row counts. At `-O3` it is inlined and the two
agree exactly. **Neither row is wrong; they answer different questions, and
quoting one without the other would publish a lever that either costs nothing or
costs 3.5×.**

⚠ **TWO levers move at once here** — the walk AND the opcode dispatch — so this
is *not* an in-contract spread for either of them separately, and §8c says so.

## 6. The R5, and what is NOT there is the result

`./verus_run.py verus.rs` → **`10 verified, 0 errors`**; `--cfg slb_twin` →
**`12 verified, 0 errors`**.

### 6a. The obligation census, MEASURED per function

`.temp/t157/verus/obligations.sh`, one `--verify-function <name> --verify-root`
run each; the log is `.temp/t157/verus/obligations.log`:

```
u32_at 0   nops_at 0   run 1   parse_fold 0
buf_get_unchecked 0    vec_get_unchecked 0    load_input 0   emit 0
kernel 2   main 5
```

`0+0+1+0+0+0+0+0+2+5 = 8` function terms **+ 2 consts** (`MAXCAP`, `SENT`) = the
pinned **10**. ⚠ p25 declares no struct, so there is no `derive` term and no
bare-struct term — p29's derive term and p32's bare-struct zero have no analogue
here.

### 6b. ⚠⚠ THE TEMPORAL OBLIGATION HAS NO ANALOGUE AT R5

Writing `c/kernel.c`'s READ in Rust needs a raw `*const u8` dereferenced under
`curbase == toks.as_ptr()`, and **Verus cannot license it**:

* reading `*cur` needs a `PointsTo` permission, and no vstd API at the pin yields
  one for a `Vec`'s buffer;
* the guard is an **address** comparison while Verus's pointers carry
  **provenance** (`PtrData { addr, provenance, metadata }`), so address equality
  does not entail that the permission you hold names that byte. **The guard is
  exactly the fact the proof would need and exactly the fact address equality
  does not give.**

So R4 and R5 save an index, `realloc` copies, and the read is correct by
construction. What is left to prove is `have ==> curi < toks@.len()` — a spatial
obligation, easy because a vector only grows.

> ⚠⚠ **p25 is the first row in this tree where the LADDER DELETES THE BUG above
> R1 rather than making it provable, and the honest statement of the R5 result is
> that its obligation is SMALLER than p27's, p29's, p32's or p34's.**

⚠ **That is a claim about the PROOF rung and not about Rust**, and
`controls/rust_bug.py` is what keeps the two apart: `controls/arm_unsafe_ptr.rs`
is `unsafe.rs` with the index replaced by `toks.as_ptr().add(curi)` and nothing
else, and it expresses the bug perfectly well (§7).

### 6c. The mutant battery — a small obligation gets MORE scrutiny, not less

`controls/proof_mutants.py`. Baseline `10 verified, 0 errors`; every substitution
count asserted to be exactly 1 before the mutant runs.

| arm | mutation | Verus |
|---|---|---|
| **ATTACK** | delete `have ==> curi < toks@.len()` from the loop invariant | `9 / 1` — **`precondition not satisfied`** (`vec_get_unchecked`) |
| **X1** | keep the invariant, strike the statement that re-establishes it (`curi = (a as usize) % toks.len();` → `curi = a as usize;`) | `9 / 1` — **`invariant not satisfied at end of loop body`** |
| **VACUITY** | a constant kernel body (`return 0;` first) | `8 / 1` — **`postcondition not satisfied`** |
| **SPEC-WEAKEN** | kernel `ensures r == parse_fold(..)` → `r == r`, `main` untouched | `9 / 1` — **`assertion failed`** at the call site |

⚠ **The diagnostics are the point, not just the failures.** ATTACK fails at the
READ and X1 fails at the SAVE, which is what says the conjunct is doing work
rather than being implied; and SPEC-WEAKEN fails in `main`, which is what says
the `assert(r == parse_fold(..))` there is load-bearing — without it the
postcondition would be decoration and deleting it entirely would still verify
(`.memory/04-verus.md`).

### 6d. The trusted base — FOUR items, three fewer than p27's and p34's

`buf_get_unchecked`, `vec_get_unchecked`, `load_input`, `emit`. Two are inside
the twin regime (`external_body` + an `ensures`) and **both are twinned**;
`load_input` and `emit` state no `ensures` and have no `unsafe` body, so they are
outside it and owe no twin. **`blocked` is `[]`** — p27's, p32's and p34's
position, not p35's.

⚠ **The reason for the smaller TCB is the same fact as §6b**: this rung allocates
through `Vec`, so allocation and deallocation are vstd's problem rather than this
file's and there is no `rec_alloc`/`rec_free` pair to trust.

⚠ **p25's R5 is the first in this tree to call `Vec::push` in exec code** —
measured, not assumed: no other `verus.rs` under `patterns/` contains an exec
`.push(` on a `Vec` (p14's, p27's, p28's, p29's and p34's are all `Seq` pushes in
ghost code). vstd's `assume_specification[Vec::push]` carries
`final(vec)@ == old(vec)@.push(value)` and **no `requires` at all**, so the
growth costs no trusted item; `vstd::std_specs::vec::group_vec_axioms` is what
ties `vec.len()` to `vec@.len()`, and no other pattern in the tree needs that
group.

## 7. Miri — the must-fire pair

`controls/rust_bug.py`, `n_iters` clamped to 4 (`check.py::MIRI_PROBE_ITERS`),
payload untouched:

| input | shipped `unsafe.rs` | `controls/arm_unsafe_ptr.rs` |
|---|---|---|
| `adversarial-move` | clean | **UB**: `memory access failed: allocNNNN has been freed, so this pointer is dangling` |
| `adversarial-lateread` | clean | **UB**, same class |
| `adversarial-many` | clean | **UB**, same class |
| `adversarial-nogrow` | clean | **clean**, and the same answer |
| `small` | clean | **clean**, and the same answer |

⚠ **Both halves matter.** The must-fire arm fires on exactly the inputs whose
windows grow the token vector after the SAVE, and is **silent** on the two that
do not — so it is not an arm that fires on everything, which is the other way for
a must-fire arm to be worthless (`TASK_145_REPORT` §4b on p32).

✅ **And this is what licenses §6b's wording.** Unsafe Rust *can* express p25's
bug; what excludes it from the shipped rung is the `identity` pin plus Verus's
provenance, not the language.

## 8. The measured matrix

### 8a. ⚠⚠ TWO Ir COLUMNS, AND THEY DISAGREE ABOUT WHICH SAFE RUNG IS FASTER

**Read this before quoting any number below.** The gate's
`marginal_ir_per_call` is computed from callgrind's `summary:` line — **the whole
program** — while `results/p25-realloc-growth.json`'s `kernel_exclusive_ir` is
the `kernel` symbol alone. On most patterns the two move together. **On p25 they
do not, because p25's kernel calls out of itself**: into `realloc`, into
`RawVec::grow_one`, and at `-O0` into the `chunks_exact` iterator, none of which
is inside the `kernel` symbol.

Both columns are given below, and each answers a different question — *what the
kernel's own instructions cost* against *what the rung costs the program*. Two
places where reading only one would have published something false:

* ⚠ **the gate column shows an R4→R5 "proof tax" of about `+269` Ir/call on
  `large` `-O3` (5379 → 5649) and there is no such thing.** Measured directly
  (`.temp/t157/irprobe/`), the two kernels cost **exactly** 9104.17 (`-O0`) and
  **exactly** 4152.71 (`-O3`), and `realloc` (205.36), `finish_grow` (159.48),
  `grow_one` (127.00) and `malloc` (84.00) are identical to the instruction in
  both binaries.
  **Conclusion, which stands on its own: the R4 and R5 KERNELS cost identical Ir
  at both levels, and the whole-program delta is not a proof cost.**

  ✅ **MECHANISM — CLOSED at `TASK_158`, over EVERY function, and it is SIX
  routines rather than the three this section first named.**
  `.temp/t158/symdiff.py`, `-O3 isolated large.bin`, environment pads 0 and 16
  giving results identical to the hundredth (`check_marginal_ir`'s own
  16-wide-window argument makes a two-pad screen a *complete* phase detector):

  ```
  verus::kernel − unsafe::kernel  =  0.00   (4152.71 each)
  verus::main   − unsafe::main    =  0.00   (  14.00 each)
  SIX glibc malloc-internal symbols            SUM = +268.88 = 100.0 % of it
    0xab570 +133.54  (reached from malloc and from 0xacf50 -> _int_malloc)
    0xab170 +111.44  (reached from free   and from 0xacf50 -> _int_free)
    0xa9ad0  +46.50 · 0xa9bb0 −31.62 · 0xacf50 +12.30 (from realloc) · 0xa91f0 −3.28
  ```

  ⚠ **This section previously said *"three unnamed libc routines — 461.00 against
  718.28"*, which is 95.7 % of the delta and reads as closed** (`TASK_158`
  minor 1): `133.54 + 111.44 + 12.30 = 257.28`, and the remaining `+11.60` is
  three further symbols. **It is NOT the environment-phase effect** (identical
  at pads 0 and 16). Symbol names are unavailable — `libc6-dbg` is absent on
  this box — so the caller edges identify them.

  ⚠ **QUOTE THIS TO THE INSTRUCTION, NOT TO THE HUNDREDTH**
  (`check_marginal_ir`'s own rule; `TASK_158` minor 2). The gate record says
  `verus … 5648.91`; two independent re-runs both give **5648.27**, a drift of
  **0.64** — 32× the ±0.02 scratch-directory term. **`unsafe` reproduces
  exactly at 5379.39.** So the honest figure is *"about +269"* and never
  *"+269.52"*.
* ⚠ **the two columns invert R2 against R3 at `-O0`.** Kernel-only they are
  within 0.6 % (`small`: 1710.46 vs 1700.99); whole-program R3 is **1.75×
  DEARER** (2741.37 vs 4807.90), and on `large` **1.75×** again (12678.50 vs
  22220.61). The `chunks_exact(2).take(nops)` iterator is a separate,
  un-inlined symbol at `-O0`, so the kernel-exclusive column does not contain
  it. At `-O3` both columns agree that R3 is cheaper.

**`small.bin`, `isolated`:**

| rung | kernel-only `-O0` | kernel-only `-O3` | whole-program `-O0` | whole-program `-O3` |
|---|---|---|---|---|
| R1 `c-gcc` | 1375.16 | 703.85 | 1896.43 | 1204.12 |
| R1h `c-gcc-h` | 1389.92 | 728.54 | 1911.19 | 1228.81 |
| R1 `c-clang` | 1418.11 | 738.8 | 1913.5 | 1227.19 |
| R1h `c-clang-h` | 1436.56 | 757.52 | 1931.95 | 1245.91 |
| R2 `safe_naive` | 1710.46 | 978.41 | 2741.37 | 1428.76 |
| R3 `safe_tuned` | 1700.99 | 787.28 | 4807.9 | 1237.63 |
| R4 `unsafe` | 1812.67 | 848.47 | 3608.82 | 1298.82 |
| R5 `verus` | 1812.67 | 848.47 | 3608.82 | 1298.82 |

**`large.bin`, `isolated`:**

| rung | kernel-only `-O0` | kernel-only `-O3` | whole-program `-O0` | whole-program `-O3` |
|---|---|---|---|---|
| R1 `c-gcc` | 6540.98 | 3173.74 | 7684.68 | 4296.44 |
| R1h `c-gcc-h` | 6672.06 | 3338.13 | 7815.76 | 4460.83 |
| R1 `c-clang` | 6828.46 | 3263.16 | 7940.48 | 4368.18 |
| R1h `c-clang-h` | 6992.31 | 3356.81 | 8104.33 | 4461.83 |
| R2 `safe_naive` | 8452.24 | 4773.55 | 12678.5 | 6000.23 |
| R3 `safe_tuned` | 8142.35 | 3790.8 | 22220.61 | 5017.48 |
| R4 `unsafe` | 9104.17 | 4152.71 | 16859.35 | 5379.39 |
| R5 `verus` | 9104.17 | 4152.71 | 17128.87 | 5648.91 |

### 8b. What the matrix says

**R4 == R5, exactly, in every kernel-only cell** (4 of 4). The project's standing
R4/R5 result — the proof licenses the unsafe code at zero instruction cost —
reproduces here, and §8a is why it has to be read off the kernel column.

⚠⚠ **AND QUOTE THE `md5` WITH IT, BECAUSE p25's `identity` IS `norel`, NOT
`exact`, AT BOTH LEVELS** (`.memory/03-measurement.md`: *"quote the `md5` when
saying a proof costs zero"*; `TASK_158` minor 7). **The gate record's two
`identity` entries both carry `md5_raw_equal: false`**, and `spec.md`:169 / :427
disclose the mechanism in full: the two crates place `kernel` `0x20` apart, so
every intra-function displacement carries that offset — `lea -0xde51(%rip)`
against `lea -0xde31(%rip)`, **both resolving to the same absolute `0x7910`** —
while `md5_fn_norel`, `md5_raw_norel` and `md5_norm` are identical and the
counts are equal on both sides: **`[189, 189, 751]` at `-O3`** and
**`[313, 313, 1791]` at `-O0`**. `md5_fn_norel` zeroes
branch-displacement fields, so `norel` does **not** entail `Ir` equality in
general; what licenses the zero here is the equal instruction count plus the
measured 4-of-4 `Ir` equality above, not the digest alone.

**The safety line, R1h − R1** (kernel-only, so this is the conjunct itself and
not the allocator):

| | `small` `-O0` | `small` `-O3` | `large` `-O0` | `large` `-O3` |
|---|---|---|---|---|
| gcc | +14.76 | +24.69 | +131.08 | +164.39 |
| clang | +18.45 | +18.72 | +163.85 | +93.65 |

⚠ **Non-zero everywhere, unlike p34's `0.00`**, because p25's safety line
*executes* on every benign input (§4) — and `controls/rederive.py` prices the
standard-clean alternative at **`2.0–2.5×` less on gcc and `5.0–5.5×` less on
clang** (§3c; *"about half"* was gcc's number quoted as both compilers').
⚠ **Both compilers and both levels are given because they do not agree on the
shape**: gcc's cost grows from `-O0` to `-O3` on both inputs, clang's *falls* on
`large` (163.85 → 93.65). A single-compiler, single-level figure would have
looked like a law.

**⚠⚠ THE R3 WALK LEVER IS WORTH MORE THAN ALL OF R4's `unsafe`, at `-O3`.**
Kernel-only, R3 beats R4 on both inputs — `small` 787.28 against 848.47, `large`
3790.80 against 4152.71 — so `chunks_exact(2).take(nops)` plus `match c % 4`
saves more than `buf_get_unchecked` and `vec_get_unchecked` do. ⚠ That is a
statement about **these two spellings**, not about safe-vs-unsafe: `spec.md`
deliberately leaves the walk unpinned (§5b), so R4 could adopt it, and nobody has
built that cell.

**C against Rust**, kernel-only, best Rust cell per column:

| | `-O0` | `-O3` |
|---|---|---|
| `small` | 1375.16 (gcc) vs 1700.99 (R3) — **+23.7 %** | 703.85 vs 787.28 (R3) — **+11.9 %** |
| `large` | 6540.98 (gcc) vs 8142.35 (R3) — **+24.5 %** | 3173.74 vs 3790.80 (R3) — **+19.4 %** |

⚠ **And Rust pays that DESPITE an allocator advantage**: `Vec<u8>` makes one
FEWER allocator call per fully-grown token vector than the C rungs do (§5a).

**Static `kernel` instructions** are in §3c for the three C arms; the gate's
stage 3a table has all 32 cells.

### 8c. What is NOT here

* **No wall-clock claim.** `results/p25-realloc-growth.json` carries the timing
  block and it is secondary by `.memory/03-measurement.md`; nothing in this file
  rests on it.
* **No in-contract spread.** `spec.md` leaves R3's walk and opcode dispatch
  unpinned, so the admissible class is wider than the shipped cell — but only
  ONE alternative spelling was built (R2's cursor, which is the shipped R2), so
  there is no measured spread to publish and quoting the R2/R3 gap as one would
  be wrong: they differ in TWO levers at once.
* **No `whole`-mode row.** Every figure above is `isolated`, named rather than
  implied, because in `whole` mode at `-O3` the kernel is inlined away and the
  `kernel` symbol does not exist (the gate's stage 3a table shows
  `kernel=None`).

## 9. SLB-TRUSTED-ARGUMENT sections

The gate requires one section per trusted item **as
`harness/check.py::_is_trusted` defines one** — `#[verifier::external_body]`
**with a non-empty `ensures`, or `unsafe` in the body** — and prints it in full on
every run. **It requires TWO for p25**, and there are two below.

⚠ **TWO is not the same denominator as §6d's TCB tally, and the two are easy to
mix** (`TASK_145_REPORT` §8 caught p32 doing exactly that):

| | `#[verifier::external_body]` items | sections the gate requires |
|---|---|---|
| **`p25`** | **4** | **2** |
| `p27` | 7 | 5 |
| `p29` | 7 | 7 |
| `p32` | 5 | 3 |
| `p34` | 7 | 5 |

The two p25 items the gate does **not** govern are `load_input` and `emit`: they
carry no `ensures` and no `unsafe`, so they cannot axiomatise a falsehood, which
is the property `_is_trusted` is keyed on. **§6d's sentence — *"TCB: four
`external_body` items"* — is the ITEM count and is correct.**

## SLB-TRUSTED-ARGUMENT verus.rs buf_get_unchecked

**(a) Is the twin's body the right checked stand-in?** The trusted body is
`unsafe { *v.get_unchecked(i) }` on a `&[u8]`; the twin's is `v[i]` on the same
`&[u8]`, with the same parameters and character-identical clause text. `v[i]` is
the checked form of the identical operation — rustc emits the bounds test
`i < v.len()` that `get_unchecked` requires of the caller — so a `requires` too
weak to license the unchecked read is too weak to license the indexed one, and
`--cfg slb_twin` rejects it. The gate re-derives that every run. This is the same
item every unsafe rung in this project ships and it is unchanged here.

**(b) Is the `ensures` complete with respect to every unchecked operation the
body performs?** The body performs exactly ONE unchecked operation — a read of
one element — and returns it. `r == v@[i as int]` names that element and its
value, and `v: &[u8]` is immutable so nothing can be modified. The completeness
question is `TASK_009_REVIEW`'s x4: a body that ALSO read `i + 1` would satisfy
this contract, this twin and the `--cfg slb_twin` run unchanged, and nothing in
the gate would notice. **What stands behind (b) here is that the body is one
expression, printed in full in every verdict, and that Miri interprets the
shipped `unsafe.rs` — which calls this accessor on every op byte — on five
inputs and reports nothing (§7).**

**(c) Does each clause mean the same in both configurations?** `v@` is
`vstd::slice`'s view and `v@.len()` is `spec_slice_len(v)` in both; neither is
`#[cfg]`-dependent, and the token `slb_twin` occurs nowhere but on the twin's own
attribute — which the gate checks and prints.

## SLB-TRUSTED-ARGUMENT verus.rs vec_get_unchecked

**(a) Is the twin's body the right checked stand-in?** The trusted body is
`unsafe { *v.get_unchecked(i) }` on a `&Vec<u8>`; the twin's is `v[i]` on the
same `&Vec<u8>`, same parameters, character-identical clauses. `Vec` indexing is
the checked form of the same operation — `Vec::index` goes through
`<usize as SliceIndex<[T]>>::index`, which vstd specifies with the precondition
`i < slice.len()` — so a `requires` too weak to license the unchecked read is too
weak to license the indexed one and the twin run rejects it.

⚠ **This item exists SEPARATELY from `buf_get_unchecked` because the receiver
type differs**, not because the operation does: `&[u8]` against `&Vec<u8>`.
`Vec::get_unchecked` reaches the slice method through `Deref`, and vstd
specifies neither — grepped in `~/tools/verus/vstd/std_specs/slice.rs` and
`vec.rs` before writing it, which is the check `CLAUDE.md` asks for before any
"no spec exists" claim. What vstd *does* specify is `Vec::index`, and that is
exactly what the twin uses.

**(b) Is the `ensures` complete with respect to every unchecked operation the
body performs?** The body performs exactly ONE unchecked operation — a read of
one element — and returns it. `r == v@[i as int]` names that element and its
value, and `v: &Vec<u8>` is immutable so nothing can be modified. The x4 gap is
the same as `buf_get_unchecked`'s and is closed by the same two things: a
one-expression body printed in every verdict, and Miri.

⚠⚠ **AND THIS IS THE ITEM THAT CARRIES p25's WHOLE R5 OBLIGATION**, so it is
worth saying what the gate does *for* it rather than only what it cannot judge:
`controls/proof_mutants.py`'s ATTACK arm deletes `have ==> curi < toks@.len()`
from the loop invariant and Verus fails with **`precondition not satisfied`** —
i.e. it is THIS item's `requires` that rejects the mutant, and the mutant is the
one that turns R5 back into R1. The `requires` is not decoration; it is the only
thing standing between the shipped rung and `c/kernel.c`'s read.

**(c) Does each clause mean the same in both configurations?** `v@` for a `Vec`
is `vstd::std_specs::vec`'s view and `v@.len()` is `spec_vec_len(v)` in both,
tied together by the `group_vec_axioms` this file `broadcast use`s; neither is
`#[cfg]`-dependent, and `slb_twin` occurs nowhere but on the twin's own
attribute.

## 10. What this row does NOT establish

* **Not** that `realloc` generally moves. It moves at `16 → 32` in this topology
  and nowhere else in any shipped window (`README.md`), and the adversarial
  inputs are tuned to that growth.
* **Not** that `E0502` says anything about interior pointers. The negative
  control prints it too (`README.md`); the safe-Rust result is that the port
  which *does* compile has **no bug**.
* **Not** that the shipped R1h is a correct C program under the abstract
  machine. It is memory-safe under every allocator that relocates, and DR 400
  still reaches its true branch (§3b). The unconditional re-derive is the rung
  that is clean, and it is priced.
* **Not** a claim about the minimum cost of either repair: no spelling was
  searched on either side (§3c).
* **Not** a claim that `Vec::push` and the C growth policy are the same program:
  they accept the same pushes and make a different number of allocator calls
  (§5a).
