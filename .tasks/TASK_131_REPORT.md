# TASK_131 — REVIEW of TASK_129 / RECAP finding 45. The zero SURVIVES; two of the sentences around it do not.

**Reviewer report. Everything below was run.** Scripts, outputs and a `REBUILD.sh`
are in `.temp/t131/`; notes in `.temp/t131/NOTES.md`. **I wrote nothing outside
`.temp/t131/` and this file.** I did not run `check.py`, `build.py`,
`measure.py` or `report.py` — I *imported* `check.py::spelling_matches`, as
`TASK_101` did. Nothing under `.temp/t129/` was modified (`orig_t129_sha256.txt`
is the pre-rerun snapshot; the rerun ran in a copy).

---

## VERDICT, in one paragraph

**§A: `ptr_offset = 0` is NOT a harness artefact of the kernel signature, and I
can name the measurement that kills the objection** — in real C, functions that
receive a pointer *and* an explicit length walk with a cursor at the same rate as
functions that do not (cgnu 9.2 % vs 9.8 %) or a *higher* rate (php 22.4 % vs
15.6 %). ✅ **The manager's own least-sure #1 resolves in the finding's favour and
neither published document needs retracting on that ground.**
⚠⚠ **BUT ONE SENTENCE IN BOTH DOCUMENTS IS FALSE AND IT IS THE COMPARISON HALF OF
THE HEADLINE:** *"`ptr_offset` is a TOP-3 OPERATOR IN EVERY ONE OF THE 22
PROGRAMS"* is **15 of 22**. ⚠⚠ **And `0 of 255` overstates the evidence by four
orders of magnitude in p-value: the honest unit is the FUNCTION and the
size-matched null gives `P(zero) = 0.061`, not `1.2e-05`.**
**§B: nothing forces it. The rungs simply were not written that way** — and §B's
own premise is half false, because **no `identity` pin involves the C rung at
all.** **§C: PHP is INSIDE the GNU spread on all 15 headline fields, so the
replication arm is stronger than the engineer argued — but content-hash dedup
does NOT remove gnulib**, and 17.5 % of the censused lines are near-duplicates.
**§D: the census reproduces byte-identically; `check` was withheld cleanly; the
generated exclusion is one code path applied to all four populations. Two
artefacts do not reproduce and there is a fifth, undisclosed instrument defect.**

---

## Findings, ranked

### B1 · blocker (to the published SENTENCE, not to the finding) — *"a top-3 operator in every one of the 22 programs"* is **15 of 22**

`.temp/t131/A_top3.txt`, computed from the **committed, byte-identical**
`php/coreutils/cgnu.json`, on the published (generated-excluded) population:

```
programs where ptr_offset is NOT in the top 3: 7 of 22
   glpk-5.0          rank 4, 0.9%      libosip2-5.3.1  rank 4, 2.5%
   depregawk-5.2.2   rank 4, 3.7%      pexec-1.0rc8    rank 4, 0.4%
   findutils-4.9.0   rank 4, 1.3%      grep-3.11       rank 4, 2.3%
   sed-4.9           rank 4, 5.3%
```

Robust to every variant I tried: `gen` included/excluded × 300-site floor / no
floor gives **15/22, 15/22, 17/25, 17/25**. In three of the seven the share is
**under 1.5 %** — `pexec` is `0.4 %`, which is a fortieth of PHP's.

**Where it is published:** `RECAP.md:3139` (with a ✅), `RECAP.md:3134`'s table
row by implication, `results/SYNTHESIS.md:1141–1142` (*"a TOP-3 OPERATOR IN EVERY
ONE OF THE 22 PROGRAMS"*), `.tasks/TASK_129_REPORT.md` §D1, and `TASK_131.md`'s
own §A. ⚠ **The true statement is available and is nearly as strong:
*`ptr_offset` occurs in all 22 programs, is second or third in 15 of them, and
its share ranges 0.4 %–26.1 % with a median of 6.9 %.*** ⚠ **That restatement is
what the manager should land; the coverage gap itself is untouched by it.**

### B2 · blocker (to the STRENGTH of the claim) — `0 of 255` is not 255 draws

The 255 sites sit in **30 site-carrying functions in 26 files that are clones of
one template** (`CLAUDE.md`: p01 is *"the template every later pattern clones"*).
`.temp/t131/A_power.txt` computes the null probability of a zero under each unit
of independence, **size-matched to the ladder's own function-size distribution**
(needed, because the fraction of functions that walk rises steeply with function
length — `A_size.txt`: cgnu 6.7 % → 27.1 % from the smallest to the largest
bucket):

```
                size-matched to the ladder's 30 fns / 255 sites
cgnu       FUNCTION unit  expected 2.66 walkers   P(zero) = 0.0612
           SITE     unit  expected 11.08 sites    P(zero) = 1.20e-05
coreutils  FUNCTION unit  expected 2.81           P(zero) = 0.0499
php        FUNCTION unit  expected 4.86           P(zero) = 0.0047
```

⚠⚠ **Against the corpus that carries §C's weight (cgnu, 21 of the 22 programs),
the honest figure is `p ≈ 0.06` — suggestive, not decisive.** The site-level
`1.2e-05` is what a reader takes from *"0 of 255"*, and it is wrong by a factor
of 5000. ✅ **The finding survives; the adjective does not.** Recommended
wording: *"no built kernel walks — 0 of 30 functions where a size-matched draw
from 21 GNU packages predicts 2.7, `p = 0.06`."*

### B3 · major — §B3, the cross-instrument control, does not reproduce

Running the engineer's own `crosscheck.py` against the engineer's own
byte-identical `*.json` (`.temp/t131/crosscheck_orig_t129.txt`) gives a table
that differs from the published one in **18 of 27 census cells**, across all
three corpora. Examples: php `memcpy` published 206 → reproduced **218**; php
`strcat` 108 → **136**; php `strlen` 586 → **633**; cgnu `memcpy` 1020 → **943**;
cgnu `sprintf` 646 → **561**.

⚠⚠ **And the sentence the arm exists to support is false at the reproduced
numbers.** The report says *"coreutils is 0 on eight of nine, which is the arm
that says the pipeline is not lossy by construction."* Reproduced, coreutils is
**0 on five of nine — and two of those five (`strcat`, `strncpy`) are trivial
0-versus-0 rows with no raw hits at all.** The non-trivial score is **3 of 7**,
and `sprintf` loses **9 of 13 (69 %)**.

**Cause, from mtimes:** `crosscheck.py` is 04:56 and `census.py`/the `*.json` are
04:59 — the table was captured from a pre-fix census run and never re-captured.
The qualitative claim (*"every delta is negative and bounded"*) survives; the
quoted table and the eight-of-nine sentence do not. ⚠ **Neither is in
`RECAP.md` or `SYNTHESIS.md`, so this is a report-only correction** — but it is
the arm that licenses *"the pipeline is not lossy by construction"*, which is
load-bearing for every zero the census prints.

### B4 · major — the classifier-independent raw regex exists in no artefact

RECAP finding 45: *"Confirmed independently of the classifier: a raw regex for
`*p++`, `*++p`, `*(p ±` returns `0` across the 26 kernel bytes and `845` over PHP
— ✅ manager-re-run, both numbers exact."* **That regex is in no committed file:
not `census.py`, not `crosscheck.py`, not `REBUILD.sh`, not `NOTES.md`.**
`grep -rn` over `.temp/t129/` finds only `census.py`'s internal classifier.

⚠ **This is the one arm that makes the headline independent of the instrument
under review, and it cannot be re-run.** I reconstructed it
(`.temp/t131/rawregex.py`): a unary-guarded `*p++ | *++p | *(p ±e)` gives
**php 854 / ladder 0 / coreutils 36 / cgnu 3305**. `ladder 0` reproduces exactly;
`854` is 1 % off `845` and I cannot close the gap without the original.
⚠⚠ **My FIRST attempt, without the unary guard, returned `ladder = 2` — and both
hits were `8 * (n + m)` in `p46`, i.e. I independently re-derived the manager's
own known-defective probe.** That is a live demonstration that this arm is easy
to get wrong and therefore must ship as a script. **Recommend promoting
`rawregex.py` (or the original) into `.temp/t129/` alongside `REBUILD.sh`.**

### B5 · major — §A's answer, with the measurement

**The objection:** *if `param 51.4 %` is a harness artefact of the `(buf, len)`
kernel signature, why is `ptr_offset 0` not one?*

I bucketed **every censused site by the signature shape of its enclosing
function**, re-parsing parameter lists from `census.py`'s own token stream so the
function boundaries are the census's (`.temp/t131/sigprobe.py`, `fnprobe.py`,
output `A_signature.txt`). `PTR+LEN` = ≥1 pointer/array param **and** ≥1
integer-scalar param. `PTR+NAMED` = the scalar's name is length-shaped.
`LADDER` = exactly one pointer param + 1–2 integer scalars and nothing else —
the closest corpus analogue of the ladder's C signature.

```
ptr_offset share, SITE level          fraction of site-carrying FUNCTIONS that walk
           ALL  PTR+LEN PTR+NAMED LADDER      ALL   PTR+LEN PTR+NAMED  LADDER
ladder    0.0%   0.0%    0.0%     0.0%      0/30    0/28     0/25      0/7
coreutils 7.4%   8.0%    2.2%     1.1%     10.8%    9.1%     4.0%      4.5%
php       8.8%  15.5%   17.8%     9.5%     15.6%   22.4%    24.8%     18.2%
cgnu      5.6%   3.9%    5.1%     3.0%      9.8%    9.2%    11.3%      8.7%
```

⚠⚠ **THE PREMISE IS REFUTED AS A MECHANISM.** *"A kernel handed an explicit
length has little reason to walk"* predicts a large depression in the `PTR+LEN`
column. At the function level cgnu goes **9.8 % → 9.2 %** (flat) and php goes
**15.6 % → 22.4 %** (**up**). Even at the strictest `LADDER` shape the rate is
**4.5 % / 18.2 % / 8.7 %** — never zero, and never close to it.
✅ **So the engineer's own artefact test, correctly applied to the second number,
does NOT dispose of it, and the two documents do not need correcting on this
ground.** The `param 51.4 %` withholding remains right for a different reason:
that comparison's numerator is the harness's *population* (leaf kernels only),
whereas `ptr_offset` is a *rate within* the matched population, which I have now
matched.

⚠ **AND A MANAGER PREMISE IS WRONG IN DETAIL, stated as ✅ manager-verified in
both `TASK_131.md` §A and `RECAP.md:3189`:** *"every C rung has the signature
`kernel(const T *v, size_t off, size_t len)`"*. Measured (`.temp/t131/sigs.txt`):
**21 of 26 take FOUR parameters** — `(const uint8_t *buf, size_t buf_len,
size_t off, size_t len)`. Only `p01`, `p19`, `p42`, `p46` are three-parameter;
`p02` is five-parameter. The extra `buf_len` makes the manager's argument
*stronger* in its own direction, but the spelling asserted is not the tree's.

**MUST-FIRE ARM, because a zero is what a broken detector prints.**
`.temp/t131/planted/p01_ptr_kernel.c` has p01's exact C signature and walks with
`*p++` and `*(p + i)`. `A_equiv.txt`: **4096 random windows, 0 mismatches**
against p01's shipped indexed kernel, and the must-differ arm **DIFFERS**.
`A_mustfire.txt`: `census.py` labels **both** sites `ptr_offset`, the raw regex
counts **2**. ✅ **Both instruments fire on a planted walker written under the
signature that is supposed to prevent walking.**

### B6 · major — §B: nothing forces it, and §B's own premise is half false

**(1) The `identity` pin cannot be the mechanism.** Across all 26 `spec.md`
blocks the pins are `unsafe ≡ verus` **×26** and `safe_naive ≡
safe_naive_verus` **×1** (p01). ⚠⚠ **NO `identity` PIN INVOLVES THE C RUNG AT
ALL.** The sentence in `RECAP.md:3202` and `TASK_131.md` §B — *"the `identity`
pin plus each pattern's `required` idiom would then be pinning every C rung to an
INDEXED spelling"* — is wrong in its first conjunct.

**(2) Nothing in `.memory/01-ladder.md` requires the C rung to mirror R2.**
Quoted, from its opening: *"The rungs must be **semantically equivalent on
well-formed input** (same checksum) and differ only in what enforces memory
safety"*, and R1 is *"Idiomatic C99 … Written the way a competent systems
programmer writes it"*. **The comparability requirement is SEMANTIC, not
syntactic.** My p01 and p11 pointer-cursor kernels produce byte-identical
checksums to the shipped ones over 4096 and 2000 windows, so R2 is untouched by a
walking R1. **§B's inference — "a pattern whose C rung walked would have no R2" —
does not follow.**

**(3) `forbidden` is the only idiom key with a gate verdict** (`check.py:40–41`
and `idiom_audit`: *"the `required` numbers stay presence, not compliance, and
never fail"*; `forbidden_verdict` fails the run). **Across all 26 patterns'
`forbidden` lists, not one entry forbids pointer arithmetic or a pointer cursor
in C** (`.temp/t131/idioms_all.txt`). The single exception is **p05's
`forbidden[1]: "a running row pointer"`**, which backticks nothing — p05 pins no
token at all, by its own `why` — so it is gate-invisible, and its stated reason
is that a row pointer *"deletes the flattened index, which IS the pattern"*, i.e.
p05's own mechanism, not R2's expressiveness.

**(4) The decisive experiment** (`.temp/t131/score1.py`, importing
`harness/check.py::spelling_matches` — name verified at `check.py:1216`). I wrote
a pointer-cursor respelling of **p11**, the walkiest built pattern (2000 windows
equivalent, must-differ arm fires) and scored it against p11's own declaration:

```
required spellings the shipped C rung matches and the pointer-cursor rung CANNOT: 5
forbidden spellings the pointer-cursor rung newly violates (gate would FAIL):     0
```

and for **p01**, whose declaration backticks nothing: **0 and 0**.

⚠ **The five broken `required` spellings are real but they are not a structural
bar.** They are `p = 4;`, `if (p >= len)`, `if (q >= len)`,
`h = h*31 + (uint64_t)buf[off + i];`, `slen = q - p;` — the **C half** of
per-language entries whose Rust half is already a *different* spelling
(`if p >= len {`). ⚠⚠ **The per-language `{"c": …, "rust": …}` key exists exactly
to let C and Rust spell one property differently, and twelve patterns already use
it.** A walking p11 would write `if (p >= end)` in the `c` key and change nothing
in the `rust` key. And `required` never fails the gate.

> ⚠⚠⚠ **§B's answer, and it is the one the task asked me to be willing to
> return: NOTHING FORCES IT. The rungs simply were not written that way.**
> The zero is a **declaration choice made 26 times**, gate-invisible, freely
> reversible through machinery the tree already uses. It is **not** a statement
> about the instrument. ⚠ **The one genuinely structural constraint I did find
> runs through R5, not R2** — several patterns pin subtraction-first cursor
> guards (`if (len - p < 8)`) *in the C rung* because *"the additive form
> `p + 8 > len` overflows usize and Verus rejects it"* (p06 `required[11]`, p14
> `required[15]`). **That is the prover reaching back into C through the
> matched-spelling convention.** It constrains the *arithmetic form*, not the
> cursor's *type*, and a pointer cursor satisfies it as easily as an integer one
> — so it does not rescue §B either. **UNPROBED beyond that.**

### B7 · major — §C: content-hash dedup does not remove gnulib

The report's defence is *"cross-corpus sha256 overlap: php∩coreutils 0,
coreutils∩cgnu 0, php∩cgnu 1. The three are content-disjoint."* ⚠ **A byte hash
cannot see a version skew, and that is exactly the shape gnulib has.**
`.temp/t131/gnulib2.py` measures line-level overlap between every pair of
surviving files sharing a basename:

```
repeated-basename pairs surviving dedup: 1223
  >= 0.99 of the 2nd copy's lines already in the 1st:  197  (16.1%)
  >= 0.95                                              501  (41.0%)
  >= 0.90                                              611  (50.0%)
REDUNDANT non-blank lines charged to 2nd-and-later copies: 150,451 of 861,940 = 17.5%
near-duplicate (>=0.90) pairs by corpus pair: coreutils<->cgnu 79, cgnu<->cgnu 406, php<->cgnu 16
```

**So 17.5 % of the censused corpus is near-duplicate, 79 pairs of it are the
coreutils↔cgnu gnulib contamination the task named, and 406 pairs are gnulib
copied across the 23 GNU packages** — which is precisely the correlation that
makes `n = 22` not `n = 22`.

✅ **The arm that must fire: does removing it move the headline?**
`.temp/t131/dedup2.py` re-dedups greedily at 0.90 line coverage (drops 657 of
2555 files, 15.6 % of lines) and recomputes:

```
                      BEFORE (published)              AFTER (near-dedup 0.90)
top operator      index 21 · str_call 1           index 20 · str_call 1
second operator   str_call 18 · ptr_offset 3 …    str_call 18 · mem_call 1 · ptr_offset 1 · index 1
top bound source  const 19 · none 2 · local 1     const 16 · none 3 · param 1 · local 1
second bound src  4 categories                    6 categories
spread const      12.7 .. 54.7  (42.0)            12.4 .. 62.6  (50.2)
```

⚠ **The OPERATOR headline holds** (`index` still tops 20 of 21). ⚠⚠ **The
BOUND-SOURCE headline weakens: `const` tops 19/22 → 16/21, second place goes from
four categories to six, and the spreads widen.** The engineer's conclusion
(*"the ordinal top is a property of C, the distribution is a property of the
program"*) survives and in fact **gets stronger on the distribution half**; the
`19 of 22` figure should carry a note that near-duplicate removal takes it to
`16 of 21`.

### B8 · minor — §C: PHP is INSIDE the GNU spread, so the replication arm is stronger than argued

`.temp/t131/outlier.py`, PHP against the 21 GNU packages on every field that
carries a headline:

```
field            php   GNUmin  GNUmed  GNUmax   in range?  rank/22    z
op:index        62.2     39.0    63.9    91.5     INSIDE     12/22  -0.19
op:ptr_offset    8.8      0.4     6.6    26.1     INSIDE      9/22   0.19
op:str_call     23.0      6.4    16.7    56.5     INSIDE      8/22   0.16
bnd:const       36.3     12.7    32.6    54.7     INSIDE      8/22   0.30
bnd:none        20.3      6.6    15.5    56.1     INSIDE      9/22   0.08
bnd:local       19.2      5.3    20.4    50.8     INSIDE     13/22  -0.17
… 15 fields, ALL INSIDE, ranks 4th–15th of 22, |z| <= 0.72, never an extreme
```

⚠ **Being "inside" a 42–50-point spread is a weak test by itself** — two of any
21 are outside by construction. **The informative statistic is the RANK: PHP is
mid-pack on all fifteen and extreme on none.** ✅ **That is what an exchangeable
draw looks like, and it licenses the engineer's *"ordinal top is a property of
C"* more than the engineer claimed.**

⚠ **But the report's own PHP caveat is false.** §E: *"PHP 4.0.2 is from 2000. Its
23 % `str_call` share is the highest of the 22"*. It is **8th of 22**:
`units 56.5 · libosip2 44.9 · wget 32.7 · make 31.2 · sed 27.8 · findutils 27.8 ·
pexec 27.1 · php 23.0`. This **contradicts the report's own §C table**, which
already records `units` as the one program where `str_call` is the *top*
operator. Not quoted in RECAP or SYNTHESIS — report-only.

### B9 · minor — a FIFTH, undisclosed instrument defect, quantified, with a null effect

`census.py::scan_locals` walks a declaration statement to its `;` and adds every
identifier whose next token is `; , = [ )` — **including the identifiers in the
INITIALISER**. So `int errind = ap_php_optind;` (php `sapi/cgi/getopt.c:87`)
registers the **file-scope global** `ap_php_optind` (declared `int
ap_php_optind = 1;` at line 14) as a **local** of `ap_php_getopt`; and
`classify_bound` tests `local` **before** `global`.

✅ **Verified directly**: `'ap_php_optind' in f.locals → True` for
`ap_php_getopt`.

⚠⚠ **This IS hand-label disagreement #57**, which the report files as a
definitional difference (*"`ap_php_optind`, compared against `argc` earlier"*)
rather than as a bug in the field it already flags as its weakest.

`.temp/t131/initbug.py` re-runs the classifier with the initialiser skipped:

```
php:       1482 names polluted;  19 of 7697 sites move (0.25%): local -14, global +13, param +3
coreutils:  364 names polluted;   2 of  515 sites move (0.39%)
NO RANKING MOVES.
```

✅ **So: a real defect, a clean negative on the published numbers.**

### B10 · minor — §D's two readings, recomputed, and the engineer's self-criticism is one point too harsh

The engineer names its own most-attackable call: it hand-labelled `bound`
**semantically**, so a reviewer could say *"the classifier implements its
definition perfectly; the definition is 43 % useful"*. **Both readings
recomputed from `hand_labels.tsv` and the six disagreements adjudicated one by
one against `classify_bound`'s own rule:**

| disagreement | classifier's own rule says | reading |
|---|---|---|
| #20 `php_imap.c:2462` `*outp++` → `cursor` | correct by construction (disclosed defect 6) | definitional |
| #56 `regex/split.c:44` `*fp++` → `cursor` | correct by construction | definitional |
| #44 `hashtable.c:112` `i` → `local` | correct — `i` is a local | definitional |
| #45 `xmlparse.c:1528` `n` → `local` | correct — `n` is a local | definitional |
| #47 `xmlparse.c:1851` `i` → `local` | correct — `i` is a local | definitional |
| **#57 `getopt.c:79`** `ap_php_optind` → `local` | ⚠ **WRONG — it is a file-scope global and the label set has `global`** | **a rule violation (B9)** |

```
SEMANTIC reading (published):   bound 54/60 = 90.0%    local 3/7
SYNTACTIC reading:              bound 59/60 = 98.3%    local 6/7   <-- NOT 60/60
```

⚠ **Publish the SEMANTIC number.** It is the one that bounds the **ranking**,
which is what the census is for; a syntactic self-comparison measures the regex,
not the code. ✅ **But the engineer's self-criticism should be capped: the
alternative reading is 59/60, not "the classifier implements its definition
perfectly", because one of the six is a genuine bug.**

### B11 · minor — RECAP's headline table is the GENERATED-INCLUDED population

The report excludes generated files because their measured recall is **0/5**, and
says the published tables do so. **`RECAP.md:3132–3136`'s table does not**:

```
                  RECAP finding 45   gen-EXCLUDED (the report's tables)
index php/cu/gnu   62.3 / 75.3 / 72.9    62.2 / 75.3 / 72.3
ptr_offset         8.8 / 7.4 / 5.7        8.8 / 7.4 / 5.6
str_call          22.9 / 10.1 / 15.9     23.0 / 10.1 / 16.5
mem_call           5.5 /  7.2 /  5.1      5.6 /  7.2 /  5.3
total sites            49 898                 46 948
```

Deltas ≤ 0.6 pp and no ranking moves, so this is hygiene — but *"49 898 bound
sites"* and the `5.7 %` in *"5.7–8.8 % of the corpora"* are the pre-exclusion
figures, and the pre-exclusion population is the one whose recall is zero.

### B12 · minor — the committed `rank.txt` is stale

`.temp/t129/rank.txt` (04:59) predates `ladder.json` (05:04) and **carries no
ladder column at all** — so the one artefact a reader would open to check
*"0 of 255"* does not contain it. Regenerating it reproduces every corpus number
byte-identically **and** produces the ladder column the report quotes
(`index 237 92.9 % · ptr_offset 0 · str_call 1 · 255 sites`). Re-run
`REBUILD.sh` and commit, or say the file is stale.

---

## Clean negatives — attacks that did NOT land

1. ✅ **The detector is not broken.** A planted pointer-cursor kernel *with p01's
   exact signature* is found by both instruments (`A_mustfire.txt`), and is
   checksum-identical to the shipped kernel over 4096 windows.
2. ✅ **`REBUILD.sh` reproduces.** Exit 0 in ~4 min. `php.json`,
   `coreutils.json`, `cgnu.json`, `agree.txt`, `perprog.txt`, `recall_php.txt`,
   `sample_php.txt`, `hand_labels.tsv`, all three manifests and every corpus
   `.files`/`.headers` are **byte-identical** (`orig_t129_sha256.txt` vs
   `new_t129_sha256.txt`). `ladder.json` is identical modulo the path prefix.
   Coverage reproduces exactly: **78.274 / 83.164 / 81.999 %**. Only `rank.txt`
   (B12) and the `crosscheck` table (B3) differ.
3. ✅ **`check` was genuinely withheld.** It appears only in `rank.txt`, marked
   *"⚠ NOT limb 3"*, and as its own error rate in RECAP/SYNTHESIS. `perprog.py`
   never reads it; no per-program table, no ratio and no derived claim uses it.
   **Nothing to correct.** This is the behaviour to copy and it was executed.
4. ✅ **The generated-file exclusion is NOT applied to one arm.** It is a single
   code path — `census.py::is_generated`, called in `process_file` — run
   identically over php, coreutils, cgnu **and the ladder**. coreutils simply
   contains no generated files (0 flagged). `zend-parser.c` is in `php.files`,
   is bison output, and yields 0 rows either way. **Not a bias.**
5. ✅ **Function SIZE is not a hidden confound for the site-level number.** The
   *fraction of functions that walk* rises steeply with length (cgnu 6.7 % →
   27.1 %), but the *site-level* `ptr_offset` share is roughly flat across
   buckets (cgnu 5.7 / 4.1 / 4.2 / 4.6 / 3.0 / 9.1). I size-matched B2's
   power calculation anyway.
6. ✅ **No `forbidden` entry anywhere in the tree excludes pointer arithmetic in
   C.** I read all 26 idiom blocks (`idioms_all.txt`). This is the attack that
   would have made §B true and it found nothing.

---

## What the manager should change (I did not edit these)

**`RECAP.md` finding 45**
- ⚠⚠ **Replace *"`ptr_offset` IS A TOP-3 OPERATOR IN EVERY ONE OF THE 22
  PROGRAMS"* with *"occurs in all 22, second or third in 15, share 0.4 %–26.1 %,
  median 6.9 %"*.** (B1)
- ⚠⚠ **Add the power statement beside `0 of 255`: `0 of 30 site-carrying
  functions, where a size-matched draw from the 21 GNU packages predicts 2.7,
  P(zero) = 0.061`.** The site-level reading is not available. (B2)
- ✅ **Record that §A's objection is SETTLED AND DISMISSED**, with the
  measurement: signature-matched corpus functions walk at 9.2 % (cgnu) / 22.4 %
  (php) / 9.1 % (coreutils) against 9.8 / 15.6 / 10.8 unmatched. (B5)
- ⚠ **Strike the ✅ on *"every C rung has the signature `kernel(const T *v,
  size_t off, size_t len)`"*: 21 of 26 are four-parameter.** (B5)
- ⚠⚠ **Replace the third reading with its measured answer: NOTHING FORCES IT.**
  No `identity` pin touches C; `.memory/01-ladder.md`'s comparability is
  semantic; no `forbidden` entry excludes a C pointer cursor; a pointer-cursor
  p11 breaks 5 `required` (which never fail) and 0 `forbidden`. **Mark the
  R5-side subtraction-first observation OPEN, not as a mechanism.** (B6)
- ⚠ **Note that the table is the generated-INCLUDED population** and either
  re-quote the excluded one or say which is meant. (B11)
- ⚠ **The `845 / 0` raw-regex figures have no artefact.** Either promote a
  script or mark the number unreproducible. (B4)
- ⚠ **`const` tops 19 of 22 → 16 of 21 after near-duplicate removal.** (B7)

**`results/SYNTHESIS.md` §7** (`:1141–1142`) — same B1 correction, and the same
B2 power caveat. **Everything else in §7 stands.**

**`.memory/03-measurement.md`, the controls list** — I did not find a new
entry-9-shaped case. ⚠ **B3 is a different shape and may deserve one: *a control
whose PUBLISHED numbers are not the ones its own committed script and committed
inputs produce.* Entries 1–8 are controls that could not fire; entry 9 is one
that fired and pointed the other way; B3 is one that fired, correctly, and whose
transcript was captured three minutes before the instrument it describes was
fixed.** The lesson is cheap: **re-capture every quoted table after the last
instrument change, or generate it into a file the way `rank.txt` and `agree.txt`
are.** ✅ **The two arms that WERE written to a file both reproduced byte-exactly;
the one that lived only in a terminal did not.**

---

## Answer to the three calls the manager was least sure of

1. ⚠⚠ **`ptr_offset = 0` SURVIVES §A.** It is not a signature artefact —
   measured, in the direction that refutes the objection. **Neither published
   document needs retracting on that ground.** ⚠ **They need correcting on a
   different one (B1) and weakening on a third (B2).**
2. ⚠⚠ **§B's third reading is just a nicer story.** Give it the most hostile
   evidence available and it dies on four independent grounds, three of them one
   `grep` each. ✅ **The manager's instinct to distrust it was right.**
3. ⚠ **The census WAS worth reviewing.** The engineer's hygiene is as good as
   the task said — the withholding, the declining, the four self-caught defects
   all check out — **but the two sentences that are wrong are both in the
   outward document, both in the headline, and neither is in the engineer's
   report's careful sections.** B1 is in `SYNTHESIS.md`. **A review that had
   closed short after §A would have left it there.**

---

## Problems / not done

- ⚠ **I could not reproduce the `845` exactly** (best reconstruction: 854). The
  original regex is not recorded anywhere. `ladder = 0` reproduces exactly and
  the conclusion is unaffected.
- ⚠ **`dedup2.py`'s 0.90 threshold is a judgement call.** I report the whole
  threshold curve in `C_gnulib.txt` rather than one number; the operator headline
  holds at every threshold I tried, the bound-source one weakens at all of them.
- ⚠ **I hand-adjudicated six disagreements, not sixty.** B10's syntactic reading
  rests on reading `classify_bound` and the six sites; I did not re-hand-label
  the sample.
- **I did not test whether a pointer-cursor rung would pass the FULL gate** —
  only the idiom stage, via the imported `spelling_matches`. `driver.canonical`,
  `collapse`, `identity` and the Verus stages are untouched by a C-rung
  respelling by inspection (no `identity` pin names C; the driver pin is over the
  driver loop, not the kernel), **but that is an argument, not a run**, and I was
  forbidden to run the gate.
- **I did not hand-check a coreutils or cgnu sample.** That remains the
  engineer's own top "unsure" and it is still open.
- **I proposed no pattern.** §E honoured: §B came out *"nothing forces it"*, so
  there is no *"the zero is real and a row is possible"* paragraph to write, and
  I draw no build/stop conclusion.

## Memory updates

**None** — `.memory/`, `RECAP.md` and `results/SYNTHESIS.md` are manager-only and
I am a reviewer. Everything durable is in `.temp/t131/` (`NOTES.md`, `REBUILD.sh`,
eleven `.py` probes, two planted `.c` kernels with their equivalence harnesses,
and the `A_*/B_*/C_*/D_*` outputs). Binaries deleted; `REBUILD.sh` rebuilds them.

---

⚠ **PROTOCOL rule 2's running count. This task was launched from 617; the
manager reconciles, not me.** What I add: **one false sentence in two published
documents** (`top-3 in every one of the 22` → 15 of 22), **one published
statistical framing overstated by 5000×** (`0 of 255` → `p = 0.061` at the honest
unit), **one control table that does not reproduce from its own committed
inputs** (§B3, 18 of 27 cells, and its `eight of nine` sentence is `five of
nine`), **one licensing arm with no artefact at all** (the raw regex),
**one manager premise wrong in detail** (21 of 26 C kernels are four-parameter),
**one §B premise half false** (no `identity` pin touches C), **one dedup defence
refuted** (content hash leaves 17.5 % near-duplicates), **one fifth undisclosed
instrument defect with a measured null effect** (`scan_locals` eats
initialisers), **one report caveat that is false and self-contradicting** (PHP's
`str_call` is 8th of 22, not highest), and **six named attacks that did not
land.**

**The call I am least sure of, and I want it attacked:** ⚠⚠ **that
`PTR+LEN`/`LADDER` signature-shape matching is the right control for §A.** I
matched on the *shape of the parameter list*; I did not match on **what the
function does**. A corpus function with `(ptr, len)` may be a parser or a string
routine, where walking is natural, while every ladder kernel folds over a
fixed-stride array, where indexing is natural. **If someone matched on WORK
rather than on SIGNATURE the depression could be larger than I measured** — and
`A_size.txt` shows the `LADDER` class in cgnu is 24.4 % `str_call`, which is
evidence that the classes are not doing the same job. ⚠ **My conclusion would
survive a smaller depression (the rates would have to fall to ~0 to make the zero
unremarkable, and they are 3–18 %), but the exact numbers in B5 would move.**
