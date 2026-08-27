# TASK_111 — review of `results/SYNTHESIS.md`: report

**Role: research reviewer. Nothing was edited.** No `git add`/`git commit`, no
`check.py`, no `build.py`, no `measure.py` except `--check-stale`. Scratch in
`.temp/r111/` only.

**Verdict.** The document's *arithmetic* is in very good shape — I checked every
figure in it against `results/synthesis.md`, `results/*.json`, `results/gate/`
and `.memory/`, and the overwhelming majority reproduce exactly, several to five
decimals. **No `‡ WITHDRAWN` cell reaches it.** The defects are not in the
numbers; they are in **what was left out, and every significant omission runs in
the same direction.** §C.1 is where the manager thought the real defect was, and
it is.

---

## Did

- Read `results/SYNTHESIS.md` (636 lines) and `results/synthesis.md` (664) in
  full; `.tasks/TASK_108_REPORT.md`; `RECAP.md` findings 1–39 and the 19-item
  retraction list; `.memory/` 00/01/03/04/06 by targeted section.
- Re-ran the writer's own `.temp/t108/census.py` (its arm that must fire: the
  9/4/9 membership lists must reproduce from the committed table — they do).
- Wrote and ran **`.temp/r111/whole_mode_symbols.py`**, two-armed. **Arm B
  fired** (M3 below).
- `timeout 300 python3 harness/measure.py --check-stale` → `52 record(s)
  examined, 0 STALE`, `EXIT=0`. The document's claim is correct.
- Notes: `.temp/r111/NOTES.md`. No artefacts to sweep — both files under
  `.temp/r111/` are a generator and evidence.

---

## Blockers

### B1. The project's strongest pro-safety result is not in the document at all

**RECAP finding 4 — *"The security result (p02), the strongest thing here"* —
appears nowhere in `results/SYNTHESIS.md`.**

> On a one-byte overflow, idiomatic C prints a plausible answer and exits 0 in
> **seven of eight builds** — silent heap corruption absorbed by glibc's chunk
> rounding. The eighth aborts only because Ubuntu defaults `_FORTIFY_SOURCE 3`.
> Every Rust and hardened-C cell handles it. Control: delete the check from safe
> Rust and it **panics rather than corrupting**, so *"Rust makes the check
> non-optional"* is a measurement. (`RECAP.md:280-287`)

Measured absence:

```
$ grep -n '\bp02\b' results/SYNTHESIS.md
101:  9 of 22 ... p01, p02, p04,          <- a cost bucket
140:  p01 / p02, the calibration pair     <- a cost paragraph
141:  ... +10 on p02 against unsafe        <- a cost figure
$ grep -in 'fortify|heap corrupt|silent|one-byte|seven of eight' results/SYNTHESIS.md
   (only `_FORTIFY_SOURCE=3` as a toolchain fact in §1, and "seven of eight
    multiples of four" in §6 trap 2 — an unrelated sentence)
```

Every mention of p02 in the document is about cost. The one measurement in this
project where **safe Rust catches a real memory-safety bug that C silently
absorbs**, with a positive control, is gone.

**Why this is a blocker rather than an omission.** §3 (*Result 2 — where safe
Rust does not help*) runs 80 lines and eight sub-results. Its counterweight is
**two sentences** at the end (p08's inexpressible bug, p38's non-reintroduced
class) — both of which are, in the document's own words, *"invisible in any `Ir`
column"*. So the reader is given: eight measured places where safety buys
nothing, two places where it buys something unmeasurable, and **zero places
where it demonstrably buys everything.** That is not what the record says. A
finding silently dropped is indistinguishable from a finding retracted, and this
one is not retracted — it is `RECAP.md`'s finding **4**, unstruck, and RECAP
calls it *the strongest thing here*.

**Fix:** one paragraph in §3, as the opening of the "other side of the ledger"
pair, quoting the seven-of-eight figure and the delete-the-check control.

### B2. Finding 14 is absent, and §1's ladder table asserts its opposite

`RECAP.md` finding **14** — *"Every rung is a spelling, the gap does not
converge, and 'safe beats unsafe' was never available as a language fact"* — is
called **"the programme's central methodological result, and the one that shapes
the writeup."** Its load-bearing half:

> **All six patterns pin `identity: unsafe ≡ verus, O3 exact`**, so an R4 is not
> a program that *may* use `unsafe` — it is a program that **must have a
> byte-identical R5 twin that Verus verifies**. R4 is bounded by what vstd can
> express; R3 is bounded by nothing. The classes are **incomparable, not
> nested.** (`RECAP.md:444-451`)

`results/SYNTHESIS.md` §1 defines R4 as:

> | **R4** | unsafe Rust | `get_unchecked`, raw pointers — whatever reaches C's
> codegen. **Correct, just unverified** |

That is affirmatively wrong at this pin: `results/synthesis.md` §3 shows
`identity: exact` on **25 of 26** patterns and `norel` on the 26th, so R4 is
constrained to spellings Verus can verify. *"Correct, just unverified"* says the
only thing missing is a proof. `grep -i 'chained\|incomparable\|prover'` over the
document returns three hits, none of them this.

**Why it is a blocker, not a definitional nit.** The constraint runs in the
**flattering direction for every `R3 − R4` in the document**: it holds R4 above
its true floor, so safe Rust looks relatively better everywhere. The measured
instance is p11 — `r4_cstr` would be **−17 526 `Ir`/call (−35%)** and is rejected
with four `is not supported` errors, and `.memory/01-ladder.md` calls p11 *"the
largest instance of finding 14's R4-chained-to-the-prover result."* The document
quotes p11's decomposition and drops the headline. On p16 the same mechanism is
measured the other way: `chunks_exact(32)` is admissible as R3 at **zero TCB**
and needs **five** trusted items as R4.

§2's closing caveat covers *search depth* (*"two rungs searched to wildly
different depths"*) — a different and weaker thing. Search depth says nobody
looked hard enough. Finding 14 says **one side is not allowed to look**. Under
§C.3's rule (*"if a claim is only correct to a reader who already knows the
caveat, it is wrong in this document"*), every `R3 − R4` in the document is
currently mis-stated to an outside reader.

**Fix:** two sentences in §1's R4 row and one in §2's caveat. Cheap, and it is
the caveat a hostile reader would find first.

---

## Majors

### M1. §2's p09 row attaches a "half" to the wrong quantity — and it runs toward the document's own thesis

```
| p09 bitset | 13 756 / 48 885 | **half is a lost 8-byte load-merge idiom**,
                                 not deleted checks |
```

No artefact states that. The two "half" statements in the record are about
**different quantities**:

- `patterns/p09-bitset/NOTES.md:982` — *"**HALF OF THAT WIN** IS A RESTORED LOAD
  IDIOM, NOT A DELETED CHECK"* — "that win" is **`m_clampb`'s** win, the p03-style
  seeding control, *"49% of the marginal on `small`, 47% on `large`"*. Not
  `R3 − R4`.
- `patterns/p09-bitset/NOTES.md:355` — `+21 lost merge / +1 spill / −5 cheaper
  query checks = +17 net` — that is the decomposition of the **R3-vs-R2
  inversion** (82 vs 65 instructions in the guarded body). Not `R3 − R4`.

And the authoritative layer says the opposite about `R3 − R4` specifically:

> **The three checks decompose with ZERO free parameters** … with `R3 − R4`
> predicted **48885.00** against measured **48885.00**.
> (`.memory/01-ladder.md:1572-1578`)

So the record attributes p09's `R3 − R4` to a zero-parameter decomposition over
**three checks**, and the document attributes **half of it away from checks**.
p09 is the **largest `R3 − R4` in the tree**, and the row sits in the table the
writer says is what makes Result 1 believable. The error direction is *"the check
is rarely the biggest term"* — the section's own headline.

### M2. Two figures on the "Retracted — do not reinstate" list are used at their retracted values

- **p22.** `RECAP.md:2053+` and finding 33: *"published `+2.00` against
  `+125/+1021` — **510×** on the large band"* — the widest retraction in the
  project. §2 lists p22 in **"9 of 22 sit within ±32 `Ir` per call on both blobs
  … Flat in the size of the data"**, using `+2.00`. The **same document** reports
  the retraction 400 lines later in §6 trap 1. The two passages cannot both be
  right, and §2 never cross-references §6. Applying the record, p22 leaves the
  "flat" bucket for the ">100" bucket and the headline distribution becomes
  **8 / 4 / 10**, not 9 / 4 / 9.
- **p17.** `RECAP.md:2109`, on the do-not-reinstate list: *"**"p17's R3 costs +32
  Ir/call, flat"** — flat *per byte*, not per call. Both published bands happen to
  have `nsuf = 3`; swept, `R3ship − R4` runs **18…63**."* §2 puts p17 in the same
  "flat" bucket at `32 / 32`. Narrowly, "flat across p17's two blobs" is true;
  the retracted claim is that it is flat as a **law**, which is what a reader
  quoting the bucket will take away. `.memory/01-ladder.md:1015-1022` adds that an
  in-contract R3 respelling measures **−19.00 flat** against the shipped R4.

The generated table's search-state column prints `undeclared` for **both** p22
and p17, which is how they got in. See "Adjacent work" — that column is wrong.

### M3. "All 20 survivors are gcc partial-inlining remnants" is false, and the generated file's own listing refutes it

`results/SYNTHESIS.md:614-616` (§7, Structural gaps) and `results/synthesis.md`
limit 1 (*"all 20 that DID keep a symbol are `kernel.part.0`"*). Checked directly
against the committed records:

```
$ python3 .temp/r111/whole_mode_symbols.py
-O3 whole-mode (cell, input) pairs : 414
  kernel_exclusive_ir is None      : 394
  survivors                        : 20
ARM A: counts 414 / 394 / 20 reproduce exactly -> the probe is live.

survivor kernel_functions, by value:
  ('kernel.part.0',)  x16
  ('kernel',)  x4

ARM B FIRED: the 20 survivors carry 2 distinct symbol values, not 1.
  4 of them are the WHOLE `kernel` symbol, not a partial-inlining remnant:
    p46-bignum-mac c-gcc   small.bin ('kernel',)
    p46-bignum-mac c-gcc   large.bin ('kernel',)
    p46-bignum-mac c-gcc-h small.bin ('kernel',)
    p46-bignum-mac c-gcc-h large.bin ('kernel',)
EXIT=1
```

`results/synthesis.md:30-33` **prints those four rows as `kernel`**, four lines
above the sentence that says all twenty are `kernel.part.0`. This is
`PROTOCOL` rule 13 exactly — the summary line above the detail is not where
anyone is looking — and `SYNTHESIS.md` inherited it without re-deriving.

Consequence beyond the wording: `synthesis.md`'s *"there is **not one**
`whole`-mode row in the tree where the kernel column means what it means in
`isolated`"* is false for p46's four C rows. The isolated-only decision survives
(one pattern, gcc-only, C-only, so no rung comparison is available), but the
justification as written does not.

### M4. p27's headline pair is a whole-program marginal quoted under a kernel-exclusive banner

§1 declares: *"Every figure below is `-O3`, inline mode `isolated`,
**kernel-exclusive `Ir` per call**, unless it says otherwise."* §2 then prints
`R3 − R4 = +230.07 / +792.75` for p27. The authoritative source says:

> `R3 − R4 = +230.07 / +792.75` **(whole-program marginal, `-O3 isolated`)**
> (`.memory/01-ladder.md:2162`)

The kernel-exclusive value for the same pair is **+109.98 / +661.82**
(`results/synthesis.md` §2). The document discloses that the row is `NOT-LIC` and
that the decomposition is p27's own caller→callee work — but it never says
*"marginal"*, and a reader applying the stated convention reads a figure that is
**2.09× the kernel-exclusive one**. This is §A.2's exact question, and it is the
one place the document silently switches convention.

(The decomposition itself is exact: `230.0694 = 109.6476 + 120.4218 + 0.0000`,
`+153.51` for the check-keeping unsafe rung, `allocator = 0.00` three-for-three —
all verified.)

### M5. §7's unreviewed list omits `TASK_100`, and the writer's own notes have it

§7 lists as unreviewed: 088, 090, 091, 092, 095, 097, 102, 106, 107, 109, 110.
`.temp/t108/NOTES.md:22` — the writer's own audit — reads:

> Still unreviewed: 088, 090, 091, 092, 095, 097, **100(a review)**, 102, 106,
> 107, 109(a review), 110

`TASK_100.md` is `Role: research reviewer` and no `TASK_100_REVIEW*` exists.
§7 includes `TASK_109` on precisely the "a review, itself unreviewed" criterion
(*"the two most recent reviews and their landings"*) and then omits `TASK_100`,
which meets it. `TASK_098` (also `Role: research reviewer`, also unreviewed) is
likewise absent.

This matters substantively: `TASK_100` is the source of the p34 *"the named kill
is dead"* correction that §3's p34 paragraph rests on, **and** of the p37
refusal-reason refutation that bears on §5 (see m7).

**This is the answer to §D's "what did the writer not catch."** It caught the
manager's stale PROVISIONAL list and rebuilt it — and left a hole in the rebuilt
list that its own scratch notes had already identified.

### M6. §4's p42 result carries no PROVISIONAL marker although it rests entirely on two tasks §7 lists as unreviewed

§4's p42 paragraph is the document's most emphatic (*"refuted by its own review
within hours … the property is stated exactly"*), and §4's *"the obligation count
does not tell a reader what the proof covers"* opens on it. Both rest on
`TASK_109` (the review) and `TASK_110` (the landing), both on §7's own unreviewed
list. `RECAP.md` finding 39 marks it: *"⚠ **PROVISIONAL — `TASK_104` and
`TASK_109` both unreviewed as a pair.**"*

The document marks p46 (§2), the stack-overflow case (§4 item 2), §5 in its
entirety and p34 (§3) as PROVISIONAL in the body. p42 is the one that is not, and
it is the one carrying the sharpest claim in §4. §C.4 verbatim.

✅ **Clean negative on the caveat the task file named:** *"deleting the ledger's
leak-freedom `ensures` still gives `18 verified, 0 errors`"* **is carried**
(§4, "The obligation count does not tell a reader what the proof covers") **and
is supported** — `patterns/p42-goto-cleanup/NOTES.md:627`,
`.tasks/TASK_110_REPORT.md:319,435`. The *"encoding choice, not the prover"*
framing and the no-linear-mode clean negative are both present and exact.

### M7. The document's only new aggregate cites a gitignored path

§2: *"re-derivable with `.temp/t108/census.py`"*, repeated in the closing
Sources line.

```
$ git check-ignore -v .temp/t108/census.py
.gitignore:3:.temp/	.temp/t108/census.py
$ git ls-files --error-unmatch .temp/t108/census.py
error: pathspec ... did not match any file(s) known to git
```

`results/SYNTHESIS.md` is committed and is *"the artefact a reader outside this
repo will actually read"*. Its 9/22 · 4/22 · 9/22 distribution — which
`TASK_108_REPORT.md` itself flags as *"a **new, unreviewed aggregate**"* — is
**not re-derivable from a clone**, and `CLAUDE.md` rule 1 instructs the next
agent to delete exactly this kind of file. The project already knows this class:
`.memory/06-catalogue.md:1233` embeds p15's artefact verbatim *"because `.temp/`
is gitignored"*.

The script is 86 lines and reads one committed markdown file. It belongs under
`synthesis/`.

### M8. §1's rule for when the two `Ir` conventions disagree is narrower than the record

> *"They answer different questions and disagree **where the rungs call different
> library routines**."*

The two largest measured disagreements in the tree are neither:

- **p27** — `+120.33 / +130.95`, and the cause is *"the SAFE side's out-of-line
  `drop_glue::<[Option<Box<u8>>; 32]>`"* (`results/synthesis.md:235-242`). Rust
  drop glue, not a library routine.
- **p36** — dispatch targets run **512 (gcc) / 384 (clang, rustc) / 0** `Ir` per
  call, which **reverses** the `match` control from dearer to cheaper and
  vanishes the gcc-vs-clang C gap (`RECAP.md` finding 34). The kernel's own
  indirect callees.

A reader given §1's rule would conclude that a pattern with no libc calls is safe
to difference. p36 is the counterexample, and it is the pattern whose finding is
titled *"the kernel-exclusive column hid an entire callee."*

### M9. gcc's `endbr64` term is absent while gcc figures are quoted

`RECAP.md` finding 34: *"the `endbr64` finding is **bigger than p36**: gcc
defaults to `-fcf-protection=full`, so **this project has been pricing a CFI
mitigation all along, at `1.00000·nrw + 1` `Ir` per call, in gcc's column only,
and never said so.** Manager-verified."* `results/synthesis.md` limit 4 carries it
and adds *"**Never attribute a gcc-vs-clang gap to codegen without naming it.**"*

`results/SYNTHESIS.md` never mentions it, and it quotes gcc figures — *"Hardened
C's own check is **+5** (gcc) / **+12** (clang)"* (§2), p11's 12.0× library factor
against C `strlen` (§2), *"gcc stays as the distro baseline"* implicitly
throughout. §1 is the page that exists to stop a reader misusing those numbers,
and this is the one term in the tree that is systematically present in exactly one
of the two C columns.

---

## Minors

- **m1 — `harness/check.py` line count.** §1: *"a ~5 400-line adversarial
  checker"*. Actual: `wc -l` = **8434** (7809 non-blank, 6441 non-comment). The
  source is `RECAP.md:2258` — *"`check.py` is ~5460 lines **against 19
  patterns**"* — a 19-pattern-era figure carried into a 26-pattern document. §A.4's
  live class, and the sentence it came from names its own denominator.
- **m2 — "+10 on p02."** §2's calibration paragraph, under the kernel-exclusive
  banner. `results/synthesis.md` §2 gives p02 `R3 − R4 = 11.00 / 11.00`. The `+10`
  is `.memory/01-ladder.md:590`'s marginal at **61 B / 4092 B** — a different
  convention *and* a different input pair. Transcribed from `RECAP.md:271`'s
  prose. (p01's `+4…+5` and hardened C's `+5`/`+12` all check out
  kernel-exclusive: `207−202 = 5`, `8770−8765 = 5`, `205−193 = 12`,
  `9776−9764 = 12`.)
- **m3 — p13's `91%`.** §2 says *"72% (`small`) and **91%** (`large`)"*.
  `.memory/01-ladder.md:1782` — the layer `CLAUDE.md` calls authoritative — says
  **90%**. `RECAP.md:1038` says 91%. The two upstream files disagree and the
  document resolved toward the non-authoritative one. **The upstream disagreement
  is itself worth landing.**
- **m4 — "between 1.05× and 3 536×, median about 7.3×" mixes two populations.**
  Re-running the cited census: the `1.05×` endpoint is **p27**, a `NOT-LIC` row
  the same section excludes; the `7.3×` median is over the **17 licensed rows**
  with `R3−R4 > 0` (p05's 7.26 is the 9th of 17). Over all 20 positive rows the
  median is **17.4×**; over the licensed 17 the minimum is **−1.37×** (p47), and
  the census's own printed low is **`0.74x`** (p09) — which
  `.tasks/TASK_108_REPORT.md:55` reproduces verbatim. The document acknowledges
  p09 and p14 inverting; it does not acknowledge that its stated floor comes from
  a row its own licence rule excludes. Either state the licensed range
  (−1.37×…3 536×) or drop the range and keep the median, as the writer's own
  "Unsure" section offered.
- **m5 — 9 + 4 + 9 = 22 reads as a partition and is not one.** p18 is in two
  buckets (within ±32 *and* negative on both); **p16** (27 / 77) is in none. The
  sum landing exactly on 22 makes the coincidence load-bearing.
- **m6 — p23 quoted without its rank.** §2's table gives p23 at `306 / 444`.
  p23's own rule, which the task file names, is *"any number quoted without its
  rank is quoted without its domain"*, and its `R3 − R4` runs **227.00 → 706.37**
  (3.11×) with everything but the pivot's rank held fixed. The "what it is paying
  for" column says *"the data's shape"*, which is the right gloss, but the two
  numbers still ship rank-free.
- **m7 — "15 rows are refused, each on a measurement."** Counted: exactly 15 ✅.
  But `p37` is one of them, and `.memory/06-catalogue.md:416` reads
  *"**REFUSED-REASON-REFUTED at TASK_100 … THE ONE ROW OF THE NINE WHOSE VERDICT
  DOES NOT SURVIVE ITS REASON** … Re-triage, do not rubber-stamp."* In a section
  arguing that a **hit rate of zero** makes the refusals structural rather than
  unlucky, that is the row a skeptic asks about.
- **m8 — "The 48-row catalogue was written before the project started."**
  `CLAUDE.md` says the catalogue is **48 rows since TASK_066 added `p48`**, and
  p48 was then refused at TASK_074. One of the 48 is a mid-project addition by the
  manager. This weakens the "written in advance, so the refusals are not selection
  bias" argument by exactly one row and should be said.
- **m9 — "Safe Rust can be worse than C" as a bold lead.** The body correctly
  retracts it (*"read this as a warning about a spelling, not a claim about the
  language"*) and the catalogue agrees (`p34`: the headline *"would survive only
  if `Rc`-both-ways were pinned as THE safe spelling"*, and it is not). But the
  **bold sentence is what gets quoted**, and it is the refused headline verbatim.
  ⚠ Separately: **no C rung was ever measured for it.** The whole evidence base is
  `miri cycle → 5 memory leaked` vs `miri weak → 0` — two *Rust* spellings. The
  catalogue says *"no cost axis was ever measured"* and `.memory/01-ladder.md:2657`
  points at the C side having no detector (itself now stale — TASK_100 found one).
  A comparison to C with no C measurement should not be a bold lead in this
  document.
- **m10 — p11's 2.00-vs-3.00 mechanism is attributed across patterns.** §2: *"the
  *same* check costs one instruction more here than in **p16's fold**"*. The
  isolating control was **within p11** — its own fold at 4.25 against its own scan
  at 3.00 (`.memory/01-ladder.md:1424-1431`), a one-loop-at-a-time control. The
  general rule is stated there correctly and is not about p16.
- **m11 — "one containerised Xeon Gold 6230."** `.memory/00-environment.md:8`:
  **2×** Xeon Gold 6230, 80 logical CPUs.
- **m12 — "three of them within three tasks of each other"** (§6 trap 3) is not
  derivable from the six live entries in `.memory/03-measurement.md`. The only
  tight cluster is entries 5 (TASK_099), 6 (TASK_100) and 7 (TASK_099) — and
  entry 5 is the **RETRACTED** one, so the count includes a struck member, which
  is the failure that list exists to prevent. Cite the entries, not a count.

---

## Clean negatives — named attacks that did NOT land

Do not re-run these.

1. **Every one of the 18 figures in §2's nine-row exception table** matches
   `results/synthesis.md` §2 `R3−R4` to the digit (p07 `3014.60/10024.93` and p23
   `305.74/443.55` presented rounded, disclosed by the rounding).
2. **The 9 / 4 / 9 membership lists reproduce exactly** from the committed table.
   Recomputed independently. The *thresholds* are the writer's choice, disclosed as
   such in the report.
3. **No withdrawn cell reaches the document.** I checked all four `‡ WITHDRAWN`
   cells (p03/p04 `R5−R4`, both blobs). §4 quotes the **kernel-exclusive** zero —
   which the generated file says is the column that reproduces on p03/p04 — and
   explicitly tells the reader *not* to cite that column as the evidence, pointing
   at the raw-byte digest instead. This is handled better than I expected.
4. **p03's clamp story** — 17→13, 14→13, gap exactly zero, zero fitted parameters;
   `sp > 1000` inert; `sp > 65` leaves the check *and* is dearer; clang **and** gcc
   both at `4.00000 Ir` per executed pop and both delete 100% byte-identically;
   *"seeding, not inability"*. Every clause exact.
5. **p04** — `9/0` against five positive controls, and *"blind to every functional
   change, not just that one"* — which is the **corrected** characterisation, not
   the one p04 published. The writer took the correction.
6. **p09's `q>>5`/`q>>7`** — `19 verified, 0 errors`, `6691.70` vs `6692.30`,
   368-byte kernel differing in one byte, all five builds wrong on the headline
   blob, *"a class of at least nine"*. Exact. (The cost attribution is M1; the bug
   story is clean.)
7. **p17** `9 verified, 1 error` → `10/0` stripped; **p47** `14 verified, 0 errors`,
   kernel obligation **unchanged at 3**, `+7088.000 Ir`, contracts identical;
   **p13** 2 vs 4 `Ir`/byte, bounded-unchecked ≡ `position()` to the instruction,
   `19/0` no new trusted item, `+44.00/+77.00`; **p07** `6.0000`/probe,
   42.53%→46.63%, asymptote `[46.15%, 50.00%]`, six distributions; **p11**
   `0.078125` / `0.937500` / 12.0× / 5.3× / `3.00000`; **p46** `6241/23341`,
   `6287/23435`, `6406/24250`, `+2.00000·n·m` over five shapes. All exact.
8. **The unroll counterfactual is measured, not derived.** *"forcing LLVM to
   unroll the checked loop recovers 0.50, not 2.25"* rests on a real run
   (`-unroll-runtime-multi-exit -unroll-count=4` → **9.50**, not 7.75) at
   `.memory/01-ladder.md:853-859`. The document's strengthened restatement is
   verbatim the ladder's.
9. **"Five kernels" for `4.25 = 2.00 + 2.25` holds** — p16, p17, p05, p11, p14,
   supported by `.memory/01-ladder.md:847, 1028, 1434, 2018` + `RECAP.md` finding
   11. I attacked this expecting three and it is five.
10. **§4's trusted-base block** — 108 items / 230 lines / 0 axioms;
    `group_slice_axioms` = six `broadcast axiom fn`s; 26/26 carry `broadcast use`;
    p08's `11/0` shipped and `15/0` under the twin; the pasteable
    `assume_specification` verifying a 1 MiB OOB read at `4 verified, 0 errors`;
    *"not gameable retrospectively, gameable prospectively"* with measured exposure
    **0**; identity `exact` on 25 + `norel` on p36; p36's vtables 40 vs 32 with
    eight slot-4 entries at one 26-byte stub. All exact.
11. **§5's refusal evidence** — 15 catalogue refusals (counted), 8 later probes
    both lists at zero, ICF-merged recursion symbol, unaligned load at the same 19
    instructions, `qsort` 80 cells / 0 ASan reports, **14** patterns on the
    `index >= len` axis (`.memory/06-catalogue.md:380`, manager-verified,
    "three tracked files assert an ordinal built on that list"). All exact.
12. **§6's eight traps** — 22 gate records; `head -4` / gcc UBSan exactly four
    lines / four rows; `7, 7, 8, 8`; `+486.00 Ir`/call at an **identical
    3332-byte** block = 69×; 20 pre-registered layouts hashed before timing; 27%;
    p23's 152 `Ir`/call and the seven-of-eight multiples of four; p42's 210 / 8707
    sign reversal; p38 `+21/+25` vs `+24/+32`; p36 `+15` → `+7`; p10's 60%.
    Every figure exact. **p06's `45–108` recomputed off §1 myself:
    `2615−2570 = 45`, `1707−1599 = 108`.** ✅
13. **The allocator-recycling rule is at its true scope.** It really is reviewed
    (`TASK_093_REVIEW*` exist) and manager-re-run
    (`.memory/01-ladder.md:2581-2624`), and the document's wording — *"a rule, not
    a pattern"*, the `#![forbid(unsafe_code)]` framing, Miri-clean in all three
    modes, the generation tag not rescuing it — is faithful clause for clause. The
    task file asked me to attack this specifically. **It holds.**
14. **§D's three corrections all landed.** §7 carries the rebuilt PROVISIONAL list
    (four moved to reviewed, three added); the document says **six** controls and
    uses no ordinal for one; `grep -c 'p24' results/SYNTHESIS.md` = **0**.
15. **Apparatus facts** — Verus `0.2026.08.09.92f466f`, gcc 13.3.0, clang 22.1.6,
    rustc 1.97.1, glibc 2.39 with gcc-default `_FORTIFY_SOURCE=3`, 24 `PASS` + 2
    `PASS-WITH-BLOCKED-ROWS`, 52 records 0 stale, **4** unlicensed `R3−R4` rows,
    **19** retractions. All correct.
16. **File citations resolve.** Every `path.ext` in backticks exists, except the
    generic `spec.md` (a template reference, not a citation) and M7's gitignored
    `census.py`.

---

## The three calls you named

### 1. Is the four-result compression honest rather than convenient?

**The structure is honest. The coverage is not, and the bias has a direction.**

The 6→4 regrouping is a genuine improvement and I could not break it: merging
"safety is usually free" with "name what you are paying for" lets the sentence
that actually generalises be *stated* rather than implied twice, and putting the
trusted base behind "what a proof discharges" gives four homeless items a home.
I attacked the merge and it held.

**What the compression cut is not an awkward result. It is the pro-safety half of
the ledger, four times, in the same direction:**

| dropped | what it says | direction |
|---|---|---|
| finding **4** | C silently corrupts the heap in 7 of 8 builds; every Rust cell handles it; deleting safe Rust's check makes it **panic** rather than corrupt | for safety |
| finding **14** | R4 is chained to the prover, so every `R3 − R4` here is measured against an inflated unsafe rung | for safety |
| finding **7** | on p01 `large`, C-clang and unsafe Rust execute **exactly 143 740 000** kernel instructions — the cleanest "Rust codegen *is* C codegen" datapoint in the tree | for safety |
| finding **32**'s price half | on gcc the **undefined** spelling is the **dearest** of its six neighbours; every fix saves exactly `6.00 Ir`/call, so *"no optimising programmer arrives here"* | for safety |

Add finding **17**'s headline (the safe class reaches `core::slice::memchr` at
zero TCB; the unsafe class cannot reach it at all, worth −17 526 `Ir`/call) and
finding **8** (p02's sawtooth, *"the only model here tested by prediction"* — the
positive control §6 trap 2 never gets).

None of these is awkward. Each is a clean, reviewed, quotable win. **A length
target did not cut the uncomfortable result; it cut the flattering-to-safety
result, four to six times running.** That is the *mirror image* of the failure
this project has spent nineteen retractions learning to catch, which is exactly
why nobody was watching for it — including, on the evidence, the manager, whose
§A.3 brief asked for *"where safe Rust does not help"* and had no counterpart
item.

Also dropped and worth a line each, in falling order of loss: finding **35**'s
sign flip (p19's buggy C rung is 5071 `Ir`/call **cheaper** at `small` and 3569
**dearer** at `large`, zero at m ≈ 2509 — *"a percentage quoted at either input is
wrong in SIGN at the other"*, a decision-maker's trap the document never names);
finding **34**'s headline (*"the prover excludes the MECHANISM, not a spelling"*,
priced at `3.00000 Ir`/dispatch); finding **23** (p04's `next_pow2(CAP) ≤
ARR_LEN` — the mechanism behind one of the nine "flat" rows the document quotes
without one); finding **21** (p12, mentioned **once** in the whole document, in a
list); finding **5** (static counts are not a cost model — and the document sends
readers to a generated file whose §4 *is* a static-count table); finding **22**
(decode the panic pad's `Location`).

**Verdict: 4-plus-a-method is the right shape and the wrong contents.** The
repair is not longer; it is one paragraph in §3 (B1) and two sentences in §1
(B2), plus a line each for findings 7 and 32.

### 2. Is §3 ("where safe Rust does not help") at its true scope?

**Every claim in it is at its true scope. The section is not, and the failure is
positional rather than per-claim.**

I attacked all eight sub-results individually. p09, p04, p06, p17, p18, p22 and
p47 are faithful transcriptions of the authoritative layer, several of them
carrying the *corrected* form rather than the published one (p04's *"blind to
every functional change"*, p22's narrowed *"nothing on this ladder **emits** the
capacity check"*). p34 is honestly labelled a refused row and a spelling warning —
though its bold lead is the refused headline and no C rung was measured (m9). The
allocator-recycling rule is correctly described as reviewed and independently
re-run (clean negative 13). **I could not break a single one of these claims.**

The overclaim is in the arithmetic of the document, not of the section: eight
measured "does not help" results, two unmeasurable "does help" results, and — per
B1 — **zero** measured "does help" results, because the one that exists was
dropped. A decision-maker who reads only §3 and its two-sentence coda takes away
that safe Rust's guarantee is narrow and unpriced, and that is not what the record
says. **You pushed for this section and got a good one; what got lost is the thing
it needed to sit next to.**

### 3. Was the synthesis worth doing instead of a 27th pattern?

**Yes — and the honest breakdown is roughly one-third new, two-thirds
re-presentation, with the new third being the valuable part.**

I ran the test you asked for. Three things in this document exist nowhere else as
a unit:

- **§6.** `RECAP.md`'s retraction list is 19 bullets of *what was retracted*.
  §6 is 8 traps of *what will happen to you*, ordered by transferability, each
  ending in an instruction, with the pattern as citation rather than subject.
  That is a different artefact, and it is the one a benchmark author outside this
  repo can actually use.
- **§5's consequence sentence** — *"this project measured the bounds-check family,
  and where safe Rust's guarantee is compile-time its runtime cost is zero by
  construction and no benchmark will ever say otherwise."* I looked for that
  sentence in `RECAP.md`, `.memory/` and the catalogue. It is not there. It is the
  single most quotable line in the document.
- **§2's distribution** (9 / 4 / 9) is a new aggregate no artefact held — which is
  also why it needs M7 fixed and M2 applied.

Against that: §2's nine-row table and all of §3 are close to a re-ordering of
`RECAP.md` findings 9–39 with better prose, and §4's first two subsections are
findings 1 and 2 nearly verbatim.

So it is **not** a restatement, but it is closer to one than §6 and §5 suggest.
The decisive argument is the one you did not make: writing it caught four manager
errors, and reviewing it surfaced a **systematic direction-bias in the project's
own findings coverage** that twenty-six pattern cycles, each individually
reviewed, had not. A 27th pattern would not have produced that. **Keep the
synthesis; land B1 and B2 before anyone quotes it.**

---

## Adjacent work (reported, not done)

1. **`synthesis/synthesize.py::SEARCH_REVIEWED` is missing three reviewed search
   results**, which is the mechanism behind M2. It has 8 entries (p01 p03 p08 p10
   p11 p13 p36 p47) and prints `undeclared` for:
   - **p22** — `.memory/01-ladder.md:2401-2406`: *"`r4_reslice` is in contract,
     verifies 20/0, is byte-identical to its own R5 at O3 … the published
     `R3 − R4 = +2.00` is a **fixed-R4 bound**, and against the cheapest
     admissible R4 the gap is **+125.00 / +1021.00 — 510×**."* Reviewed.
   - **p17** — `.memory/01-ladder.md:1017-1026`: an in-contract respelling at
     **−19.00 flat**, byte-identical; swept `18…63` over `nsuf` 1–8. TASK_018,
     reviewed.
   - **p06** — `.memory/01-ladder.md:1914-1917`: shipped R3 is `2.00000 Ir`/byte;
     the in-contract zero-`unsafe` control `c_idx` is **`0.00000 Ir`/byte, 105
     flat**. TASK_047_REVIEW, reviewed.

   Consequence: `SYNTHESIS.md`'s *"18 of 26 print `undeclared` … only **five**
   report a real search"* is true **of the table** and understates **the record**
   by three, and three of §2's nine "flat" rows are quoted at spellings the record
   already knows are beatable.
2. **`RECAP.md:1038` (91%) and `.memory/01-ladder.md:1782` (90%)** disagree on
   p13's `large` consumer-scan share. One of them should move (m3).
3. **`.memory/01-ladder.md:2657`** says *"see `.memory/00-environment.md` for why
   the C side has no detector for it here"* (p34's leak). `.memory/06-catalogue.md`
   records that TASK_100 **found one** — `__lsan_default_options()`, one line, zero
   `Ir`. Stale cross-reference in the authoritative layer.
4. **`results/synthesis.md` limit 1 and §5 claim 3** carry M3's false sentence
   independently of `SYNTHESIS.md` and need the same correction.

---

## Unsure / not done

- **I did not re-measure anything.** Every check is a comparison of the document
  against `results/*.json`, `results/gate/*.json`, `results/synthesis.md`,
  `RECAP.md` and `.memory/`. Where those disagree with each other I said so (m3)
  rather than deciding by measurement.
- **I did not read `RECAP.md`'s "Owed" queue (lines 2402–3529) in full** — the
  same gap the writer disclosed. If a live caveat lives only there, I inherited
  the miss. I did read the retraction list, all 39 findings, the recurring traps
  and the Priority section.
- **I did not read `.memory/02-bench-rules.md` or `05-layout.md` in full.**
- **The §C.1 finding walk is a judgement.** I list what the document does not
  represent; whether findings 5, 21, 22, 23 *should* be represented is arguable.
  Findings **4** and **14** are not arguable — RECAP calls them *"the strongest
  thing here"* and *"the programme's central methodological result"*.
- **M2's p17 half has wiggle room** and I want to be precise about it: `+32 / +32`
  is literally correct for p17's two shipped blobs, and *"flat in the size of the
  data"* is defensible for those two points. What is retracted is `+32` as a
  **law**, which is what a reader takes from a bucket labelled "flat". The p22 half
  has no wiggle room.
- **I did not check `results/tables/*.md`** (26 files) against the document.
  `SYNTHESIS.md` does not cite them.

## Memory updates

**None** — `.memory/` and `RECAP.md` are manager-only and I am a reviewer.
Corrections proposed above; nothing applied. Nothing in the tree was edited.

---

⚠ **`PROTOCOL` rule 2 running count: 407 → 409.** Two of the three calls you
named came back **no**: the four-result compression is not honest in coverage —
it dropped four reviewed pro-safety results, all in one direction (B1, B2,
finding 7, finding 32's price half) — and §3 is not at its true scope, though the
failure is the missing counterweight rather than any claim inside it. The third
call comes back **yes**, with the breakdown above. **The two blockers are cheap:
one paragraph and two sentences.** ⚠ **Do not let anyone quote this document
until B2 lands** — its R4 definition is affirmatively wrong at this pin, and it
is wrong in the flattering direction for every `R3 − R4` figure the document
prints.
