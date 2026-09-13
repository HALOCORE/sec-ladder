# TASK_PHP_043 — THE REVIEW ROUND: **14 unreviewed findings**, and **THREE OF THEM WOULD RETRACT SOMETHING PUBLISHED**

**Role:** research **reviewer**. **One agent, alone.**
**Report:** `.tasks-php/TASK_PHP_043_REPORT.md` — **write the FILE** (rule 10).

⚠⚠⚠ **YOUR JOB IS TO FALSIFY, NOT TO CONFIRM.** The two tasks in this programme
told to *try to break* a prior headline rather than build on it both succeeded:
`TASK_PHP_030` turned *"closes to the digit with no residue"* into an arithmetic
identity true of any input pair (F78), and **`TASK_PHP_038` refuted three
manager claims in one report** (F80/F82/F83/F84's corrections). **You are the
third, and you have the largest subject.**

⚠⚠ **AND THE SUBJECT IS LARGELY THE MANAGER'S OWN WORK, WHICH WAS WRONG EIGHT
TIMES IN THE LAST ROUND AND NOT ONCE ARITHMETICALLY**: F90 refuted by an
experiment written to be able to refute it; **two scoping errors in one probe,
the second being the one my own F82 exists to forbid**; F87 both
under-attributed and over-read; a truncated `ls` read as a deletion; `rule 11`
broken twice. ▶ **Every one was found by bringing a SECOND METHOD to something
published from one probe or two rows. Assume the same of what you review.**

---

## §0 ⛔⛔ READ THIS FIRST: THE STOP INSTRUCTION, BECAUSE THIS TASK IS DELIBERATELY BIGGER THAN ONE REPORT

**Fourteen findings are unreviewed** (F88–F101) and `TASK_PHP_038` took 840 lines
to review **five**. ⛔ **DO NOT TRY TO COVER FOURTEEN AT THAT DEPTH.**

▶ **WORK THE SECTIONS IN ORDER. WHEN YOUR DEPTH RUNS OUT, STOP AND SAY WHERE.**

⭐⭐ **A round that reviews 8 of 14 honestly and names the other 6 as UNREVIEWED
is worth strictly more than one that claims 14**, because the manager's next
move is routed off your coverage list and **a falsely-closed cycle lets a wrong
finding into `.memory-php/`, which is the one error this process exists to
prevent.** ⓘ **The manager will schedule `TASK_PHP_044` for the remainder; that
is expected, not a failure.** `UNTESTED` and `I could not tell` are **valued
answers** — `_039` shipped a negative's failure rather than hide it, `_040`
shipped a defect it could not fix, `_041` reported 15 uncertainties and found
its own citation defect. **All three were the right call.**

**Read**, in this order:
1. `RECAP_PHP.md` — the **RULE-9 STATE block** (it names your scope), then
   **F87, F88, F89, F90, F91, F92, F93, F94, F95, F96, F97, F98, F99, F100,
   F101**, then **open items 73, 75–83**. ⚠ F88 is narrowed in place and F90 is
   **struck**; read the corrections, not just the headings.
2. `.tasks-php/PROTOCOL_PHP.md` — **§H** (a validator change lands with its
   negatives), **§B1a**, **§C**, **§F5**, **§F6**, **§H1**.
3. `.tasks/PROTOCOL.md` — rules 6, **9**, 10, 11, 13, **14**. **Rule 9 is why
   this task exists.**
4. `.tasks-php/STATISTICS_001.md` — the statistic argument, committed.
5. The probes, **all present on this box and all `--selftest`-able**:
   `.temp/mgr17{0,2,3,4,5}/`, `.temp/php3{8,9}/`, `.temp/php4{0,1,2}/`.
   ⭐ **Run every `--selftest` you rely on and say so.** ⚠⚠ **`.temp/` is
   GITIGNORED — so a number you want to survive goes in YOUR REPORT, not behind
   a pointer** (that is F99's own defect; do not reproduce it).
6. The five committed checkers: `.tasks-php/{boxcheck,citecheck,coverage,quota,
   fixsurvey,preimage_screen,php_null,task_cost}.py`.

---

## §1 ⭐⭐⭐ PRIORITY 1 — ITEM 83: DOES `ph53`'s `required[4]` PIN A **SPELLING** OR A **PURPOSE**? IT DECIDES WHETHER HALF OF F100 SURVIVES

**Why this is first.** F100's headline is *"`ph53`'s **BOTH ENDPOINTS MOVE** —
2nd row in either programme"*. ⛔ **Under the spelling reading,
`r4_endpoint_degenerate` becomes `true`, the R4 half is withdrawn, and the
headline becomes *one* endpoint.** Nothing else in the backlog can retract a
headline with one ruling.

**The entry, in full, from `patterns-php/ph53-iface-tail-uninit/spec.md`'s
hashed block** (`idiom.required[4]`; extract it yourself with
`check.py::read_contract` rather than trusting this quote):

> `"rust": "`` `wrote[i]` `` -- THE ONE-BYTE-PER-SLOT WITNESS, present in
> unsafe.rs and verus.rs and in no other rung. IT IS NOT IN THE C AND IT IS NOT
> UPSTREAM: it is what makes R4's unsafe read dischargeable, and the row's
> Verus-side result is that a faithful witness-free R4 CANNOT BE VERIFIED at
> all … **It is indexed SAFELY on purpose**: reaching a rung's own safety
> witness with an unchecked access would make the witness rest on the thing it
> exists to establish."

**THREE readings are live. Rule on them, with the text.**

| | reading | consequence |
|---|---|---|
| **(a)** | **SPELLING.** The row's own hashed `why` carries the NAMED-SPELLING STANDARD **byte-identically in six patterns**: *"where a `required` entry quotes an expression in backticks it pins THAT SPELLING, not merely the property the expression has, so a rung that establishes the same fact by a different expression is out of contract **even when it is semantically identical and even when it compiles to the same bytes**"* | ⛔ `r4_bitmask` / `r4_bitmask_min` are **OUT OF CONTRACT**. **R4 endpoint DEGENERATE. F100's R4 half falls.** |
| **(b)** | **PURPOSE.** The English names a role — *"what makes R4's unsafe read dischargeable"* — and a `u32` bitmask discharges it (twins `31/0`, `32/0`) | ✅ both endpoints move; F100 stands as published |
| **(c)** | ⭐⭐ **THE ENTRY DOES NOT BELONG IN `idiom.required` AT ALL** — and **this is the manager's hypothesis, offered to be attacked, NOT a ruling.** `idiom.required` pins **the idiom extracted from the C**; this entry opens *"IT IS NOT IN THE C AND IT IS NOT UPSTREAM"* **in its own words**. An entry that pins a **Rust implementation choice** inside the hashed contract is rung selection **by declaration** | the repair is **MOVE IT**, not restate it — and then **every** row's `required` owes the same audit |

⭐ **FOUR PIECES OF EVIDENCE YOU ARE BEING HANDED, BECAUSE THE MANAGER MEASURED
THEM AND A PREMISE IN A TASK FILE IS ONE YOU HAVE NO REASON TO DOUBT (rule 14):**

1. ⭐⭐ **The row's own `why` ALREADY SEPARATES SCOPE FROM SPELLING**, in terms:
   *"the POLARITY of a quoted span … and the SET OF RUNGS it scopes to live in
   the entry's English. `spelling_matches` decides one spelling against one
   rung; **which spelling and which rung is a reading, and no gate stage
   reproduces it**."* ▶ **If English decides SCOPE and backticks decide
   SPELLING, reading (a) follows directly** — `required[4]`'s English scopes it
   to `unsafe.rs`/`verus.rs`, and within that scope the backticks bind.
   ⚠ **Check whether that is really what the sentence licenses, or whether the
   manager is over-reading a sentence about polarity.**
2. ⛔⛔ **`controls/spellings.json`'s OWN STATED INVARIANT IS VIOLATED BY ITS OWN
   RECORDED OUTPUT.** The `invariant` field opens *"Every variant is in contract
   by `harness/check.py::spelling_matches` over **EVERY** backticked idiom
   entry"* — and `r4_bitmask`, `r4_bitmask_pool`, `r4_bitmask_min` and
   `ctl_nowitness` each record `required_absent: ["required[4] \`wrote[i]\`"]`.
   ▶ **Either the invariant is false as written, or those variants are not in
   contract. Say which.**
3. ⚠⚠ **AND THE SIGNAL IS NOT UNIFORMLY DISCRIMINATING, WHICH IS THE COUNTER TO
   (2).** The **R3-side `v0_shipped` — the SHIPPED RUNG — also records four
   `required_absent` entries**, including `required[4]`, and every one of those
   absences is **correct**, because those pins' English scopes them to other
   rungs. ▶ **So `required_absent` is a RAW PRESENCE REPORT WITH NO SCOPING and
   it fires on the shipped rung.** ⭐ **But the R4-side `v0_shipped` records
   NONE** — so *within the R4 side* the signal does discriminate shipped from
   bitmask. **Is that a real contract distinction or an artefact of which pins
   happen to be R4-scoped? Settle it, and check the same field on `ph45`,
   `ph29`, `ph07`, `ph16`.**
4. **`idiom.required` is presence-only and CANNOT FAIL THE GATE**, so nothing
   mechanical was ever going to decide this, and `required_absent` correctly
   *reported* the absence on both winners.

⛔⛔ **TWO THINGS YOU MAY NOT DO.**
* **Do NOT resolve it by weakening the pin to match whichever variant won** —
  `.memory/02-bench-rules.md`'s *a rung is never cost-selected* applies to its
  pins too. ⚠ **The bitmask variants being cheaper is NOT an argument for
  reading (b).**
* **Do NOT EDIT THE ROW.** `spec.md` is in `source_sha256`, so the repair costs
  a `ph53` re-gate and that is an engineer's task. ▶ **Your deliverable is the
  RULING plus the EXACT REPLACEMENT SENTENCE, drafted**, so the manager can
  route one re-gate.

---

## §2 ⭐⭐ PRIORITY 2 — ITEM 82: WHERE WAS `ph45`'s `0.000000` pp OVER-READ, AND DOES F91 DEPEND ON IT?

**The two facts, from `controls/spellings.json` (manager-measured, re-measure
them):** `ph45` `a1_spread_pp = {R3: 0.0, R4: 0.0}` against
`wp_spread_pp = {R3: 66.730637, R4: 44.454781}` over **9** variants; `ph53`
`a1_spread_pp = {R3: 39.899657, R4: 45.313019}` against
`wp_spread_pp = {R3: 67.930558, R4: 39.543977}` over **20**.
**Two rows, two opposite answers, same statistic.**

⚠⚠ **THE MANAGER'S CENSUS OF WHERE THE CLAIM IS PUBLISHED DISAGREES WITH ITEM
82's OWN WORDING, AND YOU ARE BEING TOLD SO RATHER THAN LEFT TO FIND IT.** Item
82 says *"F87 published a row fact as a statistic fact"*. I grepped for it:

| site | wording | scoped correctly? |
|---|---|---|
| `patterns-php/ph45-htmlent-cache-int/NOTES.md:612` | *"**A1 CANNOT RESOLVE THIS ROW AT ALL** … Its spread over a side is `0.000000` pp"*, with the mechanism (*"every lever the search found lives in `dec`, which A1 excludes"*, `inside_share` 0.055–0.094) | ⭐ **YES — the row document is the most careful of the three** |
| `.tasks-php/TASK_PHP_037_REPORT.md:30` | *"A1's spread over all nine variants is `0.000000` pp on both sides"* | **YES — "over all nine variants"** |
| **F87's body in `RECAP_PHP.md`** | ⚠ **the manager found NO A1-spread claim in it at all** — F87's table publishes **W1** | — |
| **F91's evidence table** (`RECAP_PHP.md:2465`) | *"A ⛔ blind to callees … spread `0.000000` pp over 9 variants"* | ⛔ **NO — and the manager has ALREADY WITHDRAWN this clause in place** |

▶ ⭐ **SO YOUR JOB HERE IS NOT THE RESTATEMENT — IT IS THESE FOUR QUESTIONS:**

1. ⚠ **Is item 82's attribution to F87 simply WRONG?** If the over-read lived
   only in F91's table and `RECAP_PHP.md`'s statistic row — both already
   amended — then **item 82 is closeable now** and a row re-gate is NOT owed.
   ⛔ **Check `results-php/`, `.memory-php/`, every row's `NOTES.md` and
   `README.md`, and the other `spellings.json` files before concluding that.**
2. ⭐⭐ **IS `ph45`'s `0.000000` THE SAME PHENOMENON AS F86's `BLIND` CLASS?**
   F86 defines **BLIND** = *"A is exactly `0` while the whole-program figure is
   not"* and counts **14 of 366**. ▶ **If yes, the programme ALREADY HAD THE
   CONCEPT and F91 failed to use it** — which is a better finding than the
   restatement, and it tells you the right *name* for the repaired sentence.
3. **Does F91's `|B/A|` = 49.6–393.9× regime claim depend on the wrong reading?**
   The manager's position is **no — it is measured on the R4/R5 pair's
   `Δnopad`, not on respellings.** ⚠⚠ **VERIFY IT; DO NOT INHERIT IT.** This
   exact shape of assumption is what F82 got wrong.
4. ⭐ **What is the RIGHT general statement?** Candidate: *A1 resolves a code
   difference exactly to the extent the difference lands inside the kernel
   symbol* — which makes `ph45` (levers in `dec`, `inside_share` < 0.1) and
   `ph53` (levers in `kernel`) **two instances of one rule rather than a
   contradiction.** ▶ **If that is right, say so and give the predicate a row
   can be tested against BEFORE its search runs.** ⚠ **A magnitude floor with
   every sign claim** — an outlier test in this programme once fired at
   `0.00 pp`.

---

## §3 ⭐⭐ PRIORITY 3 — ITEM 78: IS F91's AXIS A **PROXY**? AND THE CHEAP ROUTE NOBODY HAS TAKEN

**F91's published axis:** *same-language* differences are 1–2 instructions under
50–394× of callee noise so only **A** resolves them; *cross-language* the callee
work **IS** the effect, so a callee-inclusive statistic is right.
**The rival:** the real axis is ***does the callee work diverge***, and language
is merely **correlated** with it. **`ph53`'s evidence for the rival:** A and B
agree in sign and closely in magnitude on **every cross-language cell** of that
row, and the stated reason is that **§B1a's O(1)-allocation precondition HOLDS**
there, so there is no allocator term for B to include and A to miss.

▶ **THE 2×2 IS THE RIGHT FRAME, AND ONLY ONE CELL IS MISSING:**

| | **callee work diverges** | **callee work does not** |
|---|---|---|
| **cross-language** | F85/F91's 28 flips (C allocates, Rust does not) | ⭐ **`ph53` — A and B AGREE.** Rival predicted it; axis did not |
| **same-language** | ⛔⛔ **THE MISSING CELL. GET IT.** | F91's 1–2-instruction regime, `|B/A|` 49.6–394× |

⭐⭐⭐ **AND THERE IS A ZERO-MEASUREMENT ROUTE TO THE MISSING CELL THAT THE
MANAGER BELIEVES NOBODY HAS TAKEN — CHECK IT FIRST, BECAUSE IT WOULD MAKE THIS
ITEM FREE.** F85/F86 report **38 flips over 366 comparisons, of which 28 are
cross-language**. ▶ **That leaves 10 SAME-LANGUAGE FLIPS ALREADY ON DISK.** A
flip *is* a sign disagreement between A and the whole-program figure, so **10
same-language comparisons where A and whole-program disagree is exactly the
missing cell.** ▶ **Pull those 10 out** (`.temp/php38/flip_columns.py`,
`.temp/mgr172/flip_exact.py` — ⭐ **and note F86's own warning that its first
version scored `BLIND` as `FLIP`, inflating 38 to 52; make sure you are reading
the corrected classifier**) and ask, of each: **does the callee work diverge in
that pair?** ⓘ The obvious same-language candidates are **R1 vs R1h** (upstream
fixes that add work: `ph53`'s R1h adds an O(n) `memset`) and **R2 vs R3**.

⚠ **THE FALLBACK, IF THOSE 10 DO NOT SETTLE IT, AND ITS COST:** the designed
test is **`ph53`'s `c-gcc` vs `c-gcc-h`** — same language, and R1h adds
`memset(ce->interfaces, 0, 8*n)`. **A already moves**: `kernel_exclusive_ir` on
`small.bin/isolated` goes `38 639 348 → 38 780 174` at `-O0` (**+0.36 %**,
manager-read from `results-php/ph53-iface-tail-uninit.json`; every cell's
`kernel_functions` is the single symbol, so **the `memset` body is outside A by
construction if it is a call**). ▶ **So the question is whether the
whole-program Δ is much LARGER than A's Δ, and at `-O0` vs `-O3` separately,
because the memset may be inlined at `-O3` and then there is no callee at all.**
⚠⚠ **W1 for `ph53` is NOT in `results-php/` and the `mgr172`/`php38` callgrind
sets PREDATE this row** — so this route **costs callgrind runs**. ⭐ **Take the
free route first and only pay if you must; and if you pay, say what you spent.**

⭐ **IF THE RIVAL HOLDS, item 62 (family C) gets narrower and cheaper** — the
condition becomes **measurable per row** instead of declared per comparison —
and the manager will not dispatch family C until you have answered.
⚠⚠ **`ph53` is ONE row and F96 says so in those words. Do not settle a
programme-wide axis on it.**

---

## §4 ⚠⚠ PRIORITY 4 — THE THREE LOAD-BEARING REMAINDER, AND **WHY THESE THREE**

Each of these is **already being depended on by the next task the manager will
dispatch**, so a defect here is a defect in row 8.

| | finding | the dependency, and the attack |
|---|---|---|
| **4.1** | **F94** — `ph53`'s R1h: the catalogue's SHA **refuted**, the real one found, and the fix converts a wild deref into a **NULL** deref | ⛔ **Row 8 (`ph52`) is queued on the words *"R1h settled (F94)"*.** ▶ **Re-derive the exclusion of `be8daf1f47fa` BY BOTH ROUTES INDEPENDENTLY** — `preimage_screen.py`'s `NOT-THE-REPAIR` label **and** the tag walk — and check they are not the same evidence twice. ⚠⚠ **The manager's own tag-walk read looked contradictory (2 occurrences at php-5.0.4, 1 at php-5.0.5) and resolved only on finding TWO DISTINCT `erealloc(ce->interfaces` SITES**, the survivor being the inheritance-merge line at `:1945`. ▶ **A count-based check that cannot disambiguate sites is unsound; does `preimage_screen.py` disambiguate?** |
| **4.2** | **F95** — the pre-image screen's **43 exclusions are 25**, and its soundness test was **promoting an exclusion to a proof** | **Every future row's fix hunt runs through this screen, starting with `ph52`.** ▶ `preimage_screen.py` is committed with negatives incl. **N10e, N11** and item D11's `INAPPLICABLE-SAME-FILE`. **Run the suite; then try to make a must-fire negative NOT fire.** ⚠ **N10e was a hardcoded `26/17` that went stale and is now computed — check the computation is not circular** (it must not derive its expectation from the same call it is testing). ⚠ **And audit the manager's `same_function` soundness guard** (*the matched hunk must contain no function-definition header before its first changed line*): **is that sufficient, or only necessary?** |
| **4.3** | **F92** — item 68 answers **NO**: the width→spread exponent is **≈ −0.5** on both rows, so widening `probe_iters` is hopeless | ⛔ **This killed a lever and REFUTED F90**, and `STATISTICS_001.md` §5 now publishes `NO`. **If F92 is wrong, the whole statistic decision reopens.** ▶ `.temp/php39/width.py --selftest`. ⭐ **The strongest attack is its F52 CONTROL**: it recovers `−0.5047` from i.i.d. noise and `−0.9799` from endpoint noise. **An exponent of `−0.5` is EXACTLY what i.i.d. sampling gives, so the measurement may be detecting its own null.** ▶ **Does the experiment DISTINGUISH "the lever is weak" from "the lever is absent and we are measuring sampling noise"?** ⚠ **And check the design's own guards held**: fixed `K=8`, fixed n-range, **disjoint** spans, **SD not range**. |

---

## §5 THE BOUNDED PASS — **F88 F89 F90 F93 F96 F97 F98 F99 F101**

**Only if §§1–4 are done.** ⛔ **Do NOT skip §§1–4 to get coverage here.**

**The bar per finding, and it is deliberately low:** **(i)** re-derive the
headline NUMBER from an artefact you name, or write **UNTESTED**; **(ii)** one
sentence on whether the CLAIM is scoped to what was measured; **(iii)** a
verdict of **UPHELD / UPHELD-NARROWED / REFUTED / UNREVIEWED**.

⭐ **Three of these have a specific cheap attack, so take them first:**

* **F101 / item 81 — `kernel_fingerprint`'s digest is PATH-SENSITIVE.** ⚠⚠ **The
  DIRECTION matters and the manager has not checked it.** Path-sensitivity makes
  byte-identical things read *different* — a **false negative** on identity. ▶
  **So does it threaten F77's headline (*"`r4_fold_iter` verifies
  BYTE-IDENTICALLY and is 5.63 pp cheaper"*) or not?** If `ph29`'s comparison
  ran both sides in one directory the defect is **latent there too**, and item
  81's *"LIVE on `ph29`"* would be **too strong**. ⛔ **Do not edit `ph29`.**
* **F98 — the verifying rung carries a coverage witness the C does not, at
  `+21.8 %`.** ⚠ **Which input is that percentage on, and which statistic?**
  (`check.py`'s own *DO NOT MAX IT OVER INPUT* has caught the manager.) ▶ **And
  is `+21.8 %` the witness's cost, or the cost of the witness PLUS everything
  else that differs between the two programs?** A difference attributed to one
  named cause is the shape F83 corrected.
* **F99 — 9 hashed `.temp/` citations, 6 of 8 rows, 3 already gone.** ▶
  `citecheck.py` is committed with negatives **N1, N1b, N1c, N2, N3, N4**. **Run
  it. Then check its `inherited = set.intersection(*per_spec.values())`
  separation is sound when a row is ADDED** — an intersection over per-row sets
  shrinks as rows arrive, so **a citation can silently reclassify from
  inherited to row-specific with no edit to any row.** Is that handled?

**F88 · F89 · F90 · F93 · F96** — bar (i)–(iii) only. ⓘ **F90 is already
REFUTED**; your job on it is to confirm the struck record states the refutation
correctly and **does not still read as live anywhere else**.

---

## §6 ⛔ Scope, brackets, traps

⚠⚠ **`RECAP_PHP.md` and `.memory-php/` ARE MANAGER-ONLY FOR WRITING.**
⚠⚠⚠ **NO EDITS under `harness/`, `common/`, `common-php/`, `patterns/`,
`patterns-php/`, `results/`, `results-php/`, or `pilot/`.** ⭐ **This task
measures and argues; it edits nothing that is hashed.** Scratch under
`.temp/php43/`. ⚠ **No `git add` / `git commit`.** Never touch `.web/`.

**Bracket**: `harness/measure.py --check-stale` → **`66/0`** and
`harness-php/gate.py --tool measure --check-stale` → **`16/0`**, **first and
last.** **Both verified by the manager immediately before writing this.**
⚠⚠ **Nothing in your scope can move either. If one moves, you have staled a
measurement — stop and report.**

1. ⚠⚠⚠ **`grep -a` ALWAYS** (F35): 41 corpus files exit 1 silently under plain
   `grep`, and a probe script does **not** reproduce it. ⭐ **AND a line-based
   grep cannot find a prose phrase that WRAPS** — that error has been made
   twice in this programme, once by the manager asserting an absence.
2. ⛔ **Never publish a percentage without saying WHICH INPUT and WHICH
   STATISTIC.** Four families are in use and three are published.
3. ⚠ **A magnitude floor with every sign claim.**
4. ⚠ **`timeout <N> <cmd>`**; never `pkill`/`killall`/substring match; no
   `until … sleep` poller loops.
5. ⚠ **A truncated `ls`/`head` is not evidence of absence.** The manager read
   `ls … | head -30` as a deletion last round; the files were there all along.
6. ⓘ **`verus_checked` and `problems` are NOT gate-record fields** — absent from
   all 8 php gate records. They live in `controls/spellings.json`; `problems` is
   also a **preflight** field. **Name the file any field came from** (F99).

---

## §7 Definition of done

1. ⭐ **A RULING ON ITEM 83**, against the three readings, with the text that
   decides it — **plus the exact replacement sentence drafted** for whoever
   lands the re-gate. ⚠ **If you cannot rule, say which evidence would.**
2. **Item 82: the census checked, and a verdict on whether it is CLOSEABLE
   WITHOUT A ROW EDIT**, plus the F86-`BLIND` reconciliation and an explicit
   yes/no on whether F91's `|B/A|` claim depends on the misreading.
3. **Item 78: the missing 2×2 cell, by the free route if it exists**, and a
   verdict on *axis* vs *proxy* with the magnitude floors. ⚠ **State the
   measurement cost you paid, if any.**
4. **F94, F95, F92: a verdict each**, each with the second method named.
5. **§5's bounded pass as far as you got**, with the bar satisfied per finding.
6. ⛔⛔ **A COVERAGE TABLE: every one of F88–F101, and for each, exactly one of
   UPHELD / UPHELD-NARROWED / REFUTED / UNREVIEWED.** ▶ **This table is how the
   manager decides what may enter `.memory-php/`, so an honest `UNREVIEWED` is
   as useful as a verdict and a falsely-closed cycle is the one unrecoverable
   error.**
7. ⭐ **WHAT YOU ARE UNSURE OF, in its own section.**
8. **Brackets `66/0` / `16/0`, unmoved, quoted first and last.**
9. ⛔ **If a finding survives everything you can throw at it, THAT IS A RESULT.**
   `_038` upheld F85 and F86 while refuting three other claims. **Do not
   manufacture a refutation to have something to report.**
