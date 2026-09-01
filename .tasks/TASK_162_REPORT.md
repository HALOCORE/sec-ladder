# TASK_162 review report — `p49`, and the one assumption the engineer named turned out to be false in the SAFE direction

**Role: research reviewer.** I do not fix; I report. All scratch, probes and logs
are under `.temp/t162/`. Nothing under `patterns/`, `.memory/`, `RECAP.md`,
`results/SYNTHESIS.md`, `harness/`, `synthesis/` or `pilot/` was edited; two
files that a *run* rewrote (`controls/no_share_break.json`,
`results/gate/p49-interned-pool.json`) were restored from `HEAD` and verified by
sha256. `git status` is clean.

---

## 0. THE HEADLINE, AND IT IS ITEM 7

**`NOTES.md` §10 assumption 3 is FALSE, and the row survives it.** The engineer
wrote (`patterns/p49-interned-pool/NOTES.md:815-821`):

> ⚠ **The epilogue folds the ownership flag**, which is what makes the
> `provenance` repair benign-observable (§3b). … **Without it, `provenance` and
> `cow` would be indistinguishable on benign input and this row would have no
> reason to prefer one.**

Measured (`.temp/t162/item7_epilogue.py` — all three arms built twice, once as
shipped and once with the single line `acc = acc * 31 + (uint64_t)rshd[t];`
deleted from the epilogue by an **asserted** one-occurrence substitution):

```
=== epilogue: as shipped ===
  cow moves a benign answer       : 0 of 3  []
  provenance moves a benign answer: 3 of 3  ['degenerate.bin','large.bin','small.bin']

=== epilogue: FLAG FOLD DELETED ===
  cow moves a benign answer       : 0 of 3  []
  provenance moves a benign answer: 2 of 3  ['large.bin','small.bin']
```

**With the fold gone, `provenance` still moves 2 of the 3 benign checksums.**
The `cow`-vs-upstream call does **not** rest on the epilogue, so **the row did
NOT ship the wrong safety line.** Only `degenerate.bin` collapses.

**The mechanism, so it is not just a number** (`.temp/t162/coverage.py`, §4):
`provenance` deletes the deduplication, so every record consumes private bytes
where interning previously shared them. The private region is 44 bytes:

```
input           arm    born_shared_new  born_shared_hit  born_owned  sent_priv_full  nrec_final
large.bin       cow                364               48         356               4         768
large.bin       prov                 0                0         762             398         762
small.bin       cow                 37                4          52               0          93
small.bin       prov                 0                0          91              11          91
degenerate.bin  cow                  8                3           1               0          12
degenerate.bin  prov                 0                0          12               0          12
```

`provenance` exhausts the private region (`sent_priv_full` 4 → 398 and 0 → 11),
which folds extra `SENT`s and changes `nrec` — **both of which the epilogue folds
independently of the ownership flag.** On `degenerate.bin` the two arms produce
identical record counts and identical refusals, which is exactly why that one
input, and only that one, needs the flag fold to separate them.

⚠ The same causal claim, in a weaker form, is in two **MEASUREMENT-hashed**
files: `c/kernel.c:202` and `c/kernel_hardened.c:205` both say the flag fold *"is
what makes the PROVENANCE repair benign-observable while copy-on-write is not"*.
It is **sufficient, not necessary**. `c/kernel.h:117-122` is fine — it only
identifies the fold with the port's `"interned"` field, which is true.
✅ **`spec.md`'s hashed `why` does NOT carry the counterfactual** — it says the
fold *keeps `rshd[]` live*, which is true. So the contract block is clean and the
correction is a re-measure of three files, not a contract move.

---

## 1. Per-item verdicts

| # | item | verdict |
|---|---|---|
| 1 | the `p08` distinction | **SURVIVES, NARROWED** — the rows are C-side distinct; the *stated ground* (partial vs total) is a correlate, not the mechanism |
| 2 | `aliasing` vs `logical` | **SURVIVES, NARROWED** — `aliasing` is right by the table's own test, but the widened DESCRIPTION now names a STRUCTURE where every other class names an ERROR |
| 3 | `model.py`, the only instrument | **SURVIVES** — 0 disagreements against an independently written third implementation over 20 078 windows; two coverage gaps, both minor |
| 4 | the positive controls | **SURVIVES** — 16 firings hand-reproduced, `ctl_asan`'s `malloc`/`free` survive gcc `-O3 -fsanitize=address` |
| 5 | *"both sides, one type apart"* | **SURVIVES, NARROWED** — the safety claim stands; *"ONE TYPE"* is false and measured false |
| 6 | the cost axis reversing between compilers | **SURVIVES, NARROWED** — reproduced, and it now HAS a mechanism that closes exactly |
| 7 | the epilogue folds the ownership flag | **FALLS** — the counterfactual is false; **the safety line STANDS** |
| 8 | the manager's pre-build claims | **PARTLY FALLS** — `README.md` inherited the refuted mechanism verbatim |
| 9 | the R5 | **SURVIVES** — every helper, wrapper and lemma has a live call site; the 2×2 bisection re-derives exactly |
| 10 | the false-citation sweep | **ONE NEW INSTANCE** (item 8's `README.md`); no dangling file citation anywhere |

---

## 2. Findings

### MAJOR 1 — `README.md:73-78` restates the manager's REFUTED mechanism as fact

```
3. **Why the reduction this row came from had a dead branch, and what fixing it
   cost.** `.temp/t160/red/k40304.c` fixed the content width at 3 against a
   threshold of 5, so the guard could never be false.
```

This is **exactly** the claim the engineer measured to be false (guard FALSE
30 263 / 97 458 evaluations, 31.1 %, because the COW body writes
`r_shared[i] = 0`). `NOTES.md` §0 lists the three files that were corrected in the
rule-6 second-half pass — `inputs/gen.py`, `c/kernel.c`, `verus.rs` — and
**`README.md` is not among them.** So a reader who reads only the one-screen
version gets the refuted mechanism with no hedge.

*Failure scenario*: the next row that reduces a CVE reads `README.md` for the
precedent, copies *"a constant width makes the guard unfireable"*, and repeats a
diagnosis this project already paid a task to correct. The true defect is *no
record is ever born owned* — which the same paragraph's next sentence gets right,
so the header and body disagree (PROTOCOL rule 13's shape).

✅ **Cheap**: `README.md` is in the **gate** `source_sha256` (49 entries) and
**not** in the measurement record's 18 → one gate re-run (**measured at ~9 min**
on this box), no re-measure, no contract move.

### MAJOR 2 — the item-7 counterfactual, in `NOTES.md` and in two measurement-hashed files

Stated above (§0). `NOTES.md:815-821` is gate-hashed; `c/kernel.c:202` and
`c/kernel_hardened.c:205` are **measurement-hashed** — correcting them costs a
re-measure. Batch them with any other rung-source fix (PROTOCOL rule 6's budget
table).

⚠ **This is the SECOND time this row has published a false sentence under a
matching hash**, and the first (`"the copy loop below"`) was caught by the same
rule-6 second-half pass that *wrote* this one.

### MAJOR 3 — *"the two `Rc` arms differ in ONE TYPE"* is false, and it is measured false

The claim appears in **`spec.md`'s HASHED `why`**, in `controls/safe_arms.py:28`
and its asserted `invariant` at `:234`, in `NOTES.md:73`'s rule-6 disclosure
table, in `TASK_161_REPORT.md` §3d, and in the `afe63d9` commit message
(*"Safe Rust expresses BOTH sides one type apart"*).

`arm_rc_makemut.rs` is **not** `arm_rc_refcell.rs` with one type changed. It also
carries a 20-line block at the write site:

```rust
let shared: bool = Rc::strong_count(&recs[t].0) > 1;   // the ownership question, spelled out
let need: usize = recs[t].0.len as usize;
if shared && priv_used + need > MEM - ARENA { SENT }
else { if shared { priv_used += need; recs[t].1 = 0; }
       Rc::make_mut(&mut recs[t].0).data[0] = 0; 2 }
```

**Measured** (`.temp/t162/rustarm/arm_C_makemut_only.rs`, built with
`harness/build.py::rust_flags("O3","isolated","unwind")`): strip that block down
to `Rc::make_mut(..).data[0] = 0;` and the arm matches **NEITHER** `c/kernel.c`
nor `c/kernel_hardened.c` on all **five** discriminating adversarial inputs:

```
input                            R1 (bug)             R1h (cow)   armC make_mut ONLY   verdict
adversarial-cascade.bin   8653438269484025856  18333534148569259008  13945149146826737664  NEITHER
adversarial-cowfull.bin   8897935692788144128   9887309797562598400   7758206308267986944  NEITHER
adversarial-many.bin     10636248267475679232   4770081662406190080  18038885826277937152  NEITHER
adversarial-rehash.bin   14042888476904305664   1773053308779294720   9592468585475294208  NEITHER
adversarial-share.bin    17203576457335438336   9997648724353765376   9589979618682960896  NEITHER
degenerate/large/small + stride3 ............................................ ==R1h
```

✅ **The SAFETY half stands**: the stripped arm still differs from `R1` on every
one of those inputs, so `make_mut` really does rule the bug out on its own. What
does **not** stand is *"one type apart"* and *"9/9 by an API choice"* — the 9/9
needs the explicit `strong_count` ownership query, the budget refusal and the
flag clear.

⚠⚠ **The arm file itself is honest** (`arm_rc_makemut.rs:17-23`: *"The one
explicit test below is a BUDGET test and not a safety test, and saying so
matters"*). **Five downstream summaries dropped the disclosure**, one of them
inside `contract_sha256`. That is PROTOCOL rule 13 exactly: the detail is
maintained and the header rots.

### MAJOR 4 — `CAVEATS["p49"]` overstates twice, and the commit message repeats both

`harness/tools/composition.py:227-246`:

**(a) The `p08` number compares two different quantities.**
> *"…two records' content ranges are always EQUAL or DISJOINT and never PARTIAL
> (11 084 equal, 892 352 disjoint, 0 partial), **while p08's are PARTIAL
> (9 copies)** — so the C-side distinction from p08 is a NUMBER and not an
> adjective."*

Read out of `controls/no_overlap.json`: p49's three figures are **RECORD-PAIR
relations**; p08's `9` are **COPY source/destination relations**. **p08 has no
records at all**, so its record-pair column does not exist and the control never
measures one. And on the like-for-like axis p08's copies are **32 887 DISJOINT
against 9 PARTIAL** (`large.bin` 32 768 disjoint, `small.bin` 128,
`adversarial-overlap.bin` 4 partial, plus 5 synthetic) — 0.027 %.

⚠ Worse for the *"NUMBER not an adjective"* framing: p49's `0 PARTIAL` is
**forced by the code**, not discovered. A record's `(off, len)` is either freshly
bump-allocated (disjoint from everything) or copied **verbatim** from a table
entry whose `(ekey, elen)` matched — so `partial` is unreachable. The census
confirms a theorem; it cannot distinguish.

**(b) *"It is also the tree's only row with NO DETECTOR AT ALL"* is FALSE.**
`p22`'s and `p47`'s models both `return "clean"` unconditionally with the same
argument (`p47/model.py:299-314`: *"ASan, UBSan, Miri and the `ensures` R5 proves
are all silent"*; `p22/model.py:263-286`: *"no diagnostic at all"*). The census
of `return "clean"` across the tree gives **`p01`, `p08`, `p22`, `p47`, `p49`**
(`p08` only in the gate's fortified gcc configuration — its bug **is** ASan-visible
under clang or `-D_FORTIFY_SOURCE=0`).

✅ **The defensible narrowing, and it is still a real novelty**: p49 is the only
row whose **sole instrument is the CHECKSUM**. p22's is a hang
(`expected_hang`), p47's is the instruction trace, p01 has no bug.

Both (a) and (b) are repeated verbatim in the `afe63d9` commit message.

### MAJOR 5 — `NOTES.md:433` prints a ladder ratio that contradicts the row's own headline

```
### 4e. The ladder, `-O3` isolated, against R1h
small.bin   c-gcc 0.99  c-gcc-h 1.00  ...
```

From `results/p49-interned-pool.json`: `c-gcc 1974.4131`, `c-gcc-h 1971.6254`,
ratio **1.001414 → 1.00**. Printing `0.99` says the **buggy** rung is 1 % cheaper
— the **opposite sign** to §4b's own `−2.79` (which says R1h is cheaper) on the
same two numbers. `large.bin`'s `0.99` is correct (0.993852). The `small.bin`
cell looks like a copy of the `large.bin` cell.

*Failure scenario*: §4e is the ladder table a reader quotes; it silently erases
the one cell in the whole row where the safety line is free, which is §4b's
headline.
Confined to `NOTES.md` — `results/tables/p49-interned-pool.md` does not carry the
ratios. Gate-hashed → gate re-run.

### MAJOR 6 — §4c says the decomposition "does NOT close". It closes, exactly, at line level

`NOTES.md:400-408` divides the per-call delta by guard evaluations, gets a figure
that moves across inputs, and publishes no mechanism. **PROTOCOL rule 12 is
exactly this case**, and the mechanism costs one callgrind run per cell.

`.temp/t162/mech/linediff.py` — `-g` builds verified **code-identical** to the
measurement record (`n_fn_nopad` 274 / 410, `md5_raw 1a7e56ae…` / `66ae47be…`),
callgrind per-source-line, R1h minus R1:

```
gcc -O3, small.bin  (measured cell delta -2.79)
   +8.43/call   if (rshd[t]) {                       0 -> 16852
   -4.62/call   m[base + j] = p49_cbyte(key, j);  40686 -> 31449   (p49_fill, inlined)
   -4.62/call   abump = abump + w;                27711 -> 18474
   -1.00/call   key = (uint8_t)(a % P49_NKEY);
   -1.00/call   w   = (uint8_t)(1u + a % P49_MAXW);
   ------------------------------------------------  sum -2.81   <-- the whole delta

gcc -O3, large.bin  (measured cell delta +31.41)
  +44.75/call   if (rshd[t]) {
   -5.70/call   m[base + j] = p49_cbyte(key, j);
   -5.70/call   abump = abump + w;
   -1.00/call   key ;  -1.00/call  w
   ------------------------------------------------  sum +31.35
```

**Three facts fall out, none of them published:**

1. **The safety line's own cost IS a constant per evaluation** —
   `16852 / 8464 evaluations = 1.99`, `8950 / 4470 = 2.00`. Per (compiler,
   level): **gcc `-O3` 2.00 · clang `-O3` 2.00 · clang `-O0` 3.00 · gcc `-O0`
   6.00** `Ir` per guard evaluation. §4c's non-constant `−0.66 … +7.66` was the
   *net* per-guard figure, which mixes the guard with what it displaces.
2. **The offset is a gcc codegen effect on the interning-DEFINE path.** `abump`
   and the `p49_fill` store each lose exactly **9 237** `Ir` — precisely the
   number of intern-creations (`ekey[nent] = key` executes 9 237 times) — i.e.
   **one instruction per creation, twice**, plus one per call in the operand
   decode.
3. ⚠⚠ **So the sign is set by the EVENT MIX, not by the compiler.** On
   `small.bin` the guard fires 4.232×/call while each offset site runs
   4.62×/call → net negative; on `large.bin` the guard fires 22.351×/call while
   the offsets run only 5.70×/call → net positive. **gcc alone already reverses
   between the two inputs** (`−2.79` vs `+31.41`), which the headline frames as a
   *compiler* reversal. Both readings are true of the table; only the event-mix
   one explains it.

⚠ **Do not attempt this on clang**: clang's line info puts **~440 `Ir`/call (19 %
of the kernel)** in `<counts for unidentified lines>` and moves the whole block
between the two files, so a clang-side line decomposition is not trustworthy.
gcc's has **zero** unidentified.

### MINOR 7 — two arms of `model.py` are invisible to the gate

`.temp/t162/mutate_model.py` plants 8 defects into a **copy** of `model.py` (each
substitution count asserted) and runs `detector_selftest()` + `selfcheck()` on
all nine inputs; `.temp/t162/mut_checksum.py` then asks whether the model's
whole-program checksum also moves (i.e. whether gate stage 2 would catch it).

```
mutation                            selfcheck   model checksum moves
D1-detector-dead                    REPORTED    0/9
D2-detector-constant-true           REPORTED    0/9
D3-safety-line-deleted              REPORTED    5/9
S1-spec-epilogue-flagfold-dropped   REPORTED    0/9
S2-sim-dedup-disabled               REPORTED    2/9
S3-sim-arena-cap-dropped            SILENT      0/9      <-- invisible to the gate
W1-share-break-census-neutered      SILENT      0/9      <-- invisible to the gate
W2-share-break-census-always        REPORTED    0/9
```

✅ **6 of 8 REPORT with the designed message and NONE crashes** — strictly better
than the p32 arm `.memory/03-measurement.md` entry 19 closes on (*"three of the
four fail by CRASHING … the DIAGNOSTIC is lost"*). Worth recording.

**S3**: the arena-capacity refusal is unreachable on this corpus. Splitting the
`or` (`.temp/t162` inline probe) over **every window of every shipped blob**:

```
                       miss_refused  table_full  arena_full  arena_full_DECIDING  priv_full
large.bin                        4           4           0                    0          4
every other blob                 0           0           0                    0        0/1
```

`abump + w > P49_ARENA` **never decides anything on any shipped input**, in
either C rung, at either level. The 4 refusals on `large.bin` are all
`nent >= NENT`. So the branch is dead on the corpus and a model defect there
cannot move a published number — but it is also untested, and `c/kernel.h`'s
four-line in-bounds proof leans on it.

**W1**: `model.py::no_share_break_problems` — the row's **structural headline**
stated as a check — has **no must-fire arm inside the gate**. Neuter
`window_share_break` to always return `False` and `selfcheck()` is silent and the
checksum is unmoved. The must-fire direction exists only in
`controls/no_share_break.py`, which asserts every adversarial blob (bar
`stride3`) hits the guard TRUE — and the gate **hashes** that control but never
**runs** it. This is entry 19's *"never fires vs cannot fire"* shape one level
up: the `Detector` got a `detector_selftest()`; the census did not.

### MINOR 8 — the `9/9` in the safe-Rust arms is really `5/9` discriminating

`controls/safe_arms.json`: on `degenerate.bin`, `large.bin`, `small.bin` and
`adversarial-stride3.bin`, **R1 and R1h print the same number**, so an arm that
matches one matches both. The claim *"reproduces `c/kernel.c` 9/9"* is true and
its **discriminating** support is **5** inputs. Same for arm C.

### MINOR 9 — three small inaccuracies

* `NOTES.md:512-513` — *"NOT the largest FILE: `p28`'s 1709 and `p29`'s 1494
  against p49's 1126"*. **`p34`'s is 1183**, also longer; p49 is 4th, not 3rd.
  (The obligation census itself re-derives **exactly**: p49 34, p29 25, p34 24,
  p28 23, p46 21, p22 20 … p32 15, p25 10, p04 9.)
* `controls/detectors.py:49-51` — *"Each control is built with the same compiler
  and the same flags as the binaries whose column it licenses"*. The control
  build omits `-DSLB_ISOLATED` and both `-I` paths and links one TU instead of
  three. Harmless for sanitizer behaviour, but it is not *the same flags*.
* `.memory/02-bench-rules.md`'s class table dropped the qualifier
  `aliasing UB` → `aliasing` in the same edit that added p49. Correct, but the
  row now no longer records that one of its two members IS undefined behaviour;
  only `CLASSES` and `CAVEATS` do.

### MINOR 10 — `RECAP.md` and the catalogue are stale against their own commit

`afe63d9` updated `.memory/02-bench-rules.md` to **33 patterns / aliasing 2** and
left `RECAP.md` untouched (`git log -1 -- RECAP.md` → `d91c4b6`, TASK_160). The
START HERE box still reads:

* *"**THE NEXT ACTION: BUILD `p49`** … IT IS THE ONLY ADMITTED ROW LEFT"*;
* *"STILL UNBUILT: `p49` and NOTHING ELSE"*;
* *"State at `TASK_158`: 32 patterns"* (there are **33**).

`.memory/06-catalogue.md:650`'s p49 cell likewise still says
`✅✅ **ADMITTED … BUILD.**` and never says BUILT. **Two authoritative artefacts
now disagree about whether the row exists.**

---

## 3. Deliverable 2 — is `p49` FINISHED? **No.**

The **anchored** completeness check (PROTOCOL rule 1 — finding **headers**, not
mentions):

```sh
awk '/^## The findings so far/,/^## Retracted/' RECAP.md | grep -E '^[0-9]+\. ' > .temp/t162/chk/h.txt   # 61 headers
for d in patterns/p*/; do id=$(basename "$d" | cut -d- -f1)
  grep -q "\b$id\b" .temp/t162/chk/h.txt || echo "MISSING: $id"; done
```
```
MISSING: p01      <-- the known benign exception (calibration row, no result to announce)
MISSING: p49      <-- REAL
```

* `results/synthesis.md` — **0** mentions of `p49`. **It needs regenerating; I
  did not regenerate it.**
* `results/SYNTHESIS.md` (CAPITALS, hand-written) — **0** mentions. Needs a
  hand edit; never regenerate over it.
* `RECAP.md` — 5 mentions, **none of them a finding header**, and four of the five
  say the row is unbuilt (MINOR 10).

Everything upstream of that is done and re-verified:

```
harness/check.py p49                 PASS   complete_run true   failures []   blocked []
                                     contract_sha256 d339ef90…  (unchanged)
harness/measure.py --check-stale     66 record(s) examined, 0 STALE
harness/tools/composition.py --check OK: 33 patterns, 10 classes
harness/tools/contract_diff.py p49   UNCHANGED (HEAD == tree)
citation sweep over .memory/ .tasks/ RECAP.md    only TASK_NNN placeholders + this file
```

**So p49 is exactly at PROTOCOL rule 1's fourth step — the one that swallowed
`p19` for 45 tasks and `p46` for 35.**

---

## 4. Deliverable 3 — what the manager overstated

Beyond MAJOR 4 (the `CAVEATS` entry and the commit message), of the four fresh
places named:

| place | verdict |
|---|---|
| the `afe63d9` commit message | **two overstatements**, both inherited from `CAVEATS["p49"]` — see MAJOR 4. Everything else in it re-derives: gate leaves, obligation census, line counts, 16 firings, `E0594`. |
| `CAVEATS["p49"]` | **MAJOR 4** |
| the widened `aliasing` description | **stands as a classification, defective as a description** — see item 2 below |
| the `.memory/02-bench-rules.md` edit | ✅ **CLEAN.** `15 of 33` is right (33 pattern dirs); `aliasing 2 p08 p49` is right; the class table sums to 33; and *"NOTHING ADMITTED REMAINS UNBUILT"* is **TRUE** — I swept all 49 catalogue rows for an `ADMITTED`/`BUILD` cell with no pattern directory and the only two hits are `p26` (REFUSED at TASK_115) and `p33` (BUILT, merged into `p32`). One MINOR at item 9. |

⚠ **And one in TASK_162.md itself.** Item 6 says *"✅ The R4/R5 null is `0.00` in
every cell"*. That is the **kernel-exclusive** column, and `NOTES.md` §4d
explicitly forbids quoting it as entry 23's null. **Entry 23's null for p49 has
never been computed. It is not zero:**

```
R4/R5 null = verus - unsafe, marginal_ir_per_call, results/gate/p49-interned-pool.json
  O0 isolated   small +0.00   large +0.00   d_ir_d_work +0.00
  O0 whole      small +0.00   large +0.00   d_ir_d_work +0.00
  O3 isolated   small -1.00   large -1.00   d_ir_d_work +0.00
  O3 whole      small -3.23   large +55.57  d_ir_d_work +0.31
```

At `-O3 isolated` — the level entry 23 publishes — p49 reads **−1.00**, below the
`2.00` band, so it does not join `p25/p42/p04/p03/p02`. At `-O3 whole` its
`+55.57` would be third-largest in that mode's list. ⚠ **Note it is non-zero even
though `identity` is `exact` at `-O3`** — the kernels are byte-identical
(`md5_raw 563ecf2f…` on both) and the slope still differs, which is entry 23's
whole point demonstrated on a fresh row. **Worth `.memory/`, stated per (level,
mode) cell.**

---

## 5. Item 1 — the `p08` distinction: SURVIVES, NARROWED

**The row does not fall.** The two C mechanisms are different in kind:

* `p08` — the overlap is between **the two arguments of one library call**, lasts
  for that call, is **UB** (C11 7.24.2.1p2), arises from arithmetic
  (`2*dr < m`), and the repair is a **different function**.
* `p49` — the sharing is between **two long-lived record handles**, is created
  deliberately by a dedup table, is **correct C**, persists across operations,
  and the repair is an **ownership test before a write** that costs storage and
  can refuse.

⚠ **But *partial vs total* is the WEAKEST way to say it, and it is the way the
row says it.** If p49's two records held *partially* overlapping ranges it would
still not be p08 — p08's overlap is not between two objects at all. And p49's
`0 PARTIAL` is a theorem of the dedup code (MAJOR 4a), so it cannot come out any
other way. **The distinction the row should lead with is the one it lists third:
what the two overlapping things ARE, and whether the overlap is UB.**

**On the attack nobody had tried — *is `aliasing` the wrong class rather than a
widened one?*** See item 2. **`p32` and `p28` do not threaten the row**: `p32`'s
alias is created BY the bug and its block has been RECYCLED, and its safety line
asks a **lifetime** question (`gen[h] != g`); `p28`'s alias is the SETUP for a
use-after-free and its safety line is a maintaining write. p49's alias is the
**contract**, nothing is recycled or freed, and the line asks an **ownership**
question. Three distinct positions, as the caveat says.

---

## 6. Item 2 — the classification (PROTOCOL rule 3: this is the manager's, so I attack it)

**`aliasing` is the right bucket and the widened DESCRIPTION is defective.**

For `aliasing`: `composition.py`'s own stated test is *what does the SAFETY LINE
ask?*, and `if (rshd[t])` asks an ownership question about a live alias. The test
applies **cleanly** here — unlike `p28`, `p34` and `p35`, whose caveats all say
the test does not apply and the class is read off the harm. And `logical`'s three
members (`p04`, `p06`, `p19`) genuinely have no aliasing structure: I checked
`p06`'s kernel (`memcpy` into a private `scr[64]`, three in-place reverses — no
second referent), and `p04`/`p19` likewise. That part of the caveat is a **clean
negative**.

For `logical`: it is literally satisfied — 216 sanitizer cells + 18 Miri cells,
0 diagnostics, nothing allocated, nothing freed, every index in bounds.
**If the manager took `logical`, what it would cost the row** is its mechanism:
`logical` says only *"wrong answer, memory-safe throughout"*, which is true of
p49 and says nothing about deduplication, ownership or the write-through — and
the row's whole novelty is that the aliasing is the **contract**.

**The narrowing, and it is the real finding here.** Every other class in
`CLASSES` names an **error condition**:

```
spatial   "an access outside the object"
logical   "wrong answer, memory-safe throughout"
temporal  "the ACCESS OUTLIVES THE OBJECT'S LIFETIME"
type      "the bytes are read at a type they were not written at"
resource  "a resource acquired and not released"
```

After widening, `aliasing` names a **structure**: *"two live references to
overlapping storage, one of them mutable"* — which is **not an error in C at
all**, and is p49's *contract*. ⚠ **It is also, as written, a Rust-model
criterion rather than a C one**, which sits awkwardly beside `CLAUDE.md` rule 6's
insistence that this project reason C-side. **The repair is one clause and I do
not apply it**: state the shared ERROR, e.g. *"a write through one reference is
observed through another"* — which covers p08 (the `memcpy` destination write
observed through the source range) and p49 (the `BREAK` write observed through
the other record) — and keep the existing UB-vs-not sentence as the split.

---

## 7. Item 3 — `model.py` attacked hardest, and it holds

**The strongest thing I can say is that I wrote my own kernel and it agrees.**
`.temp/t162/refmodel.py` is a third implementation, written by me from
`c/kernel.h`'s pseudocode contract and the two `c/kernel*.c` files, **not** from
`model.py`. `.temp/t162/cmp_model.py`:

```
A. refmodel vs the SHIPPED C BINARIES, whole program, all 9 inputs x {R1, R1h}
   mismatches: 0

B. per WINDOW: refmodel vs model._sim_window(harden=True) vs model.intern_fold
   windows compared: 78 (every window of every shipped blob)   disagreements: 0

C. 20 000 RANDOM windows x BOTH semantics
   disagreements: 0
   corpus coverage: sent_nrec_full 11150 · sent_arena_full 53 · sent_priv_full 307
                    born_shared_new 33106 · born_shared_hit 2601 · born_owned 34939
                    break_total 32574 · break_on_shared 11375
                    cow_refused 152 · cow_done 11223
```

The random corpus exercises **every arm**, including the two the shipped corpus
does not (`sent_arena_full`, `cow_refused` at volume). **Zero disagreements.**

**Is it a transliteration (`TASK_136`'s defect)?** Half of it is, and the
docstring says so. `_run_spec`/`intern_fold` **is** an offset-for-offset
transliteration of `c/kernel_hardened.c` — but it is **not** the oracle: the
gate's `expected_stdout` comes from `_sim_window`, which is genuinely
object-shaped (buffers with identity, a `dict` intern table, `arena_used` and
`priv_used` integers, **no offset arithmetic anywhere**). The two are compared
against each other in `selfcheck()`, so the transliteration is the *checker*, not
the *answer*. That is the right way round.

**Is any check a tautology of the representation (entry 19)?** No, and the one
place it could have been is **declared**: `Detector.published` coincides
extensionally with `rshd[t] == 1`, and `model.py:49-56` says so in terms
(*"Said plainly rather than dressed up"*). What makes it evidence rather than
restatement is that it is computed from the table contents and the record list —
neither of which carries a flag — and that `detector_selftest()`'s middle probe
(`_PROBE_LONE`: an interned record **no other record names**) makes `aliased` and
`published` answer **differently**. I re-derived all three probes by hand and
they do what the docstring says.

**Is `sanitizer_expect` declared?** Yes, `return "clean"` outright with the
argument beside it — `p01`/`p08`/`p22`/`p47`'s shape, which entry 19 calls
honest.

**Break it deliberately** — MINOR 7 above: 8 mutations, 6 REPORT, 0 CRASH, 2
silent.

⚠ **One coverage note that is NOT a defect**: `selfcheck()`'s
cross-implementation comparison runs on `sample_calls(8)`, which samples the
**driver orbit**, so it touches only **7 of 64** distinct windows on `large.bin`
and 5 of 8 on `small.bin`. The orbit itself visits **all** windows (64/64, 8/8),
so the *checksum* comparison against the eight built cells covers everything; and
my own run compared all 78 windows plus 20 000 random ones and found nothing.
**Clean negative — do not re-run it.**

---

## 8. Item 4 — the positive controls, hand-verified

`controls/detectors.json`: **36 control cells, 36 `ok`, 16 fired**, in exactly
the pattern the `CONTROLS` table declares; **216 kernel cells, 0 diagnostics**;
`problems: []`; all 9 `derived_from_sha256` entries re-hash clean against the
tree.

I rebuilt and ran all three controls myself at `-O3` on **both** compilers
(`env -u LD_PRELOAD`, `ASAN_OPTIONS=detect_leaks=0`), 12 cells:

```
ctl_asan        gcc/clang  O3 asan   -> ERROR: AddressSanitizer: heap-use-after-free
ctl_asan        gcc/clang  O3 ubsan  -> silent
ctl_asan_stack  gcc/clang  O3 asan   -> ERROR: AddressSanitizer: stack-buffer-overflow
ctl_asan_stack  gcc/clang  O3 ubsan  -> runtime error: index 64 out of bounds ...
ctl_ubsan       gcc/clang  O3 asan   -> silent
ctl_ubsan       gcc/clang  O3 ubsan  -> runtime error: signed integer overflow
```

✅ **`TASK_160`'s elimination hazard did NOT recur.** `objdump` of
`ctl_asan.gcc.O3.asan`'s `main`:

```
call 10e0 <malloc@plt>
call 1120 <free@plt>
call 10d0 <__printf_chk@plt>
call 1110 <__asan_report_load1@plt>
```

Both the `malloc` and the `free` survive gcc `-O3 -fsanitize=address`.

✅ **The disclosed expectation correction is real and the record matches**:
`ctl_asan_stack` fires under **UBSan** as well as ASan, 4/4 in each, on both
compilers at both levels. The `CONTROLS` table encodes the measurement, not the
original guess.

⚠ **And the fortify hazard that bit `p08` cannot bite here**: neither C rung
contains a `mem*`/`str*` call at all. `objdump` of `<kernel>` at `-O3`:

```
gcc   kernel.c  282 insns   1 call: __stack_chk_fail@plt
gcc   kernel_hardened.c 418 insns   1 call: __stack_chk_fail@plt
clang kernel.c  365 insns   0 calls
clang kernel_hardened.c 498 insns   0 calls
```

**No libc call, so no `_chk` rewrite and no kernel-exclusive leakage.** MINOR 9
notes the one loose sentence about build flags.

---

## 9. Item 5 — the safe-Rust headline

**Is the `RefCell` arm an honest port?** Yes. I read it line by line
(`controls/arm_rc_refcell.rs`): `Rc<RefCell<Buf>>`, deduplication is `Rc::clone`,
the write is `recs[t].0.borrow_mut().data[0] = 0`, the ownership flag is carried
only for the checksum with a comment saying so, and the capacity tests translate
faithfully (`priv_used + w > MEM - ARENA` ≡ C's `pbump + w > MEM`). Nothing is
bent to match; the correspondence follows from the port being literal.

**The negative control exists, runs, and prints the same code — confirmed
independently.** I compiled all three arms myself, plus a fourth I invented
(`let mut r = Rc::new(5i32); *r = 6;` — because a reviewer should check the
`mut`ability is not what is doing the work):

```
Rc<Buf> write-through            error[E0594]: cannot assign to data in an `Rc`
NEGATIVE CONTROL (Rc<i32>)       error[E0594]: cannot assign to data in an `Rc`
NEGATIVE CONTROL (let mut)       error[E0594]: cannot assign to data in an `Rc`
```

**`E0594` is NOT distinguishing** — fifth instance, correctly reported, and
`safe_arms.json` records `error_code_distinguishes: false`.

**What falls**: *"one type apart"* — MAJOR 3. **What narrows**: `9/9` → 5 of 9
discriminating — MINOR 8.

---

## 10. Item 9 — the R5

**The battery's nine arms**: I did not re-run all nine (they are one Verus run
each); I re-ran the two the report flagged as open, plus arms the battery lacks.

**`requires false` liveness battery — 11 arms, ALL FAIL. Nothing in the R5 is
dead or vacuous.** (`.temp/t162/vmut/`, `--rlimit 200`; the only edit besides the
planted clause is `#[path]` made absolute so a mutant can sit in `.temp/t162/`,
and the control confirms that edit is inert.)

```
V0-control                34 verified, 0 errors                                <-- inert edit
V2/L-fold_bytes           32 verified, 2 errors   precondition not satisfied
L-find                    33 / 1                  while loop
L-fill                    33 / 1                  precondition not satisfied
L-copy_bytes              33 / 1                  precondition not satisfied
L-cbyte                   33 / 1                  precondition not satisfied
L-buf_get_unchecked       32 / 2                  precondition not satisfied
L-arr_get_unchecked       29 / 5                  precondition not satisfied
L-arr_set_unchecked       31 / 3                  precondition not satisfied
L-lemma_find              33 / 1                  precondition not satisfied
L-lemma_rec_in_pool       32 / 2                  precondition not satisfied
L-lemma_copied_below      33 / 1                  precondition not satisfied
```

Every verified helper, every trusted wrapper and every proof lemma has **at least
one live call site**, and the counts say how many.

**`assume(false)` at the top of `kernel`: `34 verified, 0 errors`.** So Verus
alone would accept it — the R5's protection against this arm is entirely
`harness/check.py`'s `assume(`/`admit(` shout (`check.py:4485-4537`, word-anchored
and self-tested at `check.py:896-901`), and `spec.md` declares no
`verus.assumptions`. `results/gate/p49-interned-pool.json`'s `loud` carries only
the known `arr_set_unchecked` parameter-coverage false positive. **Clean negative
— the mechanism exists and is armed; do not re-run this.**

**`M1`'s failure site: still not established, and I did not establish it.** I did
not spend a 25-minute-plus run on it. The engineer's withdrawal of the
*"postcondition"* claim stands.

**`lemma_rec_in_pool` is a HINT, not load-bearing: CONFIRMED, and now from two
sides.** `M4` (delete both calls) verifies; my `L-lemma_rec_in_pool` (`requires
false`) fails at **2** call sites. So the calls are present and live, and the
facts they export are derivable without them.

✅ **The new Verus fact RE-DERIVES EXACTLY. I rebuilt all four cells of the 2×2
from the shipped `verus.rs` using `proof_mutants.py`'s own substitution texts
(so the two cannot drift), at the DEFAULT rlimit** (`.temp/t162/bisect/`):

```
lemma_rec_in_pool calls   lemma_find's 2nd ensures    result
  present                   TWO clauses               34 verified, 0 errors    <- shipped
  ABSENT                    TWO clauses               34 verified, 0 errors
  present                   ONE clause (`A && B`)     34 verified, 0 errors
  ABSENT                    ONE clause (`A && B`)     33 verified, 1 error
                                                      while loop: Resource limit (rlimit) exceeded
```

**`A && B` in one `ensures` clause is NOT `A`, `B` as two clauses for the
solver.** Two independent sufficient hints; the shipped file carries both.
⚠ **Scope it honestly when it lands in `.memory/04-verus.md`: this is a claim
about the solver's SEARCH at a given budget and a given Verus/Z3 pin, not about
provability.** It reproduced on a second, independent run here.

**TCB recount**: exactly 5 `#[verifier::external_body]` items —
`buf_get_unchecked` (505), `load_input` (528), `emit` (537),
`arr_get_unchecked` (546), `arr_set_unchecked` (567). The three `slb_twin_*`
functions are **not** `external_body`, so *"three of the five carry verified
twins"* is right. **No `assume`, no `admit`, no `assume_specification`, no
`external` anywhere.** `--cfg slb_twin` re-run: **37 verified, 0 errors**.

---

## 11. Clean negatives — named so nobody re-runs them

1. **`model.py` is not wrong.** Third independent implementation, 9 whole-program
   cells + 78 shipped windows + 20 000 random windows × 2 semantics, **0
   disagreements** (§7).
2. **The re-gate is essentially value-free on this pattern.** `check.py p49`
   re-run: `PASS`, same `contract_sha256`. Record diff vs `HEAD`: **1410 leaves,
   2 moved**, both `/miri/runs[*]/seconds`. **0 of the `marginal_ir_per_call`
   cells moved** — against entry 21's tree-wide 673-of-2772. Record restored to
   `HEAD` (`sha256 9f280c10…`).
3. **Every published `Ir` figure in `NOTES.md` §4a, §4b, §4e (bar the `0.99`
   typo), §5 and §4f re-derives EXACTLY from `results/p49-interned-pool.json`.**
   All 24 cells of §4a, all 8 deltas of §4b, all 4 rows of §5, both static counts
   (`safe_naive` 731 / `safe_tuned` 1216), `md5_raw 563ecf2f…` identical on
   `unsafe` and `verus`, and `safe_tuned`'s `bulk_calls: ["memmove@GLIBC_2.2.5"]`.
4. **The R3 lever is NOT confounded by the `memmove`.** `copy_within` sits in the
   copy-on-write path only (`safe_tuned.rs:149`), and **no benign input executes
   it** (`break_on_shared = 0` on all three matrix blobs). The `memmove` symbol is
   present statically and never called in a measured cell.
5. **`controls/no_share_break.py` is reproducible.** Re-run: every row identical,
   only `measured_utc` moved. JSON restored from `HEAD` (`914e0c46…`).
6. **PROTOCOL rule 6's chain re-derives, completely, for the first time in this
   project.** All five states in `.temp/t161/contract_step*.json` re-serialise
   (`json.dumps(obj, indent=2, ensure_ascii=False) + "\n"`) to their disclosed
   digests **exactly**, the fifth is **byte-identical** to the shipped block, and
   that equals the gate record's `contract_sha256 d339ef90…`. The key-by-key
   disclosure is exact too: leaf-diffing the five objects gives
   `4 → 1 → 1 → 1` moves and `first → shipped` moves **exactly four leaves**
   (`required[0].rust`, `required[1].c`, `required[5].c`, `why`).
   `requires`, `ensures`, `forbidden`, `verus.obligations`,
   `verus.twin_obligations`, `verus.items`, `driver`, `collapse`, `identity` and
   `miri` are byte-identical from first-written to shipped.
7. **No dangling file citation in the whole pattern.** 187 distinct
   `*.py|rs|c|h|md|json|bin|log` strings extracted and resolved; the 42
   "unresolved" are all regex artefacts (`self.c`, `re.c`, `s.rs`), system
   headers, files in `common/`/`harness/`/`.tasks/`, control-generated scratch
   under `.temp/p49ctl/`, or things the text explicitly says are absent
   (`safe_naive_verus.rs`, p08's gitignored blobs).
8. **The obligation and file-size census re-derives.** p49 34 · p29 25 · p34 24 ·
   p28 23 · p46 21 · p22 20 · p32 15 · p25 10 · p04 9; `verus.rs` lines p28 1709 ·
   p29 1494 · p34 1183 · p49 1126.
9. **`logical`'s three members really have no aliasing structure** — checked
   `p06`'s kernel directly, not just its title.
10. **`NOTHING ADMITTED REMAINS UNBUILT` is true** — swept all 49 catalogue rows.
11. **The `0 PARTIAL` census is honest about its own vacuity risk**: it fails if
    `equal == 0`, and it fails if the p08 arm finds no partial overlap. Both arms
    are live (11 084 equal; 9 partial).
12. **`--check-stale` 66/0**, **`composition.py --check` OK 33/10**,
    **`contract_diff.py p49` UNCHANGED**, **citation sweep clean**.

---

## 12. What I did NOT do

* Did not re-run the full nine-arm `proof_mutants` battery (one Verus run each);
  I re-ran the 2×2 bisection and added 12 arms of my own instead.
* Did not establish `M1`'s failure site.
* Did not regenerate `results/synthesis.md` (§3 says it needs it).
* Did not price the `Rc` arms — the report already says they carry no number.
* Did not run the `--sweep` bands, a second in-contract R3 spelling, `-O0d`, or
  `--panic abort`; all remain open exactly as `NOTES.md` §10 says.
* Did not attempt a clang-side line decomposition beyond establishing that it is
  untrustworthy (19 % unidentified lines).
* Did not check whether the `assume(`/`admit(` shout would fire on my
  `V1-assume-false.rs` through a real gate run — I read the code and the
  self-test rather than re-gating a planted tree.

---

**PROTOCOL rule 2 running count: launched from 916, +4 = 920.**
The four: *(1)* `NOTES.md` §10 assumption 3 — *"without the flag fold,
`provenance` and `cow` would be indistinguishable on benign input"* — **false**,
2 of 3 benign checksums still move (§0); *(2)* *"the two `Rc` arms differ in ONE
TYPE"*, in `spec.md`'s hashed `why` and four other places — **false**, and
stripping the extra block lands the arm on neither C rung (MAJOR 3); *(3)*
`CAVEATS["p49"]`'s *"the tree's only row with NO DETECTOR AT ALL"* — **false**,
`p22` and `p47` have none either (MAJOR 4b); *(4)* `NOTES.md` §4c's *"the
decomposition does NOT close"* — it **does**, at line level, and the guard costs a
constant 2.00 Ir per evaluation under both compilers at `-O3` (MAJOR 6).
⚠ Two of the four are the ENGINEER's, two are the MANAGER's, and MAJOR 1
(`README.md` inheriting the refuted mechanism) is the manager's claim surviving
inside the engineer's file.
⚠ **Reconciliation across branches is the manager's job, not mine.**
