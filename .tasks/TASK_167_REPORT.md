# TASK_167 — review of `TASK_166` and of the manager's `SYNTHESIS.md` fold (`7b5822a`)

**Role: research reviewer. I changed nothing.** No `git add`, no `git commit`, no
edit to any tracked file, no edit to any earlier `.temp/t*/` or `.temp/mgr*/`.
Scratch is `.temp/t167/` only; `.temp/mgr164/p28{u,v}.txt`, `.temp/t166/p{25,34,36}.*`,
`.temp/t166/oblig33{,_live}/`, `.temp/t166/t129rerun/` and `.temp/t166/t131rerun/`
were **copied out** before being used.

**No sweep, no re-measure, no re-emit was needed and none was started.**

---

## Did

| path | what |
|---|---|
| `.temp/t167/family.py` / `.out` | the attack on §2's named sentence — ARM B/C split by `composition.py`'s own axis, medians, non-overstatement rates, exact permutation test |
| `.temp/t167/ctlarm.py` / `.out` | a **third** independent implementation of §7's control arm (166/85/0), both reduction methods, both corpora |
| `.temp/t167/norel28.py`, `norel_p{25,34,36}.py`, `norel_all.out` | independent re-classification of all four available `norel` pairs |
| `.temp/t167/bands33.out`, `bands_subset.out`, `bandsweep.out` | the band table re-run, plus a finer threshold sweep the published justification does not survive |
| `.temp/t167/anticorr2.out` | the `anti-correlated` claim, quantified |
| `.temp/t167/result3.out`, `result3b.out` | §4's *"the one Result the out-of-sample rows made STRONGER"*, tested against a range-extension control |
| `.temp/t167/t129rerun/`, `t131rerun/` | `0 of 464` in 40 functions re-derived from a fresh `git HEAD` extraction, and `p = 0.0123` with the 26-row control |
| `.temp/t167/census.txt`, `oblig33.out`, `fold.diff`, `mem.diff` | supporting runs |

---

## Verdicts, per item

| item | verdict |
|---|---|
| §1 `28 exact / 5 norel`, `30 PASS + 3 PWBR`, `66 examined / 0 STALE`, `10 048`-line gate | **SURVIVES** — all four re-derived |
| §1/§2 the `15% → 30%` framing | **SURVIVES** — lumping `UNDEC` does not change it |
| §2 buckets `9/4/10`, `p32` sole entrant, median `6.75×`, `3 → 4` | **SURVIVES** — all re-derived |
| **§2 *"R2-is-dearer-than-R3 is a bounds-check-family property…"*** | ⚠⚠ **FALLS** — MAJOR 1 |
| §3 `216` sanitizer / `18` Miri cells, *"the exact inverse of p34"* | **SURVIVES** — checked against the records |
| §3 the four-row temporal table and the repair-site list | ⚠ **FALLS as written** — MAJOR 5 |
| §4 `0.920` / `0.805`, `152` items / `333` lines / `10 global` | **SURVIVES** — independently re-derived |
| §4 *"twelve probes … all `error[E0080]`"* | ⚠ **FALLS** — MAJOR 8 |
| §4 *"the one Result the out-of-sample rows made STRONGER"* | ⚠⚠ **FALLS** — MAJOR 2 |
| §5 the type-law scope note | **SURVIVES** — not softened, not strengthened; corroborated by a third instrument |
| §6 trap 1 *"Five" → "SEVEN"* | **SURVIVES, NARROWED** — the count is right, the enumeration is still one short (minor 4) |
| §7 `166/85/0`, the `83` paragraph | **SURVIVES** — third implementation reproduces every figure |
| §7 `0 of 464` in 40 functions, `p = 0.0123` | **SURVIVES** — re-derived, and the 26-row control reproduces `0.0612` exactly |
| §7 temporal `FIVE → SIX` | ⚠ **FALLS as landed** — MAJOR 6 |
| §7 the search-state paragraph | **SURVIVES**, with a broken sentence around it (minor 1) |
| **THE TITLE** *"What 33 kernels say"* | **SURVIVES, NARROWED** — see below |
| `.memory/` `norel` is a link-address property | **SURVIVES** — `2`, not `64`; OPEN mark still needed but should read *four of five* |
| `.memory/` the null is ANTI-correlated | **SURVIVES, NARROWED** — MAJOR 7 |
| `.memory/` the band re-scoring table | **SURVIVES** — reproduces exactly, all three populations |
| `.memory/`+RECAP `2.00 minimises misses` | ⚠⚠ **FALLS** — MAJOR 4 |
| finding 64's ✅/⊘ marks | one unearned ✅ (MAJOR 4), one ambiguous (minor 8) |
| `TASK_166` judgement call 1 (⊘ NO SEARCH) | **settled below — count them `declared`; the landed shape is right** |
| `TASK_166` judgement call 2 (`p ≈ 0.0123`) | **settled — reviewed and reproduced** |
| `TASK_166` judgement call 3 (`global` column) | **settled — this is what option B meant** |
| `p49` / §5, and the `13 449` fuzz half | **neither is load-bearing for a published number**; one gap in §0's table |
| **Is `SYNTHESIS.md` FINISHED?** | ⚠ **No** — five 26-scoped claims survive unmarked; listed at the end |

---

## The two editorial calls I was asked to rule on

### THE TITLE — *"What 26 kernels say"* → *"What 33 kernels say"*: **SURVIVES, NARROWED.**

**It is honest, and the manager's stated reason is the right one.** The tree has
been 33 since `b525e0b`; the title moved only when the *analysis* did. The new
note at `results/SYNTHESIS.md:12-13` — *"The title changed because the analysed
set did — not because the corpus grew"* — is literally true: the corpus grew 58
tasks before the title did.

**The narrowing.** The fold **deleted the one sentence that told a reader what
the number refers to** — the old §0 carried *"Where this document says '26
kernels' it means the analysed set, and that is the honest scope; the tree has
33."* The replacement asserts the referent changed but never states what the new
referent **is**, and the answer is not uniform: §1, §4, §6 and §7 are at 33; §2's
own licence rule prices **23**; its median arm is **18** rows; §5's law is one
row. §2's structural caveat now opens §2 in bold, which carries the honest
scope where it matters most — so the title stands. ⚠ **But five 26-scoped claims
elsewhere in the file are now read at 33 by default** (see *Is it finished?*),
and those are the concrete cost of dropping the referent sentence.

### The `15% → 30%` framing (`results/SYNTHESIS.md:149`): **SURVIVES. Lumping does not change the sentence.**

The premise in the task file is wrong on its face: `p42` is `NOT-LIC`, not
`UNDEC`; the two `UNDEC` rows are **`p35` and `p36`**.

```
--- 26 (the analysed set of the original doc): n=26
    LICENSED 22   NOT-LIC  3 p11 p27 p42   UNDEC  1 p36
    unlicensed (NOT-LIC + UNDEC) = 4/26 = 15.4%
    strict NOT-LIC only          = 3/26 = 11.5%
--- 33 (today): n=33
    LICENSED 23   NOT-LIC  8 p11 p25 p27 p28 p29 p34 p42 p49   UNDEC  2 p35 p36
    unlicensed (NOT-LIC + UNDEC) = 10/33 = 30.3%
    strict NOT-LIC only          = 8/33 = 24.2%
```

**Both ends of the published comparison already lump**: `p36` was `UNDEC` and was
inside the original *"four of 26"*. So the comparison **is** like-for-like, and
un-lumping makes it very slightly *stronger* (11.5% → 24.2%, a factor of 2.10,
against the lumped 15.4% → 30.3%, a factor of 1.97). **No change needed.**

---

## Problems

### MAJOR 1 — `results/SYNTHESIS.md:275-276`. **The sentence the manager asked to have attacked is FALSE, and it is refuted by the two sentences immediately above it.**

> ✅ **R2-is-dearer-than-R3 is a bounds-check-family property, and the row that
> weakened it came from outside that family.**

`SYNTHESIS.md:1056-1057` defines the bounds-check family as *"fourteen of its
patterns carry an `index >= len` axis"*, i.e. `composition.py`'s `spatial` class.
The 18-row ARM B population — the population the sentence is about — splits
**exactly nine inside, nine outside**:

```
=== ARM B (shipped, n=18) ===
  bounds-check family (composition `spatial`):  9 rows p09 p14 p23 p07 p05 p03 p02 p16 p17
  outside the family                         :  9 rows p47(side-channel) p32(temporal) p06(logical)
                                                       p01(calibration) p19(logical) p38(type)
                                                       p22(non-termination) p04(logical) p08(aliasing)
  median ratio INSIDE  =     7.26
  median ratio OUTSIDE =     6.24
  NOT-overstatements (ratio < 1.00) INSIDE the family : 2/9  p09(0.74) p14(0.86)
  NOT-overstatements (ratio < 1.00) OUTSIDE           : 2/9  p47(-1.37) p32(0.83)
  the 5 LARGEST ratios : p08=aliasing p04=logical p22=non-termination p17=spatial p16=spatial

ARM B Mann-Whitney U (inside vs outside) = 35.0 of 81; exact two-sided permutation p = 0.666  (n=48620 splits)
```

**Three independent ways it fails:**

1. **The counterexample rate is IDENTICAL inside and outside** — 2 of 9 both
   ways. The property is not a family property; it holds and fails at the same
   rate on both sides of the line.
2. **Two of the four non-overstatements are INSIDE the family** — `p09` at
   `0.74×` and `p14` at `0.86×`, both `spatial`, **and both were already in the
   26-pattern corpus**. So the property was weakened from inside the family
   before `p32` existed, and the sentence four lines above says so by name.
3. **The strongest evidence FOR the property comes from outside it.** The two
   largest ratios in the whole table are `p08` (3536×, `aliasing`) and `p04`
   (3323×, `logical`), and the same paragraph names `p08` as the exemplar — *"a
   `memmove` idiom R2's indexing defeats"*. Medians 7.26 vs 6.24; exact
   permutation `p = 0.666`.

Clause 2 (*"the row that weakened it came from outside that family"*) is true of
`p32` and misleading as written: `p47` at **−1.37×** — the range endpoint the same
paragraph quotes, and the most extreme non-overstatement in the table — is also
outside the family and has been since 26.

⚠ **The premise it rests on is also wrong.** `SYNTHESIS.md:225` calls the
distribution *"assembled almost entirely from the bounds-check family"*. It is
**6 of 10** in the `>100` bucket and **13 of 23** across the licensed set:

```
the 23 LICENSED rows: 13/23 spatial = 57%  non-spatial: p01(calibration) p04(logical) p06(logical)
                                            p08(aliasing) p18(ub-not-mem) p19(logical)
                                            p22(non-termination) p32(temporal) p38(type) p47(side-channel)
the >100 bucket: 6/10 spatial = 60%  non-spatial: p06(logical) p19(logical) p32(temporal) p47(side-channel)
```

**Failure scenario:** a reader quotes *"R2-is-dearer-than-R3 is a bounds-check-family
property"* as a scope limit on Result 1 and concludes the R2/R3 gap does not
generalise off the bounds-check family. The measured answer is the opposite —
the two largest gaps in the corpus are `aliasing` and `logical` rows.

**What survives, and it is the sentence worth having:** the four non-overstatements
are `p47` side-channel, `p09` spatial, `p32` temporal, `p14` spatial — **four rows
on four different axes**, which is a stronger and true statement about why the
median must be quoted rather than any row.

### MAJOR 2 — `results/SYNTHESIS.md:973-974`. ***"This is the one Result the out-of-sample rows made STRONGER"* is a range-extension artefact. The seven new rows are the WORST-fitting rows in the corpus, on both quantities.**

Pearson `r` rises when a sample's range is extended even if the new points carry
no information. The seven new rows more than doubled the obligation range
(`7..21 → 7..34`). Control: place the seven **exactly on the 26-row regression
line** and re-compute.

```
SYNTACTIC SIZE (units).  26-row fit: units = -1.80 + 0.81*oblig, resid sd = 1.59
  r(26) = 0.8938   r(33) = 0.9202
   p25  oblig= 10  units=  6  pred=   6.3  resid=  -0.3 (-0.18 sd)
   p28  oblig= 23  units= 17  pred=  16.8  resid=  +0.2 (+0.13 sd)
   p29  oblig= 25  units= 18  pred=  18.4  resid=  -0.4 (-0.25 sd)
   p32  oblig= 15  units=  8  pred=  10.3  resid=  -2.3 (-1.46 sd)
   p34  oblig= 24  units= 20  pred=  17.6  resid=  +2.4 (+1.52 sd)
   p35  oblig= 16  units=  9  pred=  11.1  resid=  -2.1 (-1.34 sd)
   p49  oblig= 34  units= 20  pred=  25.7  resid=  -5.7 (-3.58 sd)
  mean |resid|: new 1.92   old 1.27
  CONTROL (new rows exactly on the 26-row line): r = 0.9570
```

```
26-row fit (LINES): lines = 116.7 + 33.1 * obligations   resid sd = 98.6
  r(26) = 0.7953   r(33) = 0.8051
   p25 resid  +133 (+1.35 sd)   p28 resid  +832 (+8.43 sd)   p29 resid +551 (+5.58 sd)
   p32 resid   +28 (+0.29 sd)   p34 resid  +273 (+2.77 sd)   p35 resid +142 (+1.44 sd)
   p49 resid  -113 (-1.14 sd)
  mean |resid| of the 7 new rows  = 296
  mean |resid| of the 26 old rows = 69
  CONTROL -- 7 new rows placed EXACTLY on the 26-row line: r = 0.9083
```

**On both quantities the correlation is LOWER than a perfect out-of-sample fit
would have produced** (0.920 vs 0.957; 0.805 vs 0.908), and the new rows' mean
absolute residual is **1.5× worse on units and 4.3× worse on lines**. `p28` is
predicted at 877 lines and is 1709 — an **8.4 sd** miss. `p49` misses the units
model by **3.6 sd**.

⚠ **This is exactly the failure §6 trap 2 of this same file warns about** —
*"Your out-of-sample test is probably fake, in one of two ways"* — applied to
every Result except its own §4.

**Failure scenario:** a reader takes *"the out-of-sample rows made it STRONGER"*
as evidence that `obligations` predicts proof size on new patterns. The measured
answer is that on the seven newest rows the 26-row model is off by 133–832 lines,
and the coefficient rose only because the x-range doubled.

**What survives:** the *claim* — `obligations` is a size proxy — survives at 33
(`0.920` / `0.805` both re-derived, two parsers, 26-row controls reproduce
`0.894` / `0.795` exactly). **What must go is the causal reading of the rise.**
Honest wording: *"r rises to 0.920, and it rises because the seven new rows more
than doubled the obligation range; they are the worst-fitting rows in the corpus
and a perfect out-of-sample fit would have given 0.957."*

### MAJOR 3 — `results/SYNTHESIS.md:1369-1370`. **The control arm's load-bearing HEADLINE still says 26 while the code block three lines below it says 33.** PROTOCOL rule 13, exactly.

```
1370:PLAINLY: ACROSS ALL 26 PATTERNS AND EVERY ADVERSARIAL INPUT, THE FOUR RUST RUNGS
1371:HAVE NEVER ONCE DISAGREED WITH EACH OTHER.
...
1374:166  adversarial (pattern, input) pairs in results/gate/*.json   (129 at 26)
1375: 85  with ANY cell divergence                                     ( 58 at 26)
1376:  0  where safe_naive / safe_tuned / unsafe / verus differ from one another
```

The fold updated the block, added a whole new paragraph about the committed
instrument's `83`, and left the bold sentence a reader actually quotes at **26**.
§0's own verdict table says this Result *"SURVIVES — `129/58/0 → 166/85/0`"*.

I re-derived it with a **third** implementation (`.temp/t167/ctlarm.py`), sharing
no code with `.temp/t124/A/rung_split_census.py` or the manager's `rederive.py`:

```
all 33       pairs= 166  ANY-div SET= 85  ANY-div LAST= 83  rust-split SET=0  LAST=0
the OLD 26   pairs= 129  ANY-div SET= 58  ANY-div LAST= 56  rust-split SET=0  LAST=0

pairs where SET says diverge and LAST says not:
    p38 adversarial-huge.bin   values: [(-11, 11, ''), (0, None, '15963742333423663363')]
    p38 adversarial-oob.bin    values: [(0, None, '1000260849001108955'), (0, None, '3166752867558344246'), (0, None, '8516071857945885891')]
```

Every figure in the fold's paragraph is correct, including which two rows the
committed instrument drops. **Only the headline is wrong, and it is the sentence
this document says took 124 tasks to earn.**

### MAJOR 4 — `.memory/03-measurement.md` and `RECAP.md` finding 64. **The REPLACEMENT justification for `FLOOR = 2.00` is false in the same shape as the one it retracts — and it is marked ✅ manager-re-derived.**

`.memory/03-measurement.md` (new section) and RECAP finding 64:

> ✅ **Both constants SURVIVE, on a different argument.** `FLOOR = 2.00`
> **minimises misses and has the fewest false alarms among thresholds that do**
> (`1.50 → 5/24`, `2.00 → 5/23`, `2.50 → 7/20`); only `≤ 0.10` catches `p34`, at
> **98** false alarms.

`2.00` does **not** minimise misses. Finer sweep over the same 264 scored rows
(`.temp/t167/bandsweep.out`):

```
     th  hit miss   FA
  0.001  155    4  105
  0.005  156    4  104
  0.010  156    4  104
  0.050  160    4  100     <- FOUR misses
  0.100  161    5   98
  1.500  235    5   24
  2.000  236    5   23     <- current FLOOR, FIVE misses
  2.500  237    7   20
```

**Four misses are achievable; `2.00` gives five.** The retracted claim was
*"`2.00` is the only threshold at which it misses nothing"*; the replacement is
*"`2.00` minimises misses"*, and **both are false against the same records**.
The disconfirming sweep is in `TASK_166_REPORT.md:167-169` — *"finer sweep:
`0.01 → 4 misses`"* — **two lines below the headline the manager copied**. That is
rule 9's original cause verbatim, and `RECAP.md` finding 64 carries a **✅** on it.

The two false alarms the sentence needs are already in the text; the honest form
is available and costs one clause:

> `FLOOR = 2.00` minimises misses **among thresholds that keep the false-alarm
> rate under 24** (`1.50 → 5/24`, `2.00 → 5/23`, `2.50 → 7/20`). No threshold can
> catch `p03`/`p04`; the only extra catch available is `p34`'s `+0.0065`, and
> buying it needs `≤ 0.05`, at **100** false alarms against 23.

⚠ The `only ≤ 0.10` in the current text is also off by one bucket: at `0.100` the
miss count is still 5; the transition is between `0.050` and `0.100`.

✅ **Everything else in the band section reproduces exactly**, all three
populations, all three thresholds, including the published 22-row row that does
not reproduce (`.temp/t167/bands_subset.out`, `bands33.out`) — so the
*engineer's* scoring table survives a full independent re-run and needs nothing.

### MAJOR 5 — `results/SYNTHESIS.md:619-644`. **§3 promises six rows, shows a four-row table containing a non-member, and then enumerates a different six. `p25` is missing from both.**

Line 619-622: *"IT NOW HAS SIX ROWS UNDER IT AND THEY DO NOT ALL SAY THE SAME
THING… The temporal axis went from **one row to six** (`p25 p27 p28 p29 p32 p34`)"*.

The table that follows has **four** rows: `p32`, `p28`, `p34`, and **`p35`** —
which the table's own cell labels *"(tagged union, `type` axis)"*. `composition.py`
puts `p35` under `type`, not `temporal`. So:

* three of the six named rows (`p25`, `p27`, `p29`) are **absent**, and a reader
  told the six *disagree* is shown half of them;
* a `type` row is inside a table whose header sentence says *"six rows under
  [the temporal rule]"*.

Line 640-644, the repair-site sentence, is worse:

> ⚠ **And the axis that separates the six is the REPAIR SITE, not the bug class:**
> `p27`/`p29`/`p32` fix the **READ**, `p28` the **DESTROY**, `p34` the
> **ACQUIRE** …, and `p49` the **WRITE-THROUGH**.

That enumerates six names — `p27 p29 p32 p28 p34 p49` — but **the six are
`p25 p27 p28 p29 p32 p34`**. `p49` is `aliasing` (composition), not temporal, and
**`p25` has been silently dropped**.

**Where `p25`'s repair site goes, measured, from its own `NOTES.md:277-299`:**

> `### 3c. ⚠⚠ THREE REPAIR SITES — AND THE ORDERING BETWEEN THE TWO
> STANDARD-CLEAN ONES REVERSES BETWEEN OPTIMISATION LEVELS`
> **The three sites.** `R1h` guards the READ; `rederive` replaces the READ;
> `fixup` and `fixup2` refresh `cur` at the **GROWTH** and leave the READ as R1
> writes it.

So `p25` is **the row that breaks the sentence's own shape**: it has repairs at
**two** sites (READ *and* GROWTH), three spellings, and the ordering between the
two standard-clean ones **reverses between `-O0` and `-O3`**. It is the single
most informative row for a claim that *"the axis that separates the six is the
repair site"*, and it is the one row the list omits. **The list is therefore
incomplete and, as written, wrong about its own membership.**

**Failure scenario:** a reader builds a taxonomy from the four named sites and
concludes each temporal row has exactly one repair site. `p25` has two, and
they trade places between optimisation levels.

### MAJOR 6 — `results/SYNTHESIS.md:1519-1546`. **The fold updated the paragraph's header FIVE → SIX and left the body saying FIVE three times — in the paragraph whose stated purpose was to fix a five/six disagreement.**

```
1519:✅ **The temporal axis has improved most of all — from ONE row to SIX:**
1523:⚠ **This paragraph said FIVE while the composition table three paragraphs above
1524:it said SIX — the same file disagreeing with itself one section apart, and
1527:only `p29`.** **The five are not the same shape**, and the differences are the
1534:⚠⚠ **And the safe-Rust answers DISAGREE ACROSS THE FIVE, which is the sharpest
1543:guarantee is a guarantee about the allocator"* now has five rows under it rather
```

The file no longer disagrees with itself one section apart. It disagrees with
itself **four times inside one paragraph**, and the paragraph's own diagnostic
sentence (1523-1524) is what makes it read as settled. This is PROTOCOL rule 13
in its purest form and it was introduced by the commit that quotes rule 13's
lesson.

### MAJOR 7 — `.memory/03-measurement.md`, the anti-correlation block. **The table's call-volume column is `small.bin` under a header that says `large.bin`, one cell is a cross-pattern mashup, and `ANTI-correlated` over-claims what the data shows.**

The landed table:

```
-O3 isolated, large.bin     outward calls per kernel call     R5-R4 null
  p28                                   ~28..144                   +1.01
  p29                                   ~32                        -0.02
  p34                                   ~30                        -0.10
```

Measured (`TASK_166_REPORT.md:47-49`, and re-derived by me from
`synthesis/outward_ir.json`), `outward_calls_per_kernel_call` small/large:

```
p28  27.966 / 107.562      p29  31.599 / 95.871      p34  30.044 / 144.253
```

* `p29`'s *"~32"* is its **small** figure; its null `−0.02` is **large**.
* `p34`'s *"~30"* is its **small** figure; its null `−0.10` is **large**.
* `p28`'s *"~28..144"* is `p28`'s **small** figure and **`p34`'s large** figure
  joined into a range that belongs to no pattern.

The whole point of the entry is a relation between two columns, and one column is
from the wrong blob. It also **understates the counterexample**: `p34`'s real
large-blob call volume is `144.253`, the largest in the tree after `p36`, with a
null of `−0.10`. And `p36` — which the commit message calls *"the single best
counterexample"* (1024 calls, null exactly `0.00`) — **is not in the table at all**.

**On the word.** Using the same null the entry means (`synthesize.py::r5_null`,
`-O3 isolated`, per input):

```
large only n=33: pearson(calls,|null|)=-0.052  spearman=-0.268
     drop p25: pearson=-0.091  spearman=-0.316 n=32
both blobs n=66: pearson(calls,|null|)=-0.030  spearman=-0.404
     drop p25: pearson=-0.074  spearman=-0.432 n=64
```

Pearson is **−0.05**, indistinguishable from zero. The rank statistic is weakly
negative but is carried by a mass of exact-zero ties. ⚠ Dropping `p25`
*strengthens* the direction slightly, so **the outlier objection in the task file
does not land** — that is a clean negative. But *"ANTI-correlated"*, in caps in
the section title, asserts a direction `r = −0.05` cannot carry.

The entry's **own closing sentence is the correct statement** and should be
promoted to the header: *"So 'does this kernel call out?' is NOT a screen for
whether the null matters. Read the cell."* — supported decisively by `p36` at
1024 calls / null `0.00` and `p25` at 7 calls / null `+269.52`. Rule 13 again:
the header over-claims relative to its own body.

### MAJOR 8 — `results/SYNTHESIS.md:878-882`. ***"measured on twelve probes … all `error[E0080]`"* is false by both readings.**

Census over every probe log in `.temp/t165/globalprobe/`:

```
E0080   alias_false        E0080   align_false       no-E0080 align_true
no-E0080 cfg2_plain        no-E0080 cfg2_twin        no-E0080 cfg_plain
no-E0080 cfg_twin          E0080   generic_false     E0080   ghostonly_false
E0080   mod_host2          no-E0080 mod_host         no-E0080 outside_verus
E0080   re_layout_false_lib   E0080 re_layout_false
E0080   re_layout_false_unused   E0080 re_sizeof_false
```

**Nine of sixteen probe files produce `error[E0080]`; seven do not.**

* Read as *"twelve probes, all of which gave E0080"*: there are **nine**, not
  twelve, in the entire two-task record.
* Read as the manager's arithmetic — `TASK_164`'s 4 (`re_*`) + `TASK_165`'s
  *"8 new"* = 12, which is exactly `run.sh`'s twelve lines — then **four of those
  twelve are not E0080** (`align_true` is a *true* declaration and passes;
  `cfg_plain` / `cfg_twin` fail on macro scope; `mod_host` fails with
  *"postcondition not satisfied"*), and the set **does not contain
  `mod_host2`** — the `#[path]`-included module the sentence names as one of its
  five examples, which lives in `run2.sh`.

✅ **The five constructs the sentence names are each genuinely `E0080`** —
`re_layout_false_unused` (never-constructed), `re_layout_false_lib`
(`--crate-type=lib`), `generic_false`, `alias_false`, `mod_host2` — so the
**conclusion** (rustc const-evaluates a `global` and rejects a false one) is
sound, and **no probe shows rustc accepting a false `global`**. Only the
quantifier is wrong, and it is the load-bearing half of *"What keeps the `0`
defensible as a COUNT"*. Honest form: *"nine false spellings, every one
`error[E0080]`, including …"*.

### MAJOR 9 — `.temp/mgr164/QUEUE_TRIAGE.md`, item 12. **The ✅ *"`.memory/` is genuinely clean"* is wrong, and it was wrong at the commit it says it checked against.**

The task file says an error here is worth more than most because this file is
about to become a task. Item 12 reads:

> ✅ **`.memory/` is genuinely clean** — its one apparent hit is a *quotation of*
> a rotten citation.

Re-derived:

```
patterns/:  8 citations across 5 patterns  (p12, p13 x3, p16 x2, p35, p38)   <- item 12's own figure, CORRECT
.memory/ :  6 citations
  .memory/03-measurement.md:3146  check.py:2387
  .memory/03-measurement.md:3320  check.py:3303   <- self-annotated as historical: the one real quotation
  .memory/03-measurement.md:3364  check.py:2805
  .memory/06-catalogue.md:414     check.py:3941
  .memory/06-catalogue.md:414     check.py:4178-4180
  .memory/06-catalogue.md:842     check.py:1249   <- inside a block quote
```

At `4a24102` — the commit the item says it checked against, *before* `TASK_164`
moved anything:

```
check.py:2387  # ==========================================================================
check.py:2805      slope -- Ir at N calls minus Ir at N/2 calls, over the difference in calls --
check.py:1249  (blank)
```

`.memory/03-measurement.md:3146` says *"`check.py:2387` calls `sb(m.selfcheck)`
and `sb` propagates"* — line 2387 was a `# ====` separator then and is a selftest
case tuple now. `:3364` cites `check.py:2805` as documenting a convention; it was
a comment about slope then and is `return int(line.split()[1])` now. **At least
two of the six were already rotten when the triage declared the layer clean**, and
at least four are live citations rather than quotations.

**Failure scenario:** the bundled-sweep task is written from this triage, scopes
the `check.py:NNNN` fix to `patterns/` on the strength of the ✅, and leaves four
rotten pointers in the layer the project calls authoritative — which is the one
place the item says a fix is free (`.memory/` is not gate-hashed).

---

## Minor

1. **`results/SYNTHESIS.md:518-521` — a dangling back-reference and an arithmetic
   overshoot, both created by the fold.** The sentence now reads *"**14 of 33**
   patterns print `undeclared`, three more owe a span, and **19** report a real
   search or a reviewed declaration of no search"*, and the next clause is
   **"Of the nine:"** — whose antecedent was the `nine` the fold replaced with
   `19`. At 26 the three figures partitioned the corpus (`14 + 3 + 9 = 26`); at
   33 they read as three disjoint groups summing to **36 of 33**. The *"three
   more"* are `p01`, `p03` and `p08` (`R3 span OWED` in the generated table) and
   all three are **inside** the 19 — they are in `SEARCH_REVIEWED`. The generated
   file's own split is a clean partition: `14 + 19 = 33`, `19 = 16 + 3`.
2. **`results/SYNTHESIS.md:888` — *"All 26 verified sources carry `broadcast
   use`"*, four lines below the fold's own *"Across all **33** patterns: 152
   trusted items"*.** `results/synthesis.md:578` already publishes the correct
   figure: *"All **33** of the **33** `verus.rs` carry `broadcast use`"*.
3. **`results/SYNTHESIS.md:1057` — *"fourteen of its patterns carry an
   `index >= len` axis"*.** `composition.py` says **15** (`p02 p03 p05 p07 p09
   p10 p11 p12 p13 p14 p16 p17 p23 p36 p46`), and all 15 were already in the 26,
   so this was never 14. It is the sentence that **defines the family MAJOR 1 is
   about**, and the fold did not touch it.
4. **`results/SYNTHESIS.md:1083` — §6 trap 1 says *"**Seven** patterns"* and names
   six.** `TASK_166_REPORT.md:333-340` flagged exactly this defect at *"Five"*
   naming four. The fold changed the count and added two names, so the gap is
   unchanged at one. The missing row is **`p27`**, which `RECAP.md:30`'s standing
   trap row names second (*"p27 repeated it one pattern later — a dead store in
   R4 that R3 did not have"*) — and `p27`'s absence is why the paragraph could
   reach *"Five"* while naming four in the first place.
5. **`results/SYNTHESIS.md:149` states `norel`'s mechanism without the OPEN mark
   `.memory/` carries.** The authoritative layer says *"⚠ **MECHANISM PARTLY
   OPEN** … three of five, not five"*; §1's R4 row states the `p28` decomposition
   flat. The scoping to *"on `p28`'s pair"* is correct and helps, but a reader of
   §1 alone gets a settled mechanism where `.memory/` has an open one — the exact
   conclusion-vs-mechanism split PROTOCOL rule 9 was refined to prevent.
6. **`.memory/`'s *"three of five, not five"* undercounts its own evidence.**
   `TASK_166` diffed **three** (`p25`, `p34`, `p36`, dumps in `.temp/t166/`) and
   the manager did `p28` — **four of five**. Only `p29` is undiffed, and closing
   it needs a build. **Keep the OPEN mark; correct the count.**
7. **"ZERO `call` instructions differ" is true of encoded fields and false of
   printed lines.** On `p28`, **6 of 7 `call` lines are among the 71 differing
   lines** — all six are `call *0xNNNNN(%rip)` with **identical displacements** and
   different resolved GOT addresses. The sentence uses, without qualification,
   the very printed-absolute-vs-encoded-field confusion the paragraph exists to
   warn about. Say *"zero `call` instructions differ in their encoded field; six
   of seven differ in the absolute address objdump prints"*.
8. **`RECAP.md` finding 64's ✅ on the type-axis result is ambiguous.** The legend
   is *"✅ = manager re-derived"*, and the type-axis paragraph carries a ✅ —
   but `TASK_166_REPORT.md:421-445` shows it was the **engineer's** run
   (`.temp/t166/typeaxis.py`), and no manager artefact for it exists. It may be
   intended as *"the prediction HELD"* given the sentence opens *"AND THE ONE THE
   TASK FILE SAID MUST NOT BE ASSUMED HELD"*. Either way it is the exact mark
   `TASK_165` item 5 was scoped to. ✅ **The result itself is correct** — I
   corroborated it below from a third instrument.
9. **`.temp/mgr164/NOTES.md:330` — *"the big-null set ⊂ `NOT-LIC` (all five)"*
   depends on an unstated threshold.** At the project's own `FLOOR = 2.00`, `p02`
   (`|null| = 2.00`), `p03` and `p04` (`+6.00`) are big-null **and LICENSED**, so
   the subset relation fails. It holds only at `≥ 16.00`, where the set is two
   patterns, not five. Moot since `TASK_166` refuted the hypothesis the relation
   supported, but the file is cited by `SYNTHESIS.md`'s closing paragraph.
10. **The task file `TASK_167.md:45` says *"`p36` and `p42` are `UNDEC`"*.** `p42`
    is `NOT-LIC`; the second `UNDEC` row is `p35`. Manager premise stated as fact
    (PROTOCOL rule 14). It did not change my answer.

---

## `TASK_166`'s three judgement calls — settled

### 1. The three `⊘ NO SEARCH` entries: **count them `declared`. The landed shape is right. Keep `14 of 33`.**

Not a close call, for a reason that is in the artefact rather than in taste:
`undeclared`'s **published definition** is *"nobody wrote an entry"*, not
*"nobody searched"* — `results/synthesis.md:787` says so in terms, and
`SYNTHESIS.md:1430-1431` repeats it. Under that definition a reviewed
`⊘ NO SEARCH` entry **is** declared, by construction; leaving the three out
would make the column mean two different things in the same table.

Three further reasons, in order of weight:

* **The direction test.** The change moves a published count in the *flattering*
  direction (21 → 14 undeclared), which is the direction this project's own
  traps run. It survives because the split is published beside the count — *"19
  declared = 16 search results + 3 declared-no-search"* — and **both** prose
  sites carry the qualifier (`SYNTHESIS.md:519-520` and `:1426-1427`). Had either
  printed a bare `19`, I would have refused it.
* **The rows are visually distinct in the table**, not merely in a footnote:
  `p29`/`p32`/`p49` print `⊘ NO SEARCH, declared — NEITHER side searched…`,
  which no searched row can be mistaken for.
* **The alternative loses information the review process paid for.** `p32`'s
  entry names four unmeasured levers and `p49`'s says only one in-contract R3
  spelling exists — facts a reader wants and `undeclared` erases.

⚠ **One condition, and it is already met**: `14` must never be printed without
the split. It currently never is. Fix minor 1's arithmetic and this is closed.

### 2. `p ≈ 0.0123`: **SURVIVES — it is no longer the engineer's alone.** I re-derived it end to end.

Fresh extraction of all 33 kernels from `git HEAD`
(`.temp/t167/t129rerun/ladder_extract33.sh`, 131 `c/*.{c,h}` files), then the
`TASK_129` classifier (`SELFTEST PASS`) and the `TASK_131` size probe:

```
$ python3 .temp/t167/t129rerun/census.py run ... ladder33.json
{"label": "ladder33", "files": 33, "failed": 0, "functions": 50, "sites": 464, ...}
sites (non-generated): 464
operator split: {'index': 441, 'mem_call': 21, 'str_call': 1, 'cast_deref': 1}
site-carrying functions: 40  files: 33
ptr_offset: 0
```

```
                        FUNCTION unit, size-matched to cgnu
33 kernels, 40 fns:     expected walkers 4.12   P(zero) = 0.0123     (php 0.0006, coreutils 0.0149)
26 kernels, 30 fns:     expected walkers 2.66   P(zero) = 0.0612     <- reproduces the PUBLISHED value exactly
```

The 26-row control reproduces the published `0.0612` with **30** site-carrying
functions and **255** sites, so the 33-row figure comes from the same instrument.
`0 of 464` in `40` functions and `p = 0.0123` all stand.

### 3. The `global` column: **yes, the landed shape is what option B meant.**

`TASK_165_REPORT.md:150-152` specified B as *"leave the gate alone; make the
publication honest — `synthesize.py` already has `global_decls` in every gate
record, so add the column/total and rewrite the '0 axioms' sentence"*. Landed:

```
| **total** | **497** | | **152** | **333** | **0** | **10** | | |
"Trusted base, all 33 rows: 152 items (333 lines), 0 axioms and 10 `global`
 directives on 10 rows. Quote all three; there is no single one."
```

Re-derived from `results/gate/*.json`:

```
p10 global size_of usize@87   p19 size_of@63   p22 size_of@133   p28 layout Obj@162
p29 layout Rec@135   p34 layout Obj@147   p36 size_of@90   p38 size_of@80
p46 size_of@79   p47 size_of@98
patterns with >=1 global: 10   total global directives: 10
```

`verus.axioms` untouched (still `0`), no `contract_sha256` moved, no sweep. The
false gloss survives only as a quoted retraction at `SYNTHESIS.md:876`. ✅ B, exactly.

---

## The pack's two flagged gaps — are they load-bearing?

**`p49` as the second `aliasing` row, bearing on §5:** **not load-bearing for any
published number**, but it is a **gap in §0's verdict table**. §5's live subject
is *"what this instrument can and cannot price"*, and §0 gives Result 4 a
one-limb out-of-sample verdict (*"the `6.00 Ir` type law is STILL A ONE-ROW
LAW"*). At 33 the `aliasing` axis also doubled, and its second row is the tree's
cleanest instance of Result 4's own subject: correct C, every index in bounds,
nothing freed, **216 sanitizer cells and 18 Miri cells silent**, and the checksum
the only instrument. The fold put that in §3 and never connected it to §5. ⚠ Note
the fold **deleted** the sentence that used to record the axis growth (*"the TYPE
axis from one to TWO, and the ALIASING axis from one to TWO"*), so the aliasing
doubling is now stated only inside §3's `p49` paragraph. **One sentence in §0's
table closes it; nothing needs running.**

**The `13 449`-input fuzz half:** **disclosed and not load-bearing.**
`SYNTHESIS.md:1401-1402` now says plainly that it is the 26-pattern figure and
has not been re-run, while the gate-record half is `0` at 33 — which I confirmed
with a third implementation. ⚠ **But the mechanism sentence beside it is stale
in the direction that WEAKENS it**: `SYNTHESIS.md:1403-1404` says *"`requires` is
a **length** bound in **26 of 26** patterns and never mentions buffer CONTENTS"*.
Re-derived from every gate record's `derived_contract.requires`, it is **33 of
33** — 31 rows are exactly `off + len <= buf_len`, `p17` and `p42` add a range
bound, and not one mentions contents. **The document under-states its own
mechanism by seven rows, and the fix needs no run.**

---

## Is `results/SYNTHESIS.md` FINISHED?

**No.** Not *"is it current"* — there are five claims a reader would need that no
artefact backs at 33, all unmarked, in a file now titled *"What 33 kernels say"*:

1. **`:1269` — the idiom census.** *"a census of all 26 built kernels finds 14
   destination buffers, 13 `#define` capacities plus one input extent, and **ZERO
   prior-pass counts**"* (`TASK_123`). This is the **sole evidence** that the one
   surviving CVE candidate (`CVE-2021-23017`) brings a new mechanism. ⚠ **The
   fold's own commit message names the idiom census, alongside the four Results,
   as *"drawn from 26 kernels"* — and it is the only named item the fold left
   un-re-derived and unmarked.** `RECAP.md:2562` calls it *"a census of ALL built
   kernels"*, which is now false.
2. **`:1418-1420` — *"36 of the 129 adversarial inputs (27.9%) make ZERO kernel
   calls"* and *"the `adversarial-strideN.bin` template is 0-call in 22 of 26
   patterns"*.** `TASK_166_REPORT.md:524-526` explicitly owed this and did not do
   it. The `129` here is a live figure, unmarked, twelve lines after the same
   `129` is marked *"(129 at 26)"* in the code block above.
3. **`:1249` — *"8 of the 26 built patterns publish a zero on their own headline
   axis"*.** The control arm for a retracted generalisation; 26-era, unmarked.
4. **`:1057` — *"fourteen of its patterns carry an `index >= len` axis"*.** Off by
   one against `composition.py` at both 26 and 33 (it is 15). It is the
   definition MAJOR 1 turns on.
5. **`:888` — *"All 26 verified sources carry `broadcast use`"*.** The generated
   file already carries the 33 figure.

Everything else I checked is backed by a committed artefact or a re-runnable
instrument.

---

## Clean negatives — named, so nobody re-runs them (`TASK_166`'s ten not repeated)

1. **`norel` is the norm at `-O0`: `30 of 33` is RIGHT.** I got 29 and the 29 was
   my own bug — `p01` carries **two** identity pairs (`unsafe vs verus` and the
   `safe_naive_verus.rs` R2v control) and a last-wins dict overwrote the first.
   Restricted to `pair == "unsafe vs verus"`: `norel 30, exact 1 (p08),
   differ 2 (p28 p29)`. *Do not re-count without filtering on `pair`.*
2. **The band scoring table is the engineer's and it reproduces exactly** — all
   three populations × all three thresholds, including the published 22-row row
   that does **not** reproduce (`162/0/14`). *Do not re-fit.* Only the
   *justification sentence* is wrong (MAJOR 4).
3. **The oracle did not move, and by a wider test than the published one.**
   Committed 26-pattern sidecar vs today's re-emit: `0 of 208` pair rows differ,
   and `0 of 1236` numeric cell figures — a superset of the published `824`
   denominator. *Do not re-emit hoping the phase moved.*
4. **`0.805` and `0.920` re-derived, and the 26-row controls reproduce `0.795`
   and `0.894` to four digits**, with both the frozen `df14f4f` parser and
   today's `harness/vparse.py` giving identical rows. `sum obligations = 497`,
   `p49` largest at 34, `p28` longest at 1709 lines — all match. *Do not re-run.*
5. **`166 / 85 / 0` reproduced by a THIRD implementation**, sharing no code with
   the committed instrument or the manager's `rederive.py`, plus `129 / 58 / 0`
   at 26 and the committed instrument's `83 / 56` under last-run-wins; the two
   dropped rows are exactly `p38 adversarial-{huge,oob}.bin`. *The method split
   is settled; do not re-derive it a fourth time.*
6. **`norel` is a uniform link shift on `p25`, `p28`, `p34` — and NOT on `p36`.**
   Printed-absolute deltas (verus − unsafe) and rip-displacement deltas:
   ```
   p25: absolutes {-32: 33, 0: 2}   rip-disps {0: 6, 32: 2}
   p28: absolutes {-32: 69, 0: 2}   rip-disps {0: 7, 32: 2}
   p34: absolutes {-32: 31, 0: 2}   rip-disps {0: 5, 32: 2}
   p36: absolutes {272: 5, 368: 1}  rip-disps {96: 1}
   ```
   On the first three, **every** printed absolute moves by exactly `−0x20` except
   the two that did not move at all (`GCC_except_table142`), and those two are
   exactly the `lea`s whose displacement changes by `+0x20`. `p36` is a different
   arithmetic — base `+0x110`, target `+0x170`, displacement `+0x60`
   (`0x170 − 0x110 = 0x60`, consistent) — and its one real difference resolves to
   a **different** offset (`+0x168` → `+0x1a8`). ⚠ **The link-layout CONCLUSION
   holds on all four; the *"0x20 shift"* WORDING is `p25`/`p28`/`p34` only.**
   *`p29` is the only undiffed pair and needs a build.*
7. **`p28`'s `2`, not `64`, confirmed independently** — 371 instructions, 71
   differing lines, 62 same-symbol-offset, 7 same-rip-displacement, **2** real
   encoded differences, both `lea`, both to `78f0 <GCC_except_table142+0x2c>`,
   both differing by `0x20`.
8. **`p49`'s `216` + `18` and *"the exact inverse of `p34`"* both check out.**
   The 216 is `p49/controls/detectors.py` (`NOTES.md:182`, *"216 cell(s) run; 0
   carried a diagnostic"*) and the 18 is gate stage 8 plus `controls/rust_bug.py`.
   From the records: `p34`'s `adversarial-blind{,read}` **plain-build** cells are
   `diverges=False` on all eight rungs while ASan fires; `p49`'s five adversarial
   inputs are `diverges=True` on `c-gcc` and `c-clang` with **no** detector
   firing anywhere. The 2×2 really is inverted.
9. **§5's type-law scope note is corroborated by a THIRD instrument.** Neither
   the engineer's binary run nor a citation — the committed gate records'
   `adversarial` section:
   ```
   p38: c-gcc only, O3/isolated + O3/whole only, 3 inputs   (never c-clang, never O0)
   p35: c-gcc AND c-clang, O0 AND O3, all four inputs
   ```
   `1 of 4` vs `4 of 4`, exactly as published. *Not softened, not strengthened.*
10. **The kernel `requires` is a length bound in 33 of 33 and never mentions
    contents** — 31 rows are `off + len <= buf_len` verbatim; `p17` adds
    `buf_len <= i64::MAX`, `p42` adds `1 <= len <= i64::MAX`. The doc's *"26 of
    26"* is stale in the direction that weakens it.
11. **The two new `RECAP` queue citations do not dangle.** `SYNTHESIS.md:1333`
    and `:1437` cite queue items **36** and **35**; both exist (the Immediate
    queue is 36 items). ⚠ `QUEUE_TRIAGE.md`'s *"31 numbered items"* is stale.
12. **The three checks the fold's commit message claims all rc=0**, re-run:
    `composition.py --evidence` rc=0, `temp_citations.py` rc=0,
    `measure.py --check-stale` rc=0 with `66 record(s) examined, 0 STALE`.
    PROTOCOL rule 10's dangling-report check is clean apart from the documented
    `TASK_NNN` placeholders and this report.
13. **`6f5674f`'s commit message is right where `.memory/` is wrong.** Its
    anti-correlation figures — *"p36 at 1024 calls/kernel-call, p34 144, p28 108,
    p27 96, p29 96, p13 48 … all have nulls inside [−1.00, +1.01]"* and *"the five
    biggest nulls (p25 269.52, p42 −31.00, p03 +6.00, p04 +6.00, p02 −2.00) have
    1 to 7 calls"* — reproduce **exactly**, on the correct blob. The commit
    message is the artefact to copy the `.memory/` table from (MAJOR 7).
14. **`.temp/mgr164/NOTES.md:327` did land the `TASK_165` correction** — the
    superseded input-maxed nulls are marked `SUPERSEDED` with per-cell
    replacements and a *"never a single number"* instruction.
15. **The `p29`/`p32`/`p49` `⊘` rows do not contradict their own table row.** I
    checked: `p29`'s *"publishes no rung-to-rung cost at all"* sits beside a bold
    `+220.35 / +1190.87`, but that column is `corrected (derived)` — the callee
    correction — not a search spread. No defect.

---

## Unsure / not done

1. **`p29`'s `norel` pair is the one I could not close.** No disassembly dump
   exists for it and producing one is a build. The mechanism should stay marked
   **OPEN**, with the count corrected to *four of five* (minor 6).
2. **I did not re-derive the idiom census at 33** (`14 destination buffers /
   13 `#define` / 0 prior-pass counts`). It is a judgement-carrying
   classification, not a grep, and it was out of scope. I report it as unmarked
   26-scoped, not as wrong.
3. **I did not re-run the `13 449`-input fuzz corpus**, and nothing here needs it.
4. **MAJOR 2's control is a regression-residual argument, not a significance
   test.** I did not compute a confidence interval on `r`; with n = 26/33 it
   would be wide either way. The finding rests on the residuals and the
   place-them-on-the-line control, both of which are deterministic.
5. **My `1236` cell-figure denominator for *"the oracle did not move"* is not the
   published `824`** — I counted every numeric key rather than the published
   subset. The direction is the same (zero moved) and strictly stronger; I did
   not chase which subset gives 824.
6. **The `.temp/t165` probe classification is from the committed `.log` files**,
   not a re-run of Verus. The logs are unambiguous (`error[E0080]` present or
   absent) and I did not re-invoke `verus_run.py`.
7. **I did not audit the 14 old `undeclared` rows** — `RECAP` queue item 35, and
   out of scope here.
8. **`RECAP` finding 64's ✅ on the type-axis paragraph (minor 8) may be a
   legend collision rather than an unearned mark.** I could not distinguish
   *"manager re-derived"* from *"the prediction held"* from the text; the
   underlying result is correct either way.

## Memory updates

**None written — reviewers do not fix and subagents may not touch `.memory/`.**
What the manager should land, in priority order:

| file | what |
|---|---|
| `results/SYNTHESIS.md:275-276` | ⚠⚠ **MAJOR 1 — delete or replace the bounds-check-family sentence.** 2/9 inside, 2/9 outside; medians 7.26 vs 6.24; exact permutation `p = 0.666`. The true and stronger sentence: the four non-overstatements sit on **four different axes** (`p47` side-channel, `p09` spatial, `p32` temporal, `p14` spatial). Fix `:225`'s *"almost entirely"* (6/10 and 13/23) in the same pass. |
| `results/SYNTHESIS.md:973-974` | ⚠⚠ **MAJOR 2 — the *"made STRONGER"* claim is range extension.** The seven new rows are the worst-fitting in the corpus (mean \|resid\| 1.5× on units, 4.3× on lines; `p28` +8.4 sd, `p49` −3.6 sd) and a perfect out-of-sample fit would have given `0.957`/`0.908` against the measured `0.920`/`0.805`. Keep the correlations; drop the causal reading. |
| `results/SYNTHESIS.md:1370` | ⚠⚠ **MAJOR 3 — `ACROSS ALL 26 PATTERNS` → `33`.** Its own code block, three lines below, is at 33. |
| `.memory/03-measurement.md` + `RECAP.md` finding 64 | ⚠⚠ **MAJOR 4 — *"`2.00` minimises misses"* is FALSE** (`0.05 → 4` misses) and carries a **✅**. Replacement wording is in the body above. |
| `results/SYNTHESIS.md:619-644` | ⚠ **MAJOR 5 — §3's table shows 4 of a promised 6 plus a `type` row, and the repair-site list swaps `p49` (aliasing) in for `p25` (temporal).** `p25`'s repair sites are the **READ** *and* the **GROWTH** (`p25/NOTES.md:294-299`), three spellings, ordering reversing between levels — the row the sentence most needs. |
| `results/SYNTHESIS.md:1527,1534,1543` | ⚠ **MAJOR 6 — three surviving `FIVE`s under a header the fold moved to `SIX`.** |
| `.memory/03-measurement.md` (anti-correlation) | ⚠ **MAJOR 7 — the call-volume column is `small.bin` under a `large.bin` header** (`p29` 31.599→95.871, `p34` 30.044→144.253, `p28`'s `~28..144` is two patterns joined). Add `p36` (1024 calls, null `0.00`). Retitle to the entry's own closing sentence: **call volume does not predict the null** — Pearson is `−0.05`. Copy the figures from `6f5674f`'s commit message, which has them right. |
| `results/SYNTHESIS.md:878-882` | ⚠ **MAJOR 8 — *"twelve probes … all `error[E0080]`"* → *"nine false spellings, every one `error[E0080]`"*.** Measured 9 of 16; the five named constructs are each genuinely `E0080`. |
| `.temp/mgr164/QUEUE_TRIAGE.md` item 12 | ⚠ **MAJOR 9 — the ✅ *"`.memory/` is genuinely clean"* is wrong and was wrong at `4a24102`.** Six citations; `:2387` and `:2805` were already rotten. Scope the bundled sweep to `.memory/` too — it is not gate-hashed, so it is the cheapest half. |
| `results/SYNTHESIS.md:518-521` | minor 1 — `Of the nine:` has no antecedent, and `14 + 3 + 19 = 36` on a corpus of 33. The `three more` (`p01 p03 p08`) are inside the 19. |
| `results/SYNTHESIS.md:888, 1057, 1083, 1249, 1269, 1403, 1418-1420` | minors 2–4 and the *finished?* list — the stale-26 sweep the fold did not finish. `:1403`'s *"26 of 26"* is **33 of 33**, measured, and strengthens the claim. |
| `results/SYNTHESIS.md:149` and §0's table | minor 5 / the `p49` gap — carry `.memory/`'s **OPEN** mark onto §1's `norel` sentence; add one line to §0's Result 4 row for the `aliasing` axis doubling. |
| `.memory/03-measurement.md` (`norel`) | minor 6/7 — *"three of five"* → **four of five**; *"ZERO `call` instructions differ"* → *"zero differ in their **encoded field**; six of seven differ in the printed absolute"*. |

**PROTOCOL rule 2 running count: launched from 933 → 942.** Nine manager claims
refuted or narrowed by measurement: (1) the bounds-check-family sentence, on
three independent tests; (2) *"the one Result the out-of-sample rows made
STRONGER"*, against a range-extension control; (3) *"ACROSS ALL 26 PATTERNS"* in
§7's control-arm headline; (4) *"`2.00` minimises misses"*, marked ✅, false at
`0.05`; (5) §3's *"six rows"* delivered as four plus a non-member, and the
repair-site list's substitution of `p49` for `p25`; (6) §7's temporal paragraph,
header `SIX` over body `FIVE` ×3; (7) the anti-correlation table's blob mislabel
and the word *"ANTI-correlated"*; (8) *"twelve probes … all `error[E0080]`"* —
nine of sixteen; (9) `QUEUE_TRIAGE.md`'s ✅ *"`.memory/` is genuinely clean"*.
⚠ Reconciliation across branches is the manager's job, not mine.
