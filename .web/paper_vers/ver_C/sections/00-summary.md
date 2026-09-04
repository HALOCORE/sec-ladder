%% ver_C — the briefing.  No \section, no number: it precedes section 1.
%% Written to OUTLINE.md PART 1 §`00-summary.md` and Gate 2.
%%
%% ⚠⚠⚠ THE CUT PASS (.temp/brief/CUT.md).  TEN FINDINGS BECAME SIX, BY RULING.
%% The plain-language pass fixed the sentences and grew the paper to 8,713 words;
%% the supervisor's ruling is that a briefing with ten numbered findings, a hinge
%% and a scope paragraph is not a briefing.  The mapping, which a later editor
%% must not quietly undo, and which EVERY OTHER SECTION'S CITATIONS FOLLOW:
%%   F1 <- old F1     (one kernel, four costs, 0.00000 per byte)
%%   F2 <- old F2     (3 / 5 / 1 / 1 of ten, with the check's magnitude)
%%   F3 <- old F5     (our own same-machine-code rule flatters safe Rust)
%%   hinge            unchanged in job, one sentence
%%   F4 <- old F6 + old F7  (remove and re-measure; the surviving +5; the two
%%                     rows caught before publication)
%%   F5 <- old F8 + old F9  (four tools, five of ten, the blind spot a hardening
%%                     flag made)
%%   F6 <- old F10    (exit 101 is zero; ends on the BOUND, no `Do:`)
%% DROPPED FROM THIS FILE, and each survives where its evidence already was:
%%   old F3, the least-recorded caveat -> §2's caveat, which is its home;
%%   old F4, the hardening median      -> §3's C-column subsection.
%% ⚠ NO SECTION MAY CITE **F3** FOR THE SEARCH BIAS OR **F4** FOR HARDENING ANY
%% MORE.  Those citations were rewritten to \ref the owning section instead; if
%% you restore a bullet, restore its citations with it.
%% ⚠ IF WORDS COME BACK, RESTORE IN THIS ORDER: (1) old F4's hardening median as
%% its own bullet — it is the C-column half of the thesis and it is the one
%% dropped bullet that carries a figure this file no longer prints; (2) old F3
%% as its own bullet; (3) the two `Do:` lines that were merged.
%% ⚠ THE BUDGET IS 480 PROSE WORDS AND THIS FILE MISSES IT.  Six findings
%% carrying two to five figures each, with the scope clause CLAIMS.md §3.4
%% requires, plus two `Do:` lines, the hinge and the scope paragraph, do not fit
%% in 480 words of plain phrasing.  Everything reachable without deleting a
%% number is gone.  The next cut here is a WHOLE finding, by ruling; it is not
%% the qualifications, which is how the unreadable draft happened.
%%
%% THE DONE-TEST FOR THE WHOLE REPORT lives here.  Hand this file, alone and on
%% paper, to a developer who has never heard of this project: they must be able
%% to name THE THESIS IN THEIR OWN WORDS and THREE THINGS THEY WOULD DO ON
%% MONDAY.  ✅ THE COLD TEST PASSED at review, on the ten-finding version: the
%% practitioner named the thesis without looking back and gave four Monday
%% actions.  The two `Do:` lines and the hinge are what carry that; do not cut
%% them to reach a word count.
%% Everything about the file's shape follows from the done-test:
%%   - no \ref and no \pat: it has to work detached from the paper;
%%   - no `abstract` environment: an abstract reads as a summary of a paper, and
%%     this is a briefing about the reader's own codebase;
%%   - none of the paper's vocabulary (see the `resource` note below);
%%   - sentence one is the thesis, not a set-up, so a reader who stops after
%%     forty words has the argument.
%%
%% STRUCTURE, fixed by Gate 2 and not to be flattened by a later trim:
%%   F1–F3   why the problem is hard.  NO "this motivates" clause on any of
%%           them — convention 2.4 withholds it from the bad-news bullets, and
%%           that is what keeps the list from reading as salesmanship.
%%   HINGE   exactly ONE sentence, modelled on TaxDC's page-2 hinge.  It says
%%           three things: each finding above is a failure to attribute a number
%%           or a guarantee to a mechanism; every one was found by the same
%%           operation; the operation is cheap enough to run on your code.
%%           ⚠ IT SAYS "where the mechanism can be removed" — the cold reader
%%           caught the unqualified version as an overclaim, because §4's whole
%%           subject is where the operation CANNOT run.  It now counts THREE
%%           findings above it, not five; that number moved with the merge.
%%   F4–F5   each ends in what it motivates, as a `Do:` line.
%%   F6      ends in a BOUND, never a motivation, and carries no `Do:` label.
%%           It is bad news about our own recommendation, and CLAIMS.md §1.23
%%           requires the method to ship with the bound.
%% DEPENDENT ITEMS (Gate 2 wants three; there are four): F2←F1, F4←hinge,
%% F5←hinge, F6←F4+F5.  The list cannot be read out of order — that is the
%% difference between an argument and a list, and it is what ver_B lacked.
%% Where each link is carried, so a trim does not sever one by accident:
%%   F2←F1     "It repeats"
%%   F4←hinge  "Where it can be removed" answers the hinge's operation
%%   F5←hinge  "Where it cannot" is the same clause negated
%%   F6←F4+F5  "bounds both findings above" — F4 and F5 are the two that
%%             recommend something.  Not "everything above": F1–F3 are not
%%             recommendations and are not what the zero bounds.
%%
%% ⚠ WHY "Do:" AND NOT "Motivates:".  The gate requirement is structural — the
%% bullet ends in what it motivates — and the done-test is that the reader can
%% name three things to do on Monday.  An imperative label serves both.  F6
%% deliberately does NOT carry the label, which is the visible signal that it is
%% a bound and not a sell.
%%
%% ⚠⚠ THE WORD `resource` IS NOT USED HERE, deliberately.  CONVENTIONS.md §4
%% earns exactly one word of vocabulary and earns it in §4, off four named
%% tools; the redundancy map gives §4 as its home.  A coined noun in a briefing
%% that must work DETACHED is unearned by construction.  F5 says "watches".  It
%% may NOT become "covers": "covers" is the vague word §4 exists to replace, and
%% the cold reader flagged the weakening.
%%
%% ⚠⚠ THE THESIS SENTENCE'S SECOND HALF says what the guarantee WATCHES and
%% where the bug SITS.  It used to read "the coverage you assume is usually the
%% allocation", and the cold reader could not parse "the allocation" as a bare
%% noun in the one sentence in the document that most has to land.  "Most often"
%% rather than "usually" keeps C16's three-way split intact — the timing row's
%% silence is values-not-the-trace, and flattening that is the error C16 names.
%%
%% NUMBERS — every one checked against OUTLINE PART 2 (the redundancy map) and
%% against the evidence pack that sources it, not against the outline alone.
%%   F1  −2545 / 0 / +77 / +17123 and 0.00000 per folded byte — C3, E1 §1.5.
%%       ⚠ ALL FOUR ARE `large`-BLOB FIGURES, so the bullet says "on one input":
%%       a spread across four comparisons is only a spread if the input is held
%%       fixed.  ⚠ C3 forbids leading with the naive port's +69%; it is not here.
%%       "the cost of memory safety" is in quotation marks because the phrase is
%%       the thing under examination — CONVENTIONS §1 bars it unqualified.
%%       ⚠ `spelling` is glossed HERE, at its first use in the paper.
%%   F2  3 / 5 / 1 / 1 of 10 — C9, E2 §5.2.  The tree's "licensed for
%%       differencing" is stated as the RULE in plain words — "only fair when
%%       both call the same outside code" — because "licensed" means nothing to
%%       a detached reader.  §2 uses the same words, so the two files can be read
%%       in either order.
%%       ⚠ FOUR buckets are enumerated, not three (rigour m3): a §0-only reader
%%       was being given 3+5+1 under a denominator of 10.
%%       ⚠ "It repeats", never "it generalises" — `results/SYNTHESIS.md:592-599`
%%       refuses the stronger reading in its own voice ("so it is not a score.
%%       Read the entries, not the tally") and `:877-883` records that fourteen
%%       patterns carry an `index >= len` axis by construction.  The closing
%%       clause says the census cuts BOTH ways: a corpus over-weighted toward
%%       bounds bugs finding the check dominant on only three of ten is a
%%       STRONGER result.  "It repeats" is also the F2←F1 link and may not go.
%%       ⚠⚠ THE CHECK MAGNITUDE IS WELDED INTO THIS BULLET (second coverage-bias
%%       review §4.2).  This file printed five percentages, every one of which
%%       either damages our own instrument or shrinks the check, and NO
%%       check-magnitude percentage at all.  "42% to 205%" is §2's pair (42.5%
%%       rising to 46.6%, and 205.6%), each rounded DOWN so the bullet cannot
%%       overstate, and "a kernel that does nothing else" is §2's own scope
%%       clause and is not optional.  MANDATORY: this clause may not be cut
%%       without cutting §2's magnitude paragraph with it.
%%   F3  17,526 Ir/call ≈ 35% — C23, E4 A7.  ⚠ Three corrections all present: a
%%       SAVING FORGONE not a cost imposed; `large`-ONLY (the sign reverses on
%%       small, where the pinned rung is 3,448 cheaper); and the consequence.
%%       ⚠⚠ WRITTEN IN §3's WORDS.  The cold reader could not parse the old
%%       bullet at all — "I do not know what an identity pin is, what it holds,
%%       or what it holds it above" — and then, having reached §3, called the
%%       same finding "the most honourable in the paper" and asked for exactly
%%       this substitution.  The claim leads; the apparatus follows it.
%%   F4  98.6% / 99.2% — C11.  ⚠ NOT 100%: that figure is correct of the C check
%%       and became wrong when carried onto the Rust column, and printing the two
%%       percentages is what makes the correction visible.
%%       ⚠⚠ THE SURVIVING +5 IS MANDATORY (supervisor S2, and CUT.md carries it
%%       forward into the merged bullet).  A reader of this file alone came away
%%       believing the deletion was total, which is the exact overstatement C11
%%       exists to correct.  ⚠ The handle table's
%%       `230.0694 = 109.6476 + 120.4218 + 0.0000` stays out of this file, and
%%       its decomposition is now cut from §2 as well; the allocator zero
%%       survives in §1's prior-work paragraph, which is where a reader meets it.
%%       ⚠⚠ THE `Do:` CARRIES §6.1's PREDICTIVE RULE.  It was at 78% depth in a
%%       sub-bullet; the practitioner's single recommended change to the whole
%%       report was to promote it, because it says what you will find before you
%%       measure and it explains F1 and F2 retroactively.
%%       ⚠⚠ C13 GOVERNS THE SECOND HALF: the licensed shape is "the measurement
%%       would have been wrong, and it was caught before publication", NEVER
%%       "the cost trap is why the row was refused" — both rows also die on
%%       duplication and the review rejected the first stated reason for one of
%%       them.  ⚠ 6.02× / 108.4% / 3.0% / 9.6% / 100% spelling now appear NOWHERE
%%       ELSE IN THE PAPER: §2's worked example of them was cut before this pass
%%       and §6 is forbidden to cite them.  This bullet is their only home.
%%   F5  ⚠⚠ THE COUNT IS OVER THE TABLE §4 PRINTS (C31, rigour B2).  It used to
%%       read "four of six classes", which is C16's numerator over ver_B's
%%       SIX-ROW table — the truncation C15 orders restored and §4 retracts.
%%       C16's denominator is overruled: §4 counts over the twelve rows it
%%       prints, excluding the two where a detector is not measured, and gets
%%       FIVE OF TEN.  No count here may need the truncation, and no phrase here
%%       may say "at the six-class grain the previous version used" — that
%%       defines the paper's Half-B headline by reference to a document the
%%       reader cannot open.  C16's three-way split is kept whole (the allocation
%%       for two of the shared silences, values-and-not-the-trace for timing).
%%       (a) "agree", never "return the same verdict".  On three of the five rows
%%           the four detectors do NOT return the same verdict: those rows read
%%           `no / vacuous / vacuous / no`, two values the counting rule groups
%%           as silence, and §4's legend prints that they differ.
%%       (b) ALL FIVE ROWS ARE ACCOUNTED FOR (review §3.2).  The bullet gave 5 of
%%           10 and then named only the shared silences, so a detached reader
%%           learned that the detectors are uniformly blind and never that two of
%%           the five agreements are all four FIRING.
%%       (c) THE COUNT'S ONE LAX RULE SHIPS ITS SIZE (review §3.1).  Three of the
%%           five agreements exist only because two kinds of silence count alike;
%%           on one verdict it is two of ten.  The bullet keeps FIVE as its
%%           number — it is the count under §4's stated rule — but a briefing
%%           that must work detached cannot print it without the choice that
%%           produced it.
%%       ⚠⚠ THE BLIND-SPOT HALF (old F9) CARRIES NO COUNT (S9, rigour B3).  It
%%       used to read "five of those six are silences of scope", and TWO agents
%%       caught it independently: §4's own writer put in writing that the number
%%       IS NOT DERIVABLE FROM THE TABLE IT DESCRIBES, and "those six" had no
%%       referent.  It takes §4's wording — a quantifier over the printed table.
%%   F6  exit 101 zero times — C20, E4 B14 and the decisive negative at E4:1583.
%%       ⚠ THE 1,099 BEHAVIOUR GROUPS ARE NOT IN THIS FILE (S6).  The count moved
%%       under us mid-session and its denominator is used nowhere here, so the
%%       cold reader was handed a reassurance whose strength they could not
%%       judge.  §5 keeps it, with the corrected value and a gloss.
%%
%% FORBIDDEN HERE, and each was checked line by line before shipping: the
%% four-rung deleted-line table (§5's, and F6 states the result in one clause
%% with no table); the 7.26× naive-versus-tuned median (§3's); the hash probe's
%% +2 → +1021 and its 510× (§3's, "too scope-heavy for a bullet"); the coverage
%% table (§4's); the six-rung table (§1's — F1 quotes the spread, never a cell).
%%
%% ⚠ THE RUNG COUNT IS GONE from sentence two (supervisor S1).  This file said
%% "five rungs" and every other section says six; both are defensible, but one
%% pattern ships NO hardened rung, so no single count is true of the corpus.  A
%% briefing that must work detached should not open on a number no other section
%% supports.
%%
%% The last paragraph is unnumbered on purpose.  It is not a hedge and is not
%% written as one: it is what stops the findings above being misquoted, and it
%% ships the DIRECTION of each limit (CLAIMS.md §3.5).  This is the concurrency
%% statement's FIRST of exactly two appearances in the whole report; the second
%% is in §1's method paragraph.  There is no third.
%% ⚠ IT SAYS WALL CLOCK EXISTS (REVISE PART C item 5).  The cold reader's first
%% question of the author was "wall-clock is the only currency my VP accepts",
%% and the paragraph as written told them only that we do not use it.  "Every
%% COST figure" is rigour M16: §3 quotes wall clock three times, so the
%% corpus-wide form was false as written.

%% ⚠⚠⚠ THE FINAL CUT (target 6,200 prose words for the paper; the evidence for
%% that number is ver_B, which is 6,229 words and which the report's owner called
%% "easier to understand").  Its ruling for this file: 701 -> 520, "Tighten the
%% six findings.  NO FINDING IS CUT; each loses a clause."  Executed exactly:
%% every finding is still here, still numbered F1..F6, and the mapping recorded
%% at the top of this header is untouched.  ⚠ THE FILE LANDS ABOVE 520, and the
%% arithmetic is worth recording so the next pass does not try again with a
%% smaller knife: six findings carrying between two and five figures each, plus
%% two `Do:` lines, the hinge and the scope paragraph, do not compress past about
%% 600 words of plain phrasing without dropping a FIGURE, and every figure here
%% is either on the must-not-lose list or is the only copy in the paper.
%% WHAT EACH FINDING LOST, in restore order:
%%  F4  THE TWO CATCHES' DECOMPOSITION, ~16 words: "In the first, the allocator
%%      was 108.4% of the gap and its bounds check 3.0%, with the opposite sign;
%%      the second was 100% spelling."  ⚠⚠ RESTORE THIS FIRST OF ALL SIX.  Those
%%      figures — 6.02x, 108.4%, 3.0%, 9.6%, 100% spelling — appear NOWHERE ELSE
%%      IN THE PAPER: §2's worked example of them was cut two passes ago and §6
%%      is forbidden to cite them, so this bullet is their only home and the
%%      surviving summary of them is looser than the tree's own.
%%      ⚠ C13 STILL GOVERNS what replaced it: the licensed shape is "the
%%      measurement would have been wrong, and it was caught before publication",
%%      NEVER "the cost trap is why the row was refused" — both rows also die on
%%      duplication and the review rejected the first stated reason for one.
%%  F1  the gloss "— what the processor runs inside that one function".
%%      "Instructions per call" is already plain English; the gloss was
%%      belt-and-braces for a detached reader and is the cheapest thing here.
%%  F2  THE CENSUS CLAUSE, ~17 words: "This corpus is stacked toward bounds bugs,
%%      which makes three of ten the stronger result."  ⚠ RESTORE IT SECOND,
%%      after F4's decomposition.  Its evidence is `results/SYNTHESIS.md:877-883`
%%      (fourteen patterns carry an `index >= len` axis by construction) and it
%%      is what licenses the opening "It repeats" over the stronger "it
%%      generalises", which `:592-599` refuses in the tree's own voice.
%%      ⚠ IT IS NOT LOST FROM THE PAPER: §2's caveat states it on its own
%%      denominator, in the same words, beside the search-state evidence.  And it
%%      cuts in OUR DISFAVOUR to drop it — a reader of §0 alone now sees "three
%%      of ten" without being told the corpus is weighted toward bounds bugs, so
%%      the result reads weaker than the evidence supports, not stronger.
%%      ⚠ "It repeats", never "it generalises", regardless.
%%  F5  "for another reason" and one connective; the three-way split, the
%%      two-of-ten strict reading and the blind spot are all intact.
%%  F3, F6  wording only.  Both are on the must-not-lose list in full.
%% ⚠ THE SCOPE PARAGRAPH KEEPS "in both directions, and the report prints both".
%% §3 was cut to one wall-clock counterexample by the same ruling, so a
%% ONE-CLAUSE compiler pair was kept there deliberately to stop this sentence
%% going false.  If anyone cuts that clause, this one goes with it.
%% ⚠⚠⚠ THE UNDERGRADUATE PASS (.temp/brief/REVIEW-undergrad.md).  The paper's
%% target reader rated the draft 3/10 and the diagnosis is that it glosses its
%% OWN coined words (`rung`, `spelling`, `blob`, `landing pad`, `exit 101` — all
%% of which landed) and never glosses the words that exist in the world.  Changes
%% here, none of them factual:
%%   F1  `kernel` IS DEFINED, in its own sentence, at the first use in the paper.
%%       It was never defined ANYWHERE in the nine files, appears ~40 times, and
%%       the cold reader spent the whole document thinking it meant an operating
%%       system kernel.  This was their single most-requested change.
%%       ⚠ The *spelling* gloss also stopped being a mid-clause appositive: it
%%       "broke the sentence in half" and cost two reads.  Same words, own clause.
%%   F2  BOTH DENOMINATORS.  "ten of the fair pairs" had no denominator in the one
%%       file that must stand detached; §2 prints 22 and §0 did not.  And "42% to
%%       205% of a kernel that does nothing else" now says of WHAT — the reader
%%       read 205% as impossible until they guessed it was the unsafe version.
%%       ⚠ §2's mandated scope clause is intact: "kernels that do nothing else".
%%   F5  THE PAIR IS STATED ONCE, STRICT COUNT FIRST.  It led with five of ten,
%%       then conceded two of ten two sentences later, and the reader read the
%%       repetition as a tell: "leading with the 5 anyway, in three places, is not
%%       [honest]".  Both numbers still ship and FIVE is still here, which is what
%%       C31 protects; what changed is that the caution arrives with the number
%%       instead of after it, which is §3's own "publish the pair" rule applied to
%%       ourselves.  The reader's own suggested wording was "two, or five
%%       depending how you count".  ⚠ Do not restore the two-sentence form.
%%       `sanitizer` is glossed here — bare in §0, half-explained in §4.
%%   F6  "any version" added so the zero does not read as contradicting the exit
%%       101 zero above it; the reader took the two as a direct contradiction.
%%       `gate` is not §0's vocabulary (this file's own header bars the paper's
%%       vocabulary), so it says "our automated checking".
%%   F4  "publish a ratio" -> "quote the number": the cold reader was one of two
%%       places they felt talked down to ("I don't publish ratios.  Nobody in my
%%       year publishes ratios.").  The `Do:` line itself is untouched.
%% ⚠⚠⚠ THE THIRD UNDERGRADUATE PASS (.temp/brief/REVIEW-undergrad3.md), 5/10.
%% Nothing factual moved.  Two changes here:
%%   F1  ⚠⚠ THE `spelling` GLOSS IS BACK, AND THE NOTE ABOVE WAS FALSE.  This
%%       header has said "`spelling` is glossed HERE, at its first use in the
%%       paper" since the first undergraduate pass, and at some point between then
%%       and now the gloss itself was trimmed out of the bullet while the note
%%       claiming it stayed.  The third reader found it: "§0 is the part written
%%       to stand alone, and the word the summary turns on is undefined in it."
%%       It is now its OWN SENTENCE ("A *spelling* is one way of writing it"),
%%       which is the shape the first pass settled — never a mid-clause
%%       appositive, which "broke the sentence in half".  A LATER TRIM MUST NOT
%%       TAKE IT AGAIN: this file is the one that must work detached, and F1 is
%%       unreadable without it.
%%   F2  "**Those are two separate programs, not a range**" IS CUT, and this is
%%       a VOICE fix, not a content one.  The reader named three bolded "not X"
%%       pre-emptions across the paper (this one, and §3's two) and read them
%%       together as "we assume you were about to get this wrong".  The right
%%       reading now comes first instead — "one program's ... a different
%%       program's" — so there is nothing left to pre-empt.  ⚠ BOTH FIGURES AND
%%       §2's MANDATED SCOPE CLAUSE ("kernels that do nothing else") ARE
%%       UNTOUCHED, which is what the welding note above protects.
A safety number is a claim about what caused what, and both halves are usually
credited to the wrong thing. The cost you are quoted is usually not the bounds
check. The guarantee you assume is most often watching the edge of a block of
memory while the bug sits inside it.

%% ⚠⚠⚠ THE SECOND UNDERGRADUATE PASS (.temp/brief/REVIEW-undergrad2.md) ADDED THE
%% ORIENTATION PARAGRAPH BELOW, ~60 words, and it is NOT scaffolding.  The reader
%% rated the draft 4/10 and their single recommended change was to put §1's
%% opening and the ladder figure AHEAD of this file — "§0 asks me to hold −2545,
%% 0, +77 or +17123 and 3/5/1/1 of ten and 98.6% and 99.2% before I have a single
%% concrete picture to hang any of it on".  The order is fixed (paper.md's header
%% argues it), so the picture comes here instead.  ⚠ THE THESIS STILL LANDS IN THE
%% FIRST FORTY WORDS, which the header above requires: the three thesis sentences
%% run BEFORE the orientation, and the orientation runs before the findings.
%% ⚠ THE LADDER SENTENCE IS BORROWED FROM \ref{fig:ladder}'s caption — the reader
%% called it "the single clearest statement of what this project IS" and asked for
%% it as the second sentence of the document.
%% ⚠ "ALL BUT ONE" IS SUPERVISOR S1's CORRECTION KEPT: one pattern ships no
%% hardened rung, so "each is written six ways" would be false of the corpus.  Do
%% not simplify it back to a flat six.
%% ⚠ `kernel` IS DEFINED HERE NOW, not in F1.  It was defined six times across the
%% nine files in near-identical words and the reader reported that the repetition
%% "trained me to skip blocks that also contained new material".  This is the
%% paper's ONE early definition; §1 re-glosses it once and no other file may.
**What is underneath that.** \num{totals.patterns} small C programs, each a short
function with a deliberate memory bug — the **kernel**, and the only part we
measure. All but one program is written six ways. Unchecked C; C with the check added by
hand; safe Rust ported line for line; safe Rust tuned; unsafe Rust; and unsafe
Rust proved by machine. C starts unchecked and gains the
check by hand; Rust starts checked and has the cost taken out. Every cost figure
below is executed instructions per call, not seconds.

%% F1-F3: why the problem is hard.  No action clause on any of them.

- **F1.** Our kernel walks
  length-prefixed records. On one input, "the cost of
  memory safety" comes out as −2545, 0, +77 or +17123 instructions per call.
  Which you get depends only on which two *spellings* of that same kernel you
  subtract. A *spelling* is one way of writing it. Write both the same way and
  the rate per byte is exactly 0.00000.
- **F2.** It repeats. Subtracting one version from another is only fair when both
  call the same outside code, which holds for 22 of our \num{totals.patterns}
  programs. Ten of those 22 have a gap over 100 instructions per call. On three
  of the ten the bounds check is the main cost, and there it is not small: one
  program's checks cost 205% of what its unsafe version executes; a different
  program's cost 42%. The third is not priced, and all are kernels that do
  nothing else. The other seven: five where
  the cost is something else, one where nothing in our records explains it, and
  one where a line that provably never runs deletes almost all of the check.
- **F3.** Our own instrument leans one way on every comparison. We require each proved
  version to compile to exactly the same machine code as the unproved one, which
  rules out faster ways of writing the unsafe side. On one kernel the ruled-out
  way was 17,526 instructions per call cheaper on the large input, 35% of that
  kernel — a saving refused, not a cost added, which flatters safe Rust
  throughout.

%% THE HINGE.  One sentence, between F3 and F4.  Mandatory, Gate 2.

All three are one failure — a number or a guarantee credited to a mechanism that
did not produce it — and wherever the mechanism can be removed, one cheap
operation settles which it was.

%% F4-F5: why it is tractable.  Each ends in what it motivates.

- **F4.** Where it can be removed, removing it settles the attribution. One line
  that provably never runs deletes 98.6% of a bounded stack's gap on one input
  and 99.2% on the other — not all of it. Five
  instructions per call survive, and nobody has tried to remove them.
  Two comparisons would have gone out claiming safe Rust 6.02× and 9.6× cheaper: one was
  almost entirely the allocator, the other entirely spelling. Both were caught
  before publication.
  **Do:** remove the mechanism and re-measure before you blame safety or quote
  the number. Expect a per-call constant, often exactly zero, where the optimiser
  can already see what makes the check redundant — a clamp that pins the index
  into range, or a length the caller tested. Expect a cost on every element where
  it cannot.
- **F5.** Where it cannot be removed, name what the guarantee watches. Over
  twelve bug classes and four detectors, all four give the identical answer on
  **two of the ten classes** they all reach — or five, if you let two kinds of
  silence count alike. Two of the five are all four catching the bug. On the
  other three all four stay quiet — some having missed it, some never having
  looked. They are quiet where the bug never leaves the block of
  memory they watch, and on timing because they watch values while a leak is a
  property of the run. Almost every silence there is a guarantee that was never
  watching the bug. One is not. A *sanitizer* is a checking mode the compiler
  builds in, aborting the program on a bad access. One of those owned exactly
  the right check, and a hardening flag took the call off its path.
  **Do:** name what each of your own tools watches, and put a known-bad input per
  detector in the build you ship.

%% F6: the bound.  No "Do:" label, by design — see the header.

- **F6.** Exit 101 — what a Rust program returns when it *panics*, stopping
  rather than carrying on — appears zero times across
  \num{totals.patterns} programs and every hostile input. The only evidence a
  safe version's check is really there is the source code, and no stage of our
  checking reads source code. That bounds both findings above.

%% The scope paragraph, unnumbered.  Direction, not apology.

Zero of \num{totals.patterns} programs creates a thread. On four kernels here the
counter and the clock disagree, in both directions, and the report prints both.
Per-call constants transfer to your code. Fractions of our kernels do not,
because your function does other work.
