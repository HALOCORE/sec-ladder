%% ver_C section 4 -- HALF B.  The coverage table RESTORED to twelve rows, with
%% the retraction of its own predecessor's flourish standing beside it.
%%
%% ⚠⚠ PLAIN-LANGUAGE REWRITE, IN PLACE (`.temp/brief/PLAIN.md`).  PROSE ONLY:
%% not one number, correction, retraction or admission changed, no row dropped,
%% no cell regraded.  What changed is HOW it is said — one idea per sentence,
%% scope allowed to stand in the NEXT sentence (CLAIMS.md §3.4 AS AMENDED), the
%% four legend values RENAMED INTO ENGLISH, and the counting rule, the tier
%% arguments and the ruling citations moved down into these comments.
%%
%% ⚠⚠ THE LEGEND VALUES ARE RENAMED AND THE WORD `vacuous` IS GONE FROM THE
%% PAPER.  The mapping is exact and the distinction the legend exists to protect
%% is untouched:
%%     `yes`     -> **caught**       (reached the class, with a measurement)
%%     `no`      -> **missed**       (silent, and could in principle have seen)
%%     `vacuous` -> **not its job**  (silent because nothing here violates this
%%                                    mechanism's own rule — NOT the same as
%%                                    `missed`, and the retraction below turns on
%%                                    exactly that difference)
%%     `—`       -> **—**            (not measured)
%% The qualified cells keep their qualification and are still DISSENTS under the
%% counting rule: `watchdog` -> "a watchdog", `debug builds` -> "debug builds
%% only", `flag-gated yes` -> "caught, with one flag", `partly` unchanged,
%% `Rust vacuous` -> "not its job (Rust)", and p09's full-proof cell keeps its
%% "until the spec inherits the bug".  ⚠ A LATER AGENT MUST NOT COLLAPSE
%% `missed` AND `not its job` INTO ONE WORD: that collapse is half of what made
%% the retracted sentence true.
%% ⚠ The question labels lost their italics so that each row reads as a plain
%% question.  Nothing else about the table moved.
%%
%% ⚠⚠⚠ THE CUT PASS (.temp/brief/CUT.md) RENUMBERED THE SUMMARY'S FINDINGS FROM
%% TEN TO SIX, AND THIS FILE'S CITATIONS MOVED WITH THEM.  Old F8 (four tools,
%% five of ten) and old F9 (the blind spot a hardening flag made) are now ONE
%% finding, **F5**, so both `(**F8**)` and `(**F9**)` here read `(**F5**)`.  The
%% two claims are unchanged and are still made in different paragraphs; only the
%% pointer merged.  If the summary ever splits them again, split these back.
%% ⚠ CUT.md's other instructions for this file were: the twelve-row table, its
%% English legend, the count with its caution and the retraction ALL STAY; the
%% blind-spot example stays IN FULL; the two range-parser programs stay NAMED
%% SEPARATELY.  Executed: nothing in that list was touched.  What was cut is
%% recorded at each site — the bitset's two verifier counts, and the three-row
%% provenance footnote compressed to two sentences.
%% ⚠⚠ THE OTHER TWO CUTS CUT.md NAMES WERE ALREADY MADE: the redzone paragraph
%% and the ghost-ledger footnote went in the previous pass and only their `%%`
%% records remain, so this file could not yield what the 950-word target assumed.
%% It lands at ~1,580.  Everything between it and 950 is on the keep list above
%% or is a ruling's mandated worked instance; the ranked cut list at the end of
%% this header is still the order to consider, and every item on it loses
%% something a ruling names.
%%
%% RULING MAP (.temp/brief/RULINGS.md):
%%  C15 -> the restored twelve-row table + four-valued legend, the `retraction`
%%         environment, and the "one silence is not scope" finding.  This ruling
%%         is why the section exists; every other beat here serves it.
%%  C16 -> "four of six", DERIVED here rather than inherited; the three-way
%%         allocation / values / trace split that earns the word `resource`; and
%%         the corrected non-termination x memory-safety-proof cell, which reads
%%         `caught` because Verus demands a `decreases` on every exec loop by
%%         default and stripping `ensures` does not remove that obligation.
%%  C17 -> the range parser: NO shipped memory-safe rung discloses.  The two
%%         programs that DO are unshipped, in gitignored scratch, and they are
%%         NOT the same program -- the sentence here used to splice them into
%%         one that does not exist ("a verified one-line change to the shipped
%%         safe rung").  Per the fact-check against p17/NOTES.md:285-291:
%%           * `safe_naive_sliceguard` -- a one-TOKEN change to the shipped safe
%%             rung, zero `unsafe`, and NOT verified;
%%           * `verus_sliceguard_msonly` -- verified at `10 verified, 0 errors`,
%%             but it is the PROVED rung and carries a SECOND edit, the
%%             functional-spec strip, which p17/NOTES.md:301-310 says to be
%%             exact about.
%%         Both are named in the prose, in two separate sentences now, and both
%%         disclosing is the stronger claim than either alone.  DO NOT RE-MERGE.
%%         C17 corrects an earlier ruling of the supervisor's; do not undo it.
%%  C18 -> the redzone argument, and fusing it with the range parser would be a
%%         real error.  See the note where the paragraph used to be.
%%  C19 -> the bitset's correct scope (`18 verified, 1 errors` with the
%%         functional postcondition intact), the ghost ledger, the recycle
%%         probe, and the scope of the sanitizer and interpreter columns.
%%
%% ⚠⚠ THREE PLACES WHERE THE OUTLINE WAS NOT EXECUTED, each reported to the
%% supervisor.  In all three a primary artefact beats the outline, which is the
%% authority order the brief sets.
%%
%% 1. This section does NOT print "five of the six silences are scope; one is
%%    not" (OUTLINE beat 7, and F9's number).  IT IS NOT DERIVABLE FROM THE TABLE
%%    IT DESCRIBES.  ver_A's four-valued table carries roughly eighteen silent
%%    detector cells over twelve rows (70-quadruple.md:123-142); ver_B's six-row
%%    table has silences on four of its six rows.  Neither yields five.  Printing
%%    a count that only works after a truncation is the exact defect this section
%%    retracts, so the finding is written as a quantifier over the printed
%%    table -- almost every silence, and one that is not -- which is checkable.
%%    ✅ UPHELD AT REVIEW BY TWO AGENTS INDEPENDENTLY (S9, rigour B3) and §0's
%%    F9 now carries the same quantifier.  Do not reintroduce a count here.
%%
%% ⚠⚠⚠ C31 / rigour B2: THE HEADLINE COUNT IS COMPUTED OVER THE TABLE THIS
%% SECTION PRINTS.  The section used to say "four of six ... at the six-class
%% grain the previous version used".  That is C16's numerator over C15's
%% retracted denominator, and C15 and C16 could not both be executed: C15 orders
%% twelve rows restored BECAUSE the six-row grain is the bias, and C16 ordered
%% the count taken at the six-row grain.  The result was a section that retracted
%% a truncation and then took its own title's number over the same truncation,
%% excluding BOTH of its featured examples (the overlap row and the range
%% parser), in the direction that flatters its thesis.  C16's denominator is
%% overruled.
%% THE COUNTING RULE, reproducible from the printed table.  Two of its three
%% clauses are in the prose (the denominator, and the hedged cell); the third —
%% what "agreement" means — is here, because it is a definition and the prose
%% shows it instead:
%%   * a row counts only if all four detector columns carry a verdict, which
%%     excludes the recycled-handle row (one `—`) and the stack-space row (all
%%     `—`): 10 rows of 12.  ⚠ Both labels were REWORDED by the third
%%     undergraduate pass and neither row moved; the old wordings were "or the
%%     same handle recycled in place?" and "does the machine stack hold?";
%%   * `missed` and `not its job` both read as SILENCE; a qualified cell — a
%%     check that fires only in debug builds, a watchdog outside the build, a
%%     flag-gated sanitizer -- is a dissent, because it is not the same verdict;
%%   * agreement = all four silent, or all four firing.
%% That gives FIVE: the object row and the allocator row fire together; the
%% in-bounds, secret and window rows are silent together.  The five dissents are
%% the release path, non-termination, the shift, the Rust-only aliasing rule and
%% overlap.  5 of 10 -- against the 67% the old title advertised.
%%
%% ⚠⚠ AND THE SIZE OF THE ONE LAX CHOICE IS PUBLISHED (third coverage-bias
%% review §2b, its top-ranked item).  Reading `missed` and `not its job` alike is
%% worth THREE of the five: in-bounds, secret and window are each
%% `missed / not its job / not its job / missed`, four cells and two values.
%% Require the same VALUE — which is what the legend's own "not the same as
%% missed" insists on — and the count is TWO of ten, the two rows where all four
%% fire.  The review's finding was that all five agreements turn on a
%% discretionary call and every one was called the way that produces agreement;
%% the lax rule is defensible (silence is what a reader of a coverage table is
%% asking about) and the strict one is the legend's, so the paper does what it
%% does everywhere else: PUBLISH THE PAIR AND NAME THE CHOICE.
%% ⚠ It now stands as its OWN SHORT PARAGRAPH directly under the count, which
%% CLAIMS.md §3.4 AS AMENDED licenses ("a short following sentence defeats the
%% screenshot just as well and costs the reader nothing") and which PLAIN.md's
%% example 4 shows.  The old single-sentence version was the paper's least
%% readable sentence.  It may not drift further from the number than this.
%% ⚠⚠ THE PAIR IS NOW PUBLISHED LEVEL, AND THAT IS THE FOURTH UNDERGRADUATE
%% PASS'S "shaped" FINDING #1 — the only place in the paper it said the authors
%% had leaned.  FIVE stood in the title, in the bolded count and in the takeaway;
%% TWO stood once, unbolded, in the middle.  "In a paper with a rule called
%% Publish the pair, the pair is published and then one half of it is used
%% everywhere."  THE FIX IS THE BOLD, and it is the only place that moved:
%% the bolded count now carries BOTH numbers, with the verbs that separate them
%% ("do the same thing" / "give the identical verdict").  The caution paragraph
%% under it stopped being a caution ABOUT five and became the difference BETWEEN
%% the two, which is what it always was.
%% ⚠⚠ NEITHER NUMBER MOVED, NOR ITS RULE, NOR ITS DERIVATION.  Five is the count
%% under the stated rule (C31), two under the legend's strict one, and the header
%% note above still derives both.  ⚠ THE TITLE AND THE TAKEAWAY STILL CARRY FIVE
%% ALONE, which C31 orders and which this pass did NOT change — the three
%% structural findings that rest on the rows the strict rule drops are unaffected.
%% ⚠ DO NOT re-subordinate two to five by restoring "One caution about that
%% five": that sentence is what made the count read as one number with an
%% apology attached.
%% ⚠ The takeaway and §0's F8 keep FIVE — it is the count under the stated rule,
%% which is what C31 ordered.  Do NOT switch either to 2: three of the section's
%% structural findings (the three shared silences, the `resource` paragraph, the
%% takeaway) are made of exactly the rows the strict rule drops.
%% ⚠⚠ THE TITLE.  Was "Four detectors agree on five of the ten rows they all
%% reach, and the one true blind spot was made by a hardening flag" (22 words).
%% Now 11, per the brief's title rule, and BOTH claims survive with the FIVE
%% still in it.  The number did not move and no title may carry 2, or the
%% retracted four-of-six.
%%
%% ⚠ ONE TABLE CELL WAS CHANGED, in an earlier pass, and it is flagged because a
%% cell is a decision.  The overlap row's `a runtime check` cell read `n/a`,
%% which appeared nowhere in the legend and so left the row uncountable under any
%% stated rule -- exactly the row A2 says must not be excluded again.  It reads
%% `not its job` (was `vacuous`), the legend's own definition applied literally:
%% an overlapping copy whose two regions are both in bounds does not violate a
%% bounds check's own rule.  The row is a dissent either way (the interpreter
%% fires, nothing else does), so the change moves the count by nothing; it moves
%% the DENOMINATOR by one, against us.
%%
%% 2. THE MACHINE-STACK ROW SHIPS WITH EVERY CELL `—`.  The settlement is that an
%%    unsourceable cell reads `—` and the row stays.  `CLAIMS.md` §1.10 kills the
%%    instance that filled it in ver_A: there is no recursive kernel that
%%    verifies and dies of stack exhaustion.  It is a REFUSED candidate whose run
%%    logs contain zero occurrences of the exit code claimed, whose build script
%%    never invokes the prover, and whose sources do not survive a clone;
%%    ver_B's own header says DO NOT RESTORE IT.  So the row keeps its question
%%    and loses its gradings, which is the supervisor's rule applied to us.
%%
%% 3. `is the arithmetic defined?` reads `caught`, not ver_A's `UBSan yes, ASan
%%    no`.  `CLAIMS.md` §1.14: the ASan half was argued from the defect's shape
%%    and NEVER isolated -- there is no ASan-only build anywhere in the tree.
%%    `caught` is what the combined `-fsanitize=address,undefined` stage measures.
%%
%% ⚠⚠ p38's "caught, with one flag" IS NOT TySan, AND THE THIRD COVERAGE-BIAS
%% REVIEW IS WRONG ON THIS ONE (its §3.9, "Name the p38 sanitizer … it is TySan,
%% clang-only, outside the column's declared gcc build").  `(TySan)` was written
%% in and taken back out after opening the artefacts, which is the authority
%% order this project sets:
%%   * `patterns/p38-alias-pun/NOTES.md:631` §6 — **ASan** sees p38, "`yes` —
%%     `stack-buffer-overflow READ of size 2` … ⚠ ONLY when built with
%%     `-fstrict-aliasing`, WHICH IS A FLAG AND NOT A LEVEL".  That is the
%%     flag the cell is gated on.
%%   * `NOTES.md` §6b — the gate's own stage 7 PASSES `-fstrict-aliasing` since
%%     TASK_077, at `-O1`, and `model.py` declares `sanitizer_expect: "fires"`.
%%   * `results/gate/p38-alias-pun.json` — the stage FIRED on
%%     `adversarial-huge` and `adversarial-oob`, `expect: fires`,
%%     `fired: true`, exit 1, diagnostic `index 256 out of bounds for type
%%     'uint16_t [256]'` from the same `address,undefined` build.
%% So the cell is INSIDE the column's declared population: a gate-measured gcc
%% `-O1` address-and-undefined fire, gated on one compiler flag — which is
%% exactly what "caught, with one flag" says.  TySan is a different instrument in
%% that pattern's §6 table, it has its own row there, and it grades nothing here.
%% Naming it in this cell would have been a false provenance on a gate result.
%%
%% ⚠ Do NOT write that the prover cannot state leak-freedom (C19).  That exact
%% sentence is a standing retraction upstream and restating it would be the
%% fourth attempt; expressibility at this pin is OPEN.  ⚠⚠ THE TEXT DOES NOT SAY
%% SO ANYWHERE — the ghost-ledger footnote that used to carry the clause was cut,
%% so p42's full-proof `missed` ships bare and the protection is THIS COMMENT and
%% nothing else: a future agent must not read that cell as "the prover cannot
%% state it".
%% ⚠ `partly` (p42 x types) is a fifth value outside the four-valued legend.  It
%% is harmless only because the types column is never counted, and it is left
%% alone rather than regraded, because regrading a cell is a decision.
%% ⚠ Do NOT fuse the redzone paragraph into the range parser (C18): redzones
%% separate objects, the disclosure is inside one allocation, and the sanitizer
%% is provably live on that binary because a sibling input fires in the same run.
%% ⚠ `adversarial-leak.bin` is deliberately not named: its excess bytes are the
%% attacker's own header, and naming it invites the confusion TASK_011_REVIEW
%% corrected.  The disclosure is the cross-window PAIR.
%% ⚠ No cost figure is quoted for the bitset mutant: 6691.70 has no artefact of
%% any kind, and the mutant is cheaper than the shipped rung, not dearer (C19).
%% ⚠ The word `resource` is introduced here and used nowhere else but one clause
%% of §6.4.  `bearer` and `residual` are deleted vocabulary.  (No marker is used
%% in these comments: build_data.py collects \ref and \num from the WHOLE file,
%% so a \ref in a comment can fail the build on a section nobody has written yet.)
%% ⚠ Redundancy map: the deleted-line table, `totals.loud` and exit 101 belong to
%% §5 and appear nowhere here.  The user study is cited in §1 only; the clause
%% that cited it here was cut for length and `userstudy25` stays live in
%% refs.json because §1 cites it twice.
%%
%% ⚠⚠ LENGTH, MEASURED, AND THE WORD BUDGET WAS NOT MET.  Sentences 50 -> 102,
%% median 27 -> 17 words, over-35 19 -> 0, longest sentence 34.  Prose words
%% 1,491 -> 1,612, against a target of 950.  THE TARGET IS NOT REACHABLE WITH THE
%% FACTS INTACT.  Three of the overrun's causes are mandates, not slack:
%%   * the twelve-row table costs ~162 prose words and grew ~30 when the legend
%%     values were renamed into English (`vacuous` -> `not its job` is one word
%%     to three).  Both the twelve rows and the rename are ordered.
%%   * PLAIN.md's example 4 splits the count, its rule and its strict reading
%%     into three short paragraphs.  That is +70 words over the one unreadable
%%     sentence it replaces, and it is the point of the exercise.
%%   * the four glosses and one-idea-per-sentence add ~10% across the file.
%% The fixed apparatus — bridge, gloss, table intro, table, legend, per-column
%% scope, counting rule, caveat, principle, takeaway — is ~640 words on its own,
%% and C15, C16, C17 and C19 each mandate a worked instance that cannot be a
%% clause.  Ranked cut list, if a later pass must reach 950; the supervisor
%% should pick, because each loses something a ruling names:
%%   1. the bitset instance (~130) -- loses the universally-quantified contrast
%%      sentence entirely; the redundancy map gives it no other home.
%%   2. the adversarial-verus battery (~100) -- the only gate-certified proof
%%      SUCCESSES in the paper; cutting it restores the bias review's §4.1
%%      finding.
%%   3. the provenance tier sentences on the two mutants (~30) -- PLAIN.md's
%%      must-survive list names them.
%%   4. two table rows (~25) -- REFUSED here: dropping rows while retracting the
%%      drop of six is the defect this section is about.

%% ⚠⚠⚠ THE UNDERGRADUATE PASS (.temp/brief/REVIEW-undergrad.md).  This section is
%% the one the cold reader gave up on: "§4's twelve-row table — this one I gave up
%% on.  Seven columns.  Four of the six verdict columns are tools I've never heard
%% of."  No cell, row, verdict, count or retraction moved.  What changed:
%%
%%  1. ⚠⚠ SIX ONE-LINE COLUMN DESCRIPTIONS NOW SIT IMMEDIATELY ABOVE THE TABLE,
%%     IN READING ORDER.  This was the reader's single most-requested change in
%%     the document, tied with defining `kernel`: "The four-value legend is
%%     genuinely good and I understood it immediately.  It's the only part of §4
%%     that worked first time.  The problem is the legend explains the VALUES and
%%     nothing explains the COLUMNS."  Also: "The `types` column is never
%%     explained at all.  Types of what?"  ⚠ THE LEGEND IS UNTOUCHED — it works,
%%     and the new block is deliberately written in the same shape so the two read
%%     as a pair.  ⚠ `Verus` is named here, because §6 leaned on "Verus's `N
%%     verified`" as a possessive without the paper ever saying what Verus is.
%%     ⚠ `functional specification` is glossed here, on the column whose presence
%%     or absence IS the difference between the last two columns.
%%     ⚠ TWO SENTENCES WERE DELETED AS SUBSUMED, and neither was a fact: "The rows
%%     are questions rather than bins" (the rows are visibly questions) and "The
%%     memory-safety column strips the functional specification; the full-proof
%%     column keeps it" (now bullet six, in plain words).  The clause that says
%%     WHICH four columns are counted is kept, because the counting rule needs it.
%%
%%  2. `kernel` DEFINED at the gloss block, undefined in all nine files before.
%%
%%  3. ⚠⚠ THE VERIFIER BATTERY IS REWRITTEN, and the fix is a MISREADING, not
%%     length.  "Under attack the prover holds" — the reader: "I read 'under
%%     attack' and thought: hostile inputs, like §5.  It turns out to mean
%%     deliberately damaging the proof and checking the verifier complains.  That's
%%     a completely different sense of 'attack' from the one used everywhere else
%%     in the paper.  I was lost for the whole paragraph."  The first clause now
%%     says which attack this is.  ⚠ "All 89, all 29 and all 69" NAME WHAT THEY
%%     COUNT, in the sentence: 89 clause deletions, 29 precondition deletions, 69
%%     twin-part deletions — matched by position to a list in the previous
%%     sentence was costing two reads.  ⚠ `precondition`, `twin`, `conjunct`,
%%     `tautology` and `Z3` were ALL on the never-explained list and this one
%%     paragraph used four of them; `conjunct` is now "each part of a twin", which
%%     is what the gate's `per_conjunct` field ranges over.  ⚠ EVERY NUMBER AND
%%     EVERY SCOPE CLAUSE IS UNCHANGED, including "though 13 had only Z3" — the
%%     weakest-negative disclosure the third bias review ordered.
%%
%%  4. ⚠⚠ THE RETRACTION PRINTS BOTH ENDPOINTS.  This was the ONE place in the
%%     paper where the cold reader stopped trusting the authors, and they were
%%     right: "It gives me the drop and neither endpoint.  Everywhere else this
%%     document is obsessive about printing both ends of a number — §3 literally
%%     has a rule about it ('Publish the pair').  The one place it doesn't is the
%%     place where the number is embarrassing."  The pair is now printed: FOUR OF
%%     SIX (67%) under the predecessor's six-row table, FIVE OF TEN (50%) over the
%%     twelve printed here.
%%     ⚠⚠ AND "about twenty-five points" IS GONE BECAUSE IT DOES NOT REPRODUCE
%%     UNDER THIS SECTION'S OWN COUNTING RULE.  Its source is RULINGS.md C31,
%%     which computes "about five over the printed twelve rows — roughly 42%,
%%     against the 67% the title advertises", i.e. a 12-row denominator.  This
%%     section counts over TEN rows, excluding the two where a detector carries no
%%     verdict, and gets 50%.  67 − 50 = 17, not 25.  Printing the endpoints
%%     instead of a subtraction makes the discrepancy impossible to inherit again.
%%     Nothing about the retraction's substance moved.
%%     ⚠ "That sentence ran under a six-row version…" now says WHICH sentence: the
%%     reader read that opening three times before working out it meant the box's
%%     own title, and nothing in the body signalled it.
%%
%%  5. `driver` glossed on the range-parser example, another three-read sentence
%%     ("This is the entire point of the range-parser example and I cannot restate
%%     it"), and "slice-relative" / "window-relative" are said in plain words.
%%     ⚠ C17 IS UNTOUCHED: the two unshipped programs are still in separate
%%     sentences and still marked "not the same program".
%%
%%  6. THE TITLE GAINS ONE WORD, "that".  The reader parsed "one blind spot safety
%%     made" as a noun phrase and got nowhere — "the missing relative pronoun cost
%%     me".  The FIVE is still in the title, which is what C31 requires.
%% ⚠⚠⚠ THE SECOND UNDERGRADUATE PASS (.temp/brief/REVIEW-undergrad2.md), 4/10.
%% "§4's twelve-row table: this is where I nearly stopped."  No cell, row, verdict,
%% count or retraction moved.  Six changes:
%%
%%  1. ⚠⚠ THE BOLD IS GONE FROM THE TABLE, and this is a removal rather than an
%%     explanation because NOTHING IN THE TREE OR IN ANY ver_ DEFINES IT.  ver_A's
%%     `70-quadruple.md` bolds cells too and never says why; no ruling, no legend
%%     and no comment attaches a meaning to it.  The reader: "I spent real effort
%%     trying to work out whether bold `missed` was different from plain `missed`.
%%     I think it's 'this one is bad news for us', but I'm guessing, and there are
%%     enough of them that it changes how the table reads."  ⚠ NO VERDICT CHANGED
%%     AND NO COUNT MOVED: bold `missed` and plain `missed` were always the same
%%     value, which is precisely the problem.  ⚠ THE RETRACTION'S "five of them
%%     carrying a bold *missed*" NOW READS "a *missed*", which is entailed by the
%%     old sentence and is still true of the six dropped rows.  ⚠ A LATER AGENT
%%     MUST NOT RE-BOLD CELLS WITHOUT WRITING THE RULE INTO THE LEGEND.
%%
%%  2. ⚠⚠ THE SIX QUALIFIED CELLS ARE NOW DECLARED, under the legend.  The reader
%%     counted SIX values in a table whose legend defines FOUR, and `partly` in
%%     particular was "a fifth verdict with no definition".  The new sentence
%%     defines all six by construction — each is one of the four values with its
%%     catch named — and states the counting consequence.  ⚠ NO CELL WAS
%%     REGRADED; `partly` is still `partly` and regrading a cell is a decision.
%%     The old sentence "A hedged cell, such as debug builds only or one compiler
%%     flag, counts as a dissent" is gone because the new one says it for all six
%%     instead of two.  The six are: p09's full proof, p42's types, p22's runtime
%%     check, p18's runtime check, p38's types and p38's sanitizers.
%%     ⚠⚠ FOURTH PASS: EACH OF THE SIX NOW NAMES ITS ROW, and that is the whole
%%     change — no cell regraded, no value renamed, no row dropped, the four-value
%%     legend untouched, and the counting consequence still stated.  Declaring
%%     them as a bare list of six values left the reader with "a four-value table
%%     with ten values in it … at that point the table stopped being something I
%%     could read and became something I had to study."  Their own diagnosis is
%%     the fix: "the rows I'd been told a story about were the rows I could
%%     read", so each qualifier is now attached to the row it grades and can be
%%     found in the table.  The mapping, which a later editor must preserve:
%%       *partly*                              -> p42, types            ("the release row")
%%       *a watchdog*                          -> p22, a runtime check  ("non-termination")
%%       *debug builds only*                   -> p18, a runtime check  ("the arithmetic row")
%%       *caught, with one flag*               -> p38, sanitizers       ("the two-types row")
%%       *not its job (Rust)*                  -> p38, types            (same row)
%%       *caught, until the spec inherits …*   -> p09, full proof       ("the in-bounds row")
%%     ⚠ THE ROW NICKNAMES ARE THE ROW LABELS' OWN WORDS, not new coinages:
%%     "does the release happen?", "does it terminate?", "is the arithmetic
%%     defined?", "reading the same memory as two different types?", "in bounds
%%     and wrong?".  If a row label is ever reworded, reword the nickname with it.
%%     ⚠ THE OTHER OPTION WAS REFUSED: reducing the table to the legend's four
%%     values would REGRADE six cells, which this file says twice is a decision
%%     and not an edit, and would collapse exactly the distinctions the
%%     retraction below turns on.
%%
%%  3. ⚠ THE RECYCLED ROW'S LABEL HAS AN ANTECEDENT.  "or recycled in place?" had
%%     no program and no subject — "recycled WHAT?" — and it is the row that gets
%%     excluded from the count.  It now names the handle table above it and marks
%%     itself a probe, which is what the footnote two paragraphs down already
%%     said.  CLAIMS.md §1.11 still binds: the recycle finding belongs to a
%%     reviewed probe on refused rows, never to the shipped handle-table pattern.
%%
%%  4. `row` IS DEFINED FOR THIS TABLE, in the sentence above it.  §1 defines the
%%     word once for the report as one line of a printed table; this says what
%%     THIS table's rows are.  The reader found three meanings across the paper
%%     and called it the worst single problem in it.  ⚠ THE TITLE KEEPS `rows` AND
%%     KEEPS THE FIVE, which is what C31 requires.
%%
%%  5. ⚠ THE GLOSS BLOCK IS CUT.  `kernel` was defined in six files in
%%     near-identical words, and this file's copy was bundled with the six column
%%     descriptions the reader actually needed — "by the fourth time I was reading
%%     it as noise, which is dangerous".  §0 defines it and §1 re-glosses it.
%%     `precondition` also loses its parenthetical here: §1 glosses it on the
%%     six-rung list.  ⚠ THE SIX COLUMN DESCRIPTIONS AND THE FOUR-VALUE LEGEND ARE
%%     UNTOUCHED — the reader named both as the only parts of §4 that worked.
%%
%%  6. ⚠⚠ THE RETRACTION PRINTS THE WITHDRAWN SENTENCE AS A QUOTATION AND SAYS
%%     WHOSE IT WAS.  The reader was told twice that a previous version of this
%%     report was biased and never once what it said: "Retracting without stating
%%     the retracted claim is the shape of hiding something."  The withdrawn
%%     sentence is this box's title, which is where it always was, but nothing
%%     said so — so the body now says "an earlier draft of this report printed
%%     that sentence", states what it claimed, and says why it was false.  The
%%     closing line is no longer the italic clause the reader read three times and
%%     could not restate; it is the same claim written as the circle it is.
%%     ⚠ BOTH ENDPOINTS (four of six, five of ten) ARE UNTOUCHED in the second
%%     paragraph, and §7 now points here in one sentence instead of alluding.
%% ⚠⚠⚠ THE THIRD UNDERGRADUATE PASS (.temp/brief/REVIEW-undergrad3.md), 5/10.
%% ⚠⚠ THIS FILE SCORED **3**, joint-lowest with §3, AND THE DIAGNOSIS MOVED.  The
%% six column descriptions added last pass WORKED — "The six column descriptions
%% above the table are good and I'm glad they're there — but the *columns* weren't
%% my problem, the *rows* were."  So did the four-value legend, again.  No cell,
%% verdict, count or retraction moved this pass.  Six changes:
%%
%%  1. ⚠⚠⚠ THE RANGE-PARSER EXAMPLE NOW OPENS THE SECTION, immediately after the
%%     bridge and BEFORE the table.  Its own note sits at the new site.  This was
%%     the reader's second-ranked request for the whole paper.
%%
%%  2. ⚠⚠ FOUR ROW LABELS ARE REWRITTEN SO EACH NAMES ITS BUG.  The reader could
%%     not name FOUR OF TWELVE rows on first read, and one of the four is the
%%     section's own best example.  The mapping, and NOT ONE CELL MOVED WITH IT:
%%       "or the same handle recycled in place?" -> "using a handle after its slot
%%          was reused?"  ("no idea")  ⚠ CLAIMS.md §1.11 still binds: it is a
%%          REVIEWED PROBE on refused rows, never the shipped handle-table
%%          pattern, which is why the instance cell still reads "a probe".
%%       "the bytes the request named?" -> "reading outside the window the request
%%          asked for?"  ("no idea until the range-parser example" — and that
%%          example now precedes it)
%%       "a C rule Rust lacks?" -> "reading the same memory as two different
%%          types?"  ("no idea")  ⚠ The row's C-only character is still visible in
%%          its own first cell, "not its job (Rust)", which is where it belongs;
%%          §5 now glosses the strict-aliasing rule itself.
%%       "does the machine stack hold?" -> "running out of stack space? · none"
%%          ("stack overflow? and every cell is —").  The instance cell now says
%%          outright that no program fills it, and the provenance sentence says
%%          why: "the stack-space row is empty because its one candidate was
%%          refused".  The reader stared at a printed row of nothing with no
%%          explanation beside it.
%%     ⚠⚠ THE ROW STAYS, AND CLAIMS.md §1.10 IS WHY IT IS EMPTY: there is no
%%     recursive kernel that verifies and dies of stack exhaustion, only a REFUSED
%%     candidate.  Dropping the row while retracting the drop of six is the defect
%%     this section is about.  ⚠ The counting rule's note above was updated to the
%%     new labels; the DENOMINATOR of ten is unchanged.
%%
%%  3. `trace`, `termination measure` and `tactic` are GLOSSED, a clause each, in
%%     the shape of the `landing pad` gloss the reader called the best in the
%%     paper.  All three were on the never-explained list and each carries a whole
%%     finding: `trace` is the entire reason the timing row is different,
%%     `termination measure` is the entire explanation of one of the five
%%     dissents, and `tactic` is what the 13-of-98 disclosure is about ("I
%%     appreciate the honesty and I cannot judge how much weaker").
%%
%%  4. THE TAKEAWAY DROPS ITS RESTATEMENT OF WHICH ROWS COMPRESS, ~17 words.  M8's
%%     corrected account is still whole in the `resource` paragraph three
%%     paragraphs up, which is where it is derived; the takeaway was the reader's
%%     third meeting with the same arithmetic in one section, and the arithmetic is
%%     what they gave up on.  ⚠ C31's FIVE OF TEN IS STILL IN THE BOX and the
%%     blind-spot consequence is untouched.  ⚠ AN OLDER BOX SAID "two shared
%%     silences … one is the gap", a third mutually inconsistent account — do not
%%     restore that wording if this clause ever comes back.
%%
%%  5. TWO SMALL TRIMS, neither a fact: "not a class of tool" (the sentence says
%%     it) and "and five patterns have no firing row" from the sanitizer scope.
%%     ⚠ CLAIMS.md §1.17 AND §1.18 ARE BOTH STILL DISCHARGED IN FULL — one gcc
%%     `-O1` address-and-undefined build of the plain C kernel, no clang, no
%%     hardened rung, no Rust; and 192 executed, 2 blocked, unsafe rung only.
\section{Four tools, five of ten rows, one blind spot that safety made}
\label{sec:allocation}

%% OUTLINE beat 1 -- the bridge.  ⚠⚠ C32 / rigour B1.  It used to open "In §3 the
%% mechanism could be removed and the number re-measured.  Here it cannot" --
%% which is FALSE of this section, whose own headline finding was found by
%% flipping a hardening flag and re-measuring, one of the levers §3 lists.  So
%% are the range parser's one-line change and the ghost ledger's planted line.
%% The honest asymmetry is about the INSTRUMENT, not the operation: §3's
%% observable is a scalar and this half's is a boolean, so a null here carries
%% less than a zero there -- which is why this half ALSO has to name the
%% resource, not instead.  §3's join is written to match.
%% ⚠ This is PLAIN.md's example 1, and it is the wording to keep.
In \ref{sec:bothends} we could measure. Here we cannot. A tool that reports
nothing looks exactly like a tool that was never looking for it, so silence on
its own proves nothing. We have to ask a different question instead: **what does
this tool actually watch?**

%% ⚠⚠⚠ THE THIRD UNDERGRADUATE PASS MOVED THIS EXAMPLE HERE, FROM AFTER THE
%% RETRACTION, AND IT IS THE SECTION'S OPENING CONCRETE CONTENT NOW.  It was on
%% page four of the file — after the table, after the count, after the retraction
%% — and the reader's verdict was that it is "the clearest statement in the paper
%% of what the whole coverage half is about … It should open the section."  They
%% also could not read the row label that names it ("the bytes the request
%% named?": "no idea until the range-parser example") or the `resource`
%% paragraph's "a suffix range inside its own buffer" ("meant nothing to me until
%% the range-parser example two pages later"), BOTH of which now come AFTER their
%% own explanation.  ⚠ NOTHING IN THE BOX MOVED except `rung` -> `version` three
%% times, which is this file's own stated wording everywhere else.
%% ⚠⚠ C17 IS UNTOUCHED AND STILL BINDS: the two unshipped programs are in
%% SEPARATE sentences and still marked "not the same program".  A later trim MUST
%% NOT splice them — "a verified one-line change to the shipped safe rung" is a
%% program that does not exist, and C17 corrects an earlier ruling that said it
%% did.  ⚠ DO NOT MOVE THIS BOX BACK BELOW THE TABLE.
\begin{example}{A bounds check bounds the slice you were handed}
The program is a range parser.
**No shipped version with a bounds check discloses** the neighbouring
window's secret; two unshipped programs do, and they are **not the same
program**. One is a one-token change to the safe version, zero `unsafe`, and not
verified; the other is the proved version with the same guard and its functional
postcondition stripped. Our *driver*, the test program that feeds each kernel its
input, hands the kernel the whole buffer, so a bounds check only keeps the index
inside that buffer. A guard that keeps it inside the caller's own window is
strictly stronger than memory safety, and discloses nothing.
\src{results/gate/p17-http-range.json}
\end{example}

%% Hash-routed re-gloss (convention 2.10.3), welded, not a subsection.
%% ⚠ "one build of one kernel" was rigour M17: every other section glosses a
%% rung as one SPELLING, and under §1's method each rung is built eight ways, so
%% "every pattern ships six builds" was false and §1's own table prints eight
%% rows for six rungs.  One wording, used everywhere.
%% ⚠⚠ THE `obligation` GLOSS IS CUT, and it is a dead beat rather than a trim:
%% this file leaned on the word three times, and all three uses were inside the
%% bitset and constant-time instances the final cut removed.  A gloss for a word
%% the file no longer uses is pure cost.  ⚠ IF EITHER INSTANCE IS RESTORED, THE
%% GLOSS COMES BACK WITH IT — the report is hash-routed and a reader lands on
%% `#allocation` cold.  It read: "An **obligation** is something the prover must
%% prove."
%% OUTLINE beats 2 and 3, merged.  Beat 3 is mandatory and cheap: the admission is
%% the difference between a finding and a flourish (E3 §1.1).  Its "zero upstream
%% hits" half is carried by the retraction, where the legend is already the
%% subject, rather than paid for twice.
**The table is ours**: no detector-coverage table exists in the research tree, so
every cell is this paper's own grading. Each **row** is one kind of bug, asked of
one program. Six verdict columns follow the question;
the middle four are the detectors we count.

- **types** — what the compiler refuses to build.
- **a runtime check** — a test the program makes on itself as it runs, like a
  bounds check.
- **sanitizers** — checking modes the compiler builds in, which abort the program
  on a bad access.
- **Miri** — an interpreter that runs Rust slowly, watching for undefined
  behaviour.
- **memory-safety proof** — a proof, machine-checked by Verus, that every access
  is in bounds.
- **full proof** — that, plus a proved *functional specification* of what the
  kernel must compute.

%% C15 -- THE RESTORED TABLE.  Twelve rows, four values.  Dropping two thin rows
%% while retracting the drop of six would be indefensible, so the two thinnest
%% stay.  ⚠ Every marker on one line.
| question · instance | types | a runtime check | sanitizers | Miri | memory-safety proof | full proof |
|---|---|---|---|---|---|---|
| outside the object? · \pat{p02} | missed | caught | caught | caught | caught | caught |
| in bounds and wrong? · \pat{p09} | missed | missed | not its job | not its job | missed | caught, until the spec inherits the bug |
| released through the allocator? · \pat{p27} | caught | caught | caught | caught | caught | caught |
| using a handle after its slot was reused? · a probe | missed | missed | — | missed | missed | — |
| does the release happen? · \pat{p42} | partly | missed | caught | caught | missed | missed |
| running out of stack space? · none | — | — | — | — | — | — |
| does it terminate? · \pat{p22} | missed | a watchdog | missed | missed | caught | caught |
| did it depend on a secret? · \pat{p47} | missed | missed | not its job | not its job | missed | missed |
| reading outside the window the request asked for? · \pat{p17} | missed | missed | not its job | not its job | missed | caught |
| is the arithmetic defined? · \pat{p18} | missed | debug builds only | caught | caught | caught | caught |
| reading the same memory as two different types? · \pat{p38} | not its job (Rust) | missed | caught, with one flag | not its job | not its job | not its job |
| do the regions overlap? · \pat{p08} | caught | not its job | missed | caught | missed | missed |

%% THE LEGEND IS THE LOAD-BEARING PART: collapsing `missed` into `not its job` is
%% half of what made the retracted sentence true (C15, E3 §1.4, §2.3).  Restored
%% in substance from 70-quadruple.md:138-142 and then RENAMED — see the header
%% note for the exact mapping.  The recycled-storage row is a reviewed probe, not
%% a shipped pattern, and says so here rather than in the row label.
Legend.

- **caught** — it found the bug, and we have the run that proves it.
- **missed** — it was looking, and it did not see.
- **not its job** — nothing here breaks the rule that tool enforces, so there was
  nothing for it to find.
- **—** — we never tested it.

Six cells add a catch to one of the four values: *partly* on the release row, *a
watchdog* on non-termination, *debug builds only* on the arithmetic row. The
two-types row has *caught, with one flag* and *not its job (Rust)*; the in-bounds
row's full proof is *caught, until the spec inherits the bug*. In the four
counted columns a catch is a dissent.

%% ⚠ CUT PASS (.temp/brief/CUT.md): "Compress the three-row footnote paragraph
%% to two sentences." Done, and nothing is lost — the three facts it carries (the
%% two columns' difference, which row is a probe, why the machine-stack row is
%% empty) and the provenance tally are all still here, in two sentences instead
%% of three. ⚠ The other two paragraphs that ruling names — the redzone argument
%% and the ghost-ledger footnote — were already cut in the previous pass, and
%% their own notes are further down; there was nothing left to compress.
Six rows rest on gate records, four on committed generators; the stack-space row
is empty, its one candidate refused.

%% ⚠⚠ RESTORED AFTER THE FINAL CUT, COMPRESSED FROM 58 WORDS TO 30, AND IT IS A
%% CORRECTNESS FIX RATHER THAN A NICETY. The cut pass removed
%% `caveat{Every column is one mechanism at one version}` and flagged the loss
%% itself: with it gone, the five `missed` cells on the recycled-storage row read
%% as "nobody can", which is FALSE. Other type systems reach that row, and
%% relational verification is built for the timing row this prover does not
%% reach. The paper must not make that claim by omission. Three citations from
%% ver_B carried the point; one carries it well enough at this length, and the
%% other two entries stay in refs.json (build_data errors on a \cite with no
%% entry, never the reverse).
Every column is one tool at one version. Another language's type system reaches
the recycled row, and there are provers built for the timing row this one does
not reach \cite{ctverif16}. Read each **missed** as *this tool did not*, never as
*nobody could*.

%% Per-cell provenance (beat 3) plus the scope block (beat 13) welded to it.  C19
%% fixes both column scopes; the last clause is what keeps the `caught` cells
%% honest.  CLAIMS.md §1.17 (the sanitizer counts are ONE build configuration)
%% and §1.18 (Miri: 192 executed, 2 blocked, no seed, unsafe rung only) are both
%% discharged here and may not be trimmed to the counts alone.
%% ⚠ TIGHTENED, ~11 words.  CLAIMS.md §1.17 and §1.18 are both still discharged
%% in full: §1.17's "one build configuration" is the first sentence, and §1.18's
%% "192 executed, 2 blocked, unsafe rung only" is the last.  What went is two
%% \num counts whose claim is now made over all rows ("every row declared to fire
%% fired"), which is the same statement.
The sanitizer column is one gcc `-O1` build of the plain C kernel with the
address and undefined-behaviour sanitizers on — no clang, no hardened rung, no
Rust. In it, every row declared to fire fired and every declared clean stayed
clean. The Miri column is
\num{totals.miri_runs} default runs of the unsafe rung alone, 2 of them blocked,
\num{totals.miri_ub|plain} undefined behaviour, and never a safe or a C rung.

%% ⚠⚠ THE COUNT, over the printed table (C31).  See the header note for the
%% derivation, for the counting rule's third clause, and for the one cell that
%% was changed.  The termination cell's `caught` is C16's correction and stands;
%% the count no longer needs the 73/21 tally, which the fact-check found stale --
%% it was quoted accurately from a README written when the corpus had 21 verified
%% files, and there are now 26.  The CLAIM reproduces; only the tally was stale,
%% and it understated, so dropping it costs the sentence nothing.
%% ⚠⚠ "they AGREE" / "do the same thing", never "they return the same verdict"
%% (third coverage-bias review §2b).  On three of the five they do NOT return the
%% same verdict: the in-bounds, secret and window rows read
%% `missed / not its job / not its job / missed`, two values the counting rule
%% groups.  The paragraph immediately after publishes what that choice is worth.
%% ⚠ THAT RULE IS WHAT LETS THE BOLD CARRY BOTH NUMBERS: "do the same thing"
%% attaches to FIVE and "give the identical verdict" attaches to TWO, which is
%% exactly the distinction §2b insists on.  The two verbs are load-bearing and
%% may not be swapped, merged, or applied to the other number.
Two rows have a detector column with no verdict — recycled storage and the
machine stack — so ten rows count. **All four tools do the same thing on five of
those ten rows, and give the identical verdict on two**. The five: two rows where
every tool catches the bug, three where every tool stays quiet.

The gap between them is the three quiet rows. There the tools are quiet for two
different reasons — some missed the bug, some were never looking for it. Reading
those two reasons alike gives five; requiring one answer gives two.

%% ⚠ TIGHTENED, not cut: "and not for the reason the previous version gave" went
%% (the retraction box below carries the correction, at length) and the two
%% sentences became one.  C16's substance — the memory-safety proof catches
%% non-termination BECAUSE Verus demands a termination measure on every exec loop
%% by default, functional specification or not — is intact.
On the other five rows one tool dissents. Non-termination is one: a watchdog
catches it, and so does the memory-safety proof, which demands a *termination
measure* on every loop that runs — a count that must shrink each time round
(**F5**).

%% CONVENTIONS §4 -- the one word, and it is THREE-WAY.  Flattening it to "they
%% all range over the allocation" would make `resource` look like a coinage.
%% ⚠ REWRITTEN over the printed table (rigour M8).  "Two rows compress because
%% all four range over the allocation" was not derivable: of the four agreeing
%% classes at the old grain, two agreed by FIRING, and the second silent row the
%% sentence needed was excluded by the same grain.  Over twelve rows the three
%% shared silences are in-bounds, the window and timing.
%% ⚠ Recycled storage is a fourth allocation case that the counting rule excludes
%% anyway; the legend already marks that row as a reviewed probe.
Two of those three shared silences are defects that never leave the allocation:
an index in bounds but wrong, a suffix range inside its own buffer. Every
detector here watches one **resource**, that allocation. The timing row is
different: they are silent there because they watch *values*, while a leak is a
property of the *trace* — the steps the run took, which no value records.
%% ⚠ CUT, 13 words: "One word, two answers, which is why it is this paper's only
%% vocabulary."  It describes the PAPER rather than the evidence, which is
%% PLAIN.md's own named category of cuttable sentence, and the three-way split it
%% pointed at is in the two sentences above it, whole.  CONVENTIONS §4's claim
%% that `resource` is earned is now made by the paragraph doing the earning
%% rather than by announcing it.

%% C15 / C19 -- THE FORTIFICATION BLINDING, scope welded in, closing on the
%% finding that REPLACES ver_B's flourish.  See header note 1 on the count.
%% ⚠ CLAIMS.md §1.13 is discharged by silence and must stay that way: the prose
%% does NOT say the harness enables `_FORTIFY_SOURCE` (it passes no such flag;
%% Ubuntu gcc's default at -O2/-O3 does), and the discriminator is the `_chk`
%% symbol and NOT the compiler, which is why the clang clause is in the sentence.
%% ⚠ REVISE PART E item 6 is intact: the sentence it protects — "the true blind
%% spot here was made by a second safety mechanism" — is untouched, and so is the
%% "almost every silence … this one is not" quantifier that gives it its force.
\begin{example}{The one silence that is not scope}
A genuinely overlapping `memcpy` draws no report, and not for want of a check.
The sanitizer has one, in its `memcpy` interceptor. But `_FORTIFY_SOURCE`, a
hardening feature, rewrote the call to `__memcpy_chk`, so it never arrives. Flip
that flag off and the same program reports `memcpy-param-overlap` at exit 1. The
discriminator is the `_chk` symbol, not the compiler: clang with fortification
forced on goes blind too. Scope, and it is thin. We probed the fortification
default once, with the preprocessor, at an optimisation level this harness never
builds. The clang half has no build command: its silence is logged, not
reproduced.
\src{patterns/p08-overlap-move/NOTES.md}

Almost every silence here is a guarantee that never ranged over the defect.
**This one is not**: the true blind spot here was made by a second safety
mechanism (**F5**).
\end{example}

%% C15 -- THE RETRACTION LIVES HERE, beside the claim it corrects (convention
%% 2.6), NOT in §7, which cites it without restating the mechanism.
%% ⚠ THE SECOND PARAGRAPH IS THE REASON C31 OVERRULED C16: the count above used
%% to be taken over the same six rows this box calls a truncation.  Saying so
%% here is cheaper than a caveat and it is the design working -- the correction
%% sits beside the claim it corrects.
\begin{retraction}{No cell reads "silent, and it should have seen this", and that is the result}
**An earlier draft of this report printed that sentence** as this box's title,
over a six-row version of the table above. It claimed no tool here was ever
caught missing a bug it was looking for. The table above shows that it
is false: **missed** is exactly that grade. The sentence became
true only after six of the twelve rows had been dropped, five of them carrying a
*missed* — the sharpest being the overlap row above. It also collapsed *missed*
and *not its job* into one value, defined as the second. What is left is a circle
and not a result: *drop every row where a detector looked and did not see, and no
row is left where one did*.

The count above used to be taken over those same six rows, where the four
detectors agreed on four — 67%. Over the twelve above they agree on five of the
ten rows all four reach — 50%. That the detectors agree less than a truncated
table suggested is the finding. \ref{sec:caughtitself} files both as ours.
\end{retraction}

%% C17 -- THE CORRECTION THAT MATTERS: no SHIPPED memory-safe rung discloses.  The
%% window- versus slice-relative sentence is the one worth keeping, and the two
%% unshipped programs are in two SEPARATE sentences so that no later trim can
%% splice them back into one program that does not exist.
%% ⚠ THE PRIOR-WORK CLAUSE WAS CUT FOR LENGTH (14 words).  It read "— prior work
%% already files memory-safe but wrong translations as a correctness gap
%% \cite{userstudy25}".  The redundancy map ALLOWED §4 one citation of that paper
%% here; it never required one, and §1 already argues the same point at length
%% against the same source.  Do not delete the entry from refs.json.
%% ⚠⚠⚠ THE FINAL CUT: "Compress the range-parser instance to TWO SENTENCES —
%% keep both programs named separately and keep the window-versus-slice
%% mechanism, drop the rest."  Executed at three short sentences rather than two,
%% because two would have run past PLAIN.md's 35-word ceiling and the voice rule
%% outranks the sentence count.  ~99 prose words went.
%% WHAT WENT, in restore order: (a) the gate-committed opening — two committed
%% inputs differing in exactly 28 bytes of a neighbouring window's secret, plain
%% unchecked C printing a different checksum on each at exit 0 with sanitizers
%% silent, WHILE A SIBLING INPUT FIRES `heap-buffer-overflow` IN THE SAME RUN, so
%% the sanitizer is provably live; (b) "hardened C and all four Rust rungs print
%% the model's answer", which is what "no shipped rung discloses" means; (c) the
%% second program's verdict, `10 verified, 0 errors`, and that it discloses the
%% IDENTICAL bytes; (d) the closing pair naming the window-relative guard as
%% strictly stronger than memory safety.
%% ⚠⚠ C17 IS STILL OBEYED AND THIS IS THE CLAUSE THAT MATTERS: the two unshipped
%% programs are still in SEPARATE sentences and are still marked "not the same
%% program".  A later trim MUST NOT splice them into one — "a verified one-line
%% change to the shipped safe rung" is a program that does not exist, and C17
%% corrects an earlier ruling of the supervisor's that said it did.
%% ⚠⚠ THE REDZONE PARAGRAPH IS CUT — 46 prose words, named by the trim brief.
%% WHAT IT SAID: the sanitizer's redzones destroy object adjacency, so a defect
%% whose harm needs two objects to be neighbours has no sanitizer row at all —
%% AND that this does NOT explain the range parser, because redzones separate
%% objects and that disclosure is inside one.
%% ⚠ C18 IS NOT VIOLATED BY THE CUT.  C18's ruling is "the redzone argument does
%% NOT explain the range parser.  Do not FUSE them."  With the paragraph absent
%% there is nothing to fuse and nothing that could be read as explaining the
%% range parser; the error C18 forbids is unreachable.  What is lost is a true
%% observation about the sanitizer column's scope, and that scope is already
%% stated above ("one gcc `-O1` … no clang, no hardened rung, no Rust").
%% ⚠ IF IT IS RESTORED, IT MUST KEEP BOTH SENTENCES: the second is the whole
%% reason the first is here, and printing the first alone is precisely the fusion
%% C18 forbids.

%% C19 -- the bitset, with "caught by nothing" narrowed to memory-safety-shaped
%% and the contrast sentence running in the PROVER'S favour.  The backwards
%% version is still in a task report and is not picked up here.  No cost figure
%% for the mutant: 6691.70 has no artefact, and it is cheaper, not dearer.
%% ⚠⚠ THE LAST-BUT-ONE SENTENCE IS THE HALF THAT DAMNS THE PROVER (C34(a), bias
%% review §3.4).  This paragraph once kept the half that runs in the prover's
%% favour and dropped the half that damns it, INSIDE the table whose truncation
%% this section retracts -- and both halves have identical provenance, since no
%% Verus log survives for any of these mutants, including the 18/1 the paper does
%% print.  Do not cut one without the other.
%% ⚠⚠⚠ THE FINAL CUT (.temp/brief/CUT.md's successor ruling, target 6,200 prose
%% words for the paper): **THE BITSET INSTANCE IS CUT ENTIRELY**, 125 prose
%% words.  The previous pass had already dropped its two verifier counts; this
%% pass drops the paragraph.
%% WHAT IT SAID, in full, so it can be restored verbatim in substance:
%%   A bitset probe indexes `words[q >> 6]`.  Type `q >> 7` and the index stays
%%   legal — the wrong word, since dividing by 128 never exceeds dividing by 64 —
%%   so nothing memory-safety-shaped catches it.  With the functional
%%   postcondition intact the prover refuses to verify it (`18 verified,
%%   1 errors`).  That contrast runs in the PROVER'S FAVOUR: the bounds check and
%%   the sanitizer catch the sibling `q >> 5` only on an input nobody would think
%%   to write, never on the five shipped ones, while the proof catches it on
%%   every input because its obligation is universally quantified.  One step on
%%   runs the OTHER WAY: move the specification's word index to match the typo,
%%   and its bridge lemma with it, and the prover verifies the bug (`20 verified,
%%   0 errors`).  Both mutants rebuild from a committed generator; neither is
%%   certified by any gate.  \src{patterns/p09-bitset/NOTES.md}
%% ⚠⚠ C34(a) IS NOT VIOLATED BY THE CUT, and this is the reason it was cuttable
%% at all: the half that runs in the prover's favour and the half that damns it
%% had identical provenance and BOTH WENT TOGETHER.  Cutting one alone would have
%% been the defect this section retracts.  If it is restored, restore both halves,
%% both counts and the tier clause — never one of the three.
%% ⚠ RESTORE ORDER FOR THIS FILE, if words ever come back: (1) the bitset
%% instance, in full, with both halves; (2) the constant-time instance below;
%% (3) the range parser's four dropped sentences; (4) the verifier battery's
%% original six sentences.
%% ⚠ Provenance, still checked and still true, for whoever restores it:
%% `patterns/p09-bitset/controls/gen_controls.py` is committed and builds
%% `m_shift7` (line 361) and `m_shift7_spec2` (line 371);
%% `results/gate/p09-bitset.json` carries `controls_json: {}` and a single
%% `verus.rs` at 18/0.  Both clauses are mandatory on any restoration.

%% ⚠⚠ THE GHOST-LEDGER FOOTNOTE IS CUT — 57 prose words, named by the trim brief.
%% WHAT IT SAID: the ghost ledger's verifying leaker is byte-identical to the
%% unsafe rung WITH THE BUG PLANTED IN IT and moves the digest away from the
%% shipped pair, so the pin caught the attacked proof at both pinned levels —
%% "the pin protected the pattern, the proof did not" (C19) — with
%% "expressibility at this pin is open" attached, because saying the prover
%% CANNOT state leak-freedom is a standing retraction upstream.
%% ⚠ §6.4's "Budget for the thing that caught the attack" bullet used to cite
%% \ref{sec:allocation} for exactly this row.  That bullet leans only on the two
%% attacks it already names, so no \ref points at a paragraph that is not here.
%% Check that before restoring anything.
%% ⚠ WHY THIS ONE.  Second bias review §3b: every measured proof instance the
%% paper carries is a FAILURE at tier T2/T3, and this was the third of them —
%% and its own upstream file, `patterns/p42-goto-cleanup/NOTES.md:35`, records
%% the TASK_110 clause about what the ghost ledger states as "withdrawn in full".
%% The p42 table row stands, unannotated, as most rows do.

%% ⚠⚠⚠ THE FINAL CUT: **THE CONSTANT-TIME INSTANCE IS CUT ENTIRELY**, 96 prose
%% words.  It is item (2) on this file's restore list, above.
%% WHAT IT SAID: on the timing row the instance is measured and not only
%% classified — replace that kernel's constant-time loop with one that exits
%% early, add a ghost lemma, and it verifies at `14 verified, 0 errors`; the
%% KERNEL'S OWN obligation count is unchanged at three (CLAIMS.md §1.8 — the file
%% total moves 12 -> 14, and the word "kernel's" is load-bearing) and not one
%% character of its `requires` or `ensures` differs; the compiled result then
%% executes 7,088 MORE INSTRUCTIONS on one input than on another printing the
%% same checksum (CLAIMS.md §1.9 — there is NO wall-clock or cycle measurement of
%% this leak, so it is an instruction count and the sentence must say so); **the
%% top rung certifies a leaking kernel** and nothing in the gate noticed; and the
%% mutant rebuilds from a committed generator and is certified by no gate.
%% \src{patterns/p47-ct-compare/NOTES.md}
%% ⚠ WHAT SURVIVES WITHOUT IT: the timing row still ships in the table, still
%% reads `missed` under both proof columns, and the `resource` paragraph still
%% carries the reason — the detectors watch VALUES and a leak is a property of
%% the TRACE.  What is lost is the measured instance behind the class, which is a
%% strictly weaker paper.  §6.4's "delete a leak-freedom postcondition,
%% unchanged; substitute a leaking loop, unchanged" is the surviving statement of
%% it; that bullet carries no \ref to this paragraph, so nothing dangles.

%% ⚠⚠ THE GATE'S OWN ADVERSARIAL-VERUS BATTERY.  Second coverage-bias review
%% §4.1, its top-ranked omission: every measured proof instance this paper
%% carries is a FAILURE at tier T2 or T3, while SIX gate-certified, corpus-wide
%% results about the same proofs are successes and were absent in their entirety.
%% The provenance ran the same way as the bias, which is worse than the
%% imbalance.  It goes HERE and not in §6 because §6 introduces no evidence
%% (OUTLINE PART 1 rule (i)), and because the two instances it answers are the
%% two paragraphs immediately above it.
%%
%% ⚠ EVERY NUMBER RE-DERIVED from all 26 `results/gate/*.json`, not taken from
%% the review, because the parent tree moved twice that session:
%%   clause_deletion  116 mutants, 116 rejected — but only **89** carry a
%%                    `clause`; the other 27 are `assert(false)` liveness probes
%%                    for the stage itself.  The review printed 116 as the
%%                    clause-deletion count and that is the total, not the
%%                    deletions.  THE PROSE SAYS 89, which is what "delete one
%%                    clause" means.  Kinds: 28 `verified` + 61 `trusted`.
%%   requires_strength `test == "deletion"`: 29 of 29 rejected.
%%   requires_strength `test == "tautology"`: 98 of 98 return `not a tautology`,
%%                    each run under bare Z3 plus `nonlinear_arith` and
%%                    `bit_vector` where applicable.
%%   ⚠⚠ "UNDER THREE TACTICS (98 of 98)" WAS FALSE and is corrected (third
%%   coverage-bias review §1, its one factual overstatement, in the pro-proof
%%   direction).  Re-derived over all 26 gate records from `tactics_ran` /
%%   `tactics_inapplicable`: only **4** of the 98 ran three tactics, **81** ran
%%   two (`bit_vector` inapplicable) and **13** ran bare Z3 ALONE (both extra
%%   tactics inapplicable).  Every probe ran exactly the tactics the gate did not
%%   mark inapplicable, so "under every tactic that applies to it" is exact; the
%%   98 of 98 verdict is untouched.  The 13 are named in the prose because a
%%   tautology probe under fewer tactics is a WEAKER negative and this paper
%%   ships the direction of its own limits.
%%   verified_twins   56 twins over 26 patterns, 56 `signature_identical`, and
%%                    `vacuity_probe.per_conjunct` gives 69 conjuncts with
%%                    `load_bearing` 69.
%%   proof_domain     194 (pattern, input) rows, 2,512,736 calls, ZERO
%%                    `requires_ok: false`.  `harness/check.py:6481` evaluates the
%%                    kernel's derived `requires` on EVERY call of EVERY measured
%%                    input, adversarial included, and FAILS on an empty
%%                    `requires`, so the stage cannot be vacuously green.
%% ⚠⚠ 2,512,736 IS LIVE off `totals.proof_domain.calls` AND THE `literal-ok`
%% WAIVER IS GONE (third review §1).  Its justification — "data/index.json
%% publishes no proof_domain total" — was FALSE: `totals.proof_domain.calls` is
%% in the index and equals 2512736 exactly, so the section's largest pro-proof
%% figure was the one number in it that could go stale.  `.web/CLAUDE.md` rule 2.
%% Do not re-freeze it.
%% ⚠⚠ THE LAST SENTENCE IS SCOPED TO THE PROVER (third coverage-bias review
%% §3.5).  It used to read "every silence in this table is about what it was
%% given" — a universal over the whole table, asserted twelve lines below a title
%% saying one silence was made by a HARDENING FLAG and is precisely not that.
%% The title is right; the universal was wrong.  The prover's own silences ARE
%% all about what it was given, which is what the bitset paragraph demonstrates.
%% ⚠ It is the point of the paragraph and not decoration: it is the distinction
%% between a proof that is weak and a proof that was never aimed at the defect,
%% which is this whole section's subject.
%% ⚠⚠⚠ THE FINAL CUT: "Compress the verifier battery to TWO SENTENCES."  Executed
%% at four short ones, ~38 prose words lighter, for the same 35-word reason as
%% the range parser.  EVERY GATE-CERTIFIED SUCCESS SURVIVES — the successes are
%% on the must-not-lose list and "compressed is fine, absent is not".
%% WHAT WENT: the lead sentence "Neither of those is the verifier failing under
%% attack", which pointed at the two instances this pass cut and had nothing left
%% to point at; the words "one at a time" and "a trusted item's"; and the closing
%% "the prover holds what it is given, and every silence *of the prover's* in
%% this table is about what it was given" — whose demonstration was the bitset
%% paragraph, also cut, so it would have stood on nothing.  ⚠ THAT CLOSING
%% SENTENCE MUST COME BACK WITH THE BITSET INSTANCE AND NOT BEFORE, and it must
%% stay SCOPED TO THE PROVER: the unscoped universal ("every silence in this
%% table is about what it was given") is false twelve lines under a title saying
%% one silence was made by a hardening flag, and the third coverage-bias review
%% §3.5 caught it.
**On every run we attack the proofs themselves**: we damage
each proof and demand the prover notice. We delete each
clause of a specification, each precondition, and each part of a *twin*, a second
statement of the same property. That is 187 damaged proofs — 89, 29 and 69 of the
three kinds — and the prover rejected every one. We also check that no
precondition is a *tautology*, true for free and promising nothing: 98 probes, 98
clean. Thirteen of the 98 ran under Z3 alone, the solver under the prover, with
no extra *tactic* — a specialist strategy for one kind of arithmetic — to help
it. A weaker test, and we say so. The kernel's
stated precondition holds on all
\num{totals.proof_domain.calls} measured calls, adversarial inputs included.
\src{results/gate/*.json}

%% ⚠⚠⚠ THE FINAL CUT: **THE `caveat{Every column is one mechanism at one
%% version}` IS CUT**, 58 prose words.  It was carried from ver_B near-verbatim
%% and three reviewers named it load-bearing, so this is the most expensive cut
%% in the file after the two instances above.  It read:
%%   "A linear or session-typed language reaches the recycled-storage row this
%%    type system does not.  Relational verification is built for the timing row
%%    this prover at this pin does not reach \cite{ctverif16} \cite{jasmin17}
%%    \cite{compcertct}.  Read every silence as *this tool, this version*, never
%%    as *nobody can* — and every **caught** as *this build, these inputs*."
%% ⚠ WHY IT WAS THE ONE TO GO.  Everything it bounds is stated elsewhere in the
%% section by construction rather than by assertion: the legend's **not its job**
%% value says a silence can be scope rather than blindness; the per-column scope
%% paragraph names the ONE build configuration behind the sanitizer column and
%% the unsafe-rung-only population behind Miri; the blind-spot example shows a
%% silence flipping when one flag flips; and the section's own title attributes
%% the blind spot to a hardening flag rather than to any tool's limits.
%% ⚠⚠ WHAT IS GENUINELY LOST, and it is why this is FIRST on the restore list
%% after the two instances: the paper no longer says anywhere that ANOTHER
%% mechanism reaches a row this corpus's tools do not.  A reader can now take the
%% recycled-storage row's five `missed` cells as "nobody can", which is the
%% reading the caveat existed to forbid, and CLAIMS.md's authority order does not
%% protect against it.  ⚠ `ctverif16`, `jasmin17` and `compcertct` are now
%% uncited; they STAY in refs.json, because build_data.py errors only on a \cite
%% with no entry.

%% ⚠⚠ THE FINAL CUT: **THE `principle{Name the resource, not the tool}` IS CUT**,
%% 56 prose words, beyond the beats the ruling named — this file could not reach
%% its target on the bitset, the constant-time instance, the range parser and the
%% battery alone.  It read:
%%   "Before you believe that a check, a sanitizer, an interpreter or a proof
%%    covers a bug class, write down which resource its guarantee ranges over.
%%    Then ask whether the defect lives there.  Whatever it does not range over
%%    is still your problem, and you can name that before running anything."
%% ⚠ WHY THIS PRINCIPLE AND NOT ANOTHER: of the paper's four, it is the only one
%% stated twice more.  §0's F5 carries it as a `Do:` line ("name what each of
%% your own tools watches, and put a known-bad input per detector in the build
%% you ship") and §99's second closing question IS this principle in interrogative
%% form ("Of any tool that reports nothing: what does its guarantee actually
%% watch?").  §2's principle is the paper's method plus the bound CLAIMS.md §1.23
%% requires shipped with it, and §3's is \ref'd by §6.2; neither was available.
%% ⚠ THE WORD `resource` SURVIVES, in the paragraph that earns it three
%% paragraphs above and in the takeaway below.  CONVENTIONS §4 is unaffected.
%% RESTORE THIS AFTER the two cut instances and before the range parser's
%% dropped sentences.

%% ⚠ The takeaway takes the recomputed count (C31) and M8's corrected account of
%% WHICH rows compress: three shared silences, two of them the allocation and one
%% the value-versus-trace gap.  An older box said "two shared silences ... one is
%% the gap", which was a third mutually inconsistent account.
%% ⚠ FINAL CUT, ~14 words.  M8's corrected account of WHICH rows compress is kept
%% as a clause rather than a sentence; the count (C31's five of ten) and the
%% blind-spot consequence are untouched.  An older box said "two shared silences
%% … one is the gap", which was a third mutually inconsistent account — do not
%% restore that wording.
\begin{takeaway}
Four tools, five of the ten rows they all reach.
The one silence that is not scope was made by a second safety mechanism, so
detectors do not add up. \ref{sec:measure} spends this.
\end{takeaway}
