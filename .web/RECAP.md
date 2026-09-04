# RECAP — state of the report

For an agent picking this up cold. Read `CLAUDE.md` first (the rules), then this
(the state, the reasons and the traps). `README.md` is the outward-facing copy.

## START HERE

| | |
|---|---|
| **What it is** | A static report over `../results/` and `../results/gate/`. Eight views, one page, no framework beyond the vendored JSONML + Incremental DOM. |
| **Served at** | `http://127.0.0.1:8000/pw11apt/apps/pub-to38u0zfu2/` — the user's ccneo server, route `pub-to38u0zfu2` → this folder. **Do not start another server.** |
| **Before believing any change** | `node check.mjs` → must print `OK`. After a CSS change, screenshot as well; the check does not see stylesheets. |
| **After anything lands upstream** | `python3 build_data.py`. It prints warnings for evidence it does not understand, and those warnings also render at the top of the Method tab. |
| **State at last update** | Counted at build time, not written here — `python3 build_data.py` prints cells, adversarial runs and obligations, and the header counts patterns from `data/index.json`. A hard-coded figure on this line went stale within a day: it read *23 patterns · 732 cells · upstream `6e52208`*, and p46 landed upstream mid-session. |
| **Git** | This directory is its own repo, currently clean. The parent repo is other agents' live work — never write there. |
| **⏭ RESUMING COLD?** | Read this box, then **"What is built, and what is next"** immediately below, then `CLAUDE.md`, then **`PITFALLS.md`**, then `.memory/`. Those five carry everything. The rest of this file is the reasoning behind them. |
| **✍ WRITING PROSE?** | **`PITFALLS.md` first, and it is not optional.** Five framings of the report were rejected for one mistake in four disguises, and every gate was green each time. The checks in this repo cannot see whether a document is readable. |
| **Memory** | `.web/.memory/` — in the repo, **not** `~/.claude/…/memory/` (`CLAUDE.md` rule 9). It holds the *user's* preferences and standing decisions; the *app's* state is this file. |

## What is built, and what is next

*Written so a cold reader can continue without the conversation that produced it.*

### Built and verified

| area | state |
|---|---|
| Overview | rewritten to argue before it counts: two-track ladder (C adds safety, Rust removes cost), R4 de-emphasised as *not a destination*, no results figures |
| Responsive | four breakpoints; `tools/responsive_audit.mjs` checks overflow, header shape, sticky panes and split-grid alignment arithmetically |
| Syntax highlighting | `syntax.js`, hand-rolled, emits **tokens not HTML**; Verus classed semantically (spec / proof / ghost / **trusted**) |
| Diffs | 6 pairs: C→hardened, R2→R3, R3→R4, R4→R5, hardened C→R4 (clang only), gcc vs clang. Split (default) and unified, comments hidden by default, capped scrolling |
| Assembly | `asmcache/` (committed, digest-checked against `results/`), per-instruction source lines, graded **certain / likely / approximate** |
| Linking | click a source line → its instructions light and scroll; click an instruction → its line lights; cross-language sources laid out by shared-instruction anchors |
| Guarded notes | `insights/insight_*.py` — prose emitted only while its assertions hold |
| **Paper** | `paper_vers/ver_X/` → the **Paper** tab, via `paper.js`. One directory per **framing**, not per draft. `\num{}` resolves against `data/index.json` at build time and a bad path **fails the build**. Spec: `paper_vers/README.md`. **Five framings; `ver_E` is current** — a dialogue with a sceptical C developer, every section an objection in their voice. A–D are kept, not edited: each was rejected as a *framing*, and a version is a framing. The tab follows `"current": true` |
| **The talk** | `slides.js` + `slides_deck.js` + `tools/render_deck.mjs`. **50 slides**, rendered as a 16:9 banner at the top of the Paper tab, `⤢ expand` for the viewport. ⚠ **The engine refuses to build a slide that cannot name the question it answers**, and `check.mjs` renders every slide in both states. Under a hard size cap — see the talk section below |
| **⚠ `PITFALLS.md`** | **What did not work, ordered by cost. `CLAUDE.md` rule 0.** Every entry shipped with green gates. Read before writing prose or touching the renderer |

### The paper — `paper_vers/ver_A`, drafted and once-revised

*Where the obligation goes.* Thesis: **no rung discharges a safety obligation —
each relocates it**, and the residual is predictable from the resource the new
mechanism quantifies over. Core artefact: the **guarantee quadruple** (property ·
bearer · quantifier · residual) and a taxonomy of property classes against the
mechanisms that reach each, one worked case per class.

Written by five agents from the primary sources, then attacked by four reviewers
(fact-check, research rigour, practitioner value, writing advisor) and revised by
four more. **What the review found, and what it cost:**

- **Four blockers, all real.** A section repeated a claim another section
  retracted; the predictivity claim was inverted by the record (the abstraction
  accounts for the gaps *after the fact* — the one prediction the project
  registered before a probe was refuted); the trusted-base accounting omitted
  the solver entirely (`Z3`, `SMT` and `soundness` appeared **nowhere** in 18,000
  words); and the ladder's trust column said safe Rust trusts *"nothing"*, which
  is false and contradicts the paper's own thesis.
- **The thesis appeared in ZERO of the five files carrying its evidence.**
- ~2,900 words of redundancy: five anecdotes told four to six times each.
- The only *"what should you do"* section was about how to quote the paper. There
  is now a **What to do** section assembling the six things already proven.

**The fact-check settled the headline.** 129 rows, 58 deviating, **45 silent /
12 crash / 1 hung** — and both published splits are correct, differing only in a
tie-break on 6 named rows that are silent in one build and crashing in another.
It also confirmed a long list of things the paper gets right, which is as
valuable: the six-rung table reproduces cell by cell from the JSON, the naive
rung's 7.26× median and its range reproduce to the digit, and the proof totals
correctly use shipped-rung figures. **Do not "correct" those.**

⚠⚠ **The sharpest lesson of the whole review, and it is about method:** the
paper claimed the largest per-call working set was 4,328 bytes. **My own
re-derivation agreed with it and was wrong** — I matched `work/call=(\d+)B` and
p19 writes that field with no `B` suffix, so the true maximum, 6,144, was
invisible to the grep. The reviewer read the file. **A fact-check that
re-greps confirms the same blind spot; one that re-derives from the record
does not.**

⚠ ver_A is ~17,400 words and **stays as it is**. It was rejected by the owner as
a *framing*, not as a draft — *"I cannot understand anything and I don't give a
fuck of those philosophy"* — and a version is a framing, so it is not edited and
not trimmed. `ver_B` replaced it. Do not spend a session shortening ver_A.

### The paper — `paper_vers/ver_B`, the current framing (`"current": true`)

*Before you rewrite it in Rust.* **It argues nothing in the abstract.** It answers
the three questions a working developer arrives with — what will this cost me,
will my tools tell me if I am wrong, am I done if it is memory-safe or proved —
and **introduces a concept only after the obvious answer to one of them has
failed against a measurement.** `REWRITE_VERB_PLAN.md` is the plan it was built
from; `.temp/verify/RULINGS.md` records the evidence settlements, and is the file
to read before changing any claim.

**6,792 prose words, down 61% from ver_A**, and the abstraction is kept but
earned: **property · bearer · resource** arrives *fourth*, after three programs
verify and break, in a sentence that says it is *"the shortest thing that tells
those three programs apart, and for no other reason."*

**The acceptance test passed.** A practitioner persona read `00-summary.md`
cold — nothing else — and named three Monday actions unprompted: put a known-bad
input in the ASan job and fail on silence; audit where each hot loop's bound
comes from; harden the C you are not rewriting.

**What the process cost and caught.** Four grounding agents, five writers, three
blind reviewers, two trim passes. The reviewers **contradicted each other three
times** and every settlement improved the paper — that is the argument for
running them blind and in parallel. What they found:

- ⚠⚠ **One of the three "verifies and is broken anyway" programs did not
  exist.** The stack-overflow kernel is a *refused* catalogue candidate: its run
  logs contain zero occurrences of the exit code the claim quotes, its build
  script never invokes the prover, its sources do not survive a clone, and its
  own report says the verified function is not the same kernel. `RECAP.md`
  upstream registers it in a "family of three". **A summary of a measurement is
  not the measurement** — the project's own retraction rule, applied to the
  project. Cut.
- **`undeclared` in the search-state column means *nobody wrote an entry*, never
  *nobody searched*.** The binary search's shipped safe spelling is the **dearest
  of four in contract**; the cheapest found pays 5.0000 instructions per probe,
  not 6.0000. The paper now catches itself in public and moves its own worst
  number by a sixth.
- **Four omissions all ran toward safe Rust** — every cost figure the tuned rung,
  `-fcf-protection=full` unnamed beside a gcc-vs-clang comparison, the exact
  C/Rust instruction match missing, and the deleted-check evidence a full table
  where Rust wins beside a clause where it does not. One of those is *literally
  on the project's own list of the omissions that constituted its documented
  coverage bias last time.* All four fixed. **Commission this as an explicit
  review question; nothing else finds it, by construction.**
- **Two trusted-base attacks were being shown as live holes that had been
  stopped** — the verified twin rejects the weakened precondition, and the
  identity pin plus Miri catch the substitution. Bias against the verifier is
  still bias.
- **The supervisor's own ruling was wrong once** and a reviewer caught it: the
  range parser's shipped rung *is* a disclosure on the crosswin pair; the
  retraction was about a different input. See `RULINGS.md` R7-CORRECTED.

⚠ **`residual` is gone as a coined term.** Two reviewers found it unused after
its own definition, misapplied on first use, and colliding with the ordinary
regression sense the paper needs in two headline claims. What it named survives
as a sentence: *whatever a guarantee does not range over is still your problem.*

⚠ **A correction owed UPSTREAM, which we cannot make (rule 1).** The parent's
`RECAP.md` records that the largest per-call working set is 6,144 bytes, having
corrected 4,328. **That is still wrong.** The `work/call` field carries five
different units across patterns and one `model.py` says so outright — one
pattern's bare `4096` is 4096 `u64` = **32,768 bytes**. Fixing the regex is not
enough; the unit is per-pattern. ver_B makes no superlative over that field.

### The paper — `paper_vers/ver_C`, the current framing (`"current": true`)

*A safety claim is an attribution claim.* **6,935 prose words, nine files, built
from `REWRITE_VERC_PLAN.md`, then rewritten in place for plain language.** ver_A had a thesis nobody could read; ver_B is
readable and argues nothing (its own framing statement says so). ver_C keeps
ver_B's readability and adds the argument.

**The thesis:** both halves of a safety number are routinely misassigned — the
cost you are quoted is usually not the check, and the guarantee you assume is
watching the wrong resource.

⚠ **The framing correction that decides it, and the most likely regression.** The
corpus's genuinely surprising findings split *verification 8 · measurement 9 ·
mechanism 5 · C-and-Rust 6*, so **a version framed as "what does a Rust rewrite
cost" is framed against its own evidence.** ver_B was framed exactly that way.
ver_C is about attribution and measurement, with C and Rust as the **instrument**.
⚠ That split is the thesis agent's own grading of the corpus, not a figure from
the tree — treat it as an argument, not a measurement.

**Read before touching a claim:** `paper_vers/CLAIMS.md` (committed, binding on
every version) and `.temp/brief/RULINGS.md` (**34 rulings**, of which C31–C34 are
post-review settlements). ⚠ `.temp/` is gitignored and may be gone; `CLAIMS.md`
is the part that had to survive.

**What the process cost and caught.** Six evidence agents on primary artefacts,
one outline, nine writers, four blind reviewers, a revision pass, a second bias
review, a final balance pass. Highlights:

- ⚠⚠ **The plan's central tally was wrong: 3 of 10, not 2 of 10.** Two defects in
  the hand-written synthesis caused it — one row was given a *different rung
  pair's* mechanism, and one has **no instruction-level attribution anywhere** and
  is now reported as **unattributed**. A threshold sweep from 50 to 300, signed
  and absolute, returns **the identical check-dominant set every time**, which is
  better evidence than the ratio and kills the "you chose the cut-off" attack.
- ⚠⚠ **ver_B's detector table committed the coverage bias this project documented.**
  It asserted *no cell reads "silent, and it should have seen this"* — true only
  after **six of twelve rows** were dropped, one of them a sanitizer blinded by a
  hardening flag, which ver_B describes in prose three sections earlier. ver_C
  restores twelve rows and files the retraction beside the claim.
- ⚠⚠ **Exit 101 appears zero times in the corpus.** No Rust rung ever panics on
  hostile input; the safe rungs compute the reference answer. So the adversarial
  matrix cannot witness that a check is present, and the evidence a safe rung's
  bound is real is **the source text, which no gate stage reads.** That bounds the
  paper's own method, so it ships with it.
- **Three of the supervisor's rulings were overturned** — a fold width, a
  published quotation that turned out to be a **splice of two sentences from two
  pages**, and C16, whose denominator was the very truncation C15 retracts. All
  three were caught by someone who opened the artefact rather than the ruling.
- **The bias review found what four other passes missed, twice.** First: 21 unused
  results cutting against the proof and 4 for it, plus a *unit* choice — absolute
  deltas for every check row, percentages only where the number was small or
  damaged our instrument. Then, after the fix: **over-correction**, and worse, the
  paper carried non-gate-certified *failure* evidence prominently while omitting
  gate-certified *success* evidence entirely. **The provenance ran the same
  direction as the bias.**

**The acceptance test passed.** A practitioner persona read `00-summary.md` cold —
nothing else — named the thesis in their own words and gave **four** Monday
actions. ver_B passed the second half and had no thesis to name.

### ⚠⚠ THE PLAIN-LANGUAGE REWRITE, AND WHERE IT STOPPED

The owner read the finished draft and rejected it: **"It is not understandable
again... how can a fucking undergrad understand this shit at all?"** They were
right, and the cause is diagnosable. Four reviewers checked rigour, facts and
coverage bias; **one** checked readability, and every revision round ADDED words.

**What the rewrite did.** 8,037 -> **6,935** prose words. Median sentence **27 ->
17**; sentences over 35 words **40+ -> zero**. The word `vacuous` is gone; the
detector table now reads **caught / missed / not its job / —**. Section titles
went from 22 words of jargon to under twelve plain ones.

⚠ **THE ROOT CAUSE WAS A RULE OF OURS, AND IT IS AMENDED.** `CLAIMS.md` §3.4 used
to demand every number ship its scope **in the same sentence**. Applied by nine
writers under four reviewers each demanding more scope, it mechanically produces
sentences with two nested qualifications. It now permits **the next sentence**,
which defeats the screenshot just as well.

**⚠ THE SCORE PLATEAUED AT 5/10.** Four cold reads by an undergraduate persona
reading the WHOLE paper: **3 -> 4 -> 5 -> 5**. Per section on the last read:
§1 **8**, §5 **8**, §99 **8**, §7 **7**, §2 **6**, §6 **5**, §0 **4**, §3 **3**,
§4 **3**. **The paper is no longer uniformly hard; two sections carry the
deficit**, and the last reader quit at §3 calling it *"the sixth demonstration of
one idea"*.

⚠⚠ **The remaining gap is STRUCTURAL, not verbal, and the options need the
owner's ruling** — each changes what the document is:
1. **Cut §3 to its one reason to exist** (the admission that our own baseline is
   inflated) and fold the rest into §2.
2. **Shrink §4's table to the rows the paper narrates.** ⚠ This contradicts
   ruling C15: twelve rows exist BECAUSE dropping six was the documented bias.
3. **Lead with the worked example and demote the summary** — recommended
   independently by two readers.

**What the readability review caught that four rigour reviews did not:** a 15%
figure that **descends from a number with zero occurrences anywhere in the tree**,
now cut; a clause telling the reader which direction to read an admission, now
cut; and the summary and §4 publishing the same pair with **opposite** emphases.

### ✅ New this round, outside the paper

- **`insights/p16_control.py` + `p16control.json`** — the deleted-check table's
  five rungs, rebuilt from the parent's **shipped** sources and re-run (Verus
  included) in ~7 seconds. It takes its build flags from `harness/build.py` by
  spying on it, so no flag is retyped, and aborts loudly if the deletion no longer
  matches one site. **Three of its four rows previously had no surviving run log
  anywhere in the tree.** `--check` re-runs and diffs.
- **`insights/insight_p16control.py`** — the cheap half: re-hashes the shipped
  sources and withholds the note if one moved, which `build_data.py` renders as a
  Method-tab warning. Negative-tested both ways.
- **`build_data.py`: two fixes.** Markers inside `%%` comments were being
  validated, so the build could fail on prose `paper.js` never renders; and the
  reported word count included comments, publishing a 7,400-word paper as 17,700.
  Both corrected; counts are now prose-only.
- **ver_B corrected twice** — a mechanism attributed to the wrong pattern (the
  `rep`-string explanation belongs elsewhere and is explicitly ruled out there),
  and a provenance sentence the new generator made false.

### ✅ `paper_vers/ver_E` — BUILT, `"current": true`. 7,158 words, 8 objections, 11 sub-objections

⚠⚠ **THE OWNER'S LAST TWO CORRECTIONS, AND BOTH ARE STANDING RULES NOW.**

**(1) Every answer is top-down and self-skeptical internally, not just the
document.** *"The answers to the skepticism are not crisp, fuse many points
together… Focus on main point. DO NOT talk about all kinds of details randomly."*
The ladder between sections was right; **inside** them the answers were a flat
stream — §2 fused six points, §3 fused ten, §8 five. Every section and
subsection now runs **three moves and nothing else**: the answer alone, then the
smallest evidence that carries *that* answer, then — visibly separated, usually
on a hinge sentence like *"Now the parts that cut against that"* — where the
answer breaks. **The test is to render the move-1 sentences alone and read them
as a list;** `tools/render_paper.py` makes that a one-liner. That also fixed the
cold reader's *"no number survives its own paragraph"*: doubt now applies to a
whole answer instead of being welded onto every figure.

**(2) The paper may not mention earlier versions of itself, anywhere.** The
`meta.framing` abstract used to render as an open callout **above the title**;
it is now a collapsed `details` **below the references** (`index.js`). All four
in-prose self-references are gone, including §7's third retraction, which
narrated a claim a previous draft withdrew. ⚠ The *research project's* own
retractions stay — that is section 7's subject.

**Every section is an objection in a C developer's own voice; the answer is the
evidence; the next section is what they say after hearing it.** That fixed the
one error four framings repeated — organised by FINDING, not by OBJECTION. A
finding carries no motivation, so every section had to argue for its own
relevance first, which is the abstract throat-clearing the owner rejected four
times. An objection carries its own, because the reader supplied it.

**The breadth-first property is mechanically checkable, not asserted.**
`python3 tools/render_paper.py ver_E --level1` cuts every section at its first
sub-objection: **4,415 words that read as a finished paper.** Level 1 was written
and read that way *before* any sub-objection existed. If a future edit breaks it,
that command says so.

⚠ **The placement the whole framing rests on was tested, not assumed.** A sceptic
persona, given only the pitch and forbidden to read the plan, produced its own
ladder and independently put *"why not just harden my C?"* at **7 of 9** — for the
plan's reason: asked first it is a cheap dismissal, and it is only sharp once you
believe the cost is small, nonzero and unevenly spread. **Do not move it.**

**Three reviews ran. Each found a class the others were blind to.**

1. **Fact-check against primary artefacts — 13 of my own evidence pack's entries
   were wrong or misleading.** I had written that pack *after* reading
   `results/SYNTHESIS.md`. ⚠⚠ **A summary is a claim about the evidence, not the
   evidence.** Worst: *"0 of 4,104 runs end loud"* is FALSE (109 signals, 8 hangs,
   all on plain C); the C-vs-Rust comparison **reverses** on the rung the project
   says to use; *"proof text is mostly comments"* is false and runs the wrong way.
2. **Cold read by a C developer: 7/10**, sections 5 / 8 / 8 / 7 / 7 / 6 / 8 / 6.
   The intro scored lowest — 900 words of pre-emptive caveats before the first
   number — and is now ~330. Two genuine ladder holes: **nobody asked what a panic
   costs** (a stop is a DoS in a daemon), and a **strawman about C tooling**
   (static analysis and fuzzing appeared nowhere). Both now have nodes.
   ⚠ Its closing finding, and it outranks the score: *"no number in this document
   survives its own paragraph… four things out of maybe eighty stayed with me, and
   they are the ones that arrived without an immediate qualifier."* Hence the
   corollary now governing every figure: **if a number needs a qualifier it cannot
   carry, cut the number, not the qualifier.**
3. **"Which way do the gaps point?" — found a real coverage bias, and diagnosed
   it.** ⚠⚠ *"Its disclosures cluster in the two places the last review looked —
   search depth and the identity pin — and its gaps cluster in the three it did
   not: what the instrument measures, what the corpus is made of, and what the
   proof rung has been measured to fail at."* **That is a general law about
   review, and the next version should be audited against it first.**

**What that review changed, all now in the paper:** 17 patterns carry a wall
clock, not two, and the bitset is **+205.6% instructions against +205.4–219.7%
wall clock — no discount at all**, so an instruction count is not reliably even an
overstatement; the obligation count is cut entirely (it is a size proxy and
`CLAIMS.md` §3.7 was being violated); the trusted base is a **soundness surface**,
not just a price — Verus's own printed `assume_specification` carries no
`requires` and no `ensures` and will verify a 1 MiB out-of-bounds read; and §7's
bias direction was **inverted** — dropping five results that flattered safe Rust
made that document unfair *against* it.

⚠ **Two agent refusals worth keeping, both correct.** A writer refused my
instruction to call `+27 / +77` a *floor*, because the passage the reviewer cited
is struck through and marked WITHDRAWN — I had passed on the framing without
re-checking the strikethrough. And a writer caught that `143,740,000` is a
**whole-run total, not per call**. Give writers the reasoning, not just the rule,
and they check the rule.

⚠⚠ **A 27th PATTERN LANDED MID-SESSION AND BROKE THE PAPER WITHOUT BREAKING A
SINGLE `\num{}`.** `p29-bst-delete` arrived with verdict **FAIL** and no entry in
the research synthesis, moving `totals.patterns` 26 → 27. Every live value
updated correctly and the **prose went wrong anyway**: *"25 of the 26"* rendered
as *"25 of the 27"*, silently asserting two exceptions where the next sentence
describes one. **What changed was the denominator's meaning, not the number.**

✅ **The fix is `totals.passing.*`** (`build_data.py`) — the same arithmetic over
gate-passing patterns only, which reproduces every figure the paper was written
against (26 · 828 · 4,104 · 350/0 · 108/230 · 404%/424%). **A paper resolves
against that namespace; the site's own totals still pool everything, which is
right for a status page and wrong for a report.** `build_data.py` now warns
exactly this whenever something fails, and the paper discloses the excluded
program in its own opening. Rationale recorded in `paper_vers/README.md`:
**`\num{}` keeps a number live, it does not keep a sentence true.**

⚠ **`LESSONS.md` 14c was HALF WRONG and is corrected.** It blamed only the prose
for literal backticks in a heading. A title renders **twice** — through `md()` as
the `h2`, and **raw** into the outline — so a *legitimate* code span in a heading
also leaked, and a writer following that entry would have deleted correct markup
to appease a renderer defect. The outline now runs `md()`. **The doubled count
was the diagnostic and it pointed at the second render.**

### ⏭ THE ADVISOR-READY PASS — what changed and what is still owed

**Research closed at 33 patterns.** All 33 now have a write-up, assembly and a
licence-checked cost row. Four review agents (two fact-checking against the
tree, one for undergraduate readability, one role-playing the advisor) found
**33 defects**; the ones that mattered are fixed and are in the commit log.

⚠⚠ **THE VERDICT WORTH REMEMBERING**, from the advisor review:
> *"`results/SYNTHESIS.md` is more honest than the website built from it."*

That was true, and it is the standing risk for this app: the research tree
qualifies its own claims harder than the report did. **When in doubt, go and
read what the synthesis says about a number before repeating it.**

**Two of the defects were mine, from this session** — I took RECAP finding 37
without reading `SYNTHESIS.md` §5, which marks it *DISPUTED — DO NOT QUOTE*,
and I published p23's headline at `3.11×` after review corrected it to
`1.315×`. **RECAP is not the last word; the synthesis is.**

**Built this pass:** licence marks (`‡`) on every cost chart and the delta
table, including a **C→hardened-C licence the research does not publish** and
this app derives by the same rule; the provenance fold (results derived on 26,
re-derived on 33); the selection fold (33 of 49, and the withdrawn admission
bar); *the zero is a rule, not a result*; proof goals defined and marked as a
size proxy; the all-green Rust columns explained as **structural**; 43 of 186
adversarial inputs disclosed as making **zero kernel calls**; and one derived
result on the front page, which had none.

**Still owed, in priority order:**
1. ⚠⚠ **The visual pass — still nobody's eyes.** `node check.mjs --snap` then
   open `.temp/snap-index.html`. Headless capture remains broken on this box.
2. **Related work is invisible.** ~19 references exist in the Paper tab
   bibliography and **zero core tabs cite anything**. The layout finding is a
   rediscovery-with-mechanism of known work and saying so would strengthen it.
   Fil-C, CHERI, Checked C, Kani and Creusot are not mentioned at all.
3. **The pattern pages dump `NOTES.md` (up to 91 KB) and the hashed idiom
   block verbatim**, in shouted capitals with task IDs and scratch paths. Fold
   the raw contract the way the docs are folded.
4. **p02's "runs 23% slower"** is an unbracketed whole-process level ratio, and
   the pattern's own notes say so.
5. Six rows publish a cost with one or both sides unsearched; the charts mark
   the licence but not the search state.

### ⏭ STATE AT HANDOFF, AND WHAT TO DO NEXT

**Both artefacts are built, committed and green.** `paper ver_E` **7,706 words /
8 sections**, breadth-first cut **3,940**; the talk **50 slides**. `build_data.py`
0 errors, `check.mjs` OK, responsive and syntax exit 0, working tree clean at
`63ad06f`.

**What the last round changed, in one line each:** the setup was cut from three
slides / fifteen bullets to two; the paper's opening from ~500 words to ~330; the
bookkeeping paragraph (*"26 → 22 → nine → nine → four… do not add those up"*) is
**one sentence with no denominators in it**; the 26-versus-27 explanation is
**deleted, not explained**; every deck slide is under the cap; the binary
search's last frozen kernel figures are live; and *"a mistake inside an `unsafe`
block is the same class of memory corruption you get in C"* — which a cold reader
called the single most important sentence for a C developer — is now in both.

⚠ **THE NEXT MOVE IS PROBABLY STRUCTURE, NOT MORE EDITING.** Both documents have
now been read cold and scored **7/10**, and the remaining complaint is shape: too
many findings, each perfectly qualified, so a reader leaves with none. The four
things this work actually has to teach, and a candidate spine:
1. **Safe Rust is not C plus checks** — same program, two ways of writing it,
   +69% against +0.9%. So most benchmarks measure who wrote the code.
2. **Where the compiler genuinely cannot see it you pay** — rarer and smaller
   than either side claims, and only one of three rows survives searching.
3. **A proof makes the check non-optional at zero run-time cost** — but proves
   only what you wrote down, which is the one-character typo.
4. **Hardened C does fine on outcomes.** The difference is that in C the check is
   optional.

**Still owed, in priority order:**
- ⚠ **The deck CSS has never been looked at** (~120 lines, `CLAUDE.md` rule 6;
  headless capture does not work on this box). Screenshot `.temp/snap-paper.html`.
- The two remaining unclosable figures a reader could not size: the binary
  search's instructions-worsen-while-time-improves has **no explanation in the
  tree** and the paper now says so; and *"about 24 instructions per call"* is a
  median whose range (−125…+10,242) is the real finding.
- The gaps review's uncarried items: **`ptr_offset` is 0 of 255 built bound
  sites** against a 6.9% median in real C, and **four measured proof failures**,
  of which two are in the paper.

**Old note, retained for the budget argument only:** **7,158 words against a 5,000–6,000 budget** (down from 7,983;
the crispness pass cut 12% by deleting material that failed the move-2 test).
The proof node is still the heaviest at ~730 words. The gaps review listed items
still not carried: **`ptr_offset` is 0 of 255 built bound sites** against a 6.9%
median in real C, and **four measured proof failures**, of which two are in the
paper. ⚠ **Every frozen literal in the paper — 22 licensed rows, the 9/4/9
buckets, the 17 rows behind the 7.26×, fifteen spatial — was derived against the
26 passing patterns and must be re-derived together or not at all.**

### ⚠⚠⚠ `PITFALLS.md` — WRITTEN THIS SESSION, AND IT IS `CLAUDE.md` RULE 0

**Read it before writing prose or touching the renderer.** It is the record of
everything that did not work here, ordered by cost. ⚠ **Every entry shipped with
GREEN GATES** — `build_data.py`, `check.mjs`, the responsive and syntax audits all
passed on documents a reader could not follow. The checks in this repo cannot see
whether a document is readable, which is the whole reason the file exists.

The four that cost the most, and they are one mistake in four disguises:

1. **You will write a proof. You are supposed to be teaching.** This project's
   research discipline — every number ships its scope, its denominator, its
   counterexample — is right for the research and a **disease in the write-up**.
   It produces *claim → scope → denominator → counterexample → qualification*.
   Teaching needs **claim → one concrete picture → so what.**
2. **"The reader was confused by X" NEVER means "explain X better."** Four rounds
   answered confusion with another clause; the paper went 7,158 → 9,209 while
   *length* was one of three things it had been docked for. ⚠ **A fix that
   worsens the primary complaint is not a fix.**
3. **Front-loading is not motivating.** Four separate "move it earlier" fixes
   built a **seven-topic setup slide** because nobody re-read the destination.
4. **One named example is a sample, not the defect.** *"I said this is
   problematic DOES NOT MEAN this is the only problematic."*

✅ **The corollary that resolves most of it:** if a figure needs a qualifier it
cannot carry, **cut the figure, not the qualifier.**

### ⚠⚠⚠ TWO BLIND COLD READS — the deep causes, and what they cost

Both artefacts were read once, cold, at reading/talk speed, by a C developer who
knows almost no Rust and had **only the rendered output**. Both scored **7/10**.
The talk lost them at one slide and **wasted the two after it**; the paper came
within one paragraph of being abandoned in section 2. Two causes, shared:

**1. WE PUT NUMBERS ON SCREEN THAT INVITE ARITHMETIC THAT DOES NOT CLOSE.**
> *"626 to 502 is not vanishing… **I sat there doing arithmetic that doesn't
> close while the speaker moved on.** That is the moment I stopped following."*

Also: our *"the same total, to the digit"* on a figure with four trailing zeros —
*"the one place I felt actively worked on"*; a 65× span that computes to 52 or 57
from the printed numbers; three counts summing to 22 and then retracted as "not a
partition" (*"the single most expensive 40 seconds in the piece"*).
> ✅ **AN AUDIENCE SHOWN TWO NUMBERS WILL SUBTRACT OR DIVIDE THEM.** Any ratio
> stated must be derivable from what is on the page, or the numbers do not go
> there. The bounded-stack slide now shows its own working (4 off every pop, 2
> onto every dropped push, 118 and 207 pops, 352 dropped) and both results fall
> out by multiplication.

**2. BOTH RAN IN THE ORDER THE RESEARCH HAPPENED, NOT IN DEPENDENCY ORDER.**
Used-before-given, every one now moved: the bug class the whole thing is about
(talk: slide 17 → 4); every number coming from a no-inline build (slide 47 →
3); what the prover is (argued from at 16, defined at 26); and in the paper, the
proof's zero presented as a **finding** in §2 and disclosed as a **rule we
imposed** in §5.1 — *"you let me spend it for 140 lines."*
> ✅ **NOTHING MAY BE USED AS EVIDENCE BEFORE IT IS DEFINED.**

⚠ **A PLACEMENT I DEFENDED WAS HALF WRONG.** An early sceptic put *"why not just
harden my C"* late (asked first it is a shield); this reader says it is their
**first** objection and *"where it sits, it feels like it was held back."* **Both
are right: the CONCESSION moves early, the SECTION stays late.** Section 2 now
concedes the outcomes tie outright and says section 6 does not walk it back.

⚠ **A SENTENCE THAT SHOULD ALWAYS HAVE BEEN THERE.** Nothing anywhere said that
**a mistake inside `unsafe` is the same class of memory corruption you get in C**
— *"the single most important sentence for a C developer and it is missing."*
Now in §4.1.

⚠⚠ **TWO FALSE CLAIMS TRACED TO MY OWN EVIDENCE PACKS**, both found only by
translating into plain words: *"the copy has no version to price, because safe
Rust will not compile one"* — **false**, `copy_within` is priced at +0.4%/+0.1%;
and *"three assertions away"* — **appears nowhere in the research tree.** A fact
pack is not a source, for the fourth time.

⚠ **A FIX THAT WORSENS THE PRIMARY COMPLAINT IS NOT A FIX.** The paper reached
**9,209 words** mid-repair while *length* was one of three things it was docked
for. Cut back to **8,085**; the title now promises **seven** objections and says
the top level alone is a complete short paper, which is the reader's actual
complaint (*"I budgeted for eight and got 5,500 words"*) and costs nothing.
**Owed, if the owner wants sub-7,200 — each costs facts:** fold §3.1 (−120, one
rung of the ladder); drop the bitset wall-clock counterexample (−60, but the
paper would then teach that instruction counts always overstate, which is false);
cut §6.2 (−300, five measured facts); cut §5.3 (−180, the only real-CVE artefact).

⚠ **ONE THING WE CANNOT FIX AND NOW SAY SO.** The binary search's instructions
worsen with size while its wall clock improves. **The tree has no explanation** —
the one conversion sentence that existed is formally withdrawn — so the paper now
says we cannot explain it, and that quoting the instruction figure alone quotes a
cost nobody has shown anybody paying.

✅ **AND THE LESSON FROM WHAT WORKED**, in the reader's words about the one slide
they believed without checking: *"It jumps around the array by a rule the
optimiser cannot follow… **I've read that disassembly. I believed it instantly
and I didn't need the numbers.**"* **Where we gave a MECHANISM in their
vocabulary they believed us; where we gave a MAGNITUDE they tried to check it and
we lost them. Prefer mechanism.**

### ⚠⚠⚠ THE SAY-IT-OUT-LOUD TEST — apply it to the QUESTIONS, and audit ALL of them

The frame pass below fixed the answers and never checked the questions. The owner
got lost at slide 11 of 52:

> "I am lost from **'But I measured a big number'** already. **How can the
> audience 'measure' your number???** … I said this is problematic DOES NOT MEAN
> this is the only problematic."

**A third of the questions were ones a PEER REVIEWER asks about a method**, not
ones a person in a room asks about their code — *"What does the corpus say?"*,
*"How hard did you look?"*, *"Is that zero real?"*, *"Is your corpus even
representative?"* They pass every structural check (they are questions, they are
ordered, each follows the last) and they still make the deck unreadable.

> ✅ **THE TEST: could somebody say this out loud, having heard only what came
> before?** If it needs our methodology to make sense, it is us defending a
> paper. `tools/render_deck.mjs --questions` renders them alone; read them as one
> person talking.

⚠ **The worst one had its answer nine slides away.** Under *"I measured a big
number"* is **"I've seen benchmarks where Rust is slower"**, and the answer —
most published safe-Rust numbers put somebody's first port against decade-tuned
C, a factor of **seven** — was stranded after the centre section. The deck is
re-cut: that objection now sits at ≈7 min with its own answer.

⚠ **Move a concession, never drop it.** *"How hard did you look"* is not an
audience question, but its content is our best volunteered honesty and is now
slide 43 in the trust section, under **"What else would you rather I didn't
ask?"** — stronger there than it was as a methodology aside.

⚠ **52 → 48, not the 34 the re-cut plan claimed.** My own keep/cut table marked
44 of 52 KEEP, so 48 is what it arithmetically yields; the agent executed the
table and said so rather than silently cutting protected concessions. **48 is a
legitimate 45-minute deck** (8 of them are one-line objection slides).

⚠ `totals.passing.crash` / `.hung` added to `build_data.py` — their absence had
forced one slide to freeze "109 … and eight" as literals, because an unscoped
total cannot sit in a sentence whose subject is a passing-only count.

### ⚠⚠ THE FRAME PASS — the owner's third correction, and it outranks the first two

> "**The questions make sense, the answers make no sense.** You think the audience
> will read our code? Which reader will read the code and measure the data…"

Structure (ver_E) and crispness were both real fixes and **neither touched the
defect.** The answers were written *from inside the project*: the grammatical
subject of nearly every one was *this corpus*, *the shipped set*, *the 22 rows
licensed for differencing*. Nobody asked about the apparatus.

**The rule, now applied to all 8 sections and all 52 slides** (`.temp/verE/AUDIENCE.md`):
1. **Whose world is the subject?** Their code, their decision — method only where
   it changes the answer, in one clause of plain words.
2. **Is every number sized in the same breath?** *"24 instructions per call — on
   any function that does real work you will not find that in a profile."*
   *"Seven times. Not seven percent."*
3. **Could they repeat it in a meeting tomorrow?** If it needs our repository, it
   is not an answer.

⚠ **Translation, never deletion.** Every fact and scope stays and the concessions
get *stronger*: *"the safety net I am selling you has never been photographed
catching anybody"* carries the same measurement as *"zero of 4,104 runs end
loud"* and actually lands.

⚠⚠ **THE TRANSLATION IS ITSELF A REVIEW — four claims got weaker the moment the
jargon came off.** *"Hardening C is cheap"* is false as a law (the median hides
−125…+10,242, and the dearest case is a whole validation pass, not a check). The
bitset's 65× span reads as a caveat in jargon and as *"we shipped the expensive
one and the clock agrees with it"* in English. The binary search — the one row
that survives searching both sides — is 42–47% of instructions and **1.6% of wall
clock**. **If a claim only sounds strong in your own vocabulary, it is not strong.**

⚠⚠⚠ **AND `%%literal-ok` HAD BECOME A SILENCER.** The paper printed *"126
required-but-absent spellings"* with `%%literal-ok 126` beside it. The real value
is **175** — and the literal-ok was suppressing the one warning that would have
caught it. A number frozen on purpose and one frozen by mistake are
indistinguishable from inside `build_data.py`, so it now **lists every
suppression on every build**. Two more live/frozen bugs went with it: a Miri
paragraph that printed a live total then broke it down as "192 executed and 2
blocked" (194, not the total — arithmetically false on the page), and every
figure quoted out of the research synthesis now resolves against
`totals.passing.analysed`, which `build_data.py` parses from that document's own
*"drawn from N kernels"*.

### ✅ THE TALK — a 45-minute deck, banner-figure at the top of the Paper tab

`slides.js` (engine) + `slides_deck.js` (the deck) + `tools/render_deck.mjs`
(text). **50 slides**, 16:9 in the page flow, `⤢ expand` to own the viewport,
arrows and Escape while expanded.

⚠⚠ **THE DECK IS UNDER A HARD SIZE CAP AND IT MUST STAY THERE.** 24 of 35 answer
slides had drifted past 150 words or 5 bullets; the worst was **286 words** — a
page of prose projected on a wall. The cap: **one-sentence headline · at most 3
bullets of ≤30 words · one aside ≤35 words · ~120 words total.** Worst slide is
now 116. ⚠ **Get there by cutting a whole bullet, splitting the slide, or moving
it to the paper — NEVER by making sentences denser**, which is what produced the
mess. Five slides were split (claim, then concession) rather than squeezed.

Audit it with the one-liner in `.temp/verE/`-era history or simply: build the
deck, and for each answer/two slide print bullets and word count; nothing may
exceed 3 / 150.

⚠ **Slide 2 lists the six versions as a TABLE, not a sentence.** It was a 54-word
bullet and it was the slide the owner named as incomprehensible. Six things in a
sentence is a wall; six things in a table is three seconds. **Do not turn it back
into prose.**

⚠⚠ **THE DECK'S ONE RULE IS ENFORCED IN THE CONSTRUCTOR, NOT IN A STYLE GUIDE.**
Every answering slide requires `q` — the question from the floor it exists to
answer — and `SLIDES.build` **throws** without one; the engine then prints that
question on the slide. **You cannot add an interesting-but-unmotivated slide to
this deck, because the page will not render.** That is ver_E's discipline made
mechanical, and it is the reason to keep the engine rather than hand-write HTML.

- **Numbers are live, prose is hand-written** (`CLAUDE.md` 2 and 3). The deck
  body is a *function* of a data helper: `D.n("passing.patterns")` and
  `D.ir("p16","small","unsafe")` resolve against `data/index.json` at render, off
  **`totals.passing`**, so the talk and the paper cannot drift and neither can go
  stale in a drawer.
- **`node tools/render_deck.mjs --questions`** prints the questions alone. **That
  is the deck's breadth-first cut**: if the interrogation does not read as
  coherent with every slide removed, the running order is wrong. It caught three
  slides whose "question" was a stage direction (*"Row two?"*).
- **`check.mjs` renders all 52 slides in both states.** Before that it walked
  slide 1 only — 51 slides could have been malformed and it still printed OK.
  It also fails on an unresolved live value and on a deck under 20 slides.

⚠ **NOT VISUALLY VERIFIED.** `index.css` grew ~120 lines and `CLAUDE.md` rule 6
says a green render check cannot see a stylesheet. Headless capture does not work
on this box. The geometry is `container-type: inline-size` with `cqw` type so one
scale serves banner and projector, with an `@supports not` fallback — **but
nobody has looked at it.** Screenshot `.temp/snap-paper.html` before trusting it.

### ✅ `paper_vers/ver_D` — built, `"current": true`, superseded in intent by ver_E

**3,571 words. One cold read: 8/10** (sections 9 / 7 / 8 / 6 / 9), against
ver_C's plateau of 5 across four reads. The reader restated the claim correctly
without scrolling back — the question three versions had failed — and named
three things they would actually do. `REWRITE_VERD_PLAN.md` was the work order;
the brief and verified fact pack that executed it were `.temp/verD/{BRIEF,FACTS}.md`
(gitignored), and `.temp/verD/COLDREAD-1.md` holds the read.

**Title:** *One missing check, six versions, five different endings.* Six
versions produce five distinct outcomes because plain C and unsafe Rust crash
identically.

⚠⚠ **THE PLAN'S DIAGNOSIS WAS HALF WRONG, and the correction is the durable
part.** Cardinality is real but it is not why anyone quit. Re-reading the four
cold-read transcripts: **all four quit on REPETITION**, none on difficulty. One
counted eight demonstrations of *the number depends on which two versions you
subtract* — *"I would have closed the tab"* — and two of the three best sections
sat after the point they would have stopped. So there are **two** rules, not one:

1. one concrete subject in the reader's head at a time (and it must be a thing
   that **did** something — ver_C's best-scoring section has no program in it);
2. **demonstrate each finding exactly once.**

**The post has a CLAIM, in the opening's third sentence, with no numbers in it** —
*"the useful thing you get from a memory-safe language is not that the check is
fast, or well written, or even that it is there. It's that you can't leave it out
and not find out."* Three versions failed *"what is it claiming?"*; ver_D has no
summary section, so the claim had to live in the opening or nowhere.

⚠ **The hardened-C row in the opening table is load-bearing and was nearly not
written.** Without a C row that behaves perfectly, the table licenses *"C
crashes, Rust stops"* — a claim `CLAIMS.md` §2.4 bans. The cold reader: *"without
a C row that behaves perfectly, I'd have read the whole table as an advert."*

**The fact-check found seven real defects, listed under "Owed" below where they
touch other versions.** Three came out of ver_C's prose via the fact pack, which
is the lesson: **a fact pack is not a source.**

⚠⚠ **THE OWNER HAS NOW REJECTED THREE VERSIONS AND SAYS ver_B IS BETTER THAN
ver_C.** The third rejection names the exact sentence: ver_C opens *"A safety
number is a claim about what caused what"* — and the reaction was *"WHAT safety
number? campus security phone number?"* ver_B opened *"You have a C or C++
codebase and somebody has proposed rewriting part of it in Rust."* **One tells
you who you are; the other assumes you already know the subject.**

**ver_D is a BLOG POST**, 2,500–3,500 words, for a second-year undergraduate.
Not a tech report written plainly — a blog post.

**The finding the plan is built on.** Four cold reads of ver_C scored 3, 4, 5, 5.
The per-section scores track exactly one variable: **how many things the reader
must hold in mind at once.** One program, one change → 8. Ten programs in a
table → 6. Twelve bug classes × six tools → 3. It is not tables; the 8-scoring
section has one and the 3-scoring section has none. **Never more than one program
in the reader's head, and no claim about the corpus before the program it came
from.**

⚠ **ver_D does not have to be complete, because ver_C is.** All three earlier
framings stay on disk and the site has 26 pattern pages. ver_D is the front door
and it **delegates**. That is the most freeing fact in the plan.

⚠ Two failure modes that have burned three versions: **glossing our jargon and
not the real jargon** (ver_C defined `rung` and `spelling` and never once defined
`kernel`, which a reader took to mean *operating system*), and **every revision
round adding words** — plain phrasing costs ~10% more than nested phrasing, so a
readability pass makes the document longer. **If ver_D passes 3,500, cut a story,
never a qualification.**

### Owed, in the order I would take them

0. ⚠⚠ **`ver_C` SHIPS A FALSE SENTENCE THAT ver_D's FACT-CHECK CAUGHT.**
   `ver_C/sections/50-nonoptional.md` says *"no stage of our gate reads
   source"*, and ver_D's draft inherited it. **It is false.**
   `harness/check.py:1216` `spelling_matches` says so in its own docstring —
   *"since TASK_068 it is also a gate check: `idiom_audit` calls it against
   every rung source"* — and `results/gate/p16-tlv-walk.json` publishes
   `required_absent: 1` with `absent: [{spelling: "vlen > end - (p + 3)", rung:
   "c/kernel.c"}]`. Corpus-wide `totals.idiom.required_absent = 126`. The gate
   **reads** the source and **records** the missing check; what it does not do
   is **fail** — only a `forbidden` hit fails a run. ver_D now says that, and it
   is a better sentence for being true. **Fix ver_C's copy.**
   ⚠ Three further ver_C defects the same check surfaced, all in its bounded-stack
   example: the clamp is a line **added**, not a check deleted
   (`p03/NOTES.md:366-371`, and `:405` — *"the dead test is gone"*); the
   surviving `+5` **is** explained, as the window-reslice check
   (`:1259-1260`); and `p03/NOTES.md:1263-1266` says in bold **"Do not publish
   that as p03's safety tax"**, which ver_C's example box arguably does. Also
   ver_C's ten-row table reclassifies two rows away from `results/SYNTHESIS.md`
   (p05 → the check, p14 → unattributed) without saying so in the prose; the
   published table's own verdicts are **three check, seven not**.

1. ⚠⚠ **THE VISUAL PASS — and it is now a one-file job, so please do it.**
   `node check.mjs --snap` writes **`.temp/snap-index.html`**: every view in an
   iframe, with a width selector across the four real breakpoints
   (1440/900/720/560/400) and a light/dark switch. Open that one file over
   `file://` and scroll. **Nothing on this page has been looked at by a human
   except through the user's screenshots**, which have twice caught bugs no
   structural check could.
   ⚠ **Headless capture is BROKEN ON THIS BOX and it is not our page**: a
   trivial 80-byte HTML file hangs identically, warm profile or cold, at 60 s
   and at 120 s. Trap 5's recipe does not work — do not spend time on it again.
   The only unblock would be installing Playwright proper, which is a network
   install and a dependency this repo does not have; ask first.
2. ~~p46's write-up~~ · ~~`verus_exit_anomalies`~~ · ~~the layout chart~~ — **all
   done**, see "Landed since" below.
3. ~~Unsurfaced evidence~~ — **done.** Sanitizer runs are classified in the
   outcome matrix's vocabulary (10 in the corpus exit 0 with the *wrong answer*;
   one never returns, and both used to render as "silent"), Miri names its
   trusted items, and the idiom audit has a corpus section on Method plus a
   per-pattern fold.
4. **p23-partition wants its full write-up once its review lands upstream.** It
   currently carries its catalogue headline with the provisional label, and
   nothing else.
5. Older items are in "Owed, roughly in order" further down. What is genuinely
   left there is small: `data/docs/` is now **3.6 MB** of verbatim notes (fine
   locally), and Method could still say more about the two `Ir` conventions.

### Landed since the handover — read this before re-deriving anything

- **All 25 patterns have a write-up.** `p14`, `p18`, `p46` and `p23` were
  written from each pattern's own README/NOTES plus its finding in `../RECAP.md`.
  ⚠ **`p23-partition`'s is deliberately narrow**: taken from `spec.md` only, it
  quotes **no** measurement, cost law or proof result, because it landed
  mid-session and has not been reviewed upstream. Fill it in after its review.
- **`verus_exit_anomalies` is resolved, and was not guessed.** `harness/check.py`
  documents it where it writes it: a run in which Verus reported `0 errors` and
  the process still exited non-zero — the proof satisfied and `rustc` not. Empty
  on every pattern, so it ships as a KPI whose zero *is* the evidence, plus a
  per-pattern callout that renders only when non-empty.
- **The layout control has its chart** (Cost tab, under "Instruction count is
  not time"), which closes the oldest owed item. All six rung-to-rung
  comparisons **change sign** across 31 byte-identical builds; the widest band
  is 18.2 points. The chart **refuses to draw** if the control's builds ever
  stop agreeing on `md5_fn_norel` and `n_fn`.
- **A gate that did not pass now says so** — leading callout on the pattern
  page, the failure *messages* rendered (they never were), and provenance
  carries `passing / total` because every corpus count pools them.
- **`md()` grew italics.** It supported `**bold**` and `` `code` `` only, so
  **106** emphasised spans across `content.js` and `index.js` were rendering as
  literal asterisks — in sentences whose whole point was the emphasis. ⚠ It
  still does **not nest**; see `LESSONS.md` #13, and the sweep in `check.mjs`
  that now enforces it.
- **Finding 15 exists**: *this instrument can only price a check that some rung
  emits and another omits* — eight candidate bug classes probed, eight refused,
  each on a measurement. It is the answer to "how many more patterns?" and the
  report had no version of it.
- ⚠ **Two hard-coded counts were found and fixed by sweeping for them.** The
  Findings lede said *"Twelve results … Four of them are marked corrected"* while
  the list held **fifteen and five**. A finding's `caveat` field was also being
  dropped by the renderer without a trace. Both are `CLAUDE.md` rule 2 and rule 3
  failures that had already gone stale — **re-run that sweep after adding prose**
  (number-word or digit followed by patterns/findings/rungs/cells, over every
  string literal in both files).

### ⚠ Upstream moved three times in one session — plan for it

`p23-partition` appeared as **sources only**, then **gate record with no
results** (the build warns and skips it), then **results with verdict FAIL**,
then **PASS** — inside one afternoon. `p47-ct-compare` arrived complete in the
same window. **Re-run `python3 build_data.py` before believing any count**, and
expect the pattern total to move while you work. The report is built to degrade
here and does; what it must not do is *state* a stale number, which is why
`content.js` prose should never name a gate verdict — p23's caveat did, and was
false within the hour.

### The pipeline, and the order it must run in

```bash
python3 build_data.py                 # evidence -> data/   (~1 s)
python3 insights/asm_extract.py       # binaries -> asmcache/   (~3 min) — needs ../.temp/build
python3 insights/asm_map.py           # + source lines via debug twins (~10 min)
python3 build_data.py                 # again: publishes asmcache -> data/asm with digest checks
```

⚠ **`asm_extract.py` rewrites `asmcache/` and DROPS the maps**, so `asm_map.py`
must follow it. Both need the parent's `../.temp/build` binaries; they are 1.7 GB
of scratch and may be gone, in which case the committed cache still serves and
the digest check says whether it is still valid.

✅ **Both take a pattern filter, and that is the cheap path when one pattern
lands.** `python3 insights/asm_extract.py p23-partition` then
`python3 insights/asm_map.py p23-partition` took about a minute together, and
**only that pattern's maps were dropped** — the other 24 kept theirs, verified
leaf by leaf. The whole-corpus warning above is about the *unfiltered* run.

### Traps this session added — every one cost real time

- ⚠⚠ **A link that lights ONE of two panes is not half-working, it is evidence
  the coordinates disagree.** See the pane/line-map section below. My own test
  selected a line that existed in the file but not in the pane, so the assembly
  lit and the source did not, and I recorded that as success for several commits.
- **Columns only line up if they are tracks of the SAME grid.** A per-row grid
  with `min-width: max-content` sizes each row to its own content and the split
  lands somewhere different on every line. Guarded now.
- **Two rules painting the same edge at equal specificity**: whichever comes last
  wins silently. `.sel` against the confidence classes; they now carry both.
- **Prose between two panes is height stolen from the panes.** ~700 characters
  sat between source and assembly and made the linked view pointless. Folded.
- **Refusing beats guessing only when the guess is bad.** All-or-nothing twin
  refusal threw away 97-99% good data; grading recovered all 328 diffs with 0.8%
  at the weakest tier. But **positional pairing** in the alignment was genuine
  noise and was dropped. The difference is whether the signal survives being
  labelled honestly.
- **A check that never runs a code path proves nothing about it.** `check.mjs`
  had never opened the notes fold, rendered a narrow viewport, or set a
  selection — three views nothing had ever exercised.
- ⚠⚠ **Markup for evidence the corpus does not contain is dead on arrival, and
  it dies again.** The gate-failure callout was live for about two hours: p23
  arrived `FAIL` and was fixed upstream the same afternoon. `verus_exit_anomalies`
  has never been non-empty. Both now have **must-fire probes** in `check.mjs`
  that inject the evidence, assert the page says so, and assert it goes away
  again — and both were verified to fail by disabling the branch.
- **A stray `**` renders as punctuation and throws nothing.** Splitting one
  sentence between `content.js` and `index.js` put the opening marker on one
  side of the seam and the closing marker on the other. Swept now, over every
  tab and every pattern write-up, excluding `<pre>` where upstream markdown is
  content rather than ours to judge.
- **A percentage out of range is invisible to a render check AND to a
  stylesheet** — the mark simply leaves the track, exactly as the dumbbell's
  negative-width bar did at 360px. The spread chart's 12 bands and 186 ticks
  are checked arithmetically.
- ⚠⚠ **THE OVERFLOW AUDIT PASSED ON A CARD THAT WAS UNREADABLE.** The ladder
  strip's rows had **five children and two columns** at phone width, and
  `grid-row: 1 / -1` on the rail **collapsed** because the row declared no
  `grid-template-rows` — `-1` resolves against the *explicit* grid. The freed
  cells then auto-flowed `.lv-what` and `.lv-tcb` into the **4px rail column**,
  one word per line, overlapping the cell beside them. Nothing overflowed, the
  tree was perfect, every token round-tripped, and **only the user's phone
  screenshot found it.** `LESSONS.md` #14; the audit now simulates auto-flow
  and fails when a child lands in a fixed track of ≤24px.

## How it is wired

```
../results/*.json ─┐
../results/gate/*.json ─┤  build_data.py  →  data/index.json      (+ index.boot.js)
../patterns/*/     ─┘     (the only writer)   data/patterns/<id>.json
                                              data/code/<id>.json
                                              data/docs/<id>.json
                                                        ↓
                          index.html → common.js → content.js → data/index.boot.js → index.js
```

- `data/index.boot.js` puts the summary in scope at parse time, so the page opens
  with data rather than a loading flash; the per-pattern files are fetched lazily
  and cached. A missing `boot.js` falls back to fetching `index.json`.
- `index.stdio.py` is optional. `status` reports whether `data/` is older than the
  evidence; `rebuild` re-runs `build_data.py`; `doc` reads one upstream text file.
  The footer's **check / rebuild** button uses them and degrades to a toast when
  there is no backend.

## The views

| tab | what it answers |
|---|---|
| Overview | the thesis, the hero figure, the KPI row, the ladder strip, three headline results, provenance |
| The ladder | what each of the six rungs buys, costs and leaves trusted · one profile per pattern |
| Cost of safety | R3 vs R4 diverging bars · the R2↔R3 spelling gap · what the same check costs inside C · the full delta table |
| Hostile input | the outcome matrix, per-run detail, ASan/UBSan and Miri, and the cases where "memory-safe" is the wrong question |
| Proof & trusted base | obligations, trusted items and lines, twins, clause-deletion and tautology probes, byte-identity |
| Patterns | per pattern: narrative, contract, profile, inputs, adversarial table, wall clock, each rung's source, gate record, its own README/spec/NOTES |
| Findings | the cross-cutting results with `standing` / `corrected` status, and the full retraction list |
| Method | what a cell is, the two Ir columns, wall clock, what the gate checks, what this benchmark cannot tell you, the traps, provenance |

## The decisions, and why

1. **Numbers are generated; claims are hand-written.** Everything numeric comes
   from `data/`; every sentence about what a number *means* lives in
   `content.js`, attributed. The parent project's history is full of correct
   numbers under wrong sentences — keeping them in separate files means a
   rebuild can never quietly change a claim, and a claim can never quietly
   outlive its number.
2. **Claims that the data can settle are derived, not written.** The
   "every deviation is in an R1 cell" sentence, the identity count, the pattern
   and catalogue counts are all computed at render time. Each of them had
   already gone stale once as a constant.
3. **Colour is the rung.** Four base hues — gcc cyan, clang blue, safe amber,
   unsafe red — and each pair is that base at two strengths: **washed** (the
   base under white glass, keeping 62%) for the plain rung, **solid** for its
   hardened, tuned or proven twin. So R5 is solid red beside R4's washed red
   because it *is* R4 plus a proof. In the diverging cost chart the bar takes
   the colour of whichever rung the excess belongs to, so red never means two
   things. The validator report and the three deliberate deviations are in the
   comment block at the top of `index.css`; `tools/validate_palette.js` is vendored
   here so that report stays re-runnable without the skill that produced it.
4. **Profile charts are horizontal.** The rung names are the thing being
   compared; as tick labels they collided, as row labels they read. It also lets
   colour reinforce identity rather than carry it, which is what makes a washed
   member legal.
5. **The legend is the control.** Click a key to drop a rung from every profile
   and from the cost table; five presets, of which **Same backend** (C clang, C
   clang hardened, R3, R5) is the comparison with no backend difference in it.
   The selection is one shared piece of state, persisted, and hiding a rung
   never repaints the others.
6. **Every chart has a table twin, a direct label and a tooltip.** Three
   light-mode rung colours sit under 3:1 by construction; this is the relief
   that makes that acceptable rather than a defect.
7. **Corrections are shown, not folded in.** Findings carry `standing` or
   `corrected`, the retraction list ships in full, and each pattern page has a
   "The correction" callout. The project's own epistemics are part of what the
   report is for.

## Corrections this report has already had to make

- **"The verified binary is byte-identical to the unverified one"** — true for 22
  patterns and false on **p36**, where a `spec fn` declared in a trait takes a
  vtable slot in the erased build (64 B of `.data.rel.ro` + a 26-byte stub), so
  one `lea` displacement moves. Now stated as **zero executed instructions**
  everywhere, byte-identity as a derived count, and finding 1 is labelled
  `corrected` with the scope clause. Four places restated the old wording; all
  four are fixed.
- **Hard-coded counts.** "13 patterns", "47 catalogued", "Four cases where…" —
  all replaced by derived values or by counting the source (`catalogue_total()`
  reads `../.memory/06-catalogue.md`).
- **The TCB census** ("2 of 58 trusted items could be discharged") is now dated
  to the 14 patterns it was measured on rather than presented as current.
- **A per-pattern claim that outlived its measurement**: the pattern pages'
  `convention` line exists because p03, p11 and p13 disagree about which `Ir`
  column is authoritative. Do not add a cross-pattern cost comparison without it.

## The traps

1. **The gate's schema moves.** The adversarial record changed from one entry per
   (input, rung) to a **list of behaviour groups** naming the builds that produced
   each, and grew `hung` / `diverges` / `expected_hang` / `run_timeout_s`. The
   build crashed. `build_data.py` now knows its expected key set and its rung set
   and warns on anything else — **read the warnings, they are the early signal
   that this report is behind the repo**.
2. **A new rung id would be silently dropped** from every chart, because
   `RUNGS` in `build_data.py` is the ladder. That case now warns too.
3. **A green render check says nothing about CSS.** Deleting a CSS block by line
   range removed the `.sw-*` swatches and left every bar transparent; the check
   passed. Screenshot after CSS edits.
4. **Screenshots race the lazy fetches.** A live screenshot catches "Loading…".
   Use `--snap`, which freezes fully-populated static renders into `.temp/`, and
   open those over `file://` — the server does not serve dot-directories.
5. **Headless Firefox needs a warm profile.** The first invocation against a
   fresh `--profile` directory times out; run it once at `about:blank`, then
   take the real screenshot. `--screenshot` needs an **absolute** path. The
   recipe that works on this box, from inside `.web/`:

   ```bash
   FF=~/.cache/ms-playwright/firefox-1522/firefox/firefox
   node check.mjs --snap
   mkdir -p .temp/ffprof
   MOZ_HEADLESS=1 timeout 45  $FF --headless --profile $PWD/.temp/ffprof \
       --screenshot $PWD/.temp/warm.png about:blank            # warm-up, may time out
   MOZ_HEADLESS=1 timeout 90  $FF --headless --profile $PWD/.temp/ffprof \
       --screenshot $PWD/.temp/shot.png --window-size=1440,1500 \
       file://$PWD/.temp/snap-patterns.html
   ```

   For dark mode, `sed 's/<html lang="en">/<html lang="en" data-theme="dark">/'`
   the snapshot first. Delete `.temp/ffprof` and the PNGs when you are done.
6. **Not every pattern has every rung.** p01 has no hardened-C rung and does have
   the R2v control. Anything that assumes eight cells is wrong.
7. **Status colours are reserved.** good / silent+wrong / never-returned /
   crashed belong to the outcome matrix. Do not spend them on a rung, and do not
   give a rung a green.
8. **`content.js` is prose *including its numbers*.** A figure quoted there is a
   claim with a source, not a live value — if you change one, re-check it against
   the pattern's `NOTES.md` rather than against the chart.

## Owed, roughly in order

1. **Prose for new patterns.** Each pattern wants a `PATTERNS` entry and a
   `SHORT` label in `content.js`. Without one the page still renders every chart
   and table and says plainly that no write-up exists — but the fallback should
   not become the norm. Written from the pattern's own `README.md` plus its row
   in `../RECAP.md`'s pattern table.
2. **The findings feed is hand-curated — and it stays that way. DECIDED, with
   the measurement.** The question was whether per-pattern findings should be
   rendered from `../.memory/01-ladder.md` instead of retyped. They should not:

   - The file has **28 numbered finding blocks for 25 patterns**, and their
     headlines are not a uniform shape.
   - Requiring the headline to *begin* with the pattern id covers **20 of 25**.
     The five it misses are **p01, p02, p19, p23, p46** — and p19/p46 are the
     two the parent's own RECAP records as having been absent from the findings
     layer for 45 and 35 tasks. Deriving would silently reproduce that gap.
   - Relaxing to "the id appears anywhere in the headline" gains **one**
     pattern and immediately **misattributes**: p27 picks up finding 2, whose
     headline merely mentions p27 in passing.

   A wrong attribution of someone else's research finding is worse than a
   hand-written summary that says who wrote it. Re-run the numbers before
   revisiting — the extraction probe is three lines of `re.finditer` over
   `^\d+\.\s+\*\*`.
3. ~~**The layout effect has committed data and no chart.**~~ **Done** — see
   "Landed since the handover". `../common/layout/data/layout_p01.json` is now
   derived in `build_data.py::layout_effect()` and drawn by `chartSpread`.
4. **Wall clock lives only on pattern pages.** There is no cross-pattern view,
   deliberately — but the per-pattern caveat about levels-not-differences could
   be stated once in Method and linked. ⚠ **Partly addressed**: the layout
   section on Cost now makes the "a single wall-clock number has no sign"
   argument once, with the data. Method still repeats the caveat in prose.
5. **Unsurfaced evidence**: the sanitizer section's `declared_hang` / `hung`
   columns, Miri's `trusted_items`, and the per-spelling rows of the idiom audit
   are all in `data/` and shown only as counts.
6. ~~**Narrow viewports are unverified** below ~1180px.~~ **Done.** Four
   breakpoints now exist (900 / 720 / 560 / 400) and
   `node tools/responsive_audit.mjs` checks the arithmetic half at seven
   viewports down to 320px. What was wrong: the whole stylesheet had **two**
   layout media queries, every `auto-fit` grid overflowed once the viewport
   dropped under its track minimum, and the dumbbell chart's fixed label and
   value columns left the bar **negative** width at 360px. ⚠ **Still owed: the
   visual pass.** The audit proves no grid overflows; it cannot tell you the
   result reads well, and headless Firefox would not complete a capture on this
   box (see trap 5 — the warm-profile recipe did not help).
7. **`data/docs/` is ~2 MB of verbatim notes.** Fine locally; revisit if this is
   ever published anywhere that pays for bytes.

## Script-guarded notes — the mechanism, and why it exists

Any prose here that makes a claim about the research tree is one upstream task
away from being false, and this project's own history is mostly a record of
exactly that happening. So diff notes are not strings in `content.js`: they live
in `insights/insight_*.py` **attached to assertions about the evidence**, and are
emitted only while every assertion holds.

- A failing guard **withholds the note** and exits non-zero.
- `build_data.py` runs every `insights/insight_*.py` on each rebuild and turns a
  non-zero exit into a `WARNINGS` entry, which the Method tab renders.
- So a stale claim disappears from the page and announces itself, instead of
  staying confidently wrong.

`python3 insights/insight_codediff.py --print` prints each note's verdict with
the evidence behind it, which doubles as a statement of what is currently
believed.

⚠ **Guard against `results/`, `results/gate/` or the pattern's own source.**
A guard that reads a number out of `.web/data/` is circular — `build_data.py`
derived that number from the same place the note did, so the assertion cannot
fail for the reason you want it to.

**Two things it caught immediately**, which is the case for the mechanism. The
"every line here compiles to nothing" note on the R4→R5 diff is broadcast to all
patterns and **declined to apply to p36** — whose R4/R5 kernels are `norel`, not
byte-identical — with nobody having encoded that exception. And a deliberately
false probe note, asserting p01's safe and unsafe kernels were the same, was
withheld and reported rather than published.

## The source-to-assembly link — BUILT, and what it refuses to claim

`insights/asm_map.py` attaches a source line to each instruction. Read its
header before changing it; the short version, and the numbers as measured:

- **The measured binaries carry no line info for this project's code.** So the
  line table comes from a throwaway `-g` twin, and a twin is believed only when
  it is provably the same code — same `n_fn`, identical normalised instruction
  text, matching `md5_fn_norel`. C matches on `md5_fn` outright; Rust and Verus
  match on `norel`, because a debug build relocates.
- **Every line carries a confidence, and all 328 diffs now map.** The first
  design refused a pair outright whenever the twin's instruction stream differed
  at all, and that was wrong by a wide margin: the **worst** such case still
  aligned **97%** of its measured instructions into equal runs, so refusal threw
  away nearly everything to avoid being wrong about nearly nothing. The twin is
  now aligned against the measured kernel instruction by instruction and graded
  `certain` / `likely` / `approximate` — see `align()`.
  Measured over the corpus: **30,237 certain · 16,873 likely · 389 approximate**
  (0.8%), across **224 exact-twin and 104 partial-twin** diffs. What is still
  refused is a twin sharing under half the instruction stream: a different
  program, not a variant.
- ⚠ `-g` **is codegen-neutral for C and not for Rust.** Every C cell has an
  identical `md5_fn` with and without it; Rust at `-O0` changes outright (271
  instructions against 415 on p27's verus rung) and even `-O3` can shift a
  register. That is why the grading exists rather than an assumption.
- ⚠ **Coverage is partial and the page says so per view.** Across the corpus
  **47,499 of 54,941 instructions (86%) carry their own source line** and 7,442
  come from inlined library code. The link hint prints the real counts for
  whatever is on screen, because a reader clicking an instruction that has no
  line deserves to know why nothing happened.
- Selection is **per side**. A diff has two sources and two kernels, and A's
  line 49 has nothing to do with B's line 49, so `map.al` / `map.bl` hold each
  instruction's line on each side and a context instruction answers to both.

## ⚠ THE PANE AND THE LINE MAP MUST BE IN THE SAME COORDINATES

The line map is in **FILE** coordinates — `addr2line` reads the whole file. But
`build_data.py` **slices** every Rust rung (the driver banner onwards is
dropped), so the pane used to number its lines from 1. p03's `unsafe.rs` starts
at **file line 54**, so clicking any Rust line sent a number that could never
match and nothing happened. C was unaffected — its slice offset is 0 — so the
feature looked like it worked.

Nothing threw, so no render check could see it, and a test that selected a line
present in the *file* but not in the *pane* lit the assembly and not the source,
which read as success. Every code cell now carries `first_line` and every pane
numbers in file coordinates. `check.mjs` compares the two per cell-view (656 of
them) and fails if a whole map falls outside its pane.

## Aligning two sources THROUGH the assembly

The cross-language tab has no source diff — C and Rust are not the same
language — but the compiled kernels can be read backwards into one. When an
instruction is **identical on both sides** (a context op in the assembly diff)
and carries a source line on each, those two lines produced the same
instruction and are related. Selecting a line lights the other side's.

⚠ **It is sparse, and that is the data rather than the implementation.** On
p03's hardened-C-against-unsafe-Rust, **5 of 112 instructions are shared**,
giving exactly 3 line pairs: C 52↔Rust 65, 54↔68, 77↔96. Two compilers rarely
emit the same sequence. A line with no correspondence says so and names the
lines that do have one, so it is a signpost rather than a dead end.

**The two sources are also LAID OUT by those anchors** — padded so that lines
sharing an instruction sit on the same row, with the anchor rows marked `⇔`.
On p03 that pairs C's `if (nops == 0)` with Rust's `if nops == 0 {` and C's
`if (5 * (uint64_t)nops > …)` with Rust's `if 5 * (nops as u64) > …`:
semantically equivalent statements across two languages, found through the
machine code with no source-level heuristic at all. Crossing anchors are dropped
by a longest-increasing-subsequence pass, because they cannot be laid out in
order.

⚠ **The alignment counts only `certain` and `likely` instructions.** An
approximate line is a positional guess, and two guesses do not make a
correspondence.

⚠⚠ **Positional pairing was tried and DROPPED.** Pairing deletion *i* with
insertion *i* inside a change block yields a correspondence for almost every
line, and it means nothing — the pairing is an artefact of the diff algorithm,
not of the code. It would have been noise wearing the colour of evidence, which
is this project's most familiar failure. Only shared instructions count.

## Owed (was: the source-to-assembly link)

Part B of the compiler-explorer idea, investigated and not built. What is
already settled, so nobody re-derives it:

- **The measured binaries have no line info for this project's code.**
  `safe_tuned.rs` appears in **0 rows** of the DWARF line table and the C kernel
  resolves to `??:?`; the `.debug_line` that is there belongs to the
  pre-compiled stdlib. `harness/build.py` passes no `-g`.
- **A debug twin is provably the same code**, which is what makes a mapping
  trustworthy. Rebuilt with `-g` / `-C debuginfo=2`: C matches `md5_fn`
  outright; Rust and Verus match `md5_fn_norel` with **byte-identical
  normalised text** and equal `n_fn` (82==82, 66==66). So instruction *N* in the
  twin is instruction *N* in the measured kernel, and the guard is asm.py's own
  `norel` level. Verus compiles fine with debuginfo (`9 verified, 0 errors`).
- ⚠ **The mapping is partial at `-O3` and must be shown as such.** Measured on
  p03's 82 instructions: **60** map to `safe_tuned.rs` (**9 of those with no
  line**), **22** to *inlined stdlib*, 0 to nothing — so about **62%** get a
  real source line. Scheduling also makes a line's instructions non-contiguous,
  so a line maps to a *set* of ranges, not one.
- **The diff complicates it**: both panes are diffs, so linking must be
  per-side (A-side line to A-side instruction). The row data already carries
  which side it came from and its true line number.
- Twins belong in `.temp/` and get deleted; only the *mapping* would be
  committed. Time the build sweep on one pattern first — Verus re-verifies on
  every compile and may dominate.

## Verification checklist

Run all of these before believing anything. Each was added because something got
past the ones before it.

```bash
python3 build_data.py            # no `!` lines (a stale guarded note shows here)
node check.mjs                   # OK; prints the line-map, spread-chart and must-fire results
node tools/check_syntax.mjs      # every token stream reconstructs its source
node tools/responsive_audit.mjs  # exit 0: no overflow, header sane, split grid aligned
python3 insights/asm_extract.py --verify        # 0 digest mismatches against results/
python3 insights/insight_codediff.py --print    # what each guarded note claims, and why
python3 insights/insight_asmdiff.py --print
git -C .. status --porcelain | grep '\.web'    # must be EMPTY
```

Plus the two that live only in a shell one-liner, both of which have caught real
bugs: **every class the page emits must have a CSS rule** (dead markup means a
hook nothing styles), and **braces must balance**. Both are in the commit
messages if you need to retype them.

⚠ **And then look at it.** Every check above is structural. None of them can see
whether the page is legible. `node check.mjs --snap` then open
**`.temp/snap-index.html`** over `file://` — every view, both themes, five
widths, one file. That is the whole visual pass and it is the one thing here a
human has to do.

## Verification checklist (original)

- `python3 build_data.py` → no `!` warning lines (a stale guarded note shows up here).
- `node tools/check_syntax.mjs` → every token stream reconstructs its source.
- `node tools/responsive_audit.mjs` → exit 0.
- `node check.mjs` → `OK`, and the tree/node counts should not
  collapse (a suspiciously small tab fails the check by itself).
- Screenshot the tab you touched; screenshot both themes if you touched colour.
- `git -C .. status --porcelain` → unchanged by anything you ran.
- Then commit here.
