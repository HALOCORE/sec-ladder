# TASK_171 REPORT — the closing review. The reframing FALLS, and `SYNTHESIS.md` is not safe to publish as it stands.

**Role: research reviewer.** Adversarial. **Nothing was fixed.** Scratch:
`.temp/t171/`. No earlier `.temp/t*/` or `.temp/mgr*/` was modified. **No
`git add`, no `git commit`, no history-mutating git.** `harness/asm.py` was
**imported read-only and never modified**. No sweep, no re-measure, no
callgrind run, no `outward_ir.json` re-emit — none was needed.

```
$ git status --porcelain | wc -l
0
```

---

## HEADLINE

0. ⚠⚠⚠ **THE CALL NAMED FOR ATTACK FALLS.** The withdrawal of *"not every
   rung's cheapest admissible spelling has been searched"* is the flattering
   direction. `14/0/0` says every row's search state is **documented**; the
   withdrawn sentence was about **depth**. Adjudicated against the fourteen new
   entries themselves, **13 of 33 rows declare an unsearched, fiat or owed
   UNSAFE endpoint** (14 counting `p09`). The honest correction to *"the unsafe
   side is unsearched on most patterns: 14 of 33"* is **`most` → `39%`, and
   14 → a different 13** — not 14 → 0, and not *"four named levers"*.
1. ⚠⚠⚠ **A RETIREMENT REASON IS FALSE AGAINST THE SHIPPED TREE.**
   `results/SYNTHESIS.md:1566` publishes *"**No pattern ships a
   length-HETEROGENEOUS sweep band**"* as a priced, deliberate omission.
   **`patterns/p06-rotate/inputs/gen.py:62` cites that queue item BY NAME as its
   motive and `:135-137` hard-asserts that `small` IS length-heterogeneous**;
   p10 ships `sweep-h1/h2/h3.bin`; p14, p18, p22, p23 the same. And
   **`RECAP.md:6592-6596` already says so**: *"p06 shipped the first
   **length-heterogeneous** fit set (old item 11) … **Both retired.**"*
2. ⚠⚠ **THE `§` CENSUS CANNOT SEE AN INLINED `rep`, AND THAT SETTLES `p27`
   AGAINST THE MANAGER.** `TASK_169` is right and the census does not test it:
   `p27 c-gcc`'s `rep stos %rax` is **inside `<kernel>`** and `p27 c-clang`'s
   counterpart is **18 `movaps` + 1 `xorps` = 19**, both inline, **neither a
   callee edge**. `RECAP` 66(b)'s stated reason — *"its contribution is small
   and both sides may sit in one regime"* — is **a mechanism supplied for a null
   result**, and it is wrong on its own terms (13 `Ir` of a published `−25.02`
   is 52%).
3. ⚠⚠ **THE FOURTH UNEARNED `✅` EXISTS — TWO OF THEM.** *"the marked set is
   **DERIVED**, not listed"* is a list: `BULK_REGIME` is three hardcoded keys,
   two of them **bare glibc load addresses**, with **two more glibc bulk
   routines unclassified in the same sidecar** and, on `gcc-clang` pairs, a
   **compiler-dependent key space**. And *"the honest statement … runs AGAINST
   this project's usual error direction"* is an editorial judgement marked
   `✅ manager re-derived`, and it is false in the direction it claims.
4. ⚠ **BOTH OF ITEM 43's ACCUSATIONS VERIFY.** `p01 safe_tuned -O0 isolated`:
   the real kernel is **41 instructions, 0 back edges, 0 bulk calls**; the
   `Iterator::fold` window measured instead has **4 back edges** —
   `check.py:3010` fails exactly that condition, so the green is masked.
   `p05/NOTES.md` §1a: `verus::main` carries **exactly the two `xmm`
   instructions §1a says it lacks**, so the invented mechanism is confirmed
   invented. **Neither correction was landed at `d6aa844`, and
   `.memory/01-ladder.md:917` still instructs *"Quote the 23/32."***
5. ✅ **ITEM 2 SURVIVES INTACT — I could not break the pin.** `0 of 33`,
   **4272 measured leaves byte-identical**, the determinant set **exactly equals
   the tree's** on all 33, and four separate attacks on `is_build_determinant`
   missed.

---

## Per-item verdicts

| item | verdict |
|---|---|
| 1 — the `§` regime census | **SURVIVES, NARROWED** (the mark is right; the evidence string and the completeness claim are not) |
| 1b — the `p27` disagreement | **`TASK_169` STANDS; the census does not test it; the manager's reason FALLS** |
| 2 — the build-determinant pin | **SURVIVES** (re-derived on every clause) |
| 3 — the 14 search-state entries | **SURVIVES, NARROWED** — the four promoted numbers hold; two published counts around them do not |
| 4 — the retirement's reframing | **FALLS** |
| 4b — the retirement's count | **FALLS** (item 43 double-counted) |
| 4c — the retirement's reasons | **ONE FALSE** (length-heterogeneous band), **ONE MIS-STATED** (item 5) |
| 5 — what the manager overstated | **TWO unearned `✅`, one un-re-derived `✅`** |
| 6 — item 43's accusations | **BOTH VERIFIED** |

---

## 1. THE `§` REGIME CENSUS — the mark is right, the evidence string is not

### 1a. What the SECOND spelling misses

**(i) An inlined `rep` is structurally invisible, and that is not a corner
case — it is how the marked row's own gcc side works.**
`regime_crossing` (`synthesis/synthesize.py:1094-1141`) reads
`outward_by_callee_per_call`. An inlined `rep stos` produces **no callee edge at
all**. Verified on the marked pattern:

```
$ objdump -d .temp/build/p08/c-gcc-O3-isolated | awk '/^[0-9a-f]+ </{fn=$2} /rep stos|rep movs/{print fn": "$0}'
<kernel>::  19e8: f3 48 ab   rep stos %rax,%es:(%rdi)     (mov $0x200,%ecx at 19db -> 512 Ir)
<kernel>::  1acd: f3 48 a5   rep movsq %ds:(%rsi),%es:(%rdi)
```

So `p08 gcc-clang` is marked **only because clang calls out**. The census would
have been silent on a pair where *both* sides inline.

**(ii) The routine SET is a hand list of three, two of them bare glibc load
addresses.** `synthesize.py:1075-1082`:

```python
BULK_REGIME = {
    "0x0000000000189480": ("glibc `memset` …", 300.0, 4000.0),
    "0x0000000000188a80": ("glibc `memmove` …", 852.0, 8192.0),
    "__rustc::__rust_alloc_zeroed": (…, 300.0, 4000.0),
}
```

Nothing arms its completeness. **Two more glibc bulk routines are in the same
sidecar and unclassified**, identified here by disassembling the pinned libc
(the same route `.memory/03-measurement.md` used for the other two):

```
$ objdump -d --start-address=0x188080 … /lib/x86_64-linux-gnu/libc.so.6
  vpbroadcastb %xmm0,%ymm0 ; vpcmpeqb (%rdi),%ymm0,%ymm1 ; cmp $0x20,%rdx   -> __memchr_avx2
$ objdump -d --start-address=0x18b7c0 …
  vpxor %xmm0,%xmm0,%xmm0 ; vpcmpeqb (%rdi),%ymm0,%ymm1 ; tzcnt             -> __strlen_avx2
```

and they contribute **asymmetrically across published `gcc-clang` rows**
(`.temp/t171/callee_census.py`):

```
  p11 small gcc-clang  __strlen_avx2 (UNCLASSIFIED):  -2105.03 Ir   §marked=False
  p11 large gcc-clang  __strlen_avx2 (UNCLASSIFIED):  -1355.38 Ir   §marked=False
  p12 small gcc-clang  __memchr_avx2 (UNCLASSIFIED):   -143.37 Ir   §marked=False
  p12 large gcc-clang  __memchr_avx2 (UNCLASSIFIED):   -590.54 Ir   §marked=False
  p13 small gcc-clang  __strlen_avx2 (UNCLASSIFIED):   -182.00 Ir   §marked=False
  p13 large gcc-clang  __strlen_avx2 (UNCLASSIFIED):   -336.00 Ir   §marked=False
```

They probably would not clear the regime test (neither AVX2 routine has an ERMS
byte-wise path) — **but that judgement has not been made anywhere.** Their
absence from the dict is silence, not a decision, and the marker's own defence
against the first spelling was *"a name regex misses every one"*. **An address
list misses every routine whose address is not in it, and it will also miss all
three if glibc is ever bumped — silently, returning `{}`, which is the
flattering answer again.**

**(iii) ⚠⚠ ON A `gcc-clang` PAIR THE ASYMMETRY INPUT IS SYMBOL RESOLUTION, NOT
WORK — and this is the finding.** gcc-built cells report their libc callees
under the **client's own PLT address** (`0x400xxxx`); clang-built cells report
the **libc** address. Demonstrated on the marked pattern itself:

```
=== p08 callees per cell (small)
  c-clang      0000188a80=196.81(39.4/c)   0000189480=4112.84(4113.0/c)
  c-gcc        0004001160=156.00(39.0/c)
```

`0x188a80` **is** `BULK_REGIME`'s `memmove`. `c-gcc` carries the *same routine*
at *the same rate* (39.0 vs 39.4 `Ir`/callee-call — the delta is the extra
thunk), under a different key. `regime_crossing` therefore computes the memmove
asymmetry as **`196.81 − 0.00 = +196.81`**, clears the `2.00` floor, and is
saved from a spurious mark only by the regime test. **The evidence string it
would have printed is the one it does print on `memset`:**

> `synthesize.py:1137-1138` — *"while the other side does not call it at all"*

**That sentence is generated from a key space in which the other side never
calls anything the dict knows about.** On `memset` it happens to be true (I
verified gcc inlines it, above). On `memmove` the identical sentence would have
been false. The census got the right answer on `p08` **for a reason it did not
establish**.

Confirming the same split on three more patterns:

```
=== p13 small
  c-clang  0000188a80=190.0  0000189480=143.0  000018b7c0=182.0
  c-gcc    0004001150=208.0
$ objdump -d --disassemble=kernel .temp/build/p13/c-gcc-O3-isolated | grep -oE 'call.*<[^>]+>'
  call 1150 <strlen@plt> ; call 1160 <__stack_chk_fail@plt>
$ … p13/c-clang-O3-isolated
  call 1060 <strlen@plt> ; call 1080 <memset@plt> ; call 10c0 <memcpy@plt>
```

### 1b. ✅ CLEAN NEGATIVES on the marker (attacks that did **not** land)

* **A symmetric byte-wise pair.** p08's four Rust cells all carry `memset` at
  **4113.00** exactly, so the term cancels out of `R2−R4`, `R3−R4`, `R5−R4` to
  the hundredth. **Not marking them is correct**, and a symmetric byte-wise pair
  is *not* additionally incomparable: the published quantity is a difference and
  the difference is clean. Verified in the cell dump above.
* **A contribution just under 2.00.** On this data a byte-wise routine
  contributing `< 2.00 Ir`/call would have to be invoked once per ~2000 kernel
  calls; no such row exists. The floor is benign here.
* **A PLT thunk hiding a marked routine.** The largest unclassified callee in
  the whole sidecar is `0x15220`, **46 cells / 12 patterns, up to 4828 `Ir` per
  callee call** — which disassembles in `ld-linux-x86-64.so.2` to
  `_dl_runtime_resolve_xsavec` (`and $0xffffffffffffffc0,%rsp`, `mov $0xee,%eax`
  = xsavec). It is the **lazy-binding resolver**, one-shot
  (`calls/kernel-call = 4e-05`), correctly not a bulk routine. **This attack
  missed.**

### 1c. ⚠⚠ THE `p27` DISAGREEMENT — VERDICT: `TASK_169` STANDS

```
$ objdump -d .temp/build/p27/c-gcc-O3-isolated | awk '/^[0-9a-f]+ </{fn=$2} /rep stos/{print fn": "$0}'
<kernel>::   1a2e: f3 48 ab   rep stos %rax,%es:(%rdi)      (mov $0x20,%ecx at 1a22 -> 32 Ir)

$ objdump -d .temp/build/p27/c-clang-O3-isolated  (kernel window, 164 lines)
$ grep -cE "movaps|xorps"   ->  19        # 18 movaps + 1 xorps, zeroing the same buffer
```

`TASK_169`'s `32` vs `19` reproduces **exactly**, and `13 / 25.02 = 52%` of the
published `p27 gcc-clang` small figure. **Both spellings are inline, so neither
appears in `outward_by_callee_per_call` and `regime_crossing` is structurally
blind to the entire claim.** Non-marking is therefore **not evidence**, and the
`OPEN` disposition is the right disposition — but for a reason the record does
not give.

⚠⚠ **`RECAP.md:6191-6193` supplies one that is wrong**: *"its contribution is
small and both sides may sit in one regime"*. It is **52% of the row**, and the
regime question never arises because there is no callee to price. **This is the
same failure class `TASK_170` reported against `p05/NOTES.md` §1a in the same
report — a mechanism invented for a null result — committed one day later by the
agent who reported it.**

### 1d. Does marking `p08` change anything §2 or §7 says? — **No**, and the two accounts are consistent

* p08's **rung** pairs are correctly unmarked (all four Rust cells at 4113.00).
* `results/SYNTHESIS.md:149`'s *"p08 is LICENSED at 5409.88 Ir/call outward"* is
  about `R3−R4`; unaffected.
* ✅ **The direction is consistent with `.memory/`** and I attacked it and
  missed: §1's *"`Ir` charges most where the machine charges least"* looked like
  an `ns` claim with no `ns` evidence, but `.memory/03-measurement.md:417-421`
  carries the measurement — *"`Ir` therefore says c-gcc is **33% cheaper** than
  c-clang while wall clock says it is **dearer**"*, p08-specific, with the
  mechanism. **Clean negative.**
* ⚠ **but the promotion dropped a caveat the digest keeps.**
  `results/synthesis.md:314` quotes the zero-fill probe and says *"that probe is
  TASK_074's and `.memory/` marks it **PROVISIONAL, not yet reviewed**"*.
  `results/SYNTHESIS.md:152-160` — the hand-written argument, the file a reader
  reads — states the mechanism flat, with no provenance and no `PROVISIONAL`.
  **minor**, but it is a rigour downgrade on promotion.

### 1e. ⚠⚠ AND THE RETRACTED SENTENCE IS STILL LIVE AT `HEAD`, THIRD REVIEW RUNNING

`.memory/03-measurement.md:541-543`:

> *"p01, p05, p16 and p17 call no bulk routine at all. **Only p08's gcc kernels
> contain a `rep` instruction**, so no previously published `Ir` comparison is
> contaminated."*

Its own retraction is **64 lines above it** (`:477-479`: *"26 of 1052 measured
windows, across NINE patterns"*), and the new `§` mark lands on the published
row it says cannot exist. `TASK_169` Problem #1 reported it; `TASK_170` Problem
#15 reported it again as *major, manager-owned*; **it is unchanged at `HEAD`.**
`PROTOCOL` rule 9 asks for a `DISPUTED` annotation, not a deletion.

---

## 2. THE BUILD-DETERMINANT PIN — **SURVIVES**, and four attacks missed

### 2a. `0 of 33`, re-derived (`.temp/t171/pin_recheck.py`)

```
=== (a) pin status, today's tree
    entries: 33  STALE: 0 of 33
    determinants per pattern: [13] total 429
```

### 2b. Not one measured value moved (`d6aa844^` → `HEAD`)

```
patterns before/after: 33 33 same keys: True
EVERY per-input subtree identical: True
measured leaves compared: 4272
non-measured keys BEFORE: ['gate_source_sha256']
non-measured keys AFTER : ['derived_from_sha256','gate_source_sha256_at_emit','input_sha256','pin_note']
gate map preserved verbatim on all 33: True
derived_from_sha256 values all from the emit-time map: True
```

### 2c. `--emit` no longer reverts the re-pin

`synthesis/outward_ir.py:571-580`: `json.dump(doc, …)` is followed by
`rc = repin(a.emit); return rc`. **One code path decides the pin.** I did **not**
run `--emit` (352 callgrind runs, out of scope); this is a code read and is
stated as one. The `--repin` half I did exercise, via 2b.

### 2d. ⚠⚠ ATTACKING `is_build_determinant` — the set is COMPLETE, and here is the check

Not asserted from the docstring — compared per pattern against the tree:

```
$ python3 -c "…compare derived_from_sha256 against patterns/<p>/*.rs + c/* + the 5 shared…"
patterns with a discrepancy: 0 of 33
determinant-count histogram: {13: 33}
```

Four ways I tried to find something the pin misses, **all four missed**:

1. **A rung source that `#[path]`-includes a file outside the pin.** Every
   `#[path]` in every rung source resolves to `../../common/driver.rs`, which
   **is** pinned (`grep -rn '#\[path' patterns/*/[a-z_]*.rs`).
2. **A C kernel that `#include`s something outside the pin.** The complete
   census of local includes across all 131 `c/*.{c,h}` is
   `98 × "kernel.h"`, `66 × "driver.h"` — **both pinned**.
3. **A config file `build.py` reads.** It reads none;
   `grep -nE 'open\(|json.load|read_text' harness/build.py` is empty and its
   imports are stdlib only. The flags are literals.
4. **An EMPTY pin reading FRESH.** `repin`'s `gate = d.pop(…) or d.get(…) or {}`
   can yield `{}` for a pattern with no gate record, and
   `outward_pin_status` iterates an empty dict and returns no reasons — but
   `calibrate` computes `s["unpinned"]` as *"has no `derived_from_sha256`"*
   (`synthesize.py:1382-1385`) and the publisher branches on
   `if cal["stale"] or cal["unpinned"]` (`:1797`). **An empty pin cannot print
   `FRESH`.**

Residual, both already disclosed and neither a defect: no toolchain or valgrind
version is in the pin (a rustc bump would redden the gate's `md5_fn` first); and
the blob pin for `p02 p05 p07 p11 p17` starts at `TASK_170`, disclosed at
`results/synthesis.md:216`.

---

## 3. THE FOURTEEN SEARCH-STATE ENTRIES

### 3a. ✅ The four promoted numbers all check out **numerically**

| promoted claim | verdict |
|---|---|
| `p16` `+27/+77 → −199/−2545` | ✅ both numbers verbatim in **both** cited artefacts (`p16/NOTES.md:215`, `:1363`; `.memory/01-ladder.md:813-814`) |
| `p09` 65× span `+263…+16992` vs `+13756` | ✅ **and "65×" is the artefact's own word** (`p09/NOTES.md:1132`); the cleanest of the four |
| `p14` *"overstates by 88.9%"*, `+425 → +225` | ✅ verbatim at `p14/NOTES.md:1064-1067`; `425/225 = 1.8889` |
| `p42` sign flip, cheaper rung shipped | ✅ `p42/NOTES.md:1388-1389` (*"The sign flips"* is the artefact's own phrase) and `:1316` `✅ SHIPPED` |

### 3b. ⚠ `p16`'s *"the SIGN FLIPS"* is a **derived label promoted as a quotation**

Neither cited artefact frames it that way — they say *"negative on all 24
blobs"*. `p16/NOTES.md`'s **only** occurrence of the phrase is `:1072`,
**denying** one on a different axis (*"**No sign flips.** TASK_016_REVIEW M1 …
report these two C rows as 'the sign flips'; re-measured at TASK_017 they do
not"*), and `.memory/01-ladder.md`'s p16 finding contains no *"sign"* at all.
The label now sits in `results/SYNTHESIS.md:1515-1516`, `RECAP.md:24` and
`RECAP.md:6170-6171`. **The arithmetic is right; the attribution is not.**
`minor`, but on a pattern whose own file retracts that exact phrase.

### 3c. ⚠⚠ **major — `results/synthesis.md:809` says SEVEN and lists SIX**

> *"**Seven of the fourteen** name their own weaker endpoint (p02, p14 and p27
> have an unsearched R4 or R2 side; p09 and p19 rest on a review that
> re-measured one side; p46's widths are an unreviewed re-measure)"*

Six patterns. And it omits the **two most explicit declarations among the
fourteen**: `p18` (*"⊘ The R4 side is **NOT searched, declared**"*,
`synthesize.py:447`) and `p38` (*"the R4 side is disclosed but **NOT
established**, and it flatters SAFE"*, `:527-528`). The sentence is a
**hardcoded string inside a generated file** (`synthesize.py:2791-2794`) — the
exact *type-it-don't-derive* defect `TASK_170` fixed **one paragraph above it**
(`n_undecl`, difference-of-lengths → set difference) and whose confession is in
the same block. **It undercounts, in the flattering direction.**

### 3d. ⚠⚠ **major — three entries cite the BACKLOG as their "reviewed artefact", and the split counts them as searches**

```
"p01": ("R3 span OWED",                       "RECAP 'Owed' 3: p01 and p08 owe an in-contract R3-side span")
"p03": ("… the +5 constant NEVER searched",   "RECAP 'Owed' 2")
"p08": ("R3 span OWED",                       "RECAP 'Owed' 3")
```

`RECAP.md:6795` and `:6802` are **open backlog items** — outstanding work, not
reviewed measurements. Against that, `results/synthesis.md:807` publishes:

> *"every entry cited to a **reviewed** artefact — except one, `p06`"*

**False on three rows.** And `n_found` is a residual —
`len(SEARCH_REVIEWED ∩ meas) − len(SEARCH_NONE)` (`synthesize.py:2765`) — so
anything not explicitly listed in `SEARCH_NONE` is counted as *"reports a SEARCH
RESULT"*. **`p01` and `p08`, whose entries say the span is OWED, are inside the
published `30 report a SEARCH RESULT`.** Same failure shape and same direction
as the `n_undecl` defect fixed in the same task.

⚠⚠ **And the same document retires `p03`'s `+5` and `p01`/`p08`'s R3-side span
as OPEN GAPS at `results/SYNTHESIS.md:1561-1565` while counting those three rows
among the thirty that "declare a search that was reviewed".**

### 3e. `minor` — `p42`'s entry quotes a count the section it cites contradicts

`synthesize.py:541` gives the shipped do-while as *"`15 verified, 0 errors`"*
citing §9/§9a. `p42/NOTES.md:1114` (§9a) gives **`18 verified, 0 errors`** for
`r4_ship` and 15/0 for `r4_idxfold`, **the rung it replaced**;
`p42/NOTES.md:876` records *"Both counts rose by 3 at TASK_110 — they read 15
and 18."* Pre-`TASK_110` count against a post-`TASK_110` section.

### 3f. `p42`'s entry and `p42`'s `§` marker — **different cells, not in conflict**

The marker is `p42 large **R2−R4**` (`__rust_alloc_zeroed`'s fill, 4342.00
`Ir`/call, byte-wise on `safe_naive`). The search entry is about **R3/R4**
spellings and `R3ship − R4ship`. Consistent, and `§` being per-blob (`small`
189.01 `Ir`, forced vector, unmarked) is the clearest thing in the whole
mechanism.

---

## 4. THE RETIREMENT — **the reframing FALLS**

### 4a. ⚠⚠⚠ VERDICT: FLATTERING. `14/0/0` is about DOCUMENTATION; the withdrawn sentence was about DEPTH.

`results/SYNTHESIS.md:1501` — *"A STRUCTURAL GAP THIS DOCUMENT PUBLISHED FOR 62
TASKS **DOES NOT EXIST**"* — and `:1546-1554` — *"that framing is **WITHDRAWN**…
What remains is four *named* levers nobody has run."*

Adjudicated from the entries' **own words** (`.temp/t171/unsafe_endpoint.py`):

```
UNSAFE (R4) ENDPOINT UNSEARCHED / FIAT / OWED, in the entry's own words: 13 of 33
  p01  'R3 span OWED'; no R4 statement; cites RECAP 'Owed' 3
  p02  '⚠ The R4 side is explicitly UNsearched, so +6 is an R3-side bound'
  p03  '… the +5 constant NEVER searched'; no R4 statement; cites RECAP 'Owed' 2
  p06  '⊘ PROVISIONAL -- R3 searched at review'; no R4 statement; not twice-checked
  p08  'R3 span OWED'; no R4 statement; cites RECAP 'Owed' 3
  p14  '⚠ The R4 side was never searched' / 'the R4 endpoint is fiat'
  p17  'It is an R3-SIDE bound with R4 held by fiat'
  p18  '⊘ The R4 side is NOT searched, declared'
  p25  'R3/R4 rung spellings … still unsearched'
  p28  R2-vs-R3 only; 'publishes NO rung-to-rung cost … the absence is declared'
  p29  '⊘ NO SEARCH, declared -- NEITHER side searched'
  p32  '⊘ NO SEARCH, declared -- NEITHER side searched'
  p49  '⊘ NO R3-SIDE SPREAD -- only ONE in-contract R3 spelling built'
BORDERLINE (would make it 14):
  p09  headline 'R4 searched and degenerate', body: 'neither candidate had a Verus
       twin BUILT … the review names its own limit: … nor re-search R4'
```

**So:**

* the withdrawn sentence's word **`most`** was wrong — it is **39%**, not a
  majority. That is the honest correction, and it is worth making.
* the withdrawn sentence's **claim** was not. **13 of 33 rows still declare an
  unsearched, fiat or owed unsafe endpoint**, which is materially the same
  magnitude as the `14 of 33` that was withdrawn, arrived at by reading rather
  than by counting dict keys.
* **`"What remains is four named levers"` understates by an order of
  magnitude.** The four levers are `Owed` 1, 2, 3 and 11. The unsearched R4
  sides of `p02 p14 p17 p18 p25 p28 p29 p32 p49` are **not among them** and are
  named nowhere in the subsection.
* **`§7` never tells the reader the number.** `§2`'s rewrite at `:554` does say
  *"Read each row's stated search state; the count says nothing"* — but the 33
  entries are rendered in `results/synthesis.md`, **not** in the file the reader
  is reading.

**The honest replacement sentence exists and is short:** *"the search state is
now documented on all 33 rows, and on 13 of them the documentation says the
unsafe endpoint was never searched."* **That is narrower than the old claim and
it is still a limitation.** What is published instead is a boast.

### 4b. ⚠⚠ **blocker — a retirement REASON is false against the shipped tree**

`results/SYNTHESIS.md:1566-1569`:

> *"**No pattern ships a length-HETEROGENEOUS sweep band**, which makes every
> natural step basis singular … Whoever next hits a size-dispatched library
> routine needs this."*

```
$ sed -n '58,66p' patterns/p06-rotate/inputs/gen.py
small AND large: DIFFERENT RESIDUES, AND small IS LENGTH-HETEROGENEOUS
`.memory/03-measurement.md`'s queue item 11 says no pattern ships a
length-heterogeneous band. p06's records carry their own `nelem`, so the natural
place is here:
  * `small`: 5 records, `nelem` 13/47/29/61/7 -- five DIFFERENT lengths in one

$ sed -n '132,137p' patterns/p06-rotate/inputs/gen.py
    if len(set(sm)) < len(sm):
        bad.append("small is not length-heterogeneous; its whole point is that "
                   "every record has a different nelem (queue item 11)")
```

**p06's generator cites the item by name and hard-asserts the opposite.** Same
construction in `p14/inputs/gen.py:92,172`, `p18/inputs/gen.py:106,179,420`,
`p23/inputs/gen.py:176`; `p10/inputs/gen.py:43,239` documents band `h` as
*"LENGTH-HETEROGENEOUS"* and **ships `sweep-h1.bin`, `sweep-h2.bin`,
`sweep-h3.bin`**; `p22/controls/sweep_ir.py:94` fits *"the three
length-heterogeneous `sweep-h*` blobs"*.

And **`RECAP.md` already knew**, 376 lines above the item it copied:

```
$ sed -n '6592,6596p' RECAP.md
**Closed by p06:** the two-step reslice (old item 1) is now measured on a sixth
pattern at **exactly −1.00 Ir/call**, and p06 shipped the first
**length-heterogeneous** fit set (old item 11), whose leave-one-`m`-out **can
fail** — it misses by −48.000 at `m=3`, which is how the domain got established.
Both retired.
```

versus `RECAP.md:6968-6969` (item 11's body): *"… **and no pattern has one**."*

**This is `PROTOCOL` rule 13 — header/body rot — escaping the queue and being
published in `results/` as a priced, deliberate omission.** The salvageable core
is the narrow one item 11 itself states (*"p13's fit blobs are all
length-homogeneous"*, `RECAP.md:6969`) plus the forward-looking sentence. **The
universal quantifier must go.**

### 4c. ⚠ **major — item 5 is retired with the reason its own item calls the wrong one**

`results/SYNTHESIS.md:1602-1604`:

> *"The gate's `harness/*.py` glob is over-broad — `measure.py` is hashed into
> gate records and is not executed by the gate. **Argued and declined**; the
> cost of narrowing it is borne by every future harness edit either way."*

`RECAP.md:6875-6880`:

> *"ARGUED AND DECLINED at TASK_077 — leave the glob alone, and **the item's own
> TEST is the wrong test.** It asks *"does the gate execute it?"*; the right
> question is **"does a committed claim depend on it?"** — `limbs.py`,
> `report.py` and `measure.py` are cited in **64 committed doc references**, and
> `harness/limbs.py:14-19` already decided it."*

**The subsection republishes the refuted framing as the finding and drops the
actual argument.** This project's own record is that *a refusal's REASON is what
gets reused*; a reader picking item 5 back up gets the wrong question.

### 4d. ⚠ The count — 44 is right, but item 43 is counted twice

```
$ awk 'NR>=6609' RECAP.md | grep -cE "^[0-9]+\. "
44
$ … | grep -oE "^[0-9]+\." | tr -d '.' | sort -n
0 1 2 … 43        (contiguous; no letter-suffixed items exist)
```

`44` ✅ — **but only because the list starts at 0**, which the sentence does not
say, and `16b` is half of one item, so *"sixteen closed"* is fifteen items and a
half. The arithmetic defect is item **43**:

> *"…and **investigated a seventeenth (43)**. The five headings above retire
> **eleven more** (1, 2, 3, 11; **43**; 7, 8, 9; 5, 20; 25)."*

Heading (2) **is** item 43. Claimed `16 + 1 + 11 = 28`; **distinct = 27**; the
word *"more"* makes the double-count explicit. Implied remainder 16, actual 17.
**In a sentence whose own preamble says *"DERIVED rather than asserted — the
first version of this sentence invented one."***

### 4e. Minor retirement losses (each verified against `RECAP`)

* item 2 retired at **half width** — the *"one unreviewed measurement"* half
  (`RECAP.md:6795-6797`) is dropped; only the `+5` survives.
* item 3 retired at half width — the *"never the word 'minimum'"* half
  (`RECAP.md:6804-6805`) is dropped.
* item 20 drops *"and rule 5's accident test has not been run on it"*
  (`RECAP.md:7218-7220`).
* item 28 is listed among *"closed sixteen with a run"* while `RECAP.md:6048-6050`'s
  own finding headline says it **DID NOT CLOSE**.

### 4f. ✅ The retirement reasons I attacked that **held**

* *"the two-step reslice … mechanism is register allocation, so no prior
  spelling search ran it"* — `.memory/01-ladder.md:537-549` carries the
  mechanism and the instruction listing. **Held.**
* *"p03's `+5` per-call constant has never been searched at all"* — **held**
  (`p03/NOTES.md:1263-1269`).
* *"`vparse.impl_spans` refuses any `impl` whose preceding character is not
  `{};`"* — **held, exactly**: `harness/vparse.py:404-407`, and `:492-500` names
  it as `impl_spans`' documented LIMIT 2.
* *"p15 … a verified UTF-8 validator, `5 verified, 0 errors`, ZERO trusted
  items"* — **held** (`.tasks/TASK_085_REPORT.md:26,331-332`).
* *"Both pair intervals this project ever published were built from R4s that are
  not rungs"* — **held**, with a caveat worth carrying: `p03` has a
  non-degenerate pair interval whose R4 endpoints verify `9 verified, 0 errors`
  at zero new TCB and are excluded by **judgement**, not by the prover
  (`.memory/01-ladder.md:196-203`, `p03/NOTES.md:1232-1249`).

---

## 5. WHAT THE MANAGER OVERSTATED — the fourth exists, and so does a fifth

`RECAP.md:6155-6233`, finding 66. Legend: *"✅ = manager re-derived, ⊘ =
engineer's alone."*

| `✅` mark | verdict |
|---|---|
| *"Final gate: 30 PASS + 3 PASS-WITH-BLOCKED-ROWS … `p01` 1 / `p35` 3 / `p42` 1"* | ✅ **EARNED** — reproduces exactly from the 33 records |
| *"The column now reads `undeclared` on ZERO of 33"* | ✅ **EARNED** — `undeclared: 0 of 33 []` |
| *"No discount factor is published"* | ✅ **EARNED** — the only `90%` in either file is the withdrawal quoting itself |
| *"it cost NO callgrind run … the old key was never one hash but the whole MAP"* | ✅ **EARNED** — re-derived here (§2b) |
| *"Now a row in `PROTOCOL` rule 6"* | ✅ **EARNED** — `.tasks/PROTOCOL.md:355-363` |
| ⚠⚠ *"the marked set is **DERIVED rather than listed**"* | ⚠ **NOT EARNED** |
| ⚠⚠ *"The honest statement is narrower and runs AGAINST this project's usual error direction"* | ⚠ **NOT EARNABLE, and false** |
| *"Every new check has must-fire arms **SEEN TO FAIL** — 12, 16, 7, 15, 5"* and *"seen to take the module down AT IMPORT"* | ⚠ **not re-derivable from a passing selftest** |

**On *"DERIVED rather than listed"*.** The marked **rows** are derived. The
**routine set** is a three-entry hand-maintained dict keyed on two bare glibc
load addresses (§1a(ii)), with two more glibc bulk routines unclassified in the
same file, and on `gcc-clang` pairs a compiler-dependent key space (§1a(iii)).
**Nothing arms the list.** The claim as published tells a reader the census
answers *"which rows cross a regime"* when it answers *"which rows cross a
regime among three routines somebody typed in, on the side of the pair whose
compiler happens to emit a resolvable callee"*.

**On the *"honest statement"* mark.** It is an editorial judgement about
direction of error; there is no derivation to re-do. And it is **false in the
direction it claims** — §4a: 13 of 33 rows still declare an unsearched unsafe
endpoint, so the project did not merely *"search more than it could show"*.

**On the arms.** I ran what can be run:

```
$ python3 synthesis/outward_ir.py --selftest      -> OK (16 arms, 0 failing)   rc=0
$ python3 harness/tools/temp_citations.py --selftest -> OK (12 arms, 0 failing, 13 modules)  rc=0
```

**A passing selftest is evidence the arms PASS, not that they were SEEN TO
FAIL.** The evidence for that clause is `.temp/t170/{arm_break,pin_arm_break,
pin_status_break,raised_break,bs_mustfire}.py` and nothing in the fold shows any
was re-run. The mark sits on the clause the run does not cover.

---

## 6. ITEM 43's ACCUSATIONS — **BOTH VERIFIED**. `asm.py` was not touched.

### 6a. The masked stage-3a failure — **VERIFIED**

`check.py:3010` fails a cell when `not k.has_loop and not bulk`.

```
=== _RNvCs86OlWC8CPt8_10safe_tuned6kernel   (the REAL kernel)
  instructions: 41   BACK EDGES: 0
  calls:  call *0x4398f(%rip)         (dynamic thunk)
          call 16e70 <…Iterator4fold…safe_tuned6kernel…>
          call 17450 <…core5sliceSy4iter…>
=== _RINvXs2J_…Iterator4fold…safe_tuned6kernel0…   (what find_symbol PICKS)
  instructions: 70   BACK EDGES: 4
```

None of the real kernel's three callees is in `_BULK_NAMES`. **The real kernel
has no loop and no bulk call; the window measured instead has four back edges.
`p01`'s green at that cell is green because the wrong symbol was measured.**

### 6b. `p05/NOTES.md` §1a's invented mechanism — **VERIFIED**

`patterns/p05-index-flatten/NOTES.md:209-211`:

> *"The `verus` cell does not have them because its `main` never materialises
> that aggregate (`load_input` is `external_body`, so the tuple stays in the
> callee)."*

`asm.py` imported read-only, asked what it picks:

```
verus       picked=_RINvNtNtNtCs…driftsort_main…          <- MIS-RESOLVED
safe_naive  picked=_RNvCsaBH6GJeUSWJ_10safe_naive4main
safe_tuned  picked=_RNvCs86OlWC8CPt8_10safe_tuned4main
unsafe      picked=_RNvCsbJ183vTuGGA_6unsafe4main
```

and the real symbol:

```
$ objdump -d --disassemble=_RNvCs5wP2qveqZnT_5verus4main .temp/build/p05/verus-O0-whole | grep '%xmm'
  16e42: 0f 10 84 24 80 00 00   movups 0x80(%rsp),%xmm0
  16e4a: 0f 29 44 24 50         movaps %xmm0,0x50(%rsp)
```

**`verus::main` carries exactly the two instructions §1a says it lacks.** The
`—` is a symbol mis-resolution; the count is **20 of 32, four `O0 whole` hits**.
`TASK_170`'s accusation is exact.

### 6c. ⚠ The adjacent claim is also confirmed, and it is still uncorrected

I re-derived p16's 32-cell census with `asm.py` (read-only): **9 of 32 carry a
vector register**, and p16's real `verus::main` at `-O0 whole` carries the same
two `xmm` instructions (`objdump`, `16e32`/`16e3a`), so the true figure is
**10 with / 22 without**. `.memory/01-ladder.md:917` still reads:

> *"it is **23 of 32 cells**; the 9 with `['xmm']` are all `whole`-mode `main` …
> **Quote the 23/32.**"*

**The authoritative layer instructs a reader to quote a number the mis-resolution
produced.** Neither this nor `p05/NOTES.md` §1a was landed at `d6aa844`.

---

## Problems — ranked

| # | severity | finding | § |
|---|---|---|---|
| 1 | **blocker** | **`results/SYNTHESIS.md:1566` publishes *"No pattern ships a length-HETEROGENEOUS sweep band"* as a priced, deliberate omission. It is FALSE.** p06's `inputs/gen.py:62` names the queue item as its motive and `:135-137` asserts the opposite; p10 ships `sweep-h1/h2/h3.bin`; p14/p18/p22/p23 the same; and `RECAP.md:6592-6596` already recorded item 11 as retired by p06. A reader picks this up and re-does work that exists. | 4b |
| 2 | **blocker** | **The reframing is the flattering direction.** `14/0/0` documents; the withdrawn sentence measured depth. **13 of 33 rows declare an unsearched, fiat or owed UNSAFE endpoint in their own words** (14 with p09). *"What remains is four named levers"* omits nine of them. `results/SYNTHESIS.md:1501,1546-1554`. | 4a |
| 3 | **major** | **`results/synthesis.md:807`'s *"every entry cited to a reviewed artefact — except one, p06"* is false on three rows**: `p01`, `p03`, `p08` cite `RECAP` *"Owed"* — the open backlog — and say the search is OWED / NEVER done. They are counted inside the published *"30 report a SEARCH RESULT"*, because `n_found` is a residual (`synthesize.py:2765`). The same document retires those same three gaps at `SYNTHESIS.md:1561-1565`. | 3d |
| 4 | **major** | **`results/synthesis.md:809` says *"Seven of the fourteen"* and lists SIX**, omitting `p18` (*"⊘ The R4 side is NOT searched, declared"*) and `p38` (*"NOT established … flatters SAFE"*) — a hardcoded count inside a generated file (`synthesize.py:2791`), undercounting in the flattering direction, one paragraph below the same defect's own fix. | 3c |
| 5 | **major** | **`RECAP` 66(b)'s reason for `p27` is a mechanism invented for a null result.** Verified by disassembly: both p27 spellings are **inline** (`rep stos` 32 `Ir` inside `<kernel>`; 18 `movaps` + 1 `xorps` = 19), so `regime_crossing` is structurally blind. The contribution is **52% of the published row**, not *"small"*. `TASK_169` stands. | 1c |
| 6 | **major** | **`✅ "the marked set is DERIVED rather than listed"` is not earned.** `BULK_REGIME` is 3 hardcoded keys, 2 of them bare glibc addresses; `__memchr_avx2` and `__strlen_avx2` are unclassified in the same sidecar and contribute asymmetrically on 6 published `gcc-clang` rows; and on a `gcc-clang` pair gcc's libc callees are spelled as client PLT addresses, so the published evidence string *"while the other side does not call it at all"* is generated from a key space where that is true by construction. Right answer on p08, unestablished reason. | 1a, 5 |
| 7 | **major** | **`✅ "the honest statement … runs AGAINST this project's usual error direction"` is an editorial judgement marked as re-derived, and it is false** on the document's own entries. | 5 |
| 8 | **major** | **`.memory/03-measurement.md:541-543` still asserts, un-annotated, the sentence two reviews retracted** — *"Only p08's gcc kernels contain a `rep` instruction, so no previously published `Ir` comparison is contaminated"* — 64 lines below its own retraction, and the new `§` marks the published row it says cannot exist. Reported at `TASK_169` and `TASK_170`; live at `HEAD`. | 1e |
| 9 | **major** | **`results/SYNTHESIS.md:1613-1616` double-counts item 43** — *"investigated a seventeenth (43)"* and *"retire eleven **more** (…; 43; …)"*. 28 claimed, **27 distinct**. In the sentence whose preamble says it was DERIVED after inventing one. | 4d |
| 10 | **major** | **Item 5 is retired with the reason its own `RECAP` entry calls the wrong test.** `SYNTHESIS.md:1602-1604` vs `RECAP.md:6875-6880` (*"the right question is 'does a committed claim depend on it?' — 64 committed doc references"*). A refusal's reason is what gets reused. | 4c |
| 11 | **major** | **Item 43's two accusations both verify, and neither correction landed.** `p01 safe_tuned -O0 isolated` has 0 back edges and 0 bulk calls against a 4-back-edge substitute; `p05/NOTES.md:209-211`'s mechanism is invented (`verus::main` carries both `xmm` instructions); `.memory/01-ladder.md:917` still says *"Quote the 23/32"* where it is 22/10. | 6 |
| 12 | **minor** | **`p16`'s *"the SIGN FLIPS"* is a derived label promoted as a quotation** into `SYNTHESIS.md:1515`, `RECAP.md:24` and `:6170`. Neither cited artefact frames it that way, and `p16/NOTES.md:1072` **denies** that phrase about p16 on another axis. Numbers exact. | 3b |
| 13 | **minor** | **`results/SYNTHESIS.md:152-160` drops the `PROVISIONAL` flag** that `results/synthesis.md:314` carries on the TASK_074 zero-fill probe — the only evidence for *"`Ir` charges most where the machine charges least"* in the hand-written argument. (The direction itself **is** backed, at `.memory/03-measurement.md:417-421`.) | 1d |
| 14 | **minor** | **`SYNTHESIS.md:555`'s *"Of the nine:"* is a dangling antecedent** and lists six (p10, p13, p12, p22, p17, p36). Inherited, but the rewrite one sentence above removed the last number a reader could have reconciled it against, in the caveat paragraph *"that governs this whole section"*. | — |
| 15 | **minor** | **`synthesize.py:541`'s `p42` entry quotes `15 verified, 0 errors` against a section that says 18/0** for the shipped rung and 15/0 for the one it replaced (`p42/NOTES.md:1114`, `:876`). | 3e |
| 16 | **minor** | **`synthesize.py:326-327`'s *"p19 and p23 ship no committed spelling probe at all"* is incomplete** — `patterns/p02-buffer-copy/` and `patterns/p05-index-flatten/` have **no `controls/` directory at all**. Four of the fourteen, not two; and p04, p27, p46 are placed in neither branch. | — |
| 17 | **minor** | **Item 28 is listed among *"closed sixteen with a run"*** while `RECAP.md:6048-6050`'s own finding headline says it **DID NOT CLOSE**; and items 2, 3, 20 are retired at half their recorded width. | 4e |

---

## ✅ CLEAN NEGATIVES — named attacks that did NOT land

None of these repeats the ten, fifteen or twenty-one of earlier reviews.

1. **The pin's file SET is complete.** `derived_from_sha256` equals the tree's
   build determinants **exactly** on all 33 patterns, 13 apiece, 0 discrepancies.
2. **A rung source that includes a file outside the pin.** Every `#[path]` in
   every rung source resolves to `common/driver.rs`, which is pinned.
3. **A C kernel that includes a file outside the pin.** The complete local
   include census is `98 × kernel.h`, `66 × driver.h` — both pinned.
4. **A build config `build.py` reads.** It reads none; flags are literals.
5. **An empty pin reading `FRESH`.** `calibrate`'s `unpinned` set catches it and
   the publisher branches on `stale or unpinned` (`synthesize.py:1382,1797`).
6. **The re-pin re-rounding a number.** 4272 measured leaves compared across
   `d6aa844^ → HEAD`: identical; the gate map is preserved verbatim on all 33
   and every `derived_from` value comes from the emit-time map.
7. **A symmetric byte-wise pair being incomparable too.** p08's four Rust cells
   carry `memset` at 4113.00 exactly; the term cancels out of the *difference*,
   which is the published quantity. Not marking them is correct.
8. **A bulk contribution just under the 2.00 floor.** No such row exists: a
   byte-wise routine contributing `< 2.00 Ir`/call would be invoked once per
   ~2000 kernel calls.
9. **A PLT thunk hiding a marked routine.** The biggest unclassified callee in
   the sidecar — `0x15220`, 46 cells, up to 4828 `Ir`/callee-call — is
   `ld.so`'s `_dl_runtime_resolve_xsavec`, one-shot, correctly not bulk.
10. **`SYNTHESIS.md` §1's `p08` direction claim being unmeasured.** It is
    measured, p08-specific, in `.memory/03-measurement.md:417-421` (*"`Ir` says
    c-gcc 33% cheaper … wall clock says dearer"*).
11. **The `§` marker being applied to p08's rung pairs.** It is not, and the
    docstring's stated reason is the true one.
12. **`p42`'s `§` marker contradicting `p42`'s search entry.** Different cells —
    the marker is on `R2−R4`, the search on `R3/R4`. No conflict.
13. **The `44 numbered items` figure.** Contiguous 0..43, no letter-suffixed
    items, nothing above 43. Correct (though only because the list starts at 0).
14. **The gate verdicts and `blocked` counts.** Read from the 33 records:
    `{'PASS': 30, 'PASS-WITH-BLOCKED-ROWS': 3}`, `{'p01': 1, 'p35': 3,
    'p42': 1}`, failures `NONE`. Exact.
15. **`--emit` reverting the re-pin.** It cannot: `main()` ends
    `rc = repin(a.emit); return rc` (`outward_ir.py:578-580`).
16. **The four promoted search figures.** All four are in their cited artefacts
    to the digit; `p09`'s `65×` and `p42`'s *"The sign flips"* are the
    artefacts' own words, not the entry's.
17. **`p13`'s `gcc-clang` memset asymmetry being a naming artefact.** It is
    real: `p13 c-gcc`'s kernel calls only `strlen@plt` and `__stack_chk_fail@plt`
    — gcc genuinely inlines the memset and memcpy that clang calls.

---

## THE CLOSING QUESTION — **is `results/SYNTHESIS.md` safe to publish?**

**No. Not as it stands. Four sentences a reader would act on are not backed —
three of them added by the two commits under review.**

1. **`:1566`** — *"No pattern ships a length-HETEROGENEOUS sweep band."*
   **False against the shipped tree.** A reader building the band re-does p06's,
   p10's, p14's, p18's, p22's and p23's work. *(Problem 1.)*
2. **`:1501` + `:1546-1554`** — *"A STRUCTURAL GAP … DOES NOT EXIST"* / *"What
   remains is four named levers."* **13 of 33 rows say otherwise in their own
   text.** A reader takes away *"the ladder's spelling search is essentially
   complete, bar four levers"*, and cites `R3 − R4` figures as properties of the
   patterns. *(Problem 2.)*
3. **`:1613-1616`** — the retirement count, in the sentence that advertises
   itself as derived. **28 claimed, 27 distinct.** *(Problem 9.)*
4. **`:1602-1604`** — item 5's decline reason, which its own record calls the
   wrong test. **A reader who picks it up asks the wrong question.**
   *(Problem 10.)*

**And one that is inherited rather than new but is the same shape:**
`results/synthesis.md:807,809` — the *"every entry cited to a reviewed
artefact"* and *"Seven of the fourteen"* sentences, both false, both load-bearing
for §7's withdrawal.

✅ **Everything else in the two folds is publishable and several parts are
better than claimed.** The build-determinant pin is the strongest thing in this
session's output: I attacked it four ways and it held, and the `--repin`
argument — *the old key was a MAP, so the emit-time hashes were already
committed* — is exactly right and cost nothing. The four promoted search
numbers are real. The `§` marker's rows are correct even where its reasoning is
not. **The document does not need to be withdrawn; it needs four sentences
fixed, and one number told to the reader that it currently withholds — the 13.**

⚠⚠ **The one-line answer to the question the manager asked by name:** *you did
convert a limitation into a boast.* The limitation is smaller than the
withdrawn sentence said (`most` → 39%) and it is **not gone**, and the document
now tells a reader it is.

---

## Unsure / not done

* **I did not run `--emit`** (352 callgrind runs, out of scope). §2c is a code
  read of `outward_ir.py:571-580` and is stated as one. The `repin()` half is
  exercised by the before/after comparison in §2b.
* **I did not re-run the `.temp/t170/*_break.py` regression scripts.** §5's
  verdict on the *"SEEN TO FAIL"* mark is that a passing selftest does not
  evidence it, not that the arms do not fire. I ran the two selftests that exist
  as flags and both are green.
* **The 13-of-33 tally is a hand adjudication of entry text**, not a mechanical
  count — deliberately, because that is the only thing the entries support. The
  script prints each row's own words so the adjudication is checkable
  (`.temp/t171/unsafe_endpoint.py`). `p09` is borderline and I counted it
  **out**, which is the conservative direction against my own finding; counting
  it in gives 14.
* **`p27`'s clang-side 19-`Ir` figure** is an instruction count in the kernel
  window, not a callgrind attribution. It matches `TASK_169`'s and it is what
  `Ir` would charge, but I did not re-run callgrind on it.
* **I did not audit `common/census/`, `licence.json`, `composition.py` or the
  gate stages** — pre-settled by the task file, and I found no reason to doubt
  them.
* **Two subagents did the bulk reading** for §3 (the fourteen entries against
  their artefacts) and §4d–4f (the backlog count and the retirement reasons).
  **Every finding I have ranked `blocker` or `major` from that work I
  re-verified myself against the files or with a command**, and the commands are
  pasted above. The unverified residue is confined to Problems 15–17 and the
  §4e/§4f lists.
* **I did not check whether any of these defects predate `TASK_170`.** Problems
  3, 4, 14 and 16 are inherited; Problems 1, 2, 9 and 10 are new in `87baad7`.

## Memory updates

**None written — `.memory/` is the manager's, and reviewers do not fix.** What
this review asks the manager to land, in priority order:

1. ⚠⚠⚠ **`results/SYNTHESIS.md:1566`** — the length-heterogeneous claim is
   false; narrow it to p13's fit blobs, or delete the bullet.
   `RECAP.md:6968-6972` (item 11's body) needs the same correction, and
   `RECAP.md:6592-6596` already contains it.
2. ⚠⚠⚠ **`results/SYNTHESIS.md:1501,1546-1554`** — restore the limitation in its
   narrow form and **give the reader the number**: *the search state is
   documented on all 33 rows, and on 13 the documentation says the unsafe
   endpoint was never searched.*
3. ⚠⚠ **`synthesize.py:2765,2791`** — `n_found` must exclude the OWED rows, and
   *"Seven of the fourteen"* must be **derived**, not typed. `p01`/`p03`/`p08`
   need an `⊘`-class marker or a `SEARCH_OWED` set; `results/synthesis.md:807`'s
   *"every entry cited to a reviewed artefact"* is false until they do.
4. ⚠⚠ **`.memory/03-measurement.md:541-543`** — annotate as `DISPUTED` (third
   task running), and **`.memory/01-ladder.md:917`** — `23/32` → `22/32`,
   `9` → `10`, and strike *"Quote the 23/32."*
5. ⚠⚠ **`patterns/p05-index-flatten/NOTES.md:198-211`** — `19 of 32` → `20 of
   32`, three hits → four, and **delete the mechanism**; `verus::main` carries
   both `xmm` instructions. Costs a p05 gate re-run.
6. ⚠ **`RECAP.md:6191-6193`** — replace the `p27` reason: the census does not
   test the claim, because both spellings are inline and produce no callee edge.
   `TASK_169`'s figure reproduces exactly.
7. ⚠ **`RECAP.md:6185-6188`** — downgrade *"DERIVED rather than listed"*: the
   rows are derived, the routine set is a hand list of three, and on `gcc-clang`
   pairs the key space is compiler-dependent.
8. ⚠ **`results/SYNTHESIS.md:1613-1616`** — item 43 is counted twice; and
   `:1602-1604` — item 5's reason is the refuted one.
9. ⚠ **`synthesize.py:429`** — `p16`'s *"the SIGN FLIPS"* is the entry's own
   arithmetic; say so, since it is now published in three places.

**PROTOCOL rule 2 running count: launched from 948.** This review contradicts
the manager on: the retirement's reframing (*"a structural gap does not exist"* —
13 of 33 rows say it does); *"No pattern ships a length-heterogeneous sweep
band"* (six patterns do, three of them citing the queue item by name);
`RECAP` 66(b)'s reason for `p27` (the census cannot see an inlined `rep`);
`✅ "the marked set is DERIVED rather than listed"`; `✅ "the honest statement …
runs AGAINST this project's usual error direction"`;
*"every entry cited to a reviewed artefact — except one, p06"* (three cite the
backlog); *"Seven of the fourteen"* (six listed, ≥8 true); and the retirement
count (28 claimed, 27 distinct). ⚠ **Reconciliation is the manager's job, not
mine.**
