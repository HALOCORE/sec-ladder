# TASK_122 — review report: finding 41 does not survive, and the 18.9 M drift is not the box

**Role: research reviewer.** Adversarial. I did not fix anything. §B is the one
measurement I was told to actually run, and I ran it.

**Did NOT run** `harness/check.py`, `build.py` or `measure.py` (not even
`--check-stale`); did not read `results/`, `synthesis/` or `harness/check.py`.
Every probe was built with direct `rustc` under `.temp/r122/`. No `/tmp`.
No `git add`/`git commit`; read-only `git` only.

---

## VERDICT, in one paragraph

**Finding 41 does not survive, and it fails harder than finding 40 did.**
Finding 40 was wrong about a *tally*; finding 41 is wrong about a *category* and
about a *control*. `LADDER`+`COST` is not one family: it is four things, of which
**exactly one row in twenty-two (`p40`) is a genuine instrument limit**. The
sentence *"the five-rung ladder has nothing to price on it"* is literally true of
**4 of 22**, not 7 — and it does not discriminate, because **8 of the 26 BUILT
rows publish a zero on their own headline axis**, and `p46` — the 24th built
pattern — ships *"the safety tax is `0.00000` per MAC"* **and** *"The rung
boundary did not shrink; it VANISHED"* **as RECAP finding 36**. The catalogue's
own probe block already says why: *"A zero with a named axis and a mechanism is a
FINDING; a zero because two rungs compiled to the same bytes is an artefact."*
Finding 41 merges precisely the two things probe 3 separates. **Recommendation:
keep the 22-row classification, publish NO generalisation over it** — which is
the manager's own "least sure #1", and it is right. **§B: the 18.9 M drift is not
the box.** Package state, `valgrind`, `rustc` and `libc` all predate `TASK_086`;
the build is bit-reproducible across paths; the environment accounts for 62 K.
Deleting **one setup array** from the shared probe source drops the total by
**18,874,783** against a drift of **18,870,383** — 0.023%. The probe source is
`.temp/`-gitignored, so *"byte-identical pipeline"* was checked against today's
copy and is **unverifiable in principle**.

---

# §A — the attack on finding 41

## A0 — the prior art's own assert FIRES. Finding 41 no longer reproduces its own tally.

```
$ python3 .temp/r120/classify22.py
TRIGGER CHECK FAILED (the cells moved under this classification):
  p43: TRIGGER NOT FOUND -> 'i.e. **`p16` verbatim.**'
```

`p43`'s trigger was struck at `21787d5` — the commit that landed `TASK_120`
itself. ✅ **The instrument is sound and this is it working**; but it means the
7-of-22 tally cannot be re-derived from the current catalogue by the script that
produced it. Anyone re-running finding 41's evidence gets an error, not a number.

## A1 — `blocker`: `COST` is not one category, and only 1 of 22 is an instrument limit

`classify22.py` defines `COST` as *"the cost axis is flat, **zero, false**, or
below the instrument"*. Those are four different facts about the world, and
finding 41 **adds them to `LADDER` and reads the sum as one property of the
instrument**. They decompose:

| sub-kind | what actually happened | whose property is it? | rows |
|---|---|---|---|
| **FLAT** | the rungs are **the same program** — one rung, byte-identical, no boundary | the **language/compiler**: LLVM discharges the bound, or `wrapping_*` *is* the unchecked op at `-O` | `p24` `p44` `p45` |
| **BELOW** | the axis is **real** and the primary metric **cannot see it** | ⭐ **the INSTRUMENT** — the only true member | `p40` |
| **SCOPE** | the axis is real, measured, **NONZERO**, rejected for being `O(1)` not `O(n)` | a **project taste criterion** | `p20` `p43` |
| **false** | the row's own distinguishing **cost claim was measured false** | the **proposal** — this is `NOVELTY`'s definition verbatim | `p41` |

- **`p20` is priced to the instruction.** Its cell: `+6.00 Ir`/call marginal,
  `+7.00` kernel-exclusive, *"exactly the seven inserted instructions"*. The
  ladder priced it perfectly. It died because the price is `O(1)`.
- **`p41`'s own cell disclaims the ladder in as many words**: *"the row dies on
  probe 3 and on duplication, **NOT on the ladder test**"*, and *"Probes 1, 2 and
  4 all PASS"*. **Finding 41 counts, as evidence that the ladder is the problem,
  a row whose cell says the ladder is not the problem.**
- **`p40` is the real thing** and deserves its own sentence — which finding 40
  already gave it.

⚠ **So `7 of 22` splits.** Under the finding's own sentence — *"the five-rung
ladder has **nothing to price** on it"* — the true count is `FLAT + BELOW` =
**4 of 22 (18%)**, and the instrument-limit count is **1 of 22 (4.5%)**.

## A2 — `blocker`: the CONTROL ARM. The property does not discriminate.

`classify22.py` classifies only the 22 **refused** rows. That is selection on the
dependent variable: finding 41 claims the property **predicts** refusal, and a
predictor must discriminate. Nobody checked the built rows.
`.temp/r122/reclassify22.py` does, quoting each built pattern's **own** `NOTES.md`:

```
=> 8 of 26 BUILT rows publish a ZERO safety cost on their own headline axis.
  p04 'per operation: 0.00000'          p16 'slope 0.0000000'
  p08 'costs zero there'                p17 'R3 costs zero per byte'
  p09 'costs ZERO instructions on every rung'   p27 'temporal property costs zero'
  p13 '0.00000 Ir per byte'             p36 'a Verus proof costs zero executed'
```

⚠⚠ **And the sharpest one is `p46`, the 24th BUILT pattern, whose PUBLISHED
finding — RECAP finding 36 — is BOTH halves of finding 41's kill criterion:**

> **p46 — the safety tax is `0.00000` per MAC** … **The rung boundary did not
> shrink; it VANISHED.**

`p33`, `p44` and `p45` are **refused** for those two properties. `p46` was
**built and shipped** on them. **A property that is the headline of a shipped
pattern cannot be the reason 7 rows were refused.**

## A3 — `major`: the catalogue's OWN probe block already draws the line finding 41 erases

`.memory/06-catalogue.md`, *"The three probes"*, **probe 3** is **not a cost-kill
criterion**. It is a *disclosure* rule:

> **3. Any published `0.00` must name its AXIS and its CONVENTION in advance.**
> … **A zero with a named axis and a mechanism is a finding; a zero because two
> rungs compiled to the same bytes is an artefact — and only probe 2 tells them
> apart.**

**That is exactly the FLAT/BELOW distinction, already written down, already
reviewed** (restated at `TASK_081_REVIEW`), and finding 41 merges the two sides
of it into one instrument property. It also means `p41`'s cell's *"dies on probe
3"* is a **misuse of probe 3's name** — `p41` publishes no `0.00`; it published a
`9.6×` that was refuted.

## A4 — `major`: "the five-rung LADDER" is silently narrowed to the `Ir` COLUMN

`CLAUDE.md`, line 5, defines the instrument: *"compared on **assembly,
instruction count, timing, proof burden and trusted-base size**"* — **five
axes**. Finding 41 evaluates **one**. Four of the refused rows carry a measured
result on the proof-burden / TCB columns:

```
p15 REFUSED, yet '5 verified, 0 errors'  (+ zero trusted items, a verified UTF-8 validator)
p24 REFUSED, yet '6 verified, 0 errors'  (+ 7 of 8 mutants fail, a firing vacuity control)
p28 REFUSED, yet '8/0'                   (+ zero TCB, address injectivity load-bearing)
p29 REFUSED, yet '9 verified, 0 errors'  (+ TCB 0, three-case remove with in-order successor)
```

**`p24` is inside finding 41's seven.** Its cell says *"no measured safety tax"*
— true of the `Ir` column — while the same cell records a full R5 result with a
mutation battery and an anti-vacuity control. **Calling that "the ladder has
nothing to price" is the finding redefining the ladder as one of its five
columns without saying so.**

## A5 — `major`: my own re-classification, and it produces a THIRD top family

`.temp/r122/reclassify22.py` (verbatim triggers, all 22 asserted present):

```
NOVELTY   6  p15 p29 p30 p31 p41 p48
DUP       5  p21 p26 p28 p33 p39
FLAT      3  p24 p44 p45
SCOPE     2  p20 p43
ADMIN 1 p32 · BELOW 1 p40 · GATE 1 p35 · NONE 1 p25 · PIN 1 p34 · REPR 1 p37

finding 41's seven : p20 p24 p33 p40 p41 p44 p45
  I agree on       : p20 p24 p40 p44 p45
  I disagree on    : p33 p41
  I add            : p43
RANKING STABILITY  top=(6,'NOVELTY')  second=(5,'DUP')  margin=1
```

Where I disagree, in the cells' own words:

- **`p33` — `DUP`, not `LADDER`.** The cell's turn is *"**But that makes the class
  `p04`'s** … and the harm framing `p48`'s, which is refused"*. Probe 1 arrives
  next and is flagged *"**AND** PROBE 1 KILLS BOTH **INDEPENDENTLY**"* — the word
  *independently* marks it as an additional kill, not the first one.
- **`p41` — `NOVELTY`, not `COST`.** *"the apparent `9.6×` was 100% R3
  SPELLING"* is `classify22.py`'s own `NOVELTY` definition (*"the row's OWN
  distinguishing claim was MEASURED FALSE"*), and the cell disclaims the ladder.
- **`p43` — belongs in the family and is missing from it.** Its current text,
  written by `TASK_120` itself, is *"it needs a NEW reason, and **a hoisted O(1)
  length check** is the honest one"* — `p20`'s `SCOPE` shape exactly. ⚠ **But the
  cell also says the row currently has NO settled reason**, so counting it in any
  bucket counts an unadjudicated row.

⚠⚠ **The stability result is the one that matters, and it does not depend on my
read being right.** Three readers have now classified the same 22 cells:

| reader | claimed top family | count |
|---|---|---|
| manager (finding 40) | `DUP` | 7 of 22 — membership wrong 3 ways |
| `TASK_120` (finding 41) | `LADDER`+`COST` | 7 of 22 |
| `TASK_122` (this) | `NOVELTY` | 6 of 22 |

**The top-to-second margin is 1 in every reading.** A superlative — *"THE most
common thing wrong with a remaining row"* — needs a margin that no single
defensible re-reading can close, and **three readers have each moved 2–5 rows**.
**The tally cannot carry a superlative. It can carry a list.**

## A6 — `major`: §A.3's selection effect, dated in `git`, and it lands on the sentence `TASK_120` TRUSTED

`TASK_120` caught `p20`'s *duplication* clause as an appended *"a fortiori"*
reason and elevated the row's *cost* sentence as its true, prior kill. **`git`
says both sentences entered the file in the same commit:**

```
p20 "A length/offset check is O(1) and does not scale"  -> 7f01a72  (= TASK_115)
p20 "a fortiori"                                        -> 7f01a72  (= TASK_115)
p40 "THE ROW'S OWN AXIS IS INVISIBLE ..."               -> 7f01a72  (= TASK_115)
p41 "the row dies on probe 3 and on duplication"        -> 7f01a72  (= TASK_115)
p43 "a hoisted O(1) length check"                       -> 21787d5  (= TASK_120 itself)

$ git show 7f01a72^:.memory/06-catalogue.md | grep '^| p20 '
| p20 | length/offset pair validation (heartbeat-style) | … | moderate | planned |
```

⚠⚠ **`p20`'s cell was the bare word `planned` one commit earlier.** So *"the
row's OWN stated kill"* and *"the reinforcing clause appended by an agent who
already knew the built tree"* are **the same vintage, the same agent, the same
commit**. `TASK_120` treated one as evidence and the other as contamination.
**Three of finding 41's seven triggers (`p20`, `p40`, `p41`) were written in the
one commit that landed finding 40, and a fourth (`p43`) by the review that then
counted it.** The selection effect `TASK_120` diagnosed applies to `TASK_120`.

## A7 — ✅ named attacks that did NOT land. Do not re-run these.

1. *"The 22/26 split is wrong — some 'built' dir is not a pattern."* ✗ 26 built
   dirs, 48 catalogue rows, 22 non-built. Exact.
2. *"`p44`/`p45`'s one-rung result is probe 2's known-broken object-file form."*
   ✗ Already settled at `TASK_086`/`TASK_100`; `p45`'s kernels are leaf
   arithmetic folds with no relocations, and the catalogue says so.
3. *"`p24`'s byte-identity is the `.o` false positive."* ✗ Its cell records the
   linked shipped pair (`md5_fn 3d37ca7b…` both, `n_nopad 133` both).
4. *"Finding 41's `7` is arithmetically wrong."* ✗ It is 7 under
   `classify22.py`'s own buckets. The defect is the buckets, not the addition.
5. *"`p37` belongs in finding 41's family."* ✗ It is an instrument limit
   (**Verus representability**) but **not a pricing limit** — it has a measured
   cost axis (`21/20/18 Ir`/record, tag check `+2.00`). Adding it would make the
   family *more* heterogeneous, not less.

---

# §B — the 18.9 M `Ir` drift. Measured, and it is **not the box**.

Run in the order the task specified; stopped at the first thing that explains it.

## B1 — the invocation and the environment block. ⚠ Ruled out, but the recorded band is 4 orders too small.

`.temp/t86/p40_cache.sh` and `TASK_120`'s re-run use the same parameters
(`N=1048576`, 3 iterations, seed `12345`, `--cache-sim=yes`,
`--callgrind-out-file=/dev/null`). Same binary, same argv, environment varied
(`.temp/r122/envsweep.sh`; arm that must fire = `env -i`, which strips it all):

```
full-env               Ir=378984608
env-i                  Ir=378922731     <- -61,877
env-i+pad100           Ir=378923285
env-i+pad1000          Ir=378923285     <- byte-equal
env-i+pad8000          Ir=378923285     <- byte-equal
full-env+pad8000       Ir=378985122
```

**⚠ `minor`, and it is a correction to the section this task is reviewing.** The
environment block moves a **whole-program TOTAL by ~62,000 `Ir`**. The project's
recorded figure is **±7**, and that figure was measured on a **MARGINAL** — a
difference, in which every common term cancels.
`.memory/03-measurement.md`'s new *"~100 `Ir`"* band is therefore right **only
for same-binary, same-environment comparisons**, and the section does not say so.
Across environments the floor is **~6 × 10⁴**, not ~10².
✅ **Ruled out as the drift: 300× too small.**

## B2 — binary or box? **Neither.** The binary is bit-reproducible and the box has not moved.

```
sources     md5 64e61abcf445…  cost.rs   identical  .temp/t86 == .temp/r120 == mine
            md5 906319a8107b…  probe2.rs identical  (same three)
flags       .temp/t86/build.sh : rustc -O -C codegen-units=1 -o cost cost.rs   <- identical
binary      md5 97400f4a94a7…  IDENTICAL when built at two different path lengths
```

**The box, checked rather than assumed:**

```
/var/log/dpkg.log             mtime Aug 15 13:36   (no package change since)
/lib/.../libc.so.6            Jan 30 2026,  glibc 2.39-0ubuntu8.7
~/tools/valgrind/bin/valgrind             Aug 15 11:17   } binaries, not
~/tools/valgrind/libexec/.../callgrind-*  Aug 15 11:17   } just version strings
~/.rustup/toolchains/1.97.1-*/bin/rustc   Aug 15 10:16
CPU  Intel Xeon Gold 6230 (avx / avx2 / avx512f / erms)
```

**All of it predates `TASK_086` (Aug 24).** The `glibc`-upgrade and
IFUNC-reselection hypotheses are dead before they were published.

**Third independent run**, my build, my path (`.temp/r122/b86_run1.log`):

```
k40_aos  Ir=378984608  D1=4005477(2495011rd+1510466wr)
k40_soa  Ir=378984629  D1=2825832(1315366rd+1510466wr)
  Ir delta = 21          <- exact, 3rd independent confirmation
  D1 delta = 1,179,645   <- exact, 3rd independent confirmation
```

✅ **So the drift is REAL and PERSISTENT, and `TASK_086`'s `360,114,293` does not
reproduce** — but the kernel is provably untouched, and nothing in the pipeline
or the box moved.

## B3 — ⭐ the measured mechanism: it is the size of **one setup term of the shared probe source**

`callgrind_annotate` at **zero iterations** (setup only, 374.7 M):

```
130,898,829 (34.94%)  cost::main
 96,469,021 (25.75%)  FlatMap<Range<usize>, Vec<u8>, cost::main::{closure#8}>::next
 56,624,205 (15.11%)  libc.so.6:0xab170
 44,041,310 (11.76%)  malloc
 32,506,703 ( 8.68%)  free
```

`.temp/t86/cost.rs` is a **shared** probe carrying kernels for
p19/p20/p21/p23/p24/p26/p35/p40/p41/p46, and its `main` builds **ten** per-element
setup arrays for all of them. A whole-program total has no cancellation, so
**every array added to `main` lands on p40's denominator in full.** Ablation
(`.temp/r122/ablate.py`; control arm = an unablated copy):

```
v0_control      374,658,566        reproduces the unablated total to 27 Ir (path term)
v1_no_tagged    355,783,783   drop      18,874,783   <-- drift = 18,870,383
v2_no_rle        96,391,507   drop     278,267,059
v3_no_vals      355,084,705   drop      19,573,861
v4_no_raws_tags 354,035,734   drop      20,622,832
v5_no_outb      375,357,177   drop        -698,611
```

**`tagged` matches the drift to 4,400 `Ir` out of 18.87 M — 0.023%.** And
`tagged` is the **one setup term whose own source comment records a mid-session
edit**:

```rust
// ⚠ built ONCE, outside the measured loop. Building it inside made
// `k35_tagged` look 2.2x dearer than `k35_enum`; the whole gap was the
// per-iteration Vec construction.
let tagged: Vec<TaggedRaw> = (0..n) …
```

`tagged` is **p35's** array. `TASK_086` probed p35 and p40 in the same session
out of the same file.

## B4 — ⚠⚠ what I am NOT claiming, and why it cannot be settled

**I am not publishing "the `tagged` array was added after p40 was measured" as
the mechanism.** I have measured that **a single setup term of almost exactly the
right magnitude exists**, and that it is the term with a documented mid-session
edit. That is *sufficiency*, not *actuality*.

⚠⚠ **And it cannot be raised to actuality, ever, on this record: `.temp/` is
GITIGNORED.** The `cost.rs` that produced `360,114,293` **does not exist
anywhere**. `TASK_120` compared its copy to `.temp/t86/cost.rs` **as it stands
today**, which is evidence about today, not about the p40 measurement.

> **So the premise *"under a byte-identical pipeline"*, which is what makes the
> drift alarming, is UNVERIFIABLE — not false, unverifiable.** It is asserted in
> RECAP finding 40, in finding 41, and in `.memory/03-measurement.md`.

**The claim that should be struck is *"the box is not as stable as the record
assumes."*** Everything measurable about the box is unchanged, and a
parsimonious, measured-sufficient alternative exists. ✅ **The replacement
conclusion is stronger and is fully supported: a whole-program total taken from a
`.temp/` probe is not reproducible in principle, because the probe sources are
not versioned.**

## B5 — blast radius. ✅ Narrower than feared, and structurally so.

The drift is **entirely in program setup** — the kernel `Ir` delta (`21`) and the
`D1` delta (`1,179,645`) reproduce **exactly** across all three runs. Setup is a
term **common to both arms of every published difference**, because this
project's convention is *marginal whole-program `Ir`/call* — two runs of **one
binary** at two iteration counts, or two argv on one binary.

> **The drift therefore invalidates DENOMINATORS, not DIFFERENCES.**

Against the task's question *"is that the whole list?"*:

- **`p40`'s `21`** — a difference of two argv on one binary ⇒ setup cancels.
  ✅ Survives, and `TASK_120` already re-derived it against a zero-iteration
  control.
- **`p40`'s `193`** — same shape; the real defect was the `println!` name-length
  term, already caught. Not a drift exposure.
- **`p43`'s `+3.00`** — an `n1`/`n2` marginal ⇒ setup cancels.
- **`p40`'s `5.8e-8`** — ⭐ **the one true exposure, because it is the only
  published figure with a whole-program TOTAL in the denominator.**
  `TASK_120` already corrected it to `4.9e-6`. **That is the whole list.**

⚠ **`minor`:** RECAP's headline `18,870,383` differences a **plain-callgrind**
total (`378,984,676`) against a **cache-sim** total (`360,114,293`) — the two
spellings its own new memory section says differ by 60. The like-for-like figure
is **18,870,315**.

---

# §C — the owed one. Both confirmed, and the second is worse than stated.

## C1 — `minor`: the citation IS rotted, to the wrong `.memory/` file

`p39`'s cell: *"a third instance of a real rule (`.memory/03-measurement.md`): of
the `4.25` check tax, `2.00` is the `cmp/jbe` and `≈2.25` is the unroll the panic
exit edge forecloses"*.

```
$ grep -c "2.00 check\|2.00 + 2.25\|4.25 = 2.00" .memory/03-measurement.md
0
$ grep -n  "2.00 check\|2.00 + 2.25\|4.25 = 2.00" .memory/01-ladder.md
847:  So 4.2500 = 2.0000 + 2.2500 with **zero residual**
1148: **4.25 = 2.00 check + 2.25 unroll**, the *identical split* TASK_007_REVIEW
1434: **`4.25000 = 2.00 + 2.25` is now reproduced on a THIRD kernel
2018: Also here: **`4.25 = 2.00 + 2.25` on a fourth kernel**
```

**The rule lives in `.memory/01-ladder.md`.** `03-measurement.md`'s only `2.25`
hits are `p19`'s `2.25·r` **epilogue residue** term — a *different* rule. ✅ **And
`patterns/p14-field-split/NOTES.md:721` cites `01-ladder.md` correctly**, so the
right citation exists in the tree and `p39`'s is the odd one out — rot, not
ambiguity.

## C2 — `minor`: *"third instance"* is **FIVE** built instances, not four

`p39`'s cell reaches *"third"* via *"after `p35` and `p28`, that is a rule"* —
**both UNBUILT**, which is the circularity `p43`'s own cell forbids. The split is
carried by **five BUILT patterns**:

```
patterns/p05-index-flatten/NOTES.md:86   "2.00 check + 2.25 foreclosed unroll"
patterns/p07-binary-search/NOTES.md:430  "(2.00 check + 2.25 foreclosed unroll)"
patterns/p11-nul-scan/NOTES.md:276       "2.00 check (`cmp;jae`) + 2.25 foreclosed unroll"
patterns/p14-field-split/NOTES.md:721    "records `4.25 = 2.00 + 2.25`"
patterns/p16-tlv-walk/NOTES.md:529       "The arithmetic 4.25 = 2.00 + 2.25 is exact"
```

⚠ `TASK_120` said *four*; it is **five**. And `.memory/01-ladder.md` already says
*"a THIRD kernel"* (1434) and *"a fourth kernel"* (2018) **in its own text**, so
the authoritative layer contradicts the catalogue cell that cites it.
⚠ `p16:529` also **weakens** the rule — *"the two terms are not independently
recoverable"* — which `p39`'s one-line restatement drops.

## C3 — ✅ the rot sweep is otherwise CLEAN

```
dangling .memory/ citations, tree-wide : 0
dangling .tasks/*_REPORT.md            : 119, 121, 122, 123 — all IN FLIGHT
  cited from .memory/ or RECAP.md?     : NO (grep -> 0 hits)
```

**PROTOCOL rule 10 is clean.** The four dangling report paths are cited only from
task files pointing at their own future output, which is the intended shape.

---

## Severity summary

| # | sev | where | what |
|---|---|---|---|
| 1 | **blocker** | RECAP finding 41 | `LADDER`+`COST` is **four categories**, not one. Only `p40` (**1 of 22**) is an instrument limit; *"nothing to price"* is literally true of **4 of 22**, not 7 |
| 2 | **blocker** | RECAP finding 41 | **no control arm.** 8 of 26 **BUILT** rows publish a zero; `p46`'s shipped headline (finding 36) is a `0.00000` tax **and** a *"VANISHED"* rung boundary. The property does not discriminate |
| 3 | **major** | RECAP finding 41 | it merges what the catalogue's **own probe 3** separates: *"a zero with a named axis is a FINDING; a zero because two rungs compiled to the same bytes is an artefact"* |
| 4 | **major** | RECAP finding 41 / `06-catalogue.md` `p41` | `p41` is 1 of the 7 and its cell says *"**NOT on the ladder test**"*; its kill is a **refuted claim**, i.e. `NOVELTY` |
| 5 | **major** | RECAP finding 41 / `p33` | `p33`'s first stated kill is *"**makes the class `p04`'s**"*; probe 1 is flagged *"**INDEPENDENTLY**"*, i.e. a second kill |
| 6 | **major** | RECAP finding 41 | *"the five-rung ladder"* silently means *"the `Ir` column"*. `CLAUDE.md` names **five** axes; `p15`/`p24`/`p28`/`p29` carry measured proof-burden results, and `p24` is in the seven |
| 7 | **major** | RECAP finding 41 | **ranking instability**: three readers, three top families, margin **1** every time. The tally supports a list, never a superlative |
| 8 | **major** | RECAP finding 41 §A.3 | the selection effect applies to `TASK_120`: `p20`/`p40`/`p41`'s triggers all entered at `7f01a72` (=TASK_115) — the **same commit** as the *"a fortiori"* clause it condemned; `p20` was bare `planned` one commit earlier; `p43`'s at `21787d5` (=TASK_120) |
| 9 | **major** | RECAP 40/41, `03-measurement.md` | *"the box is not as stable as the record assumes"* is **not supported**. dpkg/libc/valgrind/rustc all predate TASK_086; build bit-reproducible; env = 62 K. A **measured-sufficient** alternative matches to **0.023%** |
| 10 | **major** | `.temp/` policy (`CLAUDE.md` rule 1) | *"byte-identical pipeline"* is **unverifiable**: the p40-era `cost.rs` is gitignored and gone. A whole-program total from a `.temp/` probe is not reproducible **in principle** |
| 11 | **minor** | `03-measurement.md` final section | the *"~100 `Ir`"* band holds only same-binary/same-environment. **Measured: the environment block moves a whole-program TOTAL by ~62,000 `Ir`** — the recorded ±7 was a **marginal**, where it cancels |
| 12 | **minor** | RECAP finding 40, `03-measurement.md` | the `18,870,383` headline differences a **plain-callgrind** total against a **cache-sim** one — the exact mix its own section warns about. Like-for-like: **18,870,315** |
| 13 | **minor** | `06-catalogue.md` `p39` | `4.25 = 2.00 + 2.25` is cited to `03-measurement.md`; it lives in `01-ladder.md` (**0 hits** in the cited file). `p14`'s NOTES cites it correctly |
| 14 | **minor** | `06-catalogue.md` `p39` | *"third instance"* → **five** BUILT instances (p05 p07 p11 p14 p16); the *"after `p35` and `p28`"* corroboration is two **unbuilt** rows; `01-ladder.md` itself already says *"a fourth kernel"* |
| 15 | **minor** | `.tasks/TASK_122.md` vs launch message | the running count is stated as **488** in the task file and **502** in my launch message. Rule 2 says one place; rule 1 says the **manager** reconciles |

---

## Answering the manager's three "least sure" calls

1. **"Should finding 41 have been landed at all?"** — **No, and your own instinct
   is right.** ⚠ **Carry the 22-row CLASSIFICATION and NO generalisation over
   it.** The classification is real, machine-checkable and useful; every
   superlative built on it has now failed twice, by the same mechanism both
   times — *a reason that is always available got read as the reason that was
   operative* — and a margin of 1 across three readers cannot support a
   superlative in principle. **This is respectable and it is what should have
   happened to finding 40.** ⚠ The one sentence worth keeping verbatim is
   finding 40's own `p40` sentence: **`p40` alone is an instrument limit**, it is
   measured twice, and it needs no generalisation to be useful.
2. **"Is §B worth a whole section?"** — **Yes, and it did not eat the task.** §B1
   and §B2 settled the alarming half in about twenty minutes (env = 62 K; every
   pinned component predates `TASK_086`), and the rest bought a **measured**
   mechanism plus finding 10, which is the durable result: **`.temp/` probe
   sources are gitignored, so whole-program totals published from them are
   unreproducible in principle.** That is a process defect, not a `p40` fact, and
   it applies to every future probe. ✅ **And the blast radius is one figure
   (`5.8e-8`), already corrected.**
3. **"Should the project stop? Do I have the dependency backwards?"** — **You
   have it the right way round, and the answer is now determinate.** Finding 41
   was the only *measured* ground for stopping; it does not hold; so **there is
   no stated reason to stop**, and the standing mandate — *"as many realistic C
   patterns as possible"* — is unopposed. ⚠ **But be precise about what my §A
   does and does not license.** It does **not** say the domain is rich; it says
   the 22 rows die for **many good reasons, none dominant**, which closes the
   **CATALOGUE** and says nothing about the **DOMAIN**. ⭐ **So `TASK_123`'s
   enumeration is the main line, exactly as you wrote it** — it is the only
   instrument that addresses the domain rather than the list, and a rigorous
   *"all 20 die, here is why"* would be the first evidence anyone has produced
   about the domain. ⚠ **Run probe 1 first, and do not reuse *"the ladder has
   nothing to price"* as a kill criterion in it** — §A2 shows it does not
   discriminate, and `p46` is the counter-example already in the tree.

## What I did NOT do

- Did not run `harness/check.py`, `build.py`, `measure.py` (not even
  `--check-stale`), and did not read `results/`, `synthesis/` or `check.py`.
- Did not re-adjudicate any row. §A classifies by each cell's **stated** reason,
  exactly as `TASK_120` did. Whether the verdicts are correct is untouched — I
  believe they are, and none of my findings disturbs a verdict.
- Did not re-verify `p46`'s, `p16`'s, `p27`'s or `p36`'s zero-cost measurements;
  the control quotes them from their own `NOTES.md` as **published claims**,
  which is what the control needs.
- Did not run Verus, Miri or any sanitiser. No wall-clock measurement (the tree
  is under concurrent load and wall clock is not immune to it).
- **§B is not closed.** I measured that a setup term of the right size exists; I
  did **not** prove it is what `TASK_086` compiled, and §B4 explains why nobody
  can. ⚠ **Do not let this land as "the `tagged` array explains it."** The
  landable conclusions are: *the box did not move* (measured), *the environment
  is worth ~62 K not ±7* (measured), and *`.temp/` probe totals are
  unreproducible in principle* (structural).
- Did not check whether other patterns' `.temp/` probes have the same
  shared-`main` shape. **`.temp/t86/cost.rs` carries ten patterns' setup in one
  `main`; if other probe files do too, finding 10 is tree-wide.** Untested.

## Memory updates

**None — I am a reviewer and `.memory/`, `RECAP.md`, `results/`, `synthesis/`,
`harness/`, `pilot/` and `patterns/` are untouched by me.** Corrections for the
manager to apply, in priority order: findings 1–8 against **RECAP finding 41**;
finding 9 against **RECAP findings 40 and 41 and `.memory/03-measurement.md`'s
final section**; finding 11 against **that same section's `~100 Ir` band**;
findings 13–14 against **`.memory/06-catalogue.md`'s `p39` cell**.

---

⚠ **PROTOCOL rule 2.** Launched from **502** (⚠ **the task file says 488** — see
finding 15; reconciliation is the manager's job, not mine, so I did not re-add
anything). This branch adds **18**; carried forward as **520**.
