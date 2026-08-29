# RECAP — state of the research programme

## START HERE — the next action, in one screen

**You are the research manager.** Read `.tasks/PROTOCOL.md` next (it carries the
manager's own rules), then `.memory/` 00–06 as you need them. Everything below
this box is reference; this box is what to *do*.

| | |
|---|---|
| **Patterns** | **26 exist, all built, all reviewed.** **Committed state: `24 PASS + 2 PASS-WITH-BLOCKED-ROWS`, 0 failures; 26 gate records, 26 published tables, 52 measurement records `0 STALE`.** ⚠ **The two blocked rows are `p01`** (a real 180 s Miri timeout) **and `p42`** (Miri on `large.bin`, declared in advance in its `miri.blocked_reason`) — ⚠⚠ **and `p42`'s blocked-row COUNT may legitimately vary on any given run, because the Miri slowdown is selected by the ENVIRONMENT and not by anything the gate controls (`.memory/00-environment.md`). Do NOT read a second `p42` block as a regression.** ⚠⚠ **TODAY'S COMMITTED STATE IS `p01 = 1`, `p42 = 1`, EVERY OTHER PATTERN `0` — ✅ manager-verified FROM THE JSON, and `TASK_132` re-verified it over 130 sweep logs.** ⚠⚠⚠ **AND THE MANAGER WROTE HERE THAT *"EVERY `p42 saw 2` / `p42 saw 3` / `p22 shows one blocked row` IS A GREP ARTEFACT"* — THAT OVER-GENERALISED FROM TWO TRUE INSTANCES TO A UNIVERSAL AND IT IS FALSE. ✅ `TASK_132`, ✅ manager-re-verified: `.temp/t107/gate-p42-rerun.log` CARRIES TWO GENUINELY DISTINCT BLOCKED ROWS — `adversarial-wincap.bin` AND `large.bin`, both real 180 s Miri timeouts — and `TASK_107`'s sweep used `tail -1`, NOT `grep -c`. *"p42 saw 2"* WAS A MEASUREMENT.** ⚠ **The correction destroyed the support for the sentence immediately before it, which is why that sentence now says the count may vary.** ✅ **WHAT IS TRUE: *"p42 saw 3"* and *"p22 shows one blocked row"* ARE artefacts of `TASK_125`'s `grep -c BLOCKED`, which matches the VERDICT STRING `PASS-WITH-BLOCKED-ROWS` (decoder: `grep -c BLOCKED = 2N+1`, ✅ validated 130/130 against the records); `p22`'s "hit" was its own `NOTES.md` prose echoed into the log; and *"p22 shows one blocked row and still `PASS`"* could not have been true, since a blocked row forces the other verdict.** ⚠⚠ **READ `blocked` OUT OF THE RECORD, NEVER `grep` THE LOG — and note the correction to that rule was itself made by over-generalising.** ⚠ **Otherwise a blocked Miri row is worth INVESTIGATING, not shrugging at** — the old advice here was itself the defect (TASK_077). ⚠⚠ **DERIVE THESE NUMBERS, DO NOT TRUST THIS ROW: it said *"`p23` is BUILT but NOT YET REVIEWED, `TASK_105` is the next thing to run"* for about fifteen tasks after `p23` was reviewed, corrected AND its corrections re-reviewed.** `ls -d patterns/p*/ | wc -l`; `grep -c '^| p[0-9]' .memory/06-catalogue.md`; and for the gate, read the `verdict` key out of `results/gate/p*.json` rather than re-running a 30-minute sweep. ⚠⚠ **Still PROVISIONAL: `TASK_088`** (`p19`'s re-fitted laws) **and `TASK_092`** (`p46`'s corrections, on which its headline ground stands) — **AND THE DISTINCTION IS LOAD-BEARING: `TASK_113` closed the TASKS as superseded; the FINDINGS that rest on them still carry PROVISIONAL markers** (RECAP's own findings section, in the `p19` and `p46` entries). ***The review debt being CLEAR is TRUE OF TASKS AND FALSE OF FINDINGS.*** ⚠ **This clause used to say *"this row and the `Do this next` row look like they contradict each other"* and quoted that row's wording — which the manager then DELETED in a trim. A cross-row citation rots the moment either row moves; state the distinction, do not point at neighbouring prose.** ⚠ **AND THERE IS A LIVE GAP IN THAT CLOSURE, FOUND WHILE RECONCILING THE TWO ROWS AND NOT YET ATTACKED: `TASK_113`'s stated reason was *"both are corrections-landing tasks for patterns that ALREADY HAD A REVIEW; the reviewed content is the reviewer's"* — but both markers flag NEW RESULTS LANDED IN THE CORRECTIONS TASK, not the reviewer's content.** `TASK_088`'s re-fitted laws and two-cause decomposition are a **re-fit**; `TASK_092` showed **`r4_mutreslice`'s full R5 verifies, `21 verified, 0 errors`**, against a refuted exclusion reason. ⚠ **So the closure reason may not cover what the markers flag. The manager commissioned `TASK_113` and will not clear the gap in its own commissioned review (rule 3) — WHOEVER PICKS THIS UP SHOULD DECIDE IT ON THE EVIDENCE, and *"the markers are right and the closure was too broad"* and *"the markers are stale"* are both live.** **`TASK_113` closed `090`/`091` as superseded.** |
| **Do this next** | ⚠⚠ **⚠⚠⚠ **THE PROJECT HAS A NEW PRIORITY AND IT IS THE USER'S, NOT A MEASUREMENT: NO NEW SPATIAL ROWS. THE REMAINING BUILD BUDGET GOES TO TEMPORAL AND TYPE.** **Full rule, the composition table it rests on, and the ADMISSION BAR'S NEW FOURTH LIMB: `.memory/02-bench-rules.md`, last section — READ IT BEFORE PROPOSING ANYTHING.** ⚠ **The corpus is 15 spatial / 1 temporal / 1 type out of 26. A 16th spatial row makes it worse whatever it measures.** ✅ **`ptr_offset` (finding 45) IS REFUSED BY THIS RULE — it is spatial. Record it as a limitation, do NOT probe it, and do not let a later session re-open it as *"but the census found it"*.** ⚠⚠ **THE QUEUE, IN ORDER:** ⚠⚠ **A1 and B1 ARE IN FLIGHT AS `TASK_133` AND `TASK_134`, LAUNCHED CONCURRENTLY — DO NOT RE-LAUNCH THEM; READ THEIR REPORTS.** **A1 · `TASK_133`, reviewer: re-adjudicate the FIVE unreviewed temporal refusals** (`p29 p30 p32 p33 p34` — all `PROVISIONAL, UNREVIEWED`; the temporal axis is closed on THESE reasons and a refusal's reason gets reused). ⚠⚠ **AND THE TASK IS NOT *"were they right?"* — ALL FIVE WERE DECIDED UNDER THE OLD THREE-LIMB BAR, WHOSE EVERY LIMB PRESUPPOSES A COST GRADIENT. The fourth limb did not exist then. A refusal can have been correct at `TASK_095` and wrong today with nobody having erred.** ✅ **A2 · DONE, this session — `harness/tools/composition.py`, and the hand-audited table reproduced EXACTLY.** ⚠ **It is DERIVED (population from `patterns/*/` and `results/gate/*.json`, which must agree) plus DECLARED (the category, hand-written) — the split is deliberate and `.memory/02-bench-rules.md` explains why the contract cannot derive the category. `--check` exits 1 on drift and catches a silent reclassification on MEMBERSHIP, not totals. Published into `results/SYNTHESIS.md` §7 as a scope limit.** ⚠⚠ **AND WRITING IT UP REINTRODUCED A CORRECTED FIGURE: the manager wrote *"`ptr_offset` is top-three in every one of the 22 programs"*; it OCCURS in all 22 and RANKS second or third in **15**. Finding 45's review had already made that exact correction. Caught on verification, fixed before commit.** **B1 · `TASK_134`, engineer: probe, in ONE task and BEFORE any row is written, the four non-spatial candidates: `p25` (realloc/stale pointer — THE FRONT-RUNNER), a stack-lifetime row, iterator invalidation, and `p35` (tagged union — BLOCKED, not refused, so it needs re-triage).** **B2… · build → review → WRITE THE FINDING, ~3 tasks per surviving row.** **C · writeup + stability: `SYNTHESIS.md` reconciliation; clear the 12 PROVISIONALs; the one-run lag repair and the detector allow-list inversion (finding 46 (ii) and (iii)); the 21 unpinned sidecars; final sweep.** ⚠ **9–13 tasks depending on how many rows survive B1.** ✅ **FIVE TASKS RAN THIS SESSION AND ALL FIVE ARE DONE** (`TASK_127`→46, `TASK_128`+`130`→44, `TASK_129`+`131`→45, `TASK_132` reviewed 46). ⚠ **The NARRATIVE lives in the findings — do not re-summarise it here; this row hit 11 316 characters carrying SEVEN COMPLETED tasks as if they were pending.** ⚠⚠ **NONE OF THE FOUR IS URGENT AND NONE BLOCKS THE OTHERS — the project is at a COHERENT STOPPING POINT: 26 patterns built/reviewed/found, the catalogue closed, the domain enumerated, the endgame answered. Pick on value, not on order. THE MANAGER'S RANKING, stated so it can be disagreed with: (c) the tables-pinned-on-contract class is the only one that can silently publish a FALSE NUMBER, so it goes first; (b2) is bounded and costed; (a) matters only if somebody proposes a row; the *resolves-to-wrong-content* half is real but unscoped and may not be worth scoping.** ⚠⚠ **OPERATIONAL, NEVER DELETE: `results/SYNTHESIS.md` is HAND-WRITTEN; `results/synthesis.md` (lower case) is GENERATED. Never regenerate over the capitalised one.** ⚠ **THAT LINE READ *"THE QUEUE IS EMPTY — EVERY WRITTEN TASK IS DONE"* WHILE FIVE TASKS WERE RUNNING ABOVE IT — PROTOCOL RULE 13, FOURTH TIME. Trust the row header.** ✅ **`TASK_125` LANDED: `harness/tools/temp_citations.py` plus a 66-entry BASELINE-AND-FREEZE; `rc 0 → 1 → 0` on a planted citation, ✅ manager-re-run.** ⚠⚠ **AND IT FOUND A FREE HOME FOR TOOLING, WHICH CHANGES WHAT IS CHEAP IN THIS REPO: `check.py`'s gate digest globs `harness/*.py` NON-RECURSIVELY, so `harness/tools/` IS OUTSIDE IT — ✅ verified, `source_sha256` byte-identical in 26/26 records with zero `harness/tools/` keys. Tooling there costs NO SWEEP, EVER.** ⚠ **Price, keep it written down: nothing under `harness/tools/` may be imported by `check.py`/`measure.py`/`build.py`, or it silently leaves the digest.** ⚠⚠ **THE MANAGER'S FIGURES FOR THE `.temp/` DEBT WERE WRONG TWICE — `.memory/00-environment.md` constraint 6 carries the corrected version (1441 paths / 77 dangling / 43 files, NOT 2454/88/59) AND the corrected REASON: of 66 classified entries only NINE are genuinely LOST, 25 are DESTINATIONS the citing script creates and 15 are REGENERABLE. DO NOT QUOTE THE RAW DANGLING COUNT AS DAMAGE.** ⚠⚠⚠ **AND `TASK_122`'s LOSS WAS NOT A DANGLING CITATION: `.temp/t86/cost.rs` IS ON DISK. It is UNVERSIONED, not absent — so the real failure is A CITATION THAT RESOLVES TO THE WRONG CONTENT, worse than one resolving to nothing, AND THE NEW CHECKER CALLS IT GREEN. That half is unbounded and nobody has scoped it.** **AND THAT IS ALL THAT IS WRITTEN BESIDES THE TWO IN FLIGHT.** ✅ **`TASK_118`–`126` are ALL DONE — NINE task arcs: `p42`'s third encoding (finding 39); the instrument corrections; findings 40 AND 41 both attacked and both DEAD; the CVE enumeration and its refused survivor (42); the Rust-rung theorem (43); the sidecar pin; and the `.temp/` checker.** ⚠⚠ **WHAT IS OPEN AND HAS NO TASK — read the findings before inventing one:** ✅✅ **(a) DONE — `TASK_128`, AND IT INVERTED ITS OWN PREMISE. FINDING 44.** ⚠⚠ **THE OBJECTION THE TASK LED WITH WAS RIGHT: `TASK_124` MEASURED 2 OF 6 PUBLISHED COLUMNS** (its §B2 is headed *"Verus. NOT SPENT, deliberately"*), **so *"every published difference"* — a phrase the manager copied out of THIS ROW into two more files — was wrong by four columns.** ✅ **The instrument was then pointed at the question: kernel byte-identical by construction (243 B, one sha256, both arms), `Ir` `+0.00`, and the PUBLISHED `obligations` column moves `3 → 5`.** ⚠⚠⚠ **BUT THE ENGINEER'S HEADLINE — *"so the ladder CAN price limb 2, on `obligations`"* — IS NOT MERELY UNSUPPORTED, IT IS INVERTED. ✅ REVIEWED AND DECIDED AT `TASK_130`: the columns that SEE limb 2 are ASSEMBLY and `Ir`; `obligations` is the one column that CANNOT, and it ranks a dead-code arm (`5`) ABOVE the mechanism arm (`4`).** ⚠ **The manager's own reason for doubting the headline — `_calib2` — was the WEAKEST of the three arguments available and would have LOST on its own; the reviewer's kernel-convention arms, the `8519 : 1` spelling-vs-presence ratio, and this project's own `p23`/`k_u5` and `p46` §8a precedents are what decided it.** ✅ **What survives: LIMB 2 HAS A MEASUREMENT AFTER ALL — at the LEVEL, on assembly and `Ir`. LIMB 1's census is REAL BUT OVERSTATED (see finding 44's M5/M6). LIMB 3 alone still prices on nothing shown specific to it.** ⚠⚠ **AND THE CLEAN NEGATIVE IS TWO-THIRDS RHETORIC: `p23` was scored against a DETECTABILITY test THE BAR DOES NOT STATE — the bar says *brings a new MECHANISM*, a NOVELTY criterion naming no column and no floor. It survives on LIMB 3 ONLY, and the transferable finding is better than the one reported: THE PROJECT READS ITS OWN NOVELTY BAR AS A DETECTABILITY BAR.** ✅✅ **(b) DONE — `TASK_126`, and it CORRECTED finding 43 rather than confirming it. THE QUEUE IS EMPTY AGAIN.** ⚠⚠ **THE SECOND READING WAS MIS-STATED, NOT UNTESTED: no input CAN be adversarial to a Rust rung here, because `requires` is a LENGTH bound in 26/26 and NEVER MENTIONS BUFFER CONTENTS (✅ manager-verified), `ensures` is a single TOTAL clause, and the pinned driver makes the window bound a THEOREM. MORE ADVERSARIAL INPUTS IS NOT THE FIX.** **13 449 fresh inputs, 600 rung splits, 0 Rust-rung splits; and NO RUST RUNG HAS EVER PANICKED in 107 592 fuzz runs (the C side: 29 SIGSEGVs, 8 aborts, 2 hangs).** ⚠ **My own guess was half right and the wrong half mattered: `unsafe`==`verus` holds 52/52 but `safe_naive` vs `safe_tuned` DIFFER 52/52 — so the tree has THREE behavioural Rust rungs, not two, and the R2/R3 zero is a MEASUREMENT.** ⚠⚠ **AND THE REAL QUALITY GAP IS NEW AND ELSEWHERE: 36 of 129 adversarial inputs (27.9%) MAKE ZERO KERNEL CALLS, the `adversarial-strideN.bin` template is 0-call in 22 of 26 patterns, and `p42` has 7 zero-call inputs out of 10. THAT is where the inputs are weak, and it has no task.** ⚠⚠ **(b2) NEW AND UNCOSTED UNTIL NOW — THE ZERO-CALL ADVERSARIAL INPUTS. 36 of 129 (27.9%) make NO kernel call at all; the `adversarial-strideN.bin` TEMPLATE is 0-call in 22 of 26 patterns; `p42` is 7-of-10 and `p01` is 6-of-6.** ⚠ **COST, so nobody re-scopes it from the one-liner: the fix is in `inputs/gen.py`, which is MEASUREMENT-HASHED — so it is a RE-MEASURE per pattern touched, not a gate run.** ⚠⚠ **AND WEIGH THE VALUE HONESTLY BEFORE SPENDING THAT: `TASK_126` proved no input can be adversarial to a RUST rung at all, so better inputs can only improve the C-SIDE harm matrix. That is still where all the harm is — 29 SIGSEGVs, 8 aborts, 2 hangs — but the ceiling is lower than it looks.** ✅ **The cheap, targeted version is `p42` and `p01` alone, bundled with the next re-measure either pattern needs for another reason. DO NOT sweep 26 patterns for this.** **(c) TAKEN — `TASK_127`. `TASK_121` found `results/tables/*.md` is pinned on the CONTRACT, not the CONTENT — stage 9 read `FRESH` while a table published a false sentence. THIRD instance of that class.** ✅ **THE FAMILY QUESTION IS ALREADY ANSWERED and `TASK_127` does not re-derive it: `TASK_125` §D split it — claims about CONTENT have ONE common fix (a content pin: `source_sha256`, `contract_sha256`, `derived_from_sha256`, `gate_source_sha256` are all the same mechanism), and this case is *"the known instrument pointed at the WRONG INPUT"*; claims about the OUTSIDE WORLD have none and are always a probe with a must-fire arm.** ⚠⚠ **MANAGER-MEASURED BEFORE WRITING THE TASK, AND IT REFRAMES THE ITEM: THERE IS NO LIVE INSTANCE TODAY — all 26 tables are BYTE-IDENTICAL to a fresh `report.py --stdout` render. So `TASK_127` is FORWARD protection, not a repair, and a forward-only task is one somebody later "confirms" by finding nothing.** ⚠ **The naive comparison reports 26/26 MOVED BY ONE LINE and that is an ARTEFACT of `print(md)` vs `write(md)`, not a finding.** ⚠ **Optional, and now safer than it was because the content has settled: split `SYNTHESIS.md`** (≈1 183 lines) **into argument + evidence appendix — ONLY as a PURE MOVE, `diff`-verified to contain no deletions, because a split IS a compression and compression is where this document's bias entered with no arithmetic signature.** |
| **THE CATALOGUE IS CLOSED, AND THIS TIME EVERY ROW HAS A MEASUREMENT** | ⚠⚠ **THIS ROW'S HEADER READ *"THE CATALOGUE IS RE-OPENED, and it was closed on a reason that did not hold"* WHILE ITS OWN BODY ALREADY SAID THE OPPOSITE — PROTOCOL RULE 13, COMMITTED BY THE MANAGER IN THE SAME SESSION THAT CITED RULE 13. Trust the body; fix the header.** ✅ **State: `48 = 26 BUILT + 17 REFUSED + 3 DEFERRED + 2 OTHER`, ZERO unadjudicated rows.** ⚠⚠ **RECOUNT CAREFULLY: `python3 .temp/mgr115/census.py` emits `26 + 22 + 0 = 48` and EXPLICITLY WARNS AGAINST publishing its adjudicated count as REFUSED — so it does NOT reproduce the `17/3/2` split above, which `TASK_120` verified SEPARATELY against the cells' own verbs. Two different questions; do not treat the script as the checker for the split.** ⚠ **Its `--naive` arm reproduces the trap that a keyword classifier reads 10 BUILT against a true 26, because `p24`'s and `p35`'s adjudication prose contains the word "BUILD".** **The two OTHER are `p24`** (probed, live, needs a new reason) **and `p35`** (blocked, not refused); **the deferrals are `p20`/`p21`/`p25`**, and ⚠ **`p25` is the ONE ROW ON WHICH THIS PROJECT HAS RUN NOTHING.** ⚠ **Every per-row reason is in `.memory/06-catalogue.md`'s status cell — READ THE CELL, not this box. The reasons are what get reused on the next row, and `p28` shows a right verdict can carry a wrong reason.** ⚠⚠ **WHY IT IS CLOSED — AND THE ANSWER CHANGED AT `TASK_120`. ~~FINDING 40 (duplication)~~ IS NOT THE REASON: duplication is the PRIMARY stated kill on 6 of 22 rows, 27%, so it is THE LARGEST FAMILY AND NOT A LAW — and the word covers FOUR different relations** (same predicate, strict subset, same conclusion, same detector). ⚠⚠ **AND ITS REPLACEMENT DIED TOO: ~~FINDING 41 (`LADDER`+`COST` kills 7 of 22)~~ FELL AT `TASK_122` — four categories merged into one, and NO CONTROL ARM (8 of 26 BUILT patterns publish a zero on their own headline axis).** ✅ **THE ANSWER IS THAT THERE IS NO SINGLE REASON: the 22 rows die for many individually sound reasons, and the classification is the result. PUBLISH NO GENERALISATION OVER IT.** ⚠⚠ **AND "CLOSED" NO LONGER MEANS "STOP" — BUT THE REASON HAS MOVED AGAIN, SO READ THE ENDGAME ROW AND NOT THIS SENTENCE'S EARLIER VERSION.** ~~*"the enumeration against `../LearnVeri/microbench/`'s 20 worked CVEs has never been run"*~~ ✅ **IT HAS: `TASK_123` ran it, 19 of 20 died, and `TASK_124` REFUSED the survivor. See the endgame row.** |
| **THE ENDGAME QUESTION — ANSWERED, AND THE ANSWER IS *STOP BUILDING, FOR A REASON NOBODY EXPECTED*. Kept as one row so nobody re-opens it from memory.** | ✅ **Wave 7 DONE** (`results/SYNTHESIS.md`, reviewed `TASK_111`, corrected `TASK_112`). ✅ **The catalogue is fully adjudicated** (row above). ⚠⚠ **THE 47 ROWS ARE PRE-PROJECT — ✅ `git`-verified, not inferred: `git show d5e0ccd:.memory/06-catalogue.md` has 47 rows in the FIRST commit against an empty `patterns/`. So the catalogue running out said little about the domain, and *"the catalogue is spent"* and *"there is nothing left worth building"* WERE DIFFERENT CLAIMS.** ✅✅ **SO THE DOMAIN WAS ENUMERATED AT LAST (`TASK_123`, finding 42): 20 worked CVEs against the reviewed bar, probe 1 first. NINETEEN DIED. The logical seven died MEASURED — strip the incidental index from `CVE-2021-3450` and three rungs are byte-identical at 108 B and `37.00 Ir`/call.** ⚠⚠⚠ **AND THE ONE SURVIVOR WAS THEN REFUSED — `TASK_124`, finding 42. DO NOT GO BUILD `CVE-2021-23017`; THIS ROW ADVERTISED IT AS LIVE FOR ONE TASK TOO LONG AND THAT IS THE `p23` ROT AGAIN.** **Its four-way split was a PROPERTY OF THE PORT: a perturbation contrast moved six of eight arms and left BOTH `Vec::push` arms unchanged, because `Vec::push` DELETES the bound rather than checking it. Its `R4 = Miri UB` was not an admissible R4 at all. Its `+63.00` was `+71.00`.** ⚠⚠ **AND IT DIED A SECOND TIME ON THE BAR ITSELF — BUT THAT KILL IS NOW CORRECTED AND NARROWED BY `TASK_128`, SO READ FINDING 44 BEFORE QUOTING IT.** ~~*"changing ONLY the bound's PROVENANCE moves every published difference by `+0.00`; a new source of the bound is a distinction THIS LADDER CANNOT PRICE"*~~ **overstated its evidence by FOUR COLUMNS: `TASK_124` measured 2 of 6 and its own §B2 is headed *"Verus. NOT SPENT, deliberately."* ⚠⚠⚠ **AND THE MANAGER'S FIRST REPLACEMENT SENTENCE WAS ALSO WRONG — *"cannot be priced ON ASSEMBLY OR `Ir`"* IS FALSE, CAUGHT BY `TASK_130`. SECOND TIME IN THIS THREAD A STRIKETHROUGH REPLACED ONE OVERSTATEMENT WITH A STRONGER ONE.** ✅ **THE TRUE SCOPE, and the evidence was PRINTED IN `TASK_124`'s OWN TABLE: no published rung-to-rung DIFFERENCE moves, because the sizing pass is a term COMMON TO BOTH ARMS — but every LEVEL moves, `−63.00 Ir`/call in all SEVEN of its own cells. And when both passes sit inside the kernel symbol, as a real pattern's would, the mechanism costs `+329.00 Ir`/call and `+208` kernel bytes** (`121.00 → 450.00`, `199 B → 407 B`; ✅ manager-re-run). ⚠⚠ **SO ASSEMBLY AND `Ir` DO SEE LIMB 2. What does NOT see it is `obligations`: a DEAD-CODE arm reads `5` against the MECHANISM arm's `4`, i.e. the proof column RANKS DEAD CODE ABOVE THE MECHANISM.** ⚠ **THE ROW STAYS REFUSED on its other independent grounds; finding 44 does NOT re-open it.** ⚠⚠ **THE OTHER HALF OF THE ANSWER, AND IT IS A LIMITATION OF THE SETTING: a CVE corpus answers *which mechanisms are missing* and CANNOT answer *which idioms matter* — 8 of 20 are pure decision bugs, a distribution no idiom census would produce, because CVEs select for EXPLOITABILITY not FREQUENCY. THAT HALF STANDS.** ⚠⚠⚠ **WHAT FOLLOWED IT HERE IS STRUCK, AND IT WAS THE MANAGER'S:** ~~*"AND THE IDIOM CENSUS CANNOT BE RUN HERE: there is no independent C corpus on this box"*~~ **and its consequence** ~~*"so the admission bar stays MECHANISM-based because the frequency-based alternative HAS NO INSTRUMENT — the honest reason this project's generality claims stop where they do"*~~. **The defect was a `-maxdepth 6` in the manager's own one-liner. Drop it and there is UPSTREAM PHP 4.0.2 whole, plus GNU coreutils, both on this box — with real density on this project's own axes, `goto` and `strcat` and `memcpy` included.** ✅✅ **AND IT HAS NOW BEEN RUN — `TASK_129`, FINDING 45: 49 898 bound sites over 991 147 DEDUPLICATED lines of real C in 22 PROGRAMS (PHP 4.0.2, GNU coreutils, and 24 upstream GNU packages the manager's own file list held and never characterised).** ⚠⚠ **THE ANSWER IS PARTIAL AND THAT IS THE RESULT: THE ORDINAL TOP IS A PROPERTY OF C, THE DISTRIBUTION IS A PROPERTY OF THE PROGRAM — `index` tops 21 of 22 and `const` tops 19 of 22, while the SHARES swing 42–50 points and SECOND PLACE FLIPS BETWEEN FOUR CATEGORIES. So a frequency-argued bar gets a FIRST PLACE AND NOTHING BELOW IT, which retires `TASK_113`'s request honestly.** ⚠⚠⚠ **AND THERE IS A MEASURED COVERAGE GAP: `ptr_offset` IS 0 OF 255 SITES IN THE BUILT TREE AGAINST A TOP-3 OPERATOR IN EVERY ONE OF THE 22 PROGRAMS. NO BUILT KERNEL WALKS MEMORY WITH A POINTER CURSOR.** ⚠ **UNREVIEWED, AND IT IS *NOT* A ROW — read finding 45's *"what this does and does not license"*, which names the specific reason to expect such a row to die.** ⚠ **Figures, corpus paths and caveats are in finding 42's coda and finding 45; `SYNTHESIS.md` §7 is corrected.** ⚠ **DO NOT print counts in this row.** It once carried *"1008 lines"*, *"39 findings"* and *"p26/p37 are the two live rows"* after all three had moved. **Derive them; the commands are in the `Patterns` row.** |
| **⚠⚠ The manager generalisation that was REFUTED, and it is the most useful thing here** | I read `TASK_093`'s `p28` refusal as a **family** result — *"safe Rust's answer to every pointer-backed structure is either an arena that never frees or `p27`'s mechanism, so `p29`–`p34` are ONE finding, not five."* **I wrote it into two task files by name and asked to be corrected. Both agents corrected me.** ✅ **The reviewed replacement is now in `.memory/01-ladder.md` and it is a RULE, not a refusal:** *"safe Rust's temporal guarantee is a guarantee about the **ALLOCATOR**; a structure that **recycles its own storage** gets no guarantee at all."* **There are FOUR outcomes, not two** — and outcome 3 is that **the type system is SILENT** (use-after-recycle *and* slot double-free both writable under `#![forbid(unsafe_code)]`, silently wrong, **Miri-clean**, ✅ manager-re-run), which is `p04`'s finding and kills `p32`/`p33`. ⚠ **A generation tag does NOT rescue it**, so **this file's own p14-cycle `(slot, gen)` proposal yields a `p04`-shaped row, not a temporal one.** Outcome 4 is `p34`: **the safe rung is WORSE than C** (`Rc` cycle leaks, `Weak` does not). And `p29` is the fifth and only good outcome. ⚠⚠ **AND `TASK_093`'s OWN STATED REASON WAS REJECTED BY ITS REVIEW** — *"safe Rust has no owned intrusive DLL (`E0382` + `E0499`)"* is **false**: the `E0382` was a plain double move (reproduced with a control containing no data structure at all), `E0499` is refuted by **four compiling spellings** under `forbid(unsafe_code)` including `split_at_mut` with two `&mut` alive simultaneously, and **the claim was self-contradicted by its own table two rows below it.** **Right verdict, wrong reason — `p31`'s failure mode, and rule 9 is the only thing that kept it out of `.memory/`.** ⚠ **A refusal's REASON is what gets reused on the next row. It needs the same scrutiny as a finding.** |
| **Selection is OVER — and the three box rows that used to live here are now history, moved below** | ⚠⚠ **The catalogue is closed (row above), so `p15`'s refusal, the `Pattern selection` probes and the `PROBE IN BATCHES` scheduling rule are no longer the next action.** They are preserved: **`p15`** in `.memory/06-catalogue.md`'s refusal block — ⚠ **and its NAMED UNBLOCKING CONDITION IS NOW DEAD**, because that condition was *"the day `_scan_unsafe_sites` admits a Verus-discharged `unsafe`"* and **the manager decided at TASK_096_REVIEW that the rule STAYS** (`.memory/02-bench-rules.md`); ✅ **its reusable artefact survives regardless** — a verified UTF-8 validator, `ensures res == valid_utf8(b@)` bidirectional, **`5 verified, 0 errors`, ZERO trusted items**, embedded verbatim in `.tasks/TASK_085_REPORT.md`. **THE THREE PROBES + probe 4** (the selection instrument) live in `.memory/06-catalogue.md`, ⚠ **and probe 2 is now known BROKEN IN BOTH DIRECTIONS** — the object-file md5 false-POSITIVES on relocations, the linked md5 false-NEGATIVES on any kernel with a branch or a global; **the form that works is normalised-disassembly text.** ⚠ **If a NEW row is ever proposed, the standing rule still binds: RUN ITS NOVELTY CLAIM BEFORE WRITING THE ROW** — both manager-proposed axes were refused, and both died on a claim one `grep` plus one run would have settled. |
| **Rules for writing that task** | ⚠⚠ **STATE NOVELTY CLAIMS AS QUESTIONS TO BE MEASURED, never as fact.** *"The first termination proof in the project"* was the manager's sentence in `TASK_070.md`; it was **false**, the engineer had no reason to doubt it, and it shipped into **eight places, two inside `contract_sha256`** — a review and a re-gate to remove. **Rule 9 protects `.memory/` from unreviewed findings and protects NOTHING from the task file itself.** p22's §0 counted 73 measures in one command once it was finally asked. ⚠ **Settle the bug class as the FIRST deliverable** — overturned on four patterns, upheld on two. ⚠ **A law owes its DOMAIN** (usually *missing columns*, not a caveat). **Additivity extrapolation — the only out-of-sample test here that can fail — HAS now failed once, on p38, and it was 100% attributable to three missing columns, none of them the one named.** The rule that came out of it: ⚠ **check the RESIDUE CLASS of any parameter your bands hold constant** — two of p38's three bands sat at `nw ≡ 0 (mod 8)` and the third did not, which fits in sample and misses out of it with no in-sample residual to warn you. ⚠ **Name the INLINE MODE at every figure** — p10 fitted both and the regressors *swapped*. All three in `.memory/03-measurement.md`. |
| **The trap that keeps firing** | **A headline can be wrong in the FLATTERING direction and pass a green gate.** p10 published *"safe Rust cheaper than unsafe"*: 60% was an **unsearched R4 side**, the rest **index-expression bookkeeping C pays more of than either Rust rung**. **p27 repeated it one pattern later** — a dead store in R4 that R3 did not have. **p47 is the first pattern to search the R4 side properly** (six levers, each measured *and* run through Verus). ⚠ **p38 made it four** (`+21/+25` published against a true `+24/+32`) and **p22 made it FIVE, and widest yet — `+2.00` published against `+125/+1021`, 510×.** ✅ **The trend is the good news: p38 disclosed after review, p22 disclosed BEFORE being asked, and p36 searched the R4 side FIRST and CHANGED WHICH RUNG SHIPS** — the R2-shaped unsafe rung verifies and is 1022/8190 dearer, so shipping it would have published *"safe beats unsafe by 1007/8175"*. ⚠⚠ **AND THEN p36 FELL INTO THE MIRROR IMAGE, WHICH IS THE NEW LESSON: it searched R4 and left R3 with ONE lever, which moved R3 the wrong way.** Published `R3 − R4 = +15.00 flat`; the review's first in-contract R3 respelling made it **+7**, and **+2** against the cheapest R4. ⚠ **Searching one side is not searching. A difference is only as honest as its WEAKER-searched endpoint** — count the levers on each side and say whether they are comparable. **Before publishing any rung comparison, ask what BOTH rungs' spellings are worth.** |
| **The loop** | build → review once → land corrections → ⚠⚠ **WRITE THE FINDING**. **Three tasks per pattern is the measured cost.** Per `PROTOCOL.md` rule 9, write `.memory/` **only after** the review. ⚠⚠ **THE FOURTH STEP WAS MISSING FROM THIS ROW UNTIL TASK_100 AND TWO PATTERNS FELL THROUGH THE GAP** — `p19` and `p46` were built, reviewed and corrected, and were then absent from the findings section for **45 and 35 tasks**, while this box counted them as done. **A pattern is not finished when its gate is green; it is finished when a reader can find its result.** Cross-check with `for id in $(ls -d patterns/p*/ | grep -o 'p[0-9]*'); do grep -q "\b$id\b" <the findings section> || echo "$id has no finding"; done`. |
| **Git** | Commit at task boundaries; subagents never commit. ⚠ **There is a GitHub remote** (`origin`, `HALOCORE/sec-ladder`). **Do not push unless the user asks.** ⚠⚠ **RULE 11'S HAZARD IS LIVE WHENEVER A REVIEWER PLANTS INTO TRACKED PATTERN FILES, AND THE MANAGER CAME WITHIN THREE MINUTES OF IT.** `TASK_084_REVIEW` plants real axioms into `patterns/p01-array-sum/{verus.rs,spec.md}` and restores them in a `finally:`; the manager committed **`bce8aa8` / `087a0af` / `ae19119` at 15:14:01–15:14:49** and the first plant began at **15:18**. ✅ **Nothing was contaminated** — every HEAD blob equalled the reviewer's pre-plant snapshot — **but that was luck, not sequencing.** ⚠ **Commit BEFORE launching a planting reviewer, never during**, and note the reviewer snapshotted **by bytes** rather than `git show HEAD:` precisely because the tree was dirty when it started. |
| **Before quoting any number** | `harness/measure.py --check-stale` (exit 1 on STALE). |

**Four settled answers that cost real time to get. Do not re-litigate them; each
is written up in `.memory/`.**

- **The R4/R5 pair is not a null control** — the `verus` kernel sits at a fixed
  offset from the `unsafe` one, and **that offset is a source-path-length
  artefact** (it moves if you clone elsewhere), so the pair is a **biased draw of
  size one**. *The floor is the layout population.* p06's own floor is **±4.6%**.
- **The TCB column is not gameable — retrospectively.** The census found two
  exposed items; **both have since been relocated, so the measured exposure is
  now `0`.** ⚠ Do not quote *"3.4% across the 16 patterns"* — that was this
  line, and it is wrong twice: the census ran over **14** patterns, and its
  numerator is closed (`.memory/04-verus.md`, which ships the recount).
  ⚠ **Prospectively the column IS gameable**: a `raw_ptr` pattern needs
  zero project-local trusted items. Ship **one number plus the U-license / V-gap
  / infra classification**; the two-number proposal was refuted by census.
- **`-C debug-assertions=on` also enables `assert_unsafe_precondition!` inside
  `get_unchecked`**, and 15 of 16 R4s rest on it. *"R4's advantage over R2
  disappears"* was **refuted** (true on p18/p01, false on p16). What holds on
  3 of 3: **at `-O3` with debug-assertions on, R4 becomes dearer than R3.**
- **`build.py` is hashed into the MEASUREMENT records, not just the gate
  records.** So "one harness edit, one 30-minute gate re-run" is true of
  `check.py` and **false of `build.py`** — that costs a full re-measure and
  churns published timing prose. It is why `O3d` was built, measured inert, and
  **reverted**; land it bundled with a pattern being re-measured anyway.

**The three things most likely to waste your time**, all learned the hard way:

1. **Ask to be corrected, not obeyed.** **Every agent that has contradicted the
   manager with a measurement has been right** — p13's engineer did it six times
   in one task, then six more while landing the review of it. Put your least
   certain call in every task file *by name* and ask for the measurement. The
   single highest-yield sentence in this project's history is some version of
   "I think X; prove me wrong." (Running count: the closing paragraph of the
   newest `.tasks/TASK_NNN*.md`, and nowhere else — two copies went stale here.)
2. **A green gate is evidence about the gate.** Reviews have found real defects
   past a fully green run repeatedly — including in `.memory/` text written one
   task earlier, and in the manager's own tooling.
   ⚠⚠ **AND THE SHARPEST INSTANCE IS A CHECK THE MANAGER WROTE FOR ITSELF AND
   COULD NOT HAVE FAILED.** After adding `axiom_decls` to 22 gate records, the
   manager regenerated `results/synthesis.md`, got a **byte-identical** file, and
   quoted that in a commit message as *"the change moved no published number"*.
   It is byte-identical because **`synthesize.py` reads `tcb_items` and the word
   *"axiom"* appears ZERO times in `synthesis/`** — the published column cannot
   see the field. **The three-limb acceptance test the manager wrote for the
   ENGINEER was good and caught a wrong design; the one it wrote for ITSELF was a
   tautology.** ⚠ **Before believing a check, ask what would make it FAIL.** Here
   nothing would have, and the `grep` that shows it is one command.
   ⚠⚠ **AND `TASK_084` FOUND A SECOND, DIFFERENT WAY FOR A *GOOD* ACCEPTANCE
   TEST TO MISS: IT WAS VERIFIED IN TWO HALVES AND THE JOIN WAS NEVER RUN.**
   Limb 3 was a genuinely good test — four planted axioms, one per route, and a
   checker that **exits 1 on a byte-identical `synthesis.md`**. It passed. But
   one script proved *source → gate log* and a **second** proved *hand-edited
   JSON → `synthesis.md`*, and **nobody ran a real axiom through a real gate
   into the record it wrote and on into the published table.**
   `TASK_084_REVIEW` did, on **ten** routes, and **limb 3's own stated failure
   mode reproduced on three of them** — including one where
   `grep -c r84_lie gate.log` is **0** while the gate prints *"3 TCB items"* and
   `synthesis.md` is byte-identical. ⚠ **A test split across two artefacts tests
   neither seam.** Ask **which single command carries a change from the source
   all the way to the number a reader quotes** — and if there isn't one, that is
   the test you are missing.
3. **Never write a finding into `.memory/` before its review lands** (rule 9).
   It is the only reason several overclaims were caught in RECAP rather than
   asserted as authoritative.
4. ⚠ **RUN A PROPOSED AXIS'S NOVELTY CLAIM BEFORE YOU WRITE THE ROW.** **Both
   axis proposals the manager has made were refused, and both died on the SAME
   finding: the axis's own distinguishing justification was false, and one
   `grep` plus one run settled it each time.** `p48`'s was *"no pattern
   exercises `is_init`"* — p27 exercises it in four places, including its core
   invariant. `p31`'s was *"provenance — the property Miri checks and nothing
   else does"* — Miri **warns** on the round-trip and **errors only on
   aliasing**, which is p08's shipped class. Both justifications were written
   from source reads and `vstd` greps **with nothing run**; both carried a rule-3
   PROVISIONAL flag in the catalogue **and were scheduled anyway**. **This is a
   defect in the manager's triage, not in the catalogue's rows.** The probe is
   one command and it would have cost two tasks less than the two refusals did.
   ⚠ **Both refusals were still the right OUTCOME** — each left four reusable
   measurements behind — **but the cheaper outcome was not proposing them.**

5. ⚠⚠ **HAND-RUN ASan IS BLIND ON THIS BOX, AND IT FAILS SILENTLY TO THE EXIT
   CODE.** ✅ **MANAGER-VERIFIED independently** (`.temp/mgr93/uaf.c` carries its
   own rebuild line). This shell inherits
   `LD_PRELOAD=/usr/libexec/coreutils/libstdbuf.so`, and a **dynamically**
   linked ASan binary refuses to start behind it:

   ```
   with LD_PRELOAD:  exit 1,  grep -c AddressSanitizer -> 0
                     only "==N==ASan runtime does not come first in initial
                     library list"
   env -u LD_PRELOAD: exit 1,  grep -c AddressSanitizer -> 2, full report
   ```

   ⚠ **Both exit 1**, so an exit-code check cannot tell them apart, and the
   diagnostic says *"ASan"* while every probe greps *"AddressSanitizer"*.
   `TASK_093` lost a full round of detector runs to it and read the result as
   *"nothing fires"*. ✅ **`harness/check.py` uses `-static-libasan` and is NOT
   affected** — this bites hand-run probes only. **Use `env -u LD_PRELOAD`.**
   ⚠ **Same class as `TASK_086`'s `head -4`**, which hid ASan's banner for four
   catalogue rows: *a detector that is not running looks exactly like a detector
   that found nothing.* **Ask what would make it FAIL** — here, a positive
   control that must fire.

6. ⚠⚠ **BEFORE CLAIMING A QUESTION IS OPEN, CHECK WHETHER `.memory/` ALREADY
   CLOSED IT. THE MANAGER DID NOT, AND IT COST A COMMITTED FALSE FINDING.**
   (TASK_087_REVIEW major 4.) Verifying an engineer's note, the manager
   committed *"p19 is the ONLY pattern that calls a vstd exec trusted function
   from its kernel, so 'Owed' 0's sixth route is no longer hypothetical."*
   **Refuted three ways, and each way is a different manager failure:**

   - **The grep was a WHITELIST of four slice-shaped names**, so it could only
     find slice-shaped calls. Enumerating all **187** exec `external_body` fns in
     the pinned vstd finds **p27 calling `ptr_mut_write` and `ptr_ref` from its
     kernel** — and **p27's own source says so in a comment.** ⚠ **A grep that
     can only find what you already thought of is not a census.**
   - ⚠⚠ **THE FRAMING RE-OPENED A DECISION THE AUTHORITATIVE LAYER HAD ALREADY
     CLOSED.** `.memory/04-verus.md` decided at **TASK_055_REVIEW**: one number =
     project-local trusted items, prose beside it, and a second *"vstd relied
     upon"* column **refuted with a 402-site census** and *"must not be
     reinstated"*. ⚠ **It named this exact case IN ADVANCE** — *"A pattern built
     on `vstd::raw_ptr` … **Decide how such a pattern is counted BEFORE building
     one.**"* **p27 is that pattern and it was built.** The manager wrote a
     "finding" that the layer it calls authoritative had already disposed of, in
     a section about the very column in question.
   - **It was not even the route it named.** The sixth route is about **used
     `assume_specification`s** reaching `check_miri`'s *"no trusted item ⇒ Miri
     not required"* branch. `slice_subrange` is `external_body`, and p19 has
     three local trusted items with `miri.required: true`, so **it never reaches
     that branch** — while the **literal** sixth route has been live in **22 of
     23 patterns all along** via `bytes.len()` and `bytes.as_slice()`.

   ✅ **RULE 9 CONTAINED IT.** The claim was written into a report marked
   UNREVIEWED and into the review task that asked for it to be attacked; **it
   never reached `.memory/` or this file's body, and nothing published moved.**
   **That is the process working, and it is the reason the rule exists.**
   ⚠ **The cheap check the manager skipped is one `grep` of `.memory/` for the
   column's own name.**

---

For a manager picking this up cold. Read this, then `.tasks/PROTOCOL.md` (which
now carries **the manager's own rules**), then `.memory/` 00–06.

**The `.memory/` files are authoritative and supersede any task report they
contradict** — several reports contain claims that were later refuted, and the
refutations live in `.memory/`.

## What this is

A micro-benchmark for the performance ↔ memory-safety tension. Each common C
pattern is built at five rungs — C, safe Rust (naive), safe Rust (tuned), unsafe
Rust, unsafe Rust + Verus proof — plus a sixth **R1h** hardened-C cell, across two
optimisation levels and two inline modes, and compared on assembly, executed
instructions, timing, proof burden and trusted-base size.

**48** patterns are catalogued in `.memory/06-catalogue.md` — 47 until TASK_066
added `p48` (the initialisation axis, which was missing entirely). **The ones that exist
are the table below — all green, all reviewed.** ⚠ A spelled-out count used to
sit on this line and it read *"thirteen"* against a sixteen-row table; count the
rows, or run `ls -d patterns/p*/ | wc -l`.

| | pattern | what it is here for |
|---|---|---|
| p01 | array reduce | calibration; the template every later pattern clones |
| p02 | length-prefixed copy | **the security result** — idiomatic C silent in 7 of 8 builds |
| p05 | 2-D index flatten | the first vectorised kernel; the proof→performance link |
| p08 | overlapping move | the bug safe Rust **cannot express** |
| p16 | TLV walker | the first data-dependent bound |
| p17 | HTTP suffix range | **the limit** — provably memory-safe and still leaking |
| p07 | binary search | the first kernel where R3's tax **never amortises** |
| p11 | NUL scan | library vs spelling vs safety, separated three ways |
| p03 | bounded stack | the proof's own invariant, handed to LLVM, closes the gap |
| p09 | bitset | **one character** between a bug everything catches and one nothing does |
| p12 | `strcat` fixed | the first **write**; a per-iteration check costs the bulk lowering |
| p04 | ring buffer | known **bits** survive a loop-carried phi where a range does not — `next_pow2(CAP) ≤ ARR_LEN` |
| p13 | `strncpy` truncation | a bound the optimiser can **see** outweighs the check that supplies it — and the contract pinned one side of the comparison |
| p06 | in-place rotate | **the `Ir` column is sign-wrong** — clang's hardened rung executes *fewer* instructions and runs *slower* |
| p14 | field split | **an exact law, fitted where the guard never fires** — and why "hardening is cheaper than the bug" is not publishable |
| p18 | LEB128 varint | **UB that is not memory-unsafety** — four catchers, all outside the measured matrix |
| p10 | weighted FIR stencil | **a headline wrong in the flattering direction** — safe beats unsafe, and none of it is safety |
| p27 | handle table | **the first TEMPORAL bug** — and the lifetime guarantee costs zero; safe Rust pays *less* spatial tax than unsafe |
| p47 | constant-time compare | **the proof certifies a LEAKING kernel** — identical contract, and the obligation count does not move |
| p22 | hash probe / open addressing | **the first pattern where SAFE RUST DOES NOT HELP** — a memory-safe non-terminating probe loop, Miri and ASan silent; the proof is the only rung that sees it |
| p38 | strict aliasing / type punning | **a MISCOMPILE is the harm** — and the undefined spelling is the **dearest of six neighbours**. Ships labelled a *demonstration kernel*; the first class **unsafe Rust does not reintroduce** |
| p36 | vtable / function-pointer dispatch | **the prover excludes the MECHANISM, not a spelling** — Verus cannot type `fn(u64)->u64` at all, so C's dispatch has no admissible Rust rung and the substitute costs **3.00000 `Ir`/dispatch**. Bug class is the tree's **twelfth** `index >= len` and it says so |
| p19 | protocol state machine | **safe Rust's bounds check and the validation pass C omits are THE SAME PREDICATE** — LLVM lowers it to `cmp $0x8`, a state-range check, enforced once per access vs once per call. Validation is `O(table)`, the check is `O(message)`, so **the buggy C rung is cheaper than unsafe Rust at `small` and dearer at `large`** |
| p46 | bignum limb add/mul | **the probe's sign was wrong and the boundary vanished with it** — the per-MAC safety tax is **0.00000** and `safe_naive < safe_tuned < unsafe`, because the shipped kernel lets LLVM prove `i+j < 96` and **delete all three checks**. Safe Rust's advantage is **100% an unroll decision** (`R2 − R4 = +2.00·n·m`, rolled-vs-rolled). First `by (bit_vector)` and `by (compute)` in the tree |

**If you read only one thing after this file**, read `.tasks/TASK_026.md` §0 — the
distilled rules from the thirteen-task spelling arc. Every pattern built after it
needed only prose corrections, and every pattern built before it needed
re-measurement.

## The findings so far — this is the actual output

**TWO numbering schemes — here is the map, so you never have to guess.** This
file's list is **RECAP's own digest**; `.memory/01-ladder.md` has a *different*
list, **one entry per pattern**, and **that one is authoritative**. They were
confused repeatedly before this table existed.

⚠ **The ranges that used to be written here were wrong** — this file claimed
`1–24` for itself and `1–12` for the ladder when the true counts were 25 and 14,
and the ladder's own warning claimed the mirror image. **Both guards against
citation drift had drifted.** Print the counts rather than trusting a constant;
the commands are in `.memory/01-ladder.md`'s numbering warning.

| pattern | `.memory/01-ladder.md` | RECAP (this file) |
|---|---|---|
| p16 | **4** | 9 |
| p17 | **5** | 10 |
| p05 | **6** | 12 |
| p08 | **7** | 13 |
| p07 | **8** | 15 |
| p11 | **9** | 17 |
| p03 | **10** | 18 |
| p09 | **11** | 19 |
| p12 | **12** | 21 |
| p04 | **13** | 23 |
| p13 | **14** | 25 |
| p06 | **15** | 26 |
| p14 | **16** | 27 |
| p18 | **17** | 28 |
| p10 | **18** | 29 |
| p27 | **19** | 30 |
| p47 | **20** | 31 |
| p38 | **21** | 32 |
| p22 | **22** | 33 |
| p36 | **23** | 34 |
| p01, p02 | findings 1–3 | 1–8 |

Cross-cutting entries exist only here: **14** (every rung is a spelling), **16**
(code layout / the 32-byte fetch grid), **20** and **24** (measurement and
infrastructure defects), **22** (decode panic pads).

⚠ **AND THERE IS NOW A LIVE COLLISION: "finding 14".** In
`.memory/01-ladder.md` it is **p13**; in this file it is the cross-cutting
*"every rung is a spelling"* entry. Both are cited often and they are
**unrelated**. The same trap exists at "13" (ladder = p04, here = p08).

**When you write a task file, name the pattern — *"p05's causal claim"* — never
the number.** Two task files have already sent an agent to the wrong finding.

1. **A Verus proof costs exactly zero instructions.** The proven binary is
   byte-identical to the unproven one; ghost code fully erases. Verified on raw
   machine code on all three patterns, at both opt levels.
2. **A proof alone buys nothing.** Proving safe Rust panic-free leaves every bounds
   check in place — rustc never learns what the prover knew. The payoff arrives
   only when the proof *licenses unsafe code*: R5 is R4's machine code with the
   obligations discharged.
3. **Safety is cheap — and finding 9 says it stays cheap even when the optimiser
   *cannot* see the loop.** Tuned safe Rust is **+4…+5 instructions per call on
   p01 and +10 on p02** versus unsafe — flat in the size of the data, not a
   percentage. ⚠ **This line said `+8…+10` for both until TASK_058**; p01's
   gate marginals are `safe_tuned 918.3 / 7205.3` against `unsafe 914.3 /
   7200.3`, and `p01/NOTES.md:262` and `.memory/01-ladder.md:500` both say +4/+5.
   Only p02's half was ever `+10`.
   Hardened C's check is +5 (gcc) / +12 (clang), also flat. **Always quote R3;
   R2 alone overstates safe Rust by 3.7× on p01 and by ~75× on p16.**
4. **The security result (p02), the strongest thing here.** On a one-byte
   overflow, idiomatic C prints a plausible answer and exits 0 in **seven of eight
   builds** — silent heap corruption absorbed by glibc's chunk rounding. The eighth
   aborts only because Ubuntu defaults `_FORTIFY_SOURCE 3`. Every Rust and
   hardened-C cell handles it. Control: delete the check from safe Rust and it
   panics rather than corrupting, so "Rust makes the check non-optional" is a
   measurement.
5. **Static instruction counts are not a cost model.** The ranking inverted twice.
   gcc emits fewer instructions than clang and executes 43% more.
6. **`Ir` and wall clock can disagree in direction** — gcc 10% fewer instructions,
   23% slower (p02).
7. **The same-backend comparison, which is the one that counts.** clang 22.1.6 is
   bit-for-bit rustc 1.97.1's LLVM. On p01 `large`, C-clang and unsafe Rust execute
   **exactly 143,740,000** kernel instructions. Static gap ⚠ **`+1`, not the `+2` this line published** — from the record, `n_fn` 37 vs 36 and `n_fn_nopad` 35 vs 34, i.e. **+1 padded AND unpadded** (corrected at TASK_112, which found it while restoring this finding into the synthesis and quoted only the `Ir` equality rather than inherit it) — an
   induction-variable choice, not an ABI cost. **Every C-vs-Rust claim needs the
   clang column**; gcc stays as the "what a distro ships" baseline.
8. **p02's residue curve predicts.** R2−R4 is a sawtooth, amplitude 179 Ir,
   resetting at `len ≡ 1 (mod 16)`, on a 0.21 Ir/byte linear term — re-derived at
   seven unsampled lengths and 8× the scale (178.9, 0.2125). The only model here
   tested by prediction rather than re-measurement.
9. **p16 — safety is cheap *even where it should not be*, and the one place it
   isn't, the check is only half the reason.** A TLV walker with a
   data-dependent bound, nothing hoistable, no bulk idiom to lose: the case p01
   said not to generalise to. **R3 idiomatic safe Rust is 5.7500 Ir/folded byte —
   R4's rate exactly, zero per byte**, its whole cost O(1) per call and shrinking
   with size. **The null is the result and it is now SWEPT** (TASK_025_REVIEW):
   fold both rungs the same way and safe−unsafe is a *single integer per call* at
   every length — over **127 consecutive `vlen`**, slope of the difference
   `0.0000000` Ir/byte, max residual 0.00, at six spellings. The mechanism is why
   it cannot be otherwise: the reslice (R3) and the `get_unchecked` (R4) both sit
   **outside** the fold loop, so the chunk body is mnemonic-identical at
   K = 4, 8, 16, 32 and 64. **p16's per-byte safety tax is 0.00000, and that is
   the sentence to quote.**
   ⚠ **What must NOT be quoted is a bare rate, or a difference of rates across
   unmatched folds.** In contract, one exact-string substitution apart, p16's rate
   ranges **5.04688 … 6.62500** (5.7500 shipped; 6.50000 and 6.62500 for
   `chunks_exact(4)` / `(8)`; a seventh spelling at 5.37500) — a 31% spread — and
   the measured rates carry ±0.01 Ir/byte from the driver's `println` term, which
   does not cancel within a binary and is 20× the gap between two published rates.
   The cross-spelling figure that reached four files as a headline was
   ~~−0.5625~~ and is **−0.65625**: the published value was the K=16 number left
   pointing at the K=32 rung when the sentence was re-aimed. It is a codegen
   difference between two folds and was never a safety cost. "O(1) per call" is
   separately corrected to `7 + 5·nrec` / `7 + 7·nrec` (TASK_015_REVIEW). See
   `patterns/p16-tlv-walk/NOTES.md` §10a.2 and `.tasks/TASK_025_REVIEW_REPORT.md`.
   Only the *naive indexed spelling* is O(n): +4.25 Ir/byte, +69/+72%.
   Of that 4.25, a rolled-vs-rolled control (`-unroll-count=1`, a bit-for-bit
   no-op on R2) shows **exactly 2.00 is the check and 2.25 is the 4× unroll it
   forecloses**, zero residual. And it costs **+0.27% wall clock** — the fold is
   latency-bound at 3.03 cycles/byte, identical on L1- and L3-resident inputs, so
   memory bandwidth is ruled out rather than merely unconsidered.
   **Fourth pattern in a row where R3 is the honest number.**

10. **p17 — the limit, and the most important artefact here.** A suffix-range
   parser (CVE-2017-7529). One missing `start >= 0`; the served range is the last
   `s` bytes, so one attacker `u16` picks the harm. For `content_len < s <= len`
   the bad read is **inside the allocation** — ASan clean, exit 0, and **safe Rust
   with the check deleted prints C's value bit-for-bit**. Only for `s > len` does
   it leave the allocation and Rust panic.
   Then the artefact. Guard the **slice**-relative index —
   `start >= -((off + body_start) as i64)`, which is exactly what a bounds check
   buys, no more — and Verus gives **9 verified, 1 error, the single error being
   the *functional* invariant; every access obligation discharges** (10/0 with the
   functional spec stripped). It reads a **neighbouring window's** bytes: output
   tracks the victim's secret, no panic, no `unsafe`. **A provably memory-safe
   program that leaks.** Memory safety and correctness are different properties
   and this is the measurement.
   **Two corrections are baked in above, both from TASK_011_REVIEW** — the
   shipped `adversarial-leak` row discloses only the *attacker's own* request
   table, so it shows memory-safe-but-wrong, not disclosure; and the delivered
   `start >= -(body_start as i64)` guard is strictly *stronger* than a bounds
   check, which is what made its leak vacuous. The distinction is one token and
   it is the whole finding: write "what a bounds check buys" **slice**-relative.
11. **4.25 Ir/element is a property of rustc, not of a pattern — and so is its
   2.00 + 2.25 split.** p17 reproduced p16's swept constant exactly (10.0000 /
   5.7500 once the driver's `println!` digit-count term is differenced out); p05
   reproduced it a third time on a non-Horner fold, *and* reproduced the
   decomposition — 2.00 check + 2.25 foreclosed unroll — from its own no-op
   control. ~~R3 is free for five patterns and then stops.~~ **The second
   sentence is retracted** — see finding 13. **No pattern has yet shown safe
   Rust paying an unavoidable per-element price.**
12. **p05 — safety on a vectorised loop, and the first causal link from proof to
   performance.** Per element inside the vector body the check is free (1.375000,
   five rungs identical). But it is hoisted into a 22-instruction per-row
   trip-count computation and survives in the scalar epilogue, so the cost is
   `O(nrow)`, not zero — and **wider lanes make it worse**: at AVX2 the gap is
   4.58× against SSE2's 1.42×, with safe Rust absolutely slower. `ncol ≡ 0 mod 8`
   pays a *full extra vector iteration*, so every power-of-two dimension is the
   worst case.
   The cause: the kernel already checks `nrow*ncol <= avail`, so R2's panic is
   dead on every run — but LLVM cannot eliminate it, because
   `nrow*ncol <= avail ⟹ i*ncol+j < avail` is **nonlinear**, which is exactly the
   obligation R5 discharges with `lemma_mul_inequality`. Linearising the guard in
   an isolated compilation deletes the whole per-row apparatus, so nonlinearity
   **is** the blocker for this kernel — confirmed at TASK_014_REVIEW against the
   manager's suspicion that p08 refuted it. But it is **not a general law** (p08
   keeps a dead *linear* check for a *relational* reason), and
   ~~"the safety cost is the price of the optimiser failing the lemma the proof
   proves"~~ is **retracted as written**: what those instructions price is two
   *spellings*, not safety. See finding 13.

   **REINSTATED at TASK_021_REVIEW, restricted to the row-scaled term**, in
   exactly these words: *"On p05, the `O(nrow)` part of the in-contract safety
   tax is the price of the optimiser failing the lemma the proof proves."* The
   in-contract respelling removes exactly one instruction per row — the `add`
   that makes the row base buffer-absolute — and the five that survive are the
   reslice's bounds check, whose deletion needs `(i+1)·ncol <= nrow·ncol`, the
   nonlinear fact `lemma_mul_inequality` discharges. Not true of the constants,
   not a statement about safety in general.
   **But p05 has no minimum, and neither does any pattern.** Three were
   published and all three refuted, each by the first lever the next agent
   pulled: `5·nrow + 6` → `5·nrow + 11` (respell the header) → `5·nrow + 13`
   (delete a redundant zero-check). Each had been reached by several independent
   machine-code bodies, so **"reached by many spellings" is not evidence of a
   floor**. And the quantity is unsound, not just unlucky: **`min(R3) − min(R4)`
   is the difference of two upper bounds and bounds nothing in either
   direction** — measured, the same edit is −2 on R4 and +1 on R3, and
   `5·nrow + 13` *exceeds* the published `6·nrow + 9` for `nrow < 4`.
   ~~Publish the in-contract **pair interval** (`36…134 / 128…410`, with the
   published 123/399 inside it)~~ and, if one number is wanted, the fixed-R4
   bound. ~~**An admissible pair has a tax of exactly 0.00**, so p05 does not
   support "safety costs something here" over free pairings.~~
   **Both struck at TASK_028** — the interval's endpoints and the `0.00`
   pairing are `r4_dataslice` and `c4_hu16_nz`, neither of which is a rung.
   Publish the **fixed-R4 bound** and the **R3-side span** (`5·nrow + 6` …
   `6·nrow + 13` = 101…127 / 331…403); see item 1 of "Priority" below, and note
   that this paragraph is the site that survived the first correction sweep.

13. **p08, and the retraction it forced — safe Rust beat unsafe Rust on p05.**
   p08's own result is structural: overlapping `memcpy` is UB that safe Rust
   **cannot express** (borrow checker, compile time, no runtime check and so
   nothing to measure), `unsafe` re-opens it via `copy_nonoverlapping`, and
   **R5 does not close it** — substituting `copy_nonoverlapping` into the trusted
   body verifies 11/0 and 15/0 under the twin, invisible to Verus, the twin and
   the contract pins; only Miri and the O3 identity pin catch it. On this libc
   the UB **executes and is unobservable**: glibc 2.39 `memcpy` *is* `memmove`,
   so R1 ≡ R1h at **0.00 Ir/call** — a *libc* property, never to be quoted as
   "memmove is free". ASan sees the overlap, but **`_FORTIFY_SOURCE` blinds it**
   under clang as well as gcc, because the check lives in the `memcpy`
   interceptor and not in `__memcpy_chk`.
   Then the blocker, which is about **p05**: `data.chunks_exact(ncol)` — one
   idiomatic safe expression, zero `unsafe`, no proof — is **`nrow − 7`
   instructions per call cheaper than the unsafe rung**, exactly, on every input,
   with identical output on all 150 committed p05 inputs. p05's shipped R3
   reslices by hand and pays `6·nrow + 9`. **Three patterns have now priced a
   spelling as safety's cost** (p02, p16, p05).

14. **Every rung is a spelling, the gap does not converge, and "safe beats
   unsafe" was never available as a language fact.** (TASK_015 +
   TASK_015_REVIEW. The programme's central methodological result, and the one
   that shapes the writeup.)
   The audit found **all three shipped R3s beaten**, each beater also cheaper
   than **its own R4**. The control that answered it — apply the same
   consumed-slice idiom to the *unsafe* rung — put unsafe back on top at
   **+11.00 Ir/call flat**. Then the review ran **one more round on each side**:
   replace the unsafe loop counter with the canonical C test `while rp < end`
   and it becomes **`nrow + 9`** — swept exactly over all 144 blobs, zero
   residual, with a second unrelated unsafe spelling landing on the identical
   figure. **`O(1)` became `O(nrow)` and the sign of the conclusion flipped on
   the first thing a reader would try. The gap does not converge.**
   ~~And it never could, for a reason available without measuring: R4 is defined
   by *permission*, not obligation, so every safe program is an admissible R4 and
   `inf(R4) <= inf(R3)` **by construction**.~~
   ⚠ **THAT ARGUMENT IS REFUTED — TASK_025_REVIEW, and it is the most consequential
   correction in this file.** The "reason available without measuring" was wrong
   *because* nobody measured it. **All six patterns pin
   `identity: unsafe ≡ verus, O3 exact`**, so an R4 is not a program that *may*
   use `unsafe` — it is a program that **must have a byte-identical R5 twin that
   Verus verifies**. R4 is bounded by what vstd can express; R3 is bounded by
   nothing. The classes are **incomparable, not nested**, and the inclusion runs
   the opposite way from the one that was published.
   Measured instance: p16's `chunks_exact(32)` fold is admissible as R3 at **zero
   TCB** and inadmissible as R4 — `chunks_exact`, `ChunksExact`, `by_ref`,
   `TryFromSliceError` and `get_unchecked` are each unsupported at the pin, so
   shipping it needs **five** new trusted items on a pattern whose whole claim
   rests on *one*. So "safe Rust beats unsafe Rust" is **not** disposed of by the
   definitions, and on p16 it has a mechanism instead: **the safe class can reach
   spellings the unsafe class cannot, because the unsafe class is chained to the
   prover.** Whether the infimum gap is positive is open on every pattern.
   What *is* still available a priori is nothing at all — which is the lesson.
   **Both spellings that drove this were out of contract.** p05's `spec.md`
   forbids `chunks_exact` and the running row pointer by name — either deletes
   the `i*ncol + j` multiply, which *is* the pattern — and **two consecutive
   tasks measured them and reported them as p05's numbers**, the manager's own
   retraction among them. The declaration was right both times and failed only
   by being **invisible**: it is prose, and the hashed block starts 240 lines
   later. So p05's `6·nrow + 9` **stands as a contract-relative number**, and the
   retraction of it is itself retracted.
   **And that contract-relative number bounds `inf(in-contract R3) − R4ship`
   and nothing else** — a bound only because R4 is held fixed by fiat, and the
   search for what it bounds has now failed three times
   (`patterns/p05-index-flatten/NOTES.md` §14). TASK_021 reported a *two-sided*
   floor, `5·nrow + 6`, on the ground that six in-contract unsafe spellings gave
   one instruction count. They had all decoded the header the shipped way, so it
   measured the header. TASK_021_REVIEW respelled that and got `5·nrow + 11`
   from 13 unsafe spellings; TASK_022 deleted a semantically redundant
   zero-guard and got `5·nrow + 13` from 46. **Each value had been reached by
   4–10 independent machine-code bodies, and two of the three were broken
   anyway** — so "reached by many spellings" is not evidence of a floor, and
   nothing here should ever again be published as one. See finding 12.
   TASK_021's companion claim — that the *unsafe* side "does not
   move at all" (six spellings, four distinct machine-code bodies, zero
   difference) — was **refuted** at TASK_022 on the ground that respelling the
   header moves R4 by 7 flat. ⚠ **That refutation is itself refuted**
   (TASK_027_REVIEW): the respelling needs `read_unaligned` and is not an
   admissible rung at the pinned vstd, and every alternative route to it is
   unsupported too. **TASK_021's claim was right for the wrong reason** — the
   unsafe side does not move, not because six agents happened to spell the header
   the same way, but because the `identity` pin leaves them nothing else to
   spell it with. Its
   functional form, its sign
   and its `O(nrow)` conclusion all survive under that stated pairing, but the
   "21%/18% of the tax lives in unpinned spelling" figure is the **R3 side
   alone**; over free pairs the interval is 80%/71% of the published tax. (That
   was then called "the loosest of the set"; the comparison put a *pair*
   interval next to p16's **R3-only** span. TASK_023's replacement — "p16's
   own pair interval is 111%/109%, wider" — is refuted in turn: measured, p16's
   is −239…+236 / −2449…+2244, i.e. 1759%/6095%, negative at the bottom on all
   24 blobs. **Both are withdrawn and neither is re-pointed** — a 2-lever p16
   search is not the peer of a 46-spelling p05 one.) The `nrow` axis it is swept on
   ships too: `inputs/gen.py` band D, 33 blobs, and `source_sha256` covers
   `gen.py` from TASK_021 so the law is re-derivable from a hashed file.
   **The policy, decided and implemented (TASK_016–018).** "Compare idiom-matched
   rungs" **does not work** — "same idiom" has no fixed point, its members
   differing by `O(nrow)` — and a published spread **cannot carry a safety number
   at all**, per the theorem above. What ships is a **named-spelling standard**:
   every pattern's hashed contract block carries an `idiom` object naming the
   tokens each rung must spell literally, uniform across all six, **labelled as a
   policy adopted after measuring**, with one measured clause — a rung spells the
   same operands the way its language forces — without which eight shipped cells
   fall out of contract.

   **What the pin buys is decidability, not attributability, and that was
   measured.** On p17 the excluded and an admissible spelling compile to the
   **same 478 bytes**; on p16, 42 of 77 Ir/call sit inside the unpinned part.
   What it does buy is a contract a `grep` can settle instead of one only an
   argument can settle — and a *boundary*, without which the spread is unbounded
   below on both sides.

   **The conclusion that follows, and it governs every number this project
   publishes: `R3ship − R4ship` bounds `inf(in-contract R3) − R4ship` and
   nothing else — a bound only because R4 is held fixed BY FIAT rather than
   minimised. It is NOT an upper bound on the in-contract safety tax**, which is
   what this line said until TASK_023. p16's `+27/+77` has a cheapest-found
   in-contract R3 of **−199 at `small` and −2545 at `large`** against the shipped
   R4 — the value having moved four times (~~`+19/+45`~~ TASK_023,
   ~~`−199/−2365`~~ TASK_024, ~~`−127/−2545`~~ the manager at TASK_025_REVIEW,
   who paired one rung at both inputs), and **no single spelling is cheapest on
   both blobs**: `chunks_exact(64)` is 72 Ir/call *dearer* than `(32)` at `small`
   and 180 cheaper at `large`, because a larger `K` leaves a longer scalar
   remainder tail. **A cheapest-found figure must name its input as well as its
   spelling**, which is why the word is "cheapest found" and never
   "minimum"; p17's `+32` has an in-contract respelling measuring
   **−19** against
   the shipped R4, byte-identical to the row an earlier task had excluded. Both
   patterns ship an R3 measurably off the floor of their own contract, so "the
   shipped R3 is the cheapest admissible spelling" is **false, not
   unestablished**. ⚠ **But "the unsafe rung is a spelling too" is now REFUTED on
   both of the two patterns that were said to show it** (TASK_027_REVIEW).
   ~~p05's R4 moves 7 flat (TASK_022)~~ and ~~p16's R4 moves `4·nrec` via
   `r4_hdr`~~ are **the same lever and it is not admissible on either**: at the
   pinned vstd, `read_unaligned`, `as_ptr`, `add`, `from_raw_parts`,
   `TryFromSliceError` and `from_le_bytes` are each `is not supported`, so
   ~~every route to respelling a header read needs a **new trusted item**~~ — and
   the `identity` pin makes a rung without a verifying twin not a rung.
   ⚠⚠ **"EVERY ROUTE" IS REFUTED (TASK_081_REVIEW, major 4) AND THE SIX
   `is not supported` ITEMS ARE STILL CORRECT — the error was inferring a
   universal from a list.** `vstd::slice::slice_subrange` +
   `vstd::bytes::u64_from_le_bytes` reads an arbitrary-offset little-endian
   `u64` **with its value**, at **ZERO author-written trusted items**:
   `2 verified, 0 errors`, manager-re-run. ⚠ **What this does and does not
   move:** it refutes the stated **reason**, not necessarily the conclusion —
   **that route's `Ir` cost has never been measured**, and `u64_from_le_bytes`
   wraps `try_into().unwrap()`, so it may be *dearer* than the shipped spelling.
   **Anyone re-opening p05's or p16's R4 side must measure it before claiming the
   side moves.** Until then: **neither pattern's R4 side has been shown to move
   by a single admissible instruction, and the route that might is unpriced** —
   which is a weaker sentence than the one it replaces, and is the one the
   evidence supports. The R3-side levers cost zero TCB and are large.
   Report the fixed-R4 bound —
   **`R3ship − R4ship` bounding `inf(in-contract R3) − R4ship`, R4 held by
   fiat** — and **do not report a pair interval until someone has built an
   admissible R4 that moves**; both published ones were built from rungs that do
   not exist. And **never a per-byte difference across unmatched fold
   spellings**.

15. **p07 — the first pattern where R3's tax has NO axis along which it
   amortises.** (TASK_026, reviewed at TASK_026_REVIEW: headline **confirmed**,
   two majors and five minors against the surrounding prose.)
   Binary search: `Θ(log n)` probes, no inner loop. **R3 costs `6.0000` Ir per
   probe with `probes = nq·⌈log2 n⌉`, so its share of kernel `Ir` rises in both
   `n` and `nq`** — 42.53% → 46.63% over `n` = 7 … 16 385. The asymptote is
   `6/(12 + f_lo)` ∈ **[46.15%, 50.00%]**, 47.99% on the shipped 50/50 workload:
   fixed by the kernel *and* the query distribution, not by the kernel alone.
   **Confirmed across six deliberately different workloads** — all-hit, all-miss,
   all-below, all-above, clustered, shipped — monotone rising in every one, so it
   is not an artefact of the query mix. The laws are exact integers verified
   **out of sample** on 30 fresh blobs with an independent probe-count
   implementation: `R3 − R4 = 9 + 4·nq + 6·probes`,
   `R2 − R4 = 36 + 11·nq + 11·probes`, 30/30 exact.
   ⚠ **What this is NOT: "the first counterexample to safety is cheap".** That was
   the manager's sentence and `.memory/01-ladder.md` already refuted it — p16/p17
   carry a swept **R2** tax of 4.25 Ir/folded byte whose fraction also rises
   (toward 73.9%), and p05 an `O(nrow)` **R3** tax. What is new is the *R3*
   scoping and the *no axis* part: p16/p17's R3 tax is a per-**call** constant
   (0.00000 Ir/byte, the reslice sits outside the fold loop) and p05's is
   `O(nrow)`, which vanishes along `ncol`. p07's vanishes along nothing.
   **The `Ir`-vs-`ns` half is real and was tightened, not broken.** Disabling
   LLVM's `X86CmovConverterPass` on unchanged source gives +10.07% `Ir` → −18.13%
   `ns`, and the review closed both of the delivery's own caveats: a
   symbol-by-symbol diff of the two whole binaries found **559 symbols, exactly
   one different**, and `--cache-sim` showed the lever locality-neutral (`D1mr`
   1076.82 on both). **Branch misprediction is measurable on this box after all**
   — `callgrind --branch-sim=yes` — see `.memory/00-environment.md`.
   Sharper still, with no compiler flag: changing only the *workload* makes the
   same binary execute **+7.84% more instructions in 71.75% less time**.
   ⚠ **Do not quote p07's R2 `ns` numbers.** `safe_naive`'s layout band is
   **28.47%** — the widest single-rung band this project has measured — so the
   "+28.0% small / +3.5% large, an 8× conversion factor" claim has **no
   established sign** and is withdrawn pending a bracketed re-measurement. R3's
   counterweight (+13.0% / +1.6%) *does* survive: bands disjoint on both inputs,
   in two independent runs.
   Two more, both confirmed: p07's R4 side is **degenerate, third pattern
   running** (`r4_ptr` measures −460/−1605 and its twin dies on *"dereferencing a
   raw pointer is not supported"*); and the catalogue's stated bug was **wrong** —
   midpoint overflow is unreachable by 2.1e9 because the `u32` header field binds
   long before RAM, while the reachable overflow is in the length check.

16. **Code layout moves wall clock by up to 27% at an unchanged instruction
   stream, and it is the 32-byte fetch grid.** (TASK_026 → TASK_029 →
   TASK_030_REVIEW, measured on all seven patterns.) Two binaries from identical
   source, differing only in where the linker put the kernel — same `n_fn`, same
   `md5_fn_norel`, same executed instructions — differ by up to 27% of wall clock,
   and the difference **flips the sign of a rung-to-rung comparison**.
   **The mechanism is identified and is static**: `win32` (the loop body occupies
   one more 32-byte fetch window — p01's 30-byte SSE loop sits inside one window
   at one residue and straddles two at the other) or `jcc32` (a loop branch
   crosses a 32-byte boundary, so the chunk is not DSB-cached — this box is
   Cascade Lake carrying Intel's **SKX102** JCC erratum). Both computable from the
   disassembly with **zero fitted parameters**, and both confirmed **out of sample
   on 20 pre-registered layouts** whose predictions were SHA-256'd before timing.
   **It does not hit everything.** Real on **p07 and p01**, marginal on p08,
   **absent on p02, p05, p16, p17** — the geometry flips on all seven, but only a
   front-end-bound loop pays for it.
   **The honest summary is three-part** (TASK_031, which refined it): *the signs
   survive on four patterns* — p02's +18.04% and p08's +105.16% come through
   mode-matching, and their entire 30-layout populations are 0.84–3.66% wide, so
   nothing in them could move a gap that size; *no magnitude survives to two
   decimals anywhere it was checked* — p08's `large` R2 is +50.91% published
   against +61.93% over the population, 11 points that layout does **not**
   explain; and *the C and R5 rungs of all seven patterns remain unbracketed.*
   **p01's and p05's `small` wall-clock rows are withdrawn**, for different
   reasons. **p01's sign flips: +5.80% / −3.61% (R2) and +7.10% / −5.45% (R3)** —
   re-measured at TASK_032 with the fixed timer, every number within 0.6 points of
   the blocked-timer values and no sign moved, plus a **fresh out-of-sample
   pre-registration using one directional rule (`win32@0`) with no per-rung
   tuning**, which held with perfect separation on all three rungs across two
   passes. The committed `common/layout/data/predictions_p01oos.json`'s own
   sha256 *is* the hash printed before timing — `sha256sum` it. ⚠ **p05's
   published reason was itself wrong** — the "shipped binary is the slowest layout of 31" ranking was a
   **blocked-round-robin artefact**, reproduced at TASK_031 with *zero* layout
   variation on byte-identical copies. p05's real defect: its `small` noise floor
   on byte-identical binaries is **5–45%**, wider than any gap read off it. Under
   the project's own alternating protocol its numbers are stable and positive.
   **What to publish**: mode-matched comparison, and pairwise `P(A > B)` over all
   layout pairs. Both converge. ~~Worst-vs-best range~~ and ~~dominance~~ are
   **both retracted** — both are extrema, neither converges, and the second was
   introduced as the fix for the first.
   And the instruments: callgrind's simulators are address-*sensitive* but model
   no part of the front end, so across a 27% mode they move by **≤6 events in
   10⁸**. Use them to attribute a mechanism, never to detect or rank a layout
   effect.
   **The methodological result, which outlives the finding: interleave by CELL,
   never by block, and measure the noise floor with byte-identical copies before
   believing any effect.** A probe that gives each cell a contiguous block of every
   rep — rather than alternating, as `harness/measure.py` does — flipped a sign on
   its own, and manufactured every reading that was attributed to p05's layout.
   p01's and p07's modes survived only because they are **protocol-insensitive**
   (p07 reads +27.4…+27.8% blocked *and* alternating), which is how they were told
   apart from the artefact. **All seven patterns now carry the protocol control
   and p05 is the only sensitive one** — so the bug reached no surviving published
   verdict, and p16's and p17's "gap < 1% either way" are clean negatives under
   both protocols, which had not been established before.
   **The tool ships**: `common/layout/` (hashed into all seven `source_sha256`),
   with the population data for p01 committed under `common/layout/data/` so the
   published table reproduces with **zero measurement** —
   `python3 common/layout/survives.py --dir common/layout/data p01`.

17. **p11 — the safe class reaches a library the unsafe class cannot, and it is
   worth 35% of the kernel.** (TASK_033, **reviewed** at TASK_033_REVIEW:
   headline confirmed by independent re-measurement, two majors and six minors
   against the prose, **no blockers**.) Family B's first
   pattern, and the first kernel whose **loop bound is not known before the loop**
   — a NUL scan runs until it finds a sentinel that may not be there.
   **The decomposition, which is the pattern's point** (all rates `body_len / K`
   off the listing, `vector_regs` empty on 8 of 8 kernels):

   | scan spelling | lowers to | Ir/byte |
   |---|---|---:|
   | C `strlen` | glibc IFUNC → **AVX2** | **0.078125** |
   | `CStr::from_bytes_until_nul` (R3) | `core::slice::memchr`, SWAR 2×u64 | **0.937500** |
   | `iter().position()` | scalar byte loop | 5.00000 |
   | R4 `get_unchecked` | scalar byte loop | 6.00000 |
   | R2 indexed | + `lea;cmp;jae` | 9.00000 |

   **12.0× is IFUNC+AVX2 vs baseline SWAR; 5.3× is which Rust spelling; 3.00000
   Ir/byte is the bounds check** — a library difference, a spelling difference and
   a safety cost, separated, where the naive report would have been one ratio.
   **The swept law**, zero residual over 61 points, all four residues:
   `R2 − R4 = 7.25000` Ir per string byte `= 4.25000` (fold) `+ 3.00000` (scan).
   **4.25 = 2.00 check + 2.25 unroll is p16's and p17's constant, reproduced a
   third time with the split included.** ⚠ **3.00000 is new and is the finding to
   attack**: the *same* check costs one instruction more because the scan's
   induction variable is window-relative where the fold's was hoisted to
   blob-absolute. **A bounds check costs 2 or 3 Ir/byte depending on what the loop
   already holds.**
   **And it is the largest instance of finding 14's R4-chained-to-the-prover
   result**: `r4_cstr` would be **−17 526 Ir/call (−35%)** on `large` and is
   rejected with **four** `is not supported` errors. The safe class reaches
   `core::slice::memchr` at **zero TCB**; the unsafe class cannot reach it at all.
   R3−R4 changes sign at string length 17–18, at `memchr`'s 16-byte threshold, and
   `small`/`large` are specified on opposite sides of it.
   ⚠ **And the correction that makes it a better result** (TASK_033_REVIEW major
   1): p11 discharges an overflow obligation with one line in the *program*
   (`if q >= len { break; }`) where p17 had to buy a second `requires` — and p11
   shipped calling that **free**. It is not: it costs **1.00000 Ir per scanned
   byte, 8.5% of R4**, because the guard forces the scan's exit reason into a
   register. **The real trade is 8.5% of the kernel instead of a precondition**,
   and that is more interesting than the claim it replaces. Neither route is free;
   see `.memory/04-verus.md`.

18. **p03 — the safety tax IS the price of the optimiser failing the invariant
   the proof proves; it is NOT a fact about Rust; and it retires "nobody has built
   an admissible R4 that moves".** (TASK_036, reviewed at TASK_036_REVIEW: causal
   claim **confirmed** with three negative controls, two blockers and two majors
   against the prose.) First kernel whose **control flow is attacker-chosen**,
   first whose safety law is per *executed operation*.

   **The control that does it.** `m_clamp` = R3 plus a **dead**
   `if sp > STACK_CAP { return 0; }` — R5's own invariant handed to LLVM. Safe
   17 → 13 Ir per executed pop, unsafe 14 → 13, **gap exactly zero on both sides**,
   zero fitted parameters. **It is the invariant and not range propagation**:
   `sp > 1000` is byte-identical to shipped R3 (nothing), `sp > 65` leaves the
   check standing *and* is dearer, and a non-dead early return saying nothing
   about `sp` is dearer with the check standing.
   **This generalises finding 12's reinstated p05 sentence from a NONLINEAR fact
   to a linear one** — nonlinearity was p05's whole stated excuse. ⚠ **With two
   qualifications that change what it says, both measured:** it is **not
   Rust-specific** (clang keeps a manual C bounds check at exactly 4.00000
   Ir/executed pop, gcc keeps it too, and *both* delete 100% of it given the
   identical clamp, byte-identically — two middle-ends, and gcc shares none with
   rustc); and **LLVM does eventually derive the fact** (the clamp is gone from
   the output and the `sp > 64` path is treated as unreachable), so it is analysis
   **seeding**, not inability to prove the lemma.

   **The laws**, max residual 0.0000 over 89 blobs: `R1h − R1 = 2.00000 · xpop`
   exact and **identical on gcc and clang**; `R3ship − R4ship = 3.00000 · xpop + 5`;
   and **0.00000 on push, dropped push and empty pop** — the same check deleted on
   one side of one function and kept on the other. ⚠ **The `3.00000` is the
   shipped spelling's rate, not the class's**: in contract the class runs from
   **+3.00000 to −1.00000** per executed pop, so p03's R3-side span is
   **−113 … +5110** / **−202 … +17237**. The lever is `assert!(sp <= STACK_CAP)`
   — one line, zero `unsafe`, zero TCB, admissible (the gate's own matcher takes
   it and `.memory/01-ladder.md`'s R3 definition names *"hoisted length
   assertions"*) — **and WHERE it goes is worth 2 Ir twice** (TASK_037): on the
   loop's **back edge** it is `−1.00000·xpop` with no dropped-push cost and is
   cheapest on **both** blobs; at the loop **head** it is byte-identical to
   `m_clamp` but costs `+2.00000·dpush`, because LLVM then materialises the
   now-known `sp == STACK_CAP` on that edge; in the **pop arm** it survives as a
   runtime `cmp $0x41`. Two published cheapest-founds refuted on this one
   pattern, the second after a review had confirmed the first.
   ⚠ **"The guard must be in the same basic block" is REFUTED** — hoisting it into
   the loop head is byte-identical to shipped R3 (that control is itself out of
   contract, so it refutes the *mechanism* and is not a spelling of the class).
   The real discriminator is that
   the **push** guard supplies the *upper* bound the access needs, locally, while
   the **pop** guard supplies only the lower bound and the upper must come from
   the loop-carried invariant.

   **And the standing question in finding 14 is ANSWERED.** `m_clamp_unsafe` — R4
   plus the same dead clamp — verifies **9/0 with zero new trusted items**, holds
   the `identity` pin byte-for-byte, and measures **−118 / +497** against
   `R4ship`; on the back edge (`m_clamp_unsafe_tail`, also **9/0**, identity
   byte-for-byte) it measures **−118 / −207**. **The project's first admissible
   R4s that move**, so p03 has its first non-degenerate pair interval — the R4
   endpoint now has measured width, 2884…3002 on `small` and 8177…8881 on
   `large`. (The two class minima are 5 apart on both blobs; that is the per-call
   constant and **not** a tax — `min(R3) − min(R4)` differences two upper bounds.) Paired with the asymmetry: `assert!` on the
   unsafe side is `error: panic is not supported`, so **the safe class reaches a
   spelling the unsafe class cannot** — third instance of the R4-by-permission
   result, first where the safe lever is one line.

   **The bug** is not a wild address: `sp−1` at 0 wraps to `stack−1`, inside the
   kernel's own frame. It does not fault; it returns a wrong answer, and **R1's
   checksum is not reproducible across runs** — a *pointer*-disclosure shape,
   distinct from p17's data disclosure. UBSan beats ASan (static array type); a
   sustained underflow faults at exactly the 8 MiB `ulimit -s`. **Verus 9/0 first
   run**, no lemma. And the gate caught a **tautological conjunct on a trusted
   item** via 5c-twin's per-conjunct probe — its first fire on shipped code.

19. **p09 — one character, in one position, separates a bug everything catches
   from a bug nothing catches.** (TASK_038, reviewed at TASK_038_REVIEW:
   invisibility **confirmed against four vacuity attacks**; one blocker and five
   majors against the prose, two of them project-wide.)

   ```
   words[q >> 6]   shipped
   words[q >> 5]   caught by memory safety ALONE, on every input
   words[q >> 7]   caught by NOTHING — no bounds check, no ASan/UBSan,
                   no Miri, no memory-safety proof
   ```

   `q >> 7` is `q/128 ≤ q/64`, so under the guard it is **always a legal word
   index**: `19 verified, 0 errors` with the functional spec stripped, `20/0` once
   the spec moves to match. **Zero instructions** (6691.70 vs 6692.30), and
   **the whole 368-byte R4 kernel differs in ONE BYTE** (offset 156, `06` → `07`;
   TASK_039). All five builds print the same wrong answer **on `small`, p09's
   headline blob** — not only on thin windows; ASan+UBSan are silent on *every*
   input and Miri is `exit=0 UB=no`.
   ⚠ **And it is a CLASS of ≥ 9, not an instance**: the obligation reduces to
   `C·(nwords−1) + 8 ≤ 8·nwords`, so every shift digit above 6 and every scale
   below 8 qualifies. Second member measured — `4 * (q >> 6)`, again one differing
   byte (the SIB scale), and its `_msonly` verifies **18/0 with no ghost line at
   all** where `q >> 7` needs one. `q >> 7` is the headline only because it is the
   one member in `q >> 5`'s own character position. ⚠ **This is the example to quote, not
   `q & 31`**, which is a *two*-character edit costing +32% on R4 — p09 shipped
   calling both "one-character bugs" and that is wrong on both counts.
   **The probe is not blind**: `_msonly` survived `assert(false)` in three places
   and guard deletion, so a proof that still catches R1's spatial bug discharges
   these clean.

   **The obligation that fires is a VERIFIED item's**, `load_u64`'s — not the
   trusted accessor's, whose `requires` is *shadowed*. p09 is the only pattern
   with decoder wrappers, so this is the first time the memory-safety obligation
   sits **outside the TCB boundary**. TCB is **7 lines / 4 items**, the
   second-smallest here.

   ⚠ **The reslice hazard, and it is the whole of p09's R3 > R2 inversion** (the
   first in this project). LLVM loses the 8-byte load-merge idiom on exactly one
   of eight loops: **reslice + a data-derived index + a multi-byte decode at it**.
   R2 keeps the merge on the *same* access. `+21` lost merge, `+1` spill, `−5`
   cheaper checks = `+17`. **Half of the p03-style seeding win here is the
   restored load idiom, not deleted checks**, and `q & 31`'s cost is the same
   mechanism — which unifies p09's two cost stories. **p03's seeding control does
   not transplant**: the failed inference is the composition through the
   **multiply**, not the shift.

   The three-check decomposition has **zero free parameters** — every coefficient
   is a loop-body instruction count off the listing, and out of sample it predicts
   `large` to within **1.13 Ir of 73404**. `q >> 6` ≡ `q / 64` on all three
   compilers, so that `forbidden` entry moves no number.

20. **Two measurement defects found in passing, both project-wide.**
   (TASK_038_REVIEW.)
   **(a) `measure.py`'s `ns` column is a whole-process LEVEL, never a
   difference** — the per-process constant (argv, file I/O, payload decode) is
   inside every published wall-clock number, and on p09 it is **55% of `small`
   and 73% of `large`**. Subtract `t(n_iters = 1)` before quoting any ratio. **A
   whole mechanism died on this**: p09's "the extra instructions retire cheaper
   than average" (ILP) came from a 2–4× `Ir`-vs-`ns` gap, and corrected **the
   largest surviving factor is 1.5×**. ⚠ Name the blob (TASK_039): R3's `ns`
   penalty exceeds its `Ir` penalty **on `small` only**; on `large` it stays
   below (+179…+183% against +199.4%). The correction's own error bar is **±9
   points** — `R5 − R4`, which must be 0, reads −0.9…+8.7% across four runs — so
   quote a corrected ratio only where the effect clears it, as p09's do by 11–25×.
   See `.memory/03-measurement.md`.
   **(b) A `forbidden` entry without backticks is audited ZERO times**, while the
   verdict line two above still counts it (**`check.py::idiom_audit`** keys on
   `_TICK`, which is defined in `check.py::idiom_lines`). ⚠ **This citation has
   now been wrong THREE ways**: `:929` until TASK_066, `:1103-1105` until
   TASK_071, and then `spelling_matches` -- a FUNCTION NAME, introduced by
   `f4d0e63`, **the commit whose entire subject is fixing citation rot**.
   `_TICK` appears nowhere in `spelling_matches`. p09
   shipped 5 forbidden entries and 0 audited spellings — its "forbidden: 0 hits"
   was kept **by auditing nothing**. Backtick every entry you want enforced.

21. **p12 — the bulk-copy lowering needs BOTH ends of the copy free of a
   per-iteration check; and a write bug forces the *adversarial* row, not the
   perf row.** (TASK_040, reviewed at TASK_040_REVIEW: two blockers, three
   majors; headline **confirmed and sharpened**, two published numbers moved.)
   First bug here that is a **write** safe Rust cannot express; first time
   `c-gcc` and `c-clang` differ in **behaviour**.

   **Confirmed by the control p12 did not build**: a *safe byte loop* with no bulk
   call anywhere in its source lowers to `memcpy` — so the recovery is about
   **where the check is**, not about `copy_from_slice` carrying its own bound. ⚠
   **But "on the destination" is not the rule**: checking only the *source* per
   byte also kills it. **Both ends must be free.** Consequence: `R2 − R4` has no
   per-byte law, and precisely — R2 alone is **exactly linear at 24.75 Ir per
   copied byte**; the non-law is entirely **R4's `memcpy` size dispatch**.

   ⚠ **THE STRUCTURAL CLAIM WAS TOO STRONG, and the reviewer built the row p12
   said could not exist.** What is forced, with no read analogue: *for a write bug
   whose guard's threshold **is the destination's ALLOCATED EXTENT**, every input
   on which the guard fires is one on which the unguarded rung executes an
   out-of-bounds store.*
   Whether that input can **also** be a checksum-agreeing perf row is a **design
   choice** — fold the destination at *fixed extent* and put rejection exactly at
   capacity, and checked and unchecked print identical checksums at every
   `n_iters` while ASan still fires. The price: **the perf row executes UB on
   every call**, usable only in the silent regime (≤ +8 B here).
   ⚠⚠ **AND THE PREMISE DOES NOT REACH THREE OF THE FIVE PATTERNS IT WAS WRITTEN
   FOR** (TASK_041, measured: `p12/NOTES.md` 1b, probe under ASan+UBSan). Hold
   everything fixed but the guard's threshold: at `n == sizeof dst` the guard
   fires and the unguarded rung stores OOB; at a **caller-supplied** `n < sizeof
   dst` the guard fires just as loudly — the checksums differ — and the unguarded
   rung is **ASan- and UBSan-clean**. So **p13** (`strncpy`'s `n` is
   caller-supplied, and its bug is the missing NUL and the OOB *read* downstream)
   and **p24** (`child < n`, a live length below capacity) do **not** inherit it;
   **p14**'s delimiter is not a bound at all and it is the scan's `i < len` the
   sentence reaches; **p23** and **p25** do inherit it. The generalisation is
   about the **threshold**, not about the write: a threshold at the allocation's
   extent makes "the guard fired" and "the unguarded rung committed UB" the same
   event; a threshold inside the allocation makes them independent, and then the
   write patterns behave exactly like the read patterns.
   See `.memory/02-bench-rules.md`.

   ⚠ **`−26.00` is a FIXED-R4 figure.** p12 called its pair interval degenerate on
   an *inference*; the reviewer **built** the cheaper R4 (route A) and it verifies
   **15/0, twin 18/0**, holds `R4 ≡ R5 exact`, and is **17.00 / 92.00 cheaper**.
   On `large` that **flips the sign** — shipped R3 is **+66.00 dearer** than the
   cheapest verifying R4. The fourth "safe beats unsafe" instance is fixed-R4
   only. And the `identity` pin's price is **3.00 Ir per string walked**, not the
   `+2` published — that was a static `n_fn` delta wearing a per-string label.

   Observability is a function of **magnitude and compiler**: **+1…+8 B silent
   and wrong on both**, then gcc's canary and clang's caller-frame corruption,
   then clang's SIGSEGV. ⚠ **Quote the regime, not the constant**: the two upper
   boundaries are frame-layout properties and move with the binary — step-1 on
   p12's own probe they are **+9** and **+57** (TASK_041), step-4 on the shipped
   kernel the review read them as +12 and +64, and the first publication's coarse
   grid gave +16 and +64. The **+8** boundary is the one that reproduces.
   `-fno-stack-protector` would be **both a thumb on the scale and unnecessary**.

22. **Attribute a surviving panic pad by DECODING its `core::panic::Location`.**
   (TASK_040_REVIEW.) Counting pads says *how many* checks survived, never
   **which** — and on p12 the difference overturned a published mechanism and a
   rung's source comment on the day it was written. `dst[..dlen]` contributes
   **zero** pads in all three fold spellings, so "the count stays at 2" was
   evidence the fold **never** contributed one, read as the opposite. The decoded
   survivors are the window reslice and the source reslice, which gives a sharper
   discriminator than p03's locality story and does **not** transplant it: a bound
   from a **constant** LLVM can see is elided; a bound from a **runtime value** is
   not. **Tool, now committed: `patterns/p12-strcat-fixed/controls/pads.py`**
   (TASK_041 — the review's `.temp/r40/pads.py` is gitignored, and its `%rcx`-only
   `lea` match under-counted R2 by 2 of 7; the shipped one matches any register,
   validates the decoded struct, resolves the file name through the
   `R_X86_64_RELATIVE` addend, and prints the guarded expression with a caret).
   See `.memory/03-measurement.md`.

23. **p04 — known BITS survive a loop-carried phi where a range does not, and the
   rule is `next_pow2(CAP) ≤ ARR_LEN`.** (TASK_042, reviewed at
   TASK_042_REVIEW: **the headline was confirmed by a stronger test than I asked
   for, and its stated mechanism was refuted**; one blocker, three majors.)

   **The three-operator series closes, and the closing sentence survives.** p05
   asked whether a bound survives a **multiply** (no — nonlinear), p09 a **shift**
   (yes alone; no through the composition with a multiply), p04 a **modulus**.
   The evidence that settles it is the control nobody asked for: spell the wrap as
   a **source-level branch** and both ring checks come back **at `RING_CAP = 64`
   as well as at 60** (86 → 101 instructions, 1 → 3 pads), at the identical
   provable cursor range. **So the range is never what carries; what carries is
   known bits contributed by the operator.**
   ⚠ **What was FALSE is p04's published explanation of the 60 case** — *"`% 60`
   fixes no bits"*. It fixes `< 64` (`computeKnownBits(urem x, 60)` zeroes the
   high 58), **and that survives the phi**: `% 60` into a `[u64; 64]` array
   elides. The measured rule, zero fitted parameters, is **`urem x, C` ⟹
   `x < next_pow2(C)`, and `next_pow2(CAP) ≤ ARR_LEN` is NECESSARY for elision
   and sufficient only ABSENT a cursor-relating guard** — the necessary half
   reproduces every capacity p04 built *and* the mixed cases it never built
   (`% 32` into `[u64;64]`, `% 64` into `[u64;96]`: both elide). ⚠ The qualifier
   is load-bearing: `% 60` into `[u64;64]` **with** p04's two guards is 2 pads,
   not 1 — the store check goes, the load check stays. A guard destroys the fact
   for `urem` and **not** for `and`, which is what separates the two operators.
   **`RING_CAP = 60` is still the largest single effect**: at matched execution
   counts `R3 − R4` goes **+5 → +479**, p03's dead clamp takes it back exactly,
   and three middle-ends agree in both directions — **the operator, not safe
   Rust.**

   ⚠ **THE SHIPPED R3 IS NOT THE CHEAPEST FOUND — and that yields TWO numbers,
   not a correction to one.** Six in-contract spellings across **five distinct
   machine codes** measure `3367 / 11666` against the shipped `3368 / 11667`.
   p04 **did not re-ship** (now a project rule — `.memory/02-bench-rules.md`,
   "never re-ship a rung because a cheaper spelling was found"), so the
   **fixed-R4 bound stays `+5.00`** and the **cheapest-found in-contract bound is
   `+4.00`**. Publish both, labelled; I briefly told the engineer to overwrite the
   first with the second and it refused, correctly. *"The first pattern whose
   shipped R3 is the cheapest found"* is **false** either way — beaten by the next
   lever, exactly as on p03. **The lever is new**: a **two-step reslice**
   (`split_at(off).1.split_at(len).0`), whose mechanism is **register allocation,
   not bounds-check removal** — `off + len` needs a scratch register,
   `buf_len − off` is computed in place. **Untried on every pattern before p04,
   and most patterns' R3 opens with the reslice it improves.** The `idiom` block
   pins no reslice spelling, so it is the *cheapest-found* claim that failed and
   not the declaration; p04's direction test holds.

   ⚠ **Two of the seven "exact integer cost models" fail out of sample, and no
   in-sample blob could have shown it.** The two R1 rows were fitted over 99 blobs
   on a licence verified only on band F — **where `epop == 0` by construction**.
   One fresh blob with `dpush` *and* `epop` both non-zero misses by **−385 / −330**;
   the same laws in *R1's own* counts land exactly. The other five re-derive by
   independent exact-rational solve, rank 5/5 reproduces, and the `large`
   out-of-sample prediction holds. See finding 20 and `.memory/03-measurement.md`.

   **The bug is invisible to memory safety — both guards, and both at once.**
   `m_nofull_msonly`, `m_noempty_msonly` and both-deleted all verify **9/0** with
   the functional spec stripped, against five positive controls that correctly
   fail. Second instance of finding 19, on a **container** rather than an index:
   drop the fullness check and a push overwrites the oldest element with **no OOB
   access at all**.
   ⚠ **But the published characterisation is too specific, twice.** *"The relation
   between the cursors is exactly the part of the state the obligation does not
   need"* is true and **is not a characterisation** — reading `ring[tail]` instead
   of `ring[head]`, memory-safe and functionally wrong with **no guard touched**,
   also verifies 9/0. **The memory-safety-only configuration is blind to every
   functional change.** ⚠ **And it is not about the modulus**: delete `%` entirely
   and wrap with a source branch under the guard, and the obligation is *still*
   two independent one-variable clauses and the bug *still* invisible. **The
   property is that the index bound is the array's own fixed capacity.**

   Sound and unchanged: R4 ≡ R5 `exact`, R5 **9/0 first try, no lemma**; TCB 10/5
   matching the gate; `p1_weak_requires` caught **only** by the twin; pair
   interval **degenerate** (the opposite of p03, because the clamp seeds a fact
   LLVM already has); R1's wrong answer **reproducible** across 880 runs; and the
   `ns` figures **survive a real 30-layout population** the delivery had declined
   to build (`+25.1…+26.0%` / `+9.3…+10.2%`, `P(A>B) = 100%`).
   `R2 − R3 = 20.00000·ops + 11` is p03's law exactly — and the **boundary is
   named**: it reproduces for the **opcode stream** (identical 5-byte record) and
   not for the **container** (p03's pop guard supplies only a lower bound, p04's
   `%` supplies both cursors' upper bounds unconditionally).

24. **Two defects in my own infrastructure, both found by a pattern task.**
   **(a) `.memory/00-environment.md` constraint 6's documented sweep rule was
   destructive and never described the sweep that ran.** *"delete the non-`text/*`
   ones"* deletes every `.json` — `file` reports JSON as `application/json` — so
   it would delete **every gate record it is pointed at**. The actual 2026-08-18
   script used a **deny-list** of six binary mime types; documentation and
   execution had diverged. Replaced with a keep-list by extension, which cannot
   fail open. It cost p04's engineer three evidence files.
   **(b) `common/layout/order.py` appends `.bin`**, so `--input small.bin` times
   `small.bin.bin`, every rung measures process startup, and `R2 − R4` reads
   **+0.15%** — a clean publishable-looking null from a file that does not exist,
   exit 3. **Caught only by cross-checking the `Ir` column**, which is now the
   rule: +141% `Ir` against a +0.15% `ns` null is not a conversion factor, it is a
   broken measurement.

25. **p13 — a bound the optimiser can SEE is worth more than the check costs;
   and a contract that pinned one side of its own comparison.** (TASK_043,
   reviewed at TASK_045_REVIEW, corrected at TASK_046: **three blockers, six
   majors, and six more manager prescriptions refuted while landing them.**
   ⚠ **The headline's sign, magnitude and stated mechanism ALL moved.**)
   `strncpy` truncation — the first bug here that is a **correctly-called library
   function** rather than an omitted line, and the first whose **harm lands at a
   different site from the bug**.

   **The corrected mechanism, and it is a better result than the published one.**
   p13 shipped the safe-beats-unsafe gap as *"R3 gets `memcpy`/`memset`, R4 has
   byte loops"*. **R4 makes the same two library calls at the same cost.** 72%
   (`small`) and 90% (`large`)  ⚠ *(this read `91%`; `.memory/01-ladder.md` is the authoritative file and says `90%` — corrected at TASK_111, which found the two disagreeing)* of the gap is the **consumer scan**, and its
   direction is the reverse of the published one: **a consumer whose bound LLVM
   can see fully unrolls to 2 Ir/byte; an unbounded walk stays a 4-instruction
   loop at 4** — `+2.00000` Ir per consumed byte at matched spelling.
   ⚠ **The discriminator is the BOUND, not the check**: an *unchecked but
   bounded* scan costs exactly what safe `position()` costs, to the instruction.
   A bounds check is one way of supplying the bound and is not what is paid for.
   **This is p03's
   and p04's seeding result from the other direction** — there the invariant had
   to be handed to LLVM as dead code; here the safety check supplies it as a side
   effect and more than pays for itself.

   ⚠ **The margin was inflated by p13's own contract, and this is the DIRECTION
   TEST's first fire.** `spec.md` pinned the byte-loop copy and fill in
   `unsafe.rs`/`verus.rs` and **exempted `safe_tuned.rs` by name** — only the
   safe rung could use the winning spelling. An admissible bulk R4 exists and
   verifies (`copy_nonoverlapping` + `write_bytes`, **17/0, twin 24/0**,
   `identity: exact`, TCB 5→7): the pin was worth **52% (small) / 16% (large)**
   of the margin. ⚠ **AND THE SIGN DOES NOT SURVIVE.** Allow R4 a
   *bounded* unchecked consumer — which verifies **19/0, twin 22/0, with no new
   trusted items**, excluded by nothing but `spec.md`'s English — and
   `R3ship − R4` is **+44.00 / +77.00**. **p13's "safe beats unsafe" is the price
   of a bound, and it reverses the moment the unsafe rung is allowed one.**
   Three numbers ship: fixed-R4 **−177 / −1054**, cheapest-found **−85 / −885**,
   and **+44 / +77** once the fiat goes.
   ⚠ **A scoped entry is not automatically a thumb.** p13 had three and measuring
   each gave three answers: copy/fill was a thumb (relaxed), `position()` is
   excluded by vstd one layer down (kept, free), the consumer *bound* is pure
   fiat (kept and **priced**). Price every scoped entry; publish the price beside
   the number it protects.
   ⚠ **p13 blamed the prover for the unsearched R4 side and the prover did not
   bind.** The R4-is-chained-to-the-prover mechanism (finding 14) is real and is
   now also **the most available wrong explanation here.** Run `verus_run.py`
   before invoking it.

   ⚠ **Two published figures move because the kernel-exclusive column is not
   comparable across p13's rungs** — the first pattern whose rungs call
   *different* libc routines. On the corrected tree the gcc-vs-clang `small` gap
   reads **1769** on the kernel column and **1463** on totals, and `R2 − R4`
   goes **+33.34%/+28.98% → +25.59%/+24.93%** — the difference being `memcpy`'s
   190/264 Ir/call **exactly**, which R2 never calls and R4 does. See `.memory/03-measurement.md`.
   ⚠ **And C's whole advantage is a LIBRARY difference**: every C `-O3` cell
   calls glibc `strlen` for the consumer and no Rust cell does. With clang
   `-fno-builtin-strlen`, **the sign of every same-backend C-vs-Rust row flips**.
   Consequence for the gate: `strlen(` is `forbidden`, absent from every source,
   audited at **0 hits**, and in every C object — **a text pin binds the source,
   not the object.** Across every pattern in the tree, **p13 is the only one where the
   optimiser reintroduces a forbidden spelling** (8 of 16 objects; p12 0 of 16).
   ⚠ That audit is only right **scoped to `kernel` + `main`** — unscoped it flags
   p12 too, because `std::env`, the backtrace machinery and `io::Error`'s
   `Display` call `strlen` in every Rust binary of every pattern.

   Sound: Verus **19/0** (twin **22/0**), `R4 ≡ R5 exact`, TCB 5 = the gate's own
   count, Miri 9/9. ⚠ **Said `17/0 first attempt` until TASK_058** — the delivery
   counts, superseded by TASK_046's fold repair; the pins are 19 and 22. The **termination store is `1.00000` Ir per string on both
   compilers** and is *not* DSE'd, because the fill's extent is a runtime value —
   I predicted DSE and was wrong. **`strlcpy` is dearer than `strncpy` and
   `snprintf` far dearer, on both compilers: the unsafe routine is the cheapest.**
   The two harms **separate by rung, not by input** — an adversarial row that
   truncates while every rung stays memory-safe is **unsatisfiable**, because
   content lost ⟺ no NUL in `dst` ⟺ R1 reads OOB.
   **No cost law**: `strncpy` lowers to size-dispatched vector code, every
   natural step basis is **singular** on a length-homogeneous fit set, and the
   "no law" residuals are **estimator-dependent by 3×**. Its out-of-sample band
   **could not fail, provably** — see finding 20 and the new
   `.memory/03-measurement.md` rule: hold out a **length**, not a **mixture**.

26. **p06 — the `Ir` column is SIGN-WRONG, and the deterministic metric is the
   one that misleads.** (TASK_047, reviewed at TASK_047_REVIEW — **2 blockers,
   3 majors, 5 minors and 14 clean negatives** — corrected at TASK_048.
   Authoritative version: `.memory/01-ladder.md` **finding 15**.)

   An in-place rotate by three reverses over a fixed `[u8; 64]` scratch; the
   omitted line is `r %= m`. It was built to make `Ir` *understate* a safety tax,
   because a `div` is **1.00 `Ir` and ~20–40 cycles**. It does worse: **on clang
   the hardened rung executes 45–108 FEWER instructions and runs 10–20% SLOWER.**
   An `and` control with no divide isolates the mechanism at −12.00 Ir/record —
   reducing `r` proves `r < 64`, the value stays 32-bit, and clang's
   7-instruction LE decode collapses to one `mov`. **Finding 6 finally has a
   designed instance with a named mechanism instead of an accident.**

   **The best thing in the cycle is a clean negative.** The review did not argue
   about the missing layout population — it **built** it (30 layouts/cell, both
   `%32` residues, every loop's `win32`/`jcc32` flips) and the headline survived:
   **`P(A>B) = 900/900`**, both compilers, both inputs, mode-matched, no sign
   flip. A `d_cmp` control puts **91.6% of gcc's +88.08 ns on the divide**. The
   manager's arithmetic objection to the headline was **wrong** — it divided by
   the probe's `+1.00 Ir/record` instead of the shipped law's `+8.00`.

   ⚠ **And 23% of that `+8.00·nrec` law is EXECUTED ALIGNMENT PADDING**, with
   only 1.000 of it the divide. `.memory/03-measurement.md`'s padding trap was
   static-only until now; it happened **twice on this one pattern**.

   **Two blockers, both about publishing a point as though it were a class.**
   The shipped R3 is `2.00000 Ir/byte`; an in-contract zero-`unsafe` control is
   **0.00000 Ir/byte**, and **none of the 2.00 is a bounds check** — it is the
   `zip`/`Rev` adaptor's exhaustion tests, with identical panic pads. **Fourth
   pattern to make this mistake, and finding 3 needed no correction: it says
   quote the cheaper of two in-contract R3 spellings, and p06 did not.** The
   second blocker removed a trusted item at zero `-O3` cost (**TCB 6 → 5,
   18/0, twin 23/0**) — but **not** free at `-O0`, where the gate caught
   `identity` dropping to `differ`.

   **p17's limit, arriving on a WRITE.** For `m < r ≤ SCR` (**not** `r ≥ SCR`)
   the unreduced rotate stays inside the scratch and C, safe Rust, unsafe Rust
   and the proved rung **all print the same wrong answer**, ASan and UBSan clean
   — including three delete-the-check controls, one with zero `unsafe`.

   **`_msonly` cannot separate the regimes, and the reason generalises**:
   deleting the check *and* weakening the spec to memory-safety-only **still
   fails**, because a proof quantifies over all inputs and regime 2 is genuinely
   unsafe. **The separation needs a program change, not a spec change** — p17's
   control-2 lesson, second instance.

   **Two parameter-free laws**, both exact: `swaps(m,r) = m + [m even AND r odd]`
   (so the rotate amount **does** enter the cost — the manager predicted no `r`
   term), and the per-record law at period **4, not 8**, exact on 45/45.

   ⚠ **"The twin is the sole catcher" was false on SIX patterns**, not two —
   see the audit note in the queue. **All six are now fixed** (p06 and p12
   first, then p03, p04, p05, p11 and p18 at TASK_054/056, each naming the task
   in its own `NOTES.md`). ⚠ This line said the last five were *not* fixed and
   the queue section said they were; TASK_058 caught the contradiction and the
   queue was right.

   ⚠ **p06's floor is ±4.6%, not the ±3% it published** (TASK_049_REVIEW).
   Headline intact — the clang column clears it at ~2.1×.

27. **p14 — an EXACT law, fitted entirely where the guard never fires.**
   (TASK_049, reviewed at TASK_049_REVIEW — **2 blockers, 3 majors, 4 minors,
   17 clean negatives** — corrected at TASK_050. Authoritative:
   `.memory/01-ladder.md` **finding 16**.)

   A CSV-style field split into a fixed descriptor table; the bound is
   `nt < MAXTOK`, **the first bound here that is a count of a byte value rather
   than a length.**

   **Its task made settling the bug class the FIRST deliverable, and the
   engineer rejected all four candidates it was handed** — the manager's three
   and the catalogue's — and shipped a fifth. **Fourth pattern to overturn its
   own catalogue row.** The lifetime candidate, which would have been the
   ladder's first, is *not observably wrong at `-O3`* on either compiler (p08
   exactly) and its pointer descriptors leave R4 unprovable.

   **The result is a methodology result.** `c-gcc-h − c-gcc = 1.00·bytes +
   2.00·fields − 3.00` is **exact — max residual 0.0000 over 66 blobs** — and
   **contains zero fitted inputs where the guard fires**. On the inputs p14
   exists to model it inverts: **−551, −823, −611** against +93, +93, +429.
   **The manager wanted that as the headline *"hardening is cheaper than the
   bug"*; the engineer refused it and was right** — past the cap the two cells
   compute different functions, the unhardened rung is already committing UB,
   and on one blob its `c-clang` cell **is not a function of its arguments**
   (`r₂…r₅ = 0`, marginal 17.982 `Ir` for 168 folded fields). Ships as **the law
   with its domain**, and **behaviour, not cost, outside it.**
   ⚠ **The project already keeps that rule structurally**: `measure.py`'s
   `CG_PLAN` is six entries, all `small.bin`/`large.bin`, so **no published `Ir`
   figure anywhere is measured on a bug-triggering input.** p14 would have been
   the first exception.

   ⚠ **Its leave-one-length-out cannot fail** (exact fit, rank 4 survives
   dropping any band) — p13's mistake in a new costume. ⚠ **And the R4/R5 pair
   is not a null control**; see the START HERE box.

   Sound: **19/0** (twin 23/0), `R4 ≡ R5 exact` / `norel`, **Miri 8/8**,
   **TCB 6 = 4 U-license + 2 infra** — TASK_048's classification's first use on
   a new pattern, and it survived review.

28. **p18 — UB that is not memory-unsafety, and four catchers all outside the
   measured matrix.** (TASK_051, reviewed at TASK_051_REVIEW — **1 blocker,
   7 majors, 5 minors, 15 clean negatives** — corrected at TASK_052.
   Authoritative: `.memory/01-ladder.md` **finding 17**.)

   A LEB128 varint decoder with the shift bound removed. **The first bug here
   that is UB but not a memory-safety bug**: it touches no memory and **ASan is
   silent**. §0 **upheld the catalogue's guess — the first row in five patterns
   to survive it.**

   **Four things catch it — UBSan, `-C debug-assertions`, Miri and Verus — and
   every one is outside the 24-cell matrix.** The manager published *"ASan, Miri
   and a proof are all blind"* and was wrong on two of three. ⚠ **Miri catches it
   as a PANIC, not a `Undefined Behavior` report**, so a gate keying on the `ub`
   flag alone calls it clean.

   **The row it exists for:** safe Rust with the guard deleted — **zero
   `unsafe`** — at `-O3 -C debug-assertions=off` is **bit-identical to C's R1 on
   every adversarial blob**.

   **`R1h − R1 = 2.00·bytes`, zero fitted parameters, and it does not
   amortise** — 11.89% of `small`'s kernel `Ir` *and* 11.11% of `large`'s.
   p07's never-amortises result on a new axis.

   ⚠ **`-C debug-assertions=on` also re-enables `assert_unsafe_precondition!`
   inside `get_unchecked`, and 15 of 16 R4s rest on it.** The manager's reading
   (*"R4's advantage over R2 vanishes"*) was **refuted** — true on p18 and p01,
   **false on p16**. What holds on 3 of 3: **at `-O3` with debug-assertions on,
   R4 becomes dearer than R3.**

   ⚠ **"Verus catches this bug" is spelling-conditional** — `wrapping_shl`
   verifies. **And the sanitizer catches the undefinedness, not the wrongness**:
   a *defined* `<< (shift & 63)` control has R1's cost law and R1's wrong answer
   with UBSan silent.

   **Two infrastructure results.** Its blocker — an exact law with an unstated
   domain, falsified by a **committed matrix input** — produced
   `.memory/03-measurement.md`'s domain rule and **the first out-of-sample test
   here that could have failed and did not** (additivity extrapolation: fit where
   two parameters never co-occur, predict where both fire; 40 predictions, worst
   error 0.0228). And it closed a **demonstrated gate hole** — `check.py`'s Miri
   stage never compared exit code or stdout when `expected_exit != 0` — with a
   committed regression check. **A second hole of the same shape is open.**

29. **p10 — the safe rung beats the unsafe one, and none of it is safety.**
   (TASK_057, reviewed at TASK_057_REVIEW — **1 blocker, 5 majors, 5 minors,
   21 clean negatives** — corrected at TASK_059. Authoritative:
   `.memory/01-ladder.md` **finding 18**.)

   A weighted FIR stencil; **the first kernel here with more than one indexed
   read per iteration** at a fixed offset from the cursor. Bug class **upheld**,
   second of six settled.

   **Safety's own cost is a two-part answer, not a number: `0.00` `Ir` per
   VECTORISED tap and `+3.00` per SCALAR-EPILOGUE tap.** And the `+3.00` is not
   *"the check costs 3"* — R2 spends **5** instructions on two bounds checks and
   **saves 2**, because indexed addressing off one induction variable replaces
   the unsafe rung's three pointer bumps.

   ⚠ **Its headline was wrong in the FLATTERING direction and the corrected one
   is bigger.** It shipped as `R3 − R4 = −323/−603`, *"safe Rust cheaper than
   unsafe"*, blamed on panic pads. Pads can only explain the per-tap coefficient
   and that coefficient is **0.00**. **60% of the margin was R4 spelling** — the
   rejected candidate verifies once one invariant clause is added — and the rest
   is **index-expression bookkeeping in any language**: `c-clang`, with the same
   index expression as the unsafe rung, is **dearer than both Rust rungs**, and
   there is no bounds check in any of the three. **Safe Rust beats every LLVM
   cell and does not beat gcc on `large`. Quote the backend and the blob.**

   **Three transferable results, all in `.memory/03-measurement.md`.** A law
   fitted in one **inline mode** is not the law in the other — `nout` and
   `scaltap` **swap roles** between `isolated` and `whole`, both fits rank-full
   and exact. An **`identity: exact` pin excludes every candidate R4 carrying a
   panic pad**, which bounds the R4 search space on *every* pattern. And p18's
   domain rule reproduced on an **eighth** pattern, with the diagnostic
   quantified: the old columns refitted over all rows go to residuals **9.19 …
   1606.73**, which a caveat would have hidden.

30. **p27 — the first TEMPORAL bug, and the lifetime guarantee costs ZERO.**
   (TASK_060, reviewed at TASK_060_REVIEW — **no blocker**, 3 majors, 8 minors,
   **28 clean negatives** — corrected at TASK_061. Authoritative:
   `.memory/01-ladder.md` **finding 19**.)

   A handle table over **per-record `malloc`/`free`**; R1 omits one conjunct on
   the READ path and dereferences a freed record. Every other bug here is
   spatial or logical; this is the class safe Rust rejects at **compile** time.

   **`R3 − R4 = +230.07 / +792.75` and NONE of it is temporal safety.** A
   decomposition closed over *every* function — not four chosen ones — gives
   `230.07 = 109.65 kernel + 120.42 drop glue + 0.00 allocator`, with `malloc`,
   `free`, `_int_malloc`, `_int_free` and all three `__rust_*` **equal to the
   last digit** between the rungs. And the spatial tax runs backwards: an R4
   that *keeps* R3's bounds checks costs **+153.51** against R3's **+109.65**,
   so **safe Rust pays 43.86 LESS of it**. The rest is drop glue.

   > **The lifetime guarantee's cost is zero and its shape is structural: the
   > free and the invalidation are ONE operation in safe Rust and TWO in C, and
   > the bug is neither of them going wrong — it is the THIRD, the *asking*,
   > going missing.**

   ⚠ **Two predictions this file carried for weeks were both wrong.** Safe Rust
   is **not** forced onto `(slot, generation)` — the handle comes out of a
   **file**, so it is an integer in every rung, and safe Rust is forced onto
   `Option<Box<u8>>`, niche-optimised into the hardened-C representation
   (verified on the shipped binary). And `tcb_items` is **7**, not the 2 this
   file called the prospective gameability alarm: right in substance (the
   allocation adds **zero** project-local axioms), wrong in its number.
   **TCB 7 is forced, not chosen** — `identity: exact` is an **18-of-18**
   invariant and the minimal-TCB variant's R4/R5 pair is `differ`.

   **Two methodological results, both in `.memory/`.** The **verified twin
   works and both its legs are load-bearing** — four weakenings caught at twin
   19/1, and the one-sided case caught **structurally** by signature equality
   where Verus verifies it 20/0. And the **direction test was verified
   byte-exactly for the first time**: the pre-build contract reconstructed from
   the disclosed edits alone reproduces the recorded hash, and no single edit
   does.

31. **p47 — the proof certifies a LEAKING kernel and its obligation count does
   not move.** (TASK_064, reviewed at TASK_064_REVIEW — 3 majors, 6 minors,
   **32 clean negatives** — corrected at TASK_065. Authoritative:
   `.memory/01-ladder.md` **finding 20**.)

   Constant-time compare, and the first pattern whose security property the
   ladder is structurally unable to measure. `m_leak` is `verus.rs` plus an early
   exit: **14 verified, 0 errors**, `kernel`'s obligation count **unchanged at
   3**, identical checksums on all 32 cells, **+7088.000 `Ir`** of leak.

   ⚠ **The precise reason is stronger than "Verus can't see timing".** The diff
   touches **no `requires` and no `ensures`** — the contracts are **identical**,
   and the shipped proof is a *strictly stronger intermediate* under the same
   contract. **A property of the TRACE is invisible to a logic about the VALUE**,
   and both numbers this project publishes for proof burden are blind to it.

   **`Ir` under callgrind IS the side channel** — the only pattern here whose
   primary metric is literally the harm. Spread in first-mismatch position:
   **184.000** for C, hardened C and safe Rust's `==`; **0.000** for every
   constant-time rung, identical at both inline modes.

   ⚠ **Catalogue bug class REFUTED — third overturned against two upheld.** The
   optimiser never reintroduces the branch, across LTO, PGO trained 100% on
   mismatch-at-byte-0, AVX2, AVX-512, `__builtin_expect` and a branching caller.
   **The adversary is the idiom, not the optimiser** — so `volatile` buys nothing
   and costs **6.75× / 9.68×**, inverting the standard advice.

32. **p38 — the harm is a MISCOMPILE, and the undefined spelling is the DEAREST
   of its neighbours.** A parser clamps an over-long record length in place and
   re-reads it through a punning `uint32_t` lvalue; gcc takes the trip count from
   the load *before* the clamp's two `uint16_t` stores and never reloads. `-O3`
   reads past a 256-entry array, `-O0` is correct, ASan says
   `stack-buffer-overflow READ of size 2`, and **`-fno-strict-aliasing` makes it
   vanish**. Reviewed: **no blocker**, 3 majors, 8 minors, **35 clean negatives**.

   ⚠ **It ships labelled a DEMONSTRATION KERNEL and that is the honest label.**
   Four conjunctive conditions, and **six neighbouring one-line spellings each
   remove the harm**. ✅ **The quotable result is the PRICE: on gcc the undefined
   spelling is the dearest of the six — every fix saves exactly 6.00 `Ir`/call.**
   The UB buys nothing and costs 6, so **no optimising programmer arrives here**.

   **The first bug class in the tree that UNSAFE Rust does not reintroduce** —
   Rust has no type-based aliasing rule at any rung. And *"clang is safe"* is
   false: with an offset opaque on **one side only**, clang exploits it from
   `-O1`.

   ⚠ **The R4 side is disclosed but not established, and it flatters SAFE** —
   published `+21/+25` against a true `+24/+32`. **p10's defect in kind**, at
   14%/28% of the headline.

   ⚠ **The project's first additivity-extrapolation failure — and it was 100%
   ATTRIBUTABLE.** Not to the `nw` column everyone named (`R2 − R4` is exactly
   constant in it; adding it makes out-of-sample *worse*), but to three others:
   `rlen` parity, **`nw mod 8`**, and `rlen == 1` as a law term. Repaired laws
   have **zero free parameters and 0.00000 max residual over 106 rows**.
   **The rule that generalises: check the RESIDUE CLASS of any parameter your
   bands hold constant** — two of p38's three bands sat at `nw ≡ 0 (mod 8)` and
   the third did not, which is exactly the configuration that fits in sample and
   misses out of it.

33. **p22 — the first pattern where SAFE RUST DOES NOT HELP.** An open-addressing
   probe loop that never terminates on a full table: **memory-safe, ASan and
   UBSan silent, Miri silent for 90 s.** No bounds check, no lifetime, no
   `unsafe` to point at — **the safe rungs are not better.** Only R5 sees it.
   Reviewed: 1 blocker, 3 majors, 4 minors, **54 named attacks**.

   ⚠ **Narrowed in §0, and the narrowing is the honest part.** No-guard variants
   of R2/R3/R4 all hang, but `for _ in 0..TABCAP` is idiomatic and terminates —
   so the claim is *"nothing on this ladder **emits** the capacity check; five
   rungs write it by hand"*. ✅ The review checked whether that rests on p22's own
   contract: **it does not** — the bounded spelling is measurably a **different
   function** (differs on the adversarial input, agrees on the other seven).

   ⚠ **"The first termination proof in the project" was FALSE, came from the
   MANAGER's task file, and shipped in eight places — two inside
   `contract_sha256`.** Verus demands a `decreases` on **every** exec loop, so
   there were 72 prior obligations. The counted replacement: **the tree's only
   exec-loop measure not expressible in the loop's own exec variables — 1 of
   73.** ⚠ In both files **the true sentence already sat beside the false one.**

   **The measure costs ZERO instructions** (all ghost, so `R4 ≡ R5` stays
   `exact`) — but the exec-code alternative is **334 `Ir`/call cheaper**, so the
   ghost proof does not *save* anything; it buys R4 and R5 being the same
   program. ⚠ **The bounded probe is faster too**, so *"the careful programmer
   pays for the bound"* is false here.

   ⚠ **Fifth consecutive under-searched R4 side, and it flatters SAFE**:
   published `+2.00` against `+125/+1021` — **510×** on the large band. Disclosed
   proactively this time.

34. **p36 — the prover excludes the MECHANISM, not a spelling; and the
   kernel-exclusive column hid an entire callee.** (TASK_072, reviewed at
   TASK_072_REVIEW: **2 blockers, 5 majors, 7 minors, 36 named clean
   negatives**; corrected at TASK_073, which refuted **three** prescriptions —
   two the manager's and one the review's.) A dispatch table with no
   `op < NOPS` check. ⚠ **The bug class is the tree's TWELFTH `index >= len`
   and the pattern says so up front** — everything below is what is not twelfth.

   **Verus at the pin cannot type `fn(u64) -> u64` at all** — the error is on the
   **declaration**, not the call — and the `identity` pin makes an R4 a program
   that must have a verifying R5 twin, so **C's own dispatch mechanism has no
   admissible Rust rung.** The four Rust rungs use `[&'static dyn Op; NOPS]`,
   and the difference is **priced, not waved at: exactly `3.00000` `Ir` per
   dispatch**, same intercept, zero residual over twelve swept points, with a
   **zero-fitted-parameter mechanism** off the two listings. ⚠ **Finding 14's
   prior instances exclude a SPELLING; this one excludes a MECHANISM**, and it
   is the one result here that survived both blockers untouched.

   ⚠ **Both published headlines moved.** `R3 − R4 = +15.00 flat` was fitted
   against an **R3 side with one lever, which moved R3 the wrong way**; p36 now
   publishes **`+7.00` (fixed-R4 bound, cheapest R3 found)** and **`+10.00`
   (matched pair)**, never one number and **no pair interval** — the interval
   reads `−1015 … +537`, i.e. *"safe beats unsafe by 1015"*, the exact artefact
   the search existed to prevent. And **every `Ir` was kernel-exclusive on the
   one pattern whose kernel IS a call**: dispatch targets run **512 (gcc) / 384
   (clang, rustc) / 0 (the `match` control, which inlines all eight arms)**, which
   **reverses** `match` from dearer to cheaper — *and "it is DEARER" was quoted
   inside the HASHED `idiom.why` as the reason it was forbidden* — and vanishes
   the gcc-vs-clang C gap (10 vs 11 → 14 vs 14).

   ⚠ **The `endbr64` finding is bigger than p36**: gcc defaults to
   `-fcf-protection=full`, so **this project has been pricing a CFI mitigation
   all along, at `1.00000·nrw + 1` `Ir` per call, in gcc's column only, and never
   said so.** Manager-verified. See `.memory/03-measurement.md`.

   **`Ir` exactly constant while wall clock moves 3.13×** — one binary, verified
   on **program totals** too. ⚠ **Not p07's finding in a costume**: p07's `Ir`
   *moves* and its branch is conditional; p36's is exactly constant and its
   branch is indirect, **and the novel content is about the INSTRUMENT** —
   callgrind's `Bi` counts, its `Bim` does **not** predict, and on p36 it is
   wrong in *direction* (see `.memory/00-environment.md` rule 4).

   **Catchers name the ARRAY READ, never the call**: ASan `global-buffer-overflow`
   and UBSan `index 8 out of bounds`; `-fsanitize=function` is **absent in gcc
   13.3 and defeated here under clang**; only `-fsanitize=cfi-icall` names the
   transfer, and it needs `-flto` + `-fuse-ld=lld`, so it is a control, not a
   rung. ✅ **Clean negative worth keeping**: there is **no** input where the read
   is in bounds and the call is wrong, so the sanitizers and CFI fire on
   **identical input sets** — CFI adds *vocabulary*, not *coverage*.

   ⚠ **And a scope clause on finding 1, the project's number-one result.** R5's
   vtables are **40 bytes to R4's 32**, and slot 4 of all eight points at one
   emitted **26-byte `spec_apply`** stub. A proof still costs **zero executed
   instructions and zero in the kernel symbol** — but *"ghost code fully erases"*
   and *"the proven binary is byte-identical"* are **false** for a `spec fn`
   declared in a **trait**, and its declaration position is part of the vtable
   ABI. Manager-verified before landing.

35. **p19 — safe Rust's bounds check and the C validation pass are the SAME
    PREDICATE at DIFFERENT ASYMPTOTICS, and that produces a sign flip with no
    safety content in it.** ⚠ **This finding is 45 tasks late: p19 was built at
    TASK_087 and reviewed, and was mentioned ZERO times in this section until
    TASK_100-time.**

    LLVM proves the identity for us. The `panic_bounds_check` call's length
    argument is the literal `0x800` = 2048 = `tbl.len()`, so the branch is
    provably the `tbl[…]` slice check, and it is lowered to **`cmp $0x8`** — a
    **state-range test, not an index test**, compared on `st` *before* the index
    `st<<8|b` is built. The C validation pass in the same function emits
    `cmpb $0x7,…; ja` ×4. **The same predicate, enforced once per access versus
    once per call.**

    ⚠⚠ **The asymptotics differ, so the sign of "C versus Rust" depends on the
    input and nothing else.** Validation is `O(table)` once per call; the bounds
    check is `O(message)`. The *buggy* C rung is **5071 `Ir`/call cheaper than
    unsafe Rust at `small` (m=256) and 3569 dearer at `large` (m=4096)** —
    `2.25·m − 5647`, zero at **m ≈ 2509.4**. **A percentage quoted at either
    input is wrong in SIGN at the other.**

    **Rates, `-O3`, inline mode `isolated`, disassembly `body_len / K`** (⚠ **NOT
    marginals** — see the caveat below): R2 **15.00000** `Ir`/message byte (**not
    unrolled**, 15 instrs / 1 byte) · R3 **9.75000** · R4 = R5 **8.75000** ·
    `c-gcc` 11.00000 · `c-clang` 8.75000. The gate's independent whole-program
    marginals reproduce them to five decimals (15.0000781 / 9.7500781 /
    8.7500781 / 11.0001875 / 8.7501875), the excess being the driver's
    `println!` term ÷ 3840 bytes.

    **The mechanism, which is worth more than the rates:
    `R2 − R4 = 6.25 = 3.00 check + 3.25 FORECLOSED 4× UNROLL`.** Rolled-vs-rolled
    (`-C llvm-args=-unroll-count=1`, no source change) gives R2 15 / R3 13 / R4
    12 instrs per byte, and the three rolled instructions are `cmp $0x8` + `jae`
    **plus one `mov %rdx,%rax`** — ⚠⚠ **the checked spelling must keep `st` live
    for the compare and cannot destroy it with the shift. Register pressure
    created by a bounds check is a per-byte cost this project had not priced
    before.** And `R3 − R4 = 1.00000` is **exactly one `and $0x7,%edi` per
    byte**, attributed three independent ways (rolled control; adding the mask to
    the *unsafe* rung costs `+1.00024`; and R3's fold contains exactly four
    `and $0x7,%edi` against 39 − 35 = 4).

    **The hardened-C column is a CONSTANT, and it is checked as one:** predicted
    2048 × 5.00 = 10240 (gcc, rolled) and 2048 × 2.75 = 5632 (clang); measured
    `+10242` and `+5637`, **identical at both inputs and exactly constant across
    all 19 sweep lengths m = 64…5001**. That invariance across m *is* the claim
    "a constant, not a slope" — it is not asserted, it is the measurement.

    **Two exact sweep laws, and ⚠ THE ORIGINALS WERE WRONG AND SHIPPED:**
    ```
    R2 − R4 = 6.25·m − 6 − 2.25·(m mod 4) − 4·[m mod 4 ≠ 0]
    R3 − R4 = 1.00·m + 4                  − 1·[m mod 4 ≠ 0]
    ```
    re-fitted at TASK_088 over 19 committed blobs with zero residual, replacing
    the shipped `6.25m − 8` and `1.00m − 2` — which **contradicted `NOTES.md`'s
    own printed marginals two sections above them.** ⚠⚠ **The cause was TWO
    independent things and only one was diagnosed by the review: a fixed
    per-program offset of exactly `+2`/`+6` at all ten `m ≡ 0 (mod 4)` points,
    because the probe was A DIFFERENT BINARY and only the SLOPE transfers, PLUS
    the residue term. The offset is invisible to a residue-covering band** — a
    second failure mode stacked on the one p38 taught.

    **Both sides searched, and all three spans degenerate:** R2 3 levers span 12,
    R3 3 span 11, R4 3 span 13 `Ir`/call; the review added two further in-contract
    R2 spellings measuring exactly the shipped one (**five R2 spellings, all
    degenerate**). The rejected absolute-indexing R4 was put through Verus
    **first** (`8 verified, 0 errors`) and rejected **on cost, not
    admissibility** — the right order.

    **Proof: `12 verified, 0 errors`** (twin `13/0`), **3 TCB items, 1
    contracted, no `assume`, no `admit`, no hand-written axiom**; Miri 8/8 no UB.
    ⚠ **The obligation is a LOOP-CARRIED DATA INVARIANT and that is what is new:**
    `st < NST` holds not from arithmetic on a counter but because 2048 bytes read
    **at run time** were checked once before the loop. **`c/kernel.c` is this
    program with the validation pass deleted; the invariant then has no
    establishing step. There is no Verus spelling of `c/kernel.c` that verifies**
    — the deleted lines are the premise, not an optimisation Z3 declines.

    ⚠ **The review's own attack landed sideways and the honest reading is better
    than the claim.** p19's check *is* dead in the sense the attack meant —
    provably redundant on every input the benchmark presents, and
    `safe_naive.rs:13-18` says so itself. **What p19 prices is not a live check
    but the UNLEARNABILITY of a loop-carried data invariant: 6.25 `Ir`/byte for a
    fact Z3 discharges in ghost code and LLVM cannot.** That is finding 2 **with
    a mechanism**.

    **Harm — three blobs one byte apart** (byte [769]: 8 → 10 → 255), all three
    **silent at plain `gcc -O2` on 8 of 8 C cells**: entry 8 is ASan-**clean**
    (the read is inside the object); entry 10 gives `heap-buffer-overflow`, READ
    of size 1, naming the allocation site; entry 255 gives `SEGV on unknown
    address`, *"can not provide additional info"* — too far out for the shadow
    map. ⚠ **One attacker byte decides between no diagnostic, a diagnostic that
    names the object, and a diagnostic that can name nothing.**

    **Bug class: the THIRTEENTH `index >= len`**, nearest sibling p36. The
    framing is **conditional and both conditions are pinned `forbidden`
    entries**, settled by five runs before any cell existed: the table must be
    **loaded data** (a program-constant table makes the OOB unreachable) and
    dispatch must be by **indexing, not `switch`** (the same bad entry through a
    `switch` falls to `default` with ASan *and* UBSan silent — p31's death).
    Precedent, source fetched and manager-verified genuine: Linux
    `security/apparmor/match.c`, `aa_dfa_match_until()` indexing four tables with
    no test, licensed by `verify_dfa()` at load. **Validate-once-then-index-
    unchecked IS p19's R4/R5 rung.**

    ⚠⚠ **THREE THINGS THIS FINDING DELIBERATELY DOES NOT CLAIM.** *(1)* p19 is
    **not** the only pattern forbidding a spelling for being *safe* — **p36 and
    p03 already did**, and p36 is the sibling p19 names; p19 is the **third**.
    *(2)* The manager's *"p19 is the only pattern calling a vstd exec trusted
    function from its kernel"* was **refuted three ways** — the grep behind it
    was a whitelist of four slice-shaped names, **p27 calls `ptr_mut_write` and
    `ptr_ref`**, and the framing re-opened a decision `.memory/04-verus.md` had
    closed by a 402-site census that **named this exact case in advance**. The
    review's verdict was *"DO NOT LAND AS A FINDING"* and **it is honoured
    here.** *(3)* **No wall-clock analysis exists.** The fold is a serial
    dependent-load chain, so `Ir` should *understate* the safe rungs' penalty —
    ⚠ **that is a prediction, not a measurement.**

    ⚠ **PROVISIONAL where it rests on TASK_088**, which was never reviewed: the
    re-fitted laws and their two-cause decomposition, the CVE correction, and the
    harness changes p19 is gated under today. Evidence:
    `.tasks/TASK_087_REPORT.md`, `.tasks/TASK_087_REVIEW_REPORT.md`,
    `.tasks/TASK_088_REPORT.md`, `patterns/p19-state-machine/NOTES.md`.

36. **p46 — the safety tax is `0.00000` per MAC, `safe_naive < safe_tuned <
    unsafe`, and the pre-build probe that predicted `+5.05 Ir/MAC` was WRONG IN
    SIGN. The rung boundary did not shrink; it VANISHED.** ⚠ **Also 35 tasks
    late — p46 was the 24th pattern and had no finding until TASK_100-time.**

    In the shipped kernel `n = w[0]` and `m = w[1]` are `u8`-derived and
    `n + m <= OUTCAP` is tested, which is everything LLVM needs to discharge
    `i + j < 96` itself. **It deletes all three bounds checks** (`bl[j]`, the
    `out[i+j]` read, the `out[i+j]` write) and **the safe MAC loop contains no
    conditional branch but its own `jne`.** Kernel-exclusive `Ir`/call, `-O3
    isolated`, small (n=m=24) / large (48,48): `safe_naive` **6241 / 23341** ·
    `safe_tuned` 6287 / 23435 · `unsafe` = `verus` **6406 / 24250**.

    **So "safe beats unsafe" here is 100% AN UNROLL DECISION.** Rolled-vs-rolled,
    shipped sources unedited, both sides: **`R2 − R4 = +2.00000·n·m` exactly**
    over 5 shapes, zero residual — *against* safe Rust. Per instruction: safe
    pays `xor` + `setb` (materialising the carry) plus a separate store where
    unsafe folds the accumulator update into one `add %rax,(mem)`; unsafe pays
    one extra `adc $0x0,%rdx`. **Net +2, the measured coefficient exactly, and
    neither loop contains a bounds check.**

    ⚠⚠ **AND THE MECHANISM THE PROJECT FIRST PUBLISHED FOR THAT WAS ITSELF
    FALSE — a review blocker, and it was already in `.memory/`.** The build
    report blamed `black_box`. **Every probe kernel is `#[no_mangle]
    #[inline(never)] pub fn`, i.e. external linkage, so a caller-side
    `black_box` cannot reach the callee's codegen at all** — rebuilt with and
    without it the binaries are **byte-identical**. The real cause is one level
    up: **a probe whose kernel SIGNATURE differs from the shipped kernel's loses
    the range facts the shipped kernel derives from its input header.**
    ⚠ **The retraction cuts both ways** — an author who drops `black_box` *"so as
    not to hide range facts"* re-enables the constant folding it exists to
    prevent while the real cause goes unfixed. **`.memory/03-measurement.md`'s
    rule said a probe's INTERCEPT does not transfer; p46 shows the SLOPE need not
    either.**

    **Exact cost laws, whole-program marginal, `-O3 isolated`, domain `m >= 2`**
    (`controls/sweep_ir.py --check` re-derives them and **exits 1 on any
    residual**): `R5 − R4 = 0` (49 blobs + both matrix inputs) · `R2 − R4 = 3 +
    5n − n·floor(m/2)` · `R3 − R2 = 2n − 2` (m even) / `−2` (m odd) ·
    `R1h − R1` clang `+2.00` flat. ⚠ `m = 1` is **off the domain** and is stated
    as a restriction, not explained.

    ⚠⚠ **THE STRONGEST METHOD RESULT IN THE PATTERN, AND IT IS SHARPER THAN
    p38's MISSING COLUMN: A TWO-PARAMETER LAW FITTED ON TWO AXIS-ALIGNED BANDS IS
    NOT MERELY AT RISK OF A MISSING TERM — IT IS UNDERDETERMINED, AND NO
    IN-SAMPLE RESIDUAL CAN SHOW IT.** Fitting `A + B·n + C·floor(m/2) +
    D·n·floor(m/2)` on the two axis-aligned bands gives four equations of which
    only **three** are independent; the family `A = 291 + 288D, B = −7 − 12D,
    C = −24 − 24D` fits **both bands exactly for every D**. **One off-axis point
    pins `D = −1`, and the remaining nine band-D blobs then have zero residual
    out of sample.** ⚠ **Ship one off-axis point in every band, always.**

    **Harm: 6 of 8 plain C cells are SILENT WITH A WRONG ANSWER; 2 fault — and
    the discriminator is the FRAME ORDER OF TWO AUTOMATIC ARRAYS.** gcc `-O0`/
    `-O3` and clang `-O3` place `bl − out = +768 bytes = +96 limbs`, so
    **`out[96]` IS `bl[0]`** and the overflow lands inside the b-operand scratch:
    no fault, no canary, corrupted intermediate, exit 0. clang `-O0` reverses
    them. ⚠⚠ **This is p02's "absorbed by glibc chunk rounding" moved from the
    HEAP to the STACK, and it is why `-fstack-protector-strong` — on by default
    on this box — does not help: the canary is not what gets written.**
    Sanitizers see it either way (ASan `stack-buffer-overflow`, **WRITE** of size
    8, where p05's is a read). **The clamped control is exit 0 with ASan and
    UBSan both silent at three shapes — p31's death — which is why the clamp is
    `forbidden` in the hashed block.**

    **Proof: `21 verified, 0 errors`** (twin `24/0`), **5 `external_body` items,
    3 contracted, no `assume`, no `admit`, no `assume_specification`, no
    hand-written axiom**; Miri 7/7. Closed **first attempt, before any cell
    existed**, refuting the manager's *"may not close in one session"*. Deleting
    the three lines `if n + m > OUTCAP { return REJ; }` — i.e. **writing
    `c/kernel.c` in Verus** — gives `20 verified, 1 errors`, *"invariant not
    satisfied before loop"*. **There is no Verus spelling of `c/kernel.c` that
    verifies**, the second pattern to demonstrate it (see finding 35).

    ⚠ **What is new is the MODE, not the strength:** the **first `by
    (bit_vector)` and first `by (compute)` in executable position** in the tree
    (0 hits across the 23 prior `verus.rs`; all 10 other hits are comments, and
    **ten** patterns carry a comment saying they deliberately avoid
    `bit_vector`), plus the first kernel-level **nonlinear obligation about DATA
    rather than an address** — `lemma_mac_fits` proves `a*b + c + d <= u128::MAX`
    and it is **tight**: `(2^64−1)^2 + 2(2^64−1) == 2^128 − 1` exactly.

    > **p46 separates the proof-burden column from the instruction column inside
    > one kernel:** the expensive obligation has **no runtime counterpart in
    > either language at any rung**, while the free obligation (`i + j < OUTCAP`,
    > purely linear) is the one the rungs are about — **and LLVM deletes even
    > that.**

    ⚠ **NOT proved, disclosed in four places:** `bn_fold` specifies the
    schoolbook **algorithm**, not that it computes `a × b`. The gap is closed by
    **testing** (`model.py::_fold_bigint` does one Python big-integer multiply per
    window, gate-checked, 0 disagreements) — **not by proof.**

    ⚠⚠ **THE REVIEW'S SHARPEST CONTRIBUTION IS A PROTOCOL FINDING AND IT
    GENERALISES BEYOND p46:** *"The Rule 6 verification and the stale-contract
    defect are the same fact seen twice. The `why` really WAS frozen before any
    cell was built — **which is why it still described the pre-build probe's
    world. Rule 6 protects against a declaration edited AFTER measuring; it does
    NOTHING about a declaration that measurement has since FALSIFIED.**"*
    **p46 is the first pattern where that gap is demonstrated with a matching
    hash** — deleting the `unsafe_justifications` block and one trailing comma
    reproduces the recorded pre-build sha256 `e6b12dc6…` exactly.

    **Bug class: the FOURTEENTH `index >= len`**, nearest sibling **p05, of which
    p46 is the MIRROR** — p05's *index* arithmetic is nonlinear with trivial data
    arithmetic; p46's index is purely linear and **the nonlinearity is in the
    VALUE**. p05's OOB is a read; **p46's is a write.** Precedent: OpenSSL's
    `BN_mul()` calling `bn_wexpand(rr, top)` before `bn_mul_normal()` indexes
    with no test.

    ⚠⚠ **PROVISIONAL, AND THE HEADLINE'S GROUND MOVED AT TASK_092 (UNREVIEWED).**
    A review blocker refuted the *reason* p46 excluded the `r4_mutreslice`
    spelling — *"a mutable sub-slice at this pin is SOUND but VALUELESS"* was
    **false**, the `copy_from_slice` failure mode recurring: `std_specs/slice.rs`
    ships a full **value-level** `assume_specification` for `index_mut`, and the
    engineer had read `vstd/slice.rs`'s **trait declaration** instead. TASK_092
    then showed **its full R5 verifies, `21 verified, 0 errors`**. ⚠ **The
    conclusion survives on two different measured grounds** — it costs **two new
    trusted items** (`get_unchecked` has **0 hits anywhere in the pinned vstd**),
    taking TCB 5/3 → 7/5; and **its R4/R5 pair is `differ` at `-O3`**,
    `R5 − R4 = 15n + 1` exactly, against p46's pinned `identity: unsafe == verus,
    O3 exact`. ⚠⚠ **But the honest consequence must be stated: "both spans
    degenerate" SURVIVES and "safe beats unsafe" does NOT invert — yet the
    headline is now contingent on the IDENTITY PIN and the TCB, not on a
    specification gap. Relax either and it inverts**, since `r4_mutreslice` at
    5923 and even its R5 at 6284 sit below `safe_naive` 6453 and `safe_tuned`
    6499 at (24,24). **This is `.memory/01-ladder.md`'s first counterexample to
    "R4 and R5 compile the same"** — finding 1 itself is untouched, all 24
    shipped patterns still pin and measure `unsafe ≡ verus`. ⚠ **Why LLVM
    diverges on two textually identical exec bodies is NOT established.** Cite
    it; do not explain it.

    ⚠ **A blocker-class defect NO review caught, found by the manager at
    TASK_092: a ONE-SIDED FLAG MISMATCH.** `controls/mkvariants.py` omitted
    `-C codegen-units=1`, which `build.py::rust_flags` passes to every measured
    cell — **so every number in two NOTES sections was one-sided and 1–2
    `Ir`/call off.** ⚠⚠ **One-sided mismatches do NOT cancel; two-sided ones do**
    — the rolled control applied it to both sides and was unaffected, which is
    exactly why a *different* review minor about the same flag was harmless.
    Corrected, **the conclusion got STRONGER**: R4-side span 2 (published 3),
    R3-side span 0 (published 2), both still degenerate.

    Evidence: `.tasks/TASK_089_REPORT.md`, `.tasks/TASK_089_REVIEW_REPORT.md`,
    `.tasks/TASK_092_REPORT.md`, `patterns/p46-bignum-mac/NOTES.md`.

37. ⚠⚠ **DISPUTED — REVIEWED AT `TASK_113` AND THE HEADLINE DOES NOT SURVIVE.
    BOTH HALVES OF THE "IFF" FAIL.** ⚠ **The sentence below is preserved, not
    struck** (PROTOCOL rule 9: never strike on the strength of one pass; annotate
    and name the evidence on both sides). ⚠⚠ **DO NOT QUOTE IT. `SYNTHESIS.md`
    §5 carries the same claim and is disputed with it.**

    > **This benchmark can price a safety property IF AND ONLY IF some rung emits
    > it as a compare-and-branch and another rung omits it.** A property enforced
    > by **the type system**, by **a library contract**, by **an absent
    > operation**, by **a resource limit no rung emits**, or by **a compiler
    > diagnostic** has **no machine-code footprint at all** — and probe 2 says so
    > every single time.

    **What `TASK_113` measured against it:**

    - ⚠⚠ **THE ONLY-IF HALF IS FALSE, AND THE COUNTEREXAMPLE IS A BUILT PATTERN
      THIS FILE ALREADY PUBLISHES.** **`p38` prices a TYPE-BASED ALIASING
      property at exactly `6.00 Ir`/call**, five independent one-line fixes
      agreeing to the unit — `c_symset`, `c_once`, `c_nosa`, `c_memcpy`,
      `c_union` (`patterns/p38-alias-pun/NOTES.md:962-966`). **Not one is a
      compare or a branch; one of them is a COMPILER FLAG.** ⚠ **That is
      RECAP finding 32, published as `p38`'s quotable result — while
      `TASK_102_REPORT.md:522` files `p38` under *"what it CANNOT price"*.**
    - ⚠⚠ **THE COUNTEREXAMPLE IS ALSO INSIDE THE REPORT THAT MADE THE CLAIM.**
      `TASK_102_REPORT.md:578` lists *"`p06`'s division instead of a compare"*
      **64 lines after** `:513` asserts the fourteen are *"all
      compare-and-branch"*. **`p06`'s hardened C says it outright:** *"Every
      earlier pattern's hardened cell adds a compare and a branch. This one adds
      a hardware `div`."*
    - **The IF half is unsupported and non-diagnostic.** Two of the eight
      candidates SATISFY the antecedent and were refused anyway: **C3**
      (safe Rust emits `test %r9d,%r9d` / `je <panic>`, unsafe folds the divisor
      into `divl mem`; 28/28/25 insns, three distinct rungs — and `TASK_102`'s
      own report calls it *"the only candidate of the eight that passes probe
      2"*), and **B2** (gcc's default stack-clash probe has **2** `cmp …,%rsp`
      in `f_vla`; clang and `-fno-stack-clash-protection` have **0**).
      ⚠ **Zero of the eight support sufficiency, and where the antecedent IS
      satisfied the criterion does not say WHICH property the compare belongs
      to** — `p37`'s re-triage is the clean case.
    - **Two of the quote's own quantifiers are false.** *"Probe 2 says so every
      single time"* — probe 2 was the kill in **3 of 8**; the other five died on
      harm-matrix, compiler-diagnostic, ASLR, allocator-attribution and
      libc-version grounds, **none of which finding 37 mentions.** And *"no
      machine-code footprint at all"* is false on **the clang column** (C2 moves
      on all four pairs) and on **B1** (`+162 Ir`/call).
    - ⚠ **THE REFUSAL SET IS BIASED, and it is the same one-directional
      selection `TASK_111` found in the synthesis.** All eight candidates were
      chosen for **bug-class novelty** — the criterion this file's own admission
      bar says *"predicts neither way"*. **Zero were `index >= len`**, and
      **`p23`, the fifteenth `index >= len`, shipped finding 38** (⚠ **published at `3.11×`, corrected to `1.315×` at `TASK_117`; the result stands, the magnitude does not**).

    ✅ **CLEAN NEGATIVES — the refusals themselves mostly hold.** All three
    probe-2-based kills **reproduce** under `.temp/t104/probe2.py` (the form that
    keeps `<SELF+0xNN>`); **no refused row comes back**; and `unchecked_div`
    really is absent at the pin. ⚠ **So the eight REFUSALS stand and the
    GENERALISATION does not** — which is `p28`'s shape exactly: *right verdict,
    wrong reason*, and a refusal's reason is what gets reused on the next row.

    ⚠⚠ **THE SCHEDULING CONSEQUENCE IS THE PART THAT MATTERS: *"do NOT start a
    27th pattern"* IS NOW JUSTIFIED BY A FINDING THAT DOES NOT STAND.** **The
    decision may still be right — but it needs a different reason, and nobody has
    supplied one.**

    ⚠⚠ **SCOPE OF THE DISPUTE — READ THIS BEFORE CITING ANY OF FINDING 37.**
    **This entry has THREE limbs and only the FIRST is disputed:**

    1. ⚠ **DISPUTED** — the *"iff compare-and-branch"* criterion above, and the
       *"eight refusals, hit rate zero, therefore structural"* generalisation
       built on it.
    2. ✅ **NOT ATTACKED, STANDS** — **the REPLACEMENT ADMISSION BAR**: *a row is
       admissible whenever it brings a **new mechanism** — a new operator on the
       safety line, a new source of the bound, or a new reason the check is or is
       not elided.* ⚠⚠ **`p23` SHIPPED ON THIS BAR AND ITS ADMISSION IS
       UNAFFECTED.** **`TASK_113` did not touch it**, and it is the bar any
       re-opened catalogue row should be judged against.
    3. ✅ **NOT ATTACKED, STANDS** — **the keeper: A TERMINATION PROOF DOES NOT
       BOUND THE STACK** (`3 verified, 0 errors` with `decreases`, and the binary
       dies `rc=134` at depth 1e6). **That is `p47`'s shape on a different
       resource and belongs in the synthesis, which is where it went.**

    ⚠ **And the COMPANION RULE below — *a limb that claims a new REASON owes an
    ISOLATION, not just a measurement* — is likewise untouched and is arguably
    the most reusable thing in this entry.**

    **Eight candidate rows were probed and all eight were refused, each on a
    measurement** — the manager's four and the engineer's own four, ⚠ **and both
    lists had a hit rate of ZERO, which is the point: this is structural, not bad
    luck.**

    | candidate | what killed it |
    |---|---|
    | recursion depth | `k_safe_naive`/`k_safe_tuned`/`k_unsafe` all `call` **the same ICF-merged symbol** — no bounds check, no panic edge. **R2 = R3 = R4, one rung.** Depth headroom flat too: gcc `-O2` and Rust `-O3` both **48 B/frame**, both survive **173 950**. |
    | division by zero | ⚠ **`unchecked_div` does not exist at the pin** (`E0599`, then `E0635 unknown feature`). The only lever is `unreachable_unchecked`, an **annotation**. Behaviour matrix has **one column**: C `rc=136` SIGFPE, safe Rust `rc=101` panic, unsafe Rust `rc=136`. |
    | unaligned load | Probe 2 twice: gcc `k_cast` ≡ `k_memcpy` (19 insns, `437d7f5cbf20`); Rust `ptr::read` ≡ `read_unaligned` (58 insns, `9fc2e1d8889a`). Harm never observable without a sanitizer — **36 plain cells, all `rc=0`**. |
    | format string | Harm is **ASLR-nondeterministic** (3/3 different `%p`), `%n` blocked at `-O2` by fortify. The cost axis is **glibc**, `+162 Ir`/call, **none of it a check**. |
    | stack use-after-return | **Both compilers warn by default** (`-Wreturn-local-addr` / `-Wreturn-stack-address`) and gcc then SIGSEGVs instead of exhibiting it. |
    | VLA / `alloca` stack clash | `witness_dirty=0` in **every** cell; every oversize case a plain `rc=139`. **No clash observable even unprobed, even on clang.** |
    | `qsort` comparator | **80 cells, ZERO ASan reports**, including a comparator that always returns `−1`; positive control fires `ASan=2` in 4/4. Mechanism fetched: **glibc 2.39's `qsort` is mergesort + heapsort**, all bounds are counts. |
    | TOCTOU double fetch | `k_double_fetch` ≡ `k_single_fetch`, 22 insns, `7b0e28cdead4` — **CSE'd to one load**. And it *is* `p38`, which already ships the folded control. |

    ✅ **ONE KEEPER, and it belongs in the synthesis rather than in a row: A
    TERMINATION PROOF DOES NOT BOUND THE STACK.** `b3_verus_rec.rs` verifies
    **`3 verified, 0 errors`** with `decreases buf.len() - i`, and the compiled
    binary at depth 1e6 prints **`fatal runtime error: stack overflow, aborting`,
    `rc=134`**. **The proof discharges exactly what it says and the program still
    dies** — `p47`'s shape (the proof certifies a leaking kernel), second
    instance, on a different resource.

    ⚠⚠ **THE SCHEDULING CONSEQUENCE, and it is the endgame answer: NEW ROWS ARE
    NOT WHERE THE REMAINING VALUE IS.** Eight refusals on eight probes, after
    fifteen refusals on the original catalogue, is the instrument telling us its
    domain. **Finish `p23`, take `p42` (a bug class the tree genuinely lacks and
    which fires at the gate's own flags), and spend the rest on the synthesis.**

    ⚠ **AND THE "FIFTEENTH `index >= len`" BAR WAS ON THE WRONG QUANTITY** — the
    manager suspected this and asked for it to be argued from the CVE
    distribution rather than from taste. **The replacement bar, which is better:**
    *a row is admissible whenever it brings a **new mechanism** — a new operator
    on the safety line, a new source of the bound, or a new reason the check is or
    is not elided.* **"Another `index >= len`" is not the question; "another
    `cmp`/`jbe` in the same place for the same reason" is.** `p36` shipped as the
    twelfth and was worth it; `p45`'s class was genuinely absent and was not.

    ⚠⚠ **COMPANION RULE, earned by the FIRST row admitted under this bar
    (`p23`, `TASK_105`): A LIMB THAT CLAIMS A NEW *REASON* OWES AN ISOLATION, NOT
    JUST A MEASUREMENT.** `p23` cleared limbs 1 and 2 — a new operator (the guard
    compares **two loop variables**) and a new source of the bound (**each cursor
    is bounded by the other, and both move**) — and both are true and unique in
    the tree. **Limb 3, the new elision REASON, shipped a phenomenon with an
    unverified cause**: the `k_up`/`k_dn` measurement reproduced to the
    instruction under an independent probe, **but both stated causes failed
    isolation** — making the induction variable ascend costs `+816…+1614` instead
    of recovering the elision, and removing the unsigned subtraction recovers
    `12…20` of a `184…488` gap. ⚠ **A measurement shows THAT; only an isolation
    shows WHY, and limb 3 is the only one of the three that asserts a why.**
    **This is `PROTOCOL` rule 12 (*ask for the mechanism, not the number*) meeting
    rule 9 (*don't land a finding before its review*), and `p23` is the case that
    shows the two combine.**

    Evidence: `.tasks/TASK_102_REPORT.md`, `.temp/t102/` (`REBUILD.sh`),
    `.tasks/TASK_105_REPORT.md`.

38. **p23 — THE SAFETY TAX IS A FUNCTION OF THE DATA'S SHAPE, NOT ITS SIZE.**
    The 25th pattern, and the first here whose cost axis is the *distribution* of
    the input rather than its extent. ⚠ **PROVISIONAL where it rests on
    `TASK_106`, which is unreviewed.**

    ⚠⚠ **THE HEADLINE NUMBER AND ITS MECHANISM ARE BOTH CORRECTED (`TASK_117`,
    MANAGER-RE-MEASURED). THE AXIS SURVIVES; ITS MAGNITUDE FALLS BY 9× AND ITS
    REGRESSOR INVERTS.**

    ~~`R3 − R4` runs **`227.00 → 706.37 Ir`/call, a factor of 3.11**~~ — that is
    the **shipped spelling pair**, and it reproduces exactly (all seven published
    band-K rows to ±0.00). ⚠ **But `TASK_106` itself found a cheaper in-contract
    R3 (`k_u5`, the tautological conjunct), and against that R3 the same shipped
    R4 gives `172.64 … 227.00`, a factor of `1.3148`.**

    | quantity | min | max | ratio |
    |---|---|---|---|
    | published, shipped R3 − shipped R4 | `227.00` | `706.37` | **`3.112`** |
    | cheapest in-contract R3 − shipped R4 | `172.64` | `227.00` | **`1.315`** |
    | ⚠ the SPELLING term (shipped R3 − `u5`) | **`0.00`** | **`480.00`** | — |

    ⚠⚠ **THE SPELLING TERM IS NOT A CONSTANT — IT IS EXACTLY `2·dn − 2·recs`**,
    `480.00` at `nlow=1` and `0.00` at `nlow=31`, residual `0.0000` over 41
    points. **So it is COLLINEAR WITH THE VERY AXIS THE FINDING IS ABOUT**, which
    is why it inflates one endpoint and not the other. ✅ **Manager re-ran the
    whole band-K sweep; `.temp/r117/measure_bandk.py`, with `un_base`'s `md5_fn
    43acbc727fc6…` matching the shipped R4 cell as the reproduction arm.**

    ⚠⚠ **AND THE MECHANISM CLAIM INVERTS, WHICH IS THE SHARPER HALF.**
    ~~*"The obvious confound is the swap count, and it is REFUTED — `dn` alone
    gives R² `0.9869`, `sw` alone `0.0132`."*~~ **Against the cheapest
    in-contract R3 the two SWAP PLACES: `dn`/rank falls to R² `0.0001` and `sw`
    rises to `0.9930`.** ⚠ **So the swap-count refutation — celebrated as making
    the result stronger — is TRUE OF THE SHIPPED PAIR AND FALSE OF THE PATTERN.**
    **`sw` was the right regressor all along and the shipped R3's spelling was
    hiding it.**

    ✅ **What survives, and it is still a real result: the shape axis is real at
    fixed size** — a `54.36 Ir`/call swing with element count, record count and
    bytes copied all fixed — **and `up + dn == mbytes` exactly at all 109 shipped
    points**, so total cursor work is constant and only its split moves.
    ⚠ **Quote `1.3148×` and `54.36 Ir`/call, not `3.11×` and not `479`.**

    ⚠ **Mechanism, measured on the shipped rung for the first time:** unchecking
    the downward read **alone** gives `258.00 = 2 + 32·recs` **flat at all 31
    ranks**, and both-scans-unchecked equals it exactly — **and a fully safe
    in-contract R3 is CHEAPER than that at 8 of 8 ranks.**

    **The law, and getting it right took three attempts:**

    > **`R3 − R4 = 2 + 30·recs + 2·dn + 2·sw − 3·rounds + Σ_records τ(m mod 4)`**,
    > `τ = {0→0, 1→2, 2→3, 3→4}` — **max |residual| `0.0000` over all 109 shipped
    > points**, `-O3 isolated`, kernel-exclusive `Ir`, debug-assertions **off**.
    > **Holdout: fit on bands M+N (71 points), predict the 38 nobody fitted →
    > max |error| `0.0000`.**

    ✅✅ **THE LAW SURVIVED A SERIOUS ATTACK — `TASK_117`, and this is the
    strongest clean negative in the project.** The manager's suspicion was that a
    law repaired for ONE residue blindness would be blind in another parameter,
    or that `rounds` was a linear combination absorbing the error. **Both
    refuted:** the 8-column design matrix has **rank 8/8 in EXACT arithmetic**
    over all 109 points *and* over the 71 M+N training points — **so `0.0000` is
    not collinearity** — and **twelve NEW out-of-band points**, with predictions
    **registered before measurement**, came back at **max |error| `0.00`** on a
    set that discriminates (it rejects three superseded law forms by `720`, `60`
    and `54.5`). ⚠ **Attack the law again only with new evidence; this one is
    settled.**

    ✅ **AND THE LAW AND THE §A CORRECTION ARE CONSISTENT, WHICH IS THE CHECK
    THAT MAKES BOTH BELIEVABLE.** The spelling term is `2·dn − 2·recs`, so
    subtracting it from the law leaves the in-contract tax as
    **`2 + 32·recs + 2·sw − 3·rounds + Σ τ(m mod 4)`** — **with no `dn` term at
    all.** That is exactly why the regressor inverts to `sw`, and at `recs = 8`
    its leading part is `2 + 32·8 = 258.00`, **which is the flat value the
    unchecked-downward-read arm measures at all 31 ranks.** **Three independent
    routes to the same number.**

    ⚠⚠ **THE METHOD RESULT IS WORTH MORE THAN THE LAW: p23 produced THREE
    mutually inconsistent "exact" laws, each with ZERO in-sample residual.** The
    published four-term form is **band-K-only and mispredicts the two SHIPPED
    matrix inputs by up to `152.00 Ir`/call**, despite a `0.0000` holdout *inside*
    band K. **`τ` was invisible to every band**: K sits at `m = 32` and N at
    `m = 16`, **both `≡ 0 (mod 4)`**, and the control reads band M at
    `want_m = [2,4,8,16,24,32,40,48]` — **seven of eight multiples of four**,
    leaving one non-zero sample. ⚠ **This is the residue-class trap for the THIRD
    time** (p38's additivity failure, p46's underdetermined two-band fit), and it
    is the sharpest: **p46 showed a two-band fit can be UNDERDETERMINED with no
    in-sample residual; p23 shows a one-band fit can be CONFIDENTLY WRONG with a
    PERFECT in-band holdout.** **Only out-of-band prediction caught either.**

    ⚠⚠ **AND A FINDING ABOUT THE GATE ITSELF, not about p23: A `required`
    SPELLING PIN CAN BE SATISFIED BY A TAUTOLOGICAL CONJUNCT THE COMPILER
    DELETES.** A cheaper R3 spelling was excluded as out-of-contract; **restoring
    the pinned conjunct as a redundant leading term makes it in-contract and
    changes nothing — the two compile to the SAME OBJECT CODE** (`md5_norm
    da08af26d9b1`, 249 insns, both). **The in-contract R3 floor drops `150.00`
    `Ir`/call to `2991.00`, which is `59.00` BELOW the in-contract R4 spelling —
    so the R3 and R4 spans OVERLAP, and ≥150 of the published safe-side figure is
    SPELLING, NOT SAFETY.** ⚠ **The span's TOP endpoint was wrong too** —
    `4208.00` was `r3b`, which is **`forbidden`**. ✅ **Clean negative that makes
    it precise: three *other* in-contract respellings are all DEARER than the
    shipped shape. Only the tautology recovers the saving.** ⚠⚠ **So an
    in-contract span endpoint is a statement about WHAT SOMEONE THOUGHT TO WRITE,
    not about what the declaration permits.**

    **Proof: `16 verified, 0 errors` FIRST ATTEMPT** (twin 19/0), **zero
    `proof fn`s**, TCB 5 (3 contract-bearing), no `assume`, no
    `assume_specification`. ⚠ **The manager's named kill risk was backwards:** the
    task argued the bug might live in the nested-scan Hoare form while only the
    two-index form verifies. **The Hoare form verifies `6/0` first attempt too,
    and the bug lives in the form that verifies MOST EASILY** — the spec is
    written in the shape the code moves in, which is why p06 needs three lemmas
    for a simpler obligation and p23 needs none. ✅ **Anti-vacuity: 9 of 9 mutants
    fail, 3 of 3 controls verify — the strongest mutation result in the tree**
    (p24 7/8, p29 3/4), because the postcondition is an **exact value equality**
    rather than a property. ⚠ **A multiset clause was dropped as "separable" on
    an experiment that was itself measuring a VACUOUS postcondition** (the
    multiset-deleted probe accepts a body that zeroes the prefix and never looks
    at the pivot); **right conclusion, invalid reason** — the exact fold is
    strictly stronger than the clause dropped, since a multiset is invariant
    under permutation and the fold is not.

    ⚠ **The elision PHENOMENON reproduces to the instruction and its CAUSE IS
    OPEN.** `k_up == k_r3c` and `k_dn == k_r4b` exactly, independently
    reproduced — **but "the direction of the cursor is the whole tax" failed
    THREE isolations**: making the induction variable ascend costs `+816…+1614`
    instead of recovering the elision; removing the unsigned subtraction recovers
    `12…20` of a `184…488` gap; and the *upward* scan given the blamed shape is
    **cheaper**, below the unchecked kernel at two of three ranks.

    ⚠ **The hardened-C row is rank-dependent and p23 did not apply its own rule to
    it.** `R1 − R1h` on gcc is **`+39.10 / +60.34`** — positive, i.e. **the
    hardened kernel is cheaper**, and also **smaller** (157 vs 160 insns). But the
    guard's price **flips sign twice across p23's own rank band** (`+168.48` at
    0.03, `−144.59` at 0.50, `+139.87` at 0.97), and the two shipped inputs sit at
    ranks 0.44 and 0.28 — **both inside the negative window, which `gen.py`
    enforces.** ⚠⚠ **And the negative sign is absent from p23's OWN MIXED BAND:
    the guard price is POSITIVE at all five band-X points.** So *"the safety line
    has a negative price on gcc"* holds on two enforced inputs and on no mixed
    input measured. ⚠ **p23's own warning is *"any number quoted without its rank
    is quoted without its domain"*, and its C row was quoted without one.** The
    stated mechanism is refuted too: scan steps fit R² `0.023`, **exchanges
    `0.973`**.

    ⚠⚠ **A structural lesson worth more than its occasion: A NUMBER ONLY A
    REBUILD CAN PRODUCE MUST NOT BE TRANSCRIBED INTO A FILE THE REBUILD
    RE-HASHES.** A review asked for a corrected count of distinct adversarial
    checksums; four gate runs gave **7, 7, 8, 8**, because **`NOTES.md` is in the
    gate record's `source_sha256`** — so recording the count forces a run and the
    run moves it. **`NOTES.md` now publishes the property (exit 0, silent, all
    rungs diverge, hardened rungs agree) and no number.** ✅ Nothing was ever
    pinned on those values, so the gate never depended on one.

    Evidence: `.tasks/TASK_101_REPORT.md`, `.tasks/TASK_105_REPORT.md`,
    `.tasks/TASK_106_REPORT.md`, `patterns/p23-partition/NOTES.md`.

39. ⚠⚠ **p42 — TWO HEADLINES PUBLISHED AND RETRACTED, THREE ENCODINGS BUILT AND
    ALL THREE ADMIT A VERIFYING LEAKER. THE QUESTION IS OPEN, AND THE SHIPPED
    TREE IS PROTECTED BY THE IDENTITY PIN RATHER THAN BY ITS PROOF.**
    The 26th pattern, and **the most-corrected result in the project.**
    ⚠ **Encoding 3 was correctly NOT PUBLISHED — it was built, attacked, found
    leaking, and reported as a failure. That is why the retraction count is two
    and the encoding count is three.**

    ⚠⚠ **HEADLINE 1, RETRACTED (`TASK_109`, review): *"Verus at the pin CANNOT
    state leak-freedom."*** False as stated.

    ⚠⚠ **HEADLINE 2, RETRACTED (`TASK_116`, review — AND MANAGER-VERIFIED
    INDEPENDENTLY): *"a ghost ledger states it exactly."*** **IT DOES NOT. THE
    LEDGER'S `ensures` IS SATISFIED BY A LEAKING PROGRAM.** One line, substituted
    for the error path's `led_free`:

    ```rust
    proof { let tracked _dl = led.tracked_remove(0int); }   // drop the token, never free
    return 0;
    ```

    | | shipped | leaking variant |
    |---|---|---|
    | `./verus_run.py` | `18 verified, 0 errors` | **`18 verified, 0 errors`** |
    | `--cfg slb_twin` | `21 verified, 0 errors` | **`21 verified, 0 errors`** |
    | obligations / twin / axioms | 18 / 21 / 0 | **18 / 21 / 0 — nothing moves** |
    | bytes leaked | 0 | **`n_err × win_len`, exactly `model.py::leak_bytes`** |

    ⚠⚠ **AND THE SHARPEST FORM: the leaking R5's `-O3` kernel is BYTE-IDENTICAL
    to the shipped R4 with p42's own bug planted in it** — `md5_fn
    d3f1194cb10bce2057e0e1f3e28c1e21`, `n_fn 128`, **both**. ✅ **Manager
    re-ran all four numbers; regenerate with `.temp/mgr115/p42/REBUILD.sh`.**

    **The mechanism, and it is one sentence:** `Map::tracked_remove` is the very
    call `led_free` makes, so ⚠⚠ **WRAPPING AN AFFINE RESOURCE IN A MAP DOES NOT
    MAKE IT LINEAR — IT MAKES THE DROP TAKE ONE MORE LINE.** Assigning
    `Map::tracked_empty()` over the whole ledger verifies too, which refutes
    `idiom.why`'s *"a proof cannot drop the MAP that holds it"* in its own words.
    ⚠ **The refutation was already in p42's own `NOTES.md` 6c, ONE PARAGRAPH
    BELOW THE CLAIM** — *"a tracked `Map` is as droppable as the token inside
    it."* **Nobody read the two sentences against each other.**

    ⚠⚠ **WHAT THIS DOES *NOT* SAY — and getting this wrong would be the third
    retraction.** It does **NOT** reinstate headline 1. **One ENCODING is
    refuted; INEXPRESSIBILITY IS NOT PROVEN and is OPEN.** ✅ **Repair direction,
    measured and unbuilt: a module-local `Tracked<Freed>` receipt is FORGEABLE in
    proof mode (`3 verified, 0 errors`); a PRIVACY-SCOPED one is NOT — rustc
    rejects the forgery.** ~~**That is the live lead.**~~

    ⚠⚠ **ENCODING 3 WAS BUILT AT `TASK_118` AND IT FAILS TOO. THREE ENCODINGS,
    THREE VERIFYING LEAKERS.** ✅ **MANAGER RE-RAN THE DECISIVE ARM; it
    reproduces (`.temp/t118/decoy_err.py`).** **The privacy-scoped ledger blocks
    every attack that killed encoding 2 — `atk_remove` is `error[E0616]: field
    `m` … is private`, i.e. blocked BY RUSTC — and then loses to a different
    one:**

    ```
    mustfire_err2        18 verified, 1 errors   escrow in a ledger kbody WAS HANDED   -> REJECTED
    atk_decoy_err        19 verified, 0 errors   escrow in a ledger kbody MINTS ITSELF -> ACCEPTED
    atk_decoy_err_freed  19 verified, 0 errors   same local ledger, BOTH paths free    -> floor
    leaked  1284 / 1652 / 1028 / 1044  against a constant 1028 floor
            == model.py::leak_bytes on ALL FOUR inputs
    -O3     r5decoyerr md5_fn d3f1194c… == the shipped R4 WITH p42's BUG PLANTED
    ```

    ⚠ **Two arms differing in exactly ONE respect — WHICH LEDGER — and the one
    that mints its own verifies while leaking.** ⚠⚠ **THE REUSABLE RULE, and it
    is the shape of all three failures: PRIVACY MAKES A LEDGER'S *CONTENTS*
    UNFORGEABLE (by rustc) AND CANNOT MAKE THE LEDGER *UNIQUE*.** **The
    postcondition certifies only that the author wrote *something* on each exit
    that empties a map the author controls — so the gap is one proof line wide,
    in three places.** ⚠ **PROVISIONAL: this rule is `TASK_118`'s reading and is
    UNREVIEWED (rule 9). The CONCLUSION — encoding 3 fails — is manager-verified;
    the RULE is not.**

    ⚠⚠ **AND THE ARM THAT DECIDED IT WAS ONE THE MANAGER COULD NOT PLACE.**
    Attempt 1 left a verifying leaker labelled `atk_decoy`; **the manager's
    reconstruction of that dead agent's state recorded it as *"PURPOSE UNKNOWN —
    establish before citing"* and moved on.** ⚠ **The one row a summary cannot
    place is worth more attention than the twenty it can, not less.**

    ✅ **The price was always right and the PRODUCT is nothing:** the ledger costs
    **+3 obligations, 0 TCB, 0 `Ir`** — ⚠ **and buys no leak-freedom.**
    ⚠⚠ **STILL NOT SAID, AND STILL THE THING THAT WOULD BE THE FOURTH
    RETRACTION: this does NOT show Verus cannot state leak-freedom. THREE DATA
    POINTS ARE NOT AN IMPOSSIBILITY PROOF. Expressibility at this pin is OPEN.**
    ⚠ **One unbuilt lead remains and is recorded rather than pursued:
    `dig_alloc` + `led_new` private to `mod res`, with `res::run`.**

    ⚠⚠ **THE STRUCTURAL POINT, and it is the transferable one: NOTHING IN THE
    GATE CHECKS THAT AN `ensures` MEANS WHAT ITS PROSE SAYS.** The gate was
    green, the record reproduced, the corrections landed, the obligation count
    was pinned — **and the central positive claim was false.** ✅ **The shipped
    tree is safe anyway, and it is worth knowing why: the `identity` pin catches
    the attacked R5 at both pinned levels. It is the PIN that protects p42, not
    the PROOF.**

    ✅ **Clean negative that SURVIVES the review, on better evidence: there is NO
    linear must-consume tracked mode at the pin** — **22** `verifier::`
    attributes (⚠ **this said 23; corrected at `TASK_110` and the correction
    never reached the authoritative layer until now**), none is one; full
    attribute enumeration, a 10-name binary sweep, `vstd/` **and**
    `vstd/std_specs/`. ⚠ **PROVISIONAL markers on this finding STAY — `TASK_116`
    says explicitly: do NOT clear them.**

    **`Tracked<Dealloc>` is AFFINE, not linear — a proof may simply drop it.** An
    R5 that forgets the error path's `deallocate` verifies **`2 verified, 0
    errors`**, with the must-fail arm (use-after-move) correctly rejected
    (`controls/affine_leak.rs`, both arms committed). ⚠ **`p27` proves
    deallocation is LEGAL — no double-free, no use-after-free. It never proves
    deallocation HAPPENS**, and the manager asserted the route was "precedented"
    on exactly that confusion. **Miri is what stands behind the Rust side
    instead**, so the deleted-`dig_free` positive control ships with the pattern
    and fires.

    ⚠ **SCOPE, and it is the engineer's own caveat: this is the DEFAULT
    ENCODING, not an exhaustive search.** A ghost ledger and Verus's linear mode
    were **named and not built**. The measured claim is *at the pin, with
    `Tracked<Dealloc>` as `p27` uses it, a dropped token verifies.*

    > ⚠⚠ **THIS COMPLETES A FAMILY OF THREE, AND THE FAMILY IS THE RESULT: THE
    > PROOF DISCHARGES EXACTLY WHAT IT SAYS AND THE PROGRAM IS STILL BROKEN.**
    > **(1)** `p47` — the proof certifies a **leaking** kernel (finding 31).
    > **(2)** A `decreases` clause verifies `3 verified, 0 errors` while the
    > binary dies of `fatal runtime error: stack overflow` at depth 1e6 —
    > **a termination proof does not bound the STACK** (`TASK_102`).
    > **(3)** `p42` — an affine deallocation token does not force deallocation.
    > ⚠⚠ **BUT p42's MEMBERSHIP IS NOW CONDITIONAL AND MUST BE CITED THAT WAY:
    > its SHIPPED encoding does not state the property, and a ghost ledger DOES.
    > So p42 is evidence about an ENCODING CHOICE, not about the prover.** `p47`
    > and the stack-overflow case are untouched. ⚠ **Do NOT cite p42 as evidence
    > that a prover cannot express a resource property.**
    > **The two survivors are still a resource the obligation's type does not
    > mention. Before claiming a proof covers a bug class, ask which resource it
    > quantifies over — and then ask whether a different encoding would.**

    **Gate `PASS-WITH-BLOCKED-ROWS`, 0 failures** — the one blocked row is Miri on
    `large.bin` at the 180 s budget, **declared in advance**. Verus **15/0**, twin
    **18/0**, axioms **0**, `identity unsafe ≡ verus` **`exact` at `-O3`**.

    ✅ **All three of the manager's least-sure calls came back yes, and the first
    was settled BEFORE the rungs existed** — by importing `check.py` and driving
    `check_sanitizers` itself on a synthetic pdir, 4 arms, **2 of them controls
    that must fail.** ⚠ **But the gate's `fired` is a 4-way substring OR and
    CANNOT NAME THE SANITIZER**, so a declared `"fires"` is discharged by any
    diagnostic; `controls/leak.sh` carries the finer check — 88 points, LSan
    specifically, byte counts against `model.py::leak_bytes = n_err × win_len`,
    hardened rung silent at all four `-O` levels.

    ⚠⚠ **AND THE COMPARATIVE HEADLINE IS REFUTED — *"safe-tuned Rust beats
    unsafe Rust here"* DOES NOT STAND (`TASK_109`, blocker 2).** The disclosed
    `r4_endptr` is genuinely **inadmissible**, for a reason nobody had found —
    `vstd::raw_ptr::allocate` ensures only `addr + size <= usize::MAX + 1`, so
    **the one-past-the-end pointer is not computable in verified exec code**.
    ⚠ **But the four-spelling search missed one that IS admissible**: a
    **do-while fold that never leaves the allocation** (`r4_foldonly`) verifies
    `15 verified, 0 errors`, is `identity exact` against its own R4, and agrees
    with the shipped rung on **all 12 committed inputs**. Same-session marginals,
    with `TASK_104`'s four published figures reproduced **to the hundredth**:

    ```
    cheapest R3 − cheapest R4 (as published):  −36.00   −2036.00
    cheapest R3 − r4_foldonly       (NEW):     +12.00      +11.00   <- SIGN FLIPS
    ```

    ⚠⚠ **AND THE PATTERN'S OWN HASHED DECLARATION PREDICTED THIS FAILURE
    VERBATIM**: the shared paragraph says *"`min(R3 found) − min(R4 found)` is
    NOT the repair — two upper bounds differenced bound nothing in either
    direction"*, and `NOTES` 11b is exactly that construction, calling the two
    minima **"the two INFIMA"**, which they are not. **What survives is
    `R3ship − R4ship` = `−198.00` / `−8696.00`, two shipped cells — the only form
    that paragraph licenses — and an R4 span of `1407…1617` / `51127…59834` that
    OVERLAPS R3 at both ends.** ⚠ **A difference whose endpoints overlap is not a
    difference, and p42 should say that rather than narrow the claim twice.**
    ✅ **This is `p23`'s span lesson recurring one pattern later and landing
    harder — there the floor moved 150 `Ir`/call; here it moves 210 / 8707 and
    reverses the sign.**

    ✅⚠ **BOTH RUNGS NOW SHIP (`TASK_110`), every stop condition cleared** — the
    ledger passes `--cfg slb_twin` at **`21 verified, 0 errors`** matching the
    pin, `_is_trusted` returns `False` ×3 with **TCB unchanged at 5/3**, and
    `r4_foldonly` is Miri-clean on **seeds 0–7** with its positive control
    firing. **The published table moved as predicted: R4 `1461`/`59441` →
    `1251`/`50734` against R3's `1263`/`50745`, and the R4/R5 identity held.**
    ⚠⚠ **BUT THE ENGINEER TEMPERED THE MANAGER'S FRAMING AND IS RIGHT: SHIPPING
    THE NEW R4 *REMOVES* A HEADLINE RATHER THAN IMPROVING ONE.** `p42` now
    publishes **"the R3 and R4 admissible classes are not separated"**, and its
    own `NOTES` refuses `+12`/`+11` as a headline too — **two overlapping spans
    do not become a difference by changing which endpoint you quote.**
    ⚠⚠ **AND A REAL CAVEAT ON THE LEDGER, measured rather than argued: DELETING
    ITS LEAK-FREEDOM `ensures` STILL GIVES `18 verified, 0 errors`.** No count
    moves. **Only the `spec.md` textual pin catches its removal** — so the
    obligation is load-bearing for the *program* and not for the *count*, which
    is exactly the gap a reader would assume the count closes. ⚠ **The
    declaration also never constrained the fold loop at all, which is why a
    fifth spelling could move the endpoint in the first place.**

    ⚠ **`R1 − R1h` is `0.00` on gcc — and the two kernels ARE two rungs**, a hand
    `objdump` diff showing **exactly one field** (`jne <kernel+0x91>` against
    `jne <kernel+0x8c>`). **The C side's boundary is one branch-target field
    wide, and that is what `0.00` means.** ⚠⚠ **On clang the mechanism is WINDOW
    PARITY, NOT WINDOW SIZE** — `−5.00` on even windows and `−4.00` on odd, with
    **zero size dependence over a 32× range**; the build read its own two inputs
    (97 odd, 4096 even) as a small-vs-large effect. ⚠ **FOUR terms, not three —
    and the correction is against the REVIEW, by the task that landed it**: the
    `setne`/`sete`/`or` merge is **`+1` NET, not `+3`**, because the review's
    count did not subtract the `jne`+`cmp` the merge replaces. **The totals
    agreed; the split did not.** ⚠ **Two successive tasks each isolated this
    mechanism and each got the decomposition wrong in a different way — a
    reminder that "totals agree" is not "mechanism established".**

    ✅⚠ **AND A METHOD LESSON FROM THE PREVIOUS PATTERN STOPPED A WRONG NUMBER
    HERE — the first time that has happened.** `p23` taught that a within-band
    holdout proves nothing; `p42` fitted on windows 64..79 and predicted
    512..527 **before publishing**, and **every rung's out-of-band residual is
    3×–25× its in-sample one**, the cheapest rung mispredicting **its own shipped
    `large.bin` by `−2545 Ir`/call** off an in-sample residual of `12.57`.
    **So `p42` publishes TWO POINTS AND NO RATE.** ⚠ The allocator size class is
    **refuted** as the mechanism — it is smooth curvature, not a step — and the
    real one is **OPEN**.

    ⚠ **Two disclosures that matter.** The **first gate run FAILED and all four
    causes were the engineer's own**, including that **backticked words inside a
    prose `forbidden` entry are read as forbidden SPELLINGS**. And **`r4_endptr`
    is `162 Ir`/call cheaper and admissible in principle, its R5 was never built,
    R4 was held fixed by fiat — and the published spans OVERLAP**, which is
    `p23`'s span lesson recurring one pattern later.

    Evidence: `.tasks/TASK_104_REPORT.md`, `patterns/p42-goto-cleanup/NOTES.md`.

40. ⚠⚠ **THE CATALOGUE IS FULLY ADJUDICATED — AND ITS ROWS DIE FOR MANY REASONS,
    OF WHICH DUPLICATION IS THE LARGEST AT 27%. IT IS A LIST, NOT A LAW, AND IT
    DOES NOT LICENSE "STOP".** **This was written as the honest replacement for
    finding 37, and ⚠⚠ IT DID NOT SURVIVE ITS OWN REVIEW EITHER** (`TASK_120`).
    ⚠ **Its header read *"THE CATALOGUE IS EXHAUSTED, AND THE REASON IS
    DUPLICATION"* after the body had already been corrected to say otherwise —
    PROTOCOL rule 13, committed by the manager in the same session it enforced
    rule 13 on two other rows. Trust the body.**

    ✅ **THE MEASURED PART, and it is settled:** at `TASK_115` the last seven
    rows were adjudicated and **every one of the 48 catalogue rows now carries a
    verdict with a measurement behind it.** The decomposition is
    **`48 = 26 BUILT + 17 REFUSED + 3 DEFERRED + 2 OTHER`** — `p24` (probed,
    live, needs a new reason) and `p35` (blocked, not refused) being the two.
    ⚠ **`p25` is the ONE row on which this project has run nothing, and its cell
    says so.** **Recount with `.temp/mgr115/census.py`.**

    ⚠⚠ **THE GENERALISATION WAS THE MANAGER'S READING, IT WAS REVIEWED AT
    `TASK_120`, AND IT DID NOT SURVIVE IN THE FORM IT WAS WRITTEN.** **It was
    published as:**

    > ~~**The remaining rows fail because they RE-DERIVE A MECHANISM ONE OF THE
    > BUILT 26 ALREADY CARRIES, not because they have nothing to measure.**~~

    ⚠ **`TASK_120` classified ALL 22 non-built rows by each cell's OWN stated
    kill** (`.temp/r120/classify22.py`, which pins a verbatim quote per row and
    asserts it — ✅ **the assert FIRED on `p31`, so the instrument works**):

    ```
    DUP     6  p21 p26 p28 p37 p39 p43     NOVELTY 5  p15 p29 p30 p31 p48
    COST    4  p20 p24 p40 p41             LADDER  3  p33 p44 p45
    NONE 1 p25 · ADMIN 1 p32 · PIN 1 p34 · GATE 1 p35
    duplication as PRIMARY reason: 6/22 = 27%   ·   mentioned at all: 11/22
    ```

    ✅ **So the honest sentence is *"the largest single family of stated reasons,
    at about a quarter, is duplication"* — A LIST, NOT A LAW.** ⚠ **The manager's
    own "least sure #2" guessed exactly this and was right.**

    ⚠ **The seven's MEMBERSHIP was wrong three ways**, and one of them is the
    selection effect **caught in the act with a timestamp in the cell**:

    - **`p20` is not a duplication refusal.** Its kill is the measurement —
      *"a length/offset check is O(1) and does not scale"*. ⚠⚠ **The duplication
      clause was APPENDED AT `TASK_115` and is explicitly *"the deferral holds
      A FORTIORI"* — a reinforcing reason written by an agent who already knew
      the built tree. That is the `TASK_120` §A.3 selection effect, dated.**
    - **`p41` is a two-kill row and its cell says so** — *"dies on probe 3 AND on
      duplication"*. **Probe 3 came first and is sufficient**; the apparent
      `9.6×` was 100% R3 spelling.
    - **`p28` is MISSING**, and its cell says *"it is still `p27`'s MECHANISM,
      which is why the row is refused"*. Finding 40 filed it under *"the
      allocator/recycling family"* — ⚠ **a LOCATION, not a reason.**

    ⚠⚠ **AND "DUPLICATION" IS AT LEAST FOUR DIFFERENT RELATIONS WEARING ONE WORD
    — the category error the review was asked about, CONFIRMED:** `p21`→`p14` is
    **same predicate**; `p39`→`p09` is a **strict subset** (`p09` ships both
    halves); `p26`→`p13` is the **same published conclusion**, i.e. a *result*
    and not a mechanism; `p28`→`p27` is the **same runtime detector**;
    `p43`→`p16` is a **same-kernel-shape claim the numbers contradict** (below).
    ⚠⚠ **`p37`→`p08` IS THE SHARPEST AND IT IS BACKWARDS: it is a shared
    structural ABSENCE — `p08` does not CARRY the mechanism, it LACKS one. `p37`
    has a NOVEL bug class (type confusion, absent from all 26 by census), a
    MEASURED cost axis (`21/20/18 Ir` per record, tag check `+2.00`) and a FIRING
    harm (ASan 2/2), and what actually killed it is a VERUS REPRESENTABILITY
    LIMIT. A row like that was being counted as evidence that the rows have
    nothing new.**

    ⚠⚠ **AND ONE ROW FAILS FOR A REASON WORTH ITS OWN SENTENCE, because it is
    about the INSTRUMENT rather than the row:** `p40` (SoA vs AoS) differs by
    **21 `Ir`** while its cache behaviour differs by a large factor. ✅ **THE
    CONCLUSION SURVIVES — the row's entire axis is invisible in this project's
    primary metric, and wall clock cannot rescue it** (best-of-7 spreads
    `2.8%–32.7%`, over the project's own 10% discard threshold on 3 of 4 rungs).
    ⚠⚠ **BUT THREE OF ITS FOUR PUBLISHED FIGURES DID NOT SURVIVE `TASK_120`, AND
    THE ONE THAT DID IS NOW CONFIRMED TWICE:**

    - ✅ **`21 Ir` — CONFIRMED by two independent routes**, including a
      **zero-iteration control the original lacked** that makes `k40_aos` and
      `k40_soa` byte-equal at `374,658,547`, so all 21 belong to the kernel.
    - ⚠ ~~`5.8e-8`~~ → **`4.9e-6`, 84× larger.** **The 360 M denominator is
      98.86% program SETUP**; the kernel's own marginal is `1,442,043 Ir`/call.
      ⚠ **`5.8e-8` is the figure a reader quotes — do not quote it.**
    - ⚠ ~~`+193 Ir`~~ → **`+114` over 3 calls = `38 Ir`/call.** **115 `Ir` of it
      was `println!` formatting a kernel name six characters longer**, visible
      with the kernels never called.
    - ⚠⚠ ~~`LLd read misses differ 4.20×`~~ → **DOES NOT REPRODUCE; re-runs at
      `3.68×`.** ✅ **The `D1` miss delta reproduces EXACTLY (`1,179,645`), so the
      kernels are identical and the LLd figures moved with the ENVIRONMENT** —
      and both are **whole-program** counts dominated by the 67 MB + 16 MB setup
      allocations, ⚠ **so neither `4.20×` nor `3.68×` is a property of the
      kernel at all.**

    ✅ **`p40`'s absolute `Ir` total moved `360,114,293` → `378,984,676` — 18.9 M
    — and `TASK_122` SETTLED IT: NOT the build, NOT the box, NOT the environment,
    but a SETUP ARRAY in the probe's own source (`0.023%` agreement).**
    ⚠⚠ ~~*"Something in the box changed"*~~ **and** ~~*"the box is not as stable
    as the record assumes"*~~ **are BOTH STRUCK. Full derivation in finding 41.**
    ✅ **Blast radius is ONE figure — the drift is common to both arms of every
    published DIFFERENCE, so it hits denominators only.**

    ⚠⚠ **WHAT THIS FINDING DOES NOT LICENSE — AND `TASK_120` §B IS THE ANSWER TO
    THE ENDGAME QUESTION, SO READ IT BEFORE ACTING ON THIS FINDING AT ALL.**
    **It does not say new patterns are impossible — it says THESE 22 ROWS are
    spent.** ⚠ **The admission bar from finding 37's second limb still stands and
    is untouched: *a row is admissible whenever it brings a new mechanism — a new
    operator on the safety line, a new source of the bound, or a new reason the
    check is or is not elided.*** ⚠⚠ **SO: FINDING 40 SUPPORTS *"GO FIND NEW
    ROWS"*, WEAKLY BUT GENUINELY, AND DOES NOT SUPPORT *"STOP"*. WHOEVER CITES IT
    FOR *"STOP"* IS CITING IT WRONGLY — including the manager, who wrote the box
    row that did exactly that.** **The reviewed grounds, all four measured:**

    - ✅ **The 47 rows ARE pre-project — verified in `git`, not inferred:**
      `git show d5e0ccd:.memory/06-catalogue.md` has **47 rows in the repo's
      FIRST commit**, with an empty `patterns/`. **A pre-project list running out
      after 26 builds says little about the domain.**
    - ⚠ **The honest counter-evidence, at full strength: 9 post-project proposals,
      0 admissions** (`p48` + `TASK_102`'s eight). ⚠⚠ **BUT ALL NINE WERE
      SELECTED ON BUG-CLASS NOVELTY — the criterion `TASK_113` says *"predicts
      neither way"*. NO SEARCH HAS EVER BEEN RUN UNDER THE BAR THAT SURVIVED
      REVIEW.** **The one row admitted under that bar (`p23`, chosen BECAUSE it
      was the 15th `index >= len`) shipped finding 38; the one admitted on
      bug-class absence (`p42`) shipped with BOTH headlines retracted.**
    - ⚠⚠ **THE ARGUMENT THE MANAGER ASKED FOR AT `TASK_113` — argue the bar from
      the CVE DISTRIBUTION rather than from taste — WAS NEVER DELIVERED, AND THE
      CORPUS FOR IT HAS BEEN IN THE REPO THE WHOLE TIME.**
      `../LearnVeri/microbench/` is **20 worked CVEs with completed proofs**, and
      sec-ladder has cited it **twice in its entire history, never as a row
      source** (`.memory/04-verus.md:5` for proof idioms; `TASK_011.md:13`, which
      became `p17`).
    - ✅ **The census of it, run INDEPENDENTLY BY THE REVIEWER AND BY THE MANAGER
      (`.temp/mgr121/NOTES.md`), CONVERGED on 15 of 20 and DIVERGED on one row —
      and the divergence is exactly where the manager had flagged its own mapping
      as untrustworthy.** **Both readings: the 8 TEMPORAL map onto the exhausted
      `p27` family** (all eight are fixed by a generational index; ⚠ **and `p27`'s
      own source says a freelist push into a slab makes the stale read *in bounds
      of a live allocation* — `p17`'s LOGICAL class, `TASK_055` §2.8 — ⚠⚠ **AND THE MANAGER MISQUOTED IT IN TWO FILES, CAUGHT BY `TASK_123`: §2.8 ADOPTS `(slot, gen)` for R1h/R2/R3 and rejects it only as the R4/R5 representation. The verdict stands; the reason was wrong**); **the 7 LOGICAL should die on probe 1** — no
      boundary between the rungs, which is `p31`'s and `p33`'s death — ⚠ **and
      that is a real prediction somebody can cheaply falsify.**
      ⚠⚠ **THE DIVERGENCE, AND IT IS THE ONE CANDIDATE: `CVE-2021-23017` — a
      SIZING pass under-counts a separator the WRITING pass emits, so THE BOUND
      COMES FROM AN EARLIER PASS OVER THE SAME INPUT AND THE TWO PASSES
      DISAGREE.** **Against the built tree's sources of the bound — attacker
      length field (`p02`, `p16`), byte-value count (`p14`), buffer extent
      (`p01`), carry width (`p46`), two moving cursors (`p23`) — *a bound
      computed by a previous pass* IS NOT PRESENT.** ⚠ **That is limb 2 of the
      reviewed bar verbatim. The reviewer explicitly does NOT claim it would
      survive probing — only that the enumeration has never been done.**

41. ⚠⚠ **THERE IS NO MEASURED REASON TO STOP. THE CATALOGUE IS CLOSED AND THE
    DOMAIN IS NOT — AND THE THREE GENERALISATIONS OFFERED OVER THIS REFUSAL SET
    HAVE ALL DIED, WHICH IS ITSELF THE RESULT.** ⚠⚠ **THE STANDING CONCLUSION:
    KEEP THE 22-ROW CLASSIFICATION, PUBLISH NO GENERALISATION OVER IT.**

    ⚠ **This finding was landed as `TASK_120`'s replacement for finding 40,
    marked PROVISIONAL, explicitly so it could be attacked. `TASK_122` attacked
    it AND IT DID NOT SURVIVE — it fails HARDER than finding 40 did: finding 40
    was wrong about a TALLY, finding 41 was wrong about a CATEGORY and about a
    CONTROL.** It was published as:

    > ~~**`LADDER` + `COST` is 7 of 22, so THE MOST COMMON THING WRONG WITH A
    > REMAINING ROW IS THAT THE FIVE-RUNG LADDER HAS NOTHING TO PRICE ON IT — an
    > INSTRUMENT property, which will keep killing NEW rows too.**~~

    ⚠⚠ **BLOCKER 1 — `LADDER`+`COST` IS FOUR CATEGORIES AND THE FINDING ADDED
    THEM.** `classify22.py`'s own definition of `COST` is *"flat, zero, **false**,
    or below the instrument"* — four different things:

    | split | what it really is | rows |
    |---|---|---|
    | **FLAT** | the rungs are the SAME PROGRAM — ⚠ a **COMPILER** fact, not a ladder limit | `p24` `p44` `p45` |
    | **BELOW** | a real axis the metric cannot see — ✅ **the ONLY genuine instrument limit** | **`p40`, and only `p40`** |
    | **SCOPE** | real, measured, **NONZERO**, rejected for being `O(1)` — ⚠ a **TASTE** criterion | `p20` (`+6.00`/`+7.00 Ir`), `p43` |
    | **false** | the row's cost claim was FALSE — ⚠⚠ that is `NOVELTY`'s definition VERBATIM, and `p41`'s cell literally says *"NOT on the ladder test"* | `p41` |

    ✅ **So *"nothing to price"* is true of 4 of 22, not 7 — and a genuine
    INSTRUMENT limit of ONE.**

    ⚠⚠⚠ **BLOCKER 2, AND IT IS THE ONE THAT KILLS IT: THERE IS NO CONTROL ARM.
    `classify22.py` classifies ONLY THE REFUSED ROWS — it SELECTS ON THE
    DEPENDENT VARIABLE.** **Run the criterion against the BUILT tree and it does
    not discriminate: 8 of the 26 BUILT patterns publish a ZERO on their own
    headline axis** (`p04` `p08` `p09` `p13` `p16` `p17` `p27` `p36`).
    ⚠⚠ **THE SHARPEST IS `p46`, THE 24th PATTERN BUILT, WHICH SHIPS FINDING 36 AS
    ITS RESULT: a per-MAC safety tax of `0.00000` AND *"the boundary vanished"* —
    BOTH HALVES OF FINDING 41's KILL CRITERION, PUBLISHED AS A FINDING.**
    ✅ **Manager-verified: `p46`'s and `p16`'s zeros are in this file's own
    findings section.**

    ⚠⚠ **AND THE CATALOGUE ALREADY DREW THE LINE FINDING 41 ERASED**
    (`.memory/06-catalogue.md`, probe 3, verbatim and manager-verified):
    ***"A zero with a named axis and a mechanism is a FINDING; a zero because two
    rungs compiled to the same bytes is an ARTEFACT."*** **Finding 41 merged
    exactly what probe 3 separates.**

    ⚠ **Three further defects, each enough on its own:** *(a)* ***"the five-rung
    ladder" silently means "the `Ir` column"*** — `CLAUDE.md` names FIVE axes, and
    `p15`/`p24`/`p28`/`p29` carry measured R5 results, with `p24` sitting IN the
    seven. *(b)* **RANKING INSTABILITY: three readers produced three different
    top families and the margin was 1 EVERY TIME — a tally that cannot carry a
    superlative.** *(c)* ⚠⚠ **`TASK_120`'s OWN SELECTION-EFFECT INDICTMENT OF
    `p20` WAS ITSELF SELECTIVE, and this is manager-verified in `git`: `p20`'s,
    `p40`'s AND `p41`'s trigger sentences ALL entered at commit `7f01a72` — THE
    SAME COMMIT as the *"a fortiori"* clause `TASK_120` condemned. It singled out
    one clause from a commit that wrote three, and its own classification then
    rested on the other two.**

    ⚠⚠ **THE CONSEQUENCE FOR THE PROJECT, STATED PLAINLY: finding 41 was the ONLY
    measured ground for stopping. It does not hold. SO THERE IS NO STATED REASON
    TO STOP — and `TASK_122`'s §A closes the CATALOGUE, not the DOMAIN.**
    ✅ **`TASK_123`'s enumeration is therefore the MAIN LINE, not an option.**
    ⚠ **And do NOT reuse *"the ladder has nothing to price"* as a kill criterion
    inside it — `p46` is the counter-example already in the tree.**

    Evidence: `.tasks/TASK_122_REPORT.md`, `.tasks/TASK_120_REPORT.md`,
    `.temp/r122/`.

    ⚠⚠ **AND THE 18.9 M `Ir` DRIFT IS SETTLED — IT IS NOT THE BOX, AND THE
    ALARMING SENTENCE THIS FILE CARRIED IS STRUCK.**
    ~~*"The box is not as stable as the record assumes."*~~ **`TASK_122`
    measured it out, cheapest arm first, and every candidate was eliminated by a
    measurement rather than by an argument:**

    - ✅ **Not the BUILD** — identical flags, binary bit-reproducible across paths.
    - ✅ **Not the BOX** — `dpkg` untouched since Aug 15; `libc`, `valgrind` and
      `rustc` binaries all Aug 15, **all PREDATING `TASK_086`**.
    - ✅ **Not the ENVIRONMENT** — measured at **61,877 `Ir`**, **300× too small**.
      ⚠ **But note it is FOUR ORDERS ABOVE the ±7 this project records, because
      that ±7 is a MARGINAL figure where the term cancels.**
    - ✅ **MEASURED MECHANISM: deleting ONE SETUP ARRAY (`tagged`) from the shared
      probe source drops the total by `18,874,783` against a drift of
      `18,870,383` — `0.023%`** — and it is the one term whose own source comment
      records a mid-session edit.

    ⚠ **Published as SUFFICIENCY, NOT ACTUALITY** (the `MIRIFLAGS` rule: this axis
    has already carried two confident wrong mechanisms). ⚠⚠ **AND IT CAN NEVER BE
    RAISED TO ACTUALITY, FOR A REASON THAT IS ITSELF THE FINDING: `.temp/` IS
    GITIGNORED, SO THE `p40`-ERA `cost.rs` IS GONE. *"Byte-identical pipeline"*
    was checked against TODAY'S copy and is UNVERIFIABLE.**

    > ✅ **The landable conclusion is stronger than the one it replaces:
    > WHOLE-PROGRAM TOTALS FROM `.temp/` PROBES ARE UNREPRODUCIBLE IN PRINCIPLE.**

    ✅ **BLAST RADIUS IS ONE FIGURE, and this is the reassuring half: the drift
    sits in a term COMMON TO BOTH ARMS of every published difference, so it hits
    DENOMINATORS, not DIFFERENCES.** **`5.8e-8` is the whole list, and `TASK_120`
    had already fixed it.** ⚠ **The `--cache-sim` observation stands on its own —
    whole-program totals moved by 60 between `--cache-sim=yes` and plain
    `callgrind` on the same binary and argv, while differenced numbers did not
    move at all — so *a published figure below ~100 `Ir` taken from a
    whole-program TOTAL rather than a DIFFERENCE is at the noise floor* remains
    the working rule.**

    Evidence: `.tasks/TASK_122_REPORT.md`, `.tasks/TASK_120_REPORT.md`,
    `.temp/r122/` (`REBUILD.sh` regenerates), `.temp/r120/classify22.py`.

42. ⚠⚠ **THE DOMAIN WAS FINALLY ENUMERATED, AND ONE CANDIDATE SURVIVES OUT OF
    TWENTY — BUT THE SHARPEST RESULT IS THAT THIS CORPUS ANSWERS THE WRONG
    QUESTION.** **`TASK_123`, the enumeration `TASK_113` asked for and never
    got.** ⚠ **ENGINEER WORK, NOT YET REVIEWED (rule 9).**

    **20 worked CVEs from nginx/OpenSSL/libxml2/PHP, against the reviewed
    three-limb bar, probe 1 first. 19 die on a `grep`, a run, or a load-bearing
    citation. Every verdict cites evidence rather than a reading.**

    - ✅ **The LOGICAL seven die on probe 1, MEASURED rather than assumed.**
      Strip the incidental array index from `CVE-2021-3450`'s decision and
      **safe-naive, safe-tuned and unsafe are BYTE-IDENTICAL** — 108 B, md5
      `2a7cb02d…`, **`37.00 Ir`/call each**. `CVE-2023-0465` fires and is fixed
      identically at all five arms. **Must-fire arm (an OOB gather) fires at
      `rc 134` and prices at `+44.00 Ir`/call.** ⚠ **Note the discipline: this is
      `R3 − R4 = 0.00` WITH PROBE 2 COLLIDING, which is the catalogue's own
      ARTEFACT side — NOT finding 41's banned criterion.**
    - ✅ **The TEMPORAL eight close on a citation, and no measurement was spent.**
      ⚠⚠ **AND THE MANAGER MISQUOTED THAT CITATION IN TWO FILES: `TASK_055` §2.8
      ADOPTS `(slot, gen)` for R1h/R2/R3 and rejects it ONLY as the R4/R5
      representation. *"The engineer rejected it"* was wrong. Verdict unaffected,
      reason wrong — and it had already propagated into `RECAP.md` before anyone
      checked.**
    - ⚠⚠ **THE SPATIAL FIVE RESOLVED AGAINST THE MANAGER, AND RULE 4 IS WHY IT
      COST NOTHING.** **The manager's census mapped `CVE-2021-23017` → `p12`;
      `TASK_120`'s left it open.** ✅ **`TASK_123` ran the novelty claim FIRST, as
      the rule requires, and the mapping is REFUTED: `p12`'s bound is a
      `#define`.** **A census of ALL built kernels — 14 destination buffers —
      finds **13 `#define` capacities + 1 input extent and ZERO prior-pass
      counts**, with a must-fire arm that fires on the candidate.**
      ⚠ **The task file's OWN premise, written by the manager, was also false:
      `p16` is single-pass and `p14` counts and appends in one pass.**

    ✅ **THE SURVIVOR: `CVE-2021-23017` — a SIZING pass under-counts a separator
    the WRITING pass emits, so THE BOUND COMES FROM AN EARLIER PASS OVER THE SAME
    INPUT AND THE TWO PASSES DISAGREE.** ⚠⚠ **Probe 1 gives a FOUR-WAY behaviour
    split, which no built row has — READ ON, THIS WAS AN ARTEFACT OF THE PORT AND
    `TASK_124` KILLED IT; it is preserved rather than struck because the
    refutation below is the finding:** C = ASan `heap-buffer-overflow WRITE of
    size 1`; **R2 = panic; R3 (`Vec::push`) = CORRECT**; R4 = silent OOB write,
    **Miri UB**. Probe 2: three distinct kernels. Probe 3: ~~`R2 − R4 = +63.00 Ir`/call~~ → ⚠ **`+71.00`, corrected at
    `TASK_124`: `TASK_123`'s probe evaluated `rung.starts_with(...)` INSIDE the
    measured loop — its OWN disclosed defect 2, 11% low.** ⚠ **And the project
    publishes `R3 − R4`, which fill-controlled is `+34.00` / `+22.00`.** Probe 4: `get_unchecked` 0 hits at the pin.

    ⚠⚠⚠ **AND THE SURVIVOR DID NOT SURVIVE `TASK_124`. IT IS REFUSED, TWICE
    OVER, ON TWO INDEPENDENT MEASUREMENTS. THE MANAGER GUESSED THIS ONE RIGHT
    AND SAID SO IN THE TASK FILE — the four-way split is a property of the PORT,
    not of the BUG.**

    ✅ **THE DECIDING MEASUREMENT IS A PERTURBATION CONTRAST, and it is the right
    shape: perturb the SIZING pass's count by `+8` and ask WHOSE BEHAVIOUR
    CHANGES.** **Six of eight arms had to change and did** — C (ASan
    `heap-buffer-overflow WRITE` → silent), R2 (panic → correct), two
    fixed-capacity tuned R3s (panic → correct), R4 (Miri UB → clean).
    ⚠⚠ **BOTH `Vec::push` ARMS WERE UNCHANGED, and the mechanism is MEASURED and
    not inferred: capacity `4 → 8`, the `Vec` REALLOCATED.** ✅ **A
    fill-controlled `pushfill` grows too, so it is THE IDIOM and not
    `with_capacity`.** ⚠ **`R3 = CORRECT` was `Vec::push` deleting the bug's
    PRECONDITION, exactly as suspected — it does not survive the bug, it removes
    the bound there is to violate.**

    ⚠⚠ **TWO FURTHER INDEPENDENT KILLS, either sufficient:** *(a)* **three
    admissible ZERO-`unsafe` spellings give THREE DIFFERENT R3 answers**
    (correct / panic / silent truncation) **while R1 and R4 are pinned — so "the
    R3 behaviour" is not a property of the row at all**; *(b)* ⚠ **`TASK_123`'s
    `R4 = Miri UB` IS NOT AN ADMISSIBLE R4** — `.memory/01-ladder.md` requires R4
    to be *correct, just unverified*, and the tree has **194 Miri runs with 0 UB**
    and `identity` pinned 26 of 26.

    ⚠⚠ **AND THE ROW DIES A SECOND TIME ON LIMB 2 ITSELF, which is the more
    valuable half:** `TASK_124` built the control the census could not — **hold
    the kernel fixed and change ONLY the bound's PROVENANCE, from a prior-pass
    count to an input extent.** **All six decode kernels are THE SAME
    INSTRUCTIONS** (0 mnemonic diffs; R4 byte-identical; relocation-normalised 0
    diffs, with two arms proving the normaliser still catches a planted
    `0xC0→0xE0`). ⚠⚠ **EVERY PUBLISHED `Ir` DIFFERENCE MOVES BY EXACTLY `+0.00`**
    — only the common sizing-pass term moves, and it CANCELS.
    ⚠⚠⚠ **AND THE SENTENCE THAT USED TO CLOSE THIS PARAGRAPH IS CORRECTED —
    IT OVERSTATED ITS OWN EVIDENCE BY FOUR COLUMNS. SEE FINDING 44.**
    ~~*"So a new SOURCE of the bound is a distinction THIS LADDER CANNOT PRICE,
    and limb 2 of the admission bar is weaker than it reads."*~~
    ✅ **The true statement: *a new source of the bound cannot be priced ON
    ASSEMBLY OR `Ir`*. `TASK_124` measured TWO of the project's SIX published
    columns and said so itself — its §B2 is headed *"Verus. ⚠ NOT SPENT,
    deliberately."*** ⚠ **The kill on `CVE-2021-23017` NEVERTHELESS STANDS on its
    OTHER, INDEPENDENT grounds — the port-property split, the three-R3-answers
    control, and `R4 = Miri UB` not being an admissible R4. DO NOT READ FINDING 44
    AS RE-OPENING THAT ROW.**

    ✅ **WHAT SURVIVES, and it belongs in `SYNTHESIS.md` rather than in a row:**
    ***safe Rust's idiomatic escape is `Vec::push`, which DELETES the bound
    rather than CHECKING it*** — now measured. ⚠ **It is a sentence about a Rust
    idiom, not a ladder row, precisely because it describes a rung that is no
    longer running the same program.**

    ⚠ **Three of the manager's own premises in `TASK_124.md` were false and are
    recorded so nobody re-derives them: the two-call-kernel worry** (`p42`
    allocates inside the kernel; four patterns already use kernel-TU helpers)**;
    `get_unchecked`'s 0 hits being a constraint** (it is the normal situation —
    269 uses in-tree behind `external_body` wrappers in all 26)**; and the
    allocation-shape question itself, which the perturbation contrast subsumed.**

    ⚠⚠⚠ **AND THE RESULT THAT OUTRANKS THE CANDIDATE — the manager's stated
    "least sure #1", confirmed: A CVE CORPUS ANSWERS *"WHICH MECHANISMS ARE
    MISSING?"* AND CANNOT ANSWER *"WHICH IDIOMS MATTER?"* — 8 of 20 are pure
    decision bugs, a distribution NO IDIOM CENSUS WOULD PRODUCE, because CVEs
    select for EXPLOITABILITY and not for FREQUENCY.** **`TASK_113` asked for the
    bar to be argued from the distribution; this corpus supplies only half of
    that.** ⚠ **If the project wants the bar argued from idiom frequency, THE
    ENUMERATION HAS TO BE OVER C IDIOMS, and it has still never been done.**

    ✅ **Three of the engineer's OWN instrument defects were caught by its
    must-fire arms, and two would have handed it a free refusal** — an `argv` bug
    producing `0.00000 Ir`/call from zero iterations; per-iteration `match`
    dispatch making byte-identical kernels read `43/50/37`, **which changed a
    sign**; and C loop-hoisting giving `n1 == n2` exactly. ⚠ **A `bound_census.py`
    missing `re.M` also printed the RIGHT answer for the WRONG reason.**

    ⚠⚠⚠ **CODA — STRUCK. IT WAS THE MANAGER'S, IT WAS MARKED *"one manager
    command and it should be checked before it is relied on"*, IT WAS CHECKED,
    AND IT IS FALSE. THE INSTRUMENT WAS THE DEFECT.** The struck claim:

    > ~~**THE IDIOM ENUMERATION CANNOT BE RUN ON THIS BOX, BECAUSE THERE IS NO
    > INDEPENDENT C CORPUS ON IT** — largest non-project C directory: 13 zlib
    > examples; the only C available is `../LearnVeri/microbench/`'s 49 CVE ports
    > and sec-ladder's own 77 kernels.~~

    ⚠⚠ **THE CAUSE IS `-maxdepth 6` IN THE MANAGER'S OWN ONE-LINER, AND IT IS
    THIS PROJECT'S MOST-NAMED FAILURE CLASS VERBATIM — *a grep that can only find
    what you already thought of is not a census*, and *a detector that is not
    running looks exactly like a detector that found nothing*.** **Drop the depth
    limit and the same box has 31 929 `.c` files.** ✅ **Manager-re-run,
    `.temp/mgr127/allc.txt`:**

    ```
    /home/apt/repos_common/php-in-safe-rust/build/php-4.0.2/
        301 .c + 252 .h,  186 805 lines,  22 MB   <- UPSTREAM PHP 4.0.2, whole tree
        ext/ 220, Zend/ 25, main/ 22, sapi/ 15, regex/ 8, win32/ 9, TSRM/ 1
    GNU coreutils, under unsafe-rust-pitfall's TASK014_eng_coreutils_u2 scratch
        310 .c,  56 873 lines   ⚠⚠ THAT IS THE PRE-DEDUP FIGURE AND THE MANAGER
        PUBLISHED IT: one gnulib copy per utility. ✅ TRUE FIGURE, `TASK_129`,
        manager-re-derived by content hash: 94 DISTINCT FILES, 18 862 LINES.
        ⚠ EXACT PATH IN `.tasks/TASK_129.md` §0, deliberately not repeated here —
          see the checker note below.

    AND A THIRD CORPUS THE MANAGER NEVER CHARACTERISED — `TASK_129` found it in
    the very file list this coda was derived from, under unsafe-rust-pitfall's
    shared artifacts: 24 UPSTREAM GNU PACKAGES (gawk, tar, grep, sed, make,
    wget, diffutils, findutils, cpio, gzip, patch, rcs, ed, indent, units,
    enscript, cflow, glpk, libosip2, mcsim, pexec, pth, hello, depregawk)
        2 655 .c raw -> 2 162 DISTINCT,  785 480 lines    ✅ manager-re-derived
    ```

    ✅ **TOTAL AS CENSUSED: 991 147 deduplicated lines over 22 PROGRAMS — so the
    replication arm ran at `n = 22`, not the `n = 2` the manager scoped. See
    finding 45.**

    ⚠⚠ **AND WRITING THIS DOWN FOUND A DEFECT IN `TASK_125`'s NEW CHECKER, BY
    ORDINARY USE, ONE TASK AFTER IT LANDED: `harness/tools/temp_citations.py`
    matches `\.temp/` ANYWHERE IN A LINE, so an ABSOLUTE path into ANOTHER
    REPOSITORY'S `.temp/` is read as one of THIS repo's scratch citations and
    resolved relative to sec-ladder — where it does not exist.** ✅ **The path
    resolves fine on disk; the `dangling` verdict was a MISRESOLUTION, not a
    missing file.** ⚠ **The alarm is apt for the wrong reason — another project's
    `.temp/` is MORE deletable than ours, which is exactly why `TASK_129` is told
    to commit a sha256 manifest. ✅ The fix is free (`harness/tools/` is outside
    the gate digest): anchor the pattern to a repo-relative `.temp/`, i.e. reject
    a match preceded by a path character. NOT DONE — `TASK_127` owns `harness/`
    while it runs.**

    **And the idiom density is real** (PHP 4.0.2 `.c` only): `memcpy` 235,
    `strcpy` 123, `strcat` 145, `strncpy` 52, `malloc` 899, `alloca` 303,
    `goto` 324 (**`p42`'s axis**), `[i]` 847, `for(...;...<...;)` 579.
    ⚠ **One of those numbers was 0 in the manager's first pass because the regex
    `for *(` quantifies the SPACE and opens a GROUP; corrected before landing.
    Failure-class entry 8 in the same probe that corrects entry 8's ancestor.**

    ✅ **WHAT SURVIVES OF THE CODA, AND IT IS THE HALF THAT MATTERS FOR THE CVE
    CORPUS: a CVE corpus still answers *which mechanisms are missing* and still
    cannot answer *which idioms matter* — 8 of 20 are pure decision bugs, and
    CVEs select for EXPLOITABILITY not FREQUENCY. `TASK_123` was right about
    that.** ⚠⚠ **WHAT DOES NOT SURVIVE IS THE CONSEQUENCE: *"the admission bar
    stays MECHANISM-BASED because the frequency-based alternative HAS NO
    INSTRUMENT"* IS NO LONGER TRUE, AND IT IS PUBLISHED IN `results/SYNTHESIS.md`
    §7 AS THE HONEST REASON THIS PROJECT'S GENERALITY CLAIMS STOP WHERE THEY DO.**
    ⚠ **Corrected there too; the corrected §7 says the census is RUNNABLE AND
    UNRUN, which is a weaker and truer thing to publish than *unanswerable*.**

    ⚠⚠ **TWO CAVEATS ON THE CORPORA, BOTH REAL, NEITHER FATAL:** *(1)* **both
    live in OTHER PROJECTS' repositories — `CLAUDE.md`'s `../LearnVeri/` rule
    applies to them: READ ONLY, copy what you need.** *(2)* ⚠ **the coreutils
    tree is under another project's `.temp/`, which that project's own convention
    makes DELETABLE AT ANY TIME — so a census over it must record a sha256
    manifest of what it read, or its numbers are unreproducible.** **PHP's is
    under `build/`, which is more durable but is still not this repo's.**
    ⚠ **Do NOT copy 22 MB into this tree: *promote, don't publish* is about
    kilobytes. Read in place, commit the MANIFEST and the RESULT.**

    ⚠ **This correction is MANAGER-MEASURED AND UNREVIEWED (rule 9). The
    RETRACTION lands now because it removes a claim; the REPLACEMENT — that a
    frequency census is methodologically sound on one interpreter plus one
    utility suite — is `TASK_129`'s to establish and is NOT yet claimed here.**

    Evidence: `.tasks/TASK_123_REPORT.md` §D (the full 20-row table),
    `.temp/t123/` (`A/build.sh`, `C/REBUILD.sh` regenerate).

43. ⚠⚠ **NO INPUT CAN BE ADVERSARIAL TO A RUST RUNG IN THIS TREE — AND THAT IS
    A THEOREM ABOUT THE CONTRACTS, NOT A GAP IN THE INPUTS.** ✅ **`TASK_124`
    found the census; `TASK_126` explained it and CORRECTED THIS FINDING'S FIRST
    TWO STATEMENTS.** ⚠ **Engineer work, not yet reviewed (rule 9), but the
    mechanism is one `grep` and the manager re-ran it.**

    ```
      129  adversarial (pattern, input) pairs in results/gate/*.json
       58  with ANY cell divergence     <- 58 is CORRECT; see the correction below
        0  where safe_naive / safe_tuned / unsafe / verus differ from one another
   13449  FRESH candidate inputs generated across all 26 patterns (TASK_126)
      600  with a rung split
        0  with a RUST-rung split   -- and the same corpus at debug-assertions=ON: also 0
    ```

    ⚠⚠ **THE MANAGER'S EXPLANATION WAS HALF RIGHT AND THE WRONG HALF MATTERED.**
    Measured with the gate's own `harness/asm.py::identity_level`, all six Rust
    pairs × 2 opts × 26 patterns:

    - `unsafe` vs `verus`: **same machine code 52/52** ✅ — ⚠ **but *"byte-identical"*
      is TOO STRONG: 26/52 `exact`, 26/52 `norel`, and `md5_raw_equal` is FALSE in
      25 of 26 at `-O0`.**
    - `safe_naive` vs `safe_tuned`: ⚠⚠ **`differ` 52/52 — THE MANAGER'S GUESS IS
      REFUTED.**

    ✅ **SO THE TREE HAS THREE BEHAVIOURAL RUST RUNGS — not four, and not the two
    the manager guessed — AND THE R2/R3 ZERO IS A MEASUREMENT, NOT A TAUTOLOGY.**

    ⚠⚠⚠ **THE REAL MECHANISM IS STRONGER THAN THE `identity` PIN, AND IT IS THE
    FINDING:** `derived_contract` shows `requires` is `off + len <= buf_len` in
    **26 of 26 and NEVER MENTIONS BUFFER CONTENTS** (✅ manager-verified: 0 of 26
    index the buffer); `ensures` is a single **TOTAL** value clause; and the
    pinned driver loop makes the window bound a **theorem**
    (`k < nwin`, `nwin*stride <= n_blob`). **So an adversarial input can only
    change bytes inside a window every Rust rung is contractually TOTAL on.**

    > ⚠⚠ **THEREFORE THIS FINDING'S SECOND READING — *"the harm inputs are not
    > adversarial enough"* — IS NOT MERELY UNTESTED, IT IS MIS-STATED. MORE
    > ADVERSARIAL INPUTS IS NOT THE FIX. There is nothing for them to be
    > adversarial TO.**

    ✅ **AND THE CORROBORATION IS BLUNT: NO RUST RUNG HAS EVER PANICKED.**
    **107 592 fuzz runs + 516 gate rows, zero exits outside
    `{0, EXIT_TRUNCATED, EXIT_CAP}` — and 5 of those 7 are the SHARED DRIVER
    refusing a malformed file, not a kernel.** **The C side on the same inputs:
    29 SIGSEGVs, 8 aborts, 2 hangs.**

    ⚠ **TWO CENSUS DEFECTS, NEITHER MOVING THE ZERO — and one is the manager's
    wording:** `TASK_124`'s census **keeps only the LAST ROW PER RUNG**, and
    ~~*"56 vs 58 — a grouping tie-break, not a dispute"*~~ **was wrong: it is
    that BUG. 58 is correct** (the manager's independent recount got 58 and then
    wrote the wrong reason for the gap). **It also DROPPED `stderr`, which the
    gate does record — a planted stderr-only split proved it blind.** ✅ **Zero
    unchanged once `stderr` and `hung` are added.** ✅ **Denominator honest: all
    four Rust rungs run on all 129 inputs; all 36 multi-row rungs are C;
    `skipped_inputs` empty 26/26.**

    ⚠⚠ **THE REAL QUALITY GAP IS SOMEWHERE ELSE, AND IT IS NEW: 36 OF 129
    ADVERSARIAL INPUTS (27.9%) MAKE ZERO KERNEL CALLS** and produce one identical
    behaviour in every cell; **71 of 129 (55%) produce one identical behaviour at
    all.** ⚠ **The `adversarial-strideN.bin` TEMPLATE family is 0-call in 22 of
    26 patterns** — a template copied forward without being re-aimed. **Worst:
    `p42` (10 adversarial inputs, 7 zero-call, 0 divergences) and `p01` (6 of 6
    zero-call).** ⚠ **That is a per-pattern quality number nobody had computed,
    it is one pass over committed records, and it is where "the inputs are weak"
    is TRUE — just not in the way this finding first said.**

    ⚠ **Also: the nondeterminism footprint is SEVEN patterns, not the two
    `TASK_125` named** — all C, and **0 of 4080 Rust cells unstable.**

    ✅ **Must-fire discipline worth copying: `TASK_126`'s comparison reproduced
    the gate's per-pattern divergence count EXACTLY on all 26 patterns (58/129)
    BEFORE it was trusted on a null result.** ⚠ **A null from an unvalidated
    detector is worthless, and this project has produced two of those in one
    session.**

    Evidence: `.tasks/TASK_126_REPORT.md`, `.tasks/TASK_124_REPORT.md`,
    `results/gate/*.json`, `.temp/t126/`.

44. ⚠⚠ **`TASK_124` MEASURED 2 OF THIS PROJECT'S 6 PUBLISHED COLUMNS, SO ITS
    *"THE LADDER CANNOT PRICE LIMB 2"* WAS OVERSTATED — BUT THE REPLACEMENT
    HEADLINE DID NOT SURVIVE THE MANAGER'S RE-RUN EITHER, AND THE REASON IS THE
    BETTER RESULT.** ⚠ **Engineer work (`TASK_128`), NOT YET REVIEWED (rule 9);
    the manager re-ran the whole probe (`.temp/t128/BUILD.sh`, `rc=0`), every
    figure below reproduced exactly, ⚠⚠ AND ONE OF THE ENGINEER'S OWN
    CALIBRATION ARMS TURNS OUT TO REFUTE THE HEADLINE IT WAS BUILT TO SUPPORT.**

    ✅✅ **REVIEWED AT `TASK_130` — the review DECIDED the manager-vs-engineer
    dispute (rule 3 forbade the manager clearing its own objection) and then
    corrected the manager's replacement sentence too.**

    > ⚠⚠⚠ **THE HEADLINE `TASK_128` RETURNED — ~~*"the ladder CAN price a
    > mechanism it cannot price in instructions; the column is `obligations`"*~~
    > — IS NOT MERELY UNSUPPORTED. IT IS INVERTED. The columns that SEE limb 2
    > are ASSEMBLY and `Ir`; `obligations` is the ONE COLUMN THAT CANNOT, and it
    > ranks the DEAD-CODE arm ABOVE the MECHANISM arm.**

    ⚠⚠ **THE MANAGER'S OWN STATED "LEAST SURE #1" WAS RIGHT AND THE TASK'S
    PREMISE INVERTED: `TASK_124` MEASURED 2 OF 6 PUBLISHED COLUMNS.** **This
    project publishes assembly, `Ir`, timing, PROOF BURDEN, TRUSTED BASE and the
    HARM MATRIX.** **The provenance contrast covered the first two, had NO C ARM
    (so even the assembly result is Rust-only), and its §B2 is headed *"Verus.
    ⚠ NOT SPENT, deliberately."*** ⚠ **So *"every published difference"* was a
    phrase the manager copied out of this file into two more places, and it was
    wrong by four columns.**

    ✅ **THE INSTRUMENT WAS THEN POINTED AT THE QUESTION. Kernel held
    byte-identical BY CONSTRUCTION — one Python string emitted into both arms —
    and ONLY the bound's provenance changed (input extent → prior-pass count):**

    ```
    kernel symbol   243 B   sha256 a379bee990da90af   IDENTICAL IN BOTH ARMS
    kernel-excl Ir/call        176.00  vs  176.00        ->  +0.00
    Verus `verified` (the PUBLISHED `obligations`)  3 ->  5  ->  +2   (+67%)
    ghost clauses (req/ens/inv/dec)                9 -> 13  ->  +4   (+44%)
    TCB items / lines                            1/1 -> 1/1 ->   0
    ```

    ⚠⚠ **AND `+2` IS NOT NOISE IN THAT COLUMN: ✅ manager-recounted from
    `git show HEAD:results/gate/p*.json`, `verus["verus.rs"]["verified"]` runs
    `7 … 21` over 26 patterns, and `+2` IS EXACTLY THE `p01`→`p03` GAP.**

    ⚠⚠⚠ **THE MANAGER WROTE A "STRUCTURAL AND SURVIVES" PARAGRAPH HERE AND IT IS
    STRUCK — `TASK_130` M3: IT PROVES TOO MUCH.** ~~*"`obligations`/`TCB` are
    published PER PATTERN, not as an `R_x − R_y` difference, so there is no
    second arm for the common sizing-pass term to cancel against."*~~ ⚠ **Applied
    evenly that gives `Ir` the same property, and `TASK_124` MEASURED IT: a level
    move of `−63.00 Ir`/call in EVERY ONE of its seven cells, printed in its own
    table two columns left of the `+0.00`s everybody quoted.** ✅ **`Ir` is
    published per cell as a LEVEL exactly as `obligations` is published per
    pattern. The asymmetry does not exist.** ✅ **WHAT SURVIVES IS THE SMALLER,
    TRUER STATEMENT: *the `+0.00` was a property of the COMPARISON CHOSEN — a
    rung-to-rung difference — and not of the columns.***

    ⚠⚠⚠ **THE CONTROL THE ENGINEER RAN AND READ AS CALIBRATION — AND IT REFUTES
    THE HEADLINE. ✅ MANAGER-FOUND BY RE-RUNNING THE ARTEFACTS, NOT BY READING
    THE REPORT.** **`_calib2.rs` is arm E — bound still the INPUT EXTENT — plus
    `probe_loop`, a counting function whose body is the SAME SHAPE as arm P's
    sizing pass and WHOSE RESULT IS DISCARDED. Re-run by the manager:**

    ```
    armE      3 verified      bound = input extent
    armP      5 verified      bound = PRIOR-PASS COUNT     <- the mechanism
    _calib2   5 verified      bound = input extent + an UNRELATED proved loop
    ```

    ⚠⚠ **`armP` AND `_calib2` ARE INDISTINGUISHABLE ON `obligations`. One carries
    the mechanism; the other carries dead code of the same proof shape.** **So
    the column moves with ADDED PROVED CODE, not with the bound's PROVENANCE —
    and the movement is NOT SPECIFIC TO LIMB 2.** ✅ **The engineer built exactly
    the right control and labelled it `_calib`, using it to DECOMPOSE the `+2` as
    *1 function + 1 loop* — which is the same fact, read as support instead of as
    refutation.** ⚠ **That is not a sloppy probe; it is a well-built probe whose
    strongest arm was filed under the wrong heading, and it is the reason the
    manager re-runs falling claims rather than reading reports.**

    ⚠⚠ **AND THE MANAGER'S OWN VERDICT ON THAT EVIDENCE — *"the only column that
    moves moves for a reason not specific to the mechanism"* — WAS RIGHT IN
    DIRECTION AND WRONG IN SCOPE, AND `_calib2` ALONE WOULD HAVE LOST THE
    ARGUMENT. `TASK_130` says so in terms: the §A defence genuinely blunts
    `_calib2`, and THREE STRONGER ARGUMENTS carried it instead —**

    ✅ **(i) THE DECIDING ARMS, at the PROJECT's kernel convention rather than
    `TASK_124`'s. Both `TASK_124` and `TASK_128` put the sizing pass OUTSIDE the
    measured symbol; `TASK_124` §B4 had already established a two-pass structure
    needs no second call (`p42` mallocs inside `kernel()`). Rebuild it with the
    whole two-pass function inside the kernel and ✅ manager-re-run:**

    ```
    arm  mechanism           kernel   sha256            Ir/call   obligations
    kE   input extent        199 B    ffd9c4e2186777aa   121.00        3
    kC   extent + DEAD loop  199 B    ffd9c4e2186777aa   121.00        5   <- dead code
    kP   PRIOR-PASS COUNT    407 B    f6040ef542cf2f58   450.00        4   <- the mechanism
    ```

    ⚠⚠⚠ **`kE` AND `kC` ARE BYTE-IDENTICAL WHILE `obligations` DIFFERS BY `+2`,
    AND `obligations` RANKS DEAD CODE (`5`) ABOVE THE MECHANISM (`4`). Assembly
    and `Ir` separate the mechanism cleanly and agree: `+329.00 Ir`/call,
    `+208` bytes, `3.72×`.**

    ✅ **(ii) THE RATIO, WHICH DISSOLVES THE CRUX INSTEAD OF ANSWERING IT.**
    **The right question is not *"does it differ from any change of the same
    size?"* but *"how big is a column's variation across SPELLINGS of the
    mechanism against its variation between PRESENCE and ABSENCE?"***

    ```
    Ir           spelling spread  77 total (0.039/call)   presence gap +327.99/call
                                                          at MATCHED kernel work   ->  8519 : 1
    obligations  spelling spread   2 (armP 5/armPinline 4/armPext 3)
                 presence gap    <= 2, and NEGATIVE at the kernel convention  ->     1 : 1
    ```

    ⚠⚠ **`Ir` IS INVARIANT UNDER RE-SPELLING AND MOVES UNDER PRESENCE.
    `obligations` IS THE EXACT REVERSE.** ✅ **And `obligations` is neither
    NECESSARY nor SUFFICIENT: over seven arms, presence gives `{3,4,5,7}` and
    absence gives `{3,5}` — the sets OVERLAP AT 3 AND 5.** ⚠ **`armEhard` is the
    sharpest single arm: a strictly HARDER proof (value-level `ensures`), same
    exec code, no new function or loop — `obligations` UNCHANGED at 3 while
    `ghost` jumps to 13.**

    ✅ **(iii) THIS PROJECT'S OWN PRECEDENTS, AND BOTH POINT THE SAME WAY —
    AGAINST THE ENGINEER.** ⚠ **The task file guessed they pointed in opposite
    directions; they do not.** **The project has TWICE required an `Ir` figure to
    be distinguished from *the same work spelled differently*, and BOTH TIMES
    STRUCK A PUBLISHED NUMBER when it failed: `p23`/`TASK_106`'s `k_u5`
    (tautological conjunct, same normalised disassembly, 249 instructions →
    *"the published floor was `150.00 Ir`/call too high"*), and `p46` §8a's
    rolled-vs-rolled control (→ *"p46's per-MAC safety tax is `0.00000` and that
    is the sentence to quote"*).**

    ✅ **SO THE CORRECTED VERDICT ON LIMB 2, THIRD AND REVIEWED VERSION:
    IT IS NOT UNPRICEABLE. IT PRICES ON ASSEMBLY AND `Ir`, AT THE LEVEL, ONCE THE
    KERNEL BOUNDARY IS DRAWN WHERE A REAL PATTERN WOULD DRAW IT.** ⚠ **Three
    successive statements about limb 2, each overturning the last: *cannot be
    priced* (`TASK_124`) → *prices on `obligations`* (`TASK_128`) → *prices on
    assembly and `Ir`, and `obligations` is the blind column* (`TASK_130`).
    ⚠⚠ EVERY ONE OF THE FIRST TWO WAS PUBLISHED BEFORE ITS CONTROL WAS RUN.**
    ⚠⚠ **AND THE DEFENCE OF THE ENGINEER'S HEADLINE, STATED AT FULL STRENGTH
    BECAUSE THE MANAGER MAY BE APPLYING TOO STRICT A STANDARD:** *"`_calib2`'s
    loop is DEAD CODE no real pattern would contain. A prior-pass bound
    INHERENTLY costs one proved pass — you cannot equalise the code without
    deleting the mechanism. `Ir` is accepted as PRICING a bounds check even
    though an unrelated `add` costs instructions too; by that same standard,
    `obligations` prices limb 2."***

    ✅✅ **THAT DEFENCE IS SETTLED AND IT LOST — ON FACT, NOT ON TASTE.** ⚠ **Its
    load-bearing claim was *"this project has always accepted `Ir` as pricing a
    bounds check even though an unrelated `add` also costs instructions."* THAT
    IS FALSE ABOUT THIS PROJECT'S PRACTICE: `p23`/`k_u5` and `p46` §8a are two
    occasions on which the project demanded exactly that distinction AND STRUCK
    A PUBLISHED NUMBER when it failed.** ⚠⚠ **And the crux the manager posed —
    *ANY change of the same size* vs *ITS OWN ABSENCE* — WAS A FALSE DILEMMA.
    The ratio in (ii) dissolves it by MEASURING the thing both horns argued
    about.**

    ✅ **AND THE QUESTION FINDING 44 LEFT OPEN IS ANSWERED — YES: assembly and
    `Ir` distinguish `armP` from `_calib2` decisively, and NOTHING in the proof
    columns does.** ⚠ **`ghost_clauses_total` and `proof_fn` separate NOTHING,
    and `ghost` gives `armEhard` the same `13` as `armP`; verification wall time
    separates nothing either (0.93–0.97 s, startup-dominated).**

    ⚠⚠ **AND THE COLUMN'S OWN NATURE, WHICH `synthesize.py` ALREADY DOCUMENTS
    AND NOBODY CONNECTED: `obligations` IS A CODE-SIZE PROXY.** **`verified`
    counts SMT query units — one per function body, one per loop, two per
    `assert … by (bit_vector)`.** ✅ **Over the built tree: `corr(verified,
    syntactic units) = 0.894`, `corr(verified, ghost clauses) = 0.820`,
    `corr(verified, verus.rs SOURCE LINES) = 0.795`** (✅ manager-re-run).
    ⚠ **`synthesize.py`'s own paragraph already said an axiom *"adds no verified
    function, so `obligations` does not move"* and warned that a 7-line reviewed
    wrapper trades against a zero-line axiom *"at par"*. The warning was about
    the TCB column; it is the same insensitivity.**

    ✅ **The other must-fire arms all fired and all reproduce:** deleting the
    sizing pass's `ensures` gives *"precondition not satisfied … `n <=
    src@.len()`"*, `4 verified, 1 errors`; a work-UNMATCHED arm reads `322.00`
    against `176.00`, **so the `+0.00` IS a measurement and not a dead probe.**

    ⚠ **LIMB 3 — the manager's guess was RIGHT ON THE MACHINE COLUMNS AND WRONG
    ON THE VERDICT.** `p13`'s own `NOTES` §4c already had it: **three different
    reasons the bound reaches LLVM agree to the instruction** (`+65.962` slope),
    while the OUTCOME prices at `+16.000`. Reproduced independently: **five
    reasons plus outright deletion span `2.00 Ir`/call on a 200-byte fold —
    `0.41%`, an order under the `±4.6%` layout floor** — with a `black_box`-forced
    control separating at **`3.70×`**. ⚠ **A designed arm FAILED and is recorded
    rather than dropped: `k_noelide` still elides, because LLVM unswitches the
    bound unaided.** ⚠ **The engineer also reported limb 3 *"ALSO prices on
    `obligations`"* (`2 → 4`, range vs bit-mask reason; must-fire fires on
    removing `by (bit_vector)`).** ⚠⚠ **TREAT THAT AS UNSUPPORTED, FOR LIMB 2's
    REASON AND MORE SO: it has NO `_calib`-style specificity control at all, and
    — the engineer's OWN disclosed weakening — the pair does not hold the exec
    code fixed (`+224.00 Ir`/call between the arms). It is a pair differing in
    BOTH the reason AND the code, scored on a column now known to move with
    code.**

    ⚠ **LIMB 1 — the tree runs its control 100 times already and nobody had
    counted it.** ✅ **The count reproduces THREE times — engineer, manager, and
    a reviewer's independently written census: `rows 100`, `|dIr| > 4.6%` in
    **35**, wall in **26**, 25 twins (`p01` has none), **12 patterns with any row
    above the floor**.** ⚠⚠ **BUT THE NUMBER DOES NOT MEAN WHAT IT WAS PUBLISHED
    TO MEAN, AND `TASK_130` FOUND BOTH REASONS:**

    - ✅ **M6 — the TWIN premise is BUILD-true and SOURCE-false.** `build.py`'s
      `c_flags()` never sees the kernel name and `-h` swaps ONE file, so ⚠ **the
      flag / libc-entry / stack-protector confound the review went looking for
      IS NOT THERE — a clean negative.** ⚠⚠ **The SOURCE is another matter, and
      it fails on the census's own two extremes: `p19`'s twin adds A WHOLE
      `O(TBL)` VALIDATION PASS (`361.78%`, the census maximum), `p47`'s is an
      ALGORITHM SWAP (`237.01%`, second), `p11`'s is a LIBC SWAP
      (`strlen → memchr`). 10 of the 35 above-floor rows are those three.**
      ✅ **Clean-operator twins only: `25 of 90` rows, `9 of 22` patterns.**
      ⚠ **Each PATTERN's own file is honest — `p19`'s `why` says *"THE VALIDATION
      PASS"* — the overreach is the CENSUS'S AGGREGATION.**
    - ⚠⚠ **M5 — the `±4.6%` FLOOR IS AN `ns` FLOOR APPLIED TO A CALLGRIND
      COLUMN, AND THAT IS A CATEGORY ERROR THE MANAGER PROPAGATED.**
      `p06/NOTES.md` says verbatim *"Take `±4.6%` as the honest inter-binary
      floor for **every `ns` figure** in this file"*, and `.memory/03-measurement.md`
      says of that same instrument *"a LAYOUT POPULATION IS THE WRONG TOOL …
      **callgrind is layout-blind**"* — measuring the `Ir` side of that axis at
      `kernel_exclusive 3002.00` **in all nine runs, a measured ZERO**.
      ✅ **Manager-verified both quotations.** ✅ **The honest `Ir` statement:
      **94 of 100 rows move**, 56 above 1%, **median 1.77%** (35 > 4.6%,
      27 > 10%, 8 > 25%, 6 > 100%).** ✅ **The WALL half (26/100) is sound — that
      is the floor's home instrument.**

    ⚠ **So *"limb 1 prices about a third of the time"* survives QUALITATIVELY and
    `35/100` and `12 of 25` DO NOT survive as limb-1 numbers.**

    ⚠⚠ **THE VERDICT — AND IT IS NOT THE ONE `TASK_128` RETURNED.** **The
    engineer returned SHAPE 1 (*"the bar keeps all three limbs; what it lacks is
    a statement of which column each prices on"*) and refused SHAPE 3 on the
    ground that *"the project owns a column that sees REASONS, publishes it, and
    nobody pointed it at the question."*** ⚠⚠ **`_calib2` withdrew that ground, and
    `TASK_130` went further: the column does not merely fail to see reasons —
    IT RANKS DEAD CODE ABOVE THE MECHANISM.** ✅✅ **THE REVIEWED VERDICT: KEEP ALL
    THREE LIMBS; THE BAR'S TEXT NEEDS NO CHANGE. LIMB 1 prices on the machine
    columns — qualitatively *about a third of the time*, ⚠ NOT `35/100`. LIMB 2
    prices on ASSEMBLY and `Ir` AT THE LEVEL, once the kernel boundary is drawn
    where a real pattern would draw it. LIMB 3 ALONE still prices on nothing
    shown specific to it.** ⚠⚠ **SHAPE 3 — *"the project writes its bar in terms
    of what the programmer MEANS while its instrument sees only what the machine
    DOES"* — IS REFUSED, but NOT on the engineer's ground and NOT for the
    manager's reason: it is refused because the MACHINE columns DO see limbs 1
    and 2, and the column that sees neither is the PROOF column.** ⚠ **The
    nearest true statement is the INVERSE of what the manager suspected, and it
    is `TASK_130`'s: THE PROJECT READS ITS OWN NOVELTY BAR AS A DETECTABILITY
    BAR.**

    ⚠⚠ **THE "CLEAN NEGATIVE" — `p23` CLAIMS ALL THREE LIMBS AND EXHIBITS AT
    MOST ONE — IS TWO-THIRDS RHETORIC, AND `TASK_130` M7 IS THE BETTER FINDING.**
    ✅ **All three cells verify from the committed record** (limb 1
    `−1.39 / −3.66 / +0.13 / −1.60 %`, below floor, sign flips; limb 2
    `verified 16`, `errors 0`, `tcb_items 5`, `proof_fn 0`; limb 3's own `NOTES`
    says *"⚠ The CAUSE is OPEN"* verbatim) — ⚠ **and *"mid-tree"* understates it:
    ✅ manager-recomputed, the range is `7…21` with MEDIAN 12, so `16` is
    **19th of 26**.**

    ⚠⚠⚠ **BUT *"EXHIBITS A LIMB"* HAS NO OPERATIONAL DEFINITION AND THE BAR DOES
    NOT ASK FOR ONE. The bar says *brings a new MECHANISM* — a NOVELTY criterion
    naming no column, no floor and no delta. *"Exhibits"* is the engineer's word,
    and `p23` states each limb as a NOVELTY claim WITH THE BUILT SET ENUMERATED**
    (*"a header field (p05, p07, p16, p17, p19, p36), a compile-time capacity
    (p03, p06, p12), a live length (p04, p14)"*) — **and its limb-1 claim, *a
    comparison of two loop variables*, is CHECKABLY TRUE: on the reviewer's own
    twin census `p23` is the only one of 25 whose added guard compares two moving
    cursors.** ✅ **So the clean negative survives on LIMB 3 ONLY.**
    ⚠⚠ **THE TRANSFERABLE FINDING, AND IT IS BIGGER THAN `p23`: THE PROJECT READS
    ITS OWN NOVELTY BAR AS A DETECTABILITY BAR — the same conflation the engineer
    flagged as systemic, landing on the engineer's own clean negative.**

    ⚠ **OPEN, and NOT to be filled in by inference:** the harm matrix under the
    provenance control; limb 2's *mechanism* (one probe only); and **timing,
    deliberately not measured because `TASK_127` was running and concurrent load
    corrupts a wall-clock block** — ✅ **the right call, and worth copying.**

    ⚠ **Three instrument defects in the engineer's OWN probes, each caught by a
    must-fire arm and disclosed:** a callgrind `fn=`/`cfn=` name-compression
    **silent zero**; an LLVM-hoisted `calls=1` printing `0.42 Ir`/call; and a
    `git ls-tree` resolving its pathspec against the wrong directory, printing
    **`rows: 0`** — *a detector that was not running.* ✅ **The third is
    GENUINELY FIXED: a from-scratch, deliberately different reviewer census
    reproduces `100 / 35 / 26 / 25 / 12` EXACTLY.**

    ⚠⚠ **AND FAILURE-CLASS ENTRY 8 HAS A SECOND INSTANCE IN THE SAME TASK, WHICH
    FINDING 44 MISSED UNTIL THE REVIEW: `TASK_128`'s LIMB-3 `_calibRANGE_bv` IS
    `_calib2` AGAIN** — arm RANGE plus one *unrelated* `by (bit_vector)` assert
    also reads `4 verified`, reported as *"calibration"*. **Both `_calib` arms are
    non-specificity refutations filed as calibrations.** ⚠ **So limb 3's
    `obligations` claim is unsupported for a STRONGER reason than this finding
    first gave.**

    ⚠ **STILL OPEN, and NOT to be filled in by inference:** the harm matrix
    under the provenance control (every arm is Verus-proved memory-safe, so
    nothing has been shown either way); **timing, deliberately unmeasured in BOTH
    tasks because `TASK_127`/`TASK_129` were running and concurrent load corrupts
    a wall-clock block** — ✅ **the right call, twice, and worth copying**; and
    ⚠ **the reviewer's `KIND` classification of the 25 twins is a JUDGEMENT it
    printed for checking: call `p19`'s validation pass *an operator* and the
    clean-operator count goes from 9 patterns back to 12.**

    ⚠ **Contested and disclosed by the reviewer itself: `armPext` — spelling the
    sizing pass `external_body`, which is how 26 patterns spell an unverified
    pass — moves the burden to the TCB column (`2 items / 6 lines`) rather than
    zeroing it. A partial defence of the engineer, which is why the verdict does
    NOT rest on that arm. But `+1 item` is again a COUNT, and moves identically
    for any unrelated trusted item.**

    Evidence: `.tasks/TASK_128_REPORT.md`, `.tasks/TASK_130_REPORT.md`,
    `.temp/t128/` and `.temp/t130/` (`BUILD.sh` / `RUN.sh` regenerate every
    source, binary and log, and delete the binaries).

45. ⚠⚠ **THE IDIOM CENSUS RAN — 49 898 BOUND SITES OVER 991 147 DEDUPLICATED
    LINES OF REAL C IN 22 PROGRAMS — AND THE BUILT TREE MISSES THE
    SECOND-MOST-FREQUENT OPERATOR ENTIRELY.** ⚠ **Engineer work (`TASK_129`),
    NOT YET REVIEWED (rule 9). The manager re-derived the corpus figures, the
    coverage zero and the precision table; ⚠⚠ TWO OF THE MANAGER'S THREE
    VERIFICATION PROBES WERE THE DEFECTIVE ONES THIS TIME AND THE ENGINEER'S
    WERE RIGHT — see the instrument note at the end.**

    ⚠⚠⚠ **THE HEADLINE, AND IT IS A COVERAGE STATEMENT, NOT A QUALITY ONE —
    THE BAR WAS NEVER FREQUENCY-BASED, SO THIS DESCRIBES THE BAR'S CHOICE:**

    ```
                       built tree (255 sites)     php      coreutils    24 GNU pkgs
    index                    dominant            62.3%       75.3%        72.9%
    ptr_offset          ⚠⚠  0 of 255              8.8%        7.4%         5.7%
    str_call            ⚠   1 of 255 (p11 strlen) 22.9%       10.1%        15.9%
    mem_call                 present               5.5%        7.2%         5.1%
    ```

    ✅✅ **REVIEWED AT `TASK_131`. THE ZERO SURVIVES; TWO OF THE SENTENCES THE
    MANAGER WROTE AROUND IT DO NOT.** ⚠⚠⚠ **THIS TABLE IS THE
    GENERATED-INCLUDED POPULATION (49 898 sites); the report's own tables exclude
    generated files (46 948). Deltas ≤ 0.6 pp and no ranking moves — but the
    included population is the one whose measured recall is `0/5`.**

    ⚠⚠⚠ **B1, A BLOCKER AND IT WAS PUBLISHED IN TWO DOCUMENTS: ~~*"`ptr_offset`
    is a TOP-3 OPERATOR IN EVERY ONE OF THE 22 PROGRAMS"*~~ IS **15 OF 22**.**
    **Seven put it FOURTH — glpk 0.9%, pexec 0.4%, findutils 1.3%, grep 2.3%,
    libosip2 2.5%, depregawk 3.7%, sed 5.3%.** ✅ **Manager-recounted from the
    committed census: 15/22, and robust at 15/22 · 17/25 · 17/25 across
    generated-in/out × site-floor.** ✅ **THE TRUE STATEMENT IS NEARLY AS STRONG
    AND IS THE ONE TO QUOTE: *`ptr_offset` OCCURS IN ALL 22 PROGRAMS, RANKS
    SECOND OR THIRD IN 15, SHARE `0.4%`–`26.1%`, MEDIAN `6.9%` — AND IS ZERO IN
    ALL 26 KERNELS.***

    ⚠⚠ **B2 — `0 of 255` IS NOT 255 DRAWS AND THE FRAMING OVERSTATED THE
    EVIDENCE BY ~5000× IN p-VALUE.** **The 255 sites sit in **30 site-carrying
    functions in 26 files cloned from one template**, so the FUNCTION unit is the
    honest one — and even it is generous.** ✅ **Size-matched to the ladder's own
    function-size distribution (the walking fraction rises `6.7% → 27.1%` with
    length, so this matters):**

    ```
    cgnu       FUNCTION unit  expected 2.66 walkers   P(zero) = 0.061
    coreutils  FUNCTION unit  expected 2.81           P(zero) = 0.050
    php        FUNCTION unit  expected 4.86           P(zero) = 0.0047
    ```

    ⚠ **Against the corpus carrying the replication weight the honest figure is
    `p ≈ 0.06` — SUGGESTIVE, NOT DECISIVE. Quote it that way.**

    ⚠ **B4 — the classifier-independent raw regex EXISTS IN NO ARTEFACT.** **The
    manager's *"`845` over PHP, `0` over the kernels, both numbers exact"* cannot
    be re-derived: the reviewer's reconstruction gives **854 / 0**, and ⚠⚠ **its
    FIRST attempt, without a unary guard, returned `ladder = 2` — INDEPENDENTLY
    RE-DERIVING THE MANAGER'S OWN KNOWN-DEFECTIVE PROBE, which matched `8 * (n +
    m)` in `p46`.** ✅✅ **IT NOW SHIPS —
    `common/census/ptr_cursor_regex.py` (`TASK_132`) — AND IT IS WORSE THAN
    REPORTED: THE NUMBER IS A PROPERTY OF THE GUARD, AND SO IS THE ZERO.**
    ✅ **Manager-re-run, four honest guard spellings:**

    ```
                                    v0     v1     v2     v3
    MUST-FIRE planted kernel         2      2      2      2   <- detector alive
    ladder patterns/*/c/kernel.c     2      2      0      0   <- ZERO IS v2/v3 ONLY
    ladder patterns/*/c/*.{c,h}      9      7      2      0
    php                            952    920    916    781
    ```

    ⚠⚠ **UNDER THE GUARD `TASK_131` ACTUALLY SHIPPED, THE LADDER READS `2` —
    both hits `8 * (n + m)` in `p46`, a MULTIPLICATION counted as a dereference,
    i.e. exactly the false positive that task itself named.** ⚠⚠ **AND NO
    VARIANT REPRODUCES `845` OR `854`: the four spellings span `952 → 781` over
    PHP, ±10%, so reading the `845`-vs-`854` disagreement as *"1% off"*
    understated it by an ORDER OF MAGNITUDE.** ✅ **`845` IS STRUCK. The `0`
    stands and must be quoted WITH ITS GUARD; *"three independent instruments"*
    is true of the census, the signature-shape bucketing and `v2`/`v3` — not of
    any regex you might write yourself.**

    ⚠ **`str_call` at 1 of 255 is a DISCLOSED DESIGN CHOICE whose coverage
    consequence had not been measured: `p12` and `p13` call no `str*` function
    at all, and `p13/c/kernel.c:16` says so in its own words** (*"The copy is
    spelled out rather than calling `strncpy` itself"*). ⚠⚠ **The manager's own
    check of this CONTRADICTED the engineer and the manager was wrong: a
    `grep -c` counts `strncpy` three times in `p13` and ALL THREE ARE IN
    COMMENTS. The census excluded comments; the manager's grep did not.**

    ✅✅ **THE REPLICATION ARM — THE CONTROL THAT MAKES A CENSUS MEAN ANYTHING —
    LANDED ON THE STRONG SIDE, AND AT `n = 22` RATHER THAN THE `n = 2` THE TASK
    SCOPED.** ⚠ **The manager's coda had two corpora; the engineer found a third
    IN THE MANAGER'S OWN UNCHARACTERISED FILE LIST — 24 upstream GNU packages,
    2 162 distinct `.c`, 785 480 lines.** **Result:**

    > ⚠⚠ **THE ORDINAL TOP IS A PROPERTY OF C; THE DISTRIBUTION IS A PROPERTY OF
    > THE PROGRAM.** **`index` is the top operator in 21 of 22 programs and
    > `const` the top bound source in 19 of 22 — but the SHARES swing 42–50
    > percentage points** (`const` 12.7–54.7, `none` 6.6–56.1, `local`
    > 5.3–50.8) **and SECOND PLACE FLIPS BETWEEN FOUR CATEGORIES.**

    ✅ **So a frequency-argued admission bar gets a FIRST PLACE and nothing below
    it. THAT RETIRES `TASK_113`'s REQUEST HONESTLY, which nothing before this
    had done** — and it is the *disagreement* outcome the task named as the
    stronger one, arriving in a partial form nobody predicted.

    ✅ **REVIEWED (`TASK_131`), AND THE REPLICATION ARM CAME OUT STRONGER THAN
    THE ENGINEER ARGUED ON ONE AXIS AND WEAKER ON ANOTHER:**

    - ✅ **B8 — PHP IS *INSIDE* THE GNU SPREAD ON ALL 15 HEADLINE FIELDS**, ranks
      4th–15th of 22, `|z| ≤ 0.72`, never an extreme. ⚠ **The manager's worry
      that *"21 of 22 are GNU packages in one house style and PHP is the lone
      outsider"* does not bite: the informative statistic is the RANK, not the
      range, because two of any 21 are outside by construction.** ⚠ **And the
      report's own §E caveat *"PHP's 23% `str_call` share is the highest of the
      22"* is FALSE — it is 8th, behind units 56.5, libosip2 44.9, wget 32.7,
      make 31.2 — and it contradicts the report's own §C table.**
    - ⚠⚠ **B7 — CONTENT-HASH DEDUP DOES *NOT* REMOVE GNULIB, and the engineer's
      dedup defence is refuted: 1223 repeated-basename pairs survive, 197 are
      ≥99% line-identical and 611 ≥90%; `150 451 of 861 940` non-blank lines —
      **17.5%** — are redundant.** ✅ **Arm that must fire, a greedy re-dedup at
      0.90 dropping 657 files and 15.6% of lines: the OPERATOR headline HOLDS
      (`index` tops 20 of 21) but the BOUND-SOURCE headline WEAKENS — `const`
      tops `19/22 → 16/21`, second place goes from four categories to SIX, and
      the `const` spread widens `42.0 → 50.2` points.** ⚠⚠ **Which makes the
      engineer's own conclusion STRONGER: *the distribution is a property of the
      program* survives its own strongest attack.**

    ⚠⚠ **THE FIELD THE ENGINEER DECLARED UNUSABLE RATHER THAN PUBLISHING, WHICH
    IS THE BEHAVIOUR TO COPY:** 60 hand-classified sites give **operator
    `60/60`**, **bound source `54/60`**, **check `45/60` — and `check`'s
    `earlier` label is right 3 of 10, with DIRECTIONAL errors.** ✅ **Named
    cause: a `const`-index site's bound expression contains no identifiers, so
    `check` is FORCED to `none` while an `if (argc > 4)` sits on the line above
    — 26–33% of all sites.** ⚠ **Per-category precision on `bound` is what makes
    the headline safe: `const 25/25`, `none 11/11`, `field 9/9`, `param 3/3`,
    `global 2/2` — and ⚠ **`local 3/7`, `cursor 1/3`**. **NOT ONE disagreement
    moved a site into or out of `const` or `none`.** ✅ **All figures
    manager-re-run from `agree.py`.**

    ⚠ **AND THE ENGINEER DECLINED TO PUBLISH THE LADDER-VS-CORPUS BOUND-SOURCE
    COMPARISON, correctly: the ladder reads `param 51.4%` because all 255 sites
    are leaf kernels taking `(buf, len)` from a shared driver. That is a HARNESS
    ARTEFACT, not a mechanism gap.** ⚠⚠ **A weaker engineer ships that number.**

    ⚠⚠⚠ **THE MANAGER'S OBJECTION — *"if `param 51.4%` is a harness artefact,
    why is `ptr_offset 0` not one?"* — IS SETTLED AND DISMISSED, MEASURED, AND
    THE MEASUREMENT RUNS THE OTHER WAY.** **The objection's premise was *a kernel
    handed an explicit length has little reason to walk*, which predicts a large
    depression among functions taking a pointer AND a length. ✅ `TASK_131`
    bucketed every corpus site by its enclosing function's signature shape:**

    ```
    fraction of site-carrying FUNCTIONS that walk:   ALL   PTR+LEN  LADDER-shape
      cgnu                                           9.8%    9.2%      8.7%    flat
      php                                           15.6%   22.4%     18.2%    HIGHER
      coreutils                                     10.8%    9.1%      4.5%
      the built tree                                  0/30    0/28      0/7
    ```

    ⚠ **`PTR+LEN` walks at the SAME rate or a HIGHER one. The rates would have to
    fall to ≈0 for the objection to hold and they are 3–18%.** ✅ **So the zero is
    NOT an artefact of the kernel signature, and neither published document
    needed retracting on that ground.**

    ⚠⚠ **BUT ONE MANAGER PREMISE INSIDE THE OBJECTION WAS WRONG IN DETAIL AND WAS
    MARKED ✅ IN TWO PLACES — THE ✅ IS STRUCK: ~~*"every C rung has the
    signature `kernel(const T *v, size_t off, size_t len)`"*~~. **21 OF 26 TAKE
    FOUR PARAMETERS** (`buf, buf_len, off, len`); only `p01`/`p19`/`p42`/`p46`
    are three-param and `p02` is five.** ⚠ **Manager-re-verified. The manager
    sampled six patterns, three of the six happened to be three-param, and for
    the other three the grep PRINTED NOTHING AND THE BLANK WAS READ AS
    AGREEMENT — the failure class this project names most often, committed inside
    the check that was supposed to catch a finding.**

    ⚠⚠⚠ **AND THE THIRD READING — THE MANAGER'S OWN, THE ONE IT CALLED *"the
    most interesting of the three"* — IS DEAD. ~~*"the zero is forced by the
    ladder's comparability requirement: safe Rust cannot express a pointer
    cursor, so the `identity` pin plus each pattern's `required` idiom pins every
    C rung to an indexed spelling."*~~ ✅ NOTHING FORCES IT. THE RUNGS SIMPLY WERE
    NOT WRITTEN THAT WAY. Four independent grounds, three of them one `grep`
    each:**

    1. ⚠⚠ **THE PREMISE IS HALF FALSE — NO `identity` PIN TOUCHES THE C RUNG AT
       ALL.** ✅ **Manager-recounted from all 26 records: the pins are
       `unsafe vs verus` (52) and `safe_naive vs safe_naive_verus` (2). C is not
       in any of them.**
    2. **`.memory/01-ladder.md` requires rungs to be *"semantically equivalent on
       well-formed input (same checksum)"* and R1 to be *"idiomatic C99"* —
       comparability is SEMANTIC, NOT SYNTACTIC. A walking R1 leaves R2
       untouched.**
    3. **`forbidden` is the only idiom key with a gate verdict, and NOT ONE
       `forbidden` ENTRY IN 26 PATTERNS EXCLUDES A C POINTER CURSOR.**
    4. ✅ **The decisive experiment: a pointer-cursor respelling of `p11` — the
       walkiest pattern — checksum-equivalent over 2000 windows with a
       must-differ arm that fires, scored through imported
       `check.py::spelling_matches`: 5 `required` broken, 0 `forbidden`
       violated; for `p01`, 0 and 0. The five are the C HALF of per-language
       entries whose Rust half already differs, and twelve patterns already use
       that `{"c":…,"rust":…}` mechanism.**

    ⚠ **OPEN, and the one genuinely structural constraint the review found — it
    runs through R5, NOT R2: several patterns pin subtraction-first C guards
    because *"the additive form overflows `usize` and Verus rejects it"*. That
    constrains ARITHMETIC FORM, not cursor type. Nobody has pushed on it.**

    ⚠⚠⚠ **WHAT THIS DOES AND DOES NOT LICENSE. IT IS A MEASURED COVERAGE GAP AND
    IT IS THE FIRST FREQUENCY EVIDENCE THIS PROJECT HAS EVER HAD — AND IT IS NOT
    A ROW.** **RECAP's standing rule binds: RUN A PROPOSED AXIS'S NOVELTY CLAIM
    BEFORE WRITING THE ROW; both manager-proposed axes died on a claim one
    `grep` plus one run would have settled.** ⚠ **The specific reason to expect a
    pointer-cursor row to DIE is already on file: safe Rust's answer to a pointer
    walk is an ITERATOR, which is a DIFFERENT REPRESENTATION and not *"R4 plus a
    check"* — `TASK_055` §2.8's trap, and exactly how `CVE-2021-23017` died when
    `Vec::push` deleted the bound instead of checking it.** **UNPROBED. Do not
    write a row on this paragraph.**

    ⚠ **BOUNDS ON THE CLAIM, from the engineer:** the 90/100/75 error rates are
    **measured on PHP only**; the census is a **SPATIAL** instrument, so `p18`,
    `p22`, `p27`, `p38`, `p42`, `p47` are INVISIBLE to it and absence there is
    not evidence; `local` is a bucket at 43% precision; and ⚠ **the engineer
    named its own most-attackable call — it hand-labelled `bound` SEMANTICALLY
    (tracing one assignment) rather than by the classifier's syntactic rule, so a
    reviewer could fairly say the honest reading is *"the classifier implements
    its definition perfectly; the definition is 43% useful."* Both readings are
    recomputable from `hand_labels.tsv`.**

    ✅ **FOUR SELF-CAUGHT INSTRUMENT DEFECTS, ONE OF WHICH WAS HIDING 29% OF
    PHP:** `#if`/`#else` desyncs brace depth (`fopen-wrappers.c` ends at `+3`,
    `nstrftime.c` at `−2`) and a global depth counter then silently drops every
    later function — **coverage 70.9% → 78.3%, and the counter is gone**; K&R
    definitions yielded ZERO sites; `_stmt_start` was a stub returning `i-40`;
    `*(T*)(p+e)` parsed empty. **All four caught by self-tests written BEFORE any
    counting, with a must-fire arm that fires.** ✅ **Recall check: 0 false
    positives in 40 raw draws, 23/23 sites found in hand-written C, and `0/5`
    inside bison-generated files — which were then flagged and EXCLUDED.**

    ⚠⚠ **INSTRUMENT NOTE, AND IT IS THE MANAGER'S: verifying this finding, TWO
    OF THE MANAGER'S THREE QUICK PROBES WERE WRONG AND THE ENGINEER'S WERE
    RIGHT** — a `ptr_offset` regex that matched BINARY `*` (`8 * (n + m)` in
    `p46`) and a `str*` grep that counted COMMENTS. ✅ **Both were caught by
    checking WHAT the probe had matched rather than trusting the count.**
    ⚠ **A one-line verification grep is an instrument and gets no exemption.**

    ✅ **CLEAN NEGATIVES THE REVIEW LOOKED FOR AND DID NOT FIND** — the detector
    is alive (a PLANTED walking kernel carrying `p01`'s exact signature,
    checksum-equivalent over 4096 random windows with its must-differ arm firing,
    is labelled `ptr_offset` by BOTH instruments); ✅ **`REBUILD.sh` reproduces
    every artefact BYTE-IDENTICALLY** (three corpus JSONs, `agree.txt`,
    `perprog.txt`, `hand_labels.tsv`, the manifests, coverage
    `78.274 / 83.164 / 81.999 %`); ✅ **`check` was GENUINELY withheld** — it
    appears only as its own error rate and in `rank.txt` marked *"NOT limb 3"*,
    and `perprog.py` never reads it; ✅ **the generated-file exclusion is ONE
    code path over all four populations**, not an arm-specific bias (coreutils
    simply has zero generated files); ✅ **function size is not a hidden
    confound**; ✅ **no `forbidden` entry anywhere excludes C pointer
    arithmetic.**

    ⚠ **B10 — BOTH READINGS OF THE HAND-LABEL SCORE RECOMPUTED, AND THE
    ENGINEER'S SELF-CRITICISM WAS ONE POINT TOO HARSH: adjudicating all six
    disagreements against the classifier's OWN rule, five are definitional and
    ONE IS A GENUINE RULE VIOLATION. So SEMANTIC `54/60 = 90.0%` and SYNTACTIC
    `59/60 = 98.3%` — not `60/60`.** ✅ **Publish the SEMANTIC number: it bounds
    the ranking, which is what the census is for.**

    ⚠ **B9 — a FIFTH, UNDISCLOSED instrument defect with a MEASURED NULL EFFECT:
    `scan_locals` scans a declaration's INITIALISER, so `int errind =
    ap_php_optind;` registers a file-scope GLOBAL as a LOCAL. With the
    initialiser skipped, 19 of 7697 sites move (`0.25%`, `local −14 / global
    +13`) and NO RANKING MOVES.**

    ⚠⚠ **B3 — AND THE ONE ARM THAT DOES NOT REPRODUCE IS THE ONE THAT LICENSES
    *"the pipeline is not lossy by construction"*: re-running the engineer's own
    `crosscheck.py` against its own byte-identical inputs differs in 18 OF 27
    CELLS (php `strlen` 586→633, cgnu `sprintf` 646→561), and *"coreutils is 0 on
    eight of nine"* is FIVE of nine — two of them trivial `0`-vs-`0`, so **3 of 7
    non-trivial**. ✅ **Cause identified from mtimes: the table was captured
    BEFORE the last instrument fix.** ⚠ **Report-only — it is in no published
    document — but it is a new control shape and it is landed in
    `.memory/03-measurement.md` as entry 10.**

    Evidence: `.tasks/TASK_129_REPORT.md`, `.tasks/TASK_131_REPORT.md`,
    `.temp/t129/` and `.temp/t131/` (`REBUILD.sh` in each). ⚠ **The three sha256
    manifests are 956 K in gitignored scratch and PROMOTING THEM IS OWED — a
    census whose corpus cannot be re-identified is a census nobody can check.**
    ⚠ **So is B4's raw-regex script, which currently exists nowhere.**

46. ⚠⚠⚠ **A CHECK WHOSE OWN OUTPUT IS AN INPUT TO THE ARTEFACT IT CHECKS — A
    NEW FAILURE SHAPE, AND IT PASSES THE MUST-NOT-FIRE ARM AND STILL OSCILLATES
    FOREVER.** ⚠ **Engineer work (`TASK_127`), NOT YET REVIEWED (rule 9), which
    is why it is HERE and not in `.memory/03-measurement.md`'s failure-class
    list — where it is OWED as entry 10.** ✅ **The manager re-ran the deciding
    arm end to end** (plant → gate `FAIL` → printed fix → gate `PASS`).

    **The task asked for a content pin on `results/tables/*.md` and named three
    candidate designs. The one the manager leaned to — RECOMPUTE AND COMPARE —
    won, ⚠ but the manager's stated REASON for doubting it was the wrong
    reason.** **The hazard was not reporter volatility. It was this:**

    ```
    report.py rendered the gate record's `verdict` -- an OUTPUT of the very run
    the new stage runs in.

      run N    9c fires -> rep.fail -> this run's verdict is FAIL
      report.py         -> the table now prints  verdict `FAIL`
      run N+1  render(FAIL record) == table -> FRESH -> verdict PASS
      run N+2  render(PASS record) != table -> FIRES AGAIN -> forever
    ```

    ⚠⚠ **IT BEGINS THE FIRST TIME THE CHECK DOES ITS JOB, SO THE MUST-NOT-FIRE
    ARM ON AN UNCHANGED TREE — WHICH THE MANAGER SPECIFIED AS *THE* DECIDING ARM
    — WOULD HAVE PASSED AND MISSED IT.** **Measured before fixing: 19 of 26
    tables changed bytes when the record's `verdict` changed.** ⚠ **`rep.shout`
    is WORSE, not better: `loud` is rendered too.**

    ✅ **Fixed at the source — `report.py` no longer renders `verdict` — with a
    standing detector (`harness/tools/table_render_inputs.py --selfref`) that
    exits 1 if any run-scoped key reaches the render again. ✅ Manager-re-run:
    `0` of `26 × 9`.** ⚠ **The detector is deliberately OUTSIDE the gate: wiring
    it in would put it inside the digest and cost a sweep to maintain.**

    > ⚠⚠⚠ **THE QUESTION THIS ADDS TO THE FAILURE-CLASS LIST, AND IT IS NOT ONE
    > THE EXISTING ENTRIES ASK: *DOES THIS CHECK WRITE ANYTHING THE THING IT
    > CHECKS READS?*** **The list's standing question — *what would make it
    > FAIL?* — is satisfied here and does not help.**

    ⚠ **THE RULE THAT COMES OUT OF IT, now in `report.py`'s own docstring: a
    field a gate run WRITES must not be rendered into an artefact that same gate
    run CHECKS.** **`loud`, `controls_json`, `idiom_audit` and `contract_sha256`
    are deterministic functions of the committed sources and are safe;
    `verdict` and `blocked` are functions of the RUN.**

    ✅ **THE MANAGER'S §B1 DESIGN IS DEAD BY MEASUREMENT: hashing the gate record
    WHOLE would have reported `STALE` on 21 OF 26 PATTERNS' OWN GATE RUN** (two
    honest sweeps of an unchanged tree; sanitizer 20, miri 14, adversarial 7,
    notes 2). ⚠ **`.memory/` says 17 of 26 and the engineer measures 21 — that
    section's own last paragraph already says THE COUNT IS A DRAW.** ✅ **The
    subset `report.py` actually reads is identical 26/26, and it was established
    BY MUTATION rather than by reading source: `{contract_sha256,
    controls_json, idiom_audit, loud}` read; `verdict`, `blocked`, `failures`,
    `notes`, `sanitizer`, `miri`, `adversarial`, `source_sha256` NOT read.**

    ✅ **STAGE `9c` SHIPS AND THE MANAGER RE-RAN ITS DECIDING ARM INDEPENDENTLY.
    Planting one digit into `p03`'s published table:**

    ```
    stage 9   ok   ... cites contract c51288b0c9f6, which is this run's   <- GREEN
    stage 9c  FAIL ... is STALE IN ITS CONTENT: 2 line(s) differ           <- RED
    check.py: FAIL   ->  harness/report.py p03  ->  check.py: PASS, 9c FRESH (61a0eb453665)
    ```

    ⚠⚠ **THAT IS THE `TASK_121` GAP CAUGHT LIVE IN ONE RUN: THE CONTRACT PIN
    GREEN WHILE THE CONTENT IS FALSE.**

    ⚠⚠⚠ **REVIEWED AT `TASK_132`, AND THREE OF THIS FINDING'S CLAIMS DID NOT
    SURVIVE. READ THESE BEFORE QUOTING ANY OF IT.**

    ⚠⚠⚠ **(i) BLOCKER — *"9c SUBSUMES 9"* IS FALSE, and it is written in BOTH
    docstrings and above.** ✅ **Driving the real `check_published_tables` and
    `check_table_render`: with NO GATE RECORD — the project's own three-command
    loop for a NEW pattern — the render carries no contract line, so STAGE 9
    FIRES `UNPINNED` WHILE 9c SAYS `FRESH`. Control with the record present: both
    `FRESH`.** ⚠ **Stage 9 is kept for three good reasons (no import, survives a
    broken `report.py`, three verdicts naming different fixes) — but *"subsumes"*
    is the kind of sentence that gets believed and makes stage 9 look
    removable.**

    ⚠⚠⚠ **(ii) BLOCKER — THE ONE-RUN LAG IS *NOT* "STATUS QUO", AND THE MANAGER
    ACCEPTED THAT DEFENCE WHEN LANDING THIS FINDING.** ✅ **`TASK_132` reproduced
    it end to end with two real `check.py p03` runs: add one UNPINNED
    `patterns/*/controls/*.json` — stage 9b `rep.shout`s and does NOT fail —**

    ```
    run 3   PASS,  9c FRESH        <- a user commits HERE
    run 4   nothing changed:  FAIL,  9c STALE-CONTENT, 1 line
    ```

    ⚠⚠ **AND THE TRIGGER IS IN NEITHER DIGEST — not `measurement_sources`, not
    the gate `source_sha256` glob — so `--check-stale` CANNOT SEE IT.**
    ⚠ **The *"stage 9 has the same shape"* defence conflates two lags: stage 9
    compares LIVE `spec.md` against the table, so ITS detection has no lag; 9c's
    lag IS in the detection.** ✅ **Frequency bounded, which the engineer left
    open: 26 `rep.shout(` sites over 12 sections, 5 firing today, 7 latent.**
    ⚠ **The proposed repair — compare against the four fields THIS run has
    already computed — is REASONED FROM SOURCE, NOT BUILT OR MEASURED. OPEN.**

    ⚠⚠ **(iii) MAJOR — THE SELF-REFERENCE DETECTOR IS A DENY-LIST, NOT A
    CENSUS.** **Its *"9 run-scoped keys"* is a HAND-WRITTEN TUPLE and 25 of the
    record's 34 keys are unclassified.** ⚠⚠ **A `report.py` that rendered
    `table_render` — STAGE 9c's OWN VERDICT — measures `26/26 READ` while
    `--selfref` prints `0` and exits `PASS`.** ⚠ **This project's most-named
    failure, inside the detector built to prevent it.** ✅ **Recommended repair,
    not yet built: INVERT IT TO AN ALLOW-LIST over the already-measured read set
    `{contract_sha256, controls_json, idiom_audit, loud}`.**

    ✅ **CLEAN NEGATIVES — do not re-run these: `RENDER-ERROR` IS a failing
    verdict (all six 9c branches driven; four force `FAIL`); the `--selfref`
    must-fire arm DOES fire and independently reproduces the `19 of 26`; grepped
    `verdict` and FAIL-count agree with the record `130/130`; and three fresh
    draws of `p03` move exactly the four keys the docstring names, none of them
    read by `report.py`.**

    ⚠ **THE MANAGER'S "CHEAPER ALTERNATIVE" WAS ANSWERED ON THE RECORD AND
    AGAINST THE MANAGER: *"just always re-render"* WAS ALREADY PROPOSED at
    `TASK_096_REPORT` 7b, the check was taken and THE RECIPE NEVER WAS — nothing
    in the tree runs `report.py` today — and the class then recurred TWICE
    (`p09` 16 tasks stale, `p23` no table at all).** **A recipe is prevention
    that holds only while a human runs it, leaves NO ARTEFACT, and structurally
    cannot report an ABSENT table.** ✅ **Take both.**

    ✅ **THE RIDE-ALONGS LANDED:** `p23`'s `controls.log` now has a
    `controls_pin.json` (`derived_from_sha256`, stage 9b covers it with zero new
    gate code; must-fire arm run and the four sizes `586/608/614/612` HOLD), and
    `common/layout/data/` is **ACCEPTED with the acceptance written into
    `common/layout/README.md`** — the file that would otherwise need the pin,
    not just a report. ⚠ **And `predictions_p01oos.json`'s sha256 is a
    PRE-REGISTRATION COMMITMENT; do not "upgrade" it to a staleness pin.**

    ⚠ **THE PROMOTION CLASS WAS MIS-COUNTED AND IT IS SMALLER: `grep -l
    json.dump` also matches `json.dumps`, and six of the 31 render `spec.md`
    into the tree. TRUE CLASS: 22 files / 13 patterns, one already pinned ⇒
    **21 outstanding across 12 patterns**, costing 21 pins + **12 GATE RE-RUNS,
    NOT A SWEEP** (the glob is `controls/*.py`).**

    ⚠⚠ **A SECOND LIVE INSTANCE, AND IT IS A DRAW PUBLISHED AS A FIGURE:
    `p23/NOTES.md` said `k_selfpivot` *"prints 3910418957284214752"* while its
    OWN COMMITTED `controls.log` said `…814`. Five runs of ONE binary gave THREE
    distinct values including both, because `k_selfpivot` on an all-equal record
    reads uninitialised stack BY DESIGN — while the MIXED must-be-clean arm was
    constant 5/5.** ✅ **Corrected, and named in `controls_pin.json`'s
    `pin.not_covered`, because it makes the log unreproducible for a reason
    BEYOND ASLR and paths.**

    ⚠ **DISCLOSED AGAINST ITSELF, and worth recording because the disclosure is
    the point: the engineer launched the sweep with `nohup … &`, which
    `CLAUDE.md` constraint 2 forbids BY NAME, resolved to kill by exact PID, and
    found it had already finished normally. Nothing was interrupted and no
    result is affected** (per-pattern `rc=`, 26 complete logs, every mtime after
    the last edit). ⚠ **A rule broken and self-corrected is still broken.**

    ⚠⚠ **AND A MANAGER ERROR THAT COST THE ENGINEER A RUN: the publishing-chain
    recipe in `TASK_127.md` §F — copied from `TASK_121_REPORT` §A — writes
    `synthesis/licence.py --emit` with NO PATH. `--emit` TAKES A PATH; bare, it
    exits `rc=2` and writes NOTHING, after which `synthesize.py` rebuilt
    `synthesis.md` against a stale `licence.json` and produced **209
    `LICENCE STALE` occurrences**.** ✅ **Correct spelling:
    `--emit synthesis/licence.json` and `--emit synthesis/outward_ir.json`.**
    ⚠ **Caught only because the engineer logged `rc=` per step.**

    ✅ **Sweep and chain, ✅ manager-re-verified after landing: 26 patterns,
    3454 s, `24 PASS + 2 PASS-WITH-BLOCKED-ROWS`, 0 FAIL lines, stage 9 FRESH
    26/26, stage 9c FRESH 26/26, `52 records 0 STALE`,
    `results/synthesis.md` = `c199a031`.** ⚠ **`synthesis.md` MOVED
    (`fbe0bc22 → c199a031`) and here the move is FORCED — this task moved every
    gate `source_sha256`, so the old pins are 26 genuinely stale ones.**
    ✅ **By-product worth keeping: the redraw is BYTE-IDENTICAL to `TASK_125`'s,
    so the documented ±7 phase is STICKY IN THIS ENVIRONMENT, not per-run
    random.**

    ⚠ **OPEN / not done:** ⚠⚠ **the one-run lag — see (ii): the engineer's own
    invitation to attack it was right and the defence was not**; `report.py`
    RAISES on a malformed
    `idiom_audit` rather than degrading (9c catches it as `RENDER-ERROR`; the
    brittleness is not fixed); stages 9/9b/9c are absent from `check.py`'s module
    docstring list; and ⚠⚠ **`temp_citations.py` CANNOT SEE a path a committed
    Python file ASSEMBLES with `os.path.join(REPO, ".temp", …)` — its regex needs
    a literal `.temp/`. Reported, not fixed, and it is the SECOND defect found in
    that checker by ordinary use.**

    Evidence: `.tasks/TASK_127_REPORT.md`, `.temp/t127/`.

47. ⚠⚠⚠ **THE TEMPORAL AXIS IS NOT WHAT THE MANAGER TOLD THE USER IT WAS. TWO
    MANAGER STATEMENTS, BOTH MADE IN CONVERSATION AND BOTH WRONG, CORRECTED HERE
    BEFORE THEY COULD BE ACTED ON.** ⚠ **Manager measurement, UNREVIEWED, and it
    is the premise of the whole temporal programme — ATTACK IT FIRST.**

    ~~*"Three of the four temporal outcomes have no cost gradient to price."*~~
    ⚠⚠ **FALSE. `p27` measures the gradient and it is EXACTLY THE SHAPE A READER
    EXPECTS.** ✅ **Manager-re-derived from `results/p27-handle-table.json`,
    kernel-exclusive `Ir`/call at `-O3 isolated`:**

    ```
                  small.bin    large.bin
    c-gcc            844.57      3440.09
    safe_naive      1041.14      4562.38     <- +23% / +33% over C
    safe_tuned      1031.63      4530.38
    unsafe           921.65      3868.56     <- recovers ~60% of the gap
    verus            921.65      3868.56     <- identical, `exact` at O3
    ```

    ✅ **`R3 − R4 = +109.98` / `+661.82 Ir`/call. THE TEMPORAL SAFETY TAX IS REAL
    AND LARGE.** ⚠ **The four outcomes are a claim about whether a NEW row ADDS
    anything, not about whether temporal safety COSTS anything: `p28`/`p29` died
    as DUPLICATES OF `p27`'s MECHANISM (outcome 2), not because the mechanism is
    free. The manager collapsed the HARM axis into the COST axis.**

    ~~*"`p27`'s proof does not cover the bug class the row is about."*~~
    ⚠⚠ **ALSO FALSE, AND THE TRUTH IS BETTER: `p27`'s R5 PROVES THE TEMPORAL
    OBLIGATION, WITH A LINEAR RESOURCE.** **`verus.rs`'s own header: *"Every
    other R5 in this tree proves a SPATIAL fact — an index is inside a buffer.
    p27's central obligation is a TEMPORAL one: at the moment of the read, the
    record still exists. It is carried by a linear resource, `PointsTo<u8>`,
    which `vstd::raw_ptr::deallocate` CONSUMES, so a read after a free has no
    permission to present and the proof fails."*** ✅ **And *"the temporal
    property costs none of [the TCB items]"* — five of the seven are the spatial
    accessors every pattern ships.** ⚠ **The mutant arm exists: delete
    `live[h] = 0` and the loop invariant cannot be re-established (`NOTES.md` 10,
    M2).**

    ⚠⚠⚠ **SO THE HONEST STATE OF THE TEMPORAL AXIS, AND IT IS A SHARP
    DISTINCTION NOBODY HAD DRAWN: VERUS *CAN* STATE *"NO USE-AFTER-FREE"* — a
    LINEAR `PointsTo`, proven, zero extra TCB (`p27`). VERUS *CANNOT* STATE
    *"MUST EVENTUALLY FREE"* — `Tracked<Dealloc>` is AFFINE, a proof may simply
    DROP it, three encodings burned and an attack that verifies `19/0` AND LEAKS
    (`p42`).** ✅ **LINEARITY IS THE LINE, and that is a publishable sentence.**

    ⚠⚠ **A TENSION BETWEEN TWO COMMITTED DOCUMENTS, FOUND HERE AND NOT RESOLVED
    — DO NOT PICK A SIDE WITHOUT MEASURING:** `.memory/06-catalogue.md`'s `p42`
    cell says ***"`p27` proves deallocation is LEGAL, never that it HAPPENS"***,
    while `p27/verus.rs` SAFETY(5) says ***"deallocate is called exactly once per
    record … so there is no double free, and every slot alive at the end is
    freed, so there is no leak."*** ⚠ **Both are committed. The likely
    resolution is that `p27`'s epilogue frees everything by construction while
    `p42`'s bug is an EARLY RETURN — but that is a guess and the manager's
    guesses on this class have been wrong three times today.**

    ⚠⚠ **AND THE FOUR-OUTCOME LAW HAS A SCOPE NOBODY HAD READ: it says
    *"POINTER-BACKED STRUCTURE"* and it means it.** **It makes NO claim about a
    temporal bug in a FLAT GROWABLE BUFFER (`p25`, `realloc` invalidating a saved
    pointer — the ONE catalogue row this project has run NOTHING on), a
    STACK-LIFETIME bug, or ITERATOR INVALIDATION.** ⚠⚠⚠ **AND ALL FOUR OUTCOMES
    NAME A RUNTIME MECHANISM — an allocator, a discriminant test, a refcount.
    THE BORROW CHECKER IS A SECOND TEMPORAL MECHANISM, IT ACTS AT COMPILE TIME,
    AND IT COSTS ZERO INSTRUCTIONS. The law does not contain it, so *"safe Rust's
    temporal guarantee is a guarantee about the ALLOCATOR"* MAY BE INCOMPLETE
    RATHER THAN WRONG.** ⚠ **Untested. It is the first thing the temporal
    programme should attack, and `p08` — *"a tooling-and-expressiveness result,
    not a performance one"*, `R4 == R5 exact` at both levels — is the spatial
    precedent for what that shape ships as.**

    ⚠ **UNMEASURED AND WORTH ONE PROBE: `p27`'s safe rung is
    `Vec<Option<Box<Rec>>>`, NOT `RefCell`. The `Rc<RefCell<…>>` shape — what
    real Rust reaches for on a graph, with a runtime borrow flag and a panic path
    — appears only in discarded `p28` probes and has never been priced on this
    ladder.**

    ⚠⚠ **INSTRUMENT LIMIT, and it bounds every proof-cost claim this project can
    ever make: `identity` is PINNED `exact` at `-O3` for `unsafe vs verus` in
    26 of 26. An R5 whose proof COST instructions would FAIL THE GATE rather than
    publish a nonzero proof cost. So *"the proof is free"* is true and is also
    the only answer this instrument can return.**

    Evidence: `results/p27-handle-table.json`, `results/gate/p27-handle-table.json`,
    `patterns/p27-handle-table/verus.rs` (header + SAFETY 4/5),
    `.memory/01-ladder.md` (the four outcomes and the new scope note).

48. ⚠⚠⚠ **THE BORROW CHECKER IS AN *ALIASING* MECHANISM, NOT A TEMPORAL ONE —
    AND THAT ANSWERS THE SCOPE NOTE `TASK_133`'s SESSION LEFT OPEN. ALL FOUR
    NON-SPATIAL CANDIDATES DIED.** ⚠ **Engineer work (`TASK_134`), NOT YET
    REVIEWED (rule 9). The manager re-ran the load-bearing arms — see the
    verification note at the end.**

    ⚠⚠ **THE RESULT IS TWO-DIRECTIONAL, WHICH IS WHY IT SETTLES ANYTHING.**
    `.memory/01-ladder.md`'s scope note said the borrow checker *"is a second
    temporal mechanism, acting at COMPILE TIME at ZERO INSTRUCTIONS, so the law
    may be INCOMPLETE"*, and marked it untested.

    - **It REJECTS programs that cannot have the bug.** Seven controls, all
      `#![forbid(unsafe_code)]`, ✅ **manager-recompiled**: a `struct S { v: u32 }`
      with no heap and no container prints **`E0502`, the message identical to
      `p25`'s safe rung**; a `Vec` with capacity 64 reserved and length 1 —
      which provably cannot reallocate — prints **`E0502`**; a stack `[u8; 16]`
      prints `E0506`; a single integer local prints `E0597`/`E0515`.
    - **It ACCEPTS a real use-after-recycle in the same data structure.**
      `pop` ends the element's lifetime, `push` recycles the slot, the read gets
      the new occupant: **`v[2] = 9999` where 30 was marked, `buffer moved:
      false`, ZERO `unsafe` blocks, `forbid(unsafe_code)`, and MIRI-CLEAN.**
      ✅ **Manager-re-run WITH A POSITIVE CONTROL that must fire** — a genuine
      use-after-free scores `rc=1` and *"alloc245 has been freed, so this
      pointer is dangling"*, while the subject scores `rc=0` and zero UB lines.

    > ✅ **So the borrow checker is neither SOUND nor COMPLETE for the temporal
    > property. It is a FIFTH mechanism and it is not a temporal one — the four
    > runtime outcomes STAND, and OUTCOME 3 (*"the type system is SILENT"*)
    > EXTENDS VERBATIM from pointer-backed structures to FLAT GROWABLE BUFFERS**,
    > which was the scope note's own first exclusion and is `p25`'s structure.

    ⚠⚠ **AND IT RETIRES *"SAFE RUST CANNOT EXPRESS THE BUG"* AS A DISTINGUISHING
    CLAIM FOR THREE CANDIDATES AT ONCE. THIRD INSTANCE OF THE FAILURE MODE**
    (`TASK_093`'s `E0382`, `TASK_094`'s `E0502`, now these) — **the compile error
    is real and is not about the row's bug.** ⚠ **It cost about ten minutes to
    check, and the project's own method rule is what caught it.**

    ⚠⚠⚠ **`p25` IS REFUSED, AND THE MANAGER'S OWN PREDICTION ABOUT IT WAS WRONG
    IN AN INTERESTING WAY.** The catalogue cell said *"a stale INDEX is not a
    stale POINTER: if the port uses indices the bug vanishes into `p04`'s
    class"*. ✅ **Manager-re-run: the index port has NO BUG AT ALL** — `realloc`
    **copies**, so `v[k]` names the same element afterwards and the answer is
    simply correct. **Not a different bug class; no bug.** The three addressing
    modes are `&T` across a `push` → `E0502`, `as_ptr()` + deref → `E0133`,
    index → compiles and is correct. **So `p25` is a row only if
    pointer-addressed.**

    ⚠⚠ **AND THEN THE KILL, WHICH NOBODY PREDICTED: IN `p25`'s SHIPPED HEAP
    TOPOLOGY `realloc` NEVER MOVES.** The driver `malloc`s the blob before the
    kernel runs, so the kernel's vector is the newest allocation and glibc
    extends it in place. ✅ **Manager-re-run, both compilers:**

    ```
    A  vector alone at the top of the heap   gcc moved=0/12   clang moved=0/12   <- SHIPPED
    B  a pin malloc'd after it               gcc moved=2/12   clang moved=0/12
    C  two vectors grown alternately         9/12 and 10/12, both compilers
    D  alone, past the 128 KiB mmap threshold          8/20, both compilers
    ```

    **In regime A the stale pointer is never stale**, the buggy rung's answer
    EQUALS the correct one in 6 of 6 compiler × `-O` cells, and **ASan fires only
    because ASan's own allocator moves on every `realloc`.** ⚠ **So the UB
    executes and is unobservable — `p08`'s published sentence verbatim, and
    `p08` is built.**

    ✅ **Three further kills, each independently sufficient, and they do NOT
    depend on the topology inference:** *(1)* **there is no safety conjunct to
    omit** — C cannot ask *"did my block move"* without comparing the base
    pointer, and a rung that saves `(base, k)` and re-derives on mismatch **IS
    the index port**; `p27`'s *"R1 omits exactly `&& live[h] == 1`"* has **no
    analogue**, because the safety line here is an ADDRESSING MODE, not a check.
    *(2)* the gradient is **`+1.00 Ir` per read, ONE instruction** of register
    allocation (122 → 123 in the symbol; the delta reproduced exactly at `+3052`
    across two runs while the level moved by 34). *(3)* **R1 has no reproducible
    checksum** — same binary, same input, `3196606969367904911` then
    `4868875711876342483` — **and a nondeterministic R1 cannot be gated against
    `model.py` at all.** ⚠ **The growth-overflow half is a measured
    `heap-buffer-overflow WRITE`, i.e. SPATIAL, refused on sight.**

    ⚠ **The OTHER two candidates died too.** **Stack lifetime**: both compilers
    warn at DEFAULT flags (`-Wreturn-local-addr` / `-Wreturn-stack-address`), so
    C is not silently wrong; the bug fires on `benign.bin` too, violating
    adversarial-only — **the exact constraint that made `p27` retract its
    original shape**; and **the gate's gcc-only ASan is BLIND to it** (0 hits
    even with `--param asan-use-after-return=1`; gcc's own positive control
    degrades to `SEGV on unknown address 0x0`). **Iterator invalidation**: the C
    rung's bug is one of exactly three things and the detector says which —
    `heap-use-after-free` (= `p25`), `heap-buffer-overflow` (= spatial), or
    `free(node); node->next` (= `p27`, built). **There is no fourth spelling.**

    ⚠⚠ **`p35` STAYS BLOCKED, ON A SHARPER REASON, AND TWO CATALOGUE STATEMENTS
    ABOUT IT WERE WRONG.** The `unsafe` can only live in an
    `#[verifier::external_body]` body (`check.py:4178-4180` is the ONE allowed
    branch), which makes it a trusted item, **which owes a TWIN — and a twin must
    be a SAFE SPELLING OF THE SAME OPERATION.** `p01`'s twin for `get_unchecked`
    is literally `v[i]`. **Rust has a safe spelling for indexing and NONE for a
    union read**, so the twin is `error[E0133]`. ✅ **The remaining hatch,
    `verus.twin_justifications`, appears in 0 of 26 shipped contracts —
    manager-verified — and its only occurrence under `patterns/` is
    `p17`'s NOTES REJECTING an axiom for this very reason.**

    ⚠ **Correction 1 — the cell's *"no configuration in which its safety
    obligation is CHECKED"* is TOO STRONG for the `external_body` route.** Verus
    **does** check the correct-variant obligation at the call site and the
    wrapper **can** carry a full functional `ensures` via
    `get_union_field::<U, u32>(v, "i")`. ⚠ **Union support is a LANGUAGE BUILTIN
    (`~/tools/verus/builtin/src/lib.rs`), not a vstd spec — which is why probe
    4's `std_specs/` grep missed it. NOT re-run by the manager; it rests on the
    engineer's six Verus runs.**
    ✅ **Correction 2 — the *"a GATE-CLEAN `p35` DOES EXIST"* `include!` route is
    CLOSED AT HEAD, and the catalogue still advertised it. Manager-verified at
    `harness/check.py:3941`: `cand += _include_literals(txt)[0]`, so
    `_path_includes` DOES resolve `include!`.**

    ⚠⚠ **WHAT THE MANAGER DID *NOT* VERIFY, AND THE ENGINEER FLAGGED IT FIRST:
    NOTHING HERE IS GATE-CERTIFIED.** The engineer was barred from `check.py`
    (concurrent agents), so the `p35` twin/`n_twins` interaction rests on reading
    predicates plus running Verus, **not on executing the gate against a
    synthetic pdir the way `TASK_096`/`097` did.** ⚠ **That is the weakest link
    and it is the first thing a review should execute.** ⚠ **`TOPO=0` being the
    shipped topology is an INFERENCE from the driver's allocation order — the
    manager checked `common/driver.c` `malloc`s the payload and body before the
    call, which supports it, but no real pattern driver was built.** ✅ **The
    `p25` verdict does not depend on it: kills (1), (2) and (3) above are
    topology-independent, and (3) alone makes the row ungatable.**

    ⚠ **The one revival route the engineer declined to measure, recorded so it is
    not rediscovered as new: a deliberately TWO-VECTOR kernel (regime C) moves
    reliably — but it is a kernel designed to produce its own bug, which is
    contrived rather than idiomatic.**

    Evidence: `.tasks/TASK_134_REPORT.md`, `.temp/t134/NOTES.md` and its
    `p25/ stack/ iter/ p35/` trees (all re-runnable from the committed `run.sh`
    scripts), `.temp/mgr134/` (the manager's re-runs and the Miri positive
    control).

## Retracted — do not reinstate

- **"Safe Rust pays an O(n) bounds-check tax"** (p02). The indexed fold's bounds
  checks cost *zero*; the whole delta was one spelling of an overflow check
  defeating LLVM's `memcpy` idiom recognition. Restated as a **codegen fragility**
  finding: one spelling loses the idiom, three others are +10 flat.
- **"C beats Rust"** (pilot). A **gcc-only** measurement generalised to "C"; the
  sign was backwards. The clang result was never affected.
- **"gcc's byte loop beats glibc `memcpy`"** — mislabelled; it beats R4, not gcc's
  own memcpy build.
- **"p16 is the first true O(n) *safety* cost"** — written by the manager from an
  engineer's report **without re-measuring**, and corrected at TASK_007_REVIEW.
  R3's per-byte rate equals R4's exactly, so the O(n) cost belongs to one
  *spelling*, not to safety. This file's own rule — *never publish a safety-cost
  claim without R3* — was broken by the person who wrote it, one pattern later.
- **"gcc is 36% behind clang on p16"** — a flag default, not a codegen limit.
  With `-funroll-loops` gcc reaches 2823 and **beats** clang's 2993. Reproduced on
  p17: 7065 → 4813, past clang again.
- **"The cost of the check is the conversion, not the comparison"** (manager's
  prediction for p17). False: `i128` index arithmetic costs +4.0000 Ir/byte, but
  **signedness itself is 4 Ir per call, flat — 0.17% of the gap.**
- **"The twin's value accrues from p17 on"** — p17's accessor is single-clause
  too, and for a structural reason: its interesting harm is not a memory error.
  The twin's value starts at the first *multi-clause trusted accessor*, a property
  of the wrapped intrinsic (p27+), not of the pattern number.
- **"p17's leak is an information disclosure"** — as shipped it is not; the excess
  bytes are the attacker's own request table. Corrected to a *slice*-relative
  guard, which does disclose a neighbour window. See finding 10.
- **"`scaling_cur_freq` shows the clock"** — it reported 800 MHz for six seconds
  while the core ran at 3.80–3.89 GHz. Measure the clock with a dependent chain,
  interleaved — and even then it spans ±15% within one session.
- **"On a vectorised loop the bounds check costs 0.0000 Ir/element"** and **"the
  wider the lane, the cheaper safety gets"** (p05, manager). The first is true
  only of the vector steady state — the check is hoisted into a per-row
  trip-count computation and survives in the scalar epilogue, an `O(nrow)` cost.
  The second is **refuted**: at AVX2 the gap is 4.58× against SSE2's 1.42×.
- **"`chunks_exact` refutes p05's R3 cost"** (TASK_014_REVIEW's blocker, which
  the manager landed as a retraction). **The retraction is itself retracted**:
  `chunks_exact` is forbidden by p05's own `spec.md`, so it measures a different
  kernel. p05's `6·nrow + 9` stands **as a contract-relative number**. What does
  not stand is reading it as "what safe Rust costs" — finding 14.
- **"Safe Rust beat unsafe Rust"**, and its repair **"p05's idiom-matched safety
  number is +11.00 Ir/call, flat, `O(1)`"**. One more unsafe round makes it
  `nrow + 9`. Both spellings were out of contract. (This entry used to add "and
  `inf(R4) <= inf(R3)` holds by construction anyway" — **that half is itself
  retracted at TASK_025_REVIEW**; see finding 14. The retraction of "safe beats
  unsafe" stands on the out-of-contract ground, which is the measured one.)
- **"`inf(R4) ≤ inf(R3)` by construction, so safe-beats-unsafe is never available
  as a language fact"** (manager, offered as "a reason available without
  measuring", carried for six patterns in three files). **All six patterns pin
  `identity: unsafe ≡ verus, O3 exact`**, so an R4 must have a byte-identical R5
  that Verus verifies: R4 is bounded by what vstd can express and R3 by nothing.
  The classes are **incomparable**. Measured on p16 — the same fold is admissible
  as R3 at zero TCB and needs five trusted items as R4. See finding 14.
- **"Compare idiom-matched rungs"** (manager, one turn after inventing it).
  "Same idiom" has no fixed point; its members differ by `O(nrow)`.
- **"p17's R3 costs +32 Ir/call, flat"** — flat *per byte*, not per call. Both
  published bands happen to have `nsuf = 3`; swept, `R3ship − R4` runs 18…63.
  p17 ships no sweep inputs, which is how a two-point constant became a law.
- **"p16's R3 cost is O(1) per call"** — `7 + 5·nrec` at `vlen ≡ 0 (mod 4)`,
  `7 + 7·nrec` otherwise. `O(nrec)`, and the two published points were nrec 4
  and 10.
- **"Overlap UB is not caught by ASan"** (manager, in the catalogue since it was
  written). It is caught — `memcpy-param-overlap`, exact to the byte — unless
  the call site is fortified to `__memcpy_chk`, which blinds ASan under clang as
  well as gcc.
- **"The bug is not expressible at R5"** (p08's own README). It is, and it
  verifies clean: a proof of a `requires` is not a proof that the trusted body
  honours it.
- **"p08 undermines p05's nonlinearity claim"** (manager, TASK_014_REVIEW Part 3).
  Refuted with disassembly: p08's retained check is blocked by a *relational*
  deduction, not a nonlinear one, and p05's linearisation counterfactual goes the
  manager's way. p05's cost claim fell for an unrelated reason.

## Working method

See `.tasks/PROTOCOL.md` for the full rules. The short version: manager writes
specs and `.memory/`, one subagent at a time alternating engineer → reviewer,
manager lands `.memory/` corrections and commits.

**Do not write a finding into `.memory/` before its review lands** —
`.tasks/PROTOCOL.md` rule 9. Four consecutive reviews caught the manager
overclaiming, every time from the same cause. Engineer writes `NOTES.md`, manager
commits it, reviewer attacks it, *then* `.memory/`.

**Ask to be corrected, not obeyed.** Every agent that has contradicted the
manager's written instructions with a measurement has been right. Two were
prescriptions that could not have worked at all; one overturned three premises in
a single review; p04's engineer refuted three of the manager's prescriptions in
one task. Say so in every task file, and **name the call you are least sure of**.
⚠ **The running count lives in one place — the closing paragraph of the newest
`.tasks/TASK_NNN*.md`** — because it was duplicated here and in `PROTOCOL.md`
and both copies went stale (13 and 7 against the task files' 55).

## The recurring traps

- ⚠⚠ **THE NEWEST AND THE ONLY ONE FOUND BY LOOKING AT THE PROJECT RATHER THAN AT
  A PATTERN: A CORRECTION REFLEX BECOMES A BIAS IN THE OPPOSITE DIRECTION.**
  (`TASK_111`, reviewing the synthesis. **PROVISIONAL — that review is
  unreviewed.**) Nineteen retractions trained this project to distrust any
  headline saying *safety is cheap*. **So when the synthesis compressed 39
  findings to four results, what it dropped was not the awkward result — it was
  the PRO-SAFETY half of the ledger, four to six times running**: finding **4**
  (*"the strongest thing here"* — C prints a plausible answer and exits 0 in
  **seven of eight builds** on a one-byte overflow, and deleting safe Rust's check
  makes it **panic rather than corrupt**), finding **14** (the R3/R4 classes are
  **incomparable, not nested**, so every `R3 − R4` here is measured against an
  inflated R4), finding **7** (C-clang and unsafe Rust executing **exactly
  143 740 000** kernel instructions), and finding **32**'s price half (**the
  undefined spelling is the DEAREST of its six neighbours** — the UB buys nothing
  and costs `6.00 Ir`/call).
  ⚠⚠ **AND THE MANAGER BUILT THE ASYMMETRY IN: the brief asked for a section on
  *where safe Rust does not help* AND HAD NO COUNTERPART ITEM.** The result was a
  document with **eight measured places where safety buys nothing, two
  unmeasurable places where it buys something, and ZERO measured places where it
  demonstrably buys everything.**
  **The transferable form: when you have a well-drilled reflex against
  overclaiming in one direction, audit your COVERAGE in the other. Twenty-six
  individually-reviewed pattern cycles did not surface this; one review of the
  aggregate did.**

- **A green gate is evidence about the gate.** Four reviews found defects past a
  fully green run, twice with an unchanged contract hash.
- **A vacuous truth in a log reads like a discharged obligation.** Six instances of
  "every X is Y" printed over an empty collection. Now a rule: a count-bearing
  success line prints its `n`, and `n == 0` fails.
- **Checks fail open.** Three times a malformed mutant that failed to *compile* was
  read as "the check passed".
- **Declared pins are self-certifying** — they move in the same commit as the code
  they constrain. Derive where possible; the Miri cross-check and the new
  callgrind "did this code run" check are the models.
- **Residues.** p01 tripped mod 4 three times; p02's real modulus was 16. Sweep two
  full cycles; never sample two points.
- **Attribute nothing without decomposing.** Change one loop at a time. This is
  what killed the O(n) claim.
- **Say which columns a staleness argument covers.** "The kernels are identical so
  the numbers stand" was right about kernel columns, wrong about whole-binary ones.
- **Residues bite at whatever width the codegen chose, and the round numbers are
  the worst case.** p01 mod 4, p02 mod 16, p16 mod 4, p05 mod 8 with **residue 0
  the outlier** — so every power-of-two dimension pays a full extra vector
  iteration. The size a benchmark author reaches for first is the trap.
- **`ns` is a measurement on this box; `cycles` is an inference.** The clock is
  set by other tenants and spans ±15% even measured interleaved in one session.
- **A finding needs a mechanism, not just a number.** "It vanished" was p05's
  first answer; the real one was a hoisted trip-count computation and a surviving
  scalar epilogue, and it changed the conclusion.
- **You are measuring a spelling until you have written two — and then you are
  still measuring a spelling.** Three retractions (p02, p16, p05) came from one
  plausible R3 published as what *safe Rust* costs. Writing a second spelling
  does not fix it: on p05 the spread across eleven exceeds the safe-vs-unsafe
  gap, and the unsafe rung has spellings too. Only a matched pair under a
  **declared, pre-registered** idiom carries a safety number (finding 14).
- **Read the pattern's `spec.md` before believing a cross-pattern rule.** Two
  consecutive tasks measured spellings p05's `spec.md` forbids **by name**, in a
  section titled "Load-bearing, do not improve", and neither cited it — because
  `.memory/01-ladder.md`'s R3 definition listed the forbidden spelling as a
  technique. A general file and a pattern file disagreed and the general one
  won twice.
- **A tool that reports nothing may be a tool that cannot see.** ASan is silent
  on p08's overlap not because there is none but because fortify rewrote the call
  to `__memcpy_chk`. A gate row records `clean` for both reasons identically.
- **Two files, two numbering schemes** — now with a **map** at the head of the
  findings list, which is the fix this entry asked for three times. Name the
  pattern, never the number.
  **And one task file is misnumbered**: `.tasks/TASK_025_REVIEW.md` reviews
  **TASK_024**, not TASK_025 (there is no TASK_025). Every other
  `TASK_NNN_REVIEW` reviews `TASK_NNN`; `TASK_027_REVIEW` restores the
  convention. Cite reviews by what they *found*, not by their number.
  (This file also *shipped findings 13 and 14 twice*, with divergent text, from
  an insert-where-a-replace-was-meant. One copy asserted p05's `5·nrow + 6`
  floor as a narrowing result while the other recorded its refutation. Deduped
  and merged 2026-08-18. When you edit a finding, `grep` its opening words first.)
- **Never publish a bare per-byte rate, or a difference of rates across unmatched
  spellings. Publish only matched-spelling differences.** (TASK_024,
  TASK_025_REVIEW — the answer to "is K-dependence a finding or a surrender" is
  *both*, split.) A bare rate is **not a property of the kernel**: p16's ranges
  5.04688 … 6.62500 in contract, one exact-string substitution apart, and is not
  even measurable past ±0.01 because the driver's `println` term does not cancel
  within a binary. So p16's 5.7500, p17's 10.0000/5.7500, p05's 1.375000 and
  finding 11's 4.25 are all quoting a free parameter. A **cross-spelling
  difference** of two such rates is worse — that is exactly what −0.65625 is, and
  it reached four files as a headline with the wrong arithmetic on top. But the
  **matched-spelling difference is a property of the kernel**: 0.0000000 Ir/byte
  over 127 consecutive lengths × 6 spellings, with the mechanism visible. Note
  what this means: **the rule TASK_024 adopted — "name the fold beside the rate" —
  does not catch its own headline figure.** A mechanical backstop was costed at
  ~90 lines (`spec.md` pins the shipped fold's chunk-body instruction count;
  `check.py` asserts `body_len / K` equals the published rate) and is **not yet
  proposed as gate work** — it would have to pass "could this happen by
  accident?" first, and it has happened by accident twice.
- **A cited artefact can refute the claim it is cited for.** `.temp/p24/foldbody.py`
  is named in p16's `NOTES.md` as the evidence for mnemonic identity; re-run as
  committed it prints `identical=False` at every `K`. The claim is *true* — a
  reviewer re-derived it — but for a year nobody would have known which. Re-run
  the artefact, do not cite it.
- **Run `./verus_run.py` on an R5 twin BEFORE differencing any unsafe-side
  variant.** Every `identity`-pinned rung is chained to the prover, so an
  unsafe-side "cheaper spelling" that vstd cannot express is not a rung and its
  number means nothing. This one check would have caught p16's `u_c32`, p16's
  `r4_hdr`, p05's `c4_hu16_nz`, p05's `r4_dataslice` and both endpoints of p05's
  published pair interval — five published figures, across two patterns, over
  four tasks. It costs about eleven minutes.
  **And read the error text, not the exit code**: `is not supported` disqualifies
  (it forces a new *trusted* item); *"postcondition not satisfied"* disqualifies
  nothing — measured on p05, the same exec code went from `11 verified, 1 errors`
  to `13 verified, 0 errors` with one lemma and one `proof` block, at zero TCB.

## Priority — read this before planning

**Fifty-six tasks in, 16 of 47 patterns exist**, and the ratio is the thing to
watch. Six tasks went to gate hardening before the user called it; **T015–028 —
thirteen consecutive tasks — went to the spelling problem** and produced no new
pattern. Both arcs paid for themselves, and neither was on anyone's plan. But the
honest reading is that **this project is better at discovering its own numbers are
wrong than at producing new ones**, and the correction is simple: **alternate
build → review, and make a methodology proposal argue for itself against a
pattern.**

**Since T033 the loop has held** — p11, p03, p09, p12, p04, p13, p06, p14, p18
each built and reviewed, every one green on its first complete run, and every one produced a
finding no one predicted. That is the working mode; do not drift off it.
⚠ **The last five each needed a THIRD task to land their corrections** (T044, T046,
T048, T050, T052), and all five were worth it: p04's review moved its headline number,
p13's reversed its headline's sign, and p06's corrected two published laws and a
`.memory/` claim that had stood since TASK_004. **Budget build → review → land,
not build → review.** Three tasks per pattern is the real cost; plan with it.

The gate's threat model is **honest mistake, not malicious author**
(`.memory/02-bench-rules.md`, top section, with the residuals deliberately left
open). **New gate work must pass "could this happen by accident?" first** — and
`check.py` is ~5460 lines against 19 patterns, so the next gate proposal should
have to beat that ratio.

**Review each pattern once; do not review each fix to each check.** The two
highest-yield review targets, measured across every review so far: a claim the
engineer *flagged against itself*, and a mechanism asserted without a control.

## Immediate queue

⚠ **This header said *"`TASK_055_REVIEW` is the next task"* roughly forty-five
tasks after that stopped being true.** **The next action is ALWAYS the START HERE
box at the top of this file, never this section** — this is the standing backlog.
**Do not write a "next task" sentence here again; there is exactly one place for
it and duplicating it is how this one rotted.**

✅ **Measured at TASK_100-time, because the rule below is what licenses running
agents in parallel: `harness/check.py` contains NO wall-clock measurement at
all** — `grep -n 'perf_counter\|time\.time\|best-of' harness/check.py` returns
one hit and it is a comment. **The gate is `Ir`-only and deterministic, so gate
sweeps are immune to concurrent load; `harness/measure.py` is the one that is
not.** That is the line the relaxation below actually turns on.

⚠ **The concurrency rule, so it is not read as blanket licence.** One agent at a
time is the default. It is relaxed **only** for work that touches neither
**measurement** — concurrent CPU load corrupts a `ns` column, and two timing jobs
corrupt each other — nor **gate JSONs**, which `check.py` rewrites in place.
`TASK_058` qualifies because it is forbidden from executing anything at all.
`TASK_055_REVIEW` does **not** qualify: it runs valgrind and Verus. Deterministic
`Ir` under callgrind is immune to contention; wall clock is not, and the failure
is silent.

### CLOSED at TASK_053–056 — history, not work

The gate audit swept all **18** stages and found **6** defects; every one is now
fixed or declined with a reason, on a tree that re-ran 16/16 green.
**Do not re-open these:** the second sanitizer hole (F3) is **fixed**, and **every
sanitizer row carries `stdout`** — 114/114 when that was written against 16
patterns, **135/135 re-verified at TASK_066 across 19**; the invariant is the
*zero missing*, not the count; the tautology battery (F2) no longer lets an aborting
tactic overwrite a real verdict; the adversarial key (F1) records all behaviours
with their cells; the comment-in-a-clause bypass (F4) is repaired in `vparse`;
`forbidden_hits` (F6) was **declined** and is now **RE-OPENED** (TASK_062 found a real defect it could see; TASK_063 settled the defect and recommends **fail, batched** — `.memory/02-bench-rules.md`, PROVISIONAL). It was recorded as a known residual with the
measurement. p12's, p03's, p04's, p05's, p11's and p18's sole-catcher prose is
corrected; p08 is TCB 4 → 3 with `identity: exact` at both levels; `limbs.py`
lives in `harness/`; the `.partial.json` trap is gone (they now write to
`.temp/gate-partial/`).

✅ **Clean negative, TASK_066: this section re-verifies.** After item 6 below
turned out to have been closed by a command that matched prose, four of this
list's checkable claims were re-derived from the tree — `harness/limbs.py`
present, **no `.partial.json` under `results/`**, **135/135 sanitizer rows carry
`stdout`**, **p08 `tcb_items` = 3** (`move_right`, `load_input`, `emit`). All
four hold. **The CLOSED list is trustworthy; item 6 was the anomaly, and it was
in "Owed", not here.** Do not re-run this check.
⚠ **`O3d` was built, measured inert, and REVERTED** — see
`.memory/03-measurement.md`: `build.py` is hashed into the *measurement* records
too, so landing it costs a full re-measure and would churn ten patterns' timing
prose. **Land it bundled with a pattern that is being re-measured anyway.**

**New, from p10's cycle:**

- **p10's R4-side span is a LOWER BOUND ON ITS OWN WIDTH.** `u_win` is the
  cheapest admissible R4 found (194.00 / 362.00 below shipped), but it carries a
  panic pad, so `identity: exact` excludes it. **Nobody has looked for an R4 that
  is both cheaper and PAD-FREE**, which is the one that could actually ship.
- **p10's `-O3 whole` laws have no registered out-of-sample test** — band `e` was
  registered for the `isolated` column only, so for `whole` it is an ordinary
  hold-out.
- **p10's whole-mode per-output coefficients are not decomposed** mnemonic by
  mnemonic, and its padding caveat applies to them.
- **`u_win` was never run through `check.py` as a rung** — its `required`
  spellings were checked by reading.
- **`measure.py p10` was re-run at TASK_059** (comment edits touch
  `source_sha256`). Every deterministic metric was diffed and is identical; the
  wall column moved ~8% and one cell now trips the 10% spread threshold.

**Still open, from p18's cycle:**

- **p18's controls were never re-swept over its new band `t`** — `t_1step`,
  `t_chain`, `t_iter`, `t_pos`, `t_wshl`, `t_cshl`, `c_mask`, `c_ncap`,
  `c_reject`, every `*_noguard` rung and every `O0d`/`O3d` law are still
  `cut = brk = 0` laws. **p18's own largest remaining gap**, recorded in its §8d
  and §12. `cut`/`brk` are also `-O3 isolated` only.
- **p18 publishes no pair interval and its R4 side is unsearched in contract**;
  its `R3 − R4` is a fixed-R4 reading only. Same standing gap as p01 and p08.
- **p18 has no `ns` figure for R2 or R3** (no layout population for the safe
  cells), and its `large` `ns` row is weak (P = 0.676 / 0.829) and quoted with
  its P.

**New, from p14's cycle:**

- **No C or safe-Rust cell on p14 has a layout population**, so its whole `ns`
  column stays **withdrawn rather than filtered**. `c-clang-h − c-clang`
  (+18.21%) may well survive one. `controls/clayout.py` now ships on both p06
  and p14; porting it is cheap.
- **p06's `adversarial-past48` `c-clang` stdout moved between BUILDS**
  (`497` → `6008526198855114936`), and the same binary prints `497` on three
  consecutive runs. p06 §7 records that cell as `0, 497`. The `c-gcc` instability
  beside it is documented (six observations); **this one is new and undocumented,
  and build-varying is a different mechanism from run-varying.**
- ✅ **THE LIFETIME PATTERN IS UNBLOCKED AND UNBUILT — the biggest open
  opportunity here, and it is now the NEXT ACTION.** `vstd::raw_ptr` works
  (TASK_055, **reviewed at TASK_055_REVIEW**): a heap kernel verifies with **zero
  project-local trusted items**, and the ghost split loop the probe never
  wrote — the one thing the whole pattern was blocked on — verifies **7/0** at
  **150 ms**, with the **identical rlimit** at `n <= 1_000_000`, so the slot
  count is free. p14's rejection reason is refuted (`add`/`offset` unsupported,
  **`addr`/`with_addr` supported**); stack locals are out
  (`SharedReference::new` is private). Formulation: a **slab with pointer
  handles at R4/R5 and `(slot, generation)` at R1h/R2/R3**, so safe Rust's cost
  is a **representation change, not a check** — an axis this project has never
  had.
  ⚠ **Three measured constraints, all in `.memory/04-verus.md`, none fatal:**
  the UAF must live on **adversarial inputs only** (at `-O3` the stores into the
  recycled slab are **dead-store-eliminated**, so that row does not execute the
  bug and the checksums disagree across `-O` level — the offset-16 fix was
  necessary and **not sufficient**); **`dloop.py:361` raises on rung-signature
  arity**, and the one escape measured to work is a **dead `slab` argument** on
  R4, whose `-O3` survival is unmeasured; and the R5 catcher is an **ordinary
  SMT obligation, not linearity** — that claim is retracted.
  ⚠ **TCB counting is SETTLED**: the manager's `tcb_reach` column was proposed,
  attacked and **rejected** — keep one number, add prose, and the residual is
  live and named.
- **p14's `-O0` rows are unexplained** (R3 dearer than R2 there, sign inverting
  at `-O3`) and **clang's `R1h − R1` law is unsolved** — mechanism and mnemonic
  table only, no closed form. No claim rests on either.

**Closed by p06:** the two-step reslice (old item 1) is now measured on a sixth
pattern at **exactly −1.00 Ir/call**, and p06 shipped the first
**length-heterogeneous** fit set (old item 11), whose leave-one-`m`-out **can
fail** — it misses by −48.000 at `m=3`, which is how the domain got established.
Both retired.

**New, from p06's cycle:**

- **`b_nored`'s Verus failure is a resource-exhaustion, not an obligation**, and
  `--rlimit 30/60` does not convert it. A mutant that dies of rlimit is a weaker
  control than one that fails on a named obligation, and the pinned counts hide
  the difference.
- **p02 keeps a trusted wrapper it does not strictly need**, with the price now
  measured (`+5.00 Ir/call`, one extra panic pad, breaks `identity: exact`). Not
  a defect — the hard stop working — but someone will ask why p06 removed one and
  p02 did not.

### Owed, in priority order

0. ⚠⚠ **RE-OPENED at TASK_083_REVIEW, ONE COMMIT AFTER BEING CLOSED. TASK_082
   CLOSED ONE OF AT LEAST FOUR ROUTES.** Three more body-less trusted forms
   verify a falsehood and are **invisible to the new stage**, and the published
   column never saw the fix at all. ✅ **All four manager-verified.**

   **B1 — `#[verifier::external_trait_specification]`.** A fourth body-less
   trusted form, **54× in the pinned vstd**, and
   `grep -c 'external_trait_specification\|external_fn_specification' harness/*.py`
   is **0 in all nine files**. Probe: Verus proves `r == 0`, **the compiled
   program prints 7**, `axiom_decls` returns `[]`, and no item carries
   `.external` (the attributes sit on a `struct`/`trait`), so the TCB inventory
   is empty and 5c-twin shouts *"no trusted item"*. ⚠ **And Verus PRINTED the
   `external_type_specification` line to paste — the identical accident vector as
   this item's original.**
   **B2 — `#[verifier::external_fn_specification]`.** `vparse`'s
   `\bverifier::external\b` does not match it (next char is `_`), so `.external`
   is `None` and it is **not a TCB item**. In `verus.items` it is
   **indistinguishable from a verified function**.
   **B3 — an axiom in a `#[path]`-included SUBDIR module.** The scan runs over
   `verus.obligations` and its one guard uses **`os.listdir`, which is FLAT**.
   ⚠⚠ **THIS VECTOR IS LIVE IN ALL 22 PATTERNS** — every `verus.rs`
   `#[path]`-includes `common/driver.rs`, so `common/` is in every pattern's
   token stream. `_scan_unsafe_sites` already walks `_path_includes` for exactly
   this threat; the axiom scan does not.

   ⚠⚠ **AND THE PUBLISHED COLUMN NEVER SAW THE FIX.** `synthesize.py` reads
   **`tcb_items`**, and the word *"axiom"* appears **zero times** in
   `synthesis/*.py` and `results/synthesis.md`. ⚠ **So the manager's
   verification that *"`results/synthesis.md` regenerates byte-identical, so
   nothing moved"* PASSED FOR THE WRONG REASON** — it is byte-identical because
   **the published TCB column cannot see `axiom_decls` at all.** *A green check is
   evidence about the check.*

   **What TASK_082 DID close, and it stands:** the three-keyword matcher is
   sound on what it claims — **7 of 7 spelling variants caught** (`pub(crate)`,
   split keywords, comment between, generic + `where`, mod-nested, target on the
   next line), the `broadcast proof fn`-with-a-body boundary is exactly where it
   was said to be, and the declared-count escape works as int and as name-list.
   ✅ **And the `_is_trusted` exclusion reason is TRUE** — `uninterp` with a body
   is a Verus error, so 5c-twin really would demand an impossible twin. ⚠ **But
   its stated CONSEQUENCE pointed at the wrong function**: the published column
   is `tcb_items`, not `_is_trusted`.

   ⚠⚠ **B4 — A SIXTH ROUTE, AND IT IS THE WIDEST: A *USED* vstd
   `assume_specification` IS INVISIBLE TOO.** (TASK_085_REVIEW blocker 1.)
   `_axiom_items` scans the pattern's own sources with `vparse.axiom_decls`,
   which matches **declarations**. **A pattern that merely CALLS a vstd
   `assume_specification` declares nothing**, so `_trusted_items` = 0 and
   `_axiom_items` = 0 — and then `check_miri`'s `if not why_required` branch
   **prints** *"this pattern has NO trusted item and NO hand-written axiom, so
   there is no trusted `ensures` whose incompleteness Miri would have to
   backstop — Miri not required."* ⚠ **That sentence would be FALSE**, because
   the executed call is licensed by `vstd/string.rs:135-139`'s
   `assume_specification[str::from_utf8_unchecked] … requires valid_utf8(v@)
   ensures res.spec_bytes() =~= v@` — **verbatim the `ensures` a wrapper would
   write, and verbatim `_axiom_items`' own definition of an axiom.**
   ⚠ **Today nothing exploits it**, because `check.py::_scan_unsafe_sites`
   forbids an `unsafe` token outside an `external_body` item and **vstd specs
   none of the operations the tree uses** (`grep -rn "get_unchecked"
   ~/tools/verus/vstd/` → **0 hits**, so all 47 wrappers were unavoidable).
   ⚠⚠ **So `_scan_unsafe_sites` is LOAD-BEARING, not backwards — it is the only
   thing standing between this hole and a green verdict.** **`p15` is the row
   that would have walked through it, and that is why it is refused.**
   **Softening that rule is admissible only AFTER this route is closed.**

   ⚠⚠ **B5 — A SEVENTH ROUTE, AND `TASK_084` OPENED HALF OF IT WHILE CLOSING
   B3: THE `#[path]` WALK FEEDS ONE OF THREE DETECTORS.** (TASK_084_REVIEW major
   1, **three planted gate runs**.) D3 widened `_check_axiom_decls` and
   `_axiom_items` to `_path_includes`. It did **not** widen **`_trusted_items`**
   — *the function immediately above `_axiom_items`, same shape, same purpose* —
   nor the TCB inventory `tcb = [i for i in item_list if i.external]` inside
   `check_verus_contract`. Both still iterate `verus.obligations` only. So an
   `#[verifier::external_body]` with a **false `ensures`** in a
   `#[path]`-included module ships **fully green with no gate output at all**:
   `grep -c r84_lie gate.log` → **0**, the gate prints *"3 TCB items"*, and
   `synthesis.md` is **byte-identical**. Same for a bodied
   `external_fn_specification`, and the `assume(`/`admit(` shout also runs over
   `sorted(pinned_obl)` only.
   ✅ **Clean negative that bounds it: `unsafe` in an included module IS
   caught** (`[tcb-unsafe]`), **so the vector is false claims about SAFE
   operations** — exactly the threat `_check_axiom_decls`' own docstring names.
   **Fix: widen `_trusted_items`, the `tcb` inventory and the keyword shout the
   same way `_axiom_items` was.**

   **Still owed:** the `#[path]` walk's **other two detectors** (B5), the
   **sixth route** (used vstd `assume_specification`s), and **minors 1, 4 and 5
   of `TASK_084_REVIEW`** — a shared axiom in `common/driver.rs` is counted
   **22 times** in the published total (dedupe on `(key, name, line)`), a
   `pub(crate) trait` under an external-trait attribute under-counts to one
   `ExW::?`, and a `#[path]` include resolving *inside* `pdir` gets **two keys**
   and is counted twice. ✅ **B1, B2, B3 and the published column are CLOSED at
   `TASK_084` and reviewed.**

   *Original closure text kept below — it is right about what it covers.*

   ✅ **CLOSED at TASK_082 — and the repair the item PRESCRIBED would have broken
   a green pattern.** `vparse.axiom_decls()` is a **separate keyword-keyed
   matcher**; `parse()` is untouched. New gate stage: counts body-less trusted
   declarations, compares against an optional `spec.md` `verus.axioms` key
   (**default 0**), `rep.fail("proof-axiom")` on mismatch and
   `rep.shout("tcb-axiom")` whenever any exist; the `assume(`/`admit(` scan went
   `rep.note` → `rep.shout`; `axiom_decls` now ships in every gate record.

   ⚠⚠ **DO NOT "SIMPLIFY" IT BY WIDENING `parse()` — that is what this item
   originally implied and it turns p36 RED in six stages.** A **trait method
   declaration is body-less**, and p36 declares `fn apply` / `spec fn spec_apply`
   in the trait and defines them in the impl, so keeping body-less items makes
   `by_name` raise `duplicate item name(s)`. ⚠ **And `assume_specification` has
   no `fn` token at all, so widening would have paid p36's price and still missed
   the target.** Full write-up: `.memory/05-layout.md`.

   ✅ **Acceptance, all three limbs, manager-verified:** 22 verdicts identical
   (21 `PASS` + p01 `PASS-WITH-BLOCKED-ROWS`), **0 failures**; **TCB total 92 →
   92** with `axiom_decls` present and empty in all 22 — ⚠⚠ **but `92` IS NOT THE
   PUBLISHED TOTAL AND THIS LINE IS ONE OF FOUR THAT SAY IT IS.**
   `results/synthesis.md` prints **90**: 92 is the sum over **all** Verus
   sources, 90 is the sum over **`verus.rs`**, and the difference is p01's
   `safe_naive_verus.rs` (`['load_input','emit']`). ✅ **Manager-verified.**
   The other three are `TASK_082.md`, `TASK_083.md` and
   `TASK_083_REVIEW_REPORT.md` — **and the last one names this very table while
   quoting 92.** ⚠ **Both numbers are real; the error is the LABEL. Say which
   sum you mean.** This is "Owed" 0's fifth route showing up in the project's
   own bookkeeping (TASK_084 #236); and the injected-false-
   axiom demonstration now **FAILS** where every other pin still says green —
   `parse()` sees 7 items either way, `_is_trusted` is unchanged, the obligation
   count matches, and only the new stage catches it.
   ⚠ **The design is VISIBILITY, not prohibition** — declare `verus.axioms` and
   it passes, with a shout in every verdict. **No pattern declares one today, so
   no `contract_sha256` moved.**
   ⚠ **Deliberately NOT fed into `_is_trusted`**: stage 5c-twin would demand a
   twin of an item with no body, turning a legal declaration into an unpassable
   gate.

   *Original text kept below.*

   ⚠⚠ **THE GATE COUNTS NO
   `assume_specification`, AND TCB SIZE IS A PUBLISHED COLUMN.**
   (TASK_081_REVIEW blocker 1, **manager-verified**.) `harness/vparse.py`'s item
   matcher keys on `fn NAME` **with a body**, and drops every body-less item — so
   `assume_specification`, `broadcast axiom fn` and `uninterp spec fn` are **all
   invisible to the parser**, and `check.py::_is_trusted` additionally requires
   `verifier::external_body`.

   **Demonstrated on a real pattern.** `patterns/p01-array-sum/verus.rs` with
   **two deliberately FALSE axioms on safe std functions** added:

   ```
   ./verus_run.py .temp/r81/p01_axiom.rs   ->  7 verified, 0 errors
   parser: n_items 7, identical names to the untouched file
   _is_trusted: ['get_unchecked']  (unchanged)
   kernel bytes: md5 e3e4441313c93057730ab568fb000846 — IDENTICAL to baseline
   ```

   **Blind to it:** the published TCB column in `results/synthesis.md`, the pinned
   obligation count, the `identity` pin, `check_miri` (`n_trusted == 0` ⇒ *"Miri
   not required"*), and stages 5c / 5c-req / 5c-twin. The only trace is an
   informational `rep.note`.

   ⚠ **Scope it correctly — the hole is axioms on SAFE functions.** An unsafe
   intrinsic's call site still trips `_scan_unsafe_sites`. **But safe functions
   are exactly finding 14's list** — p16's `chunks_exact`/`by_ref`/
   `TryFromSliceError`, p11's four `CStr` items, `from_le_bytes` — i.e. precisely
   the items someone now has a measured reason to want to axiomatise.
   ⚠ **`RECAP`'s settled answer already says the TCB column is *prospectively*
   gameable; this is a SECOND and sharper mechanism** — not "needs zero
   project-local items" but "adds items the parser cannot see".

   **Cheapest honest repair** (the reviewer's, not implemented): a declared count
   plus `rep.note` → `rep.shout`. ⚠ **It is a `check.py`/`vparse.py` edit, so it
   stales every gate record — batch it**, and it clears rule 5's *"could this
   happen by accident?"* test on the evidence above rather than on an argument.

1. **The two-step reslice is untried on most patterns**, and most patterns' R3
   opens with the window reslice it improves. It costs zero `unsafe` and zero
   TCB, and its mechanism is register allocation rather than bounds-check
   removal, so it is *not* the lever any prior spelling search ran. **One
   substitution per pattern, gate re-run, no re-measurement of anything else.**
   `.memory/01-ladder.md` finding 3 carries the spelling and the mechanism.
   ⚠ **Do NOT quote "−1 `Ir`/call, confirmed on seven patterns" — the manager
   did, and it levels two very different pieces of evidence.** On p04 the
   −1 was **20% of the whole published tax**. On p10 it is **one instruction**
   (3268 against 3269), which `.memory/03-measurement.md` requires be called
   **instruction-count-only and stopped there** — it does not retire this item
   on its own, and TASK_059 retracted the claim that it did.
2. **p03's span rests on one unreviewed measurement.** TASK_037's `a_tail` is
   swept (`maxres 0.000000`, 19 blobs) and its admissibility comes from the gate's
   own decidable matcher, which is why it was landed — but it refuted a number a
   review had just confirmed. **And the `+5` per-call constant has never been
   searched at all**; it is the whole remaining gap between p03's two class
   minima, and the belief that safe Rust must pay it is an argument, not a
   measurement.
3. **p01 and p08 owe an in-contract R3-side span.** Do **not** let either publish
   a pair interval — both this project published were built from R4s that are not
   rungs — and never the word "minimum"; write "cheapest found" and name the
   input, because on p03 and p16 the cheapest spelling changes with it.
4. **p17 ships no sweep inputs**, which is how its "+32 Ir/call flat" was
   published from two bands that both had `nsuf = 3`. A `sweep-*` band appended
   last costs **one gate re-run, not a re-measure** (`.memory/05-layout.md`).

   ✅ **CLOSED at TASK_082, and the law's CHARACTER moved while its VALUE did
   not.** `patterns/p17-http-range/inputs/gen.py --sweep` emits
   `sweep-nsuf-01..08.bin`; the 8 pre-existing matrix blobs are byte-identical
   and `matrix_inputs` still returns **8, not 16**, so no re-measure was
   triggered (`0 STALE`, manager-verified).

   ⚠ **`≈7·nsuf + 9` is a straight line drawn through a STAIRCASE.** Measured
   `R3ship − R4` over `nsuf = 1..8`: **18, 23, 30, 37, 44, 49, 56, 63** — steps
   of `+5, +7, +7, +7, +5, +7, +7`. Least squares gives `6.4762·nsuf + 10.8571`
   with max residual **0.81**; **lag-4 differencing gives 26, 26, 26, 26 with
   ZERO residual = 6.50 `Ir` per request** — a **mod-4 sawtooth** from the 4×-
   unrolled table walk, the same device p17 §3b already uses on the byte axis.
   ⚠ **This reproduces TASK_015_REVIEW's published table byte-for-byte**, now
   from committed inputs and a hashed generator rather than uncommitted ones.
   ✅ **No published p17 number is wrong**: `+32` is the shipped pair at
   `nsuf = 3`, this band gives 30 there, and §10 already discloses that.
   **PROVISIONAL — in `patterns/p17-http-range/NOTES.md` §10b per rule 9,
   awaiting review.**
   ⚠ **The band does NOT hold folded bytes fixed**, which is sound for a rung
   *difference* (§3b measured the per-byte rate at exactly 0, so it cancels) and
   **unsound for an absolute per-call law of any single rung.**
   ⚠ **`R3ship − R3′ = 17·nsuf` was NOT re-measured** — `R3′` is out of contract
   and p17 ships no cell for it, so that row is still TASK_015_REVIEW's, on
   uncommitted inputs.

   *Original text kept below.*

   ✅ **The SPEC now exists, written by TASK_080's engineer at zero cost after it
   declined the work** (`TASK_080` authorised this item by name in one section and
   forbade editing existing patterns in another — **the task file contradicted
   itself and the engineer reported that instead of guessing**). Confirmed:
   `grep -c sweep` on `patterns/p17-http-range/inputs/gen.py` → **0**, and p17's
   own `NOTES.md:85` already says a shipped `nsuf` sweep is owed. **The spec:**
   add `--sweep` modelled on **p16's `inputs/gen.py`**, emit
   `sweep-nsuf-NN.bin` over `nsuf = 1..8` (TASK_015_REVIEW measured
   `≈7·nsuf + 9`), **regenerate twice and diff** for determinism, then **one gate
   re-run — no re-measure**, because both `check.py` and `measure.py` skip the
   `sweep-` prefix. **Ready to hand to an engineer as written.**
5. ⚠ **ARGUED AND DECLINED at TASK_077 — leave the glob alone, and the item's
    own TEST is the wrong test.** It asks *"does the gate execute it?"*; the right
    question is **"does a committed claim depend on it?"** — `limbs.py`,
    `report.py` and `measure.py` are cited in **64 committed doc references**, and
    `harness/limbs.py:14-19` already decided it: *"That coupling is deliberate...
    The staleness is the alarm."* ⚠ **And the item's COST FIGURE IS 3.3x STALE:**
    ~~13 min~~ is **2593 s = 43.2 min** measured, 2672 s = 44.5 min on the next
    sweep. **A full sweep is three quarters of an hour; batch accordingly.**

    *Original text kept below.*

    **`check.py`'s `harness/*.py` glob is over-broad** — it imports five modules
   but hashes all of them, so a `measure.py` edit costs eight gate re-runs (13 min
   measured) for a file the gate never executes. Judgement call; belt-and-braces
   cannot under-cover.
6. ⚠ **RE-OPENED at TASK_066. It was marked ✅ CLOSED on the strength of a
   command that cannot tell the hash from a sentence ABOUT the hash.**

   The item claimed *"every pattern record now carries `source_sha256`; the only
   file without one is `results/p02-residue-sweep.json`, a side record"*.
   **Measured today: six files lack the top-level key, five of them real
   patterns** — `p02-buffer-copy`, `p05-index-flatten`, `p07-binary-search`,
   `p11-nul-scan`, `p17-http-range`, plus the side record. That is the *original*
   count this item said the re-measures had cleared. **Nothing was cleared.**

   **The mechanism, and it is worth remembering.** The closing one-liner was
   `'source_sha256' not in open(f).read()` — a substring search over raw text. In
   all five files the string occurs exactly once, inside `/git/note`, in a
   sentence advising *"Use `results/gate/*.json`'s `source_sha256`"*.
   **The note telling you where to find the hash is what convinced the checker
   the hash was there.** Third instance of TASK_065's lesson: *a wrong command is
   worse than a wrong constant, because it looks self-verifying.* Parse the JSON:

   ```bash
   python3 -c "import json,glob;print([f for f in sorted(glob.glob('results/*.json')+glob.glob('results/gate/*.json')) if 'source_sha256' not in json.load(open(f))])"
   ```

   **What it actually means — and it is narrower than it sounds.**
   `measure.py --check-stale` prints `NO BASELINE` for those five and **does not
   count them as `bad`**, so the run says `38 record(s) examined, 0 STALE` and
   **exits 0**. ⚠ **"0 STALE" is therefore not "everything is verified"**: five
   of nineteen *measurement* records cannot be checked by hash at all, and they
   include **p02 (the project's strongest security result)** and **p17**.
   ✅ **Mitigating, and verified: all 19 GATE records DO carry `source_sha256`**
   — which is exactly what that `/git/note` sentence is pointing at. So the gap
   is in the **measurement layer only**, and provenance for those five exists one
   file over.

   **The fix is a re-measure of those five**, which is the expensive operation
   (settled answer 4) and must not run concurrently with anything. Queue it
   behind pattern work; do not let it displace a pattern.
   ⚠ The old sub-claim that `p11-nul-scan.json` was *"recorded stale on
   `bulk_calls`"* is **not checkable as written** — with no baseline there is
   nothing to compare — and p11's `bulk_calls` are populated today
   (`memchr@plt` on the C rungs). Re-derive it after the re-measure, or drop it.
7. **p04's `small` R2 layout population is bimodal at 1.42× and unexplained**
   (TASK_042_REVIEW minor 8): 27 layouts at 6.43–7.17 ms, four at 9.30–9.88 ms,
   reproducible across both passes, and **neither `analyze.py`'s `(loop,
   property)` pairs nor `addr%32` separates it**. All four outliers are `order|*`
   builds and are among the *fastest* on `large`, so a startup-side effect is
   plausible. Finding 16 says every layout mode found so far is `win32` or
   `jcc32`; **this one is neither**, and it is the first counterexample to that.
   It does not move a published verdict (the mode-matched `R2 − R4` figures agree
   with the shipped ones), so it is a curiosity — but it is a *named* one.
8. **p13's `controls/library_axis.py` deliberately keeps the OLD narrow fold**,
   because `strlcpy`/`snprintf` do not zero-fill and a full-extent fold would
   make the six routines print six checksums for a non-cost reason. Its *levels*
   are therefore not comparable with p13's §4; every *difference* inside it is.
   Documented in the control — but it is the only place in the tree where two
   folds coexist, so check it before quoting across the boundary.
9. **p13's corrected wall-clock ratios (+7.64 / −5.39) do not clear the ±9-point
   bar**, so its quotable timing evidence is the raw *level* under the
   identical-copy protocol. Not a defect — the rule working — but it means p13
   has no corrected-ratio row and someone will look for one.
10. ✅ **CLOSED at TASK_069 — and its prediction was confirmed LIVE on the way
    out.** This said `check.py::spelling_matches` does not blank
    `#[cfg(slb_twin)]` bodies, so a Verus rung's idiom audit could be satisfied
    by code no build contains, and called it *"hygiene, 0 of 15 pins"*.
    **`exec_code` now blanks it structurally** — items gated on a cfg no cell
    sets, so `slb_twin` falls out of the rule rather than being named by it.

    ⚠ **Two things this item got wrong, both worth keeping.** (a) It stopped
    being hygiene the moment `forbidden_hits` began hard-failing: the harm
    direction **inverted**, from falsely *satisfying* a `required` count that
    never failed to falsely *hitting* a `forbidden` entry that blocks the gate,
    and the denominator went from 15 pins to **every forbidden spelling in the tree, across 21 files,
    all containing twin bodies**. (b) *"0 of 15"* was wrong — **the predicted
    false satisfaction was live**: p27's `` `deallocate` `` was spelled in exactly
    one place in the tree, **its own `#[cfg(slb_twin)]` twin**, so the entry read
    PRESENT on code no cell compiles. p12's matched only inside `spec fn fin`.
    Tree-wide `required_absent` **96 → 94**, `required_pins_nothing` **15 → 16**
    (manager-verified).

11. **A length-heterogeneous sweep band is what a step-basis test actually
   needs**, and no pattern has one. p13's fit blobs are all length-homogeneous,
   which makes every natural step basis *singular* — so p13 could not have
   fitted the step law even if one exists. Whoever next hits a size-dispatched
   library routine will need this.
12. **`check.py:NNNN` citations in the PATTERN docs have decayed.** ⚠ **This
    header said "22 of them across 12 patterns" long after that stopped being
    true; re-measured at TASK_100-time it is SEVEN across FOUR patterns** —
    `grep -roh 'check\.py:[0-9]\+' patterns/ | wc -l` → **7** (p12, p13 ×3,
    p16 ×2, p38), and the body below already had the right breakdown. ⚠ **All
    four distinct targets spot-checked are rotten**: `:1249` is now `for e in
    v:`, `:625` a fragment of an error string, `:459` the comment `# helpers`,
    `:469` a blank line. ✅ **The `.memory/` half is genuinely clean** — its one
    apparent hit (`06-catalogue.md:830`) is a **quotation of a rotten citation
    being corrected**, not decay. Audited at TASK_066 and **still not fixed**.
    ⚠ **Cost, re-derived: all seven sit in `model.py`/`inputs/gen.py`, which
    `measure.py::measurement_sources` globs PER PATTERN — so this stales FOUR
    records, not all 24.** It is four single-pattern re-measures, not the
    43-minute global one, and the old "defer, it is expensive" framing was
    sizing it against the wrong scope. The
    `.memory/` half *is* fixed (5 of 9 were wrong; the convention and the audit
    aid are at the end of `.memory/02-bench-rules.md`). Spot-checks: p04 and p09
    `spec.md` cite `:929`, now a **blank line**; p05 and p17 `NOTES.md` cite
    `:1446`, now `return {}`; p10 cites `:1254-1292`, now an unrelated comment.
    **Not all are wrong** — p47's `:1755-1760` is still right, and the newest
    patterns' citations are the healthiest, which is the drift signature.

    ⚠ **DO NOT do this as a standalone task, and the reason is a scheduling
    fact worth keeping.** A pattern's gate record globs **`pdir/*.md`**
    (in `check.py::main`), so editing any `NOTES.md`/`README.md`/`spec.md` makes
    that gate record STALE — 12 gate re-runs. But `measure.py`'s `provenance()`
    (`:226-235`) does **not** glob `*.md`, so **it costs no re-measure at all.**

    > **Batch it with the `check.py` edit** that is already owed —
    > `forbidden_hits` fail-vs-print plus p22's per-input timeout
    > (`.memory/02-bench-rules.md`, `.memory/06-catalogue.md`'s p22 triage).
    > That edit stales **every** gate record anyway via the `harness/*.py` glob
    > (item 5 above), so the doc fixes ride along for free.
    > ⚠ **A FOURTH joined the batch at TASK_066_REVIEW and it is one line**:
    > stage 7 builds C at `-O1` **without `-fstrict-aliasing`**, so it cannot see
    > a flag-gated UB class. **It is one flag wide, not one opt level wide** —
    > adding `-fstrict-aliasing` to `check.py::check_sanitizers` makes stage 7 see p38 at
    > `-O1` (ASan `stack-buffer-overflow READ of size 2`). **Blast radius
    > measured across all 20 gate records: exactly one pattern.** 16 patterns
    > declare a `fires` input and **all 16 already fire at `-O1`**, p18 included.
    > ⚠ Do **not** raise stage 7's optimisation level instead — that perturbs 20
    > patterns to fix one.
    > **Four owed changes, one sweep.**

    ✅ **MOSTLY DONE at TASK_068: 25 citations across 13 patterns re-cited by
    function.** ⚠ **6 are deliberately LEFT** — they live in `model.py` /
    `inputs/gen.py` (p12, p13 ×3, p16 ×2, p38), which are **measurement-hashed**,
    so fixing them costs a re-measure. **This item's claim that the sweep costs
    no re-measure is true of the `*.md`/`controls/` subset ONLY.** Targets are in
    `.temp/p68/NOTES.md`; land them behind the p38 re-measure in item 14.
    ⚠ p09's `contract_sha256` moved in the sweep and is disclosed in its
    `NOTES.md`.
    ✅ **The control-name audit is a clean negative — and incomplete.** Only
    **8 of 20** patterns have a `--list`; the other 12 cannot be audited that
    way. All 32 candidates on the 8 were false positives, in five shapes; the
    instructive one is p38's `r4_end`/`r4_slice`, selectable through a *second*
    generator (`controls/span.py --only`) that has no `--list` — **so a naive aid
    would have produced a false accusation.**

    ⚠ **Original note kept for the next sweep: extend it to CONTROL NAMES.** Same
    class, found by the same review: `s_asan_O3` is cited in **three** committed
    p38 files (`NOTES.md`, `model.py`, `spec.md`, hence its generator) and
    **does not exist** — the `-O3` ASan build is anonymous inside
    `do_sanitizers()` and cannot be selected by name. **A doc referring to a
    control nobody can run is PROTOCOL rule 10's failure inside the hashed
    layer.** No cross-pattern audit has been done; control registries are
    heterogeneous (p38 a dict plus hardcoded prints, p47 a `VARIANTS` list), so
    it wants `--list` per pattern rather than a grep.

13. ✅ **CLOSED at TASK_075/076 — `results/synthesis.md` exists**, generated by
    `synthesis/synthesize.py` **from committed records only**, and reviewed
    (TASK_075_REVIEW: 1 blocker, 6 majors, 7 minors, **41 clean negatives**).
    ⚠ **Nothing under `synthesis/` is gate-checked** — it sits outside all
    eleven of `check.py`'s hashed globs, deliberately, so that adding it could
    not stale 22 gate records. **That means no stage validates a number in it;
    the review is the only thing that ever has.**
    **It leads with four limits before the first number**, which is the shape to
    keep: `isolated`-only (of 350 `whole`-mode `-O3` pairs, **334 have
    `kernel_exclusive_ir = None` and all 16 survivors are gcc `kernel.part.0`**,
    so there is not one `whole` row that means what `isolated` means); a
    **per-row licence** on the kernel column; `Ir` is not time; and gcc's column
    carries mitigations clang's does not. ⚠ **`R5 − R4 = 0.00` on all 44 rows is
    scoped as a TAUTOLOGY** — `exact` and `norel` both force `Ir` equality — and
    presenting it as a result would be presenting a gate check as a measurement.
    ⚠ **Still open inside it**: the search objection (`R3 − R4` partly measures
    how hard each side was searched — p13 `−177/−1054` becomes **`+44/+77`, a
    sign flip**), and a `SEARCH_REVIEWED` table that is **hand-maintained for
    lack of a derivable proxy** (only 5 of 10 `--list`s name a source file).

    *Original text kept below — the reasoning still governs where the tool
    lives.*

    **There is NO cross-pattern synthesis, and that is the project's stated
    purpose.** 20 per-pattern tables under `results/tables/`, nothing that
    compares them — while `CLAUDE.md` describes the project as patterns
    *"compared on assembly, instruction count, timing, proof burden and
    trusted-base size"*. A working aggregation probe exists at
    **`.temp/synth/aggregate.py`** (kept per the keep-the-generator rule; it
    reads only committed records, runs in seconds, and needs no measurement).

    ⚠ **It must NOT live in `harness/`** — `check.py` hashes `harness/*.py` into
    every gate record (the `harness/*.py` glob in `check.py::main`), so a file there stales all 21 gates for
    a script the gate never executes. `common/` and `common/layout/` are hashed
    too. Pick the location deliberately.

    **Three things it already exposes — all PROVISIONAL, none reviewed:**

    - **`R5 − R4 = 0.00` on all 40 rows**, both inputs, every pattern. The
      `identity: exact` invariant, visible whole for the first time.
    - **`R3 − R4` is NEGATIVE on 5 of 20 patterns** — p10 (−323/−603), p11
      (−5768/**−24503**), p12 (−26 large), p13 (−177/−1054), p18 (−25/−12). So
      *"safe tuned Rust is dearer than unsafe"* fails on a quarter of the tree.
      ⚠ **Do not quote that as a result.** Several of those patterns have an
      **unsearched R4 side** — the trap in the START HERE box — so the sign may
      be an artefact of R4's spelling. **What the aggregate genuinely adds is
      making that a systematic problem rather than a per-pattern footnote.**
    - ⚠ **A cross-pattern `Ir` comparison is available in `isolated` mode ONLY.**
      Measured: of 318 `-O3` cell/input pairs, `whole` mode has
      `kernel_exclusive_ir = None` in **302** — the kernel is inlined and has no
      symbol. Since **p10 showed regressors SWAP between modes**, any synthesis
      can only ever speak for the mode where that swap was observed. **State that
      limit before the first number, not after the table.**

14. ✅ **CLOSED at TASK_077.** The token landed; blast radius **re-derived**
    across all 22 patterns at **158 rows, 3 differ, all 3 on p38**, and p38's
    `sanitizer_expect` — which returned `"clean"` unconditionally — is now
    **derived** and agrees with the binary on **8/8 gate inputs and 13/13 inputs
    p38 does not ship**. ⚠ **Its domain is narrower than its docstring claimed**
    (it walks the DEFINED window chain; a constructed 2-window blob where a clamp
    diverges the checksum makes the model say `clean` while the binary fires).
    Latent — every shipped clamping input has `nwin == 1`.
    ⚠ **The re-measure cost estimate in the ORIGINAL text below was 3.3x wrong**;
    see the ≈18% retraction in `.memory/03-measurement.md`.

    *Original text kept below.*

    **`-fstrict-aliasing` on stage 7 is MEASURED, CORRECT, and BLOCKED — land it
    bundled with a p38 re-measure.** TASK_068 proved the one-token fix works and
    that the blast radius is **exactly one pattern** (153 matrix rows × 20; p02's
    and p11's apparent diffs are **ELF BuildId inside the ASan text, not
    behaviour**). ⚠ **But the token turns p38's gate RED**, because
    `p38/model.py::sanitizer_expect` returns `"clean"` unconditionally and two
    adversarial rows then fire on an input declared clean. Correcting that edits
    a **measurement-hashed** file → stales `results/p38-alias-pun.json` → forces
    a re-measure → which re-takes the **wall-clock** block, whose `ns` floor is a
    *session* property (≈18% shift measured on p08 for unchanged cells), so it
    **moves p38's published timing rows**. **Schedule token + `sanitizer_expect`
    + re-measure as ONE unit**, and pull item 12's six measurement-hashed
    citations into the same commit.
15. **p01 (1 entry) and p05 (2 entries) ship `forbidden` entries with ZERO
    backticked spellings**, so their *"forbidden: 0 hits"* is earned by auditing
    an **empty set** — the p09 defect `TASK_038_REVIEW` found and TASK_039 fixed
    **on p09 only**. Both now **shout**. Left as a shout deliberately:
    backticking them is a **declaration** edit and owes the direction test, which
    makes it pattern work, not harness work. ⚠ **Now that `forbidden_hits`
    HARD-FAILS, re-ask whether shout is still the right severity.**

16. **Two residuals from the gate's new hard fail, both deliberate, both worth
    re-asking when a pattern trips them.** (a) **Three false-positive shapes
    survive** — substring (`split` vs `split_first()`), whitespace-collapse
    (`q / 64` vs `freq / 64`), and an entry that backticks the *replacement*.
    Each is an entry quoting a span genuinely present in exec code, and
    token-aware matching would break the standard itself: most of the **197**
    spellings are *expressions*, not identifiers, and whitespace deletion is
    **forced by p17**. 0 of 197 fire today. (b) ⚠ **`CODEGEN_CFGS` is a
    whitelist and nothing couples it to `build.py`** — a new `--cfg` there and
    that code silently leaves the audit. **A cross-check against `build.py`'s
    flag list would close it**; it was not built because `build.py` was out of
    scope. ⚠ **`build.py` is measurement-hashed**, so pair it with item 14.
17. ✅ **CLOSED at TASK_077/078 — and it went further than the item asked.**
    The item wanted a decision; TASK_077 made it `(rung x opt)` and **TASK_078
    re-runs EVERY hung cell**. Measured cost on p22: the gate went **221 s ->
    301 s**, i.e. the whole price of confirming 8 cells instead of 1 is **80 s on
    one pattern**. ⚠ **The `mode` collapse the original repair asserted was itself
    the shape it refuted** — it always picked the `isolated` representative.

    *Original text kept below.*

    **`_confirm_hang` verifies ONE cell** (first in sorted matrix order) — it
    proves the declared budget is not absurdly short, **not** that every recorded
    `hung=True` is right. Checking all of them costs `10 × budget × n_hung`.
    **p22 hangs 12–20 cells, so decide there**; it is a one-line change.
18. ✅ **CLOSED at TASK_082** — landed as `patterns/p27-handle-table/NOTES.md`
    §13e with a pointer from `check.py`, bundled into the tree-wide gate sweep
    exactly as this item prescribed.

    *Original text kept below.*

    **p27's `required[2]` finding lives in `check.py`'s docstring, not in
    `patterns/p27-handle-table/NOTES.md`.** Its `` `deallocate` `` entry pinned
    only twin-gated code. The engineer judged a pattern-doc edit outside
    TASK_069's authorised set and **flagged it rather than doing it** — correct.
    ⚠ Landing it moves p27's `source_sha256` and costs a gate run; **bundle it
    with the next thing that re-runs p27.**

19. ✅ **BOTH CLOSED at TASK_077, and (a) turned out to be a check that was not
    running at all rather than a comment that was wrong.** (a) `check_miri` now
    reads stage 4's **measured per-rung `hung` column**; p22's Miri row runs and
    the pattern is `PASS`. **Unchecked-for-UB rows tree-wide: 1 -> 0.** Verified
    as a STRENGTHENING against nine doctored stage-4 tables — the block still
    fires in six, including hangs-only-at-`-O3` and hangs-only-in-`whole`.
    (b) `_confirm_hang` now re-runs **every** hung cell (see item 17).
    ⚠ **Residual, TASK_078 m2**: `_hung_rungs` returns `(hung, measured)` so the
    record can no longer conflate *terminated* with *never measured* — the earlier
    shape printed a sentence stage 4 never said.

    *Original text kept below.*

    **Two gate defects from the hang machinery, both measured twice on p22 and
    NEITHER fixed** (`.memory/02-bench-rules.md` carries both). (a)
    **`check_miri`'s block reason is structurally false for every pattern here** —
    it says *"R4 does not return under Miri either"*, but the bug is in R1 only,
    so `miri.sources` always names a rung carrying the fix. **Cost: one genuinely
    unchecked Miri row per declared hang.** Needs a **per-rung axis** on
    `expected_hang`; `model.py` has a per-input bool only. (b) **`_confirm_hang`
    picks the first cell in sorted order** — `c-clang O0` on p22, **never an
    `-O3` cell**, which is the one C11 6.8.5p6 puts at risk. ⚠ The obvious repair
    is **refuted**: per distinct *rung* would still pick two `O0` cells and would
    have caught nothing. **The axis is (rung × opt).**
    ⚠ **Both are `check.py` edits — batch them**, and note the batch is now
    **FIVE**: these two, item 14's `-fstrict-aliasing` token, and items 20–21
    below.

20. ⚠⚠ **NARROWED AND CORRECTED at TASK_077/078 — NOT CLOSED, and it was one
    commit from being closed wrongly.** The item said the fix is to key
    `duplicate_names` by `(impl, name)`. **That was implemented and it does NOT
    admit the eight-impl spelling**, because `harness/vparse.py::by_name` stays
    bare-keyed and **six** consumers turn its `ValueError` into a failure —
    `check_call_site`, `check_clause_deletion`, `check_requires_strength`,
    `check_trusted_twins`, `derive_contract` in `check.py`, plus
    **`harness/limbs.py:102`, which the review did not name.**

    ⚠ **And there is a STRUCTURAL reason qualification cannot fix it, found at
    TASK_078 and decisive**: `check_trusted_twins` builds its lookup key as
    `TWIN_PREFIX + t.name`, which **hits in a bare map and misses in a qualified
    one**; and `vparse.impl_spans` refuses any `impl` whose preceding character
    is not `{};`, while `#[cfg(slb_twin)]` ends in `]` — **so qualification
    cannot separate the twins the twin stage requires, on the very file this
    item exists for.**

    **Route (b) was taken deliberately: the CLAIM was corrected rather than the
    code**, with five new selftest assertions pinning both limits and
    `check.py`'s comment now saying the spelling is still refused. ⚠ **Changing
    `impl_spans`' matching rule was explicitly NOT done** — it feeds the
    tautology probe's synthesis site for **every** pattern and rule 5's accident
    test has not been run on it. **That is the open work, and it is bigger than
    this item first looked.**
21. ✅ **CLOSED at TASK_075_REVIEW — the answer is NO, and the reason is that the
    column was already in `git`.** `results/gate/pNN.json` carries
    **`marginal_ir_per_call`**, which is whole-program and therefore
    symbol-independent, so `(marg[A] − marg[B]) − (kex[A] − kex[B])` **is** the
    callee correction. It reproduces every large correction in the tree — p11
    `+9815.56`, p08 `−4152.92`, p09 `+379/+2626`, p13 `−190/−264`, p27
    `+120.33/+130.95`, p47 `+88.37/+166.00`, p36 `+129/+1025` — with **0 misses
    at a 2.0 `Ir` threshold** and, above `|corr| >= 16.00`, **34 rows real and 0
    spurious**. ⚠ **Floor ±2 `Ir`, max residual 15.79**, so it cannot resolve
    the ±7 `memset` or the +2 PLT thunk; those need the callee sweep, which
    `synthesis/outward_ir.py` does on demand and publishes nothing from.
    ⚠ **This is `.memory/03-measurement.md`'s OWN prescribed "author-checkable
    test" and the boilerplate in 22 of 22 `results/tables/*.md`.** A `check.py`
    stage and two hashed sidecars were nearly built on the strength of one
    sentence saying it could not be done.

22. ⚠ **DISPOSED at TASK_077/078, and one third of it was REJECTED ON THE
    MERITS — the manager wrote this item and it was wrong.** **`__popcountdi2` is
    NOT a defect**: `is_bulk_symbol`'s contract is *"is this call the kernel's
    loop?"*, scoped to routines scanning or copying an unbounded run of the
    CALLER's bytes; `__popcountdi2` is a libgcc arithmetic helper over **one
    register**, the class `_BULK_STR_WORDS` already excludes (`strtoul`,
    `strerror`). ⚠ **And widening it would have widened GATE STAGE 3a's
    anti-collapse escape hatch** — a documentation complaint would have become a
    regression. **What p09 actually needs is the outward-dispatch list**
    (`.memory/03-measurement.md`), a different question.
    ✅ **`bcmp` upheld as a table defect (4 cells); p11 upheld as a STALE RECORD,
    not a table defect (6 cells), fixable by `measure.py p11` alone** — which
    would also give p11 its first `source_sha256` (item 6).
    ⚠ **The fix is BLOCKED for a scheduling reason, not a technical one:
    `harness/asm.py` sits at `measure.py::measurement_sources:233`, ONE LINE BELOW
    `build.py`, and stales 22 gate + 17 measurement records** — the tree-wide
    radius. ⚠ **Counts were re-derived on ALL cells x opts x modes at TASK_078;
    an `isolated`-only scan undercounts (p11 4->6, p47 3->4).**

    *Original text kept below.*

    **`harness/asm.py`'s bulk-symbol table is wrong in three measured places**,
    so three patterns' records misdescribe their own routine lists.
    `asm.is_bulk_symbol('bcmp')` is **`False`**, so
    `results/p47-ct-compare.json` records `c-gcc: ['memcmp@plt']`,
    `c-clang: []` and `safe_naive: []` for **three cells calling the same entry
    point** (`0x188320` — confirmed by call counts; the whole apparent
    difference is gcc's PLT thunk). `__popcountdi2` is unrecognised, so **p09's
    gcc column records `[]`** while carrying 378.00 / 2625.00 `Ir` per call of
    libgcc software popcount. And **p11's four plain `c-gcc`/`c-clang` cells
    record `[]` while calling `strlen@plt`** — a *stale record*, since
    `is_bulk_symbol('strlen@plt')` is `True`; only its two **R1h** cells are
    populated. ⚠ **That last one supersedes "Owed" 6's follow-up sentence**,
    which said p11's `bulk_calls` are populated today. Reported by two agents,
    fixed by neither — it is `harness/` work.

23. ✅ **CLOSED at TASK_084 — the manager regenerated all three, and the fix
    was exactly the one command this item named.** `harness/report.py p09 p12
    p27` (run separately), diff **9+/10−** across the three files, and all three
    now cite their record's `contract_sha256` — verified by reading each
    `results/gate/*.json` back and checking the hash appears in the table
    (`c391270c673f`, `809c0d6041f5`, `397de62b01ea`, all **True**). No gate run,
    no re-measure, no `contract_sha256` moved. ⚠ **The item had drifted by ONE
    ANYWAY**: it said p12 was stale only on audit counts, but p12's cited
    contract hash moved too. **Re-derive before trusting a stale-list.**
    ⚠ **And nothing will detect the NEXT three**: `results/tables/` is still in
    no hash set, so `--check-stale` remains blind to it. **This item will
    recur.**

    ⚠⚠ **IT RECURRED, EXACTLY AS PREDICTED, AND IT TOOK 16 TASKS.** Measured at
    TASK_100-time: **`results/tables/p09-bitset.md` cites `0a37c0cd1418` while
    `results/gate/p09-bitset.json` says `ea0295eaea6a`.** p09's contract has
    moved **twice** since this item closed — `0a37c0cd1418` at TASK_096 and
    `ea0295eaea6a` at TASK_097 — and the published table followed neither.
    ⚠ **`patterns/p09-bitset/NOTES.md` is CORRECT and complete** (it records all
    four digests in sequence, TASK_068 through TASK_097) **and it even reported
    the RECAP half of the problem itself. The pattern doc was maintained; the
    generated table was not.**

    ✅ **The detector this item said did not exist now does:
    `.temp/mgr99/tables_stale.py`.** It compares the 12-hex prefix each table
    cites against its gate record's `contract_sha256` and **exits 1** on any
    disagreement. Current reading: **24 checked, 1 STALE, 0 skipped.**
    ⚠ **Both arms fire on real data** — 23 tables pass and p09 fails — so it is
    not another control that could not have failed.
    ⚠ **Read the gate records only when no sweep is running**; `check.py`
    rewrites `results/gate/*.json` in place.

    **Fix is one command, `harness/report.py p09`** — but it renders *from* the
    record, so it must run **after** any in-flight sweep, not during.
    ⚠⚠ **The durable fix is the one this item asked for and still has not got:
    put `results/tables/` in a hash set so `--check-stale` covers it.** Until
    then this recurs a third time, and the script above is the stopgap, not the
    answer.

    *Original text kept below.*

    **Three `results/tables/*.md` are CONTENT-stale and cost nothing to fix**
    (TASK_078, flagged by the engineer and deliberately not done — not that
    task's patterns), **re-measured at 3 of 22 by TASK_084**. **p09, p12 and p27**: p09/p27 cite a **superseded
    `contract_sha256`**, and p12/p27 publish **pre-TASK_069 audit counts** —
    p27's still shows RECAP "Owed" 10's *pre*-correction numbers
    (`required pins nothing 3` where its record says 4, missing the
    `` `deallocate` `` row). ⚠ **Nothing will ever detect these**:
    `results/tables/` is in **no** hash set, so `--check-stale` is blind to it
    (`.memory/05-layout.md`). **Regenerating costs no gate run and no
    re-measure** — `harness/report.py pNN`. ⚠ **Do NOT diff bytes to find them**:
    `report.py --stdout` emits one trailing blank line the file writer does not,
    which is why an earlier sweep reported *"22 of 22 stale"* when the real
    figure was 4. Diffs are in `.temp/p78/tablecheck.out`.

24. ⚠ **The old item 21, kept because its question is still live.** Should
    `results/*.json` carry a callee / whole-program `Ir` column?
    p36's **B2 was found by a reviewer summing `callgrind_annotate` rows by
    hand**, and what it found was a *reversed published comparison* sitting
    inside a hashed `idiom.why`. The kernel-exclusive column is right for a
    self-contained kernel and silently wrong when work leaves the symbol — and
    `.memory/03-measurement.md`'s rule was phrased as `@plt`/`@GLIBC`, which p36
    walked past because **its callees are project-local**. The rule is now
    widened; **the open question is whether the harness should record the column
    so the next pattern cannot walk past it either.** ⚠ Cost: `measure.py` is in
    the gate's `harness/*.py` glob (item 5), so it stales every gate record —
    **batch it**, and note `measure.py` is *not* executed by the gate, which is
    why item 5 calls that glob over-broad.

25. ⚠⚠ **`p15` IS RECOMMENDED FOR REFUSAL, AND THE MANAGER'S HALF OF THIS ITEM
    WAS MEASURED WRONG. RUN BY `TASK_085`
    (`.tasks/TASK_085_REPORT.md`) — UNREVIEWED, so nothing here is in `.memory/`
    yet.** ⚠ **The named kill-risk is DEAD and was never the problem.**

    ✅ **A verified UTF-8 validator CLOSES at the pin.**
    `fn is_valid_utf8(b: &[u8]) -> (res: bool) ensures res == valid_utf8(b@)` —
    the **`==`**, not the one-directional `==>` — **`5 verified, 0 errors`,
    ~120 lines, ~10 of them proof, ZERO trusted items**, on three vstd lemmas
    (`partial_valid_utf8_extend`, `partial_valid_partial_invalid_utf8`,
    `partial_valid_utf8` as the loop invariant). The **end-to-end call site**
    the review said it did not know closes verifies **`8 verified, 0 errors`**,
    with vstd's `requires valid_utf8(v@)` discharged **by the validator's
    postcondition alone**. Non-vacuous two ways: a differential oracle against
    `core::str::from_utf8` over **18 499 985 cases, 0 mismatches**, and a
    **10-mutant battery, all 10 failing** — ⚠ **three of them break only the
    COMPLETENESS direction, which a `res ==> valid_utf8` bar would not have
    caught.** ⚠ **This validator is reusable and is the most valuable artefact
    the probe produced; do not let it be lost with the row.**

    **THE THREE JUSTIFICATIONS THE ROW WAS SELECTED ON, EACH MEASURED AWAY:**

    - ⚠⚠ **The harm row is REFUTED — and RECAP repeated it, so this item was
      part of the error.** TASK_083_REVIEW published the truncated-lead cell as
      *"prints NOTHING, exit 0"*, *"ASan n/a"*, *"bounds violation: none"*, i.e.
      *"the optimiser deleted the program's own `println!`"*. **Measured on a
      byte-for-byte replica of the review's own file: `exit 139` — SIGSEGV, not
      exit 0 — 30/30 runs across `-O`, `-O2`, `-O1`, `-O3`, `±codegen-units=1`,
      `±debug-assertions`, and nightly.** And **ASan catches it**:
      `heap-buffer-overflow READ`, a one-past-the-end heap read. **So it is a
      bounds violation, it is the tree's FOURTEENTH `index >= len`, and the new
      harm class does not exist.** ✅ **MANAGER-VERIFIED on an independent
      build** — `rustc -O` on the probe's replica, `trunc` → `exit=139` with
      empty stdout, `other` → `exit=0 len=4 fold=100507`, three runs each. **This
      refutation does not need the review to land.** What survives is row 1 — a silent wrong
      answer **Miri does not catch** — **which is p18's harm, and p18's harm is
      what killed p45.**
    - **The cost axis survives but reverses the row's point.** A verified
      validator is **DEARER than `core::str::from_utf8` at every alphabet**:
      **`+57%` on pure ASCII and `+7%` on all-non-ASCII** — 73756 vs 46921 and
      87661 vs 81960 marginal `Ir`/call, **whole-program marginal, `-O3`, inline
      mode `isolated`**. TASK_083's `+4.1% ASCII` reproduces exactly. **That is
      p11's result a fourth time** — *the safe class reaches a library the
      unsafe class cannot* — **and it is a real finding, not a consolation
      prize.**
      ⚠⚠ **`15.58×` IS WITHDRAWN AND THIS ITEM IS WHERE IT WAS PUBLISHED**
      (TASK_085_REVIEW major 3). ~~`15.58×` on pure ASCII, collapsing to
      `1.13×`~~ is a **RESIDUAL ratio dressed as a rung ratio**: both terms are
      differences against `ctl_assume`, **which is neither rung**. It also
      shipped **with no `Ir` convention and no inline mode beside it**, which
      `.memory/03-measurement.md` requires at every figure because p10 fitted
      both modes and the regressors *swapped*. ✅ **The residual view is still
      the MECHANISM and is worth keeping** — std validates ASCII at **0.449
      `Ir`/byte** against the verified validator's **7.001**, which is the
      word-at-a-time fast path — **but a mechanism ratio is not a rung
      penalty.**
      ⚠ **The slopes are also withdrawn as headline figures.** `R3 +384.78 /
      A +191.18` `Ir`/call per point are **OLS over a strongly concave curve**:
      R3 runs **1210 `Ir`/pt** over 0→10 and **129** over 75→100, and the fit is
      off by **−7210 at pct = 0, which is exactly where the headline ratio
      lives.** ⚠ **And the axis is labelled two ways in the probe's own source**
      — *"non-ASCII **bytes**"* in one place and *"scalars"* in two others, and
      they differ by more than a factor of two (pct=10 by scalars is ~21.9% by
      bytes).
    - **The rung boundary does not survive the gate**, see the new obstacle
      below.

    ⚠⚠ **AND THE OBSTACLE NOBODY NAMED, which is the sharpest thing here:
    `check.py::_scan_unsafe_sites` FORBIDS VERIFIED UNSAFE.** Every `unsafe`
    token in a pinned Verus source must sit inside an `#[verifier::external_body]`
    item or it is a hard `tcb-unsafe` failure. p15's R5 needs
    `unsafe { str::from_utf8_unchecked(b) }` inside a **verified** fn — precondition
    discharged by Verus, **TCB contribution zero**. Complying would *move a
    Verus-discharged call into the counted TCB*, need a hand-written `ensures`
    about `&str` semantics (**the axiom class `TASK_084` is closing**), and need
    a twin that is **unwritable** — `grep -rn "from_utf8" ~/tools/verus/vstd/`
    returns **one** line, the unchecked one. ✅ **Clean negative:**
    `grep -rn "get_unchecked" ~/tools/verus/vstd/` → **0 hits**, so the tree's
    **47** `external_body` wrappers are all unavoidable and **this rule has cost
    the project nothing so far.** **p15 would be the first pattern whose unsafe
    operation vstd actually specs** — i.e. the first R5 that could carry a
    *legitimate* zero in the TCB column. ⚠ **So the live question is no longer
    "can p15 be built" but "is `_scan_unsafe_sites` right?", and the manager has
    NOT decided it** — rule 3 forbids clearing its own call, and the probe's
    evidence for it is a **code read, not an executed gate**.

    ⚠ **What the probe did NOT run, in its own words:** it was barred from
    `check.py`/`measure.py` by the concurrency constraint, so **Q2 and the
    `_scan_unsafe_sites` finding are both code reads of `git show HEAD:`**, and
    **no pattern with `identity: differ` has been through the gate.** One real
    run is owed before either enters `.memory/`.

    *The manager's original analysis is kept below. Its first bullet is
    UPHELD and strengthened; **its second bullet is REFUTED**.*

    - ✅ **UPHELD, and by a hard gate stage rather than the rule reading the
      manager offered.** `check.py::check_proof_domain` (stage 5d) `eval`s every
      derived `requires` at **every kernel call of every model, adversarial
      included**, and `rep.fail`s on the first violation — so this is a **gate
      failure**, not a style objection. ✅ **Clean negative: 0 of 22 patterns
      violate**, re-derived independently by driving each `model.py` over each
      `adversarial-*.bin`. **21 of 22 kernels carry exactly one `requires`** and
      it is the window fact `off + len <= buf@.len()`.
    - ⚠⚠ **REFUTED: `identity` is mandatory as a MEASUREMENT, but the LEVEL is
      a free choice, and the gate EXPLICITLY ADMITS R4 ≠ R5.** `check_identity`
      enforces a **floor only** (`got_i < want_i` is the sole failure path) and
      `rep.note`s when a pattern pins nothing at all;
      `asm.IDENTITY_LEVELS = ["differ", "counts", "norel", "exact"]`, so
      **`differ` is a legal pin.** What makes an identity measurement mandatory
      is `check_miri`, transitively — no pin naming the R4/R5 pair is a hard
      failure at stage 8. And `check_miri` treats R4 ≠ R5 as **supported**: it
      appends *"R4 and R5 differ at O3 …, so R4 does not inherit R5's discharged
      obligations at all"* to `why_required` — **a reason Miri is REQUIRED, not
      a failure.** **So *"21 of 22 pin `exact`"* is true and *"none allows
      R4 ≠ R5"* is true of the `spec.md` files and FALSE about the gate.**

    *Original text of both bullets, kept:*

    - **`requires valid_utf8(b@)` is forbidden outright.**
      `.memory/02-bench-rules.md` *"The precondition must be structural. The
      attack must be data"* is settled at TASK_003_REVIEW and names this exact
      failure: *"a precondition narrow enough to make the proof easy is a
      precondition no caller can discharge."* p15's adversarial inputs are
      invalid UTF-8 **by construction**, so such a `requires` assumes the attack
      away. Same class as the pilot's `requires n < 1000`. **This half of the
      review's advice is right and is not in doubt.**
    - **But "R4 assumes and is UB" cannot ship either, because of the
      `identity` pin.** Measured across the tree: **21 of 22 patterns pin
      `unsafe vs verus` at `exact`** and p36 pins `norel`; **none allows R4 ≠
      R5.** So R4's exec code *is* R5's, R5 must verify with no attack-excluding
      `requires`, and therefore **R4 must be provably memory-safe on invalid
      UTF-8** — i.e. it may not hand unvalidated bytes to
      `str::from_utf8_unchecked`. An R4 that "assumes and is UB" has **no
      verifying twin and is therefore not a rung** (finding 14).

    ⚠ **And that is not a technicality — it eats the measurement p15 was
    selected on.** The probe-3 numbers (**+4.1% ASCII / +100.1% on 2–3-byte
    scalars**) compare *validating* against *not validating*. If R4 must
    validate, that gap is **not a gap between admissible rungs**, and probe 3
    has to be re-run against whatever R4 actually becomes.

    **Three shapes are on the table; the engineer settles it with measurements
    as deliverable §1, before a single cell is built:**

    - **(A) R4 validates with a hand-written verified validator, then calls
      `from_utf8_unchecked`.** Keeps the alphabet axis, and the comparison
      becomes *std's `from_utf8` (SIMD/word-at-a-time ASCII fast path) versus a
      verified hand-written validator*. ⚠ **Predicted outcome is that R4 comes
      out DEARER than R3** — which is **p11's result, a fourth time** (*the safe
      class reaches a library the unsafe class cannot*), and is a real finding
      rather than a consolation prize. The "assumes and is UB" cell still ships,
      as a **control**, which is where its two adversarial rows belong anyway.
    - **(B) R4's cheap check is STRUCTURAL ONLY** (continuation-byte shape, no
      overlong / surrogate rejection), so R4 is total and never reads out of
      bounds, and the proof obligation is what the *missing* checks cost. ⚠
      **Unverified guess: `valid_utf8` is not derivable from the structural
      check** (overlongs pass it), so R5 would have to add them back and the
      identity pin breaks again. **Check this before believing it.**
    - **(C) REFUSE the row**, and publish the refusal as *"the `identity` pin
      makes the interesting unsafe rung inadmissible"* — finding 14's
      R4-chained-to-the-prover result, with p11 and p16 as prior instances.
      ⚠ **A refusal here is a legitimate outcome and the fourth in a row is
      not, by itself, a reason to force a build.**

    ⚠⚠ **THE PARAGRAPH BELOW IS REFUTED — `TASK_085` MEASURED IT AND TWO OF ITS
    FOUR CELLS ARE WRONG. It is kept because it is the reason the row was
    scheduled, and because RECAP repeating TASK_083_REVIEW's cell without
    re-running it is the error worth remembering: `exit 139` (SIGSEGV) not exit
    0, and ASan reports `heap-buffer-overflow READ`. See the top of this item.**

    ~~⚠ **What survives all three, and is why the row is still worth a session:**
    p15's **row-2 adversarial cell** — truncated lead byte, `rustc -O`, the
    binary **prints nothing and exits 0** because `unreachable_unchecked` inside
    `next_code_point` let LLVM delete the program's own `println!`, with **no
    bounds violation anywhere**. Miri catches it, ASan has nothing to catch.~~
    ~~That is *"the optimiser deleted the programmer's code"* — the harm class
    proposed for `p45` and **refuted as stated there** — real, measured, and in
    the shipped-language rung. **It ships as a control under (A) and (B) and as
    the evidence under (C).**~~ ⚠⚠ **STRUCK TOO. `p45`'s harm class was refuted
    there and it is refuted here as well** — the truncated-lead cell is an
    ordinary out-of-bounds read that SIGSEGVs and that ASan reports, so nothing
    in it is *"the optimiser deleted the programmer's code"*. **Two rows now
    claimed that class and neither had it.**

    ✅ **Row 1 SURVIVES, was re-measured, and is the honest weakness — it belongs
    in any p15 `spec.md` up front, not discovered later:** an invalid
    *continuation* byte is a silent wrong answer, `len=4 fold=100507`, exit 0,
    **Miri clean** — which is p18's harm, **and p18's harm is what killed p45.**
    ⚠ **With row 2 gone, row 1 is the WHOLE of p15's harm story, and it is a
    class the project has already refused a row over.**

26. ⚠ **THE `copy_from_slice` FALSE CLAIM IS ALIVE IN `check.py` ITSELF — THIRD
    SITE, AND THE WORST ONE.** (TASK_085_REVIEW minor 7.) The **5c-twin stage's
    own docstring** says *"there is no vstd spec for `copy_from_slice`, so a
    bulk-copy twin is not available"*. **The pinned vstd ships
    `assume_specification<T: Copy>[ <[T]>::copy_from_slice ]` at
    `std_specs/slice.rs:205`.** `patterns/p02-buffer-copy/NOTES.md:692` already
    carries the correction; **the gate's explanation of its own rule does not.**
    ⚠ **This is the exact claim `CLAUDE.md` records as having stood from
    TASK_004 to TASK_048** — and this site is **the one an engineer reads while
    being told to write a twin**, so it is the site most likely to cause the
    error again. ⚠ **Cost: it is a `check.py` edit, so it stales every gate
    record — BATCH IT with the next thing that re-gates**, and do **not** send it
    to an agent mid-sweep, which would invalidate the records already written.

27. ⚠⚠ **THIS ITEM'S HEADER SAID THE OPPOSITE OF ITS OWN BODY AND IS FIXED HERE.**
    It read *"the authoritative layer cites 34 `.temp/` paths, and NONE of them
    exists in a fresh clone"* — while the very next paragraph said all 34 exist
    and there are **zero** broken citations. **The body was right.** Re-measured
    at TASK_100-time: **`.memory/` cites 45 distinct `.temp/` paths, 43 exist,
    and the 2 that do not are the `pNN` PLACEHOLDERS** (`.temp/build/pNN/`,
    `.temp/pNN/`), which are prose. ⚠ **Item 12 above had the same defect — a
    stale header over a maintained body. When skimming this queue by header,
    do not trust the header.** Original text, corrected, follows.

    **The authoritative layer's `.temp/` citations all resolve.** Measured, not
    estimated:
    `grep -rho '\.temp/[A-Za-z0-9_./-]*' .memory/ RECAP.md | sort -u` gives
    **36**, of which **2 are `pNN` PLACEHOLDERS** (`.temp/build/pNN/`,
    `.temp/pNN/`) and the other **34 all exist on this box**. ✅ **So there are
    ZERO broken citations today** — do not go chasing the two, they are prose.

    ⚠ **The open question is not "are they broken" but "are they BACKED".**
    `.memory/05-layout.md` item 11 permits a `.temp/` artefact **provided a
    committed generator derives it**; `p15` exposed the gap where no generator
    can exist (a refused row has no pattern dir), and that gap is now closed by
    item 11's corollary. **Nobody has audited the other 34 against item 11's
    condition.** ⚠ **This is a manager's count plus a manager's inference, and
    the inference is the untested half** — the count is one command and it is
    above; whether a missing generator actually costs anything is not.
    **Cheap to settle: for each of the 34, does a committed file regenerate it?**

28. ⚠ **"BLAST RADIUS CHECKED AND EMPTY" FOR THE `rep movsb` `Ir` INFLATION IS A
    TASK_074 STATEMENT, AND SIX PATTERNS HAVE LANDED SINCE.** (Raised by
    TASK_090, disposed by the manager.) `.memory/03-measurement.md` records that
    glibc's byte-wise `rep` paths cost **≈1 `Ir` per byte** against the vector
    path's **0.104** — a **10×** inflation of one retired instruction — and that
    the blast radius was checked **at TASK_074**, when p02's 61 B and 4092 B
    copies were the evidence. ✅ **TASK_090 sharpened the crossover to
    EXACTLY 8192 bytes** with a `GLIBC_TUNABLES` control, which is a better
    instrument than the original bisection.

    ⚠ **What is owed is only the RE-CHECK**, over the patterns built since —
    p13, p14, p18, p10, p27, p47, p38, p22, p36, p19. ⚠ **And it must respect
    the distinction TASK_090's own worry blurred: what matters is the size of an
    individual `memcpy`/`memmove`/`memset` CALL inside the measured window, not
    the size of the input file.** The shipped 16 KB and 12 MB blobs are not
    themselves copied. **Needs `measure.py`, so batch it with something that
    re-measures anyway.**

29. ⚠⚠ **`TASK_086`'s HARM TABLE IS HALF-SHOWN FOR FOUR ROWS, AND THE CAUSE IS
    `head -4`.** (TASK_090.) `.temp/t86/harms.sh` truncates each run's output to
    four lines; **gcc's UBSan report for these rows is exactly four lines and
    ASan's banner is on lines 5–6.** Re-reported with `grep`, rows **`p21`,
    `p24`, `p26` and `p41` each fire BOTH detectors.** The p24 cell — *"only
    UBSan sees it, ASan did NOT report a heap-buffer-overflow"* — is **false**:
    ASan reports it in **all three storage classes on both compilers**, and
    **UBSan alone reports nothing anywhere.** ✅ **Reproduced on TASK_086's own
    unmodified binary.** ⚠ **Treat every harm cell in that table as half-shown
    until re-run.** ✅ **p24's row is corrected in the catalogue; p21, p26 and
    p41 are NOT** — p41's refusal does not rest on its harm (it died on probe 3
    and on duplicating p07), and p21 and p26 are deferred, **but whoever
    schedules them re-runs the harm first.**
    ⚠ **The general lesson: `head -N` on a sanitizer's output is a truncation
    that looks like a measurement.** Use `grep` for the banner you want.

    ✅✅ **CLOSED — the re-run this item asked for is DONE, and it is a CLEAN
    NEGATIVE.** Manager, at TASK_100-time: `bash .temp/mgr99/harms_grep.sh`
    rebuilds from `.temp/t86/harms.c` **unmodified**, changing only `head -4` →
    `grep` (and adding `env -u LD_PRELOAD`). **The half-shown claim reproduces
    exactly** — `p21` (ASan 1 / UBSan 2), `p24` (1/1), `p26` (1/1), `p41` (1/1)
    all fire both, while `p20` (ASan 2 / UBSan 0) and `p19` (0/2) fire one each
    and **were shown correctly all along.** ⚠ **`p19ok`, the no-bug row, reads
    clean on both binaries — so the corrected table has a failing arm and is not
    another vacuous control.** ⚠ **`-O2` exit codes worth keeping: `p24` exits
    `0` — SILENT and wrong; `p26` exits `134`, glibc abort; `p19`/`p35p` exit
    `139`, SIGSEGV.**

    ⚠⚠ **AND THE VERDICTS ALL SURVIVE, WHICH IS WHY IT WAS WORTH CHECKING RATHER
    THAN ASSUMING.** The corrupted cells are descriptive, not load-bearing:
    **`p21`'s DEFER** rests on *"p14's bug class verbatim"* plus *"no new
    bound"*; **`p41`'s REFUSE** rests entirely on probe 3 (`k41_tuned 2387.00`
    beating `k41_unchecked 2404.00` — the safe rung wins by `17.00 Ir`/call and
    the apparent 9.6× was **100% R3 spelling**) plus duplication of `p07`;
    **`p40`'s REFUSE** is a cache-sim result and untouched. **Four harm cells
    were corrupted and ZERO verdicts were.**
    ⚠ **Do NOT merge this table with `TASK_090`'s p24 sweep** — that one covered
    three storage classes on both compilers and concluded *"UBSan alone reports
    nothing anywhere"*; **`harms.c`'s `p24` row is one synthetic shape and fires
    both.** Different experiments, both correct.

30. ⚠ **`check.py::check_marginal_ir`'s DOCSTRING IS TOO STRONG ABOUT THE ±7
    BISTABLE TERM, and p46 is the FOURTH pattern to hit it.** (TASK_092.) The
    docstring says *"the term is `whole`-mode only"* and that `isolated` *"is not
    merely small, it is **exactly invariant**"* — evidenced on an **`-O3
    isolated`** cell. **p46's movers include five `-O0 isolated` cells.**
    ✅ **Corrected rule: `-O3 isolated` is invariant; `-O0` moves in BOTH
    modes.** The docstring also names **three** patterns at ±7 (p03, p04, p38);
    **p46 is the fourth.**

    ✅ **The rest of the docstring is RIGHT and TASK_092 confirmed it end to
    end:** the term is **bistable**, the discriminator is *"the presence of a
    single environment variable, not its size"*, and the mechanism is the
    environment block shifting the stack pointer → a per-call stack array's
    alignment → a different tail in `__memset_avx2_unaligned_erms`. **p46
    `memset`s TWO stack arrays per call, which is why its `unsafe`/`verus`
    `O3 whole` cells move by exactly `−14 = 2 × 7`.** ✅ **And it explains the
    "gate record is not bit-reproducible" minor two reviews have now raised: two
    consecutive `check.py p46` runs move 2 of 963 values, both ASan address
    strings, ZERO `Ir`.**

    ⚠ **Cost: it is a `check.py` edit, so it stales every gate record — a
    24-pattern sweep (~45 min) for a comment. BATCH IT** with "Owed" 0's sixth
    route, B5's remaining minors, and the `p09/spec.md` citations.

### Deferred with a stated reason

- **The mechanical rate-vs-disassembly backstop** (~90 lines, prototype exists).
  Deferred twice, and the second time the engineer's own session was the argument:
  every defect that actually occurred was a class-membership or arithmetic error
  no `body_len / K` assertion would catch.
- ⚠ **RETIRED at TASK_082 — THIS ITEM WAS ALREADY DONE AND SAT HERE FOR FIFTY
  TASKS.** It said stage 3c's `head()` still reads *"recorded as a result"*.
  **It has read `"3c. structural identity R4-vs-R5 (recorded as a result AND
  enforced)"` since `1b41c85` (TASK_032).** ⚠ **The mechanism is worth more than
  the item was: a naive `grep` for the substring `recorded as a result` STILL
  HITS the corrected line**, because the correction *appended* rather than
  replaced — so every re-audit confirmed the item was live. **A substring search
  cannot tell a claim from its own correction**, which is the third instance of
  TASK_065's lesson (*a wrong command is worse than a wrong constant, because it
  looks self-verifying*). **Grep for what the FIXED text would say, not for what
  the broken text said.**
  ⚠ **Adjacent and NOT fixed, found while retiring this:**
  `patterns/p01-array-sum/spec.md` still carries
  `| identity | recorded as a **result**, not a gate condition` — the exact
  sentence `check.py` says was false. **Only p01 has it.** It is a hashed pattern
  doc, so it costs a p01 gate re-run; **bundle it with the next thing that
  re-gates p01.**

### Closed arcs — history, not work

- **Gate hardening** (T001–T010). Closed by the user's call.
- **The spelling arc** (T015–028, thirteen tasks). Produced the named-spelling
  standard, four refuted floors, p16's sign error, and the
  **R4-is-chained-to-the-prover** result. Its distilled rules are
  `.tasks/TASK_026.md` §0 — **the shortest statement of what this project knows
  about reporting spellings, and worth reading before writing any task file.**
- **The layout arc** (T026 → 029 → 030_REVIEW → 031). Produced finding 16 and
  `common/layout/`.

## State

**Verified at this handoff** — re-run these four before trusting anything below:

```bash
harness/measure.py --check-stale          # the invariant is "0 STALE"; the record
                                          # count moves with every pattern added
harness/check.py p13                      # or any pattern; every one is green
grep -rho '\.tasks/TASK_[A-Za-z0-9_]*\.md' .memory/ .tasks/ RECAP.md \
  | sort -u | while read f; do [ -e "$f" ] || echo "MISSING: $f"; done
# the shared named-spelling paragraph must be ONE hash across all patterns:
python3 -c "import hashlib,glob;print({hashlib.sha256(open(f).read()[open(f).read().find('NAMED-SPELLING STANDARD'):open(f).read().find('p01 and p08 neither')+19].encode()).hexdigest()[:12] for f in glob.glob('patterns/*/spec.md')})"
```

- **Every pattern green**: p01 is `PASS-WITH-BLOCKED-ROWS` (Miri policy on its
  `large.bin`, documented, not a regression) and **every other pattern is
  `PASS`, with 0 failures tree-wide.** ⚠ **A list of pattern names used to sit
  here and it went stale twice.** Print it:

  ```bash
  python3 -c "
  import json,glob
  for f in sorted(glob.glob('results/gate/*.json')):
      d=json.load(open(f))
      print(f.split('/')[-1][:-5], d['verdict'], len(d.get('failures') or []))"
  ```
- **The shared named-spelling paragraph is byte-identical across every**
  `idiom.why` block — currently one hash, `59748cce2db5`, 11 003 bytes.
  ⚠ **The value depends on how you slice the span**, so trust the *command*
  above (all patterns equal) and not a copied constant: this line previously
  recorded `c3d36c92a28a` for the same intact invariant, measured over a span one
  byte longer. **What matters is that the set has size 1.**
- `harness/` — `check.py` (**18** stages; this line said 17 and
  `.memory/05-layout.md` said 16 — enumerate them with
  `grep -o 'head("[0-9][^"]*"' harness/check.py | sort -u | wc -l`, do not copy a
  constant. ⚠ **The `sort -u` is load-bearing and the first version of this
  command lacked it**, returning 19: `head("1. build the matrix")` appears
  **twice**, two entry points into one stage. TASK_058 caught
  it — a command that is wrong is worse than a constant that is right, because it
  looks self-verifying. ⚠ The two line numbers written here were `:1218`/`:4903`
  and had drifted to **`:1404`/`:5104`** by TASK_066 — **which is the point:
  the command is still right, and the constants beside it rotted.** Run
  `grep -n 'head("1\. build' harness/check.py` rather than trusting either),
  `asm.py`, `dloop.py`, `vparse.py`,
  `build.py`, `measure.py` (now writes `source_sha256` + `input_sha256` and has
  `--check-stale`), `report.py`, `fixture.py`. `common/layout/` ships the layout
  harness and `common/layout/data/` its p01 population, so finding 16 is
  **auditable without re-measuring**.
- **Reports exist for every task whose report is cited.** Six recent tasks
  (T036, T038–T042) have **no `_REPORT.md`** — nothing cites them, and their
  content lives in the commit messages and the patterns' own `NOTES.md`, which
  the gate hashes. **Write one before citing it** (PROTOCOL rule 10); that rule
  exists because the manager once cited a report it never wrote.
- **Toolchain**: Verus `0.2026.08.09.92f466f`, rustc 1.97.1, clang/LLVM 22.1.6,
  valgrind 3.27.1, nightly+Miri, all in `~/tools`, no root. `TOOLCHAIN.md`.
- **Gitignored blobs outside `.temp/`**: `patterns/*/inputs/*.bin`. All
  regenerable from each pattern's `inputs/gen.py`, all verified deterministic by
  regenerate-and-diff. `rm` outside `.temp/` stalls on review, so they are the
  user's call.
- **`.temp/`** is scratch and is swept periodically. ⚠ Read
  `.memory/00-environment.md` constraint 6 **as it now stands** — its first
  written form was destructive.
- **Commits run through the p04 landing. Tree clean.** ⚠ **A GitHub remote exists
  (`origin`, `HALOCORE/sec-ladder`) and the local branch runs ahead of it. Do not
  push unless the user asks.**

## Decisions

- **Proof-effort budget**: one engineer session per R5 cell, then stop and report
  where the proof stuck — that report *is* the deliverable for that row. Set by the
  manager, pending a user override.
- **`perf_event_paranoid ≤ 1` needs root and is still owed by the user.** It is the
  only way to explain *why* gcc's shorter loop runs slower. Nothing works around it.
