%% ver_C's close. Under 190 words, all scaffolding, and it is NOT a summary.
%%
%% ⚠⚠ PLAIN-LANGUAGE PASS. Same two questions, same artefacts, shorter
%% sentences. The one vocabulary change is deliberate and is recorded below.
%%
%% WHY TWO QUESTIONS AND NOT SIX ACTIONS. ver_B closed on a six-item list of
%% things to do. §6 is now ~1,000 words of exactly those, so the list would be the
%% same story twice — the redundancy this outline exists to stop (OUTLINE 0.5
%% item 4). This close restates the THESIS, narrower, and enumerates nothing.
%%
%% WHAT "NARROWER" MEANS HERE. `00-summary.md` states the thesis as a claim
%% about safety claims in general: a safety claim is an attribution claim, and
%% this corpus misattributes both halves. The close does not restate that. It
%% hands the reader the two questions the two halves reduce to, each named
%% against the artefact that earned it — the one running kernel for the cost
%% half, the detector table for the coverage half.
%%
%% ⚠ "built at six rungs" was cut from the first question on an accuracy check.
%% Three of the four costs on that kernel are differences of shipped rungs; the
%% fourth is a `chunks_exact` safe fold that is in contract and is NOT a shipped
%% rung (RULINGS C3). And "there is an in-contract respelling beside every rung"
%% would be false of this very kernel, which publishes no pair interval at all
%% because it has no admissible unsafe respelling that moves (C3, §1's caveat).
%% The wording says only that the answer comes out four ways on one kernel,
%% which is what the evidence supports. It also drops the word `rung` entirely,
%% so the close needs no gloss for it.
%%
%% ⚠ THIS IS NOT §6.2's ACTION. §6.2 tells an author what to PUBLISH (the
%% triple: the number, the pair of spellings, the side nobody searched). This
%% tells a reader what to ASK of a number somebody handed them. If the two ever
%% read the same, this one goes — §6 owns the actions.
%%
%% ⚠ NO NUMBERS, deliberately. The six-rung figures are §1's and the coverage
%% cells are §4's (redundancy map). The close names the artefacts and \refs
%% them; "four different costs" and "one of them in safe Rust's favour" are
%% shapes of the result, not cells of the table.
%%
%% ⚠⚠ `resource` IS NO LONGER IN THIS FILE, title or prose. It was here only
%% because the old Gate-1 title used it, and CONVENTIONS §4 gives the word one
%% home (§4) plus one licensed use outside it (§6.4). The plain-language title
%% asks what the tool WATCHES, which is the same question in a word an
%% undergraduate does not have to decode, and §6.4 now holds the single
%% licensed use uncontested. §4 still owns the concept.
%%
%% ⚠ `spelling` is gone too, and with it its gloss: the first question says
%% "two versions ... two ways of writing one kernel against one pinned
%% contract", which IS the gloss, in the sentence that needs it. No other term
%% on the re-gloss list — rung, pattern, Ir, obligation, trusted base — appears
%% in this file at all.
%%
%% ⚠ SECOND QUESTION, ACCURACY. It says "where four detectors go quiet
%% TOGETHER", not "they agree on four of six classes". Per RULINGS C16 the four
%% agree on four classes but agreement is not always silence — they agree by
%% CATCHING a write outside the object. The compression worth restating is the
%% shared-silence one, and its reason is three-way, not one: two rows compress
%% because all four range over the allocation, the timing row because they range
%% over values and not over the trace. "Each of them watches something the
%% defect never touched" is the form that is true of both cases; §4 owns the
%% distinction itself.
%%
%% ⚠ ENDS ON THE READER'S OWN CODE, NOT ON THE CORPUS. The last clause is
%% deliberately close to ver_B's, which was the one line of its close that
%% survived review: what you leave with is a question, not a number.

\section{Ask which two versions, and ask what the tool watches}
\label{sec:close}

%% ⚠ FINAL CUT, ~14 words, light as the ruling requires: "not claims about
%% safety, but things to establish about one number and one tool" went.  The two
%% questions below say what they are about in their own first six words, and this
%% clause described the close rather than the evidence.
%% ⚠ THE UNDERGRADUATE PASS (.temp/brief/REVIEW-undergrad.md).  THE TWO QUESTIONS
%% ARE UNTOUCHED — the cold reader named them as one of the five passages that
%% worked ("If the paper were four pages long and consisted of §0, §1, §5, §7 and
%% §99, I'd give it an 8").  The only change is one clause in the lead defining
%% `kernel`, which the questions use and which was undefined in all nine files.
%% ⚠ THE SECOND UNDERGRADUATE PASS (.temp/brief/REVIEW-undergrad2.md): the
%% `kernel` gloss added to the lead in the previous pass is CUT.  It was the sixth
%% near-verbatim copy in nine files, and the reader reported that the repetition
%% trained them to skip blocks that also carried new material.  §0 defines the
%% word in its orientation paragraph and §1 re-glosses it once.  The word still
%% appears in the first question below, where the sentence defines it in place
%% ("two ways of writing one kernel against the same fixed contract").
%% ⚠ THE TWO QUESTIONS REMAIN UNTOUCHED.
Two questions are left, each narrower than the finding behind it.

%% ⚠ CUT PASS (.temp/brief/CUT.md): light trim only, ~10 words. What went: "and
%% the choice is not a detail", an editorial clause that the four different
%% answers in the same sentence demonstrate. Nothing else here moved.

**Of any number offered as the cost of memory safety: which two versions is it the difference of**? Two versions are two ways of writing one kernel against the same fixed contract. On the one kernel this report runs on, the answer comes out four different ways, one of them in safe Rust's favour — and somebody chose both ends of each (\ref{sec:onekernel}, \ref{sec:bothends}).

**Of any tool that reports nothing: what does its guarantee actually watch**? Where four detectors here go quiet together, it is not because the defect is exotic. Each watches something the defect never touched, most often the allocation it never left. What a guarantee does not watch is still yours (\ref{sec:allocation}).

Neither question needs our machine, our pinning rules or our corpus. Both are answerable on the code in front of you, with the tools you already have — and neither answer is a number you can quote from here.
