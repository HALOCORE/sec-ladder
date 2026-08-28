# TASK_120 — review of RECAP finding 40

**Role: research reviewer.** PROTOCOL rule 3 — this attacks a design the manager
wrote and may not clear itself. Scratch: `.temp/r120/` (`NOTES.md` + `REBUILD.sh`
regenerate every number below). No `harness/check.py`, `build.py` or `measure.py`
was run; every probe was built with `rustc` directly under `.temp/r120/`. No
`git add`/`commit`. Nothing under `.memory/`, `RECAP.md`, `results/`, `harness/`,
`pilot/` or `patterns/*/` was edited.

---

## VERDICT, in one paragraph

**Finding 40's measured half is confirmed. Its generalisation is not, and the
honest version is a different and better finding.** Duplication is the primary
stated reason for **6 of 22 rows (27%)**, not "the remaining rows"; the seven the
finding tallies are not even the right six (`p20` and `p41` do not belong,
`p28` does); "duplication" names **at least four different relations**; and the
largest reason-family, once ladder-separation and cost-degeneracy are put
together, is **7 of 22 and is a property of the INSTRUMENT, not of the rows**.
**On §B: finding 40 does not license "stop", and by its own last paragraph it
says so. The record contains no argument that the domain is worked out — and it
contains a request for that argument, made by the manager at `TASK_113`, that was
never answered.**

---

# §B — the one with consequences. **THE FINDING DOES NOT LICENSE "STOP", AND NOTHING ELSE DOES EITHER.**

*(Ranked first because the task file ranks it first and because it is the only
section that changes what happens next.)*

## B1 — finding 40 disclaims the conclusion it is being used for, in its own text

RECAP:2263 — *"It does **not** say new patterns are impossible — it says **these
22 rows** are spent."* That is correct and it is the whole of what the evidence
supports. **"The 48-row catalogue is spent" and "there is nothing left worth
building" are different claims, and finding 40 asserts only the first.**

The claim that *did* carry the scheduling consequence was finding 37's
*"NEW ROWS ARE NOT WHERE THE REMAINING VALUE IS"* (RECAP:1847). `TASK_113`
disputed exactly that limb, and RECAP:1797 already records the consequence:
*"**do NOT start a 27th pattern** IS NOW JUSTIFIED BY A FINDING THAT DOES NOT
STAND … it needs a different reason, and nobody has supplied one."*

**Finding 40 is not that reason and does not claim to be. So as of today the
project's direction rests on no stated reason at all.** The manager's box says
this; my review confirms it rather than repairing it.

## B2 — the 47 rows are pre-project, verified in `git`, not inferred

```
$ git log --format=%H --reverse -- .memory/06-catalogue.md | head -1
d5e0ccd1fa77530092c9b560d5a8714f6933607f          # 2026-08-15, the repo's first commit
$ git show d5e0ccd:.memory/06-catalogue.md | grep -c '^| p[0-9]'
47
$ git ls-tree -d --name-only d5e0ccd:patterns
(empty)
```

**47 rows existed before a single `patterns/` directory did.** `p48` is the only
row ever added afterwards (manager, `TASK_066`). **A pre-project list running out
after 26 builds is close to the expected outcome and is not evidence about the
supply of C patterns.**

## B3 — the honest counter-evidence, stated at full strength

**Every row proposed after the project began has been refused: 9 for 9.**

| proposal | when | outcome |
|---|---|---|
| `p48` (uninit info leak) | manager, `TASK_066` | REFUSED `TASK_074` |
| recursion depth, div-by-zero, unaligned load, format string, stack UAR, VLA stack clash, `qsort` comparator, TOCTOU double fetch | `TASK_102`, manager's four + engineer's four | **all 8 REFUSED**, each on a measurement |

`TASK_113` re-ran the eight and confirmed *"no refused row comes back"*. **If you
want a reason to stop, this table is it, and I am not going to soften it.**

## B4 — but the 9 were selected on a criterion the project's own review rejects

`TASK_113`, landed and reviewed (RECAP:1784): *"**THE REFUSAL SET IS BIASED** …
All eight candidates were chosen for **bug-class novelty** — the criterion this
file's own admission bar says *predicts neither way*. **Zero were `index >= len`**,
and **`p23`, the fifteenth `index >= len`, shipped finding 38.**"*

The bar that survived review (finding 37 limb 2, `✅ NOT ATTACKED, STANDS`) is:
*a row is admissible whenever it brings a **new mechanism** — a new operator on
the safety line, a new source of the bound, or a new reason the check is or is not
elided.*

⚠ **No search for new rows has ever been run under that bar.** The one row
admitted under it — `p23`, chosen *because* it was the tree's fifteenth
`index >= len`, i.e. the exact opposite of bug-class novelty — shipped as the 25th
pattern and produced finding 38. The one row admitted on **bug-class absence**
(`p42`, on finding 37's own recommendation) shipped and then had **two headlines
retracted, with its question still open** (finding 39, *"the most-corrected result
in the project"*). **The two admissions are a small sample, but they point the
same way `TASK_113` does: the reviewed bar predicts and bug-class novelty does
not.**

## B5 — the argument the manager asked for was never delivered, and the corpus for it is already in the repo

RECAP:1853, finding 37: *"**AND THE 'FIFTEENTH `index >= len`' BAR WAS ON THE
WRONG QUANTITY** — the manager suspected this and **asked for it to be argued from
the CVE distribution rather than from taste.**"* **That request has never been
answered.**

`CLAUDE.md` names the corpus for it: `../LearnVeri/microbench/` — *"20 CVE ports
with security proofs; reusable kernels."* It contains **18 CVE directories + 2
issue directories, all with completed Verus proofs**, classified by that repo's
own tracker as **spatial 5 / logical 7 / temporal 8**.

**sec-ladder has cited it exactly twice in its whole history**, and never as a row
source:

```
$ grep -rn 'microbench' .memory/ RECAP.md .tasks/*.md
.memory/04-verus.md:5:   ... has 20 worked CVE proofs to lift          # proof idioms
.tasks/TASK_011.md:13:   ../LearnVeri/microbench/CVE-2017-7529/ ...    # became p17
```

I am a reviewer and will not propose rows, so here is only the census, done
against the built tree:

- **temporal (8)** — all eight are fixed by a generational index, which is `p27`'s
  shipped shape. This family maps onto `p27`/`p28`/`p29`/`p32`/`p33`/`p34`, which
  the project has already worked to exhaustion. **Expect nothing here.**
- **logical (7)** — decision-correctness bugs (an overloaded `ret`, a counter that
  drifts, a policy loop starting at index 1). **These would almost certainly die on
  probe 1**: there is no boundary between C, safe-naive, safe-tuned and unsafe,
  which is `p31`'s and `p33`'s death exactly. **Expect nothing here either, and
  that is a real prediction someone can cheaply falsify.**
- **spatial (5)** — `CVE-2017-7529` is already `p17`; `CVE-2014-0160` is `p20`;
  `CVE-2014-3508` and `CVE-2017-8872` look like `p14`/`p16`/`p13` shapes.
  ⚠ **`CVE-2021-23017` does not**: a *sizing* pass under-counts a separator that
  the *writing* pass emits, so the bound comes from **an earlier pass over the same
  input** and the two passes disagree. Against the built tree's sources of the
  bound — attacker length field (`p02`, `p16`), byte-value count (`p14`), buffer
  extent (`p01`), carry width (`p46`), two moving cursors (`p23`) — **"a bound
  computed by a previous pass" is not present.** Under the reviewed bar that is
  *a new source of the bound*, which is limb 2 of the bar verbatim.

**That is one candidate from a five-minute census of one corpus the project
already owns, and I am not claiming it would survive probing.** I am claiming the
enumeration has never been done.

## B6 — §B verdict

**Finding 40 supports "go find new rows", weakly but genuinely, and does not
support "stop".** Precisely:

1. **It is honest about its own scope** and should be published with that scope
   intact. Whoever cites it for "stop" is citing it wrongly.
2. **"The domain is worked out" has never been argued.** The one enumeration ever
   run (9 proposals) used the criterion `TASK_113` rejected, and the manager's own
   request for a distribution-based argument is outstanding.
3. ⚠ **The strongest thing I can say against reopening is not in finding 40 at
   all** — it is in my §A classification: **7 of 22 rows die because the FIVE-RUNG
   LADDER cannot separate them** (one-rung kills, flat/zero cost, `Ir`-invisible),
   plus two more as a secondary reason. **That is an instrument property and it
   will keep killing new rows too.** A 27th pattern is a bet on the instrument, not
   on the catalogue — **and that is the "different reason" RECAP:1798 says nobody
   has supplied. It points at "stop" for a completely different reason than
   duplication, and it is measurable rather than a matter of taste.**

**Recommendation to the manager (not a fix — a scoping):** if the project stops,
stop on **(3)**, which is measured, and not on finding 40, which disclaims it. If
the project continues, the cheapest next move is the enumeration nobody has run:
20 worked CVEs against the reviewed three-limb bar, with probe 1 applied first.

---

# §A — "the remaining rows" is 6 of 22, and "duplication" is four different relations

Generator: `.temp/r120/classify22.py`. It pins a **verbatim quote** from each of
the 22 status cells and `assert`s the quote is still present, so the
classification cannot drift away from the catalogue silently. ⚠ **The assert
fired on the first run** (`p31`'s trigger was in the row's *bug* column, not its
*status* column); the wrong trigger is kept in the file as the control.

## A1 — the classification, by each cell's own stated kill

```
trigger check: 22/22 verbatim quotes still present in .memory/06-catalogue.md

PRIMARY stated reason, all 22 rows:
  DUP       6  p21 p26 p28 p37 p39 p43     row re-derives a BUILT pattern
  NOVELTY   5  p15 p29 p30 p31 p48         the row's OWN distinguishing claim was measured FALSE
  COST      4  p20 p24 p40 p41             cost axis flat / zero / false / below the instrument
  LADDER    3  p33 p44 p45                 rungs do not separate (probe 1 / one rung)
  NONE      1  p25                         never probed
  ADMIN     1  p32                         merged into p33
  PIN       1  p34                         headline needs an arbitrary spelling pinned
  GATE      1  p35                         gate/toolchain rule blocks it

duplication as PRIMARY reason : 6/22 = 27%
duplication mentioned at all  : 11/22 = 50%
ladder-or-cost as PRIMARY     : 7/22   p20 p24 p33 p40 p41 p44 p45
```

**`major` — "The remaining rows fail because they RE-DERIVE A MECHANISM" is true
of 27% of them.** The honest sentence is *"the largest single family of stated
reasons, at about a quarter, is duplication"* — which is a list, not a law. The
manager's own "least sure #2" guessed this and is right.

⚠ **And a better headline is available from the same data.** `LADDER` + `COST`
is **7 of 22 as a primary reason**, plus `p31` and `p35` as a secondary and
`p39`/`p43` carrying a zero/flat cost alongside their duplication. **The most
common thing wrong with a remaining row is that the five-rung ladder has nothing
to price on it** — which is a statement about this benchmark, not about C. It is
also the only reason-family that would predict anything about a *future* row.

## A2 — `major`: the seven's membership is wrong in three places

```
finding 40's seven            : p20 p21 p26 p37 p39 p41 p43
  agrees with DUP-primary     : p21 p26 p37 p39 p43
  in the seven, NOT DUP-primary: p20 p41
  DUP-primary, NOT in the seven: p28
```

- **`p20` is not a duplication refusal.** Its cell's kill is the measurement —
  *"a length/offset check is O(1) and does not scale"*. The duplication clause was
  **appended at `TASK_115`** and is explicitly *"the deferral holds **a
  fortiori**"* — i.e. a reinforcing reason, added by an agent who already knew the
  built tree. **This is §A.3's selection effect, caught in the act, with the
  timestamp in the cell.**
- **`p41` is a two-kill row and its cell says so**: *"the row dies on probe 3
  **and** on duplication"*. Probe 3 came first and is sufficient — the apparent
  `9.6×` was 100% R3 spelling.
- **`p28` is missing.** Its cell says, in as many words, *"it is still p27's
  **mechanism**, which is why the row is refused"*. Finding 40 files `p28` under
  "the allocator/recycling family" instead, which is a *location*, not a reason.

## A3 — `major`: "duplication" is at least four different relations

| row | relation to the built row | is it "re-derives a mechanism one of the built 26 already carries"? |
|---|---|---|
| `p21` → `p14` | **same predicate** — *"NO NEW BOUND"* | yes |
| `p39` → `p09` | **strict subset** — `TASK_100`: *"p39 is a subset of p09, not a sibling"* (p09 ships both halves, p39 only the caught one) | yes, weakly |
| `p26` → `p13` | **same published conclusion**, *including p13's retraction* | no — it re-derives a **result**, not a mechanism |
| `p28` → `p27` | **same runtime detector** (the allocator catches it) | no — it shares a **detector** |
| `p37` → `p08` | **shared structural ABSENCE** — the obligation is unrepresentable at R5 | ⚠ **no, and it is backwards**: `p08` does not *carry* a mechanism here, it *lacks* one |
| `p43` → `p16` | **same kernel shape** — and the numbers contradict it (§C2) | no |

⚠ **`p37` is the sharpest case.** Its cell records a **measured cost axis**
(`21.00 / 20.00 / 18.00` `Ir`/record, tag check `+2.00`), a **firing harm** (ASan
2/2), and — verbatim — *"**Type confusion IS absent from the built tree — census
of all 26 rows, not a whitelist grep**"*. **A row with a novel bug class, a
measured cost and a live harm is being counted as evidence that "the rows have
nothing new", when what killed it was a Verus representability limit.** That is a
category error, and it is load-bearing: **it is 1 of the 7.**

## A4 — `minor`, but it is the rule `p43`'s own cell wrote: five refusals corroborate against UNBUILT rows

`p43`'s cell: *"**A refusal must be corroborated against BUILT patterns;
corroborating one unbuilt row with another is circular.**"* Applied to the other
fifteen:

- `p33` — *"which is **`p31`**'s death"*, *"the harm framing **`p48`**'s"* — both refused, neither built
- `p44` — opens with *"**`p45`**'s verdict reproduced on a second row"* — `p45` is refused
- `p45` — *"**`p31`**'s finding 2 verbatim"*
- `p40` — closes *"**`p01`**'s axis with **`p31`**'s problem"*
- `p39` — *"after **`p35`** and **`p28`**, that is a rule, not a coincidence"* — a rule whose three cited instances are three **unbuilt** rows (see §C4)

**Mitigating, and it matters:** `p33`, `p44` and `p45` each carry an independent
measurement (probe 1; 67-instruction normalised identity; md5-identical sections),
so the *evidence* is not circular even where the *citation* is. **The verdicts
stand; the reasons are written in a form the catalogue's own rule forbids.**

---

# §C — three load-bearing reasons checked against artefacts

**Chosen, and why:** `p43` and `p39` as the task suggests — both are in the seven
and both are `PROVISIONAL, UNREVIEWED`. **`p20` instead of `p26`**, because `p20`
is the row whose number `p43`'s cell struck as circular, so it is load-bearing
twice; `p26` has already been attacked twice and I verified its arithmetic
closes (§C5) rather than spending a rebuild on it.

Pipeline: `cost.py` and `probe2.rs` are **byte-identical** to `TASK_086`'s
(`diff` clean); `cost.rs` is `TASK_086`'s own file. Convention as declared:
marginal whole-program `Ir`/call, `n_iters` 100 vs 200, `N=4096`, `rustc -O -C
codegen-units=1`. Disassembly by **ELF `st_value`/`st_size`**
(`.temp/r120/symdis.py`), never by probe 2's last-`ret` rule.

## C1 — `p20`: `major`. "Six instructions" is seven, and `+10.00` is `+6.00`

```
$ python3 symdis.py cost k20_checked      # k20_checked  st_size=251  instructions=78
$ python3 symdis.py cost k20_unchecked    # k20_unchecked st_size=235  instructions=71
$ diff u.mn c.mn
0a1,7
> mov            <-- the cell does not list this one
> add   > setb   > cmp   > seta   > or   > jne
```

✅ **Probe 2 reproduces exactly**: `251 B` / `235 B`, the published sizes.

⚠ **The check is SEVEN instructions, not six.** The cell (and
`TASK_115_REPORT.md:435`, and `.temp/t86/NOTES.md:113`) lists
`add;setb;cmp;seta;or;jne` and omits the leading `mov %rcx,%rax` that computes
`off+len`. **The whole delta is those seven and nothing else** — the diff is a
clean 7-line insertion.

```
$ marginal Ir/call, n_iters 100 vs 200, N=4096
k20_checked    22066.00      (published: 22070.00)
k20_unchecked  22060.00      (published: 22060.00 — EXACT)
=> +6.00 Ir/call, not +10.00

$ kernel-EXCLUSIVE (callgrind_annotate, 100 calls)
k20_checked    2,203,600 / 100 = 22036.00
k20_unchecked  2,202,900 / 100 = 22029.00
=> +7.00 Ir/call — exactly the seven inserted instructions
```

**The corrected mechanism predicts the corrected number to the instruction, and
the published pair does not.** `0.0024 Ir`/byte becomes `0.00146`.

⚠ **`p21` moves the same way and by the same amount**: `26858.00 / 26788.00 =
+70.00`, against a published `+74.00`, with the **unchecked twin again exact**.
Two checked rungs, both exactly `−4`; both unchecked twins exact.
**Cause not established.** I ran the obvious hypothesis and killed it:
rebuilding with `--remap-path-prefix` so the embedded panic-location strings match
`TASK_086`'s build path gives **identical numbers** (`.temp/r120/pathtest.log`),
so it is not `.rodata`-driven alignment. `k41` (`23614.00` exact),
`k43` (`26664/23593/26661`, all three exact) and `k39` (`36895/36895/19496`, all
three exact) **all reproduce**, so this is narrow, not a general drift.

**Consequence:** the verdict (`O(1)`, does not scale) is unaffected and in fact
strengthened. **The reason as written is wrong in its instruction list and in its
number, and `.memory/06-catalogue.md`, `.tasks/TASK_115_REPORT.md` and
`.temp/t86/NOTES.md` all carry both errors.**

## C2 — `p43`: `blocker` for the reason, not the verdict. **"`p16` verbatim" is contradicted by `p16`'s own artefact**

The cell: *"`+3.00 Ir`/call **flat**, the hoisted check visible in `objdump`, i.e.
**`p16` verbatim**."*

`p16`'s own `NOTES.md`, first paragraph, in bold:

> R3's whole cost is **`7 + 5·nrec` when the value length is ≡ 0 (mod 4) and
> `7 + 7·nrec` otherwise** … so it is **O(records) and not O(1) per call**
> ⚠ **"O(1) per call" is what this paragraph said until TASK_016, and it was
> wrong.**

**`p43` is flat. `p16` is `O(nrec)`. They differ in ORDER, and `p16`'s NOTES
carries a bold warning against exactly the conflation `p43`'s cell performs.**
The measurement offered as *confirmation* of p16-likeness is the measurement that
distinguishes them.

What the `+3.00` actually is, from the ELF-extent disassembly:

```
k43_naive (44 insns, 149 B)          k43_unchecked (36 insns, 119 B)
  0 test %rdx,%rdx                     0 test %rdx,%rdx
  1 je   <ret0>                        1 je   <ret0>
  2 lea  -0x1(%rdx),%rax   <-- +1      2 cmp  $0x1,%rdx
  3 cmp  %rax,%rsi         <-- +1      ...
  4 jbe  <panic>           <-- +1
```

**Three instructions — `lea; cmp; jbe` — executed once per call, hoisted out of
the loop. That is a whole-slice length check with `O(1)` cost.** It is `p20`'s
phenomenon (a hoisted length/offset test, `+7` static, `+6.00` measured), not
`p16`'s per-record one.

⚠⚠ **The citation that `TASK_100` STRUCK is the one that matched.** `p43`'s cell
struck *"`p16`/`p20` verbatim"* down to `p16` because `p20` is unbuilt — and `p20`
is the row whose measurement `p43`'s actually resembles. **The surviving
corroboration is the mismatched one; the accurate one is unavailable under the
built-rows-only rule.** This is `p28`'s shape precisely: right verdict, wrong
reason, and the reason is what the next row gets judged against.

✅ Clean negative: all three `p43` marginals reproduce exactly
(`26664.00 / 23593.00 / 26661.00`), and `26661 − 23593 = 3068 = 0.749 Ir`/byte at
`n=4096`, confirming the tuned-beats-unsafe figure.

## C3 — `p39`: the duplication claim SURVIVES, including in a spelling nobody had measured

✅ **All three published `k39_id_*` marginals reproduce exactly.**

⚠ **The probe has a second, never-measured family.** `.temp/r100/b/cost.rs` also
defines `k39_unpack_masked` / `k39_unpack_offbyone` / `k39_unpack_nomask` — the
**actual wire-format bitfield unpack**, which is what the catalogue row is about —
and no cost log in the repo contains them. The `k39_id_*` family that *was*
measured is, by its own source comment, deliberately reshaped so the bad mask
**indexes a 512-entry op table** — i.e. reshaped into `p09`'s spelling before
being refused for resembling `p09`. **That is the selection effect operating
inside the probe.** So I measured the family nobody had:

```
k39_unpack_masked     94255.00
k39_unpack_offbyone   94255.00   <-- the bug still costs 0.00 Ir
k39_unpack_nomask     81950.00
```

✅ **The refusal's core claim holds in the spelling it was never tested in**: the
bug is worth **`0.00 Ir`** in the wire-format unpack too. **`p39`'s duplication
verdict stands and is now better evidenced than when it was written.**

⚠ `minor` — but the number quoted is not the project's cost axis. `0.00 Ir` is the
cost of the **bug**; the row's **safety** axis is `36895 − 19496 = +4.25 Ir`/element
(id family) and `94255 − 81950 = +3.00 Ir`/element (unpack family), both `O(n)`
and both larger than several published taxes. A cell whose headline number is
`0.00 Ir` reads as *"nothing to measure"*, which is the exact reading finding 40's
own sentence tries to rule out.

## C4 — `p39`, second defect: `minor`, but it is citation rot of the class PROTOCOL rule 13 names

The cell: *"a third instance of a real rule (**`.memory/03-measurement.md`**): of
the `4.25` check tax, `2.00` is the `cmp/jbe` and `≈2.25` is the unroll the panic
exit edge forecloses — **after `p35` and `p28`, that is a rule, not a
coincidence**."*

Both halves are wrong:

1. **Wrong file.** `grep '4\.25\|forecloses' .memory/03-measurement.md` → nothing.
   The rule lives in **`.memory/01-ladder.md`** (`:847`, `:1148`, `:1434`, `:2018`).
2. **Wrong count, and it undercounts by ignoring the built tree.**
   `.memory/01-ladder.md:1434` (from `TASK_033`/`TASK_048`, long before `p39` was
   adjudicated) already reads *"`4.25000 = 2.00 + 2.25` is now reproduced on a
   **THIRD kernel** with the split intact (**p16, p17, p11**)"*, and `:2018` adds
   *"on a **fourth kernel**"* (`p14`). **All four are BUILT patterns.** `p39` is at
   best the seventh instance, and calling itself the third *"after `p35` and
   `p28`"* counts only unbuilt rows — §A4's circularity again, in the one clause
   the cell offers as the row's positive contribution.

## C5 — `p26`: arithmetic closes, but two supporting claims do not survive its own sweep

The instruction accounting is internally consistent and I confirm it from the
published figures: `8387 + 1173 = 9560`; `9560 / 3200 = 2.9875 ≈ 2.99`;
`8.75 − 5.75 = 3.00`; the null control's `+8339` is **99.4%** of the `8387` it
nullifies. **`p26`'s refusal is well evidenced.**

Against its own artefact (`.temp/t115/sweep_runlen.json`, 254 run lengths):

- ✅ *"four sign changes (r=4,33,59,65)"* — **exact**.
- ⚠ `minor` — *"`ship_safe` dropping **exactly `−2804.00 Ir`** at **every**
  `r ≡ 1 (mod 32)`"*: the measured steps are
  `r=33: −2564.11`, `r=65: −2803.29`, `r=97: −2804.00`, `r=129: −2804.00`,
  `r=161: −2804.00`, `r=193: −2803.70`, `r=225: −2804.30`. **Three of seven are
  `−2804.00`; the r=33 step is 240 Ir off.** "Exactly" and "every" are both wrong;
  the phenomenon is right.
- ⚠ `major` — *"**The sign is a property of `r mod 32`, not a threshold**"* and
  *"there is no input band to design"*. The sweep says `S−U < 0` for
  `r ∈ {1,2,3} ∪ [33,58] ∪ [65,254]` — **the last sign change is at `r=65` and
  there is none after it, across 190 consecutive run lengths.** That *is* a
  threshold, and `[65,254]` *is* a designable band in which the published
  inversion holds without exception. The verdict is unaffected (the inversion is
  `p13`'s finding either way), but the sentence that says a designer could not
  have picked a band is refuted by the row's own data.

---

# §D — clean negatives and the census

## D1 — ✅ the census confirms, and its control fires

```
$ python3 .temp/mgr115/census.py
 48 catalogue rows
 26 BUILT           (on disk)
 22 adjudicated, not built   p15 p20 p21 p24 p25 p26 p28 p29 p30 p31 p32 p33 p34
                             p35 p37 p39 p40 p41 p43 p44 p45 p48
  0 bare `planned`
    26 + 22 + 0 = 48
    orphans: 0 both ways

$ python3 .temp/mgr115/census.py --naive
naive keyword classifier: 12 BUILT   (true: 26)
control fires: the keyword classifier and the disk disagree, as it must
```

**`48 = 26 + 22`, zero unadjudicated rows. Confirmed.**

⚠ **But `26 + 17 + 3 + 2` is NOT the census's output**, and `census.py:56` says so
in its own closing lines: *"'adjudicated' is NOT 'refused' … **Do not publish
`len(adjudicated)` as a REFUSED count.**"* The 17/3/2 split is a hand
classification. **I verified it separately, against the cells' own verbs**
(`classify22.py`):

```
cells whose own verb is DEFER: 3 ['p20', 'p21', 'p25']
cells the finding calls OTHER : 2 ['p24', 'p35']
remainder (REFUSE/REFUSED)   : 17
=> 26 BUILT + 17 + 3 + 2 = 48   CONFIRMED against the cells' own verbs
```

⚠ `minor` — the catalogue says *"`p32` **AND** `p33` **ARE ONE ROW**"*, so **the
17 refusals are 16 distinct adjudications**. And `p35`'s cell says both
`BLOCKED` *and* *"the row stays **REFUSED** on the merits"*, so its placement in
`OTHER` rather than `REFUSED` is a choice, not a reading.

## D2 — `p40`: the `21 Ir` is CONFIRMED twice; the other three figures are not

Re-run with `TASK_086`'s own `p40_cache.sh` parameters (`N=1048576`, 3 iterations,
`callgrind --cache-sim=yes`), plus a **zero-iteration control** the original did
not have.

| kernel | 0 iters (setup+print only) | 3 iters | marginal, 3 calls |
|---|---|---|---|
| `k40_aos` | 374,658,547 | 378,984,676 | **4,326,129** |
| `k40_soa` | 374,658,547 | 378,984,697 | **4,326,150** |
| `k40_soa_idx` | 374,658,601 | 378,984,844 | 4,326,243 |
| `k40_soa_unchecked` | 374,658,486 | 378,984,615 | 4,326,129 |

**✅ `21 Ir` — CONFIRMED, and by two independent routes**: whole-program at 3
iterations (`378,984,697 − 378,984,676 = 21`) and marginal after subtracting the
zero-iteration control (`4,326,150 − 4,326,129 = 21`). **The zero-iteration
control makes `k40_aos` and `k40_soa` byte-for-byte equal (`374,658,547` both), so
all 21 belong to the kernel.** That is 7 `Ir` per 1,048,576-element traversal.

**⚠ `major` — the denominator is 98.86% program setup.** The kernel's own marginal
cost is **1,442,043 `Ir`/call**, not 360 M. The published `5.8e-8` should be
`21 / 4,326,129 = 4.9e-6` — **84× larger.** *(The conclusion — invisible in `Ir` —
is untouched; the exponent is not, and `5.8e-8` is the figure a reader quotes.)*

**⚠ `major` — the `+193 Ir` safety-axis figure is 60% instrument artefact.** The
zero-iteration control shows `k40_soa_idx` and `k40_soa_unchecked` differ by
**115 `Ir` with the kernels never called**, because `println!("{which} …")` formats
a kernel name 6 characters longer. The real marginal is **114 `Ir` over 3 calls =
38 `Ir`/call**; today's whole-program spelling gives `+229`. **`6.4e-5 Ir`/element
should be `3.6e-5`.** `k40_aos`/`k40_soa` are immune to this only because their
names happen to be the same length.

**⚠ `major` — `LLd read misses differ 4.20×` DOES NOT REPRODUCE.**

| | published | re-run | |
|---|---|---|---|
| `k40_aos` LLd rd | 1,912,884 | 2,092,499 | |
| `k40_soa` LLd rd | 454,953 | 568,304 | |
| **ratio** | **4.2046×** | **3.6820×** | ✗ |
| `k40_aos` D1 − `k40_soa` D1 | 1,179,645 | **1,179,645** | ✓ exact |

**The D1 miss delta reproduces to the miss, so the kernels are identical; the LLd
figures moved with the environment** — and note both are *whole-program* miss
counts dominated by the 67 MB + 16 MB setup allocations, so neither `4.20×` nor
`3.68×` is a property of the kernel. **Absolute `Ir` totals also moved
(`360,114,293` → `378,984,676`), so something in the box changed since
`TASK_086`; `rustc` is still the pinned `1.97.1 / LLVM 22.1.6`, `valgrind` is
`3.27.1`.** I could not attribute it and am not claiming the number was wrong when
written — **only that it does not reproduce and should not be quoted as `4.20×`.**

⚠ **Instrument note, general:** whole-program `Ir` totals moved by **60** between
`--cache-sim=yes` and plain `callgrind` on the same binary and argv. **Marginal
(differenced) numbers did not move at all.** Any published figure below ~100 `Ir`
taken from a whole-program total rather than a difference is at the noise floor —
that covers `p40`'s `21`, `p40`'s `193`, and `p43`'s `+3.00`.

## D3 — named attacks that did NOT land. Do not re-run these.

1. **"`p39`'s `0.00 Ir` is an artefact of the `k39_id_*` spelling."** ✗ Refuted —
   the never-measured `k39_unpack_*` family gives `94255.00 ≡ 94255.00`, the same
   zero, in the wire-format spelling.
2. **"The `−4 Ir` on `k20_checked`/`k21_checked` is `.rodata` alignment from a
   different build path."** ✗ Refuted — `--remap-path-prefix` to `TASK_086`'s path
   gives identical numbers (`.temp/r120/pathtest.log`).
3. **"`p26`'s instruction accounting does not close."** ✗ It closes:
   `8387 + 1173 = 9560`, `9560/3200 = 2.9875 ≈ 2.99`, `8.75 − 5.75 = 3.00`.
4. **"`p26`'s four sign changes are mis-stated."** ✗ `r = 4, 33, 59, 65`, exact.
5. **"`p20`'s probe-2 sizes are wrong."** ✗ `251 B` / `235 B`, exact.
6. **"`p43`/`p44`/`p39` were refused on the broken form of probe 2."** ✗ Already
   settled at `TASK_100`; my ELF-extent disassembly agrees with all of them.
7. **"`p41`'s numbers do not reproduce."** ✗ `k41_checked 23614.00` exact
   (`tuned`/`unchecked` within 3 `Ir` on a ~2400 `Ir` base).

---

## Severity summary

| # | sev | where | what |
|---|---|---|---|
| 1 | **blocker** *(reason, not verdict)* | `06-catalogue.md` `p43` | *"`p16` verbatim"* contradicted by `p16`'s own `NOTES.md` (`7+5·nrec`, `O(nrec)`) against `p43`'s `+3.00` flat; the `+3.00` is `lea;cmp;jbe`, a hoisted `O(1)` check — `p20`'s phenomenon, and `p20` is the citation that was struck |
| 2 | **major** | RECAP finding 40 | *"the remaining rows"* is **6 of 22 (27%)**; the finding should be a list, not a law |
| 3 | **major** | RECAP finding 40 | the seven's membership is wrong three ways — `p20` and `p41` are not duplication-primary, `p28` is and is absent |
| 4 | **major** | RECAP finding 40 | *"duplication"* names ≥4 relations; `p37` (novel bug class, measured cost, live harm) is filed as duplication of an **absence** |
| 5 | **major** | `06-catalogue.md` `p40`, `TASK_115_REPORT` §C | `5.8e-8` denominator is 98.86% setup (→`4.9e-6`); `+193 Ir` is 115 `Ir` of `println!` artefact (→`+114`/3 calls); `4.20×` re-runs at `3.68×` |
| 6 | **major** | `06-catalogue.md` `p20` + `TASK_115_REPORT:435` + `.temp/t86/NOTES.md:113` | the check is **7** instructions, not six; `+10.00` re-measures `+6.00` (whole-program) / `+7.00` (kernel-exclusive, = the 7 instructions). `p21` moves `+74.00`→`+70.00` |
| 7 | **major** | `06-catalogue.md` `p26` | *"the sign is … not a threshold"* — the sweep has no sign change above `r=65` across 190 run lengths, so a band exists |
| 8 | **minor** | `06-catalogue.md` `p39` | the `4.25 = 2.00 + 2.25` rule is cited to the **wrong `.memory/` file** and called *"a third instance"* when four earlier instances exist on **built** patterns |
| 9 | **minor** | `06-catalogue.md` ×5 | `p33`, `p44`, `p45`, `p40`, `p39` corroborate refusals against **unbuilt** rows — the circularity `p43`'s own cell forbids (evidence is independent in each case; the wording is not) |
| 10 | **minor** | `06-catalogue.md` `p26` | *"exactly `−2804.00` at every `r ≡ 1 (mod 32)`"* — 3 of 7 steps are `−2804.00`; `r=33` is `−2564.11` |
| 11 | **minor** | RECAP finding 40 / `census.py` | `17 + 3 + 2` is a hand split the census does not produce and warns against; `p32`+`p33` are one adjudication, so the 17 are 16 |

## Answering the manager's three "least sure" calls

1. **"Is finding 40 any better than finding 37?"** — **Yes, but not for the reason
   given.** The census is genuinely better evidence than an inference. But the
   *generalisation* is the same move at the same strength, and it is wrong by the
   same mechanism: a reason that is always *available* got read as the reason that
   was *operative*. ⚠ **My recommendation: keep the census, keep the `p40`
   instrument sentence (with §D2's corrections), and replace the generalisation
   with the classification in §A1 — which is a list, is machine-checkable, and
   yields a stronger claim than duplication does.**
2. **"Does §A's count matter?"** — **Yes, but the manager's own guess is the right
   one.** *"The rows fail for many different good reasons"* is exactly what the
   cells say, and it still closes the catalogue. What is not available is a law.
3. **"Does the catalogue being spent mean the project should stop?"** — **No, and
   finding 40 says so itself.** See §B. **The measured reason to stop, if there is
   one, is §B6(3): 7 of 22 rows die because the five-rung ladder cannot separate
   them, and that will keep happening. That is a claim about the instrument, it is
   measurable, and nobody has written it down.**

## What I did NOT do

- Did not run `harness/check.py`, `build.py` or `measure.py` (not even
  `--check-stale`); did not read anything from `results/` or
  `patterns/p42-goto-cleanup/`, both of which `TASK_118` is rewriting.
- Did not publish any wall-clock comparison. `p40`'s *"best-of-7 spreads
  2.8%–32.7%"* is therefore **unverified by me**.
- Did not re-run the `p26` Verus or harm work, the `p37` Verus probe
  (`2 verified, 1 errors`), the `p20` leak/ASan matrix, or `p24`'s R5.
- Did not attribute the `−4 Ir` on `k20_checked`/`k21_checked` or the 18.9 M `Ir`
  shift in `p40`'s totals. **Both are open**, and the second one means the box has
  changed under `TASK_086`'s figures in some way nobody has characterised.
- Did not verify `p37`'s *"type confusion absent from the built tree"* census, nor
  `p28`/`p29`/`p30`/`p34`'s allocator measurements. §A classifies them by their
  **stated** reason; it does not re-adjudicate them.
- §B5's CVE census is a **read of one tracker file**, not a probe. No candidate
  from it has been tested against probe 1, and I expect the logical family to fail
  it.

---

⚠ **PROTOCOL rule 2.** Launched from **466**. This branch adds **22**; carried
forward as **488**. ⚠ **Reconciliation across concurrent branches is the
manager's job, not mine** — `TASK_118` and `TASK_119` were launched from the same
figure and their deltas must not be added to this one.
