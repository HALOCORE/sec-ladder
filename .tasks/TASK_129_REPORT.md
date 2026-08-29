# TASK_129 — the idiom census, run. 991 147 lines of deduplicated C, 22 programs.

**Engineer report. Not reviewed.** Everything below was run; commands and their
output are in `.temp/t129/` (`REBUILD.sh` regenerates all of it in ~1 minute).
**I wrote nothing outside `.temp/t129/` and this file.** I did not run
`check.py`, `build.py`, `measure.py` or `report.py`.

---

## HEADLINE

1. ⚠⚠ **THE CENSUS RUNS, AND ITS ERROR RATE IS MEASURED PER FIELD.**
   Against 60 hand-classified sites: **operator 60/60 (100%)**, **bound source
   54/60 (90%)**, **check 45/60 (75%)**. ⚠ **The `check` field is UNUSABLE and I
   report it as such** — its `earlier` label is right **3 times out of 10**, and
   the errors are directional, not noise. **The operator table is solid; the
   bound-source table is solid at the top and unreliable in the middle.**
2. ⚠⚠ **THE REPLICATION ARM IS n=22 PROGRAMS, NOT n=2 — I FOUND A THIRD CORPUS
   THE MANAGER'S FILE LIST HAD NOT BEEN CHARACTERISED FOR.** 24 GNU/third-party
   program directories = **23 distinct programs** (`gawk-5.2.2` and
   `depregawk-5.2.2` are byte-identical, 91/91 `.c` hashes), **2 162 distinct
   `.c`, 785 480 lines**, at
   `unsafe-rust-pitfall/.temp/shared/artifacts/pr2/benchmarks/c-gnu/`.
3. ✅ **AND THE ASYMMETRIC TEST CAME OUT ON THE STRONG SIDE, WHICH THE MANAGER
   DID NOT EXPECT.** `index` is the top operator in **21 of 22** programs and
   `str_call` the second in **18 of 22**; `const` is the top bound source in
   **19 of 22**. ⚠⚠ **BUT THE SHARES SWING ENORMOUSLY — `const` ranges 12.7 % to
   54.7 %, `none` 6.6 % to 56.1 %, `local` 5.3 % to 50.8 %.** **So: the ORDINAL
   TOP is a property of C; the DISTRIBUTION is a property of the program.** ⚠ **A
   frequency-argued admission bar can therefore be given a first place and
   nothing else** — second place flips between four categories across 22 real
   programs of one house style.
4. ⚠⚠ **THE COVERAGE ANSWER, AND IT IS A CLEAN MEASUREMENT: the built tree
   covers the frequent OPERATOR and misses the second-most-frequent one
   entirely.** Same instrument on the 26 built `c/kernel.c`: **`ptr_offset` 0 of
   255 sites** (5.6–8.8 % of the corpora) and **`str_call` 1 of 255**
   (10.1–23.0 %). **The one `str_call` is `p11`'s `strlen`.** ⚠ **`p12` and
   `p13` — the catalogue's *"`strcat` into a fixed stack buffer"* and
   *"`strncpy`/`snprintf` truncation"* — call NO `str*` function at all: both
   kernels spell the copy out by hand, and `p13`'s own comment says so.**
5. ⚠ **THE MANAGER'S coreutils FIGURE IS A PRE-DEDUP FIGURE.** `310 .c /
   56 873 lines` deduplicates to **94 files / 18 862 lines** — a 3.0× reduction,
   and the tree is only **7 utilities**. As specified it is **one tenth** of the
   PHP arm and would have been a weak control on its own.
6. ⚠⚠ **MY OWN CENSUS HAD FOUR INSTRUMENT DEFECTS, EXACTLY AS THE TASK
   PREDICTED, AND ONE OF THEM MADE 29 % OF PHP INVISIBLE.** All four were caught
   by arms written before any counting. Listed in §F.

---

## §0 — corpora, deduplicated, with a manifest

`manifest.sh` writes `sha256sum` manifests of **every `.c` and `.h` file read**,
from all three trees. They live at `.temp/t129/{php,coreutils,cgnu}.manifest`
(80 K / 180 K / 696 K, 5 342 lines total). Roll-up digests of the manifests
themselves, so this report carries a checkable fingerprint:

```
4da6224a408be379385743ef8d783322eacb80c1c507dc323725a9e072509948  php.manifest
267339d555d7e1ff9bbd2437a661349c366f45e897728133a135847353a0ba96  coreutils.manifest
f2fe5679a57ace664a990ae757a00d127947344cb3bb38f4b6ab9645640cbc43  cgnu.manifest
```

| corpus | `.c` files | **distinct by sha256** | dedup lines | MB |
|---|---|---|---|---|
| php-4.0.2 (`php-in-safe-rust/build/`) | 301 | **299** | 186 805 | 5.04 |
| coreutils (`TASK014_eng_coreutils_u2/.temp/work/`) | 310 | **94** | **18 862** | 0.58 |
| **c-gnu, 23 distinct programs** (`unsafe-rust-pitfall/.temp/shared/artifacts/pr2/benchmarks/c-gnu/`) | 2 651 | **2 162** | **785 480** | 23.45 |
| **total censused** | 3 262 | **2 555** | **991 147** | 29.07 |

Cross-corpus sha256 overlap on `.c`: php∩coreutils **0**, coreutils∩cgnu **0**,
php∩cgnu **1**. The three are content-disjoint. Nothing was copied into this
tree; all three were read in place, read-only.

**The third corpus, and how I found it.** The task's least-sure #2 asked for a
third corpus and gave the command. `find / -name '*.c' …` with **no `-maxdepth`**
gives 31 929 rows (`.temp/t129/allc.txt`). 17 115 of them are `TASK003`'s c2rust
synthetic benchmark (excluded, as instructed) and 3 793 are `php-5.0.0` build
trees (**not independent of php-4.0.2**, excluded). What was left uncharacterised
is `.temp/shared/artifacts/pr2/benchmarks/c-gnu/`: **findutils-4.9.0 307,
tar-1.34 291, indent-2.2.13 263, grep-3.11 250, diffutils-3.10 242, sed-4.9 228,
glpk-5.0 201, cpio-2.14 191, gawk-5.2.2 90, depregawk-5.2.2 90 (⚠ **the same 90
files byte-for-byte — one of the two is dropped by dedup**), cflow-1.7 79,
enscript-1.6.6 75, libosip2-5.3.1 67, make-4.4.1 59, wget-1.21.4 53, rcs-5.10.1
38, pth-2.0.7 37, mcsim-6.2.0 35, gzip-1.12 17, pexec 9, patch-2.7.6 8, ed-1.19
8, units-2.22 5, hello-2.12.1 1.**
⚠ **Caveat, stated once and meant: these are GNU-style utilities, so they are
independent of coreutils in PROGRAM but NOT in HOUSE STYLE. The one non-GNU
sample is PHP.** That is the ceiling on §C's claim.

---

## §A — the categories, fixed before any counting

A **site** is a memory access whose safety depends on a bound. Label sets, and
the classifier's priority order, were written into `census.py`'s docstring and
`.temp/t129/NOTES.md` **before** the first count.

- **operator** — `index` · `ptr_offset` (`*(p±e)`, `*p++`, `*++p`) · `mem_call` ·
  `str_call` · `cast_deref`. ⚠ A plain `*p` is **excluded**: its safety depends
  on validity, not on a bound.
- **bound source** — `none` (the operator carries no size argument at all) ·
  `const` (`sizeof`, a literal, or a `#define`d integer) · `strlen` · `call` ·
  `field` · `induction` · `cursor` · `param` · `local` · `global`, applied in
  that order to the **bound expression** (the subscript, the offset, or the
  size argument). For an `induction` site a second field `resolved` re-applies
  the same classifier to the **enclosing loop's own bound**, which is the
  informative one and the one §B checks.
- **check** — `at_site` · `earlier` · `none`.
  ⚠⚠ **THIS IS NOT LIMB 3. Limb 3 is ELISION, which is a property of the
  compiler and is not observable in source at all. I did not attempt it and no
  number below should be read as one.** `check` is a strictly weaker,
  syntactic thing: where a relational comparison mentioning a root identifier of
  the bound expression sits relative to the site.

⚠ **Two of the task's own bound-source names have no separate label here, and it
matters for §D.** *"an attacker length field"* and *"a prior pass's count"* are
both **semantic** and land in `field` or `local` depending only on where the
program stores the number. Sample site 38 is exactly `CVE-2021-23017`'s
mechanism, in PHP's own `ext/standard/scanf.c`: `BuildCharSet` counts ranges in
a **sizing pass**, `emalloc`s `sizeof(struct Range)*nranges`, then fills
`cset->ranges[cset->nranges]` in a **writing pass with no re-check**. My census
labels it `field`. **It cannot separate that from any other struct-field bound,
and I am not claiming it can.**

---

## §B — the arm without which this is worthless. MEASURED.

### B1 · precision — 60 sites, hand-classified

Drawn **by site, not by file**, from the PHP census: `random.Random(129).sample(
range(7838), 60)`, sorted. Reproduce with
`census.py sample php.json --n 60 --seed 129 --out sample_php.txt`. The 60 labels
are in `.temp/t129/hand_labels.tsv` with the hand rule stated at the top; the
agreement is computed mechanically by `agree.py`, not by hand-tallying prose.

```
AGREEMENT, classifier vs 60 hand labels (php-4.0.2 sample, seed 129)
  op      60/60 = 100.0%   (0 disagreements)
  bound   54/60 =  90.0%   (6 disagreements)
  check   45/60 =  75.0%   (15 disagreements)
```

**Per-category precision — this is what biases the ranking, and the answer is
that the top of the table is clean and the middle is not:**

```
bound label   correct/drawn        check label   correct/drawn
  const          25/25               none           34/40
  none           11/11               at_site         8/10
  field           9/9                earlier         3/10     <-- unusable
  param           3/3
  global          2/2
  local           3/7      <-- 43%
  cursor          1/3      <-- 33%
```

**The six `bound` disagreements, individually** (the task asked for these, not a
percentage):

| # | file:line | auto | hand | why |
|---|---|---|---|---|
| 20 | `php_imap.c:2462` | `cursor` | `none` | `*outp++` — **`outp` has no bound at all**; `*p++` is labelled `cursor` by construction |
| 56 | `regex/split.c:44` | `cursor` | `param` | `*fp++`, bounded by the `fn = nfields` countdown |
| 44 | `hashtable.c:112` | `local` | `field` | `i = h & (table->size - 1)` — a mask from a struct field, one assignment away |
| 45 | `xmlparse.c:1528` | `local` | `call` | loop bound `n = XmlGetAttributes(...)` |
| 47 | `xmlparse.c:1851` | `local` | `strlen` | `for (i=0; protocolEncodingName[i]; i++)` — a **NUL scan spelled with an index**, which the `strlen` label cannot see |
| 57 | `sapi/cgi/getopt.c:79` | `local` | `param` | `ap_php_optind`, compared against `argc` earlier |

⚠ **The confusion is entirely `local` ↔ (`field`, `call`, `strlen`, `param`) and
`cursor` ↔ (`none`, `param`). Not one disagreement moved a site into or out of
`const` or `none`.** So the two top ranks are unaffected by classifier error,
and **`local` (13.8–20.7 % of sites) and `cursor` (7.1–10.2 %) are inflated:
about half of `local` is really a bound established one assignment away.** ⚠⚠
**This is the manager's least-sure #1 confirmed exactly: `local` is where an
unresolvable bound goes, and a source census cannot chase it further without
becoming a dataflow analysis.**

**The 15 `check` disagreements, by direction** — they are systematic, which is
why the field is dead:

```
auto=none    hand=earlier   x4      <- switch(argc) case 7:, if(argc<3||argc>4)
auto=earlier hand=at_site   x4      <- the site sits in an inner if's CONDITION
auto=earlier hand=none      x3      <- root-id collision (local `nranges` vs `cset->nranges`)
auto=none    hand=at_site   x2      <- CONST-INDEX SITES CAN NEVER BE ANYTHING BUT `none`
auto=at_site hand=none      x1
auto=at_site hand=earlier   x1
```

> ⚠⚠ **VERDICT ON `check`: UNUSABLE, AND THE FIELD THAT KILLS IT IS THE BOUND
> EXPRESSION HAVING NO IDENTIFIERS.** A `const`-index site (33 % of PHP,
> 26–32 % of the others) has a bound expression like `4`, so the root-identifier
> match is empty and `check` is forced to `none` — while the guard
> `if (argc > 4)` is right there on the line above. **Do not cite the CHECK
> table.** I have left it in `rank.txt` marked, because deleting it would hide
> the measurement that condemns it.

### B2 · recall — the arm precision cannot give you

Precision says nothing about what the census never saw. `recall.py` samples raw
`0x5B` bytes from the corpus — **an instrument sharing no code with the
tokenizer** — and I hand-adjudicated all 40 draws
(`.temp/t129/recall_adjudication.md`). Raw `[` population: **7 505**.

- **11 are not sites** (7 comments, 3 array declarators, 1 prototype with array
  parameter types) — the census recorded **0 of 11**. **False positives: 0.**
- **23 are sites in ordinary hand-written C — 23/23 found. Recall 100 %.**
- **5 are sites inside bison-generated files** (`zend-parser.c` ×4,
  `parsedate.c` ×1) — **0/5. Recall 0 %.**
- 1 is a site in an `#ifdef` branch the census resolved away — disclosed cap.

✅ **Both generated files are already flagged by `census.py::is_generated`, so
the published tables EXCLUDE generated files and the applicable recall figure is
the 100 %.** Excluding them moves the totals php 7 838 → 7 697 and cgnu
41 545 → 38 736, and moves **no ranking**.

### B3 · the cross-instrument control

`crosscheck.py` counts nine library calls with a regex over **raw bytes**
(comments and strings not stripped) and compares with the census:

```
              php                 coreutils            cgnu
fn        raw  census  delta    raw census delta    raw census delta
memcpy    233   206    -27       20    20     0    1116  1020   -96
memmove    13    13      0        3     3     0     123   114    -9
memset    121   110    -11        4     4     0     807   784   -23
strcpy    127   113    -14        8     8     0     481   452   -29
strlen    690   586   -104       20    20     0    2563  2382  -181
strncpy    48    43     -5        0     0     0     104   100    -4
sprintf   270   258    -12       13    10    -3     714   646   -68
snprintf  126    97    -29        1     1     0     311   197  -114
strcat    151   108    -43        0     0     0     121   102   -19
```

Every delta is **negative and bounded**, and every one is accounted for by a
disclosed exclusion: prototypes, comments and strings, `#define` bodies, dropped
`#ifdef` branches, and file-scope initialisers. **coreutils is 0 on eight of
nine, which is the arm that says the pipeline is not lossy by construction.**

### B4 · the must-fire arm on the instrument itself

`census.py selftest` builds a 60-line C file with 27 hand-declared ground-truth
sites across three functions (ANSI, adversarial, K&R), asserts **all four
fields** on every one, runs a **negative control** (a file with no memory access
→ must give 0 sites), and runs a **must-fire arm**: it disables comment
stripping and requires the site count to CHANGE.

```
OK   t1: 20/20 sites, all four fields match
OK   t2: 3/3 sites, all four fields match
OK   t3: 4/4 sites, all four fields match
NEGATIVE control: 0 sites (must be 0)
MUST-FIRE arm (disable comment stripping): sites 27 -> 30 => FIRED
SELFTEST PASS
```

---

## §C — the replication arm, run at n=22 instead of n=2

`perprog.py` treats each **program** as an independent sample (22 with ≥ 300
sites). Bound source with `induction` resolved to the loop's own bound, %:

```
program                 sites    const   none  local cursor  field  param global   call
glpk-5.0                10252     12.7    6.6   50.8    3.2    8.6   16.7    0.5    0.8
php-4.0.2                7697     36.3   20.3   19.2   10.2    9.1    2.9    0.8    0.8
depregawk-5.2.2          3285     30.5   14.1   24.5    6.2   15.3    7.2    1.6    0.3
mcsim-6.2.0              3055     36.4    7.6   26.9    5.2    9.7    8.1    5.1    0.4
tar-1.34                 3041     31.5   16.0   22.3   13.3    9.7    6.3    0.7    0.1
diffutils-3.10           2506     54.7   11.6   11.5   12.4    5.7    1.8    1.6    0.2
make-4.4.1               2210     35.2   30.3   19.9    7.5    3.1    1.7    1.5    0.3
enscript-1.6.6           1866     28.6   19.9   23.4   13.9    9.6    2.6    0.9    0.5
findutils-4.9.0          1783     42.7   26.1   13.0    9.8    1.8    2.6    1.0    2.5
indent-2.2.13            1482     40.1    8.9    5.3   15.7   15.6    3.7   10.7    0.0
wget-1.21.4              1478     30.1   29.2   18.9   12.2    2.6    2.9    0.5    3.4
cpio-2.14                1431     36.3   12.3   16.4   19.1   11.3    3.9    0.5    0.1
libosip2-5.3.1           1157     35.2   33.8   24.4    2.6    0.6    3.3    0.0    0.0
pexec-1.0rc8             1062     23.3   26.7   21.4    0.4    2.4   24.8    0.0    0.0
grep-3.11                 660     40.9   21.7   15.5    8.2    2.6    2.1    0.9    7.9
patch-2.7.6               572     41.1   12.8   22.0    7.0    0.0    4.4   12.1    0.5
rcs-5.10.1                524     43.3    9.2   12.6   27.3    3.2    2.9    1.1    0.2
coreutils(7 utils)        515     32.2    8.9   20.4    9.7    1.6   24.5    2.7    0.0
units-2.22                510     16.3   56.1   16.9    3.7    4.9    0.8    0.0    0.8
gzip-1.12                 475     32.6   13.9   29.7    6.7    0.4    8.0    8.0    0.2
sed-4.9                   468     32.1   26.5   23.1    9.2    6.6    0.9    1.5    0.0
cflow-1.7                 401     28.9   15.5   17.0   11.0    5.5   16.0    6.0    0.2

SPREAD           min   median    max   range (percentage points)
const           12.7     33.9   54.7    42.0
none             6.6     15.7   56.1    49.5
local            5.3     20.1   50.8    45.6
cursor           0.4      9.4   27.3    26.9
param            0.8      3.5   24.8    24.0
field            0.0      5.2   15.6    15.6
```

**Top bound source per program: `const` 19 · `none` 2 (`units`, `pexec`) ·
`local` 1 (`glpk`).**
**Top operator per program: `index` 21 · `str_call` 1 (`units`).
Second operator: `str_call` 18 · `ptr_offset` 3 · `index` 1.**

Operator shares, the three corpora side by side (generated excluded):

```
              php     coreutils    cgnu      ladder(26 kernels)
index        62.2%      75.3%     72.3%          92.9%
str_call     23.0%      10.1%     16.5%           0.4%
ptr_offset    8.8%       7.4%      5.6%           0.0%
mem_call      5.6%       7.2%      5.3%           6.3%
cast_deref    0.5%       0.0%      0.3%           0.4%
```

> ⚠⚠ **WHAT §C LICENSES, IN THE TASK'S OWN TERMS.** The rankings **AGREE at the
> top** across a 2000-era interpreter and 21 GNU utilities, so *"index is the
> dominant operator and a compile-time constant is the dominant bound source"*
> **has a claim to be about C rather than about PHP.** ⚠ **It is still a weak
> claim, and here is exactly how weak: 21 of my 22 programs are GNU-style
> utilities, so this is n=1 house style plus one interpreter, not a sample of
> C.** ⚠⚠ **And the DISAGREEMENT half of the task's test also fired, at a finer
> grain: the SHARES swing by 42–50 percentage points and second place flips
> between `none`, `local`, `cursor` and `param` across the 22. Idiom frequency
> below first place IS a property of the program.** ✅ **That retires
> `TASK_113`'s request honestly: a frequency-argued admission bar can be given a
> first place on this evidence and nothing below it.**

---

## §D — the coverage question, with the SAME instrument on both sides

I ran the identical census on the **26 built `patterns/*/c/kernel.c`** (extracted
read-only from `git show HEAD:` into `.temp/t129/`, regenerated by
`ladder_extract.sh`, the copies then deleted): **26 files, 39 functions,
255 sites.**

**Answer: the built tree covers the frequent OPERATOR and misses the
second-most-frequent one entirely.** Stated as coverage, not as quality — the
bar was never frequency-based, so this describes the bar's choice.

1. ⚠⚠ **`ptr_offset` — 0 of 255 sites in the built tree, against 5.6–8.8 % of
   the corpora and a top-3 operator in every one of the 22 programs.** ✅ **This
   is not a classifier blind spot and I checked it independently:** a raw regex
   for `*p++`, `*++p` and `*(p ±` over the 26 kernel bytes returns **ZERO in all
   26**; the same regex over PHP returns **845** (census 690, the gap being
   comments/strings/dropped branches). **No built kernel walks memory with a
   pointer cursor. Every one indexes.**
2. ⚠⚠ **`str_call` — 1 of 255 (0.4 %), against 10.1–23.0 %.** The one is
   `p11-nul-scan`'s `strlen`. ⚠ **`p12-strcat-fixed` and `p13-strncpy-trunc`
   call no `str*` function at all** — the catalogue names them for `strcat` and
   `strncpy`/`snprintf`, and both kernels spell the copy out by hand.
   `p13/c/kernel.c:16` says so in its own words: *"The copy is spelled out
   rather than calling `strncpy` itself"*. **This is a disclosed design choice,
   not a discovery — but its consequence for coverage had not been measured.**
3. **Tied to (2): bound source `none`** — an operator with **no size argument at
   all** — is **2 of 255 (0.8 %)** in the tree against a per-program median of
   **15.7 %** and a max of **56.1 %**. ⚠ **This is the SAME finding as (2), not
   an independent one:** `none` comes from `strcpy`/`strcat`/`sprintf`/`strlen`.
   I am counting it once.
4. ⚠⚠ **I DECLINE THE REST OF THE BOUND-SOURCE COMPARISON, AND THE REASON IS A
   CONFOUND I CAN NAME.** The tree reads `param` **51.4 %** against 0.8–24.8 %
   in the corpora, and `const` **10.2 %** against 12.7–54.7 %. **That is a
   population artefact, not a mechanism gap: all 255 ladder sites are inside
   leaf kernels that receive `(buf, len)` from a driver, while the corpus
   population is every function in a program.** ⚠ **A comparison whose top
   category is produced by the harness architecture is not a measurement of the
   patterns, and I am not publishing one.** ⚠ **Note this also does NOT
   contradict `TASK_123`'s *"13 of 14 built destination buffers are `#define`
   capacities"* — that census counted DESTINATION BUFFERS, mine counts ALL
   SITES, and the two populations are different.**
5. ✅ **THE REVERSE GAP THE TASK ASKED FOR: THERE IS NONE, at this granularity.**
   Every operator and every bound source the built tree uses occurs in the
   corpora. **No built row's realism claim is measured negative by this census.**
   ⚠ **And the honest caveat the task demanded: check the confusion matrix
   first. `ptr_offset` and `str_call` are the two categories where the classifier
   has ZERO measured error (operator 60/60), so the two zeros above are real
   zeros. The categories with measured error — `local`, `cursor` — are not zero
   anywhere and no zero rests on them.**
6. ⚠ **What this census structurally CANNOT see, so absence here is not
   evidence:** `p38` (strict aliasing), `p47` (timing), `p18` (unbounded shift),
   `p22` (non-termination), `p27`/`p42` (temporal, allocation). **An
   operator × bound-source census is a SPATIAL instrument.** Six of the 26 built
   patterns are about something it does not measure.

---

## §E — bounds on what may be claimed

- ⚠⚠ **n = 22 PROGRAMS, of which 21 are GNU-style utilities and 1 is a 2000-era
  interpreter. Not "C".** Every sentence above carries the corpus.
- ⚠ **PHP 4.0.2 is from 2000.** Its 23 % `str_call` share is the highest of the
  22 and its `strcpy`/`strcat`/`sprintf` density is a fact about 2000-era C.
- **991 147 deduplicated lines**, 2 555 distinct files, manifested by sha256.
  The coreutils tree lives under another project's `.temp/` and may vanish; the
  manifest is what makes its numbers reproducible.
- ⚠ **The `check` table is reported and condemned in the same breath.** ⚠⚠ **No
  number here is about limb 3.**
- ⚠ **Disclosed caps, no silent ones.** Sites are counted only inside recognised
  function bodies (token coverage **php 78.3 % / coreutils 83.2 % / cgnu
  82.0 %**; the remainder is file-scope tables, prototypes, typedefs and macro-
  named function definitions). Non-selected `#ifdef` branches are dropped:
  **3 570 / 1 214 / 27 110 lines**. `#define` bodies are not scanned:
  **110 / 3 / 442** `[`. Generated files are excluded: **141 php sites,
  2 809 cgnu sites.**

---

## §F — the instrument defects in my own census

The task said to assume there was one. There were four, all caught by arms
written before any counting, plus five live-and-disclosed.

1. ⚠⚠ **`#if`/`#else` DESYNCHRONISED BRACE DEPTH AND MADE 29 % OF PHP INVISIBLE
   — this is the big one.** `main/fopen-wrappers.c` ends at brace depth **+3**
   and `cpio/gnu/nstrftime.c` at **−2**, because both branches of every
   conditional survive directive stripping. With a global depth counter, **every
   function after the skew is silently dropped**: `fopen-wrappers.c` reported
   4 functions and 3.1 % coverage; `php_mysql.c` 6.5 %; `hg_comm.c` 1.6 %.
   Fixed twice over — conditionals are now resolved to one configuration, **and
   the depth counter is gone entirely** (function bodies are found by local
   brace matching with span suppression, which cannot desync). Coverage
   **70.9 % → 78.3 %**. ⚠ **This is the project's most-named failure class
   verbatim: a detector that is not running looks exactly like a detector that
   found nothing.**
2. **K&R function definitions produced ZERO sites.** Caught by self-test arm
   `t3` before any corpus run. PHP 4.0.2 and gnulib both contain them.
3. **`_stmt_start` was a stub returning `i-40`**, so any comparison within 40
   tokens counted as a check at the site. Caught by arm S14 (`if (n < CAP) { }`
   followed by an unguarded `gbuf[n]`).
4. **`*(T *)(p + e)` produced an empty bound expression.** Caught by arm S18.

**Live and disclosed** (5–7 are the measured error rate, not bugs to fix):
5. A **const-index** site has no identifiers in its bound expression, so `check`
   is forced to `none` — **6 of the 15 `check` disagreements**.
6. **`*p++` is `cursor` by construction** — 2 of the 6 `bound` disagreements.
7. **Root-identifier matching cannot tell a local `nranges` from a field
   `cset->nranges`** — 3 more `check` disagreements.
8. **Generated files: recall 0** → excluded from the published population.
9. **Dropped `#ifdef` branches and unscanned macro bodies** → counted above.

---

## Problems

- **The `check` field is dead.** I could rebuild it (track `switch` discriminants,
  propagate constant indices against the declared array extent, use the innermost
  *enclosing block* rather than the innermost conditional) but that is a second
  task, and shipping the measured 75 % with its confusion matrix is the honest
  cheap outcome the task authorised.
- **`local` is a bucket, not a category.** 43 % precision. Chasing it needs
  intra-procedural dataflow. **This is the manager's least-sure #1 and it stands:
  a source-level census can classify the source of the bound only when the bound
  is written at the site.**
- **The ladder's bound-source column is confounded by the kernel/driver split**
  and I did not publish it. The operator column is not confounded and I did.
- coreutils as specified is **18 862 lines**, too small to be a control on its
  own; the c-gnu corpus is what carries §C.

## Unsure / not done

- **I did not hand-check a sample from coreutils or c-gnu.** The 90 %/100 %/75 %
  figures are measured **on PHP only**. The classifier is corpus-independent
  code, but PHP's macro density is unusual and the error rate could differ.
  **If one number in this report needs a second measurement, it is that.**
- **I did not verify that `is_generated` catches every generated file** — it
  fires on the two the recall sample found, and it flags 141 php + 2 809 cgnu
  sites, but I have no independent enumeration of generated files.
- **Site 23's hand label rests on a loop I read separately** (`ii.c` `for(k=1;
  k<=j;k++)`), not on the sample window; sites 6 and 38 likewise. All three are
  cited in `hand_labels.tsv`.
- **Three c-gnu programs fall below the 300-site floor and are in the corpus
  totals but not the per-program table**: `pth-2.0.7` 291, `ed-1.19` 223,
  `hello-2.12.1` 4. **`gawk-5.2.2` contributes 0 rows because all 91 of its `.c`
  files are byte-identical to `depregawk-5.2.2`'s and were deduplicated away —
  the `depregawk-5.2.2` row IS gawk.** So the per-program table is
  **20 c-gnu + php + coreutils = 22**.
- **I did not attempt limb 3 and no number here bears on it.**
- I did **not** build, propose, or rank any pattern, and I draw no
  build/stop conclusion.

## Memory updates

**None** — `.memory/` is manager-only and rule 9 applies: this is unreviewed
engineer work. Everything durable is in `.temp/t129/` (`NOTES.md`, `census.py`,
`hand_labels.tsv`, `recall_adjudication.md`, `agree.txt`, `rank.txt`,
`perprog.txt`, the three `*.manifest`, `REBUILD.sh`).
⚠ **The manifests are the artefact the task asked to be committed** (956 K
total, `.temp/` is gitignored, so promoting them is the manager's call).

---

⚠ **PROTOCOL rule 2's running count.** This task was launched from **583** and
`TASK_127`/`TASK_128` carry it concurrently; **reconciliation is the manager's
job, not mine.** What I add: **four instrument defects in my own census** (one
of which hid 29 % of the primary corpus), **one pre-dedup figure corrected in
the manager's own task file** (coreutils 56 873 → 18 862 lines), **one corpus
the file list had not been characterised for** (785 480 lines), and **one
measured field declared unusable rather than published** (`check`, 75 %).

**The call I am least sure of, and I want it attacked:** ⚠⚠ **that hand-labelling
`bound` SEMANTICALLY (tracing one assignment) rather than by the classifier's own
syntactic rule is the right comparison.** It is why `local` scores 43 % instead
of 100 %. **I chose it because a syntactic self-comparison would have measured
nothing** — but it means the 90 % figure is a statement about the *label set*,
not only about the *code*, and a reviewer could reasonably say the honest number
is *"the classifier implements its definition perfectly; the definition is what
is 43 % useful for `local`"*. **Both readings are in `hand_labels.tsv`; the raw
disagreements are listed so either can be recomputed.**
