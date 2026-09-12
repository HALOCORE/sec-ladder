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
> The narrative, the open items and findings **F1–F48** live in `RECAP_PHP.md`
> (⚠ this said *F1–F41* for seven findings — `PROTOCOL.md` rule 13, headers rot;
> count it with `grep -c '^### F' RECAP_PHP.md` rather than trusting the line).

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

| `safe_naive` | `safe_tuned` | `unsafe` | `verus` | `c-gcc-h` (real 2004 fix) |
|---:|---:|---:|---:|---:|
| **+26.8 %** | **+3.7 %** | **−7.6 %** | **−7.6 %** | **−0.4 %** |

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
