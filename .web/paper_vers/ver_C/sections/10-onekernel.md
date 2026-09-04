%% ver_C section 1 — the running example, the position, the method.  Written to
%% OUTLINE.md PART 1 §`10-onekernel.md`, beats 1–9, in order.
%%
%% ⚠⚠ PLAIN-LANGUAGE PASS (.temp/brief/PLAIN.md).  Rewritten for a reader who
%% knows C, has heard of Rust and has never used a verifier.  NOTHING FACTUAL
%% MOVED: every cell, every pair, the identity digest, the caveat's quotation and
%% the prior-work figures are as they were.  What changed:
%%   - long sentences split; median sentence is now under 20 words;
%%   - glossed at first use, because readers land here by hash route: `Ir` /
%%     instructions per call, *spelling*, *rung*, *blob* (in the caption),
%%     "mechanically ported" (= translated line for line), "in contract"
%%     (= still meeting the contract), "landing pad";
%%   - the machinery list dropped "driving every build against an independent
%%     reference", a THIRD duplication of the Method paragraph two lines below —
%%     the earlier two are recorded under rigour M9 further down.  The gate is
%%     still named and the independent reference is still stated, once.
%% ⚠⚠ THE CUT PASS (.temp/brief/CUT.md) then took the prior-work paragraph from
%% ~240 prose words to ~110 and the method paragraph to ~70 — the file's only two
%% rulings — and the file lands at ~780 against a 620 target.  CUT.md's own
%% instruction for everything else here is "Keep in full: the six-version table,
%% the four costs, the per-byte zero, the C rung that ships the bug, the
%% compiler-gap beat, the caveat", which is the whole remainder of the file.  The
%% remaining gap IS that keep list; closing it needs a ruling that drops one of
%% those six, not another trim.
%% ⚠⚠ ONE CONTRADICTION BETWEEN THE BRIEF AND A PRIMARY ARTEFACT, and the
%% artefact wins (authority order in CONVENTIONS.md).  RULINGS.md C3 and the
%% outline both say "a `chunks_exact(32)` safe fold is −199 / −2545 against the
%% shipped unsafe rung".  The hashed `why` block in
%% `results/tables/p16-tlv-walk.md:37` — which I opened — says instead:
%%   "the CHEAPEST FOUND in contract against the SHIPPED R4 is -199 (small,
%%    `chunks_exact(16)` or `(32)`) / -2545 (large, `chunks_exact(64)`)"
%% and, two sentences on: "`chunks_exact(64)` is 72 Ir/call DEARER than
%% `chunks_exact(32)` at `small` … so NO SINGLE SPELLING IS CHEAPEST ON BOTH
%% BLOBS and a cheapest-found figure must name its input as well as its
%% spelling (TASK_027)."  So −2545 is NOT a `chunks_exact(32)` number.  The text
%% below names the width with the input, which is what that block demands, and
%% keeps the load-bearing part of C3 intact — it is a SAFE fold, one exact-string
%% substitution from the shipped safe rung, zero `unsafe` tokens, cheaper than
%% the unsafe rung.  Supervisor: C3's parenthetical needs the same fix.
%%
%% ⚠ CUT FOR BUDGET, recorded so nobody thinks it was missed: on the SMALL blob
%% the cheapest found in contract is −199, at `chunks_exact(16)` or `(32)` — a
%% narrower width than the large blob's winner, and `chunks_exact(64)` is 72
%% Ir/call DEARER than `(32)` at small.  If this section ever gets words back,
%% that sentence is the first thing to restore: it is the reason a cheapest-found
%% figure must name its input as well as its spelling.
%%
%% ⚠⚠ RULING C3 GOVERNS THE OPENING.  `.tasks/TASK_007_REVIEW_REPORT.md` F1
%% (major) is that this project's own write-ups lead with the naive port's +69%
%% while the tuned safe rung's per-byte rate equals the unsafe rung's EXACTLY.
%% So the opening leads with the SPREAD — after a five-word framing sentence
%% naming the kernel, which the plain-language pass added and which states no
%% number — and +69% / +72% is named in the same sentence as the port it belongs
%% to ("the line-for-line port's number").  Do not re-promote it.
%%
%% ⚠ RULING C1.  The plain C rung SHIPS without the length test — `c/kernel.c:1`
%% reads "p16 rung R1 … THE BUG." and lines 51–54 are a comment standing where
%% the code would go; `c/kernel_hardened.c:35-36` is the rung that has it.  I
%% opened both.  Never "we deleted a line from each rung"; that framing is
%% `sec:nonoptional`'s to correct and its table is forbidden here
%% (OUTLINE PART 2).
%%
%% ⚠ Numbers re-derived, not copied: the eight table cells are
%% `results/synthesis.md:98-99` (machine-generated), which agrees cell-for-cell
%% with `results/p16-tlv-walk.json`'s raw callgrind totals ÷ call count (E1 §1.2,
%% every division exact).  gcc−clang = 1069 / 8933 is that file's own
%% `gcc-clang` delta table, marked LICENSED.  The identity digest
%% `852405e0fa438a9df19c778fb3eff314` and level `exact` are from
%% `results/gate/p16-tlv-walk.json` `identity[1]`, which I read.
%%
%% ⚠ RULING C8 is the antibody against the framing regression (OUTLINE §0.6): a
%% C-column finding with the same shape as the Rust-column ones.  The
%% `-fcf-protection=full` qualification is MANDATORY in the same passage —
%% `results/synthesis.md:58` forbids the unqualified comparison in as many words.
%%
%% ⚠ RULING C7 is the caveat, and it is the paper's own thesis arriving as a
%% limitation.  "No bucket" here is the census's own sentence
%% (`results/SYNTHESIS.md:153-155`), NOT the cross-pattern distribution, which
%% belongs to `sec:notthecheck` and is forbidden here.
%%
%% ⚠ RULINGS C24 / C25 / C26 govern the position paragraph.  The quotation
%% everyone was passing around is a SPLICE of two sentences from two pages; the
%% two quotations below were read by me from the rendered arXiv pages 7 and 8 of
%% `ref_papers/UserStudy.pdf` (CLAIMS.md §3.10 — never from the extracted text).
%% ⚠ CORRECTED AT REVISION: the p8 item is verbatim and carries quotation marks;
%% the p7 item is a PARAPHRASE and deliberately carries none.  This note used to
%% say "both are verbatim", which is how a later agent would have promoted the
%% paraphrase into quotation marks.  Agreement first, their counterweight in the
%% breath, then the gap sentence with "controlled difference", unqualified "cost
%% of memory safety" and "one C program against one Rust program" all dropped —
%% that last is literally false of the paper cited one sentence earlier.
%% C27: cite the PAPER as NDSS 2025, any PAGE as arXiv:2411.14174v2.
%%
%% ⚠ The concurrency clause in the method is its SECOND AND FINAL appearance
%% (`00-summary.md`'s last bullet is the first).  Do not add a third.
%%
%% ⚠ The handle table's allocator zero is licensed here for the agreement
%% paragraph ONLY and its decomposition belongs to `sec:notthecheck` (OUTLINE
%% PART 2).  Do not print the three terms.

%% ⚠⚠⚠ THE UNDERGRADUATE PASS (.temp/brief/REVIEW-undergrad.md), and this file
%% is the one the cold reader praised — "§1's opening two sentences … the reason
%% I kept going".  THE OPENING SPREAD SENTENCE IS UNTOUCHED, deliberately.  What
%% changed, none of it factual:
%%   * `kernel` DEFINED, in its own sentence, at the point the word first carries
%%     weight here.  It was undefined in all nine files and the reader read it as
%%     "operating system kernel" for the whole document.  The gloss replaces the
%%     old "The kernel (\pat{p16}) walks…", so the pattern marker is still there.
%%   * `fold` glossed where the kernel is described — the reader: "Used constantly
%%     and it's the actual operation being measured … In C I would call this a
%%     loop.  Nobody says that."
%%   * THE CAPTION SAYS WHY THERE ARE EIGHT ROWS FOR SIX VERSIONS.  "I counted the
%%     rows twice.  I now think it's because C is built with two compilers, but
%%     nothing says that and I was sure I'd misread something."
%%   * `precondition` glossed on the six-rung list, as a trailing appositive —
%%     the shape of the landing-pad gloss, which the reader called the best in the
%%     paper.  Every gloss added in this pass uses that shape.
%%   * THE IDENTITY SENTENCE was a three-read sentence ("I do not know what the
%%     gate is yet, what pins means, what an md5 hash is doing in a sentence about
%%     instruction counts, or what level `exact` is a level of").  Split in two,
%%     `pins` spelled out as what it does.  ⚠ THE DIGEST AND THE LEVEL BOTH STAY —
%%     they are the evidence that the zero is enforced.
%%   * THE −2,545 SENTENCE was the one the reader could not read at all: "I cannot
%%     read that sentence.  Not one clause of it."  Same four facts, two sentences,
%%     and `chunks_exact(64)` KEEPS ITS EXACT SPELLING because the artefact
%%     demands the width be named with the input (see the C3 note above).
%%   * `reslice` / `get_unchecked` replaced by what they DO, at no cost in words;
%%     `slice` glossed once, since it is used across four files.
%%   * "5.04688 to 6.62500" carries its unit — the reader asked "5.04688 of what".
%%   * THE CAVEAT'S ORPHAN QUOTATION IS GONE, and this is a CORRECTION, not a cut:
%%     "published as a minimum four times" is the count CLAIMS.md §3.8 calls "the
%%     STALEST version of this count", the supported form is §3's principle box
%%     ("five published minima … across three patterns, plus two more elsewhere"),
%%     and the reader flagged the quotation marks as having nobody attached
%%     ("Who said that?  Whose sentence am I reading?").  "Held by fiat" went with
%%     it; it was one of three near-identical phrasings of the same metaphor and
%%     the reader stopped at each to check whether it was the same claim.  The
%%     other two (§3's principle, §7's rule) stand.
%%   * THE METHOD PARAGRAPH NAMES **the model**.  §5 says "where the model exits
%%     0" three times and nothing connected it to this Python reference; the
%%     reader worked it out only at the end.
%% ⚠ TITLE REWRITTEN for the plain-language pass: "One kernel, four safety taxes,
%% and a per-byte rate of exactly zero" (12 words, two of them jargon — "taxes"
%% for a difference nobody levies, "per-byte rate" for a slope).  It is still a
%% claim and it still names the two numbers the section exists for: the spread of
%% four, and the zero.  Do not re-inflate it.
%% ⚠⚠⚠ THE SECOND UNDERGRADUATE PASS (.temp/brief/REVIEW-undergrad2.md), 4/10.
%% THE OPENING PARAGRAPH IS UNTOUCHED AGAIN — the reader named it as one of the
%% five passages the thesis actually came from.  Nothing factual moved.  Changes:
%%   * ⚠⚠ `row` IS DEFINED HERE, ONCE, FOR THE WHOLE REPORT, under the first
%%     table a reader meets.  It was the worst single problem in the paper: the
%%     reader found THREE meanings (a line of a table, one program-comparison, one
%%     (program, input) pair) and it sat in a section title.  The settlement is
%%     ONE SENSE — a line of a printed table — and every other use was reworded.
%%     §0, §2 and §3 no longer use the word for a comparison at all; §4 says what
%%     ITS rows are (one bug class) at the table that prints them.  ⚠ Do not
%%     reintroduce "on every row" for "on every comparison".
%%   * ⚠ THE `kernel` GLOSS HERE IS NOW THE PAPER'S ONE RE-GLOSS.  §0 defines the
%%     word in its orientation paragraph; §2, §4, §6 and §99 had near-verbatim
%%     copies and all four are cut.  The reader reported the sixth copy trained
%%     them to skip blocks that also carried new material.  Do not add a third.
%%   * `prover` and `obligation` glossed on the six-rung list.  They used to be
%%     glossed in §6 — "Being handed the two easy words at the end feels like the
%%     wrong half", after `md5_fn`, `identity level exact` and `510×` had all gone
%%     by unexplained.  §6's "Two words first" opening is cut.
%%   * ⚠ THE IDENTITY SENTENCE glosses `the gate`, `identity level` and `exact`.
%%     The reader skipped the digest entirely and said so.  THE DIGEST AND THE
%%     LEVEL BOTH STAY — they are the evidence that the zero is enforced — and the
%%     gate gloss here is what lets §6 drop its own.
%%   * ⚠ THE PER-BYTE PARAGRAPH NAMES ITS TWO QUANTITIES.  `0.00000` and
%%     `5.04688 to 6.62500` were both called "the per-byte cost" one paragraph
%%     apart; the first is the DIFFERENCE between two versions and the second is
%%     what one version costs.  Both figures are unchanged.  `residual` is not
%%     used here any more (§2 glosses it where it defines it); `slice` is glossed.
%%   * the caveat drops `census` and `cost bucket`, and says the +27/+77 bound in
%%     plain words: the reader was "still only 70% sure" what it claimed.
%%   * the handle-table sentence was the one the reader gave up on in this file
%%     ("I don't know what a missing symbol would be").  Same fact, plain words.
%%   * `mitigation` -> "a security feature"; the `-fcf-protection=full`
%%     qualification C8 makes mandatory is in the next sentence, untouched.
%% ⚠⚠⚠ THE THIRD UNDERGRADUATE PASS (.temp/brief/REVIEW-undergrad3.md), 5/10.
%% THE OPENING PARAGRAPH AND THE EIGHT-ROWS-FOR-SIX-VERSIONS CAPTION ARE
%% UNTOUCHED AGAIN — the reader scored this file 8, the highest in the paper, and
%% named both.  Nothing factual moved.  Three changes:
%%  1. ⚠⚠⚠ THE SAME-MACHINE-CODE RULE IS NOW JUSTIFIED, HERE, AT ITS FIRST USE
%%     IN THE BODY, IN THREE SENTENCES.  THIS WAS THE READER'S SINGLE
%%     HIGHEST-VALUE REQUESTED CHANGE and it repairs four sections at once.  The
%%     rule appears FIVE times in the paper — §0's F3, this digest sentence, §3's
%%     whole third subsection, §6.4's first bullet, §7's closing rule — and the
%%     only justification anywhere was §3's five words, "That keeps the proof
%%     honest".  The reader: "for four sections I was being told about the
%%     consequences of a design decision whose purpose I couldn't see, and the
%%     paper's own verdict on it is that it biases every number in the paper.  My
%%     reaction was: then why not drop it?"
%%     ⚠ WHAT THE THREE SENTENCES MAY NOT LOSE, in order: (a) what the rule buys
%%     — without it we would be pricing the PROOF'S EFFECT ON THE COMPILER rather
%%     than the cost of the code; (b) that a proof which moved the code could HIDE
%%     the difference being measured; (c) that we keep it KNOWING it costs us, with
%%     the \ref to §3, which is the section that prices the cost.  Part (c) is what
%%     stops the passage reading as a defence: the admission is still §3's and this
%%     only says the rule was chosen with the price known.
%%     ⚠ IT IS A RATIONALE AND CARRIES NO FIGURE, deliberately.  The −17,526 is
%%     §3's (redundancy map) and may not be imported here.
%%     ⚠ §3's opening lost "That keeps the proof honest, and" in the same pass and
%%     now \refs here instead; if this passage is ever cut, that clause goes back.
%%  2. "in no band" IS GONE from the caveat.  The reader: "Bands are never
%%     mentioned again anywhere.  I don't know what a band is, so I don't know what
%%     it means for this kernel to be in none."  Same fact — the census's own
%%     sentence at `results/SYNTHESIS.md:153-155` — said as grouping by gap size.
%%     ⚠ C7 IS UNTOUCHED: this is still the census's own count and NOT the
%%     cross-pattern distribution, which is `sec:notthecheck`'s.
%%  3. "not a missing symbol" IS GONE from the prior-work paragraph, ~4 words, and
%%     it is the SECOND time this clause has been rewritten for the same reader
%%     complaint ("I don't know what a missing symbol would be here or why I'd have
%%     suspected one.  This sentence is defending against an objection I didn't
%%     have").  The fact it defends is unchanged and is now said in plain words:
%%     the calls are present and equal on both sides, so the zero is equal work
%%     rather than an absent call.  ⚠ THE ALLOCATOR ZERO ITSELF STAYS — it is the
%%     paper's only meeting with `0.0000 Ir per call` and the one point on which we
%%     and \cite{userstudy25} agree by different methods.
\section{One kernel, four different safety costs, and zero per byte}
\label{sec:onekernel}

%% ⚠ `spelling` is glossed HERE, at first use in the body, not in the closing
%% section (REVISE PART C item 2). It is the paper's central unit of comparison,
%% this sentence is unreadable without it, and the cold reader needed three
%% passes to reconstruct it.
One 13-line C loop, written six ways. On its larger input, the difference
between two of those versions — what anyone calls the cost of memory safety — is
**−2,545, 0, +77 or +17,123 executed instructions per call**. Which of the four
you get depends only on which two *spellings* you subtract — two ways of writing
that one loop against one fixed contract. The largest is the line-for-line
port's number, the +69% / +72% that gets quoted. That loop is the **kernel**:
the one small C function we measure, and here it is \pat{p16}. It walks length-prefixed
records: read a three-byte header, believe the length on the wire, then *fold*
that many bytes — walk them and add them up.

| rung | small | large |
|---|---:|---:|
| plain, unchecked C, gcc | 4062 | 32694 |
| hardened C, gcc | 4079 | 32735 |
| plain, unchecked C, clang | 2993 | 23761 |
| hardened C, clang | 3017 | 23815 |
| safe Rust, ported | 5095 | 40921 |
| safe Rust, tuned | 3037 | 23875 |
| unsafe Rust | 3010 | 23798 |
| unsafe Rust, proved | 3010 | 23798 |

*Eight rows, six versions: plain and hardened C are built by both
compilers. Executed instructions inside the kernel function alone (`Ir`), per
call, at `-O3` with inlining suppressed, over the two committed input files —
the* small *and* large *blobs* \src{results/synthesis.md}.

%% ⚠ THE FINAL CUT dropped the prose gloss "That is what the processor really
%% runs inside the one function we measure" (13 words) from the opening: the
%% table caption immediately above it already reads "Executed instructions inside
%% the kernel function alone (`Ir`), per call", which is the same gloss attached
%% to the same number.  PLAIN.md's rule is that the bare SYMBOL is never used
%% unglossed on first use, and the caption discharges it.
%% ⚠ `blob` glossed in the caption above (REVISE PART C item 3): it appears ~20
%% times across the paper and was never defined anywhere.
%% ⚠ The "ships the bug" sentence is compressed to a clause: §5 states it in
%% full and this section already sends the reader there, and the cold reader
%% named the pair as near-verbatim duplication four sections apart.
A **row** in this report is always one line of a printed table. Each of those
six versions is a **rung**: one
spelling of one pinned **contract** — what the kernel must compute — not a
language. Plain, unchecked C carries the pattern's bug: this walker **ships**
without the length test, nobody deleted a line (\ref{sec:nonoptional}), and the
hardened rung adds it back by hand. *Mechanically ported* means translated line
for line. The top rung's proof covers every *precondition*, what the unsafe code
needs true before it runs; the **prover** is the tool that checks such a proof,
and each thing it must prove is an **obligation**.

\figure{ladder}{C starts unchecked and gains the check by hand; Rust starts checked and has the cost taken out.}
\label{fig:ladder}

%% ⚠ rigour M11: the 0 was presented as a discovery, in the opening sentence,
%% with the correction two sections away — but the gate's identity pin REQUIRES
%% byte-identity, so proved-minus-unsafe is zero by construction (CLAIMS.md §2.3
%% calls it a tautology). Saying so here is a BETTER opening, because it makes
%% the point that one of the four safety taxes people quote is a definition.
%% ⚠ rigour m4: the −2,545 is not a row in the table above and a reader hunts
%% for it. Named as not-a-row in the sentence that states it.
Naming the pairs. Mechanical port minus unsafe is **+2,085** small and
**+17,123** large. Tuned safe minus unsafe is **+27 (+0.897%)** and
**+77 (+0.324%)**. Proved minus unsafe is **0** on both. We enforce that zero.
**The gate** — the check every version must pass before we believe its numbers —
requires both to compile at `-O3` to one digest of the function's bytes,
`md5_fn 852405e0…`. It records that as identity level `exact`, its name for
byte-for-byte
\src{results/gate/p16-tlv-walk.json}.

Why that rule exists. Without it we would be pricing the proof's effect on the
compiler, not the cost of the code. A proof that moved the code could also hide
the difference we are trying to measure. We keep the rule even though it costs
us, and \ref{sec:bothends} prices what it costs.

%% ⚠⚠⚠ THE CAVEAT MOVED UP HERE, from the END of the file, and NOTHING IN IT
%% CHANGED — same six sentences, same +27 / +77, same C7 census sentence.  The
%% fourth undergraduate pass's #1 item under "things I needed earlier than I got
%% them": "I spent the whole section believing this was a representative program.
%% Finding out at the end that it was deliberately chosen to be weird
%% retroactively changed how I read the four numbers I'd just been given."
%% ⚠ WHY HERE AND NOT HIGHER.  The reader asked for "near the table", and this is
%% the EARLIEST point at which every term the box uses is already defined: the
%% *contract* two paragraphs up, "our own rule" in the paragraph immediately
%% above (the identity pin and its justification), and +27 / +77 named as a pair
%% in "Naming the pairs".  Put above the caption it would forward-reference all
%% three, which is the defect PLAIN.md's gloss rule exists to prevent — and it
%% would land the atypicality claim before the reader has the table it is about.
%% It now sits above the three paragraphs that supply the section's other
%% numbers (the −2,545, the per-byte zero, the compiler gap), which is what the
%% finding asks for: the caveat arrives BEFORE they are absorbed as typical.
%% ⚠ C7 IS UNTOUCHED and so is the "in no band" repair of the third pass.
\begin{caveat}{An instrument, not a typical case}
This project groups its patterns by how big the safe-versus-unsafe gap is. Its
own count puts this one in none of those groups. We picked it to
break the rule that safety is cheap where the optimiser can see the loop. Within
the contract we found no rewrite of the unsafe side that moves the number. So the
unsafe end of +27 / +77 is set by our own rule, not by a search. Do not
generalise the size.
\end{caveat}

The −2,545 is not a row above. It is a
**safe** version: the shipped safe rung with one string changed to
`chunks_exact(64)`, folding the large blob sixty-four bytes at a time. It meets
the contract, has no `unsafe` in it, and is cheaper than the unsafe rung.

The per-byte **difference** between the two — what anyone would call the bounds
check — is **0.00000 `Ir` per folded byte**, once both sides are written the same
way. That holds over six ways of writing the fold, with a largest error of 0.00
against any measured cell. Both versions take their *slice* of the buffer — a
pointer and a length, naming part of it — **outside** the fold loop, the safe one
checked and the unsafe not. What each version costs on its own is a different
quantity: across spellings that meet the
contract it ranges 5.04688 to 6.62500 instructions per folded byte
\src{results/tables/p16-tlv-walk.md}. The cost here is per record, and nothing
per byte.

The biggest number here is not about Rust. Plain clang beats the unsafe Rust rung
by 17 instructions per call small and 37 large. And gcc against clang on
identical C source is **1,069 and 8,933** `Ir` per call — **40× and 116× the
entire tuned-safe cost**. Part of that is a security feature, not code generation. gcc
defaults to `-fcf-protection=full` here, so every function opens with a landing
pad — an instruction marking a legal jump target — that clang's and rustc's
columns do not carry \src{results/synthesis.md}.

%% ⚠⚠⚠ THE CUT PASS (.temp/brief/CUT.md): THE PRIOR-WORK PARAGRAPH GOES FROM
%% ~240 PROSE WORDS TO ~110, BY RULING. "An undergraduate does not need the gap
%% sentence's full defence. Keep three things and nothing else: we agree with
%% them and measured it a different way; their own later section already found
%% memory-safe-but-wrong translations; nobody has priced safety as a *graded*
%% choice with the contract held fixed." All three are below. WHAT WENT, AND
%% WHAT TO RESTORE FIRST IF WORDS COME BACK, in order:
%%  (1) ⚠⚠ THE 20%-HEADLINE RECONCILIATION — rigour M9(1), and it is the first
%%      thing a reviewer holding the PDF does. Their p8 box reads "For Rust
%%      translations most similar to the original C code, the overhead is mostly
%%      within 20% and Rust is often faster", while our table prints +69% / +72%
%%      for the ported rung — an apparent 3.5x disagreement with the closest
%%      prior work. ONE SENTENCE CLOSED IT and that sentence is what was cut:
%%      the same page states their method — running time between entry and exit
%%      of `main`, averaged over 70 trials, on whole programs — against our
%%      kernel-exclusive per-call instruction count with inlining suppressed. I
%%      read page 8 of the rendered PDF myself (CLAIMS.md §3.10 forbids the
%%      extracted text). RESTORE THIS FIRST. Nothing below asserts anything the
%%      cut sentence was defending, but a reviewer will still ask.
%%  (2) the two page-sourced figures: the p8 VERBATIM quotation "Temporal safety
%%      is achieved mostly statically (95.6%), whereas spatial safety is mostly
%%      through runtime checks" (arXiv:2411.14174v2, p8), which carries quotation
%%      marks and its page, and their own counterweight a page earlier — 90.9% of
%%      the references used may require a runtime check on access (p7), a
%%      PARAPHRASE that deliberately carries no quotation marks. ⚠ An older note
%%      here said "both are verbatim"; that was wrong for the p7 item, and it is
%%      how a later agent would promote a paraphrase into a quotation.
%%  (3) "their variation is also human and after the fact", and the p8 quotation
%%      that supported it ("We did not ask users to measure or optimize for
%%      performance" — VERBATIM, restore with quotation marks and "(p8)").
%%  (4) the machinery list — "one pinned contract per pattern, flags supplied by
%%      the harness, and the *gate*, this project's per-pattern check over every
%%      rung". The Method paragraph below already names the gate's independent
%%      reference and its flags, which is why this was the cheapest cut here.
%% ⚠ WHAT MAY NOT GO WITH IT: the forward reference to \ref{sec:bothends} is
%% rigour M10 / Q1. The machinery answers "do the six rungs compute the same
%% function"; the objection is "is each rung a competent representative of its
%% class", and the paper's own answer is §3's. Without the pointer §1 overclaims
%% and §3 is orphaned — it was, before M10.
%% ⚠ C27: cite the PAPER as NDSS 2025, any PAGE as arXiv:2411.14174v2.
%% ⚠ The handle table's allocator zero STAYS. §2's handle-table decomposition was
%% cut by the same ruling, so this clause is now the reader's only meeting with
%% that figure, and §0's F4 note points here for it.
%% ⚠ THE FINAL CUT (target 6,200 prose words for the paper) took ~16 more words
%% off this paragraph, all of it wording.  CUT.md's three keep-items are still
%% here, each in its own sentence: we agree with them and measured it a different
%% way; their own later section already files memory-safe-but-wrong translations
%% as a correctness gap; nobody has priced safety as a GRADED choice with the
%% contract held fixed.  ⚠ THE ALLOCATOR ZERO STAYS — §2's handle-table
%% decomposition is cut, so this clause is the paper's ONLY meeting with
%% `0.0000 Ir per call`, and it is the point on which we and \cite{userstudy25}
%% agree by different methods.  Without it "where we overlap we agree" has no
%% evidence at all.  ⚠ THE FORWARD REFERENCE TO \ref{sec:bothends} STAYS (rigour
%% M10 / Q1): the machinery answers "do the six rungs compute the same function",
%% the objection is "is each rung a competent representative of its class", and
%% §3 is that answer.  Without the pointer §1 overclaims and §3 is orphaned.
The closest prior work measures 31 safe-Rust translations of 8 C programs by 33
participants \cite{userstudy25}. Where we overlap we agree, by a different
method: they count reference declarations, we count instructions. On a handle
table both versions call the allocator equally often, so it adds **0.0000 `Ir`
per call** to the difference. That zero is equal work, not a call that went
missing.
Their own later
section files memory-safe but wrong translations as a correctness gap. To our
knowledge no prior study prices memory safety as a **graded** choice across rungs
like these, with the contract **held fixed and independently checked** at every
one. \ref{sec:bothends} measures how far off each end is, which is why we quote
the pair and not the number.

%% ⚠ CUT TO ~60 WORDS BY THE SAME RULING. What went: "on inputs built to break
%% that pattern" (the adversarial inputs' design), and "on the cost in isolation"
%% (the upper bound's direction). Both are restated in §5 and §2 respectively.
%% ⚠ The concurrency clause is its SECOND AND FINAL appearance (`00-summary.md`'s
%% last paragraph is the first). Do not add a third, and do not cut this one: it
%% is the only place a reader is told what the corpus is not evidence about.
**Method.** \num{totals.patterns} patterns — small C kernels, each with a named
defect — built at every rung over two C compilers, two optimisation levels and
two inlining modes: \num{totals.cells} measured builds. Each is driven against
**the model**, a Python reference sharing no code with any kernel, then attacked
\num{totals.adversarial_runs} times. The unit is `Ir` inside the kernel symbol,
never across the whole program, with inlining suppressed, so each figure is an
upper bound. Nothing here is concurrent: zero patterns create a thread, so on
data races this report is evidence neither way.
