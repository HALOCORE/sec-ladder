# `.memory-php/02-ladder.md` — how an EXTRACTED row's ladder differs

> ⚠ **`.memory-php/` is the AUTHORITATIVE layer for the PHP programme, and it
> SUPERSEDES any task report it contradicts** (`.tasks/PROTOCOL.md` rule 9).
> Only findings that have survived a full engineer→reviewer cycle are here.
>
> ⚠⚠ **SCOPE: this carries ONLY what is php-specific.** The PAT `.memory/`
> 00–06 applies unchanged — same harness, same bench rules, same measurement
> discipline, same Verus notes. **Do not restate any of it here; two copies of
> one rule is how both go stale.**
>
> The narrative, the open items and findings **F1–F111** live in `RECAP_PHP.md`
> ⭐ **and the statistic decision is `.tasks-php/STATISTICS_001.md`, committed**
> (⚠ this said *F1–F41* for seven findings, then *F1–F48* for forty-two
> more, then *F1–F90* for eleven more — `PROTOCOL.md` rule 13, **and it
> has now rotted THREE TIMES IN THIS FILE.** ✅ **`.tasks-php/boxcheck.py`
> CHECKS THIS LINE against the actual highest finding as of 2026-09-13,
> so it is the last time.** Count it: `grep -c '^### F' RECAP_PHP.md`).

---


- ⚠⚠⚠ **R2–R5 ARE NOT PORTS OF R1h.** Where the real upstream fix is
  **incomplete**, a safe-Rust rung built to it **panics** on the surviving
  inputs — **and a rung that panics is not a translation of the C.** So the
  hardened C rung carries the historical fix, the Rust rungs carry whatever is
  actually memory-safe, and only R1 diverges. ✅ **Reviewed and upheld.**
- ⭐⭐ **And an upstream fix can be BOTH dead and incomplete.** `ph03`'s 2004
  fix has two hunks: hunk 1 is **provably redundant** (Verus verifies 25/0 with
  it deleted from exec *and* with it neutralised in the spec; all 1 953 of its C
  firings are also refused by hunk 2), and hunk 2 leaves **144 over-reads in
  12 600 documents**. ⚠ **Do not assume a shipped fix is minimal OR sufficient —
  measure both ends.**
- ⚠ **A sanitizer limb is a claim about YOUR allocator, not about PHP.** `ph03`'s
  ASan evidence is **silent** when the source is allocated the way `emalloc`
  really allocates a zval string (`ALIGN8(len+1)`) — the over-read lands in
  padding. **Say "a detector fires under this allocator", never "PHP faults",
  unless the row models PHP's allocator.**
- ⭐⭐⭐ **AND AN UPSTREAM FIX CAN BE TOO BIG — PHP DELETED HALF OF ONE, AS A BUG,
  WITH A REGRESSION TEST.** `ph07`'s `cb3cca21b345` (2005) added two guards;
  `c2471b495009` (2009-09-23) removed hunk (b) as **bug #49354**. Measured:
  hunk (b) removes **0 of 396** over-reads and changes the answer on **13.5 %**
  of benign calls; hunk (a) alone removes **396 of 396** and changes none.
  ⚠⚠ **So `check.py` stage 7h — which refused the two-hunk rung for differing
  from R1 on benign inputs — WAS RIGHT, and it detected in the row's first hour
  what PHP's maintainers took four years and a bug report to find.**
  ⭐ **A gate stage that refuses your row is a hypothesis about your row before
  it is a hypothesis about the gate.**
  ⚠ **This is NOT a general permission to ship a subset of a `fix_commit`** —
  n = 1, and two drafts written as a permission were refused
  (`PROTOCOL_PHP.md` §C). ⚠ **Set beside `ph03`: of two shipped security fixes,
  one was half dead and half incomplete, the other half wrong. NEITHER WAS
  MINIMAL NOR SUFFICIENT AS SHIPPED.**
  ⚠⚠ **A THIRD ROW BREAKS THE RUN, AND IT IS UNREVIEWED — `RECAP_PHP.md` F57.**
  `ph16`'s `99e290f882c9` is reported **complete and minimal** for the
  memory-safety defect. **n = 3 now, and the sentence above is true of the two
  rows it names and NOT of the population** — which is what it was starting to
  be read as. **Nothing here is retracted until a reviewer has looked**; the
  pointer is so the next agent does not generalise from two.
  ⚠⚠⚠ **A FOURTH ROW, AND IT SWINGS BACK — ALSO UNREVIEWED (`RECAP_PHP.md`
  F65).** `ph29` (`TASK_PHP_027`) measured **BOTH** stages of its upstream fix
  and reports that **NEITHER removes the row's defect**: stage 2 buys *exactly
  two values of `to_read`* over stage 1 and removes **ZERO** truncation faults,
  and the stage-1 guard is **over-broad** — it refuses `to_read == 0`, which was
  never a fault. ⭐ **So at n = 4 the tally is: two shipped fixes not minimal and
  not sufficient (`ph03`, `ph07`), one complete and minimal (`ph16`), and one
  where neither of two candidate stages closes the defect at all (`ph29`).**
  ⚠⚠ **THE HONEST READING IS THAT THERE IS NO RUN AND NEVER WAS ONE** — four
  rows, four different answers. **Do not generalise from any of them until a
  reviewer has been over `_027` and `_025`.**
- ⭐⭐⭐ **AND ONLY THE VALUE POSTCONDITION MOVED. A memory-safety-only proof
  cannot see the difference at ANY strength.** Demonstrated by construction, not
  asserted (`TASK_PHP_022` §1): a mechanical weakening of `ph07`'s `verus.rs`
  verifies **17/0 plain and 20/0 twin against BOTH** the two-hunk and the
  one-hunk exec, and the `diff` between the two proofs is *hunk (b)'s six exec
  lines and comments* — **not one invariant, assert, ghost binding or
  `decreases`.**
  ⭐⭐ **The sharper half is what "memory-safety-only" costs to state here:
  NOTHING, because there is nothing to state.** The kernel returns a `u64` and
  writes no caller-visible memory, so the honest memory-safety-only spec is the
  **empty postcondition**; safety lives in the trusted items' `requires`, the
  `decreases`, and Verus's built-in checks. **Vacuity measured: the same kernel
  with its body replaced by `0u64` verifies 13/0.** An explicit ghost *"no read
  past `slen`"* postcondition also verifies in both configurations — **and even
  with all four of its instrumentation points deleted.**
  ⭐⭐⭐ **The number that says it best: the memory-safety-only proof verifies at
  `rlimit` 1 against the row's 9. Essentially the ENTIRE proof budget is the
  value postcondition.**
  ⚠⚠ **What this does NOT say, and the handoff said it for a day: *"only a value
  postcondition could have noticed."* The GATE would have** — stage 2's identity
  check moves on 4/32 and 297/2050 windows. **The claim is about PROOFS, not
  about observers.**
- **R1h = the real upstream `fix_commit`**, not a hand-written control.
  ⚠ `git fetch` of a bare SHA is refused by the server; **the patch URL works**:
  `https://github.com/php/php-src/commit/<sha>.patch` (~1.4 KB). Keep the patch
  bytes under the row so the citation survives without network. (F26.)
- ⚠ **A green php gate does NOT mean the upstream fix is complete, and cannot.**
  `check_sanitizers_hardened` hard-fails on any R1h diagnostic — correct for a
  hand-written PAT control, wrong for a shipped fix that is incomplete. That
  evidence lives in the row's `controls/`. **Standing limitation, not a bug to
  file.** (F31.)
  ⚠⚠ **DO NOT EXTEND THIS TO `check.py` STAGE 7h — that analogy was drawn at
  `TASK_PHP_017` §4b, the manager adopted it, and it is WRONG** (`TASK_PHP_018`
  §4.3). **They are different questions on different axes**: stage 7h asks
  whether R1h changes **benign output** — *a property of the fix*;
  `check_sanitizers_hardened` asks whether it still **faults** — *a property of
  the fix's completeness*. **Stage 7h has no known false refusal; its one
  refusal to date was correct.**
- ⚠ **`harness/build.py` links no `-lm`.** `floor()` emits a real call at `-O0`
  and is inlined at `-O3`, and libm was never merged into libc — so a `verbatim`
  libm kernel fails to link in the `-O0` cells. **Batched, not fixed.**
  ⭐ Whoever does it should know **`-lm` is link-only**, so for every pattern
  calling no libm function the re-measured numbers must be byte-identical —
  the re-measure is self-verifying. (F31.)

- ⭐⭐ **WHERE TO LOOK FOR THE FIX: a missing bound is often restored IN A
  DIFFERENT FRAME — and possibly MORE THAN ONCE.** `ph07`'s `mbfl_strcut` was
  characterised — by the catalogue *and* by an engineer — **by its loop**, so
  both checked the loop in the fixed version, found it still expressed in terms
  of `from`, and concluded no fix existed. **Both the conclusion and the first
  correction to it were wrong:**

  | | |
  |---|---|
  | **the fix**, 2005-12-15 | **`cb3cca21b345`**, *"Fixed possible memory corruption inside `mb_strcut()`"* — **in the CALLER, `ext/mbstring/mbstring.c`**, one function up and one file away |
  | 5.4.0's prologue clamp | `d9dda48f8a7e`, 2010, a **64-file libmbfl re-sync** with no bug number and no security label — **a second, later restoration of the same bound** |

  ⚠ **This entry previously said *"restored in the PROLOGUE"* and named the 2010
  clamp as the fix. That is the 2010 story, not the repair.** ⭐ **The lesson is
  one level up: `01-extraction.md`'s three frames need a FOURTH — the REPAIR
  SITE — and a search keyed on the defect's function cannot find a fix whose
  subject names the caller.** (F34, corrected by F38 and `TASK_PHP_016` §2.)
- ⚠ **A fix can ship inside an unlabelled rewrite.** `ph07`'s vulnerable code went
  out **byte-identical from 5.0.0 through 5.3.2** (⚠ **this said `5.3.x`; 5.3.3
  carries the rewrite** — `TASK_PHP_016` §4.1) and was re-clamped by a 5.4.0
  rewrite carrying no security label — so *"no CVE, no security commit"* is **not**
  evidence that a defect was never fixed. Check the code at later tags.
- ⚠⚠ **AND THE CORPUS INDEX HAS A `fix_commit` COLUMN — LOOK THERE FIRST.**
  `index.csv` carries a sha for **all 166 rows**, and every catalogued row's fix
  is surveyed in `.tasks-php/FIXSURVEY_001.md`. ⚠ **It names *a* fix for the
  row's function, NOT necessarily the one that removes the 5.0.0 defect** —
  `ph12`, `ph21` and `ph22` all name a later hardening. **Read the column, fetch
  the patch, then confirm against the tags.** (F38, F40.)

## The ladder, as row 1 actually measured it

`ph03`, `Ir(kernel)`, `small.bin`, `O3 / isolated` — ⚠ **within-row ratios only**
(`03-numbers.md` forbids any comparison with a `pNN` figure):

> ⛔⛔⛔ **THIS TABLE SHIPPED WITHOUT NAMING ITS BASELINE FOR A DAY, AND TWO OF
> ITS FOUR RUST CELLS CHANGE SIGN WHEN THE BASELINE CHANGES** (`TASK_PHP_049`
> §2.3). **Repaired 2026-09-13 by adding the `c-clang` column, which
> `.memory/01-ladder.md` has called MANDATORY for any C-vs-Rust claim since
> `TASK_001` and which this layer never inherited.** ⚠⚠ **The bullet two below
> warned that *"`c-clang` beats `c-gcc` by 15.4 %, larger than every safety
> effect on this row"* — so the file warned about the effect and then published
> the table the effect reverses.**

**Re-derived `TASK_PHP_049` §2.3 from `results-php/ph03-uudecode-bound.json`,
A1, `O3/isolated`, *"rung dearer than the named C baseline by"* — ⚠ all eight
cells from ONE source, rather than splicing a clang row onto the older gcc row:**

| input | baseline | `safe_naive` | `safe_tuned` | `unsafe` | `verus` |
|---|---|---:|---:|---:|---:|
| `small.bin` | `c-gcc` *("what a distro ships")* | +27.06 % | +3.78 % | ⛔ **−7.49 %** | ⛔ **−7.49 %** |
| `small.bin` | ⭐ **`c-clang`** *(**the SAME-BACKEND baseline**)* | +49.95 % | +22.48 % | ⛔ **+9.17 %** | ⛔ **+9.17 %** |
| `large.bin` | `c-gcc` | +29.71 % | +5.78 % | ⛔ **−5.70 %** | ⛔ **−5.70 %** |
| `large.bin` | ⭐ **`c-clang`** | +52.35 % | +24.25 % | ⛔ **+10.76 %** | ⛔ **+10.76 %** |

⛔⛔ **SO *"unsafe Rust is 7.6 % FASTER than C"* IS A `gcc` STATEMENT. Against
the same-backend baseline the SAME CELLS ARE ~9–11 % SLOWER, on BOTH inputs, at
5.7–10.8 pp.** ▶ **Quote both columns, or say explicitly that only one was
measured** — one column is not a number with error bars, **it is a different
sign.** ⓘ The `c-gcc-h` cell (**−0.4 %**, the real 2004 fix) is a **C-vs-C**
comparison and is unaffected. ⚠ The figures previously published here
(`+26.8 / +3.7 / −7.6 / −7.6`) differ from the re-derivation in the second
decimal; **the re-derivation governs, and both are the same story.**

⭐⭐⭐ **AND `ph03`'s OWN `NOTES.md:692-697` ALREADY SAID SO** — *"Unsafe Rust
beats gcc C on this kernel and loses to clang C, and the clang column is why that
must be stated as two numbers."* ▶ **The ROW got it right and the AUTHORITATIVE
LAYER dropped the column.** ⚠⚠ **That is the `SYNTHESIS.md`-beats-`RECAP_PAT.md`
pattern `CLAUDE.md` records, one level deeper: here the row beats `.memory-php/`.**

- **Tuning recovers 86.4 % of the naive-safe gap**, so *"safe Rust costs 27 %"*
  and *"safe Rust is nearly free"* are **the same pattern written two ways.**
- ⭐ **`verus` is BYTE-IDENTICAL to `unsafe`** (`md5_fn 33850579` on both) — **the
  proof costs nothing at run time.**
- ⭐ **The safety check can be NEGATIVE-cost**: the hardened C beats the unchecked
  C, because the check lets gcc drop a `setae` and two `cmove`s. (F30, F33.)
- ⚠⚠ **Two things in that same table are NOT safety effects and will be misread
  as such**: `c-clang` beats `c-gcc` by **15.4 %** (larger than every safety
  effect on the row), and **both C compilers vectorise while no Rust rung does** —
  the latter is a property of *how the translation is written*, not of Rust.
- ⚠⚠⚠ **NO RATIO HERE IS *THE* COST OF SAFETY, AND THESE ARE `fixed-R4 bound`s
  — PAT's term, and PAT's rule is that a bound ships LABELLED, beside a
  cheapest-found counterpart.** `controls/spellings.py` was not built, so each
  figure is the cost of *these spellings* of these rungs. **The debt is now on
  BOTH built rows** (`TASK_PHP_016` §7.1).
  ⚠ **The obligation is inside `ph03`'s own hashed `why`**: *"Every pattern owes
  an in-contract spread beside its headline."* Undischarged, not unforeseen.
  ⚠⚠⚠ **AND THE MANAGER'S *"the direction is not a coin flip — it moves against
  safe Rust"* IS WITHDRAWN. It was a theorem about taking a minimum, presented
  as an observation** (`TASK_PHP_017` §2.4). What the record actually supports:

  > Of the **19** PAT rows whose R4 side was searched, **eight found a cheaper
  > R4 and eleven found none** — the R4 endpoint is degenerate more often than
  > not. Where one *is* found the published gap necessarily widens against safe
  > Rust, **because the statistic is `R3ship − min(R4 found)` and a minimum can
  > only fall**; the direction of those four is *forced by the arithmetic* and is
  > not evidence about an unsearched number. ⚠ **Three of the four counterparts
  > are OUT OF CONTRACT by their own patterns' records**; only `p22`'s is
  > admissible. `SYNTHESIS.md:271-277` already states the real asymmetry — *the
  > number moves toward whichever side you did not search*, and **the R3-side
  > levers are the cheap ones**: on **≥ 9** PAT rows an R3-side respelling moved
  > the headline **TOWARD** safe Rust.

  ⭐⭐⭐ **AND `ph07` HAS NOW SEARCHED BOTH SIDES — the first php row to do so,
  and the first to discharge the obligation** (`controls/spellings.py`, the
  first in `patterns-php/`; `TASK_PHP_018` §2, reviewed at `TASK_PHP_022` §3):

  | | |
  |---|---:|
  | `fixed-R4 bound` — `R3ship − R4ship` | **+11.98 %** |
  | cheapest-found in-contract — `inf(R3 found) − R4ship` (`r3_reslice`) | **+1.96 %** |

  ⚠ **Quote both, labelled, or neither.** ⚠ **`TASK_PHP_017` B1's `+2.62 %` is
  SUPERSEDED** — it was measured on the corpus the R1h rebuild deleted.
  ⭐⭐ **The R4 side is DEGENERATE**: seven spellings from two agents, none
  cheaper than a tie, **and the metric objection was tested and failed** (whole
  -program `Ir` beside kernel-exclusive). **So this bound is over a SEARCHED
  endpoint**, which is a materially stronger object than an unsearched one — and
  it makes `ph07` the **12th of 20** rows where an R4-side search found nothing,
  confirming `SYNTHESIS.md`'s *"degenerate more often than not"* from inside
  this programme. ⚠ **NO PAIR INTERVAL**: `min(R3 found) − min(R4 found)`
  differences two upper bounds and bounds nothing.
  ⭐ **`r4_index0` is a THIRD kind of result the bench rule has no name for**:
  `s[0]` for `*s.get_unchecked(0)` is **byte-identical machine code** (checked
  independently), verifies 21/0, and **removes one of four `get_unchecked` call
  sites** — *a smaller trusted surface at the same price*, which is neither a
  cheaper spelling nor a re-ship.
  ⚠⚠ **`ph03` has still searched NEITHER side and is unbounded in BOTH
  directions.** (F39, corrected by `TASK_PHP_017` §2.4; discharged for `ph07`
  only.)
  ⚠⚠ **AND SO DOES `ph16`, DELIBERATELY.** Row 3 (`TASK_PHP_025`) was told to
  say if carrying `controls/spellings.py` made the build two tasks; **it did**,
  so the row shipped with the debt declared in three places. ⚠⚠⚠ **`ph16`'s
  `R3ship − R4ship` is NEGATIVE — safe-tuned measures CHEAPER than unsafe — so
  no figure in that row is a `fixed-R4 bound` at all**, and whether that is a
  real non-monotone ladder or a spelling artefact is **unknown**.
  ⚠⚠⚠ **AND SO DOES `ph29`, AND ITS SPREAD IS NEGATIVE TOO — UNREVIEWED
  (`RECAP_PHP.md` F65).** Row 4 (`TASK_PHP_027`) measured **`R3 − R4` at
  −6.1 %/−6.4 %**, the same direction as `ph16` and larger.
  ⭐⭐ **THAT IS THE PART WORTH NOTICING: TWO INDEPENDENTLY BUILT ROWS, IN
  DIFFERENT FAMILIES, PUT SAFE-TUNED CHEAPER THAN UNSAFE.** Re-derived by the
  manager from the published tables (`Ir`, O3/isolated), **not taken from a
  report**:

  ```
  ph03   R3 191,208,596  R4 170,434,489   +12.19 %   POSITIVE
  ph16   R3  88,874,724  R4  89,974,452    -1.22 %   NEGATIVE
  ph29   R3  23,441,029  R4  24,951,895    -6.06 %   NEGATIVE
  ```

  ⚠⚠ **n = 2, and both came off the same machinery, so this is NOT yet an effect
  and must not be reported as one** — but it is materially harder to explain as a
  per-row spelling artefact than one row was. ⚠ **`ph03` is POSITIVE and belongs
  to the other case** — it owes the search because it is unbounded on both
  sides, not because its sign is odd. **`TASK_PHP_028` is how we find out.**

  > ⚠⚠⚠ **FLAG — NOT A FINDING (rule 9). `TASK_PHP_028` HAS REPORTED ON `ph16`
  > AND IS UNREVIEWED.** Recorded here because the paragraph above states the
  > question as open and it is answered for one of the three rows.
  > `RECAP_PHP.md` **F67**; `.tasks-php/TASK_PHP_028_REPORT.md`.
  >
  > **`ph16` IS DISCHARGED.** `fixed-R4 bound` **−1.22 %** · `cheapest-found
  > in-contract` **−1.42 %** (`r3_split_at`), per-call statistic, **both
  > labelled, no pair interval, no rung re-shipped.** ✅ Manager re-verified:
  > `check.py: PASS`, brackets `66/0` and `10/0`, no re-measure.
  >
  > ⭐⭐ **AND THE SPREAD IS A *RESULT*, NOT A SPELLING ARTEFACT.** The R4 side
  > is **degenerate** — four respellings of the very index the mechanism blames
  > are all dearer or byte-identical, **including `r4x_subslice`, which is R3's
  > own spelling, at +1.80 %.** The **mirror control** settles it: `r3_absindex`
  > (R3 given R4's signature) is **byte-identical to `safe_naive.rs`** at
  > **+33.07 %**. **So the subslice is worth −24.9 % in safe Rust and +1.8 % in
  > unsafe Rust: the two rungs are cheapest under DIFFERENT spellings, and R3's
  > minimum sits under R4's.**
  >
  > ⚠⚠ **STILL n = 1 FOR THIS EXPLANATION — AND THE THIRD FLAG BELOW CONFIRMS
  > IT RATHER THAN EXTENDING IT.** `ph29` has since been searched on both sides
  > (`TASK_PHP_035`) and is **NOT** this mechanism: same spelling cheapest on
  > both sides, R4 **not** degenerate. **F67 stays n = 1.**
  > ⚠ **`ph29` cannot simply be cloned into**: its `.idiom_audit` is
  > `spellings: 4, forbidden: 4, required: 0`, so a `spellings.py` copied from
  > `ph07` would **pass every candidate while checking nothing**
  > (`RECAP_PHP.md` open item 51 — a manager `spec.md` call, owed first).
  > ✅ **BOTH SENTENCES ARE NOW HISTORY**: item 51 is **closed**, the audit reads
  > **12 / 4 / 8**, and the debt is **discharged**. Kept because the *reason* the
  > clone would have been vacuous is the durable part.
  > ⚠ **`ph03` (+12.19 %) is searchable with no `spec.md` edit** —
  > `spellings: 11`, 6 forbidden. **`TASK_PHP_028.md` §4.3 said otherwise and
  > named the wrong row** (F70).
  >
  > ⚠ **Which statistic a bound is quoted in is UNDECIDED across rows**: `ph07`
  > is published from the **marginal** and this from the **per-call**, and on
  > `ph16` they differ by **0.72 pp — 59 % of the figure.** Open item 52.

  > ⚠⚠⚠ **SECOND FLAG — NOT A FINDING (rule 9). `TASK_PHP_032` BUILT `ph64`,
  > THE FIRST TEMPORAL ROW, AND IT IS UNREVIEWED.** `RECAP_PHP.md` **F71**.
  >
  > ⚠⚠ **THE "TWO ROWS, SAME SIGN" READING ABOVE IS NOW 2 OF 4 AND MUST NOT BE
  > QUOTED AS A TREND.** `ph64` ships `fixed-R4 bound` **+17.08 % / +15.37 %**,
  > **unsearched on both sides** — so it owes the same debt, and it **breaks the
  > pair**:
  >
  > ```
  > ph03  +12.19 %   POSITIVE      ph16   -1.22 %   NEGATIVE
  > ph64  +17.08 %   POSITIVE      ph29   -6.06 %   NEGATIVE
  > ```
  >
  > **Two positive, two negative, across three axes' worth of machinery.** ⭐ The
  > `ph16` mechanism (F67 — the two rungs cheapest under *different* spellings)
  > remains the only *explanation* anyone has, and it is established on **one**
  > row.
  >
  > ⚠⚠ **AND `ph64`'s FIGURES ARE IN `marginal_ir_per_call`, NOT
  > `kernel_exclusive_ir`** — on this row that column **hides the upstream fix
  > entirely** (identical to the instruction for both C rungs) **and reverses R2
  > vs R3.** ⚠ **Never difference two rows of a php table without checking which
  > column each is quoted in** — which is open item 52's question arriving on a
  > second row, from a different direction.

  > ⚠⚠⚠ **THIRD FLAG — NOT A FINDING (rule 9). `TASK_PHP_033` REPAIRED `ph29`'s
  > DECLARATION AND `TASK_PHP_035` DISCHARGED ITS SPELLINGS DEBT. BOTH ARE
  > UNREVIEWED.** `RECAP_PHP.md` **F72–F79**. Manager-verified from
  > `results-php/gate/` and from `controls/spellings.json`, not from the reports.
  >
  > ⚠ **THE `4 / 4 / 0` AUDIT NUMBERS ABOVE ARE STALE, TWICE OVER.** Item 51 is
  > **closed**: the declaration now pins **`spellings: 12`, forbidden 4,
  > required 8**, `present 22`, `required_pins_nothing 0`. And the item's own
  > framing was half wrong — **`required` CANNOT fail the gate BY DESIGN**
  > (its scope lives in English; `idiom_audit`'s docstring argues it at length)
  > while `forbidden_hits` does. What was really wrong is that **nothing
  > positive was pinned**, so the admissible class was **undecidable by grep**.
  >
  > ⭐⭐⭐ **AND THE HEADLINE: `ph29`'s R4 ENDPOINT IS *NOT* DEGENERATE — THE
  > FIRST ROW IN EITHER PROGRAMME WHERE IT MOVES.** `r4_fold_iter` has a Verus
  > twin that **verifies (10/0, no `assume`, no new trusted item, no
  > `is not supported`) AND compiles to a byte-identical kernel** (209 insn,
  > `d71669d3c0e6`, exec == twin). `r4_endpoint_degenerate: false`.
  > **A1, `Ir`/call, `small.bin`:** `fixed-R4 bound` **−6.06 %**; R3-side span
  > **−6.06 % .. +5.08 %**; `r4_fold_iter` **−5.63 %**, admissible and cheaper;
  > `r4_fold_slice` a byte-identical tie; `r4_head_array` out of contract.
  >
  > ⚠⚠ **THIS IS A COUNTEREXAMPLE TO `.memory/02-bench-rules.md` REASON 2's
  > PREMISE**, *"the R4 side is chained to the prover … so it usually cannot
  > move"*. ✅ **The RULE — never re-ship a rung for a cheaper spelling — is
  > untouched and in fact VINDICATED**: a cost-selected R4 would have shrunk
  > this row's published gap by **5.63 pp**. ⚠ That is a PAT-side memory and it
  > is **not edited from here**; it is reported.
  >
  > ⚠⚠ **`ph29` IS NOT `ph16`'s F67 MECHANISM, SO F67 STAYS n = 1.** F67 is
  > *two rungs cheapest under DIFFERENT spellings, with a degenerate R4*. Here
  > the **same** spelling is cheapest on both sides and R4 is **not**
  > degenerate. The mirror is symmetric — R4's fold in R3 gives −0.38 %, R3's in
  > R4 gives −5.63 % — so **neither rung's `unsafe`-ness contributes measurably
  > to this row's gap.**
  >
  > ⚠⚠⚠ **AND OPEN ITEM 52 GETS SHARPER, ON A NEW AXIS.** `r3_copy_loop` is
  > **`+5.08 %` on A1 and `−0.99 %` on the slope — the two DISAGREE ON SIGN**,
  > on an in-contract R3 variant. ⚠ **This is a disagreement WITHIN family A**
  > (per-call vs per-window-byte), not the A-vs-B one F74 measured, and its
  > driver is the **fixed per-call cost** — `r3_copy_loop`'s is **105.35**
  > against R4ship's **45.19** — **not callee share.** ▶ **F74's
  > `|Δinside_share| ≤ 0.02` rule does not cover this case and must not be
  > quoted as if it did.**

  > ⚠⚠⚠ **FOURTH FLAG — NOT A FINDING (rule 9). `TASK_PHP_036` BUILT `ph45`,
  > ROW 6 AND THE FIRST TYPE ROW, AND IT IS UNREVIEWED.** `RECAP_PHP.md`
  > **F80/F81**. Gate `PASS-WITH-BLOCKED-ROWS`, `failures []`, brackets `66/0`
  > and `14/0` — manager-verified from the record. **All three axes are now
  > open.**
  >
  > ⭐⭐⭐ **THE ROW'S RESULT CONTRADICTS ITS OWN BUILD BRIEF, WHICH THE MANAGER
  > WROTE.** *"Safe Rust cannot store a pointer in an `i32` at all"* is **false**
  > — re-verified independently by the manager: `(&x[0] as *const u8) as i32`
  > compiles under `rustc -D warnings -O` with **zero diagnostics**, truncates,
  > and casts back to a wild pointer, **with no `unsafe` block**. The same idiom
  > in C **warns once per cast site**, and **bug #30573 IS that warning**. Only
  > **Verus** refuses. ▶ **So safe Rust blocks the wild WRITE (`E0133` on the
  > dereference) and NOT the wild VALUE** — ⭐ **F71's shape on a second axis, so
  > it is now TWICE**, and it is the sharpest ladder result in the corpus.
  >
  > ⚠⚠⚠ **AND IT REFUTES F74's PUBLISHED RULE, ONE ROW AFTER THE MANAGER
  > PUBLISHED IT AND PUT IT INTO TWO TASK FILES.** `ph45`'s `inside_share` is
  > **0.055–0.094**, seven times more extreme than anything else in the corpus,
  > and it **flips sign between A1 and the whole-program statistic at
  > `|Δinside_share| = 0.003`** — well inside F74's 0.02 threshold. **The
  > condition passes and A1 is still wrong.** ▶ **CORRECTED RULE, two conditions,
  > conjunction measured clean at 151 of 366 comparisons with ZERO flips:**
  > **(i) `min(inside_share)` over the two cells must be HIGH — A must actually
  > SEE both — AND (ii) `|Δinside_share| ≤ 0.02`.** ⚠ The threshold in (i) is
  > **not tuned and six rows cannot pin it** (`>0.3`, `>0.5`, `>0.6` all give 0
  > flips). ⚠ **Do not quote F74's one-condition form.**
  >
  > ⚠ `ph45` publishes **both** families, labelled: A1 **+0.37 %**,
  > whole-program **−3.06 %**. ⚠ **The upstream fix is 68,613 `Ir` CHEAPER than
  > the defect** and A1 reports that as **`0.00 %`**.
  >
  > ⚠⚠ **`ph45`'s R4 endpoint is UNSEARCHED, making it 3 of 6** (with `ph03` and
  > `ph64`) — and F77 has just shown that debt is **not cosmetic**.

  > ⚠⚠⚠ **FIFTH FLAG — NOT A FINDING (rule 9), AND IT IS THE MANAGER'S OWN
  > CORRECTION TO THE FOURTH.** `RECAP_PHP.md` **F82**, `.temp/mgr172/NOTES.md`,
  > probe `identity_null.py` (`--selftest` PASS, 9 must-fire negatives).
  >
  > ⚠⚠ **F74's NULL CONTROL RESTS ON A PREMISE THAT WAS NEVER CHECKED PER ROW.**
  > `.temp/mgr170/null_control.py` asserted *"`identity` pins R4 and R5
  > byte-identical"* for **all 39 rows**. Measured at O3: `exact` on **4 of 7
  > PHP** and **28 of 33 PAT**. ✅ **Every number F74 published SURVIVES** —
  > the correct predicate is **`Δnopad == 0 and Δbytes == 0`**, not the level,
  > because `norel` also covers *same instructions at different rip-relative
  > displacements* (`ph07` and `p25` both say so in their own `identity` notes).
  > Under it **all 33 PAT rows are true nulls** and `ph03` really is `exact`.
  > ⚠⚠ **Restricting on the LEVEL instead would have dropped PAT's family-B
  > worst null from `+5.0102 %` to `−0.8734 %` — a 5.7× reduction to a plausible
  > number, by discarding five VALID cells. The manager would have published it.**
  >
  > ⭐⭐⭐ **THE REAL GAP, AND IT IS A GAP IN THE ARGUMENT AND NOT IN A NUMBER:
  > A NULL CONTROL IS ONE-SIDED. A statistic hard-wired to `0` would ace every
  > null in this tree, and F74 argued from nothing else.** The **sensitivity**
  > half is now measured, off the two rows that are *not* nulls: family A
  > resolves a **2-instruction** static difference **to the instruction** —
  > `Δ = −3000` over 1500 calls and `−400` over 200, `exec_rate` **1.0000**
  > twice — while `ph64`'s single instruction sits on a **conditional** path
  > whose rate two inputs agree on to **0.0007**. ⚠ `1.0000` is *too clean* and
  > **`ph64` is the control on `ph45`**: a self-feeding computation would read
  > `1.0` everywhere.
  >
  > ⭐ **AND THE SIGN: ON `ph45` AND `ph64` THE PROVED RUNG IS CHEAPER THAN THE
  > UNSAFE ONE** — Δnopad `−2` and `−1`, family A `−0.0383 %` and `−0.0067 %`
  > ⚠ (**`small.bin`**; on `large.bin` the same two cells read **−0.0054 %** and
  > **−0.0009 %**, **7× apart**), **with no search at all**. Nothing is
  > violated; both rows pin `differ`. ⚠⚠ **THIS LINE CARRIED THE TWO FIGURES
  > UNLABELLED** — `TASK_PHP_037` §9.3 flagged it, `RECAP_PHP.md:2120` was
  > corrected and **this layer was not**, which is `check.py`'s own *⚠⚠⚠ DO NOT
  > MAX IT OVER INPUT* landing inside the finding that quotes it approvingly.
  >
  > ⭐⭐ **AND THE SENSITIVITY HALF FOR FAMILY B, WHICH THIS SECTION NEVER
  > MEASURED** (`.tasks-php/php_null.py`, `--selftest` PASS, 12 negatives;
  > ✅ **REVIEWED AND UPHELD at `TASK_PHP_043` §2.5 — the ratio was re-derived
  > from the table's OWN population (`Δnopad`, `unsafe` vs `verus`, 9 cells,
  > zero respellings), so it does NOT rest on `ph45`'s respelling spread**).
  > ⛔⛔ **BUT THE *AXIS* THIS PARAGRAPH ONCE CARRIED IS REFUTED — see the
  > `inside_share` ruling at the end of this block.** On the same four cells:
  > **A resolves the
  > static difference to the instruction while `|B/A|` is 49.6×–393.9×**, and it
  > is **0.2×–3.0×** at every large-Δ cell (`ph03`/`ph07`/`ph16`/`ph45`/`ph64` at
  > `-O0`, Δnopad `+17`…`−170`). ▶ **A clean regime separation with no overlap:
  > B loses a SMALL code difference completely, and small-Δ is exactly where a
  > `fixed-R4 bound` operates.** ⛔⛔ **AND THE SEPARATING VARIABLE IS `|Δ|`, NOT
  > LANGUAGE: all nine of these cells are SAME-LANGUAGE** (`TASK_PHP_043` §3.5),
  > **so the *"same-language ⇒ only A resolves it"* axis this evidence was once
  > read as supporting is FALSE ON THIS VERY TABLE.** ⚠ **B is not "wrong"** — it is a whole-program
  > slope, so its true value is not `−2`; the defensible statement is that **at
  > most `|Δnopad|` Ir/call of B's reading can be the code change**, so on
  > `ph45/O3/large` at least **785.86 of 787.86** is something else. ⚠ **The
  > MAGNITUDE ratio separates by regime; the SIGN does not** — 5 of 9 cells
  > disagree in sign, 3 of 4 small-Δ against 2 of 5 large-Δ. ⛔ **Family C's
  > sensitivity is UNMEASURED**; on `ph03/small` C reads `+265.924` against B's
  > `+266.000` on a **byte-identical** pair, so the prediction is that C fails
  > this regime too — **which is what open item 62 must test FIRST.**
  >
  > ⚠⚠⚠ **AND IT WIDENS THE R4 SEARCH THIS SECTION IS ABOUT.** The shared `why`
  > block argues R4 admissibility **from the identity pin** — *"All six patterns
  > pin `identity: unsafe == verus, O3 exact`, so an R4 … must have a
  > byte-identical R5 twin that Verus verifies."* **That antecedent is FALSE on
  > `ph07`, `ph45` and `ph64`.** ▶ **An R4 candidate on those three need only
  > VERIFY, not compile byte-identically**, so their searches are **wider than
  > `ph29`'s** and F77's method is not the binding constraint. Open items 60
  > (PAT-side routing) and 61.

  > ⚠⚠⚠ **SIXTH FLAG — THE MANAGER CORRECTED HIMSELF FOUR TIMES IN ONE ROUND,
  > `TASK_PHP_037` DISCHARGED ITEM 58 ON `ph45`, AND THEN `TASK_PHP_038`
  > REVIEWED THE LOT AND REFUTED THREE MORE OF MY CLAIMS.**
  >
  > ✅✅ **STATUS, 2026-09-13: THIS BLOCK IS NOW AUTHORITATIVE.** F83–F86 were
  > UPHELD-NARROWED at `TASK_PHP_038`; **`TASK_PHP_043` closed the cycle on
  > twelve more** — **F88 · F93 · F95 · F99 UPHELD**, **F89 · F91 · F92 · F94 ·
  > F98 · F100 · F101 UPHELD-NARROWED**, **F90 REFUTED**, and **F96 · F97 still
  > UNREVIEWED and therefore still excluded.** ⚠⚠ **Every narrowing is APPLIED
  > IN THE SENTENCE IT NARROWS below, not appended** (`RECAP_PHP.md` item 73),
  > because a correction appended leaves the old number readable — which this
  > layer has now done four times.
  > ⚠ **The 2026-09-12 wording said *"Nothing below is authoritative yet; this
  > is still a FLAG"*. It is no longer a flag; the parts that are still open say
  > so individually.**
  >
  > ⛔⛔ **WHAT THE REVIEW REFUTED, and all three were mine:**
  > **(1) F84's `−1.00` mechanism.** It is **not** the slope — it is exactly
  > **one instruction per kernel call in `main`**, `main_exclusive_ir`
  > `Δ/n = −1.0000` on `ph00` and `p11`, **already in every committed record
  > and needing no callgrind.** ⭐ **My decomposition was right and I put the
  > instance in the wrong term.** C reads `0.000` because `main` is outside
  > the call tree, so **B is RIGHT there and C is blind.**
  > **(2) F83's environment control is worthless** — it tests a *stack*-array
  > alignment mechanism on a row whose per-call buffer is `emalloc`, i.e.
  > **heap**. The mechanism F83 itself names is **UNTESTED**; its conclusion
  > survives on the B/C agreement alone, on **one** leg not two.
  > **(3) F86(b) is a logical TAUTOLOGY** — *"0 mispredictions over 366"* is
  > not evidence, and my negative cannot fire for the reason it states.
  > F86(c) is **too strong**; *"three independent statistics"* is **wrong** —
  > C and W1 are **nested scopes of one run**, ≈176 k `Ir` apart. And the
  > cross-language flip count is **29, not 28**, which the draft's own
  > arithmetic already implied.
  >
  > ⭐⭐⭐ **AND THE REVIEWER'S OWN FINDING IS BIGGER THAN ANYTHING IT
  > REFUTED: FAMILY B IS ONE DRAW OF A SAMPLING DISTRIBUTION.** `probe_iters`
  > is **`[100, 200]` in all seven PHP `spec.md`s and in `p11`**
  > (manager-verified), the driver picks its window by a pseudo-random
  > function of a running accumulator, and on `ph29` the slope level moves
  > **32 % across draws with the published draw the LARGEST of seven.**
  > ⚠⚠ **NAME THE DENOMINATOR: that `32 %` is `range / mean`, re-derived by the
  > reviewer as `31.42 %` on an INDEPENDENT 8-span sweep (`TASK_PHP_043` §5.6,
  > F88 UPHELD). A second normalisation, `38.6 %`, is also in circulation and
  > NEITHER document said which it was using** — `RECAP_PHP.md` item **92**.
  > `ph03` reads **0.03 %** because its per-window work is uniform — **that
  > contrast is the control.** ⚠⚠ **So `inside_share` is ARITHMETICALLY FINE
  > AND INTERPRETIVELY VOID on any row with heterogeneous per-window work:
  > it divides a mean over 25 000 calls by a biased 100-call sample.**
  > ▶ **90–93 % of the B-vs-C gap I called *"the confound is real and
  > present"* is the DRAW.** ✅ Signs stable over seven draws, so **no flip
  > verdict moves.**
  >
  > ▶ **THE DECISION: publish both, and the second column MUST BE FAMILY C.**
  > Family B is disqualified twice — it misses real work (F84) and it is one
  > unstable draw (F88) — and W1 is not independent of C. ⚠⚠ **So the only
  > admissible second column is the one nobody has built (item 62).**
  > ✅ **`ph64`'s B1 headline: item 66 ANSWERED NO — the draw CANCELS in a
  > same-language ratio and does NOT cross-language (F89, reviewed, and the
  > contrast reproduces at `55.6×` by a different design).** ⚠ **F89's
  > `0.07 pp` is `1.95×` from the reviewer's `0.1365 pp` over a DIFFERENT span
  > set, so quote it as *that sweep's* same-language spread and never as *the*
  > same-language spread.**
  >
  > ### ⭐⭐⭐ AND THE AXIS IS SETTLED, AT `TASK_PHP_043` §3 — **IT IS `inside_share`, AND BOTH EARLIER CANDIDATES LOSE**
  >
  > **The rule, and it is the one to apply from here on:** ⭐ **a code difference
  > is resolved by family A exactly to the extent the difference lands INSIDE
  > THE KERNEL SYMBOL, and the measure of that is `inside_share` — which is
  > ALREADY COMPUTED FOR EVERY CELL IN EVERY RECORD.** The two-condition
  > conjunction this file already states is the operative test; **it is
  > language-agnostic, it is measurable PER COMPARISON with no new machinery,
  > and it catches all nine same-language flips.**
  >
  > ⛔ **REFUTED: *"same-language vs cross-language"*** (F91's axis) — all nine
  > of its own cells are same-language and separate by `|Δ|`.
  > ⛔ **REFUTED: *"does the callee work diverge"*** (the rival, item 78) —
  > **a flip ENTAILS callee divergence** (`a·b < 0` on all 38), **so the rival's
  > variable does not vary**; and on the 3 cells with `Δnopad` ground truth the
  > callee-inclusive column is wrong by **50–400×**.
  > ⭐ **CONSEQUENCE FOR ITEM 62 (family C): narrower and cheaper. The condition
  > is `inside_share`, not a per-comparison declaration** — and **F91's own open
  > demand is the only thing item 62 must do FIRST: measure C's SENSITIVITY, not
  > just its null.**
  > ⚠⚠ **SCOPE: the nine cells are from TWO rows** — `ph45` (7) and `ph64` (2),
  > both with known statistic pathologies — and **`ph00`/`ph03`/`ph07`/`ph16`/
  > `ph29` contribute ZERO same-language flips.** ▶ **The phenomenon is
  > concentrated, and a third row could still move this.**
  >
  > ⭐ **A PRE-SEARCH PREDICATE, because this is usable before a row's endpoint
  > search runs:** compute `inside_share` first; **`ph45` at 9.5 % published in
  > W1 and `ph53` at 89.5 % published in A1, and both were right.**
  >
  > ⚠ **The count of my corrections this round is SEVEN, and not one was
  > arithmetic.** Every one came from a second method applied to something I
  > had published from a single probe, a two-row sample, or — twice now — a
  > restatement of a definition mistaken for a measurement.
  > `RECAP_PHP.md` **F83–F87**, `.temp/mgr172/NOTES.md`, probes
  > `identity_null.py` · `inclusive_ir.py` · `bc_sweep.py` · `flip_exact.py`,
  > all `--selftest` PASS. ⚠ **The statistic decision is
  > `.tasks-php/STATISTICS_001.md`, COMMITTED.** ✅ **AS OF 2026-09-13 TWELVE OF
  > ITS FOURTEEN UNREVIEWED FINDINGS HAVE CLOSED THEIR CYCLE, so the parts quoted
  > in this file ARE authoritative** — ⚠ **but that file is still marked NOT
  > AUTHORITATIVE as a whole and still carries F96/F97's open material.**
  > ⛔⛔ **AND IT HAS NOW BEEN THE STALE COPY TWICE:** its status box read *"F90
  > disagrees with the reviewer"* while **its own §5, 145 lines later, settled
  > item 68 `NO` and F90 is REFUTED**; and its §2 table cell published A as
  > *"blind to callees"* on evidence `RECAP_PHP.md` had already withdrawn.
  > ▶ **Both repaired 2026-09-13. This is item 73's shape for the third time:
  > the correction lands in `RECAP_PHP.md` and not in the document `RECAP_PHP.md`
  > calls "the whole argument".** ⓘ This line
  > used to cite that file's **gitignored predecessor draft** (named in
  > `STATISTICS_001.md`'s own header), i.e. **the authoritative layer rested on
  > a gitignored draft** — open item **65**'s defect, live. Re-pointed at the
  > committed successor for free. ⚠ The old path is **not repeated here**, so
  > `citecheck.py` stays quiet on a citation that is deliberately historical.
  > ⚠⚠ **`STATISTICS_001 §6`'s first clause is itself FALSE and staged for
  > correction**: `PROTOCOL_PHP.md` is in **no** digest, so writing a rule there
  > costs nothing; only the shared `idiom.why` (in `contract_sha256`) costs a
  > six-row re-gate.
  >
  > ⭐⭐⭐ **`ph45`'s R4 ENDPOINT MOVES AND SO DOES ITS R3 — THE FIRST ROW WHERE
  > BOTH DO.** `r4_buf_slice_inline` is **−23.47 %** whole-program with a twin
  > verifying **41/0** and **10 unchecked-dereference sites against the shipped
  > rung's 12** — cheaper *and* a smaller trusted surface. `r3_namecmp_fn` is
  > **18.2 %** under the shipped R3. ⚠⚠ **THE SIGN OF THE BOUND REVERSES UNDER
  > SEARCH** — shipped, R3 is cheaper; cheapest-found each side, R4 is cheaper
  > by 3.5 %. ▶ **So this row is NOT `ph16`'s F67 mechanism: F67 STAYS n = 1.**
  > **Manager-verified from `results-php/gate/` and `controls/spellings.json`,
  > with both brackets re-run independently at `66/0` and `14/0`.**
  >
  > ⭐⭐⭐ **AND `get_unchecked` IS THE EXPENSIVE SPELLING ON THIS ROW.** The
  > mirror control is the winner's shape exactly — same signature, same hoist,
  > same attribute, same 12 trusted sites — with the arena reads left
  > **unchecked**, and it is **44 pp DEARER**. ⚠ **The conclusion is landed and
  > the MECHANISM is marked OPEN**, after the engineer re-read its own prose and
  > found it had stated a story as fact. **That is the strongest form of *"the
  > safety check can be negative-cost"* in either programme.**
  >
  > ⚠⚠ **AND A1 IS BLIND ON THIS ROW: spread `0.000000` pp across all NINE
  > searched variants, against 66.7 pp (R3) and 44.5 pp (R4) whole-program.**
  > ▶ **A control pricing `ph45` in A1 alone writes `r4_endpoint_degenerate:
  > true` AND `r3_endpoint_degenerate: true`. Both are false.** ⭐ That is the
  > corrected two-condition rule earning its keep on the FIRST row it was
  > applied to — condition (i) catches it, while F74's **withdrawn**
  > one-condition form PASSES at `|Δinside_share| = 0.003` and would have
  > licensed A1.
  >
  > ⚠⚠⚠ **THE STATISTIC PICTURE, AND IT IS NOT SETTLED.** F83: F74's "null" was
  > **measuring real work** — family C reproduces B's `+266.000` as `+265.924`
  > on `ph03/small` by an independent method, so **B's defect is ATTRIBUTION,
  > not noise, and a confound does not shrink with measurement.** F84: B and C
  > agree on 6 of 12 R4/R5 cells and **B can MISS real work as well as invent
  > it.** F86: the A/B disagreement has **three** classes — agree 314, **FLIP
  > 38**, **BLIND 14** (A exactly `0` against a nonzero effect) — and the exact
  > flip test **needs both ratios**, so ⭐⭐⭐ **NO FUNCTION OF THE SHARES CAN
  > CERTIFY A AT ANY THRESHOLD. There is no shortcut: PUBLISH BOTH, LABELLED,
  > ALWAYS.**
  >
  > ⚠⚠⚠ **F85 IS THE ONE THAT MATTERS: 29 of the 38 sign flips are
  > CROSS-LANGUAGE, and 28 OF THE 29 SURVIVE family C** — `ph03` 6/6, `ph07`
  > 6/6, `ph29` 16/16 survive, `ph00` 0/1 REFUTED (`TASK_PHP_038` §1.1, which
  > adjudicated all 29 and not the 12 the manager had). ⚠⚠ **THIS SENTENCE SAID
  > `28 of the 38` AND `UNREVIEWED`, AND BOTH WERE STALE while the paragraph
  > above beginning *"the cross-language flip count is 29, not 28"* ALREADY
  > RECORDED THE FIX** (cited by its text, not a line number, because the
  > numbers move) — **a correction landed as a new paragraph instead of applied
  > to the sentence it corrects, so this file stated both numbers at once and
  > THIS is the layer that outranks
  > `RECAP_PHP.md`.** ⛔⛔⛔ **REPAIRED 2026-09-13 (`TASK_PHP_049` §1.3): EVERY
  > NUMBER IN THE NEXT SENTENCE IS AGAINST `c-gcc`, AND THIS UNIT NEVER SAID SO
  > — the strings `c-gcc` and `c-clang` appeared NOWHERE in its 182 lines, in the
  > layer that outranks everything.** On **`ph29/large`, A1, `O3/isolated`**:
  > **A says `c-gcc` is +33.01 % dearer than naive safe Rust; B, C and W1 all say
  > ~1 % CHEAPER**, agreeing to ~2 pp. ⚠⚠ **AND THE SAME CELL AGAINST `c-clang`
  > IS NOT ~1 % ANYTHING: A `−4.36 %`, C `−27.78 %`, W1 `−27.61 %`.** ▶ ⛔ **SO
  > *"A disagrees with three other statistics"* IS A `c-gcc` STATEMENT, AND THE
  > ~2 pp AGREEMENT AMONG B/C/W1 IS TOO.** ⭐ **The disagreement is REAL and the
  > swap does not rescue A** — against `c-clang` it shrinks from 34.07 to 23.42 pp
  > and **gains a sign flip on `small.bin` that gcc did not have.** **That is the
  > difference between *"safe Rust is a third cheaper than C here"* and *"they are
  > the same"* — this programme's central claim, and it owes its baseline in the
  > same breath, every time.** ⚠ `ph07` and `ph03` are **B-only** so far (item 64).
  > ⭐ **It generalises open item 54 rather than repeating it: it is not one row.**
  >
  > ⚠ **Four corrections to the manager's own published work this round:** F74's
  > mechanism (F83), its generalisation (F84), F82's percentages published
  > **unlabelled** per input (`_037` §9.3 — `check.py`'s own *DO NOT MAX IT OVER
  > INPUT* warning landing inside the finding that quotes it), and a scalar
  > restatement of the flip rule **refuted 30 of 346**. ▶ **Not one was
  > arithmetic. Every one came from a second method on something published from
  > one probe or two rows.**

  ▶ **`ph03`, `ph64` AND `ph45` REMAIN UNDISCHARGED and need their own task.**
  **3 of 6 built rows are unbounded in both directions** — ⚠ this line said
  **3 of 4** until `TASK_PHP_028` reported, then **2 of 4**, `ph64` took it back
  up to **3 of 5**, `TASK_PHP_035` brought it to **2 of 5**, and `ph45` takes it
  to **3 of 6** — ⭐ **count it, do not trust this line**; it has moved five
  times. It remains the largest standing threat to the programme's headline
  quantity. ⚠ **`ph29` was BLOCKED on open item 51 and is no longer**; both
  halves are done. **`ph03` (`spellings: 11`) and `ph64` (`spellings: 13`, 6
  forbidden) are searchable today, and `ph45` has no `spellings.py` at all** —
  which makes it the **cheapest of the three**, since there is no declaration
  repair to do first (open item 58).

---

## Landed 2026-09-13 from `TASK_PHP_043` — the pin, and the endpoint search

- ⭐⭐⭐ **AN `idiom.required` ENTRY'S BACKTICKED SPAN PINS THE *REPRESENTATION*,
  AND ITS ENGLISH DECIDES WHICH RUNGS IT SCOPES TO — BUT THE PRESENCE REPORT
  DECIDES NOTHING.** `ph53`'s `required[4]` reads `` `wrote[i]` `` — *"THE
  ONE-BYTE-PER-SLOT WITNESS"* — and a `u32` bitmask that discharges the identical
  obligation **more cheaply and with a smaller trusted surface** is **OUT OF
  CONTRACT**, because the named-spelling standard resolves exactly that case:
  *"a rung that establishes the same fact by a different expression is out of
  contract even when it is semantically identical and even when it compiles to
  the same bytes."* ▶ **So `r4_endpoint_degenerate` is TRUE on that row and
  F100's *"both endpoints move"* keeps only its R3 half.**
  ⛔⛔ **AND THE WAY *NOT* TO REACH THAT ANSWER, because the manager tried it:**
  the `why`'s *"WHAT NO GREP SETTLES"* sentence does **not** license reading every
  backticked `required` span as a spelling pin. **Its own final clause says
  *"which spelling … is a reading"*, and `harness/check.py::idiom_audit`
  (`check.py:2198-2212`) measures the naive every-span-in-every-rung reading at
  **41 misses of 158 obligations, all 41 non-defects, 17 of them ANTI-signal**
  (a `required` entry may quote a span **in order to say it is ABSENT**).
  ⭐ **`required` is PRESENCE-ONLY, cannot fail the gate, and is judged against
  the entry's English by a reader. `required_absent` is a raw presence report
  that fires on shipped rungs too** — on `ph53` it fires on R3's `v0_shipped`.
  ▶ **Read the entry, not the report.** (F100 narrowed, item 83 closed.)

- ⚠⚠ **WHAT DECIDED IT WAS THE ENTRY'S *LEADING APPOSITIVE*, SO WRITE THAT
  CLAUSE DELIBERATELY.** *"THE ONE-BYTE-PER-SLOT WITNESS"* defines **what the
  backticked span IS** — a representation — and the challenger was declared *"a
  u32 bitmask **instead of `[bool; MAXD]`**"*, one bit per slot; a further clause,
  *"It is **indexed** SAFELY on purpose"*, also fails on a bitmask, which performs
  no indexed access. ▶ **English 2-to-1 against the challenger, AGREEING with the
  backticks — so there was never a spelling-versus-purpose conflict**, and the
  claim that there was is what made the question look undecidable for two tasks.
  ⭐ **When you write a `required` entry, the appositive is the pin's definition;
  everything after it is commentary.**

- ⭐ **A COST-SELECTION TRAP THE RULING AVOIDS, AND IT IS WHY THE RULING IS
  CREDIBLE.** `.memory/02-bench-rules.md`'s *a rung is never cost-selected*
  applies to its **pins** too. The reading that won is the one under which the
  **cheaper** variants LOSE — ▶ **so the row's headline was retracted in the
  direction that costs it something**, which is the only direction in which a
  pin ruling can be trusted.

- ⭐⭐ **A WITNESS-REPRESENTATION CHANGE THAT IS CHEAPER *AND* SMALLER-SURFACE
  CAN BE OUT OF CONTRACT, AND THAT IS A PUBLISHABLE RESULT RATHER THAN A
  PROBLEM.** `ph53`'s `r4_bitmask_min` is **3 trusted call sites against the
  shipped rung's 10 and 2 accessors against 4**, and it is out of contract.
  ▶ **Publish it as a CONTROL-class result**: *"a cheaper, smaller-surface
  witness exists and this row's contract excludes it"* — which says more than an
  endpoint would. ⚠ **And the four reductions that KEEP the shipped witness are
  all dearer** (+0.50 / +2.99 / +3.03 / +6.60 %), **so *"a smaller trusted
  surface costs something"* is not a law — it is what you measure when you change
  ONE thing.**

- ⚠ **AN ENDPOINT SEARCH STILL PAYS, AND THE SCORE IS NOW 3 OF 4 ROWS WITH A
  MOVING ENDPOINT** — `ph29`'s R4 (byte-identically, F77), `ph45`'s R4 **and** R3
  with the bound's sign reversing (F87), and `ph53`'s **R3 only** (F100, after
  review). ⛔ **`ph07` and `ph16` found their R4 degenerate, and that is on
  file.** ▶ **Search both endpoints on every row; do not manufacture a variant to
  have something to report.**


> ✅✅ **CYCLE CLOSED 2026-09-13 BY `TASK_PHP_047` — THE BANNER BELOW IS KEPT AS A
> RECORD, AND THE MATERIAL IS NOW REVIEWED, WITH ONE CLAUSE REFUTED AND REPAIRED
> IN PLACE.**
>
> | finding | verdict | what it cost this file |
> |---|---|---|
> | **F105** | ⛔ **REFUTED in part** | the `97.6 % attributed` clause is **gone** — it was two errors cancelling on one input. ✅ The `0.82 %` is **UPHELD and grows to `1.02 %`** |
> | **F106** | ✅ **UPHELD, and UNDER-STATED** | the relocation objection is adjudicated in `.memory/04-verus.md`; see the `tcb_items` entry below |
> | **F97 · F102 · F104** | ⚠ **UPHELD-NARROWED** | narrowings applied where they touch this file |
> | **F103** | ⛔ **REFUTED** (the decomposition) | ⓘ **never in this layer** — it lives in `RECAP_PHP.md` only, so it cost a RECAP edit and no removal here |
> | **F96** | ⛔ **still UNREVIEWED** | not in this file |
>
> ⚠⚠ **THE BANNER THIS REPLACES IS WORTH KEEPING IN SUBSTANCE, BECAUSE THE DEFECT
> IT RECORDS WAS MINE.** I wrote the RULE-9 STATE block one day before landing
> `04-process.md` law 12 (*a manager finding from one probe or two rows should be
> assumed narrowable until a reviewer has had it*) — **and then put seven
> unreviewed entries into the layer that supersedes everything.** ▶ **Caught by
> auditing before a handoff, which is the only reason it was marked at all.**
> ⭐⭐ **AND LAW 12 HELD AGAIN: of the five findings in this file's unreviewed
> block, ONE was refuted outright, ONE lost its headline clause, and THREE were
> narrowed. Not one survived unchanged.**

- ⛔⛔⛔ **A BACKTICK IN AN `idiom.required` / `forbidden` ENTRY *IS* A PIN,
  INCLUDING AROUND A FILENAME, A TYPE NAME OR A FIELD NAME — SO ANY DRAFT OF
  THAT PROSE GOES THROUGH `idiom_audit` BEFORE IT LANDS.** `harness/check.py::spelling_matches`
  matches every backticked span against every rung of the entry's language, so
  a span quoted merely to *refer* to something becomes a declared obligation.
  **Two failure modes, both measured:** a span that matches **every** rung is a
  pin that cannot discriminate — the **ANTI-signal** class `idiom_audit` counts
  at **17 of 41** — and a span that matches **none** is a `pins nothing` entry.
  ⭐⭐ **THE INSTANCE IS THE STRONGEST POSSIBLE ONE: the review that established
  *"a backticked span pins the representation"* then drafted three spans it did
  not mean to pin — `` `u32` `` (matches every rung), `` `controls/spellings.json` ``
  and `` `required_absent` `` (match none) — inside the very sentence
  establishing the rule.** ⭐ **And the engineer applying it caught one of its own
  the same way: a meta-sentence saying *"ONLY `x` AND `y` ARE BACKTICKED HERE"*
  re-backticked and duplicated both.** ▶ **Neither was found by reasoning. Both
  were found by running `controls/spellings.py --audit-only` and READING THE
  OUTPUT.** ⓘ The convention was already on file — `p42`'s `required[1]`:
  *"quoting a file name or a retracted span would pin it too"*. **It is the
  checking step that was missing, not the rule.** (`TASK_PHP_044` §2, item 100.)

- ⚠⚠ **ADMISSION NEEDS **BOTH** FIELDS: `in_contract` AND `english_verdict`.
  READING EITHER ALONE GIVES THE WRONG ANSWER.** A `spellings.py` variant is
  admissible only if `forbidden_hits` is empty **and** no `english_verdict`
  excludes it. ⭐ **`_043` read `in_contract: true` on `r3_no_capacity` and
  concluded it was admitted; it had already been excluded on a different entry's
  `english_verdict`** — so the repair it asked for was already in place.
  ⭐⭐ **That is the same class as `_043`'s own ruling — that `required_absent`
  is not self-interpreting — committed while establishing it**, and it is why
  `02-ladder`'s pin rule above says *read the entry, not the report*: here, read
  **both** fields, not one. (`TASK_PHP_044` §4, item 90.)

- ⭐⭐⭐ **A *SAFE* RESPELLING CAN BEAT THE SAME RUNG WITH EVERY BOUNDS CHECK
  REMOVED — SO `get_unchecked` IS NOT A CEILING ON THE SAFE SIDE.** Measured on
  `ph52`: `ctl_r3_unchecked` (the shipped R3 with `win.get_unchecked` everywhere) is
  **`−6.66 %`** while the safe `r3_chunks_exact` is **`−7.42 %`** — **the safe
  spelling wins by `0.82 %`**, because `get_unchecked` deletes the checks and
  **leaves the offset arithmetic**, where the safe respelling deletes both.
  ⛔ **So a control built as *"the ceiling of the R3 search"* bounds nothing**, and
  the task that built it retracted the claim in its own sidecar under
  `ctl_r3_unchecked_is_not_an_upper_bound`. ✅ **It is still the right CONTROL** —
  it isolates the bounds-check term *at the shipped spelling*, which is what makes
  that row's bounds-check attribution checkable — **and the check REFUTED the
  `128.00` of `131.19` framing** (see the next bullet) — **but it is not a
  bound.** ⭐ **The `0.82 %` itself is REVIEWED AND UPHELD, and it GROWS to
  `1.02 %` on `large.bin`, ~14 000× the noise floor.** (F105, `TASK_PHP_046` §3.3;
  reviewed `TASK_PHP_047` §2.4.)

- ⚠⚠ **THE R3−R4 GAP IS SOMETIMES A SPELLING AND SOMETIMES A MECHANISM, SO THE
  QUESTION IS WORTH ASKING ON EVERY ROW.** `ph53`: **mechanism** — nine window
  bounds checks at `281.8 Ir/call`, larger than the whole R3−R4 gap, and the
  prediction's spelling *was* what shipped. `ph52`: **spelling** — four per-op
  window bounds checks, measured directly by the row's own `ctl_r3_unchecked`
  control at **138.86 Ir/call on `small.bin`** and **354.47 on `large.bin`**: a
  two-input slope of **7.99 instructions per op against a predicted 8**, plus a
  fixed **`+11.1 Ir/call`** the model omits. ⚠⚠ **That term is 105.8 % / 105.6 %
  of the R3−R4 gap it is offered to explain**, because R4 carries an
  opposite-signed second term — the R3 rung with its window checks removed is
  **cheaper than the shipped R4** on both inputs. ⛔⛔ **DO NOT QUOTE
  `128.00 of 131.19 = 97.6 %`: that ratio is TWO ERRORS CANCELLING on `small.bin`,
  and on `large.bin` the same construction gives `102.4 %` with the residual
  CHANGING SIGN** (`TASK_PHP_047` §2.1–2.3 refuted it; ⭐ **the slope is what
  survives, and a slope needs two inputs, which is why one input could not see
  the error**). ⭐ **Both rows' answers corrected the row's own prose**
  — `ph52`'s §8c/§10 had framed its gap as `Option` vs `MaybeUninit`+witness.
  ▶ **Name the term and attribute a percentage of the gap to it, or the answer is
  an adjective.** (F100, F105.)

- ⭐⭐ **SEARCH REVERSES THE `fixed-R4 bound`'s ORDERING ON 2 OF 4 ROWS SEARCHED
  (`n = 2`, NOT AN ANECDOTE).** `ph45` (F87) and `ph52` (F105): published, R3 is
  dearer than R4; cheapest in-contract R3, R3 is **cheaper**. ⛔ **ORDERING, NEVER AN
  INTERVAL** — the shared `why` forbids publishing a pair interval and neither row
  computes one. ▶ **So a row that publishes the bound without a search publishes an
  ordering that a search can flip**, which is the argument for the search being part
  of a row rather than an optional extra. ⓘ Score so far: `ph29` R4 moved, `ph45`
  both moved, `ph53` R3 moved, `ph52` R3 moved; **`ph07`, `ph16` and now `ph52`'s R4
  are degenerate and that is on file too.**

- ⭐⭐⭐ **THE PUBLISHED TRUSTED-SURFACE AXIS IS THE GATE'S OWN `tcb_items`, IT
  DELIBERATELY DOES NOT COUNT `vstd`, AND THAT IS A MEASURED DECISION RATHER THAN
  AN OVERSIGHT — SO "REMOVING A WRAPPER JUST RELOCATES THE AXIOM INTO vstd" IS
  ALREADY ADJUDICATED AND THE ANSWER IS NO.** `.memory/04-verus.md`: *"what ships
  instead: one headline number — the gate's own `tcb_items`"*, reported as
  **`TCB: N lines across M items`**, counted over `verus.rs` only. ⛔ **Two richer
  proposals were built and REJECTED**: a second column for *"vstd assumed
  specifications relied upon"* (**refuted with a census — the pinned vstd holds
  402 `assume_specification` sites, 272 `external_body` items and 545 `broadcast`
  proof fns; *"relied upon"* is undecidable from the text, and every rung depends
  on the same vstd core so the column would not discriminate**) and a `tcb_reach`
  classification (`safe`/`local-external-body`/`vstd-axiom`), rejected at
  `TASK_055_REVIEW` for the same undecidability. ⭐⭐ **AND THE PRECEDENT IS
  EXACT**: `p06` deleted a hand-written `external_body` wrapper because the pinned
  vstd already specified the operation (`copy_from_slice`), shipping
  **`18 verified, 0 errors` at BYTE-IDENTICAL `-O3` machine code, TCB 6 → 5** —
  and the project counted that as a reduction and published it. ▶ **So deleting a
  hand-written wrapper whose contract the pinned vstd already proves is a STRICT
  REDUCTION, not a relocation.** ⭐ **The machine proof, not the argument, is what
  settles it**: `ph52`'s `r4_no_wrapper` verifies **34/0 with its contract
  textually unchanged**, so the hand-written axiom was a **theorem**, and deleting
  a theorem that was being asserted as an axiom takes something real out.
  ⚠⚠ **QUOTE IT AS *"a reduction on the published `tcb_items` axis"*, NEVER as
  *"a reduction in the trusted base"* full stop** — `unsafe_tokens` (2) and
  `trusted_call_sites` (11) do **not** move on that variant, and
  `.memory/04-verus.md` marks the accounting rule itself **PROVISIONAL**.
  (F106; ruled `TASK_PHP_047` §1.3–1.4, which found the adjudication the manager
  had not cited.)
