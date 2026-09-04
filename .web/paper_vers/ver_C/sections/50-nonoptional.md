%% ============================================================================
%% 50-nonoptional.md — section 5. Writer's notes.
%%
%% ⚠⚠ PLAIN-LANGUAGE PASS. The owner's verdict on the previous wording was that
%% an undergraduate cannot read it, and the diagnosis was length: four review
%% rounds each ADDED a defence inside the sentence it defended. NOTHING FACTUAL
%% WAS DROPPED HERE. Every number, scope clause, provenance line and retraction
%% below is the one that was here before, in shorter sentences. Where a
%% qualification would not fit its sentence it moved to the NEXT sentence —
%% which CLAIMS.md §3.4 as amended licenses and prefers — or into these
%% comments. Before restoring any longer wording, read .temp/brief/PLAIN.md:
%% the length was the defect, not the caveats.
%%
%% TITLE. Under 12 words, still the section's claim, and still carrying the
%% second clause that is what this section costs us: it bounds the method §2
%% defines and §6 sells. The old 22-word title said the same thing.
%%
%% VOCABULARY (mandatory, not trimmable — the report is hash-routed and a
%% reader lands on `#nonoptional` cold, convention 2.10.3):
%%   `rung`   glossed once in the opening, then the prose says "version".
%%   `pattern` glossed as "a small C program with one deliberate bug".
%%   `the gate` glossed where the argument turns on what it does not read.
%%   `instructions per call` glossed in place at its one appearance (6.00).
%%
%% ⚠ ONE DEPARTURE FROM THE OUTLINE, DECLARED FOR THE SUPERVISOR.
%% OUTLINE beat 7 ("why one missing test is unbounded", ~60 w, ruling C5) is NOT
%% printed. The budget could not carry it once the deleted-line table went from
%% four rows to five (C30) and C22's three unsmoothed qualifications landed;
%% nothing else in the section is optional. I verified the analytic claim at
%% source anyway (patterns/p16-tlv-walk/c/kernel.c:47-62 — the cursor advances
%% by `3 + vlen >= 3` and the exit test is `end - p >= 3` on `size_t`, so once
%% `p` passes `end` the difference wraps and the walk cannot stop short of a
%% 2^64 wrap) and it is available if a later pass reallocates words here.
%% ⚠ C5 requires the 200.0 MiB / 6,459-record probe illustration to travel with
%% its "the probe places the blob in a 256 MiB mapping so the walk has somewhere
%% to go" caveat. Dropping the pair together is safe; printing the measurement
%% without the caveat would not have been. If §5 regains words, restore BOTH.
%%
%% REDUNDANCY MAP compliance (OUTLINE PART 2):
%%   * No cell of §1's six-rung table appears here, and no Ir figure for the
%%     walker at all. We share a pattern with §1, not an artefact.
%%   * HOME here: totals.loud = 0, exit 101, the 1099 groups, the single hang,
%%     hardened C matching everywhere, the two wins with no cost axis.
%%   * "not one bounds check fires anywhere in the shipped matrix" appears ONCE
%%     in this file, in the TAKEAWAY, which is the box a reader quotes (C33).
%%     Do not also put it in the caveat: carrying it in both was 11 words of
%%     verbatim repetition inside one section.
%%   * FORBIDDEN here and absent: the fortification blinding, the range parser,
%%     the hardening median and the 2048-entry validation pass, the identity
%%     pin's −17,526, the concurrency scope, the word `resource`.
%%   * "remove the mechanism and re-measure" is DEFINED in §2; §5 BOUNDS it and
%%     must ADD something. The addition: §2's bound is a hypothetical (a zero
%%     could be a deleted check or two rungs that compiled alike); §5's is
%%     observed — the corpus has no independent witness for the safe side at
%%     all, and the one control that would be it is out of gate.
%% ============================================================================

%% ⚠⚠⚠ THE UNDERGRADUATE PASS (.temp/brief/REVIEW-undergrad.md).  This file's
%% five-row deleted-line table is what the cold reader called "the best table in
%% the paper by a distance" and it is untouched, as are the caveat, the quotation,
%% the population paragraph and the takeaway's scope clauses.  Nothing factual
%% moved.  Four terms are glossed, all four on the reader's never-explained list:
%%   * **the model** — used three times here and never connected to anything.  §1's
%%     method paragraph now names it at the point it is introduced; this is the
%%     gloss at the point of use, because a reader lands on `#nonoptional` cold.
%%   * **invariant** — the last table row's diagnostic turns on it, and the
%%     sentence explaining WHICH invariant assumed the reader knew what one is.
%%     C2's both-halves requirement is intact: the inner value-fold loop's, not
%%     the outer walk's, and "prints the correct checksum" is still marked vacuous
%%     for the row that never builds.
%%   * **borrow checker** — "a committed control produces three borrow-checker
%%     errors" was the whole evidence for one of the two wins.
%%   * **Miri** and **the prover** — the reader read that closing sentence three
%%     times and counted four unknowns in it.  ⚠ C19's verb rule still binds and
%%     is unchanged: "Miri reported nothing", never "Miri certifies it clean".
%% ⚠ `strict-aliasing` is deliberately NOT glossed: the sentence already says what
%% the rule is ("no type-based aliasing rule to unlock") and the words to buy a
%% fuller gloss were not there.  Next pass, if the budget grows.
%% ⚠⚠⚠ THE SECOND UNDERGRADUATE PASS (.temp/brief/REVIEW-undergrad2.md), 4/10.
%% THE FIVE-ROW DELETED-LINE TABLE IS UNTOUCHED — "the best thing in the paper …
%% I understood it completely, on one read, with no glossary."  So are the caveat,
%% the quotation, the population paragraph and the takeaway.  Nothing factual
%% moved.  Three changes:
%%   * ⚠ THE `pattern` / `rungs` GLOSS BLOCK IS CUT and the `panic` gloss with it.
%%     §0 now defines `panic` where exit 101 is first stated ("stopping itself
%%     rather than carrying on") and §1's method paragraph glosses `pattern`; this
%%     file's copies were the fifth and second.  ⚠ rigour M12's ATTRIBUTION FRAME
%%     SURVIVES: "these programs — each one a deliberate bug written six ways" and
%%     "across all N of them" are both still on the zero, which is what M12 asks
%%     for.  ⚠ `the gate` and `the model` are still glossed here, and both are the
%%     paper's one licensed re-gloss for those words.
%%   * ⚠ 1,099 GETS ITS DENOMINATOR.  "I read the gloss and I still don't know if
%%     1,099 is a lot.  Out of what?  4,104 runs is in the same paragraph."  It is
%%     4,104, and the sentence now says so.  ⚠ THE COUNT ITSELF IS UNCHANGED and
%%     its `literal-ok` waiver above still applies.
%%   * "It is inadmissible only because…" names its subject.  The reader gave up
%%     on that sentence: "What is 'it'?  Inadmissible TO WHAT?"
%% ⚠⚠⚠ THE THIRD UNDERGRADUATE PASS (.temp/brief/REVIEW-undergrad3.md), 5/10.
%% THIS FILE SCORED **8**, joint-highest with §1.  THE FIVE-ROW DELETED-LINE TABLE
%% IS UNTOUCHED FOR THE THIRD PASS RUNNING — "the best thing in the paper … I
%% understood it completely on one read with no glossary and it made the point
%% better than the three sections before it."  So are the caveat under the outcome
%% figure (which the reader singled out as the paper telling them its headline
%% comparison is partly rigged by construction), the quotation, the population
%% paragraph and the takeaway.  Nothing factual moved.  Four changes:
%%  1. ⚠⚠ `strict aliasing` IS GLOSSED, ONE CLAUSE, and the note above saying it
%%     was "deliberately NOT glossed … next pass, if the budget grows" is
%%     DISCHARGED.  The reader: "I've heard 'strict aliasing' in a lecture and
%%     could not define it.  This is one of only two claimed wins in the section
%%     and I can't evaluate it."  The gloss is the rule itself — a C compiler may
%%     assume two pointers of different types never name the same bytes — and the
%%     claim after it is unchanged: Rust has no such rule, so there is nothing for
%%     a Rust version to break.  ⚠ It does NOT say Rust cannot miscompile, and it
%%     does not touch the qualification below it that `unsafe` re-opens the win.
%%  2. ⚠⚠ "its loop flipped" IS SAID IN PLAIN WORDS, and the direction is the
%%     tree's, not a guess.  `patterns/p08-overlap-move/NOTES.md:669-683`, §5c
%%     "Control 3 — safe, compiles, does not panic, and wrong": `fwd_loop.rs` is
%%     `safe_naive.rs` with `for j in (0..m - dr).rev()` -> `for j in 0..m - dr`,
%%     ONE SUBSTITUTION, and the file's own sentence is "Write the loop in the
%%     wrong direction and the buffer is replicated instead of shifted — safely,
%%     silently, exit 0."  The prose now says that.  ⚠ "is simply wrong" was the
%%     old ending and the reader asked "Flipped how?  Reversed?  Inverted
%%     condition?"; naming the outcome answers it and costs eight words.
%%  3. THE 1,099 SENTENCE NAMES WHAT REPEATED.  "the rest repeated one" — the
%%     reader: "The rest of what repeated one what?"  Same count, same
%%     denominator, same `literal-ok` waiver.
%%  4. THE PROVENANCE SENTENCE IS SHORTENED, ~9 words.  The reader stopped reading
%%     the provenance formula after its third appearance ("reproducible from a
%%     committed generator, certified by no gate" reads as ritual), so it ships in
%%     FULL at its first use — §2's clamp box — and short here.  ⚠ BOTH CLAUSES
%%     SURVIVE, which is what C30 and CLAIMS.md §1.21 require: a committed
%%     generator, and no gate.  What went is "rebuilt and re-run … that retypes no
%%     build flag"; the generator is still named by \src and still committed.
\section{Nothing here ever panics, and no gate reads the check}
\label{sec:nonoptional}

%% BEAT 1 — RULING C20, the strongest fact in the report. The numbers come
%% first, before any framing (convention 2.2), and were derived twice,
%% independently, from results/gate/*.json (E4 B14) — not read back out of
%% .web/data/.
%% ⚠ 1,099 has no \num{} path: data/index.json publishes the key count (1026)
%% and the run count (4104), not the behaviour-GROUP count. Declared below so
%% the literal check is not silent about it.
%% ⚠⚠ IT WAS 1,098 AND THE TREE MOVED UNDER US (fact-check §1.2, supervisor S6).
%% Six gate records were rewritten between 19:03 and 19:11 and one class went
%% 143 -> 144. I re-counted all 26 `results/gate/*.json` `adversarial` maps
%% myself after that and get 1,099 groups over 4,104 runs, per pattern
%% p01 42 p02 58 p03 44 p04 24 p05 38 p06 48 p07 40 p08 32 p09 24 p10 32 p11 40
%% p12 51 p13 68 p14 47 p16 24 p17 48 p18 40 p19 40 p22 40 p23 53 p27 44 p36 32
%% p38 45 p42 80 p46 33 p47 32. THE ZERO IS UNAFFECTED — the exit-code histogram
%% over all 4,104 runs has no 101 in it at all, not merely none among the Rust
%% rungs. §0 dropped the count entirely rather than carry a second copy of a
%% number whose denominator it never used (S6); this file is its only home, and
%% it is glossed, because a cold reader could not judge the strength of a
%% reassurance measured in a unit nobody had defined.
%%literal-ok 1099  behaviour groups; data/index.json publishes keys and runs, not groups
%% ⚠ Four different units are all called "a row" upstream (E4 B9). Every number
%% in this paragraph names its unit.
%% ⚠ rigour M12: this reads as a fact about Rust panics unless it sits inside
%% the attribution frame, and `#nonoptional` is a URL a reader can land on cold.
%% The opening sentence is that frame; it is not scaffolding, it is the scope.

%% ⚠ CUT, 17 words: "Section \ref{sec:notthecheck} asked what a cost pays for.
%% This section asks whether the check is there at all."  It describes the paper
%% rather than the evidence, which is PLAIN.md's named cuttable category, and the
%% \section title says the same thing four words above it.  ⚠ rigour M12's
%% attribution frame is NOT this sentence — it is the *pattern* gloss and the
%% "across all N of them" scope on the zero, both of which stand.
Across all \num{totals.patterns} of these programs — each a deliberate bug written six ways — on every hostile input, **exit code 101, the panic exit code, appears zero times**. \num{totals.loud|plain} of \num{totals.adversarial_runs} hostile runs end with a version refusing to continue where the model exits 0 \src{results/gate/*.json}. The *model* is our separate Python implementation of the right answer. Those \num{totals.adversarial_runs} runs produced only 1,099 distinct outcomes between them; every other run repeated one already counted.

%% BEAT 2 — C20's positive half, which the ruling calls stronger than "the check
%% fires". The 6-of-129 bound is welded to the zero it bounds, so it counts F
%% and not L (GATE 3's rule); 129 is totals.plain_c.rows, one (pattern, input)
%% pair, the same unit as the sentence it qualifies.
%% ⚠ m2: the step from "the model exits non-zero" to "the kernel is not reached"
%% is the driver's pre-kernel rejection. It is an inference, not arithmetic, and
%% it is now stated in the clause that uses it rather than a paragraph earlier.

%% ⚠⚠⚠ THE FINAL CUT (target 6,200 prose words for the paper): **THE "STRONGER
%% THAN THE CHECK FIRES" BEAT IS CUT**, 94 prose words, by ruling.
%% WHAT IT SAID: "**Stronger than 'the check fires':** on the inputs that reach
%% the kernel, the safe versions just compute the model's answer.  On the
%% corpus's one hanging program, both plain-C compilers hang in all four builds,
%% while every Rust version and both hardened-C versions return that answer at
%% exit 0.  Safety here is a right answer that terminates, not an abort.  The
%% model itself exits non-zero on 6 of \num{totals.plain_c.rows} (pattern, input)
%% pairs; there the driver rejects the input before the kernel runs, so no check
%% of ours fires.  So the zero covers the 123 pairs that do reach it — 95%."
%% ⚠⚠ THE 6-OF-129 BOUND WENT WITH THE CLAIM IT BOUNDED, WHICH IS WHY THE BEAT
%% HAD TO GO WHOLE.  It was welded (GATE 3's rule) and printing either half alone
%% would be worse than printing neither: the positive half without the bound
%% overclaims, and the bound without the positive half bounds nothing.
%% ⚠ WHAT THE ZERO STILL SHIPS WITH, one paragraph up: "on every hostile input",
%% \num{totals.loud|plain} of \num{totals.adversarial_runs} runs, and the 1,099
%% behaviour groups with their gloss.  The zero is not left bare.
%% ⚠ WHAT IS LOST BESIDES THE WORDS, so a restorer can price it: this file was
%% the redundancy map's HOME for the single hanging program and for hardened C
%% matching the model everywhere, and neither now appears in the paper.  The
%% second is a coverage-bias item — it runs AGAINST the paper's Rust column —
%% and CLAIMS.md §2.4 leans on it ("hardened C matched the model everywhere").
%% RESTORE THIS BEAT AHEAD OF ANYTHING ELSE IN THIS FILE.

%% BEAT 3 — figure, then caveat, in that order and AFTER the headline. The
%% caveat is carried from ver_B; three reviewers named it load-bearing.
%% ⚠ BOTH LIMITS ARE NOW IN THE CAVEAT, and the caption is one line. They used
%% to be split — the design-choice limit in the caption, the scoreboard's
%% blindness in the caveat — and each needed its own "this table does not say
%% X" preamble, which was ~15 words of repeated framing. Neither limit is lost;
%% they are two sentences of one box, immediately under the figure they bound.
%% ⚠ \figure{}{} MUST BE ON ONE LINE — a wrapped one vanishes silently and takes
%% its \label with it. Two figures shipped that way once.

\figure{outcomes}{The worst thing each version did on any hostile input.}
\label{fig:outcomes}

\begin{caveat}{What the outcome table does not measure}
\ref{fig:outcomes} does not say "Rust catches it". The Rust versions are the fixed program and the plain C one carries the bug, so it counts a design choice as much as a language difference. Its scoreboard compares only exit code and printed output, so a memory leak and a timing leak both score as matches. No deviation is not the same as no bug.
\end{caveat}

%% BEAT 4 — the consequence, unhedged, cited as F10. Every clause is E4 B14,
%% established by grepping harness/check.py and harness/asm.py rather than by
%% reading a write-up. The identity-pin clause is spelled out as "compile alike"
%% rather than named, which glosses it and shortens it at once.
%% ⚠ PART 5 item 3 and C20: DO NOT print a total for the identity pairs. The
%% arithmetic (52 + 2) is the paper's, not the tree's, and the claim that
%% matters is the negative, which needs no count of ours.

%% ⚠ FINAL CUT, ~18 words: one of the five gate gaps — "the idiom declaration,
%% which constructs a version must use, never fails on its `required` half".  The
%% other four stand, and the claim §6 \refs here ("\ref{sec:nonoptional} lists
%% what ours never reads") is still a list.  ⚠ EVERY CLAUSE HERE WAS ESTABLISHED
%% BY GREPPING harness/check.py AND harness/asm.py, not by reading a write-up
%% (E4 B14); restore from there, not from a summary.
**That zero bounds our own method**. A check that never fires cannot be caught working, so the only evidence it is present is the source text — and no stage of our gate reads source. Nothing looks in the machine code for a compare, a branch or a panic; nothing scans a safe version for `unsafe`; **nothing requires a safe version and an unsafe one to compile alike**. The hostile-input stage records what happened without demanding anything (**F6**).

%% BEAT 5 — the tree's own worry, quoted rather than buried (convention 2.8).
%% ⚠ The literal 129 inside a QUOTATION collides with totals.plain_c.rows and
%% would warn. It is quoted text and may not be rewritten as \num{}.
%%literal-ok 129  inside a verbatim quotation from results/SYNTHESIS.md

\begin{quote}{results/SYNTHESIS.md}
a tree with 129 adversarial pairs and ZERO Rust-rung divergences may be telling you the harm inputs are not adversarial ENOUGH. Nobody has tested that reading.
\end{quote}

%% BEAT 6 — the deleted-line table, FIVE rows (C30). It lands here and not in §1
%% because its force is that it is the corpus's committed, re-runnable witness
%% for the panic (OUTLINE §0.2 said "only"; see the correction below, which is
%% why the prose claims committed-and-re-runnable and nothing more).
%% ⚠⚠ RULING C1 IS THE MOST LIKELY FACTUAL ERROR IN THIS FILE. The plain C rung
%% SHIPS the omission — c/kernel.c:51-54 is a comment standing where the test
%% would go, and the file's header reads "THE BUG". NEVER "delete one line from
%% each rung". Only the Rust rungs had a line deleted.
%% ⚠ Every row read from insights/p16control.json, the generator's committed
%% output, which I opened directly; the five outcomes reproduce E1 §2 and E6.
%% ⚠ Exit-code spelling: only rc −11 appears, with SIGSEGV beside it, so the
%% tree's other spelling (139 = 128 + 11) cannot cause an inconsistency here.
%%
%% ⚠⚠ A5 / C33 / rigour B5(i): "ONE control in the corpus witnesses that panic"
%% is FALSE. results/SYNTHESIS.md:548-556 records a buffer copy's, in the tree's
%% own voice — "the control is what makes it a measurement rather than an
%% assertion" — and .memory/01-ladder.md:936-947 records a range parser's.
%% CLAIMS.md §1.6 is the honest population: EIGHT patterns carry the control, it
%% panics on four, is conditional on two, and is FALSE on two — one stripped
%% safe rung is bit-identical in output to plain C on every adversarial input,
%% and another hangs with every detector silent. That population is printed
%% below and may not be dropped: building this argument on the single most
%% favourable case is the coverage-bias failure mode, committed by the section
%% whose job is to bound the paper's own method. The claim here is only that
%% this control is the one that is committed and re-runnable, which is true.

**One control here strips the Rust versions only**. The walker \pat{p16} **ships** the omission in C — a comment stands where the test would go — so nothing was deleted there. The Rust versions all ship the check, and those are what the control deletes a line from.

| the same omission | on the overrun input |
|---|---|
| plain C — the version that **ships** it | rc −11, SIGSEGV, both streams empty |
| unsafe Rust, line deleted | rc −11, SIGSEGV, **identical to C** |
| safe Rust naive, line deleted | rc 101, `index out of bounds: the len is 3072 but the index is 3072` |
| safe Rust tuned, line deleted | rc 101, `range end index 7107 out of range for slice of length 3072` |
| the proved version, line deleted | **will not build**: `9 verified, 1 errors`, `invariant not satisfied before loop` |

%% ⚠ C2, both halves. Say WHICH invariant — the inner value-fold loop's, not the
%% outer walk's. And "prints the correct checksum" is VACUOUS for the last row,
%% which is the row's whole rhetorical value: no build, no run, no input. The
%% word "vacuous" is now spelled out for a reader who has never met it.
%% ⚠ C30's fifth row is new evidence the plan did not know about, and the point
%% is diagnostics, not whether the rung stops.
%% ⚠ "9 verified, 1 errors" is quoted as a build diagnostic, not leaned on as a
%% magnitude; §6.4 carries the "N verified counts items" gloss once, for the
%% whole paper.

**"Safe Rust panics" is true here; "Rust panics" is not**. The unsafe version's deletion segfaults exactly as C does. Both safe versions abort, but the tuned one names the length the attacker declared rather than the wall it hit — a difference in disclosure, not in stopping. The last row fails on an *invariant*: something the prover must show holds every time round a loop. That loop is the inner byte-folding one, not the outer walk. Every version that builds still prints the correct checksum on well-formed input — an empty promise for the last row, which never builds and so never runs.

%% ⚠ RULING C30 on provenance, and it moved in the good direction this round.
%% The wording is "reproducible from a committed generator; not gate-certified"
%% (CLAIMS §1.21). ver_B's disclaimer — "no committed generator, does not
%% survive a clone" — is now FALSE and must not be reinstated. The second
%% clause stays: the parent's gate does not run this, and its clause-deletion
%% stage deletes SPEC clauses, so none of its mutants is this test.

Provenance: the C row is the shipped version, gate-certified in all four build cells. The Rust rows are deletions from those sources, re-run from a committed generator and certified by no gate \src{.web/insights/p16_control.py}.

%% ⚠⚠ THE POPULATION. Without it this table is the corpus's single cleanest case
%% standing for a general claim (C33 item 3, bias review §3.3, CLAIMS.md §1.6).
%% It converts the section's weakest claim into a second instance of the paper's
%% best habit, and it is the one paragraph here that must not shrink further.

**The corpus disagrees with itself about what deletion proves**. Eight patterns carry this control. On four, deletion turns silent corruption into a panic. On two it depends on the input. On two it does not fire at all: one stripped safe version prints C's exact answer, and another hangs, with every detector silent \src{patterns/p18-varint-shift/NOTES.md}.

%% BEAT 8 — RULING C22. Compressed into short sentences, but not one of the
%% three qualifications is smoothed: safe-rungs-only, UB-not-bug, and the
%% analogue WAS BUILT.
%% ⚠⚠⚠ THE CUT PASS (.temp/brief/CUT.md) CUT THE UNDER-CREDITING DISCUSSION,
%% ~65 prose words, and gave the reason: "It is our own framing, it is contested
%% in the tree, and it costs 120 words to state honestly."
%% WHAT WENT, and it was four sentences: that neither win can show up in a count
%% of instructions and therefore **we** say a cost-only instrument under-credits
%% safety; that the tree declines that step in its own voice — *"it is not a
%% score"*, results/SYNTHESIS.md:597; that the tree uses THIS SAME PATTERN
%% against the claim next door, that only compare-and-branch properties can be
%% priced; and that it prices one at exactly 6.00 Ir/call, kernel-exclusive. The
%% title clause "— a fact about our instrument" went with them.
%% ⚠ WHAT SURVIVES IS THE HALF THAT IS NOT OURS: both wins, all three
%% qualifications unsmoothed, and the plain sentence that neither shows up in an
%% instruction count. What is gone is the INFERENCE from that fact and the
%% in-tree rebuttal of it — which had to travel together, and did.
%% ⚠ RESTORE BOTH HALVES OR NEITHER. Printing "a cost-only instrument
%% under-credits safety" without the tree's refusal is the exact defect the
%% paragraph was written to avoid, and three generalisations over the refusal set
%% have already died.
%% ⚠ C19's verb rule still applies to the surviving Miri clause: "Miri reported
%% nothing", never "Miri certifies it clean".
%% ⚠ C19's verb rule applies to the interpreter: "Miri reported nothing", never
%% "Miri certifies it clean".
%% ⚠ PART 3 item 2 — provenance on every quoted mutant. The E0502 result comes
%% from the pattern's own committed controls/gen_controls.py (re-run by the
%% evidence agent: exit 1, exactly 3 x error[E0502]); it is NOT gate pass/fail,
%% which is why the prose says "a committed control" and claims nothing more.
%% ⚠ rigour M12 again: the subject of the opening sentence is the INSTRUMENT,
%% not Rust. That is what the section is about, and the recast is deliberate.

%% ⚠ THE FINAL CUT: "Compress the two-wins paragraph to three sentences, keeping
%% ALL THREE QUALIFICATIONS."  The qualifications are three sentences on their
%% own, so the compression fell on the two wins and the framing, ~14 words; each
%% qualification is still its own sentence and none is smoothed.  C22 is intact:
%% safe-rungs-only, UB-not-bug, and the analogue WAS BUILT.
%% ⚠ C19's verb rule still binds: "Miri reported nothing", never "Miri certifies
%% it clean".  ⚠ The E0502 result is the pattern's own committed
%% controls/gen_controls.py — exit 1, exactly 3 x error[E0502] — and is NOT gate
%% pass/fail, which is why the prose says "a committed control" and no more.
**Two wins here have no cost column at all**. An overlapping `memcpy` does not compile in safe Rust: a committed control produces three errors from the borrow checker, the part of the compiler that stops two names writing the same memory. No Rust version brings back the strict-aliasing miscompile either: C lets a compiler assume two pointers of different types never name the same bytes, and Rust has no such rule. Neither win shows up in a count of instructions. Three qualifications. The aliasing win is the safe versions' alone: `unsafe` re-opens it and the proof does not close it. Safe Rust prevents the undefined behaviour, not the bug: a control with no `unsafe` in it, its copy loop run forwards instead of backwards, quietly replicates the buffer instead of shifting it. And the exact Rust version of that bug **was built**, defined and correct, with Miri reporting nothing. That version cannot ship as a rung here, only because our prover cannot express what it would have to prove.

%% BEAT 9 — takeaway (convention 2.5: scope + claim, no implication in the box
%% beyond the pointer to the §6 subsection that spends it).
%% ⚠ No hardening numbers here — the median and the validation pass are §3's.
%% F4 is cited without a figure, which the redundancy map permits.
%% ⚠⚠ THE TAKEAWAY CARRIED THREE OVERCLAIMS AND ALL THREE ARE FIXED (C33,
%% rigour B5, M13). It is the box a reader quotes, so it is where the scope has
%% to be, not two paragraphs up.
%%  (i)  "No check in this corpus was ever observed working" is refuted forty
%%       lines above it by this file's own table, and by §4 grading a runtime
%%       check `yes` on two rows. The scope is "the SHIPPED matrix", and it is
%%       in the box.
%%  (ii) "the impossibility of omitting it" generalises over a control that is
%%       false on two of the eight patterns carrying it. Scoped to what the
%%       corpus measures, which is CLAIMS.md §2.4's own form.
%%  (iii) §3 prices hardening in the C COLUMN; importing that median to price
%%       "the check in either language" called §2's +48,885 row small.
%%       The qualifier names the column and points at the exception.
%%       ⚠ THIS USED TO CITE **F4**, and the cut pass (.temp/brief/CUT.md) took
%%       the hardening median out of the summary "to section 3", so F4 is now
%%       the remove-and-re-measure finding and the citation would resolve to the
%%       wrong claim. It points at \ref{sec:bothends}, which is the finding's
%%       only remaining home. Same for §6.1's hardening bullet.
%%       ⚠ The **F10** citation in beat 4 is now **F6** for the same reason: ten
%%       findings became six and the exit-101 bound is the sixth.
%% ⚠⚠ (iii) AGAIN, AND IT READ AS A CONTRADICTION OF §2 (fourth undergraduate
%% pass): "small in the C column … and largest where it is not" put both halves
%% of one sentence on quantities from DIFFERENT COLUMNS and named only the first
%% column, so a reader holding §2's "the check is the biggest cost on three of
%% ten" saw a conflict and could not resolve it. BOTH COLUMNS ARE NOW NAMED, one
%% per sentence: hardening in the C column adds the check and nothing else (§3),
%% and the large safe-minus-unsafe numbers are the Rust column, where far more
%% than the check differs (§2). ⚠ NO NUMBER IS IMPORTED — the hardening median
%% and §2's three-of-ten are still their own sections', which the redundancy map
%% requires — and the claim is the one (iii) fixed: this box does not price "the
%% check in either language" off §3's C-column median.
\begin{takeaway}
What a safe version buys is not the price of the check. That price is small in the C column, where hardening adds the check and nothing else (\ref{sec:bothends}). The big safe-minus-unsafe numbers are in the Rust column, where far more than the check differs (\ref{sec:notthecheck}). What it buys is the difficulty of leaving the check out. Not one bounds check fires anywhere in the shipped matrix, and the control that would witness one settles it on half the patterns carrying it. \ref{sec:measure} says what a gate would need to add.
\end{takeaway}
