# REWRITE_VERC_PLAN — build `paper_vers/ver_C`

**Written to be executed cold, after the conversation that produced it is gone.**
Everything needed is here or named by path. Resume with: *"resume from
REWRITE_VERC_PLAN.md and systematically proceed with the next version of the
research report."*

Read order on resume: **this file → `.temp/verify/FACTS.md` (verified numbers +
DO-NOT-CLAIM) → `.temp/verify/RULINGS.md` (evidence settlements) →
`.temp/thesis/CANDIDATES.md` → `.temp/refstudy/*.md` → `paper_vers/README.md`.**
⚠ Everything under `.temp/` is gitignored scratch and **may be gone**. §9 lists
what must be re-derived if so, and §11 says how.

---

## 0. THE ONE-LINE BRIEF

ver_A had a thesis nobody could read. ver_B is readable and has no thesis — the
owner's verdict: **"Easier to understand but no central theme now."** ver_C keeps
ver_B's readability and adds the argument its own framing statement explicitly
disclaimed.

**Do not start from scratch.** ver_B is accurate, fact-checked and passed its
acceptance test. ver_C is a *re-argument* of largely the same evidence, plus the
material §3 says ver_B under-uses.

---

## 1. WHY ver_B HAS NO THEME — three mechanical signatures, three mechanical fixes

Diagnosed from the artefact, not from taste. Each fix is checkable.

| signature | evidence | fix, and it is a gate |
|---|---|---|
| **Section titles are containers, not claims.** | 6 of 7: *"What safety costs"*, *"The argument in the room"*, *"What this cannot tell you"*. Only *"Proved is not done"* asserts anything. | **Every section title states a claim the section proves.** If it cannot be written as a claim, the section is a container: merge or cut it. |
| **The summary is 8 independent items.** | ver_B's own spec said *"No item may depend on a later item"* — which guarantees a list, not an argument. | **At least three summary items must depend on the one before**, and the list carries a one-sentence **hinge** that turns it (§7.3). |
| **It was built themeless on purpose.** | `ver_B/meta.json`: *"ver_B argues nothing about safety in the abstract."* | **The framing statement must name a belief the paper refutes**, and the refutation must be measured. |

A fourth, from the reference study (§7): ver_B's **proportions are wrong**.

| | reference papers | ver_B | **ver_C target** |
|---|---|---|---|
| findings | 42–44% | 67% | 45–50% |
| limitations | **1–3%** | **17%** | **≤6%** |
| implications / what to do | 6–27% | ~4% | **15–20%** |

ver_B spends six times the published norm on what it cannot tell you and a
quarter of the norm on what to do. **That trade is the theme problem in another
unit.** Limitations do not disappear — they move next to the claims they bound
(§7.6), which is where the in-house draft puts them anyway.

---

## 2. THE THESIS

### 2.1 The sentence

> **A safety claim is an attribution claim, and this corpus shows both halves are
> routinely misattributed: the cost you measure is usually not the check, and the
> coverage you assume is usually the allocation.**

### 2.2 The two halves, each independently carried

**Half A — cost.** *When safe Rust costs you, it is usually not the bounds check.
Delete the mechanism and re-measure, or you are quoting a number about something
else.*

Of the **10 licensed safe-tuned-minus-unsafe rows above 100 `Ir`/call**, the
bounds check is the named dominant term on **2** (binary search, bitset). On
**7** it is explicitly something else — iterator-adaptor exhaustion tests, the
unsafe rung's missing reslice, a single mask instruction, a foreclosed unroll,
data shape plus spelling, a constant-time discipline, a hoisted trip count. On
the 8th it *is* the check, and one provably dead line deletes 100% of it.

⚠⚠ **The count `2 of 10` is DERIVED, not quoted, and the evidence agent must
re-derive it before a word is written.** `results/SYNTHESIS.md` carries the
per-row attributions — the table around *"what the delta actually is"* gives
*"none of it is a bounds check — `zip`/`Rev` adaptor exhaustion tests"*, *"the
unsafe rung's missing reslice"*, *"a hoisted per-row trip count"*, *"R4's
foreclosed unroll"*, and elsewhere *"100% an unroll decision and 0% a check"* —
but **no sentence in the tree states the 2-of-10 tally.** Rebuild it row by row
from the licensed rows in `results/synthesis.md` §1 plus those attributions, and
**if the tally comes out differently, the thesis takes the new number** — its
force does not depend on the exact ratio, only on the check being a minority.
This is precisely the shape of claim this project has got wrong before by
trusting a summary over the rows.

Six further parameter-free decompositions land the same way — a handle table's
`230.07 = 109.65 kernel + 120.42 drop glue + 0.00 allocator`, a NUL scan's
12.0× library / 5.3× spelling split, a buffer copy whose indexed fold's checks
cost zero and whose delta was a lost `memcpy` idiom.

And it was caught **prospectively**: a refused row would have published *"safe
Rust is 6.02× cheaper"* with **108.4% of the gap in the allocator** and the check
at 3.0% of the magnitude, **opposite sign**.

**Half B — coverage.** *Four detectors, one blind spot: a bounds check, a
sanitizer, an interpreter and a memory-safety proof return the same verdict on
five of six bug classes, because they all range over the allocation.*

Carried by the coverage table (**no cell reads "silent, and it should have seen
this"**), the one-character bitset index, the provably-memory-safe range-parser
leak, the constant-time compare, and the recycle probe. Two facts make stacking
detectors worse rather than better: fortification blinds the sanitizer, and the
sanitizer's redzones **destroy object adjacency**, so a provenance harm is
unobservable under it in principle.

### 2.3 Why the two halves are one paper

Both are **attribution**. You cannot attribute a cost to a mechanism without
removing the mechanism and re-measuring; you cannot attribute a guarantee to a
mechanism without naming the resource it ranges over. **The corpus's instrument —
a controlled ladder of *spellings* of one kernel, with the proved rung pinned
byte-identical to the unproved one — is what makes either attribution possible.**
That instrument is the methodological contribution and it is why this evidence
exists nowhere else.

### 2.4 ⚠ The framing correction that decides the paper

The thesis agent's axis count over the corpus's genuinely surprising findings:
**verification 8 · measurement 9 · mechanism 5 · C-and-Rust 6.**

**A ver_C framed as "what does a Rust rewrite cost" is framed against its own
evidence.** ver_B was framed exactly that way. ver_C is a paper about
**attribution and measurement**, in which C and Rust are the instrument, not the
subject — and which is *therefore* useful to someone deciding on a rewrite,
because it tells them the number they were handed is probably about something
else and how to get one that is not.

Do not let this drift back. It is the single most likely regression.

### 2.5 The abstraction, finally placed

ver_A's four coordinates failed as a framework. ver_B cut them to three
(**property · bearer · resource**) and earned them after three failures. **ver_C
does not need the vocabulary at all in Half A**, and in Half B needs exactly one
word: **resource**. Half B's headline — *they all range over the allocation* — is
the entire abstraction, stated as a measured finding about four named tools.
**If a draft reintroduces "bearer" or "residual" as coined nouns, cut them.**

---

## 3. WHAT ver_C USES THAT ver_B UNDER-USES

ver_B is accurate but spends its evidence on the wrong axis. These are in the
tree, verified, and mostly absent from ver_B:

1. **The decomposition table.** Ten large rows, each attributed to a named term.
   This is Half A's spine and ver_B has fragments of it in prose.
2. **The prospective catches** (the 6.02× row with 108.4% in the allocator;
   another 9.6× that was 100% spelling). ver_B has neither. **A method that
   caught an error before publication is worth more than one that explains an
   error afterwards** — this is the strongest evidence in the corpus that the
   method works.
3. **The coverage table's negative space** — that no cell reads *"silent, and it
   should have seen this."* ver_B prints the table and never says the thing that
   makes it a finding.
4. **The sanitizer-redzone provenance argument.** Absent from ver_B.
5. **The positioning against the closest related work** (§4).

---

## 4. POSITION — the conversation ver_C joins

The closest related work is **`ref_papers/UserStudy.pdf`** — *Translating C To
Rust: Lessons from a User Study*, NDSS 2025 — same topic, and by the look of the
author list, adjacent to this project's own authors. `ref_papers/TaxDC.pdf` and
`ref_papers/SKEL.pdf` are the structural models (§7).

**The gap sentence. Lead with the methodological one:**

> To the best of our knowledge, no prior study measures the cost of memory safety
> as a controlled difference between **spellings of the same kernel**. Existing
> evidence compares one C program against one Rust program — a human
> translation, a tool's output, or an instrumented binary — and therefore cannot
> separate what safety costs from what the rewrite happened to change.

The substantive gap (*no study asks what a memory-safe rewrite does not buy on
the program it made safe*) is **what that design produced**, not a second
standalone claim. The verification gap is a clause inside it, never a universal.

**How to relate to the user study — this is a correctness requirement, not
diplomacy.** Their framed finding reads, verbatim:

> "All the known memory safety vulnerabilities in C programs are eliminated in
> the translated Rust code."

⚠ **It is scoped to the *known* vulnerabilities in their eight benchmark
programs, and it is true as scoped.** An earlier agent paraphrased it as a
universal ("in each one of the Rust translations") and that paraphrase is wrong.
**Write the relationship as COMPLICATION, never contradiction:** the residual
class our range parser exhibits — *the bytes folded into the answer are the bytes
the request named* — is functional, so it was never on a memory-safety
vulnerability list; and **their own §VI already found this class and filed it as
a correctness gap.** Their data is consistent with our conclusion; their framing
is not. That is the whole claim, and it is enough.

⚠⚠ **Quote published papers from the PDF via `Read` with `pages`.** The extracted
text in `ref_papers/.temp/` **interleaves the two columns** and will corrupt any
quote. Verify every quotation against the rendered page.

**Where we agree, and say so first:** their central mechanism — that Rust moves
the expensive half of temporal safety to compile time — we confirm by
*instruction accounting* rather than by counting declarations: a handle table's
allocator term is **0.00 `Ir`/call**, with `malloc`, `free` and all three Rust
allocator shims equal to the last digit between rungs.

**The counterweight, and it must be in the paper:** every rung above plain C —
hardened C included — matched the model on all **4,104** adversarial runs, and
two bug classes are safety wins with **no cost axis at all** (an overlapping
`memcpy` is inexpressible in safe Rust; strict aliasing is not reintroduced at
any Rust rung). **An instruction-count study systematically under-credits safety,
this one included.**

---

## 5. WHO IT IS FOR

Unchanged from ver_B, plus one: **a working developer or tech lead with a C/C++
codebase being asked whether to rewrite part of it in Rust**, *and* **a
researcher or tool author who publishes safety-cost numbers.** The second reader
is new and is the one the thesis is aimed at; the first is the one who must still
be able to read it.

Undergraduate-readable. No prior Verus, formal methods, or knowledge of this
project. ⚠ The report is **hash-routed** — readers land at
`#patterns/p17-http-range` having never read §1 — so §7.9 applies.

---

## 6. THE RUNNING EXAMPLE — one artefact, redrawn

SKEL runs eight pages of design on **one** 21-line program redrawn as five views
and introduces **zero** new examples. ver_B cites ~10 patterns and the reader
carries none. **ver_C runs its spine on the TLV walker (`p16-tlv-walk`)**, which
carries the whole ladder by itself.

Verified from `results/synthesis.md` §1 (kernel-exclusive `Ir`/call, `-O3
isolated`; ⚠ **re-derive before writing**, upstream moves):

| rung | small | large | derived |
|---|---:|---:|---|
| plain C (**carries the bug**) | 4062 | 32694 | — |
| hardened C, gcc | 4079 | 32735 | **+17 / +41** |
| plain C, clang | 2993 | 23761 | — |
| hardened C, clang | 3017 | 23815 | **+24 / +54** |
| **safe Rust, naive** | 5095 | 40921 | **+2085 / +17123 vs unsafe → +69% / +72%** |
| **safe Rust, tuned** | 3037 | 23875 | **+27 / +77 vs unsafe → +0.9% / +0.3%** |
| unsafe Rust | 3010 | 23798 | — |
| proved | 3010 | 23798 | **identical to unsafe** |

**On one pattern, the same safety guarantee costs +0.3% or +72% depending only on
how the safe rung is written.** That is Half A in one artefact the reader already
knows.

The same pattern also carries **the four-rung deleted-line experiment** — delete
`if vlen > end - (p + 3) { break; }` from each rung: plain C → SIGSEGV silent;
unsafe Rust → SIGSEGV, *identical to C*; safe Rust → `exit 101`, `index out of
bounds: the len is 3072 but the index is 3072`; proved rung → **will not build**.
**And all four still print the correct checksum on the well-formed inputs.**

⚠ Provenance, mandatory every time: the C row is the shipped rung and
gate-certified; **the three Rust rows are `.temp/` scratch with no committed
generator and do not survive a clone.**

**Second example, used only where Half B needs a failure the walker cannot
show:** the bitset one-character index (`>> 6` → `>> 7`). Keep the corpus's other
patterns as *rows in tables*, not as narrated examples.

---

## 7. WORKING CONVENTIONS

Extracted from TaxDC (ASPLOS'16), the NDSS'25 user study, SKEL (PLDI'25) and the
in-house draft at `ref_papers/.temp/m/DRAFT_*.txt`. Full analyses:
`.temp/refstudy/EMPIRICAL.md`, `CONCEPT.md`, `HOUSE.md`.

### 7.1 Open on one instance that already contains the thesis
Numbers in sentence one, no framing before them. The in-house model:

> "C2SaferRust rewrote `sd_markdown_free`, one function of the `snudown` Markdown
> library, and all five counters this field publishes fell: 1/10/22/13/21 →
> 0/2/4/4/4."

Select the instance for five properties: **it has a control; the difference is
minimal and nameable; the metric and the truth point opposite ways; the mechanism
is explained at source level in one sentence; and it is real, not constructed.**
⚠ Buy **one** orientation sentence *after* the numbers — ver_A died of a
zero-onramp opening and our audience is wider than that draft's.

### 7.2 State the rubric before you have a candidate, then score prior work on it
SKEL names three requirements in intro ¶2 and in ¶3 uses them to grade LLM
translation. Requirements stated *after* the idea read as reverse-engineered.

### 7.3 Findings list on page one, split by a one-sentence hinge
TaxDC: 8 bullets, ~380 words, 22–61 words each. Bullets 1–4 are why the problem
is hard; 5–8 why it is tractable; the hinge between them is *"Nevertheless,
through a careful and detailed study of each bug, our results also bring fresh
and positive insights:"* **The hinge is what turns a list into an argument** —
this is the direct fix for ver_B's front page.

### 7.4 End a finding with what it motivates, number it, and cite it later
Anatomy: `[quantified claim] + [mechanism clause] + [this motivates …]`. TaxDC
numbers findings #1–#6 and cites them 20+ times like references. ⚠ **Withhold the
motivates clause from the bad-news bullets** — that is what keeps it from
sounding like salesmanship.

### 7.5 Promote each subsection's conclusion into a framed box where its evidence lands
The user study has exactly 10, one per subsection, 1–4 sentences, shaped
`[scope] + [claim] + [number]`, **with no implication** (those are deferred to
one section). We already have a `takeaway` environment; use it this way.

### 7.6 File every limit beside the claim it limits, and say that you are doing so
In-house: *"The same census carries counter-evidence, and it belongs here rather
than in a threats list."* Reserve a threats section for the instrument critique
and the withdrawn claims only. **This is how §1's proportion fix is achieved
without losing a single caveat.**

### 7.7 Number discipline
- **Route every percentage to a named exhibit.** TaxDC never states a bare
  percentage: *"faults (63% in Figure 3b)"*.
- **Use `N of M` while M is memorable**; switch to percentages only once a large
  base is named.
- **Put the counting rule within eye-range of the number** — in the caption or a
  footnote bolted to the figure, never in a distant methodology paragraph.
  Model: *"The total is more than 104 because some bugs require more than one
  triggering condition."*
- **Give every headline number more than one denominator and reason from the
  smaller one.**
- **Report a changed number by carrying both, earlier first**, when the earlier
  one ran against you.
- **Lead with your weaker number.** SKEL headlines *"4 out of 9 real-world
  programs"*; the flattering 95% arrives one sentence later at a different
  granularity.

### 7.8 Honesty conventions — the source of this voice's authority
- **Ship a withdrawn-claims table**: *the claim, and it was ours | what killed it
  | what stands instead*. ver_B's §6 becomes this.
- **Name the sentence you will not write.** *"One sentence is therefore licensed
  … another is forbidden … and we do not write it."*
- **Price every refusal**: *"each refusal costs us something we would have liked
  to offer."*
- **Defend the opponent where the evidence defends them.**
- **Admit, then bound the admission with a falsifiable symptom** — not "but it
  works fine."

### 7.9 Teaching a mixed audience — the mechanism that costs nothing
**Bolded lead sentence + explanatory body, keyed to one figure.** An expert reads
the bold lines in fifteen seconds; a non-expert reads the paragraphs. Model:
*"**(c) Undefined behaviour is not a synonym for a crash.**"*

⚠ Three conventions from the in-house draft that would **hurt us** — do not copy:
1. **The zero-onramp opening.** Steal the shape; gloss the terms inline.
2. **Sustained maximum density.** After each dense paragraph, one short plain
   sentence saying what just happened.
3. **The never-re-explain rule.** Right for a linear PDF, wrong for a hash-routed
   report. **Re-gloss `rung`, `pattern`, obligation, trusted base and `Ir` at the
   head of each view**, and keep a conventions box reachable from every page.
4. **Do not import the adversarial framing.** That draft audits someone else's
   published numbers; we audit nobody. The same rhythms over our own measurements
   read as defensive.

### 7.10 Section titles are claims, questions or stances — never topics
In-house models: *"One direction, not a scatter"*, *"Where the counters are not
blind"*, *"The mechanism we spent longest on is the baseline's"*, *"Three things
we will not recommend"*. The compound form `X, and Y` recurs and **the second
clause is always the part that costs something**.

### 7.11 Inherited rules that still hold
From ver_B, and they are not negotiable: say **"plain, unchecked C"**, never
"idiomatic C"; **no pattern IDs as nouns** (`\pat{p16}` only where the reader
might go look); **every number ships its scope in the same sentence**; **every
limitation ships its direction**; round, except where exactness is the evidence;
**never editorialise about a language without a measurement**; and Verus's
`N verified` counts **items**, not verification conditions.

---

## 8. THE SPINE

Target **6,000–7,000 prose words** (ver_B is 6,792). ver_C is not shorter — it is
**re-proportioned** per §1. Every title below is a claim; a writer who cannot
defend the title should not write the section.

| file | § | words | the claim the title makes |
|---|---|---:|---|
| `00-summary.md` | — | 500 | The findings list, **with the hinge** (§7.3). Numbered findings F1–F8, each ending in what it motivates except the bad-news ones. |
| `10-instance.md` | 1 | 650 | **"One deleted line, four rungs, four different failures"** — the running example (§6) opened per §7.1, then the gap sentence (§4) and the rubric (§7.2). Method ≤150 words. |
| `20-notthecheck.md` | 2 | 1500 | **"When safe Rust costs you, it is usually not the check"** — Half A. The decomposition table (10 rows), the dead clamp, the two rows where it *is* the check, the prospective catches. |
| `30-spelling.md` | 3 | 900 | **"The number moves when you respell the side nobody tuned"** — 7.26× median, 510× on one band, two sign flips, 14 of 26 undeclared. Ends in the method: **delete the mechanism and re-measure.** |
| `40-allocation.md` | 4 | 1400 | **"Four detectors, one blind spot: they all range over the allocation"** — Half B. The coverage table introduced as *questions* (§8.1), its negative space, the bitset, the range parser, the recycle probe, fortification and redzones. |
| `50-nonoptional.md` | 5 | 700 | **"What you buy is not the check but the impossibility of omitting it"** — hardened C ties on all 4,104 runs; the four-rung table pays off; the check costs about the same in both languages. |
| `60-implications.md` | 6 | 1000 | **"What to measure instead"** — §7.4's loops closed, one subsection per audience (practitioner / benchmark author / tool author / verification). **This section is 15–20% of the paper and ver_B had nothing like it.** |
| `70-withdrawn.md` | 7 | 450 | **"Eight claims that were ours, and what killed each"** — the withdrawn-claims table (§7.8), opening with what held. |
| `99-close.md` | — | 250 | The thesis restated **narrower** than in §1 (§7.8's in-house convention). |

⚠ **Limitations do not get a section.** They are filed beside their claims
(§7.6). The instrument critique lives in `70-withdrawn.md`. The concurrency scope
statement stays on page one and in one clause of §1 — it is a *scope*, not a
limitation.

### 8.1 The coverage table, per TaxDC
Introduce it **in the method, before any data, as a table of questions with no
counts in it** — rows are italic questions, cells are permitted answers. Counts
live in a separate exhibit. *"A question is something a reader wants answered; a
bin is bureaucracy."*

---

## 9. FACTS, AND WHAT THE CORPUS CANNOT SUPPORT

**Authority order:** `../.memory/` 00–06 (supersedes any task report) →
`../RECAP.md` → `../results/SYNTHESIS.md` → `../results/gate/*.json` → pattern
`NOTES.md`/`spec.md`.

⚠⚠ **`paper_vers/CLAIMS.md` IS COMMITTED AND IS THE DURABLE RECORD. READ IT
BEFORE WRITING A WORD.** It carries the 23-item DO-NOT-CLAIM list, the four
theses the corpus cannot carry, and the standing wording rules — every entry is a
claim some draft actually made and had to withdraw. It spans all versions,
because a claim that is false is false in every framing.

`.temp/verify/FACTS.md` and `.temp/verify/RULINGS.md` hold the fuller working
notes and the per-settlement citations, **but they are gitignored scratch and may
be gone.** `CLAIMS.md` is the part that had to survive; if the `.temp/` files are
missing, re-derive the supporting detail per §11 — about four agent-hours.

### The four claims the evidence does NOT carry. Do not write them.

1. **"Memory safety costs ~X%."** The distribution moves `9/4/9` → `7/3/10` at
   searched values with two sign flips; 14 of 26 rows are undeclared; 4 are
   unlicensed for differencing; the identity pin holds one endpoint above its
   floor by a measured **−17,526 `Ir`**; and one pattern's percentage is **wrong
   in sign at the other input**. No cross-pattern wall clock exists.
2. **"Rust catches it."** `totals.loud = 0` of **4,104** adversarial runs — not
   one bounds check fires anywhere in the shipped matrix, and hardened C matched
   the model everywhere. The deleted-check control holds on 4 of 8 patterns, is
   conditional on 2, and is **false on 2**.
3. **"A proof buys memory safety free" / "verified means done."** The
   proved-minus-unsafe zero is a **tautology** — the identity pin entails it. A
   proof-enabling change cost 8.5% of one kernel and shipped described as free.
   Ghost code does not fully erase. There is no compile-time or authoring-hours
   data, so the price is a **floor**.
4. ⚠ **"Safety is free here"** read off a zero difference. **Nothing in the gate
   distinguishes a deleted check from two rungs that compiled to the same
   bytes.** This bounds ver_C's own recommended method, so **§2's method must
   ship with it** (§7.8: admit, then bound the admission).

---

## 10. FORMAT AND GATES

Spec: `paper_vers/README.md`. Create `paper_vers/ver_C/` with `meta.json`
(**set `"current": true`; ver_B's must be flipped to `false`**), `paper.md`,
`sections/*.md`, `refs.json`. Add the three reference papers to `refs.json`.

Markers: `\section{}` `\subsection{}` `\label{}` `\ref{}` `\num{path}`
`\figure{id}{cap}` `\src{}` `\cite{}` `\pat{}` `\todo{}`; environments
`abstract|principle|example|takeaway|caveat|retraction|quote`; `%%` comments;
`%%literal-ok <n>`.

Figure ids: `ladder` `spread` `outcomes` `identity` `tcb` `rungcost`. An unknown
id is a build error. **A new figure means adding a drawing function to
`paper.js`'s `paperFigure` and its id to `FIGURE_IDS` in `build_data.py`** — the
decomposition table of §8 §2 may want one.

⚠ **Renderer traps, each of which has already cost time:**
- Emphasis does **not** nest; code spans inside emphasis are fine.
- Every block marker on **one line** — a wrapped `\figure{}{}` used to vanish
  silently, taking its `\label` with it.
- A label is **not** prose: `PATTERNS[].title` and `SHORT[]` render raw.
- `\num{}` for every corpus count; the build **fails** on a bad path and **warns**
  on a bare literal ≥100 matching a corpus total.
- `totals.proof_text.ratio_pct` is an **integer percentage**, not a multiplier.

```bash
python3 build_data.py            # 0 errors, 0 todo, no literal-figure warning
node check.mjs                   # OK
node tools/responsive_audit.mjs  # exit 0
git -C .. status --porcelain | grep '\.web'   # empty
```

**And the test no gate runs:** hand `00-summary.md` to a developer who has never
heard of this project. **They must name the thesis in their own words, and three
things they would do on Monday.** ver_B passes the second half already; the first
half is what ver_C adds.

---

## 11. PROCESS

The eleven-agent pipeline that produced ver_B worked; `.memory/paper-writing-process.md`
carries its nine lessons and they are binding. In order:

1. **Evidence agent first, on PRIMARY ARTEFACTS.** Re-derive §6's table and §2's
   decomposition counts from `results/` and pattern `NOTES.md`. ⚠ Tell it to open
   the log, not the write-up: ver_B's plan inherited a three-program set from a
   summary and one of the three **had no surviving evidence**.
2. **One outline agent**, applying §1's three fixes as gates and rejecting any
   section whose title cannot be written as a claim.
3. **Writers, one per section**, each owning whole files, with word budgets that
   **already include** the mandated caveats and scope clauses.
4. **Three reviewers, blind and in parallel** — rigour, practitioner persona,
   fact-checker re-deriving from `results/gate/*.json`. **They will contradict
   each other; the contradictions are the point** and the supervisor settles them
   against the tree, not by preferring the more confident report.
5. **A coverage-bias reviewer**, commissioned explicitly: *which way do this
   paper's gaps point?* Nothing else finds it, by construction. Last time it
   found four omissions all favouring safe Rust.
6. **One trim agent owning every file**, so cross-file moves are possible.

⚠ **Check the supervisor's own rulings.** On ver_B one of mine was
over-generalised and a reviewer caught it (`RULINGS.md` R7-CORRECTED).

---

## 12. WHAT CARRIES OVER, AND WHAT IS BURNED

**Carry over from ver_B, near-verbatim — three reviewers named these load-bearing:**
- the outcome-matrix caveat (*"not one bounds check fires anywhere in the shipped
  matrix"*) and its placement after the headline and example
- the binary-search self-correction — the paper applying its own rule to its own
  worst number and moving it by a sixth
- the four-rung deleted-line table and the happy-path clause
- the coverage-bias retraction
- the detector-coverage ordering in §5, which becomes part of §6's implications
- the concurrency scope caveat, verbatim

**Burn:** ver_B's three-question spine and its section titles; its limitations
section as a section; the *"this paper will not decide for you"* refrain; and any
sentence whose job is to describe the paper rather than the evidence.

**ver_A and ver_B both stay on disk.** A version is a framing. Three framings over
one corpus is the point of the directory, and a reader can compare them.
