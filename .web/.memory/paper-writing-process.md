---
name: paper-writing-process
description: "How the ver_A paper was produced with sub-agents, and the four things that actually decided its quality"
metadata:
  type: feedback
---

The user asked for a systematic, self-improving writing process with named
roles — brainstorm, customer delegation, research reviewer, writing advisor,
writing agent — with me as supervisor staying high-level. It worked. What
follows is what mattered, so the next version does not re-learn it.

**Why:** the roles are not decoration. Each caught a class of defect the others
were structurally blind to, and the overlaps were small enough to be worth the
cost.

**How to apply.**

**1. Ground before you frame.** The first agent out is an evidence inventory:
every claimable result with its number, unit, measurement convention, scope,
status and the caveat a careful reviewer would raise, sourced to a file. It is
the anti-hallucination substrate for everything after it — and it found a real
defect in the site itself, that the proof totals silently included a control
cell and so disagreed with the research they reported. No check here could have
caught that, because none of them knew what the number was supposed to be.

**2. Brainstorm in parallel from different angles, then DECIDE.** Two framing
agents (measurement angle, safety angle) plus a practitioner produced three
incompatible good papers. The supervisor's job is to pick one and write the
framing statement down — `meta.json`'s `framing` field exists for that. ⚠ The
review then found ver_A was **carrying ver_B inside it**: the measurement thesis
its own framing statement demoted appeared as a caveat, a retraction, a
principle and two more retractions, and by word count was the headline. A
version is a framing, and a framing has to be enforced, not just declared.

**3. Writers must be told to verify the brief, not just execute it.** Two did,
and both were right to: one found the Miri seed premise I passed on had been
retracted upstream; another found a p11 claim superseded in the authoritative
layer. ⚠ **And two agents contradicted each other on the same evidence** — one
reporting a claim supported, the other retracted. The supervisor settles that
against the tree, not by preferring the more confident report. See
[[division-of-labour]]: agent reports get checked like anything else.

**4. The reviewers found what I could not.** Four blockers, all real, none of
which any automated gate could see: a section repeating a claim another section
retracted; a predictivity claim the research record inverts; a trusted-base
accounting that omitted the solver (`Z3`, `SMT` and `soundness` appeared nowhere
in 18,000 words); and a table asserting safe Rust trusts *"nothing"*, which
contradicted the paper's own thesis. **Adversarial review is the step that
produced the quality, and it is not optional.**

**Round 2 (ver_B) confirmed all of the above and added five.**

**5. Ground the evidence agent on PRIMARY ARTEFACTS, and say so.** ver_B's plan
inherited a "three programs verify and are broken anyway" set from `RECAP.md`.
Two agents opened the actual run logs and the third member had **no surviving
evidence** — a refused catalogue candidate whose logs contain zero occurrences of
the exit code the claim quotes, whose build script never invokes the prover, and
whose own report says the verified function is not the same kernel. `RECAP.md` is
a summary, and this project's own retraction rule is *a summary of a measurement
is not the measurement*. **Tell the evidence agent the authority order and tell
it to open the log, not the write-up.**

**6. Run reviewers BLIND AND IN PARALLEL — the contradictions are the point.**
Three reviewers disagreed three times, and every settlement improved the paper.
A practitioner and a rigour reviewer independently concluded that three of the
four coined words were unused re-labels — convergence from different premises is
much stronger evidence than either report alone. Elsewhere they appeared to
conflict on whether a shipped rung leaked; the settlement was that *"the shipped
rung"* is ambiguous when a pattern ships six. **Both objections dissolved into
one wording fix, and neither reviewer could have found it alone.**

**7. ⚠ The supervisor's own rulings are not exempt.** I issued a ruling saying a
pattern's shipped rung was not a disclosure. True of one input; I generalised it
to the pattern, and the tree says the opposite for a different committed input —
*"It is in fact the genuine leak."* A reviewer caught it. **Write rulings with
the same citation discipline you demand of writers, and expect them to be
checked.** See [[division-of-labour]].

**8. Apply the coverage-bias test to the document you just produced.** §6's own
retraction says omissions can all run one way while every figure reproduces. The
rigour reviewer applied that to ver_B and found four omissions, all favourable to
safe Rust — including one that is *literally on the project's own list of the
five omissions that constituted its documented bias last time*. **Commission
this as an explicit review question. Nothing else finds it, by construction.**

**9. Make the practitioner run the acceptance test COLD, on one file, first.**
The instruction was: read `00-summary.md`, stop, now name three things you would
do on Monday. That produced a clean pass/fail before any of the reviewer's other
opinions could contaminate it — and their three actions, in their own words, are
the evidence the rewrite worked.

**Round 3 (ver_C) confirmed all of the above and added six.**

**10. ⚠ Expect your own rulings to be wrong, and invite the overrule in writing.**
Three of mine were overturned this round: a fold width, a "verbatim" published
quotation that was a **splice of two sentences from two pages**, and the deepest
one below. **Every one was caught by someone who opened the artefact rather than
the ruling.** The mechanism that caught the worst was a line in the reviewer's
brief inviting them to overrule me, with a section of the report reserved for it.
Without that line they may have written around it.

**11. Two rulings can each be right and jointly impossible — and a faithful writer
will execute both.** I ruled that a truncated table was the coverage bias and
must be restored to twelve rows; I then ruled its headline count corrected *at
the truncated grain*. The section did both, and so **retracted a truncation and
computed its own title's number over that same truncation**, excluding both of
its featured examples, in the direction that flattered it. Nobody noticed inside
one section. **Check rulings against each other, not just against the evidence.**

**12. Re-run the bias review after the revision. It is not a one-off gate.** Its
own closing instruction was *"the revision will move the residue again"*, and it
was right: the revision **over-corrected**, and the axis flipped. A third bounded
pass was still finding discretionary calls. Budget for at least two.

**13. ⚠⚠ Check the direction of the PROVENANCE, not only of the claims.** The
sharpest finding of the whole round: the paper carried **non-gate-certified
failure evidence prominently and omitted gate-certified success evidence
entirely**. Every claim was true, every figure reproduced, and the *evidence
tiers* ran one way. That has no arithmetic signature **and no claim-level
signature** — counting claims for and against would have scored it clean.

**14. Give the bias reviewer the evidence packs, not just the paper.** The gaps
live in the difference between what was gathered and what was used, and the packs
were several times the length of the paper. A reviewer holding only the document
can see repetition and hedging but cannot see an omission.

**15. Tell writers to verify the brief, then expect them to find the brief
contradicting itself.** Three writers independently found conflicts between the
outline's per-section spec and its own redundancy map, and one found the summary
spec forbidding cross-references two lines before requiring one. They resolved
them correctly and said so in comments. **A brief long enough to be useful is
long enough to be inconsistent** — say which part wins.

**What I would change next time.**

- **Give writers word budgets that include the mandated additions.** All four
  revisers independently reported the same thing: the targets were unreachable
  because the blocker fixes cost more words than the cuts licensed. Three
  independent agents saying so is evidence the target was wrong, not the work.
- **Assign cross-file moves to ONE agent.** Moving a principle out of section 9
  and into section 6 works only if both files have the same owner. Where they
  did not, I had to carry the instruction in two prompts and hope.
- **Ask for the redundancy map early.** A five-agent draft from a shared outline
  repeats itself: five anecdotes told four to six times, ~2,400 words. The
  writing advisor found it in one pass; a writer cannot see it from inside one
  section.

---

## ver_D — what the fourth framing added

**16. Diagnose the failure from the transcripts, not from the scores.** I built
ver_D's brief on *cardinality* — how many things the reader holds at once — which
the per-section scores supported. A red-team then re-read the four cold-read
transcripts and found that **all four readers quit on REPETITION, and none named
difficulty**. One counted eight demonstrations of a single finding: *"From the
fourth on I stopped reading the numbers and just scanned for whether the point
had changed. It hadn't."* Two of the three best sections sat **after** the point
they would have stopped. **Scores tell you which sections were bad; only the
transcript tells you why the reader left.** The rule that came out of it —
*demonstrate each finding exactly once* — cut a section from nine beats to five.

**17. A fact pack is not a source, and mine propagated three errors.** ver_D's
`FACTS.md` was assembled largely from ver_C's fact-checked prose, and it carried
three defects straight into the draft: the bounded-stack clamp described as a
*deletion* when it is a line **added**; a surviving `+5` called unexplained when
the tree names it two lines away; and a tally I stated as *six of ten* while
**forbidding the correct seven**. Worse, the pack was confidently wrong — the
forbidding is what made it dangerous. **Point the fact-checker at the pack as
well as the draft**, and say so.

**18. The most damaging sentence was the one the project was proudest of.**
ver_C and ver_D both said *"no stage of our gate reads source"*. The gate reads
every rung's source, matches the pinned spelling, and publishes the missing check
in the very record behind the flagship table. It survived four rigour reviews of
ver_C **because it flattered the paper's thesis** — a document admitting a
weakness gets less scrutiny than one claiming a strength. The true version is
sharper: the gate records the missing check **and passes anyway**.

**19. Stop the writer when the brief is wrong, not when the draft is.** The
red-team landed 30 seconds after the writer started. Killing it, rebuilding the
brief and relaunching cost one minute; applying the same changes to a finished
3,000-word draft would have been most of a rewrite. **A critique of the plan is
worth more before the work than after it — run them concurrently and be willing
to throw the work away.**

**20. Ask what a reader will DO, and cut what they skip.** All four cold readers
skipped the buy-a-proof material — *"I have never bought a proof, I'm not going
to"* — so ver_D's close went from four imperatives to three. And of six sentences
a reader named as buying the most trust, **not one was a provenance claim**; they
were all admissions of ignorance. The provenance formula went from six
appearances to two. **Keep every admission, cut every ritual.**

---

## From ver_E — the lessons that were new

**21. Derive the structure a second time, blind, and compare.** Before writing,
a sceptic persona was given only the pitch — and explicitly forbidden to read the
plan — and asked to produce its own ladder of objections in the order it would
raise them. It independently placed *"why not just harden my C?"* at 7 of 9, for
the plan's own reason: asked first it is a cheap dismissal, and it only becomes
the sharp question once you already believe the cost is small, nonzero and
unevenly spread. That converted the framing's single load-bearing decision from
a hope into a tested one, and the same pass found five gaps — the largest being
that **system integration, not performance, is the reader's real blocker**, which
the corpus cannot answer and the paper now declines to extrapolate to.

**22. "Verified at source" has two meanings and only one of them counts.** I
wrote the writers' evidence pack *after* reading `results/SYNTHESIS.md`, which is
the project's own hand-written synthesis and its second-highest authority. An
independent fact-check against the **primary artefacts** — the patterns'
`NOTES.md` — then found **thirteen** of my entries wrong or materially
misleading, including one that was false in a way that would have handed a
hostile reader a counterexample in seconds. A summary is a claim about the
evidence, not the evidence. ⚠ This is the third round in which the *brief* was
the defect rather than the draft.

**23. Push corrections into running writers; do not wait for the draft.** The
fact-check landed while two writers were mid-section. Sending each a targeted
correction cost a few minutes; letting them finish against a wrong pack would
have cost two finished sections. Both then applied the corrections *and*
independently caught further errors — one found that a `143,740,000` figure I had
labelled per-call was a whole-run total, one found that a correction of mine was
worded backwards and resolved it by arithmetic against the table, and one caught
a derived ratio it had written itself (46/1.6 ≈ 29, not 60) and removed it.
**A writer given the reasoning behind a rule will check the rule.**

**24. Put the instrument's own blind spot in the paper.** The strongest omission
the review found ran *in favour* of the argument: two bug classes safe Rust wins
outright — an overlapping `memcpy` the borrow checker rejects at compile time,
and a strict-aliasing miscompile — and **neither is visible in any instruction
column**, which is what this entire report is made of. A corpus that prices
things cannot see what it cannot price. Saying so in our own voice is worth more
than either number, and it is also the answer to *"what does hardening my C not
buy me?"*

**25. When a percentage has a wall-clock twin, the twin is not a hedge.** A +72%
instruction tax is +0.27% of time; a 46% one is +1.6%. One pattern's notes say in
as many words that **neither number may be quoted without the other**. Shipping
only the instruction figure would not have been a rounding error — it would have
been the report's own thesis, applied to everyone except itself.

---

## 26. The frame test, and it outranks everything above

The owner, after two passes that fixed structure and crispness:

> "**The questions make sense, the answers make no sense.** You think the
> audience will read our code? Which reader will read the code and measure the
> data…"

Both earlier fixes were real and neither touched the actual defect. The answers
were **written from inside the project**: the grammatical subject of nearly every
one was *this corpus*, *the shipped set*, *the 22 rows licensed for
differencing*, *what is fair to subtract*. Nobody had asked about the apparatus.
They had asked whether to rewrite **their** C.

**Why:** structure and concision are properties of the text. Frame is a property
of the relationship between the text and the person reading it, and it survives
every edit that does not name it. A listener cannot re-read, does not have the
source open, and cannot size "+24 instructions per call" until somebody says
whether 24 is a lot.

**How to apply — three tests, on every answer:**
1. **Whose world is the subject?** The first sentence is about their code and
   their decision. Method appears only where it changes the answer, in one clause
   of plain words.
2. **Is every number sized in the same breath?** *"about 24 instructions per
   call — on any function that does real work you will not find that in a
   profile."* *"Seven times. Not seven percent."*
3. **Could they repeat it in a meeting tomorrow?** If the sentence needs our
   repository, it is not an answer.

⚠ **It is a translation, not a cut.** Every fact and every scope stays, and the
concessions come out *stronger* in plain words — *"the safety net I am selling
you has never been photographed catching anybody"* carries the same measurement
as *"zero of 4,104 adversarial runs end loud"* and actually lands.

⚠⚠ **And the translation is itself a review.** Forced to say "24 instructions —
you would not find it in a profile", the writer discovered the median's range is
−125…+10,242 and the dearest case is not a check at all, so *"hardening C is
cheap"* is false as a law. Three more claims got visibly weaker the moment the
jargon came off. **If a claim only sounds strong in your own vocabulary, it is
not strong.**

---

## 27. The say-it-out-loud test — apply it to the QUESTIONS, not just the answers

Lesson 26 fixed the answers and I never checked the questions. The owner got lost
at slide 11 of 52 and had to say it a second time:

> "I am lost from **'But I measured a big number'** already. What the heck what
> numbers. **How can the audience 'measure' your number???** … I said this is
> problematic DOES NOT MEAN this is the only problematic."

**Why:** a document organised as objection → answer feels rigorous from the
inside even when a third of the objections are ones a **peer reviewer** would
raise about the method, not ones the **reader** would raise about their code.
Those questions pass every structural check — they are questions, they are in
order, each follows the last — and they still make the document unreadable,
because the reader never asked them and cannot answer them.

**The test:**

> **Could somebody say this out loud, having heard only what came before it?**

Failing questions from that deck, all of which had survived three review passes:
*"What does the corpus say?"* · *"How hard did you look?"* · *"Is that zero
real?"* · *"Is your corpus even representative?"* · *"Start with the one that
does not hold up."* — and the one that broke it: **"But I measured a big
number"**, whose answer then offered *"which two versions you subtract"*, which
presumes the reader owns our six versions and is differencing pairs on a bench.

**How to apply.**
1. Render the questions alone, in order, and read them as one person talking.
   `tools/render_deck.mjs --questions` exists for exactly this.
2. Any question containing a word that only exists in our method — *corpus,
   rung, spelling, row, version-pair, "your numbers"* — is ours, not theirs.
3. **Find the real objection underneath and answer that one instead.** Under "I
   measured a big number" is **"I've seen benchmarks where Rust is slower"** —
   and we already had that answer (most published safe-Rust numbers compare an
   untuned port against tuned C), nine slides away from the question it answers.
4. **Move a concession, never drop it.** A reviewer's question can hide content
   worth volunteering: *"how hard did you look"* is not something an audience
   asks, but the answer — we searched the safe side harder, and it pushes every
   number our way — belongs in *"why should I believe you"*, where it is stronger.

⚠ **And the meta-lesson, which the owner had to state explicitly: one named
example is a sample, not the defect.** When told a slide is broken, audit every
slide against the property that broke it before reporting back.
