%% ver_C section 6 — the implications section, which ver_B had nothing like.
%% ver_B's only "what to do" material was six numbered lines in 99-close.md and it
%% measured ~4% of the document; the reference papers spend 6–27% (CONVENTIONS.md
%% 2.6). That imbalance was the "no central theme" verdict in another guise, and
%% this file is the fix: 15–20% of the paper, spending credit the other sections
%% earned and adding no evidence of its own.
%%
%% ⚠⚠ PLAIN-LANGUAGE PASS. Nothing factual was dropped: every bound, every
%% welded qualification and every F-number below was here before, in longer
%% sentences. Short sentences cost about 5% MORE words than the clause-stacked
%% ones they replace, so this file did not shrink as much as a word target
%% would like; what changed is that a reader can follow it. Before restoring a
%% longer wording, read .temp/brief/PLAIN.md — and note that CLAIMS.md §3.4 as
%% amended prefers a scope in the NEXT sentence to a scope nested in this one.
%%
%% TITLE: under 12 words, still the section's instruction and still carrying the
%% bound that makes it honest. Same claim as the old 20-word title.
%%
%% GLOSSES, all three in the opening, because the report is hash-routed and a
%% reader lands on `#measure` cold: `rung` (then the prose says "version"),
%% `obligation` ("one thing the prover has to prove"), `instructions per call`
%% ("what the processor really runs inside the function being measured"). The
%% trusted base is glossed in 6.4's first bullet, where it is used.
%%
%% THREE RULES, from OUTLINE.md PART 1 for this file. They are what keep it from
%% being padding:
%%  (i)   INTRODUCE NO EVIDENCE. Every figure leaned on here is already published,
%%        in the same units, in the section named beside it. A passage here that
%%        explains a measurement has stolen someone else's section.
%%  (ii)  Every item is something the reader does to their own code, never a
%%        number to quote. That is ver_A's 15-whattodo rule — the one section of
%%        ver_A its hostile reader did not object to — and ver_B kept it verbatim.
%%  (iii) Findings are cited by number, F1..F6, the way TaxDC back-references its
%%        own six findings 28 times in its lessons section (CONVENTIONS.md 2.4).
%%        That syntax is what makes this a set of references rather than a list,
%%        and this file carries the most back-references in the paper: F2, F3,
%%        F4, F5 and F6 — five of the summary's six, all but F1.
%%        ⚠⚠ THE CUT PASS (.temp/brief/CUT.md) RENUMBERED F1..F10 TO F1..F6 AND
%%        EVERY CITATION HERE MOVED WITH IT. The map, so a later editor can
%%        check any one of them: old F6 (remove and re-measure) and old F7 (the
%%        two catches) are now **F4**; old F8 (four tools) and old F9 (the blind
%%        spot) are now **F5**; old F10 (exit 101) is now **F6**; old F5 (the
%%        same-machine-code rule) is now **F3**. TWO CITATIONS HAD NO SUCCESSOR
%%        AND POINT AT SECTIONS INSTEAD: old F4, the hardening median, which
%%        moved out of the summary into §3, so the hardening bullet cites
%%        \ref{sec:bothends}; and old F3, the one-way search bias, which moved
%%        into §2's caveat, so the "publish the triple" lead cites
%%        \ref{sec:notthecheck}. Neither claim changed; only its address did.
%%
%% ⚠ STANDALONE CAVEAT ALLOWANCE HERE IS ZERO (OUTLINE PART 4). No \begin{caveat}
%% in this file, and no bounding paragraph: every limit below is welded into the
%% sentence carrying the claim it bounds — "a percentage measured here can only
%% shrink on your code", "line counts are mostly comments and mean nothing", "a
%% bigger count is a bigger program", and the whole opening concession.
%%
%% ⚠⚠⚠ THE REDUNDANCY MAP NO LONGER OUTRANKS CAVEAT-BESIDE-CLAIM HERE.
%% Rigour B6, and it is the load-bearing justification for having no limitations
%% section at all: where the one-home rule collides with filing every caveat
%% beside the claim it bounds, the map was winning and the caveat was being
%% EXILED from the page that needs it — worst on this file, the most actionable
%% one. §6.4 told a proof buyer to budget zero while the map banned from §6 the
%% number that says otherwise, and §6.1 sold hardened C as outcome-equivalent
%% while the map forbade §5 and §6 from mentioning that a hardening flag made
%% the corpus's one detector blind spot. On a hash-routed report a reader lands
%% on `#measure` directly, and a cross-reference is not a substitute.
%% THE RULE NOW: where a section makes a RECOMMENDATION, the bound on that
%% recommendation ships on the same page, as a clause, even where its full
%% treatment lives elsewhere. The map's own preamble already licenses this —
%% F-number citations with no figures repeated — and the writers read its
%% "forbidden" column as absolute and dropped the pointer along with the number.
%% Every bound added below is a clause, and none repeats another section's
%% figure except where the figure IS the bound (§6.4's 8.5%, which has no other
%% home in this paper at all).
%%
%% ⚠ REDUNDANCY MAP (OUTLINE PART 2) — what this file may NOT restate:
%%   the threshold sweep is an ACTION here with NO numbers (home: §2);
%%   F2's 3/5/1/1 tally is cited, never restated;
%%   the hardening median and the 2048-entry validation pass are §3's.
%%     ⚠ THE BRIEF DISAGREES WITH ITSELF HERE and I took the stricter reading:
%%     OUTLINE PART 1's 6.1 bullet writes out "six of the eight largest cells here
%%     price a different program", while PART 2's map licenses this row in §6.1
%%     only "as an action with no numbers" and rule (ii) says never a number to
%%     quote. So the count is dropped and the \ref carries it. ⚠ It used to be
%%     **F4** that carried it; the cut pass moved the hardening median out of the
%%     summary and into §3, so the pointer is now \ref{sec:bothends}.
%%   the coverage table's cells are §4's — here it is only "order by coverage";
%%   the identity pin's −17,526 is §3's and must not appear anywhere here;
%%   the bounded stack's dead clamp is F4, cited, never re-derived;
%%   the two prospective catches (6.02×, 9.6×) are FORBIDDEN in §6 — they are now
%%     part of **F4**, and this file cites F4 only for the dead clamp and the
%%     surviving +5, never for those two rows;
%%   `resource` may appear ONCE in the whole paper outside §4, and it is 6.4's.
%%
%% ⚠⚠ WORD BUDGET, MEASURED. CUT.md targets 700 prose words for this file and it
%% lands at ~1,085. The only cut it rules here is the merge of the two middle
%% audiences, which saves a subsection heading and a lead sentence, and its other
%% instruction is a KEEP list — "all four of the concrete actions: known-bad
%% input in the shipped configuration; delete a check and run your tests; publish
%% the pair; budget the proof honestly". All four are here. Reaching 700 means
%% deleting four or five whole bullets, and every bullet here is an action backed
%% by a finding, several carrying a bound rigour B6 says must ship on this page
%% (the hardening bullet's blind spot, 6.4's 8.5%). That is a ruling this pass
%% did not have. Ranked, cheapest first, if the supervisor wants it: (1) "Name
%% your population…", 25 words, the most generic; (2) "Buy it for memory safety
%% and nothing else", 30, which restates F5's own `Do:` line; (3) "Order the bug
%% classes by what your detectors can see", 55, whose action survives in §0's F5
%% and §4's principle; (4) the noise-floor bullet, 60, which is the only place
%% this paper cites the measurement-bias literature.
%%
%% ⚠ The title's second clause is a real concession and it is honoured in the
%% opening paragraph, plainly, once (CLAIMS.md §1.23). The gate half of the
%% merged subsection then carries it into the gate as an action instead of
%% restating the mechanism —
%% "remove the mechanism and re-measure" appears four times in this paper and each
%% appearance must ADD something (stated §2, failed §4, bounded §5, operationalised
%% here).
%%
%% Provenance for the two facts in 6.4 that are not in another section:
%%   trusted base + escape hatch — results/SYNTHESIS.md §"The trusted base is the
%%   number to look at" (108 items / 230 lines / 0 pattern-local axioms; the
%%   assume_specification form Verus prints "carries no requires and no ensures at
%%   all, and will verify a 1 MiB out-of-bounds read");
%%   the two attacks — the same section's copy_nonoverlapping substitution, caught
%%   by Miri and the byte-identity pin, plus the ghost ledger (RULINGS C19: "the
%%   pin protected the pattern, the proof did not"). Both are cited to §4 in the
%%   prose because §4 owns the ghost ledger row.
%% Checked in the parent tree: no shipped rung DECLARES an assume_specification —
%% three grep hits under patterns/, all three in comments (p08, p14, p46).

%% ⚠⚠⚠ THE UNDERGRADUATE PASS (.temp/brief/REVIEW-undergrad.md).  Every bullet,
%% bound, figure and F-number is unchanged.  The cold reader skipped §6.4 whole —
%% "advice for someone who already knows what buying a proof means" — and named
%% the opening as the second of two places they felt talked down to: "Explaining
%% 'obligation' to me in a section that has never once said what a prover is felt
%% like being handed the easy half."  So:
%%   * `prover` is glossed BEFORE `obligation`, in the same breath.  `Verus` is
%%     named as the prover on the bullet that leans on its output — "Verus's `N
%%     verified`" was the only appearance of the name in the paper and it arrived
%%     as a possessive, as if the reader already knew.
%%   * `kernel` DEFINED — undefined in all nine files, used four times here.
%%   * `sanitizer` glossed on the gate bullet, which is where this file uses it.
%%   * `postcondition` and `twin` are said in plain words ("the proof's promise
%%     that nothing leaks", "one half of a claim proved twice").  Both were on the
%%     never-explained list; §4 glosses `twin` and `precondition` for the paper.
%%   * "Budget about four times the source text — 404% of the unsafe version's raw
%%     lines" read as a contradiction cold: "reading it cold I couldn't tell
%%     whether the % number was going to be 4 or 400."  One word ("the proofs run
%%     to") makes the two the same statement.  The figure is still live \num.
%%   * ⚠ CUT, 17 words: "Now the title, plainly: delete the mechanism, and if the
%%     number does not move you learned nothing."  It restates the \section title
%%     three lines above it, and "remove the mechanism and re-measure" is the
%%     phrase the reader counted FIVE OR SIX times across the paper ("By §6 I was
%%     slightly irritated").  ⚠ CLAIMS.md §1.23 IS STILL DISCHARGED HERE: the
%%     concession is the sentence immediately after it, which is the substance
%%     rather than the slogan — nothing tells apart a deleted check from two
%%     versions that compiled alike.  The title still carries the second clause.
%% ⚠⚠⚠ THE SECOND UNDERGRADUATE PASS (.temp/brief/REVIEW-undergrad2.md), 4/10.
%% Every bullet, bound, figure and F-number is unchanged.  ALL FOUR OF THIS FILE'S
%% GLOSSES ARE CUT, and every one of them was a duplicate:
%%   * "Two words first.  The *prover* … an *obligation* …" — MOVED TO §1, onto
%%     the six-rung list where the machine-checked proof is first described.  The
%%     reader named this opening as one of two places they felt talked down to:
%%     "That's section SIX.  I had already been shown `md5_fn 852405e0…`,
%%     `identity level exact`, `510×` and 'though 13 had only Z3' without so much
%%     as a comma of explanation.  Being handed the two easy words at the end
%%     feels like the wrong half."  ⚠ THE WORDS ARE NOT LOST — they are earlier.
%%   * the `kernel` gloss — the sixth in nine files.  §0 defines it, §1 re-glosses
%%     it once, and those two are the whole allowance.  "Being told what a kernel
%%     is for the sixth time" was the reader's other talked-down-to item.
%%   * the `gate` gloss on the gate bullet — §1 glosses `the gate` at the identity
%%     digest and §5 re-glosses it where its argument turns on what the gate does
%%     not read.  This was the third.
%%   * the `sanitizer` gloss — §0's F5 and §4's column list both carry it in
%%     near-identical words; this was the third of three.
%% ⚠ IF ANY OF THE FOUR WORDS EVER LOSES ITS EARLIER HOME, ITS GLOSS COMES BACK
%% HERE, because a reader lands on `#measure` cold by hash route.
%% ⚠ "your bucket" -> "above the line" on the threshold bullet: `bucket` was on
%% the reader's never-explained list and this file used it once.
\section{Delete the mechanism and re-measure; if nothing moves, you learned nothing}
\label{sec:measure}

%% ⚠⚠⚠ THE FINAL CUT (target 6,200 prose words for the paper).  Its ruling for
%% this file: "Cut the four non-core bullets named in your header menu (~170).
%% Compress the remaining bullets."  ALL FOUR ARE GONE, in the ranked order the
%% header itself set, and each is recorded at its own site below:
%%   (1) "Name your population and the rule that admits a row to it" — 23 words;
%%   (2) "Buy it for memory safety and nothing else" — 26;
%%   (3) "Order the bug classes by what your detectors can see" — 54;
%%   (4) the noise-floor bullet — 51.
%% RESTORE IN THE REVERSE ORDER: (4) first, because it is the paper's only
%% citation of the measurement-bias literature and a reviewer in that area reads
%% the uncited version as reinvention; then (3), (2), (1).
%% ⚠ `mytkowicz09` and `stabilizer13` are now uncited.  They STAY in refs.json —
%% build_data.py errors on a \cite with no entry, never on an entry with no
%% \cite, and deleting them is what would make the restoration lossy.
%% ⚠ CUT (1) DOES NOT COST THE PAPER ITS POPULATION RULE: §2 states the licence
%% rule in plain words and gives both denominators, and §3's `principle` box is
%% what this subsection cites.  ⚠ CUT (2) WAS `resource`'s ONE LICENSED
%% APPEARANCE OUTSIDE §4; the word now lives only in §4, which owns it.
%%
%% ⚠ THE GLOSSES STAY.  Both `obligation` and `instructions per call` are still
%% used below, and a reader lands on `#measure` cold by hash route.
%% ⚠⚠ TWO OF THIS FILE'S THREE GLOSSES ARE CUT, ~22 words, and they were DEAD
%% BEATS rather than a trim — the same defect as §4's `obligation` gloss.  The
%% file used the word `rung` exactly once, in its own gloss, and the phrase
%% "instructions per call" exactly once, in its own gloss; the prose says
%% "version" and "executed instructions" everywhere else.  A gloss for a word the
%% file never uses is pure cost on a hash-routed page.
%% ⚠ THE `obligation` GLOSS STAYS: the file leans on the word four times, in
%% 6.4's two lead paragraphs, the strength bullet and the figure caption.
%% ⚠ THE CORPUS SENTENCE STAYS TOO, without the `rungs` label — a reader landing
%% on `#measure` cold still meets "\num{totals.identity_exact} of
%% \num{totals.patterns} patterns" and "on two of these kernels" below, and needs
%% to know what those are.  If either glossed word returns to this file, its
%% gloss returns with it.
Nothing here tells a check the compiler already deleted apart from two versions that happened to compile alike (**F6**, \ref{sec:nonoptional}).

\subsection{If you are deciding on a rewrite}

%% "take the constant, not the fraction" is CLAIMS.md §3.5's direction rule as an
%% action: the limitation ships pointing which way it distorts, in-sentence.
%% ⚠ rigour M20: "often exactly zero" read back onto §2's evidence as the
%% RETRACTED "one dead line deletes 100% of it" (C11: must not come back). §2's
%% residue is a per-call constant and it is NOT zero. The bullet names it.
%% ⚠ A6(b): the hardening bullet keeps the blind-spot clause. Without it a
%% reader landing on `#measure` concludes hardening buys Rust's outcomes with
%% none of the rewrite and is never told that a hardening flag made this
%% corpus's one true detector blind spot. It is an F-number, no figure.
%% ⚠ F4's count is corrected here too — see §3's note; "most of the biggest"
%% rested on the six-of-eight figure that does not reproduce.

%% ⚠⚠ CUT (3) OF THE FINAL CUT'S FOUR, 54 words, and it sat here: "**Order the
%% bug classes by what your detectors can see, not by how exploitable they
%% look**.  Counting how many tools in your toolchain can see a class needs no
%% threat model, reads off the questions in section \ref{sec:allocation}, and one
%% known-bad input per class tests it (**F5**).  Fix first what nothing you own
%% can see."  ⚠ THE ACTION IS NOT LOST: §0's F5 carries it as a `Do:` line ("name
%% what each of your own tools watches, and put a known-bad input per detector in
%% the build you ship"), §4's `principle` box states it as a rule, and the
%% known-bad-input half survives verbatim in this file's gate bullet below.
%% ⚠ TIGHTENED, not cut: the first paragraph's "the tax is a constant per call.
%% Often it is exactly zero" is now one clause.  ⚠ M20 still binds — "often
%% exactly zero" may NOT be read back onto §2 as the retracted "one dead line
%% deletes 100% of it" (C11), which is why the surviving +5 is named in the
%% bullet under it.
**Ask where the bound comes from before you count bounds checks**. Where the optimiser can already see the fact that justifies the check — a clamp, say — the tax is a per-call constant, often exactly zero (**F4**). Where it cannot, expect a cost on every element (**F2**, \ref{sec:notthecheck}).

%% ⚠ CUT, ~20 words: "Even where the tax was deleted outright, five instructions
%% per call survive that nobody has searched."  THE SURVIVING `+5` IS ON THE
%% MUST-NOT-LOSE LIST AND IT IS NOT LOST — this was its THIRD appearance.  §0's
%% F4 says "Five instructions per call survive, and nobody has tried to remove
%% them", and §2's dead-clamp example says "The `+5` survives on both blobs —
%% 2889 − 2884 and 8886 − 8881 … nobody has searched it at all", which is the
%% evidence.  ⚠ M20 still binds on what remains: "often exactly zero" in the
%% paragraph above may NOT be read back onto §2 as the retracted "one dead line
%% deletes 100% of it" (C11), so restore this clause first if that ever looks
%% ambiguous to a reader.
- **Take the per-call constant, never the percentage**: these kernels do nothing but the loop, so a percentage measured here can only shrink on your code (**F4**).
- **If you are not rewriting it, harden it — and price the hardening you are actually buying**. The biggest hardening numbers here pay for a different program, not for a check (\ref{sec:bothends}). On outcomes, these measurements cannot separate hardened C from Rust (**F6**). And one hardening flag here blinded a sanitizer that owned exactly the right check (**F5**, \ref{sec:allocation}).

%% ⚠⚠⚠ THE CUT PASS (.temp/brief/CUT.md): "FOUR AUDIENCES BECOME THREE. Merge
%% the tool-author and benchmark-author subsections: their advice overlaps
%% heavily and the reader who is one is usually the other." Executed here: the
%% old §6.3, "If you are building the tool, or the gate", is now the second half
%% of THIS subsection, under a title naming both readers. Nothing in either half
%% was dropped — the four actions CUT.md names all survive, two of them in this
%% subsection ("publish the pair"; "a known-bad input in the shipped
%% configuration"; "delete a check and run your tests") — and the two leads are
%% now one paragraph and one bridge sentence.
%% ⚠ THE ORDER IS DELIBERATE: what to publish, then what a gate must do about it,
%% because the gate paragraph's force is that OUR gate does not do it.
\subsection{If you are publishing a number, or building the gate that checks it}

%% ⚠ CUT: this subsection used to restate \ref{sec:bothends}'s `principle` box
%% almost word for word ("the number, the pair of spellings it differences, and
%% which side anybody tried to make fast ... a bound with one endpoint held by
%% decree", identical down to "held by decree"), and its last bullet restated
%% the same box's "cheapest found, never minimum". Both are §3's, three
%% reviewers named that box load-bearing, and citing it is what the finding
%% numbers are for. ~55 words, and nothing is lost.
%% ⚠ rigour M16: "quotes no wall clock" is false — §3 quotes it four times now.
%% The forbidden thing is a wall-clock COST figure, which is what the project
%% does not publish, and that is what the bullet says.
%% ⚠ rigour M21: the noise-floor bullet is a restatement of the measurement-bias
%% literature's own result and was carrying no attribution; a reviewer in the
%% area reads it as reinvention. Citing costs two words and strengthens the
%% thesis, because the paper's claim is that memory-safety measurement is an
%% instance of a general attribution failure.

**Publish the triple** that section \ref{sec:bothends} asks for. The two parts people drop are the two that bound the number (**F3**, \ref{sec:notthecheck}).

%% ⚠⚠ CUTS (1) AND (4) OF THE FINAL CUT'S FOUR SAT HERE, 74 words together.
%%  (1) "**Name your population and the rule that admits a row to it, in the
%%      sentence with the statistic**.  Then give a second denominator."  The
%%      most generic bullet in the file, and the `principle` box this subsection
%%      opens by citing already asks for the pair and the unsearched side.
%%  (4) "**Interleave by cell, never by block, and measure your noise floor on
%%      byte-identical copies** \cite{mytkowicz09} \cite{stabilizer13}.  If the
%%      floor is wider than the effect, you have not measured the effect.  Never
%%      publish an extreme value, and never repair one with another: this project
%%      did both, and publishes no wall-clock cost figure at all
%%      (\ref{sec:bothends})."
%%      ⚠⚠ RESTORE (4) FIRST OF ALL FOUR.  It is the paper's ONLY citation of the
%%      measurement-bias literature (rigour M21: uncited, a reviewer in the area
%%      reads it as reinvention), and its last clause is a confession about this
%%      project's own conduct — "this project did both".  Losing a confession is
%%      the cut that costs the most trust per word, and it is why this one is at
%%      the top of the restore list.
%%      ⚠ WHAT SURVIVES IT: §3 prints the wall-clock disagreements and the
%%      "no cross-pattern timing column, no hardware counter" bound; the bullet
%%      below still says the counter and the clock disagree in direction.
%% ⚠ rigour M16 still binds on whatever is restored: "quotes no wall clock" is
%% FALSE — §3 quotes it four times.  The forbidden thing is a wall-clock COST
%% figure.
- **Sweep the threshold; do not publish one cut-off** (**F2**). If the same programs come out above the line at every threshold, say so, and the *you chose the cut-off* objection is dead.
%% ⚠⚠ CUT, 39 prose words, beyond the four the ruling named — the file could not
%% reach its 800-word target on those four alone.  It read: "**Where two metrics
%% disagree, report both and name the one you publish**.  Two counting rules here
%% disagree about which rows are even negative, and the counter and the clock
%% disagree in direction on four kernels (\ref{sec:bothends})."
%% ⚠ WHY IT WAS AFFORDABLE: it is the only bullet in this file whose action is
%% not on CUT.md's keep list, and both facts behind it are §3's — §3 prints the
%% clock disagreement in both directions, and §0's scope paragraph states the
%% four kernels.  Restore it AFTER the noise-floor bullet and before (1).

%% ⚠ CUT: this paragraph restated §5's gate-gap list near-verbatim — the cold
%% reader called it "the clearest cut-and-paste in the document" — where the
%% finding number is the citation. ~40 words, and §5 keeps the list whole.
%% ⚠ rigour Q3's one gap: "delete one check and run your test suite" is a
%% BEHAVIOURAL operation, not a cost one, so the bound stated in the section
%% opening does not cover it; its own bound (a silent detector and an absent one
%% write the same log line) was one bullet above and unconnected. Joined.
%% ⚠ CUT FOR LENGTH, ~45 words: a third bullet, "Carry the bound into the gate",
%% whose content was "a gate that cannot make a check fire cannot tell a deleted
%% check from an absent one, and reports both as zero". That is the SAME
%% sentence as the log-line clause in bullet 1 and the green-suite clause in
%% bullet 2 — the idea was stated three times in six lines. It now appears once,
%% welded to the operation it bounds (Q3's requirement) and closing on "why the
%% control input is not optional", which is what the deleted bullet was for.
%% The missing STAGE is still named in the lead paragraph above, unchanged.

%% ⚠ TIGHTENED, ~25 words, no clause dropped: "A safety benchmark's gate" became
%% "It"; the sanitizer bullet's "where the sanitizer owns exactly the right
%% check" is carried by the \ref and the F-number; the last bullet's two closing
%% sentences became one.  BOTH BOUNDS SURVIVE WELDED, which is what rigour B6
%% requires on a page that makes a recommendation: a silent detector and an
%% absent one write the same log line, and a green suite cannot tell an untested
%% check from an absent one.
**If you are building the gate, our gap is your to-do list**. \ref{sec:nonoptional} lists what ours never reads (**F6**). It needs the stage this one lacks: **a control input per version that makes the check fire, and a failure when it does not**.

- **Put a known-bad input in the sanitizer job and fail the build on silence — in the configuration you ship**. A hardening flag can take the check off its path (**F5**, \ref{sec:allocation}), and a silent detector and an absent one write the same log line.
- **Delete one check in a branch and run your tests**. Then read a green suite the way you read that log line: neither can tell an untested check from an absent one. That is the position this corpus is in, and why the control input is not optional.

\subsection{If you are buying a proof}

%% ⚠⚠⚠ "BUDGET ZERO EXECUTED INSTRUCTIONS" UNQUALIFIED IS GONE. Ruling C34(a),
%% the coverage-bias review's central finding, and it was the single sentence
%% that review was written against. The authoritative layer — `.memory/04-verus.md:8-52`,
%% which supersedes every task report — prices a proof obligation IN A SHIPPED
%% RUNG: p11 writes `if q >= len { break; }` solely to discharge an overflow
%% obligation, deleting it leaves every checksum unchanged and moves the marginal
%% 19,084 -> 17,481 and 50,174 -> 45,909, i.e. +1.00000 `Ir` per scanned byte,
%% 8.4% / 8.5% of the unsafe rung, zero residual over four string lengths. That
%% entry ends "**Quote the trade, never 'it was free.'**" — and this passage
%% once printed the sentence it forbids. I read the entry myself. The same entry
%% prices the alternative route, a second `requires` on another pattern, at ZERO
%% instructions, which is why the prose gives both ends rather than one number.
%% ⚠ The zero itself is also a TAUTOLOGY of the identity pin, not a finding
%% about proofs (CLAIMS.md §2.3, rigour B6, and the cold reader spotted the
%% contradiction with §2's own principle box unaided). Said here, once, and the
%% pin is now spelled out ("we require the two to compile alike") rather than
%% named, which glosses it in place.
%% ⚠ rigour M14: the \ref for the exception pointed at §1, which documents no
%% exception. It points at §3, which now states it.
%% ⚠ bias review 3.10: "the zero holds on the exception too" is the first half
%% of that pattern's own scope clause with the "but" removed — the proof costs
%% 64 bytes of read-only data and an emitted stub there. Restored.
%%   ⚠ TIER, recorded and NOT printed: those 64 bytes come from
%%   `.temp/p36c/vtable_probe.py`, a gitignored probe, not from a gate record —
%%   `p36/NOTES.md:601` names it. The figure reproduces (the same file derives it
%%   twice, from the vtable gaps 32→40 over 8 types and from `TABLE` moving
%%   exactly 64 bytes) and the identity level it qualifies IS gate data, so it is
%%   quotable; a tier clause would cost ~10 words on a page with none to spare
%%   and the prose already says the figure is an exception. Next reviewer: if
%%   the budget grows, this is the one anti-proof figure in the paper still
%%   printed without its tier.
%% ⚠⚠ THE AUTHORING COUNTERWEIGHT IS HERE, second bias review §4.4 / N3. The
%% floor clause is correct and is anti-proof, and the direction it points is the
%% one the corpus contradicts: the review counted NINETEEN patterns recording an
%% R5 that verified on the first or second attempt. ⚠ I DID NOT PRINT 19. I
%% could not reproduce it — grepping the obvious phrasings over all 26 NOTES
%% gives 11 files, and settling the true count needs a stated rule and a read of
%% every file, which this pass did not have. What IS verified first-hand and is
%% quoted instead: `p16/NOTES.md:999-1000` "R5 verified on the **first
%% attempt**, `10 verified, 0 errors`, which was not expected — the task
%% budgeted a full engineer session for this cell", and `p07/NOTES.md:574`
%% "**First try, no stalls.** The one-session R5 budget went unused, as it did
%% on p16." Two kernels, both named in the source, is a claim that cannot go
%% stale under a recount. OWED: the census.

%% ⚠ TIGHTENED, ~16 words, and NOTHING on the protected list moved.  Still here,
%% in order: the zero is OUR OWN RULE and not a discovery about proofs
%% (CLAIMS.md §2.3 — it is a tautology of the identity pin); the one exception's
%% 64 bytes and emitted stub, which runs AGAINST the proof (bias review 3.10);
%% the 8.5%, which has no other home in this paper at all; the zero-cost
%% alternative route on another kernel; the floor clause; and the pro-proof
%% counterweight of two kernels verifying first try.
**Budget zero executed instructions — and know why the zero is there**. On \num{totals.identity_exact} of \num{totals.patterns} patterns the proved kernel and the unproved one are the same machine code, because we require the two to compile alike: our own rule at work, not a discovery about proofs. On the one exception the proof costs 64 bytes of read-only data and one function that never runs (\ref{sec:bothends}).

**Where a proof changes the program, it is not free**. On one kernel a line written only to discharge an overflow obligation costs 1.00 instruction per byte scanned, 8.5% of the unsafe version; on another the same obligation costs nothing, discharged by a precondition \src{.memory/04-verus.md}. No compile time and no authoring hours are measured here, so every price below is a floor. The other way: on two of these kernels the proof went through first try, leaving the budgeted engineer session unused \src{patterns/p16-tlv-walk/NOTES.md}.

%% \num{totals.proof_text.ratio_pct} is an INTEGER PERCENTAGE (404), not a
%% multiplier — CONVENTIONS.md §5. "Line counts mean nothing" is ruling C6: the
%% tree's own totals are comment-dominated, which is why the trusted base is the
%% figure this bullet actually recommends budgeting.
%% ⚠⚠ THE BULLET USED TO CONTRADICT ITSELF AND IT NO LONGER DOES (fourth
%% undergraduate pass, its "numbers I could not pin down" list). It told the
%% reader IN BOLD to budget 404% of the source and then, three lines later, that
%% "line counts are mostly comments and mean nothing" — a bolded instruction in a
%% unit the same bullet calls meaningless. C6 is the tiebreak, so the TRUSTED
%% BASE now leads, in the bold, and the 404 is explicitly labelled THE CRUDE
%% FIGURE. ⚠ NOTHING FACTUAL MOVED: the same \num, the same two trusted-base
%% counts, the same vstd clause, and C6's comment-domination is still stated.
%% ⚠ DO NOT PUT 404 BACK IN THE BOLD without deleting the comment clause, and
%% C6 forbids deleting the comment clause.
%% ⚠ bias review 3.10: the recommended metric sits on an unpublished substrate —
%% the pinned vstd beneath those 108 items holds 402 `assume_specification`
%% sites, 272 `external_body` items and 545 broadcast axiom lemmas, and "relied
%% upon is not decidable from the text". A clause, no figures.
%% ⚠ bias review 3.6 / C34(a): the obligation count is BLIND, which the tree
%% calls "the sharpest and least comfortable finding in the section, because the
%% count is the number every paper reports". §4 now carries the measured
%% instance; this is the action that falls out of it, and it belongs on the page
%% that tells a buyer what to look at.
%% ⚠⚠ SECOND BIAS REVIEW §4.1, AND IT IS THE HALF THIS BULLET WAS MISSING. The
%% bullet correctly told a buyer that `N verified` is not a strength measure and
%% then offered, as the thing to prefer, a trusted-item count the tree records
%% as prospectively gameable — while the measure that IS adversarial, IS
%% gate-certified and IS regenerated on every run went unmentioned in the whole
%% paper. It now names the OPERATION here, as an action with no figures (rule
%% (ii)), and §4 carries the measured result with its counts. Rule (i) —
%% introduce no evidence — is why the numbers are there and not here.
%% ⚠ THE `\ref{sec:allocation}` ON THE ATTACK BULLET IS GONE, because §4's
%% ghost-ledger footnote is gone with it and a \ref must not point at a
%% paragraph that is not there. The bullet leans only on the two attacks it
%% names, which is what results/SYNTHESIS.md §"The trusted base is the number to
%% look at" supports on its own; the clause that needed §4 was "on one pattern
%% the pin protected the pattern while the proof did not".
%% ⚠⚠ CUT (2) OF THE FINAL CUT'S FOUR, 26 words, and it sat here: "**Buy it for
%% memory safety and nothing else**.  The guarantee ranges over one resource —
%% one thing it watches — and everything outside it is still yours (**F5**)."  It
%% restates F5's own `Do:` line and §4's `principle` box in one bullet, which is
%% why the header ranked it second-cheapest.  ⚠ IT WAS `resource`'s ONE LICENSED
%% APPEARANCE OUTSIDE §4 (CONVENTIONS §4).  The word now appears only in §4,
%% which owns it; if this bullet comes back, the licence is still there.
%% ⚠⚠ "Nor does it move when the guarantee does" IS NOW THE PAPER'S ONLY HOME FOR
%% THE LEAKING-KERNEL FINDING.  §4's measured instance — the constant-time mutant
%% verifying at `14 verified, 0 errors` with the kernel's own obligation count
%% unchanged, then executing 7,088 more instructions on one input than on another
%% printing the same checksum — was cut by the same ruling.  This clause is a
%% CLAIM and carries no figure, which is what rule (i) requires of §6; but if
%% anyone restores §4's instance, this clause is where the \ref belongs.
%% ⚠ Do not delete it to save words.  It is bias review 3.6 / C34(a), which the
%% tree calls "the sharpest and least comfortable finding in the section, because
%% the count is the number every paper reports", and it is anti-proof.
- **Budget by the trusted base, not by the line count**. That is \num{totals.tcb_items} hand-written items over \num{totals.tcb_lines} lines the prover takes on trust and never checks, sitting on a standard library whose own trusted surface is larger and is not counted here. The crude figure — \num{totals.proof_text.ratio_pct}% of the unsafe version's raw lines, about four times the source text — counts mostly comments.
- **Do not read the count of proved obligations as a strength; ask what the proof was attacked with**. Our prover is Verus. Its `N verified` counts items — functions, loop bodies, sub-proofs — not the conditions inside them, so a bigger count is a bigger program. Nor does it move when the guarantee does: delete the proof's promise that nothing leaks, unchanged; substitute a leaking loop, unchanged. A mutation does move it: damage the proof yourself and require the verifier to notice. It is cheap, and runs here on every run (\ref{sec:allocation}).
%% ⚠⚠ CUT, 37 prose words, again beyond the ruling's four: "**Budget for whatever
%% catches the attack, because it may not be the prover**.  Both attacks on the
%% trusted base here were stopped from outside it, by a byte-identity pin and by
%% an interpreter.  You build both yourself."
%% ⚠ It is anti-proof and it is a real action, so it is a genuine loss; it went
%% because the bullet above it now carries the same instruction ("ask what the
%% proof was attacked with") and because its action is not on CUT.md's keep list.
%% ⚠ It also lost its \ref{sec:allocation} in an earlier pass, when §4's
%% ghost-ledger footnote was cut, so nothing points at it and nothing dangles.
%% Its source is results/SYNTHESIS.md §"The trusted base is the number to look
%% at" (the copy_nonoverlapping substitution, caught by Miri and the byte-identity
%% pin) plus the ghost ledger (RULINGS C19: "the pin protected the pattern, the
%% proof did not").  Restore it before the escape-hatch bullet and after (1).
%% ⚠⚠ CUT, 54 prose words, and it is the last thing this file could give.  It
%% read: "**Read the escape hatch before you accept it**.  Rejecting a call, the
%% verifier offers you a specification to paste in with no `requires` and no
%% `ensures` at all — and a program built on one verifies a 1 MiB out-of-bounds
%% read.  No version here declares one, which was somebody's decision, not a
%% property of the tool."
%% ⚠⚠ RESTORE THIS FIRST OF EVERYTHING CUT FROM THIS FILE, ahead of the four the
%% ruling named.  It is the most concrete anti-proof warning in the report, it is
%% checkable by any reader against their own verifier, and its last clause is the
%% one that keeps it fair — no shipped rung here uses the hatch, and that was a
%% decision somebody made rather than something the tool prevents.
%% ⚠ Source: results/SYNTHESIS.md §"The trusted base is the number to look at" —
%% the `assume_specification` form Verus prints "carries no requires and no
%% ensures at all, and will verify a 1 MiB out-of-bounds read".  Checked in the
%% parent tree: three grep hits for a declared `assume_specification` under
%% patterns/, all three in comments (p08, p14, p46).  The surviving trusted-base
%% bullet still tells a buyer to look at the trusted base, so the METRIC is not
%% lost; what is lost is the demonstration that the base can be widened by one
%% pasted line.

\figure{tcb}{Per pattern: obligations discharged, trusted items, trusted lines the verifier never checks, and twins re-deriving them.}
\label{fig:tcb}
